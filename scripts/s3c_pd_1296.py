"""(s3c-pd): (s3c) with primary dealers' reverse repo plus securities borrowed as a balance-sheet state input, scored against (s3c), (s3), B1, B1' and B2
(#1296; H5 step 3, an arm on the candidate with a new public source; ledger item 72 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_pd_1296.json` (the arm) and `metadata/sources_pd_financing_1296.json` (the source and its availability), and this script refuses to
read the arm's declaration unless it is committed and unchanged. The arm is `repo_model.s3c_pd`: (s3)'s fit with one state term added, the z-score of
the latest public week's primary dealer level (reverse repo plus securities borrowed on Treasury collateral, New York Fed FR 2004, released Thursdays
at about 4:15 p.m.) against the year before it, read at the decision instant; the SRF cap at full allotment is (s3c)'s, applied to the arm's quantiles
after the walk (`repo_model.s3c_candidate`). The frames and the machinery are #1255's and #1265's and are loaded as they are: the development window
(targets up to 2025-12-31) and the 2026 development days (targets 2026-01-02 to 2026-09-03, the near-blind tier open since GO #151); the blind tier and
every lockbox day are refused by the frames' own guards. The arm is walked on the same decision days with the same refit schedule as (s3), and (s3)
re-forecast inside that walk must equal the frame's (s3) cell for cell, or the run stops.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp), on scoring protocol v1's
studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill interval beside, split by regime (2026 split out), by
pressure-day type, by lead, and by the decision days on which the state is defined against the others; the 90% band coverage beside (s3c)'s; and the
fitted effect of the state term in bp per standard unit.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_pd_1296.py score --panel PUB.csv --output docs/research/s3c-pd-1296/result.json
    PYTHONPATH=src python3 scripts/s3c_pd_1296.py page \\
        --score docs/research/s3c-pd-1296/result.json --output docs/research/s3c-pd-1296-result.md

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
    path = REPO / "scripts" / f"{name}.py"
    held = sys.modules.get(alias)
    if held is not None and getattr(held, "__file__", None) == str(path):
        return held  # another loader in this process already holds the alias: share it, so pickled task names stay one object (#1294)
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, metrics, policy_events, s3c_candidate, s3c_pd  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1265's script (its cell table with the Brier cell, its table cell) and, through it, #1255's, #1241's and #1229's, loaded under an alias of
#: their own so that the pickling of the worker pool's tasks does not meet another test module's copy.
m1265 = _load("s3c_turn_cap_1265", "s3c_turn_cap_1265_in_1296")
m1255 = m1265.m1255
k, d1222 = m1255.k, m1255.d1222
c, s686, s761, load_daily_panel = k.c, k.s686, k.s761, m1255.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_pd_1296.json"
SOURCE_DECLARATION = REPO / "metadata" / "sources_pd_financing_1296.json"
SNAPSHOT = REPO / "tests" / "fixtures" / "snapshots" / "nyfed-pd-financing"
RECORD_1255 = REPO / "docs" / "research" / "s3c-candidate-1255" / "result.json"
SEED = 1296
LAST_DAY = EXPLORATORY_END
S3, S3C, S3PD, B1P = k.S3, m1255.S3C, "sc_s3c_pd", k.B1P
BENCHMARKS = ("B1", B1P, "B2")
ARMS = (S3, S3C, S3PD)
MODELS = BENCHMARKS + ARMS
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3: "(s3)", S3C: "(s3c)", S3PD: "(s3c-pd)"}
#: The measures that are tested, and the one that is reported as a mean only (the closed 90% band, q05 to q95).
TEST_METRICS = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
METRIC_NAMES = TEST_METRICS + ("coverage_90",)
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)", "coverage_90": "90% band coverage"}
LO, HI = sp.GRID.index(0.05), sp.GRID.index(0.95)
WINDOWS = ("development", "2026")
WINDOW_TITLES = m1255.WINDOW_TITLES
MIN_GROUP_DAYS = k.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
CHANGED = "state_defined"
NONZERO, OTHER = "decision days on which the state is defined", "decision days with no state"


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What (s3c-pd) is tested against: (s3c), (s3), then the benchmarks. No other model is a candidate here."""

    return [S3C, S3] + list(BENCHMARKS) if candidate == S3PD else []


