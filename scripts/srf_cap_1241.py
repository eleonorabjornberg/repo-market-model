"""The SRF minimum bid as a ceiling on (s3)'s upper tail: the measurement and the capped arms (#1241; H5 step 3, ledger item 58 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice
is in `metadata/srf_cap_1241.json`, which this script refuses to read unless it is committed and unchanged. The SRF line is
`repo_model.srf_line.srf_line_bps`: the Standing Repo Facility's minimum bid rate less the IORB in bp, read from
`metadata/policy_events.json` as it was public at the decision instant. The arms are (s3) of #1145 (the H5 candidate, unchanged, the
comparator) and three transforms of its forecast quantiles, each clipping every quantile at the line plus a margin of 0, 5 or 10 bp;
the primary is the margin of 0, named in the declaration before any score. The study measures (1) how often SOFR - IORB closed above
the line, (2) how often (s3)'s upper quantile levels sit above it, and (3) scores each cap arm against (s3), paired, with the scorer
of scoring protocol v1 (`repo_model.scoring_protocol`: grid CRPS over h = 1..5 and upper-tail twCRPS, the studentized stationary
bootstrap of ruling 1, read on the bound on mean d, her #1009 ruling, with the skill interval beside), and against B1, B1' (#960) and
B2 for context. Scored decision days are those whose five targets are on or before 2025-12-31; no later day is read and no locked day
is scored (`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640).

(s3) reads the calendar at the target day on direct pairs, so the walk is not calendar-blind and needs no provisional-register entry; the
cap fits nothing. It reuses the helpers of `scripts/calendar_mr_1115.py`, `scripts/state_calendar_1145.py`,
`scripts/s3_decomposition_1172.py` and `scripts/s3_terms_1196.py` (the frame, the cells, the groups, the readings).

The walk is minutes and the paired tests are the longer part, so the run is a cloud run. Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/srf_cap_1241.py score --panel PUB.csv --output docs/research/srf-cap-1241/result.json
    PYTHONPATH=src python3 scripts/srf_cap_1241.py page \\
        --score docs/research/srf-cap-1241/result.json --output docs/research/srf-cap-1241-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
from datetime import date, datetime, time
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


from repo_model import announced_iorb, b1_calendar as b1c, metrics, onset, policy_events, srf_line  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

c = _load("calendar_mr_1115")
s686, s761, b949 = c.s686, c.s761, c.b949
d1145 = _load("state_calendar_1145")
d1172 = _load("s3_decomposition_1172")
d1196 = _load("s3_terms_1196")

DECLARATION = REPO / "metadata" / "srf_cap_1241.json"
SEED = 1241
LAST_DAY = c.LAST_DAY
DECISION_TIME = c.DECISION_TIME
MIN_GROUP_DAYS = c.MIN_GROUP_DAYS
B1P = c.B1P
A = sc.ARM_A
S3 = sc.ARMS[2].name
#: The cap arms in the declaration's order: name -> margin in bp. The primary is the first.
MARGINS: Dict[str, float] = {"srf_cap_m0": 0.0, "srf_cap_m5": 5.0, "srf_cap_m10": 10.0}
PRIMARY = "srf_cap_m0"
CAPS = tuple(MARGINS)
#: The arms scored against the references, (s3) first.
ARMS = (S3,) + CAPS
BENCHMARKS = ("B1", B1P, "B2")
MODELS = BENCHMARKS + ARMS
METRIC_NAMES = c.METRIC_NAMES
REGIMES = c.REGIMES
DAY_TYPES = c.DAY_TYPES
ORDINARY = c.ORDINARY
#: The quantile levels from the median up, and the ones that carry an interval.
UPPER = tuple(i for i, p in enumerate(sp.GRID) if p >= 0.5)
KEY_LEVELS = (0.75, 0.9, 0.95, 0.975, 0.99)
Q95, Q99 = sp.GRID.index(0.95), sp.GRID.index(0.99)
#: The calibration measures of a cell reported here: the q95 exceedance under both hit rules.
RATES = ("hit_above", "hit_at_or_above")
CELL_BLOCK = c.CELL_BLOCK
BLOCK = float(sp.BLOCK_LENGTH)
FACILITY_GROUP = ("facility", "srf_days")
#: Intervals are given for a group of at least this many days or cells.
MIN_INTERVAL = 20


def verdict(row: Optional[dict]) -> str:
    """`identical` for a group the cap leaves unchanged; otherwise #1196's reading on the mean-d bound."""

    if row is not None and row.get("identical"):
        return "identical to (s3)"
    return d1196.verdict(row)


def skill_verdict(row: Optional[dict]) -> str:
    return "identical to (s3)" if row is not None and row.get("identical") else d1196.skill_verdict(row)


def reading_words(row: Optional[dict]) -> str:
    """`gain`, `loss`, `undecided` or `identical to (s3)` on the mean-d bound, with the skill interval's reading where it differs."""

    if row is not None and row.get("identical"):
        return "identical to (s3)"
    return d1196.reading_words(row)


