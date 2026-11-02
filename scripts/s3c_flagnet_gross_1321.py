"""(s3c-ann-flagnet) and (s3c-ann-gross): two arms on avenue #1318 beside the candidate (s3c-ann-net), made at the 18:00 decision instant
(#1321; H5 step 3; her ruling of 30 October 2026, ledger item 81; diagnosis #1320).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_flagnet_gross_1321.json`, which this script refuses to read unless it is committed and unchanged. The arms are
`repo_model.s3c_announced`: (s3c-ann-flagnet), (s3c-ann)'s two announced flags with #1273's announced net beside each; and (s3c-ann-gross), the
coupon leg sized by the announced gross offering and the bill leg the announced flag, each capped as (s3c) is capped
(`repo_model.s3c_candidate`, unchanged). The references (s3c), (s3c-ann) and (s3c-ann-net) are re-run in the same run, at 18:00
(`repo_model.decision_instant`); nothing of #1288's record (made at 16:00) is edited, and the pooled means of #1288 are shown beside the re-run
ones for the move in the instant only. The frames and the machinery are #1255's, #1273's and #1288's and are loaded as they are: the development
window of #1145 and #1241 (targets up to 2025-12-31) and the 2026 development days of #1229 (targets 2026-01-02 to 2026-09-03, the near-blind tier
open since GO #151). The blind tier and every lockbox day are refused by the frames' own guards.

It measures grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009
ruling) with the skill interval beside, split by lead, regime, pressure-day type and the settlement-day type of the target at each lead; reports the
coverage of the central 90% band; and reports each arm's fitted settlement shift against the realised settlement-day premium by regime
(the table 4b of #1320) and the fitted effect of the settlement terms by lead and regime.

Commands, from a clone of the branch (the walks are minutes, the paired tests the longer part; a cloud run unless the measured time says
otherwise):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_flagnet_gross_1321.py score --panel PUB.csv \\
        --output docs/research/s3c-flagnet-gross-1321/result.json
    PYTHONPATH=src python3 scripts/s3c_flagnet_gross_1321.py page \\
        --score docs/research/s3c-flagnet-gross-1321/result.json --output docs/research/s3c-flagnet-gross-1321-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
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


from repo_model import announced_iorb, metrics, policy_events, s3c_announced, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.decision_instant import DECISION_TIME, LEGACY_DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model import spread_mr_calendar as cal  # noqa: E402

#: #1288's script (and through it #1273's, #1255's, #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker
#: pool's tasks does not meet another test module's copy.
m1288 = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1321")
m1273, m1255, k, c, s686, s761 = m1288.m1273, m1288.m1255, m1288.k, m1288.c, m1288.s686, m1288.s761
load_daily_panel = m1288.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_flagnet_gross_1321.json"
RECORD_1288 = REPO / "docs" / "research" / "s3c-announced-settlement-1288" / "result.json"
SEED = 1321
LAST_DAY = EXPLORATORY_END
WINDOW_LAST = m1288.WINDOW_LAST
WINDOWS = m1288.WINDOWS
WINDOW_TITLES = m1288.WINDOW_TITLES
S3, S3C, ANN, ANNNET = m1288.S3, m1288.S3C, m1288.ANN, m1288.ANNNET
FLAGNET, GROSS = "sc_s3c_ann_flagnet", "sc_s3c_ann_gross"
ARMS = (FLAGNET, GROSS)
REFERENCES = (ANNNET, S3C, ANN)
MODELS = (S3, S3C, ANN, ANNNET, FLAGNET, GROSS)
LABELS = {S3: "(s3)", S3C: "(s3c)", ANN: "(s3c-ann), the flag", ANNNET: "(s3c-ann-net), the candidate",
          FLAGNET: "(s3c-ann-flagnet)", GROSS: "(s3c-ann-gross)"}
SHORT = {S3: "(s3)", S3C: "(s3c)", ANN: "(s3c-ann)", ANNNET: "(s3c-ann-net)", FLAGNET: "(s3c-ann-flagnet)", GROSS: "(s3c-ann-gross)"}
TESTED = m1288.TESTED
METRIC_NAMES = m1288.METRIC_NAMES
METRIC_TITLES = m1288.METRIC_TITLES
MIN_GROUP_DAYS = m1288.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
EPSILON = 1e-9
LEADS = tuple(sp.HORIZONS)
SPLITS = ("pooled", "lead", "regime", "pressure_day_type")
DAY_TYPE = m1288.DAY_TYPE
TYPE_LABELS = m1288.TYPE_LABELS
#: The arms whose fitted settlement shift is compared with the realised premium, and the terms each reads, in the order of the effect tables.
SHIFT_ARMS = (ANN, ANNNET, FLAGNET, GROSS)
EFFECT_TERMS: Mapping[str, Tuple[str, ...]] = {
    ANN: ("settlement_coupon", "settlement_bill"),
    ANNNET: ("settlement_coupon", "settlement_bill"),
    FLAGNET: ("settlement_coupon", "settlement_bill", sc.NET_COUPON, sc.NET_BILL),
    GROSS: (sc.GROSS_COUPON, "settlement_bill"),
}
TERM_TITLES = {
    "settlement_coupon": "coupon flag", "settlement_bill": "bill flag", sc.NET_COUPON: "net coupon", sc.NET_BILL: "net bill",
    sc.GROSS_COUPON: "gross coupon",
}
#: The unit of each term's effect: bp per flagged day, or bp per USD 100 bn.
TERM_UNITS = {"settlement_coupon": "bp", "settlement_bill": "bp", sc.NET_COUPON: "bp per USD 100 bn", sc.NET_BILL: "bp per USD 100 bn",
              sc.GROSS_COUPON: "bp per USD 100 bn"}
#: The effect tables print the pooled row at every lead and the regime rows at this lead only; the record holds them all.
REGIME_LEAD = "3"
REPS = 2000


def chain_modules() -> list:
    """Every module of `scripts/` this study reaches: those #1288 loads and, through their module-level names, those they load, each object once
    (a module loaded twice under two aliases is two objects, and the walks read the one their own module holds)."""

    seen, queue = [], [m1288]
    while queue:
        module = queue.pop()
        if any(module is x for x in seen):
            continue
        seen.append(module)
        for value in list(vars(module).values()):
            path = getattr(value, "__file__", None)
            if isinstance(value, type(sys)) and path and Path(path).parent == REPO / "scripts":
                queue.append(value)
    return seen


@contextlib.contextmanager
def decision_instant_pinned():
    """Run the study modules of #1115 to #1288 at the decision instant of `repo_model.decision_instant` (18:00), for the length of the block.

    Those scripts type the 16:00 of the published records once, in `spread_mean_reversion_686.DECISION_TIME`, and every other copies it as a module
    constant (`DECISION_TIME = c.DECISION_TIME`) that its frame builders and walks read when they run. This sets each such constant, in every
    loaded module of `scripts/` that holds the legacy 16:00, to the declared instant, and puts it back on exit, so that nothing else in the
    process (another study's tests) sees the change. The records of those studies stay what they were: made at 16:00.

    Raises:
        ValueError: a module the walks read still holds another instant inside the block.
    """

    held = []
    for module in chain_modules():
        if getattr(module, "DECISION_TIME", None) == LEGACY_DECISION_TIME:
            held.append(module)
            module.DECISION_TIME = DECISION_TIME
    try:
        for name, value in (("k", k.DECISION_TIME), ("c", c.DECISION_TIME), ("s686", s686.DECISION_TIME)):
            if value != DECISION_TIME:
                raise ValueError(f"{name}.DECISION_TIME is {value}, not the declared instant {DECISION_TIME}")
        yield DECISION_TIME
    finally:
        for module in held:
            module.DECISION_TIME = LEGACY_DECISION_TIME


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def plan(candidate: str) -> List[str]:
    """What an arm is tested against: the candidate (s3c-ann-net), (s3c) and (s3c-ann)."""

    return list(REFERENCES) if candidate in ARMS else []


# -- the walks and the frame ---------------------------------------------------------------------------------------------


def walks_of(window: str, frame, panel, splits, registry, table, results, auctions, first: Optional[date]):
    """The walks of the references (s3c-ann), (s3c-ann-net) and of the two arms, over #1255's decision days, with the tables they read.

    Raises:
        ValueError: a scored decision day has no forecast of a walk, or (s3c-ann) is not (s3) at lead 1 on a scored decision day.
    """

    days = m1288.candidate_days(frame, window, first)
    settings = dict(registry=registry, decision_time=k.DECISION_TIME, splits=splits)
    states = s3c_net.constant_states(panel)
    iorb = announced_iorb.load_announcements(c.IORB_TABLE)
    term_table = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=k.DECISION_TIME)
    size_terms = s3c_announced.AnnouncedSizeTerms(term_table, net_table)
    walks = {
        "refs": sc.walk(panel, days, term_table, states, (s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM), sizes=net_table, **settings),
        "new": sc.walk(panel, days, term_table, states, (s3c_announced.FLAGNET_ARM, s3c_announced.GROSS_ARM), iorb=size_terms, **settings),
    }
    names = {"refs": (s3c_announced.ANN_ARM.name, s3c_announced.ANN_NET_ARM.name),
             "new": (s3c_announced.FLAGNET_ARM.name, s3c_announced.GROSS_ARM.name)}
    for key, walk in walks.items():
        for name in names[key]:
            for d in frame.days:
                if d not in walk.forecasts[name]:
                    raise ValueError(f"the {key} walk has no forecast of {name} on the scored decision day {d}")
    for d in frame.days:
        if walks["refs"].forecasts[s3c_announced.ANN_ARM.name][d][1] != frame.forecasts[S3][d][1]:
            raise ValueError(f"(s3c-ann) is not (s3) at lead 1 on {d}: lead 1 reads the panel's flags as (s3c) does")
    return walks, term_table, net_table, size_terms


def build(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]):
    """#1255's frame of `window` with the references and the arms added: `(frame, notes, walks, tables, groups_fn)`."""

    frame, notes, _mine, _cells, groups_fn = m1255.build(window, panel, splits, registry, table, register, first)
    walks, term_table, net_table, size_terms = walks_of(window, frame, panel, splits, registry, table, results, auctions, first)
    raw = {
        ANN: {d: walks["refs"].forecasts[s3c_announced.ANN_ARM.name][d] for d in frame.days},
        ANNNET: {d: walks["refs"].forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in frame.days},
        FLAGNET: {d: walks["new"].forecasts[s3c_announced.FLAGNET_ARM.name][d] for d in frame.days},
        GROSS: {d: walks["new"].forecasts[s3c_announced.GROSS_ARM.name][d] for d in frame.days},
    }
    forecasts = {S3: frame.forecasts[S3], S3C: frame.forecasts[S3C]}
    for name, found in raw.items():
        forecasts[name] = m1255.s3c_forecasts(frame, register, found)
    frame.forecasts = {name: {d: forecasts[name][d] for d in frame.days} for name in MODELS}
    notes = dict(notes, refits_refs=len(walks["refs"].fits), refits_new=len(walks["new"].fits))
    return frame, notes, walks, (term_table, net_table, size_terms), groups_fn


# -- the fitted effect ---------------------------------------------------------------------------------------------------


def effect_values(arm: str, lead: int, index: int, term_table, net_table, size_terms) -> Dict[str, float]:
    """The value of each of the arm's terms on the target of the decision on row `index`: a 0/1 flag, or a size in units of USD 100 bn."""

    if arm == ANN:
        flags = term_table.read(lead, index)
        return {t: float(flags[t]) for t in EFFECT_TERMS[arm]}
    if arm == ANNNET:
        sizes = net_table.read(lead, index)
        return {t: sizes[t] / sc.SIZE_UNIT for t in EFFECT_TERMS[arm]}
    flags = term_table.read(lead, index)
    extras = size_terms.read(lead, index)
    return {t: (float(flags[t]) if t in flags and t not in sc.SIZE_EXTRAS else extras.get(t, 0.0)) for t in EFFECT_TERMS[arm]}


def effects(frame, walk, arm_name: str, terms: Sequence[str], lead: int, read, *, reps: int = REPS) -> Dict[str, dict]:
    """The fitted effect of each term in bp (per flagged day, or per USD 100 bn) at `lead`, by regime of the target day and pooled.

    For each decision day the effect is that of the refit the forecast used at `lead` times the anchor's scale in bp (0 where the term was not in
    the fit, counted). `read(lead, index)` gives the value of every term on the day's target. The shift is the sum of effect times value over the
    terms, so the mean absolute shift on the days some term is non-zero is reported. Each mean carries the 90% stationary-bootstrap interval over
    decision days (an interval over days that share refits, not a sampling interval for a coefficient).
    """

    per_day: Dict[date, dict] = {}
    for d in frame.days:
        estimate = walk.estimates[walk.fit_used[d]][arm_name][lead]
        scale = float(walk.detail[d]["scale"])
        value = read(lead, frame.position[d])
        row = {"regime": frame.regime(frame.target(d, lead))}
        for t in terms:
            row[t] = estimate.effect.get(t, 0.0) * scale
            row[f"in_fit_{t}"] = 1.0 if t in estimate.effect else 0.0
            row[f"value_{t}"] = value.get(t, 0.0)
        row["shift"] = sum(row[t] * row[f"value_{t}"] for t in terms)
        per_day[d] = row
    groups: Dict[str, List[date]] = {"all": list(frame.days)}
    for d, row in per_day.items():
        groups.setdefault(row["regime"], []).append(d)
    out: Dict[str, dict] = {}
    for name, members in groups.items():
        members = sorted(members)
        entry: dict = {"days": len(members)}
        columns = {t: [per_day[d][t] for d in members] for t in terms}
        for t in terms:
            entry[t] = {"mean": sum(columns[t]) / len(members),
                        "share_in_fit": sum(per_day[d][f"in_fit_{t}"] for d in members) / len(members)}
        if len(members) >= MIN_GROUP_DAYS:
            intervals = metrics.stationary_bootstrap_intervals(
                lambda idx: [sum(columns[t][i] for i in idx) / len(idx) for t in terms], len(members),
                block_length=BLOCK, seed=SEED, replications=reps)
            for t, interval in zip(terms, intervals):
                entry[t]["interval"] = [interval[0], interval[1]]
        active = [d for d in members if any(abs(per_day[d][f"value_{t}"]) > EPSILON for t in terms)]
        entry["active_days"] = len(active)
        entry["mean_abs_shift_bp_on_active_days"] = sum(abs(per_day[d]["shift"]) for d in active) / len(active) if active else None
        out[name] = entry
    return out


# -- the settlement shift against the realised premium ------------------------------------------------------------------


def fitted_shift_bp(estimate: sc.StateEstimate, scale: float, flags, sizes, extras, sized: bool) -> float:
    """The fitted settlement shift of one forecast in bp: the standardised shift of the refit times the scale at the anchor.

    A sized arm (s3c-ann-net) holds the scarcity state at its maximum, so the plain `size / SIZE_UNIT` enters (`s3c_net.constant_states`).
    """

    state = sc.level(sc.STATE_MAX) if sized else None
    return sc.standardised_shift(estimate, flags, state, sizes if sized else None, extras) * scale


def shift_cells(frame, walks, tables, facts) -> List[dict]:
    """One dict per (decision day, lead): the realised spread, the regime and settlement type of the target, the median of each model and the
    fitted settlement shift of each of `SHIFT_ARMS`, for the days of `frame`."""

    term_table, net_table, size_terms = tables
    median_at = sp.GRID.index(0.5)
    keys = {ANN: ("refs", s3c_announced.ANN_ARM.name), ANNNET: ("refs", s3c_announced.ANN_NET_ARM.name),
            FLAGNET: ("new", s3c_announced.FLAGNET_ARM.name), GROSS: ("new", s3c_announced.GROSS_ARM.name)}
    out: List[dict] = []
    for d in frame.days:
        i = frame.position[d]
        for h in LEADS:
            t = frame.target(d, h)
            flags = term_table.read(h, i)
            sizes = net_table.read(h, i)
            extras = size_terms.read(h, i)
            shifts = {}
            for arm, (walk_key, name) in keys.items():
                walk = walks[walk_key]
                estimate = walk.estimates[walk.fit_used[d]][name][h]
                shifts[arm] = fitted_shift_bp(estimate, float(walk.detail[d]["scale"]), flags, sizes, extras, arm == ANNNET)
            f = facts[t]
            out.append({
                "d": d, "h": h, "y": frame.outcome[t], "regime": frame.regime(t), "settle": bool(f["coupon"] or f["bill"]),
                "med": {m: frame.forecasts[m][d][h][median_at] for m in MODELS}, "shift": shifts,
            })
    return out


BIAS_MODELS = (S3C,) + SHIFT_ARMS
#: Layout of a unit's vector: n on settlement days, n on the others, the sum of y on each, then per model the sums of error on each and of shift.
_HEAD = 4


def bias_vector(cells: Sequence[dict]) -> List[float]:
    v = [0.0] * (_HEAD + 3 * len(BIAS_MODELS))
    for x in cells:
        on = x["settle"]
        v[0 if on else 1] += 1
        v[2 if on else 3] += x["y"]
        for j, m in enumerate(BIAS_MODELS):
            base = _HEAD + 3 * j
            v[base + (0 if on else 1)] += x["y"] - x["med"][m]
            if on:
                v[base + 2] += x["shift"].get(m, 0.0)
    return v


def bias_units(cells: Sequence[dict], leads: Sequence[int]) -> List[Dict[str, List[float]]]:
    """Per decision day, the sums the shift and bias tables need, by regime of the target."""

    by_day: Dict[date, Dict[str, List[dict]]] = {}
    for x in cells:
        if x["h"] in leads:
            by_day.setdefault(x["d"], {}).setdefault(x["regime"], []).append(x)
    return [{regime: bias_vector(members) for regime, members in by_day[d].items()} for d in sorted(by_day)]


def bias_statistics(totals: Mapping[str, Sequence[float]], names: Sequence[Tuple[str, str, str]]) -> List[float]:
    """The values of `names` ((regime, model, field), field in premium, shift, bias) on the summed vectors; a regime with no settlement-day or no
    other cell reads 0, so a resample that loses one never breaks the interval."""

    out = []
    for regime, model, field in names:
        t = totals.get(regime)
        if t is None or t[0] == 0 or t[1] == 0:
            out.append(0.0)
            continue
        if field == "premium":
            out.append(t[2] / t[0] - t[3] / t[1])
            continue
        base = _HEAD + 3 * BIAS_MODELS.index(model)
        out.append(t[base + 2] / t[0] if field == "shift" else t[base] / t[0] - t[base + 1] / t[1])
    return out


def _sum_units(units: Sequence[Mapping[str, Sequence[float]]], idx: Sequence[int]) -> Dict[str, List[float]]:
    out: Dict[str, List[float]] = {}
    for i in idx:
        for regime, vec in units[i].items():
            tot = out.setdefault(regime, [0.0] * len(vec))
            for j, value in enumerate(vec):
                tot[j] += value
    all_ = [0.0] * (_HEAD + 3 * len(BIAS_MODELS))
    for vec in out.values():
        for j, value in enumerate(vec):
            all_[j] += value
    out["all"] = all_
    return out


def shift_against_premium(cells: Sequence[dict], leads: Sequence[int], reps: int) -> dict:
    """The fitted settlement shift against the realised settlement-day premium and the bias, by regime of the target, for the cells at `leads`.

    The realised premium is the mean spread on settlement-day targets less that on the others; the shift is each arm's mean fitted shift on
    the settlement-day targets; the bias is the mean error on settlement-day targets less that on the others (negative: the forecast median is
    too high on settlement days). Each carries the 90% stationary-bootstrap interval over decision days of the regime (20 or more).
    """

    units = bias_units(cells, leads)
    regimes = ["all"] + sorted({r for u in units for r in u}, key=lambda r: min(x["d"] for x in cells if x["regime"] == r))
    names: List[Tuple[str, str, str]] = []
    for r in regimes:
        names.append((r, S3C, "premium"))
        for m in BIAS_MODELS:
            names.append((r, m, "bias"))
            if m != S3C:
                names.append((r, m, "shift"))
    point = bias_statistics(_sum_units(units, range(len(units))), names)
    result: Dict[str, dict] = {r: {"cells": 0} for r in regimes}
    for x in cells:
        if x["h"] in leads:
            result["all"]["cells"] += 1
            result[x["regime"]]["cells"] += 1
    days_in = {r: sum(1 for u in units if r in u) for r in regimes}
    days_in["all"] = len(units)
    intervals: Dict[Tuple[str, str, str], Optional[List[float]]] = {n: None for n in names}
    if len(units) >= MIN_GROUP_DAYS:
        found = metrics.stationary_bootstrap_intervals(
            lambda idx: bias_statistics(_sum_units(units, idx), names), len(units), block_length=BLOCK, seed=SEED, replications=reps)
        for name, interval in zip(names, found):
            if days_in[name[0]] >= MIN_GROUP_DAYS:
                intervals[name] = [interval[0], interval[1]]
    for name, value in zip(names, point):
        regime, model, field = name
        key = "premium" if field == "premium" else model
        slot = result[regime].setdefault(key, {})
        entry = {"value": value}
        if intervals[name] is not None:
            entry["interval"] = intervals[name]
        if field == "premium":
            result[regime]["premium"] = entry
        else:
            slot[field] = entry
    for r in regimes:
        result[r]["decision_days"] = days_in[r]
    return {"leads": list(leads), "regimes": regimes, "by_regime": result}


# -- the groups and the tests --------------------------------------------------------------------------------------------


_STATE: Dict = {}


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def unstudentized(series, candidate: str, reference: str, members: Sequence[date], reps: int) -> dict:
    """Mean d and its 90% stationary-bootstrap percentile interval, for a group whose studentized bound cannot be computed. Not the protocol's
    interval; no reading is taken from it. `d = S(reference) - S(candidate)`, positive favours the candidate."""

    d = [series[reference][x] - series[candidate][x] for x in sorted(members)]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=BLOCK, seed=SEED, replications=reps)
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
            out[name]["unstudentized"] = unstudentized(series, candidate, name, days, _STATE["reps"])
    return (split, label, metric, candidate), out


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_pairs_task, jobs, chunksize=1)


