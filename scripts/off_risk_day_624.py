"""Skill on the days that are not risk dates (#624): step 1, the measurement; step 2 follows in the same file once it is declared.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Nothing is
published, no day after 2025-12-31 is read (`docs/decisions/lockbox.md`; `require_unlocked`), and the live record and pin do not move.

Step 1 (`measure`, committed before any step 2 declaration) asks, of the every-day part of five rows, whether it has skill on the days
that are not risk dates beyond the base rate: the part of `risk_gbm+every_day+gate+settle+h41+iorb` (#579, PR #582) that serves those
days, the same row capped by the tail spread's trailing history (`+tailcap75`, #601, PR #609) and the three floors of #610 (PR #612).
Per lead 1 to 5, on the days that are not risk dates (`announcement_dating_rescore.risk_flag`), for a pressure day at +5 bp:

* discrimination: the area under the ROC curve (ties half) of the row's forecast against the day's outcome;
* the Brier skill against the walk-forward climatology: 1 less the row's Brier score over that of the pooled rate of pressure days among
  the earlier such days whose outcome was observable at the block's fit (`group_calibration.fit_floor`), on the days that rate exists;
* the reliability curve's slope and intercept: the logistic recalibration of the outcome on the logit of the forecast, on the days on which
  the forecast is above 0 (the row forecasts exactly 0 on the others; their number and the pressure days on them are reported beside it);
* each with a 90% stationary-bootstrap interval, and the same split by regime and by as-of reserve-scarcity state.

    # AUG2.csv is the scratch panel of risk_date_severity.py; the forecast files are those of scripts/tailcap_floor_610.py and
    # scripts/iorb_every_day_579.py (OUT/iorb_h?.json, OUT/cap_h?.json, OUT/v610_h?.json)
    PYTHONPATH=src python3 scripts/off_risk_day_624.py measure --panel PUBLISHED.csv --scratch AUG2.csv \\
        --iorb 'OUT/iorb_h{h}.json' --cap 'OUT/cap_h{h}.json' --floors 'OUT/v610_h{h}.json' \\
        --output OUT/step1.json --markdown OUT/step1.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import random
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import (  # noqa: E402
    group_calibration as gc, h41_release, measurement_fields, probability_calibration as pc, pressure_judge as pj, satiation as sat,
)
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import _as_of_folds, climatology_exceedance, panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


ann = _load("announcement_dating_rescore")
rds = _load("risk_date_severity")
sd = _load("satiation_distance_598")

SPLITS = REPO / "metadata" / "evaluation_splits.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
STEP_ONE_DECLARATION = REPO / "metadata" / "off_risk_day_624_step1.json"
STEP_TWO_DECLARATION = REPO / "metadata" / "off_risk_day_624.json"
LEADS = (1, 2, 3, 4, 5)
TAU = 5.0
ROW = "risk_gbm+every_day+gate+settle+h41+iorb"
CAP = ROW + "+tailcap75"
FLOORS = {"floor": CAP + "+floor", "state_floor": CAP + "+state_floor", "recent_floor": CAP + "+recent_floor"}
#: row name -> the forecast file kind that holds it
ROWS = {ROW: "iorb", CAP: "cap", **{name: "floors" for name in FLOORS.values()}}
#: a forecast this small is read as 0 by the reliability fit (the rows forecast exactly 0 on the days they leave out)
RELIABILITY_FLOOR = 1e-4


# -- the pure readers --------------------------------------------------------------------------------------


def climatology_column(
    outcomes: Sequence[int],
    scored: Sequence[date],
    train_ends: Sequence[date],
    off_risk: Sequence[bool],
    *,
    minimum_pairs: int = gc.GROUP_MINIMUM_PAIRS,
) -> List[Optional[float]]:
    """The walk-forward climatology on the days that are not risk dates: each refit block's pooled rate of pressure days among the
    earlier such days whose outcome was observable at the block's fit; None on a risk date and while those days number fewer than
    `minimum_pairs`.

    Raises:
        ValueError: for columns of different lengths.
        LookAheadError: if a pair read for a block is of a day after the block's fit (`group_calibration.fit_floor`).
    """

    if len({len(outcomes), len(scored), len(train_ends), len(off_risk)}) != 1:
        raise ValueError("outcomes, dates, train ends and risk flags must be one per scored day")
    column: List[Optional[float]] = [None] * len(outcomes)
    for start, stop, end in pc.blocks(scored, train_ends):
        past = [i for i in pc.past_positions(scored, train_ends, start) if off_risk[i]]
        rate = gc.fit_floor([(scored[i], 0.0, outcomes[i], "") for i in past], end, minimum_pairs=minimum_pairs)
        for index in range(start, stop):
            if off_risk[index]:
                column[index] = rate
    return column


def brier(probabilities: Sequence[float], outcomes: Sequence[int]) -> float:
    return sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / len(outcomes)


def brier_skill(probabilities: Sequence[float], outcomes: Sequence[int], reference: Sequence[float]) -> Optional[float]:
    """1 less the row's Brier score over the reference's; None when the reference's score is 0 or there are no days."""

    if not outcomes:
        return None
    base = brier(reference, outcomes)
    return None if base == 0.0 else 1.0 - brier(probabilities, outcomes) / base


