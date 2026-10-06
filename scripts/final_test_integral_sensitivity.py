"""The final test's primary cell, re-scored with the trapezoid CRPS (#259): reported only.

The final test's score is `metrics.crps_from_quantiles`, the unweighted mean of
five pinball losses. It is a fixed score and not the CRPS integral. The
independent review's rule for that integral is `metrics.crps_trapezoid_from_quantiles`
(trapezoid weights between the declared levels, constant tails). This script
scores the same frozen paired comparison with it, once, and publishes the
result as a new record beside `docs/runs/final_test_near_blind.json`:

    PYTHONPATH=src python3 scripts/final_test_integral_sensitivity.py compare PUB.csv --report OUT/integral.json
    PYTHONPATH=src python3 scripts/final_test_integral_sensitivity.py assemble OUT/integral.json \\
        --output docs/runs/final_test_near_blind_integral_sensitivity.json

`compare` runs the frozen command (`final_test_preregistration.CRPS_COMMAND`)
with its loss swapped for the trapezoid one, injected here at run time. The
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

LOSS_KEY = "crps-integral"
STATISTIC = "crps_integral"
RECORD_NAME = "final_test_near_blind_integral_sensitivity.json"
PRIMARY_RECORD = "docs/runs/final_test_near_blind.json"
RULE = ("the trapezoid rule: the quantile loss is linear between the declared levels and constant "
        "beyond the lowest and highest, and the score is twice its integral over (0, 1) "
        "(`metrics.crps_trapezoid_from_quantiles`)")
SIGN = ("persistence minus the published distribution, both by the trapezoid CRPS; positive "
        "favours the published distribution")


def _integral_at(fitted, feature_row, actual):
    levels = tuple(fitted.levels)
    if levels != tuple(QUANTILE_LEVELS):
        raise ValueError(f"the fitted model reports quantile levels {levels}, not the contract's")
    return metrics.crps_trapezoid_from_quantiles(levels, fitted.predict(feature_row), actual)


def command() -> list:
    """The frozen command with its loss swapped; nothing else differs."""

    argv = list(fp.CRPS_COMMAND)
    argv[argv.index("--loss") + 1] = LOSS_KEY
    return argv


def compare_command(args) -> int:
    losses = dict(baseline.COMPARISON_LOSSES)
    losses[LOSS_KEY] = baseline._ComparisonLoss(f"{STATISTIC}_bps", STATISTIC, _integral_at)
    patched = baseline.MappingProxyType(losses)
    baseline.COMPARISON_LOSSES = patched
    cli_eval.COMPARISON_LOSSES = patched
    argv = command()
    argv[1] = str(args.panel)
    argv[argv.index("--report") + 1] = str(args.report)
    return cli.main(argv)


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


def cell(compare: dict) -> dict:
    """The sensitivity cell, from the swapped-loss report's window days."""

    frozen = fp.crps_declaration()
    declared = compare["declaration"]
    for key in ("model_a", "model_b", "minimum_history", "refit_every", "decision_time", "end"):
        if declared.get(key) != frozen[key]:
            raise ValueError(f"the report's {key} is not the frozen CRPS test's")
    if compare["comparison"].get("loss") != f"{STATISTIC}_bps":
        raise ValueError("the report's loss is not the trapezoid CRPS")
    if compare["panel"]["sha256"] != frozen["panel_sha256"]:
        raise ValueError("the report was not scored on the published panel")
    inside = window(compare)
    if len(inside) != fp.CRPS_WINDOW_DAYS:
        raise ValueError(f"the report scores {len(inside)} window days, not {fp.CRPS_WINDOW_DAYS}")
    differences = [float(entry["difference_bps"]) for entry in inside]
    sensitivity = frozen["sensitivity_interval"]
    return {
        "cell": "crps, h = 1, trapezoid",
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


def assemble_command(args) -> int:
    compare = json.loads(args.report.read_text(encoding="utf-8"))
    primary = json.loads((REPO / PRIMARY_RECORD).read_text(encoding="utf-8"))
    document = {
        "directive": "#259",
        "record": "the final test's primary cell, re-scored with the trapezoid CRPS: reported only, "
                  "decides nothing",
        "primary_record": PRIMARY_RECORD,
        "rule": RULE,
        "crps_declaration_sha256": fp.crps_declaration_checksum(),
        "primary_cell_by_the_plain_score": {
            key: primary["primary"]["cell"][key]
            for key in ("crps_persistence_bps", "crps_published_bps", "mean_difference_bps", "days")
        },
        "command": command(),
        "cell": cell(compare),
        "window_per_origin": [
            {key: entry[key] for key in ("scored_date", "loss_a_bps", "loss_b_bps", "difference_bps")}
            for entry in window(compare)
        ],
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: document["cell"][key] for key in
                      ("days", "mean_difference_bps", "interval", "sensitivity_interval")}, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="step", required=True)
    one = sub.add_parser("compare")
    one.add_argument("panel", type=Path)
    one.add_argument("--report", type=Path, required=True)
    one.set_defaults(run=compare_command)
    two = sub.add_parser("assemble")
    two.add_argument("report", type=Path)
    two.add_argument("--output", type=Path, default=REPO / "docs" / "runs" / RECORD_NAME)
    two.set_defaults(run=assemble_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
