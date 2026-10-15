#!/usr/bin/env python3
"""Power by empirical replay and three test families (H1 step 3, #754).

The rule it follows is `docs/research/power-replay-754.md`, committed before this script produced any number.
Development data only: no day after 2025-12-31 (`STUDY_END`) is read, and nothing here is a verdict.

    PYTHONPATH=src python3 scripts/power_replay.py describe
    PYTHONPATH=src python3 scripts/power_replay.py run --out docs/research/power-replay-754 [--workers K]
    PYTHONPATH=src python3 scripts/power_replay.py report --out docs/research/power-replay-754
    PYTHONPATH=src python3 scripts/power_replay.py check --out docs/research/power-replay-754

`run` builds the published pool of the confirmation-design study (`scripts/confirmation_design.py`), replays windows
over real forecast pairs and over known-equal series, simulates the same families on bootstrap paths, and writes
`result.json`. `report` writes the result page from `result.json` alone, so no figure on the page is typed. `check`
refuses a `result.json` made from another text of the rule. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing
import random
import sys
import tempfile
from dataclasses import dataclass
from statistics import NormalDist
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

_spec = importlib.util.spec_from_file_location("confirmation_design_for_replay", REPO / "scripts" / "confirmation_design.py")
cd = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = cd
_spec.loader.exec_module(cd)

RULE = REPO / "docs" / "research" / "power-replay-754.md"
PAGE = REPO / "docs" / "research" / "power-replay-754-result.md"

# The rule's constants (§3 to §6).
STUDY_END = cd.STUDY_END
WINDOW_LENGTHS = (60, 125, 250)
SYNTHETIC_LENGTHS = (60, 125, 250, 500)
STEP = 5
FLIP_BLOCK = 20
DM_RATIO = 0.1
WINDOWS = 20_000
PATHS = 2_000
SEED = 754
CALIBRATION_SEED = 1
INTERVAL_DRAWS = 1_000
FULL_DELTAS = (0.0, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50)
OTHER_DELTAS = (0.0, 0.03, 0.10)
TARGET_POWER = 0.80
SIZE_LIMIT = 0.05
FAMILIES = ("a1", "a2", "b", "c1", "c5")
CANDIDATE_FAMILIES = ("a2", "b", "c1")
REGIMES = ("2018-19", "2020-24", "2025")
DAY_CELLS = ("all", "ordinary", "pressure")
KINDS = ("real", "E1", "E2", "E3")
PAIRS = ("P2", "P2r", "P3")
LAMBDA_CAP = 0.5
LAMBDA_PRIOR = 0.25


class RuleError(ValueError):
    """The study was asked for something its rule does not say."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# -- the guard (§2) --------------------------------------------------------------------------------------------------


def require_study_window(days) -> None:
    """§2: the study reads no day after `STUDY_END`.

    Raises:
        LookAheadError: a day is later than `STUDY_END`.
    """

    late = sorted(day for day in days if day > STUDY_END)
    if late:
        raise LookAheadError(f"the power-replay study reads no day after {STUDY_END}; got {late[0]}")


def regime_of(when: date) -> str:
    if when.year < 2020:
        return "2018-19"
    return "2020-24" if when.year < 2025 else "2025"


# -- the series (§3) -------------------------------------------------------------------------------------------------


@dataclass
class Cell:
    """A score series: `d` is S(B1) - S(candidate) and `b` is S(B1), the mean over leads 1 to 5; `d1`, `b1` are lead 1."""

    dates: List[date]
    d: List[float]
    b: List[float]
    d1: List[float]
    b1: List[float]

    def subset(self, keep: Sequence[bool]) -> "Cell":
        pick = [i for i, flag in enumerate(keep) if flag]
        return Cell([self.dates[i] for i in pick], [self.d[i] for i in pick], [self.b[i] for i in pick],
                    [self.d1[i] for i in pick], [self.b1[i] for i in pick])


def demean(values: Sequence[float]) -> List[float]:
    centre = sum(values) / len(values)
    return [v - centre for v in values]


def null_cell(cell: Cell, kind: str) -> Cell:
    """§3: the known-equal series E1 (zeros) and E2 (demeaned) cut from a pair; E3 is flipped per window."""

    if kind in ("real", "E3"):
        return cell
    if kind == "E1":
        return Cell(cell.dates, [0.0] * len(cell.d), cell.b, [0.0] * len(cell.d1), cell.b1)
    if kind == "E2":
        return Cell(cell.dates, demean(cell.d), cell.b, demean(cell.d1), cell.b1)
    raise RuleError(f"unknown series kind {kind!r}")


def flip_blocks(values: Sequence[float], seed: int) -> List[float]:
    """§3, E3: the series cut into blocks of `FLIP_BLOCK` days, each block's sign flipped by a fair coin."""

    rng = random.Random(seed)
    out: List[float] = []
    for start in range(0, len(values), FLIP_BLOCK):
        sign = 1.0 if rng.random() < 0.5 else -1.0
        out.extend(sign * v for v in values[start:start + FLIP_BLOCK])
    return out


