"""(s3c-gse-roll): the GSE ramp with the payment-day roll, scored beside (s3c-gse), (s3c), (s3), B1, B1' and B2 (#1287; H5 step 3; finding #1285;
ledger item 70 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_gse_roll_1287.json`, which this script refuses to read unless it is committed and unchanged. The arm is `repo_model.s3c_gse_roll`:
(s3) of #1145 walked on a term table whose `dom_19_23` slot holds the GSE ramp of #1274 with one change, the 25th's value read on the payment day
(the first business day on or after the 25th, `repo_model.data.market_holidays()` and weekends), then capped where `repo_model.s3c_candidate` caps
(s3). The control is (s3c-gse) of #1274, re-run unchanged in the same run: `scripts/s3c_gse_1274.py` is loaded as it stands and supplies the frames
(#1255's), the walk, the cap, the cells, the effect arithmetic and the control's forecasts.

(s3) is walked three times over every decision day from the start of the panel to the last with five targets on or before 2026-09-03: on the base
table (it must equal the frames' (s3) cell for cell on every scored decision day, or no record is written), on the (s3c-gse) table and on the
(s3c-gse-roll) table. The control's pooled means are compared with `docs/research/s3c-gse-1274/result.json`. The two ramps differ only on the payment
days of the months whose 25th is not a business day; the study reports how many target days that is.

Measures: grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp); scoring protocol v1's
studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill interval beside; pooled, by lead, by regime
(development window) or target month (2026), by pressure-day type, on the rolled payment days against the other days, and on the days the changed
term is non-zero; the 90% band's coverage; the fitted effect of the term in bp by regime.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_gse_roll_1287.py score --panel PUB.csv --output docs/research/s3c-gse-roll-1287/result.json
    PYTHONPATH=src python3 scripts/s3c_gse_roll_1287.py page \\
        --score docs/research/s3c-gse-roll-1287/result.json --output docs/research/s3c-gse-roll-1287-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, alias: str):
    """Load `scripts/<name>.py` as a module registered under `alias`."""

    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, data, metrics, policy_events, s3c_candidate, s3c_gse, s3c_gse_roll, turn_days  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal  # noqa: E402
from repo_model import spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import require_exploratory_window  # noqa: E402

#: #1274's script, as it stands (and through it #1255's, #1241's and #1229's), loaded under an alias of its own.
m74 = _load("s3c_gse_1274", "s3c_gse_1274_in_1287")
k, c, s686, s761, d1222 = m74.k, m74.c, m74.s686, m74.s761, m74.d1222

DECLARATION = REPO / "metadata" / "s3c_gse_roll_1287.json"
RECORD_1274 = REPO / "docs" / "research" / "s3c-gse-1274" / "result.json"
SEED = 1287
LAST_DAY = m74.LAST_DAY
WINDOWS = m74.WINDOWS
S3, S3C, S3CG, S3CGR = m74.S3, m74.S3C, m74.S3CG, "sc_s3c_gse_roll"
B1P = m74.B1P
BENCHMARKS = m74.BENCHMARKS
MODELS = BENCHMARKS + (S3, S3C, S3CG, S3CGR)
#: What (s3c-gse-roll) is tested against, the control first.
REFERENCES = (S3CG, S3C, S3) + BENCHMARKS
LABELS = {**m74.LABELS, S3CGR: "(s3c-gse-roll)"}
METRIC_NAMES, METRIC_TITLES = m74.METRIC_NAMES, m74.METRIC_TITLES
TAU, RATE = m74.TAU, m74.RATE
COVERAGE_MODELS = (S3CGR, S3CG, S3C, S3)
MIN_GROUP_DAYS, BLOCK, CELL_BLOCK = m74.MIN_GROUP_DAYS, m74.BLOCK, m74.CELL_BLOCK
S3_ARM, TERM = m74.S3_ARM, m74.TERM
WINDOW_TITLES = m74.WINDOW_TITLES
MOVED_SPLIT = "payment_day"
MOVED_DAYS, OTHER_DAYS = "rolled payment days (the roll changes the term)", "other target days"
RAMP_SPLIT = "ramp_day"
RAMP_DAYS, NON_RAMP_DAYS = "target days 19th to the payment day (the term is non-zero)", "other target days"
PRIOR = 1274


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def in_roll(t: date) -> bool:
    """Whether (s3c-gse-roll)'s term is non-zero on target day `t`."""

    return s3c_gse_roll.roll_ramp(t) > 0.0


