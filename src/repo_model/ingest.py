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


def _nmfp_table(archive: zipfile.ZipFile, name: str):
    try:
        payload = archive.read(name)
    except KeyError as exc:
        raise ValueError(f"SEC Form N-MFP ZIP lacks required table {name}") from exc
    return csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), delimiter="\t")


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


def _sec_nmfp_rows(artifact: SnapshotArtifact, payload: bytes):
    """Aggregate one SEC bulk extract without inventing absent holdings."""

    from .data import PointInTimeObservation

    available_at = datetime.fromisoformat(artifact.retrieved_at.replace("Z", "+00:00"))
    totals = {}

    def add(series_id: str, ref_date: date, value: float) -> None:
        key = (series_id, ref_date)
        totals[key] = totals.get(key, 0.0) + value

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        reports = {}
        for record in _nmfp_table(archive, "NMFP_SUBMISSION.tsv"):
            accession = (record.get("ACCESSION_NUMBER") or "").strip()
            if not accession:
                raise ValueError("SEC Form N-MFP submission lacks ACCESSION_NUMBER")
            report_date = _nmfp_date(record.get("REPORTDATE"), "REPORTDATE")
            if accession in reports and reports[accession] != report_date:
                raise ValueError(f"SEC Form N-MFP accession {accession} has two report dates")
            reports[accession] = report_date

        balance_fields = {
            "CASH": "mmf_cash",
            "TOTALVALUEPORTFOLIOSECURITIES": "mmf_portfolio_securities",
            "TOTALVALUEOTHERASSETS": "mmf_other_assets",
            "TOTALVALUELIABILITIES": "mmf_liabilities",
            "NETASSETOFSERIES": "mmf_net_assets",
        }
        for record in _nmfp_table(archive, "NMFP_SERIESLEVELINFO.tsv"):
            accession = (record.get("ACCESSION_NUMBER") or "").strip()
            if accession not in reports:
                raise ValueError(f"SEC Form N-MFP series row has unknown accession {accession}")
            for raw_field, series_id in balance_fields.items():
                value = _nmfp_number(record.get(raw_field), raw_field)
                if value is not None:
                    add(series_id, reports[accession], value / 1_000_000_000)

        flow_fields = {
            "DAILYGROSSSUBSCRIPTIONS": "mmf_gross_subscriptions",
            "DAILYGROSSREDEMPTIONS": "mmf_gross_redemptions",
        }
        for record in _nmfp_table(archive, "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv"):
            ref_date = _nmfp_date(
                record.get("DAILYSHAREHOLDERFLOWDATE"),
                "DAILYSHAREHOLDERFLOWDATE",
            )
            values = {}
            for raw_field, series_id in flow_fields.items():
                value = _nmfp_number(record.get(raw_field), raw_field)
                if value is not None:
                    values[series_id] = value / 1_000_000_000
                    add(series_id, ref_date, values[series_id])
            if len(values) == 2:
                add(
                    "mmf_net_flow",
                    ref_date,
                    values["mmf_gross_subscriptions"]
                    - values["mmf_gross_redemptions"],
                )

        for record in _nmfp_table(archive, "NMFP_SCHPORTFOLIOSECURITIES.tsv"):
            accession = (record.get("ACCESSION_NUMBER") or "").strip()
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
            ref_date = reports[accession]
            category = (record.get("INVESTMENTCATEGORY") or "").strip()
            if "Repurchase Agreement" in category:
                add("mmf_repo_holdings", ref_date, value / 1_000_000_000)
                counterparty = " ".join(
                    str(record.get(field) or "")
                    for field in ("NAMEOFISSUER", "TITLEOFISSUER", "BRIEFDESCRIPTION")
                ).upper()
                if "FEDERAL RESERVE" in counterparty:
                    add("mmf_on_rrp", ref_date, value / 1_000_000_000)
            elif category == "U.S. Treasury Debt":
                add("mmf_treasury_holdings", ref_date, value / 1_000_000_000)

    return [
        PointInTimeObservation(
            series_id=series_id,
            ref_date=ref_date,
            available_at=available_at,
            value=value,
            vintage_id=artifact.retrieved_at,
            source_sha=artifact.sha256,
        )
        for (series_id, ref_date), value in sorted(totals.items())
    ]


def observations_from_snapshots(
    artifacts: Iterable[SnapshotArtifact],
):
    """Parse supported immutable snapshots into canonical long observations."""

    candidates = []
    for artifact in artifacts:
        payload = _artifact_payload(artifact)
        if artifact.source_id.startswith("nyfed_"):
            parsed_rows = _nyfed_rows(artifact, payload)
        elif artifact.source_id == "fred_macro_latest_vintage":
            parsed_rows = _fred_rows(artifact, payload)
        elif artifact.source_id == "treasury_auctions":
            parsed_rows = _treasury_rows(artifact, payload)
        elif artifact.source_id == "sec_nmfp":
            parsed_rows = _sec_nmfp_rows(artifact, payload)
        else:
            raise ValueError(f"no point-in-time parser for {artifact.source_id}")
        retrieved_at = datetime.fromisoformat(
            artifact.retrieved_at.replace("Z", "+00:00")
        )
        candidates.extend((retrieved_at, row) for row in parsed_rows)

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
    return rows


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
    rows = observations_from_snapshots(materialized)
    if not rows:
        raise ValueError("raw snapshots produced no point-in-time observations")
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load source registry: {exc}") from exc
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
        rows, quality_report_path, expected_ref_dates=expected_dates
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
