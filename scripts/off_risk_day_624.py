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
        --row 'risk_gbm+every_day+gate+settle+h41+iorb=OUT/iorb_h{h}.json' \\
        --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75=OUT/cap_h{h}.json' \\
        --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+floor=OUT/v610_h{h}.json' \\
        --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+state_floor=OUT/v610_h{h}.json' \\
        --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+recent_floor=OUT/v610_h{h}.json' \\
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
#: the reference rows of #681: the persistence-logistic benchmark (a probability) and the raw as-of spread (a level in bp, ranked only)
PERSISTENCE = "persistence_logistic"
SPREAD_REFERENCE = "spread_bps_asof"
STEP_THREE_DECLARATION = REPO / "metadata" / "off_risk_day_681.json"
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


def cell_statistics(
    probabilities: Sequence[float], outcomes: Sequence[int], reference: Sequence[Optional[float]], *, probability: bool = True
) -> dict:
    """The step 1 statistics of one cell of days: the outcomes, the reference being the walk-forward climatology.

    The Brier skill is taken on the days on which the reference exists. With `probability` false the column is a level, not a probability
    (the raw as-of spread of #681): only its ranking is a statistic, and the Brier skill and the reliability fit are None.
    """

    if not probability:
        return {
            "days": len(outcomes), "pressure_days": int(sum(outcomes)), "auroc": pj.auroc(list(probabilities), list(outcomes)),
            "brier_skill": None, "skill_days": 0, "positive_days": 0, "pressure_days_on_zero": 0, "intercept": None, "slope": None,
        }

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


def paired_cells(
    cells: Mapping[str, Sequence[int]],
    row: Sequence[float],
    other: Sequence[float],
    outcomes: Sequence[int],
    reference: Sequence[Optional[float]],
    *,
    seed: int,
    replications: int,
    block_length: float,
    level: float,
) -> Dict[str, dict]:
    """The row less `other` (AUROC and Brier skill against the climatology), per cell, with a 90% interval from paired resamples.

    Both rows are scored on the same days; a resample draws day positions once (the seed, block length and replications of `intervals`, so
    the draws are the ones that gave each row's own interval) and both rows keep the same drawn days of a cell. Positive favours the row.
    A difference undefined on a resample (a cell with no pressure day, say) is left out of that cell's draws and counted beside the interval.

    Raises:
        ValueError: for columns of different lengths.
    """

    n = len(outcomes)
    if not len(row) == len(other) == len(reference) == n:
        raise ValueError("the two rows, the outcomes and the reference must be one per day")
    member = {name: [False] * n for name in cells}
    for name, positions in cells.items():
        for i in positions:
            member[name][i] = True

    def differences(keep: Sequence[int]) -> Dict[str, Optional[float]]:
        a, b = pj.auroc([row[i] for i in keep], [outcomes[i] for i in keep]), pj.auroc([other[i] for i in keep], [outcomes[i] for i in keep])
        paired = [i for i in keep if reference[i] is not None]
        ys, rs = [outcomes[i] for i in paired], [reference[i] for i in paired]
        s = brier_skill([row[i] for i in paired], ys, rs)
        t = brier_skill([other[i] for i in paired], ys, rs)
        return {"auroc": None if a is None or b is None else a - b, "brier_skill": None if s is None or t is None else s - t}

    points = {name: differences(positions) for name, positions in cells.items()}
    draws: Dict[str, Dict[str, List[float]]] = {name: {"auroc": [], "brier_skill": []} for name in cells}
    rng = random.Random(seed)
    for _ in range(replications):
        drawn = stationary_bootstrap_indices(n, block_length, rng)
        for name in cells:
            keep = [i for i in drawn if member[name][i]]
            if not keep:
                continue
            for stat, value in differences(keep).items():
                if value is not None:
                    draws[name][stat].append(value)
    tail = (1.0 - level) / 2.0
    out: Dict[str, dict] = {}
    for name in cells:
        out[name] = {}
        for stat, values in draws[name].items():
            if not values or points[name][stat] is None:
                out[name][stat] = None
                continue
            ordered = sorted(values)
            out[name][stat] = {
                "difference": points[name][stat], "lower": _quantile(ordered, tail), "upper": _quantile(ordered, 1.0 - tail),
                "draws": len(ordered), "left_out": replications - len(ordered),
            }
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


