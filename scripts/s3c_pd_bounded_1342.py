"""(s3c-pd) with the weekly-carry bound on, scored at the 18:00 decision against (s3c-ann-net) and (s3c)
(#1342; H5 step 3; her ruling of 1 November 2026 on #1340, option (a); after #1341).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_pd_bounded_1342.json`, which this script refuses to read unless it is committed and unchanged. It scores the variant `carry_bounded_v2` that
`metadata/s3c_pd_1329.json` declared and left unscored: (s3c-pd) of #1296 (`repo_model.s3c_pd`: (s3)'s fit with one state term, the z-score of the latest
public week's primary dealer financing level against the year before it, then (s3c)'s SRF cap at full allotment), with the state read as the weekly-carry
bound has it (`docs/decisions/weekly-carry.md`, as #1341 amended it): a level more than `data.WEEKLY_CARRY_MAX_STALENESS_DAYS` days older than the
latest public week is no level, and the state is unknown once the newest public week is older than the bound from the decision day plus the source's
release lag. #1296's script kept the unbounded read so that its record reproduces; this one takes the defaults of `s3c_pd`, and reads the state and walks
at the declared 18:00 instant (`repo_model.decision_instant`), pinned.

The decision days are put in four classes by the state they read: *fresh* (the level read is the latest public week's own), *carried* (older, within the
bound), *removed by the bound* (defined on the unbounded read, not on this one: the term reads 0 and the arm is (s3c) up to the refit) and *no state*.
The pooled figure moves toward (s3c) by construction on the days the bound removed, so the fresh-state days are read beside it.

The frames and the machinery are #1255's, #1288's and #1321's and are loaded as they are: the development window (targets up to 2025-12-31) and the 2026
development days (targets 2026-01-02 to 2026-09-03, the near-blind tier open since GO #151); the blind tier and every lockbox day are refused by the
frames' own guards. (s3c-ann-net) is walked as #1321 walked it, at 18:00; the state walk's (s3) must equal the frame's (s3) cell for cell, and the
pooled means of (s3c) and (s3c-ann-net) must equal #1321's record to 1e-9, or the run stops.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp), on scoring protocol v1's
studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill interval beside, split by lead, regime (the 2026 days in
their own window), pressure-day type and the state class of the decision day.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_pd_bounded_1342.py score --panel PUB.csv --output docs/research/s3c-pd-bounded-1342/result.json
    PYTHONPATH=src python3 scripts/s3c_pd_bounded_1342.py page \\
        --score docs/research/s3c-pd-bounded-1342/result.json --output docs/research/s3c-pd-bounded-1342-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
from collections import Counter
from datetime import date, time
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


from repo_model import announced_iorb, metrics, policy_events, s3c_announced, s3c_net, s3c_pd  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.decision_instant import DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1356's script (and through it #1321's, #1288's, #1273's and #1255's), loaded under an alias of its own so that the pickling of the worker pool's tasks
#: does not meet another test module's copy. Its `decision_instant_pinned` runs the chain at the declared 18:00 instant.
m1356 = _load("s3c_ann_net_cmb_1356", "s3c_ann_net_cmb_1356_in_1342")
m1321, m1288, m1273, m1255 = m1356.m1321, m1356.m1288, m1356.m1273, m1356.m1255
k, c, s686, s761 = m1356.k, m1356.c, m1356.s686, m1356.s761
load_daily_panel = m1288.load_daily_panel
decision_instant_pinned = m1321.decision_instant_pinned

DECLARATION = REPO / "metadata" / "s3c_pd_bounded_1342.json"
OLDER_DECLARATION = REPO / "metadata" / "s3c_pd_1329.json"
SNAPSHOT = REPO / "tests" / "fixtures" / "snapshots" / "nyfed-pd-financing"
RECORD_1296 = REPO / "docs" / "research" / "s3c-pd-1296" / "result.json"
RECORD_1321 = REPO / "docs" / "research" / "s3c-flagnet-gross-1321" / "result.json"
SEED = 1342
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3, S3C, ANNNET, B1P = k.S3, m1288.S3C, m1288.ANNNET, k.B1P
PDB = "sc_s3c_pd_bounded"
BENCHMARKS = m1288.BENCHMARKS
MODELS = BENCHMARKS + (S3C, ANNNET, PDB)
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3C: "(s3c), the H5 candidate", ANNNET: "(s3c-ann-net), the candidate of #1318",
          PDB: "(s3c-pd), bounded"}
SHORT = {"B1": "B1", B1P: "B1'", "B2": "B2", S3C: "(s3c)", ANNNET: "(s3c-ann-net)", PDB: "(s3c-pd), bounded"}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
REPS = 2000
#: The weekly-carry bound: the panel's constant, never a copy (`s3c_pd.MAX_CARRY_DAYS` is it).
MAX_CARRY_DAYS: int = s3c_pd.MAX_CARRY_DAYS
#: The classes of a decision day by the state it reads, the split that holds them, and their titles.
CLASSES = ("fresh", "carried", "removed_by_bound", "no_state")
CLASS_SPLIT = "state_class"
CLASS_TITLES = {"fresh": "state fresh (the latest public week's own level)", "carried": "state carried over a withheld week (within the bound)",
                "removed_by_bound": "state removed by the bound (the term reads 0)", "no_state": "no state on either read"}
_STATE: Dict = {}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def declaration_variant() -> str:
    """The variant of `metadata/s3c_pd_1329.json` this study scores."""

    return json.loads(DECLARATION.read_text(encoding="utf-8"))["variant"]


def plan(candidate: str) -> List[str]:
    """What (s3c-pd), bounded, is tested against: (s3c-ann-net) and (s3c). The benchmarks are scored beside them and compared on their means."""

    return [ANNNET, S3C] if candidate == PDB else []


def require_instant(decision_time: time) -> None:
    """Refuse to make this study at another decision instant than the declared 18:00.

    Raises:
        ValueError: `decision_time` is not `repo_model.decision_instant.DECISION_TIME`.
    """

    if decision_time != DECISION_TIME:
        raise ValueError(f"the chain runs at {decision_time}, not the declared decision instant {DECISION_TIME}")


# -- the state, bounded --------------------------------------------------------------------------------------------------


def bounded_states(levels: Mapping[date, Optional[float]], days: Sequence[date]) -> Dict[date, Optional[float]]:
    """The state a decision on each day could read: the bounded read of the weekly-carry record, at the declared 18:00 instant.

    Recorded mutation: see `tests/test_s3c_pd_bounded_1342.py` (`max_carry_days=None` for `max_carry_days=MAX_CARRY_DAYS`).
    """

    return s3c_pd.decision_states(levels, days, decision_time=DECISION_TIME, max_carry_days=MAX_CARRY_DAYS)


def state_class(levels: Mapping[date, Optional[float]], day: date) -> str:
    """The class of a decision day: `fresh`, `carried`, `removed_by_bound` or `no_state` (see `CLASSES`)."""

    if bounded_states(levels, [day])[day] is not None:
        return "fresh" if s3c_pd.skipped_weeks(levels, day, decision_time=DECISION_TIME) == 0 else "carried"
    unbounded = s3c_pd.state_at(levels, day, decision_time=DECISION_TIME, max_carry_days=None)
    return "removed_by_bound" if unbounded is not None else "no_state"


def level_behind_days(levels: Mapping[date, Optional[float]], day: date) -> Optional[int]:
    """How many days older than the latest public week the level read on `day` is (the quantity the bound limits), or `None` with no level."""

    week = s3c_pd.latest_defined_week(levels, day, decision_time=DECISION_TIME, max_carry_days=MAX_CARRY_DAYS)
    latest = s3c_pd.latest_public_week(levels, day, decision_time=DECISION_TIME)
    return None if week is None or latest is None else (latest - week).days


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def candidate_days(panel, last: date, first: Optional[date]) -> List[date]:
    """The decision days of #1255's frames: every panel day whose fifth target is on or before `last` (from `first`, in a test)."""

    dates = [row.date for row in panel]
    return [d for i, d in enumerate(dates) if i + max(sp.HORIZONS) < len(panel) and dates[i + max(sp.HORIZONS)] <= last and (first is None or d >= first)]