def lead_difference(frame, base: str, other: str) -> dict:
    return m1273.lead_difference(frame, base, other)


def announcement_check(frame, panel, results, facts, term_table, net_table) -> dict:
    """What the announcement dating gives on the scored target days (#1288's check): the announced gross against the panel's at lead 1, and the
    coverage by lead."""

    return m1288.announcement_check(frame, panel, results, facts, term_table, net_table)


def run_window(window: str, panel, splits, registry, table, register, results, auctions, args) -> dict:
    frame, notes, walks, tables, groups_fn = build(window, panel, splits, registry, table, register, results, auctions, args.first)
    term_table, net_table, size_terms = tables
    last = WINDOW_LAST[window]
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    facts = m1288.settlement_facts(panel, auctions)
    cells = {m: m1288.cell_table(frame, frame.forecasts[m], last) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")
    groups = [g for g in groups_fn(frame, labels, pressure) if g[0] in SPLITS]
    for lead in LEADS:
        for label, members in m1288.day_type_members(frame, facts, lead).items():
            groups.append((DAY_TYPE, f"h={lead}: {label}", f"lead{lead}", members))
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
            for candidate in ARMS:
                jobs.append((split, label, grain, metric, candidate, tuple(members)))
    done = run_jobs(jobs, args.workers)

    shift_rows = shift_cells(frame, walks, tables, facts)
    reads = {
        ANN: lambda lead, i: effect_values(ANN, lead, i, term_table, net_table, size_terms),
        ANNNET: lambda lead, i: effect_values(ANNNET, lead, i, term_table, net_table, size_terms),
        FLAGNET: lambda lead, i: effect_values(FLAGNET, lead, i, term_table, net_table, size_terms),
        GROSS: lambda lead, i: effect_values(GROSS, lead, i, term_table, net_table, size_terms),
    }
    arm_names = {ANN: ("refs", s3c_announced.ANN_ARM.name), ANNNET: ("refs", s3c_announced.ANN_NET_ARM.name),
                 FLAGNET: ("new", s3c_announced.FLAGNET_ARM.name), GROSS: ("new", s3c_announced.GROSS_ARM.name)}
    result: dict = {
        "notes": notes, "groups": {}, "skipped_groups": skipped,
        "announcement_check": announcement_check(frame, panel, results, facts, term_table, net_table),
        "lead_difference": {
            "ann_against_s3c": lead_difference(frame, S3C, ANN), "ann_net_against_s3c": lead_difference(frame, S3C, ANNNET),
            "flagnet_against_ann_net": lead_difference(frame, ANNNET, FLAGNET), "gross_against_ann_net": lead_difference(frame, ANNNET, GROSS),
            "flagnet_against_ann": lead_difference(frame, ANN, FLAGNET), "gross_against_ann": lead_difference(frame, ANN, GROSS),
        },
        "shift_against_premium": {
            "later": shift_against_premium(shift_rows, LEADS[1:], args.reps), "lead1": shift_against_premium(shift_rows, LEADS[:1], args.reps),
        },
        "effects": {
            arm: {str(h): effects(frame, walks[arm_names[arm][0]], arm_names[arm][1], EFFECT_TERMS[arm], h, reads[arm], reps=args.reps)
                  for h in LEADS}
            for arm in SHIFT_ARMS
        },
    }
    for split, label, grain, members in groups:
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(members)})
        for metric in METRIC_NAMES:
            ser = series[(grain, metric)]
            entry[metric] = {"means": {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}, "vs": {}}
    for (split, label, metric, candidate), payload in done:
        result["groups"][split][label][metric]["vs"][candidate] = payload
    result["pressure_day_type_counts"] = {x: sum(1 for t in pressure.values() if t == x) for x in sorted(set(pressure.values()))}
    return result


