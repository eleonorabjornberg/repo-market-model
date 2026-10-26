"""H5 development step 4 (#758): is more model work worthwhile? H5's best candidate against H2's ceiling.

A development measurement, never a claim and never a verdict (scoring protocol v1, #46). It writes JSON and Markdown to the paths it is given and nothing
into `docs/runs/`, registers nothing and changes no rule. Every choice, the reading rule included, is in `metadata/h5_step4_758.json`, which this script
refuses to read unless it is committed and unchanged. No day after 2025-12-31 and no day of a locked tier is read (`docs/decisions/lockbox.md`).

It puts the candidates of #634 on the scale of H2's upper-bound study (#635): the same 1,598 walk-forward decision days, grid CRPS against B1 on ordinary
targets, beside the cross-fitted ceiling and the reachable line, which are rerun by `scripts/upper_bound_635.py fit` (their per-day laws are not tracked).

    # PUB.csv: the published panel; DERIV.csv: the scratch panel of docs/pivot/derived-features-result.md (Reproduce);
    # T2D.csv: the scratch panel of scripts/spread_distribution_634.py's docstring
    PYTHONPATH=src python3 scripts/upper_bound_635.py fit --panel DERIV.csv --output OUT/fits.json
    for h in 1 2 3 4 5; for v in gbm_funding c_two_part_new:
        PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant $v --horizon $h --published PUB.csv --panel T2D.csv --output OUT/${v}_h$h.json
    PYTHONPATH=src python3 scripts/h5_step4_758.py score --published PUB.csv --fits OUT/fits.json --walks OUT --output score.json
    PYTHONPATH=src python3 scripts/h5_step4_758.py report score.json --output report.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "h5_step4_758.json"
LAST_DAY = date(2025, 12, 31)
SEED = 758
PROTOCOL_DRAWS = 10_000
SPLIT_DRAWS = 2_000
BLOCK = 10
MINIMUM_DAYS = 30
CANDIDATES = ("gbm_funding", "c_two_part_new")
#: H2's recorded skills against B1 on the walk-forward ordinary days (`docs/pivot/evidence/upper-bound/score.json`)
RECORDED = {"reachable gbm": 0.192, "ceiling gbm": 0.162}
RECORDED_TOLERANCE = 0.001


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the pure parts ------------------------------------------------------------------------------------------------


def refuse_after_last_day(days: Sequence[date]) -> None:
    """Refuse a read of a day after 2025-12-31 (the last development day this step may read): raises `LookAheadError`."""

    late = sorted(day for day in days if day > LAST_DAY)
    if late:
        raise LookAheadError(f"{late[0]} is after {LAST_DAY}; step 4 reads development days to 2025-12-31 only (#758)")


def headroom(
    b1: Mapping[date, float], candidate: Mapping[date, float], ceiling: Mapping[date, float], *, draws: int, seed: int, block: float = BLOCK
) -> dict:
    """The ceiling's lead over the candidate in points of skill against B1: `(mean(candidate) - mean(ceiling)) / mean(b1)`.

    The interval is the 5th to 95th percentile of that quantity over `draws` stationary-bootstrap resamples of the decision days, the one resample
    shared by the three series (so the gap is paired, as the protocol's tests are). Positive favours the ceiling.
    """

    from repo_model.metrics import _quantile, stationary_bootstrap_indices

    days = sorted(b1)
    if sorted(candidate) != days or sorted(ceiling) != days:
        raise ValueError("the benchmark, the candidate and the ceiling must score the same decision days")
    n = len(days)
    b = [b1[d] for d in days]
    c = [candidate[d] for d in days]
    u = [ceiling[d] for d in days]
    point = (sum(c) - sum(u)) / sum(b)
    rng = random.Random(seed)
    out = []
    for _ in range(draws):
        indices = stationary_bootstrap_indices(n, block, rng)
        bm = sum(map(b.__getitem__, indices))
        out.append((sum(map(c.__getitem__, indices)) - sum(map(u.__getitem__, indices))) / bm)
    out.sort()
    return {"n": n, "headroom": point, "interval_90": [_quantile(out, 0.05), _quantile(out, 0.95)], "draws": draws}


def recommend(cells: Mapping[str, Mapping]) -> dict:
    """The declared reading rule: headroom is shown where the 90% interval's lower end is above 0 on at least 30 decision days."""

    where = [name for name, cell in cells.items() if cell["n"] >= MINIMUM_DAYS and cell["interval_90"][0] > 0.0]
    return {"recommendation": "continue model work" if where else "stop at the best available candidate", "where": where}


def require_reproduced(rerun: Mapping[str, float], recorded: Mapping[str, float] = RECORDED, tolerance: float = RECORDED_TOLERANCE) -> None:
    """The ceiling and reachable fits are H2's only if the rerun reproduces H2's recorded skills; otherwise `ValueError`."""

    for name, value in recorded.items():
        if abs(rerun[name] - value) > tolerance:
            raise ValueError(f"the rerun of {name} scores {rerun[name]:+.4f} against B1, H2 recorded {value:+.3f}: these are not H2's fits")


def committed_declaration() -> dict:
    return _load("risk_date_severity").committed_declaration(DECLARATION)


def percentile_interval(draws: Sequence[float]) -> Optional[List[float]]:
    from repo_model.metrics import _quantile

    ordered = sorted(draws)
    return [_quantile(ordered, 0.05), _quantile(ordered, 0.95)] if ordered else None


def paired_cell(test) -> dict:
    return {
        "n": test.n,
        "benchmark_mean": test.benchmark_mean,
        "candidate_mean": test.benchmark_mean - test.mean_difference,
        "skill": test.skill,
        "skill_interval_90": percentile_interval(test.skill_draws),
        "lower_mean_difference_one_sided_95": test.lower_mean_difference(),
    }


# -- the measurement -----------------------------------------------------------------------------------------------


def score_command(args) -> int:
    from repo_model import protocol_benchmarks as pb, scoring_protocol as sp
    from repo_model.data import load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.lockbox import require_unlocked

    committed_declaration()
    ub = _load("upper_bound_635")
    sd = _load("spread_distribution_634")
    fits = json.loads(args.fits.read_text(encoding="utf-8"))
    if fits["declaration"] != ub.committed():
        raise SystemExit("the fits were made under a different declaration than metadata/upper_bound_635.json")
    panel = [r for r in load_daily_panel(args.published) if r.date <= LAST_DAY]
    dates = [r.date for r in panel]
    scored_rows = fits["scored_rows"]
    if [dates[i].isoformat() for i in scored_rows] != fits["scored_days"]:
        raise SystemExit("the published panel's days are not the fit panel's")
    refuse_after_last_day(dates[i] for i in scored_rows)
    require_unlocked([dates[i] for i in scored_rows], where="h5_step4_758")
    splits = load_split_declaration(ub.SPLITS)
    registry = json.loads(ub.SOURCES.read_text(encoding="utf-8"))
    decision_time = time(*ub.DECISION_TIME)

    data = ub.unpack(fits)
    models = {(f, m): ub.decision_forecasts(data["forecast"][f][m], scored_rows, dates) for f in ("reachable", "ceiling") for m in ub.MODELS}
    walk_days = sorted(set(models[("reachable", "gbm")]) & set(models[("reachable", "ridge")]))
    b1_all = pb.forecasts(pb.b1_forecast, panel, sorted(set(models[("ceiling", "gbm")]) | set(walk_days)), registry=registry, decision_time=decision_time)
    b2 = {}
    for day in walk_days:
        try:
            b2.update(pb.forecasts(pb.b2_forecast, panel, [day], registry=registry, decision_time=decision_time, splits=splits))
        except sp.ProtocolError:
            pass  # the first decision days have no B2 and are left out of every window (as in H2)
    walk_days = [d for d in walk_days if d in b2]
    if args.without_day is not None:
        # #882 (finding #798): the same scoring on every decision day but one; the day must be a scored one
        walk_days = _load("h5_splits_805").drop_day(walk_days, args.without_day)

    candidates: Dict[str, Dict] = {}
    missing = {}
    for name in CANDIDATES:
        laws = sd.load_laws(args.walks, name)
        decisions, covered = sd.lead_forecasts(laws, dates)
        refuse_after_last_day(dates[dates.index(d) + h] for d in covered for h in sp.HORIZONS)
        usable = [d for d in walk_days if d in decisions]
        if len(usable) != len(walk_days):
            raise SystemExit(f"{name}: its walks cover {len(usable)} of the {len(walk_days)} walk-forward decision days")
        filled = sp.fill_missing({d: decisions[d] for d in walk_days}, {d: b1_all[d] for d in walk_days}, walk_days)
        candidates[name] = filled.forecasts
        missing[name] = {"days": len(filled.missing_days), "share": filled.missing_share}
    forecasts: Dict[str, Dict] = {
        "B1": {d: b1_all[d] for d in walk_days},
        "B2": {d: b2[d] for d in walk_days},
        "reachable gbm": {d: models[("reachable", "gbm")][d] for d in walk_days},
        "ceiling gbm": {d: models[("ceiling", "gbm")][d] for d in walk_days},
        **candidates,
    }
    for fc in forecasts.values():
        refuse_after_last_day(fc)

    ordinary = fits["ordinary"]
    target_date = [dates[i] for i in scored_rows]
    outcome = {d: fits["spread"][p] for p, d in enumerate(target_date) if fits["spread"][p] is not None}
    ordinary_dates = {d for d, o in zip(target_date, ordinary) if o}
    regimes = [splits.regime(d) for d in target_date]
    daytypes = [turn_days.reporting_day_type(splits, d, panel[i].values) for d, i in zip(target_date, scored_rows)]
    every = set(outcome)
    subsets: Dict[str, set] = {"pooled, all targets": every, "pooled, ordinary targets": every & ordinary_dates}
    for label in splits.regime_labels:
        subsets[f"regime: {label}"] = {d for d, r in zip(target_date, regimes) if r == label and d in every} & ordinary_dates
    for kind in sorted(set(daytypes)):
        subsets[f"day type: {kind}"] = {d for d, k in zip(target_date, daytypes) if k == kind and d in every}
    HEADLINE = "pooled, ordinary targets"

    names = list(forecasts)
    ceiling_candidates = list(candidates)
    document: dict = {
        "declaration_sha256": hashlib.sha256(DECLARATION.read_bytes()).hexdigest(),
        "fits_panel_sha256": fits["panel_sha256"],
        "decision_days": {"n": len(walk_days), "first": walk_days[0].isoformat(), "last": walk_days[-1].isoformat()},
        "missing": missing,
        "cells": {},
    }

    def build(kind: str, subset: str, members: set) -> Optional[dict]:
        score = sp.grid_crps if kind == "crps" else sp.upper_tail_twcrps
        outcomes = {d: (outcome[d] if d in members else None) for d in outcome}
        scores = {k: sp.day_scores(fc, outcomes, dates, score=score) for k, fc in forecasts.items()}
        days = set.intersection(*(set(v) for v in scores.values()))
        if len(days) < MINIMUM_DAYS:
            return {"n": len(days), "note": f"fewer than {MINIMUM_DAYS} decision days"}
        scores = {k: {d: v[d] for d in days} for k, v in scores.items()}
        draws = PROTOCOL_DRAWS if subset in (HEADLINE, "pooled, all targets") and kind == "crps" else SPLIT_DRAWS
        pairs, keys = [], []
        for bench in ("B1", "B2"):
            for k in names[2:]:
                pairs.append((scores[bench], scores[k]))
                keys.append(f"{bench} -> {k}")
        for c in ceiling_candidates:
            for upper in ("ceiling gbm", "reachable gbm"):
                pairs.append((scores[c], scores[upper]))
                keys.append(f"{c} -> {upper}")
        tests = sp.paired_tests(pairs, seed=SEED, draws=draws)
        cell = {"n": len(days), "draws": draws, "means": {k: sum(v.values()) / len(v) for k, v in scores.items()}, "tests": {}, "headroom": {}}
        for key, test in zip(keys, tests):
            cell["tests"][key] = paired_cell(test)
        for c in ceiling_candidates:
            for upper in ("ceiling gbm", "reachable gbm"):
                cell["headroom"][f"{c} -> {upper}"] = headroom(scores["B1"], scores[c], scores[upper], draws=draws, seed=SEED)
        return cell

    for kind in ("crps", "twcrps"):
        document["cells"][kind] = {}
        for subset, members in subsets.items():
            if kind == "twcrps" and not subset.startswith("pooled"):
                continue
            document["cells"][kind][subset] = build(kind, subset, members)
            print(json.dumps({"scored": kind, "subset": subset}), flush=True)

    head = document["cells"]["crps"][HEADLINE]
    rerun = {k: head["tests"][f"B1 -> {k}"]["skill"] for k in RECORDED}
    document["reproduction"] = {"rerun": rerun, "recorded": RECORDED, "tolerance": args.tolerance, "fits_panel_sha256": fits["panel_sha256"]}
    print(json.dumps({"reproduction": document["reproduction"]}), flush=True)
    if args.without_day is None:
        require_reproduced(rerun, tolerance=args.tolerance)
    else:
        document["without_day"] = args.without_day.isoformat()
    best = min(ceiling_candidates, key=lambda c: head["means"][c])
    document["best_candidate"] = best
    reading_cells = {}
    for subset, cell in document["cells"]["crps"].items():
        if "headroom" in cell:
            reading_cells[subset] = cell["headroom"][f"{best} -> ceiling gbm"]
    tail = document["cells"]["twcrps"]
    for subset, cell in tail.items():
        if "headroom" in cell:
            reading_cells[f"upper tail (twCRPS), {subset.replace('pooled, ', '')}"] = cell["headroom"][f"{best} -> ceiling gbm"]
    document["reading"] = {**recommend(reading_cells), "candidate": best, "cells_read": sorted(reading_cells)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "reading": document["reading"]}))
    return 0


