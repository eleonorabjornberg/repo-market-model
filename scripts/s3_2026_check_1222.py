"""The H5 candidate (s3) on the 2026 development days, with #845's calibration check (#1229; H5 step 3, avenue #1222).

A development check, never a verdict, and no choice is made on it. It writes JSON and Markdown to the paths it is given and nothing
into `docs/runs/`. Every choice is in `metadata/s3_2026_check_1222.json`, which this script refuses to read unless it is committed and
unchanged. There is no new arm: the model is (s3) of #1145 (`repo_model.spread_mr_state_calendar.ARMS[2]`, #941's scaled mean
reversion with calendar terms in standardised units, a Huber fit, ridge 5, direct pairs), refit walk-forward as #1196 declared, beside
(a) (#941), B1, B1' (#960) and B2 of scoring protocol v1. It reads the helpers of `scripts/s3_terms_1196.py` (the readings, the cell
format) and of `scripts/calibration_reserve_mgmt_845.py` (the decomposition and the stationary bootstrap of #845's table).

Scored decision days are those whose five targets fall from 2026-01-02 to 2026-09-03 (`repo_model.exploration.EXPLORATORY_END`): the
near-blind tier was opened on 2026-10-05 (`metadata/lockbox.json`, GO #151) and is development history. Every scored day passes
`lockbox.require_unlocked` (through `spread_mean_reversion_686.require_scored_days`) and no day after 2026-09-03 is read. #845's table
is read over the ordinary target days from 2025-12-12, as #845 declared its stretch; those days were scored by #1196 already.

The walk takes minutes and the paired tests are the long part (under an hour on 4 cores), so the run is a cloud run. Commands, from a
clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3_2026_check_1222.py score --panel PUB.csv \\
        --output docs/research/s3-2026-check-1222/result.json --withheld WITHHELD.json
    PYTHONPATH=src python3 scripts/s3_2026_check_1222.py page \\
        --score docs/research/s3-2026-check-1222/result.json --output docs/research/s3-2026-check-1222-result.md

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


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, b1_calendar as b1c, metrics  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mean_reversion as smr, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model.splits import LookAheadError, SplitError  # noqa: E402

m1196 = _load("s3_terms_1196")
c = m1196.c
s686, s761 = c.s686, c.s761
d845 = _load("calibration_reserve_mgmt_845")

DECLARATION = REPO / "metadata" / "s3_2026_check_1222.json"
SEED = 1222
#: The last day this study reads, and the first target day of its scored decision days.
LAST_DAY = EXPLORATORY_END
FIRST_TARGET = date(2026, 1, 2)
#: The first target day of #845's stretch, which its table is read from.
TABLE_FIRST = date(2025, 12, 12)
DECISION_TIME = c.DECISION_TIME
MIN_GROUP_DAYS = c.MIN_GROUP_DAYS
B1P = c.B1P
A = sc.ARM_A
S3 = sc.ARMS[2].name
#: The two models of #845's table, and of the paired tests as candidates.
ARMS = (A, S3)
BENCHMARKS = ("B1", B1P, "B2")
MODELS = BENCHMARKS + ARMS
METRIC_NAMES = c.METRIC_NAMES
DAY_TYPES = c.DAY_TYPES
ORDINARY = c.ORDINARY
RATES = m1196.RATES
BANDS = m1196.d1145.BANDS
Q95 = c.Q95
TAU = d845.TAU
#: The coverage interval blocks: one lead's cells are one per day, several leads' are five per day.
LEAD_BLOCK = float(sp.BLOCK_LENGTH)
CELL_BLOCK = c.CELL_BLOCK
#: Windows of #845's table: its stretch, and the target days of the scored decision days alone.
WINDOWS = (("after_purchases_2025_26", TABLE_FIRST, LAST_DAY), ("scored_days_2026", FIRST_TARGET, LAST_DAY))
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", A: "(a) #941 mad 20, floor 0.5", S3: "(s3) of #1145, the H5 candidate"}
METRIC_TITLES = m1196.METRIC_TITLES
_fmt, verdict, skill_verdict, reading_words, _bold = m1196._fmt, m1196.verdict, m1196.skill_verdict, m1196.reading_words, m1196._bold


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def month_of(day: date) -> str:
    """The calendar month of a day, `YYYY-MM`."""

    return f"{day.year:04d}-{day.month:02d}"


# -- the span ---------------------------------------------------------------------------------------------------------


def require_span(first_targets: Mapping[date, date], last_targets: Mapping[date, date]) -> None:
    """Refuse a scored decision day whose first target is before `FIRST_TARGET`, or whose fifth target is after `LAST_DAY`.

    The study scores the 2026 development days only; a decision day with an earlier target would put a day #1196 scored into the 2026
    figures, and a later one reads the blind tier. The lockbox itself is checked by `require_scored_days`.

    Mutation record: replacing `if first < FIRST_TARGET:` with `if first < FIRST_TARGET - timedelta(days=30):` made
    `test_s3_2026_check_1222_script.SpanTests.test_a_decision_day_with_a_target_before_2026_is_refused` fail with `AssertionError`
    (`LookAheadError` not raised); restored, it passes.

    Raises:
        LookAheadError: a decision day outside the span, naming it.
    """

    for day in sorted(first_targets):
        first, last = first_targets[day], last_targets[day]
        if first < FIRST_TARGET:
            raise LookAheadError(f"decision day {day} has a target on {first}, before {FIRST_TARGET}: #1196 scored that day already")
        if last > LAST_DAY:
            raise LookAheadError(f"decision day {day} has a target on {last}, after {LAST_DAY}: the blind tier stays shut")


# -- the frame --------------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, table, first: Optional[date] = None):
    """The walk of (a) and (s3) on every decision day, and the scored decision days with a forecast of every model.

    `first` starts the walk later than the declared study does; it exists for the test of this script, and the declared run never
    passes it. Returns the frame, the notes and the walk.
    """

    frame = s686.Frame(panel, splits, registry, None)
    frame.outcome = {row.date: row.spread_bps for row in panel if row.date <= LAST_DAY}
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY and (first is None or day >= first)
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)
    mine = sc.walk(panel, candidate_days, table, {}, (sc.ARMS[2],), **settings)
    scored = [d for d in candidate_days if d in mine.forecasts[S3] and frame.target(d, 1) >= FIRST_TARGET]
    b1, b1p, b2, dropped = {}, {}, {}, []
    for day in scored:
        index = frame.position[day]
        try:
            one = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            prime = b1c.b1_calendar_forecast(panel, index, **settings)
            two = pb.b2_forecast(panel, index, **settings)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
            continue
        b1[day], b1p[day], b2[day] = one, prime, two
    days = [d for d in scored if d in b1]
    require_span({d: frame.target(d, 1) for d in days}, {d: frame.target(d, max(sp.HORIZONS)) for d in days})
    s686.require_scored_days({frame.target(d, h) for d in days for h in sp.HORIZONS} | set(days), LAST_DAY)
    frame.days = days
    frame.forecasts = {"B1": b1, B1P: b1p, "B2": b2, **{a: mine.forecasts[a] for a in ARMS}}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    notes = {
        "decision_days_walked": len(candidate_days), "candidate_skipped_for_history": len(mine.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "first_target": frame.target(days[0], 1).isoformat(), "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
        "refits": len(mine.fits),
    }
    return frame, notes, mine


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]]) -> Dict[str, Dict[Tuple[date, int], float]]:
    """Both scores, the q95 hits and the band hits of every (decision day, lead) cell of `forecasts`, after the days are checked."""

    days = sorted(forecasts)
    cells = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), LAST_DAY)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in METRIC_NAMES + RATES}
    for (d, h), t in cells.items():
        q, y = forecasts[d][h], frame.outcome[t]
        out["grid_crps"][(d, h)] = sp.grid_crps(q, y)
        out["upper_tail_twcrps"][(d, h)] = sp.upper_tail_twcrps(q, y)
        out["hit_above"][(d, h)] = 1.0 if y > q[Q95] else 0.0
        out["hit_at_or_above"][(d, h)] = 1.0 if y >= q[Q95] else 0.0
        for name, (lo, hi) in BANDS.items():
            out[f"{name}_closed"][(d, h)] = 1.0 if q[lo] <= y <= q[hi] else 0.0
            out[f"{name}_open"][(d, h)] = 1.0 if q[lo] < y < q[hi] else 0.0
    return out


# -- #845's table -----------------------------------------------------------------------------------------------------


def large_rows(frame, mine, first: date, last: date, lead: int) -> List[dict]:
    """The ordinary target days of the window at one lead, in order: the lead-`lead` law of each model, made `lead` rows earlier.

    Raises:
        LookAheadError: a target or decision day after `LAST_DAY` or in a locked tier.
    """

    rows = []
    for target in sorted(t for t in frame.outcome if first <= t <= last):
        index = frame.position[target] - lead
        if index < 0 or frame.day_type(target) != ORDINARY:
            continue
        decision = frame.dates[index]
        laws = {name: mine.forecasts[name].get(decision) for name in ARMS}
        if any(law is None for law in laws.values()):
            continue
        s686.require_scored_days({decision, target}, LAST_DAY)
        q = {name: [float(v) for v in law[lead]] for name, law in laws.items()}
        y = frame.outcome[target]
        rows.append({"day": target, "outcome": y, "event": exceeds_bp(y, TAU), "p": {n: smr.exceedance(v, TAU) for n, v in q.items()}, "q": q})
    return rows


def large_cell(rows: Sequence[dict], *, draws: int) -> dict:
    """One (window, lead) cell of #845's table from its rows: the realised share, each model's mean P and error with intervals, and the
    level and residual-pool parts of the error."""

    n = len(rows)
    events = [1.0 if row["event"] else 0.0 for row in rows]
    cell: dict = {"cells": n, "pressure_days": int(sum(events))}
    if not n:
        return cell
    series = [events] + [[row["p"][name] for row in rows] for name in ARMS] + [[row["p"][name] - e for row, e in zip(rows, events)] for name in ARMS]
    bounds = d845.stationary_interval(series, draws=draws, seed=SEED, block=d845.BLOCK)
    cell["realised"], cell["realised_interval"] = sum(events) / n, list(bounds[0])
    cell["models"] = {}
    for k, name in enumerate(ARMS):
        mean_p = sum(row["p"][name] for row in rows) / n
        parts = d845.decompose([row["q"][name] for row in rows], [row["outcome"] for row in rows])
        cell["models"][name] = {
            "mean_p": mean_p, "mean_p_interval": list(bounds[1 + k]), "error": mean_p - cell["realised"],
            "error_interval": list(bounds[1 + len(ARMS) + k]),
            **{key: parts[key] for key in ("level", "pool", "delta_bp", "centred_mean_p", "mean_median_bp", "mean_outcome_bp")},
        }
    return cell


def calibration_in_the_large(frame, mine, draws: int) -> Tuple[dict, dict]:
    """#845's table by window and lead. Returns the tracked table (a cell under the minimum of pressure days keeps its counts only,
    Eleonora's ruling on #710) and the withheld figures of those cells."""

    tracked: dict = {}
    withheld: dict = {}
    for name, first, last in WINDOWS:
        tracked[name] = {"first_target_day": first.isoformat(), "last_target_day": last.isoformat(), "leads": {}}
        for h in sp.HORIZONS:
            cell = large_cell(large_rows(frame, mine, first, last, h), draws=draws)
            under = d845.under_minimum(cell["pressure_days"])
            tracked[name]["leads"][str(h)] = d845.tracked_cell(cell, withheld=under)
            if under:
                withheld.setdefault(name, {})[str(h)] = cell
    return tracked, withheld