def _logit(p: float) -> float:
    p = min(1.0 - RELIABILITY_FLOOR, max(RELIABILITY_FLOOR, p))
    return math.log(p / (1.0 - p))


def reliability(probabilities: Sequence[float], outcomes: Sequence[int], *, iterations: int = 50) -> Optional[Tuple[float, float]]:
    """`(intercept, slope)` of the logistic recalibration of the outcome on the logit of the forecast, by Newton's method.

    A calibrated forecast has intercept 0 and slope 1; a slope below 1 means the forecast spreads further than the outcomes do, a slope
    above 1 that it is too tight, and a slope of 0 that it ranks nothing. None when the forecasts are all alike, or the outcomes are all
    one class, or the fit does not converge.
    """

    xs = [_logit(p) for p in probabilities]
    ys = list(outcomes)
    if not xs or len(set(ys)) < 2 or max(xs) - min(xs) < 1e-9:
        return None
    a, b = math.log(max(sum(ys), 0.5) / max(len(ys) - sum(ys), 0.5)), 0.0
    for _ in range(iterations):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y in zip(xs, ys):
            z = a + b * x
            p = 1.0 / (1.0 + math.exp(-z)) if z > -700 else 0.0
            w = p * (1.0 - p)
            g0 += y - p
            g1 += (y - p) * x
            h00 += w
            h01 += w * x
            h11 += w * x * x
        det = h00 * h11 - h01 * h01
        if det <= 1e-12:
            return None
        step_a, step_b = (h11 * g0 - h01 * g1) / det, (h00 * g1 - h01 * g0) / det
        a, b = a + step_a, b + step_b
        if abs(step_a) < 1e-9 and abs(step_b) < 1e-9:
            return a, b
    return None


def cell_statistics(probabilities: Sequence[float], outcomes: Sequence[int], reference: Sequence[Optional[float]]) -> dict:
    """The step 1 statistics of one cell of days: the outcomes, the reference being the walk-forward climatology.

    The Brier skill is taken on the days on which the reference exists.
    """

    paired = [(p, y, r) for p, y, r in zip(probabilities, outcomes, reference) if r is not None]
    p, y, r = [x[0] for x in paired], [x[1] for x in paired], [x[2] for x in paired]
    positive = [(pp, yy) for pp, yy in zip(probabilities, outcomes) if pp > RELIABILITY_FLOOR]
    fit = reliability([a for a, _ in positive], [b for _, b in positive]) if positive else None
    return {
        "days": len(outcomes),
        "pressure_days": int(sum(outcomes)),
        "auroc": pj.auroc(list(probabilities), list(outcomes)),
        "brier_skill": brier_skill(p, y, r),
        "skill_days": len(paired),
        "positive_days": len(positive),
        "pressure_days_on_zero": int(sum(outcomes)) - int(sum(b for _, b in positive)),
        "intercept": None if fit is None else fit[0],
        "slope": None if fit is None else fit[1],
    }


