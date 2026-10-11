"""The OFR "not yet published" flag and fill (#537, follow-up to #477 and PR #496).

The OFR repo-segment rates (`ofr_tri_rate`, `ofr_gcf_rate`) have no value before 2020-09-09
(`FIRST_PUBLIC`), the day the OFR began publishing in real time: earlier values were filled in after
the fact and are not read (#508, #522). A direct model refuses an unobserved input, so including a
rate dropped every scored day before September 2020, among them 2018 and 2020. This module adds, per
rate, two scratch columns that keep those days in a comparison:

* `<series>_not_yet_published`: 1.0 on a row dated before `FIRST_PUBLIC`, else 0.0. **A function of the
  row's date alone.** It is never read off whether a value exists, because the presence of an OFR GCF
  value is not an admissible input (Eleonora's ruling of 10 October 2026 on #520: its gaps differ
  between the preliminary and the final series).
* `<series>_filled`: the rate where the panel has it; 0.0 on a flagged row; missing otherwise. A gap
  after `FIRST_PUBLIC` is **not** filled, so a fit that needs the column still refuses that day. The
  GCF rate is empty on most days after publication, and any fill of those days would turn the value
  into a presence signal.

`add_columns` first refuses, with `LookAheadError`, a panel that holds an OFR value from before
`FIRST_PUBLIC` (`dvp_segment.require_ofr_public`, #522). Each new column draws on its series' own
source field, so the as-of rule reads it at that source's release lag.

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`: no published panel, declaration or
record reads these columns. Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from . import dvp_segment
from .data import DailyObservation
from .ingest import OFR_STFM_SEGMENTS_SOURCE_ID

__all__ = ["COLUMNS", "COLUMN_FIELDS", "FIRST_PUBLIC", "RAW_FIELDS", "SERIES", "add_columns"]

#: First day the OFR's values were public on their own date (#508).
FIRST_PUBLIC = dvp_segment.OFR_REAL_TIME_START

#: Raw panel column -> (filled column, flag column).
SERIES: Mapping[str, Tuple[str, str]] = {
    "ofr_tri_rate": ("tri_rate_filled", "tri_rate_not_yet_published"),
    "ofr_gcf_rate": ("gcf_rate_filled", "gcf_rate_not_yet_published"),
}
#: Raw panel column -> its source fields, for the as-of rule.
RAW_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    "ofr_tri_rate": ((OFR_STFM_SEGMENTS_SOURCE_ID, "REPO-TRI_AR_OO-P"),),
    "ofr_gcf_rate": ((OFR_STFM_SEGMENTS_SOURCE_ID, "REPO-GCF_AR_OO-P"),),
}
COLUMNS = tuple(column for pair in SERIES.values() for column in pair)
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    column: RAW_FIELDS[raw] for raw, pair in SERIES.items() for column in pair
}


def add_columns(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with the flag and filled columns of every series in `SERIES`; the input is not changed."""

    dvp_segment.require_ofr_public(rows)
    out: List[DailyObservation] = []
    for row in rows:
        values: Dict[str, object] = dict(row.values)
        flagged = row.date < FIRST_PUBLIC
        for raw, (filled, flag) in SERIES.items():
            value = row.values.get(raw)
            values[flag] = 1.0 if flagged else 0.0
            values[filled] = 0.0 if flagged else value
        out.append(DailyObservation(row.date, values))
    return out