# -- the groups -------------------------------------------------------------------------------------------------------


def groups_of(frame, labels: Mapping[date, Sequence[str]]) -> List[Tuple[str, str, str, List[date]]]:
    """`(split, label, grain, members)`: pooled, by lead, by target month, and by target-day type (overlapping). The regime split of
    the other pages has one regime here and is the pooled row."""

    out = [g for g in c.groups_of(frame, labels) if g[0] != "regime"]
    months: Dict[str, List[date]] = {}
    for t in sorted(labels):
        months.setdefault(month_of(t), []).append(t)
    position = next(i for i, g in enumerate(out) if g[0] == "target_day_type")
    return out[:position] + [("month", label, "target", members) for label, members in sorted(months.items())] + out[position:]


# -- the tests, in parallel -------------------------------------------------------------------------------------------

_STATE: Dict = {}


def pair_plan(candidate: str) -> List[str]:
    """What a candidate is tested against: B1, B1' and B2, and (a) for (s3)."""

    return list(BENCHMARKS) + ([A] if candidate != A else [])


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in pair_plan(candidate):
        days = list(members)
        if len(days) < MIN_GROUP_DAYS:
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"],
                                  mean_d_fallback=True)[name]
    return (split, label, metric, candidate), out


def _interval_task(job):
    key, values, block = job
    n = len(values)
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx), n, block_length=block, seed=SEED, replications=_STATE["reps"])
    return key, [low, high]


