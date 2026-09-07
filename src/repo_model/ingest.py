"""Immutable, checksummed ingestion from official public sources.

This module deliberately uses only the Python standard library. Raw responses are
saved without modification alongside a manifest recording retrieval time, URL and
SHA-256 digest. Transformations belong in a separate modeling-panel step.
"""

from __future__ import annotations

import csv
import hashlib
import gzip
import io
import json
import os
import re
import tempfile
import zipfile
from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
# Imported by name, not as a module: `datetime.time` above already holds that
# name, and `import time` would shadow it.
from time import sleep as _sleep
from typing import Callable, Iterable, List, Mapping, Optional, Sequence
from urllib.parse import parse_qs, urlencode, urlparse
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
    "RRPONTSYAWARD",  # overnight reverse-repo award rate
    "TREAST",     # Treasury securities held outright by the Federal Reserve
)
TREASURY_AUCTIONS_BASE = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
    "v1/accounting/od/auctions_query"
)
DEFAULT_SOURCE_REGISTRY = Path(__file__).parents[2] / "metadata" / "sources.json"
#: The declared set of Form N-MFP archives that constitutes the `sec_nmfp`
#: source. Committed, because `data/raw/` is not: without it a checkout with an
#: empty `data/raw/` cannot tell "not downloaded yet" from "never existed", and
#: cannot tell either from "downloaded, and refused".
SEC_NMFP_ARCHIVE_MANIFEST = (
    Path(__file__).parents[2] / "metadata" / "sec_nmfp_archives.json"
)
#: Seconds between SEC downloads. The archives are 5-15 MB each and SEC
#: rate-limits aggressively; a backfill is a hundred of them in a row.
SEC_REQUEST_PAUSE_SECONDS = 1.0

# Snapshots captured before the registry adopted Python-style source IDs remain
# immutable evidence. Normalize their manifest IDs at the parser boundary rather
# than rewriting the checksummed artifacts in place.
LEGACY_SOURCE_IDS = {
    "fred-macro-latest-vintage": "fred_macro_latest_vintage",
    "nyfed-sofr-rate": "nyfed_sofr",
    "nyfed-sofr-volume": "nyfed_sofr",
}


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


@dataclass(frozen=True)
class PanelArtifact:
    """A reproducible processed snapshot and the raw snapshots behind it."""

    path: Path
    created_at: str
    sha256: str
    row_count: int
    source_shas: Sequence[str]
    raw_snapshots: Sequence[Mapping[str, object]]
    quality_report_path: Path
    quality_report_sha256: str
    accounting_residuals: Mapping[str, float]

    def as_dict(self) -> Mapping[str, object]:
        return {
            "path": str(self.path),
            "created_at": self.created_at,
            "sha256": self.sha256,
            "row_count": self.row_count,
            "source_shas": list(self.source_shas),
            "raw_snapshots": list(self.raw_snapshots),
            "quality_report_path": str(self.quality_report_path),
            "quality_report_sha256": self.quality_report_sha256,
            "accounting_residuals": dict(sorted(self.accounting_residuals.items())),
        }


def _download(url: str, timeout: int = 60) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urlopen(request, timeout=timeout) as response:
        payload = response.read()
        encoding = response.headers.get("Content-Encoding", "").lower()
        return _decode_transport(payload, encoding)


def _download_sec(url: str, contact_email: str, timeout: int = 60) -> bytes:
    identity = contact_email.strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", identity):
        raise ValueError("SEC downloads require a valid contact email")
    request = Request(
        url,
        headers={
            "User-Agent": f"repo-market-model/0.1 {identity}",
            "Accept": "application/zip, application/octet-stream",
        },
    )
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
    snapshot_path = output_root / source_id / f"{stamp}_{digest[:12]}.{suffix}"
    _atomic_write(snapshot_path, payload)
    path = snapshot_path.resolve()
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
                source_id=f"nyfed_{rate_name}",
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
            source_id="fred_macro_latest_vintage",
            url=url,
            payload=payload,
            output_root=output_root,
            suffix=suffix,
        )
    ]


def fetch_treasury_auctions(
    output_root: Path,
    start: str,
    end: str,
    downloader: Callable[[str], bytes] = _download,
) -> List[SnapshotArtifact]:
    """Fetch Treasury auction records whose issue date falls in a date range."""

    # Validate before interpolating caller-provided dates into a query.
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    if start_date > end_date:
        raise ValueError("Treasury auction start date must not follow end date")
    query = urlencode(
        {
            "filter": f"issue_date:gte:{start},issue_date:lte:{end}",
            "page[size]": "10000",
            "sort": "record_date,issue_date,cusip",
        }
    )
    url = f"{TREASURY_AUCTIONS_BASE}?{query}"
    payload = downloader(url)
    parsed = json.loads(payload)
    if not isinstance(parsed, dict) or not isinstance(parsed.get("data"), list):
        raise ValueError("Treasury Fiscal Data response does not contain a data list")
    return [
        _save_snapshot(
            source_id="treasury_auctions",
            url=url,
            payload=payload,
            output_root=output_root,
            suffix="json",
        )
    ]


