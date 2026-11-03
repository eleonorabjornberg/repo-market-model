#!/usr/bin/env python3
"""H9 step 3, the nested test on (s3c-ann-net) at the 18:00 decision instant (#1345; her ruling of 1 November 2026, ledger item 96): walks, scoring and page.

A development study, never a verdict (scoring protocol v1, #640). It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/h9_nested_1800_1345.json`, which this script refuses to read unless it is committed and unchanged.

It re-asks #842's and #932's question, H9's kill clause "no nested gain for H5", of H5's candidate as it now stands: does (s3c-ann-net) improve when it also
reads a forecast of one of the richer targets (BGCR dispersion, ON RRP daily change, SOFR dispersion)? Three things differ from #932:

* **The base** is (s3c-ann-net) (`repo_model.s3c_announced.ANN_NET_ARM`, capped as (s3c), `repo_model.s3c_candidate`), walked as #1288 and #1321 walk it, not `gbm_funding`.
  A plus arm is the same arm with one extra term, the target's lead-h median (`repo_model.s3c_h9`, `spread_mr_state_calendar.H9_FORECAST`), on direct pairs.
* **The instant** is 18:00 (`repo_model.decision_instant`), pinned explicitly for every module of the chain (`decision_instant_pinned`, as #1321's), the
  study family's and the H9 chain's (#634, #639, #706 type their own `time(16, 0)`). #1333 found that 18:00 changes nothing for (s3c-ann-net); the
  targets read series published between 16:00 and 18:00, so the **target walks are redone at 18:00** (`target-walk`), on the scratch panel built at 18:00.
* **The panel** is the published one (`PUB1800.csv`, digest `4ddc3882...`, byte-identical at either instant) for the base; the scratch panel `H9D1800.csv`
  (`0967f5c0...`) differs from the 16:00 one (`26c51093...`) in the satiation-distance column, which reads H.4.1 releases that are public between 16:00 and
  18:00 on Thursdays (`satiation_distance_598.py` reads `RMM_DECISION_TIME`). The target walks are walked on it.

Commands, from a clone of the branch. The panels are built in the cloud and shipped (finding #1309: the scratch panel's libm digest differs on macOS); the
fifteen target walks are the long part (see `needs-mac:` on the pull request); the scoring is minutes to tens of minutes.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB1800.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/satiation_distance_598.py panel --panel AUG2.csv --output AUG2D1800.csv
    PYTHONPATH=src python3 scripts/richer_targets_639.py panel --panel AUG2D1800.csv --output H9D1800.csv
    for T in bgcr_dispersion_bps on_rrp_change_bn sofr_dispersion_bps: for h in 1 2 3 4 5:
        PYTHONPATH=src python3 scripts/h9_nested_1800_1345.py target-walk --target $T --horizon $h --panel H9D1800.csv --output TW/${T}_h$h.json
    PYTHONPATH=src python3 scripts/h9_nested_1800_1345.py score --panel PUB1800.csv --scratch H9D1800.csv --target-walks TW --output OUT/result.json
    PYTHONPATH=src python3 scripts/h9_nested_1800_1345.py page --score OUT/result.json --output docs/research/h9-nested-1800-1345-result.md

`target-walk` is #706's walk (`richer_targets_706.walk_command`: candidate (b) of #634 on the target, direct pairs under #932's amendment) at 18:00; a walk whose
output already holds the same target, lead, panel and instant is skipped, so a stopped run resumes. `score` reads the walks that exist: a target with all
five leads is scored; one with fewer is refused unless `--allow-partial` (a smoke run), which records the leads it had.
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import hashlib
import importlib.util
import json
import multiprocessing
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


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


from repo_model import announced_iorb, metrics, policy_events, s3c_announced, s3c_h9, s3c_net, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_state_calendar as sc, target_forecasts as tf  # noqa: E402
from repo_model.asof import fold_grid, refit_blocks  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.decision_instant import DECISION_TIME, LEGACY_DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

#: #1321's script (and through it #1288's, #1273's, #1255's), and #842's (and through it #634's, #706's, #639's), each under an alias of its own.
m1321 = _load("s3c_flagnet_gross_1321", "s3c_flagnet_gross_1321_in_1345")
m842 = _load("h9_nested_842", "h9_nested_842_in_1345")
m1288, m1255, k, c = m1321.m1288, m1321.m1255, m1321.k, m1321.c
m706, m634 = m842.m706, m842.m634
s639 = m706.s639
s761, s686, m1273 = m1321.s761, m1321.s686, m1321.m1273

DECLARATION = REPO / "metadata" / "h9_nested_1800_1345.json"
SEED = 1345
TARGETS = tf.TARGETS
LEADS = tuple(sp.HORIZONS)
GRID = sp.GRID
LAST_TARGET = m842.LAST_TARGET
EXCLUDED_DAY = m842.EXCLUDED_DAY
WINDOW = "development"
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
BASE = m1321.ANNNET
S3C = m1321.S3C
PLUS = {t: f"{BASE}+{t}" for t in TARGETS}
MODELS = (S3C, BASE) + tuple(PLUS.values())
TESTED = ("grid_crps", "upper_tail_twcrps")
METRIC_NAMES = m1321.METRIC_NAMES
MIN_GROUP_DAYS = m1321.MIN_GROUP_DAYS
INSTANT_TEXT = DECISION_TIME.isoformat(timespec="minutes")
LABELS = {S3C: "(s3c)", BASE: "(s3c-ann-net)", **{PLUS[t]: f"(s3c-ann-net) + {t}" for t in TARGETS}}
TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)"}
EXCLUDED_LABEL = f"excluding {EXCLUDED_DAY.isoformat()}"

def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return m1321.committed_declaration(path)


# -- the instant -----------------------------------------------------------------------------------------------------------


def chain_modules() -> list:
    """Every module of `scripts/` the study reaches: those #1321 loads and those #842 loads, and through their module-level names, theirs."""

    seen, queue = [], [m1321, m842]
    while queue:
        module = queue.pop()
        if any(module is x for x in seen):
            continue
        seen.append(module)
        for value in list(vars(module).values()):
            path = getattr(value, "__file__", None)
            if isinstance(value, type(sys)) and path and Path(path).parent == REPO / "scripts":
                queue.append(value)
    return seen