# -- the report ----------------------------------------------------------------------------------------------------


def _f(value: float, digits: int = 3, signed: bool = True) -> str:
    return f"{value:+.{digits}f}" if signed else f"{value:.{digits}f}"


def _iv(interval, digits: int = 3) -> str:
    return "n/a" if interval is None else f"[{_f(interval[0], digits)}, {_f(interval[1], digits)}]"


def report_command(args) -> int:
    document = json.loads(args.score.read_text(encoding="utf-8"))
    best = document["best_candidate"]
    lines = [
        "# H5 step 4: the best candidate against H2's ceiling (#758), tables",
        "",
        f"Decision days: {document['decision_days']['n']} ({document['decision_days']['first']} to {document['decision_days']['last']}).",
        "Skill = (mean S(B1) - mean S(forecast)) / mean S(B1), with the 90% interval of the stationary bootstrap (5th to 95th percentile). Headroom = skill(ceiling) - skill(candidate) in points of skill, paired, same resample.",
        "",
    ]
    for kind, title in (("crps", "Grid CRPS (bp)"), ("twcrps", "Upper-tail twCRPS, weight 1{y > 0 bp}")):
        for subset, cell in document["cells"][kind].items():
            lines += [f"## {title}: {subset}", ""]
            if "tests" not in cell:
                lines += [f"n = {cell['n']}: {cell.get('note', '')}", ""]
                continue
            lines += [f"n = {cell['n']} decision days, {cell['draws']} draws.", "", "| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |", "|---|---|---|---|"]
            for k in cell["means"]:
                if k in ("B1", "B2"):
                    lines.append(f"| {k} | {_f(cell['means'][k], 3, False)} | | |")
                    continue
                t1, t2 = cell["tests"][f"B1 -> {k}"], cell["tests"][f"B2 -> {k}"]
                lines.append(f"| {k} | {_f(cell['means'][k], 3, False)} | {_f(t1['skill'])} {_iv(t1['skill_interval_90'])} | {_f(t2['skill'])} {_iv(t2['skill_interval_90'])} |")
            lines += ["", "| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |", "|---|---|---|"]
            for k, h in cell["headroom"].items():
                rel = cell["tests"][k]
                lines.append(f"| {k} | {_f(h['headroom'])} {_iv(h['interval_90'])} | {_f(rel['skill'])} {_iv(rel['skill_interval_90'])} |")
            lines.append("")
    reading = document["reading"]
    lines += [f"Reading on {best}: **{reading['recommendation']}**; headroom shown in: {', '.join(reading['where']) or 'nowhere'}.", ""]
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


from repo_model import turn_days  # noqa: E402


@turn_days.with_legacy_flag
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("score")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--fits", type=Path, required=True)
    p.add_argument("--walks", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--without-day", type=date.fromisoformat, default=None, help="leave this decision day out of every window (#882); the reproduction check is then not made")
    p.add_argument("--tolerance", type=float, default=RECORDED_TOLERANCE, help="how far the rerun's skills may sit from H2's recorded ones")
    p.set_defaults(run=score_command)
    p = sub.add_parser("report")
    p.add_argument("score", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
