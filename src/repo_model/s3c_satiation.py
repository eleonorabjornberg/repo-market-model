"""The daily as-of satiation distance as a continuous input of (s3c-ann-net) (H5 step 2 follow-up, #1507).

`repo_model.satiation.build_distance_columns` (#598) builds two panel columns, `satiation_dist_roll` (the reserves-to-assets ratio the as-of rule reads at a
row's own decision minus the rolling satiation level) and `satiation_hinge_roll` (the percentage points by which the ratio is below the level). Each row's
value is public at that row's own decision (zero lag): row `i` reads rows `0..i` only, and `satiation.check_distance_no_future` refuses a column that does
not. `SatiationTable` serves one of them to `spread_mr_state_calendar` as an extra term, in percentage points, as
`spread_mr_state_calendar.walk`'s `iorb` argument reads a table (`at` for a training pair, `read` for a forecast).

**Alignment.** A column is a state of the *decision* row, not a scheduled field of the target row. The value at target row `row` for a lead-`lead` decision
is the column at row `row - lead`, the decision row of the direct pair (as `s3c_h9.TargetForecastTable`); a forecast made at decision row `d` reads the
column at `d` whatever the lead. A training pair whose decision row has no value is a data error (`ValueError`); a forecast whose decision row has none
serves `{}` and enters at 0. Standard library only.
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence

from . import satiation, spread_mr_state_calendar as sc
from .data import DailyObservation

__all__ = ["MergedTable", "PERCENTAGE_POINTS", "SatiationTable", "TERMS"]

#: The columns are ratios (0.12 is 12 per cent) except the hinge, which is already in percentage points; the distance is read in percentage points.
PERCENTAGE_POINTS = 100.0
#: Term name -> (panel column, factor to percentage points).
TERMS = {
    sc.SATIATION_DIST: (satiation.DISTANCE_COLUMN, PERCENTAGE_POINTS),
    sc.SATIATION_HINGE: (satiation.HINGE_COLUMN, 1.0),
}


class SatiationTable:
    """One satiation column at every panel row, as `spread_mr_state_calendar.walk`'s `iorb` argument reads it.

    `rows` are the panel rows carrying the built columns (`satiation.build_distance_columns`), in the walk's panel order; `term` is `SATIATION_DIST` or
    `SATIATION_HINGE`.
    """

    def __init__(self, rows: Sequence[DailyObservation], term: str):
        if term not in TERMS:
            raise ValueError(f"unknown satiation term {term!r}; expected one of {sorted(TERMS)}")
        column, factor = TERMS[term]
        self.term = term
        self.dates = [row.date for row in rows]
        self._values = [None if row.values.get(column) is None else float(row.values[column]) * factor for row in rows]

    def _value(self, decision_row: int) -> Optional[float]:
        if decision_row < 0 or decision_row >= len(self._values):
            return None
        return self._values[decision_row]

    def at(self, lead: int, row: int) -> Dict[str, float]:
        """The term at target row `row` for a decision `lead` rows before (a training row): the column at the decision row `row - lead`.

        Raises:
            ValueError: the decision row has no value (a training pair must have it).
        """

        value = self._value(row - lead)
        if value is None:
            raise ValueError(f"no {self.term} at the decision row {row - lead} of the lead-{lead} pair with target row {row}")
        return {self.term: value}

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The term a forecast of the decision on row `decision_index` reads: that row's own column, whatever the lead; `{}` where it has none.

        Mutation record: see `tests/test_s3c_satiation.py` (`SatiationTable.read`).
        """

        value = self._value(decision_index)
        return {} if value is None else {self.term: value}


class MergedTable:
    """Several tables served as one (`spread_mr_state_calendar.walk` takes one `iorb` table): the union of their terms; an arm reads the terms it names."""

    def __init__(self, *tables: SatiationTable):
        if not tables:
            raise ValueError("a merged table needs at least one table")
        self.tables = tables
        self.dates = list(tables[0].dates)

    def at(self, lead: int, row: int) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for table in self.tables:
            out.update(table.at(lead, row))
        return out

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for table in self.tables:
            out.update(table.read(lead, decision_index))
        return out