@contextlib.contextmanager
def instant_pinned():
    """Run the whole chain at the decision instant of `repo_model.decision_instant` (18:00) for the length of the block.

    The family of #1115 to #1321 holds its 16:00 as `DECISION_TIME` (#1321's `decision_instant_pinned` sets those); the H9 chain of #634, #639, #706 and #842
    types it once more each, as `DECISION` or `DECISION_TIME`. This sets every such constant, in every loaded module of `scripts/` that holds the legacy 16:00,
    to the declared instant, and puts it back on exit, so that nothing else in the process (another study's tests) sees the change.

    Raises:
        ValueError: a module the walks read still holds another instant inside the block.
    """

    held = []
    with m1321.decision_instant_pinned():
        for module in chain_modules():
            for name in ("DECISION", "DECISION_TIME"):
                if getattr(module, name, None) == LEGACY_DECISION_TIME:
                    held.append((module, name))
                    setattr(module, name, DECISION_TIME)
        try:
            for label, value in (("spread_distribution_634.DECISION", m634.DECISION), ("richer_targets_706.DECISION", m706.DECISION),
                                 ("richer_targets_639.DECISION_TIME", s639.DECISION_TIME), ("h9_nested_842.DECISION", m842.DECISION)):
                if value != DECISION_TIME:
                    raise ValueError(f"{label} is {value}, not the declared instant {DECISION_TIME}")
            yield DECISION_TIME
        finally:
            for module, name in held:
                setattr(module, name, LEGACY_DECISION_TIME)


# -- the target walks ------------------------------------------------------------------------------------------------------


def target_walk_command(args) -> int:
    """#706's walk of one target at one lead, at 18:00, on the 18:00 scratch panel."""

    declared = committed_declaration()
    declared_706 = m706.committed_declaration()
    target, h = args.target, args.horizon
    if target not in declared["targets"]["chosen"]:
        raise SystemExit(f"{target!r} is not a declared target")
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    require_unlocked([LAST_TARGET], where="h9_nested_1800_1345")
    digest = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    if digest != declared["panels"]["scratch_1800_sha256"]:
        raise SystemExit(f"the scratch panel's digest {digest} is not the declared {declared['panels']['scratch_1800_sha256']}")
    if finished_target_walk(args.output, target, h, digest):
        print(json.dumps({"target": target, "horizon": h, "skipped": "finished walk at " + str(args.output)}))
        return 0
    with instant_pinned():
        sd = m634._load("satiation_distance_598")
        registry = sd.measurement_fields.load_registry()
        panel = m706.panel_rows(args.panel, target)
        timed_rows, timed_registry = sd.ann.arm_inputs("both", panel, registry, h)
        features = m634.new_features(h)
        fit = m706.target_fitter(features)
        model = declared_706["model"]
        with sd.switched_on(), sd.h41_release.release_dating(), m706.scarcity.own_leg_composition(), m706.richer_targets.swap_target_fields(target):
            rows = m706.richer_targets.as_target(timed_rows, target)
            result, levels, settings = m634.walk(
                rows, fit=fit, features=features, online_calibration=None, registry=timed_registry, horizon=h,
                minimum_history=model["minimum_history"], refit_every=model["refit_every"], expected_levels=GRID,
            )
    m706.check_pairing(settings)
    document = {
        "target": target, "horizon": h, "levels": levels, "panel_sha256": digest, "decision_time": INSTANT_TEXT,
        "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(), "features": list(features),
        "settings": json.loads(json.dumps(settings, default=str)), "laws": {rows[i].date.isoformat(): q for i, q in result},
    }
    partial = args.output.with_name(args.output.name + ".partial")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    partial.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(json.dumps({"target": target, "horizon": h, "days": len(document["laws"])}))
    return 0