def measure_row(table: Mapping, bootstrap: Mapping, *, probability: bool = True) -> dict:
    cells = split_cells(table)
    # a level has no climatology to skill-score against and no reliability curve: its reference is empty and no cell is refit
    clim = table["clim"] if probability else [None] * len(table["y"])
    ci = intervals(
        cells, table["p"], table["y"], clim, seed=bootstrap["seed"], replications=bootstrap["replications"],
        block_length=bootstrap["block_length"], level=bootstrap["level"], reliability_cells=("all",) if probability else (),
    )
    out = {}
    for name, positions in cells.items():
        stats = cell_statistics(
            [table["p"][i] for i in positions], [table["y"][i] for i in positions], [clim[i] for i in positions], probability=probability
        )
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
    extra: Optional[Mapping[float, Sequence[Optional[float]]]] = None,
) -> Dict[float, List[float]]:
    """The forecast of a day-level model for each threshold on the days that are not risk dates; 0 everywhere else.

    Each refit block (the judge's cadence) is fitted on the earlier scored days that were not risk dates, have a complete design and had an
    outcome observable at the block's fit (`probability_calibration.past_positions`), and serves the block's days that are not risk
    dates and have a complete design. Nothing is fitted until those pairs number `minimum_pairs` and hold `minimum_events` pressure days
    at the threshold, or when every pair is a pressure day; the block is then left at 0.

    `extra[tau]`, when given, is one more column of the design at that threshold (the trailing rate of pressure days, whose own reading is
    observable at each day's block); a day for which it is None has no complete design at that threshold.

    Raises:
        ValueError: for columns of different lengths.
        LookAheadError: if a training pair is of a day after the block's fit.
    """

    n = len(scored)
    lengths = {len(designs), len(train_ends), len(off_risk), n, *(len(v) for v in outcomes.values())}
    if extra is not None:
        lengths |= {len(v) for v in extra.values()}
    if len(lengths) != 1:
        raise ValueError("designs, outcomes, dates, train ends and risk flags must be one per scored day")
    columns = {tau: [0.0] * n for tau in outcomes}
    for start, stop, end in pc.blocks(scored, train_ends):
        for tau, outcome in outcomes.items():
            column = None if extra is None else extra[tau]

            def row(i):
                if designs[i] is None or (column is not None and column[i] is None):
                    return None
                return list(designs[i]) + ([] if column is None else [column[i]])

            past = [i for i in pc.past_positions(scored, train_ends, start) if off_risk[i] and row(i) is not None]
            served = [i for i in range(start, stop) if off_risk[i] and row(i) is not None]
            if not served:
                continue
            pairs = [(scored[i], 0.0, outcome[i], "") for i in past]
            require_observable_pairs(pairs, end)
            events = sum(outcome[i] for i in past)
            if len(past) < minimum_pairs or events < minimum_events or events == len(past):
                continue
            fitted = fit(kind, [row(i) for i in past], [outcome[i] for i in past], [row(i) for i in served], monotone)
            for i, value in zip(served, fitted):
                columns[tau][i] = float(value)
    return columns


def trailing_rate_column(
    outcomes: Sequence[int],
    scored: Sequence[date],
    train_ends: Sequence[date],
    off_risk: Sequence[bool],
    *,
    window: int = gc.GROUP_MINIMUM_PAIRS,
) -> List[Optional[float]]:
    """The rate of pressure days over the `window` most recent earlier scored days that were not risk dates and whose outcome was
    observable at each refit block's fit, for the days of that block; None until `window` such days exist.

    This is the rate #610's `+recent_floor` forecasts, read here as an input to a model and not as the forecast.

    Raises:
        ValueError: for columns of different lengths.
        LookAheadError: if a day read for a block is after the block's fit.
    """

    if len({len(outcomes), len(scored), len(train_ends), len(off_risk)}) != 1:
        raise ValueError("outcomes, dates, train ends and risk flags must be one per scored day")
    column: List[Optional[float]] = [None] * len(outcomes)
    for start, stop, end in pc.blocks(scored, train_ends):
        past = [i for i in pc.past_positions(scored, train_ends, start) if off_risk[i]][-window:]
        require_observable_pairs([(scored[i], 0.0, outcomes[i], "") for i in past], end)
        if len(past) < window:
            continue
        rate = sum(outcomes[i] for i in past) / len(past)
        for index in range(start, stop):
            column[index] = rate
    return column


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


def asof_spread_document(reads: Mapping[str, Mapping[str, Optional[float]]], days: Sequence[str], horizon: int) -> dict:
    """The raw as-of spread (bp) as a forecast document, so that `day_table` reads it like any row (#681): the level is the "forecast" at
    +5 bp. It is a level, not a probability, and is only ranked.

    `reads` is `read_features`'s as-of read of each scored day.

    Raises:
        ValueError: if a scored day is not on the read grid or its spread is a hole.
    """

    column: Dict[str, float] = {}
    for day in days:
        value = reads.get(day, {}).get("spread_bps")
        if value is None:
            raise ValueError(f"{day}: no as-of spread_bps read")
        column[day] = float(value)
    return {"horizon": horizon, "forecasts": {SPREAD_REFERENCE: {f"{TAU:g}": column}}}


