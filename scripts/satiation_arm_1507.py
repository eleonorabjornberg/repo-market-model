"""The satiation-distance arm of the family ablation on the candidate (s3c-ann-net) (#1507; H5 step 2 follow-up, milestone H5.M3; her ruling of 7 November 2026,
decision docket, card f1505-satiation-row, option run-arm; finding #1505).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/satiation_arm_1507.json`, a dated amendment of `metadata/family_ablation_1483.json` (which is not edited), and this script refuses to read it
unless it is committed and unchanged.

#1483 gave the satiation-distance family no row on the premise that no daily as-of series exists on main. `satiation_dist_roll` and `satiation_hinge_roll`
(`repo_model.satiation`, #598) are exactly that. This study adds each, as one term, to (s3c-ann-net) on direct pairs, and scores the candidate with the
term against the candidate, on both windows of #1483, with #1483's machinery and settings:

* (s3c-ann-net-satdist): (s3c-ann-net) with `satiation_dist_roll`, in percentage points, as one extra term (`repo_model.s3c_satiation`);
* (s3c-ann-net-sathinge): the same with `satiation_hinge_roll`.

The two columns are built at the 18:00 instant, per H.4.1 release (#622), from the scratch panel of `scripts/pressure_v1_1.py` (which carries
`bank_total_assets`), after two checks reported on the page: the share of days the hinge is on, by year (#621), and the columns on the weekly lag against
the per-release read (#622).

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv --end 2026-09-03
    PYTHONPATH=src python3 scripts/satiation_arm_1507.py prechecks --aug-panel AUG.csv \\
        --output docs/research/satiation-arm-1507/prechecks.json
    PYTHONPATH=src python3 scripts/satiation_arm_1507.py score --panel PUB.csv --aug-panel AUG.csv --window development \\
        --output docs/research/satiation-arm-1507/result-development.json
    PYTHONPATH=src python3 scripts/satiation_arm_1507.py score --panel PUB.csv --aug-panel AUG.csv --window 2026 \\
        --output docs/research/satiation-arm-1507/result-2026.json
    PYTHONPATH=src python3 scripts/satiation_arm_1507.py assemble --output docs/research/satiation-arm-1507/result.json
    PYTHONPATH=src python3 scripts/satiation_arm_1507.py page \\
        --score docs/research/satiation-arm-1507/result.json --output docs/research/satiation-arm-1507-result.md
    PYTHONPATH=src python3 scripts/family_ablation_1483.py page \\
        --score docs/research/family-ablation-1483/result.json --satiation docs/research/satiation-arm-1507/result.json \\
        --output docs/research/family-ablation-1483-result.md

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

#: The columns are built at the declared decision instant; `scripts/satiation_distance_598.py` reads it from the environment when it is loaded.
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


from repo_model import announced_iorb, policy_events, s3c_announced, s3c_net, s3c_satiation  # noqa: E402
from repo_model import satiation as sat, scoring_protocol as sp, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.decision_instant import DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

fa = _load("family_ablation_1483", "family_ablation_1483_in_1507")
s598 = _load("satiation_distance_598", "satiation_distance_598_in_1507")
m1321, m1288, m1273, m1255, k, c, s686, s761 = fa.m1321, fa.m1288, fa.m1273, fa.m1255, fa.k, fa.c, fa.s686, fa.s761

DECLARATION = REPO / "metadata" / "satiation_arm_1507.json"
RECORD_1483 = REPO / "docs" / "research" / "family-ablation-1483" / "result.json"
OUT_DIR = REPO / "docs" / "research" / "satiation-arm-1507"
SEED = fa.SEED
LAST_DAY = EXPLORATORY_END
WINDOW_LAST, WINDOWS, WINDOW_TITLES = fa.WINDOW_LAST, fa.WINDOWS, fa.WINDOW_TITLES
S3, S3C, ANNNET = fa.S3, fa.S3C, fa.ANNNET
TESTED, METRIC_NAMES, METRIC_TITLES, MIN_GROUP_DAYS = fa.TESTED, fa.METRIC_NAMES, fa.METRIC_TITLES, fa.MIN_GROUP_DAYS
REPS = fa.REPS
SPLITS = fa.SPLITS
#: Rows of the built columns between two no-look-ahead rebuilds (`satiation.check_distance_no_future`); 1 is every row.
CHECK_EVERY = 1

# -- the arms ------------------------------------------------------------------------------------------------------------

_BASE = s3c_announced.ANN_NET_ARM
DIST_ARM = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_satdist", extra=(sc.SATIATION_DIST,),
    role="(s3-ann-net-satdist) (s3-ann-net) with the satiation distance (satiation_dist_roll, percentage points) as one term",
)
HINGE_ARM = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_sathinge", extra=(sc.SATIATION_HINGE,),
    role="(s3-ann-net-sathinge) (s3-ann-net) with the satiation hinge (satiation_hinge_roll, percentage points) as one term",
)
WALK_ARMS = (_BASE, DIST_ARM, HINGE_ARM)


def model_of(arm: sc.StateArm) -> str:
    return fa.model_of(arm)


DIST, HINGE = model_of(DIST_ARM), model_of(HINGE_ARM)
ARMS = (DIST, HINGE)
MODELS = (S3, S3C, ANNNET) + ARMS
LABELS = {S3: "(s3)", S3C: "(s3c)", ANNNET: "(s3c-ann-net), the candidate", DIST: "(s3c-ann-net) with the satiation distance",
          HINGE: "(s3c-ann-net) with the satiation hinge"}
SHORT = {S3: "(s3)", S3C: "(s3c)", ANNNET: "(s3c-ann-net)", DIST: "(ann-net) + distance", HINGE: "(ann-net) + hinge"}
#: `(key, family, with the family, without it)`: the model that reads the family against the one that does not.
ROWS: Tuple[Tuple[str, str, str, str], ...] = (
    ("satiation_dist", "satiation distance", DIST, ANNNET),
    ("satiation_hinge", "satiation distance", HINGE, ANNNET),
)
ROW_TITLES = {"satiation_dist": "the satiation distance (satiation_dist_roll) as one term", "satiation_hinge": "the satiation hinge (satiation_hinge_roll) as one term"}
CANDIDATES = tuple(dict.fromkeys(r[2] for r in ROWS))


def plan(candidate: str) -> List[str]:
    return [without for _k, _f, with_, without in ROWS if with_ == candidate]


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the columns -----------------------------------------------------------------------------------------------------------


def distance_rule() -> InformationRule:
    """The rule the columns read the two legs through at the declared instant, per H.4.1 release (#622)."""

    if s598.DECISION_TIME != DECISION_TIME:
        raise ValueError(f"the columns are built at {s598.DECISION_TIME}, not at the declared instant {DECISION_TIME}")
    return s598.distance_rule()


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


def build_columns(rows, *, check_every: int = CHECK_EVERY, release: bool = True, rule: Optional[InformationRule] = None):
    """`rows` with the two distance columns at the declared instant, checked for look-ahead (`satiation.check_distance_no_future`)."""

    return s598.distance_rows(rows, LAST_DAY, check_every, rule=rule, release=release)


def prechecks_of(rows, check_every: int = CHECK_EVERY) -> dict:
    """The two checks of the declaration: #621 (the hinge share by year) and #622 (the weekly lag against the per-release read), at 18:00."""

    release = build_columns(rows, check_every=check_every)
    with s598.switched_on():
        weekly_rule = InformationRule(s598.measurement_fields.load_registry(), sat.READ_FEATURES, decision_time=DECISION_TIME, horizon=1)
    weekly = build_columns(rows, check_every=check_every, release=False, rule=weekly_rule)
    gaps, flips, flip_days = [], 0, []
    for a, b in zip(release, weekly):
        da, db = a.values.get(sat.DISTANCE_COLUMN), b.values.get(sat.DISTANCE_COLUMN)
        if da is None or db is None:
            continue
        if da != db:
            gaps.append(abs(da - db) * 100.0)
        if (a.values[sat.HINGE_COLUMN] > 0.0) != (b.values[sat.HINGE_COLUMN] > 0.0):
            flips += 1
            flip_days.append(a.date.isoformat())
    values = [(r.values.get(sat.DISTANCE_COLUMN), r.values.get(sat.HINGE_COLUMN)) for r in release]
    return {
        "decision_time": DECISION_TIME.strftime("%H:%M"), "rows": len(rows), "check_every": check_every,
        "rows_with_a_value": sum(1 for d, _h in values if d is not None), "first_row_with_a_value": next(i for i, (d, _h) in enumerate(values) if d is not None),
        "no_future_check": "passed (satiation.check_distance_no_future, LookAheadError on a value that depends on a later row)",
        "hinge_share_by_year": {"per_release_18:00": s598.hinge_share_by_year(release), "weekly_lag_18:00": s598.hinge_share_by_year(weekly)},
        "weekly_against_per_release": {
            "rows_where_the_distance_differs": len(gaps), "median_pp": statistics.median(gaps) if gaps else 0.0, "largest_pp": max(gaps) if gaps else 0.0,
            "hinge_switches_differently_on_days": flips, "hinge_flip_days_first_ten": flip_days[:10],
        },
        "distance_pp": {"min": min(d for d, _h in values if d is not None) * 100.0, "median": statistics.median(d for d, _h in values if d is not None) * 100.0,
                        "max": max(d for d, _h in values if d is not None) * 100.0},
    }


def prechecks(args) -> int:
    declaration = committed_declaration()
    del declaration
    panel_rows = [row for row in load_daily_panel(Path(args.aug_panel)) if row.date <= LAST_DAY]
    require_exploratory_window([r.date for r in panel_rows], where="scripts/satiation_arm_1507")
    out = prechecks_of(panel_rows, args.check_every)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the walk ------------------------------------------------------------------------------------------------------------


def walks_of(window: str, frame, panel, built, splits, registry, results, auctions, first: Optional[date]):
    """One walk of the candidate and the two satiation arms, over #1255's decision days.

    Raises:
        ValueError: the walk is not at the declared decision instant, the built rows are not the panel's days, or a scored decision day has no
            forecast of an arm.
    """

    if k.DECISION_TIME != DECISION_TIME:
        raise ValueError(f"the walks run at {k.DECISION_TIME}, not at the declared decision instant {DECISION_TIME}")
    if [r.date for r in built] != [r.date for r in panel]:
        raise ValueError("the rows carrying the satiation columns are not the panel's days")
    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, announcements, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    satiation_table = s3c_satiation.MergedTable(
        s3c_satiation.SatiationTable(built, sc.SATIATION_DIST), s3c_satiation.SatiationTable(built, sc.SATIATION_HINGE))
    walk = sc.walk(panel, days, term_table, states, WALK_ARMS, sizes=net_table, iorb=satiation_table, **settings)
    for arm in WALK_ARMS:
        for d in frame.days:
            if d not in walk.forecasts[arm.name]:
                raise ValueError(f"the walk has no forecast of {arm.name} on the scored decision day {d}")
    return walk


def build(window: str, panel, built, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with the candidate and the two arms added: `(frame, notes, walk, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk = walks_of(window, frame, panel, built, splits, registry, results, auctions, first)
    forecasts = {S3: frame.forecasts[S3], S3C: frame.forecasts[S3C]}
    for arm in WALK_ARMS:
        found = {d: walk.forecasts[arm.name][d] for d in frame.days}
        forecasts[model_of(arm)] = m1255.s3c_forecasts(frame, register, found)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    return frame, dict(notes, refits=len(walk.fits)), walk, groups_fn


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
                    "differing_cells": {name: m1273.lead_difference(frame, ANNNET, name) for name in ARMS},
                    "fits": effects_of(walk, window)}
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def effects_of(walk, window: str) -> dict:
    """The fitted coefficient of each satiation term (standardised units) over the refits of the walk, per lead: mean, min, max, and the refits in which it entered."""

    out: Dict[str, Dict[str, dict]] = {}
    for arm, term in ((DIST_ARM, sc.SATIATION_DIST), (HINGE_ARM, sc.SATIATION_HINGE)):
        per_lead: Dict[str, dict] = {}
        for h in sp.HORIZONS:
            found = [estimates[arm.name][h].effect[term] for estimates in walk.estimates.values() if term in estimates[arm.name][h].effect]
            per_lead[str(h)] = {"refits": len(walk.estimates), "entered": len(found),
                                "mean": statistics.fmean(found) if found else None, "min": min(found) if found else None, "max": max(found) if found else None}
        out[model_of(arm)] = per_lead
    return out


def against_1483(result: Mapping[str, dict], window: str) -> dict:
    """The pooled means of the references and the candidate here beside #1483's record: the control is #1483's, so they agree to rounding."""

    if not RECORD_1483.exists():
        return {}
    there = json.loads(RECORD_1483.read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all decision days"]
    here = result["groups"]["pooled"]["all decision days"]
    return {m: {x: {"now": here[m]["means"][x], "then": there[m]["means"][x], "difference": here[m]["means"][x] - there[m]["means"][x]}
                for x in (S3, S3C, ANNNET)} for m in ("grid_crps", "upper_tail_twcrps", "brier_gt5")}


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
    require_exploratory_window([row.date for row in panel], where="scripts/satiation_arm_1507")
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
        "issue": 1507, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha, "window": args.window,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arms": list(ARMS), "rows": [list(r) for r in ROWS], "reading_rules": declaration["reading_rules"], "data": out,
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
        "issue": 1507, "declaration": first["declaration"], "panel_sha256": first["panel_sha256"], "decision_time": first["decision_time"],
        "label": first["label"], "seed": first["seed"], "draws": first["draws"], "reps": first["reps"], "models": first["models"], "arms": first["arms"],
        "rows": first["rows"], "reading_rules": declaration["reading_rules"],
        "windows": {w: p["data"] for w, p in parts.items()}, "against_1483": {w: p["against_1483"] for w, p in parts.items()}, "prechecks": checks,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def _pct(x: float) -> str:
    return f"{100.0 * x:.0f}%"


def hinge_table(checks: Mapping[str, object]) -> List[str]:
    shares = checks["hinge_share_by_year"]
    years = sorted({y for s in shares.values() for y in s})
    out = ["| hinge on, by year | " + " | ".join(years) + " |", "|---|" + "---|" * len(years)]
    for label, s in (("per H.4.1 release at 18:00 (in force)", shares["per_release_18:00"]), ("weekly lag at 18:00 (the first build's read)", shares["weekly_lag_18:00"])):
        out.append(f"| {label} | " + " | ".join(f"{_pct(s[y][0] / s[y][1])} ({s[y][0]} of {s[y][1]})" if y in s else "-" for y in years) + " |")
    return out


def prechecks_section(r: Mapping[str, object]) -> List[str]:
    p = r["prechecks"]
    w = p["weekly_against_per_release"]
    shares = p["hinge_share_by_year"]["per_release_18:00"]
    quiet = [shares[y][0] / shares[y][1] for y in ("2022", "2023")]
    busy = [shares[y][0] / shares[y][1] for y in ("2018", "2019", "2025")]
    return [
        "## Checks of the columns at 18:00 (findings #621 and #622)", "",
        f"The columns are built at the {p['decision_time']} decision instant on {p['rows']:,} panel rows; {p['rows_with_a_value']:,} have a value (the first at row "
        f"{p['first_row_with_a_value']}). Look-ahead: {p['no_future_check']}, rebuilt every {p['check_every']} row(s).", "",
        "**#621: does the rolling level act as a two-year reserves low?** Share of days the hinge is on (the ratio below the rolling level):", ""] + hinge_table(p) + [
        "",
        f"A hinge that is on for {_pct(min(quiet))} to {_pct(max(quiet))} of the days of 2022 and 2023, years with no pressure days, and for {_pct(min(busy))} to "
        f"{_pct(max(busy))} of the days of 2018, 2019 and 2025, is a signal of reserves being low against their own last two years, not of closeness to a "
        "demand-curve kink: finding #621 holds at the 18:00 instant. Nothing here changes the level's rule (#587's constants are unchanged); it is the reading to "
        "keep in mind for the rows below. Per-year shares are measurements of the column, not a result of the walk.", "",
        "**#622: does the column read reserves one release behind?** The built columns on the per-release read (in force since #647) against the weekly lag, both at "
        f"18:00: the distance differs on {w['rows_where_the_distance_differs']:,} rows (median {w['median_pp']:.2f} pp, largest {w['largest_pp']:.2f} pp), and the "
        f"hinge switches on or off differently on {w['hinge_switches_differently_on_days']} days. The weekly lag is the older read, so the difference is staleness, "
        "not leakage; the walk reads the per-release build.", ""]


def render(r: dict) -> str:
    out = [
        "# The satiation-distance arm of the family ablation (#1507)", "",
        "**Does the daily as-of satiation distance, added as one term, help the candidate (s3c-ann-net)?** The first table is the answer: one row per column, the "
        "candidate with the term against the candidate, on grid CRPS and upper-tail twCRPS in both windows. A positive skill and a positive mean d say the term "
        "helps; the reading is taken from the studentized bound on mean d (her ruling on #1009).", "",
        "**Hypothesis and step:** H5 (primary goal), step 2, a follow-up of #1483 (milestone H5.M3). **Development data, not a verdict** (scoring protocol v1, #640). "
        "Her ruling of 7 November 2026 (decision docket, card f1505-satiation-row, option run-arm), from finding #1505. **(s3c-ann-net) stays the candidate; nothing here "
        "changes it.** Nothing is registered or published and no claim changes; H5.M3 is not re-marked. Generated by `scripts/satiation_arm_1507.py page` from "
        f"`docs/research/satiation-arm-1507/result.json`, not edited by hand; declared in `{r['declaration']}` (a dated amendment of `metadata/family_ablation_1483.json`) "
        "before any score.", "",
        "**What was wrong.** #1483's declaration and page said no daily as-of satiation-distance series exists on main. `satiation_dist_roll` and `satiation_hinge_roll` "
        "(`repo_model.satiation`, #598) are exactly such columns, built from the as-of reserves ratio with no row after the one read. They were off in every published "
        "declaration, which is why they were missed.", "",
        "## The rows", "",
        "| term | contrast | " + " | ".join(f"{WINDOW_TITLES[w].split(' (')[0]}: {METRIC_TITLES[m]}" for w in ("development", "2026") for m in TESTED[:2]) + " |",
        "|---|---|" + "---|" * 4]
    for key, _family, with_, without in ROWS:
        out.append(f"| {ROW_TITLES[key]} | {SHORT[with_]} against {SHORT[without]} | " + " | ".join(
            "not run" if fa.pooled(r, w) is None else fa.cell(fa._vs(fa.pooled(r, w), m, with_, without)) for w in ("development", "2026") for m in TESTED[:2]) + " |")
    out += ["", ""]
    out += [
        f"Panel digest `{r['panel_sha256']}`, built at the 18:00 decision instant. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']} (#1483's), two-sided 90% interval (the lower end is the one-sided 95% bound). **Caveat (Lens C, #958):** the lag-10 HAC "
        "standard error that studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals of a "
        "group of target days keep the **current method** (#1221 questions it and #1228 will decide); no reading of a group is a finding. Groups of fewer than 20 days are "
        "listed and not tested.", ""]
    out += prechecks_section(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n = w["notes"]
        out += [f"## {WINDOW_TITLES[window]}", "", f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits.", ""]
        for key, _family, with_, without in ROWS:
            out += [f"### {ROW_TITLES[key][0].upper() + ROW_TITLES[key][1:]}", ""]
            for split, title in (("pooled", "Pooled"), ("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
                table = m1288.split_table(w, split, with_, without)
                if table:
                    out += [f"#### {title}: {SHORT[with_]} against {SHORT[without]}", ""] + table + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
        out += fit_lines(w)
    out += control_section(r)
    return "\n".join(out).rstrip() + "\n"


def fit_lines(w: Mapping[str, object]) -> List[str]:
    """How often the term entered the fit and its coefficient (standardised units), per lead."""

    fits = w.get("fits")
    if not fits:
        return []
    out = ["### The fitted coefficient of the term", "",
           "Coefficient of the term in the Huber fit over the refits of the walk, in scale units per percentage point of the column (the effect in bp is the coefficient times the "
           "anchor's scale). `entered` counts the refits in which the term had enough non-zero pairs.", "",
           "| term | lead | refits | entered | mean | min | max |", "|---|---|---|---|---|---|---|"]
    for name in ARMS:
        for h, e in fits[name].items():
            out.append(f"| {SHORT[name]} | h={h} | {e['refits']} | {e['entered']} | " + " | ".join("n/a" if e[x] is None else f"{e[x]:+.4f}" for x in ("mean", "min", "max")) + " |")
    return out + [""]


def control_section(r: Mapping[str, object]) -> List[str]:
    diffs = [abs(v["difference"]) for a in r.get("against_1483", {}).values() for ms in a.values() for v in ms.values()]
    if not diffs:
        return []
    return ["## The control against #1483's record", "",
            "(s3), (s3c) and (s3c-ann-net) are re-run in this walk; the pooled means of all three metrics, in both windows, are compared with `docs/research/family-ablation-1483/result.json`. "
            f"Largest absolute difference of a pooled mean: {max(diffs):.1e}. Shown, not required to agree; no record is edited.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prechecks", help="the checks of findings #621 and #622 on the columns at 18:00")
    p.add_argument("--aug-panel", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--check-every", type=int, default=CHECK_EVERY)
    p.set_defaults(func=prechecks)
    s = sub.add_parser("score", help="walk the candidate and the two satiation arms on one window, cap them as (s3c) is capped, and score")
    s.add_argument("--panel", required=True)
    s.add_argument("--aug-panel", required=True)
    s.add_argument("--window", required=True, choices=list(WINDOWS))
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized intervals")
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
