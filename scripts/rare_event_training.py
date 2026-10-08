"""Rare-event training of the pressure classifiers (#381, a track of #374).

A scratch measurement, not a record: it writes JSON to the path it is given and
nothing into `docs/runs/`. The candidates, features, cut-offs and horizons are in
`metadata/rare_event_training.json`, which this script refuses to read unless it is
committed and unchanged.

    PYTHONPATH=src python3 scripts/rare_event_training.py horizon --panel PANEL --horizon H --output OUT/rare_hH.json

Each candidate is `ml.pressure_rare_event_exceedance` (class weights, a focal-loss
gradient-boosted classifier, or event-balanced bootstraps within each training fold),
scored walk-forward by `baseline.rolling_exceedance_backtest` on the shared fold grid
at +5 and +10 bp, days before 2026-01-01 only, then recalibrated out of fold
(`pressure.recalibrated`). The output has the shape of `pressure_model_v1.py horizon`'s
`forecasts` block (`forecasts`: every candidate `+recalibrated`, the form the judge declares; the raw fits are kept
under `unrecalibrated_forecasts` as an ablation), so the judge of #375 reads it:

    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PANEL --output OUT/judge.json OUT/rare_h1.json ... OUT/rare_h5.json
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
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "rare_event_training.json"
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


def summary(report, taus):
    """Brier, AUROC and recall/precision at each tau's declared cut-off, descriptive."""

    from repo_model.pressure_judge import auroc

    out = {}
    for position, tau in enumerate(taus):
        forecast, _, outcomes = report.at_tau(position)
        flags = [1 if p >= DECLARED["cutoffs"][f"{tau:g}"] else 0 for p in forecast]
        events = sum(outcomes)
        hits = sum(f and o for f, o in zip(flags, outcomes))
        out[f"{tau:g}"] = {
            "days": len(outcomes),
            "events": events,
            "brier": sum((p - o) ** 2 for p, o in zip(forecast, outcomes)) / len(outcomes),
            "auroc": auroc(forecast, outcomes),
            "flags": sum(flags),
            "recall": hits / events if events else None,
            "precision": hits / sum(flags) if sum(flags) else None,
        }
    return out


def horizon_command(args) -> int:
    global DECLARED
    DECLARED = committed_declaration(DECLARATION)
    h = args.horizon
    if h not in DECLARED["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(DECLARED["scoring"]["last_day"])
    require_unlocked([last], where="rare_event_training")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    taus = tuple(float(t) for t in DECLARED["thresholds_bp"])
    features = tuple(name for name in DECLARED["features"] if h == 1 or name != SETTLEMENT)
    minimum = DECLARED["scoring"]["minimum_history"]

    forecasts, raw_forecasts, declarations, scores = {}, {}, {}, {}
    for name, spec in DECLARED["candidates"].items():
        report = rolling_exceedance_backtest(
            rows,
            predictor=ml.pressure_rare_event_exceedance(
                spec["kind"], spec["treatment"], features, splits, minimum_history=minimum
            ),
            model_name=name,
            features=features,
            registry=registry,
            decision_time=time(16, 0),
            taus=taus,
            minimum_history=minimum,
            refit_every=DECLARED["scoring"]["refit_every"],
            end=last,
            horizon=h,
        )
        for label, version in ((name, report), (name + DECLARED["judged_form"], pressure.recalibrated(report))):
            target = forecasts if version is not report else raw_forecasts
            target[label] = {
                f"{tau:g}": {
                    when.isoformat(): curve[position]
                    for when, curve in zip(version.scored_dates, version.forecast)
                }
                for position, tau in enumerate(version.taus)
            }
            scores[label] = summary(version, taus)
        declarations[name] = {
            "features": list(report.features),
            "model_settings": dict(report.model_settings),
            "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        }
        print(json.dumps({"horizon": h, "candidate": name, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.panel),
        "declaration": DECLARED,
        "declarations": declarations,
        "descriptive_scores": scores,
        "forecasts": forecasts,
        "unrecalibrated_forecasts": raw_forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


DECLARED: dict = {}


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
