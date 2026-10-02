#!/usr/bin/env python3
"""How much the calibration masking of `information-set.md`'s Method notes moves the scores.

`scripts/calibration_masking_exposure.py` (PR #74) bounded the bias's exposure:
for the funding declaration, 0.39% of the excluding models' training pairs,
all on `reserve_balances` and `tga`. Directive #78 asks for its effect. This
scores one declaration twice on the as-of grid, with
`ml.fit_gradient_boosted_quantiles` exactly as `--model gbm --calibration
cross_conformal` binds it, once as published (`calibration_masking=None`) and
once with `calibration_masking="held_out_row"`, and reports the paired
difference, masked minus published, per scored day.

**Only days before the locked period are scored** (`docs/decisions/lockbox.md`):
the panel is cut before `--scored-before`, which may not be later than
2026-01-01, and every scored day is checked against it. Training uses what the
as-of rule allows inside the cut panel; a forecast before the cut reads nothing
after it, so the cut changes no forecast it keeps.

Two steps, so the two scorings can run in parallel:

    PYTHONPATH=src python3 scripts/calibration_masking_effect.py score PANEL \\
        --path backtest --masking off --feature ... --output off.json
    PYTHONPATH=src python3 scripts/calibration_masking_effect.py score PANEL \\
        --path backtest --masking on --feature ... --output on.json
    PYTHONPATH=src python3 scripts/calibration_masking_effect.py compare \\
        off.json on.json PANEL

`--path backtest` scores the quantile vector as `backtest` and `compare
--loss crps` do: per day, whether the 0.05-0.95 band covers (the calibration
score `backtest` publishes), its width, and the CRPS. `--path exceedance`
scores the exceedance curve as `exceedance-backtest` does: per day and
threshold, the Brier score. `compare` pairs the two scorings by date, refuses
any day the other lacks, and reports each difference pooled and split by
regime and pressure-day type, with `metrics.stationary_bootstrap_interval`
intervals. A measurement, not a record: nothing is written to `docs/runs/`.

Needs the `ml` extra for `score`; `compare` is standard library only.
"""

from __future__ import annotations

import argparse
import functools
import json
import sys
from datetime import date, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from repo_model import baseline  # noqa: E402
from repo_model.contract import QUANTILE_LEVELS  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration, split_summary  # noqa: E402
from repo_model.metrics import crps_from_quantiles, stationary_bootstrap_interval  # noqa: E402

#: The first locked day, `docs/decisions/lockbox.md`'s near-blind tier.
LOCKED_FROM = date(2026, 1, 1)
#: The published records' block length and replications, so the intervals here
#: are drawn as theirs are.
BLOCK_LENGTH = 2
REPLICATIONS = 2000
LEVEL = 0.9
SEED = 78


def _cut(rows, scored_before):
    if scored_before > LOCKED_FROM:
        raise ValueError(
            f"--scored-before {scored_before} is after {LOCKED_FROM}, the first "
            f"locked day (docs/decisions/lockbox.md); a comparison scores only "
            f"days before it"
        )
    return [row for row in rows if row.date < scored_before]


def score(args):
    from repo_model import ml

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    rows = _cut(load_daily_panel(args.panel), args.scored_before)
    features = tuple(args.feature)
    regressors = tuple(column for column in features if column != "spread_bps")
    settings = {"calibration": "cross_conformal", "calibration_folds": args.calibration_folds}
    if args.masking == "on":
        settings["calibration_masking"] = "held_out_row"
    decision_time = time.fromisoformat(args.decision_time)
    out = {
        "path": args.path,
        "masking": args.masking,
        "features": sorted(features),
        "settings": settings,
        "minimum_history": args.minimum_history,
        "refit_every": args.refit_every,
        "scored_before": args.scored_before.isoformat(),
        "panel_last_row_used": rows[-1].date.isoformat(),
    }
    if args.path == "backtest":
        report = baseline.rolling_persistence_backtest(
            rows,
            features=features,
            registry=registry,
            decision_time=decision_time,
            minimum_history=args.minimum_history,
            fit_model=functools.partial(
                ml.fit_gradient_boosted_quantiles, regressors=regressors, **settings
            ),
            refit_every=args.refit_every,
        )
        days = []
        for fold, forecast in zip(report.folds, report.forecasts):
            days.append(
                {
                    "date": fold.scored_date.isoformat(),
                    "actual": forecast.actual_bps,
                    "lower": forecast.lower_bps,
                    "upper": forecast.upper_bps,
                    "covered": int(forecast.lower_bps <= forecast.actual_bps <= forecast.upper_bps),
                    "width": forecast.upper_bps - forecast.lower_bps,
                    "crps": crps_from_quantiles(
                        QUANTILE_LEVELS, forecast.quantiles_bps, forecast.actual_bps
                    ),
                }
            )
        out["model_settings"] = dict(baseline._model_settings(report.model))
    else:
        taus = tuple(args.tau)
        report = baseline.rolling_exceedance_backtest(
            rows,
            predictor=ml.gbm_exceedance(
                regressors, minimum_history=args.minimum_history, **settings
            ),
            model_name="gbm",
            features=features,
            registry=registry,
            decision_time=decision_time,
            taus=taus,
            minimum_history=args.minimum_history,
            refit_every=args.refit_every,
        )
        days = []
        for when, forecast, outcome in zip(report.scored_dates, report.forecast, report.outcomes):
            days.append(
                {
                    "date": when.isoformat(),
                    "probability": list(forecast),
                    "outcome": list(outcome),
                    "brier": [(p - y) ** 2 for p, y in zip(forecast, outcome)],
                }
            )
        out["taus_bp"] = list(taus)
        out["model_settings"] = dict(report.model_settings)
    late = [day["date"] for day in days if date.fromisoformat(day["date"]) >= LOCKED_FROM]
    if late:
        raise ValueError(f"scored a locked day: {late[0]}")
    out["days"] = days
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _summary(labels_regime, labels_type, series, splits):
    values = [float(value) for value in series]

    def mean(indices):
        return sum(values[i] for i in indices) / len(indices)

    lower, upper = stationary_bootstrap_interval(
        mean,
        len(values),
        block_length=BLOCK_LENGTH,
        seed=SEED,
        replications=REPLICATIONS,
        level=LEVEL,
    )
    common = dict(block_length=BLOCK_LENGTH, seed=SEED, replications=REPLICATIONS, level=LEVEL)
    return {
        "mean": sum(values) / len(values),
        "interval": {"lower": lower, "upper": upper},
        "days_changed": sum(value != 0.0 for value in values),
        "by_regime": split_summary(labels_regime, values, splits.regime_labels, **common),
        "by_day_type": split_summary(
            labels_type, values, ("quarter_end", "month_end", "tax_date", "ordinary"), **common
        ),
    }


