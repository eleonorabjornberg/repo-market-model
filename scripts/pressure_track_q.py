"""Track Q of #374 (#385): full predictive distributions with better tails, scored by the pressure-day judge.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it
is given and nothing into `docs/runs/`. The candidates, their features, the
flagging cut-offs and the distribution scores are in `metadata/pressure_track_q.json`,
which this script refuses to read unless it is committed and unchanged.

    PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PANEL --horizon H \
        --output OUT/track_q_h{H}.json --distribution OUT/distribution_h{H}.json
    PYTHONPATH=src python3 scripts/pressure_track_q.py judge --panel PANEL \
        --output OUT/judge.json --markdown OUT/judge.md \
        OUT/forecasts_h1.json ... OUT/track_q_h1.json ...
    PYTHONPATH=src python3 scripts/pressure_track_q.py distribution --panel PANEL \
        --output OUT/distribution.json --markdown OUT/distribution.md OUT/distribution_h1.json ...

`forecasts` runs every declared candidate and the gbm reference at one horizon,
once each, over the integer-basis-point grid the CRPS needs plus +5 and +10 bp.
It writes the +5 and +10 bp probabilities in the format `scripts/pressure_judge.py
forecasts` writes (the file `judge` reads) and, separately, each day's CRPS and
central-band ends. `judge` adds the candidates to the judge's own declaration in
memory and runs the judge. `distribution` reports CRPS and band coverage by
regime and pressure-day type, and the candidates' CRPS against the gbm's, paired.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml, pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402

DECLARATION = REPO / "metadata" / "pressure_track_q.json"
REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


judge_script = _load_script("pressure_judge")
MINIMUM_HISTORY = judge_script.MINIMUM_HISTORY
REFIT_EVERY = judge_script.REFIT_EVERY
DECISION = judge_script.DECISION


def load_declaration() -> dict:
    """The track's declaration, refused unless committed and unchanged."""

    judge_script.require_committed_declaration(DECLARATION)
    return json.loads(DECLARATION.read_text(encoding="utf-8"))


def _predictor(name, entry, declaration, splits):
    features = tuple(declaration["features"])
    if name == "gbm":
        return ml.gbm_exceedance(tuple(entry["regressors"]), minimum_history=MINIMUM_HISTORY)
    if entry["model"] == "pressure_qrf_exceedance":
        return ml.pressure_qrf_exceedance(features, splits, minimum_history=MINIMUM_HISTORY)
    return ml.pressure_natural_gradient_exceedance(
        features, splits, minimum_history=MINIMUM_HISTORY, family=entry["family"]
    )


def grid_taus(declaration):
    low, high = declaration["distribution"]["grid_bp"]
    return [float(k) for k in range(int(low), int(high) + 1)]


def day_scores(curve, taus, outcome, band):
    """The discrete CRPS and the central-band ends of one day's curve.

    `curve[i]` is P(spread > taus[i]) at integer taus in ascending order, so
    F(k) = 1 - curve; the CRPS sums (F(k) - 1[outcome <= k])^2 over the grid.
    """

    cdf = [1.0 - p for p in curve]
    crps = sum((f - (1.0 if outcome <= k else 0.0)) ** 2 for f, k in zip(cdf, taus))
    lower = next((k for f, k in zip(cdf, taus) if f >= band[0]), taus[-1])
    upper = next((k for f, k in zip(cdf, taus) if f >= band[1]), taus[-1])
    return crps, lower, upper


