"""(s3c-ann-net-qe): a shrunk residual multiplier on quarter-end target days only, beside the frozen candidate (s3c-ann-net), at the 18:00 decision
instant (#1531; H5 step 3, arm A of her ruling of 9 November 2026).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/qe_shrunk_scale_1531.json`, which this script refuses to read unless it is committed and unchanged. The candidate (s3c-ann-net) stays frozen.

The candidate's quantiles are `centre + scale * (shift + pool_j)`. On a target day whose `turn_days.reporting_day_type` is `quarter_end_turn` or `year_end`
the arm replaces the pool's spread about its median by `m` times it (`repo_model.day_type_scale.rescaled`), `m = 1 + w (m_raw - 1)`, `w = n / (n + k)`,
`m_raw` #1402's root-mean-square ratio of the group's training residuals to all of them, `n` the group's training pairs at that refit and lead, and `k`
the declared constant (a question for her in the pull request). On every other target day the arm's quantiles are the candidate's, bit for bit: the walk
fails otherwise (`outside_group_identical`).

On the group it measures, by horizon and pooled, the 90% coverage, the lower (below q05) and upper (above q95) tail miss rates, the q01 and q99 miss
rates, grid CRPS and upper-tail twCRPS, the arm against the candidate on the same cells, with 90% intervals from a cluster bootstrap over turn events
(the h = 1..5 forecasts aimed at one turn and the turn's two days are one cluster). Pooled and by regime and pressure-day type it scores the arm and the
candidate against B1, B1' and B2 (grid CRPS, upper-tail twCRPS) and B3 (the published record's five levels) on scoring protocol v1's studentized
stationary bootstrap. The 2026 development days are a window of their own and decide nothing.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/qe_shrunk_scale_1531.py score --panel PUB.csv \\
        --output docs/research/qe-shrunk-scale-1531/result.json
    PYTHONPATH=src python3 scripts/qe_shrunk_scale_1531.py page \\
        --score docs/research/qe-shrunk-scale-1531/result.json --output docs/research/qe-shrunk-scale-1531-result.md

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
        return held
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import day_type_scale as dts  # noqa: E402
from repo_model import policy_events, announced_iorb  # noqa: E402
from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1402's script (and through it #1321's chain), loaded under an alias of its own so that the worker pool's pickling does not meet another module's copy.
m1402 = _load("day_type_scale_1402", "day_type_scale_1402_in_1531")
m1533 = _load("qe_diagnosis_1533", "qe_diagnosis_1533_in_1531")
m1321, m1288, m1273, m1255, k_mod, c, s686, s761 = (
    m1402.m1321, m1402.m1288, m1402.m1273, m1402.m1255, m1402.k, m1402.c, m1402.s686, m1402.s761)
load_daily_panel = m1402.load_daily_panel

DECLARATION = REPO / "metadata" / "qe_shrunk_scale_1531.json"
RECORD_1314 = m1402.RECORD_1314
B3_DAILY = REPO / "docs" / "runs" / "published_distribution_daily_h{h}.json"
B3_LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
SEED = 1531
#: The shrinkage constant, as the declaration writes it (checked against it when the study runs).
K = 20
EVENT_REPS = 2000
LAST_DAY = EXPLORATORY_END
WINDOWS = m1288.WINDOWS
WINDOW_LAST = m1288.WINDOW_LAST
WINDOW_TITLES = m1288.WINDOW_TITLES
ANNNET = m1288.ANNNET
ARM = "sc_s3c_ann_net_qeshrunk"
ARM_NET = m1402.ARM_NET
REFERENCES = tuple(m1288.BENCHMARKS)  # B1, B1_prime, B2
MODELS = REFERENCES + (ANNNET, ARM)
LABELS = {ANNNET: "(s3c-ann-net)", ARM: "(s3c-ann-net-qe)", "B1": "B1", "B1_prime": "B1'", "B2": "B2", "B3": "B3"}
TESTED = ("grid_crps", "upper_tail_twcrps")
METRIC_NAMES = m1402.METRIC_NAMES
METRIC_TITLES = m1402.METRIC_TITLES
SPLITS = ("pooled", "regime", "pressure_day_type")
MIN_GROUP_DAYS = m1402.MIN_GROUP_DAYS
LEADS = tuple(sp.HORIZONS)
GROUP_TYPES = dts.GROUP_TYPES
RATES = ("cover90", "miss_below_q05", "miss_above_q95", "miss_below_q01", "miss_above_q99")
SCORES = ("grid_crps", "upper_tail_twcrps")
MEASURES = RATES + SCORES
_I = {lv: sp.GRID.index(lv) for lv in (0.01, 0.05, 0.95, 0.99)}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the arm -------------------------------------------------------------------------------------------------------------


def multipliers_by_type(m: float) -> Dict[str, float]:
    """`m` for each type in the group, 1 for every other type (so a day outside the group is rescaled by exactly 1: the candidate's quantiles)."""

    return {t: (m if t in GROUP_TYPES else 1.0) for t in dts.TYPES}


def arm_forecasts(walk, panel, labels: Mapping[int, str], registry, decision_time, days: Sequence[date], k: float) -> Tuple[Dict[date, dict], dict]:
    """The candidate's raw (uncapped) forecasts of `days` with the pool rescaled on group target days, and the record of the multipliers.

    The multiplier of a refit and lead is computed once from that refit's estimate, the labels of its training targets and the anchor of the refit's
    decision (the last row public at it).

    Raises:
        LookAheadError: a training target of a refit is after the refit's anchor (`repo_model.day_type_scale.group_multiplier`).
    """

    position = {row.date: i for i, row in enumerate(panel)}
    estimates = {r: per_arm[ARM_NET] for r, per_arm in walk.estimates.items()}
    fitted: Dict[date, Dict[int, dict]] = {}
    for refit, per_lead in estimates.items():
        anchor = pb._anchor(panel, position[refit], registry, decision_time)
        fitted[refit] = {h: dts.group_multiplier(est, labels, anchor, k=k) for h, est in per_lead.items()}
    out: Dict[date, dict] = {}
    for d in days:
        refit = m1402.refit_for(estimates, d)
        index = position[d]
        types = {h: labels[index + h] for h in LEADS}
        by_lead = {h: multipliers_by_type(fitted[refit][h]["m"]) for h in LEADS}
        out[d] = dts.rescale_day(walk.forecasts[ARM_NET][d], estimates[refit], by_lead, types, walk.detail[d]["scale"])
    return out, multiplier_record(fitted, k)


def multiplier_record(fitted: Mapping[date, Mapping[int, Mapping[str, float]]], k: float) -> dict:
    """Per lead, over the refits: the mean, least and greatest of `m_raw`, `w` and `m`, the mean and least number of group pairs, and the share of refits
    at the fallback (fewer than the minimum of pairs) and at a bound."""

    out: dict = {"refits": len(fitted), "k": k, "minimum_rows": dts.MIN_ROWS, "bounds": list(dts.BOUNDS), "by_lead": {}}
    for h in LEADS:
        rows = [fitted[r][h] for r in fitted]
        block = {}
        for name in ("m_raw", "w", "m"):
            values = [x[name] for x in rows]
            block[name] = {"mean": sum(values) / len(values), "min": min(values), "max": max(values)}
        block["n"] = {"mean": sum(x["n"] for x in rows) / len(rows), "min": min(x["n"] for x in rows), "max": max(x["n"] for x in rows)}
        block["share_fallback"] = sum(1 for x in rows if x["n"] < dts.MIN_ROWS) / len(rows)
        block["share_at_bound"] = sum(1 for x in rows if x["m_raw"] in dts.BOUNDS) / len(rows)
        out["by_lead"][str(h)] = block
    return out


def outside_group_identical(
    candidate: Mapping[date, Mapping[int, Sequence[float]]], arm: Mapping[date, Mapping[int, Sequence[float]]], labels: Mapping[int, str],
    position: Mapping[date, int], days: Sequence[date],
) -> Dict[str, int]:
    """The directive's claim: on every cell whose target day is outside the group, every quantile of the arm equals the candidate's. Counts the cells.

    `labels[row]` is the pressure-day type of a panel row, `position[day]` the row of a decision day.

    Raises:
        ValueError: a cell whose target is outside the group differs in any quantile.
    """

    counts = {"group_cells": 0, "group_cells_changed": 0, "other_cells": 0}
    for d in days:
        for h in LEADS:
            label = labels[position[d] + h]
            same = list(arm[d][h]) == list(candidate[d][h])
            if label in GROUP_TYPES:
                counts["group_cells"] += 1
                counts["group_cells_changed"] += 0 if same else 1
                continue
            if not same:
                raise ValueError(f"{d} lead {h}: the target day is {label}, outside the group, and the arm's quantiles differ from the candidate's")
            counts["other_cells"] += 1
    return counts


# -- cells, rates and events ---------------------------------------------------------------------------------------------


def rate_vector(q: Sequence[float], y: float) -> List[float]:
    """`[inside the closed q05..q95 band, below q05, above q95, below q01, above q99]` as 0/1 for one cell."""

    return [
        1.0 if q[_I[0.05]] <= y <= q[_I[0.95]] else 0.0, 1.0 if y < q[_I[0.05]] else 0.0, 1.0 if y > q[_I[0.95]] else 0.0,
        1.0 if y < q[_I[0.01]] else 0.0, 1.0 if y > q[_I[0.99]] else 0.0,
    ]


def event_of(day: date) -> Optional[str]:
    """The turn event (`YYYY-MM` of the quarter-end) a target day belongs to, or `None` outside a quarter-end turn (#1533's definition)."""

    return m1533.quarter_end_event(day)


def cluster_interval(sums: Sequence[Sequence[float]], counts: Sequence[int], *, reps: int = EVENT_REPS, seed: int = SEED) -> List[Tuple[float, float]]:
    """90% percentile intervals of the pooled means of several columns, resampling whole events (`sums[e][column]`, `counts[e]` cells) with replacement."""

    return m1533.event_mean_intervals(sums, counts, reps=reps, seed=seed)


def group_cells(frame, labels: Mapping[int, str], table, candidate, arm) -> List[dict]:
    """Every cell of the group (and every cell on a #1363 `quarter_end` day): its event, lead, type and the measures of the candidate, the arm and their
    difference (arm minus candidate).

    Raises:
        ValueError: a cell of the group has no turn event.
    """

    out = []
    for d in frame.days:
        for h in LEADS:
            index = frame.position[d] + h
            label = labels[index]
            qe1363 = bool(table.day_types(index).get("quarter_end"))
            if label not in GROUP_TYPES and not qe1363:
                continue
            t = frame.target(d, h)
            y = frame.outcome[t]
            event = event_of(t)
            if label in GROUP_TYPES and event is None:
                raise ValueError(f"{t}: a {label} day with no turn event")
            row = {}
            for name, forecast in (("candidate", candidate), ("arm", arm)):
                q = forecast[d][h]
                row[name] = rate_vector(q, y) + [sp.grid_crps(q, y), sp.upper_tail_twcrps(q, y)]
            row["diff"] = [a - b for a, b in zip(row["arm"], row["candidate"])]
            out.append({"event": event or f"day-{t.isoformat()}", "h": h, "type": label, "qe1363": qe1363, "in_group": label in GROUP_TYPES,
                        "vec": row["candidate"] + row["arm"] + row["diff"]})
    return out


def summarise(cells: Sequence[dict], *, reps: int = EVENT_REPS, seed: int = SEED) -> Optional[dict]:
    """The means and event-cluster intervals of every measure for a set of cells, or `None` for an empty set."""

    if not cells:
        return None
    by_event: Dict[str, List[dict]] = {}
    for cell_ in cells:
        by_event.setdefault(cell_["event"], []).append(cell_)
    events = sorted(by_event)
    width = len(cells[0]["vec"])
    sums = [[sum(x["vec"][j] for x in by_event[e]) for j in range(width)] for e in events]
    counts = [len(by_event[e]) for e in events]
    total = sum(counts)
    means = [sum(s[j] for s in sums) / total for j in range(width)]
    intervals = cluster_interval(sums, counts, reps=reps, seed=seed)
    n = len(MEASURES)
    out: dict = {"cells": total, "events": len(events), "measures": {}}
    for i, name in enumerate(MEASURES):
        out["measures"][name] = {
            "candidate": means[i], "candidate_interval": list(intervals[i]),
            "arm": means[n + i], "arm_interval": list(intervals[n + i]),
            "diff": means[2 * n + i], "diff_interval": list(intervals[2 * n + i]),
        }
    return out


def group_report(cells: Sequence[dict], *, reps: int = EVENT_REPS) -> dict:
    """The group pooled and by lead, by type, and the #1363 `quarter_end` subset."""

    inside = [x for x in cells if x["in_group"]]
    out = {"pooled": summarise(inside, reps=reps), "by_lead": {}, "by_type": {}}
    for h in LEADS:
        out["by_lead"][str(h)] = summarise([x for x in inside if x["h"] == h], reps=reps)
    for t in GROUP_TYPES:
        out["by_type"][t] = summarise([x for x in inside if x["type"] == t], reps=reps)
    out["quarter_end_1363"] = summarise([x for x in cells if x["qe1363"]], reps=reps)
    out["events"] = sorted({x["event"] for x in inside})
    return out


def kill_reading(group: Mapping[str, object]) -> dict:
    """The declared kill: the group's 90% coverage does not improve beyond its interval (the lower end of the paired difference is not above zero), or
    the group's mean grid CRPS of the arm is above the candidate's."""

    pooled = group["pooled"]["measures"]
    coverage, crps = pooled["cover90"]["diff"], pooled["grid_crps"]["diff"]
    no_gain = pooled["cover90"]["diff_interval"][0] <= 0.0
    loses = crps > 0.0
    return {"coverage_gain": coverage, "coverage_gain_interval": pooled["cover90"]["diff_interval"], "coverage_improves_beyond_interval": not no_gain,
            "group_crps_diff": crps, "group_crps_diff_interval": pooled["grid_crps"]["diff_interval"], "group_crps_loses": loses, "killed": no_gain or loses}


# -- B3 -------------------------------------------------------------------------------------------------------------------


def b3_series(frame, forecasts: Mapping[str, Mapping[date, Mapping[int, Sequence[float]]]]) -> Tuple[List[date], Dict[str, Dict[date, float]]]:
    """B3's five-level CRPS averaged over h = 1..5 and each model's at the same five levels, on the decision days where the published record has all
    five leads (ruling of 13 October 2026, PR #660).

    Raises:
        ValueError: the published record's outcome for a target day is not the panel's.
    """

    daily = {}
    for h in LEADS:
        record = json.loads(Path(str(B3_DAILY).format(h=h)).read_text(encoding="utf-8"))
        daily[h] = {x["date"]: x for x in record["days"]}
    position = {d: i for i, d in enumerate(frame.dates)}
    kept = [d for d in frame.days
            if all(position[d] + h < len(frame.dates) and frame.dates[position[d] + h].isoformat() in daily[h] for h in LEADS)]
    five = sp.level_crps(B3_LEVELS)
    out: Dict[str, Dict[date, float]] = {"B3": {}, **{m: {} for m in forecasts}}
    for d in kept:
        totals = {m: 0.0 for m in out}
        for h in LEADS:
            target = frame.dates[position[d] + h]
            entry = daily[h][target.isoformat()]
            observed = frame.outcome[target]
            if abs(float(entry["actual_bps"]) - float(observed)) > 1e-9:
                raise ValueError(f"the published record's outcome for {target} is {entry['actual_bps']}, the panel's is {observed}")
            totals["B3"] += five([float(x) for x in entry["quantiles_bps"]], observed)
            for m in forecasts:
                totals[m] += five(sp.on_levels(forecasts[m][d][h], B3_LEVELS), observed)
        for m in out:
            out[m][d] = totals[m] / len(LEADS)
    return kept, out


# -- the paired tests ----------------------------------------------------------------------------------------------------

_STATE: Dict = {}


def plan(candidate: str) -> List[str]:
    """What a model is tested against: the references, and for the arm the candidate too (identical wherever the group is not in the set)."""

    return list(REFERENCES) + ([ANNNET] if candidate == ARM else [])


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


def b3_tests(frame, forecasts, draws: int) -> dict:
    """The arm and the candidate against B3 on B3's five levels, pooled and by regime of the decision day, on the studentized stationary bootstrap."""

    kept, series = b3_series(frame, {m: forecasts[m] for m in (ANNNET, ARM)})
    groups = {"all decision days": list(kept)}
    for d in kept:
        groups.setdefault(frame.regime(d), []).append(d)
    out: dict = {"days": len(kept), "groups": {}}
    for label, members in groups.items():
        if not members:
            continue
        entry: dict = {"days": len(members), "means": {m: sum(series[m][d] for d in members) / len(members) for m in series}, "vs": {}}
        if len(members) < MIN_GROUP_DAYS:
            entry["skipped"] = True
        else:
            for candidate in (ANNNET, ARM):
                entry["vs"][candidate] = s761.run_pairs({"B3": series["B3"]}, series[candidate], members, seed=SEED, draws=draws, mean_d_fallback=True)["B3"]
        out["groups"][label] = entry
    return out


# -- the run -------------------------------------------------------------------------------------------------------------


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date], k: float):
    """#1255's frame of `window` with the candidate and the arm added: `(frame, notes, labels, record, counts, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walk = m1402.walks_of(window, frame, panel, splits, registry, results, auctions, first)
    labels = m1402.type_of_rows(panel, splits)
    raw_arm, record = arm_forecasts(walk, panel, labels, registry, k_mod.DECISION_TIME, frame.days, k)
    raw = {ANNNET: {d: walk.forecasts[ARM_NET][d] for d in frame.days}, ARM: raw_arm}
    forecasts = {name: m1255.s3c_forecasts(frame, register, found) for name, found in raw.items()}
    keep = {name: frame.forecasts[name] for name in REFERENCES}
    frame.forecasts = {**{name: {d: keep[name][d] for d in frame.days} for name in REFERENCES}, **{name: {d: forecasts[name][d] for d in frame.days} for name in raw}}
    counts = outside_group_identical(frame.forecasts[ANNNET], frame.forecasts[ARM], labels, frame.position, frame.days)
    return frame, dict(notes, refits=len(walk.fits)), labels, record, counts, groups_fn


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args, k: float) -> dict:
    frame, notes, labels, record, counts, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first, k)
    last = WINDOW_LAST[window]
    day_labels = c.day_labels(frame, table)
    pressure = k_mod.pressure_labels(frame, sorted(day_labels))
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in (ANNNET, ARM):
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, day_labels, pressure) if g[0] in SPLITS]
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
            for candidate in (ARM, ANNNET):
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped, "multipliers": record, "outside_the_group": counts,
        "pressure_day_type_counts": {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))},
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["group"] = group_report(group_cells(frame, labels, table, frame.forecasts[ANNNET], frame.forecasts[ARM]), reps=args.event_reps)
    result["group"]["kill"] = kill_reading(result["group"])
    result["b3"] = b3_tests(frame, frame.forecasts, args.draws)
    return result


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant."""

    with m1321.decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    k = declaration["form"]["k"]
    if k != K:
        raise SystemExit(f"the declaration's k is {k!r}, the script's is {K!r}")
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/qe_shrunk_scale_1531")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1531, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": sha, "decision_time": c.DECISION_TIME.strftime("%H:%M"),
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict", "seed": SEED, "draws": args.draws,
        "reps": args.reps, "event_reps": args.event_reps, "k": k, "models": list(MODELS), "windows": {},
        "reading_rules": declaration["reading_rules"], "kill_rule": declaration["kill"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args, k)
    result["reproduction"] = m1402.reproduction(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def _f(x: float, d: int = 3) -> str:
    return f"{x:.{d}f}"


def _iv(interval: Sequence[float], d: int = 3) -> str:
    return f"[{interval[0]:.{d}f}, {interval[1]:.{d}f}]"


def _signed(x: float, d: int = 3) -> str:
    return f"{x:+.{d}f}"


def _siv(interval: Sequence[float], d: int = 3) -> str:
    return f"[{interval[0]:+.{d}f}, {interval[1]:+.{d}f}]"


def rates_table(rows: Sequence[Tuple[str, Optional[dict]]]) -> List[str]:
    """Coverage and tail misses, candidate / arm, with the paired difference and its event-cluster interval for the coverage."""

    out = ["| set | cells | events | 90% coverage: candidate | arm | arm minus candidate | below q05 (5%): cand. / arm | above q95 (5%): cand. / arm "
           "| below q01 (1%): cand. / arm | above q99 (1%): cand. / arm |", "|---|---|---|---|---|---|---|---|---|---|"]
    for label, s in rows:
        if s is None:
            continue
        m = s["measures"]
        pair = lambda name: f"{_f(m[name]['candidate'])} / {_f(m[name]['arm'])}"  # noqa: E731
        out.append(f"| {label} | {s['cells']} | {s['events']} | {_f(m['cover90']['candidate'])} {_iv(m['cover90']['candidate_interval'])} | "
                   f"{_f(m['cover90']['arm'])} {_iv(m['cover90']['arm_interval'])} | {_signed(m['cover90']['diff'])} {_siv(m['cover90']['diff_interval'])} | "
                   f"{pair('miss_below_q05')} | {pair('miss_above_q95')} | {pair('miss_below_q01')} | {pair('miss_above_q99')} |")
    return out


def scores_table(rows: Sequence[Tuple[str, Optional[dict]]]) -> List[str]:
    out = ["| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm "
           "| arm minus candidate |", "|---|---|---|---|---|---|---|"]
    for label, s in rows:
        if s is None:
            continue
        g, t = s["measures"]["grid_crps"], s["measures"]["upper_tail_twcrps"]
        out.append(f"| {label} | {_f(g['candidate'])} | {_f(g['arm'])} | {_signed(g['diff'])} {_siv(g['diff_interval'])} | "
                   f"{_f(t['candidate'])} | {_f(t['arm'])} | {_signed(t['diff'])} {_siv(t['diff_interval'])} |")
    return out


def group_rows(group: Mapping[str, object]) -> List[Tuple[str, Optional[dict]]]:
    rows = [("group, pooled over h = 1-5", group["pooled"])] + [(f"group, h = {h}", group["by_lead"][str(h)]) for h in LEADS]
    return rows + [(f"group, {t} only", group["by_type"][t]) for t in GROUP_TYPES] + [("`quarter_end` days of the calibration study (the group behind its 49.3% figure)", group["quarter_end_1363"])]


def short_of_nominal(group: Mapping[str, object]) -> str:
    m = group["pooled"]["measures"]["cover90"]
    return (f"The arm's 90% band covers {_f(m['arm'])} {_iv(m['arm_interval'])} of the group's cells against {_f(m['candidate'])} for the candidate; "
            f"the gap to 90% is {100 * (0.9 - m['arm']):.1f} percentage points" + ("." if m["arm"] < 0.9 else " (negative: the band covers more than 90%)."))


def kill_sentence(kill: Mapping[str, object]) -> str:
    gain = (f"Coverage on the group: {_signed(kill['coverage_gain'])} {_siv(kill['coverage_gain_interval'])} (arm minus candidate, event-cluster 90% interval). "
            + ("The lower end of the interval is above zero, so the arm improves beyond its interval."
               if kill["coverage_improves_beyond_interval"] else "The lower end of the interval is not above zero, so the arm does not improve beyond its interval."))
    crps = (f"Grid CRPS on the group: {_signed(kill['group_crps_diff'])} {_siv(kill['group_crps_diff_interval'])} bp (arm minus candidate). "
            + ("The arm's is above the candidate's, so the arm loses." if kill["group_crps_loses"] else "The arm's is not above the candidate's, so the arm does not lose."))
    return f"{gain} {crps} **Against the declared kill: {'killed' if kill['killed'] else 'not killed'}.**"


def multiplier_table(record: Mapping[str, object]) -> List[str]:
    out = ["| lead | group pairs n: mean (least to greatest) | m_raw: mean (least to greatest) | w: mean | m: mean (least to greatest) | share of refits at the fallback | share at a bound |",
           "|---|---|---|---|---|---|---|"]
    for h in map(str, LEADS):
        e = record["by_lead"][h]
        out.append(f"| h={h} | {e['n']['mean']:.1f} ({e['n']['min']} to {e['n']['max']}) | {e['m_raw']['mean']:.3f} ({e['m_raw']['min']:.3f} to {e['m_raw']['max']:.3f}) "
                   f"| {e['w']['mean']:.3f} | {e['m']['mean']:.3f} ({e['m']['min']:.3f} to {e['m']['max']:.3f}) | {e['share_fallback']:.2f} | {e['share_at_bound']:.2f} |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for candidate in (ANNNET, ARM):
        for ref in REFERENCES:
            out.append(f"| {LABELS[candidate]} against {LABELS[ref]} | " + " | ".join(m1402.cell(m1402._vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, candidate: str, reference: str) -> List[str]:
    return m1402.split_table(window, split, candidate, reference)


def b3_table(b3: Mapping[str, object]) -> List[str]:
    out = ["| decision days | days | B3 | (s3c-ann-net) | (s3c-ann-net-qe) | (s3c-ann-net) against B3 | (s3c-ann-net-qe) against B3 |", "|---|---|---|---|---|---|---|"]
    if not b3["groups"]:
        return ["The published record holds no decision day of this window with all five leads, so B3 is not scored here.", ""]
    for label, g in b3["groups"].items():
        if g.get("skipped"):
            out.append(f"| {label} | {g['days']} | not tested (fewer than {MIN_GROUP_DAYS} days) | | | | |")
            continue
        out.append(f"| {label} | {g['days']} | {g['means']['B3']:.3f} | {g['means'][ANNNET]:.3f} | {g['means'][ARM]:.3f} | "
                   + " | ".join(m1402.cell(g["vs"][m]) for m in (ANNNET, ARM)) + " |")
    return out


GLOSSARY = "glossary.md"
RESULT_TITLES = {"development": "Result on the development window (targets up to 2025-12-31)",
                 "2026": "The 2026 development days (targets 2026-01-02 to 2026-09-03)"}
CELL_GUIDE = ("Each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and "
              "ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero. A note in brackets "
              "says where the interval of the skill reads differently.")


def window_section(window: str, w: Mapping[str, object]) -> List[str]:
    g, n = w["group"], w["notes"]
    development = window == "development"
    out = [f"## {RESULT_TITLES[window]}", ""]
    if not development:
        out += ["These days are kept apart from the development window. The kill rule is not read on them and they decide nothing.", ""]
    out += [f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits']} refits. "
            f"Group cells: {w['outside_the_group']['group_cells']:,}, of which the arm changes {w['outside_the_group']['group_cells_changed']:,}; "
            f"cells outside the group: {w['outside_the_group']['other_cells']:,}, every one identical to the candidate (the walk fails otherwise). "
            f"The group holds {g['pooled']['events']} turn events and {g['pooled']['cells']} cells; **roughly 30 to 44 events is small.**", "",
            "### Coverage and tail misses on the group, candidate against arm", "",
            "Read the first row, and in it the column \"arm minus candidate\": that difference and its interval are what the kill rule reads. A 90% band "
            "that works covers 90% of the cells, so the two coverage columns show how far each model is from that. The four tail columns give the share of "
            "cells whose outcome fell outside a quantile, candidate first and arm second, with the share a calibrated model would show in brackets in the "
            "column head. The rows by lead and by day type hold fewer cells, and their intervals are wider.", ""] + rates_table(group_rows(g)) + [
            "", f"**{short_of_nominal(g)}**", "",
            "### Accuracy of the distribution on the group (paired, same cells)", "",
            "Both scores are in bp and lower is better, so a negative difference favors the arm. The first row holds the grid CRPS difference the kill rule "
            "reads.", ""] + scores_table(group_rows(g)) + [
            "", "### The declared kill" + ("" if development else " (shown apart; the kill is read on the development window only, and these days decide nothing)"), "",
            kill_sentence(g["kill"]), "",
            "### The multipliers (shrunk), over the window's refits", "",
            "The table shows how large the adjustment was at each lead. `m_raw` is the ratio before shrinkage, `w` the weight it receives and `m` the "
            "multiplier applied; an `m` above 1 widens the band. The fallback is the `m_raw` of 1 used below 10 pairs, and a bound is 0.5 or 4.", ""
            ] + multiplier_table(w["multipliers"]) + [""]
    pooled = w["groups"]["pooled"]["all decision days"]
    out += ["### Pooled, against B1, B1' and B2 (studentized stationary bootstrap)", "",
            "This table places both models in the scoring protocol's frame, on all decision days. " + CELL_GUIDE + " Everything outside the group is "
            "identical, so the arm and the candidate differ against a benchmark only through the group, and their rows are close: the comparison that "
            "separates them is the group's, above.", ""]
    out += against_table(pooled) + [""]
    splits = []
    for split, title in (("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
        for ref in REFERENCES:
            for cand in (ANNNET, ARM):
                t = split_table(w, split, cand, ref)
                if t:
                    splits += [f"#### {title}: {LABELS[cand]} against {LABELS[ref]}", ""] + t + [""]
    if splits:
        out += ["### The same comparison, split", "",
                "A pooled development figure is not a result on its own, so the comparison is repeated by regime and by pressure-day type of the target day. "
                "These are reference tables. For each benchmark the candidate's table comes first and the arm's second; the two differ only through the "
                "group's cells, so look at the rows that hold quarter-end and year-end days. The cells read as in the pooled table.", ""] + splits
    t = split_table(w, "pressure_day_type", ARM, ANNNET)
    if t:
        out += ["### By pressure-day type: the arm against the candidate (identical outside the group)", "",
                "Here the candidate takes the benchmark's place, so a positive d favors the arm. A row reads \"identical\" where the arm changes nothing.", ""] + t + [""]
    out += ["### Against B3 (the published record's five levels, grid CRPS on those five)", "",
            "B3 is the published model. It forecasts five quantile levels, so grid CRPS (bp) is computed on those five for all three models. The comparison "
            "is reported and carries no decision rule.", ""] + b3_table(w["b3"]) + [""]
    if w["skipped_groups"]:
        out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    return out


def question() -> List[str]:
    return [
        "## Question for Eleonora (marked; the default changes no claim)", "",
        "**Question 1. What is the shrinkage constant k?** The rule is `w = n / (n + k)`, `n` the group's training pairs at a refit and lead (a turn gives two "
        "pairs per lead). It is written in the declaration before any score and was not tuned on scores: this page uses k = 20, ten turns' worth of pairs, "
        "where the raw ratio is trusted by half. It is a judgment call, so it is yours.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **k = 20** (default). Half weight at ten turns, three fifths at thirty. This page.",
        "2. **k = 10.** Less shrinkage: half weight at five turns. A fresh run with a fresh declaration.",
        "3. **k = 40.** More shrinkage: half weight at twenty turns, about two fifths at thirty. A fresh run with a fresh declaration.", "",
        "**Question 2. Does the arm go on?** The Mechanism section of the quarter-end diagnosis reads the failure as a shape problem with a location shift, "
        "and says no single multiplier fits every level. The design was run as ruled and not revised. Whether a width-only arm closes anything, or the work "
        "moves to B or to an event-conditional distribution model, is yours; adopting the arm is not in scope and the 2 November freeze holds.", "",
        "**Options:** 1. **Read this page, then decide B or the event-conditional model** (default; no claim changes). 2. **Re-run with k = 10 or 40** "
        "(option 2 or 3 above). 3. **Stop the family here.**", ""]


def answer(dev: Mapping[str, object]) -> str:
    """The answer in two sentences: where the band stands against 90%, and how the arm reads against the declared kill."""

    m, kill = dev["pooled"]["measures"]["cover90"], dev["kill"]
    first = ("Not on the development data: the" if m["arm"] < 0.9 else "On the development data the") + short_of_nominal(dev)[len("The"):]
    gained = "improved on the candidate's coverage beyond its interval" if kill["coverage_improves_beyond_interval"] else "did not improve on the candidate's coverage beyond its interval"
    lost = "scored worse on grid CRPS" if kill["group_crps_loses"] else "did not score worse on grid CRPS"
    second = f"The arm {gained} and {lost}, so under the rule declared before the run it is {'killed' if kill['killed'] else 'not killed'}."
    return f"{first} {second}"


def record(r: dict) -> List[str]:
    """The footer: the issue numbers, the files and the digests a reader needs to trace the page, kept out of the prose above."""

    out = ["## Record", "",
           "- Study: #1531. Hypothesis and step: H5 (primary goal), step 3, arm A of her ruling of 9 November 2026.",
           "- Status: **development data, not a verdict** (scoring protocol v1, #640). (s3c-ann-net) stays frozen; nothing is adopted, registered or "
           "published and no claim changes.",
           f"- Generated by `scripts/qe_shrunk_scale_1531.py page` from `docs/research/qe-shrunk-scale-1531/result.json`, not edited by hand; declared in "
           f"`{r['declaration']}` before any score.",
           f"- Panel digest `{r['panel_sha256']}`."]
    if r.get("reproduction"):
        out += ["- Reproduction: the candidate's pooled mean grid CRPS equals #1314's 18:00 record to 1e-9 (development "
                f"{r['reproduction']['development']['here']:.6f}, 2026 {r['reproduction']['2026']['here']:.6f}), or the script refused to write this record."]
    out += ["- Where the parts come from: the target-day labels, #959; the raw multiplier, #1402; the quarter-end diagnosis, #1533; the `quarter_end` "
            "group and its 49.3% figure, #1363; the development window, #1145 and #1241; the 2026 development days, #1229 and #1252.",
            "- Open or inherited rulings: the day-type interval method, where #1228 has not ruled; the reading from the mean-d bound, her ruling on #1009; "
            "the understated HAC standard error, #958.", ""]
    return out


def render(r: dict) -> str:
    dev = r["windows"]["development"]["group"]
    out = [
        "# A shrunk quarter-end scale beside the frozen candidate", "",
        f"Terms such as arm, cell, kill rule, grid CRPS and B1 are defined in the [glossary]({GLOSSARY}). Issue numbers and files are in the Record at the "
        "end.", "",
        "## The question", "",
        "**Does a shrunk residual multiplier on quarter-end target days alone repair the candidate's quarter-end bands?** The candidate's 90% band "
        "covers too few outcomes around quarter-ends. This study tests one repair: rescale the band on those days only, and leave every other forecast as it is.", "",
        "## The answer", "",
        answer(dev), "",
        "## Data", "",
        "The published panel, with every forecast made at the 18:00 decision. Two sets of days are scored and kept apart: the development window, where the "
        "kill rule is read, and the 2026 development days, which are shown separately and decide nothing. Each section below opens with its count of days, "
        "cells and turn events.", "",
        "## Method", "",
        "**The change.** The group is every target day whose type is `quarter_end_turn` or `year_end`: the last business day of each calendar quarter and "
        "the first after it. On those days the candidate's residual pool is rescaled about its median by `m = 1 + w (m_raw - 1)`, `w = n / (n + k)`, `k = "
        + str(r["k"]) + "`. `m_raw` is the root-mean-square ratio of the group's training residuals to all of them (per refit and lead, 1 below 10 pairs, "
        "clamped to [0.5, 4]), and `n` is the number of the group's training pairs, so a group with few pairs is pulled toward a multiplier of 1. On every "
        "other target day every quantile equals the candidate's, bit for bit, and the walk fails if it does not. The center, the calendar terms, the scale "
        "and the fit are the candidate's, on direct pairs; the SRF cap is applied after.", "",
        "**The kill rule.** Declared before any score: the arm is killed if its 90% coverage on the group does not improve on the candidate's beyond its "
        "interval (the lower end of the 90% event-cluster interval of the paired difference, arm minus candidate, is not above zero), or if the arm's mean "
        "grid CRPS on the group is above the candidate's. Pooled figures cannot pass or fail it alone, since everything outside the group is identical.", "",
        f"**The intervals.** The h = 1-5 forecasts aimed at one turn, and the turn's two days, are one cluster. Intervals on the group are 90% "
        f"percentile intervals of a cluster bootstrap over turn events ({r['event_reps']:,} resamples, seed {r['seed']}). The development window holds "
        f"{dev['pooled']['events']} events: roughly 30 to 44 is small, so every interval is wide. Against the benchmarks the interval is the studentized "
        f"stationary bootstrap (mean block {sp.BLOCK_LENGTH} business days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval), and the "
        "reading is taken from the bound on mean d. Two caveats carry over: which interval method applies to day types has not been ruled on, and the HAC "
        "standard error is understated about 2x after 2020. In the paired tables against a benchmark, a positive mean d favors the model named first.", "",
        "**Design not revised.** The Mechanism section of the quarter-end diagnosis was read before this run. It gives a reason to doubt a single "
        "multiplier (the failure is one of shape as well as width) but none to change the declared group or shrinkage rule, so the arm was run as ruled; "
        "the doubt is Question 2 below.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is not None:
            out += window_section(window, w)
    out += ["## What it means, and its limits", "",
            "The page shows what one width multiplier on the quarter-end group does to the candidate's coverage, tail misses and CRPS on development days. "
            "It does not show a verdict, an adoption, or what a distribution with its own shape on those days would do. \"Not killed\" means the arm did not "
            "fail the declared rule; the candidate stays frozen and nothing is adopted, registered or published. The 2026 days are shown apart and decide "
            "nothing.", ""]
    out += question()
    out += record(r)
    return "\n".join(out).rstrip() + "\n"


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the candidate, make the arm and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=m1402.REPS, help="bootstrap resamples of the unstudentized intervals")
    s.add_argument("--event-reps", type=int, default=EVENT_REPS, help="event-cluster resamples on the group")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None, help="start the walk on this day (a subset, for the script's test only)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
