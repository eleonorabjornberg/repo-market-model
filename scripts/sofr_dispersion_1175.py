"""The H5 candidate scaled by SOFR's in-panel dispersion, scored (#1175; H5 step 3, avenue #1166 option 1).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/sofr_dispersion_1175.json`, which this script refuses to read unless it is committed and unchanged.
The base is (s3) of #1145 (`repo_model.spread_mr_state_calendar`), the comparator beside it is (a), #941's variant
(`repo_model.spread_mr_fhs`); the arms (d1) to (d3) are `repo_model.spread_mr_dispersion` (the scale times a factor read from the
as-of SOFR interquartile range, or from `sofr_p75 - SOFR`, relative to its trailing median, fitted walk-forward and capped; (d3)
on the upper half of the law only). They are scored with the scorer of scoring protocol v1 (`repo_model.scoring_protocol`)
against (s3), (a), B1 with B1' beside it and B2 (`repo_model.protocol_benchmarks`, `repo_model.b1_calendar`), on the studentized
stationary bootstrap of ruling 1 (#739), the skill interval with the studentized interval of mean(d) beside it and the reading on
that bound (#1009), the Politis-White block beside the block of 10 and the scaled score of #967 beside the raw one. Scored
decision days are those whose five targets are on or before 2025-12-31; no later day is read and no locked day is scored
(`docs/decisions/lockbox.md`).

The headline is the clustering of the misses, as #1153: coverage of the 50, 80, 90 and 98% bands, the exceedances of q05, q95,
q01 and q99, Kupiec's test, Christoffersen's independence and conditional coverage tests per lead under both hit rules, and the
length of the runs of misses, against (s3). The hit rule is Eleonora's open question (#993): both are reported.
The randomised tie rule of #1156 is not on main (PR #1160 is open) and is reported as not available.

The helpers of `scripts/faster_scale_1153.py` (the cells, the runs, the hit tables, the kill assessment) are used unchanged.
Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/sofr_dispersion_1175.py score --panel PUB.csv \\
        --output docs/research/sofr-dispersion-1175/result.json
    PYTHONPATH=src python3 scripts/sofr_dispersion_1175.py page \\
        --score docs/research/sofr-dispersion-1175/result.json --output docs/research/sofr-dispersion-1175-result.md

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
    loaded = sys.modules.get(name)
    if loaded is not None and Path(getattr(loaded, "__file__", "")) == REPO / "scripts" / f"{name}.py":
        return loaded
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, b1_calendar as b1c  # noqa: E402
from repo_model import coverage_tests as ct  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_dispersion as dsp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

f1153 = _load("faster_scale_1153")
s686, s761, s967, f941, b949, w1133 = f1153.s686, f1153.s761, f1153.s967, f1153.f941, f1153.b949, f1153.w1133

DECLARATION = REPO / "metadata" / "sofr_dispersion_1175.json"
IORB_TABLE = f1153.IORB_TABLE
SEED = 1175
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
A = dsp.ARM_A
S3 = dsp.BASE_ARM.name
ARMS: Tuple[str, ...] = tuple(a.name for a in dsp.ARMS)
BENCHMARKS: Tuple[str, ...] = f1153.BENCHMARKS
#: What each candidate is paired against, besides the benchmarks.
COMPARATORS: Tuple[str, ...] = (S3, A)
METRICS = f1153.METRICS
COVERAGE_METRICS = f1153.COVERAGE_METRICS
BANDS = f1153.BANDS
REGIME_ORDER, DAYTYPE_ORDER = f1153.REGIME_ORDER, f1153.DAYTYPE_ORDER
SPLIT_TITLES, METRIC_TITLES = f1153.SPLIT_TITLES, f1153.METRIC_TITLES
OFF_ZERO = f1153.OFF_ZERO
LABELS: Dict[str, str] = {
    "B1": "B1", "B1p": "B1' (#960)", "B2": "B2", A: "(a) #941 mad20", S3: "(s3) base (#1145)",
    "d1_iqr": "(d1) IQR scale", "d2_upper_half": "(d2) p75 - SOFR scale", "d3_iqr_upper_tail": "(d3) IQR scale, upper tail only",
}
LENS_C = ("Lens C's caveat (#958, #1009): the lag-10 HAC standard error behind a studentized interval is understated by about 2x "
          "after 2020, so an interval after 2020 is narrower than it should be.")


def label_of(model: str) -> str:
    return LABELS.get(model, model)


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def constants_agree(declaration: Mapping) -> List[str]:
    """The names of the declared constants that differ from the module's (empty when they agree)."""

    declared = declaration["arms"]["constants"]
    actual = {
        "window_rows": dsp.WINDOW, "min_rows": dsp.MIN_ROWS, "median_floor_bp": dsp.MEDIAN_FLOOR_BP, "ratio_cap": dsp.X_CAP,
        "factor_min": dsp.F_MIN, "factor_max": dsp.F_MAX, "gamma_max": dsp.GAMMA_MAX, "min_pairs": dsp.MIN_PAIRS,
        "ridge": dsp.sc.ROBUST_RIDGE, "huber_k": dsp.sc.HUBER_K,
    }
    return sorted(k for k in set(declared) | set(actual) if declared.get(k) != actual.get(k))


