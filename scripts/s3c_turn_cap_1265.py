"""(s3c-t): (s3c) with the cap off on turn days, scored against (s3), (s3c), B1, B1' and B2 on every decision day since full allotment, the days
of 24 to 30 December 2025 included (#1265; H5 step 3; findings #1261 and #1264; ledger item 62 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_turn_cap_1265.json`, which this script refuses to read unless it is committed and unchanged. The candidate is
`repo_model.s3c_turn_cap` (the cap of `repo_model.s3c_candidate` left off on a target day whose reporting type is a turn); (s3c) is
`repo_model.s3c_candidate`. The frame is one contiguous run of decision days from 2025-12-10 to the last whose five targets fall on or before
2026-09-03 (the near-blind tier open since GO #151), so the decision days of 24 to 30 December 2025, which are in neither of #1255's windows,
are scored. The walk of (s3) is #1229's and #1255's (every decision day from the start of the panel, refit every 21 decision days): on the
decision days both score, (s3) is the same forecast, and the page compares the pooled means with #1255's record. The blind tier and every
lockbox day are refused by the frame's guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp) and P(> +10 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009
ruling) with the skill interval beside, split by turn days and other days, by pressure-day type, by lead and by month; and lists every target day
on which SOFR - IORB closed above +5 or +10 bp with each model's probabilities.

Commands, from a clone of the branch (the full run is minutes of walk and the paired tests; a cloud run unless the measured time says
otherwise):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_turn_cap_1265.py score --panel PUB.csv --output docs/research/s3c-turn-cap-1265/result.json
    PYTHONPATH=src python3 scripts/s3c_turn_cap_1265.py page \\
        --score docs/research/s3c-turn-cap-1265/result.json --output docs/research/s3c-turn-cap-1265-result.md

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


from repo_model import announced_iorb, b1_calendar as b1c, data, metrics, policy_events, s3c_candidate, s3c_turn_cap  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mean_reversion as smr, spread_mr_calendar as cal, spread_mr_state_calendar as sc, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

#: #1255's script (and through it #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker pool's tasks does
#: not meet another test module's copy.
m1255 = _load("s3c_candidate_1255", "s3c_candidate_1255_in_1265")
k, d1222 = m1255.k, m1255.d1222
c, s686, s761, load_daily_panel = k.c, k.s686, k.s761, m1255.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_turn_cap_1265.json"
RECORD_1255 = REPO / "docs" / "research" / "s3c-candidate-1255" / "result.json"
SEED = 1265
LAST_DAY = EXPLORATORY_END
#: The first decision day scored: the day the removal of the aggregate limit was announced (`standing_repo-20251210`, 14:00), the last
#: decision day before the first target at full allotment (2025-12-11). A study constant of the directive, not read by the candidate.
FIRST_DECISION = date(2025, 12, 10)
#: The decision days of 24 to 30 December 2025, which are in neither window of #1255.
GAP_FIRST, GAP_LAST = date(2025, 12, 24), date(2025, 12, 30)
#: The first decision day of #1255's 2026 window (its first target is 2026-01-02).
WINDOW_2026_FIRST = date(2025, 12, 31)
S3, S3C, S3CT = k.S3, m1255.S3C, "sc_s3c_turn"
B1P = k.B1P
BENCHMARKS = ("B1", B1P, "B2")
ARMS = (S3, S3C, S3CT)
MODELS = BENCHMARKS + ARMS
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3: "(s3)", S3C: "(s3c)", S3CT: "(s3c-t)"}
METRIC_NAMES = ("grid_crps", "upper_tail_twcrps", "brier_gt5", "brier_gt10")
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)", "brier_gt10": "Brier P(> +10 bp)"}
TAUS = {"brier_gt5": 5.0, "brier_gt10": 10.0}
MIN_GROUP_DAYS = k.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What an arm is tested against: the arms before it, latest first, then the benchmarks. (s3) is tested against the benchmarks only."""

    return list(reversed(ARMS[: ARMS.index(candidate)])) + list(BENCHMARKS) if candidate in ARMS else []


# -- the candidate's forecasts and the frame -----------------------------------------------------------------------------


