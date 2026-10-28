"""(s3c-ann) and (s3c-ann-net): (s3c) with its settlement terms read at leads 2 to 5 from the auction announcement, scored against (s3c), (s3),
(s3c-net), B1, B1' and B2 on both development windows of #1255 (#1288; H5 step 3; ledger item 71 on #1116; avenue #1286).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_announced_settlement_1288.json`, which this script refuses to read unless it is committed and unchanged. The arms are
`repo_model.s3c_announced`: (s3) with the coupon and bill settlement flags served at every lead from the announcement dating of
`metadata/settlement_announcement_dating.json` ((s3c-ann)), and (s3) with #1273's net settlement served the same way ((s3c-ann-net)), each capped
as (s3c) is capped (`repo_model.s3c_candidate`, unchanged). Two leg references admit one leg alone, so that the coupon and the bill leg are reported
separately. The frames and the machinery are #1255's and #1273's and are loaded as they are: the development window of #1145 and #1241 (targets
up to 2025-12-31) and the 2026 development days of #1229 (targets 2026-01-02 to 2026-09-03, the near-blind tier open since GO #151). The blind
tier and every lockbox day are refused by the frames' own guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009
ruling) with the skill interval beside, split by lead, regime, pressure-day type, target month, the settlement-day type of the target at each lead,
and by the decision days on which the announced term is non-zero; reports the coverage of the central 90% band beside (s3c)'s; and reports the
fitted effect of the settlement terms by lead and regime.

Commands, from a clone of the branch (the walks are minutes and the paired tests are the longer part; a cloud run unless the measured time says
otherwise):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_announced_settlement_1288.py score --panel PUB.csv \\
        --output docs/research/s3c-announced-settlement-1288/result.json
    PYTHONPATH=src python3 scripts/s3c_announced_settlement_1288.py page \\
        --score docs/research/s3c-announced-settlement-1288/result.json --output docs/research/s3c-announced-settlement-1288-result.md

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
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, data, metrics, net_settlement, policy_events, s3c_announced, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, settlement_dating, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1273's script (and through it #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker pool's tasks
#: does not meet another test module's copy.
m1273 = _load("s3c_net_settlement_1273", "s3c_net_settlement_1273_in_1288")
m1255, k = m1273.m1255, m1273.k
c, s686, s761, load_daily_panel = m1273.c, m1273.s686, m1273.s761, m1273.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_announced_settlement_1288.json"
DATING = REPO / "metadata" / "settlement_announcement_dating.json"
AUCTIONS = m1273.AUCTIONS
RECORD_1273 = REPO / "docs" / "research" / "s3c-net-settlement-1273" / "result.json"
SEED = 1288
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1273.WINDOW_LAST
S3, S3C, S3CN, B1P = m1273.S3, m1273.S3C, m1273.S3CN, m1273.B1P
ANN, ANNNET, ANNC, ANNB = "sc_s3c_ann", "sc_s3c_ann_net", "sc_s3c_ann_coupon", "sc_s3c_ann_bill"
BENCHMARKS = m1273.BENCHMARKS
MODELS = BENCHMARKS + (S3, S3C, S3CN, ANN, ANNNET, ANNC, ANNB)
ARMS = (ANN, ANNNET)
LEGS = (ANNC, ANNB)
LABELS = {
    "B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3: "(s3)", S3C: "(s3c)", S3CN: "(s3c-net) of #1273", ANN: "(s3c-ann)",
    ANNNET: "(s3c-ann-net)", ANNC: "(s3c-ann-coupon), the coupon leg", ANNB: "(s3c-ann-bill), the bill leg",
}
WINDOWS = m1273.WINDOWS
WINDOW_TITLES = m1273.WINDOW_TITLES
TESTED = m1273.TESTED
METRIC_NAMES = m1273.METRIC_NAMES
METRIC_TITLES = m1273.METRIC_TITLES
BAND90 = m1273.BAND90
MIN_GROUP_DAYS = m1273.MIN_GROUP_DAYS
BLOCK = m1273.BLOCK
EPSILON = 1e-9
TERMS = tuple(sc.SIZED_TERMS)
LEADS = tuple(sp.HORIZONS)
LONG_LEADS = tuple(h for h in LEADS if h >= 2)
#: The splits tested against every reference; the others (the settlement-day types and the announced-term days) are tested against the references
#: that bear on the question: (s3c), (s3c-net) and, for the net arm, (s3c-ann).
FULL_SPLITS = ("pooled", "lead", "regime", "pressure_day_type", "target_day_type", "month")
DAY_TYPE = "settlement_day_type"
ANNOUNCED = "announced_gross"
ANNOUNCED_NET = "announced_net"
TYPE_LABELS = ("coupon settlement day", "bill settlement day", "bill settlement day with a cash management bill",
               "bill settlement day without one", "neither settles")
#: The splits the page prints against (s3c), (s3c-net) and, for (s3c-ann-net), (s3c-ann) only; the record holds every pairing.
SHORT_SPLITS = ("regime", "pressure_day_type", "month", "target_day_type", DAY_TYPE)
FLAG_TITLES = {"settlement_bill": "bill flag", "settlement_coupon": "coupon flag"}
#: The effect tables print the pooled row at every lead and the regime rows at this lead only; the record holds them all.
REGIME_LEAD = "3"
NET_TITLES = {"settlement_bill": "net bill settlement", "settlement_coupon": "net coupon settlement"}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str, split: str = "pooled") -> List[str]:
    """What an arm is tested against: both arms against (s3c), (s3), (s3c-net) and the benchmarks, (s3c-ann-net) also against (s3c-ann);
    on the announced-term splits only against (s3c), (s3c-net) and, for (s3c-ann-net), (s3c-ann); a leg reference against (s3c) alone."""

    if candidate in LEGS:
        return [S3C]
    narrow = split in (ANNOUNCED, ANNOUNCED_NET)
    if candidate == ANN:
        return [S3C, S3CN] if narrow else [S3C, S3, S3CN] + list(BENCHMARKS)
    if candidate == ANNNET:
        return [S3C, S3CN, ANN] if narrow else [S3C, S3, S3CN, ANN] + list(BENCHMARKS)
    return []


def load_results(path: Path = AUCTIONS, declaration: Optional[dict] = None) -> Tuple[settlement_dating.AuctionResult, ...]:
    """The auction records the published panel builds its gross settlement from, dated by their announcement (#541)."""

    files = sorted(p for p in Path(path).glob("*.json") if not p.name.endswith(".manifest.json"))
    if len(files) != 1:
        raise ValueError(f"{path}: expected exactly one auctions snapshot, found {len(files)}")
    declaration = settlement_dating.load_result_dating(DATING) if declaration is None else declaration
    return settlement_dating.load_snapshot_results(files[0], declaration)


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def candidate_days(frame, window: str, first: Optional[date]) -> List[date]:
    """The decision days #1255's frame of `window` walks."""

    return m1273.candidate_days(frame, window, first)


def extra_walks(window: str, frame, panel, splits, registry, table, results, auctions, first: Optional[date]):
    """The walks of (s3c-ann) and (s3c-ann-net), of the two leg references and of #1273's (s3c-net), over #1255's decision days.

    Raises:
        ValueError: the (s3) of the (s3c-net) walk differs from the frame's on a scored decision day; an arm that must equal its reference at
            lead 1 does not; or a scored decision day has no forecast.
    """

    days = candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    both = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    walks = {
        "ann": sc.walk(panel, days, both, states, (s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM), sizes=net_table, **settings),
        "coupon": sc.walk(panel, days, s3c_announced.AnnouncedTermTable(panel, iorb, results, legs=("settlement_coupon",),
                                                                         decision_time=k.DECISION_TIME),
                          states, (s3c_announced.COUPON_ARM,), **settings),
        "bill": sc.walk(panel, days, s3c_announced.AnnouncedTermTable(panel, iorb, results, legs=("settlement_bill",),
                                                                       decision_time=k.DECISION_TIME),
                        states, (s3c_announced.BILL_ARM,), **settings),
        "net": sc.walk(panel, days, table, states, (sc.ARMS[2], s3c_net.NET_ARM),
                       sizes=s3c_net.NetSizeTable(panel, auctions, decision_time=k.DECISION_TIME), **settings),
    }
    arms = {"ann": s3c_announced.ANN_ARM.name, "coupon": s3c_announced.COUPON_ARM.name, "bill": s3c_announced.BILL_ARM.name,
            "net": s3c_net.NET_ARM.name}
    for name, walk in walks.items():
        for d in frame.days:
            if d not in walk.forecasts[arms[name]]:
                raise ValueError(f"the {name} walk has no forecast of the scored decision day {d}")
    for d in frame.days:
        if walks["net"].forecasts[S3][d] != frame.forecasts[S3][d]:
            raise ValueError(f"the (s3c-net) walk's (s3) differs from #1255's frame on {d}: the walks are not the same")
        at_one = frame.forecasts[S3][d][1]
        for name in ("ann", "coupon", "bill"):
            if walks[name].forecasts[arms[name]][d][1] != at_one:
                raise ValueError(f"the {name} arm is not (s3) at lead 1 on {d}: lead 1 reads the panel's flags as (s3c) does")
        if walks["ann"].forecasts[s3c_announced.ANN_NET_ARM.name][d][1] != walks["net"].forecasts[s3c_net.NET_ARM.name][d][1]:
            raise ValueError(f"(s3c-ann-net) is not (s3c-net) at lead 1 on {d}")
    return walks, both, net_table


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with the arms, the leg references and (s3c-net) added: `(frame, notes, walks, tables, cell_table, groups_fn)`."""

    frame, notes, _mine, cell_table_, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walks, term_table, net_table = extra_walks(window, frame, panel, splits, registry, table, results, auctions, first)
    raw = {
        S3CN: {d: walks["net"].forecasts[s3c_net.NET_ARM.name][d] for d in frame.days},
        ANN: {d: walks["ann"].forecasts[s3c_announced.ANN_ARM.name][d] for d in frame.days},
        ANNNET: {d: walks["ann"].forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in frame.days},
        ANNC: {d: walks["coupon"].forecasts[s3c_announced.COUPON_ARM.name][d] for d in frame.days},
        ANNB: {d: walks["bill"].forecasts[s3c_announced.BILL_ARM.name][d] for d in frame.days},
    }
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS}
    forecasts[S3], forecasts[S3C] = frame.forecasts[S3], frame.forecasts[S3C]
    for name, found in raw.items():
        forecasts[name] = m1255.s3c_forecasts(frame, register, found)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    notes = dict(notes, refits_ann=len(walks["ann"].fits), refits_net=len(walks["net"].fits))
    return frame, notes, walks, (term_table, net_table), cell_table_, groups_fn


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]], last_day: date):
    return m1273.cell_table(frame, forecasts, last_day)


# -- the checks ----------------------------------------------------------------------------------------------------------


def settlement_facts(panel, auctions) -> Dict[date, dict]:
    """The settlement-day type of every panel day: the panel's gross settlement above zero (coupon, bill), and whether a cash management bill
    settles that day (`net_settlement.Auction.cmb`)."""

    cmb = {a.settles for a in auctions if a.cmb}
    return {
        row.date: {
            "coupon": float(row.values.get("treasury_settlement_coupons") or 0.0) > 0.0,
            "bill": float(row.values.get("treasury_settlement_bills") or 0.0) > 0.0,
            "cmb": row.date in cmb,
        }
        for row in panel
    }


def day_type_members(frame, facts: Mapping[date, dict], lead: int) -> Dict[str, List[date]]:
    """The decision days whose lead-`lead` target is each settlement-day type (the types overlap: a day can settle both)."""

    out: Dict[str, List[date]] = {label: [] for label in TYPE_LABELS}
    for d in frame.days:
        f = facts[frame.target(d, lead)]
        if f["coupon"]:
            out[TYPE_LABELS[0]].append(d)
        if f["bill"]:
            out[TYPE_LABELS[1]].append(d)
            out[TYPE_LABELS[2] if f["cmb"] else TYPE_LABELS[3]].append(d)
        if not f["coupon"] and not f["bill"]:
            out[TYPE_LABELS[4]].append(d)
    return out


def announced_members(frame, term_table, net_table, lead: int) -> Tuple[Tuple[List[date], List[date]], Tuple[List[date], List[date]]]:
    """The decision days on which the announced term is non-zero at `lead` (a coupon or bill flag, then a non-zero net), and the others."""

    flagged, plain, net_on, net_off = [], [], [], []
    for d in frame.days:
        i = frame.position[d]
        flags = term_table.read(lead, i)
        (flagged if any(flags[t] for t in TERMS) else plain).append(d)
        sizes = net_table.read(lead, i)
        (net_on if any(abs(v) > EPSILON for v in sizes.values()) else net_off).append(d)
    return (flagged, plain), (net_on, net_off)


def announcement_check(frame, panel, results, facts: Mapping[date, dict], term_table, net_table) -> dict:
    """What the announcement dating gives on the scored target days.

    * `lead_1_differences`: the announced gross compared with the panel's gross columns on every scored target day (the dating declaration states they
      agree at lead 1); the (column, day) pairs that differ are counted.
    * `coverage`: per lead, the share of scored settlement target days (coupon, bill, bill with a cash management bill) whose flag is 1 at the
      decision, and the share of target days with a non-zero announced net.
    """

    by_day: Dict[date, List[settlement_dating.AuctionResult]] = {}
    for r in results:
        by_day.setdefault(r.settles, []).append(r)
    rows = {row.date: row for row in panel}
    targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
    differ = []
    for t in targets:
        for term, column in s3c_announced.COLUMN.items():
            announced = sum(r.amount for r in by_day.get(t, ()) if r.column == column)
            if abs(float(rows[t].values.get(column) or 0.0) - announced) > 1e-6:
                differ.append({"date": t.isoformat(), "column": column})
    coverage: Dict[str, dict] = {}
    for lead in LEADS:
        counts = {"coupon_days": 0, "coupon_announced": 0, "bill_days": 0, "bill_announced": 0, "cmb_days": 0, "cmb_announced": 0,
                  "net_days": 0, "net_non_zero": 0}
        for d in frame.days:
            t = frame.target(d, lead)
            flags = term_table.read(lead, frame.position[d])
            f = facts[t]
            if f["coupon"]:
                counts["coupon_days"] += 1
                counts["coupon_announced"] += flags["settlement_coupon"]
            if f["bill"]:
                counts["bill_days"] += 1
                counts["bill_announced"] += flags["settlement_bill"]
                if f["cmb"]:
                    counts["cmb_days"] += 1
                    counts["cmb_announced"] += flags["settlement_bill"]
            if f["coupon"] or f["bill"]:
                counts["net_days"] += 1
                counts["net_non_zero"] += any(abs(v) > EPSILON for v in net_table.read(lead, frame.position[d]).values())
        coverage[str(lead)] = counts
    return {"target_days": len(targets), "lead_1_differences": len(differ), "examples": differ[:5], "coverage": coverage}


def lead_difference(frame, base: str, other: str) -> dict:
    return m1273.lead_difference(frame, base, other)


# -- the fitted effect ---------------------------------------------------------------------------------------------------


def effects(frame, walk, arm: sc.StateArm, lead: int, read, *, unit: float = 1.0) -> Dict[str, dict]:
    """The fitted effect of each settlement term in bp at `lead`, by regime of the target day and pooled (mean over the scored decision days).

    For each decision day the effect is that of the refit the forecast used at `lead` times the anchor's scale in bp (0 where the term was not in
    the fit, counted). `read(lead, index)` gives the term's value on the day's target (a 0/1 flag, or a net in USD billions with `unit` 100, so
    that the effect is per USD 100 bn). The shift is that effect times the value, so the mean absolute shift on the days the term is non-zero is
    reported. Each mean carries the 90% stationary-bootstrap interval over decision days (an interval over days that share refits, not a sampling
    interval for the coefficient).
    """

    per_day: Dict[date, dict] = {}
    for d in frame.days:
        used = walk.fit_used[d]
        estimate = walk.estimates[used][arm.name][lead]
        scale = float(walk.detail[d]["scale"])
        eff = s3c_net.bp_per_100bn(estimate, scale)
        size = read(lead, frame.position[d])
        per_day[d] = {
            "regime": frame.regime(frame.target(d, lead)),
            **{t: eff.get(t, 0.0) for t in TERMS},
            **{f"in_fit_{t}": 1.0 if t in estimate.effect else 0.0 for t in TERMS},
            **{f"size_{t}": size.get(t, 0.0) / (unit if unit else 1.0) for t in TERMS},
        }
        per_day[d]["shift"] = sum(per_day[d][t] * per_day[d][f"size_{t}"] for t in TERMS)
    groups: Dict[str, List[date]] = {"all": list(frame.days)}
    for d, row in per_day.items():
        groups.setdefault(row["regime"], []).append(d)
    out: Dict[str, dict] = {}
    for name, members in groups.items():
        members = sorted(members)
        entry: dict = {"days": len(members)}
        for t in TERMS:
            values = [per_day[d][t] for d in members]
            entry[t] = {"mean": sum(values) / len(values), "share_in_fit": sum(per_day[d][f"in_fit_{t}"] for d in members) / len(members)}
            if len(values) >= MIN_GROUP_DAYS:
                low, high = metrics.stationary_bootstrap_interval(
                    lambda idx, v=values: sum(v[i] for i in idx) / len(idx), len(values), block_length=BLOCK, seed=SEED, replications=2000)
                entry[t]["interval"] = [low, high]
        active = [d for d in members if any(abs(per_day[d][f"size_{t}"]) > EPSILON for t in TERMS)]
        entry["active_days"] = len(active)
        entry["mean_abs_shift_bp_on_active_days"] = sum(abs(per_day[d]["shift"]) for d in active) / len(active) if active else None
        out[name] = entry
    return out


# -- the groups and the tests --------------------------------------------------------------------------------------------


_STATE: Dict = {}


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
            out[name]["unstudentized"] = m1273.unstudentized(series, candidate, name, days)
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, walks, (term_table, net_table), _cells, groups_fn = build(
        window, panel, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    facts = settlement_facts(panel, auctions)
    cells = {m: cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = list(groups_fn(frame, labels, pressure))
    announced_counts: Dict[str, dict] = {}
    for lead in LONG_LEADS:
        for label, members in day_type_members(frame, facts, lead).items():
            groups.append((DAY_TYPE, f"h={lead}: {label}", f"lead{lead}", members))
        (flagged, plain), (net_on, net_off) = announced_members(frame, term_table, net_table, lead)
        groups += [
            (ANNOUNCED, f"h={lead}: a coupon or bill settlement announced on the target", f"lead{lead}", flagged),
            (ANNOUNCED, f"h={lead}: none announced", f"lead{lead}", plain),
            (ANNOUNCED_NET, f"h={lead}: a non-zero announced net on the target", f"lead{lead}", net_on),
            (ANNOUNCED_NET, f"h={lead}: net zero or not announced", f"lead{lead}", net_off),
        ]
        announced_counts[str(lead)] = {"gross_announced": len(flagged), "none_announced": len(plain), "net_non_zero": len(net_on),
                                       "net_zero": len(net_off)}
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
            for candidate in ARMS + LEGS:
                if candidate in LEGS and split in (ANNOUNCED, ANNOUNCED_NET):
                    continue
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    result: dict = {
        "notes": notes, "refits": len(walks["ann"].fits), "groups": {}, "skipped_groups": skipped,
        "announcement_check": announcement_check(frame, panel, results, facts, term_table, net_table),
        "lead_difference": {
            "ann_against_s3c": lead_difference(frame, S3C, ANN), "ann_net_against_s3c": lead_difference(frame, S3C, ANNNET),
            "ann_net_against_s3c_net": lead_difference(frame, S3CN, ANNNET),
            "coupon_against_s3c": lead_difference(frame, S3C, ANNC), "bill_against_s3c": lead_difference(frame, S3C, ANNB),
        },
        "effects": {
            "ann": {str(h): effects(frame, walks["ann"], s3c_announced.ANN_ARM, h, term_table.read) for h in LEADS},
            "ann_net": {str(h): effects(frame, walks["ann"], s3c_announced.ANN_NET_ARM, h, net_table.read, unit=sc.SIZE_UNIT) for h in LEADS},
            "coupon_leg": {str(h): effects(frame, walks["coupon"], s3c_announced.COUPON_ARM, h,
                                           lambda lead, i: {"settlement_coupon": term_table.read(lead, i)["settlement_coupon"]})
                           for h in LONG_LEADS},
            "bill_leg": {str(h): effects(frame, walks["bill"], s3c_announced.BILL_ARM, h,
                                         lambda lead, i: {"settlement_bill": term_table.read(lead, i)["settlement_bill"]})
                         for h in LONG_LEADS},
        },
        "announced_days": announced_counts,
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


def against_records(results: Mapping[str, dict]) -> dict:
    """(s3), (s3c) here against #1255's record and (s3c-net) here against #1273's: the walks are the same, so the pooled means must agree."""

    out: Dict[str, dict] = {}
    for key, path, models in (("1255", REPO / "docs" / "research" / "s3c-candidate-1255" / "result.json", (S3, S3C)),
                              ("1273", RECORD_1273, (S3, S3C, S3CN))):
        if not path.exists():
            continue
        there = json.loads(path.read_text(encoding="utf-8"))["windows"]
        for window, result in results.items():
            a = there[window]["groups"]["pooled"]["all decision days"]
            b = result["groups"]["pooled"]["all decision days"]
            out.setdefault(key, {})[window] = {"record": str(path.relative_to(REPO)), "metrics": {
                m: {x: {"here": b[m]["means"][x], "there": a[m]["means"][x], "difference": b[m]["means"][x] - a[m]["means"][x]} for x in models}
                for m in ("grid_crps", "upper_tail_twcrps")}}
    return out


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_announced_settlement_1288")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = load_results()
    result: dict = {
        "issue": 1288, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "arms": list(ARMS), "legs": list(LEGS),
        "margin_bp": s3c_candidate.MARGIN_BP, "dating": json.loads(DATING.read_text(encoding="utf-8"))["available_time"],
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args)
    result["against_records"] = against_records(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def words(row: Optional[dict]) -> str:
    return m1273.words(row)


def cell(row: Optional[dict]) -> str:
    return m1273.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1273._vs(group, metric, candidate, reference)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str, split: str = "pooled") -> List[str]:
    out = [f"| {LABELS[candidate]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(candidate, split):
        out.append(f"| {LABELS[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, candidate: str, reference: str, order: Optional[Sequence[str]] = None) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|---|" + "---|" * len(TESTED)]
    for label in (order if order is not None else sorted(labels)):
        if label not in labels:
            continue
        g = labels[label]
        skipped = f"{split}/{label}" in window["skipped_groups"]
        out.append(f"| {label} | {g['days']} | " + " | ".join(
            "not tested (fewer than 20 days)" if skipped else cell(_vs(g, m, candidate, reference)) for m in TESTED) + " |")
    return out if len(out) > 2 else []


def means_split_table(window: Mapping[str, object], split: str, metric: str, models: Sequence[str] = (S3, S3C, S3CN, ANN, ANNNET)) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(LABELS[m] for m in models) + " |", "|---|---|" + "---|" * len(models)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in models) + " |")
    return out if len(out) > 2 else []


