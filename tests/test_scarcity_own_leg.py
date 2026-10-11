"""The scarcity state reads each leg at its own latest public row (#586, Eleonora's ruling on #571).

`scarcity.own_leg_states` forms the state from the reserves (WRESBAL), the H.8 total assets and the
day's ON RRP, each read by `InformationRule` on its own declaration, so the daily ON RRP leg is no
older than the Desk's lag and the H.8 lag no longer sets the row the other two are read at. The older
same-row read (`with_reserve_scarcity_state` through the `reserve_scarcity_state` column) is unchanged
and is what `test_scarcity.py` pins.

Written first, and watched failing: before `own_leg_states` existed every test here raised
`AttributeError: module 'repo_model.scarcity' has no attribute 'own_leg_states'`.

**Recorded mutation** (CLAUDE.md), 11 October 2026, in a disposable copy: in
`scarcity._require_public_legs`, `if read.available_at > info.decision_instant` mutated to
`if read.available_at > info.decision_instant + timedelta(days=30)` (the guard that every leg is public
at the decision instant). `test_a_leg_not_yet_public_is_refused` then failed with
`AssertionError: LookAheadError not raised`. Second mutation, same function: `if read.feature in LEGS:`
mutated to `if False:` (no leg is recorded as read); every test that calls `own_leg_states` then raised
`LookAheadError` ("the scarcity state's legs [...] were not read"), and
`test_a_leg_not_yet_public_is_refused` raised it on the unforced call. Both restored, green.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, time, timedelta
from pathlib import Path

from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

sys.path.insert(0, str(Path(__file__).parent))

import test_scarcity as base  # noqa: E402  (shared rows and the tracked registry)

REGISTRY = base.REGISTRY
DECISION = time(16, 0)
MINIMUM_HISTORY = 20
#: Early enough that the H.8 (declared twelve days late) has printed before the first scored day.
DATES = base.weekdays(date(2025, 7, 7), 80)
WEDNESDAYS = [date(2025, 7, 2) + timedelta(days=7 * week) for week in range(16)]
RESERVES = {week: base.carried(base.RESERVES, max(week, date(2025, 8, 27))) for week in WEDNESDAYS}
BANK_ASSETS = {week: base.carried(base.BANK_ASSETS, max(week, date(2025, 8, 27))) for week in WEDNESDAYS}


def rows_with_onset(drop_on=date(2025, 9, 15), high=500.0, low=29.0):
    """Rows whose ON RRP balance falls below the buffer on `drop_on` (reserves in the band)."""

    return [
        DailyObservation(
            when,
            {
                "sofr": 2.0 + index / 100.0,
                "iorb": 2.0,
                "reserve_balances": base.carried(RESERVES, when),
                "bank_total_assets": base.carried(BANK_ASSETS, when),
                "on_rrp": high if when < drop_on else low,
            },
        )
        for index, when in enumerate(DATES)
    ]


def old_state(rows, when):
    """The same-row read: the `reserve_scarcity_state` column at the row the old read lands on."""

    from repo_model.scarcity import with_reserve_scarcity_state

    shaped = with_reserve_scarcity_state(rows)
    information = InformationRule(
        REGISTRY, ("spread_bps", "reserve_scarcity_state"), decision_time=DECISION
    )
    info = information.information_set(DATES, DATES.index(when))
    return information.observation(shaped, info).values["reserve_scarcity_state"]


class OwnLegTests(unittest.TestCase):
    def setUp(self):
        switch = base.scarcity_inputs_on()
        switch.start()
        self.addCleanup(switch.stop)
        from repo_model import scarcity

        self.scarcity = scarcity

    def days(self, rows=None):
        rows = rows or rows_with_onset()
        scored = self.scarcity.own_leg_states(
            rows, registry=REGISTRY, decision_time=DECISION, minimum_history=MINIMUM_HISTORY
        )
        return rows, {entry.day: entry for entry in scored}

    def test_an_onset_is_read_when_its_own_leg_is_public_not_when_the_h8_lag_allows(self):
        """The 2025-09-15 pattern: the ON RRP leg drops below the buffer, reserves sit in the band."""

        rows, days = self.days()
        differing = [
            day for day, entry in days.items() if old_state(rows, day) != entry.state
        ]
        self.assertTrue(differing, "the own-leg read never differs from the same-row read")
        first = min(differing)
        self.assertEqual(days[first].state, 2)
        self.assertEqual(old_state(rows, first), 1)
        # the leg that moved was read from the Desk's own row, two panel days back at most
        self.assertLessEqual(DATES.index(first) - DATES.index(days[first].read_dates["on_rrp"]), 3)
        self.assertGreater(days[first].read_dates["on_rrp"], days[first].read_dates["bank_total_assets"])

    def test_every_leg_is_read_on_its_own_row(self):
        _rows, days = self.days()
        for entry in days.values():
            self.assertEqual(
                set(entry.read_dates), {"reserve_balances", "bank_total_assets", "on_rrp"}
            )
            for leg, read in entry.read_dates.items():
                self.assertLess(read, entry.day, leg)

    def test_when_every_leg_is_equally_old_the_two_reads_agree(self):
        """No onset: ON RRP constant. The own-leg read adds nothing a same-row read missed."""

        rows = rows_with_onset(drop_on=date(2030, 1, 1))
        _rows, days = self.days(rows)
        for day, entry in days.items():
            if entry.read_dates["bank_total_assets"] == entry.read_dates["reserve_balances"]:
                self.assertEqual(entry.state, old_state(rows, day), day)

    def test_a_leg_not_yet_public_is_refused(self):
        information = InformationRule(
            REGISTRY,
            ("spread_bps",) + self.scarcity.LEGS,
            decision_time=DECISION,
        )
        rows = rows_with_onset()
        scored = DATES.index(date(2025, 9, 29))
        info = information.information_set(DATES, scored)
        information.check(DATES, info)
        self.scarcity._require_public_legs(info)  # as read: fine
        # the H.8 row that carries the week ending 17 September is public only after this decision
        late = DATES.index(date(2025, 9, 19))
        forced = info._replace(
            reads=tuple(
                read._replace(
                    row=late,
                    available_at=information.availability(DATES, read.fields, late),
                )
                if read.feature == "bank_total_assets"
                else read
                for read in info.reads
            )
        )
        with self.assertRaises(LookAheadError):
            self.scarcity._require_public_legs(forced)

    def test_the_composed_feature_reads_the_same_state_as_own_leg_states(self):
        """Under `own_leg_composition` the rule's `reserve_scarcity_state` is the own-leg state."""

        rows, days = self.days()
        with self.scarcity.own_leg_composition():
            information = InformationRule(
                REGISTRY, ("spread_bps", "reserve_scarcity_state"), decision_time=DECISION
            )
            for when, entry in days.items():
                info = information.information_set(DATES, DATES.index(when))
                information.check(DATES, info)
                observed = information.observation(rows, info).values["reserve_scarcity_state"]
                self.assertEqual(observed, entry.state, when)

    def test_the_composition_is_undone_on_the_way_out_even_on_a_raise(self):
        from repo_model import asof, contract

        before = contract.COMPOSED_FEATURES, asof.COMPOSED_FEATURES, dict(asof.COMPOSERS)
        with self.assertRaises(RuntimeError):
            with self.scarcity.own_leg_composition():
                self.assertIn("reserve_scarcity_state", contract.COMPOSED_FEATURES)
                self.assertIn("reserve_scarcity_state", asof.COMPOSERS)
                raise RuntimeError
        after = contract.COMPOSED_FEATURES, asof.COMPOSED_FEATURES, dict(asof.COMPOSERS)
        self.assertEqual(before, after)
        self.assertNotIn("reserve_scarcity_state", contract.COMPOSED_FEATURES)

    def test_a_hole_in_a_leg_is_a_hole_in_the_state(self):
        rows = [
            DailyObservation(row.date, {**row.values, "on_rrp": None}) for row in rows_with_onset()
        ]
        _rows, days = self.days(rows)
        self.assertTrue(all(entry.state is None for entry in days.values()))


if __name__ == "__main__":
    unittest.main()
