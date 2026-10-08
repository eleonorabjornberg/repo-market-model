"""Track S of #374 (#378): write the scarcity-conditioned calendar's forecasts for the judge.

A scratch measurement, not a record: it writes JSON to the path it is given and
nothing into `docs/runs/`. The candidates, their features, calibration and
flagging-cut-off rule are in `metadata/pressure_judge.json` (pinned to
`repo_model.scarcity_event_bar` by a test), which this script refuses to read
unless it is committed and unchanged. The state and its inputs are off in every
published declaration; they are switched on for these runs only, on the scratch
panel `pressure_v1_1.py panel` builds from tracked fixtures.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon H --output OUT/s_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel AUG.csv --horizon H --output OUT/b_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel AUG.csv --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/b_h1.json OUT/s_h1.json ... OUT/b_h5.json OUT/s_h5.json

`forecasts` scores every candidate of `scarcity_event_bar.CANDIDATES` at one
horizon (or the ones named by `--candidate`), walk-forward on the shared fold
grid (minimum history 61, refit every 21 days, scored days through
2025-12-31), recalibrated out of fold. Its output has the shape of
`pressure_model_v1.py horizon`'s `forecasts` block. At horizons of 2 or more the
interaction variants have no settlement to cross, so they are the base form and
take its forecasts under their own name.
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


from repo_model import ml, pressure, pressure_judge as pj, scarcity  # noqa: E402
from repo_model import scarcity_calendar as sc, scarcity_event_bar as eb  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

judge_script = _script("pressure_judge")
REGISTRY = judge_script.REGISTRY
SPLITS = judge_script.SPLITS
MINIMUM_HISTORY = judge_script.MINIMUM_HISTORY
REFIT_EVERY = judge_script.REFIT_EVERY
DECISION = judge_script.DECISION


def score(entry, rows, splits, registry, declaration, horizon):
    """One candidate's recalibrated forecasts at one horizon, as a `Forecast`."""

    features = eb.features_at_horizon(entry.name, horizon)
    predictor = ml._scarcity_calendar_predictor(
        entry.form,
        features,
        splits,
        sc.STATE_FORMS[eb.STATE_FORM],
        minimum_history=MINIMUM_HISTORY,
        interactions=entry.variant == "interactions",
        regime_pooled=entry.variant == "regime_pooled",
    )
    with scarcity.measurement_declaration():
        raw = rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=entry.name, features=features, registry=registry,
            decision_time=DECISION, taus=declaration.thresholds, minimum_history=MINIMUM_HISTORY,
            refit_every=REFIT_EVERY, end=declaration.last_day, horizon=horizon,
        )
    return pj.report_forecast(entry.name, pressure.recalibrated(raw))


def forecasts_command(args) -> int:
    declaration = pj.load_declaration()
    commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    wanted = args.candidate or [c.name for c in eb.CANDIDATES]
    for name in wanted:
        eb.candidate(name)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())

    done = {}
    for name in wanted:
        entry = eb.candidate(name)
        base = next(c for c in eb.CANDIDATES if (c.form, c.variant) == (entry.form, "base"))
        if entry.variant == "interactions" and args.horizon > 1 and base.name in done:
            same = done[base.name]
            done[name] = pj.Forecast(name, same.horizon, same.dates, same.probabilities)
        else:
            done[name] = score(entry, rows, splits, registry, declaration, args.horizon)
        print(json.dumps({"candidate": name, "horizon": args.horizon, "days": len(done[name].dates)}), flush=True)
    document = judge_script._document(args.horizon, panel_sha256(args.panel), list(done.values()))
    document["declaration_commit"] = commit
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.add_argument("--candidate", action="append", choices=[c.name for c in eb.CANDIDATES])
    forecasts.set_defaults(run=forecasts_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