def lead_rows(window: Mapping[str, object], candidate: str, reference: str) -> List[str]:
    """One row per lead: the arm against the reference on the three metrics, from the `lead` split."""

    return split_table(window, "lead", candidate, reference)


def coverage_table(check: Mapping[str, object]) -> List[str]:
    out = ["| lead | coupon settlement days | coupon announced | bill settlement days | bill announced | with a cash management bill | cash management bill announced | settlement days | non-zero announced net |",
           "|---|---|---|---|---|---|---|---|---|"]
    for lead in LEADS:
        n = check["coverage"][str(lead)]

        def share(a: int, b: int) -> str:
            return f"{a} ({a / b:.0%})" if b else "0"

        out.append(f"| h={lead} | {n['coupon_days']} | {share(n['coupon_announced'], n['coupon_days'])} | {n['bill_days']} | "
                   f"{share(n['bill_announced'], n['bill_days'])} | {n['cmb_days']} | {share(n['cmb_announced'], n['cmb_days'])} | "
                   f"{n['net_days']} | {share(n['net_non_zero'], n['net_days'])} |")
    return out


def effect_table(by_lead: Mapping[str, Mapping[str, dict]], titles: Mapping[str, str], unit: str) -> List[str]:
    cols = [f"{titles[t]} ({unit}) [90%]" for t in TERMS]
    out = ["| lead | regime | days | " + " | ".join(cols) + " | share of days in the fit (bill / coupon) | mean abs shift on active days (bp) |",
           "|---|---|---|" + "---|" * (len(TERMS) + 2)]
    for lead in sorted(by_lead, key=int):
        eff = by_lead[lead]
        for name in sorted(eff, key=lambda x: (x != "all", x)):
            if name != "all" and lead != REGIME_LEAD:
                continue
            e = eff[name]
            parts = []
            for t in TERMS:
                m = e[t]
                parts.append(f"{m['mean']:+.3f}" + (f" [{m['interval'][0]:+.3f}, {m['interval'][1]:+.3f}]" if "interval" in m else " (too few days)"))
            shift = "n/a" if e["mean_abs_shift_bp_on_active_days"] is None else f"{e['mean_abs_shift_bp_on_active_days']:.3f}"
            share = " / ".join(f"{e[t]['share_in_fit']:.2f}" for t in TERMS)
            out.append(f"| h={lead} | {name} | {e['days']} | " + " | ".join(parts) + f" | {share} | {shift} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(
            f"{text}, grid CRPS against (s3c): (s3c-ann) {cell(_vs(entry, 'grid_crps', ANN, S3C))}; "
            f"(s3c-ann-net) {cell(_vs(entry, 'grid_crps', ANNNET, S3C))}")
    return "; ".join(parts) + "."


