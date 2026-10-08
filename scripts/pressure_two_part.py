"""The two-part pressure model (#382, track S of #374): P(spike) times a conditional size law.

A scratch measurement, not a record: it writes JSON and a Markdown summary to the paths it is
given, and nothing into `docs/runs/`. Nothing published moves.

The model is `ml.pressure_two_part_exceedance`: a classifier of `spread > +5 bp` (the spike),
times the conditional law of the spike's whole-bp excess (geometric, log-linear mean on the same
design; `ml.TWO_PART_SETTINGS`). Its exceedance curve at +5, +10, +20 and +50 bp is therefore a
full tail distribution above +5 bp, non-increasing in the threshold by construction. The two
candidates, declared in `metadata/pressure_judge.json` before anything was scored, differ in the
classifier: `two_part_logistic` and `two_part_gbm`.

Scored as pressure model v1 was (#114): `baseline.rolling_exceedance_backtest` on the published
panel, one horizon per invocation, walk-forward with an expanding window, refitted every 21
scored days, scoring only days before 2026-01-01 (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/pressure_two_part.py horizon --panel PANEL --horizon H \\
        --output OUT/two_part_hH.json
    PYTHONPATH=src python3 scripts/pressure_two_part.py assemble --output OUT/two_part.json \\
        --markdown OUT/two_part.md OUT/two_part_h1.json ... OUT/two_part_h5.json

`horizon` writes the candidates' +5 and +10 bp probabilities in the shape
`scripts/pressure_judge.py judge` reads (its `forecasts` block), which is where the event bar is
judged, by scarcity state, regime, pressure-day type and on the knowledge holdouts. It also
writes, per scored day, the **tail CRPS**: the threshold-weighted CRPS over the declared tail
family {5, 10, 20, 50} bp (`baseline.twcrps_weights`; the distribution above +5 bp, the part the
two-part model is a model of), for each candidate, the published v1 (the recalibrated
distributional gbm, as `scripts/pressure_judge.py` builds it) and the two benchmarks.
`assemble` pairs the candidates against each on that loss, with the stationary-bootstrap interval,
beside the event bar. The tail CRPS is a report, not the bar.

Pressure model v2 (#244) is a quantile-vector model at h = 1 whose record
(`docs/runs/pressure_model_v2_distribution_h1.json`) keeps whole-distribution CRPS, not exceedance
probabilities at the tail thresholds, so it is not scored here: the two losses are on different
scales and the record cannot be re-expressed on this one without re-running v2.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import metrics  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    calendar_climatology_exceedance,
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
    twcrps_weights,
)
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
#: The declared tail family: +5 and +10 bp are the event thresholds the judge reads; +20 and +50 bp
#: carry no pooled skill claim (`docs/decisions/pressure-probability.md`) and enter only the tail CRPS.
TAUS = (5.0, 10.0, 20.0, 50.0)
EVENT_TAUS = (5.0, 10.0)
HORIZONS = (1, 2, 3, 4, 5)
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)
END = date(2025, 12, 31)
FEATURES = (
    "spread_bps", "days_to_month_end", "quarter_end", "tax_date",
    "treasury_settlement_coupons", "reserve_balances",
)
CALENDAR_FEATURES = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")
#: Scheduled one business day ahead, so not public at a longer horizon (as in v1 and #137).
SCHEDULED_ONE_DAY_AHEAD = ("treasury_settlement", "treasury_settlement_coupons")
CANDIDATES = ("two_part_logistic", "two_part_gbm")
BOOTSTRAP = {"block_length": 10, "seed": 382, "replications": 2000, "level": 0.90}


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _at_horizon(features, horizon):
    return tuple(n for n in features if horizon == 1 or n not in SCHEDULED_ONE_DAY_AHEAD)


def _run(rows, registry, name, predictor, features, horizon):
    return rolling_exceedance_backtest(
        rows,
        predictor=predictor,
        model_name=name,
        features=features,
        registry=registry,
        decision_time=DECISION,
        taus=TAUS,
        minimum_history=MINIMUM_HISTORY,
        refit_every=REFIT_EVERY,
        end=END,
        horizon=horizon,
    )


def _published(rows, splits, registry, horizon):
    """Pressure model v1 at the tail family: `scripts/pressure_judge.py`'s published run, four taus.

    The same run (the distributional gbm, nested-fold PID, recalibrated out of fold), kept as a
    report so its whole curve is scored.
    """

    from repo_model import ml, pressure
    from repo_model.recalibration import NestedFoldPid

    model = _load_script("pressure_model_v1")
    features = model._at_horizon(model.GBM_FEATURES, horizon)
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=REFIT_EVERY))
        return built[-1]

    raw = rolling_exceedance_backtest(
        rows,
        predictor=ml.gbm_exceedance(
            tuple(n for n in features if n != "spread_bps"), minimum_history=MINIMUM_HISTORY
        ),
        model_name="distributional_gbm",
        features=features,
        registry=registry,
        decision_time=DECISION,
        taus=TAUS,
        minimum_history=MINIMUM_HISTORY,
        refit_every=REFIT_EVERY,
        end=END,
        horizon=horizon,
        online_calibration=online,
    )
    return pressure.recalibrated(raw)


def _tail_losses(report):
    """{day: threshold-weighted CRPS over TAUS} for one report."""

    weights = twcrps_weights(TAUS)
    return {
        when.isoformat(): metrics.threshold_weighted_crps(TAUS, curve, value, weights)
        for when, curve, value in zip(report.scored_dates, report.forecast, report.realized_bps)
    }


def horizon_command(args) -> int:
    from repo_model import ml, pressure

    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    h = args.horizon
    features = _at_horizon(FEATURES, h)

    reports = {
        "two_part_logistic": _run(
            rows, registry, "two_part_logistic",
            ml.pressure_two_part_exceedance(features, splits, minimum_history=MINIMUM_HISTORY),
            features, h,
        ),
        "two_part_gbm": _run(
            rows, registry, "two_part_gbm",
            ml.pressure_two_part_exceedance(
                features, splits, minimum_history=MINIMUM_HISTORY, classifier="gbm_classifier"
            ),
            features, h,
        ),
    }
    comparators = {
        "calendar_climatology": _run(
            rows, registry, "calendar_climatology",
            calendar_climatology_exceedance(splits, minimum_history=MINIMUM_HISTORY),
            CALENDAR_FEATURES, h,
        ),
        "persistence_logistic": _run(
            rows, registry, "persistence_logistic",
            persistence_logistic_exceedance(minimum_history=MINIMUM_HISTORY),
            ("spread_bps",), h,
        ),
        "published_v1": _published(rows, splits, registry, h),
    }
    # the event shape: candidates only, at the event thresholds
    forecasts = {
        name: {
            f"{tau:g}": {
                when.isoformat(): curve[position]
                for when, curve in zip(report.scored_dates, report.forecast)
            }
            for position, tau in enumerate(report.taus)
            if tau in EVENT_TAUS
        }
        for name, report in reports.items()
    }
    everyone = {**reports, **comparators}
    days = {name: [d.isoformat() for d in report.scored_dates] for name, report in everyone.items()}
    if len({tuple(v) for v in days.values()}) != 1:
        raise SystemExit("the candidates and comparators are not on one grid")
    digest = panel_sha256(args.panel)
    document = {
        "horizon": h,
        "panel_sha256": digest,
        "scored_window": {
            "first": days["two_part_gbm"][0],
            "last": days["two_part_gbm"][-1],
            "days": len(days["two_part_gbm"]),
        },
        "fold_grid": {
            "walk_forward": "expanding window",
            "refit_every": REFIT_EVERY,
            "minimum_history": MINIMUM_HISTORY,
            "decision_time": DECISION.isoformat(timespec="minutes"),
            "end": END.isoformat(),
        },
        "declarations": {
            name: {
                "features": list(report.features),
                "model_settings": json.loads(json.dumps(dict(report.model_settings), default=str)),
            }
            for name, report in reports.items()
        },
        "tail_family_bp": list(TAUS),
        "tail_crps": {name: _tail_losses(report) for name, report in everyone.items()},
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output), **document["scored_window"]}))
    return 0


# -- assembly -----------------------------------------------------------------


def _paired(candidate, comparator):
    """mean(comparator loss - candidate loss) over common days, with its stationary-bootstrap interval."""

    common = sorted(set(candidate) & set(comparator))
    diff = [comparator[d] - candidate[d] for d in common]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: statistics.fmean(diff[i] for i in idx),
        len(diff),
        block_length=BOOTSTRAP["block_length"],
        seed=BOOTSTRAP["seed"],
        replications=BOOTSTRAP["replications"],
        level=BOOTSTRAP["level"],
    )
    return {
        "days": len(diff),
        "mean": statistics.fmean(diff),
        "lower": low,
        "upper": high,
        "candidate_better": low > 0.0,
        "comparator_better": high < 0.0,
    }


def assemble_command(args) -> int:
    parts = sorted((json.loads(Path(p).read_text()) for p in args.inputs), key=lambda d: d["horizon"])
    table = {}
    for part in parts:
        losses = part["tail_crps"]
        table[str(part["horizon"])] = {
            "days": part["scored_window"]["days"],
            "mean_tail_crps": {name: statistics.fmean(v.values()) for name, v in losses.items()},
            "paired_vs": {
                name: {
                    other: _paired(losses[name], losses[other])
                    for other in losses
                    if other not in CANDIDATES
                }
                for name in CANDIDATES
            },
        }
    document = {
        "directive": "#382",
        "status": "scratch measurement; not a record, nothing published moves",
        "tail_family_bp": parts[0]["tail_family_bp"],
        "loss": "threshold-weighted CRPS over the tail family, weights tau/max(tau) (baseline.twcrps_weights)",
        "bootstrap": BOOTSTRAP,
        "panel_sha256": parts[0]["panel_sha256"],
        "by_horizon": table,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "markdown": str(args.markdown)}))
    return 0


def _markdown(document) -> str:
    out = [
        f"Panel `{document['panel_sha256'][:12]}…`. Loss: {document['loss']}, over "
        f"{document['tail_family_bp']} bp. Paired difference = loss(comparator) − loss(candidate); "
        "positive means the candidate is better; 90% stationary-bootstrap interval.\n"
    ]
    for h, entry in document["by_horizon"].items():
        out.append(f"**Horizon {h}** ({entry['days']} days). Mean tail CRPS:\n")
        out.append("| Model | Mean tail CRPS |\n|---|---|")
        for name, value in entry["mean_tail_crps"].items():
            out.append(f"| {name} | {value:.4f} |")
        out.append("")
        out.append("| Candidate | Comparator | Paired difference [90% interval] | Reading |\n|---|---|---|---|")
        for name, versus in entry["paired_vs"].items():
            for other, cell in versus.items():
                reading = (
                    "candidate better" if cell["candidate_better"]
                    else "comparator better" if cell["comparator_better"] else "interval contains zero"
                )
                out.append(
                    f"| {name} | {other} | {cell['mean']:+.4f} [{cell['lower']:+.4f}, {cell['upper']:+.4f}] | {reading} |"
                )
        out.append("")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("horizon", help="score the candidates and comparators at one horizon")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=horizon_command)
    merge = sub.add_parser("assemble", help="pair the tail CRPS across horizons")
    merge.add_argument("--output", type=Path, required=True)
    merge.add_argument("--markdown", type=Path, required=True)
    merge.add_argument("inputs", nargs="+")
    merge.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
