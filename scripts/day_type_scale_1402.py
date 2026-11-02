"""(s3c-ann-net-typed) and (s3c-ann-net-pooled): a residual scale per pressure-day type of the target day, beside the frozen candidate (s3c-ann-net), at the
18:00 decision instant (#1402; H5 step 3; her ruling of 2 November 2026 on avenue #1387, option 1).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/day_type_scale_1402.json`, which this script refuses to read unless it is committed and unchanged. The candidate (s3c-ann-net) is frozen by the
same ruling: the result goes to the known limits of the registration and does not reopen the candidate.

The candidate's quantiles are `centre + scale * (shift + pool_j)`, the pool being the 23 quantiles of the refit's standardised residuals. Each arm
rescales the pool's spread about its median by a multiplier per pressure-day type of the target day (`repo_model.day_type_scale`): the typed arm one for
each of turn, quarter_end_turn, tax_date, year_end and ordinary; the pooled arm one for all four non-ordinary types together. The multiplier is the
root-mean-square ratio of that type's training residuals to all of them, per refit and lead, computed from the walk's own estimates after it has run
(`StateEstimate.residuals`, `.targets`); the walk is `spread_mr_state_calendar.walk` on direct pairs, unchanged, and the SRF cap is applied after the
multiplier as to the candidate.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`) on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with
the skill interval beside, against the candidate and against B1'*, split by lead, regime and pressure-day type (and the union of the non-ordinary types);
the coverage of the central 50% and 90% bands by regime, pressure-day type and the calendar target-day types of #1363; and the clustering of the band
misses on the reading in force at the base of the pull request (#1363's, with the protocol's thinned table). The 2026 development days are a window of
their own.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/day_type_scale_1402.py score --panel PUB.csv \\
        --output docs/research/day-type-scale-1402/result.json
    PYTHONPATH=src python3 scripts/day_type_scale_1402.py page \\
        --score docs/research/day-type-scale-1402/result.json --output docs/research/day-type-scale-1402-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
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
        return held
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, day_type_scale as dts, policy_events, s3c_announced, s3c_net  # noqa: E402
from repo_model import b1_calendar as b1c  # noqa: E402
from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import scoring_protocol as sp, turn_days  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1321's script (and through it #1288's, #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker
#: pool's tasks does not meet another test module's copy. #1363's, for its coverage and clustering machinery.
m1321 = _load("s3c_flagnet_gross_1321", "s3c_flagnet_gross_1321_in_1402")
m1288, m1273, m1255, k, c, s686, s761 = m1321.m1288, m1321.m1273, m1321.m1255, m1321.k, m1321.c, m1321.s686, m1321.s761
m1363 = _load("candidate_calibration_1363", "candidate_calibration_1363_in_1402")
load_daily_panel = m1321.load_daily_panel

DECLARATION = REPO / "metadata" / "day_type_scale_1402.json"
RECORD_1314 = REPO / "docs" / "research" / "s3c-ann-net-1800-1314" / "announced-settlement-1800.json"
SEED = 1402
LAST_DAY = EXPLORATORY_END
WINDOWS = m1288.WINDOWS
WINDOW_LAST = m1288.WINDOW_LAST
WINDOW_TITLES = m1288.WINDOW_TITLES
ANNNET = m1288.ANNNET
TYPED, POOLED = dts.ARM_NAMES["typed"], dts.ARM_NAMES["pooled"]
B1PS = "B1_prime_star"
ARMS = (TYPED, POOLED)
MODE_OF = {TYPED: "typed", POOLED: "pooled"}
MODELS = (ANNNET, TYPED, POOLED, B1PS)
LABELS = {ANNNET: "(s3c-ann-net)", TYPED: "(s3c-ann-net-typed)", POOLED: "(s3c-ann-net-pooled)", B1PS: "B1'*"}
SHORT = LABELS
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
NON_ORDINARY = "non-ordinary (turn, quarter_end_turn, tax_date, year_end)"
REPS = 2000
COVERAGE_MODELS = (ANNNET, TYPED, POOLED)
ARM_NET = s3c_announced.ANN_NET_ARM.name


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What a model is tested against: both arms against the candidate and B1'*, the candidate against B1'* (the gap the arms start from)."""

    if candidate in ARMS:
        return [ANNNET, B1PS]
    return [B1PS] if candidate == ANNNET else []


