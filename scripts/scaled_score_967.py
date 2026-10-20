#!/usr/bin/env python3
"""H1 step 2 and the H5 primary score (#967): does a scale-free score confirm what raw CRPS cannot?

Everything it computes is declared in `metadata/scaled_score_967.json`, which `run` refuses to read unless it is committed
and unchanged. Development days only (decision days whose fifth target is on or before 2025-12-31, no lockbox day), from the
grid CRPS of B1, B2, `spread_mr_ctx` and `gbm_funding`. A report that changes nothing: the protocol's constants are only read.

The scale of a decision day is the median of B2's grid CRPS over the trailing year of cells whose target has the same
pressure-day type (the last 6 pool positions left out, as #733's D4). The script

- re-runs #733's six designs with that scale in place of D4's trailing mean of B1, calibrated on contiguous post-2020 windows
  (#963's method, on the single comparison S(B2) - S(B1)), and reports size and power at 3% and 10% on the post-2020 history,
  beside the old D4 and D5 and the trapezoid companion (#259);
- splits `gbm_funding` and `spread_mr_ctx` by regime under the raw and the scaled score, side by side.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/spread_distribution_634.py walk \\
        --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
    PYTHONPATH=src python3 scripts/scaled_score_967.py run --published PUB.csv --walks OUT --output OUT/result.json --workers 4
    python3 scripts/scaled_score_967.py report OUT/result.json
    python3 scripts/scaled_score_967.py check

`run` writes the record; `report` copies it to `docs/research/scaled-score-967/result.json` and writes the page
`docs/research/scaled-score-967-result.md` from it alone; `check` fails when the page is not what the record gives.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing
import random
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import crps_trapezoid_from_quantiles, stationary_bootstrap_indices  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

RESEARCH = REPO / "docs" / "research"
DECLARATION = REPO / "metadata" / "scaled_score_967.json"
RECORD = RESEARCH / "scaled-score-967" / "result.json"
PAGE = RESEARCH / "scaled-score-967-result.md"
RECORD_1014 = RESEARCH / "scaled-score-967" / "result-1014.json"
PAGE_1014 = RESEARCH / "scaled-score-967-orientation-1014-result.md"
ORIENTATION = "S(B1) - S(B2)"
ROW_CHECK_DESIGNS = ("D0", "D4")
SPLITS_PATH = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
PANEL_MANIFEST = REPO / "metadata" / "funding_panel_manifest.json"

STUDY_END = date(2025, 12, 31)
FIRST_DECISION = date(2018, 6, 29)
POST_2020_FIRST = date(2020, 4, 3)
DECISION_TIME = "16:00:00"

#: The declaration's scale: a trailing year of 252 pool positions, the last 6 left out, 20 cells of a type at least.
TRAILING = 252
SCALE_LAG = 6
MIN_CELLS = 20
KINDS = ("month_end", "quarter_end", "tax_date", "ordinary")

LOOK_FRACTIONS = (0.24, 0.5, 1.0)
OLD_WINDOW = 60
WINDOWS = 20_000
CALIBRATION_SEED = 1
PATHS = 2_000
SEED = 967
SCENARIO_STRIDE = 1_000_003
MME = sp.MME
SIZE_LIMIT = 0.05
POWER_FLOOR = 0.20
MINIMUM_REGIME_DAYS = 60
CANDIDATES = ("gbm_funding", "spread_mr_ctx")
SCENARIOS = (
    ("size", 0.0), ("3%", 0.03), ("10%", 0.10), ("5%", 0.05), ("7.5%", 0.075),
    ("15%", 0.15), ("20%", 0.20), ("30%", 0.30),
)
SCENARIO_NAMES = {0.03: "3%", 0.05: "5%", 0.075: "7.5%", 0.10: "10%", 0.15: "15%", 0.20: "20%", 0.30: "30%"}
MDE_GRID = (0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30)
TARGET_POWER = 0.80


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


DESIGNS = (
    Design("D0", 250, sp.HORIZONS, "raw"),
    Design("D1", 375, sp.HORIZONS, "raw"),
    Design("D2", 500, sp.HORIZONS, "raw"),
    Design("D3", 250, (1,), "raw"),
    Design("D4", 250, sp.HORIZONS, "new"),
    Design("D5", 375, sp.HORIZONS, "new"),
    Design("D4old", 250, sp.HORIZONS, "old"),
    Design("D5old", 375, sp.HORIZONS, "old"),
    Design("D0t", 250, sp.HORIZONS, "raw", "trapezoid"),
    Design("D4t", 250, sp.HORIZONS, "new", "trapezoid"),
)
DESIGN_BY_ID = {design.id: design for design in DESIGNS}


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the guards -------------------------------------------------------------------------------------------------------


def require_public(decision: date, target: date) -> None:
    """A scale cell's outcome was public at the decision instant: its target day is before the decision day.

    Raises:
        LookAheadError: the target day is on or after the decision day.
    """

    if target >= decision:
        raise LookAheadError(f"a scale for decision day {decision} reads the outcome of {target}, not public at the instant")


def require_study_window(days) -> None:
    """The study reads no day after `STUDY_END`.

    Raises:
        LookAheadError: a day is later than `STUDY_END`.
    """

    late = sorted(day for day in days if day > STUDY_END)
    if late:
        raise LookAheadError(f"the scaled-score study reads no day after {STUDY_END}; got {late[0]}")


# -- the scale --------------------------------------------------------------------------------------------------------------


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0


def trailing_scales(decisions, targets, kinds, scores, *, trailing: int = TRAILING, lag: int = SCALE_LAG,
                    minimum: int = MIN_CELLS) -> List[Optional[Dict[str, float]]]:
    """The scale of each pool position: a median per pressure-day type of the trailing year's cells.

    `decisions[i]` is the decision day of position `i`; `targets[i][h]`, `kinds[i][h]` and `scores[i][h]` the target day,
    its pressure-day type and the score of lead `h + 1`. The scale at position `i` reads positions `i - lag - trailing + 1`
    to `i - lag`; `None` where that window does not fit. A type with fewer than `minimum` cells in the window takes the
    median over all of the window's cells.

    Raises:
        LookAheadError: a cell in the window has a target day on or after the decision day.
    """

    out: List[Optional[Dict[str, float]]] = [None] * len(decisions)
    for i in range(len(decisions)):
        first, last = i - lag - trailing + 1, i - lag
        if first < 0:
            continue
        by_kind: Dict[str, List[float]] = {kind: [] for kind in KINDS}
        everything: List[float] = []
        for u in range(first, last + 1):
            for h, value in enumerate(scores[u]):
                require_public(decisions[i], targets[u][h])
                by_kind[kinds[u][h]].append(value)
                everything.append(value)
        whole = _median(everything)
        out[i] = {kind: (_median(cells) if len(cells) >= minimum else whole) for kind, cells in by_kind.items()}
    return out


def scaled_day(day_scores: Sequence[float], day_kinds: Sequence[str], scale: Dict[str, float]) -> float:
    """A decision day's scaled score: the mean over its leads of each cell over the scale of its target's type."""

    return sum(value / scale[kind] for value, kind in zip(day_scores, day_kinds)) / len(day_scores)


# -- the pool ---------------------------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True,
                           check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Pool:
    decisions: List[date]
    targets: List[List[date]]
    kinds: List[List[str]]
    s1: List[List[float]]
    s2: List[List[float]]
    t1: List[List[float]]
    t2: List[List[float]]


def build_pool(rows, splits, registry) -> Pool:
    """B1 and B2 on every decision day of #733's pool, per lead, by the grid CRPS and by the trapezoid companion."""

    cd = _load("confirmation_design")
    positions = [t for t in cd.decision_positions(rows) if rows[t].date >= FIRST_DECISION]
    decisions = [rows[t].date for t in positions]
    targets = [[rows[t + h].date for h in sp.HORIZONS] for t in positions]
    require_study_window(d for per in targets for d in per)
    lockbox.require_unlocked(set(decisions) | {d for per in targets for d in per}, where="scaled_score_967")
    settings = {"registry": registry, "decision_time": cd.DECISION}
    b1 = pb.forecasts(pb.b1_forecast, rows, decisions, **settings)
    b2 = pb.forecasts(pb.b2_forecast, rows, decisions, splits=splits, **settings)
    kinds, s1, s2, t1, t2 = [], [], [], [], []
    for t, day in zip(positions, decisions):
        kinds.append([splits.reporting_day_type(rows[t + h].date, rows[t + h].values) for h in sp.HORIZONS])
        outcomes = [rows[t + h].spread_bps for h in sp.HORIZONS]
        s1.append([sp.grid_crps(b1[day][h], y) for h, y in zip(sp.HORIZONS, outcomes)])
        s2.append([sp.grid_crps(b2[day][h], y) for h, y in zip(sp.HORIZONS, outcomes)])
        t1.append([crps_trapezoid_from_quantiles(sp.GRID, b1[day][h], y) for h, y in zip(sp.HORIZONS, outcomes)])
        t2.append([crps_trapezoid_from_quantiles(sp.GRID, b2[day][h], y) for h, y in zip(sp.HORIZONS, outcomes)])
    return Pool(decisions, targets, kinds, s1, s2, t1, t2)


