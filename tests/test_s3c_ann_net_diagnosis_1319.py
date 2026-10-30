"""`scripts/s3c_ann_net_diagnosis_1319.py` (#1319; H5 step 3, development tier): a diagnosis of the three losses of (s3c-ann-net) on #1288's page.

Written first, against `metadata/s3c_ann_net_diagnosis_1319.json`. The study reads #1288's walks as they were made and fits nothing, so the one new read
of announced data is the legs of the net (gross, maturing, net of a class at a decision instant); the rest is arithmetic, pinned here on hand cases: the
net-to-gross classes, the thirds by maturing share, the least squares of the gross-and-maturing form against the net-only form, the reading rules, the
share of a loss, the settlement-day bias, and the refusal of a record that is not #1288's.

Recorded mutation (the new availability read, `legs_of_day`): in `legs_of_day`, `known = ns.known_auctions(auctions, instant)` was changed to
`known = list(auctions)` (every auction counted, announced or not). `LegsTests.test_an_auction_announced_after_the_decision_is_not_counted` then
failed with `LookAheadError` (the cross-check against `net_settlement.net_for_day` raised it); restored, it passes. Second mutation (the reading
rule): in `reading`, `high < 0.0` was changed to `high <= 0.0 or True`; `ReadingTests.test_a_loss_is_read_only_when_the_interval_is_above_zero`
then failed with `AssertionError`.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, datetime
from pathlib import Path

from repo_model import net_settlement as ns
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_ann_net_diagnosis_1319", ROOT / "scripts" / "s3c_ann_net_diagnosis_1319.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_ann_net_diagnosis_1319"] = script
_spec.loader.exec_module(script)

SETTLES = date(2025, 3, 14)
BEFORE = datetime(2025, 3, 10, 16, 0)


def auction(is_bill, offering, maturing, announced, cmb=False):
    return ns.Auction(SETTLES, "Bill" if is_bill else "Note", is_bill, offering, maturing, None, announced, None, cmb)


class LegsTests(unittest.TestCase):
    def test_the_legs_of_a_coupon_day_are_gross_maturing_and_net(self):
        # two notes announced, one maturing figure repeated on both records: it is subtracted once, as net_for_day does
        a = [auction(False, 30.0, 50.0, datetime(2025, 3, 5, 12)), auction(False, 40.0, 50.0, datetime(2025, 3, 5, 12))]
        legs = script.legs_of_day(a, BEFORE)
        self.assertEqual((legs["coupon"].gross, legs["coupon"].maturing, legs["coupon"].net), (70.0, 50.0, 20.0))
        self.assertTrue(legs["coupon"].settles and legs["coupon"].full)
        self.assertFalse(legs["bill"].settles)

    def test_a_negative_net_keeps_its_sign(self):
        legs = script.legs_of_day([auction(True, 60.0, 90.0, datetime(2025, 3, 6, 12))], BEFORE)
        self.assertEqual((legs["bill"].gross, legs["bill"].net), (60.0, -30.0))

    def test_a_class_announced_in_part_is_left_out_and_marked(self):
        a = [auction(False, 30.0, 50.0, datetime(2025, 3, 5, 12)), auction(False, 40.0, 50.0, datetime(2025, 3, 11, 12))]
        legs = script.legs_of_day(a, BEFORE)
        self.assertTrue(legs["coupon"].settles)
        self.assertFalse(legs["coupon"].full)
        self.assertEqual((legs["coupon"].gross, legs["coupon"].net), (0.0, 0.0))

    def test_an_auction_announced_after_the_decision_is_not_counted(self):
        """The leakage test of the one new read: a bill announced after the decision instant does not enter the legs."""
        late = auction(True, 80.0, 10.0, datetime(2025, 3, 11, 12), cmb=True)
        known = auction(True, 20.0, 5.0, datetime(2025, 3, 6, 12))
        legs = script.legs_of_day([known, late], BEFORE)
        self.assertEqual((legs["bill"].gross, legs["bill"].net), (20.0, 15.0))
        self.assertTrue(legs["bill"].full)  # a cash management bill is on no schedule before its own announcement (#738)

    def test_a_reading_that_counts_a_later_announcement_raises(self):
        with self.assertRaises(LookAheadError):
            script.require_known_net(script.legs_of_day([auction(True, 20.0, 5.0, datetime(2025, 3, 6, 12))], BEFORE),
                                     [auction(True, 20.0, 5.0, datetime(2025, 3, 6, 12)), auction(True, 80.0, 0.0, datetime(2025, 3, 11, 12))],
                                     BEFORE)


class ClassTests(unittest.TestCase):
    def leg(self, gross, maturing, full=True, settles=True):
        return script.Leg(settles, full, gross if full else 0.0, maturing if full else 0.0, (gross - maturing) if full else 0.0)

    def classes(self, coupon, bill):
        return script.net_class({"coupon": coupon, "bill": bill})

    def test_no_settlement(self):
        self.assertEqual(self.classes(self.leg(0, 0, settles=False), self.leg(0, 0, settles=False)), "no settlement")

    def test_net_at_or_below_zero_on_a_settling_leg(self):
        self.assertEqual(self.classes(self.leg(50, 50), self.leg(0, 0, settles=False)), "net at or below zero")
        self.assertEqual(self.classes(self.leg(80, 30), self.leg(20, 40)), "net at or below zero")

    def test_below_half_at_or_above_half_and_mixed(self):
        off = self.leg(0, 0, settles=False)
        self.assertEqual(self.classes(self.leg(80, 60), off), "net below half of gross")
        self.assertEqual(self.classes(self.leg(80, 40), off), "net at or above half of gross")  # net 40 is exactly half
        self.assertEqual(self.classes(self.leg(80, 60), self.leg(20, 0)), "mixed legs")

    def test_a_class_partly_announced_is_its_own_class(self):
        self.assertEqual(self.classes(self.leg(80, 0, full=False), self.leg(20, 0)), "a class partly announced")

    def test_the_maturing_share_and_its_thirds(self):
        legs = {"coupon": self.leg(80, 20), "bill": self.leg(20, 30)}
        self.assertAlmostEqual(script.maturing_share(legs), 50.0 / 100.0)
        self.assertIsNone(script.maturing_share({"coupon": self.leg(0, 0, settles=False), "bill": self.leg(0, 0, settles=False)}))
        cuts = script.thirds_cuts([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        self.assertEqual([script.third(x, cuts) for x in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)], [0, 0, 1, 1, 2, 2])


class RegressionTests(unittest.TestCase):
    def rows(self, g_coef, m_coef):
        out = []
        for i in range(60):
            gross, maturing = 0.2 + (i % 7) * 0.1, 0.1 + (i % 5) * 0.15
            out.append({"r": 0.5 + g_coef * gross + m_coef * maturing + 0.3 * (i % 2), "gross": gross, "maturing": maturing, "other": i % 2})
        return out

    def test_ols_recovers_exact_coefficients(self):
        x = [[1.0, a, b] for a in (0.0, 1.0, 2.0) for b in (0.0, 1.0, 3.0)]
        y = [2.0 + 3.0 * r[1] - 1.0 * r[2] for r in x]
        for found, want in zip(script.ols(x, y), (2.0, 3.0, -1.0)):
            self.assertAlmostEqual(found, want, places=6)

    def test_the_net_alone_when_maturing_offsets_the_gross_one_for_one(self):
        fit = script.fit_leg(self.rows(2.0, -2.0))
        self.assertAlmostEqual(fit["g"], 2.0, places=6)
        self.assertAlmostEqual(fit["m"], -2.0, places=6)
        self.assertAlmostEqual(fit["g_plus_m"], 0.0, places=6)
        self.assertAlmostEqual(fit["mse_net"], fit["mse_full"], places=9)
        self.assertLess(fit["mse_net"], fit["mse_gross"])

    def test_the_gross_alone_when_maturing_does_not_matter(self):
        fit = script.fit_leg(self.rows(2.0, 0.0))
        self.assertAlmostEqual(fit["g_plus_m"], 2.0, places=6)
        self.assertAlmostEqual(fit["mse_gross"], fit["mse_full"], places=9)
        self.assertGreater(fit["mse_net"], fit["mse_full"])

    def test_a_leg_with_no_variation_in_gross_is_not_fitted(self):
        rows = [{"r": 1.0, "gross": 0.5, "maturing": 0.1 * i, "other": 0} for i in range(30)]
        self.assertTrue(script.no_variation(rows))
        self.assertFalse(script.no_variation(self.rows(1.0, 1.0)))


class ReadingTests(unittest.TestCase):
    def test_a_loss_is_read_only_when_the_interval_is_above_zero(self):
        """A difference d is the arm less the reference: above zero is a loss, below a gain, an interval over zero is undecided."""
        self.assertEqual(script.reading([0.1, 0.4]), "loss")
        self.assertEqual(script.reading([-0.4, -0.1]), "gain")
        self.assertEqual(script.reading([-0.1, 0.4]), "undecided")
        self.assertEqual(script.reading(None), "not read")

    def test_h_a_is_read_from_g_plus_m(self):
        up, over, down = [0.2, 0.9], [-0.3, 0.4], [-0.9, -0.2]
        self.assertEqual(script.read_h_a(up, over), "supported")
        self.assertEqual(script.read_h_a(over, [0.1, 0.5]), "not supported")  # net fits better than gross alone, g + m over zero
        self.assertEqual(script.read_h_a(over, over), "undecided")
        self.assertEqual(script.read_h_a(down, over), "not supported")

    def test_the_skill_is_one_less_the_ratio_of_the_means(self):
        self.assertAlmostEqual(script.skill(0.9, 1.0), 0.1)
        self.assertAlmostEqual(script.skill(1.1, 1.0), -0.1)


class ShareTests(unittest.TestCase):
    def test_the_share_of_a_loss_is_the_group_sum_over_the_total(self):
        self.assertAlmostEqual(script.share([1.0, 2.0], [1.0, 2.0, 1.0, 4.0]), 3.0 / 8.0)
        self.assertIsNone(script.share([1.0], [1.0, -1.0]))  # a total of zero has no share

    def test_the_settlement_day_bias_is_the_error_on_settlement_cells_less_that_on_the_others(self):
        cells = [
            {"settle": True, "y": 3.0, "med": 4.0, "shift": 1.0}, {"settle": True, "y": 5.0, "med": 6.0, "shift": 3.0},
            {"settle": False, "y": 1.0, "med": 1.5, "shift": 0.0}, {"settle": False, "y": 2.0, "med": 2.5, "shift": 0.0},
        ]
        out = script.settlement_bias(cells)
        self.assertAlmostEqual(out["bias"], (-1.0) - (-0.5))
        self.assertAlmostEqual(out["shift"], 2.0)
        self.assertAlmostEqual(out["premium"], 4.0 - 1.5)


class RecordTests(unittest.TestCase):
    def test_a_mean_that_is_not_1288s_is_refused(self):
        script.check_means({"a": 1.0}, {"a": 1.0 + 1e-12}, "pooled")
        with self.assertRaises(ValueError):
            script.check_means({"a": 1.0}, {"a": 1.1}, "pooled")

    def test_the_declaration_names_what_the_module_has(self):
        import json

        declared = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(declared["seed"], script.SEED)
        self.assertEqual(declared["issue"], 1319)
        self.assertEqual(declared["amendments"], script.AMENDMENTS)


def hand_cell(d, h, arm, ref, t=None, event=False):
    return {"d": d, "t": t or d, "h": h, "event": event,
            "score": {script.NET: {m: arm for m in script.METRICS}, script.ANN: {m: ref for m in script.METRICS}}}


class RowTests(unittest.TestCase):
    def test_a_row_is_the_arm_less_the_reference_with_its_share_of_the_loss(self):
        cells = [hand_cell(date(2025, 1, 1 + i), 1, 1.2, 1.0) for i in range(3)]
        total = cells + [hand_cell(date(2025, 2, 1), 1, 0.9, 1.0)]
        row = script.diff_row(cells, script.NET, script.ANN, "d", total=total)
        self.assertAlmostEqual(row["grid_crps"]["mean_d"], 0.2)
        self.assertAlmostEqual(row["grid_crps"]["skill"], 1 - 1.2)
        self.assertAlmostEqual(row["share_of_loss"], 0.6 / 0.5)  # the group's 0.6 over the total 0.5: other cells offset it
        self.assertNotIn("_intervals", row)  # three days are too few for an interval

    def test_the_leads_of_a_target_day_are_averaged_at_target_grain(self):
        cells = [hand_cell(date(2025, 1, 1), 1, 1.0, 1.0, t=date(2025, 1, 3)), hand_cell(date(2025, 1, 2), 2, 2.0, 1.0, t=date(2025, 1, 3))]
        row = script.diff_row(cells, script.NET, script.ANN, "t")
        self.assertEqual(row["units"], 1)
        self.assertAlmostEqual(row["grid_crps"]["mean_d"], 0.5)

    def test_the_scarcity_state_labels(self):
        self.assertEqual([script.state_label(x) for x in (0.0, 1.0, 2.0, 3.0, None)], list(script.STATE_LABELS[i] for i in (0, 1, 1, 2, 3)))

    def test_h_b_needs_the_bias_below_2018_19_a_loss_on_the_largest_settlements_and_none_elsewhere(self):
        self.assertEqual(script.read_h_b([-5.0, -1.0], "loss", False), "supported")
        self.assertEqual(script.read_h_b([-5.0, -1.0], "undecided", False), "undecided")
        self.assertEqual(script.read_h_b([-5.0, -1.0], "loss", True), "undecided")
        self.assertEqual(script.read_h_b([0.5, 2.0], "loss", False), "not supported")
        self.assertEqual(script.read_h_b([-5.0, -1.0], "gain", False), "not supported")


class RecordPageTests(unittest.TestCase):
    PAGE = ROOT / "docs" / "research" / "s3c-ann-net-diagnosis-1319-result.md"
    RESULT = ROOT / "docs" / "research" / "s3c-ann-net-diagnosis-1319" / "result.json"

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        for number in (1, 2, 3):
            self.assertIn(f"**Question {number}.", text)
        self.assertEqual(text.count("(default)"), 3)
        self.assertNotIn("GO #", text)

    def test_the_record_is_the_declared_run_on_the_published_panel_and_reproduces_1288(self):
        import json

        r = json.loads(self.RESULT.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(r["subset_from"])
        self.assertEqual(r["seed"], 1319)
        self.assertIn(r["panel_sha256"], json.dumps(manifest))
        for window in ("development", "2026"):
            self.assertIn("checked", r["windows"][window]["reproduction"])

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        import json

        r = json.loads(self.RESULT.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(r))

    def test_no_lockbox_or_late_day_is_in_the_record(self):
        text = self.RESULT.read_text(encoding="utf-8")
        self.assertNotIn("2026-09-04", text)


if __name__ == "__main__":
    unittest.main()