def _dispatch(job):
    kind, payload = job
    return kind, (_pairs_task(payload) if kind == "pairs" else _interval_task(payload))


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- the coverage -----------------------------------------------------------------------------------------------------


def coverage_groups(frame, cells_of: Mapping[str, Mapping[str, Mapping[Tuple[date, int], float]]]) -> Dict[str, List[Tuple[date, int]]]:
    """The cells of each coverage group, in date order: pooled, by lead, and by target month."""

    keys = sorted(cells_of[A]["hit_above"])
    out = {"pooled": keys}
    for h in sp.HORIZONS:
        out[f"h={h}"] = [k for k in keys if k[1] == h]
    months: Dict[str, List[Tuple[date, int]]] = {}
    for k in sorted(keys, key=lambda k: (frame.target(*k), k[1])):
        months.setdefault(month_of(frame.target(*k)), []).append(k)
    out.update(dict(sorted(months.items())))
    return out


def block_of(group: str) -> float:
    """The mean block of a coverage group's interval, in cells."""

    return LEAD_BLOCK if group.startswith("h=") else CELL_BLOCK


# -- the score --------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3_2026_check_1222")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=DECISION_TIME)
    frame, notes, mine = build_frame(panel, splits, registry, table, args.first)
    labels = c.day_labels(frame, table)

    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    large, withheld = calibration_in_the_large(frame, mine, args.draws)

    groups = groups_of(frame, labels)
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
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
    cover = coverage_groups(frame, cells)
    cover_days = {g: len({frame.target(*k) for k in keys}) for g, keys in cover.items()}
    for group, keys in cover.items():
        if cover_days[group] < MIN_GROUP_DAYS:
            continue
        for m in MODELS:
            for rule in RATES:
                jobs.append(("interval", ((group, m, rule), [cells[m][rule][k] for k in keys], block_of(group))))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, mem) for s_, l_, g, mem in groups}
    result: dict = {
        "issue": 1229, "avenue": 1222, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "notes": notes, "models": list(MODELS), "arms": list(ARMS),
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.phi} for day, fit in sorted(mine.fits.items())],
        "calibration_in_the_large": large, "minimum_pressure_days": d845.MINIMUM_PRESSURE_DAYS, "tau_bp": TAU,
        "groups": {}, "skipped_groups": skipped, "coverage": {}, "coverage_days": cover_days,
        "reading_rules": declaration["reading_rules"],
    }
    for kind, payload in done:
        if kind == "pairs":
            (split, label, metric, candidate), out = payload
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = out
        else:
            (group, m, rule), interval = payload
            result["coverage"].setdefault(group, {}).setdefault(m, {}).setdefault(rule, {})["interval"] = interval
    for group, keys in cover.items():
        for m in MODELS:
            for rule in RATES:
                values = [cells[m][rule][k] for k in keys]
                result["coverage"].setdefault(group, {}).setdefault(m, {}).setdefault(rule, {}).update(
                    {"rate": sum(values) / len(values), "cells": len(values)})
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in METRIC_NAMES:
                if metric in entry:
                    ser = series[(grain, metric)]
                    entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    result["day_type_counts"] = {k: sum(1 for t in labels if k in labels[t]) for k in DAY_TYPES + (ORDINARY,)}
    result["month_counts"] = {label: len(members) for split, label, _g, members in groups if split == "month"}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.withheld:
        Path(args.withheld).write_text(json.dumps(
            {"issue": 1229, "withheld_cells": withheld, "note": "not tracked; for the pull request body (#710)"}, indent=1, sort_keys=True) + "\n",
            encoding="utf-8")
    return 0