def build_cells() -> Tuple[Dict[str, Cell], Dict[date, str], str, "cd.Pool"]:
    """The two pairs on their days, the lead-1 target day type of every decision day, the panel digest."""

    with tempfile.TemporaryDirectory() as tmp:
        panel = cd.build_panel(Path(tmp))
        digest = cd.sha256(panel)
        rows = load_daily_panel(panel)
    pool = cd.build_pool(rows)
    require_study_window(pool.dates + pool.dates3)
    position = {row.date: i for i, row in enumerate(rows)}
    kinds: Dict[date, str] = {}
    for day in pool.dates:
        target = rows[position[day] + 1]
        kinds[day] = cd.SPLITS.reporting_day_type(target.date, target.values)
    horizons = sp.HORIZONS
    b2 = cd.mean_over(pool.s1, horizons)
    d2 = [x - y for x, y in zip(b2, cd.mean_over(pool.s2, horizons))]
    p2 = Cell(list(pool.dates), d2, b2, [x - y for x, y in zip(pool.s1[1], pool.s2[1])], list(pool.s1[1]))
    b2r = cd.mean_over(pool.s2, horizons)
    p2r = Cell(list(pool.dates), [-v for v in d2], b2r, [-v for v in p2.d1], list(pool.s2[1]))
    b3 = cd.mean_over(pool.f1, horizons)
    d3 = [x - y for x, y in zip(b3, cd.mean_over(pool.f3, horizons))]
    p3 = Cell(list(pool.dates3), d3, b3, [x - y for x, y in zip(pool.f1[1], pool.f3[1])], list(pool.f1[1]))
    return {"P2": p2, "P2r": p2r, "P3": p3}, kinds, digest, pool


def day_cell(cell: Cell, kinds: Dict[date, str], which: str) -> Cell:
    if which == "all":
        return cell
    if which == "ordinary":
        return cell.subset([kinds[day] == "ordinary" for day in cell.dates])
    if which == "pressure":
        return cell.subset([kinds[day] != "ordinary" for day in cell.dates])
    raise RuleError(f"unknown day-type cell {which!r}")


# -- the three families (§4) -----------------------------------------------------------------------------------------


def _se(values: Sequence[float], lag: int) -> Optional[float]:
    variance = sp._long_run_variance(values, lag)
    return None if variance <= 0.0 else math.sqrt(variance / len(values))


def detect_a(d: Sequence[float], b: Sequence[float], looks: Sequence[int], critical: Dict[int, float]):
    """(a): the studentized mean of the first n days against the per-comparison value at looks 2 and 3.

    Returns (test, gated, undefined): `undefined` when a look has no variance (the series scores alike).
    """

    test = gated = undefined = False
    for n in looks[1:]:
        part = d[:n]
        se = _se(part, sp.HAC_LAG)
        if se is None:
            undefined = True
            continue
        mean = sum(part) / n
        if mean / se > critical[n]:
            test = True
            if mean / (sum(b[:n]) / n) >= sp.MME:
                gated = True
    return test, gated, undefined


def dm_lag(n: int) -> int:
    return int(round(DM_RATIO * n))


_DM_CACHE: Dict[Tuple[int, int, int], float] = {}


def dm_critical(n: int, lag: int, draws: int = WINDOWS) -> float:
    """(b): the one-sided 5% value of the statistic on independent standard-normal series (fixed-b)."""

    key = (n, lag, draws)
    if key not in _DM_CACHE:
        rng = random.Random(CALIBRATION_SEED)
        stats = []
        for _ in range(draws):
            x = [rng.gauss(0.0, 1.0) for _ in range(n)]
            se = _se(x, lag)
            stats.append(sum(x) / n / se)
        stats.sort()
        _DM_CACHE[key] = sp._bound(stats, 1.0 - sp.ALPHA, draws)
    return _DM_CACHE[key]


def detect_b(d: Sequence[float], b: Sequence[float], n: int, critical: float):
    """(b): one read at the window's end of the mean over its Bartlett standard error at lag round(0.1 N)."""

    se = _se(d, dm_lag(n))
    if se is None:
        return False, False, True
    mean = sum(d) / len(d)
    hit = mean / se > critical
    return hit, hit and mean / (sum(b) / len(b)) >= sp.MME, False


def log_capital(d: Sequence[float], scale: float):
    """(c): yields (s, log K_s, sum of x_r squared) for the betting e-process on d / scale.

    Raises ValueError if a difference exceeds `scale` (the bet would not be valid).
    """

    threshold = math.log(1.0 / sp.ALPHA)
    log_k = sum_sq = 0.0
    for s, dv in enumerate(d, 1):
        if abs(dv) > scale * (1.0 + 1e-9):
            raise ValueError(f"a difference of {dv} exceeds the e-process scale {scale}")
        v = (LAMBDA_PRIOR + sum_sq) / s
        lam = min(LAMBDA_CAP, math.sqrt(2.0 * threshold / (v * s * math.log(1.0 + s))))
        x = dv / scale
        log_k += math.log1p(lam * x)
        sum_sq += x * x
        yield s, log_k


def detect_c(d: Sequence[float], b: Sequence[float], scale: float):
    """(c): detected if the e-process reaches 1 / alpha on any day. Returns (test, gated)."""

    threshold = math.log(1.0 / sp.ALPHA)
    sum_d = sum_b = 0.0
    test = gated = False
    for (s, log_k), dv, bv in zip(log_capital(d, scale), d, b):
        sum_d += dv
        sum_b += bv
        if log_k >= threshold:
            test = True
            if sum_d / sum_b >= sp.MME:
                gated = True
                break
    return test, gated


def draw_windows(values: Sequence[float], days: int, rng: random.Random, generator: str) -> List[float]:
    out: List[float] = []
    size = len(values)
    if generator == "circular":
        while len(out) < days:
            start = rng.randrange(size)
            out.extend(values[(start + k) % size] for k in range(sp.WINDOW_BLOCK))
    elif generator == "stationary":
        while len(out) < days:
            out.extend(values[i] for i in stationary_bootstrap_indices(size, sp.BLOCK_LENGTH, rng))
    else:
        raise RuleError(f"unknown generator {generator!r}")
    return out[:days]


