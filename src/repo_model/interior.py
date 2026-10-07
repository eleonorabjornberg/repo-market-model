"""Pressure model v2's distribution: v1 unchanged, its interior tracked online (#244).

#243 found that the published distribution's 50% band covers about a third of
outcomes. #247 diagnosed why: the trees' interior is too narrow out of sample,
mostly on the low side, and no setting of the trees fixes it. #247's declared
selection rule then chose (i), per-level online quantile tracking of q25, q50
and q75, on v1's unchanged trees and nested conformal PID
(`docs/diagnosis-interior-calibration.md`, "What #244 should build"). This
module builds exactly that, and names it pressure model v2:

* **Levels.** q25, q50 and q75 each carry an offset, starting at 0. q05 and
  q95 stay as nested PID issues them, unless the sort below moves them.
* **Update.** Before a day's vector is issued, every earlier scored day whose
  label is observable at the day's anchor updates, in date order:
  `offset_tau += step * (tau - below(y, q_tau))`, where `below` counts a tie
  as one half and `q_tau` is the vector that step issued for that earlier day.
* **Step.** Each step in `INTERIOR_STEPS` runs its own trackers. At the first
  scored day of each block of `refit_every` days, the step with the least
  pooled CRPS over the observable days is chosen (`select_constants`, the
  nested walk-forward selection nested PID already uses, #125), and
  `INTERIOR_FALLBACK` while there are none.
* **Issue.** The offset vector, sorted (the rearrangement `ml.py` uses), so
  that the quantiles never cross. `require_ordered` refuses anything else.

* **Width (the fix, #244).** The diagnosis on the inner block found the turn
  days' realised |y - q50| larger than the band the trees and the pooled
  trackers issue for them, and per-day-type level trackers could not learn it
  from so few days. After the levels, `OnlineWidth` scales q25 - q50 and
  q75 - q50 by `exp(log_scale)`, one log scale per width class (turn days,
  ordinary days: `WIDTH_CLASSES`), moved by `rate * (0.5 - inside)` on each
  observable label of the 50% band the layer issued, its rate chosen by the same
  nested walk-forward selection (`WidthState`). The reference implementation is
  `width_tracking` in `scripts/pressure_model_v2.py`.

`OnlineInterior` holds this between calls. `NestedInteriorFoldPid` runs it
inside a fold loop on the output of `recalibration.NestedFoldPid`, which it
leaves untouched: v1's vector is computed first, as before, and v2's is made
from it. The reference implementation, `interior_tracking` in
`scripts/interior_diagnosis.py`, produced #247's figures. `tests/test_pressure_model_v2.py`
holds this module to it, to the bit.

Standard library only.
"""

from __future__ import annotations

import math
from collections import deque
from datetime import date
from typing import Deque, List, NamedTuple, Optional, Sequence, Tuple

from .metrics import crps_from_quantiles
from .recalibration import NestedFoldPid, SelectedBlock, _PidView, select_constants
from .splits import LookAheadError

#: The levels v2 tracks. The outer two stay nested PID's.
INTERIOR_LEVELS = (0.25, 0.5, 0.75)
#: The candidate steps, in basis points per unit of miss, and the step used
#: before any label is observable (#247, `TRACKING_STEPS`, `TRACKING_FALLBACK`).
INTERIOR_STEPS = (0.01, 0.05, 0.1, 0.2)
INTERIOR_FALLBACK = 0.05
#: The width layer (#244, the fix chosen on the inner block): after the interior
#: levels are moved, the 50% band's half-widths are scaled by a per-class online
#: tracker. The candidate rates, in log-scale units per unit of miss, and the rate
#: used before any label is observable.
WIDTH_RATES = (0.02, 0.05, 0.1, 0.2)
WIDTH_FALLBACK = 0.05
#: A scored day's width class, by its pressure-day type: ordinary days and turn
#: days (every other type) each carry their own scale.
WIDTH_CLASSES = {
    "quarter_end": "turn",
    "month_end": "turn",
    "tax_date": "turn",
    "ordinary": "ordinary",
}
#: Two spreads within this many basis points are the same print. The panel's
#: spreads are whole basis points carried as differences of percentages
#: (17.000000000000014), so exact float equality would miss almost every tie.
TIE_BPS = 1e-9