def forecasts_command(args) -> int:
    declaration = load_declaration()
    last_day = date.fromisoformat(declaration["scoring"]["last_day"])
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = judge_script.load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    grid = grid_taus(declaration)
    thresholds = [float(t) for t in declaration["thresholds_bp"]]
    taus = tuple(sorted(set(grid) | set(thresholds)))
    band = (declaration["distribution"]["band"]["lower"], declaration["distribution"]["band"]["upper"])
    entries = dict(declaration["candidates"])
    entries.update({"gbm_reference": declaration["reference"]["gbm"]})
    forecasts, distribution = {}, {}
    for name, entry in entries.items():
        predictor = _predictor("gbm" if name == "gbm_reference" else name, entry, declaration, splits)
        features = tuple(declaration["features"])
        report = rolling_exceedance_backtest(
            rows,
            predictor=predictor,
            model_name=name,
            features=features,
            registry=registry,
            decision_time=DECISION,
            taus=taus,
            minimum_history=MINIMUM_HISTORY,
            refit_every=REFIT_EVERY,
            end=last_day,
            horizon=args.horizon,
        )
        position = {tau: i for i, tau in enumerate(report.taus)}
        forecasts[name] = pj.Forecast(
            name=name,
            horizon=args.horizon,
            dates=tuple(report.scored_dates),
            probabilities={
                tau: tuple(curve[position[tau]] for curve in report.forecast) for tau in thresholds
            },
        )
        scores = []
        for curve, realised in zip(report.forecast, report.realized_bps):
            at_grid = [curve[position[k]] for k in grid]
            scores.append(day_scores(at_grid, grid, round(float(realised)), band))
        distribution[name] = {
            "dates": [d.isoformat() for d in report.scored_dates],
            "realised_bp": [round(float(v)) for v in report.realized_bps],
            "crps": [s[0] for s in scores],
            "band_lower": [s[1] for s in scores],
            "band_upper": [s[2] for s in scores],
        }
        chosen = getattr(predictor, "selections", None)
        if chosen:
            key = "min_samples_leaf" if "min_samples_leaf" in chosen[0] else "stages"
            distribution[name]["chosen"] = dict(Counter(str(record[key]) for record in chosen))
    document = judge_script._document(args.horizon, panel_sha256(args.panel), list(forecasts.values()))
    document["declaration_commit"] = judge_script.require_committed_declaration(DECLARATION)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    args.distribution.write_text(
        json.dumps({"horizon": args.horizon, "panel_sha256": panel_sha256(args.panel), "models": distribution}) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"horizon": args.horizon, "models": sorted(forecasts), "days": len(next(iter(forecasts.values())).dates)}))
    return 0


def _composed_declaration(track: dict) -> pj.Declaration:
    """The judge's declaration with this track's candidates (and the gbm reference) added, for this run only."""

    base = json.loads(pj.DEFAULT_DECLARATION.read_text(encoding="utf-8"))
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    entries = dict(track["candidates"])
    entries["gbm_reference"] = track["reference"]["gbm"]
    for name, entry in entries.items():
        features = ["spread_bps"] + (
            entry["regressors"] if name == "gbm_reference" else [f for f in track["features"] if f != "spread_bps"]
        )
        base["candidates"][name] = {
            "role": "candidate",
            "features": sorted(set(features)),
            "calibration": "none",
            "cutoffs": entry["cutoffs"],
        }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pressure_judge_with_track_q.json"
        path.write_text(json.dumps(base), encoding="utf-8")
        return pj.load_declaration(path)


def judge_command(args) -> int:
    track = load_declaration()
    declaration = _composed_declaration(track)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = judge_script.load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    forecasts = []
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))
    grids = {}
    for horizon in declaration.horizons:
        reference = next(f for f in forecasts if f.horizon == horizon and f.name == declaration.climatology)
        grids[horizon] = pj.build_grid(
            declaration, horizon, rows, reference.dates, splits,
            scarcity_state=judge_script._scarcity_states(horizon, declaration.last_day),
        )
    wanted = {name for name in declaration.candidates}
    forecasts = [f for f in forecasts if f.name in wanted]
    result = pj.judge(
        declaration, grids, forecasts, calendar=[row.date for row in rows], holdouts=judge_script._holdouts()
    )
    result["provenance"] = {
        "panel_sha256": digest,
        "judge_declaration_commit": judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION),
        "track_q_declaration_commit": judge_script.require_committed_declaration(DECLARATION),
        "forecast_files": [str(p) for p in args.inputs],
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(judge_script.markdown(result), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "verdicts": {name: c["verdict"]["passes"] for name, c in result["candidates"].items()},
    }))
    return 0


def _mean(values):
    return sum(values) / len(values) if values else None


