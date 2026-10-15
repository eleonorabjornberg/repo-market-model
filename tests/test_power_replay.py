"""The power-by-replay study (H1 step 3, #754): `scripts/power_replay.py`.

The rule is `docs/research/power-replay-754.md`. These tests cover the script's parts on small inputs and its agreement
with the rule's text; the study's own result is `docs/research/power-replay-754/result.json`, made by `run` and checked
by `check`.

**Recorded mutation** (CLAUDE.md), 15 October 2026, in a disposable copy of the tree, CPython 3.11,
`PYTHONDONTWRITEBYTECODE=1`, applied by `sed` and confirmed by `grep`: `power_replay.require_study_window`, the guard
`if late:` changed to `if False:`. `StudyWindowTests.test_a_day_after_the_study_end_is_refused` failed with
`AssertionError: LookAheadError not raised`.
"""

import importlib.util
import json
import math
import random
import sys
import unittest
from datetime import date
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("power_replay_script", ROOT / "scripts" / "power_replay.py")
pr = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pr
spec.loader.exec_module(pr)

RULE = ROOT / "docs" / "research" / "power-replay-754.md"
RESULT = ROOT / "docs" / "research" / "power-replay-754" / "result.json"


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            pr.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])

    def test_the_study_end_itself_is_allowed(self):
        pr.require_study_window([date(2025, 12, 31), date(2018, 6, 29)])


class EProcessTests(unittest.TestCase):
    def test_a_clear_gain_is_detected(self):
        rng = random.Random(1)
        d = [0.5 + rng.gauss(0, 0.2) for _ in range(250)]
        b = [1.0] * 250
        test, gated = pr.detect_c(d, b, scale=max(abs(v) for v in d))
        self.assertTrue(test and gated)

    def test_no_gain_is_rarely_detected(self):
        rng = random.Random(2)
        hits = 0
        for _ in range(400):
            d = [rng.gauss(0, 1) for _ in range(125)]
            hits += pr.detect_c(d, [1.0] * 125, scale=max(abs(v) for v in d))[0]
        self.assertLessEqual(hits / 400, 0.05)

    def test_a_difference_beyond_the_scale_is_refused(self):
        with self.assertRaises(ValueError):
            pr.detect_c([2.0, 0.1], [1.0, 1.0], scale=1.0)

    def test_the_gate_withholds_a_small_skill(self):
        rng = random.Random(3)
        d = [0.05 + rng.gauss(0, 0.01) for _ in range(250)]
        test, gated = pr.detect_c(d, [10.0] * 250, scale=max(abs(v) for v in d))
        self.assertTrue(test)
        self.assertFalse(gated)


class DieboldMarianoTests(unittest.TestCase):
    def test_the_lag_is_a_tenth_of_the_window(self):
        self.assertEqual([pr.dm_lag(n) for n in (60, 125, 250, 500)], [6, 12, 25, 50])

    def test_the_fixed_b_value_exceeds_the_normal_one_and_grows_with_the_ratio(self):
        small = pr.dm_critical(60, 2, draws=4000)
        large = pr.dm_critical(60, 20, draws=4000)
        self.assertGreater(small, 1.645)
        self.assertGreater(large, small)

    def test_a_series_with_no_variance_is_undefined_not_detected(self):
        self.assertEqual(pr.detect_b([0.0] * 60, [1.0] * 60, 60, 2.0), (False, False, True))


