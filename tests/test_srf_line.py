"""The SRF line and the cap built on it (#1241; H5 step 3).

`repo_model.srf_line` reads the Standing Repo Facility's minimum bid rate less the IORB, in bp, from `metadata/policy_events.json`
(never a hard-coded +10 bp), as it was public at a decision instant, for a target day. A change announced after the decision
instant is not known; a change announced and effective on or before the target day is. The line does not exist before the facility
(2021-07-29). `cap_quantiles` clips a forecast's quantiles at the line plus a margin: monotone, so the levels stay ordered.

The availability declaration (`metadata/srf_cap_1241.json`, `scheduled_availability`) conforms to `asof.validate_scheduled_availability`
and states the instant the module reads: one panel business day before the target, at 16:00.

Recorded mutation (leakage guard, #1241): in `srf_line.srf_line_bps`, `known = known_entries(register, as_of)` mutated to
`known = tuple(register)`, so an entry announced after the decision instant is read when it is effective on or before the target.
`test_a_change_announced_after_the_decision_instant_is_not_read`, `test_the_friday_cut_is_not_read_by_the_friday_decision` and
`test_perturbing_every_later_entry_leaves_the_line_unchanged` then failed with `LookAheadError` (raised by the `require_announced`
check the module runs on each entry it reads) and, with that check also removed, with `AssertionError`.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import asof, policy_events as pe, srf_line  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

REGISTER = pe.load_register()
DECISION = time(16, 0)


def entry(ident, kind, announced, effective, rate, *, hour=14, **details):
    return pe.PolicyEntry(
        ident, kind, "change", ident, datetime.combine(announced, time(hour, 0)), "stated", effective, "https://example.org", True,
        {"rate_percent": rate, **details})


def decision(day):
    return datetime.combine(day, DECISION)


class SyntheticLineTests(unittest.TestCase):
    """A register with a line that moves: SRF 0.25 and IORB 0.15 (10 bp), then SRF 0.45 and IORB 0.15 (30 bp) from a Thursday."""

    FRIDAY, THURSDAY = date(2022, 3, 11), date(2022, 3, 17)

    def setUp(self):
        self.register = pe.known_entries([
            entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 0.25),
            entry("iorb-0", "iorb_rate", date(2021, 6, 16), date(2021, 6, 17), 0.15),
            entry("srf-1", "standing_repo", date(2022, 3, 16), self.THURSDAY, 0.45),
        ], datetime(2030, 1, 1))

    def test_the_line_is_the_minimum_bid_less_iorb_in_bp(self):
        self.assertAlmostEqual(srf_line.srf_line_bps(self.register, decision(date(2022, 1, 5)), date(2022, 1, 6)), 10.0, places=9)

    def test_the_line_does_not_exist_before_the_facility(self):
        self.assertIsNone(srf_line.srf_line_bps(self.register, decision(date(2021, 7, 27)), date(2021, 7, 28)))
        self.assertIsNone(srf_line.srf_line_bps(self.register, decision(date(2021, 7, 28)), date(2021, 7, 28)))

    def test_the_line_starts_on_the_effective_day_not_the_announcement(self):
        self.assertIsNone(srf_line.srf_line_bps(self.register, decision(date(2021, 7, 28)), date(2021, 7, 28)))
        self.assertAlmostEqual(srf_line.srf_line_bps(self.register, decision(date(2021, 7, 28)), date(2021, 7, 29)), 10.0, places=9)

    def test_a_change_announced_after_the_decision_instant_is_not_read(self):
        # srf-1 is announced Wednesday 2022-03-16 at 14:00, effective Thursday; the decision on Wednesday is at 16:00, so it is read
        self.assertAlmostEqual(srf_line.srf_line_bps(self.register, decision(date(2022, 3, 16)), self.THURSDAY), 30.0, places=9)
        # a decision on Tuesday does not know it, for any target
        self.assertAlmostEqual(srf_line.srf_line_bps(self.register, decision(date(2022, 3, 15)), self.THURSDAY), 10.0, places=9)
        # a decision just before the release on the announcement day does not know it either
        early = datetime.combine(date(2022, 3, 16), time(13, 59))
        self.assertAlmostEqual(srf_line.srf_line_bps(self.register, early, self.THURSDAY), 10.0, places=9)

    def test_a_change_known_but_not_yet_effective_does_not_apply_before_its_day(self):
        self.assertAlmostEqual(srf_line.srf_line_bps(self.register, decision(date(2022, 3, 16)), date(2022, 3, 16)), 10.0, places=9)

    def test_the_friday_cut_is_not_read_by_the_friday_decision(self):
        """A change announced after the decision instant, whose effective day is on or before the target (a weekend announcement)."""

        register = pe.known_entries([
            entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 0.25),
            entry("iorb-0", "iorb_rate", date(2021, 6, 16), date(2021, 6, 17), 0.15),
            entry("srf-w", "standing_repo", date(2022, 3, 13), date(2022, 3, 14), 0.05, hour=17),
        ], datetime(2030, 1, 1))
        friday = decision(date(2022, 3, 11))
        self.assertAlmostEqual(srf_line.srf_line_bps(register, friday, date(2022, 3, 14)), 10.0, places=9)
        self.assertAlmostEqual(srf_line.srf_line_bps(register, decision(date(2022, 3, 14)), date(2022, 3, 15)), -10.0, places=9)

    def test_perturbing_every_later_entry_leaves_the_line_unchanged(self):
        for day in (date(2022, 3, 15), date(2022, 3, 16), date(2022, 3, 17)):
            as_of = decision(day)
            honest = [srf_line.srf_line_bps(self.register, as_of, target) for target in (day + timedelta(days=k) for k in range(1, 6))]
            later = [e for e in self.register if e.announced_at > as_of]
            moved = [e._replace(details={**e.details, "rate_percent": e.details["rate_percent"] + 3.0},
                                effective=e.announced_at.date() + timedelta(days=1)) if e in later else e for e in self.register]
            dropped = [e for e in self.register if e.announced_at <= as_of]
            for register in (moved, dropped):
                self.assertEqual(
                    [srf_line.srf_line_bps(register, as_of, target) for target in (day + timedelta(days=k) for k in range(1, 6))],
                    honest, day)

    def test_a_register_with_an_iorb_missing_where_the_facility_exists_is_refused(self):
        register = pe.known_entries([entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 0.25)], datetime(2030, 1, 1))
        with self.assertRaises(ValueError):
            srf_line.srf_line_bps(register, decision(date(2021, 8, 2)), date(2021, 8, 3))

    def test_the_as_of_instant_must_be_a_naive_datetime(self):
        with self.assertRaises(ValueError):
            srf_line.srf_line_bps(self.register, date(2022, 3, 16), self.THURSDAY)


class RealRegisterTests(unittest.TestCase):

    def test_the_line_is_read_from_the_events_and_is_10_bp_where_they_say_so(self):
        srf = [e for e in REGISTER if e.kind == "standing_repo" and e.effective is not None]
        self.assertEqual(len(srf), 19)
        for e in srf:
            as_of = datetime.combine(e.effective, time(23, 59, 59))
            iorb = pe.policy_state(REGISTER, as_of).latest("iorb_rate")
            expected = 100 * (e.details["rate_percent"] - iorb.details["rate_percent"])
            line = srf_line.srf_line_bps(REGISTER, as_of, e.effective)
            self.assertAlmostEqual(line, expected, places=6, msg=e.id)
            # the events' own words: the minimum bid is at the top of the range and IORB 15 bp over its bottom in a 25 bp range
            if (e.details["rate_offset_from_range_top_bps"] == 0 and iorb.details["offset_from_range_bottom_bps"] == 15
                    and round(100 * (iorb.details["range_top_percent"] - iorb.details["range_bottom_percent"]), 6) == 25):
                self.assertAlmostEqual(line, 10.0, places=6, msg=e.id)

    def test_the_line_is_10_bp_on_every_day_of_the_facility_to_the_end_of_2025(self):
        day = date(2021, 7, 29)
        while day <= date(2025, 12, 31):
            if day.weekday() < 5:
                self.assertAlmostEqual(srf_line.srf_line_bps(REGISTER, datetime.combine(day, time(23, 59, 59)), day), 10.0, places=6, msg=day)
            day += timedelta(days=1)

    def test_there_is_no_line_before_the_facility_was_established(self):
        self.assertEqual(srf_line.FACILITY_EFFECTIVE, date(2021, 7, 29))
        self.assertIsNone(srf_line.srf_line_bps(REGISTER, datetime(2021, 7, 28, 16, 0), date(2021, 7, 28)))
        self.assertIsNone(srf_line.srf_line_bps(REGISTER, datetime(2019, 9, 17, 16, 0), date(2019, 9, 18)))

    def test_the_facility_date_is_the_first_standing_repo_entry_of_the_events(self):
        first = min(e.effective for e in REGISTER if e.kind == "standing_repo" and e.effective is not None)
        self.assertEqual(first, srf_line.FACILITY_EFFECTIVE)


class CapTests(unittest.TestCase):
    Q = [-3.0, -1.0, 0.0, 2.0, 6.0, 9.0, 11.0, 12.5, 18.0]

    def test_the_cap_clips_at_the_line_plus_the_margin_and_nothing_below(self):
        self.assertEqual(srf_line.cap_quantiles(self.Q, 10.0, 0.0), [-3.0, -1.0, 0.0, 2.0, 6.0, 9.0, 10.0, 10.0, 10.0])
        self.assertEqual(srf_line.cap_quantiles(self.Q, 10.0, 5.0), [-3.0, -1.0, 0.0, 2.0, 6.0, 9.0, 11.0, 12.5, 15.0])
        self.assertEqual(srf_line.cap_quantiles(self.Q, 10.0, 10.0), [-3.0, -1.0, 0.0, 2.0, 6.0, 9.0, 11.0, 12.5, 18.0])

    def test_the_cap_keeps_the_levels_ordered(self):
        for margin in (0.0, 5.0, 10.0):
            out = srf_line.cap_quantiles(self.Q, 10.0, margin)
            self.assertEqual(out, sorted(out))
            self.assertEqual(len(out), len(self.Q))

    def test_no_line_leaves_the_forecast_unchanged(self):
        self.assertEqual(srf_line.cap_quantiles(self.Q, None, 0.0), self.Q)

    def test_a_negative_margin_is_refused(self):
        with self.assertRaises(ValueError):
            srf_line.cap_quantiles(self.Q, 10.0, -1.0)

    def test_the_input_is_not_modified(self):
        q = list(self.Q)
        srf_line.cap_quantiles(q, 10.0, 0.0)
        self.assertEqual(q, self.Q)


class AvailabilityDeclarationTests(unittest.TestCase):
    DECLARATION = ROOT / "metadata" / "srf_cap_1241.json"

    def test_the_declared_block_conforms_and_states_the_decision_instant_the_module_reads(self):
        declared = json.loads(self.DECLARATION.read_text(encoding="utf-8"))
        block = declared["availability"]["scheduled_availability"]
        self.assertEqual(asof.validate_scheduled_availability("srf_line", block), [])
        self.assertEqual((block["days"], block["available_time"], block["unit"]), (1, srf_line.DECISION_TIME.strftime("%H:%M"), "business_days"))
        self.assertEqual(block["fields"], ["srf_line_bps"])
        self.assertEqual(block["timezone"], "America/New_York")


if __name__ == "__main__":
    unittest.main()
