"""Live record (#215): log the published pressure model's forecast, frozen, each decision day.

Eleonora's decision of 3 October 2026 (#215). Every business day, after the
16:00 ET decision instant, `.github/workflows/live-log.yml` runs this script at
a pinned code SHA. It fetches the day's sources with the repository's own
fetchers, builds the as-of panel, runs every declared model (`MODELS`: the
published pressure model v1 now) and its baselines for horizons 1-5, and writes
one JSON record for the day, `live/YYYY-MM-DD.json`, before any outcome exists.
The workflow appends that file to the `live-log` branch.

    PYTHONPATH=src python3 scripts/live_record.py run --date YYYY-MM-DD --out-dir DIR \\
        [--work-dir W] [--raw-root R] [--pinned-sha SHA] [--status FILE] [--dry-run]
    PYTHONPATH=src python3 scripts/live_record.py pin
    PYTHONPATH=src python3 scripts/live_record.py missed --live-dir DIR --date YYYY-MM-DD

Rules this script holds, each a `ValueError`:

* a day on or before `PANEL_END` (2026-09-03) is never logged: the final test
  (#150, #151) scores no day after it, and the live record no day before;
* a day's file is written once and never overwritten;
* a run is made on its own decision day, after the decision instant: a missed
  day is never backfilled (`--dry-run` writes a record marked as one, for a
  scratch directory, and the workflow never passes it);
* a day that is not a decision day under `metadata/market_holidays.json`
  writes nothing and exits 0; a day the table does not cover is refused.

**How a forecast of a day not yet in the panel is made.** The panel's dates are
the calendar the as-of rule counts horizons on (`asof.py`). The panel built at
the decision day ends at the day before it, the last SOFR published by then.
`extend_panel` appends placeholder rows for the decision day and the next
decision days, carrying only what is known in advance: the calendar columns
(`data.CALENDAR_COLUMN_RULES`) and the Treasury settlements the auction snapshot
lists (`treasury_auctions`' `scheduled_availability`); every other cell is
empty, and the spread is the last real row's, so that a row exists. The
forecast loop (`forecast_run`) is `baseline.rolling_exceedance_backtest`'s,
walked through the target day; it computes no metric and scores no day, which
is why it does not consult the lockbox: `docs/decisions/lockbox.md` lets a model
"be trained on, and forecast, the days its as-of information set allows".
`require_reads_on_real_rows` refuses a forecast that would read anything but
the calendar or a scheduled settlement off a placeholder (`LookAheadError`).
A placeholder's label is fed to the online calibration after its own band, as
in a backtest; every calibration and recalibration step reads only labels at or
before the forecast's anchor, so no placeholder label reaches the target's
forecast.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import platform
import subprocess
import sys
import time as clock
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _script(name):
    spec = importlib.util.spec_from_file_location(f"live_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: Pressure model v1's published code path (#124, #169).
v1 = _script("pressure_model_v1")
#: The final test's frozen CRPS declaration (#220): `CRPS_COMMAND` builds the
#: published distribution and as-of persistence exactly as `compare` does.
final_test = _script("final_test_preregistration")

from repo_model import onset, pressure  # noqa: E402
from repo_model.asof import (  # noqa: E402
    KIND_OBSERVED,
    InformationRule,
    fold_grid,
    refit_blocks,
    require_refit_every,
)
from repo_model.baseline import (  # noqa: E402
    SCORING_HOLDOUT,
    ExceedanceBacktestReport,
    ScoredFold,
    _AsOfFold,
    _at_decision,
    _check_decision_relative_availability,
    _check_fitter_stayed_inside,
    _exceedance_at_folds,
    _fit_at_origin,
    _leap_at_folds,
    _ml_libraries,
    _model_settings,
    _reads_histories,
    _reads_information,
    _resolve_fields,
    _validate_prediction,
    _validate_taus,
    _with_online_settings,
    calendar_climatology_exceedance,
    persistence_logistic_exceedance,
    twcrps_weights,
)
from repo_model.contract import QUANTILE_LEVELS  # noqa: E402
from repo_model.data import (  # noqa: E402
    CALENDAR_COLUMN_RULES,
    SETTLEMENT_ZERO_COLUMNS,
    DailyObservation,
    audit_panel,
    exceeds_bp,
    load_daily_panel,
    load_point_in_time_panel,
    load_stress_thresholds,
    market_holidays,
)
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.ingest import (  # noqa: E402
    _artifact_payload,
    check_settlement_schedule,
    load_snapshot_manifest,
)
from repo_model.splits import LookAheadError, SplitError  # noqa: E402

RECORD_VERSION = 1
#: The last day of the published panel. The final test (#150) scores no day
#: after it; the live record logs no day on or before it.
PANEL_END = date(2026, 9, 3)
HORIZONS = v1.HORIZONS
DECISION = v1.DECISION
MINIMUM_HISTORY = v1.MINIMUM_HISTORY
REFIT_EVERY = v1.REFIT_EVERY
CALENDAR_FEATURES = v1.CALENDAR_FEATURES
TAUS = (5.0, 10.0)
PRESSURE_TARGETS = tuple(f"+{tau:g}bp" for tau in TAUS)
#: #139's plain leap at `onset.LEAP_JUMP_BP[h]`.
LEAP_TARGETS = ("leap",)
TARGET_NAMES = PRESSURE_TARGETS + LEAP_TARGETS
EASTERN = ZoneInfo("America/New_York")
#: v1's declared features at each horizon (`pressure_model_v1._at_horizon`).
V1_FEATURES = {h: v1._at_horizon(v1.GBM_FEATURES, h) for h in HORIZONS}
REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
THRESHOLDS = REPO / "metadata" / "stress_thresholds.json"

#: The declared models, each with the published record whose declaration it
#: runs. #150's chosen model joins this list the day #150 merges, in its own
#: pull request, with a dated version-bump record (#215, Do 6 and 7).
MODELS = (
    {
        "name": "pressure_model_v1",
        "published": "docs/runs/pressure_model_v1_h{h}.json",
    },
)
#: The published distribution's features (`compare`'s `--feature-b`), as the
#: final test freezes them; their reads are checked against the placeholders.
CRPS_FEATURES = final_test.CRPS_FEATURES
#: The published distribution (Eleonora's ruling of 4 October 2026 on #215):
#: the record `compare` published its CRPS in (#169), whose declaration the
#: final test freezes as `CRPS_COMMAND`. Each day's file carries its quantile
#: grid, and as-of persistence's, at every horizon, so that the day's CRPS can
#: be scored from the file alone.
CRPS_RECORD = "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
DISTRIBUTION_SIDES = ("published", "persistence")


def published_distribution_record(h: int) -> str:
    """The published record whose declaration the distribution at horizon `h` runs.

    At h = 1 the CRPS record (`CRPS_RECORD`). At h = 2 to 5 that declaration
    would read a Treasury settlement not yet scheduled at the decision, which
    the as-of rule refuses; there it is pressure model v1's published record at
    `h` (#169): the same gbm and nested PID, without the settlement read.
    """

    return CRPS_RECORD if h == 1 else MODELS[0]["published"].format(h=h)


def published_features(h: int) -> tuple:
    """The published distribution's features at horizon `h` (v1's `_at_horizon`)."""

    return tuple(v1._at_horizon(CRPS_FEATURES, h))
#: The code every record is made with. `None`: the merge commit that brought
#: this file onto main (`resolve_pin`). It changes only through a dated
#: version-bump record in `docs/decisions/`, and never retroactively: each
#: record carries the SHA it was made with. A pull request that changes it,
#: `resolve_pin`, or the models logged (`MODELS` and the records named here)
#: cites Eleonora's own approval in `metadata/owner_attestations.json`, which CI
#: checks (`scripts/owner_attested.py`, #256).
PINNED_CODE_SHA = None

#: The steps whose durations a record carries. Fitting and forecasting are one
#: walk-forward replay per model (the target's forecast is its last fold), so
#: they are timed together.
STEPS = (
    "fetch", "build", "fit_forecast_models", "fit_forecast_baselines",
    "fit_forecast_distributions", "write", "total",
)

#: Columns the panel is built with: everything v1 and its baselines read.
BUILD_COLUMNS = (
    "sofr", "iorb", "sofr_volume", "sofr_p25", "sofr_p75", "reserve_balances", "tga",
    "treasury_settlement", "treasury_settlement_bills", "treasury_settlement_coupons",
    "treasury_settlement_soma", "tbill_4w", "tbill_13w", "quarter_end", "tax_date",
    "days_to_month_end",
)
#: The settlement columns and the auction series each is drawn from.
SETTLEMENT_SERIES = {
    "treasury_settlement": "treasury_settlement",
    "treasury_settlement_bills": "treasury_settlement_bill",
    "treasury_settlement_coupons": "treasury_settlement_coupon",
    "treasury_settlement_soma": "treasury_settlement_soma",
}
#: The calendar columns the panel is built with, each from its rule.
CALENDAR_COLUMNS = tuple(column for column in BUILD_COLUMNS if column in CALENDAR_COLUMN_RULES)
#: What a placeholder row carries: what is known before the day.
PLACEHOLDER_COLUMNS = CALENDAR_COLUMNS + tuple(SETTLEMENT_SERIES)

RECORD_KEYS = (
    "record_version", "decision_day", "decision_instant", "code", "packages", "inputs",
    "targets", "models", "baselines", "distributions", "run",
)
BASELINE_NAMES = {
    "persistence_logistic": PRESSURE_TARGETS,
    "calendar_climatology": PRESSURE_TARGETS,
    onset.LEAP_PERSISTENCE_LOGISTIC: LEAP_TARGETS,
    onset.LEAP_CALENDAR_CLIMATOLOGY: LEAP_TARGETS,
}


# -- the calendar -------------------------------------------------------------


def is_decision_day(day: date) -> bool:
    """A weekday the market holiday table does not close.

    Raises:
        ValueError: if the table does not cover `day`. Its last year is the
            last the script can log; extending it is a reviewed change.
    """

    table = market_holidays()
    if not table.first <= day <= table.last:
        raise ValueError(
            f"{day} is outside metadata/market_holidays.json ({table.first} to "
            f"{table.last}); extend the table before logging it"
        )
    return day.weekday() < 5 and day not in table.closed


def next_decision_days(day: date, count: int) -> list:
    out = []
    current = day
    while len(out) < count:
        current += timedelta(days=1)
        if is_decision_day(current):
            out.append(current)
    return out


def previous_decision_day(day: date) -> date:
    current = day - timedelta(days=1)
    while not is_decision_day(current):
        current -= timedelta(days=1)
    return current


def require_loggable(day: date) -> None:
    if day <= PANEL_END:
        raise ValueError(
            f"{day} is on or before the panel end, {PANEL_END}: the live record logs "
            f"no day the final test (#150) can score"
        )


# -- the record ---------------------------------------------------------------


def _probability(value, where):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{where} is {value!r}, not a probability")


def _forecast_block(block, targets, where):
    if not isinstance(block, dict) or set(block) != {str(h) for h in HORIZONS}:
        raise ValueError(f"{where} must hold horizons {list(HORIZONS)}")
    for h, cells in block.items():
        if not isinstance(cells, dict) or set(cells) != set(targets):
            raise ValueError(f"{where}[{h}] must hold exactly {list(targets)}")
        for name, value in cells.items():
            _probability(value, f"{where}[{h}][{name}]")


def validate_record(record) -> None:
    """The record's schema. Raises `ValueError` naming what is wrong."""

    if not isinstance(record, dict) or set(record) != set(RECORD_KEYS) | (
        {"dry_run"} if isinstance(record, dict) and "dry_run" in record else set()
    ):
        missing = sorted(set(RECORD_KEYS) - set(record or {}))
        raise ValueError(f"a record holds exactly {list(RECORD_KEYS)}; missing {missing}")
    if record["record_version"] != RECORD_VERSION:
        raise ValueError(f"record_version must be {RECORD_VERSION}")
    day = date.fromisoformat(record["decision_day"])
    require_loggable(day)
    datetime.fromisoformat(record["decision_instant"])
    for key in ("sha", "pinned_sha"):
        if not isinstance(record["code"].get(key), str) or len(record["code"][key]) != 40:
            raise ValueError(f"code.{key} must be a full commit SHA")
    for key in ("python", "numpy", "scikit-learn"):
        if not record["packages"].get(key):
            raise ValueError(f"packages.{key} is missing")
    inputs = record["inputs"]
    if not inputs.get("snapshots"):
        raise ValueError("inputs.snapshots is empty")
    for snapshot in inputs["snapshots"]:
        if set(snapshot) != {"source_id", "sha256", "retrieved_at", "url"}:
            raise ValueError("each snapshot carries source_id, sha256, retrieved_at and url")
    for key in ("build_cutoff", "panel_sha256", "panel_last_date"):
        if not inputs.get(key):
            raise ValueError(f"inputs.{key} is missing")
    horizons = [target.get("horizon") for target in record["targets"]]
    if horizons != list(HORIZONS):
        raise ValueError(f"targets must hold horizons {list(HORIZONS)} in order")
    for target in record["targets"]:
        for key in ("target_date", "anchor_date", "train_end"):
            if date.fromisoformat(target[key]) is None:
                raise ValueError(f"targets.{key}")
        if date.fromisoformat(target["target_date"]) <= day:
            raise ValueError("a target day falls after its decision day")
        if not isinstance(target.get("anchor_spread_bp"), int):
            raise ValueError("targets.anchor_spread_bp must be whole basis points")
        if target.get("leap_threshold_bp") != onset.LEAP_JUMP_BP[target["horizon"]]:
            raise ValueError("targets.leap_threshold_bp must be onset.LEAP_JUMP_BP[h]")
    if not record["models"] or set(record["models"]) != {model["name"] for model in MODELS}:
        raise ValueError(f"models must hold exactly {[model['name'] for model in MODELS]}")
    for name, model in record["models"].items():
        if set(model.get("declaration_sha256", {})) != {str(h) for h in HORIZONS}:
            raise ValueError(f"models.{name}.declaration_sha256 must hold every horizon")
        _forecast_block(model.get("forecasts"), TARGET_NAMES, f"models.{name}.forecasts")
    if set(record["baselines"]) != set(BASELINE_NAMES):
        raise ValueError(f"baselines must hold exactly {sorted(BASELINE_NAMES)}")
    for name, targets in BASELINE_NAMES.items():
        _forecast_block(record["baselines"][name].get("forecasts"), targets, f"baselines.{name}.forecasts")
    _validate_distributions(record["distributions"])
    durations = record["run"].get("durations_seconds", {})
    if set(durations) != set(STEPS):
        raise ValueError(f"run.durations_seconds must hold {list(STEPS)}")


