"""The setup diagnostic (#480): does the evaluation setup explain the misses?

Reported-only measurements on the pressure-day judge. They change no bar, no declaration and no
published figure. The declaration is `metadata/setup_diagnostic.json`.

Mutation record
---------------
The one guard here is `require_window`: no day after the declared last scored day (2025-12-31) is read
(`docs/decisions/lockbox.md`). Applied in a scratch copy, the unmutated suite green before and after:

1. In `repo_model/setup_diagnostic.py`, `require_window`, replace `if late:` with `if False:`. Killed:
   `test_a_day_after_the_last_scored_day_is_refused`, with `AssertionError` (`LookAheadError not raised`).
"""

import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import pressure
from repo_model import setup_diagnostic as sd
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "setup_diagnostic.json").read_text())


def business_days(start, count):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class WindowGuard(unittest.TestCase):
    def test_days_up_to_the_last_scored_day_pass(self):
        sd.require_window([date(2025, 12, 30), date(2025, 12, 31)], date(2025, 12, 31))

    def test_a_day_after_the_last_scored_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            sd.require_window([date(2025, 12, 31), date(2026, 1, 2)], date(2025, 12, 31))


class Episodes(unittest.TestCase):
    def setUp(self):
        self.days = business_days(date(2020, 1, 6), 30)
        self.spread = [0.0] * 30
        for k in (8, 9, 10, 14, 20):
            self.spread[k] = 7.0

    def test_five_calm_days_open_an_episode_only_after_a_quiet_week(self):
        found = sd.episodes(self.days, self.spread, self.days, tau=5, calm=5)
        # day 14 follows pressure on day 10 only four panel days earlier: not an episode
        self.assertEqual(found, [self.days[8], self.days[20]])

    def test_a_shorter_calm_rule_adds_the_second_burst(self):
        found = sd.episodes(self.days, self.spread, self.days, tau=5, calm=3)
        self.assertEqual(found, [self.days[8], self.days[14], self.days[20]])

    def test_the_default_rule_is_the_published_onset_rule(self):
        rows = [
            DailyObservation(date=d, values={"sofr": 1.0 + s / 100.0, "iorb": 1.0})
            for d, s in zip(self.days, self.spread)
        ]
        published = pressure.onsets(rows, 5.0, self.days)
        found = sd.episodes(self.days, [r.spread_bps for r in rows], self.days, tau=5, calm=pressure.ONSET_QUIET_DAYS)
        self.assertEqual(tuple(found), published)

    def test_a_threshold_is_strict_and_read_on_whole_basis_points(self):
        spread = [0.0] * 30
        spread[8] = 5.0000000004
        spread[15] = 5.6
        found = sd.episodes(self.days, spread, self.days, tau=5, calm=5)
        self.assertEqual(found, [self.days[15]])

    def test_only_scored_days_can_be_episodes(self):
        found = sd.episodes(self.days, self.spread, self.days[10:], tau=5, calm=5)
        self.assertEqual(found, [self.days[20]])

    def test_comparison_lists_appearing_and_disappearing_days(self):
        base = [self.days[8], self.days[20]]
        other = [self.days[8], self.days[14]]
        self.assertEqual(sd.compare(base, other), {"kept": [self.days[8]], "appear": [self.days[14]], "disappear": [self.days[20]]})


class Training(unittest.TestCase):
    def test_counts_pressure_days_and_onsets_inside_the_training_window_only(self):
        days = business_days(date(2020, 1, 6), 30)
        spread = [0.0] * 30
        for k in (8, 9, 10, 20):
            spread[k] = 7.0
        seen = sd.training_counts(days, spread, last=days[12], tau=5, calm=5)
        self.assertEqual(seen, {"first": days[0], "last": days[12], "pressure_days": 3, "onsets": 1})

    def test_an_empty_window_is_refused(self):
        days = business_days(date(2020, 1, 6), 5)
        with self.assertRaises(ValueError):
            sd.training_counts(days, [0.0] * 5, last=date(2019, 1, 1), tau=5, calm=5)

    def test_the_refit_in_force_is_the_block_of_21_scored_days(self):
        scored = business_days(date(2020, 1, 6), 60)
        block = sd.refit_block(scored, scored[45], step=21)
        self.assertEqual((block["first_index"], block["last_index"]), (42, 59))
        self.assertEqual(block["first"], scored[42])


class Target(unittest.TestCase):
    def test_a_change_that_is_not_a_multiple_of_25_bp_is_technical(self):
        for change, technical in ((20, True), (-5, True), (-30, True), (5, True), (25, False), (-50, False), (-100, False), (75, False)):
            self.assertEqual(sd.is_technical(change), technical, change)

    def test_level_changes_are_found_and_the_renaming_is_not_one(self):
        days = business_days(date(2020, 1, 6), 6)
        iorb = [1.0, 1.0, 1.2, 1.2, 1.2, 1.15]
        sofr = [1.0, 1.0, 1.1, 1.1, 1.1, 1.1]
        found = sd.iorb_changes(days, iorb, sofr)
        self.assertEqual([(c["date"], c["change_bps"]) for c in found], [(days[2], 20), (days[5], -5)])
        self.assertEqual(found[0]["mechanical_spread_shift_bps"], -20)

    def test_quantiles_of_a_small_sample(self):
        self.assertEqual(sd.quantiles([4, 1, 3, 2, 5], [0.0, 0.5, 1.0]), [1, 3, 5])