def s3ct_forecasts(frame, register: Sequence[policy_events.PolicyEntry], s3: Mapping[date, Mapping[int, Sequence[float]]]):
    """(s3)'s forecasts with each cell's quantiles clipped as (s3c-t) clips them: at the line at full allotment, except on a turn day."""

    out = {}
    for d, per_h in s3.items():
        out[d] = {}
        for h, q in per_h.items():
            t = frame.target(d, h)
            out[d][h] = s3c_turn_cap.capped_quantiles(q, register, k.decision_instant(d), t, frame.day_type(t))
    return out


def build_frame(panel, splits, registry, table, register, first: Optional[date] = None):
    """The walk of (s3) over every decision day, and the scored decision days from `FIRST_DECISION` with a forecast of every model.

    `first` starts the walk and the scored days later than the declared study does; it exists for the test of this script, and the declared
    run never passes it. Returns the frame, the notes and the walk.

    Raises:
        LookAheadError: a scored decision day or target day is after `LAST_DAY` or in a locked tier.
    """

    frame = s686.Frame(panel, splits, registry, None)
    frame.outcome = {row.date: row.spread_bps for row in panel if row.date <= LAST_DAY}
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY and (first is None or day >= first)
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    mine = sc.walk(panel, candidate_days, table, {}, (sc.ARMS[2],), **settings)
    scored = [d for d in candidate_days if d in mine.forecasts[S3] and d >= FIRST_DECISION]
    b1, b1p, b2, dropped = {}, {}, {}, []
    for day in scored:
        index = frame.position[day]
        try:
            one = pb.b1_forecast(panel, index, registry=registry, decision_time=k.DECISION_TIME)
            prime = b1c.b1_calendar_forecast(panel, index, **settings)
            two = pb.b2_forecast(panel, index, **settings)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
            continue
        b1[day], b1p[day], b2[day] = one, prime, two
    days = [d for d in scored if d in b1]
    s686.require_scored_days({frame.target(d, h) for d in days for h in sp.HORIZONS} | set(days), LAST_DAY)
    frame.days = days
    s3 = {d: mine.forecasts[S3][d] for d in days}
    s3c = m1255.s3c_forecasts(frame, register, s3)
    s3ct = s3ct_forecasts(frame, register, s3)
    frame.forecasts = {"B1": b1, B1P: b1p, "B2": b2, S3: s3, S3C: s3c, S3CT: s3ct}
    notes = {
        "decision_days_walked": len(candidate_days), "candidate_skipped_for_history": len(mine.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "first_target": frame.target(days[0], 1).isoformat(), "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
        "refits": len(mine.fits),
    }
    return frame, notes, mine


def probability(q: Sequence[float], tau: float) -> float:
    """P(spread > tau) as `spread_mean_reversion.exceedance` reads it off the 23 quantiles: 1 - F(floor(tau) + 0.5)."""

    return smr.exceedance(q, tau)


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]]) -> Dict[str, Dict[Tuple[date, int], float]]:
    """The four scores of every (decision day, lead) cell of `forecasts`, after the days are checked. The Brier cell is
    `(P(> tau) - 1{y > tau})^2` with the event strict and on whole basis points (`data.exceeds_bp`)."""

    days = sorted(forecasts)
    cells = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), LAST_DAY)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in METRIC_NAMES}
    for (d, h), t in cells.items():
        q, y = forecasts[d][h], frame.outcome[t]
        out["grid_crps"][(d, h)] = sp.grid_crps(q, y)
        out["upper_tail_twcrps"][(d, h)] = sp.upper_tail_twcrps(q, y)
        for name, tau in TAUS.items():
            out[name][(d, h)] = (probability(q, tau) - (1.0 if data.exceeds_bp(y, tau) else 0.0)) ** 2
    return out


# -- the checks ----------------------------------------------------------------------------------------------------------


