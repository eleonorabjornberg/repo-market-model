"""(s3c-ann-net-bill): one arm on the candidate (s3c-ann-net), reading the 4-week bill rate less IORB of the previous business day, made at the
18:00 decision instant (#1346; H5 step 3; her ruling of 1 November 2026, ledger item 97).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_bill_iorb_1346.json`, which this script refuses to read unless it is committed and unchanged. The arm is
`repo_model.s3c_bill_iorb.BILL_ARM`: (s3c-ann-net) (`repo_model.s3c_announced.ANN_NET_ARM`) with one extra term, the bill rate less IORB of the
previous business day in units of 10 bp, capped as (s3c) is capped (`repo_model.s3c_candidate`, unchanged). The references (s3c) and
(s3c-ann-net) are re-run in the same walk, at 18:00 (`repo_model.decision_instant`); nothing of #1321's record is edited, and its pooled means
for the references are shown beside the re-run ones as a check that the walk is the same. The frames and the machinery are #1255's, #1273's, #1288's
and #1321's and are loaded as they are: the development window of #1145 and #1241 (targets up to 2025-12-31) and the 2026 development days of #1229
(targets 2026-01-02 to 2026-09-03, the near-blind tier open since GO #151). The blind tier and every lockbox day are refused by the frames' own
guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009
ruling) with the skill interval beside, split by lead, regime and pressure-day type; reports the coverage of the central 90% band; and reports the
fitted effect of the new term by lead and regime and the range of the term.

Commands, from a clone of the branch (the walks are minutes, the paired tests the longer part; a cloud run unless the measured time says
otherwise):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_bill_iorb_1346.py score --panel PUB.csv \\
        --output docs/research/s3c-bill-iorb-1346/result.json
    PYTHONPATH=src python3 scripts/s3c_bill_iorb_1346.py page \\
        --score docs/research/s3c-bill-iorb-1346/result.json --output docs/research/s3c-bill-iorb-1346-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import math
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


from repo_model import announced_iorb, metrics, policy_events, s3c_announced, s3c_bill_iorb, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.decision_instant import DECISION_TIME, LEGACY_DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1288's script (and through it #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker
#: pool's tasks does not meet another test module's copy.
m1288 = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1346")
m1273, m1255, k, c, s686, s761 = m1288.m1273, m1288.m1255, m1288.k, m1288.c, m1288.s686, m1288.s761
load_daily_panel = m1288.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_bill_iorb_1346.json"
RECORD_1321 = REPO / "docs" / "research" / "s3c-flagnet-gross-1321" / "result.json"
SEED = 1346
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3, S3C, ANNNET = m1288.S3, m1288.S3C, m1288.ANNNET
BILL = "sc_s3c_ann_net_bill"
ARMS = (BILL,)
REFERENCES = (ANNNET, S3C)
MODELS = (S3, S3C, ANNNET, BILL)
LABELS = {S3: "(s3)", S3C: "(s3c)", ANNNET: "(s3c-ann-net), the candidate", BILL: "(s3c-ann-net-bill)"}
SHORT = {S3: "(s3)", S3C: "(s3c)", ANNNET: "(s3c-ann-net)", BILL: "(s3c-ann-net-bill)"}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
EPSILON = 1e-9
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
#: The effect table prints the pooled row at every lead and the regime rows at this lead only; the record holds them all.
REGIME_LEAD = "3"
REPS = 2000


def chain_modules() -> list:
    """Every module of `scripts/` this study reaches: those #1288 loads and, through their module-level names, those they load, each object once
    (a module loaded twice under two aliases is two objects, and the walks read the one their own module holds)."""

    seen, queue = [], [m1288]
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
def decision_instant_pinned():
    """Run the study modules of #1115 to #1288 at the decision instant of `repo_model.decision_instant` (18:00), for the length of the block.

    Those scripts type the 16:00 of the published records once, in `spread_mean_reversion_686.DECISION_TIME`, and every other copies it as a module
    constant (`DECISION_TIME = c.DECISION_TIME`) that its frame builders and walks read when they run. This sets each such constant, in every
    loaded module of `scripts/` that holds the legacy 16:00, to the declared instant, and puts it back on exit, so that nothing else in the
    process (another study's tests) sees the change. The records of those studies stay what they were: made at 16:00.

    Raises:
        ValueError: a module the walks read still holds another instant inside the block.
    """

    held = []
    for module in chain_modules():
        if getattr(module, "DECISION_TIME", None) == LEGACY_DECISION_TIME:
            held.append(module)
            module.DECISION_TIME = DECISION_TIME
    try:
        for name, value in (("k", k.DECISION_TIME), ("c", c.DECISION_TIME), ("s686", s686.DECISION_TIME)):
            if value != DECISION_TIME:
                raise ValueError(f"{name}.DECISION_TIME is {value}, not the declared instant {DECISION_TIME}")
        yield DECISION_TIME
    finally:
        for module in held:
            module.DECISION_TIME = LEGACY_DECISION_TIME


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What the arm is tested against: the candidate (s3c-ann-net) and (s3c)."""

    return list(REFERENCES) if candidate in ARMS else []


# -- the walk and the frame ----------------------------------------------------------------------------------------------


def walk_of(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """One walk of (s3c-ann-net) and the arm over #1255's decision days, with the tables they read.

    Raises:
        ValueError: a scored decision day has no forecast of (s3c-ann-net) or of the arm.
    """

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    bill_table = s3c_bill_iorb.BillLessIorbTable(panel)
    walk = sc.walk(panel, days, term_table, states, (s3c_announced.ANN_NET_ARM, s3c_bill_iorb.BILL_ARM), sizes=net_table, iorb=bill_table,
                   **settings)
    for name in (s3c_announced.ANN_NET_ARM.name, s3c_bill_iorb.BILL_ARM.name):
        for d in frame.days:
            if d not in walk.forecasts[name]:
                raise ValueError(f"the walk has no forecast of {name} on the scored decision day {d}")
    return walk, bill_table


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with (s3c-ann-net) and the arm added: `(frame, notes, walk, bill_table, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk, bill_table = walk_of(window, frame, panel, splits, registry, results, auctions, first)
    raw = {
        ANNNET: {d: walk.forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in frame.days},
        BILL: {d: walk.forecasts[s3c_bill_iorb.BILL_ARM.name][d] for d in frame.days},
    }
    forecasts = {S3: frame.forecasts[S3], S3C: frame.forecasts[S3C]}
    for name, found in raw.items():
        forecasts[name] = m1255.s3c_forecasts(frame, register, found)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    notes = dict(notes, refits=len(walk.fits))
    return frame, notes, walk, bill_table, groups_fn


# -- the term and its fitted effect --------------------------------------------------------------------------------------


def term_range(frame, bill_table) -> dict:
    """The minimum, maximum, mean and standard deviation of the term over the scored decision days (one figure per day, as every lead reads the
    same one), in units of 10 bp and in bp, and the share of days it is above zero."""

    values = [bill_table.read(1, frame.position[d])[sc.BILL_LESS_IORB] for d in frame.days]
    n = len(values)
    mean = sum(values) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / n)
    return {"days": n, "min": min(values), "max": max(values), "mean": mean, "sd": sd, "unit_bp": s3c_bill_iorb.UNIT_BPS,
            "share_positive": sum(1 for v in values if v > 0.0) / n}


def effects(frame, walk, lead: int, bill_table, *, reps: int = REPS) -> Dict[str, dict]:
    """The fitted effect of the term in bp per 10 bp of the gap at `lead`, by regime of the target day and pooled.

    For each decision day the effect is that of the refit the forecast used at `lead` times the anchor's scale in bp (0 where the term was not in
    the fit, counted); the shift is that effect times the term's value for the day, and the mean absolute shift is reported. Each mean carries the
    90% stationary-bootstrap interval over decision days (an interval over days that share refits, not a sampling interval for a coefficient).
    """

    name = s3c_bill_iorb.BILL_ARM.name
    per_day: Dict[date, dict] = {}
    for d in frame.days:
        estimate = walk.estimates[walk.fit_used[d]][name][lead]
        scale = float(walk.detail[d]["scale"])
        value = bill_table.read(lead, frame.position[d])[sc.BILL_LESS_IORB]
        effect = estimate.effect.get(sc.BILL_LESS_IORB, 0.0) * scale
        per_day[d] = {"regime": frame.regime(frame.target(d, lead)), "effect": effect, "in_fit": 1.0 if sc.BILL_LESS_IORB in estimate.effect else 0.0,
                      "shift": abs(effect * value)}
    groups: Dict[str, List[date]] = {"all": list(frame.days)}
    for d, row in per_day.items():
        groups.setdefault(row["regime"], []).append(d)
    out: Dict[str, dict] = {}
    for label, members in groups.items():
        members = sorted(members)
        column = [per_day[d]["effect"] for d in members]
        entry: dict = {"days": len(members), "mean": sum(column) / len(members),
                       "share_in_fit": sum(per_day[d]["in_fit"] for d in members) / len(members),
                       "mean_abs_shift_bp": sum(per_day[d]["shift"] for d in members) / len(members)}
        if len(members) >= MIN_GROUP_DAYS:
            low, high = metrics.stationary_bootstrap_interval(
                lambda idx: sum(column[i] for i in idx) / len(idx), len(members), block_length=BLOCK, seed=SEED, replications=reps)
            entry["interval"] = [low, high]
        out[label] = entry
    return out


# -- the paired tests ----------------------------------------------------------------------------------------------------

_STATE: dict = {}


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


def lead_difference(frame, base: str, other: str) -> dict:
    return m1273.lead_difference(frame, base, other)


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, walk, bill_table, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
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
            for candidate in ARMS:
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped,
        "lead_difference": {"bill_against_ann_net": lead_difference(frame, ANNNET, BILL), "bill_against_s3c": lead_difference(frame, S3C, BILL),
                            "ann_net_against_s3c": lead_difference(frame, S3C, ANNNET)},
        "term_range": term_range(frame, bill_table),
        "effects": {str(h): effects(frame, walk, h, bill_table, reps=args.reps) for h in LEADS},
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def against_1321(results: Mapping[str, dict]) -> dict:
    """The references' pooled means here beside #1321's record, which re-ran them at 18:00 too: the walk is the same, so they must agree. Shown
    with the difference; the page says whether they do."""

    if not RECORD_1321.exists():
        return {}
    there = json.loads(RECORD_1321.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        a, b = there[window]["groups"]["pooled"]["all decision days"], result["groups"]["pooled"]["all decision days"]
        out[window] = {m: {x: {"now": b[m]["means"][x], "then": a[m]["means"][x], "difference": b[m]["means"][x] - a[m]["means"][x]}
                           for x in (S3, S3C, ANNNET)} for m in ("grid_crps", "upper_tail_twcrps", "brier_gt5")}
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
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_bill_iorb_1346")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1346, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arms": list(ARMS), "references": list(REFERENCES), "margin_bp": s3c_candidate.MARGIN_BP, "unit_bp": s3c_bill_iorb.UNIT_BPS,
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args)
    result["against_1321"] = against_1321(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str) -> List[str]:
    out = [f"| {SHORT[candidate]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(candidate):
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, candidate: str, reference: str, order: Optional[Sequence[str]] = None) -> List[str]:
    return m1288.split_table(window, split, candidate, reference, order)


def means_split_table(window: Mapping[str, object], split: str, metric: str) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(SHORT[m] for m in MODELS) + " |", "|---|---|" + "---|" * len(MODELS)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in MODELS) + " |")
    return out if len(out) > 2 else []


def effect_table(by_lead: Mapping[str, Mapping[str, dict]]) -> List[str]:
    out = ["| lead | regime | days | effect, bp per 10 bp of the gap [90%] | share of days in the fit | mean abs shift (bp) |", "|---|---|---|---|---|---|"]
    for lead in sorted(by_lead, key=int):
        eff = by_lead[lead]
        for name in sorted(eff, key=lambda x: (x != "all", x)):
            if name != "all" and lead != REGIME_LEAD:
                continue
            e = eff[name]
            text = f"{e['mean']:+.3f}" + (f" [{e['interval'][0]:+.3f}, {e['interval'][1]:+.3f}]" if "interval" in e else " (too few days)")
            out.append(f"| h={lead} | {name} | {e['days']} | {text} | {e['share_in_fit']:.2f} | {e['mean_abs_shift_bp']:.3f} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text}, grid CRPS: against (s3c-ann-net) {cell(_vs(entry, 'grid_crps', BILL, ANNNET))}; "
                     f"against (s3c) {cell(_vs(entry, 'grid_crps', BILL, S3C))}")
    return "; ".join(parts) + "."


def summary(r: Mapping[str, object]) -> List[str]:
    """The first screen: grid CRPS against (s3c-ann-net) and (s3c), by lead, in each window."""

    out = ["## Summary: grid CRPS by lead", "",
           "Skill and its 90% interval, the mean difference d and its studentized 90% interval, and the reading on the mean-d bound (positive favours "
           "the arm). The full tables, with the other metrics, follow.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        out += [f"**{WINDOW_TITLES[window].split(' (')[0]}**", "", "| lead | against (s3c-ann-net) | against (s3c) |", "|---|---|---|"]
        for lead in LEADS:
            g = w["groups"]["lead"][f"h={lead}"]
            out.append(f"| h={lead} | " + " | ".join(cell(_vs(g, "grid_crps", BILL, x)) for x in REFERENCES) + " |")
        g = w["groups"]["pooled"]["all decision days"]
        out.append("| pooled over h = 1..5 | " + " | ".join(cell(_vs(g, "grid_crps", BILL, x)) for x in REFERENCES) + " |")
        out.append("")
    return out


def render(r: dict) -> str:
    out = [
        "# (s3c-ann-net-bill): the 4-week bill rate less IORB beside the candidate (s3c-ann-net), at the 18:00 decision (#1346)", "",
        "**Does the previous business day's 4-week bill rate less IORB carry information about the spread beyond what (s3c-ann-net) reads?** "
        + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, one arm on the candidate (s3c-ann-net); ledger item 97. **Development data, not a "
        "verdict** (scoring protocol v1, #640). Her ruling of 1 November 2026 (chat, relayed on #1346): one arm that reads the 4-week bill rate "
        "less IORB, the previous business day's bill rate only, so that the arm does not rest on the same-day availability that #1334 leaves "
        "unmeasured; paired against (s3c-ann-net) and (s3c). **(s3c-ann-net) stays the H5 candidate; nothing here changes it.** Nothing is "
        "registered or published and no claim changes. Generated by `scripts/s3c_bill_iorb_1346.py page` from "
        f"`docs/research/s3c-bill-iorb-1346/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        "**What changed.** (s3c-ann-net) reads the settlement terms from the auction announcement and sizes them by net settlement. (s3c-ann-net-bill) "
        "adds one term to its fit: `(tbill_4w - iorb)` in units of 10 bp, read from the panel row before the decision day, the same figure at every "
        "lead. It enters the Huber fit with the ridge of 5 in the model's standardised units, so its effect in bp is the fitted coefficient times the "
        f"scale at the anchor, per {r['unit_bp']:g} bp of the gap. Everything else is (s3c-ann-net)'s and the SRF cap is (s3c)'s; the fit is on direct "
        "pairs. The references are re-run in the same walk.", "",
        "**Availability.** The decision on day D reads the rate dated D - 1. `metadata/sources.json` declares Treasury's bill rates public at 16:30 on the "
        "day they are dated, so the 16:00 decision of the published records already reads row D - 1 and the 18:00 decision would read row D: the "
        "same-day posting time that #1334 asks to measure. This arm reads D - 1 at 18:00 and would at 16:00, so it does not depend on whether Treasury's "
        "page carries day D's rate by 18:00. It still rests on Treasury's own export (not H.15) having posted day D - 1's rate by the morning of D, "
        "which no source contradicts and none measures; `tests/test_s3c_bill_iorb.py` pins the source row against `asof.InformationRule`.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "the arm. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a "
        "Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is "
        "understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days keep "
        "the **current method** (the group's days, scattered, resampled in date order as if consecutive), which #1221 questions and #1228 will decide; "
        "no reading of a day-type group is a finding. Where two models differ on few days of a group the bound may not be computed: the unstudentized "
        "interval of mean d is then given beside it, and no reading is taken from that. Groups of fewer than 20 days are listed with their means and not "
        "tested. The benchmarks are not part of this directive's comparisons and are not scored here.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, and by #1229, #1255, #1273, #1288 and #1321. "
        "This is a check on one arm queued by her ruling, not evidence for a verdict. The term is one number per decision day, so the pooled figure "
        "averages five leads that read the same figure; read the lead rows beside it.", ""]
    out += summary(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled, tr, ld = w["notes"], w["groups"]["pooled"]["all decision days"], w["term_range"], w["lead_difference"]["bill_against_ann_net"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits of the walk. The term over "
                f"the scored decision days (units of {tr['unit_bp']:g} bp): minimum {tr['min']:+.2f}, maximum {tr['max']:+.2f}, mean {tr['mean']:+.2f}, "
                f"standard deviation {tr['sd']:.2f}; above zero on {tr['share_positive']:.0%} of the days. The Huber fit down-weights large residuals "
                "but not extreme values of a regressor, so the extremes are shown. Cells on which the arm is not (s3c-ann-net) element for element, by "
                f"lead (of {ld['cells_per_lead']:,} each): " + ", ".join(f"h={h}: {ld['differing_cells'][str(h)]:,}" for h in LEADS) + ".", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled) + ["", f"### {LABELS[BILL]} against each reference (pooled)", ""] + against_table(
                    pooled, BILL) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
            for ref in plan(BILL):
                table = split_table(w, split, BILL, ref)
                if table:
                    out += [f"### {title}: {SHORT[BILL]} against {SHORT[ref]}", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split, "b90_closed")
            if table:
                out += [f"### 90% band coverage by {title}", ""] + table + [""]
        out += ["### The fitted effect of the term, by lead and regime of the target day", ""] + effect_table(w["effects"]) + [
            "", "The effect is the standardised effect of the refit the forecast used times the scale at the anchor in bp, per 10 bp of the gap. The "
            "pooled row is printed at every lead and the regime rows at h = 3 only (the record holds them all). The interval is a bootstrap interval "
            "of the mean over decision days, which share refits; it is not a sampling interval for the coefficient. The term enters a fit only when at "
            "least three training pairs carry a non-zero value. The mean absolute shift is the mean of |effect x term| over the days, in bp.", ""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_1321"):
        out += ["## The references against #1321's record (also made at 18:00)", "",
                "The references are re-run in the same walk as the arm. #1321 re-ran the same models over the same days at the same instant, so the "
                "pooled means below should agree. The largest absolute difference of a pooled mean is "
                f"{max(abs(v['difference']) for ms in r['against_1321'].values() for rows in ms.values() for v in rows.values()):.1e}.", ""]
        for window, metrics_ in r["against_1321"].items():
            out += [f"{WINDOW_TITLES[window].split(' (')[0]}: " + "; ".join(
                f"{METRIC_TITLES[m]}: " + ", ".join(f"{SHORT[x]} {v['now']:.6f} now, {v['then']:.6f} then" for x, v in rows.items())
                for m, rows in metrics_.items()) + ".", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. Does the arm replace (s3c-ann-net) as the H5 candidate?** The candidate does not change in this directive. Whether the arm "
        "should replace it rests on days already seen, split as above.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c-ann-net) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests the arm prospectively**, on the confirmation days only, under the scoring protocol.",
        "3. **Ask for a further arm** (another tenor, the same-day rate once #1334 has measured its posting time, or the 13-week rate), in a directive "
        "of its own.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3c-ann-net) and the arm, cap them as (s3c) is capped, and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized and effect intervals")
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
