"""(s3c-mbs): (s3c) with indicators for the settlement days of the agency MBS classes A to D, scored against (s3c), (s3), B1, B1' and B2 (#1276; H5 step 3,
an arm on the candidate, with a new source; ledger item 68 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_mbs_1276.json`, which this script refuses to read unless it is committed and unchanged, and the source's availability is declared in
`metadata/sifma_mbs_1276.json` (the per-year `public_from`, taken from the Internet Archive's captures of SIFMA's page). The arm is `repo_model.s3c_mbs`:
(s3)'s fit with one 0/1 indicator per class added, on a target day that is a settlement day of that class and whose year's calendar was public at the
decision instant (else 0); if a class has fewer than 20 settlement days in the development window the four classes pool into one indicator, and the
script says which it did. The SRF cap at full allotment is (s3c)'s, applied to the arm's quantiles after the walk (`repo_model.s3c_candidate`). The frames
and the machinery are #1255's and #1265's and are loaded as they are: the development window (targets up to 2025-12-31) and the 2026 development days
(targets 2026-01-02 to 2026-09-03, the near-blind tier open since GO #151); the blind tier and every lockbox day are refused by the frames' own guards.
The arm is walked on the same decision days with the same refit schedule as (s3), and (s3) re-forecast inside that walk must equal the frame's (s3) cell
for cell, or the run stops.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp), on scoring protocol v1's
studentized stationary bootstrap read on the bound on mean d (her #1009 ruling) with the skill interval beside, split by regime, by pressure-day type, by
lead, and by the target days on which the indicators are non-zero against the others (and each class's days); the 90% band coverage beside (s3c)'s; and
the fitted effect of each indicator in bp, by regime.

Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    python3 scripts/build_sifma_table_1276.py --check
    PYTHONPATH=src python3 scripts/s3c_mbs_1276.py score --panel PUB.csv --output docs/research/s3c-mbs-1276/result.json
    PYTHONPATH=src python3 scripts/s3c_mbs_1276.py page \\
        --score docs/research/s3c-mbs-1276/result.json --output docs/research/s3c-mbs-1276-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import statistics
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


from repo_model import announced_iorb, metrics, policy_events, s3c_candidate, s3c_mbs, sifma_mbs  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal, turn_days  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1265's script (its cell table with the Brier cell, its table cell) and, through it, #1255's, #1241's and #1229's, loaded under an alias of
#: their own so that the pickling of the worker pool's tasks does not meet another test module's copy.
m1265 = _load("s3c_turn_cap_1265", "s3c_turn_cap_1265_in_1276")
m1255 = m1265.m1255
k, d1222 = m1255.k, m1255.d1222
c, s686, s761, load_daily_panel = k.c, k.s686, k.s761, m1255.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_mbs_1276.json"
AVAILABILITY = REPO / "metadata" / "sifma_mbs_1276.json"
RECORD_1255 = REPO / "docs" / "research" / "s3c-candidate-1255" / "result.json"
SEED = 1276
LAST_DAY = EXPLORATORY_END
#: The window the pooling rule counts in: the development window of #1145 (targets up to 2025-12-31).
POOLING_WINDOW_LAST = s686.LAST_DAY
S3, S3C, S3CM, B1P = k.S3, m1255.S3C, "sc_s3c_mbs", k.B1P
BENCHMARKS = ("B1", B1P, "B2")
ARMS = (S3, S3C, S3CM)
MODELS = BENCHMARKS + ARMS
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3: "(s3)", S3C: "(s3c)", S3CM: "(s3c-mbs)"}
#: The measures that are tested, and the one that is reported as a mean only (the closed 90% band, q05 to q95).
TEST_METRICS = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
METRIC_NAMES = TEST_METRICS + ("coverage_90",)
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)", "coverage_90": "90% band coverage"}
LO, HI = sp.GRID.index(0.05), sp.GRID.index(0.95)
WINDOWS = ("development", "2026")
WINDOW_TITLES = m1255.WINDOW_TITLES
MIN_GROUP_DAYS = k.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
CHANGED = "settlement_day"
ANY_DAYS, OTHER_DAYS = "target days on which an indicator is non-zero", "other target days"


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def committed_availability() -> dict:
    """The source's availability declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(AVAILABILITY)


