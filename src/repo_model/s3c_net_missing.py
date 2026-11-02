"""(s3c-ann-net) with the missing maturing amounts handled two ways (#1390; H5, registration design: data meaning; her ruling of 2 November 2026).

`net_settlement.net_for_day` returns 0.0 for a class whose net it cannot form: a maturing estimate that no announced record carries is read as 0.0
(the class then drains its whole offering), and a class that is not fully announced is left out. A genuine zero looks the same. `net_settlement.net_state`
names the state of each class (#1390); this module serves two readings of the candidate's settlement terms (`sc_s3c_ann_net`, `s3c_announced`), both
declared in `metadata/s3c_net_missing_1390.json` before any score:

* **as now**: `s3c_announced.AnnouncedNetSizeTable`, untouched. The missing state is not read by the fit, only logged (`NetMissingTerms.log_row`).
* **drop**: `DroppedNetSizeTable` gives a class that rests on a missing figure (`net_settlement.MISSING_STATES`) a net of 0.0, and `NetMissingTerms` serves
  the 0/1 flag `net_missing` (`spread_mr_state_calendar.MISSING_FLAG`), 1 when either class of the target day rests on a missing figure at the decision
  instant, as an extra term of the fit. `DROP_ARM` is the candidate's arm with that one extra term.

Nothing here is read by a published declaration, record or panel. What a missing amount should mean in the registered recipe is data meaning, hers
(#1390 item 4; the default is to keep the current reading and log the state).

**Information set.** The state of a class and the flag are functions of the auctions announced, and of the published schedule, at the decision instant of
the row `lead` rows before the target (18:00, `repo_model.decision_instant`). A training pair reads the figure of its own decision, so a training figure and
a forecast figure are the same function of the same announcements. `read` recomputes the figure at the decision it is asked for and raises
`LookAheadError` when the served figure is not that one. A cash management bill announced later is not on the schedule (#738) and no flag can know it is
coming: it never enters the state (`net_settlement.cmb_pending` is hindsight, for counting only).

Stdlib only.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime, time
from typing import Dict, List, Mapping, Sequence, Tuple

from .decision_instant import DECISION_TIME
from . import net_settlement as ns
from . import s3c_announced
from . import spread_mr_calendar as cal
from . import spread_mr_state_calendar as sc
from .data import DailyObservation
from .splits import LookAheadError

__all__ = ["DROP_ARM", "DroppedNetSizeTable", "NetMissingTerms"]

#: (s3c-ann-net-drop): the candidate's arm with a missing class dropped from the net terms (`DroppedNetSizeTable`) and the missingness flag beside them.
DROP_ARM = dataclasses.replace(
    s3c_announced.ANN_NET_ARM, name="sc_s3_ann_net_drop",
    role="(s3-ann-net-drop) (s3-ann-net) with a class that rests on a missing figure dropped from the net term and a missingness flag beside the net terms",
    extra=sc.MISSING_EXTRAS,
)


class DroppedNetSizeTable(s3c_announced.AnnouncedNetSizeTable):
    """`AnnouncedNetSizeTable` with a class that rests on a missing figure read as 0.0 (`net_settlement.NetState.terms(drop=True)`); same interface."""

    @staticmethod
    def _terms(auctions: Sequence[ns.Auction], instant: datetime) -> Dict[str, float]:
        return ns.net_state(auctions, instant).terms(drop=True)

    def _value(self, decision_row: int, target_row: int) -> Dict[str, float]:
        """The dropped net by term of the target row as announced at the decision instant of `decision_row`.

        Mutation record: see `tests/test_net_missing_1390.py` (`NetMissingTermsTests`).
        """

        if decision_row < 0 or target_row >= len(self.dates):
            raise ValueError(f"row {target_row} read at the decision of row {decision_row} is outside the panel")
        key = (decision_row, target_row)
        if key not in self._cache:
            instant = datetime.combine(self.dates[decision_row], self._time)
            self._cache[key] = self._terms(self._by_day.get(self.dates[target_row], ()), instant)
        return self._cache[key]

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The sizes a forecast of the decision on row `decision_index` at `lead` reads, from its target row.

        Raises:
            LookAheadError: the figure is not the dropped net announced at the decision instant.
        """

        row = cal.target_row(decision_index, lead)
        out = self.sizes_at(lead, row)
        instant = datetime.combine(self.dates[decision_index], self._time)
        announced = self._terms(self._by_day.get(self.dates[row], ()), instant)
        for name in sc.SIZED_TERMS:
            if abs(out[name] - announced[name]) > 1e-9:
                raise LookAheadError(
                    f"dropped net {name!r} for {self.dates[row]} is {out[name]}, but {announced[name]} was announced by the decision instant "
                    f"{instant} of the forecast made {lead} panel day(s) ahead"
                )
        return out


