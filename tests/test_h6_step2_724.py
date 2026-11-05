"""`scripts/h6_step2_724.py` (#724; H6 development step 2, development tier): (s3c-ann-net) on #1131's event-day strata, and one risk-date-specialised variant.

Written first, against `metadata/h6_step2_724.json`. The candidate's walk is `scripts/capped_baselines_b2star_1434.py`'s and the strata are
`scripts/h6_design_1131.py`'s; what this study adds is pinned here on hand cases: the variant's scale (its point-in-time estimation and its rescaling), the
coupon flag read as #849 does for the strata, the per-target-day mean over leads, and the reading rules.

**Recorded mutations** (5 November 2026).

1. In `usable_history` (the variant's scale for a decision day may use only cells whose outcome was public at that decision: target row at or before the
   decision day's anchor row), the line

       if target_row <= anchor_row

   was changed to `if target_row <= anchor_row + 3`. `ScaleLookAheadTests.test_a_cell_realised_after_the_anchor_never_moves_the_scale` then failed with
   `LookAheadError` (from `require_realised`, which re-checks every cell the selection returns); restored, it passes.

2. In `evaluation_membership` (a coupon settlement is a risk date for the strata only where its flag was public at the lead-1 decision instant,
   #849), the line

       if coupons > 0.0 and coupon_public:

   was changed to `if coupons > 0.0:`. `CouponPublicTests.test_a_coupon_not_public_at_the_lead_1_instant_is_not_a_member` then failed with
   `AssertionError: 'coupon_settlement' unexpectedly found in {...}`; restored, it passes.

3. In `select_scale` (a label with fewer than `MIN_CELLS` realised cells keeps k = 1, so the variant is the candidate until it has history), the line

       if len(window_cells) < minimum:

   was changed to `if len(window_cells) < 1:`. `SelectScaleTests.test_too_few_cells_keep_the_candidate` then failed with `AssertionError: 0.5 != 1.0`; restored,
   it passes.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("h6_step2_724", ROOT / "scripts" / "h6_step2_724.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["h6_step2_724"] = script
_spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def grid(spread: float, centre: float = 0.0):
    """23 quantiles, `centre` at the median, `spread` bp per grid step either side (monotone)."""

    mid = sp.GRID.index(0.5)
    return [centre + spread * (i - mid) for i in range(len(sp.GRID))]


class RescaleTests(unittest.TestCase):
    def test_one_is_the_candidate(self):
        raw = grid(1.0, 2.0)
        self.assertEqual(script.rescale(raw, 1.0), raw)

    def test_the_median_is_fixed_and_distances_scale(self):
        raw = grid(1.0, 2.0)
        out = script.rescale(raw, 2.0)
        mid = sp.GRID.index(0.5)
        self.assertEqual(out[mid], raw[mid])
        for a, b in zip(raw, out):
            self.assertAlmostEqual(b - raw[mid], 2.0 * (a - raw[mid]))

    def test_order_is_kept(self):
        out = script.rescale(grid(0.7, -1.0), 0.5)
        self.assertEqual(out, sorted(out))

    def test_a_non_positive_scale_is_refused(self):
        with self.assertRaises(ValueError):
            script.rescale(grid(1.0), 0.0)


class SelectScaleTests(unittest.TestCase):
    K = (0.5, 1.0, 2.0)

    def cells(self, n, best):
        """n realised cells (target rows 0..n-1) whose loss is lowest at the grid value `best`."""

        return [(row, tuple(0.0 if k == best else 1.0 for k in self.K)) for row in range(n)]

    def test_the_lowest_mean_loss_wins(self):
        self.assertEqual(script.select_scale(self.cells(80, 2.0), self.K, window=150, minimum=60), 2.0)

    def test_too_few_cells_keep_the_candidate(self):
        self.assertEqual(script.select_scale(self.cells(59, 0.5), self.K, window=150, minimum=60), 1.0)

    def test_a_tie_goes_to_the_value_nearest_one_then_the_smaller(self):
        flat = [(row, (1.0, 1.0, 1.0)) for row in range(70)]
        self.assertEqual(script.select_scale(flat, self.K, window=150, minimum=60), 1.0)
        tie = [(row, (1.0, 5.0, 1.0)) for row in range(70)]
        # 0.5 is 0.5 from one in ratio terms (|log|: 0.69) and 2.0 is 0.69 too: the smaller wins
        self.assertEqual(script.select_scale(tie, self.K, window=150, minimum=60), 0.5)

    def test_only_the_most_recent_window_counts(self):
        old = [(row, (0.0, 1.0, 1.0)) for row in range(100)]
        recent = [(100 + row, (1.0, 1.0, 0.0)) for row in range(80)]
        self.assertEqual(script.select_scale(old + recent, self.K, window=80, minimum=60), 2.0)
        self.assertEqual(script.select_scale(old + recent, self.K, window=180, minimum=60), 0.5)


class ScaleLookAheadTests(unittest.TestCase):
    def test_a_cell_realised_after_the_anchor_never_moves_the_scale(self):
        losses = lambda best: tuple(0.0 if k == best else 1.0 for k in (0.5, 1.0, 2.0))
        history = [(row, losses(2.0)) for row in range(80)] + [(80 + i, losses(0.5)) for i in range(200)]
        # the anchor is row 79: only the first 80 cells were public. The 200 later cells all favour 0.5.
        used = script.usable_history(history, anchor_row=79)
        self.assertEqual(len(used), 80)
        self.assertEqual(script.select_scale(used, (0.5, 1.0, 2.0), window=150, minimum=60), 2.0)

    def test_the_guard_refuses_a_cell_after_the_anchor(self):
        with self.assertRaises(LookAheadError):
            script.require_realised([(80, (1.0,))], anchor_row=79)
        script.require_realised([(79, (1.0,))], anchor_row=79)


class CouponPublicTests(unittest.TestCase):
    values = {"treasury_settlement_coupons": 5.0, "treasury_settlement_bills": 0.0, "tax_date": 0.0}

    def test_a_coupon_public_at_the_lead_1_instant_is_a_member(self):
        got = script.evaluation_membership(date(2024, 5, 15), self.values, fomc_meeting=False, post_fomc=False, bill_floor=None, coupon_public=True)
        self.assertIn("coupon_settlement", got)

    def test_a_coupon_not_public_at_the_lead_1_instant_is_not_a_member(self):
        got = script.evaluation_membership(date(2024, 5, 15), self.values, fomc_meeting=False, post_fomc=False, bill_floor=None, coupon_public=False)
        self.assertNotIn("coupon_settlement", got)

    def test_the_other_strata_are_those_of_1131(self):
        values = {"treasury_settlement_coupons": 0.0, "treasury_settlement_bills": 90.0, "tax_date": 0.0}
        got = script.evaluation_membership(date(2024, 5, 14), values, fomc_meeting=True, post_fomc=True, bill_floor=80.0, coupon_public=False)
        self.assertEqual(got, {"bill_settlement_large", "fomc_meeting", "post_fomc_window"})


class LabelTests(unittest.TestCase):
    def test_the_first_in_the_declared_order(self):
        self.assertEqual(script.cell_label({"fomc_meeting", "tax_date", "coupon_settlement"}), "tax_date")
        self.assertEqual(script.cell_label({"post_fomc_window", "fomc_meeting"}), "fomc_meeting")
        self.assertEqual(script.cell_label({"quarter_and_year_end", "quarter_end_turn", "month_end_turn"}), "quarter_and_year_end")

    def test_no_stratum_is_no_label(self):
        self.assertIsNone(script.cell_label(set()))

    def test_the_priority_is_the_declaration_s(self):
        declared = script.declaration_file()["variant"]["cell_label"]
        positions = [declared.index(name) for name in script.LABEL_PRIORITY]
        self.assertEqual(positions, sorted(positions))


class TargetMeanTests(unittest.TestCase):
    def test_the_mean_over_the_five_leads_that_target_a_day(self):
        dates = [date(2024, 1, d) for d in range(1, 12)]
        positions = {day: i for i, day in enumerate(dates)}
        cells = {(dates[5 - h], h): float(h) for h in range(1, 6)}
        out = script.target_means(dates, positions, cells, first=dates[0], last=dates[-1])
        self.assertEqual(out, {dates[5]: 3.0})

    def test_a_missing_lead_drops_the_day(self):
        dates = [date(2024, 1, d) for d in range(1, 12)]
        positions = {day: i for i, day in enumerate(dates)}
        cells = {(dates[5 - h], h): 1.0 for h in range(1, 5)}
        self.assertEqual(script.target_means(dates, positions, cells, first=dates[0], last=dates[-1]), {})

    def test_a_target_after_the_last_day_is_not_scored(self):
        dates = [date(2024, 1, d) for d in range(1, 12)]
        positions = {day: i for i, day in enumerate(dates)}
        cells = {(dates[5 - h], h): 1.0 for h in range(1, 6)}
        self.assertEqual(script.target_means(dates, positions, cells, first=dates[0], last=dates[4]), {})


class ReadingTests(unittest.TestCase):
    def row(self, lo, hi):
        return {"skill": (lo + hi) / 2, "skill_interval": [lo, hi]}

    def test_skill_only_if_both_lower_ends_are_above_zero(self):
        self.assertEqual(script.kill_reading(self.row(0.01, 0.1), self.row(0.02, 0.2)), "skill")
        self.assertEqual(script.kill_reading(self.row(0.01, 0.1), self.row(-0.02, 0.2)), "no skill shown")
        self.assertEqual(script.kill_reading(self.row(-0.05, -0.01), self.row(0.02, 0.2)), "no skill shown")

    def test_an_undefined_row_is_not_a_reading(self):
        self.assertEqual(script.kill_reading({"undefined": "x"}, self.row(0.01, 0.1)), "undefined")

    def test_the_variant_adds_skill_only_above_zero(self):
        self.assertTrue(script.variant_adds(self.row(0.001, 0.02)))
        self.assertFalse(script.variant_adds(self.row(-0.001, 0.02)))
        self.assertFalse(script.variant_adds({"thin": True}))


class DeclarationTests(unittest.TestCase):
    def test_the_constants_are_the_declaration_s(self):
        d = script.declaration_file()
        self.assertEqual(tuple(d["variant"]["k_grid"]), script.K_GRID)
        self.assertEqual(d["variants"]["count"], 1)
        self.assertEqual(d["issue"], 724)
        self.assertIn(str(script.WINDOW), d["variant"]["estimation"])
        self.assertIn(str(script.MIN_CELLS), d["variant"]["estimation"])

    def test_the_study_is_made_at_1800(self):
        with self.assertRaises(ValueError):
            script.require_instant("16:00")
        script.require_instant("18:00")

    def test_a_day_after_the_last_scored_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2026, 1, 2)])


if __name__ == "__main__":
    unittest.main()
