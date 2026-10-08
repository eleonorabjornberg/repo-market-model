"""The extreme-value tail model (#383, track E of #374): forecasts for the judge, and the tail's diagnostics.

A scratch measurement, not a record: it writes JSON and a Markdown summary to
the paths it is given, and nothing into `docs/runs/`. The model, its threshold,
its features and its cut-offs are in `metadata/pressure_tail.json` (and the
candidate's entry in `metadata/pressure_judge.json`), which this script refuses
to read unless both are committed and unchanged.

    PYTHONPATH=src python3 scripts/pressure_tail.py forecasts --panel PANEL --horizon H --output OUT/tail_hH.json
    PYTHONPATH=src python3 scripts/pressure_tail.py diagnostics --panel PANEL --output OUT/tail_diag.json \
        --markdown OUT/tail_diag.md OUT/tail_h1.json ... OUT/tail_h5.json

`forecasts` writes the walk-forward per-day probabilities P(SOFR - IORB > tau) at
+5 and +10 bp for one horizon, in the shape the judge reads
(`pressure_judge.py judge ... OUT/tail_hH.json`), with, beside them, one entry
per fold of its tail fit (the shape, the scale's coefficients, the number of
excesses, the fit's mode) and, per scored day, the body probability and the
fitted scale. Days are before 2026-01-01 (`docs/decisions/lockbox.md`, #374).

`diagnostics` reads those files and reports, for the tail:

* the fits over the folds: how many were a generalised Pareto, an exponential
  (too few excesses) or empty, the shape's path, and the scale's coefficients
  (on standardised columns: reserves, quarter end, month end, tax date);
* the out-of-sample tail calibration: for each tau, the number of scored days
  above tau and the expected number, the sum of the forecast probabilities, by
  horizon and by regime;
* the out-of-sample probability integral transform of the excesses: for each
  scored day above u, the mid-point PIT of its spread under the forecast's own
  fitted tail, its decile counts and its Kolmogorov distance from uniform.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "pressure_tail.json"
CALIBRATION_TAUS = (3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0)


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_declaration(path=DECLARATION):
    raw = Path(path).read_bytes()
    document = json.loads(raw.decode("utf-8"))
    for key in ("candidate", "scoring", "thresholds_bp", "horizons", "features", "model", "cutoffs"):
        if key not in document:
            raise ValueError(f"{path} declares no {key!r}")
    threshold = float(document["model"]["threshold_bp"])
    taus = tuple(float(t) for t in document["thresholds_bp"])
    if not all(tau > threshold for tau in taus):
        raise ValueError(f"{path}: every threshold must lie above u = {threshold:g} bp")
    hour, minute = (int(part) for part in str(document["scoring"]["decision_time"]).split(":"))
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "candidate": document["candidate"],
        "last_day": date.fromisoformat(document["scoring"]["last_day"]),
        "minimum_history": int(document["scoring"]["minimum_history"]),
        "refit_every": int(document["scoring"]["refit_every"]),
        "decision_time": time(hour, minute),
        "thresholds": taus,
        "horizons": tuple(int(h) for h in document["horizons"]),
        "features": tuple(document["features"]),
        "threshold_bp": threshold,
    }


# -- forecasts ----------------------------------------------------------------


def forecasts_command(args) -> int:
    judge = _judge_script()
    declaration = load_declaration()
    commits = {
        "pressure_tail": judge.require_committed_declaration(DECLARATION),
        "pressure_judge": judge.require_committed_declaration(pj.DEFAULT_DECLARATION),
    }
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    record = []
    report = rolling_exceedance_backtest(
        rows,
        predictor=ml.pressure_tail_exceedance(
            declaration["features"],
            splits,
            minimum_history=declaration["minimum_history"],
            threshold_bp=declaration["threshold_bp"],
            record=record,
        ),
        model_name=declaration["candidate"],
        features=declaration["features"],
        registry=registry,
        decision_time=declaration["decision_time"],
        taus=declaration["thresholds"],
        minimum_history=declaration["minimum_history"],
        refit_every=declaration["refit_every"],
        end=declaration["last_day"],
        horizon=args.horizon,
    )
    served = [item for fold in record for item in fold["served"]]
    if len(served) != len(report.scored_dates):
        raise SystemExit("the tail's per-day record does not line up with the scored days")
    forecast = pj.report_forecast(declaration["candidate"], report)
    folds = [{k: v for k, v in fold.items() if k != "served"} for fold in record]
    sizes = [len(fold["served"]) for fold in record]
    document = {
        "horizon": args.horizon,
        "panel_sha256": panel_sha256(args.panel),
        "declaration_commits": commits,
        "declaration_sha256": declaration["sha256"],
        "scored_window": {
            "first": report.scored_dates[0].isoformat(),
            "last": report.scored_dates[-1].isoformat(),
            "days": len(report.scored_dates),
        },
        "model_settings": dict(report.model_settings),
        "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        "forecasts": {
            forecast.name: {
                f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, column)}
                for tau, column in forecast.probabilities.items()
            }
        },
        "tail": {
            "threshold_bp": declaration["threshold_bp"],
            "folds": [dict(fold, scored_days=n) for fold, n in zip(folds, sizes)],
            "days": {
                day.isoformat(): {"anchor": item["anchor"], "body": item["body"], "sigma": item["sigma"]}
                for day, item in zip(report.scored_dates, served)
            },
        },
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "output": str(args.output), **document["scored_window"]}))
    return 0


# -- diagnostics --------------------------------------------------------------


def _log_survival(z, sigma, shape):
    if shape < 1e-8:
        return -z / sigma
    return -math.log1p(shape * z / sigma) / shape


def mid_pit(spread, u, sigma, shape):
    """The mid-point PIT of a basis-point spread above `u` under the fitted tail.

    The excess is the bin `[k - u - 1, k - u)`; its conditional CDF at the bin's
    two ends is `1 - S`, and the mid-point PIT is their average.
    """

    k = round(spread - u)
    low = math.exp(_log_survival(k - 1.0, sigma, shape))
    high = math.exp(_log_survival(float(k), sigma, shape))
    return 1.0 - 0.5 * (low + high)


def kolmogorov_distance(values):
    ordered = sorted(values)
    n = len(ordered)
    return max(
        max((i + 1) / n - v, v - i / n) for i, v in enumerate(ordered)
    ) if n else None


def diagnostics_command(args) -> int:
    declaration = load_declaration()
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(SPLITS)
    spread = {row.date.isoformat(): float(row.spread_bps) for row in rows}
    u = declaration["threshold_bp"]
    out = {"declaration_sha256": declaration["sha256"], "threshold_bp": u, "horizons": {}}
    lines = [
        f"# Tail diagnostics: {declaration['candidate']} (u = {u:g} bp)",
        "",
        f"Declaration `metadata/pressure_tail.json` sha256 `{declaration['sha256'][:12]}…`; panel `{panel_sha256(args.panel)[:12]}…`.",
        "",
    ]
    for path in args.forecasts:
        document = json.loads(Path(path).read_text())
        horizon = int(document["horizon"])
        tail = document["tail"]
        folds = tail["folds"]
        days = tail["days"]
        # the folds' scored days, in order, from the per-day record
        names = sorted(days)
        index = 0
        shape_of = {}
        for fold in folds:
            for day in names[index : index + fold["scored_days"]]:
                shape_of[day] = (fold["shape"], fold["mode"])
            index += fold["scored_days"]
        modes = {}
        for fold in folds:
            modes[fold["mode"]] = modes.get(fold["mode"], 0) + 1
        gpd = [fold for fold in folds if fold["mode"] == "gpd"]
        entry = {
            "folds": len(folds),
            "modes": modes,
            "shape": {
                "first": gpd[0]["shape"] if gpd else None,
                "last": gpd[-1]["shape"] if gpd else None,
                "min": min((f["shape"] for f in gpd), default=None),
                "max": max((f["shape"] for f in gpd), default=None),
                "mean": sum(f["shape"] for f in gpd) / len(gpd) if gpd else None,
            },
            "last_fit": {key: folds[-1][key] for key in ("mode", "excesses", "shape", "intercept", "coefficients", "train_end")},
        }
        calibration = {}
        for tau in CALIBRATION_TAUS:
            by_regime = {}
            for day, scale in days.items():
                value, mode = shape_of[day]
                z = tau - u
                if mode == "none":
                    survival = 0.0
                else:
                    survival = math.exp(_log_survival(z, scale["sigma"], value))
                p = scale["body"] * survival
                observed = 1 if spread[day] > tau else 0
                regime = splits.regime(date.fromisoformat(day))
                cell = by_regime.setdefault(regime, [0, 0.0, 0])
                cell[0] += observed
                cell[1] += p
                cell[2] += 1
            total = [sum(c[i] for c in by_regime.values()) for i in range(3)]
            calibration[f"{tau:g}"] = {
                "observed": total[0],
                "expected": total[1],
                "days": total[2],
                "by_regime": {k: {"observed": v[0], "expected": v[1], "days": v[2]} for k, v in sorted(by_regime.items())},
            }
        pits = []
        for day, scale in days.items():
            if spread[day] > u and shape_of[day][1] != "none":
                pits.append(mid_pit(spread[day], u, scale["sigma"], shape_of[day][0]))
        deciles = [0] * 10
        for value in pits:
            deciles[min(9, int(value * 10))] += 1
        entry["calibration"] = calibration
        entry["excess_pit"] = {
            "excesses": len(pits),
            "mean": sum(pits) / len(pits) if pits else None,
            "kolmogorov_distance": kolmogorov_distance(pits),
            "kolmogorov_5pct_critical": 1.36 / math.sqrt(len(pits)) if pits else None,
            "deciles": deciles,
        }
        out["horizons"][str(horizon)] = entry
        lines += [f"## Horizon {horizon}", ""]
        lines.append(
            f"Folds {len(folds)}: " + ", ".join(f"{n} {m}" for m, n in sorted(modes.items()))
            + (f"; shape over the generalised Pareto folds {entry['shape']['min']:.3f} to {entry['shape']['max']:.3f} "
               f"(mean {entry['shape']['mean']:.3f}, last {entry['shape']['last']:.3f})." if gpd else ".")
        )
        last = entry["last_fit"]
        lines.append(
            f"Last fit (training to {last['train_end']}, {last['excesses']} excesses, {last['mode']}): shape {last['shape']:.3f}, "
            f"log scale intercept {last['intercept']:.3f}, standardised coefficients "
            + ", ".join(f"{k} {v:+.3f}" for k, v in last["coefficients"].items()) + "."
        )
        lines += ["", "| tau (bp) | days above | expected | ratio |", "|---|---|---|---|"]
        for tau in CALIBRATION_TAUS:
            cell = calibration[f"{tau:g}"]
            ratio = cell["observed"] / cell["expected"] if cell["expected"] else float("nan")
            lines.append(f"| {tau:g} | {cell['observed']} | {cell['expected']:.1f} | {ratio:.2f} |")
        pit = entry["excess_pit"]
        if pit["excesses"]:
            lines += [
                "",
                f"Mid-point PIT of the {pit['excesses']} scored days above u: mean {pit['mean']:.3f} (uniform 0.5), "
                f"Kolmogorov distance {pit['kolmogorov_distance']:.3f} (5% critical {pit['kolmogorov_5pct_critical']:.3f}); "
                f"deciles {pit['deciles']}.",
            ]
        lines.append("")
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "horizons": list(out["horizons"])}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("forecasts")
    f.add_argument("--panel", type=Path, required=True)
    f.add_argument("--horizon", type=int, required=True)
    f.add_argument("--output", type=Path, required=True)
    f.set_defaults(run=forecasts_command)
    d = sub.add_parser("diagnostics")
    d.add_argument("--panel", type=Path, required=True)
    d.add_argument("--output", type=Path, required=True)
    d.add_argument("--markdown", type=Path)
    d.add_argument("forecasts", nargs="+", type=Path)
    d.set_defaults(run=diagnostics_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