def against_1288(results: Mapping[str, dict]) -> dict:
    """The pooled means here beside #1288's record, which was made at 16:00: the references are re-run at 18:00, so the two differ by the move
    in the decision instant alone. Shown, never required to agree."""

    if not RECORD_1288.exists():
        return {}
    there = json.loads(RECORD_1288.read_text(encoding="utf-8"))["windows"]
    out: Dict[str, dict] = {}
    for window, result in results.items():
        a, b = there[window]["groups"]["pooled"]["all decision days"], result["groups"]["pooled"]["all decision days"]
        out[window] = {m: {x: {"now": b[m]["means"][x], "then": a[m]["means"][x], "difference": b[m]["means"][x] - a[m]["means"][x]}
                           for x in (S3, S3C, ANN, ANNNET)} for m in ("grid_crps", "upper_tail_twcrps", "brier_gt5")}
    return out


def score(args) -> int:
    """Score both windows with every module of the chain at the declared decision instant (`decision_instant_pinned`)."""

    with decision_instant_pinned():
        return _score(args)


def _score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_flagnet_gross_1321")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    result: dict = {
        "issue": 1321, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "decision_time": c.DECISION_TIME.strftime("%H:%M"), "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS),
        "arms": list(ARMS), "references": list(REFERENCES), "margin_bp": s3c_candidate.MARGIN_BP,
        "dating": json.loads(m1288.DATING.read_text(encoding="utf-8"))["available_time"],
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, results, auctions, args)
    result["against_1288"] = against_1288(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------


def cell(row: Optional[dict]) -> str:
    return m1288.cell(row)


def _vs(group: Optional[Mapping[str, object]], metric: str, candidate: str, reference: str) -> Optional[dict]:
    return m1288._vs(group, metric, candidate, reference)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{group[x]['means'][m]:.3f}" if x in ("grid_crps", "upper_tail_twcrps") else f"{group[x]['means'][m]:.4f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object], candidate: str) -> List[str]:
    out = [f"| {SHORT[candidate]} against | " + " | ".join(METRIC_TITLES[m] for m in TESTED) + " |", "|---|" + "---|" * len(TESTED)]
    for ref in plan(candidate):
        out.append(f"| {SHORT[ref]} | " + " | ".join(cell(_vs(group, m, candidate, ref)) for m in TESTED) + " |")
    return out


