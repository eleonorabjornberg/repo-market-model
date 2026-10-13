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


def _counts(flag: Sequence[int], outcome: Sequence[int], stratum: Sequence[int], strata: int):
    """The `(with events, with days, without events, without days)` table per stratum code, as a (strata, 4) integer array."""

    import numpy

    code = numpy.asarray(stratum) * 4 + numpy.asarray(flag) * 2 + numpy.asarray(outcome)
    cells = numpy.bincount(code, minlength=strata * 4).reshape(strata, 2, 2)  # [stratum, flag, outcome]
    return numpy.stack([cells[:, 1, 1], cells[:, 1, :].sum(axis=1), cells[:, 0, 1], cells[:, 0, :].sum(axis=1)], axis=1)


def _mh(table, members) -> Optional[float]:
    """`mantel_haenszel` over the strata `members` of a (strata, 4) array."""

    return mantel_haenszel({int(k): tuple(int(v) for v in table[k]) for k in members})


def _raw(table, members) -> Optional[float]:
    with_events = sum(int(table[k][0]) for k in members)
    with_n = sum(int(table[k][1]) for k in members)
    without_events = sum(int(table[k][2]) for k in members)
    without_n = sum(int(table[k][3]) for k in members)
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
    args = parser.parse_args(argv)
    return args.function(args)


if __name__ == "__main__":
    sys.exit(main())