def summary(r: Mapping[str, object]) -> List[str]:
    """The first screen: grid CRPS against (s3c) by lead for each arm and leg reference, in each window."""

    out = ["## Summary: grid CRPS against (s3c), by lead", "",
           "Skill and its 90% interval, the mean difference d and its studentized 90% interval, and the reading on the mean-d bound (positive favours "
           "the arm). The lead-1 row is (s3c)'s own cell for the gross arm and the leg references (identical) and (s3c-net)'s for the net arm. "
           "The full tables, with the other metrics and references, follow.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        out += [f"**{WINDOW_TITLES[window].split(' (')[0]}**", "",
                "| lead | " + " | ".join(LABELS[x] for x in (ANN, ANNNET, ANNC, ANNB)) + " |", "|---|---|---|---|---|"]
        for lead in LEADS:
            g = w["groups"]["lead"][f"h={lead}"]
            out.append(f"| h={lead} | " + " | ".join(cell(_vs(g, "grid_crps", x, S3C)) for x in (ANN, ANNNET, ANNC, ANNB)) + " |")
        g = w["groups"]["pooled"]["all decision days"]
        out.append("| pooled over h = 1..5 | " + " | ".join(cell(_vs(g, "grid_crps", x, S3C)) for x in (ANN, ANNNET, ANNC, ANNB)) + " |")
        out.append("")
    return out


