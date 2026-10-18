"""The power study of scoring protocol v1 (#656, H5 groundwork G4): `scripts/power_study.py`.

The rule is `docs/research/power-study-656.md`. These tests cover the script's parts on small inputs; the study's own
result is `docs/research/power-study-656/result.json`, made by `run`, and checked by `check`.

**Recorded mutation** (CLAUDE.md), 13 October 2026, in a disposable copy of the tree, CPython 3.11,
`PYTHONDONTWRITEBYTECODE=1`, applied by `sed` and confirmed by `grep`: `power_study.development_series`, the guard
`if rows[t + max(sp.HORIZONS)].date > PANEL_END:` changed to `if False:`.
`DevelopmentSeriesTests.test_no_day_after_the_panel_end_is_scored` errored with `LookAheadError` (the lockbox refused
the first day whose target is in the blind tier), instead of the series ending at 2026-09-03.
"""

import importlib.util
import json
import random
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from nightly import nightly
from test_protocol_benchmarks import published_panel

from repo_model import scoring_protocol as sp
from repo_model.data import DailyObservation, next_business_day
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("power_study_script", ROOT / "scripts" / "power_study.py")
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


class CandidateTests(unittest.TestCase):
    def test_the_candidates_skill_against_b1_is_exactly_delta(self):
        rng = random.Random(1)
        s1 = [1.0 + rng.random() for _ in range(300)]
        s2 = [1.0 + rng.random() for _ in range(300)]
        for noise in (1.0, 0.5, 0.25, 0.0):
            d = ps.candidate_differences(s1, s2, 0.03, noise)
            self.assertAlmostEqual(sum(d) / sum(s1), 0.03, places=12)

    def test_noise_scales_the_spread_of_the_differences(self):
        rng = random.Random(2)
        s1 = [1.0 + rng.random() for _ in range(300)]
        s2 = [1.0 + rng.random() for _ in range(300)]
        spread = {n: max(ps.candidate_differences(s1, s2, 0.03, n)) - min(ps.candidate_differences(s1, s2, 0.03, n))
                  for n in (1.0, 0.5, 0.25)}
        self.assertGreater(spread[1.0], spread[0.5])
        self.assertGreater(spread[0.5], spread[0.25])


class DevelopmentSeriesTests(unittest.TestCase):
    def test_the_series_is_inside_the_development_period(self):
        rows = published_panel()["rows"]
        days, s1, s2 = ps.development_series(rows)
        self.assertEqual(len(days), len(s1))
        self.assertEqual(len(days), len(s2))
        self.assertGreaterEqual(days[0], ps.years_after(rows[0].date, 2))
        self.assertLessEqual(days[-1], ps.PANEL_END)
        self.assertTrue(all(value >= 0.0 for value in s1 + s2))

    def test_no_day_after_the_panel_end_is_scored(self):
        rows = list(published_panel()["rows"])
        last = rows[-1]
        day = last.date
        for _ in range(8):
            day = next_business_day(day, 1)
            rows.append(DailyObservation(date=day, values=dict(last.values)))
        days, _, _ = ps.development_series(rows)
        self.assertLessEqual(days[-1], ps.PANEL_END)
        self.assertEqual(days[-1], ps.development_series(published_panel()["rows"])[0][-1])