# -- the arm's forecasts -------------------------------------------------------------------------------------------------


def candidate_days(panel, last: date, first: Optional[date]) -> List[date]:
    """The decision days the frames of #1255 walk: every panel day whose fifth target is on or before `last` (from `first`, in a test)."""

    dates = [row.date for row in panel]
    return [d for i, d in enumerate(dates) if i + max(sp.HORIZONS) < len(panel) and dates[i + max(sp.HORIZONS)] <= last and (first is None or d >= first)]


def s3pd_forecasts(frame, register, walk: s3c_pd.PdWalk):
    """The arm's forecasts on the frame's days, each cell clipped by (s3c)'s cap (`m1255.s3c_forecasts`): the state walk's quantiles, capped.

    Raises:
        ValueError: (s3) re-forecast in the state walk differs from the frame's (s3) on a cell, or a frame day is not in the walk.
    """

    s3 = frame.forecasts[S3]
    for d in frame.days:
        if d not in walk.forecasts:
            raise ValueError(f"the decision day {d} is in the frame and not in the state walk")
        if walk.s3[d] != s3[d]:
            raise ValueError(f"(s3) of the state walk differs from the frame's (s3) on the decision day {d}")
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


def term_use(frame, walk: s3c_pd.PdWalk, s3c, s3pd, levels=None) -> dict:
    """Where the state is defined and where the arm's forecast differs from (s3c)'s, by lead; the refits in which the term is active."""

    out: Dict[str, dict] = {str(h): {"cells": 0, "state_defined": 0, "differs_from_s3c": 0} for h in sp.HORIZONS}
    for d in frame.days:
        for h in sp.HORIZONS:
            row = out[str(h)]
            row["cells"] += 1
            if walk.values[d] is not None:
                row["state_defined"] += 1
            if list(s3c[d][h]) != list(s3pd[d][h]):
                row["differs_from_s3c"] += 1
    used = sorted({walk.fit_used[d] for d in frame.days})
    out["refits_in_use"] = len(used)
    out["refits_active"] = {str(h): sum(1 for r in used if walk.estimates[r][h].active) for h in sp.HORIZONS}
    out["decision_days"] = len(frame.days)
    out["days_with_state"] = sum(1 for d in frame.days if walk.values[d] is not None)
    if levels is not None:
        skipped = [s3c_pd.skipped_weeks(levels, d) for d in frame.days if walk.values[d] is not None]
        out["skipped_weeks"] = ({"decision_days": len(skipped), "mean": statistics.fmean(skipped), "max": max(skipped),
                                 "older_than_4_weeks": sum(1 for x in skipped if x > 4)} if skipped else None)
    return out


def fitted_effect(frame, walk: s3c_pd.PdWalk, levels) -> dict:
    """The fitted effect of the state term in bp per standard unit (the refit's coefficient times the scale at the anchor of the decision day), by
    lead and by regime of the decision day; the coefficient in standardised units by lead and refit; the mean absolute shift of the location in bp
    on the days the state is defined; and the size of a standard unit in USD billions."""

    per_unit: Dict[str, Dict[str, List[float]]] = {}
    shift: List[float] = []
    for d in frame.days:
        x = walk.values[d]
        for h in sp.HORIZONS:
            est = walk.estimates[walk.fit_used[d]][h]
            effect = est.coefficient * walk.scales[d]
            for key in ("all", frame.regime(d)):
                per_unit.setdefault(str(h), {}).setdefault(key, []).append(effect)
            if x is not None and h == 1:
                shift.append(abs(effect * x))
    by_lead = {h: {key: {"decision_days": len(v), "mean_bp_per_unit": statistics.fmean(v), "min": min(v), "max": max(v)}
                   for key, v in sorted(groups.items())} for h, groups in sorted(per_unit.items())}
    coefficients: Dict[str, List[float]] = {}
    for r in sorted({walk.fit_used[d] for d in frame.days}):
        for h in sp.HORIZONS:
            est = walk.estimates[r][h]
            coefficients.setdefault(str(h), []).append(est.coefficient if est.active else 0.0)
    coefficient = {h: {"refits": len(v), "active": sum(1 for x in v if x != 0.0), "median": statistics.median(v), "min": min(v), "max": max(v)}
                   for h, v in sorted(coefficients.items())}
    units = []
    for d in frame.days:
        week = s3c_pd.latest_defined_week(levels, d)
        if week is None:
            continue
        trailing = [levels[w] for w in levels if 0 < (week - w).days <= 7 * s3c_pd.TRAILING_WEEKS and levels[w] is not None]
        if len(trailing) >= s3c_pd.MIN_TRAILING and statistics.stdev(trailing) > 0.0:
            units.append(statistics.stdev(trailing))
    return {"effect_bp_per_unit_by_lead": by_lead, "coefficient_by_lead": coefficient,
            "mean_abs_shift_bp_lead1_on_state_days": statistics.fmean(shift) if shift else None,
            "standard_unit_usd_bn": {"decision_days": len(units), "mean": statistics.fmean(units) if units else None,
                                      "min": min(units) if units else None, "max": max(units) if units else None}}


