"""#934's ordinary-day result restated on the five declared regimes (#1023; H1 regime splits, over H5 step 3 data).

Written before `scripts/ordinary_day_p5_1023.py`: it fails with `ModuleNotFoundError` until the script exists.

Mutation record (the regime boundary guard): in `scripts/ordinary_day_p5_1023.py`, making `regime_of` return the
three-regime `base.rr.regime_of(day)` (a line inserted at the top of its body) makes
`BoundaryTests.test_a_day_is_assigned_to_the_declared_regime` fail with `AssertionError` (2020-06-01 reads `2020-24`, not `2020`);
restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
SCORE_934 = ROOT / "docs" / "pivot" / "ordinary-day-p5-844" / "score.json"


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_t1023", ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = _load("ordinary_day_p5_1023")

DECLARED = (
    ("2018-19", date(2018, 1, 1), date(2019, 12, 31)),
    ("2020", date(2020, 1, 1), date(2020, 12, 31)),
    ("2021-23", date(2021, 1, 1), date(2023, 12, 31)),
    ("2024", date(2024, 1, 1), date(2024, 12, 31)),
    ("2025-26", date(2025, 1, 1), date(2026, 12, 31)),
)


class BoundaryTests(unittest.TestCase):

    def test_the_declared_boundaries_are_pinned_to_the_file(self):
        document = json.loads(SPLITS.read_text(encoding="utf-8"))
        read = tuple((r["label"], date.fromisoformat(r["first"]), date.fromisoformat(r["last"])) for r in document["regimes"])
        self.assertEqual(read[:5], DECLARED)
        self.assertEqual(script.REGIMES, DECLARED)

    def test_a_day_is_assigned_to_the_declared_regime(self):
        cases = {
            date(2018, 4, 3): "2018-19", date(2019, 12, 31): "2018-19", date(2020, 1, 1): "2020", date(2020, 6, 1): "2020",
            date(2020, 12, 31): "2020", date(2021, 1, 4): "2021-23", date(2023, 12, 29): "2021-23", date(2024, 1, 2): "2024",
            date(2024, 12, 31): "2024", date(2025, 1, 2): "2025-26", date(2025, 12, 31): "2025-26",
        }
        for day, label in cases.items():
            self.assertEqual(script.regime_of(day), label, day)

    def test_a_day_outside_every_scored_regime_is_refused(self):
        for day in (date(2017, 12, 29), date(2027, 6, 1)):
            with self.assertRaises(ValueError):
                script.regime_of(day)

    def test_the_three_regime_cell_that_crosses_regimes_is_the_one_marked(self):
        self.assertEqual(script.CROSS_REGIME_CELLS, {"2020-24"})


def _cells(days_by_regime):
    rows = []
    for regime, (start, n) in days_by_regime.items():
        for i in range(n):
            day = date.fromordinal(start.toordinal() + i)
            y = 1 if i % 4 == 0 else 0
            rows.append({
                "day": day.isoformat(), "y": y, "regime": "stale",
                "ordinary": {"non_ordinary": True, "scheduled": True},
                "p": {"persistence_logistic": 0.3 if y else 0.2, "as_of_spread": float(i % 7), "spread_mr_level10": 0.5 if y else 0.1,
                      "spread_mr_ctx": 0.4, "c_two_part_new": 0.2 + 0.01 * (i % 3), "gbm_funding": 0.6 if y else 0.15},
            })
    return rows


class ScoreTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rows = _cells({"2018-19": (date(2018, 4, 3), 40), "2020": (date(2020, 3, 2), 20), "2025-26": (date(2025, 1, 2), 30)})
        cls.document = {"horizons": {str(h): rows for h in range(1, 6)}, "panel_sha256": "x", "decision_days": 90, "walks": {}}
        cls.result = script.score_document(cls.document, replications=20)

    def test_the_stale_three_regime_label_in_the_cells_is_ignored(self):
        cells = self.result["definitions"]["non_ordinary"]["1"]
        self.assertEqual(set(cells) - {"pooled"}, {"2018-19", "2020", "2025-26"})
        self.assertEqual(cells["2020"]["days"], 20)

    def test_a_cell_with_too_few_pressure_days_has_no_auroc(self):
        rows = _cells({"2024": (date(2024, 2, 1), 8)})
        result = script.score_document({"horizons": {str(h): rows for h in range(1, 6)}, "panel_sha256": "x", "decision_days": 8, "walks": {}},
                                       replications=5)
        cell = result["definitions"]["non_ordinary"]["1"]["2024"]
        self.assertEqual(cell["pressure_days"], 2)
        self.assertIsNone(cell["rows"]["gbm_funding"]["auroc_minus_reference"]["value"])

    def test_a_day_after_the_declared_end_is_refused(self):
        rows = _cells({"2025-26": (date(2025, 12, 20), 30)})
        with self.assertRaises(Exception) as caught:
            script.score_document({"horizons": {"1": rows}, "panel_sha256": "x", "decision_days": 30, "walks": {}}, replications=5)
        self.assertEqual(type(caught.exception).__name__, "LookAheadError")


class PageTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rows = _cells({"2018-19": (date(2018, 4, 3), 40), "2020": (date(2020, 3, 2), 20), "2025-26": (date(2025, 1, 2), 30)})
        document = {"horizons": {str(h): rows for h in range(1, 6)}, "panel_sha256": "x", "decision_days": 90, "walks": {}}
        cls.result = script.score_document(document, replications=20)
        cls.three = json.loads(SCORE_934.read_text(encoding="utf-8"))
        cls.text = script.render(cls.result, cls.three)

    def test_the_three_regime_table_is_kept_with_its_cross_regime_cell_marked(self):
        self.assertIn("| 2018-19 | 2020-24 (cross-regime, not a regime result) | 2025-26 |", self.text)
        self.assertNotIn("| 2018-19 | 2020-24 | 2025-26 |", self.text)

    def test_the_five_regime_table_comes_first_and_the_page_is_not_a_verdict(self):
        self.assertLess(self.text.index("| 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |"), self.text.index("(cross-regime, not a regime result)"))
        self.assertIn("not a verdict", self.text.split("\n## ", 1)[0].lower())

    def test_the_kept_figures_are_the_committed_figures(self):
        cell = self.three["definitions"]["non_ordinary"]["1"]["2020-24"]["rows"]["gbm_funding"]["auroc_minus_reference"]
        self.assertIn(script.base.fmt(cell, signed=True), self.text)


class StudentizedTests(unittest.TestCase):

    Y = [1 if i % 4 == 0 else 0 for i in range(60)]
    MODEL = [0.8 if y else 0.2 + 0.01 * (i % 5) for i, y in enumerate(Y)]
    REFERENCE = [0.5 + 0.1 * ((i * 7) % 5) for i in range(60)]

    def test_the_influence_series_has_the_auroc_as_its_statistic_and_mean_zero(self):
        theta, psi = script.auroc_influence(self.MODEL, self.Y)
        self.assertAlmostEqual(theta, script.base.auroc(self.MODEL, self.Y))
        self.assertAlmostEqual(sum(psi) / len(psi), 0.0)

    def test_ties_count_half(self):
        theta, _ = script.auroc_influence([1.0, 1.0, 1.0, 1.0], [1, 0, 1, 0])
        self.assertAlmostEqual(theta, 0.5)

    def test_no_auroc_without_both_kinds_of_day(self):
        self.assertIsNone(script.auroc_influence([0.1, 0.2], [0, 0]))

    def test_the_bound_is_below_the_point_value_and_reproducible(self):
        a = script.studentized_bound(self.MODEL, self.REFERENCE, self.Y, seed=7, replications=200)
        b = script.studentized_bound(self.MODEL, self.REFERENCE, self.Y, seed=7, replications=200)
        self.assertEqual(a, b)
        point = script.base.auroc(self.MODEL, self.Y) - script.base.auroc(self.REFERENCE, self.Y)
        self.assertLess(a["lower_bound"], point)
        self.assertEqual(a["draws_used"] + a["draws_dropped"], 200)
        self.assertEqual(a["lag"], 10)
        self.assertAlmostEqual(a["level"], 0.95)

    def test_a_better_model_has_a_higher_bound_than_a_worse_one(self):
        good = script.studentized_bound(self.MODEL, self.REFERENCE, self.Y, seed=3, replications=200)
        worse = script.studentized_bound(self.REFERENCE, self.MODEL, self.Y, seed=3, replications=200)
        self.assertGreater(good["lower_bound"], worse["lower_bound"])

    def test_a_cell_with_no_variation_has_no_bound(self):
        self.assertIsNone(script.studentized_bound(self.MODEL, self.MODEL, self.Y, seed=1, replications=50))

    def test_score_document_attaches_the_bound_beside_the_percentile_interval(self):
        rows = _cells({"2018-19": (date(2018, 4, 3), 60)})
        result = script.score_document({"horizons": {"1": rows}, "panel_sha256": "x", "decision_days": 60, "walks": {}}, replications=30)
        entry = result["definitions"]["non_ordinary"]["1"]["2018-19"]["rows"]["c_two_part_new"]["auroc_minus_reference"]
        self.assertIn("interval", entry)
        self.assertIn("lower_bound", entry["studentized"])

    def test_the_page_shows_the_bound_and_records_the_ruling_not_a_question(self):
        rows = _cells({"2018-19": (date(2018, 4, 3), 60)})
        result = script.score_document({"horizons": {"1": rows}, "panel_sha256": "x", "decision_days": 60, "walks": {}}, replications=30)
        text = script.render(result, json.loads(SCORE_934.read_text(encoding="utf-8")))
        self.assertIn("studentized lower bound", text)
        self.assertIn("6340379028", text)
        self.assertNotIn("Marked question", text)
        self.assertNotIn("is hers", text)
        self.assertIn("over target days", text)


class CommittedPageTests(unittest.TestCase):

    def test_the_committed_page_is_what_render_writes_from_the_committed_result(self):
        result = json.loads((ROOT / "docs" / "research" / "ordinary-day-p5-1023" / "result.json").read_text(encoding="utf-8"))
        three = json.loads(SCORE_934.read_text(encoding="utf-8"))
        page = (ROOT / "docs" / "research" / "ordinary-day-p5-1023-result.md").read_text(encoding="utf-8")
        self.assertEqual(page, script.render(result, three))

    def test_the_committed_two_edge_regimes_equal_the_committed_three_regime_figures(self):
        result = json.loads((ROOT / "docs" / "research" / "ordinary-day-p5-1023" / "result.json").read_text(encoding="utf-8"))
        three = json.loads(SCORE_934.read_text(encoding="utf-8"))
        for lead, cells in result["definitions"]["non_ordinary"].items():
            for regime in ("2018-19", "2025-26"):
                for name, row in cells[regime]["rows"].items():
                    kept = three["definitions"]["non_ordinary"][lead][regime]["rows"][name]
                    self.assertEqual(row.get("auroc_minus_reference", {}).get("value"), kept.get("auroc_minus_reference", {}).get("value"), (lead, regime, name))


if __name__ == "__main__":
    unittest.main()


class ProvisionalMarkAndStudentizedColumnTests(unittest.TestCase):
    """#1169: the page is marked provisional under the register, and the studentized column is complete once re-scored.

    Recorded mutation (the page's provisional mark, a staleness-class guard on what the page claims): deleting the
    `PROVISIONAL_NOTE` paragraph from `render` in scripts/ordinary_day_p5_1023.py made
    `test_the_page_is_marked_provisional_under_the_register` fail with AssertionError (the page no longer contained
    "provisional: calendar not read at the target day").
    """

    RESULT = ROOT / "docs" / "research" / "ordinary-day-p5-1023" / "result.json"
    CELLS = ROOT / "docs" / "research" / "ordinary-day-p5-1023" / "cells.json"

    def test_the_page_is_marked_provisional_under_the_register(self):
        result = json.loads(self.RESULT.read_text(encoding="utf-8"))
        three = json.loads(SCORE_934.read_text(encoding="utf-8"))
        self.assertIn("provisional: calendar not read at the target day", script.render(result, three))
        page = (ROOT / "docs" / "research" / "ordinary-day-p5-1023-result.md").read_text(encoding="utf-8")
        self.assertIn("provisional: calendar not read at the target day", page)
        self.assertIn("docs/research/provisional-calendar-register.md", page)
        self.assertIn("#934", page.split("## Five declared regimes")[0])

    def test_every_five_regime_cell_with_an_interval_carries_the_studentized_bound_once_rescored(self):
        if not self.CELLS.exists():
            self.skipTest("the Mac re-score (needs-mac on #1169) has not been committed: no cells.json yet")
        result = json.loads(self.RESULT.read_text(encoding="utf-8"))
        missing = []
        for definition in result["definitions"].values():
            for lead, cells in definition.items():
                for regime, cell in cells.items():
                    for name in script.base.MODEL_ROWS:  # the page's model rows; neither the reference nor the raw-spread diagnostic
                        entry = cell["rows"][name].get("auroc_minus_reference")
                        if entry is not None and entry.get("interval") is not None and "studentized" not in entry:
                            missing.append((lead, regime, name))
        self.assertEqual(missing, [])