class FamilyATests(unittest.TestCase):
    def test_a_zero_series_is_undefined_not_detected(self):
        test, gated, undefined = pr.detect_a([0.0] * 60, [1.0] * 60, (14, 30, 60), {30: 2.0, 60: 2.0})
        self.assertEqual((test, gated, undefined), (False, False, True))

    def test_a_clear_gain_is_detected_at_the_last_look(self):
        rng = random.Random(4)
        d = [1.0 + rng.gauss(0, 0.1) for _ in range(60)]
        test, gated, undefined = pr.detect_a(d, [10.0] * 60, (14, 30, 60), {30: 3.0, 60: 2.0})
        self.assertTrue(test and gated and not undefined)

    def test_the_matched_and_circular_generators_differ(self):
        rng = random.Random(5)
        series = [rng.gauss(0, 1) + (3.0 if (i // 20) % 2 else 0.0) for i in range(300)]
        circular = pr.window_statistics_gen(series, 60, (30,), 400, 1, "circular")[30]
        matched = pr.window_statistics_gen(series, 60, (30,), 400, 1, "stationary")[30]
        self.assertNotEqual(circular, matched)

    def test_an_unknown_generator_is_refused(self):
        with self.assertRaises(pr.RuleError):
            pr.window_statistics_gen([1.0, 2.0, 3.0] * 30, 20, (10,), 5, 1, "normal")


class NullSeriesTests(unittest.TestCase):
    def test_the_sign_flip_keeps_every_magnitude(self):
        d = [float(i + 1) for i in range(100)]
        flipped = pr.flip_blocks(d, 17)
        self.assertEqual([abs(v) for v in flipped], d)
        self.assertNotEqual(flipped, d)

    def test_the_sign_flip_flips_whole_blocks(self):
        flipped = pr.flip_blocks([1.0] * 100, 5)
        for start in range(0, 100, pr.FLIP_BLOCK):
            self.assertEqual(len(set(flipped[start:start + pr.FLIP_BLOCK])), 1)

    def test_the_demeaned_series_has_a_zero_mean(self):
        self.assertAlmostEqual(sum(pr.demean([1.0, 2.0, 6.0])), 0.0)


class ReplayTests(unittest.TestCase):
    def test_windows_start_every_fifth_day(self):
        self.assertEqual(pr.window_starts(100, 60), [0, 5, 10, 15, 20, 25, 30, 35, 40])

    def test_a_series_shorter_than_a_window_has_no_windows(self):
        self.assertEqual(pr.window_starts(59, 60), [])

    def test_the_interval_contains_the_share(self):
        flags = [1] * 30 + [0] * 70
        share, low, high = pr.share_interval(flags, block=5, rng=random.Random(1))
        self.assertAlmostEqual(share, 0.3)
        self.assertLessEqual(low, share)
        self.assertGreaterEqual(high, share)

    def test_a_constant_share_has_a_degenerate_interval(self):
        self.assertEqual(pr.share_interval([0] * 40, block=5, rng=random.Random(1)), (0.0, 0.0, 0.0))

    def test_regimes_follow_the_directive(self):
        self.assertEqual([pr.regime_of(date(y, 3, 1)) for y in (2018, 2019, 2020, 2024, 2025)],
                         ["2018-19", "2018-19", "2020-24", "2020-24", "2025"])


class RuleAgreementTests(unittest.TestCase):
    def test_the_constants_are_the_rules(self):
        text = RULE.read_text(encoding="utf-8")
        self.assertEqual(pr.WINDOW_LENGTHS, (60, 125, 250))
        self.assertEqual(pr.SYNTHETIC_LENGTHS, (60, 125, 250, 500))
        self.assertEqual(pr.STEP, 5)
        self.assertEqual(pr.FLIP_BLOCK, 20)
        self.assertEqual(pr.DM_RATIO, 0.1)
        for token in ("every 5th day", "blocks of 20 consecutive days", "round(0.1 N)", "`K_t >= 20`",
                      "2,000 paths per cell", "20,000"):
            self.assertIn(token, text)
        self.assertEqual(pr.PATHS, 2000)
        self.assertEqual(pr.WINDOWS, 20000)
        self.assertEqual(round(1 / sp.ALPHA), 20)

    def test_the_grids_are_the_rules(self):
        self.assertEqual(pr.FULL_DELTAS, (0.0, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50))
        self.assertEqual(pr.OTHER_DELTAS, (0.0, 0.03, 0.10))

    def test_a_committed_result_was_made_under_this_rule(self):
        if not RESULT.exists():
            self.skipTest("no result committed yet")
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(result["rule_sha256"], pr.sha256(RULE))
        self.assertLessEqual(result["pool"]["last"], pr.STUDY_END.isoformat())


if __name__ == "__main__":
    unittest.main()
