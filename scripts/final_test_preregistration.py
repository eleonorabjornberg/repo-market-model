"""The final test, part 1 (#150): choose the model on pre-2026 evidence and freeze it.

A scratch measurement, not a record: it writes pickles and JSON to the paths it
is given, and nothing into `docs/runs/`. Nothing published moves. Every scored
day is on or before 2025-12-31 (`docs/decisions/lockbox.md`): each run's
`end` is `END`, every scoring entry point refuses a locked day, and `select`
and `calibrator` refuse one again.

The pre-registration record is `docs/decisions/final-test-preregistration.md`.
The amendments of 3 October 2026 on #150 fix what is computed here:

* `candidate` runs one of the six candidates (`CANDIDATES`, the closed list,
  in the fixed simplicity ranking) at horizon 1 on its own scratch panel, and
  keeps its raw plain-leap probability at #139's `J_1` on every scored day,
  walk-forward on the shared fold grid, with its raw +5 bp probability.
* `calibrator` computes the calibrator-selection cell: the published v1's
  plain-leap Brier at h = 1 under each of `probability_calibration.CALIBRATORS`,
  each paired against Platt, and applies the rule (`choose_calibrator`).
* `select` applies that one calibrator to every candidate's raw plain-leap
  probabilities, walk-forward, scores the selection cell, and applies the
  selection rule (`choose_model`).
* `declaration` prints the frozen declaration of the chosen model and its
  checksum (`declaration`, `declaration_checksum`), which the record pins and
  `tests/test_final_test_freeze.py` checks.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output V11.csv
    PYTHONPATH=src python3 scripts/early_warning_inputs.py panel --panel PUB.csv --output EW.csv
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_preregistration.py candidate \\
        --name NAME --panel PANEL --output OUT/NAME.pickle      # PANEL: CANDIDATE_PANELS[NAME]
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_preregistration.py calibrator \\
        --panel PUB.csv --runs OUT --output OUT/calibrator.json
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/final_test_preregistration.py select \\
        --panel PUB.csv --runs OUT --calibrator METHOD --output OUT/selection.json
    PYTHONPATH=src python3 scripts/final_test_preregistration.py declaration
"""

from __future__ import annotations

import argparse
import ast
import copyreg
import dataclasses
import hashlib
import importlib.util
import json
import pickle
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset, probability_calibration as pc  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
THRESHOLDS = REPO / "metadata" / "stress_thresholds.json"
RECORD = REPO / "docs" / "decisions" / "final-test-preregistration.md"
#: The selection cell's horizon (#150, amendment of 3 October: the selection score).
HORIZON = 1
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)
#: The last day any run here may score (`docs/decisions/lockbox.md`).
END = date(2025, 12, 31)
#: The thresholds every run also carries, for the descriptive onset-day Brier.
TAUS = (5.0, 10.0)
ONSET_TAU = 5.0

#: The closed candidate list, in the fixed simplicity ranking, simplest first
#: (#150, amendment of 3 October: the candidate list).
CANDIDATES = (
    "scarcity_calendar",
    "dynamic_logit",
    "direct_logistic_sofr_p1",
    "published_v1",
    "v1_1",
    "stacked_combiner",
)
#: The scratch panel each candidate is scored on, as its own directive scored it.
CANDIDATE_PANELS = {
    "scarcity_calendar": "V11.csv (scripts/pressure_v1_1.py panel)",
    "dynamic_logit": "PUB.csv (the published panel)",
    "direct_logistic_sofr_p1": "EW.csv (scripts/early_warning_inputs.py panel)",
    "published_v1": "PUB.csv (the published panel)",
    "v1_1": "V11.csv (scripts/pressure_v1_1.py panel)",
    "stacked_combiner": "PUB.csv (the published panel)",
}
#: The candidate whose raw probabilities choose the calibrator.
CALIBRATOR_CHOOSER = "published_v1"
#: The default calibrator, replaced only by a gain whose interval excludes zero.
DEFAULT_CALIBRATOR = "platt"

#: The model the selection rule chose (`select`), frozen by the record.
CHOSEN = "dynamic_logit"
#: The calibrator the calibrator rule chose (`calibrator`), frozen by the record.
CHOSEN_CALIBRATOR = "platt_recency"


def _proxy(mapping):
    return MappingProxyType(mapping)


