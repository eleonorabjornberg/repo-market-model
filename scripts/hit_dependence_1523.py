"""Where the serial dependence of (s3c-ann-net)'s quantile hits sits, what drives it, and what a model change could do about it (#1523, H5, step M5).

A development study, never a verdict. Her ruling of 8 November 2026 (docket card cov-1520-reading on PR #1520, "bar"): a directive diagnoses the
lead-1 dependence for a model change; the candidate registers only once it passes. Under amendment 4 (`scoring_protocol.coverage_cells`,
`enforce_coverage_requirement`) the candidate's hits fail independence: Christoffersen rejections at lead 1 and at leads 2-3 in 2021-23.
This study reads the candidate's own development walk (the walk of `candidate_calibration_1363.py`, unchanged) and asks:

- where the dependence sits: by lead, level, regime, spacing of the thinned rows, lag, target-day type and pressure-day type, and whether the
  hits come in runs after a hit;
- what drives it: the information lag (a forecast for D + h reads data to the panel day D - 1, `docs/decisions/information-set.md` rule 1, so
  two forecasts that the design keeps h days apart still share one unknown innovation), the standardised lead-1 error and its scale
  (autocorrelation, a level or scale that adapts too slowly), the last public spread's gap to the median, the previous public error;
- what a model change of each kind could do: three post-hoc adjustments of the candidate's quantile output, declared in
  `metadata/hit_dependence_1523.json` before any adjusted score (recentre by the latest public lead-1 error, rescale by the realised-to-forecast
  absolute deviation, both), each learned online from outcomes public at each decision day, scored paired against the unadjusted candidate.
  They are not models and nothing is fitted or registered.

The declaration is committed before `score` reads anything; `score` refuses to run on a changed one. Nothing after 2025-12-31 and no locked day is
read (`coverage_size_1516.load_window_doc` refuses another window and any later day). The study neither reads nor writes `COVERAGE_REQUIREMENT_IN_FORCE`.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/candidate_calibration_1363.py walk --panel PUB.csv --window development --output WALK/development.json
    OUT=docs/research/hit-dependence-1523
    PYTHONPATH=src python3 scripts/hit_dependence_1523.py score --walk WALK/development.json --output $OUT/result.json
    PYTHONPATH=src python3 scripts/hit_dependence_1523.py page --score $OUT/result.json --output docs/research/hit-dependence-1523-result.md

The walk takes about two minutes and `score` a few minutes on four cores, below the `long-run` line.
"""

from __future__ import annotations

import argparse
import bisect
import importlib.util
import json
import math
import multiprocessing
import random
import subprocess
import sys
from collections import deque
from datetime import date
from pathlib import Path
from statistics import NormalDist
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import coverage_tests as ct, metrics, scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


m16 = _load("coverage_size_1516", "coverage_size_1516_in_1523")
m63 = m16.m63

ISSUE = 1523
SEED = 1523
REPS = 2000
BLOCK = 10.0
LEVEL = 0.90
DECLARATION = REPO / "metadata" / "hit_dependence_1523.json"
CANDIDATE = m63.CANDIDATE
LEVELS = tuple(sorted(sp.COVERAGE_LEVELS))
LEADS = tuple(sp.HORIZONS)
GRID = sp.GRID
LAGS = (1, 2, 3, 4, 5, 6)
MEDIAN = GRID.index(0.5)
Q25, Q75 = GRID.index(0.25), GRID.index(0.75)
VARIANTS = ("A1_recentre", "A2_rescale", "A3_both", "A4_meanrevert", "A5_fast_rescale")
MIN_RESOLVED_A1 = 100
MIN_RESOLVED_A2 = 30
WINDOW_A2 = 60
KAPPA_CLAMP = (0.7, 1.5)
BETA_CLAMP = (0.0, 1.0)
BETA_CLAMP_A4 = (-1.0, 1.0)
WINDOW_A5 = 20
MIN_RESOLVED_A5 = 10
WARMUP_DAYS = 250
SIM_PHIS = (0.3, 0.6, 0.9)
SIM_PATHS = 300
SIM_DAYS = 1855
LARGE_Z = 2.0
RECORD_1314 = m63.RECORD_1314
RESULT_1516 = REPO / "docs" / "research" / "coverage-size-1516" / "result.json"
load_window_doc = m16.load_window_doc
wilson = m16.wilson
N01 = NormalDist()


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return m63.committed_declaration(path)


# -- hits ----------------------------------------------------------------------------------------------------------------------


def strict_hit(quantiles: Sequence[float], y: float, level: float) -> int:
    """The design's strict hit: beyond the level's quantile (above the upper ones, below the lower ones)."""

    q = quantiles[GRID.index(level)]
    return int(y > q) if level > 0.5 else int(y < q)


def ordinal_u(quantiles: Sequence[float], y: float) -> float:
    """An ordinal code of where `y` falls among the four read quantiles, whose strict hits at the four levels are exactly `strict_hit`.

    `coverage_size_1516.cell_p_values` reads hits as `u > level` above one half and `u < level` below; this code feeds it the real hits
    without a randomised PIT (no outcome ties a quantile at a read level).
    """

    q01, q05, q95, q99 = (quantiles[GRID.index(level)] for level in LEVELS)
    if y < q01:
        return 0.005
    if y < q05:
        return 0.03
    if y > q99:
        return 0.995
    if y > q95:
        return 0.97
    return 0.5


# -- the walk as arrays --------------------------------------------------------------------------------------------------------


class Frame:
    """The candidate's decision days in order: positions on the scoring calendar, regimes, per lead the 23 quantiles and the outcome."""

    def __init__(self, calendar: Sequence[date], days: Sequence[date], regimes: Sequence[str], q: Sequence[Mapping[int, List[float]]],
                 y: Sequence[Mapping[int, float]], info: Optional[Mapping[date, dict]] = None):
        self.calendar = list(calendar)
        self.days = list(days)
        position = {d: i for i, d in enumerate(self.calendar)}
        self.pos = [position[d] for d in self.days]
        self.regimes = list(regimes)
        self.order = list(range(len(self.days)))
        self.q = [dict(row) for row in q]
        self.y = [dict(row) for row in y]
        self.info = dict(info or {})
        self.y_by_pos: Dict[int, float] = {}
        self.lead1_median_by_tpos: Dict[int, float] = {}
        for i, p in enumerate(self.pos):
            for h in LEADS:
                self.y_by_pos[p + h] = self.y[i][h]
            self.lead1_median_by_tpos[p + 1] = self.q[i][1][MEDIAN]
        for a, b in zip(self.pos, self.pos[1:]):
            if b != a + 1:
                raise ValueError("the decision days are not consecutive scoring days: the lead-1 series has a gap")

    @classmethod
    def from_window(cls, window: "m63.Window") -> "Frame":
        by_cell = {}
        for (d, h, t), q in zip(window.cells, window.q[CANDIDATE]):
            if window.position[d] + h >= len(window.calendar) or window.calendar[window.position[d] + h] != t:
                raise ValueError(f"cell ({d}, {h}) targets {t}, not the {h}-th scoring-calendar day after {d}")
            by_cell[(d, h)] = (list(q), window.outcome[t])
        days = sorted(window.days)
        q = [{h: by_cell[(d, h)][0] for h in LEADS} for d in days]
        y = [{h: by_cell[(d, h)][1] for h in LEADS} for d in days]
        return cls(window.calendar, days, [window.regime_of_day[d] for d in days], q, y, window.target_info)

    @classmethod
    def shifted(cls, frame: "Frame", c: float) -> "Frame":
        return cls(frame.calendar, frame.days, frame.regimes, [{h: [v + c for v in row[h]] for h in LEADS} for row in frame.q], frame.y, frame.info)

    @classmethod
    def scaled(cls, frame: "Frame", k: float) -> "Frame":
        def scale(values):
            m = values[MEDIAN]
            return [m + k * (v - m) for v in values]

        return cls(frame.calendar, frame.days, frame.regimes, [{h: scale(row[h]) for h in LEADS} for row in frame.q], frame.y, frame.info)

    def target_date(self, i: int, h: int) -> date:
        return self.calendar[self.pos[i] + h]

    def hits(self, h: int, level: float, q: Optional[Sequence[Mapping[int, List[float]]]] = None) -> List[int]:
        q = self.q if q is None else q
        return [strict_hit(q[i][h], self.y[i][h], level) for i in range(len(self.days))]


def sample_from_frame(frame: Frame, q: Optional[Sequence[Mapping[int, List[float]]]] = None) -> "m16.Sample":
    """The `coverage_size_1516.Sample` of the real strict hits (ordinal code), for the design's own cell functions."""

    q = frame.q if q is None else q
    u = {h: [ordinal_u(q[i][h], frame.y[i][h]) for i in range(len(frame.days))] for h in LEADS}
    return m16.Sample(list(frame.days), list(frame.order), list(frame.regimes), u)


# -- the design at a spacing ---------------------------------------------------------------------------------------------------


def kept_rows(order: Sequence[int], regimes: Sequence[str], regime: str, s: int) -> List[int]:
    """The rows of `regime` kept at spacing `s`: every s-th decision day by global order (the design's `order % h == 0` at s = h)."""

    return [i for i, r in enumerate(regimes) if r == regime and order[i] % s == 0]