def require_same_s3(frame, walk) -> None:
    """The state walk's (s3) must be the frame's, cell for cell, and every frame day must be in the walk.

    Raises:
        ValueError: a frame day is not in the walk, or (s3) re-forecast in the walk differs from the frame's.
    """

    s3 = frame.forecasts[S3]
    for d in frame.days:
        if d not in walk.forecasts:
            raise ValueError(f"the decision day {d} is in the frame and not in the state walk")
        if walk.s3[d] != s3[d]:
            raise ValueError(f"(s3) of the state walk differs from the frame's (s3) on the decision day {d}")


def annnet_walk(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """(s3c-ann-net) walked over #1255's decision days, as #1321 and #1356 walked it (the scarcity state held constant).

    Raises:
        ValueError: a scored decision day has no forecast.
    """

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    term_table = s3c_announced.AnnouncedTermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    walk = sc.walk(panel, days, term_table, s3c_net.constant_states(panel), (s3c_announced.ANN_NET_ARM,), sizes=net_table, **settings)
    for d in frame.days:
        if d not in walk.forecasts[s3c_announced.ANN_NET_ARM.name]:
            raise ValueError(f"the (s3c-ann-net) walk has no forecast on the scored decision day {d}")
    return walk


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date], walk: s3c_pd.PdWalk):
    """#1255's frame of `window` with (s3c-ann-net) and (s3c-pd), bounded, added: `(frame, notes, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    require_same_s3(frame, walk)
    ann = annnet_walk(window, frame, panel, splits, registry, results, auctions, first)
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS + (S3C,)}
    forecasts[ANNNET] = m1255.s3c_forecasts(frame, register, {d: ann.forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in frame.days})
    forecasts[PDB] = m1255.s3c_forecasts(frame, register, {d: walk.forecasts[d] for d in frame.days})
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    return frame, dict(notes, refits_ann_net=len(ann.fits)), groups_fn


# -- what the bound did --------------------------------------------------------------------------------------------------


def term_use(frame, walk: s3c_pd.PdWalk, classes: Mapping[date, str], levels) -> dict:
    """The decision days by state class, how far behind the latest public week the level read is, where (s3c-pd), bounded, differs from (s3c), by lead,
    and the refits in which the term is active."""

    behind = [level_behind_days(levels, d) for d in frame.days if walk.values[d] is not None]
    if any(x is None or x > MAX_CARRY_DAYS for x in behind):
        raise ValueError("a state is defined on a level older than the weekly-carry bound")
    out: dict = {"decision_days": len(frame.days), "class_counts": {x: sum(1 for d in frame.days if classes[d] == x) for x in CLASSES},
                 "days_with_state": len(behind), "level_behind_days": {str(x): n for x, n in sorted(Counter(behind).items())},
                 "largest_level_age_days": max(behind) if behind else None, "differs_from_s3c": {}}
    s3c, pdb = frame.forecasts[S3C], frame.forecasts[PDB]
    for h in LEADS:
        out["differs_from_s3c"][str(h)] = sum(1 for d in frame.days if list(s3c[d][h]) != list(pdb[d][h]))
    used = sorted({walk.fit_used[d] for d in frame.days})
    out["refits_in_use"] = len(used)
    out["refits_active"] = {str(h): sum(1 for r in used if walk.estimates[r][h].active) for h in LEADS}
    return out


def class_groups(frame, classes: Mapping[date, str]) -> List[Tuple[str, str, str, List[date]]]:
    """One group per state class, over the decision days (the grain of the cells)."""

    return [(CLASS_SPLIT, CLASS_TITLES[x], "decision", [d for d in frame.days if classes[d] == x]) for x in CLASSES]


# -- the tests -----------------------------------------------------------------------------------------------------------


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def unstudentized(series, candidate: str, reference: str, members: Sequence[date], reps: int) -> dict:
    """Mean d and its 90% stationary-bootstrap percentile interval, for a group whose studentized bound cannot be computed. Not the protocol's
    interval; no reading is taken from it. `d = S(reference) - S(candidate)`, positive favours the candidate."""

    d = [series[reference][x] - series[candidate][x] for x in sorted(members)]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=BLOCK, seed=SEED, replications=reps)
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
            out[name]["unstudentized"] = unstudentized(series, candidate, name, days, _STATE["reps"])
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args, walk, classes, levels) -> dict:
    frame, notes, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first, walk)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in SPLITS] + class_groups(frame, classes)
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
            jobs.append((split, label, grain, metric, PDB, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {"notes": notes, "groups": {}, "skipped_groups": skipped, "term_use": term_use(frame, walk, classes, levels)}
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS} if members else {}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def against_1321(results: Mapping[str, dict]) -> dict:
    """The pooled means of (s3c) and (s3c-ann-net) here beside #1321's record, made at 18:00 with the same walks: they must agree to 1e-9.

    Raises:
        ValueError: they do not.
    """

    return m1356.against_1321(results) if RECORD_1321.exists() else {}


def record_1296() -> dict:
    """#1296's published pooled rows of (s3c-pd) against (s3c) (16:00, unbounded read), for the page to quote beside this study's. Not re-scored."""

    if not RECORD_1296.exists():
        return {}
    there = json.loads(RECORD_1296.read_text(encoding="utf-8"))["windows"]
    return {window: {m: there[window]["groups"]["pooled"]["all decision days"][m]["vs"]["sc_s3c_pd"][S3C] for m in TESTED} for window in there}


