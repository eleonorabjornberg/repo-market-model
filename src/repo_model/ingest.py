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
    accounting_identities: Mapping[str, object]

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
            # Renamed from `accounting_residuals`, 8 Sep 2026. A residual is
            # what an identity produces when it evaluates; it says nothing
            # about the reference dates where it could not. The value is now
            # a verdict per identity, and it reads `held` only when nothing
            # was left unchecked.
            "accounting_identities": {
                key: evaluation.as_dict()
                for key, evaluation in sorted(self.accounting_identities.items())
            },
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


#: The two things that can be wrong with an archive, which are not the same
#: claim about the same file and must not be recorded as one.
#:
#: `UNREADABLE` -- a table the archive *does* carry has a column the adapter
#: reads under a changed name, or the bytes are not a ZIP at all. That failure
#: is silent: `record.get()` returns `None`, the row is skipped, and the archive
#: parses "successfully" while contributing a partial balance sheet that
#: satisfies the identity because both sides lost the same rows. Nothing
#: downstream can see it, so the whole archive is refused.
#:
#: `ABSENT_FIELDS` -- a table is simply not in the archive. That is loud, it is
#: attributable to named panel fields, and its only consequence is that those
#: fields have no observation for this archive. The panel already represents
#: that state, because absent is not zero and never has been. So it costs its
#: own fields and nothing else.
REFUSAL_UNREADABLE = "unreadable"
REFUSAL_ABSENT_FIELDS = "absent_fields"


@dataclass(frozen=True)
class ArchiveRefusal:
    """One thing the parser cannot get from an archive, and what it costs.

    `kind` is `REFUSAL_UNREADABLE` or `REFUSAL_ABSENT_FIELDS`. `fields` names
    the panel series an `ABSENT_FIELDS` entry costs, so the manifest records the
    consequence and not only the cause: a reader should not have to know which
    table supplies `mmf_net_flow` to see that this archive has none.
    """

    kind: str
    detail: str
    table: str = ""
    fields: tuple = ()

    def as_dict(self) -> Mapping[str, object]:
        return {
            "kind": self.kind,
            "table": self.table,
            "fields": list(self.fields),
            "detail": self.detail,
        }

    @classmethod
    def from_mapping(cls, entry: object) -> "ArchiveRefusal":
        if not isinstance(entry, Mapping):
            raise ValueError(
                "N-MFP archive manifest refusal must be an object naming its "
                f"kind, not {entry!r}. A bare string cannot distinguish an "
                "archive that is unreadable from one that merely lacks a table, "
                "and those are different claims about the same file"
            )
        kind = str(entry.get("kind") or "")
        if kind not in {REFUSAL_UNREADABLE, REFUSAL_ABSENT_FIELDS}:
            raise ValueError(
                f"N-MFP archive manifest refusal has unknown kind {kind!r}; "
                f"expected {REFUSAL_UNREADABLE!r} or {REFUSAL_ABSENT_FIELDS!r}"
            )
        return cls(
            kind=kind,
            detail=str(entry.get("detail") or ""),
            table=str(entry.get("table") or ""),
            fields=tuple(str(item) for item in entry.get("fields") or ()),
        )


@dataclass(frozen=True)
class ArchiveRecord:
    """One immutable Form N-MFP archive, as the committed manifest records it.

    `sha256` and `byte_count` identify the bytes; `url` says where they came
    from; `first_retrieved_at` says when the digest was first observed here. The
    bytes themselves stay out of git.

    `refusals` is the parser's own verdict on the archive, computed by running
    `nmfp_schema_refusals` over the downloaded bytes rather than typed in by
    hand. It holds `ArchiveRefusal` records rather than strings because refusal
    is per-table: an archive missing a whole table is still read for every field
    the tables it does carry supply. Recording the verdict this way is what
    keeps "never existed", "not downloaded yet", "downloaded, read, and short
    three fields" and "downloaded, and unreadable" four visibly different states
    in a fresh checkout instead of two.
    """

    url: str
    sha256: str = ""
    byte_count: int = 0
    first_retrieved_at: str = ""
    refusals: tuple = ()

    @property
    def unreadable(self) -> tuple:
        """The refusals that condemn the whole archive, if any."""

        return tuple(item for item in self.refusals if item.kind == REFUSAL_UNREADABLE)

    @property
    def absent_fields(self) -> tuple:
        """Every panel series this archive carries no table for."""

        fields = set()
        for item in self.refusals:
            if item.kind == REFUSAL_ABSENT_FIELDS:
                fields.update(item.fields)
        return tuple(sorted(fields))

    @property
    def admitted(self) -> bool:
        """True for an archive that was fetched and can be read faithfully.

        An unfetched record is neither admitted nor refused, and must not be
        reported as either: `sha256` is empty precisely because nobody has
        looked yet. An archive missing a table *is* admitted -- it supplies
        every field its remaining tables supply, and `absent_fields` says which
        ones it does not.
        """

        return bool(self.sha256) and not self.unreadable

    def as_dict(self) -> Mapping[str, object]:
        return {
            "url": self.url,
            "sha256": self.sha256,
            "byte_count": self.byte_count,
            "first_retrieved_at": self.first_retrieved_at,
            "refusals": [item.as_dict() for item in self.refusals],
        }


