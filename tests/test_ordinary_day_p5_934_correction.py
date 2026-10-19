"""The dated correction of #853's ordinary-day page (#934; H5 step 3, development tier).

The page is rendered from the committed `score.json` of #844 by `scripts/ordinary_day_p5_934.py`; no scoring is redone.
Written before the script: it fails with `ModuleNotFoundError` until the script exists.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCORE = ROOT / "docs" / "pivot" / "ordinary-day-p5-844" / "score.json"
PAGE = ROOT / "docs" / "pivot" / "ordinary-day-p5-844" / "correction-934.md"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = _load("ordinary_day_p5_934")


class CorrectionPageTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(SCORE.read_text(encoding="utf-8"))
        cls.text = script.render(cls.result)

    def test_the_committed_page_is_what_the_script_renders(self):
        self.assertEqual(PAGE.read_text(encoding="utf-8"), self.text)

    def test_the_page_leads_with_the_regimes_and_claims_no_pooled_gain(self):
        head = self.text.split("\n## ", 1)[0]
        self.assertIn("no pooled gain is claimed", head.lower())
        self.assertIn("not a verdict", head.lower())
        self.assertLess(self.text.index("| lead | 2018-19 |"), self.text.index("## Why the pooled"))
        self.assertNotIn("## Why the pooled", head)

    def test_every_regime_lead_and_model_cell_is_in_the_table(self):
        for h in range(1, 6):
            self.assertIn(f"| {h} |", self.text)
        for regime in ("2018-19", "2020-24", "2025-26"):
            self.assertIn(regime, self.text)
        for label in script.base.LABELS.values():
            if label not in ("raw as-of spread", "persistence-logistic"):
                self.assertIn(label, self.text)

    def test_a_figure_is_the_committed_figure(self):
        cell = self.result["definitions"]["non_ordinary"]["3"]["2018-19"]["rows"]["gbm_funding"]["auroc_minus_reference"]
        self.assertIn(script.base.fmt(cell, signed=True), self.text)

    def test_the_count_of_pooled_gains_above_every_regime_is_recomputed(self):
        base = script.base
        count = total = 0
        for name in base.MODEL_ROWS:
            for h in base.HORIZONS:
                cells = self.result["definitions"]["non_ordinary"][str(h)]
                regimes = [cells[r]["rows"][name]["auroc_minus_reference"]["value"] for r in script.REGIMES
                           if cells[r]["pressure_days"] >= base.MINIMUM_PRESSURE_DAYS]
                total += 1
                count += cells["pooled"]["rows"][name]["auroc_minus_reference"]["value"] > max(regimes)
        self.assertIn(f"In {count} of {total} model-by-lead rows below", self.text)

    def test_the_published_pages_are_not_rewritten(self):
        self.assertTrue((ROOT / "docs" / "pivot" / "ordinary-day-p5-844" / "report.md").exists())
        self.assertTrue((ROOT / "docs" / "pivot" / "ordinary-day-p5-result.md").exists())
        self.assertIn("ordinary-day-p5-result.md", self.text)


if __name__ == "__main__":
    unittest.main()
