"""Score the risk-date severity model (#428, track V of #374) for the pressure-day judge.

A scratch measurement, not a record: it writes JSON to the path it is given and nothing
into `docs/runs/`. The candidates, features and risk-date rule are in
`metadata/risk_date_severity.json`, which this script refuses to read unless it is committed
and unchanged, as `metadata/pressure_judge.json` (the same candidates, and the flag
cut-off rule) is for the judge. Every input beyond the published panel is off in every
published declaration and switched on for these runs only.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv \\
        --horizon H --output OUT/risk_hH.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv \\
        --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h1.json ... OUT/risk_h1.json ...
    PYTHONPATH=src python3 scripts/risk_date_severity.py report --panel PUBLISHED.csv \\
        --output OUT/risk_dates.json OUT/bench_h?.json OUT/risk_h?.json

`run` fits every declared candidate on the risk-date label days of the shared fold grid
(`ml.pressure_risk_date_exceedance`), walk-forward at +5 and +10 bp, days before 2026-01-01
only. The output has the shape of `pressure_model_v1.py horizon`'s: the forecasts are the raw
fits (no recalibration), exactly 0 on every day that is not a risk date.

`report` is the judge's reading on all days and on the declared risk dates alone, under the
judge's own cut-offs (`pressure_judge.choose_cutoffs`): at each lead h = 1 to 5, the +5 bp
onsets flagged and the false alarms per onset, the flags on days that are not risk dates (none
by construction, checked), the Brier score and the AUROC on the risk dates against calendar
climatology, persistence-logistic and the candidate's own twin without the new inputs, paired,
with a stationary-bootstrap 90% interval.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import random
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import contract, measurement_fields, ml, scarcity  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "risk_date_severity.json"
SETTLEMENT_COLUMNS = ("treasury_settlement", "treasury_settlement_coupons")
COUPONS = "treasury_settlement_coupons"
TWIN_SUFFIX = "_base"


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
    """The candidate's declared inputs at `horizon`: the settlement columns only at h = 1."""

    names = [name for group in spec["inputs"] for name in declared["features"][group]]
    return tuple(name for name in names if horizon == 1 or name not in SETTLEMENT_COLUMNS)


def is_risk_date(splits, values, horizon: int) -> bool:
    """The declared risk-date rule, read off a panel row (the same rule `ml._RiskDateDesign.member` serves)."""

    if splits.day_type(values) != "ordinary":
        return True
    return horizon == 1 and float(values.get(COUPONS) or 0.0) > 0.0


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
    require_unlocked([last], where="risk_date_severity")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    names = [args.candidate] if args.candidate else list(declared["candidates"])
    forecasts, settings = {}, {}
    for name in names:
        spec = declared["candidates"][name]
        features = features_at_horizon(declared, spec, h)
        predictor = ml.pressure_risk_date_exceedance(spec["kind"], features, splits, minimum_history=minimum)
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
        forecasts[name] = column(report)
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
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def _brier(p, y):
    return sum((a - b) ** 2 for a, b in zip(p, y)) / len(y) if y else None


def _auroc(pj, p, y):
    return pj.auroc(p, y) if y and 0 < sum(y) < len(y) else None


def _paired(rng_seed, a, b, y, block, replications, level):
    """Mean Brier difference a - b over `y` with a stationary-bootstrap interval (negative favours a)."""

    n = len(y)
    if n == 0:
        return None
    diffs = [(p - o) ** 2 - (q - o) ** 2 for p, q, o in zip(a, b, y)]
    rng = random.Random(rng_seed)
    draws = sorted(sum(diffs[i] for i in stationary_bootstrap_indices(n, block, rng)) / n for _ in range(replications))
    low = draws[int(((1 - level) / 2) * replications)]
    high = draws[min(replications - 1, int((1 - (1 - level) / 2) * replications))]
    return {"difference": sum(diffs) / n, "low": low, "high": high, "excludes_zero": bool(high < 0 or low > 0)}


