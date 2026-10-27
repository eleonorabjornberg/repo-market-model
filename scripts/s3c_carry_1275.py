"""(s3c-carry): (s3c) with a month-end carryover term sized to the spike, on business days 1 and 2 of the month, scored against (s3c), (s3), B1, B1'
and B2 (#1275; H5 step 3, an arm on the candidate; ledger item 67 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_carry_1275.json`, which this script refuses to read unless it is committed and unchanged. The arm is `repo_model.s3c_carry`: (s3)'s
fit with one term added, `DECAY[bday] * spike` on business day 1 and 2 of the month (`DECAY = {1: 1.0, 2: 0.5}`), the spike being the month-end's
SOFR - IORB less the model's level, floored at 0, read only if it was public at the decision instant and 0 otherwise; the SRF cap at full allotment
is (s3c)'s, applied to the arm's quantiles after the walk (`repo_model.s3c_candidate`). The frames and the machinery are #1255's and #1265's and are
loaded as they are: the development window (targets up to 2025-12-31) and the 2026 development days (targets 2026-01-02 to 2026-09-03, the near-blind
tier open since GO #151); the blind tier and every lockbox day are refused by the frames' own guards. The arm is walked on the same decision days with
the same refit schedule as (s3), and (s3) re-forecast inside that walk must equal the frame's (s3) cell for cell, or the run stops.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp), on scoring protocol v1's
studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill interval beside, split by regime, by pressure-day type,
by lead, and at lead 1 by the decision days on which the changed term is non-zero against the others; the 90% band coverage beside (s3c)'s; and the
fitted effect of the changed term in bp, by regime.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_carry_1275.py score --panel PUB.csv --output docs/research/s3c-carry-1275/result.json
    PYTHONPATH=src python3 scripts/s3c_carry_1275.py page \\
        --score docs/research/s3c-carry-1275/result.json --output docs/research/s3c-carry-1275-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, alias: Optional[str] = None):
    """Load `scripts/<name>.py` as a module registered under `alias` (default `name`)."""

    alias = alias or name
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, metrics, policy_events, s3c_candidate, s3c_carry  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1265's script (its cell table with the Brier cell, its table cell) and, through it, #1255's, #1241's and #1229's, loaded under an alias of
#: their own so that the pickling of the worker pool's tasks does not meet another test module's copy.
m1265 = _load("s3c_turn_cap_1265", "s3c_turn_cap_1265_in_1275")
m1255 = m1265.m1255
k, d1222 = m1255.k, m1255.d1222
c, s686, s761, load_daily_panel = k.c, k.s686, k.s761, m1255.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_carry_1275.json"
RECORD_1255 = REPO / "docs" / "research" / "s3c-candidate-1255" / "result.json"
SEED = 1275
LAST_DAY = EXPLORATORY_END
S3, S3C, S3CC, B1P = k.S3, m1255.S3C, "sc_s3c_carry", k.B1P
BENCHMARKS = ("B1", B1P, "B2")
ARMS = (S3, S3C, S3CC)
MODELS = BENCHMARKS + ARMS
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3: "(s3)", S3C: "(s3c)", S3CC: "(s3c-carry)"}
#: The measures that are tested, and the one that is reported as a mean only (the closed 90% band, q05 to q95).
TEST_METRICS = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
METRIC_NAMES = TEST_METRICS + ("coverage_90",)
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)", "coverage_90": "90% band coverage"}
LO, HI = sp.GRID.index(0.05), sp.GRID.index(0.95)
WINDOWS = ("development", "2026")
WINDOW_TITLES = m1255.WINDOW_TITLES
MIN_GROUP_DAYS = k.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
CHANGED = "changed_term"
NONZERO, OTHER = "decision days on which the term is non-zero (lead 1)", "other decision days (lead 1)"


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What (s3c-carry) is tested against: (s3c), (s3), then the benchmarks. No other model is a candidate here."""

    return [S3C, S3] + list(BENCHMARKS) if candidate == S3CC else []


# -- the arm's forecasts -------------------------------------------------------------------------------------------------


def candidate_days(panel, last: date, first: Optional[date]) -> List[date]:
    """The decision days the frames of #1255 walk: every panel day whose fifth target is on or before `last` (from `first`, in a test)."""

    dates = [row.date for row in panel]
    return [d for i, d in enumerate(dates) if i + max(sp.HORIZONS) < len(panel) and dates[i + max(sp.HORIZONS)] <= last and (first is None or d >= first)]


