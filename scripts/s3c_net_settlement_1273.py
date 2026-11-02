"""(s3c-net): (s3c) with net bill and net coupon settlement in place of the gross settlement flags, scored against (s3c), (s3), B1, B1' and B2
on both development windows of #1255 (#1273; H5 step 3; ledger item 65 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_net_settlement_1273.json`, which this script refuses to read unless it is committed and unchanged. The candidate is
`repo_model.s3c_net` (the two settlement terms of (s3) as the signed net of the target day in USD 100 bn, read at the decision instant from the
auctions the published panel builds from) capped as (s3c) is capped (`repo_model.s3c_candidate`, unchanged). The control is the same change of
form with the panel's gross sizes. The frames and the machinery are #1255's and are loaded as they are: the development window of #1145 and
#1241 (targets up to 2025-12-31) and the 2026 development days of #1229 (targets 2026-01-02 to 2026-09-03, the near-blind tier open since
GO #151). The blind tier and every lockbox day are refused by the frames' own guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009
ruling) with the skill interval beside, split by regime, pressure-day type, lead, target month, and by the decision days on which the changed term
is non-zero; reports the coverage of the central 90% band beside (s3c)'s; and reports the fitted effect of the changed terms in bp per USD 100 bn
of settlement, by regime.

Commands, from a clone of the branch (the walks are minutes and the paired tests are the longer part; a cloud run unless the measured time says
otherwise):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_net_settlement_1273.py score --panel PUB.csv --output docs/research/s3c-net-settlement-1273/result.json
    PYTHONPATH=src python3 scripts/s3c_net_settlement_1273.py page \\
        --score docs/research/s3c-net-settlement-1273/result.json --output docs/research/s3c-net-settlement-1273-result.md

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
    path = REPO / "scripts" / f"{name}.py"
    held = sys.modules.get(alias)
    if held is not None and getattr(held, "__file__", None) == str(path):
        return held  # another loader in this process already holds the alias: share it, so pickled task names stay one object (#1294)
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, data, metrics, net_settlement, policy_events, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mean_reversion as smr, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1255's script (and through it #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker pool's tasks does
#: not meet another test module's copy.
m1255 = _load("s3c_candidate_1255", "s3c_candidate_1255_in_1273")
k, d1222 = m1255.k, m1255.d1222
c, s686, s761, load_daily_panel = k.c, k.s686, k.s761, m1255.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_net_settlement_1273.json"
NET_DECLARATION = REPO / "metadata" / "net_settlement.json"
AUCTIONS = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "treasury_auctions"
SEED = 1273
LAST_DAY = EXPLORATORY_END
#: The last scored day of each window (the frames' own).
WINDOW_LAST = {"development": c.LAST_DAY, "2026": d1222.LAST_DAY}
S3, S3C = k.S3, m1255.S3C
S3CN, S3CG = "sc_s3c_net", "sc_s3c_gross"
B1P = k.B1P
BENCHMARKS = ("B1", B1P, "B2")
MODELS = BENCHMARKS + (S3, S3C, S3CG, S3CN)
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3: "(s3)", S3C: "(s3c)", S3CG: "(s3c-gross), the control", S3CN: "(s3c-net)"}
WINDOWS = m1255.WINDOWS
WINDOW_TITLES = m1255.WINDOW_TITLES
TESTED = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
METRIC_NAMES = TESTED + ("b90_closed",)
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)", "b90_closed": "90% band coverage"}
TAU = 5.0
BAND90 = k.d1145.BANDS["b90"]
MIN_GROUP_DAYS = k.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
EPSILON = 1e-9
TERMS = tuple(sc.SIZED_TERMS)
TERM_TITLES = {"settlement_bill": "net bill settlement", "settlement_coupon": "net coupon settlement"}
CHANGED = "changed_term"
CHANGED_LABELS = ("net bill or coupon settlement is not zero on the target day (lead 1)", "net settlement is zero on the target day (lead 1)")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What an arm is tested against: (s3c-net) against (s3c), (s3), the control and the benchmarks; the control against (s3c) for context."""

    if candidate == S3CN:
        return [S3C, S3, S3CG] + list(BENCHMARKS)
    if candidate == S3CG:
        return [S3C]
    return []