def plan(candidate: str) -> List[str]:
    """What (s3c-mbs) is tested against: (s3c), (s3), then the benchmarks. No other model is a candidate here."""

    return [S3C, S3] + list(BENCHMARKS) if candidate == S3CM else []


# -- the arm's forecasts -------------------------------------------------------------------------------------------------


def candidate_days(panel, last: date, first: Optional[date]) -> List[date]:
    """The decision days the frames of #1255 walk: every panel day whose fifth target is on or before `last` (from `first`, in a test)."""

    dates = [row.date for row in panel]
    return [d for i, d in enumerate(dates) if i + max(sp.HORIZONS) < len(panel) and dates[i + max(sp.HORIZONS)] <= last and (first is None or d >= first)]


def s3cm_forecasts(frame, register, walk: s3c_mbs.MbsWalk):
    """The arm's forecasts on the frame's days, each cell clipped by (s3c)'s cap (`m1255.s3c_forecasts`): the arm walk's quantiles, capped.

    Raises:
        ValueError: (s3) re-forecast in the arm's walk differs from the frame's (s3) on a cell, or a frame day is not in the walk.
    """

    s3 = frame.forecasts[S3]
    for d in frame.days:
        if d not in walk.forecasts:
            raise ValueError(f"the decision day {d} is in the frame and not in the MBS walk")
        if walk.s3[d] != s3[d]:
            raise ValueError(f"(s3) of the MBS walk differs from the frame's (s3) on the decision day {d}")
    return m1255.s3c_forecasts(frame, register, {d: walk.forecasts[d] for d in frame.days})



def cell_table(frame, forecasts) -> Dict[str, Dict[Tuple[date, int], float]]:
    """#1265's cells (the two scores and the Brier scores, after the days are checked) with the closed 90% band's hit."""

    out = m1265.cell_table(frame, forecasts)
    out["coverage_90"] = {}
    for d in sorted(forecasts):
        for h in sp.HORIZONS:
            q, y = forecasts[d][h], frame.outcome[frame.target(d, h)]
            out["coverage_90"][(d, h)] = 1.0 if q[LO] <= y <= q[HI] else 0.0
    return {m: out[m] for m in METRIC_NAMES}


# -- what the terms did --------------------------------------------------------------------------------------------------


def nonzero(values: Mapping[str, int]) -> bool:
    return any(v > 0 for v in values.values())


def term_use(frame, walk: s3c_mbs.MbsWalk, s3c, s3cm) -> dict:
    """Where an indicator is non-zero and where the arm's forecast differs from (s3c)'s, by lead; the refits in which each indicator is active."""

    out: Dict[str, dict] = {str(h): {"cells": 0, "term_nonzero": 0, "differs_from_s3c": 0} for h in sp.HORIZONS}
    for d in frame.days:
        for h in sp.HORIZONS:
            row = out[str(h)]
            row["cells"] += 1
            if nonzero(walk.values[d][h]):
                row["term_nonzero"] += 1
            if list(s3c[d][h]) != list(s3cm[d][h]):
                row["differs_from_s3c"] += 1
    used = sorted({walk.fit_used[d] for d in frame.days})
    out["refits_in_use"] = len(used)
    terms = sorted({t for r in used for h in sp.HORIZONS for t in walk.estimates[r][h].coefficient})
    out["refits_active"] = {str(h): {t: sum(1 for r in used if t in walk.estimates[r][h].active) for t in terms} for h in sp.HORIZONS}
    return out