def nmfp_schema_refusals(payload: bytes) -> tuple:
    """What the parser cannot get from this archive, per table, or nothing.

    Derived from `NMFP_REQUIRED_COLUMNS` and `NMFP_TABLE_FIELDS`, the same
    declarations the parser reads, so the manifest cannot record a verdict the
    parser disagrees with. The difference is only that a parse raises on the
    first problem, which is right for a parse and wrong for a report: an archive
    from a schema the project has never seen should name everything it is
    missing in one pass.

    The verdict is per table. An absent table costs the panel fields that table
    supplies and is recorded as `REFUSAL_ABSENT_FIELDS`. A table that is present
    with a column the adapter reads missing is `REFUSAL_UNREADABLE` and refuses
    the whole archive, because a renamed column is indistinguishable from an
    absent value at `record.get()` and produces a silently partial series. The
    spine table is the one exception to the first rule: without
    `NMFP_SUBMISSION.tsv` no row can be attributed to a series or a report date,
    so its absence is unreadable rather than a cost in fields.

    A schema check on headers is not a schema check on meaning. It cannot see a
    column that kept its name and changed its units, or a categorical whose
    vocabulary was rewritten -- `NMFP_INVESTMENT_CATEGORY_ERAS` is where the
    second of those is declared, and this function returns no refusal for it.
    """

    problems = []
    try:
        archive = zipfile.ZipFile(io.BytesIO(payload))
    except zipfile.BadZipFile:
        return (
            ArchiveRefusal(
                kind=REFUSAL_UNREADABLE, detail="not a valid ZIP archive"
            ),
        )
    with archive:
        names = frozenset(archive.namelist())
        for table, required in sorted(NMFP_REQUIRED_COLUMNS.items()):
            if table not in names:
                if table == NMFP_SPINE_TABLE:
                    problems.append(
                        ArchiveRefusal(
                            kind=REFUSAL_UNREADABLE,
                            table=table,
                            detail=(
                                f"lacks {table}, which attributes every other "
                                "row to a series and a report date; nothing in "
                                "the archive can be placed without it"
                            ),
                        )
                    )
                    continue
                fields = NMFP_TABLE_FIELDS[table]
                problems.append(
                    ArchiveRefusal(
                        kind=REFUSAL_ABSENT_FIELDS,
                        table=table,
                        fields=fields,
                        detail=(
                            f"lacks {table}; no observation of "
                            f"{', '.join(fields)} for this archive"
                        ),
                    )
                )
                continue
            header = archive.open(table).readline().decode("utf-8-sig")
            reader = csv.reader(io.StringIO(header.rstrip("\r\n")), delimiter="\t")
            columns = frozenset(next(reader, []))
            missing = required - columns
            if missing:
                problems.append(
                    ArchiveRefusal(
                        kind=REFUSAL_UNREADABLE,
                        table=table,
                        detail=(
                            f"{table} lacks required columns "
                            f"{', '.join(sorted(missing))}"
                        ),
                    )
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
                refusals=tuple(
                    ArchiveRefusal.from_mapping(item)
                    for item in entry.get("refusals") or ()
                ),
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
            "with an empty sha256 has never been fetched here. Refusal is per "
            "table, so a refusals entry says which of two different things "
            "happened. kind 'absent_fields' means the archive does not carry "
            "that table at all: it is read for everything its other tables "
            "supply, it is placed under data/raw/, and the named fields simply "
            "have no observation from it -- absent, not zero. kind 'unreadable' "
            "means a table the archive does carry has a column the adapter "
            "reads under a changed name, which is indistinguishable from an "
            "absent value at parse time and would yield a silently partial "
            "series; such an archive contributes no observations and is not "
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
    already recorded as unreadable -- re-downloading a hundred archives to
    re-derive a verdict that is written down is not politeness. `recheck=True`
    forces both, for the day the parser's requirements change and the verdicts
    have to be re-earned.

    A record whose only recorded refusals are absent tables is *not* skipped
    when its bytes are missing from `output_root`. That archive is admitted
    under the per-table rule and belongs in the raw tree; the recorded verdict
    says which fields it lacks, not that it should stay unfetched. This is what
    makes the widening of the refusal rule re-earn its own history without
    `--recheck` re-downloading the archives that are already here.

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
            if record.unreadable or record.sha256 in existing:
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
        if not any(item.kind == REFUSAL_UNREADABLE for item in refusals):
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


#: The FR 2004 Primary Dealer Statistics source. Named once so the parser, the
#: dispatch in `parse_snapshots` and the registry lookup cannot drift apart.
FR2004_SOURCE_ID = "nyfed_fr2004"

#: The three columns the export carries. Checked as a subset rather than an
#: equality: a column this adapter does not read is not a reason to refuse a
#: file, and a column it does read going missing is.
FR2004_COLUMNS = ("As Of Date", "Time Series", "Value (millions)")

#: What the New York Fed writes in place of a figure withheld for
#: confidentiality. It is neither zero nor a failed read, and the difference is
#: the whole of the handling below: it yields no observation at all, so the
#: identity that names the suppressed series comes back `not_evaluable` for that
#: week instead of `violated` against a fabricated zero.
FR2004_SUPPRESSED = "*"

#: The export is denominated in USD millions and `DATA.md` denominates the panel
#: in USD billions.
FR2004_MILLIONS_PER_BILLION = 1000.0


def _fr2004_rows(artifact: SnapshotArtifact, payload: bytes, registry):
    """Parse one FR 2004 Primary Dealer Statistics export.

    Three things this does not do, each of which is a way the same file has been
    read wrongly elsewhere:

    * It never takes a reference date from the file. Every row carries its own
      `As Of Date` and the tracked fixture mixes five of them, so a single date
      read once and applied to the whole export would misdate 441 of its 1540
      rows.
    * It never hard-codes availability. `days`, `available_time` and `timezone`
      come from the registry's `release_lag` on every call, which is what
      `AvailableAtDerivationTests` then holds the adapter to.
    * It never globs a series name. The declared `fields` are matched exactly,
      so `PDPOSGSC-L2C` is not read as `PDPOSGSC-L2`'s bucket and each era of
      the identity keeps exactly the terms it declares.
    """

    from zoneinfo import ZoneInfo
    from .contract import validate_release_lag
    from .data import PointInTimeObservation

    source = registry.get(FR2004_SOURCE_ID) if isinstance(registry, Mapping) else None
    if not isinstance(source, Mapping):
        raise ValueError(
            f"{FR2004_SOURCE_ID} is not declared in the source registry; the "
            f"adapter reads its fields and its release lag from there"
        )
    declared_fields = {str(field) for field in source.get("fields", ())}
    release_lag = source.get("release_lag")
    problems = validate_release_lag(FR2004_SOURCE_ID, release_lag)
    if problems:
        raise ValueError("; ".join(problems))
    if release_lag["basis"] != "ref_date":
        raise ValueError(
            f"{FR2004_SOURCE_ID}: availability is derived from the as-of date, so "
            f"the declared basis must be 'ref_date', got {release_lag['basis']!r}"
        )
    lag_days = int(release_lag["days"])
    available_time = time.fromisoformat(release_lag["available_time"])
    zone = ZoneInfo(release_lag["timezone"])

    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    if not reader.fieldnames or not set(FR2004_COLUMNS).issubset(reader.fieldnames):
        raise ValueError(
            "FR 2004 snapshot is not the expected CSV format; it must carry "
            f"the columns {list(FR2004_COLUMNS)}"
        )

    rows = []
    for record_number, record in enumerate(reader, start=2):
        series_id = (record.get("Time Series") or "").strip()
        # A series the registry does not declare is ignored, not parsed. The
        # export carries over 200 of them and this adapter makes no claim about
        # any but its fifteen -- the fourteen current series and `PDPOSGSC-G11`,
        # the over-eleven-year bucket retired in 2022, which the identity's
        # earlier eras are checked against and which no current export carries.
        if series_id not in declared_fields:
            continue
        raw_ref_date = (record.get("As Of Date") or "").strip()
        try:
            ref_date = date.fromisoformat(raw_ref_date)
        except ValueError as exc:
            raise ValueError(
                f"FR 2004 row {record_number} has no valid As Of Date; each row "
                f"carries its own reference date and none may be taken from the file"
            ) from exc
        raw_value = (record.get("Value (millions)") or "").strip()
        if raw_value == FR2004_SUPPRESSED:
            continue
        try:
            value = float(raw_value.replace(",", ""))
        except ValueError as exc:
            raise ValueError(
                f"FR 2004 {series_id} is not numeric in row {record_number}; "
                f"only {FR2004_SUPPRESSED!r} marks a suppressed value"
            ) from exc
        rows.append(
            PointInTimeObservation(
                series_id=series_id,
                ref_date=ref_date,
                available_at=datetime.combine(
                    _next_weekday(ref_date, lag_days), available_time, tzinfo=zone
                ),
                value=value / FR2004_MILLIONS_PER_BILLION,
                vintage_id=artifact.retrieved_at,
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


def _treasury_amount(record, field, record_number):
    """One Fiscal Data money field in USD billions, or `None` where withheld.

    Fiscal Data reports a field it does not yet have as the JSON **string**
    `"null"`, not as JSON null, so `float()` is the only thing that separates
    it from a figure and `record.get(field) is None` never fires. An auction
    that has not been held carries its results that way. Returning `0.0` there
    would publish an award nobody has made; returning nothing at all leaves the
    caller to decide what an absent leg means, which is the caller's decision
    to make and not this helper's.

    A field the payload does not carry at all is a different thing -- a renamed
    or dropped column -- and is refused by the caller rather than read as
    withheld.
    """

    raw = record.get(field)
    raw = "" if raw is None else str(raw).strip()
    if raw in {"", "null"}:
        return None
    try:
        return float(raw.replace(",", "")) / 1_000_000_000
    except ValueError as exc:
        raise ValueError(
            f"Treasury record {record_number} has a non-numeric {field}: {raw!r}"
        ) from exc


def _treasury_rows(artifact: SnapshotArtifact, payload: bytes):
    """Auction records to `treasury_settlement` and its declared components.

    The split -- which `security_type` settles into which component, which
    components sum to the aggregate, and the tolerance that sum is held to --
    is `src/repo_model/contract.py`'s, read from there. Restating any of it
    here would be a second definition, and the adapter would then be checked
    against its own copy.

    Three things a key can be missing, and only one of them is a zero:

    * **No auction of a kind.** 801 of the fixture's 1088 settlement dates
      have no coupon and 204 have no bill. That key gets no observation for
      the absent leg. A `0.0` would claim Treasury settled nothing of that
      kind that day, which is true, and would also be indistinguishable from
      a day the adapter failed to classify -- and it is the second reading
      the panel would have to trust.
    * **A result not yet awarded.** `soma_accepted` is `"null"` until the
      auction is held. The whole key loses `treasury_settlement_soma`, not
      just the unheld record's share: summing the rest publishes a partial
      award under the face of a complete one.
    * **A genuine zero award.** 1093 fixture records have `soma_accepted`
      `"0"`, and those are real. They sum like any other figure.
    """

    from zoneinfo import ZoneInfo
    from .contract import (
        TREASURY_SETTLEMENT_COMPONENTS,
        treasury_settlement_component,
    )
    from .data import PointInTimeObservation

    parsed = json.loads(payload)
    records = parsed.get("data")
    if not isinstance(records, list):
        raise ValueError("Treasury Fiscal Data response does not contain a data list")

    #: The components that sit outside `treasury_settlement`, mapped to the
    #: auction-record field each sums. Derived from the contract's own
    #: "is it inside the aggregate" flag, so a component moved across that line
    #: moves here with it.
    outside_aggregate = {
        series: field
        for series, (field, _types, inside) in TREASURY_SETTLEMENT_COMPONENTS.items()
        if not inside
    }

    totals = {}
    components = {}
    #: `(key, series)` pairs the snapshot withholds a contributing value for.
    #: Held separately from `components` because a key can have both a real
    #: figure and a withheld one, and the withheld one decides.
    withheld = set()
    for record_number, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"Treasury record {record_number} is not an object")
        try:
            ref_date = date.fromisoformat(str(record["issue_date"]))
            record_date = date.fromisoformat(str(record["record_date"]))
            auction_date = date.fromisoformat(str(record["auction_date"]))
            security_type = str(record["security_type"])
            amount = float(str(record["offering_amt"]).replace(",", "")) / 1_000_000_000
        except (KeyError, ValueError) as exc:
            raise ValueError(
                f"Treasury record {record_number} lacks issue_date, record_date, "
                f"auction_date, security_type, or offering_amt"
            ) from exc
        key = (ref_date, record_date)
        totals[key] = totals.get(key, 0.0) + amount

        public_leg = treasury_settlement_component(security_type)
        public_field = TREASURY_SETTLEMENT_COMPONENTS[public_leg][0]
        if public_field not in record:
            raise ValueError(
                f"Treasury record {record_number} does not carry {public_field}, "
                f"which {public_leg} sums"
            )
        public_amount = _treasury_amount(record, public_field, record_number)
        if public_amount is None:
            raise ValueError(
                f"Treasury record {record_number} withholds {public_field}: an "
                f"announced offering amount is known when the auction is announced"
            )
        components[(key, public_leg)] = (
            components.get((key, public_leg), 0.0) + public_amount
        )

        for series, field in outside_aggregate.items():
            if field not in record:
                raise ValueError(
                    f"Treasury record {record_number} does not carry {field}, "
                    f"which {series} sums"
                )
            value = _treasury_amount(record, field, record_number)
            if value is None:
                withheld.add((key, series))
                continue
            if record_date < auction_date:
                raise ValueError(
                    f"Treasury record {record_number} carries {field}, an auction "
                    f"result, dated {record_date.isoformat()} by record_date, which "
                    f"precedes its auction_date {auction_date.isoformat()}: a result "
                    f"dated before its auction"
                )
            components[(key, series)] = components.get((key, series), 0.0) + value

    emitted = {(key, "treasury_settlement"): value for key, value in totals.items()}
    emitted.update(
        {
            (key, series): value
            for (key, series), value in components.items()
            if (key, series) not in withheld
        }
    )
    return [
        PointInTimeObservation(
            series_id=series,
            ref_date=ref_date,
            available_at=datetime.combine(
                record_date, time(23, 59), tzinfo=ZoneInfo("America/New_York")
            ),
            value=value,
            vintage_id=f"{record_date.isoformat()}:{artifact.retrieved_at}",
            source_sha=artifact.sha256,
        )
        for ((ref_date, record_date), series), value in sorted(emitted.items())
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

#: The table that attributes every other row. It carries no panel field of its
#: own; it says which series and which report date each accession speaks for.
#: An archive without it cannot place a single value, so its absence is the one
#: absent table that refuses the archive rather than costing fields.
NMFP_SPINE_TABLE = "NMFP_SUBMISSION.tsv"

#: What each table costs the panel when the archive does not carry it. Derived
#: from the same field mappings the parser reads, so a field added to the
#: adapter cannot be left out of the accounting for an absent table.
#:
#: This is the declaration that makes refusal per-table rather than per-archive.
#: The 71 Form N-MFP archives filed before 2024-06-10 predate
#: `NMFP_DLYSHAREHOLDERFLOWREPORT`; the daily shareholder-flow data did not
#: exist, and discarding fourteen years of balance sheets and holdings over its
#: absence confuses "we have no flow observation for this month" with "we cannot
#: read this file".
NMFP_TABLE_FIELDS = {
    NMFP_SPINE_TABLE: (),
    "NMFP_SERIESLEVELINFO.tsv": tuple(sorted(NMFP_BALANCE_FIELDS.values())),
    "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv": tuple(
        sorted(set(NMFP_FLOW_FIELDS.values()) | {"mmf_net_flow"})
    ),
    "NMFP_SCHPORTFOLIOSECURITIES.tsv": (
        "mmf_on_rrp",
        "mmf_repo_holdings",
        "mmf_treasury_holdings",
    ),
}

#: The panel fields that come from matching `INVESTMENTCATEGORY` by value, named
#: once so a cross-section whose era has no declared vocabulary can say which
#: fields it is short.
NMFP_CATEGORY_FIELDS = NMFP_TABLE_FIELDS["NMFP_SCHPORTFOLIOSECURITIES.tsv"]

#: Panel fields this adapter derives by matching a *value inside a row it has
#: already counted into another field*, mapped to the field whose observation is
#: the derivation's input.
#:
#: `mmf_on_rrp` is the only one, and it is the reason this declaration exists.
#: Every other panel field is absent for a reason the archive states: the table
#: is not there, or the report month has no declared `INVESTMENTCATEGORY`
#: vocabulary, and both are recorded in `CrossSectionCoverage.absent_fields`. A
#: derived field has a third way to be absent that neither of those covers and
#: that the panel could not previously represent -- the table was present,
#: readable and parsed, its rows produced `mmf_repo_holdings` for the very same
#: cross-section, and the counterparty match found no `FEDERAL RESERVE` in any of
#: them. No row is emitted and, until this declaration, nothing recorded that the
#: derivation had run at all, so a month in which money funds lent nothing to the
#: facility was indistinguishable from a month the adapter never looked at.
#:
#: The mapping is *from* the derived field *to* its input, and the input is what
#: makes the record safe to state. "The derivation matched nothing" is only a
#: fact about the market when the rows it matches over were observed; if
#: `mmf_repo_holdings` is itself unobserved for the cross-section there were no
#: repo rows to find a counterparty in, and the derived field's absence is
#: inherited rather than measured. That case is deliberately *not* recorded here.
#:
#: Declared rather than inferred from the parser, for the same reason
#: `InvestmentCategoryEra` declares its vocabulary: "this field is derived by a
#: match" is a claim about what the number means, and a reader must be able to
#: find it stated rather than reconstruct it from a substring test 300 lines
#: down.
NMFP_DERIVED_FROM_MATCH = {"mmf_on_rrp": "mmf_repo_holdings"}


@dataclass(frozen=True)
class InvestmentCategoryEra:
    """The `INVESTMENTCATEGORY` vocabulary this adapter matches on, for one era.

    Header compatibility is not value compatibility, and this is the declaration
    that says so out loud. Every column the adapter reads is present under the
    same name in every Form N-MFP archive back to 2010q4, so a header check
    admits all of them -- and then `INVESTMENTCATEGORY`, which is a categorical
    the adapter matches on by *value*, silently means something different. The
    label for Treasury debt was rewritten from `Treasury Debt` to
    `U.S. Treasury Debt` between the 2016-03-31 and 2016-04-30 report months, so
    a header-only check would read a 2013 archive with `mmf_repo_holdings`
    populated and `mmf_treasury_holdings` empty, the identity satisfied, and
    nothing flagged.

    Declaring the vocabulary per era, rather than widening the matcher to accept
    both spellings, is the difference between "we have more history" and "we
    changed what the number means". Each era states three closed sets and their
    union is the complete vocabulary observed in that era:

    - `treasury` -- categories counted into `mmf_treasury_holdings`.
    - `repo` -- categories counted into `mmf_repo_holdings`, and into
      `mmf_on_rrp` when the counterparty rule also matches.
    - `excluded` -- categories this adapter deliberately reads no field from.
      Declared rather than defaulted, because "we do not read commercial paper"
      and "we have never seen this string" must not look the same.

    A value in none of the three raises. Falling through to no row would be the
    silent-partial failure this declaration exists to prevent, arriving one layer
    down: the row would be dropped, the series would be short, and the identity
    would still hold.

    `start` and `end` are report dates, inclusive, and the last era is bounded by
    the newest report month the declared archive set actually carries. It is not
    left open-ended: the vocabulary is still moving -- `U.S. Government Agency
    Debt` split into coupon-paying and no-coupon variants in the 2024-06 report
    month -- so an open era would be a claim about months nobody has read. A
    report date in no declared era costs `NMFP_CATEGORY_FIELDS` for that
    cross-section and nothing else, the same per-table posture the absent-table
    rule takes.
    """

    start: date
    end: date
    treasury: frozenset
    repo: frozenset
    excluded: frozenset

    @property
    def declared(self) -> frozenset:
        return self.treasury | self.repo | self.excluded


#: The `INVESTMENTCATEGORY` vocabulary, era by era, enumerated from all 97
#: declared archives on 7 September 2026 rather than from documentation. Each
#: era's three sets are exactly the distinct values observed in the report
#: months it covers -- no value is declared that the source has never emitted,
#: and no observed value is left undeclared.
#:
#: Two boundaries, both sharp, both at a report month rather than a filing date:
#:
#: 2016-04-30 -- the Form N-MFP2 relabelling. `Treasury Debt` becomes
#: `U.S. Treasury Debt` and every other label is rewritten with it. This is the
#: boundary the previous block found and could not act on: the adapter matched
#: only the later spelling, so the whole 2010-11..2016-03 era would have parsed
#: with `mmf_treasury_holdings` empty and `mmf_repo_holdings` populated -- the
#: substring `Repurchase Agreement` survived the rewrite and exact equality on
#: `U.S. Treasury Debt` did not.
#:
#: 2024-06-30 -- the Form N-MFP3 expansion. `U.S. Government Agency Debt` splits
#: into coupon-paying and no-coupon variants, and `Other Repurchase Agreement,
#: if any collateral falls outside ...` loses the word `any`. This adapter reads
#: neither agency-debt variant, but the repo relabelling is one word away from
#: dropping a repo category on the floor, and it is the reason the last era is
#: bounded rather than open.
#:
#: Two single-month spelling artifacts are declared literally, with the double
#: space the source filed: `Government  Agency Repurchase Agreement` in 2013-10
#: and `Other  Note` in 2012-07. Normalising whitespace here would be this
#: adapter deciding what a filer meant; declaring the string is the source
#: saying it.
NMFP_INVESTMENT_CATEGORY_ERAS = (
    InvestmentCategoryEra(
        start=date(2010, 11, 30),
        end=date(2016, 3, 31),
        treasury=frozenset({"Treasury Debt"}),
        repo=frozenset(
            {
                "Government  Agency Repurchase Agreement",
                "Government Agency Repurchase Agreement",
                "Other Repurchase Agreement",
                "Treasury Repurchase Agreement",
            }
        ),
        excluded=frozenset(
            {
                "Asset Backed Commercial Paper",
                "Certificate of Deposit",
                "Financial Company Commercial Paper",
                "Government Agency Debt",
                "Insurance Company Funding Agreement",
                "Investment Company",
                "Other  Note",
                "Other Commercial Paper",
                "Other Instrument",
                "Other Municipal Debt",
                "Other Note",
                "Structured Investment Vehicle Note",
                "Variable Rate Demand Note",
            }
        ),
    ),
    InvestmentCategoryEra(
        start=date(2016, 4, 1),
        end=date(2024, 5, 31),
        treasury=frozenset({"U.S. Treasury Debt"}),
        repo=frozenset(
            {
                "Other Repurchase Agreement, if any collateral falls outside "
                "Treasury, Government Agency and cash",
                "U.S. Government Agency Repurchase Agreement, collateralized "
                "only by U.S. Government Agency securities, U.S. Treasuries, "
                "and cash",
                "U.S. Treasury Repurchase Agreement, if collateralized only by "
                "U.S. Treasuries (including Strips) and cash",
            }
        ),
        excluded=frozenset(
            {
                "Asset Backed Commercial Paper",
                "Certificate of Deposit",
                "Financial Company Commercial Paper",
                "Insurance Company Funding Agreement",
                "Investment Company",
                "Non-Financial Company Commercial Paper",
                "Non-Negotiable Time Deposit",
                "Non-U.S. Sovereign, Sub-Sovereign and Supra-National debt",
                "Other Asset Backed Securities",
                "Other Instrument",
                "Other Municipal Security",
                "Tender Option Bond",
                "U.S. Government Agency Debt",
                "Variable Rate Demand Note",
            }
        ),
    ),
    InvestmentCategoryEra(
        start=date(2024, 6, 1),
        end=date(2026, 7, 31),
        treasury=frozenset({"U.S. Treasury Debt"}),
        repo=frozenset(
            {
                "Other Repurchase Agreement, if collateral falls outside "
                "Treasury, Government Agency and cash",
                "U.S. Government Agency Repurchase Agreement, collateralized "
                "only by U.S. Government Agency securities, U.S. Treasuries, "
                "and cash",
                "U.S. Treasury Repurchase Agreement, if collateralized only by "
                "U.S. Treasuries (including Strips) and cash",
            }
        ),
        excluded=frozenset(
            {
                "Asset Backed Commercial Paper",
                "Certificate of Deposit",
                "Financial Company Commercial Paper",
                "Insurance Company Funding Agreement",
                "Investment Company",
                "Non-Financial Company Commercial Paper",
                "Non-Negotiable Time Deposit",
                "Non-U.S. Sovereign, Sub-Sovereign and Supra-National debt",
                "Other Asset Backed Securities",
                "Other Instrument",
                "Other Municipal Security",
                "Tender Option Bond",
                "U.S. Government Agency Debt (if categorized as coupon-paying notes)",
                "U.S. Government Agency Debt (if categorized as no-coupon "
                "discount notes)",
                "Variable Rate Demand Note",
            }
        ),
    ),
)


def nmfp_investment_category_era(report_date: date):
    """The declared vocabulary for a report month, or `None` if there is none."""

    for era in NMFP_INVESTMENT_CATEGORY_ERAS:
        if era.start <= report_date <= era.end:
            return era
    return None


def _nmfp_category_field(era: InvestmentCategoryEra, category: str, report_date: date):
    """Which holdings field a category feeds in this era, or `None` for neither.

    Raises on a category the era does not declare at all. An undeclared value is
    not evidence that the holding is uninteresting; it is evidence that the
    vocabulary moved again and that nobody has looked.
    """

    if category in era.treasury:
        return "mmf_treasury_holdings"
    if category in era.repo:
        return "mmf_repo_holdings"
    if category in era.excluded:
        return None
    raise ValueError(
        f"SEC Form N-MFP INVESTMENTCATEGORY {category!r} on {report_date.isoformat()} "
        f"is not declared for the {era.start.isoformat()}..{era.end.isoformat()} "
        "vocabulary era, neither as a category this adapter reads nor as one it "
        "excludes. Matching it to nothing would leave a holdings series short "
        "with the identity still satisfied and nothing flagged, which is exactly "
        "the failure NMFP_INVESTMENT_CATEGORY_ERAS exists to prevent. Declare it"
    )


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


def _nmfp_table_if_present(archive: zipfile.ZipFile, name: str):
    """One table's reader, or `None` when the archive does not carry it at all.

    The two failures this distinguishes are not the same claim about a file. A
    table whose columns moved is unreadable and refuses the archive, because a
    renamed column reaches `record.get()` as `None` and skips the row silently.
    A table that is simply absent costs the panel fields it supplies -- named in
    `NMFP_TABLE_FIELDS` -- and nothing else, because a field with no observation
    is a state the panel already represents. So this returns `None` for absence
    and still raises, through `_nmfp_table`, for a header that has moved.
    """

    if name not in frozenset(archive.namelist()):
        return None
    return _nmfp_table(archive, name)


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

#: How a contributed cell earns its `ref_date`, recorded in the cell key rather
#: than recovered from the series name. A balance-sheet or holdings cell is
#: dated by the cross-section it was filed under, so assembling a split
#: month-end into one cross-section re-dates it; a daily shareholder-flow cell
#: is dated by the day whose flows it reports, and that day does not move
#: because the month around it was assembled. The distinction cannot be read off
#: the `ref_date` -- a flow reported on the last business day of the month
#: carries the same date as the cross-section it was filed under -- and June
#: 2024, the first report month with a flow table, is itself a split month-end,
#: so the ambiguity is present the first time the table exists.
NMFP_DATED_BY_CROSS_SECTION = "cross_section"
NMFP_DATED_BY_FLOW_DATE = "flow_date"


def _nmfp_cross_section(report_date: date) -> tuple:
    """The cross-section a report date belongs to: its calendar month.

    A month-end that is not a business day splits the reporting universe across
    two adjacent `REPORTDATE`s -- the funds reporting as of the last business
    day and the funds reporting as of the last calendar day -- and neither half
    is the universe. The calendar month is the unit, and it is the calendar
    month rather than a window around a month-end because any window wide enough
    to gather a split month-end also gathers the month next to it: 30 April 2016
    and 31 May 2016 are 31 days apart. See `docs/DATA_QUALITY_DECISIONS.md`,
    "The split month-end".
    """

    return (report_date.year, report_date.month)


def _resolve_nmfp_submissions(submissions):
    """Pick the one submission that speaks for each (series, cross-section).

    `submissions` maps accession to `(series_id, cross_section, filing_date)`.
    The **caller** says what a cross-section is, and it is not always the report
    date: `_sec_nmfp_rows` reads one archive and keys on the report date, while
    `_assemble_sec_nmfp` assembles a split month-end into one cross-section and
    keys on the calendar month. Both are the same rule -- one submission speaks
    for a series in a cross-section -- applied to the unit the caller assembles
    on. Hard-coding the report date here would mean that a series filing in both
    halves of a split month kept both filings and had its balance sheet booked
    twice into the month they were assembled into.

    Form N-MFP is filed per series per month, so a series that appears twice for
    one cross-section has been amended: `N-MFP3/A` is a second accession
    restating the first, not a second fund. The value tables aggregate by adding
    every accession's values together, which is right across series and wrong
    across a series and its own amendment -- it books the restated balance sheet
    on top of the one it replaces. A quarterly extract and the monthly extract
    that follows it both carry such pairs, so the backfill turns a case that
    never arose on one archive into the normal one.

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
    for accession, (series_id, cross_section, filing_date) in submissions.items():
        key = (series_id, cross_section)
        rank = (filing_date, accession)
        if key not in best or rank > best[key][0]:
            best[key] = (rank, accession)
    kept = {accession for _rank, accession in best.values()}
    return kept, frozenset(submissions) - kept


def _nmfp_archive_scan(payload: bytes):
    """Read one archive into per-accession contributions, resolving nothing.

    Returns `(submissions, submission_types, contributions, absent)`.
    `submissions` maps accession to `(series_id, report_date, filing_date)`;
    `submission_types` maps accession to its `SUBMISSIONTYPE`; `contributions`
    maps accession to the `(series_id, ref_date, dated_by)` cells it supplies
    and the value it supplies to each, where `dated_by` is one of
    `NMFP_DATED_BY_CROSS_SECTION` or `NMFP_DATED_BY_FLOW_DATE` and says whether
    the cell's `ref_date` moves when its cross-section is assembled; `absent`
    maps each report date this archive carries to the panel series this archive
    could supply no observation of, because the table that carries them is not
    in the archive or because the report month has no declared
    `INVESTMENTCATEGORY` vocabulary. Absent, never zero.

    Supersession is deliberately *not* applied here, and that is the whole point
    of the split. An amendment is resolved per `(SERIESID, REPORTDATE)` across
    every archive -- see `parse_snapshots` -- and an archive read on its own
    cannot know that one of its filings was restated in another one. Reading and
    resolving were a single step for as long as the repository held a single
    extract; separating them is what lets the resolution see the whole archive
    set instead of one window of it.

    Contributions are kept per accession rather than summed per cross-section
    for the same reason: a submission that a later archive amends has to be
    removable after the fact, and a running total it has already been added to
    cannot give it back.

    An archive missing a whole table is read for everything its other tables
    supply. Only `NMFP_SUBMISSION.tsv` is indispensable, because without it no
    row can be attributed to a series or a report date.
    """

    submissions = {}
    submission_types = {}
    contributions = {}

    def add(
        accession: str,
        series_id: str,
        ref_date: date,
        value: float,
        dated_by: str,
    ) -> None:
        cells = contributions.setdefault(accession, {})
        key = (series_id, ref_date, dated_by)
        cells[key] = cells.get(key, 0.0) + value

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
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
            submission_types[accession] = (
                (record.get("SUBMISSIONTYPE") or "").strip() or "(blank)"
            )

        sections = {report_date for _e, report_date, _f in submissions.values()}
        absent = {section: set() for section in sections}

        series_table = _nmfp_table_if_present(archive, "NMFP_SERIESLEVELINFO.tsv")
        if series_table is None:
            for fields in absent.values():
                fields.update(NMFP_TABLE_FIELDS["NMFP_SERIESLEVELINFO.tsv"])
        else:
            for record in series_table:
                accession = (record.get("ACCESSION_NUMBER") or "").strip()
                if accession not in submissions:
                    raise ValueError(
                        f"SEC Form N-MFP series row has unknown accession {accession}"
                    )
                section = submissions[accession][1]
                for raw_field, series_id in NMFP_BALANCE_FIELDS.items():
                    value = _nmfp_number(record.get(raw_field), raw_field)
                    if value is not None:
                        add(
                            accession,
                            series_id,
                            section,
                            value / 1_000_000_000,
                            NMFP_DATED_BY_CROSS_SECTION,
                        )

        # Every archive filed before 2024-06-10 predates this table: daily
        # shareholder flows were not collected, so there is nothing to read and
        # nothing to impute. A month with no flow table has no `mmf_net_flow`
        # row. It does not have a zero one, and writing one here would turn
        # fourteen years of absent observations into fourteen years of stated
        # zero flows that every downstream check would accept.
        flow_table = _nmfp_table_if_present(
            archive, "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv"
        )
        if flow_table is None:
            for fields in absent.values():
                fields.update(NMFP_TABLE_FIELDS["NMFP_DLYSHAREHOLDERFLOWREPORT.tsv"])
        else:
            for record in flow_table:
                accession = (record.get("ACCESSION_NUMBER") or "").strip()
                if accession not in submissions:
                    raise ValueError(
                        f"SEC Form N-MFP flow row has unknown accession {accession}"
                    )
                # A daily flow date is its own ref_date, but the submission it
                # was filed under is its cross-section. Deriving the
                # cross-section from the flow date instead would be a guess that
                # happens to be right on this extract, and wrong the first time a
                # filing reports a day outside its own reporting month.
                ref_date = _nmfp_date(
                    record.get("DAILYSHAREHOLDERFLOWDATE"),
                    "DAILYSHAREHOLDERFLOWDATE",
                )
                values = {}
                for raw_field, series_id in NMFP_FLOW_FIELDS.items():
                    value = _nmfp_number(record.get(raw_field), raw_field)
                    if value is not None:
                        values[series_id] = value / 1_000_000_000
                        add(
                            accession,
                            series_id,
                            ref_date,
                            values[series_id],
                            NMFP_DATED_BY_FLOW_DATE,
                        )
                if len(values) == 2:
                    add(
                        accession,
                        "mmf_net_flow",
                        ref_date,
                        values["mmf_gross_subscriptions"]
                        - values["mmf_gross_redemptions"],
                        NMFP_DATED_BY_FLOW_DATE,
                    )

        holdings_table = _nmfp_table_if_present(
            archive, "NMFP_SCHPORTFOLIOSECURITIES.tsv"
        )
        if holdings_table is None:
            for fields in absent.values():
                fields.update(NMFP_CATEGORY_FIELDS)
        else:
            # A cross-section whose report month falls in no declared
            # `INVESTMENTCATEGORY` era loses the holdings fields and keeps the
            # rest of its balance sheet. Reading it against some other era's
            # vocabulary is the failure this guard exists for: the strings would
            # not match, the rows would be dropped, and the series would come out
            # empty rather than refused.
            undeclared = set()
            for record in holdings_table:
                accession = (record.get("ACCESSION_NUMBER") or "").strip()
                if accession not in submissions:
                    raise ValueError(
                        f"SEC Form N-MFP security row has unknown accession {accession}"
                    )
                section = submissions[accession][1]
                era = nmfp_investment_category_era(section)
                if era is None:
                    undeclared.add(section)
                    continue
                # The category is classified before the value is read, so an
                # undeclared string raises whether or not that particular row
                # happens to carry a number. A vocabulary that moved is a fact
                # about the archive, not about which rows were populated.
                category = (record.get("INVESTMENTCATEGORY") or "").strip()
                field = _nmfp_category_field(era, category, section)
                if field is None:
                    continue
                value = _nmfp_number(
                    record.get("INCLUDINGVALUEOFANYSPONSORSUPP"),
                    "INCLUDINGVALUEOFANYSPONSORSUPP",
                )
                if value is None:
                    continue
                add(
                    accession,
                    field,
                    section,
                    value / 1_000_000_000,
                    NMFP_DATED_BY_CROSS_SECTION,
                )
                if field == "mmf_repo_holdings":
                    counterparty = " ".join(
                        str(record.get(name) or "")
                        for name in (
                            "NAMEOFISSUER", "TITLEOFISSUER", "BRIEFDESCRIPTION"
                        )
                    ).upper()
                    if "FEDERAL RESERVE" in counterparty:
                        add(
                            accession,
                            "mmf_on_rrp",
                            section,
                            value / 1_000_000_000,
                            NMFP_DATED_BY_CROSS_SECTION,
                        )
            for section in undeclared:
                absent.setdefault(section, set()).update(NMFP_CATEGORY_FIELDS)

    return submissions, submission_types, contributions, absent


def _sec_nmfp_rows(artifact: SnapshotArtifact, payload: bytes):
    """Aggregate one SEC bulk extract read in isolation, without inventing rows.

    Returns `(rows, entity_counts, submission_types, absent_fields)` -- the shape
    this adapter has always returned, for the one caller that legitimately holds
    a single archive and no others: a schema check on a rewritten payload.

    `parse_snapshots` no longer goes through here. Resolving supersession inside
    this function resolves it inside one archive, which was correct when the
    repository held one extract and became wrong the moment the backfill put a
    filing and its amendment in different ones. The panel is assembled by
    `_assemble_sec_nmfp` instead, which resolves per `(SERIESID, month)` across
    every archive.

    **This function and the panel no longer agree, and the difference is not an
    oversight.** It groups by `REPORTDATE`, so on a split month-end it reports
    the two halves the archive actually filed; the panel assembles them into one
    cross-section dated the month's greatest `REPORTDATE`. That is right for
    what this is used for -- one caller, a schema check on a rewritten payload,
    which asks what a single archive *says* rather than what the panel makes of
    it -- and it would be wrong to answer that question with an assembly the
    archive did not perform. Nothing downstream of the panel reads this.

    Each element of `rows` pairs an observation with the report date of the
    submission it came from -- its cross-section as this function groups them --
    which is not always its own `ref_date`: a daily shareholder-flow row is
    dated within the reporting month but belongs to that month's cross-section
    and stands or falls with it.
    `entity_counts` maps each cross-section to the number of distinct reporting
    entities that filed for it. `submission_types` maps each cross-section to
    how many submissions of each `SUBMISSIONTYPE` it carries, superseded ones
    included: it corroborates the coverage decision without participating in it.
    `absent_fields` maps each cross-section to the panel series this archive
    could supply no observation of. Absent, never zero.
    """

    from .data import PointInTimeObservation

    available_at = datetime.fromisoformat(artifact.retrieved_at.replace("Z", "+00:00"))
    submissions, submission_types, contributions, absent = _nmfp_archive_scan(payload)
    kept_accessions, _superseded = _resolve_nmfp_submissions(submissions)

    totals = {}
    for accession in sorted(kept_accessions):
        section = submissions[accession][1]
        for (series_id, ref_date, _dated_by), value in contributions.get(
            accession, {}
        ).items():
            # One archive read alone assembles nothing, so a cell's `ref_date`
            # is already the one it will carry and the basis is not consulted.
            key = (section, series_id, ref_date)
            totals[key] = totals.get(key, 0.0) + value

    entities = {}
    types = {}
    for accession, (entity, section, _filing) in submissions.items():
        entities.setdefault(section, set()).add(entity)
        mix = types.setdefault(section, {})
        kind = submission_types[accession]
        mix[kind] = mix.get(kind, 0) + 1

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
        types,
        {section: tuple(sorted(fields)) for section, fields in absent.items() if fields},
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


def _nmfp_unmatched_derived_fields(observed, structural_zeros, ref_date):
    """Derived fields whose input was observed and which matched nothing.

    `observed` is the set of panel field names this cross-section supplies;
    `structural_zeros` maps a field to the `StructuralZeroPeriod` the registry
    declares for it, as `declared_structural_zeros` reads it; `ref_date` is this
    cross-section's own report month. Returns `(field, disposition)` pairs
    in field order, for `CrossSectionCoverage.unmatched_derived_fields`.

    Both halves of the condition matter and they fail in opposite directions:

    * The **input must be observed.** Without it there were no rows to match
      over, so the derived field is absent because its source is, which
      `absent_fields` already records once and must not record twice under a
      second name. This is also what keeps the third kind of absence disjoint
      from the first two by construction rather than by a rule someone has to
      remember -- a cross-section whose holdings table is missing, or whose
      report month has no declared `INVESTMENTCATEGORY` era, contributes no repo
      rows at all, so its input is unobserved and it can never appear here.
    * The **derived field must not be observed.** A cross-section with even one
      matching row has an observation, and the value it carries is the answer;
      there is nothing absent to record.

    The disposition is read off the registry and nothing else. This function does
    not decide *why* the derivation matched nothing -- whether the facility did
    not exist yet, or existed and these funds did not use it -- because that is a
    review, recorded by a human in `metadata/sources.json` under
    `structural_zeros` with `structural_zeros_reviewed`. What it records is that
    the derivation ran and came back empty, which is the fact the review needs
    and the one nothing was keeping.

    A declaration applies to a **period**, and the date it is compared against is
    this cross-section's own `ref_date`. Not today, not the build cutoff, not the
    latest month in the batch: each of those happens to get `sec_nmfp`'s case
    right on the archives currently on disk and then reads differently on a
    re-run six months later, or on a backfill of older ones, which would make a
    coverage record depend on when it was produced rather than on what was in
    the archive. Outside the declared period the answer is
    `DERIVED_ABSENCE_UNDECLARED`, which is not a hedge -- it is literally true
    that nobody has declared that month, and it is the answer that keeps
    2026-07-31 distinguishable from the thirty-two pre-facility months once the
    pending review declares them.
    """

    from .data import DERIVED_ABSENCE_DECLARED_ZERO, DERIVED_ABSENCE_UNDECLARED

    found = []
    for derived, base in sorted(NMFP_DERIVED_FROM_MATCH.items()):
        if base not in observed or derived in observed:
            continue
        period = structural_zeros.get(derived)
        found.append(
            (
                derived,
                DERIVED_ABSENCE_DECLARED_ZERO
                if period is not None and period.covers(ref_date)
                else DERIVED_ABSENCE_UNDECLARED,
            )
        )
    return tuple(found)


def _assemble_sec_nmfp(
    artifacts: Sequence[SnapshotArtifact],
    registry: Mapping[str, Mapping[str, object]],
):
    """Assemble every `sec_nmfp` archive into cross-sections, then admit them.

    Returns `(candidates, coverage)`: `(retrieved_at, observation)` pairs for the
    revision logic, and one `CrossSectionCoverage` per archive that files into a
    calendar month, recording the *assembled* state of that cross-section as of
    that archive -- including, per `NMFP_DERIVED_FROM_MATCH`, any derived field
    whose input was observed for that cross-section and which matched none of the
    rows it was derived over. No row is emitted for such a field: it has no
    observation, and a `0.0` would be one.

    A cross-section is a calendar month, not a report date and not an archive.
    Both corrections were made against the same original claim -- that a
    cross-section is an archive -- which was true while the repository held one
    extract and stopped being true without anything noticing, because each
    archive on its own still looks exactly as it did. Three questions were being
    decided on a unit that was wrong for all of them, and they are not the same
    question:

    - **Supersession is per `(SERIESID, REPORTDATE)` across every archive.**
      `N-MFP3/A` is a second accession restating the first, and the backfill
      routinely puts the restatement in a different archive from the original --
      a quarterly extract carries the original and the monthly extract that
      follows carries the amendment. Resolving inside one archive cannot see
      that pair, so the panel carried the superseded original.
    - **Coverage is per `REPORTDATE` across every archive.** The straggler
      cohorts an archive carries for adjacent months are individually far below
      the floor, and excluding each one separately is the right verdict about a
      cross-section and the wrong one about an amendment: it throws the
      amendments away with the cohort, leaving the originals they were filed to
      replace standing unreplaced, and drops a series that filed only there.

    - **The cross-section is the calendar month, not the `REPORTDATE`.** A
      month-end that is not a business day splits the reporting universe across
      two adjacent `REPORTDATE`s, and judged a report date at a time neither
      half is the universe: usually only the larger clears the floor and the
      month is admitted about a quarter short, and where both cleared it the
      month put two partial cross-sections in the panel and the identity was
      reconciled on each as though it were whole. The month's reference date is
      the **greatest `REPORTDATE` observed in it** -- a date the data contains,
      rather than the calendar month-end, which in a month ending on a Sunday is
      a date no filer used.

    Assembly is progressive, in retrieval order, and that is what keeps this a
    change to *what* a cross-section is rather than to when the panel could have
    known it. At each archive the cross-sections that archive touches are
    reassembled from every archive retrieved up to and including it, and emitted
    with that archive's retrieval time. A later archive that changes a cell
    reaches the revision logic as a later vintage of it, exactly as before; a
    later archive that changes nothing is not a revision and the revision logic
    already drops it. Assembling only the final state instead would collapse the
    correction history into one row and claim the whole panel was knowable at
    the last retrieval, which is a look-ahead in everything but name.

    Three things follow from assembling by month, and each is a way it could be
    got wrong:

    - **Supersession resolves on the assembled cross-section.** A series that
      files in both halves of a split month-end is one series' account of one
      cross-section, so the later-filed submission supersedes the earlier rather
      than being added to it. Resolving on the report date instead would keep
      both and book that series' balance sheet into the month twice.
    - **Only cross-section-dated cells move.** A balance-sheet or holdings cell
      is dated by the cross-section it was filed under and is re-dated with it;
      a daily shareholder-flow cell is dated by the day whose flows it reports
      and is not. `NMFP_DATED_BY_CROSS_SECTION` and `NMFP_DATED_BY_FLOW_DATE` carry
      that in the cell key so it is not re-derived from the series name.
    - **The reference date is progressive, like the floor.** It is the greatest
      report date observed *in the archives retrieved so far*, for the same
      reason the count is taken over those archives: dating a month by a report
      date that no archive had yet filed would label a cross-section with a day
      nobody had observed. Where a later archive extends a month past the date
      an earlier vintage was emitted under, the earlier vintage stands as what
      was known then; it is not retracted and no zero is written at it.

    The floor's value is untouched, and so is the unit it counts -- distinct
    `SERIESID`. Only the population it counts over changed, from one archive's
    filings for a report date to every archive's filings for a calendar month.
    """

    from .data import (
        CrossSectionCoverage,
        PointInTimeObservation,
        declared_coverage_floor,
        declared_structural_zeros,
    )

    ordered = sorted(artifacts, key=lambda item: item.retrieved_at)
    if not ordered:
        return [], []

    source_id = ordered[0].source_id
    try:
        source = registry[source_id]
    except KeyError as exc:
        raise ValueError(
            f"snapshots have no source-registry entry: [{source_id!r}]"
        ) from exc
    floors = declared_coverage_floor(source_id, source)
    entity_unit = floors.entity_unit
    # Read once per source, asked per cross-section. Which fields a source
    # declares is a property of the source, so parsing them once is right;
    # whether a declaration reaches a given month is a property of the month,
    # and `StructuralZeroPeriod.covers` answers that below against each
    # cross-section's own ref_date.
    structural_zeros = declared_structural_zeros(source_id, source)

    submissions = {}          # accession -> (series_id, report_date, filing_date)
    submission_types = {}     # accession -> SUBMISSIONTYPE
    contributions = {}        # accession -> {(series_id, ref_date, dated_by): value}
    cell_accessions = {}      # cell -> {accession}
    section_cells = {}        # (month, series_id) -> {cross-section-dated cell}
    section_accessions = {}   # month -> {accession}
    absent = {}               # month -> set of unobservable fields

    scanned_sections = []     # per archive, the months it files into
    scanned_accessions = []   # per archive, the accessions it carries

    for artifact in ordered:
        payload = _artifact_payload(artifact)
        scanned, types, cells, missing = _nmfp_archive_scan(payload)
        for accession, entry in scanned.items():
            if accession in submissions and submissions[accession] != entry:
                # Accessions are unique across the whole of EDGAR, so one that
                # describes two different submissions is a corrupt archive
                # whichever archive it turned up in. Checking it across the set
                # is strictly more of the same check, not a new rule.
                raise ValueError(
                    f"SEC Form N-MFP accession {accession} describes two submissions"
                )
            submissions[accession] = entry
            submission_types[accession] = types[accession]
            section_accessions.setdefault(
                _nmfp_cross_section(entry[1]), set()
            ).add(accession)
        for accession, supplied in cells.items():
            contributions[accession] = supplied
            for cell in supplied:
                cell_accessions.setdefault(cell, set()).add(accession)
                # A cross-section-dated cell is filed with its submission's own
                # report date -- that is what `_nmfp_archive_scan` dates it by --
                # so the month it belongs to is readable from the cell, without
                # the accession. That is what lets `panel_cell` be a function of
                # the cell alone, and it is what this index records.
                if cell[2] == NMFP_DATED_BY_CROSS_SECTION:
                    key = (_nmfp_cross_section(cell[1]), cell[0])
                    section_cells.setdefault(key, set()).add(cell)
        # `missing` is seeded with exactly the report dates the archive carries,
        # populated or not, so its keys name the archive's cross-sections once
        # they are folded onto the month.
        archive_absent = {}
        for report_date, fields in missing.items():
            section = _nmfp_cross_section(report_date)
            if section in archive_absent:
                archive_absent[section] &= set(fields)
            else:
                archive_absent[section] = set(fields)
        for section, fields in archive_absent.items():
            # A field is absent from an assembled cross-section only when no
            # archive filing into that month could supply it. One archive
            # predating the daily-flow table does not make the month's flows
            # unobservable if another archive carries them.
            if section in absent:
                absent[section] &= fields
            else:
                absent[section] = fields
        scanned_sections.append(sorted(archive_absent))
        scanned_accessions.append(frozenset(scanned))

    active = set()
    assembled = {}
    candidates = []
    coverage = []
    known = set()
    admitted = set()
    section_ref_dates = {}    # month -> greatest report date observed so far

    def panel_cell(cell):
        """Where a contributed cell lands in the panel, given today's assembly.

        A cross-section-dated cell carries its month's reference date; a
        flow-dated cell carries the day whose flows it reports, which does not
        move because the month around it was assembled.
        """

        series_id, ref_date, dated_by = cell
        if dated_by == NMFP_DATED_BY_CROSS_SECTION:
            ref_date = section_ref_dates[_nmfp_cross_section(ref_date)]
        return (series_id, ref_date)

    def contributing_cells(target):
        """Every contributed cell that lands on one panel cell today.

        The cross-section-dated ones are the month's, which the target's own
        reference date names because that date is one of the month's report
        dates. The flow-dated one is the cell for that exact day. A series is
        dated one way or the other, so one of these two is always empty -- and
        if a series were ever dated both ways, both contributions would belong
        to that panel cell anyway.
        """

        series_id, ref_date = target
        found = set(section_cells.get((_nmfp_cross_section(ref_date), series_id), ()))
        found.add((series_id, ref_date, NMFP_DATED_BY_FLOW_DATE))
        return found

    for index, artifact in enumerate(ordered):
        retrieved_at = datetime.fromisoformat(
            artifact.retrieved_at.replace("Z", "+00:00")
        )
        sections = scanned_sections[index]
        known |= scanned_accessions[index]
        # The greatest report date observed *so far* in each month. Taking it
        # over every archive instead would date a cross-section by a report date
        # that no archive had yet filed, which is the same look-ahead the count
        # below is careful to avoid, one field over.
        previous_ref_dates = dict(section_ref_dates)
        for accession in scanned_accessions[index]:
            report_date = submissions[accession][1]
            section = _nmfp_cross_section(report_date)
            if report_date > section_ref_dates.get(section, date.min):
                section_ref_dates[section] = report_date
        # Compared against the previous archive's state rather than accumulated
        # while scanning this one: a month first seen here has not moved, and
        # two accessions of one month arriving in either order must give the
        # same answer. `scanned_accessions` is a set, so an incremental test
        # would depend on its iteration order.
        moved = {
            section
            for section, ref_date in section_ref_dates.items()
            if section in previous_ref_dates and previous_ref_dates[section] != ref_date
        }
        # A submission speaks for a series in a *cross-section*, and the
        # cross-section is the month: a series that filed in both halves of a
        # split month-end filed twice about one month, and the later filing
        # supersedes the earlier rather than being added to it.
        kept, _superseded = _resolve_nmfp_submissions(
            {
                accession: (
                    submissions[accession][0],
                    _nmfp_cross_section(submissions[accession][1]),
                    submissions[accession][2],
                )
                for accession in known
            }
        )
        # Counted over the archives retrieved so far, not over all of them. The
        # floor is a statement about what had been assembled by this retrieval,
        # and reading a later archive's filers into an earlier vintage's count
        # would admit a cross-section before its filers were observable.
        members = {
            section: {
                accession
                for accession in section_accessions[section]
                if accession in known
            }
            for section in sections
        }
        counts = {
            section: len({submissions[accession][0] for accession in found})
            for section, found in members.items()
        }
        for section in sections:
            # The floor is the one declared for the era the cross-section's own
            # reference date falls in. A section in no declared era is refused:
            # there is no floor to clear, and admitting it on the nearest era's
            # floor would judge it against a universe it is not part of.
            era = floors.era_for(section_ref_dates[section])
            if era is not None and counts[section] >= era.minimum_reporting_entities:
                admitted.add(section)
        wanted = {
            accession
            for accession in kept
            if _nmfp_cross_section(submissions[accession][1]) in admitted
        }
        changed = (wanted - active) | (active - wanted)
        # A month whose reference date moved re-dates every cross-section-dated
        # cell its active submissions supply, whether or not those submissions
        # themselves changed. The rows emitted at the month's previous reference
        # date are left standing: they are what this source said when that was
        # the greatest report date anyone had seen, and retracting a vintage --
        # or writing a zero at it -- would state something the archives do not.
        restated = {
            accession
            for accession in wanted
            if _nmfp_cross_section(submissions[accession][1]) in moved
        }
        active = wanted
        dirty = set()
        for accession in changed | restated:
            for cell in contributions.get(accession, ()):
                dirty.add(panel_cell(cell))
        for target in dirty:
            total = 0.0
            for cell in sorted(contributing_cells(target)):
                for accession in sorted(cell_accessions.get(cell, ())):
                    if accession in active:
                        total += contributions[accession][cell]
            assembled[target] = total
        for series_id, ref_date in sorted(dirty):
            candidates.append(
                (
                    retrieved_at,
                    PointInTimeObservation(
                        series_id=series_id,
                        ref_date=ref_date,
                        available_at=retrieved_at,
                        value=assembled[(series_id, ref_date)],
                        vintage_id=artifact.retrieved_at,
                        source_sha=artifact.sha256,
                    ),
                )
            )
        for section in sections:
            mix = {}
            for accession in members[section]:
                kind = submission_types[accession]
                mix[kind] = mix.get(kind, 0) + 1
            # `row_count` counts what this cross-section would put in the panel,
            # so an excluded one still reports the rows it was declined for.
            surviving = {
                panel_cell(cell)
                for accession in members[section] & kept
                for cell in contributions.get(accession, ())
            }
            era = floors.era_for(section_ref_dates[section])
            # Taken from `surviving`, so it is a statement about the *assembled*
            # cross-section as of this archive: a derived field is recorded
            # unmatched only when no submission surviving supersession, in any
            # archive retrieved so far, produced a value for it. Deciding it per
            # archive instead would record an absence that the next archive in
            # the same month refutes, and the record would then contradict the
            # panel beside it.
            observed = {series_id for series_id, _ref_date in surviving}
            coverage.append(
                CrossSectionCoverage(
                    source_id=source_id,
                    ref_date=section_ref_dates[section],
                    entity_unit=entity_unit,
                    entity_count=counts[section],
                    declared_floor=(
                        None if era is None else era.minimum_reporting_entities
                    ),
                    era_id=None if era is None else era.era_id,
                    admitted=section in admitted,
                    row_count=len(surviving),
                    submission_types=tuple(sorted(mix.items())),
                    absent_fields=tuple(sorted(absent.get(section, ()))),
                    unmatched_derived_fields=_nmfp_unmatched_derived_fields(
                        observed, structural_zeros, section_ref_dates[section]
                    ),
                )
            )
    return candidates, coverage


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

    `sec_nmfp` is assembled across archives rather than parsed one at a time --
    see `_assemble_sec_nmfp`. A report date it carries is one cross-section
    however many archives filed into it, and both supersession and the coverage
    floor are decided on that assembled unit.
    """

    from .data import declared_coverage_floor

    if registry is None:
        registry = load_source_registry(registry_path)

    candidates = []
    coverage = []
    nmfp = []
    for artifact in artifacts:
        artifact = replace(
            artifact,
            source_id=LEGACY_SOURCE_IDS.get(artifact.source_id, artifact.source_id),
        )
        if artifact.source_id == "sec_nmfp":
            nmfp.append(artifact)
            continue
        payload = _artifact_payload(artifact)
        if artifact.source_id == FR2004_SOURCE_ID:
            # Before the `nyfed_` prefix test below, which would otherwise send
            # a CSV export to the reference-rate JSON parser.
            parsed_rows = _fr2004_rows(artifact, payload, registry)
        elif artifact.source_id.startswith("nyfed_"):
            parsed_rows = _nyfed_rows(artifact, payload)
        elif artifact.source_id == "fred_macro_latest_vintage":
            parsed_rows = _fred_rows(artifact, payload)
        elif artifact.source_id == "treasury_auctions":
            parsed_rows = _treasury_rows(artifact, payload)
        else:
            raise ValueError(f"no point-in-time parser for {artifact.source_id}")
        retrieved_at = datetime.fromisoformat(
            artifact.retrieved_at.replace("Z", "+00:00")
        )
        candidates.extend((retrieved_at, row) for row in parsed_rows)

    if nmfp:
        _check_declared_entity_unit("sec_nmfp", registry, NMFP_ENTITY_UNIT)
        nmfp_candidates, nmfp_coverage = _assemble_sec_nmfp(nmfp, registry)
        candidates.extend(nmfp_candidates)
        coverage.extend(nmfp_coverage)

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
    # `parse_snapshots` normalizes legacy manifest IDs through
    # `LEGACY_SOURCE_IDS`; the registry check below read the un-normalized
    # artifacts and so refused every snapshot captured before the registry
    # adopted Python-style IDs -- the parse succeeded and the builder then
    # rejected it by a check that had never learned the mapping. Resolve once,
    # here, so the parse, the registry check and `selected_registry` agree.
    # `materialized` is kept as filed: the manifest's `raw_snapshots` records
    # the evidence as it sits on disk, not as this builder reads it.
    resolved = [
        replace(
            item,
            source_id=LEGACY_SOURCE_IDS.get(item.source_id, item.source_id),
        )
        for item in materialized
    ]
    parsed = parse_snapshots(resolved, registry=registry)
    rows = list(parsed.rows)
    if not rows:
        raise ValueError("raw snapshots produced no point-in-time observations")
    unknown_sources = sorted(
        {item.source_id for item in resolved if item.source_id not in registry}
    )
    if unknown_sources:
        raise ValueError(f"snapshots have no source-registry entry: {unknown_sources}")
    selected_registry = {
        source_id: registry[source_id]
        for source_id in sorted({item.source_id for item in resolved})
    }
    from .data import (
        expected_ref_dates_from_registry,
        validate_accounting_identities,
        validate_publication_gaps,
        write_point_in_time_audit_report,
    )

    validate_publication_gaps(rows, selected_registry)
    accounting_identities = validate_accounting_identities(rows, selected_registry)
    unevaluated_identities = [
        item
        for evaluation in accounting_identities.values()
        for item in evaluation.unevaluated
    ]
    # A violated identity no longer raises out of `validate_accounting_identities`
    # -- it is a verdict now, and this is where it is written down. The abort
    # lives in `build_daily_panel`, the first hop that knows whether the panel
    # contains a column from the source; see rule 5 there and
    # `docs/DATA_QUALITY_DECISIONS.md`. Carrying the verdicts no further than
    # the manifest would be the loosening the decision is not, so they go into
    # the quality report where findings go.
    violated_identities = [
        item
        for evaluation in accounting_identities.values()
        for item in evaluation.violations
    ]
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
        unevaluated_identities=unevaluated_identities,
        violated_identities=violated_identities,
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
        accounting_identities=accounting_identities,
    )
    _atomic_write(
        output_path.with_suffix(output_path.suffix + ".manifest.json"),
        json.dumps(artifact.as_dict(), indent=2, sort_keys=True).encode("utf-8") + b"\n",
    )
    return artifact
