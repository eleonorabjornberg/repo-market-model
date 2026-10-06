"""The knowledge holdout and the H.4.1 lag, as two reported-only studies (#280).

Eleonora's ruling of 6 October 2026 on #269, items 8 and 18. Both studies decide
nothing and move no headline: the live model keeps the five-day H.4.1 lag, and
no published record is edited. This script writes one JSON file, to a path
given, and nothing into `docs/runs/`.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/knowledge_holdout_lag_study.py \\
        --panel /tmp/funding_panel.csv --journal /tmp/kh/journal.jsonl \\
        --output docs/pivot/studies/knowledge_holdout_lag_study.json

Study 1 -- the knowledge holdout (item 18). Each declared window in
`metadata/events.json` is scored once per model by `event_eval.evaluate_event_window`:
crises stripped from training, the as-of rule on every read. The models are the
**uncalibrated** gbm on the two published feature sets, and the three benchmarks
(climatology, calendar-type climatology, persistence-logistic). No published
(calibrated) model is held out from these windows: the published records are
scored with the crisis days in the training set once they are in the past, and
the calibration is fitted on that history. The tables are labelled uncalibrated
for that reason. Results are paired day by day (benchmark Brier minus model
Brier, so positive favours the model), carry a stationary-bootstrap interval, and
are split by regime and by pressure-day type by the declaration's own
`split_document`. The contract's rule that a single window gets no aggregate
number is kept for each window alone; this is the pooled evaluation over the
declared windows that `event_eval`'s docstring says a metric would belong to, and
it is reported separately, never averaged into a main table.

Study 2 -- the H.4.1 lag (item 8). (a) First-print lags measured from the tracked
ALFRED vintages: for each Wednesday observation, the first tracked vintage that
carries it. (b) A shorter lag priced against the declared five days on the
published nine-feature funding declaration (uncalibrated gbm), by scoring the same
rolling grid under a copy of the registry whose H.4.1 fields (WRESBAL, WTREGEN)
carry the shorter lag. The registry file is not edited. Scored days end
2025-12-31; `lockbox.require_unlocked` refuses anything later.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import re
import sys
from datetime import date, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from repo_model import cli_eval  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    benchmark_comparison_document,
    rolling_exceedance_backtest,
    split_document,
)
from repo_model.cli import build_parser  # noqa: E402
from repo_model.data import load_daily_panel, load_stress_thresholds  # noqa: E402
from repo_model.event_eval import evaluate_event_window, load_events_file  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_interval  # noqa: E402
from repo_model.onset import whole_bp  # noqa: E402

DECISION_TIME = time(16, 0)
MINIMUM_HISTORY = 61
END = date(2025, 12, 31)
BLOCK_LENGTH = 2
REPLICATIONS = 2000
LEVEL = 0.90

PUBLISHED_FOUR = ("sofr_p25", "sofr_p75", "sofr_volume", "spread_bps")
PUBLISHED_NINE = (
    "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps",
    "tbill_13w", "tbill_4w", "tga", "treasury_settlement",
)
BENCHMARK_ORDER = ("climatology", "calendar_climatology", "persistence_logistic")
H41_FIELDS = ("WRESBAL", "WTREGEN")
H41_SOURCE = "fred_macro_latest_vintage"
SHORTER_LAGS = (1, 2)
MAXIMUM_VINTAGE_GAP_DAYS = 7
FIRST_PRINT = ROOT / "tests" / "fixtures" / "snapshots" / "alfred-h41-first-print"


# --------------------------------------------------------------------------
# Predictors, selected the way the event-holdout command selects them
# --------------------------------------------------------------------------


def _predictor(model: str, features, splits_path: Path):
    arguments = [
        "event-holdout", "--panel", "-", "--events", "-", "--thresholds", "-",
        "--registry", "-", "--journal", "-", "--decision-time", "16:00",
        "--model", model, "--minimum-history", str(MINIMUM_HISTORY),
    ]
    for feature in features:
        arguments += ["--feature", feature]
    args = build_parser().parse_args(arguments)
    # `event-holdout` has no --splits; the calendar benchmark reads the pressure-day
    # types from the declaration, so the namespace carries the path.
    args.splits = str(splits_path)
    return cli_eval._select_model(args, settings_flags=True)[1]


# --------------------------------------------------------------------------
# Study 1: the knowledge holdout
# --------------------------------------------------------------------------


def _label(realized: float, tau: float) -> int:
    return 1 if whole_bp(realized) > tau else 0


def knowledge_holdout(rows, registry, declaration, windows, taus, splits_path, journal):
    runs = {}
    candidates = (
        [("gbm_published_4", "gbm", PUBLISHED_FOUR)]
        + [("gbm_published_9", "gbm", PUBLISHED_NINE)]
        + [
            ("climatology", "climatology", ("spread_bps",)),
            (
                "calendar_climatology", "calendar_climatology",
                cli_eval.BENCHMARK_FEATURES["calendar_climatology"],
            ),
            ("persistence_logistic", "persistence_logistic", ("spread_bps",)),
        ]
    )
    for name, model, features in candidates:
        predictor = _predictor(model, features, splits_path)
        reports = []
        for window in windows:
            reports.append(
                evaluate_event_window(
                    rows, predictor, window,
                    features=features, registry=registry,
                    decision_time=DECISION_TIME, taus=taus,
                    model_config={
                        "model": model, "study": "knowledge_holdout_lag_study (#280)",
                        "features": sorted(features),
                        "minimum_history": MINIMUM_HISTORY,
                        "taus_bp": list(taus),
                    },
                    journal_path=journal,
                )
            )
        runs[name] = reports
    dates, outcomes = [], []
    for report in runs["climatology"]:
        for when, realized in zip(report.scored_dates, report.realized):
            dates.append(when)
            outcomes.append([_label(realized, tau) for tau in taus])
    for name, reports in runs.items():  # the grid must be one grid
        got = [d for report in reports for d in report.scored_dates]
        if got != dates:
            raise ValueError(f"{name} scored different days from the climatology")
    curves = {
        name: [list(c) for report in reports for c in report.exceedance]
        for name, reports in runs.items()
    }
    pairs = {
        "gbm_published_4": BENCHMARK_ORDER,
        "gbm_published_9": BENCHMARK_ORDER,
        "persistence_logistic": ("climatology", "calendar_climatology"),
        "calendar_climatology": ("climatology",),
        "climatology": ("climatology",),  # the control: must be exactly zero
    }
    table = {}
    for model, benchmarks in pairs.items():
        for bench in benchmarks:
            per_tau = {}
            for position, tau in enumerate(taus):
                model_loss = [
                    (curves[model][i][position] - outcomes[i][position]) ** 2
                    for i in range(len(dates))
                ]
                bench_loss = [
                    (curves[bench][i][position] - outcomes[i][position]) ** 2
                    for i in range(len(dates))
                ]
                diff = [b - m for b, m in zip(bench_loss, model_loss)]
                seed = 280_000 + 100 * position + len(model) + 7 * len(bench)

                def mean_of(indices, values=diff):
                    return sum(values[i] for i in indices) / len(indices)

                lower, upper = stationary_bootstrap_interval(
                    mean_of, len(diff), block_length=BLOCK_LENGTH, seed=seed,
                    replications=REPLICATIONS, level=LEVEL,
                )
                per_tau[f"{tau:g}"] = {
                    "tau_bp": tau,
                    "days": len(diff),
                    "positive_days": sum(o[position] for o in outcomes),
                    "model_brier": sum(model_loss) / len(diff),
                    "benchmark_brier": sum(bench_loss) / len(diff),
                    "paired_brier_difference": {
                        "mean": mean_of(range(len(diff))),
                        "interval": {"lower": lower, "upper": upper, "level": LEVEL},
                        "splits": split_document(
                            declaration, rows, dates, diff,
                            block_length=BLOCK_LENGTH, seed=seed,
                        ),
                    },
                }
            table[f"{model} vs {bench}"] = per_tau
    return {
        "label": "uncalibrated: no published (calibrated) model is held out from these windows",
        "windows": [
            {
                "name": report.window.name, "start": report.window.start.isoformat(),
                "end": report.window.end.isoformat(),
                "train_rows": report.train_rows,
                "last_train_date": report.last_train_date.isoformat(),
            }
            for report in runs["climatology"]
        ],
        "days": [d.isoformat() for d in dates],
        "taus_bp": list(taus),
        "sign": "benchmark Brier minus model Brier; positive favours the model",
        "bootstrap": {"block_length": BLOCK_LENGTH, "replications": REPLICATIONS, "level": LEVEL},
        "comparisons": table,
        "curves": {
            name: [
                {"date": d.isoformat(), "exceedance": curves[name][i]}
                for i, d in enumerate(dates)
            ]
            for name in curves
        },
        "realized_bps": [
            r for report in runs["climatology"] for r in report.realized
        ],
    }


# --------------------------------------------------------------------------
# Study 2a: measured first-print lags, from the tracked vintages
# --------------------------------------------------------------------------


def _vintage(path: Path):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    stamp = re.fullmatch(r"(\w+?)_(\d{8})", rows[0][1].strip()).group(2)
    vintage = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
    return vintage, {
        date.fromisoformat(r[0]): r[1] for r in rows[1:] if r[1].strip() not in ("", ".")
    }


def measured_lags():
    cases = []
    for series in ("WRESBAL", "WLRRAOL"):
        vintages = sorted(_vintage(p) for p in FIRST_PRINT.glob(f"{series}_*.csv"))
        for (earlier, before), (later, after) in zip(vintages, vintages[1:]):
            if (later - earlier).days > MAXIMUM_VINTAGE_GAP_DAYS:
                # Not adjacent daily vintages: an observation new between them
                # was first printed somewhere in the gap, so no lag is measured.
                continue
            new = sorted(set(after) - set(before))
            for observation in new:
                cases.append(
                    {
                        "series": series,
                        "observation": observation.isoformat(),
                        "last_vintage_without": earlier.isoformat(),
                        "first_vintage_with": later.isoformat(),
                        "lag_calendar_days_at_most": (later - observation).days,
                        "lag_calendar_days_at_least": (earlier - observation).days + 1,
                    }
                )
    return cases


# --------------------------------------------------------------------------
# Study 2b: a shorter lag, priced against the declared five days
# --------------------------------------------------------------------------


def with_h41_lag(registry, days):
    """A copy of the registry whose H.4.1 fields carry `days` instead of their lag."""

    changed = copy.deepcopy(registry)
    fields = changed[H41_SOURCE]["field_release_lags"]
    for name in H41_FIELDS:
        fields[name]["days"] = days
        fields[name]["note"] = (
            f"#280 STUDY COPY, never written to metadata/sources.json: {days} "
            f"calendar day(s) in place of the declared lag."
        )
    return changed


def _run(rows, registry, taus, features, name):
    predictor = _predictor("gbm", features, ROOT / "metadata" / "evaluation_splits.json")
    return rolling_exceedance_backtest(
        rows, predictor=predictor, model_name=name, features=features,
        registry=registry, decision_time=DECISION_TIME, taus=taus,
        minimum_history=MINIMUM_HISTORY, refit_every=21, end=END,
    )


def lag_pricing(rows, registry, declaration, taus, panel_sha):
    baseline = _run(rows, registry, taus, PUBLISHED_NINE, "gbm_lag_5")
    require_unlocked(baseline.scored_dates, where="knowledge_holdout_lag_study")
    out = {
        "model": "uncalibrated gbm on the nine published funding features",
        "declared_lag_calendar_days": registry[H41_SOURCE]["field_release_lags"]["WRESBAL"]["days"],
        "scored_days": len(baseline.scored_dates),
        "first_scored": baseline.scored_dates[0].isoformat(),
        "last_scored": baseline.scored_dates[-1].isoformat(),
        "sign": "5-day Brier minus shorter-lag Brier; positive favours the shorter lag",
        "information": {
            feature: baseline.information["features"].get(feature)
            if isinstance(baseline.information, dict) and "features" in baseline.information
            else None
            for feature in ("reserve_balances", "tga")
        },
        "shorter": {},
    }
    for days in SHORTER_LAGS:
        shorter = _run(
            rows, with_h41_lag(registry, days), taus, PUBLISHED_NINE, f"gbm_lag_{days}"
        )
        document = benchmark_comparison_document(
            shorter, baseline, panel_sha256=panel_sha, rows=rows, declaration=declaration
        )
        out["shorter"][str(days)] = {
            "scored_days": len(shorter.scored_dates),
            "same_grid": list(shorter.scored_dates) == list(baseline.scored_dates),
            "comparison": document,
            "information": shorter.information,
        }
    out["information"] = baseline.information
    return out


# --------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-lag-pricing", action="store_true")
    args = parser.parse_args(argv)

    import hashlib

    panel_sha = hashlib.sha256(args.panel.read_bytes()).hexdigest()
    rows = load_daily_panel(args.panel)
    registry = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
    thresholds = load_stress_thresholds(ROOT / "metadata" / "stress_thresholds.json")
    taus = tuple(float(t) for t in thresholds["taus_bp"])
    splits_path = ROOT / "metadata" / "evaluation_splits.json"
    declaration = load_split_declaration(splits_path)
    windows = load_events_file(ROOT / "metadata" / "events.json")
    # The knowledge-holdout windows precede the locked tiers; the guard says so.
    require_unlocked(
        [d for w in windows for d in (w.start, w.end)],
        where="knowledge_holdout_lag_study windows",
    )

    result = {
        "reported_only": True,
        "decides_nothing": "the live model keeps the 5-day H.4.1 lag; no published record or headline moves",
        "panel_sha256": panel_sha,
        "knowledge_holdout": knowledge_holdout(
            rows, registry, declaration, windows, taus, splits_path, args.journal
        ),
        "h41_measured_lags": measured_lags(),
    }
    if not args.skip_lag_pricing:
        result["h41_lag_pricing"] = lag_pricing(
            rows, registry, declaration, taus, panel_sha
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
