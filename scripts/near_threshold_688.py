"""A near-threshold bill input and a post-month-end window for the spread distribution (#688, H5 step 2): screen, walks, scoring.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every
choice is in `metadata/near_threshold_688.json`, which this script refuses to read unless it is committed and unchanged. Scored
days are 2018-06-29 to 2025-12-31 and a decision day is scored when its fifth target day is on or before 2025-12-31; no day of
the locked blind tier is read (`docs/decisions/lockbox.md`; `require_unlocked`, and the scorer's own guard). Development days give a
score and an interval, never a verdict (scoring protocol v1, #640). Neither input joins a published declaration.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/satiation_distance_598.py panel --panel AUG2.csv --output AUG2D.csv
    PYTHONPATH=src python3 scripts/near_threshold_688.py screen --panel AUG2D.csv --output OUT/screen.json
    for h in 1 2 3 4 5: for v in control bill_x_band post_month_end_window:
        PYTHONPATH=src python3 scripts/near_threshold_688.py walk --variant $v --horizon $h --published PUBLISHED.csv \\
            --panel AUG2D.csv --output OUT/${v}_h$h.json
    PYTHONPATH=src python3 scripts/near_threshold_688.py score --published PUBLISHED.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/near_threshold_688.py report --screen OUT/screen.json --score OUT/score.json --output OUT/report.md

`screen` is the declaration's screen of each input on the ordinary days. `walk` fits a variant walk-forward on the shared fold
grid with the two-part spread distribution of #632 (`ml.pressure_spread_distribution_exceedance`, structure two_part), at the
23 levels of the protocol, and keeps each scored day's quantiles. A walk at lead h scores target day s from the information
public h business days earlier (`asof.InformationRule(horizon=h)`), so the five leads of one decision day d are the walks' laws
for the targets d + 1 .. d + 5. `score` assembles them, adds the benchmarks of protocol section 4 and scores every decision day
with `scoring_protocol.day_scores`, pairing each variant with the control and with B1 and B2 (`scoring_protocol.paired_tests`).
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import random
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, derived_features, metrics, ml, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import DailyObservation, audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "near_threshold_688.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
LAST_TARGET = date(2025, 12, 31)
FIRST_DAY = date(2018, 6, 29)
SEED = 688
DECISION = time(16, 0)
HORIZONS = sp.HORIZONS
GRID = sp.GRID
#: the levels on which pinball loss, the median and the coverages are reported (the contract's fixed grid).
REPORT_LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
THRESHOLD_BP = 5.0
NEAR_FROM_BP = 2.0
WINDOW_DAYS = 3
FLAG = "post_month_end_window"
BILLS = "treasury_settlement_bills"
STATE = "reserve_scarcity_state"
#: the row the two-part model of #632 is named for in the declaration of that issue
BEST = "risk_gbm+settle+h41+dist_roll"
#: the every-day inputs each row adds to `ml.EVERY_DAY_COMPONENT_INPUTS`
EXTRA = {"control": (), "bill_x_band": (BILLS,), "post_month_end_window": (FLAG,)}
VARIANTS = ("bill_x_band", "post_month_end_window")
ROWS = ("control",) + VARIANTS
BENCHMARKS = ("B1", "B2")
MINIMUM_CELL_DAYS = 30
MINIMUM_CELL_EVENTS = 3
RESAMPLES = 1000
BLOCK = 10


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the declaration -----------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any number")
    document = json.loads(path.read_text(encoding="utf-8"))
    if len(document["model"]["variants"]) > 3:
        raise SystemExit("at most 3 rows are run (#688, #567)")
    return document


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would score a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="near_threshold_688")


# -- the readings --------------------------------------------------------------------------------------------------


def post_month_end_window(day: date) -> float:
    """1.0 on the first `WINDOW_DAYS` market days of a month, else 0.0: a function of the date and the holiday table (#677)."""

    return 1.0 if derived_features.bday_of_month(day) <= WINDOW_DAYS else 0.0


def spread_band(spread_bps: Optional[float]) -> Optional[str]:
    """The as-of spread band of #676: below 2 bp, 2 bp up to +5 bp (whole basis points: a day on +5 is not above it), above +5 bp."""

    if spread_bps is None:
        return None
    if exceeds_bp(spread_bps, THRESHOLD_BP):
        return "high"
    return "near" if spread_bps >= NEAR_FROM_BP else "low"


def state_band(state: Optional[float]) -> str:
    """The scarcity state band of the screens (#631): ample below 2, scarce at 2 or more, unknown when not read."""

    if state is None:
        return "unknown"
    return "ample" if state < 2 else "scarce"


def with_flag(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with the window flag as a column, each from its own date."""

    return [DailyObservation(row.date, {**row.values, FLAG: post_month_end_window(row.date)}) for row in rows]


@contextlib.contextmanager
def switched() -> Iterator[None]:
    """The scarcity state, the measurement fields, the distance columns and the window flag as declared inputs, for this run only.

    The flag is a calendar feature (known in advance, as `bday_of_month` is in #631): the as-of rule reads it for the scored
    day itself, whatever the lead.
    """

    from repo_model import asof

    sd = _load("satiation_distance_598")
    calendar = contract.CALENDAR_FEATURES | {FLAG}
    with sd.switched_on(), mock.patch.object(contract, "CALENDAR_FEATURES", calendar), mock.patch.object(
        asof, "CALENDAR_FEATURES", calendar
    ):
        yield


def read_inputs(
    rows: Sequence[DailyObservation],
    registry: Mapping[str, Mapping[str, object]],
    lead: int,
    columns: Sequence[str],
    *,
    first: date = FIRST_DAY,
    last: date = LAST_TARGET,
    minimum_history: int = 61,
    limit: Optional[int] = None,
) -> Dict[date, Dict[str, Optional[float]]]:
    """Each scored day's as-of value of each of `columns` at `lead`, under the 'both' arm's timing, and the as-of spread.

    A day on which a column was not public at the decision instant has `None` for it. `rows` carry the window flag
    (`with_flag`). Returns `{scored day: {column: value, "spread_bps": the as-of spread}}`.
    """

    from repo_model.asof import InformationRule, InformationSet, fold_grid
    from repo_model.splits import LookAheadError

    sd = _load("satiation_distance_598")
    rows = with_flag(rows)
    dates = [row.date for row in rows]
    scored = [i for i in fold_grid(dates, registry, decision_time=DECISION, minimum_history=minimum_history, horizon=1) if first <= dates[i] <= last]
    if limit is not None:
        scored = scored[:limit]
    refuse_locked(dates[i] for i in scored)
    out: Dict[date, Dict[str, Optional[float]]] = {}
    with switched(), sd.h41_release.release_dating():
        timed_rows, timed_registry = sd.ann.arm_inputs("both", list(rows), registry, lead)
        rule = InformationRule(timed_registry, tuple(columns), decision_time=DECISION, horizon=lead)
        wanted = {group.feature: k for k, group in enumerate(rule.groups) if k}
        for index in scored:
            info = rule.information_set(dates, index)
            cell: Dict[str, Optional[float]] = {"spread_bps": rows[info.anchor].spread_bps}
            for column in columns:
                read = info.reads[wanted[column]]
                try:
                    rule.check(dates, InformationSet(info.scored_index, info.decision_instant, info.anchor, (read,)))
                except LookAheadError:
                    cell[column] = None
                    continue
                cell[column] = timed_rows[read.row].values.get(column)
            out[dates[index]] = cell
    return out


# -- the statistics ------------------------------------------------------------------------------------------------


def rate_cell(rows: Sequence[Tuple[int, int]], minimum_days: int = 1, minimum_events: int = 0) -> dict:
    """The pressure rate with and without the input: `rows` are `(flag, outcome)`; no difference below the declared minimums."""

    with_n = sum(1 for flag, _ in rows if flag)
    with_events = sum(1 for flag, outcome in rows if flag and outcome)
    without_n = len(rows) - with_n
    without_events = sum(1 for flag, outcome in rows if not flag and outcome)
    cell = {
        "with_n": with_n, "with_events": with_events, "without_n": without_n, "without_events": without_events,
        "with_rate": with_events / with_n if with_n else None,
        "without_rate": without_events / without_n if without_n else None,
        "difference": None,
    }
    if with_n >= minimum_days and without_n >= minimum_days and with_events + without_events >= minimum_events:
        cell["difference"] = cell["with_rate"] - cell["without_rate"]
    return cell


def stratified_table(rows: Sequence[Tuple[int, int, str]]) -> Dict[str, Tuple[int, int, int, int]]:
    """`(flag, outcome, stratum)` rows as `{stratum: (with events, with days, without events, without days)}`."""

    table: Dict[str, List[int]] = {}
    for flag, outcome, stratum in rows:
        entry = table.setdefault(stratum, [0, 0, 0, 0])
        entry[0 if flag else 2] += 1 if outcome else 0
        entry[1 if flag else 3] += 1
    return {stratum: tuple(entry) for stratum, entry in table.items()}


def mantel_haenszel(table: Mapping[str, Tuple[int, int, int, int]]) -> Optional[float]:
    """The Mantel-Haenszel rate difference over strata that hold days on both sides; `None` when no stratum does.

    Each stratum's difference of rates is weighted by n_with * n_without / n: the weighted mean of the within-stratum
    differences, so it does not move with how the strata are populated on each side of the input.
    """

    weight_sum = difference_sum = 0.0
    for with_events, with_n, without_events, without_n in table.values():
        if with_n == 0 or without_n == 0:
            continue
        weight = with_n * without_n / (with_n + without_n)
        weight_sum += weight
        difference_sum += weight * (with_events / with_n - without_events / without_n)
    return difference_sum / weight_sum if weight_sum else None


def stratified_difference(rows: Sequence[Tuple[int, int, str]]) -> Optional[float]:
    """`mantel_haenszel` of `(flag, outcome, stratum)` rows."""

    return mantel_haenszel(stratified_table(rows))


# -- the screen ----------------------------------------------------------------------------------------------------


def _counts(flag: Sequence[int], outcome: Sequence[int], stratum: Sequence[int], strata: int, index: Optional[Sequence[int]] = None):
    """The `[with events, with days, without events, without days]` table per stratum code, over the days `index` (all if none)."""

    table = [[0, 0, 0, 0] for _ in range(strata)]
    for i in range(len(flag)) if index is None else index:
        entry = table[stratum[i]]
        if flag[i]:
            entry[0] += outcome[i]
            entry[1] += 1
        else:
            entry[2] += outcome[i]
            entry[3] += 1
    return table


def _mh(table, members) -> Optional[float]:
    """`mantel_haenszel` over the strata `members` of a (strata, 4) array."""

    return mantel_haenszel({k: tuple(table[k]) for k in members})


def _raw(table, members) -> Optional[float]:
    with_events = sum(table[k][0] for k in members)
    with_n = sum(table[k][1] for k in members)
    without_events = sum(table[k][2] for k in members)
    without_n = sum(table[k][3] for k in members)
    if not with_n or not without_n:
        return None
    return with_events / with_n - without_events / without_n


# -- the walks -----------------------------------------------------------------------------------------------------


@contextlib.contextmanager
def protocol_grid() -> Iterator[None]:
    """`ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS` with the protocol's 23 levels in place of #632's 13, for this run only."""

    settings = MappingProxyType({**ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS, "quantile_grid": tuple(GRID)})
    with mock.patch.object(ml, "PRESSURE_SPREAD_DISTRIBUTION_SETTINGS", settings):
        yield


def row_features(variant: str, horizon: int) -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
    """`(risk-date features, every-day inputs, all columns read)` of a row at `horizon`."""

    sd = _load("satiation_distance_598")
    risk = tuple(sd.variant_features(BEST, horizon))
    every_day = tuple(ml.EVERY_DAY_COMPONENT_INPUTS) + EXTRA[variant]
    return risk, every_day, tuple(dict.fromkeys(risk + every_day))


def walk_command(args) -> int:
    declared = committed_declaration()
    h, variant = args.horizon, args.variant
    if h not in declared["scoring"]["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    if variant not in declared["model"]["variants"]:
        raise SystemExit(f"{variant!r} is not a declared row")
    refuse_locked([LAST_TARGET])
    minimum = declared["scoring"]["minimum_history"]
    refit = declared["scoring"]["refit_every"]
    sd = _load("satiation_distance_598")
    panel = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(panel)
    panel = with_flag(panel)
    registry = sd.measurement_fields.load_registry()
    splits = load_split_declaration(SPLITS)
    risk, every_day, columns = row_features(variant, h)
    record: list = []
    with switched(), protocol_grid(), sd.h41_release.release_dating():
        timed_rows, timed_registry = sd.ann.arm_inputs("both", panel, registry, h)
        predictor = ml.pressure_spread_distribution_exceedance(
            risk, splits, minimum_history=minimum, structure="two_part", component_inputs=every_day, record=record
        )
        report = rolling_exceedance_backtest(
            timed_rows, predictor=predictor, model_name=variant, features=columns, registry=timed_registry,
            decision_time=DECISION, taus=(5.0, 10.0), minimum_history=minimum, refit_every=refit, end=LAST_TARGET, horizon=h,
        )
    days = [fold.scored_date.isoformat() for fold in report.folds]
    if len(record) != len(days):
        raise SystemExit(f"{variant}: {len(record)} laws recorded for {len(days)} scored days")
    laws = {day: (list(quantiles) if quantiles is not None else None) for day, (_part, quantiles) in zip(days, record)}
    parts = {day: part for day, (part, _quantiles) in zip(days, record)}
    document = {
        "variant": variant,
        "horizon": h,
        "levels": list(GRID),
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "risk_date_features": list(risk),
        "every_day_inputs": list(every_day),
        "laws": laws,
        "parts": parts,
    }
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"variant": variant, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


# -- the screen ----------------------------------------------------------------------------------------------------

#: The statistics of a screen cell. Each is a difference of pressure rates, input on minus input off, or `None`.
STATISTICS = ("raw_all", "raw_near", "raw_high", "raw_low", "stratified_all", "stratified_near")
BAND_CODE = {"low": 0, "near": 1, "high": 2}
STATE_CODE = {"ample": 0, "scarce": 1, "unknown": 2}


def cell_statistics(table) -> Dict[str, Optional[float]]:
    """The six statistics of a (9, 4) stratum table; strata are `band * 3 + state`."""

    by_band = {band: [code * 3 + state for state in range(3)] for band, code in BAND_CODE.items()}
    everything = list(range(9))
    return {
        "raw_all": _raw(table, everything),
        "raw_near": _raw(table, by_band["near"]),
        "raw_high": _raw(table, by_band["high"]),
        "raw_low": _raw(table, by_band["low"]),
        "stratified_all": _mh(table, everything),
        "stratified_near": _mh(table, by_band["near"]),
    }


def persistence_share(raw: Optional[float], stratified: Optional[float]) -> Optional[float]:
    """The share of a positive raw difference that the as-of spread band and the scarcity state account for: 1 - stratified / raw."""

    if raw is None or stratified is None or raw <= 0.0:
        return None
    return 1.0 - stratified / raw


MEMBERS = {
    "raw_all": "all", "stratified_all": "all", "persistence_share": "all",
    "raw_near": "near", "stratified_near": "near", "raw_high": "high", "raw_low": "low",
}


def qualifies(table, members: Sequence[int]) -> bool:
    """Whether the strata `members` hold the declared minimum: 30 days with and without the input, and 3 pressure days."""

    with_n = sum(table[k][1] for k in members)
    without_n = sum(table[k][3] for k in members)
    events = sum(table[k][0] + table[k][2] for k in members)
    return with_n >= MINIMUM_CELL_DAYS and without_n >= MINIMUM_CELL_DAYS and events >= MINIMUM_CELL_EVENTS


def screen_cell(flag, outcome, stratum, seed: str) -> dict:
    """The rates of one cell and its statistics; a statistic whose own strata hold too few days is `None`, with no interval."""

    flag, outcome, stratum = list(flag), list(outcome), list(stratum)
    table = _counts(flag, outcome, stratum, 9)
    cell: dict = {
        "days": len(flag), "pressure_days": sum(outcome), "input_days": sum(flag),
        "rates": {
            band: rate_cell([(int(f), int(o)) for f, o, k in zip(flag, outcome, stratum) if k // 3 == code])
            for band, code in BAND_CODE.items()
        },
        "statistics": {},
    }
    groups = {"all": list(range(9)), **{band: [code * 3 + state for state in range(3)] for band, code in BAND_CODE.items()}}
    enough = {name: qualifies(table, groups[which]) for name, which in MEMBERS.items()}
    point = cell_statistics(table)
    point["persistence_share"] = persistence_share(point["raw_all"], point["stratified_all"])
    draws: Dict[str, list] = {name: [] for name in point}
    if any(enough.values()):
        rng = random.Random(seed)
        for _ in range(RESAMPLES):
            index = metrics.stationary_bootstrap_indices(len(flag), BLOCK, rng)
            resampled = cell_statistics(_counts(flag, outcome, stratum, 9, index))
            resampled["persistence_share"] = persistence_share(resampled["raw_all"], resampled["stratified_all"])
            for name, value in resampled.items():
                if value is not None and enough[name]:
                    draws[name].append(value)
    for name, value in point.items():
        interval = None
        values = sorted(draws[name])
        if enough[name] and len(values) >= 0.5 * RESAMPLES:
            interval = [metrics._quantile(values, 0.05), metrics._quantile(values, 0.95)]
        cell["statistics"][name] = {"value": value if enough[name] else None, "interval": interval}
    return cell


def screen_command(args) -> int:
    declared = committed_declaration()
    refuse_locked([LAST_TARGET])
    sd = _load("satiation_distance_598")
    rows = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
    audit_panel(rows)
    registry = sd.measurement_fields.load_registry()
    splits = load_split_declaration(SPLITS)
    position = {row.date: index for index, row in enumerate(rows)}
    inputs = {
        "bill_x_band": lambda cell: None if cell[BILLS] is None else int(cell[BILLS] > 0.0),
        "post_month_end_window": lambda cell: None if cell[FLAG] is None else int(cell[FLAG] > 0.0),
    }
    result: dict = {name: {} for name in inputs}
    scope: dict = {}
    for lead in HORIZONS:
        read = read_inputs(rows, registry, lead, (BILLS, FLAG, STATE))
        days = [
            day for day in sorted(read)
            if not sd.ann.risk_flag(splits, rows[position[day]].values, True) and spread_band(read[day]["spread_bps"]) is not None
        ]
        scope[str(lead)] = {"scored_days": len(read), "ordinary_days": len(days)}
        outcome = {day: int(exceeds_bp(rows[position[day]].spread_bps, THRESHOLD_BP)) for day in days}
        for name, flag_of in inputs.items():
            subsets = {"pooled": [d for d in days if flag_of(read[d]) is not None]}
            for label in splits.regime_labels:
                subsets[f"regime:{label}"] = [d for d in subsets["pooled"] if splits.regime(d) == label]
            result[name][str(lead)] = {}
            for split, members in subsets.items():
                if not members:
                    continue
                result[name][str(lead)][split] = screen_cell(
                    [flag_of(read[d]) for d in members],
                    [outcome[d] for d in members],
                    [BAND_CODE[spread_band(read[d]["spread_bps"])] * 3 + STATE_CODE[state_band(read[d][STATE])] for d in members],
                    f"{SEED}:{name}:{lead}:{split}",
                )
        print(json.dumps({"lead": lead, "ordinary_days": len(days)}), flush=True)
    cells = sum(len(by_split) for by_lead in result.values() for by_split in by_lead.values())
    intervals = sum(
        1 for by_lead in result.values() for by_split in by_lead.values() for cell in by_split.values()
        for stat in cell["statistics"].values() if stat["interval"] is not None
    )
    document = {
        "declaration": "metadata/near_threshold_688.json",
        "panel_sha256": panel_sha256(args.panel),
        "first_day": FIRST_DAY.isoformat(), "last_day": LAST_TARGET.isoformat(),
        "resamples": RESAMPLES, "block": BLOCK, "seed": SEED,
        "scope": scope, "cells": cells, "statistics_with_interval": intervals,
        "regimes": list(splits.regime_labels),
        "screen": result,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "cells": cells, "statistics_with_interval": intervals}))
    return 0


# -- scoring -------------------------------------------------------------------------------------------------------


def load_laws(directory: Path, variant: str) -> Dict[int, Dict[date, Optional[List[float]]]]:
    """A row's walks at the five leads as `{h: {target day: 23 quantiles or None}}`."""

    out: Dict[int, Dict[date, Optional[List[float]]]] = {}
    for h in HORIZONS:
        document = json.loads((directory / f"{variant}_h{h}.json").read_text(encoding="utf-8"))
        if document["horizon"] != h or document["variant"] != variant:
            raise ValueError(f"{variant}_h{h}.json is not the walk of {variant} at lead {h}")
        if tuple(document["levels"]) != tuple(GRID):
            raise ValueError(f"{variant}_h{h}.json is not on the protocol's grid")
        out[h] = {
            date.fromisoformat(day): (None if law is None else [float(v) for v in law]) for day, law in document["laws"].items()
        }
    return out


def lead_forecasts(
    laws: Mapping[int, Mapping[date, Optional[Sequence[float]]]], calendar: Sequence[date]
) -> Tuple[Dict[date, Dict[int, Optional[List[float]]]], List[date]]:
    """Per-lead walks (`laws[h][target day]`) as decision-day forecasts (`out[d][h]`), and the scored decision days.

    A walk at lead h scores target `s` from the decision made h business days before it, so decision day `d` has the
    lead-h law of target `calendar[position(d) + h]`. A decision day is scored when all five targets are in their walks
    (`None` is a missing forecast, to be filled by B1; absent is not scored).
    """

    position = {day: index for index, day in enumerate(calendar)}
    candidates: Optional[set] = None
    for h in HORIZONS:
        days = set()
        for target in laws[h]:
            if target not in position:
                raise ValueError(f"target day {target} is not on the scoring calendar")
            if position[target] - h < 0:
                raise ValueError(f"lead {h} target {target} has no decision day on the calendar")
            days.add(calendar[position[target] - h])
        candidates = days if candidates is None else candidates & days
    out: Dict[date, Dict[int, Optional[List[float]]]] = {}
    for day in sorted(candidates or ()):
        out[day] = {h: laws[h][calendar[position[day] + h]] for h in HORIZONS}
    return out, sorted(out)


def day_means(cells: Mapping[Tuple[date, int], float], include) -> Dict[date, float]:
    """A decision day's mean over its leads whose cell `include(decision, h)` admits; days with none are absent."""

    sums: Dict[date, List[float]] = {}
    for (decision, h), value in cells.items():
        if include(decision, h):
            sums.setdefault(decision, []).append(value)
    return {day: sum(values) / len(values) for day, values in sums.items()}


def summarise(test: "sp.PairedTest") -> dict:
    """One pair's row: both skill bounds are the scorer's studentized ones (ruling 1, #660 and #739), like mean(d)'s (#804)."""

    skill_lower = test.skill - sp._bound(test.skill_t_draws, 1.0 - test.alpha, test.draws) * test.skill_standard_error
    return {
        "n": test.n,
        "benchmark_mean": test.benchmark_mean,
        "mean_difference": test.mean_difference,
        "skill": test.skill,
        "mean_difference_lower_95_one_sided": test.lower_mean_difference(),
        "skill_lower_95_one_sided": skill_lower,
        "skill_upper_95_one_sided": test.upper_skill(),
        "bootstrap_p": test.p_value,
        "dm_statistic": test.dm_statistic,
        "dm_p": test.dm_p_value,
    }


def pair_table(
    scores: Mapping[str, Mapping[date, float]], pairs: Sequence[Tuple[str, str]], days: Sequence[date], draws: int
) -> Dict[str, dict]:
    """`paired_tests` of each (reference, candidate) name pair on `days`; empty when the days cannot carry the lag."""

    if len(days) <= sp.HAC_LAG:
        return {}
    chosen = [({d: scores[b][d] for d in days}, {d: scores[c][d] for d in days}) for b, c in pairs]
    try:
        tests = sp.paired_tests(chosen, seed=SEED, draws=draws)
    except sp.ProtocolError:
        return {f"{b} -> {c}": _single_pair(scores, b, c, days, draws) for b, c in pairs}
    return {f"{b} -> {c}": summarise(test) for (b, c), test in zip(pairs, tests)}


def _single_pair(scores: Mapping[str, Mapping[date, float]], reference: str, candidate: str, days: Sequence[date], draws: int) -> dict:
    """One pair when the stream of pairs failed: a difference with no long-run variance cannot be studentized (#804).

    The ruling replaced the percentile interval, so none stands in. A pair whose difference is zero on every day is a
    zero row marked `identical`; any other pair the scorer refuses carries its point values and no bounds, marked
    `not_studentizable`. Neither carries a bound or a p-value. A pair that studentizes is exactly `summarise`'s row.
    """

    try:
        (test,) = sp.paired_tests(
            [({d: scores[reference][d] for d in days}, {d: scores[candidate][d] for d in days})], seed=SEED, draws=draws
        )
        return summarise(test)
    except sp.ProtocolError:
        pass
    difference = [scores[reference][d] - scores[candidate][d] for d in days]
    mean = sum(difference) / len(days)
    benchmark_mean = sum(scores[reference][d] for d in days) / len(days)
    row = {
        "n": len(days), "benchmark_mean": benchmark_mean, "mean_difference": mean,
        "skill": mean / benchmark_mean if benchmark_mean else None,
        "mean_difference_lower_95_one_sided": None, "skill_lower_95_one_sided": None, "skill_upper_95_one_sided": None,
        "bootstrap_p": None, "dm_statistic": None, "dm_p": None,
    }
    if all(value == 0.0 for value in difference):
        row.update({"identical": True})
    else:
        row.update({"not_studentizable": True})
    return row


def score_command(args) -> int:
    declared = committed_declaration()
    refuse_locked([LAST_TARGET])
    draws = args.draws
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: index for index, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    decisions, days_by_row = {}, {}
    for name in ROWS:
        decisions[name], days_by_row[name] = lead_forecasts(load_laws(args.walks, name), calendar)
    common = sorted(set.intersection(*(set(days) for days in days_by_row.values())))
    common = [day for day in common if calendar[position[day] + max(HORIZONS)] <= LAST_TARGET]
    refuse_locked(common + [calendar[position[day] + h] for day in common for h in HORIZONS])
    if not common:
        raise SystemExit("no decision day is covered by every walk")
    # a decision day on which a benchmark cannot be built is not scored for any row (the days are listed in the record)
    usable, unbuilt = [], []
    for day in common:
        try:
            pb.forecasts(pb.b1_forecast, rows, [day], registry=registry, decision_time=DECISION)
            pb.forecasts(pb.b2_forecast, rows, [day], registry=registry, decision_time=DECISION, splits=splits)
            usable.append(day)
        except sp.ProtocolError as error:
            unbuilt.append((day.isoformat(), str(error)))
    common = usable
    if args.without_day is not None:
        # #882 (finding #798): the same scoring on every decision day but one; the day must be a scored one
        common = _load("h5_splits_805").drop_day(common, args.without_day)
    b1 = pb.forecasts(pb.b1_forecast, rows, common, registry=registry, decision_time=DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, common, registry=registry, decision_time=DECISION, splits=splits)
    forecasts: Dict[str, Dict[date, Dict[int, Sequence[float]]]] = {"B1": b1, "B2": b2}
    missing = {}
    for name in ROWS:
        filled = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common)
        forecasts[name] = filled.forecasts
        missing[name] = {"days": len(filled.missing_days), "share": filled.missing_share}
    names = list(BENCHMARKS) + list(ROWS)
    primary = {n: sp.day_scores(forecasts[n], outcomes, calendar) for n in names}
    secondary = {n: sp.day_scores(forecasts[n], outcomes, calendar, score=sp.upper_tail_twcrps) for n in names}
    days = sorted(primary["B1"])
    for n in names:
        if sorted(primary[n]) != days or sorted(secondary[n]) != days:
            raise SystemExit(f"{n} does not score the same decision days as B1")
    pairs = [("control", v) for v in VARIANTS] + [(b, r) for r in ROWS for b in BENCHMARKS]
    document: dict = {
        "declaration": "metadata/near_threshold_688.json",
        "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "draws": draws, "seed": SEED,
        "decision_days_without_a_benchmark": unbuilt,
        **({"without_day": args.without_day.isoformat()} if args.without_day is not None else {}),
        "missing": missing,
        "names": names,
        "mean_primary": {n: sum(primary[n].values()) / len(days) for n in names},
        "mean_key_secondary": {n: sum(secondary[n].values()) / len(days) for n in names},
        "pooled_primary": pair_table(primary, pairs, days, draws),
        "pooled_key_secondary": pair_table(secondary, pairs, days, draws),
    }
    cells = {}
    for n in names:
        cells[n] = {}
        for decision, leads in forecasts[n].items():
            for h in HORIZONS:
                target = calendar[position[decision] + h]
                if outcomes.get(target) is not None:
                    cells[n][(decision, h)] = sp.grid_crps(leads[h], outcomes[target])
    document["by_lead"] = {
        n: {str(h): sum(v for (d, hh), v in cells[n].items() if hh == h) / sum(1 for (d, hh) in cells[n] if hh == h) for h in HORIZONS}
        for n in names
    }
    # paired by lead: each variant against the control on the grid CRPS of one lead alone
    by_lead_tests = {}
    for h in HORIZONS:
        per_day = {n: {d: v for (d, hh), v in cells[n].items() if hh == h} for n in ROWS}
        lead_days = sorted(set.intersection(*(set(m) for m in per_day.values())))
        by_lead_tests[str(h)] = pair_table(per_day, [("control", v) for v in VARIANTS], lead_days, draws)
    document["by_lead_tests"] = by_lead_tests
    by_regime = {}
    for label in splits.regime_labels:
        group = [day for day in days if splits.regime(day) == label]
        if len(group) > sp.HAC_LAG:
            by_regime[label] = {
                "n": len(group),
                "mean_primary": {n: sum(primary[n][d] for d in group) / len(group) for n in names},
                "tests": pair_table(primary, pairs, group, draws),
            }
    document["by_regime"] = by_regime

    def kind_of(day: date) -> str:
        return splits.reporting_day_type(day, row_of[day].values)

    by_type = {}
    for kind in sorted({kind_of(calendar[position[d] + h]) for d in days for h in HORIZONS}):
        include = lambda d, h, kind=kind: kind_of(calendar[position[d] + h]) == kind
        means = {n: day_means(cells[n], include) for n in names}
        group = sorted(set.intersection(*(set(m) for m in means.values())))
        if len(group) > sp.HAC_LAG:
            by_type[kind] = {
                "decision_days": len(group),
                "target_cells": sum(1 for d in days for h in HORIZONS if include(d, h)),
                "mean_primary": {n: sum(means[n][d] for d in group) / len(group) for n in names},
                "tests": pair_table(means, pairs, group, draws),
            }
    document["by_type"] = by_type
    # pinball at the contract's levels, the median's absolute error and central coverage, pooled over cells
    detail: Dict[str, Dict[Tuple[date, int], Dict[str, float]]] = {n: {} for n in names}
    for n in names:
        for decision, leads in forecasts[n].items():
            for h in HORIZONS:
                y = outcomes.get(calendar[position[decision] + h])
                if y is None:
                    continue
                q = leads[h]
                at = lambda level: q[GRID.index(level)]
                cell = {f"pinball_{level:g}": metrics.pinball_loss(level, at(level), y) for level in REPORT_LEVELS}
                cell["mae_median"] = abs(at(0.5) - y)
                cell["hit_50"] = 1.0 if at(0.25) <= y <= at(0.75) else 0.0
                cell["hit_90"] = 1.0 if at(0.05) <= y <= at(0.95) else 0.0
                detail[n][(decision, h)] = cell
    measures = [f"pinball_{level:g}" for level in REPORT_LEVELS] + ["mae_median"]
    also = {}
    for measure in measures:
        daily = {n: day_means({k: v[measure] for k, v in detail[n].items()}, lambda d, h: True) for n in names}
        group = sorted(set.intersection(*(set(m) for m in daily.values())))
        also[measure] = {
            "mean": {n: sum(daily[n][d] for d in group) / len(group) for n in names},
            "tests": pair_table(daily, [("control", v) for v in VARIANTS], group, draws),
        }
    document["also"] = also
    document["coverage"] = {
        key: {n: sum(v[key] for v in detail[n].values()) / len(detail[n]) for n in names} for key in ("hit_50", "hit_90")
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


# -- the report ----------------------------------------------------------------------------------------------------

INPUT_LABELS = {
    "bill_x_band": "bill settlement on the scored day (#676)",
    "post_month_end_window": "first three market days of the month (#677)",
}
LABELS = {
    "B1": "B1 as-of persistence",
    "B2": "B2 calendar climatology",
    "control": "control (two-part, #632)",
    "bill_x_band": "+ bill settlement (#676)",
    "post_month_end_window": "+ post-month-end window (#677)",
}


def _pp(value: Optional[float], digits: int = 1) -> str:
    return "n/a" if value is None else f"{100.0 * value:+.{digits}f}"


def _with_interval(statistic: Mapping) -> str:
    interval = statistic["interval"]
    text = _pp(statistic["value"])
    return text if interval is None else f"{text} [{_pp(interval[0])}, {_pp(interval[1])}]"


def _rate(cell: Mapping) -> str:
    if cell["with_rate"] is None or cell["without_rate"] is None:
        return f"{cell['with_events']}/{cell['with_n']} against {cell['without_events']}/{cell['without_n']}"
    return (
        f"{cell['with_events']}/{cell['with_n']} ({cell['with_rate']:.2f}) against "
        f"{cell['without_events']}/{cell['without_n']} ({cell['without_rate']:.2f})"
    )


def screen_text(screen: Mapping) -> str:
    lines = [
        "# The screen (#688)",
        "",
        "Ordinary scored days, 2018-06-29 to 2025-12-31. Pressure day: the spread strictly above +5 bp. Differences are in percentage points of "
        "the pressure rate, input on minus input off, with 90% stationary-bootstrap intervals (1000 resamples, mean block 10) where the cell holds "
        "30 days on each side and 3 pressure days. `strat.` is the Mantel-Haenszel difference over the six strata of as-of spread band by "
        "scarcity state band. The persistence share is one minus the stratified over the raw difference (negative: the strata do not explain "
        "it away, they hide more of it). Cells computed: "
        f"{screen['cells']}; statistics with an interval: {screen['statistics_with_interval']}. Nothing is corrected for multiplicity.",
        "",
    ]
    for name, by_lead in screen["screen"].items():
        lines += [f"## {INPUT_LABELS[name]}", "", "### Pooled, by lead", ""]
        lines += [
            "| lead | days | input days | near band, rate with against without | raw, near | strat., near | raw, all | strat., all | "
            "above +5 bp (persistence), with against without | raw, above +5 | persistence share |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for lead, splits in by_lead.items():
            cell = splits["pooled"]
            st = cell["statistics"]
            lines.append(
                f"| {lead} | {cell['days']} | {cell['input_days']} | {_rate(cell['rates']['near'])} | {_with_interval(st['raw_near'])} | "
                f"{_with_interval(st['stratified_near'])} | {_with_interval(st['raw_all'])} | {_with_interval(st['stratified_all'])} | "
                f"{_rate(cell['rates']['high'])} | {_with_interval(st['raw_high'])} | {_with_interval(st['persistence_share'])} |"
            )
        lines += ["", "### By regime (raw difference in the near band; stratified difference over all strata)", ""]
        header = "| regime | " + " | ".join(f"lead {lead}" for lead in by_lead) + " |"
        lines += [header, "|---|" + "---|" * len(by_lead)]
        for label in screen["regimes"]:
            if all(f"regime:{label}" not in splits for splits in by_lead.values()):
                continue
            row = []
            for lead, splits in by_lead.items():
                cell = splits.get(f"regime:{label}")
                if cell is None:
                    row.append("no days")
                    continue
                st = cell["statistics"]
                row.append(
                    f"{cell['days']} d, {cell['pressure_days']} p; near {_with_interval(st['raw_near'])}; strat. {_with_interval(st['stratified_all'])}"
                )
            lines.append(f"| {label} | " + " | ".join(row) + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def _skill(test: Mapping) -> str:
    if test["skill_lower_95_one_sided"] is None:
        why = "identical forecasts" if test.get("identical") else "no interval: the difference cannot be studentized"
        return f"{test['mean_difference']:+.4f} ({100 * test['skill']:+.2f}%; {why})"
    return (
        f"{test['mean_difference']:+.4f} ({100 * test['skill']:+.2f}% [{100 * test['skill_lower_95_one_sided']:+.2f}%, "
        f"{100 * test['skill_upper_95_one_sided']:+.2f}%]), p {test['bootstrap_p']:.3f}"
    )


def score_text(score: Mapping) -> str:
    names = score["names"]
    lines = [
        "# The model test (#688)",
        "",
        f"Decision days: {score['decision_days']['n']} ({score['decision_days']['first']} to {score['decision_days']['last']}). Grid CRPS in bp, "
        "averaged over h = 1 to 5, per decision day. A paired cell is the reference's score minus the candidate's (positive favours the "
        "candidate), its skill the same over the reference's mean, with the one-sided 95% interval of the protocol "
        f"({score['draws']} studentized stationary-bootstrap draws, seed {score['seed']}). Development days: a description, not a verdict.",
        "",
        "| row | mean grid CRPS | mean twCRPS above 0 bp | days filled with B1 |",
        "|---|---|---|---|",
    ]
    for n in names:
        filled = score["missing"].get(n)
        lines.append(
            f"| {LABELS[n]} | {score['mean_primary'][n]:.4f} | {score['mean_key_secondary'][n]:.4f} | "
            f"{'n/a' if filled is None else str(filled['days'])} |"
        )
    for key, title in (("pooled_primary", "Primary: grid CRPS"), ("pooled_key_secondary", "Key secondary: upper-tail twCRPS")):
        lines += ["", f"## {title}, pooled", "", "| pair | difference (skill [95% bounds]), bootstrap p |", "|---|---|"]
        for pair, test in score[key].items():
            a, b = pair.split(" -> ")
            lines.append(f"| {LABELS[a]} -> {LABELS[b]} | {_skill(test)} |")
    lines += ["", "## By lead, grid CRPS of one lead alone", "", "| row | " + " | ".join(f"h = {h}" for h in HORIZONS) + " |", "|---|" + "---|" * len(HORIZONS)]
    for n in names:
        lines.append(f"| {LABELS[n]} | " + " | ".join(f"{score['by_lead'][n][str(h)]:.4f}" for h in HORIZONS) + " |")
    lines += ["", "Each variant against the control, by lead (difference, skill [95% bounds], p):", ""]
    lines += ["| variant | " + " | ".join(f"h = {h}" for h in HORIZONS) + " |", "|---|" + "---|" * len(HORIZONS)]
    for v in VARIANTS:
        cells = []
        for h in HORIZONS:
            test = score["by_lead_tests"][str(h)].get(f"control -> {v}")
            cells.append("n/a" if test is None else _skill(test))
        lines.append(f"| {LABELS[v]} | " + " | ".join(cells) + " |")
    for title, group in (("By regime of the decision day", score["by_regime"]), ("By pressure-day type of the target day", score["by_type"])):
        lines += ["", f"## {title}, grid CRPS", "", "| group | days | " + " | ".join(LABELS[n] for n in names) + " | " + " | ".join(f"control -> {LABELS[v]}" for v in VARIANTS) + " |"]
        lines.append("|---|---|" + "---|" * (len(names) + len(VARIANTS)))
        for label, cell in group.items():
            days = cell.get("n", cell.get("decision_days"))
            tests = cell["tests"]
            lines.append(
                f"| {label} | {days} | " + " | ".join(f"{cell['mean_primary'][n]:.4f}" for n in names) + " | "
                + " | ".join("n/a" if f"control -> {v}" not in tests else _skill(tests[f"control -> {v}"]) for v in VARIANTS) + " |"
            )
    lines += ["", "## Pinball loss at the contract's levels, the median's absolute error and central coverage", "",
              "| measure | " + " | ".join(LABELS[n] for n in names) + " |", "|---|" + "---|" * len(names)]
    for measure, cell in score["also"].items():
        lines.append(f"| {measure} | " + " | ".join(f"{cell['mean'][n]:.4f}" for n in names) + " |")
    for key in ("hit_50", "hit_90"):
        lines.append(f"| {key} (nominal {'0.50' if key == 'hit_50' else '0.90'}) | " + " | ".join(f"{score['coverage'][key][n]:.3f}" for n in names) + " |")
    lines += ["", "Each variant against the control on those measures (positive favours the variant):", "",
              "| measure | " + " | ".join(LABELS[v] for v in VARIANTS) + " |", "|---|" + "---|" * len(VARIANTS)]
    for measure, cell in score["also"].items():
        lines.append(f"| {measure} | " + " | ".join(
            "n/a" if f"control -> {v}" not in cell["tests"] else _skill(cell["tests"][f"control -> {v}"]) for v in VARIANTS) + " |")
    if score["decision_days_without_a_benchmark"]:
        lines += ["", f"Decision days without a benchmark (not scored for any row): {len(score['decision_days_without_a_benchmark'])}."]
    return "\n".join(lines) + "\n"


def report_command(args) -> int:
    screen = json.loads(args.screen.read_text(encoding="utf-8"))
    score = json.loads(args.score.read_text(encoding="utf-8"))
    args.output.write_text(screen_text(screen) + "\n" + score_text(score), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    walk = commands.add_parser("walk", help="walk-forward one row at one lead and keep each day's quantiles")
    walk.add_argument("--variant", required=True)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--published", type=Path, required=True)
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(function=walk_command)
    screen = commands.add_parser("screen", help="screen each input on the ordinary days")
    screen.add_argument("--panel", type=Path, required=True)
    screen.add_argument("--output", type=Path, required=True)
    screen.set_defaults(function=screen_command)
    score = commands.add_parser("score", help="score the walks against the control and the benchmarks")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.add_argument("--without-day", type=date.fromisoformat, default=None, help="leave this decision day out of every window (#882)")
    score.set_defaults(function=score_command)
    report = commands.add_parser("report", help="write the report from the screen and the score")
    report.add_argument("--screen", type=Path, required=True)
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(function=report_command)
    args = parser.parse_args(argv)
    return args.function(args)


if __name__ == "__main__":
    sys.exit(main())
