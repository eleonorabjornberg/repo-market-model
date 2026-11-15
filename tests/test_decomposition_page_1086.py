"""The page of the 2021-23 decomposition (#1086, H5 step 3, criterion 1) quotes only what `decompose.json` holds.

The decomposition itself (`scripts/direct_pairs_diagnosis_1086.py decompose`) reads walks that exist on Eleonora's Mac only, so the cloud cannot re-run it;
what is pinned here is that the committed output is internally consistent and that the page and `result.json` are made from it.

* every group's total is the sum of its bands and the sum of its 23 levels;
* the three pairs are consistent: aligned over gbm_funding = aligned over direct + direct over gbm_funding, cell for cell, in every group (the means of
  differences are differences of means over the same cells);
* `result.json` is `headline(decompose.json)`;
* the page carries the figures it reads in words (the 2021-23 total, the centre share, the lead and year figures) to four decimals, as `decompose.json` has them.

Recorded mutation: `headline`, `groups = windows["2021-23"]` changed to `groups = windows["outside 2021-23"]`:
`HeadlineTests.test_result_json_is_the_headline_of_decompose_json` fails with `AssertionError` (the totals differ).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("direct_pairs_diagnosis_1086_script", REPO / "scripts" / "direct_pairs_diagnosis_1086.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

DIR = REPO / "docs" / "research" / "direct-pairs-diagnosis-1086"
PAGE = REPO / "docs" / "research" / "decomposition-1086-result.md"
DECOMPOSE = json.loads((DIR / "decompose.json").read_text(encoding="utf-8"))
DIRECT_OVER = "gbm_funding_cal_direct over gbm_funding"
ALIGNED_OVER_DIRECT = "gbm_funding_cal_aligned over gbm_funding_cal_direct"
ALIGNED_OVER = "gbm_funding_cal_aligned over gbm_funding"


class ConsistencyTests(unittest.TestCase):
    def test_totals_are_the_sum_of_bands_and_of_levels(self):
        for pair, windows in DECOMPOSE["pairs"].items():
            for window, groups in windows.items():
                for name, g in groups.items():
                    self.assertAlmostEqual(sum(g["by_band"].values()), g["total"], places=9, msg=(pair, window, name))
                    self.assertAlmostEqual(sum(g["by_level"]), g["total"], places=9, msg=(pair, window, name))

    def test_the_three_pairs_add_up_in_every_shared_group(self):
        for window in ("2021-23", "outside 2021-23"):
            a, b, c = (DECOMPOSE["pairs"][p][window] for p in (ALIGNED_OVER, ALIGNED_OVER_DIRECT, DIRECT_OVER))
            for name in c:
                self.assertEqual(a[name]["days"], c[name]["days"])
                self.assertAlmostEqual(a[name]["total"], b[name]["total"] + c[name]["total"], places=9, msg=(window, name))


class HeadlineTests(unittest.TestCase):
    def test_result_json_is_the_headline_of_decompose_json(self):
        result = json.loads((DIR / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(result, script.headline(DECOMPOSE))

    def test_the_headline_reads_the_2021_23_window(self):
        head = script.headline(DECOMPOSE)["pairs"][DIRECT_OVER]
        self.assertAlmostEqual(head["total"], DECOMPOSE["pairs"][DIRECT_OVER]["2021-23"]["all"]["total"], places=12)


class PageTests(unittest.TestCase):
    def test_the_page_quotes_the_figures_it_reads(self):
        page = PAGE.read_text(encoding="utf-8")
        for pair in (DIRECT_OVER, ALIGNED_OVER_DIRECT, ALIGNED_OVER):
            groups = DECOMPOSE["pairs"][pair]["2021-23"]
            for name in ("all", "lead 1", "lead 5", "year 2021", "year 2022", "year 2023", "ordinary", "quarter_end"):
                self.assertIn(f"{groups[name]['total']:+.4f}", page, msg=(pair, name))
            self.assertIn(f"{groups['all']['by_band']['centre']:+.4f}", page)

    def test_the_page_says_whether_the_cause_looks_fixable(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("Does the cause look fixable", page)
        self.assertIn("development data", page.lower())
        self.assertIn("settled-questions.md", page)


if __name__ == "__main__":
    unittest.main()
