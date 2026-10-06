"""The five-quantile score is named for what it is on generated text (#259).

The final test's score is the unweighted mean of five pinball losses, at the
published quantile levels (`metrics.crps_from_quantiles`). It is a fixed score
and not the CRPS integral, so generated pages and the site do not call the
forecast "the full distribution" and name the score as the five-quantile score.
Records already published keep their field names and wording; only generated
text is checked.

Recorded mutation (the guard's text restored in `scripts/emit_results.py`, the
claim passed through unchanged, `final_test_claim_wording = lambda claim: claim`):
`test_the_generated_final_test_section_never_says_full_distribution` fails with
`AssertionError`.
"""

import importlib.util
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BANNED = re.compile(r"full\s+distribution", re.IGNORECASE)


def _script(name):
    spec = importlib.util.spec_from_file_location(f"naming_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _generated_blocks(text):
    """The text between `<!-- generated: x -->` and its end marker."""

    return re.findall(r"<!-- generated: ([\w-]+) -->(.*?)<!-- end generated: \1 -->", text, re.DOTALL)


class FullDistributionTests(unittest.TestCase):
    def test_the_generated_final_test_section_never_says_full_distribution(self):
        section = _script("emit_results").final_test_section()
        self.assertIsNone(BANNED.search(section), BANNED.findall(section))
        self.assertIn("five-quantile score", section)
        self.assertIn("five published quantiles", section)

    def test_generated_blocks_and_pages_never_say_full_distribution(self):
        for name in ("README.md", "docs/final-test.md", "METHODOLOGY.md", "PLAN.md"):
            text = (REPO / name).read_text(encoding="utf-8")
            for key, block in _generated_blocks(text):
                with self.subTest(file=name, block=key):
                    self.assertIsNone(BANNED.search(block))
        for name in ("site/index.html", "site/template.html"):
            with self.subTest(file=name):
                self.assertIsNone(BANNED.search((REPO / name).read_text(encoding="utf-8")))
        for path in sorted((REPO / "docs/visual/data").glob("*.json")):
            with self.subTest(file=path.name):
                self.assertIsNone(BANNED.search(path.read_text(encoding="utf-8")))

    def test_the_site_names_the_score_for_what_it_is(self):
        page = (REPO / "site/index.html").read_text(encoding="utf-8")
        self.assertIn("five-quantile score", page)
        self.assertIn("mean pinball loss", page)


class TrapezoidSensitivityRecordTests(unittest.TestCase):
    """The published sensitivity record reproduces the review's figures (#259)."""

    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(
            (REPO / "docs/runs/final_test_near_blind_integral_sensitivity.json").read_text(encoding="utf-8")
        )
        cls.cell = cls.record["cell"]

    def test_it_reproduces_the_reviewers_figures(self):
        self.assertEqual(self.cell["days"], 169)
        self.assertAlmostEqual(self.cell["mean_difference_bps"], 0.1816, places=4)
        self.assertAlmostEqual(self.cell["interval"]["lower"], 0.0391, places=4)
        self.assertAlmostEqual(self.cell["interval"]["upper"], 0.3624, places=4)
        self.assertEqual(self.cell["interval"]["block_length"], 2)
        self.assertAlmostEqual(self.cell["sensitivity_interval"]["lower"], 0.0391, places=4)
        self.assertAlmostEqual(self.cell["sensitivity_interval"]["upper"], 0.3492, places=4)
        self.assertEqual(self.cell["sensitivity_interval"]["block_length"], 10)

    def test_it_recomputes_from_its_own_per_origin_losses(self):
        origins = self.record["window_per_origin"]
        self.assertEqual(len(origins), self.cell["days"])
        for entry in origins:
            self.assertAlmostEqual(entry["loss_a_bps"] - entry["loss_b_bps"], entry["difference_bps"], places=9)
        mean = sum(e["difference_bps"] for e in origins) / len(origins)
        self.assertAlmostEqual(mean, self.cell["mean_difference_bps"], places=9)
        self.assertAlmostEqual(sum(e["loss_a_bps"] for e in origins) / len(origins),
                               self.cell["crps_integral_persistence_bps"], places=9)

    def test_it_is_reported_only_and_rests_on_the_frozen_declaration(self):
        primary = json.loads((REPO / "docs/runs/final_test_near_blind.json").read_text(encoding="utf-8"))
        self.assertEqual(self.cell["role"], "reported only")
        self.assertEqual(self.record["crps_declaration_sha256"], primary["crps_declaration_sha256"])
        self.assertEqual(self.record["crps_declaration_sha256"],
                         _script("final_test_preregistration").crps_declaration_checksum())
        # The primary record is untouched: its own cell still carries the plain score.
        self.assertEqual(self.record["primary_cell_by_the_plain_score"]["crps_persistence_bps"],
                         primary["primary"]["cell"]["crps_persistence_bps"])

    def test_the_window_differences_match_the_primary_cell_in_dates(self):
        primary = json.loads((REPO / "docs/runs/final_test_near_blind.json").read_text(encoding="utf-8"))
        self.assertEqual([e["scored_date"] for e in self.record["window_per_origin"]],
                         [e["scored_date"] for e in primary["primary"]["window_per_origin"]])

    def test_the_assembler_refuses_a_report_that_is_not_the_frozen_run(self):
        script = _script("final_test_integral_sensitivity")
        with self.assertRaises(ValueError):
            script.cell({"declaration": {}, "comparison": {"loss": "crps_integral_bps"}, "panel": {}})


if __name__ == "__main__":
    unittest.main()