def split_table(window: Mapping[str, object], split: str, candidate: str, reference: str, order: Optional[Sequence[str]] = None) -> List[str]:
    return m1288.split_table(window, split, candidate, reference, order)


def means_split_table(window: Mapping[str, object], split: str, metric: str) -> List[str]:
    labels = window["groups"].get(split, {})
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(SHORT[m] for m in MODELS) + " |", "|---|---|" + "---|" * len(MODELS)]
    for label in sorted(labels):
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[metric]['means'][m]:.4f}" for m in MODELS) + " |")
    return out if len(out) > 2 else []


def _iv(entry: Optional[Mapping[str, object]], digits: int = 2) -> str:
    if entry is None:
        return "n/a"
    text = f"{entry['value']:+.{digits}f}"
    if "interval" in entry:
        text += f" [{entry['interval'][0]:+.{digits}f}, {entry['interval'][1]:+.{digits}f}]"
    return text


def shift_table(block: Mapping[str, object]) -> List[str]:
    arms = SHIFT_ARMS
    out = ["| regime | decision days | realised premium (bp) | " + " | ".join(f"{SHORT[a]} shift" for a in arms) + " |",
           "|---|---|---|" + "---|" * len(arms)]
    for regime in block["regimes"]:
        e = block["by_regime"][regime]
        out.append(f"| {regime} | {e['decision_days']} | {_iv(e.get('premium'))} | " + " | ".join(_iv(e[a].get("shift")) for a in arms) + " |")
    return out


