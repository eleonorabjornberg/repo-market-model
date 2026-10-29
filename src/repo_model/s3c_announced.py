"""(s3c-ann) and (s3c-ann-net): the settlement terms of (s3c) read at leads 2 to 5 from the auction announcement (#1288; H5 step 3, ledger
item 71 on #1116; her ruling of 28 October 2026 on avenue #1286).

(s3c)'s two settlement terms, `settlement_coupon` and `settlement_bill`, are scheduled fields of the *target* row
(`spread_mr_calendar.TERMS`: scheduled, span `(0,)`). `metadata/sources.json` declares a settlement public at 15:00 on the panel day before it
settles, so `spread_mr_calendar.readable_offsets` keeps the terms at lead 1 only, and at leads 2 to 5 (four of the five leads of the primary
score) (s3c) cannot see a settlement announced days earlier. `metadata/settlement_announcement_dating.json` (#541, measured and off) dates a
settlement from its auction's announcement instead: 12:00 on the `announcemt_date`. These two arms read that dating as a measurement. Nothing in
`spread_mr_calendar`, `spread_mr_state_calendar`, `s3c_net`, `metadata/sources.json` or the dating declaration is edited, and no published
declaration reads this module.

* `AnnouncedTermTable` is `spread_mr_calendar.TermTable` with the two settlement flags served at every lead. At lead `h` the flag of target day
  `T` is 1 when the coupon (bill) auctions settling on `T` that had been announced by the decision instant of day `T - h` (16:00, the published
  records' decision time) offer more than zero in total. At lead 1 it is the panel's flag exactly as (s3c) reads it (the dating declaration
  states the two agree at lead 1; the study compares them). `legs` admits one leg alone at leads 2 to 5, for the reference walks that report
  the coupon and the bill leg separately.
* `AnnouncedNetSizeTable` is #1273's `s3c_net.NetSizeTable` (the signed net of the target day in USD 100 bn, each figure read at its
  announcement) served at every lead.
* `ANN_ARM`, `ANN_NET_ARM`, `COUPON_ARM` and `BILL_ARM` are (s3) and (s3-net) under their own names; the fit is `spread_mr_state_calendar`'s,
  unchanged, on direct pairs (`TRAINING_PAIRS`), so `one_step_guard` holds with no allow-list entry.

**Information set.** A figure for target `T` at lead `h` counts an auction only when its announcement (12:00 on its `announcemt_date`) is at or
before 16:00 on the panel day `h` rows before `T`. A training pair reads the figure of its own decision, `T - h`, so a training figure and a
forecast figure are the same function of the same announcements. `read` re-checks the figure it serves against the decision it is asked for:
a figure that counts an auction announced after that decision raises `LookAheadError`, one that leaves an announced auction out raises
`StaleReadError` (the analogue of `settlement_dating.check_known_columns`). Lens E's caveat (item G) applies to the bill leg: Treasury publishes
no clock time for an announcement, and a cash management bill is ad hoc, announced the same or the previous day; the 12:00 instant is
unverified.

Stdlib only.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime, time
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .decision_instant import DECISION_TIME
from . import announced_iorb, fomc_calendar
from . import settlement_dating as sd
from . import spread_mr_calendar as cal
from . import spread_mr_state_calendar as sc
from . import s3c_net
from .asof import StaleReadError
from .data import DailyObservation
from .splits import LookAheadError

__all__ = [
    "ANN_ARM", "ANN_NET_ARM", "BILL_ARM", "COLUMN", "COUPON_ARM", "LEGS", "TRAINING_PAIRS",
    "AnnouncedNetSizeTable", "AnnouncedTermTable",
]

#: The fit trains on direct pairs only: the settlement terms are read at the target day (`one_step_guard` holds, no allow-list entry).
TRAINING_PAIRS = "direct"
#: The two settlement legs, as terms of `spread_mr_calendar.TERMS`.
LEGS: Tuple[str, ...] = ("settlement_coupon", "settlement_bill")
#: The panel column each leg is dated from (`settlement_dating.AuctionResult.column`).
COLUMN: Mapping[str, str] = {"settlement_coupon": "treasury_settlement_coupons", "settlement_bill": "treasury_settlement_bills"}

#: (s3c-ann): (s3) of #1145 with its settlement flags announced at leads 2 to 5. The arm is (s3)'s; what differs is the table that serves its flags.
ANN_ARM = dataclasses.replace(
    sc.ARMS[2], name="sc_s3_ann", role="(s3-ann) (s3) with the settlement flags read at leads 2 to 5 from the auction announcement"
)
#: (s3c-ann-net): #1273's net arm (signed net settlement in USD 100 bn, state held at its maximum) with the net announced at leads 2 to 5.
ANN_NET_ARM = dataclasses.replace(
    s3c_net.NET_ARM, name="sc_s3_ann_net",
    role="(s3-ann-net) (s3-net) with the net settlement read at leads 2 to 5 from the auction announcement",
)
#: The leg references of (s3c-ann): one flag announced at leads 2 to 5, the other at lead 1 only.
COUPON_ARM = dataclasses.replace(ANN_ARM, name="sc_s3_ann_coupon", role="(s3-ann-coupon) (s3-ann) with the coupon flag alone announced")
BILL_ARM = dataclasses.replace(ANN_ARM, name="sc_s3_ann_bill", role="(s3-ann-bill) (s3-ann) with the bill flag alone announced")


def _by_day(results: Sequence[sd.AuctionResult]) -> Dict[date, List[sd.AuctionResult]]:
    out: Dict[date, List[sd.AuctionResult]] = {}
    for item in results:
        out.setdefault(item.settles, []).append(item)
    return out


class AnnouncedTermTable(cal.TermTable):
    """`spread_mr_calendar.TermTable` with the settlement flags in `legs` served at every lead from the auction announcement.

    The flag for target row `row` read at lead `lead` is 1 when the auctions of the leg's column settling on `dates[row]` that were announced
    at or before the decision instant of row `row - lead` offer more than zero. A row with no decision row `lead` rows before (`row < lead`)
    reads 0. Lead 1 and every other term are the base table's, so at lead 1 the table is (s3c)'s own.
    """

    def __init__(
        self,
        panel: Sequence[DailyObservation],
        announcements: Sequence[announced_iorb.IorbAnnouncement],
        results: Sequence[sd.AuctionResult],
        calendar: Optional[Sequence[fomc_calendar.Meeting]] = None,
        *,
        legs: Sequence[str] = LEGS,
        decision_time: time = DECISION_TIME,
    ):
        unknown = [name for name in legs if name not in LEGS]
        if unknown:
            raise ValueError(f"legs must be among {list(LEGS)}, got {unknown}")
        super().__init__(panel, announcements, calendar, decision_time=decision_time)
        self.legs = tuple(name for name in LEGS if name in legs)
        self._time = decision_time
        self._results = _by_day(results)
        self._counted_cache: Dict[Tuple[int, int], Dict[str, Tuple[sd.AuctionResult, ...]]] = {}

    # -- what is counted -----------------------------------------------------------------------------------------------

    def _counted(self, lead: int, row: int) -> Dict[str, Tuple[sd.AuctionResult, ...]]:
        """The auctions of each leg settling on `dates[row]` that were announced by the decision `lead` rows before it.

        Mutation record: see `tests/test_s3c_announced.py` (`AnnouncedTermTable._counted`).
        """

        key = (lead, row)
        if key not in self._counted_cache:
            if row - lead < 0:
                self._counted_cache[key] = {name: () for name in LEGS}
            else:
                instant = datetime.combine(self.dates[row - lead], self._time)
                settling = self._results.get(self.dates[row], ())
                self._counted_cache[key] = {
                    name: tuple(r for r in settling if r.column == COLUMN[name] and r.public_at is not None and r.public_at <= instant)
                    for name in LEGS
                }
        return self._counted_cache[key]

    def _flag(self, lead: int, row: int, name: str) -> int:
        return 1 if sum(r.amount for r in self._counted(lead, row)[name]) > 0.0 else 0

    def _announced_leg(self, name: str, lead: int) -> bool:
        return lead >= 2 and name in self.legs

    def _settlement_flags(self, lead: int, row: int) -> Dict[str, int]:
        return {name: self._flag(lead, row, name) for name in LEGS if self._announced_leg(name, lead)}

    # -- the table's interface -----------------------------------------------------------------------------------------

    def flag(self, term: str, lead: int, row: int) -> Optional[int]:
        if term in LEGS and self._announced_leg(term, lead):
            return self._flag(lead, row, term)
        return super().flag(term, lead, row)

    def flags_at(self, lead: int, row: int) -> Dict[str, int]:
        """The flags of the terms readable at `lead` at row `row` (a training row), with the announced settlement flags added."""

        base = super().flags_at(lead, row)
        base.update(self._settlement_flags(lead, row))
        return base

    def read(self, lead: int, decision_index: int) -> Dict[str, int]:
        """The flags a forecast of the decision on row `decision_index` at `lead` reads, from the target row.

        Raises:
            LookAheadError: a scheduled field of a row that is not public at the decision (`require_public`), or a settlement figure that
                counts an auction announced after the decision instant.
            StaleReadError: a settlement figure that leaves out an auction announced by the decision instant.
        """

        out = super().read(lead, decision_index)
        row = cal.target_row(decision_index, lead)
        instant = datetime.combine(self.dates[decision_index], self._time)
        counted = self._counted(lead, row)
        settling = self._results.get(self.dates[row], ())
        for name in LEGS:
            if not self._announced_leg(name, lead):
                continue
            for item in counted[name]:
                if item.public_at is None or item.public_at > instant:
                    raise LookAheadError(
                        f"term {name!r} for {self.dates[row]} counts an auction announced at {item.public_at}, after the decision "
                        f"instant {instant} of the forecast made {lead} panel day(s) ahead"
                    )
            for item in settling:
                if item.column == COLUMN[name] and item.public_at is not None and item.public_at <= instant and item not in counted[name]:
                    raise StaleReadError(
                        f"term {name!r} for {self.dates[row]} leaves out an auction announced at {item.public_at}, by the decision "
                        f"instant {instant}"
                    )
            out[name] = self._flag(lead, row, name)
        return out


class AnnouncedNetSizeTable(s3c_net.NetSizeTable):
    """#1273's net settlement by term, served at every lead: the net of target row `row` as announced at the decision `lead` rows before.

    Same interface as `s3c_net.NetSizeTable` (`sizes_at`, `read`), which the sized arm calls; lead 1 is that table's. The figure counts an
    auction only when it was announced by the decision instant, and a class announced in part reads 0 until fully announced
    (`net_settlement.net_for_day`).
    """

    def sizes_at(self, lead: int, row: int) -> Dict[str, float]:
        """The net of every sized term at target row `row` as the decision `lead` rows earlier read it (a training row: public by construction).

        Mutation record: see `tests/test_s3c_announced.py` (`AnnouncedNetSizeTable.sizes_at`).
        """

        value = self._value(row - lead, row)
        return {name: value[name] for name in sc.SIZED_TERMS}

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The sizes a forecast of the decision on row `decision_index` at `lead` reads, from its target row.

        Raises:
            LookAheadError: the figure is not the net announced at the decision instant (it counts an announcement made later, or not yet made).
        """

        row = cal.target_row(decision_index, lead)
        out = self.sizes_at(lead, row)
        instant = datetime.combine(self.dates[decision_index], self._time)
        announced = s3c_net.net_by_term(self._by_day.get(self.dates[row], ()), instant)
        for name in sc.SIZED_TERMS:
            if abs(out[name] - announced[name]) > 1e-9:
                raise LookAheadError(
                    f"net {name!r} for {self.dates[row]} is {out[name]}, but {announced[name]} was announced by the decision instant "
                    f"{instant} of the forecast made {lead} panel day(s) ahead"
                )
        return out
