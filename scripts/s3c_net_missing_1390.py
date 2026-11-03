"""The net settlement reader's missing state: how often a net rests on a missing figure, and (s3c-ann-net) with those days read two ways (#1390;
H5, registration design: data meaning; her ruling of 2 November 2026, the second outside review).

A development study, never a verdict. It writes JSON, CSV and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_net_missing_1390.json`, which this script refuses to read unless it is committed and unchanged. Three commands:

* `count`: step 1. By calendar year and class, the settlement days on which the net rests on a missing maturing estimate, on a class not fully announced,
  or (in hindsight only) on a cash management bill not yet on any schedule, against the days with a genuine zero. It uses `repo_model.net_settlement.net_state`.
* `score`: step 3. (s3c-ann-net) as now (`repo_model.s3c_announced`), and (s3c-ann-net-drop) (`repo_model.s3c_net_missing`): a class that rests on a missing
  figure contributes 0.0 to the net term, with the 0/1 flag `net_missing` beside the net terms. Both on direct pairs, at the 18:00 decision instant, with
  the SRF cap of (s3c) (`repo_model.s3c_candidate`, unchanged). Grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier
  score of P(> +5 bp), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill interval
  beside, on the development window (targets up to 2025-12-31) and the 2026 development days (targets 2026-01-02 to 2026-09-03) apart, split by lead,
  regime, pressure-day type, the settlement-day type of the target and the missing state of the target at each lead. The blind tier and every lockbox
  day are refused by the frames' own guards. It also writes the per-forecast log of the state (item 2).
* `page`: the result page from the score file.

Commands, from a clone of the branch (the walks are minutes, the paired tests the longer part; a cloud run unless the measured time says otherwise):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_net_missing_1390.py count --panel PUB.csv --output docs/research/s3c-net-missing-1390/counts.json
    PYTHONPATH=src python3 scripts/s3c_net_missing_1390.py score --panel PUB.csv --counts docs/research/s3c-net-missing-1390/counts.json \\
        --output docs/research/s3c-net-missing-1390/result.json --log docs/research/s3c-net-missing-1390/missing_log.csv
    PYTHONPATH=src python3 scripts/s3c_net_missing_1390.py page \\
        --score docs/research/s3c-net-missing-1390/result.json --output docs/research/s3c-net-missing-1390-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import multiprocessing
import sys
from datetime import date, datetime
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


from repo_model import announced_iorb, metrics, net_settlement as ns, policy_events, s3c_announced, s3c_candidate, s3c_net, s3c_net_missing  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1356's script (and through it #1321's, #1288's, #1273's and #1255's), loaded under an alias of its own so that the pickling of the worker pool's tasks does
#: not meet another test module's copy. Its `decision_instant_pinned` runs the chain at the declared 18:00 instant.
m1356 = _load("s3c_ann_net_cmb_1356", "s3c_ann_net_cmb_1356_in_1390")
m1321, m1288, m1273, m1255, k, c, s686, s761 = m1356.m1321, m1356.m1288, m1356.m1273, m1356.m1255, m1356.k, m1356.c, m1356.s686, m1356.s761
load_daily_panel = m1288.load_daily_panel
decision_instant_pinned = m1356.decision_instant_pinned

DECLARATION = REPO / "metadata" / "s3c_net_missing_1390.json"
RECORD_1356 = REPO / "docs" / "research" / "s3c-ann-net-cmb-1356" / "result.json"
SEED = 1390
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3C, ANNNET, B1P = m1288.S3C, m1288.ANNNET, m1288.B1P
DROP = "sc_s3c_ann_net_drop"
BENCHMARKS = m1288.BENCHMARKS
MODELS = BENCHMARKS + (S3C, ANNNET, DROP)
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3C: "(s3c), the H5 candidate", ANNNET: "(s3c-ann-net), as now",
          DROP: "(s3c-ann-net-drop), missing dropped with a flag"}
SHORT = {"B1": "B1", B1P: "B1'", "B2": "B2", S3C: "(s3c)", ANNNET: "(s3c-ann-net)", DROP: "(drop)"}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
EPSILON = 1e-9
LEADS = tuple(sp.HORIZONS)
COUNT_LEADS = (0,) + LEADS
FULL_SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
DAY_TYPE = m1288.DAY_TYPE
MISSING_SPLIT = "net_missing_state"
STATE_LABELS = ("net rests on a missing figure", "settlement day, no missing figure", "neither settles")
EFFECT_TERMS: Mapping[str, Tuple[str, ...]] = {
    ANNNET: ("settlement_coupon", "settlement_bill"),
    DROP: ("settlement_coupon", "settlement_bill", sc.MISSING_FLAG),
}
TERM_TITLES = {"settlement_coupon": "net coupon", "settlement_bill": "net bill", sc.MISSING_FLAG: "missing flag"}
TERM_UNITS = {"settlement_coupon": "bp per USD 100 bn", "settlement_bill": "bp per USD 100 bn", sc.MISSING_FLAG: "bp per flagged day"}
REGIME_LEAD = "3"
REPS = 2000
_STATE: Dict = {}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str, split: str = "pooled") -> List[str]:
    """What the drop reading is tested against: (s3c-ann-net) and (s3c), and on the full splits the benchmarks."""

    if candidate == DROP:
        return [ANNNET, S3C] + (list(BENCHMARKS) if split in FULL_SPLITS else [])
    return []


# -- step 1: the count ---------------------------------------------------------------------------------------------------


def _blank_day() -> Dict[str, int]:
    return {"settlement_days": 0, "net_rests_on_missing": 0, "of_which_missing_maturing": 0, "of_which_class_not_fully_announced": 0,
            "nothing_public": 0, "genuine_zero": 0, "complete_nonzero": 0, "cmb_pending_days": 0, "cmb_pending_and_not_otherwise_missing": 0}


def _blank_class() -> Dict[str, int]:
    return {ns.ABSENT: 0, ns.COMPLETE: 0, "complete_zero": 0, ns.MISSING_MATURING: 0, ns.INCOMPLETE: 0, ns.UNANNOUNCED: 0}


def count_states(dates: Sequence[date], auctions: Sequence[ns.Auction], last: date, decision_time) -> dict:
    """The state of every settlement day of the panel up to `last` at each lead of `COUNT_LEADS`, by calendar year of the settlement day.

    A settlement day is a panel day on which some auction settles. Lead 0 reads the settlement day's own `decision_time`; lead `h` the `decision_time`
    of the panel day `h` rows before. Per year and lead: `day` (the day-level categories, which exclude one another: the net rests on a missing figure,
    nothing is public yet, a genuine zero, a complete non-zero net) and `bill` and `coupon` (the state of each class). `cmb_pending_days` is HINDSIGHT: the
    days on which a cash management bill announced after the instant settles (`net_settlement.cmb_pending`); it is on no schedule at the instant and is
    not part of any state. The drain read on a missing maturing amount is summed in USD billions beside the absolute net of all settlement days.
    """

    by_day: Dict[date, List[ns.Auction]] = {}
    for a in auctions:
        by_day.setdefault(a.settles, []).append(a)
    out: Dict[str, Dict[str, dict]] = {}
    for i, day in enumerate(dates):
        if day > last or day not in by_day:
            continue
        for lead in COUNT_LEADS:
            if i - lead < 0:
                continue
            instant = datetime.combine(dates[i - lead], decision_time)
            state = ns.net_state(by_day[day], instant)
            entry = out.setdefault(str(day.year), {}).setdefault(str(lead), {
                "day": _blank_day(), "bill": _blank_class(), "coupon": _blank_class(), "drain_read_on_missing_maturing_bn": 0.0, "abs_net_bn": 0.0})
            counts = entry["day"]
            counts["settlement_days"] += 1
            pending = ns.cmb_pending(by_day[day], instant) > 0
            for name, read in (("bill", state.bill), ("coupon", state.coupon)):
                entry[name][read.state] += 1
                if read.state == ns.COMPLETE and read.net == 0.0:
                    entry[name]["complete_zero"] += 1
                if read.state == ns.MISSING_MATURING:
                    entry["drain_read_on_missing_maturing_bn"] += read.net
            entry["abs_net_bn"] += abs(state.net())
            if state.missing:
                counts["net_rests_on_missing"] += 1
                counts["of_which_missing_maturing"] += int(ns.MISSING_MATURING in (state.bill.state, state.coupon.state))
                counts["of_which_class_not_fully_announced"] += int(
                    any(r.state in (ns.INCOMPLETE, ns.UNANNOUNCED) for r in (state.bill, state.coupon)))
            elif state.bill.state == ns.ABSENT and state.coupon.state == ns.ABSENT:
                counts["nothing_public"] += 1
            elif state.net() == 0.0:
                counts["genuine_zero"] += 1
            else:
                counts["complete_nonzero"] += 1
            if pending:
                counts["cmb_pending_days"] += 1
                counts["cmb_pending_and_not_otherwise_missing"] += int(not state.missing)
    return out


def count(args) -> int:
    declaration = committed_declaration()
    panel = [row for row in load_daily_panel(Path(args.panel)) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_net_missing_1390")
    auctions = m1273.load_auctions()
    with decision_instant_pinned():
        result = {
            "issue": 1390, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(Path(args.panel)),
            "decision_time": c.DECISION_TIME.strftime("%H:%M"), "label": "development, not a verdict", "states": declaration["states"],
            "last_day": LAST_DAY.isoformat(), "leads": list(COUNT_LEADS),
            "counts": count_states([row.date for row in panel], auctions, LAST_DAY, c.DECISION_TIME),
        }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- step 3: the walks and the frame -------------------------------------------------------------------------------------


def walks_of(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """The walks of (s3c-ann-net) as now and of the drop reading over #1255's decision days, with the tables they read.

    Raises:
        ValueError: a scored decision day has no forecast of a walk.
    """

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    drop_table = s3c_net_missing.DroppedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    missing = s3c_net_missing.NetMissingTerms(panel, auctions, decision_time=k.DECISION_TIME)
    walks = {
        "ref": sc.walk(panel, days, term_table, states, (s3c_announced.ANN_NET_ARM,), sizes=net_table, **settings),
        "drop": sc.walk(panel, days, term_table, states, (s3c_net_missing.DROP_ARM,), sizes=drop_table, iorb=missing, **settings),
    }
    names = {"ref": s3c_announced.ANN_NET_ARM.name, "drop": s3c_net_missing.DROP_ARM.name}
    for key, walk in walks.items():
        for d in frame.days:
            if d not in walk.forecasts[names[key]]:
                raise ValueError(f"the {key} walk has no forecast of {names[key]} on the scored decision day {d}")
    return walks, names, (term_table, net_table, drop_table, missing)


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with (s3c-ann-net) as now and the drop reading added: `(frame, notes, walks, names, tables, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walks, names, tables = walks_of(window, frame, panel, splits, registry, results, auctions, first)
    raw = {ANNNET: ("ref", names["ref"]), DROP: ("drop", names["drop"])}
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS + (S3C,)}
    for model, (key, arm) in raw.items():
        forecasts[model] = m1255.s3c_forecasts(frame, register, {d: walks[key].forecasts[arm][d] for d in frame.days})
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    notes = dict(notes, refits_ref=len(walks["ref"].fits), refits_drop=len(walks["drop"].fits))
    return frame, notes, walks, names, tables, groups_fn


def effect_values(model: str, lead: int, index: int, tables) -> Dict[str, float]:
    """The value of each of the model's terms on the target of the decision on row `index`, in units of USD 100 bn, or 0/1 for the flag."""

    _term, net_table, drop_table, missing = tables
    if model == ANNNET:
        sizes = net_table.read(lead, index)
        return {t: sizes[t] / sc.SIZE_UNIT for t in EFFECT_TERMS[model]}
    sizes = drop_table.read(lead, index)
    out = {t: sizes[t] / sc.SIZE_UNIT for t in ("settlement_coupon", "settlement_bill")}
    out.update(missing.read(lead, index))
    return out