def load_auctions(path: Path = AUCTIONS) -> Tuple[net_settlement.Auction, ...]:
    """The auction records the published panel builds its gross settlement from, as `net_settlement.Auction`s."""

    files = sorted(p for p in Path(path).glob("*.json") if not p.name.endswith(".manifest.json"))
    if len(files) != 1:
        raise ValueError(f"{path}: expected exactly one auctions snapshot, found {len(files)}")
    return net_settlement.load_snapshot(files[0], net_settlement.load_declaration(NET_DECLARATION))


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def candidate_days(frame, window: str, first: Optional[date]) -> List[date]:
    """The decision days #1255's frame of `window` walks: every day whose five targets fall on or before the window's last day."""

    last = WINDOW_LAST[window]
    days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(frame.dates) and frame.dates[i + max(sp.HORIZONS)] <= last and (first is None or day >= first)
    ]
    s686.require_scored_days(days, last)
    return days


def extra_walks(window: str, frame, panel, splits, registry, table, auctions, first: Optional[date]):
    """The walks of (s3) with the net arm (net sizes) and with the control arm (the panel's gross sizes), over #1255's decision days.

    Raises:
        ValueError: a walk's (s3) forecast differs from the frame's on a scored decision day, or a scored decision day has no forecast.
    """

    days = candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    net_table = s3c_net.NetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    net = sc.walk(panel, days, table, states, (sc.ARMS[2], s3c_net.NET_ARM), sizes=net_table, **settings)
    gross = sc.walk(panel, days, table, states, (sc.ARMS[2], s3c_net.GROSS_ARM), sizes=sc.SizeTable(panel), **settings)
    for name, walk, arm in (("net", net, s3c_net.NET_ARM), ("gross", gross, s3c_net.GROSS_ARM)):
        for d in frame.days:
            if d not in walk.forecasts[arm.name]:
                raise ValueError(f"the {name} walk has no forecast of the scored decision day {d}")
            if walk.forecasts[S3][d] != frame.forecasts[S3][d]:
                raise ValueError(f"the {name} walk's (s3) differs from #1255's frame on {d}: the walks are not the same")
    return net, gross, net_table


def build(window: str, panel, splits, registry, table, register, auctions, first: Optional[date]):
    """`#1255`'s frame of `window` with (s3c-net) and the control added: `(frame, notes, net walk, gross walk, net table, cell_table, groups_fn)`."""

    frame, notes, _mine, cell_table_, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    net, gross, net_table = extra_walks(window, frame, panel, splits, registry, table, auctions, first)
    s3 = frame.forecasts[S3]
    arms = {
        S3CN: {d: net.forecasts[s3c_net.NET_ARM.name][d] for d in frame.days},
        S3CG: {d: gross.forecasts[s3c_net.GROSS_ARM.name][d] for d in frame.days},
    }
    forecasts = {name: frame.forecasts[name] for name in BENCHMARKS}
    forecasts[S3], forecasts[S3C] = s3, frame.forecasts[S3C]
    for name, raw in arms.items():
        forecasts[name] = m1255.s3c_forecasts(frame, register, raw)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    notes = dict(notes, refits_net=len(net.fits), refits_gross=len(gross.fits))
    return frame, notes, net, gross, net_table, cell_table_, groups_fn


def probability(q: Sequence[float], tau: float = TAU) -> float:
    """P(spread > tau) as `spread_mean_reversion.exceedance` reads it off the 23 quantiles: 1 - F(floor(tau) + 0.5)."""

    return smr.exceedance(q, tau)


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]], last_day: date) -> Dict[str, Dict[Tuple[date, int], float]]:
    """The scores of every (decision day, lead) cell of `forecasts`, after the days are checked: both losses, the Brier cell of P(> +5 bp) with
    the event strict and on whole basis points (`data.exceeds_bp`), and the closed hit of the central 90% band."""

    days = sorted(forecasts)
    cells = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), last_day)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in METRIC_NAMES}
    lo, hi = BAND90
    for (d, h), t in cells.items():
        q, y = forecasts[d][h], frame.outcome[t]
        out["grid_crps"][(d, h)] = sp.grid_crps(q, y)
        out["upper_tail_twcrps"][(d, h)] = sp.upper_tail_twcrps(q, y)
        out["brier_gt5"][(d, h)] = (probability(q) - (1.0 if data.exceeds_bp(y, TAU) else 0.0)) ** 2
        out["b90_closed"][(d, h)] = 1.0 if q[lo] <= y <= q[hi] else 0.0
    return out


