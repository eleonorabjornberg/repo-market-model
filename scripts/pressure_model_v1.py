"""Pressure model v1 (#114): score every candidate against both benchmarks.

A scratch measurement, not a record: it writes JSON and a Markdown summary to
the paths it is given, and nothing into `docs/runs/`.

Every candidate and benchmark is scored by `baseline.rolling_exceedance_backtest`
on the published panel at one horizon per invocation, walk-forward with an
expanding window, refitted every 21 scored days, at +5 and +10 bp, scoring only
days before 2026-01-01 (`docs/decisions/lockbox.md`). Then `assemble` merges the
horizons, adds lead time and the October 2025 onset, and writes the tables.

    PYTHONPATH=src python3 scripts/pressure_model_v1.py horizon --panel PANEL --horizon H --output OUT/hH.json \
        [--gbm-cache OUT/hH.gbm.pickle [--gbm-only]]
    PYTHONPATH=src python3 scripts/pressure_model_v1.py assemble --panel PANEL --output OUT/pressure_v1.json \
        --markdown OUT/pressure_v1.md OUT/h1.json OUT/h2.json OUT/h3.json OUT/h4.json OUT/h5.json

The candidates:

* `distributional_gbm`: the published `exceedance_gbm_cross_conformal_funding`
  declaration (gbm, cross-conformal, its nine features), read at +5 and +10 bp.
* `direct_logistic` and `direct_gbm_classifier`: `ml.pressure_logistic_exceedance`
  and `ml.pressure_classifier_exceedance` on the latest spread, the pressure-day
  type, the settlement size, reserves as the scarcity state, the type and
  settlement terms times reserves, and the TGA's weekly change times reserves.

At horizons of 2 or more `treasury_settlement` is not public at the decision
instant under its declaration (`metadata/sources.json`, `treasury_auctions`:
one business day ahead), so every declaration drops it there. Each candidate is
also reported recalibrated out of fold (`pressure.RECALIBRATION`).
"""

from __future__ import annotations

import argparse
import copyreg
import json
import pickle
import sys
from types import MappingProxyType
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    calendar_climatology_exceedance,
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
TAUS = (5.0, 10.0)
HORIZONS = (1, 2, 3, 4, 5)
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)
#: The last day any comparison may score (`docs/decisions/lockbox.md`).
END = date(2025, 12, 31)

#: The published distributional declaration, `docs/runs/exceedance_gbm_cross_conformal_funding.json`.
GBM_FEATURES = (
    "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps",
    "tbill_13w", "tbill_4w", "tga", "treasury_settlement",
)
DIRECT_FEATURES = (
    "spread_bps", "days_to_month_end", "quarter_end", "tax_date",
    "treasury_settlement", "reserve_balances", "tga",
)
CALENDAR_FEATURES = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")
#: Scheduled one business day ahead, so not public at a longer horizon.
SETTLEMENT = "treasury_settlement"


# The reports carry read-only mappings; pickle them as the dicts they wrap, so
# the slow distributional run can be cached and the horizons run in parallel.
copyreg.pickle(MappingProxyType, lambda proxy: (MappingProxyType, (dict(proxy),)))


def _distributional(rows, h, cache):
    """The distributional candidate at horizon `h`, from `cache` when it exists."""

    from repo_model import ml

    if cache is not None and cache.exists():
        return pickle.loads(cache.read_bytes())
    gbm_features = _at_horizon(GBM_FEATURES, h)
    regressors = tuple(name for name in gbm_features if name != "spread_bps")
    report = _run(
        rows,
        "distributional_gbm",
        ml.gbm_exceedance(
            regressors, minimum_history=MINIMUM_HISTORY,
            calibration="cross_conformal", calibration_folds=5,
        ),
        gbm_features,
        h,
    )
    if cache is not None:
        cache.write_bytes(pickle.dumps(report))
    return report


