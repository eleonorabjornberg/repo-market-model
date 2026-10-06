"""Pressure model v2: v1's distribution with its interior quantiles calibrated (#244).

Pressure model v1's distribution at h = 1 is #169's gbm with nested conformal
PID (`recalibration.NestedFoldPid`). Conformal PID moves only the outer two
quantiles, so v1's 90% band is calibrated and its 50% band is the trees' own:
it covers about 30% of outcomes before 2026, and the outcome falls below q25
more often than above q75 (#243). Eleonora's ruling of 6 October 2026 on #244
fixes this as a new model, v2, logged alongside an unchanged v1.

v2 takes the vector v1 issues for a scored day, keeps its q05 and q95 exactly,
and moves q25, q50 and q75 by an online tracker. The trackers are conformal
PID's own arithmetic, on the interior levels:

* **`per_level`** (candidates `a`, `c` and `d`). Each interior level `tau`
  carries an offset `theta_tau`, the paper's quantile tracking (the "P" part):
  each observed label moves it by `-step * B * (below - tau)`, `below` 1 when
  the label fell below the level issued for it (a half when exactly on it,
  `below`). With a non-zero `integrator_gain` (candidate `c`) the level also
  carries the saturating integrator over the summed error
  `E_tau = sum(below - tau)` of the `n` observed labels,
  `-K_I * B * tan(E_tau log(n + 1) / (C_sat (n + 1)))`, its argument clipped
  to `+-PID_TANGENT_LIMIT`, exactly as `PidState._integrator` takes it.
* **`shift_scale`** (candidate `b`). The interior is shifted by `s` and
  scaled about v1's median by `exp(kappa)`: q50 is `m + s`, and q25 and q75
  are `m + s + exp(kappa) (q - m)`. The shift tracks the 25/75 imbalance,
  `s += step * B * (above75 - below25)`, and the scale tracks the 50% band's
  miss rate, `kappa += step * (below25 + above75 - 0.5)`.

`B` is the range of the last `PID_STEP_WINDOW` observed residuals about v1's
median, floored at `PID_SCALE_FLOOR`, as conformal PID scales its step. Every
constant is the PID grid's (`recalibration.PID_GRID_STEPS`,
`PID_GRID_INTEGRATOR_GAINS`, `PID_GRID_SATURATIONS`); none is new, and none
was searched. The candidates are declared here, before any fold was scored
with them, and the set is fixed (`CANDIDATES`).

**Order.** The adjusted interior is rearranged (sorted) and each level clipped
into v1's `[q05, q95]`, so v1's outer pair is never moved. `require_ordered`
then refuses, with `ValueError`, any vector whose levels are not finite and
non-decreasing; a band that reached it unordered would be a bug.

**Information.** A label moves a tracker only once it was public at the
decision instant of the band being issued: a scored day's label is observable
at a decision whose anchor (the fold's feature date) is on or after it.
`InteriorState.observe` refuses any other with `LookAheadError`, and
`OnlineInterior` holds each label back until it qualifies, as `OnlinePid` does.

**In a fold loop: `FoldInterior`.** It wraps v1's own fold-loop calibration
(`NestedFoldPid`): each scored day's v1 band is issued by v1 exactly as
without v2, and v1 is told each label exactly as without v2, so v1's state,
bands and declaration are untouched (`settings` is v1's). Every candidate
runs its own tracker over every scored day. The band issued is chosen by
nested walk-forward selection on the backtest's refit blocks, as
`NestedFoldPid` chooses its constants: at each block's first scored day, the
candidate with the least pooled CRPS over the scored days whose labels were
observable there (`recalibration.select_constants`, the guard), and
`FALLBACK` while there are none. With `frozen` it issues one candidate on
every day instead.
"""

from __future__ import annotations

import math
from collections import deque
from datetime import date
from typing import Deque, List, NamedTuple, Optional, Sequence, Tuple

from .contract import QUANTILE_LEVELS
from .recalibration import (
    PID_GRID_STEPS,
    PID_INTEGRATOR_GAIN,
    PID_SATURATION,
    PID_SCALE_FLOOR,
    PID_STEP,
    PID_STEP_WINDOW,
    PID_TANGENT_LIMIT,
    OnlineDay,
    SelectedBlock,
    _PidView,
    select_constants,
)
from .splits import LookAheadError

#: The positions of q25, q50 and q75 in `QUANTILE_LEVELS`.
INTERIOR = (1, 2, 3)

#: The two ways a candidate moves the interior.
KINDS = ("per_level", "shift_scale")