def bias_table(block: Mapping[str, object]) -> List[str]:
    models = BIAS_MODELS
    out = ["| regime | " + " | ".join(SHORT[m] for m in models) + " |", "|---|" + "---|" * len(models)]
    for regime in block["regimes"]:
        e = block["by_regime"][regime]
        out.append(f"| {regime} | " + " | ".join(_iv(e[m].get("bias")) for m in models) + " |")
    return out


def effect_table(by_lead: Mapping[str, Mapping[str, dict]], terms: Sequence[str]) -> List[str]:
    cols = [f"{TERM_TITLES[t]} ({TERM_UNITS[t]}) [90%]" for t in terms]
    out = ["| lead | regime | days | " + " | ".join(cols) + " | share of days in the fit | mean abs shift on active days (bp) |",
           "|---|---|---|" + "---|" * (len(terms) + 2)]
    for lead in sorted(by_lead, key=int):
        eff = by_lead[lead]
        for name in sorted(eff, key=lambda x: (x != "all", x)):
            if name != "all" and lead != REGIME_LEAD:
                continue
            e = eff[name]
            parts = []
            for t in terms:
                m = e[t]
                parts.append(f"{m['mean']:+.3f}" + (f" [{m['interval'][0]:+.3f}, {m['interval'][1]:+.3f}]" if "interval" in m else " (too few days)"))
            shift = "n/a" if e["mean_abs_shift_bp_on_active_days"] is None else f"{e['mean_abs_shift_bp_on_active_days']:.3f}"
            share = " / ".join(f"{e[t]['share_in_fit']:.2f}" for t in terms)
            out.append(f"| h={lead} | {name} | {e['days']} | " + " | ".join(parts) + f" | {share} | {shift} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        entry = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        parts.append(f"{text}, grid CRPS against (s3c-ann-net): (s3c-ann-flagnet) {cell(_vs(entry, 'grid_crps', FLAGNET, ANNNET))}; "
                     f"(s3c-ann-gross) {cell(_vs(entry, 'grid_crps', GROSS, ANNNET))}")
    return "; ".join(parts) + "."


