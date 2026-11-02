"""`scripts/s3c_flagnet_diagnosis_1344.py` (#1344; H5 step 3, development tier): why (s3c-ann-flagnet) gains on the Brier score of P(> +5 bp) against
(s3c-ann-net) and loses to it in 2020, and the power of the prospective comparison drafted beside it.

Written first, against the declaration. What these tests pin: that the declaration names what the module has (seed, models, the last day, no
amendment, the three hypotheses); the three reading rules on hand cases; the leg and settlement-day labels; the difference rows (the sign, the share
of the difference, a group too small to be given an interval); the realised-event block; the split of the flagnet's fitted shift into the part its
flags carry and the part its nets carry; the power arithmetic (the days needed on a hand case, the window statistics are shift-invariant, the size
check); the refusal of a cell after the declared last day or on a locked day; the refusal to write a record whose means are not #1321's; and the
questions and the draft declaration (numbered options and a default; the draft says it is not registered, names the same candidate and holds the
protocol's multiplicity). When the full run is committed, that the tracked page is what the script renders from the tracked record.

Recorded mutation (the guard of this study, #1344): in `s3c_flagnet_diagnosis_1344.require_cells_inside_limit`, the line
`s686.require_scored_days(days, LAST_DAY)` was changed to `s686.require_scored_days([], LAST_DAY)`.
`LimitTests.test_a_cell_after_the_last_day_is_refused` then failed with `AssertionError` (`LookAheadError not raised`); restored, it passes. (A last day
moved by 400 days is not caught by a test of this guard, because every later day is in the blind tier, which the lockbox refuses by itself.)
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_flagnet_diagnosis_1344", ROOT / "scripts" / "s3c_flagnet_diagnosis_1344.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_flagnet_diagnosis_1344"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

ARM, REF = script.FLAGNET, script.ANNNET


def cell(d, h, arm_score, ref_score, **kw):
    """A cell with the same grid CRPS, twCRPS and Brier for the arm and the reference as given (one number each)."""

    base = {
        "d": d, "t": d + timedelta(days=h), "h": h, "y": 1.0, "regime": "2020", "settle": False, "types": [script.TYPE_LABELS[4]],
        "leg": "neither", "event": False, "immediate": False, "immediate_cmb": False, "state": "0 (abundant)", "month": d.month,
        "score": {ARM: {m: arm_score for m in script.METRICS}, REF: {m: ref_score for m in script.METRICS}},
        "prob": {ARM: 0.1, REF: 0.2},
    }
    base.update(kw)
    return base


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1344)
        self.assertEqual(script.SEED, 1344)
        self.assertIn("seed 1344", declaration["intervals"])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual(sorted(declaration["hypotheses"]), ["H-f", "H-g", "H-h"])
        self.assertIn("sc_s3c_ann_flagnet", declaration["arms"]["arm"])
        self.assertEqual(script.FLAGNET, "sc_s3c_ann_flagnet")
        self.assertEqual(script.ANNNET, "sc_s3c_ann_net")
        self.assertIn("seed 1344", declaration["power"]["method"])

    def test_the_draft_prospective_declaration_is_a_draft_beside_the_same_candidate(self):
        draft = json.loads((ROOT / "metadata" / "s3c_flagnet_prospective_draft_1344.json").read_text(encoding="utf-8"))
        self.assertIn("not registered", draft["status"].lower())
        self.assertEqual(draft["arm"]["name"], script.FLAGNET)
        self.assertEqual(draft["candidate"]["name"], script.ANNNET)
        self.assertEqual(draft["candidate"]["changes"], False)
        self.assertEqual(draft["scoring_protocol"], "docs/decisions/scoring-protocol.md (v1)")
        self.assertEqual(draft["registration"]["by"], "GO #1344, Eleonora's own GitHub comment")
        self.assertEqual(draft["registration"]["registered"], False)
        self.assertIn("multiplicity", draft)
        self.assertIn("power", draft)
        # a draft is not a registration: nothing under the registration directories
        self.assertFalse((ROOT / "metadata" / "registrations").exists() and any((ROOT / "metadata" / "registrations").glob("*flagnet*")))


class ReadingTests(unittest.TestCase):

    def test_reading_of_an_interval_on_d_is_a_loss_above_zero(self):
        self.assertEqual(script.reading([0.1, 0.3]), "loss")
        self.assertEqual(script.reading([-0.3, -0.1]), "gain")
        self.assertEqual(script.reading([-0.1, 0.3]), "undecided")
        self.assertEqual(script.reading(None), "not read")

    def test_h_f(self):
        gain, flat = [-0.004, -0.001], [-0.002, 0.001]
        self.assertEqual(script.read_h_f(gain, flat, gain), "supported")
        self.assertEqual(script.read_h_f(gain, flat, flat), "undecided")
        self.assertEqual(script.read_h_f(flat, gain, gain), "not supported")
        self.assertEqual(script.read_h_f(gain, gain, gain), "undecided")
        self.assertEqual(script.read_h_f(None, flat, gain), "not read")

    def test_h_g(self):
        shift, premium, bias = [1.0, 1.8], [-0.4, 0.9], [-1.5, -0.2]
        self.assertEqual(script.read_h_g(shift, premium, bias, "loss"), "supported")
        self.assertEqual(script.read_h_g(shift, premium, bias, "undecided"), "undecided")
        self.assertEqual(script.read_h_g([0.5, 1.8], premium, bias, "loss"), "not supported")  # the shift's interval reaches the premium's
        self.assertEqual(script.read_h_g(shift, premium, [-1.5, 0.2], "loss"), "not supported")  # the bias interval contains zero
        self.assertEqual(script.read_h_g(shift, None, bias, "loss"), "not read")

    def test_h_h(self):
        self.assertEqual(script.read_h_h("loss", "undecided"), "supported")
        self.assertEqual(script.read_h_h("loss", "gain"), "supported")
        self.assertEqual(script.read_h_h("loss", "loss"), "not supported")
        self.assertEqual(script.read_h_h("undecided", "undecided"), "not read")
        self.assertEqual(script.read_h_h("loss", "not read"), "undecided")


class LabelTests(unittest.TestCase):

    def test_the_leg_of_a_target_day(self):
        self.assertEqual(script.leg_label({"coupon": True, "bill": False, "cmb": False}), "coupon only")
        self.assertEqual(script.leg_label({"coupon": False, "bill": True, "cmb": True}), "bill only")
        self.assertEqual(script.leg_label({"coupon": True, "bill": True, "cmb": False}), "both legs")
        self.assertEqual(script.leg_label({"coupon": False, "bill": False, "cmb": False}), "neither")

    def test_the_settlement_day_types_of_a_target_day(self):
        T = script.TYPE_LABELS
        self.assertEqual(script.type_labels({"coupon": True, "bill": False, "cmb": False}), [T[0]])
        self.assertEqual(script.type_labels({"coupon": False, "bill": True, "cmb": True}), [T[1], T[2]])
        self.assertEqual(script.type_labels({"coupon": True, "bill": True, "cmb": False}), [T[0], T[1], T[3]])
        self.assertEqual(script.type_labels({"coupon": False, "bill": False, "cmb": False}), [T[4]])

    def test_the_state_label(self):
        self.assertEqual(script.state_label(None), "no state")
        self.assertEqual(script.state_label(0.0), "0 (abundant)")
        self.assertEqual(script.state_label(2.0), "1 to 2")
        self.assertEqual(script.state_label(3.0), "3 (scarce)")


class DifferenceRowTests(unittest.TestCase):

    def setUp(self):
        script._PENDING.clear()
        self.day = date(2020, 3, 2)

    def rows(self, n, arm, ref):
        out, d = [], self.day
        for _ in range(n):
            while d.weekday() >= 5:
                d += timedelta(days=1)
            out.append(cell(d, 1, arm, ref))
            d += timedelta(days=1)
        return out

    def test_d_is_arm_less_reference_and_a_gain_is_negative(self):
        row = script.diff_row(self.rows(5, 0.9, 1.0), ARM, REF, "t")
        self.assertAlmostEqual(row["grid_crps"]["mean_d"], -0.1)
        self.assertAlmostEqual(row["grid_crps"]["skill"], 0.1)
        self.assertEqual(row["units"], 5)
        self.assertEqual(script._PENDING, [])  # fewer than 20 units: listed, no interval queued

    def test_a_group_of_twenty_units_is_queued_for_an_interval_and_read(self):
        row = script.diff_row(self.rows(25, 0.9, 1.0), ARM, REF, "t")
        self.assertEqual(len(script._PENDING), 1)
        script.finish(1)
        script.resolve_intervals(row)
        self.assertEqual(row["grid_crps"]["reading"], "gain")
        self.assertLess(row["grid_crps"]["interval"][1], 0.0)

    def test_the_leads_of_a_target_are_averaged_before_the_bootstrap(self):
        a = cell(self.day, 1, 0.5, 1.0)
        b = cell(self.day, 2, 1.5, 1.0)
        b["t"] = a["t"]
        row = script.diff_row([a, b], ARM, REF, "t")
        self.assertEqual(row["units"], 1)
        self.assertAlmostEqual(row["grid_crps"]["mean_d"], 0.0)

    def test_the_share_of_the_difference(self):
        total = self.rows(4, 0.9, 1.0)
        group = total[:1]
        row = script.diff_row(group, ARM, REF, "t", total=total)
        self.assertAlmostEqual(row["share_of_difference"], 0.25)

    def test_a_zero_total_has_no_share(self):
        total = self.rows(3, 1.0, 1.0)
        self.assertIsNone(script.diff_row(total[:1], ARM, REF, "t", total=total)["share_of_difference"])


class EventBlockTests(unittest.TestCase):

    def test_the_block_reports_the_probabilities_the_frequency_and_the_brier_difference_by_set(self):
        d = date(2020, 4, 1)
        hit = cell(d, 1, 0.0, 0.0, event=True, prob={ARM: 0.6, REF: 0.4})
        hit["score"][ARM]["brier_gt5"], hit["score"][REF]["brier_gt5"] = 0.16, 0.36
        miss = cell(d + timedelta(days=1), 1, 0.0, 0.0, event=False, prob={ARM: 0.2, REF: 0.1})
        miss["score"][ARM]["brier_gt5"], miss["score"][REF]["brier_gt5"] = 0.04, 0.01
        block = script.event_block([hit, miss], ARM, REF)
        self.assertEqual(block["event"]["cells"], 1)
        self.assertAlmostEqual(block["event"]["prob_arm"], 0.6)
        self.assertAlmostEqual(block["event"]["prob_ref"], 0.4)
        self.assertAlmostEqual(block["event"]["brier_d_sum"], -0.20)
        self.assertAlmostEqual(block["other"]["brier_d_sum"], 0.03)
        self.assertAlmostEqual(block["frequency"], 0.5)


class ShiftPartsTests(unittest.TestCase):

    def test_the_flag_part_and_the_net_part_add_to_the_fitted_shift(self):
        from repo_model import spread_mr_state_calendar as sc

        estimate = sc.StateEstimate(
            terms=("settlement_coupon", "settlement_bill", sc.NET_COUPON, sc.NET_BILL),
            effect={"settlement_coupon": 0.5, "settlement_bill": 0.25, sc.NET_COUPON: 0.4, sc.NET_BILL: 0.1},
            slope={}, flagged={}, pool=[0.0], pairs=10, unknown_state=0, iterations=1)
        flags = {"settlement_coupon": 1, "settlement_bill": 0}
        extras = {sc.NET_COUPON: 0.3, sc.NET_BILL: -0.2}
        flag_part, net_part = script.shift_parts(estimate, flags, extras, scale=2.0)
        self.assertAlmostEqual(flag_part, 0.5 * 2.0)
        self.assertAlmostEqual(net_part, (0.4 * 0.3 + 0.1 * -0.2) * 2.0)
        self.assertAlmostEqual(flag_part + net_part, sc.standardised_shift(estimate, flags, None, None, extras) * 2.0)


class PowerTests(unittest.TestCase):

    def test_days_needed_on_a_hand_case(self):
        # sigma 1, effect 0.1, one-sided 5%, power 0.8: ((1.6449 + 0.8416) / 0.1) ** 2 = 618.2
        self.assertAlmostEqual(script.days_needed(1.0, 0.1, 0.05), 618.2, delta=0.5)
        self.assertIsNone(script.days_needed(1.0, 0.0, 0.05))
        self.assertIsNone(script.days_needed(1.0, -0.1, 0.05))

    def test_window_statistics_do_not_depend_on_the_shift_and_size_is_the_level(self):
        import random

        rng = random.Random(7)
        series = [rng.gauss(0.0, 1.0) for _ in range(600)]
        stats = script.window_statistics(series, days=60, windows=2000, seed=1344)
        self.assertEqual(len(stats), 2000)
        cv = script.critical_value(stats, 0.05)
        self.assertAlmostEqual(script.power_at(stats, cv, 0.0), 0.05, delta=0.01)
        self.assertGreater(script.power_at(stats, cv, 0.5), script.power_at(stats, cv, 0.2))
        self.assertGreater(script.power_at(stats, cv, 0.2), script.power_at(stats, cv, 0.0))
        again = script.window_statistics(series, days=60, windows=2000, seed=1344)
        self.assertEqual(stats, again)

    def test_a_smaller_level_needs_a_larger_critical_value(self):
        import random

        rng = random.Random(3)
        series = [rng.gauss(0.0, 1.0) for _ in range(600)]
        stats = script.window_statistics(series, days=60, windows=2000, seed=1344)
        self.assertGreater(script.critical_value(stats, 0.01), script.critical_value(stats, 0.05))

    def test_the_series_starts_where_every_confirmation_day_falls(self):
        self.assertEqual(script.POST_COVID_FROM, date(2020, 4, 3))
        cells = [cell(date(2020, 4, 2), 1, 0.9, 1.0), cell(date(2020, 4, 3), 1, 0.8, 1.0), cell(date(2020, 4, 6), 1, 0.7, 1.0)]
        for x in cells:
            x["regime"] = "2020"
        series = script.daily_difference(cells, "grid_crps", first=script.POST_COVID_FROM)
        self.assertEqual(sorted(series), [date(2020, 4, 3), date(2020, 4, 6)])
        self.assertAlmostEqual(series[date(2020, 4, 3)], 0.2)  # positive favours the arm: reference less arm


class LimitTests(unittest.TestCase):

    def test_a_cell_after_the_last_day_is_refused(self):
        late = cell(script.LAST_DAY + timedelta(days=1), 1, 0.9, 1.0)
        with self.assertRaises(LookAheadError):
            script.require_cells_inside_limit([late])

    def test_a_cell_inside_the_limit_is_accepted(self):
        script.require_cells_inside_limit([cell(date(2025, 12, 1), 1, 0.9, 1.0)])

    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_cells_inside_limit([cell(date(2026, 9, 4), 1, 0.9, 1.0)])


class ReproductionTests(unittest.TestCase):

    def test_a_mean_that_is_not_the_records_is_refused(self):
        script.check_means({"a": 1.0}, {"a": 1.0}, "pooled")
        with self.assertRaises(ValueError):
            script.check_means({"a": 1.0 + 1e-6}, {"a": 1.0}, "pooled")


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        self.assertIn("(default)", text)
        self.assertRegex(text, r"\n1\. ")
        self.assertRegex(text, r"\n2\. ")
        self.assertIn("GO #1344", text)


class CommittedRecordTests(unittest.TestCase):

    def setUp(self):
        self.record = ROOT / "docs" / "research" / "s3c-flagnet-diagnosis-1344" / "result.json"
        self.page = ROOT / "docs" / "research" / "s3c-flagnet-diagnosis-1344-result.md"
        if not self.record.exists():
            self.skipTest("the full run is not committed yet")

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        r = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(script.render(r), self.page.read_text(encoding="utf-8"))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        r = json.loads(self.record.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(r["issue"], 1344)
        self.assertIsNone(r["subset_from"])
        self.assertEqual(r["panel_sha256"], manifest["sha256"] if "sha256" in manifest else r["panel_sha256"])
        self.assertEqual(r["seed"], 1344)
        self.assertEqual(r["amendments"], [])
        self.assertEqual(r["decision_time"], "18:00")

    def test_no_cell_is_after_the_last_day(self):
        r = json.loads(self.record.read_text(encoding="utf-8"))
        for window in r["windows"].values():
            self.assertLessEqual(window["notes"]["last_target"], script.LAST_DAY.isoformat())


if __name__ == "__main__":
    unittest.main()
