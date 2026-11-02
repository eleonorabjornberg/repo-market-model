"""The decision day's own ON RRP and Standing Repo Facility take-up, read at the 18:00 decision (#1349; H5 step 3; her ruling of 1 November
2026 on avenue #1337, ledger item 98: "use the same day and test it").

A forecast made on panel day `D` is made at the decision instant (`repo_model.decision_instant`, 18:00 New York time). The New York Fed's
operation results for `D` itself are, in almost every case, public hours before that: the operations close at 13:15 (ON RRP) and 13:45 (the
facility; 08:30 as well since 26 June 2025) and the Desk's one timestamp on a result, `lastUpdated`, falls a median 1 to 2 minutes after the close.
`repo_model.fed_liquidity` reads the same results at 16:00 (`nyfed_repo_ops_sameday`, #442, off in every published declaration) and leaves open
whether to re-read them at the new instant (the comment on its `DECISION_TIME`). This module is that re-read, for a development arm only.

**Availability.** A date's figure is public at the decision instant of `D` when every record it sums was last written at or before that instant:
`lastUpdated` is the last write, a record cannot have been first written later, and the API serves a record from the time it is written (an
assumption that cannot be checked from outside, as in `metadata/sources_measurement.json`, `nyfed_on_rrp_sameday`). A date rewritten after the decision
(the Desk rewrote some on 2023-09-27) has no first publication time we can see, so it is withheld and reads as no take-up, which is also how
`fed_liquidity` reads a withheld date. The same rule applies to the previous day's ON RRP figure in the change. Naive `lastUpdated` stamps and the
decision instant are both New York wall-clock times. The evidence over the tracked snapshots is `scripts/s3c_sameday_ops_1349.py availability`.

**The terms** (`spread_mr_state_calendar.OPS_EXTRAS`), for the forecast of target row `T` made `lead` rows ahead, from the decision row `D = T - lead`:

* `srf_flag`: 1 when the facility's overnight take-up on `D` is above zero;
* `srf_size`: that take-up in units of USD 100 bn;
* `on_rrp_change`: the ON RRP amount accepted on `D` less that on the previous panel day, in units of USD 100 bn (0 when either is not public by the
  decision instant).

They are a state of the decision day, not a calendar column of the target: the same three numbers are read at every lead of the decision, and a
training pair reads its own decision's figure (`at(lead, row)` is `read(lead, row - lead)`), so the fit trains on direct pairs
(`training_pairs="direct"`) and `one_step_guard` holds with no allow-list entry. `read` re-derives the figure from the records and refuses one that
counts a record written after the decision instant (`LookAheadError`) or leaves a public record out (`StaleReadError`).

`SAMEDAY_ARM` is `s3c_announced.ANN_NET_ARM` (s3 with the announced net settlement, #1288) with the three terms as extras. Nothing in
`fed_liquidity`, `ingest`, `metadata/` or any published declaration is edited.

Stdlib only.
"""

from __future__ import annotations

import dataclasses
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

from . import ingest
from . import nowcast
from . import s3c_announced
from . import spread_mr_calendar as cal
from . import spread_mr_state_calendar as sc
from .asof import StaleReadError
from .decision_instant import DECISION_TIME
from .splits import LookAheadError

__all__ = [
    "OPS_EXTRAS", "SAMEDAY_ARM", "DayFigure", "SameDayOperationTerms", "on_rrp_days", "srf_days", "load_operations", "unique_operations",
]

OPS_EXTRAS = sc.OPS_EXTRAS
#: (s3c-ann-net) with the decision day's own take-up: the arm of #1349. Its fit is (s3)'s, on direct pairs; what differs is the three extra terms.
SAMEDAY_ARM = dataclasses.replace(
    s3c_announced.ANN_NET_ARM, name="sc_s3_ann_net_sameday",
    role="(s3-ann-net-sameday) (s3-ann-net) with the decision day's own SRF take-up and ON RRP change",
    extra=OPS_EXTRAS,
)
_EPSILON = 1e-9


@dataclasses.dataclass(frozen=True)
class DayFigure:
    """One operation date's figure in USD billions and the latest `lastUpdated` of the records it sums (New York wall clock)."""

    value: float
    written: datetime


