"""Fed repo operations and SRF take-up as scratch measurement fields (#425, track F of #374).

A scratch measurement input, not a record: it writes a CSV and a summary to the paths it
is given, and nothing into `docs/runs/`. Every column is off in every published declaration
(`repo_model.fed_liquidity`); a track switches them on for its own run with `switched_on()`.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/fed_liquidity.py panel --panel AUG.csv --output AUG_F.csv

`panel` adds to the panel the raw columns (from the tracked snapshots of the Desk's repo
operation results, `tests/fixtures/snapshots/repo_ops_inputs`) and then the derived ones, and
keeps the rows up to 2025-12-31 (`docs/decisions/lockbox.md`). A track that scores with the
columns does so inside `switched_on()`.

    PYTHONPATH=src python3 scripts/fed_liquidity.py forecasts --panel AUG_F.csv --published PUB.csv \\
        --horizon H --output OUT/f_hH.json
    PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon H --output OUT/h_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon H --output OUT/b_hH.json --published
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/b_h1.json OUT/h_h1.json OUT/f_h1.json ...

`forecasts` scores each candidate declared by track F in `metadata/pressure_judge.json`
(`fed_liquidity.CANDIDATES`: the hierarchical logistic of #406 with the inputs added),
walk-forward on the shared fold grid (minimum history 61, refit every 21 days, scored days
through 2025-12-31), recalibrated out of fold. It refuses a declaration that is not
committed and unchanged. The control, the same classifier without the inputs, is
`scripts/hierarchical_logistic.py forecasts` on the same grid.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import importlib.util  # noqa: E402

from repo_model import contract, fed_liquidity, ml, pressure, pressure_judge as pj, scarcity  # noqa: E402
from repo_model import scarcity_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model import hierarchical_logistic as hl  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


judge_script = _script("pressure_judge")
MINIMUM_HISTORY = judge_script.MINIMUM_HISTORY
REFIT_EVERY = judge_script.REFIT_EVERY
DECISION = judge_script.DECISION
SPLITS = judge_script.SPLITS

SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots" / "repo_ops_inputs"
#: The published panel's build cutoff (`metadata/funding_panel_manifest.json`).
BUILD_CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=timezone.utc)
#: The last day any comparison may score, or any row of the scratch panel carry
#: (`docs/decisions/lockbox.md`).
END = date(2025, 12, 31)


@contextlib.contextmanager
def switched_on():
    """`fed_liquidity.COLUMN_FIELDS` in the feature map, for this run only."""

    fields = dict(fed_liquidity.COLUMN_FIELDS)
    with mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{
                    column: tuple(sorted({source for source, _f in pairs}))
                    for column, pairs in fields.items()
                },
            }
        ),
    ):
        yield


def _cell(value):
    return "" if value is None else repr(float(value))


def panel_command(args) -> int:
    published = load_daily_panel(args.panel)
    rows, summary = fed_liquidity.assemble(published, SNAPSHOTS, cutoff=BUILD_CUTOFF, end=END)
    with args.panel.open(newline="", encoding="utf-8") as handle:
        base = next(csv.reader(handle))
    header = list(dict.fromkeys(base + list(fed_liquidity.RAW_COLUMNS) + list(fed_liquidity.DERIVED_COLUMNS)))
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow([row.date.isoformat()] + [_cell(row.values.get(name)) for name in header[1:]])
    summary.update(
        output=str(args.output),
        sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
        rows=len(rows),
        first=rows[0].date.isoformat(),
        last=rows[-1].date.isoformat(),
    )
    print(json.dumps(summary, indent=1))
    return 0


def score(rows, splits, registry, declaration, name, horizon):
    """One candidate's recalibrated forecasts at one horizon."""

    features = fed_liquidity.features_at_horizon(name, horizon)
    predictor = ml._scarcity_calendar_predictor(
        "logistic", features, splits, sc.STATE_FORMS[hl.STATE_FORM],
        minimum_history=MINIMUM_HISTORY, regime_hierarchical=True,
    )
    with scarcity.measurement_declaration(), switched_on():
        raw = rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=name, features=features, registry=registry,
            decision_time=DECISION, taus=declaration.thresholds, minimum_history=MINIMUM_HISTORY,
            refit_every=REFIT_EVERY, end=declaration.last_day, horizon=horizon,
        )
    return pj.report_forecast(name, pressure.recalibrated(raw))


def forecasts_command(args) -> int:
    declaration = pj.load_declaration()
    commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    require_unlocked([declaration.last_day], where="fed_liquidity")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = fed_liquidity.load_registry()
    names = [args.candidate] if args.candidate else list(fed_liquidity.CANDIDATES)
    produced = []
    for name in names:
        produced.append(score(rows, splits, registry, declaration, name, args.horizon))
        print(json.dumps({"candidate": name, "horizon": args.horizon, "days": len(produced[-1].dates)}), flush=True)
    document = judge_script._document(args.horizon, panel_sha256(args.published), produced)
    document["scratch_panel_sha256"] = panel_sha256(args.panel)
    document["declaration_commit"] = commit
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    panel = commands.add_parser("panel", help="the panel plus the Fed liquidity fields")
    panel.add_argument("--panel", type=Path, required=True)
    panel.add_argument("--output", type=Path, required=True)
    panel.set_defaults(handler=panel_command)
    forecasts = commands.add_parser("forecasts", help="the track-F candidates' forecasts for the judge")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--published", type=Path, required=True)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--candidate", choices=sorted(fed_liquidity.CANDIDATES))
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.set_defaults(handler=forecasts_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