copyreg.pickle(MappingProxyType, lambda proxy: (_proxy, (dict(proxy),)))


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def leap_jump_bp(horizon: int = HORIZON) -> float:
    return float(onset.LEAP_JUMP_BP[horizon])


# -- the candidates ------------------------------------------------------------------


def _backtest(rows, name, predictor, features, taus, window, calibration=None):
    """One walk-forward run on the shared fold grid; `window` is `(horizon, end)`."""

    horizon, end = window
    return rolling_exceedance_backtest(
        rows,
        predictor=predictor,
        model_name=name,
        features=features,
        registry=json.loads(REGISTRY.read_text()),
        decision_time=DECISION,
        taus=taus,
        minimum_history=MINIMUM_HISTORY,
        refit_every=REFIT_EVERY,
        end=end,
        horizon=horizon,
        leap_jump_bp=leap_jump_bp(horizon),
        online_calibration=calibration,
    )


def _stress_taus():
    from repo_model.data import load_stress_thresholds

    return tuple(float(tau) for tau in load_stress_thresholds(THRESHOLDS)["taus_bp"])


def _published_v1(rows, splits, window):
    """#169's published v1 before its recalibration: the gbm with nested PID (#124)."""

    from repo_model import ml
    from repo_model.recalibration import NestedFoldPid

    v1 = _script("pressure_model_v1")
    features = v1._at_horizon(v1.GBM_FEATURES, window[0])

    def online(rows_, rule):
        return NestedFoldPid(rows_, rule, splits=splits, refit_every=REFIT_EVERY)

    return _backtest(
        rows, "distributional_gbm",
        ml.gbm_exceedance(tuple(n for n in features if n != "spread_bps"),
                          minimum_history=MINIMUM_HISTORY),
        features, _stress_taus(), window, online,
    )


def _v1_1(rows, splits, window):
    """#117's `joint` run: v1 with all five #117 inputs (`scripts/pressure_v1_1.py`)."""

    from repo_model import ml
    from repo_model.recalibration import NestedFoldPid

    v11s = _script("pressure_v1_1")
    v1 = v11s.v1
    columns = v11s.columns_at_horizon(v11s.candidate_columns(v11s.JOINT), window[0])
    features = v1._at_horizon(v1.GBM_FEATURES, window[0]) + columns

    def online(rows_, rule):
        return NestedFoldPid(rows_, rule, splits=splits, refit_every=REFIT_EVERY)

    with v11s.switched_on():
        return _backtest(
            rows, v11s.JOINT,
            ml.gbm_exceedance(tuple(n for n in features if n != "spread_bps"),
                              minimum_history=MINIMUM_HISTORY),
            features, _stress_taus(), window, online,
        )


def _scarcity_calendar(rows, splits, window):
    """#128's blind primary form: the logistic with the state alone, four levels."""

    from repo_model import ml, scarcity_calendar as sc

    v11s = _script("pressure_v1_1")
    (name,) = [n for n in sc.PRIMARY_CANDIDATES if sc.candidate(n).form == "logistic"]
    entry = sc.candidate(name)
    features = sc.features_at_horizon(name, window[0])
    with v11s.switched_on():
        return _backtest(
            rows, name,
            ml._scarcity_calendar_predictor(
                entry.form, features, splits, sc.STATE_FORMS[entry.state],
                minimum_history=MINIMUM_HISTORY,
            ),
            features, _stress_taus(), window,
        )


def _dynamic_logit(rows, splits, window):
    """#137's `dynamic_logit` (`ml.DYNAMIC_LOGIT_SETTINGS`), as `scripts/pressure_dynamic_logit.py`."""

    from repo_model import ml

    dl = _script("pressure_dynamic_logit")
    features = dl._at_horizon(dl.DYNAMIC_FEATURES, window[0])
    return _backtest(
        rows, "dynamic_logit",
        ml.dynamic_logit_exceedance(features, splits, minimum_history=MINIMUM_HISTORY),
        features, dl.TAUS, window,
    )


def _direct_logistic_sofr_p1(rows, splits, window):
    """#114's direct logistic plus #127's `sofr_p1`, as #172 measured it."""

    from repo_model import ml

    ew = _script("early_warning_inputs")
    control = ew._at_horizon(ew.DIRECT_FEATURES, window[0])
    columns, products = ew.runs()["sofr_p1"]
    features = control + tuple(c for c in columns if c not in control and c not in ew.DESIGN_HAS)
    with ew.switched_on():
        return _backtest(
            rows, "direct_logistic_sofr_p1",
            ml.pressure_logistic_exceedance(
                features, splits, minimum_history=MINIMUM_HISTORY, products=products
            ),
            features, ew.TAUS, window,
        )