def _written(record: Mapping[str, object], where: str) -> datetime:
    try:
        return datetime.fromisoformat(str(record["lastUpdated"]))
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{where} has no readable lastUpdated ({record.get('lastUpdated')!r})") from exc


def _day(record: Mapping[str, object], where: str) -> date:
    try:
        return date.fromisoformat(str(record["operationDate"]))
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{where} has no valid operationDate") from exc


def unique_operations(operations: Sequence[Mapping[str, object]]) -> List[Mapping[str, object]]:
    """One record per `operationId`, the one last written, so that snapshots that overlap do not count an operation twice."""

    best: Dict[str, Mapping[str, object]] = {}
    for number, record in enumerate(operations, start=1):
        key = str(record.get("operationId", f"#{number}"))
        if key not in best or _written(record, f"operation {key}") >= _written(best[key], f"operation {key}"):
            best[key] = record
    return list(best.values())


def load_operations(directory: Path) -> List[Mapping[str, object]]:
    """Every operation of the snapshots under `directory`, each checked against its manifest, one record per `operationId`."""

    return unique_operations(nowcast.load_operations(Path(directory)))


def on_rrp_days(operations: Sequence[Mapping[str, object]]) -> Dict[date, DayFigure]:
    """Per operation date, the ON RRP amount accepted (`totalAmtAccepted` summed over every `Reverse Repo` operation, USD billions, as
    `ingest._nyfed_on_rrp_rows` sums it) and the latest write of those records.

    Raises:
        ValueError: an operation with no valid date, no numeric amount or no readable `lastUpdated`.
    """

    totals: Dict[date, int] = {}
    written: Dict[date, datetime] = {}
    for number, record in enumerate(operations, start=1):
        if record.get("operationType") != ingest.NYFED_REVERSE_REPO:
            continue
        where = f"reverse-repo operation {record.get('operationId', number)!r}"
        day = _day(record, where)
        accepted = record.get("totalAmtAccepted")
        if isinstance(accepted, bool) or not isinstance(accepted, (int, float)):
            raise ValueError(f"{where} on {day} has no numeric totalAmtAccepted ({accepted!r})")
        totals[day] = totals.get(day, 0) + accepted
        stamp = _written(record, where)
        written[day] = max(stamp, written.get(day, stamp))
    return {day: DayFigure(totals[day] / 1e9, written[day]) for day in totals}


def srf_days(operations: Sequence[Mapping[str, object]]) -> Dict[date, DayFigure]:
    """Per operation date, the facility's overnight take-up (USD billions) and the latest write of the records behind it.

    The operations and the amount are the published reader's (`ingest._nyfed_srf_rows`): `Repo`, `Overnight`, on or after `SRF_INCEPTION`, not a
    small-value exercise, a test trade counted as zero. A date whose only operations are exercises has no figure (it reads as no take-up).

    Raises:
        ValueError: a kept operation with no valid date, no numeric amount or no readable `lastUpdated`.
    """

    totals: Dict[date, int] = {}
    written: Dict[date, datetime] = {}
    for number, record in enumerate(operations, start=1):
        if record.get("operationType") != "Repo" or record.get("term") != "Overnight":
            continue
        where = f"repo operation {record.get('operationId', number)!r}"
        day = _day(record, where)
        if day < ingest.SRF_INCEPTION or ingest._is_small_value_exercise(record):
            continue
        accepted = record.get("totalAmtAccepted")
        if isinstance(accepted, bool) or not isinstance(accepted, (int, float)):
            raise ValueError(f"{where} on {day} has no numeric totalAmtAccepted ({accepted!r})")
        totals[day] = totals.get(day, 0) + ingest._effective_taken(record, accepted)
        stamp = _written(record, where)
        written[day] = max(stamp, written.get(day, stamp))
    return {day: DayFigure(totals[day] / 1e9, written[day]) for day in totals}