class Integrity(unittest.TestCase):
    def setUp(self):
        self.days = business_days(date(2020, 1, 6), 12)
        self.columns = ["sofr", "tga"]
        self.rows = [{"sofr": 1.0 + 0.01 * k, "tga": 100.0 + (k // 5)} for k in range(12)]

    def test_a_missing_weekday_is_a_gap_unless_it_is_a_holiday(self):
        days = [d for d in self.days if d != self.days[4]]
        rows = [r for d, r in zip(self.days, self.rows) if d != self.days[4]]
        found = sd.window_integrity(days, rows, self.days[9], 8, [], ["sofr"], ["tga"])
        self.assertEqual(found["gaps"], [self.days[4].isoformat()])
        held = sd.window_integrity(days, rows, self.days[9], 8, [self.days[4]], ["sofr"], ["tga"])
        self.assertEqual(held["gaps"], [])

    def test_a_repeated_daily_value_is_a_forward_fill(self):
        self.rows[6]["sofr"] = self.rows[5]["sofr"]
        found = sd.window_integrity(self.days, self.rows, self.days[9], 8, [], ["sofr"], ["tga"])
        self.assertEqual(found["repeats"], {"sofr": [self.days[6].isoformat()]})

    def test_a_row_copied_from_the_day_before_is_a_forward_fill(self):
        rows = [dict(r, volume=500.0 + k) for k, r in enumerate(self.rows)]
        rows[6] = dict(rows[5])
        found = sd.window_integrity(self.days, rows, self.days[9], 8, [], ["sofr"], ["tga"], copy_columns=["sofr", "volume"])
        self.assertEqual(found["copied_rows"], [self.days[6].isoformat()])
        self.assertFalse(found["blinds_a_model"])
        copied_decision_day = sd.window_integrity(self.days, rows, self.days[7], 8, [], ["sofr"], ["tga"], copy_columns=["sofr", "volume"])
        self.assertTrue(copied_decision_day["blinds_a_model"])

    def test_a_blank_cell_is_reported(self):
        self.rows[8]["sofr"] = None
        found = sd.window_integrity(self.days, self.rows, self.days[9], 8, [], ["sofr"], ["tga"])
        self.assertEqual(found["blanks"], {"sofr": [self.days[8].isoformat()]})
        self.assertTrue(found["blinds_a_model"])

    def test_a_weekly_column_is_stale_after_seven_calendar_days(self):
        self.rows = [{"sofr": 1.0 + 0.01 * k, "tga": 100.0} for k in range(12)]
        found = sd.window_integrity(self.days, self.rows, self.days[11], 3, [], ["sofr"], ["tga"])
        self.assertEqual(found["stale_weekly"], {"tga": (self.days[10] - self.days[0]).days})
        self.assertTrue(found["blinds_a_model"])

    def test_a_clean_window_blinds_nothing(self):
        found = sd.window_integrity(self.days, self.rows, self.days[9], 8, [], ["sofr"], ["tga"])
        self.assertFalse(found["blinds_a_model"])


class Revisions(unittest.TestCase):
    def test_a_vintage_that_differs_is_a_revision(self):
        first = {date(2020, 1, 8): 100.0, date(2020, 1, 15): 101.0}
        latest = {date(2020, 1, 8): 100.0, date(2020, 1, 15): 103.5}
        found = sd.revisions([date(2020, 1, 8), date(2020, 1, 15)], first, latest)
        self.assertEqual(found, [{"date": "2020-01-15", "first": 101.0, "latest": 103.5}])


class Units(unittest.TestCase):
    def test_a_series_in_millions_is_rescaled_to_billions(self):
        reference = {date(2020, 1, 1): 1.5, date(2020, 1, 8): 2.5}
        later = {date(2020, 1, 1): 1500.0, date(2020, 1, 8): 2500.0, date(2020, 1, 15): 3000.0}
        self.assertEqual(sd.same_unit(reference, later), {date(2020, 1, 1): 1.5, date(2020, 1, 8): 2.5, date(2020, 1, 15): 3.0})

    def test_a_revision_inside_one_unit_is_kept(self):
        reference = {date(2020, 1, 1): 100.0, date(2020, 1, 8): 200.0}
        later = {date(2020, 1, 1): 100.0, date(2020, 1, 8): 203.0}
        self.assertEqual(sd.same_unit(reference, later), later)


class Declaration(unittest.TestCase):
    def test_the_declared_last_day_is_before_the_lockbox(self):
        self.assertLess(date.fromisoformat(DECLARED["scoring"]["last_day"]), date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
