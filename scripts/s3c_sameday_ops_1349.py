"""(s3c-ann-net-sameday): the decision day's own ON RRP and SRF take-up as a development arm on the candidate (s3c-ann-net), at the 18:00 decision
instant (#1349; H5 step 3; her ruling of 1 November 2026 on avenue #1337, ledger item 98: "use the same day and test it").

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_sameday_ops_1349.json`, which this script refuses to read unless it is committed and unchanged. The arm is
`repo_model.same_day_operations.SAMEDAY_ARM`: (s3c-ann-net) with three extra terms of the decision day itself, the overnight Standing Repo
Facility take-up (a 0/1 flag and its size) and the change in the ON RRP amount accepted from the previous panel day, each read only when the Desk
had last written its records at or before the decision instant. The references (s3c) and (s3c-ann-net) are re-run in the same run, at 18:00
(`repo_model.decision_instant`); the frames and machinery are #1255's, #1273's, #1288's and #1321's and are loaded as they are. The blind tier and
every lockbox day are refused by the frames' own guards.

`availability` comes first and is committed with the declaration: it shows, from the Desk's own write times in the tracked snapshots, which operation
dates are public by 18:00 on their own day, and which are withheld.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009
ruling) with the skill interval beside, split by lead, regime, pressure-day type and the decision day's own take-up; reports the coverage of the
central 90% band; and the fitted effect of the three terms by lead and regime. The 2026 development days are a window of their own.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_sameday_ops_1349.py availability \\
        --output docs/research/s3c-sameday-ops-1349/availability.json
    PYTHONPATH=src python3 scripts/s3c_sameday_ops_1349.py score --panel PUB.csv \\
        --output docs/research/s3c-sameday-ops-1349/result.json
    PYTHONPATH=src python3 scripts/s3c_sameday_ops_1349.py page \\
        --score docs/research/s3c-sameday-ops-1349/result.json --output docs/research/s3c-sameday-ops-1349-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import statistics
import sys
from datetime import date, datetime, timedelta
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


from repo_model import announced_iorb, metrics, policy_events, s3c_announced, s3c_candidate, s3c_net  # noqa: E402
from repo_model import same_day_operations as sdo  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.decision_instant import DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1321's script (and through it #1288's, #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the
#: worker pool's tasks does not meet another test module's copy.
m1321 = _load("s3c_flagnet_gross_1321", "s3c_flagnet_gross_1321_in_1349")
m1288, m1273, m1255, k, c, s686, s761 = m1321.m1288, m1321.m1273, m1321.m1255, m1321.k, m1321.c, m1321.s686, m1321.s761
load_daily_panel = m1321.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_sameday_ops_1349.json"
AVAILABILITY = REPO / "docs" / "research" / "s3c-sameday-ops-1349" / "availability.json"
RECORD_1321 = REPO / "docs" / "research" / "s3c-flagnet-gross-1321" / "result.json"
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"
ON_RRP_DIR = SNAPSHOTS / "on_rrp_inputs" / "nyfed_on_rrp"
SRF_DIR = SNAPSHOTS / "srf_inputs" / "nyfed_srf"
SEED = 1349
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3, S3C, ANNNET = m1288.S3, m1288.S3C, m1288.ANNNET
SAMEDAY = "sc_s3c_ann_net_sameday"
ARMS = (SAMEDAY,)
REFERENCES = (ANNNET, S3C)
MODELS = (S3, S3C, ANNNET, SAMEDAY)
LABELS = {S3: "(s3)", S3C: "(s3c)", ANNNET: "(s3c-ann-net), the candidate", SAMEDAY: "(s3c-ann-net-sameday)"}
SHORT = {S3: "(s3)", S3C: "(s3c)", ANNNET: "(s3c-ann-net)", SAMEDAY: "(s3c-ann-net-sameday)"}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
TAKE_UP = "decision_day_take_up"
TAKE_UP_LABELS = ("SRF take-up above zero on the decision day", "no SRF take-up on the decision day",
                  "ON RRP changed by USD 10 bn or more on the decision day", "ON RRP changed by less than USD 10 bn on the decision day")
#: A move of the ON RRP amount accepted that counts as a change on the take-up split, in units of `sc.SIZE_UNIT` (USD 10 bn).
CHANGE_CUT = 10.0 / sc.SIZE_UNIT
TERM_TITLES = {sc.SRF_FLAG: "SRF flag", sc.SRF_SIZE: "SRF size", sc.RRP_CHANGE: "ON RRP change"}
TERM_UNITS = {sc.SRF_FLAG: "bp per flagged day", sc.SRF_SIZE: "bp per USD 100 bn", sc.RRP_CHANGE: "bp per USD 100 bn"}
REGIME_LEAD = "3"
REPS = 2000
SOURCES = ("on_rrp", "srf")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What the arm is tested against: the candidate (s3c-ann-net) and (s3c)."""

    return list(REFERENCES) if candidate in ARMS else []