BEST = "risk_gbm+settle+h41+dist_roll"
PARENT = "risk_gbm+settle+h41"
#: the three variants of step 2 and the form of each: (name, design form, estimator, monotone constraint on the design, trailing rate as an input)
VARIANTS = {
    "a": (BEST + "+offday", "interaction", "logistic", None, False),
    "b": (BEST + "+offday_mono", "monotone", "gbm_classifier", [0, 0, 0, 0, 1], False),
    "c": (BEST + "+offday_rate", "interaction", "logistic", None, True),
}


def declaration_document() -> dict:
    """The step 2 declaration (`metadata/off_risk_day_624.json`), written before any score of a variant."""

    step_one = json.loads(STEP_ONE_DECLARATION.read_text(encoding="utf-8"))
    common_inputs = {
        "tail_level": "the SOFR 99th percentile less IORB (bp, sofr_p99_iorb_bps), at its latest public row",
        "tail_change_5": "that read less the read 5 scored days earlier; both public at the day's decision instant",
        "dispersion_p99_p1": "the SOFR 99th percentile less the 1st (percentage points), at their latest public row",
        "satiation_distance": "the rolling satiation distance of #587 (satiation_dist_roll), built per H.4.1 release as #622 requires",
        "scarcity_state": "the reserve-scarcity state 0 to 3 as of the decision instant, each leg at its own latest public row (#586); a day whose state is unknown is not served",
    }
    return {
        "status": (
            "declared by the pull request that closes #624 after step 1 was committed (docs/pivot/off-risk-day-result.md, docs/pivot/evidence/off-risk-day/) and "
            "before any score of a step 2 variant; a measurement, not a record. Nothing here is published: no variant joins any published declaration, no day "
            "after 2025-12-31 is scored, no rule changes and the live record and pin do not move. The variants were built after seeing 2018-2025, so a pass here "
            "is not a confirmation (ruling of 11 October 2026 on #567)"
        ),
        "issue": 624,
        "step": 2,
        "scoring": step_one["scoring"],
        "thresholds_bp": [5, 10],
        "horizons": list(LEADS),
        "parent": {"row": BEST, "from": "metadata/satiation_distance_598.json, variant (a); its forecasts, on risk dates, are not changed"},
        "second_parent": CAP,
        "replaces": "the constant 0 on a day that is not a risk date (announcement_dating_rescore.risk_flag(splits, values, True)); a risk date keeps the parent's forecast",
        "step_one": "docs/pivot/off-risk-day-result.md: the control's own inputs rank the days (AUROC 0.70 to 0.75 pooled, 0.65 to 0.70 inside 2018-19) and the cap and the constant floors do not; part of a trailing rate's pooled skill is the split between regimes",
        "variants": {
            name: {
                "label": f"({key})",
                "parent": BEST,
                "form": form,
                "kind": kind,
                "monotone": monotone,
                "rate": rate,
            }
            for key, (name, form, kind, monotone, rate) in VARIANTS.items()
        },
        "variant_rules": {
            VARIANTS["a"][0]: (
                "(a) a ridge logistic (ml.PRESSURE_LOGISTIC_SETTINGS: C = 1, standardized) of a pressure day at the threshold on the four inputs, the scarcity "
                "state, and each input times the state; fitted at each refit block on the earlier scored days that were not risk dates, whose outcome was "
                "observable at the block's fit and whose inputs and state are all public; it serves the block's days that are not risk dates"
            ),
            VARIANTS["b"][0]: (
                "(b) as (a), in the gradient-boosted form (ml.PRESSURE_CLASSIFIER_SETTINGS: a HistGradientBoostingClassifier) on the four inputs and the state, with a "
                "monotone constraint of +1 on the state, so that a scarcer state never lowers the forecast; the interaction is the trees' own"
            ),
            VARIANTS["c"][0]: (
                "(c) chosen from step 1: as (a), with one more input, the rate of pressure days at the threshold over the 60 most recent earlier scored days that "
                "were not risk dates and whose outcome was observable at the block's fit (the rate #610's +recent_floor forecasts, the only row of step 1 whose "
                "pooled figures separate from the climatology at every lead). A day has the block's rate; nothing is read until 60 such days exist"
            ),
        },
        "inputs": common_inputs,
        "inputs_reading": (
            "each input is read at the decision instant of the day's own lead through asof.InformationRule, on the 'both' arm of #541 (settlements dated from "
            "the auction announcement, the H.4.1 per release), with the leakage and staleness guards of baseline._as_of_folds. The days that train a block are "
            "the same days read at their own decision instants. No outcome after the block's fit enters a training label or the trailing rate"
        ),
        "satiation_distance_version": (
            "built per H.4.1 release (scripts/off_risk_day_624.py panel), as #622 requires, and #623 has landed: scripts/satiation_distance_598.py panel "
            "makes the same build. The parent row's forecasts are re-scored on it with scripts/satiation_distance_598.py run, the same build as the variants"
        ),
        "constants": {
            "minimum_pairs": gc.GROUP_MINIMUM_PAIRS,
            "minimum_events": gc.GROUP_MINIMUM_EVENTS,
            "trailing_window": gc.GROUP_MINIMUM_PAIRS,
            "searched": "none: every constant is #606's or #610's, declared before any scoring",
            "fit": "a block is fitted only when its training pairs number minimum_pairs and hold minimum_events pressure days at the threshold, and not every pair is a pressure day; else its days are 0",
        },
        "off_risk_rule": "a scored day for which announcement_dating_rescore.risk_flag(splits, values, True) is false, as in #606 and #610",
        "cadence": "the judge's: a refit every 21 scored days from 61 days of history",
        "monotone_in_threshold": "the curve across +5 and +10 bp is made non-increasing afterwards (probability_calibration.monotone_curves), as every row's is",
        "no_hindsight_regimes": "no regime label enters a fit; the scarcity state is read as of the decision instant (ruling on #515). The back-filled 2014-2018 history is not used (the guard of #572)",
        "variants_declared": "these three; no other variant, input, window, constant or form",
        "rows": {
            "controls": [PARENT, BEST, CAP],
            "new": [v[0] for v in VARIANTS.values()],
            "pairs": {v[0]: BEST for v in VARIANTS.values()},
        },
        "judge": "the judge as in force on main (metadata/pressure_judge.json, unchanged), under the weighted rule in force and the flat rule beside it",
        "pairing": "each variant against risk_gbm+settle+h41+dist_roll and against +tailcap75, with 90% stationary-bootstrap intervals, split by regime and pressure-day type",
        "reports": [
            "tier 1 pooled and per lead, tiers 3 and 5, under the weighted rule with the flat rule beside it",
            "on the days that are not risk dates: AUROC, Brier skill against the walk-forward climatology, the reliability slope and intercept (scripts/off_risk_day_624.py measure, step 1's declaration)",
            "onsets kept and lost by date, against the parent and against +tailcap75",
            "a variant that passes a tier through its mean only is reported as such: the off-risk-day discrimination is read beside the verdict",
        ],
        "ruling_567": "these variants were built after seeing 2018-2025; a pass is not a confirmation, and a variant can replace a shortlist slot only by Eleonora's decision before the 2026 window opens",
        "published": "nothing; no variant joins any published declaration",
    }