# -- the arms ------------------------------------------------------------------------------------------------------------


def type_of_rows(panel, splits) -> Dict[int, str]:
    """The pressure-day type of every panel row, `turn_days.reporting_day_type` on the row's own calendar columns (a function of its date).

    Raises:
        ValueError: a row's type is not one of `dts.TYPES`, or a calendar column is missing (as `SplitDeclaration.day_type`).
    """

    out: Dict[int, str] = {}
    for i, row in enumerate(panel):
        label = turn_days.reporting_day_type(splits, row.date, row.values)
        if label not in dts.TYPES:
            raise ValueError(f"{row.date}: pressure-day type {label!r} is not one of {dts.TYPES}")
        out[i] = label
    return out


def refit_for(estimates: Mapping[date, object], day: date) -> date:
    """The refit a forecast of `day` used: the latest one on or before it."""

    return max(r for r in estimates if r <= day)


def arm_forecasts(walk, panel, labels: Mapping[int, str], registry, decision_time, days: Sequence[date], mode: str) -> Tuple[Dict[date, dict], dict]:
    """The candidate's raw (uncapped) forecasts of `days` with the pool rescaled by the multipliers of `mode`, and the record of the multipliers.

    The multipliers of a refit and lead are computed once from that refit's estimate, the labels of its training targets and the anchor of the refit's
    decision (the last row public at it).

    Raises:
        LookAheadError: a training target of a refit is after the refit's anchor (`repo_model.day_type_scale.multipliers`).
    """

    position = {row.date: i for i, row in enumerate(panel)}
    estimates = {r: per_arm[ARM_NET] for r, per_arm in walk.estimates.items()}
    fitted: Dict[date, Dict[int, Dict[str, float]]] = {}
    rows: Dict[date, Dict[int, Dict[str, int]]] = {}
    for refit, per_lead in estimates.items():
        anchor = pb._anchor(panel, position[refit], registry, decision_time)
        fitted[refit], rows[refit] = {}, {}
        for h, est in per_lead.items():
            fitted[refit][h] = dts.multipliers(est, labels, anchor, mode=mode)
            counts = {t: 0 for t in dts.TYPES}
            for target in est.targets:
                counts[labels[target]] += 1
            rows[refit][h] = counts
    out: Dict[date, dict] = {}
    for d in days:
        refit = refit_for(estimates, d)
        index = position[d]
        types = {h: labels[index + h] for h in LEADS}
        out[d] = dts.rescale_day(walk.forecasts[ARM_NET][d], estimates[refit], fitted[refit], types, walk.detail[d]["scale"])
    return out, multiplier_record(fitted, rows, mode)


def multiplier_record(fitted, rows, mode: str) -> dict:
    """Per lead and type, over the refits: the mean, least and greatest multiplier, the share of refits at the fallback (too few rows) and at a bound,
    and the mean number of training pairs."""

    out: dict = {"refits": len(fitted), "minimum_rows": dts.MIN_ROWS, "bounds": list(dts.BOUNDS), "by_lead": {}}
    for h in LEADS:
        block = {}
        for t in dts.TYPES:
            values = [fitted[r][h][t] for r in fitted]
            counts = [rows[r][h][t] for r in rows]
            non = [sum(rows[r][h][x] for x in dts.NON_ORDINARY) for r in rows]
            seen = non if (mode == "pooled" and t != dts.ORDINARY) else counts
            fallback = 0 if (mode == "pooled" and t == dts.ORDINARY) else sum(1 for n in seen if n < dts.MIN_ROWS)
            block[t] = {
                "mean": sum(values) / len(values), "min": min(values), "max": max(values),
                "share_fallback": fallback / len(values),
                "share_at_bound": sum(1 for v in values if v in dts.BOUNDS) / len(values),
                "mean_rows": sum(counts) / len(counts),
            }
        out["by_lead"][str(h)] = block
    return out