def compare(args):
    off = json.loads(args.off.read_text(encoding="utf-8"))
    on = json.loads(args.on.read_text(encoding="utf-8"))
    if (off["masking"], on["masking"]) != ("off", "on"):
        raise ValueError("compare takes the masking-off scoring first, then masking-on")
    for key in ("path", "features", "minimum_history", "refit_every", "scored_before"):
        if off[key] != on[key]:
            raise ValueError(f"the two scorings differ in {key}: {off[key]!r} != {on[key]!r}")
    dates_off = [day["date"] for day in off["days"]]
    if dates_off != [day["date"] for day in on["days"]]:
        raise ValueError("the two scorings did not score the same days")
    splits = load_split_declaration(args.splits)
    panel = {row.date: row for row in load_daily_panel(args.panel)}
    days = [date.fromisoformat(when) for when in dates_off]
    regimes = [splits.regime(when) for when in days]
    types = [splits.day_type(panel[when].values) for when in days]
    result = {
        "path": off["path"],
        "features": off["features"],
        "settings_off": off["model_settings"],
        "settings_on": on["model_settings"],
        "minimum_history": off["minimum_history"],
        "refit_every": off["refit_every"],
        "scored_days": len(days),
        "scored_window": [dates_off[0], dates_off[-1]],
        "sign": "masked minus published (calibration_masking held_out_row minus None)",
        "bootstrap": {"block_length": BLOCK_LENGTH, "replications": REPLICATIONS, "level": LEVEL, "seed": SEED},
    }
    if off["path"] == "backtest":
        for name in ("covered", "width", "crps"):
            a = [day[name] for day in off["days"]]
            b = [day[name] for day in on["days"]]
            result[name] = {
                "published_mean": sum(a) / len(a),
                "masked_mean": sum(b) / len(b),
                "difference": _summary(regimes, types, [y - x for x, y in zip(a, b)], splits),
            }
    else:
        result["taus_bp"] = off["taus_bp"]
        result["brier"] = {}
        for position, tau in enumerate(off["taus_bp"]):
            a = [day["brier"][position] for day in off["days"]]
            b = [day["brier"][position] for day in on["days"]]
            result["brier"][f"{tau:g}"] = {
                "published_mean": sum(a) / len(a),
                "masked_mean": sum(b) / len(b),
                "difference": _summary(regimes, types, [y - x for x, y in zip(a, b)], splits),
            }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score")
    s.add_argument("panel", type=Path)
    s.add_argument("--path", choices=("backtest", "exceedance"), required=True)
    s.add_argument("--masking", choices=("off", "on"), required=True)
    s.add_argument("--registry", type=Path, default=ROOT / "metadata" / "sources.json")
    s.add_argument("--feature", action="append", required=True)
    s.add_argument("--decision-time", default="16:00")
    s.add_argument("--minimum-history", type=int, required=True)
    s.add_argument("--refit-every", type=int, required=True)
    s.add_argument("--calibration-folds", type=int, default=5)
    s.add_argument("--tau", type=float, action="append", default=None)
    s.add_argument("--scored-before", type=date.fromisoformat, default=LOCKED_FROM)
    s.add_argument("--output", type=Path, required=True)
    c = sub.add_parser("compare")
    c.add_argument("off", type=Path)
    c.add_argument("on", type=Path)
    c.add_argument("panel", type=Path)
    c.add_argument("--splits", type=Path, default=ROOT / "metadata" / "evaluation_splits.json")
    args = parser.parse_args(argv)
    if args.command == "score":
        if args.path == "exceedance" and not args.tau:
            parser.error("--path exceedance needs --tau, repeatable")
        return score(args)
    return compare(args)


if __name__ == "__main__":
    raise SystemExit(main())