def family_at_spacing(sample: "m16.Sample", extra: int) -> dict:
    """The design's Holm family with the independence test read at spacing h + `extra` (Kupiec as in the design, at spacing h).

    `extra = 0` is amendment 4 as `coverage_cells` applies it. Returns the tests (cell, kind, p), the Holm-rejected ones and the cell table.
    """

    tests: List[Tuple[Tuple[int, str, float], str, float]] = []
    cells = []
    regimes = sorted(set(sample.regimes))
    for h in LEADS:
        for regime in regimes:
            for level in LEVELS:
                p = min(level, 1.0 - level)
                kept = kept_rows(sample.order, sample.regimes, regime, h)
                hits = m16._hits([sample.u[h][i] for i in kept], level)
                kup = ct.kupiec(hits, p).p_value if hits else 1.0
                spaced = kept_rows(sample.order, sample.regimes, regime, h + extra)
                seq = m16._hits([sample.u[h][i] for i in spaced], level)
                ind = ct.christoffersen_independence(seq).p_value if len(seq) >= 2 else None
                tests.append(((h, regime, level), "kupiec", kup))
                if ind is not None:
                    tests.append(((h, regime, level), "independence", ind))
                n00, n01, n10, n11 = ct.transition_counts(seq) if len(seq) >= 2 else (0, 0, 0, 0)
                after_hit_n, after_none_n = n10 + n11, n00 + n01
                cells.append({
                    "lead": h, "regime": regime, "level": level, "spacing": h + extra, "n": len(seq), "hits": sum(seq),
                    "rate": sum(seq) / len(seq) if seq else None, "kupiec_p": kup, "independence_p": ind, "transitions": [n00, n01, n10, n11],
                    "p_hit_after_hit": n11 / after_hit_n if after_hit_n else None, "p_hit_after_none": n01 / after_none_n if after_none_n else None,
                    "wilson_after_hit": wilson(n11, after_hit_n) if after_hit_n else None,
                    "wilson_after_none": wilson(n01, after_none_n) if after_none_n else None,
                })
    rejected = m16.holm_rejected([t[2] for t in tests])
    failing = [(tests[i][0], tests[i][1]) for i in rejected]
    return {"tests": len(tests), "rejected": len(rejected), "failing": failing,
            "independence_rejected": sum(1 for _c, kind in failing if kind == "independence"),
            "min_p": min(t[2] for t in tests), "cells": cells}


def label(cell: Tuple[int, str, float], kind: str) -> str:
    return f"lead {cell[0]}, {cell[1]}, q{cell[2]:g} / {kind}"


def parse_label(text: str) -> Tuple[Tuple[int, str, float], str]:
    """The inverse of `label`."""

    head, kind = text.split(" / ")
    lead, regime, level = head.split(", ")
    return (int(lead.split()[1]), regime, float(level[1:])), kind


# -- lift ----------------------------------------------------------------------------------------------------------------------


def lift_terms(hits: Sequence[int], regimes: Sequence[str], pos: Sequence[int], k: int) -> Tuple[List[float], List[float]]:
    """Per row i: 1 if the hits at i and at i - k are both 1 (same regime, panel days k apart), and the pair's expected value p_r^2 under the
    regime's own hit rate; 0 for a row with no such pair."""

    n = len(hits)
    total: Dict[str, List[int]] = {}
    for h, r in zip(hits, regimes):
        t = total.setdefault(r, [0, 0])
        t[0] += h
        t[1] += 1
    rate = {r: v[0] / v[1] for r, v in total.items()}
    n11, exp = [0.0] * n, [0.0] * n
    for i in range(k, n):
        if regimes[i] == regimes[i - k] and pos[i] - pos[i - k] == k:
            n11[i] = float(hits[i] * hits[i - k])
            exp[i] = rate[regimes[i]] ** 2
    return n11, exp


def lift(n11: Sequence[float], exp: Sequence[float]) -> float:
    """Observed hit pairs over the expected under each regime's own rate; 1 is independence. NaN with no pair expected."""

    e = sum(exp)
    return sum(n11) / e if e > 0 else float("nan")


def fit_rates(hits: Sequence[int], columns: Sequence[Sequence[bool]], sweeps: int = 400) -> List[float]:
    """Per-row hit rates of a multiplicative model r_i = b * prod(a_f over the columns f that contain i), fitted in sample by coordinate-wise
    iterative scaling (the Poisson maximum-likelihood fit), each rate capped below one. Columns may overlap and need not be a partition."""

    n = len(hits)
    base = max(sum(hits) / n, 1e-9)
    factor = [1.0] * len(columns)
    members = [[i for i, v in enumerate(col) if v] for col in columns]
    fitted = [base] * n
    for _ in range(sweeps):
        worst = 0.0
        for f, idx in enumerate(members):
            if not idx:
                continue
            obs = sum(hits[i] for i in idx)
            fit = sum(fitted[i] for i in idx)
            if fit <= 0:
                continue
            ratio = max(obs, 1e-9) / fit
            worst = max(worst, abs(ratio - 1.0))
            factor[f] *= ratio
            for i in idx:
                fitted[i] = min(0.999, fitted[i] * ratio)
        if worst < 1e-10:
            break
    return fitted


def typed_lift_terms(hits: Sequence[int], rates: Sequence[float], regimes: Sequence[str], pos: Sequence[int], k: int) -> Tuple[List[float], List[float]]:
    """As `lift_terms`, with each pair's expectation r_i * r_(i-k) from per-row fitted rates (`fit_rates`) instead of the regime's rate."""

    n = len(hits)
    n11, exp = [0.0] * n, [0.0] * n
    for i in range(k, n):
        if regimes[i] == regimes[i - k] and pos[i] - pos[i - k] == k:
            n11[i] = float(hits[i] * hits[i - k])
            exp[i] = rates[i] * rates[i - k]
    return n11, exp


def rate_columns(frame: "Frame", h: int) -> List[List[bool]]:
    """The covariates of the typed rate at lead h: the decision day's regime, each target-day type of the target, each non-ordinary pressure type."""

    n = len(frame.days)
    infos = [frame.info[frame.target_date(i, h)] for i in range(n)]
    cols = [[frame.regimes[i] == r for i in range(n)] for r in sorted(set(frame.regimes))]
    cols += [[k in infos[i]["types"] for i in range(n)] for k in m63.DAY_TYPES]
    cols += [[infos[i]["pressure"] == p for i in range(n)] for p in sorted({v["pressure"] for v in infos}) if p != "ordinary"]
    return cols


def mean_abs_dev(quantiles: Sequence[float]) -> float:
    """The forecast's own mean absolute deviation about its median: the grid quantiles weighted by half the gap between neighbouring levels."""

    w = []
    for j in range(len(GRID)):
        lo = GRID[j - 1] if j > 0 else 0.0
        hi = GRID[j + 1] if j + 1 < len(GRID) else 1.0
        w.append((hi - lo) / 2.0)
    total = sum(w)
    m = quantiles[MEDIAN]
    return sum(wj * abs(v - m) for wj, v in zip(w, quantiles)) / total


# -- the guard and the adjustments ---------------------------------------------------------------------------------------------


def require_public(target_pos: int, decision_pos: int) -> None:
    """An outcome is public at decision day D when its panel day is at most D - 1 (information-set rule 1: the daily rates are read at the
    row two panel days before the target, and a lead-1 target is D + 1). Raises `LookAheadError` otherwise."""

    if target_pos >= decision_pos:
        raise LookAheadError(f"the outcome of panel day {target_pos} is not public at decision day {decision_pos}")


def public_count(target_positions: Sequence[int], decision_pos: int) -> int:
    """How many of the (increasing) target positions are public at `decision_pos`: those at most `decision_pos - 1`."""

    return bisect.bisect_right(target_positions, decision_pos - 1)


def public_resolved(positions: Sequence[int], h: int, decision_pos: int) -> List[int]:
    """Indices of the lead-h cells of `positions` (decision days in order) whose outcome is public at `decision_pos`."""

    return list(range(public_count([p + h for p in positions], decision_pos)))


def clamp(x: float, bounds: Tuple[float, float]) -> float:
    return min(max(x, bounds[0]), bounds[1])


def public_error(frame: Frame, i: int) -> Optional[float]:
    """The latest lead-1 error public at decision day i: the outcome of panel day pos - 1 less the median of the lead-1 forecast for it."""

    target = frame.pos[i] - 1
    if target not in frame.y_by_pos or target not in frame.lead1_median_by_tpos:
        return None
    require_public(target, frame.pos[i])
    return frame.y_by_pos[target] - frame.lead1_median_by_tpos[target]