def fitted_effect(frame, walk: s3c_mbs.MbsWalk) -> dict:
    """The fitted effect of each indicator in bp, by regime of the target day, on the cells where it is 1 (coefficient of the refit in force times the
    scale at the decision's anchor), and the coefficient of each refit in use summarised by the regime of the refit day (lead 1)."""

    cells: Dict[str, Dict[str, List[float]]] = {}
    for d in frame.days:
        for h in sp.HORIZONS:
            est = walk.estimates[walk.fit_used[d]][h]
            for term, flag in walk.values[d][h].items():
                if flag:
                    effect = est.coefficient[term] * walk.scale[d]
                    for key in ("all", frame.regime(frame.target(d, h))):
                        cells.setdefault(term, {}).setdefault(key, []).append(effect)
    effect = {term: {key: {"cells": len(v), "mean_bp": statistics.fmean(v), "min_bp": min(v), "max_bp": max(v)} for key, v in sorted(by.items())}
              for term, by in sorted(cells.items())}
    coefficients: Dict[str, Dict[str, List[float]]] = {}
    for r in sorted({walk.fit_used[d] for d in frame.days}):
        est = walk.estimates[r][1]
        for term, value in est.coefficient.items():
            for key in ("all", frame.regime(r)):
                coefficients.setdefault(term, {}).setdefault(key, []).append(value)
    coefficient = {term: {key: {"refits": len(v), "active": sum(1 for x in v if x != 0.0), "median": statistics.median(v), "min": min(v), "max": max(v)}
                          for key, v in sorted(by.items())} for term, by in sorted(coefficients.items())}
    return {"effect_bp_by_regime": effect, "coefficient_by_refit_regime": coefficient}


# -- one window ----------------------------------------------------------------------------------------------------------