# -- the checks ----------------------------------------------------------------------------------------------------------


def gross_check(frame, panel, auctions) -> dict:
    """The gross the net is built from against the panel's gross columns, on every scored target day; the days they differ on are counted."""

    gross = net_settlement.gross_by_day(auctions)
    rows = {row.date: row for row in panel}
    targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
    differ = []
    for t in targets:
        have = gross.get(t, {"treasury_settlement_bills": 0.0, "treasury_settlement_coupons": 0.0})
        for column in ("treasury_settlement_bills", "treasury_settlement_coupons"):
            if abs(float(rows[t].values.get(column) or 0.0) - have[column]) > 1e-6:
                differ.append({"date": t.isoformat(), "column": column})
    return {"target_days": len(targets), "differences": len(differ), "examples": differ[:5]}


def lead_difference(frame, base: str, other: str) -> dict:
    """The cells, by lead, on which `other` is not `base` element for element (the terms are read at lead 1 only)."""

    out: Dict[str, int] = {str(h): 0 for h in sp.HORIZONS}
    for d in frame.days:
        for h in sp.HORIZONS:
            if list(frame.forecasts[other][d][h]) != list(frame.forecasts[base][d][h]):
                out[str(h)] += 1
    return {"cells_per_lead": len(frame.days), "differing_cells": out}


def changed_term_days(frame, net_table) -> Tuple[List[date], List[date]]:
    """The decision days whose lead-1 target has a non-zero net bill or coupon settlement, and the others."""

    nonzero, zero = [], []
    for d in frame.days:
        sizes = net_table.read(1, frame.position[d])
        (nonzero if any(abs(v) > EPSILON for v in sizes.values()) else zero).append(d)
    return nonzero, zero


# -- the fitted effect ---------------------------------------------------------------------------------------------------


