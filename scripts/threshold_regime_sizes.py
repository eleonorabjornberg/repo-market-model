#!/usr/bin/env python3
"""How many training rows each threshold regime gets, fold by fold.

The threshold ARX lost to persistence under CRPS with a very wide interval on
the paired difference, and the leading explanation is that splitting the
training frame in two leaves one regime too little data to fit. This script
tests that explanation instead of repeating it: it walks the origins
`paired_model_comparison` walks -- `splits.rolling_origin` with the gap
`baseline._derive_purge` prices for the declared features -- fits
`baseline.fit_threshold` on each training frame exactly as `compare
--model threshold` binds it (regressors split from the declaration by
`cli_eval._regressors_and_regime`, not by a copy of that rule), and records the
estimated threshold, the design rows in each regime, and which regime the
origin's feature row falls in.

The last one is the number that matters: a regime with few rows is harmless if
no forecast is made from it, and decisive if the forecasts are.

A full walk is one fit per origin on an expanding frame, and the fit's
threshold search grows with the frame -- about an hour on the frozen panel.
`--every N` fits one origin in N (earliest first, always including the last) for
a quick look; the summary says which it did. Reads the gitignored frozen panel,
so it is not a test. Nothing is published by running it.

Usage:

    PYTHONPATH=src python3 scripts/threshold_regime_sizes.py \
        [--panel data/processed/funding_panel.csv] \
        [--registry metadata/sources.json] [--decision-time 16:00] \
        [--minimum-history 61] [--regime-variable sofr_volume] \
        [--feature spread_bps --feature sofr_volume ...] \
        [--every 1] [--csv OUT.csv] [--json OUT.json]

The defaults are the declaration of the unpublished `sofr_volume` threshold run.
Stdlib only.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from datetime import time
from pathlib import Path

from repo_model.baseline import (
    _derive_purge,
    _feature_index,
    fit_threshold,
    panel_sha256,
)
from repo_model.cli_eval import _regressors_and_regime
from repo_model.data import load_daily_panel
from repo_model.ingest import load_source_registry
from repo_model.splits import rolling_origin

DEFAULT_FEATURES = ("spread_bps", "sofr_volume", "sofr_p25", "sofr_p75")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--panel", type=Path, default=Path("data/processed/funding_panel.csv"))
    parser.add_argument("--registry", type=Path, default=Path("metadata/sources.json"))
    parser.add_argument("--decision-time", default="16:00")
    parser.add_argument("--minimum-history", type=int, default=61)
    parser.add_argument("--regime-variable", default="sofr_volume")
    parser.add_argument("--feature", action="append")
    parser.add_argument("--every", type=int, default=1)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    if args.every < 1:
        parser.error("--every must be at least 1")

    features = tuple(args.feature or DEFAULT_FEATURES)
    regressors, regime = _regressors_and_regime(
        argparse.Namespace(feature=list(features), regime_variable=args.regime_variable),
        "threshold",
        True,
    )
    rows = load_daily_panel(args.panel)
    dates = [row.date for row in rows]
    _fields, _sources, purge = _derive_purge(
        load_source_registry(args.registry),
        tuple(sorted(features)),
        decision_time=time.fromisoformat(args.decision_time),
    )
    folds = list(rolling_origin(dates, args.minimum_history, 1, purge))
    chosen = [i for i in range(len(folds)) if i % args.every == 0]
    if chosen[-1] != len(folds) - 1:
        chosen.append(len(folds) - 1)

    records = []
    for i in chosen:
        train_indices, test_indices = folds[i]
        frame = [rows[j] for j in train_indices]
        fitted = fit_threshold(
            frame, regressors, regime, minimum_history=args.minimum_history
        )
        feature_row = rows[_feature_index(dates, train_indices, test_indices[0], purge)]
        side = fitted.regime_for(feature_row)
        counts = dict(fitted.regime_rows)
        records.append(
            {
                "feature_date": feature_row.date.isoformat(),
                "scored_date": rows[test_indices[0]].date.isoformat(),
                "train_rows": len(train_indices),
                "threshold": fitted.threshold,
                "low_rows": counts["low"],
                "high_rows": counts["high"],
                "feature_regime": side,
                "feature_regime_rows": counts[side],
            }
        )

    forecast_rows = [r["feature_regime_rows"] for r in records]
    smaller = [min(r["low_rows"], r["high_rows"]) for r in records]
    summary = {
        "panel": {"path": str(args.panel), "sha256": panel_sha256(args.panel)},
        "regressors": list(regressors),
        "regime_variable": regime,
        "purge_days": purge,
        "minimum_history": args.minimum_history,
        "origins": len(folds),
        "fitted": len(records),
        "every": args.every,
        "feature_row_in_high": sum(r["feature_regime"] == "high" for r in records),
        "feature_regime_rows": {
            "min": min(forecast_rows),
            "median": statistics.median(forecast_rows),
            "max": max(forecast_rows),
        },
        "smaller_regime_rows": {
            "min": min(smaller),
            "median": statistics.median(smaller),
            "max": max(smaller),
        },
        "feature_regime_share_of_train": {
            "min": round(min(r["feature_regime_rows"] / r["train_rows"] for r in records), 4),
            "median": round(
                statistics.median(r["feature_regime_rows"] / r["train_rows"] for r in records), 4
            ),
        },
    }
    if args.csv:
        with args.csv.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    if args.json:
        args.json.write_text(json.dumps({"summary": summary, "folds": records}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