def missing_members(frame, facts: Mapping[date, dict], tables, lead: int) -> Dict[str, List[date]]:
    """The decision days whose lead-`lead` target settlement rests on a missing figure at the decision, those that settle with none, and those with no settlement."""

    missing = tables[3]
    out: Dict[str, List[date]] = {label: [] for label in STATE_LABELS}
    for d in frame.days:
        target = frame.target(d, lead)
        if missing.read(lead, frame.position[d])[sc.MISSING_FLAG]:
            out[STATE_LABELS[0]].append(d)
        elif facts[target]["coupon"] or facts[target]["bill"]:
            out[STATE_LABELS[1]].append(d)
        else:
            out[STATE_LABELS[2]].append(d)
    return out


def forecast_log(frame, tables) -> List[Mapping[str, object]]:
    """The per-forecast log (#1390 item 2): the state of each class of the target day's settlement at every scored (decision day, lead)."""

    missing = tables[3]
    return [missing.log_row(lead, frame.position[d]) for d in frame.days for lead in LEADS]


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in plan(candidate, split):
        days = list(members)
        if _identical(series, candidate, name, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = m1356.unstudentized(series, candidate, name, days, _STATE["reps"])
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def extra_groups(frame, facts, tables) -> List[tuple]:
    """The groups this study adds to #1255's: the settlement-day types and the missing state of the target, at each lead."""

    out: List[tuple] = []
    for lead in LEADS:
        for label, members in m1288.day_type_members(frame, facts, lead).items():
            out.append((DAY_TYPE, f"h={lead}: {label}", f"lead{lead}", members))
        for label, members in missing_members(frame, facts, tables, lead).items():
            out.append((MISSING_SPLIT, f"h={lead}: {label}", f"lead{lead}", members))
    return [g for g in out if g[3]]


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> Tuple[dict, List[Mapping[str, object]]]:
    frame, notes, walks, names, tables, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    facts = m1288.settlement_facts(panel, auctions)
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in FULL_SPLITS]
    groups += extra_groups(frame, facts, tables)
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
            jobs.append((split, label, grain, metric, DROP, tuple(members)))
    done = run_jobs(jobs, args.workers)

    reads = {m: (lambda lead, i, m=m: effect_values(m, lead, i, tables)) for m in (ANNNET, DROP)}
    arm_walk = {ANNNET: ("ref", names["ref"]), DROP: ("drop", names["drop"])}
    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped,
        "lead_difference": m1273.lead_difference(frame, ANNNET, DROP),
        "effects": {m: {str(h): m1356.effects(frame, walks[arm_walk[m][0]], arm_walk[m][1], EFFECT_TERMS[m], h, reads[m], reps=args.reps) for h in LEADS}
                    for m in (ANNNET, DROP)},
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    result["flag_share_by_lead"] = {
        str(h): sum(tables[3].read(h, frame.position[d])[sc.MISSING_FLAG] for d in frame.days) / len(frame.days) for h in LEADS}
    return result, forecast_log(frame, tables)