def snapshot_record() -> dict:
    """The tracked snapshot, refused unless every byte is the manifest's (scripts/fetch_pd_financing_1296.py check), and its manifest."""

    fetch = _load("fetch_pd_financing_1296", "fetch_pd_financing_1296_in_1342")
    if fetch.check() != 0:
        raise SystemExit("the tracked primary dealer snapshot differs from its manifest")
    return json.loads((SNAPSHOT / "manifest.json").read_text(encoding="utf-8"))


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    manifest = snapshot_record()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_pd_bounded_1342")
    require_instant(c.DECISION_TIME)
    require_instant(k.DECISION_TIME)
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    levels = s3c_pd.load_levels(SNAPSHOT)
    dates = [row.date for row in panel]
    states = bounded_states(levels, dates)
    classes = {d: state_class(levels, d) for d in dates}
    days = candidate_days(panel, LAST_DAY, args.first)
    s686.require_scored_days(days, LAST_DAY)
    walk = s3c_pd.walk(panel, days, table, states, registry=registry, decision_time=DECISION_TIME, splits=splits)
    result: dict = {
        "issue": 1342, "declaration": str(DECLARATION.relative_to(REPO)), "variant": declaration["variant"], "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "bound_days": MAX_CARRY_DAYS, "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": PDB,
        "references": [ANNNET, S3C] + list(BENCHMARKS),
        "snapshot": {item["keyid"]: {"sha256": item["sha256"], "retrieved_at": item["retrieved_at"]} for item in manifest["files"]},
        "levels": {"weeks": len(levels), "with_level": sum(1 for v in levels.values() if v is not None), "first": min(levels).isoformat(),
                   "last": max(levels).isoformat(), "release_lag_business_days": s3c_pd.RELEASE_LAG_BUSINESS_DAYS,
                   "release_time": s3c_pd.RELEASE_TIME.strftime("%H:%M"), "trailing_weeks": s3c_pd.TRAILING_WEEKS,
                   "minimum_trailing_weeks": s3c_pd.MIN_TRAILING},
        "reading_rules": declaration["reading_rules"], "state_classes": declaration["state_classes"],
        "walk": {"decision_days": len(walk.forecasts), "skipped": len(walk.skipped), "refits": len(walk.estimates)}, "windows": {},
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args, walk, classes, levels)
    result["against_1321"] = against_1321(result["windows"]) if args.first is None else {}
    result["record_1296"] = record_1296()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


