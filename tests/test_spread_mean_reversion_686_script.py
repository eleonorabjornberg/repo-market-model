"""The helpers of `scripts/spread_mean_reversion_686.py` (#686; H5, development tier).

Written after the script, which is measurement code; its one guard, `require_scored_days`, has a recorded mutation:
replacing `if day > last:` with `if day > last + timedelta(days=400):` made
`ScopeTests.test_a_day_after_the_declared_end_is_refused` fail with `AssertionError` ("LookAheadError not raised");
restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("spread_mean_reversion_686", ROOT / "scripts" / "spread_mean_reversion_686.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


class ScopeTests(unittest.TestCase):

    def test_a_day_after_the_declared_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2025, 12, 31), date(2026, 1, 2)])

    def test_the_declared_last_day_is_scored(self):
        script.require_scored_days([date(2025, 12, 31)])

    def test_a_locked_day_is_refused_even_when_the_end_is_moved(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2026, 9, 4)], last=date(2027, 1, 1))

    def test_the_declaration_ends_where_the_script_does(self):
        declaration = json.loads((ROOT / "metadata" / "spread_distribution_686.json").read_text())
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["limits"]["max_variants"], len(declaration["variants"]))


class StatisticsTests(unittest.TestCase):

    def days(self, n):
        start = date(2020, 1, 1)
        return [start + timedelta(days=i) for i in range(n)]

    def test_interval_is_the_5th_and_95th_percentile(self):
        draws = [float(i) for i in range(101)]
        self.assertEqual(script.interval(draws), [5.0, 95.0])

    def test_a_better_candidate_has_positive_skill(self):
        days = self.days(80)
        bench = {d: 2.0 + 0.1 * (i % 5) for i, d in enumerate(days)}
        cand = {d: v - 0.5 - 0.05 * (i % 3) for i, (d, v) in enumerate(bench.items())}
        row = script.run_pairs({"B": bench}, cand, days, draws=300)["B"]
        self.assertGreater(row["skill"], 0.0)
        self.assertGreater(row["difference"], 0.5)
        self.assertGreater(row["skill_interval"][0], 0.0)

    def test_a_benchmark_that_scores_zero_has_undefined_skill_not_a_crash(self):
        days = self.days(40)
        row = script.run_pairs({"B": {d: 0.0 for d in days}}, {d: 0.0 for d in days}, days, draws=50)["B"]
        self.assertIn("undefined", row)
        self.assertEqual(script.skill_text(row), "undefined (benchmark scores 0)")

    def test_groups_keep_each_day_once(self):
        days = self.days(6)
        labels = {d: "a" if i % 2 else "b" for i, d in enumerate(days)}
        grouped = script.group_days(days, labels)
        self.assertEqual(sorted(sum(grouped.values(), [])), days)

    def test_the_five_levels_are_in_the_grid(self):
        self.assertEqual([sp.GRID[i] for i in script.FIVE_AT], list(script.FIVE))


if __name__ == "__main__":
    unittest.main()


class AnchorDayTypeReportTests(unittest.TestCase):
    """#741: skill against B1 is reported by the anchor's day type, with the pooled figure beside it."""

    def result(self):
        def vs(skill):
            row = {"days": 100, "skill": skill, "skill_interval": [skill - 0.01, skill + 0.01],
                   "difference": 0.1, "difference_interval": [0.0, 0.2]}
            return {"B1": row, "B2": row}

        def cell(skill):
            return {"means": {"B1": 2.0, "B2": 2.0, script.NAME: 1.5}, "vs": vs(skill)}

        group = lambda days, skill: {"days": days, "grid_crps": cell(skill), "upper_tail_twcrps": cell(skill)}  # noqa: E731
        return {
            "label": "development, not a verdict", "declaration": "d.json", "panel_sha256": "0" * 64, "draws": 10, "seed": 686,
            "notes": {"scored_decision_days": 1000, "first": "2018-06-29", "last": "2025-12-24", "last_target": "2025-12-31",
                      "candidate_skipped_for_history": 0, "benchmark_missing": [], "refits": 3},
            "primary": {"grid_crps": {"means": cell(0.2)["means"], "vs": vs(0.2), "by_lead": {}},
                        "upper_tail_twcrps": {"means": cell(0.2)["means"], "vs": vs(0.2), "by_lead": {}}},
            "splits": {"regime": {}, "regime_three": {}, "day_type": {},
                       "anchor_day_type": {"ordinary": group(800, 0.01), "quarter_end": group(30, 0.4),
                                           "tax_date": {"days": 5, "note": "fewer than 20 days; not tested"}}},
            "tail": {"tau_bp": 5, "reading": "r", "by_regime": {"ordinary": {}, "all": {}}, "brier_vs": {"ordinary": {}, "all": {}}},
            "published": {"levels": [], "days": 1, "days_without_five_published_leads": 0,
                          "means": {"published": 1.0, script.NAME: 1.0, "B1": 1.0, "B2": 1.0},
                          "candidate_vs": {k: vs(0.0)["B1"] for k in ("published", "B1", "B2")}, "by_lead": {}, "by_regime": {}, "by_day_type": {}},
            "variant_b_632": {"variant": "v", "note": "n", "by_lead": {}},
            "fit": {"refits": [{"fitted_on": "2020-01-02", "phi": 0.5, "pairs": {"1": 10}}]},
        }

    def test_the_report_has_the_pooled_row_beside_each_anchor_type(self):
        text = script.render_report(self.result())
        section = text.split("by the type of the anchor, on the decision day (#741)")[1].split("##")[0]
        self.assertIn("| pooled | 1000 |", section)
        self.assertIn("| quarter_end | 30 |", section)
        self.assertIn("| ordinary | 800 |", section)
        self.assertIn("fewer than 20 days; not tested", section)

    def test_the_page_carries_the_same_split(self):
        import tempfile

        with tempfile.TemporaryDirectory() as folder:
            score, out = Path(folder, "s.json"), Path(folder, "p.md")
            score.write_text(json.dumps(self.result()), encoding="utf-8")
            script.page(type("Args", (), {"score": str(score), "output": str(out)})())
            page = out.read_text(encoding="utf-8")
        self.assertIn("by the type of the anchor", page)
        self.assertIn("| pooled | 1000 |", page)
        self.assertIn("| quarter_end | 30 |", page)