def _leap_view(report, labels, jump_bp):
    """`report` as a one-threshold report of its raw plain-leap probability.

    The stacked combiner reads its bases' forecasts and outcomes per threshold;
    this hands it the leap column as the one threshold, with the leap labels.
    """

    return dataclasses.replace(
        report,
        taus=(jump_bp,),
        forecast=tuple((p,) for p in report.leap_forecast),
        outcomes=tuple((y,) for y in labels),
    )


def _stacked_combiner(rows, splits, window):
    """#137's stacked combiner over the persistence-logistic, the gbm and the dynamic logit.

    As measured for #168 (`scripts/pressure_dynamic_logit.py`): the bases enter
    raw, the gbm is the cross-conformal distributional gbm. On the leap target
    the combiner is fitted on the bases' raw leap probabilities and the leap
    labels, out of fold, exactly as it is fitted per threshold.
    """

    from repo_model import ml
    from repo_model.baseline import persistence_logistic_exceedance

    dl = _script("pressure_dynamic_logit")
    gbm_features = dl._at_horizon(dl.GBM_FEATURES, window[0])
    bases = {
        "persistence_logistic": _backtest(
            rows, "persistence_logistic",
            persistence_logistic_exceedance(minimum_history=MINIMUM_HISTORY),
            ("spread_bps",), dl.TAUS, window,
        ),
        "distributional_gbm": _backtest(
            rows, "distributional_gbm",
            ml.gbm_exceedance(
                tuple(n for n in gbm_features if n != "spread_bps"),
                minimum_history=MINIMUM_HISTORY,
                calibration="cross_conformal",
                calibration_folds=5,
            ),
            gbm_features, dl.TAUS, window,
        ),
        "dynamic_logit": _dynamic_logit(rows, splits, window),
    }
    combined = ml.stacked_combiner(bases)
    labels = leap_labels(rows, bases["dynamic_logit"].scored_dates, window[0])
    leap = ml.stacked_combiner(
        {name: _leap_view(report, labels, leap_jump_bp(window[0])) for name, report in bases.items()}
    )
    return dataclasses.replace(
        combined,
        leap_forecast=tuple(curve[0] for curve in leap.forecast),
        pressure_leap_forecast=None,
        leap_threshold_bp=leap_jump_bp(window[0]),
    )


RUNNERS = {
    "scarcity_calendar": _scarcity_calendar,
    "dynamic_logit": _dynamic_logit,
    "direct_logistic_sofr_p1": _direct_logistic_sofr_p1,
    "published_v1": _published_v1,
    "v1_1": _v1_1,
    "stacked_combiner": _stacked_combiner,
}


def leap_labels(rows, scored_dates, horizon=HORIZON):
    """The plain-leap outcome of each scored day at `J_h`, read as-of (#139)."""

    rule = InformationRule(
        json.loads(REGISTRY.read_text()), ("spread_bps",), decision_time=DECISION, horizon=horizon
    )
    targets = onset.LeapTargets(rows, rule, leap_jump_bp(horizon))
    position = {when: index for index, when in enumerate(targets.dates)}
    return [1 if targets.leap[position[when]] else 0 for when in scored_dates]


def _refuse_locked(scored_dates):
    if any(when >= date(2026, 1, 1) for when in scored_dates):
        raise ValueError("a scored day is locked (docs/decisions/lockbox.md)")


def candidate_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    report = RUNNERS[args.name](rows, splits, (HORIZON, END))
    _refuse_locked(report.scored_dates)
    position = report.taus.index(ONSET_TAU)
    document = {
        "name": args.name,
        "panel_sha256": panel_sha256(args.panel),
        "model_name": report.model_name,
        "features": list(report.features),
        "model_settings": json.loads(json.dumps(dict(report.model_settings), default=str)),
        "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        "scored_dates": list(report.scored_dates),
        "train_ends": [fold.train_end for fold in report.folds],
        "block_length": _block(report),
        "leap_threshold_bp": report.leap_threshold_bp,
        "leap_raw": list(report.leap_forecast),
        "tau_raw": {f"{ONSET_TAU:g}": [curve[position] for curve in report.forecast]},
        "tau_outcomes": {f"{ONSET_TAU:g}": [o[position] for o in report.outcomes]},
    }
    args.output.write_bytes(pickle.dumps(document))
    print(json.dumps({
        "name": args.name, "model": report.model_name, "features": list(report.features),
        "first": report.scored_dates[0].isoformat(), "last": report.scored_dates[-1].isoformat(),
        "days": len(report.scored_dates), "output": str(args.output),
    }))
    return 0


