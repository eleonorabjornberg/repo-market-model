"""The published distribution as the `blend_equal` blend (#491), read off its record.

The record `docs/runs/published_distribution_blend_equal_daily_h1.json` is `blend_equal` as #455 declared and
scored it, written as a daily record beside the published model's. These tests need no panel: they read the
record, the published daily record and #455's stored score. Re-scoring from the panel is
`scripts/blend_equal_491.py score`.
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "runs"
LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]


def _load(name):
    spec = importlib.util.spec_from_file_location(name + "_t", ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class BlendEqualRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load("blend_equal_491")
        cls.record = _json(RUNS / "published_distribution_blend_equal_daily_h1.json")
        cls.published = _json(RUNS / "published_distribution_daily_h1.json")
        cls.score = _json(ROOT / "docs" / "pivot" / "evidence" / "turning_point_variant" / "score.json")

    def test_same_days_and_outcomes_as_the_published_record_to_2025(self):
        base = [d for d in self.published["days"] if d["date"] <= "2025-12-31"]
        mine = self.record["days"]
        self.assertEqual([d["date"] for d in mine], [d["date"] for d in base])
        self.assertEqual([d["actual_bps"] for d in mine], [d["actual_bps"] for d in base])

    def test_no_2026_day_is_scored(self):
        self.assertLessEqual(self.record["last"], "2025-12-31")
        self.assertTrue(all(d["date"] <= "2025-12-31" for d in self.record["days"]))
        self.assertTrue(all(c["days"] <= 1873 for c in self.record["before_after"]["cells"].values()))

    def test_vectors_do_not_cross(self):
        for d in self.record["days"]:
            self.assertEqual(d["quantiles_bps"], sorted(d["quantiles_bps"]), d["date"])

    def test_the_table_reproduces_455_exactly(self):
        cells = self.record["before_after"]["cells"]
        for name, cell in cells.items():
            stored = self.score["crps"][name]
            self.assertEqual(cell["days"], stored["days"], name)
            self.assertEqual(cell["crps_before"], stored["mean_crps"]["published"], name)
            self.assertEqual(cell["crps_after"], stored["mean_crps"]["blend_equal"], name)
            self.assertEqual(cell["gain"], stored["gain_over_published"]["blend_equal"], name)
        self.assertEqual(cells["all"]["gain"]["mean"], self.score["primary"]["blend_equal"]["mean"])
        self.assertEqual(self.record["before_after"]["coverage"]["after"],
                         self.score["coverage"]["all"]["blend_equal"])

    def test_the_record_scores_to_its_own_table(self):
        from repo_model.metrics import crps_from_quantiles

        days = self.record["days"]
        mean = sum(crps_from_quantiles(LEVELS, d["quantiles_bps"], d["actual_bps"]) for d in days) / len(days)
        self.assertAlmostEqual(mean, self.record["before_after"]["cells"]["all"]["crps_after"], places=12)

    def test_the_old_record_is_left_as_it_is_and_the_pin_is_not_read(self):
        self.assertEqual(self.record["base_record"], "docs/runs/published_distribution_daily_h1.json")
        self.assertIn("live pin are not read or changed", self.record["decides"])

    def test_the_page_is_the_record_rendered(self):
        page = (ROOT / "docs" / "blend_equal_491.md").read_text(encoding="utf-8")
        self.assertEqual(page, self.mod.render(self.record))


class CheckDaysTests(unittest.TestCase):
    """The guard that keeps 2026 days out of the record.

    Recorded mutation (#491): in `check_days`, `d["date"] > END.isoformat()` -> `d["date"] > "2999-01-01"`;
    `test_a_2026_day_is_refused` then failed with `AssertionError: ValueError not raised`.
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = _load("blend_equal_491")

    @staticmethod
    def day(iso, actual=1.0, q=None):
        return {"date": iso, "actual_bps": actual, "quantiles_bps": q or [0.0, 1.0, 2.0, 3.0, 4.0]}

    def test_the_same_days_pass(self):
        base = [self.day("2025-12-30"), self.day("2025-12-31")]
        self.mod.check_days(base, [self.day("2025-12-30"), self.day("2025-12-31")])

    def test_a_2026_day_is_refused(self):
        base = [self.day("2025-12-31"), self.day("2026-01-02")]
        with self.assertRaises(ValueError):
            self.mod.check_days(base, [self.day("2025-12-31"), self.day("2026-01-02")])

    def test_other_days_a_different_outcome_and_a_crossing_vector_are_refused(self):
        base = [self.day("2025-12-30"), self.day("2025-12-31")]
        with self.assertRaises(ValueError):
            self.mod.check_days(base, [self.day("2025-12-31")])
        with self.assertRaises(ValueError):
            self.mod.check_days(base, [self.day("2025-12-30", actual=2.0), self.day("2025-12-31")])
        with self.assertRaises(ValueError):
            self.mod.check_days(base, [self.day("2025-12-30", q=[3.0, 1.0, 2.0, 3.0, 4.0]), self.day("2025-12-31")])


if __name__ == "__main__":
    unittest.main()
