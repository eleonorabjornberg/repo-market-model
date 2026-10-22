"""The pooled workers of the confirmation-design studies (#733, #886), importable by name so a `spawn` pool can run them.

macOS starts pool workers by `spawn`: the child unpickles each function and class by importing its module by name. The
workers used to live in `scripts/confirmation_design.py`, which `scripts/postcovid_886.py` loads by path under a name no
child can import (finding #1088, the class of #1054 and #1061). They live here; the scripts import them, and nothing
they compute changes. Standard library only.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Sequence, Tuple

from . import scoring_protocol as sp
from .metrics import stationary_bootstrap_indices

#: §4 of `docs/research/confirmation-design-733.md`: the looks at these fractions of a design's days.
LOOK_FRACTIONS = (0.24, 0.5, 1.0)
CALIBRATION_SEED = 1
#: Decision days from this day are "post-2020".
POST_2020_FIRST = date(2020, 4, 3)


class RuleError(ValueError):
    """The study was asked for something its rule does not say."""


def checkpoints(days: int) -> Tuple[int, int, int]:
    """§4: the looks at 24%, 50% and 100% of `days`, rounded half up."""

    first, second = (int(fraction * days + 0.5) for fraction in LOOK_FRACTIONS[:2])
    return first, second, days


@dataclass(frozen=True)
class Design:
    id: str
    days: int
    leads: Tuple[int, ...]
    standardized: bool

    @property
    def checkpoints(self) -> Tuple[int, int, int]:
        return checkpoints(self.days)


@dataclass
class Series:
    """A design's series on its score scale: `dates`, `b` (B1's score), `e` (B1 minus B2), and B3's pair `dates3`, `e3`."""

    dates: List[date]
    b: List[float]
    e: List[float]
    dates3: List[date]
    e3: List[float]


def candidate(b: Sequence[float], e: Sequence[float], delta: float, noise: float) -> List[float]:
    """§3: `x_t = delta * b_t + noise * (e_t - mean(e))`. Its mean skill against B1 is `delta`."""

    centre = sum(e) / len(e)
    return [delta * x + noise * (y - centre) for x, y in zip(b, e)]


# -- the calibration (§5) --------------------------------------------------------------------------------------------


def window_statistics(series: Sequence[float], *, days: int, lengths: Sequence[int], windows: int, seed: int,
                      block: int = sp.WINDOW_BLOCK) -> Dict[int, List[float]]:
    """Sorted studentized means of `windows` windows of `days` days, read at each prefix length in `lengths`.

    The windows are those of `scoring_protocol.window_t_statistics` (same draws for the same seed), whose statistic is
    `(mean_w - mean(series)) / se_w`; a look reads the window's first `lengths[k]` days.
    """

    values = [float(v) for v in series]
    truth = sum(values) / len(values)
    rng = random.Random(seed)
    size = len(values)
    out = {n: [] for n in lengths}
    for _ in range(windows):
        window: List[float] = []
        while len(window) < days:
            start = rng.randrange(size)
            window.extend(values[(start + k) % size] for k in range(block))
        window = window[:days]
        for n in lengths:
            part = window[:n]
            out[n].append((sum(part) / n - truth) / sp._standard_error(part, sp.HAC_LAG, "a window"))
    return {n: sorted(v) for n, v in out.items()}


def pair_series(series: Series) -> Dict[str, List[float]]:
    """The four calibration series. `e` is S(B1) - S(B2), so "B2-B1" here is the candidate-side orientation (a B2-like
    candidate against B1) and "B1-B2" is `S(B2) - S(B1)`, the orientation PR #695 calls B2 - B1."""

    return {
        "B2-B1": list(series.e), "B1-B2": [-v for v in series.e],
        "B3-B1 (five levels)": list(series.e3), "B1-B3 (five levels)": [-v for v in series.e3],
    }


def calibrate_design(args) -> Tuple[str, Dict[str, object]]:
    """The design's critical values at looks 2 and 3: per pair, and the largest across the four."""

    design, series, windows = args
    looks = design.checkpoints
    levels = sp.nominal_levels(looks)
    per_pair = {}
    for name, values in pair_series(series).items():
        ordered = window_statistics(values, days=design.days, lengths=looks[1:], windows=windows, seed=CALIBRATION_SEED)
        per_pair[name] = {
            str(n): sp._bound(ordered[n], 1.0 - levels[k + 1], windows) for k, n in enumerate(looks[1:])
        }
    protocol = {str(n): max(per_pair[name][str(n)] for name in per_pair) for n in looks[1:]}
    return design.id, {
        "checkpoints": list(looks), "nominal_levels": list(levels), "per_pair": per_pair,
        "critical_values": protocol, "series_days": len(series.b), "series_days_b3": len(series.e3),
    }


