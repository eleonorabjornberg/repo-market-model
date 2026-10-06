"""The final test's influence table and its wording (#260, review finding 7).

`scripts/final_test_influence.py` reads `docs/runs/final_test_near_blind.json`'s
per-day paired differences and computes, with no new scoring, how much of the
pass a few days carry. The page blocks that print it (`docs/final-test.md` by
`emit_results.py`, the site section by `emit_visual.py`) take every number from
here. The tests pin the figures the second independent review reported, and refuse
the sentence that implied a clean holdout.

Mutation record (`InfluenceTests`, the ordering of the top days): `ordered = sorted(
range(n), key=lambda i: -diffs[i])` in `influence` changed to `key=lambda i: diffs[i]`
(smallest first), confirmed applied by grep; `test_drop_top_five_and_ten` then failed
with `AssertionError` (0.17406 != 0.0251: the means were of the wrong days).
Restored, green.

Mutation record (`WordingTests`, the unhedged sentence): the generator's
`FINAL_TEST_HEDGE` replaced by the old text "a stretch of days that no choice of model
had been made on" in `scripts/emit_results.py`, confirmed applied by grep;
`test_the_unhedged_sentence_does_not_return` then failed with `AssertionError`
(the forbidden sentence was found in the generated block). Restored, green.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECORD = REPO / "docs" / "runs" / "final_test_near_blind.json"
FORBIDDEN = "no choice of model had been made on"


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


influence_script = load_script("final_test_influence")


def record():
    return json.loads(RECORD.read_text(encoding="utf-8"))


class InfluenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = record()
        cls.got = influence_script.influence(cls.record)

    def test_the_mean_and_median_are_the_records(self):
        self.assertAlmostEqual(self.got["mean"], self.record["primary"]["cell"]["mean_difference_bps"], places=9)
        self.assertAlmostEqual(self.got["median"], 0.0122, places=4)
        self.assertEqual((self.got["wins"], self.got["n"]), (87, 169))

    def test_the_top_ten_days_are_dated_and_ordered(self):
        top = self.got["top"]
        self.assertEqual(len(top), 10)
        self.assertEqual([d for d, _ in top[:2]], ["2026-01-05", "2026-01-06"])
        self.assertEqual([v for _, v in top], sorted((v for _, v in top), reverse=True))
        self.assertAlmostEqual(top[0][1], 11.22, places=2)
        self.assertAlmostEqual(top[1][1], 5.13, places=2)

    def test_drop_top_five_and_ten(self):
        self.assertAlmostEqual(self.got["drop"][5], 0.0251, places=4)
        self.assertAlmostEqual(self.got["drop"][10], -0.0354, places=4)

    def test_leave_two_out_uses_the_records_own_bootstrap(self):
        lto = self.got["leave_two_out"]
        interval = self.record["primary"]["cell"]["interval"]
        self.assertEqual((lto["block_length"], lto["seed"], lto["replications"], lto["level"]),
                         (interval["block_length"], interval["seed"], interval["replications"], interval["level"]))
        self.assertAlmostEqual(lto["mean"], 0.078, places=3)
        self.assertAlmostEqual(lto["lower"], -0.014, places=3)
        self.assertAlmostEqual(lto["upper"], 0.180, places=3)

    def test_diebold_mariano_is_the_two_sided_p_of_the_review(self):
        dm = self.got["dm"]
        self.assertEqual(dm["lag"], 4)
        self.assertAlmostEqual(dm["p"], 0.106, places=3)
        self.assertAlmostEqual(dm["plain_p"], 0.052, places=3)

    def test_a_window_that_does_not_average_to_the_cell_is_refused(self):
        bad = record()
        bad["primary"]["window_per_origin"][0]["difference_bps"] += 1.0
        with self.assertRaises(ValueError):
            influence_script.influence(bad)

    def test_a_window_too_short_to_drop_ten_is_refused(self):
        bad = record()
        bad["primary"]["window_per_origin"] = bad["primary"]["window_per_origin"][:12]
        with self.assertRaises(ValueError):
            influence_script.influence(bad)

    def test_the_leap_cell_is_read_from_the_record_or_absent(self):
        cell = influence_script.leap_against_climatology(self.record)
        self.assertAlmostEqual(cell["mean"], 0.0053, places=4)
        self.assertAlmostEqual(cell["lower"], -0.0029, places=4)
        self.assertAlmostEqual(cell["upper"], 0.0137, places=4)
        stripped = record()
        for doc in stripped["events_reported_only"]:
            doc["targets"].pop("leap", None)
        self.assertIsNone(influence_script.leap_against_climatology(stripped))


class WordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = load_script("emit_results")

    def test_the_unhedged_sentence_does_not_return(self):
        block = self.results.final_test_section()
        self.assertNotIn(FORBIDDEN, block)
        self.assertNotIn(FORBIDDEN, (REPO / "docs" / "final-test.md").read_text(encoding="utf-8"))
        self.assertNotIn("The test was fixed before these days were scored", block)

    def test_the_block_names_the_live_record_and_disclaims_stress(self):
        block = self.results.final_test_section()
        self.assertIn("first genuinely blind confirmation", block)
        self.assertIn("does not validate stress performance", block)
        self.assertIn("Influence", block)

    def test_the_site_section_carries_the_same_figures_and_disclaimers(self):
        import sys
        sys.path.insert(0, str(REPO / "src"))
        visual = load_script("emit_visual")
        from repo_model.lockbox import locked_tiers
        data, fills = visual.final_test(visual.run_records(REPO), locked_tiers(REPO / visual.LOCKBOX))
        text = " ".join(str(v) for v in fills.values())
        self.assertNotIn(FORBIDDEN, text)
        self.assertIn("first genuinely blind confirmation", text)
        self.assertIn("does not validate stress performance", text)
        self.assertIn("+0.0251", fills["ft_influence_table"])
        self.assertIn("\u22120.0354", fills["ft_influence_table"])
        self.assertIn("quarter-end window", fills["ft_window_table"])
        self.assertIn("+0.0053", fills["ft_switch"])
        self.assertEqual(data["influence"]["wins"], 87)


if __name__ == "__main__":
    unittest.main()