def b1_prime_star(panel, frame, splits, registry) -> Dict[date, dict]:
    """B1'* on every scored decision day of `frame` (#1388): the calendar-aware persistence with the horizon counted from the last public anchor."""

    settings = dict(registry=registry, decision_time=k.DECISION_TIME)
    return {d: b1c.b1_calendar_anchor_forecast(panel, frame.position[d], splits=splits, **settings) for d in frame.days}


def walks_of(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """The walk of (s3c-ann-net) as #1363 walks it (arms ANN_ARM and ANN_NET_ARM), over #1255's decision days.

    Raises:
        ValueError: the walk is not at the declared 18:00 instant, or a scored decision day has no forecast.
    """

    if k.DECISION_TIME.isoformat(timespec="minutes") != "18:00":
        raise ValueError(f"the walks run at {k.DECISION_TIME}, not at the declared 18:00 decision instant")
    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    both = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    walk = m1288.sc.walk(panel, days, both, s3c_net.constant_states(panel), (s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM), sizes=net_table, **settings)
    for d in frame.days:
        if d not in walk.forecasts[ARM_NET]:
            raise ValueError(f"the walk has no forecast of the scored decision day {d}")
    return walk


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with the candidate, the two arms and B1'* added: `(frame, notes, walk, labels, record, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk = walks_of(window, frame, panel, splits, registry, results, auctions, first)
    labels = type_of_rows(panel, splits)
    raw = {ANNNET: {d: walk.forecasts[ARM_NET][d] for d in frame.days}}
    record: dict = {}
    for arm in ARMS:
        raw[arm], record[arm] = arm_forecasts(walk, panel, labels, registry, k.DECISION_TIME, frame.days, MODE_OF[arm])
    forecasts = {name: m1255.s3c_forecasts(frame, register, found) for name, found in raw.items()}
    forecasts[B1PS] = b1_prime_star(panel, frame, splits, registry)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    return frame, dict(notes, refits=len(walk.fits)), walk, labels, record, groups_fn


def differing_cells(frame, labels: Mapping[int, str]) -> dict:
    """Per arm and per pressure-day type of the target day: the cells on which the arm's quantiles differ from the candidate's, of all cells of the type.

    Raises:
        ValueError: the pooled arm differs from the candidate on a cell whose target is an ordinary day (it leaves them as they are).
    """

    out: dict = {}
    for arm in ARMS:
        counts = {t: [0, 0] for t in dts.TYPES}
        for d in frame.days:
            for h in LEADS:
                t = labels[frame.position[d] + h]
                counts[t][1] += 1
                counts[t][0] += 1 if frame.forecasts[arm][d][h] != frame.forecasts[ANNNET][d][h] else 0
        out[arm] = {t: {"differing": a, "cells": n} for t, (a, n) in counts.items()}
    if out[POOLED][dts.ORDINARY]["differing"]:
        raise ValueError("the pooled-scale arm differs from the candidate on an ordinary target day: it must leave them as they are")
    return out


# -- the paired tests ----------------------------------------------------------------------------------------------------

_STATE: Dict = {}


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in plan(candidate):
        days = list(members)
        if m1321._identical(series, candidate, name, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = m1321.unstudentized(series, candidate, name, days, _STATE["reps"])
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def non_ordinary_group(pressure: Mapping[date, str]) -> Tuple[str, str, str, List[date]]:
    """The union of the four non-ordinary pressure-day types of the target days, as a group of the `pressure_day_type` split."""

    return ("pressure_day_type", NON_ORDINARY, "target", sorted(t for t, kind in pressure.items() if kind != dts.ORDINARY))


# -- coverage and clustering ---------------------------------------------------------------------------------------------


def coverage_doc(window: str, frame, panel, table, sha: str) -> dict:
    """#1363's walk-file shape for the models of `COVERAGE_MODELS`, built in memory from the frame (so `m1363.Window` reads it)."""

    cells, outcome, targets, regime_of_day = [], {}, {}, {}
    for d in frame.days:
        regime_of_day[d.isoformat()] = frame.regime(d)
        for h in LEADS:
            t = frame.target(d, h)
            cells.append([d.isoformat(), h, t.isoformat()])
            outcome[t.isoformat()] = frame.outcome[t]
            if t.isoformat() not in targets:
                flags = table.day_types(frame.position[t])
                kinds = [x for x in m1363.DAY_TYPES[:-1]
                         if flags.get("settlement_coupon" if x == "coupon_settlement" else "settlement_bill" if x == "bill_settlement" else x)]
                targets[t.isoformat()] = {"regime": frame.regime(t), "types": kinds or ["ordinary"], "pressure": frame.day_type(t)}
    m1363.refuse_beyond([date.fromisoformat(x[2]) for x in cells] + list(frame.days), WINDOW_LAST[window], where="day_type_scale_1402")
    return {
        "window": window, "instant": "18:00", "panel_sha256": sha, "calendar": [row.date.isoformat() for row in panel], "cells": cells,
        "outcome": outcome, "targets": targets, "regime_of_day": regime_of_day,
        "models": {m: [list(frame.forecasts[m][date.fromisoformat(d)][h]) for d, h, _t in cells] for m in COVERAGE_MODELS},
    }


def coverage_report(doc: dict, workers: int, permutations: int = m1363.PERMUTATIONS) -> dict:
    """#1363's group reports, clustering and the protocol's thinned reading for the models of `COVERAGE_MODELS`."""

    window = m1363.Window(doc)
    groups = window.groups()
    out: dict = {"window": window.name, "decision_days": len(window.days), "cells": len(window.cells), "models": {}}
    for model in COVERAGE_MODELS:
        hits = m1363.cell_hits(window, model)
        brackets = m1363.brackets(list(zip(window.q[model], window.y)))
        out["models"][model] = {
            "groups": [m1363.group_report(window, model, s, lab, idx, hits, brackets, reps=REPS) for s, lab, idx in groups],
            "clustering": m1363.clustering(window, model, permutations=permutations, workers=workers, regimes=window.name == "development"),
            "protocol": m1363.protocol_reading(window, model),
        }
    return out


# -- the run -------------------------------------------------------------------------------------------------------------


def run_window(window: str, panel, splits, registry, table, register, results, auctions, sha, args) -> dict:
    frame, notes, _walk, labels_of, record, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    day_labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(day_labels))
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, day_labels, pressure) if g[0] in SPLITS]
    groups.append(non_ordinary_group(pressure))
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
        for metric in TESTED:
            for candidate in ARMS + (ANNNET,):
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped, "multipliers": record, "differing_cells": differing_cells(frame, labels_of),
        "pressure_day_type_counts": {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))},
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["coverage"] = coverage_report(coverage_doc(window, frame, panel, table, sha), args.workers, args.permutations)
    return result


