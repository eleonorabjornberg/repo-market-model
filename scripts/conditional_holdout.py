"""A conditional pressure-probability predictor against climatology on the knowledge holdouts (#372).

Reported-only. The declaration is `docs/pivot/conditional-vs-climatology-declaration.json`,
committed before anything was scored; this script reads it, refuses a window or a setting
that is not the one it declares, and writes one JSON file and nothing into `docs/runs/`.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/conditional_holdout.py \\
        --panel /tmp/funding_panel.csv --journal /tmp/ch/journal.jsonl \\
        --output docs/pivot/studies/conditional_vs_climatology_holdout.json

Each declared window is scored once per model by `event_eval.evaluate_event_window`: the
window stripped from training, the as-of rule on every read. The models are the uncalibrated
conditional predictors of the declaration, and the benchmarks. Targets are +5 bp, +10 bp
and the plain leap at h = 1 (`onset.LEAP_JUMP_BP[1]`). A predictor's curve is requested at
+5, +10 and each day's leap level together, and read at the target's level. Scores are
paired Brier differences (benchmark minus predictor, positive favours the predictor) with a
stationary-bootstrap interval, split by regime, pressure-day type and the at-risk groups.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from repo_model import cli_eval, ml, onset, pressure  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import split_document  # noqa: E402
from repo_model.cli import build_parser  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.event_eval import evaluate_event_window, load_events_file  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION_PATH = ROOT / "docs" / "pivot" / "conditional-vs-climatology-declaration.json"
EVENTS = ROOT / "metadata" / "events.json"
REGISTRY = ROOT / "metadata" / "sources.json"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
DECISION_TIME = time(16, 0)
MINIMUM_HISTORY = 61
HORIZON = 1
BLOCK_LENGTH = 2
REPLICATIONS = 2000
LEVEL = 0.90
PRESSURE_TAUS = (5, 10)
BENCHMARKS = ("climatology", "persistence_logistic")
PREDICTORS = {
    "gbm_published_4": ("sofr_p25", "sofr_p75", "sofr_volume", "spread_bps"),
    "gbm_published_9": (
        "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps",
        "tbill_13w", "tbill_4w", "tga", "treasury_settlement",
    ),
    "dynamic_logit": (
        "spread_bps", "days_to_month_end", "quarter_end", "tax_date",
        "treasury_settlement_coupons", "reserve_balances",
    ),
}
PREDICTORS["probit_literature"] = PREDICTORS["dynamic_logit"]
PREDICTORS["quantile_literature"] = PREDICTORS["dynamic_logit"]
BENCHMARK_FEATURES = ("spread_bps",)
USEFULNESS_MU = 0.5
ALARM_LEVEL = 0.5
TARGETS = ("pressure_5", "pressure_10", "leap")


def declaration_digest(declared) -> str:
    text = json.dumps(declared, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_declaration(declared) -> None:
    """Raise ValueError unless the declaration names exactly the windows of `events.json`."""

    events = json.loads(EVENTS.read_text())
    names = [window["name"] for window in events["windows"]]
    if list(declared["holdout_windows"]["names"]) != names:
        raise ValueError(
            f"the declaration names windows {declared['holdout_windows']['names']}, "
            f"but {EVENTS.name} declares {names}"
        )


def auroc(forecast, outcome):
    """Mann-Whitney area under the ROC, ties one half; `None` when a class is empty."""

    positives = [f for f, o in zip(forecast, outcome) if o]
    negatives = [f for f, o in zip(forecast, outcome) if not o]
    if not positives or not negatives:
        return None
    wins = sum(
        1.0 if p > n else 0.5 if p == n else 0.0 for p in positives for n in negatives
    )
    return wins / (len(positives) * len(negatives))


def usefulness(forecast, outcome, *, mu=USEFULNESS_MU):
    """Sarlin's usefulness of the best alarm `forecast >= theta`, in sample.

    loss(theta) = mu * missed-event rate + (1 - mu) * false-alarm rate;
    absolute = min(mu, 1 - mu) - min over theta of loss. `None` when a class is empty.
    """

    positives = sum(1 for o in outcome if o)
    negatives = len(outcome) - positives
    if not positives or not negatives:
        return None
    blind = min(mu, 1.0 - mu)
    best = min(
        mu * sum(1 for f, o in zip(forecast, outcome) if o and f < theta) / positives
        + (1.0 - mu) * sum(1 for f, o in zip(forecast, outcome) if not o and f >= theta) / negatives
        for theta in sorted(set(forecast))
    )
    return {"mu": mu, "loss": best, "absolute": blind - best, "relative": (blind - best) / blind}


def lead_time(forecast, days, onset_days, *, level=ALARM_LEVEL):
    """`pressure.lead_times` at this study's one horizon (h = 1)."""

    by_day = dict(zip(days, forecast))
    found = pressure.lead_times({1: by_day}, list(onset_days), level)
    return {key: found[key] for key in ("alarm_level", "onsets", "flagged", "mean_lead_days")}


