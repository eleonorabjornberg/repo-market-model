"""The pressure-day judge (#375): score candidates under #374's declared bar.

A scratch measurement, not a record: it writes JSON and a Markdown summary to
the paths it is given, and nothing into `docs/runs/`. The bar, the thresholds,
the horizons and every flagging cut-off are in `metadata/pressure_judge.json`,
which this script refuses to read unless it is committed and unchanged: a
declaration is made before scoring, not edited beside it.

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PANEL --horizon H \
        --output OUT/forecasts_hH.json [--published]
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PANEL \
        --output OUT/judge.json --markdown OUT/judge.md OUT/forecasts_h1.json ... OUT/forecasts_h5.json

`forecasts` scores the two benchmarks at one horizon (`pressure_judge.benchmark_forecasts`)
and, with `--published`, the current published probability (pressure model v1:
the published funding declaration's distribution, conformal PID with nested
selection, recalibrated out of fold; `scripts/pressure_model_v1.py publish`) as
the `published_v1` baseline row. Its output has the shape of
`pressure_model_v1.py horizon`'s `forecasts` block, so a candidate track writes
its own forecasts in that shape and passes the file to `judge`.

`judge` reads the forecast files, builds the shared grid at each horizon (the
declared groupings: year regimes, the reserve-scarcity state of #115 read as of
each forecast's decision instant, and the pressure-day type), and writes the
bar's evidence for every declared candidate. Scored days are before 2026-01-01
(`docs/decisions/lockbox.md`, #374).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
EVENTS = REPO / "metadata" / "events.json"
THRESHOLDS = REPO / "metadata" / "stress_thresholds.json"
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_committed_declaration(path: Path) -> str:
    """The commit that last changed the declaration, refusing one that is not committed.

    Raises:
        SystemExit: if the file differs from `HEAD` or is untracked.
    """

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(
            f"{relative} is not committed ({dirty}); the judge's declaration is committed before "
            f"any score is computed"
        )
    return subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()


def _document(horizon, digest, forecasts):
    return {
        "horizon": horizon,
        "panel_sha256": digest,
        "forecasts": {
            forecast.name: {
                f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, column)}
                for tau, column in forecast.probabilities.items()
            }
            for forecast in forecasts
        },
    }


def _published(rows, splits, registry, horizon, declaration):
    """The published probability: pressure model v1's recalibrated distributional gbm.

    The same run as `pressure_model_v1.py publish`, which writes a record and
    not the per-day probabilities this judge needs.
    """

    from repo_model import ml, pressure
    from repo_model.baseline import rolling_exceedance_backtest
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
            tuple(name for name in features if name != "spread_bps"), minimum_history=MINIMUM_HISTORY
        ),
        model_name="distributional_gbm",
        features=features,
        registry=registry,
        decision_time=DECISION,
        taus=declaration.thresholds,
        minimum_history=MINIMUM_HISTORY,
        refit_every=REFIT_EVERY,
        end=declaration.last_day,
        horizon=horizon,
        online_calibration=online,
    )
    return pj.report_forecast("published_v1", pressure.recalibrated(raw))


def forecasts_command(args) -> int:
    declaration = pj.load_declaration()
    commit = require_committed_declaration(pj.DEFAULT_DECLARATION)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text())
    forecasts = pj.benchmark_forecasts(
        declaration, rows, splits, registry, horizon=args.horizon,
        decision_time=DECISION, minimum_history=MINIMUM_HISTORY, refit_every=REFIT_EVERY,
    )
    if args.published:
        forecasts.append(_published(rows, splits, registry, args.horizon, declaration))
    document = _document(args.horizon, panel_sha256(args.panel), forecasts)
    document["declaration_commit"] = commit
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "models": sorted(document["forecasts"]), "output": str(args.output)}))
    return 0


def _scarcity_states(horizon, last_day):
    """{day: state} on the shared grid, read as of each forecast's decision instant at `horizon`."""

    from repo_model.asof import InformationRule
    from repo_model.baseline import _as_of_folds
    from repo_model.scarcity import (
        RESERVE_SCARCITY_STATE, measurement_declaration, with_reserve_scarcity_state,
    )

    validation = _load_script("scarcity_validation")
    with measurement_declaration(), tempfile.TemporaryDirectory() as tmp:
        build, _, registry, decision = validation.build_measurement_panel(REGISTRY, Path(tmp))
        rows = with_reserve_scarcity_state(build.observations)
        rule = InformationRule(
            registry, ("spread_bps", RESERVE_SCARCITY_STATE), decision_time=decision, horizon=horizon
        )
        states = {}
        for fold in _as_of_folds(
            rows, rule, minimum_history=MINIMUM_HISTORY, refit_every=len(rows),
            entry="pressure_judge.scarcity_state", end=last_day,
        ):
            states[rows[fold.index].date] = fold.feature_row.values.get(RESERVE_SCARCITY_STATE)
    return states


def _holdouts():
    document = json.loads(EVENTS.read_text())
    return {
        window["name"]: (date.fromisoformat(window["start"]), date.fromisoformat(window["end"]))
        for window in document["windows"]
    }