def _block(report):
    from repo_model.baseline import _maximum_horizon_overlap

    return _maximum_horizon_overlap(report.folds)


# -- scoring -------------------------------------------------------------------------


def _load(runs, name):
    return pickle.loads((Path(runs) / f"{name}.pickle").read_bytes())


def _brier(column, outcomes, positions=None):
    positions = range(len(outcomes)) if positions is None else positions
    positions = list(positions)
    if not positions:
        return None
    return sum((column[k] - outcomes[k]) ** 2 for k in positions) / len(positions)


def _seed(*parts):
    return onset._seed("#150", *parts)


def calibrator_cell(part, outcomes):
    """The published v1's plain-leap Brier under each calibrator, paired against Platt."""

    scored, ends = part["scored_dates"], part["train_ends"]
    columns = {
        method: list(pc.walk_forward(method, part["leap_raw"], outcomes, scored, ends))
        for method in pc.CALIBRATORS
    }
    cell = {"days": len(outcomes), "events": sum(outcomes), "brier": {}, "vs_platt": {}}
    for method, column in columns.items():
        cell["brier"][method] = _brier(column, outcomes)
        if method != DEFAULT_CALIBRATOR:
            cell["vs_platt"][method] = pc._paired(
                columns[DEFAULT_CALIBRATOR], column, outcomes,
                block_length=part["block_length"], seed=_seed("calibrator", method),
            )
    return cell


def choose_calibrator(cell):
    """Platt, unless another method's gain over Platt has an interval wholly above zero.

    The gain is Brier(Platt) - Brier(method). If several clear zero, the
    largest gain wins (#150, amendment of 3 October: the calibrator).
    """

    clearing = {
        method: paired["mean"]
        for method, paired in cell["vs_platt"].items()
        if paired["interval"]["lower"] > 0
    }
    if not clearing:
        return DEFAULT_CALIBRATOR
    return max(clearing, key=lambda method: clearing[method])


def calibrator_command(args) -> int:
    rows = load_daily_panel(args.panel)
    part = _load(args.runs, CALIBRATOR_CHOOSER)
    _refuse_locked(part["scored_dates"])
    outcomes = leap_labels(rows, part["scored_dates"])
    cell = calibrator_cell(part, outcomes)
    document = {
        "directive": "#150",
        "status": "scratch measurement; not a record, nothing published moves",
        "panel_sha256": panel_sha256(args.panel),
        "candidate": CALIBRATOR_CHOOSER,
        "horizon": HORIZON,
        "leap_threshold_bp": leap_jump_bp(),
        "scored_window": _window(part["scored_dates"]),
        "sign_convention": "vs_platt = Brier(platt) - Brier(method); positive: the method is better",
        "calibration_declaration": pc.declaration(),
        "cell": cell,
        "chosen": choose_calibrator(cell),
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"chosen": document["chosen"], "brier": cell["brier"]}, indent=1))
    return 0


def _window(scored):
    return {"first": scored[0].isoformat(), "last": scored[-1].isoformat(), "days": len(scored)}


def choose_model(scores):
    """The highest-ranked candidate whose selection score is within the interval of the best.

    `scores[name]["vs_best"]` is Brier(best) - Brier(name) with its 90%
    stationary-bootstrap interval. A candidate is within when that interval
    reaches zero (its upper end is at or above 0): the data do not tell it
    apart from the best. The ranking is `CANDIDATES`' order, simplest first.
    """

    for name in CANDIDATES:
        if name in scores and scores[name]["within"]:
            return name
    raise ValueError("no candidate is within the interval of the best")


