"""Tier 3 for the tier-1 passers (#471): diagnose regime calibration and score a per-regime recalibration.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing
into `docs/runs/`. The remedy, its bases and its gate are in `metadata/regime_recalibration.json`, which
this script refuses to read unless it is committed and unchanged, as it does the judge's declaration and
the risk-date declaration the bases come from (`metadata/risk_date_severity.json`, #428).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/regime_recalibration.py run --panel AUG2.csv \\
        --published PUBLISHED.csv --horizon H --output OUT/regime_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --published \\
        --output OUT/bench_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule unweighted \\
        --output OUT/judge_flat.json OUT/bench_h?.json OUT/regime_h?.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule weighted \\
        --output OUT/judge_weighted.json OUT/bench_h?.json OUT/regime_h?.json
    PYTHONPATH=src python3 scripts/regime_recalibration.py tables OUT/judge_flat.json OUT/judge_weighted.json \\
        --output OUT/tables.md

`run` fits each declared base to the risk-date label days exactly as `risk_date_severity.py run` does,
walk-forward at +5 and +10 bp on days before 2026-01-01, then recalibrates it per declared regime
(`group_calibration.regime_walk_forward`). The output holds both forms: `forecasts` carries every base raw
(the form the judge already declares) and `<base>+regime_recal`.

`tables` reads the two judge results: the diagnosis (tier 3 by regime for each base, with the direction of
the miss) and the full judge row (tiers 1, 3, 5) for each base and its recalibrated form under both rules.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import group_calibration as gc, measurement_fields, ml, probability_calibration as pc  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "regime_recalibration.json"
RISK = None


def _risk():
    """`risk_date_severity.py`, loaded by path: its fit, its inputs switch and its committed-declaration check."""

    global RISK
    if RISK is None:
        spec = importlib.util.spec_from_file_location("risk_date_severity_script", REPO / "scripts" / "risk_date_severity.py")
        RISK = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(RISK)
    return RISK


def recalibrate(report, regimes, splits, declared_taus):
    """{tau: [probability per scored day]} for one raw run, Platt per regime, non-increasing in tau."""

    scored = list(report.scored_dates)
    train_ends = [fold.train_end for fold in report.folds]
    columns = []
    for tau in declared_taus:
        forecast, _, outcomes = report.at_tau(report.taus.index(tau))
        columns.append(gc.regime_walk_forward(list(forecast), list(outcomes), scored, train_ends, regimes, splits))
    curves = pc.monotone_curves(list(zip(*columns)))
    return {tau: [curve[k] for curve in curves] for k, tau in enumerate(declared_taus)}


def run_command(args) -> int:
    risk = _risk()
    declared = risk.committed_declaration(DECLARATION)
    base_declared = risk.committed_declaration(risk.DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="regime_recalibration")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = base_declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["bases"])
    suffix = declared["remedy"]["judged_form"]
    forecasts, settings = {}, {}
    for name in names:
        spec = base_declared["candidates"][name]
        features = risk.features_at_horizon(base_declared, spec, h)
        predictor = ml.pressure_risk_date_exceedance(spec["kind"], features, splits, minimum_history=minimum)
        with risk.switched_on():
            report = rolling_exceedance_backtest(
                rows,
                predictor=predictor,
                model_name=name,
                features=features,
                registry=registry,
                decision_time=time.fromisoformat(base_declared["scoring"]["decision_time"]),
                taus=taus,
                minimum_history=minimum,
                refit_every=base_declared["scoring"]["refit_every"],
                end=last,
                horizon=h,
            )
        scored = list(report.scored_dates)
        regimes = [splits.regime(day) for day in scored]
        forecasts[name] = risk.column(report)
        recalibrated = recalibrate(report, regimes, splits, taus)
        forecasts[name + suffix] = {
            f"{tau:g}": {day.isoformat(): recalibrated[tau][k] for k, day in enumerate(scored)} for tau in taus
        }
        settings[name] = {
            "features": list(report.features),
            "model_settings": dict(report.model_settings),
            "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
            "regime_counts": {label: regimes.count(label) for label in sorted(set(regimes))},
        }
        print(json.dumps({"horizon": h, "candidate": name, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "calibration": gc.declaration(),
        "declarations": settings,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def _read(path):
    result = json.loads(Path(path).read_text())
    if result.get("mode") != "development":
        raise SystemExit(f"{path} is not a development-mode judge result; the 2026 tier is not compared (lockbox.md)")
    return result


def _interval(cell):
    if cell is None:
        return "–"
    low, high = cell.get("lower"), cell.get("upper")
    mean = cell.get("mean")
    if mean is None or low is None or high is None:
        return "–"
    return f"{mean:+.3f} [{low:+.3f}, {high:+.3f}]"


def _direction(cell):
    low, high = cell["lower"], cell["upper"]
    if low > 0:
        return "under-forecast"
    if high < 0:
        return "over-forecast"
    return "covers zero"


def diagnosis(result, names):
    """Tier 3 by regime at +5 bp for each name, each horizon: predicted vs observed with the judge's interval."""

    lines = [
        "| model | h | regime | days | events | predicted | observed | observed minus predicted [90%] | verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name in names:
        candidate = result["candidates"].get(name)
        if candidate is None:
            continue
        for h, per_tau in sorted(candidate["horizons"].items(), key=lambda kv: int(kv[0])):
            row = per_tau[next(iter(per_tau))] if "5" not in per_tau else per_tau["5"]
            for regime, cell in row["splits"]["regime"].items():
                gap = cell["realised_minus_predicted"]
                if cell["events"] > 0:
                    verdict = "fail, " + _direction(gap) if _direction(gap) != "covers zero" else "calibrated"
                else:
                    verdict = "no pressure day (reported)" + ("" if _direction(gap) == "covers zero" else ", " + _direction(gap))
                lines.append(
                    f"| {name} | {h} | {regime} | {cell['days']} | {cell['events']} | {cell['mean_predicted']:.3f} | "
                    f"{cell['realised_frequency']:.3f} | {_interval(gap)} | {verdict} |"
                )
    return "\n".join(lines)


def _tier(candidate, key):
    verdict = candidate["verdict"]
    return {
        "1": verdict["tier_1_onset_warning"],
        "3": verdict["tier_3_no_crying_wolf"],
        "5": verdict["tier_5_week_ahead"],
    }[key]


def _yn(value):
    return "pass" if value else "fail"


def judge_rows(flat, weighted, names):
    """Full judge row, tiers 1, 3, 5 and the pass, under both rules for each name."""

    lines = [
        "| model | onsets flagged (flat rule) | worst FA per onset (flat) | tier 1 / 3 / 5, flat rule | pass, flat rule "
        "| onsets flagged (weighted rule) | worst FA per onset (weighted, weighted count) | tier 1 / 3 / 5, weighted rule | pass, weighted rule |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name in names:
        cells = []
        for run, label in ((flat, "flat"), (weighted, "weighted")):
            candidate = run["candidates"].get(name)
            if candidate is None:
                cells.extend(["–"] * 4)
                continue
            near = candidate["tiers"]["onset_warning"]["lead_at_least_1"]
            onsets, flagged = near.get("onsets"), near.get("onsets_flagged")
            horizons = near.get("false_alarms_by_horizon", {})
            worst = None
            if horizons:
                key = "flat" if label == "flat" else "weighted"
                worst = max(h[key] for h in horizons.values())
            fa = "–" if worst is None else f"{worst:.2f}"
            tiers = " / ".join(_yn(_tier(candidate, k)) for k in ("1", "3", "5"))
            passes = _yn(candidate["verdict"]["passes"])
            cells.extend([f"{flagged} of {onsets}" if onsets is not None else "–", fa, tiers, passes])
        lines.append(f"| {name} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {cells[4]} | {cells[5]} | {cells[6]} | {cells[7]} |")
    return "\n".join(lines)


def tables_command(args) -> int:
    declared = json.loads(DECLARATION.read_text())
    flat, weighted = _read(args.flat), _read(args.weighted)
    if flat["scored_window"] != weighted["scored_window"]:
        raise SystemExit("the two runs scored different windows")
    suffix = declared["remedy"]["judged_form"]
    bases = declared["bases"]
    both = [n for b in bases for n in (b, b + suffix)]
    window = flat["scored_window"]
    parts = [
        f"Scored days {window['first']} to {window['last']}; +5 bp primary; h = 1 to 5; 90% stationary-bootstrap intervals.",
        "",
        "Table 1. Diagnosis: tier 3 calibration by regime, the base forms, flat rule (the rule in force). "
        "Observed minus predicted pressure-day rate; positive = the model under-forecasts.",
        "",
        diagnosis(flat, bases),
        "",
        "Table 2. The same, the recalibrated forms.",
        "",
        diagnosis(flat, [b + suffix for b in bases]),
        "",
        "Table 3. Full judge row, base and recalibrated, under the rule in force (flat) and the draft weighted rule.",
        "",
        judge_rows(flat, weighted, both),
        "",
    ]
    text = "\n".join(parts)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("run", help="fit the declared bases and recalibrate them per regime at one horizon")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--published", type=Path, required=True)
    one.add_argument("--horizon", type=int, choices=(1, 2, 3, 4, 5), required=True)
    one.add_argument("--candidate")
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=run_command)
    tables = commands.add_parser("tables", help="the diagnosis and the judge rows from the two judge results")
    tables.add_argument("flat", type=Path)
    tables.add_argument("weighted", type=Path)
    tables.add_argument("--output", type=Path)
    tables.set_defaults(func=tables_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