# -- the page ---------------------------------------------------------------------------------------------------------


def _interval_text(value: float, interval: Sequence[float]) -> str:
    return f"{value:.3f} [{interval[0]:.3f}, {interval[1]:.3f}]"


def large_table(r: dict, name: str, body: dict) -> List[str]:
    """#845's table of one window: counts, realised share, each model's mean P, then the error and its two parts."""

    out = [f"### {name}", "", f"Ordinary target days {body['first_target_day']} to {body['last_target_day']}.", "",
           "**Mean P(spread > +5 bp) against the realised share** (mean P [5th, 95th percentile])", "",
           "| lead | cells | pressure days | realised share | " + " | ".join(LABELS[a] for a in ARMS) + " |",
           "|---|---|---|---|" + "---|" * len(ARMS)]
    for h, cell in body["leads"].items():
        if cell.get("withheld"):
            out.append(f"| {h} | {cell['cells']} | {cell['pressure_days']} | under the minimum of {r['minimum_pressure_days']} pressure days: counts only |" + " |" * len(ARMS))
        elif not cell["cells"]:
            out.append(f"| {h} | 0 | 0 | no cells |" + " |" * len(ARMS))
        else:
            out.append(f"| {h} | {cell['cells']} | {cell['pressure_days']} | {_interval_text(cell['realised'], cell['realised_interval'])} | "
                       + " | ".join(_interval_text(cell["models"][a]["mean_p"], cell["models"][a]["mean_p_interval"]) for a in ARMS) + " |")
    shown = {h: cell for h, cell in body["leads"].items() if not cell.get("withheld") and cell["cells"]}
    if shown:
        out += ["", "**Error (mean P less the realised share), and its level and residual-pool parts**", "",
                "| lead | model | error [5th, 95th percentile] | level part | residual-pool part | centre shift (bp) |", "|---|---|---|---|---|---|"]
        for h, cell in shown.items():
            for a in ARMS:
                e = cell["models"][a]
                out.append(f"| {h} | {LABELS[a]} | {e['error']:+.3f} [{e['error_interval'][0]:+.3f}, {e['error_interval'][1]:+.3f}] | "
                           f"{e['level']:+.3f} | {e['pool']:+.3f} | {e['delta_bp']:+.2f} |")
    return out + [""]