# -- one window ----------------------------------------------------------------------------------------------------------


def build(window: str, panel, splits, registry, table, register, first: Optional[date], walk: s3c_pd.PdWalk):
    """The frame of a window with the models of `MODELS`: returns `(frame, notes, groups_fn, s3c, s3pd)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    s3pd = s3pd_forecasts(frame, register, walk)
    s3c = frame.forecasts[S3C]
    keep = {name: frame.forecasts[name] for name in BENCHMARKS + (S3, S3C)}
    frame.forecasts = {**keep, S3PD: {d: s3pd[d] for d in frame.days}}
    return frame, notes, groups_fn, s3c, frame.forecasts[S3PD]


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


def changed_term_groups(frame, walk: s3c_pd.PdWalk) -> List[Tuple[str, str, str, List[date]]]:
    """The decision days on which the state is defined against those on which it is not (the arm is (s3c) there, up to the refit)."""

    defined = [d for d in frame.days if walk.values[d] is not None]
    other = [d for d in frame.days if walk.values[d] is None]
    return [(CHANGED, NONZERO, "decision", defined), (CHANGED, OTHER, "decision", other)]


def run_window(window: str, panel, splits, registry, table, register, args, walk: s3c_pd.PdWalk, levels) -> dict:
    frame, notes, groups_fn, s3c, s3pd = build(window, panel, splits, registry, table, register, args.first, walk)
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
            jobs.append((split, label, grain, metric, S3PD, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {"notes": notes, "refits": len(walk.estimates), "groups": {}, "skipped_groups": skipped,
                    "term_use": term_use(frame, walk, s3c, s3pd, levels), "fitted_effect": fitted_effect(frame, walk, levels)}
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


def snapshot_record() -> dict:
    """The tracked snapshot, refused unless every byte is the manifest's (scripts/fetch_pd_financing_1296.py check), and its manifest."""

    fetch = _load("fetch_pd_financing_1296", "fetch_pd_financing_1296_in_1296")
    if fetch.check() != 0:
        raise SystemExit("the tracked primary dealer snapshot differs from its manifest")
    return json.loads((SNAPSHOT / "manifest.json").read_text(encoding="utf-8"))