def window_statistics_gen(series: Sequence[float], days: int, lengths: Sequence[int], windows: int, seed: int,
                          generator: str) -> Dict[int, List[float]]:
    """Sorted studentized means of `windows` windows of `days` days, read at each prefix length in `lengths`."""

    values = [float(v) for v in series]
    truth = sum(values) / len(values)
    rng = random.Random(seed)
    out = {n: [] for n in lengths}
    for _ in range(windows):
        window = draw_windows(values, days, rng, generator)
        for n in lengths:
            part = window[:n]
            out[n].append((sum(part) / n - truth) / sp._standard_error(part, sp.HAC_LAG, "a window"))
    return {n: sorted(v) for n, v in out.items()}


def calibrate_a(series: Sequence[float], days: int, generator: str, windows: int = WINDOWS) -> Dict[int, float]:
    """(a): the per-comparison critical values at looks 2 and 3 of a window of `days`."""

    looks = cd.checkpoints(days)
    levels = sp.nominal_levels(looks)
    ordered = window_statistics_gen(series, days, looks[1:], windows, CALIBRATION_SEED, generator)
    return {n: sp._bound(ordered[n], 1.0 - levels[k + 1], windows) for k, n in enumerate(looks[1:])}


@dataclass
class Tests:
    """Everything a window needs to be read by the five families."""

    days: int
    a1: Dict[int, float]
    a2: Dict[int, float]
    b: float
    scale5: float
    scale1: float


def evaluate(d5, b5, d1, b1, tests: Tests) -> Dict[str, Tuple[bool, bool, bool]]:
    """Each family's (test, gated, undefined) on one window."""

    looks = cd.checkpoints(tests.days)
    out = {
        "a1": detect_a(d5, b5, looks, tests.a1),
        "a2": detect_a(d5, b5, looks, tests.a2),
        "b": detect_b(d5, b5, tests.days, tests.b),
    }
    out["c1"] = (*detect_c(d1, b1, tests.scale1), False)
    out["c5"] = (*detect_c(d5, b5, tests.scale5), False)
    return out


# -- the replay (§5) -------------------------------------------------------------------------------------------------


def window_starts(size: int, days: int) -> List[int]:
    return list(range(0, size - days + 1, STEP))


def share_interval(flags: Sequence[int], *, block: int, rng: random.Random) -> Tuple[float, float, float]:
    """The share of 1s and its 95% moving-block bootstrap interval over the (overlapping) windows."""

    n = len(flags)
    share = sum(flags) / n
    if share in (0.0, 1.0):
        return share, share, share
    block = max(1, min(block, n))
    prefix = [0]
    for f in flags:
        prefix.append(prefix[-1] + f)
    count = max(1, math.ceil(n / block))
    draws = []
    for _ in range(INTERVAL_DRAWS):
        total = 0
        for _ in range(count):
            s = rng.randrange(n - block + 1)
            total += prefix[s + block] - prefix[s]
        draws.append(total / (count * block))
    draws.sort()
    return share, draws[int(0.025 * INTERVAL_DRAWS)], draws[int(0.975 * INTERVAL_DRAWS) - 1]


def replay_cell(cell: Cell, kind: str, tests: Tests):
    """The windows of one series: for each, its last day and each family's (test, gated, undefined)."""

    base = null_cell(cell, kind)
    out = []
    for start in window_starts(len(base.d), tests.days):
        end = start + tests.days
        d5, d1 = base.d[start:end], base.d1[start:end]
        if kind == "E3":
            seed = SEED * 1_000_003 + start * 31 + tests.days
            d5, d1 = flip_blocks(d5, seed), flip_blocks(d1, seed)
        out.append((base.dates[end - 1], evaluate(d5, base.b[start:end], d1, base.b1[start:end], tests)))
    return out


def summarize_replay(windows, days: int) -> Dict[str, Dict[str, object]]:
    """Per regime (and pooled): windows, effective independent windows, shares with intervals."""

    rng = random.Random(SEED)
    out: Dict[str, Dict[str, object]] = {}
    block = math.ceil(days / STEP)
    for label in ("all",) + REGIMES:
        part = [w for w in windows if label == "all" or regime_of(w[0]) == label]
        if not part:
            continue
        cell: Dict[str, object] = {"windows": len(part), "effective": max(1, round((len(part) - 1) * STEP / days) + 1)}
        for family in FAMILIES:
            for measure, position in (("test", 0), ("gated", 1)):
                flags = [int(w[1][family][position]) for w in part]
                cell[f"{family}.{measure}"] = list(share_interval(flags, block=block, rng=rng))
            cell[f"{family}.undefined"] = sum(1 for w in part if w[1][family][2]) / len(part)
        out[label] = cell
    return out


# -- calibration jobs ------------------------------------------------------------------------------------------------


def calibrate_job(job):
    key, series, days, generator, windows = job
    return key, calibrate_a(series, days, generator, windows)


def scale_of(values: Sequence[float]) -> float:
    top = max((abs(v) for v in values), default=0.0)
    return top if top > 0.0 else 1.0


# -- the synthetic study (§6) ----------------------------------------------------------------------------------------

_DATA: Dict[str, object] = {}


def init_worker(histories, tests_by_days):
    _DATA["histories"] = histories
    _DATA["tests"] = tests_by_days
    _DATA["candidates"] = {}


def candidate_series(history: str, delta: float):
    """§6: `x_t = delta * b_t + (e_t - mean(e))`, on the five-lead and lead-1 scales, and their scales."""

    cache = _DATA["candidates"]
    key = (history, delta)
    if key not in cache:
        h = _DATA["histories"][history]
        out = []
        for b, e in ((h.b, h.d), (h.b1, h.d1)):
            centre = sum(e) / len(e)
            x = [delta * bv + (ev - centre) for bv, ev in zip(b, e)]
            out.append((x, scale_of(x)))
        cache[key] = out
    return cache[key]


