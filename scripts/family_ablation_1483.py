"""The family-by-family ablation on the candidate (s3c-ann-net), on direct pairs reading the calendar at the target day (#1483; H5 step 2, milestone
H5.M3; her ruling of 6 November 2026, decision docket, relayed; #1354 Directive B).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/family_ablation_1483.json`, which this script refuses to read unless it is committed and unchanged.

The H5 manual's step 2 names five input families: settlement and H.4.1 timing; the IORB change; the scarcity state read per leg; satiation
distance; tail spread. (s3c-ann-net) reads only the first of them (its settlement terms) and the calendar columns. A family it does not read is a
family whose drop is the candidate itself, so for those the contrast is the nested one: the candidate with the family added, paired against the
candidate. The page says, for each family, what the candidate reads and which of the two it is. `metadata/family_ablation_1483.json` declares the
rows, and which are scored here and which are re-used from records already merged.

Scored here, in one walk per window (the arms share the base fit and #941's pool), on #1255's frames at the 18:00 decision instant:

* (s3c-ann-net-nosettle), (-nocoupon) and (-nobill): (s3c-ann-net) with both settlement terms, or one leg's, taken out of the fit. The other columns,
  the Huber fit, the ridge of 5 and the SRF cap are the candidate's, element for element.
* (s3c-ann): (s3c-ann-net) with the settlement flags in place of the net sizes (the announcement dating without the size). With (s3c), which reads the
  flags at lead 1 only, it separates the timing of the settlement from its size.
* (s3c-ann-net-iorbs): (s3c-ann-net) with `iorb_window`, the signed announced IORB change and the technical-adjustment indicator
  (`spread_mr_state_calendar.IORB_EXTRAS`, #1227's terms), read from the announcement at the decision instant.

Re-used, read from the merged records and not re-run: the scarcity state per leg and the H.4.1 timing (#1350), the tail spread (#1345).

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/family_ablation_1483.py score --panel PUB.csv --window development \\
        --output docs/research/family-ablation-1483/result-development.json
    PYTHONPATH=src python3 scripts/family_ablation_1483.py score --panel PUB.csv --window 2026 \\
        --output docs/research/family-ablation-1483/result-2026.json
    PYTHONPATH=src python3 scripts/family_ablation_1483.py assemble \\
        --output docs/research/family-ablation-1483/result.json
    PYTHONPATH=src python3 scripts/family_ablation_1483.py page \\
        --score docs/research/family-ablation-1483/result.json --output docs/research/family-ablation-1483-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import dataclasses
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


from repo_model import announced_iorb, policy_events, s3c_announced, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.decision_instant import DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1321's script (and through it #1288's, #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the
#: worker pool's tasks does not meet another test module's copy.
m1321 = _load("s3c_flagnet_gross_1321", "s3c_flagnet_gross_1321_in_1483")
m1288, m1273, m1255, k, c, s686, s761 = m1321.m1288, m1321.m1273, m1321.m1255, m1321.k, m1321.c, m1321.s686, m1321.s761
load_daily_panel = m1321.load_daily_panel

DECLARATION = REPO / "metadata" / "family_ablation_1483.json"
RECORD_1350 = REPO / "docs" / "research" / "h41-per-release-1350" / "result.json"
RECORD_1345 = REPO / "docs" / "research" / "h9-nested-1800-1345" / "result.json"
RECORD_1321 = REPO / "docs" / "research" / "s3c-flagnet-gross-1321" / "result.json"
SEED = 1483
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3, S3C, ANNNET, ANN = m1288.S3, m1288.S3C, m1288.ANNNET, m1288.ANN
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
REPS = 2000

# -- the arms ------------------------------------------------------------------------------------------------------------

_BASE = s3c_announced.ANN_NET_ARM
_SETTLEMENT = tuple(sc.SIZED_TERMS)
#: The candidate's terms with the settlement terms in `dropped` taken out; everything else about the arm is the candidate's.
def _without(dropped: Sequence[str]) -> Tuple[str, ...]:
    return tuple(n for n in _BASE.location if n not in dropped)


NOSETTLE_ARM = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_nosettle", location=_without(_SETTLEMENT),
    role="(s3-ann-net-nosettle) (s3-ann-net) without its coupon and bill settlement terms",
)
NOCOUPON_ARM = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_nocoupon", location=_without(("settlement_coupon",)),
    role="(s3-ann-net-nocoupon) (s3-ann-net) without its coupon settlement term",
)
NOBILL_ARM = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_nobill", location=_without(("settlement_bill",)),
    role="(s3-ann-net-nobill) (s3-ann-net) without its bill settlement term",
)
#: (s3c-ann-net) with the IORB family: `iorb_window` and the signed announced change and technical-adjustment indicator (#1227's terms).
IORB_ARM = dataclasses.replace(
    _BASE, name="sc_s3_ann_net_iorbs", location=tuple(n for n in cal.ALL_TERMS if n in _BASE.location or n == "iorb_window"),
    extra=sc.IORB_EXTRAS,
    role="(s3-ann-net-iorbs) (s3-ann-net) with iorb_window and the signed announced IORB change and technical-adjustment indicator",
)
#: The arms of the walk, the candidate first. (s3c-ann) is `s3c_announced.ANN_ARM`: the flags announced, no net size.
WALK_ARMS = (_BASE, s3c_announced.ANN_ARM, NOSETTLE_ARM, NOCOUPON_ARM, NOBILL_ARM, IORB_ARM)


def model_of(arm: sc.StateArm) -> str:
    """The capped model's name: the arm's name with the `c` (`sc_s3_...` is `sc_s3c_...`)."""

    return arm.name.replace("sc_s3_", "sc_s3c_", 1)


NOSETTLE, NOCOUPON, NOBILL, IORBS = (model_of(a) for a in (NOSETTLE_ARM, NOCOUPON_ARM, NOBILL_ARM, IORB_ARM))
ARMS = (NOSETTLE, NOCOUPON, NOBILL, IORBS)
MODELS = (S3, S3C, ANN, ANNNET) + ARMS
LABELS = {
    S3: "(s3)", S3C: "(s3c)", ANN: "(s3c-ann)", ANNNET: "(s3c-ann-net), the candidate", NOSETTLE: "(s3c-ann-net) without settlement",
    NOCOUPON: "(s3c-ann-net) without the coupon term", NOBILL: "(s3c-ann-net) without the bill term", IORBS: "(s3c-ann-net) with the IORB terms",
}
SHORT = {
    S3: "(s3)", S3C: "(s3c)", ANN: "(s3c-ann)", ANNNET: "(s3c-ann-net)", NOSETTLE: "(ann-net) no settlement", NOCOUPON: "(ann-net) no coupon",
    NOBILL: "(ann-net) no bill", IORBS: "(ann-net) + IORB",
}
#: The rows scored here: `(key, family, with the family, without it)`. A row is "the model that reads the family against the one that does not", so
#: a positive mean d (and a positive skill) says the family helps. `candidate` of a job is the "with" model and its references the "without" ones.
ROWS: Tuple[Tuple[str, str, str, str], ...] = (
    ("settlement", "settlement and H.4.1 timing", ANNNET, NOSETTLE),
    ("settlement_coupon", "settlement and H.4.1 timing", ANNNET, NOCOUPON),
    ("settlement_bill", "settlement and H.4.1 timing", ANNNET, NOBILL),
    ("settlement_size", "settlement and H.4.1 timing", ANNNET, ANN),
    ("settlement_timing", "settlement and H.4.1 timing", ANN, S3C),
    ("iorb", "the IORB change", IORBS, ANNNET),
)
ROW_KEYS = tuple(r[0] for r in ROWS)


def plan(candidate: str) -> List[str]:
    """What a model is tested against: the models without the family it reads, in the order of `ROWS`."""

    out: List[str] = []
    for _key, _family, with_, without in ROWS:
        if with_ == candidate and without not in out:
            out.append(without)
    return out


CANDIDATES = tuple(dict.fromkeys(r[2] for r in ROWS))


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the walk ------------------------------------------------------------------------------------------------------------


def walks_of(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """One walk of the candidate and the five arms, over #1255's decision days.

    Raises:
        ValueError: the walk is not at the declared decision instant, or a scored decision day has no forecast of an arm.
    """

    if k.DECISION_TIME != DECISION_TIME:
        raise ValueError(f"the walks run at {k.DECISION_TIME}, not at the declared decision instant {DECISION_TIME}")
    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, announcements, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    iorb_table = sc.IorbTable(panel, announcements, decision_time=k.DECISION_TIME)
    walk = sc.walk(panel, days, term_table, states, WALK_ARMS, sizes=net_table, iorb=iorb_table, **settings)
    for arm in WALK_ARMS:
        for d in frame.days:
            if d not in walk.forecasts[arm.name]:
                raise ValueError(f"the walk has no forecast of {arm.name} on the scored decision day {d}")
    return walk


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with the candidate and the arms added: `(frame, notes, walk, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk = walks_of(window, frame, panel, splits, registry, results, auctions, first)
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


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, walk, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
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
                    "differing_cells": {arm_name: m1273.lead_difference(frame, ANNNET, arm_name) for arm_name in ARMS}}
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def against_1321(result: Mapping[str, dict], window: str) -> dict:
    """The pooled means of the references here beside #1321's record, made at the same instant with the same machinery: they agree to rounding."""

    if not RECORD_1321.exists():
        return {}
    there = json.loads(RECORD_1321.read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all decision days"]
    here = result["groups"]["pooled"]["all decision days"]
    return {m: {x: {"now": here[m]["means"][x], "then": there[m]["means"][x], "difference": here[m]["means"][x] - there[m]["means"][x]}
                for x in (S3, S3C, ANNNET)} for m in ("grid_crps", "upper_tail_twcrps", "brier_gt5")}


def score(args) -> int:
    """Score one window with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with m1321.decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    if args.window not in WINDOWS:
        raise SystemExit(f"--window must be one of {WINDOWS}")
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/family_ablation_1483")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    out = run_window(args.window, panel, splits, registry, table, register, results, auctions, args)
    result: dict = {
        "issue": 1483, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha, "window": args.window,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arms": list(ARMS), "rows": [list(r) for r in ROWS], "margin_bp": s3c_candidate.MARGIN_BP,
        "reading_rules": declaration["reading_rules"], "data": out,
        "against_1321": against_1321(out, args.window) if args.first is None else {},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the records that are re-used ------------------------------------------------------------------------------------------

#: #1350's arms (`scripts/h41_per_release_1350.py`): the candidate (s3c-ann-net) with the scarcity state read (carried), and the same arm with the
#: H.4.1 read per release.
STATE_CARRIED, STATE_PERREL = "sc_s3c_ann_net_state_carried", "sc_s3c_ann_net_state_perrel"
#: #1345's target for the tail: the SOFR dispersion forecast (the nearest of #1345's three targets to the H5 manual's "tail spread").
TAIL_TARGET = "sofr_dispersion_bps"


def reused_1350(record: Mapping[str, object], window: str, split: str, label: str, metric: str, candidate: str, reference: str) -> Optional[dict]:
    """A row of #1350's record: the paired test of `candidate` against `reference` in `window`, scope `all decision days`, group `split/label`."""

    group = record["windows"][window]["groups"]["all"].get(split, {}).get(label)
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(candidate, {}).get(reference)


def reused_rows(record_1350: Mapping[str, object]) -> Dict[str, Dict[str, dict]]:
    """The re-used rows of the two families #1350 measures, by window: the scarcity state per leg (the state arm against the candidate) and the
    H.4.1 timing (the per-release reading of that arm against the carried one). Each carries the pooled, lead, regime and pressure-day-type groups of
    both primary metrics, as #1350 recorded them."""

    spec = {"scarcity_state": (STATE_CARRIED, ANNNET), "h41_timing": (STATE_PERREL, STATE_CARRIED)}
    out: Dict[str, Dict[str, dict]] = {}
    for window in WINDOWS:
        if window not in record_1350["windows"]:
            continue
        groups = record_1350["windows"][window]["groups"]["all"]
        out[window] = {}
        for key, (candidate, reference) in spec.items():
            rows: Dict[str, dict] = {}
            for split in SPLITS:
                for label, group in groups.get(split, {}).items():
                    rows[f"{split}/{label}"] = {"days": group["days"], **{
                        metric: group[metric]["vs"].get(candidate, {}).get(reference) for metric in TESTED if metric in group}}
            out[window][key] = {"with": candidate, "without": reference, "rows": rows}
    return out


def reused_tail(record_1345: Mapping[str, object]) -> dict:
    """What #1345 recorded for the SOFR dispersion forecast as one term of (s3c-ann-net): its window, and for the pooled, lead, regime and
    pressure-day-type groups the nested row of the target (`candidate_mean` is the candidate with the term, `difference` is the candidate less that
    with the term, so a positive `difference` and `skill` favour the term), for both primary metrics."""

    rows: Dict[str, dict] = {}
    for split, labels in record_1345["groups"].items():
        for label, group in labels.items():
            if split == "pooled" and label != "all decision days":
                continue
            rows[f"{split}/{label}"] = {"days": group["days"], **{
                metric: group[metric]["nested"].get(TAIL_TARGET) for metric in TESTED[:2] if metric in group}}
    return {"window": record_1345["window"], "target": TAIL_TARGET, "reading_rule": record_1345["reading_rule"], "rows": rows}


def assemble(args) -> int:
    """Join the per-window scores and the re-used records into `result.json`."""

    declaration = committed_declaration()
    parts = {w: json.loads(Path(args.input_dir, f"result-{w}.json").read_text(encoding="utf-8")) for w in WINDOWS
             if Path(args.input_dir, f"result-{w}.json").exists()}
    if not parts:
        raise SystemExit("no per-window score found: run `score` first")
    shas = {p["panel_sha256"] for p in parts.values()}
    if len(shas) != 1:
        raise SystemExit("the windows were scored on different panels")
    record_1350 = json.loads(RECORD_1350.read_text(encoding="utf-8"))
    record_1345 = json.loads(RECORD_1345.read_text(encoding="utf-8"))
    first = next(iter(parts.values()))
    result = {
        "issue": 1483, "declaration": first["declaration"], "panel_sha256": first["panel_sha256"], "decision_time": first["decision_time"],
        "label": first["label"], "seed": first["seed"], "draws": first["draws"], "reps": first["reps"], "models": first["models"],
        "arms": first["arms"], "rows": first["rows"], "reading_rules": declaration["reading_rules"],
        "windows": {w: p["data"] for w, p in parts.items()}, "against_1321": {w: p["against_1321"] for w, p in parts.items()},
        "reused": {"h41_per_release_1350": reused_rows(record_1350), "h9_nested_1345": reused_tail(record_1345),
                   "panel_sha256_1350": record_1350["panel_sha256"], "panel_sha256_1345": record_1345["panel_sha256"]},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


#: How a row's contrast reads in the family table.
ROW_CONTRAST = {
    "settlement": "candidate against the candidate without both settlement terms (coupon and bill)",
    "settlement_coupon": "candidate against the candidate without the coupon term",
    "settlement_bill": "candidate against the candidate without the bill term",
    "settlement_size": "candidate against (s3c-ann): the settlement flags announced, without the net size",
    "settlement_timing": "(s3c-ann) against (s3c): the settlement flags announced at leads 2 to 5, against read at lead 1 only",
    "iorb": "candidate with the IORB terms against the candidate",
}
ROW_TITLES = {
    "settlement": "both settlement terms (coupon and bill)", "settlement_coupon": "the coupon term alone", "settlement_bill": "the bill term alone",
    "settlement_size": "the settlement size: the net, against the 0/1 flag announced", "settlement_timing": "the settlement timing: announced at leads 2 to 5, "
    "against read at lead 1 only (the flag, both)", "iorb": "the IORB change",
}
FAMILY_ORDER = ("settlement and H.4.1 timing", "the IORB change", "the scarcity state read per leg", "satiation distance", "tail spread")


def pooled(r: Mapping[str, object], window: str) -> Optional[dict]:
    w = r["windows"].get(window)
    return None if w is None else w["groups"]["pooled"]["all decision days"]


def row_cells(r: Mapping[str, object], key: str) -> Dict[str, str]:
    """The row's grid CRPS and twCRPS cells in each window, pooled."""

    _k, _f, with_, without = next(x for x in ROWS if x[0] == key)
    out: Dict[str, str] = {}
    for window in WINDOWS:
        g = pooled(r, window)
        for metric in TESTED[:2]:
            out[f"{window}/{metric}"] = "not run" if g is None else cell(_vs(g, metric, with_, without))
    return out


def tail_cell(row: Optional[Mapping[str, object]]) -> str:
    """#1345's nested row as a cell, in the form of the other rows. The interval is the one #1345 recorded (two-sided 90%, the lower end the one-sided
    95% bound) and the reading is taken from it as here."""

    if not row or row.get("difference") is None:
        return "n/a"
    d = row["difference"]
    if row.get("difference_interval") is None:
        return f"d {d:+.3f}: interval not recorded"
    lo, hi = row["difference_interval"]
    word = "gain" if lo > 0 else "loss" if hi < 0 else "undecided"
    skill = "skill n/a" if row.get("skill") is None or row.get("skill_interval") is None else (
        f"{row['skill']:+.1%} [{row['skill_interval'][0]:+.1%}, {row['skill_interval'][1]:+.1%}]")
    return f"{skill}; d {d:+.3f} [{lo:+.3f}, {hi:+.3f}]: **{word}**"


def reused_cells(r: Mapping[str, object], key: str) -> Dict[str, str]:
    rows = r["reused"]["h41_per_release_1350"]
    out: Dict[str, str] = {}
    for window in WINDOWS:
        entry = rows.get(window, {}).get(key, {}).get("rows", {}).get("pooled/all decision days")
        for metric in TESTED[:2]:
            out[f"{window}/{metric}"] = "not recorded" if not entry or not entry.get(metric) else cell(entry[metric])
    return out


def family_rows(r: Mapping[str, object]) -> List[dict]:
    """The rows of the family table as data: `family`, what the candidate `reads`, the `contrast`, how it was `obtained`, a `short` name for the prose,
    and the `cells` by window and metric (grid CRPS and upper-tail twCRPS, pooled)."""

    rows: List[dict] = []

    def add(family, reads, contrast, how, short, cells):
        rows.append({"family": family, "reads": reads, "contrast": contrast, "how": how, "short": short, "cells": cells})

    reads = "both settlement terms, announced at leads 2 to 5 and sized by the net (USD 100 bn); no H.4.1 series (the scarcity state is held constant)"
    for key in ROW_KEYS:
        if key == "iorb":
            continue
        add("settlement and H.4.1 timing", reads if key == "settlement" else "as above",
            ROW_CONTRAST[key], "scored here", f"settlement ({key.replace('settlement_', '').replace('settlement', 'both terms')})", row_cells(r, key))
    add("settlement and H.4.1 timing", "no H.4.1 series, so dropping its timing leaves the candidate unchanged",
        "(s3c-ann-net x state), H.4.1 per release against carried (the only arm that reads the H.4.1)", "re-used from #1350", "H.4.1 per release",
        reused_cells(r, "h41_timing"))
    add("the IORB change", "no IORB term (IORB enters only through the SRF cap's line)", ROW_CONTRAST["iorb"],
        "scored here", "the IORB terms", row_cells(r, "iorb"))
    add("the scarcity state read per leg", "no state (held at its maximum, so the net terms are plain sizes)",
        "candidate with the state read (carried) against the candidate", "re-used from #1350", "the scarcity state", reused_cells(r, "scarcity_state"))
    add("satiation distance", "nothing", "no input exists on main to add: the estimate is H7's (the liquidity repository), see question 2", "not measured",
        "satiation distance", {f"{w}/{m}": "no row" for w in ("development", "2026") for m in TESTED[:2]})
    tail = r["reused"]["h9_nested_1345"]
    tail_cells = {f"{w}/{m}": "not recorded" for w in ("development", "2026") for m in TESTED[:2]}
    entry = tail["rows"].get("pooled/all decision days", {})
    for metric in TESTED[:2]:
        if entry.get(metric):
            tail_cells[f"development/{metric}"] = tail_cell(entry[metric])
    add("tail spread", "no tail input", f"candidate with the {TAIL_TARGET} forecast as a term against the candidate (#1345, development window only)",
        "re-used from #1345", "the SOFR dispersion forecast", tail_cells)
    return rows


def family_table(r: Mapping[str, object]) -> List[str]:
    """One row per family (and one per sub-row of the first): the candidate with the family against the candidate without it, the grid CRPS and the
    upper-tail twCRPS, on the development window and on the 2026 days."""

    out = ["| family | what the candidate reads | contrast | how obtained | " + " | ".join(
        f"{WINDOW_TITLES[w].split(' (')[0]}: {METRIC_TITLES[m]}" for w in ("development", "2026") for m in TESTED[:2]) + " |",
           "|---|---|---|---|" + "---|" * 4]
    for row in family_rows(r):
        out.append(f"| {row['family']} | {row['reads']} | {row['contrast']} | {row['how']} | " + " | ".join(
            row["cells"][f"{w}/{m}"] for w in ("development", "2026") for m in TESTED[:2]) + " |")
    return out


def word_of(cell_text: str) -> str:
    """`helps`, `hurts` or `undecided` from a cell's reading on the mean-d bound (a cell with no reading is `none`)."""

    for word, name in (("**gain", "helps"), ("**loss", "hurts"), ("**undecided", "undecided")):
        if word in cell_text:
            return name
    return "none"


def reading_lines(r: Mapping[str, object]) -> List[str]:
    """What the table says, generated from it: per window and metric, the rows that help, hurt and are undecided on the mean-d bound."""

    rows = family_rows(r)
    out = ["Generated from the table: on the studentized bound on mean d, the family helps when its lower end is above zero and hurts when its upper end is "
           "below zero. A reading says only that the interval excludes zero; it is not a size, and a pooled "
           "reading is not read without the splits below.", ""]
    for window in ("development", "2026"):
        for metric in TESTED[:2]:
            groups: Dict[str, List[str]] = {"helps": [], "hurts": [], "undecided": [], "none": []}
            for row in rows:
                groups[word_of(row["cells"][f"{window}/{metric}"])].append(row["short"])
            out.append(f"* {WINDOW_TITLES[window].split(' (')[0]}, {METRIC_TITLES[metric]}: helps: " + ("; ".join(groups["helps"]) or "none") + ". hurts: "
                       + ("; ".join(groups["hurts"]) or "none") + ". undecided: " + ("; ".join(groups["undecided"]) or "none") + ". no reading: "
                       + ("; ".join(groups["none"]) or "none") + ".")
    return out + [""]


def split_tables(w: Mapping[str, object], split: str, title: str, with_: str, without: str) -> List[str]:
    table = m1288.split_table(w, split, with_, without)
    return [f"#### {title}: {SHORT[with_]} against {SHORT[without]}", ""] + table + [""] if table else []


def render(r: dict) -> str:
    out = [
        "# Family-by-family ablation on the candidate (s3c-ann-net) (#1483)", "",
        "**Which of the H5 manual's input families help the candidate, one at a time, with intervals?** The first table has one row per family. A positive "
        "skill and a positive mean d say the family helps; the reading is taken from the studentized bound on mean d (her ruling on #1009).", "",
        "**Hypothesis and step:** H5 (primary goal), step 2, milestone H5.M3 (ablation of the new inputs published). **Development data, not a verdict** "
        "(scoring protocol v1, #640). Her ruling of 6 November 2026 (decision docket, relayed): #1354 Directive B (a). **(s3c-ann-net) stays the candidate; "
        "nothing here changes it.** Nothing is registered or published and no claim changes. Generated by `scripts/family_ablation_1483.py page` from "
        f"`docs/research/family-ablation-1483/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        "## The families, one row each", ""] + family_table(r) + [""] + reading_lines(r)
    out += [
        "A family is *dropped* only if the candidate reads it. (s3c-ann-net) reads the settlement family and the calendar columns and nothing else of the five, "
        "so for the other four a drop is the candidate itself, and the contrast is the nested one: the candidate with the family added against the candidate. "
        "That is a choice of this directive, put to her as question 1.", "",
        f"Panel digest `{r['panel_sha256']}`, built at the 18:00 decision instant. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} "
        f"business days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). **Caveat (Lens C, #958):** "
        "the lag-10 HAC standard error that studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it "
        "should be. The intervals of a group of target days keep the **current method** (#1221 questions it and #1228 will decide); no reading of a group is a "
        "finding. Groups of fewer than 20 days are listed and not tested.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n = w["notes"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits.", ""]
        for key, _family, with_, without in ROWS:
            out += [f"### {ROW_TITLES[key][0].upper() + ROW_TITLES[key][1:]}", ""]
            for split, title in (("pooled", "Pooled"), ("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
                out += split_tables(w, split, title, with_, without)
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    out += reused_sections(r)
    out += references_section(r)
    out += question()
    return "\n".join(out).rstrip() + "\n"


def references_section(r: Mapping[str, object]) -> List[str]:
    """The references re-run here against #1321's record: the pooled means agree to rounding (a shown check, not a requirement)."""

    if not r.get("against_1321"):
        return []
    diffs = [abs(v["difference"]) for a in r["against_1321"].values() for ms in a.values() for v in ms.values()]
    return ["## The references against #1321's record", "",
            "(s3), (s3c) and (s3c-ann-net) are re-run here with the machinery and at the instant of #1321's record; the pooled means of all three metrics, in both "
            f"windows, are compared with it. Largest absolute difference of a pooled mean: {max(diffs):.1e}. Shown, not required to agree; no record is edited.", ""]


def reused_sections(r: Mapping[str, object]) -> List[str]:
    out = ["## Rows re-used from merged records", "",
           "Not re-run here. `scripts/family_ablation_1483.py assemble` reads them from the records and `result.json` carries them; the contrast is the one the "
           "record made, on the panel digest of that record.", "",
           f"* **The scarcity state per leg** and **the H.4.1 timing**: `docs/research/h41-per-release-1350/result.json` (#1350), panel `{r['reused']['panel_sha256_1350']}`, "
           "scope all decision days, both windows, with the pooled, lead, regime and pressure-day-type groups. The state arm is (s3c-ann-net) with every term "
           "times the scarcity state and the net settlement times the state (`s3c_announced.ANN_NET_ARM` on the carried states); the H.4.1 contrast is that arm "
           "read per release against carried. #1350 shows the candidate itself is unmoved by the per-release reading, because it reads no H.4.1 series.",
           f"* **The tail spread**: `docs/research/h9-nested-1800-1345/result.json` (#1345), panel `{r['reused']['panel_sha256_1345']}`, the development window only. "
           "It adds the walk-forward forecast of a richer target (here the SOFR dispersion) as one term of the candidate, on the 18:00 instant and direct pairs. "
           "Its test is #1345's (a Diebold-Mariano statistic and a bootstrap interval of mean d, not re-run here), and the target is a dispersion, not the "
           "99th percentile less IORB that the manual's tail spread names: question 3.", ""]
    tail = r["reused"]["h9_nested_1345"]["rows"]
    out += [f"### Development window: (s3c-ann-net) with the {TAIL_TARGET} forecast as a term, against (s3c-ann-net) (#1345)", "",
            "| group | days | " + " | ".join(METRIC_TITLES[m] for m in TESTED[:2]) + " |", "|---|---|" + "---|" * 2]
    for name, entry in tail.items():
        out.append(f"| {name} | {entry['days']} | " + " | ".join(tail_cell(entry.get(m)) for m in TESTED[:2]) + " |")
    out.append("")
    for window in WINDOWS:
        rows = r["reused"]["h41_per_release_1350"].get(window)
        if not rows:
            continue
        for key, title in (("scarcity_state", "scarcity state read (carried) against (s3c-ann-net)"),
                           ("h41_timing", "(s3c-ann-net x state), H.4.1 per release against carried")):
            out += [f"### {WINDOW_TITLES[window].split(' (')[0]}: {title} (#1350)", "",
                    "| group | days | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|---|" + "---|" * len(TESTED)]
            for name, entry in rows[key]["rows"].items():
                out.append(f"| {name} | {entry['days']} | " + " | ".join(cell(entry.get(m)) for m in TESTED) + " |")
            out.append("")
    return out


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. What is a family drop when the candidate does not read the family?** (s3c-ann-net) reads only the settlement family of the manual's five. "
        "Dropping any other is the candidate, so the table scores the family *added* to the candidate for those, and the settlement family dropped. Options (the "
        "default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Drop where read, add where not** (default; this page). H5.M3 is marked on the merge, on these rows.",
        "2. **Rebuild the ablation on the full model each family belongs to.** Start from an arm that reads every family (the candidate with the IORB terms, the "
        "state, a satiation distance and a tail input all at once) and drop each in turn. It needs the satiation distance (question 2) and is a new arm of "
        "the search, so it is a directive of its own.",
        "3. **Do not mark H5.M3 on this page.** Keep the rows as evidence and mark when the satiation row exists.", "",
        "**Question 2. Satiation distance.** No input on main carries it as a daily as-of series: `satiation.fit_level` fits the kink at a refit and H7's estimator "
        "is in the liquidity repository, gating the nested test here. Options: (1) **leave the row as `not measured`** until H7's estimate exists (default); "
        "(2) add the scarcity state's band distance (`scarcity.reserves_ratio` less the 0.12 band) as a term here, which the state arm of #1350 already reads "
        "through the state; (3) a directive that builds the rolling satiation column (`satiation.ROLLING_COLUMN`) as an input to the candidate.", "",
        "**Question 3. Tail spread.** The H5 manual's tail spread has no arm on the candidate except #1345's dispersion forecasts, which are not the tail "
        "of the SOFR distribution (the 99th percentile less IORB). Options: (1) **re-use #1345's row, as here** (default); (2) a directive for the "
        "99th-percentile-less-IORB forecast as a term, on the protocol's test; (3) drop the family from the manual's step 2.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the candidate and the arms on one window, cap them as (s3c) is capped, and score")
    s.add_argument("--panel", required=True)
    s.add_argument("--window", required=True, choices=list(WINDOWS))
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized intervals")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    a = sub.add_parser("assemble", help="join the per-window scores and the re-used records into result.json")
    a.add_argument("--input-dir", default=str(REPO / "docs" / "research" / "family-ablation-1483"))
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