def finished_target_walk(output: Path, target: str, horizon: int, digest: str) -> bool:
    """Whether `output` already holds this walk: the same target and lead, from the same scratch panel bytes, at 18:00, under this declaration."""

    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (
        isinstance(document, dict) and isinstance(document.get("laws"), dict) and document.get("target") == target
        and document.get("horizon") == horizon and document.get("panel_sha256") == digest and document.get("decision_time") == INSTANT_TEXT
        and document.get("declaration_sha256") == hashlib.sha256(DECLARATION.read_bytes()).hexdigest()
    )


def check_target_walk(document: Mapping, target: str, horizon: int, digest: str) -> None:
    """A target walk is read only if it is this target's and lead's, walked at 18:00 on the declared scratch panel on direct pairs.

    Raises:
        ValueError: it is another walk, was made at another instant, on another panel, under another declaration, or not on direct pairs.
    """

    if document.get("target") != target or document.get("horizon") != horizon:
        raise ValueError(f"not the walk of {target} at lead {horizon}")
    if document.get("decision_time") != INSTANT_TEXT:
        raise ValueError(f"the walk of {target} at lead {horizon} was made at {document.get('decision_time')}, not {INSTANT_TEXT}")
    if document.get("panel_sha256") != digest:
        raise ValueError(f"the walk of {target} at lead {horizon} was not walked on the declared scratch panel")
    if document.get("declaration_sha256") != hashlib.sha256(DECLARATION.read_bytes()).hexdigest():
        raise ValueError(f"the walk of {target} at lead {horizon} was walked under another declaration")
    if list(document["levels"]) != list(GRID):
        raise ValueError(f"the walk of {target} at lead {horizon} is not on the protocol's grid")
    m706.check_pairing(_settings(document))


def _settings(document: Mapping) -> Mapping:
    settings = document.get("settings", {})
    if isinstance(settings, str):
        import ast

        settings = ast.literal_eval(settings)
    if not isinstance(settings, Mapping):
        raise ValueError(f"the walk's settings are not a mapping: {settings!r}")
    return settings


def target_tables(walks: Path, scratch: Path, panel_dates: Sequence[date], *, allow_partial: bool) -> Tuple[Dict[str, s3c_h9.TargetForecastTable], dict]:
    """One `TargetForecastTable` per target from its walks, and what was read.

    The decision day of a law is the panel day `lead` rows before its target day, on the target's own panel; the fit that made it is rebuilt from the fold
    grid and refit blocks the walk used (`target_forecasts.fit_decision_dates`), and the published panel must give the same calendar.

    Raises:
        ValueError: a target with fewer than five leads without `allow_partial`, a walk that is not the declared one, or two calendars that disagree.
    """

    declared_706 = m706.committed_declaration()
    digest = hashlib.sha256(scratch.read_bytes()).hexdigest()
    tables: Dict[str, s3c_h9.TargetForecastTable] = {}
    read: dict = {}
    for target in TARGETS:
        medians: Dict[int, Dict[date, Optional[float]]] = {}
        fits: Dict[int, Dict[date, date]] = {}
        for h in LEADS:
            path = walks / f"{target}_h{h}.json"
            if not path.exists():
                continue
            document = json.loads(path.read_text(encoding="utf-8"))
            check_target_walk(document, target, h, digest)
            forecasts, fit_days = m842.decision_forecasts(document, target, h, scratch, declared_706)
            medians[h] = {day: None if law is None else tf.median_of(law) for day, law in forecasts.items()}
            fits[h] = fit_days
            position = {d: i for i, d in enumerate(panel_dates)}
            for day in medians[h]:
                if day not in position:
                    raise ValueError(f"{target} lead {h}: the walk's decision day {day} is not a day of the published panel")
        if len(medians) < len(LEADS) and not allow_partial:
            raise ValueError(f"{target}: leads {sorted(set(LEADS) - set(medians))} have no walk in {walks} (--allow-partial is for a smoke run)")
        if medians:
            tables[target] = s3c_h9.TargetForecastTable(panel_dates, medians, fits, unit=s3c_h9.UNITS[target])
        read[target] = {"leads": sorted(medians), "forecasts": {str(h): sum(1 for v in found.values() if v is not None) for h, found in medians.items()}}
    return tables, read