class InteriorCandidate(NamedTuple):
    """One declared interior calibration.

    `kind` is one of `KINDS`; `step` the tracker's step as a share of `B`
    (the P part); `integrator_gain` and `saturation` the I part's `K_I` and
    `C_sat`, a zero gain meaning no integrator.
    """

    name: str
    kind: str
    step: float
    integrator_gain: float
    saturation: float


#: The candidates, declared before any scoring (#244, Do 1). At most four.
CANDIDATES: Tuple[InteriorCandidate, ...] = (
    # (a) per-level quantile tracking, conformal PID's P part, at #122's step.
    InteriorCandidate("a_per_level_p", "per_level", PID_STEP, 0.0, PID_SATURATION),
    # (b) a shift and a scale of the interior about v1's median, set by the
    # 25/75 miss rates, at #122's step.
    InteriorCandidate("b_shift_scale", "shift_scale", PID_STEP, 0.0, PID_SATURATION),
    # (c) (a) with #122's integrator.
    InteriorCandidate("c_per_level_pi", "per_level", PID_STEP, PID_INTEGRATOR_GAIN, PID_SATURATION),
    # (d) (a) at the PID grid's smallest step: slower, and steadier on calm days.
    InteriorCandidate("d_per_level_p_slow", "per_level", PID_GRID_STEPS[0], 0.0, PID_SATURATION),
)

#: The candidate issued while no scored day is observable at a refit.
FALLBACK = 0


def declaration() -> dict:
    """What a record states of v2's interior calibration: every candidate and constant."""

    return {
        "method": "interior calibration on v1's issued vector (#244)",
        "levels_moved": [QUANTILE_LEVELS[position] for position in INTERIOR],
        "levels_kept": [QUANTILE_LEVELS[0], QUANTILE_LEVELS[-1]],
        "candidates": [candidate._asdict() for candidate in CANDIDATES],
        "fallback": CANDIDATES[FALLBACK].name,
        "fixed_constants": {
            "PID_STEP_WINDOW": PID_STEP_WINDOW,
            "PID_SCALE_FLOOR": PID_SCALE_FLOOR,
            "PID_TANGENT_LIMIT": PID_TANGENT_LIMIT,
        },
        "edge_rule": "an outcome exactly on a level counts as half below it",
    }


def below(actual: float, level: float) -> float:
    """1 when `actual` is below `level`, a half when exactly on it, else 0."""

    if actual < level:
        return 1.0
    if actual == level:
        return 0.5
    return 0.0


def require_ordered(vector: Sequence[float]) -> Tuple[float, ...]:
    """`vector` as a tuple, when its levels are finite and non-decreasing.

    Raises:
        ValueError: a level is not finite, or a level is above the next.
    """

    values = tuple(float(value) for value in vector)
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"quantiles {values} are not all finite")
    if any(low > high for low, high in zip(values, values[1:])):
        raise ValueError(
            f"quantiles {values} are not ordered; v2 keeps q05 <= q25 <= q50 <= q75 <= q95"
        )
    return values