def select_command(args) -> int:
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(SPLITS)
    parts = {name: _load(args.runs, name) for name in CANDIDATES}
    first = parts[CANDIDATES[0]]
    for name, part in parts.items():
        _refuse_locked(part["scored_dates"])
        if part["scored_dates"] != first["scored_dates"] or part["train_ends"] != first["train_ends"]:
            raise ValueError(f"{name} is not on {CANDIDATES[0]}'s fold grid")
        if part["leap_threshold_bp"] != leap_jump_bp():
            raise ValueError(f"{name}'s leap threshold is not J_1")
    scored, ends, block = first["scored_dates"], first["train_ends"], first["block_length"]
    outcomes = leap_labels(rows, scored)
    method = args.calibrator
    columns = {
        name: list(pc.walk_forward(method, part["leap_raw"], outcomes, scored, ends))
        for name, part in parts.items()
    }
    brier = {name: _brier(column, outcomes) for name, column in columns.items()}
    best = min(CANDIDATES, key=lambda name: brier[name])

    groups = onset.day_groups(rows, scored, splits)
    rule = InformationRule(
        json.loads(REGISTRY.read_text()), ("spread_bps",), decision_time=DECISION, horizon=HORIZON
    )
    targets = onset.LeapTargets(rows, rule, leap_jump_bp())
    leap_at_risk = onset.leap_onset_group(targets, scored)
    baselines = {
        onset.LEAP_CALENDAR_CLIMATOLOGY: onset.leap_calendar_climatology(
            targets, "leap", scored, ends, splits),
        onset.LEAP_PERSISTENCE_LOGISTIC: onset.leap_persistence_logistic(
            targets, "leap", scored, ends),
    }
    tau = f"{ONSET_TAU:g}"
    tau_outcomes = first["tau_outcomes"][tau]

    best_losses = [(columns[best][k] - outcomes[k]) ** 2 for k in range(len(outcomes))]
    from repo_model.metrics import stationary_bootstrap_interval

    best_level = stationary_bootstrap_interval(
        lambda idx: sum(best_losses[i] for i in idx) / len(idx),
        len(best_losses), block_length=block, seed=_seed("best_level", best),
        replications=pc.REPLICATIONS, level=pc.LEVEL,
    )
    scores = {}
    for rank, name in enumerate(CANDIDATES, start=1):
        part = parts[name]
        entry = {
            "rank": rank,
            "model_name": part["model_name"],
            "features": part["features"],
            "panel_sha256": part["panel_sha256"],
            "brier": brier[name],
            "brier_raw": _brier(part["leap_raw"], outcomes),
        }
        if name == best:
            entry["vs_best"] = None
            entry["within"] = True
        else:
            entry["vs_best"] = pc._paired(
                columns[best], columns[name], outcomes,
                block_length=block, seed=_seed("vs_best", name),
            )
            entry["within"] = entry["vs_best"]["interval"]["upper"] >= 0
        entry["within_unpaired_reading"] = brier[name] <= best_level[1]
        entry["vs_leap_baselines"] = {
            bench: pc._paired(values, columns[name], outcomes,
                              block_length=block, seed=_seed("vs_baseline", name, bench))
            for bench, values in baselines.items()
        }
        onset_column = list(pc.walk_forward(method, part["tau_raw"][tau], tau_outcomes, scored, ends))
        entry["descriptive"] = {
            "onset_at_risk_brier_+5bp": _brier(onset_column, tau_outcomes, groups[onset.GROUP_ONSET]),
            "onset_one_day_brier_+5bp": _brier(
                onset_column, tau_outcomes, groups[onset.GROUP_ONSET_ONE_DAY]),
            "leap_onset_at_risk_brier": _brier(columns[name], outcomes, leap_at_risk),
        }
        scores[name] = entry
    chosen = choose_model(scores)
    unpaired = next(name for name in CANDIDATES if scores[name]["within_unpaired_reading"])
    document = {
        "directive": "#150",
        "status": "scratch measurement; not a record, nothing published moves",
        "panel_sha256": panel_sha256(args.panel),
        "horizon": HORIZON,
        "leap_threshold_bp": leap_jump_bp(),
        "calibrator": method,
        "scored_window": _window(scored),
        "block_length": block,
        "events": sum(outcomes),
        "groups": {
            "onset_at_risk": {"days": len(groups[onset.GROUP_ONSET]),
                              "events": sum(tau_outcomes[k] for k in groups[onset.GROUP_ONSET])},
            "onset_one_day": {"days": len(groups[onset.GROUP_ONSET_ONE_DAY]),
                              "events": sum(tau_outcomes[k] for k in groups[onset.GROUP_ONSET_ONE_DAY])},
            "leap_onset_at_risk": {"days": len(leap_at_risk),
                                   "events": sum(outcomes[k] for k in leap_at_risk)},
        },
        "sign_convention": (
            "vs_best = Brier(best) - Brier(candidate); within when its 90% interval reaches 0. "
            "vs_leap_baselines = Brier(baseline) - Brier(candidate), descriptive only"
        ),
        "leap_baselines_brier": {bench: _brier(values, outcomes) for bench, values in baselines.items()},
        "best": best,
        "best_brier_interval": {"lower": best_level[0], "upper": best_level[1]},
        "scores": scores,
        "chosen": chosen,
        "chosen_under_unpaired_reading": unpaired,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"best": best, "chosen": chosen, "unpaired": unpaired,
                      "brier": brier}, indent=1))
    return 0