def early_warning(forecast, outcome, days, target, rows, targets):
    """AUROC, usefulness and lead time of one model at one target, pooled."""

    if target == "leap":
        onset_days = [days[k] for k in onset.leap_onset_group(targets, days) if outcome[k]]
    else:
        onset_days = pressure.onsets(rows, float(target.split("_")[1]), days)
    return {
        "auroc": auroc(forecast, outcome),
        "usefulness": usefulness(forecast, outcome),
        "lead_time": lead_time(forecast, days, onset_days),
    }


def leap_level(*, anchor_bp: float, jump_bp: float) -> float:
    """The spread above which a day is a leap (`onset.LeapTargets.event_threshold`)."""

    import math

    return math.floor(anchor_bp + jump_bp) + 0.5


def cell_verdict(pooled, cells) -> str:
    """The declared pass rule for one predictor at one target.

    `pooled` maps each benchmark to the pooled paired difference; `cells` is every
    regime and day-type cell's paired difference against either benchmark. A cell
    without an interval is reported and does not count.
    """

    def interval(entry):
        found = entry.get("interval")
        return None if found is None else (found["lower"], found["upper"])

    bounds = [interval(entry) for entry in pooled.values()]
    if any(b is None for b in bounds):
        return "inconclusive"
    worse = any(upper < 0 for _, upper in bounds)
    for cell in cells:
        found = interval(cell)
        if found is not None and found[1] < 0:
            worse = True
    if worse:
        return "not_met"
    if all(lower > 0 for lower, _ in bounds):
        return "met"
    return "inconclusive"


def _predictor(model, features):
    arguments = [
        "event-holdout", "--panel", "-", "--events", "-", "--thresholds", "-",
        "--registry", "-", "--journal", "-", "--decision-time", "16:00",
        "--model", model, "--minimum-history", str(MINIMUM_HISTORY),
    ]
    for feature in features:
        arguments += ["--feature", feature]
    args = build_parser().parse_args(arguments)
    args.splits = str(SPLITS)
    return cli_eval._select_model(args, settings_flags=True)[1]


def _candidates(declaration):
    """`(name, predictor, features)` for every predictor and benchmark scored."""

    out = []
    for name, features in PREDICTORS.items():
        if name.startswith("gbm"):
            predictor = _predictor("gbm", features)
        elif name == "probit_literature":
            predictor = ml.pressure_probit_exceedance(
                features, declaration, minimum_history=MINIMUM_HISTORY
            )
        elif name == "quantile_literature":
            predictor = ml.pressure_quantile_exceedance(
                features, declaration, minimum_history=MINIMUM_HISTORY
            )
        else:
            predictor = ml.dynamic_logit_exceedance(
                features, declaration, minimum_history=MINIMUM_HISTORY
            )
        out.append((name, predictor, features))
    out.append(("climatology", _predictor("climatology", BENCHMARK_FEATURES), BENCHMARK_FEATURES))
    out.append(
        (
            "persistence_logistic",
            _predictor("persistence_logistic", BENCHMARK_FEATURES),
            BENCHMARK_FEATURES,
        )
    )
    return out


