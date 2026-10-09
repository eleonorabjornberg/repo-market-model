"""Track X of #374 (#410): the stacked ensemble of the track forecasts, for the judge.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it
is given and nothing into `docs/runs/`. The members, the stacking form, its
penalty, refit blocks and fallback are in `metadata/pressure_stack.json`, which
this script refuses to read unless it is committed and unchanged; the stack and
its equal-average comparison are candidates in `metadata/pressure_judge.json`.

    PYTHONPATH=src python3 scripts/pressure_stack.py forecasts --panel PUB.csv --horizon H \\
        --output OUT/stack_hH.json MEMBER_FILE_H ...
    PYTHONPATH=src python3 scripts/pressure_stack.py weights --output OUT/weights.md OUT/stack_h1.json ...

`forecasts` reads the members' walk-forward probabilities (the files
`pressure_judge.py forecasts` and each track's script write, one or more per file;
the members are picked out by name), checks that they share their scored days
and that none is after the declared last scored day, and writes the stack's and
the equal average's probabilities at +5 and +10 bp in the shape the judge reads.
A member file scored on another panel than `--panel` is accepted only when
`--scratch-panel` names that panel (a panel that adds columns to the published
one; the dates are checked to be the grid's, as the re-judge of #407 did).
`weights` reports, per horizon and threshold, the mean fitted weights.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj, stacking  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _members(declaration, paths, digests, horizon, last_day):
    found = {}
    for path in paths:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        if document["panel_sha256"] not in digests:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        if int(document["horizon"]) != horizon:
            raise SystemExit(f"{path} is horizon {document['horizon']}, not {horizon}")
        for forecast in pj.forecasts_from_horizon_document(document):
            if forecast.name in declaration.members:
                if forecast.name in found:
                    raise SystemExit(f"member {forecast.name!r} appears in two files")
                found[forecast.name] = forecast
    missing = [name for name in declaration.members if name not in found]
    if missing:
        raise SystemExit(f"members missing from the files given: {missing}")
    dates = {found[name].dates for name in declaration.members}
    if len(dates) != 1:
        raise SystemExit("the members do not share their scored days")
    days = next(iter(dates))
    if days[-1] > last_day:
        raise ValueError(f"member days run to {days[-1]}, after the declared last scored day {last_day}")
    for name in declaration.members:
        for tau in declaration.thresholds:
            if tau not in found[name].probabilities:
                raise SystemExit(f"member {name!r} has no probabilities at {tau:g} bp")
    return found, days


def forecasts_command(args) -> int:
    declaration = stacking.load_declaration()
    stack_commit = _judge_script().require_committed_declaration(stacking.DEFAULT_DECLARATION)
    judge = pj.load_declaration()
    if judge.thresholds != declaration.thresholds:
        raise ValueError("the stack's thresholds are not the judge's")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    digest = panel_sha256(args.panel)
    accepted = {digest} | ({panel_sha256(args.scratch_panel)} if args.scratch_panel else set())
    found, days = _members(declaration, args.files, accepted, args.horizon, judge.last_day)
    by_date = {row.date: row for row in rows}
    calendar = [row.date for row in rows]
    probabilities, equal, trace = {}, {}, {}
    for tau in declaration.thresholds:
        members = {name: found[name].probabilities[tau] for name in declaration.members}
        outcomes = [int(exceeds_bp(by_date[day].spread_bps, tau)) for day in days]
        result = stacking.stack(
            days, calendar, members, outcomes, horizon=args.horizon, step=declaration.step,
            ridge=declaration.ridge, clip=declaration.clip, fallback=declaration.fallback,
            iterations=declaration.iterations, tolerance=declaration.tolerance,
        )
        probabilities[tau] = result.probabilities
        equal[tau] = stacking.equal_average(members)
        trace[f"{tau:g}"] = list(result.trace)
    forecasts = [
        pj.Forecast(name=declaration.candidate, horizon=args.horizon, dates=days, probabilities=probabilities),
        pj.Forecast(name=declaration.comparison, horizon=args.horizon, dates=days, probabilities=equal),
    ]
    document = _judge_script()._document(args.horizon, digest, forecasts)
    document["declaration_commit"] = stack_commit
    document["stack"] = {"members": list(declaration.members), "refits": trace}
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "days": len(days), "output": str(args.output)}))
    return 0


def weights_command(args) -> int:
    lines = [
        "| h | threshold | refits fitted / equal | " + " | ".join(stacking.load_declaration().members) + " | mean intercept |",
        "|---|---|---|" + "---|" * (len(stacking.load_declaration().members) + 1),
    ]
    for path in args.files:
        document = json.loads(path.read_text(encoding="utf-8"))
        for tau, refits in sorted(document["stack"]["refits"].items(), key=lambda kv: float(kv[0])):
            fitted = [r for r in refits if r["mode"] == "fitted"]
            if fitted:
                means = [sum(r["weights"][j] for r in fitted) / len(fitted) for j in range(len(fitted[0]["weights"]))]
                intercept = sum(r["intercept"] for r in fitted) / len(fitted)
                cells = " | ".join(f"{m:.2f}" for m in means) + f" | {intercept:+.2f}"
            else:
                cells = " | ".join("–" for _ in document["stack"]["members"]) + " | –"
            lines.append(f"| {document['horizon']} | +{tau} bp | {len(fitted)} / {len(refits) - len(fitted)} | {cells} |")
    text = "\n".join(lines) + "\n"
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    forecasts = commands.add_parser("forecasts")
    forecasts.add_argument("--panel", type=Path, required=True)
    forecasts.add_argument("--scratch-panel", type=Path)
    forecasts.add_argument("--horizon", type=int, required=True)
    forecasts.add_argument("--output", type=Path, required=True)
    forecasts.add_argument("files", type=Path, nargs="+")
    forecasts.set_defaults(run=forecasts_command)
    weights = commands.add_parser("weights")
    weights.add_argument("--output", type=Path, required=True)
    weights.add_argument("files", type=Path, nargs="+")
    weights.set_defaults(run=weights_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