def is_moved(t: date) -> bool:
    """Whether the roll changes the term on target day `t`: the payment day of a month whose 25th is not a business day."""

    return s3c_gse_roll.roll_ramp(t) != s3c_gse.ramp(t)


# -- the groups --------------------------------------------------------------------------------------------------------------


def groups_of(frame, window: str) -> List[Tuple[str, str, str, List[date]]]:
    """`(split, label, grain, members)`: pooled; by lead; by regime (development) or target month (2026); by pressure-day type; the rolled
    payment days against the other target days; and the days the rolled term is non-zero against the others."""

    out = [g for g in m74.groups_of(frame, window) if g[0] != m74.RAMP_SPLIT]
    targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
    out.append((MOVED_SPLIT, MOVED_DAYS, "target", [t for t in targets if is_moved(t)]))
    out.append((MOVED_SPLIT, OTHER_DAYS, "target", [t for t in targets if not is_moved(t)]))
    out.append((RAMP_SPLIT, RAMP_DAYS, "target", [t for t in targets if in_roll(t)]))
    out.append((RAMP_SPLIT, NON_RAMP_DAYS, "target", [t for t in targets if not in_roll(t)]))
    return out


def moved_rows(frame, series: Mapping[str, Mapping[date, float]]) -> List[dict]:
    """Each target day the roll moves: the realised spread, the term in the control and in the arm, and the grid CRPS of the arms on it."""

    targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
    return [{"date": t.isoformat(), "spread_bp": frame.outcome[t], "control_term": s3c_gse.ramp(t), "arm_term": s3c_gse_roll.roll_ramp(t),
             "pressure_day_type": frame.day_type(t), "grid_crps": {m: series[m][t] for m in (S3, S3C, S3CG, S3CGR)}}
            for t in targets if is_moved(t)]


# -- the tests, in parallel --------------------------------------------------------------------------------------------------

_STATE: Dict = {}


def plan(candidate: str) -> List[str]:
    """What an arm is tested against: only (s3c-gse-roll) is a candidate here."""

    return list(REFERENCES) if candidate == S3CGR else []


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
        if all(series[candidate][d] == series[name][d] for d in days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = unstudentized(series, candidate, name, days)
    return (split, label, metric, candidate), out


def _interval_task(job):
    key, values, block = job
    n = len(values)
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx), n, block_length=block, seed=SEED, replications=_STATE["reps"])
    return key, [low, high]


def _dispatch(job):
    kind, payload = job
    return kind, (_pairs_task(payload) if kind == "pairs" else _interval_task(payload))


def run_jobs(jobs, workers: int):
    import multiprocessing

    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- one window --------------------------------------------------------------------------------------------------------------