def below_half_tie(actual: float, quantile: float) -> float:
    """1 if `actual` is below `quantile`, one half on a tie (within `TIE_BPS`), else 0."""

    if abs(actual - quantile) <= TIE_BPS:
        return 0.5
    return 1.0 if actual < quantile else 0.0


def require_ordered(vector: Sequence[float]) -> Tuple[float, ...]:
    """`vector` as a tuple, if its quantiles are finite and do not cross.

    Raises:
        ValueError: a quantile is not finite, or a lower level's quantile lies
            above a higher level's.
    """

    values = tuple(float(value) for value in vector)
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"quantiles {values} are not all finite")
    if not all(a <= b for a, b in zip(values, values[1:])):
        raise ValueError(f"quantiles {values} cross: q05 <= q25 <= q50 <= q75 <= q95 must hold")
    return values


def _slots(levels: Sequence[float]) -> Tuple[int, ...]:
    levels = tuple(levels)
    missing = [level for level in INTERIOR_LEVELS if level not in levels]
    if missing:
        raise ValueError(f"levels {levels} lack the interior levels {missing}")
    return tuple(levels.index(level) for level in INTERIOR_LEVELS)


class InteriorDay(NamedTuple):
    """One scored day as v2 sees it before its label.

    `vector` is the vector nested PID issued for the day (v1's); `anchor` the
    latest panel day whose label was observable at its decision instant. `kind`
    is the day's width class (`WIDTH_CLASSES`): the levels' trackers ignore it.
    """

    scored_date: date
    anchor: date
    vector: Tuple[float, ...]
    kind: str = "all"


class InteriorState:
    """One step's trackers: what the labels observed so far have taught them."""

    def __init__(self, levels: Sequence[float], step: float) -> None:
        self.levels = tuple(levels)
        self.slots = _slots(self.levels)
        self.step = float(step)
        self.offsets = [0.0] * len(self.slots)
        self.observed = 0
        self.last_observed: Optional[date] = None

    def issue(self, vector: Sequence[float], kind: str = "all") -> Tuple[float, ...]:
        """`vector` with each interior level moved by its offset, sorted."""

        moved = [float(value) for value in vector]
        if len(moved) != len(self.levels):
            raise ValueError(f"a vector of {len(moved)} quantiles for {len(self.levels)} levels")
        for slot, position in enumerate(self.slots):
            moved[position] += self.offsets[slot]
        return require_ordered(sorted(moved))

    def observe(
        self, day: InteriorDay, issued: Sequence[float], actual: float, decision: InteriorDay
    ) -> None:
        """Update on `day`'s label, as seen at `decision`'s decision instant.

        `issued` is the vector this step issued for `day`.

        Raises:
            LookAheadError: if `day`'s label was not observable at that
                instant: `day` is scored after `decision`'s anchor.
            ValueError: if labels are observed out of date order or twice.
        """

        if day.scored_date > decision.anchor:
            raise LookAheadError(
                f"the label of {day.scored_date} is not observable at the decision "
                f"for {decision.scored_date}, whose latest observable label is "
                f"{decision.anchor}; an interior tracker may update only on labels "
                f"public at the instant its vector is issued"
            )
        if self.last_observed is not None and day.scored_date <= self.last_observed:
            raise ValueError(
                f"the label of {day.scored_date} is observed after that of "
                f"{self.last_observed}; labels are observed once, in date order"
            )
        self._learn(day, issued, actual)
        self.observed += 1
        self.last_observed = day.scored_date

    def _learn(self, day: InteriorDay, issued: Sequence[float], actual: float) -> None:
        for slot, position in enumerate(self.slots):
            level = self.levels[position]
            self.offsets[slot] += self.step * (level - below_half_tie(actual, issued[position]))


