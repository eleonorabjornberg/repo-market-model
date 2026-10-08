"""Score the settlement-timing probit and quantile regression (#379) for the pressure-day judge.

A scratch measurement, not a record: it writes JSON to the paths it is given and nothing
into `docs/runs/`. The candidates are `repo_model.settlement_timing.CANDIDATES`, their
cut-offs are in `metadata/pressure_judge.json`, both committed before any score was
computed. Every input they read beyond the published panel is off in every published
declaration and switched on for these runs only.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/settlement_timing.py run --panel AUG2.csv --published PUBLISHED.csv \\
        --candidate NAME --horizon H --output OUT/NAME_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv \\
        --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h1.json ... OUT/NAME_h1.json ...

`run` walks the candidate forward on the shared fold grid (`pressure_judge`'s: minimum
history 61, refit every 21 scored days, last scored day the declaration's, 2025-12-31)
at one horizon and writes its probabilities at +5 and +10 bp in the shape
`pressure_judge.forecasts_from_horizon_document` reads. The judge's `panel_sha256` check
compares with the published panel's digest, which is what `--published` gives; the
scratch panel's digest is recorded beside it.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from datetime import time
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, measurement_fields, ml, pressure_judge as pj, scarcity  # noqa: E402
from repo_model import settlement_timing as st  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)


@contextlib.contextmanager
def switched_on():
    """The scarcity state and the measurement fields in the feature map, for this run only."""

    fields = dict(measurement_fields.COLUMN_FIELDS)
    with scarcity.measurement_declaration(), mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{column: tuple(sorted({source for source, _f in pairs})) for column, pairs in fields.items()},
            }
        ),
    ):
        yield


def run_command(args) -> int:
    declaration = pj.load_declaration()
    entry = st.candidate(args.candidate)
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    features = st.features_at_horizon(args.candidate, args.horizon)
    predictor = ml._settlement_timing_predictor(
        st.FORMS[entry.form], features, splits, minimum_history=MINIMUM_HISTORY
    )
    with switched_on():
        report = rolling_exceedance_backtest(
            rows,
            predictor=predictor,
            model_name=args.candidate,
            features=features,
            registry=registry,
            decision_time=DECISION,
            taus=declaration.thresholds,
            minimum_history=MINIMUM_HISTORY,
            refit_every=REFIT_EVERY,
            end=declaration.last_day,
            horizon=args.horizon,
        )
    forecast = pj.report_forecast(args.candidate, report)
    document = {
        "horizon": args.horizon,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "features": list(features),
        "forecasts": {
            forecast.name: {
                f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, column)}
                for tau, column in forecast.probabilities.items()
            }
        },
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate": args.candidate, "horizon": args.horizon, "days": len(forecast.dates),
        "first": forecast.dates[0].isoformat(), "last": forecast.dates[-1].isoformat(),
        "output": str(args.output),
    }))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--candidate", required=True, choices=[c.name for c in st.CANDIDATES])
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
