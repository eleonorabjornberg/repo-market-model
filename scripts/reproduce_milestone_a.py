#!/usr/bin/env python3
"""Reproduce the published persistence run from what a clone receives.

Milestone A's exit criterion has two clauses. Publication was met when
`docs/runs/persistence_funding.json` became generated output. Reproduction is
this script: one command that a reader runs in a fresh clone, with no network
and no gitignored file, and that either re-derives the record's figures or
says which ones it could not.

Three steps, each through the same command line a reader would type, so that a
passing run is evidence about the published commands and not about a private
code path:

1. `build` the daily panel from the raw inputs tracked under
   `tests/fixtures/snapshots/funding_inputs/`, with the build cutoff and
   decision time `metadata/funding_panel_manifest.json` records;
2. `verify-panel` the result against that manifest's `sha256` -- the bytes,
   not the extent;
3. `backtest` it under the record's own `declaration`, and compare the new
   record with the published one.

What is compared is everything the record says about the run -- `declaration`,
`derived`, `folds`, `metrics`, and the panel's digest, extent and build
manifest -- and nothing about where or when it ran: `provenance` and the
paths are expected to differ, and a comparison that included them could never
pass. Floats are compared exactly. The run is deterministic, and the bootstrap
carries its seed; a tolerance here would be a second, unstated criterion.

Everything is written to a temporary directory, so the checkout is left as it
was found. Standard library only.

    python3 scripts/reproduce_milestone_a.py          # exit 0 if it reproduces
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "docs" / "runs" / "persistence_funding.json"
MANIFEST = ROOT / "metadata" / "funding_panel_manifest.json"
INPUTS = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
REGISTRY = ROOT / "metadata" / "sources.json"

# Declaration keys this script knows how to turn back into `backtest`
# arguments. A record declaring anything else is refused rather than re-run
# without it: dropping a declared argument re-runs a different experiment.
DECLARATION_KEYS = {"decision_time", "features", "minimum_history", "model"}

# Whole blocks of the record that describe the run, and the panel keys that do.
COMPARED_BLOCKS = ("declaration", "derived", "folds", "metrics")
COMPARED_PANEL = ("sha256", "row_count", "first_date", "last_date")


class ReproductionError(Exception):
    """A step could not run at all, as distinct from running and disagreeing."""


def _cli(*args):
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONDONTWRITEBYTECODE="1")
    done = subprocess.run(
        [sys.executable, "-B", "-m", "repo_model.cli", *args],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    if done.returncode != 0:
        raise ReproductionError(
            "repo_model.cli %s exited %d:\n%s"
            % (args[0], done.returncode, (done.stderr or done.stdout).strip())
        )
    return done.stdout


def _without_path(mapping):
    """A build manifest minus where it was written and its own digest.

    `sha256` is dropped here because it is compared once, as `panel.sha256`,
    and a manifest written before the digest landed -- the frozen panel's is
    one -- carries no copy of it to compare.
    """
    return {key: value for key, value in mapping.items() if key not in ("path", "sha256")}


def _differences(published, rebuilt, prefix=""):
    """Every leaf at which two JSON values disagree, as dotted paths."""
    if isinstance(published, dict) and isinstance(rebuilt, dict):
        found = []
        for key in sorted(set(published) | set(rebuilt)):
            where = "%s.%s" % (prefix, key) if prefix else str(key)
            if key not in published or key not in rebuilt:
                found.append("%s: present on one side only" % where)
            else:
                found.extend(_differences(published[key], rebuilt[key], where))
        return found
    if published != rebuilt:
        return ["%s: published %r, rebuilt %r" % (prefix, published, rebuilt)]
    return []


def reproduce(workdir):
    """Run the three steps in `workdir`. Returns the list of disagreements."""
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    declaration = record["declaration"]
    unknown = set(declaration) - DECLARATION_KEYS
    if unknown:
        raise ReproductionError(
            "the record declares %s, which this script cannot re-run"
            % ", ".join(sorted(unknown))
        )

    panel = Path(workdir) / "funding_panel.csv"
    _cli(
        "build",
        "--raw-root", str(INPUTS),
        "--registry", str(REGISTRY),
        "--output", str(panel),
        "--build-cutoff", manifest["build_cutoff"],
        "--decision-time", manifest["decision_time"],
    )
    _cli("verify-panel", str(panel), "--manifest", str(MANIFEST))

    report = Path(workdir) / "persistence_funding.json"
    arguments = [
        "backtest", str(panel),
        "--registry", str(REGISTRY),
        "--decision-time", declaration["decision_time"],
        "--model", declaration["model"],
        "--minimum-history", str(declaration["minimum_history"]),
        "--report", str(report),
    ]
    for feature in declaration["features"]:
        arguments += ["--feature", feature]
    _cli(*arguments)
    rebuilt = json.loads(report.read_text(encoding="utf-8"))

    found = []
    for block in COMPARED_BLOCKS:
        found.extend(_differences(record.get(block), rebuilt.get(block), block))
    for key in COMPARED_PANEL:
        found.extend(
            _differences(record["panel"].get(key), rebuilt["panel"].get(key), "panel." + key)
        )
    found.extend(
        _differences(
            _without_path(record["panel"]["build_manifest"]),
            _without_path(rebuilt["panel"]["build_manifest"]),
            "panel.build_manifest",
        )
    )
    return found


def main(argv=None):
    with tempfile.TemporaryDirectory(prefix="reproduce-milestone-a-") as workdir:
        try:
            found = reproduce(workdir)
        except ReproductionError as exc:
            print("did not run: %s" % exc, file=sys.stderr)
            return 2
    if found:
        print("does not reproduce %s:" % RECORD.relative_to(ROOT), file=sys.stderr)
        for line in found:
            print("  " + line, file=sys.stderr)
        return 1
    print(
        "reproduced %s: panel rebuilt from %s, verified against %s, "
        "every figure re-derived exactly."
        % (RECORD.relative_to(ROOT), INPUTS.relative_to(ROOT), MANIFEST.relative_to(ROOT))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