def _quantile(sorted_values: Sequence[float], q: float) -> float:
    position = q * (len(sorted_values) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (position - low)


def intervals(
    cells: Mapping[str, Sequence[int]],
    probabilities: Sequence[float],
    outcomes: Sequence[int],
    reference: Sequence[Optional[float]],
    *,
    seed: int,
    replications: int,
    block_length: float,
    level: float,
    reliability_cells: Sequence[str] = ("all",),
) -> Dict[str, dict]:
    """A 90% stationary-bootstrap interval for each statistic of each cell, from the same resamples of the date-ordered days.

    A resample draws day positions in blocks (`metrics.stationary_bootstrap_indices`) and each cell keeps the drawn days that are in
    it. A statistic that is undefined on a resample (a cell with no pressure day, say) is left out of that cell's draws and the number
    left out is reported beside the interval: dropping them quietly would narrow it. The reliability fit is bootstrapped for the cells
    named in `reliability_cells` only (it is a Newton fit per resample).
    """

    n = len(outcomes)
    member = {name: [False] * n for name in cells}
    for name, positions in cells.items():
        for i in positions:
            member[name][i] = True
    draws: Dict[str, Dict[str, List[float]]] = {name: {"auroc": [], "brier_skill": [], "slope": [], "intercept": []} for name in cells}
    rng = random.Random(seed)
    for _ in range(replications):
        drawn = stationary_bootstrap_indices(n, block_length, rng)
        for name in cells:
            keep = [i for i in drawn if member[name][i]]
            if not keep:
                continue
            p = [probabilities[i] for i in keep]
            y = [outcomes[i] for i in keep]
            a = pj.auroc(p, y)
            if a is not None:
                draws[name]["auroc"].append(a)
            paired = [(probabilities[i], outcomes[i], reference[i]) for i in keep if reference[i] is not None]
            if paired:
                s = brier_skill([x[0] for x in paired], [x[1] for x in paired], [x[2] for x in paired])
                if s is not None:
                    draws[name]["brier_skill"].append(s)
            if name in reliability_cells:
                positive = [(pp, yy) for pp, yy in zip(p, y) if pp > RELIABILITY_FLOOR]
                fit = reliability([a_ for a_, _ in positive], [b_ for _, b_ in positive]) if positive else None
                if fit is not None:
                    draws[name]["intercept"].append(fit[0])
                    draws[name]["slope"].append(fit[1])
    tail = (1.0 - level) / 2.0
    out: Dict[str, dict] = {}
    for name in cells:
        out[name] = {}
        for stat, values in draws[name].items():
            if not values:
                out[name][stat] = None
                continue
            ordered = sorted(values)
            out[name][stat] = {"lower": _quantile(ordered, tail), "upper": _quantile(ordered, 1.0 - tail), "draws": len(ordered), "left_out": replications - len(ordered)}
    return out


# -- the grid ---------------------------------------------------------------------------------------------


def grid(rows, splits, scoring: Mapping, horizon: int, taus: Sequence[float], last: date):
    """The judge's fold grid at `horizon`: the scored days, the training end of each, and the outcome at each threshold."""

    registry = measurement_fields.load_registry()
    report = rolling_exceedance_backtest(
        rows, predictor=climatology_exceedance(scoring["minimum_history"]), model_name="grid", features=("spread_bps",), registry=registry,
        decision_time=time.fromisoformat(scoring["decision_time"]), taus=tuple(taus), minimum_history=scoring["minimum_history"],
        refit_every=scoring["refit_every"], end=last, horizon=horizon,
    )
    scored = list(report.scored_dates)
    train_ends = [fold.train_end for fold in report.folds]
    outcomes = {tau: list(report.at_tau(report.taus.index(tau))[2]) for tau in taus}
    return scored, train_ends, outcomes


def day_table(name: str, document: Mapping, horizon: int, rows, splits, scoring: Mapping, states: Mapping, last: date) -> dict:
    """The days that are not risk dates at `horizon`, with the row's forecast at +5 bp, the outcome, the climatology and the labels."""

    by_date = {row.date: row for row in rows}
    scored, train_ends, outcomes = grid(rows, splits, scoring, horizon, [TAU], last)
    days = [d.isoformat() for d in scored]
    forecast = document["forecasts"][name][f"{TAU:g}"]
    if sorted(forecast) != days:
        raise SystemExit(f"{name}: the scored days at +{TAU:g} bp are not the grid's at h = {horizon}")
    off_risk = [not ann.risk_flag(splits, by_date[d].values, True) for d in scored]
    clim = climatology_column(outcomes[TAU], scored, train_ends, off_risk)
    keep = [i for i, flag in enumerate(off_risk) if flag]
    return {
        "dates": [days[i] for i in keep],
        "p": [forecast[days[i]] for i in keep],
        "y": [int(outcomes[TAU][i]) for i in keep],
        "clim": [clim[i] for i in keep],
        "regime": [splits.regime(scored[i]) for i in keep],
        "state": [gc.scarcity_state_label(states.get(scored[i])) for i in keep],
        "scored_days": len(scored),
    }


def split_cells(table: Mapping, minimum_days: int = 1) -> Dict[str, List[int]]:
    cells: Dict[str, List[int]] = {"all": list(range(len(table["y"])))}
    for key, prefix in (("regime", "regime "), ("state", "scarcity state ")):
        for label in sorted(set(table[key])):
            positions = [i for i, v in enumerate(table[key]) if v == label]
            if len(positions) >= minimum_days:
                cells[prefix + label] = positions
    return cells


def measure_row(table: Mapping, bootstrap: Mapping) -> dict:
    cells = split_cells(table)
    ci = intervals(
        cells, table["p"], table["y"], table["clim"], seed=bootstrap["seed"], replications=bootstrap["replications"],
        block_length=bootstrap["block_length"], level=bootstrap["level"],
    )
    out = {}
    for name, positions in cells.items():
        stats = cell_statistics([table["p"][i] for i in positions], [table["y"][i] for i in positions], [table["clim"][i] for i in positions])
        stats["intervals"] = ci[name]
        out[name] = stats
    return out


# -- step 2: a day-level model on the days that are not risk dates -----------------------------------------

TAIL = "sofr_p99_iorb_bps"
DISTANCE = "satiation_dist_roll"
#: the four inputs of the day-level model, in the order of its design (the inputs that showed separation in #601 and #564)
INPUTS = ("tail_level", "tail_change_5", "dispersion_p99_p1", "satiation_distance")
#: the tail spread's change is over this many scored days
CHANGE_DAYS = 5
READ_FIELDS = (TAIL, "sofr_p99", "sofr_p1", DISTANCE)


def design_rows(reads: Sequence[Mapping[str, Optional[float]]], states: Sequence[Optional[float]]) -> List[Optional[List[float]]]:
    """The four inputs of each scored day, from the as-of reads of the scored days in date order, or None when any is a hole.

    `reads[k]` is what the information rule gives at scored day `k`'s own decision instant. The tail spread's change is its read less its
    read `CHANGE_DAYS` scored days earlier, both public at day `k`'s decision (a later read of an earlier day is never used); the dispersion
    is the 99th less the 1st percentile. A day whose state is unknown is left out.
    """

    if len(reads) != len(states):
        raise ValueError("reads and states must be one per scored day")
    out: List[Optional[List[float]]] = []
    for k, read in enumerate(reads):
        tail, p99, p1, dist = read.get(TAIL), read.get("sofr_p99"), read.get("sofr_p1"), read.get(DISTANCE)
        earlier = reads[k - CHANGE_DAYS].get(TAIL) if k >= CHANGE_DAYS else None
        if None in (tail, p99, p1, dist, earlier) or states[k] is None:
            out.append(None)
            continue
        out.append([float(tail), float(tail) - float(earlier), float(p99) - float(p1), float(dist)])
    return out


def variant_vector(form: str, row: Sequence[float], state: float) -> List[float]:
    """The design row of a form: `interaction` is the inputs, the state and the inputs times the state; `monotone` the inputs and the state."""

    if form == "interaction":
        return list(row) + [state] + [x * state for x in row]
    if form == "monotone":
        return list(row) + [state]
    raise ValueError(f"form {form!r} is not declared")


def require_observable_pairs(pairs, fitted_at: date) -> None:
    """Refuse a training pair of a day after the fit (`group_calibration.require_observable`)."""

    gc.require_observable(pairs, fitted_at)


def walk_forward_day_model(
    designs: Sequence[Optional[Sequence[float]]],
    outcomes: Mapping[float, Sequence[int]],
    scored: Sequence[date],
    train_ends: Sequence[date],
    off_risk: Sequence[bool],
    *,
    kind: str,
    monotone: Optional[Sequence[int]],
    minimum_pairs: int,
    minimum_events: int,
    fit,
) -> Dict[float, List[float]]:
    """The forecast of a day-level model for each threshold on the days that are not risk dates; 0 everywhere else.

    Each refit block (the judge's cadence) is fitted on the earlier scored days that were not risk dates, have a complete design and had an
    outcome observable at the block's fit (`probability_calibration.past_positions`), and serves the block's days that are not risk
    dates and have a complete design. Nothing is fitted until those pairs number `minimum_pairs` and hold `minimum_events` pressure days
    at the threshold, or when every pair is a pressure day; the block is then left at 0.

    Raises:
        ValueError: for columns of different lengths.
        LookAheadError: if a training pair is of a day after the block's fit.
    """

    n = len(scored)
    if len({len(designs), len(train_ends), len(off_risk), *(len(v) for v in outcomes.values())} | {n}) != 1:
        raise ValueError("designs, outcomes, dates, train ends and risk flags must be one per scored day")
    columns = {tau: [0.0] * n for tau in outcomes}
    for start, stop, end in pc.blocks(scored, train_ends):
        past = [i for i in pc.past_positions(scored, train_ends, start) if off_risk[i] and designs[i] is not None]
        served = [i for i in range(start, stop) if off_risk[i] and designs[i] is not None]
        if not served:
            continue
        for tau, outcome in outcomes.items():
            pairs = [(scored[i], 0.0, outcome[i], "") for i in past]
            require_observable_pairs(pairs, end)
            events = sum(outcome[i] for i in past)
            if len(past) < minimum_pairs or events < minimum_events or events == len(past):
                continue
            fitted = fit(kind, [list(designs[i]) for i in past], [outcome[i] for i in past], [list(designs[i]) for i in served], monotone)
            for i, value in zip(served, fitted):
                columns[tau][i] = float(value)
    return columns


def monotone_across_thresholds(columns: Mapping[float, Sequence[float]], taus: Sequence[float]) -> Dict[float, List[float]]:
    """The forecast curve across thresholds made non-increasing in the threshold (`probability_calibration.monotone_curves`)."""

    curves = pc.monotone_curves(list(zip(*(columns[tau] for tau in taus))))
    return {tau: [curve[k] for curve in curves] for k, tau in enumerate(taus)}


def combine(
    best: Mapping[float, Sequence[float]], model: Mapping[float, Sequence[float]], off_risk: Sequence[bool], taus: Sequence[float]
) -> Dict[float, List[float]]:
    """`best`'s forecasts with the model's on the days that are not risk dates, where the row forecasts exactly 0.

    Raises:
        ValueError: if the row forecast above 0 on a day that is not a risk date (it must be the constant 0 the model replaces).
    """

    out = {}
    for tau in taus:
        column = []
        for k, flag in enumerate(off_risk):
            if flag and best[tau][k] != 0.0:
                raise ValueError("the best row forecast a non-zero probability on a day that is not a risk date")
            column.append(model[tau][k] if flag else best[tau][k])
        out[tau] = column
    return out


# -- the per-release satiation distance and the as-of reads ----------------------------------------------


def per_release_panel_command(args) -> int:
    """The scratch panel with the rolling satiation distance built per H.4.1 release (#622, ruling on #541).

    `scripts/satiation_distance_598.py panel` builds the two columns with a registry that dates the H.4.1 five days after its Wednesday. The
    rows the distance joins read the H.4.1 per release (`metadata/h41_release_dating.json`), so the ratio here is read per release too:
    the same builder, the same constants (`metadata/satiation_587.json`), the registry release-dated for the run. The panel written
    is a scratch input of this measurement and is not committed.
    """

    end = date.fromisoformat(rds.committed_declaration(STEP_ONE_DECLARATION)["scoring"]["last_day"])
    require_unlocked([end], where="off_risk_day_624")
    rolling = sd.rolling_constants()
    rows = [row for row in load_daily_panel(args.panel) if row.date <= end]
    kw = dict(q=rolling["quantile"], window=rolling["window_rows"], minimum=rolling["minimum_rows"])
    registry = h41_release.release_dated_registry(measurement_fields.load_registry(), h41_release.load_release_dating(ann.H41))
    with sd.switched_on(), h41_release.release_dating():
        rule = InformationRule(registry, sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)
        built = sat.build_distance_columns(rows, rule, last_day=end, **kw)
        sat.check_distance_no_future(rows, built, rule, last_day=end, indices=range(0, len(built), args.check_every), **kw)
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + [sat.DISTANCE_COLUMN, sat.HINGE_COLUMN]))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in built:
            writer.writerow([row.date.isoformat()] + [sd._cell(row.values.get(name)) for name in header[1:]])
    older = {row.date: row.values.get(sat.DISTANCE_COLUMN) for row in load_daily_panel(args.compare_with)} if args.compare_with else {}
    changed = [
        r.date.isoformat() for r in built if r.date in older and older[r.date] is not None and r.values.get(sat.DISTANCE_COLUMN) is not None
        and abs(older[r.date] - r.values[sat.DISTANCE_COLUMN]) > 1e-12
    ]
    print(json.dumps({
        "output": str(args.output), "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "rows": len(built),
        "rows_that_differ_from_the_old_lag_build": len(changed),
    }, indent=1))
    return 0


