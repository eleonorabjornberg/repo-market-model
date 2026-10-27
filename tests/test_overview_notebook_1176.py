"""The Colab notebooks state the project's current question and run (#1176; H5 framing, distribution first, calendar first).

`notebooks/00_overview.ipynb` is what the README's Colab badge opens. It once stated the +5 bp probability as the headline,
defined month-end as the last two business days, and scored only the 5 bp classification baselines. These tests pin the
framing and run the notebook's code, so a stale notebook is a red suite and not a page nobody opened.

- The framing tests read the notebook source.
- `test_the_stdlib_cells_run_and_score_the_distribution` executes the cells tagged `stdlib` (the clone-or-find, build and
  verify cells, and the cell that scores B1 and B1-prime by grid CRPS through `scoring_protocol`) in a fresh interpreter
  from a path outside the repository's working directory, with no network. It needs nothing beyond the standard library.
- `test_the_whole_notebook_runs` executes every code cell when pandas, matplotlib, scikit-learn and IPython are importable
  (the Colab environment has them; the core CI job does not).

This adds no leakage, availability or staleness guard, so there is no recorded mutation. The notebook scores development
days only (targets through 2025-12-31, as the project's development scripts do); the test pins that line.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "notebooks/00_overview.ipynb"
WALKTHROUGH = ROOT / "notebooks/01_portfolio_walkthrough.ipynb"

RUNNER = r"""
import json, sys
cells = json.load(open(sys.argv[1], encoding="utf-8"))["cells"]
only = sys.argv[2] == "stdlib"
g = {"__name__": "__main__"}
for i, c in enumerate(cells):
    if c["cell_type"] != "code":
        continue
    if only and "stdlib" not in c["metadata"].get("tags", []):
        continue
    exec(compile("".join(c["source"]), "cell%d" % i, "exec"), g)
"""


def cells(path):
    return json.loads(path.read_text(encoding="utf-8"))["cells"]


def text(path, kind=None):
    return "\n".join("".join(c["source"]) for c in cells(path) if kind in (None, c["cell_type"]))


def run(mode, notebook=NOTEBOOK, cwd=ROOT):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if notebook == NOTEBOOK:
        env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run([sys.executable, "-B", "-c", RUNNER, str(notebook), mode], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=600)


class FramingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = text(NOTEBOOK)
        cls.prose = text(NOTEBOOK, "markdown")

    def test_the_distribution_is_the_question_and_the_5_bp_event_one_reading(self):
        self.assertNotIn("headline target is a probability", self.all)
        self.assertNotIn("Its headline question is", self.all)
        intro = "".join(cells(NOTEBOOK)[0]["source"])
        self.assertIn("whole distribution", intro)
        self.assertLess(intro.index("distribution"), intro.index("pressure day"))
        self.assertIn("one reading", self.prose)

    def test_the_calendar_comes_first_and_the_turn_definition_is_read_from_turn_days(self):
        self.assertNotIn("last two business days", self.all)
        self.assertIn("calendar", "".join(cells(NOTEBOOK)[0]["source"]).lower())
        self.assertIn("from repo_model import turn_days", self.all)
        self.assertIn("turn_days.turn_day_type", self.all)
        self.assertIn("turn_days.in_force()", self.all)

    def test_it_scores_b1_and_b1_prime_through_the_scorer(self):
        self.assertIn("b1_calendar.b1_calendar_forecast", self.all)
        self.assertIn("pb.b1_forecast", self.all)
        self.assertIn("sp.day_scores", self.all)
        self.assertIn("scouting illustration, not a record", self.prose)

    def test_it_points_to_the_candidate_without_copying_its_figures(self):
        self.assertIn("docs/research/h5-candidate.json", self.prose)
        self.assertIn("docs/research/state-calendar-1145-result.md", self.prose)
        for name in ("docs/research/h5-candidate.json", "docs/research/state-calendar-1145-result.md"):
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertIsNone(re.search(r"[+-]\d+\.\d%", self.prose))

    def test_the_embedded_figure_exists(self):
        self.assertTrue((ROOT / "docs/figures/overview-light.svg").is_file())

    def test_no_outputs_are_stored(self):
        for path in (NOTEBOOK, WALKTHROUGH):
            for c in cells(path):
                if c["cell_type"] == "code":
                    self.assertEqual(c["outputs"], [], path.name)
                    self.assertIsNone(c["execution_count"], path.name)


class WalkthroughNoteTests(unittest.TestCase):
    def test_the_synthetic_walkthrough_keeps_its_machinery_and_says_what_changed(self):
        prose = text(WALKTHROUGH, "markdown")
        self.assertIn("what has changed since", prose)
        self.assertIn("23 October 2026", prose)
        self.assertIn("whole distribution", prose)
        self.assertIn("00_overview.ipynb", prose)


class RunTests(unittest.TestCase):
    def test_the_stdlib_cells_run_and_score_the_distribution(self):
        done = run("stdlib")
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])
        self.assertIn("panel verified", done.stdout)
        self.assertIn("targets through 2025-12-31", done.stdout)  # development days only
        lines = {l.split("  ")[0].strip(): l for l in done.stdout.splitlines()}
        pooled = lines["all target days"].split()
        b1, b1_prime = float(pooled[-3]), float(pooled[-2])
        self.assertGreater(b1, 0)
        self.assertLess(b1_prime, b1)  # the calendar-aware persistence is the better benchmark on development days
        self.assertIn("ordinary target days", lines)
        self.assertIn("turn and year-end target days", lines)

    def test_the_walkthrough_notebook_finds_the_repository_from_the_notebooks_directory(self):
        """Run from `notebooks/` with no PYTHONPATH, the way Colab opens it inside a clone (it once needed the repo root)."""
        done = run("all", WALKTHROUGH, ROOT / "notebooks")
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])
        self.assertIn("reports written to", done.stdout)

    @unittest.skipUnless(all(importlib.util.find_spec(m) for m in ("pandas", "matplotlib", "sklearn", "IPython")),
                         "needs the Colab packages (pandas, matplotlib, scikit-learn, IPython)")
    def test_the_whole_notebook_runs(self):
        done = run("all")
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])
        self.assertIn("notebook finished in", done.stdout)


if __name__ == "__main__":
    unittest.main()