def candidate_entries() -> dict:
    base = json.loads((CANDIDATES / f"{BEST}.json").read_text(encoding="utf-8"))
    rules = declaration_document()["variant_rules"]
    entries = {}
    for _key, (name, *_rest) in VARIANTS.items():
        entry = dict(base)
        entry["track"] = "#624"
        entry["parent"] = BEST
        entry["inputs_note"] = "the parent's risk-date part unchanged, with a day-level model on the days that are not risk dates in place of the constant 0 (the declared inputs are in metadata/off_risk_day_624.json)"
        entry["calibration"] = (
            base["calibration"].split("; metadata/satiation_distance_598.json")[0].replace("fitted on risk-date label days only and exactly 0 on every other day", "the risk-date part fitted on risk-date label days only")
            + "; then, on the days that are not risk dates, the constant 0 is replaced by a day-level model fitted walk-forward on those days only: "
            + rules[name] + "; metadata/off_risk_day_624.json"
        )
        entries[name] = entry
    return entries


def declare_command(args) -> int:
    STEP_TWO_DECLARATION.write_text(json.dumps(declaration_document(), indent=2) + "\n", encoding="utf-8")
    written = [str(STEP_TWO_DECLARATION)]
    for name, entry in candidate_entries().items():
        path = CANDIDATES / f"{name}.json"
        path.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
        written.append(str(path))
    print(json.dumps({"written": written}, indent=1))
    return 0