def read_features(rows, registry, last: date, horizon: int, fields: Sequence[str] = READ_FIELDS) -> Dict[str, Dict[str, Optional[float]]]:
    """The as-of read of each field at the decision instant of every scored day at `horizon` (`every_day_conditioning_601.read_levels`'s read).

    Settlements are dated from the auction announcement and the H.4.1 per release (the "both" arm of #541), the distance columns are
    switched on for the run only, and every read passes the leakage and staleness guards (`asof.InformationRule`, `_as_of_folds`).
    """

    timed_rows, timed_registry = ann.arm_inputs("both", rows, registry, horizon)
    dates = [row.date for row in timed_rows]
    out: Dict[str, Dict[str, Optional[float]]] = {}
    with sd.switched_on(), h41_release.release_dating():
        rule = InformationRule(timed_registry, ("spread_bps",) + tuple(fields), decision_time=time(16, 0), horizon=horizon)
        for fold in _as_of_folds(
            timed_rows, rule, minimum_history=61, refit_every=len(timed_rows), entry="off_risk_day_624", end=last
        ):
            out[dates[fold.index].isoformat()] = {
                field: (None if fold.feature_row.values.get(field) is None else float(fold.feature_row.values[field])) for field in fields
            }
    return out


# -- the command ------------------------------------------------------------------------------------------


