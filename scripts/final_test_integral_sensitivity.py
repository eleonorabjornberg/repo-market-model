"""The final test's primary cell, re-scored with integral rules for the CRPS (#259): reported only.

The final test's score is `metrics.crps_from_quantiles`, the unweighted mean of
five pinball losses. It is a fixed score and not the CRPS integral. This script
scores the same frozen paired comparison under three rules for that integral, once
each, and publishes the result as a new record beside `docs/runs/final_test_near_blind.json`.
The rules, with the equal-weight primary as the fourth row, are:

- `trapezoid`: cell-width weights (0.15, 0.225, 0.25, 0.225, 0.15) times two, flat tails
  (`metrics.crps_trapezoid_from_quantiles`);
- `exact-flat`: the integral of the piecewise-linear quantile function, flat tails;
- `exact-linear`: the same, with the end segments extended linearly to 0 and 1
  (`metrics.crps_piecewise_linear_from_quantiles`).

    PYTHONPATH=src python3 scripts/final_test_integral_sensitivity.py compare PUB.csv --report OUT/trapezoid.json
    PYTHONPATH=src python3 scripts/final_test_integral_sensitivity.py assemble OUT/trapezoid.json \\
        OUT/trapezoid-exact-flat.json OUT/trapezoid-exact-linear.json --output docs/runs/final_test_near_blind_integral_sensitivity.json

`compare` runs the frozen command (`final_test_preregistration.CRPS_COMMAND`)
with its loss swapped for the trapezoid one, injected here at run time. The same pass records each
scored quantile vector and writes the two exact rules' reports beside it, so every rule scores
identical vectors. The
frozen declaration hashes `baseline.COMPARISON_LOSSES`, so the loss is not added
to that module: the pre-registered primary test is unchanged, and the declaration
checksum is the one the published record carries.

The record decides nothing. Its intervals are the primary cell's: the same seeds
and block lengths (`CRPS_BLOCK_LENGTH`, `CRPS_SENSITIVITY_BLOCK_LENGTH`), on the
same 169 window days.
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

from repo_model import baseline, cli, cli_eval, metrics  # noqa: E402
from repo_model.contract import QUANTILE_LEVELS  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(f"sensitivity_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fp = _script("final_test_preregistration")

RULES = {
    "trapezoid": {
        "loss_key": "crps-integral", "statistic": "crps_integral",
        "label": "cell-width trapezoid, flat tails",
        "rule": "the trapezoid rule: the quantile loss is linear between the declared levels and constant "
                "beyond the lowest and highest, so the weights are the cell widths (0.15, 0.225, 0.25, 0.225, "
                "0.15) and the score is twice the weighted sum (`metrics.crps_trapezoid_from_quantiles`)",
    },
    "exact-flat": {
        "loss_key": "crps-exact-flat", "statistic": "crps_exact_flat",
        "label": "exact piecewise-linear, flat tails",
        "rule": "twice the exact integral of the quantile loss for the piecewise-linear quantile function, "
                "the end quantiles held beyond the lowest and highest levels "
                "(`metrics.crps_piecewise_linear_from_quantiles`, tails flat)",
    },
    "exact-linear": {
        "loss_key": "crps-exact-linear", "statistic": "crps_exact_linear",
        "label": "exact piecewise-linear, linear tails",
        "rule": "as exact-flat, with the end segments' lines extended to 0 and 1 "
                "(`metrics.crps_piecewise_linear_from_quantiles`, tails linear)",
    },
}
RECORD_NAME = "final_test_near_blind_integral_sensitivity.json"
PRIMARY_RECORD = "docs/runs/final_test_near_blind.json"
SIGN = ("persistence minus the published distribution, both by the rule named; positive "
        "favours the published distribution")
FUNCTIONS = {
    "trapezoid": metrics.crps_trapezoid_from_quantiles,
    "exact-flat": lambda levels, quantiles, actual: metrics.crps_piecewise_linear_from_quantiles(
        levels, quantiles, actual, tails="flat"),
    "exact-linear": lambda levels, quantiles, actual: metrics.crps_piecewise_linear_from_quantiles(
        levels, quantiles, actual, tails="linear"),
}


def _recording_loss(calls):
    """The trapezoid loss, recording every vector it scores so one pass yields all three rules."""

    def at(fitted, feature_row, actual):
        levels = tuple(fitted.levels)
        if levels != tuple(QUANTILE_LEVELS):
            raise ValueError(f"the fitted model reports quantile levels {levels}, not the contract's")
        quantiles = fitted.predict(feature_row)
        calls.append({rule: score(levels, quantiles, actual) for rule, score in FUNCTIONS.items()})
        return calls[-1]["trapezoid"]

    return at


def command(rule="trapezoid") -> list:
    """The frozen command with its loss swapped; nothing else differs."""

    argv = list(fp.CRPS_COMMAND)
    argv[argv.index("--loss") + 1] = RULES[rule]["loss_key"]
    return argv


def _pair(calls, per_origin):
    """The calls' scores per origin, as (persistence, published), by matching the trapezoid values.

    The walk may score the two models interleaved or one after the other; the order that
    reproduces every origin's reported losses is the one used, and none matching is an error.
    """

    n = len(per_origin)
    if len(calls) != 2 * n:
        raise ValueError(f"{len(calls)} scored vectors for {n} origins")
    layouts = {
        "interleaved, persistence first": [(calls[2 * i], calls[2 * i + 1]) for i in range(n)],
        "interleaved, published first": [(calls[2 * i + 1], calls[2 * i]) for i in range(n)],
        "persistence block first": [(calls[i], calls[n + i]) for i in range(n)],
        "published block first": [(calls[n + i], calls[i]) for i in range(n)],
    }
    for pairs in layouts.values():
        if all(abs(a["trapezoid"] - float(o["loss_a_bps"])) < 1e-9 and abs(b["trapezoid"] - float(o["loss_b_bps"])) < 1e-9
               for (a, b), o in zip(pairs, per_origin)):
            return pairs
    raise ValueError("the scored vectors do not reproduce the report's trapezoid losses in any order")


def compare_command(args) -> int:
    calls = []
    losses = dict(baseline.COMPARISON_LOSSES)
    spec = RULES["trapezoid"]
    losses[spec["loss_key"]] = baseline._ComparisonLoss(
        f"{spec['statistic']}_bps", spec["statistic"], _recording_loss(calls))
    patched = baseline.MappingProxyType(losses)
    baseline.COMPARISON_LOSSES = patched
    cli_eval.COMPARISON_LOSSES = patched
    argv = command("trapezoid")
    argv[1] = str(args.panel)
    argv[argv.index("--report") + 1] = str(args.report)
    status = cli.main(argv)
    if status:
        return status
    report = json.loads(args.report.read_text(encoding="utf-8"))
    per_origin = report["comparison"]["per_origin"]
    pairs = _pair(calls, per_origin)
    for rule in ("exact-flat", "exact-linear"):
        extra = json.loads(json.dumps(report))
        extra["comparison"]["loss"] = f"{RULES[rule]['statistic']}_bps"
        for entry, (a, b) in zip(extra["comparison"]["per_origin"], pairs):
            entry["loss_a_bps"], entry["loss_b_bps"] = a[rule], b[rule]
            entry["difference_bps"] = a[rule] - b[rule]
        args.report.with_name(f"{args.report.stem}-{rule}.json").write_text(
            json.dumps(extra, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def window(compare: dict) -> list:
    return [entry for entry in compare["comparison"]["per_origin"]
            if fp.CRPS_FIRST <= date.fromisoformat(entry["scored_date"]) <= fp.CRPS_LAST]


def interval(differences, block_length, seed):
    def mean_difference(indices):
        return sum(differences[i] for i in indices) / len(indices)

    lower, upper = metrics.stationary_bootstrap_interval(
        mean_difference, len(differences), block_length=block_length, seed=seed,
        replications=baseline.BOOTSTRAP_REPLICATIONS, level=baseline.BOOTSTRAP_LEVEL,
    )
    return {"lower": lower, "upper": upper, "level": baseline.BOOTSTRAP_LEVEL,
            "replications": baseline.BOOTSTRAP_REPLICATIONS, "block_length": block_length,
            "seed": seed, "method": "stationary_bootstrap"}


def cell(compare: dict, rule="trapezoid") -> dict:
    """The sensitivity cell, from the swapped-loss report's window days."""

    statistic = RULES[rule]["statistic"]

    frozen = fp.crps_declaration()
    declared = compare["declaration"]
    for key in ("model_a", "model_b", "minimum_history", "refit_every", "decision_time", "end"):
        if declared.get(key) != frozen[key]:
            raise ValueError(f"the report's {key} is not the frozen CRPS test's")
    if compare["comparison"].get("loss") != f"{statistic}_bps":
        raise ValueError(f"the report's loss is not the {rule} rule's")
    if compare["panel"]["sha256"] != frozen["panel_sha256"]:
        raise ValueError("the report was not scored on the published panel")
    inside = window(compare)
    if len(inside) != fp.CRPS_WINDOW_DAYS:
        raise ValueError(f"the report scores {len(inside)} window days, not {fp.CRPS_WINDOW_DAYS}")
    differences = [float(entry["difference_bps"]) for entry in inside]
    sensitivity = frozen["sensitivity_interval"]
    return {
        "cell": f"crps, h = 1, {RULES[rule]['label']}",
        "rule": RULES[rule]["rule"],
        "role": "reported only",
        "horizon": fp.CRPS_HORIZON,
        "days": len(inside),
        "first": inside[0]["scored_date"],
        "last": inside[-1]["scored_date"],
        "crps_integral_persistence_bps": sum(float(e["loss_a_bps"]) for e in inside) / len(inside),
        "crps_integral_published_bps": sum(float(e["loss_b_bps"]) for e in inside) / len(inside),
        "mean_difference_bps": sum(differences) / len(differences),
        "interval": interval(differences, frozen["interval"]["block_length"], frozen["interval"]["seed"]),
        "sensitivity_interval": interval(differences, sensitivity["block_length"], sensitivity["seed"]),
        "sign_convention": SIGN,
    }