def against_1356(results: Mapping[str, dict]) -> dict:
    """The pooled means of (s3c) and (s3c-ann-net) here beside #1356's record, made at 18:00 with the same walks: they must agree to 1e-9.

    Raises:
        ValueError: they do not.
    """

    if not RECORD_1356.exists():
        return {}
    there = json.loads(RECORD_1356.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        a, b = there[window]["groups"]["pooled"]["all decision days"], result["groups"]["pooled"]["all decision days"]
        out[window] = {m: {x: {"now": b[m]["means"][x], "then": a[m]["means"][x], "difference": b[m]["means"][x] - a[m]["means"][x]}
                           for x in (S3C, ANNNET)} for m in ("grid_crps", "upper_tail_twcrps", "brier_gt5")}
        worst = max(abs(v["difference"]) for rows in out[window].values() for v in rows.values())
        if worst > 1e-9:
            raise ValueError(f"the references of the {window} window differ from #1356's record by {worst:.2e}: the walks are not the same")
    return out


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with decision_instant_pinned():
        return _score(args)


def write_log(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["window", "decision_day", "lead", "target_day", "bill", "coupon", "missing"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_net_missing_1390")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1390, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "references": [ANNNET, S3C] + list(BENCHMARKS), "margin_bp": s3c_candidate.MARGIN_BP,
        "windows": {}, "reading_rules": declaration["reading_rules"],
        "counts": json.loads(Path(args.counts).read_text(encoding="utf-8")) if args.counts else {},
    }
    log: List[dict] = []
    for window in WINDOWS:
        result["windows"][window], rows = run_window(window, panel, splits, registry, table, register, results, auctions, args)
        log += [dict(row, window=window) for row in rows]
    result["against_1356"] = against_1356(result["windows"]) if args.first is None else {}
    result["log_rows"] = len(log)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.log:
        write_log(Path(args.log), log)
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


def pct(part: int, whole: int) -> str:
    return f"{part:,} ({part / whole:.0%})" if whole else "0"


def _sum_years(by_year: Mapping[str, Mapping[str, dict]], lead: str, years: Optional[Sequence[str]] = None) -> Tuple[dict, dict, dict]:
    day, bill, coupon = _blank_day(), _blank_class(), _blank_class()
    for year, leads in by_year.items():
        if years is not None and year not in years or lead not in leads:
            continue
        for key, value in leads[lead]["day"].items():
            day[key] += value
        for target, name in ((bill, "bill"), (coupon, "coupon")):
            for key, value in leads[lead][name].items():
                target[key] += value
    return day, bill, coupon


def count_year_table(counts: Mapping[str, Mapping[str, dict]], lead: str) -> List[str]:
    out = ["| year | settlement days | net rests on a missing figure | of which a maturing estimate missing | of which a class not fully announced | "
           "nothing public yet | genuine zero | complete, non-zero | CMB announced later (hindsight) |", "|---|---|---|---|---|---|---|---|---|"]
    for year in sorted(counts):
        if lead not in counts[year]:
            continue
        d = counts[year][lead]["day"]
        n = d["settlement_days"]
        out.append(f"| {year} | {n} | {pct(d['net_rests_on_missing'], n)} | {d['of_which_missing_maturing']} | {d['of_which_class_not_fully_announced']} | "
                   f"{d['nothing_public']} | {d['genuine_zero']} | {d['complete_nonzero']} | {d['cmb_pending_days']} |")
    d, _b, _c = _sum_years(counts, lead)
    n = d["settlement_days"]
    out.append(f"| all | {n} | {pct(d['net_rests_on_missing'], n)} | {d['of_which_missing_maturing']} | {d['of_which_class_not_fully_announced']} | "
               f"{d['nothing_public']} | {d['genuine_zero']} | {d['complete_nonzero']} | {d['cmb_pending_days']} |")
    return out


def count_class_table(counts: Mapping[str, Mapping[str, dict]], lead: str) -> List[str]:
    out = ["| year | class | absent | complete, non-zero | genuine zero | maturing estimate missing | partly announced | none announced yet |",
           "|---|---|---|---|---|---|---|---|"]
    for year in sorted(counts) + ["all"]:
        _d, bill, coupon = _sum_years(counts, lead, None if year == "all" else [year])
        for name, c_ in (("bill", bill), ("coupon", coupon)):
            if not sum(c_.values()):
                continue
            nonzero = c_[ns.COMPLETE] - c_["complete_zero"]
            out.append(f"| {year} | {name} | {c_[ns.ABSENT]} | {nonzero} | {c_['complete_zero']} | {c_[ns.MISSING_MATURING]} | {c_[ns.INCOMPLETE]} | {c_[ns.UNANNOUNCED]} |")
    return out


def count_lead_table(counts: Mapping[str, Mapping[str, dict]], leads: Sequence[int]) -> List[str]:
    out = ["| read at | settlement days | net rests on a missing figure | maturing estimate missing | class not fully announced | genuine zero | "
           "CMB announced later (hindsight) |", "|---|---|---|---|---|---|---|"]
    for lead in leads:
        d, _b, _c = _sum_years(counts, str(lead))
        n = d["settlement_days"]
        when = "the settlement day's own 18:00" if lead == 0 else f"lead h = {lead}"
        out.append(f"| {when} | {n} | {pct(d['net_rests_on_missing'], n)} | {d['of_which_missing_maturing']} | {d['of_which_class_not_fully_announced']} | "
                   f"{d['genuine_zero']} | {d['cmb_pending_days']} |")
    return out


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], split: str = "pooled") -> List[str]:
    out = [f"| {SHORT[DROP]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(DROP, split):
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, DROP, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, reference: str) -> List[str]:
    return m1288.split_table(window, split, DROP, reference)