def fetch_sec_nmfp(
    output_root: Path,
    url: str,
    downloader: Optional[Callable[[str], bytes]] = None,
    *,
    contact_email: Optional[str] = None,
) -> List[SnapshotArtifact]:
    """Fetch and validate one official SEC Form N-MFP flat-file archive.

    SEC publishes period-specific links rather than a stable latest-data URL, so
    the discovered official URL is explicit input and is preserved in provenance.
    """

    if not url.lower().startswith("https://www.sec.gov/"):
        raise ValueError("Form N-MFP URL must be an official https://www.sec.gov/ URL")
    if downloader is None:
        if not contact_email:
            raise ValueError("SEC downloads require contact_email for the User-Agent")
        payload = _download_sec(url, contact_email)
    else:
        payload = downloader(url)
    if not payload.startswith(b"PK"):
        raise ValueError("SEC Form N-MFP response is not a ZIP archive")
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            tabular = [
                name for name in archive.namelist()
                if name.lower().endswith((".tsv", ".txt", ".csv"))
            ]
    except zipfile.BadZipFile as exc:
        raise ValueError("SEC Form N-MFP response is not a valid ZIP archive") from exc
    if not tabular:
        raise ValueError("SEC Form N-MFP ZIP contains no flat data files")
    return [
        _save_snapshot(
            source_id="sec_nmfp",
            url=url,
            payload=payload,
            output_root=output_root,
            suffix="zip",
        )
    ]


@dataclass(frozen=True)
class ArchiveRecord:
    """One immutable Form N-MFP archive, as the committed manifest records it.

    `sha256` and `byte_count` identify the bytes; `url` says where they came
    from; `first_retrieved_at` says when the digest was first observed here. The
    bytes themselves stay out of git.

    `refusals` is the parser's own verdict on the archive, computed by running
    `nmfp_schema_refusals` over the downloaded bytes rather than typed in by
    hand. An empty tuple means the archive was read faithfully and is part of
    the source; a non-empty one names every table and column the parser needs
    and the archive does not have. Recording the verdict is what makes the
    difference between "never existed", "not downloaded yet" and "downloaded,
    and refused" visible from a fresh checkout.
    """

    url: str
    sha256: str = ""
    byte_count: int = 0
    first_retrieved_at: str = ""
    refusals: tuple = ()

    @property
    def admitted(self) -> bool:
        """True only for an archive that was fetched and read faithfully.

        An unfetched record is neither admitted nor refused, and must not be
        reported as either: `sha256` is empty precisely because nobody has
        looked yet.
        """

        return bool(self.sha256) and not self.refusals

    def as_dict(self) -> Mapping[str, object]:
        return {
            "url": self.url,
            "sha256": self.sha256,
            "byte_count": self.byte_count,
            "first_retrieved_at": self.first_retrieved_at,
            "refusals": list(self.refusals),
        }


def nmfp_schema_refusals(payload: bytes) -> tuple:
    """Every reason the parser cannot read this archive faithfully, or none.

    Derived from `NMFP_REQUIRED_COLUMNS`, the same declaration `_nmfp_table`
    enforces, so the manifest cannot record a verdict the parser disagrees with.
    The difference is only that `_nmfp_table` raises on the first problem, which
    is right for a parse and wrong for a report: an archive from a schema the
    project has never seen should name everything it is missing in one pass.

    A schema check on headers is not a schema check on meaning. It cannot see a
    column that kept its name and changed its units, or a categorical whose
    vocabulary was rewritten. See `docs/track-a-decisions-2026-09-07.md` for a
    dated instance of the second, which this function returns no refusal for.
    """

    problems = []
    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except zipfile.BadZipFile:
        return ("not a valid ZIP archive",)
    with archive:
        names = frozenset(archive.namelist())
        for table, required in sorted(NMFP_REQUIRED_COLUMNS.items()):
            if table not in names:
                problems.append(f"lacks required table {table}")
                continue
            header = archive.open(table).readline().decode("utf-8-sig")
            reader = csv.reader(io.StringIO(header.rstrip("\r\n")), delimiter="\t")
            columns = frozenset(next(reader, []))
            missing = required - columns
            if missing:
                problems.append(
                    f"{table} lacks required columns {', '.join(sorted(missing))}"
                )
    return tuple(problems)


