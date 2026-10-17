"""The `--without-day` option of the four scoring scripts re-read by #882 (finding #798, H5 step 3).

#882 re-runs the scored results of #758, #761 and #688 without decision day 2019-09-18. The option leaves one decision day
out of every window of the existing scoring and changes nothing else; without it a script's output is what it was. These
tests pin the option on each script's `score` command and the cut's refusal of a day that is not scored (a cut that
silently left every day in would report the pooled figure as the figure without the day).

No new leakage or staleness guard: the scripts read no day the lockbox locks and the option only removes a day.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COMPARE = REPO / "scripts" / "without_day_882.py"
SCRIPTS = ("h5_step4_758.py", "spread_mr_variants_761.py", "near_threshold_688.py")


def _compare():
    spec = importlib.util.spec_from_file_location("without_day_882_script", COMPARE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OptionTests(unittest.TestCase):
    def test_each_score_command_takes_the_option(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                done = subprocess.run(
                    [sys.executable, "-B", str(REPO / "scripts" / script), "score", "--help"],
                    capture_output=True, text=True, env={"PYTHONPATH": str(REPO / "src"), "PYTHONDONTWRITEBYTECODE": "1"},
                )
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertIn("--without-day", done.stdout)

    def test_a_day_that_is_not_scored_is_refused(self):
        spec = importlib.util.spec_from_file_location("h5_splits_805_script_882", REPO / "scripts" / "h5_splits_805.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        with self.assertRaises(ValueError):
            module.drop_day([date(2019, 9, 17), date(2019, 9, 19)], date(2019, 9, 18))


class CompareTests(unittest.TestCase):
    """`scripts/without_day_882.py` lines two score files up; it scores nothing."""

    def setUp(self):
        self.m = _compare()

    def test_a_bound_that_crosses_zero_is_flagged_and_one_that_does_not_is_not(self):
        self.assertTrue(self.m.bound_sign_change((0.1, 0.4), (-0.02, 0.4)))
        self.assertTrue(self.m.bound_sign_change((0.0, 0.4), (0.1, 0.4)))
        self.assertFalse(self.m.bound_sign_change((0.1, 0.4), (0.05, 0.3)))
        self.assertFalse(self.m.bound_sign_change(None, (0.05, 0.3)))

    def test_intervals_are_read_in_each_stored_form(self):
        self.assertEqual(self.m.bounds({"skill": 1, "skill_interval_90": [0.1, 0.2]}), (0.1, 0.2))
        self.assertEqual(self.m.bounds({"skill": 1, "skill_lower_95_one_sided": 0.1, "skill_upper_95_one_sided": 0.3, "mean_difference_lower_95_one_sided": 9.0}), (0.1, 0.3))
        self.assertIsNone(self.m.bounds({"skill": 1}))

    def test_records_are_found_at_any_depth_with_their_path(self):
        doc = {"a": {"b": {"skill": 0.1, "n": 3}, "c": [1, 2]}, "headroom": 0.2}
        self.assertEqual([p for p, _ in self.m.records(doc)], ["", "/a/b"])

    def test_the_reproduction_is_the_largest_difference_of_a_figure_or_a_bound(self):
        tracked = {"x": {"skill": 0.2, "skill_interval_90": [0.1, 0.3]}, "y": {"skill": 0.5}}
        rerun = {"x": {"skill": 0.25, "skill_interval_90": [0.1, 0.2]}, "z": {"skill": 0.5}}
        out = self.m.reproduction(tracked, rerun)
        self.assertEqual((out["records_compared"], out["not_in_the_tracked_file"]), (1, 1))
        self.assertAlmostEqual(out["max_abs_difference"], 0.1)

    def test_compare_pairs_each_record_with_its_own_path(self):
        tracked = {"x": {"skill": 0.2, "n": 5, "skill_interval_90": [0.1, 0.3]}}
        without = {"x": {"skill": 0.1, "n": 4, "skill_interval_90": [-0.1, 0.3]}}
        out = self.m.compare("t", tracked, tracked, without)
        self.assertEqual(out["reproduction"]["max_abs_difference"], 0.0)
        (row,) = out["rows"]
        self.assertEqual((row["n"], row["n_without"], row["with"], row["without"]), (5, 4, 0.2, 0.1))
        self.assertTrue(row["bound_sign_change"])


if __name__ == "__main__":
    unittest.main()