def _fmt(row: Optional[dict]) -> str:
    """The cell of a table: `identical`, the protocol's skill and mean-d interval, or, where the studentized bound cannot be computed,
    `undefined` and beside it the unstudentized percentile interval of mean d (not the protocol's interval; no reading is taken from it)."""

    if row is not None and row.get("identical"):
        return "identical"
    text = d1172._fmt(row)
    extra = None if row is None else row.get("unstudentized")
    if extra is not None and "undefined" in row:
        text += f" (studentized bound not computed); unstudentized d {extra['mean_d']:+.3f} [{extra['interval'][0]:+.3f}, {extra['interval'][1]:+.3f}]"
    return text


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the line and the cap ---------------------------------------------------------------------------------------------


def decision_instant(day: date) -> datetime:
    """The instant a decision on `day` is made, a naive America/New_York wall-clock datetime."""

    return datetime.combine(day, DECISION_TIME)


def lines_of(frame, register: Sequence[policy_events.PolicyEntry]) -> Dict[Tuple[date, int], Optional[float]]:
    """The line a forecast of each (decision day, lead) cell could use: what the register announced by the decision instant gives."""

    return {(d, h): srf_line.srf_line_bps(register, decision_instant(d), frame.target(d, h)) for d in frame.days for h in sp.HORIZONS}


def realised_line(register: Sequence[policy_events.PolicyEntry], day: date) -> Optional[float]:
    """The line in force on `day`, from everything announced by the end of that day (an ex post description, not a forecast input)."""

    return srf_line.srf_line_bps(register, datetime.combine(day, time(23, 59, 59)), day)


def capped(forecasts: Mapping[date, Mapping[int, Sequence[float]]], lines: Mapping[Tuple[date, int], Optional[float]],
           margin: float) -> Dict[date, Dict[int, List[float]]]:
    """(s3)'s forecasts with each cell's quantiles clipped at its line plus `margin` (unchanged where the cell has no line)."""

    return {d: {h: srf_line.cap_quantiles(q, lines[(d, h)], margin) for h, q in per_h.items()} for d, per_h in forecasts.items()}


# -- the frame -------------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, table, states, register, first: Optional[date] = None):
    """The decision days with a forecast of every model, whose five targets are scored days.

    `first` starts the walk later than the declared study does; it exists for the test of this script, and the declared run never
    passes it.
    """

    frame = s686.Frame(panel, splits, registry, None)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY and (first is None or day >= first)
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)
    b1, b1p, b2, dropped = {}, {}, {}, []
    for day in candidate_days:
        index = frame.position[day]
        try:
            one = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            prime = b1c.b1_calendar_forecast(panel, index, **settings)
            two = pb.b2_forecast(panel, index, **settings)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
            continue
        b1[day], b1p[day], b2[day] = one, prime, two
    mine = sc.walk(panel, candidate_days, table, states, (sc.ARMS[2],), **settings)
    days = [d for d in candidate_days if d in b1 and d in mine.forecasts[S3]]
    frame.days = days
    lines = lines_of(frame, register)
    s3 = {d: mine.forecasts[S3][d] for d in days}
    frame.forecasts = {"B1": b1, B1P: b1p, "B2": b2, S3: s3, **{a: capped(s3, lines, MARGINS[a]) for a in CAPS}}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(mine.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(mine.fits),
    }
    return frame, notes, mine, lines


def cell_table(frame, forecasts):
    """Both scores and the calibration hits of every (decision day, lead) cell of `forecasts` (`state_calendar_1145.cell_table`)."""

    return d1145.cell_table(frame, forecasts)


# -- the groups ------------------------------------------------------------------------------------------------------


def pressure_labels(frame, targets: Sequence[date]) -> Dict[date, str]:
    """The pressure-day type of each target day: the turn record in force (`turn_days.reporting_day_type`)."""

    return {t: frame.day_type(t) for t in targets}


def groups_of(frame, labels, pressure: Mapping[date, str], lines: Mapping[Tuple[date, int], Optional[float]]):
    """`(split, label, grain, members)`: #1115's groups, then the pressure-day types and the SRF-regime target days."""

    out = c.groups_of(frame, labels)
    by_type: Dict[str, List[date]] = {}
    for t in sorted(pressure):
        by_type.setdefault(pressure[t], []).append(t)
    for label in sorted(by_type):
        out.append(("pressure_day_type", label, "target", by_type[label]))
    facility = sorted({frame.target(d, h) for (d, h), line in lines.items() if line is not None})
    if facility:
        out.append((*FACILITY_GROUP, "target", facility))
    return out


# -- the tests, in parallel ------------------------------------------------------------------------------------------

_STATE: Dict = {}


def pair_plan(candidate: str) -> List[str]:
    """What a candidate is tested against: B1, B1' and B2, and (s3) for every cap arm."""

    return list(BENCHMARKS) + ([S3] if candidate != S3 else [])


def block_plan(candidate: str) -> List[str]:
    """What the Politis-White block is reported against: (s3) for every cap arm."""

    return [] if candidate == S3 else [S3]


