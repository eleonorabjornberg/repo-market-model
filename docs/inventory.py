#!/usr/bin/env python3
"""Regenerate the file inventory for `docs/state-of-main-*.md`.

Why this exists: the inventory in that report went stale three times in a single
afternoon — once between measuring the tree and finishing the prose, twice more
while the two tracks kept merging. Hand-typed line counts and test counts in a
document describing a moving tree are a maintenance debt with no upside, so they
are generated instead.

Usage, from the repository root:

    PYTHONPATH=src python3 -B docs/inventory.py            # print the markdown
    PYTHONPATH=src python3 -B docs/inventory.py --check    # exit 1 if the report is stale

Ownership is read from `.github/check_ownership.py` rather than restated here,
for the same reason the shared shapes live in `src/repo_model/contract.py`: a
second reading of a rule is a second rule.

Stdlib only, by contract.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_GLOB = "docs/state-of-main-*.md"


def _gate():
    spec = importlib.util.spec_from_file_location(
        "_gate", ROOT / ".github" / "check_ownership.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def owner_of(path: str, gate) -> str:
    """Who owns `path`, per the gate. Forbidden to a track means owned by the other."""

    def hit(patterns):
        return any(gate.matches(path, pattern) for pattern in patterns)

    if hit(gate.HUMAN_ONLY):
        return "human"
    if hit(gate.SHARED):
        return "neither"
    if hit(gate.TRACKS["feature/model-eval"]["forbidden"]):
        return "Track A"
    if hit(gate.TRACKS["feature/data-layer"]["forbidden"]):
        return "Track B"
    return "**UNOWNED**"


def head() -> str:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    return out.stdout.strip() or "unknown"


def count_tests(path: Path) -> int:
    """Tests declared in one file, without running them."""

    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(ROOT / "tests"), pattern=path.name, top_level_dir=str(ROOT / "tests")
    )
    return suite.countTestCases()


def lines(path: Path) -> int:
    return len(path.read_text().splitlines())


def render() -> str:
    gate = _gate()
    rows = []

    src = sorted((ROOT / "src" / "repo_model").glob("*.py"), key=lambda p: -lines(p))
    total_src = sum(lines(p) for p in src)
    rows.append(f"**Source — {total_src:,} lines**\n")
    rows.append("| Path | Lines | Owner |")
    rows.append("|---|---:|---|")
    for p in src:
        rel = f"src/repo_model/{p.name}"
        rows.append(f"| `{rel}` | {lines(p)} | {owner_of(rel, gate)} |")

    tests = sorted((ROOT / "tests").glob("test_*.py"), key=lambda p: -lines(p))
    total_lines = sum(lines(p) for p in tests)
    counts = {p: count_tests(p) for p in tests}
    rows.append(f"\n**Tests — {total_lines:,} lines, {sum(counts.values())} tests**\n")
    rows.append("| Path | Lines | Tests |")
    rows.append("|---|---:|---:|")
    for p in tests:
        rows.append(f"| `tests/{p.name}` | {lines(p)} | {counts[p]} |")

    docs = [
        ROOT / n
        for n in ("AGENT_CONTRACT.md", "PLAN.md", "DATA.md", "METHODOLOGY.md", "README.md")
    ] + sorted((ROOT / "metadata").glob("*.json"))
    rows.append("\n**Metadata and documents**\n")
    rows.append("| Path | Lines |")
    rows.append("|---|---:|")
    for p in docs:
        if p.exists():
            rows.append(f"| `{p.relative_to(ROOT)}` | {lines(p)} |")

    rows.append(
        f"\n**Suite:** {sum(counts.values())} tests. Standard library only; no install "
        f"step. Measured at `{head()}`.\n\n```\n"
        "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests\n"
        "```"
    )
    return "\n".join(rows)


def check() -> int:
    """Fail if the report's stated test total no longer matches the tree."""

    reports = sorted(ROOT.glob(REPORT_GLOB))
    if not reports:
        print("no report found", file=sys.stderr)
        return 1

    actual = sum(
        count_tests(p) for p in (ROOT / "tests").glob("test_*.py")
    )
    stale = []
    for report in reports:
        text = report.read_text()
        claimed = {int(n) for n in re.findall(r"\*\*Suite:\*\* ([0-9]+) tests", text)}
        claimed |= {int(n) for n in re.findall(r"([0-9]+) tests, OK", text)}
        wrong = sorted(n for n in claimed if n != actual)
        if wrong:
            stale.append(f"{report.relative_to(ROOT)}: claims {wrong}, tree has {actual}")

    if stale:
        print("Report is stale:", *stale, sep="\n  ", file=sys.stderr)
        print(
            "\nRegenerate Appendix B with:  PYTHONPATH=src python3 -B docs/inventory.py",
            file=sys.stderr,
        )
        return 1
    print(f"Report is current: {actual} tests at {head()}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if the report is stale")
    args = parser.parse_args()
    raise SystemExit(check() if args.check else (print(render()) or 0))
