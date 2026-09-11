#!/usr/bin/env python3
"""Autocorrelation of spread changes and of their size, on the frozen panel.

The question this answers is the one the gbm-variant agenda (GARCH, a
conditional-volatility residual law) rests on: **is there volatility clustering
in `spread_bps`, and is it there at the horizon the comparisons score?** The
rolling-residual result (a trailing-window residual law beating persistence
under CRPS) is consistent with clustering and does not establish it. This
script measures it, so the statement is re-runnable rather than prose.

Two parts, both printed as JSON:

* **Daily changes.** `d_t = s_t - s_{t-1}` over consecutive panel rows, where
  `s` is `DailyObservation.spread_bps` -- the package's definition, not a copy.
  Sample autocorrelations at lags 1..L of `d`, `|d|` and `d^2`, the 95% band
  under independence (`1.96 / sqrt(n)`), and Ljung-Box Q(L) with its p-value.
  Autocorrelation in `d` bears on the centre (is persistence's point rule
  improvable?); autocorrelation in `|d|` and `d^2` is clustering.

* **Persistence's error at the scored horizon.** The comparisons do not score a
  one-day change: each origin's forecast is conditioned on the last row that
  clears the purge gap, several rows before the scored day. This part walks
  `splits.rolling_origin` with the gap `baseline._derive_purge` prices for the
  declared features -- the construction `paired_model_comparison` uses -- and
  takes `e = s(scored) - s(feature)` at every origin. Two errors whose origins
  are at most the widest window apart share increments, or share an endpoint
  row (lag equal to a window: one error's scored day is the other's feature
  day, so a one-day spike inflates both). Their autocorrelation there is
  mechanical, so for `|e|` only lags beyond the widest window are reported;
  those are what a scale model could exploit.

Reads the gitignored frozen panel, so it is not a test, the same posture as
`scripts/nmfp_identity_residuals.py`. Nothing here is published by being run;
a page quoting these numbers cites this script and the panel digest it prints.

Usage:

    PYTHONPATH=src python3 scripts/spread_change_autocorrelation.py \
        [--panel data/processed/funding_panel.csv] \
        [--registry metadata/sources.json] [--decision-time 16:00] \
        [--minimum-history 61] [--lags 10] \
        [--feature spread_bps --feature sofr_volume ...] [--json OUT.json]

`--lags` must be even: the Ljung-Box p-value uses the closed-form chi-square
survival function for even degrees of freedom, so no special-function
approximation stands between the statistic and its p-value. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import time
from pathlib import Path

from repo_model.baseline import _derive_purge, _feature_index, panel_sha256
from repo_model.data import load_daily_panel
from repo_model.ingest import load_source_registry
from repo_model.splits import rolling_origin

#: The gbm and threshold comparisons' declaration; persistence's gap is priced
#: over the same set in every published CRPS record.
DEFAULT_FEATURES = ("spread_bps", "sofr_volume", "sofr_p25", "sofr_p75")


def autocorrelations(series, lags):
    """Sample autocorrelation at 1..lags, the usual biased estimator."""

    n = len(series)
    mean = sum(series) / n
    centred = [x - mean for x in series]
    denominator = sum(c * c for c in centred)
    return [
        sum(centred[t] * centred[t - k] for t in range(k, n)) / denominator
        for k in range(1, lags + 1)
    ]


def ljung_box(acf, n):
    """Q over the given autocorrelations, and its chi-square(len) p-value."""

    q = n * (n + 2) * sum(r * r / (n - k) for k, r in enumerate(acf, start=1))
    df = len(acf)
    half = q / 2.0
    # Survival function of chi-square with even df = 2m: exp(-x/2) * sum_{i<m} (x/2)^i / i!
    term, total = 1.0, 1.0
    for i in range(1, df // 2):
        term *= half / i
        total += term
    return q, math.exp(-half) * total


def describe(series, lags):
    acf = autocorrelations(series, lags)
    q, p = ljung_box(acf, len(series))
    return {
        "n": len(series),
        "acf": [round(r, 4) for r in acf],
        "band_95": round(1.96 / math.sqrt(len(series)), 4),
        "ljung_box_q": round(q, 2),
        "ljung_box_p": p,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--panel", type=Path, default=Path("data/processed/funding_panel.csv"))
    parser.add_argument("--registry", type=Path, default=Path("metadata/sources.json"))
    parser.add_argument("--decision-time", default="16:00")
    parser.add_argument("--minimum-history", type=int, default=61)
    parser.add_argument("--lags", type=int, default=10)
    parser.add_argument("--feature", action="append")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    if args.lags < 2 or args.lags % 2:
        parser.error("--lags must be an even number, at least 2")

    rows = load_daily_panel(args.panel)
    spreads = [row.spread_bps for row in rows]
    daily = [b - a for a, b in zip(spreads, spreads[1:])]

    features = tuple(sorted(args.feature or DEFAULT_FEATURES))
    decision_time = time.fromisoformat(args.decision_time)
    _fields, _sources, purge = _derive_purge(
        load_source_registry(args.registry), features, decision_time=decision_time
    )
    dates = [row.date for row in rows]
    errors, widths = [], []
    for train_indices, test_indices in rolling_origin(
        dates, args.minimum_history, 1, purge
    ):
        scored = test_indices[0]
        feature = _feature_index(dates, train_indices, scored, purge)
        errors.append(spreads[scored] - spreads[feature])
        widths.append(scored - feature)
    width = max(widths)
    absolute = [abs(e) for e in errors]
    beyond = autocorrelations(absolute, width + args.lags)[width:]

    report = {
        "panel": {
            "path": str(args.panel),
            "sha256": panel_sha256(args.panel),
            "rows": len(rows),
            "first_date": rows[0].date.isoformat(),
            "last_date": rows[-1].date.isoformat(),
        },
        "daily_change": {
            "d": describe(daily, args.lags),
            "abs_d": describe([abs(x) for x in daily], args.lags),
            "d_squared": describe([x * x for x in daily], args.lags),
        },
        "persistence_error_at_scored_horizon": {
            "features": list(features),
            "purge_days": purge,
            "minimum_history": args.minimum_history,
            "origins": len(errors),
            "window_rows": {"min": min(widths), "max": width},
            "e": describe(errors, args.lags),
            "abs_e_from_lag": width + 1,
            "abs_e_acf_beyond_overlap": [round(r, 4) for r in beyond],
            "band_95": round(1.96 / math.sqrt(len(errors)), 4),
        },
    }
    text = json.dumps(report, indent=2)
    if args.json:
        args.json.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
