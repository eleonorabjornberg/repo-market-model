"""B2*-cap proper: the capped-baselines study of #1421 re-run with B2* (#1440, the finding of #1434; H5, registration design, benchmarks, step 3).

A development study, never a verdict. #1422 scored "B2*-cap" with plain B2 standing in, because B2* (#1420) was thought not to be on main; #1423 had merged. This
study is the same study with the stand-in replaced: B2* is `protocol_benchmarks.b2_star_forecast` and B2*-cap is `protocol_benchmarks.b2_star_capped_forecast` (B2*
clipped at the candidate's own Standing Repo Facility line on target days at full allotment, the rule of B1'*-cap). The candidate is walked as #1288, #1314 and
#1389 did (the code of `scripts/s3c_announced_settlement_1288.py`, unchanged, at the 18:00 decision instant); B1'* and B2* are computed on the same decision days;
each baseline is scored uncapped and capped, every probability read under rule (b) (`capped_law`, `open_tail`). Grid CRPS (primary), upper-tail twCRPS and the Brier
score of P(> +5 bp), pooled and on the cells at full allotment, by regime and by pressure-day type, on the development window (targets to 2025-12-31, which decides
what the page reads) and, apart, on the 2026 days; the candidate against each baseline, each cap against its uncapped version, and the share of the candidate's gain
the cap alone buys. The seed stays #1421's so the unchanged rows (the candidate, B1'*, B1'*-cap) reproduce #1422's page; the result refuses to be written unless they
do. Every choice is in `metadata/capped_baselines_b2star_1434.json`, which `walk` and `score` refuse to read unless it is committed and unchanged.

Commands (a cloud run; each walk is minutes, the paired tests a minute or two each):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    OUT=docs/research/capped-baselines-b2star-1434
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/capped_baselines_b2star_1434.py walk --panel PUB.csv --window development --output WALK/development.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/capped_baselines_b2star_1434.py walk --panel PUB.csv --window 2026 --output WALK/2026.json
    PYTHONPATH=src python3 scripts/capped_baselines_b2star_1434.py score --walks WALK --output $OUT/result.json
    PYTHONPATH=src python3 scripts/capped_baselines_b2star_1434.py page --score $OUT/result.json --output docs/research/capped-baselines-b2star-1434-result.md

Stdlib only. No day after 2026-09-03 and no locked day is read.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import multiprocessing
import os
import random
import sys
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import capped_law as cl  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model import turn_days  # noqa: E402
from repo_model.data import exceeds_bp  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402

DECLARATION = REPO / "metadata" / "capped_baselines_b2star_1434.json"
RECORD_1314 = REPO / "docs" / "research" / "s3c-ann-net-1800-1314" / "announced-settlement-1800.json"
RECORD_1388 = REPO / "docs" / "research" / "b1-anchor-horizon-1388" / "result.json"
RECORD_1420 = REPO / "docs" / "research" / "b2-star-1420" / "result.json"
RECORD_1421 = REPO / "docs" / "research" / "capped-baselines-1421" / "result.json"
SEED = 1421
REPS = 2000
WINDOWS = ("development", "2026")
WINDOW_LAST = {"development": date(2025, 12, 31), "2026": EXPLORATORY_END}
LEADS = tuple(sp.HORIZONS)
MARGIN_BP = 0.0
MIN_GROUP_DAYS = 20
TAU = 5.0
METRICS = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)"}
CANDIDATE = "candidate"
#: model -> (the baseline whose raw quantiles it reads, capped).
BASES = ("B1p_star", "B2star")
MODELS: Dict[str, Tuple[str, bool]] = {
    CANDIDATE: (CANDIDATE, True),
    "B1p_star": ("B1p_star", False), "B1p_star_cap": ("B1p_star", True),
    "B2star": ("B2star", False), "B2star_cap": ("B2star", True),
}
LABELS = {
    CANDIDATE: "(s3c-ann-net)", "B1p_star": "B1'* (uncapped)", "B1p_star_cap": "B1'*-cap",
    "B2star": "B2* (uncapped)", "B2star_cap": "B2*-cap",
}
SHORT = {CANDIDATE: "(s3c-ann-net)", "B1p_star": "B1'*", "B1p_star_cap": "B1'*-cap", "B2star": "B2*", "B2star_cap": "B2*-cap"}
#: The group order of the splits shown.
GROUPS = ("pooled", "full_allotment")
_STATE: Dict = {}


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


# -- the arithmetic ------------------------------------------------------------------------------------------------------------


def model_cell(raw: Sequence[float], line: Optional[float], outcome: float, *, capped: bool, margin: float = MARGIN_BP) -> dict:
    """One model's scores on one cell, from its UNCAPPED 23 quantiles.

    A capped model is scored on the vector clipped at `line` (`capped_law.cap`) and reads its probability under rule (b) (`capped_law`, `open_tail`); an
    uncapped one on the vector as it is, with no line. Where there is no line the two are the same. The event is strict and on whole basis points.
    """

    use = line if capped else None
    vector = cl.cap(raw, use, margin)
    event = int(exceeds_bp(outcome, TAU))
    p = cl.exceedance(raw, use, TAU, "open_tail", margin)
    return {"vector": vector, "grid_crps": sp.grid_crps(vector, outcome), "upper_tail_twcrps": sp.upper_tail_twcrps(vector, outcome),
            "p5": p, "event5": event, "brier_gt5": (p - event) ** 2}


def share_explained(*, uncapped: float, capped: float, candidate: float) -> Optional[float]:
    """The part of the candidate's gain over the uncapped baseline that the cap alone buys: `(uncapped - capped) / (uncapped - candidate)`.

    Losses, lower is better. `None` where the candidate does not gain on the uncapped baseline (the denominator is not positive).
    """

    gain = uncapped - candidate
    if gain <= 0.0:
        return None
    return (uncapped - capped) / gain


def day_series(cells: Sequence[Mapping[str, object]], values: Sequence[Optional[float]], member: Callable[[Mapping[str, object]], bool]) -> Dict[date, float]:
    """The mean of `values` over the cells of each decision day that `member` admits (a value of `None` is no cell)."""

    total: Dict[date, float] = {}
    count: Dict[date, int] = {}
    for cell, value in zip(cells, values):
        if value is None or not member(cell):
            continue
        d = date.fromisoformat(str(cell["day"]))
        total[d] = total.get(d, 0.0) + value
        count[d] = count.get(d, 0) + 1
    return {d: total[d] / count[d] for d in total}


def share_interval(uncapped: Sequence[float], capped: Sequence[float], candidate: Sequence[float], *, reps: int = REPS, seed: int = SEED,
                   block: float = float(sp.BLOCK_LENGTH), level: float = 0.90) -> dict:
    """The share of the gain the cap buys, with its percentile interval over stationary bootstrap resamples of the days (in date order).

    Resamples whose candidate gain is not positive have no share and are dropped and counted. Raises `ValueError` if no resample keeps one.
    """

    n = len(uncapped)
    gain = [u - a for u, a in zip(uncapped, candidate)]
    cap = [u - c for u, c in zip(uncapped, capped)]
    rng = random.Random(seed)
    kept: List[float] = []
    for _ in range(reps):
        idx = stationary_bootstrap_indices(n, block, rng)
        g = sum(gain[i] for i in idx)
        if g > 0.0:
            kept.append(sum(cap[i] for i in idx) / g)
    if not kept:
        raise ValueError("no resample has a positive candidate gain")
    kept.sort()
    tail = (1.0 - level) / 2.0
    lo, hi = kept[int(tail * len(kept))], kept[min(len(kept) - 1, int((1.0 - tail) * len(kept)))]
    point = share_explained(uncapped=sum(uncapped) / n, capped=sum(capped) / n, candidate=sum(candidate) / n)
    return {"share": point, "interval": [lo, hi], "dropped_resamples": reps - len(kept), "resamples": reps}


# -- the walk ------------------------------------------------------------------------------------------------------------------


def baseline_forecasts(panel, index: int, settings: Mapping[str, object]) -> Dict[str, Dict[int, List[float]]]:
    """The two uncapped baselines at decision row `index`: B1'* and B2* (`b2_star_forecast`, not B2 as #1422 had it)."""

    from repo_model import protocol_benchmarks as pb

    return {"B1p_star": pb.b1_calendar_anchor_forecast(panel, index, **settings), "B2star": pb.b2_star_forecast(panel, index, **settings)}


