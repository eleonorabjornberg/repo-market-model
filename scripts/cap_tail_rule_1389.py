"""One coherent rule for the SRF cap, the tail completion and the probabilities: the candidate's emitted law, three readings (#1389; H5, registration design).

A development study, never a verdict. `repo_model.spread_mean_reversion.exceedance` reads the candidate's capped quantiles with the linear law between
them, run on at the outer segments' slopes. Where the cap binds that law is not one distribution (`docs/research/cap-tail-rule-1389-design.md`). This
study walks the candidate (s3c-ann-net) as #1288 and #1314 did, keeps each cell's uncapped quantiles and its line, and reads them three ways
(`repo_model.capped_law`, each behind its `rule` flag, the default being the published reading): the status quo; (a) a bounded law with an atom
at the line; (b) the capped percentiles with an unbounded completion. Every choice is in `metadata/cap_tail_rule_1389.json`, which `walk` and `score`
refuse to read unless it is committed and unchanged.

The grid CRPS (primary) and the upper-tail twCRPS (key secondary) read the quantile vector, which is the capped vector under every rule: they are
the same by construction and the study checks that each rule's law has the capped vector as its quantiles. The rules differ in P(> tau): the Brier
scores of P(> +5 bp), P(> +10 bp) and P(> line), the line exceedances (outcomes above the line against the sum of the predicted probabilities) and
the randomized PIT, pooled, on the cells at full allotment, on the cells where the cap binds, by regime and by pressure-day type, on the development
window and, apart, on the 2026 days.

Commands (a cloud run; each walk is minutes, the paired tests a minute each):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    OUT=docs/research/cap-tail-rule-1389
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/cap_tail_rule_1389.py walk --panel PUB.csv --window development --output WALK/development.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/cap_tail_rule_1389.py walk --panel PUB.csv --window 2026 --output WALK/2026.json
    PYTHONPATH=src python3 scripts/cap_tail_rule_1389.py score --walks WALK --output $OUT/result.json
    PYTHONPATH=src python3 scripts/cap_tail_rule_1389.py page --score $OUT/result.json --output docs/research/cap-tail-rule-1389-result.md

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
from repo_model.data import exceeds_bp  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

DECLARATION = REPO / "metadata" / "cap_tail_rule_1389.json"
RECORD_1314 = REPO / "docs" / "research" / "s3c-ann-net-1800-1314" / "announced-settlement-1800.json"
SEED = 1389
WINDOWS = ("development", "2026")
WINDOW_LAST = {"development": date(2025, 12, 31), "2026": EXPLORATORY_END}
LEADS = tuple(sp.HORIZONS)
RULES = cl.RULES
OPTIONS = ("atom_at_line", "open_tail")
MARGIN_BP = 0.0
MIN_GROUP_DAYS = 20
METRICS = ("brier5", "brier10", "brier_line")
CLASSES = ("0", "1", "2-3", "4+")
LABELS = {"status_quo": "status quo (the candidate as run)", "atom_at_line": "(a) bounded, atom at the line", "open_tail": "(b) capped percentiles, open tail"}
METRIC_TITLES = {"brier5": "Brier P(> +5 bp)", "brier10": "Brier P(> +10 bp)", "brier_line": "Brier P(> line)"}
_STATE: Dict = {}


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


# -- the arithmetic ------------------------------------------------------------------------------------------------------------


def binding_count(raw: Sequence[float], line: Optional[float], margin: float = MARGIN_BP) -> int:
    """The number of upper levels the cap changes: those whose uncapped quantile is above the ceiling (`line + margin`); 0 with no line."""

    if line is None:
        return 0
    ceiling = line + margin
    return sum(1 for v in raw if v > ceiling)


def binding_class(count: int) -> str:
    """The class of a binding count: `0`, `1`, `2-3` or `4+`."""

    return "0" if count == 0 else "1" if count == 1 else "2-3" if count <= 3 else "4+"


def cell_scores(raw: Sequence[float], line: Optional[float], outcome: float, margin: float = MARGIN_BP) -> Dict[str, dict]:
    """For each rule, the probabilities of the events above +5 bp, above +10 bp and above the line, the events (whole basis points, strict,
    `data.exceeds_bp`), the Brier cells (the line's only where there is a line) and the PIT interval of the outcome."""

    event5, event10 = int(exceeds_bp(outcome, 5.0)), int(exceeds_bp(outcome, 10.0))
    line_event = None if line is None else int(exceeds_bp(outcome, line))
    out: Dict[str, dict] = {}
    for rule in RULES:
        p5 = cl.exceedance(raw, line, 5.0, rule, margin)
        p10 = cl.exceedance(raw, line, 10.0, rule, margin)
        p_line = None if line is None else cl.exceedance(raw, line, line, rule, margin)
        law = cl.emitted_law(raw, line, rule, margin)
        out[rule] = {
            "p5": p5, "p10": p10, "p_line": p_line, "event5": event5, "event10": event10, "line_event": line_event,
            "brier5": (p5 - event5) ** 2, "brier10": (p10 - event10) ** 2,
            "brier_line": None if line is None else (p_line - line_event) ** 2,
            "pit": cl.pit_interval(law, outcome),
        }
    return out


def check_quantiles(raw: Sequence[float], line: Optional[float], margin: float = MARGIN_BP, tolerance: float = 1e-4,
                    laws: Optional[Mapping[str, cl.PiecewiseLaw]] = None) -> None:
    """Every rule's law has the capped vector as its quantiles at the 23 levels (the status quo's nudge is under 3e-5 bp).

    Raises:
        ValueError: a rule's law has a different quantile.
    """

    capped = cl.cap(raw, line, margin)
    laws = dict(laws) if laws is not None else {rule: cl.emitted_law(raw, line, rule, margin) for rule in RULES}
    for rule, law in laws.items():
        for level, want in zip(sp.GRID, capped):
            got = law.quantile(level)
            if abs(got - want) > tolerance:
                raise ValueError(f"{rule}: the law's {level} quantile is {got}, the capped vector's is {want}")


def tail_extent(raw: Sequence[float], line: Optional[float], rule: str, margin: float = MARGIN_BP) -> float:
    """How far above the line (bp) the law of `rule` runs on: its upper end less the ceiling, never below 0. Zero for a bounded law."""

    if line is None:
        return 0.0
    return max(0.0, cl.emitted_law(raw, line, rule, margin).quantile(1.0) - (line + margin))


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


def decile_counts(pits: Sequence[float]) -> List[int]:
    """How many PIT values fall in each tenth of [0, 1] (1.0 in the last)."""

    counts = [0] * 10
    for p in pits:
        counts[min(9, int(p * 10))] += 1
    return counts


# -- the walk ------------------------------------------------------------------------------------------------------------------


def walk_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    m66 = _load("calibration_masking_candidate_1366", "calibration_masking_candidate_1366_in_1389")
    declared = m66.committed_declaration(DECLARATION)
    from repo_model import announced_iorb, decision_instant, policy_events, s3c_announced, s3c_candidate, spread_mr_calendar as cal
    from repo_model.baseline import panel_sha256
    from repo_model.evaluation_splits import load_split_declaration

    m = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1389")
    if decision_instant.DECISION_TIME.isoformat(timespec="minutes") != "18:00" or m.k.DECISION_TIME.isoformat(timespec="minutes") != "18:00":
        raise ValueError("this study is made at the 18:00 decision instant")
    window = args.window
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in m.load_daily_panel(panel_path) if row.date <= m.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/cap_tail_rule_1389")
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

    cells, quantiles = [], {}
    for d in frame.days:
        for h in LEADS:
            t = frame.target(d, h)
            line = s3c_candidate.cap_line(register, m.k.decision_instant(d), t)
            key = f"{d.isoformat()}/{h}"
            if list(as_run[d][h]) != cl.cap(raw[d][h], line, MARGIN_BP):
                raise ValueError(f"{key}: the capped vector of repo_model.capped_law differs from the candidate's as run")
            cells.append({"key": key, "day": d.isoformat(), "lead": h, "target": t.isoformat(), "y": frame.outcome[t], "line": line,
                          "regime": frame.regime(t), "pressure": frame.day_type(t)})
            quantiles[key] = list(raw[d][h])
    m66.refuse_beyond([date.fromisoformat(c["target"]) for c in cells] + list(frame.days), WINDOW_LAST[window], where="cap_tail_rule_1389")
    doc = {"window": window, "instant": "18:00", "panel_sha256": sha, "declaration": declared["issue"], "decision_days": len(frame.days),
           "cells": cells, "uncapped_quantiles": quantiles}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: {window}, {len(frame.days)} decision days, {len(cells)} cells")
    return 0


# -- the score -----------------------------------------------------------------------------------------------------------------


def _pairs_task(job):
    key, reference, option, ref_series, opt_series, days = job
    m = _STATE["m"]
    if all(ref_series[d] == opt_series[d] for d in days):
        return key, {"identical": True, "days": len(days)}
    row = m.s761.run_pairs({reference: ref_series}, opt_series, days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[reference]
    return key, row


def _groups(cells: Sequence[dict], counts: Sequence[int]) -> List[Tuple[str, str, Callable[[Mapping[str, object]], bool]]]:
    by_key = {c["key"]: n for c, n in zip(cells, counts)}
    out: List[Tuple[str, str, Callable]] = [
        ("pooled", "all cells", lambda c: True),
        ("full_allotment", "target days at full allotment", lambda c: c["line"] is not None),
        ("cap_binds", "the cap binds (the uncapped q99 is above the line)", lambda c: by_key[c["key"]] > 0),
    ]
    for label in sorted({c["regime"] for c in cells}):
        out.append(("regime", label, lambda c, label=label: c["regime"] == label))
    for label in sorted({c["pressure"] for c in cells}):
        out.append(("pressure_day_type", label, lambda c, label=label: c["pressure"] == label))
    return out


def window_result(doc: Mapping[str, object], record: Mapping[str, object], draws: int, workers: int) -> dict:
    cells: List[dict] = doc["cells"]
    raw = doc["uncapped_quantiles"]
    counts = [binding_count(raw[c["key"]], c["line"]) for c in cells]
    rng = random.Random(SEED)
    scored = []
    for c in cells:
        row = cell_scores(raw[c["key"]], c["line"], c["y"])
        check_quantiles(raw[c["key"]], c["line"])
        for rule in RULES:
            lo, hi = row[rule]["pit"]
            row[rule]["pit_value"] = lo + rng.random() * (hi - lo)
        scored.append(row)
    capped = [cl.cap(raw[c["key"]], c["line"], MARGIN_BP) for c in cells]
    grid = [sp.grid_crps(q, c["y"]) for q, c in zip(capped, cells)]
    twc = [sp.upper_tail_twcrps(q, c["y"]) for q, c in zip(capped, cells)]
    name = doc["window"]
    theirs = record["windows"][name]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]["sc_s3c_ann_net"]
    theirs = theirs["mean"] if isinstance(theirs, dict) else theirs
    mine = sum(grid) / len(grid)
    if abs(mine - theirs) > 1e-9:
        raise ValueError(f"{name}: the mean grid CRPS of the capped vector is {mine!r} here and {theirs!r} in the 1314 record")

    groups = _groups(cells, counts)
    series: Dict[Tuple[str, str, str, str], Dict[date, float]] = {}
    result: dict = {
        "decision_days": doc["decision_days"], "cells": len(cells), "cells_at_full_allotment": sum(1 for c in cells if c["line"] is not None),
        "cells_where_the_cap_binds": sum(1 for n in counts if n > 0),
        "reproduction": {"mean_grid_crps": mine, "record_1314": theirs},
        "grid_scores": {"mean_grid_crps": mine, "mean_upper_tail_twcrps": sum(twc) / len(twc),
                        "identical_under_every_rule": True},
        "groups": {},
    }
    jobs = []
    for split, label, member in groups:
        entry = {"cells": sum(1 for c in cells if member(c)), "metrics": {}}
        members = [c for c in cells if member(c)]
        entry["grid_crps_mean"] = sum(g for g, c in zip(grid, cells) if member(c)) / max(1, len(members))
        entry["twcrps_mean"] = sum(g for g, c in zip(twc, cells) if member(c)) / max(1, len(members))
        for metric in METRICS:
            per_rule = {rule: day_series(cells, [s[rule][metric] for s in scored], member) for rule in RULES}
            days = sorted(per_rule["status_quo"])
            if any(sorted(per_rule[r]) != days for r in RULES):
                raise ValueError("the rules are not scored on the same days")
            if not days:
                continue
            entry["metrics"][metric] = {"days": len(days), "means": {r: sum(per_rule[r][d] for d in days) / len(days) for r in RULES}, "vs": {}}
            if len(days) < MIN_GROUP_DAYS:
                entry["metrics"][metric]["not_tested"] = f"fewer than {MIN_GROUP_DAYS} decision days"
                continue
            for option in OPTIONS:
                jobs.append(((split, label, metric, option), "status_quo", option, per_rule["status_quo"], per_rule[option], days))
        result["groups"].setdefault(split, {})[label] = entry
    _STATE["draws"] = draws
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        for (split, label, metric, option), row in pool.map(_pairs_task, jobs, chunksize=1):
            result["groups"][split][label]["metrics"][metric]["vs"][option] = row

    def tally(member, tau_key, event_key):
        rows = [(s, c) for s, c in zip(scored, cells) if member(c) and s["status_quo"][event_key] is not None]
        return {"cells": len(rows), "observed": sum(s["status_quo"][event_key] for s, _ in rows),
                "predicted": {r: sum(s[r][tau_key] for s, _ in rows) for r in RULES}}

    result["exceedances"] = {
        "above_5_bp": {label: tally(member, "p5", "event5") for label, member in (("all cells", lambda c: True), ("at full allotment", lambda c: c["line"] is not None))},
        "above_10_bp": {label: tally(member, "p10", "event10") for label, member in (("all cells", lambda c: True), ("at full allotment", lambda c: c["line"] is not None))},
        "above_the_line": {label: tally(member, "p_line", "line_event")
                           for label, member in (("at full allotment", lambda c: c["line"] is not None), ("the cap binds", lambda c: c["line"] is not None))},
    }
    bound = {c["key"]: n for c, n in zip(cells, counts)}
    result["exceedances"]["above_the_line"]["the cap binds"] = tally(lambda c: bound[c["key"]] > 0, "p_line", "line_event")
    classes = {}
    for cls in CLASSES:
        rows = [(s, c) for s, c in zip(scored, cells) if c["line"] is not None and binding_class(bound[c["key"]]) == cls]
        if not rows:
            continue
        classes[cls] = {"cells": len(rows), "observed_above_10": sum(s["status_quo"]["event10"] for s, _ in rows) / len(rows),
                        "mean_p10": {r: sum(s[r]["p10"] for s, _ in rows) / len(rows) for r in RULES},
                        "mean_p_line": {r: sum(s[r]["p_line"] for s, _ in rows) / len(rows) for r in RULES},
                        "status_quo_p10_under_1e-6": sum(1 for s, _ in rows if s["status_quo"]["p10"] < 1e-6),
                        "mean_tail_extent_bp": {r: sum(tail_extent(raw[c["key"]], c["line"], r) for _, c in rows) / len(rows) for r in RULES}}
    result["binding_classes"] = classes
    full = [s for s, c in zip(scored, cells) if c["line"] is not None]
    result["pit_deciles_at_full_allotment"] = {r: decile_counts([s[r]["pit_value"] for s in full]) for r in RULES}
    result["largest_uncapped_q99_above_the_line_bp"] = max([raw[c["key"]][-1] - c["line"] for c in cells if c["line"] is not None] or [0.0])
    return result


def score_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    m66 = _load("calibration_masking_candidate_1366", "calibration_masking_candidate_1366_in_1389")
    declared = m66.committed_declaration(DECLARATION)
    _STATE["m"] = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1389")
    record = json.loads(RECORD_1314.read_text(encoding="utf-8"))
    result: dict = {"issue": 1389, "declaration": "metadata/cap_tail_rule_1389.json", "label": "development, not a verdict", "windows": {},
                    "walk_files": {}, "amendments": declared["amendments"], "draws": args.draws, "seed": SEED}
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
        result["windows"][name] = window_result(doc, record, args.draws, args.workers)
    if not result["windows"]:
        raise SystemExit(f"no walk file in {args.walks}")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk", help="walk the candidate and write the uncapped quantiles of every cell")
    w.add_argument("--panel", required=True)
    w.add_argument("--window", choices=WINDOWS, required=True)
    w.add_argument("--output", required=True)
    w.add_argument("--first", type=date.fromisoformat, default=None, help="first decision day (for a short trial)")
    s = sub.add_parser("score", help="score the rules on the walks")
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


def page_command(args) -> int:  # replaced below
    raise SystemExit("the page is written after the scores")


if __name__ == "__main__":
    raise SystemExit(main())
