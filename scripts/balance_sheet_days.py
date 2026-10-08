"""Track B of #374 (#427): write the balance-sheet candidates' forecasts for the judge.

A scratch measurement, not a record: it writes JSON to the path it is given and
nothing into `docs/runs/`. The candidates, their features and calibration are in
`metadata/pressure_judge.json` (pinned to `repo_model.balance_sheet_candidates`
by a test), which this script refuses to read unless it is committed and
unchanged. The inputs are off in every published declaration and on for these
runs only, on the scratch panel `pressure_v1_1.py panel` builds from tracked
fixtures.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/balance_sheet_days.py forecasts --panel AUG.csv --candidate NAME --horizon H --output OUT/NAME_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel AUG.csv --horizon H --output OUT/b_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel AUG.csv --output OUT/judge.json --markdown OUT/judge.md OUT/*.json

The comparison classifiers (`hierarchical_logistic`, `scarcity_gbm`) are scored by
`scripts/hierarchical_logistic.py forecasts` and `scripts/scarcity_event_bar.py
forecasts --candidate scarcity_gbm` on the same panel and grid.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


from repo_model import balance_sheet_candidates as bc, ml, pressure, pressure_judge as pj, scarcity  # noqa: E402
from repo_model import scarcity_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

judge_script = _script("pressure_judge")
REGISTRY = judge_script.REGISTRY
SPLITS = judge_script.SPLITS
MINIMUM_HISTORY = judge_script.MINIMUM_HISTORY
REFIT_EVERY = judge_script.REFIT_EVERY
DECISION = judge_script.DECISION


def score(rows, splits, registry, declaration, name, horizon):
    """The candidate's recalibrated forecasts at one horizon."""

    features = bc.features_at_horizon(name, horizon)
    form = bc.CANDIDATES[name][1]
    predictor = ml._scarcity_calendar_predictor(
        "gbm" if form == "gbm" else "logistic", features, splits, sc.STATE_FORMS["four_level"],
        minimum_history=MINIMUM_HISTORY, regime_hierarchical=form == "hierarchical", balance_sheet=True,
    )
    with scarcity.measurement_declaration():
        raw = rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=name, features=features, registry=registry,
            decision_time=DECISION, taus=declaration.thresholds, minimum_history=MINIMUM_HISTORY,
            refit_every=REFIT_EVERY, end=declaration.last_day, horizon=horizon,
        )
    return pj.report_forecast(name, pressure.recalibrated(raw))


def forecasts_command(args) -> int:
    declaration = pj.load_declaration()
    commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    forecast = score(rows, splits, registry, declaration, args.candidate, args.horizon)
    print(json.dumps({"candidate": args.candidate, "horizon": args.horizon, "days": len(forecast.dates)}), flush=True)
    document = judge_script._document(args.horizon, panel_sha256(args.panel), [forecast])
    document["declaration_commit"] = commit
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--candidate", choices=sorted(bc.CANDIDATES), required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.set_defaults(run=forecasts_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