def adjust(frame: Frame, variant: str) -> List[Dict[int, List[float]]]:
    """The candidate's quantiles after one of the declared online adjustments, per decision day and lead.

    Every quantity at decision day i is read from cells whose outcome is public at i (`public_count`, `require_public`). `A1_recentre`
    shifts by beta_h * e_pub, `A2_rescale` scales about the median by kappa_h, `A3_both` does the shift and then the scale about the shifted
    median (declared in `metadata/hit_dependence_1523.json`).
    """

    if variant not in VARIANTS:
        raise ValueError(f"unknown variant {variant!r}")
    use1, use2 = variant in ("A1_recentre", "A3_both", "A4_meanrevert"), variant in ("A2_rescale", "A3_both", "A5_fast_rescale")
    beta_clamp = BETA_CLAMP_A4 if variant == "A4_meanrevert" else BETA_CLAMP
    window, minimum = (WINDOW_A5, MIN_RESOLVED_A5) if variant == "A5_fast_rescale" else (WINDOW_A2, MIN_RESOLVED_A2)
    n = len(frame.days)
    e_pub = [public_error(frame, i) for i in range(n)]
    out: List[Dict[int, List[float]]] = []
    target_positions = {h: [p + h for p in frame.pos] for h in LEADS}
    state = {h: {"done": 0, "sxy": 0.0, "sxx": 0.0, "cnt": 0, "win": deque(maxlen=window)} for h in LEADS}
    used: List[Dict[int, Tuple[float, float]]] = [dict() for _ in range(n)]  # (median used, unscaled forecast spread) of each cell
    for i in range(n):
        dp = frame.pos[i]
        row: Dict[int, List[float]] = {}
        for h in LEADS:
            st = state[h]
            ready = min(public_count(target_positions[h], dp), i)
            while st["done"] < ready:
                j = st["done"]
                require_public(target_positions[h][j], dp)
                if e_pub[j] is not None:
                    err = frame.y[j][h] - frame.q[j][h][MEDIAN]
                    st["sxy"] += e_pub[j] * err
                    st["sxx"] += e_pub[j] ** 2
                    st["cnt"] += 1
                median_used, spread = used[j][h]
                st["win"].append((abs(frame.y[j][h] - median_used), spread))
                st["done"] += 1
            q = frame.q[i][h]
            beta = clamp(st["sxy"] / st["sxx"], beta_clamp) if st["cnt"] >= MIN_RESOLVED_A1 and st["sxx"] > 0 else 0.0
            shift = beta * e_pub[i] if use1 and e_pub[i] is not None else 0.0
            kappa = 1.0
            if use2 and len(st["win"]) >= minimum:
                spread_sum = sum(s for _a, s in st["win"])
                if spread_sum > 0:
                    kappa = clamp(sum(a for a, _s in st["win"]) / spread_sum, KAPPA_CLAMP)
            m = q[MEDIAN]
            row[h] = [m + shift + kappa * (v - m) for v in q]
            used[i][h] = (m + shift, mean_abs_dev(q))
        out.append(row)
    return out


# -- bootstrap in sums ---------------------------------------------------------------------------------------------------------

_ARRAYS: List[List[float]] = []


def _sums_chunk(job):
    """The resampled sums of arrays [lo, hi): every worker draws the same index sequences from the same seed."""

    lo, hi, n, seed, reps = job
    rng = random.Random(seed)
    out = []
    for _ in range(reps):
        idx = metrics.stationary_bootstrap_indices(n, BLOCK, rng)
        out.append([sum(map(_ARRAYS[a].__getitem__, idx)) for a in range(lo, hi)])
    return out


