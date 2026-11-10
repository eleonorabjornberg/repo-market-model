"""The reserves ratio R and the scarcity state S as continuous inputs of (s3c-ann-net) (H7 step 2, H7f, #1526).

(s3c-ann-net) reads neither. Its scarcity state is held at its maximum (`s3c_net.constant_states`), so the sized settlement terms are the plain signed net
over USD 100 bn, and its scale and its calendar and settlement terms read no reserves series (`metadata/h7f_rs_1526.json`, `candidate_reads`). This module
builds the two missing readings and serves them to `spread_mr_state_calendar` as extra terms, as `s3c_satiation` serves the satiation distance (#1507):

* **R**, `rs_reserves_ratio`: `scarcity.reserves_ratio` of the reserve balances over the H.8 total assets of all commercial banks, each read at its own latest
  row public at the decision instant. Served as `rs_ratio`, in percentage points.
* **S**, `rs_scarcity_state`: `scarcity.reserve_scarcity_state` of those two legs and the day's ON RRP, which is read at its own latest public row too (the
  own-leg read of #586, Eleonora's ruling on #571): 0 (abundant) to 3 (scarce), a hole when a leg is one. Served as `rs_state`, the state over 3
  (`spread_mr_state_calendar.level`), so 0 on the floor and 1 when scarce.

**Alignment.** Both are states of the *decision* row, not scheduled fields of the target row. The value at target row `row` for a lead-`lead` decision is the
column at `row - lead`, the decision row of the direct pair; a forecast made at decision row `d` reads the column at `d` whatever the lead (as
`s3c_satiation`). Row `i`'s columns read rows `0..i` only, through the rule with the scored row `i + 1`, exactly as a forecast made at `i` would; the legs are
checked to be public at the decision instant (`_require_public`), and `check_rs_no_future` refuses a column that depends on a later row. A training pair whose
decision row has no value is a data error (`ValueError`); a forecast whose decision row has none serves `{}` and enters at 0.

The caller holds `scarcity.measurement_declaration()` (the legs' declarations) and, for the per-release read of the H.4.1 legs, `h41_release.release_dating()`.
Stdlib only.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Sequence, Tuple

from . import scarcity, spread_mr_state_calendar as sc
from .asof import InformationRule
from .data import DailyObservation
from .satiation import _extended as extended_dates
from .splits import LookAheadError, SplitError

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "read_legs": (
        "not_entry",
        "reads the three legs the as-of rule gives one panel row's decision (#1526); scores nothing, "
        "`_values` (its only caller) reads no row after the declared last day, `build_rs_columns` "
        "takes that day as an argument, and `scripts/h7f_rs_1526.py` passes its fixed LAST_DAY",
    ),
}

__all__ = [
    "LEGS", "RATIO_COLUMN", "RSTable", "STATE_COLUMN", "TERMS", "build_rs_columns", "check_rs_no_future", "extended_dates", "merged", "read_legs",
]

#: The three legs of the scarcity state; the ratio needs the first two.
LEGS: Tuple[str, ...] = scarcity.LEGS
RATIO_COLUMN = "rs_reserves_ratio"
STATE_COLUMN = "rs_scarcity_state"
#: Term name -> (panel column, factor to the served unit). R is read in percentage points; S as `state / 3`.
TERMS: Dict[str, Tuple[str, float]] = {
    sc.RS_RATIO: (RATIO_COLUMN, 100.0),
    sc.RS_STATE: (STATE_COLUMN, 1.0 / sc.STATE_MAX),
}


def _require_public(info) -> None:
    """Every leg read was public at the decision instant.

    Raises:
        LookAheadError: a leg read at a row public after the decision instant, or a read with no publication instant.
    """

    for read in info.reads:
        if read.feature in LEGS and (read.available_at is None or read.available_at > info.decision_instant):
            raise LookAheadError(
                f"the {read.feature!r} leg of R and S is read at a row public at {read.available_at}, after the {info.decision_instant} decision"
            )


def read_legs(
    rows: Sequence[DailyObservation], dates: Sequence[date], i: int, rule: InformationRule
) -> Optional[Dict[str, Optional[float]]]:
    """The three legs as a forecast made at row `i` reads them, each at its own latest public row; `None` if the rule reads none of them.

    Raises:
        LookAheadError: a leg read is not public at the decision instant.
    """

    try:
        info = rule.information_set(extended_dates(dates, i), i + 1)
    except SplitError:
        return None
    _require_public(info)
    read = {r.feature: r.row for r in info.reads}
    if any(leg not in read for leg in LEGS):
        return None
    out: Dict[str, Optional[float]] = {}
    for leg in LEGS:
        value = rows[read[leg]].values.get(leg)
        out[leg] = None if value is None else float(value)
    return out


def _values(rows: Sequence[DailyObservation], rule: InformationRule, last_day: date) -> List[Tuple[Optional[float], Optional[float]]]:
    dates = [row.date for row in rows]
    out: List[Tuple[Optional[float], Optional[float]]] = []
    for i, row in enumerate(rows):
        legs = None if row.date > last_day else read_legs(rows, dates, i, rule)
        if legs is None:
            out.append((None, None))
            continue
        reserves, assets, on_rrp = legs["reserve_balances"], legs["bank_total_assets"], legs["on_rrp"]
        ratio = None if reserves is None or assets is None else scarcity.reserves_ratio(reserves, assets)
        state = scarcity.reserve_scarcity_state(reserves, assets, on_rrp)
        out.append((ratio, None if state is None else float(state)))
    return out


def build_rs_columns(rows: Sequence[DailyObservation], rule: InformationRule, *, last_day: date) -> List[DailyObservation]:
    """`rows` with `rs_reserves_ratio` and `rs_scarcity_state`, for rows to `last_day`; a later row's values are `None`.

    Row `i` carries what a forecast made at `i` reads; only rows up to `i` are read.
    """

    values = _values(rows, rule, last_day)
    out = []
    for i, row in enumerate(rows):
        ratio, state = values[i]
        columns = dict(row.values)
        columns[RATIO_COLUMN], columns[STATE_COLUMN] = ratio, state
        out.append(DailyObservation(row.date, columns))
    return out


def check_rs_no_future(
    rows: Sequence[DailyObservation], built: Sequence[DailyObservation], rule: InformationRule, *, last_day: date, indices: Sequence[int]
) -> None:
    """Refuse a built column that is not what the panel cut at its own row gives.

    Raises:
        LookAheadError: a checked row's R or S differs from the same row rebuilt from `rows` up to and including it, so it depended on a later row.
    """

    for i in indices:
        if rows[i].date > last_day:
            continue
        again = build_rs_columns(rows[: i + 1], rule, last_day=last_day)[i]
        for column in (RATIO_COLUMN, STATE_COLUMN):
            have, want = built[i].values.get(column), again.values.get(column)
            if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-12):
                raise LookAheadError(
                    f"{column} on {rows[i].date.isoformat()} is {have}, but the panel cut at that row gives {want}; the column depended on a later row"
                )


class RSTable:
    """One of the two columns at every panel row, as `spread_mr_state_calendar.walk`'s `iorb` argument reads a table (`at`, `read`).

    `rows` are the panel rows carrying the built columns (`build_rs_columns`), in the walk's panel order; `term` is `sc.RS_RATIO` or `sc.RS_STATE`.
    """

    def __init__(self, rows: Sequence[DailyObservation], term: str):
        if term not in TERMS:
            raise ValueError(f"unknown R/S term {term!r}; expected one of {sorted(TERMS)}")
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

        Mutation record: see `tests/test_s3c_rs.py` (`RSTable.read`).
        """

        value = self._value(decision_index)
        return {} if value is None else {self.term: value}


def merged(rows: Sequence[DailyObservation]):
    """Both terms served as one table (`s3c_satiation.MergedTable`)."""

    from .s3c_satiation import MergedTable

    return MergedTable(RSTable(rows, sc.RS_RATIO), RSTable(rows, sc.RS_STATE))
