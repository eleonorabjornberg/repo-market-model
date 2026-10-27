"""The candidate (s3c): (s3) capped at the SRF line from full allotment onwards (#1255; H5 step 3, her ruling of 26 October 2026).

`repo_model.s3c_candidate` decides, per target day, whether the facility is at full allotment, and caps a forecast's quantiles at the
line (margin 0 bp) only then. "At full allotment" is read from `metadata/policy_events.json`: the `standing_repo` entry in force on the
target day, among the entries announced by the decision instant, carries no aggregate operation limit. No date is written in the module:
an entry that re-imposes a limit stops the cap on its effective day, and an entry that removes it again restarts it. A change announced
after the decision instant is not read.

What these tests pin: the real register (not at full allotment on 10 December 2025, at full allotment from 11 December); both directions
on a synthetic register; the information set (the declaration of 10 December 2025 is announced at 14:00, so a decision at 13:59 on that
day does not know it, and one at 16:00 does; a later re-imposition is not read before its announcement); that a day without full
allotment is (s3) itself, element by element; that a day at full allotment is `min(q, line)`, monotone; that the margin is 0.

Recorded mutation (leakage guard, #1255): in `s3c_candidate.full_allotment`, `known = known_entries(register, as_of)` was mutated to
`known = tuple(register)`, so an entry announced after the decision instant is read when it is effective on or before the target.
`SyntheticRegisterTests.test_a_change_announced_after_the_decision_instant_is_not_read`,
`SyntheticRegisterTests.test_perturbing_every_later_entry_leaves_the_flag_unchanged` and
`CappedQuantilesTests.test_days_before_full_allotment_in_the_real_register_are_s3_itself` then failed with `LookAheadError` (raised by the
`require_announced` check the module runs on the entry it reads). With that check also removed, the first two failed with `AssertionError`
(the flag read the later entry). Restored, all pass.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import policy_events as pe, s3c_candidate as s3c, srf_line  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

REGISTER = pe.load_register()
Q = [float(x) for x in range(-2, 21)]  # 23 ordered values from -2 to 20 bp


def entry(ident, kind, announced, effective, rate, *, hour=14, limit="absent"):
    details = {"rate_percent": rate}
    if limit != "absent":
        details["aggregate_operation_limit_bn"] = limit
    return pe.PolicyEntry(ident, kind, "change", ident, datetime.combine(announced, time(hour, 0)), "stated", effective,
                          "https://example.org", True, details)


def decision(day, hour=16, minute=0):
    return datetime.combine(day, time(hour, minute))


class RealRegisterTests(unittest.TestCase):

    def test_not_at_full_allotment_the_day_before_the_removal_of_the_limit(self):
        self.assertFalse(s3c.full_allotment(REGISTER, decision(date(2025, 12, 10)), date(2025, 12, 10)))
        self.assertIsNone(s3c.cap_line(REGISTER, decision(date(2025, 12, 9)), date(2025, 12, 10)))

    def test_at_full_allotment_from_the_effective_day(self):
        self.assertTrue(s3c.full_allotment(REGISTER, decision(date(2025, 12, 10)), date(2025, 12, 11)))
        self.assertTrue(s3c.full_allotment(REGISTER, decision(date(2026, 3, 2)), date(2026, 3, 3)))

    def test_the_line_at_full_allotment_is_the_facility_line_of_srf_line(self):
        as_of, target = decision(date(2026, 3, 2)), date(2026, 3, 3)
        self.assertEqual(s3c.cap_line(REGISTER, as_of, target), srf_line.srf_line_bps(REGISTER, as_of, target))
        self.assertIsNotNone(s3c.cap_line(REGISTER, as_of, target))

    def test_before_the_facility_there_is_no_cap(self):
        self.assertFalse(s3c.full_allotment(REGISTER, decision(date(2021, 7, 1)), date(2021, 7, 2)))
        self.assertIsNone(s3c.cap_line(REGISTER, decision(date(2021, 7, 1)), date(2021, 7, 2)))

    def test_the_margin_is_zero(self):
        self.assertEqual(s3c.MARGIN_BP, 0.0)


class SyntheticRegisterTests(unittest.TestCase):
    """Facility with a $500bn limit from 2021, full allotment from Mon 2024-03-04, a limit re-imposed from Mon 2024-06-03 and removed
    again from Mon 2024-09-02, with IORB at 0.15 throughout."""

    def setUp(self):
        self.register = pe.known_entries([
            entry("iorb-0", "iorb_rate", date(2021, 6, 16), date(2021, 6, 17), 0.15),
            entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 0.25, limit=500),
            entry("srf-full", "standing_repo", date(2024, 2, 28), date(2024, 3, 4), 0.25, limit=None),
            entry("srf-limit", "standing_repo", date(2024, 5, 29), date(2024, 6, 3), 0.25, limit=300),
            entry("srf-full2", "standing_repo", date(2024, 8, 28), date(2024, 9, 2), 0.30, limit=None),
        ], datetime(2030, 1, 1))

    def test_the_cap_starts_on_the_effective_day_not_the_announcement(self):
        as_of = decision(date(2024, 3, 1))
        self.assertFalse(s3c.full_allotment(self.register, as_of, date(2024, 3, 1)))
        self.assertTrue(s3c.full_allotment(self.register, as_of, date(2024, 3, 4)))

    def test_a_reimposed_limit_stops_the_cap_on_its_effective_date(self):
        as_of = decision(date(2024, 5, 31))
        self.assertTrue(s3c.full_allotment(self.register, as_of, date(2024, 5, 31)))
        self.assertFalse(s3c.full_allotment(self.register, as_of, date(2024, 6, 3)))
        self.assertIsNone(s3c.cap_line(self.register, as_of, date(2024, 6, 3)))
        self.assertEqual(s3c.capped_quantiles(Q, self.register, as_of, date(2024, 6, 3)), Q)

    def test_a_removed_limit_restarts_the_cap_on_its_effective_date(self):
        as_of = decision(date(2024, 8, 30))
        self.assertFalse(s3c.full_allotment(self.register, as_of, date(2024, 8, 30)))
        self.assertTrue(s3c.full_allotment(self.register, as_of, date(2024, 9, 2)))
        self.assertAlmostEqual(s3c.cap_line(self.register, as_of, date(2024, 9, 2)), 15.0, places=9)

    def test_a_change_announced_after_the_decision_instant_is_not_read(self):
        # srf-limit is announced Wed 2024-05-29 at 14:00: known to the decision of 16:00 that day, not to one at 13:59
        target = date(2024, 6, 3)
        self.assertFalse(s3c.full_allotment(self.register, decision(date(2024, 5, 29)), target))
        self.assertTrue(s3c.full_allotment(self.register, decision(date(2024, 5, 29), 13, 59), target))
        self.assertTrue(s3c.full_allotment(self.register, decision(date(2024, 5, 28)), target))

    def test_perturbing_every_later_entry_leaves_the_flag_unchanged(self):
        for day in (date(2024, 2, 27), date(2024, 5, 28), date(2024, 8, 27)):
            as_of = decision(day)
            targets = [day + timedelta(days=k) for k in range(1, 120)]
            honest = [s3c.full_allotment(self.register, as_of, t) for t in targets]
            moved = [e._replace(details={**e.details, "aggregate_operation_limit_bn": 1 if e.details["aggregate_operation_limit_bn"] is None else None},
                                effective=e.announced_at.date() + timedelta(days=1)) if e.announced_at > as_of else e for e in self.register]
            dropped = [e for e in self.register if e.announced_at <= as_of]
            for register in (moved, dropped):
                self.assertEqual([s3c.full_allotment(register, as_of, t) for t in targets], honest, day)

    def test_an_entry_read_after_its_announcement_is_refused_by_the_guard(self):
        late = [e for e in self.register if e.id == "srf-full"][0]
        with self.assertRaises(LookAheadError):
            pe.require_announced(late, decision(date(2024, 2, 27)))

    def test_an_entry_without_the_limit_field_is_refused(self):
        register = pe.known_entries([
            entry("iorb-0", "iorb_rate", date(2021, 6, 16), date(2021, 6, 17), 0.15),
            entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 0.25),
        ], datetime(2030, 1, 1))
        with self.assertRaises(ValueError):
            s3c.full_allotment(register, decision(date(2021, 8, 2)), date(2021, 8, 3))

    def test_a_naive_instant_is_required(self):
        from datetime import timezone
        with self.assertRaises(ValueError):
            s3c.full_allotment(self.register, datetime(2024, 3, 1, 16, tzinfo=timezone.utc), date(2024, 3, 4))


class CappedQuantilesTests(unittest.TestCase):

    def setUp(self):
        self.register = pe.known_entries([
            entry("iorb-0", "iorb_rate", date(2021, 6, 16), date(2021, 6, 17), 0.15),
            entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 0.25, limit=500),
            entry("srf-full", "standing_repo", date(2024, 2, 28), date(2024, 3, 4), 0.25, limit=None),
        ], datetime(2030, 1, 1))

    def test_a_day_without_full_allotment_is_s3_itself(self):
        out = s3c.capped_quantiles(Q, self.register, decision(date(2024, 2, 28)), date(2024, 3, 1))
        self.assertEqual(out, Q)
        self.assertIsNot(out, Q)

    def test_a_day_at_full_allotment_is_min_q_line(self):
        out = s3c.capped_quantiles(Q, self.register, decision(date(2024, 3, 1)), date(2024, 3, 4))
        self.assertEqual(out, [min(q, 10.0) for q in Q])
        self.assertEqual(max(out), 10.0)

    def test_the_levels_stay_ordered(self):
        out = s3c.capped_quantiles(Q, self.register, decision(date(2024, 3, 1)), date(2024, 3, 4))
        self.assertEqual(out, sorted(out))

    def test_days_before_full_allotment_in_the_real_register_are_s3_itself(self):
        day = date(2023, 1, 3)
        while day < date(2025, 12, 11):
            for h in (1, 3, 5):
                target = day + timedelta(days=h)
                if target >= date(2025, 12, 11):
                    continue
                self.assertEqual(s3c.capped_quantiles(Q, REGISTER, decision(day), target), Q, (day, h))
            day += timedelta(days=13)


if __name__ == "__main__":
    unittest.main()