# -- the frozen declaration ----------------------------------------------------------

#: The code a frozen model is, per candidate: (file, root definitions). Each
#: root is hashed with every top-level definition of the same file it reaches,
#: so an edit to a helper moves the checksum too (`_top_level_source`).
_SHARED_SOURCE = (
    ("src/repo_model/onset.py", ("LeapTargets", "leap_calendar_climatology",
                                 "leap_persistence_logistic", "leap_onset_group", "day_groups")),
    ("src/repo_model/baseline.py", ("rolling_exceedance_backtest", "_leap_at_folds")),
    ("src/repo_model/probability_calibration.py", ("walk_forward", "CALIBRATORS")),
)
_MODEL_SOURCE = {
    "published_v1": (
        ("src/repo_model/ml.py", ("gbm_exceedance",)),
        ("src/repo_model/recalibration.py", ("NestedFoldPid",)),
        ("scripts/final_test_preregistration.py", ("_published_v1",)),
    ),
    "v1_1": (
        ("src/repo_model/ml.py", ("gbm_exceedance",)),
        ("src/repo_model/recalibration.py", ("NestedFoldPid",)),
        ("scripts/final_test_preregistration.py", ("_v1_1",)),
    ),
    "scarcity_calendar": (
        ("src/repo_model/ml.py", ("_scarcity_calendar_predictor",)),
        ("src/repo_model/scarcity_calendar.py", ("STATE_FORMS", "features_at_horizon")),
        ("scripts/final_test_preregistration.py", ("_scarcity_calendar",)),
    ),
    "dynamic_logit": (
        ("src/repo_model/ml.py", ("dynamic_logit_exceedance",)),
        ("scripts/pressure_dynamic_logit.py", ("DYNAMIC_FEATURES", "_at_horizon")),
        ("scripts/final_test_preregistration.py", ("_dynamic_logit",)),
    ),
    "direct_logistic_sofr_p1": (
        ("src/repo_model/ml.py", ("pressure_logistic_exceedance",)),
        ("scripts/final_test_preregistration.py", ("_direct_logistic_sofr_p1",)),
    ),
    "stacked_combiner": (
        ("src/repo_model/ml.py", ("stacked_combiner", "gbm_exceedance", "dynamic_logit_exceedance")),
        ("scripts/pressure_dynamic_logit.py", ("DYNAMIC_FEATURES", "GBM_FEATURES", "_at_horizon")),
        ("scripts/final_test_preregistration.py", ("_stacked_combiner", "_dynamic_logit")),
    ),
}
#: Each candidate's declared inputs at horizon 1, as `candidate` scored them.
_FEATURES = {
    "scarcity_calendar": ("spread_bps", "reserve_scarcity_state", "days_to_month_end",
                          "quarter_end", "tax_date", "treasury_settlement"),
    "dynamic_logit": ("spread_bps", "days_to_month_end", "quarter_end", "tax_date",
                      "treasury_settlement_coupons", "reserve_balances"),
    "direct_logistic_sofr_p1": ("spread_bps", "days_to_month_end", "quarter_end", "tax_date",
                                "treasury_settlement", "reserve_balances", "tga", "sofr_p1"),
    "published_v1": ("reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps",
                     "tbill_13w", "tbill_4w", "tga", "treasury_settlement"),
    "v1_1": ("reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps",
             "tbill_13w", "tbill_4w", "tga", "treasury_settlement", "iorb_announced_change_bps",
             "iorb_days_to_announced_change", "on_rrp_depleted", "reserves_when_depleted",
             "settlement_day", "settlement_day_when_depleted", "effr_minus_iorb_bp",
             "reserve_scarcity_state"),
    "stacked_combiner": ("persistence_logistic", "distributional_gbm", "dynamic_logit"),
}


