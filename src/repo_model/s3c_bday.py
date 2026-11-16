"""(s3c-ann-net) with business day 1, 2 and 3 after a month-end as three columns in place of the one post-month-end flag (#1631; H5 step 4, development arm;
avenue #1627; her ruling of 16 November 2026, docket card a1627-bday-split-1116, option (a)).

`metadata/bday_columns_1631.json` is the declaration. The candidate's `post_month_end_window` term is one flag, `bday_of_month <= 3`
(`metadata/calendar_mr_1115.json`, carried by `metadata/state_calendar_1145.json`). The arms are `s3c_announced.ANN_NET_ARM` with that term taken out
of the fit and replaced by extra terms of `spread_mr_state_calendar` that `BdayTable` serves through the `iorb` argument of `spread_mr_state_calendar.walk`
(`at` for a training pair, `read` for a forecast), beside the net table that the arm's `sized` terms read through `sizes`:

* `PRIMARY`: `bday_1`, `bday_2`, `bday_3`, one 0/1 column per business day, uncrossed;
* `SECONDARY` (declared, never the primary): the six columns `bday_b_quarter` and `bday_b_other`, the business day crossed with the kind of the month-end
  before it (the target falls in January, April, July or October: 'quarter');
* `CONTROL_ARM`: the one column `bday_le3` in the place of the flag; the same column, so it must reproduce the candidate's forecasts exactly (the check of
  the walk, not an arm that is scored).

Nothing in `spread_mr_calendar`, `s3c_net`, `s3c_announced`, `metadata/sources.json` or any published declaration is edited, and no published declaration,
record or live path reads this module. `spread_mr_state_calendar` gains only the names (`BDAY_EXTRAS`), so that the pool and the shift read them as extras.

**Information set.** Every column is a function of the target row's own date and the market holiday table, as `post_month_end_window` is: always public.
A forecast reads the target row of its decision (`spread_mr_calendar.target_row`), a training pair the target row of the pair (`training_pairs="direct"`,
`TRAINING_PAIRS`), never the origin row: a one-step fit would learn the day one row off (the #914 class; `fit_state_terms` raises `ValueError` for it).

Stdlib only.
"""

from __future__ import annotations

import dataclasses
from typing import Dict, Sequence

from . import derived_features, s3c_announced
from . import spread_mr_calendar as cal
from . import spread_mr_state_calendar as sc
from .data import DailyObservation

__all__ = ["BDAY_EXTRAS", "BdayTable", "CONTROL", "CONTROL_ARM", "CONTROL_EXTRAS", "PRIMARY", "QUARTER_EXTRAS", "QUARTER_MONTHS", "SECONDARY", "TRAINING_PAIRS",
           "business_day", "columns_of"]

#: The fit trains on direct pairs only (`one_step_guard` holds, no allow-list entry).
TRAINING_PAIRS = "direct"
#: The month-ends that close a quarter: a target day in the month after is in the 'quarter' kind.
QUARTER_MONTHS = (1, 4, 7, 10)
BDAY_EXTRAS = ("bday_1", "bday_2", "bday_3")
QUARTER_EXTRAS = tuple(f"bday_{b}_{kind}" for kind in ("quarter", "other") for b in (1, 2, 3))
CONTROL = "bday_le3"
CONTROL_EXTRAS = (CONTROL,)

_WITHOUT_FLAG = tuple(name for name in s3c_announced.ANN_NET_ARM.location if name != "post_month_end_window")
_BASE = s3c_announced.ANN_NET_ARM
#: (s3c-ann-net-bday): the three uncrossed business-day columns in place of `post_month_end_window`. Everything else is the arm's.
PRIMARY = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_bday", role="(s3-ann-net-bday) (s3-ann-net) with business day 1, 2 and 3 after a month-end as three columns",
    location=_WITHOUT_FLAG, extra=BDAY_EXTRAS,
)
#: The declared secondary: the six columns of the business day crossed with the kind of the month-end before.
SECONDARY = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_bday_q", role="(s3-ann-net-bday-q) the business-day columns crossed with the quarter-end kind (secondary)",
    location=_WITHOUT_FLAG, extra=QUARTER_EXTRAS,
)
#: The control: the candidate's own single column, as an extra. It must reproduce the candidate.
CONTROL_ARM = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_bday_le3", role="(s3-ann-net-bday-le3) the candidate's one flag served as an extra: the check that the path changes nothing",
    location=_WITHOUT_FLAG, extra=CONTROL_EXTRAS,
)


def business_day(day) -> int:
    """The market business day of the month of `day` (`derived_features.bday_of_month`, the count `post_month_end_window` reads)."""

    return int(derived_features.bday_of_month(day))


def columns_of(day) -> Dict[str, float]:
    """Every column of the arms at target day `day`: a function of its own date and the market holiday table.

    `bday_b` is 1 on business day b (b = 1, 2, 3); `bday_b_quarter` / `bday_b_other` the same by the kind of the month-end before (the month of `day` in
    `QUARTER_MONTHS`); `bday_le3` is 1 when the business day count is 3 or less, the candidate's flag.
    """

    b = business_day(day)
    kind = "quarter" if day.month in QUARTER_MONTHS else "other"
    out: Dict[str, float] = {f"bday_{i}": 1.0 if b == i else 0.0 for i in (1, 2, 3)}
    for i in (1, 2, 3):
        for k in ("quarter", "other"):
            out[f"bday_{i}_{k}"] = 1.0 if (b == i and kind == k) else 0.0
    out[CONTROL] = 1.0 if b <= 3 else 0.0
    return out


class BdayTable:
    """The business-day columns at every panel row; the `iorb` table of `sc.walk`. Each is read from the target row's own date, at every lead."""

    def __init__(self, panel: Sequence[DailyObservation]):
        self.dates = [row.date for row in panel]
        self._columns = [columns_of(d) for d in self.dates]

    def at(self, lead: int, row: int) -> Dict[str, float]:
        """The columns of target row `row` for a lead-`lead` decision (a training row: public by construction)."""

        return dict(self._columns[row])

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The columns a forecast of the decision on row `decision_index` at `lead` reads, from its target row.

        Raises:
            ValueError: the target row is not in the panel (its date is not known here).

        Mutation record: see `tests/test_s3c_bday.py` (`BdayTable.read`, `BdayTable.at`).
        """

        row = cal.target_row(decision_index, lead)
        if row >= len(self.dates):
            raise ValueError(f"the target row {row} of the decision on row {decision_index} at lead {lead} is not in the panel")
        return self.at(lead, row)