class WidthState(InteriorState):
    """One rate's width trackers: a log scale per class, learned from the 50% band's coverage.

    `issue` moves q25 and q75 to `q50 + scale * (q - q50)`, `scale` being the
    exponential of the day's class's log scale (0 until that class has a label),
    and sorts. Each observable label moves its class's log scale by
    `rate * (0.5 - inside)`, `inside` being 1 when the label lies strictly
    inside the band the state issued for that day, one half on an edge tie, and
    0 outside: a band that covers less than half widens, one that covers more
    narrows. The same label guards as `InteriorState`'s.
    """

    def __init__(self, levels: Sequence[float], step: float) -> None:
        super().__init__(levels, step)
        self.log_scale: dict = {}

    def issue(self, vector: Sequence[float], kind: str = "all") -> Tuple[float, ...]:
        moved = [float(value) for value in vector]
        if len(moved) != len(self.levels):
            raise ValueError(f"a vector of {len(moved)} quantiles for {len(self.levels)} levels")
        scale = math.exp(self.log_scale.get(kind, 0.0))
        centre = moved[self.slots[1]]
        moved[self.slots[0]] = centre + (moved[self.slots[0]] - centre) * scale
        moved[self.slots[2]] = centre + (moved[self.slots[2]] - centre) * scale
        return require_ordered(sorted(moved))

    def _learn(self, day: InteriorDay, issued: Sequence[float], actual: float) -> None:
        low, high = issued[self.slots[0]], issued[self.slots[2]]
        if abs(actual - low) <= TIE_BPS or abs(actual - high) <= TIE_BPS:
            inside = 0.5
        else:
            inside = 1.0 if low < actual < high else 0.0
        self.log_scale[day.kind] = self.log_scale.get(day.kind, 0.0) + self.step * (0.5 - inside)


class OnlineInterior:
    """v2's interior one day at a time: issue a day's vector, later learn its label.

    Every step in `steps` runs its own `InteriorState` over every day. The
    vector issued is the chosen step's; the choice is made at the first day of
    each block of `refit_every` issued days, by least pooled CRPS over the days
    whose labels were observable at that day's anchor (`select_constants`).
    `blocks` records the choices.
    """

    def __init__(
        self,
        levels: Sequence[float],
        *,
        refit_every: int,
        steps: Sequence[float] = INTERIOR_STEPS,
        fallback: float = INTERIOR_FALLBACK,
        state: type = InteriorState,
    ) -> None:
        if refit_every < 1:
            raise ValueError(f"refit_every is {refit_every}; a block holds at least one day")
        self.levels = tuple(levels)
        self.steps = tuple(steps)
        self.refit_every = refit_every
        self._fallback = self.steps.index(fallback)
        self._states = [state(self.levels, step) for step in self.steps]
        self._pending: Deque[Tuple[InteriorDay, Tuple[Tuple[float, ...], ...], float]] = deque()
        self._losses: List[Tuple[date, Tuple[float, ...]]] = []
        self._issued_count = 0
        self._chosen = self._fallback
        self._open: Optional[Tuple[InteriorDay, Tuple[Tuple[float, ...], ...]]] = None
        self._last: Optional[InteriorDay] = None
        self.blocks: Tuple[SelectedBlock, ...] = ()

    @property
    def chosen_step(self) -> float:
        return self.steps[self._chosen]

    def issue(self, day: InteriorDay) -> Tuple[float, ...]:
        """`day`'s vector, from the labels observable at its decision.

        Raises:
            LookAheadError: if `day` is anchored on or after its own scored
                date, which would make its own label observable before its
                vector is issued.
            ValueError: if the previous day's label is outstanding, or `day` is
                not after the last day issued, or its anchor moves back.
        """

        if day.anchor >= day.scored_date:
            raise LookAheadError(
                f"{day.scored_date} is anchored at {day.anchor}: its own label "
                f"would be observable before its vector is issued"
            )
        if self._open is not None:
            raise ValueError(
                f"the vector for {self._open[0].scored_date} was issued and its label "
                f"not yet given; each day's label is learned before the next day's vector"
            )
        last = self._last
        if last is not None and (day.scored_date <= last.scored_date or day.anchor < last.anchor):
            raise ValueError(
                f"days must be in scored-date order with anchors that do not move "
                f"back: {last.scored_date} (anchor {last.anchor}) is followed by "
                f"{day.scored_date} (anchor {day.anchor})"
            )
        while self._pending and self._pending[0][0].scored_date <= day.anchor:
            earlier, vectors, actual = self._pending.popleft()
            for state, vector in zip(self._states, vectors):
                state.observe(earlier, vector, actual, day)
        if self._issued_count % self.refit_every == 0:
            history = [(when, losses) for when, losses in self._losses if when <= day.anchor]
            self._chosen, past = select_constants(
                history, day.anchor, len(self.steps), fallback=self._fallback
            )
            self.blocks += (SelectedBlock(day.scored_date, day.anchor, past, self._chosen),)
        vectors = tuple(state.issue(day.vector, day.kind) for state in self._states)
        self._issued_count += 1
        self._open = (day, vectors)
        self._last = day
        return vectors[self._chosen]

    def record(self, day: InteriorDay, actual: float) -> None:
        """`day`'s label, held until a later decision can observe it."""

        if self._open is None or self._open[0] != day:
            raise ValueError(
                f"a label for {day.scored_date} was given, but the vector open is "
                f"{'none' if self._open is None else self._open[0].scored_date}; "
                f"a label is learned once, after its own day's vector"
            )
        _, vectors = self._open
        actual = float(actual)
        self._pending.append((day, vectors, actual))
        self._losses.append(
            (day.scored_date, tuple(crps_from_quantiles(self.levels, v, actual) for v in vectors))
        )
        self._open = None