cell = m1356.cell
_vs = m1356._vs


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text} (s3c-pd), bounded, on grid CRPS against (s3c-ann-net): {cell(_vs(entry, 'grid_crps', PDB, ANNNET))}; "
                     f"against (s3c): {cell(_vs(entry, 'grid_crps', PDB, S3C))}")
    return "; ".join(parts) + "."


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = ["| (s3c-pd), bounded, against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(PDB):
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, PDB, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, reference: str, order: Optional[Sequence[str]] = None) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|---|" + "---|" * len(TESTED)]
    for label in (order if order is not None else sorted(labels)):
        if label not in labels:
            continue
        g = labels[label]
        skipped = f"{split}/{label}" in window["skipped_groups"]
        out.append(f"| {label} | {g['days']} | " + " | ".join(
            "not tested (fewer than 20 days)" if skipped else cell(_vs(g, m, PDB, reference)) for m in TESTED) + " |")
    return out if len(out) > 2 else []


def class_table(use: Mapping[str, object]) -> List[str]:
    out = ["| state class of the decision day | decision days |", "|---|---|"]
    for x in CLASSES:
        out.append(f"| {CLASS_TITLES[x]} | {use['class_counts'][x]} |")
    return out


def behind_table(use: Mapping[str, object]) -> List[str]:
    out = ["| level read, days behind the latest public week | decision days with a state |", "|---|---|"]
    for days_, n in use["level_behind_days"].items():
        out.append(f"| {days_} | {n} |")
    return out