def score(args) -> int:
    declaration = committed_declaration()
    source = json.loads(SOURCE_DECLARATION.read_text(encoding="utf-8"))
    manifest = snapshot_record()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_pd_1296")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    levels = s3c_pd.load_levels(SNAPSHOT)
    states = s3c_pd.decision_states(levels, [row.date for row in panel])
    s686.require_scored_days(candidate_days(panel, LAST_DAY, args.first), LAST_DAY)
    walk = s3c_pd.walk(panel, candidate_days(panel, LAST_DAY, args.first), table, states, registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    result: dict = {
        "issue": 1296, "declaration": str(DECLARATION.relative_to(REPO)), "source_declaration": str(SOURCE_DECLARATION.relative_to(REPO)),
        "panel_sha256": published_sha, "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": S3PD, "margin_bp": s3c_candidate.MARGIN_BP,
        "snapshot": {item["keyid"]: {"sha256": item["sha256"], "retrieved_at": item["retrieved_at"]} for item in manifest["files"]},
        "levels": {"weeks": len(levels), "with_level": sum(1 for v in levels.values() if v is not None), "first": min(levels).isoformat(),
                   "last": max(levels).isoformat(), "release_lag_business_days": s3c_pd.RELEASE_LAG_BUSINESS_DAYS,
                   "release_time": s3c_pd.RELEASE_TIME.strftime("%H:%M"), "trailing_weeks": s3c_pd.TRAILING_WEEKS,
                   "minimum_trailing_weeks": s3c_pd.MIN_TRAILING, "withheld_by_series": withheld_by_series()},
        "release_evidence": source["release"]["evidence"]["text"], "reading_rules": declaration["reading_rules"],
        "walk": {"decision_days": len(walk.forecasts), "skipped": len(walk.skipped), "refits": len(walk.estimates)}, "windows": {},
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, args, walk, levels)
    result["against_records"] = against_records(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def withheld_by_series() -> Dict[str, int]:
    """The number of as-of weeks each tracked series has withheld ('*')."""

    out = {}
    for key in s3c_pd.SERIES:
        rows = json.loads((SNAPSHOT / f"{key}.json").read_text(encoding="utf-8"))["pd"]["timeseries"]
        out[key] = sum(1 for r in rows if str(r["value"]).strip() == "*")
    return out


# -- the page ------------------------------------------------------------------------------------------------------------


cell = m1265.cell


def _vs(group: Optional[Mapping[str, object]], metric: str, reference: str) -> Optional[dict]:
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(S3PD, {}).get(reference)


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text} (s3c-pd) against (s3c) on grid CRPS: {cell(_vs(entry, 'grid_crps', S3C))}")
    return "; ".join(parts) + "."


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(f"{group[x]['means'][m]:.4f}" if x in ("brier_gt5", "coverage_90") else f"{group[x]['means'][m]:.3f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = ["| (s3c-pd) against | " + " | ".join(METRIC_TITLES[m] for m in TEST_METRICS) + " |", "|---|" + "---|" * len(TEST_METRICS)]
    for ref in plan(S3PD):
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
    """The closed 90% band's coverage of (s3), (s3c) and (s3c-pd): pooled, by regime, by lead and on the changed-term days (means)."""

    out = ["| group | days | (s3) | (s3c) | (s3c-pd) |", "|---|---|---|---|---|"]
    for split in ("pooled", "regime", "lead", CHANGED):
        for label, g in sorted(r["groups"].get(split, {}).items()):
            m = g["coverage_90"]["means"]
            if not m:
                continue
            out.append(f"| {split.replace('_', ' ')}: {label} | {g['days']} | {m[S3]:.3f} | {m[S3C]:.3f} | {m[S3PD]:.3f} |")
    return out


def effect_tables(fe: Mapping[str, object]) -> List[str]:
    out = ["| lead | regime of the decision day | decision days | mean effect (bp per standard unit) | smallest | largest |", "|---|---|---|---|---|---|"]
    for h, groups in fe["effect_bp_per_unit_by_lead"].items():
        for key, v in groups.items():
            out.append(f"| {h} | {key} | {v['decision_days']} | {v['mean_bp_per_unit']:+.3f} | {v['min']:+.3f} | {v['max']:+.3f} |")
    out += ["", "| lead | refits in use | refits with the term active | median coefficient (standardised units per standard unit) | smallest | largest |", "|---|---|---|---|---|---|"]
    for h, v in fe["coefficient_by_lead"].items():
        out.append(f"| {h} | {v['refits']} | {v['active']} | {v['median']:+.3f} | {v['min']:+.3f} | {v['max']:+.3f} |")
    unit = fe["standard_unit_usd_bn"]
    if unit["mean"] is not None:
        out += ["", f"One standard unit is the trailing-year standard deviation of the level: USD {unit['mean']:,.0f} bn on average over the {unit['decision_days']:,} "
                    f"decision days that have a state (smallest {unit['min']:,.0f}, largest {unit['max']:,.0f})."]
    if fe["mean_abs_shift_bp_lead1_on_state_days"] is not None:
        out += ["", f"Mean absolute shift of the location at lead 1 on the days the state is defined: {fe['mean_abs_shift_bp_lead1_on_state_days']:.3f} bp."]
    return out


def use_table(use: Mapping[str, object]) -> List[str]:
    out = ["| lead | cells | cells with a state | cells where (s3c-pd) differs from (s3c) | refits in use with the term active |", "|---|---|---|---|---|"]
    for h in sp.HORIZONS:
        u = use[str(h)]
        out.append(f"| {h} | {u['cells']} | {u['state_defined']} | {u['differs_from_s3c']} | {use['refits_active'][str(h)]} of {use['refits_in_use']} |")
    return out


def render(r: dict) -> str:
    lv = r["levels"]
    out = [
        "# (s3c-pd): (s3c) with primary dealers' reverse repo plus securities borrowed as a balance-sheet state input (#1296)", "",
        "**Does the level of primary dealers' reverse repo plus securities borrowed, against its own past year, improve (s3c)?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c) with a new public source, ledger item 72 on #1116. **Development "
        "data, not a verdict** (scoring protocol v1, #640). Her ruling of 28 October 2026 (chat, relayed on #1296) queued it and took the decision to add "
        "the source. **(s3c-pd)** is (s3c) with one state term added to (s3)'s fit: the z-score of the latest public week's level, the sum of four New York "
        "Fed primary dealer (FR 2004) Treasury totals (reverse repo and securities borrowed, Treasury excluding TIPS and TIPS), against the "
        f"{lv['trailing_weeks']} weeks before it. Every other term, the Huber fit, the ridge of 5 and the SRF cap at full allotment are (s3c)'s "
        "(`repo_model.s3c_pd`). Generated by `scripts/s3c_pd_1296.py page` from `docs/research/s3c-pd-1296/result.json`, not edited by hand; the arm is "
        f"declared in `{r['declaration']}` and the source in `{r['source_declaration']}` before any score.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "(s3c-pd). **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009, 20 October 2026), with the skill "
        "interval beside it. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x after "
        "2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days keep the **current method** "
        "(the group's days, scattered, resampled in date order as if consecutive), which #1221 questions and #1228 will decide. Where (s3c-pd) "
        "differs from its reference on few days of a group, some resamples have no long-run variance: the bound is then not computed, the "
        "unstudentized interval of mean d is given beside it, and no reading is taken from it.", "",
        "**What kind of look this is.** The development window and the 2026 days were already seen by the predecessors (#1145, #1229, #1252, #1255, "
        "#1265, #1273 to #1275). This is a check on an input she asked about, not evidence for a verdict. The regime that matters for the idea, the "
        "2026 days after the leverage-ratio change, is a short stretch of already-seen days.", "",
        "## The source and what it can say", "",
        f"The series are the New York Fed's `{'`, `'.join(s3c_pd.SERIES)}` (USD millions), snapshotted under `tests/fixtures/snapshots/nyfed-pd-financing/` "
        f"with their SHA-256 and retrieval instants in `manifest.json`. They run weekly (Wednesdays) from {lv['first']} to {lv['last']}; "
        f"{lv['with_level']:,} of {lv['weeks']:,} weeks have a level, because the New York Fed withholds ('*') some figures for confidentiality "
        "(weeks withheld by series: " + ", ".join(f"`{k}` {v}" for k, v in lv["withheld_by_series"].items()) + "). A week with any of the four withheld "
        "has no level; the level read is that of the latest released week that has one, carried over the withheld weeks (how many is reported "
        "below), and the term is 0 on a decision day with no state (fewer than " + str(lv["minimum_trailing_weeks"]) + " defined weeks in the year before the level read). "
        "**Release.** The New York Fed's page says: \"" + r["release_evidence"] + f"\" The declared instant is {lv['release_lag_business_days']} market "
        f"business days after the as-of Wednesday at {lv['release_time']} America/New_York, so a decision at 16:00 on the release Thursday reads the "
        "week before and the next business day's reads the new one (`tests/test_s3c_pd.py`). The page says \"approximately\" and no release archive was read. "
        "**Vintage.** The snapshot is the latest revised vintage the API served, not first prints. **Not the OFR route.** The Office of Financial Research "
        "chart the directive names draws on these series, but the OFR's data API serves the reverse-repo leg only to 2021-12-29, so the New York Fed's "
        "own API is used for both legs.", "",
        "**What the share of defined days means.** A state exists on a decision day only when at least " + str(lv["minimum_trailing_weeks"]) + " of the " +
        str(lv["trailing_weeks"]) + " weeks before the level read have a level. The tables below count the decision days that have one; on the others "
        "(s3c-pd) differs from (s3c) only through the refit.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        use = w["term_use"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {use['days_with_state']:,} of the {use['decision_days']:,} decision days have a state. "
                f"The state walk refit {r['walk']['refits']} times over the whole panel ({use['refits_in_use']} refits in use in this window).", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled) + ["", "### (s3c-pd) against each reference (pooled)", ""] + against_table(pooled) + [""]
        out += ["### Where the term acts", ""] + use_table(use) + [""]
        if use.get("skipped_weeks"):
            sk = use["skipped_weeks"]
            out += [f"The level read is the latest public one, carried over weeks the New York Fed withheld: on the {sk['decision_days']:,} decision days with a state it is "
                    f"{sk['mean']:.2f} weeks older than the latest public week on average (at most {sk['max']}), and {sk['older_than_4_weeks']:,} of those days read a level "
                    "more than 4 weeks older than it.", ""]
        for split, title in (("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"), ("lead", "By lead"),
                             (CHANGED, "By whether the decision day has a state"), ("target_day_type", "By calendar target-day type"), ("month", "By target month")):
            table = split_table(w, split, S3C)
            if table:
                out += [f"### {title}: (s3c-pd) against (s3c)", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type"), ("lead", "lead"), (CHANGED, "whether the decision day has a state")):
            table = split_table(w, split, S3)
            if table:
                out += [f"### By {title}: (s3c-pd) against (s3)", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type"), ("lead", "lead")):
            for ref in BENCHMARKS:
                table = split_table(w, split, ref)
                if table:
                    out += [f"### By {title}: (s3c-pd) against {LABELS[ref]}", ""] + table + [""]
        out += ["### 90% band coverage beside (s3c)'s (means; closed band q05 to q95; nominal 0.90)", ""] + coverage_table(w) + [""]
        out += ["### The fitted effect of the state term in bp per standard unit", "", "The effect is the refit's coefficient times the scale at the anchor "
                "of the decision day, by lead and by regime of the decision day; the forecast adds it times the state.", ""] + effect_tables(w["fitted_effect"]) + [""]
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
        "**Question 1. Register the source?** The series is declared in `metadata/sources_pd_financing_1296.json` with a proposed registry entry; "
        "`metadata/sources.json` is unchanged because it is pinned under the final-test pre-registration (#1276, #1241). Registering it is a change to "
        "that file and to the pinned checksums, and is yours.", "",
        "**Question 2. Some weeks have no level, and the level read can be old.** The New York Fed withholds some totals, so the level read is carried over "
        "withheld weeks without a limit on their number (the directive's 'latest public level', read literally), and a minimum of defined weeks in the "
        "year decides whether a state exists. Both were declared from how many weeks are withheld, not from a score. A limit on the age of the level, "
        "or a different minimum, is a threshold nobody has set. The tables above give the age of the level read and the days with a state.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Read the result as it stands, leave the source unregistered, queue nothing further on this input** (default). (s3c) stays the candidate; "
        "nothing changes.",
        "2. **Queue a follow-up arm with a limit on the age of the level you set**, declared as its own arm with its own staleness rule and leakage test.",
        "3. **Ask for the source to be registered** in a pull request that moves the pre-registration's checksums under your own GO.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3) and the state arm, cap it as (s3c) is capped, and score (s3c-pd) on both windows")
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
