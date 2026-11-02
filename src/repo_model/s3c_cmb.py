"""(s3c-ann-net-cmb): the bill leg of (s3c-ann-net) split into regular bills and cash management bills, the latter given a term of their own
(#1356; H5 step 3; her ruling of 2 November 2026 on avenue #1306).

(s3c-ann-net) (`repo_model.s3c_announced.ANN_NET_ARM`) reads two settlement terms at every lead, the announced signed net coupon and the announced
signed net bill settlement of the target day, in USD 100 bn. The bill net treats a cash management bill (CMB) as one more bill. This module splits
it, and nothing else:

* `CmbSizeTable` is `s3c_announced.AnnouncedNetSizeTable` with the bill term of leads 2 to 5 replaced by the net of the **regular bills** (the
  bill net with the announced cash management bills left out). The coupon term is unchanged. At lead 1 it is that table exactly: the CMB term
  is read at leads 2 to 5, as the avenue states, and lead 1 is (s3c-ann-net)'s own.
* `CmbTerms` serves the **cash management bill term** as an extra term of the fit (`spread_mr_state_calendar.CMB_EXTRAS`, read through `walk`'s
  `iorb` argument), at leads 2 to 5: `cmb_flag`, 1 when the announced offering of the cash management bills settling on the target day is more
  than zero, or `cmb_net`, what the announced cash management bills add to the bill net, in USD 100 bn.

The split is exact: the regular bill net and `cmb_net` add up to the bill net of `net_settlement.net_for_day`, at every instant, so that the
arm's span contains (s3c-ann-net)'s (the two coefficients equal give the same shift). `cmb_net` is the cash management bills' offering when
regular bills settle with them (the maturing amount of the class is one total, netted once, against the regular bills); on a day only cash
management bills settle, it carries the class's whole net, the maturing amount included. A class announced in part reads 0 in both legs
(#679, #738): the unannounced cash management bills of the day are not in the schedule, so they do not make the class partly announced.

**Information set.** A figure for target `T` at lead `h` counts an auction only when its announcement (12:00 on its `announcemt_date`,
`metadata/net_settlement.json`) is at or before the decision instant of the panel day `T - h` (`repo_model.decision_instant`, 18:00). A
training pair reads the figure of its own decision. `CmbTerms.read` re-derives the figure from the announced auctions at the decision instant:
a figure that counts an auction announced after it raises `LookAheadError`; a flag that leaves out an announced cash management bill raises
`StaleReadError`. **Finding #1301:** Treasury's announcement files state no release time for 163 announcements ("for immediate release"), 153 of
them cash management bills, so the 12:00 stamp of a cash management bill announced on the decision day itself is unverified. `prior_day_only`
is the reading that does not rely on it: a cash management bill counts only when it was announced before the decision day (and is otherwise left
out of the bill net and of the term, as if unannounced). The sensitivity arms read that way; the arms of the declared reading count the stamp.

Stdlib only.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime
from typing import Dict, List, Mapping, Sequence, Tuple

from . import net_settlement as ns
from . import spread_mr_calendar as cal
from . import spread_mr_state_calendar as sc
from . import s3c_announced
from .asof import StaleReadError
from .splits import LookAheadError

__all__ = [
    "FLAG_ARM", "FLAG_PRIOR_ARM", "SIZE_ARM", "SIZE_PRIOR_ARM", "TRAINING_PAIRS", "CmbSizeTable", "CmbTerms", "cmb_values", "split_bill_net",
]

#: The fit trains on direct pairs only (`one_step_guard` holds, no allow-list entry).
TRAINING_PAIRS = "direct"
#: The cash management bill term is read at these leads; lead 1 is (s3c-ann-net)'s.
CMB_LEADS = (2, 3, 4, 5)

#: (s3c-ann-net) with the cash management bill flag as an extra term, the bill leg of the sized terms being the regular bills.
FLAG_ARM = dataclasses.replace(
    s3c_announced.ANN_NET_ARM, name="sc_s3_ann_net_cmb_flag", extra=(sc.CMB_FLAG,),
    role="(s3-ann-net-cmb, flag) (s3-ann-net) with the cash management bills split out of the bill net and a 0/1 flag of their own",
)
#: (s3c-ann-net) with the cash management bill net as an extra term.
SIZE_ARM = dataclasses.replace(
    s3c_announced.ANN_NET_ARM, name="sc_s3_ann_net_cmb_size", extra=(sc.CMB_NET,),
    role="(s3-ann-net-cmb, size) (s3-ann-net) with the cash management bills split out of the bill net and a size term of their own",
)
#: The same two arms on the tables that count a cash management bill only when it was announced before the decision day (finding #1301).
FLAG_PRIOR_ARM = dataclasses.replace(FLAG_ARM, name="sc_s3_ann_net_cmb_flag_prior",
                                     role=FLAG_ARM.role + ", a cash management bill counted only when announced before the decision day")
SIZE_PRIOR_ARM = dataclasses.replace(SIZE_ARM, name="sc_s3_ann_net_cmb_size_prior",
                                     role=SIZE_ARM.role + ", a cash management bill counted only when announced before the decision day")


def _visible(auctions: Sequence[ns.Auction], instant: datetime, prior_day_only: bool) -> List[ns.Auction]:
    """The auctions the reading admits at `instant`: all, or all but the cash management bills announced on the decision day or later."""

    if not prior_day_only:
        return list(auctions)
    return [a for a in auctions if not (a.cmb and a.announced_at.date() >= instant.date())]


def split_bill_net(auctions: Sequence[ns.Auction], instant: datetime, *, prior_day_only: bool = False) -> Tuple[float, float]:
    """`(net of the regular bills, what the cash management bills add)` of one settlement day's auctions as announced at `instant`, in USD billions.

    The sum is the bill net of `net_settlement.net_for_day` over the same auctions.
    """

    seen = _visible(auctions, instant, prior_day_only)
    _net, bills, _unknown = ns.net_for_day(seen, instant)
    regular = ns.net_for_day([a for a in seen if not a.cmb], instant)[1]
    return regular, bills - regular


def cmb_values(auctions: Sequence[ns.Auction], instant: datetime, *, prior_day_only: bool = False) -> Dict[str, float]:
    """The split of one settlement day as announced at `instant`, in USD billions: the coupon net, the regular bill net, the cash management bill
    net (`cmb_net`) and the 0/1 flag that an announced cash management bill of positive offering settles (`cmb_flag`)."""

    seen = _visible(auctions, instant, prior_day_only)
    net, bills, _unknown = ns.net_for_day(seen, instant)
    regular, cmb_net = split_bill_net(auctions, instant, prior_day_only=prior_day_only)
    flagged = sum(a.offering for a in seen if a.cmb and a.announced_at <= instant) > 0.0
    return {"settlement_coupon": net - bills, "settlement_bill": regular, sc.CMB_NET: cmb_net, sc.CMB_FLAG: 1.0 if flagged else 0.0}


class CmbSizeTable(s3c_announced.AnnouncedNetSizeTable):
    """The sized terms of (s3c-ann-net) with the bill term read net of the cash management bills at leads 2 to 5; lead 1 is the parent's.

    Same interface as the parent (`sizes_at`, `read`), which the sized arm calls. `prior_day_only` counts a cash management bill only when it was
    announced before the decision day.
    """

    def __init__(self, panel, auctions: Sequence[ns.Auction], *, prior_day_only: bool = False, **kw):
        super().__init__(panel, auctions, **kw)
        self.prior_day_only = prior_day_only
        self._split_cache: Dict[Tuple[int, int], Dict[str, float]] = {}

    def _split(self, decision_row: int, target_row: int) -> Dict[str, float]:
        """`cmb_values` of the target row as announced at the decision instant of `decision_row`.

        Mutation record: see `tests/test_s3c_cmb_1356.py` (`CmbSizeTable._split`).
        """

        if decision_row < 0 or target_row >= len(self.dates):
            raise ValueError(f"row {target_row} read at the decision of row {decision_row} is outside the panel")
        key = (decision_row, target_row)
        if key not in self._split_cache:
            instant = datetime.combine(self.dates[decision_row], self._time)
            self._split_cache[key] = cmb_values(self._by_day.get(self.dates[target_row], ()), instant, prior_day_only=self.prior_day_only)
        return self._split_cache[key]

    def sizes_at(self, lead: int, row: int) -> Dict[str, float]:
        if lead not in CMB_LEADS:
            return super().sizes_at(lead, row)
        value = self._split(row - lead, row)
        return {name: value[name] for name in sc.SIZED_TERMS}

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The sizes a forecast of the decision on row `decision_index` at `lead` reads.

        Raises:
            LookAheadError: the figure is not the one announced at the decision instant.
        """

        if lead not in CMB_LEADS:
            return super().read(lead, decision_index)
        row = cal.target_row(decision_index, lead)
        out = self.sizes_at(lead, row)
        instant = datetime.combine(self.dates[decision_index], self._time)
        announced = cmb_values(self._by_day.get(self.dates[row], ()), instant, prior_day_only=self.prior_day_only)
        for name in sc.SIZED_TERMS:
            if abs(out[name] - announced[name]) > 1e-9:
                raise LookAheadError(
                    f"net {name!r} for {self.dates[row]} is {out[name]}, but {announced[name]} was announced by the decision instant "
                    f"{instant} of the forecast made {lead} panel day(s) ahead"
                )
        return out