def reproduction(results: Mapping[str, dict]) -> dict:
    """The candidate's pooled mean grid CRPS here against #1314's 18:00 record, to 1e-9.

    Raises:
        ValueError: they differ by more than 1e-9.
    """

    there = json.loads(RECORD_1314.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        mine = result["groups"]["pooled"]["all decision days"]["grid_crps"]["means"][ANNNET]
        theirs = there[window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]["sc_s3c_ann_net"]
        theirs = theirs["mean"] if isinstance(theirs, dict) else theirs
        if abs(mine - theirs) > 1e-9:
            raise ValueError(f"{window}: the candidate's mean grid CRPS is {mine!r} here and {theirs!r} in the 1314 record")
        out[window] = {"here": mine, "record": theirs}
    return out


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with m1321.decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/day_type_scale_1402")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1402, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": sha, "decision_time": c.DECISION_TIME.strftime("%H:%M"),
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict", "seed": SEED, "draws": args.draws,
        "reps": args.reps, "permutations": args.permutations, "models": list(MODELS), "arms": list(ARMS), "windows": {},
        "reading_rules": declaration["reading_rules"], "reading": declaration["reading"]["which_reading"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, sha, args)
    result["reproduction"] = reproduction(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


def _p(x: Optional[float], digits: int = 1) -> str:
    return m1363._p(x, digits)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for candidate in ARMS + (ANNNET,):
        for ref in plan(candidate):
            out.append(f"| {SHORT[candidate]} against {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, candidate: str, reference: str, order: Optional[Sequence[str]] = None) -> List[str]:
    return m1288.split_table(window, split, candidate, reference, order)


def coverage_by_type(window: Mapping[str, object], split: str, labels: Sequence[str], metric: str = "b90_closed") -> List[str]:
    groups = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(SHORT[m] for m in (ANNNET, TYPED, POOLED)) + " |", "|---|---|---|---|---|"]
    for label in labels:
        if label in groups:
            g = groups[label]
            out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.3f}" for m in (ANNNET, TYPED, POOLED)) + " |")
    return out if len(out) > 2 else []


def multiplier_table(record: Mapping[str, object], arm: str) -> List[str]:
    rec = record[arm]
    out = [f"| lead | type | mean multiplier | least | greatest | share of refits at the fallback | share at a bound | mean training pairs |", "|---|---|---|---|---|---|---|---|"]
    for lead in map(str, LEADS):
        for t in dts.TYPES:
            e = rec["by_lead"][lead][t]
            out.append(f"| h={lead} | {t} | {e['mean']:.3f} | {e['min']:.3f} | {e['max']:.3f} | {e['share_fallback']:.2f} | {e['share_at_bound']:.2f} | {e['mean_rows']:.1f} |")
    return out


def coverage_group_table(cov: Mapping[str, object], split: str, labels: Optional[Sequence[str]] = None) -> List[str]:
    m1363.LABELS.update(LABELS)
    return m1363.group_table(cov, COVERAGE_MODELS, split, labels)


def clustering_counts(cov: Mapping[str, object]) -> List[str]:
    out = ["| model | sequences (all days) | clustered by Holm | sequences inside regimes | clustered by Holm |", "|---|---|---|---|---|"]
    for model in COVERAGE_MODELS:
        c_ = cov["models"][model]["clustering"]
        a = [r for block in c_["all"].values() for r in block.values()]
        g = [r for by_lead in c_["regime"].values() for block in by_lead.values() for r in block.values()]
        out.append(f"| {LABELS[model]} | {len(a)} | {sum(r['holm_clusters'] for r in a)} | {len(g) or 'n/a'} | {sum(r['holm_clusters'] for r in g) if g else 'n/a'} |")
    return out


def lead_one_miss_table(cov: Mapping[str, object]) -> List[str]:
    out = ["| model | 90% band misses at lead 1 | P(miss after miss) | P(miss after hit) | longest run | p (permutation) | clusters (Holm) |", "|---|---|---|---|---|---|---|"]
    for model in COVERAGE_MODELS:
        r = cov["models"][model]["clustering"]["all"]["1"]["band90/strict"]
        out.append(f"| {LABELS[model]} | {r['misses']} ({_p(r['rate'])}) | {_p(r['p_miss_after_miss'])} | {_p(r['p_miss_after_hit'])} | {r['longest_run']} | "
                   f"{r['p_permutation']:.4f} | {'yes' if r['holm_clusters'] else 'no'} |")
    return out


def _skill_of(row: Optional[dict]) -> str:
    return cell(row)


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("development", "On the development window"), ("2026", "on the 2026 days")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        if entry is None:
            continue
        parts.append(f"{text}, pooled grid CRPS against (s3c-ann-net): typed {cell(_vs(entry, 'grid_crps', TYPED, ANNNET))}; "
                     f"pooled-scale {cell(_vs(entry, 'grid_crps', POOLED, ANNNET))}")
    return "; ".join(parts) + "."


def type_summary(r: Mapping[str, object]) -> List[str]:
    out = ["## Summary: by pressure-day type of the target day, grid CRPS and 90% band coverage", "",
           "The declared reading is by type (`reading.which_reading` of the declaration): a gain is read type by type on the mean-d bound, with the skill "
           "interval beside it; a pooled figure over all days is shown below and read only beside these rows.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        labels = list(dts.NON_ORDINARY) + [NON_ORDINARY, dts.ORDINARY]
        groups = w["groups"].get("pressure_day_type", {})
        out += [f"**{WINDOW_TITLES[window].split(' (')[0]}**", "",
                "| target-day type | days | typed against candidate | pooled-scale against candidate | 90% coverage: candidate / typed / pooled |", "|---|---|---|---|---|"]
        for label in labels:
            g = groups.get(label)
            if g is None:
                continue
            if f"pressure_day_type/{label}" in w["skipped_groups"]:
                out.append(f"| {label} | {g['days']} | not tested (fewer than 20 days) | not tested | "
                           + " / ".join(f"{g['b90_closed']['means'][m]:.3f}" for m in (ANNNET, TYPED, POOLED)) + " |")
                continue
            out.append(f"| {label} | {g['days']} | {cell(_vs(g, 'grid_crps', TYPED, ANNNET))} | {cell(_vs(g, 'grid_crps', POOLED, ANNNET))} | "
                       + " / ".join(f"{g['b90_closed']['means'][m]:.3f}" for m in (ANNNET, TYPED, POOLED)) + " |")
        pooled = w["groups"]["pooled"]["all decision days"]
        out.append(f"| all decision days (pooled, not read alone) | {pooled['days']} | {cell(_vs(pooled, 'grid_crps', TYPED, ANNNET))} | "
                   f"{cell(_vs(pooled, 'grid_crps', POOLED, ANNNET))} | "
                   + " / ".join(f"{pooled['b90_closed']['means'][m]:.3f}" for m in (ANNNET, TYPED, POOLED)) + " |")
        out.append("")
    return out


def render(r: dict) -> str:
    out = [
        "# Day-type residual scale beside the frozen candidate (s3c-ann-net), at the 18:00 decision (#1402)", "",
        "**Does a residual scale by type of target day fix the candidate's coverage on calendar days?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, two development arms on the candidate (s3c-ann-net) for the known-limits section of the "
        "registration; avenue #1387, her ruling of 2 November 2026 (option 1). **Development data, not a verdict** (scoring protocol v1, #640). "
        "**(s3c-ann-net) is frozen by the same ruling: this result goes to the known limits and does not reopen the candidate unless she says so.** "
        "Nothing is adopted, registered or published and no claim changes. Generated by `scripts/day_type_scale_1402.py page` from "
        f"`docs/research/day-type-scale-1402/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        "**What changed.** The candidate draws every day's spread from one pool of residuals. (s3c-ann-net-typed) multiplies the pool's spread about its "
        "median by one number per pressure-day type of the target day (turn, quarter_end_turn, tax_date, year_end, ordinary): the root-mean-square ratio "
        "of that type's training residuals to all of them, per refit and lead, 1 below 10 training pairs and clamped to [0.5, 4]. "
        "(s3c-ann-net-pooled) uses one number for all four non-ordinary types together and leaves ordinary days exactly as the candidate. The centre, the "
        "calendar and settlement terms, the scale and the fit are the candidate's, on direct pairs; the SRF cap is applied after the multiplier.", "",
        f"**Which reading, declared in advance.** {r['reading']}", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, "
        f"seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours the arm. **A reading (gain, loss, "
        "undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a Brier score the skill is the Brier "
        "skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x after 2020, so an "
        "interval that excludes zero is narrower than it should be. The intervals of a group of target days keep the **current method** (#1221 questions it "
        "and #1228 will decide); no reading of a group is a finding. Groups of fewer than 20 days are listed and not tested. The 2026 days were already "
        "seen by #845, the #151 final test and every study since #1229: they are shown apart and decide nothing.", ""]
    if r.get("reproduction"):
        out += ["**Reproduction.** The candidate's pooled mean grid CRPS equals #1314's 18:00 record to 1e-9 (development "
                f"{r['reproduction']['development']['here']:.6f}, 2026 {r['reproduction']['2026']['here']:.6f}), or the script refused to write this record. "
                "The pooled-scale arm equals the candidate on every cell whose target is an ordinary day, or the script refused too.", ""]
    out += type_summary(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits. Pressure-day types of the target days of "
                "the scored cells' decision days: " + ", ".join(f"{x} {v}" for x, v in w["pressure_day_type_counts"].items()) + ".", "",
                "### Cells the arms change", "", "| arm | " + " | ".join(dts.TYPES) + " |", "|---|" + "---|" * len(dts.TYPES)]
        for arm in ARMS:
            d = w["differing_cells"][arm]
            out.append(f"| {LABELS[arm]} | " + " | ".join(f"{d[t]['differing']:,} of {d[t]['cells']:,}" for t in dts.TYPES) + " |")
        out += ["", "### Mean scores (pooled)", ""] + mean_table(pooled) + ["", "### Each model against its references (pooled)", ""] + against_table(pooled) + [""]
        for arm in ARMS:
            for ref in plan(arm):
                for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
                    table = split_table(w, split, arm, ref)
                    if table:
                        out += [f"### {title}: {SHORT[arm]} against {SHORT[ref]}", ""] + table + [""]
        table = split_table(w, "pooled", ANNNET, B1PS)
        out += ["### The candidate against B1'* (the gap the arms start from)", ""]
        for split in ("lead", "regime", "pressure_day_type"):
            t = split_table(w, split, ANNNET, B1PS)
            if t:
                out += t + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            labels = sorted(w["groups"].get(split, {}))
            table = coverage_by_type(w, split, labels)
            if table:
                out += [f"### 90% band coverage by {title} (rates; the intervals are in the coverage section)", ""] + table + [""]
        out += ["### The multipliers", "", "(s3c-ann-net-typed), over the window's refits:", ""] + multiplier_table(w["multipliers"], TYPED) + [
            "", "(s3c-ann-net-pooled), over the window's refits (ordinary is 1 by construction and counts no fallback; the fallback share of a non-ordinary row is that of the four types together):", ""
        ] + multiplier_table(w["multipliers"], POOLED) + [""]
        cov = w["coverage"]
        out += ["### Band coverage by regime and pressure-day type, with intervals", "",
                "Rates with 90% stationary-bootstrap percentile intervals (mean block 10 target days, 2000 resamples), the current method which #1221 questions; "
                "a band is read 'under-covers' or 'over-covers' when its interval lies wholly below or above the nominal. Groups of fewer than 20 target days "
                "are not read.", ""]
        out += coverage_group_table(cov, "pooled") + [""] + coverage_group_table(cov, "regime") + [""] + coverage_group_table(cov, "pressure_day_type") + [""]
        out += ["### Band coverage by calendar target-day type (the types of #1363)", ""] + coverage_group_table(cov, "target_day_type") + [""]
        out += ["### Clustering of the band misses, on the reading in force at this pull request's base", "",
                "#1363's reading (an unthinned permutation test whose null keeps no h-1 overlap) and the protocol's thinned table (`scoring_protocol.coverage_cells`). "
                "#1400 declares a thinned reading for leads 2 to 5; it is not on main and is not used here, so a count below is on a reading that rejects a "
                "calibrated forecaster too often. Read it beside the candidate's, not alone.", ""]
        out += clustering_counts(cov) + [""] + lead_one_miss_table(cov) + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**Question 1. Does anything from this arm enter the registration's known-limits section, or the candidate?** (s3c-ann-net) is frozen by your ruling "
        "of 2 November 2026, and nothing here changes it. What the page shows is where a day-type scale would and would not repair the coverage table of "
        "#1378; whether it is written into the known limits as 'a day-type scale was tried, and gains / does not gain' is yours.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Write the result into the known limits and keep (s3c-ann-net) frozen** (default). No forecast, record or declaration changes.",
        "2. **Reopen the candidate** with the better arm, in a directive of its own, with a fresh declaration and its own prospective test.",
        "3. **Leave the result out** of the known limits and the registration text.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the candidate, make the two arms and B1'*, and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized intervals")
    s.add_argument("--permutations", type=int, default=m1363.PERMUTATIONS, help="permutations of the clustering test")
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