class InteriorState:
    """One candidate's tracker: what the labels observed so far have taught it."""

    def __init__(self, candidate: InteriorCandidate, levels: Sequence[float] = QUANTILE_LEVELS) -> None:
        if candidate.kind not in KINDS:
            raise ValueError(f"{candidate.name}: kind {candidate.kind!r} is not one of {KINDS}")
        if tuple(levels) != tuple(QUANTILE_LEVELS):
            raise ValueError(f"levels {tuple(levels)} are not {QUANTILE_LEVELS}")
        self.candidate = candidate
        self.levels = tuple(levels)
        self.offsets = [0.0] * len(INTERIOR)
        self.error_sums = [0.0] * len(INTERIOR)
        self.shift = 0.0
        self.log_scale = 0.0
        self.observed = 0
        self.last_observed: Optional[date] = None
        self.recent: Deque[float] = deque(maxlen=PID_STEP_WINDOW)

    def _scale(self) -> float:
        spread = max(self.recent) - min(self.recent) if len(self.recent) >= 2 else 0.0
        return max(spread, PID_SCALE_FLOOR)

    def _integrator(self, position: int) -> float:
        candidate = self.candidate
        if not self.observed or candidate.integrator_gain == 0.0:
            return 0.0
        n = self.observed
        argument = self.error_sums[position] * math.log(n + 1) / (candidate.saturation * (n + 1))
        argument = max(-PID_TANGENT_LIMIT, min(PID_TANGENT_LIMIT, argument))
        return -candidate.integrator_gain * self._scale() * math.tan(argument)

    def band(self, day: OnlineDay) -> Tuple[float, ...]:
        """The v2 vector issued for `day`, from v1's `day.vector` and the labels observed so far."""

        vector = require_ordered(day.vector)
        if len(vector) != len(self.levels):
            raise ValueError(f"{day.scored_date}: {len(vector)} quantiles, expected {len(self.levels)}")
        if self.candidate.kind == "per_level":
            moved = [
                vector[position] + self.offsets[k] + self._integrator(k)
                for k, position in enumerate(INTERIOR)
            ]
        else:
            median = vector[2]
            factor = math.exp(self.log_scale)
            moved = [
                median + self.shift + factor * (vector[position] - median) for position in INTERIOR
            ]
        low, high = vector[0], vector[-1]
        inner = [min(max(value, low), high) for value in sorted(moved)]
        return require_ordered((low, *inner, high))

    def observe(
        self, day: OnlineDay, band: Sequence[float], actual: float, decision: OnlineDay
    ) -> None:
        """Update on `day`'s label, as seen at `decision`'s decision instant.

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
                f"public at the instant its band is issued"
            )
        if self.last_observed is not None and day.scored_date <= self.last_observed:
            raise ValueError(
                f"the label of {day.scored_date} is observed after that of "
                f"{self.last_observed}; labels are observed once, in date order"
            )
        actual = float(actual)
        scale = self._scale()
        step = self.candidate.step
        if self.candidate.kind == "per_level":
            for k, position in enumerate(INTERIOR):
                error = below(actual, band[position]) - self.levels[position]
                self.offsets[k] -= step * scale * error
                self.error_sums[k] += error
        else:
            low = below(actual, band[1])
            high = 1.0 - below(actual, band[3])
            self.shift += step * scale * (high - low)
            self.log_scale += step * (low + high - 0.5)
        self.observed += 1
        self.last_observed = day.scored_date
        self.recent.append(actual - day.vector[2])


class OnlineInterior:
    """One candidate one day at a time: issue a day's band, later learn its label.

    Before a day's band is issued, every earlier day whose label is observable
    at its decision (scored on or before its anchor) is observed, in date
    order, as `recalibration.OnlinePid` does.
    """

    def __init__(self, candidate: InteriorCandidate) -> None:
        self.state = InteriorState(candidate)
        self._pending: Deque[Tuple[OnlineDay, Tuple[float, ...], float]] = deque()
        self._last: Optional[OnlineDay] = None

    def issue(self, day: OnlineDay) -> Tuple[float, ...]:
        """`day`'s band, from the labels observable at its decision.

        Raises:
            LookAheadError: if `day` is anchored on or after its own scored date.
            ValueError: if `day` is not after the last day issued, or its
                anchor moves back.
        """

        if day.anchor >= day.scored_date:
            raise LookAheadError(
                f"{day.scored_date} is anchored at {day.anchor}: its own label "
                f"would be observable before its band is issued"
            )
        last = self._last
        if last is not None and (day.scored_date <= last.scored_date or day.anchor < last.anchor):
            raise ValueError(
                f"days must be in scored-date order with anchors that do not move "
                f"back: {last.scored_date} (anchor {last.anchor}) is followed by "
                f"{day.scored_date} (anchor {day.anchor})"
            )
        while self._pending and self._pending[0][0].scored_date <= day.anchor:
            earlier, issued, label = self._pending.popleft()
            self.state.observe(earlier, issued, label, day)
        band = self.state.band(day)
        self._last = day
        return band

    def record(self, day: OnlineDay, band: Sequence[float], actual: float) -> None:
        """`day`'s label, held until a later decision can observe it."""

        self._pending.append((day, tuple(band), float(actual)))


def interior_walk(
    days: Sequence[OnlineDay], actuals: Sequence[float], candidate: InteriorCandidate
) -> List[Tuple[float, ...]]:
    """One candidate over `days` in order, each label learned after its own band."""

    if len(days) != len(actuals):
        raise ValueError(f"{len(days)} days and {len(actuals)} labels; they are aligned")
    online = OnlineInterior(candidate)
    bands = []
    for day, actual in zip(days, actuals):
        band = online.issue(day)
        online.record(day, band, actual)
        bands.append(band)
    return bands


class InteriorDay(NamedTuple):
    """One scored day of a fold loop under v2.

    `v1` is the vector v1 issued; `bands` every candidate's; `chosen` the
    candidate issued.
    """

    index: int
    scored_date: date
    anchor: date
    v1: Tuple[float, ...]
    bands: Tuple[Tuple[float, ...], ...]
    chosen: int


