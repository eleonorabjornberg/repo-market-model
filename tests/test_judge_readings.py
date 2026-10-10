"""The judge readings (#523): the helpers of `scripts/judge_readings.py`, a scratch measurement.

The script re-reads tier 1 under the readings the forensic audit questioned and changes nothing the judge decides. These
tests pin its helpers on small series: the weight that discounts only the alarms before an episode (#514), the union of
false-alarm days across horizons (#509), the year mask (#510) and the training-window check beside the realised count
(#512).

**Recorded mutation** (CLAUDE.md: each new leakage guard carries one that kills it). `before_only_weights` reads the
pressure days known at the refit and refuses a day after `known_through`. Mutation: in `scripts/judge_readings.py`
`before_only_weights`, replace `if late:` with `if False:`; the failing test was
`test_a_day_after_the_known_instant_is_refused`, which raised `AssertionError` (`LookAheadError not raised`).
"""

import importlib.util
import unittest
from pathlib import Path

from repo_model import pressure_judge as pj
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("judge_readings_script", ROOT / "scripts" / "judge_readings.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RULE = pj.WeightedMiss(
    path="test", sha256="rule", in_force=True, applied=True, bands=((2, 0.25), (5, 0.5)), beyond=1.0
)


class BeforeOnlyWeightTests(unittest.TestCase):
    def test_an_alarm_before_an_episode_is_discounted_by_its_distance_to_it(self):
        weights = _script().before_only_weights(
            RULE, positions=list(range(30)), pressure=[1 if k == 10 else 0 for k in range(30)], known_through=29
        )
        self.assertEqual(weights[8], 0.25)
        self.assertEqual(weights[6], 0.5)
        self.assertEqual(weights[0], 1.0)
        self.assertEqual(weights[10], 0.0)

    def test_an_alarm_after_the_last_pressure_day_counts_in_full(self):
        weights = _script().before_only_weights(
            RULE, positions=list(range(30)), pressure=[1 if k == 10 else 0 for k in range(30)], known_through=29
        )
        self.assertEqual(weights[11], 1.0)
        self.assertEqual(weights[12], 1.0)

    def test_between_two_episodes_only_the_next_one_counts(self):
        pressure = [1 if k in (10, 20) else 0 for k in range(30)]
        weights = _script().before_only_weights(RULE, positions=list(range(30)), pressure=pressure, known_through=29)
        self.assertEqual(weights[11], 1.0)  # the day after an episode: 9 days from the next, beyond the bands
        self.assertEqual(weights[18], 0.25)  # two days before the next one
        # the drafted rule would have discounted day 11 by its distance (1) to the episode behind it
        drafted = pj.false_alarm_weights(RULE, positions=list(range(30)), pressure=pressure, known_through=29)
        self.assertEqual(drafted[11], 0.25)

    def test_a_day_after_the_known_instant_is_refused(self):
        with self.assertRaises(LookAheadError):
            _script().before_only_weights(RULE, positions=[1, 2, 3], pressure=[0, 0, 1], known_through=2)

    def test_the_series_must_agree(self):
        with self.assertRaises(ValueError):
            _script().before_only_weights(RULE, positions=[1, 2], pressure=[0], known_through=2)


class PooledAlarmTests(unittest.TestCase):
    def test_a_day_flagged_at_two_horizons_is_one_false_alarm_day(self):
        flags = {1: [1, 1, 0, 0], 2: [1, 0, 1, 0]}
        pressure = [0, 0, 0, 1]
        self.assertEqual(_script().pooled_false_alarm_days(flags, pressure), [1, 1, 1, 0])

    def test_a_flag_on_a_pressure_day_is_not_a_false_alarm(self):
        self.assertEqual(_script().pooled_false_alarm_days({1: [0, 0, 1]}, [0, 0, 1]), [0, 0, 0])


class YearMaskTests(unittest.TestCase):
    def test_the_mask_splits_the_days_by_calendar_year(self):
        from datetime import date

        days = [date(2019, 12, 31), date(2020, 1, 2), date(2018, 7, 2), date(2025, 1, 2)]
        inside, outside = _script().year_masks(days, (2018, 2019))
        self.assertEqual(inside, [True, False, True, False])
        self.assertEqual(outside, [False, True, False, True])


class TrainingCheckTests(unittest.TestCase):
    def test_the_check_counts_the_flags_a_cutoff_would_have_raised_on_the_window(self):
        # four days, two pressure days; cut-off 0.5 flags days 0, 1 and 3; day 1 is a pressure day.
        check = _script().window_false_alarms_per_onset(
            probabilities=[0.9, 0.7, 0.2, 0.6], pressure=[0, 1, 0, 0], onset=[0, 1, 0, 0], cutoff=0.5, weights=None
        )
        self.assertEqual(check, 2.0)

    def test_a_cutoff_that_flags_nothing_raises_nothing(self):
        check = _script().window_false_alarms_per_onset(
            probabilities=[0.9], pressure=[0], onset=[1], cutoff=float("inf"), weights=None
        )
        self.assertEqual(check, 0.0)

    def test_a_window_without_an_onset_has_no_rate(self):
        check = _script().window_false_alarms_per_onset(
            probabilities=[0.9], pressure=[0], onset=[0], cutoff=0.5, weights=None
        )
        self.assertIsNone(check)

    def test_weights_replace_the_count(self):
        check = _script().window_false_alarms_per_onset(
            probabilities=[0.9, 0.9], pressure=[0, 0], onset=[1, 0], cutoff=0.5, weights=[0.25, 0.5]
        )
        self.assertEqual(check, 0.75)


if __name__ == "__main__":
    unittest.main()