def turn_check(frame, register, s3, s3c, s3ct) -> dict:
    """What the three arms are cell by cell: (s3c-t) is (s3c) on every target day that is not a turn at full allotment and (s3) on every turn
    day; (s3c) is (s3) before full allotment.

    Raises:
        ValueError: a cell breaks that.
    """

    cells = turn_cells = turn_at_full = moved_by_cap = 0
    for d in frame.days:
        for h in sp.HORIZONS:
            t = frame.target(d, h)
            cells += 1
            turn = s3c_turn_cap.is_turn(frame.day_type(t))
            at_full = s3c_candidate.cap_line(register, k.decision_instant(d), t) is not None
            if turn:
                turn_cells += 1
                if list(s3ct[d][h]) != list(s3[d][h]):
                    raise ValueError(f"the cell ({d}, h={h}) has a turn-day target and (s3c-t) differs from (s3)")
                if at_full:
                    turn_at_full += 1
                    moved_by_cap += 1 if list(s3c[d][h]) != list(s3[d][h]) else 0
            elif list(s3ct[d][h]) != list(s3c[d][h]):
                raise ValueError(f"the cell ({d}, h={h}) has a target that is not a turn day and (s3c-t) differs from (s3c)")
    return {"cells": cells, "turn_day_cells": turn_cells, "turn_day_cells_at_full_allotment": turn_at_full,
            "turn_day_cells_where_the_cap_moves_s3c": moved_by_cap}


def bounds(frame, register, forecasts: Mapping[str, Mapping[date, Mapping[int, Sequence[float]]]]) -> dict:
    """The page's plain statement, from the figures: over the cells at full allotment, the highest P(> +10 bp) of each arm and the cells where it
    is exactly 0; the same split into turn-day targets and the others."""

    out: Dict[str, dict] = {}
    for name in ARMS:
        row = {key: {"cells": 0, "max_p10": 0.0, "max_p5": 0.0, "p10_zero": 0} for key in ("all", "turn", "other")}
        for d in frame.days:
            for h in sp.HORIZONS:
                t = frame.target(d, h)
                if s3c_candidate.cap_line(register, k.decision_instant(d), t) is None:
                    continue
                q = forecasts[name][d][h]
                p10, p5 = probability(q, 10.0), probability(q, 5.0)
                kinds = ("all", "turn" if s3c_turn_cap.is_turn(frame.day_type(t)) else "other")
                for key in kinds:
                    r = row[key]
                    r["cells"] += 1
                    r["max_p10"] = max(r["max_p10"], p10)
                    r["max_p5"] = max(r["max_p5"], p5)
                    r["p10_zero"] += 1 if p10 == 0.0 else 0
        out[name] = row
    return out


def events(frame) -> dict:
    """Every target day of the frame on which SOFR - IORB closed strictly above +5 or +10 bp (whole basis points), with each model's P(> +5) and
    P(> +10) at each lead whose decision day is scored (`docs/decisions/pressure-probability.md`)."""

    targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
    rows = []
    for t in targets:
        y = frame.outcome[t]
        above5, above10 = data.exceeds_bp(y, 5.0), data.exceeds_bp(y, 10.0)
        if not above5:
            continue
        probs: Dict[str, Dict[str, Optional[Dict[str, float]]]] = {m: {} for m in MODELS}
        for h in sp.HORIZONS:
            i = frame.position[t] - h
            d = frame.dates[i] if i >= 0 else None
            for m in MODELS:
                if d is not None and d in frame.days:
                    q = frame.forecasts[m][d][h]
                    probs[m][str(h)] = {"p5": probability(q, 5.0), "p10": probability(q, 10.0)}
                else:
                    probs[m][str(h)] = None
        rows.append({"date": t.isoformat(), "spread_bp": y, "day_type": frame.day_type(t), "turn": s3c_turn_cap.is_turn(frame.day_type(t)),
                     "above_5": above5, "above_10": above10, "probabilities": probs})
    cells = [(d, h) for d in frame.days for h in sp.HORIZONS]
    return {"days": rows, "positive_days_5": sum(1 for r in rows if r["above_5"]), "positive_days_10": sum(1 for r in rows if r["above_10"]),
            "positive_cells_5": sum(1 for d, h in cells if data.exceeds_bp(frame.outcome[frame.target(d, h)], 5.0)),
            "positive_cells_10": sum(1 for d, h in cells if data.exceeds_bp(frame.outcome[frame.target(d, h)], 10.0)),
            "cells": len(cells), "target_days": len(targets)}


# -- the groups and the tests --------------------------------------------------------------------------------------------