class NetMissingTerms:
    """The missingness flag of `sc.MISSING_EXTRAS` at every lead, as the decision `lead` rows before could read it; the `iorb` table of `sc.walk`.

    `net_missing` is 1.0 when either class of the settlement of target row `row` rests on a missing figure (`net_settlement.MISSING_STATES`) at the
    decision instant of row `row - lead`, else 0.0. A row with no decision row `lead` rows before reads 0.0. `log_row` is the per-forecast record of the
    state of each class, for any reading.
    """

    def __init__(self, panel: Sequence[DailyObservation], auctions: Sequence[ns.Auction], *, decision_time: time = DECISION_TIME):
        self.dates = [row.date for row in panel]
        self._time = decision_time
        self._by_day: Dict[date, List[ns.Auction]] = {}
        for item in auctions:
            self._by_day.setdefault(item.settles, []).append(item)
        self._cache: Dict[Tuple[int, int], Dict[str, float]] = {}

    def _state(self, decision_row: int, target_row: int) -> ns.NetState:
        instant = datetime.combine(self.dates[decision_row], self._time)
        return ns.net_state(self._by_day.get(self.dates[target_row], ()), instant)

    def at(self, lead: int, row: int) -> Dict[str, float]:
        """The flag of target row `row` as the decision `lead` rows earlier read it (a training row: public by construction).

        Mutation record: see `tests/test_net_missing_1390.py` (module docstring).
        """

        key = (lead, row)
        if key not in self._cache:
            if row - lead < 0:
                self._cache[key] = {sc.MISSING_FLAG: 0.0}
            else:
                self._cache[key] = {sc.MISSING_FLAG: 1.0 if self._state(row - lead, row).missing else 0.0}
        return self._cache[key]

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The flag a forecast of the decision on row `decision_index` at `lead` reads, from its target row.

        Raises:
            LookAheadError: the flag is not the one announced at the decision instant.
        """

        row = cal.target_row(decision_index, lead)
        out = self.at(lead, row)
        announced = 1.0 if self._state(decision_index, row).missing else 0.0
        if abs(out[sc.MISSING_FLAG] - announced) > 1e-9:
            raise LookAheadError(
                f"term {sc.MISSING_FLAG!r} for {self.dates[row]} is {out[sc.MISSING_FLAG]}, but {announced} followed from what was announced by the "
                f"decision instant {datetime.combine(self.dates[decision_index], self._time)} of the forecast made {lead} panel day(s) ahead"
            )
        return out

    def log_row(self, lead: int, decision_index: int) -> Mapping[str, object]:
        """The per-forecast record (#1390 item 2): the state of each class of the target day's settlement at the decision, and whether either is missing."""

        row = cal.target_row(decision_index, lead)
        state = self._state(decision_index, row)
        return {
            "decision_day": self.dates[decision_index].isoformat(), "lead": lead, "target_day": self.dates[row].isoformat(),
            "bill": state.bill.state, "coupon": state.coupon.state, "missing": int(state.missing),
        }