@nightly
class SimulationTests(unittest.TestCase):
    def series(self, skill):
        rng = random.Random(3)
        s1 = [2.0 + rng.random() for _ in range(400)]
        d = [skill * a + rng.gauss(0.0, 0.02) for a in s1]
        return s1, d

    def test_a_strong_effect_is_detected_by_the_last_checkpoint_and_a_null_is_not(self):
        s1, strong = self.series(0.20)
        got = ps.simulate(s1, strong, paths=12, seed=1, workers=1)
        self.assertEqual(got["power"]["250"], 1.0)
        s1, null = self.series(0.0)
        got = ps.simulate(s1, null, paths=12, seed=1, workers=1)
        self.assertEqual(got["power"]["250"], 0.0)

    def test_look_1_cannot_be_read_with_the_protocols_draws(self):
        self.assertLess(sp.nominal_levels()[0] * sp.DRAWS, 1.0)
        s1, strong = self.series(0.20)
        got = ps.simulate(s1, strong, paths=6, seed=2, workers=1)
        self.assertEqual(got["power"]["60"], 0.0)
        self.assertEqual(got["share_of_paths_with_an_unresolvable_level"], 1.0)

    def test_power_does_not_fall_with_more_days(self):
        s1, d = self.series(0.05)
        got = ps.simulate(s1, d, paths=10, seed=3, workers=1)["power"]
        self.assertLessEqual(got["60"], got["125"])
        self.assertLessEqual(got["125"], got["250"])

    def test_the_same_seed_gives_the_same_study(self):
        s1, d = self.series(0.05)
        self.assertEqual(ps.simulate(s1, d, paths=6, seed=4, workers=1), ps.simulate(s1, d, paths=6, seed=4, workers=1))

    def test_days_needed_is_the_first_checkpoint_at_the_target(self):
        self.assertEqual(ps.days_needed({"60": 0.1, "125": 0.8, "250": 0.95}), 125)
        self.assertIsNone(ps.days_needed({"60": 0.0, "125": 0.2, "250": 0.5}))

    def test_the_normal_approximation_rises_with_the_effect(self):
        s1, small = self.series(0.02)
        _, large = self.series(0.08)
        low = ps.normal_approximation(s1, small, paths=2000, seed=1)
        high = ps.normal_approximation(s1, large, paths=2000, seed=1)
        self.assertLess(low["250"], high["250"])
        self.assertLessEqual(high["125"], high["250"])


class H7mGoalpostTests(unittest.TestCase):
    def test_the_standard_error_falls_with_more_non_events(self):
        self.assertGreater(ps.hanley_mcneil_se(0.65, 10, 100), ps.hanley_mcneil_se(0.65, 10, 1000))

    def test_the_standard_error_of_a_known_case(self):
        # By hand from the formula: Q1 = A/(2-A), Q2 = 2A^2/(1+A), var = (A(1-A) + (n1-1)(Q1-A^2) + (n2-1)(Q2-A^2)) / (n1 n2).
        a = 0.85
        q1, q2 = a / (2 - a), 2 * a * a / (1 + a)
        var = (a * (1 - a) + 50 * (q1 - a * a) + 57 * (q2 - a * a)) / (51 * 58)
        self.assertAlmostEqual(ps.hanley_mcneil_se(a, 51, 58), var**0.5, places=12)
        self.assertAlmostEqual(var**0.5, 0.0381, places=4)


class NullPathTests(unittest.TestCase):
    """The post-hoc size check (`docs/research/power-study-656-addendum.md`)."""

    def test_a_series_with_no_difference_is_rarely_detected_and_never_by_the_gated_rule(self):
        rng = random.Random(5)
        s1 = [2.0 + rng.random() for _ in range(400)]
        d = [rng.gauss(0.0, 0.3) for _ in s1]
        d = [x - sum(d) / len(d) for x in d]
        ps.init_worker(s1, d)
        ungated = [ps.run_null_path((9000 + i,)) for i in range(20)]
        self.assertTrue(all(g is None for _, g in ungated))
        self.assertLessEqual(sum(1 for u, _ in ungated if u is not None), 3)


class CheckTests(unittest.TestCase):
    def test_a_result_made_under_another_rule_text_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "result.json").write_text(
                json.dumps({"rule_sha256": "0" * 64, "development": {"last": "2026-09-03"}}), encoding="utf-8"
            )

            class Args:
                out = tmp

            with self.assertRaises(ValueError):
                ps.check_command(Args)


if __name__ == "__main__":
    unittest.main()
