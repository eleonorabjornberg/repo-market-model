"""The pooled workers of the scaled-score study (#967, #999, #1013), importable by name so a `spawn` pool can run them.

macOS starts pool workers by `spawn`: the child unpickles each function and class by importing its module by name. The
workers used to live in `scripts/scaled_score_967.py`, importable only while `scripts/` is on `sys.path` (finding #1088,
the class of #1054 and #1061). They live here, with the contiguous-window helpers `calibrate` reads, which
`scripts/contiguous_calibration_963.py` defined and now imports from here. The scripts import them; nothing they compute
changes. Standard library only.
"""

from __future__ import annotations

import contextlib
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from . import scoring_protocol as sp
from .metrics import stationary_bootstrap_indices

LOOK_FRACTIONS = (0.24, 0.5, 1.0)
CALIBRATION_SEED = 1
MME = sp.MME


@dataclass(frozen=True)
class Design:
    id: str
    days: int
    leads: Tuple[int, ...]
    scale: str  # "raw", "new" (this study's), "old" (#733's D4 scale)
    score: str = "grid"  # "grid" or "trapezoid"

    @property
    def checkpoints(self) -> Tuple[int, int, int]:
        first, second = (int(fraction * self.days + 0.5) for fraction in LOOK_FRACTIONS[:2])
        return first, second, self.days


def contiguous_window_statistics(series: Sequence[float], *, days: int, hac_lag: int = sp.HAC_LAG) -> List[float]:
    """Sorted studentized means of every window of `days` consecutive days of `series`, none wrapping.

    A window starting at `s` holds `series[s:s + days]` for every `s` in `[0, n - days]`; its statistic is
    `(mean_w - mean(series)) / se_w` with `se_w` its Newey-West standard error at `hac_lag`, as
    `scoring_protocol.window_t_statistics` computes it.

    Raises:
        ValueError: the series is shorter than `days`, or `days` cannot carry the lag.
    """

    values = [sp._finite(v, "a daily difference") for v in series]
    if days > len(values):
        raise ValueError(f"a series of {len(values)} days holds no window of {days} days")
    if days <= hac_lag:
        raise ValueError(f"windows of {days} days cannot carry a lag-{hac_lag} long-run variance")
    truth = sum(values) / len(values)
    out = []
    for start in range(len(values) - days + 1):
        window = values[start:start + days]
        out.append((sum(window) / days - truth) / sp._standard_error(window, hac_lag, "a window"))
    return sorted(out)


@contextlib.contextmanager
def stationary_windows():
    """Within the block, `scoring_protocol`'s windows are stationary-bootstrap resamples (as #886 draws them)."""

    original = sp._window_indices
    sp._window_indices = lambda size, days, rng, block: list(stationary_bootstrap_indices(size, block, rng)[:days])
    try:
        yield
    finally:
        sp._window_indices = original


def candidate(b: Sequence[float], e: Sequence[float], delta: float, noise: float = 1.0) -> List[float]:
    centre = sum(e) / len(e)
    return [delta * x + noise * (y - centre) for x, y in zip(b, e)]


def calibrate(job) -> Tuple[str, Dict[str, object]]:
    """The design's critical value at each look after the first: the contiguous windows of the series `e` the paths are built
    on (S(B1) - S(B2), positive where B2 is better), and, beside it, the stationary-10 windows of #886.

    `job` is `(design, e, windows)`, or `(design, e, windows, -1.0)` for the orientation #999 used, which calibrated on
    `-e` while the paths used `e` (finding #1000); only the row check of #1013 asks for it."""

    design, e, windows = job[:3]
    sign = job[3] if len(job) > 3 else 1.0
    looks = design.checkpoints
    levels = sp.nominal_levels(looks)
    series = [sign * v for v in e]
    contiguous, stationary, counts = {}, {}, {}
    for k, n in enumerate(looks[1:], start=1):
        ordered = contiguous_window_statistics(series, days=n)
        contiguous[str(n)] = sp._bound(ordered, 1.0 - levels[k], len(ordered))
        counts[str(n)] = len(ordered)
        with stationary_windows():
            ordered = sp.window_t_statistics(series, days=n, windows=windows, seed=CALIBRATION_SEED, block=sp.BLOCK_LENGTH)
        stationary[str(n)] = sp._bound(ordered, 1.0 - levels[k], len(ordered))
    return design.id, {"checkpoints": list(looks), "nominal_levels": list(levels), "critical": contiguous,
                       "critical_stationary": stationary, "windows": counts, "series_days": len(e)}


_DATA: Dict[str, object] = {}


def _init(histories, critical):
    _DATA["histories"] = histories
    _DATA["critical"] = critical


def run_path(job) -> Tuple[Optional[int], Optional[int]]:
    """One path: the look at which the bound is first above zero, and the first at which the gated rule also holds."""

    design, delta, seed, generator = job
    b, e = _DATA["histories"][design.id]
    critical = _DATA["critical"][design.id]
    x = candidate(b, e, delta)
    rng = random.Random(seed)
    if generator == "stationary":
        index = list(stationary_bootstrap_indices(len(b), sp.BLOCK_LENGTH, rng))[: design.days]
    else:
        index = []
        while len(index) < design.days:
            start = rng.randrange(len(b))
            index.extend((start + k) % len(b) for k in range(sp.WINDOW_BLOCK))
        index = index[: design.days]
    xs, bs = [x[i] for i in index], [b[i] for i in index]
    ungated = gated = None
    for n in design.checkpoints[1:]:
        part = xs[:n]
        mean = sum(part) / n
        if mean - critical[str(n)] * sp._standard_error(part, sp.HAC_LAG, "a path") > 0.0:
            if ungated is None:
                ungated = n
            if gated is None and mean / (sum(bs[:n]) / n) >= MME:
                gated = n
    return ungated, gated
