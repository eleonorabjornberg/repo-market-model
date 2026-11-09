"""Why (s3c-ann-net)'s bands fail on quarter-end days: event influence, tail-support provenance and same-target paths (#1533, H5, step 3).

A development study, never a verdict. It diagnoses the candidate's own forecasts and changes, fits and registers nothing. Her ruling of 9 November
2026 (relayed on #1533): the first diagnostic package combines event influence, tail-support provenance and same-target forecast paths, reusing the
development forecasts, and names the mechanism the evidence supports and the repair it points to (A, B, C or D), or says the evidence cannot yet
tell; and, on docket card h5-family-1109, says plainly whether the quarter-end tails point to a width problem or a shape problem.

Every choice is in `metadata/qe_diagnosis_1533.json`, which `walk` and `score` refuse to read unless it is committed and unchanged. `walk` calls
`scripts/candidate_calibration_1363.py walk` unchanged (it only keeps the `Walk` that `spread_mr_state_calendar.walk` returns), checks the sha256 of
the file it writes against `docs/research/candidate-calibration-1363/result.json` (`walk_files`) and refuses to go on otherwise, then writes an
extension file with each refit's coefficients, Huber iterations and residual pool. No day after 2026-09-03 and no locked day is read.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    for W in development 2026; do
      RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/qe_diagnosis_1533.py walk --panel PUB.csv --window $W \\
          --output WALK/$W.json --extension EXT/$W.json
    done
    OUT=docs/research/qe-diagnosis-1533
    PYTHONPATH=src python3 scripts/qe_diagnosis_1533.py score --walks WALK --extensions EXT --output $OUT/result.json --tail-support $OUT/tail-support.json
    PYTHONPATH=src python3 scripts/qe_diagnosis_1533.py page --score $OUT/result.json --output docs/research/qe-diagnosis-1533-result.md

The walks take about three and a half minutes in all, the tail bootstrap a few minutes on four cores: below the `long-run` line. Stdlib only.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from multiprocessing import Pool
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import metrics, protocol_benchmarks as pb, scoring_protocol as sp, turn_days  # noqa: E402
from repo_model.exploration import EXPLORATORY_END  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "qe_diagnosis_1533.json"
RECORD_1363 = REPO / "docs" / "research" / "candidate-calibration-1363" / "result.json"
SEED = 1533
BLOCK = 10.0
SENSITIVITY_BLOCKS = (5.0, 20.0)
POOL_REPS = 500
EVENT_REPS = 2000
LEVEL = 0.90
TAILS = (0.01, 0.05, 0.95, 0.99)
MIDDLE = (0.25, 0.5, 0.75)
GRID = sp.GRID
LEADS = tuple(sp.HORIZONS)
WINDOWS = ("development", "2026")
WINDOW_LAST = {"development": date(2025, 12, 31), "2026": EXPLORATORY_END}
CANDIDATE = "sc_s3c_ann_net"
EVENT_TYPES = (turn_days.QUARTER_END_TURN, turn_days.YEAR_END)
PRESSURE_TYPES = (turn_days.QUARTER_END_TURN, turn_days.YEAR_END, turn_days.TURN, turn_days.TAX_DATE, turn_days.ORDINARY)
CLUSTER_GAP = 5
ZERO_BEFORE = "before the first regime"


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any figure")
    return json.loads(path.read_text(encoding="utf-8"))


def refuse_beyond(days: Sequence[date], last: date, *, where: str = "qe_diagnosis_1533") -> None:
    """Refuse a day after `last` (the window's declared end): raises `LookAheadError`."""

    for day in days:
        if day > last:
            raise LookAheadError(f"{where}: day {day} is after {last}, the last day of the window this study reads")


# -- which pool members set a tail ---------------------------------------------------------------------------------------------


def support_position(n: int, tau: float) -> Tuple[int, float]:
    """The rank below the interpolated quantile and the weight on the next rank, as `protocol_benchmarks.empirical_quantiles`."""

    position = tau * (n - 1)
    low = int(position)
    return low, position - low


def setter_ranks(n: int, tau: float) -> Tuple[int, ...]:
    """The sorted ranks that set the quantile at `tau`: one when the position is whole, two otherwise."""

    low, weight = support_position(n, tau)
    return (low, low + 1) if weight else (low,)


def neighbour_ranks(n: int, tau: float) -> Tuple[int, ...]:
    """The ranks just outside the setters (clipped to the pool)."""

    low, weight = support_position(n, tau)
    outer = (low - 1, low + 2) if weight else (low - 1, low + 1)
    return tuple(r for r in outer if 0 <= r < n)


def zone_ranks(n: int, tau: float) -> range:
    """The ranks strictly beyond the quantile: below it for a lower tail (tau < 0.5), above it for an upper one."""

    low, weight = support_position(n, tau)
    if tau < 0.5:
        return range(0, low + 1 if weight else low)
    return range(low + 1, n)


def rank_order(values: Sequence[float]) -> List[int]:
    """The pool positions in ascending order of value, ties by position: `order[r]` is the member of sorted rank `r`."""

    return sorted(range(len(values)), key=lambda i: (values[i], i))


# -- events --------------------------------------------------------------------------------------------------------------------


def quarter_end_event(day: date) -> Optional[str]:
    """The id (`YYYY-MM` of the quarter-end's last business day) when `day` is one of the two turn days of a quarter-end, else `None`."""

    previous = (day.year, day.month - 1) if day.month > 1 else (day.year - 1, 12)
    for year, month in (previous, (day.year, day.month)):
        if day in turn_days.turn_days_of_month(year, month) and turn_days._month_label(month) in EVENT_TYPES:
            return f"{year}-{month:02d}"
    return None


def distinct_clusters(rows: Sequence[int], gap: int, events: Sequence[Optional[str]]) -> int:
    """The number of distinct events among members at panel rows `rows`: one per quarter-end event id, and one per chain of other
    members whose rows lie within `gap` of the next."""

    ids = {e for e in events if e is not None}
    other = sorted(r for r, e in zip(rows, events) if e is None)
    chains = 0
    previous = None
    for r in other:
        if previous is None or r - previous > gap:
            chains += 1
        previous = r
    return len(ids) + chains


# -- influence ------------------------------------------------------------------------------------------------------------------


def leave_one_out(cells: Sequence, key: Callable, statistic: Callable) -> dict:
    """`statistic` of the cells with each event left out in turn: the full value, the range and the events that make its ends."""

    events = sorted({key(c) for c in cells}, key=str)
    values = {e: statistic([c for c in cells if key(c) != e]) for e in events if any(key(c) != e for c in cells)}
    lo = min(values, key=lambda e: (values[e], str(e)))
    hi = max(values, key=lambda e: (values[e], str(e)))
    return {"full": statistic(list(cells)), "min": values[lo], "min_event": lo, "max": values[hi], "max_event": hi, "events": len(events),
            "values": values}


def greedy_drop(cells: Sequence, key: Callable, statistic: Callable, count: int) -> List[dict]:
    """Remove, `count` times, the event whose removal moves `statistic` most; each step's event and the value after it."""

    rest = list(cells)
    out = []
    for _ in range(count):
        events = sorted({key(c) for c in rest}, key=str)
        if len(events) < 2:
            break
        now = statistic(rest)
        best = max(events, key=lambda e: (abs(statistic([c for c in rest if key(c) != e]) - now), str(e)))
        rest = [c for c in rest if key(c) != best]
        out.append({"event": best, "value": statistic(rest)})
    return out


def percentile(sorted_values: Sequence[float], p: float) -> float:
    return sorted_values[min(len(sorted_values) - 1, max(0, int(p * (len(sorted_values) - 1) + 0.5)))]


def interval_of(values: Sequence[float], level: float = LEVEL) -> Tuple[float, float]:
    ordered = sorted(values)
    return percentile(ordered, (1 - level) / 2), percentile(ordered, 1 - (1 - level) / 2)


def event_interval(cells: Sequence, key: Callable, statistic: Callable, *, reps: int = EVENT_REPS, seed: int = SEED) -> Tuple[float, float]:
    """The 90% percentile interval of `statistic` over resamples of whole events (iid, with replacement)."""

    groups: Dict = defaultdict(list)
    for c in cells:
        groups[key(c)].append(c)
    clusters = [groups[k] for k in sorted(groups, key=str)]
    rng = random.Random(seed)
    draws = []
    for _ in range(reps):
        picked = [c for i in (rng.randrange(len(clusters)) for _ in clusters) for c in clusters[i]]
        draws.append(statistic(picked))
    return interval_of(draws)


def event_mean_intervals(sums: Sequence[Sequence[float]], counts: Sequence[int], *, reps: int = EVENT_REPS, seed: int = SEED) -> List[Tuple[float, float]]:
    """Intervals of the pooled means of several metrics at once from per-event sums (`sums[e][m]`) and cell counts, off the same resamples."""

    k = len(sums)
    width = len(sums[0]) if sums else 0
    rng = random.Random(seed)
    draws: List[List[float]] = [[] for _ in range(width)]
    for _ in range(reps):
        picks = [rng.randrange(k) for _ in range(k)]
        n = sum(counts[i] for i in picks)
        for m in range(width):
            draws[m].append(sum(sums[i][m] for i in picks) / n)
    return [interval_of(d) for d in draws]


# -- the bootstrap of a pool ----------------------------------------------------------------------------------------------------


def stationary_indices(n: int, mean_block: float, rng: random.Random) -> List[int]:
    """One stationary-bootstrap resample of `n` positions (Politis and Romano): a block continues with probability 1 - 1/mean_block and wraps."""

    restart = 1.0 / mean_block
    out = [rng.randrange(n)]
    for _ in range(n - 1):
        out.append(rng.randrange(n) if rng.random() < restart else (out[-1] + 1) % n)
    return out


def quantile_of_sorted(ordered: Sequence[float], tau: float) -> float:
    low, weight = support_position(len(ordered), tau)
    value = ordered[low]
    if weight:
        value = value + weight * (ordered[low + 1] - value)
    return value


def pool_tail_intervals(pool: Sequence[float], taus: Sequence[float], *, block: float, reps: int, seed: int) -> Dict[float, Tuple[float, float, float]]:
    """For each tau: the pool's quantile (interpolated as the model does), and the 90% percentile interval of that quantile when the pool, in the
    order given (time order), is resampled by the stationary bootstrap with mean block `block`."""

    n = len(pool)
    ordered = sorted(pool)
    rng = random.Random(seed)
    draws: Dict[float, List[float]] = {t: [] for t in taus}
    for _ in range(reps):
        resample = sorted(pool[i] for i in stationary_indices(n, block, rng))
        for t in taus:
            draws[t].append(quantile_of_sorted(resample, t))
    out = {}
    for t in taus:
        lo, hi = interval_of(draws[t])
        out[t] = (quantile_of_sorted(ordered, t), lo, hi)
    return out


# -- paths ----------------------------------------------------------------------------------------------------------------------


def information_changed(before: Mapping[str, float], after: Mapping[str, float], tolerance: float = 1e-9) -> bool:
    """Whether the settlement flags and sizes a forecast read differ between two steps."""

    keys = set(before) | set(after)
    return any(abs(float(before.get(k, 0.0)) - float(after.get(k, 0.0))) > tolerance for k in keys)


def misplaced(early_error: float, late_error: float, keep: float = 0.8) -> bool:
    """The error at h = 1 keeps the sign and at least `keep` of the size of the error at h = 5."""

    if early_error == 0.0 or late_error == 0.0:
        return False
    return (early_error > 0) == (late_error > 0) and abs(late_error) >= keep * abs(early_error)


def mean_ci(values: Sequence[float], clusters: Optional[Sequence] = None, *, reps: int = EVENT_REPS, seed: int = SEED) -> Tuple[float, float, float]:
    """The mean and its 90% percentile interval: whole clusters resampled iid when `clusters` is given, else the stationary bootstrap (mean block
    `BLOCK`) in the order given."""

    n = len(values)
    if n == 0:
        return (float("nan"),) * 3
    mean = sum(values) / n
    rng = random.Random(seed)
    if clusters is not None:
        groups: Dict = defaultdict(list)
        for v, c in zip(values, clusters):
            groups[c].append(v)
        parts = [groups[k] for k in sorted(groups, key=str)]
        draws = []
        for _ in range(reps):
            picked = [v for i in (rng.randrange(len(parts)) for _ in parts) for v in parts[i]]
            draws.append(sum(picked) / len(picked))
    else:
        draws = [sum(values[i] for i in stationary_indices(n, BLOCK, rng)) / n for _ in range(reps)]
    lo, hi = interval_of(draws)
    return mean, lo, hi


# -- the same forecasts ---------------------------------------------------------------------------------------------------------


def verify_walk(path: Path, window: str, record: Mapping[str, object], *, refits: int) -> str:
    """The sha256 of the walk file and its refit count against the 1363 record's `walk_files`; raises `ValueError` on a difference."""

    declared = record["walk_files"][window]
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != declared["sha256"]:
        raise ValueError(f"{window}: the regenerated walk has sha256 {digest}, the 1363 record has {declared['sha256']}")
    if refits != declared["refits"]:
        raise ValueError(f"{window}: the regenerated walk refits {refits} times, the 1363 record {declared['refits']}")
    return digest


def wrap_walk(function: Callable, seen: list) -> Callable:
    """`function` that also appends (result, args, kwargs) of each call to `seen` and returns the result untouched."""

    def wrapped(*args, **kwargs):
        result = function(*args, **kwargs)
        seen.append((result, args, kwargs))
        return result

    return wrapped


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def day_meta_of(panel, splits) -> Dict[str, list]:
    """For every panel day: its regime, its pressure-day type (turn_days.turn_day_type with the panel's tax_date column) and its quarter-end event id."""

    out = {}
    for row in panel:
        try:
            regime = splits.regime(row.date)
        except ValueError:
            regime = ZERO_BEFORE
        kind = turn_days.turn_day_type(row.date, tax_date=float(row.values["tax_date"]) == 1.0)
        out[row.date.isoformat()] = [regime, kind, quarter_end_event(row.date) if kind in EVENT_TYPES else None]
    return out


def walk_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    committed_declaration()
    from repo_model import s3c_announced
    from repo_model import spread_mr_state_calendar as sc

    m1363 = _load("candidate_calibration_1363", "candidate_calibration_1363_in_1533")
    record = json.loads(RECORD_1363.read_text(encoding="utf-8"))
    seen: list = []
    original = sc.walk
    sc.walk = wrap_walk(original, seen)
    try:
        m1363.walk_command(argparse.Namespace(panel=args.panel, window=args.window, output=args.output, first=None))
    finally:
        sc.walk = original
    from repo_model import s3c_announced as announced

    mine = [call for call in seen if announced.ANN_NET_ARM.name in call[0].forecasts]
    if len(mine) != 1:
        raise ValueError(f"expected one call of spread_mr_state_calendar.walk for the candidate's arm, found {len(mine)} of {len(seen)}")
    walk, call_args, call_kwargs = mine[0]
    digest = verify_walk(Path(args.output), args.window, record, refits=len(walk.fits))
    doc = json.loads(Path(args.output).read_text(encoding="utf-8"))
    panel, _days, both = call_args[0], call_args[1], call_args[2]
    sizes, registry, decision_time, splits = call_kwargs["sizes"], call_kwargs["registry"], call_kwargs["decision_time"], call_kwargs["splits"]
    dates = [row.date for row in panel]
    refuse_beyond(dates, EXPLORATORY_END)
    position = {d.isoformat(): i for i, d in enumerate(dates)}
    arm = s3c_announced.ANN_NET_ARM.name
    cap = sc.MAX_ITERATIONS
    refits = []
    for day in sorted(walk.estimates):
        per_h = {}
        for h, est in walk.estimates[day][arm].items():
            per_h[str(h)] = {
                "effect": dict(est.effect), "slope": dict(est.slope), "flagged": dict(est.flagged), "pairs": est.pairs,
                "unknown_state": est.unknown_state, "iterations": est.iterations, "cap_hit": est.iterations >= cap,
                "origins": list(est.origins), "targets": list(est.targets), "residuals": list(est.residuals),
            }
        refits.append({"date": day.isoformat(), "fitted_on": walk.fits[day].fitted_on.isoformat(), "h": per_h})
    raw, info = [], []
    for d, h, _t in doc["cells"]:
        day = date.fromisoformat(d)
        idx = position[d]
        raw.append(list(walk.forecasts[arm][day][h]))
        read = {k: v for k, v in both.read(h, idx).items() if k.startswith("settlement")}
        read.update(sizes.read(h, idx))
        info.append(read)
    decisions = {}
    for day in sorted(walk.detail):
        idx = position[day.isoformat()]
        anchor = pb._anchor(panel, idx, registry, decision_time)
        decisions[day.isoformat()] = {"anchor": dates[anchor].isoformat(), "last": panel[anchor].spread_bps, "scale": walk.detail[day]["scale"]}
    ext = {
        "window": args.window, "walk_sha256": digest, "walk_refits": len(walk.fits), "max_iterations": cap, "refits": refits,
        "day_meta": day_meta_of(panel, splits), "raw": raw, "info": info, "decisions": decisions,
    }
    Path(args.extension).parent.mkdir(parents=True, exist_ok=True)
    Path(args.extension).write_text(json.dumps(ext, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{args.window}: walk sha256 {digest} equals the 1363 record; wrote {args.extension} ({len(refits)} refits)")
    return 0


# -- the cells -------------------------------------------------------------------------------------------------------------------

#: The metrics of one cell, in this order (the vector `cell_vector` returns).
METRIC_NAMES = (
    "cov90", "cov98", "miss_q05_low", "miss_q95_up", "miss_q01_low", "miss_q99_up",
    "weak_q05_low", "weak_q95_up", "weak_q01_low", "weak_q99_up",
    "crps", "twcrps", "dcrps_B1p", "dcrps_B2", "dtw_B1p", "dtw_B2",
)
G = {tau: GRID.index(tau) for tau in (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)}


def cell_vector(q: Sequence[float], y: float, b1p: Sequence[float], b2: Sequence[float]) -> List[float]:
    """The sixteen numbers one cell contributes: band coverage, strict and weak tail misses, the candidate's scores and the paired differences."""

    c, t = sp.grid_crps(q, y), sp.upper_tail_twcrps(q, y)
    return [
        float(q[G[0.05]] <= y <= q[G[0.95]]), float(q[G[0.01]] <= y <= q[G[0.99]]),
        float(y < q[G[0.05]]), float(y > q[G[0.95]]), float(y < q[G[0.01]]), float(y > q[G[0.99]]),
        float(y <= q[G[0.05]]), float(y >= q[G[0.95]]), float(y <= q[G[0.01]]), float(y >= q[G[0.99]]),
        c, t, c - sp.grid_crps(b1p, y), c - sp.grid_crps(b2, y), t - sp.upper_tail_twcrps(b1p, y), t - sp.upper_tail_twcrps(b2, y),
    ]


class Window:
    """One window's cells with everything the three items read."""

    def __init__(self, name: str, doc: dict, ext: dict):
        self.name, self.doc, self.ext = name, doc, ext
        refuse_beyond([date.fromisoformat(c[2]) for c in doc["cells"]] + [date.fromisoformat(c[0]) for c in doc["cells"]], WINDOW_LAST[name])
        if ext["walk_sha256"] is None:
            raise ValueError("the extension names no walk")
        self.calendar = doc["calendar"]
        self.refit_dates = [r["date"] for r in ext["refits"]]
        self.models = doc["models"]
        self.cells: List[dict] = []
        for i, (d, h, t) in enumerate(doc["cells"]):
            meta = doc["targets"][t]
            kind = meta["pressure"]
            event = ext["day_meta"][t][2] if kind in EVENT_TYPES else None
            if kind in EVENT_TYPES and event is None:
                raise ValueError(f"{t} is {kind} in the 1363 walk and has no quarter-end event here")
            fit = self.refit_dates[bisect.bisect_right(self.refit_dates, d) - 1]
            cell = {
                "i": i, "d": d, "h": h, "t": t, "y": doc["outcome"][t], "q": self.models[CANDIDATE][i], "raw": ext["raw"][i], "info": ext["info"][i],
                "pressure": kind, "regime": meta["regime"], "event": event, "fit": fit,
            }
            cell["vec"] = cell_vector(cell["q"], cell["y"], self.models["B1_prime"][i], self.models["B2"][i])
            self.cells.append(cell)
        self.event_regime = {}
        for c in self.cells:
            if c["event"] is not None:
                self.event_regime.setdefault(c["event"], c["regime"])

    def group(self) -> List[dict]:
        return [c for c in self.cells if c["event"] is not None]

    def rest(self) -> List[dict]:
        return [c for c in self.cells if c["event"] is None]


def mean_vec(cells: Sequence[dict]) -> List[float]:
    n = len(cells)
    return [sum(c["vec"][m] for c in cells) / n for m in range(len(METRIC_NAMES))] if n else [float("nan")] * len(METRIC_NAMES)


def target_series(cells: Sequence[dict]) -> Tuple[List[str], List[List[float]]]:
    """The metrics as series in target-day order: the mean of the cells that target each day."""

    by_day: Dict[str, List[dict]] = defaultdict(list)
    for c in cells:
        by_day[c["t"]].append(c)
    days = sorted(by_day)
    return days, [mean_vec(by_day[t]) for t in days]


def stationary_means(cells: Sequence[dict], metric_ids: Sequence[int], *, reps: int, seed: int) -> List[Tuple[float, float]]:
    """90% stationary-bootstrap intervals (mean block 10, target-day series, the current method of #1363) of the pooled metric means."""

    days, rows = target_series(cells)
    if len(days) < 2:
        return [(float("nan"), float("nan"))] * len(metric_ids)
    columns = [[r[m] for r in rows] for m in metric_ids]
    n = len(days)

    def statistic(indices):
        return [sum(map(col.__getitem__, indices)) / n for col in columns]

    return [tuple(x) for x in metrics.stationary_bootstrap_intervals(statistic, n, block_length=BLOCK, seed=seed, replications=reps, level=LEVEL)]


# -- item 1: event influence ------------------------------------------------------------------------------------------------------


def figure_row(cells: Sequence[dict], *, clustered: bool, reps: int) -> dict:
    """The sixteen means of `cells` with a 90% interval each: whole events resampled when `clustered`, the stationary bootstrap otherwise."""

    values = mean_vec(cells)
    ids = list(range(len(METRIC_NAMES)))
    if not cells:
        return {"n": 0}
    if clustered:
        events = sorted({c["event"] for c in cells}, key=str)
        by = {e: [c for c in cells if c["event"] == e] for e in events}
        sums = [[sum(c["vec"][m] for c in by[e]) for m in ids] for e in events]
        intervals = event_mean_intervals(sums, [len(by[e]) for e in events], reps=reps, seed=SEED)
    else:
        intervals = stationary_means(cells, ids, reps=reps, seed=SEED)
    return {"n": len(cells), "events": len({c["event"] for c in cells if c["event"]}) if clustered else None,
            "mean": dict(zip(METRIC_NAMES, values)), "interval": {k: list(v) for k, v in zip(METRIC_NAMES, intervals)}}


KEY_FOR_LOO = ("cov90", "cov98", "miss_q05_low", "miss_q95_up", "miss_q01_low", "miss_q99_up", "crps", "twcrps", "dcrps_B1p", "dcrps_B2")


def influence(cells: Sequence[dict]) -> dict:
    """The leave-one-event-out range of the key metrics over the event cells `cells`, with the event at each end, and the greedy drop of three."""

    out = {}
    for name in KEY_FOR_LOO:
        m = METRIC_NAMES.index(name)

        def stat(sub, m=m):
            return sum(c["vec"][m] for c in sub) / len(sub)

        loo = leave_one_out(cells, key=lambda c: c["event"], statistic=stat)
        loo.pop("values")
        out[name] = loo
    m = METRIC_NAMES.index("cov90")
    out["drop3_cov90"] = greedy_drop(cells, key=lambda c: c["event"], statistic=lambda sub: sum(c["vec"][m] for c in sub) / len(sub), count=3)
    return out


def influence_of_all(window: Window) -> dict:
    """Leave each event out of the summaries over ALL cells (the event's cells removed, every other cell kept), by metric, pooled and by h."""

    out = {}
    group = window.group()
    events = sorted({c["event"] for c in group}, key=str)
    for label, hh in [("pooled", None)] + [(f"h{h}", h) for h in LEADS]:
        cells = [c for c in window.cells if hh is None or c["h"] == hh]
        sums = [sum(c["vec"][m] for c in cells) for m in range(len(METRIC_NAMES))]
        n = len(cells)
        per = {}
        for e in events:
            sub = [c for c in cells if c["event"] == e]
            per[e] = [(sums[m] - sum(c["vec"][m] for c in sub)) / (n - len(sub)) for m in range(len(METRIC_NAMES))]
        entry = {}
        for name in KEY_FOR_LOO:
            m = METRIC_NAMES.index(name)
            lo = min(events, key=lambda e: (per[e][m], e))
            hi = max(events, key=lambda e: (per[e][m], e))
            entry[name] = {"full": sums[m] / n, "min": per[lo][m], "min_event": lo, "max": per[hi][m], "max_event": hi}
        out[label] = entry
    return out


def event_table(window: Window) -> List[dict]:
    rows = []
    for e in sorted({c["event"] for c in window.group()}):
        cells = [c for c in window.group() if c["event"] == e]
        mv = dict(zip(METRIC_NAMES, mean_vec(cells)))
        rows.append({"event": e, "regime": window.event_regime[e], "labels": sorted({c["pressure"] for c in cells}), "n": len(cells), **mv})
    return rows


def item1(window: Window, reps: int) -> dict:
    group = window.group()
    out: dict = {"events": len({c["event"] for c in group}), "cells_in_group": len(group), "cells": len(window.cells)}
    out["group"] = {"pooled": figure_row(group, clustered=True, reps=reps), "by_h": {str(h): figure_row([c for c in group if c["h"] == h], clustered=True, reps=reps) for h in LEADS}}
    out["rest"] = {"pooled": figure_row(window.rest(), clustered=False, reps=reps), "by_h": {str(h): figure_row([c for c in window.rest() if c["h"] == h], clustered=False, reps=reps) for h in LEADS}}
    out["all"] = {"pooled": figure_row(window.cells, clustered=False, reps=reps)}
    out["leave_one_out_group"] = {"pooled": influence(group), "by_h": {str(h): influence([c for c in group if c["h"] == h]) for h in LEADS}}
    out["leave_one_out_all"] = influence_of_all(window)
    out["by_pressure_type"] = {k: figure_row([c for c in window.cells if c["pressure"] == k], clustered=k in EVENT_TYPES, reps=reps) for k in PRESSURE_TYPES}
    regimes = sorted({c["regime"] for c in window.cells})
    out["by_regime_group"] = {r: figure_row([c for c in group if c["regime"] == r], clustered=True, reps=reps) for r in regimes if any(c["regime"] == r for c in group)}
    out["by_regime_rest"] = {r: figure_row([c for c in window.rest() if c["regime"] == r], clustered=False, reps=reps) for r in regimes if any(c["regime"] == r for c in window.rest())}
    out["events_table"] = event_table(window)
    shortfall = [e for e in out["events_table"] if e["cov90"] < 0.9 - 1.0 / e["n"]]
    out["events_below_nominal"] = {"count": len(shortfall), "of": len(out["events_table"]), "share": len(shortfall) / len(out["events_table"])}
    total = sum(e["crps"] * e["n"] for e in out["events_table"])
    total_tw = sum(e["twcrps"] * e["n"] for e in out["events_table"])
    ranked = sorted(out["events_table"], key=lambda e: -e["crps"] * e["n"])
    ranked_tw = sorted(out["events_table"], key=lambda e: -e["twcrps"] * e["n"])
    out["concentration"] = {
        "top3_crps_events": [e["event"] for e in ranked[:3]], "top3_crps_share": sum(e["crps"] * e["n"] for e in ranked[:3]) / total,
        "top3_twcrps_events": [e["event"] for e in ranked_tw[:3]], "top3_twcrps_share": sum(e["twcrps"] * e["n"] for e in ranked_tw[:3]) / total_tw,
        "equal_share_of_three": 3 / len(out["events_table"]),
    }
    return out


# -- item 2: tail-support provenance ----------------------------------------------------------------------------------------------


def _pool_task(job):
    """One (refit, h): the tails of the pool and their bootstrap intervals at the primary and the sensitivity block lengths."""

    key, residuals_in_time_order, seed = job
    taus = TAILS + MIDDLE
    primary = pool_tail_intervals(residuals_in_time_order, taus, block=BLOCK, reps=POOL_REPS, seed=seed)
    side = {str(b): pool_tail_intervals(residuals_in_time_order, TAILS, block=b, reps=POOL_REPS, seed=seed) for b in SENSITIVITY_BLOCKS}
    return key, primary, side


def member(window: Window, refit: dict, h: str, p: int) -> dict:
    """The pool member at position `p`: its dates, residual, day type, regime, event."""

    data = refit["h"][h]
    t_row, o_row = data["targets"][p], data["origins"][p]
    tdate, odate = window.calendar[t_row], window.calendar[o_row]
    regime, kind, event = window.ext["day_meta"][tdate]
    return {"target": tdate, "origin": odate, "residual": data["residuals"][p], "type": kind, "regime": regime, "event": event, "row": t_row}


def tail_rows(window: Window, used_refits: Sequence[str], workers: int) -> List[dict]:
    """Per used refit, h and tail: the setters, neighbours and zone, with their types, regimes and distinct events, ages and bootstrap intervals."""

    by_date = {r["date"]: r for r in window.ext["refits"]}
    jobs, shapes = [], {}
    for rd in used_refits:
        refit = by_date[rd]
        for h, data in refit["h"].items():
            order = sorted(range(len(data["targets"])), key=lambda p: (data["targets"][p], p))
            jobs.append(((rd, h), [data["residuals"][p] for p in order], SEED))
            shapes[(rd, h)] = order
    if workers > 1:
        with Pool(workers) as pool:
            results = pool.map(_pool_task, jobs, chunksize=4)
    else:
        results = [_pool_task(j) for j in jobs]
    boots = {k: (p, s) for k, p, s in results}
    rows = []
    for rd in used_refits:
        refit = by_date[rd]
        refit_row = window.calendar.index(rd) if rd in window.calendar else None
        refit_regime = window.ext["day_meta"][rd][0]
        for h in sorted(refit["h"], key=int):
            data = refit["h"][h]
            residuals = data["residuals"]
            n = len(residuals)
            order = rank_order(residuals)
            targets_sorted = sorted(data["targets"])
            ages = [refit_row - r for r in data["targets"]] if refit_row is not None else []
            kinds = [window.ext["day_meta"][window.calendar[r]] for r in data["targets"]]
            pool_qe = sum(1 for k in kinds if k[2] is not None) / n
            qe_res = [residuals[p] for p, k in enumerate(kinds) if k[2] is not None]
            primary, side = boots[(rd, h)]
            for tau in TAILS:
                setters = [member(window, refit, h, order[r]) | {"rank": r} for r in setter_ranks(n, tau)]
                neighbours = [member(window, refit, h, order[r]) | {"rank": r} for r in neighbour_ranks(n, tau)]
                zone = [order[r] for r in zone_ranks(n, tau)]
                zone_kinds = [kinds[p] for p in zone]
                zone_rows = [data["targets"][p] for p in zone]
                near = setters + neighbours
                pctl = []
                for m in near:
                    older = sum(1 for t in data["targets"] if t < m["row"])
                    pctl.append(older / n)  # share of pool members that are older (earlier target) than the member
                est, lo, hi = primary[tau]
                rows.append({
                    "refit": rd, "h": int(h), "tau": tau, "pool": n, "quantile": est, "ci": [lo, hi],
                    "ci_block5": list(side[str(SENSITIVITY_BLOCKS[0])][tau][1:]), "ci_block20": list(side[str(SENSITIVITY_BLOCKS[1])][tau][1:]),
                    "setters": [{k: v for k, v in m.items() if k != "row"} for m in setters],
                    "neighbours": [{k: v for k, v in m.items() if k != "row"} for m in neighbours],
                    "setter_near_qe": sum(1 for m in near if m["event"] is not None), "setter_near_n": len(near),
                    "setter_near_events": distinct_clusters([m["row"] for m in near], CLUSTER_GAP, [m["event"] for m in near]),
                    "setter_older_share": sum(pctl) / len(pctl),
                    "zone_n": len(zone), "zone_qe": sum(1 for k in zone_kinds if k[2] is not None),
                    "zone_events": distinct_clusters(zone_rows, CLUSTER_GAP, [k[2] for k in zone_kinds]),
                    "zone_other_regime": sum(1 for k in zone_kinds if k[0] != refit_regime) / max(1, len(zone)),
                    "pool_other_regime": sum(1 for k in kinds if k[0] != refit_regime) / n,
                    "pool_qe_share": pool_qe,
                    "mid_ci": {str(t): [primary[t][0], primary[t][1], primary[t][2]] for t in MIDDLE},
                    "iterations": data["iterations"], "cap_hit": data["cap_hit"],
                    "rms_ratio_qe": (math.sqrt(sum(x * x for x in qe_res) / len(qe_res)) / math.sqrt(sum(x * x for x in residuals) / n)) if qe_res else None,
                })
    return rows


def median(xs: Sequence[float]) -> float:
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return float("nan")
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def spread_of(xs: Sequence[float]) -> List[float]:
    xs = sorted(xs)
    return [xs[0], percentile(xs, 0.25), median(xs), percentile(xs, 0.75), xs[-1]] if xs else []


def item2(window: Window, rows: Sequence[dict]) -> dict:
    """The tail-support summaries over the refits in force on the window's scored days, and for the group's cells."""

    out: dict = {"refits_used": len({r["refit"] for r in rows})}
    by = defaultdict(list)
    for r in rows:
        by[(r["h"], r["tau"])].append(r)
    summary = {}
    for (h, tau), rs in sorted(by.items()):
        iqr = [r["mid_ci"]["0.75"][0] - r["mid_ci"]["0.25"][0] for r in rs]
        width = [r["ci"][1] - r["ci"][0] for r in rs]
        mid_width = [r["mid_ci"]["0.5"][2] - r["mid_ci"]["0.5"][1] for r in rs]
        summary[f"h{h}/tau{tau}"] = {
            "refits": len(rs), "pool_median": median([r["pool"] for r in rs]),
            "ci_width_median": median(width), "ci_width_over_iqr": median([w / i for w, i in zip(width, iqr)]),
            "median_ci_width_for_median": median(mid_width),
            "ci_width_block5": median([r["ci_block5"][1] - r["ci_block5"][0] for r in rs]),
            "ci_width_block20": median([r["ci_block20"][1] - r["ci_block20"][0] for r in rs]),
            "zone_n_median": median([r["zone_n"] for r in rs]), "zone_events_median": median([r["zone_events"] for r in rs]),
            "zone_events_range": [min(r["zone_events"] for r in rs), max(r["zone_events"] for r in rs)],
            "zone_qe_share_mean": sum(r["zone_qe"] / r["zone_n"] for r in rs) / len(rs),
            "pool_qe_share_mean": sum(r["pool_qe_share"] for r in rs) / len(rs),
            "setter_near_qe_share_mean": sum(r["setter_near_qe"] / r["setter_near_n"] for r in rs) / len(rs),
            "setter_near_events_median": median([r["setter_near_events"] for r in rs]),
            "setter_older_share_mean": sum(r["setter_older_share"] for r in rs) / len(rs),
            "zone_other_regime_mean": sum(r["zone_other_regime"] for r in rs) / len(rs),
            "pool_other_regime_mean": sum(r["pool_other_regime"] for r in rs) / len(rs),
        }
    out["summary"] = summary
    iters = [(r["h"], r["iterations"], r["cap_hit"]) for r in rows if r["tau"] == TAILS[0]]
    out["huber"] = {"fits": len(iters), "cap_hit": sum(1 for _h, _i, c in iters if c), "median_iterations": median([i for _h, i, _c in iters]),
                    "max_iterations": max(i for _h, i, _c in iters),
                    "by_h": {str(h): {"fits": sum(1 for x in iters if x[0] == h), "cap_hit": sum(1 for x in iters if x[0] == h and x[2])} for h in LEADS}}
    rms = defaultdict(list)
    for r in rows:
        if r["tau"] == TAILS[0] and r["rms_ratio_qe"] is not None:
            rms[r["h"]].append(r["rms_ratio_qe"])
    out["pool_composition"] = {str(h): {"rms_ratio_qe_median": median(v), "range": [min(v), max(v)]} for h, v in sorted(rms.items())}
    # the group's cells: the tail rows of the refit in force at the decision and the lead
    index = {(r["refit"], r["h"], r["tau"]): r for r in rows}
    group = window.group()
    cell_rows = defaultdict(list)
    for c in group:
        for tau in TAILS:
            r = index.get((c["fit"], c["h"], tau))
            if r is not None:
                cell_rows[tau].append((c, r))
    cells = {}
    for tau, pairs in sorted(cell_rows.items()):
        shares = [r["setter_near_qe"] / r["setter_near_n"] for _c, r in pairs]
        events = [c["event"] for c, _r in pairs]
        zshare = [r["zone_qe"] / r["zone_n"] for _c, r in pairs]
        enrich = [(r["zone_qe"] / r["zone_n"]) / r["pool_qe_share"] if r["pool_qe_share"] else float("nan") for _c, r in pairs]
        ordinary_majority = [s < 0.5 for s in shares]
        cells[str(tau)] = {
            "cells": len(pairs), "pool_median": median([r["pool"] for _c, r in pairs]), "pool_min": min(r["pool"] for _c, r in pairs),
            "setter_near_qe_share": mean_ci(shares, clusters=events, reps=1000),
            "median_setter_near_qe_share": median(shares),
            "share_of_cells_with_ordinary_majority": sum(ordinary_majority) / len(ordinary_majority),
            "zone_qe_share": mean_ci(zshare, clusters=events, reps=1000),
            "pool_qe_share": sum(r["pool_qe_share"] for _c, r in pairs) / len(pairs),
            "zone_enrichment": mean_ci([e for e in enrich if e == e], clusters=[ev for ev, e in zip(events, enrich) if e == e], reps=1000),
            "zone_events_median": median([r["zone_events"] for _c, r in pairs]),
            "setter_older_share": sum(r["setter_older_share"] for _c, r in pairs) / len(pairs),
            "ci_width_over_iqr": median([(r["ci"][1] - r["ci"][0]) / (r["mid_ci"]["0.75"][0] - r["mid_ci"]["0.25"][0]) for _c, r in pairs]),
            "ci_width_bp": mean_ci([(r["ci"][1] - r["ci"][0]) * window.ext["decisions"][c["d"]]["scale"] for c, r in pairs], clusters=events, reps=1000),
            "by_h": {str(h): {"cells": sum(1 for c, _r in pairs if c["h"] == h),
                              "median_setter_near_qe_share": median([r["setter_near_qe"] / r["setter_near_n"] for c, r in pairs if c["h"] == h])} for h in LEADS},
        }
    out["group_cells"] = cells
    out["cap"] = {name: {"clipped": sum(1 for c in group if c["q"][G[tau]] != c["raw"][G[tau]]), "cells": len(group)}
                  for name, tau in (("q95", 0.95), ("q99", 0.99), ("q05", 0.05), ("q01", 0.01))}
    out["cap_rest"] = {"clipped_q99": sum(1 for c in window.rest() if c["q"][G[0.99]] != c["raw"][G[0.99]]), "cells": len(window.rest())}
    return out


def quantile_list(xs: Sequence[float], tau: float) -> float:
    return quantile_of_sorted(sorted(xs), tau)


SHAPE_LEVELS = (0.01, 0.05, 0.25, 0.75, 0.95, 0.99)


def shape_ratios(cells: Sequence[dict]) -> dict:
    """The realised quantiles of z = (y - q50)/(q95 - q05) (raw quantiles) against the forecast law's, as ratios of the distance from the median."""

    usable = [c for c in cells if c["raw"][G[0.95]] > c["raw"][G[0.05]]]
    z = [(c["y"] - c["raw"][G[0.5]]) / (c["raw"][G[0.95]] - c["raw"][G[0.05]]) for c in usable]
    law = {tau: sum((c["raw"][G[tau]] - c["raw"][G[0.5]]) / (c["raw"][G[0.95]] - c["raw"][G[0.05]]) for c in usable) / len(usable) for tau in SHAPE_LEVELS}
    med = quantile_list(z, 0.5)
    out = {"cells": len(usable), "dropped": len(cells) - len(usable), "median_z": med, "law": law, "realised": {}, "ratio": {}}
    for tau in SHAPE_LEVELS:
        r = quantile_list(z, tau) - med
        out["realised"][str(tau)] = r
        out["ratio"][str(tau)] = r / law[tau]
    return out


def shape_interval(cells: Sequence[dict], *, clustered: bool, reps: int) -> dict:
    """`shape_ratios` with a 90% interval of the median shift and of each ratio: whole events (clustered) or stationary blocks of target days."""

    base = shape_ratios(cells)
    rng = random.Random(SEED)
    draws = {"median_z": []} | {str(t): [] for t in SHAPE_LEVELS}
    if clustered:
        events = sorted({c["event"] for c in cells}, key=str)
        by = {e: [c for c in cells if c["event"] == e] for e in events}
        for _ in range(reps):
            picked = [c for e in (events[rng.randrange(len(events))] for _ in events) for c in by[e]]
            s = shape_ratios(picked)
            draws["median_z"].append(s["median_z"])
            for t in SHAPE_LEVELS:
                draws[str(t)].append(s["ratio"][str(t)])
    else:
        days = sorted({c["t"] for c in cells})
        by_day: Dict[str, List[dict]] = defaultdict(list)
        for c in cells:
            by_day[c["t"]].append(c)
        for _ in range(reps):
            picked = [c for i in stationary_indices(len(days), BLOCK, rng) for c in by_day[days[i]]]
            s = shape_ratios(picked)
            draws["median_z"].append(s["median_z"])
            for t in SHAPE_LEVELS:
                draws[str(t)].append(s["ratio"][str(t)])
    base["interval"] = {k: list(interval_of(v)) for k, v in draws.items()}
    return base


def item2b(window: Window, reps: int) -> dict:
    group = window.group()
    out = {"group": shape_interval(group, clustered=True, reps=reps)}
    out["control_ordinary"] = shape_interval([c for c in window.cells if c["pressure"] == turn_days.ORDINARY], clustered=False, reps=max(100, reps // 4))
    out["by_regime"] = {}
    for r in sorted({c["regime"] for c in group}):
        sub = [c for c in group if c["regime"] == r]
        out["by_regime"][r] = {"events": len({c["event"] for c in sub}), **shape_ratios(sub)}
    out["by_h"] = {str(h): {"events": len({c["event"] for c in group}), **shape_ratios([c for c in group if c["h"] == h])} for h in LEADS}
    out["by_label"] = {k: {"events": len({c["event"] for c in group if c["pressure"] == k}), **shape_ratios([c for c in group if c["pressure"] == k])} for k in EVENT_TYPES}
    return out


# -- item 3: same-target paths -----------------------------------------------------------------------------------------------------


def paths(window: Window) -> List[dict]:
    """For each target day with all five leads: the path h = 5 to 1."""

    by_t: Dict[str, Dict[int, dict]] = defaultdict(dict)
    for c in window.cells:
        by_t[c["t"]][c["h"]] = c
    out = []
    for t in sorted(by_t):
        cells = by_t[t]
        if set(cells) != set(LEADS):
            continue
        steps, previous = [], None
        for h in sorted(LEADS, reverse=True):
            c = cells[h]
            q = c["q"]
            err = c["y"] - q[G[0.5]]
            decision = window.ext["decisions"][c["d"]]
            row = {
                "h": h, "decision_day": c["d"], "median": q[G[0.5]], "q05": q[G[0.05]], "q95": q[G[0.95]], "q01": q[G[0.01]], "q99": q[G[0.99]],
                "error": err, "span": q[G[0.95]] - q[G[0.05]], "miss90": int(not (q[G[0.05]] <= c["y"] <= q[G[0.95]])), "refit": c["fit"],
                "last_public": decision["last"], "anchor": decision["anchor"],
            }
            if previous is None:
                row.update({"new_refit": None, "new_announcement": None, "new_spread": None, "last_change": None})
            else:
                row.update({
                    "new_refit": int(c["fit"] != previous["fit"]), "new_announcement": int(information_changed(previous["info"], c["info"])),
                    "new_spread": int(decision["anchor"] != previous["anchor"]), "last_change": decision["last"] - previous["last_public_value"],
                })
            steps.append(row)
            previous = {"fit": c["fit"], "info": c["info"], "anchor": decision["anchor"], "last_public_value": decision["last"]}
        out.append({"target": t, "y": cells[1]["y"], "pressure": cells[1]["pressure"], "regime": cells[1]["regime"], "event": cells[1]["event"], "path": steps})
    return out


def item3(window: Window, reps: int) -> dict:
    ps = paths(window)
    out: dict = {"targets": len(ps)}

    def abs_err(p, h):
        return abs(next(s for s in p["path"] if s["h"] == h)["error"])

    def summarise(sub: Sequence[dict], clustered: bool) -> dict:
        clusters = [p["event"] for p in sub] if clustered else None
        by_h = {}
        for h in LEADS:
            ae = [abs_err(p, h) for p in sub]
            sp_ = [next(s for s in p["path"] if s["h"] == h)["span"] for p in sub]
            miss = [next(s for s in p["path"] if s["h"] == h)["miss90"] for p in sub]
            rel = [a / s if s > 0 else 0.0 for a, s in zip(ae, sp_)]
            by_h[str(h)] = {"abs_error": mean_ci(ae, clusters, reps=reps), "abs_error_over_span": mean_ci(rel, clusters, reps=reps),
                            "miss90": mean_ci(miss, clusters, reps=reps), "span": sum(sp_) / len(sp_)}
        change = [abs_err(p, 1) - abs_err(p, 5) for p in sub]
        kept = [float(misplaced(next(s for s in p["path"] if s["h"] == 5)["error"], next(s for s in p["path"] if s["h"] == 1)["error"])) for p in sub]
        always = [float(all(s["miss90"] for s in p["path"])) for p in sub]
        return {"targets": len(sub), "events": len({p["event"] for p in sub if p["event"]}), "by_h": by_h,
                "change_5_to_1": mean_ci(change, clusters, reps=reps), "misplaced_share": mean_ci(kept, clusters, reps=reps),
                "miss_at_every_h": mean_ci(always, clusters, reps=reps)}

    group = [p for p in ps if p["event"] is not None]
    out["group"] = summarise(group, True)
    out["by_pressure_type"] = {k: summarise([p for p in ps if p["pressure"] == k], k in EVENT_TYPES) for k in PRESSURE_TYPES if any(p["pressure"] == k for p in ps)}
    out["group_by_label"] = {k: summarise([p for p in group if p["pressure"] == k], True) for k in EVENT_TYPES if any(p["pressure"] == k for p in group)}
    regimes = sorted({p["regime"] for p in ps})
    out["group_by_regime"] = {r: summarise([p for p in group if p["regime"] == r], True) for r in regimes if any(p["regime"] == r for p in group)}
    out["rest_by_regime"] = {r: summarise([p for p in ps if p["regime"] == r and p["event"] is None], False) for r in regimes if any(p["regime"] == r and p["event"] is None for p in ps)}

    def steps_of(sub: Sequence[dict]) -> dict:
        classes: Dict[str, List[float]] = defaultdict(list)
        changes: Dict[str, List[float]] = defaultdict(list)
        for p in sub:
            by = {s["h"]: s for s in p["path"]}
            for h in (4, 3, 2, 1):
                s = by[h]
                label = "both" if s["new_announcement"] and s["new_refit"] else "announcement" if s["new_announcement"] else "refit" if s["new_refit"] else "neither"
                delta = abs(s["error"]) - abs(by[h + 1]["error"])
                classes[label].append(float(delta > 0))
                changes[label].append(delta)
        return {k: {"steps": len(v), "rise_share": sum(v) / len(v), "mean_change": sum(changes[k]) / len(changes[k])} for k, v in sorted(classes.items())}

    def persistence(sub: Sequence[dict], clustered: bool) -> dict:
        """The model's absolute error minus the error of the last public spread (persistence) at h = 5 and h = 1; negative favours the model."""

        res = {}
        for h in (5, 1):
            diffs, better = [], []
            for p in sub:
                st = next(x for x in p["path"] if x["h"] == h)
                naive = abs(p["y"] - st["last_public"])
                diffs.append(abs(st["error"]) - naive)
                better.append(float(naive < abs(st["error"])))
            clusters = [p["event"] for p in sub] if clustered else None
            res[str(h)] = {"model_minus_persistence": mean_ci(diffs, clusters, reps=reps), "persistence_closer_share": mean_ci(better, clusters, reps=reps)}
        return res

    out["persistence_group"] = persistence(group, True)
    out["persistence_ordinary"] = persistence([p for p in ps if p["pressure"] == turn_days.ORDINARY], False)
    out["steps_group"] = steps_of(group)
    out["steps_rest"] = steps_of([p for p in ps if p["event"] is None])
    out["steps_group_by_h"] = {}
    for h in (4, 3, 2, 1):
        vals = []
        for p in group:
            by = {s["h"]: s for s in p["path"]}
            vals.append(abs(by[h]["error"]) - abs(by[h + 1]["error"]))
        out["steps_group_by_h"][str(h)] = {"mean_change": mean_ci(vals, [p["event"] for p in group], reps=reps)}
    # the failed events
    failed = []
    for e in sorted({p["event"] for p in group}):
        sub = [p for p in group if p["event"] == e]
        cells = [s for p in sub for s in p["path"]]
        miss = sum(s["miss90"] for s in cells)
        entry = {"event": e, "regime": sub[0]["regime"], "cells": len(cells), "miss90": miss, "targets": []}
        for p in sub:
            entry["targets"].append({"target": p["target"], "y": p["y"], "label": p["pressure"], "path": p["path"]})
        if miss * 2 >= len(cells):
            failed.append(entry)
    out["failed_events"] = failed
    out["events_total"] = len({p["event"] for p in group})
    return out


# -- score ------------------------------------------------------------------------------------------------------------------------


def load_window(name: str, walks: Path, extensions: Path, record: Mapping[str, object]) -> Optional[Window]:
    wp, ep = Path(walks) / f"{name}.json", Path(extensions) / f"{name}.json"
    if not wp.exists() or not ep.exists():
        return None
    ext = json.loads(ep.read_text(encoding="utf-8"))
    digest = hashlib.sha256(wp.read_bytes()).hexdigest()
    if digest != record["walk_files"][name]["sha256"] or ext["walk_sha256"] != digest:
        raise ValueError(f"{name}: the walk file is not the 1363 walk (sha256 {digest})")
    return Window(name, json.loads(wp.read_bytes()), ext)


def rounded(value, digits: int = 6):
    """`value` with every float rounded to `digits` places (a stored figure, not an input of any later arithmetic)."""

    if isinstance(value, float):
        return round(value, digits)
    if isinstance(value, dict):
        return {k: rounded(v, digits) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [rounded(v, digits) for v in value]
    return value


def score_command(args) -> int:
    declared = committed_declaration()
    record = json.loads(RECORD_1363.read_text(encoding="utf-8"))
    result: dict = {"issue": 1533, "declaration": "metadata/qe_diagnosis_1533.json", "label": "development, not a verdict", "seed": SEED, "block": BLOCK,
                    "sensitivity_blocks": list(SENSITIVITY_BLOCKS), "pool_reps": POOL_REPS, "event_reps": EVENT_REPS, "level": LEVEL,
                    "amendments": declared["amendments"], "walk_files": {}, "windows": {}}
    tail_out: dict = {}
    for name in WINDOWS:
        window = load_window(name, Path(args.walks), Path(args.extensions), record)
        if window is None:
            continue
        result["panel_sha256"] = window.doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": window.ext["walk_sha256"], "refits": window.ext["walk_refits"],
                                      "extension_bytes": (Path(args.extensions) / f"{name}.json").stat().st_size,
                                      "extension_sha256": hashlib.sha256((Path(args.extensions) / f"{name}.json").read_bytes()).hexdigest()}
        used = sorted({c["fit"] for c in window.cells})
        rows = tail_rows(window, used, args.workers)
        tail_out[name] = rows
        result["windows"][name] = {
            "cells": len(window.cells), "decision_days": len({c["d"] for c in window.cells}), "refits_in_force": len(used),
            "item1": item1(window, EVENT_REPS), "item2": item2(window, rows), "item2b": item2b(window, 1000), "item3": item3(window, 1000),
        }
        print(f"{name}: done")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(rounded(result), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.tail_support).write_text(json.dumps(tail_out, separators=(",", ":")) + "\n", encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk", help="regenerate the 1363 walk, check its sha256, and write the extension")
    w.add_argument("--panel", required=True)
    w.add_argument("--window", choices=WINDOWS, required=True)
    w.add_argument("--output", required=True)
    w.add_argument("--extension", required=True)
    w.set_defaults(func=walk_command)
    s = sub.add_parser("score", help="the three items from the walk files and their extensions")
    s.add_argument("--walks", required=True)
    s.add_argument("--extensions", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--tail-support", required=True)
    s.add_argument("--workers", type=int, default=4)
    s.set_defaults(func=score_command)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=lambda a: page_command(a))
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


# -- the page ---------------------------------------------------------------------------------------------------------------------


def num(x, d: int = 3) -> str:
    return "n/a" if x is None or x != x else f"{x:.{d}f}"


def ivs(a, d: int = 3) -> str:
    return "n/a" if not a or a[0] != a[0] else f"[{a[0]:.{d}f}, {a[1]:.{d}f}]"


def fig(row: Mapping[str, object], name: str, d: int = 3) -> str:
    """`mean [lo, hi]` of a metric of a figure row."""

    if not row.get("n"):
        return "n/a"
    return f"{row['mean'][name]:.{d}f} {ivs(row['interval'][name], d)}"


def mci(a, d: int = 3) -> str:
    """`mean [lo, hi]` of a `mean_ci` triple."""

    return "n/a" if not a or a[0] != a[0] else f"{a[0]:.{d}f} {ivs(a[1:], d)}"


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return out + [""]


def pct(x, d: int = 0) -> str:
    return "n/a" if x is None or x != x else f"{100 * x:.{d}f}%"


def mechanism(w: dict) -> List[str]:
    """The 'Mechanism' section, every figure read from the score."""

    i1, i2, i2b, i3 = w["item1"], w["item2"], w["item2b"], w["item3"]
    g = i1["group"]["pooled"]
    loo = i1["leave_one_out_group"]["pooled"]
    cell95, cell99 = i2["group_cells"]["0.95"], i2["group_cells"]["0.99"]
    ratio = i2b["group"]["ratio"]
    iv = i2b["group"]["interval"]
    conc = i1["concentration"]
    grp3 = i3["group"]
    ordinary3 = i3["by_pressure_type"]["ordinary"]
    stale = [i2["summary"][f"h{h}/tau{t}"]["setter_older_share_mean"] for h in LEADS for t in (0.95, 0.99)]
    other = [i2["summary"][f"h{h}/tau{t}"]["zone_other_regime_mean"] for h in LEADS for t in (0.95, 0.99)]
    pool_other = i2["summary"]["h1/tau0.95"]["pool_other_regime_mean"]
    ordinary_q95 = cell95["share_of_cells_with_ordinary_majority"]
    ordinary_q99 = cell99["share_of_cells_with_ordinary_majority"]
    shape_rule = cell95["median_setter_near_qe_share"] < 0.5 and cell99["median_setter_near_qe_share"] < 0.5
    if not shape_rule:
        raise ValueError("the Mechanism text was written for a met majority rule; the figures no longer meet it, so the text must be rewritten")
    spread = max(ratio[str(t)] for t in SHAPE_LEVELS) / min(ratio[str(t)] for t in SHAPE_LEVELS)
    lines = [
        "## Mechanism", "",
        "Development data on the development window, not a verdict. Read under the rules declared in `metadata/qe_diagnosis_1533.json` before any figure.", "",
        f"**Reading: the evidence points to a shape problem (with a location shift), not to a width problem alone. The repair it points to is, under her 9 November "
        f"ruling on `h5-family-1109`, an event-conditional distribution model in place of B. A (#1531) applies one multiplier, and the ratios of point 3 say that no single multiplier fits every level. "
        f"Stale support (C) is not supported. The evidence does not say what sets the 98% band's outer edge, because too few events support it.** "
        f"The reading rests on a majority rule declared here (see the marked question in the pull request); at q95 it is met in {pct(ordinary_q95)} of the group's cells and at q99 in {pct(ordinary_q99)}.", "",
        "The figures behind it:", "",
        f"1. **The failure recurs and sits in the upper tail.** On the quarter-end group the 90% band covers {fig(g, 'cov90')} against 0.90 and the 98% band "
        f"{fig(g, 'cov98')} against 0.98. The upper tail misses {fig(g, 'miss_q95_up')} of the time against 0.05; the lower tail {fig(g, 'miss_q05_low')}. "
        f"{i1['events_below_nominal']['count']} of {i1['events_below_nominal']['of']} events have coverage below 0.90 by more than one cell's worth. "
        f"Leaving out any one event moves the group's 90% coverage only between {num(loo['cov90']['min'])} (without {loo['cov90']['min_event']}) and "
        f"{num(loo['cov90']['max'])} (without {loo['cov90']['max_event']}); removing the three most influential reaches {num(loo['drop3_cov90'][-1]['value'])}. "
        f"Coverage is not a few events' doing. The scores are: three events ({', '.join(conc['top3_crps_events'])}) carry {pct(conc['top3_crps_share'])} of the group's "
        f"grid CRPS, against {pct(conc['equal_share_of_three'])} if events were equal.", "",
        f"2. **The tails are set by ordinary-day residuals.** Quarter-end-event targets are {pct(cell95['pool_qe_share'], 1)} of the residual pool. At q95 the members "
        f"that set the quantile and their neighbours are quarter-end targets {pct(cell95['setter_near_qe_share'][0], 1)} of the time; in {pct(ordinary_q95)} of the group's cells "
        f"most of them are ordinary-day or other-turn residuals. The tail zone beyond q95 is enriched {num(cell95['zone_enrichment'][0], 1)} times in quarter-end targets "
        f"and is still {pct(cell95['zone_qe_share'][0])} quarter-end. At q99 the setters are {pct(cell99['setter_near_qe_share'][0])} quarter-end ({pct(ordinary_q99)} of "
        f"cells have an ordinary-day majority; the declared rule, a majority at both q95 and q99 in the median cell, is "
        f"{'met' if shape_rule else 'not met'}), and the zone is {pct(cell99['zone_qe_share'][0])} quarter-end. The pool does hold the signal: the root-mean-square residual of its "
        f"quarter-end members is {num(min(v['rms_ratio_qe_median'] for v in i2['pool_composition'].values()), 2)} to {num(max(v['rms_ratio_qe_median'] for v in i2['pool_composition'].values()), 2)} times the whole pool's "
        f"(median over refits, by lead), diluted by the other members.", "",
        f"3. **One multiplier does not fit all levels.** For the group's cells z = (y - q50)/(q95 - q05), the outcome in units of the forecast's own 90% span; "
        f"the realised distance from the median over the forecast's, by level: q01 {num(ratio['0.01'], 2)}, q05 {num(ratio['0.05'], 2)}, q25 {num(ratio['0.25'], 2)}, "
        f"q75 {num(ratio['0.75'], 2)}, q95 {num(ratio['0.95'], 2)} {ivs(iv['0.95'], 2)}, q99 {num(ratio['0.99'], 2)} {ivs(iv['0.99'], 2)}. A pure width problem gives one ratio. "
        f"These differ by a factor of {num(spread, 1)} and by side, and the q95 and q99 intervals do not overlap. The realised median sits {num(i2b['group']['median_z'], 2)} span units above "
        f"the forecast median {ivs(iv['median_z'], 2)}. On ordinary-day cells, the control, the ratios are {num(i2b['control_ordinary']['ratio']['0.05'], 2)} to "
        f"{num(i2b['control_ordinary']['ratio']['0.25'], 2)} in the body and median shift {num(i2b['control_ordinary']['median_z'], 2)}.", "",
        f"4. **Support is stale only mildly, and sparse at q99.** The tail setters are about as old as a typical pool member (the share of the pool older than a setter is "
        f"{num(min(stale), 2)} to {num(max(stale), 2)}, 0.5 being typical). The share of the tail zone from another regime than the refit's is {num(min(other), 2)} to "
        f"{num(max(other), 2)} against {num(pool_other, 2)} for the pool. That is no case for C. At q99 the zone holds about {num(i2['summary']['h1/tau0.99']['zone_n_median'], 0)} members from a median of "
        f"{num(cell99['zone_events_median'], 0)} distinct events; the time-block bootstrap interval of that quantile is {num(cell99['ci_width_over_iqr'], 1)} times the interquartile interval's width, "
        f"{mci(cell99['ci_width_bp'], 1)} bp wide in the group's cells, against {mci(cell95['ci_width_bp'], 1)} bp at q95.", "",
        f"5. **The forecasts do not improve much as information arrives.** On quarter-end targets the absolute error changes by {mci(grp3['change_5_to_1'], 2)} bp from h = 5 to h = 1, "
        f"against {mci(ordinary3['change_5_to_1'], 2)} bp on ordinary targets. {pct(grp3['misplaced_share'][0])} of quarter-end targets keep the sign and at least 80% of the size of "
        f"their h = 5 error, and {pct(grp3['miss_at_every_h'][0])} miss the 90% band at every lead. Neither a refit nor a new settlement announcement shows a worsening, on "
        f"{i3['steps_group'].get('refit', {}).get('steps', 0)} refit steps and {i3['steps_group'].get('announcement', {}).get('steps', 0)} announcement steps (too few to read). At h = 1 the forecast median is no closer to the "
        f"outcome than the last public spread on quarter-end targets: the model's absolute error minus persistence's is {mci(i3['persistence_group']['1']['model_minus_persistence'], 2)} bp "
        f"(ordinary targets {mci(i3['persistence_ordinary']['1']['model_minus_persistence'], 2)}).", "",
        "**What each repair gets from this.** A (a shrunk quarter-end scale) targets the width signal of point 3 and the sparse support of point 4, and the failure that "
        "recurs (point 1); it fixes one multiplier, and the ratios say none fits every level. B (regularized quantile corrections) corrects levels one by one and would inherit the same sparse "
        "support at the outer levels. An event-conditional distribution model gives the quarter-end days their own shape and location; it is what points 2 and 3 call for. C "
        "(older or other-regime support) has no support in point 4. What the evidence cannot say: whether the outer edge (q99) is wrong in shape or only unsupported, since a median of "
        f"{num(cell99['zone_events_median'], 0)} distinct events sets it; and how much of the miss any public information could have prevented (section 3 gives the last public spread beside each path).", "",
    ]
    return lines


def page(r: dict) -> str:
    d = r["windows"]["development"]
    i1, i2, i2b, i3 = d["item1"], d["item2"], d["item2b"], d["item3"]
    out = [
        "# Quarter-end band failure of (s3c-ann-net): event influence, tail-support provenance and same-target paths (#1533)", "",
        "**Development, not a verdict.** H5, step 3 (diagnosis of the calendar-day band failure of (s3c-ann-net)). No candidate change, no lockbox day, no re-score of a "
        "published record, nothing registered. Every figure below is read from `docs/research/qe-diagnosis-1533/result.json`; the declaration is "
        "`metadata/qe_diagnosis_1533.json`, committed before any figure. Her ruling of 9 November 2026 asked for the three diagnostics together and a named mechanism.", "",
    ]
    out += mechanism(d)
    wf = r["walk_files"]["development"]
    out += [
        "## The same forecasts", "",
        "The study regenerates the walk of `scripts/candidate_calibration_1363.py` unchanged (it only keeps the `Walk` object) and refuses to go on unless the file's sha256 and refit "
        "count equal `walk_files` in `docs/research/candidate-calibration-1363/result.json`. They do, for both windows:", "",
    ]
    out += table(["window", "walk sha256", "refits", "extension sha256 (not committed)"],
                 [[w, f"`{v['sha256']}`", str(v["refits"]), f"`{v['extension_sha256'][:16]}…`"] for w, v in r["walk_files"].items()])
    out += [
        f"Published panel `{r['panel_sha256']}`. The extension holds each refit's coefficients, Huber iteration counts and residual pool, and each cell's raw (pre-cap) quantiles; it adds no "
        f"forecast. Quarter-end event: every cell whose target has pressure-day type `quarter_end_turn` or `year_end`, grouped by the quarter-end it belongs to; all five leads and both turn "
        f"days are one cluster. The development window has {i1['events']} events and {i1['cells_in_group']} cells in the group.", "",
        "## 1. Event influence", "",
        "The forecasts are fixed; each event is left out of the summaries in turn. Intervals are 90% percentile intervals: whole events resampled for the group (iid, 2,000 resamples); the "
        "stationary bootstrap of target days (mean block 10) for the rest, the current day-type method with #1221's caveat that #1228 has not ruled. Paired differences are candidate "
        "minus benchmark on the same cells; negative favours the candidate.", "",
    ]
    names = [("cov90", "90% coverage"), ("cov98", "98% coverage"), ("miss_q05_low", "miss < q05"), ("miss_q95_up", "miss > q95"), ("miss_q01_low", "miss < q01"),
             ("miss_q99_up", "miss > q99")]
    sets = [("quarter-end group", i1["group"]["pooled"]), ("all other cells", i1["rest"]["pooled"]), ("all cells", i1["all"]["pooled"])]
    out += table(["set", "cells"] + [n for _k, n in names], [[lab, str(row["n"])] + [fig(row, k) for k, _n in names] for lab, row in sets])
    out += table(["set", "grid CRPS", "twCRPS", "CRPS minus B1'", "CRPS minus B2", "twCRPS minus B1'", "twCRPS minus B2"],
                 [[lab] + [fig(row, k, 2) for k in ("crps", "twcrps", "dcrps_B1p", "dcrps_B2", "dtw_B1p", "dtw_B2")] for lab, row in sets])
    out += ["By lead, the quarter-end group:", ""]
    out += table(["h", "cells", "90% coverage", "98% coverage", "miss > q95", "miss < q05", "miss > q99", "miss < q01", "grid CRPS", "CRPS minus B1'"],
                 [[str(h), str(i1["group"]["by_h"][str(h)]["n"])] + [fig(i1["group"]["by_h"][str(h)], k, 2 if "crps" in k else 3)
                  for k in ("cov90", "cov98", "miss_q95_up", "miss_q05_low", "miss_q99_up", "miss_q01_low", "crps", "dcrps_B1p")] for h in LEADS])
    out += ["Leaving one event out (range over the left-out events, the event at each end named). This is a range, not an interval.", ""]
    rows = []
    for k, label in (("cov90", "90% coverage"), ("miss_q95_up", "miss > q95"), ("miss_q99_up", "miss > q99"), ("miss_q05_low", "miss < q05"), ("crps", "grid CRPS"),
                     ("twcrps", "twCRPS"), ("dcrps_B1p", "CRPS minus B1'"), ("dcrps_B2", "CRPS minus B2")):
        v = i1["leave_one_out_group"]["pooled"][k]
        rows.append([label, num(v["full"], 3), f"{num(v['min'], 3)} (without {v['min_event']})", f"{num(v['max'], 3)} (without {v['max_event']})"])
    out += table(["group figure, pooled over leads", "all events", "lowest", "highest"], rows)
    drops = i1["leave_one_out_group"]["pooled"]["drop3_cov90"]
    out += [f"Dropping the events that move the group's 90% coverage most, one at a time: " + ", then ".join(f"{x['event']} ({num(x['value'])})" for x in drops) + ".", ""]
    rows = []
    for h in LEADS:
        v = i1["leave_one_out_group"]["by_h"][str(h)]
        rows.append([str(h)] + [f"{num(v[k]['min'])} to {num(v[k]['max'])}" for k in ("cov90", "miss_q95_up", "miss_q99_up", "dcrps_B1p")])
    out += table(["h", "90% coverage", "miss > q95", "miss > q99", "CRPS minus B1' (group)"], rows)
    out += ["Leaving each event out of **all** cells (the other cells kept): the overall figure moves in this range.", ""]
    rows = []
    for lab in ["pooled"] + [f"h{h}" for h in LEADS]:
        v = i1["leave_one_out_all"][lab]
        rows.append([lab] + [f"{num(v[k]['min'])} to {num(v[k]['max'])}" for k in ("cov90", "cov98", "miss_q95_up", "miss_q99_up")] + [f"{num(v['crps']['min'], 3)} to {num(v['crps']['max'], 3)}"])
    out += table(["", "90% coverage", "98% coverage", "miss > q95", "miss > q99", "grid CRPS"], rows)
    c = i1["concentration"]
    out += [
        f"Concentration: the three events with the largest summed grid CRPS ({', '.join(c['top3_crps_events'])}) carry {pct(c['top3_crps_share'])} of the group's total, and the three with the "
        f"largest twCRPS ({', '.join(c['top3_twcrps_events'])}) {pct(c['top3_twcrps_share'])}; equal events would carry {pct(c['equal_share_of_three'])}.", "",
        "By pressure-day type (the group's labels are resampled by event):", "",
    ]
    out += table(["type", "cells", "90% coverage", "98% coverage", "miss > q95", "grid CRPS", "CRPS minus B1'"],
                 [[k, str(v["n"])] + [fig(v, m, 2 if "crps" in m else 3) for m in ("cov90", "cov98", "miss_q95_up", "crps", "dcrps_B1p")] for k, v in i1["by_pressure_type"].items()])
    out += ["By regime of the event (the group) and of the target (the rest):", ""]
    rows = []
    for rg in sorted(set(i1["by_regime_group"]) | set(i1["by_regime_rest"])):
        a, b = i1["by_regime_group"].get(rg), i1["by_regime_rest"].get(rg)
        rows.append([rg, str(a["events"]) if a else "", fig(a, "cov90") if a else "", fig(a, "miss_q95_up") if a else "", fig(a, "dcrps_B1p", 2) if a else "",
                     fig(b, "cov90") if b else "", fig(b, "dcrps_B1p", 2) if b else ""])
    out += table(["regime", "events", "group 90% coverage", "group miss > q95", "group CRPS minus B1'", "rest 90% coverage", "rest CRPS minus B1'"], rows)
    out += ["Per event (all five leads, both turn days):", ""]
    out += table(["event", "regime", "cells", "90% cov", "98% cov", "miss > q95", "miss < q05", "miss > q99", "grid CRPS", "minus B1'", "minus B2"],
                 [[e["event"], e["regime"], str(e["n"]), num(e["cov90"], 2), num(e["cov98"], 2), num(e["miss_q95_up"], 2), num(e["miss_q05_low"], 2), num(e["miss_q99_up"], 2),
                   num(e["crps"], 2), num(e["dcrps_B1p"], 2), num(e["dcrps_B2"], 2)] for e in i1["events_table"]])
    out += [
        "**What it informs.** Does A address a recurring failure, or is its apparent benefit dominated by a few exceptional events? The coverage failure recurs: "
        f"{i1['events_below_nominal']['count']} of {i1['events_below_nominal']['of']} events fall below 0.90 and no single event moves the group's coverage by more than "
        f"{num(max(i1['leave_one_out_group']['pooled']['cov90']['max'] - i1['leave_one_out_group']['pooled']['cov90']['full'], i1['leave_one_out_group']['pooled']['cov90']['full'] - i1['leave_one_out_group']['pooled']['cov90']['min']), 3)}. "
        "The CRPS and twCRPS are concentrated in a few events, so a benefit read from CRPS alone, on this group, can be dominated by them; a benefit read from coverage cannot. "
        "With about thirty events the intervals are wide, and the group's CRPS difference to B1' has an interval that includes zero.", "",
        "## 2. Tail-support provenance", "",
        "The candidate's quantiles are `centre + scale * (shift + pool)`: the tails are the pool's order statistics, interpolated as `protocol_benchmarks.empirical_quantiles`. "
        "For every refit in force on a scored day and every lead, `docs/research/qe-diagnosis-1533/tail-support.json` lists, for q01, q05, q95 and q99, the setters (the one or two members at the "
        "interpolated ranks), their neighbours (the ranks just outside), their dates, day types and regimes, the members of the tail zone beyond the quantile, the distinct events among them, and the "
        "time-block bootstrap interval of the quantile. The pool is the training pairs of the refit (about 500 pairs per lead at the median refit; the first refits are smaller).", "",
        "The group's cells, each read at the refit in force at its decision and its lead (intervals resample events):", "",
    ]
    rows = []
    for t in TAILS:
        v = i2["group_cells"][str(t)]
        rows.append([f"q{int(round(t * 100)):02d}", str(v["cells"]), mci(v["setter_near_qe_share"]), pct(v["share_of_cells_with_ordinary_majority"]), mci(v["zone_qe_share"]),
                     mci(v["zone_enrichment"], 1), num(v["zone_events_median"], 0), num(v["setter_older_share"], 2)])
    out += table(["tail", "cells", "setters and neighbours that are quarter-end targets", "cells with an ordinary-day majority", "tail zone that is quarter-end", "zone enrichment (x the pool's share)",
                  "distinct events in zone (median)", "share of pool older than a setter"], rows)
    out += ["The uncertainty of each tail of the pool (time-block bootstrap of the pool in target order, 500 resamples, mean block 10 declared before any figure; widths of the 90% interval, in scale units, median over refits; "
            "the same at mean blocks 5 and 20 beside):", ""]
    rows = []
    for t in TAILS:
        for h in (1, 3, 5):
            v = i2["summary"][f"h{h}/tau{t}"]
            rows.append([f"q{int(round(t * 100)):02d}", str(h), num(v["ci_width_median"], 2), num(v["ci_width_block5"], 2), num(v["ci_width_block20"], 2), num(v["ci_width_over_iqr"], 2),
                         num(v["median_ci_width_for_median"], 2), num(v["zone_n_median"], 0), num(v["zone_events_median"], 0), f"{v['zone_events_range'][0]} to {v['zone_events_range'][1]}"])
    out += table(["tail", "h", "width (block 10)", "block 5", "block 20", "x the IQR's width", "median's width", "zone members", "distinct events (median)", "range"], rows)
    gc = i2["group_cells"]
    out += ["In basis points, for the group's cells (width x the scale the forecast used): " + "; ".join(f"q{int(round(t * 100)):02d} {mci(gc[str(t)]['ci_width_bp'], 1)}" for t in TAILS) + ". "
            f"The median pool in those cells has {num(gc['0.95']['pool_median'], 0)} members (smallest {gc['0.95']['pool_min']}).", ""]
    out += ["Staleness and regime: by tail and lead (mean over refits):", ""]
    rows = []
    for t in (0.95, 0.99):
        for h in LEADS:
            v = i2["summary"][f"h{h}/tau{t}"]
            rows.append([f"q{int(round(t * 100)):02d}", str(h), pct(v["setter_near_qe_share_mean"], 1), pct(v["zone_qe_share_mean"], 1), pct(v["pool_qe_share_mean"], 1), num(v["setter_older_share_mean"], 2),
                         pct(v["zone_other_regime_mean"]), pct(v["pool_other_regime_mean"])])
    out += table(["tail", "h", "setters+neighbours quarter-end", "zone quarter-end", "pool quarter-end", "older-than-setter share", "zone from another regime", "pool from another regime"], rows)
    cp = i2["cap"]
    out += [
        f"The candidate is the pool's quantile clipped at the full-allotment line. In the group the clip changes q95 in {cp['q95']['clipped']} of {cp['q95']['cells']} cells and q99 in "
        f"{cp['q99']['clipped']}; so the group's tails are the pool's. Outside the group it changes q99 in {i2_rest(d)} cells.", "",
        "Pool composition: the root-mean-square residual of the quarter-end members over that of the whole pool (the `m_raw` of #1402), by lead, median and range over refits:", "",
    ]
    out += table(["h", "median", "range"], [[h, num(v["rms_ratio_qe_median"], 2), ivs(v["range"], 2)] for h, v in sorted(i2["pool_composition"].items())])
    hb = i2["huber"]
    out += [
        f"**Huber iterations (a fact only; the stricter replay is her item 7).** Of {hb['fits']} fits (refit x lead) in force on scored days, {hb['cap_hit']} ended at the iteration cap "
        f"of 50 (a fit that converged on exactly the last allowed iteration is counted with them); the median fit took {num(hb['median_iterations'], 0)} iterations. By lead: "
        + ", ".join(f"h = {h}: {v['cap_hit']} of {v['fits']}" for h, v in sorted(hb["by_h"].items())) + ".", "",
        "**What it informs.** Sparse support favours shrinkage or partial pooling (A-type); stale support strengthens C. The tails of the quarter-end forecasts are set by ordinary-day members, with the "
        "quarter-end members enriched in the tail zone but a minority of it; the q99 rests on a handful of members from a handful of events; the setters are not older than typical and the regime "
        "mix of the zone differs only mildly.", "",
        "## 2b. Width or shape (her docket ruling h5-family-1109)", "",
        "For the group's cells, z = (y - q50) / (q95 - q05) on the raw (pre-cap) quantiles: the outcome in units of the forecast's own 90% span. The forecast law has its own z at each level; the ratio is "
        "the realised distance from the realised median over the law's. A pure width problem has one ratio at every level and on both sides; a shape problem has ratios that change with the level or the "
        "side. Intervals resample whole events (the control, stationary blocks of target days).", "",
    ]

    def shape_rows(label: str, s: dict, with_interval: bool) -> List[str]:
        row = [label, str(s["cells"]), num(s["median_z"], 2) + (" " + ivs(s["interval"]["median_z"], 2) if with_interval else "")]
        for t in SHAPE_LEVELS:
            row.append(num(s["ratio"][str(t)], 2) + (" " + ivs(s["interval"][str(t)], 2) if with_interval else ""))
        return row

    levels = [f"q{int(round(t * 100)):02d}" for t in SHAPE_LEVELS]
    rows = [shape_rows("quarter-end group", i2b["group"], True), shape_rows("ordinary days (control)", i2b["control_ordinary"], True)]
    out += table(["set", "cells", "median z (shift)"] + levels, rows)
    out += ["The law's z by level for the group: " + ", ".join(f"{lv} {num(i2b['group']['law'][str(t)], 2)}" for lv, t in zip(levels, SHAPE_LEVELS)) + "; the realised, from the realised median: "
            + ", ".join(f"{lv} {num(i2b['group']['realised'][str(t)], 2)}" for lv, t in zip(levels, SHAPE_LEVELS)) + ".", "",
            "By regime of the event, label and lead (point values; events are few, so no interval is shown):", ""]
    rows = [shape_rows(f"{k} ({v['events']} events)", v, False) for k, v in i2b["by_regime"].items()]
    rows += [shape_rows(f"{k} ({v['events']} events)", v, False) for k, v in i2b["by_label"].items()]
    rows += [shape_rows(f"h = {k}", v, False) for k, v in i2b["by_h"].items()]
    out += table(["split", "cells", "median z (shift)"] + levels, rows)
    out += [
        "The reading is descriptive: no multiplier is fitted or scored here, about thirty events is small, and the ratios in the body are inflated by any shift in location that the median "
        "removes imperfectly.", "",
        "## 3. Same-target paths", "",
        "For each target day with all five leads, the forecast at h = 5, 4, 3, 2, 1: median, q05, q95, q01, q99 and the eventual error y - median. Each step from h + 1 to h is marked: new refit "
        "(the fit in force differs), new settlement announcement (the settlement flags or sizes the forecast read differ, from `metadata/settlement_announcement_dating.json` as served by "
        "`repo_model.s3c_announced`), new spread (always one panel day). The full paths of every quarter-end target are in `result.json` (`item3.failed_events` for the failed events).", "",
    ]

    def path_rows(label, v):
        return [[label, str(v["targets"])] + [mci(v["by_h"][str(h)]["abs_error"], 2) for h in (5, 3, 1)] + [mci(v["by_h"][str(h)]["miss90"], 2) for h in (5, 1)]
                + [mci(v["change_5_to_1"], 2), mci(v["misplaced_share"], 2), mci(v["miss_at_every_h"], 2)]]

    rows = path_rows("quarter-end group", i3["group"])
    for k, v in i3["by_pressure_type"].items():
        if k not in EVENT_TYPES:
            rows += path_rows(k, v)
    for k, v in i3["group_by_label"].items():
        rows += path_rows(f"  {k}", v)
    for k, v in i3["group_by_regime"].items():
        rows += path_rows(f"  group, {k} ({v['events']} events)", v)
    for k, v in i3["rest_by_regime"].items():
        rows += path_rows(f"  non-event, {k}", v)
    out += table(["targets", "n", "mean |error| h=5", "h=3", "h=1", "90% miss h=5", "h=1", "|error| h=1 minus h=5", "keeps sign and 80% of size", "misses at every h"], rows)
    out += ["How a step changes the absolute error, by what the step brought (group first, then every other target):", ""]
    rows = []
    for lab, steps in (("quarter-end group", i3["steps_group"]), ("other targets", i3["steps_rest"])):
        for k in ("neither", "refit", "announcement", "both"):
            if k in steps:
                v = steps[k]
                rows.append([lab, k, str(v["steps"]), pct(v["rise_share"]), num(v["mean_change"], 3)])
    out += table(["set", "the step brought", "steps", "share where |error| rises", "mean change (bp)"], rows)
    out += ["By step, the group's mean change of |error| (h + 1 to h): " + "; ".join(f"to h = {h}: {mci(v['mean_change'], 2)}" for h, v in sorted(i3["steps_group_by_h"].items(), reverse=True)) + ".", ""]
    out += [f"Failed events (at least half of the cells outside the closed 90% band): {len(i3['failed_events'])} of {i3['events_total']}. The path of each target, as error at h = 5, 4, 3, 2, 1 in bp "
            "(`*` marks a miss of the 90% band; `R` a new refit, `A` a new settlement announcement on that step):", ""]
    rows = []
    for e in i3["failed_events"]:
        for t in e["targets"]:
            cells = []
            for s in sorted(t["path"], key=lambda s: -s["h"]):
                mark = ("*" if s["miss90"] else "") + ("R" if s["new_refit"] else "") + ("A" if s["new_announcement"] else "")
                cells.append(f"{s['error']:+.1f}{mark}")
            rows.append([e["event"], e["regime"], t["target"], t["label"], f"{t['y']:.0f}"] + cells + [f"{t['path'][-1]['last_public']:.0f}"])
    out += table(["event", "regime", "target", "label", "outcome", "h=5", "h=4", "h=3", "h=2", "h=1", "last public spread at h=1"], rows)
    out += [
        "**What it informs.** Whether the forecasts improve as information arrives, stay misplaced, or worsen after one update; the tables separate an information limit from a fitting problem only as "
        "far as these rows go. Quarter-end targets: the error changes little from h = 5 to h = 1 and its interval includes zero, while on ordinary targets it shrinks clearly. The last public spread, "
        "compared with the forecast median:", "",
    ]
    rows = []
    for lab, v in (('quarter-end group', i3['persistence_group']), ('ordinary targets', i3['persistence_ordinary'])):
        for h in ('5', '1'):
            rows.append([lab, h, mci(v[h]['model_minus_persistence'], 2), mci(v[h]['persistence_closer_share'], 2)])
    out += table(['targets', 'h', 'model |error| minus persistence |error| (bp)', 'share where persistence is closer'], rows)
    out += [
        "## The 2026 days (shown apart, decide nothing)", "",
    ]
    if "2026" in r["windows"]:
        w = r["windows"]["2026"]
        g = w["item1"]["group"]["pooled"]
        out += [f"The 2026 window has {w['item1']['events']} quarter-end events and {w['item1']['cells_in_group']} group cells, against {w['item1']['cells'] - w['item1']['cells_in_group']} others. "
                f"Group 90% coverage {fig(g, 'cov90')}, 98% coverage {fig(g, 'cov98')}, miss > q95 {fig(g, 'miss_q95_up')}. The full tables are in `result.json` under `windows.2026`. "
                "They were already seen by earlier studies and are too few to read.", ""]
    out += [
        "## Limits and what was not checked", "",
        "- Development data on seen days, never a verdict. The development window has about thirty quarter-end events; every interval from it is wide and every split by regime has five to thirteen events.",
        "- The diagnosis reads the candidate's own walk. It fits and scores nothing new, tunes nothing, and registers nothing.",
        "- The Huber iteration counts are a fact; whether stricter convergence changes any forecast is her item 7, not done. Her items 4 (out-of-sample predictability of misses), 5 (error against fit age) and "
        "6 (interval-score decomposition) are a later package.",
        "- The same-target step table separates a new refit and a new settlement announcement from a plain step, but a step also carries one new public spread and other inputs this study does not isolate.",
        "- The mechanism reading depends on the majority rule declared here for 'set by ordinary-day residuals'. It is met at q95 in nearly every cell and at q99 in a bit over half of them. The pull request marks it as a question for her.",
        "- B4 (#1360) is not compared. The 98% band is q01 to q99, closed.", "",
        "## Reproduction", "",
        "See the header of `scripts/qe_diagnosis_1533.py`; the test is `tests/test_qe_diagnosis_1533.py`. Seed 1533 throughout.", "",
    ]
    return "\n".join(out)


def i2_rest(d: dict) -> int:
    return d["item2"]["cap_rest"]["clipped_q99"]


def page_command(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(page(result), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
