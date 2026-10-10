"""The setup sensitivity diagnostics (#482): arithmetic and the declaration they are read under.

Reported-only measurements on top of the judge of #375 as amended by #407. They change no rule, no
declaration and no published figure. The declaration is `metadata/setup_sensitivity.json`.

Mutation record
---------------
The one guard here is `select_cutoff_weighted`: a cut-off is chosen from a refit's training window alone, as
`pressure_judge.select_cutoff` does (`docs/decisions/lockbox.md`, `docs/decisions/information-set.md`). Applied in a
scratch copy of `repo_model/setup_sensitivity.py`, the unmutated suite green before and after:

1. Replace `if late:` with `if False:` in `select_cutoff_weighted`. Killed:
   `test_a_window_past_the_training_end_is_refused` and `test_a_window_with_a_day_but_no_training_end_is_refused`,
   both with `AssertionError` (`LookAheadError not raised`).
"""

import json
import math
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import pressure_judge as pj
from repo_model import setup_sensitivity as ss
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "setup_sensitivity.json").read_text())
ONSETS = json.loads((ROOT / "metadata" / "onset_diagnostics.json").read_text())


def days(n):
    return [date(2019, 1, 1) + timedelta(days=k) for k in range(n)]


class DeclarationTests(unittest.TestCase):
    def test_the_rows_are_the_five_tier_one_rows(self):
        self.assertEqual(DECLARED["rows"]["chosen"], ONSETS["false_alarms"]["rows"]["chosen"])

    def test_only_days_before_2026_are_scored(self):
        self.assertLess(date.fromisoformat(DECLARED["scoring"]["last_day"]), date(2026, 1, 1))

    def test_the_cadences_and_combiners_differ_from_the_declared_ones(self):
        judge = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())
        self.assertNotIn(judge["cutoff_rule"]["refit_every"], DECLARED["refit_cadence"]["every"])
        self.assertEqual(DECLARED["week_ahead_combiner"]["declared"], judge["tiers"]["week_ahead"]["combine"])
        self.assertNotEqual(DECLARED["week_ahead_combiner"]["other"], judge["tiers"]["week_ahead"]["combine"])


class DownweightTests(unittest.TestCase):
    def test_the_period_gets_its_share_of_the_weight(self):
        flags = [True] * 6 + [False] * 14
        weights = ss.downweights(flags, 0.2)
        inside = sum(w for w, f in zip(weights, flags) if f)
        self.assertAlmostEqual(inside / sum(weights), 0.2)
        self.assertEqual(set(weights[6:]), {1.0})

    def test_a_window_with_one_side_only_is_not_rebalanced(self):
        self.assertEqual(ss.downweights([True] * 3, 0.2), [1.0] * 3)
        self.assertEqual(ss.downweights([False] * 3, 0.2), [1.0] * 3)

    def test_a_share_outside_zero_one_is_refused(self):
        for bad in (0.0, 1.0, -0.1):
            with self.assertRaises(ValueError):
                ss.downweights([True, False], bad)


