"""The H.4.1 weeklies read per release at the 18:00 decision, against the carried-forward weekly reading in force (#1350; H5 step 3; avenue #1338; her ruling of
1 November 2026).

A development comparison, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/h41_per_release_1350.json`, which this script refuses to read unless it is committed and unchanged. The registry's reading is not changed: the
per-release reading is `repo_model.h41_release` (`metadata/h41_release_dating.json`, #541), switched on for the length of a walk only
(`release_dating()` over `release_dated_registry`), and every scarcity-state read of the per-release run passes `h41_release.require_release_read`, which
re-derives the Thursday 16:30 print from the declaration and raises `LookAheadError` or `StaleReadError`.

Two readings are compared at the declared 18:00 instant (`repo_model.decision_instant`, pinned): *carried* (the registry in force: a Wednesday level is public
five calendar days later, so from the Monday) and *per release* (public from its Thursday 16:30 print, so from the Thursday 18:00 decision). The arms:
(s3c-ann-net), which holds the scarcity state constant and so reads no H.4.1 series; (s3c+state), the scarcity-state arm of #1196 with (s3c)'s SRF cap; and
(s3c-ann-net x state), the candidate's net settlement terms each times the as-of scarcity state (the sized arm of #1172 on the announced net). The only H.4.1
leg of the state is `reserve_balances` (WRESBAL); the H.8 and ON RRP legs are read as before. Each arm is walked on both readings over #1255's decision days
and scored with (s3c-ann-net) and (s3c) beside it, at the 18:00 instant, on the development window of #1145 and #1241 and on the 2026 development days of #1229
(targets to 2026-09-03). The blind tier and every lockbox day are refused by the frames' own guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp), on scoring protocol v1's
studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill interval beside, on all decision days and on the Thursday,
Friday and Monday-to-Wednesday decisions separately, by lead, regime and pressure-day type.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/h41_per_release_1350.py score --panel PUB.csv --output docs/research/h41-per-release-1350/result.json
    PYTHONPATH=src python3 scripts/h41_per_release_1350.py page \\
        --score docs/research/h41-per-release-1350/result.json --output docs/research/h41-per-release-1350-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import importlib.util
import json
import multiprocessing
import sys
import tempfile
from datetime import date, timedelta
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


from repo_model import announced_iorb, data as data_module, h41_release, metrics, policy_events, s3c_announced, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.decision_instant import DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model.scarcity import measurement_declaration, own_leg_states  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1356's script (and through it #1321's, #1288's, #1273's and #1255's), loaded under an alias of its own so that the pickling of the worker pool's tasks does
#: not meet another test module's copy. Its `decision_instant_pinned` runs the chain at the declared 18:00 instant.
m1356 = _load("s3c_ann_net_cmb_1356", "s3c_ann_net_cmb_1356_in_1350")
m1321, m1288, m1273, m1255 = m1356.m1321, m1356.m1288, m1356.m1273, m1356.m1255
k, c, s686, s761 = m1356.k, m1356.c, m1356.s686, m1356.s761
d1145 = m1255.d1145
load_daily_panel = m1288.load_daily_panel
decision_instant_pinned = m1321.decision_instant_pinned

DECLARATION = REPO / "metadata" / "h41_per_release_1350.json"
H41 = REPO / "metadata" / "h41_release_dating.json"
RECORD_1321 = REPO / "docs" / "research" / "s3c-flagnet-gross-1321" / "result.json"
SEED = 1350
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3C, ANNNET, B1P = m1288.S3C, m1288.ANNNET, m1288.B1P
BENCHMARKS = m1288.BENCHMARKS
PRN = "sc_s3c_ann_net_perrel"
S3SC, S3SP = "sc_s3c_state_carried", "sc_s3c_state_perrel"
ANSC, ANSP = "sc_s3c_ann_net_state_carried", "sc_s3c_ann_net_state_perrel"
ARMS = (PRN, S3SC, S3SP, ANSC, ANSP)
MODELS = BENCHMARKS + (S3C, ANNNET) + ARMS
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3C: "(s3c), the H5 candidate", ANNNET: "(s3c-ann-net), carried", PRN: "(s3c-ann-net), per release",
          S3SC: "(s3c+state), carried", S3SP: "(s3c+state), per release", ANSC: "(s3c-ann-net x state), carried",
          ANSP: "(s3c-ann-net x state), per release"}
SHORT = {"B1": "B1", B1P: "B1'", "B2": "B2", S3C: "(s3c)", ANNNET: "(s3c-ann-net)", PRN: "(ann-net) per release", S3SC: "(s3c+state) carried",
         S3SP: "(s3c+state) per release", ANSC: "(ann-net x state) carried", ANSP: "(ann-net x state) per release"}
#: The carried counterpart of each per-release arm: the comparison the ruling asks for.
COUNTERPART = {PRN: ANNNET, S3SP: S3SC, ANSP: ANSC}
#: What each arm is tested against (paired); the benchmarks are scored beside them and compared on their means.
PLAN: Mapping[str, Tuple[str, ...]] = {
    PRN: (ANNNET, S3C),
    S3SC: (ANNNET, S3C),
    S3SP: (S3SC, ANNNET, S3C),
    ANSC: (ANNNET, S3C),
    ANSP: (ANSC, ANNNET, S3C),
}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
LEADS = tuple(sp.HORIZONS)
#: The splits of #1356, kept: pooled, by lead, by regime and by pressure-day type of the target day.
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
#: Scope name, its title, and the weekdays of the decisions it holds (Monday is 0). Thursday and Friday are the only days on which the readings differ.
SCOPES: Tuple[Tuple[str, str, Tuple[int, ...]], ...] = (
    ("all", "all decision days", (0, 1, 2, 3, 4)),
    ("thursday", "Thursday decisions", (3,)),
    ("friday", "Friday decisions", (4,)),
    ("mon_wed", "Monday to Wednesday decisions", (0, 1, 2)),
)
SCOPE_TITLES = {name: title for name, title, _days in SCOPES}
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
REPS = 2000
EPSILON = 1e-9
_STATE: Dict = {}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the state, on each reading ------------------------------------------------------------------------------------------


def wednesday_of(day: date) -> date:
    """The Wednesday whose level the panel row of `day` carries (the latest Wednesday on or before it)."""

    return day - timedelta(days=(day.weekday() - 2) % 7)


def read_states(per_release: bool, end: date = LAST_DAY, registry_path: Path = c.SOURCES) -> Tuple[Dict[date, Optional[float]], List[dict], List[date]]:
    """The scarcity state a decision on each panel day could read, keyed by the decision day, on the carried or the per-release reading.

    The same arithmetic as `state_calendar_1145.decision_states` (the own-leg grid at horizon 1, each leg at its own latest public row), with the H.4.1 dated
    per release inside `h41_release.release_dating()` over the release-dated registry when `per_release`. Every read of the per-release run is passed through
    `h41_release.require_release_read`, which re-derives the print from `metadata/h41_release_dating.json`.

    Returns `(states, reads, dates)`: `reads` has one row per scored day with the decision day, the state, the panel row the reserve leg was read at and the
    age in calendar days of the level read at the decision day.

    Raises:
        LookAheadError, StaleReadError: a per-release read that is not the latest level printed by the decision instant.
        ValueError: the measurement panel is not built at the declared decision instant, or a level read is older than the weekly-carry bound.
    """

    declaration = h41_release.load_release_dating(H41)
    with measurement_declaration(), tempfile.TemporaryDirectory() as tmp:
        build, _digest, registry, decision = d1145.sv.build_measurement_panel(registry_path, Path(tmp))
        if decision != DECISION_TIME:
            raise ValueError(f"the measurement panel is built at {decision}, not at the declared decision instant {DECISION_TIME}")
        dates = [row.date for row in build.observations]
        scope = contextlib.nullcontext()
        if per_release:
            registry = h41_release.release_dated_registry(registry, declaration)
            scope = h41_release.release_dating()
        with scope:
            scored = own_leg_states(
                build.observations, registry=registry, decision_time=decision, minimum_history=d1145.STATE_MINIMUM_HISTORY, horizon=1, end=end)
    position = {day: i for i, day in enumerate(dates)}
    reads: List[dict] = []
    for entry in scored:
        decision_day = dates[position[entry.day] - 1]
        read = entry.read_dates.get("reserve_balances")
        if read is None:
            raise ValueError(f"the reserve leg of the state for {entry.day} has no read row")
        if per_release:
            h41_release.require_release_read(declaration, dates, decision_day, read, decision)
        age = (decision_day - wednesday_of(read)).days
        if age > data_module.WEEKLY_CARRY_MAX_STALENESS_DAYS:
            raise ValueError(f"the level read by the decision of {decision_day} is {age} days old, past the weekly-carry bound "
                             f"{data_module.WEEKLY_CARRY_MAX_STALENESS_DAYS}")
        reads.append({"decision_day": decision_day, "scored_day": entry.day, "state": entry.state, "read": read, "age_days": age})
    grid = {entry.day: entry.state for entry in scored}
    states = {dates[i]: grid.get(dates[i + 1]) for i in range(len(dates) - 1)}
    return states, reads, dates


def state_check(carried: Sequence[dict], per_release: Sequence[dict], first: Optional[date] = None) -> dict:
    """What the per-release reading moves in the state, by weekday of the decision.

    * `level_differs`: the decisions at which the two readings read the reserve level of different weeks;
    * `state_differs`: the decisions at which the scarcity state is different (with both values listed);
    * the largest age of the level read, in calendar days, under each reading, against the weekly-carry bound.
    """

    by_day = {r["decision_day"]: r for r in per_release}
    out: Dict[str, dict] = {w: {"decisions": 0, "level_differs": 0, "state_differs": 0} for w in WEEKDAYS}
    changed: List[dict] = []
    for r in carried:
        p = by_day.get(r["decision_day"])
        if p is None or (first is not None and r["decision_day"] < first):
            continue
        day = WEEKDAYS[r["decision_day"].weekday()]
        out[day]["decisions"] += 1
        out[day]["level_differs"] += 1 if wednesday_of(r["read"]) != wednesday_of(p["read"]) else 0
        if r["state"] != p["state"]:
            out[day]["state_differs"] += 1
            changed.append({"decision_day": r["decision_day"].isoformat(), "weekday": day, "carried": r["state"], "per_release": p["state"]})
    return {
        "by_weekday": out, "state_changes": changed,
        "max_age_days": {"carried": max(r["age_days"] for r in carried), "per_release": max(r["age_days"] for r in per_release)},
        "weekly_carry_bound_days": data_module.WEEKLY_CARRY_MAX_STALENESS_DAYS,
        "reads_checked_by_guard": len(per_release),
    }


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def walks_of(window: str, frame, panel, splits, registry, release_registry, table, results, auctions, first: Optional[date], states: Mapping[str, Mapping]):
    """The six walks over #1255's decision days: (s3c-ann-net) on each reading, (s3c+state) on each, (s3c-ann-net x state) on each.

    A per-release walk runs inside `h41_release.release_dating()` over the release-dated registry. `states` has the keys `constant`, `carried` and
    `per_release`.

    Raises:
        ValueError: a scored decision day has no forecast of a walk.
    """

    days = m1288.candidate_days(frame, window, first)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    specs = {
        "ref": (s3c_announced.ANN_NET_ARM, term_table, net_table, "constant", False),
        "ref_p": (s3c_announced.ANN_NET_ARM, term_table, net_table, "constant", True),
        "s3s": (sc.S3_STATE, table, None, "carried", False),
        "s3s_p": (sc.S3_STATE, table, None, "per_release", True),
        "ans": (s3c_announced.ANN_NET_ARM, term_table, net_table, "carried", False),
        "ans_p": (s3c_announced.ANN_NET_ARM, term_table, net_table, "per_release", True),
    }
    walks: Dict[str, sc.Walk] = {}
    for key, (arm, tbl, sizes, which, per_release) in specs.items():
        settings = dict(registry=release_registry if per_release else registry, decision_time=k.DECISION_TIME, splits=splits)
        scope = h41_release.release_dating() if per_release else contextlib.nullcontext()
        with scope:
            walks[key] = sc.walk(panel, days, tbl, states[which], (arm,), sizes=sizes, **settings)
        for d in frame.days:
            if d not in walks[key].forecasts[arm.name]:
                raise ValueError(f"the {key} walk has no forecast of {arm.name} on the scored decision day {d}")
    names = {key: spec[0].name for key, spec in specs.items()}
    return walks, names


def build(window: str, panel, splits, registry, release_registry, table, register, results, auctions, first: Optional[date], states):
    """#1255's frame of `window` with the six walks added: `(frame, notes, walks, names, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walks, names = walks_of(window, frame, panel, splits, registry, release_registry, table, results, auctions, first, states)
    raw = {ANNNET: "ref", PRN: "ref_p", S3SC: "s3s", S3SP: "s3s_p", ANSC: "ans", ANSP: "ans_p"}
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS + (S3C,)}
    for model, key in raw.items():
        forecasts[model] = m1255.s3c_forecasts(frame, register, {d: walks[key].forecasts[names[key]][d] for d in frame.days})
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    notes = dict(notes, **{f"refits_{key}": len(walk.fits) for key, walk in walks.items()})
    return frame, notes, groups_fn