def model_table(cell: dict) -> List[str]:
    """Mean score of every model in one group, and (a) and (s3) against B1, B1', B2 and (a), each with the mean-d bound beside it."""

    out = ["| | mean | skill vs B1 [90%]; mean d (bp) [90%] | vs B1' | vs B2 | vs (a) |", "|---|---|---|---|---|---|"]
    means = cell["means"]
    for name in BENCHMARKS:
        out.append(f"| {LABELS[name]} | {means[name]:.3f} |" + " |" * 4)
    for name in ARMS:
        vs = cell["vs"].get(name, {})
        cells = [_fmt(vs.get(b)) for b in BENCHMARKS] + ["" if name == A else _fmt(vs.get(A))]
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | " + " | ".join(cells) + " |")
    return out


def coverage_table(r: dict, rule: str, groups: Sequence[str]) -> List[str]:
    out = ["| | " + " | ".join(f"{g} ({r['coverage_days'][g]} d)" for g in groups) + " |", "|---|" + "---|" * len(groups)]
    for m in MODELS:
        cells = []
        for g in groups:
            e = r["coverage"][g][m][rule]
            text = f"{e['rate']:.3f}"
            cells.append(text + (f" [{e['interval'][0]:.3f}, {e['interval'][1]:.3f}]" if "interval" in e else ""))
        out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
    return out + [""]


