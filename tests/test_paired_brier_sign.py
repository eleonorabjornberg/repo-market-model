"""The sign of the paired Brier difference (#604): the reference's squared error minus the candidate's, so positive favours the candidate.

`pressure_judge._paired_vectors` builds the difference as the reference's loss minus the candidate's, and its own comment says so.
The tables of `announcement_dating_rescore.py compare` and `iorb_every_day_579.py compare` printed the opposite ("negative favours the
arm"), which inverted every reading of "which arm is better" taken from them. These tests pin the statistic and the headers.

`scripts/pooled_gate_595.py` printed the old header too (#613, found while working #610); its Table 3 now says "positive favours the row".
Recorded mutation (12 October 2026, disposable copy): the header restored to "(negative favours the row)" fails
`HeaderTests.test_the_pooled_gate_table_says_positive_favours_the_row` and `HeaderTests.test_no_script_that_pairs_against_the_judges_statistic_says_negative_favours`
with `AssertionError`.
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model import pressure_judge as pj

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load(name):
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location(f"{name}_sign_test", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _difference(candidate, reference, outcomes):
    flat = [0.5] * len(outcomes)
    vectors = pj._paired_vectors(candidate, reference, flat, outcomes)
    return pj._PAIRED_STATS["brier_difference_vs_climatology"]([sum(vector) for vector in vectors])


class StatisticTests(unittest.TestCase):
    outcomes = [1, 0, 0, 1]

    def test_a_candidate_with_the_lower_squared_error_gives_a_positive_difference(self):
        reference = [0.5, 0.5, 0.5, 0.5]
        candidate = [0.9, 0.1, 0.1, 0.9]
        self.assertGreater(_difference(candidate, reference, self.outcomes), 0)

    def test_a_candidate_with_the_higher_squared_error_gives_a_negative_difference(self):
        reference = [0.9, 0.1, 0.1, 0.9]
        candidate = [0.5, 0.5, 0.5, 0.5]
        self.assertLess(_difference(candidate, reference, self.outcomes), 0)

    def test_the_difference_is_the_references_squared_error_minus_the_candidates(self):
        reference = [0.5, 0.5, 0.5, 0.5]
        candidate = [0.9, 0.1, 0.1, 0.9]
        expected = sum((r - y) ** 2 - (c - y) ** 2 for r, c, y in zip(reference, candidate, self.outcomes)) / 4
        self.assertAlmostEqual(_difference(candidate, reference, self.outcomes), expected)


class HeaderTests(unittest.TestCase):
    def test_the_compare_headers_say_positive_favours_the_candidate(self):
        announcement = _load("announcement_dating_rescore")
        iorb = _load("iorb_every_day_579")
        for header in (announcement.PAIRED_BRIER_HEADER, iorb.PAIRED_BRIER_HEADER):
            self.assertIn("positive favours", header)
            self.assertNotIn("negative favours", header)

    def test_the_iorb_table_prints_its_header(self):
        iorb = _load("iorb_every_day_579")
        document = json.loads((ROOT / "docs" / "pivot" / "evidence" / "iorb-every-day" / "compare-weighted.json").read_text())
        pairs = [("iorb", iorb.NEW, iorb.PARENT)]
        self.assertIn(iorb.PAIRED_BRIER_HEADER, iorb.markdown(document, pairs))

    def test_the_pooled_gate_table_says_positive_favours_the_row(self):
        # #613: scripts/pooled_gate_595.py printed "negative favours the row" under the same statistic
        pooled = _load("pooled_gate_595")
        document = {"onsets_in_cell": {}, "flags": {}, "recall_at_some_lead": {}, "caught_at_some_lead": {}, "brier": {"row": {"1": {}}}}
        text = pooled.comparison_markdown(document, [("both", "row", "reference")])
        self.assertIn("positive favours the row", text)
        self.assertNotIn("negative favours", text)

    def test_no_script_that_pairs_against_the_judges_statistic_says_negative_favours(self):
        # scripts that build their own a - b difference (unused_inputs, risk_date_severity, pressure_hazard) say what they compute
        offenders = []
        for path in sorted(SCRIPTS.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            judges = "_paired_vectors" in text or '_load("announcement_dating_rescore")' in text
            if judges and "negative favours" in text:
                offenders.append(path.name)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
