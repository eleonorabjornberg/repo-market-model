"""gbm_funding fit on SOFR's distance from the ON RRP rate (`scripts/onrrp_distance_948.py`, #948): the parts that decide what is read.

Recorded mutations (the leakage guards this script adds; the scorer's own lockbox guard is tested with the scorer):

* `rate_in_force`, the pool `known_entries(register, as_of)` changed to `register` (every entry, announced or not): the entry chosen
  for a target day can be one announced after the decision instant, and `policy_events.require_announced` on it raises, so
  `AnnouncementTests.test_a_change_announced_after_the_decision_is_not_seen` fails with `LookAheadError`.
* `require_study_window`, the line `if late:` changed to `if False:`:
  `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with `AssertionError` (`LookAheadError not raised`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("onrrp_distance_948_script", REPO / "scripts" / "onrrp_distance_948.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import policy_events  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

REGISTER = policy_events.load_register()


def end_of(day: date) -> datetime:
    return script.end_of_day(day)


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 30), date(2025, 12, 31)])


class WidthTests(unittest.TestCase):
    """The IORB - ON RRP width, in bp, from the register alone, on the days the directive lists."""

    def test_the_steps_of_the_width_are_those_of_the_register(self):
        steps = [
            (date(2018, 3, 22), 25.0), (date(2018, 6, 13), 25.0), (date(2018, 6, 14), 20.0), (date(2018, 12, 19), 20.0),
            (date(2018, 12, 20), 15.0), (date(2019, 5, 1), 15.0), (date(2019, 5, 2), 10.0), (date(2020, 3, 16), 10.0),
            (date(2022, 6, 16), 10.0), (date(2024, 12, 18), 10.0), (date(2024, 12, 19), 15.0), (date(2025, 12, 31), 15.0),
        ]
        for day, expected in steps:
            self.assertEqual(script.width_bp(REGISTER, day, end_of(day)), expected, day)

    def test_the_width_is_the_rate_difference_in_bp_not_the_rate(self):
        # 2022-06-16: IORB 1.65, ON RRP 1.55; 2018-06-14: IORB 1.95, ON RRP 1.75
        self.assertAlmostEqual(script.width_bp(REGISTER, date(2022, 6, 16), end_of(date(2022, 6, 16))), 10.0, places=9)
        self.assertAlmostEqual(script.width_bp(REGISTER, date(2018, 6, 14), end_of(date(2018, 6, 14))), 20.0, places=9)

    def test_a_rate_unchanged_by_a_meeting_is_carried(self):
        # ON RRP has no entry for 2019-05-01 (the IOER technical adjustment): the 2018-12-19 rate stays in force
        self.assertEqual(script.rate_percent(REGISTER, "on_rrp", date(2019, 5, 2), end_of(date(2019, 5, 2))), 2.25)
        self.assertEqual(script.rate_percent(REGISTER, "iorb_rate", date(2019, 5, 2), end_of(date(2019, 5, 2))), 2.35)

    def test_a_target_day_before_the_register_starts_is_refused(self):
        with self.assertRaises(ValueError):
            script.width_bp(REGISTER, date(2018, 3, 1), end_of(date(2018, 3, 1)))


class AnnouncementTests(unittest.TestCase):
    """A rate is read from its announcement instant, never from its effective date and never before it."""

    def test_a_change_announced_after_the_decision_is_not_seen(self):
        # announced 2018-06-13 14:00, effective 2018-06-14: a decision at 13:59 still sees 25 bp, one at 14:00 sees 20 bp
        target = date(2018, 6, 14)
        self.assertEqual(script.width_bp(REGISTER, target, datetime(2018, 6, 13, 13, 59)), 25.0)
        self.assertEqual(script.width_bp(REGISTER, target, datetime(2018, 6, 13, 14, 0)), 20.0)
        # announced 2024-12-18 14:00, effective 2024-12-19
        target = date(2024, 12, 19)
        self.assertEqual(script.width_bp(REGISTER, target, datetime(2024, 12, 18, 13, 0)), 10.0)
        self.assertEqual(script.width_bp(REGISTER, target, datetime(2024, 12, 18, 16, 0)), 15.0)

    def test_an_announcement_with_no_stated_time_is_public_only_at_the_end_of_its_day(self):
        base = json.loads(policy_events.REGISTER_PATH.read_text(encoding="utf-8"))
        late = {
            "id": "iorb-test", "kind": "iorb_rate", "action": "set_rate", "title": "t", "announced_date": "2024-12-18",
            "announced_time": None, "time_basis": "not_stated", "effective_date": "2024-12-19", "effective_precision": "day",
            "source_url": "https://example.org/x", "read_at_source": True, "details": {"rate_percent": 9.0},
        }
        base["entries"] = [e for e in base["entries"] if e["id"] != "iorb-20241218"] + [late]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "register.json"
            path.write_text(json.dumps(base), encoding="utf-8")
            register = policy_events.load_register(path)
        target = date(2024, 12, 19)
        # the 16:00 decision of the announcement date never sees an entry that states no time
        before = script.rate_percent(register, "iorb_rate", target, datetime(2024, 12, 18, 16, 0))
        self.assertEqual(before, 4.65)
        self.assertEqual(script.rate_percent(register, "iorb_rate", target, datetime(2024, 12, 18, 23, 59, 59)), 9.0)

    def test_a_malformed_register_entry_is_refused(self):
        base = json.loads(policy_events.REGISTER_PATH.read_text(encoding="utf-8"))
        broken = [dict(e) for e in base["entries"]]
        for entry in broken:
            if entry["id"] == "on_rrp-20241218":
                entry["details"] = {"limit": 1}
        base["entries"] = broken
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "register.json"
            path.write_text(json.dumps(base), encoding="utf-8")
            register = policy_events.load_register(path)
        with self.assertRaises(ValueError):
            script.width_bp(register, date(2024, 12, 19), end_of(date(2024, 12, 19)))


class FrameTests(unittest.TestCase):
    def frame(self):
        days = [date(2018, 6, 12), date(2018, 6, 13), date(2018, 6, 14), date(2018, 6, 15)]
        return [DailyObservation(day, {"sofr": 1.80 + 0.01 * i, "iorb": 1.75 if i < 2 else 1.95, "tga": 100.0 + i}) for i, day in enumerate(days)]

    def test_the_target_is_sofr_less_the_on_rrp_rate_in_bp(self):
        frame = script.distance_frame(self.frame(), REGISTER)
        # ON RRP: 1.50 until 2018-06-13, 1.75 from 2018-06-14
        expected = [100 * (1.80 - 1.50), 100 * (1.81 - 1.50), 100 * (1.82 - 1.75), 100 * (1.83 - 1.75)]
        for row, value in zip(frame, expected):
            self.assertAlmostEqual(row.spread_bps, value, places=9)

    def test_the_distance_is_the_spread_plus_the_width_and_nothing_else_moves(self):
        original, shifted = self.frame(), script.distance_frame(self.frame(), REGISTER)
        for before, after, width in zip(original, shifted, (25.0, 25.0, 20.0, 20.0)):
            self.assertAlmostEqual(after.spread_bps - before.spread_bps, width, places=9)
            self.assertEqual(after.date, before.date)
            self.assertEqual(dict(after.values), dict(before.values))

    def test_the_rate_is_a_target_and_never_a_regressor(self):
        frame = script.distance_frame(self.frame(), REGISTER)
        for row in frame:
            self.assertNotIn("on_rrp", row.values)
            self.assertNotIn("RRPONTSYAWARD", row.values)

    def test_the_settlement_field_is_aligned_only_where_it_is_an_input(self):
        frame = self.frame()
        for position, row in enumerate(frame):
            frame[position] = DailyObservation(row.date, {**row.values, "treasury_settlement": float(position)})
        aligned = script.training_frame(frame, REGISTER, align=True)
        self.assertEqual([r.values["treasury_settlement"] for r in aligned], [1.0, 2.0, 3.0, None])
        plain = script.training_frame(frame, REGISTER, align=False)
        self.assertEqual([r.values["treasury_settlement"] for r in plain], [0.0, 1.0, 2.0, 3.0])
        self.assertAlmostEqual(aligned[2].spread_bps, plain[2].spread_bps, places=9)

    def test_alignment_is_declared_for_the_leads_that_read_the_field(self):
        self.assertTrue(script.aligns(("a", "treasury_settlement", "spread_bps")))
        self.assertFalse(script.aligns(("a", "b", "spread_bps")))


class ServedRowTests(unittest.TestCase):
    """The fit takes the last observed spread as an input, so the row it is served is re-expressed like the training rows."""

    class Recorder:
        levels = (0.5,)

        def __init__(self):
            self.rows = []

        def predict(self, row):
            self.rows.append(row)
            return (row.spread_bps,)

        def with_history(self, history):
            self.history = list(history)
            return self

    def test_the_served_feature_row_carries_the_distance_not_the_spread(self):
        recorder = self.Recorder()
        model = script.DistanceModel(recorder, REGISTER)
        row = DailyObservation(date(2018, 6, 14), {"sofr": 1.90, "iorb": 1.95})
        # IORB - ON RRP is 20 bp that day: SOFR - IORB = -5 bp, SOFR - ON RRP = +15 bp
        self.assertAlmostEqual(model.predict(row)[0], 15.0, places=9)
        self.assertAlmostEqual(row.spread_bps, -5.0, places=9)

    def test_history_handed_to_the_model_is_re_expressed_too(self):
        recorder = self.Recorder()
        model = script.DistanceModel(recorder, REGISTER)
        row = DailyObservation(date(2018, 6, 13), {"sofr": 1.80, "iorb": 1.75})
        view = model.with_history([row])
        self.assertIsInstance(view, script.DistanceModel)
        self.assertAlmostEqual(recorder.history[0].spread_bps, 100 * (1.80 - 1.50), places=9)

    def test_the_wrapped_fits_attributes_are_still_read(self):
        self.assertEqual(script.DistanceModel(self.Recorder(), REGISTER).levels, (0.5,))


class MapBackTests(unittest.TestCase):
    def test_the_mapped_back_quantiles_are_the_fitted_ones_shifted_by_the_width(self):
        z = [1.0, 2.5, 4.0, 4.0, 9.25]
        for width in (25.0, 20.0, 15.0, 10.0):
            mapped = script.map_back(z, width)
            self.assertEqual(mapped, [value - width for value in z])
            self.assertEqual(mapped, sorted(mapped))

    def test_a_missing_law_stays_missing(self):
        self.assertIsNone(script.map_back(None, 10.0))


class PanelTests(unittest.TestCase):
    def test_a_panel_iorb_that_disagrees_with_the_register_is_refused(self):
        good = DailyObservation(date(2018, 6, 14), {"sofr": 1.9, "iorb": 1.95})
        script.check_panel_iorb([good], REGISTER)
        bad = DailyObservation(date(2018, 6, 14), {"sofr": 1.9, "iorb": 1.75})
        with self.assertRaises(ValueError):
            script.check_panel_iorb([bad], REGISTER)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_reads_the_register_and_never_the_realised_award_rate(self):
        document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(document["issue"], 948)
        self.assertIn("policy_events.json", document["inputs"]["on_rrp_offering_rate"]["source"])
        self.assertIn("never FRED's RRPONTSYAWARD", document["inputs"]["on_rrp_offering_rate"]["source"])
        self.assertIn("availability", document["inputs"]["on_rrp_offering_rate"])
        self.assertEqual(list(document["arms"]), ["gbm_funding_onrrp"])
        self.assertEqual(script.ARM, "gbm_funding_onrrp")
        self.assertEqual(script.EXCLUDED_DAY, date(2019, 9, 18))


if __name__ == "__main__":
    unittest.main()
