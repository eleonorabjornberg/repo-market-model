"""Announced IORB (directive #38): the dated table and the two features.

`repo_model.announced_iorb` reads the implementation-note table and computes,
for each scored row `T`, the IORB change already announced for `T` and the
business days to the next announced change, from the notes public at `T`'s
decision instant (16:00 on the panel day before `T`).
"""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model.announced_iorb import (
    ANNOUNCED_CHANGE,
    DAYS_TO_CHANGE,
    FEATURES,
    IorbAnnouncement,
    announced_iorb_features,
    check_announcements,
    load_announcements,
    with_announced_iorb,
)
from repo_model.contract import OVERLAY_FEATURES
from repo_model.asof import KIND_SCHEDULED, InformationRule
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements"
TABLE = SNAPSHOT / "iorb_changes.csv"
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
DECISION = time(16, 0)


def weekdays(start: date, end: date):
    """Every weekday from `start` to `end`: a panel calendar for these tests."""

    out, day = [], start
    while day <= end:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


DATES = weekdays(date(2018, 4, 2), date(2026, 10, 2))
ANNOUNCEMENTS = load_announcements(TABLE)


def features_at(dates, announcements, day):
    return announced_iorb_features(dates, announcements, decision_time=DECISION)[dates.index(day)]


class TableTests(unittest.TestCase):
    """The table is read from the tracked pages, and the pages' bytes are pinned."""

    def test_the_tracked_table_rebuilds_from_the_tracked_pages(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_iorb_table.py"), str(SNAPSHOT), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_table_whose_bytes_are_not_the_manifests_is_refused(self):
        with tempfile.TemporaryDirectory() as scratch:
            table = Path(scratch) / TABLE.name
            table.write_bytes(TABLE.read_bytes().replace(b"1.95", b"2.00", 1))
            (Path(scratch) / (TABLE.name + ".manifest.json")).write_bytes(
                (SNAPSHOT / (TABLE.name + ".manifest.json")).read_bytes()
            )
            with self.assertRaises(ValueError):
                load_announcements(table)

    def test_the_changes_cover_2018_04_to_retrieval_and_every_change_is_after_its_note(self):
        changes = [row for row in ANNOUNCEMENTS if row.kind == "change"]
        self.assertEqual(ANNOUNCEMENTS[0].kind, "anchor")
        self.assertLess(ANNOUNCEMENTS[0].effective, date(2018, 4, 3))
        self.assertGreaterEqual(changes[0].effective, date(2018, 4, 3))
        for row in ANNOUNCEMENTS:
            self.assertGreater(row.effective, row.announced_at.date())

    def test_the_sunday_cut_is_dated_from_its_release(self):
        row = next(row for row in ANNOUNCEMENTS if row.effective == date(2020, 3, 16))
        self.assertEqual(row.announced_at, datetime(2020, 3, 15, 17, 0))
        self.assertEqual(row.change_bps, -100)


class CheckAnnouncementsTests(unittest.TestCase):
    """`check_announcements` refuses a table the features cannot be read from.

    Recorded mutation (availability guard): in `check_announcements`,
    `if row.effective <= row.announced_at.date():` mutated to
    `if row.effective < row.announced_at.date():`.
    `test_a_note_effective_on_its_own_announcement_day_is_refused` then failed
    with `AssertionError` ("ValueError not raised").
    """

    def test_a_note_effective_on_its_own_announcement_day_is_refused(self):
        rows = list(ANNOUNCEMENTS)
        index = next(i for i, row in enumerate(rows) if row.effective == date(2020, 3, 4))
        rows[index] = rows[index]._replace(effective=date(2020, 3, 3))
        with self.assertRaises(ValueError):
            check_announcements(rows)

    def test_a_change_that_disagrees_with_the_rates_is_refused(self):
        rows = list(ANNOUNCEMENTS)
        rows[1] = rows[1]._replace(change_bps=rows[1].change_bps + 5)
        with self.assertRaises(ValueError):
            check_announcements(rows)

    def test_out_of_order_rows_are_refused(self):
        rows = list(ANNOUNCEMENTS)
        rows[1], rows[2] = rows[2], rows[1]
        with self.assertRaises(ValueError):
            check_announcements(rows)


class FuturePerturbationTests(unittest.TestCase):
    """Nothing announced after a decision instant moves that decision's features.

    For each scored day, every note announced after its decision instant is
    perturbed -- its rate, its change and its effective date moved, or the note
    dropped -- and the features read at that instant must not change.

    Recorded mutation (leakage guard): in `announced_iorb_features`,
    `if row.announced_at <= instant and row.effective > decided` mutated to
    `if row.effective > decided`, keying on the effective date alone.
    `test_perturbing_every_later_note_leaves_each_decision_unchanged` and
    `test_the_friday_decision_does_not_see_the_sunday_cut` then failed with
    `AssertionError`.
    """

    #: Scored days around each change, and the 2020-03 emergency cuts.
    DAYS = sorted(
        {
            DATES[DATES.index(day) + offset]
            for row in ANNOUNCEMENTS
            if row.kind == "change"
            for day in [min(d for d in DATES if d >= row.effective)]
            for offset in (-2, -1, 0, 1, 2)
            if 0 < DATES.index(day) + offset < len(DATES)
        }
    )

    def test_perturbing_every_later_note_leaves_each_decision_unchanged(self):
        for day in self.DAYS:
            scored = DATES.index(day)
            instant = datetime.combine(DATES[scored - 1], DECISION)
            later = [i for i, row in enumerate(ANNOUNCEMENTS) if row.announced_at > instant]
            if not later:
                continue
            honest = features_at(DATES, ANNOUNCEMENTS, day)
            moved = list(ANNOUNCEMENTS)
            for i in later:
                row = moved[i]
                moved[i] = row._replace(
                    rate_bps=row.rate_bps + 75,
                    change_bps=row.change_bps + 75 if row.kind == "change" else 75,
                    kind="change",
                    # As early as a later note could be effective: the day after
                    # its own announcement, which may be the scored day itself.
                    effective=row.announced_at.date() + timedelta(days=1),
                )
            dropped = [row for row in ANNOUNCEMENTS if row.announced_at <= instant]
            with self.subTest(day=day):
                self.assertEqual(features_at(DATES, moved, day), honest)
                self.assertEqual(features_at(DATES, dropped, day), honest)

    def test_the_friday_decision_does_not_see_the_sunday_cut(self):
        # The forecast for Monday 2020-03-16 is made at 16:00 on Friday
        # 2020-03-13; the -100 bp cut was released at 17:00 EDT on Sunday 15th.
        self.assertEqual(
            features_at(DATES, ANNOUNCEMENTS, date(2020, 3, 16)),
            {ANNOUNCED_CHANGE: 0.0, DAYS_TO_CHANGE: None},
        )
        # By the 2020-03-16 decision it is already in force: nothing is pending.
        self.assertEqual(
            features_at(DATES, ANNOUNCEMENTS, date(2020, 3, 17)),
            {ANNOUNCED_CHANGE: 0.0, DAYS_TO_CHANGE: None},
        )

    def test_a_morning_announcement_is_read_by_that_afternoons_decision(self):
        # 2020-03-03, 10:00 EST, -50 bp effective 2020-03-04.
        self.assertEqual(
            features_at(DATES, ANNOUNCEMENTS, date(2020, 3, 4)),
            {ANNOUNCED_CHANGE: -50.0, DAYS_TO_CHANGE: 0.0},
        )

    def test_a_scheduled_meeting_is_read_by_the_decision_after_its_release(self):
        # 2022-06-15, 14:00 EDT, +75 bp effective 2022-06-16.
        self.assertEqual(
            features_at(DATES, ANNOUNCEMENTS, date(2022, 6, 16)),
            {ANNOUNCED_CHANGE: 75.0, DAYS_TO_CHANGE: 0.0},
        )
        self.assertEqual(
            features_at(DATES, ANNOUNCEMENTS, date(2022, 6, 15)),
            {ANNOUNCED_CHANGE: 0.0, DAYS_TO_CHANGE: None},
        )


class NoAnnouncementTests(unittest.TestCase):
    """On a day with no announcement read, the change is 0 and the days null."""

    def test_every_day_without_an_announced_change_reads_zero_and_null(self):
        features = announced_iorb_features(DATES, ANNOUNCEMENTS, decision_time=DECISION)
        changed = 0
        for scored in range(1, len(DATES)):
            instant = datetime.combine(DATES[scored - 1], DECISION)
            pending = [
                row
                for row in ANNOUNCEMENTS
                if row.kind == "change"
                and row.announced_at <= instant
                and row.effective > DATES[scored - 1]
            ]
            with self.subTest(day=DATES[scored]):
                if pending:
                    changed += 1
                    self.assertIsNotNone(features[scored][DAYS_TO_CHANGE])
                else:
                    self.assertEqual(
                        features[scored], {ANNOUNCED_CHANGE: 0.0, DAYS_TO_CHANGE: None}
                    )
        self.assertGreater(changed, 0)
        self.assertEqual(features[0], {ANNOUNCED_CHANGE: None, DAYS_TO_CHANGE: None})

    def test_the_unchanged_rate_note_is_no_change(self):
        # 2021-07-28: IORB replaced IOER at an unchanged 0.15 percent.
        self.assertEqual(
            features_at(DATES, ANNOUNCEMENTS, date(2021, 7, 29)),
            {ANNOUNCED_CHANGE: 0.0, DAYS_TO_CHANGE: None},
        )

    def test_days_count_panel_rows_then_weekdays_past_the_panel(self):
        note = IorbAnnouncement(datetime(2020, 1, 6, 9, 0), date(2020, 1, 14), 160, 5, "change")
        anchor = IorbAnnouncement(datetime(2019, 12, 1, 14, 0), date(2019, 12, 2), 155, 0, "anchor")
        panel = weekdays(date(2020, 1, 6), date(2020, 1, 9))  # ends Thursday 9th
        features = announced_iorb_features(panel, [anchor, note], decision_time=DECISION)
        # Forecast for Tue 7th: 8th, 9th in the panel, then 10th, 13th, 14th.
        self.assertEqual(features[1], {ANNOUNCED_CHANGE: 0.0, DAYS_TO_CHANGE: 5.0})


class InformationRuleTests(unittest.TestCase):
    """The as-of rule reads both features as scheduled, at the scored row."""

    def setUp(self):
        self.dates = weekdays(date(2022, 6, 1), date(2022, 6, 30))

    def test_both_features_are_scheduled_and_pass_the_guards_at_16_00(self):
        rule = InformationRule(REGISTRY, ("spread_bps",) + FEATURES, decision_time=DECISION)
        scored = self.dates.index(date(2022, 6, 16))
        info = rule.information_set(self.dates, scored)
        reads = {read.feature: read for read in info.reads}
        for name in FEATURES:
            self.assertEqual(reads[name].kind, KIND_SCHEDULED)
            self.assertEqual(reads[name].row, scored)
        rule.check(self.dates, info)

    def test_an_earlier_decision_time_is_refused_not_read_late(self):
        rule = InformationRule(REGISTRY, ("spread_bps",) + FEATURES, decision_time=time(15, 0))
        scored = self.dates.index(date(2022, 6, 16))
        info = rule.information_set(self.dates, scored)
        with self.assertRaises(LookAheadError):
            rule.check(self.dates, info)

    def test_the_contract_declares_exactly_these_columns_as_overlay(self):
        self.assertEqual(
            {name for name, module in OVERLAY_FEATURES.items() if module == "repo_model.announced_iorb"},
            set(FEATURES),
        )

    def test_the_declaration_is_the_registrys_and_names_both_fields(self):
        block = REGISTRY["fed_iorb_announcements"]["scheduled_availability"]
        self.assertEqual(sorted(block["fields"]), sorted(FEATURES))
        self.assertEqual((block["days"], block["available_time"]), (1, "16:00"))


class WithAnnouncedIorbTests(unittest.TestCase):
    def test_adds_the_two_columns_and_touches_nothing_else(self):
        rows = [
            DailyObservation(day, {"sofr": 1.5, "iorb": 1.55})
            for day in weekdays(date(2020, 3, 2), date(2020, 3, 6))
        ]
        before = copy.deepcopy(rows)
        out = with_announced_iorb(rows, ANNOUNCEMENTS, decision_time=DECISION)
        self.assertEqual(rows, before)
        for original, added in zip(rows, out):
            self.assertEqual(
                {k: v for k, v in added.values.items() if k not in FEATURES}, original.values
            )
        self.assertEqual(out[2].values[ANNOUNCED_CHANGE], -50.0)

    def test_a_panel_that_already_carries_a_column_is_refused(self):
        rows = [DailyObservation(date(2020, 3, 2), {"sofr": 1.5, "iorb": 1.55, ANNOUNCED_CHANGE: 0.0})]
        with self.assertRaises(ValueError):
            with_announced_iorb(rows, ANNOUNCEMENTS, decision_time=DECISION)


if __name__ == "__main__":
    unittest.main()