class OnlineWidth(OnlineInterior):
    """The width layer, one day at a time: `OnlineInterior`'s machinery over `WidthState`.

    Each rate in `WIDTH_RATES` runs its own `WidthState` over every day. The
    vector issued is the chosen rate's, chosen at the first day of each block of
    `refit_every` issued days by least pooled CRPS over the days whose labels
    were observable at that day's anchor. A day's `vector` is the interior
    layer's output, and its `kind` its width class.
    """

    def __init__(
        self,
        levels: Sequence[float],
        *,
        refit_every: int,
        rates: Sequence[float] = WIDTH_RATES,
        fallback: float = WIDTH_FALLBACK,
    ) -> None:
        super().__init__(levels, refit_every=refit_every, steps=rates, fallback=fallback, state=WidthState)


class IssuedDay(NamedTuple):
    """What v2 issued for one scored day, beside v1's vector it was made from.

    `vector` is the vector issued; `tracked` the interior layer's output the
    width layer started from (the same, with no width layer).
    """

    index: int
    scored_date: date
    anchor: date
    pid: Tuple[float, ...]
    vector: Tuple[float, ...]
    tracked: Tuple[float, ...] = ()
    kind: str = "all"


class NestedInteriorFoldPid(NestedFoldPid):
    """Pressure model v2's online calibration, alongside a fold loop.

    `NestedFoldPid` (v1's nested conformal PID) runs first, unchanged, and
    issues v1's vector. `OnlineInterior` then moves its interior levels and,
    with `width_layer`, `OnlineWidth` scales the 50% band by the scored day's
    width class (`WIDTH_CLASSES`, read from the split declaration's pressure-day
    type of the scored day's own calendar columns). The loop reads v2's vector;
    `issued_days` keeps both. A view's point forecast stays the fit's own, as
    under v1.

    v2 is a distribution: its exceedance curve is not defined here, so `law`
    and `curve` are refused.

    Raises (besides `NestedFoldPid`'s):
        LookAheadError: from `OnlineInterior` and `OnlineWidth`, a label not
            observable at the decision instant of the vector being issued.
        ValueError: a law or curve asked of v2; crossed quantiles.
    """

    name = "conformal_pid_nested_interior"

    def __init__(self, rows, rule, *, splits, refit_every: int, width_layer: bool = False, **kwargs) -> None:
        super().__init__(rows, rule, splits=splits, refit_every=refit_every, **kwargs)
        self._width_layer = bool(width_layer)
        self._interior: Optional[OnlineInterior] = None
        self._width: Optional[OnlineWidth] = None
        self._interior_open: Optional[Tuple[int, InteriorDay, Optional[InteriorDay]]] = None
        self.issued_days: List[IssuedDay] = []

    @property
    def settings(self) -> dict:
        """Nested PID's declaration, and the interior layer v2 adds after it."""

        settings = super().settings
        settings["calibration"] = self.name
        settings["interior_calibration"] = {
            "model": "pressure model v2 (#244), the fix #247 recommends",
            "method": "per-level online quantile tracking after nested conformal PID",
            "levels": list(INTERIOR_LEVELS),
            "steps": list(INTERIOR_STEPS),
            "fallback": INTERIOR_FALLBACK,
            "tie_bps": TIE_BPS,
            "selection": "nested walk-forward selection by pooled CRPS at the loop's refits (#125)",
            "refit_every": self._refit_every,
            "issue": "sorted, so that the quantiles never cross",
        }
        if self._width_layer:
            settings["width_calibration"] = {
                "model": "pressure model v2's width layer (#244), chosen on the inner block",
                "method": "per-class online log-scale tracker on the 50% band, after the interior levels",
                "classes": dict(WIDTH_CLASSES),
                "rates": list(WIDTH_RATES),
                "fallback": WIDTH_FALLBACK,
                "update": "log_scale += rate * (0.5 - inside), an edge tie counting one half inside",
                "selection": "nested walk-forward selection by pooled CRPS at the loop's refits (#125)",
                "refit_every": self._refit_every,
            }
        return settings

    def account(self) -> dict:
        """`NestedFoldPid.account`, and the interior step chosen at each refit block."""

        account = super().account()
        interior = self._interior
        account["interior_blocks"] = [] if interior is None else [
            {
                "first_scored": block.first_scored.isoformat(),
                "anchor": block.anchor.isoformat(),
                "past_days": block.past_days,
                "step": interior.steps[block.chosen],
            }
            for block in interior.blocks
        ]
        width = self._width
        if self._width_layer:
            account["width_blocks"] = [] if width is None else [
                {
                    "first_scored": block.first_scored.isoformat(),
                    "anchor": block.anchor.isoformat(),
                    "past_days": block.past_days,
                    "rate": width.steps[block.chosen],
                }
                for block in width.blocks
            ]
        return account

    def view(self, model, index: int, feature_row) -> _PidView:
        """`model` as scored day `rows[index]` reads it: v2's vector, at `feature_row`."""

        pid = tuple(float(value) for value in super().view(model, index, feature_row).predict(feature_row))
        if self._interior is None:
            self._interior = OnlineInterior(model.levels, refit_every=self._refit_every)
        day = InteriorDay(self._dates[index], feature_row.date, pid)
        tracked = self._interior.issue(day)
        vector, width_day = tracked, None
        if self._width_layer:
            if self._width is None:
                self._width = OnlineWidth(model.levels, refit_every=self._refit_every)
            kind = WIDTH_CLASSES[self._splits.day_type(self._rows[index].values)]
            width_day = InteriorDay(day.scored_date, day.anchor, tracked, kind)
            vector = self._width.issue(width_day)
        self._interior_open = (index, day, width_day)
        self.issued_days.append(IssuedDay(
            index, day.scored_date, day.anchor, pid, vector, tracked,
            "all" if width_day is None else width_day.kind))
        return _PidView(model, feature_row.date, vector)

    def law(self, *args, **kwargs):
        raise ValueError(
            "pressure model v2 is a distribution; its law and exceedance curve are not "
            "defined (#244). Use view"
        )

    def curve(self, *args, **kwargs):
        return self.law(*args, **kwargs)

    def label(self, index: int, actual: float) -> None:
        """The realised spread of scored day `rows[index]`, for v1's PID and for v2."""

        super().label(index, actual)
        if self._interior_open is None or self._interior_open[0] != index:
            raise ValueError(f"no v2 vector is open for {self._dates[index]}")
        _, day, width_day = self._interior_open
        self._interior.record(day, actual)
        if width_day is not None:
            self._width.record(width_day, actual)
        self._interior_open = None
