"""Fed repo operations and Standing Repo Facility take-up as measurement fields (#425, track F of #374).

Eleonora's directive: test whether Fed liquidity use warns of pressure. The New York
Fed's repo operation results (`ingest.NYFED_REPO_OPS_SOURCE_ID`, the 2019-2020 temporary
operations and the Standing Repo Facility from 2021-07-29) are a source of their own,
`nyfed_repo_ops`, declared in `metadata/sources_measurement.json` and not in
`metadata/sources.json`, which the final-test pre-registration freezes by its bytes. Each
operation date's values are read after the Desk's recorded publication time and the
registry's declared lag, whichever is later (`ingest._nyfed_repo_ops_rows`).

**The columns** (`COLUMN_FIELDS`, with the source fields each draws on, which is what the
as-of rule reads their lag from). Every one is observed on every panel row: a panel date
with no repo operation is a date nothing was taken, read as zero.

* raw: `fed_repo_accepted` and `fed_repo_submitted` (USD billions), `fed_repo_rate_iorb_bps`
  (the amount-weighted rate accepted minus IORB, in bp, zero where nothing was accepted at
  a stated rate), `fed_repo_ops` (the number of the date's operations that accepted anything);
* derived: `fed_repo_log_accepted` (`ln(1 + fed_repo_accepted)`), `fed_repo_log_accepted_change`
  (that, minus the previous panel row's), and `fed_repo_days_since_positive` (panel rows since
  a row with `fed_repo_accepted > 0`, 0 on such a row, `DAYS_SINCE_CAP` before the first and
  after that many).

Every derived value comes from its own row and earlier ones. A forecast reads a column at the
row its slowest source field allows (`docs/decisions/information-set.md`, rule 1).

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`: no published panel,
declaration or record reads these columns. A track switches them on for its own run
(`scripts/fed_liquidity.py` builds the augmented scratch panel and shows how), as
`scripts/measurement_fields.py` does for #377's.

**A second availability reading (#442).** The declaration above is conservative: a date's
results are public at 16:00 ET on the next business day. The Desk's one timestamp (`lastUpdated`)
falls a median 0.7 minutes after the close, so a date's take-up is very likely public before the
16:00 decision the same day. `SAME_DAY` is that less conservative reading, as a *sensitivity test
only*: a measurement source of its own, `nyfed_repo_ops_sameday` (days = 0), and a second set of
columns with the suffix `_sameday` (`COLUMN_FIELDS_SAME_DAY`). A date is read at 16:00 on its own
date unless its record was written later (`ingest.repo_operation_same_day_available_at`), in which
case the row is withheld from that date and reads as zero, as a date with no operation does: a
value written at 16:10 is invisible to that day's 16:00 decision. The published `nyfed_srf`
declaration (`metadata/sources.json`) does not change.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import math
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

from .contract import FEATURE_FIELDS
from .data import DailyObservation
from .ingest import (
    NYFED_REPO_OPS_ACCEPTED,
    NYFED_REPO_OPS_COUNT,
    NYFED_REPO_OPS_RATE,
    NYFED_REPO_OPS_SOURCE_ID,
    NYFED_REPO_OPS_SUBMITTED,
    load_snapshot_manifest,
    parse_snapshots,
    repo_operation_publication_times,
    repo_operation_same_day_available_at,
)
from . import hierarchical_logistic as _hl
from .measurement_fields import load_registry

__all__ = [
    "ALL_COLUMN_FIELDS",
    "CANDIDATES",
    "COLUMN_FIELDS_SAME_DAY",
    "CONSERVATIVE",
    "SAME_DAY",
    "SAME_DAY_SOURCE_ID",
    "SAME_DAY_SUFFIX",
    "CALIBRATION",
    "COLUMN_FIELDS",
    "DAYS_SINCE_CAP",
    "DERIVED_COLUMNS",
    "RAW_COLUMNS",
    "assemble",
    "build_columns",
    "declaration_entry",
    "features_at_horizon",
    "load_registry",
    "series_from_snapshots",
]

#: The two availability readings of the same snapshots. `CONSERVATIVE` is the declaration
#: (`nyfed_repo_ops`: 16:00 ET on the next business day); `SAME_DAY` is #442's sensitivity test
#: (`nyfed_repo_ops_sameday`: 16:00 ET on the operation date, unless written later).
CONSERVATIVE = "conservative"
SAME_DAY = "same_day"
SAME_DAY_SOURCE_ID = NYFED_REPO_OPS_SOURCE_ID + "_sameday"
SAME_DAY_SUFFIX = "_sameday"
DECISION_TIME = time(16, 0)

#: Panel rows after which "days since a non-zero take-up" stops growing; also its value
#: before the first non-zero row.
DAYS_SINCE_CAP = 250

_IORB_FIELDS = tuple(FEATURE_FIELDS["iorb"])
_ACCEPTED = ((NYFED_REPO_OPS_SOURCE_ID, NYFED_REPO_OPS_ACCEPTED),)
_SUBMITTED = ((NYFED_REPO_OPS_SOURCE_ID, NYFED_REPO_OPS_SUBMITTED),)
_RATE = ((NYFED_REPO_OPS_SOURCE_ID, NYFED_REPO_OPS_RATE),)
_COUNT = ((NYFED_REPO_OPS_SOURCE_ID, NYFED_REPO_OPS_COUNT),)

#: Every column's source fields, for the as-of rule. **Off**: switched on only by a
#: track's own run, never part of `contract.FEATURE_FIELDS`. The rate is read with IORB
#: because the column is their difference.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    "fed_repo_accepted": _ACCEPTED,
    "fed_repo_submitted": _SUBMITTED,
    "fed_repo_rate_iorb_bps": _RATE + _ACCEPTED + _IORB_FIELDS,
    "fed_repo_ops": _COUNT,
    "fed_repo_log_accepted": _ACCEPTED,
    "fed_repo_log_accepted_change": _ACCEPTED,
    "fed_repo_days_since_positive": _ACCEPTED,
}

#: The same columns under the same-day reading: each name carries `SAME_DAY_SUFFIX` and each
#: `nyfed_repo_ops` field is read from `nyfed_repo_ops_sameday` (days = 0). IORB is unchanged.
COLUMN_FIELDS_SAME_DAY: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    name + SAME_DAY_SUFFIX: tuple(
        (SAME_DAY_SOURCE_ID if source == NYFED_REPO_OPS_SOURCE_ID else source, field) for source, field in pairs
    )
    for name, pairs in COLUMN_FIELDS.items()
}
#: Both sets, for a run that switches the inputs on.
ALL_COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {**COLUMN_FIELDS, **COLUMN_FIELDS_SAME_DAY}

#: Raw column -> the series of `nyfed_repo_ops` it is read from.
RAW_SERIES: Mapping[str, str] = {
    "fed_repo_accepted": NYFED_REPO_OPS_ACCEPTED,
    "fed_repo_submitted": NYFED_REPO_OPS_SUBMITTED,
    "fed_repo_ops": NYFED_REPO_OPS_COUNT,
}
RAW_COLUMNS = ("fed_repo_accepted", "fed_repo_submitted", "fed_repo_rate_iorb_bps", "fed_repo_ops")
DERIVED_COLUMNS = (
    "fed_repo_log_accepted",
    "fed_repo_log_accepted_change",
    "fed_repo_days_since_positive",
)


def _artifacts(directory: Path):
    return [load_snapshot_manifest(path) for path in sorted(directory.rglob("*.manifest.json"))]


def same_day_instants(directory: Path) -> Dict[date, datetime]:
    """Per operation date, when its results are public under the same-day reading (#442)."""

    written: Dict[date, datetime] = {}
    for artifact in _artifacts(directory):
        for day, stamp in repo_operation_publication_times(artifact.path.read_bytes()).items():
            if day not in written or stamp > written[day]:
                written[day] = stamp
    return {day: repo_operation_same_day_available_at(day, stamp) for day, stamp in written.items()}


def series_from_snapshots(
    directory: Path, cutoff: datetime, reading: str = CONSERVATIVE
) -> Dict[str, Dict[date, float]]:
    """`{series: {ref_date: value}}` of `nyfed_repo_ops` from the snapshots under `directory`.

    The latest vintage whose `available_at` (the later of the Desk's recorded publication time
    and the declared lag) is at or before `cutoff`, per series and date. Under `SAME_DAY`, a
    date whose results are not public at 16:00 on the date itself
    (`ingest.repo_operation_same_day_available_at`) is left out: a value written after that
    decision is invisible to it.
    """

    if reading not in (CONSERVATIVE, SAME_DAY):
        raise ValueError(f"reading must be {CONSERVATIVE!r} or {SAME_DAY!r}, got {reading!r}")
    best = {}
    for row in parse_snapshots(_artifacts(directory)).rows:
        if row.available_at > cutoff:
            continue
        key = (row.series_id, row.ref_date)
        if key not in best or row.available_at >= best[key].available_at:
            best[key] = row
    instants = same_day_instants(directory) if reading == SAME_DAY else {}
    out: Dict[str, Dict[date, float]] = {
        name: {}
        for name in (NYFED_REPO_OPS_ACCEPTED, NYFED_REPO_OPS_SUBMITTED, NYFED_REPO_OPS_RATE, NYFED_REPO_OPS_COUNT)
    }
    for (series, ref_date), row in best.items():
        if reading == SAME_DAY and instants.get(ref_date, _decision(ref_date)) > _decision(ref_date):
            continue
        out[series][ref_date] = row.value
    return out


def _decision(day: date) -> datetime:
    return datetime.combine(day, DECISION_TIME, tzinfo=ZoneInfo("America/New_York"))


def _get(row: DailyObservation, column: str) -> Optional[float]:
    value = row.values.get(column)
    return None if value is None else float(value)


def build_columns(rows: Sequence[DailyObservation], suffix: str = "") -> List[DailyObservation]:
    """`rows` with the derived columns added, each from its own row and earlier ones.

    Reads `fed_repo_accepted` + `suffix` (required on every row: a missing value is a
    `ValueError`, never a guessed zero).
    """

    out: List[DailyObservation] = []
    since = DAYS_SINCE_CAP
    previous_log: Optional[float] = None
    source = "fed_repo_accepted" + suffix
    for row in rows:
        accepted = _get(row, source)
        if accepted is None or not math.isfinite(accepted) or accepted < 0.0:
            raise ValueError(f"{row.date}: {source} must be a non-negative number, got {accepted!r}")
        values: Dict[str, Optional[float]] = dict(row.values)
        logged = math.log1p(accepted)
        values["fed_repo_log_accepted" + suffix] = logged
        values["fed_repo_log_accepted_change" + suffix] = 0.0 if previous_log is None else logged - previous_log
        previous_log = logged
        since = 0 if accepted > 0.0 else min(since + 1, DAYS_SINCE_CAP)
        values["fed_repo_days_since_positive" + suffix] = float(since)
        out.append(DailyObservation(row.date, values))
    return out


def assemble(
    rows: Sequence[DailyObservation],
    snapshots: Path,
    *,
    cutoff: datetime,
    end: date,
    reading: str = CONSERVATIVE,
) -> Tuple[List[DailyObservation], Dict[str, object]]:
    """The panel's `rows` up to `end`, with the raw and derived columns added.

    A date with no repo operation is read as zero take-up (amounts, count and rate spread zero).
    Under `SAME_DAY` the columns carry the suffix `_sameday` and a date whose results were not
    public at its own 16:00 is read the same way (`series_from_snapshots`); the conservative
    columns, if the rows already carry them, are left as they are. Returns the rows and a
    summary: how many dates had an operation, and how many a non-zero take-up (and, under
    `SAME_DAY`, how many dates were withheld). `snapshots` is the directory holding
    `nyfed_repo_ops/`'s parent (`tests/fixtures/snapshots/repo_ops_inputs`).
    """

    suffix = SAME_DAY_SUFFIX if reading == SAME_DAY else ""
    series = series_from_snapshots(snapshots, cutoff, reading)
    full = series_from_snapshots(snapshots, cutoff) if reading == SAME_DAY else series
    rate = series[NYFED_REPO_OPS_RATE]
    iorb_name = "iorb"
    added: List[DailyObservation] = []
    operated = positive = withheld = 0
    for row in rows:
        if row.date > end:
            continue
        values = dict(row.values)
        accepted = series[NYFED_REPO_OPS_ACCEPTED].get(row.date)
        operated += accepted is not None
        positive += bool(accepted)
        withheld += (row.date in full[NYFED_REPO_OPS_ACCEPTED]) and accepted is None
        values["fed_repo_accepted" + suffix] = accepted or 0.0
        values["fed_repo_submitted" + suffix] = series[NYFED_REPO_OPS_SUBMITTED].get(row.date, 0.0)
        values["fed_repo_ops" + suffix] = series[NYFED_REPO_OPS_COUNT].get(row.date, 0.0)
        iorb = _get(row, iorb_name)
        stated = rate.get(row.date)
        values["fed_repo_rate_iorb_bps" + suffix] = (
            0.0 if stated is None or not accepted else (stated - iorb) * 100.0 if iorb is not None else None
        )
        added.append(DailyObservation(row.date, values))
    built = build_columns(added, suffix)
    missing = sum(1 for row in built if row.values.get("fed_repo_rate_iorb_bps" + suffix) is None)
    summary: Dict[str, object] = {
        "dates_with_an_operation": operated,
        "dates_with_a_non_zero_take_up": positive,
        "rate_spread_missing_iorb": missing,
    }
    if reading == SAME_DAY:
        summary["dates_withheld_from_the_same_day_reading"] = withheld
    return built, summary


# --------------------------------------------------------------------------
# The candidates (declared in metadata/pressure_judge.json before any score)
# --------------------------------------------------------------------------

#: The classifier of #406 (the hierarchical logistic of track H, the best of that track's
#: candidates in the judge's re-judge) with the inputs added as declared linear columns, and
#: the same classifier without them as the control: `hierarchical_logistic`.
#:
#: `hierarchical_logistic_srf` adds the take-up level, its change and the days since the last
#: non-zero take-up (the directive's three inputs); `hierarchical_logistic_fed_repo` adds to
#: those the amount submitted, the rate against IORB and the count of operations that accepted.
CANDIDATES: Mapping[str, Tuple[str, ...]] = {
    "hierarchical_logistic_srf": (
        "fed_repo_log_accepted",
        "fed_repo_log_accepted_change",
        "fed_repo_days_since_positive",
    ),
    "hierarchical_logistic_fed_repo": (
        "fed_repo_log_accepted",
        "fed_repo_log_accepted_change",
        "fed_repo_days_since_positive",
        "fed_repo_submitted",
        "fed_repo_rate_iorb_bps",
        "fed_repo_ops",
    ),
}
#: #442's sensitivity test: each candidate above with its inputs read under the same-day
#: availability reading (`_sameday` columns), and nothing else changed.
SAME_DAY_OF: Mapping[str, str] = {
    "hierarchical_logistic_srf_sameday": "hierarchical_logistic_srf",
    "hierarchical_logistic_fed_repo_sameday": "hierarchical_logistic_fed_repo",
}
CANDIDATES = {
    **CANDIDATES,
    **{
        name: tuple(column + SAME_DAY_SUFFIX for column in CANDIDATES[counterpart])
        for name, counterpart in SAME_DAY_OF.items()
    },
}
CALIBRATION = _hl.CALIBRATION


def features_at_horizon(name: str, horizon: int) -> Tuple[str, ...]:
    """The control's features at `horizon` and the candidate's added columns."""

    return tuple(_hl.features_at_horizon(horizon)) + CANDIDATES[name]


def declaration_entry(name: str) -> dict:
    """The candidate's entry in `metadata/pressure_judge.json`, as this module defines it."""

    return {
        "role": "candidate",
        "track": "F (#425)" if name not in SAME_DAY_OF else "F (#425), same-day reading (#442)",
        "features": sorted(features_at_horizon(name, 1)),
        "calibration": CALIBRATION,
    }