def run_window(window: str, panel, splits, registry, table, register, walks: Mapping[str, sc.Walk], args) -> dict:
    frame, notes, mine = m74.build(window, panel, splits, registry, table, register, args.first)
    checked = m74.same_as_frame(frame, walks["base"])
    _ramped, control = m74.gse_forecasts(frame, walks["gse"], register)
    ramped, capped = m74.gse_forecasts(frame, walks["roll"], register)
    frame.forecasts[S3CG], frame.forecasts[S3CGR] = control, capped
    labels = {t: frame.day_type(t) for t in {frame.target(d, h) for d in frame.days for h in sp.HORIZONS}}

    cells = {m: m74.cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    groups = groups_of(frame, window)
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
        for metric in METRIC_NAMES:
            jobs.append(("pairs", (split, label, grain, metric, S3CGR, tuple(members))))
    cover = m74.coverage_groups(frame, sorted(cells[S3CGR][RATE]))
    for group, keys in cover.items():
        for m in COVERAGE_MODELS:
            jobs.append(("interval", ((group, m), [cells[m][RATE][x] for x in keys], m74.block_of(group))))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, mem) for s_, l_, g, mem in groups}
    result: dict = {"notes": notes, "refits": len(walks["roll"].estimates), "groups": {}, "skipped_groups": skipped, "coverage": {},
                    "walk_equals_frame_days": checked,
                    "effect": {"roll": m74.effect_cells(frame, walks["roll"], s3c_gse_roll.roll_ramp),
                               "gse_ramp": m74.effect_cells(frame, walks["gse"], s3c_gse.ramp),
                               "flat_19_23": m74.effect_cells(frame, walks["base"], lambda t: 1.0 if 19 <= t.day <= 23 else 0.0)}}
    for kind, payload in done:
        if kind == "pairs":
            (split, label, metric, candidate), out = payload
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = out
        else:
            (group, m), interval = payload
            result["coverage"].setdefault(group, {}).setdefault(m, {})["interval"] = interval
    for group, keys in cover.items():
        for m in COVERAGE_MODELS:
            values = [cells[m][RATE][x] for x in keys]
            result["coverage"][group][m].update({"rate": sum(values) / len(values), "cells": len(values)})
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in METRIC_NAMES:
                if metric in entry:
                    ser = series[(grain, metric)]
                    entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    # the groups too small to test still get their means
    for split, label, grain, members in groups:
        if f"{split}/{label}" in skipped and members:
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
            for metric in METRIC_NAMES:
                ser = series[(grain, metric)]
                entry.setdefault(metric, {"means": {}, "vs": {}})["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    targets = sorted(labels)
    moved = [t for t in targets if is_moved(t)]
    result["pressure_day_type_counts"] = {x: sum(1 for v in labels.values() if v == x) for x in sorted(set(labels.values()))}
    result["target_days"] = {"all": len(targets), "ramp": sum(1 for t in targets if in_roll(t)), "moved_by_the_roll": len(moved),
                             "control_ramp": sum(1 for t in targets if s3c_gse.ramp(t) > 0.0)}
    result["moved_rows"] = moved_rows(frame, series[("target", "grid_crps")])
    result["moved_cells"] = sum(1 for d in frame.days for h in sp.HORIZONS if is_moved(frame.target(d, h)))
    result["positive_days_5"] = sum(1 for t in targets if data.exceeds_bp(frame.outcome[t], TAU))
    result["cells_where_roll_differs_from_gse"] = sum(1 for d in frame.days for h in sp.HORIZONS if frame.forecasts[S3CGR][d][h] != frame.forecasts[S3CG][d][h])
    result["cells_where_roll_differs_from_s3c"] = sum(1 for d in frame.days for h in sp.HORIZONS if frame.forecasts[S3CGR][d][h] != frame.forecasts[S3C][d][h])
    result["cells"] = len(frame.days) * len(sp.HORIZONS)
    result["before_full_allotment_is_the_roll_walk"] = all(
        list(capped[d][h]) == list(ramped[d][h]) for d in frame.days for h in sp.HORIZONS
        if s3c_candidate.cap_line(register, k.decision_instant(d), frame.target(d, h)) is None)
    return result


def against_1274(results: Mapping[str, dict]) -> dict:
    """The pooled means here against #1274's record, on each window: the control, (s3), (s3c), B1, B1' and B2 must reproduce it."""

    out: Dict[str, dict] = {}
    if not RECORD_1274.exists():
        return out
    record = json.loads(RECORD_1274.read_text(encoding="utf-8"))["windows"]
    for window in WINDOWS:
        if window not in results:
            continue
        there = record[window]["groups"]["pooled"]["all decision days"]
        here = results[window]["groups"]["pooled"]["all decision days"]
        out[window] = {"days_here": here["days"], "days_there": there["days"], "metrics": {
            m: {x: {"here": here[m]["means"][x], "there": there[m]["means"][x], "difference": here[m]["means"][x] - there[m]["means"][x]}
                for x in (S3, S3C, S3CG) + BENCHMARKS} for m in METRIC_NAMES}}
    return out


def months_moved() -> dict:
    """The months from July 2018 to August 2026 whose 25th is not a business day (#1285 counts 37 of 98), in the development window and in 2026."""

    months = [(y, m) for y in range(2018, 2027) for m in range(1, 13) if date(2018, 7, 1) <= date(y, m, 1) <= date(2026, 8, 1)]
    moved = [(y, m) for y, m in months if s3c_gse_roll.payment_day(y, m).day != s3c_gse_roll.LAST_DAY]
    return {"months": len(months), "moved": len(moved), "moved_development": sum(1 for y, _ in moved if y < 2026), "moved_2026": sum(1 for y, _ in moved if y == 2026),
            "payment_days": [s3c_gse_roll.payment_day(y, m).isoformat() for y, m in moved]}


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in m74.load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_gse_roll_1287")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    table = cal.TermTable(panel, announcements, decision_time=c.DECISION_TIME)
    tables = {"base": table, "gse": s3c_gse.GseTermTable(panel, announcements, decision_time=c.DECISION_TIME),
              "roll": s3c_gse_roll.RollTermTable(panel, announcements, decision_time=c.DECISION_TIME)}
    dates = [row.date for row in panel]
    days = m74.candidate_days(panel, dates, args.first)
    walks = {name: m74.walk_s3(panel, days, t, splits, registry) for name, t in tables.items()}
    result: dict = {
        "issue": 1287, "finding": 1285, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": S3CGR, "control": S3CG,
        "margin_bp": s3c_candidate.MARGIN_BP, "ramp": {"first_day": s3c_gse_roll.FIRST_DAY, "last_day": s3c_gse_roll.LAST_DAY, "replaces": TERM},
        "months": months_moved(), "walk_days": len(days),
        "refit_effects": {name: m74.refit_effects(walks[name]) for name in ("roll", "gse", "base")},
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, walks, args)
    result["against_1274"] = against_1274(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ----------------------------------------------------------------------------------------------------------------

words, cell = m74.words, m74.cell


def _vs(group: Optional[Mapping[str, object]], metric: str, reference: str) -> Optional[dict]:
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(S3CGR, {}).get(reference)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(f"{group[x]['means'][m]:.4f}" if x.startswith("brier") else f"{group[x]['means'][m]:.3f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = ["| (s3c-gse-roll) against | " + " | ".join(METRIC_TITLES[m] for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for ref in REFERENCES:
        out.append(f"| {LABELS[ref]} | " + " | ".join(cell(_vs(group, m, ref)) for m in METRIC_NAMES) + " |")
    return out


def split_table(w: Mapping[str, object], split: str, reference: str, metrics_: Sequence[str]) -> List[str]:
    labels = w["groups"].get(split, {})
    order = c.REGIMES if split == "regime" else sorted(labels)
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in metrics_) + " |", "|---|---|" + "---|" * len(metrics_)]
    for label in order:
        if label not in labels:
            continue
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(
            "not tested (fewer than 20 days)" if f"{split}/{label}" in w["skipped_groups"] else cell(_vs(g, m, reference)) for m in metrics_) + " |")
    return out if len(out) > 2 else []


