"""(s3c-ann-net-bill): (s3c-ann-net) with the 4-week bill rate less IORB of the previous business day as one more term (#1346; H5 step 3,
ledger item 97; her ruling of 1 November 2026).

`metadata/s3c_bill_iorb_1346.json` is the declaration. The arm is `s3c_announced.ANN_NET_ARM`, (s3c)'s announced-net arm, with one extra term of
the fit, `spread_mr_state_calendar.BILL_LESS_IORB`: for the decision on panel row `d`, `(tbill_4w - iorb) x 100 / UNIT_BPS` read from row `d - 1`,
the same figure at every lead. `BillLessIorbTable` serves it through the `iorb` argument of `spread_mr_state_calendar.walk` (`at` for a training
pair, `read` for a forecast), beside the net table that the arm's `sized` terms read through `sizes`. Nothing in `spread_mr_calendar`,
`spread_mr_state_calendar` (beyond the name of the term), `s3c_net`, `s3c_announced`, `metadata/sources.json` or any published declaration is
edited, and no published declaration, record or live path reads this module.

**Information set.** The panel row `r` holds the bill rate and IORB dated `r`. `metadata/sources.json` declares `treasury_bill_rates` public at
16:30 on the day it is dated, so at the 16:00 decision of the published records the latest bill row is the previous business day's, and at the
18:00 decision of `repo_model.decision_instant` it would be the decision day's own (the same-day posting time that #1334 asks to measure, and that
this arm does not use). The arm reads row `d - 1` at both instants: `source_row` is the row of a figure, `read` re-derives it from the decision
and refuses one that is not the previous business day's, with `LookAheadError` when it is the decision day's own row or later and
`StaleReadError` when it is older. A training pair reads the figure of its own decision (target row less lead), so a training figure and a
forecast figure are the same function of the same rows. The fit is on direct pairs (`TRAINING_PAIRS`), so `one_step_guard` holds with no
allow-list entry.

Stdlib only.
"""

from __future__ import annotations

import dataclasses
from typing import Dict, Sequence

from . import s3c_announced
from . import spread_mr_calendar as cal
from . import spread_mr_state_calendar as sc
from .asof import StaleReadError
from .data import DailyObservation
from .splits import LookAheadError

__all__ = ["BILL_ARM", "BillLessIorbTable", "TRAINING_PAIRS", "UNIT_BPS"]

#: The fit trains on direct pairs only (`one_step_guard` holds, no allow-list entry).
TRAINING_PAIRS = "direct"
#: The term is read in units of 10 bp (a bill rate 25 bp above IORB reads 2.5).
UNIT_BPS = 10.0
#: (s3c-ann-net-bill): (s3c-ann-net)'s arm with the one price term. Everything else is the arm's.
BILL_ARM = dataclasses.replace(
    s3c_announced.ANN_NET_ARM, name="sc_s3_ann_net_bill",
    role="(s3-ann-net-bill) (s3-ann-net) with the 4-week bill rate less IORB of the previous business day",
    extra=(sc.BILL_LESS_IORB,),
)


class BillLessIorbTable:
    """`bill_less_iorb` at every panel row, as the decision `lead` rows before could read it; the `iorb` table of `sc.walk`.

    The figure for target row `row` at `lead` is read from panel row `row - lead - 1`: the previous business day of the decision on row
    `row - lead`. A row with no such row reads nothing (`{}`).
    """

    def __init__(self, panel: Sequence[DailyObservation]):
        self.dates = [row.date for row in panel]
        self._bill = [row.values.get("tbill_4w") for row in panel]
        self._iorb = [row.values.get("iorb") for row in panel]

    def source_row(self, lead: int, row: int) -> int:
        """The panel row the figure of target row `row` at `lead` is read from: the previous business day of the decision `lead` rows before.

        Mutation record: see `tests/test_s3c_bill_iorb.py` (`BillLessIorbTable.source_row`).
        """

        return row - lead - 1

    def _figure(self, source: int) -> float:
        bill, iorb = self._bill[source], self._iorb[source]
        if bill is None or iorb is None:
            raise ValueError(f"the 4-week bill rate or IORB of {self.dates[source]} is missing; the term is read from the previous business day")
        return (float(bill) - float(iorb)) * 100.0 / UNIT_BPS

    def at(self, lead: int, row: int) -> Dict[str, float]:
        """The term at target row `row` for a lead-`lead` decision (a training row: public by construction); `{}` with no previous row."""

        source = self.source_row(lead, row)
        if source < 0:
            return {}
        return {sc.BILL_LESS_IORB: self._figure(source)}

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The term a forecast of the decision on row `decision_index` at `lead` reads, from its target row.

        Raises:
            LookAheadError: the figure is read from the decision day's own row or a later one.
            StaleReadError: the figure is read from an older row than the previous business day of the decision.
        """

        row = cal.target_row(decision_index, lead)
        source = self.source_row(lead, row)
        if source < 0:
            return {}
        if source >= decision_index:
            raise LookAheadError(
                f"term {sc.BILL_LESS_IORB!r} for {self.dates[row]} is read from {self.dates[source]}, which is not before the decision day "
                f"{self.dates[decision_index]}: only the previous business day's bill rate is read"
            )
        if source < decision_index - 1:
            raise StaleReadError(
                f"term {sc.BILL_LESS_IORB!r} for {self.dates[row]} is read from {self.dates[source]}, but the previous business day of the "
                f"decision on {self.dates[decision_index]} is {self.dates[decision_index - 1]}"
            )
        return self.at(lead, row)
