"""Track C of #374 (#380): is recalibrating the current model's probabilities enough?

A scratch measurement, not a record: it writes forecast files for the judge
(`scripts/pressure_judge.py judge`) and nothing into `docs/runs/`. The candidates,
their cut-offs and the pooled and conditional recalibrators are declared in
`metadata/pressure_judge.json` and `repo_model.group_calibration` before any
score is computed.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/recalibration_bakeoff.py raw \\
        --panel PANEL --forecast pressure_v1 --horizon H --output OUT/raw_hH.pickle
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/recalibration_track.py forecasts \\
        --panel PANEL --input OUT/raw_hH.pickle --output OUT/forecasts_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PANEL \\
        --output OUT/judge.json --markdown OUT/judge.md OUT/forecasts_h?.json

The raw forecast is pressure model v1's `distributional_gbm` before its
recalibration (what `recalibration_bakeoff.py raw --forecast pressure_v1`
produces; its pickle also carries the two benchmarks, run exactly as
`pressure_judge.benchmark_forecasts` runs them). Each threshold and horizon is
recalibrated out of fold on its own, then made non-increasing in tau.
"""

from __future__ import annotations

import argparse
import copyreg
import importlib.util
import json
import pickle
import sys
from pathlib import Path
from types import MappingProxyType

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import group_calibration as gc, pressure, pressure_judge as pj, probability_calibration as pc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"

def _proxy(mapping):
    # `recalibration_bakeoff.py raw` pickles a mapping proxy as `__main__._proxy`.
    return MappingProxyType(mapping)


copyreg.pickle(MappingProxyType, lambda proxy: (_proxy, (dict(proxy),)))


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


def forecasts_command(args) -> int:
    declaration = pj.load_declaration()
    judge_script = _load_script("pressure_judge")
    commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    part = pickle.loads(args.input.read_bytes())
    report = part["report"]
    horizon = int(part["horizon"])
    scored = list(report.scored_dates)
    pj.require_scored_days(declaration, scored, where="recalibration_track.forecasts")
    states = judge_script._scarcity_states(horizon, declaration.last_day)
    by_date = {row.date: row for row in rows}
    groups = [
        gc.group_label(states.get(day), splits.reporting_day_type(day, by_date[day].values))
        for day in scored
    ]
    forecasts = []
    for name, columns in candidate_columns(report, groups, declaration.thresholds).items():
        forecasts.append(pj.Forecast(name, horizon, tuple(scored),
                                     {tau: tuple(col) for tau, col in columns.items()}))
    forecasts.append(pj.report_forecast("published_v1", pressure.recalibrated(report)))
    names = {"calendar_climatology": declaration.climatology, "persistence_logistic": declaration.persistence}
    for key, name in names.items():
        forecasts.append(pj.report_forecast(name, part["benchmarks"][key]))
    document = judge_script._document(horizon, digest, forecasts)
    document["declaration_commit"] = commit
    document["group_counts"] = {g: groups.count(g) for g in sorted(set(groups))}
    document["calibration"] = {"pooled": pc.declaration(), "conditional": gc.declaration()}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": horizon, "models": sorted(document["forecasts"]), "output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("forecasts", help="recalibrate one horizon's raw run for the judge")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--input", type=Path, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=forecasts_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
