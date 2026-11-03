"""The per-release read of the H.4.1 at the 18:00 decision, and its guard (#1350; H5 step 3, avenue #1338).

`repo_model.h41_release.require_release_read` re-derives, from `metadata/h41_release_dating.json` and not from the registry the as-of rule was served,
the print of the Wednesday level that a decision read, and refuses a level printed after the decision instant (`LookAheadError`) and a read that is not the
latest level printed by it (`StaleReadError`). What these tests pin: the hand cases at 18:00 (the Thursday decision reads the Thursday row, the Wednesday
decision the Tuesday row, a moved release is read from its moved date, a week outside the declared coverage is refused); the same decisions at 16:00, which
cannot read a Thursday 16:30 print; and, on the tracked fixtures, that the scarcity-state reads of the per-release run (`own_leg_states` over the
release-dated registry, `h41_release.release_dating()`) pass the guard, while a registry that dates the release a day early (the mutation below, served
through `release_dated_registry`) makes the guard raise.

Recorded mutation (leakage, #1350): in `h41_release.release_dated_registry`, the line `"offset_days": declaration["offset_days"],` was changed to
`"offset_days": 0,` (the Wednesday level dated at the Wednesday's own 16:30, a day before its print).
`PerReleaseReadTests.test_the_state_reads_of_the_per_release_run_pass_the_guard` then raised `LookAheadError` (the 18:00 decision of 2018-05-02 read the
2018-05-02 row, whose level is printed on 2018-05-03; the as-of rule, served the early registry, had admitted it); restored, it passes.
`test_a_registry_that_dates_the_print_early_is_refused` serves the same early registry without touching the source, so it stays a standing test of the guard.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model import h41_release
from repo_model.asof import StaleReadError
from repo_model.decision_instant import DECISION_TIME
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
H41 = ROOT / "metadata" / "h41_release_dating.json"
DECLARATION = h41_release.load_release_dating(H41)
LEGACY = time(16, 0)


def business_days(first: date, n: int):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


#: Monday 2026-06-29 to Friday 2026-07-17: the Wednesdays are 07-01, 07-08 and 07-15, released on the Thursdays 07-02, 07-09 and 07-16 at 16:30.
DATES = business_days(date(2026, 6, 29), 15)


class HandCaseTests(unittest.TestCase):

    def test_the_declared_instant_is_18_00(self):
        self.assertEqual(DECISION_TIME, time(18, 0))

    def test_the_thursday_decision_reads_the_thursday_row(self):
        h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 9), date(2026, 7, 9), DECISION_TIME)

    def test_the_friday_decision_reads_the_friday_row(self):
        h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 10), date(2026, 7, 10), DECISION_TIME)

    def test_the_wednesday_decision_reads_the_tuesday_row(self):
        h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 8), date(2026, 7, 7), DECISION_TIME)

    def test_the_wednesday_row_is_not_public_on_the_wednesday(self):
        with self.assertRaises(LookAheadError):
            h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 8), date(2026, 7, 8), DECISION_TIME)

    def test_the_thursday_decision_may_not_read_the_wednesday_row_the_carried_reading_would(self):
        # The Wednesday row carries the same level as the Thursday row, but the Thursday row is public at 18:00 and is the latest one.
        with self.assertRaises(StaleReadError):
            h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 9), date(2026, 7, 8), DECISION_TIME)

    def test_the_old_instant_cannot_read_a_thursday_16_30_print(self):
        with self.assertRaises(LookAheadError):
            h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 9), date(2026, 7, 9), LEGACY)
        h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 9), date(2026, 7, 7), LEGACY)

    def test_a_read_after_the_decision_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 9), date(2026, 7, 10), DECISION_TIME)

    def test_a_moved_release_is_read_from_its_moved_date(self):
        # The week of Wednesday 2025-06-18 was released on Friday 2025-06-20 (the Thursday was Juneteenth).
        dates = business_days(date(2025, 6, 16), 8)
        h41_release.require_release_read(DECLARATION, dates, date(2025, 6, 20), date(2025, 6, 20), DECISION_TIME)
        with self.assertRaises(LookAheadError):
            h41_release.require_release_read(DECLARATION, dates, date(2025, 6, 19), date(2025, 6, 19), DECISION_TIME)
        h41_release.require_release_read(DECLARATION, dates, date(2025, 6, 19), date(2025, 6, 18) - timedelta(days=1), DECISION_TIME)
        with self.assertRaises(StaleReadError):
            h41_release.require_release_read(DECLARATION, dates, date(2025, 6, 20), date(2025, 6, 19), DECISION_TIME)

    def test_a_week_outside_the_declared_coverage_is_refused(self):
        dates = business_days(date(2026, 9, 7), 5)
        with self.assertRaises(ValueError):
            h41_release.require_release_read(DECLARATION, dates, dates[-1], dates[-1], DECISION_TIME)

    def test_a_date_that_is_not_a_panel_date_is_refused(self):
        with self.assertRaises(ValueError):
            h41_release.require_release_read(DECLARATION, DATES, date(2026, 7, 11), date(2026, 7, 9), DECISION_TIME)


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PerReleaseReadTests(unittest.TestCase):
    """The scarcity-state reads of the per-release run, on the tracked fixtures, held to the declaration."""

    END = date(2018, 7, 31)

    @classmethod
    def setUpClass(cls):
        cls.script = _script("h41_per_release_1350")

    def _reads(self, registry_declaration):
        """The own-leg state reads on the release-dated registry built from `registry_declaration`, with the real build."""

        from repo_model.scarcity import measurement_declaration, own_leg_states

        s = self.script
        with measurement_declaration(), tempfile.TemporaryDirectory() as tmp:
            build, _digest, registry, decision = s.d1145.sv.build_measurement_panel(s.c.SOURCES, Path(tmp))
            dates = [row.date for row in build.observations]
            registry = h41_release.release_dated_registry(registry, registry_declaration)
            with h41_release.release_dating():
                scored = own_leg_states(build.observations, registry=registry, decision_time=decision,
                                        minimum_history=s.d1145.STATE_MINIMUM_HISTORY, horizon=1, end=self.END)
        position = {d: i for i, d in enumerate(dates)}
        return dates, decision, [(dates[position[e.day] - 1], e.read_dates["reserve_balances"]) for e in scored]

    def test_the_state_reads_of_the_per_release_run_pass_the_guard(self):
        dates, decision, reads = self._reads(DECLARATION)
        self.assertTrue(reads)
        for decision_day, read in reads:
            h41_release.require_release_read(DECLARATION, dates, decision_day, read, decision)

    def test_a_registry_that_dates_the_print_early_is_refused(self):
        early = copy.deepcopy(DECLARATION)
        early["offset_days"] = 0  # the registry the mutation `"offset_days": 0` serves
        dates, decision, reads = self._reads(early)
        with self.assertRaises(LookAheadError):
            for decision_day, read in reads:
                h41_release.require_release_read(DECLARATION, dates, decision_day, read, decision)

    def test_the_two_readings_differ_only_on_thursdays_and_fridays(self):
        s = self.script
        carried, c_reads, dates = s.read_states(False, end=self.END)
        per, p_reads, _ = s.read_states(True, end=self.END)
        check = s.state_check(c_reads, p_reads)
        panel_days = set(dates)
        by_per = {r["decision_day"]: r for r in p_reads}
        for r in c_reads:
            day = r["decision_day"]
            if day.weekday() < 3 and s.wednesday_of(r["read"]) != s.wednesday_of(by_per[day]["read"]):
                # Only a Monday after a Wednesday that is not a panel day (4 July 2018): the carried reading counts its five days from a row date.
                self.assertEqual(day.weekday(), 0)
                self.assertNotIn(day - timedelta(days=5), panel_days)
        self.assertGreater(check["by_weekday"]["Thursday"]["level_differs"] + check["by_weekday"]["Friday"]["level_differs"], 0)
        self.assertLessEqual(check["max_age_days"]["per_release"], check["weekly_carry_bound_days"])
        self.assertEqual(sorted(carried), sorted(per))


if __name__ == "__main__":
    unittest.main()