def measure_command(args) -> int:
    declared = rds.committed_declaration(STEP_ONE_DECLARATION)
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="off_risk_day_624")
    pj.require_scored_days(pj.load_declaration(), [last], where="off_risk_day_624")
    rows = load_daily_panel(args.scratch)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    paths = {"iorb": args.iorb, "cap": args.cap, "floors": args.floors}
    pj_script = _load("pressure_judge")
    result: Dict[str, dict] = {}
    for h in LEADS:
        documents = {}
        for kind, template in paths.items():
            document = json.loads(Path(template.format(h=h)).read_text(encoding="utf-8"))
            if document["horizon"] != h or document["panel_sha256"] != panel_sha256(args.panel):
                raise SystemExit(f"{template.format(h=h)} is not the forecasts at h = {h} on this panel")
            documents[kind] = document
        states = pj_script._scarcity_states(h, last)
        for name, kind in ROWS.items():
            table = day_table(name, documents[kind], h, rows, splits, scoring, states, last)
            result.setdefault(name, {})[str(h)] = {"scored_days": table["scored_days"], "cells": measure_row(table, declared["bootstrap"])}
            print(json.dumps({"row": name, "horizon": h, "off_risk_days": len(table["y"])}), flush=True)
    document = {"declaration": declared, "panel_sha256": panel_sha256(args.panel), "scratch_panel_sha256": panel_sha256(args.scratch), "rows": result}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(document), encoding="utf-8")
    return 0