def draw_path(size: int, days: int, rng: random.Random) -> List[int]:
    index: List[int] = []
    while len(index) < days:
        index.extend(stationary_bootstrap_indices(size, sp.BLOCK_LENGTH, rng))
    return index[:days]


def path_job(job):
    """`count` paths of one synthetic cell: per family, the numbers of tests and gated detections."""

    cell_id, history, days, delta, seed0, count = job
    h = _DATA["histories"][history]
    (x5, scale5), (x1, scale1) = candidate_series(history, delta)
    fixed = _DATA["tests"][days]
    tests = Tests(days, fixed.a1, fixed.a2, fixed.b, scale5, scale1)
    totals = {f"{f}.{m}": 0 for f in FAMILIES for m in ("test", "gated")}
    undefined = {f: 0 for f in ("a1", "a2", "b")}
    for i in range(count):
        rng = random.Random(seed0 + i)
        index = draw_path(len(x5), days, rng)
        d5 = [x5[j] for j in index]
        b5 = [h.b[j] for j in index]
        d1 = [x1[j] for j in index]
        b1 = [h.b1[j] for j in index]
        for family, (test, gated, undef) in evaluate(d5, b5, d1, b1, tests).items():
            totals[f"{family}.test"] += int(test)
            totals[f"{family}.gated"] += int(gated)
            if undef and family in undefined:
                undefined[family] += 1
    return cell_id, totals, undefined, count


def synthetic_cells(histories: Dict[str, Cell]):
    cells = []
    for delta in FULL_DELTAS:
        for days in SYNTHETIC_LENGTHS:
            cells.append(("full", days, delta))
    for history in histories:
        if history == "full":
            continue
        for delta in OTHER_DELTAS:
            for days in WINDOW_LENGTHS:
                cells.append((history, days, delta))
    return cells


def run_synthetic(histories, tests_by_days, paths, workers):
    cells = synthetic_cells(histories)
    jobs = []
    chunk = 250
    for c, (history, days, delta) in enumerate(cells):
        for first in range(0, paths, chunk):
            seed0 = SEED * 100_003 + c * 1_000_003 + first
            jobs.append((c, history, days, delta, seed0, min(chunk, paths - first)))
    with multiprocessing.Pool(max(1, workers), initializer=init_worker, initargs=(histories, tests_by_days)) as pool:
        done = pool.map(path_job, jobs, chunksize=1)
    agg: Dict[int, Dict[str, int]] = {}
    und: Dict[int, Dict[str, int]] = {}
    count: Dict[int, int] = {}
    for cell_id, totals, undefined, n in done:
        a = agg.setdefault(cell_id, {k: 0 for k in totals})
        u = und.setdefault(cell_id, {k: 0 for k in undefined})
        for k, v in totals.items():
            a[k] += v
        for k, v in undefined.items():
            u[k] += v
        count[cell_id] = count.get(cell_id, 0) + n
    out = {}
    for c, (history, days, delta) in enumerate(cells):
        n = count[c]
        out[f"{history}|{days}|{delta}"] = {
            "paths": n,
            **{k: v / n for k, v in agg[c].items()},
            **{f"{k}.undefined": v / n for k, v in und[c].items()},
        }
    return out


def history_cells(p2: Cell, kinds: Dict[date, str]) -> Dict[str, Cell]:
    out = {"full": p2}
    for regime in REGIMES:
        out[regime] = p2.subset([regime_of(day) == regime for day in p2.dates])
    out["ordinary"] = day_cell(p2, kinds, "ordinary")
    out["pressure"] = day_cell(p2, kinds, "pressure")
    return out


# -- reading (§6, §7) ------------------------------------------------------------------------------------------------


def smallest_gain(synthetic, family: str, days: int, measure: str = "gated") -> Optional[float]:
    for delta in FULL_DELTAS[1:]:
        if synthetic[f"full|{days}|{delta}"][f"{family}.{measure}"] >= TARGET_POWER:
            return delta
    return None


def reading(replay, synthetic) -> Dict[str, object]:
    """§7: the one recommended test among a2, b, c1, by the rule's size limit and synthetic power."""

    rows = {}
    for family in CANDIDATE_FAMILIES:
        sizes = {
            f"{pair}|{kind}": replay[f"{pair}|all|{kind}|250"]["all"][f"{family}.test"][0]
            for pair in PAIRS for kind in ("E2", "E3")
        }
        sizes["synthetic"] = synthetic["full|250|0.0"][f"{family}.test"]
        power = synthetic["full|250|0.03"][f"{family}.gated"]
        rows[family] = {"sizes": sizes, "power_at_3": power, "admissible": all(v <= SIZE_LIMIT for v in sizes.values())}
    admissible = [f for f in CANDIDATE_FAMILIES if rows[f]["admissible"]]
    pick = None
    if admissible:
        best = max(rows[f]["power_at_3"] for f in admissible)
        winners = [f for f in admissible if rows[f]["power_at_3"] == best]
        pick = winners[0] if len(winners) == 1 else None
    return {"families": rows, "admissible": admissible, "pick": pick}


# -- the commands ----------------------------------------------------------------------------------------------------


def describe_command(args) -> int:
    cells, kinds, digest, pool = build_cells()
    print(json.dumps({
        "panel_sha256": digest, "first": pool.dates[0].isoformat(), "last": pool.dates[-1].isoformat(),
        "days_p2": len(cells["P2"].d), "days_p3": len(cells["P3"].d),
        "ordinary_p2": len(day_cell(cells["P2"], kinds, "ordinary").d),
        "pressure_p2": len(day_cell(cells["P2"], kinds, "pressure").d),
    }, sort_keys=True))
    return 0