# -- the walks and the frame ----------------------------------------------------------------------------------------------


def plus_arm(target: str) -> sc.StateArm:
    """(s3c-ann-net)'s arm with the target's forecast as one extra term."""

    return dataclasses.replace(
        s3c_announced.ANN_NET_ARM, name=f"sc_s3_ann_net_h9_{target}",
        role=f"(s3-ann-net) with the lead-h median of {target}'s walk as a centred extra term", extra=(sc.H9_FORECAST,),
    )


def walks_of(frame, panel, splits, registry, table, results, auctions, first: Optional[date], window: str, tables: Mapping[str, s3c_h9.TargetForecastTable]):
    """The walk of (s3c-ann-net) and of each plus arm over #1255's decision days, on the same tables.

    Raises:
        ValueError: an arm has no forecast on a scored decision day.
    """

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    walks = {BASE: sc.walk(panel, days, term_table, states, (s3c_announced.ANN_NET_ARM,), sizes=net_table, **settings)}
    arms = {BASE: s3c_announced.ANN_NET_ARM.name}
    for target, h9 in tables.items():
        arm = plus_arm(target)
        walks[PLUS[target]] = sc.walk(panel, days, term_table, states, (arm,), sizes=net_table, iorb=h9, **settings)
        arms[PLUS[target]] = arm.name
    for model, walk in walks.items():
        for d in frame.days:
            if d not in walk.forecasts[arms[model]]:
                raise ValueError(f"the walk of {model} has no forecast on the scored decision day {d}")
    return walks, arms


def build(window, panel, splits, registry, table, register, results, auctions, first, tables):
    """#1255's frame with (s3c-ann-net) and the plus arms added: `(frame, notes, walks, arms, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walks, arms = walks_of(frame, panel, splits, registry, table, results, auctions, first, window, tables)
    forecasts = {S3C: frame.forecasts[S3C]}
    for model, walk in walks.items():
        found = {d: walk.forecasts[arms[model]][d] for d in frame.days}
        forecasts[model] = m1255.s3c_forecasts(frame, register, found)
    present = [m for m in MODELS if m in forecasts]
    frame.forecasts = {m: {d: forecasts[m][d] for d in frame.days} for m in present}
    notes = dict(notes, refits={m: len(w.fits) for m, w in walks.items()})
    return frame, notes, walks, arms, groups_fn, present


def term_in_fit(walk, arm: str, frame) -> dict:
    """The share of scored (decision day, lead) cells whose refit had the forecast in the fit, and its mean effect in bp per unit, by lead."""

    out = {}
    for h in LEADS:
        inside, effects = 0, []
        for d in frame.days:
            estimate = walk.estimates[walk.fit_used[d]][arm][h]
            if sc.H9_FORECAST in estimate.effect:
                inside += 1
                effects.append(estimate.effect[sc.H9_FORECAST] * float(walk.detail[d]["scale"]))
        out[str(h)] = {"share_in_fit": inside / len(frame.days), "mean_effect_bp_per_unit": (sum(effects) / len(effects)) if effects else None}
    return out


# -- the groups and the tests ---------------------------------------------------------------------------------------------

_STATE: Dict = {}


def nested_task(job):
    split, label, grain, metric, target, members = job
    series = _STATE["series"][(grain, metric)]
    plus, base = PLUS[target], BASE
    days = list(members)
    if all(series[plus][d] == series[base][d] for d in days):
        return (split, label, metric, target), {"identical": True, "days": len(days)}
    out = s761.run_pairs({base: series[base]}, series[plus], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[base]
    return (split, label, metric, target), out


def run_jobs(jobs, workers: int):
    if workers <= 1:
        return [nested_task(j) for j in jobs]
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(nested_task, jobs, chunksize=1)


def holm(p_values: Sequence[float]) -> List[float]:
    return m842.holm(p_values)


def reading(row: Optional[Mapping]) -> str:
    """#842's and #932's reading of a target on the pooled primary score: improves only if the one-sided 95% lower bound of mean(d) is above zero."""

    if row is None or "identical" in row:
        return "identical forecasts" if row else "not tested"
    interval = row.get("difference_interval")
    if interval is None:
        return "undefined"
    return "improves the candidate" if interval[0] > 0 else "no improvement beyond its interval"