def effect_table(by_lead: Mapping[str, Mapping[str, dict]], terms: Sequence[str]) -> List[str]:
    cols = [f"{TERM_TITLES[t]} ({TERM_UNITS[t]}) [90%]" for t in terms]
    out = ["| lead | regime | days | " + " | ".join(cols) + " | share of days in the fit | mean abs shift on active days (bp) |",
           "|---|---|---|" + "---|" * (len(terms) + 2)]
    for lead in sorted(by_lead, key=int):
        eff = by_lead[lead]
        for name in sorted(eff, key=lambda x: (x != "all", x)):
            if name != "all" and lead != REGIME_LEAD:
                continue
            e = eff[name]
            parts = []
            for t in terms:
                m = e[t]
                parts.append(f"{m['mean']:+.3f}" + (f" [{m['interval'][0]:+.3f}, {m['interval'][1]:+.3f}]" if "interval" in m else " (too few days)"))
            shift = "n/a" if e["mean_abs_shift_bp_on_active_days"] is None else f"{e['mean_abs_shift_bp_on_active_days']:.3f}"
            share = " / ".join(f"{e[t]['share_in_fit']:.2f}" for t in terms)
            out.append(f"| h={lead} | {name} | {e['days']} | " + " | ".join(parts) + f" | {share} | {shift} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("development", "On the development window"), ("2026", "on the 2026 development days")):
        w = r["windows"].get(window)
        if w is None:
            continue
        g = w["groups"]["pooled"]["all decision days"]
        parts.append(f"{text}, the drop reading's pooled grid CRPS against (s3c-ann-net): {cell(_vs(g, 'grid_crps', DROP, ANNNET))}")
    return "; ".join(parts) + "."


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**What should a missing maturing amount mean in the registered recipe?** This is data meaning (#1390 item 4), and it is hers. The reader today "
        "reads a maturing estimate that no announced record carries as 0.0, so the class drains its whole offering, and it leaves a class that is not fully "
        "announced at 0.0. This page counts how often each happens and what scoring the other reading changes. Nothing here changes the candidate.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Keep the current reading and log the missing state per forecast** (default). The candidate and every published figure stay as they are; the log of "
        "this page's kind is kept for the live record.",
        "2. **Register the drop reading** (a missing class contributes 0.0 and a missingness flag enters). This changes the candidate's recipe and needs "
        "a directive of its own that tests it prospectively.",
        "3. **Treat a missing maturing estimate as a data-quality finding** and ask for the Fiscal Data records to be checked for the days counted here, "
        "in a directive of its own, before any reading is chosen.", ""]


def render(r: dict) -> str:
    counts = r.get("counts", {}).get("counts", {})
    out = [
        "# The net settlement reader's missing state, and (s3c-ann-net) with the missing days read two ways (#1390)", "",
        "**Does a net settlement figure of 0.0 mean zero, and does reading the missing ones another way move the candidate's score?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), registration design (data meaning), step 3 on the candidate (s3c-ann-net); her ruling of 2 November 2026 "
        "(chat, relayed on #1390: the second outside review). **Development data, not a verdict** (scoring protocol v1, #640). **(s3c-ann-net) stays the "
        "candidate of avenue #1318 and (s3c) the H5 candidate; nothing here changes either, and what a missing amount means is hers.** Nothing is registered or "
        "published, no figure of a published record changes, and the published declaration `metadata/net_settlement.json` does not change. Generated by "
        f"`scripts/s3c_net_missing_1390.py page` from `docs/research/s3c-net-missing-1390/result.json`, not edited by hand; declared in `{r['declaration']}` "
        "before any score.", "",
        "**What the reader does.** For each settlement day and each class (bill types, coupon types) `net_settlement.net_state` now names the state: "
        "`complete` (fully announced, with a maturing estimate), `absent` (nothing of the class settles), `missing_maturing` (fully announced, no announced record "
        "carries a maturing estimate, so the net reads the maturing amount as 0.0 and the class drains its whole offering), `incomplete` (partly announced: the "
        "class is left out and reads 0.0, #679) and `unannounced` (on the schedule, nothing announced: reads 0.0). `net_for_day` returns the same numbers as "
        "before (tests pin hand values that the function on main also returns). A cash management bill (CMB) announced after the instant is on no published "
        "schedule (#738), so nothing at the instant can say it is coming; it is counted below in hindsight and is not part of the state, the flag or the "
        "per-forecast log.", "",
        "## Step 1: how many settlement days rest on a missing figure", ""]
    if counts:
        out += ["Panel days from 2018-04-03 to 2026-09-03 on which an auction settles, by year of the settlement day, read at the decision instant "
                f"({r['decision_time']}) of the day before the settlement (lead h = 1), the lead of the settlement terms in the published declaration:", ""]
        out += count_year_table(counts, "1") + ["", "By class, the same reading:", ""] + count_class_table(counts, "1") + [""]
        out += ["Read at every lead (all years). The more days ahead, the fewer auctions are announced, so the more classes are not fully announced; at the "
                "settlement day's own 18:00 (lead 0) every scheduled auction is announced and what remains missing is the maturing estimate itself:", ""]
        out += count_lead_table(counts, COUNT_LEADS) + [""]
        d1, _b, _c = _sum_years(counts, "1")
        d0, _b0, _c0 = _sum_years(counts, "0")
        drain = sum(counts[y]["1"]["drain_read_on_missing_maturing_bn"] for y in counts if "1" in counts[y])
        total = sum(counts[y]["1"]["abs_net_bn"] for y in counts if "1" in counts[y])
        out += [f"At lead 1, {d1['of_which_missing_maturing']} settlement days read a missing maturing estimate as 0.0 (the drain so read sums to USD {drain:,.0f} bn, "
                f"against USD {total:,.0f} bn of absolute net settlement over all settlement days at that lead); at the settlement day's own 18:00 the figure is "
                f"{d0['of_which_missing_maturing']}. The column 'genuine zero' counts the days on which every class that settles is fully announced, carries a "
                "maturing estimate, and the net is exactly 0.0; 'nothing public yet' counts the days on which a settlement exists in the records but nothing of it was on the "
                "schedule or announced at the instant (a cash management bill alone, announced later), which the net reads as 0.0 as well.", ""]
    else:
        out += ["(The count file was not given to this run.)", ""]
    out += [
        "## Step 3: the candidate with the missing days read two ways", "",
        "**Two readings, stated before any score.** *As now*: (s3c-ann-net), the missing maturing amount read as 0.0, a class not fully announced left out, "
        "the state logged and not read. *Drop*: a class whose state is `missing_maturing`, `incomplete` or `unannounced` contributes 0.0 to the net term, and a "
        f"0/1 flag `net_missing` (1 when either class of the target day rests on a missing figure at the decision instant, {r['decision_time']} of D = T - h) "
        "enters beside the two net terms. Only `missing_maturing` differs in the net between the two (the other two states read 0.0 in both); the flag is what is "
        "new. Both on direct pairs, with the SRF cap of (s3c). The references (s3c-ann-net) and (s3c), and the benchmarks B1, B1' and B2, are scored in the "
        "same run.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, "
        f"seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours the model named first. **A reading "
        "(gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a Brier score the skill is the "
        "Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x after 2020, so an "
        "interval that excludes zero is narrower than it should be. The intervals of a group of target days keep the **current method** (#1221, #1228). Where two "
        "models differ on few days of a group the bound may not be computed: the unstudentized interval of mean d is then given beside it, and no reading is "
        "taken from that. Groups of fewer than 20 days are listed and not tested. The benchmarks are tested on the pooled, lead, regime and pressure-day-type "
        "groups only.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, and by #1229 and the studies after it. They are shown "
        "separately and decide nothing.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        ld = w["lead_difference"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits_ref']} refits of the reference walk and "
                f"{n['refits_drop']} of the drop walk. Cells on which the drop reading is not (s3c-ann-net) element for element, by lead (of "
                f"{ld['cells_per_lead']:,} each): " + ", ".join(f"h={h}: {ld['differing_cells'][str(h)]:,}" for h in LEADS)
                + ". Share of decision days on which the flag is 1, by lead: " + ", ".join(f"h={h}: {w['flag_share_by_lead'][str(h)]:.0%}" for h in LEADS) + ".", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled) + ["", "### The drop reading against each reference (pooled)", ""] + against_table(pooled) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"),
                             (DAY_TYPE, "By the settlement-day type of the target at each lead"),
                             (MISSING_SPLIT, "By the missing state of the target at each lead")):
            for ref in plan(DROP, split)[:2]:
                table = split_table(w, split, ref)
                if table:
                    out += [f"### {title}: {SHORT[DROP]} against {SHORT[ref]}", ""] + table + [""]
        out += ["### The fitted effect, by lead and regime of the target day", ""]
        for model in (ANNNET, DROP):
            out += [f"{LABELS[model]}:", ""] + effect_table(w["effects"][model], EFFECT_TERMS[model]) + [""]
        out += ["The effect is the standardised effect of the refit the forecast used times the scale at the anchor in bp. The pooled row is printed at every "
                "lead and the regime rows at h = 3 only (the record holds them all). The interval is a bootstrap interval of the mean over decision days, which "
                "share refits; it is not a sampling interval for the coefficient. A term enters a fit only when at least three training pairs carry it.", ""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_1356"):
        out += ["## The references against #1356's record (made at 18:00)", "",
                "(s3c) and (s3c-ann-net) are re-run here with the same walks; the pooled means equal #1356's to 1e-9 (the run refuses to write otherwise). "
                "Largest absolute difference: "
                f"{max(abs(v['difference']) for ms in r['against_1356'].values() for rows in ms.values() for v in rows.values()):.1e}.", ""]
    out += [f"The per-forecast log of the state ({r.get('log_rows', 0):,} rows, one per scored decision day and lead of both windows) is "
            "`docs/research/s3c-net-missing-1390/missing_log.csv`; it is a function of the announcements at each decision instant only.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    n = sub.add_parser("count", help="step 1: count the settlement days by state, by year, class and lead")
    n.add_argument("--panel", required=True)
    n.add_argument("--output", required=True)
    n.set_defaults(func=count)
    s = sub.add_parser("score", help="walk (s3c-ann-net) as now and the drop reading, cap them as (s3c) is capped, and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--counts", default=None, help="the count file of `count`, copied into the score file for the page")
    s.add_argument("--log", default=None, help="write the per-forecast log of the state (CSV)")
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