def _validate_distributions(block) -> None:
    """Both distributions, at every horizon, on the contract's quantile grid."""

    if not isinstance(block, dict) or set(block) != {"levels", *DISTRIBUTION_SIDES}:
        raise ValueError(f"distributions must hold levels and exactly {list(DISTRIBUTION_SIDES)}")
    if list(block["levels"]) != list(QUANTILE_LEVELS):
        raise ValueError(f"distributions.levels must be {list(QUANTILE_LEVELS)}")
    if block["published"].get("records") != {
        str(h): published_distribution_record(h) for h in HORIZONS
    }:
        raise ValueError("distributions.published.records must name each horizon's published record")
    digests = block["published"].get("declaration_sha256")
    if not isinstance(digests, dict) or set(digests) != {str(h) for h in HORIZONS} or not all(
        isinstance(digest, str) and len(digest) == 64 for digest in digests.values()
    ):
        raise ValueError("distributions.published.declaration_sha256 must hold every horizon")
    for side in DISTRIBUTION_SIDES:
        quantiles = block[side].get("quantiles_bps")
        if not isinstance(quantiles, dict) or set(quantiles) != {str(h) for h in HORIZONS}:
            raise ValueError(f"distributions.{side}.quantiles_bps must hold horizons {list(HORIZONS)}")
        for h, vector in quantiles.items():
            if not isinstance(vector, list) or len(vector) != len(QUANTILE_LEVELS) or not all(
                isinstance(value, (int, float)) and not isinstance(value, bool) for value in vector
            ):
                raise ValueError(
                    f"distributions.{side}.quantiles_bps[{h}] must be {len(QUANTILE_LEVELS)} numbers"
                )