class WeightedCutoffTests(unittest.TestCase):
    P = [0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
    PRESSURE = [1, 0, 0, 1, 0, 0, 1]
    ONSET = [1, 0, 0, 1, 0, 0, 1]

    def call(self, weights, limit=2.0, window=None, end=None):
        window = days(7) if window is None else window
        return ss.select_cutoff_weighted(
            limit, days=window, probabilities=self.P, pressure=self.PRESSURE, onset=self.ONSET,
            weights=weights, training_end=window[-1] if end is None else end,
        )

    def test_unit_weights_are_the_judges_cutoff(self):
        declaration = pj.load_declaration()
        for limit in (0.0, 0.5, 1.0, 2.0):
            judged = pj.select_cutoff(
                declaration.__class__(**{**declaration.__dict__, "cutoff_false_alarms_at_most": limit}),
                days=days(7), probabilities=self.P, pressure=self.PRESSURE, onset=self.ONSET,
                training_end=days(7)[-1],
            )
            self.assertEqual(self.call([1.0] * 7, limit), judged)

    def test_weights_change_the_cutoff(self):
        # Unit weights: 3 onsets, 4 false alarms at the lowest cut-off: 4/3 <= 2 so 0.4 flags everything.
        self.assertEqual(self.call([1.0] * 7), 0.4)
        # False alarms weighing 3 each: at 0.4 there are 12 weighted false alarms over 3 onsets (4 > 2), at 0.6 6/2 (3 > 2),
        # at 0.7 3/2 is within the limit with two onsets caught.
        self.assertEqual(self.call([1, 3, 3, 1, 3, 3, 1], limit=2.0), 0.7)

    def test_a_window_with_no_weighted_onset_never_flags(self):
        self.assertTrue(math.isinf(ss.select_cutoff_weighted(
            2.0, days=days(2), probabilities=[0.9, 0.1], pressure=[0, 0], onset=[0, 0],
            weights=[1.0, 1.0], training_end=days(2)[-1],
        )))

    def test_a_window_past_the_training_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            self.call([1.0] * 7, end=days(7)[3])

    def test_a_window_with_a_day_but_no_training_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            ss.select_cutoff_weighted(
                2.0, days=days(2), probabilities=[0.9, 0.1], pressure=[1, 0], onset=[1, 0],
                weights=[1.0, 1.0], training_end=None,
            )

    def test_lengths_and_weights_are_checked(self):
        with self.assertRaises(ValueError):
            self.call([1.0] * 6)
        with self.assertRaises(ValueError):
            self.call([1.0] * 6 + [0.0])


class GroupTests(unittest.TestCase):
    def test_tier_one_by_group(self):
        groups = ["a", "a", "a", "b", "b"]
        onset = [1, 0, 1, 1, 0]
        caught = [1, 0, 0, 1, 0]
        alarms = {1: [0, 1, 0, 0, 1], 2: [0, 1, 1, 0, 0]}
        got = ss.tier_one_by_group(groups, onset, caught, alarms)
        self.assertEqual(got["a"]["onsets"], 2)
        self.assertEqual(got["a"]["onsets_flagged"], 1)
        self.assertEqual(got["a"]["worst_false_alarms"], 2)
        self.assertEqual(got["a"]["worst_false_alarms_per_onset"], 1.0)
        self.assertEqual(got["b"]["recall"], 1.0)
        self.assertEqual(got["b"]["false_alarms_by_horizon"], {1: 1, 2: 0})

    def test_a_group_without_onsets_has_no_rate(self):
        got = ss.tier_one_by_group(["a", "a"], [0, 0], [0, 0], {1: [1, 0]})
        self.assertIsNone(got["a"]["recall"])
        self.assertIsNone(got["a"]["worst_false_alarms_per_onset"])

    def test_flag_rate_per_year(self):
        got = ss.flag_rate_by_group(["a", "a", "b"], [1, 0, 1], 252)
        self.assertEqual(got["a"]["flags_per_year"], 126.0)
        self.assertEqual(got["b"]["flags_per_year"], 252.0)

    def test_changed_onsets_lists_only_onsets_that_differ(self):
        got = ss.changed_onsets(days(4), [1, 1, 0, 1], [1, 0, 1, 1], [0, 0, 0, 1])
        self.assertEqual(got, [{"day": "2019-01-01", "declared_flagged": True, "other_flagged": False}])


class ChooseCutoffsWithTests(unittest.TestCase):
    def test_the_judges_selector_gives_the_judges_cutoffs(self):
        from test_pressure_judge import Series, _load

        series = Series()
        declaration = _load()
        grid = series.grid(1)
        forecast = series.forecast("sharp", 1, [0.8 if y else 0.1 for y in series.y5], [0.6 if y else 0.0 for y in series.y10])

        def selector(**kwargs):
            return pj.select_cutoff(declaration, **kwargs)

        (mine,) = ss.choose_cutoffs_with(declaration, {1: grid}, [forecast], series.dates, selector)
        (theirs,) = pj.choose_cutoffs(declaration, {1: grid}, [forecast], series.dates)
        self.assertEqual(mine.cutoffs, theirs.cutoffs)
        self.assertEqual(mine.cutoff_rule, theirs.cutoff_rule)


if __name__ == "__main__":
    unittest.main()