def _row(name, label, cell_):
    return {"rule": name, "label": label, "mean_difference_bps": cell_["mean_difference_bps"],
            "interval": cell_["interval"], "sensitivity_interval": cell_["sensitivity_interval"]}


def assemble_command(args) -> int:
    reports = {"trapezoid": args.trapezoid, "exact-flat": args.exact_flat, "exact-linear": args.exact_linear}
    compares = {rule: json.loads(path.read_text(encoding="utf-8")) for rule, path in reports.items()}
    primary = json.loads((REPO / PRIMARY_RECORD).read_text(encoding="utf-8"))
    cells = {rule: cell(compare, rule) for rule, compare in compares.items()}
    plain = primary["primary"]["cell"]
    rows = [{"rule": "equal-weights", "label": "equal weights (the primary score)",
             "mean_difference_bps": plain["mean_difference_bps"], "interval": plain["interval"],
             "sensitivity_interval": plain["sensitivity_interval"]}]
    rows += [_row(rule, RULES[rule]["label"], cells[rule]) for rule in RULES]
    document = {
        "directive": "#259",
        "record": "the final test's primary cell, re-scored with integral rules for the CRPS: reported only, "
                  "decides nothing",
        "primary_record": PRIMARY_RECORD,
        "rule": RULES["trapezoid"]["rule"],
        "rules": {rule: RULES[rule]["rule"] for rule in RULES},
        "crps_declaration_sha256": fp.crps_declaration_checksum(),
        "primary_cell_by_the_plain_score": {
            key: plain[key]
            for key in ("crps_persistence_bps", "crps_published_bps", "mean_difference_bps", "days")
        },
        "command": command(),
        "cell": cells["trapezoid"],
        "rows": rows,
        "other_rules": {
            rule: {"cell": cells[rule],
                   "window_per_origin": [
                       {key: entry[key] for key in ("scored_date", "loss_a_bps", "loss_b_bps", "difference_bps")}
                       for entry in window(compares[rule])]}
            for rule in ("exact-flat", "exact-linear")
        },
        "window_per_origin": [
            {key: entry[key] for key in ("scored_date", "loss_a_bps", "loss_b_bps", "difference_bps")}
            for entry in window(compares["trapezoid"])
        ],
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="step", required=True)
    one = sub.add_parser("compare")
    one.add_argument("panel", type=Path)
    one.add_argument("--report", type=Path, required=True)
    one.set_defaults(run=compare_command)
    two = sub.add_parser("assemble")
    two.add_argument("trapezoid", type=Path)
    two.add_argument("exact_flat", type=Path)
    two.add_argument("exact_linear", type=Path)
    two.add_argument("--output", type=Path, default=REPO / "docs" / "runs" / RECORD_NAME)
    two.set_defaults(run=assemble_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