def _at_horizon(features, horizon):
    return tuple(name for name in features if horizon == 1 or name != SETTLEMENT)


def _run(rows, name, predictor, features, horizon):
    return rolling_exceedance_backtest(
        rows,
        predictor=predictor,
        model_name=name,
        features=features,
        registry=json.loads(REGISTRY.read_text()),
        decision_time=DECISION,
        taus=TAUS,
        minimum_history=MINIMUM_HISTORY,
        refit_every=REFIT_EVERY,
        end=END,
        horizon=horizon,
    )


def _forecasts(report):
    return {
        f"{tau:g}": {
            when.isoformat(): curve[position]
            for when, curve in zip(report.scored_dates, report.forecast)
        }
        for position, tau in enumerate(report.taus)
    }


def horizon_command(args) -> int:
    from repo_model import ml

    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    h = args.horizon
    direct_features = _at_horizon(DIRECT_FEATURES, h)

    runs = {}
    runs["distributional_gbm"] = _distributional(rows, h, args.gbm_cache)
    if args.gbm_only:
        print(json.dumps({"horizon": h, "cached": str(args.gbm_cache)}))
        return 0
    runs["direct_logistic"] = _run(
        rows,
        "direct_logistic",
        ml.pressure_logistic_exceedance(direct_features, splits, minimum_history=MINIMUM_HISTORY),
        direct_features,
        h,
    )
    runs["direct_gbm_classifier"] = _run(
        rows,
        "direct_gbm_classifier",
        ml.pressure_classifier_exceedance(direct_features, splits, minimum_history=MINIMUM_HISTORY),
        direct_features,
        h,
    )
    benchmarks = {
        "calendar_climatology": _run(
            rows, "calendar_climatology",
            calendar_climatology_exceedance(splits, minimum_history=MINIMUM_HISTORY),
            CALENDAR_FEATURES, h,
        ),
        "persistence_logistic": _run(
            rows, "persistence_logistic",
            persistence_logistic_exceedance(minimum_history=MINIMUM_HISTORY),
            ("spread_bps",), h,
        ),
    }
    candidates = {}
    for name, report in runs.items():
        candidates[name] = report
        candidates[f"{name}+recalibrated"] = pressure.recalibrated(report)

    digest = panel_sha256(args.panel)
    card = pressure.scorecard(
        candidates, benchmarks, rows=rows, declaration=splits, panel_sha256=digest
    )
    first = runs["distributional_gbm"]
    document = {
        "horizon": h,
        "panel_sha256": digest,
        "scored_window": {
            "first": first.scored_dates[0].isoformat(),
            "last": first.scored_dates[-1].isoformat(),
            "days": len(first.scored_dates),
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
                "model_settings": dict(report.model_settings),
                "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
            }
            for name, report in {**runs, **benchmarks}.items()
        },
        "recalibration": pressure.RECALIBRATION,
        "splits": splits.document(),
        "scorecard": card,
        "forecasts": {name: _forecasts(report) for name, report in {**candidates, **benchmarks}.items()},
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output), **document["scored_window"]}))
    return 0


# -- assembly -----------------------------------------------------------------


def _fmt(value, places=4):
    return "–" if value is None else f"{value:.{places}f}"


def _interval(paired):
    interval = paired["interval"]
    return f"{paired['mean']:+.4f} [{interval['lower']:+.4f}, {interval['upper']:+.4f}]"


def _split_cell(entry):
    if "mean" not in entry:
        return "– (n=0)"
    interval = entry.get("interval")
    if not interval:
        return f"{entry['mean']:+.4f} (n={entry['count']}, no interval)"
    return f"{entry['mean']:+.4f} [{interval['lower']:+.4f}, {interval['upper']:+.4f}]"