def persistence_declaration_document() -> dict:
    """The declaration of #681 (`metadata/off_risk_day_681.json`), written before any score of a reference row."""

    step_one = json.loads(STEP_ONE_DECLARATION.read_text(encoding="utf-8"))
    return {
        "status": (
            "declared by the pull request that closes #681 before any score of a reference row; a measurement, not a record. It adds two reference rows to "
            "the off-risk-day measurement of #624 (finding #667): CLAUDE.md requires a pressure probability to be stated against climatology and a "
            "persistence-logistic model, and #624 stated it against climatology only. Nothing is published: no rule, threshold or declaration changes, no day "
            "after 2025-12-31 is scored, and the live record and pin do not move. The days read are 2018-2025, so a result describes that history and does not "
            "confirm anything (ruling of 11 October 2026 on #567). Exploration on development data, not a verdict (scoring protocol v1, #640)"
        ),
        "issue": 681,
        "serves": "H2 (the data we hold carries signal for ordinary-day pressure) and H5",
        "scoring": step_one["scoring"],
        "bootstrap": step_one["bootstrap"],
        "population": step_one["population"],
        "outcome": step_one["outcome"],
        "statistics": step_one["statistics"],
        "reference_rows": {
            PERSISTENCE: (
                "the persistence-logistic benchmark of the judge (scripts/pressure_judge.py forecasts: pressure_judge.persistence_logistic_exceedance, a logistic "
                "regression of a pressure day at +5 bp on the as-of spread_bps, walk-forward on the judge's fold grid). A probability, so it has every statistic of "
                "step 1"
            ),
            SPREAD_REFERENCE: (
                "the raw as-of spread_bps in bp at the decision instant of the day's own lead, read through asof.InformationRule on the 'both' arm of #541 "
                "(off_risk_day_624.read_features, with its leakage and staleness guards). A level and not a probability: only its AUROC is a statistic; the Brier "
                "skill and the reliability curve are not defined for it and are reported as not applicable"
            ),
        },
        "pairing": (
            "every probability row of step 1 and step 2 is paired against persistence_logistic on the same days (the same population, the same climatology): the "
            "row less persistence_logistic for AUROC and for the Brier skill against the walk-forward climatology, pooled, by the judge's regimes (2018-19, 2020, 2021-23, 2024, 2025-26), "
            "by as-of scarcity state, at leads 1 to 5, with a 90% stationary-bootstrap interval from resamples shared by the two rows (the "
            "seed and block length of step 1). A positive difference favours the row"
        ),
        "near_empty_cells": "a cell of fewer than 10 pressure days is called near-empty on the page, and a gain that sits only in such cells is reported as such",
        "no_hindsight_regimes": "the regimes are the judge's, by calendar date; no regime label enters any forecast (ruling on #515)",
        "published": "nothing",
    }


def declare_persistence_command(args) -> int:
    STEP_THREE_DECLARATION.write_text(json.dumps(persistence_declaration_document(), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"written": [str(STEP_THREE_DECLARATION)]}, indent=1))
    return 0


def declared_document() -> dict:
    return rds.committed_declaration(STEP_TWO_DECLARATION)