def _identical(series, candidate: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[S3][d] for d in members)


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in pair_plan(candidate):
        days = list(members)
        if len(days) < MIN_GROUP_DAYS:
            continue
        if name == S3 and _identical(series, candidate, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"],
                                  mean_d_fallback=True)[name]
        if name == S3 and "undefined" in out[name]:
            out[name]["unstudentized"] = unstudentized_mean_d(series, candidate, days)
    return (split, label, metric, candidate), out


def unstudentized_mean_d(series, candidate: str, members: Sequence[date]) -> dict:
    """Mean d against (s3) and its 90% stationary-bootstrap percentile interval (mean block 10, in date order), for a group whose
    studentized bound cannot be computed (most of its days score alike). It is not the protocol's interval and no reading is taken
    from it; it only shows which way the mean difference points. `d = S((s3)) - S(candidate)`, positive favours the candidate."""

    d = [series[S3][x] - series[candidate][x] for x in sorted(members)]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=BLOCK, seed=SEED, replications=_STATE["reps"])
    return {"mean_d": sum(d) / len(d), "interval": [low, high], "days": len(d)}


def _block_task(job):
    """The Politis-White block of the paired loss differential of a cap arm against (s3), and the pooled interval at that block."""

    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = sorted(members)
    out: Dict[str, Optional[dict]] = {}
    for reference in block_plan(candidate):
        if _identical(series, candidate, ordered):
            out[reference] = None
            continue
        d = [series[reference][x] - series[candidate][x] for x in ordered]
        try:
            block = b949.politis_white(d)
        except ValueError:
            out[reference] = None
            continue
        entry = {"block": block, "days": len(ordered)}
        if split == "pooled":
            at = max(1, round(block))
            entry["at_block"] = at
            try:
                test = sp.paired_tests([({x: series[reference][x] for x in ordered}, {x: series[candidate][x] for x in ordered})],
                                       seed=SEED, draws=_STATE["draws"], block_length=float(at))[0]
                entry["row"] = s761.paired_row(test)
            except sp.ProtocolError as error:
                # a cap that moves a few days only leaves resamples with no variance (the first full run died here); say so, never drop it
                entry["undefined"] = str(error)
        out[reference] = entry
    return (split, label, metric, candidate), out


def _interval_task(job):
    kind, key, values, block = job
    n = len(values)
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx), n, block_length=block, seed=SEED, replications=_STATE["reps"])
    return (kind, key), [low, high]


def _dispatch(job):
    kind, payload = job
    if kind == "pairs":
        return kind, _pairs_task(payload)
    if kind == "block":
        return kind, _block_task(payload)
    return kind, _interval_task(payload)


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- the measurements ------------------------------------------------------------------------------------------------


def quantile7(values: Sequence[float], p: float) -> float:
    """The `p` quantile by linear interpolation between order statistics (type 7)."""

    ordered = sorted(values)
    if not ordered:
        raise ValueError("no values")
    rank = p * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (rank - low) * (ordered[high] - ordered[low])


def realised_days(frame, register, targets: Sequence[date]) -> List[dict]:
    """For each target day with a line: the spread, the line in force that day and the excess on whole basis points."""

    rows = []
    for t in sorted(targets):
        line = realised_line(register, t)
        if line is None:
            continue
        spread = frame.outcome[t]
        rows.append({"date": t, "spread": spread, "line": line, "excess": onset.whole_bp(spread) - line,
                     "regime": frame.regime(t), "type": frame.day_type(t)})
    return rows


def realised_tables(rows: Sequence[dict], jobs: List) -> dict:
    """Measure 1: per group, the days, the count above the line, the share (an interval job), the largest and the 99th percentile."""

    groups: Dict[str, List[dict]] = {"pooled": list(rows)}
    for r in rows:
        groups.setdefault(f"regime/{r['regime']}", []).append(r)
        groups.setdefault(f"pressure_day_type/{r['type']}", []).append(r)
    out: dict = {}
    for name, members in groups.items():
        excess = [m["excess"] for m in members]
        above = [m for m in members if m["excess"] > 0]
        top = sorted(members, key=lambda m: (-m["excess"], m["date"]))[:10]
        out[name] = {
            "days": len(members), "above": len(above), "share": len(above) / len(members),
            "largest": [{"date": m["date"].isoformat(), "spread": m["spread"], "line": m["line"], "excess": m["excess"]} for m in top],
            "excess_p99": quantile7(excess, 0.99), "excess_max": max(excess),
            "excess_p99_among_above": quantile7([m["excess"] for m in above], 0.99) if above else None,
            "interval": None,
        }
        if len(members) >= MIN_INTERVAL:
            jobs.append(("interval", ("realised", name, [1.0 if m["excess"] > 0 else 0.0 for m in members], BLOCK)))
    return out


def forecast_cells(frame, lines, pressure: Mapping[date, str]) -> List[dict]:
    """The (s3) cells whose target has a line, in (decision day, lead) order, with what the tables split by."""

    cells = []
    for d in frame.days:
        for h in sp.HORIZONS:
            line = lines[(d, h)]
            if line is None:
                continue
            t = frame.target(d, h)
            cells.append({"d": d, "h": h, "line": line, "q": frame.forecasts[S3][d][h], "regime": frame.regime(t), "type": pressure[t]})
    return cells