# -- the checks ----------------------------------------------------------------------------------------------------------


def cells_differ(frame, base: str, other: str) -> dict:
    """The (decision day, lead) cells on which `other` is not `base` element for element, by weekday of the decision and by lead."""

    out = {w: {str(h): 0 for h in LEADS} for w in WEEKDAYS}
    totals = {w: 0 for w in WEEKDAYS}
    for d in frame.days:
        w = WEEKDAYS[d.weekday()]
        totals[w] += 1
        for h in LEADS:
            if list(frame.forecasts[other][d][h]) != list(frame.forecasts[base][d][h]):
                out[w][str(h)] += 1
    return {"decision_days": totals, "differing_cells": out}


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def _pairs_task(job):
    scope, split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(scope, grain, metric)]
    out: Dict[str, dict] = {}
    for name in PLAN[candidate]:
        days = list(members)
        if _identical(series, candidate, name, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = m1356.unstudentized(series, candidate, name, days, _STATE["reps"])
    return (scope, split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def scoped_frame(frame, weekdays: Sequence[int]):
    """A copy of the frame whose decision days are those on the given weekdays (the groups and series of a scope are built from it)."""

    scoped = copy.copy(frame)
    scoped.days = [d for d in frame.days if d.weekday() in weekdays]
    return scoped


def scoped_cells(cells: Mapping[str, Mapping[Tuple[date, int], float]], weekdays: Sequence[int]):
    return {metric: {key: v for key, v in table.items() if key[0].weekday() in weekdays} for metric, table in cells.items()}


def run_window(window: str, panel, splits, registry, release_registry, table, register, results, auctions, states, args) -> dict:
    frame, notes, groups_fn = build(window, panel, splits, registry, release_registry, table, register, results, auctions, args.first, states)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    series: Dict[Tuple[str, str, str], Dict[str, Dict[date, float]]] = {}
    groups: List[tuple] = []
    for scope, _title, weekdays in SCOPES:
        fr = scoped_frame(frame, weekdays)
        part = {m: scoped_cells(cells[m], weekdays) for m in MODELS}
        seen: set = set()
        for split, label, grain, members in groups_fn(fr, labels, pressure):
            if split not in SPLITS:
                continue
            for metric in METRIC_NAMES:
                if (scope, grain, metric) not in series:
                    series[(scope, grain, metric)] = {m: c.series_of(fr, part[m][metric], grain) for m in MODELS}
            present = series[(scope, grain, METRIC_NAMES[0])][S3C]
            kept = [d for d in members if d in present]
            if kept and (scope, split, label) not in seen:
                seen.add((scope, split, label))
                groups.append((scope, split, label, grain, kept))
    _STATE.update(series=series, draws=args.draws, reps=args.reps)

    jobs, skipped = [], {}
    for scope, split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{scope}/{split}/{label}"] = len(members)
            continue
        for metric in TESTED:
            for candidate in ARMS:
                jobs.append((scope, split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped,
        "cells_differ": {f"{model}|{COUNTERPART[model]}": cells_differ(frame, COUNTERPART[model], model) for model in COUNTERPART},
        "pressure_day_type_counts": {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))},
    }
    for scope, split, label, grain, members in groups:
        entry = result["groups"].setdefault(scope, {}).setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(scope, grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (scope, split, label, metric, candidate), payload in done:
        result["groups"][scope][split][label][metric]["vs"][candidate] = payload
    return result


def against_1321(results: Mapping[str, dict]) -> dict:
    """The pooled means of (s3c) and (s3c-ann-net) here beside #1321's record, made at 18:00 with the same walks: they must agree to 1e-9.

    Raises:
        ValueError: they do not.
    """

    if not RECORD_1321.exists():
        return {}
    there = json.loads(RECORD_1321.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        a, b = there[window]["groups"]["pooled"]["all decision days"], result["groups"]["all"]["pooled"]["all decision days"]
        out[window] = {m: {x: {"now": b[m]["means"][x], "then": a[m]["means"][x], "difference": b[m]["means"][x] - a[m]["means"][x]}
                           for x in (S3C, ANNNET)} for m in ("grid_crps", "upper_tail_twcrps", "brier_gt5")}
        worst = max(abs(v["difference"]) for rows in out[window].values() for v in rows.values())
        if worst > 1e-9:
            raise ValueError(f"the references of the {window} window differ from #1321's record by {worst:.2e}: the walks are not the same")
    return out


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/h41_per_release_1350")
    if c.DECISION_TIME != DECISION_TIME:
        raise ValueError(f"the chain runs at {c.DECISION_TIME}, not the declared {DECISION_TIME}")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    release_registry = h41_release.release_dated_registry(registry, h41_release.load_release_dating(H41))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    carried, carried_reads, _dates = read_states(False)
    per_release, per_release_reads, _ = read_states(True)
    # #1145's states end at its own last day (2025-12-31); the 2026 days need the same arithmetic to 2026-09-03.
    theirs = d1145.decision_states(c.SOURCES)
    if any(carried.get(d) != v for d, v in theirs.items() if d < d1145.LAST_DAY):
        raise ValueError("the carried state of this run is not #1145's decision_states")
    states = {"constant": s3c_net.constant_states(panel), "carried": carried, "per_release": per_release}
    result: dict = {
        "issue": 1350, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arms": list(ARMS), "references": [ANNNET, S3C] + list(BENCHMARKS), "reading_rules": declaration["reading_rules"],
        "state_check": state_check(carried_reads, per_release_reads, args.first),
        "release_dating": json.loads(H41.read_text(encoding="utf-8"))["available_time"], "windows": {},
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, release_registry, table, register, results, auctions, states, args)
    result["against_1321"] = against_1321(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    if row is not None and row.get("identical"):
        return f"identical on all {row['days']} days"
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


def reading(row: Optional[dict]) -> str:
    """`gain`, `loss`, `undecided`, `identical` or `n/a` on the mean-d bound, for a candidate against a reference."""

    if row is None:
        return "n/a"
    return "identical" if row.get("identical") else k.reading_words(row).split(" ")[0].strip("*")


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str) -> List[str]:
    out = [f"| {SHORT[candidate]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in PLAN[candidate]:
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def scope_window(window: Mapping[str, object], scope: str) -> dict:
    """The window as `m1288.split_table` reads it, restricted to one scope of decision days."""

    return {"groups": window["groups"].get(scope, {}),
            "skipped_groups": {key.split("/", 1)[1]: v for key, v in window["skipped_groups"].items() if key.startswith(scope + "/")}}


def split_table(window: Mapping[str, object], scope: str, split: str, candidate: str, reference: str) -> List[str]:
    labels = window["groups"].get(scope, {}).get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|---|" + "---|" * len(TESTED)]
    for label in sorted(labels):
        g = labels[label]
        skipped = f"{scope}/{split}/{label}" in window["skipped_groups"]
        out.append(f"| {label} | {g['days']} | " + " | ".join(
            "not tested (fewer than 20 days)" if skipped else cell(_vs(g, m, candidate, reference)) for m in TESTED) + " |")
    return out if len(out) > 2 else []


def state_table(check: Mapping[str, object]) -> List[str]:
    out = ["| decision weekday | decisions | read a different week's reserve level | scarcity state different |", "|---|---|---|---|"]
    for day in WEEKDAYS:
        n = check["by_weekday"][day]
        out.append(f"| {day} | {n['decisions']} | {n['level_differs']} | {n['state_differs']} |")
    return out


def differ_table(differ: Mapping[str, dict], model: str) -> List[str]:
    entry = differ[f"{model}|{COUNTERPART[model]}"]
    out = ["| decision weekday | decisions | " + " | ".join(f"h={h}" for h in LEADS) + " |", "|---|---|" + "---|" * len(LEADS)]
    for day in WEEKDAYS:
        out.append(f"| {day} | {entry['decision_days'][day]} | " + " | ".join(str(entry["differing_cells"][day][str(h)]) for h in LEADS) + " |")
    return out


def largest_change(r: Mapping[str, object]) -> Dict[str, dict]:
    """For each window, the per-release arm and group with the largest absolute relative change in grid CRPS against its carried counterpart, among the
    tested groups (an identical group has none)."""

    out: Dict[str, dict] = {}
    for window, w in r["windows"].items():
        best = {"skill": 0.0}
        for scope, splits in w["groups"].items():
            for split, labels in splits.items():
                for label, g in labels.items():
                    for arm, ref in COUNTERPART.items():
                        row = g.get("grid_crps", {}).get("vs", {}).get(arm, {}).get(ref)
                        if row is None or row.get("identical") or row.get("skill") is None:
                            continue
                        if abs(row["skill"]) > abs(best["skill"]):
                            best = {"skill": row["skill"], "arm": arm, "scope": scope, "split": split, "label": label, "days": g["days"]}
        out[window] = best
    return out


def answer(r: Mapping[str, object]) -> List[str]:
    """The plain answer, built from the intervals: does reading the weeklies per release move the forecasts or their grid CRPS, on Thursdays and Fridays."""

    out = ["## Does the per-release reading change anything?", "",
           "Grid CRPS (primary), a per-release arm against its carried counterpart, on the mean-d bound; the other scores and the full tables follow. "
           "Positive d favours the per-release arm.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        out.append(f"**{WINDOW_TITLES[window].split(' (')[0]}.**")
        for arm in COUNTERPART:
            ref = COUNTERPART[arm]
            parts = []
            for scope, title, _d in SCOPES:
                g = w["groups"].get(scope, {}).get("pooled", {}).get("all decision days")
                if g is not None:
                    parts.append(f"{title.replace(' decisions', '')}: {cell(_vs(g, 'grid_crps', arm, ref))}")
            n_cells = sum(sum(v.values()) for v in w["cells_differ"][f"{arm}|{ref}"]["differing_cells"].values())
            out.append(f"- {SHORT[arm]} against {SHORT[ref]} ({n_cells} forecast cells differ): " + "; ".join(parts) + ".")
        big = largest_change(r)[window]
        if "arm" in big:
            out.append(f"- Size: the largest relative change in grid CRPS from the per-release reading, over every tested group of this window, is "
                       f"{big['skill']:+.2%} ({SHORT[big['arm']]}, {SCOPE_TITLES[big['scope']].lower()}, {big['split'].replace('_', ' ')}: {big['label']}, "
                       f"{big['days']} days). A reading of 'gain' or 'loss' says that the interval of mean d excludes zero; it is not a size.")
        out.append("")
    return out


def render(r: dict) -> str:
    check = r["state_check"]
    out = [
        "# The H.4.1 weeklies read per release at the 18:00 decision (#1350)", "",
        "**Does reading the H.4.1 weeklies that feed the scarcity state per release (from the Thursday 16:30 print) instead of five calendar days after the "
        "Wednesday change the forecasts or their scores, at the 18:00 decision?** The answer is under the first heading below, from the intervals.", "",
        "**Hypothesis and step:** H5 (primary goal), step 3; avenue #1338; her ruling of 1 November 2026 (chat, relayed; ledger item 99) on her open question 2 "
        "on PR #1315. **Development data, not a verdict** (scoring protocol v1, #640). **The registry's reading is not changed here** (`metadata/sources.json`, "
        "`docs/decisions/information-set.md`, every record and declaration are as they were), nothing is registered or published and no claim changes. Generated "
        "by `scripts/h41_per_release_1350.py page` from `docs/research/h41-per-release-1350/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        "**The two readings.** *Carried* (the registry in force): a Wednesday level is public five calendar days later at 16:30, so a decision reads it from "
        "the Monday. *Per release* (`metadata/h41_release_dating.json`, #541, through `repo_model.h41_release`, switched on for the length of a walk only): the "
        f"level is public at its release's print, the Thursday after at {r['release_dating']} (the Board's moved date in a holiday week), so the 18:00 "
        "decision on that Thursday reads it. The two readings serve the same level from the Monday on, so they can differ only on Thursday and Friday decisions "
        "(and on the day a release was moved to, and on the Monday after a Wednesday that is a holiday with no panel row). Thursdays and Fridays are shown separately, with the Monday-to-Wednesday decisions beside them: on those both readings serve the same state, so their forecasts can differ there only through the refits, whose training pairs include earlier Thursday and Friday states.", "",
        "**What reads the H.4.1.** The scarcity state has three legs, each read at its own latest public row: the reserve balances (the H.4.1's WRESBAL), the "
        "H.8 bank assets and ON RRP. Only the first is an H.4.1 weekly, so the per-release reading moves one leg of the state. The TGA is dated per release too "
        "in the variant registry, but no arm here reads it, so it is not tested. (s3c-ann-net) holds the state constant (`s3c_net.constant_states`) and reads no "
        "H.4.1 series: run as the ruling names it, it is expected to be unmoved, and the page says what it measured. The two arms that do read the state are "
        "(s3c+state), the scarcity-state arm of #1196 with (s3c)'s SRF cap, and (s3c-ann-net x state), built for this comparison: (s3c-ann-net)'s announced net "
        "settlement terms each times the as-of scarcity state (the sized arm of #1172 on the announced net). It is a measuring arm, not a proposal.", "",
        f"Panel digest `{r['panel_sha256']}`. Decision instant {r['decision_time']} New York, pinned. Studentized stationary bootstrap (ruling 1), mean block "
        f"{sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d "
        "favours the model named first. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval "
        "beside it; for a Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is "
        "understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The groups of target days keep the current method, "
        "which #1221 questions and #1228 will decide. A group in which two models score alike on every day is listed as identical and not tested; groups of "
        "fewer than 20 days are listed with their means and not tested.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, and by #1229 and the studies after it. They are shown "
        "separately and decide nothing.", ""]
    out += answer(r)
    out += ["## What the per-release reading moves in the state", "",
            "The decisions at which the two readings read the reserve level of a different week, and at which the scarcity state differs, by weekday of the "
            "decision (both windows, every scored decision day).", ""] + state_table(check) + [
            "", "On a Monday where the readings differ, the Wednesday five days before is not a panel day (a holiday, for example 4 July 2018): the carried "
            "reading counts its five days from a row date and so reads the row before the holiday, while the per-release reading reads the print of the week. "
            "`test_h41_per_release_read_1350` pins this for the 2018 start of the range; for the whole range it was checked with the same function when this "
            "page was written, and the record does not list those Mondays.", ""]
    if check["state_changes"]:
        out += ["The decisions at which the state differs:", "", "| decision day | weekday | carried | per release |", "|---|---|---|---|"]
        out += [f"| {x['decision_day']} | {x['weekday']} | {x['carried']} | {x['per_release']} |" for x in check["state_changes"]] + [""]
    out += [f"Weekly-carry rules: the 13-day bound is the panel's (`data.WEEKLY_CARRY_MAX_STALENESS_DAYS` = {check['weekly_carry_bound_days']}). The age of the "
            f"level read at the decision day, in calendar days, is at most {check['max_age_days']['carried']} on the carried reading and "
            f"{check['max_age_days']['per_release']} per release, both inside the bound (the run refuses a read past it; the decision-day check of #1341 is "
            f"not merged, so it is reported here and binds nothing). Every one of the {check['reads_checked_by_guard']:,} per-release reads passed "
            "`h41_release.require_release_read`, which re-derives the print from the declaration.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n = w["notes"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}).", "", "### Mean scores (all decision days)", ""]
        out += mean_table(w["groups"]["all"]["pooled"]["all decision days"])
        for arm in ARMS:
            out += ["", f"### {LABELS[arm]}: forecast cells that differ from {SHORT[COUNTERPART[arm]]}" if arm in COUNTERPART else f"### {LABELS[arm]}", ""]
            if arm in COUNTERPART:
                out += differ_table(w["cells_differ"], arm) + [""]
            for scope, title, _d in SCOPES:
                g = w["groups"].get(scope, {}).get("pooled", {}).get("all decision days")
                if g is not None:
                    out += [f"{title}, {g['days']} decision days:", ""] + against_table(g, arm) + [""]
        for arm in COUNTERPART:
            for scope, title, _d in SCOPES:
                for split, heading in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
                    table = split_table(w, scope, split, arm, COUNTERPART[arm])
                    if table:
                        out += [f"### {heading}, {title}: {SHORT[arm]} against {SHORT[COUNTERPART[arm]]}", ""] + table + [""]
        for scope, title, _d in SCOPES[:3]:
            table = split_table(w, scope, "regime", ANSP, ANNNET)
            if table:
                out += [f"### By regime, {title}: {SHORT[ANSP]} against {SHORT[ANNNET]}", ""] + table + [""]
        skipped = {x: v for x, v in w["skipped_groups"].items()}
        if skipped:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({v})" for x, v in sorted(skipped.items())) + ".", ""]
    if r.get("against_1321"):
        out += ["## The references against #1321's record (made at 18:00)", "",
                "(s3c) and (s3c-ann-net) are re-run here with the same walks; the pooled means equal #1321's to 1e-9 (the run refuses to write otherwise). "
                "Largest absolute difference: "
                f"{max(abs(v['difference']) for ms in r['against_1321'].values() for rows in ms.values() for v in rows.values()):.1e}.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**Should the registry read the H.4.1 weeklies per release?** This study changes no reading. Whether to turn the per-release reading on in "
        "`metadata/sources.json` is a decision about the final-test freeze (that file is pinned by bytes) and about the information set, and rests on "
        "development days already seen, split as above.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Keep the declared lags; nothing changes** (default).",
        "2. **Draft the amendment to `docs/decisions/information-set.md` and the registry change** for your review, to be made on the prospective "
        "confirmation days only.",
        "3. **Ask for a study of the other H.4.1 lines** (the TGA and the related lines no arm here reads), in a directive of its own.",
        "4. **Ask whether (s3c-ann-net x state) should become a candidate arm**, in a directive of its own: here it is only the arm on which the candidate reads the state.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the arms on both readings of the H.4.1 and score them on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized intervals")
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