def run_command(args) -> int:
    """Each declared variant at one lead: the best row's forecasts with the day-level model's on the days that are not risk dates."""

    declared = declared_document()
    for name in declared["variants"]:
        rds.committed_declaration(CANDIDATES / f"{name}.json")
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="off_risk_day_624")
    pj.require_scored_days(pj.load_declaration(), [last], where="off_risk_day_624")
    best_name = declared["parent"]["row"]
    best_document = json.loads(args.best.read_text(encoding="utf-8"))
    if best_document["horizon"] != h or best_document["panel_sha256"] != panel_sha256(args.published) or best_name not in best_document["forecasts"]:
        raise SystemExit(f"{args.best} is not the {best_name!r} forecasts at h = {h} on this panel")
    best = best_document["forecasts"][best_name]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    by_date = {row.date: row for row in rows}
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    scored, train_ends, outcomes = grid(rows, splits, scoring, h, taus, last)
    days = [d.isoformat() for d in scored]
    for tau in taus:
        if sorted(best[f"{tau:g}"]) != days:
            raise SystemExit(f"the best row's scored days at +{tau:g} bp are not the grid's at h = {h}")
    off_risk = [not ann.risk_flag(splits, by_date[d].values, True) for d in scored]
    states = _load("pressure_judge")._scarcity_states(h, last)
    state_value = [None if states.get(d) is None else float(states[d]) for d in scored]
    reads = read_features(rows, measurement_fields.load_registry(), last, h)
    missing = [d for d in days if d not in reads]
    if missing:
        raise SystemExit(f"h = {h}: {len(missing)} scored days are not on the read grid, the first {missing[0]}")
    base = design_rows([reads[d] for d in days], state_value)
    best_by_tau = {tau: [best[f"{tau:g}"][d] for d in days] for tau in taus}
    from repo_model import ml

    forecasts, settings = {}, {}
    for name, spec in declared["variants"].items():
        designs = [None if row is None else variant_vector(spec["form"], row, state_value[k]) for k, row in enumerate(base)]
        extra = (
            {tau: trailing_rate_column(outcomes[tau], scored, train_ends, off_risk, window=declared["constants"]["trailing_window"]) for tau in taus}
            if spec["rate"] else None
        )
        model = walk_forward_day_model(
            designs, {tau: outcomes[tau] for tau in taus}, scored, train_ends, off_risk, kind=spec["kind"], monotone=spec.get("monotone"),
            minimum_pairs=declared["constants"]["minimum_pairs"], minimum_events=declared["constants"]["minimum_events"],
            fit=ml.fit_off_risk_day_model, extra=extra,
        )
        column = monotone_across_thresholds(combine(best_by_tau, model, off_risk, taus), taus)
        forecasts[name] = {f"{tau:g}": {d: column[tau][k] for k, d in enumerate(days)} for tau in taus}
        served = [k for k in range(len(days)) if off_risk[k] and designs[k] is not None]
        settings[name] = {
            "parent": best_name, "off_risk_days": sum(off_risk), "served_days": len(served),
            "first_served_day": next((days[k] for k in served if model[taus[0]][k] > 0.0), None),
            "satiation_distance": "built per H.4.1 release (#622)",
        }
        print(json.dumps({"horizon": h, "row": name, "served_days": len(served)}), flush=True)
    out = {
        "horizon": h, "panel_sha256": panel_sha256(args.published), "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared, "declarations": settings, "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def _patch_pg():
    pg = _load("pooled_gate_595")
    declared = declared_document()
    pg.DECLARATION = STEP_TWO_DECLARATION
    pg.VARIANTS = {name: name for name in declared["variants"]}
    pg.ROW = CAP
    pg.PARENT = declared["parent"]["row"]
    return pg


def compare_command(args) -> int:
    """`announcement_dating_rescore.py compare` with each variant against one reference row (`+dist_roll` or `+tailcap75`)."""

    pg = _patch_pg()
    declared = declared_document()
    reference = declared["parent"]["row"] if args.reference == "distroll" else CAP
    pairs = [("variant", name, reference) for name in declared["variants"]]
    if args.reference == "distroll":
        pairs.append(("row", CAP, reference))
    ann.DECLARATION = STEP_TWO_DECLARATION
    ann.rows_of_pairs = lambda: pairs
    # the table's header in pooled_gate_595.py reads the sign the other way (#604): the difference is the reference's loss less the row's
    ann.markdown = lambda document, p: pg.comparison_markdown(document, p).replace(
        "(negative " + "favours the row)", "(the reference's squared error less the row's, so positive favours the row, #604)"
    )
    return ann.compare_command(args)


def passthrough_command(args) -> int:
    """`pooled_gate_595.py`'s onsets and summary, over these rows (the reference of onsets is +tailcap75)."""

    pg = _patch_pg()
    if args.row == "distroll":
        pg.ROW = declared_document()["parent"]["row"]
    return pg.main(args.rest)


# -- the command ------------------------------------------------------------------------------------------


def measure_command(args) -> int:
    """Each `--row NAME=TEMPLATE`: the forecasts of row NAME are in the files TEMPLATE names (with `{h}` for the lead).

    A template `asof:spread_bps` is the raw as-of spread read through the information rule (a level, ranked only; #681). With
    `--pair-with NAME`, every other probability row is also paired against row NAME on the same days (`paired_cells`).
    """

    declared = rds.committed_declaration(args.declaration)
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="off_risk_day_624")
    pj.require_scored_days(pj.load_declaration(), [last], where="off_risk_day_624")
    rows = load_daily_panel(args.scratch)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    templates = dict(item.split("=", 1) for item in args.row)
    if args.pair_with and args.pair_with not in templates:
        raise SystemExit(f"--pair-with {args.pair_with!r} is not one of the rows")
    pj_script = _load("pressure_judge")
    bootstrap = declared["bootstrap"]
    result: Dict[str, dict] = {}
    for h in LEADS:
        states = pj_script._scarcity_states(h, last)
        documents: Dict[str, dict] = {}
        tables: Dict[str, dict] = {}
        for name, template in templates.items():
            if template.startswith("asof:"):
                if template != "asof:spread_bps" or name != SPREAD_REFERENCE:
                    raise SystemExit(f"{template!r}: only the raw as-of spread_bps, as {SPREAD_REFERENCE!r}, is read from the panel")
                if template not in documents:
                    grid_days = [d.isoformat() for d in grid(rows, splits, scoring, h, [TAU], last)[0]]
                    reads = read_features(rows, measurement_fields.load_registry(), last, h, fields=("spread_bps",))
                    documents[template] = asof_spread_document(reads, grid_days, h)
                path = template
            else:
                path = template.format(h=h)
                if path not in documents:
                    document = json.loads(Path(path).read_text(encoding="utf-8"))
                    if document["horizon"] != h or document["panel_sha256"] != panel_sha256(args.panel):
                        raise SystemExit(f"{path} is not the forecasts at h = {h} on this panel")
                    documents[path] = document
            table = day_table(name, documents[path], h, rows, splits, scoring, states, last)
            tables[name] = table
            result.setdefault(name, {})[str(h)] = {
                "scored_days": table["scored_days"], "cells": measure_row(table, bootstrap, probability=name != SPREAD_REFERENCE),
            }
            print(json.dumps({"row": name, "horizon": h, "off_risk_days": len(table["y"])}), flush=True)
        if args.pair_with:
            other = tables[args.pair_with]
            for name, table in tables.items():
                if name in (args.pair_with, SPREAD_REFERENCE):
                    continue
                if table["dates"] != other["dates"] or table["y"] != other["y"] or table["clim"] != other["clim"]:
                    raise SystemExit(f"h = {h}: {name} and {args.pair_with} are not scored on the same days")
                result[name][str(h)]["paired_with_" + args.pair_with] = paired_cells(
                    split_cells(table), table["p"], other["p"], table["y"], table["clim"], seed=bootstrap["seed"],
                    replications=bootstrap["replications"], block_length=bootstrap["block_length"], level=bootstrap["level"],
                )
    document = {
        "declaration": declared, "panel_sha256": panel_sha256(args.panel), "scratch_panel_sha256": panel_sha256(args.scratch), "rows": result,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(document, args.title), encoding="utf-8")
    return 0