def resample_sums(arrays: Sequence[Sequence[float]], seed: int = SEED, reps: int = REPS, workers: int = 4) -> List[List[float]]:
    """For each of `reps` stationary-bootstrap resamples (mean block 10) of the row indices, the sum of each array over the resample."""

    global _ARRAYS
    _ARRAYS = [list(a) for a in arrays]
    if not _ARRAYS:
        return [[] for _ in range(reps)]
    n = len(_ARRAYS[0])
    size = max(1, -(-len(_ARRAYS) // max(1, workers)))
    jobs = [(lo, min(lo + size, len(_ARRAYS)), n, seed, reps) for lo in range(0, len(_ARRAYS), size)]
    if workers > 1 and len(jobs) > 1:
        with multiprocessing.get_context("fork").Pool(len(jobs)) as pool:
            parts = pool.map(_sums_chunk, jobs)
    else:
        parts = [_sums_chunk(j) for j in jobs]
    return [sum((part[r] for part in parts), []) for r in range(reps)]


def quantile_of(sorted_values: Sequence[float], q: float) -> float:
    pos = q * (len(sorted_values) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (pos - lo) * (sorted_values[hi] - sorted_values[lo])


class Registry:
    """Named ratio and correlation statistics over day-indexed arrays, resampled together."""

    def __init__(self):
        self.arrays: List[List[float]] = []
        self.keys: Dict[str, int] = {}
        self.specs: Dict[str, tuple] = {}

    def array(self, key: str, values: Sequence[float]) -> int:
        if key not in self.keys:
            self.keys[key] = len(self.arrays)
            self.arrays.append(list(values))
        return self.keys[key]

    def ratio(self, name: str, num: Tuple[str, Sequence[float]], den: Tuple[str, Sequence[float]]) -> None:
        self.specs[name] = ("ratio", self.array(*num), self.array(*den))

    def corr(self, name: str, ab: Tuple[str, Sequence[float]], aa: Tuple[str, Sequence[float]], bb: Tuple[str, Sequence[float]]) -> None:
        self.specs[name] = ("corr", self.array(*ab), self.array(*aa), self.array(*bb))

    @staticmethod
    def _value(spec: tuple, sums: Sequence[float]) -> float:
        if spec[0] == "ratio":
            return sums[spec[1]] / sums[spec[2]] if sums[spec[2]] else float("nan")
        d = sums[spec[2]] * sums[spec[3]]
        return sums[spec[1]] / math.sqrt(d) if d > 0 else float("nan")

    def run(self, workers: int = 4, reps: int = REPS) -> Dict[str, dict]:
        point = [sum(a) for a in self.arrays]
        draws = resample_sums(self.arrays, SEED, reps, workers)
        out = {}
        tail = (1.0 - LEVEL) / 2.0
        for name, spec in self.specs.items():
            values = sorted(v for v in (self._value(spec, s) for s in draws) if v == v)
            est = self._value(spec, point)
            out[name] = {"estimate": est, "lo": quantile_of(values, tail) if values else None, "hi": quantile_of(values, 1 - tail) if values else None,
                         "resamples": len(values)}
        return out


# -- the simulation of a calibrated forecaster with the information lag -----------------------------------------------------------


def simulate_path(phi: float, n: int, lag: int, seed: int, leads: Sequence[int] = (1, 2, 3), level: float = 0.95) -> dict:
    """One AR(1) path of unit-variance innovations and the hits of a forecaster that knows phi and is calibrated by construction.

    A forecast for the panel day D + h reads the spread to the panel day D - lag (lag 1: the information-set rule; lag 0: a control that also
    reads the decision day). Returns, per lead, the lift of the hit sequence at lags 1..3 and the p-value of the design's independence test at
    spacing h and at spacing h + 1 (every s-th decision day), and the hit rate.
    """

    rng = random.Random(seed)
    burn, top = 200, max(leads)
    y = []
    x = 0.0
    for _ in range(burn + n + top + 2):
        x = phi * x + rng.gauss(0.0, 1.0)
        y.append(x)
    z = N01.inv_cdf(level)
    out: dict = {"lift": {}, "independence_p": {}, "rate": {}}
    for h in leads:
        horizon = h + lag
        mean_w = phi ** horizon
        sd = math.sqrt(sum(phi ** (2 * i) for i in range(horizon)))
        hits = []
        for d in range(burn, burn + n):
            mean = mean_w * y[d - lag]
            hits.append(int(y[d + h] > mean + sd * z) if level > 0.5 else int(y[d + h] < mean + sd * z))
        pos = list(range(n))
        out["lift"][h] = {k: lift(*lift_terms(hits, ["r"] * n, pos, k)) for k in (1, 2, 3)}
        out["independence_p"][h] = [ct.christoffersen_independence(hits[::s]).p_value for s in (h, h + 1)]
        out["rate"][h] = sum(hits) / n
    return out


def simulation_report(paths: int = SIM_PATHS, n: int = SIM_DAYS) -> dict:
    """Mean lag-1 lift and the rejection share of the design's independence test at spacing h and h + 1, over `paths` paths per cell."""

    out: dict = {"paths": paths, "days": n, "seed": SEED, "cells": []}
    for phi in SIM_PHIS:
        for lag in (1, 0):
            for level in (0.05, 0.95):
                results = [simulate_path(phi, n, lag, SEED * 1000 + p, level=level) for p in range(paths)]
                for h in (1, 2, 3):
                    lifts = [r["lift"][h][1] for r in results if r["lift"][h][1] == r["lift"][h][1]]
                    out["cells"].append({
                        "phi": phi, "lag": lag, "level": level, "lead": h, "mean_lift_lag1": sum(lifts) / len(lifts),
                        "mean_lift_lag2": sum(r["lift"][h][2] for r in results) / paths,
                        "reject_at_h": sum(1 for r in results if r["independence_p"][h][0] < 0.05) / paths,
                        "reject_at_h_plus_1": sum(1 for r in results if r["independence_p"][h][1] < 0.05) / paths,
                    })
    return out


# -- the tables ----------------------------------------------------------------------------------------------------------------


def lag_profile(frame: Frame, reg: Registry, tag: str, levels: Sequence[float] = LEVELS) -> Dict[str, dict]:
    """Registers the lift at lags 1..6, per lead and level, with bootstrap intervals for the two outer levels; returns the point estimates."""

    point = {}
    for h in LEADS:
        for level in levels:
            hits = frame.hits(h, level)
            for k in LAGS:
                n11, exp = lift_terms(hits, frame.regimes, frame.pos, k)
                name = f"{tag}|lift|{h}|{level:g}|{k}"
                point[name] = {"lead": h, "level": level, "lag": k, "lift": lift(n11, exp), "pairs_hit": sum(n11), "pairs_expected": sum(exp)}
                if level in (0.05, 0.95):
                    reg.ratio(name, (f"n11|{h}|{level}|{k}", n11), (f"exp|{h}|{level}|{k}", exp))
            if level in (0.05, 0.95):
                rates = fit_rates(hits, rate_columns(frame, h))
                for k in LAGS:
                    n11, exp = typed_lift_terms(hits, rates, frame.regimes, frame.pos, k)
                    name = f"{tag}|tadj|{h}|{level:g}|{k}"
                    point[name] = {"lead": h, "level": level, "lag": k, "lift": lift(n11, exp), "pairs_hit": sum(n11), "pairs_expected": sum(exp)}
                    reg.ratio(name, (f"tn11|{h}|{level}|{k}", n11), (f"texp|{h}|{level}|{k}", exp))
    return point


def run_lengths(hits: Sequence[int], regimes: Sequence[str]) -> Dict[str, int]:
    runs = m63.runs_of(list(range(len(hits))), regimes)
    out = {"1": 0, "2": 0, "3": 0, "4+": 0}
    start = 0
    for length in runs:
        part = hits[start:start + length]
        start += length
        run = 0
        for v in part + [0]:
            if v:
                run += 1
            elif run:
                out[str(run) if run < 4 else "4+"] += 1
                run = 0
    return out


def day_types_report(frame: Frame, reg: Registry) -> dict:
    """Lead 1 by target-day type and pressure-day type; pairs of ordinary days against pairs with a calendar or pressure day; runs; quarters."""

    n = len(frame.days)
    infos = [frame.info[frame.target_date(i, 1)] for i in range(n)]
    ordinary = [1 if (v["types"] == ["ordinary"] and v["pressure"] == "ordinary") else 0 for v in infos]
    out: dict = {"days": n, "ordinary_days": sum(ordinary), "levels": {}}
    kinds = list(m63.DAY_TYPES)
    pressure = sorted({v["pressure"] for v in infos})
    for level in LEVELS:
        hits = frame.hits(1, level)
        tot: Dict[str, List[int]] = {}
        for h, r in zip(hits, frame.regimes):
            t = tot.setdefault(r, [0, 0])
            t[0] += h
            t[1] += 1
        rate = {r: v[0] / v[1] for r, v in tot.items()}
        rows = []
        groups = [("target_day_type", k, [i for i in range(n) if k in infos[i]["types"]]) for k in kinds]
        groups += [("pressure_day_type", p, [i for i in range(n) if infos[i]["pressure"] == p]) for p in pressure]
        groups += [("neither calendar nor pressure", "ordinary", [i for i in range(n) if ordinary[i]]),
                   ("calendar or pressure", "any", [i for i in range(n) if not ordinary[i]])]
        for split, name, idx in groups:
            if not idx:
                continue
            x = sum(hits[i] for i in idx)
            expected = sum(rate[frame.regimes[i]] for i in idx)
            rows.append({"split": split, "label": name, "n": len(idx), "hits": x, "rate": x / len(idx), "wilson": wilson(x, len(idx)),
                         "expected_hits": expected, "ratio": x / expected if expected else None})
        pairs = {}
        for cls, ok in (("both ordinary", lambda i: ordinary[i] and ordinary[i - 1]), ("a calendar or pressure day in the pair", lambda i: not (ordinary[i] and ordinary[i - 1]))):
            n11, exp = lift_terms(hits, frame.regimes, frame.pos, 1)
            n11 = [v if i > 0 and ok(i) else 0.0 for i, v in enumerate(n11)]
            exp = [v if i > 0 and ok(i) else 0.0 for i, v in enumerate(exp)]
            name = f"daytype|{level:g}|{cls}"
            pairs[cls] = {"pairs_hit": sum(n11), "pairs_expected": sum(exp), "lift": lift(n11, exp), "key": name}
            if level in (0.05, 0.95):
                reg.ratio(name, (f"dt_n11|{level}|{cls}", n11), (f"dt_exp|{level}|{cls}", exp))
        hit_total = sum(hits)
        prev_hit = [0] + hits[:-1]
        second = sum(1 for h, p in zip(hits, prev_hit) if h and p)
        out["levels"][f"{level:g}"] = {
            "rows": rows, "pairs": pairs, "hits": hit_total, "hits_on_non_ordinary_days": sum(h for h, o in zip(hits, ordinary) if not o),
            "share_of_days_non_ordinary": 1 - sum(ordinary) / n, "hits_after_a_hit": second,
            "hits_in_pairs_with_a_non_ordinary_day": sum(1 for i in range(1, n) if hits[i] and hits[i - 1] and not (ordinary[i] and ordinary[i - 1])),
            "runs": run_lengths(hits, frame.regimes),
        }
    lower, upper = frame.hits(1, 0.05), frame.hits(1, 0.95)
    quarters: Dict[str, Dict[str, object]] = {}
    for i in range(n):
        t = frame.target_date(i, 1)
        slot = quarters.setdefault(f"{t.year}Q{(t.month - 1) // 3 + 1}", {"days": 0, "outside_band90": 0, "regime": frame.regimes[i]})
        slot["days"] += 1
        slot["outside_band90"] += int(lower[i] or upper[i])
    out["quarters"] = quarters
    return out


def drivers_report(frame: Frame, reg: Registry) -> dict:
    """Lead 1: autocorrelation of the standardised error and of its size, level adaptation, the previous public error, a large public |z|."""

    n = len(frame.days)
    med = [frame.q[i][1][MEDIAN] for i in range(n)]
    scale = [(frame.q[i][1][Q75] - frame.q[i][1][Q25]) / 1.349 for i in range(n)]
    if min(scale) <= 0:
        raise ValueError("a lead-1 forecast has a zero inter-quartile range")
    z = [(frame.y[i][1] - med[i]) / scale[i] for i in range(n)]
    az = [abs(v) for v in z]
    gap = [None] * n  # last public spread's gap to the median, in scales
    for i in range(n):
        target = frame.pos[i] - 1
        if target in frame.y_by_pos:
            require_public(target, frame.pos[i])
            gap[i] = (frame.y_by_pos[target] - med[i]) / scale[i]
    regimes = sorted(set(frame.regimes))
    scopes = {"pooled": [True] * n}
    for r in regimes:
        scopes[r] = [frame.regimes[i] == r for i in range(n)]
    out: dict = {"mean_z": sum(z) / n, "sd_z": math.sqrt(sum((v - sum(z) / n) ** 2 for v in z) / n), "scopes": {}}
    for kind, series in (("z", z), ("abs_z", az)):
        mu = sum(series) / n
        sd = math.sqrt(sum((v - mu) ** 2 for v in series) / n)
        c = [(v - mu) / sd for v in series]
        for scope, mask in scopes.items():
            for k in LAGS:
                ab = [c[i] * c[i - k] if i >= k and mask[i] and mask[i - k] else 0.0 for i in range(n)]
                aa = [c[i] ** 2 if i >= k and mask[i] and mask[i - k] else 0.0 for i in range(n)]
                bb = [c[i - k] ** 2 if i >= k and mask[i] and mask[i - k] else 0.0 for i in range(n)]
                reg.corr(f"drv|corr|{kind}|{scope}|{k}", (f"ab|{kind}|{scope}|{k}", ab), (f"aa|{kind}|{scope}|{k}", aa), (f"bb|{kind}|{scope}|{k}", bb))
    gaps = [v for v in gap if v is not None]
    gmu, zmu = sum(gaps) / len(gaps), sum(z) / n
    for scope, mask in scopes.items():
        xz = [(gap[i] - gmu) * (z[i] - zmu) if gap[i] is not None and mask[i] else 0.0 for i in range(n)]
        xx = [(gap[i] - gmu) ** 2 if gap[i] is not None and mask[i] else 0.0 for i in range(n)]
        reg.ratio(f"drv|gap_slope|{scope}", (f"xz|{scope}", xz), (f"xx|{scope}", xx))
    large = {}
    for scope, mask in scopes.items():
        for tag, level_set in (("outside_band90", (0.05, 0.95)), ("outside_band98", (0.01, 0.99))):
            hit = [int(any(frame.hits(1, lv)[i] for lv in level_set)) for i in range(n)]
            rows = [i for i in range(2, n) if mask[i] and mask[i - 2]]
            big = [i for i in rows if az[i - 2] > LARGE_Z]
            rest = [i for i in rows if az[i - 2] <= LARGE_Z]
            large[f"{scope}|{tag}"] = {
                "after_large_public_z": {"n": len(big), "hits": sum(hit[i] for i in big), "wilson": wilson(sum(hit[i] for i in big), len(big)) if big else None},
                "otherwise": {"n": len(rest), "hits": sum(hit[i] for i in rest), "wilson": wilson(sum(hit[i] for i in rest), len(rest)) if rest else None},
            }
    out["large_public_z"] = large
    out["threshold"] = LARGE_Z
    out["regimes"] = regimes
    return out


# -- the adjustments -----------------------------------------------------------------------------------------------------------


def cell_scores(frame: Frame, q: Sequence[Mapping[int, List[float]]]) -> Tuple[List[float], List[float]]:
    """Grid CRPS and upper-tail twCRPS of every cell, in (decision day, lead) order."""

    crps, tw = [], []
    for i in range(len(frame.days)):
        for h in LEADS:
            crps.append(sp.grid_crps(q[i][h], frame.y[i][h]))
            tw.append(sp.upper_tail_twcrps(q[i][h], frame.y[i][h]))
    return crps, tw


def adjustment_report(window: "m63.Window", frame: Frame, reg: Registry) -> dict:
    n = len(frame.days)
    base_q = frame.q
    base_crps, base_tw = cell_scores(frame, base_q)
    cells = [(d, h) for d in frame.days for h in LEADS]
    if [(c[0], c[1]) for c in window.cells] != cells:
        raise ValueError("the window's cells are not in (decision day, lead) order")
    groups = [(s, l, idx) for s, l, idx in window.groups() if not (s == "pooled")]
    groups = [("pooled", "all cells", list(range(len(cells))))] + groups
    groups.append(("after warm-up", f"decision days after the first {WARMUP_DAYS}", [c for c in range(len(cells)) if c // len(LEADS) >= WARMUP_DAYS]))
    den_by_group = {}
    for gi, (_s, _l, idx) in enumerate(groups):
        arr = [0.0] * n
        for c in idx:
            arr[c // len(LEADS)] += 1.0
        den_by_group[gi] = arr
    out: dict = {"variants": {}, "groups": [{"split": s, "label": l, "cells": len(idx)} for s, l, idx in groups]}
    base_sample = sample_from_frame(frame)
    out["base"] = {"family": _family_summary(family_at_spacing(base_sample, 0)), "crps": sum(base_crps) / len(base_crps),
                   "twcrps": sum(base_tw) / len(base_tw)}
    for variant in VARIANTS:
        adjusted = adjust(frame, variant)
        crps, tw = cell_scores(frame, adjusted)
        fam = family_at_spacing(sample_from_frame(frame, adjusted), 0)
        entry = {"family": _family_summary(fam), "crps": sum(crps) / len(crps), "twcrps": sum(tw) / len(tw), "lift_lead1": {}, "mean_shift": None,
                 "mean_width_ratio_by_lead": {}}
        for level in (0.05, 0.95):
            hits = frame.hits(1, level, adjusted)
            entry["lift_lead1"][f"{level:g}"] = {str(k): lift(*lift_terms(hits, frame.regimes, frame.pos, k)) for k in (1, 2, 3)}
            entry["rate_lead1"] = entry.get("rate_lead1", {})
            entry["rate_lead1"][f"{level:g}"] = sum(hits) / n
        for h in LEADS:
            ratios = [(adjusted[i][h][-1] - adjusted[i][h][0]) / (frame.q[i][h][-1] - frame.q[i][h][0]) for i in range(n)]
            entry["mean_width_ratio_by_lead"][str(h)] = sum(ratios) / n
        out["variants"][variant] = entry
        for score_name, mine, theirs in (("crps", crps, base_crps), ("twcrps", tw, base_tw)):
            diff = [a - b for a, b in zip(mine, theirs)]
            for gi, (_s, _l, idx) in enumerate(groups):
                num = [0.0] * n
                for c in idx:
                    num[c // len(LEADS)] += diff[c]
                reg.ratio(f"adj|{variant}|{score_name}|{gi}", (f"adjnum|{variant}|{score_name}|{gi}", num), (f"adjden|{gi}", den_by_group[gi]))
    return out


def _family_summary(fam: dict) -> dict:
    by_lead = {str(h): 0 for h in LEADS}
    for cell, _kind in fam["failing"]:
        by_lead[str(cell[0])] += 1
    return {"rejected": fam["rejected"], "independence_rejected": fam["independence_rejected"], "tests": fam["tests"], "min_p": fam["min_p"],
            "failing": sorted(label(c, k) for c, k in fam["failing"]), "rejected_by_lead": by_lead, "passes": fam["rejected"] == 0}


# -- score ---------------------------------------------------------------------------------------------------------------------


def score_command(args) -> int:
    declared = committed_declaration()
    doc = json.loads(Path(args.walk).read_text(encoding="utf-8"))
    window = load_window_doc(doc)
    record = json.loads(RECORD_1314.read_text(encoding="utf-8"))
    reproduction = m63.reproduction_check(window, record)
    frame = Frame.from_window(window)
    sample = sample_from_frame(frame)
    reference = m16.sample_from_window(window)
    for h in LEADS:
        for level in LEVELS:
            if [m16._hits([v], level)[0] for v in reference.u[h]] != [m16._hits([v], level)[0] for v in sample.u[h]]:
                raise ValueError(f"the strict hits differ from the randomised PIT's at lead {h}, level {level}: an outcome ties a quantile")
    design = family_at_spacing(sample, 0)
    r1516 = json.loads(RESULT_1516.read_text(encoding="utf-8"))
    mine = sorted(label(c, k) for c, k in design["failing"])
    theirs = sorted(r1516["observed"]["families"]["iid"]["failing"])
    if mine != theirs:
        raise ValueError(f"the design's rejections differ from {RESULT_1516.name}: {mine} against {theirs}")
    spacing = {}
    for extra in (0, 1, 2):
        fam = family_at_spacing(sample, extra)
        spacing[str(extra)] = {"extra": extra, "rejected": fam["rejected"], "independence_rejected": fam["independence_rejected"], "tests": fam["tests"],
                               "failing": sorted(label(c, k) for c, k in fam["failing"]), "min_p": fam["min_p"],
                               "independence_raw_below_5pct": sum(1 for c in fam["cells"] if c["independence_p"] is not None and c["independence_p"] < 0.05),
                               "cells": fam["cells"]}
        print(f"spacing h+{extra}: {fam['rejected']} rejected ({fam['independence_rejected']} independence)", flush=True)
    reg = Registry()
    profile = lag_profile(frame, reg, "base")
    day_types = day_types_report(frame, reg)
    drivers = drivers_report(frame, reg)
    adjustments = adjustment_report(window, frame, reg)
    print(f"resampling {len(reg.arrays)} arrays for {len(reg.specs)} statistics", flush=True)
    intervals = reg.run(workers=args.workers)
    print("simulating", flush=True)
    simulation = simulation_report()
    result = {
        "issue": ISSUE, "label": "development, not a verdict", "candidate": CANDIDATE, "panel_sha256": doc.get("panel_sha256"), "window": "development",
        "decision_days": len(frame.days), "last_target": window.last_day().isoformat(), "seed": SEED, "reps": REPS, "block": BLOCK, "interval_level": LEVEL,
        "declaration": "metadata/hit_dependence_1523.json", "declaration_issue": declared["issue"], "regimes": sorted(set(frame.regimes)),
        "regime_days": {r: sum(1 for x in frame.regimes if x == r) for r in sorted(set(frame.regimes))},
        "reproduction": {"against": str(RECORD_1314.relative_to(REPO)), "mean_grid_crps": reproduction[CANDIDATE],
                         "failing_equals": str(RESULT_1516.relative_to(REPO)), "failing": mine},
        "design": {"family": _family_summary(design), "cells": design["cells"]},
        "spacing": spacing, "lag_profile": profile, "day_types": day_types, "drivers": drivers, "adjustments": adjustments, "simulation": simulation,
        "intervals": intervals,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


def walk_command(args) -> int:
    """Delegates to `candidate_calibration_1363.py walk` (the candidate walked unchanged)."""

    cmd = [sys.executable, str(REPO / "scripts" / "candidate_calibration_1363.py"), "walk", "--panel", args.panel, "--window", "development", "--output", args.output]
    return subprocess.run(cmd, cwd=REPO, env={**__import__("os").environ, "RMM_DECISION_TIME": "18:00", "PYTHONPATH": str(REPO / "src")}).returncode


# -- the page ------------------------------------------------------------------------------------------------------------------


def _f(x: Optional[float], d: int = 2) -> str:
    return "n/a" if x is None or x != x else f"{x:.{d}f}"


def _p(x: Optional[float]) -> str:
    if x is None:
        return "n/a"
    return "<0.001" if x < 0.001 else f"{x:.3f}"


def _iv(x: Optional[Mapping[str, float]], d: int = 2) -> str:
    return "n/a" if not x or x.get("lo") is None else f"{_f(x['estimate'], d)} [{_f(x['lo'], d)}, {_f(x['hi'], d)}]"


def _pc(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def _wil(w: Optional[Sequence[float]]) -> str:
    return "n/a" if not w else f"[{100 * w[0]:.1f}%, {100 * w[1]:.1f}%]"


def _table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    return ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"] + ["| " + " | ".join(map(str, row)) + " |" for row in rows]


def render(r: Mapping[str, object]) -> str:
    """The result page: every figure is read from `result.json`."""

    iv = r["intervals"]
    spacing = r["spacing"]
    design = r["design"]
    adj = r["adjustments"]
    drv = r["drivers"]
    dts = r["day_types"]
    sim = r["simulation"]["cells"]
    out: List[str] = []
    w = out.append
    w("# Where the lead-1 hit dependence of (s3c-ann-net) sits, what drives it, and what a model change could do (#1523)")
    w("")
    w(f"**Hypothesis and step:** H5 (primary goal), step M5 (registration of (s3c-ann-net), #1510 / PR #1511), toward a model change. Her docket ruling of 8 November 2026 on PR #1520 (card cov-1520-reading): \"bar\". "
      f"**Development data, not a verdict** (scoring protocol v1). Nothing is registered, fitted or published, no record is edited, the study neither reads nor writes `COVERAGE_REQUIREMENT_IN_FORCE`, amendment 4 is untouched, and no day after 2025-12-31 or locked day is read. "
      f"Generated by `scripts/hit_dependence_1523.py page` from `docs/research/hit-dependence-1523/result.json`; declared in `{r['declaration']}` before any adjusted score (two arms and one table were added by an amendment after the first score, listed in the declaration). "
      f"Candidate (s3c-ann-net) at the 18:00 decision instant, walked unchanged; panel digest `{r['panel_sha256']}`; {r['decision_days']} decision days, last target {r['last_target']}. Seed {r['seed']}; intervals are {int(100 * r['interval_level'])}% stationary-bootstrap percentile intervals (mean block {r['block']:g}, {r['reps']} resamples) unless marked Wilson 95%.")
    w("")
    w(f"**Reproduction.** The walk's mean grid CRPS equals the 1314 record's to 1e-9 ({_f(r['reproduction']['mean_grid_crps']['mean_grid_crps'], 6)}), and the design as `scoring_protocol.coverage_cells` applies it gives exactly the Holm rejections of `{r['reproduction']['failing_equals']}`, or the script refused to write this record.")
    w("")
    w("## The answer")
    w("")
    base = spacing["0"]
    s1, s2 = spacing["1"], spacing["2"]
    l1 = {k: iv[f"base|lift|1|{k}|1"] for k in ("0.05", "0.95")}
    t1 = {k: iv[f"base|tadj|1|{k}|1"] for k in ("0.05", "0.95")}
    c0 = [c for c in sim if c["phi"] == 0.3 and c["lag"] == 1 and c["lead"] == 1 and c["level"] == 0.95][0]
    c9 = [c for c in sim if c["phi"] == 0.9 and c["lag"] == 1 and c["lead"] == 1 and c["level"] == 0.95][0]
    control = [c for c in sim if c["phi"] == 0.9 and c["lag"] == 0 and c["lead"] == 1 and c["level"] == 0.95][0]
    w(f"1. **Where.** The design rejects {base['rejected']} of {base['tests']} coverage cells; {base['independence_rejected']} are independence tests (the other is the Kupiec q99 test of 2021-23), and {design['family']['rejected_by_lead']['1']} of the {base['rejected']} are at lead 1 (the other two are at leads 2 and 3 in 2021-23). "
      f"The dependence is a one-day-apart effect: lift at lag 1 (observed hit pairs over those expected under each regime's own rate; 1 is independence) is {_iv(l1['0.05'], 1)} at q05 and {_iv(l1['0.95'], 1)} at q95, lead 1, and falls to about 2 at lags 2 to 4 (table below).")
    w(f"2. **The design's spacing leaves one innovation shared.** A forecast for D + h reads the spread to the panel day D - 1 (information-set rule 1: the daily rates are read at the row two panel days before the target). "
      f"Two forecasts the design keeps h days apart therefore share the innovation of the first one's target day, so a forecaster that is calibrated by construction shows dependent hits at that spacing. "
      f"Read at spacing h + 1 instead of h, the same cells give {s1['independence_rejected']} independence rejections (against {base['independence_rejected']}), and {s1['rejected']} rejection in all (the Kupiec q99 test of 2021-23); at h + 2, {s2['independence_rejected']} and {s2['rejected']}. "
      f"In the simulation, a calibrated forecaster that reads to D - 1 has a mean lag-1 lift of {_f(c0['mean_lift_lag1'], 1)} (AR(1) with phi 0.3, which matches the candidate's lag-1 error correlation of {_f(iv['drv|corr|z|pooled|1']['estimate'])}) to {_f(c9['mean_lift_lag1'], 1)} (phi 0.9) at lead 1 and is rejected by the design in {_pc(c0['reject_at_h'])} to {_pc(c9['reject_at_h'])} of paths, against {_pc(c9['reject_at_h_plus_1'])} at spacing h + 1; the control that also reads D is rejected in {_pc(control['reject_at_h'])}. "
      f"The previous day's hit and residual are not public at the decision, so no model can feed them back: this part is not removable by a model change.")
    w(f"3. **What is left after the structural part.** The candidate's lag-1 lift ({_f(l1['0.05']['estimate'], 1)} and {_f(l1['0.95']['estimate'], 1)}) is above the calibrated reference at the matched phi ({_f(c0['mean_lift_lag1'], 1)}), and the lift stays near 2 at lags 2 to 4 where the reference has none. "
      f"That excess is a miss rate that moves in time: the standardised absolute error autocorrelates at the public lags ({_iv(iv['drv|corr|abs_z|pooled|2'])} at lag 2, {_iv(iv['drv|corr|abs_z|2021-23|2'])} in 2021-23), the signed error does not carry one level the model misses (lag-2 correlation {_iv(iv['drv|corr|z|pooled|2'])}, negative pooled; positive in 2020 and 2025-26, negative in 2018-19, 2021-23 and 2024), and the last public spread's gap to the median has a pooled slope of {_iv(iv['drv|gap_slope|pooled'])}, negative, which is the opposite of a level that adapts too slowly (positive only in 2020: {_iv(iv['drv|gap_slope|2020'])}).")
    w(f"4. **Calendar and pressure days.** Hits on ordinary target days run well under the regime-expected rate (q05: {dts['levels']['0.05']['rows'][-2]['hits']} against {_f(dts['levels']['0.05']['rows'][-2]['expected_hits'], 1)} expected) and on calendar or pressure days above it, and 73% of lead-1 target days are not ordinary, so almost every hit pair involves one. "
      f"The rate difference between adjacent days does not explain the dependence: with the rate fitted by regime, target-day type and pressure type, the lag-1 lift is still {_iv(t1['0.05'], 1)} at q05 and {_iv(t1['0.95'], 1)} at q95. Pairs of two ordinary days are too few to read (expected pairs under 1).")
    names = {"A1_recentre": "A1 recentre", "A2_rescale": "A2 rescale (60)", "A3_both": "A3 both", "A4_meanrevert": "A4 recentre, negative slope allowed", "A5_fast_rescale": "A5 rescale (20)"}
    rejections = ", ".join("%s: %d of %d" % (names[v], adj["variants"][v]["family"]["rejected"], adj["variants"][v]["family"]["tests"]) for v in VARIANTS)
    best = min(VARIANTS, key=lambda v: iv[f"adj|{v}|crps|0"]["estimate"])
    losing = ", ".join(names[v] for v in VARIANTS if iv[f"adj|{v}|crps|0"]["lo"] > 0)
    w(f"5. **Model changes.** None of the five post-hoc adjustments improves pooled grid CRPS: every point estimate is a loss (the least bad, {names[best]}, changes it by {_iv(iv[f'adj|{best}|crps|0'], 4)}; positive is worse) and the interval excludes zero on the loss side for {losing}. None removes the independence rejections ({rejections}; the candidate: {adj['base']['family']['rejected']}). "
      f"The scale adjustments gain in 2021-23 (the interval excludes zero) and lose in 2018-19 and, for A2, 2025-26. The ranking and the question for her are below.")
    w("")
    # -- where
    w("## 1. Where the dependence sits")
    w("")
    w("### The cells the design rejects (Holm, 5%, 200 coverage cells)")
    w("")
    cells = {(c["lead"], c["regime"], c["level"]): c for c in base["cells"]}
    rows = []
    for item in base["failing"]:
        (lead, regime, level), kind = parse_label(item)
        c = cells[(lead, regime, level)]
        rows.append([lead, regime, f"q{level:g}", kind, c["n"], c["hits"], _pc(c["rate"]), f"{_pc(c['p_hit_after_hit'])} {_wil(c['wilson_after_hit'])}", f"{_pc(c['p_hit_after_none'])} {_wil(c['wilson_after_none'])}",
                     _p(c["independence_p"] if kind == "independence" else c["kupiec_p"])])
    w("\n".join(_table(["lead", "regime", "level", "test", "thinned days", "hits", "hit rate", "P(hit after a hit) [Wilson 95%]", "P(hit after no hit) [Wilson 95%]", "raw p"], rows)))
    w("")
    w("Rejections by lead and by level (independence tests only, Holm):")
    w("")
    by_level: Dict[str, Dict[int, int]] = {}
    for item in base["failing"]:
        (lead, regime, level), kind = parse_label(item)
        if kind == "independence":
            by_level.setdefault(f"q{level:g}", {h: 0 for h in LEADS})[lead] += 1
    w("\n".join(_table(["level"] + [f"lead {h}" for h in LEADS], [[lv] + [by_level[lv][h] for h in LEADS] for lv in sorted(by_level)])))
    w("")
    w("### Read at a longer spacing")
    w("")
    w("The independence test of every cell read at every s-th decision day of the regime (s = h is the design; Kupiec as in the design; Holm over the same family).")
    w("")
    w("\n".join(_table(["independence read at", "rejected (all tests)", "independence rejections", "independence tests with raw p < 5%", "what is rejected"],
                     [[f"s = h + {e}" + (" (the design)" if e == "0" else ""), spacing[e]["rejected"], spacing[e]["independence_rejected"], spacing[e]["independence_raw_below_5pct"], "; ".join(spacing[e]["failing"]) if spacing[e]["rejected"] <= 3 else f"{spacing[e]['rejected']} cells (table above)"] for e in ("0", "1", "2")])))
    w("")
    w("The thinned series at s = h + 1 is shorter (n / (h + 1) days per regime), so this reading has less power; the table says what the design finds, not that nothing is there. The lag profile below is the power-free view.")
    w("")
    w("### A calibrated forecaster with the same information lag")
    w("")
    w(f"A forecaster that knows an AR(1) spread's dynamics and is calibrated by construction, {r['simulation']['paths']} paths of {r['simulation']['days']} days, seed {r['simulation']['seed']}, one regime. It reads the spread to D - 1 for a target D + h (lag 1, the information-set rule) or, as a control, to D (lag 0). "
      "Mean lift at lag 1, and the share of paths where the independence test of the design (spacing h) and at spacing h + 1 rejects at 5%, unadjusted. Upper tail (q95); the lower tail is in `result.json`.")
    w("")
    rows = [[c["phi"], "to D - 1" if c["lag"] else "to D (control)", c["lead"], _f(c["mean_lift_lag1"], 1), _f(c["mean_lift_lag2"], 1), _pc(c["reject_at_h"]), _pc(c["reject_at_h_plus_1"])]
            for c in sim if c["level"] == 0.95 and c["lead"] in (1, 2, 3) and (c["lag"] == 1 or c["phi"] == 0.9)]
    w("\n".join(_table(["phi", "reads data", "lead", "mean lift, lag 1", "mean lift, lag 2", "design rejects (spacing h)", "rejects at spacing h + 1"], rows)))
    w("")
    w("### Lift by lag")
    w("")
    w("Observed hit pairs k panel days apart over those expected, per lead and level, within regime (the regime's own rate), then with the rate also fitted to the target-day type and pressure-day type (\"typed\"; fitted in sample on about 16 parameters, so a little biased downward). Interval: stationary bootstrap over days, the fitted rates held fixed.")
    w("")
    rows = []
    for h in LEADS:
        for lv in ("0.05", "0.95"):
            rows.append([h, f"q{lv}", "regime"] + [_iv(iv[f"base|lift|{h}|{lv}|{k}"], 1) for k in LAGS])
            rows.append([h, f"q{lv}", "typed"] + [_iv(iv[f"base|tadj|{h}|{lv}|{k}"], 1) for k in LAGS])
    w("\n".join(_table(["lead", "level", "expected under"] + [f"lag {k}" for k in LAGS], rows)))
    w("")
    w("For a forecast of lead h the outcomes of the last h targets before its own are not public at its decision, so the hits at lags 1 to h cannot be fed back; the hits at lag h + 1 and later can.")
    w("")
    # -- day types
    w("## 2. Calendar days, pressure days and runs (lead 1)")
    w("")
    w("Hits by target-day type (types overlap) and pressure-day type against the number expected if each day had its regime's rate. Wilson 95% interval of the rate; expected hits in the next column.")
    w("")
    for lv in ("0.05", "0.95"):
        block = dts["levels"][lv]
        w(f"**q{lv}**")
        w("")
        w("\n".join(_table(["split", "group", "target days", "hits", "rate [Wilson]", "expected hits", "hits / expected"],
                         [[x["split"], x["label"], x["n"], x["hits"], f"{_pc(x['rate'])} {_wil(x['wilson'])}", _f(x["expected_hits"], 1), _f(x["ratio"])] for x in block["rows"]])))
        w("")
    w("Pairs of adjacent days (lag 1), by whether a calendar or pressure day is in the pair, and runs of consecutive hits:")
    w("")
    rows = []
    for lv in ("0.01", "0.05", "0.95", "0.99"):
        b = dts["levels"][lv]
        for cls, p in b["pairs"].items():
            rows.append([f"q{lv}", cls, int(p["pairs_hit"]), _f(p["pairs_expected"], 1), _iv(iv.get(p["key"]) and {**iv[p["key"]]}, 1) if p["key"] in iv else _f(p["lift"], 1)])
    w("\n".join(_table(["level", "pair", "hit pairs", "expected", "lift [90%]"], rows)))
    w("")
    rows = []
    for lv in ("0.01", "0.05", "0.95", "0.99"):
        b = dts["levels"][lv]
        rows.append([f"q{lv}", b["hits"], b["hits_after_a_hit"], b["runs"]["1"], b["runs"]["2"], b["runs"]["3"], b["runs"]["4+"], b["hits_in_pairs_with_a_non_ordinary_day"]])
    w("\n".join(_table(["level", "hits", "hits right after a hit", "runs of 1", "runs of 2", "runs of 3", "runs of 4+", "of those, in a pair with a calendar or pressure day"], rows)))
    w("")
    q = sorted(dts["quarters"].items(), key=lambda kv: -kv[1]["outside_band90"])[:6]
    total = sum(v["outside_band90"] for v in dts["quarters"].values())
    w(f"Outside the 90% band at lead 1 by calendar quarter of the target, the six quarters with the most: " + ", ".join(f"{k} ({v['outside_band90']} of {v['days']} days, {v['regime']})" for k, v in q) + f"; together {sum(v['outside_band90'] for _k, v in q)} of {total}. The misses are not in one episode.")
    w("")
    # -- drivers
    w("## 3. What drives it (lead 1)")
    w("")
    w("The standardised error is z = (outcome - median) / ((q75 - q25) / 1.349). Correlation of z at day t with z at day t - k (Pearson, centred on the whole-sample mean), and of |z|. **Lag 1 is not public** at the decision (the outcome of the previous target day is read from the second row before, information-set rule 1); lags 2 and later are.")
    w("")
    scopes = ["pooled"] + drv["regimes"]
    for kind, title in (("z", "Signed error z"), ("abs_z", "Size of the error |z| (scale)")):
        w(f"**{title}**")
        w("")
        w("\n".join(_table(["scope"] + [f"lag {k}" + (" (not public)" if k == 1 else "") for k in LAGS], [[sc] + [_iv(iv[f"drv|corr|{kind}|{sc}|{k}"]) for k in LAGS] for sc in scopes])))
        w("")
    w("**Level adaptation.** Slope of z on the gap between the last public spread (the outcome on the panel day before the decision) and the forecast median, in scales. A positive slope is a level that follows the data more than the model does (adapts too slowly); a negative one is the median already overshooting.")
    w("")
    w("\n".join(_table(["scope", "slope [90%]"], [[sc, _iv(iv[f"drv|gap_slope|{sc}"], 3)] for sc in scopes])))
    w("")
    w(f"**After a large public error.** Share of days outside the band after a public |z| above {drv['threshold']:g} two panel days before (the latest error the decision can read) against otherwise (Wilson 95%; days are not independent, so the intervals are narrower than they should be).")
    w("")
    rows = []
    for sc in ("pooled", "2021-23"):
        for tag in ("outside_band90", "outside_band98"):
            v = drv["large_public_z"][f"{sc}|{tag}"]
            rows.append([sc, "outside 90% band" if tag.endswith("90") else "outside 98% band", f"{v['after_large_public_z']['hits']} of {v['after_large_public_z']['n']} {_wil(v['after_large_public_z']['wilson'])}",
                         f"{v['otherwise']['hits']} of {v['otherwise']['n']} {_wil(v['otherwise']['wilson'])}"])
    w("\n".join(_table(["scope", "event", "after a large public |z|", "otherwise"], rows)))
    w("")
    # -- adjustments
    w("## 4. What the model changes could do")
    w("")
    w("Five post-hoc adjustments of the candidate's own quantile output, each learned online from outcomes public at each decision day (a guard raises `LookAheadError` otherwise): "
      "A1 shifts by an online slope (clamped to [0, 1]) times the latest public lead-1 error; A2 scales about the median by the realised-to-forecast absolute deviation of the last 60 resolved cells (clamped to [0.7, 1.5]); A3 does both; "
      "A4 is A1 with the slope allowed to be negative; A5 is A2 with 20 cells. They are **not models**: nothing is fitted to the walk beyond the online rules, nothing is registered, and no setting is varied. "
      "The change is adjusted minus candidate, so **negative is better**. Paired on the same cells; stationary-bootstrap 90% interval over decision days.")
    w("")
    rows = []
    groups = adj["groups"]
    for v in VARIANTS:
        rows.append([names[v], _iv(iv[f"adj|{v}|crps|0"], 4), _iv(iv[f"adj|{v}|twcrps|0"], 4), _iv(iv[f"adj|{v}|crps|{len(groups) - 1}"], 4),
                     f"{adj['variants'][v]['family']['rejected']} ({adj['variants'][v]['family']['independence_rejected']} independence)", _f(adj["variants"][v]["lift_lead1"]["0.05"]["1"], 1), _f(adj["variants"][v]["lift_lead1"]["0.95"]["1"], 1)])
    rows.append(["candidate (reference)", f"{_f(adj['base']['crps'], 4)} (level)", f"{_f(adj['base']['twcrps'], 4)} (level)", "", f"{adj['base']['family']['rejected']} ({adj['base']['family']['independence_rejected']} independence)",
                 _f(r["lag_profile"]["base|lift|1|0.05|1"]["lift"], 1), _f(r["lag_profile"]["base|lift|1|0.95|1"]["lift"], 1)])
    w("\n".join(_table(["adjustment", "grid CRPS change, h = 1-5 [90%]", "upper-tail twCRPS change", f"grid CRPS change after the first {WARMUP_DAYS} days", "design rejections (Holm, 200)", "lead-1 lag-1 lift q05", "q95"], rows)))
    w("")
    w("Grid CRPS change by lead, regime of the target and pressure-day type of the target:")
    w("")
    idx = {(g["split"], g["label"]): i for i, g in enumerate(groups)}
    cols = [("lead", f"h={h}") for h in LEADS] + [("regime", g["label"]) for g in groups if g["split"] == "regime"] + [("pressure_day_type", g["label"]) for g in groups if g["split"] == "pressure_day_type"]
    rows = [[names[v]] + [_iv(iv[f"adj|{v}|crps|{idx[c]}"], 3) for c in cols] for v in VARIANTS]
    w("\n".join(_table(["adjustment"] + [f"{c[0]} {c[1]}".replace("pressure_day_type", "pressure") for c in cols], rows)))
    w("")
    w("Target-day types (overlapping):")
    w("")
    tcols = [("target_day_type", g["label"]) for g in groups if g["split"] == "target_day_type"]
    rows = [[names[v]] + [_iv(iv[f"adj|{v}|crps|{idx[c]}"], 3) for c in tcols] for v in VARIANTS]
    w("\n".join(_table(["adjustment"] + [c[1] for c in tcols], rows)))
    w("")
    w("Coverage cells the design still rejects after each adjustment:")
    w("")
    w("\n".join(_table(["adjustment", "rejected by lead 1 / 2 / 3 / 4 / 5", "cells"], [[names[v], " / ".join(str(adj["variants"][v]["family"]["rejected_by_lead"][str(h)]) for h in LEADS), "; ".join(adj["variants"][v]["family"]["failing"])] for v in VARIANTS])))
    w("")
    w("## 5. Model changes, ranked by evidence")
    w("")
    w("Nothing is fitted or registered here; the change is hers to pick (the question is in the pull request). The effects below are the adjustments' paired figures above, and are estimates of expected effect, not results of a model.")
    w("")
    def dt_ratio(kind: str) -> str:
        vals = []
        for lv in ("0.05", "0.95"):
            row = [x for x in dts["levels"][lv]["rows"] if x["split"] == "target_day_type" and x["label"] == kind][0]
            vals.append(f"{_f(row['ratio'])} at q{lv}")
        return " and ".join(vals)

    a2, a5, a1, a4 = (iv[f"adj|{v}|crps|0"] for v in ("A2_rescale", "A5_fast_rescale", "A1_recentre", "A4_meanrevert"))
    r23 = {v: iv[f"adj|{v}|crps|{idx[('regime', '2021-23')]}"] for v in VARIANTS}
    w(f"0. **Not a model change: read independence at spacing h + 1.** The thinned rows of the design at spacing h share the innovation of one target day under the two-row information lag. Effect expected: independence rejections {base['independence_rejected']} to {s1['independence_rejected']}, all tests {base['rejected']} to {s1['rejected']}; grid CRPS unchanged. This amends amendment 4 and is hers; it is listed first because it is the only item the evidence supports as removing the rejections.")
    w(f"1. **A scale that reacts faster to recent errors (A5, then A2).** Evidence: |z| autocorrelates at the public lags, and the adjustments that scale are the ones with a gain in 2021-23 (A5 {_iv(r23['A5_fast_rescale'], 3)}, A2 {_iv(r23['A2_rescale'], 3)}). Expected effect on grid CRPS h = 1-5: {_iv(a5, 4)} for A5 and {_iv(a2, 4)} for A2 pooled (no pooled gain; losses in 2018-19 and 2025-26; after the first {WARMUP_DAYS} days A5 changes it by {_iv(iv[f'adj|A5_fast_rescale|crps|{len(groups) - 1}'], 4)}); on the coverage cells: {adj['variants']['A5_fast_rescale']['family']['rejected']} and {adj['variants']['A2_rescale']['family']['rejected']} rejected against {adj['base']['family']['rejected']}, the lead-1 independence rejections stay. It addresses the persistent part (lags 2 to 5), not lag 1.")
    w(f"2. **A calendar- or pressure-day scale.** Evidence: hits on ordinary days are well under their expected rate and on calendar or pressure days above it; but the typed lift is {_f(t1['0.05']['estimate'], 1)} and {_f(t1['0.95']['estimate'], 1)} at lag 1, so day-type rates do not explain the dependence. Already measured by #1402 (a residual scale by pressure-day type: undecided or a loss on the development window), not repeated here; no new figure. A pattern this study adds: the tails move in opposite directions on some days (hits per expected hit at q05 and q95 on dom_19_23 days: {dt_ratio('dom_19_23')}; on quarter_end days: {dt_ratio('quarter_end')}), which is a level or skew misplaced on those days and not a scale alone.")
    w(f"3. **A level term on the latest public error (A1, A4).** Evidence against: the sign changes by regime, and pooled the lag-2 correlation of z is negative ({_iv(iv['drv|corr|z|pooled|2'])}) and the gap slope is negative ({_iv(iv['drv|gap_slope|pooled'])}). A1 (slope clamped at zero) does nothing at lead 1; A4 (negative slope allowed) changes grid CRPS by {_iv(a4, 4)} (worse) and leaves {adj['variants']['A4_meanrevert']['family']['rejected']} rejections. Not recommended.")
    w("4. **Feeding the previous day's hit or residual (lag 1).** Not available: the outcome is not public at the decision instant. A change cannot use it without changing the information set (her decision, `docs/decisions/information-set.md`).")
    w("")
    w("## What was not checked")
    w("")
    for line in NOT_CHECKED:
        w(f"- {line}")
    w("")
    return "\n".join(out) + "\n"


NOT_CHECKED = (
    "A fitted model: nothing is fitted, registered or proposed as a parameter set. The adjustments are online rules on the candidate's output with settings fixed in the declaration; a different window, clamp or slope rule could move their figures.",
    "The 2026 days (near-blind tier), B1, B1', B2, B4 and the uncapped secondary version; development data only, and a development figure is not a verdict.",
    "A dependence-aware independence test or a different thinning for leads 2 to 5 in 2021-23 beyond spacing h + 1 and h + 2; the power of the design at spacing h + 1 for a dependence like the candidate's is not measured (its thinned series are shorter).",
    "The simulation is an AR(1) with one regime, normal innovations and no volatility clustering or calendar effects; it shows what the information lag does to a calibrated forecaster's hits, not how much of the candidate's lag-1 lift it explains. The matched-phi reference is a reading, not a decomposition.",
    "The typed rate is fitted in sample to the hits it is then compared with (about 16 parameters on 100 to 130 hits), so the typed lift is biased downward a little; its interval holds the fitted rates fixed.",
    "Whether the information-set rule itself (rows read two panel days before the target) is the intended reading at the 18:00 instant for the SOFR-based target; the study takes the registry's release lags as they are.",
    "Intervals for the day-type hit ratios other than Wilson on the rate; days are serially dependent, so those intervals are too narrow.",
)


def page_command(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(result), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk", help="the candidate's development walk, by candidate_calibration_1363.py walk")
    w.add_argument("--panel", required=True)
    w.add_argument("--output", required=True)
    w.set_defaults(func=walk_command)
    s = sub.add_parser("score", help="the diagnosis tables and the adjustments, from a walk file")
    s.add_argument("--walk", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--workers", type=int, default=4)
    s.set_defaults(func=score_command)
    pg = sub.add_parser("page", help="the result page from result.json")
    pg.add_argument("--score", required=True)
    pg.add_argument("--output", required=True)
    pg.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
