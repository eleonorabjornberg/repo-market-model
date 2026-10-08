"""Score the policy-register features (#412, track P of #374) for the pressure-day judge.

A scratch measurement, not a record: it writes CSV and JSON to the paths it is given and nothing
into `docs/runs/`. The candidates, controls and columns are in `metadata/policy_features.json`,
which this script refuses to read unless it is committed and unchanged. Every column is off in
every published declaration and switched on for these runs only.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/policy_features.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/policy_features.py run --panel AUG3.csv --published PUBLISHED.csv \\
        --horizon H --output OUT/policy_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv \\
        --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h1.json ... OUT/policy_h1.json ...

`panel` adds the nine register columns (`repo_model.policy_features`) to a scratch panel, each read
at its own row's 16:00 decision instant from the entries announced by then. `run` fits, for the best
rare-event classifier of #381 and the best onset classifier of #409, the control (the classifier as
its own track declared it) and the same classifier with the register columns added, walk-forward on
the shared fold grid at +5 and +10 bp, days before 2026-01-01 only, then recalibrates each out of
fold against the pressure-day outcome (`pressure.recalibrated`). The output has the shape of
`pressure_model_v1.py horizon`'s: `forecasts` holds every candidate `+recalibrated`, the form the
judge declares; the raw fits are kept under `unrecalibrated_forecasts` as an ablation.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, measurement_fields, ml, policy_features, pressure, scarcity  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "policy_features.json"
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


def control_features(spec: dict, horizon: int) -> tuple:
    """The inputs of the candidate's control, as its own track declared them, at `horizon`."""

    track = committed_declaration(REPO / spec["declaration"])
    if spec["estimator"] == "rare_event":
        names = list(track["features"])
        optional = []
    else:
        base = track["candidates"][spec_name(spec, track)]
        names = [n for group in base["inputs"] for n in track["features"][group]]
        optional = list(base["optional"])
    return tuple(n for n in names if horizon == 1 or n != SETTLEMENT), tuple(optional)


def spec_name(spec: dict, track: dict) -> str:
    """The control's name in its own track's declaration: the declared candidate with this kind and treatment."""

    for name, base in track["candidates"].items():
        if base["kind"] == spec["kind"] and base.get("treatment") == spec["treatment"]:
            if spec["estimator"] == "onset" and base["inputs"] != ["base", "funding"]:
                continue
            return name
    raise SystemExit(f"no candidate of {spec['declaration']} has kind {spec['kind']} and treatment {spec['treatment']}")


def features_of(declared: dict, spec: dict, horizon: int) -> tuple:
    """(features, optional) the candidate reads at `horizon`: the control's, plus the register when `policy`."""

    names, optional = control_features(spec, horizon)
    if spec["policy"]:
        names = names + tuple(declared["policy_columns"])
    return names, optional


@contextlib.contextmanager
def switched_on(estimator: str):
    """The register columns (and, for the onset estimator, the track's own inputs) in the feature map."""

    fields = dict(policy_features.COLUMN_FIELDS)
    stack = contextlib.ExitStack()
    if estimator == "onset":
        fields.update(measurement_fields.COLUMN_FIELDS)
        stack.enter_context(scarcity.measurement_declaration())
    with stack:
        with mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
            FEATURE_SOURCES=MappingProxyType(
                {
                    **contract.FEATURE_SOURCES,
                    **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
                }
            ),
        ):
            yield


def column(version):
    return {
        f"{tau:g}": {when.isoformat(): curve[position] for when, curve in zip(version.scored_dates, version.forecast)}
        for position, tau in enumerate(version.taus)
    }


def _cell(value):
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    rows = policy_features.add_columns(load_daily_panel(args.panel))
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + list(policy_features.COLUMNS)))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                "rows": len(rows),
                "first": rows[0].date.isoformat(),
                "last": rows[-1].date.isoformat(),
                "columns": list(policy_features.COLUMNS),
            },
            indent=1,
        )
    )
    return 0


def run_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="policy_features")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    missing = [c for c in policy_features.COLUMNS if c not in rows[0].values]
    if missing:
        raise SystemExit(f"{args.panel} carries no {missing}; build it with `policy_features.py panel`")
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["candidates"])
    forecasts, raw_forecasts, settings = {}, {}, {}
    for name in names:
        spec = declared["candidates"][name]
        features, optional = features_of(declared, spec, h)
        if spec["estimator"] == "rare_event":
            predictor = ml.pressure_rare_event_exceedance(
                spec["kind"], spec["treatment"], features, splits, minimum_history=minimum
            )
        else:
            predictor = ml.pressure_onset_exceedance(
                spec["kind"], spec["treatment"], features, splits, minimum_history=minimum, optional=optional
            )
        with switched_on(spec["estimator"]):
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    panel = commands.add_parser("panel", help="a scratch panel plus the register columns")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--output", type=Path, required=True)
    panel.set_defaults(handler=panel_command)
    run = commands.add_parser("run", help="score the declared candidates and controls at one horizon")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