def differ_table(use: Mapping[str, object]) -> List[str]:
    out = ["| lead | cells where (s3c-pd), bounded, differs from (s3c) | refits in use with the term active |", "|---|---|---|"]
    for h in LEADS:
        out.append(f"| {h} | {use['differs_from_s3c'][str(h)]} of {use['decision_days']} | {use['refits_active'][str(h)]} of {use['refits_in_use']} |")
    return out


def beside_1296(r: Mapping[str, object]) -> List[str]:
    """#1296's published rows beside this study's: two records at two instants, not a paired test."""

    there = r.get("record_1296") or {}
    if not there:
        return []
    out = ["## Beside #1296 (context, not a test)", "",
           "#1296's record was made at 16:00 with no limit on the weeks a level is carried, and it stands unedited. The rows below are its published figures "
           "for (s3c-pd) against (s3c) on grid CRPS, next to this study's at 18:00 with the bound. The two differ in the instant and in the bound at once, "
           "so no paired test between them is made and none of the difference is put down to either.", "",
           "| window | #1296: (s3c-pd), unbounded, 16:00, against (s3c) | here: (s3c-pd), bounded, 18:00, against (s3c) |", "|---|---|---|"]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None or window not in there:
            continue
        mine = w["groups"]["pooled"]["all decision days"]
        out.append(f"| {WINDOW_TITLES[window].split(' (')[0]} | {cell(there[window]['grid_crps'])} | {cell(_vs(mine, 'grid_crps', PDB, S3C))} |")
    return out + [""]