def known_better(cells: Dict[str, Cell]) -> Dict[str, Dict[str, object]]:
    out = {}
    for pair, cell in cells.items():
        skill = sum(cell.d) / sum(cell.b)
        benchmark = dict(zip(cell.dates, cell.b))
        candidate = {day: b - d for day, b, d in zip(cell.dates, cell.b, cell.d)}
        test = sp.paired_test(benchmark, candidate, seed=SEED, with_skill=False)
        out[pair] = {"days": len(cell.d), "skill": skill, "p_value": test.p_value,
                     "known_better": skill >= sp.MME and test.p_value < sp.ALPHA}
    return out


def eprocess_diagnostics(cells: Dict[str, Cell]) -> Dict[str, Dict[str, object]]:
    """Post-hoc (rule §9): the scale of the e-process against the size of the signal, on each pair's whole series."""

    out = {}
    for pair, cell in cells.items():
        for label, d, b in (("5", cell.d, cell.b), ("1", cell.d1, cell.b1)):
            scale = scale_of(d)
            mean = sum(d) / len(d)
            sd = math.sqrt(sum((v - mean) ** 2 for v in d) / (len(d) - 1))
            crossing = next((s for s, k in log_capital(d, scale) if k >= math.log(1.0 / sp.ALPHA)), None)
            out[f"{pair}|lead{label}"] = {"scale": scale, "mean": mean, "sd": sd, "mean_over_scale": mean / scale,
                                         "sharpe": mean / sd, "first_crossing_day": crossing, "days": len(d)}
    return out


def run_command(args) -> int:
    out = Path(args.out)
    cells, kinds, digest, pool = build_cells()
    better = known_better(cells)
    print("known better", json.dumps(better), flush=True)
    day_cells = {(pair, which): day_cell(cells[pair], kinds, which) for pair in PAIRS for which in DAY_CELLS}
    jobs = []
    for (pair, which), cell in day_cells.items():
        for days in (SYNTHETIC_LENGTHS if (pair, which) == ("P2", "all") else WINDOW_LENGTHS):
            if len(cell.d) < days + STEP:
                continue
            for generator, tag in (("circular", "a1"), ("stationary", "a2")):
                jobs.append((f"{pair}|{which}|{days}|{tag}", cell.d, days, generator, args.windows))
    with multiprocessing.Pool(max(1, args.workers)) as workers:
        calibrated = dict(workers.map(calibrate_job, jobs, chunksize=1))
    print("calibrated", len(calibrated), flush=True)
    crit = {k: {str(n): c for n, c in v.items()} for k, v in calibrated.items()}

    def lookup(prefix: str) -> Dict[str, Dict[int, float]]:
        return {tag: calibrated[f"{prefix}|{tag}"] for tag in ("a1", "a2")}

    replay = {}
    for (pair, which), cell in day_cells.items():
        for days in WINDOW_LENGTHS:
            if len(cell.d) < days + STEP:
                replay[f"{pair}|{which}|empty|{days}"] = {"days": len(cell.d)}
                continue
            found = lookup(f"{pair}|{which}|{days}")
            for kind in KINDS:
                series = null_cell(cell, kind)
                tests = Tests(days, found["a1"], found["a2"], dm_critical(days, dm_lag(days)),
                              scale_of(series.d), scale_of(series.d1))
                windows = replay_cell(cell, kind, tests)
                replay[f"{pair}|{which}|{kind}|{days}"] = summarize_replay(windows, days)
        print("replayed", pair, which, flush=True)

    histories = history_cells(cells["P2"], kinds)
    tests_by_days = {
        days: Tests(days, calibrated[f"P2|all|{days}|a1"], calibrated[f"P2|all|{days}|a2"],
                    dm_critical(days, dm_lag(days)), 1.0, 1.0)
        for days in SYNTHETIC_LENGTHS
    }
    synthetic = run_synthetic(histories, tests_by_days, args.paths, args.workers)
    mde = {family: {str(days): smallest_gain(synthetic, family, days) for days in (125, 250, 500)}
           for family in FAMILIES}
    mde_test = {family: {str(days): smallest_gain(synthetic, family, days, "test") for days in (125, 250, 500)}
                for family in FAMILIES}
    result = {
        "rule": str(RULE.relative_to(REPO)), "rule_sha256": sha256(RULE), "panel_sha256": digest,
        "study_end": STUDY_END.isoformat(),
        "pool": {"first": pool.dates[0].isoformat(), "last": max(pool.dates + pool.dates3).isoformat(),
                 "days_p2": len(cells["P2"].d), "days_p3": len(cells["P3"].d),
                 "ordinary_p2": len(histories["ordinary"].d), "pressure_p2": len(histories["pressure"].d),
                 "regime_days": {r: len(histories[r].d) for r in REGIMES}},
        "constants": {"windows": args.windows, "paths": args.paths, "seed": SEED, "step": STEP,
                      "flip_block": FLIP_BLOCK, "dm_ratio": DM_RATIO, "interval_draws": INTERVAL_DRAWS,
                      "mme": sp.MME, "alpha": sp.ALPHA, "hac_lag": sp.HAC_LAG, "block_length": sp.BLOCK_LENGTH,
                      "window_block": sp.WINDOW_BLOCK, "lambda_cap": LAMBDA_CAP, "lambda_prior": LAMBDA_PRIOR},
        "pairs": better,
        "eprocess_diagnostics": eprocess_diagnostics(cells),
        "critical_a": crit,
        "critical_b": {str(n): dm_critical(n, dm_lag(n)) for n in SYNTHETIC_LENGTHS},
        "replay": replay,
        "synthetic": synthetic,
        "smallest_gain": {"gated": mde, "test": mde_test},
        "reading": reading(replay, synthetic),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out / "result.json")
    return 0