# -- the designs' series ---------------------------------------------------------------------------------------------------


def design_series(pool: Pool, design: Design, scales, trap_scales) -> Tuple[List[date], List[float], List[float]]:
    """`(dates, b, e)` of a design on the post-2020 history: `b` the benchmark's score, `e` = B1's minus B2's, both on the
    design's scale and lead set."""

    one, two = (pool.t1, pool.t2) if design.score == "trapezoid" else (pool.s1, pool.s2)
    use = trap_scales if design.score == "trapezoid" else scales
    leads = [h - 1 for h in design.leads]
    old = None
    if design.scale == "old":
        pooled = [sum(row) / len(row) for row in pool.s1]
        old = [None] * len(pooled)
        warmup = OLD_WINDOW + SCALE_LAG - 1
        for i in range(warmup, len(pooled)):
            window = pooled[i - warmup: i - SCALE_LAG + 1]
            old[i] = sum(window) / len(window)
    dates, b, e = [], [], []
    for i, day in enumerate(pool.decisions):
        if day < POST_2020_FIRST:
            continue
        a_cells, b_cells = [one[i][h] for h in leads], [two[i][h] for h in leads]
        if design.scale == "new":
            scale = use[i]
            if scale is None:
                continue
            kinds = [pool.kinds[i][h] for h in leads]
            sb, sb2 = scaled_day(a_cells, kinds, scale), scaled_day(b_cells, kinds, scale)
        elif design.scale == "old":
            if old[i] is None:
                continue
            sb, sb2 = sum(a_cells) / len(a_cells) / old[i], sum(b_cells) / len(b_cells) / old[i]
        else:
            sb, sb2 = sum(a_cells) / len(a_cells), sum(b_cells) / len(b_cells)
        dates.append(day)
        b.append(sb)
        e.append(sb - sb2)
    return dates, b, e


