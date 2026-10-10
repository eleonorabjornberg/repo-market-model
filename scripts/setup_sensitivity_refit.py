#!/usr/bin/env python3
"""The 2018-19 down-weighting test, with the models refitted (#518, of #524): a reported-only measurement.

`setup_sensitivity.py` (#482) down-weighted 2018-19 in the choice of the flag cut-off only. This script refits the
five tier-1 risk-date models with the period down-weighted (`ml.pressure_risk_date_exceedance(train_weight=...)`) and
reads tier 1 under four readings (`metadata/setup_sensitivity_refit.json`, committed before any refit): the model as
declared or refitted, the cut-off as declared or chosen with the same weights.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/risk_date_severity.py run --panel AUG2.csv --published PUB.csv \\
        --horizon H --output OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon H --output OUT/bench_hH.json
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/setup_sensitivity_refit.py refit --panel AUG2.csv --published PUB.csv \\
        --bench OUT/bench_hH.json --horizon H --output OUT/dw_hH.json
    PYTHONPATH=src python3 scripts/setup_sensitivity_refit.py report --panel PUB.csv --bench 'OUT/bench_h{h}.json' \\
        --parent 'OUT/risk_h{h}.json' --refit 'OUT/dw_h{h}.json' --rule unweighted --output OUT/refit.json --markdown OUT/refit.md

Scored days are before 2026-01-01 (`docs/decisions/lockbox.md`); no 2026 day is read and nothing is written into `docs/runs/`.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import subprocess
import sys
from dataclasses import replace
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model import setup_sensitivity as ss  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "setup_sensitivity_refit.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SUFFIX = "+dw"
READINGS = ("declared", "cutoff_only", "refit", "refit_and_cutoff")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed(path: Path) -> dict:
    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def period_share(declared: dict, scored_days) -> tuple:
    period = declared["period"]
    first, last = date.fromisoformat(period["first"]), date.fromisoformat(period["last"])
    return first, last, sum(1 for d in scored_days if first <= d <= last) / len(scored_days)


def refit_command(args) -> int:
    declared = committed(DECLARATION)
    risk = _load("risk_date_severity")
    base = risk.committed_declaration(risk.DECLARATION)
    h = args.horizon
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="setup_sensitivity_refit")
    bench = json.loads(args.bench.read_text())
    reference = next(f for f in pj.forecasts_from_horizon_document(bench) if f.name == "calendar_climatology")
    first, period_last, share = period_share(declared, reference.dates)
    weigh = ss.period_weights(first, period_last, share)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    from repo_model import measurement_fields

    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in base["thresholds_bp"])
    minimum = base["scoring"]["minimum_history"]
    forecasts, settings = {}, {}
    for name in declared["rows"]["chosen"]:
        spec = base["candidates"][name]
        features = risk.features_at_horizon(base, spec, h)
        predictor = ml.pressure_risk_date_exceedance(spec["kind"], features, splits, minimum_history=minimum, train_weight=weigh)
        with risk.switched_on():
            report = rolling_exceedance_backtest(
                rows, predictor=predictor, model_name=name + SUFFIX, features=features, registry=registry,
                decision_time=time.fromisoformat(base["scoring"]["decision_time"]), taus=taus, minimum_history=minimum,
                refit_every=base["scoring"]["refit_every"], end=last, horizon=h,
            )
        forecasts[name + SUFFIX] = risk.column(report)
        settings[name + SUFFIX] = {"features": list(report.features), "model_settings": dict(report.model_settings)}
        print(json.dumps({"horizon": h, "candidate": name + SUFFIX, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "period_share": share,
        "declarations": settings,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output), "share": share}))
    return 0


def weights_by_window(declaration, dates, calendar, first, last, share) -> dict:
    """The weight on a period day in each cut-off or refit window, by the calendar year in which the window ends."""

    out = {}
    step = declaration.cutoff_refit_every
    position = {d: k for k, d in enumerate(calendar)}
    for start in range(step, len(dates), step):
        block_first = dates[start]
        end = calendar[position[block_first] - 2]  # the horizon-1 training end: one decision before the block
        window = [d for d in dates[:start] if d <= end]
        weights = ss.period_weights(first, last, share)(window)
        inside = [w for w, d in zip(weights, window) if first <= d <= last]
        if inside:
            out.setdefault(str(end.year), []).append(inside[0])
    return {year: {"refits": len(v), "min": min(v), "max": max(v)} for year, v in sorted(out.items())}


def report_command(args) -> int:
    declared = committed(DECLARATION)
    judge_script = _load("pressure_judge")
    sens = _load("setup_sensitivity")
    declaration = pj.load_declaration()
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    declaration = replace(declaration, weighted_miss=pj.load_weighted_miss(applied=args.rule == "weighted"))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    horizons = declaration.horizons
    names = declared["rows"]["chosen"]
    parents, refits, digests = {}, {}, {}
    forecasts = {h: [] for h in horizons}
    for h in horizons:
        bench = json.loads(Path(args.bench.format(h=h)).read_text())
        digests[f"bench_h{h}"] = bench["panel_sha256"]
        found = pj.forecasts_from_horizon_document(bench)
        reference = next(f for f in found if f.name == "calendar_climatology")
        forecasts[h].extend(f for f in found if f.name in (declaration.climatology, declaration.persistence))
        for template, wanted, store in ((args.parent, names, parents), (args.refit, [n + SUFFIX for n in names], refits)):
            document = json.loads(Path(template.format(h=h)).read_text())
            digests[Path(template).name.format(h=h)] = document["panel_sha256"]
            for forecast in pj.forecasts_from_horizon_document(document):
                if forecast.name in wanted:
                    if forecast.dates != reference.dates:
                        raise SystemExit(f"{forecast.name} h = {h}: its days are not the benchmark's")
                    store.setdefault(h, []).append(forecast)
    states = {h: judge_script._scarcity_states(h, declaration.last_day) for h in horizons}

    def grids_of(items):
        return {
            h: pj.build_grid(declaration, h, rows, next(f for f in items if f.horizon == h and f.name == declaration.climatology).dates,
                             splits, scarcity_state=states[h])
            for h in horizons
        }

    calendar = [r.date for r in rows]
    everything = [f for h in horizons for f in forecasts[h] + parents[h] + refits[h]]
    grids = grids_of(everything)
    for h in horizons:
        pj.require_scored_days(declaration, grids[h].dates, where="setup sensitivity refit")
    first, last, share = period_share(declared, grids[horizons[0]].dates)

    def selector(**kwargs):
        weights = ss.period_weights(first, last, share)(kwargs["days"])
        return ss.select_cutoff_weighted(declaration.cutoff_false_alarms_at_most, weights=weights, **kwargs)

    def readings(source, rename=""):
        flat = [f for h in horizons for f in forecasts[h] + source[h]]
        declared_cut = pj.choose_cutoffs(declaration, grids, flat, calendar)
        weighted_cut = ss.choose_cutoffs_with(declaration, grids, flat, calendar, selector)
        return (
            sens.tier_readings(declaration, declared_cut, grids, None),
            sens.tier_readings(declaration, weighted_cut, grids, None),
        )

    parent_declared, parent_cutoff = readings(parents)
    refit_declared, refit_cutoff = readings(refits)
    table = {}
    keep = ("onsets", "onsets_flagged", "worst_false_alarms_per_onset", "by_year")
    for name in names:
        row = {
            "declared": parent_declared[name],
            "cutoff_only": parent_cutoff[name],
            "refit": refit_declared[name + SUFFIX],
            "refit_and_cutoff": refit_cutoff[name + SUFFIX],
        }
        table[name] = {
            reading: {k: v for k, v in row[reading].items() if k in keep}
            for reading in READINGS
        }
        table[name]["warned_days_changed_by_the_refit"] = {
            "refit_and_cutoff_vs_declared": [
                day for day, a, b, o in zip(row["declared"]["days"], row["declared"]["caught"], row["refit_and_cutoff"]["caught"], row["declared"]["onset"])
                if o and bool(a) != bool(b)
            ]
        }
    result = {
        "declaration": "metadata/setup_sensitivity_refit.json",
        "judge_sha256": declaration.sha256,
        "miss_rule": args.rule,
        "panel_sha256": panel_sha256(args.panel),
        "forecast_panels": digests,
        "period_share": share,
        "weights_by_window": weights_by_window(declaration, grids[horizons[0]].dates, calendar, first, last, share),
        "rows": table,
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def markdown(result: dict) -> str:
    years = sorted({y for r in result["rows"].values() for y in r["declared"]["by_year"]})
    lines = [
        "# 2018-19 down-weighted in the refit as well as the cut-off (#518)",
        "",
        f"The period's share of the scored days: {result['period_share']:.3f}. Miss rule: {result['miss_rule']}.",
        "",
        "## Table 1. The weight on a 2018-19 day, by the calendar year in which the refit window ends",
        "",
        "| window ends in | refits | weight on a 2018-19 day (min / max) |",
        "|---|---|---|",
    ]
    for year, cell in result["weights_by_window"].items():
        lines.append(f"| {year} | {cell['refits']} | {cell['min']:.3f} / {cell['max']:.3f} |")
    lines += [
        "",
        "## Table 2. Tier 1 under the four readings (onsets flagged of onsets at some horizon, +5 bp; worst false alarms per onset)",
        "",
        "| row | reading | flagged | worst FA per onset | " + " | ".join(years) + " |",
        "|---|---|---|---|" + "---|" * len(years),
    ]
    for name, row in result["rows"].items():
        for reading in READINGS:
            cell = row[reading]
            by_year = " | ".join(f"{cell['by_year'][y]['onsets_flagged']} of {cell['by_year'][y]['onsets']}" if y in cell["by_year"] else "–" for y in years)
            lines.append(f"| {name} | {reading} | {cell['onsets_flagged']} of {cell['onsets']} | {cell['worst_false_alarms_per_onset']:.2f} | {by_year} |")
    lines += ["", "Onsets whose warning differs between the declared reading and refit_and_cutoff:", ""]
    for name, row in result["rows"].items():
        changed = row["warned_days_changed_by_the_refit"]["refit_and_cutoff_vs_declared"]
        lines.append(f"* {name}: " + (", ".join(changed) if changed else "none"))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    refit = commands.add_parser("refit")
    refit.add_argument("--panel", type=Path, required=True)
    refit.add_argument("--published", type=Path, required=True)
    refit.add_argument("--bench", type=Path, required=True)
    refit.add_argument("--horizon", type=int, required=True)
    refit.add_argument("--output", type=Path, required=True)
    refit.set_defaults(run=refit_command)
    report = commands.add_parser("report")
    report.add_argument("--panel", type=Path, required=True)
    report.add_argument("--rule", choices=("unweighted", "weighted"), default="unweighted", help="the judge's miss rule; #482 read the flat (unweighted) one")
    report.add_argument("--bench", required=True)
    report.add_argument("--parent", required=True)
    report.add_argument("--refit", required=True)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--markdown", type=Path)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