def render(r: dict) -> str:
    lv = r["levels"]
    out = [
        "# (s3c-pd) with the weekly-carry bound, at 18:00 (#1342)", "",
        "**Was the loss of the primary dealers' financing level in #1296 a loss of the input, or of how stale the level it read could be?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c) with a source already tracked; her ruling of 1 November 2026 "
        "(chat, relayed on #1340; ledger item 93), option (a), after #1341. **Development data, not a verdict** (scoring protocol v1, #640). Nothing is "
        "registered or published and no claim changes; #1296's page and record are not edited, and stand as made (16:00, no limit on the carry). "
        "**(s3c-pd), bounded,** is the variant `carry_bounded_v2` of `metadata/s3c_pd_1329.json`: (s3c) with one state term added to (s3)'s fit, the z-score of "
        f"the latest public week's level of the sum of four New York Fed primary dealer (FR 2004) Treasury totals against the {lv['trailing_weeks']} weeks "
        f"before it, read as `docs/decisions/weekly-carry.md` has it since #1341: a level more than {r['bound_days']} days older than the latest public "
        f"week is no level, and the state is unknown once the newest public week is older than {r['bound_days']} days from the decision day plus the "
        "source's release lag. The term then reads 0, as an unknown state does. The state and the walk are read at the declared 18:00 instant, pinned. "
        "Every other term, the Huber fit, the ridge of 5 and the SRF cap at full allotment are (s3c)'s (`repo_model.s3c_pd`). Generated by "
        "`scripts/s3c_pd_bounded_1342.py page` from `docs/research/s3c-pd-bounded-1342/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        f"Panel digest `{r['panel_sha256']}`. Decision instant {r['decision_time']} New York. Studentized stationary bootstrap (ruling 1), mean block "
        f"{sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive "
        "mean d favours the model named first. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill "
        "interval beside it; for a Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The groups of target days "
        "keep the current method, which #1221 questions and #1228 will decide. Where two models score alike on every day of a group it is listed as identical "
        "and not tested; groups of fewer than 20 days are listed with their means and not tested; where the studentized bound cannot be computed the "
        "unstudentized interval of mean d is given beside it and no reading is taken from it.", "",
        "**What kind of look this is.** The development window and the 2026 days were already seen by the predecessors (#1145, #1229, #1255, #1296 and the "
        "studies after them). This is a check on how an input was read, not evidence for a verdict. The 2026 days are shown in a window of their own.", "",
        "**What to read first.** On the days the bound removed, (s3c-pd), bounded, is (s3c) up to the refit, so a pooled figure moves toward (s3c) by "
        "construction and could turn a loss into a draw without the dealer level adding anything. The days on which the state is fresh (the level read is "
        "the latest public week's own) are therefore read beside the pooled figure, under \"By the state class of the decision day\" in each window.", ""]
    out += beside_1296(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled, use = w["notes"], w["groups"]["pooled"]["all decision days"], w["term_use"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {use['days_with_state']:,} of the {use['decision_days']:,} "
                f"decision days read a state. The state walk refit {r['walk']['refits']} times over the whole panel ({use['refits_in_use']} refits in use in this window). "
                f"The largest age of a level read is {use['largest_level_age_days']} days behind the latest public week, against the bound of {r['bound_days']}; "
                "the run refuses a state on an older one.", "",
                "### The state classes", ""] + class_table(use) + ["", "The level read, in days behind the latest public week (0 is the latest week's own):", ""] + behind_table(use) + [""]
        out += ["### Mean scores (all decision days)", ""] + mean_table(pooled) + ["", "### (s3c-pd), bounded, against the references (all decision days)", ""] + against_table(pooled) + [""]
        out += ["### Where the term acts", ""] + differ_table(use) + [""]
        for ref in (ANNNET, S3C):
            for split, title in ((CLASS_SPLIT, "the state class of the decision day"), ("regime", "regime"), ("pressure_day_type", "pressure-day type of the target day"),
                                 ("lead", "lead")):
                table = split_table(w, split, ref, [CLASS_TITLES[x] for x in CLASSES] if split == CLASS_SPLIT else None)
                if table:
                    out += [f"### By {title}: (s3c-pd), bounded, against {SHORT[ref]}", ""] + table + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({v})" for x, v in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_1321"):
        out += ["## The references against #1321's record (made at 18:00)", "",
                "(s3c) and (s3c-ann-net) are re-run here with the same walks; the pooled means equal #1321's to 1e-9 (the run refuses to write otherwise). "
                f"Largest absolute difference: {max(abs(v['difference']) for ms in r['against_1321'].values() for rows in ms.values() for v in rows.values()):.1e}.", ""]
    out += ["## What this does not show", "",
            "It does not re-score #1296, and it does not isolate the bound from the instant: no unbounded run at 18:00 was made, so the comparison with #1296 "
            "above changes two things at once. It does not say whether the dealer level helps on days not yet seen: all of these days were seen. The source is "
            f"the latest revised vintage the API served, not first prints; the New York Fed's page says the figures are updated \"approximately\" at 4:15 p.m. "
            f"and the declared instant is {lv['release_lag_business_days']} market business days after the as-of Wednesday at {lv['release_time']}.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**Should anything change because of this result?** This page changes no reading, no registration and no candidate. Whether the input is set aside, "
        "or tried further, rests on development days already seen, split as above, and is yours.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Leave the candidates and the input as they are; queue nothing further on the dealers' financing level** (default).",
        "2. **Queue the bounded dealer state as an arm on (s3c-ann-net)**, declared as its own arm with its own leakage and staleness tests.",
        "3. **Set the input aside for good**, and record that no later arm reads the dealers' financing level."]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3c-ann-net) and the bounded state arm, cap them as (s3c) is capped, and score both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized interval")
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
