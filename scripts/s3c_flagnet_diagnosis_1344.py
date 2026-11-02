"""Why (s3c-ann-flagnet) gains on the Brier score and loses in 2020, and what a prospective test of it could show (#1344; H5 step 3; her ruling of
1 November 2026, ledger item 95, on #1326 question 1; diagnosis of #1321's record).

A development study, never a verdict, and a diagnosis of a record that exists: the walks, fits and forecasts are #1321's, built by
`scripts/s3c_flagnet_gross_1321.py` exactly as merged, at the 18:00 decision instant (`decision_instant_pinned`). Nothing is fitted here that #1321
did not fit and nothing is scored that it did not score; the 2026 days are split further and decide nothing. Every choice is in
`metadata/s3c_flagnet_diagnosis_1344.json`, which this script refuses to read unless it is committed and unchanged. It answers:

1. where the Brier gain of (s3c-ann-flagnet) against (s3c-ann-net) sits (settlement-day type, leg, regime, month, scarcity state, realised event, lead);
2. where the 2020 loss sits, and whether it is on the immediate-release cash management bill days (#1301);
3. the fitted settlement shift against the realised settlement-day premium by regime, split into the part the flags carry and the part the nets carry;
4. the power of the prospective comparison drafted in `metadata/s3c_flagnet_prospective_draft_1344.json` (development series, the protocol's looks).

Commands, from a clone of the branch (the two walks per window are minutes, the bootstraps a few minutes more; a cloud run):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_flagnet_diagnosis_1344.py score --panel PUB.csv \\
        --output docs/research/s3c-flagnet-diagnosis-1344/result.json
    PYTHONPATH=src python3 scripts/s3c_flagnet_diagnosis_1344.py page \\
        --score docs/research/s3c-flagnet-diagnosis-1344/result.json --output docs/research/s3c-flagnet-diagnosis-1344-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import multiprocessing
import random
import sys
from datetime import date, datetime
from pathlib import Path
from statistics import NormalDist
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

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


from repo_model import announced_iorb, data, metrics, policy_events, s3c_announced  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1321's script (and through it #1288's, #1273's and #1255's), loaded under an alias of its own so that the pickling of the worker pool's tasks
#: does not meet another test module's copy.
m1321 = _load("s3c_flagnet_gross_1321", "s3c_flagnet_gross_1321_in_1344")
m1288, m1273, c, k, s686 = m1321.m1288, m1321.m1273, m1321.c, m1321.k, m1321.s686

DECLARATION = REPO / "metadata" / "s3c_flagnet_diagnosis_1344.json"
DRAFT = REPO / "metadata" / "s3c_flagnet_prospective_draft_1344.json"
RECORD_1321 = REPO / "docs" / "research" / "s3c-flagnet-gross-1321" / "result.json"
RELEASE_TIMES = REPO / "metadata" / "announcement_release_times_1301.json"
SEED = 1344
REPS = 2000
LAST_DAY = EXPLORATORY_END
BLOCK = float(sp.BLOCK_LENGTH)
MIN_UNITS = 20
POST_COVID_FROM = date(2020, 4, 3)
S3C, ANN, ANNNET, FLAGNET = m1288.S3C, m1288.ANN, m1288.ANNNET, m1321.FLAGNET
MODELS = (ANNNET, FLAGNET, ANN, S3C)
METRICS = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)"}
LEADS = tuple(sp.HORIZONS)
TAU = m1273.TAU
TYPE_LABELS = m1288.TYPE_LABELS
LEG_LABELS = ("coupon only", "bill only", "both legs", "neither")
STATE_LABELS = ("0 (abundant)", "1 to 2", "3 (scarce)", "no state")
REGIMES = ("2018-19", "2020", "2021-23", "2024", "2025-26")
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
WINDOWS = m1321.WINDOWS
WINDOW_LAST = m1321.WINDOW_LAST
EFFECT_SKILLS = (0.005, 0.01, 0.03)
FAMILY_SIZES = (1, 2, 3)
LOOKS = (125, 250)
POWER_METRICS = ("grid_crps", "upper_tail_twcrps")
EFFECT_ORDER = ("observed", "skill 0.5%", "skill 1.0%", "skill 3.0%", "zero")
POWER_WINDOWS = 40_000
TARGET_POWER = 0.8


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def require_cells_inside_limit(cells: Iterable[dict]) -> None:
    """Refuse a cell whose decision or target day is after the declared last day or in a locked tier.

    Mutation record: replacing `s686.require_scored_days(days, LAST_DAY)` with `s686.require_scored_days([], LAST_DAY)` makes
    `LimitTests.test_a_cell_after_the_last_day_is_refused` fail with `AssertionError` (`LookAheadError not raised`); restored, it passes. (Moving
    the last day by 400 days instead is not caught by this test: every day after 2026-09-03 is in the blind tier, which `lockbox.require_unlocked`
    refuses on its own, so the declared last day and the lockbox agree.)

    Raises:
        LookAheadError: a day after `LAST_DAY`, or in a tier of `metadata/lockbox.json` that has not been opened.
    """

    days = set()
    for x in cells:
        days.add(x["d"])
        days.add(x["t"])
    s686.require_scored_days(days, LAST_DAY)


# -- labels --------------------------------------------------------------------------------------------------------------


def leg_label(f: Mapping[str, object]) -> str:
    """Which leg settles on a target day: coupon only, bill only, both, neither."""

    if f["coupon"] and f["bill"]:
        return LEG_LABELS[2]
    if f["coupon"]:
        return LEG_LABELS[0]
    if f["bill"]:
        return LEG_LABELS[1]
    return LEG_LABELS[3]


def type_labels(f: Mapping[str, object]) -> List[str]:
    """The settlement-day types a target day belongs to (a day can be a coupon and a bill day)."""

    out: List[str] = []
    if f["coupon"]:
        out.append(TYPE_LABELS[0])
    if f["bill"]:
        out += [TYPE_LABELS[1], TYPE_LABELS[2] if f["cmb"] else TYPE_LABELS[3]]
    if not f["coupon"] and not f["bill"]:
        out.append(TYPE_LABELS[4])
    return out


def state_label(state: Optional[float]) -> str:
    if state is None:
        return STATE_LABELS[3]
    return STATE_LABELS[0] if state < 0.5 else STATE_LABELS[2] if state > 2.5 else STATE_LABELS[1]


# -- readings ------------------------------------------------------------------------------------------------------------


def reading(interval: Optional[Sequence[float]]) -> str:
    """A difference d is the arm less the reference, so above zero is a loss for the arm, below zero a gain."""

    if interval is None:
        return "not read"
    low, high = interval
    if low > 0.0:
        return "loss"
    if high < 0.0:
        return "gain"
    return "undecided"


def read_h_f(settle: Optional[Sequence[float]], neither: Optional[Sequence[float]], event: Optional[Sequence[float]]) -> str:
    """H-f (the declaration's rule). The three arguments are the 90% intervals of mean d on the Brier score over the settlement-day target
    cells, the neither-settles cells and the cells where the spread exceeded +5 bp."""

    if settle is None:
        return "not read"
    settle_gain = settle[1] < 0.0
    neither_gain = neither is not None and neither[1] < 0.0
    event_gain = event is not None and event[1] < 0.0
    if settle_gain and not neither_gain and event_gain:
        return "supported"
    if neither_gain and not settle_gain:
        return "not supported"
    return "undecided"


def read_h_g(shift: Optional[Sequence[float]], premium: Optional[Sequence[float]], bias: Optional[Sequence[float]], loss: str) -> str:
    """H-g. `shift`, `premium` and `bias` are intervals (bp); `loss` is the reading of the 2020 settlement-day grid CRPS difference."""

    if shift is None or premium is None or bias is None:
        return "not read"
    above = shift[0] > premium[1]
    if not above or bias[0] <= 0.0 <= bias[1]:
        return "not supported"
    if bias[1] < 0.0 and loss == "loss":
        return "supported"
    return "undecided"


def read_h_h(with_days: str, without_days: str) -> str:
    """H-h. The readings of the 2020 grid CRPS difference with the immediate-release cash management bill days in, and with them left out."""

    if with_days != "loss":
        return "not read"
    if without_days == "not read":
        return "undecided"
    return "supported" if without_days != "loss" else "not supported"


# -- the bootstrap, in parallel ------------------------------------------------------------------------------------------

_PENDING: List[Tuple[dict, str, tuple]] = []


def _job(series):
    n = len(series[0])
    out = metrics.stationary_bootstrap_intervals(
        lambda idx: [sum(s[i] for i in idx) / len(idx) for s in series], n, block_length=BLOCK, seed=SEED, replications=REPS)
    return [list(x) for x in out]


def finish(workers: int) -> None:
    """Run every queued bootstrap in a pool and write each interval list into the row that asked."""

    jobs = [item[2] for item in _PENDING]
    if workers > 1 and len(jobs) > 1:
        with multiprocessing.get_context("fork").Pool(workers) as pool:
            done = pool.map(_job, jobs, chunksize=1)
    else:
        done = [_job(j) for j in jobs]
    for (container, key, _), result in zip(_PENDING, done):
        container[key] = result
    _PENDING.clear()


def resolve_intervals(node) -> None:
    """After `finish`: move each row's `_intervals` list into its metric entries and add the readings."""

    if isinstance(node, dict):
        if "_intervals" in node:
            for metric, interval in zip(METRICS, node.pop("_intervals")):
                node[metric]["interval"] = interval
                node[metric]["reading"] = reading(interval)
        for metric in METRICS:
            entry = node.get(metric)
            if isinstance(entry, dict) and "mean_d" in entry and "reading" not in entry:
                entry["interval"] = None
                entry["reading"] = reading(None)
        for v in node.values():
            resolve_intervals(v)
    elif isinstance(node, list):
        for v in node:
            resolve_intervals(v)


# -- the difference rows -------------------------------------------------------------------------------------------------


def _units(cells: Sequence[dict], unit: str) -> Dict[object, List[dict]]:
    out: Dict[object, List[dict]] = {}
    for x in cells:
        out.setdefault(x[unit], []).append(x)
    return out


def diff_row(cells: Sequence[dict], arm: str, ref: str, unit: str, total: Optional[Sequence[dict]] = None) -> dict:
    """The arm against the reference over `cells`, grain `unit` ('t': target day, 'd': decision day; the leads of a unit averaged).

    Per score: the means of both, mean d (arm less reference: above zero is a loss), its 90% stationary-bootstrap interval over the units in date
    order when there are at least 20, the skill. `share_of_difference` is the sum of d (grid CRPS) over these cells over the sum over `total`.
    """

    units = _units(cells, unit)
    keys = sorted(units)
    row: dict = {"cells": len(cells), "units": len(keys)}
    series = []
    for metric in METRICS:
        arm_u = [sum(x["score"][arm][metric] for x in units[u]) / len(units[u]) for u in keys]
        ref_u = [sum(x["score"][ref][metric] for x in units[u]) / len(units[u]) for u in keys]
        d_u = [a - r for a, r in zip(arm_u, ref_u)]
        series.append(d_u)
        if keys:
            ma, mr = sum(arm_u) / len(keys), sum(ref_u) / len(keys)
            row[metric] = {"mean_arm": ma, "mean_ref": mr, "mean_d": sum(d_u) / len(keys), "skill": (1.0 - ma / mr) if mr else None}
    if total is not None:
        t = sum(x["score"][arm]["grid_crps"] - x["score"][ref]["grid_crps"] for x in total)
        g = sum(x["score"][arm]["grid_crps"] - x["score"][ref]["grid_crps"] for x in cells)
        row["share_of_difference"] = None if abs(t) < 1e-12 else g / t
    if len(keys) >= MIN_UNITS:
        _PENDING.append((row, "_intervals", tuple(series)))
    return row


def group_rows(cells: Sequence[dict], groups: Sequence[Tuple[str, Sequence[dict]]], arm: str, ref: str, unit: str) -> Dict[str, dict]:
    return {label: diff_row(members, arm, ref, unit, total=cells) for label, members in groups if members}


def event_block(cells: Sequence[dict], arm: str, ref: str) -> dict:
    """On the cells where the spread exceeded +5 bp and on the others: the count, the mean predicted probability of each model, and the Brier
    difference summed (arm less reference; below zero favours the arm). `frequency` is the share of cells with the event."""

    out: dict = {"frequency": sum(1 for x in cells if x["event"]) / len(cells) if cells else None}
    for key, members in (("event", [x for x in cells if x["event"]]), ("other", [x for x in cells if not x["event"]])):
        n = len(members)
        out[key] = {
            "cells": n,
            "prob_arm": sum(x["prob"][arm] for x in members) / n if n else None,
            "prob_ref": sum(x["prob"][ref] for x in members) / n if n else None,
            "brier_d_sum": sum(x["score"][arm]["brier_gt5"] - x["score"][ref]["brier_gt5"] for x in members),
        }
    return out


# -- the shift -----------------------------------------------------------------------------------------------------------


def shift_parts(estimate: sc.StateEstimate, flags: Mapping[str, int], extras: Mapping[str, float], scale: float) -> Tuple[float, float]:
    """The fitted settlement shift of (s3c-ann-flagnet) in bp, split in the part its flags carry and the part its nets carry: the standardised shift
    with the nets left out and with the flags set to zero, each times the scale at the anchor. The two add to `sc.standardised_shift` of the whole."""

    zero = {name: 0 for name in flags}
    return (sc.standardised_shift(estimate, flags, None, None, {}) * scale,
            sc.standardised_shift(estimate, zero, None, None, extras) * scale)


# -- the cells -----------------------------------------------------------------------------------------------------------


def release_days(snapshot_dir: Path = m1288.AUCTIONS, path: Path = RELEASE_TIMES) -> Dict[str, List[str]]:
    """The settlement days with an auction whose announcement states no release time ('For Immediate Release', #1301), all and cash management bills."""

    stated = json.loads(Path(path).read_text(encoding="utf-8"))["stated"]
    files = sorted(p for p in Path(snapshot_dir).glob("*.json") if not p.name.endswith(".manifest.json"))
    records = json.loads(files[0].read_text(encoding="utf-8"))["data"]
    every, cmb = set(), set()
    for r in records:
        if stated.get(r["pdf_filenm_announcemt"]) == "immediate":
            every.add(r["issue_date"])
            if r["cash_management_bill_cmb"] == "Yes":
                cmb.add(r["issue_date"])
    return {"all": sorted(every), "cmb": sorted(cmb)}


def assemble(frame, walks, tables, panel, auctions, states, immediate, last: date) -> Tuple[List[dict], dict]:
    """One dict per (decision day, lead) of `frame`: the outcome, the scores, the probabilities of the four models, the day types, the scarcity state and
    the flagnet's fitted settlement shift split in its flag and net parts. Also the cell tables, for the reproduction check."""

    term_table, _net_table, size_terms = tables
    cell_scores = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    facts = m1288.settlement_facts(panel, auctions)
    new = walks["new"]
    name = s3c_announced.FLAGNET_ARM.name
    out: List[dict] = []
    for d in frame.days:
        i = frame.position[d]
        scale = float(new.detail[d]["scale"])
        estimate_of = new.estimates[new.fit_used[d]][name]
        for h in LEADS:
            t = frame.target(d, h)
            f = facts[t]
            flag_part, net_part = shift_parts(estimate_of[h], term_table.read(h, i), size_terms.read(h, i), scale)
            out.append({
                "d": d, "t": t, "h": h, "y": frame.outcome[t], "regime": frame.regime(t), "month": t.month,
                "settle": bool(f["coupon"] or f["bill"]), "types": type_labels(f), "leg": leg_label(f),
                "immediate": t.isoformat() in immediate["all"], "immediate_cmb": t.isoformat() in immediate["cmb"],
                "state": state_label(states.get(d)), "event": bool(data.exceeds_bp(frame.outcome[t], TAU)),
                "score": {m: {metric: cell_scores[m][metric][(d, h)] for metric in METRICS} for m in MODELS},
                "prob": {m: m1273.probability(frame.forecasts[m][d][h]) for m in MODELS},
                "shift_flag_part": flag_part, "shift_net_part": net_part,
            })
    return out, cell_scores


def check_means(here: Mapping[str, float], there: Mapping[str, float], where: str, tolerance: float = 1e-9) -> None:
    """Refuse a mean that is not #1321's record's.

    Raises:
        ValueError: a model's mean differs from the record's by more than `tolerance`.
    """

    for name, value in here.items():
        if abs(value - there[name]) > tolerance:
            raise ValueError(f"{where}: {name} is {value:.12f} here and {there[name]:.12f} in #1321's record: this is not the record's walk")


def reproduce(frame, cell_scores, record: Mapping[str, dict]) -> dict:
    """The pooled, lead and regime means of the four models and the three scores, checked against #1321's record."""

    groups = record["groups"]
    checked = 0
    for metric in METRICS:
        per = {m: cell_scores[m][metric] for m in MODELS}
        pooled = {m: _mean(list(s686.by_decision(per[m]).values())) for m in MODELS}
        check_means(pooled, groups["pooled"]["all decision days"][metric]["means"], f"pooled {metric}")
        for h in LEADS:
            check_means({m: _mean(list(s686.by_lead(per[m], h).values())) for m in MODELS}, groups["lead"][f"h={h}"][metric]["means"],
                        f"lead {h} {metric}")
        for regime in REGIMES:
            if regime not in groups.get("regime", {}):
                continue
            means = {}
            for m in MODELS:
                by_t = s686.by_target(frame, per[m])
                means[m] = _mean([v for t, v in by_t.items() if frame.regime(t) == regime])
            check_means(means, groups["regime"][regime][metric]["means"], f"regime {regime} {metric}")
        checked += 1
    return {"metrics_checked": checked, "tolerance": 1e-9, "equal": True}


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def _close(a, b, tolerance: float = 1e-9) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_close(a[x], b[x], tolerance) for x in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_close(x, y, tolerance) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= tolerance
    return a == b


# -- the groups ----------------------------------------------------------------------------------------------------------


def settle_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [("any settlement", [x for x in cells if x["settle"]]), ("neither settles", [x for x in cells if not x["settle"]])]


def type_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [(label, [x for x in cells if label in x["types"]]) for label in TYPE_LABELS]


def leg_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [(label, [x for x in cells if x["leg"] == label]) for label in LEG_LABELS]


def regime_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [(r, [x for x in cells if x["regime"] == r]) for r in REGIMES]


def month_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [(MONTHS[m - 1], [x for x in cells if x["month"] == m]) for m in range(1, 13)]


def state_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [(s, [x for x in cells if x["state"] == s]) for s in STATE_LABELS]


def lead_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    return [(f"h={h}", [x for x in cells if x["h"] == h]) for h in LEADS]


def year_month_groups(cells: Sequence[dict]) -> List[Tuple[str, List[dict]]]:
    keys = sorted({x["t"].strftime("%Y-%m") for x in cells})
    return [(key, [x for x in cells if x["t"].strftime("%Y-%m") == key]) for key in keys]


# -- the tables ----------------------------------------------------------------------------------------------------------


def table_1(cells: Sequence[dict], arm: str, ref: str, *, full: bool) -> dict:
    """Where the difference of the arm against the reference sits."""

    out = {
        "pooled": diff_row(cells, arm, ref, "d"),
        "lead": group_rows(cells, lead_groups(cells), arm, ref, "d"),
        "settlement": group_rows(cells, settle_groups(cells), arm, ref, "t"),
        "type": group_rows(cells, type_groups(cells), arm, ref, "t"),
        "leg": group_rows(cells, leg_groups(cells), arm, ref, "t"),
        "regime": group_rows(cells, regime_groups(cells), arm, ref, "t"),
        "state": group_rows(cells, state_groups(cells), arm, ref, "d"),
        "event_probabilities": event_block(cells, arm, ref),
        "event_rows": group_rows(cells, [("event: spread above +5 bp", [x for x in cells if x["event"]]),
                                         ("no event", [x for x in cells if not x["event"]])], arm, ref, "t"),
    }
    if full:
        out["month"] = group_rows(cells, month_groups(cells), arm, ref, "t")
        out["settlement_by_regime"] = {r: group_rows(members, settle_groups(members), arm, ref, "t") for r, members in regime_groups(cells) if members}
    return out


def table_2(cells: Sequence[dict], arm: str, ref: str) -> dict:
    """The 2020 difference of the arm against the reference."""

    y = [x for x in cells if x["regime"] == "2020"]
    if not y:
        return {}
    cmb_days = [x for x in y if x["immediate_cmb"]]
    imm_days = [x for x in y if x["immediate"]]
    return {
        "all_2020": diff_row(y, arm, ref, "t"),
        "month": group_rows(y, [(MONTHS[m - 1], [x for x in y if x["month"] == m]) for m in range(1, 13)], arm, ref, "t"),
        "march_to_june": group_rows(y, [("March to June", [x for x in y if 3 <= x["month"] <= 6]),
                                        ("rest of 2020", [x for x in y if not 3 <= x["month"] <= 6])], arm, ref, "t"),
        "state": group_rows(y, state_groups(y), arm, ref, "d"),
        "type": group_rows(y, type_groups(y), arm, ref, "t"),
        "leg": group_rows(y, leg_groups(y), arm, ref, "t"),
        "settlement": group_rows(y, settle_groups(y), arm, ref, "t"),
        "settlement_leads_2_5": diff_row([x for x in y if x["settle"] and x["h"] >= 2], arm, ref, "t"),
        "immediate_cmb": {
            "in": diff_row(cmb_days, arm, ref, "t", total=y) if cmb_days else None,
            "left_out": diff_row([x for x in y if not x["immediate_cmb"]], arm, ref, "t"),
            "target_days": len({x["t"] for x in cmb_days}),
        },
        "immediate_any": {
            "in": diff_row(imm_days, arm, ref, "t", total=y) if imm_days else None,
            "left_out": diff_row([x for x in y if not x["immediate"]], arm, ref, "t"),
            "target_days": len({x["t"] for x in imm_days}),
        },
    }


def table_3(cells: Sequence[dict], shift_rows: Sequence[dict], reps: int) -> dict:
    """#1321's table of the fitted settlement shift against the realised premium (called as merged), and the flagnet's shift split in its parts."""

    out = {"later": m1321.shift_against_premium(shift_rows, m1321.LEADS[1:], reps), "lead1": m1321.shift_against_premium(shift_rows, m1321.LEADS[:1], reps)}
    parts: Dict[str, dict] = {}
    for key, leads in (("later", m1321.LEADS[1:]), ("lead1", m1321.LEADS[:1])):
        by_regime: Dict[str, dict] = {}
        for label, members in [("all", list(cells))] + regime_groups(cells):
            on = [x for x in members if x["settle"] and x["h"] in leads]
            if on:
                by_regime[label] = {"cells": len(on), "flag_part": _mean([x["shift_flag_part"] for x in on]),
                                    "net_part": _mean([x["shift_net_part"] for x in on])}
        parts[key] = by_regime
    out["parts"] = parts
    return out


def hypotheses(r: Mapping[str, object]) -> dict:
    """The three readings, from the development window only."""

    dev = r["windows"]["development"]
    t1 = dev["table_1"]
    settle = t1["settlement"]
    f_in = lambda row: None if row is None else row["brier_gt5"].get("interval")  # noqa: E731
    h_f = read_h_f(f_in(settle.get("any settlement")), f_in(settle.get("neither settles")), f_in(t1["event_rows"].get("event: spread above +5 bp")))
    t3 = dev["table_3"]["later"]["by_regime"].get("2020", {})
    shift = (t3.get(FLAGNET) or {}).get("shift", {}).get("interval")
    premium = (t3.get("premium") or {}).get("interval")
    bias = (t3.get(FLAGNET) or {}).get("bias", {}).get("interval")
    t2 = dev["table_2_annnet"]
    loss_row = t2.get("settlement_leads_2_5") or {}
    loss = (loss_row.get("grid_crps") or {}).get("reading", "not read")
    h_g = read_h_g(shift, premium, bias, loss)
    out = {"H-f": h_f, "H-g": h_g}
    for ref_key, table in (("annnet", dev["table_2_annnet"]), ("ann", dev["table_2_ann"])):
        cmb = table.get("immediate_cmb", {})
        w = (table.get("all_2020") or {}).get("grid_crps", {}).get("reading", "not read")
        wo = ((cmb.get("left_out") or {}).get("grid_crps") or {}).get("reading", "not read")
        out[f"H-h against {ref_key}"] = read_h_h(w, wo)
    return out


# -- the power -----------------------------------------------------------------------------------------------------------


def daily_difference(cells: Sequence[dict], metric: str, *, first: date, arm: str = FLAGNET, ref: str = ANNNET) -> Dict[date, float]:
    """The daily difference d = score(reference) - score(arm) per decision day from `first`, the leads averaged: positive favours the arm."""

    sums: Dict[date, List[float]] = {}
    for x in cells:
        if x["d"] >= first:
            sums.setdefault(x["d"], []).append(x["score"][ref][metric] - x["score"][arm][metric])
    return {d: _mean(v) for d, v in sums.items()}


def window_statistics(series: Sequence[float], *, days: int, windows: int, seed: int) -> List[Tuple[float, float]]:
    """`(mean, Newey-West standard error)` of `windows` windows of `days` days drawn as the protocol draws them (circular blocks of 10, seed `seed`)
    from the series centred at its mean. A shift of the series moves each window's mean and leaves its standard error where it is, so one draw
    serves every effect size."""

    values = [float(v) for v in series]
    mean = _mean(values)
    centred = [v - mean for v in values]
    rng = random.Random(seed)
    out = []
    for _ in range(windows):
        window = [centred[i] for i in sp._window_indices(len(centred), days, rng, sp.WINDOW_BLOCK)]
        out.append((sum(window) / days, sp._standard_error(window, sp.HAC_LAG, "a window")))
    return out


def critical_value(stats: Sequence[Tuple[float, float]], level: float) -> float:
    """The `1 - level` quantile of the studentized means of the windows of a centred series: the value a bound `mean - c * se` must clear."""

    ordered = sorted(m / s for m, s in stats)
    return ordered[min(len(ordered) - 1, int((1.0 - level) * len(ordered)))]


def power_at(stats: Sequence[Tuple[float, float]], value: float, delta: float) -> float:
    """The share of windows whose studentized mean, shifted by a true effect `delta`, exceeds `value`."""

    return sum(1 for m, s in stats if (m + delta) / s > value) / len(stats)


def days_needed(sigma: float, delta: float, level: float, power: float = TARGET_POWER) -> Optional[float]:
    """Days for a one-sided test at `level` to reach `power` at a true effect `delta`, with `sigma` the long-run standard deviation of a daily
    difference: `((z(1 - level) + z(power)) * sigma / delta) ** 2`; `None` when the effect is not positive."""

    if delta <= 0.0:
        return None
    normal = NormalDist()
    return ((normal.inv_cdf(1.0 - level) + normal.inv_cdf(power)) * sigma / delta) ** 2


def power_study(cells: Sequence[dict], windows: int) -> dict:
    """The declared power read of the prospective comparison: the arm against the candidate on the development series from `POST_COVID_FROM`."""

    out: dict = {"from": POST_COVID_FROM.isoformat(), "windows": windows, "seed": SEED, "looks": list(LOOKS), "families": list(FAMILY_SIZES),
                 "levels": {str(m): list(sp.nominal_levels(alpha=sp.ALPHA / m)) for m in FAMILY_SIZES}, "metrics": {}}
    for metric in POWER_METRICS:
        series = daily_difference(cells, metric, first=POST_COVID_FROM)
        days = sorted(series)
        values = [series[d] for d in days]
        score_ref = _mean([_mean([x["score"][ANNNET][metric] for x in cells if x["d"] == d]) for d in days])
        observed = _mean(values)
        sigma = math.sqrt(sp._long_run_variance(values, sp.HAC_LAG))
        effects = {"zero": 0.0, "observed": observed}
        for s in EFFECT_SKILLS:
            effects[f"skill {100 * s:.1f}%"] = s * score_ref
        entry: dict = {"days": len(values), "first": days[0].isoformat(), "last": days[-1].isoformat(), "mean_d": observed,
                       "mean_score_reference": score_ref, "observed_skill": observed / score_ref, "long_run_sd": sigma,
                       "effects": effects, "looks": {}}
        for look in LOOKS:
            stats = window_statistics(values, days=look, windows=windows, seed=SEED)
            per_family = {}
            for m in FAMILY_SIZES:
                level = sp.nominal_levels(alpha=sp.ALPHA / m)[sp.CHECKPOINTS.index(look)]
                cv = critical_value(stats, level)
                per_family[str(m)] = {
                    "level": level, "critical_value": cv, "tail_windows": max(1, int(level * windows)),
                    "power": {name: power_at(stats, cv, delta) for name, delta in effects.items()},
                    "days_needed": {name: days_needed(sigma, delta, level) for name, delta in effects.items()},
                }
            entry["looks"][str(look)] = per_family
        out["metrics"][metric] = entry
    return out


# -- the run -------------------------------------------------------------------------------------------------------------


def run_window(window: str, panel, splits, registry, table, register, results, auctions, states, immediate, args, record: Optional[dict]) -> dict:
    frame, notes, walks, tables, _groups = m1321.build(window, panel, splits, registry, table, register, results, auctions, args.first)
    last = WINDOW_LAST[window]
    cells, cell_scores = assemble(frame, walks, tables, panel, auctions, states, immediate, last)
    require_cells_inside_limit(cells)
    full = window == WINDOWS[0]
    facts = m1288.settlement_facts(panel, auctions)
    shift_rows = m1321.shift_cells(frame, walks, tables, facts)
    result: dict = {"notes": notes, "cells": len(cells), "decision_days": len({x["d"] for x in cells}), "table_1": table_1(cells, FLAGNET, ANNNET, full=full),
                    "table_3": table_3(cells, shift_rows, args.reps)}
    if record is not None:
        result["reproduction"] = reproduce(frame, cell_scores, record)
        result["reproduction"]["shift_table_equal"] = _close(
            {key: json.loads(json.dumps(result["table_3"][key])) for key in ("later", "lead1")},
            {key: record["shift_against_premium"][key] for key in ("later", "lead1")}, 1e-6)
        if not result["reproduction"]["shift_table_equal"]:
            raise ValueError(f"{window}: the fitted-shift table is not #1321's record's")
    if full:
        result["table_1_vs_ann"] = table_1(cells, FLAGNET, ANN, full=False)
        result["table_1_annnet_vs_ann"] = table_1(cells, ANNNET, ANN, full=False)
        result["table_2_annnet"] = table_2(cells, FLAGNET, ANNNET)
        result["table_2_ann"] = table_2(cells, FLAGNET, ANN)
        result["table_2_annnet_vs_ann"] = table_2(cells, ANNNET, ANN)
        result["table_2_vs_s3c"] = table_2(cells, FLAGNET, S3C)
        result["immediate_release"] = {"target_days_all": len(immediate["all"]), "target_days_cmb": len(immediate["cmb"])}
        result["_cells"] = cells
    return result


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with m1321.decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in m1321.load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_flagnet_diagnosis_1344")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    states = k.d1145.decision_states(c.SOURCES)
    immediate = release_days()
    record = json.loads(RECORD_1321.read_text(encoding="utf-8")) if args.first is None else None
    result: dict = {
        "issue": 1344, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha, "decision_time": c.DECISION_TIME.strftime("%H:%M"),
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict", "seed": SEED, "reps": args.reps,
        "block": BLOCK, "amendments": declaration["amendments"], "reading_rules": declaration["reading_rules"], "windows": {},
    }
    cells_dev: List[dict] = []
    for window in WINDOWS:
        r = run_window(window, panel, splits, registry, table, register, results, auctions, states, immediate, args, None if record is None else record["windows"][window])
        cells_dev = r.pop("_cells", cells_dev)
        result["windows"][window] = r
    finish(args.workers)
    resolve_intervals(result)
    result["hypotheses"] = hypotheses(result)
    result["power"] = power_study(cells_dev, args.power_windows)
    result["draft"] = json.loads(DRAFT.read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def _pct(x: Optional[float], digits: int = 1) -> str:
    return "n/a" if x is None else f"{100.0 * x:+.{digits}f}%"


def _iv(interval: Optional[Sequence[float]], digits: int = 3) -> str:
    return "no interval" if not interval else f"[{interval[0]:+.{digits}f}, {interval[1]:+.{digits}f}]"


def _cell(row: Optional[dict], metric: str) -> str:
    if not row or metric not in row:
        return "n/a"
    e = row[metric]
    return f"skill {_pct(e['skill'])}; d {e['mean_d']:+.4f} {_iv(e.get('interval'), 4)}: **{e.get('reading', 'not read')}**"


def diff_table(rows: Mapping[str, dict], first: str = "group") -> List[str]:
    out = [f"| {first} | cells | units | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | share of the grid CRPS difference |", "|---|---|---|---|---|---|---|"]
    for label, row in rows.items():
        share = row.get("share_of_difference")
        out.append(f"| {label} | {row['cells']:,} | {row['units']:,} | {_cell(row, 'grid_crps')} | {_cell(row, 'upper_tail_twcrps')} | "
                   f"{_cell(row, 'brier_gt5')} | {'n/a' if share is None else _pct(share, 0)} |")
    return out


def event_table(block: Mapping[str, object]) -> List[str]:
    out = ["| set | cells | mean P(> +5 bp), arm | reference | Brier difference summed (arm less reference) |", "|---|---|---|---|---|"]
    for key, label in (("event", "spread above +5 bp"), ("other", "no event")):
        e = block[key]
        out.append(f"| {label} | {e['cells']:,} | {e['prob_arm']:.3f} | {e['prob_ref']:.3f} | {e['brier_d_sum']:+.2f} |")
    out.append(f"\nObserved frequency of the event over these cells: {100.0 * block['frequency']:.1f}%.")
    return out


def _value(entry: Optional[Mapping[str, object]]) -> str:
    """A fitted statistic with its interval: `+1.31 [+0.86, +1.85]`; the value alone when it has no interval (a regime of fewer than 20 days)."""

    if not entry:
        return "n/a"
    if entry.get("interval"):
        return f"{entry['value']:+.2f} {_iv(entry['interval'], 2)}"
    return f"{entry['value']:+.2f}"


def shift_table(block: Mapping[str, object], parts: Mapping[str, dict]) -> List[str]:
    out = ["| regime | decision days | realised premium (bp) | (s3c-ann) shift | (s3c-ann-net) shift | (s3c-ann-flagnet) shift | of it, flags | of it, nets | "
           "flagnet bias |", "|---|---|---|---|---|---|---|---|---|"]
    for regime in block["regimes"]:
        r = block["by_regime"][regime]
        p = parts.get(regime)
        flag_part = "n/a" if not p else f"{p['flag_part']:+.2f}"
        net_part = "n/a" if not p else f"{p['net_part']:+.2f}"
        out.append(
            f"| {regime} | {r['decision_days']:,} | {_value(r.get('premium'))} | {_value((r.get(ANN) or {}).get('shift'))} | "
            f"{_value((r.get(ANNNET) or {}).get('shift'))} | {_value((r.get(FLAGNET) or {}).get('shift'))} | {flag_part} | {net_part} | "
            f"{_value((r.get(FLAGNET) or {}).get('bias'))} |")
    return out


def power_tables(power: Mapping[str, object]) -> List[str]:
    out: List[str] = []
    for metric, entry in power["metrics"].items():
        out += [f"**{METRIC_TITLES[metric]}.** {entry['days']:,} decision days from {entry['first']} to {entry['last']}; mean d {entry['mean_d']:+.4f} "
                f"(skill {_pct(entry['observed_skill'], 2)} of the candidate's mean score {entry['mean_score_reference']:.3f}); long-run standard deviation of a daily difference "
                f"{entry['long_run_sd']:.3f}.", ""]
        names = [n for n in EFFECT_ORDER if n in entry["effects"]]
        out += ["| look (days) | family size | nominal level | critical value | " + " | ".join(f"power at {n}" for n in names) + " |",
                "|---|---|---|---|" + "---|" * len(names)]
        for look, per in entry["looks"].items():
            for m, v in per.items():
                out.append(f"| {look} | {m} | {v['level']:.4f} | {v['critical_value']:.2f} | " + " | ".join(f"{100 * v['power'][n]:.1f}%" for n in names) + " |")
        positive = [n for n in names if n != "zero"]
        out += ["", "Days a one-sided test at the final look's level needs for 80% power (analytic, long-run variance), by effect:", "",
                "| family size | " + " | ".join(positive) + " |", "|---|" + "---|" * len(positive)]
        for m, v in entry["looks"][str(LOOKS[-1])].items():
            cells = []
            for n in positive:
                days = v["days_needed"][n]
                cells.append("never (effect not positive)" if days is None else f"{days:,.0f}")
            out.append(f"| {m} | " + " | ".join(cells) + " |")
        out.append("")
    return out


def answers(r: Mapping[str, object]) -> List[str]:
    dev = r["windows"]["development"]
    t1, h = dev["table_1"], r["hypotheses"]
    settle = t1["settlement"]
    ev = t1["event_probabilities"]
    reg = t1["regime"]
    cmb = dev["table_2_annnet"].get("immediate_cmb", {})
    s20 = dev["table_3"]["later"]["by_regime"].get("2020", {})
    out = [
        "## Answers (development window; diagnostic intervals; readings from the interval on mean d)", "",
        f"1. **Where the Brier gain sits (H-f: {h['H-f']}).** Against (s3c-ann-net), over the settlement-day target cells the Brier difference is "
        f"{_cell(settle.get('any settlement'), 'brier_gt5')}; over the neither-settles cells {_cell(settle.get('neither settles'), 'brier_gt5')}. "
        f"Summed over the cells where the spread went above +5 bp it is {ev['event']['brier_d_sum']:+.2f} (mean P(> +5 bp) {ev['event']['prob_arm']:.3f} against "
        f"the candidate's {ev['event']['prob_ref']:.3f}), over the others {ev['other']['brier_d_sum']:+.2f}. By regime: 2018-19 {_cell(reg.get('2018-19'), 'brier_gt5')}; "
        f"2020 {_cell(reg.get('2020'), 'brier_gt5')}.",
        f"2. **The 2020 loss (H-g, an over-shift: {h['H-g']}).** At leads 2 to 5 in 2020 the realised settlement-day premium is {_value(s20.get('premium'))} bp; the fitted "
        f"settlement shift is {_value((s20.get(ANNNET) or {}).get('shift'))} for (s3c-ann-net) and {_value((s20.get(FLAGNET) or {}).get('shift'))} for (s3c-ann-flagnet); the "
        f"flagnet's settlement-day bias (error on settlement days less the others; negative: forecast too high) is {_value((s20.get(FLAGNET) or {}).get('bias'))}. "
        f"The 2020 grid CRPS difference on settlement-day targets at leads 2 to 5: {_cell(dev['table_2_annnet'].get('settlement_leads_2_5'), 'grid_crps')}.",
        f"3. **The immediate-release cash management bill days (H-h against (s3c-ann-net): {h['H-h against annnet']}; against (s3c-ann): {h['H-h against ann']}).** The 2020 "
        f"grid CRPS difference with those days in: {_cell((dev['table_2_annnet'].get('all_2020')), 'grid_crps')}; with them left out: "
        f"{_cell((cmb.get('left_out')), 'grid_crps')}. They are {cmb.get('target_days', 0)} of the 2020 target days.", ""]
    return out


def question(r: Optional[dict] = None) -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. Register (s3c-ann-flagnet) beside the candidate for the prospective confirmation days?** The draft declaration "
        "(`metadata/s3c_flagnet_prospective_draft_1344.json`) is drafted, not registered. Registering it is her GitHub action, `GO #1344`; the "
        "candidate (s3c-ann-net) does not change.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Do not register; keep the draft on file (default).** Nothing is scored on the confirmation days for the arm.",
        "2. **Register the arm as a secondary candidate as drafted**, compared with the candidate head to head as a reported comparison with no rule, "
        "and tested against B1 and B2 under the protocol's rule with Holm across the secondaries and the key secondary metric.",
        "3. **Register it, but read the comparison with the candidate on the Brier score of P(> +5 bp) as well**, as a further reported comparison "
        "(no decision rule), because that is where the development gain sits.", "",
        "**Question 2 of #1326 (the announcement dating in published declarations)** keeps its default: off. Nothing here asks for it.", ""]


def render(r: dict) -> str:
    dev, y26 = r["windows"]["development"], r["windows"]["2026"]
    lines: List[str] = [
        "# (s3c-ann-flagnet): where it gains, why it loses in 2020, and a draft prospective test (#1344)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3, the arm (s3c-ann-flagnet) beside the candidate (s3c-ann-net); her ruling of 1 November 2026 "
        "(ledger item 95, on #1326 question 1): test and diagnose the better arm. **Development data, not a verdict** (scoring protocol v1, #640). "
        "Nothing is registered or published; (s3c-ann-net) stays the candidate.", "",
        f"Panel digest `{r['panel_sha256']}` (built at the {r['decision_time']} decision instant). The walks are #1321's, rebuilt as merged and checked against "
        f"its record: every pooled, lead and regime mean of the four models equals it to 1e-9 and the fitted-shift table equals it "
        f"({dev.get('reproduction', {}).get('equal', 'not checked on a subset')}). Diagnostic intervals: 90% stationary bootstrap, block 10, {r['reps']} replications, "
        f"seed {r['seed']}, over the units of each group; they are not the protocol's studentized test, whose figures are #1321's. d is the arm less the reference, so "
        "below zero is a gain for the arm. The days of a group are resampled in date order as if consecutive (#1221).", ""]
    lines += answers(r)
    lines += ["## Readings of the declared hypotheses", "", "| hypothesis | reading |", "|---|---|"]
    for key, value in r["hypotheses"].items():
        lines.append(f"| {key} | **{value}** |")
    lines += ["", "## Table 1. Where (s3c-ann-flagnet) differs from (s3c-ann-net), development window", "",
              "**Pooled** (grain: the decision day, the five leads averaged)", ""] + diff_table({"pooled": dev["table_1"]["pooled"]}) + [""]
    for key, title, first in (("lead", "By lead", "lead"), ("settlement", "By whether a leg settles on the target day", "target day"),
                              ("type", "By settlement-day type of the target day", "type"), ("leg", "By leg", "leg"),
                              ("regime", "By regime of the target day", "regime"), ("month", "By calendar month of the target day", "month"),
                              ("state", "By the scarcity state of the decision day", "state"), ("event_rows", "By realised event", "set")):
        lines += [f"**{title}**", ""] + diff_table(dev["table_1"][key], first) + [""]
    lines += ["**The probabilities and the Brier difference by realised event**", ""] + event_table(dev["table_1"]["event_probabilities"]) + [""]
    lines += ["**Settlement-day cells against the rest, by regime**", ""]
    for regime, rows in dev["table_1"]["settlement_by_regime"].items():
        lines += [f"*{regime}*", ""] + diff_table(rows, "target day") + [""]
    lines += ["**Against (s3c-ann) (the flag) and (s3c-ann-net) against (s3c-ann), pooled and by regime**", "",
              "(s3c-ann-flagnet) against (s3c-ann):", ""] + diff_table({"pooled": dev["table_1_vs_ann"]["pooled"], **dev["table_1_vs_ann"]["regime"]}, "group") + [
              "", "(s3c-ann-net) against (s3c-ann):", ""] + diff_table({"pooled": dev["table_1_annnet_vs_ann"]["pooled"], **dev["table_1_annnet_vs_ann"]["regime"]}, "group") + [""]
    lines += ["## Table 2. The 2020 difference", ""]
    for key, title in (("table_2_annnet", "(s3c-ann-flagnet) against (s3c-ann-net)"), ("table_2_ann", "(s3c-ann-flagnet) against (s3c-ann)"),
                       ("table_2_annnet_vs_ann", "(s3c-ann-net) against (s3c-ann), as #1320 read it"), ("table_2_vs_s3c", "(s3c-ann-flagnet) against (s3c)")):
        t = dev[key]
        if not t:
            lines += [f"### {title}", "", "No cell of this regime in the days run (a subset run only).", ""]
            continue
        lines += [f"### {title}", "", "**All of 2020, and March to June against the rest**", ""] + diff_table(
            {"2020": t["all_2020"], **t["march_to_june"]}, "group") + ["", "**By month of the target day**", ""] + diff_table(t["month"], "month") + [
            "", "**By settlement-day type, by leg, and by the scarcity state of the decision day**", ""] + diff_table(
            {**t["settlement"], **t["type"], **t["leg"], **{f"state {k}": v for k, v in t["state"].items()}}, "group") + [""]
        im = t["immediate_cmb"]
        lines += ["**The immediate-release cash management bill days** (an auction with no stated release time settles on the target day, #1301)", ""]
        rows = {"in them": im["in"], "2020 with them left out": im["left_out"]}
        lines += diff_table({k: v for k, v in rows.items() if v}, "group") + [f"\nTarget days: {im['target_days']}.", ""]
        ia = t["immediate_any"]
        rows = {"any immediate-release day": ia["in"], "2020 with them all left out": ia["left_out"]}
        lines += diff_table({k: v for k, v in rows.items() if v}, "group") + [f"\nTarget days: {ia['target_days']}.", ""]
    lines += ["## Table 3. The fitted settlement shift against the realised settlement-day premium (bp)", "",
              "Called from #1321 as merged (decision-day bootstrap, seed 1321); the flag and net parts are added here and carry no interval.", "",
              "**Leads 2 to 5**", ""] + shift_table(dev["table_3"]["later"], dev["table_3"]["parts"]["later"]) + [
              "", "**Lead 1**", ""] + shift_table(dev["table_3"]["lead1"], dev["table_3"]["parts"]["lead1"]) + [""]
    lines += ["## The 2026 development days (decide nothing; cells #1321 already scored, split further)", "",
              "**Pooled, and by whether a leg settles**", ""] + diff_table({"pooled": y26["table_1"]["pooled"], **y26["table_1"]["settlement"]}, "group") + [
              "", "**By settlement-day type**", ""] + diff_table(y26["table_1"]["type"], "type") + [
              "", "**By lead**", ""] + diff_table(y26["table_1"]["lead"], "lead") + [
              "", "**By realised event**", ""] + diff_table(y26["table_1"]["event_rows"], "set") + [""] + event_table(y26["table_1"]["event_probabilities"]) + [""]
    lines += ["## Power of the prospective comparison (development series; descriptive)", "",
              f"d = score of (s3c-ann-net) less score of (s3c-ann-flagnet) per decision day, positive favouring the arm, from {r['power']['from']}; "
              f"{r['power']['windows']:,} windows of the look's length (circular blocks of 10, seed {r['power']['seed']}), the protocol's Newey-West lag 10. "
              "Critical values are calibrated on this series at the nominal level of the look (`scoring_protocol.nominal_levels`, alpha 0.05 spent over 60, 125 and 250 days; "
              "look 60 checks futility only) and, for a family of m, at alpha/m. Each look is read on its own. The Monte Carlo error of a power is at most "
              f"{100 * 0.5 / math.sqrt(r['power']['windows']):.1f} points (the tail of the strictest level rests on a few dozen windows, so those are rougher).", ""]
    lines += power_tables(r["power"])
    d = r["draft"]
    lines += ["## The draft prospective declaration (drafted, not registered)", "",
              f"`metadata/s3c_flagnet_prospective_draft_1344.json`: {d['status']}", "",
              f"- **What it adds:** {d['arm']['definition']}", f"- **The candidate:** {d['candidate']['statement']}",
              f"- **Days:** {d['days']['statement']}", f"- **Scoring:** {d['scoring']['statement']}",
              f"- **Multiplicity:** {d['multiplicity']['statement']}", f"- **Power:** {d['power']['statement']}",
              f"- **Registration:** {d['registration']['statement']}", ""]
    lines += question(r)
    lines += ["## What this does and does not show", "",
              "It shows where, in the development data, the flagnet's differences from the candidate sit, and what a prospective comparison of the two could resolve. "
              "It does not show that either arm is better: the days were seen, the 2026 days were seen by #845, #151, #1229, #1255, #1273, #1288 and #1321, intervals of a group of "
              "target days keep the method that #1221 questions, and the bill leg and the net bill carry Lens E's caveat on the 12:00 announcement time of a cash management bill "
              "(item G). The mechanisms named are readings of the tables; no arm was run to test them. Nothing is a verdict.", ""]
    return "\n".join(lines).rstrip() + "\n"


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="rebuild #1321's walks, split the flagnet's differences, read the three hypotheses and the power")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the intervals")
    s.add_argument("--power-windows", type=int, default=POWER_WINDOWS)
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
