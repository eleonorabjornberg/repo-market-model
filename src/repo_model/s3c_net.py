"""(s3c-net): the settlement terms of (s3c) as net bill and net coupon settlement (#1273; H5 step 3, ledger item 65 on #1116).

Eleonora, 27 October 2026 (chat, relayed): what adds collateral and drains cash on a settlement day is
*new* money, the securities settling less those maturing, not the gross settlement. `repo_model.net_settlement` (#426) builds that net
from the Fiscal Data auction records, each figure read at its announcement. (s3c) (`repo_model.s3c_candidate`) does not read it: its two
settlement terms (`settlement_coupon`, `settlement_bill`) are 0/1 flags of the gross settlement being above zero
(`spread_mr_calendar.TermTable`). (s3c-net) replaces the two terms, and only them, by the signed net of the target day in units of
USD 100 bn: the bill types and the coupon types separately, the sign kept (more maturing than settling reads negative).

The fit is `spread_mr_state_calendar`'s, unchanged: the sized arm of #1172 (`sized=True`) with the scarcity state held at its maximum
(`constant_states`), so that the sized regressor `size / SIZE_UNIT * level(state)` is the plain signed `size / 100`. Nothing else changes:
(s3)'s other terms, the Huber fit, the ridge of 5 and the direct pairs are the arm's own. `NET_ARM` is `sc.ARMS[2]` with `sized=True`; `GROSS_ARM`
is the same with the panel's gross sizes (`sc.SizeTable`), the control that separates the change of form (flag to size) from the change
from gross to net.

**Information set.** A settlement size is a scheduled field of the *target* row, read at lead 1 only, exactly as the gross flag of the same
term is (`spread_mr_calendar.TERMS`: span `(0,)`). The net of target day `T` read by the decision on day `D` is `net_settlement.net_for_day`
over the auctions settling on `T`, at the instant 16:00 on `D` (the published records' decision time): an auction counts only when its
`announcemt_date` is on or before `D` (its announcement is stamped 12:00, `metadata/net_settlement.json`), and a class announced only in
part reads 0 until fully announced (#679, #738). A training pair reads the figure of its own decision, `target_row - lead`. The declared
`net_settlement` column is read at 12:00 on `T` itself, which is after the 16:00 decision of the day before, so it is not used for the
target day; this table reads the same function at the decision instant.

Stdlib only.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime, time
from typing import Dict, List, Mapping, Sequence, Tuple

from .decision_instant import DECISION_TIME
from . import net_settlement as ns
from . import spread_mr_calendar as cal
from . import spread_mr_state_calendar as sc
from .data import DailyObservation

__all__ = ["GROSS_ARM", "NET_ARM", "NetSizeTable", "bp_per_100bn", "constant_states", "net_by_term"]

#: (s3c)'s walk arm, (s3) of #1145, `sc.ARMS[2]`, with its two settlement terms as signed net sizes in units of USD 100 bn.
NET_ARM = dataclasses.replace(
    sc.ARMS[2], name="sc_s3_net", role="(s3-net) (s3) with net bill and net coupon settlement in place of the gross flags", sized=True
)
#: The control: the same change of form with the panel's gross sizes (the gross settlement in units of USD 100 bn, no flag).
GROSS_ARM = dataclasses.replace(
    sc.ARMS[2], name="sc_s3_gross_size", role="(s3-gross) (s3) with gross bill and gross coupon settlement as sizes, the control of (s3-net)",
    sized=True,
)


def net_by_term(auctions: Sequence[ns.Auction], instant: datetime) -> Dict[str, float]:
    """The net of one settlement day's auctions as announced at `instant`, in USD billions, by `sc.SIZED_TERMS`.

    `net_settlement.net_for_day` gives the net and the net of the bill types; the coupon types are the difference. The sign is kept.
    """

    net, bills, _unknown = ns.net_for_day(auctions, instant)
    return {"settlement_bill": bills, "settlement_coupon": net - bills}


class NetSizeTable(sc.SizeTable):
    """The net bill and net coupon settlement at every panel row, as the decision `lead` rows before could read them.

    Same interface as `spread_mr_state_calendar.SizeTable` (`sizes_at`, `read`), which the sized arm calls. The figure for target row `r`
    read at lead `lead` is the net of the auctions settling on `dates[r]` that were announced at or before the decision instant of row
    `r - lead` (`decision_time` on that day). Only lead 1 is readable, as for the gross flags.
    """

    def __init__(self, panel: Sequence[DailyObservation], auctions: Sequence[ns.Auction], *, decision_time: time = DECISION_TIME):
        self.dates = [row.date for row in panel]
        self._time = decision_time
        self._by_day: Dict[date, List[ns.Auction]] = {}
        for item in auctions:
            self._by_day.setdefault(item.settles, []).append(item)
        self._cache: Dict[Tuple[int, int], Dict[str, float]] = {}

    def _value(self, decision_row: int, target_row: int) -> Dict[str, float]:
        """The net by term of the target row as announced at the decision instant of `decision_row`.

        Mutation record: see `tests/test_s3c_net.py` (`NetSizeTable._value`).
        """

        if decision_row < 0 or target_row >= len(self.dates):
            raise ValueError(f"row {target_row} read at the decision of row {decision_row} is outside the panel")
        key = (decision_row, target_row)
        if key not in self._cache:
            instant = datetime.combine(self.dates[decision_row], self._time)
            self._cache[key] = net_by_term(self._by_day.get(self.dates[target_row], ()), instant)
        return self._cache[key]

    def sizes_at(self, lead: int, row: int) -> Dict[str, float]:
        """The sizes of the terms readable at `lead`, at target row `row`, as the decision `lead` rows earlier read them."""

        names = [name for name in sc.SIZED_TERMS if cal.available(cal.TERM[name], lead)]
        if not names:
            return {}
        value = self._value(row - lead, row)
        return {name: value[name] for name in names}

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The sizes a forecast of the decision on row `decision_index` at `lead` reads, from its target row."""

        return self.sizes_at(lead, cal.target_row(decision_index, lead))


def constant_states(panel: Sequence[DailyObservation]) -> Dict[date, float]:
    """The scarcity state held at its maximum on every day, so that `sc.level` is 1 and a sized term is the plain `size / SIZE_UNIT`."""

    return {row.date: sc.STATE_MAX for row in panel}


def bp_per_100bn(estimate: sc.StateEstimate, scale: float) -> Dict[str, float]:
    """The fitted effect of each sized term in bp per USD 100 bn of settlement: the standardised effect times the anchor's scale in bp."""

    return {name: effect * scale for name, effect in estimate.effect.items() if name in sc.SIZED_TERMS}