def assemble_command(args) -> int:
    rows = load_daily_panel(args.panel)
    parts = sorted(
        (json.loads(Path(path).read_text()) for path in args.inputs), key=lambda d: d["horizon"]
    )
    horizons = [part["horizon"] for part in parts]
    names = list(parts[0]["scorecard"]["candidates"])
    benchmark_names = list(parts[0]["scorecard"]["benchmarks"])
    common = set.intersection(
        *(set(part["forecasts"][benchmark_names[0]]["5"]) for part in parts)
    )
    common_dates = sorted(date.fromisoformat(when) for when in common)

    lead = {}
    october = {}
    for tau in TAUS:
        key = f"{tau:g}"
        onset_days = pressure.onsets(rows, tau, common_dates)
        lead[key] = {"onsets": [when.isoformat() for when in onset_days], "by_model": {}}
        october[key] = {}
        for name in names + benchmark_names:
            per_h = {
                part["horizon"]: {
                    date.fromisoformat(when): p
                    for when, p in part["forecasts"][name][key].items()
                }
                for part in parts
            }
            lead[key]["by_model"][name] = [
                pressure.lead_times(per_h, onset_days, level) for level in pressure.ALARM_LEVELS
            ]
            october[key][name] = {
                when.isoformat(): {str(h): per_h[h].get(when) for h in horizons}
                for when in onset_days
                if when.year == 2025 and when.month == 10
            }

    document = {
        "directive": "#114",
        "status": "scratch measurement; not a record, nothing published moves",
        "horizons": {str(part["horizon"]): {k: v for k, v in part.items() if k != "forecasts"} for part in parts},
        "lead_time": lead,
        "october_2025_onset": october,
        "onset_definition": (
            f"an event day (spread strictly above the threshold) with no event on the "
            f"{pressure.ONSET_QUIET_DAYS} panel days before it, among days scored at every horizon"
        ),
        "lead_time_definition": (
            "the longest horizon whose forecast of the onset day reached the alarm level; 0 when none did"
        ),
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(parts, names, benchmark_names, lead, october), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "markdown": str(args.markdown)}))
    return 0


