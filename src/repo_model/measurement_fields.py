"""Measurement fields from the new point-in-time sources (#377, track D of #374).

Eleonora's directive of 7 October 2026: add the data #374's literature scope
names as point-in-time sources, read as of each decision instant, off in every
published declaration and available to the tracks as measurement fields.

**The sources**

* The New York Fed's SOFR 1st and 99th percentiles are fields of the existing
  `nyfed_sofr` source (`SOFR_p1`, `SOFR_p99`, #127), already snapshotted in
  `tests/fixtures/snapshots/funding_inputs/` under the registry's declared lag.
  They are not fetched again.
* The daily Treasury General Account balance is the new `treasury_dts_tga`
  source (Daily Treasury Statement, Fiscal Data), `ingest.fetch_treasury_dts_tga`.
* The OFR Short-term Funding Monitor's tri-party and GCF segments are the new
  `REPO-TRI_*` and `REPO-GCF_*` series of the existing `ofr_stfm_repo` source,
  `ingest.OFR_STFM_SEGMENT_MNEMONICS`.

**The columns** (`COLUMN_FIELDS`, with the source fields each draws on, which is
what the as-of rule reads their lag from)

* raw: `sofr_p1`, `sofr_p99` (percent), `tga_daily` (USD billions), `ofr_tri_rate`
  and `ofr_gcf_rate` (percent, the overnight/open average rate, preliminary;
  `None` before `OFR_REAL_TIME_START`, because an earlier value was filled in
  after the fact);
* `sofr_p99_iorb_bps`: SOFR's 99th percentile minus IORB, in bp (the definition
  `early_warning` uses);
* `sofr_p99_iorb_sd15_bps`: the sample standard deviation (n − 1) of that spread
  over the 15 panel rows ending at the row, `None` unless all 15 are present;
* `tga_daily_change`: `tga_daily` minus the previous panel row's, USD billions;
* `tga_change_x_reserves`: `tga_daily_change` (USD billions) times
  `reserve_balances` (USD trillions: the published column is in billions, and
  the product is kept near unit scale).

Every derived value comes from its own row and earlier ones; a row's derived
column is the same whatever follows it. A forecast reads a column at the row
its slowest source field allows (`docs/decisions/information-set.md`, rule 1).

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`: no published
panel, declaration or record reads these columns. A track switches them on for
its own run (`scripts/measurement_fields.py` builds the augmented scratch panel
and shows how), as `scripts/early_warning_inputs.py` does for #127's.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import math
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Set, Tuple

from .contract import FEATURE_FIELDS
from .data import DailyObservation
from .ingest import (
    OFR_STFM_REAL_TIME_START,
    OFR_STFM_SOURCE_ID,
    TREASURY_DTS_TGA_FIELD,
    TREASURY_DTS_TGA_SOURCE_ID,
    load_snapshot_manifest,
    parse_snapshots,
)

__all__ = [
    "COLUMN_FIELDS",
    "DERIVED_COLUMNS",
    "ONE_ROW_HOLE_COLUMNS",
    "RAW_COLUMNS",
    "RAW_SERIES",
    "SD_ROWS",
    "assemble",
    "build_columns",
    "carry_one_row_holes",
    "series_from_snapshots",
]

#: The rolling window of `sofr_p99_iorb_sd15_bps`, in panel rows.
SD_ROWS = 15
#: First day the OFR's values were public on their own date.
OFR_REAL_TIME_START = OFR_STFM_REAL_TIME_START

_SOFR = "nyfed_sofr"
_IORB_FIELDS = tuple(FEATURE_FIELDS["iorb"])
_RESERVE_FIELDS = tuple(FEATURE_FIELDS["reserve_balances"])
_SOFR_P99 = ((_SOFR, "SOFR_p99"),)
_TGA = ((TREASURY_DTS_TGA_SOURCE_ID, TREASURY_DTS_TGA_FIELD),)

#: Every column's source fields, for the as-of rule. **Off**: switched on only
#: by a track's own run, never part of `contract.FEATURE_FIELDS`.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    "sofr_p1": ((_SOFR, "SOFR_p1"),),
    "sofr_p99": _SOFR_P99,
    "tga_daily": _TGA,
    "ofr_tri_rate": ((OFR_STFM_SOURCE_ID, "REPO-TRI_AR_OO-P"),),
    "ofr_gcf_rate": ((OFR_STFM_SOURCE_ID, "REPO-GCF_AR_OO-P"),),
    "sofr_p99_iorb_bps": _SOFR_P99 + _IORB_FIELDS,
    "sofr_p99_iorb_sd15_bps": _SOFR_P99 + _IORB_FIELDS,
    "tga_daily_change": _TGA,
    "tga_change_x_reserves": _TGA + _RESERVE_FIELDS,
}

#: Raw column -> (snapshot directory under the snapshots root, series id).
RAW_SERIES: Mapping[str, Tuple[str, str]] = {
    "sofr_p1": ("funding_inputs", "SOFR_p1"),
    "sofr_p99": ("funding_inputs", "SOFR_p99"),
    "tga_daily": ("dts_inputs", TREASURY_DTS_TGA_FIELD),
    "ofr_tri_rate": ("ofr_inputs", "REPO-TRI_AR_OO-P"),
    "ofr_gcf_rate": ("ofr_inputs", "REPO-GCF_AR_OO-P"),
}
RAW_COLUMNS = tuple(RAW_SERIES)
DERIVED_COLUMNS = (
    "sofr_p99_iorb_bps",
    "sofr_p99_iorb_sd15_bps",
    "tga_daily_change",
    "tga_change_x_reserves",
)
#: SOFR's percentiles have two one-day holes (2019-05-31, 2021-08-05).
ONE_ROW_HOLE_COLUMNS = ("sofr_p1", "sofr_p99")


def _get(row: DailyObservation, column: str) -> Optional[float]:
    value = row.values.get(column)
    return None if value is None else float(value)


def _sample_sd(values: Sequence[float]) -> float:
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


def build_columns(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with the derived columns added, each from its own and earlier rows.

    Reads, where present, `sofr_p99`, `iorb`, `tga_daily` and `reserve_balances`.
    A column whose inputs are missing on a row it needs is `None` there.
    """

    spreads: List[Optional[float]] = []
    out: List[DailyObservation] = []
    for position, row in enumerate(rows):
        values: Dict[str, Optional[float]] = dict(row.values)
        p99, iorb = _get(row, "sofr_p99"), _get(row, "iorb")
        spread = None if p99 is None or iorb is None else (p99 - iorb) * 100.0
        spreads.append(spread)
        values["sofr_p99_iorb_bps"] = spread
        window = spreads[position - SD_ROWS + 1 : position + 1] if position >= SD_ROWS - 1 else []
        values["sofr_p99_iorb_sd15_bps"] = (
            None if len(window) < SD_ROWS or any(v is None for v in window) else _sample_sd(window)
        )
        tga, before = _get(row, "tga_daily"), (_get(rows[position - 1], "tga_daily") if position else None)
        change = None if tga is None or before is None else tga - before
        values["tga_daily_change"] = change
        reserves = _get(row, "reserve_balances")
        values["tga_change_x_reserves"] = (
            None if change is None or reserves is None else change * (reserves / 1000.0)
        )
        out.append(DailyObservation(row.date, values))
    return out


