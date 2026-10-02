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
   `tests/fixtures/snapshots/funding_inputs/`, with the build cutoff,
   decision time and columns `metadata/funding_panel_manifest.json` records
   -- one `--column` per `built_columns` entry. The columns are the
   load-bearing one: a source joining the registry adds a column to a default
   build, and a default build would no longer be these bytes;
2. `verify-panel` the result against that manifest's `sha256` -- the bytes,
   not the extent;
3. `backtest` it under the record's own `declaration`, and compare the new
   record with the published one.

What is compared is everything the record says about the run -- `declaration`,
`derived`, `folds`, `metrics`, and the panel's digest, extent and build
manifest less its refusals (see `_without_path`) -- and nothing about where or
when it ran: `provenance` and the
paths are expected to differ, and a comparison that included them could never
pass. Floats are compared exactly. The run is deterministic, and the bootstrap
carries its seed; a tolerance here would be a second, unstated criterion.

**A record scored under the purge rule is not re-run.** Its `derived` carries
`purge_days`, and the scoring path has since moved to the as-of rule
(`docs/decisions/information-set.md`), under which it cannot reproduce by
design. For such a record steps 1 and 2 still run and must pass -- the panel is
unaffected -- and step 3 raises `PrePurgeRuleRecord`, naming the rule. The
re-scoring pull request replaces the record with one scored under the as-of
rule, and from then on all three steps run again.

**Nor is a record whose scored days reach a locked tier.** The lockbox
(`docs/decisions/lockbox.md`, `metadata/lockbox.json`) refuses to score a day
in a tier that has not been opened, and the published record was scored
through the end of the panel, inside the near-blind tier. Steps 1 and 2 still
run and must pass, and step 3 raises `LockedRecord`, naming the tier. The day
the tier is opened, all three steps run again with no edit here.

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
DECLARATION_KEYS = {
    "decision_time", "end", "features", "minimum_history", "model", "refit_every",
}

# Whole blocks of the record that describe the run, and the panel keys that do.
COMPARED_BLOCKS = ("declaration", "derived", "folds", "metrics")
COMPARED_PANEL = ("sha256", "row_count", "first_date", "last_date")


class ReproductionError(Exception):
    """A step could not run at all, as distinct from running and disagreeing."""


class PrePurgeRuleRecord(ReproductionError):
    """The record was scored under the purge rule, which the code no longer runs."""


class LockedRecord(ReproductionError):
    """The record scored days in a locked tier, which the code refuses to score."""


def locked_tier_refusal(record):
    """The lockbox's refusal of the record's scored days, or `None`.

    The record's first and last scored days are checked by the guard every
    scoring entry point calls (`repo_model.lockbox.require_unlocked`), so this
    says what step 3 would meet without running it. The tiers are contiguous
    to the end of time, so the two ends of the record's scored days decide it.
    """
    if str(ROOT / "src") not in sys.path:
        sys.path.insert(0, str(ROOT / "src"))
    from datetime import date

    from repo_model.lockbox import require_unlocked
    from repo_model.splits import LookAheadError

    folds = record["folds"]
    days = [date.fromisoformat(folds[end]["scored_date"]) for end in ("first", "last")]
    try:
        require_unlocked(days, where=str(RECORD.relative_to(ROOT)))
    except LookAheadError as exc:
        return str(exc)
    return None


def scored_under_purge_rule(record):
    """Was this record scored before the as-of rule? Its `derived` says so."""
    return "purge_days" in record.get("derived", {})


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


# Build-manifest keys that describe the invocation or the path, not the panel.
UNCOMPARED_MANIFEST = ("path", "sha256", "refused_columns")


def _without_path(mapping):
    """A build manifest minus where it was written, its digest and its refusals.

    `sha256` is dropped here because it is compared once, as `panel.sha256`,
    and a manifest written before the digest landed -- the frozen panel's is
    one -- carries no copy of it to compare.

    `refused_columns` is dropped because it records what that invocation was
    asked for and could not build, not what the panel holds. The published
    build asked for every declared column and refused seven; this script asks
    for `built_columns` only, and a build given `--column` refuses nothing or
    exits. The panel's content is still held twice: `built_columns` is
    compared here, and the bytes are compared by digest.
    """
    return {key: value for key, value in mapping.items() if key not in UNCOMPARED_MANIFEST}


