#!/usr/bin/env python3
"""H6 development step 2 (#724): (s3c-ann-net) on #1131's event-day strata, and one risk-date-specialised variant.

A development measurement, never a verdict (scoring protocol v1, #640). Nothing is published, no locked day and no day after 2025-12-31 is scored.
Everything it computes is declared in `metadata/h6_step2_724.json`, which `run` refuses to read unless it is committed and unchanged.

* The candidate is the frozen H5 candidate (s3c-ann-net), walked by `scripts/capped_baselines_b2star_1434.py` unchanged at the 18:00 instant; this
  script reads that walk's file and never fits a model.
* The strata, their membership and the paired test are #1131's (`scripts/h6_design_1131.py`), with the coupon flag read as #849 does.
* The benchmarks are B1, B1', B2 and the risk-date calendar benchmark (#693) as #1131 scored them, and B2*-cap and B1'*-cap from the walk (#1440).
  `spread_mr_ctx` (#761) is carried beside the candidate as #1131's reference column.
* The variant `sc_s3c_ann_net_riskscale` rescales the candidate's 23 quantiles about their median by a factor chosen, per stratum, from the candidate's
  own realised scores as of each decision instant.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/capped_baselines_b2star_1434.py walk --panel PUB.csv --window development --output WALK/development.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/h6_step2_724.py run --published PUB.csv --walk WALK/development.json
    python3 scripts/h6_step2_724.py report
    python3 scripts/h6_step2_724.py check

The walk takes about three minutes and `run` about ten on four cores. `run` writes `docs/research/h6-step2-724/result.json`; `report` writes the
page `docs/research/h6-step2-724-result.md` from it alone; `check` fails when the page is not what the record gives. Standard library only.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import importlib.util
import json
import math
import multiprocessing
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Set, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "h6_step2_724.json"
RECORD = REPO / "docs" / "research" / "h6-step2-724" / "result.json"
PAGE = REPO / "docs" / "research" / "h6-step2-724-result.md"
RECORD_1434 = REPO / "docs" / "research" / "capped-baselines-b2star-1434" / "result.json"

SEED = 724
DRAWS = 10_000
EVENT_BLOCK = 3.0
EVENT_LAG = 3
FIRST_DECISION = date(2020, 4, 3)
LAST_TARGET = date(2025, 12, 31)
MINIMUM_EVENTS = 30
LONGEST_LEAD = max(sp.HORIZONS)
TOLERANCE = 1e-9

#: The variant (declaration, `variant`).
K_GRID: Tuple[float, ...] = (0.5, 0.67, 0.8, 1.0, 1.25, 1.5, 2.0)
WINDOW = 150
MIN_CELLS = 60
LABEL_PRIORITY: Tuple[str, ...] = ("quarter_and_year_end", "month_end_turn", "tax_date", "coupon_settlement", "bill_settlement_large", "fomc_meeting",
                                   "post_fomc_window")
_MEDIAN = sp.GRID.index(0.5)

METRICS = ("grid_crps", "upper_tail_twcrps")
METRIC_TITLES = {"grid_crps": "grid CRPS (primary)", "upper_tail_twcrps": "upper-tail twCRPS (key secondary)"}
MODELS = ("candidate", "variant", "reference")
MODEL_TITLES = {"candidate": "(s3c-ann-net)", "variant": "risk-date variant", "reference": "spread_mr_ctx"}
BENCHMARKS = ("B1", "B1_prime", "B2", "calendar", "B2star_cap", "B1p_star_cap")
BENCH_TITLES = {"B1": "B1", "B1_prime": "B1'", "B2": "B2", "calendar": "risk-date calendar (#693)", "B2star_cap": "B2*-cap", "B1p_star_cap": "B1'*-cap"}
DECISIVE = ("B1", "B2")
UNION = "union"
UNION_EX_BILL = "union_without_bill"
PRIMARY_SET = UNION_EX_BILL
STRATUM_TEXT = {
    "coupon_settlement": "coupon settlement", "bill_settlement_large": "large bill settlement", "month_end_turn": "month-end turn",
    "quarter_end_turn": "quarter-end turn (Mar, Jun, Sep)", "year_end": "year-end", "quarter_and_year_end": "quarter-end and year-end",
    "tax_date": "tax date", "fomc_meeting": "FOMC meeting day", "post_fomc_window": "IORB-change window (two days after a meeting)",
    UNION: "union of the strata", UNION_EX_BILL: "union without the bill stratum (primary)",
}
_STATE: Dict = {}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_in_724", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_in_724"] = module
    spec.loader.exec_module(module)
    return module


def declaration_file() -> dict:
    return json.loads(DECLARATION.read_text(encoding="utf-8"))


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_instant(text: str) -> None:
    """The study is made at the 18:00 decision instant (#1312, #1397).

    Raises:
        ValueError: any other instant.
    """

    if text != "18:00":
        raise ValueError(f"this study is made at 18:00, not {text}")


def require_scored_days(days, last: date = LAST_TARGET) -> None:
    """Refuse a day after `last`, the declared end of the scored days, and a locked day.

    Raises:
        LookAheadError: a day after `last`, or in a locked tier.
    """

    days = sorted(days)
    for day in days:
        if day > last:
            raise LookAheadError(f"{day} is after {last}, the last day #724 scores; the declaration admits no later day")
    lockbox.require_unlocked(days, where="scripts/h6_step2_724")


# -- the variant -----------------------------------------------------------------------------------------------------------


def rescale(raw: Sequence[float], k: float) -> List[float]:
    """`c + k * (r - c)` for each quantile `r`, `c` the median: the candidate's width times `k`, its median and order kept.

    Raises:
        ValueError: `k` is not positive.
    """

    if not k > 0.0:
        raise ValueError(f"the scale must be positive, got {k}")
    c = raw[_MEDIAN]
    return [c + k * (r - c) for r in raw]


def require_realised(history: Sequence[Tuple[int, Sequence[float]]], anchor_row: int) -> None:
    """Every history cell's outcome must have been public at the decision: its target row at or before `anchor_row`.

    Raises:
        LookAheadError: a cell realised after the anchor.
    """

    for target_row, _ in history:
        if target_row > anchor_row:
            raise LookAheadError(f"a cell targeting row {target_row} is after the decision's anchor row {anchor_row}; its outcome was not public")


def usable_history(history: Sequence[Tuple[int, Sequence[float]]], anchor_row: int) -> List[Tuple[int, Sequence[float]]]:
    """The cells of `history` (target row, losses at each grid value) whose outcome was public at a decision with anchor row `anchor_row`."""

    out = [(target_row, losses) for target_row, losses in history if target_row <= anchor_row]
    require_realised(out, anchor_row)
    return out


def select_scale(history: Sequence[Tuple[int, Sequence[float]]], grid: Sequence[float] = K_GRID, *, window: int = WINDOW, minimum: int = MIN_CELLS) -> float:
    """The grid value with the lowest mean loss over the most recent `window` cells (by target row), or 1.0 with fewer than `minimum`.

    A tie goes to the value nearest one (in |log k|), then to the smaller.
    """

    window_cells = sorted(history, key=lambda cell: cell[0])[-window:]
    if len(window_cells) < minimum:
        return 1.0
    means = [sum(cell[1][i] for cell in window_cells) / len(window_cells) for i in range(len(grid))]
    best = min(range(len(grid)), key=lambda i: (round(means[i], 12), abs(math.log(grid[i])), grid[i]))
    return grid[best]


def cell_label(strata: Set[str]) -> Optional[str]:
    """The first of `LABEL_PRIORITY` that holds, or `None`."""

    for name in LABEL_PRIORITY:
        if name in strata:
            return name
    return None


# -- the strata ------------------------------------------------------------------------------------------------------------


def evaluation_membership(day: date, values: Mapping[str, Optional[float]], *, fomc_meeting: bool, post_fomc: bool, bill_floor: Optional[float],
                          coupon_public: bool) -> Set[str]:
    """#1131's strata for a target day, with the coupon settlement read as #849 does: a member only where its flag was public at the decision instant."""

    h6 = _STATE.get("h6") or _load("h6_design_1131")
    _STATE["h6"] = h6
    out = h6.membership(day, {**values, "treasury_settlement_coupons": 0.0}, fomc_meeting=fomc_meeting, post_fomc=post_fomc, bill_floor=bill_floor)
    coupons = float(values.get("treasury_settlement_coupons") or 0.0)
    if coupons > 0.0 and coupon_public:
        out.add("coupon_settlement")
    return out


def target_means(dates: Sequence[date], positions: Mapping[date, int], cells: Mapping[Tuple[date, int], float], *, first: date, last: date) -> Dict[date, float]:
    """`{target day: mean over leads 1-5 of the cells that target it}`, where all five exist, decision days from `first`, targets to `last`."""

    out = {}
    for target in dates:
        pos = positions[target]
        if target > last or pos < LONGEST_LEAD or dates[pos - LONGEST_LEAD] < first:
            continue
        parts = []
        for h in sp.HORIZONS:
            cell = (dates[pos - h], h)
            if cell not in cells:
                parts = None
                break
            parts.append(cells[cell])
        if parts:
            out[target] = sum(parts) / len(parts)
    return out


# -- the reading rules -----------------------------------------------------------------------------------------------------


def _lower(row: Optional[Mapping[str, object]]) -> Optional[float]:
    if not row or row.get("thin") or "undefined" in row or row.get("identical") or row.get("skill_interval") is None:
        return None
    return row["skill_interval"][0]


def kill_reading(row_b1: Mapping[str, object], row_b2: Mapping[str, object]) -> str:
    """The development reading of the kill rule: skill only if the lower end of the 90% interval is above zero against B1 and against B2."""

    lowers = (_lower(row_b1), _lower(row_b2))
    if any(x is None for x in lowers):
        return "undefined"
    return "skill" if all(x > 0.0 for x in lowers) else "no skill shown"


def variant_adds(row: Mapping[str, object]) -> bool:
    """The variant adds skill over the candidate if the lower end of its 90% interval against the candidate is above zero."""

    lower = _lower(row)
    return lower is not None and lower > 0.0


# -- the paired tests, in parallel ------------------------------------------------------------------------------------------


def paired(bench: Mapping[date, float], cand: Mapping[date, float], events: Sequence[date]) -> dict:
    s761 = _STATE.get("s761") or _load("spread_mr_variants_761")
    _STATE["s761"] = s761
    if len(events) < MINIMUM_EVENTS:
        return {"events": len(events), "thin": True}
    if all(bench[e] == cand[e] for e in events):
        return {"events": len(events), "identical": True}
    pair = ({e: bench[e] for e in events}, {e: cand[e] for e in events})
    try:
        (test,) = sp.paired_tests([pair], seed=SEED, draws=DRAWS, block_length=EVENT_BLOCK, hac_lag=EVENT_LAG)
    except sp.ProtocolError as error:
        return {"undefined": str(error), "events": len(events)}
    return {**s761.paired_row(test), "events": len(events)}


def _task(job):
    key, metric, bench, model, events = job
    scores = _STATE["scores"][metric]
    return key, paired(scores[bench], scores[model], events)


# -- the run ---------------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    declaration = committed_declaration()
    h6 = _load("h6_design_1131")
    cb = _load("capped_baselines_b2star_1434")
    from repo_model import capped_law as cl, protocol_benchmarks as pb, spread_mr_variants as smv
    from repo_model import fomc_calendar as fc
    from repo_model.baseline import panel_sha256

    s686 = _load("b1_calendar_960").s686
    instant = s686.DECISION_TIME.isoformat(timespec="minutes")
    require_instant(instant)
    published = Path(args.published)
    walk = json.loads(Path(args.walk).read_text(encoding="utf-8"))
    if walk["panel_sha256"] != panel_sha256(published) or walk["instant"] != "18:00" or walk["window"] != "development":
        raise ValueError("the walk is not the development walk of this panel at 18:00")

    data = h6.build(published)
    frame, panel = data["frame"], data["panel"]
    decision_time = s686.DECISION_TIME
    positions, dates = frame.position, frame.dates
    values = [row.values for row in panel]
    meetings = fc.load_calendar()

    # -- the walk's cells ------------------------------------------------------------------------------------------------
    cells = walk["cells"]
    raw = walk["uncapped_quantiles"]
    scores: Dict[str, Dict[str, Dict[Tuple[date, int], float]]] = {m: {} for m in METRICS}
    cand_cells: Dict[Tuple[date, int], dict] = {}
    for model, (base, capped) in (("candidate", (None, True)), ("B2star_cap", ("B2star", True)), ("B1p_star_cap", ("B1p_star", True))):
        for metric in METRICS:
            scores[metric][model] = {}
        for c in cells:
            vector = raw[c["key"]] if base is None else walk["baselines"][base][c["key"]]
            cell = cb.model_cell(vector, c["line"], c["y"], capped=capped)
            for metric in METRICS:
                scores[metric][model][(date.fromisoformat(c["day"]), c["lead"])] = cell[metric]
    reproduction = json.loads(RECORD_1434.read_text(encoding="utf-8"))["windows"]["development"]["groups"]["pooled"]["all cells"]["metrics"]
    reproduced = {}
    for model, key in (("candidate", "candidate"), ("B2star_cap", "B2star_cap"), ("B1p_star_cap", "B1p_star_cap")):
        for metric in METRICS:
            here = sum(scores[metric][model].values()) / len(scores[metric][model])
            there = reproduction[metric]["means"][key]
            reproduced[f"{model}/{metric}"] = {"here": here, "1434": there}
            if abs(here - there) > TOLERANCE:
                raise ValueError(f"{model} {metric}: mean {here} here, {there} in #1434's record")

    # -- the variant -----------------------------------------------------------------------------------------------------
    anchors: Dict[date, int] = {}
    fomc_cache: Dict[date, Tuple[Set[date], Set[date]]] = {}
    registry = frame.registry
    labels: Dict[str, Optional[str]] = {}
    losses: Dict[str, Tuple[float, ...]] = {}
    order = sorted(cells, key=lambda c: (c["day"], c["lead"]))
    for c in order:
        d, t = date.fromisoformat(c["day"]), date.fromisoformat(c["target"])
        pos_d, pos_t = positions[d], positions[t]
        if d not in anchors:
            anchors[d] = pb._anchor(panel, pos_d, registry, decision_time)
            fomc_cache[d] = h6.fomc_days(meetings, datetime.combine(d, decision_time))
        meeting_days, window_days = fomc_cache[d]
        strata = evaluation_membership(
            t, values[pos_t], fomc_meeting=t in meeting_days, post_fomc=t in window_days, bill_floor=h6.bill_threshold(values, pos_d),
            coupon_public=smv.coupon_public(panel, pos_t, pos_d, registry=registry, decision_time=decision_time))
        labels[c["key"]] = cell_label(strata)
        losses[c["key"]] = tuple(sp.grid_crps(cl.cap(rescale(raw[c["key"]], k), c["line"], cb.MARGIN_BP), c["y"]) for k in K_GRID)
    by_label: Dict[str, List[Tuple[int, Tuple[float, ...]]]] = {}
    for c in order:
        if labels[c["key"]] is not None:
            by_label.setdefault(labels[c["key"]], []).append((positions[date.fromisoformat(c["target"])], losses[c["key"]]))
    for label in by_label:
        by_label[label].sort(key=lambda cell: cell[0])
    for metric in METRICS:
        scores[metric]["variant"] = {}
    chosen: Dict[str, Optional[float]] = {}
    for c in order:
        d = date.fromisoformat(c["day"])
        label = labels[c["key"]]
        k = 1.0 if label is None else select_scale(usable_history(by_label[label], anchors[d]))
        chosen[c["key"]] = k
        cell = cb.model_cell(rescale(raw[c["key"]], k), c["line"], c["y"], capped=True)
        for metric in METRICS:
            scores[metric]["variant"][(d, c["lead"])] = cell[metric]
    scale_summary: Dict[str, dict] = {}
    for c in order:
        label = labels[c["key"]] or "none"
        entry = scale_summary.setdefault(label, {"cells": 0, "moved": 0, "sum_log_k": 0.0, "by_k": {}})
        k = chosen[c["key"]]
        entry["cells"] += 1
        entry["moved"] += int(k != 1.0)
        entry["sum_log_k"] += math.log(k)
        entry["by_k"][str(k)] = entry["by_k"].get(str(k), 0) + 1
    for entry in scale_summary.values():
        entry["geometric_mean_k"] = math.exp(entry.pop("sum_log_k") / entry["cells"])

    # -- the frame's models and benchmarks ---------------------------------------------------------------------------------
    for metric in METRICS:
        for model, source in (("reference", "spread_mr_ctx"), ("B1", "B1"), ("B1_prime", "B1_prime"), ("B2", "B2"), ("calendar", "calendar")):
            scores[metric][model] = data["cells"][metric][source]
    target_scores = {m: {name: target_means(dates, positions, series, first=FIRST_DECISION, last=LAST_TARGET) for name, series in scores[m].items()}
                     for m in METRICS}
    required = ("candidate", "variant", "reference", "B1", "B1_prime", "B2", "B2star_cap", "B1p_star_cap")
    common = sorted(set.intersection(*(set(target_scores["grid_crps"][name]) for name in required)))
    require_scored_days(common)
    require_scored_days({dates[positions[t] - h] for t in common for h in sp.HORIZONS})

    # -- the strata on the common days ---------------------------------------------------------------------------------------
    sets: Dict[str, List[date]] = {name: [] for name in h6.STRATA}
    union: List[date] = []
    union_ex: List[date] = []
    coupon_moved = 0
    for t in common:
        pos = positions[t]
        as_of = datetime.combine(dates[pos - LONGEST_LEAD], decision_time)
        meeting_days, window_days = h6.fomc_days(meetings, as_of)
        public = smv.coupon_public(panel, pos, pos - LONGEST_LEAD, registry=registry, decision_time=decision_time)
        member = evaluation_membership(t, values[pos], fomc_meeting=t in meeting_days, post_fomc=t in window_days, bill_floor=h6.bill_threshold(values, pos),
                                       coupon_public=public)
        if float(values[pos].get("treasury_settlement_coupons") or 0.0) > 0.0 and not public:
            coupon_moved += 1
        for name in member:
            sets[name].append(t)
        if member:
            union.append(t)
        if member - {"bill_settlement_large"}:
            union_ex.append(t)
    sets[UNION], sets[UNION_EX_BILL] = union, union_ex
    years = (common[-1] - common[0]).days / 365.25
    order_sets = h6.STRATA + (UNION, UNION_EX_BILL)
    strata_rows = {}
    for name in order_sets:
        events = sets[name]
        strata_rows[name] = {"n": len(events), "per_year": len(events) / years, "thin": len(events) < MINIMUM_EVENTS,
                             "by_year": {y: sum(1 for e in events if str(e.year) == y) for y in sorted({str(e.year) for e in events})},
                             "covered": {b: sum(1 for e in events if e in target_scores["grid_crps"][b]) for b in BENCHMARKS}}
    record: Dict[str, object] = {
        "declaration_sha256": sha256(DECLARATION), "panel_sha256": sha256(published), "walk_panel_sha256": walk["panel_sha256"], "seed": SEED,
        "draws": DRAWS, "event_block": EVENT_BLOCK, "event_lag": EVENT_LAG, "instant": instant, "k_grid": list(K_GRID), "window": WINDOW,
        "min_cells": MIN_CELLS, "minimum_events": MINIMUM_EVENTS, "variants_scored": 1,
        "history": {"first_target": common[0].isoformat(), "last_target": common[-1].isoformat(), "target_days": len(common), "years": years,
                    "walk_decision_days": walk["decision_days"], "walk_cells": len(cells)},
        "reproduces_1434": reproduced, "coupon_days_not_public_at_lead_5": coupon_moved, "strata": strata_rows, "variant_scales": scale_summary,
    }

    # -- the jobs --------------------------------------------------------------------------------------------------------------
    regime = {t: frame.regime(t) for t in common}
    day_type = {t: frame.day_type(t) for t in common}
    groups: Dict[str, Dict[str, List[date]]] = {"regime": {}, "pressure_day_type": {}}
    for t in union_ex:
        groups["regime"].setdefault(regime[t], []).append(t)
        groups["pressure_day_type"].setdefault(day_type[t], []).append(t)
    jobs: List[tuple] = []

    def events_of(scope: Sequence[date], *names: str, metric: str) -> List[date]:
        return [e for e in scope if all(e in target_scores[metric][n] for n in names)]

    scopes: Dict[str, Sequence[date]] = {f"set/{name}": sets[name] for name in order_sets}
    for kind, by in groups.items():
        for label, events in sorted(by.items()):
            scopes[f"{kind}/{label}"] = events
    for scope, base_events in scopes.items():
        split = not scope.startswith("set/")
        benches = BENCHMARKS if not split else ("B1", "B1_prime", "B2", "B2star_cap")
        for metric in METRICS:
            for model in MODELS:
                for bench in benches:
                    jobs.append(((scope, metric, model, bench), metric, bench, model, events_of(base_events, bench, model, metric=metric)))
            jobs.append(((scope, metric, "variant", "candidate"), metric, "candidate", "variant", events_of(base_events, "candidate", "variant", metric=metric)))
    _STATE["scores"] = target_scores
    context = multiprocessing.get_context("fork")
    with context.Pool(args.workers) as pool:
        results = pool.map(_task, jobs, chunksize=4)
    rows: Dict[str, dict] = {}
    for (scope, metric, model, bench), row in results:
        rows.setdefault(scope, {}).setdefault(metric, {}).setdefault(model, {})[bench] = row
    record["rows"] = rows
    record["scopes"] = {scope: len(events) for scope, events in scopes.items()}

    primary = rows[f"set/{PRIMARY_SET}"]["grid_crps"]
    record["reading"] = {
        "kill_rule_candidate": kill_reading(primary["candidate"]["B1"], primary["candidate"]["B2"]),
        "kill_rule_variant": kill_reading(primary["variant"]["B1"], primary["variant"]["B2"]),
        "variant_adds_grid_crps": variant_adds(primary["variant"]["candidate"]),
        "variant_adds_twcrps": variant_adds(rows[f"set/{PRIMARY_SET}"]["upper_tail_twcrps"]["variant"]["candidate"]),
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {RECORD}: {len(common)} target days, {len(jobs)} paired tests")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------------


def pct(x: Optional[float], signed: bool = True) -> str:
    return "n/a" if x is None else format(100.0 * x, "+.1f" if signed else ".1f") + "%"


def skill_text(row: Optional[Mapping[str, object]]) -> str:
    if row is None:
        return "n/a"
    if row.get("thin"):
        return f"thin ({row['events']})"
    if row.get("identical"):
        return "identical"
    if "undefined" in row:
        return "undefined"
    lo, hi = row["skill_interval"]
    return f"{pct(row['skill'])} [{pct(lo)}, {pct(hi)}]"


def diff_text(row: Optional[Mapping[str, object]]) -> str:
    if row is None or row.get("thin") or row.get("identical") or "undefined" in row:
        return skill_text(row)
    lo, hi = row["difference_interval"]
    return f"{row['difference']:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def _scope_title(scope: str) -> str:
    kind, label = scope.split("/", 1)
    return STRATUM_TEXT.get(label, label) if kind == "set" else label


def skill_table(r: Mapping[str, object], metric: str, scopes: Sequence[str], benches: Sequence[str]) -> List[str]:
    lines = ["| stratum | benchmark | events | " + " | ".join(MODEL_TITLES[m] for m in MODELS) + " |", "|---|---|---|---|---|---|"]
    for scope in scopes:
        for bench in benches:
            cells = [r["rows"][scope][metric][m][bench] for m in MODELS]
            lines.append(f"| {_scope_title(scope)} | {BENCH_TITLES[bench]} | {cells[0].get('events', 0)} | " + " | ".join(skill_text(c) for c in cells) + " |")
    return lines


def variant_table(r: Mapping[str, object], scopes: Sequence[str]) -> List[str]:
    lines = ["| cut | events | grid CRPS skill over (s3c-ann-net) | grid CRPS difference (bp) | twCRPS skill over (s3c-ann-net) |", "|---|---|---|---|---|"]
    for scope in scopes:
        g = r["rows"][scope]["grid_crps"]["variant"]["candidate"]
        t = r["rows"][scope]["upper_tail_twcrps"]["variant"]["candidate"]
        lines.append(f"| {_scope_title(scope)} | {g.get('events', 0)} | {skill_text(g)} | {diff_text(g)} | {skill_text(t)} |")
    return lines


def render(r: Mapping[str, object]) -> str:
    d = declaration_file()
    set_scopes = [f"set/{name}" for name in (UNION_EX_BILL, UNION) + tuple(n for n in STRATUM_TEXT if n not in (UNION, UNION_EX_BILL))]
    split_scopes = sorted(s for s in r["scopes"] if not s.startswith("set/"))
    regimes = [s for s in split_scopes if s.startswith("regime/")]
    types = [s for s in split_scopes if s.startswith("pressure_day_type/")]
    h = r["history"]
    prim = r["rows"][f"set/{PRIMARY_SET}"]
    reading = r["reading"]
    out: List[str] = []
    out += ["# H6 development step 2: (s3c-ann-net) on the event-day strata, and a risk-date variant (#724)", ""]
    out += [f"**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), development step 2, milestone M2: the H5 model scored on risk dates, then a "
            f"risk-date-specialised variant. **Development data, not a verdict** (scoring protocol v1, #640): the days were seen before the declaration "
            f"(`metadata/h6_step2_724.json`, committed before any score), no confirmation day is scored, nothing is published and no locked day or day after "
            f"2025-12-31 is read. Script `scripts/h6_step2_724.py`; every figure below is read from `docs/research/h6-step2-724/result.json`. Made at the "
            f"{r['instant']} decision instant, on the published panel (`{r['panel_sha256'][:12]}...`).", ""]
    out += ["## 1. What is scored", ""]
    out += [f"- **Candidate.** (s3c-ann-net), frozen by Eleonora on 2 November 2026 (SRF cap kept, probability rule b), walked by `scripts/capped_baselines_b2star_1434.py` "
            f"unchanged. The pooled development means of the candidate, B2*-cap and B1'*-cap reproduce #1434's record within 1e-9 "
            f"({len(r['reproduces_1434'])} figures checked).",
            f"- **Strata.** #1131's (`metadata/h6_design_1131.json`), every one read from the calendar at the target day, over {h['target_days']} target days from "
            f"{h['first_target']} to {h['last_target']} ({h['years']:.1f} years) on which the candidate, the variant, the reference and every benchmark but the "
            f"calendar one have a forecast at all five leads. A day may be in several strata; the union counts it once.",
            f"- **Score.** The H5 metric: grid CRPS averaged over leads 1 to 5 at the target day (primary), upper-tail twCRPS (key secondary). Paired, positive favours the "
            f"model; #1131's studentized stationary bootstrap (block {r['event_block']:.0f} events, HAC lag {r['event_lag']}, {r['draws']} draws, seed {r['seed']}), two-sided 90%, so "
            f"the lower end is the one-sided 95% lower bound.",
            f"- **Benchmarks.** B1 and B2 decide (default 6 of #1131); B1', the risk-date calendar benchmark (#693), B2*-cap (#1440, merged as #1449) and B1'*-cap are reported. "
            f"`spread_mr_ctx` (#761) is #1131's reference column, carried beside the candidate; it is not a candidate here.",
            f"- **Variant (1 declared, 1 scored).** `sc_s3c_ann_net_riskscale`: the candidate's 23 quantiles stretched about their median by k, chosen from "
            f"{r['k_grid']} per stratum as the k with the lowest mean grid CRPS of the candidate's own rescaled, capped forecasts over the most recent {r['window']} cells of "
            f"that stratum (fewer than {r['min_cells']}: k = 1), using only cells whose outcome was public at the decision (target row at or before the decision's anchor row). "
            f"A cell's stratum is read at its own decision instant. Direct pairs: the variant fits nothing.", ""]
    out += ["### Defaults and rulings", "",
            "Rulings: " + "; ".join(d["defaults_and_rulings"]["ruled"]) + ".", "",
            "Defaults of #1131's section 6 that Eleonora has not ruled on, taken here: " + "; ".join(d["defaults_and_rulings"]["defaults_of_1131_section_6_taken_because_she_has_not_ruled"]) + ".", "",
            f"The coupon flag is read as #849 does: {r['coupon_days_not_public_at_lead_5']} target days have a coupon settlement that was not public at the lead-5 decision "
            f"instant and are not coupon-stratum members (#1131 read the panel's flag).", ""]
    out += ["## 2. The strata", "",
            "| stratum | events | per year | by calendar year | " + " | ".join(BENCH_TITLES[b] for b in BENCHMARKS) + " |", "|---|---|---|---|" + "---|" * len(BENCHMARKS)]
    for name in [s[4:] for s in set_scopes]:
        s = r["strata"][name]
        by_year = ", ".join(f"{y}: {n}" for y, n in s["by_year"].items())
        out.append(f"| {STRATUM_TEXT[name]}{' (thin)' if s['thin'] else ''} | {s['n']} | {s['per_year']:.1f} | {by_year} | " + " | ".join(str(s["covered"][b]) for b in BENCHMARKS) + " |")
    out += ["", "Columns after the year split: events each benchmark covers. The calendar benchmark exists only on a day typed as one of its four risk types at all five leads.", ""]
    for metric in METRICS:
        out += [f"## 3. Skill by stratum: {METRIC_TITLES[metric]}", "",
                "Skill is the share of the benchmark's mean score the model removes, with the 90% interval. Development data, not a verdict.", ""]
        out += skill_table(r, metric, set_scopes, BENCHMARKS) + [""]
    out += ["## 4. The variant against (s3c-ann-net)", "",
            "Paired on the same events, same bootstrap; positive favours the variant. Grid CRPS difference is in bp (candidate minus variant).", ""]
    out += variant_table(r, set_scopes) + [""]
    out += ["## 5. By regime and by pressure-day type (the union without the bill stratum)", ""]
    for title, scopes in (("Regime", regimes), ("Pressure-day type", types)):
        out += [f"### {title}: grid CRPS skill", ""]
        out += skill_table(r, "grid_crps", scopes, ("B1", "B1_prime", "B2", "B2star_cap")) + [""]
        out += [f"### {title}: the variant against (s3c-ann-net)", ""] + variant_table(r, scopes) + [""]
    out += ["## 6. What the variant did", "", "| label | cells | cells with k not 1 | geometric mean k | cells by k |", "|---|---|---|---|---|"]
    for label, s in sorted(r["variant_scales"].items()):
        out.append(f"| {label} | {s['cells']} | {s['moved']} | {s['geometric_mean_k']:.3f} | " + ", ".join(f"{k}: {n}" for k, n in sorted(s["by_k"].items(), key=lambda kv: float(kv[0]))) + " |")
    out += ["", "A label is the cell's first stratum in the declared order; `none` is a cell in no stratum, which keeps k = 1.", ""]
    out += ["## 7. Reading (development, not a verdict)", ""]
    g_b1, g_b2 = prim["grid_crps"]["candidate"]["B1"], prim["grid_crps"]["candidate"]["B2"]
    out += [
        f"**Kill rule, in words.** H6's kill is no CRPS skill against as-of persistence and the risk-date calendar benchmark on the risk dates. Read on development data: "
        f"(s3c-ann-net) shows no skill on the union without the bill stratum if the 90% interval of its grid CRPS skill against B1 or against B2 includes zero or lies below it, "
        f"and shows skill if the lower end is above zero against both. Against B1 it is {skill_text(g_b1)}, against B2 {skill_text(g_b2)}: **{reading['kill_rule_candidate']}**. "
        f"B1' ({skill_text(prim['candidate']['B1_prime'])}) and B2*-cap ({skill_text(prim['candidate']['B2star_cap'])}) do not decide; they say what the skill is worth. "
        f"The risk-date calendar benchmark (#693) covers {r['strata'][PRIMARY_SET]['covered']['calendar']} of the {r['strata'][PRIMARY_SET]['n']} events: "
        f"{skill_text(prim['candidate']['calendar'])}.", "",
        f"The variant, read the same way, is **{reading['kill_rule_variant']}** (against B1 {skill_text(prim['variant']['B1'])}, against B2 {skill_text(prim['variant']['B2'])}). "
        f"The reference `spread_mr_ctx` is {skill_text(prim['reference']['B1'])} against B1 and {skill_text(prim['reference']['B2'])} against B2.", "",
        "This is a development reading on days already seen. It closes nothing and registers nothing; the verdict is for prospective confirmation days only.", ""]
    out += ["## What this shows, and does not", "",
            "- It shows how the frozen candidate scores on #1131's event-day strata on 2020-2025 development days, split by stratum, regime and pressure-day type, and "
            "whether one declared risk-date rescaling improves on it there.",
            "- It does not show skill on any confirmation day, does not change the candidate, and sets no rule. The strata overlap and the days within a stratum are "
            "dependent; the intervals use #1131's block of 3 events.",
            "- The reported cuts carry no multiplicity correction (default 7). One variant was declared and scored, so the variant count is 1; the scale grid is part of that variant.",
            "- Not checked: B1' and the calendar benchmark on days outside their cover; the 2026 days (#1394's confirmation, not this step); a stratum-specific calendar "
            "benchmark for the FOMC and IORB rows (question 8 of #1131, default not added).", ""]
    verdict = ("adds skill" if reading["variant_adds_grid_crps"] else "adds no skill that this data can show")
    g = prim["grid_crps"]["variant"]["candidate"]
    t = prim["upper_tail_twcrps"]["variant"]["candidate"]
    out.append(f"**Does the specialised variant add skill over (s3c-ann-net) on the union (without the bill stratum)? It {verdict} on grid CRPS: {skill_text(g)} over "
               f"{g.get('events', 0)} events (twCRPS {skill_text(t)}). Development data, not a verdict.**")
    return "\n".join(out) + "\n"


def report_command(args) -> int:
    PAGE.write_text(render(json.loads(RECORD.read_text(encoding="utf-8"))), encoding="utf-8")
    return 0


def check_command(args) -> int:
    expected = render(json.loads(RECORD.read_text(encoding="utf-8")))
    if PAGE.read_text(encoding="utf-8") != expected:
        print(f"{PAGE} is not what {RECORD} gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="score the candidate, the variant and the benchmarks on the strata")
    run.add_argument("--published", required=True)
    run.add_argument("--walk", required=True)
    run.add_argument("--workers", type=int, default=4)
    sub.add_parser("report", help="write the page from the record")
    sub.add_parser("check", help="fail if the page is not what the record gives")
    args = parser.parse_args(argv)
    return {"run": run_command, "report": report_command, "check": check_command}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
