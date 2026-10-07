"""The README's first screen is a landing page (#303).

A reader who stops after forty lines has the question, the verdict in plain words, the
near-blind final-test result with its limits and a link to the live site; the quick start
is within eighty lines; an architecture and ownership map and a note on the agent files
follow. The verdict and the figures are generated (`scripts/emit_results.py`), so this
test reads them off the records and never types a figure.

Written first, and red: on `main` at `c4fbdad` every test here failed, the first with
`AssertionError: '<!-- generated: landing -->' not found in the first 45 lines`.
"""

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
GUIDE = (ROOT / "PROJECT_GUIDE.md").read_text(encoding="utf-8").splitlines()  # the map moved there (#344)
SITE = "https://eleonorabjornberg.github.io/repo-market-model/"


def head(count):
    return "\n".join(README[:count])


class LandingTest(unittest.TestCase):
    def test_first_screen_carries_verdict_final_test_and_site(self):
        first = head(45)
        self.assertIn("<!-- generated: landing -->", first)
        self.assertIn("what is the chance that tomorrow SOFR is more than 5 basis points above IORB", first.replace("\n", " "))
        self.assertIn("Where this is", first)
        self.assertIn("near blind", first)
        self.assertIn("not a stress warning", first)
        self.assertIn("distribution", first)
        self.assertIn(SITE, first)

    def test_final_test_figures_are_the_records(self):
        cell = json.loads((ROOT / "docs/runs/final_test_near_blind.json").read_text())["primary"]["cell"]
        first = head(45)
        for value in (cell["crps_published_bps"], cell["crps_persistence_bps"]):
            self.assertIn("%.3f bp" % value, first)
        self.assertIn("%+.3f" % cell["mean_difference_bps"], first)
        self.assertIn("%+.3f" % cell["interval"]["lower"], first)
        self.assertIn("%+.3f" % cell["interval"]["upper"], first)

    def test_quick_start_within_eighty_lines(self):
        quick = [n for n, line in enumerate(README) if line.startswith("## Quick start")]
        self.assertTrue(quick)
        self.assertLess(quick[0], 80)
        block = "\n".join(README[quick[0]:quick[0] + 25])
        self.assertIn("unittest discover", block)
        self.assertIn("repo_model.cli", block)

    def test_map_and_agent_files(self):
        text = "\n".join(GUIDE)
        self.assertIn("## Architecture and ownership", text)
        self.assertLess(text.index("## Architecture and ownership"), text.index("## Why this project"))
        self.assertIn("#who-decides-and-who-reviews", text)
        for name in ("AGENTS.md", "CLAUDE.md", ".claude/"):
            self.assertIn(name, text.split("## Architecture and ownership")[1].split("\n## ")[0])


if __name__ == "__main__":
    unittest.main()