def _f(x, digits=3):
    return "–" if x is None else f"{x:.{digits}f}"


def _iv(value, interval) -> str:
    if value is None:
        return "–"
    if interval is None:
        return f"{value:.3f}"
    return f"{value:.3f} [{interval['lower']:.3f}, {interval['upper']:.3f}]"


def markdown(document: Mapping) -> str:
    out = [
        "# Step 1: skill on the days that are not risk dates (#624)", "",
        "Generated by `scripts/off_risk_day_624.py measure`; not edited by hand.", "",
    ]
    for name, by_lead in document["rows"].items():
        out += [f"## `{name}`", ""]
        out += [
            "| lead | days | pressure days | on zero forecast | AUROC [90%] | Brier skill vs climatology [90%] | slope [90%] | intercept [90%] |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for h, entry in by_lead.items():
            c = entry["cells"]["all"]
            ci = c["intervals"]
            out.append(
                f"| {h} | {c['days']} | {c['pressure_days']} | {c['pressure_days_on_zero']} of {c['days'] - c['positive_days']} zero days | "
                f"{_iv(c['auroc'], ci['auroc'])} | {_iv(c['brier_skill'], ci['brier_skill'])} | {_iv(c['slope'], ci['slope'])} | {_iv(c['intercept'], ci['intercept'])} |"
            )
        out.append("")
        for h, entry in by_lead.items():
            out += [f"Lead {h}, by regime and as-of scarcity state.", "", "| cell | days | pressure days | AUROC [90%] | Brier skill [90%] | slope | intercept |", "|---|---|---|---|---|---|---|"]
            for cell, c in entry["cells"].items():
                if cell == "all":
                    continue
                ci = c["intervals"]
                out.append(
                    f"| {cell} | {c['days']} | {c['pressure_days']} | {_iv(c['auroc'], ci['auroc'])} | {_iv(c['brier_skill'], ci['brier_skill'])} | {_f(c['slope'])} | {_f(c['intercept'])} |"
                )
            out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--panel", type=Path, required=True, help="the published panel")
    m.add_argument("--scratch", type=Path, required=True)
    m.add_argument("--iorb", required=True, help="template with {h}: the control row's forecasts")
    m.add_argument("--cap", required=True, help="template with {h}: the tailcap75 forecasts")
    m.add_argument("--floors", required=True, help="template with {h}: the three floors' forecasts")
    m.add_argument("--output", type=Path, required=True)
    m.add_argument("--markdown", type=Path)
    m.set_defaults(func=measure_command)
    pn = sub.add_parser("panel", help="the scratch panel with the satiation distance built per H.4.1 release")
    pn.add_argument("--panel", type=Path, required=True, help="AUG2.csv")
    pn.add_argument("--output", type=Path, required=True)
    pn.add_argument("--compare-with", type=Path, help="AUG2D.csv (the old-lag build), to count the rows that differ")
    pn.add_argument("--check-every", type=int, default=25)
    pn.set_defaults(func=per_release_panel_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