def candidate(b: Sequence[float], e: Sequence[float], delta: float, noise: float = 1.0) -> List[float]:
    centre = sum(e) / len(e)
    return [delta * x + noise * (y - centre) for x, y in zip(b, e)]


# -- the calibration --------------------------------------------------------------------------------------------------------


def calibrate(job) -> Tuple[str, Dict[str, object]]:
    """The design's critical value at each look after the first: the contiguous windows of S(B1) - S(B2), the series
    `candidate` and `run_path` draw from, and, beside it, the stationary-10 windows of #886."""

    design, e, windows = job
    return calibrate_series(design, list(e), windows)  # S(B1) - S(B2), the series the paths are drawn from (#1014)


def calibrate_series(design: Design, series: Sequence[float], windows: int) -> Tuple[str, Dict[str, object]]:
    cc = _load("contiguous_calibration_963")
    looks = design.checkpoints
    levels = sp.nominal_levels(looks)
    contiguous, stationary, counts = {}, {}, {}
    for k, n in enumerate(looks[1:], start=1):
        ordered = cc.contiguous_window_statistics(series, days=n)
        contiguous[str(n)] = sp._bound(ordered, 1.0 - levels[k], len(ordered))
        counts[str(n)] = len(ordered)
        with cc.stationary_windows():
            ordered = sp.window_t_statistics(series, days=n, windows=windows, seed=CALIBRATION_SEED, block=sp.BLOCK_LENGTH)
        stationary[str(n)] = sp._bound(ordered, 1.0 - levels[k], len(ordered))
    return design.id, {"checkpoints": list(looks), "nominal_levels": list(levels), "critical": contiguous,
                       "critical_stationary": stationary, "windows": counts, "series_days": len(series)}