def score_command(args) -> int:
    with instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    require_unlocked([LAST_TARGET], where="h9_nested_1800_1345")
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    if published_sha != declaration["panels"]["published_sha256"]:
        raise SystemExit(f"the published panel's digest {published_sha} is not the declared {declaration['panels']['published_sha256']}")
    scratch_sha = hashlib.sha256(Path(args.scratch).read_bytes()).hexdigest()
    if scratch_sha != declaration["panels"]["scratch_1800_sha256"]:
        raise SystemExit(f"the scratch panel's digest {scratch_sha} is not the declared {declaration['panels']['scratch_1800_sha256']}")
    panel = [row for row in load_daily_panel(panel_path) if row.date <= EXPLORATORY_END]
    require_exploratory_window([row.date for row in panel], where="scripts/h9_nested_1800_1345")
    tables, read = target_tables(Path(args.target_walks), Path(args.scratch), [row.date for row in panel], allow_partial=args.allow_partial)
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = m1321.cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    frame, notes, walks, arms, groups_fn, present = build(WINDOW, panel, splits, registry, table, register, results, auctions, args.first, tables)
    last = m1288.WINDOW_LAST[WINDOW]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in present}
    for m in present:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in SPLITS]
    # #798: every headline with and without decision day 2019-09-18; a split group that holds it is also read without it
    extra = [("pooled", EXCLUDED_LABEL, "decision", [d for d in frame.days if d != EXCLUDED_DAY])]
    for split, label, grain, members in groups:
        if grain in ("decision", "lead1", "lead2", "lead3", "lead4", "lead5") and EXCLUDED_DAY in members and (split, label) != ("pooled", "all decision days"):
            extra.append((split, f"{label} ({EXCLUDED_LABEL})", grain, [d for d in members if d != EXCLUDED_DAY]))
    groups = groups + extra
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in present}
    _STATE.update(series=series, draws=args.draws)
    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in TESTED:
            for target in tables:
                jobs.append((split, label, grain, metric, target, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {
        "issue": 1345, "declaration": str(DECLARATION.relative_to(REPO)), "label": "development, not a verdict", "seed": SEED, "draws": args.draws,
        "decision_time": INSTANT_TEXT, "window": WINDOW, "panel_sha256": published_sha, "scratch_panel_sha256": scratch_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "smoke": bool(args.allow_partial or args.first is not None),
        "models": list(present), "targets": list(tables), "target_walks": read, "notes": notes,
        "pressure_day_type_counts": {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))},
        "skipped_groups": skipped, "groups": {}, "in_fit": {PLUS[t]: term_in_fit(walks[PLUS[t]], arms[PLUS[t]], frame) for t in tables},
        "reading_rule": declaration["reading_rule"],
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in present}, "nested": {}}
    for (split, label, metric, target), payload in done:
        result["groups"][split][label][metric]["nested"][target] = payload
    result["holm"] = holm_block(result)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def holm_block(result: Mapping) -> dict:
    """Holm across the targets tested on the pooled primary score, with and without 2019-09-18, on the Diebold-Mariano p-value the row carries."""

    out = {}
    for label in ("all decision days", EXCLUDED_LABEL):
        row = result["groups"].get("pooled", {}).get(label, {}).get("grid_crps", {}).get("nested", {})
        targets = [t for t in TARGETS if t in row and "dm_p_value" in row[t] and row[t]["dm_p_value"] is not None]
        if targets:
            adjusted = holm([row[t]["dm_p_value"] for t in targets])
            out[label] = {t: {"p": row[t]["dm_p_value"], "holm_p": a} for t, a in zip(targets, adjusted)}
    return out


# -- the page --------------------------------------------------------------------------------------------------------------


def cell(row: Optional[Mapping]) -> str:
    if row is None:
        return "n/a"
    if "identical" in row:
        return "identical forecasts"
    if "difference" not in row:
        return "undefined"
    text = f"{row['difference']:+.4f}"
    if row.get("difference_interval"):
        text += f" [{row['difference_interval'][0]:+.4f}]"
    if row.get("skill") is not None:
        text += f", skill {row['skill']:+.3f}"
    return text