def run(panel_path: Path, journal: Path) -> dict:
    declared = json.loads(DECLARATION_PATH.read_text())
    check_declaration(declared)
    registry = json.loads(REGISTRY.read_text())
    declaration = load_split_declaration(SPLITS)
    windows = load_events_file(EVENTS)
    rows = load_daily_panel(panel_path)
    jump = onset.LEAP_JUMP_BP[HORIZON]
    rule = InformationRule(
        registry, PREDICTORS["dynamic_logit"], decision_time=DECISION_TIME, horizon=HORIZON
    )
    targets = onset.LeapTargets(rows, rule, jump)
    position_of = {row.date: i for i, row in enumerate(rows)}

    # The days, the leap levels and the labels: levels read only the anchor's spread,
    # public at the decision; labels are the outcomes.
    days, levels, labels = [], [], {name: [] for name in TARGETS}
    for window in windows:
        for row in rows:
            if window.start <= row.date <= window.end:
                index = position_of[row.date]
                days.append(row.date)
                levels.append(targets.event_threshold(index, pressure=False))
                for tau in PRESSURE_TAUS:
                    labels[f"pressure_{tau}"].append(int(onset.whole_bp(row.spread_bps) > tau))
                labels["leap"].append(int(targets.leap[index]))
    require_unlocked(days, where="conditional_holdout")
    taus = tuple(sorted({float(t) for t in PRESSURE_TAUS} | set(levels)))

    curves, last_train, not_scored = {}, {}, {}
    for name, predictor, features in _candidates(declaration):
        per_day = []
        for window in windows:
            try:
                report = evaluate_event_window(
                    rows, predictor, window, features=features, registry=registry,
                    decision_time=DECISION_TIME, taus=taus,
                    model_config={
                        "model": name, "study": "conditional_holdout (#372)",
                        "features": sorted(features), "minimum_history": MINIMUM_HISTORY,
                        "taus_bp": list(taus),
                    },
                    journal_path=journal,
                )
            except ValueError as error:
                if name in BENCHMARKS:
                    raise
                not_scored[name] = f"{window.name}: {error}"
                per_day = None
                break
            last_train[window.name] = report.last_train_date
            for when, curve in zip(report.scored_dates, report.exceedance):
                per_day.append((when, curve))
        if per_day is None:
            continue
        if [d for d, _ in per_day] != days:
            raise ValueError(f"{name} scored different days from the declared windows")
        curves[name] = [curve for _, curve in per_day]

    column = {"pressure_5": taus.index(5.0), "pressure_10": taus.index(10.0)}
    forecasts = {name: {} for name in curves}
    for name, per_day in curves.items():
        for target in ("pressure_5", "pressure_10"):
            forecasts[name][target] = [curve[column[target]] for curve in per_day]
        forecasts[name]["leap"] = [
            curve[taus.index(level)] for curve, level in zip(per_day, levels)
        ]

    # The leap's own benchmarks (declared): the pooled training frequency and the
    # persistence-logistic of the leap, fitted on the days before each window.
    train_ends = [last_train[w.name] for w in windows for _ in range(
        sum(1 for d in days if w.start <= d <= w.end))]
    pooled_frequency = {}
    for window in windows:
        last = position_of[last_train[window.name]]
        counted = [targets.leap[i] for i in range(last + 1) if targets.jump[i] is not None]
        pooled_frequency[window.name] = sum(counted) / len(counted)
    forecasts["climatology"]["leap"] = [
        pooled_frequency[w.name] for w in windows
        for d in days if w.start <= d <= w.end
    ]
    forecasts["persistence_logistic"]["leap"] = onset.leap_persistence_logistic(
        targets, "leap", days, train_ends
    )

    groups = onset.day_groups(rows, days, declaration)
    leap_groups = {
        onset.GROUP_ALL: list(range(len(days))),
        onset.GROUP_LEAP_ONSET: onset.leap_onset_group(targets, days),
    }

    document = {
        "declaration": str(DECLARATION_PATH.relative_to(ROOT)),
        "declaration_sha256": declaration_digest(declared),
        "label": "uncalibrated: no published (calibrated) model is held out from these windows",
        "sign": "benchmark Brier minus predictor Brier; positive favours the predictor",
        "windows": [
            {"name": w.name, "start": w.start.isoformat(), "end": w.end.isoformat(),
             "last_train_date": last_train[w.name].isoformat()}
            for w in windows
        ],
        "days": [d.isoformat() for d in days],
        "leap": {"jump_bp": jump, "levels_bp": levels},
        "bootstrap": {"block_length": BLOCK_LENGTH, "replications": REPLICATIONS, "level": LEVEL},
        "not_scored": not_scored,
        "results": {},
    }
    for target in TARGETS:
        outcome = labels[target]
        target_groups = leap_groups if target == "leap" else groups
        entry = {"days": len(days), "events": sum(outcome)}
        for position, name in enumerate(PREDICTORS):
            if name not in curves:
                entry[name] = {"not_scored": not_scored[name], "verdict": "not scored"}
                continue
            columns = {
                model: forecasts[model][target] for model in (name,) + BENCHMARKS
            }
            block = onset._group_block(
                name, columns, outcome, target_groups, block_length=BLOCK_LENGTH,
                seed_parts=("conditional_holdout", target, name),
                test_all_days=False,
            )
            splits, pooled, cells = {}, {}, []
            for bench in BENCHMARKS:
                diff = [
                    (forecasts[bench][target][k] - outcome[k]) ** 2
                    - (forecasts[name][target][k] - outcome[k]) ** 2
                    for k in range(len(days))
                ]
                splits[bench] = split_document(
                    declaration, rows, days, diff, block_length=BLOCK_LENGTH,
                    seed=onset._seed("conditional_holdout", target, name, bench),
                )
                pooled[bench] = block[onset.GROUP_ALL]["paired"][bench]
                for kind in ("by_regime", "by_day_type"):
                    cells.extend(
                        cell for cell in splits[bench][kind].values() if cell.get("count")
                    )
            entry[name] = {
                "groups": block,
                "splits": splits,
                "verdict": cell_verdict(pooled, cells),
            }
        for model in list(PREDICTORS) + list(BENCHMARKS):
            if model in forecasts:
                entry.setdefault(model, {})["early_warning"] = early_warning(
                    forecasts[model][target], outcome, days, target, rows, targets
                )
        document["results"][target] = entry
    return document


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    args.journal.parent.mkdir(parents=True, exist_ok=True)
    document = run(args.panel, args.journal)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