def s3cc_forecasts(frame, register, walk: s3c_carry.CarryWalk):
    """The arm's forecasts on the frame's days, each cell clipped by (s3c)'s cap (`m1255.s3c_forecasts`): the carry walk's quantiles, capped.

    Raises:
        ValueError: (s3) re-forecast in the carry walk differs from the frame's (s3) on a cell, or a frame day is not in the walk.
    """

    s3 = frame.forecasts[S3]
    for d in frame.days:
        if d not in walk.forecasts:
            raise ValueError(f"the decision day {d} is in the frame and not in the carry walk")
        if walk.s3[d] != s3[d]:
            raise ValueError(f"(s3) of the carry walk differs from the frame's (s3) on the decision day {d}")
    return m1255.s3c_forecasts(frame, register, {d: walk.forecasts[d] for d in frame.days})


def cell_table(frame, forecasts) -> Dict[str, Dict[Tuple[date, int], float]]:
    """#1265's cells (the two scores and the Brier scores, after the days are checked) with the closed 90% band's hit."""

    out = m1265.cell_table(frame, forecasts)
    out["coverage_90"] = {}
    for d in sorted(forecasts):
        for h in sp.HORIZONS:
            q, y = forecasts[d][h], frame.outcome[frame.target(d, h)]
            out["coverage_90"][(d, h)] = 1.0 if q[LO] <= y <= q[HI] else 0.0
    return {m: out[m] for m in METRIC_NAMES}


# -- what the term did ---------------------------------------------------------------------------------------------------


def term_use(frame, walk: s3c_carry.CarryWalk, s3c, s3cc) -> dict:
    """Where the changed term is non-zero and where the arm's forecast differs from (s3c)'s, by lead; the refits in which it is active."""

    out: Dict[str, dict] = {str(h): {"cells": 0, "term_nonzero": 0, "differs_from_s3c": 0} for h in sp.HORIZONS}
    for d in frame.days:
        for h in sp.HORIZONS:
            row = out[str(h)]
            row["cells"] += 1
            if walk.values[d][h] > 0.0:
                row["term_nonzero"] += 1
            if list(s3c[d][h]) != list(s3cc[d][h]):
                row["differs_from_s3c"] += 1
    used = sorted({walk.fit_used[d] for d in frame.days})
    out["refits_in_use"] = len(used)
    out["refits_active"] = {str(h): sum(1 for r in used if walk.estimates[r][h].active) for h in sp.HORIZONS}
    return out


def fitted_effect(frame, walk: s3c_carry.CarryWalk) -> dict:
    """The fitted effect of the changed term in bp, by regime of the target day, on the cells where the column is positive (coefficient of the
    refit in force times the column), and the coefficient of each refit in use summarised by the regime of the refit day."""

    cells: Dict[str, List[float]] = {}
    for d in frame.days:
        for h in sp.HORIZONS:
            value = walk.values[d][h]
            if value > 0.0:
                effect = walk.estimates[walk.fit_used[d]][h].coefficient * value
                for key in ("all", frame.regime(frame.target(d, h))):
                    cells.setdefault(key, []).append(effect)
    effect = {key: {"cells": len(v), "mean_bp": statistics.fmean(v), "min_bp": min(v), "max_bp": max(v)} for key, v in sorted(cells.items())}
    coefficients: Dict[str, List[float]] = {}
    for r in sorted({walk.fit_used[d] for d in frame.days}):
        est = walk.estimates[r][1]
        for key in ("all", frame.regime(r)):
            coefficients.setdefault(key, []).append(est.coefficient if est.active else 0.0)
    coefficient = {key: {"refits": len(v), "active": sum(1 for x in v if x != 0.0), "median": statistics.median(v), "min": min(v), "max": max(v)}
                   for key, v in sorted(coefficients.items())}
    return {"effect_bp_by_regime": effect, "coefficient_by_refit_regime": coefficient}


# -- one window ----------------------------------------------------------------------------------------------------------