def groups_of(frame) -> List[Tuple[str, str, str, List[date]]]:
    """`(split, label, grain, members)`: pooled; the decision days of the gap; by lead; turn days and other days; the pressure-day types; months."""

    out: List[Tuple[str, str, str, List[date]]] = [("pooled", "all decision days", "decision", list(frame.days))]
    gap = [d for d in frame.days if GAP_FIRST <= d <= GAP_LAST]
    out.append(("decision_window", "decision days 24 to 30 Dec 2025 (in neither window of #1255)", "decision", gap))
    out.append(("decision_window", "decision days 10 Dec 2025 to 23 Dec 2025", "decision", [d for d in frame.days if d < GAP_FIRST]))
    out.append(("decision_window", "decision days from 31 Dec 2025 (#1255's 2026 window)", "decision", [d for d in frame.days if d >= WINDOW_2026_FIRST]))
    for h in sp.HORIZONS:
        out.append(("lead", f"h={h}", f"lead{h}", list(frame.days)))
    targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
    turn = [t for t in targets if s3c_turn_cap.is_turn(frame.day_type(t))]
    out.append(("turn_day", "turn days (cap off in (s3c-t))", "target", turn))
    out.append(("turn_day", "other days", "target", [t for t in targets if t not in set(turn)]))
    by_type: Dict[str, List[date]] = {}
    by_month: Dict[str, List[date]] = {}
    for t in targets:
        by_type.setdefault(frame.day_type(t), []).append(t)
        by_month.setdefault(t.strftime("%Y-%m"), []).append(t)
    out += [("pressure_day_type", label, "target", by_type[label]) for label in sorted(by_type)]
    out += [("month", label, "target", by_month[label]) for label in sorted(by_month)]
    return out


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


def run(panel, splits, registry, table, register, args) -> dict:
    frame, notes, mine = build_frame(panel, splits, registry, table, register, args.first)
    s3, s3c, s3ct = (frame.forecasts[x] for x in ARMS)
    check = turn_check(frame, register, s3, s3c, s3ct)
    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = groups_of(frame)
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
        for metric in METRIC_NAMES:
            for candidate in ARMS:
                if plan(candidate):
                    jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {"notes": notes, "refits": len(mine.fits), "groups": {}, "skipped_groups": skipped, "turn_check": check,
                    "bounds": bounds(frame, register, frame.forecasts), "events": events(frame)}
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    labels = {t: frame.day_type(t) for t in {frame.target(d, h) for d in frame.days for h in sp.HORIZONS}}
    result["pressure_day_type_counts"] = {x: sum(1 for v in labels.values() if v == x) for x in sorted(set(labels.values()))}
    return result


def against_1255(result: Mapping[str, object]) -> Optional[dict]:
    """The pooled means of (s3), (s3c), B1, B1' and B2 on the decision days from 2025-12-31 here, against #1255's 2026 window (the same days,
    the same walk). `None` when the record is not there."""

    if not RECORD_1255.exists():
        return None
    there = json.loads(RECORD_1255.read_text(encoding="utf-8"))["windows"]["2026"]["groups"]["pooled"]["all decision days"]
    here = result["groups"]["decision_window"]["decision days from 31 Dec 2025 (#1255's 2026 window)"]
    out = {"record": str(RECORD_1255.relative_to(REPO)), "days_here": here["days"], "days_there": there["days"], "metrics": {}}
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out["metrics"][metric] = {m: {"here": here[metric]["means"][m], "there": there[metric]["means"][m],
                                      "difference": here[metric]["means"][m] - there[metric]["means"][m]} for m in (S3, S3C) + BENCHMARKS}
    return out


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_turn_cap_1265")
    if not turn_days.in_force():
        raise SystemExit("the turn-day record is not in force: (s3c-t) reads the day types in force")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    result: dict = {
        "issue": 1265, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": S3CT, "margin_bp": s3c_candidate.MARGIN_BP,
        "turn_labels": sorted(turn_days.TURN_LABELS), "reading_rules": declaration["reading_rules"],
    }
    result.update(run(panel, splits, registry, table, register, args))
    result["against_1255"] = against_1255(result) if args.first is None else None
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