def carry_one_row_holes(
    rows: Sequence[DailyObservation], columns: Sequence[str] = ONE_ROW_HOLE_COLUMNS
) -> Tuple[List[DailyObservation], List[str]]:
    """`rows` with a column's single-row hole filled from the row before it, and every fill listed.

    A hole after a present value takes that earlier value (older, never newer,
    so the staleness guard holds); a run of two or more holes is left, and so is
    one at the start. The list is `"<date>:<column>"` for each fill.
    """

    out: List[DailyObservation] = []
    carried: List[str] = []
    for position, row in enumerate(rows):
        values = dict(row.values)
        for name in columns:
            if values.get(name) is not None or position == 0:
                continue
            earlier = rows[position - 1].values.get(name)
            following = rows[position + 1].values.get(name) if position + 1 < len(rows) else None
            if earlier is not None and following is not None:
                values[name] = earlier
                carried.append(f"{row.date.isoformat()}:{name}")
        out.append(DailyObservation(row.date, values))
    return out, carried


def series_from_snapshots(
    directory: Path, wanted: Set[str], cutoff: datetime
) -> Dict[str, Dict[date, float]]:
    """`{series: {ref_date: value}}` from the snapshots under `directory`.

    The latest vintage whose declared `available_at` is at or before `cutoff`,
    per series and date.
    """

    artifacts = [load_snapshot_manifest(path) for path in sorted(directory.rglob("*.manifest.json"))]
    best = {}
    for row in parse_snapshots(artifacts).rows:
        if row.series_id not in wanted or row.available_at > cutoff:
            continue
        key = (row.series_id, row.ref_date)
        if key not in best or row.available_at >= best[key].available_at:
            best[key] = row
    out: Dict[str, Dict[date, float]] = {name: {} for name in wanted}
    for (series, ref_date), row in best.items():
        out[series][ref_date] = row.value
    return out


def assemble(
    rows: Sequence[DailyObservation],
    snapshots: Path,
    *,
    cutoff: datetime,
    end: date,
) -> Tuple[List[DailyObservation], Dict[str, object]]:
    """The published panel's `rows` up to `end`, with the raw and derived columns added.

    Returns the rows and a summary: the holes of each raw column (dates with no
    value, other than the OFR's days before it was real time), the fills of
    `carry_one_row_holes`, and the count of derived values missing. Raises
    `ValueError` if the SOFR percentile source and the panel disagree on a day.
    """

    wanted: Dict[str, Set[str]] = {}
    for _column, (directory, series) in RAW_SERIES.items():
        wanted.setdefault(directory, set()).add(series)
    parsed = {
        directory: series_from_snapshots(snapshots / directory, names, cutoff)
        for directory, names in wanted.items()
    }
    sofr = series_from_snapshots(snapshots / "funding_inputs", {"SOFR"}, cutoff)["SOFR"]
    added: List[DailyObservation] = []
    holes: Dict[str, List[str]] = {name: [] for name in RAW_COLUMNS}
    for row in rows:
        if row.date > end:
            continue
        panel_sofr = row.values.get("sofr")
        if panel_sofr is not None and abs(sofr.get(row.date, math.inf) - float(panel_sofr)) > 1e-12:
            raise ValueError(f"{row.date}: the snapshot's SOFR differs from the panel's")
        values = dict(row.values)
        for column, (directory, series) in RAW_SERIES.items():
            value = parsed[directory][series].get(row.date)
            if column.startswith("ofr_") and row.date < OFR_REAL_TIME_START:
                value = None
            elif value is None:
                holes[column].append(row.date.isoformat())
            values[column] = value
        added.append(DailyObservation(row.date, values))
    filled, carried = carry_one_row_holes(added)
    built = build_columns(filled)
    return built, {
        "holes": {name: dates for name, dates in holes.items() if dates},
        "one_row_holes_filled": carried,
        "derived_missing": {
            name: sum(1 for row in built if row.values.get(name) is None) for name in DERIVED_COLUMNS
        },
    }
