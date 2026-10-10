"""Refit the tier-1 passers with inputs the repository already holds (#477, track U of #374).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing
into `docs/runs/`. The groups, the five passers and the fifteen candidates are in
`metadata/unused_inputs.json`, which this script refuses to read unless it is committed and unchanged, and each
candidate in a file of its own under `metadata/pressure_judge/candidates/`. Every column is off in every published
declaration and switched on for these runs only.

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/fed_liquidity.py panel --panel AUG3.csv --output AUG4.csv
    PYTHONPATH=src python3 scripts/policy_features.py panel --panel AUG4.csv --output AUG5.csv
    PYTHONPATH=src python3 scripts/unused_inputs.py inventory --output OUT/inventory.md
    for h in 1 2 3 4 5:
      PYTHONPATH=src python3 scripts/unused_inputs.py run --panel AUG5.csv --published PUBLISHED.csv \\
          --horizon $h --output OUT/unused_h$h.json
      PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published \\
          --output OUT/bench_h$h.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/bench_h?.json OUT/unused_h?.json
    PYTHONPATH=src python3 scripts/unused_inputs.py report --panel PUBLISHED.csv --output OUT/paired.json \\
        --markdown OUT/paired.md OUT/bench_h?.json OUT/unused_h?.json

* `inventory` lists each collected input: whether it is a column of the published panel, its as-of availability
  (the registry's release lag), and the declared candidates that read it today.
* `run` fits the five passers (the controls) and the fifteen candidates on the risk-date label days of the shared
  fold grid, walk-forward at +5 and +10 bp, days before 2026-01-01 only, in the judge's `forecasts` shape.
* `report` pairs each candidate with its passer (Brier difference with a stationary-bootstrap interval) on all
  days, by regime and by pressure-day type, and gives the +5 bp onset recall by year at each lead and at some
  lead 1 to 5, under the judge's own cut-offs.
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

from repo_model import contract, fed_liquidity, measurement_fields, ml, net_settlement, policy_features  # noqa: E402
from repo_model import pressure_judge as pj, scarcity  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


risk = _script("risk_date_severity")

SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECLARATION = REPO / "metadata" / "unused_inputs.json"
RISK_DECLARATION = REPO / "metadata" / "risk_date_severity.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"


def committed_declaration(path: Path) -> dict:
    return risk.committed_declaration(path)


def all_column_fields() -> dict:
    """Every scratch column's source fields: #377's, the net settlement, the Fed repo (both readings) and the register."""

    return {
        **measurement_fields.COLUMN_FIELDS,
        **net_settlement.COLUMN_FIELDS,
        **fed_liquidity.ALL_COLUMN_FIELDS,
        **policy_features.COLUMN_FIELDS,
    }


@contextlib.contextmanager
def switched_on():
    """The scarcity state and every scratch column in the feature map, for this run only."""

    fields = all_column_fields()
    with scarcity.measurement_declaration(), mock.patch.multiple(
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


def candidate_features(declared: dict, risk_declared: dict, name: str, horizon: int) -> tuple:
    """The inputs of a passer or of one of its groups' candidates at `horizon`."""

    if name in declared["candidates"]:
        entry = declared["candidates"][name]
        passer, extra = entry["passer"], declared["groups"][entry["group"]]["columns"]
    else:
        passer, extra = name, []
    base = risk.features_at_horizon(risk_declared, risk_declared["candidates"][passer], horizon)
    return tuple(dict.fromkeys(list(base) + list(extra)))


def run_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    risk_declared = committed_declaration(RISK_DECLARATION)
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="unused_inputs")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = declared["scoring"]["minimum_history"]
    passers = sorted({entry["passer"] for entry in declared["candidates"].values()})
    names = [args.candidate] if args.candidate else passers + list(declared["candidates"])
    forecasts, settings, failed = {}, {}, {}
    for name in names:
        kind = risk_declared["candidates"][declared["candidates"].get(name, {"passer": name})["passer"]]["kind"]
        features = candidate_features(declared, risk_declared, name, h)
        predictor = ml.pressure_risk_date_exceedance(kind, features, splits, minimum_history=minimum)
        try:
            with switched_on():
                report = rolling_exceedance_backtest(
                    rows, predictor=predictor, model_name=name, features=features, registry=registry,
                    decision_time=time.fromisoformat(declared["scoring"]["decision_time"]),
                    taus=taus, minimum_history=minimum, refit_every=declared["scoring"]["refit_every"],
                    end=last, horizon=h,
                )
        except (ValueError, TypeError) as error:
            # A fit that the solver cannot complete (the skew-t quantile regression's linear program on
            # unscaled inputs, for one) is recorded as a failure of that candidate, not as a score.
            failed[name] = f"{type(error).__name__}: {error}"
            print(json.dumps({"horizon": h, "candidate": name, "failed": failed[name]}), flush=True)
            continue
        forecasts[name] = risk.column(report)
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
        "failed": failed,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def prune_command(args) -> int:
    """Drop, from every horizon's file, a candidate whose fit failed at any horizon (the judge needs all five)."""

    documents = [json.loads(Path(path).read_text()) for path in args.inputs]
    dropped = sorted({name for d in documents for name in d.get("failed", {})})
    for path, document in zip(args.inputs, documents):
        for name in dropped:
            document["forecasts"].pop(name, None)
            document["declarations"].pop(name, None)
        out = args.directory / Path(path).name.replace("unused_", "pruned_")
        out.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"dropped": {name: {str(d["horizon"]): d["failed"][name] for d in documents if name in d.get("failed", {})}
                                  for name in dropped}}, indent=1))
    return 0