def summary(r: Mapping[str, object]) -> List[str]:
    """The first screen: grid CRPS against (s3c-ann-net), by lead, for each arm, in each window."""

    out = ["## Summary: grid CRPS against (s3c-ann-net), by lead", "",
           "Skill and its 90% interval, the mean difference d and its studentized 90% interval, and the reading on the mean-d bound (positive favours "
           "the arm). The full tables, with the other metrics and references, follow.", ""]
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        out += [f"**{WINDOW_TITLES[window].split(' (')[0]}**", "", "| lead | " + " | ".join(SHORT[x] for x in ARMS) + " |", "|---|---|---|"]
        for lead in LEADS:
            g = w["groups"]["lead"][f"h={lead}"]
            out.append(f"| h={lead} | " + " | ".join(cell(_vs(g, "grid_crps", x, ANNNET)) for x in ARMS) + " |")
        g = w["groups"]["pooled"]["all decision days"]
        out.append("| pooled over h = 1..5 | " + " | ".join(cell(_vs(g, "grid_crps", x, ANNNET)) for x in ARMS) + " |")
        out.append("")
    return out


def render(r: dict) -> str:
    out = [
        "# (s3c-ann-flagnet) and (s3c-ann-gross): two arms on avenue #1318 beside (s3c-ann-net), at the 18:00 decision (#1321)", "",
        "**Does keeping the flag and adding the net beside it, or sizing the coupon leg by the gross it finances, beat the net alone?** " + headline(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, two arms on the candidate (s3c-ann-net); ledger item 81, avenue #1318, diagnosis #1320. "
        "**Development data, not a verdict** (scoring protocol v1, #640). Her ruling of 30 October 2026 (chat, relayed on #1321): test both the "
        "flag-plus-net arm and a gross-sized arm; the net x scarcity interaction is not part of it. **(s3c-ann-net) stays the candidate of the avenue "
        "and (s3c) the H5 candidate; nothing here changes either.** Nothing is registered or published and no claim changes. Generated by "
        "`scripts/s3c_flagnet_gross_1321.py page` from `docs/research/s3c-flagnet-gross-1321/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score.", "",
        "**What changed.** The settlement terms are read at every lead from the auction announcement "
        f"({r['dating']} New York time on the `announcemt_date`, #541, not in force), at the {r['decision_time']} decision instant "
        "(amended on 29 October 2026, #1312; #1288's record was made at 16:00, so the references are re-run here). **(s3c-ann-flagnet)** keeps "
        "(s3c-ann)'s two announced 0/1 flags and adds #1273's announced net coupon and net bill beside them (four settlement terms, the nets in units "
        "of USD 100 bn). **(s3c-ann-gross)** sizes the coupon leg by the announced gross coupon offering (USD 100 bn) in place of its flag and keeps "
        "the bill flag. Everything else is (s3)'s and the SRF cap is (s3c)'s; the fit is on direct pairs. The references (s3c), (s3c-ann) and "
        "(s3c-ann-net) are re-run in the same run.", "",
        "**The bill leg carries Lens E's caveat** (`docs/reviews/2026-10-19-five-lens/lens-E-data-plumbing.md`, item G): Treasury publishes no clock "
        "time for an announcement, and the 12:00 announcement time of a cash management bill is unverified. If one is announced after 12:00 on the "
        "decision day the term counts it too early; any decision instant from 12:00 to 23:59 counts the same auctions, so the move to 18:00 does not "
        "change the announced sums.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "the arm named first in the table's heading. **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the "
        "skill interval beside it; for a Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals "
        "of a group of target days keep the **current method** (the group's days, scattered, resampled in date order as if consecutive), which #1221 "
        "questions and #1228 will decide; no reading of a day-type group is a finding. Where two arms differ on few days of a group the bound may "
        "not be computed: the unstudentized interval of mean d is then given beside it, and no reading is taken from that. Groups of fewer than 20 "
        "days are listed with their means and not tested. The benchmarks are not part of this directive's comparisons and are not scored here.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, by the #151 final test, and by #1229, #1255, #1273 and #1288. This is a "
        "check on arms queued by her ruling, not evidence for a verdict. The announced terms act at every lead here, so the pooled figure averages "
        "five leads; read the lead rows beside it.", ""]
    out += summary(r)
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        a, ld = w["announcement_check"], w["lead_difference"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {n['refits_refs']} refits of the reference walk and "
                f"{n['refits_new']} of the arms' walk. At lead 1 the announced gross settlement and the panel's gross columns differ on "
                f"{a['lead_1_differences']} (column, day) pairs of {a['target_days']:,} scored target days. Cells on which an arm is not (s3c-ann-net) "
                f"element for element, by lead (of {ld['flagnet_against_ann_net']['cells_per_lead']:,} each): (s3c-ann-flagnet): "
                + ", ".join(f"h={h}: {ld['flagnet_against_ann_net']['differing_cells'][str(h)]:,}" for h in LEADS) + "; (s3c-ann-gross): "
                + ", ".join(f"h={h}: {ld['gross_against_ann_net']['differing_cells'][str(h)]:,}" for h in LEADS) + ".", "",
                "### Mean scores (pooled)", ""] + mean_table(pooled)
        for arm in ARMS:
            out += ["", f"### {LABELS[arm]} against each reference (pooled)", ""] + against_table(pooled, arm) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day"),
                             (DAY_TYPE, "By the settlement-day type of the target at each lead")):
            for arm in ARMS:
                for ref in plan(arm):
                    table = split_table(w, split, arm, ref)
                    if table:
                        out += [f"### {title}: {SHORT[arm]} against {SHORT[ref]}", ""] + table + [""]
        for split, title in (("regime", "regime"), ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split, "b90_closed")
            if table:
                out += [f"### 90% band coverage by {title}", ""] + table + [""]
        sp_block = w["shift_against_premium"]
        out += ["### The fitted settlement shift against the realised settlement-day premium, by regime of the target", "",
                "As #1320's table 4b. The realised premium is the mean spread on settlement-day targets less that on the other targets; each arm's shift "
                "is its mean fitted settlement shift on the settlement-day targets (bp). Intervals are 90% stationary-bootstrap intervals over decision "
                "days that share refits.", "", "**Leads 2 to 5**", ""] + shift_table(sp_block["later"]) + [
                "", "**Lead 1**", ""] + shift_table(sp_block["lead1"]) + [
                "", "The bias is the mean error (realised less the forecast median) on settlement-day targets less that on the others; negative means the "
                "median is too high on settlement days. Leads 2 to 5:", ""] + bias_table(sp_block["later"]) + ["", "Lead 1:", ""] + bias_table(
                    sp_block["lead1"]) + [""]
        out += ["### The fitted effect, by lead and regime of the target day", ""]
        for arm in SHIFT_ARMS:
            out += [f"{LABELS[arm]}:", ""] + effect_table(w["effects"][arm], EFFECT_TERMS[arm]) + [""]
        out += ["The effect is the standardised effect of the refit the forecast used times the scale at the anchor in bp. The pooled row is printed at every "
                "lead and the regime rows at h = 3 only (the record holds them all). The interval is a bootstrap interval of the mean over decision days, "
                "which share refits; it is not a sampling interval for the coefficient. A term enters a fit only when at least three training pairs carry it.", ""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    if r.get("against_1288"):
        out += ["## The references against #1288's record (made at 16:00)", "",
                "The references are re-run at 18:00; the pooled means below differ from #1288's record by the move in the decision instant alone. Shown, "
                "not required to agree; no record is edited. The largest absolute difference of a pooled mean here is "
                f"{max(abs(v['difference']) for ms in r['against_1288'].values() for rows in ms.values() for v in rows.values()):.1e}: the "
                "references read the spread series (public the next morning) and the calendar columns, so the move from 16:00 to 18:00 leaves their "
                "anchors, and so their forecasts, where they were (#1314 re-runs the candidate and the 16:00 against 18:00 row on its own terms).", ""]
        for window, metrics_ in r["against_1288"].items():
            out += [f"{WINDOW_TITLES[window].split(' (')[0]}: " + "; ".join(
                f"{METRIC_TITLES[m]}: " + ", ".join(f"{SHORT[x]} {v['now']:.6f} now, {v['then']:.6f} then" for x, v in rows.items())
                for m, rows in metrics_.items()) + ".", ""]
    out += question(r)
    return "\n".join(out).rstrip() + "\n"


def question(r: Optional[dict] = None) -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. Does either arm replace (s3c-ann-net) as the candidate of avenue #1318?** The candidate does not change in this directive. "
        "Whether an arm should replace it rests on days already seen, split as above.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c-ann-net) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests the better arm prospectively**, on the confirmation days only, under the scoring protocol.",
        "3. **Ask for a further arm** from the shift-against-premium table, in a directive of its own.", "",
        "**Question 2. The announcement dating.** These arms read `metadata/settlement_announcement_dating.json`, which is measured and off. "
        "Turning it on in the published declaration is her decision; nothing here asks for it.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **Leave the dating off** (default). Nothing changes.",
        "2. **Ask for a prospective test of the dating**, in a directive of its own, on the confirmation days only.", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the references and the two arms, cap them as (s3c) is capped, and score on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=REPS, help="bootstrap resamples of the unstudentized, effect and shift intervals")
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