def record_path(root: Path, day: date) -> Path:
    return Path(root) / "live" / f"{day.isoformat()}.json"


def record_bytes(record) -> bytes:
    return (json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8")


def write_record(root: Path, record):
    """Write the day's record once. Returns its path and the SHA-256 of its bytes.

    Raises:
        ValueError: on a malformed record, a day on or before `PANEL_END`, or a
            day whose file already exists.
    """

    validate_record(record)
    path = record_path(root, date.fromisoformat(record["decision_day"]))
    if path.exists():
        raise ValueError(f"{path} exists: a day's record is written once and never overwritten")
    payload = record_bytes(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
    return path, hashlib.sha256(payload).hexdigest()


# -- fetch and build ----------------------------------------------------------


def _cli(argv):
    from repo_model.cli import main as cli_main

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cli_main(argv)
    if code != 0:
        raise ValueError(f"repo_model.cli {' '.join(argv)} exited {code}")
    return out.getvalue()


def fetch(raw_root: Path, day: date) -> None:
    """The day's sources, each by the repository's own fetcher, into `raw_root`.

    The auctions have no `cli fetch` choice; `ingest.fetch_treasury_auctions`
    is the fetcher the tracked snapshot came from. Its range runs 60 days past
    the decision day so the settlements already announced are in it.
    """

    from repo_model.ingest import fetch_treasury_auctions

    end = day.isoformat()
    root = str(raw_root)
    _cli(["fetch", "nyfed-sofr", "--start", "2018-04-03", "--end", end, "--output-root", root])
    _cli(["fetch", "fred-macro", "--output-root", root])
    _cli(["fetch", "treasury-bill-rates", "--start", "2018-04-03", "--end", end, "--output-root", root])
    fetch_treasury_auctions(
        Path(raw_root), start="2017-01-03", end=(day + timedelta(days=60)).isoformat()
    )


def build(raw_root: Path, panel: Path, cutoff: datetime) -> None:
    argv = [
        "build", "--raw-root", str(raw_root), "--output", str(panel),
        "--build-cutoff", cutoff.isoformat(), "--decision-time", "16:00:00",
    ]
    for column in BUILD_COLUMNS:
        argv += ["--column", column]
    _cli(argv)


def snapshots(raw_root: Path) -> list:
    out = []
    for path in sorted(Path(raw_root).glob("*/*.manifest.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        out.append(
            {
                "source_id": manifest["source_id"],
                "sha256": manifest["sha256"],
                "retrieved_at": manifest["retrieved_at"],
                "url": manifest["url"],
            }
        )
    return out


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# -- the extended panel -------------------------------------------------------


def _settlements(pit_path: Path, days) -> dict:
    """Each day's settlement columns, as the auction snapshot lists them.

    The latest row per series and day, whatever its `available_at`: these are
    scheduled values (`treasury_auctions`' `scheduled_availability`), read
    before their day. A day the snapshot lists nothing for reads 0.0 on each
    leg, as the build's rule 8 reads it; the SOMA leg reads 0.0 only when no
    series lists the day, and is empty otherwise.
    """

    wanted = set(days)
    latest = {}
    for row in load_point_in_time_panel(Path(pit_path)):
        if row.ref_date in wanted and row.series_id in SETTLEMENT_SERIES.values():
            key = (row.series_id, row.ref_date)
            if key not in latest or row.available_at >= latest[key].available_at:
                latest[key] = row
    out = {}
    for day in days:
        listed = {series for series, when in latest if when == day}
        values = {}
        for column, series in SETTLEMENT_SERIES.items():
            if (series, day) in latest:
                values[column] = float(latest[(series, day)].value)
            elif SETTLEMENT_ZERO_COLUMNS[column] == "day" and listed:
                values[column] = None
            else:
                values[column] = 0.0
        out[day] = values
    return out


def auction_records(raw_root: Path) -> list:
    """Every record of the `treasury_auctions` snapshots under `raw_root`, verified.

    The auctions `extend_panel` judges: the build checks the ones inside its own
    window (`check_scheduled_settlements`), and the live run reads the
    placeholder days beyond it.

    Raises:
        ValueError: if a snapshot fails its checksum.
    """

    records = []
    for path in sorted(Path(raw_root).glob("*/*.manifest.json")):
        artifact = load_snapshot_manifest(path)
        if artifact.source_id == "treasury_auctions":
            records.extend(json.loads(_artifact_payload(artifact)).get("data") or [])
    return records


def extend_panel(real_rows, decision_day: date, horizon: int, pit_path: Path, auctions):
    """The panel as of `decision_day`, extended through its `horizon`-th target day.

    Returns `(rows, target_days)`. The real rows must end on the decision day
    before `decision_day`: the spread a forecast reads is the latest public at
    its decision, and a missing one would leave the as-of rule reading a
    placeholder's.

    The placeholders read their settlement columns as scheduled inputs
    (`treasury_auctions`' `scheduled_availability`), which holds only for an
    auction that closed before the declared instant on the panel day before it
    settles. The build checks that for the auctions inside its window; a
    placeholder day is outside it, so `auctions` (`auction_records`) are checked
    here against the real days and the placeholders together. A same-day
    cash-management bill settling on a target day is therefore refused.

    Raises:
        ValueError: if the real rows do not end on the previous decision day, or
            an auction settling on a real or placeholder day closed after the
            declared instant.
    """

    real = list(real_rows)
    before = previous_decision_day(decision_day)
    if not real or real[-1].date != before:
        raise ValueError(
            f"the panel ends on {real[-1].date if real else None}, not on {before}, the "
            f"decision day before {decision_day}; its spread is not yet in the snapshot"
        )
    targets = next_decision_days(decision_day, horizon)
    days = [decision_day] + targets
    block = json.loads(REGISTRY.read_text(encoding="utf-8"))["treasury_auctions"]["scheduled_availability"]
    check_settlement_schedule(auctions, [row.date for row in real] + days, block)
    settled = _settlements(pit_path, days)
    last = real[-1].values
    extended = list(real)
    for day in days:
        values = {"sofr": last["sofr"], "iorb": last["iorb"]}
        for column in CALENDAR_COLUMNS:
            values[column] = CALENDAR_COLUMN_RULES[column](day)
        values.update(settled[day])
        extended.append(DailyObservation(date=day, values=values))
    return extended, targets


def require_reads_on_real_rows(rows, rule: InformationRule, index: int, last_real: int) -> None:
    """Refuse a forecast of `rows[index]` that reads a placeholder's unknown cell.

    A read on a row after `last_real` (a placeholder) is admissible only for a
    column the placeholder carries, the calendar or a scheduled settlement.

    Raises:
        LookAheadError: if an observed read, or any read of another column,
            lands on a placeholder row.
    """

    dates = [row.date for row in rows]
    info = rule.information_set(dates, index)
    # The spread is an observed read at the anchor, so an anchor on a
    # placeholder is caught here too.
    for read in info.reads:
        if read.row > last_real and (
            read.kind == KIND_OBSERVED or read.feature not in PLACEHOLDER_COLUMNS
        ):
            raise LookAheadError(
                f"the forecast of {dates[index]} reads {read.feature} ({read.kind}) on "
                f"{dates[read.row]}, a placeholder row that does not carry it"
            )


# -- the forecast loop --------------------------------------------------------


def forecast_run(
    rows, *, predictor, model_name, features, registry, taus, horizon,
    online_calibration=None, leap_jump_bp=None,
) -> ExceedanceBacktestReport:
    """`rolling_exceedance_backtest`'s fold loop, walked through the last row, scoring nothing.

    The same grid, refit blocks, guards, predictor calls and online
    calibration, in the same order, so every curve is the one a backtest ending
    on the last row would issue. No metric is computed: the report's
    `metrics` is empty, and its `holdout_role` says it is a forecast.
    """

    declared = tuple(features)
    _field_sources, sources = _resolve_fields(declared)
    rule = InformationRule(registry, declared, decision_time=DECISION, horizon=horizon)
    refit = require_refit_every(REFIT_EVERY)
    tau_family = _validate_taus(taus)
    dates = [row.date for row in rows]
    grid = fold_grid(
        dates, registry, decision_time=DECISION, minimum_history=MINIMUM_HISTORY, horizon=horizon
    )
    if not grid or grid[-1] != len(rows) - 1:
        raise SplitError(f"{dates[-1]} is not on the fold grid")
    reads_information = _reads_information(predictor)
    reads_histories = _reads_histories(predictor)
    online = None if online_calibration is None else online_calibration(rows, rule)
    folds, scored, realized, forecast, leaps = [], [], [], [], []
    ml_libraries, settings, checked = None, {}, False
    for indices in refit_blocks(grid, refit):
        block = []
        for index in indices:
            info = rule.information_set(dates, index)
            rule.check(dates, info)
            for read in info.reads:
                _check_decision_relative_availability(
                    registry, read.fields, dates, read.row, index,
                    decision_time=DECISION, horizon=horizon,
                )
            frame = rule.frame(rows, info) if index == indices[0] else None
            if frame is not None and len(frame) < MINIMUM_HISTORY:
                raise SplitError(f"the fit for {dates[index]} has too few labels")
            block.append(_AsOfFold(index, info, frame, rule.observation(rows, info)))
        train_rows = tuple(block[0].frame)
        predicted = _exceedance_at_folds(
            predictor, train_rows, rows, rule, block, tau_family,
            reads_information=reads_information, reads_histories=reads_histories,
            uncalibrated=online is not None,
        )
        curves = _validate_prediction(predicted, len(block), tau_family)
        if leap_jump_bp is not None:
            block_leaps, _pressure = _leap_at_folds(
                predictor, train_rows, rows, rule, block, float(leap_jump_bp),
                reads_information=reads_information, reads_histories=reads_histories,
            )
            leaps.extend(block_leaps)
        parts = predicted.uncalibrated if online is not None else None
        if online is not None and (parts is None or len(parts) != len(block)):
            raise ValueError(f"{model_name} handed over no uncalibrated parts")
        for position, (fold, curve) in enumerate(zip(block, curves)):
            if not checked:
                _check_fitter_stayed_inside(predicted.features_read, declared, sources)
                ml_libraries = _ml_libraries(predicted)
                settings = _with_online_settings(_model_settings(predicted), online)
                checked = True
            if online is not None:
                vector, low, high = parts[position]
                curve = online.curve(fold.index, fold.feature_row.date, vector, low, high, tau_family)
                online.label(fold.index, rows[fold.index].spread_bps)
            forecast.append(curve)
            folds.append(
                ScoredFold(
                    train_start=train_rows[0].date, train_end=train_rows[-1].date,
                    train_rows=len(train_rows), feature_date=fold.feature_row.date,
                    scored_date=dates[fold.index],
                )
            )
            scored.append(dates[fold.index])
            realized.append(rows[fold.index].spread_bps)
    outcomes = tuple(tuple(1 if exceeds_bp(v, tau) else 0 for tau in tau_family) for v in realized)
    return ExceedanceBacktestReport(
        holdout_role=f"{SCORING_HOLDOUT}: not scored, a live forecast (#215)",
        model_name=model_name, features=declared, sources=sources,
        field_sources=_field_sources, refit_every=refit, information={},
        decision_time=DECISION, minimum_history=MINIMUM_HISTORY, panel_rows=len(rows),
        panel_first_date=dates[0], panel_last_date=dates[-1], folds=tuple(folds),
        taus=tau_family, scored_dates=tuple(scored), realized_bps=tuple(realized),
        forecast=tuple(forecast), reference=tuple(forecast), outcomes=outcomes, metrics=(),
        twcrps_weights=twcrps_weights(tau_family), ml_libraries=ml_libraries,
        model_settings=settings, horizon=horizon,
        leap_forecast=None if leap_jump_bp is None else tuple(leaps),
        leap_threshold_bp=None if leap_jump_bp is None else float(leap_jump_bp),
    )


def _cells(curve, taus):
    return {f"+{tau:g}bp": curve[taus.index(tau)] for tau in TAUS}


def v1_forecast(rows, h, registry, splits, taus):
    """Pressure model v1 at horizon `h`, as `pressure_model_v1.py publish` runs it.

    `distributional_gbm`, calibrated by nested conformal PID, recalibrated out
    of fold (`pressure.recalibrated`); the leap read off the model's own curve
    at the day's leap level (#139: under an online calibration the leap is the
    uncalibrated model's, as `rolling_exceedance_backtest` reads it).
    """

    from repo_model import ml
    from repo_model.recalibration import NestedFoldPid

    features = V1_FEATURES[h]
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=REFIT_EVERY))
        return built[-1]

    raw = forecast_run(
        rows,
        predictor=ml.gbm_exceedance(
            tuple(name for name in features if name != "spread_bps"),
            minimum_history=MINIMUM_HISTORY,
        ),
        model_name=v1.PUBLISHED, features=features, registry=registry, taus=taus,
        horizon=h, online_calibration=online, leap_jump_bp=onset.LEAP_JUMP_BP[h],
    )
    report = pressure.recalibrated(raw)
    cells = _cells(report.forecast[-1], taus)
    cells["leap"] = raw.leap_forecast[-1]
    return cells, raw


def baseline_forecasts(rows, h, registry, splits, taus) -> dict:
    """The four baselines' forecasts of the last row, at horizon `h`.

    Calendar climatology and the persistence-logistic at the thresholds, as
    `pressure_model_v1.py publish` runs them; #139's leap calendar climatology
    and leap persistence-logistic, fitted on the same refit block.
    """

    out = {}
    for name, predictor, features in (
        (
            "calendar_climatology",
            calendar_climatology_exceedance(splits, minimum_history=MINIMUM_HISTORY),
            CALENDAR_FEATURES,
        ),
        (
            "persistence_logistic",
            persistence_logistic_exceedance(minimum_history=MINIMUM_HISTORY),
            ("spread_bps",),
        ),
    ):
        report = forecast_run(
            rows, predictor=predictor, model_name=name, features=features,
            registry=registry, taus=taus, horizon=h,
        )
        out[name] = _cells(report.forecast[-1], taus)
    train_end = report.folds[-1].train_end
    target = rows[-1].date
    rule = InformationRule(registry, ("spread_bps",), decision_time=DECISION, horizon=h)
    leap = onset.LeapTargets(rows, rule, onset.LEAP_JUMP_BP[h])
    out[onset.LEAP_CALENDAR_CLIMATOLOGY] = {
        kind: onset.leap_calendar_climatology(leap, kind, [target], [train_end], splits)[0]
        for kind in LEAP_TARGETS
    }
    out[onset.LEAP_PERSISTENCE_LOGISTIC] = {
        kind: onset.leap_persistence_logistic(leap, kind, [target], [train_end])[0]
        for kind in LEAP_TARGETS
    }
    out["train_end"] = train_end
    return out


def published_declaration_sha256(h: int) -> str:
    """The SHA-256 of `published_distribution_record(h)`'s declaration, canonical JSON."""

    published = json.loads((REPO / published_distribution_record(h)).read_text(encoding="utf-8"))
    canonical = json.dumps(published["declaration"], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _compare_sides(h: int = 1, splits_path: Path = SPLITS):
    """Both sides of the final test's frozen `compare`, built as `compare` builds them.

    `CRPS_COMMAND` is parsed by the repository's own parser, and each side goes
    through `cli_eval`'s `_side`, `_online_calibration` and `_select_fitter`,
    so the fitters and the nested-PID factory are the ones `compare` runs. At
    `h` above 1 the published side drops the features `published_features`
    drops. Returns `{side: (model name, fitter, features, online factory)}` and the
    parsed arguments.
    """

    from repo_model.cli import build_parser
    from repo_model.cli_eval import FITTER_FACTORIES, _online_calibration, _select_fitter, _side

    argv = list(final_test.CRPS_COMMAND)
    # At horizon `h`, the published features (`published_features`).
    dropped = set(CRPS_FEATURES) - set(published_features(h))
    kept = []
    for position, part in enumerate(argv):
        if part in dropped and argv[position - 1] == "--feature-b":
            kept.pop()
            continue
        kept.append(part)
    argv = kept
    argv[argv.index("--splits") + 1] = str(splits_path)
    argv[argv.index("--registry") + 1] = str(REGISTRY)
    args = build_parser().parse_args(argv)
    sides = {}
    for side, key in (("persistence", "a"), ("published", "b")):
        projected, online = _online_calibration(
            _side(args, key), FITTER_FACTORIES.get(getattr(args, f"model_{key}")),
            splits=args.splits, refit_every=args.refit_every, side=f"-{key}",
        )
        name, fit = _select_fitter(projected, side=f"-{key}")
        sides[side] = (name, fit, tuple(getattr(args, f"feature_{key}")), online)
    return sides, args


def distribution_run(rows, *, fit, features, online_calibration, registry, horizon,
                     minimum_history, refit_every):
    """`paired_model_comparison`'s fold loop for one side, through the last row, scoring nothing.

    The same grid, refit blocks, guards, fits, as-of views and online
    calibration, in the same order, so the last row's quantile vector is the
    one `compare` would score; only `horizon` is the record's. Each fold's
    vector is drawn, as `compare`'s loss draws it, before its label is fed to
    the online calibration. Returns `(levels, quantiles, settings, train_end)`.
    """

    declared = tuple(features)
    _field_sources, sources = _resolve_fields(declared)
    rule = InformationRule(registry, declared, decision_time=DECISION, horizon=horizon)
    refit = require_refit_every(refit_every)
    dates = [row.date for row in rows]
    grid = fold_grid(
        dates, registry, decision_time=DECISION, minimum_history=minimum_history, horizon=horizon
    )
    if not grid or grid[-1] != len(rows) - 1:
        raise SplitError(f"{dates[-1]} is not on the fold grid")
    reads_information = _reads_information(fit)
    online = None if online_calibration is None else online_calibration(rows, rule)
    fitted, frame, settings, checked = None, (), {}, False
    levels = quantiles = None
    for indices in refit_blocks(grid, refit):
        for index in indices:
            info = rule.information_set(dates, index)
            rule.check(dates, info)
            for read in info.reads:
                _check_decision_relative_availability(
                    registry, read.fields, dates, read.row, index,
                    decision_time=DECISION, horizon=horizon,
                )
            block_frame = rule.frame(rows, info) if index == indices[0] else None
            if block_frame is not None and len(block_frame) < minimum_history:
                raise SplitError(f"the fit for {dates[index]} has too few labels")
            fold = _AsOfFold(index, info, block_frame, rule.observation(rows, info))
            if block_frame is not None:
                frame = block_frame
                fitted = _fit_at_origin(
                    fit, block_frame, minimum_history=minimum_history,
                    information=rule, reads_information=reads_information,
                )
                if not checked:
                    _check_fitter_stayed_inside(fitted.features_read, declared, sources)
                    settings = _with_online_settings(_model_settings(fitted), online)
                    checked = True
            view = _at_decision(fitted, rows, rule, fold)
            if online is not None:
                view = online.view(view, index, fold.feature_row)
            if tuple(view.levels) != tuple(QUANTILE_LEVELS):
                raise ValueError(f"the model reports quantile levels {tuple(view.levels)}")
            predicted = [float(value) for value in view.predict(fold.feature_row)]
            if online is not None:
                online.label(index, rows[index].spread_bps)
            levels, quantiles = list(view.levels), predicted
    return levels, quantiles, settings, frame[-1].date


def _require_crps_declaration(side, h, model_name, features, settings) -> None:
    """A side's run is its published declaration, field by field.

    Persistence is the CRPS record's `model_a` at every horizon. The published
    distribution is `published_distribution_record(h)`'s: the CRPS record's
    `model_b` at h = 1, v1's record's declaration after it.
    """

    if side == "persistence" or h == 1:
        source = CRPS_RECORD
        declared = json.loads((REPO / source).read_text(encoding="utf-8"))["declaration"]
        declared = declared["model_b" if side == "published" else "model_a"]
    else:
        source = published_distribution_record(h)
        declared = json.loads((REPO / source).read_text(encoding="utf-8"))["declaration"]
        model_name = declared.get("model")
    checks = {"model": model_name, "features": sorted(features)}
    for key in ("calibration", "calibration_constants", "calibration_selection"):
        if key in declared or key in settings:
            checks[key] = json.loads(json.dumps(settings.get(key)))
    for key, value in checks.items():
        expected = sorted(declared.get(key)) if key == "features" else declared.get(key)
        if expected != value:
            raise ValueError(
                f"the {side} distribution at h={h}: {key} is {value!r}, but {source} "
                f"declares {expected!r}"
            )


def distribution_forecasts(rows, h, registry, splits=None) -> dict:
    """The published distribution and as-of persistence's, for the last row, at horizon `h`.

    `splits` is unused (the nested PID reads `SPLITS` through `compare`'s own
    factory); it is taken so the three forecast calls share one signature.
    """

    sides, args = _compare_sides(h)
    out = {"declaration_sha256": published_declaration_sha256(h)}
    for side, (name, fit, features, online) in sides.items():
        levels, quantiles, settings, train_end = distribution_run(
            rows, fit=fit, features=features, online_calibration=online, registry=registry,
            horizon=h, minimum_history=args.minimum_history, refit_every=args.refit_every,
        )
        _require_crps_declaration(side, h, name, features, settings)
        out["levels"] = levels
        out[side] = quantiles
        out["train_end"] = train_end
    return out


# -- provenance ---------------------------------------------------------------


def _git(*argv) -> str:
    return subprocess.run(
        ["git", *argv], cwd=REPO, check=True, capture_output=True, text=True
    ).stdout.strip()


def resolve_pin(ref: str = "origin/main") -> str:
    """The pinned code SHA: `PINNED_CODE_SHA`, or the merge that brought this file onto main."""

    if PINNED_CODE_SHA is not None:
        return PINNED_CODE_SHA
    found = _git("rev-list", "--first-parent", "--reverse", ref, "--", "scripts/live_record.py")
    if not found:
        raise ValueError(f"scripts/live_record.py is not on {ref}'s first-parent history yet")
    return found.splitlines()[0]


def _declaration_sha256(model, h) -> str:
    published = json.loads((REPO / model["published"].format(h=h)).read_text(encoding="utf-8"))
    canonical = json.dumps(published["declaration"], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _require_declaration(model, h, raw, taus) -> None:
    """The run's declaration is the published record's, field by field."""

    declared = json.loads((REPO / model["published"].format(h=h)).read_text(encoding="utf-8"))[
        "declaration"
    ]
    settings = dict(raw.model_settings)
    checks = {
        "features": list(raw.features),
        "horizon": raw.horizon,
        "minimum_history": raw.minimum_history,
        "refit_every": raw.refit_every,
        "taus_bp": list(taus),
        "recalibration": dict(pressure.RECALIBRATION),
    }
    for key in ("calibration", "calibration_constants", "calibration_selection"):
        checks[key] = json.loads(json.dumps(settings.get(key)))
    for key, value in checks.items():
        if declared.get(key) != value:
            raise ValueError(
                f"{model['name']} at h={h}: {key} is {value!r}, but the published "
                f"declaration has {declared.get(key)!r}"
            )


def _packages() -> dict:
    from importlib.metadata import version

    return {
        "python": platform.python_version(),
        "numpy": version("numpy"),
        "scikit-learn": version("scikit-learn"),
    }


# -- commands -----------------------------------------------------------------


def _status(path, step):
    if path is not None:
        Path(path).write_text(json.dumps({"step": step}) + "\n", encoding="utf-8")


def run_command(args) -> int:
    day = date.fromisoformat(args.date)
    require_loggable(day)
    if not is_decision_day(day):
        print(json.dumps({"date": day.isoformat(), "result": "not a decision day; nothing written"}))
        return 0
    out_dir = Path(args.out_dir)
    if record_path(out_dir, day).exists():
        raise ValueError(f"{record_path(out_dir, day)} exists: a day is logged once")
    started = datetime.now(timezone.utc)
    instant = datetime.combine(day, DECISION, tzinfo=EASTERN)
    if not args.dry_run:
        now = started.astimezone(EASTERN)
        if now.date() != day or now < instant:
            raise ValueError(
                f"a record for {day} is made on that day after {instant.isoformat()}, "
                f"not at {now.isoformat()}: a missed day is never backfilled"
            )
    head = _git("rev-parse", "HEAD")
    pinned = args.pinned_sha or head
    if not args.dry_run:
        if head != pinned:
            raise ValueError(f"the checkout is {head}, not the pinned {pinned}")
        if _git("status", "--porcelain", "--untracked-files=no"):
            raise ValueError("the checkout has local changes; a record is made from the pinned tree")

    durations = {}
    work = Path(args.work_dir) if args.work_dir else out_dir.parent / f"live-work-{day.isoformat()}"
    work.mkdir(parents=True, exist_ok=True)
    tick = clock.monotonic()
    _status(args.status, "fetch")
    raw_root = Path(args.raw_root) if args.raw_root else work / "raw"
    if not args.raw_root:
        fetch(raw_root, day)
    durations["fetch"] = clock.monotonic() - tick

    tick = clock.monotonic()
    _status(args.status, "build")
    cutoff = datetime.now(timezone.utc).replace(microsecond=0)
    panel = work / "panel.csv"
    build(raw_root, panel, cutoff)
    rows = load_daily_panel(panel)
    audit_panel(rows)
    real = [row for row in rows if row.date < day]
    pit = panel.with_name(panel.stem + "_point_in_time.csv")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    splits = load_split_declaration(SPLITS)
    taus = tuple(float(tau) for tau in load_stress_thresholds(THRESHOLDS)["taus_bp"])
    auctions = auction_records(raw_root)
    extended = {h: extend_panel(real, day, h, pit, auctions) for h in HORIZONS}
    durations["build"] = clock.monotonic() - tick

    targets = []
    for h in HORIZONS:
        rows_h, target_days = extended[h]
        last_real = len(real) - 1
        for features in (V1_FEATURES[h], CALENDAR_FEATURES, ("spread_bps",), published_features(h)):
            rule = InformationRule(registry, features, decision_time=DECISION, horizon=h)
            require_reads_on_real_rows(rows_h, rule, len(rows_h) - 1, last_real)
        anchor = InformationRule(
            registry, ("spread_bps",), decision_time=DECISION, horizon=h
        ).anchor([row.date for row in rows_h], len(rows_h) - 1)
        targets.append(
            {
                "horizon": h,
                "target_date": target_days[-1].isoformat(),
                "anchor_date": rows_h[anchor].date.isoformat(),
                "anchor_spread_bp": onset.whole_bp(rows_h[anchor].spread_bps),
                "leap_threshold_bp": onset.LEAP_JUMP_BP[h],
            }
        )

    tick = clock.monotonic()
    _status(args.status, "fit_forecast_models")
    models = {}
    for model in MODELS:
        forecasts, digests = {}, {}
        for h in HORIZONS:
            cells, raw = v1_forecast(extended[h][0], h, registry, splits, taus)
            _require_declaration(model, h, raw, taus)
            forecasts[str(h)] = cells
            digests[str(h)] = _declaration_sha256(model, h)
            targets[h - 1]["train_end"] = raw.folds[-1].train_end.isoformat()
        models[model["name"]] = {
            "published": model["published"],
            "declaration_sha256": digests,
            "forecasts": forecasts,
        }
    durations["fit_forecast_models"] = clock.monotonic() - tick

    tick = clock.monotonic()
    _status(args.status, "fit_forecast_baselines")
    baselines = {name: {"forecasts": {}} for name in BASELINE_NAMES}
    for h in HORIZONS:
        got = baseline_forecasts(extended[h][0], h, registry, splits, taus)
        if got.pop("train_end").isoformat() != targets[h - 1]["train_end"]:
            raise ValueError(f"the baselines at h={h} were fitted on another refit block")
        for name in BASELINE_NAMES:
            baselines[name]["forecasts"][str(h)] = got[name]
    durations["fit_forecast_baselines"] = clock.monotonic() - tick

    tick = clock.monotonic()
    _status(args.status, "fit_forecast_distributions")
    distributions = {
        "levels": list(QUANTILE_LEVELS),
        "published": {
            "records": {str(h): published_distribution_record(h) for h in HORIZONS},
            "declaration_sha256": {str(h): published_declaration_sha256(h) for h in HORIZONS},
            "quantiles_bps": {},
        },
        "persistence": {"quantiles_bps": {}},
    }
    for h in HORIZONS:
        got = distribution_forecasts(extended[h][0], h, registry)
        if got["levels"] != list(QUANTILE_LEVELS):
            raise ValueError(f"the distributions at h={h} are on another quantile grid")
        for side in DISTRIBUTION_SIDES:
            distributions[side]["quantiles_bps"][str(h)] = got[side]
    durations["fit_forecast_distributions"] = clock.monotonic() - tick

    tick = clock.monotonic()
    _status(args.status, "write")
    record = {
        "record_version": RECORD_VERSION,
        "decision_day": day.isoformat(),
        "decision_instant": instant.isoformat(),
        "code": {"sha": head, "pinned_sha": pinned},
        "packages": _packages(),
        "inputs": {
            "snapshots": snapshots(raw_root),
            "build_cutoff": cutoff.isoformat(),
            "panel_sha256": _sha256(panel),
            "panel_last_date": real[-1].date.isoformat(),
            "registry_sha256": _sha256(REGISTRY),
            "splits_sha256": _sha256(SPLITS),
            "thresholds_sha256": _sha256(THRESHOLDS),
        },
        "targets": targets,
        "models": models,
        "baselines": baselines,
        "distributions": distributions,
        "run": {
            "started_at": started.isoformat(),
            "workflow_run": args.workflow_run,
            "durations_seconds": {},
        },
    }
    if args.dry_run:
        record["dry_run"] = True
    durations["write"] = clock.monotonic() - tick
    durations["total"] = sum(durations.values())
    record["run"]["durations_seconds"] = {step: round(durations[step], 3) for step in STEPS}
    record["run"]["finished_at"] = datetime.now(timezone.utc).isoformat()
    path, digest = write_record(out_dir, record)
    _status(args.status, "done")
    print(json.dumps({"date": day.isoformat(), "record": str(path), "sha256": digest}))
    return 0


def pin_command(args) -> int:
    print(resolve_pin(args.ref))
    return 0


def missed_command(args) -> int:
    """The decision days after the latest logged day and before `--date`: missed, never backfilled."""

    live = Path(args.live_dir) / "live"
    logged = sorted(date.fromisoformat(path.stem) for path in live.glob("*.json")) if live.is_dir() else []
    day = date.fromisoformat(args.date)
    missing = []
    if logged:
        current = logged[-1] + timedelta(days=1)
        while current < day:
            if is_decision_day(current):
                missing.append(current.isoformat())
            current += timedelta(days=1)
    print(json.dumps({"missed": missing}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="log one decision day")
    run.add_argument("--date", required=True)
    run.add_argument("--out-dir", required=True)
    run.add_argument("--work-dir", default=None)
    run.add_argument("--raw-root", default=None, help="snapshots already fetched; skips the fetch")
    run.add_argument("--pinned-sha", default=None)
    run.add_argument("--status", default=None, help="a file naming the step in progress")
    run.add_argument("--workflow-run", default=None, help="the Actions run's URL")
    run.add_argument(
        "--dry-run", action="store_true",
        help="for a scratch directory: any day, any checkout; the record says so",
    )
    run.set_defaults(func=run_command)
    pin = sub.add_parser("pin", help="print the pinned code SHA")
    pin.add_argument("--ref", default="origin/main")
    pin.set_defaults(func=pin_command)
    missed = sub.add_parser("missed", help="decision days with no record")
    missed.add_argument("--live-dir", required=True)
    missed.add_argument("--date", required=True)
    missed.set_defaults(func=missed_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
