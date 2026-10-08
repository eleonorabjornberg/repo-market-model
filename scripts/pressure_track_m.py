"""Track M of #374 (#384): a Markov-switching spread model, scored by the pressure-day judge.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it
is given and nothing into `docs/runs/`. The candidates, the model settings and
the flagging cut-offs are in `metadata/pressure_track_m.json`, which this script
refuses to read unless it is committed and unchanged.

    PYTHONPATH=src python3 scripts/pressure_track_m.py forecasts --panel PANEL --horizon H \
        --output OUT/markov_h{H}.json
    PYTHONPATH=src python3 scripts/pressure_track_m.py judge --panel PANEL \
        --output OUT/judge.json --markdown OUT/judge.md \
        OUT/forecasts_h1.json ... OUT/markov_h1.json ...
    PYTHONPATH=src python3 scripts/pressure_track_m.py states --panel PANEL --horizon H \
        --output OUT/states_hH.json

`forecasts` runs every declared candidate at one horizon, in the format
`scripts/pressure_judge.py forecasts` writes, on the measurement panel (the
published columns plus #115's inputs, `scarcity.measurement_declaration`). The
`judge` inputs also carry the benchmark files that script writes
(`pressure_judge.py forecasts --panel PANEL --horizon H --published`): this
command adds the declared candidates to the judge's own declaration in memory
and runs the judge on the lot. `states` reports the filtered state against
#115's declared scarcity state.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ml, pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.scarcity import (  # noqa: E402
    RESERVE_SCARCITY_STATE,
    measurement_declaration,
    with_reserve_scarcity_state,
)

DECLARATION = REPO / "metadata" / "pressure_track_m.json"
REGISTRY = REPO / "metadata" / "sources.json"


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
    """The track's declaration, refused unless committed and unchanged; settings pinned to the model's."""

    judge_script.require_committed_declaration(DECLARATION)
    document = json.loads(DECLARATION.read_text(encoding="utf-8"))
    if document["settings"] != dict(ml.MARKOV_SWITCHING_SETTINGS):
        raise SystemExit("the declared settings are not the model's")
    return document


def _measurement_rows(last_day):
    """The measurement panel's rows with #115's state, through the last scored day, and its registry."""

    validation = _load_script("scarcity_validation")
    with tempfile.TemporaryDirectory() as tmp:
        build, _, registry, _decision = validation.build_measurement_panel(REGISTRY, Path(tmp))
        rows = [row for row in with_reserve_scarcity_state(build.observations) if row.date <= last_day]
    return rows, registry


def forecasts_command(args) -> int:
    from datetime import date

    declaration = load_declaration()
    last_day = date.fromisoformat(declaration["scoring"]["last_day"])
    published = load_daily_panel(args.panel)
    audit_panel(published)
    taus = tuple(float(t) for t in declaration["thresholds_bp"])
    forecasts = {}
    with measurement_declaration():
        rows, registry = _measurement_rows(last_day)
        for name, entry in declaration["candidates"].items():
            scarcity = RESERVE_SCARCITY_STATE if entry["scarcity_covariate"] else None
            features = ("spread_bps",) + ((RESERVE_SCARCITY_STATE,) if scarcity else ())
            report = rolling_exceedance_backtest(
                rows,
                predictor=ml.markov_switching_exceedance(
                    states=entry["states"], minimum_history=MINIMUM_HISTORY, scarcity_column=scarcity
                ),
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
            forecasts[name] = pj.report_forecast(name, report)
    document = judge_script._document(args.horizon, panel_sha256(args.panel), list(forecasts.values()))
    document["declaration_commit"] = judge_script.require_committed_declaration(DECLARATION)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "models": sorted(forecasts), "days": len(next(iter(forecasts.values())).dates)}))
    return 0


def _composed_declaration(track: dict) -> pj.Declaration:
    """The judge's declaration with this track's candidates added, for this run only."""

    base = json.loads(pj.DEFAULT_DECLARATION.read_text(encoding="utf-8"))
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    for name, entry in track["candidates"].items():
        base["candidates"][name] = {
            "role": "candidate",
            "features": ["spread_bps"] + ([RESERVE_SCARCITY_STATE] if entry["scarcity_covariate"] else []),
            "calibration": "none",
            "cutoffs": entry["cutoffs"],
        }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pressure_judge_with_track_m.json"
        path.write_text(json.dumps(base), encoding="utf-8")
        return pj.load_declaration(path)


def judge_command(args) -> int:
    track = load_declaration()
    declaration = _composed_declaration(track)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = judge_script.load_split_declaration(judge_script.SPLITS)
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
        "track_m_declaration_commit": judge_script.require_committed_declaration(DECLARATION),
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


def states_command(args) -> int:
    """The filtered state (the most likely state of the model's as-of distribution) against #115's state.

    For the declared three-state scarcity-covariate candidate, refitted every refit block as the
    backtest does: per scored day, the argmax of the filtered distribution and #115's state read at
    the same decision, tabulated, with the share of days above +5 bp in each cell.
    """

    from datetime import date
    from repo_model.asof import InformationRule
    from repo_model.baseline import _as_of_folds
    from repo_model.data import exceeds_bp

    declaration = load_declaration()
    last_day = date.fromisoformat(declaration["scoring"]["last_day"])
    entry = declaration["candidates"]["markov_k3_scarcity"]
    cells = Counter()
    events = Counter()
    with measurement_declaration():
        rows, registry = _measurement_rows(last_day)
        rule = InformationRule(
            registry, ("spread_bps", RESERVE_SCARCITY_STATE), decision_time=DECISION, horizon=args.horizon
        )
        fitted = None
        for fold in _as_of_folds(
            rows, rule, minimum_history=MINIMUM_HISTORY, refit_every=REFIT_EVERY,
            entry="pressure_track_m.states", end=last_day,
        ):
            if fold.frame is not None:  # the row that opens a refit block fits on its frame
                train_rows = list(fold.frame)
                fitted = ml.fit_markov_switching(
                    [ml._observed_spread(r, "states") for r in train_rows],
                    ml._tight_covariates(train_rows, RESERVE_SCARCITY_STATE),
                    states=entry["states"],
                )
            history = rule.frame(rows, fold.info)
            cov = ml._tight_covariates(history, RESERVE_SCARCITY_STATE)
            filtered = ml.filter_markov_switching(
                fitted, [ml._observed_spread(r, "states") for r in history], cov
            )
            filtered_state = max(range(entry["states"]), key=lambda k: filtered[k])
            scarcity = fold.feature_row.values.get(RESERVE_SCARCITY_STATE)
            label = "unknown" if scarcity is None else str(int(scarcity))
            scored = rows[fold.info.scored_index]
            cells[(label, filtered_state)] += 1
            events[(label, filtered_state)] += int(exceeds_bp(scored.spread_bps, 5.0))
    table = [
        {"scarcity_state": label, "filtered_state": state, "days": n, "pressure_days_at_5bp": events[(label, state)]}
        for (label, state), n in sorted(cells.items())
    ]
    args.output.write_text(json.dumps({"horizon": args.horizon, "table": table}, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "cells": len(table)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.set_defaults(run=forecasts_command)
    judge = commands.add_parser("judge")
    judge.add_argument("--panel", type=Path, required=True)
    judge.add_argument("--output", type=Path, required=True)
    judge.add_argument("--markdown", type=Path)
    judge.add_argument("inputs", nargs="+", type=Path)
    judge.set_defaults(run=judge_command)
    states = commands.add_parser("states")
    states.add_argument("--panel", type=Path, required=True)
    states.add_argument("--horizon", type=int, required=True)
    states.add_argument("--output", type=Path, required=True)
    states.set_defaults(run=states_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