def _f(x, digits=3):
    return "–" if x is None else f"{x:.{digits}f}"


def _iv(value, interval) -> str:
    if value is None:
        return "–"
    if interval is None:
        return f"{value:.3f}"
    return f"{value:.3f} [{interval['lower']:.3f}, {interval['upper']:.3f}]"


def markdown(document: Mapping, title: str = "Step 1: skill on the days that are not risk dates (#624)") -> str:
    out = [
        f"# {title}", "",
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


def summary_markdown(document: Mapping, within: str = "regime 2018-19") -> str:
    """One table over the rows: per lead, the pooled cell and the cell of one regime, each as AUROC and Brier skill with 90% intervals."""

    out = [f"| row | lead | AUROC, all days [90%] | Brier skill, all days [90%] | slope, all days [90%] | AUROC, {within} [90%] | Brier skill, {within} [90%] |", "|---|---|---|---|---|---|---|"]
    for name, by_lead in document["rows"].items():
        for h, entry in by_lead.items():
            c, w = entry["cells"]["all"], entry["cells"].get(within)
            ci, wi = c["intervals"], (w or {}).get("intervals", {})
            out.append(
                f"| `{name.replace(ROW, 'ROW')}` | {h} | {_iv(c['auroc'], ci['auroc'])} | {_iv(c['brier_skill'], ci['brier_skill'])} | {_iv(c['slope'], ci['slope'])} | "
                f"{_iv(w and w['auroc'], wi.get('auroc'))} | {_iv(w and w['brier_skill'], wi.get('brier_skill'))} |"
            )
    return "\n".join(out) + "\n"


def summary_command(args) -> int:
    document = json.loads(args.input.read_text(encoding="utf-8"))
    text = summary_markdown(document, args.within)
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


dr = _load("dist_roll_606")


def calibration_markdown(judge: Mapping, names: Sequence[str]) -> str:
    """Predicted against realised at +5 bp, h = 1, per regime and per pressure-day type; tier 3 per lead; tier 5's calibration."""

    minimum = pj.load_declaration().calibration_min_events
    lines = [
        "# Predicted against realised, +5 bp (#624)", "",
        "Generated by `scripts/off_risk_day_624.py calibration` from the judge's own output. Realised minus predicted with its 90% stationary-bootstrap "
        f"interval; `tested` marks a cell with at least {minimum} pressure days (the third tier tests only those).", "",
    ]
    for dimension in ("regime", "day_type"):
        lines += [
            f"## By {dimension.replace('_', ' ')}, h = 1", "",
            "| row | " + dimension + " | days | pressure days | predicted | realised | realised minus predicted [90%] | tested | covers zero |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for name in names:
            cells = judge["candidates"][name]["horizons"]["1"]["5"]["splits"][dimension]
            for label in sorted(cells):
                c = dr.regime_cell(cells[label], minimum_events=minimum)
                lines.append(
                    f"| {name} | {label} | {c['days']:g} | {c['events']:g} | {c['predicted']:.4f} | {c['realised']:.4f} | {c['difference']:+.4f} "
                    f"[{c['lower']:+.4f}, {c['upper']:+.4f}] | {'yes' if c['tested'] else 'no'} | {'yes' if c['covers_zero'] else 'no'} |"
                )
        lines.append("")
    lines += ["## Tier 3 per lead: regimes calibrated (2018-19, 2025-26)", "", "| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |", "|---|---|---|---|---|---|"]
    for name in names:
        cells = []
        for h in range(1, 6):
            reg = judge["candidates"][name]["tiers"]["no_crying_wolf"][str(h)]["calibrated_by_regime"]
            cells.append(", ".join(f"{k}: {'yes' if v else 'no'}" for k, v in sorted(reg.items())))
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines += [
        "", "## Tier 5, week ahead", "",
        "| row | mean forecast | base rate | realised minus predicted [90%] | calibrated | Brier vs climatology [90%] | beats climatology |", "|---|---|---|---|---|---|---|",
    ]
    for name in names:
        w = judge["candidates"][name]["tiers"]["week_ahead"]
        r, b = w["realised_minus_predicted"], w["brier_difference_vs_climatology"]
        lines.append(
            f"| {name} | {w['mean_predicted']:.4f} | {w['base_rate']:.4f} | {r['mean']:+.4f} [{r['interval']['lower']:+.4f}, {r['interval']['upper']:+.4f}] | "
            f"{'yes' if w['criteria']['calibrated'] else 'no'} | {b['mean']:+.4f} [{b['interval']['lower']:+.4f}, {b['interval']['upper']:+.4f}] | "
            f"{'yes' if w['criteria']['beats_climatology_brier'] else 'no'} |"
        )
    return "\n".join(lines) + "\n"


def calibration_command(args) -> int:
    judge = json.loads(args.judge.read_text(encoding="utf-8"))
    declared = declared_document()
    names = [PARENT, BEST, CAP, *declared["variants"]]
    args.output.write_text(calibration_markdown(judge, names), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--panel", type=Path, required=True, help="the published panel")
    m.add_argument("--scratch", type=Path, required=True)
    m.add_argument("--declaration", type=Path, default=STEP_ONE_DECLARATION, help="the committed declaration whose scoring and bootstrap are used")
    m.add_argument("--row", action="append", required=True, help="NAME=TEMPLATE, TEMPLATE with {h}: the file of the row's forecasts at each lead")
    m.add_argument("--pair-with", help="a row NAME: every other probability row is also paired against it on the same days (#681)")
    m.add_argument("--title", default="Step 1: skill on the days that are not risk dates (#624)")
    m.add_argument("--output", type=Path, required=True)
    m.add_argument("--markdown", type=Path)
    m.set_defaults(func=measure_command)
    r = sub.add_parser("run")
    r.add_argument("--panel", type=Path, required=True, help="the scratch panel with the distance built per release (AUG2R.csv)")
    r.add_argument("--published", type=Path, required=True)
    r.add_argument("--horizon", type=int, required=True)
    r.add_argument("--best", type=Path, required=True, help="the file of the best row's forecasts at this lead (OUT/dist_h?.json)")
    r.add_argument("--output", type=Path, required=True)
    r.set_defaults(func=run_command)
    c = sub.add_parser("compare")
    c.add_argument("--rule", choices=("unweighted", "weighted"), default="weighted")
    c.add_argument("--reference", choices=("distroll", "tailcap"), default="distroll")
    c.add_argument("--panel", type=Path, required=True)
    c.add_argument("--output", type=Path, required=True)
    c.add_argument("--markdown", type=Path)
    c.add_argument("inputs", nargs="+", type=Path)
    c.set_defaults(func=compare_command)
    t = sub.add_parser("pg")
    t.add_argument("--row", choices=("tailcap", "distroll"), default="tailcap", help="the row that onsets are kept and lost against")
    t.add_argument("rest", nargs=argparse.REMAINDER)
    t.set_defaults(func=passthrough_command)
    sub.add_parser("declare").set_defaults(func=declare_command)
    sub.add_parser("declare-persistence", help="the declaration of #681").set_defaults(func=declare_persistence_command)
    k = sub.add_parser("calibration")
    k.add_argument("--judge", type=Path, required=True)
    k.add_argument("--output", type=Path, required=True)
    k.set_defaults(func=calibration_command)
    sm = sub.add_parser("summary")
    sm.add_argument("--input", type=Path, required=True)
    sm.add_argument("--within", default="regime 2018-19")
    sm.add_argument("--output", type=Path, required=True)
    sm.set_defaults(func=summary_command)
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