def build(window: str, panel, splits, registry, table, register, first: Optional[date], walk: s3c_carry.CarryWalk):
    """The frame of a window with the models of `MODELS`: returns `(frame, notes, groups_fn, s3c, s3cc)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    s3cc = s3cc_forecasts(frame, register, walk)
    s3c = frame.forecasts[S3C]
    keep = {name: frame.forecasts[name] for name in BENCHMARKS + (S3, S3C)}
    frame.forecasts = {**keep, S3CC: {d: s3cc[d] for d in frame.days}}
    return frame, notes, groups_fn, s3c, frame.forecasts[S3CC]


_STATE: Dict = {}


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def unstudentized(series, candidate: str, reference: str, members: Sequence[date]) -> dict:
    """Mean d and its 90% stationary-bootstrap percentile interval, for a group whose studentized bound cannot be computed. Not the protocol's
    interval; no reading is taken from it. `d = S(reference) - S(candidate)`, positive favours the candidate."""

    d = [series[reference][x] - series[candidate][x] for x in sorted(members)]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=BLOCK, seed=SEED, replications=_STATE["reps"])
    return {"mean_d": sum(d) / len(d), "interval": [low, high], "days": len(d)}


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in plan(candidate):
        days = list(members)
        if _identical(series, candidate, name, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = unstudentized(series, candidate, name, days)
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def changed_term_groups(frame, walk: s3c_carry.CarryWalk) -> List[Tuple[str, str, str, List[date]]]:
    """At lead 1, the decision days on which the changed term is non-zero against the others (the term is 0 at every other lead)."""

    nonzero = [d for d in frame.days if walk.values[d][1] > 0.0]
    other = [d for d in frame.days if walk.values[d][1] <= 0.0]
    return [(CHANGED, NONZERO, "lead1", nonzero), (CHANGED, OTHER, "lead1", other)]


def run_window(window: str, panel, splits, registry, table, register, args, walk: s3c_carry.CarryWalk) -> dict:
    frame, notes, groups_fn, s3c, s3cc = build(window, panel, splits, registry, table, register, args.first, walk)
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = groups_fn(frame, labels, pressure) + changed_term_groups(frame, walk)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws, reps=args.reps)
    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in TEST_METRICS:
            jobs.append((split, label, grain, metric, S3CC, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {"notes": notes, "refits": len(walk.estimates), "groups": {}, "skipped_groups": skipped,
                    "term_use": term_use(frame, walk, s3c, s3cc), "fitted_effect": fitted_effect(frame, walk)}
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS} if members else {}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def against_records(results: Mapping[str, dict]) -> dict:
    """(s3) and (s3c) pooled mean scores here against #1255's record, window by window: the frames and the walk are the same."""

    if not RECORD_1255.exists():
        return {}
    there_all = json.loads(RECORD_1255.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        there = there_all[window]["groups"]["pooled"]["all decision days"]
        here = result["groups"]["pooled"]["all decision days"]
        out[window] = {"record": str(RECORD_1255.relative_to(REPO)), "metrics": {
            m: {model: {"here": here[m]["means"][model], "there": there[m]["means"][model], "difference": here[m]["means"][model] - there[m]["means"][model]}
                for model in (S3, S3C) + BENCHMARKS} for m in ("grid_crps", "upper_tail_twcrps")}}
    return out


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_carry_1275")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    s686.require_scored_days(candidate_days(panel, LAST_DAY, args.first), LAST_DAY)
    walk = s3c_carry.walk(panel, candidate_days(panel, LAST_DAY, args.first), table, registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    result: dict = {
        "issue": 1275, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": S3CC, "margin_bp": s3c_candidate.MARGIN_BP,
        "decay": {str(day): x for day, x in s3c_carry.DECAY.items()}, "reading_rules": declaration["reading_rules"],
        "walk": {"decision_days": len(walk.forecasts), "skipped": len(walk.skipped), "refits": len(walk.estimates)}, "windows": {},
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, args, walk)
    result["against_records"] = against_records(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


cell = m1265.cell


def _vs(group: Optional[Mapping[str, object]], metric: str, reference: str) -> Optional[dict]:
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(S3CC, {}).get(reference)


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text} (s3c-carry) against (s3c) on grid CRPS: {cell(_vs(entry, 'grid_crps', S3C))}")
    return "; ".join(parts) + "."


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(f"{group[x]['means'][m]:.4f}" if x in ("brier_gt5", "coverage_90") else f"{group[x]['means'][m]:.3f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = ["| (s3c-carry) against | " + " | ".join(METRIC_TITLES[m] for m in TEST_METRICS) + " |", "|---|" + "---|" * len(TEST_METRICS)]
    for ref in plan(S3CC):
        out.append(f"| {LABELS[ref]} | " + " | ".join(cell(_vs(group, m, ref)) for m in TEST_METRICS) + " |")
    return out


def split_table(r: Mapping[str, object], split: str, reference: str, metrics_: Sequence[str] = TEST_METRICS) -> List[str]:
    labels = r["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in metrics_) + " |", "|---|---|" + "---|" * len(metrics_)]
    for label in sorted(labels):
        g = labels[label]
        untested = f"{split}/{label}" in r["skipped_groups"]
        out.append(f"| {label} | {g['days']} | " + " | ".join("not tested (fewer than 20 days)" if untested else cell(_vs(g, m, reference)) for m in metrics_) + " |")
    return out if len(out) > 2 else []


def coverage_table(r: Mapping[str, object]) -> List[str]:
    """The closed 90% band's coverage of (s3), (s3c) and (s3c-carry): pooled, by regime, by lead and on the changed-term days (means)."""

    out = ["| group | days | (s3) | (s3c) | (s3c-carry) |", "|---|---|---|---|---|"]
    for split in ("pooled", "regime", "lead", CHANGED):
        for label, g in sorted(r["groups"].get(split, {}).items()):
            m = g["coverage_90"]["means"]
            if not m:
                continue
            out.append(f"| {split.replace('_', ' ')}: {label} | {g['days']} | {m[S3]:.3f} | {m[S3C]:.3f} | {m[S3CC]:.3f} |")
    return out


def effect_tables(fe: Mapping[str, object]) -> List[str]:
    out = ["| regime of the target day | cells with the term non-zero | mean effect (bp) | smallest | largest |", "|---|---|---|---|---|"]
    for key, v in fe["effect_bp_by_regime"].items():
        out.append(f"| {key} | {v['cells']} | {v['mean_bp']:+.3f} | {v['min_bp']:+.3f} | {v['max_bp']:+.3f} |")
    out += ["", "| regime of the refit day | refits in use | refits with the term active (lead 1) | median coefficient | smallest | largest |", "|---|---|---|---|---|---|"]
    for key, v in fe["coefficient_by_refit_regime"].items():
        out.append(f"| {key} | {v['refits']} | {v['active']} | {v['median']:+.3f} | {v['min']:+.3f} | {v['max']:+.3f} |")
    return out


def use_table(use: Mapping[str, object]) -> List[str]:
    out = ["| lead | cells | cells with the term non-zero | cells where (s3c-carry) differs from (s3c) | refits in use with the term active |", "|---|---|---|---|---|"]
    for h in sp.HORIZONS:
        u = use[str(h)]
        out.append(f"| {h} | {u['cells']} | {u['term_nonzero']} | {u['differs_from_s3c']} | {use['refits_active'][str(h)]} of {use['refits_in_use']} |")
    return out


def render(r: dict) -> str:
    out = [
        "# (s3c-carry): (s3c) with the month-end carryover sized to the spike (#1275)", "",
        "**Does a carryover term, the size of the last month-end spike times a declared decay, improve (s3c)?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c), ledger item 67 on #1116. **Development data, not a "
        "verdict** (scoring protocol v1, #640). Her ruling of 27 October 2026 (chat, relayed on #1275) queued four arms on (s3c), one directive "
        "each; this is the spike-sized carryover. **(s3c-carry)** is (s3c) with one term added to (s3)'s fit, on business days 1 and 2 of the month: "
        "the spike of the last month-end (its SOFR - IORB less the model's level, the median of the last 10 ordinary days, floored at 0) times a "
        "declared decay, 1 on business day 1 and 0.5 on business day 2 (declared before any score, not tuned). The column is divided by the scale "
        "at the pair's origin, so its coefficient is a carryover fraction and its effect in bp is the coefficient times decay times spike. Every "
        "other term, the Huber fit, the ridge of 5 and the SRF cap at full allotment are (s3c)'s; `post_month_end_window` is kept and the term sits "
        "beside it (`repo_model.s3c_carry`). The month-end spread is read only if it was public at the decision instant, and the term is 0 when it "
        "was not (a new availability rule, with a leakage test and one recorded mutation in `tests/test_s3c_carry.py`). Nothing is registered or "
        "published and no claim changes. Generated by `scripts/s3c_carry_1275.py page` from `docs/research/s3c-carry-1275/result.json`, not edited "
        f"by hand; declared in `{r['declaration']}` before any score.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "(s3c-carry). **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009, 20 October 2026), with the skill "
        "interval beside it. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x after "
        "2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days keep the **current method** "
        "(the group's days, scattered, resampled in date order as if consecutive), which #1221 questions and #1228 will decide. Where (s3c-carry) "
        "differs from its reference on few days of a group, some resamples have no long-run variance: the bound is then not computed, the "
        "unstudentized interval of mean d is given beside it, and no reading is taken from it.", "",
        "**What kind of look this is.** The development window and the 2026 days were already seen by the predecessors (#1145, #1229, #1252, #1255, "
        "#1265). This is a check on a term she asked about, not evidence for a verdict.", "",
        "**Where the term can be non-zero.** The panel dates SOFR so that the last public row at a decision is the day before the decision day, so "
        "the month-end spread is public only from the second business day of the next month. Under the as-of rule the column is therefore non-zero "
        "only at lead 1 on business day 2; on business day 1 the month-end is the decision day itself and its spread is not public, and at leads 2 to 5 "
        "the decision falls before the month-end. The tables below count the cells; every other cell of (s3c-carry) is (s3c)'s at leads 2 to 5, "
        "element for element, and at lead 1 differs only through the refit of the lead-1 fit.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}). The carry walk refit {r['walk']['refits']} times over the whole panel "
                f"({w['term_use']['refits_in_use']} refits in use in this window).", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled) + ["", "### (s3c-carry) against each reference (pooled)", ""] + against_table(pooled) + [""]
        out += ["### Where the term acts", ""] + use_table(w["term_use"]) + [""]
        for split, title in ((CHANGED, "At lead 1: the days on which the changed term is non-zero against the others"), ("regime", "By regime"),
                             ("pressure_day_type", "By pressure-day type of the target day"), ("lead", "By lead"),
                             ("target_day_type", "By calendar target-day type"), ("month", "By target month")):
            table = split_table(w, split, S3C)
            if table:
                out += [f"### {title}: (s3c-carry) against (s3c)", ""] + table + [""]
        for split, title in ((CHANGED, "the days on which the term is non-zero"), ("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = split_table(w, split, S3)
            if table:
                out += [f"### By {title}: (s3c-carry) against (s3)", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type"), (CHANGED, "the days on which the term is non-zero")):
            for ref in BENCHMARKS:
                table = split_table(w, split, ref)
                if table:
                    out += [f"### By {title}: (s3c-carry) against {LABELS[ref]}", ""] + table + [""]
        out += ["### 90% band coverage beside (s3c)'s (means; closed band q05 to q95; nominal 0.90)", ""] + coverage_table(w) + [""]
        out += ["### The fitted effect of the changed term in bp, by regime", "", "The effect is the refit's coefficient times the column, on the cells where the "
                "column is positive.", ""] + effect_tables(w["fitted_effect"]) + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_records"):
        out += ["## Reproduction of #1255", ""]
        for window, rec in r["against_records"].items():
            out += [f"{WINDOW_TITLES[window].split(' (')[0]}: (s3) and (s3c) pooled means here against `{rec['record']}`: " + "; ".join(
                f"{METRIC_TITLES[m]} (s3c) {v[S3C]['here']:.6f} against {v[S3C]['there']:.6f} (difference {v[S3C]['difference']:+.2e}), (s3) {v[S3]['here']:.6f} "
                f"against {v[S3]['there']:.6f} (difference {v[S3]['difference']:+.2e})" for m, v in rec["metrics"].items()) + ". The frames and the walk are the same.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. The term is live on one cell in five by the information set.** Read as declared, the month-end spread is public from "
        "business day 2, so the term acts at lead 1 on business day 2 and nowhere else. A carryover on business day 1, or at longer leads, would have "
        "to be sized from something that is public before the month-end (the spread of the last public row before it, say), which is a different "
        "term and a different information rule, or from the month-end spread itself, which is not public at the decision instant and which no "
        "model here reads.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Read the result as it stands and queue nothing further on this term** (default). (s3c) stays the candidate; nothing changes.",
        "2. **Queue a follow-up arm that sizes the carryover from the last public row before the month-end**, declared as its own arm with its own "
        "availability rule and leakage test.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3) and the carry arm, cap it as (s3c) is capped, and score (s3c-carry) on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of the unstudentized interval")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