def _markdown(parts, names, benchmark_names, lead, october) -> str:
    out = []
    w = parts[0]["scored_window"]
    out.append(f"Panel `{parts[0]['panel_sha256'][:12]}…`. Scored window per horizon below; "
               f"no scored day on or after 2026-01-01.\n")
    out.append("| Horizon | First scored | Last scored | Days |\n|---|---|---|---|")
    for part in parts:
        sw = part["scored_window"]
        out.append(f"| {part['horizon']} | {sw['first']} | {sw['last']} | {sw['days']} |")
    out.append("")
    for tau in TAUS:
        key = f"{tau:g}"
        out.append(f"### +{key} bp: Brier, decomposition, precision-recall, paired differences\n")
        out.append(
            "Paired difference = Brier(benchmark) − Brier(candidate), mean over scored days, "
            "90% stationary-bootstrap interval; positive means the candidate had the lower Brier.\n"
        )
        for part in parts:
            card = part["scorecard"]
            out.append(f"**Horizon {part['horizon']}** (scored {part['scored_window']['first']} to "
                       f"{part['scored_window']['last']}, {part['scored_window']['days']} days)\n")
            out.append("| Model | Brier | Reliability | Resolution | Uncertainty | AP | Base rate | "
                       "vs calendar climatology | vs persistence-logistic |")
            out.append("|---|---|---|---|---|---|---|---|---|")
            for name in benchmark_names:
                m = card["benchmarks"][name][key]
                d = m.get("decomposition", {})
                out.append(f"| {name} (benchmark) | {_fmt(m['brier'])} | {_fmt(d.get('reliability'))} | "
                           f"{_fmt(d.get('resolution'))} | {_fmt(d.get('uncertainty'))} | "
                           f"{_fmt(m.get('average_precision'), 3)} | {_fmt(m['base_rate'], 3)} | | |")
            for name in names:
                entry = card["candidates"][name]
                m = entry["metrics"][key]
                d = m.get("decomposition", {})
                cells = [
                    _interval(entry["paired"][b]["by_tau"][key]["paired_brier_difference"])
                    for b in benchmark_names
                ]
                out.append(f"| {name} | {_fmt(m['brier'])} | {_fmt(d.get('reliability'))} | "
                           f"{_fmt(d.get('resolution'))} | {_fmt(d.get('uncertainty'))} | "
                           f"{_fmt(m.get('average_precision'), 3)} | {_fmt(m['base_rate'], 3)} | "
                           + " | ".join(cells) + " |")
            out.append("")
    for tau in TAUS:
        key = f"{tau:g}"
        for bench in benchmark_names:
            out.append(f"### +{key} bp: paired difference against {bench}, split by regime and pressure-day type\n")
            for part in parts:
                card = part["scorecard"]
                first = card["candidates"][names[0]]["paired"][bench]["by_tau"][key]["paired_brier_difference"]["splits"]
                regimes = list(first["by_regime"])
                types = list(first["by_day_type"])
                out.append(f"**Horizon {part['horizon']}**\n")
                out.append("| Model | " + " | ".join(regimes + types) + " |")
                out.append("|---|" + "---|" * (len(regimes) + len(types)))
                for name in names:
                    s = card["candidates"][name]["paired"][bench]["by_tau"][key]["paired_brier_difference"]["splits"]
                    cells = [_split_cell(s["by_regime"][r]) for r in regimes] + [
                        _split_cell(s["by_day_type"][t]) for t in types
                    ]
                    out.append(f"| {name} | " + " | ".join(cells) + " |")
                out.append("")
    out.append("### Lead time to pressure onset\n")
    out.append("Lead time is the longest horizon (1–5 business days) whose forecast of the onset day "
               "reached the alarm level; 0 is a miss.\n")
    for tau in TAUS:
        key = f"{tau:g}"
        out.append(f"**+{key} bp**: {len(lead[key]['onsets'])} onsets\n")
        out.append("| Model | " + " | ".join(
            f"flagged at {lv:g} | mean lead at {lv:g}" for lv in pressure.ALARM_LEVELS) + " |")
        out.append("|---|" + "---|---|" * len(pressure.ALARM_LEVELS))
        for name, results in lead[key]["by_model"].items():
            cells = []
            for result in results:
                cells += [f"{result['flagged']}/{result['onsets']}", _fmt(result["mean_lead_days"], 2)]
            out.append(f"| {name} | " + " | ".join(cells) + " |")
        out.append("")
    out.append("### The October 2025 onset\n")
    for tau in TAUS:
        key = f"{tau:g}"
        days = sorted({when for model in october[key].values() for when in model})
        if not days:
            out.append(f"**+{key} bp**: no onset in October 2025 under the onset definition.\n")
            continue
        for when in days:
            out.append(f"**+{key} bp, onset {when}**: probability forecast of that day at each horizon\n")
            out.append("| Model | h=1 | h=2 | h=3 | h=4 | h=5 |\n|---|---|---|---|---|---|")
            for name, by_day in october[key].items():
                values = by_day.get(when, {})
                out.append(f"| {name} | " + " | ".join(_fmt(values.get(str(h)), 3) for h in HORIZONS) + " |")
            out.append("")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("horizon", help="score every candidate and benchmark at one horizon")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.add_argument(
        "--gbm-cache", type=Path, default=None,
        help="pickle of the distributional run: read if present, else written",
    )
    one.add_argument(
        "--gbm-only", action="store_true",
        help="run (and cache) the distributional candidate only, then stop",
    )
    one.set_defaults(func=horizon_command)
    merge = sub.add_parser("assemble", help="merge the horizons; lead time; tables")
    merge.add_argument("--panel", type=Path, required=True)
    merge.add_argument("--output", type=Path, required=True)
    merge.add_argument("--markdown", type=Path, required=True)
    merge.add_argument("inputs", nargs="+")
    merge.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