# -- the inventory ---------------------------------------------------------------


def candidate_users(column: str) -> list:
    users = []
    for path in sorted(CANDIDATES.glob("*.json")):
        entry = json.loads(path.read_text(encoding="utf-8"))
        if column in entry.get("features", []) and entry.get("track") != "U (#477)":
            users.append(path.stem)
    return users


def _lag(registry: dict, source: str) -> str:
    lag = registry.get(source, {}).get("release_lag") or {}
    if not lag:
        return "none declared"
    if "days" not in lag:
        return str(lag.get("basis", "?"))
    unit = "business day" if lag.get("unit") == "business_days" else "calendar day"
    return f"{lag['days']} {unit}{'' if lag['days'] == 1 else 's'} after the {lag.get('basis', '?')} at {lag.get('available_time', '?')}"


def inventory_rows() -> list:
    """One row per collected column: (column, sources, in published panel, as-of availability, users)."""

    registry = measurement_fields.load_registry()
    published = set(contract.FEATURE_FIELDS)
    fields = {**contract.FEATURE_FIELDS, **all_column_fields()}
    rows = []
    for column in sorted(fields):
        sources = sorted({source for source, _f in fields[column]})
        users = candidate_users(column)
        rows.append(
            {
                "column": column,
                "sources": sources,
                "published_declaration": column in published,
                "availability": "; ".join(f"{s}: {_lag(registry, s)}" for s in sources),
                "users": users,
            }
        )
    return rows