# -- availability --------------------------------------------------------------------------------------------------------


def _hours(moment: datetime) -> float:
    return moment.hour + moment.minute / 60 + moment.second / 3600


def source_availability(figures: Mapping[date, sdo.DayFigure], operations: Sequence[Mapping[str, object]], kind, last: date) -> dict:
    """Which operation dates of a source are public by the decision instant of their own day, from the Desk's last write of their records.

    A date is public when its latest `lastUpdated` is at or before 18:00 New York on the date itself (`repo_model.same_day_operations`). The
    margin is the time between the latest write among the public dates and the instant. `close_to_write_minutes` is, per operation of the date
    that was written on its own date, the minutes from the stated `closeTime` to `lastUpdated`.
    """

    dates = sorted(d for d in figures if d <= last)
    public, withheld = [], []
    for d in dates:
        written = figures[d].written
        (public if written <= datetime.combine(d, DECISION_TIME) else withheld).append(d)
    hours = sorted(_hours(figures[d].written) for d in public)
    lags = []
    for record in operations:
        if not kind(record) or record.get("operationDate") is None or date.fromisoformat(str(record["operationDate"])) > last:
            continue
        close, written = record.get("closeTime"), datetime.fromisoformat(str(record["lastUpdated"]))
        if close and written.date().isoformat() == str(record["operationDate"]):
            at = datetime.combine(written.date(), datetime.strptime(str(close), "%H:%M").time())
            lags.append((written - at).total_seconds() / 60)
    lags.sort()

    def quantile(values: Sequence[float], q: float) -> Optional[float]:
        return None if not values else values[min(len(values) - 1, int(q * len(values)))]

    by_year: Dict[str, Dict[str, int]] = {}
    for d in dates:
        slot = by_year.setdefault(str(d.year), {"dates": 0, "public": 0})
        slot["dates"] += 1
        slot["public"] += 1 if d in public else 0
    latest = min(public, key=lambda d: datetime.combine(d, DECISION_TIME) - figures[d].written) if public else None
    return {
        "operation_dates": len(dates), "first": dates[0].isoformat(), "last": dates[-1].isoformat(),
        "public_by_decision": len(public), "withheld": [{"date": d.isoformat(), "last_write": figures[d].written.isoformat(sep=" ")} for d in withheld],
        "share_public": len(public) / len(dates),
        "write_hour_median": statistics.median(hours), "write_hour_p99": quantile(hours, 0.99), "write_hour_max": hours[-1],
        "closest_public_write": None if latest is None else {"date": latest.isoformat(), "last_write": figures[latest].written.isoformat(sep=" ")},
        "margin_minutes_of_closest_public_write": None if latest is None else
        (datetime.combine(latest, DECISION_TIME) - figures[latest].written).total_seconds() / 60,
        "public_by_16": sum(1 for d in dates if figures[d].written <= datetime.combine(d, datetime.strptime("16:00", "%H:%M").time())),
        "close_to_write_minutes": {"operations": len(lags), "median": statistics.median(lags) if lags else None, "p99": quantile(lags, 0.99),
                                   "max": lags[-1] if lags else None},
        "by_year": by_year,
    }