def report_command(args) -> int:
    # The judge's script is a sibling file, not a package module; load it by path.
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)

    from repo_model import pressure_judge as pj

    declared = committed_declaration(DECLARATION)
    declaration = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    by_date = {row.date: row for row in rows}
    digest = panel_sha256(args.panel)
    forecasts = []
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))

    def grids_of(items):
        out = {}
        for h in declaration.horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state={})
        return out

    calendar = [row.date for row in rows]
    chosen = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    grids = grids_of(chosen)
    tau = declaration.primary
    bootstrap = declaration.document()["bootstrap"]
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    table, union = {}, {}
    for name in sorted(by_name):
        per_horizon, flagged_any = {}, {}
        for h, forecast in sorted(by_name[name].items()):
            grid = grids[h]
            risk = [is_risk_date(splits, by_date[day].values, h) for day in grid.dates]
            outcomes, onset = grid.outcomes[tau], grid.onset_at(tau, tau)
            p = forecast.probabilities[tau]
            flags = [1 if q >= c else 0 for q, c in zip(p, forecast.cutoffs[tau])]
            if name.startswith("risk_") and any(f for f, r in zip(flags, risk) if not r):
                raise SystemExit(f"{name} h={h}: a flag on a day that is not a risk date")
            risk_idx = [k for k, r in enumerate(risk) if r]
            cell = {}
            for label, members in (("all_days", list(range(len(flags)))), ("risk_dates", risk_idx)):
                onsets = sum(onset[k] for k in members)
                caught = sum(flags[k] and onset[k] for k in members)
                false = sum(flags[k] and not outcomes[k] for k in members)
                cell[label] = {
                    "days": len(members),
                    "pressure_days": sum(outcomes[k] for k in members),
                    "onsets": onsets,
                    "onsets_flagged": caught,
                    "recall": caught / onsets if onsets else None,
                    "flags": sum(flags[k] for k in members),
                    "false_alarms": false,
                    "false_alarms_per_onset": false / onsets if onsets else None,
                }
            cell["onsets_on_risk_dates_share"] = (
                cell["risk_dates"]["onsets"] / cell["all_days"]["onsets"] if cell["all_days"]["onsets"] else None
            )
            y = [outcomes[k] for k in risk_idx]
            clim = [by_name[declaration.climatology][h].probabilities[tau][k] for k in risk_idx]
            pers = [by_name[declaration.persistence][h].probabilities[tau][k] for k in risk_idx]
            pr = [p[k] for k in risk_idx]
            cell["risk_date_scores"] = {
                "brier": _brier(pr, y),
                "brier_calendar_climatology": _brier(clim, y),
                "brier_persistence_logistic": _brier(pers, y),
                "auroc": _auroc(pj, pr, y),
                "auroc_calendar_climatology": _auroc(pj, clim, y),
            }
            if name.startswith("risk_"):
                seed = bootstrap["seed"] * 1000 + h
                pairs = {"vs_calendar_climatology": clim, "vs_persistence_logistic": pers}
                twin = by_name.get(name + TWIN_SUFFIX) if not name.endswith(TWIN_SUFFIX) else None
                if twin:
                    pairs["vs_twin_without_new_inputs"] = [twin[h].probabilities[tau][k] for k in risk_idx]
                cell["risk_date_paired_brier"] = {
                    key: _paired(seed, pr, other, y, bootstrap["block_length"], bootstrap["replications"], bootstrap["level"])
                    for key, other in pairs.items()
                }
            per_horizon[str(h)] = cell
            for k, day in enumerate(grid.dates):
                if onset[k]:
                    flagged_any[day] = flagged_any.get(day, False) or bool(flags[k])
        table[name] = per_horizon
        total = len(flagged_any)
        union[name] = {
            "onsets_seen_at_some_lead": total,
            "flagged_at_some_lead_1_to_5": sum(flagged_any.values()),
            "recall_at_some_lead": sum(flagged_any.values()) / total if total else None,
        }
    document = {"declaration": declared, "per_lead": table, "any_lead": union, "cutoff_rule": declaration.document()["cutoff_rule"]}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("| model | " + " | ".join(f"h={h} all / risk dates" for h in declaration.horizons) + " |")
    print("|---|" + "---|" * len(declaration.horizons))
    for name in sorted(table):
        cells = []
        for h in declaration.horizons:
            c = table[name][str(h)]

            def part(x):
                return f"{x['onsets_flagged']}/{x['onsets']}, {x['false_alarms_per_onset']:.2f}" if x["onsets"] else "-"

            cells.append(f"{part(c['all_days'])} / {part(c['risk_dates'])}")
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
    report = commands.add_parser("report", help="the judge's reading on all days and on the risk dates alone")
    report.add_argument("--panel", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("inputs", nargs="+", type=Path)
    report.set_defaults(handler=report_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
