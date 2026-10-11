"""The re-score of the judge's rows under the rulings of 10 October 2026 (#536): its tables and its cross-check.

`scripts/judge_rulings_rescore.py` renders the judge's amended tier 1 (pooled false alarms, each lead alone, inside and
outside 2018-19, equal-weight recall by regime) and tier 3 (regimes tested). These tests render a synthetic series so each
table has a known answer, and check that the cross-check against readings (b) and (e) of #523 flags a figure that moved.
"""

from __future__ import annotations

import importlib.util
import unittest
from dataclasses import replace
from pathlib import Path

from repo_model import pressure_judge as pj

from test_pressure_judge import Series, _load


def _script():
    spec = importlib.util.spec_from_file_location(
        "judge_rulings_rescore", Path(__file__).parents[1] / "scripts" / "judge_rulings_rescore.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DOCUMENT = {
    "rows": {
        "risk_date_passers": ["sharp"], "best_recall_rows": [], "gate_rows": [],
        "references": ["calendar_climatology", "persistence_logistic"],
    }
}


class RescoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = _script()
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        cls.results = {}
        for rule in ("weighted", "unweighted"):
            declaration = replace(_load(), weighted_miss=pj.load_weighted_miss(applied=(rule == "weighted")))
            cls.results[rule] = pj.judge(declaration, grids, forecasts, calendar=series.dates)

    def test_the_tables_carry_every_line_the_rulings_add(self):
        text = self.script.markdown(
            self.results["weighted"], self.results["unweighted"], {"readings": {"weighted": {}, "unweighted": {}}}, DOCUMENT
        )
        for needle in (
            "Weighted rule in force", "Tier 1 at each lead alone", "Inside and outside 2018-19",
            "equal weight per regime", "Tier 3: the regimes tested", "| sharp |",
        ):
            self.assertIn(needle, text)

    def test_tier_three_lists_the_regimes_tested_and_not(self):
        table = self.script.tier3(self.results["weighted"]["candidates"]["sharp"])
        # The synthetic declaration tests a regime from one pressure day on (calibration_min_pressure_days = 1).
        self.assertEqual(set(table["tested"]), {"a", "b"})
        self.assertEqual(table["reported"], {})

    def test_the_cross_check_flags_a_figure_that_moved(self):
        result = self.results["unweighted"]
        cell = self.script.near_cell(result["candidates"]["sharp"])
        b1 = {
            h: {
                "onsets_flagged": lead["onsets_flagged"],
                "false_alarms_per_onset_flat": lead["false_alarms_per_onset"]["flat"]["mean"],
                "false_alarms_per_onset_weighted": lead["false_alarms_per_onset"]["weighted"]["mean"],
            }
            for h, lead in cell["per_lead"].items()
        }
        outside = cell["early_years"]["outside"]
        old = {
            "b2": {
                "onsets_flagged": cell["onsets_flagged"], "recall": cell["recall"]["mean"],
                "false_alarms_per_onset_flat": cell["pooled_false_alarms_per_onset"],
                "false_alarms_per_onset_weighted": cell["pooled_weighted_false_alarms_per_onset"],
            },
            "b1": b1,
            "e": {"outside_2018_19": {"onsets_flagged": outside["onsets_flagged"], "recall": outside["recall"]["mean"]}},
        }
        readings = {"readings": {"unweighted": {"sharp": old}, "weighted": {}}}
        agree = self.script.cross_check(result, readings, "unweighted")
        self.assertTrue(agree and all(c["agree"] for c in agree))
        old["b2"]["false_alarms_per_onset_flat"] += 0.5
        moved = [c for c in self.script.cross_check(result, readings, "unweighted") if not c["agree"]]
        self.assertEqual([c["what"] for c in moved], ["b2 flat false alarms per onset"])


if __name__ == "__main__":
    unittest.main()
