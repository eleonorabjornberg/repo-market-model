"""Track C of #374 (#380): is recalibrating the current model's probabilities enough?

A scratch measurement, not a record: it writes a forecast file for the judge
(`scripts/pressure_judge.py judge`) and nothing into `docs/runs/`. The candidates,
their cut-offs and the pooled and conditional recalibrators are declared in
`metadata/pressure_judge.json` and `repo_model.group_calibration` before any
score is computed; this script refuses to run unless that file is committed.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/recalibration_track.py horizon \\
        --panel PANEL --horizon H --output OUT/recal_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PANEL --horizon H \\
        --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PANEL \\
        --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/recal_h?.json

The raw forecast is pressure model v1's `distributional_gbm`: the published
funding declaration's gbm, conformal PID with nested selection, before any
recalibration (the run `pressure_judge.py forecasts --published` recalibrates
by Platt and names `published_v1`). The output carries `published_v1` (that
raw run through `pressure.recalibrated`, so the judge's baseline row needs no
second run) and the four recalibrated candidates. Each threshold and horizon
is recalibrated out of fold on its own, then made non-increasing in tau. The
benchmarks come from `pressure_judge.py forecasts`, run beside this.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import group_calibration as gc, pressure, pressure_judge as pj, probability_calibration as pc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
judge_script = None



def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def candidate_columns(report, groups, declared_taus):
    """{candidate: {tau: [probability per scored day]}} for one raw run."""

    scored = list(report.scored_dates)
    train_ends = [fold.train_end for fold in report.folds]
    methods = {
        "recal_isotonic": lambda f, y: pc.walk_forward("isotonic", f, y, scored, train_ends),
        "recal_platt": lambda f, y: pc.walk_forward("platt", f, y, scored, train_ends),
        "recal_platt_group": lambda f, y: gc.walk_forward("group", f, y, scored, train_ends, groups),
        "recal_platt_weighted": lambda f, y: gc.walk_forward("weighted", f, y, scored, train_ends, groups),
    }
    positions = [report.taus.index(tau) for tau in declared_taus]
    out = {}
    for name, method in methods.items():
        columns = []
        for position in positions:
            forecast, _, outcomes = report.at_tau(position)
            columns.append(method(list(forecast), list(outcomes)))
        curves = pc.monotone_curves(list(zip(*columns)))
        out[name] = {tau: [curve[k] for curve in curves] for k, tau in enumerate(declared_taus)}
    return out


def _raw_report(rows, splits, registry, horizon, declaration):
    """Pressure model v1's distributional gbm, unrecalibrated (what `pressure_judge._published` fits)."""

    from repo_model import ml
    from repo_model.baseline import rolling_exceedance_backtest
    from repo_model.recalibration import NestedFoldPid

    model = _load_script("pressure_model_v1")
    features = model._at_horizon(model.GBM_FEATURES, horizon)
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=judge_script.REFIT_EVERY))
        return built[-1]

    return rolling_exceedance_backtest(
        rows,
        predictor=ml.gbm_exceedance(
            tuple(name for name in features if name != "spread_bps"),
            minimum_history=judge_script.MINIMUM_HISTORY,
        ),
        model_name="distributional_gbm",
        features=features,
        registry=registry,
        decision_time=judge_script.DECISION,
        taus=declaration.thresholds,
        minimum_history=judge_script.MINIMUM_HISTORY,
        refit_every=judge_script.REFIT_EVERY,
        end=declaration.last_day,
        horizon=horizon,
        online_calibration=online,
    )


def horizon_command(args) -> int:
    global judge_script
    declaration = pj.load_declaration()
    judge_script = _load_script("pressure_judge")
    commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads((REPO / "metadata" / "sources.json").read_text())
    horizon = args.horizon
    report = _raw_report(rows, splits, registry, horizon, declaration)
    scored = list(report.scored_dates)
    pj.require_scored_days(declaration, scored, where="recalibration_track.horizon")
    states = judge_script._scarcity_states(horizon, declaration.last_day)
    by_date = {row.date: row for row in rows}
    groups = [
        gc.group_label(states.get(day), splits.reporting_day_type(day, by_date[day].values))
        for day in scored
    ]
    forecasts = [
        pj.Forecast(name, horizon, tuple(scored), {tau: tuple(col) for tau, col in columns.items()})
        for name, columns in candidate_columns(report, groups, declaration.thresholds).items()
    ]
    forecasts.append(pj.report_forecast("published_v1", pressure.recalibrated(report)))
    document = judge_script._document(horizon, panel_sha256(args.panel), forecasts)
    document["declaration_commit"] = commit
    document["group_counts"] = {g: groups.count(g) for g in sorted(set(groups))}
    document["calibration"] = {"pooled": pc.declaration(), "conditional": gc.declaration()}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": horizon, "models": sorted(document["forecasts"]), "output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("horizon", help="fit and recalibrate the raw forecast at one horizon")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--horizon", type=int, choices=(1, 2, 3, 4, 5), required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=horizon_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