def load_sec_nmfp_archive_manifest(
    path: Path = SEC_NMFP_ARCHIVE_MANIFEST,
) -> tuple:
    """Read the declared archive set, reporting a bad path or bad JSON alike."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load N-MFP archive manifest: {exc}") from exc
    archives = payload.get("archives") if isinstance(payload, Mapping) else None
    if not isinstance(archives, list) or not archives:
        raise ValueError(
            f"N-MFP archive manifest {path} declares no archives; an empty "
            "declared set is indistinguishable from a source nobody has "
            "described, and must not read as one"
        )
    records = []
    seen = set()
    for entry in archives:
        if not isinstance(entry, Mapping) or not str(entry.get("url") or "").strip():
            raise ValueError(f"N-MFP archive manifest {path} has an entry with no url")
        url = str(entry["url"]).strip()
        if url in seen:
            raise ValueError(f"N-MFP archive manifest {path} declares {url} twice")
        seen.add(url)
        records.append(
            ArchiveRecord(
                url=url,
                sha256=str(entry.get("sha256") or ""),
                byte_count=int(entry.get("byte_count") or 0),
                first_retrieved_at=str(entry.get("first_retrieved_at") or ""),
                refusals=tuple(str(item) for item in entry.get("refusals") or ()),
            )
        )
    return tuple(records)


def write_sec_nmfp_archive_manifest(
    records: Iterable[ArchiveRecord],
    path: Path = SEC_NMFP_ARCHIVE_MANIFEST,
    *,
    index_url: str = "",
) -> None:
    """Write the declared archive set. Ordered by url, so a re-run is a no-op."""

    payload = {
        "source_id": "sec_nmfp",
        "index_url": index_url,
        "note": (
            "The Form N-MFP archives that constitute this source. data/raw/ is "
            "gitignored and these bytes are not committed, so this file is how a "
            "fresh checkout knows what history is supposed to exist. An entry "
            "with an empty sha256 has never been fetched here. An entry with a "
            "non-empty refusals list was fetched and refused: the parser cannot "
            "read it faithfully, so it contributes no observations and is not "
            "placed under data/raw/."
        ),
        "archives": [
            record.as_dict()
            for record in sorted(records, key=lambda record: record.url)
        ],
    }
    _atomic_write(
        path, json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )


def fetch_sec_nmfp_archives(
    output_root: Path,
    records: Iterable[ArchiveRecord],
    *,
    contact_email: Optional[str] = None,
    downloader: Optional[Callable[[str], bytes]] = None,
    recheck: bool = False,
    pause_seconds: float = SEC_REQUEST_PAUSE_SECONDS,
    sleep: Callable[[float], None] = _sleep,
) -> tuple:
    """Fetch the declared archive set politely, idempotently, and refusing early.

    Idempotent in both directions. An archive whose recorded `sha256` already
    matches a snapshot on disk is not downloaded again, and neither is one
    already recorded as refused -- re-downloading a hundred archives to re-derive
    a verdict that is written down is not politeness. `recheck=True` forces both,
    for the day the parser's requirements change and the verdicts have to be
    re-earned.

    An archive is validated before it is placed under `output_root`, so
    `data/raw/` only ever holds archives the parser can read faithfully. This is
    the difference between refusing an archive and quarantining it after the
    fact: everything under `data/raw/` is panel input by construction, and an
    unreadable archive sitting there is a claim that it is one.

    Returns the updated records, in the order given.
    """

    if downloader is None and not contact_email:
        raise ValueError("SEC downloads require contact_email for the User-Agent")

    existing = {}
    for manifest_path in sorted((output_root / "sec_nmfp").glob("*.manifest.json")):
        try:
            existing[load_snapshot_manifest(manifest_path).sha256] = manifest_path
        except ValueError:
            # A manifest that no longer describes its bytes is not evidence that
            # the archive is present. Re-fetch rather than trust it.
            continue

    updated = []
    for index, record in enumerate(records):
        if not record.url.lower().startswith("https://www.sec.gov/"):
            raise ValueError(
                f"Form N-MFP URL must be an official https://www.sec.gov/ URL: "
                f"{record.url}"
            )
        if not recheck and record.sha256:
            if record.refusals or record.sha256 in existing:
                updated.append(record)
                continue
        if index and pause_seconds:
            sleep(pause_seconds)
        payload = (
            downloader(record.url)
            if downloader is not None
            else _download_sec(record.url, contact_email)
        )
        digest = hashlib.sha256(payload).hexdigest()
        if record.sha256 and digest != record.sha256:
            raise ValueError(
                f"{record.url} no longer matches its recorded digest: manifest "
                f"declares {record.sha256}, download is {digest}. These archives "
                "are immutable snapshots; a changed digest is a changed source, "
                "not a stale cache"
            )
        refusals = nmfp_schema_refusals(payload)
        retrieved_at = record.first_retrieved_at or datetime.now(
            timezone.utc
        ).isoformat()
        if not refusals:
            artifact = _save_snapshot(
                source_id="sec_nmfp",
                url=record.url,
                payload=payload,
                output_root=output_root,
                suffix="zip",
            )
            retrieved_at = record.first_retrieved_at or artifact.retrieved_at
        updated.append(
            replace(
                record,
                sha256=digest,
                byte_count=len(payload),
                first_retrieved_at=retrieved_at,
                refusals=refusals,
            )
        )
    return tuple(updated)


def _artifact_payload(artifact: SnapshotArtifact) -> bytes:
    payload = artifact.path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != artifact.sha256:
        raise ValueError(
            f"snapshot checksum mismatch for {artifact.path}: expected {artifact.sha256}"
        )
    return payload


def load_snapshot_manifest(path: Path) -> SnapshotArtifact:
    """Rehydrate and verify a raw snapshot from its saved manifest."""

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        artifact = SnapshotArtifact(
            source_id=str(manifest["source_id"]),
            path=Path(manifest["path"]),
            retrieved_at=str(manifest["retrieved_at"]),
            sha256=str(manifest["sha256"]),
            url=str(manifest["url"]),
            byte_count=int(manifest["byte_count"]),
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid snapshot manifest {path}: {exc}") from exc
    payload = _artifact_payload(artifact)
    if len(payload) != artifact.byte_count:
        raise ValueError(
            f"snapshot byte count mismatch for {artifact.path}: "
            f"expected {artifact.byte_count}"
        )
    retrieved_at = datetime.fromisoformat(
        artifact.retrieved_at.replace("Z", "+00:00")
    )
    if retrieved_at.tzinfo is None or retrieved_at.utcoffset() is None:
        raise ValueError(f"snapshot manifest {path} has a naive retrieved_at")
    return artifact


def _next_weekday(value: date, days: int) -> date:
    current = value
    remaining = days
    while remaining:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def _nyfed_rows(artifact: SnapshotArtifact, payload: bytes):
    from zoneinfo import ZoneInfo
    from .data import PointInTimeObservation

    parsed = json.loads(payload)
    records = parsed.get("refRates")
    if not isinstance(records, list):
        raise ValueError("New York Fed response does not contain a refRates list")
    parsed_url = urlparse(artifact.url)
    path_parts = parsed_url.path.rstrip("/").split("/")
    query = parse_qs(parsed_url.query)
    observation_type = query.get("type", [None])[0]
    if len(path_parts) < 2 or observation_type not in {"rate", "volume"}:
        raise ValueError(f"unsupported New York Fed artifact ID: {artifact.source_id}")
    rate_name = path_parts[-2].upper()
    if artifact.source_id != f"nyfed_{rate_name.lower()}":
        raise ValueError(
            f"New York Fed artifact source {artifact.source_id!r} does not match URL"
        )
    rate_fields = {
        "percentRate": rate_name,
        "percentPercentile1": f"{rate_name}_p1",
        "percentPercentile25": f"{rate_name}_p25",
        "percentPercentile75": f"{rate_name}_p75",
        "percentPercentile99": f"{rate_name}_p99",
        # The API has used both spellings across response versions.
        "percentile1": f"{rate_name}_p1",
        "percentile25": f"{rate_name}_p25",
        "percentile75": f"{rate_name}_p75",
        "percentile99": f"{rate_name}_p99",
    }
    field_map = rate_fields if observation_type == "rate" else {
        "volumeInBillions": f"{rate_name}_volume"
    }
    rows = []
    retrieved = datetime.fromisoformat(artifact.retrieved_at.replace("Z", "+00:00"))
    for record_number, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"New York Fed record {record_number} is not an object")
        try:
            ref_date = date.fromisoformat(str(record["effectiveDate"]))
        except (KeyError, ValueError) as exc:
            raise ValueError(
                f"New York Fed record {record_number} has no valid effectiveDate"
            ) from exc
        # When the API does not expose an exact publication timestamp, apply the
        # registry's conservative finalized-rate convention uniformly.
        available_date = _next_weekday(ref_date, 1)
        declared_available_at = datetime.combine(
            available_date, time(15, 0), tzinfo=ZoneInfo("America/New_York")
        )
        # A snapshot retrieved before the conservative finalized time proves only
        # that the preliminary observation existed at retrieval.
        available_at = min(declared_available_at, retrieved)
        revision = str(record.get("revisionIndicator", "unknown")).strip() or "unknown"
        for raw_field, series_id in field_map.items():
            raw_value = record.get(raw_field)
            normalized = str(raw_value).strip() if raw_value is not None else ""
            if normalized.upper() in {"", "NA", "N/A", "."}:
                continue
            try:
                value = float(normalized.replace(",", ""))
            except ValueError as exc:
                raise ValueError(
                    f"New York Fed {raw_field} is not numeric in record {record_number}"
                ) from exc
            rows.append(
                PointInTimeObservation(
                    series_id=series_id,
                    ref_date=ref_date,
                    available_at=available_at,
                    value=value,
                    vintage_id=f"{artifact.retrieved_at}:{observation_type}:{revision}",
                    source_sha=artifact.sha256,
                )
            )
    return rows


def _fred_csv_payloads(payload: bytes) -> Iterable[bytes]:
    if not payload.startswith(b"PK"):
        return (payload,)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".csv"))
        return tuple(archive.read(name) for name in names)


def _fred_rows(artifact: SnapshotArtifact, payload: bytes):
    from .data import PointInTimeObservation

    available_at = datetime.fromisoformat(artifact.retrieved_at.replace("Z", "+00:00"))
    rows = []
    for content in _fred_csv_payloads(payload):
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        if not reader.fieldnames or "observation_date" not in reader.fieldnames:
            raise ValueError("FRED snapshot is not the expected CSV format")
        for record_number, record in enumerate(reader, start=2):
            try:
                ref_date = date.fromisoformat(record["observation_date"])
            except (KeyError, ValueError) as exc:
                raise ValueError(f"FRED row {record_number} has an invalid date") from exc
            for series_id in reader.fieldnames:
                if series_id == "observation_date":
                    continue
                raw_value = (record.get(series_id) or "").strip()
                if raw_value in {"", "."}:
                    continue
                try:
                    value = float(raw_value)
                except ValueError as exc:
                    raise ValueError(
                        f"FRED {series_id} is not numeric in row {record_number}"
                    ) from exc
                rows.append(
                    PointInTimeObservation(
                        series_id=series_id,
                        ref_date=ref_date,
                        available_at=available_at,
                        value=value,
                        vintage_id=artifact.retrieved_at,
                        source_sha=artifact.sha256,
                    )
                )
    return rows


def _treasury_rows(artifact: SnapshotArtifact, payload: bytes):
    from zoneinfo import ZoneInfo
    from .data import PointInTimeObservation

    parsed = json.loads(payload)
    records = parsed.get("data")
    if not isinstance(records, list):
        raise ValueError("Treasury Fiscal Data response does not contain a data list")
    totals = {}
    for record_number, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"Treasury record {record_number} is not an object")
        try:
            ref_date = date.fromisoformat(str(record["issue_date"]))
            record_date = date.fromisoformat(str(record["record_date"]))
            amount = float(str(record["offering_amt"]).replace(",", "")) / 1_000_000_000
        except (KeyError, ValueError) as exc:
            raise ValueError(
                f"Treasury record {record_number} lacks issue_date, record_date, or offering_amt"
            ) from exc
        key = (ref_date, record_date)
        totals[key] = totals.get(key, 0.0) + amount
    return [
        PointInTimeObservation(
            series_id="treasury_settlement",
            ref_date=ref_date,
            available_at=datetime.combine(
                record_date, time(23, 59), tzinfo=ZoneInfo("America/New_York")
            ),
            value=value,
            vintage_id=f"{record_date.isoformat()}:{artifact.retrieved_at}",
            source_sha=artifact.sha256,
        )
        for (ref_date, record_date), value in sorted(totals.items())
    ]


#: The value columns each N-MFP table contributes, mapped to the series they
#: feed. Module-level rather than local to `_sec_nmfp_rows` so the required
#: header below is derived from the mapping the parser actually reads.
NMFP_BALANCE_FIELDS = {
    "CASH": "mmf_cash",
    "TOTALVALUEPORTFOLIOSECURITIES": "mmf_portfolio_securities",
    "TOTALVALUEOTHERASSETS": "mmf_other_assets",
    "TOTALVALUELIABILITIES": "mmf_liabilities",
    "NETASSETOFSERIES": "mmf_net_assets",
}

NMFP_FLOW_FIELDS = {
    "DAILYGROSSSUBSCRIPTIONS": "mmf_gross_subscriptions",
    "DAILYGROSSREDEMPTIONS": "mmf_gross_redemptions",
}

#: Every column the adapter reads, stated once at the parser boundary. A
#: renamed column otherwise looks exactly like an absent value to `record.get`
#: and can silently erase or misclassify a series.
NMFP_REQUIRED_COLUMNS = {
    "NMFP_SUBMISSION.tsv": frozenset(
        {
            "ACCESSION_NUMBER",
            "SERIESID",
            "REPORTDATE",
            # Which of two submissions for one (series, report date) supersedes
            # the other. Without a filing order the adapter cannot tell an
            # amendment from a second original and has to sum them, which is
            # the double count `_resolve_nmfp_submissions` exists to prevent.
            "FILING_DATE",
            # Recorded, never filtered on. A cross-section is admitted or
            # excluded on its reporting-entity count alone; the submission-type
            # mix is carried alongside that decision so a reader can see whether
            # an excluded month was a straggler cohort or something else.
            "SUBMISSIONTYPE",
        }
    ),
    "NMFP_SERIESLEVELINFO.tsv": (
        frozenset({"ACCESSION_NUMBER"}) | frozenset(NMFP_BALANCE_FIELDS)
    ),
    "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv": (
        frozenset({"ACCESSION_NUMBER", "DAILYSHAREHOLDERFLOWDATE"})
        | frozenset(NMFP_FLOW_FIELDS)
    ),
    "NMFP_SCHPORTFOLIOSECURITIES.tsv": frozenset(
        {
            "ACCESSION_NUMBER",
            "INVESTMENTCATEGORY",
            "INCLUDINGVALUEOFANYSPONSORSUPP",
            "NAMEOFISSUER",
            "TITLEOFISSUER",
            "BRIEFDESCRIPTION",
        }
    ),
}


def _nmfp_table(archive: zipfile.ZipFile, name: str):
    """Open one N-MFP table only when its header supports faithful parsing."""

    try:
        payload = archive.read(name)
    except KeyError as exc:
        raise ValueError(f"SEC Form N-MFP ZIP lacks required table {name}") from exc
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), delimiter="\t")
    # A header-only table is valid and remains empty. A zero-byte table has no
    # header, so all of its required columns are correctly reported missing.
    missing = NMFP_REQUIRED_COLUMNS[name] - frozenset(reader.fieldnames or ())
    if missing:
        raise ValueError(
            f"SEC Form N-MFP table {name} lacks required columns "
            f"{', '.join(sorted(missing))}"
        )
    return reader


def _nmfp_number(raw: object, field: str) -> Optional[float]:
    normalized = str(raw).strip() if raw is not None else ""
    if normalized.upper() in {"", "NA", "N/A", "."}:
        return None
    try:
        return float(normalized.replace(",", ""))
    except ValueError as exc:
        raise ValueError(f"SEC Form N-MFP {field} value is not numeric: {raw!r}") from exc


def _nmfp_date(raw: object, field: str) -> date:
    try:
        return datetime.strptime(str(raw).strip(), "%d-%b-%Y").date()
    except ValueError as exc:
        raise ValueError(f"SEC Form N-MFP {field} is not DD-MON-YYYY: {raw!r}") from exc


#: What `_sec_nmfp_rows` counts as one reporting entity, named here so the
#: registry's `cross_section.entity_unit` can be checked against it rather than
#: merely agreeing with it by coincidence -- the same twin-declaration hole
#: `AvailableAtDerivationTests` closed for `available_at`. A fund series is the
#: filing unit of Form N-MFP; an amendment is a second accession for the same
#: series, so counting accessions would count an amended series twice.
NMFP_ENTITY_UNIT = "series_id"


def _resolve_nmfp_submissions(submissions):
    """Pick the one submission that speaks for each (series, report date).

    Form N-MFP is filed per series per month, so a series that appears twice for
    one report date has been amended: `N-MFP3/A` is a second accession restating
    the first, not a second fund. `_sec_nmfp_rows` aggregates by adding every
    accession's values together, which is right across series and wrong across a
    series and its own amendment -- it books the restated balance sheet on top of
    the one it replaces. A quarterly extract and the monthly extract that follows
    it both carry such pairs, so the backfill turns a case that never arose on one
    archive into the normal one.

    The winner is the latest `FILING_DATE`, because that is the archive's own
    statement of filing order and it is what makes an amendment an amendment.
    `SUBMISSIONTYPE` is deliberately not the rule: it distinguishes one amendment
    from an original but not the second amendment from the first, and a rule that
    silently stops discriminating is worse than one that never claimed to.
    `ACCESSION_NUMBER` breaks a same-day tie so the choice is deterministic rather
    than dependent on row order in the file.

    Returns `(kept, superseded)`: the accession chosen for each pair, and the
    accessions it displaced. Displaced accessions are skipped by the value tables,
    not treated as unknown -- an unknown accession is a corrupt archive and still
    raises.
    """

    best = {}
    for accession, (series_id, report_date, filing_date) in submissions.items():
        key = (series_id, report_date)
        rank = (filing_date, accession)
        if key not in best or rank > best[key][0]:
            best[key] = (rank, accession)
    kept = {accession for _rank, accession in best.values()}
    return kept, frozenset(submissions) - kept


def _sec_nmfp_rows(artifact: SnapshotArtifact, payload: bytes):
    """Aggregate one SEC bulk extract without inventing absent holdings.

    Returns `(rows, entity_counts, submission_types)`. Each element of `rows`
    pairs an observation with the report date of the submission it came from --
    its cross-section -- which is not always its own `ref_date`: a daily
    shareholder-flow row is dated within the reporting month but belongs to that
    month's cross-section and stands or falls with it. `entity_counts` maps each
    cross-section to the number of distinct reporting entities that filed for it.
    `submission_types` maps each cross-section to how many submissions of each
    `SUBMISSIONTYPE` it carries, superseded ones included: it corroborates the
    coverage decision without participating in it.
    """

    from .data import PointInTimeObservation

    available_at = datetime.fromisoformat(artifact.retrieved_at.replace("Z", "+00:00"))
    totals = {}

    def add(section: date, series_id: str, ref_date: date, value: float) -> None:
        key = (section, series_id, ref_date)
        totals[key] = totals.get(key, 0.0) + value

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        submissions = {}
        entities = {}
        submission_types = {}
        for record in _nmfp_table(archive, "NMFP_SUBMISSION.tsv"):
            accession = (record.get("ACCESSION_NUMBER") or "").strip()
            if not accession:
                raise ValueError("SEC Form N-MFP submission lacks ACCESSION_NUMBER")
            entity = (record.get("SERIESID") or "").strip()
            if not entity:
                raise ValueError(
                    f"SEC Form N-MFP submission {accession} lacks SERIESID, so its "
                    "cross-section cannot be counted in reporting entities"
                )
            report_date = _nmfp_date(record.get("REPORTDATE"), "REPORTDATE")
            filing_date = _nmfp_date(record.get("FILING_DATE"), "FILING_DATE")
            entry = (entity, report_date, filing_date)
            if accession in submissions and submissions[accession] != entry:
                raise ValueError(
                    f"SEC Form N-MFP accession {accession} describes two submissions"
                )
            submissions[accession] = entry
            entities.setdefault(report_date, set()).add(entity)
            submission_type = (record.get("SUBMISSIONTYPE") or "").strip() or "(blank)"
            mix = submission_types.setdefault(report_date, {})
            mix[submission_type] = mix.get(submission_type, 0) + 1

        kept_accessions, superseded = _resolve_nmfp_submissions(submissions)
        reports = {
            accession: submissions[accession][1] for accession in kept_accessions
        }

        for record in _nmfp_table(archive, "NMFP_SERIESLEVELINFO.tsv"):
            accession = (record.get("ACCESSION_NUMBER") or "").strip()
            if accession in superseded:
                continue
            if accession not in reports:
                raise ValueError(f"SEC Form N-MFP series row has unknown accession {accession}")
            section = reports[accession]
            for raw_field, series_id in NMFP_BALANCE_FIELDS.items():
                value = _nmfp_number(record.get(raw_field), raw_field)
                if value is not None:
                    add(section, series_id, section, value / 1_000_000_000)

        for record in _nmfp_table(archive, "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv"):
            accession = (record.get("ACCESSION_NUMBER") or "").strip()
            if accession in superseded:
                continue
            if accession not in reports:
                raise ValueError(
                    f"SEC Form N-MFP flow row has unknown accession {accession}"
                )
            # A daily flow date is its own ref_date, but the submission it was
            # filed under is its cross-section. Deriving the cross-section from
            # the flow date instead would be a guess that happens to be right on
            # this extract, and wrong the first time a filing reports a day
            # outside its own reporting month.
            section = reports[accession]
            ref_date = _nmfp_date(
                record.get("DAILYSHAREHOLDERFLOWDATE"),
                "DAILYSHAREHOLDERFLOWDATE",
            )
            values = {}
            for raw_field, series_id in NMFP_FLOW_FIELDS.items():
                value = _nmfp_number(record.get(raw_field), raw_field)
                if value is not None:
                    values[series_id] = value / 1_000_000_000
                    add(section, series_id, ref_date, values[series_id])
            if len(values) == 2:
                add(
                    section,
                    "mmf_net_flow",
                    ref_date,
                    values["mmf_gross_subscriptions"]
                    - values["mmf_gross_redemptions"],
                )

        for record in _nmfp_table(archive, "NMFP_SCHPORTFOLIOSECURITIES.tsv"):
            accession = (record.get("ACCESSION_NUMBER") or "").strip()
            if accession in superseded:
                continue
            if accession not in reports:
                raise ValueError(
                    f"SEC Form N-MFP security row has unknown accession {accession}"
                )
            value = _nmfp_number(
                record.get("INCLUDINGVALUEOFANYSPONSORSUPP"),
                "INCLUDINGVALUEOFANYSPONSORSUPP",
            )
            if value is None:
                continue
            section = reports[accession]
            category = (record.get("INVESTMENTCATEGORY") or "").strip()
            if "Repurchase Agreement" in category:
                add(section, "mmf_repo_holdings", section, value / 1_000_000_000)
                counterparty = " ".join(
                    str(record.get(field) or "")
                    for field in ("NAMEOFISSUER", "TITLEOFISSUER", "BRIEFDESCRIPTION")
                ).upper()
                if "FEDERAL RESERVE" in counterparty:
                    add(section, "mmf_on_rrp", section, value / 1_000_000_000)
            elif category == "U.S. Treasury Debt":
                add(section, "mmf_treasury_holdings", section, value / 1_000_000_000)

    rows = [
        (
            section,
            PointInTimeObservation(
                series_id=series_id,
                ref_date=ref_date,
                available_at=available_at,
                value=value,
                vintage_id=artifact.retrieved_at,
                source_sha=artifact.sha256,
            ),
        )
        for (section, series_id, ref_date), value in sorted(totals.items())
    ]
    return (
        rows,
        {section: len(members) for section, members in entities.items()},
        submission_types,
    )


def load_source_registry(registry_path: Path = DEFAULT_SOURCE_REGISTRY):
    """Read the source registry, reporting a bad path or bad JSON the same way."""

    try:
        return json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load source registry: {exc}") from exc


@dataclass(frozen=True)
class ParsedSnapshots:
    """Admitted observations, plus every cross-section the coverage floor saw.

    `coverage` holds one entry per cross-section, admitted or not, so a caller
    can report the exclusions rather than infer them from what is absent. An
    exclusion that leaves no trace is the silent drop this guard exists to
    replace.
    """

    rows: tuple
    coverage: tuple


def parse_snapshots(
    artifacts: Iterable[SnapshotArtifact],
    *,
    registry: Optional[Mapping[str, Mapping[str, object]]] = None,
    registry_path: Path = DEFAULT_SOURCE_REGISTRY,
) -> ParsedSnapshots:
    """Parse immutable snapshots, applying each source's declared coverage floor.

    A cross-sectional source can emit a `ref_date` whose rows are all present,
    parseable and self-consistent while representing a small fraction of its
    universe -- an amendment and straggler month in a quarterly bulk extract, in
    the case that motivated this. Such a cross-section is excluded from the
    panel and recorded in `coverage`. It is not raised on: a partial month is
    the expected shape of the source, not a fault.
    """

    from .data import CrossSectionCoverage, declared_coverage_floor

    if registry is None:
        registry = load_source_registry(registry_path)

    candidates = []
    coverage = []
    for artifact in artifacts:
        payload = _artifact_payload(artifact)
        artifact = replace(
            artifact,
            source_id=LEGACY_SOURCE_IDS.get(artifact.source_id, artifact.source_id),
        )
        # `None` means "this source publishes no cross-section", which is not
        # the same as "this source published an empty one". An empty extract
        # must not satisfy a coverage floor vacuously.
        entity_counts = None
        submission_types = {}
        if artifact.source_id.startswith("nyfed_"):
            parsed_rows = [(None, row) for row in _nyfed_rows(artifact, payload)]
        elif artifact.source_id == "fred_macro_latest_vintage":
            parsed_rows = [(None, row) for row in _fred_rows(artifact, payload)]
        elif artifact.source_id == "treasury_auctions":
            parsed_rows = [(None, row) for row in _treasury_rows(artifact, payload)]
        elif artifact.source_id == "sec_nmfp":
            parsed_rows, entity_counts, submission_types = _sec_nmfp_rows(
                artifact, payload
            )
            _check_declared_entity_unit(
                artifact.source_id, registry, NMFP_ENTITY_UNIT
            )
        else:
            raise ValueError(f"no point-in-time parser for {artifact.source_id}")
        retrieved_at = datetime.fromisoformat(
            artifact.retrieved_at.replace("Z", "+00:00")
        )

        admitted = None
        if entity_counts is not None:
            try:
                source = registry[artifact.source_id]
            except KeyError as exc:
                raise ValueError(
                    f"snapshots have no source-registry entry: [{artifact.source_id!r}]"
                ) from exc
            entity_unit, floor = declared_coverage_floor(artifact.source_id, source)
            admitted = {
                section for section, count in entity_counts.items() if count >= floor
            }
            section_rows = {}
            for section, _row in parsed_rows:
                section_rows[section] = section_rows.get(section, 0) + 1
            coverage.extend(
                CrossSectionCoverage(
                    source_id=artifact.source_id,
                    ref_date=section,
                    entity_unit=entity_unit,
                    entity_count=count,
                    declared_floor=floor,
                    admitted=section in admitted,
                    row_count=section_rows.get(section, 0),
                    submission_types=tuple(
                        sorted(submission_types.get(section, {}).items())
                    ),
                )
                for section, count in sorted(entity_counts.items())
            )

        kept = [
            row
            for section, row in parsed_rows
            if admitted is None or section in admitted
        ]
        if admitted is not None:
            # Contributions to one cell are aggregated across every admitted
            # cross-section, which is what this adapter did before the floor
            # existed. Splitting the aggregation by cross-section is how the
            # floor decides what to admit; it is not a change to what an
            # admitted cell means. Left unmerged, two admitted cross-sections
            # that both report a shareholder-flow date would reach the revision
            # logic as two vintages of the same cell with one availability
            # timestamp, and be rejected as unorderable.
            merged = {}
            for row in kept:
                key = (row.series_id, row.ref_date)
                previous = merged.get(key)
                merged[key] = (
                    row if previous is None
                    else replace(row, value=previous.value + row.value)
                )
            kept = [merged[key] for key in sorted(merged)]

        candidates.extend((retrieved_at, row) for row in kept)

    # A later snapshot containing the same value is not a revision. If its value
    # changed but the source exposes no historical revision timestamp, retrieval
    # is the earliest defensible availability for that newly observed vintage.
    rows = []
    prior = {}
    for retrieved_at, row in sorted(
        candidates,
        key=lambda item: (
            item[0], item[1].series_id, item[1].ref_date, item[1].vintage_id
        ),
    ):
        key = (row.series_id, row.ref_date)
        previous = prior.get(key)
        if previous is not None and row.value == previous.value:
            continue
        if previous is not None and row.available_at <= previous.available_at:
            if retrieved_at <= previous.available_at:
                raise ValueError(
                    f"cannot order vintages for {row.series_id} {row.ref_date}: "
                    "changed values have no increasing observation time"
                )
            row = replace(row, available_at=retrieved_at)
        rows.append(row)
        prior[key] = row
    rows.sort(key=lambda row: (row.available_at, row.series_id, row.ref_date, row.vintage_id))
    return ParsedSnapshots(rows=tuple(rows), coverage=tuple(coverage))


def _check_declared_entity_unit(
    source_id: str,
    registry: Mapping[str, Mapping[str, object]],
    counted_unit: str,
) -> None:
    """Fail if the registry names a reporting entity the adapter does not count.

    The declaration and the adapter are two statements of the same fact, and
    nothing else makes them agree. A registry that said `entity_unit: "cik"`
    would silently be guarded by a series count instead -- a floor measured in
    the wrong unit, which is how a bound comes to be wrong in a way no test on
    either side can see.
    """

    source = registry.get(source_id)
    if not isinstance(source, Mapping):
        return
    declaration = source.get("cross_section")
    if not isinstance(declaration, Mapping):
        return
    declared = declaration.get("entity_unit")
    if declared != counted_unit:
        raise ValueError(
            f"{source_id}: registry declares cross_section.entity_unit "
            f"{declared!r}, but the adapter counts {counted_unit!r}"
        )


def observations_from_snapshots(
    artifacts: Iterable[SnapshotArtifact],
    *,
    registry: Optional[Mapping[str, Mapping[str, object]]] = None,
    registry_path: Path = DEFAULT_SOURCE_REGISTRY,
):
    """Parse supported immutable snapshots into canonical long observations."""

    return list(
        parse_snapshots(
            artifacts, registry=registry, registry_path=registry_path
        ).rows
    )


def build_point_in_time_snapshot(
    artifacts: Iterable[SnapshotArtifact],
    output_path: Path,
    *,
    created_at: Optional[datetime] = None,
    registry_path: Path = DEFAULT_SOURCE_REGISTRY,
) -> PanelArtifact:
    """Create a frozen, checksummed canonical panel from raw snapshot artifacts."""

    materialized = list(artifacts)
    if not materialized:
        raise ValueError("at least one raw snapshot is required")
    registry = load_source_registry(registry_path)
    parsed = parse_snapshots(materialized, registry=registry)
    rows = list(parsed.rows)
    if not rows:
        raise ValueError("raw snapshots produced no point-in-time observations")
    unknown_sources = sorted(
        {item.source_id for item in materialized if item.source_id not in registry}
    )
    if unknown_sources:
        raise ValueError(f"snapshots have no source-registry entry: {unknown_sources}")
    selected_registry = {
        source_id: registry[source_id]
        for source_id in sorted({item.source_id for item in materialized})
    }
    from .data import (
        expected_ref_dates_from_registry,
        validate_accounting_identities,
        validate_publication_gaps,
        write_point_in_time_audit_report,
    )

    validate_publication_gaps(rows, selected_registry)
    accounting_residuals = validate_accounting_identities(rows, selected_registry)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(("series_id", "ref_date", "available_at", "value", "vintage_id", "source_sha"))
    for row in rows:
        writer.writerow(
            (
                row.series_id,
                row.ref_date.isoformat(),
                row.available_at.isoformat(),
                format(row.value, ".15g"),
                row.vintage_id,
                row.source_sha,
            )
        )
    payload = buffer.getvalue().encode("utf-8")
    timestamp = created_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("processed snapshot created_at must include a UTC offset")
    _atomic_write(output_path, payload)
    quality_report_path = output_path.with_suffix(output_path.suffix + ".quality.json")
    expected_dates = expected_ref_dates_from_registry(rows, selected_registry)
    write_point_in_time_audit_report(
        rows,
        quality_report_path,
        expected_ref_dates=expected_dates,
        excluded_cross_sections=[
            item for item in parsed.coverage if not item.admitted
        ],
    )
    quality_report_sha256 = hashlib.sha256(quality_report_path.read_bytes()).hexdigest()
    artifact = PanelArtifact(
        path=output_path,
        created_at=timestamp.isoformat(),
        sha256=hashlib.sha256(payload).hexdigest(),
        row_count=len(rows),
        source_shas=tuple(sorted({item.sha256 for item in materialized})),
        raw_snapshots=tuple(item.as_dict() for item in materialized),
        quality_report_path=quality_report_path.resolve(),
        quality_report_sha256=quality_report_sha256,
        accounting_residuals=accounting_residuals,
    )
    _atomic_write(
        output_path.with_suffix(output_path.suffix + ".manifest.json"),
        json.dumps(artifact.as_dict(), indent=2, sort_keys=True).encode("utf-8") + b"\n",
    )
    return artifact