def means_split_table(w: Mapping[str, object], split: str) -> List[str]:
    """The mean grid CRPS and Brier score of (s3c), (s3c-gse) and (s3c-gse-roll) in each group of a split, tested or not."""

    labels = w["groups"].get(split, {})
    arms = (S3C, S3CG, S3CGR)
    cols = [(x, m) for x in ("grid_crps", "brier_gt5") for m in arms]
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(f"{METRIC_TITLES[x]} {LABELS[m]}" for x, m in cols) + " |", "|---|---|" + "---|" * len(cols)]
    for label in (c.REGIMES if split == "regime" else sorted(labels)):
        if label not in labels:
            continue
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[x]['means'][m]:.4f}" for x, m in cols) + " |")
    return out if len(out) > 2 else []


def coverage_table(cover: Mapping[str, dict]) -> List[str]:
    out = ["| group | cells | " + " | ".join(f"{LABELS[m]} 90% band [90% interval]" for m in COVERAGE_MODELS) + " |", "|---|---|" + "---|" * len(COVERAGE_MODELS)]
    for group, models in cover.items():
        out.append(f"| {group} | {models[S3CGR]['cells']:,} | " + " | ".join(
            f"{models[m]['rate']:.3f} [{models[m]['interval'][0]:.3f}, {models[m]['interval'][1]:.3f}]" for m in COVERAGE_MODELS) + " |")
    return out