def _differences(published, rebuilt, prefix=""):
    """Every leaf at which two JSON values disagree, as dotted paths."""
    if isinstance(published, dict) and isinstance(rebuilt, dict):
        found = []
        for key in sorted(set(published) | set(rebuilt)):
            where = "%s.%s" % (prefix, key) if prefix else str(key)
            if key not in published:
                # The rebuild computes a field this record was scored before.
                # No figure the record publishes disagrees, so under Milestone
                # A's clause this is the record being older than the code and
                # not a reproduction failure. The converse below is.
                continue
            elif key not in rebuilt:
                found.append(
                    "%s: present only in the published record" % where
                )
            else:
                found.extend(_differences(published[key], rebuilt[key], where))
        return found
    if published != rebuilt:
        return ["%s: published %r, rebuilt %r" % (prefix, published, rebuilt)]
    return []


def reproduce_panel(workdir):
    """Steps 1 and 2: build the panel from tracked inputs and verify its digest.

    Returns the panel's path. Raises `ReproductionError` if either step fails.
    """
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    columns = manifest.get("built_columns")
    if not columns:
        raise ReproductionError(
            "%s records no built_columns; a default build is not pinned to the "
            "published panel's columns" % MANIFEST.relative_to(ROOT)
        )
    panel = Path(workdir) / "funding_panel.csv"
    build = [
        "build",
        "--raw-root", str(INPUTS),
        "--registry", str(REGISTRY),
        "--output", str(panel),
        "--build-cutoff", manifest["build_cutoff"],
        "--decision-time", manifest["decision_time"],
    ]
    for column in columns:
        build += ["--column", column]
    _cli(*build)
    _cli("verify-panel", str(panel), "--manifest", str(MANIFEST))
    return panel


def reproduce(workdir):
    """Run the three steps in `workdir`. Returns the list of disagreements.

    Raises `PrePurgeRuleRecord` after steps 1 and 2 when the record was scored
    under the purge rule, and `LockedRecord` when it scored a locked day.
    """
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    declaration = record["declaration"]
    unknown = set(declaration) - DECLARATION_KEYS
    if unknown:
        raise ReproductionError(
            "the record declares %s, which this script cannot re-run"
            % ", ".join(sorted(unknown))
        )

    panel = reproduce_panel(workdir)
    if scored_under_purge_rule(record):
        raise PrePurgeRuleRecord(
            "%s was scored under the purge rule (derived.purge_days %r); the "
            "scoring path runs the as-of rule, so the record is re-scored, not "
            "reproduced. The panel it was scored on still reproduces."
            % (RECORD.relative_to(ROOT), record["derived"]["purge_days"])
        )

    refusal = locked_tier_refusal(record)
    if refusal is not None:
        raise LockedRecord(
            "%s; the record is not re-scored while the tier is locked. The "
            "panel it was scored on still reproduces." % refusal
        )

    report = Path(workdir) / "persistence_funding.json"
    arguments = [
        "backtest", str(panel),
        "--registry", str(REGISTRY),
        "--decision-time", declaration["decision_time"],
        "--model", declaration["model"],
        "--minimum-history", str(declaration["minimum_history"]),
        "--refit-every", str(declaration.get("refit_every", 1)),
        "--report", str(report),
    ]
    if "end" in declaration:
        arguments += ["--end", declaration["end"]]
    for feature in declaration["features"]:
        arguments += ["--feature", feature]
    # A record split by regime and pressure-day type (#27) names the
    # declaration it was split by, as the path the publishing run passed:
    # relative to the checkout, which is where this runs the command from.
    if "splits" in record:
        arguments += ["--splits", record["splits"]["declaration"]["path"]]
    _cli(*arguments)
    rebuilt = json.loads(report.read_text(encoding="utf-8"))

    found = []
    for block in COMPARED_BLOCKS + (("splits",) if "splits" in record else ()):
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
