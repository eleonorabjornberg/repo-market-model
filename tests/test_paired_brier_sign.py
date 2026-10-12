"""The sign of the paired Brier difference (#604): the reference's squared error minus the candidate's, so positive favours the candidate.

`pressure_judge._paired_vectors` builds the difference as the reference's loss minus the candidate's, and its own comment says so.
The tables of `announcement_dating_rescore.py compare` and `iorb_every_day_579.py compare` printed the opposite ("negative favours the
arm"), which inverted every reading of "which arm is better" taken from them. These tests pin the statistic and the headers.
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

    def test_no_script_that_pairs_against_the_judges_statistic_says_negative_favours(self):
        offenders = []
        for path in sorted(SCRIPTS.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            if "_paired_vectors" in text and "negative favours" in text:
                offenders.append(path.name)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