# -- the paths (§5, §6) ----------------------------------------------------------------------------------------------

_DATA: Dict[str, object] = {}


def init_worker(histories, critical):
    _DATA["histories"] = histories
    _DATA["critical"] = critical


def history_slice(series: Series, history: str) -> Tuple[List[float], List[float]]:
    if history == "full":
        return series.b, series.e
    if history == "post-2020":
        keep = [i for i, day in enumerate(series.dates) if day >= POST_2020_FIRST]
        return [series.b[i] for i in keep], [series.e[i] for i in keep]
    raise RuleError(f"unknown history {history!r}")


def run_path(job) -> Optional[int]:
    """One path: the look at which the candidate is detected (gated), and the first look its bound is above zero."""

    design, history, delta, noise, seed, *rest = job
    generator = rest[0] if rest else "stationary"
    b, e = _DATA["histories"][(design.id, history)]
    critical = _DATA["critical"][design.id]
    x = candidate(b, e, delta, noise)
    rng = random.Random(seed)
    if generator == "stationary":
        index = stationary_bootstrap_indices(len(b), sp.BLOCK_LENGTH, rng)[: design.days]
    elif generator == "circular":
        index = []
        while len(index) < design.days:
            start = rng.randrange(len(b))
            index.extend((start + k) % len(b) for k in range(sp.WINDOW_BLOCK))
        index = index[: design.days]
    else:
        raise RuleError(f"unknown generator {generator!r}")
    xs = [x[i] for i in index]
    bs = [b[i] for i in index]
    ungated = gated = None
    for n in design.checkpoints[1:]:
        part = xs[:n]
        mean = sum(part) / n
        if mean - critical[str(n)] * sp._standard_error(part, sp.HAC_LAG, "a path") > 0.0:
            if ungated is None:
                ungated = n
            if gated is None and mean / (sum(bs[:n]) / n) >= sp.MME:
                gated = n
    return ungated, gated


# -- the post-2020 stationary values of #886 -------------------------------------------------------------------------


def post_2020(days, values):
    """The days from `POST_2020_FIRST` and their values, in order.

    Raises:
        ValueError: `days` and `values` differ in length.
    """

    if len(days) != len(values):
        raise ValueError(f"{len(days)} days but {len(values)} values")
    kept = [(d, v) for d, v in zip(days, values) if d >= POST_2020_FIRST]
    return [d for d, _ in kept], [v for _, v in kept]


def stationary_window_indices(size, days, rng, block):
    """A window of `days` positions drawn as the power study draws a path: a stationary bootstrap resample."""

    return list(stationary_bootstrap_indices(size, block, rng)[:days])


def stationary_window_statistics(series, *, days, lengths, windows, seed, block=sp.BLOCK_LENGTH):
    """`window_statistics` with stationary-bootstrap windows: sorted studentized means at each look."""

    values = [float(v) for v in series]
    truth = sum(values) / len(values)
    rng = random.Random(seed)
    out = {n: [] for n in lengths}
    for _ in range(windows):
        window = [values[i] for i in stationary_window_indices(len(values), days, rng, block)]
        for n in lengths:
            part = window[:n]
            out[n].append((sum(part) / n - truth) / sp._standard_error(part, sp.HAC_LAG, "a window"))
    return {n: sorted(v) for n, v in out.items()}


def design_values(job):
    """A design's values at looks 2 and 3 on the candidate-side series `e`: (a) full history, circular blocks (#873's
    reading) and (b) post-2020 days, stationary bootstrap (#886's)."""

    design, series, windows = job
    looks = design.checkpoints
    levels = sp.nominal_levels(looks)
    full = window_statistics(series.e, days=design.days, lengths=looks[1:], windows=windows, seed=CALIBRATION_SEED)
    _days, post = post_2020(series.dates, series.e)
    after = stationary_window_statistics(post, days=design.days, lengths=looks[1:], windows=windows, seed=CALIBRATION_SEED)
    return design.id, {
        "full_history_circular": {str(n): sp._bound(full[n], 1.0 - levels[k + 1], windows) for k, n in enumerate(looks[1:])},
        "post_2020_stationary": {str(n): sp._bound(after[n], 1.0 - levels[k + 1], windows) for k, n in enumerate(looks[1:])},
        "series_days": len(series.e), "post_2020_days": len(post),
    }