class FoldInterior:
    """v2 alongside a fold loop: v1's online calibration, then the interior.

    `pid` is v1's own fold-loop calibration over the same rows. The loop calls
    `view` and `label` exactly as it calls `pid`'s; each is passed to `pid`
    unchanged, first. `days` records every scored day.

    Raises (besides `pid`'s):
        ValueError: a band issued while the previous day's label is
            outstanding, or a label for a day other than the one issued.
        LookAheadError: from `select_constants`, if a day scored after a
            refit's anchor reached its choice; from `OnlineInterior`.
    """

    name = "interior_nested"

    def __init__(
        self,
        rows,
        pid,
        *,
        refit_every: int,
        candidates: Sequence[InteriorCandidate] = CANDIDATES,
        frozen: Optional[int] = None,
    ) -> None:
        from .asof import require_refit_every

        self._dates = [row.date for row in rows]
        self._pid = pid
        self._refit_every = require_refit_every(refit_every)
        self._candidates = tuple(candidates)
        if frozen is not None and not 0 <= frozen < len(self._candidates):
            raise ValueError(f"frozen candidate {frozen} is not one of {len(self._candidates)}")
        self._frozen = frozen
        self._onlines = [OnlineInterior(candidate) for candidate in self._candidates]
        self._open: Optional[Tuple[int, OnlineDay, Tuple[Tuple[float, ...], ...]]] = None
        self._losses: List[Tuple[date, Tuple[float, ...]]] = []
        self._chosen = FALLBACK if frozen is None else frozen
        self.blocks: Tuple[SelectedBlock, ...] = ()
        self.days: List[InteriorDay] = []

    @property
    def settings(self) -> dict:
        """v1's declaration, unchanged: v2 does not alter what v1 issues."""

        return self._pid.settings

    @property
    def interior_settings(self) -> dict:
        """v2's interior declaration, and how it chooses among the candidates."""

        choice = (
            {"method": "frozen", "candidate": self._candidates[self._frozen].name}
            if self._frozen is not None
            else {"method": "nested walk-forward selection", "loss": "crps",
                  "refit_every": self._refit_every}
        )
        return {**declaration(), "selection": choice}

    def account(self) -> dict:
        """v1's account, and the candidate chosen at each refit block."""

        account = dict(self._pid.account())
        account["interior_blocks"] = [
            {
                "first_scored": block.first_scored.isoformat(),
                "anchor": block.anchor.isoformat(),
                "past_days": block.past_days,
                "chosen": self._candidates[block.chosen].name,
            }
            for block in self.blocks
        ]
        return account

    def view(self, model, index: int, feature_row) -> _PidView:
        """`model` as scored day `rows[index]` reads it under v2."""

        if self._open is not None:
            raise ValueError(
                f"the band for {self._dates[self._open[0]]} was issued and its label "
                f"not yet given; a fold loop learns each day's label before the next "
                f"day's band"
            )
        base = self._pid.view(model, index, feature_row)
        v1 = tuple(float(value) for value in base.predict(feature_row))
        day = OnlineDay(scored_date=self._dates[index], anchor=feature_row.date, vector=v1, calendar=())
        bands = tuple(online.issue(day) for online in self._onlines)
        if self._frozen is None and len(self.days) % self._refit_every == 0:
            history = [(when, losses) for when, losses in self._losses if when <= day.anchor]
            self._chosen, past = select_constants(
                history, day.anchor, len(self._candidates), fallback=FALLBACK
            )
            self.blocks += (SelectedBlock(day.scored_date, day.anchor, past, self._chosen),)
        self._open = (index, day, bands)
        self.days.append(InteriorDay(index, day.scored_date, day.anchor, v1, bands, self._chosen))
        return _PidView(base, feature_row.date, bands[self._chosen])

    def label(self, index: int, actual: float) -> None:
        """The realised spread of scored day `rows[index]`: to v1 first, then every candidate."""

        from .metrics import crps_from_quantiles

        if self._open is None or self._open[0] != index:
            raise ValueError(
                f"a label for {self._dates[index]} was given, but the band open is "
                f"{'none' if self._open is None else self._dates[self._open[0]]}; "
                f"a label is learned once, after its own day's band"
            )
        self._pid.label(index, actual)
        _, day, bands = self._open
        losses = []
        for online, band in zip(self._onlines, bands):
            online.record(day, band, actual)
            losses.append(crps_from_quantiles(QUANTILE_LEVELS, band, float(actual)))
        self._losses.append((day.scored_date, tuple(losses)))
        self._open = None