# -- the paths --------------------------------------------------------------------------------------------------------------

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


def summarize(design: Design, results, paths: int) -> Dict[str, object]:
    def share(position, upto):
        return sum(1 for r in results if r[position] is not None and r[position] <= upto) / paths

    out: Dict[str, object] = {"paths": paths}
    for label, position in (("without_the_mme_gate", 0), ("with_the_mme_gate", 1)):
        by_look = {str(n): share(position, n) for n in design.checkpoints}
        out[label] = by_look
        last = by_look[str(design.days)]
        out[label + "_se"] = math.sqrt(last * (1 - last) / paths)
    return out


def simulate(histories, critical, designs, *, paths: int, workers: int) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {design.id: {} for design in designs}
    for s, (name, delta) in enumerate(SCENARIOS):
        generators = ("stationary", "circular") if name == "size" else ("stationary",)
        for design in designs:
            for generator in generators:
                jobs = [(design, delta, SEED * 100_003 + s * SCENARIO_STRIDE + i, generator) for i in range(paths)]
                with multiprocessing.Pool(workers, initializer=_init, initargs=(histories, critical)) as pool:
                    results = pool.map(run_path, jobs, chunksize=max(1, paths // (workers * 8)))
                key = name if generator == "stationary" else f"{name}, circular"
                out[design.id][key] = summarize(design, results, paths)
        print("scenario", name, flush=True)
    return out


# -- the readings -----------------------------------------------------------------------------------------------------------


def design_rows(scenarios) -> Dict[str, Dict[str, object]]:
    rows = {}
    for design in DESIGNS:
        last = str(design.days)
        cells = scenarios[design.id]

        def gated(name):
            return cells[name]["with_the_mme_gate"][last]

        smallest = next((g for g in MDE_GRID if gated(SCENARIO_NAMES[g]) >= TARGET_POWER), None)
        rows[design.id] = {
            "days": design.days,
            "size": cells["size"]["without_the_mme_gate"][last],
            "size_se": cells["size"]["without_the_mme_gate_se"],
            "size_circular": cells["size, circular"]["without_the_mme_gate"][last],
            "power_3": gated("3%"), "power_3_se": cells["3%"]["with_the_mme_gate_se"],
            "power_10": gated("10%"), "power_10_se": cells["10%"]["with_the_mme_gate_se"],
            "smallest_skill_at_80": smallest,
        }
    return rows


def kill_scale_buys_nothing(record) -> Dict[str, object]:
    """The first kill rule: D4's gated power at 10% skill is below 20%, or its size is above 5%, on the post-2020 history."""

    row = record["designs"]["D4"]["post_2020"]
    low_power, high_size = row["power_10"] < POWER_FLOOR, row["size"] > SIZE_LIMIT
    return {"fires": low_power or high_size, "power_10": row["power_10"], "size": row["size"],
            "low_power": low_power, "high_size": high_size}


def misranking(by_regime) -> Dict[str, object]:
    """The second rule: the two candidates swap order between the raw and the scaled score in a regime with enough days."""

    changed, read = [], []
    for label, cell in by_regime.items():
        if cell["n"] < MINIMUM_REGIME_DAYS:
            continue
        raw_first = max(CANDIDATES, key=lambda c: cell["raw"][c])
        scaled_first = max(CANDIDATES, key=lambda c: cell["scaled"][c])
        read.append(label)
        if raw_first != scaled_first:
            changed.append(label)
    return {"holds": bool(changed), "changed": changed, "read": read}


# -- the run ----------------------------------------------------------------------------------------------------------------


def regime_split(published: Path, walks: Path, pool: Pool, scales, splits) -> Dict[str, object]:
    cc = _load("contiguous_calibration_963")
    data = cc.build(published, walks)
    position = {day: i for i, day in enumerate(pool.decisions)}
    cells = data["cells"]
    names = ("B1",) + CANDIDATES
    rows = []
    for day in data["days"]:
        i = position.get(day)
        if i is None or scales[i] is None or day > STUDY_END:
            continue
        if any((day, h) not in cells[name] for name in names for h in sp.HORIZONS):
            continue
        raw = {n: sum(cells[n][(day, h)] for h in sp.HORIZONS) / 5 for n in names}
        scaled = {n: scaled_day([cells[n][(day, h)] for h in sp.HORIZONS], pool.kinds[i], scales[i]) for n in names}
        rows.append((day, raw, scaled))
    by_regime: Dict[str, Dict[str, object]] = {}
    for label in splits.regime_labels:
        group = [r for r in rows if splits.regime(r[0]) == label]
        if not group:
            continue
        by_regime[label] = {
            "n": len(group),
            "raw": {c: sum(r[1]["B1"] - r[1][c] for r in group) / len(group) for c in CANDIDATES},
            "scaled": {c: sum(r[2]["B1"] - r[2][c] for r in group) / len(group) for c in CANDIDATES},
        }
    return {"days": len(rows), "first": rows[0][0].isoformat(), "last": rows[-1][0].isoformat(), "by_regime": by_regime}


def row_check(series, windows: int, published: Path = RECORD) -> Dict[str, object]:
    """#1014 criterion 3: calibrate D0 and D4 on `-e`, the orientation #999 used, and compare with #999's committed values."""

    old = json.loads(published.read_text(encoding="utf-8"))["designs"]
    out: Dict[str, object] = {}
    for design_id in ROW_CHECK_DESIGNS:
        design = DESIGN_BY_ID[design_id]
        _, reproduced = calibrate_series(design, [-v for v in series[design_id][2]], windows)
        out[design_id] = {"reproduced": {k: reproduced[k] for k in ("critical", "critical_stationary")},
                          "published_999": {k: old[design_id][k] for k in ("critical", "critical_stationary")},
                          "matches": all(reproduced[k] == old[design_id][k] for k in ("critical", "critical_stationary"))}
    return out


def run_command(args) -> int:
    declaration = committed_declaration()
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    manifest = json.loads(PANEL_MANIFEST.read_text(encoding="utf-8"))
    digest = sha256(args.published)
    if digest != manifest.get("sha256", digest):
        raise ValueError("the panel is not the published one")
    splits = load_split_declaration(SPLITS_PATH)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    pool = build_pool(rows, splits, registry)
    scales = trailing_scales(pool.decisions, pool.targets, pool.kinds, pool.s2)
    trap_scales = trailing_scales(pool.decisions, pool.targets, pool.kinds, pool.t2)
    series = {d.id: design_series(pool, d, scales, trap_scales) for d in DESIGNS}
    histories = {d.id: (series[d.id][1], series[d.id][2]) for d in DESIGNS}
    with multiprocessing.Pool(max(1, args.workers)) as workers:
        calibrated = dict(workers.map(calibrate, [(d, histories[d.id][1], args.windows) for d in DESIGNS]))
    print("calibrated", json.dumps({k: v["critical"] for k, v in calibrated.items()}), flush=True)
    critical = {k: v["critical"] for k, v in calibrated.items()}
    scenarios = simulate(histories, critical, DESIGNS, paths=args.paths, workers=args.workers)
    rows_ = design_rows(scenarios)
    record: Dict[str, object] = {
        "declaration_sha256": sha256(DECLARATION), "panel_sha256": digest, "study_end": STUDY_END.isoformat(),
        "constants": {"windows": args.windows, "paths": args.paths, "seed": SEED, "calibration_seed": CALIBRATION_SEED,
                      "mme": MME, "trailing": TRAILING, "scale_lag": SCALE_LAG, "minimum_cells": MIN_CELLS,
                      "size_limit": SIZE_LIMIT, "power_floor": POWER_FLOOR},
        "pool": {"first": pool.decisions[0].isoformat(), "last": pool.decisions[-1].isoformat(), "days": len(pool.decisions),
                 "first_scaled": next(d for d, s in zip(pool.decisions, scales) if s is not None).isoformat(),
                 "post_2020_days": sum(1 for d in pool.decisions if d >= POST_2020_FIRST)},
        "designs": {d.id: {"days": d.days, "leads": list(d.leads), "scale": d.scale, "score": d.score,
                           **calibrated[d.id], "post_2020": rows_[d.id]} for d in DESIGNS},
        "scenarios": scenarios,
    }
    record["orientation"] = ORIENTATION
    record["row_check"] = row_check(series, args.windows)
    record["kill_scale_buys_nothing"] = kill_scale_buys_nothing(record)
    record["regimes"] = regime_split(args.published, args.walks, pool, scales, splits)
    record["misranking"] = misranking(record["regimes"]["by_regime"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "kill": record["kill_scale_buys_nothing"]["fires"],
                      "misranking": record["misranking"]["holds"]}))
    return 0


# -- the report -------------------------------------------------------------------------------------------------------------


def pct(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{100 * value:.1f}%"


def f(value: Optional[float], digits: int = 3, sign: bool = False) -> str:
    return "n/a" if value is None else f"{value:{'+' if sign else ''}.{digits}f}"


def correction_section(record) -> List[str]:
    """#1014: what changed against #999's page, and the row check that the old orientation still gives #999's values."""

    old = json.loads(RECORD.read_text(encoding="utf-8"))["designs"]
    L = ["## What this page corrects (#1014)", "",
         "#999 built each path from `e = S(B1) - S(B2)` but calibrated the critical value on `-e`. The windows are studentized "
         "about the series mean, so a skewed series has a different upper quantile from its negation, and the two disagreed. This "
         f"page calibrates on {record['orientation']}, the series the paths use, and changes nothing else: the generator, the "
         "constants, the scale, the pool and the panel are #999's. #999's page and record stand beside this one. The values "
         "below are the contiguous and the stationary-10 critical values at the last two looks (the first and the second "
         "number of each pair), #999's beside the corrected.", "",
         "| design | #999 contiguous | corrected contiguous | #999 stationary-10 | corrected stationary-10 | #999 size | corrected size | #999 power at 10% | corrected power at 10% |",
         "|---|---|---|---|---|---|---|---|---|"]
    for d in DESIGNS:
        new = record["designs"][d.id]
        looks = new["checkpoints"]

        def pair(info, key):
            return f"{info[key][str(looks[1])]:.2f} / {info[key][str(looks[2])]:.2f}"

        L.append(f"| {d.id} | {pair(old[d.id], 'critical')} | {pair(new, 'critical')} | {pair(old[d.id], 'critical_stationary')} | "
                 f"{pair(new, 'critical_stationary')} | {pct(old[d.id]['post_2020']['size'])} | {pct(new['post_2020']['size'])} | "
                 f"{pct(old[d.id]['post_2020']['power_10'])} | {pct(new['post_2020']['power_10'])} |")
    rc = record["row_check"]
    L += ["", "Row check: calibrating D0 and D4 on `-e`, the old orientation, on this run's histories "
          + ("reproduces #999's critical values exactly (contiguous and stationary-10): " if all(v["matches"] for v in rc.values())
             else "does NOT reproduce #999's critical values: ")
          + ", ".join(f"{k} {'yes' if v['matches'] else 'no'}" for k, v in rc.items()) + ".", ""]
    return L


def render(record) -> str:
    c, pool, designs, sc = record["constants"], record["pool"], record["designs"], record["scenarios"]
    kill, mis = record["kill_scale_buys_nothing"], record["misranking"]
    corrected = bool(record.get("orientation"))
    L = [
        "# A scale-free primary score: size, power and the regime ranking "
        + ("re-read with the critical value calibrated on the series the paths use (#1014, H1 step 2 and H5)" if corrected
           else "(#967, H1 step 2 and H5)"), "",
        "**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.CRITICAL_VALUES` and "
        "`docs/decisions/scoring-protocol.md` are only read. No day after 2025-12-31 and no lockbox day is scored. Everything is "
        "declared in `metadata/scaled_score_967.json` before any score and read from "
        + ("`docs/research/scaled-score-967/result-1014.json`" if corrected else "`docs/research/scaled-score-967/result.json`")
        + " by `scripts/scaled_score_967.py report`. The series are development data seen before the declaration.", "",
        *(correction_section(record) if corrected else []),
        "## Question for Eleonora (marked)", "",
        "**Does the primary score change?** Replacing raw grid CRPS by the scaled score in the confirmation test is a section 13 "
        "decision and is hers. This page is its evidence: the scale's size and power, and whether it ranks the two candidates "
        "differently. It changes no protocol in code.", "",
        "## The scale", "",
        "The scale of a decision day is the median of B2's grid CRPS over the trailing year (252 pool positions, the last 6 left out "
        "so that every outcome in it was public at the instant) of cells whose target day has the same pressure-day type; a type "
        f"with fewer than {c['minimum_cells']} cells takes the median of the whole window. A decision day's scaled score is the mean "
        f"over its five leads of the cell over its scale. The pool is {pool['days']} decision days from {pool['first']} to {pool['last']}; "
        f"the first scaled day is {pool['first_scaled']}; the designs below are read on the {pool['post_2020_days']} post-2020 days "
        "(from 2020-04-03).", "",
        "## 1. Size and power of #733's six designs under the scale", "",
        "Contiguous calibration (#963): the critical value of a look is the quantile of every contiguous post-2020 window of "
        f"that length, on {record.get('orientation', 'S(B2) - S(B1)')} alone (reading (b), her ruling on PR #695, Q-E), at the look's nominal level. Size is the "
        "false-detection share by the last look under no true difference, without the MME gate, on stationary-bootstrap paths "
        f"of the same history ({c['paths']} paths a scenario); power is the gated share. D4 and D5 use this study's scale; D4old "
        "and D5old use #733's (the trailing 60-day mean of B1); D0t and D4t are the trapezoid companion (#259) on the raw and "
        "the scaled 250-day design. Every share carries its Monte Carlo standard error.", "",
        "| design | days | scale | score | c at look 2 / 3 (contiguous) | c at look 2 / 3 (stationary-10) | size | size, circular | power at 3% | power at 10% | smallest skill at 80% |",
        "|---|---|---|---|---|---|---|---|---|---|---|"]
    for d in DESIGNS:
        info, row = designs[d.id], designs[d.id]["post_2020"]
        looks = info["checkpoints"]
        cv, cs = info["critical"], info["critical_stationary"]
        L.append(
            f"| {d.id} | {d.days} | {d.scale} | {d.score} | {cv[str(looks[1])]:.2f} / {cv[str(looks[2])]:.2f} | "
            f"{cs[str(looks[1])]:.2f} / {cs[str(looks[2])]:.2f} | {pct(row['size'])} ± {pct(row['size_se'])} | "
            f"{pct(row['size_circular'])} | {pct(row['power_3'])} ± {pct(row['power_3_se'])} | "
            f"{pct(row['power_10'])} ± {pct(row['power_10_se'])} | "
            f"{'none on the grid' if row['smallest_skill_at_80'] is None else pct(row['smallest_skill_at_80'])} |")
    L += ["", "### Gated power by true skill (last look)", "",
          "| design | " + " | ".join(pct(g) for g in MDE_GRID) + " |", "|---|" + "---|" * len(MDE_GRID)]
    for d in DESIGNS:
        L.append(f"| {d.id} | " + " | ".join(pct(sc[d.id][SCENARIO_NAMES[g]]["with_the_mme_gate"][str(d.days)]) for g in MDE_GRID) + " |")
    L += ["", "### Kill rule (declared): the scale buys nothing", "",
          "Fires when D4's gated power at 10% true skill on the post-2020 history is below 20%, or its size is above 5%.", "",
          f"D4: power at 10% {pct(kill['power_10'])}, size {pct(kill['size'])}. **The rule "
          f"{'fires: the scale buys nothing' if kill['fires'] else 'does not fire'}**"
          + (f" (power below {pct(c['power_floor'])}: {'yes' if kill['low_power'] else 'no'}; size above "
             f"{pct(c['size_limit'])}: {'yes' if kill['high_size'] else 'no'})." if True else "."), ""]
    reg = record["regimes"]
    L += ["## 2. The regime ranking of the two candidates", "",
          f"d = S(B1) - S(candidate) on the {reg['days']} decision days from {reg['first']} to {reg['last']} on which B1 and both "
          "candidates have a forecast and the scale exists, split by the regime of the decision day (the declared regimes). The "
          "scaled d divides each cell by its scale before averaging; a positive d favours the candidate. Means only: this is an "
          "ordering demonstration, not a test.", "",
          "| regime | days | gbm_funding raw | spread_mr_ctx raw | first, raw | gbm_funding scaled | spread_mr_ctx scaled | first, scaled | order changes |",
          "|---|---|---|---|---|---|---|---|---|"]
    for label, cell in reg["by_regime"].items():
        raw_first = max(CANDIDATES, key=lambda k: cell["raw"][k])
        scaled_first = max(CANDIDATES, key=lambda k: cell["scaled"][k])
        thin = cell["n"] < MINIMUM_REGIME_DAYS
        L.append(f"| {label} | {cell['n']}{' (thin: not read)' if thin else ''} | {f(cell['raw']['gbm_funding'], 3, True)} | "
                 f"{f(cell['raw']['spread_mr_ctx'], 3, True)} | {raw_first} | {f(cell['scaled']['gbm_funding'], 4, True)} | "
                 f"{f(cell['scaled']['spread_mr_ctx'], 4, True)} | {scaled_first} | {'yes' if raw_first != scaled_first and not thin else 'no'} |")
    L += ["", "### Kill rule (declared): the misranking demonstration fails", "",
          f"The regimes read (at least {MINIMUM_REGIME_DAYS} days): {', '.join(mis['read']) or 'none'}. The order changes in: "
          f"{', '.join(mis['changed']) or 'none'}. **The demonstration "
          f"{'holds: the scaled score ranks the candidates differently in at least one regime' if mis['holds'] else 'fails: the order is the same in every regime read, so section 13(a) is not met by this demonstration, and the trapezoid companion still stands'}.**",
          "", "## Limits", "",
          "The history is development data seen before the declaration, so a result is exploration. The paths resample one history, so "
          "power is an upper bound (the B2 half of Supported and futility stopping are not simulated), and contiguous calibration "
          "rests on a handful of independent stretches (#963). The Full history is not simulated; the scaled series starts when a "
          "full trailing year exists. Nothing is registered, published or changed.", ""]
    return "\n".join(L)


def report_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    record_path, page_path = (RECORD_1014, PAGE_1014) if record.get("orientation") else (RECORD, PAGE)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    page_path.write_text(render(record), encoding="utf-8")
    print("wrote", page_path)
    return 0


def check_command(_args) -> int:
    if not RECORD.exists():
        print("no record yet: `run` and `report` have not been run", file=sys.stderr)
        return 1
    for record_path, page_path in ((RECORD, PAGE), (RECORD_1014, PAGE_1014)):
        if not record_path.exists():
            continue
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if record["declaration_sha256"] != sha256(DECLARATION):
            print("the record was made under another text of the declaration", file=sys.stderr)
            return 1
        if record["pool"]["last"] > STUDY_END.isoformat():
            print("the study scored a day after its end", file=sys.stderr)
            return 1
        if not page_path.exists() or page_path.read_text(encoding="utf-8") != render(record):
            print("the page is not what the record gives; run `report`", file=sys.stderr)
            return 1
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--walks", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--workers", type=int, default=4)
    run.add_argument("--paths", type=int, default=PATHS)
    run.add_argument("--windows", type=int, default=WINDOWS)
    run.set_defaults(func=run_command)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