FAMILY_NAMES = {
    "a1": "(a1) the current test, critical values from circular blocks",
    "a2": "(a2) the current test, critical values matched to the paths (stationary bootstrap)",
    "b": "(b) the self-normalised Diebold-Mariano test (fixed-b)",
    "c1": "(c1) the anytime-valid e-process, lead 1",
    "c5": "(c5) the anytime-valid e-process, mean of leads 1 to 5",
}
KIND_NAMES = {"real": "real pair", "E1": "E1 relabelled copy", "E2": "E2 demeaned", "E3": "E3 sign-flipped"}
PAIR_NAMES = {"P2": "P2 B2 vs B1", "P2r": "P2r B1 vs B2", "P3": "P3 B3 vs B1"}


def pct(value: float) -> str:
    return f"{100.0 * value:.0f}%" if value not in (0.0, 1.0) else f"{100.0 * value:.0f}%"


def share_cell(cell: Optional[Dict[str, object]], key: str) -> str:
    if cell is None or key not in cell:
        return "n/a"
    share, low, high = cell[key]
    if share in (0.0, 1.0) and low == high:
        return f"{100.0 * share:.0f}%"
    return f"{100.0 * share:.0f}% [{100.0 * low:.0f}, {100.0 * high:.0f}]"


def table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return out + [""]


QUESTIONS = [
    "## Sources read, and what they say", "",
    "Read as abstracts only, on arXiv, on 15 October 2026; the full texts were not read, so what follows is limited to "
    "the abstracts.", "",
    "- Henzi and Ziegel, *Valid sequential inference on probability forecast performance* (arXiv 2103.08402): the "
    "abstract is about **probability forecasts for binary events**, and its e-values are for score differences of such "
    "forecasts. It does not say that they cover the CRPS of a distribution forecast, so family (c) here is a betting "
    "e-process of the same kind applied to a CRPS difference, not their construction.",
    "- Choe and Ramdas, *Comparing sequential forecasters* (arXiv 2110.00115): the abstract says the main theorems apply "
    "to **bounded scores**, with alternative methods for unbounded ones, and that the procedures test a weak null "
    "(better on average). Family (c) takes a declared bound `C` (the largest absolute difference in the development "
    "history) and a plug-in bet; it is not their variance-adaptive confidence sequence.",
    "- Diebold and Mariano (1995), Giacomini and White (2006), Kiefer and Vogelsang: not fetched. The fixed-b value of "
    "(b) is simulated here on standard-normal series at the same lag, not taken from their tables.", "",
    "## Questions for Eleonora (this page decides nothing)", "",
    "1. **Is a confirmation test with no power at the MME acceptable to carry forward?** No family reaches 80% power "
    "at any gain up to 30% in 250 days, and (a) reaches it only at a 50% gain in 500 days. The arithmetic above says why: "
    "per day the signal is a small fraction of the noise, even for the 22% gain of B3. Whether to change the MME, the "
    "days or the target is hers; #769 re-runs the power study on the test in force.",
    "2. **Is the current test's size acceptable?** Its per-comparison critical value is calibrated on a skewed series, "
    "so on a symmetric null (E3, the sign-flipped B3 pair) it flags 27% to 33% of windows, with the matched generator "
    "(a2) as well as without it. A symmetrised or recentred null would be a change to the protocol: a draft decision "
    "record, not code.",
    "3. **Should family (c) be studied with a variance-adaptive confidence sequence?** As declared (a bound set by the "
    "largest difference in history) its bets are too small to cross in the whole history; a different construction is a "
    "different test, and one more step.",
    "4. **The only known-better pair is B3 on development days.** The replay's power is for a gain of 22%, not 3%. Pairs "
    "with a known gain near the MME do not exist in the data held.", ""
]