def judge_command(args) -> int:
    declaration = pj.load_declaration()
    commit = require_committed_declaration(pj.DEFAULT_DECLARATION)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
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
            scarcity_state=_scarcity_states(horizon, declaration.last_day),
        )
    result = pj.judge(declaration, grids, forecasts, holdouts=_holdouts())
    result["provenance"] = {
        "panel_sha256": digest,
        "declaration_commit": commit,
        "forecast_files": [str(p) for p in args.inputs],
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "verdicts": {name: c["verdict"]["passes"] for name, c in result["candidates"].items()},
    }))
    return 0


# -- the summary --------------------------------------------------------------


def _f(value, places=3):
    return "–" if value is None else f"{value:.{places}f}"


def _cell(cell):
    if "interval" in cell:
        i = cell["interval"]
        return f"{cell['mean']:+.4f} [{i['lower']:+.4f}, {i['upper']:+.4f}]"
    return f"{_f(cell['mean'], 4)} (no interval)"


def markdown(result) -> str:
    declaration = result["declaration"]
    primary = f"{declaration['primary_threshold_bp']:g}"
    lines = [
        "# Pressure-day judge (#375)",
        "",
        f"Declaration `{declaration['path']}` sha256 `{declaration['sha256'][:12]}…`. "
        f"Scored days {result['scored_window']['first']} to {result['scored_window']['last']}. "
        "Bar: recall ≥ {recall_at_least}, false alarms per true day ≤ {false_alarms_per_true_at_most}, "
        "and a win over calendar climatology at the same recall (paired, {level:.0%} stationary "
        "bootstrap) on Brier and on precision.".format(**declaration["bar"]),
        "",
    ]
    for name, candidate in result["candidates"].items():
        verdict = candidate["verdict"]
        lines += [
            f"## {name} ({candidate['role']}): {'PASS' if verdict['passes'] else 'FAIL'} at +{primary} bp",
            "",
            "| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for horizon, per_tau in candidate["horizons"].items():
            row = per_tau[primary]
            clim = row.get("paired", {}).get("vs_calendar_climatology")
            lines.append(
                f"| {horizon} | {row['cutoff']:g} | {_f(row['flags']['recall'])} | {_f(row['flags']['precision'])} | "
                f"{_f(row['flags']['false_alarms_per_true'])} | {_f(row['brier'], 4)} | "
                f"{_cell(clim['brier_difference']) if clim else '–'} | "
                f"{_cell(clim['precision_difference']) if clim else '–'} | "
                f"{_f(row['auroc'])} | {_f(row['usefulness'].get('relative'))} | "
                f"{'pass' if row['bar']['passes'] else 'fail'} |"
            )
        floors = [
            (h, per_tau[primary]["at_recall_floor_ex_post"]) for h, per_tau in candidate["horizons"].items()
        ]
        lines += [
            "",
            "Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: "
            + "; ".join(
                f"h = {h}: " + ("no event" if f is None else f"cut-off {f['cutoff']:.3f}, precision {_f(f['precision'])}, false alarms per true {_f(f['false_alarms_per_true'])}")
                for h, f in floors
            ),
        ]
        lead = candidate["lead_time"]
        lines += [
            "",
            f"Lead time at +{primary} bp: {lead['flagged']} of {lead['onsets']} onsets flagged, mean {_f(lead['mean_lead_days'], 2)} days."
            if "onsets" in lead
            else f"Lead time: {lead['unavailable']}.",
            "",
        ]
        first = next(iter(candidate["horizons"]))
        row = candidate["horizons"][first][primary]
        lines += [
            f"The bar by group at h = {first}:",
            "",
            "| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for dimension, cells in row.get("splits", {}).items():
            for label, cell in cells.items():
                flags = cell["flags"]
                lines.append(
                    f"| {dimension} | {label} | {cell['days']} | {cell['events']} | {_f(flags['recall'])} | "
                    f"{_f(flags['precision'])} | {_cell(cell['brier_difference']) if isinstance(cell.get('brier_difference'), dict) else _f(cell.get('brier_difference'), 4)} | "
                    f"{_cell(cell['precision_difference']) if isinstance(cell.get('precision_difference'), dict) else _f(cell.get('precision_difference'), 4)} | "
                    f"{'pass' if cell.get('bar', {}).get('passes') else 'fail' if 'bar' in cell else '–'} |"
                )
        if row.get("holdouts"):
            lines += ["", f"Knowledge holdouts at h = {first} (descriptive):", "", "| window | days | events | recall | precision | Brier | climatology Brier |", "|---|---|---|---|---|---|---|"]
            for window, cell in row["holdouts"].items():
                if not cell.get("days"):
                    lines.append(f"| {window} | 0 | | | | | |")
                    continue
                lines.append(
                    f"| {window} | {cell['days']} | {cell['events']} | {_f(cell['flags']['recall'])} | "
                    f"{_f(cell['flags']['precision'])} | {_f(cell['brier'], 4)} | {_f(cell['climatology_brier'], 4)} |"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.add_argument("--published", action="store_true")
    forecasts.set_defaults(run=forecasts_command)
    judge = commands.add_parser("judge")
    judge.add_argument("--panel", type=Path, required=True)
    judge.add_argument("--output", type=Path, required=True)
    judge.add_argument("--markdown", type=Path)
    judge.add_argument("inputs", nargs="+", type=Path)
    judge.set_defaults(run=judge_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
