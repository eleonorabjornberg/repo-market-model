"""Track H of #374 (#386): write the hierarchical logistic's forecasts for the judge.

A scratch measurement, not a record: it writes JSON to the path it is given and
nothing into `docs/runs/`. The candidate, its features, calibration and flagging
cut-off are in `metadata/pressure_judge.json` (pinned to
`repo_model.hierarchical_logistic` by a test), which this script refuses to read
unless it is committed and unchanged. The state and its inputs are off in every
published declaration; they are switched on for these runs only, on the scratch
panel `pressure_v1_1.py panel` builds from tracked fixtures.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon H --output OUT/h_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel AUG.csv --horizon H --output OUT/b_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel AUG.csv --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/b_h1.json OUT/h_h1.json ... OUT/b_h5.json OUT/h_h5.json
    PYTHONPATH=src python3 scripts/hierarchical_logistic.py effects OUT/h_h1.json OUT/h_h2.json ...

`forecasts` scores the candidate at one horizon, walk-forward on the shared fold
grid (minimum history 61, refit every 21 days, scored days through 2025-12-31),
recalibrated out of fold. Its output has the shape of `pressure_judge.py
forecasts`, plus a `hierarchical` block: for every fold and threshold, the
deviation scale the fit chose and the regime-specific effects it fitted.
`effects` reads those blocks and prints the shrinkage by fold and the effects of
the calendar terms by regime from the last fold, in the design's own units.
"""

from __future__ import annotations

import argparse
import functools
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


from repo_model import hierarchical_logistic as hl, ml, pressure, pressure_judge as pj, scarcity  # noqa: E402
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


def _keyed(value):
    """`value` with every dict key a string, so it can be written sorted."""

    if isinstance(value, dict):
        return {str(key): _keyed(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_keyed(item) for item in value]
    return value


def score(rows, splits, registry, declaration, horizon):
    """The candidate's recalibrated forecasts at one horizon, and what each fold fitted."""

    features = hl.features_at_horizon(horizon)
    predictor = ml._scarcity_calendar_predictor(
        "logistic", features, splits, sc.STATE_FORMS[hl.STATE_FORM],
        minimum_history=MINIMUM_HISTORY, regime_hierarchical=True,
    )
    folds = []

    @functools.wraps(predictor)
    def recording(*args, **kwargs):
        curves = predictor(*args, **kwargs)
        settings = curves.model_settings
        folds.append(
            {
                "scale_by_threshold": list(settings.get("regime_shrinkage_chosen", [])),
                "effects": _keyed(settings.get("regime_effects", [])),
                "design": list(settings["design"]),
            }
        )
        return curves

    with scarcity.measurement_declaration():
        raw = rolling_exceedance_backtest(
            rows, predictor=recording, model_name=hl.NAME, features=features, registry=registry,
            decision_time=DECISION, taus=declaration.thresholds, minimum_history=MINIMUM_HISTORY,
            refit_every=REFIT_EVERY, end=declaration.last_day, horizon=horizon,
        )
    return pj.report_forecast(hl.NAME, pressure.recalibrated(raw)), {
        "thresholds": list(declaration.thresholds),
        "grid": list(ml.REGIME_SHRINKAGE_GRID),
        "folds": folds,
    }


def forecasts_command(args) -> int:
    declaration = pj.load_declaration()
    commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    forecast, fitted = score(rows, splits, registry, declaration, args.horizon)
    print(json.dumps({"candidate": hl.NAME, "horizon": args.horizon, "days": len(forecast.dates)}), flush=True)
    document = judge_script._document(args.horizon, panel_sha256(args.panel), [forecast])
    document["declaration_commit"] = commit
    document["hierarchical"] = fitted
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def effects_command(args) -> int:
    """Shrinkage by fold, and the regime-specific effects of the last fold, per forecast file."""

    for path in args.files:
        document = json.loads(path.read_text(encoding="utf-8"))
        block = document["hierarchical"]
        names = block["folds"][-1]["design"]
        print(f"== horizon {document.get('horizon')}: {path.name}")
        for index, tau in enumerate(block["thresholds"]):
            scales = [fold["scale_by_threshold"][index] for fold in block["folds"] if len(fold["scale_by_threshold"]) > index]
            counts = {s: scales.count(s) for s in sorted(set(scales))}
            print(f"  +{tau:g} bp: folds {len(scales)}, chosen scale (count): {counts}")
            effects = [fold["effects"][index] for fold in block["folds"] if len(fold["effects"]) > index]
            if not effects:
                continue
            last = effects[-1]
            for regime, entry in sorted(last["regimes"].items(), key=lambda kv: float(kv[0])):
                terms = {names[int(k)] if k != "intercept" else "intercept": round(v, 3) for k, v in entry.items()}
                print(f"    state {float(regime):g}: {terms}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.set_defaults(run=forecasts_command)
    effects = commands.add_parser("effects")
    effects.add_argument("files", type=Path, nargs="+")
    effects.set_defaults(run=effects_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