def forecast_tables(cells: Sequence[dict], jobs: List) -> dict:
    """Measure 2: per split, lead and level from the median up, the share of cells whose quantile is strictly above the line; and
    per cap arm the share of cells in which the cap moves the 0.95 and the 0.99 level."""

    splits: Dict[str, List[dict]] = {"pooled": list(cells)}
    for cell in cells:
        splits.setdefault(f"regime/{cell['regime']}", []).append(cell)
        splits.setdefault(f"pressure_day_type/{cell['type']}", []).append(cell)
    out: dict = {"levels": [sp.GRID[i] for i in UPPER], "splits": {}}
    for name, members in splits.items():
        per_lead: Dict[str, dict] = {}
        for lead in ("all",) + tuple(str(h) for h in sp.HORIZONS):
            kept = members if lead == "all" else [m for m in members if m["h"] == int(lead)]
            entry: dict = {"cells": len(kept), "share_above": {}, "interval": {}, "binds": {}}
            if kept:
                for i in UPPER:
                    values = [1.0 if m["q"][i] > m["line"] else 0.0 for m in kept]
                    entry["share_above"][str(sp.GRID[i])] = sum(values) / len(values)
                    if len(kept) >= MIN_INTERVAL and sp.GRID[i] in KEY_LEVELS:
                        jobs.append(("interval", ("forecast", (name, lead, str(sp.GRID[i])), values, CELL_BLOCK if lead == "all" else BLOCK)))
                for arm in CAPS:
                    margin = MARGINS[arm]
                    entry["binds"][arm] = {
                        "q95": sum(1 for m in kept if m["q"][Q95] > m["line"] + margin) / len(kept),
                        "q99": sum(1 for m in kept if m["q"][Q99] > m["line"] + margin) / len(kept),
                    }
            per_lead[lead] = entry
        out["splits"][name] = per_lead
    return out


# -- the score -------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=DECISION_TIME)
    states = d1145.decision_states(c.SOURCES)
    frame, notes, mine, lines = build_frame(panel, splits, registry, table, states, register, args.first)
    published_sha = panel_sha256(panel_path)
    days = frame.days
    labels = c.day_labels(frame, table)
    targets = sorted(labels)
    pressure = pressure_labels(frame, targets)

    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    groups = groups_of(frame, labels, pressure, lines)
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
                if candidate != S3 and split in ("pooled", "regime"):
                    jobs.append(("block", (split, label, grain, metric, candidate, tuple(members))))
    # calibration: the q95 exceedance under both hit rules, pooled, by regime and on the SRF-regime cells
    cell_groups: Dict[Tuple[str, str], List[Tuple[date, int]]] = {}
    facility_cells = {(d, h) for (d, h), line in lines.items() if line is not None}
    for m in MODELS:
        keys = sorted(cells[m]["hit_above"])
        cell_groups[(m, "pooled/all cells")] = keys
        kept = [k for k in keys if k in facility_cells]
        if len(kept) >= MIN_GROUP_DAYS:
            cell_groups[(m, "facility/srf cells")] = kept
        for regime in REGIMES:
            kept = [k for k in keys if frame.regime(frame.target(*k)) == regime]
            if len(kept) >= MIN_GROUP_DAYS:
                cell_groups[(m, f"regime/{regime}")] = kept
    for (m, name), keys in cell_groups.items():
        for rule in RATES:
            jobs.append(("interval", ("calib", (rule, m, name), [cells[m][rule][k] for k in keys], CELL_BLOCK)))
    rows = realised_days(frame, register, targets)
    realised = realised_tables(rows, jobs)
    forecast = forecast_tables(forecast_cells(frame, lines, pressure), jobs)
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1241, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "notes": notes, "models": list(MODELS), "primary": PRIMARY,
        "arms": [{"name": S3, "margin_bp": None}] + [{"name": a, "margin_bp": MARGINS[a]} for a in CAPS],
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.phi} for day, fit in sorted(mine.fits.items())],
        "groups": {}, "skipped_groups": skipped, "politis_white": {}, "q95": {}, "realised": realised, "forecast": forecast,
        "reading_rules": declaration["reading_rules"],
        "line": line_segments(register, frame),
    }
    for kind, (ident, payload) in done:
        if kind == "pairs":
            split, label, metric, candidate = ident
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = payload
        elif kind == "block":
            split, label, metric, candidate = ident
            result["politis_white"].setdefault(split, {}).setdefault(label, {}).setdefault(metric, {})[candidate] = payload
        else:
            tag, key = ident
            if tag == "realised":
                realised[key]["interval"] = payload
            elif tag == "forecast":
                name, lead, level = key
                forecast["splits"][name][lead]["interval"][level] = payload
            else:
                rule, m, name = key
                result["q95"].setdefault(name, {}).setdefault(m, {})[rule] = {"interval": payload}
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in METRIC_NAMES:
                if metric not in entry:
                    continue
                ser = series[(grain, metric)]
                entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    for name, by_model in result["q95"].items():
        for m, rules in by_model.items():
            keys = cell_groups[(m, name)]
            for rule in rules:
                values = [cells[m][rule][k] for k in keys]
                rules[rule]["rate"] = sum(values) / len(values)
                rules[rule]["cells"] = len(values)
    result["day_type_counts"] = {k: sum(1 for t in labels if k in labels[t]) for k in DAY_TYPES + (ORDINARY,)}
    result["pressure_day_type_counts"] = {k: sum(1 for t in pressure.values() if t == k) for k in sorted(set(pressure.values()))}
    result["cells_with_a_line"] = len(facility_cells)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def line_segments(register, frame) -> List[dict]:
    """The line over the scored target days, as the runs of days that share a value: from, to, bp, and the entries that set it."""

    out: List[dict] = []
    for t in sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS}):
        value = realised_line(register, t)
        if value is None:
            continue
        if out and out[-1]["bp"] == value:
            out[-1]["to"] = t.isoformat()
            out[-1]["days"] += 1
        else:
            out.append({"from": t.isoformat(), "to": t.isoformat(), "bp": value, "days": 1})
    return out