def distribution_command(args) -> int:
    """CRPS and band coverage by regime and pressure-day type, and each candidate's CRPS against the gbm's."""

    track = load_declaration()
    judge_declaration = _composed_declaration(track)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = judge_script.load_split_declaration(SPLITS)
    by_date = {row.date: row for row in rows}
    digest = panel_sha256(args.panel)
    out = {"panel_sha256": digest, "horizons": {}}
    lines = ["# Track Q: CRPS and band coverage", ""]
    for path in sorted(args.inputs):
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        horizon = document["horizon"]
        models = document["models"]
        dates = [date.fromisoformat(d) for d in models["gbm_reference"]["dates"]]
        groups = {
            "all": ["all"] * len(dates),
            "regime": [splits.regime(d) for d in dates],
            "day_type": [splits.reporting_day_type(d, by_date[d].values) for d in dates],
        }
        table = {}
        for name, data in models.items():
            covered = [lo <= y <= hi for y, lo, hi in zip(data["realised_bp"], data["band_lower"], data["band_upper"])]
            width = [hi - lo for lo, hi in zip(data["band_lower"], data["band_upper"])]
            cells = {}
            for dimension, labels in groups.items():
                for label in dict.fromkeys(labels):
                    members = [i for i, l in enumerate(labels) if l == label]
                    cells[f"{dimension}:{label}"] = {
                        "days": len(members),
                        "crps": _mean([data["crps"][i] for i in members]),
                        "band_coverage": _mean([1.0 if covered[i] else 0.0 for i in members]),
                        "band_width": _mean([width[i] for i in members]),
                    }
            table[name] = {"cells": cells, **({"chosen": data["chosen"]} if "chosen" in data else {})}
        paired = {}
        reference = models["gbm_reference"]["crps"]
        for name, data in models.items():
            if name == "gbm_reference":
                continue
            difference = [r - c for r, c in zip(reference, data["crps"])]
            cells = {}
            for dimension, labels in groups.items():
                for label in dict.fromkeys(labels):
                    inside = [1.0 if l == label else 0.0 for l in labels]
                    cells[f"{dimension}:{label}"] = [inside, [i * d for i, d in zip(inside, difference)]]
            result = pj._bootstrap(
                judge_declaration,
                cells,
                {"crps_difference_vs_gbm": pj._ratio(1, 0)},
                len(difference),
                seed=pj._seed(judge_declaration.seed, "track_q", name, horizon),
            )
            paired[name] = result
        out["horizons"][str(horizon)] = {"models": table, "paired_vs_gbm": paired}
        lines += [f"## h = {horizon}", ""]
        lines += ["| model | cell | days | CRPS (bp) | 90% band coverage | band width (bp) | CRPS gain vs gbm [90%] |", "|---|---|---|---|---|---|---|"]
        for name, entry in table.items():
            for cell, value in entry["cells"].items():
                gain = ""
                if name in paired:
                    stat = paired[name][cell]["crps_difference_vs_gbm"]
                    interval = stat.get("interval")
                    gain = (
                        f"{stat['mean']:+.3f} [{interval['lower']:+.3f}, {interval['upper']:+.3f}]"
                        if interval and stat["mean"] is not None else "n/a"
                    )
                lines.append(
                    f"| {name} | {cell} | {value['days']} | {value['crps']:.3f} | {value['band_coverage']:.3f} | "
                    f"{value['band_width']:.2f} | {gain} |"
                )
        lines.append("")
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "horizons": sorted(out["horizons"])}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.add_argument("--distribution", type=Path, required=True)
    forecasts.set_defaults(run=forecasts_command)
    judge = commands.add_parser("judge")
    judge.add_argument("--panel", type=Path, required=True)
    judge.add_argument("--output", type=Path, required=True)
    judge.add_argument("--markdown", type=Path)
    judge.add_argument("inputs", nargs="+", type=Path)
    judge.set_defaults(run=judge_command)
    distribution = commands.add_parser("distribution")
    distribution.add_argument("--panel", type=Path, required=True)
    distribution.add_argument("--output", type=Path, required=True)
    distribution.add_argument("--markdown", type=Path)
    distribution.add_argument("inputs", nargs="+", type=Path)
    distribution.set_defaults(run=distribution_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
