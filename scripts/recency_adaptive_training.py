"""Recency-weighted and adaptive training of the pressure classifier (#411, a track of #374).

A scratch measurement, not a record: it writes JSON to the path it is given and
nothing into `docs/runs/`. The candidates, features and horizons are in
`metadata/recency_adaptive_training.json`, which this script refuses to read unless
it is committed and unchanged.

    PYTHONPATH=src python3 scripts/recency_adaptive_training.py horizon --panel PANEL --horizon H --output OUT/recency_hH.json

The base is track W's class-weighted logistic (`ml.pressure_rare_event_exceedance`).
Five recency fits (decaying sample weights at three half-lives, trailing windows at two
lengths; `ml.PRESSURE_RECENCY_SETTINGS`) are recalibrated out of fold
(`pressure.recalibrated`); the base's raw forecasts are recalibrated online two ways
(`pressure.online_recalibrated`). The base under the out-of-fold Platt step is re-scored
beside them as the paired reference. Days before 2026-01-01 only. The output has the shape
of `pressure_model_v1.py horizon`'s `forecasts` block, so the judge of #375 reads it:

    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PANEL --output OUT/judge.json OUT/bench_h*.json OUT/recency_h*.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml, pressure  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "recency_adaptive_training.json"
SETTLEMENT = "treasury_settlement"


def committed_declaration(path: Path) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def table(report):
    return {
        f"{tau:g}": {when.isoformat(): curve[position] for when, curve in zip(report.scored_dates, report.forecast)}
        for position, tau in enumerate(report.taus)
    }


def horizon_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="recency_adaptive_training")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    features = tuple(name for name in declared["features"] if h == 1 or name != SETTLEMENT)
    minimum = declared["scoring"]["minimum_history"]
    base = declared["base"]

    def run(name, recency):
        report = rolling_exceedance_backtest(
            rows,
            predictor=ml.pressure_rare_event_exceedance(
                base["kind"], base["treatment"], features, splits, minimum_history=minimum, recency=recency
            ),
            model_name=name,
            features=features,
            registry=registry,
            decision_time=time(16, 0),
            taus=taus,
            minimum_history=minimum,
            refit_every=declared["scoring"]["refit_every"],
            end=last,
            horizon=h,
        )
        print(json.dumps({"horizon": h, "candidate": name, "done": True}), flush=True)
        return report

    forecasts, raw, declarations = {}, {}, {}
    base_report = run(base["name"], None)
    forecasts[base["name"] + "+recalibrated"] = table(pressure.recalibrated(base_report))
    raw[base["name"]] = table(base_report)
    for name, spec in declared["online_recalibration"]["candidates"].items():
        forecasts[name] = table(pressure.online_recalibrated(base_report, spec["method"]))
    for name, spec in declared["recency_fits"]["candidates"].items():
        report = run(name, (spec["mode"], spec["parameter"]))
        forecasts[name + declared["recency_fits"]["judged_form"]] = table(pressure.recalibrated(report))
        raw[name] = table(report)
        declarations[name] = {
            "features": list(report.features),
            "model_settings": dict(report.model_settings),
            "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        }
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": declarations,
        "forecasts": forecasts,
        "unrecalibrated_forecasts": raw,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    horizon = commands.add_parser("horizon", help="score the declared candidates at one horizon")
    horizon.add_argument("--panel", type=Path, required=True)
    horizon.add_argument("--horizon", type=int, required=True)
    horizon.add_argument("--output", type=Path, required=True)
    horizon.set_defaults(run=horizon_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
