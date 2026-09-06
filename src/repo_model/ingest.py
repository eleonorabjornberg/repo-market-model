"""Immutable, checksummed ingestion from official public sources.

This module deliberately uses only the Python standard library. Raw responses are
saved without modification alongside a manifest recording retrieval time, URL and
SHA-256 digest. Transformations belong in a separate modeling-panel step.
"""

from __future__ import annotations

import hashlib
import gzip
import io
import json
import os
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Mapping, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen


USER_AGENT = (
    "repo-market-model/0.1 "
    "(+https://github.com/eleonorabjornberg/repo-market-model; academic research)"
)
NYFED_BASE = "https://markets.newyorkfed.org/api/rates/secured"
FRED_GRAPH_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FRED_MACRO_SERIES = (
    "IORB",       # interest on reserve balances, 2021-present
    "IOER",       # interest on excess reserves, historical policy anchor
    "WRESBAL",    # reserve balances with Federal Reserve Banks
    "WTREGEN",    # Treasury General Account
    "RRPONTSYD",  # overnight reverse-repurchase agreements
    "DFF",        # effective federal funds rate
)


@dataclass(frozen=True)
class SnapshotArtifact:
    source_id: str
    path: Path
    retrieved_at: str
    sha256: str
    url: str
    byte_count: int

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "path": str(self.path),
            "retrieved_at": self.retrieved_at,
            "sha256": self.sha256,
            "url": self.url,
            "byte_count": self.byte_count,
        }


def _download(url: str, timeout: int = 60) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urlopen(request, timeout=timeout) as response:
        payload = response.read()
        encoding = response.headers.get("Content-Encoding", "").lower()
        return _decode_transport(payload, encoding)


def _decode_transport(payload: bytes, encoding: str = "") -> bytes:
    if encoding.lower() == "gzip" or payload.startswith(b"\x1f\x8b"):
        return gzip.decompress(payload)
    return payload


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _save_snapshot(
    source_id: str,
    url: str,
    payload: bytes,
    output_root: Path,
    suffix: str,
    retrieved_at: Optional[datetime] = None,
) -> SnapshotArtifact:
    timestamp = retrieved_at or datetime.now(timezone.utc)
    stamp = timestamp.strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(payload).hexdigest()
    path = output_root / source_id / f"{stamp}_{digest[:12]}.{suffix}"
    _atomic_write(path, payload)
    artifact = SnapshotArtifact(
        source_id=source_id,
        path=path,
        retrieved_at=timestamp.isoformat(),
        sha256=digest,
        url=url,
        byte_count=len(payload),
    )
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    manifest = json.dumps(artifact.as_dict(), indent=2, sort_keys=True).encode("utf-8") + b"\n"
    _atomic_write(manifest_path, manifest)
    return artifact


def fetch_nyfed_reference_rate(
    output_root: Path,
    rate_name: str,
    start: str,
    end: str,
    downloader: Callable[[str], bytes] = _download,
) -> List[SnapshotArtifact]:
    """Fetch both the rate distribution and volume for a NY Fed reference rate."""

    artifacts: List[SnapshotArtifact] = []
    retrieved_at = datetime.now(timezone.utc)
    for observation_type in ("rate", "volume"):
        query = urlencode({"startDate": start, "endDate": end, "type": observation_type})
        url = f"{NYFED_BASE}/{rate_name}/search.json?{query}"
        payload = downloader(url)
        parsed = json.loads(payload)
        if not isinstance(parsed.get("refRates"), list):
            raise ValueError("New York Fed response does not contain a refRates list")
        artifacts.append(
            _save_snapshot(
                source_id=f"nyfed-{rate_name}-{observation_type}",
                url=url,
                payload=payload,
                output_root=output_root,
                suffix="json",
                retrieved_at=retrieved_at,
            )
        )
    return artifacts


def fetch_fred_macro(
    output_root: Path,
    downloader: Callable[[str], bytes] = _download,
) -> List[SnapshotArtifact]:
    """Fetch the current-vintage macro panel from FRED's public graph endpoint.

    This endpoint does not provide historical vintages. The manifest and source
    registry make that limitation explicit; an ALFRED adapter will be added when a
    free FRED API key is configured locally.
    """

    url = f"{FRED_GRAPH_BASE}?{urlencode({'id': ','.join(FRED_MACRO_SERIES)})}"
    payload = downloader(url)
    suffix = "csv"
    contents = [payload]
    if payload.startswith(b"PK"):
        suffix = "zip"
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise ValueError("FRED ZIP does not contain a CSV data file")
            contents = [archive.read(name) for name in csv_names]
    headers = [content.splitlines()[0].decode("utf-8") for content in contents if content]
    if not headers or any("observation_date" not in header for header in headers):
        raise ValueError("FRED response is not the expected CSV format")
    return [
        _save_snapshot(
            source_id="fred-macro-latest-vintage",
            url=url,
            payload=payload,
            output_root=output_root,
            suffix=suffix,
        )
    ]