def inventory_markdown(declared: dict) -> str:
    rows = inventory_rows()
    new_columns = {c for g in declared["groups"].values() for c in g["columns"]}
    out = [
        "| input | source | in the published feature map | as-of availability | declared candidates reading it today |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        users = r["users"]
        shown = ", ".join(users[:6]) + (f" and {len(users) - 6} more" if len(users) > 6 else "") if users else "none"
        out.append(
            f"| `{r['column']}`{' (this directive)' if r['column'] in new_columns else ''} | {', '.join(r['sources'])} | "
            f"{'yes' if r['published_declaration'] else 'no'} | {r['availability']} | {shown} |"
        )
    return "\n".join(out) + "\n"


def inventory_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    text = inventory_markdown(declared)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


# -- the report ------------------------------------------------------------------


def _interval(diffs, seed, block, replications, level):
    n = len(diffs)
    if n == 0:
        return None
    rng = random.Random(seed)
    draws = sorted(sum(diffs[i] for i in stationary_bootstrap_indices(n, block, rng)) / n for _ in range(replications))
    low = draws[int(((1 - level) / 2) * replications)]
    high = draws[min(replications - 1, int((1 - (1 - level) / 2) * replications))]
    return {"difference": sum(diffs) / n, "low": low, "high": high, "days": n}


def report_command(args) -> int:
    declared = committed_declaration(DECLARATION)
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
    boot = declaration.document()["bootstrap"]
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast

    def flags_of(name, h):
        f = by_name[name][h]
        return [1 if q >= c else 0 for q, c in zip(f.probabilities[tau], f.cutoffs[tau])]

    def recall_by_year(name):
        """+5 bp onset recall by calendar year: at each lead, and at some lead 1 to 5."""

        per_lead, any_lead = {}, {}
        for h in declaration.horizons:
            grid, flags = grids[h], flags_of(name, h)
            for k, day in enumerate(grid.dates):
                if grid.onset[k]:
                    cell = per_lead.setdefault(h, {}).setdefault(day.year, [0, 0])
                    cell[1] += 1
                    cell[0] += flags[k]
                    seen = any_lead.setdefault(day, False)
                    any_lead[day] = seen or bool(flags[k])
        by_year = {}
        for day, hit in any_lead.items():
            cell = by_year.setdefault(day.year, [0, 0])
            cell[1] += 1
            cell[0] += int(hit)
        return {"per_lead": {str(h): {str(y): c for y, c in sorted(v.items())} for h, v in per_lead.items()},
                "any_lead": {str(y): c for y, c in sorted(by_year.items())}}

    def totals(name, h):
        grid, flags = grids[h], flags_of(name, h)
        onsets = sum(grid.onset)
        caught = sum(f and o for f, o in zip(flags, grid.onset))
        false = sum(f and not y for f, y in zip(flags, grid.outcomes[tau]))
        return {"onsets": onsets, "flagged": caught, "false_alarms": false,
                "false_alarms_per_onset": false / onsets if onsets else None}

    result = {"declaration": declared, "paired": {}, "onsets": {}, "recall_by_year": {}}
    for name, entry in declared["candidates"].items():
        control = entry["passer"]
        result["paired"][name] = {"control": control, "horizons": {}}
        for h in declaration.horizons:
            grid = grids[h]
            outcomes = grid.outcomes[tau]
            p, q = by_name[name][h].probabilities[tau], by_name[control][h].probabilities[tau]
            diffs = [(a - o) ** 2 - (b - o) ** 2 for a, b, o in zip(p, q, outcomes)]
            seed = boot["seed"] * 1000 + h
            cell = {"all": _interval(diffs, seed, boot["block_length"], boot["replications"], boot["level"])}
            for dimension in ("regime", "day_type"):
                parts = {}
                for label in sorted(set(grid.groups[dimension])):
                    members = [k for k, g in enumerate(grid.groups[dimension]) if g == label]
                    parts[label] = _interval([diffs[k] for k in members], seed, boot["block_length"],
                                             boot["replications"], boot["level"])
                cell[dimension] = parts
            result["paired"][name]["horizons"][str(h)] = cell
            result["onsets"].setdefault(name, {})[str(h)] = totals(name, h)
            result["onsets"].setdefault(control, {})[str(h)] = totals(control, h)
        result["recall_by_year"][name] = recall_by_year(name)
        result["recall_by_year"][control] = recall_by_year(control)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(report_markdown(result, declaration.horizons), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _fmt(cell):
    if not cell:
        return "-"
    star = " *" if cell["high"] < 0 or cell["low"] > 0 else ""
    return f"{cell['difference']:+.4f} [{cell['low']:+.4f}, {cell['high']:+.4f}]{star}"


def report_markdown(result: dict, horizons) -> str:
    out = ["Paired Brier difference, candidate minus its passer, +5 bp, all scored days (negative favours the candidate; "
           "90% stationary-bootstrap interval; * = interval excludes zero).", "",
           "| candidate | " + " | ".join(f"h={h}" for h in horizons) + " |", "|---|" + "---|" * len(horizons)]
    for name, entry in sorted(result["paired"].items()):
        out.append(f"| {name} | " + " | ".join(_fmt(entry["horizons"][str(h)]["all"]) for h in horizons) + " |")
    for dimension in ("regime", "day_type"):
        out += ["", f"By {dimension}, h = 1:", ""]
        labels = sorted({label for e in result["paired"].values() for label in e["horizons"]["1"][dimension]})
        out += ["| candidate | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
        for name, entry in sorted(result["paired"].items()):
            parts = entry["horizons"]["1"][dimension]
            out.append(f"| {name} | " + " | ".join(_fmt(parts.get(label)) for label in labels) + " |")
    years = sorted({y for r in result["recall_by_year"].values() for y in r["any_lead"]})
    out += ["", "+5 bp onsets flagged / onsets at some lead 1 to 5, by year, under the judge's cut-offs:", "",
            "| model | " + " | ".join(years) + " | all |", "|---|" + "---|" * (len(years) + 1)]
    for name, r in sorted(result["recall_by_year"].items()):
        cells = [f"{r['any_lead'][y][0]}/{r['any_lead'][y][1]}" if y in r["any_lead"] else "-" for y in years]
        flagged = sum(c[0] for c in r["any_lead"].values())
        total = sum(c[1] for c in r["any_lead"].values())
        out.append(f"| {name} | " + " | ".join(cells) + f" | {flagged}/{total} |")
    out += ["", "+5 bp onsets flagged / onsets at lead 1, false alarms per onset (all days):", "",
            "| model | " + " | ".join(f"h={h}" for h in horizons) + " |", "|---|" + "---|" * len(horizons)]
    for name, cell in sorted(result["onsets"].items()):
        out.append(f"| {name} | " + " | ".join(
            f"{cell[str(h)]['flagged']}/{cell[str(h)]['onsets']}, {cell[str(h)]['false_alarms_per_onset']:.2f}" for h in horizons) + " |")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory")
    inventory.add_argument("--output", type=Path)
    inventory.set_defaults(handler=inventory_command)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--horizon", type=int, required=True)
    run.add_argument("--candidate")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_command)
    prune = commands.add_parser("prune", help="drop a candidate that failed to fit at any horizon")
    prune.add_argument("--directory", type=Path, required=True)
    prune.add_argument("inputs", nargs="+", type=Path)
    prune.set_defaults(handler=prune_command)
    report = commands.add_parser("report")
    report.add_argument("--panel", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--markdown", type=Path)
    report.add_argument("inputs", nargs="+", type=Path)
    report.set_defaults(handler=report_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