def walk_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    m66 = _load("calibration_masking_candidate_1366", "calibration_masking_candidate_1366_in_1434")
    m = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1434")
    declared = m.s686.committed_declaration(DECLARATION)
    from repo_model import announced_iorb, decision_instant, policy_events, s3c_announced, s3c_candidate, spread_mr_calendar as cal
    from repo_model import protocol_benchmarks as pb
    from repo_model.baseline import panel_sha256
    from repo_model.evaluation_splits import load_split_declaration

    if decision_instant.DECISION_TIME.isoformat(timespec="minutes") != "18:00" or m.k.DECISION_TIME.isoformat(timespec="minutes") != "18:00":
        raise ValueError("this study is made at the 18:00 decision instant")
    window = args.window
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in m.load_daily_panel(panel_path) if row.date <= m.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/capped_baselines_b2star_1434")
    splits = load_split_declaration(m.c.SPLITS)
    registry = json.loads(m.c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(m.c.IORB_TABLE), decision_time=m.c.DECISION_TIME)
    auctions = m.m1273.load_auctions()
    results = m.load_results()
    frame, _notes, _mine, _cell_table, _groups = m.m1255.build(window, panel, splits, registry, table, register, args.first)
    days = m.candidate_days(frame, window, args.first)
    settings = dict(registry=registry, decision_time=m.k.DECISION_TIME, splits=splits)
    iorb = announced_iorb.load_announcements(m.c.IORB_TABLE)
    both = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=m.k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=m.k.DECISION_TIME)
    walk = m.sc.walk(panel, days, both, m.s3c_net.constant_states(panel), (s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM), sizes=net_table, **settings)
    raw = {d: walk.forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in frame.days}
    as_run = m.m1255.s3c_forecasts(frame, register, raw)

    baselines: Dict[str, Dict[date, Dict[int, List[float]]]] = {"B1p_star": {}, "B2star": {}}
    for d in frame.days:
        for name, forecast in baseline_forecasts(panel, frame.position[d], settings).items():
            baselines[name][d] = forecast

    cells, quantiles = [], {}
    base_quantiles: Dict[str, Dict[str, List[float]]] = {name: {} for name in baselines}
    for d in frame.days:
        index = frame.position[d]
        capped = {name: pb.capped_forecast(baselines[name][d], panel, index, register=register, decision_time=m.k.DECISION_TIME) for name in baselines}
        for h in LEADS:
            t = frame.target(d, h)
            if panel[index + h].date != t:
                raise ValueError(f"{d} lead {h}: the frame's target {t} is not the panel row {panel[index + h].date}")
            line = s3c_candidate.cap_line(register, m.k.decision_instant(d), t)
            key = f"{d.isoformat()}/{h}"
            if list(as_run[d][h]) != cl.cap(raw[d][h], line, MARGIN_BP):
                raise ValueError(f"{key}: the capped vector of repo_model.capped_law differs from the candidate's as run")
            for name in baselines:
                if capped[name][h] != cl.cap(baselines[name][d][h], line, MARGIN_BP):
                    raise ValueError(f"{key}: {name} is capped at a line other than the candidate's")
                base_quantiles[name][key] = list(baselines[name][d][h])
            cells.append({"key": key, "day": d.isoformat(), "lead": h, "target": t.isoformat(), "y": frame.outcome[t], "line": line,
                          "regime": frame.regime(t), "pressure": frame.day_type(t)})
            quantiles[key] = list(raw[d][h])
    m66.refuse_beyond([date.fromisoformat(c["target"]) for c in cells] + list(frame.days), WINDOW_LAST[window], where="capped_baselines_b2star_1434")
    doc = {"window": window, "instant": "18:00", "panel_sha256": sha, "declaration": declared["issue"], "decision_days": len(frame.days),
           "cells": cells, "uncapped_quantiles": quantiles, "baselines": base_quantiles}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: {window}, {len(frame.days)} decision days, {len(cells)} cells")
    return 0


