#!/usr/bin/env python3
"""Re-score every archived run record under the as-of rule, from its own declaration.

Directive 03 (#27) replaces every record scored under the earlier rule. This script
reads each record in `docs/runs/archive/pre-asof/`, rebuilds the `repo_model.cli`
command its `declaration` describes, adds `--refit-every`, and writes the new record
under the same file name to the output directory. Nothing about a model is typed
here: every flag comes from the archived declaration, so a re-scored record differs
from its predecessor only in the rule and the refit cadence.

The two pressure-probability benchmarks (`calendar-climatology` and
`persistence-logistic`) have no predecessor and are scored by name at the end, on
the thresholds the other exceedance records use. Every exceedance record is scored
with both benchmarks paired in (`--benchmark`), a benchmark's record with the other.

Standard library only. Jobs run in parallel, one process each.

    python3 scripts/rescore.py PANEL OUTDIR [--refit-every 21] [--jobs 4] [--only NAME ...]
    python3 scripts/rescore.py PANEL OUTDIR --dry-run     # print the commands
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "docs/runs/archive/pre-asof"
REGISTRY = "metadata/sources.json"
THRESHOLDS = "metadata/stress_thresholds.json"

#: Declaration keys and the flag each becomes, per side on `compare`.
SETTINGS = {
    "calibration": "--calibration",
    "calibration_share": "--calibration-share",
    "calibration_folds": "--calibration-folds",
    "spread_change_lags": "--spread-change-lags",
    "volatility_feature": "--volatility-feature",
    "arx_feature": "--arx-feature",
    "tail": "--tail",
    "regime_variable": "--regime-variable",
    "residual_window": "--residual-window",
}

#: Keys a declaration carries that are outputs or fixed by the thresholds file,
#: not flags.
DERIVED = {"features", "model", "decision_time", "minimum_history", "taus_bp",
           "twcrps_weights", "refit_every"}

#: The benchmarks scored by name, with the features each reads.
BENCHMARKS = {
    "exceedance_calendar_climatology.json": (
        "calendar-climatology",
        ["spread_bps", "treasury_settlement_coupons"],
    ),
    "exceedance_persistence_logistic.json": ("persistence-logistic", ["spread_bps"]),
}


class DeclarationError(RuntimeError):
    """A declaration carries a key this script cannot turn into a flag."""


def _side_flags(side, suffix=""):
    flags = []
    for key, value in sorted(side.items()):
        if key in DERIVED:
            continue
        if key not in SETTINGS:
            raise DeclarationError(f"no flag for declaration key {key!r}")
        flags += [SETTINGS[key] + suffix, str(value)]
    return flags


def command(name, record, panel, refit_every):
    """The CLI argument list that re-scores `record` under the as-of rule."""

    dec = record["declaration"]
    common = ["--registry", REGISTRY, "--decision-time", dec["decision_time"],
              "--minimum-history", str(dec["minimum_history"]),
              "--refit-every", str(refit_every)]
    if "model_a" in dec:
        args = ["compare", panel] + common
        for side, suffix in (("model_a", "-a"), ("model_b", "-b")):
            args += ["--model" + suffix, dec[side]["model"]]
            for feature in dec[side]["features"]:
                args += ["--feature" + suffix, feature]
            args += _side_flags(dec[side], suffix)
        loss = record["comparison"]["loss"]
        args += ["--loss", "crps" if loss.startswith("crps") else "absolute-error"]
        return args
    features = []
    for feature in dec["features"]:
        features += ["--feature", feature]
    if "taus_bp" in dec:
        return (["exceedance-backtest", "--panel", panel, "--thresholds", THRESHOLDS,
                 "--model", dec["model"]] + common + features + _side_flags(dec)
                + _benchmark_flags(dec["model"]))
    return ["backtest", panel, "--model", dec["model"]] + common + features + _side_flags(dec)


def _benchmark_flags(model):
    """Both pressure benchmarks, paired with every exceedance record but their own."""

    flags = []
    for name, (benchmark, _features) in sorted(BENCHMARKS.items()):
        if benchmark != model:
            flags += ["--benchmark", benchmark]
    return flags


def benchmark_command(model, features, panel, refit_every):
    args = ["exceedance-backtest", "--panel", panel, "--thresholds", THRESHOLDS,
            "--model", model, "--registry", REGISTRY, "--decision-time", "16:00",
            "--minimum-history", "61", "--refit-every", str(refit_every)]
    for feature in features:
        args += ["--feature", feature]
    return args + _benchmark_flags(model)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("panel")
    parser.add_argument("outdir")
    parser.add_argument("--refit-every", type=int, default=21)
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--only", nargs="*")
    parser.add_argument("--dry-run", action="store_true")
    options = parser.parse_args(argv)

    out = Path(options.outdir)
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for path in sorted(ARCHIVE.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if "declaration" not in record:
            continue  # the panel manifest copy is not a scored record
        jobs.append((path.name, command(path.name, record, options.panel, options.refit_every)))
    for name, (model, features) in BENCHMARKS.items():
        jobs.append((name, benchmark_command(model, features, options.panel, options.refit_every)))
    if options.only:
        jobs = [job for job in jobs if job[0] in options.only]

    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), OMP_NUM_THREADS="1")

    def run(job):
        name, args = job
        full = [sys.executable, "-m", "repo_model.cli"] + args + ["--report", str(out / name)]
        if options.dry_run:
            return name, 0, " ".join(full)
        done = subprocess.run(full, cwd=ROOT, env=env, capture_output=True, text=True)
        return name, done.returncode, done.stderr[-2000:]

    failed = 0
    with ThreadPoolExecutor(max_workers=max(1, options.jobs)) as pool:
        for name, code, detail in pool.map(run, jobs):
            print(f"{'ok ' if code == 0 else 'ERR'} {name}" + (f"\n{detail}" if code or options.dry_run else ""), flush=True)
            failed += code != 0
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
