"""H7f: the nested development test of the reserves ratio R and the scarcity state S on the H5 candidate (s3c-ann-net) (#1526; H7 step 2, milestone H7.M2;
her ruling of 28 October 2026, queued on her instruction of 8 November 2026).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/h7f_rs_1526.json`, which this script refuses to read unless it is committed and unchanged.

Question: does the scarcity reading, R+S, improve H5's primary score as an input, on development data? R is `scarcity.reserves_ratio`, S the own-leg
scarcity state (`scarcity.reserve_scarcity_state`, #586). No liquidity estimator is involved.

**Step 1 (what the candidate already reads)** is established from the code, not assumed: (s3c-ann-net) is the sized arm of #1172 with its scarcity state held at
its maximum (`s3c_net.constant_states`), and no term, scale or cap of it reads a reserves series. `candidate_reads` writes the evidence to `result.json`
and the page states it first. The arm adds what is missing, both: (s3c-ann-net-rs) is the candidate with R and S as two extra terms
(`spread_mr_state_calendar.RS_EXTRAS`, `repo_model.s3c_rs`), on direct pairs, at the 18:00 decision instant, everything else the candidate's.

It is scored on the two windows of #1255 (as #1483 and #1507) under scoring protocol v1, with #1483's machinery: grid CRPS averaged over h = 1..5 and
upper-tail twCRPS, against the candidate and against B1, B1' and B2 on the 23-level grid, and against B3 on its five levels (the published v1 record's
leads), on the studentized stationary bootstrap, split by lead, regime and pressure-day type of the target day. It also reports the miss-after-miss rate at
lead 1 of the arm beside the candidate's, in the form of #1363 (reported, not a gate). The 2026 days are a window of their own and decide nothing.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv --end 2026-09-03
    PYTHONPATH=src python3 scripts/h7f_rs_1526.py prechecks --panel PUB.csv --aug-panel AUG.csv --output docs/research/h7f-rs-1526/prechecks.json
    PYTHONPATH=src python3 scripts/h7f_rs_1526.py score --panel PUB.csv --aug-panel AUG.csv --window development \\
        --output docs/research/h7f-rs-1526/result-development.json
    PYTHONPATH=src python3 scripts/h7f_rs_1526.py score --panel PUB.csv --aug-panel AUG.csv --window 2026 \\
        --output docs/research/h7f-rs-1526/result-2026.json
    PYTHONPATH=src python3 scripts/h7f_rs_1526.py assemble --output docs/research/h7f-rs-1526/result.json
    PYTHONPATH=src python3 scripts/h7f_rs_1526.py page \\
        --score docs/research/h7f-rs-1526/result.json --output docs/research/h7f-rs-1526-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import multiprocessing
import os
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

os.environ["RMM_DECISION_TIME"] = "18:00"


def _load(name: str, alias: Optional[str] = None):
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


from repo_model import announced_iorb, h41_release, measurement_fields, policy_events, s3c_announced, s3c_net, s3c_rs  # noqa: E402
from repo_model import scarcity, scoring_protocol as sp, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.decision_instant import DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

fa = _load("family_ablation_1483", "family_ablation_1483_in_1526")
c1363 = _load("candidate_calibration_1363", "candidate_calibration_1363_in_1526")
m1321, m1288, m1273, m1255, k, c, s686, s761 = fa.m1321, fa.m1288, fa.m1273, fa.m1255, fa.k, fa.c, fa.s686, fa.s761

DECLARATION = REPO / "metadata" / "h7f_rs_1526.json"
RECORD_1483 = REPO / "docs" / "research" / "family-ablation-1483" / "result.json"
H41 = REPO / "metadata" / "h41_release_dating.json"
B3_DAILY = REPO / "docs" / "runs" / "published_distribution_daily_h{h}.json"
OUT_DIR = REPO / "docs" / "research" / "h7f-rs-1526"
SEED = 1526
LAST_DAY = EXPLORATORY_END
WINDOW_LAST, WINDOWS, WINDOW_TITLES = fa.WINDOW_LAST, fa.WINDOWS, fa.WINDOW_TITLES
ANNNET = fa.ANNNET
B1, B1P, B2 = "B1", c.B1P, "B2"
BENCHMARKS = (B1, B1P, B2)
TESTED, METRIC_NAMES, METRIC_TITLES, MIN_GROUP_DAYS = fa.TESTED, fa.METRIC_NAMES, fa.METRIC_TITLES, fa.MIN_GROUP_DAYS
REPS = fa.REPS
SPLITS = fa.SPLITS
#: Rows of the built columns between two no-look-ahead rebuilds (`s3c_rs.check_rs_no_future`); 1 is every row.
CHECK_EVERY = 1
B3_LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
B3 = "B3"
#: The permutation count and seed of #1363's independence test.
PERMUTATIONS = c1363.PERMUTATIONS
DEPENDENCE_SEED = c1363.SEED
DEPENDENCE_SEQUENCES = ("band90/strict", "upper/strict")

# -- the arm -------------------------------------------------------------------------------------------------------------

_BASE = s3c_announced.ANN_NET_ARM
RS_ARM = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_rs", extra=sc.RS_EXTRAS,
    role="(s3-ann-net-rs) (s3-ann-net) with the reserves ratio R (percentage points) and the scarcity state S (over 3) as two extra terms",
)
WALK_ARMS = (_BASE, RS_ARM)


def model_of(arm: sc.StateArm) -> str:
    return fa.model_of(arm)


RS = model_of(RS_ARM)
MODELS = BENCHMARKS + (ANNNET, RS)
LABELS = {B1: "B1", B1P: "B1' (#960)", B2: "B2", B3: "B3 (five levels)", ANNNET: "(s3c-ann-net), the candidate", RS: "(s3c-ann-net) with R+S"}
SHORT = {B1: "B1", B1P: "B1'", B2: "B2", B3: "B3", ANNNET: "(s3c-ann-net)", RS: "(ann-net) + R+S"}
#: The models that are tested and the references each is tested against; the arm's first reference is the candidate.
CANDIDATES = (RS, ANNNET)


def plan(candidate: str) -> List[str]:
    if candidate == RS:
        return [ANNNET] + list(BENCHMARKS)
    if candidate == ANNNET:
        return list(BENCHMARKS)
    return []


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- step 1: what the candidate reads --------------------------------------------------------------------------------------


def candidate_reads(panel: Sequence) -> dict:
    """What (s3c-ann-net) reads of R and S, established from its arm and its state series, not assumed.

    Raises:
        ValueError: the candidate already reads R or S as a term (the step would then report that as the result), or its state is not held constant.
    """

    arm = _BASE
    terms = tuple(arm.location) + tuple(arm.extra)
    reads_reserves_term = [t for t in terms if t in sc.RS_EXTRAS or t in sc.SATIATION_EXTRAS or "reserve" in t or "scarcity" in t]
    states = s3c_net.constant_states(panel)
    levels = sorted({sc.level(v) for v in states.values()})
    held = levels == [1.0]
    if reads_reserves_term:
        raise ValueError(f"the candidate already reads {reads_reserves_term}: H7f is answered by construction and the step reports that")
    if not held:
        raise ValueError(f"the candidate's scarcity state is not held at its maximum: levels {levels}")
    return {
        "arm": arm.name, "location_terms": list(arm.location), "extra_terms": list(arm.extra), "sized": arm.sized, "interact": arm.interact,
        "state_levels_read": levels, "state_held_at_maximum": held, "days": len(states),
        "reads_R": False, "reads_S": False,
        "scale": "the median absolute daily change of the spread (spread_mr_fhs, #941): no reserves series",
        "cap": "the SRF line from the policy register (s3c_candidate): no reserves series",
        "the_arm_adds": list(sc.RS_EXTRAS),
        "answered_by_construction": False,
    }


# -- the columns -----------------------------------------------------------------------------------------------------------


def rs_rule() -> InformationRule:
    """The rule R and S read their three legs through at the declared instant: the H.4.1 legs per release (#541, #622), the ON RRP at its own row."""

    registry = h41_release.release_dated_registry(measurement_fields.load_registry(), h41_release.load_release_dating(H41))
    return InformationRule(registry, s3c_rs.LEGS, decision_time=DECISION_TIME, horizon=1)


def build_columns(rows, *, check_every: int = CHECK_EVERY):
    """`rows` with R and S at the declared instant, checked for look-ahead (`s3c_rs.check_rs_no_future`)."""

    with scarcity.measurement_declaration(), h41_release.release_dating():
        rule = rs_rule()
        built = s3c_rs.build_rs_columns(rows, rule, last_day=LAST_DAY)
        s3c_rs.check_rs_no_future(rows, built, rule, last_day=LAST_DAY, indices=range(0, len(built), check_every))
    return built


def aug_rows(aug_path: Path, panel) -> list:
    """The scratch panel's rows (to the last exploratory day), refused unless its dates and every published column are the published panel's.

    Raises:
        ValueError: the dates differ, or a published column's value differs on a row.
    """

    rows = [row for row in load_daily_panel(Path(aug_path)) if row.date <= LAST_DAY]
    if [r.date for r in rows] != [r.date for r in panel]:
        raise ValueError("the scratch panel's dates are not the published panel's")
    for a, b in zip(rows, panel):
        for name, value in b.values.items():
            if name in a.values and a.values[name] != value:
                raise ValueError(f"the scratch panel differs from the published panel on {a.date} in {name}")
    return rows


def prechecks_of(rows, panel, check_every: int = CHECK_EVERY) -> dict:
    """The columns' own checks, at 18:00: no look-ahead on every row, what S and R look like by year, and what the candidate reads."""

    built = build_columns(rows, check_every=check_every)
    years: Dict[str, dict] = {}
    for row in built:
        r, s = row.values.get(s3c_rs.RATIO_COLUMN), row.values.get(s3c_rs.STATE_COLUMN)
        if r is None or s is None:
            continue
        y = years.setdefault(str(row.date.year), {"days": 0, "ratios": [], "state_days": {"0": 0, "1": 0, "2": 0, "3": 0}})
        y["days"] += 1
        y["ratios"].append(r)
        y["state_days"][str(int(s))] += 1
    by_year = {y: {"days": v["days"], "ratio_median_pct": 100.0 * statistics.median(v["ratios"]), "ratio_min_pct": 100.0 * min(v["ratios"]),
                   "ratio_max_pct": 100.0 * max(v["ratios"]), "state_days": v["state_days"]} for y, v in sorted(years.items())}
    values = [(r.values.get(s3c_rs.RATIO_COLUMN), r.values.get(s3c_rs.STATE_COLUMN)) for r in built]
    both = [(a, b) for a, b in values if a is not None and b is not None]
    return {
        "decision_time": DECISION_TIME.strftime("%H:%M"), "rows": len(rows), "check_every": check_every,
        "rows_with_a_value": len(both), "first_row_with_a_value": next(i for i, (a, b) in enumerate(values) if a is not None and b is not None),
        "rows_with_ratio_only": sum(1 for a, b in values if a is not None and b is None),
        "no_future_check": "passed (s3c_rs.check_rs_no_future, LookAheadError on a value that depends on a later row)",
        "by_year": by_year, "candidate_reads": candidate_reads(panel),
    }


def prechecks(args) -> int:
    committed_declaration()
    published = Path(args.panel)
    panel = [row for row in load_daily_panel(published) if row.date <= LAST_DAY]
    require_exploratory_window([r.date for r in panel], where="scripts/h7f_rs_1526")
    rows = aug_rows(Path(args.aug_panel), panel)
    out = prechecks_of(rows, panel, args.check_every)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the walk ------------------------------------------------------------------------------------------------------------


def walks_of(window: str, frame, panel, built, splits, registry, results, auctions, first: Optional[date]):
    """One walk of the candidate and the R+S arm, over #1255's decision days.

    Raises:
        ValueError: the walk is not at the declared decision instant, the built rows are not the panel's days, or a scored decision day has no
            forecast of an arm.
    """

    if k.DECISION_TIME != DECISION_TIME:
        raise ValueError(f"the walks run at {k.DECISION_TIME}, not at the declared decision instant {DECISION_TIME}")
    if [r.date for r in built] != [r.date for r in panel]:
        raise ValueError("the rows carrying R and S are not the panel's days")
    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, announcements, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    walk = sc.walk(panel, days, term_table, states, WALK_ARMS, sizes=net_table, iorb=s3c_rs.merged(built), **settings)
    for arm in WALK_ARMS:
        for d in frame.days:
            if d not in walk.forecasts[arm.name]:
                raise ValueError(f"the walk has no forecast of {arm.name} on the scored decision day {d}")
    return walk


def build(window: str, panel, built, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with the candidate and the arm added: `(frame, notes, walk, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk = walks_of(window, frame, panel, built, splits, registry, results, auctions, first)
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS}
    for arm in WALK_ARMS:
        found = {d: walk.forecasts[arm.name][d] for d in frame.days}
        forecasts[model_of(arm)] = m1255.s3c_forecasts(frame, register, found)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    return frame, dict(notes, refits=len(walk.fits)), walk, groups_fn


# -- the five-level comparison with B3 -----------------------------------------------------------------------------------------


def b3_record() -> Dict[int, Dict[str, dict]]:
    """The published v1 record's daily quantiles by lead and target day (read, never edited)."""

    out: Dict[int, Dict[str, dict]] = {}
    for h in sp.HORIZONS:
        record = json.loads(Path(str(B3_DAILY).format(h=h)).read_text(encoding="utf-8"))
        out[h] = {x["date"]: x for x in record["days"]}
    return out


def b3_scores(frame, models: Sequence[str], daily: Mapping[int, Mapping[str, dict]]) -> Tuple[List[date], Dict[str, Dict[date, float]]]:
    """B3's five-level CRPS and each model's, read at the same five levels, averaged over h = 1..5, on the decision days with all five leads in the record.

    Raises:
        ValueError: the record's outcome for a target day is not the panel's.
    """

    position = {d: i for i, d in enumerate(frame.dates)}
    five = sp.level_crps(B3_LEVELS)
    kept = [d for d in frame.days if all(position[d] + h < len(frame.dates) and frame.dates[position[d] + h].isoformat() in daily[h] for h in sp.HORIZONS)]
    series: Dict[str, Dict[date, float]] = {B3: {}, **{m: {} for m in models}}
    for d in kept:
        totals = {name: 0.0 for name in series}
        for h in sp.HORIZONS:
            target = frame.dates[position[d] + h]
            entry = daily[h][target.isoformat()]
            observed = frame.outcome[target]
            if abs(float(entry["actual_bps"]) - float(observed)) > 1e-9:
                raise ValueError(f"the published record's outcome for {target} is {entry['actual_bps']}, the panel's is {observed}")
            totals[B3] += five([float(x) for x in entry["quantiles_bps"]], observed)
            for m in models:
                totals[m] += five(sp.on_levels(frame.forecasts[m][d][h], B3_LEVELS), observed)
        for name, total in totals.items():
            series[name][d] = total / len(sp.HORIZONS)
    return kept, series


def b3_leg(frame, args) -> dict:
    """The arm and the candidate against B3 on the five levels: the means and the paired tests on the days the record covers."""

    kept, series = b3_scores(frame, (ANNNET, RS), b3_record())
    out: dict = {"levels": list(B3_LEVELS), "days": len(kept), "first": kept[0].isoformat() if kept else None, "last": kept[-1].isoformat() if kept else None,
                 "means": {name: sum(s[d] for d in kept) / len(kept) for name, s in series.items()} if kept else {}, "vs": {}}
    for candidate in (RS, ANNNET):
        if not kept:
            continue
        payload = s761.run_pairs({B3: series[B3]}, series[candidate], kept, seed=SEED, draws=args.draws, mean_d_fallback=True)[B3]
        if "undefined" in payload:
            payload["unstudentized"] = m1321.unstudentized(series, candidate, B3, kept, args.reps)
        out["vs"][candidate] = payload
    return out


# -- the dependence at lead 1 -------------------------------------------------------------------------------------------------


def lead_1_dependence(frame, permutations: int = PERMUTATIONS) -> dict:
    """The miss sequences at lead 1 in the form of #1363, for the candidate and the arm: P(miss after miss) beside P(miss after hit).

    The decision days are taken in order; a transition is counted only between consecutive panel days. Reported, not a gate.
    """

    days = sorted(frame.days)
    position = {d: i for i, d in enumerate(frame.dates)}
    positions = [position[d] for d in days]
    runs = c1363.runs_of(positions)
    out: dict = {}
    for model in (ANNNET, RS):
        events = [c1363.event_hits(frame.forecasts[model][d][1], frame.outcome[frame.target(d, 1)]) for d in days]
        out[model] = {name: c1363.sequence_report([e[name] for e in events], runs, permutations=permutations, seed=DEPENDENCE_SEED)
                      for name in DEPENDENCE_SEQUENCES}
    return out


# -- the tests -----------------------------------------------------------------------------------------------------------

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


def effects_of(walk) -> dict:
    """The fitted coefficient of each term (standardised units) over the refits of the walk, per lead: mean, min, max, and the refits it entered."""

    out: Dict[str, Dict[str, dict]] = {}
    for term in sc.RS_EXTRAS:
        per_lead: Dict[str, dict] = {}
        for h in sp.HORIZONS:
            found = [e[RS_ARM.name][h].effect[term] for e in walk.estimates.values() if term in e[RS_ARM.name][h].effect]
            per_lead[str(h)] = {"refits": len(walk.estimates), "entered": len(found),
                                "mean": statistics.fmean(found) if found else None, "min": min(found) if found else None, "max": max(found) if found else None}
        out[term] = per_lead
    return out


def run_window(window: str, panel, built, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, walk, groups_fn = build(window, panel, built, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in SPLITS]
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
            for candidate in CANDIDATES:
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {"notes": notes, "groups": {}, "skipped_groups": skipped,
                    "differing_cells": m1273.lead_difference(frame, ANNNET, RS), "fits": effects_of(walk)}
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    result["b3"] = b3_leg(frame, args)
    result["lead_1_dependence"] = lead_1_dependence(frame, args.permutations)
    return result


def against_1483(result: Mapping[str, dict], window: str) -> dict:
    """The candidate's pooled means here beside #1483's record: the control is #1483's, so they agree to rounding."""

    if not RECORD_1483.exists():
        return {}
    there = json.loads(RECORD_1483.read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all decision days"]
    here = result["groups"]["pooled"]["all decision days"]
    return {m: {x: {"now": here[m]["means"][x], "then": there[m]["means"][x], "difference": here[m]["means"][x] - there[m]["means"][x]}
                for x in (B1, B1P, B2, ANNNET)} for m in ("grid_crps", "upper_tail_twcrps", "brier_gt5")}


def score(args) -> int:
    with m1321.decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    if args.window not in WINDOWS:
        raise SystemExit(f"--window must be one of {WINDOWS}")
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/h7f_rs_1526")
    scratch = aug_rows(Path(args.aug_panel), panel)
    built = build_columns(scratch, check_every=args.check_every)
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    out = run_window(args.window, panel, built, splits, registry, table, register, results, auctions, args)
    result: dict = {
        "issue": 1526, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha, "window": args.window,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arm": RS, "candidates": list(CANDIDATES), "reading_rules": declaration["reading_rules"], "data": out,
        "against_1483": against_1483(out, args.window) if args.first is None else {},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def assemble(args) -> int:
    """Join the per-window scores and the pre-checks into `result.json`."""

    declaration = committed_declaration()
    input_dir = Path(args.input_dir)
    parts = {w: json.loads((input_dir / f"result-{w}.json").read_text(encoding="utf-8")) for w in WINDOWS if (input_dir / f"result-{w}.json").exists()}
    if not parts:
        raise SystemExit("no per-window score found: run `score` first")
    if len({p["panel_sha256"] for p in parts.values()}) != 1:
        raise SystemExit("the windows were scored on different panels")
    checks = json.loads((input_dir / "prechecks.json").read_text(encoding="utf-8"))
    first = next(iter(parts.values()))
    result = {
        "issue": 1526, "declaration": first["declaration"], "panel_sha256": first["panel_sha256"], "decision_time": first["decision_time"],
        "label": first["label"], "seed": first["seed"], "draws": first["draws"], "reps": first["reps"], "models": first["models"], "arm": first["arm"],
        "candidates": first["candidates"], "reading_rules": declaration["reading_rules"],
        "candidate_reads": checks["candidate_reads"],
        "windows": {w: p["data"] for w, p in parts.items()}, "against_1483": {w: p["against_1483"] for w, p in parts.items()}, "prechecks": checks,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def _pct(x: float) -> str:
    return f"{100.0 * x:.0f}%"


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return fa._vs(group, metric, candidate, reference)


def pooled(r: Mapping[str, object], window: str) -> Optional[dict]:
    return fa.pooled(r, window)


def reading_word(row: Optional[Mapping[str, object]]) -> str:
    """The reading the pooled mean-d bound gives (her ruling on #1009), in the words of the other pages; `n/a` where there is no row."""

    if row is None:
        return "n/a"
    return "identical" if row.get("identical") else k.reading_words(row).strip("*")


def candidate_reads_section(r: Mapping[str, object]) -> List[str]:
    reads = r["candidate_reads"]
    return [
        "## What the candidate already reads (step 1)", "",
        "The step asks first whether (s3c-ann-net) already reads R or S, because if it read both, H7f would be answered by construction. It reads neither, "
        "established from the arm and its state series, not assumed:", "",
        f"- **S: no.** The candidate is the sized arm of #1172 with its scarcity state held at its maximum (`s3c_net.constant_states`): on all {reads['days']:,} panel days "
        f"the level it reads is {', '.join(f'{x:g}' for x in reads['state_levels_read'])}, so its sized settlement terms are the plain signed net over USD 100 bn. "
        "The 'scarcity state read per leg' row of #1483 was a different contrast (every term times the state, an interaction); S as an additive input has not been measured on it.",
        f"- **R: no.** Its terms are the calendar and settlement terms ({', '.join(f'`{t}`' for t in reads['location_terms'])}), its scale is {reads['scale'].split(': ')[0]}, "
        f"and its cap reads {reads['cap'].split(': ')[0]}; no reserves series enters.", "",
        "**The arm adds what is missing, both:** `rs_ratio` (R in percentage points of reserves over the H.8 total assets of all commercial banks) and `rs_state` (S over 3), "
        "as two extra terms of the Huber fit after the candidate's terms. Everything else is the candidate's. The contrast therefore cannot separate R from S: "
        "a gain is R+S together, and a loss or an undecided reading says R+S as read here adds nothing to the candidate.", ""]


def columns_section(r: Mapping[str, object]) -> List[str]:
    p = r["prechecks"]
    out = [
        "## The columns at 18:00", "",
        f"R and S are built at the {p['decision_time']} decision instant on {p['rows']:,} panel rows; {p['rows_with_a_value']:,} have both (the first at row "
        f"{p['first_row_with_a_value']}). Look-ahead: {p['no_future_check']}, rebuilt every {p['check_every']} row(s). The share of days at each state, and R, by year:", "",
        "| year | days | S=0 | S=1 | S=2 | S=3 | R median (%) | R min | R max |", "|---|---|---|---|---|---|---|---|---|"]
    for y, v in p["by_year"].items():
        s = v["state_days"]
        out.append(f"| {y} | {v['days']} | " + " | ".join(_pct(s[x] / v["days"]) for x in "0123") + f" | {v['ratio_median_pct']:.2f} | {v['ratio_min_pct']:.2f} | {v['ratio_max_pct']:.2f} |")
    return out + ["", "A measurement of the columns, not a result of the walk.", ""]


def answer_table(r: Mapping[str, object]) -> List[str]:
    out = ["| arm against the candidate | " + " | ".join(f"{WINDOW_TITLES[w].split(' (')[0]}: {METRIC_TITLES[m]}" for w in ("development", "2026") for m in TESTED[:2]) + " |",
           "|---|" + "---|" * 4,
           f"| {SHORT[RS]} against {SHORT[ANNNET]} | " + " | ".join(
               "not run" if pooled(r, w) is None else fa.cell(_vs(pooled(r, w), m, RS, ANNNET)) for w in ("development", "2026") for m in TESTED[:2]) + " |"]
    return out


def benchmark_table(w: Mapping[str, object]) -> List[str]:
    """Pooled: each of the arm and the candidate against B1, B1' and B2 on the grid, and B3 on its five levels."""

    group = w["groups"]["pooled"]["all decision days"]
    out = ["| model against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for candidate in CANDIDATES:
        for ref in BENCHMARKS:
            out.append(f"| {SHORT[candidate]} against {SHORT[ref]} | " + " | ".join(fa.cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def b3_lines(w: Mapping[str, object]) -> List[str]:
    b3 = w["b3"]
    if not b3["days"]:
        return ["No decision day of this window has all five leads in the published record."]
    out = [f"B3 is the published v1 declaration's five levels {', '.join(str(x) for x in b3['levels'])}, scored on those five against each model read at the same five "
           f"(a secondary comparison, protocol section 4). The record covers {b3['days']:,} of the window's decision days ({b3['first']} to {b3['last']}). "
           "Mean five-level CRPS: " + ", ".join(f"{SHORT[m] if m in SHORT else m} {v:.3f}" for m, v in b3["means"].items()) + ".", "",
           "| model against B3 | five-level CRPS |", "|---|---|"]
    for candidate in CANDIDATES:
        out.append(f"| {SHORT[candidate]} against B3 | {fa.cell(b3['vs'].get(candidate))} |")
    return out


def dependence_table(w: Mapping[str, object]) -> List[str]:
    dep = w["lead_1_dependence"]
    out = ["| model | sequence | n | misses (rate) | P(miss after miss) | P(miss after hit) | longest run | LR p (asymptotic) | p (permutation) |",
           "|---|---|---|---|---|---|---|---|---|"]

    def p(x):
        return "n/a" if x is None else f"{100.0 * x:.1f}%"

    for model in (ANNNET, RS):
        for name in DEPENDENCE_SEQUENCES:
            e = dep[model][name]
            out.append(f"| {SHORT[model]} | {name} | {e['n']} | {e['misses']} ({p(e['rate'])}) | {p(e['p_miss_after_miss'])} | {p(e['p_miss_after_hit'])} | "
                       f"{e['longest_run']} | {e['p_asymptotic']:.3f} | {e['p_permutation']:.3f} |")
    return out


def fit_lines(w: Mapping[str, object]) -> List[str]:
    fits = w.get("fits")
    if not fits:
        return []
    out = ["### The fitted coefficients of R and S", "",
           "Coefficient of the term in the Huber fit over the refits of the walk, in scale units per percentage point of R, and per unit of S over 3 (the effect in bp is the "
           "coefficient times the anchor's scale). `entered` counts the refits in which the term had enough non-zero pairs.", "",
           "| term | lead | refits | entered | mean | min | max |", "|---|---|---|---|---|---|---|"]
    for term in sc.RS_EXTRAS:
        for h, e in fits[term].items():
            out.append(f"| {term} | h={h} | {e['refits']} | {e['entered']} | " + " | ".join("n/a" if e[x] is None else f"{e[x]:+.4f}" for x in ("mean", "min", "max")) + " |")
    return out + [""]


def control_section(r: Mapping[str, object]) -> List[str]:
    diffs = [abs(v["difference"]) for a in r.get("against_1483", {}).values() for ms in a.values() for v in ms.values()]
    if not diffs:
        return []
    return ["## The control against #1483's record", "",
            "B1, B1', B2 and (s3c-ann-net) are re-run in this walk; their pooled means of all three metrics, in both windows, are compared with "
            f"`docs/research/family-ablation-1483/result.json`. Largest absolute difference of a pooled mean: {max(diffs):.1e}. Shown, not required to agree; no record is edited.", ""]


def question_section(r: Mapping[str, object]) -> List[str]:
    return [
        "## Question for Eleonora: what does this reading do to H7?", "",
        "The page is a development reading on days already seen; it decides nothing, and H7.M2 is not marked done by this change "
        "(`docs/research/milestones.json` is untouched). The H7 kill, as #46 states it, is that the scarcity reading does not predict later spread behaviour beyond "
        "the current scarcity state. The candidate reads neither R nor S, so this contrast tests R+S together and cannot say whether R or S carries a gain.", "",
        "1. **Leave H7 as it stands and mark nothing** (default). The reading goes into the H7 manual's markers; the milestone is marked, and H7 closed or registered, "
        "only by your ruling.",
        "2. **Mark H7.M2 done** on this page's evidence (the nested development test with R+S alone has been run), without closing H7.",
        "3. **Queue the separating arms**: R alone and S alone on the candidate, so a gain (or a loss) can be put on one of them. This adds two arms and decides nothing.", ""]


def render(r: dict) -> str:
    reading = {w: reading_word(_vs(pooled(r, w), TESTED[0], RS, ANNNET)) for w in ("development", "2026") if pooled(r, w) is not None}
    out = [
        "# H7f: the nested development test of R+S on the H5 candidate (#1526)", "",
        "**Does the scarcity reading, R+S, improve H5's primary score as an input, on development data?** The first table is the answer: the candidate with R and S "
        "added against the candidate, on grid CRPS (primary) and upper-tail twCRPS, in both windows. A positive skill and a positive mean d say R+S helps; the reading "
        "is taken from the studentized bound on mean d (her ruling on #1009). Pooled grid CRPS reads: "
        + ", ".join(f"{WINDOW_TITLES[w].split(' (')[0]} **{word}**" for w, word in reading.items()) + ".", ""]
    out += answer_table(r) + [""]
    out += [
        "**Hypothesis and step:** H7, step 2 (milestone H7.M2): the development nested forecast test, H7f, with R+S alone. **Development data, not a verdict** (scoring protocol v1, "
        "#640); the 2026 days are shown separately and decide nothing. Her ruling of 28 October 2026 (\"H7f goes on with R+S in the model repo\"), queued on her instruction of "
        "8 November 2026. **(s3c-ann-net) stays the candidate; nothing here changes it.** Nothing is registered or published and no claim changes; whether the arm is adopted, "
        "and whether H7 is closed or registered, are hers. Generated by `scripts/h7f_rs_1526.py page` from `docs/research/h7f-rs-1526/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        f"Panel digest `{r['panel_sha256']}`, built at the 18:00 decision instant. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days keep the "
        "**current method** (#1221 questions it and #1228 will decide); no reading of a group is a finding. Groups of fewer than 20 days are listed and not tested.", ""]
    out += candidate_reads_section(r)
    out += columns_section(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n = w["notes"]
        out += [f"## {WINDOW_TITLES[window]}", "", f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits.", ""]
        out += [f"### R+S against the candidate", ""]
        for split, title in (("pooled", "Pooled"), ("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
            table = m1288.split_table(w, split, RS, ANNNET)
            if table:
                out += [f"#### {title}: {SHORT[RS]} against {SHORT[ANNNET]}", ""] + table + [""]
        out += ["### Against the benchmarks B1, B1' and B2 (23-level grid), pooled", "", "Orientation d = S(benchmark) - S(model): a positive skill favours the model.", ""]
        out += benchmark_table(w) + [""]
        for ref in BENCHMARKS:
            for split, title in (("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
                table = m1288.split_table(w, split, RS, ref)
                if table:
                    out += [f"#### {title}: {SHORT[RS]} against {SHORT[ref]}", ""] + table + [""]
        out += ["### Against B3 (five levels)", ""] + b3_lines(w) + [""]
        out += ["### Dependence at lead 1 (the form of #1363)", "",
                "The 0/1 sequences of a miss of the central 90% band and of a miss above q95 (strict), over the scored decision days of lead 1 in order, no transition across a "
                "gap. P(miss after miss) beside P(miss after hit) is the clustering the H5 candidate shows at lead 1; Christoffersen's statistic and its permutation p "
                f"({PERMUTATIONS:,} permutations, seed {DEPENDENCE_SEED}) as #1363. **Reported, not a gate.**", ""]
        out += dependence_table(w) + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
        out += fit_lines(w)
    out += control_section(r)
    out += question_section(r)
    return "\n".join(out).rstrip() + "\n"


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prechecks", help="what the candidate reads, and the checks of the columns R and S at 18:00")
    p.add_argument("--panel", required=True)
    p.add_argument("--aug-panel", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--check-every", type=int, default=CHECK_EVERY)
    p.set_defaults(func=prechecks)
    s = sub.add_parser("score", help="walk the candidate and the R+S arm on one window, cap them as (s3c) is capped, and score")
    s.add_argument("--panel", required=True)
    s.add_argument("--aug-panel", required=True)
    s.add_argument("--window", required=True, choices=list(WINDOWS))
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized intervals")
    s.add_argument("--permutations", type=int, default=PERMUTATIONS, help="permutations of the lead-1 independence test")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--check-every", type=int, default=CHECK_EVERY)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    a = sub.add_parser("assemble", help="join the per-window scores and the pre-checks into result.json")
    a.add_argument("--input-dir", default=str(OUT_DIR))
    a.add_argument("--output", required=True)
    a.set_defaults(func=assemble)
    g = sub.add_parser("page", help="write the result page from the assembled record")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