# -- the score -----------------------------------------------------------------------------------------------------------------


def _pairs_task(job):
    key, reference, arm, ref_series, arm_series, days = job
    m = _STATE["m"]
    if all(ref_series[d] == arm_series[d] for d in days):
        return key, {"identical": True, "days": len(days)}
    return key, m.s761.run_pairs({reference: ref_series}, arm_series, days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[reference]


def _groups(cells: Sequence[dict]) -> List[Tuple[str, str, Callable[[Mapping[str, object]], bool]]]:
    out: List[Tuple[str, str, Callable]] = [
        ("pooled", "all cells", lambda c: True),
        ("full_allotment", "target days at full allotment", lambda c: c["line"] is not None),
    ]
    for label in sorted({c["regime"] for c in cells}):
        out.append(("regime", label, lambda c, label=label: c["regime"] == label))
    for label in sorted({c["pressure"] for c in cells}):
        out.append(("pressure_day_type", label, lambda c, label=label: c["pressure"] == label))
    return out


def comparisons() -> List[Tuple[str, str, str]]:
    """(comparison name, reference, arm): the arm is the one a positive mean d favours."""

    out = [(f"cand_vs:{name}", name, CANDIDATE) for name in MODELS if name != CANDIDATE]
    out += [(f"cap_vs:{base}", base, f"{base}_cap") for base in BASES]
    return out


def reproduce(window: str, means: Mapping[str, float]) -> dict:
    """The pooled mean grid CRPS against what is already on main, to 1e-9: the candidate (record 1314), the uncapped B1'* (result 1388), B2* (result 1420), and
    the candidate, B1'* and B1'*-cap again against #1422's result, which this run must leave unchanged."""

    theirs = json.loads(RECORD_1314.read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]
    other = json.loads(RECORD_1388.read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]
    star = json.loads(RECORD_1420.read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]
    prior = json.loads(RECORD_1421.read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all cells"]["metrics"]["grid_crps"]["means"]
    pairs = {CANDIDATE: ("record 1314", theirs["sc_s3c_ann_net"]), "B1p_star": ("result 1388", other["B1_prime_star"]), "B2star": ("result 1420", star["B2_star"]),
             "B1p_star_cap": ("result 1421", prior["B1p_star_cap"])}
    out = {}
    for name, (where, want) in pairs.items():
        out[name] = {"here": means[name], "there": want, "source": where}
        if abs(means[name] - want) > 1e-9:
            raise ValueError(f"{window}: the mean grid CRPS of {name} is {means[name]!r} here and {want!r} in the {where}")
    for name in (CANDIDATE, "B1p_star"):
        if abs(means[name] - prior[name]) > 1e-9:
            raise ValueError(f"{window}: the mean grid CRPS of {name} is {means[name]!r} here and {prior[name]!r} in result 1421")
    return out


def stand_in_of_1422(window: str) -> dict:
    """The pooled mean losses of plain B2 and of B2-cap (the stand-in of #1422), copied from its result, so the page can set them beside B2*-cap."""

    group = json.loads(RECORD_1421.read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all cells"]["metrics"]
    return {model: {metric: group[metric]["means"][model] for metric in METRICS} for model in ("B2", "B2_cap")}


def window_result(doc: Mapping[str, object], draws: int, workers: int) -> dict:
    cells: List[dict] = doc["cells"]
    name = doc["window"]
    scored: Dict[str, List[dict]] = {}
    for model, (source, capped) in MODELS.items():
        pool = doc["uncapped_quantiles"] if model == CANDIDATE else doc["baselines"][source]
        scored[model] = [model_cell(pool[c["key"]], c["line"], c["y"], capped=capped) for c in cells]
    means = {model: sum(s["grid_crps"] for s in rows) / len(rows) for model, rows in scored.items()}
    repro = reproduce(name, means)
    binds = {model: sum(1 for c, s in zip(cells, scored[model]) if c["line"] is not None and (doc["uncapped_quantiles"] if model == CANDIDATE else doc["baselines"][MODELS[model][0]])[c["key"]][-1] > c["line"])
             for model in MODELS}
    result: dict = {
        "decision_days": doc["decision_days"], "cells": len(cells), "cells_at_full_allotment": sum(1 for c in cells if c["line"] is not None),
        "cells_where_the_cap_binds_at_q99": binds, "reproduction": repro, "groups": {}, "share_explained": {},
        "stand_in_1422": stand_in_of_1422(name),
    }
    series: Dict[Tuple[str, str, str], Dict[str, Dict[date, float]]] = {}
    jobs = []
    for split, label, member in _groups(cells):
        entry = {"cells": sum(1 for c in cells if member(c)), "metrics": {}}
        for metric in METRICS:
            per_model = {model: day_series(cells, [s[metric] for s in scored[model]], member) for model in MODELS}
            days = sorted(per_model[CANDIDATE])
            if any(sorted(per_model[x]) != days for x in MODELS):
                raise ValueError("the models are not scored on the same days")
            if not days:
                continue
            series[(split, label, metric)] = per_model
            entry["metrics"][metric] = {"days": len(days), "means": {x: sum(per_model[x][d] for d in days) / len(days) for x in MODELS}, "vs": {}}
            if len(days) < MIN_GROUP_DAYS:
                entry["metrics"][metric]["not_tested"] = f"fewer than {MIN_GROUP_DAYS} decision days"
                continue
            for comp, reference, arm in comparisons():
                jobs.append(((split, label, metric, comp), reference, arm, per_model[reference], per_model[arm], days))
        result["groups"].setdefault(split, {})[label] = entry
    _STATE["draws"] = draws
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        for (split, label, metric, comp), row in pool.map(_pairs_task, jobs, chunksize=1):
            result["groups"][split][label]["metrics"][metric]["vs"][comp] = row

    for split, label in (("pooled", "all cells"), ("full_allotment", "target days at full allotment")):
        for base in BASES:
            for metric in METRICS:
                per_model = series.get((split, label, metric))
                entry = result["groups"][split][label]["metrics"].get(metric)
                if per_model is None or entry is None:
                    continue
                days = sorted(per_model[CANDIDATE])
                u, cp, ca = ([per_model[x][d] for d in days] for x in (base, f"{base}_cap", CANDIDATE))
                row = {"days": len(days), "uncapped": sum(u) / len(u), "capped": sum(cp) / len(cp), "candidate": sum(ca) / len(ca)}
                tested = entry["vs"].get(f"cand_vs:{base}")
                if tested is None or tested.get("identical") or "difference_interval" not in tested:
                    row["not_defined"] = "the candidate's gain over the uncapped baseline was not tested"
                elif not tested["difference_interval"][0] > 0:
                    row["not_defined"] = "the candidate's gain over the uncapped baseline is not distinguished from zero"
                else:
                    row.update(share_interval(u, cp, ca))
                result["share_explained"].setdefault(f"{split}/{label}", {}).setdefault(base, {})[metric] = row
    return result


def score_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    m = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1434")
    declared = m.s686.committed_declaration(DECLARATION)
    _STATE["m"] = m
    result: dict = {"issue": 1440, "study_of": 1421, "finding": 1434, "declaration": "metadata/capped_baselines_b2star_1434.json", "label": "development, not a verdict", "windows": {},
                    "walk_files": {}, "amendments": declared["amendments"], "draws": args.draws, "seed": SEED, "reps": REPS,
                    "models": {k: list(v) for k, v in MODELS.items()}, "supersedes": "docs/research/capped-baselines-1421-result.md (#1422): its B2-cap rows used plain B2 in B2*'s place"}
    for name in WINDOWS:
        path = Path(args.walks) / f"{name}.json"
        if not path.exists():
            continue
        raw = path.read_bytes()
        doc = json.loads(raw)
        if result.get("panel_sha256") not in (None, doc["panel_sha256"]):
            raise ValueError("the walk files were made from different panels")
        result["panel_sha256"] = doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": hashlib.sha256(raw).hexdigest()}
        result["windows"][name] = window_result(doc, args.draws, args.workers)
    if not result["windows"]:
        raise SystemExit(f"no walk file in {args.walks}")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk", help="walk the candidate, compute the baselines, and write the uncapped quantiles of every cell")
    w.add_argument("--panel", required=True)
    w.add_argument("--window", choices=WINDOWS, required=True)
    w.add_argument("--output", required=True)
    w.add_argument("--first", type=date.fromisoformat, default=None, help="first decision day (for a short trial)")
    s = sub.add_parser("score", help="score the models on the walks")
    s.add_argument("--walks", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--workers", type=int, default=4)
    g = sub.add_parser("page", help="write the page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if args.command == "walk":
        return walk_command(args)
    if args.command == "score":
        return score_command(args)
    return page_command(args)


# -- the page ------------------------------------------------------------------------------------------------------------------

WINDOW_TITLES = {
    "development": "Development window (targets up to 2025-12-31; this window decides what the page reads)",
    "2026": "2026 days (targets 2026-01-02 to 2026-09-03; full allotment on every target), shown apart",
}


def _reading(row: Optional[dict]) -> str:
    if row is None:
        return "not tested"
    if row.get("identical"):
        return "identical"
    if "undefined" in row:
        return "undefined"
    lo, hi = row["difference_interval"]
    return "gain" if lo > 0 else "loss" if hi < 0 else "undecided"


def _diff(row: Optional[dict], digits: int = 4, sci: bool = False) -> str:
    """Mean d (benchmark less arm; positive favours the arm) with its 90% interval, and the reading. `sci`: scientific notation, for tiny differences."""

    if row is None:
        return "not tested"
    if row.get("identical"):
        return "identical"
    if "undefined" in row:
        return "undefined"
    lo, hi = row["difference_interval"]
    mark = " †" if row.get("dropped_resamples") else ""
    f = f"+.{digits}e" if sci else f"+.{digits}f"
    return f"{format(row['difference'], f)} [{format(lo, f)}, {format(hi, f)}]: {_reading(row)}{mark}"


def _mean(x: Optional[float], metric: str) -> str:
    return "n/a" if x is None else f"{x:.{4 if metric == 'brier_gt5' else 3}f}"


def means_table(w: Mapping[str, object], split: str, label: str) -> List[str]:
    g = w["groups"].get(split, {}).get(label)
    if g is None:
        return []
    out = ["| model | " + " | ".join(METRIC_TITLES[m] for m in METRICS) + " |", "|---|---|---|---|"]
    for model in MODELS:
        out.append(f"| {LABELS[model]} | " + " | ".join(_mean(g["metrics"][m]["means"][model], m) if m in g["metrics"] else "n/a" for m in METRICS) + " |")
    return out


def vs_table(w: Mapping[str, object], split: str, label: str, wanted: Sequence[Tuple[str, str]]) -> List[str]:
    g = w["groups"].get(split, {}).get(label)
    if g is None:
        return []
    out = ["| comparison | " + " | ".join(METRIC_TITLES[m] for m in METRICS) + " |", "|---|---|---|---|"]
    for comp, title in wanted:
        cells = []
        for m in METRICS:
            x = g["metrics"].get(m)
            tiny = comp.startswith("cap_vs:")
            cells.append("n/a" if x is None else x["not_tested"] if "not_tested" in x
                         else _diff(x["vs"].get(comp), 2 if tiny and m == "brier_gt5" else 4 if tiny or m == "brier_gt5" else 3, sci=tiny and m == "brier_gt5"))
        out.append(f"| {title} | " + " | ".join(cells) + " |")
    return out


CAND_VS = [(f"cand_vs:{n}", f"(s3c-ann-net) against {SHORT[n]}") for n in ("B1p_star_cap", "B1p_star", "B2star_cap", "B2star")]
CAP_VS = [(f"cap_vs:{b}", f"{SHORT[b]}-cap against {SHORT[b]} (what the cap alone buys)") for b in BASES]


def split_table(w: Mapping[str, object], split: str, comp: str, metric: str) -> List[str]:
    labels = w["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | decision days | " + SHORT.get(comp.split(':')[1], comp) + " |", "|---|---|---|"]
    for label in sorted(labels):
        x = labels[label]["metrics"].get(metric)
        if x is None:
            continue
        out.append(f"| {label} | {x['days']} | " + ("not tested" if "not_tested" in x else _diff(x["vs"].get(comp), 4 if metric == "brier_gt5" else 3)) + " |")
    return out if len(out) > 2 else []


def share_table(w: Mapping[str, object]) -> List[str]:
    out = ["| group | baseline | metric | uncapped | capped | candidate | share of the gain the cap alone buys [90% interval] |", "|---|---|---|---|---|---|---|"]
    same = w["groups"]["full_allotment"]["target days at full allotment"]["cells"] == w["cells"]
    for group, bases in w["share_explained"].items():
        if same and group.startswith("full_allotment/"):
            continue
        for base, metrics in bases.items():
            for metric, row in metrics.items():
                if "not_defined" in row:
                    text = f"not defined: {row['not_defined']}"
                else:
                    lo, hi = row["interval"]
                    text = f"{row['share']:.3f} [{lo:.3f}, {hi:.3f}]" + (f" ({row['dropped_resamples']} resample(s) without a gain dropped)" if row["dropped_resamples"] else "")
                out.append(f"| {group.split('/')[1]} | {SHORT[base]} | {METRIC_TITLES[metric]} | {_mean(row['uncapped'], metric)} | {_mean(row['capped'], metric)} | "
                           f"{_mean(row['candidate'], metric)} | {text} |")
    return out


def render(r: dict) -> str:
    L: List[str] = []
    add = L.append
    add("# The simple baselines with the candidate's SRF cap, with B2*-cap proper: B1'*-cap and B2*-cap (#1440, the finding of #1434)")
    add("")
    add("**Development data, not a verdict.** Hypothesis H5 (primary goal), registration design (benchmarks), step 3. The candidate, (s3c-ann-net), is "
        "capped at the Standing Repo Facility line on target days at full allotment. A baseline left uncapped could make part of the candidate's gain a "
        "mechanical truncation at that line. This page gives the baselines the candidate's own cap (the same line, read from `metadata/policy_events.json` as "
        "public at the decision instant, margin 0 bp) and the candidate's probability rule (b) (`capped_law`, `open_tail`), and scores them beside the uncapped "
        f"versions. This is the study of #1421 re-run, the same scores, days, intervals and splits, with B2* in the place plain B2 held on #1422's page. Panel digest `{r['panel_sha256']}`; walked at the 18:00 decision instant; seed {r['seed']}, {r['draws']} draws.")
    add("")
    add("**Which version is confirmatory is ruled, not open** (Eleonora, 3 November 2026, comment on #1421): the capped baselines are the confirmatory "
        "benchmarks and the uncapped versions are reported beside them. This page does not reopen it.")
    add("")
    add("**This page supersedes the B2-cap rows of [#1422's page](capped-baselines-1421-result.md).** That page capped plain B2 in B2\\*'s place, because B2\\* "
        "(#1420) was thought not to be on main; it was (#1423). Here B2\\* is `protocol_benchmarks.b2_star_forecast` and B2\\*-cap is `b2_star_capped_forecast`. "
        "#1422's page is not edited; its B1'\\*-cap rows are unchanged and reproduce here to 1e-9. Plain B2 and the stand-in B2-cap are copied from its result "
        "beside B2\\*-cap in the pooled mean-loss table, labelled as such.")
    add("")
    add("The grid CRPS, the upper-tail twCRPS and the Brier score are losses (lower is better). \"Mean d\" is the reference's loss less the arm's, so a positive "
        "value favours the arm; the interval is scoring protocol v1's studentized stationary bootstrap on decision-day means, read on the bound on mean d (her ruling "
        "on #1009) as `gain`, `loss` or `undecided` from whether it excludes zero. † marks a bound taken from the resamples that have a long-run variance (#1239). "
        f"A group of fewer than {MIN_GROUP_DAYS} decision days is not tested. The pooled mean grid CRPS of the candidate reproduces #1314's record, "
        "that of B1'* #1388's result, that of B2* #1420's result, and the candidate, B1'* and B1'*-cap #1422's result, to 1e-9 in both windows (the study refuses to "
        "write otherwise).")
    add("")
    for name, w in r["windows"].items():
        add(f"## {WINDOW_TITLES[name]}")
        add("")
        b = w["cells_where_the_cap_binds_at_q99"]
        add(f"{w['decision_days']} decision days, {w['cells']} cells, {w['cells_at_full_allotment']} of them at full allotment. Cells at full allotment where the "
            "model's uncapped q99 is above the line, so that the cap changes at least one quantile: "
            + ", ".join(f"{SHORT[m]} {b[m]}" for m in ("B1p_star", "B2star")) + f"; the candidate's own uncapped vector, {b[CANDIDATE]}.")
        add("")
        add("**Mean losses, pooled (all cells)**")
        add("")
        L.extend(means_table(w, "pooled", "all cells"))
        L.extend(f"| {title} (from #1422's result) | " + " | ".join(_mean(w["stand_in_1422"][key][m], m) for m in METRICS) + " |"
                 for key, title in (("B2", "B2 (plain; the stand-in)"), ("B2_cap", "B2-cap (plain B2 capped; the stand-in of #1422)")))
        add("")
        add("**The candidate against each baseline, pooled** (mean d: baseline less candidate; positive favours the candidate)")
        add("")
        L.extend(vs_table(w, "pooled", "all cells", CAND_VS))
        add("")
        add("**What the cap alone buys, pooled** (mean d: uncapped baseline less capped baseline; positive favours the cap)")
        add("")
        L.extend(vs_table(w, "pooled", "all cells", CAP_VS))
        add("")
        same = w["groups"]["full_allotment"]["target days at full allotment"]["cells"] == w["cells"]
        if same:
            add("Every target of this window is at full allotment, so the group \"target days at full allotment\" is the pooled group and its tables are not repeated.")
            add("")
        else:
            add("**Mean losses, target days at full allotment**")
            add("")
            L.extend(means_table(w, "full_allotment", "target days at full allotment"))
            add("")
            add("**The candidate against each baseline, target days at full allotment**")
            add("")
            L.extend(vs_table(w, "full_allotment", "target days at full allotment", CAND_VS))
            add("")
            add("**What the cap alone buys, target days at full allotment**")
            add("")
            L.extend(vs_table(w, "full_allotment", "target days at full allotment", CAP_VS))
            add("")
        add("**The share of the candidate's gain over the uncapped baseline that the cap alone buys** "
            "(uncapped less capped, over uncapped less candidate; defined only where the candidate's gain over the uncapped baseline excludes zero on the positive side; "
            "interval: percentile, stationary bootstrap of the decision days)")
        add("")
        L.extend(share_table(w))
        add("")
        for metric in METRICS:
            for comp, title in (("cand_vs:B1p_star_cap", "against B1'*-cap"), ("cand_vs:B2star_cap", "against B2*-cap")):
                for split in ("regime", "pressure_day_type"):
                    t = split_table(w, split, comp, metric)
                    if t:
                        add(f"**{METRIC_TITLES[metric]}: (s3c-ann-net) {title}, by {split.replace('_', ' ')} of the target day**")
                        add("")
                        L.extend(t)
                        add("")
    add("## What it shows, and what it does not")
    add("")
    L.extend(conclusions(r))
    add("")
    add("## Ruled, and what stays open")
    add("")
    add("- **Ruled** (3 November 2026): the capped versions are the confirmatory benchmarks, the uncapped versions are reported beside them. "
        "`protocol_benchmarks` carries `capped_forecast`, `capped_exceedance`, `b1_calendar_anchor_capped_forecast` and, since #1440, `b2_star_capped_forecast`; "
        "the stand-in `b2_capped_forecast` is gone.")
    add("- **Not done:** any change to the scoring protocol's text, to #1394 or to the confirmation design; no benchmark is adopted, the candidate stays frozen, "
        "and no verdict is given. Walked at the 18:00 instant only.")
    add("")
    return "\n".join(L) + "\n"


def against_b2star_cap(r: dict) -> str:
    """The plain statement of the issue: the candidate against B2*-cap, on twCRPS and Brier, pooled, in each window: the means, the paired difference and its reading."""

    parts = []
    for name, w in r["windows"].items():
        g = w["groups"]["pooled"]["all cells"]["metrics"]
        sentences = []
        for metric in ("upper_tail_twcrps", "brier_gt5"):
            x = g[metric]
            row = x["vs"].get("cand_vs:B2star_cap")
            sentences.append(f"{METRIC_TITLES[metric]}: candidate {_mean(x['means'][CANDIDATE], metric)}, B2*-cap {_mean(x['means']['B2star_cap'], metric)}, "
                             f"paired difference (B2*-cap less candidate) {_diff(row, 4)}")
        parts.append(f"{name}: " + "; ".join(sentences))
    return ("- **Against B2\\*-cap, pooled, upper-tail twCRPS and Brier P(> +5 bp)** (a loss is lower-is-better; a positive difference favours the candidate): "
            + ". ".join(parts) + ". Where the reading is `loss` or `undecided`, the candidate does not beat the confirmatory benchmark on that measure there.")


def conclusions(r: dict) -> List[str]:
    """The bullets, read from the result: nothing here is typed from a number."""

    out: List[str] = []
    dev = r["windows"].get("development")
    for name, w in r["windows"].items():
        g = w["groups"]["pooled"]["all cells"]["metrics"]
        parts = []
        for metric in METRICS:
            reads = {n: _reading(g[metric]["vs"].get(f"cand_vs:{n}")) for n in ("B1p_star_cap", "B2star_cap")}
            parts.append(f"{METRIC_TITLES[metric]}: " + ", ".join(f"{reads[n]} against {SHORT[n]}" for n in reads))
        out.append(f"- **{name}, pooled, the candidate against the capped baselines:** " + "; ".join(parts) + ".")
        caps = []
        for metric in METRICS:
            caps.append(f"{METRIC_TITLES[metric]}: " + ", ".join(f"{_reading(g[metric]['vs'].get(f'cap_vs:{b}'))} for {SHORT[b]}" for b in BASES))
        out.append(f"- **{name}, pooled, what the cap alone buys the baselines:** " + "; ".join(caps) + ".")
        fa = w["groups"]["full_allotment"]["target days at full allotment"]["metrics"]["grid_crps"]
        if "not_tested" in fa:
            out.append(f"- **{name}, target days at full allotment:** {fa['days']} decision days, so the comparisons are not tested ({fa['not_tested']}); the means are in the table.")
        shares = w["share_explained"].get("pooled/all cells", {})
        defined = [(b, m, row) for b, ms in shares.items() for m, row in ms.items() if "not_defined" not in row]
        if defined:
            out.append(f"- **{name}, pooled, the share of the candidate's gain the cap alone buys:** " + "; ".join(
                f"{SHORT[b]}, {METRIC_TITLES[m]}: {row['share']:.3f} [{row['interval'][0]:.3f}, {row['interval'][1]:.3f}]" for b, m, row in defined) + ".")
        else:
            out.append(f"- **{name}, pooled, the share of the candidate's gain the cap alone buys:** not defined for any baseline or metric (the candidate's gain "
                       "over the uncapped baseline is not distinguished from zero, or is not positive).")
    out.append(against_b2star_cap(r))
    out.append("- A development figure is paired, carries an interval and is split by regime and by pressure-day type; a pooled figure alone is not a result. "
               "The development window decides what this page reads; the 2026 days have been seen by earlier studies and are shown apart.")
    out.append("- Lens C's caveat: the lag-10 HAC standard error is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be.")
    out.append("- Nothing is registered, published or adopted here. The cap is a transform of the baselines' quantiles; no model was fitted or tuned.")
    return out


def page_command(args) -> int:
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