def availability_record(on_rrp_dir: Path = ON_RRP_DIR, srf_dir: Path = SRF_DIR, last: date = LAST_DAY) -> dict:
    """The evidence that the decision day's own ON RRP result and SRF take-up are public before the 18:00 decision, from the tracked snapshots.

    Both sources are read by the rule of `repo_model.same_day_operations`; the record states which of the two the arm may use.
    """

    rrp_ops = sdo.load_operations(on_rrp_dir)
    srf_ops = sdo.load_operations(srf_dir)
    rrp = source_availability(sdo.on_rrp_days(rrp_ops), rrp_ops, lambda r: r.get("operationType") == "Reverse Repo", last)
    srf_figures = sdo.srf_days(srf_ops)
    kept = [r for r in srf_ops if r.get("operationType") == "Repo" and r.get("term") == "Overnight"
            and date.fromisoformat(str(r["operationDate"])) in srf_figures]
    srf = source_availability(srf_figures, kept, lambda r: True, last)
    used = [name for name, block in (("on_rrp", rrp), ("srf", srf)) if block["share_public"] >= 0.99]
    return {
        "issue": 1349, "decision_time": DECISION_TIME.strftime("%H:%M"), "last_day": last.isoformat(),
        "rule": ("a date's figure is public at the decision instant of its own day when the latest lastUpdated of its records is at or before 18:00 "
                 "New York on that day; a date written later (or rewritten later) is withheld and reads as no take-up"),
        "caveat": ("lastUpdated is the Desk's last write, not a stated publication time: the Desk states no clock time for its results, and the "
                   "reading assumes the API serves a record from the time it is written, which cannot be verified from outside"),
        "on_rrp": rrp, "srf": srf, "used": used,
        "reading": ("both sources are used" if len(used) == 2 else f"only {used} is used"),
    }


def availability(args) -> int:
    record = availability_record()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def load_terms(panel) -> sdo.SameDayOperationTerms:
    """The table of the three terms over the panel's dates, from the tracked operation snapshots, at the decision instant."""

    return sdo.SameDayOperationTerms(
        [row.date for row in panel], sdo.srf_days(sdo.load_operations(SRF_DIR)), sdo.on_rrp_days(sdo.load_operations(ON_RRP_DIR)),
        decision_time=k.DECISION_TIME)