def build(window: str, panel, splits, registry, table, register, first: Optional[date], walk: s3c_mbs.MbsWalk):
    """The frame of a window with the models of `MODELS`: returns `(frame, notes, groups_fn, s3c, s3cm)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    s3cm = s3cm_forecasts(frame, register, walk)
    s3c = frame.forecasts[S3C]
    keep = {name: frame.forecasts[name] for name in BENCHMARKS + (S3, S3C)}
    frame.forecasts = {**keep, S3CM: {d: s3cm[d] for d in frame.days}}
    return frame, notes, groups_fn, s3c, frame.forecasts[S3CM]


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


def settlement_groups(frame, walk: s3c_mbs.MbsWalk) -> List[Tuple[str, str, str, List[date]]]:
    """The target days on which an indicator is non-zero (read by the best-informed decision of the window that targets the day) against the others,
    and, for each term, the target days on which that term is non-zero."""

    flagged: Dict[date, set] = {}
    targets = set()
    for d in frame.days:
        for h in sp.HORIZONS:
            t = frame.target(d, h)
            targets.add(t)
            for term, v in walk.values[d][h].items():
                if v:
                    flagged.setdefault(t, set()).add(term)
    terms = sorted({term for names in flagged.values() for term in names})
    out = [(CHANGED, ANY_DAYS, "target", sorted(t for t in targets if t in flagged)),
           (CHANGED, OTHER_DAYS, "target", sorted(t for t in targets if t not in flagged))]
    for term in terms:
        out.append((CHANGED, f"{term}: settlement days", "target", sorted(t for t, names in flagged.items() if term in names)))
    return out


def run_window(window: str, panel, splits, registry, table, register, args, walk: s3c_mbs.MbsWalk) -> dict:
    frame, notes, groups_fn, s3c, s3cm = build(window, panel, splits, registry, table, register, args.first, walk)
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = groups_fn(frame, labels, pressure) + settlement_groups(frame, walk)
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
        for metric in TEST_METRICS:
            jobs.append((split, label, grain, metric, S3CM, tuple(members)))
    done = run_jobs(jobs, args.workers)
    result: dict = {"notes": notes, "refits": len(walk.estimates), "groups": {}, "skipped_groups": skipped,
                    "term_use": term_use(frame, walk, s3c, s3cm), "fitted_effect": fitted_effect(frame, walk)}
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS} if members else {}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def against_records(results: Mapping[str, dict]) -> dict:
    """(s3) and (s3c) pooled mean scores here against #1255's record, window by window: the frames and the walk are the same."""

    if not RECORD_1255.exists():
        return {}
    there_all = json.loads(RECORD_1255.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        there = there_all[window]["groups"]["pooled"]["all decision days"]
        here = result["groups"]["pooled"]["all decision days"]
        out[window] = {"record": str(RECORD_1255.relative_to(REPO)), "metrics": {
            m: {model: {"here": here[m]["means"][model], "there": there[m]["means"][model], "difference": here[m]["means"][model] - there[m]["means"][model]}
                for model in (S3, S3C) + BENCHMARKS} for m in ("grid_crps", "upper_tail_twcrps")}}
    return out


def source_summary(table, public_from, counts: Mapping[str, int], pooled: bool) -> dict:
    """What the source gives the arm: the years the archive shows, each year's settlement dates by class, the window counts and the pooling outcome."""

    years = {}
    for year in sorted({d.year for days in table.values() for d in days}):
        stamp = public_from.get(year)
        years[str(year)] = {"public_from_utc": None if stamp is None else stamp.isoformat(),
                            "dates_by_class": {kl: sum(1 for d in table[kl] if d.year == year) for kl in sifma_mbs.CLASSES}}
    return {"window_last": POOLING_WINDOW_LAST.isoformat(), "settlement_days_in_window": dict(counts), "min_class_days": s3c_mbs.MIN_CLASS_DAYS,
            "pooled": pooled, "terms": list(s3c_mbs.MbsTable([], table, public_from, pooled=pooled).terms), "years": years}


def score(args) -> int:
    declaration = committed_declaration()
    availability = committed_availability()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_mbs_1276")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    sifma = sifma_mbs.load_table()
    public_from = sifma_mbs.parse_public_from(availability["public_from"])
    counts = s3c_mbs.class_counts(panel, sifma, public_from, last=POOLING_WINDOW_LAST, decision_time=k.DECISION_TIME)
    pooled = s3c_mbs.must_pool(counts)
    mbs = s3c_mbs.MbsTable(panel, sifma, public_from, pooled=pooled, decision_time=k.DECISION_TIME)
    s686.require_scored_days(candidate_days(panel, LAST_DAY, args.first), LAST_DAY)
    walk = s3c_mbs.walk(panel, candidate_days(panel, LAST_DAY, args.first), table, mbs, registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    result: dict = {
        "issue": 1276, "declaration": str(DECLARATION.relative_to(REPO)), "availability": str(AVAILABILITY.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": S3CM, "margin_bp": s3c_candidate.MARGIN_BP,
        "source": source_summary(sifma, public_from, counts, pooled), "reading_rules": declaration["reading_rules"],
        "walk": {"decision_days": len(walk.forecasts), "skipped": len(walk.skipped), "refits": len(walk.estimates)}, "windows": {},
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, args, walk)
    result["against_records"] = against_records(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


cell = m1265.cell


def _vs(group: Optional[Mapping[str, object]], metric: str, reference: str) -> Optional[dict]:
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(S3CM, {}).get(reference)


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text} (s3c-mbs) against (s3c) on grid CRPS: {cell(_vs(entry, 'grid_crps', S3C))}")
    return "; ".join(parts) + "."


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(f"{group[x]['means'][m]:.4f}" if x in ("brier_gt5", "coverage_90") else f"{group[x]['means'][m]:.3f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = ["| (s3c-mbs) against | " + " | ".join(METRIC_TITLES[m] for m in TEST_METRICS) + " |", "|---|" + "---|" * len(TEST_METRICS)]
    for ref in plan(S3CM):
        out.append(f"| {LABELS[ref]} | " + " | ".join(cell(_vs(group, m, ref)) for m in TEST_METRICS) + " |")
    return out


def split_table(r: Mapping[str, object], split: str, reference: str, metrics_: Sequence[str] = TEST_METRICS) -> List[str]:
    labels = r["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in metrics_) + " |", "|---|---|" + "---|" * len(metrics_)]
    for label in sorted(labels):
        g = labels[label]
        untested = f"{split}/{label}" in r["skipped_groups"]
        out.append(f"| {label} | {g['days']} | " + " | ".join("not tested (fewer than 20 days)" if untested else cell(_vs(g, m, reference)) for m in metrics_) + " |")
    return out if len(out) > 2 else []


def coverage_table(r: Mapping[str, object]) -> List[str]:
    """The closed 90% band's coverage of (s3), (s3c) and (s3c-mbs): pooled, by regime, by lead and on the settlement days (means)."""

    out = ["| group | days | (s3) | (s3c) | (s3c-mbs) |", "|---|---|---|---|---|"]
    for split in ("pooled", "regime", "lead", CHANGED):
        for label, g in sorted(r["groups"].get(split, {}).items()):
            m = g["coverage_90"]["means"]
            if not m:
                continue
            out.append(f"| {split.replace('_', ' ')}: {label} | {g['days']} | {m[S3]:.3f} | {m[S3C]:.3f} | {m[S3CM]:.3f} |")
    return out


def effect_tables(fe: Mapping[str, object]) -> List[str]:
    out = ["| indicator | regime of the target day | cells with the indicator at 1 | mean effect (bp) | smallest | largest |", "|---|---|---|---|---|---|"]
    for term, by in fe["effect_bp_by_regime"].items():
        for key, v in by.items():
            out.append(f"| {term} | {key} | {v['cells']} | {v['mean_bp']:+.3f} | {v['min_bp']:+.3f} | {v['max_bp']:+.3f} |")
    out += ["", "| indicator | regime of the refit day | refits in use | refits with the indicator active (lead 1) | median coefficient (scale units) | smallest | largest |",
            "|---|---|---|---|---|---|---|"]
    for term, by in fe["coefficient_by_refit_regime"].items():
        for key, v in by.items():
            out.append(f"| {term} | {key} | {v['refits']} | {v['active']} | {v['median']:+.3f} | {v['min']:+.3f} | {v['max']:+.3f} |")
    return out


def use_table(use: Mapping[str, object]) -> List[str]:
    terms = sorted(use["refits_active"]["1"])
    out = ["| lead | cells | cells with an indicator non-zero | cells where (s3c-mbs) differs from (s3c) | refits in use with each indicator active (" + ", ".join(terms) + ") |",
           "|---|---|---|---|---|"]
    for h in sp.HORIZONS:
        u = use[str(h)]
        out.append(f"| {h} | {u['cells']} | {u['term_nonzero']} | {u['differs_from_s3c']} | " + ", ".join(
            f"{use['refits_active'][str(h)][t]}" for t in terms) + f" of {use['refits_in_use']} |")
    return out


def source_lines(src: Mapping[str, object]) -> List[str]:
    out = [f"**The source and when it is public.** Settlement days in the pooling window (the panel's rows to {src['window_last']}, each read at lead 1, a year "
           "counted only where the archive shows it): " + ", ".join(f"class {kl} {n}" for kl, n in src["settlement_days_in_window"].items())
           + f". The rule pools the classes into one indicator when a class has fewer than {src['min_class_days']}: "
           + ("**the classes were pooled** (indicator `mbs_any`)." if src["pooled"] else "**no class is below it, so the four indicators `mbs_a` to `mbs_d` were kept.**"), "",
           "| year | public from (UTC, the archive's capture) | settlement dates A / B / C / D |", "|---|---|---|"]
    for year, v in src["years"].items():
        stamp = v["public_from_utc"]
        out.append(f"| {year} | {'not shown by any capture: the indicators are 0' if stamp is None else stamp.replace('+00:00', '').replace('T', ' ') + ' UTC'} | "
                   + " / ".join(str(v["dates_by_class"][kl]) for kl in sifma_mbs.CLASSES) + " |")
    return out


def render(r: dict) -> str:
    years = [y for y, v in r["source"]["years"].items() if v["public_from_utc"] is not None]
    dark = [y for y, v in r["source"]["years"].items() if v["public_from_utc"] is None]
    out = [
        "# (s3c-mbs): (s3c) with the settlement days of the agency MBS classes (#1276)", "",
        "**Do the settlement days of the agency MBS classes A to D move the spread, beyond (s3c)'s calendar terms?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c) with a new source, ledger item 68 on #1116. **Development data, not a "
        "verdict** (scoring protocol v1, #640). Her ruling of 27 October 2026 (chat, relayed on #1276) queued four arms on (s3c), one directive each, and added "
        "the source in that ruling; this is the MBS settlement days. **(s3c-mbs)** is (s3c) with one 0/1 indicator per class (A to D) added to (s3)'s fit, 1 on a "
        "target day that is a settlement day of that class and whose year's calendar was public at the decision instant, 0 otherwise; the effect of each is "
        "estimated per lead by the Huber fit in standardised units, the ridge of 5 and the direct pairs of (s3), and a forecast adds the coefficient times the "
        "scale at the anchor to every quantile. Every other term, the fit and the SRF cap at full allotment are (s3c)'s (`repo_model.s3c_mbs`). Nothing is "
        "registered or published and no claim changes. Generated by `scripts/s3c_mbs_1276.py page` from `docs/research/s3c-mbs-1276/result.json`, not edited "
        f"by hand; declared in `{r['declaration']}` and `{r['availability']}` before any score. The page cites no source for the idea beyond her ruling and "
        "compares with no outside figure.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "(s3c-mbs). **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009, 20 October 2026), with the skill "
        "interval beside it. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated about 2x after "
        "2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days keep the **current method** "
        "(the group's days, scattered, resampled in date order as if consecutive), which #1221 questions and #1228 will decide. Where (s3c-mbs) "
        "differs from its reference on few days of a group, some resamples have no long-run variance: the bound is then not computed, the "
        "unstudentized interval of mean d is given beside it, and no reading is taken from it.", "",
        "**What kind of look this is.** The development window and the 2026 days were already seen by the predecessors (#1145, #1229, #1252, #1255, "
        "#1265, #1273, #1274, #1275). This is a check on a term she asked about, not evidence for a verdict.", ""]
    out += source_lines(r["source"]) + [""]
    out += [
        "**Where the indicators can be non-zero.** An indicator is 1 only where the archive shows the year's calendar at the decision instant. "
        f"The years it shows are {', '.join(years)}; for {', '.join(dark)} no capture shows the calendar, so every indicator is 0 there and (s3c-mbs) is "
        "(s3c) up to the refit of the fit. In the years the archive shows, a date is read only from the capture's instant on (a date earlier in the year than "
        "the capture is not read). The fit is trained on all the panel's days, so the days of the years with no capture, on which the classes did settle, enter "
        "it as days without a settlement; that bias, and what to do about it, is the first marked question below. The tables count the cells.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}). The MBS walk refit {r['walk']['refits']} times over the whole panel "
                f"({w['term_use']['refits_in_use']} refits in use in this window).", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled) + ["", "### (s3c-mbs) against each reference (pooled)", ""] + against_table(pooled) + [""]
        out += ["### Where the indicators act", ""] + use_table(w["term_use"]) + [""]
        for split, title in ((CHANGED, "The target days on which the indicators are non-zero against the others, and each indicator's days"), ("regime", "By regime"),
                             ("pressure_day_type", "By pressure-day type of the target day"), ("lead", "By lead"),
                             ("target_day_type", "By calendar target-day type"), ("month", "By target month")):
            table = split_table(w, split, S3C)
            if table:
                out += [f"### {title}: (s3c-mbs) against (s3c)", ""] + table + [""]
        for split, title in ((CHANGED, "the settlement days"), ("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = split_table(w, split, S3)
            if table:
                out += [f"### By {title}: (s3c-mbs) against (s3)", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type"), (CHANGED, "the settlement days")):
            for ref in BENCHMARKS:
                table = split_table(w, split, ref)
                if table:
                    out += [f"### By {title}: (s3c-mbs) against {LABELS[ref]}", ""] + table + [""]
        out += ["### 90% band coverage beside (s3c)'s (means; closed band q05 to q95; nominal 0.90)", ""] + coverage_table(w) + [""]
        out += ["### The fitted effect of each indicator in bp, by regime", "", "The effect is the refit's coefficient times the scale at the decision's anchor, "
                "on the (decision day, lead) cells where the indicator is 1.", ""] + effect_tables(w["fitted_effect"]) + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_records"):
        out += ["## Reproduction of #1255", ""]
        for window, rec in r["against_records"].items():
            out += [f"{WINDOW_TITLES[window].split(' (')[0]}: (s3) and (s3c) pooled means here against `{rec['record']}`: " + "; ".join(
                f"{METRIC_TITLES[m]} (s3c) {v[S3C]['here']:.6f} against {v[S3C]['there']:.6f} (difference {v[S3C]['difference']:+.2e}), (s3) {v[S3]['here']:.6f} "
                f"against {v[S3]['there']:.6f} (difference {v[S3]['difference']:+.2e})" for m, v in rec["metrics"].items()) + ". The frames and the walk are the same.", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. How publication is established for the years the archive does not show.** The archive's captures show the calendar of 2020, 2021, "
        "2024, 2025, 2026 and 2027; they do not show 2018, 2019, 2022 and 2023 (the page of those years carried no label of the years it covered, and the "
        "workbook itself was captured only in 2025). The declaration reads a year as public only from the earliest capture that shows it, and not at all "
        "where none does, so those four years carry no indicator. The cost is a fit that sees the classes settle on days it is told are ordinary.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Keep the declaration as it is** (default). Years with no capture are never public; the result stands as the conservative reading.",
        "2. **Send the Mac to fetch the archive's captures of the workbook files the page linked at each date** (the 2017/06, 2023/03, 2023/06 and 2024/02 "
        "workbooks, `scripts/sifma_wayback_fetch_1276.py --url ...`), then re-declare `public_from` from what they hold, with the first-posted dates of each year "
        "instead of the 2025 file's corrected ones, and re-run.",
        "3. **Read a year's label as covering the earlier years of the same workbook** (so the capture of 2019-08-20, labelled for 2020, would show 2019 and "
        "2018 from that day, and the capture of 2023-03-14 would show 2022 and 2023 from that day). This adds almost no decision instants, since those years had "
        "mostly passed.",
        "4. **Drop the arm.**", "",
        "**Question 2. The dates of the earlier years are the corrected file's.** The workbook the 2017 to 2024 dates are read from was captured on 2025-07-24; "
        "SIFMA's own notes in it record corrections (3/11/2021, 7/15/21 for the Juneteenth settlement of 22 June 2022, and two typos of 2022 in notification dates). "
        "A date as first posted may differ from the one used for 2020 and 2021. Option 2 above is what would show it; the default accepts the file as captured.", "",
        "**Question 3. The source's place in the registry.** `metadata/sources.json` is not edited: any change to it moves the checksums pinned by the final-test "
        "pre-registration (`test_final_test_freeze` and `test_live_score_freeze` fail), as #1241 found for the SRF line. The availability is declared in "
        "`metadata/sifma_mbs_1276.json` and the registry entry is prepared there.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Leave the source in its own declaration file** (default), as the SRF line is.",
        "2. **Add the entry to `metadata/sources.json` and re-pin the final-test pre-registration under your own `GO`** (an owner-attested change).", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3) and the MBS arm, cap it as (s3c) is capped, and score (s3c-mbs) on both windows")
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