def _vs(group: Mapping[str, object], metric: str, candidate: str, reference: str) -> Optional[dict]:
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(candidate, {}).get(reference)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(f"{group[x]['means'][m]:.4f}" if x.startswith("brier") else f"{group[x]['means'][m]:.3f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str, metrics_: Sequence[str] = METRIC_NAMES) -> List[str]:
    out = [f"| {LABELS[candidate]} against | " + " | ".join(METRIC_TITLES[m] for m in metrics_) + " |", "|---|" + "---|" * len(metrics_)]
    for ref in plan(candidate):
        out.append(f"| {LABELS[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in metrics_) + " |")
    return out


def split_table(r: Mapping[str, object], split: str, candidate: str, reference: str, metrics_: Sequence[str]) -> List[str]:
    labels = r["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in metrics_) + " |", "|---|---|" + "---|" * len(metrics_)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(cell(_vs(g, m, candidate, reference)) if f"{split}/{label}" not in r["skipped_groups"] else "not tested (fewer than 20 days)" for m in metrics_) + " |")
    return out


def means_split_table(r: Mapping[str, object], split: str) -> List[str]:
    """The mean grid CRPS and the mean Brier scores of the three arms in each group of a split, tested or not."""

    labels = r["groups"].get(split, {})
    cols = [(x, m) for x in ("grid_crps", "brier_gt5", "brier_gt10") for m in ARMS]
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(f"{METRIC_TITLES[x]} {LABELS[m]}" for x, m in cols) + " |", "|---|---|" + "---|" * len(cols)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[x]['means'][m]:.4f}" for x, m in cols) + " |")
    return out


def bounds_table(b: Mapping[str, dict]) -> List[str]:
    out = ["| model | cells at full allotment | highest P(> +10 bp) | cells with P(> +10 bp) exactly 0 | highest P(> +5 bp) |", "|---|---|---|---|---|"]
    for name in ARMS:
        for key, title in (("all", "all"), ("turn", "turn-day targets"), ("other", "other targets")):
            x = b[name][key]
            out.append(f"| {LABELS[name]}, {title} | {x['cells']} | {x['max_p10']:.4f} | {x['p10_zero']} | {x['max_p5']:.4f} |")
    return out


def event_table(ev: Mapping[str, object], threshold: str) -> List[str]:
    """One row per event day: the arms' P(> threshold) at the leads whose decision day is scored (h=1..5, `-` where it is not)."""

    key = "p5" if threshold == "5" else "p10"
    names = (S3, S3C, S3CT, "B2")
    out = ["| target day | SOFR - IORB (bp) | type | " + " | ".join(f"{LABELS[m]} h=1..5" for m in names) + " |", "|---|---|---|" + "---|" * len(names)]
    for row in ev["days"]:
        if threshold == "10" and not row["above_10"]:
            continue
        cells_ = []
        for m in names:
            cells_.append(" / ".join("-" if row["probabilities"][m][str(h)] is None else f"{row['probabilities'][m][str(h)][key]:.3f}" for h in sp.HORIZONS))
        out.append(f"| {row['date']} | {row['spread_bp']:+.0f} | {row['day_type']}{' (turn)' if row['turn'] else ''} | " + " | ".join(cells_) + " |")
    return out


def headline(r: Mapping[str, object]) -> str:
    pooled = r["groups"]["pooled"]["all decision days"]
    turn_label = "turn days (cap off in (s3c-t))"
    turn = r["groups"]["turn_day"][turn_label]
    parts = [f"pooled, {METRIC_TITLES[m]}, (s3c-t) against (s3c): {cell(_vs(pooled, m, S3CT, S3C))}" for m in ("grid_crps", "brier_gt10")]
    if f"turn_day/{turn_label}" in r["skipped_groups"]:
        parts.append(f"on the {turn['days']} turn days (too few to test) the mean grid CRPS is {turn['grid_crps']['means'][S3C]:.3f} for (s3c) and "
                     f"{turn['grid_crps']['means'][S3CT]:.3f} for (s3c-t), the mean Brier score of P(> +10 bp) {turn['brier_gt10']['means'][S3C]:.4f} and "
                     f"{turn['brier_gt10']['means'][S3CT]:.4f}")
    else:
        parts += [f"on turn days, {METRIC_TITLES[m]}, (s3c-t) against (s3c): {cell(_vs(turn, m, S3CT, S3C))}" for m in ("grid_crps", "brier_gt10")]
    return "; ".join(parts) + "."


def closes_above_the_line(r: Mapping[str, object]) -> str:
    """Which of the days above +10 bp the rule reaches: those whose reporting type is a turn, and those it leaves under the cap."""

    days = [x for x in r["events"]["days"] if x["above_10"]]
    on_turn = [x for x in days if x["turn"]]
    off_turn = [x for x in days if not x["turn"]]

    def show(rows) -> str:
        return ", ".join(f"{x['date']} ({x['spread_bp']:+.0f} bp, `{x['day_type']}`)" for x in rows) or "none"

    top = max((x["probabilities"][S3CT][h]["p10"] for x in off_turn for h in x["probabilities"][S3CT] if x["probabilities"][S3CT][h]), default=0.0)
    return (f"Days on which SOFR - IORB closed above +10 bp in the frame: {len(days)}. On a turn day (the cap is off in (s3c-t)): {show(on_turn)}. "
            f"Not on a turn day, so (s3c-t) is (s3c) and the cap stays on: {show(off_turn)}; the highest P(> +10 bp) (s3c-t) gave any of them, at any "
            f"lead, is {top:.4f}. The day types are those in force (`turn_days.reporting_day_type`): a day that is not a `turn`, `quarter_end_turn` or "
            "`year_end` is not lifted, whatever SOFR did on it. Which days the rule should lift is the choice behind Question 1.")


def render(r: dict) -> str:
    b, ev, chk = r["bounds"], r["events"], r["turn_check"]
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# (s3c) with the cap off on turn days, scored since full allotment (#1265)", "",
        "**Does leaving the cap off on turn days help (s3c)'s tail, and what does the cap cost on the days SOFR closed above the line?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, the candidate (s3c); ledger item 62 on #1116; findings #1261 and #1264. **Development data, "
        "not a verdict** (scoring protocol v1, #640). Her ruling of 27 October 2026 (chat, relayed on #1265): option 1 on finding #1261, which takes in "
        "avenue #1264. **(s3c) stays the candidate until she rules on this result.** Nothing is registered or published and no claim changes. "
        f"Generated by `scripts/s3c_turn_cap_1265.py page` from `docs/research/s3c-turn-cap-1265/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        "**What (s3c) says about the tail, plainly.** At full allotment (s3c) caps every quantile at the SRF line (IORB + 10 bp, margin 0), and the "
        "event is read as 1 - F(10.5). So at full allotment (s3c) gives P(> +10 bp) of at most about 1% by construction, and exactly 0 when the "
        f"upper quantiles (q97.5 and q99) sit on the line. In these cells: the highest P(> +10 bp) of (s3c) is {b[S3C]['all']['max_p10']:.4f} over "
        f"{b[S3C]['all']['cells']:,} cells at full allotment, and it is exactly 0 in {b[S3C]['all']['p10_zero']:,} of them; (s3)'s highest is "
        f"{b[S3]['all']['max_p10']:.4f}, and (s3c-t)'s on turn-day targets {b[S3CT]['turn']['max_p10']:.4f}.", "",
        "**The arms.** (s3) is (s3) of #1145; (s3c) is (s3) capped at the line from full allotment (`repo_model.s3c_candidate`); **(s3c-t)** is "
        "(s3c) with the cap off on a turn day (`repo_model.s3c_turn_cap`): on a target day whose reporting type is `year_end`, `quarter_end_turn` or "
        "`turn` (the day types in force, read at the target day as the calendar columns are) the quantiles are (s3)'s, and on every other day they "
        "are (s3c)'s. No date is written in the code and the margin is 0 bp, not tuned.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours the arm "
        "named first in the table's heading. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill "
        "interval beside it; for a Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals "
        "of a group of target days (turn days, other days, a pressure-day type, a month) keep the **current method** (the group's days, scattered, "
        "resampled in date order as if consecutive), which #1221 questions and #1228 will decide; no reading of a day-type group is a finding. Where "
        "two arms differ on few days of a group, some resamples have no long-run variance: the bound is then not computed, the unstudentized interval "
        "of mean d is given beside it, and no reading is taken from that. Groups of fewer than 20 days are listed with their means and not tested.", "",
        f"**What kind of look this is.** The frame is one run of {n['scored_decision_days']:,} decision days ({n['first']} to {n['last']}; targets "
        f"{n['first_target']} to {n['last_target']}), from the day the removal of the aggregate limit was announced. It includes the decision days "
        "of 24 to 30 December 2025, which are in neither window of #1255. The days from 2026-01-02 were already seen by #845, the #151 final test, "
        "#1229, #1252 and #1255. This is a check on the candidate she chose, not evidence for a verdict.", "",
        f"The cells check: on {chk['turn_day_cells']:,} of {chk['cells']:,} cells the target is a turn day and (s3c-t) is (s3) element for element "
        f"({chk['turn_day_cells_at_full_allotment']:,} of them at full allotment, where the cap moves (s3c) in {chk['turn_day_cells_where_the_cap_moves_s3c']:,}); "
        "on every other cell (s3c-t) is (s3c) element for element. The script refuses to write a record if one cell breaks that.", ""]
    ag = r.get("against_1255")
    if ag:
        out += ["Reproduction of #1255 (same walk, the 2026 window's decision days, "
                f"{ag['days_here']} here and {ag['days_there']} there): pooled mean difference here minus there, " + "; ".join(
                    f"{METRIC_TITLES[m]}: " + ", ".join(f"{LABELS[x]} {v['difference']:+.2e}" for x, v in rows.items()) for m, rows in ag["metrics"].items()) + ".", ""]
    out += ["## What the turn-day rule does to the days above the line", "", closes_above_the_line(r), "",
            "## Mean scores (pooled)", ""] + mean_table(pooled) + [""]
    for cand in (S3CT, S3C, S3):
        out += [f"## {LABELS[cand]} against each reference (pooled)", ""] + against_table(pooled, cand) + [""]
    out += ["## Where the cap acts and what it bounds", ""] + bounds_table(b) + [""]
    for metric_set, title in (((("grid_crps", "upper_tail_twcrps")), "grid CRPS and upper-tail twCRPS"), (("brier_gt5", "brier_gt10"), "the Brier scores of the pressure events")):
        for split, name in (("turn_day", "By turn day and other days"), ("decision_window", "By decision window"), ("pressure_day_type", "By pressure-day type of the target day"),
                            ("month", "By target month"), ("lead", "By lead")):
            for cand, ref in ((S3CT, S3C), (S3C, S3)):
                table = split_table(r, split, cand, ref, metric_set)
                if len(table) > 2:
                    out += [f"## {name}: {LABELS[cand]} against {LABELS[ref]}, {title}", ""] + table + [""]
    for split, name in (("turn_day", "turn days and other days"), ("decision_window", "decision window"), ("pressure_day_type", "pressure-day type"), ("month", "target month")):
        out += [f"## Mean scores of the three arms by {name}", ""] + means_split_table(r, split) + [""]
    if r["skipped_groups"]:
        out += ["Groups of fewer than 20 days, listed with their means and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(r["skipped_groups"].items())) + ".", ""]
    out += ["## The event list", "",
            f"Every target day in the frame on which SOFR - IORB closed strictly above +5 bp (whole basis points): {ev['positive_days_5']} of {ev['target_days']} target days "
            f"({ev['positive_cells_5']} of {ev['cells']:,} cells); above +10 bp: {ev['positive_days_10']} days ({ev['positive_cells_10']} cells). Each entry shows the "
            "probability at the leads h = 1..5 whose decision day is scored (`-` where it is not): the five scored business days before the event and the day itself "
            "(`docs/decisions/pressure-probability.md`). The other models are in `result.json`.", "",
            "### Above +5 bp: P(> +5 bp)", ""] + event_table(ev, "5") + ["", "### Above +10 bp: P(> +10 bp)", ""] + event_table(ev, "10") + [""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. What follows from this result.** (s3c) stays the H5 candidate. Whether (s3c-t), or a cap that is lifted in some other way, "
        "replaces it is a choice for her, and it rests on days already seen.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests (s3c-t) prospectively**, on the confirmation days only, under the scoring protocol.",
        "3. **Rule on the cap itself** (keep it, lift it on turn days, or lift it on every day), in a decision record she reviews.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3), cap it, lift the cap on turn days, and score the three arms from full allotment")
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