class CmbTerms:
    """The cash management bill term at leads 2 to 5, as the decision `lead` rows before could read it; the `iorb` table of `sc.walk`.

    `names` picks which of `sc.CMB_EXTRAS` are served (an arm reads one). `cmb_net` is in USD 100 bn. At lead 1 nothing is served.
    """

    def __init__(self, size: CmbSizeTable, names: Sequence[str] = sc.CMB_EXTRAS):
        unknown = [name for name in names if name not in sc.CMB_EXTRAS]
        if unknown:
            raise ValueError(f"names must be among {list(sc.CMB_EXTRAS)}, got {unknown}")
        self.size = size
        self.names = tuple(name for name in sc.CMB_EXTRAS if name in names)
        self.dates = size.dates
        self._time = size._time

    @staticmethod
    def _scaled(value: Mapping[str, float], name: str):
        return int(value[name]) if name == sc.CMB_FLAG else value[name] / sc.SIZE_UNIT

    def at(self, lead: int, row: int) -> Dict[str, float]:
        """The term of target row `row` as the decision `lead` rows earlier read it (a training row: public by construction)."""

        if lead not in CMB_LEADS:
            return {}
        value = self.size._split(row - lead, row)
        return {name: self._scaled(value, name) for name in self.names}

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The term a forecast of the decision on row `decision_index` at `lead` reads, from its target row.

        Raises:
            LookAheadError: a flag or size that counts an announcement made after the decision instant.
            StaleReadError: a flag that leaves out a cash management bill announced by the decision instant.
        """

        if lead not in CMB_LEADS:
            return {}
        row = cal.target_row(decision_index, lead)
        instant = datetime.combine(self.dates[decision_index], self._time)
        out = self.at(lead, row)
        announced = cmb_values(self.size._by_day.get(self.dates[row], ()), instant, prior_day_only=self.size.prior_day_only)
        for name in self.names:
            want = self._scaled(announced, name)
            if name == sc.CMB_FLAG:
                if out[name] > want:
                    raise LookAheadError(
                        f"term {name!r} for {self.dates[row]} counts a cash management bill announced after the decision instant {instant} "
                        f"of the forecast made {lead} panel day(s) ahead"
                    )
                if out[name] < want:
                    raise StaleReadError(
                        f"term {name!r} for {self.dates[row]} leaves out a cash management bill announced by the decision instant {instant}"
                    )
            elif abs(out[name] - want) > 1e-9:
                raise LookAheadError(
                    f"term {name!r} for {self.dates[row]} is {out[name]}, but {want} was announced by the decision instant {instant} "
                    f"of the forecast made {lead} panel day(s) ahead"
                )
        return out