def render_page(result) -> str:
    replay, synth = result["replay"], result["synthetic"]
    k = result["constants"]
    pool = result["pool"]
    lines: List[str] = [
        "# Power by empirical replay and three test families: result (H1 step 3, #754)", "",
        "<!-- generated: scripts/power_replay.py report; never hand-edited -->", "",
        f"The rule is [`power-replay-754.md`](power-replay-754.md) (committed before the study ran; sha256 "
        f"`{result['rule_sha256'][:12]}…`). Development data only: {pool['days_p2']} decision days from {pool['first']} to "
        f"{pool['last']}, panel `{result['panel_sha256'][:8]}…`; no day after {result['study_end']} is read. It is a "
        f"design study: no verdict, nothing registered, no protocol code changed. Replay windows start every {k['step']} "
        f"days and overlap, so each share is shown with a {k['interval_draws']}-draw moving-block bootstrap interval "
        f"and the effective number of independent windows is given. Synthetic cells have {k['paths']} paths; "
        f"critical values are calibrated on {k['windows']} windows.", ""]

    lines += ["## The pairs", "",
              "A pair is known better only if its mean skill is at least the MME (3%) and the studentized bootstrap "
              "p-value is below 5%. P2 and P2r are the same noise in the two orientations (amendment in the rule).", ""]
    lines += table(["pair", "days", "mean skill against its benchmark", "p-value", "known better"],
                   [[PAIR_NAMES[p], str(v["days"]), f"{100 * v['skill']:.1f}%", f"{v['p_value']:.3f}",
                     "yes" if v["known_better"] else "**no**"] for p, v in result["pairs"].items()])
    better = [p for p, v in result["pairs"].items() if v["known_better"]]
    lines += [("Only " + ", ".join(better) + " is a known-better pair; a detection share on the others is not power."
               if len(better) < len(PAIRS) else "Every pair is known better."), "",
              f"Day-type cells (lead-1 target day): {pool['ordinary_p2']} ordinary days and {pool['pressure_p2']} pressure "
              f"days of P2's {pool['days_p2']}. Regime days: "
              + ", ".join(f"{r} {n}" for r, n in pool["regime_days"].items()) + ".", ""]

    lines += ["## Effective windows", "",
              "Windows of `N` days every 5 days over the all-days series, and the effective number of independent windows "
              "(`(windows - 1) * 5 / N + 1`).", ""]
    rows = []
    for pair in PAIRS:
        for days in WINDOW_LENGTHS:
            c = replay[f"{pair}|all|real|{days}"]["all"]
            rows.append([PAIR_NAMES[pair], str(days), str(c["windows"]), str(c["effective"])])
    lines += table(["pair", "N", "windows", "effective"], rows)

    lines += ["## Replay: size and power on real forecast pairs", "",
              "Each cell is the share of windows in which the family flags the candidate (the test alone; the MME-gated "
              "share is in the next table), with its interval. The real pair's share is power only for a known-better "
              "pair. E1 is the relabelled copy (always 0%; (a) and (b) are undefined there, because the two scores "
              "never differ), E2 the demeaned pair, E3 the block sign-flip.", ""]
    for family in FAMILIES:
        lines += [f"### {FAMILY_NAMES[family]}", ""]
        rows = []
        for pair in PAIRS:
            for kind in KINDS:
                row = [PAIR_NAMES[pair], KIND_NAMES[kind]]
                for days in WINDOW_LENGTHS:
                    row.append(share_cell(replay[f"{pair}|all|{kind}|{days}"].get("all"), f"{family}.test"))
                for days in WINDOW_LENGTHS:
                    row.append(share_cell(replay[f"{pair}|all|{kind}|{days}"].get("all"), f"{family}.gated"))
                rows.append(row)
        lines += table(["pair", "series"] + [f"test, N={n}" for n in WINDOW_LENGTHS] + [f"gated, N={n}" for n in WINDOW_LENGTHS], rows)

    lines += ["## Replay: the pooled figure beside its splits", "",
              "The test alone, by the regime of the window's last day and by day-type cell. `ordinary` and `pressure` "
              "cut the series (windows of `N` consecutive retained days); n/a is a cell with no windows.", ""]
    for family in FAMILIES:
        lines += [f"### {FAMILY_NAMES[family]}", ""]
        rows = []
        for pair in PAIRS:
            for kind in ("real", "E2", "E3"):
                for days in WINDOW_LENGTHS:
                    allc = replay[f"{pair}|all|{kind}|{days}"]
                    row = [PAIR_NAMES[pair], KIND_NAMES[kind], str(days), share_cell(allc.get("all"), f"{family}.test")]
                    row += [share_cell(allc.get(r), f"{family}.test") for r in REGIMES]
                    for which in ("ordinary", "pressure"):
                        cell = replay.get(f"{pair}|{which}|{kind}|{days}")
                        row.append(share_cell(cell.get("all") if cell else None, f"{family}.test"))
                    rows.append(row)
        lines += table(["pair", "series", "N", "all windows"] + list(REGIMES) + ["ordinary days", "pressure days"], rows)

    lines += ["## Synthetic: size and power by gain", "",
              "Paths drawn by the stationary bootstrap from the P2 full history; the candidate has true mean skill `delta` "
              "against B1. Each cell is `test / gated` (standard error at most 1.1 points). The `delta = 0` row is size.", ""]
    for family in FAMILIES:
        lines += [f"### {FAMILY_NAMES[family]}", ""]
        rows = []
        for delta in FULL_DELTAS:
            row = [f"{100 * delta:g}%"]
            for days in SYNTHETIC_LENGTHS:
                c = synth[f"full|{days}|{delta}"]
                row.append(f"{pct(c[family + '.test'])} / {pct(c[family + '.gated'])}")
            rows.append(row)
        lines += table(["true skill"] + [f"N={n}" for n in SYNTHETIC_LENGTHS], rows)

    lines += ["### Synthetic by regime and day type", "",
              "Test / gated at `N` = 60, 125 and 250 for a path drawn from one regime's days or one day-type cell "
              "(critical values of (a) still calibrated on the full history).", ""]
    for family in FAMILIES:
        lines += [f"#### {FAMILY_NAMES[family]}", ""]
        rows = []
        for history in ("full",) + REGIMES + ("ordinary", "pressure"):
            for days in WINDOW_LENGTHS:
                row = [history, str(days)]
                for delta in OTHER_DELTAS:
                    c = synth[f"{history}|{days}|{delta}"]
                    row.append(f"{pct(c[family + '.test'])} / {pct(c[family + '.gated'])}")
                rows.append(row)
        lines += table(["history", "N", "size (0%)", "3% skill", "10% skill"], rows)

    lines += ["## What matching the null generator changes", "",
              "Critical values of (a) at looks 2 and 3 on the P2 full history, and synthetic size and power at 3% skill.", ""]
    rows = []
    for days in SYNTHETIC_LENGTHS:
        c1, c2 = result["critical_a"][f"P2|all|{days}|a1"], result["critical_a"][f"P2|all|{days}|a2"]
        first, last = sorted(c1, key=int)[0], sorted(c1, key=int)[-1]
        s0, s3 = synth[f"full|{days}|0.0"], synth[f"full|{days}|0.03"]
        rows.append([str(days), f"{c1[first]:.2f} / {c1[last]:.2f}", f"{c2[first]:.2f} / {c2[last]:.2f}",
                     f"{pct(s0['a1.test'])} → {pct(s0['a2.test'])}", f"{pct(s3['a1.gated'])} → {pct(s3['a2.gated'])}"])
    lines += table(["N", "critical value, a1 (look 2 / 3)", "a2 (look 2 / 3)", "synthetic size, a1 → a2",
                    "synthetic gated power at 3%, a1 → a2"], rows)

    lines += ["## The smallest detectable gain at 80% power", "",
              "The smallest `delta` on the grid (3% to 50%) at which the synthetic gated power is at least 80%; `none` "
              "means none on the grid.", ""]
    rows = []
    for family in FAMILIES:
        row = [FAMILY_NAMES[family]]
        for days in (125, 250, 500):
            g = result["smallest_gain"]["gated"][family][str(days)]
            t = result["smallest_gain"]["test"][family][str(days)]
            row.append(("none" if g is None else f"{100 * g:g}%") + " (test alone: " + ("none" if t is None else f"{100 * t:g}%") + ")")
        rows.append(row)
    lines += table(["family", "125 days", "250 days", "500 days"], rows)

    lines += ["## The e-process scale (post-hoc description, rule §9)", "",
              "Over each pair's whole series. `mean / scale` is the daily average of the bounded bet; the last column is "
              "the day the e-process first reaches 20 when run from the first day.", ""]
    rows = []
    for key, v in result["eprocess_diagnostics"].items():
        pair, lead = key.split("|")
        rows.append([PAIR_NAMES[pair], lead, f"{v['scale']:.3g}", f"{v['mean']:.3g}", f"{v['sd']:.3g}",
                     f"{v['mean_over_scale']:.2g}", f"{v['sharpe']:.2f}",
                     "never" if v["first_crossing_day"] is None else str(v["first_crossing_day"])])
    lines += table(["pair", "reading", "scale C (max abs d)", "mean d", "sd d", "mean / C", "mean / sd", "first crossing (of "
                    f"{pool['days_p2']})"], rows)

    z = NormalDist().inv_cdf(1.0 - sp.ALPHA) + NormalDist().inv_cdf(TARGET_POWER)
    lines += ["### The arithmetic behind it", "",
              "With independent days and a known standard deviation, a one-sided 5% test has 80% power when "
              f"`n = ({z:.3f} / s)^2`, `s` being the mean over the standard deviation of the daily difference. This is a "
              "calculation from the whole-series figures above, not a simulation; serial dependence and a studentized "
              "statistic need more days.", ""]
    rows = []
    for pair in PAIRS:
        v = result["eprocess_diagnostics"][f"{pair}|lead5"]
        skill = result["pairs"][pair]["skill"]
        if v["sharpe"] <= 0.0:
            rows.append([PAIR_NAMES[pair], f"{v['sharpe']:.3f}", "the pair is worse than its benchmark", "n/a"])
            continue
        at_mme = v["sharpe"] * sp.MME / skill
        rows.append([PAIR_NAMES[pair], f"{v['sharpe']:.3f}", f"{(z / v['sharpe']) ** 2:,.0f} days",
                     f"{(z / at_mme) ** 2:,.0f} days"])
    lines += table(["pair", "s (mean / sd, leads 1 to 5)", "days at the pair's own gain", "days if the gain were the 3% MME"], rows)

    reading_ = result["reading"]
    lines += ["## Reading (§7)", ""]
    rows = []
    for family in CANDIDATE_FAMILIES:
        r = reading_["families"][family]
        worst = max(r["sizes"].values())
        rows.append([FAMILY_NAMES[family], "yes" if r["admissible"] else "no", pct(worst), pct(r["power_at_3"])])
    lines += table(["family", "size at most 5% everywhere", "largest size among the seven checks", "synthetic gated power at 3%, 250 days"], rows)
    pick = reading_["pick"]
    lines += [f"Families holding the size limit: {', '.join(reading_['admissible']) or 'none'}.", ""]
    if pick is None:
        lines += ["**No family holds the size limit and singles itself out; the rule recommends none.**", ""]
    else:
        power = reading_["families"][pick]["power_at_3"]
        a1 = synth["full|250|0.03"]["a1.gated"]
        gain = result["smallest_gain"]["gated"][pick]["250"]
        lines += [f"**Recommended by the rule: {pick}** ({FAMILY_NAMES[pick]}).", "",
                  f"Trade-off against the current design (a1, 250 days): synthetic gated power at 3% {pct(a1)} → {pct(power)}; "
                  f"synthetic size {pct(synth['full|250|0.0']['a1.test'])} → {pct(synth['full|250|0.0'][pick + '.test'])}.", "",
                  f"Smallest detectable gain at 250 days at 80% power: {'none on the grid (up to 50%)' if gain is None else f'{100 * gain:g}%'}.", ""]
        if power < TARGET_POWER:
            lines += [f"**The pick has no useful power:** its synthetic gated power at 3% is {pct(power)}. It holds the size "
                      "limit because it almost never flags anything, which is not a recommendation of a test that can "
                      "confirm the MME.", ""]
    lines += QUESTIONS
    return "\n".join(lines).rstrip() + "\n"


def report_command(args) -> int:
    result = json.loads((Path(args.out) / "result.json").read_text(encoding="utf-8"))
    PAGE.write_text(render_page(result), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(args) -> int:
    result = json.loads((Path(args.out) / "result.json").read_text(encoding="utf-8"))
    if result["rule_sha256"] != sha256(RULE):
        raise RuleError("result.json was made under another text of the rule")
    if result["pool"]["last"] > STUDY_END.isoformat():
        raise RuleError("the study scored a day after its end")
    if PAGE.read_text(encoding="utf-8") != render_page(result):
        raise RuleError("the result page is not the one result.json renders")
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("describe").set_defaults(func=describe_command)
    run = sub.add_parser("run")
    run.add_argument("--out", required=True)
    run.add_argument("--paths", type=int, default=PATHS)
    run.add_argument("--windows", type=int, default=WINDOWS)
    run.add_argument("--workers", type=int, default=1)
    run.set_defaults(func=run_command)
    for name, func in (("report", report_command), ("check", check_command)):
        command = sub.add_parser(name)
        command.add_argument("--out", required=True)
        command.set_defaults(func=func)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