def walks_of(window: str, frame, panel, splits, registry, results, auctions, first: Optional[date]):
    """One walk of (s3c-ann-net) and (s3c-ann-net-sameday), over #1255's decision days, with the tables they read.

    Raises:
        ValueError: the walk is not at the declared decision instant, or a scored decision day has no forecast of an arm.
    """

    if k.DECISION_TIME != DECISION_TIME:
        raise ValueError(f"the walks run at {k.DECISION_TIME}, not at the declared decision instant {DECISION_TIME}")
    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    ops = load_terms(panel)
    walk = sc.walk(panel, days, term_table, states, (s3c_announced.ANN_NET_ARM, sdo.SAMEDAY_ARM), sizes=net_table, iorb=ops, **settings)
    for name in (s3c_announced.ANN_NET_ARM.name, sdo.SAMEDAY_ARM.name):
        for d in frame.days:
            if d not in walk.forecasts[name]:
                raise ValueError(f"the walk has no forecast of {name} on the scored decision day {d}")
    return walk, (term_table, net_table, ops)


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with the reference (s3c-ann-net) and the arm added: `(frame, notes, walk, tables, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk, tables = walks_of(window, frame, panel, splits, registry, results, auctions, first)
    raw = {
        ANNNET: {d: walk.forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in frame.days},
        SAMEDAY: {d: walk.forecasts[sdo.SAMEDAY_ARM.name][d] for d in frame.days},
    }
    forecasts = {S3: frame.forecasts[S3], S3C: frame.forecasts[S3C]}
    for name, found in raw.items():
        forecasts[name] = m1255.s3c_forecasts(frame, register, found)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    return frame, dict(notes, refits=len(walk.fits)), walk, tables, groups_fn


# -- the decision day's take-up ------------------------------------------------------------------------------------------


def take_up_of(frame, ops: sdo.SameDayOperationTerms) -> Dict[date, Dict[str, float]]:
    """The three terms of each scored decision day (the same at every lead), read as a forecast reads them."""

    return {d: ops.read(1, frame.position[d]) for d in frame.days}


def take_up_members(frame, ops: sdo.SameDayOperationTerms) -> Dict[str, List[date]]:
    """The scored decision days with an SRF take-up above zero, those without, and the days on which the ON RRP amount moved by `CHANGE_CUT` or more."""

    found = take_up_of(frame, ops)
    out: Dict[str, List[date]] = {label: [] for label in TAKE_UP_LABELS}
    for d, terms in found.items():
        out[TAKE_UP_LABELS[0] if terms[sc.SRF_FLAG] else TAKE_UP_LABELS[1]].append(d)
        out[TAKE_UP_LABELS[2] if abs(terms[sc.RRP_CHANGE]) >= CHANGE_CUT else TAKE_UP_LABELS[3]].append(d)
    return out


def coverage_of(frame, ops: sdo.SameDayOperationTerms) -> dict:
    """How the three terms act on the scored decision days: days with an SRF take-up, with an ON RRP move, and the days whose figure was withheld."""

    found = take_up_of(frame, ops)
    withheld_srf = withheld_rrp = 0
    for d in frame.days:
        i = frame.position[d]
        instant = ops.instant(i)
        figure = ops.srf.get(d)
        withheld_srf += 1 if figure is not None and figure.written > instant else 0
        now, before = ops.rrp.get(d), ops.rrp.get(ops.dates[i - 1])
        withheld_rrp += 1 if any(f is not None and f.written > instant for f in (now, before)) else 0
    by_regime: Dict[str, dict] = {}
    for d, terms in found.items():
        slot = by_regime.setdefault(frame.regime(d), {"decision_days": 0, "srf_days": 0, "srf_mean_size_on_active_days": 0.0, "rrp_moves": 0})
        slot["decision_days"] += 1
        if terms[sc.SRF_FLAG]:
            slot["srf_days"] += 1
            slot["srf_mean_size_on_active_days"] += terms[sc.SRF_SIZE]
        slot["rrp_moves"] += 1 if abs(terms[sc.RRP_CHANGE]) >= CHANGE_CUT else 0
    for slot in by_regime.values():
        slot["srf_mean_size_on_active_days"] = slot["srf_mean_size_on_active_days"] / slot["srf_days"] if slot["srf_days"] else None
    return {"decision_days": len(found), "srf_days": sum(1 for t in found.values() if t[sc.SRF_FLAG]),
            "rrp_moves": sum(1 for t in found.values() if abs(t[sc.RRP_CHANGE]) >= CHANGE_CUT),
            "withheld_srf_days": withheld_srf, "withheld_rrp_days": withheld_rrp, "by_regime": by_regime}


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
    frame, notes, walk, tables, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
    _term_table, _net_table, ops = tables
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
    for label, members in take_up_members(frame, ops).items():
        groups.append((TAKE_UP, label, "decision", members))
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
        "notes": notes, "groups": {}, "skipped_groups": skipped, "take_up": coverage_of(frame, ops),
        "lead_difference": {"against_ann_net": m1273.lead_difference(frame, ANNNET, SAMEDAY), "ann_net_against_s3c": m1273.lead_difference(frame, S3C, ANNNET)},
        "effects": {str(h): m1321.effects(frame, walk, sdo.SAMEDAY_ARM.name, sdo.OPS_EXTRAS, h, ops.read, reps=args.reps) for h in LEADS},
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
    """The pooled means of the references here beside #1321's record, made at the same instant with the same machinery: they agree to rounding."""

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

    with m1321.decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    if not AVAILABILITY.exists():
        raise SystemExit(f"{AVAILABILITY.relative_to(REPO)} is missing: the availability is shown before any score")
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_sameday_ops_1349")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1349, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arms": list(ARMS), "references": list(REFERENCES), "margin_bp": s3c_candidate.MARGIN_BP,
        "availability": json.loads(AVAILABILITY.read_text(encoding="utf-8")),
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


def against_table(group: Mapping[str, object]) -> List[str]:
    out = [f"| {SHORT[SAMEDAY]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(SAMEDAY):
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, SAMEDAY, ref)) for m in TESTED) + " |")
    return out


def means_split_table(window: Mapping[str, object], split: str, metric: str) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(SHORT[m] for m in MODELS) + " |", "|---|---|" + "---|" * len(MODELS)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in MODELS) + " |")
    return out if len(out) > 2 else []


def effect_table(by_lead: Mapping[str, Mapping[str, dict]]) -> List[str]:
    terms = sdo.OPS_EXTRAS
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


def availability_table(block: Mapping[str, object]) -> List[str]:
    out = ["| | ON RRP | SRF |", "|---|---|---|"]
    a, b = block["on_rrp"], block["srf"]
    rows = (
        ("operation dates, " + a["first"] + " to " + a["last"], f"{a['operation_dates']:,}", f"{b['operation_dates']:,} (from {b['first']})"),
        ("public by 18:00 on their own day", f"{a['public_by_decision']:,} ({a['share_public']:.1%})", f"{b['public_by_decision']:,} ({b['share_public']:.1%})"),
        ("public by 16:00 (the reading of #442)", f"{a['public_by_16']:,}", f"{b['public_by_16']:,}"),
        ("median / 99th percentile / latest last write (New York hour of the day)",
         f"{a['write_hour_median']:.2f} / {a['write_hour_p99']:.2f} / {a['write_hour_max']:.2f}",
         f"{b['write_hour_median']:.2f} / {b['write_hour_p99']:.2f} / {b['write_hour_max']:.2f}"),
        ("minutes before 18:00 of the closest write among the public dates", f"{a['margin_minutes_of_closest_public_write']:.0f}",
         f"{b['margin_minutes_of_closest_public_write']:.0f}"),
        ("minutes from the stated close to the last write (median / 99th percentile)",
         f"{a['close_to_write_minutes']['median']:.1f} / {a['close_to_write_minutes']['p99']:.1f}",
         f"{b['close_to_write_minutes']['median']:.1f} / {b['close_to_write_minutes']['p99']:.1f}"),
        ("withheld (written after 18:00, or rewritten later)", ", ".join(f"{w['date']} ({w['last_write']})" for w in a["withheld"]) or "none",
         ", ".join(f"{w['date']} ({w['last_write']})" for w in b["withheld"]) or "none"),
    )
    for label, x, y in rows:
        out.append(f"| {label} | {x} | {y} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text}, grid CRPS of (s3c-ann-net-sameday) against (s3c-ann-net) {cell(_vs(entry, 'grid_crps', SAMEDAY, ANNNET))}; "
                     f"against (s3c) {cell(_vs(entry, 'grid_crps', SAMEDAY, S3C))}")
    return "; ".join(parts) + "."


def summary(r: Mapping[str, object]) -> List[str]:
    out = ["## Summary: grid CRPS of (s3c-ann-net-sameday), by lead", "",
           "Skill and its 90% interval, the mean difference d and its studentized 90% interval, and the reading on the mean-d bound (positive favours "
           "the arm). The full tables, with the other metrics, follow.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        out += [f"**{WINDOW_TITLES[window].split(' (')[0]}**", "", "| lead | against (s3c-ann-net) | against (s3c) |", "|---|---|---|"]
        for lead in LEADS:
            g = w["groups"]["lead"][f"h={lead}"]
            out.append(f"| h={lead} | {cell(_vs(g, 'grid_crps', SAMEDAY, ANNNET))} | {cell(_vs(g, 'grid_crps', SAMEDAY, S3C))} |")
        g = w["groups"]["pooled"]["all decision days"]
        out.append(f"| pooled over h = 1..5 | {cell(_vs(g, 'grid_crps', SAMEDAY, ANNNET))} | {cell(_vs(g, 'grid_crps', SAMEDAY, S3C))} |")
        out.append("")
    return out


def split_tables(w: Mapping[str, object], split: str, title: str) -> List[str]:
    out: List[str] = []
    for ref in plan(SAMEDAY):
        table = m1288.split_table(w, split, SAMEDAY, ref)
        if table:
            out += [f"### {title}: {SHORT[SAMEDAY]} against {SHORT[ref]}", ""] + table + [""]
    return out


def render(r: dict) -> str:
    a = r["availability"]
    out = [
        "# (s3c-ann-net-sameday): the decision day's own ON RRP and SRF take-up beside the candidate (s3c-ann-net), at the 18:00 decision (#1349)", "",
        "**Does the take-up of the day the forecast is made on improve the candidate?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, a development arm on the candidate (s3c-ann-net); ledger item 98, avenue #1337. "
        "**Development data, not a verdict** (scoring protocol v1, #640). Her ruling of 1 November 2026 (chat, relayed on #1337): use the same day and "
        "test it. **(s3c-ann-net) stays the candidate of avenue #1318 and (s3c) the H5 candidate; nothing here changes either.** Nothing is registered or "
        "published and no claim changes; the same-day reading enters no published declaration. Generated by `scripts/s3c_sameday_ops_1349.py page` from "
        f"`docs/research/s3c-sameday-ops-1349/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        "**What changed.** (s3c-ann-net) is (s3c) with its two settlement terms read at leads 2 to 5 from the auction announcement and sized by the net. "
        "(s3c-ann-net-sameday) adds three terms of the decision day itself, the day the forecast is made: the overnight Standing Repo Facility take-up "
        "as a 0/1 flag and in USD 100 bn, and the change in the ON RRP amount accepted from the previous panel day in USD 100 bn. They are the same "
        "three numbers at every lead of a decision. Everything else is (s3)'s, the SRF cap is (s3c)'s and the fit is on direct pairs. The references "
        "(s3c) and (s3c-ann-net) are re-run in the same run, at the 18:00 decision instant "
        f"(`repo_model.decision_instant`, pinned for the run: {r['decision_time']}).", "",
        "## Availability: are the decision day's results public before 18:00?", "",
        f"**{a['reading'].capitalize()}.** {a['rule']}. {a['caveat']}.", ""] + availability_table(a) + [
        "", "A date written after 18:00, or rewritten later (the Desk rewrote six ON RRP dates of 2018 to 2021 on 2023-09-27, for example), has no first publication "
        "time we can see; the arm reads it as no take-up, as `fed_liquidity` reads a withheld date. The terms are read per decision, from the records the "
        "Desk had written by that decision's 18:00 (`repo_model.same_day_operations`, leakage-tested in `tests/test_same_day_operations_1349.py`).", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours the arm. "
        "**A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a Brier score "
        "the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x "
        "after 2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days keep the **current method** "
        "(#1221 questions it and #1228 will decide); no reading of a group is a finding. Where the arm and a reference differ on few days of a group the "
        "bound may not be computed: the unstudentized interval of mean d is then given beside it, and no reading is taken from that. Groups of fewer than "
        "20 days are listed and not tested. The benchmarks are not part of this directive's comparisons.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test and by every study since #1229. This is a check on "
        "an arm queued by her ruling, not evidence for a verdict. SRF take-up is zero on most days before late 2025, so the terms act only where there "
        "is take-up; read the lead rows and the take-up split beside the pooled figure. A same-day take-up spike partly reflects the pressure the model is "
        "forecasting at lead 1, so a gain that sits at h = 1 and fades is not a gain at the leads the primary score averages.", ""]
    out += summary(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled, tu = w["notes"], w["groups"]["pooled"]["all decision days"], w["take_up"]
        ld = w["lead_difference"]["against_ann_net"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits. The decision day's SRF take-up is above "
                f"zero on {tu['srf_days']:,} of them, the ON RRP amount moved by USD 10 bn or more on {tu['rrp_moves']:,}; {tu['withheld_srf_days']} SRF "
                f"and {tu['withheld_rrp_days']} ON RRP days were withheld as written after 18:00. Cells on which the arm is not (s3c-ann-net) element for "
                f"element, by lead (of {ld['cells_per_lead']:,} each): " + ", ".join(f"h={h}: {ld['differing_cells'][str(h)]:,}" for h in LEADS) + ".", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled) + ["", f"### {LABELS[SAMEDAY]} against each reference (pooled)", ""] + against_table(pooled) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"),
                             (TAKE_UP, "By the decision day's own take-up")):
            out += split_tables(w, split, title)
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split, "b90_closed")
            if table:
                out += [f"### 90% band coverage by {title}", ""] + table + [""]
        out += ["### Where the terms act, by regime of the decision day", "", "| regime | decision days | SRF take-up days | mean size on those days (USD 100 bn) | ON RRP moves of USD 10 bn or more |",
                "|---|---|---|---|---|"]
        for regime, e in sorted(tu["by_regime"].items()):
            size = "n/a" if e["srf_mean_size_on_active_days"] is None else f"{e['srf_mean_size_on_active_days']:.3f}"
            out.append(f"| {regime} | {e['decision_days']} | {e['srf_days']} | {size} | {e['rrp_moves']} |")
        out += ["", "### The fitted effect of the three terms, by lead and regime of the target day", ""] + effect_table(w["effects"]) + [
            "", "The effect is the standardised effect of the refit the forecast used times the scale at the anchor in bp. The pooled row is printed at every "
            "lead and the regime rows at h = 3 only (the record holds them all). The interval is a bootstrap interval of the mean over decision days, which "
            "share refits; it is not a sampling interval for the coefficient. A term enters a fit only when at least three training pairs carry it.", ""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_1321"):
        out += ["## The references against #1321's record", "",
                "The references are re-run here with the machinery and at the instant of #1321's record; the pooled means should agree. Shown, not required "
                "to; no record is edited. Largest absolute difference of a pooled mean: "
                f"{max(abs(v['difference']) for ms in r['against_1321'].values() for rows in ms.values() for v in rows.values()):.1e}.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. Does the same-day reading enter a published declaration, or does the arm go back as a candidate?** The registry is not changed in this "
        "directive: `nyfed_repo_ops_sameday` and `nyfed_on_rrp_sameday` stay off in every published declaration, and the 18:00 availability above is "
        "development evidence. Whether to declare the same-day reading at the new decision instant is a data-meaning question, and so hers.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Leave the same-day reading off and (s3c-ann-net) as the candidate** (default). Nothing changes.",
        "2. **Draft a decision record** that declares the 18:00 same-day reading of the Desk's results as a source, for her review; no forecast changes with it.",
        "3. **Ask for a prospective test of the arm**, in a directive of its own, on the confirmation days only, under the scoring protocol.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("availability", help="show from the Desk's write times which operation dates are public by 18:00 on their own day")
    a.add_argument("--output", required=True)
    a.set_defaults(func=availability)
    s = sub.add_parser("score", help="walk the reference and the arm, cap them as (s3c) is capped, and score on both windows")
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