def effects(frame, walk, arm: sc.StateArm, table) -> Dict[str, dict]:
    """The fitted effect of each sized term in bp per USD 100 bn, by regime of the target day and pooled (mean over the scored decision days).

    For each decision day the effect is that of the refit the forecast used at lead 1 times the anchor's scale in bp (0 where the term was not in the fit,
    counted); the shift is that effect times the day's size in USD 100 bn, so the mean absolute shift on the days the term is non-zero is reported.
    Each mean carries the 90% stationary-bootstrap interval over decision days (an interval over days that share refits, not a sampling interval for the
    coefficient).
    """

    per_day: Dict[date, dict] = {}
    for d in frame.days:
        used = walk.fit_used[d]
        estimate = walk.estimates[used][arm.name][1]
        scale = float(walk.detail[d]["scale"])
        eff = s3c_net.bp_per_100bn(estimate, scale)
        size = table.read(1, frame.position[d])
        per_day[d] = {
            "regime": frame.regime(frame.target(d, 1)),
            **{t: eff.get(t, 0.0) for t in TERMS},
            **{f"in_fit_{t}": 1.0 if t in estimate.effect else 0.0 for t in TERMS},
            **{f"size_{t}": size.get(t, 0.0) / sc.SIZE_UNIT for t in TERMS},
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
        entry["mean_size_100bn"] = {t: sum(per_day[d][f"size_{t}"] for d in members) / len(members) for t in TERMS}
        total = sum(per_day[d][f"size_{t}"] for d in active for t in TERMS)
        entry["implied_bp_per_100bn_on_active_days"] = (sum(per_day[d]["shift"] for d in active) / total) if abs(total) > EPSILON else None
        out[name] = entry
    return out


# -- the groups and the tests --------------------------------------------------------------------------------------------


_STATE: Dict = {}


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def unstudentized(series, candidate: str, reference: str, members: Sequence[date]) -> dict:
    """Mean d and its 90% stationary-bootstrap percentile interval, for a group whose studentized bound cannot be computed. Not the protocol's
    interval; no reading is taken from it. `d = S(reference) - S(candidate)`, positive favours the candidate."""

    d = [series[reference][x] - series[candidate][x] for x in sorted(members)]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=BLOCK, seed=SEED, replications=_STATE["reps"])
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
            out[name]["unstudentized"] = unstudentized(series, candidate, name, days)
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def run_window(window: str, panel, splits, registry, table, register, auctions, args) -> dict:
    frame, notes, net, gross, net_table, _cells, groups_fn = build(window, panel, splits, registry, table, register, auctions, args.first)
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    nonzero, zero = changed_term_days(frame, net_table)
    cells = {m: cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = list(groups_fn(frame, labels, pressure))
    groups += [(CHANGED, CHANGED_LABELS[0], "lead1", nonzero), (CHANGED, CHANGED_LABELS[1], "lead1", zero)]
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
            for candidate in (S3CN, S3CG):
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "notes": notes, "refits": len(net.fits), "groups": {}, "skipped_groups": skipped,
        "gross_check": gross_check(frame, panel, auctions),
        "lead_difference": {"net_against_s3c": lead_difference(frame, S3C, S3CN), "gross_against_s3c": lead_difference(frame, S3C, S3CG)},
        "effects": {"net": effects(frame, net, s3c_net.NET_ARM, net_table), "gross": effects(frame, gross, s3c_net.GROSS_ARM, sc.SizeTable(panel))},
        "changed_term_days": {"non_zero": len(nonzero), "zero": len(zero)},
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


def against_1255(results: Mapping[str, dict]) -> dict:
    """(s3) and (s3c) pooled here against #1255's record: the walk and the frame are the same, so the means must agree."""

    path = REPO / "docs" / "research" / "s3c-candidate-1255" / "result.json"
    if not path.exists():
        return {}
    there = json.loads(path.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        a = there[window]["groups"]["pooled"]["all decision days"]
        b = result["groups"]["pooled"]["all decision days"]
        out[window] = {"record": str(path.relative_to(REPO)), "metrics": {
            m: {x: {"here": b[m]["means"][x], "there": a[m]["means"][x], "difference": b[m]["means"][x] - a[m]["means"][x]} for x in (S3, S3C)}
            for m in ("grid_crps", "upper_tail_twcrps")}}
    return out


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_net_settlement_1273")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = load_auctions()
    result: dict = {
        "issue": 1273, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": S3CN, "control": S3CG,
        "margin_bp": s3c_candidate.MARGIN_BP,
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, auctions, args)
    result["against_1255"] = against_1255(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def words(row: Optional[dict]) -> str:
    """The reading on the mean-d bound, in bold once; `identical` for a group the arms score alike on every day."""

    if row is not None and row.get("identical"):
        return "identical"
    text = k.reading_words(row)
    return text if text.startswith("**") else f"**{text}**"


def cell(row: Optional[dict]) -> str:
    return "n/a" if row is None else (k._fmt(row) if row.get("identical") else f"{k._fmt(row)}: {words(row)}")


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(candidate, {}).get(reference)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(f"{group[x]['means'][m]:.4f}" if x != "grid_crps" and x != "upper_tail_twcrps" else f"{group[x]['means'][m]:.3f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str) -> List[str]:
    out = [f"| {LABELS[candidate]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(candidate):
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
        out.append(f"| {label} | {g['days']} | " + " | ".join("not tested (fewer than 20 days)" if skipped else cell(_vs(g, m, candidate, reference)) for m in TESTED) + " |")
    return out if len(out) > 2 else []


def means_split_table(window: Mapping[str, object], split: str, metric: str) -> List[str]:
    """One metric's mean of (s3), (s3c), the control and (s3c-net) in each group of a split, tested or not."""

    labels = window["groups"].get(split, {})
    models = (S3, S3C, S3CG, S3CN)
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(LABELS[m] for m in models) + " |", "|---|---|" + "---|" * len(models)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in models) + " |")
    return out if len(out) > 2 else []


def effect_table(eff: Mapping[str, dict], title: str) -> List[str]:
    cols = [f"{TERM_TITLES[t]} (bp per USD 100 bn) [90%]" for t in TERMS]
    out = [f"| {title} | days | " + " | ".join(cols) + " | share of days in the fit | mean abs shift on active days (bp) | implied bp per USD 100 bn on active days |", "|---|---|" + "---|" * (len(TERMS) + 3)]
    for name in sorted(eff, key=lambda x: (x != "all", x)):
        e = eff[name]
        parts = []
        for t in TERMS:
            m = e[t]
            parts.append(f"{m['mean']:+.3f}" + (f" [{m['interval'][0]:+.3f}, {m['interval'][1]:+.3f}]" if "interval" in m else " (too few days)"))
        shift = "n/a" if e["mean_abs_shift_bp_on_active_days"] is None else f"{e['mean_abs_shift_bp_on_active_days']:.3f}"
        implied = "n/a" if e["implied_bp_per_100bn_on_active_days"] is None else f"{e['implied_bp_per_100bn_on_active_days']:+.3f}"
        share = " / ".join(f"{e[t]['share_in_fit']:.2f}" for t in TERMS)
        out.append(f"| {name} | {e['days']} | " + " | ".join(parts) + f" | {share} | {shift} | {implied} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text} (s3c-net) against (s3c), grid CRPS: {cell(_vs(entry, 'grid_crps', S3CN, S3C))}")
    return "; ".join(parts) + "."


def render(r: dict) -> str:
    out = [
        "# (s3c-net): net bill and net coupon settlement in place of the gross flags (#1273)", "",
        "**Does sizing the two settlement terms by what is new (the securities settling less those maturing) help (s3c)?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c); ledger item 65 on #1116. **Development data, not a verdict** "
        "(scoring protocol v1, #640). Her ruling of 27 October 2026 (chat, relayed on #1273): queue the four arms, one "
        "directive each. **(s3c) stays the candidate until she rules on this result.** Nothing is registered or published and no claim changes. "
        f"Generated by `scripts/s3c_net_settlement_1273.py page` from `docs/research/s3c-net-settlement-1273/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        "**What changed, and what the directive's wording leaves open.** (s3c) carries `settlement_coupon` and `settlement_bill` as 0/1 flags (1 when the "
        "gross settlement of the target day is above zero), not as sizes. (s3c-net) replaces the two by the signed NET settlement of the target day in units "
        "of USD 100 bn: the offerings less the announced publicly held maturing amount, the bill types and the coupon types separately "
        "(`repo_model.net_settlement`, #426; the SOMA leg cancels), read at the 16:00 decision of the day before at lead 1, the only lead at which the gross "
        "flags are read; the sign is kept. Everything else is (s3)'s (the other terms, the Huber fit, the ridge of 5, direct pairs) and the SRF cap is "
        "(s3c)'s. That makes two changes in each term at once, flag to size and gross to net. **The control (s3c-gross)** takes the first alone: the same "
        "signed sizes in USD 100 bn from the panel's gross settlement. Net against the control isolates gross against net; the control against (s3c) "
        "isolates flag against size. The control is a reference, not an arm.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "the arm named first in the table's heading. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the "
        "skill interval beside it; for a Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals "
        "of a group of target days keep the **current method** (the group's days, scattered, resampled in date order as if consecutive), which #1221 "
        "questions and #1228 will decide; no reading of a day-type group is a finding. Where two arms differ on few days of a group, some resamples have "
        "no long-run variance: the bound is then not computed, the unstudentized interval of mean d is given beside it, and no reading is taken from "
        "that. Groups of fewer than 20 days are listed with their means and not tested.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, by #1229, #1252 and #1255. This is a check "
        "on an arm queued by her ruling, not evidence for a verdict. The changed terms are read at lead 1 only, so the average over h = 1..5 dilutes them by about "
        "a fifth: read the lead-1 row and the non-zero-term days beside the pooled figure.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        g, ld = w["gross_check"], w["lead_difference"]["net_against_s3c"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits of (s3), {n['refits_net']} of the net walk. "
                f"The net the arm reads is built from the same auctions snapshot as the panel's gross columns: on {g['target_days']:,} scored target days they differ from the panel "
                f"on {g['differences']} (column, day) pairs. Cells on which (s3c-net) is not (s3c) element for element, by lead (of {ld['cells_per_lead']:,} each): "
                + ", ".join(f"h={h}: {ld['differing_cells'][str(h)]:,}" for h in sp.HORIZONS) + ". "
                f"Decision days with a non-zero net settlement on the lead-1 target: {w['changed_term_days']['non_zero']:,}; zero: {w['changed_term_days']['zero']:,}.", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled) + ["", "### (s3c-net) against each reference (pooled)", ""] + against_table(pooled, S3CN) + [""]
        out += ["### The control (s3c-gross) against (s3c) (pooled)", ""] + against_table(pooled, S3CG) + [""]
        for split, title in (("lead", "By lead"), (CHANGED, "By the changed term (decision days, lead 1)"), ("regime", "By regime"),
                             ("pressure_day_type", "By pressure-day type of the target day"), ("month", "By target month"),
                             ("target_day_type", "By calendar target-day type")):
            for ref in (S3C, S3, S3CG):
                table = split_table(w, split, S3CN, ref)
                if table:
                    out += [f"### {title}: (s3c-net) against {LABELS[ref]}", ""] + table + [""]
        for ref in BENCHMARKS:
            for split, title in (("regime", "By regime"), ("pressure_day_type", "By pressure-day type")):
                table = split_table(w, split, S3CN, ref)
                if table:
                    out += [f"### {title}: (s3c-net) against {LABELS[ref]}", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split, "b90_closed")
            if table:
                out += [f"### 90% band coverage by {title}, (s3c-net) beside (s3c)", ""] + table + [""]
        out += [f"### The fitted effect in bp per USD 100 bn, by regime of the target day", "",
                "(s3c-net), per USD 100 bn of NET settlement, lead 1:", ""] + effect_table(w["effects"]["net"], "regime") + [
                "", "The control (s3c-gross), per USD 100 bn of GROSS settlement, lead 1:", ""] + effect_table(w["effects"]["gross"], "regime") + [
                "", "The effect is the standardised effect of the refit the forecast used times the scale at the anchor in bp, so it is in bp per USD 100 bn. The interval "
                "is a bootstrap interval of the mean over decision days, which share refits; it is not a sampling interval for the coefficient. A term enters a fit only "
                "when at least three training pairs have a positive column; the share of days in the fit is shown for the bill and the coupon term. The implied figure is "
                "the sum of the shifts over the sum of the sizes on the days either term is non-zero, a ratio of the fitted location shifts to the settled amounts.", ""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_1255"):
        out += ["## Reproduction of #1255", ""]
        for window, rec in r["against_1255"].items():
            out += [f"{WINDOW_TITLES[window].split(' (')[0]}: pooled mean here against `{rec['record']}`: " + "; ".join(
                f"{METRIC_TITLES[m]}: " + ", ".join(f"{LABELS[x]} {v['here']:.6f} against {v['there']:.6f} (difference {v['difference']:+.2e})" for x, v in rows.items())
                for m, rows in rec["metrics"].items()) + ". The walk is the same one.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. How the arm should read the settlement terms.** The directive describes (s3c)'s settlement terms as sized by the gross settlement; in the tree they "
        "are 0/1 flags. This arm turns them into signed sizes in USD 100 bn so that a net figure keeps its sign and the effect can be stated per USD 100 bn. The control "
        "on the page separates the change of form from the change to net. Should a net FLAG (1 when the net is above zero) also be tried?", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **No: the sized form is the arm** (default). Nothing changes.",
        "2. **Add a flag version of the net as a further arm**, in a directive of its own.",
        "3. **Read the result on the control's terms**: take the sized gross form as the baseline for the other three arms.", "",
        "**Question 2. What follows from this result.** (s3c) stays the H5 candidate. Whether (s3c-net) replaces it, or the net terms are carried into the "
        "arms of the other three queued arms, is a choice for her, and it rests on days already seen.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests (s3c-net) prospectively**, on the confirmation days only, under the scoring protocol.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3) with the net and gross size arms, cap them as (s3c) is capped, and score on both windows")
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
