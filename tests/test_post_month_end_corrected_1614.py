"""The re-issued post-month-end split of (s3c-ann-net)'s misses (#1614): `scripts/post_month_end_corrected_1614.py`.

#1613 found that #1611's studentized interval threw away every resample that drew no miss and still reported an interval when 90% were left.
The tests fix the corrected arithmetic on hand cases: a resample with no variance is kept, at t = -infinity (or +infinity, or 0 on a tie), so
that a rare-event share's upper end can reach 1; a series with no variation still has no studentized interval; the share printed beside a cell
count is misses over cells, not a mean of per-day shares; the exploratory score interval (a Wilson interval on an effective number of cells,
the design effect read from the Newey-West variance of the daily shares, never below 1) matches its closed form; and the comparison with the
#1611 figures lists the rows that moved.

Recorded mutations (the guards and rules this script adds):

* `t_value`, the line `return math.copysign(math.inf, resampled_mean - mean) if resampled_mean != mean else 0.0` replaced by `return None`
  (the old drop, in effect): `test_a_resample_with_no_variance_is_kept_at_infinity` fails with `AssertionError` (`None != -inf`), and the four
  interval tests (`test_every_resample_is_kept_and_the_no_miss_ones_are_counted` and three more) fail with `TypeError` (a `None` t-value cannot be
  sorted); restored, all pass.
* `check_cells_per_day`, the test `if len(set(counts.values())) > 1:` replaced by `if False:`: `test_unequal_cells_per_day_are_refused_in_a_scored_window`
  fails with `AssertionError` (`ValueError not raised`); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


script = _load("post_month_end_corrected_1614", "post_month_end_corrected_1614_script")
old = _load("post_month_end_split_1611", "post_month_end_split_1611_for_1614_tests")

G05, G50, G95 = script.G05, script.G50, script.G95


def cell(t: str, h: int, y: float, *, low: float = -1.0, mid: float = 0.0, high: float = 1.0, regime: str = "2021-23") -> dict:
    q = [0.0] * len(script.q.GRID)
    q[G05], q[G50], q[G95] = low, mid, high
    return {"d": "2021-01-01", "h": h, "t": t, "y": y, "q": q, "regime": regime}


def rare(n: int = 60, hits=(7,)) -> list:
    return [1.0 if i in hits else 0.0 for i in range(n)]


class KeptResampleTests(unittest.TestCase):
    def test_a_resample_with_no_variance_is_kept_at_infinity(self):
        self.assertEqual(script.t_value(resampled_mean=0.0, mean=0.05, variance=0.0, n=40), -math.inf)
        self.assertEqual(script.t_value(resampled_mean=1.0, mean=0.05, variance=0.0, n=40), math.inf)
        self.assertEqual(script.t_value(resampled_mean=0.05, mean=0.05, variance=0.0, n=40), 0.0)

    def test_a_resample_with_variance_is_studentized_by_its_own_error(self):
        self.assertAlmostEqual(script.t_value(resampled_mean=0.30, mean=0.10, variance=4.0, n=100), 0.20 / math.sqrt(4.0 / 100))

    def test_every_resample_is_kept_and_the_no_miss_ones_are_counted(self):
        values = rare()
        out = script.studentized(values, reps=400, seed=5, clip=(0.0, 1.0))
        self.assertEqual(out["resamples"], 400)
        self.assertGreater(out["no_variance"], 0)  # one miss in sixty days: some resamples draw none
        self.assertEqual(len(out["interval"]), 3)

    def test_the_upper_end_of_a_rare_share_reaches_one_where_1611_did_not(self):
        values = rare(60, hits=(7, 30))
        new = script.studentized(values, reps=2000, seed=5, clip=(0.0, 1.0))["interval"]
        was = old.studentized_interval(values, reps=2000, seed=5)
        self.assertEqual(new[2], 1.0)
        self.assertLess(was[2], 1.0)
        self.assertAlmostEqual(new[0], 2 / 60)
        self.assertLessEqual(new[1], new[0])

    def test_a_series_with_no_variation_has_no_studentized_interval(self):
        out = script.studentized([0.0] * 40, reps=200, seed=1, clip=(0.0, 1.0))
        self.assertIsNone(out["interval"])

    def test_a_short_series_has_no_interval(self):
        self.assertIsNone(script.studentized([0.0, 1.0] * 5, reps=100, seed=1, clip=(0.0, 1.0))["interval"])

    def test_without_a_dropped_resample_the_interval_equals_1611s(self):
        values = [0.2 * (i % 5 == 0) + 0.1 * (i % 3 == 0) for i in range(80)]
        new = script.studentized(values, reps=300, seed=11, clip=(0.0, 1.0))
        self.assertEqual(new["no_variance"], 0)
        self.assertEqual(new["interval"], old.studentized_interval(values, reps=300, seed=11))

    def test_the_percentile_of_a_sorted_list_with_infinite_ends(self):
        self.assertEqual(script.percentile([-math.inf, -math.inf, 1.0, 2.0], 0.1), -math.inf)
        self.assertEqual(script.percentile([-1.0, 0.0, 1.0, math.inf], 0.9), math.inf)
        self.assertEqual(script.percentile([-math.inf, -math.inf, 1.0], 0.25), -math.inf)
        self.assertAlmostEqual(script.percentile([1.0, 2.0, 3.0], 0.5), 2.0)

    def test_an_unclipped_interval_with_an_unbounded_end_stores_it_as_none(self):
        # a series whose resamples are mostly constant: 3 distinct values would still vary; two days of signal in forty
        values = rare(40, hits=(5,))
        out = script.studentized(values, reps=600, seed=2, clip=None)["interval"]
        self.assertIsNone(out[2])  # no clip: the unbounded end is not a number
        self.assertIsNotNone(out[0])


class ScoreIntervalTests(unittest.TestCase):
    Z = 1.6448536269514722

    def test_the_closed_form_for_no_miss_and_no_dependence(self):
        lo, hi = script.score_interval(0, 100, 1.0)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, self.Z ** 2 / (100 + self.Z ** 2), places=9)

    def test_the_interval_holds_the_point_and_stays_in_the_unit_interval(self):
        lo, hi = script.score_interval(4, 80, 1.0)
        self.assertLess(lo, 4 / 80)
        self.assertGreater(hi, 4 / 80)
        self.assertGreaterEqual(lo, 0.0)
        lo, hi = script.score_interval(80, 80, 1.0)
        self.assertAlmostEqual(hi, 1.0, places=9)

    def test_a_larger_design_effect_widens_it(self):
        a = script.score_interval(5, 100, 1.0)
        b = script.score_interval(5, 100, 4.0)
        self.assertLess(b[0], a[0])
        self.assertGreater(b[1], a[1])

    def test_the_design_effect_is_one_for_independent_cells_and_never_below_one(self):
        # forty days, five cells each, misses spread so that the daily shares are not serially dependent
        series = [0.2 if i % 8 == 0 else 0.0 for i in range(40)]
        self.assertGreaterEqual(script.design_effect(series, cells=200), 1.0)
        self.assertEqual(script.design_effect([0.0] * 40, cells=200), 1.0)  # no miss: not estimable, held at 1

    def test_misses_that_come_together_in_time_give_a_design_effect_above_one(self):
        clustered = [1.0] * 8 + [0.0] * 32
        spread = [1.0 if i % 5 == 0 else 0.0 for i in range(40)]
        self.assertGreater(script.design_effect(clustered, cells=40), script.design_effect(spread, cells=40))
        self.assertGreater(script.design_effect(clustered, cells=40), 1.5)

    def test_leads_that_miss_together_give_a_design_effect_near_the_leads_per_day(self):
        # every day's five leads agree: day shares are 0 or 1, 8 days in 80
        series = [1.0 if i in (3, 21, 40, 58, 66, 70, 74, 78) else 0.0 for i in range(80)]
        d = script.design_effect(series, cells=400)
        self.assertGreater(d, 3.0)
        self.assertLess(d, 6.5)


class EntryTests(unittest.TestCase):
    def test_the_share_is_misses_over_cells_not_a_mean_of_daily_shares(self):
        cells = [cell("2026-02-02", h, 5.0 if h == 1 else 0.0) for h in (1, 2, 3, 4, 5)] + [cell("2026-03-02", h, 0.0) for h in (1, 2, 3, 4)]
        e = script.entry(cells, reps=0, seed=1)
        self.assertEqual(e["cells"], 9)
        self.assertEqual(e["up"]["misses"], 1)
        self.assertAlmostEqual(e["up"]["share"], 1 / 9)  # the mean of the daily shares would be 0.1

    def test_unequal_cells_per_day_are_refused_in_a_scored_window(self):
        cells = [cell("2021-02-02", h, 0.0) for h in (1, 2, 3, 4, 5)] + [cell("2021-03-02", h, 0.0) for h in (1, 2, 3, 4)]
        with self.assertRaises(ValueError):
            script.check_cells_per_day(cells)

    def test_equal_cells_per_day_pass(self):
        script.check_cells_per_day([cell("2021-02-02", h, 0.0) for h in (1, 2, 3, 4, 5)] + [cell("2021-03-02", h, 0.0) for h in (1, 2, 3, 4, 5)])

    def test_a_rare_miss_group_carries_both_intervals_and_the_count_of_resamples_without_a_miss(self):
        cells = []
        for i in range(30):
            t = f"{2018 + i // 12}-{i % 12 + 1:02d}-02"
            for h in (1, 2):
                cells.append(cell(t, h, 5.0 if (i == 6 and h == 1) else 0.0))
        e = script.entry(cells, reps=400, seed=3)
        up = e["up"]
        self.assertEqual(up["misses"], 1)
        self.assertEqual(up["interval"][1], 1.0)
        self.assertGreater(up["no_variance_resamples"], 0)
        lo, hi = up["score_interval"][:2]
        self.assertLess(lo, up["share"])
        self.assertGreater(hi, up["share"])
        self.assertGreaterEqual(up["design_effect"], 1.0)

    def test_a_group_with_no_miss_has_no_studentized_interval_but_a_score_interval(self):
        cells = [cell(f"{2018 + i // 12}-{i % 12 + 1:02d}-02", 1, 0.0) for i in range(30)]
        e = script.entry(cells, reps=200, seed=3)
        self.assertIsNone(e["low"]["interval"])
        self.assertEqual(e["low"]["score_interval"][0], 0.0)
        self.assertGreater(e["low"]["score_interval"][1], 0.0)
        self.assertEqual(e["low"]["vs_nominal"], "no interval")

    def test_a_thin_group_has_neither_interval(self):
        cells = [cell(f"2021-{m:02d}-02", 1, 5.0) for m in range(1, 11)]
        e = script.entry(cells, reps=100, seed=3)
        self.assertIsNone(e["up"]["interval"])
        self.assertIsNone(e["up"]["score_interval"])


class ComparisonTests(unittest.TestCase):
    def tails(self, interval, vs):
        return {"misses": 3, "share": 0.05, "interval": interval, "vs_nominal": vs}

    def test_rows_whose_interval_moved_are_listed_with_both_figures(self):
        before = {"windows": {"development": {"scopes": {"all": {"1": {"3": {"days": 60, "cells": 60,
                  "low": self.tails([0.003, 0.054], "holds 0.05"), "up": self.tails([0.01, 0.1], "holds 0.05")}}}}, "by_regime": {}}}}
        after = {"windows": {"development": {"scopes": {"all": {"1": {"3": {"days": 60, "cells": 60,
                 "low": self.tails([0.003, 1.0], "holds 0.05") | {"no_variance_resamples": 700},
                 "up": self.tails([0.01, 0.1], "holds 0.05") | {"no_variance_resamples": 0}}}}}, "by_regime": {}}}}
        rows = script.compare(before, after)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tail"], "low")
        self.assertEqual(rows[0]["before"], [0.003, 0.054])
        self.assertEqual(rows[0]["after"], [0.003, 1.0])
        self.assertEqual(rows[0]["no_variance_resamples"], 700)
        self.assertFalse(rows[0]["reading_changed"])
        self.assertTrue(rows[0]["visible"])

    def test_a_difference_beyond_the_third_decimal_is_stored_but_not_visible_and_storage_rounding_is_not_a_change(self):
        before = {"windows": {"development": {"scopes": {"all": {"1": {"3": {"days": 60, "cells": 60,
                  "low": self.tails([0.013741, 0.066382], "holds 0.05"), "up": self.tails([0.0107, 0.1], "holds 0.05")}}}}, "by_regime": {}}}}
        after = {"windows": {"development": {"scopes": {"all": {"1": {"3": {"days": 60, "cells": 60,
                 "low": self.tails([0.0137931234, 0.066382], "holds 0.05") | {"no_variance_resamples": 148},
                 "up": self.tails([0.01070004, 0.09999999], "holds 0.05") | {"no_variance_resamples": 0}}}}}, "by_regime": {}}}}
        rows = script.compare(before, after)
        self.assertEqual([r["tail"] for r in rows], ["low"])  # the up row differs only by the 6-place storage of #1611
        self.assertFalse(rows[0]["visible"])

    def test_a_row_that_gained_an_interval_or_changed_its_reading_is_flagged(self):
        before = {"windows": {"development": {"scopes": {}, "by_regime": {"2": {"2021-23": {"days": 36, "cells": 180,
                  "low": self.tails([0.0, 0.045], "below 0.05"), "up": self.tails(None, "no interval")}}}}}}
        after = {"windows": {"development": {"scopes": {}, "by_regime": {"2": {"2021-23": {"days": 36, "cells": 180,
                 "low": self.tails([0.0, 1.0], "holds 0.05") | {"no_variance_resamples": 708},
                 "up": self.tails([0.01, 1.0], "holds 0.05") | {"no_variance_resamples": 5}}}}}}}
        rows = {r["tail"]: r for r in script.compare(before, after)}
        self.assertTrue(rows["low"]["reading_changed"])
        self.assertEqual(rows["low"]["reading_before"], "below 0.05")
        self.assertEqual(rows["low"]["reading_after"], "holds 0.05")
        self.assertIsNone(rows["up"]["before"])


class SplitAndPageTests(unittest.TestCase):
    def cells(self):
        out = []
        for year in (2019, 2021):
            for month in range(1, 13):
                for day in (1, 2, 3):
                    t = f"{year}-{month:02d}-{day:02d}"
                    if date.fromisoformat(t).weekday() >= 5:
                        continue
                    for h in (1, 2):
                        out.append(cell(t, h, 2.0 if h == 1 else 0.0, regime="2018-19" if year == 2019 else "2021-23"))
        return out

    def test_the_split_has_one_entry_per_business_day_and_lead(self):
        res = script.split(self.cells(), reps=40, seed=1)
        self.assertEqual(sorted(res), ["1", "2", "3"])
        for leads in res.values():
            self.assertEqual(sorted(leads), ["1", "2", "all"])

    def test_the_page_states_the_kept_resample_rule_and_marks_the_second_interval_exploratory(self):
        score = script.score_cells({"development": self.cells(), "2026": [cell("2026-02-02", 1, 5.0), cell("2026-02-02", 2, 0.0), cell("2026-03-02", 1, 0.0)]},
                                   reps=40, seed=1, previous=None)
        json.dumps(score)
        text = script.page(score)
        self.assertIn("#1614", text)
        self.assertIn("every resample is kept", text.lower())
        self.assertIn("exploratory", text)
        self.assertIn("misses over cells", text)
        self.assertIn("#1611", text)

    def test_the_2026_share_beside_the_cell_count_is_misses_over_cells(self):
        later = [cell("2026-02-02", h, 5.0 if h == 1 else 0.0) for h in (1, 2, 3, 4, 5)] + [cell("2026-03-02", h, 0.0) for h in (1, 2, 3, 4)]
        score = script.score_cells({"development": self.cells(), "2026": later}, reps=0, seed=1, previous=None)
        pooled = score["windows"]["2026"]["scopes"]["all"]["1"]["all"]
        self.assertEqual(pooled["cells"], 9)
        self.assertAlmostEqual(pooled["up"]["share"], 1 / 9)


class NoteTests(unittest.TestCase):
    """The dated note under the known limit is on the page and quotes the figures of `result.json`; the validation report states none."""

    def test_the_page_note_quotes_the_corrected_pooled_figures(self):
        result = json.loads((REPO / "docs/research/post-month-end-corrected-1614/result.json").read_text(encoding="utf-8"))
        text = (REPO / "docs/research/post-month-end-corrected-1614-result.md").read_text(encoding="utf-8")
        note = text[text.index("## Note of 15 November 2026"):text.index("## What is measured")]
        pooled = result["windows"]["development"]["scopes"]["all"]
        for bday, tail in (("1", "up"), ("2", "up"), ("3", "low")):
            e = pooled[bday]["all"][tail]
            self.assertIn(f"({e['share']:.3f})", note)
            self.assertIn(f"[{e['interval'][0]:.3f}, {e['interval'][1]:.3f}]", note)
        regime = result["windows"]["development"]["by_regime"]["2"]["2021-23"]["low"]
        self.assertEqual(regime["interval"][1], 1.0)
        self.assertIn("[0.000, 1.000]", note)

    def test_the_page_is_the_script_output_of_the_result_file(self):
        result = json.loads((REPO / "docs/research/post-month-end-corrected-1614/result.json").read_text(encoding="utf-8"))
        self.assertEqual((REPO / "docs/research/post-month-end-corrected-1614-result.md").read_text(encoding="utf-8"), script.page(result))


if __name__ == "__main__":
    unittest.main()