def page(args) -> int:
    doc = json.loads(Path(args.score).read_text(encoding="utf-8"))
    out = [
        f"# H9 step 3: the nested test on (s3c-ann-net), made at {doc['decision_time']} (#1345)", "",
        "**Development data, not a verdict** (scoring protocol v1). H9's kill clause is not read here; reading it is Eleonora's."
        + (" **This is a smoke run on a slice, not the study.**" if doc["smoke"] else ""), "",
        f"- Window: development (targets to {LAST_TARGET.isoformat()}); decision instant {doc['decision_time']}; seed {doc['seed']}.",
        f"- Published panel `{doc['panel_sha256'][:8]}...`; scratch panel (18:00) `{doc['scratch_panel_sha256'][:8]}...`.",
        "- d = S(base) - S(base + target); positive favours the target's forecast. Cells: mean d [one-sided 95% lower bound], skill.", "",
    ]
    for label in ("all decision days", EXCLUDED_LABEL):
        group = doc["groups"]["pooled"].get(label)
        if group is None:
            continue
        out += [f"## Pooled, {label} ({group['days']} decision days)", "", "| target | " + " | ".join(TITLES[m] for m in TESTED) + " | reading (grid CRPS) |",
                "|---|" + "---|" * (len(TESTED) + 1)]
        for target in doc["targets"]:
            rows = [group[m]["nested"].get(target) for m in TESTED]
            out.append(f"| {target} | " + " | ".join(cell(r) for r in rows) + f" | {reading(rows[0])} |")
        out.append("")
    if doc["holm"]:
        out += ["## Holm across the targets (pooled, grid CRPS)", "", "| group | target | p | Holm p |", "|---|---|---|---|"]
        for label, rows in doc["holm"].items():
            out += [f"| {label} | {t} | {v['p']:.3f} | {v['holm_p']:.3f} |" for t, v in rows.items()]
        out.append("")
    for split in ("lead", "regime", "pressure_day_type"):
        groups = doc["groups"].get(split, {})
        if not groups:
            continue
        out += [f"## By {split.replace('_', ' ')} (grid CRPS)", "", "| group | days | " + " | ".join(doc["targets"]) + " |", "|---|---|" + "---|" * len(doc["targets"])]
        for label in sorted(groups):
            nested = groups[label]["grid_crps"]["nested"]
            out.append(f"| {label} | {groups[label]['days']} | " + " | ".join(cell(nested.get(t)) for t in doc["targets"]) + " |")
        out.append("")
    out += ["## The forecast in the fit", "", "| arm | lead | share of cells with the term in the fit | mean effect (bp per unit) |", "|---|---|---|---|"]
    for arm, leads in doc["in_fit"].items():
        for h, v in sorted(leads.items()):
            eff = "n/a" if v["mean_effect_bp_per_unit"] is None else f"{v['mean_effect_bp_per_unit']:+.4f}"
            out.append(f"| {LABELS[arm]} | {h} | {v['share_in_fit']:.3f} | {eff} |")
    out += ["", "## Target walks read", "", "```json", json.dumps(doc["target_walks"], indent=1, sort_keys=True), "```", ""]
    Path(args.output).write_text("\n".join(out), encoding="utf-8")
    return 0


# -- the command line ------------------------------------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    w = commands.add_parser("target-walk", help="#706's walk of one target at one lead, at 18:00")
    w.add_argument("--target", required=True)
    w.add_argument("--horizon", type=int, required=True)
    w.add_argument("--panel", type=Path, required=True)
    w.add_argument("--output", type=Path, required=True)
    s = commands.add_parser("score", help="walk (s3c-ann-net) and its plus arms, score the nested differences")
    s.add_argument("--panel", type=Path, required=True)
    s.add_argument("--scratch", type=Path, required=True)
    s.add_argument("--target-walks", type=Path, required=True)
    s.add_argument("--output", type=Path, required=True)
    s.add_argument("--first", type=date.fromisoformat, default=None, help="score the decision days from this day only (a smoke slice)")
    s.add_argument("--allow-partial", action="store_true", help="read the target leads that exist (a smoke run)")
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--workers", type=int, default=4)
    p = commands.add_parser("page", help="the result page from a score")
    p.add_argument("--score", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return {"target-walk": target_walk_command, "score": score_command, "page": page}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
