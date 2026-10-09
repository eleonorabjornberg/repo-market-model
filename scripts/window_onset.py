"""Score the five-day-window onset learners (#460, a track of #374) for the pressure-day judge.

A scratch measurement, not a record: it writes JSON to the path it is given and nothing into
`docs/runs/`. The candidates, features and target are in `metadata/window_onset.json`, which this
script refuses to read unless it is committed and unchanged; so are the judge's candidate files.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/window_onset.py run --panel AUG.csv --published PUBLISHED.csv --outdir OUT
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output OUT/bench_h$h.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/window_h?.json

`run` fits each candidate to "an onset in the next five panel days" (`ml.pressure_window_onset_exceedance`)
at horizon 1, walk-forward on the shared fold grid at +5 and +10 bp, scored days through
2025-12-31 only, then recalibrates it out of fold against "a pressure day in the next five panel
days" (`window_recalibrated`). One probability per decision day results; it is written as the
judge's five horizon files, `OUT/window_h1.json` .. `window_h5.json`: the file for horizon h holds,
for target day D, the window probability made h business days before D, so the judge's week-ahead
maximum over the five files is the window probability itself and a day D is flagged at lead h when
the window probability made h days earlier reached the cut-off.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml, pressure, scarcity  # noqa: E402
from repo_model import scarcity_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
REGISTRY = REPO / "metadata" / "sources.json"
DECLARATION = REPO / "metadata" / "window_onset.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
NEVER = date.max


def committed(path: Path) -> None:
    """Refuse a file that is not committed and unchanged since `HEAD`: a declaration is made before any score."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")


def window_recalibrated(report, rows, last_day: date, width: int = ml.WINDOW_ONSET_DAYS):
    """`pressure.recalibrated` against the window's pressure-day outcome, never reading past `last_day`.

    The outcome of the fold scored on day s is whether any of the `width` panel days from s is above
    the threshold. A fold's outcome is known on the window's last day, so that is the date the
    recalibration compares with a refit's training end; a window that would end after `last_day`
    is never known (`date.max`) and is never used.
    """

    calendar = [row.date for row in rows if row.date <= last_day]
    spreads = [float(row.spread_bps) for row in rows if row.date <= last_day]
    position = {day: k for k, day in enumerate(calendar)}
    outcomes, folds = [], []
    for fold, old in zip(report.folds, report.outcomes):
        start = position[fold.scored_date]
        complete = start + width <= len(calendar)
        window = spreads[start : start + width]
        outcomes.append(
            tuple(1 if complete and any(exceeds_bp(v, float(tau)) for v in window) else 0 for tau in report.taus)
        )
        folds.append(dataclasses.replace(fold, scored_date=calendar[start + width - 1] if complete else NEVER))
    return pressure.recalibrated(dataclasses.replace(report, outcomes=tuple(outcomes), folds=tuple(folds)))


def by_horizon(report, calendar, last_day: date, horizon: int) -> dict:
    """The horizon-`horizon` file's column per threshold: target day D gets the window probability made `horizon` days before."""

    position = {day: k for k, day in enumerate(calendar)}
    out = {}
    for index, tau in enumerate(report.taus):
        column = {}
        for when, curve in zip(report.scored_dates, report.forecast):
            target = position[when] + horizon - 1
            if target < len(calendar) and calendar[target] <= last_day:
                column[calendar[target].isoformat()] = curve[index]
        out[f"{tau:g}"] = column
    return out


def candidate_predictor(spec: dict, features, splits):
    if spec["design"] == "pressure":
        return ml.pressure_window_onset_exceedance(spec["kind"], spec["treatment"], features, splits, minimum_history=61)
    design = ml._ScarcityCalendarDesign(
        features, splits, sc.STATE_FORMS["four_level"], monotone=False, regime_hierarchical=True
    )
    return ml.pressure_window_onset_exceedance(
        spec["kind"], spec["treatment"], features, splits, minimum_history=61, design=design
    )


def run_command(args) -> int:
    committed(DECLARATION)
    declared = json.loads(DECLARATION.read_text())
    for name in declared["candidates"]:
        committed(CANDIDATES / f"{name}{declared['judged_form']}.json")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="window_onset")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    calendar = [row.date for row in rows if row.date <= last]
    names = [args.candidate] if args.candidate else list(declared["candidates"])
    forecasts = {h: {} for h in declared["horizons"]}
    raw_forecasts, settings = {}, {}
    for name in names:
        spec = declared["candidates"][name]
        features = tuple(declared["features"][spec["features"]])
        with scarcity.measurement_declaration():
            report = rolling_exceedance_backtest(
                rows,
                predictor=candidate_predictor(spec, features, splits),
                model_name=name,
                features=features,
                registry=registry,
                decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                taus=taus,
                minimum_history=declared["scoring"]["minimum_history"],
                refit_every=declared["scoring"]["refit_every"],
                end=last,
                horizon=1,
            )
        recalibrated = window_recalibrated(report, rows, last)
        for h in declared["horizons"]:
            forecasts[h][name + declared["judged_form"]] = by_horizon(recalibrated, calendar, last, h)
        raw_forecasts[name] = by_horizon(report, calendar, last, 1)
        settings[name] = {
            "features": list(report.features),
            "model_settings": dict(report.model_settings),
            "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        }
        print(json.dumps({"candidate": name, "done": True}), flush=True)
    args.outdir.mkdir(parents=True, exist_ok=True)
    for h in declared["horizons"]:
        document = {
            "horizon": h,
            "panel_sha256": panel_sha256(args.published),
            "scratch_panel_sha256": panel_sha256(args.panel),
            "declaration": declared,
            "declarations": settings,
            "forecasts": forecasts[h],
            "unrecalibrated_forecasts_at_decision_plus_one": raw_forecasts if h == 1 else {},
        }
        path = args.outdir / f"window_h{h}.json"
        path.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
        print(json.dumps({"horizon": h, "output": str(path)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--candidate")
    run.add_argument("--outdir", type=Path, required=True)
    run.set_defaults(handler=run_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
