"""Score the onset classifier (#409, a track of #374) for the pressure-day judge.

A scratch measurement, not a record: it writes JSON to the path it is given and nothing
into `docs/runs/`. The candidates, features, weighting and horizons are in
`metadata/onset_classifier.json`, which this script refuses to read unless it is committed
and unchanged, as `metadata/pressure_judge.json` (the same candidates, and the flag
cut-off rule) is for the judge. Every input beyond the published panel is off in every
published declaration and switched on for these runs only.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/onset_classifier.py run --panel AUG2.csv --published PUBLISHED.csv \\
        --horizon H --output OUT/onset_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv \\
        --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h1.json ... OUT/onset_h1.json ...

`run` fits every declared candidate to the onset label (`ml.pressure_onset_exceedance`),
walk-forward on the shared fold grid at +5 and +10 bp, days before 2026-01-01 only, then
recalibrates it out of fold against the pressure-day outcome (`pressure.recalibrated`).
The output has the shape of `pressure_model_v1.py horizon`'s: `forecasts` holds every
candidate `+recalibrated`, the form the judge declares; the onset-rate raw fits are kept
under `unrecalibrated_forecasts` as an ablation. After the judge, `leads` reports the onset
recall and the false alarms per onset at each lead h = 1 to 5 under the judge's own cut-offs:

    PYTHONPATH=src python3 scripts/onset_classifier.py leads --panel PUBLISHED.csv --output OUT/leads.json OUT/bench_h?.json OUT/onset_h?.json
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, measurement_fields, ml, pressure, scarcity  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "onset_classifier.json"
SETTLEMENT = "treasury_settlement"


def committed_declaration(path: Path) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def features_at_horizon(declared: dict, spec: dict, horizon: int) -> tuple:
    """The candidate's declared inputs at `horizon`: the settlement column only at h = 1."""

    names = [name for group in spec["inputs"] for name in declared["features"][group]]
    return tuple(name for name in names if horizon == 1 or name != SETTLEMENT)


@contextlib.contextmanager
def switched_on():
    """The scarcity state and the measurement fields in the feature map, for this run only."""

    fields = dict(measurement_fields.COLUMN_FIELDS)
    with scarcity.measurement_declaration(), mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{column: tuple(sorted({source for source, _f in pairs})) for column, pairs in fields.items()},
            }
        ),
    ):
        yield


def column(version):
    return {
        f"{tau:g}": {when.isoformat(): curve[position] for when, curve in zip(version.scored_dates, version.forecast)}
        for position, tau in enumerate(version.taus)
    }


def run_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="onset_classifier")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["candidates"])
    forecasts, raw_forecasts, settings = {}, {}, {}
    for name in names:
        spec = declared["candidates"][name]
        features = features_at_horizon(declared, spec, h)
        predictor = ml.pressure_onset_exceedance(
            spec["kind"], spec["treatment"], features, splits, minimum_history=minimum, optional=spec["optional"]
        )
        with switched_on():
            report = rolling_exceedance_backtest(
                rows,
                predictor=predictor,
                model_name=name,
                features=features,
                registry=registry,
                decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                taus=taus,
                minimum_history=minimum,
                refit_every=declared["scoring"]["refit_every"],
                end=last,
                horizon=h,
            )
        forecasts[name + declared["judged_form"]] = column(pressure.recalibrated(report))
        raw_forecasts[name] = column(report)
        settings[name] = {
            "features": list(report.features),
            "model_settings": dict(report.model_settings),
            "ml_libraries": None if report.ml_libraries is None else dict(report.ml_libraries),
        }
        print(json.dumps({"horizon": h, "candidate": name, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "declarations": settings,
        "forecasts": forecasts,
        "unrecalibrated_forecasts": raw_forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def leads_command(args) -> int:
    """Onset recall and false alarms per onset at each lead, under the judge's own cut-offs.

    The judge reports the onset tier at "lead at least 1" and "at least 3"; this reads the same
    grids and the cut-offs `pressure_judge.choose_cutoffs` chooses for each forecast, and reports
    the share of +5 bp onsets flagged at exactly horizon h and the false alarms (flags on days
    that are not pressure days) per onset, for h = 1 to 5.
    """

    # The judge's script is a sibling file, not a package module; load it by path.
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    from repo_model import pressure_judge as pj

    declaration = pj.load_declaration()
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
    states = {h: script._scarcity_states(h, declaration.last_day) for h in declaration.horizons}

    def grids_of(items):
        out = {}
        for h in declaration.horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    grids = grids_of(chosen)
    tau = declaration.primary
    table = {}
    for forecast in chosen:
        grid = grids[forecast.horizon]
        flags = [1 if p >= c else 0 for p, c in zip(forecast.probabilities[tau], forecast.cutoffs[tau])]
        outcomes, onset = grid.outcomes[tau], grid.onset_at(tau, tau)
        onsets = sum(onset)
        caught = sum(f and o for f, o in zip(flags, onset))
        false_alarms = sum(f and not y for f, y in zip(flags, outcomes))
        table.setdefault(forecast.name, {})[str(forecast.horizon)] = {
            "onsets": onsets,
            "onsets_flagged": caught,
            "recall": caught / onsets if onsets else None,
            "flags": sum(flags),
            "false_alarms": false_alarms,
            "false_alarms_per_onset": false_alarms / onsets if onsets else None,
        }
    args.output.write_text(json.dumps(table, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("| model | " + " | ".join(f"h={h}" for h in declaration.horizons) + " |")
    print("|---|" + "---|" * len(declaration.horizons))
    for name in sorted(table):
        cells = [
            f"{c['onsets_flagged']}/{c['onsets']} ({c['recall']:.2f}), {c['false_alarms_per_onset']:.2f}"
            for c in (table[name][str(h)] for h in declaration.horizons)
        ]
        print(f"| {name} | " + " | ".join(cells) + " |")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    leads = commands.add_parser("leads", help="onset recall and false alarms per onset at each lead")
    leads.add_argument("--panel", type=Path, required=True)
    leads.add_argument("--output", type=Path, required=True)
    leads.add_argument("inputs", nargs="+", type=Path)
    leads.set_defaults(handler=leads_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