def render(r: dict) -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    leads = [f"h={h}" for h in sp.HORIZONS]
    months = list(r["month_counts"])
    out = [
        "# The H5 candidate (s3) on the 2026 development days, with #845's calibration check (#1229)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3, a check of the chosen candidate (avenue #1222). **Development data, not a "
        f"verdict** (scoring protocol v1, #640): target days {n['first_target']} to {n['last_target']}, no lockbox day (the near-blind tier is "
        "open, GO #151). Generated by `scripts/s3_2026_check_1222.py page` from `docs/research/s3-2026-check-1222/result.json`, not edited by "
        f"hand; declared in `{r['declaration']}` before any number.", "",
        "**What kind of look this is.** These days were already seen by #845 and by the #151 final test. This is a check, not evidence for "
        "a verdict or a choice. No arm was added and nothing is chosen, adopted or retuned on it. (a), B1 and B2 carry the provisional "
        "calendar register's mark (`docs/research/provisional-calendar-register.md`); (s3) reads the calendar at the target day on direct "
        "pairs and does not.", "",
        f"Panel digest `{r['panel_sha256']}`. Models: (s3) of #1145, refit walk-forward as #1196 declared (every 21 decision days from the "
        f"first, {n['refits']} refits to the last day), (a) #941's scaled mean reversion, B1, B1' (Lens C's calendar-aware persistence, #960, "
        "beside B1 in every table; B1 stays the protocol's benchmark) and B2. Scored decision days: "
        f"{n['scored_decision_days']:,} ({n['first']} to {n['last']}), those whose five targets fall from 2026-01-02 to 2026-09-03."
        + (f" B2 refused {len(n['benchmark_missing'])} decision days, recorded as missing: {', '.join(n['benchmark_missing'])}."
           if n["benchmark_missing"] else " B2 refused no decision day."), "",
        f"Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, seed {r['seed']}, "
        "two-sided 90% interval (the lower end is the one-sided 95% bound). Skill is `mean(d) / mean(S(benchmark))` with "
        "`d = S(benchmark) - S(candidate)`, positive favours the candidate. **Every row shows the skill interval and, beside it, the "
        "studentized interval on mean d (bp); a reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), "
        "not from the skill interval. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated "
        "about 2x after 2020, so an interval that excludes zero is narrower than it should be. A row with no mean-d bound reads \"no reading\" "
        "with the reason (#1215).", "",
        "**The month and target-day-type intervals are the current method, not a settled one.** They pass the group's own days to the paired "
        "test as one short series, and #1221 asks whether that is right (queued as #1228; not decided). Read them as that method's output; "
        "they follow #1221's outcome when it is merged. A group of fewer than "
        f"{MIN_GROUP_DAYS} days is listed and not tested. 2026 has few pressure days, so every upper-tail and P(> +5 bp) split is thin.", "",
        "## 1. Calibration in the large (#845's table)", "",
        f"The mean P(spread > +{r['tau_bp']:g} bp) each model gives on ordinary target days against the share that realised it (whole basis "
        "points, strictly above), by lead. Intervals are the 5th and 95th percentile of a stationary bootstrap over the cells (mean block 10, "
        f"{r['draws']:,} draws). The error is split into a level part (what moving each cell's law by the mean of outcome less the law's "
        "median would remove, a hindsight diagnostic) and a residual-pool part; the two add to the error exactly. #845 found the older laws "
        "over-forecast pressure on these days, the error sitting in the residual pool; (s3) scales its residuals by recent volatility and "
        f"this reads whether that held. A (window, lead) cell with fewer than {r['minimum_pressure_days']} pressure days shows its counts "
        "only (Eleonora's ruling on #710).", ""]
    for name, body in r["calibration_in_the_large"].items():
        out += large_table(r, name, body)
    out += ["## 2. Coverage of the central bands", "",
            "The share of (decision day, lead) cells whose outcome falls in the central band, with a 90% stationary-bootstrap percentile "
            "interval over the cells in date order (mean block 10 for one lead, 50 cells for several leads; none for a group under "
            f"{MIN_GROUP_DAYS} target days). Both hit rules of #993 are given: the closed band and the open band; the exceedance is `y > q` and `y >= q`.", ""]
    for rule, title in (("b50_closed", "the central 50% band (q25 to q75), closed (nominal 0.50)"), ("b50_open", "the central 50% band, open (nominal 0.50)"),
                        ("b90_closed", "the central 90% band (q05 to q95), closed (nominal 0.90)"), ("b90_open", "the central 90% band, open (nominal 0.90)"),
                        ("hit_above", "the 95th-percentile exceedance, `y > q` (nominal 0.05)"),
                        ("hit_at_or_above", "the 95th-percentile exceedance, `y >= q` (nominal 0.05)")):
        out += [f"### {title}", "", "By lead, and pooled:", ""] + coverage_table(r, rule, ["pooled"] + leads)
        out += ["By target month:", ""] + coverage_table(r, rule, months)
    out += ["## 3. Grid CRPS and upper-tail twCRPS, paired", "",
            "Each cell of a table is the skill with its 90% interval and, after the semicolon, mean d (bp) with its 90% interval. The score is "
            "the mean over the leads 1 to 5; lower is better.", ""]
    for metric in METRIC_NAMES:
        out += [f"### Pooled: {METRIC_TITLES[metric]}", ""] + model_table(pooled[metric]) + [""]
    for metric in METRIC_NAMES:
        out += [f"### By lead: {METRIC_TITLES[metric]}", ""]
        for label, entry in r["groups"]["lead"].items():
            out += [f"**{label}**", ""] + model_table(entry[metric]) + [""]
    for metric in METRIC_NAMES:
        out += [f"### By target month: {METRIC_TITLES[metric]} (the current method)", ""]
        for label in months:
            entry = r["groups"].get("month", {}).get(label)
            out += ([f"**{label}** ({entry['days']} days)", ""] + model_table(entry[metric]) + [""]) if entry else \
                   [f"**{label}**: {r['month_counts'][label]} target days, listed and not tested.", ""]
    for metric in METRIC_NAMES:
        out += [f"### By target-day type: {METRIC_TITLES[metric]} (the current method; the groups overlap)", ""]
        for label in list(DAY_TYPES) + [ORDINARY, "calendar_days"]:
            entry = r["groups"].get("target_day_type", {}).get(label)
            if entry is None:
                count = r["skipped_groups"].get(f"target_day_type/{label}", r["day_type_counts"].get(label))
                out += [f"**{label}**: {count} target days, listed and not tested.", ""]
            else:
                out += [f"**{label}** ({entry['days']} days)", ""] + model_table(entry[metric]) + [""]
    out += ["## Reading under the declared rules (the mean-d bound, with the skill interval's reading beside it)", ""]
    for reference in (A,):
        for metric in METRIC_NAMES:
            parts = []
            for split in ("pooled", "month", "target_day_type"):
                for label, entry in r["groups"].get(split, {}).items():
                    parts.append(f"{label}: {reading_words(entry[metric]['vs'].get(S3, {}).get(reference))}")
            out.append(f"- **(s3)** against (a), {METRIC_TITLES[metric]}: " + "; ".join(parts) + ".")
    for reference, name in (("B1", "B1"), (B1P, "B1'"), ("B2", "B2")):
        parts = []
        for split in ("pooled", "month", "target_day_type"):
            for label, entry in r["groups"].get(split, {}).items():
                parts.append(f"{label}: {reading_words(entry['grid_crps']['vs'].get(S3, {}).get(reference))}")
        out.append(f"- **(s3)** against {name}, {METRIC_TITLES['grid_crps']}: " + "; ".join(parts) + ".")
    out.append("")
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## What this is not", "",
            "A check on development days that #845 and the #151 final test had already seen, never a verdict and not evidence for a choice. "
            "It adds no arm and tunes nothing. The `gbm_funding` comparison is a long run for Eleonora's Mac and was not asked for. "
            "The month and day-type intervals are the current method (#1221, queued as #1228); the pressure-day and upper-tail splits are "
            "thin because 2026 has few pressure days. Whether any of this changes what is claimed for (s3) is hers.", "",
            "**Question for Eleonora (no default needed; nothing waits on it):** the month and day-type rows above should be re-read when "
            "#1221 is decided (#1228). Until then they are not evidence for a pressure-day type either way.", ""]
    return "\n".join(out) + "\n"


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (a) and (s3) and score them")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--withheld", help="where the figures of #845 cells under the minimum go (not tracked)")
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of a coverage interval")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