# -- the page --------------------------------------------------------------------------------------------------------

LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3: "(s3) the H5 candidate",
          "srf_cap_m0": "cap at the line (margin 0 bp; the primary)", "srf_cap_m5": "cap at the line + 5 bp",
          "srf_cap_m10": "cap at the line + 10 bp"}
METRIC_TITLES = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})"}
SPLIT_TITLES = {"pooled": "all decision days", "regime": "regime", "pressure_day_type": "pressure-day type",
                "target_day_type": "calendar target-day type", "facility": "SRF-regime target days"}


def _pct(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{100 * value:.1f}%"


def _pct_ci(value: float, interval: Optional[Sequence[float]]) -> str:
    return _pct(value) if interval is None else f"{_pct(value)} [{_pct(interval[0])}, {_pct(interval[1])}]"


def model_table(cell: dict) -> List[str]:
    """Mean score of every model in one group, and each cap arm's skill over (s3), B1, B1' and B2, each with the mean-d bound beside it."""

    out = ["| | mean | vs (s3): skill [90%]; mean d (bp) [90%] | vs B1 | vs B1' | vs B2 |", "|---|---|---|---|---|---|"]
    means = cell["means"]
    for name in BENCHMARKS:
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | | | | |")
    for name in ARMS:
        vs = cell["vs"].get(name, {})
        first = "" if name == S3 else _fmt(vs.get(S3))
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | {first} | " + " | ".join(_fmt(vs.get(b)) for b in BENCHMARKS) + " |")
    return out


def tally(r: dict, arm: str, metric: str = "grid_crps") -> Dict[str, int]:
    """The regimes in which the arm's mean-d bound against (s3) reads as a gain, a loss, undecided, identical or not computed."""

    count = {"gain": 0, "loss": 0, "undecided": 0, "identical": 0, "no reading": 0}
    for label in REGIMES:
        entry = r["groups"].get("regime", {}).get(label)
        if entry is None:
            continue
        row = entry[metric]["vs"].get(arm, {}).get(S3)
        if row is not None and row.get("identical"):
            count["identical"] += 1
        elif row is not None and "undefined" in row:
            count["no reading"] += 1
        else:
            count[d1172.verdict(row) if row is not None else "undecided"] += 1
    return count


def summary_rows(r: dict) -> List[str]:
    """The pooled and SRF-regime reading of each cap arm against (s3), on both measures, with the regime tally."""

    out = ["| arm | split | grid CRPS vs (s3) | twCRPS vs (s3) | regimes, grid CRPS (gain / loss / undecided / identical) |", "|---|---|---|---|---|"]
    for arm in CAPS:
        for split, label in (("pooled", "all decision days"), FACILITY_GROUP):
            entry = r["groups"].get(split, {}).get(label)
            if entry is None:
                continue
            t = tally(r, arm)
            out.append(
                f"| {LABELS[arm]} | {SPLIT_TITLES[split] if split != 'pooled' else 'all decision days'} ({entry['days']} days) | "
                f"{_fmt(entry['grid_crps']['vs'].get(arm, {}).get(S3))}: **{reading_words(entry['grid_crps']['vs'].get(arm, {}).get(S3))}** | "
                f"{_fmt(entry['upper_tail_twcrps']['vs'].get(arm, {}).get(S3))}: **{reading_words(entry['upper_tail_twcrps']['vs'].get(arm, {}).get(S3))}** | "
                f"{t['gain']} / {t['loss']} / {t['undecided']} / {t['identical']}" + (f" / {t['no reading']} no reading" if t["no reading"] else "") + " |")
    return out


def realised_table(r: dict, names: Sequence[str]) -> List[str]:
    out = ["| group | days | above the line | share [90%] | 99th percentile of spread - line (bp) | largest excess (bp) |", "|---|---|---|---|---|---|"]
    for name in names:
        e = r["realised"].get(name)
        if e is not None:
            out.append(f"| {name} | {e['days']} | {e['above']} | {_pct_ci(e['share'], e['interval'])} | {e['excess_p99']:+.1f} | {e['excess_max']:+.1f} |")
    return out


def forecast_table(r: dict, split: str, levels: Sequence[str]) -> List[str]:
    entry = r["forecast"]["splits"].get(split)
    if entry is None:
        return []
    out = ["| lead | cells | " + " | ".join(f"q{l}" for l in levels) + " |", "|---|---|" + "---|" * len(levels)]
    for lead in ("all",) + tuple(str(h) for h in sp.HORIZONS):
        e = entry[lead]
        if not e["cells"]:
            continue
        out.append(f"| {'all leads' if lead == 'all' else 'h=' + lead} | {e['cells']} | " + " | ".join(
            _pct_ci(e["share_above"][l], e["interval"].get(l)) for l in levels) + " |")
    return out


def _levels(r: dict) -> List[str]:
    return [str(p) for p in r["forecast"]["levels"]]


def render(r: dict) -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# The SRF minimum bid as a ceiling on (s3)'s upper tail (#1241)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (the candidate's upper tail), ledger item 58 on #1116. **Development data, not a "
        f"verdict** (scoring protocol v1, #640): days to {n['last_target']}, no lockbox day. Nothing is adopted and no claim changes. "
        f"Generated by `scripts/srf_cap_1241.py page` from `docs/research/srf-cap-1241/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any number.", "",
        "**What kind of look this is.** The Standing Repo Facility's minimum bid rate is an administered rate above the spread "
        "(`docs/decisions/pressure-probability.md`), and no H5 model reads it. If it caps repo rates, the upper quantiles of (s3) may be "
        "too wide in the facility's regime, which costs grid CRPS and upper-tail twCRPS. This is a look at 2021-2025 after (s3) was chosen on "
        "those days, aimed at the upper tail; a gain is evidence for a question, with the selection noted. Whether a cap becomes part of the "
        "candidate is Eleonora's decision on this page.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Skill is "
        "`mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`, positive favours the candidate. **Every row shows the skill "
        "interval and, beside it, the studentized interval on mean d (bp); a reading (gain, loss, undecided) is taken from the mean-d bound** "
        "(her ruling on #1009, 20 October 2026). **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is "
        "understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals of a "
        "pressure-day-type or calendar-day-type group keep the current method (the days of a type, scattered, resampled in date order as if "
        "consecutive), which #1221 questions. **Where a cap changes only a few days of a group, the studentized bound cannot be computed** (a resample "
        "has no long-run variance): the cell reads \"undefined\", no reading is taken, and the unstudentized percentile interval of mean d "
        "(the same stationary bootstrap, mean block 10, not the protocol's interval) is shown beside it so the direction is visible. **The two "
        "scores move by the same amount here**: a cap changes a forecast only above the line, which is above 0 bp, where the weight of the "
        "upper-tail twCRPS is 1, so mean d on grid CRPS and on twCRPS is the same number in every group and the two readings agree; the "
        f"tables show both because the protocol names both. Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); the "
        f"fit is renewed {n['refits']} times. The pressure-day types are the month-end turn record in force (#1161) and B2 reads the thin-pool "
        "record in force (#1198), so (s3) and B2 are not the figures of pages scored on earlier labels.", "",
        "**The line.** `repo_model.srf_line` reads the minimum bid rate less the IORB, in bp, from `metadata/policy_events.json`, as public "
        "at the decision instant (16:00 on the decision day): an entry announced after it is not known, and one announced and scheduled "
        "for the target day is. Nothing writes +10 bp into the code. Before the facility (effective 2021-07-29) there is no line and every cap "
        "arm equals (s3). The line on the scored target days:", "",
        "| from | to | line (bp) | target days |", "|---|---|---|---|"]
    out += [f"| {s['from']} | {s['to']} | {s['bp']:+.1f} | {s['days']} |" for s in r["line"]]
    primary = r["primary"]
    out += ["", f"**The arms.** (s3) of #1145 is unchanged. Each cap arm clips every quantile of (s3) at the line plus a margin of 0, 5 or 10 bp "
            f"(`min(q, line + margin)`, monotone, so the levels stay ordered); days before the facility are unchanged. **The primary, named in "
            f"the declaration before any score, is {LABELS[primary]}**; the other two are sensitivity arms. The cap fits nothing; (s3)'s walk reads "
            "the calendar at the target day on direct pairs, so the class is not provisional.", "",
            "## What the step had to show, and whether it showed it", "",
            "It had to show (1) how often SOFR - IORB closed above the line, (2) how often (s3)'s upper quantiles sit above it, and (3) whether "
            "capping them at the line helps or costs. The readings are from the mean-d bound; the pooled row includes the decision days "
            "whose targets precede the facility, which no cap moves, so the SRF-regime row is the one the cap can change.", ""]
    out += summary_rows(r)
    out += ["", "## 1. Realised: how often SOFR - IORB closed above the line", "",
            "On the target days of the scored decisions that are on or after 2021-07-29. A day is above the line when its spread, read on whole "
            "basis points, is strictly above the line in force that day (docs/decisions/pressure-probability.md, #155). The share carries a 90% "
            "stationary-bootstrap percentile interval over the days in date order (mean block 10).", ""]
    names = ["pooled"] + [f"regime/{l}" for l in REGIMES if f"regime/{l}" in r["realised"]]
    out += realised_table(r, names) + ["", "By pressure-day type:", ""]
    out += realised_table(r, [k for k in r["realised"] if k.startswith("pressure_day_type/")]) + ["", "The largest exceedances, with their dates:", "",
            "| date | spread (bp) | line (bp) | excess (bp) |", "|---|---|---|---|"]
    out += [f"| {x['date']} | {x['spread']:+.1f} | {x['line']:+.1f} | {x['excess']:+.1f} |" for x in r["realised"]["pooled"]["largest"]]
    for label in ("regime/2021-23", "regime/2025-26"):
        e = r["realised"].get(label)
        if e is not None:
            out += ["", f"The largest in {label.split('/')[1]}:", "", "| date | spread (bp) | line (bp) | excess (bp) |", "|---|---|---|---|"]
            out += [f"| {x['date']} | {x['spread']:+.1f} | {x['line']:+.1f} | {x['excess']:+.1f} |" for x in e["largest"][:5]]
    out += ["", "## 2. Forecast: how often (s3)'s upper quantile levels sit above the line", "",
            "Share of the (decision day, lead) cells whose target day has a line in which (s3)'s quantile is strictly above the line known at "
            "the decision instant. Levels from the median; an interval (stationary bootstrap over the cells in date order, mean block 10 cells "
            "per lead and 50 over all leads) for the five key levels. The point shares of the other levels are in `result.json`.", ""]
    levels = [str(p) for p in KEY_LEVELS]
    for split in ["pooled"] + [f"regime/{l}" for l in REGIMES if f"regime/{l}" in r["forecast"]["splits"]]:
        out += [f"**{split}**", ""] + forecast_table(r, split, levels) + [""]
    out += ["By pressure-day type of the target day, all leads:", "", "| type | cells | " + " | ".join(f"q{l}" for l in levels) + " |",
            "|---|---|" + "---|" * len(levels)]
    for split, per_lead in r["forecast"]["splits"].items():
        if split.startswith("pressure_day_type/") and per_lead["all"]["cells"]:
            e = per_lead["all"]
            out.append(f"| {split.split('/')[1]} | {e['cells']} | " + " | ".join(_pct_ci(e["share_above"][l], e["interval"].get(l)) for l in levels) + " |")
    out += ["", "How often each cap arm changes the forecast, as the share of the same cells in which (s3)'s level is above the ceiling "
            "(line plus margin):", "", "| split | cells | " + " | ".join(f"{LABELS[a]}: q95 / q99" for a in CAPS) + " |", "|---|---|" + "---|" * len(CAPS)]
    for split in ["pooled"] + [f"regime/{l}" for l in REGIMES if f"regime/{l}" in r["forecast"]["splits"]]:
        e = r["forecast"]["splits"][split]["all"]
        out.append(f"| {split} | {e['cells']} | " + " | ".join(f"{_pct(e['binds'][a]['q95'])} / {_pct(e['binds'][a]['q99'])}" for a in CAPS) + " |")
    out += ["", "## 3. Score: each cap arm against (s3), paired", ""]
    for split, label in (("pooled", "all decision days"), FACILITY_GROUP):
        entry = r["groups"].get(split, {}).get(label)
        if entry is None:
            continue
        for metric in METRIC_NAMES:
            out += [f"### {SPLIT_TITLES[split]}: {METRIC_TITLES[metric]}, mean over leads 1 to 5 (bp) ({entry['days']} days)", ""] + model_table(entry[metric]) + [""]
    for split, order in (("regime", REGIMES), ("pressure_day_type", sorted(r["groups"].get("pressure_day_type", {}))),
                         ("target_day_type", list(DAY_TYPES) + [ORDINARY, "calendar_days"]), ("lead", [f"h={h}" for h in sp.HORIZONS])):
        for metric in METRIC_NAMES:
            title = {"regime": "regime (target day)", "pressure_day_type": "pressure-day type (turn record in force; target day)",
                     "target_day_type": "calendar target-day type (the groups overlap)", "lead": "lead"}[split]
            out += [f"### {METRIC_TITLES[metric]} by {title}", ""]
            for label in order:
                entry = r["groups"].get(split, {}).get(label)
                if entry is not None:
                    out += [f"**{label}** ({entry['days']} days)", ""] + model_table(entry[metric]) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["A group in which a cap arm's score equals (s3)'s on every day (a group wholly before the facility) reads \"identical\" and is not tested.", "",
            "## The Politis-White block beside the block of 10", "",
            "The automatic block length (Politis and White 2004, with the correction of Patton, Politis and White 2009) of the paired loss "
            "differential `S((s3)) - S(arm)`, in days, with the pooled skill over (s3) at that block. Reported, never substituted for 10.", ""]
    columns = ["pooled"] + [l for l in REGIMES if l in r["politis_white"].get("regime", {})]
    for metric in METRIC_NAMES:
        out += [f"{METRIC_TITLES[metric]}, against (s3):", "", "| | " + " | ".join(columns) + " | pooled skill at that block |", "|---|" + "---|" * (len(columns) + 1)]
        for name in CAPS:
            cells, at = [], ""
            for col in columns:
                split, label = ("pooled", "all decision days") if col == "pooled" else ("regime", col)
                e = (r["politis_white"].get(split, {}).get(label, {}).get(metric, {}).get(name) or {}).get(S3)
                cells.append("n/a" if not e else f"{e['block']:.1f}")
                if col == "pooled" and e and "row" in e:
                    at = f"block {e['at_block']}: {_fmt(e['row'])}"
                elif col == "pooled" and e and "undefined" in e:
                    at = f"block {e['at_block']}: undefined ({e['undefined']})"
            out.append(f"| {LABELS[name]} | " + " | ".join(cells) + f" | {at} |")
        out.append("")
    names = list(r["q95"])
    for rule, title in (("hit_above", "the 95th-percentile exceedance rate, hit when `y > q` (nominal 0.05)"),
                        ("hit_at_or_above", "the 95th-percentile exceedance rate, hit when `y >= q` (nominal 0.05)")):
        out += [f"## Calibration: {title}", "", "Share of (decision day, lead) cells, with a 90% stationary-bootstrap percentile interval over the cells in "
                "date order (mean block 50 cells). `facility/srf cells` are the cells whose target has a line.", "",
                "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
        for m in MODELS:
            cells = []
            for name in names:
                e = r["q95"][name].get(m, {}).get(rule)
                cells.append("n/a" if e is None else f"{e['rate']:.3f} [{e['interval'][0]:.3f}, {e['interval'][1]:.3f}]")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["The two hit rules agree to within a tie of the outcome with a quantile; which rule counts is Eleonora's open question (#993), so both "
            "are above and in `result.json`.", "",
            "## What this is not", "",
            "Development data from 2018 to 2025, split by regime and pressure-day type, never a verdict. The cap arms are a transform of (s3)'s "
            "forecast with one declared margin each; no margin, line or threshold was tried before the declaration, and the primary was named "
            "before any score. The days on which SOFR closed above the SRF rate are the days a hard cap costs, and the realised table lists "
            "them; the margins of 5 and 10 bp are the sensitivity to that. The regime rows are the ones to read before the pooled one. "
            + line_sentence(r) + " Whether a cap becomes part of the candidate is her decision.", ""]
    out += question(r)
    return "\n".join(out) + "\n"


def line_sentence(r: dict) -> str:
    """What the line did over the scored days, from the segments of the record."""

    segments = r["line"]
    if len(segments) == 1:
        return (f"The line is {segments[0]['bp']:+.1f} bp on every scored target day that has one, as the register's arrangement of the minimum bid "
                "and IORB gives it; a change of that arrangement would show as a new segment in the table above.")
    return "The line takes more than one value over the scored days; the table above lists the segments."


def question(r: dict) -> List[str]:
    """The closing question for Eleonora: whether a cap becomes part of the H5 candidate."""

    groups = r["groups"]
    cols = [("pooled", "all decision days", "pooled"), (*FACILITY_GROUP, "SRF-regime days")] + [("regime", l, l) for l in REGIMES if l in groups.get("regime", {})]
    out = ["## Question for Eleonora: does a cap become part of the H5 candidate?", "",
           "Your ruling of 26 October 2026 on #1241 asked for the avenue to be pursued and left the decision to you after this page. **Nothing is "
           "adopted here and no claim changes.** The tables give the mean score of (s3) and the three cap arms (lower is better; B1, B1' and "
           "B2 are in the tables above).", ""]
    for metric, title in (("grid_crps", "Grid CRPS (bp)"), ("upper_tail_twcrps", "Upper-tail twCRPS (bp)")):
        out += [f"**{title}**", "", "| | " + " | ".join(col[2] for col in cols) + " |", "|---|" + "---|" * len(cols)]
        for m in ARMS:
            cells = []
            for split, label, _name in cols:
                entry = groups.get(split, {}).get(label)
                cells.append("n/a" if entry is None or m not in entry[metric]["means"] else f"{entry[metric]['means'][m]:.3f}")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["**Options** (numbered; the default applies if you have not answered by the next 5 pm batch):", "",
            "1. **Keep (s3) as the H5 candidate, with no cap** (default). Nothing changes; the cap arms stay development results.",
            "2. **Take a cap into the candidate (which margin: your choice)**, on the evidence above. That is a decision for you and would be "
            "followed by a registration discussion; this page does not pre-empt it.",
            "3. **Ask for a further step** before deciding (for example the cap on the 2026 development days, or a cap that depends on the "
            "regime or on the day type).", "",
            "A separate question: the SRF line is declared in `metadata/srf_cap_1241.json` and not in `metadata/sources.json`, because that file "
            "is pinned by digests in declarations already merged. Whether to register it there is yours."]
    return out


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3), cap it and score the arms")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of a rate interval")
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