def render(r: dict) -> str:
    out = [
        "# (s3c-ann) and (s3c-ann-net): the settlement terms of (s3c) read at leads 2 to 5 from the auction announcement (#1288)", "",
        "**Does letting (s3c) see a settlement that was announced days earlier help at leads 2 to 5?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c); ledger item 71 on #1116, avenue #1286. **Development data, "
        "not a verdict** (scoring protocol v1, #640). Her ruling of 28 October 2026 (chat, relayed on #1288): test avenue #1286. **(s3c) stays the "
        "candidate until she rules on this result.** Nothing is registered or published and no claim changes: `metadata/sources.json`, the "
        "published declaration, `metadata/settlement_announcement_dating.json` and `docs/decisions/information-set.md` are unchanged, and the "
        "announcement dating stays off in every published declaration. Generated by `scripts/s3c_announced_settlement_1288.py page` from "
        f"`docs/research/s3c-announced-settlement-1288/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        "**What changed.** (s3c)'s two settlement terms are scheduled fields of the target row and are public at 15:00 on the panel day before it settles "
        "(`metadata/sources.json`), so (s3c) reads them at lead 1 only. The arms read them at leads 2 to 5 too, dated from the auction announcement "
        f"({r['dating']} New York time on the `announcemt_date`, #541, ruled by Eleonora on 10 October 2026 and not in force): at lead h the term of "
        "target day T is read from what had been announced by 16:00 on the panel day h rows before T. **(s3c-ann)** keeps the two 0/1 flags (1 when the "
        "announced offerings of the leg settling on T are above zero). **(s3c-ann-net)** sizes the two terms by #1273's net settlement (the offerings "
        "less the announced publicly held maturing amount, in units of USD 100 bn, the sign kept; a class announced only in part reads 0 until fully "
        "announced). Everything else is (s3)'s and the SRF cap is (s3c)'s. At lead 1 the arms are (s3c) and (s3c-net) cell for cell (checked for every "
        "scored decision day), so any difference sits at h = 2 to 5. **The legs are reported separately** by two reference walks, not arms: "
        "(s3c-ann-coupon) announces the coupon flag alone and (s3c-ann-bill) the bill flag alone.", "",
        "**The bill leg carries Lens E's caveat** (`docs/reviews/2026-10-19-five-lens/lens-E-data-plumbing.md`, item G). Treasury publishes no clock time "
        "for an announcement, and the 12:00 announcement time of a cash management bill is unverified: a cash management bill is ad hoc, announced the "
        "same or the previous day, sometimes auctioned at 11:30 and settled at T+0 or T+1. If one is announced after 12:00 the arm counts it too early, "
        "and the bill leg's gain at h = 2 to 5 would be read from information a desk did not yet have. An announcement dated before the decision "
        "day counts whatever its clock time; one dated the decision day itself counts only if it was made by 16:00, which the 12:00 stamp assumes "
        "(any stamp from 12:00 to 15:59 gives the same sums). The page does not measure how many flags hang on a same-day announcement. The "
        "settlement-day-type tables below separate the bill settlement days with a cash management bill from those without one.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "the arm named first in the table's heading. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the "
        "skill interval beside it; for a Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals "
        "of a group of target days keep the **current method** (the group's days, scattered, resampled in date order as if consecutive), which #1221 "
        "questions and #1228 will decide; no reading of a day-type group is a finding. Where two arms differ on few days of a group, some resamples have "
        "no long-run variance: the bound is then not computed, the unstudentized interval of mean d is given beside it, and no reading is taken from "
        "that. Groups of fewer than 20 days are listed with their means and not tested. The announced-term splits are tested against (s3c) and "
        "(s3c-net) (and (s3c-ann) for the net arm) only; every other split against every reference, the benchmarks included. For length, the page "
        "prints the regime, pressure-day-type, month, calendar-day-type and settlement-day-type splits against (s3c) and (s3c-net) (and (s3c-ann) "
        "for the net arm) and the benchmark tables for the lead, settlement-day-type, regime and pressure-day-type splits; the other pairings are "
        "in the record.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, by #1229, #1252, #1255 and #1273. This is a check "
        "on an arm queued by her ruling, not evidence for a verdict. The announced terms act at h = 2 to 5 only: the pooled figure averages four leads "
        "that can differ with one that cannot, so read the lead rows beside it.", ""]
    out += summary(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        a, ld = w["announcement_check"], w["lead_difference"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits of each arm's walk. "
                f"At lead 1 the announced gross settlement and the panel's gross columns differ on {a['lead_1_differences']} (column, day) pairs of "
                f"{a['target_days']:,} scored target days. Cells on which an arm is not (s3c) element for element, by lead (of {ld['ann_against_s3c']['cells_per_lead']:,} each): "
                f"(s3c-ann): " + ", ".join(f"h={h}: {ld['ann_against_s3c']['differing_cells'][str(h)]:,}" for h in sp.HORIZONS) + "; "
                f"(s3c-ann-net): " + ", ".join(f"h={h}: {ld['ann_net_against_s3c']['differing_cells'][str(h)]:,}" for h in sp.HORIZONS) + ".", "",
                "### How much of the settlement is announced by the decision", "",
                "Scored decision days whose lead-h target is a settlement day, and how many of them the announcement dating shows by the 16:00 decision "
                "(a flag of 1 or, for the net, a non-zero figure). At h = 1 every one is shown.", ""] + coverage_table(a) + [
                "", "### Mean scores (pooled)", ""] + mean_table(pooled)
        for arm in ARMS:
            out += ["", f"### {LABELS[arm]} against each reference (pooled)", ""] + against_table(pooled, arm) + [""]
        out += ["### The leg references against (s3c) (pooled)", ""]
        for leg in LEGS:
            out += against_table(pooled, leg) + [""]
        for split, title in (("lead", "By lead"), (DAY_TYPE, "By the settlement-day type of the target at each lead"),
                             (ANNOUNCED, "By the decision days on which a settlement is announced (gross flag)"),
                             (ANNOUNCED_NET, "By the decision days on which a non-zero net is announced"),
                             ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"),
                             ("month", "By target month"), ("target_day_type", "By calendar target-day type")):
            for arm in ARMS:
                shown = [x for x in plan(arm, split) if x not in BENCHMARKS]
                if split in SHORT_SPLITS:
                    shown = [x for x in shown if x in (S3C, S3CN) or (arm == ANNNET and x == ANN)]
                for ref in shown:
                    table = split_table(w, split, arm, ref)
                    if table:
                        out += [f"### {title}: {LABELS[arm]} against {LABELS[ref]}", ""] + table + [""]
            if split in ("lead", DAY_TYPE):
                for leg in LEGS:
                    table = split_table(w, split, leg, S3C)
                    if table:
                        out += [f"### {title}: {LABELS[leg]} against {LABELS[S3C]}", ""] + table + [""]
        for ref in BENCHMARKS:
            for arm in ARMS:
                for split, title in (("lead", "By lead"), (DAY_TYPE, "By settlement-day type"), ("regime", "By regime"),
                                     ("pressure_day_type", "By pressure-day type")):
                    table = split_table(w, split, arm, ref)
                    if table:
                        out += [f"### {title}: {LABELS[arm]} against {LABELS[ref]}", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split, "b90_closed")
            if table:
                out += [f"### 90% band coverage by {title}, the arms beside (s3c)", ""] + table + [""]
        out += ["### The fitted effect, by lead and regime of the target day", "",
                "(s3c-ann), bp when the flag is 1:", ""] + effect_table(w["effects"]["ann"], FLAG_TITLES, "bp") + [
                "", "(s3c-ann-net), bp per USD 100 bn of net settlement:", ""] + effect_table(w["effects"]["ann_net"], NET_TITLES, "bp per USD 100 bn") + [
                "", "The coupon leg alone ((s3c-ann-coupon)), bp when the coupon flag is 1:", ""] + effect_table(
                    w["effects"]["coupon_leg"], FLAG_TITLES, "bp") + [
                "", "The bill leg alone ((s3c-ann-bill)), bp when the bill flag is 1:", ""] + effect_table(w["effects"]["bill_leg"], FLAG_TITLES, "bp") + [
                "", "The effect is the standardised effect of the refit the forecast used times the scale at the anchor in bp. The pooled row is printed at every lead "
                "and the regime rows at h = 3 only (the record holds them all). The interval is a bootstrap interval of the "
                "mean over decision days, which share refits; it is not a sampling interval for the coefficient. A term enters a fit only when at least three "
                "training pairs carry it; the share of days in the fit is shown for the bill and the coupon term (a term of the other leg in a leg-reference walk is "
                "not in its fit at h = 2 to 5 and reads 0 there).", ""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_records"):
        out += ["## Reproduction of #1255 and #1273", ""]
        for key, windows in r["against_records"].items():
            for window, rec in windows.items():
                out += [f"{WINDOW_TITLES[window].split(' (')[0]}: pooled mean here against `{rec['record']}`: " + "; ".join(
                    f"{METRIC_TITLES[m]}: " + ", ".join(f"{LABELS[x]} {v['here']:.6f} against {v['there']:.6f} (difference {v['difference']:+.2e})" for x, v in rows.items())
                    for m, rows in rec["metrics"].items()) + ". The walk is the same one.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. The announcement dating.** These arms read `metadata/settlement_announcement_dating.json`, which is measured and off. Turning it on "
        "in the published declaration is her decision, on `docs/decisions/information-set.md` and on `metadata/sources.json`, which the final-test "
        "pre-registration freezes. Nothing here asks for it, and no result on this page is a reason to.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Leave the dating off** (default). Nothing changes.",
        "2. **Ask for a prospective test of the dating**, in a directive of its own, on the confirmation days only.", "",
        "**Question 2. The bill leg.** The 12:00 announcement time of a cash management bill is unverified (Lens E, item G). Should the bill leg be "
        "dropped, or read only for the regular bills, if the dating is ever used?", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Keep both legs and the caveat** (default).",
        "2. **Read the coupon leg alone** until the clock time of a cash management bill announcement can be verified.", "",
        "**Question 3. What follows from this result.** (s3c) stays the H5 candidate. Whether either arm replaces it rests on days already seen.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests the better arm prospectively**, on the confirmation days only, under the scoring protocol.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3) with the announced arms, cap them as (s3c) is capped, and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of the unstudentized interval")
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