def effect_table(effect: Mapping[str, dict], title: str) -> List[str]:
    """The term's fitted effect in bp by regime of the target day: bp per unit of the term (the shift on the payment day for the ramps, on any
    day of the 19th to 23rd for the flat flag) pooled over leads, the share of cells whose fit holds the term, and the mean shift applied on the
    target days that carry it."""

    out = [f"| {title}: regime of the target day | cells | fit holds the term | mean effect, bp per unit of the term | cells carrying the term | mean shift applied there, bp |",
           "|---|---|---|---|---|---|"]
    for regime in list(c.REGIMES) + ["all regimes"]:
        e = effect.get(regime, {}).get("all")
        if e is None:
            continue
        applied = "n/a" if e["mean_applied_bp"] is None else f"{e['mean_applied_bp']:+.3f}"
        out.append(f"| {regime} | {e['cells']:,} | {e['with_term'] / e['cells']:.1%} | {e['mean_bp_per_unit']:+.3f} | {e['carry']:,} | {applied} |")
    return out


def effect_by_lead(w: Mapping[str, object]) -> List[str]:
    out = ["| lead | (s3c-gse-roll), bp per unit (the payment day) | (s3c-gse), bp per unit (the 25th) | (s3) flat 19th-23rd, bp per day |", "|---|---|---|---|"]
    for h in sp.HORIZONS:
        a, b, f = (w["effect"][x]["all regimes"][str(h)] for x in ("roll", "gse_ramp", "flat_19_23"))
        out.append(f"| h={h} | {a['mean_bp_per_unit']:+.3f} | {b['mean_bp_per_unit']:+.3f} | {f['mean_bp_per_unit']:+.3f} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        pooled = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        if pooled is None:
            continue
        parts.append(f"{text}, grid CRPS, (s3c-gse-roll) against (s3c-gse): {cell(_vs(pooled, 'grid_crps', S3CG))}; against (s3c): {cell(_vs(pooled, 'grid_crps', S3C))}")
    return "; ".join(parts) + "."


def moved_sentence(r: Mapping[str, object]) -> str:
    """Where the arm moves the score: on the rolled payment days and the other days against (s3c-gse), by window (current-method intervals)."""

    parts = []
    for window, text in (("2026", "the 2026 days"), ("development", "the development window")):
        w = r["windows"].get(window)
        groups = w.get("groups", {}).get(MOVED_SPLIT) if w else None
        if not groups:
            continue
        for label, name in ((MOVED_DAYS, "on the rolled payment days"), (OTHER_DAYS, "on the other days")):
            g = groups.get(label)
            if g is None:
                continue
            body = ", ".join(f"{METRIC_TITLES[m]} {cell(_vs(g, m, S3CG))}" for m in ("grid_crps", "upper_tail_twcrps")) \
                if f"{MOVED_SPLIT}/{label}" not in w["skipped_groups"] else f"not tested (fewer than {MIN_GROUP_DAYS} days; listed below)"
            parts.append(f"{text}, {name} ({g['days']} target days): {body}")
    return ("Against (s3c-gse), on the days the roll changes the term and on the others (the intervals of these groups keep the current method, "
            "#1221): " + "; ".join(parts) + ".")


def moved_table(rows: Sequence[dict]) -> List[str]:
    out = ["| rolled payment day | pressure-day type | SOFR - IORB, bp | term in (s3c-gse) | term in (s3c-gse-roll) | grid CRPS (s3) | (s3c) | (s3c-gse) | (s3c-gse-roll) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for x in rows:
        g = x["grid_crps"]
        out.append(f"| {x['date']} | {x['pressure_day_type']} | {x['spread_bp']:+.1f} | {x['control_term']:.3f} | {x['arm_term']:.3f} | "
                   f"{g[S3]:.3f} | {g[S3C]:.3f} | {g[S3CG]:.3f} | {g[S3CGR]:.3f} |")
    return out


def reproduction_sentence(ag: Mapping[str, dict], window: str) -> str:
    a = ag[window]
    worst = max(abs(v["difference"]) for rows in a["metrics"].values() for v in rows.values())
    return (f"Reproduction of #1274 (same frame, control re-run unchanged): the largest absolute difference in a pooled mean here against there, over "
            f"{len(a['metrics'])} metrics and {len(next(iter(a['metrics'].values())))} models, is {worst:.2e} ({a['days_here']} days here, {a['days_there']} there).")


def render(r: dict) -> str:
    mm = r["months"]
    out = [
        "# (s3c-gse-roll): the GSE ramp with the payment-day roll, on (s3c) (#1287)", "",
        "**Does reading the ramp's peak on the payment day, when the 25th is not a business day, improve (s3c-gse)?** " + headline(r), "", moved_sentence(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c); ledger item 70 on #1116; finding #1285. **Development data, not a "
        "verdict** (scoring protocol v1, #640). Her ruling of 28 October 2026 (chat, relayed on #1285 and #1287): test the finding with a development re-run "
        "of the ramp with the payment-day roll. **(s3c) stays the candidate until she rules on the result.** Nothing is registered or published, "
        "(s3c-gse)'s page (#1277) is not edited and no claim changes. Generated by `scripts/s3c_gse_roll_1287.py page` from "
        f"`docs/research/s3c-gse-roll-1287/result.json`, not edited by hand; declared in `{r['declaration']}` before any score. The page cites no source for "
        "the idea beyond her ruling and compares with no outside figure.", "",
        "**The arm.** (s3c-gse) (#1274) reads a ramp on the calendar date: (d - 18) / 7 on day d from the 19th to the 25th, 0 otherwise. The agencies pay on the "
        "25th, or on the next business day when the 25th is a weekend or a holiday, so in those months the ramp reads 0 on the payment day and peaks on the day "
        "before. **(s3c-gse-roll)** reads the 25th's value (7/7) on the payment day, the first business day on or after the 25th (`repo_model.data.market_holidays()` and "
        "weekends); the days before keep their own date's value, the 25th (which has no row in such a month) reads nothing, and the days after the payment day read 0. "
        "When the 25th is a business day the term is (s3c-gse)'s. The rule is declared and not tuned. It is read from the target row's own date and the holiday table "
        "alone, on direct pairs (`repo_model.s3c_gse_roll`). Every other term, the Huber fit, the ridge of 5 and the cap at the line from full allotment are (s3c)'s. "
        "**The control** is (s3c-gse), re-run unchanged in this run.", "",
        f"**How many days the roll moves.** From July 2018 to August 2026 the 25th is not a business day in {mm['moved']} of {mm['months']} months "
        f"({mm['moved_development']} before 2026 and {mm['moved_2026']} in 2026), the count of #1285. The two terms differ on one target day in each: the payment day. "
        + " ".join(f"On the {w} {('window' if w == 'development' else 'days')}: {r['windows'][w]['target_days']['moved_by_the_roll']} of "
                   f"{r['windows'][w]['target_days']['all']:,} target days ({r['windows'][w]['moved_cells']:,} of {r['windows'][w]['cells']:,} scored cells have a moved "
                   f"target); (s3c-gse-roll)'s forecast differs from the control's in {r['windows'][w]['cells_where_roll_differs_from_gse']:,} cells (the walk refits "
                   "with the changed training column, so a forecast can move on other days too)." for w in WINDOWS if w in r["windows"]), "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "(s3c-gse-roll). **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a "
        "Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated "
        "about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days (a regime, a month, "
        "a pressure-day type, the rolled payment days, the ramp days) keep the **current method** (the group's days, scattered, resampled in date order as if "
        "consecutive), which #1221 questions and #1228 will decide; no pressure-day type is read from them. Where two arms differ on few days of a group, some "
        "resamples have no long-run variance: the bound is then not computed, the unstudentized interval of mean d is given beside it, and no reading is taken "
        "from that. Groups of fewer than 20 days are listed with their means and not tested.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, the #151 final test, #1229, #1252, #1255 and #1274. This is a check on an arm "
        "of the candidate she chose, not evidence for a verdict. Before full allotment (s3c) is (s3), so on those days the arms differ from (s3c) only through "
        "the ramp.", ""]
    ag = r.get("against_1274")
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {w['refits']} refits of (s3) on the roll table. The base-table walk "
                f"of (s3) equals #1255's frame cell for cell on all {w['walk_equals_frame_days']:,} scored decision days (the script refuses to write a record otherwise). "
                f"Cells where (s3c-gse-roll) differs from (s3c-gse): {w['cells_where_roll_differs_from_gse']:,} of {w['cells']:,}; from (s3c): "
                f"{w['cells_where_roll_differs_from_s3c']:,}; cells before full allotment equal the roll walk's (s3): "
                f"{'yes' if w['before_full_allotment_is_the_roll_walk'] else 'NO'}. Target days: {w['target_days']['all']:,}, of which {w['target_days']['ramp']:,} "
                f"carry the rolled term and {w['target_days']['moved_by_the_roll']} are rolled payment days; target days with SOFR - IORB above +5 bp: {w['positive_days_5']}.", ""]
        if ag and window in ag:
            out += [reproduction_sentence(ag, window), ""]
        out += ["### Mean scores (pooled)", ""] + mean_table(pooled) + ["", "### (s3c-gse-roll) against each reference (pooled)", ""] + against_table(pooled) + [""]
        out += ["### The rolled payment days, one by one", "",
                "The target days on which the roll changes the term, with the grid CRPS (mean over the leads that reach the day) of each arm on that day.", ""]
        out += moved_table(w["moved_rows"]) + [""]
        out += ["### 90% band coverage beside the others'", "",
                "The share of cells in which the realised spread lies in the q05-q95 band (nominal 0.90), with the stationary-bootstrap interval of #1229 "
                "(cells in date order).", ""] + coverage_table(w["coverage"]) + [""]
        out += ["### The fitted effect of the changed term, in bp", "",
                "The coefficient of the fit in use at each decision, in scale units, times the scale at the decision's anchor, averaged over the scored "
                "(decision day, lead) cells of each regime of the target day. For the two ramps, bp per unit is the shift on the payment day (the 25th in "
                "(s3c-gse)); the shift on the 22nd is 4/7 of it. For (s3)'s flat flag it is the shift on each day of the 19th to 23rd. \"Fit holds the term\" is the "
                "share of cells whose fit has the term.", ""]
        out += effect_table(w["effect"]["roll"], "(s3c-gse-roll) rolled ramp") + [""] + effect_table(w["effect"]["gse_ramp"], "(s3c-gse) ramp") + [""]
        out += effect_table(w["effect"]["flat_19_23"], "(s3) flat 19th-23rd") + [""] + ["By lead, all regimes:", ""] + effect_by_lead(w) + [""]
        for split, title in ((MOVED_SPLIT, "the rolled payment days"), (RAMP_SPLIT, "the days the changed term is non-zero"), ("regime", "regime"),
                             ("month", "target month"), ("pressure_day_type", "pressure-day type of the target day"), ("lead", "lead")):
            for ref in (S3CG, S3C, S3):
                table = split_table(w, split, ref, METRIC_NAMES)
                if table:
                    out += [f"### By {title}: (s3c-gse-roll) against {LABELS[ref]}", ""] + table + [""]
        for split, title in ((MOVED_SPLIT, "the rolled payment days"), (RAMP_SPLIT, "the days the changed term is non-zero"), ("regime", "regime"),
                             ("pressure_day_type", "pressure-day type"), ("lead", "lead")):
            for ref in BENCHMARKS:
                table = split_table(w, split, ref, ("grid_crps", "upper_tail_twcrps"))
                if table:
                    out += [f"### By {title}: (s3c-gse-roll) against {LABELS[ref]}", ""] + table + [""]
        for split, title in ((MOVED_SPLIT, "the rolled payment days"), (RAMP_SPLIT, "the ramp days"), ("regime", "regime"), ("month", "target month"),
                             ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split)
            if table:
                out += [f"### Mean scores of (s3c), (s3c-gse) and (s3c-gse-roll) by {title}", ""] + table + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. What follows from this result.** (s3c) stays the H5 candidate, and (s3c-gse) (#1277) stays as it stands, with the roll recorded as the limit "
        "this study measured. Whether either ramp is carried forward, and whether the sign of the fitted effect (negative: cash lent into repo before the "
        "payment, not the day it leaves) says the peak belongs on another day altogether, is a choice for her, and it rests on days already seen.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests the rolled ramp prospectively**, on the confirmation days only, under the scoring protocol.",
        "3. **Hold this result until the other arms on (s3c) are in, and rule on them together** (which combine, in what order, and on what evidence).", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3) on the base, ramp and roll tables, cap it, and score (s3c-gse-roll) on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of the unstudentized and the coverage intervals")
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