def _definitions(tree) -> dict:
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            found[node.name] = node
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(
            node.targets[0], ast.Name
        ):
            found[node.targets[0].id] = node
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            found[node.target.id] = node
    return found


def _top_level_source(path: str, roots) -> dict:
    """The sha256 of each top-level definition `roots` reach within `path`.

    A root reaches every top-level name of the same file that its source
    mentions, and so on: the definition's helpers and constants.
    """

    text = (REPO / path).read_text(encoding="utf-8")
    definitions = _definitions(ast.parse(text))
    missing = sorted(set(roots) - set(definitions))
    if missing:
        raise ValueError(f"{path} defines none of {missing}")
    reached, stack = set(), list(roots)
    while stack:
        name = stack.pop()
        if name in reached:
            continue
        reached.add(name)
        for node in ast.walk(definitions[name]):
            if isinstance(node, ast.Name) and node.id in definitions:
                stack.append(node.id)
    return {
        name: hashlib.sha256(
            ast.get_source_segment(text, definitions[name]).encode("utf-8")
        ).hexdigest()
        for name in sorted(reached)
    }


def declaration(name: str = CHOSEN, calibrator: str = CHOSEN_CALIBRATOR) -> dict:
    """Everything the pre-registered model is: inputs, constants, calibrator, code."""

    if name not in _MODEL_SOURCE:
        raise ValueError(f"unknown candidate {name!r}")
    source = {}
    for path, names in _SHARED_SOURCE + _MODEL_SOURCE[name]:
        source[path] = {**source.get(path, {}), **_top_level_source(path, names)}
    return {
        "model": name,
        "features": list(_FEATURES.get(name, ())),
        "calibrator": calibrator,
        "calibration_constants": {
            "minimum_pairs": pc.MINIMUM_PAIRS,
            "minimum_events": pc.MINIMUM_EVENTS,
            "probability_floor": pc.PROBABILITY_FLOOR,
            "recency_half_life_scored_days": pc.RECENCY_HALF_LIFE_DAYS,
        },
        "leap_jump_bp": {str(h): float(j) for h, j in sorted(onset.LEAP_JUMP_BP.items())},
        "leap_onset_calm_days": onset.LEAP_ONSET_CALM_DAYS,
        "onset_threshold_bp": onset.ONSET_THRESHOLD_BP,
        "onset_calm_days": onset.ONSET_CALM_DAYS,
        "minimum_events": onset.MINIMUM_EVENTS,
        "fold_grid": {
            "walk_forward": "expanding window",
            "minimum_history": MINIMUM_HISTORY,
            "refit_every": REFIT_EVERY,
            "decision_time": DECISION.isoformat(timespec="minutes"),
        },
        "interval": {"level": pc.LEVEL, "replications": pc.REPLICATIONS,
                     "method": "stationary_bootstrap"},
        "source_sha256": source,
    }


def declaration_checksum(name: str = CHOSEN, calibrator: str = CHOSEN_CALIBRATOR) -> str:
    text = json.dumps(declaration(name, calibrator), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def declaration_command(args) -> int:
    print(json.dumps({"declaration": declaration(), "sha256": declaration_checksum()},
                     indent=1, sort_keys=True))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("candidate", help="score one candidate's raw leap probability at h = 1")
    one.add_argument("--name", choices=CANDIDATES, required=True)
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=candidate_command)
    cal = sub.add_parser("calibrator", help="the calibrator-selection cell, and the rule's choice")
    cal.add_argument("--panel", type=Path, required=True)
    cal.add_argument("--runs", type=Path, required=True)
    cal.add_argument("--output", type=Path, required=True)
    cal.set_defaults(func=calibrator_command)
    sel = sub.add_parser("select", help="the selection cell, and the rule's choice")
    sel.add_argument("--panel", type=Path, required=True)
    sel.add_argument("--runs", type=Path, required=True)
    sel.add_argument("--calibrator", choices=pc.CALIBRATORS, required=True)
    sel.add_argument("--output", type=Path, required=True)
    sel.set_defaults(func=select_command)
    dec = sub.add_parser("declaration", help="the frozen declaration and its checksum")
    dec.set_defaults(func=declaration_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