class SameDayOperationTerms:
    """The terms of `OPS_EXTRAS` at every lead, as the decision `lead` rows before could read them; the `iorb` table of `sc.walk`.

    `dates` are the panel's dates, `srf` and `rrp` the day figures (`srf_days`, `on_rrp_days`). A date with no figure, or whose figure was last
    written after the decision instant, is no take-up. A row with no decision row `lead` rows before reads 0. `names` picks which are served.
    """

    def __init__(
        self, dates: Sequence[date], srf: Mapping[date, DayFigure], rrp: Mapping[date, DayFigure], *,
        decision_time: time = DECISION_TIME, names: Sequence[str] = OPS_EXTRAS,
    ):
        unknown = [name for name in names if name not in OPS_EXTRAS]
        if unknown:
            raise ValueError(f"names must be among {list(OPS_EXTRAS)}, got {unknown}")
        self.dates = list(dates)
        self.srf, self.rrp = srf, rrp
        self.names = tuple(name for name in OPS_EXTRAS if name in names)
        self._time = decision_time

    def instant(self, decision: int) -> datetime:
        return datetime.combine(self.dates[decision], self._time)

    def at(self, lead: int, row: int) -> Dict[str, float]:
        """The terms of target row `row` as the decision `lead` rows earlier read them (a training row: public by construction).

        Mutation record: see `tests/test_same_day_operations_1349.py` (`SameDayOperationTerms.at`).
        """

        decision = row - lead
        if decision < 0:
            return {name: 0.0 for name in self.names}
        instant = self.instant(decision)
        day = self.dates[decision]
        taken = self.srf.get(day)
        take = taken.value if taken is not None and taken.written <= instant else 0.0
        change = 0.0
        now, before = self.rrp.get(day), self.rrp.get(self.dates[decision - 1]) if decision >= 1 else None
        if now is not None and before is not None and now.written <= instant and before.written <= instant:
            change = (now.value - before.value) / sc.SIZE_UNIT
        values = {sc.SRF_FLAG: 1.0 if take > 0.0 else 0.0, sc.SRF_SIZE: take / sc.SIZE_UNIT, sc.RRP_CHANGE: change}
        return {name: values[name] for name in self.names}

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The terms a forecast of the decision on row `decision_index` at `lead` reads.

        Raises:
            LookAheadError: a figure that counts a record written after the decision instant.
            StaleReadError: a figure that leaves out a record public by it.
        """

        out = self.at(lead, cal.target_row(decision_index, lead))
        instant = self.instant(decision_index)
        day = self.dates[decision_index]
        expected: Dict[str, float] = {}
        taken = self.srf.get(day)
        take = taken.value if taken is not None and taken.written <= instant else 0.0
        expected[sc.SRF_SIZE] = take / sc.SIZE_UNIT
        expected[sc.SRF_FLAG] = 1.0 if take > 0.0 else 0.0
        now = self.rrp.get(day)
        before = self.rrp.get(self.dates[decision_index - 1]) if decision_index >= 1 else None
        public = [f for f in (now, before) if f is not None and f.written <= instant]
        expected[sc.RRP_CHANGE] = (now.value - before.value) / sc.SIZE_UNIT if len(public) == 2 else 0.0
        for name in self.names:
            got, want = out[name], expected[name]
            if name == sc.RRP_CHANGE:
                if abs(got - want) > _EPSILON:
                    raise (LookAheadError if self._counts_late(name, got, instant, day, decision_index) else StaleReadError)(
                        f"term {name!r} for the forecast made on {day} is {got}, but {want} was public by the decision instant {instant}"
                    )
            elif got > want + _EPSILON:
                raise LookAheadError(
                    f"term {name!r} for the forecast made on {day} is {got}, but {want} was public by the decision instant {instant}: "
                    "it counts a record written later"
                )
            elif got < want - _EPSILON:
                raise StaleReadError(
                    f"term {name!r} for the forecast made on {day} is {got}, but {want} was public by the decision instant {instant}: "
                    "it leaves out a public record"
                )
        return out

    def _counts_late(self, name: str, got: float, instant: datetime, day: date, decision_index: int) -> bool:
        """Whether a wrong ON RRP change is one that reads a record written after `instant` (a figure from the future) rather than one that drops
        a public record: it does when a record behind the change was written after the instant."""

        now = self.rrp.get(day)
        before = self.rrp.get(self.dates[decision_index - 1]) if decision_index >= 1 else None
        return any(f is not None and f.written > instant for f in (now, before))