# -- the frame ----------------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, table, first: Optional[date] = None):
    """The decision days with a forecast of (a), (s3), every arm and the benchmarks, whose five targets are scored days.

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
    walk = dsp.walk(panel, [d for d in candidate_days if d in b1], table, **settings)
    days = [d for d in candidate_days if d in b1 and all(d in walk.forecasts[m] for m in dsp.MODEL_NAMES)]
    frame.days = days
    frame.forecasts = {"B1": {d: b1[d] for d in days}, "B1p": {d: b1p[d] for d in days}, "B2": {d: b2[d] for d in days},
                       **{m: {d: walk.forecasts[m][d] for d in days} for m in dsp.MODEL_NAMES}}
    frame.all_days = days
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(walk.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(walk.fits),
    }
    gammas: Dict[str, Dict[str, List[float]]] = {a: {str(h): [] for h in sp.HORIZONS} for a in ARMS}
    for per_arm in walk.leads.values():
        for arm, per_lead in per_arm.items():
            for h, fit in per_lead.items():
                gammas[arm][str(h)].append(fit.gamma)
    ratios = {kind: [walk.detail[d][kind] for d in days] for kind in ("iqr", "upper")}
    diagnostics = {"gamma": gammas, "ratio_at_anchor": {k: _summary(v) for k, v in ratios.items()}}
    return frame, notes, diagnostics


def _summary(values: Sequence[float]) -> dict:
    ordered = sorted(values)
    n = len(ordered)
    return {"n": n, "min": ordered[0], "median": ordered[n // 2], "max": ordered[-1], "mean": sum(ordered) / n,
            "share_at_cap": sum(1 for v in ordered if v >= dsp.X_CAP) / n, "share_neutral": sum(1 for v in ordered if v == 1.0) / n}


def models_of() -> Tuple[str, ...]:
    return BENCHMARKS + (A, S3) + ARMS


def candidates_of() -> Tuple[str, ...]:
    return (A, S3) + ARMS


# -- the tests, in parallel ---------------------------------------------------------------------------------------------

_STATE: Dict = {}


def _members(series, members, models):
    return [d for d in sorted(members) if all(d in series[m] for m in models)]


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    names = list(BENCHMARKS) + [c for c in COMPARATORS if c != candidate]
    days = _members(series, members, list(names) + [candidate])
    if len(days) < MIN_GROUP_DAYS:
        return (split, label, metric, candidate), {
            n: {"undefined": "fewer than %d days with a scale" % MIN_GROUP_DAYS, "days": len(days)} for n in names}
    return (split, label, metric, candidate), s761.run_pairs(
        {n: series[n] for n in names}, series[candidate], days, seed=SEED, draws=_STATE["draws"])


def _coverage_task(job):
    split, label, grain, metric, members = job
    series = _STATE["series"][(grain, metric)]
    models = _STATE["models"]
    ordered = _members(series, members, models)
    pooled = split == "pooled"
    out = {}
    for model in models:
        values = [series[model][d] for d in ordered]
        entry = {"mean": sum(values) / len(values)}
        if pooled:
            entry["interval"] = f941.mean_interval(values, seed=SEED, reps=_STATE["reps"])
        out[model] = entry
    return (split, label, metric), out


def _block_task(job):
    """The Politis-White block of the paired loss differential of an arm against (s3), and the pooled skill at that block."""

    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = _members(series, members, [S3, candidate])
    d = [series[S3][x] - series[candidate][x] for x in ordered]
    try:
        block = b949.politis_white(d)
    except ValueError:
        return (split, label, metric, candidate), None
    entry = {"block": block, "days": len(ordered)}
    if split == "pooled":
        at = max(1, round(block))
        test = sp.paired_tests([({x: series[S3][x] for x in ordered}, {x: series[candidate][x] for x in ordered})], seed=SEED,
                               draws=_STATE["draws"], block_length=float(at))[0]
        entry["at_block"] = at
        entry["row"] = s761.paired_row(test)
    return (split, label, metric, candidate), entry


def _dispatch(job):
    kind, payload = job
    return kind, {"pairs": _pairs_task, "coverage": _coverage_task, "block": _block_task}[kind](payload)


def run_jobs(jobs, workers: int):
    context = multiprocessing.get_context("fork")
    with context.Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- the kill rule, against (s3) -----------------------------------------------------------------------------------------


def kill_assessment(hits: Mapping) -> dict:
    """The declared kill rule against (s3): see `faster_scale_1153.kill_assessment`, with (s3) as the base."""

    return f1153.kill_assessment(hits, (S3,) + ARMS, S3)


# -- the report ---------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    differ = constants_agree(declaration)
    if differ:
        raise SystemExit(f"the declared constants differ from spread_mr_dispersion's: {', '.join(differ)}")
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(s686.SPLITS)
    registry = json.loads(s686.SOURCES.read_text(encoding="utf-8"))
    table = cal.TermTable(panel, announced_iorb.load_announcements(IORB_TABLE), decision_time=DECISION_TIME)
    frame, notes, diagnostics = build_frame(panel, splits, registry, table, args.first)
    models, candidates = models_of(), candidates_of()
    cells = f1153.all_cells(frame, models)
    groups = f941.groups_of(frame)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _split, _label, grain, _members_ in groups:
        for metric in METRICS + COVERAGE_METRICS:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: f941.series_of(frame, cells[metric][m], grain) for m in models}
    _STATE.update(series=series, draws=args.draws, reps=args.reps, models=models)
    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRICS:
            if split == "lead" and metric == "scaled_grid_crps":
                continue
            for candidate in candidates:
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
                if candidate in ARMS and split in ("pooled", "regime") and metric != "scaled_grid_crps":
                    jobs.append(("block", (split, label, grain, metric, candidate, tuple(members))))
        for metric in COVERAGE_METRICS:
            jobs.append(("coverage", (split, label, grain, metric, tuple(members))))
    done = run_jobs(jobs, args.workers)
    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1175, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps,
        "notes": notes, "models": list(models), "base": S3, "comparators": list(COMPARATORS), "arms": list(ARMS),
        "diagnostics": diagnostics, "groups": {}, "skipped_groups": skipped, "politis_white": {},
        "randomised_tie_rule": "not available: #1156 is not on main (PR #1160 is open)",
    }
    for kind, (ident, payload) in done:
        split, label, metric = ident[:3]
        if kind == "block":
            result["politis_white"].setdefault(split, {}).setdefault(label, {}).setdefault(metric, {})[ident[3]] = payload
            continue
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
        if kind == "pairs":
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][ident[3]] = payload
        else:
            entry[metric] = payload
    for split, labels in result["groups"].items():
        for label, entry in labels.items():
            grain, members = by_key[(split, label)]
            for metric in METRICS:
                if split == "lead" and metric == "scaled_grid_crps":
                    continue
                ser = series[(grain, metric)]
                days = _members(ser, members, models)
                entry[metric]["means"] = {m: sum(ser[m][d] for d in days) / len(days) for m in models} if days else {}
                entry[metric]["days"] = len(days)
    result["hits"] = f1153.hit_tables(frame, models)
    result["kill"] = kill_assessment(result["hits"])
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page -----------------------------------------------------------------------------------------------------------


def skill(row: Optional[dict]) -> str:
    return "n/a" if row is None else s761.skill_text(row)


def bound(row: Optional[dict]) -> str:
    """The studentized interval of mean(d) of one row."""

    return "n/a" if row is None else s761.diff_text(row)


def reading(row: Optional[dict]) -> str:
    """The reading on the mean-d bound (#1009): gain, loss or undecided."""

    if row is None or "undefined" in row:
        return "undecided"
    lo, hi = row["difference_interval"]
    return "gain" if lo > 0.0 else "loss" if hi < 0.0 else "undecided"


def _ordered(split: str, labels) -> List[str]:
    return f941._ordered(split, labels)


HEADER = ["| | mean | vs B1: skill [90%] | vs B1': skill [90%] | vs B2: skill [90%] | vs (a): skill [90%]; mean d [90%] | "
          "vs (s3): skill [90%]; mean d [90%]; reading |", "|---|---|---|---|---|---|---|"]


def _score_rows(cell: dict, r: dict) -> List[str]:
    means = cell["means"]
    if not means:
        return ["| (no day with a scale) | | | | | | |"]
    out = [f"| {label_of(m)} | {means[m]:.3f} | | | | | |" for m in BENCHMARKS]
    for m in candidates_of():
        vs = cell["vs"][m]
        cols = []
        for c in COMPARATORS:
            if c == m:
                cols.append("")
            else:
                cols.append(f"{skill(vs[c])}; {bound(vs[c])}" + ("; " + reading(vs[c]) if c == S3 else ""))
        out.append(f"| {label_of(m)} | {means[m]:.3f} | {skill(vs['B1'])} | {skill(vs['B1p'])} | {skill(vs['B2'])} | "
                   f"{cols[1]} | {cols[0]} |")
    return out


def _fmt_p(e: Optional[dict], key: str) -> str:
    return "n/a" if not e or not e.get(key) else f"{e[key]['p_value']:.3f}"


def clustering_section(r: dict) -> List[str]:
    hits, models = r["hits"], list(r["comparators"]) + r["arms"]
    out = ["## The clustering of the 90% band's misses (the headline of this fix)", "",
           "Per lead, pooled over the scored days: the miss rate (nominal 0.10), then Christoffersen's independence p and the conditional "
           "coverage p. A p of 0.000 is below 0.0005. Reporting only: no p-value is a gate.", ""]
    for rule in hits["rules"]:
        words = "closed band, a miss is `y` outside `[q05, q95]`" if rule == "above" else "open band, a miss includes `y` equal to a bound"
        out += [f"Rule `{rule}` ({words}); rate (independence p / conditional coverage p):", "",
                "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for m in models:
            cells = []
            for h in sp.HORIZONS:
                e = hits["rows"][m][rule]["band90"].get(f"h={h}", {}).get("pooled")
                cells.append("n/a" if e is None else f"{e['rate']:.3f} ({_fmt_p(e, 'independence')} / {_fmt_p(e, 'conditional')})")
            out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
        out.append("")
    out += [f"The randomised tie rule of #1156: {r['randomised_tie_rule']}.", "",
            "Independence p of the 90% band's misses within a regime (consecutive days of the regime), by lead, closed rule (`above`):", ""]
    for regime in REGIME_ORDER:
        out += [f"**{regime}**", "", "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for m in models:
            out.append(f"| {label_of(m)} | " + " | ".join(
                _fmt_p(hits["rows"][m]["above"]["band90"].get(f"h={h}", {}).get(f"regime/{regime}"), "independence")
                for h in sp.HORIZONS) + " |")
        out.append("")
    out += ["### Miss runs", "",
            "A run is a block of consecutive misses in a lead's sequence of consecutive decision days. Pooled over the five leads: the number "
            "of runs, the mean run length (misses per run; about 1.11 for independent misses at a 10% rate) and the longest run, for the "
            "90% band and for q95 (above its quantile).", ""]
    for rule in hits["rules"]:
        out += [f"Rule `{rule}`:", "", "| | 90% band: runs | mean | longest | q95: runs | mean | longest |", "|---|---|---|---|---|---|---|"]
        for m in models:
            band = f1153.pooled_runs([hits["rows"][m][rule]["band90"][f"h={h}"]["runs"] for h in sp.HORIZONS])
            tail = f1153.pooled_runs([hits["rows"][m][rule]["q95"][f"h={h}"]["runs"] for h in sp.HORIZONS])
            f = lambda x: "n/a" if x["mean"] is None else f"{x['mean']:.3f}"  # noqa: E731
            out.append(f"| {label_of(m)} | {band['runs']} | {f(band)} | {band['longest']} | {tail['runs']} | {f(tail)} | {tail['longest']} |")
        out.append("")
    return out


def kill_section(r: dict) -> List[str]:
    k = r["kill"]
    out = ["## Against the kill rule", "",
           "The kill rule (the issue's, read in the declaration): stop if no arm moves the independence p-value off 0.000 at any lead and no "
           f"arm shortens the miss runs. 'Off 0.000' is a pooled independence p of the 90% band of at least {k['off_zero_threshold']}, "
           "at any lead, under either hit rule; 'shortens' is a mean run (closed rule, pooled over leads) below (s3)'s "
           f"({k['base_mean_run']:.3f}).", "",
           "| model | leads off 0.000, `above` | leads off 0.000, `at_or_above` | mean run, `above` (longest) | mean run, `at_or_above` (longest) |",
           "|---|---|---|---|---|"]
    for m in [S3] + r["arms"]:
        e = k["models"][m]
        fm = lambda x: "n/a" if x["mean"] is None else f"{x['mean']:.3f} ({x['longest']})"  # noqa: E731
        leads = {rule: (", ".join(f"h={h}" for h in e["off_zero_leads"][rule]) or "none") for rule in e["off_zero_leads"]}
        out.append(f"| {label_of(m)} | {leads['above']} | {leads['at_or_above']} | {fm(e['runs']['above'])} | {fm(e['runs']['at_or_above'])} |")
    out += ["", f"Arms with a lead off 0.000: {', '.join(label_of(m) for m in k['arms_off_zero']) or 'none'}. "
            f"Arms with a shorter mean run than (s3): {', '.join(label_of(m) for m in k['arms_shorter_runs']) or 'none'}. "
            f"**The kill rule is {'met' if k['met'] else 'not met'}.**", ""]
    return out


def diagnostics_section(r: dict) -> List[str]:
    d = r["diagnostics"]
    mid = lambda v: sorted(v)[len(v) // 2] if v else float("nan")  # noqa: E731
    out = ["## What the fit did", "",
           "The slope gamma of the factor `1 + gamma (x - 1)`, fitted at each refit and lead (0 where the dispersion carries nothing about "
           "the size of the miss): the median over the refits, with the share of refits at 0 and at the cap "
           f"({dsp.GAMMA_MAX:g}).", "", "| arm | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
    for arm in r["arms"]:
        cells = []
        for h in sp.HORIZONS:
            g = d["gamma"][arm][str(h)]
            cells.append(f"{mid(g):.3f} ({sum(1 for x in g if x == 0.0) / len(g):.2f} / {sum(1 for x in g if x >= dsp.GAMMA_MAX) / len(g):.2f})")
        out.append(f"| {label_of(arm)} | " + " | ".join(cells) + " |")
    out += ["", "Cells: median gamma (share of refits at 0 / share at the cap).", "",
            "The ratio at the anchor on the scored decision days (1 is the trailing median; the cap is "
            f"{dsp.X_CAP:g}):", "", "| numerator | min | median | mean | max | share at the cap | share neutral |", "|---|---|---|---|---|---|---|"]
    for kind, name in (("iqr", "IQR, p75 - p25"), ("upper", "p75 - SOFR")):
        s = d["ratio_at_anchor"][kind]
        out.append(f"| {name} | {s['min']:.2f} | {s['median']:.2f} | {s['mean']:.2f} | {s['max']:.2f} | {s['share_at_cap']:.3f} | {s['share_neutral']:.3f} |")
    out.append("")
    return out


def coverage_section(r: dict) -> List[str]:
    out = ["## Band coverage", "",
           "Share of (decision day, lead) cells whose outcome is inside the band, with its 90% interval (pooled). Closed: `q_lo <= y <= q_hi` "
           "(the hit rule `y > q`); open: `q_lo < y < q_hi` (the rule `y >= q`). Nominal 0.50, 0.80, 0.90, 0.98. The hit rule is Eleonora's "
           "open question (#993) and both are reported.", ""]
    groups = [("pooled", "all decision days")] + [("lead", f"h={h}") for h in sp.HORIZONS] + [
        (s_, l) for s_ in ("regime", "pressure_day_type") for l in _ordered(s_, r["groups"].get(s_, {}))]
    for c in BANDS:
        for kind in ("closed", "open"):
            metric = f"cover{c}_{kind}"
            out += [f"**{c}% band, {kind}**", "", "| | " + " | ".join(l for _, l in groups) + " |", "|---|" + "---|" * len(groups)]
            for m in r["models"]:
                cells = []
                for split, label in groups:
                    e = r["groups"][split][label][metric][m]
                    cells.append(f"{e['mean']:.3f}" + (f" [{e['interval'][0]:.3f}, {e['interval'][1]:.3f}]" if "interval" in e else ""))
                out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
            out.append("")
    return out


def hit_section(r: dict) -> List[str]:
    hits = r["hits"]
    models = list(r["comparators"]) + r["arms"]
    out = ["## Exceedances and band misses, by lead, under both hit rules", "",
           "Each cell is the rate (nominal in the heading) with the p-values of Kupiec's unconditional coverage test, Christoffersen's "
           "independence test and his conditional coverage test (`repo_model.coverage_tests`). Upper tails: the outcome above q95 / q99; "
           "lower tails: below q05 / q01; a band miss: outside the band. Reporting only: no p-value is a gate. By regime and "
           "pressure-day type, the five leads together with Kupiec's p; the independence tests per regime and lead are in `result.json`.", ""]
    nominal = w1133.kinds_and_p()
    for rule in hits["rules"]:
        words = "strictly beyond the quantile / outside the closed band" if rule == "above" else "at or beyond the quantile / outside the open band"
        for kind in hits["kinds"]:
            p = nominal[kind]
            out += [f"### {kind} (nominal {p:.2f}), rule `{rule}` ({words})", "",
                    "Pooled; rate (Kupiec p / independence p / conditional coverage p):", "",
                    "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
            for m in models:
                cells = []
                for h in sp.HORIZONS:
                    e = hits["rows"][m][rule][kind].get(f"h={h}", {}).get("pooled")
                    cells.append("n/a" if e is None else
                                 f"{e['rate']:.3f} ({e['kupiec']['p_value']:.3f} / {e['independence']['p_value']:.3f} / {e['conditional']['p_value']:.3f})")
                out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
            out.append("")
            for split, order in (("regime", REGIME_ORDER), ("pressure_day_type", DAYTYPE_ORDER)):
                out += [f"By {SPLIT_TITLES[split]}: rate (Kupiec p).", "",
                        "| | " + " | ".join(order) + " |", "|---|" + "---|" * len(order)]
                for m in models:
                    cells = []
                    for label in order:
                        total = hit_count = 0
                        for h in sp.HORIZONS:
                            e = hits["rows"][m][rule][kind].get(f"h={h}", {}).get(f"{split}/{label}")
                            if e is not None:
                                total, hit_count = total + e["n"], hit_count + e["hits"]
                        cells.append("n/a" if not total else
                                     f"{hit_count / total:.3f} ({ct.kupiec([1] * hit_count + [0] * (total - hit_count), p).p_value:.3f})")
                    out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
                out.append("")
    return out


def politis_white_section(r: dict) -> List[str]:
    out = ["## The Politis-White block beside the block of 10", "",
           "The automatic block length (Politis and White 2004, with the correction of Patton, Politis and White 2009, "
           "`scripts/block_length_949.py`) of the paired loss differential `S(s3) - S(arm)`, in days, with the pooled skill over (s3) at that "
           "block. Reported, never substituted for 10.", ""]
    columns = ["pooled"] + [l for l in REGIME_ORDER if l in r["politis_white"].get("regime", {})]
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(columns) + " | pooled skill vs (s3) at that block |", "|---|" + "---|" * (len(columns) + 1)]
        for m in r["arms"]:
            cells, at = [], ""
            for col in columns:
                split, label = ("pooled", "all decision days") if col == "pooled" else ("regime", col)
                e = r["politis_white"].get(split, {}).get(label, {}).get(metric, {}).get(m)
                cells.append("n/a" if not e else f"{e['block']:.1f}")
                if col == "pooled" and e and "row" in e:
                    at = f"block {e['at_block']}: {skill(e['row'])}"
            out.append(f"| {label_of(m)} | " + " | ".join(cells) + f" | {at} |")
        out.append("")
    return out


def render(r: dict) -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# The H5 candidate scaled by SOFR's in-panel dispersion (#1175)", "",
        f"**Hypothesis and step:** H5 (primary goal), step 3 (fix), the clustered misses of the scaled mean reversion, avenue #1166 option 1 "
        f"(Eleonora, 23 October 2026). **{r['label'].capitalize()}**: development days to {n['last_target']}, no verdict (scoring protocol v1, "
        "#640). Any change to the candidate is Eleonora's decision. Generated by `scripts/sofr_dispersion_1175.py page` from "
        f"`docs/research/sofr-dispersion-1175/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business "
        f"days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval. Skill is `mean(d) / mean(S(comparator))` with "
        "`d = S(comparator) - S(candidate)`, positive favours the candidate; beside it the studentized interval of mean(d) itself (the "
        "mean-d bound of #1009), on which the reading is made: a gain when the interval is above zero, a loss when below, otherwise "
        f"undecided. {LENS_C} Coverage intervals are 90% stationary-bootstrap percentile intervals ({r['reps']:,} resamples), pooled. "
        f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); every model is scored on the same days.", "",
        "**What this is.** The base is (s3) of #1145: #941's scaled mean reversion with state-scaled calendar terms, a Huber fit and ridge "
        "5, the calendar read at the target day on direct pairs. The arms multiply its scale by a factor read from SOFR's own dispersion "
        "as of the decision (`sofr_p25`, `sofr_p75`, `sofr`, all in the panel; the tail percentiles p1 and p99 are not read and stay out "
        "of the panel). (a) is #941's variant, beside. The base was chosen after seeing 2018-2025. `gbm_funding` is not compared "
        "(its walks are a long run for Eleonora's Mac and the directive does not ask for it).", ""]
    out += kill_section(r)
    out += clustering_section(r)
    for metric in METRICS:
        out += [f"## {METRIC_TITLES[metric]}, mean over leads 1 to 5, pooled", ""] + HEADER + _score_rows(pooled[metric], r) + [""]
    out += ["## Skill of each arm over (s3), by lead [90%]; mean d [90%]", ""]
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for m in r["arms"]:
            out.append(f"| {label_of(m)} | " + " | ".join(
                skill(r["groups"]["lead"][f"h={h}"][metric]["vs"][m][S3]) + "; " + bound(r["groups"]["lead"][f"h={h}"][metric]["vs"][m][S3])
                for h in sp.HORIZONS) + " |")
        out.append("")
    for split in ("regime", "pressure_day_type"):
        labels = _ordered(split, r["groups"].get(split, {}))
        for metric in METRICS:
            out += [f"## {METRIC_TITLES[metric]} by {SPLIT_TITLES[split]}", ""]
            for label in labels:
                cell = r["groups"][split][label][metric]
                out += [f"**{label}** ({cell.get('days', 0)} days)", ""] + HEADER + _score_rows(cell, r) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## Reading under the declared rule", "",
            "On the grid CRPS against (s3), the mean-d bound: a gain is a studentized interval of mean(d) above zero, a loss below zero, "
            "otherwise undecided. The skill interval is shown beside and not read.", ""]
    for m in r["arms"]:
        parts = []
        for split in ("pooled", "regime", "pressure_day_type"):
            for label in _ordered(split, r["groups"].get(split, {})):
                parts.append(f"{label}: {reading(r['groups'][split][label]['grid_crps']['vs'][m][S3])}")
        out.append(f"- **{label_of(m)}**: " + "; ".join(parts) + ".")
    out.append("")
    out += diagnostics_section(r)
    out += coverage_section(r)
    out += hit_section(r)
    out += politis_white_section(r)
    return "\n".join(out) + "\n"


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (a), (s3) and the arms and score them")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of a coverage interval")
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
