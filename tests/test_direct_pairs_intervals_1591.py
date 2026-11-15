"""The dated note on the #1086 decomposition page and the interval re-read of its walks (#1591, H5 step 3).

The note quotes only what `docs/research/direct-pairs-diagnosis-1086/decompose.json` holds, and leaves the page's own text as it was.
The re-read (`scripts/direct_pairs_intervals_1591.py`) reads walks that exist on Eleonora's Mac only, so what is pinned here is its arithmetic on hand
cases and its two guards.

Recorded mutation (the guard `require_current_day_types`): `if not turn_days.in_force():` changed to `if False:`:
`DayTypeTests.test_the_retired_flags_are_refused` fails with `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("direct_pairs_intervals_1591_script", REPO / "scripts" / "direct_pairs_intervals_1591.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import turn_days  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

PAGE = REPO / "docs" / "research" / "decomposition-1086-result.md"
DECOMPOSE = json.loads((REPO / "docs" / "research" / "direct-pairs-diagnosis-1086" / "decompose.json").read_text(encoding="utf-8"))
DIRECT_OVER = "gbm_funding_cal_direct over gbm_funding"


class NoteTests(unittest.TestCase):
    def setUp(self):
        self.page = PAGE.read_text(encoding="utf-8")
        self.note = self.page.split("## Note of 12 November 2026", 1)[1].split("\n## ", 1)[0]
        self.outside = DECOMPOSE["pairs"][DIRECT_OVER]["outside 2021-23"]

    def test_the_note_is_dated_and_names_its_issue(self):
        self.assertIn("## Note of 12 November 2026", self.page)
        self.assertIn("#1591", self.note)

    def test_the_note_quotes_the_figures_it_cites(self):
        for name in ("year 2018", "year 2019", "year 2020", "year 2021", "ordinary", "tax_date", "all", "month_end", "quarter_end", "year 2024", "year 2025"):
            self.assertIn(f"{self.outside.get(name, DECOMPOSE['pairs'][DIRECT_OVER]['2021-23'].get(name))['total']:+.4f}", self.note, msg=name)
        self.assertIn(f"{self.outside['ordinary']['by_band']['centre']:+.4f}", self.note)

    def test_the_note_says_the_page_groups_by_the_retired_flags(self):
        self.assertIn("retired", self.note)
        self.assertIn("month_end", self.note)
        self.assertIn("quarter_end", self.note)
        self.assertIn("#1161", self.note)

    def test_the_note_says_no_interval_and_no_verdict(self):
        self.assertIn("no interval", self.note.lower())
        self.assertIn("development data", self.note.lower())

    def test_the_pages_own_text_is_unchanged(self):
        for sentence in (
            "The 2021-23 loss does not come from the calendar columns misfiring on pressure days.",
            "The locus is narrow and the same for both variants",
            "**No interval is attached.**",
            "| year 2019 | 1250 | +0.1743 | +0.0141 | +0.0307 | +0.1779 | -0.0070 | -0.0414 |",
        ):
            self.assertIn(sentence, self.page)


class DayTypeTests(unittest.TestCase):
    def test_the_retired_flags_are_refused(self):
        with turn_days.legacy_reading():
            with self.assertRaises(ValueError):
                script.require_current_day_types()

    def test_the_turn_labels_in_force_are_read(self):
        script.require_current_day_types()


class WindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2026, 1, 2)])


class DailyScoreTests(unittest.TestCase):
    def test_a_target_day_is_the_mean_over_its_leads(self):
        d = date(2022, 3, 1)
        cells = [(d, 1.0, 3.0), (d, 2.0, 3.0), (date(2022, 3, 2), 5.0, 5.0)]
        out = script.target_day_scores(cells)
        self.assertEqual(out[d], (1.5, 3.0))
        self.assertEqual(out[date(2022, 3, 2)], (5.0, 5.0))


class GroupTests(unittest.TestCase):
    def test_a_day_is_in_its_year_type_window_and_cross_groups(self):
        names = script.groups_of(date(2019, 6, 4), "ordinary")
        self.assertEqual(set(names), {"all", "outside 2021-23", "year 2019", "type ordinary", "year 2019 / ordinary"})
        names = script.groups_of(date(2022, 6, 30), "quarter_end_turn")
        self.assertEqual(set(names), {"all", "2021-23", "year 2022", "type quarter_end_turn", "year 2022 / pressure"})


class IntervalTests(unittest.TestCase):
    def series(self, n, shift):
        start = date(2020, 1, 1)
        days = [start + timedelta(days=k) for k in range(n)]
        base = {d: 1.0 + 0.01 * (k % 7) for k, d in enumerate(days)}
        return {d: (v, v + shift + 0.02 * ((k * 5) % 3 - 1)) for k, (d, v) in enumerate(base.items())}

    def test_the_excess_is_candidate_minus_reference_and_the_interval_brackets_it(self):
        out = script.excess_interval(self.series(120, 0.5), seed=7, draws=300)
        self.assertAlmostEqual(out["excess"], 0.5, delta=0.02)
        self.assertLess(out["lower"], out["excess"])
        self.assertGreater(out["upper"], out["excess"])
        self.assertEqual(out["days"], 120)

    def test_a_group_with_too_few_days_has_no_interval(self):
        out = script.excess_interval(self.series(script.sp.HAC_LAG, 0.5), seed=7, draws=300)
        self.assertIsNone(out["lower"])
        self.assertIn("too few", out["note"])
        self.assertAlmostEqual(out["excess"], 0.5, delta=0.02)


if __name__ == "__main__":
    unittest.main()
