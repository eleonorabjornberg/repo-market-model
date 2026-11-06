"""A SOFR first print that was not kept is flagged and listed (#1404; H5 prospective-confirmation groundwork).

On Monday 2 November 2026 GitHub started none of `sofr-first-print.yml`'s morning slots on time. A day's first print
that is not kept by its revision instant (14:30 ET on the publication day) is lost and never back-filled, so the
repository has to (a) make a late scheduler less likely to cost a day, (b) say loudly when one is lost, and (c) keep a
tracked list of the lost days for the confirmation's missing-outcome rule (#1393, rule 8).

**Recorded mutation** (2 November 2026), in `repo_model.sofr_first_print.unflagged_misses`: the line

    return [day for day in due if day not in captured and day not in missed]

was changed to `return []` (a business day with no file is never reported). `MissedDayTests.test_the_days_lost_since_
the_workflow_started_are_found` failed with `AssertionError: Lists differ: [] != [datetime.date(2026, 10, 23), ...]`
and `ScriptTests.test_an_unlisted_missed_day_fails_and_names_the_date` failed with `AssertionError: 0 != 3`.
Separately, in `due_days`, the comparison `<= now` (the day is due at its revision instant) was changed to `< now`:
`DueDaysTests.test_a_day_is_due_at_its_revision_instant` failed with `AssertionError: [] != [datetime.date(2026,
10, 26)]`.

The workflow is read as text (no YAML parser), like `tests/test_workflows.py`.
"""

from __future__ import annotations

import importlib.util
import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from repo_model import sofr_first_print as fp

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "sofr-first-print.yml"
ET_EDT = timedelta(hours=-4)

#: The files on `sofr-first-prints` on 2 November 2026, before this change.
CAPTURED_ON_2_NOV = [date(2026, 10, d) for d in (19, 20, 21, 22, 26, 27, 29)]
LOST = [date(2026, 10, 23), date(2026, 10, 28), date(2026, 10, 30)]
NOW = datetime(2026, 11, 2, 22, 0, tzinfo=timezone.utc)


def _script():
    spec = importlib.util.spec_from_file_location("sofr_first_print_script_1404", ROOT / "scripts" / "sofr_first_print.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tree(days):
    tmp = tempfile.TemporaryDirectory()
    (Path(tmp.name) / "sofr").mkdir()
    for day in days:
        (Path(tmp.name) / "sofr" / f"{day.isoformat()}.json").write_text("{}\n", encoding="utf-8")
    return tmp


def _list(directory, days):
    path = Path(directory) / "missed.json"
    path.write_text(
        json.dumps({"description": "test", "days": [{"effective_date": d.isoformat(), "reason": "test"} for d in days]}),
        encoding="utf-8",
    )
    return path


class DueDaysTests(unittest.TestCase):
    def test_a_day_is_due_at_its_revision_instant(self):
        # Monday 26 October is revised, if at all, at 14:30 ET (18:30 UTC) on Tuesday 27 October.
        before = datetime(2026, 10, 27, 18, 29, tzinfo=timezone.utc)
        at = datetime(2026, 10, 27, 18, 30, tzinfo=timezone.utc)
        self.assertEqual(fp.due_days(before, first=date(2026, 10, 26)), [])
        self.assertEqual(fp.due_days(at, first=date(2026, 10, 26)), [date(2026, 10, 26)])

    def test_a_friday_is_due_on_monday_afternoon_not_on_the_weekend(self):
        saturday = datetime(2026, 10, 24, 20, 0, tzinfo=timezone.utc)
        monday = datetime(2026, 10, 26, 19, 0, tzinfo=timezone.utc)
        self.assertNotIn(date(2026, 10, 23), fp.due_days(saturday))
        self.assertIn(date(2026, 10, 23), fp.due_days(monday))

    def test_weekends_and_holidays_are_never_due(self):
        # 12 October 2026 (Columbus Day) is a market holiday; 17 and 18 October are a weekend.
        due = fp.due_days(NOW)
        for day in (date(2026, 10, 24), date(2026, 10, 25), date(2026, 11, 1)):
            self.assertNotIn(day, due)

    def test_an_instant_needs_a_time_zone(self):
        with self.assertRaises(ValueError):
            fp.due_days(datetime(2026, 11, 2, 22, 0))


class MissedDayTests(unittest.TestCase):
    def test_the_days_lost_since_the_workflow_started_are_found(self):
        self.assertEqual(fp.unflagged_misses(CAPTURED_ON_2_NOV, NOW, {}), LOST)

    def test_a_listed_day_is_not_reported_again(self):
        self.assertEqual(fp.unflagged_misses(CAPTURED_ON_2_NOV, NOW, {LOST[0]: "late"}), LOST[1:])

    def test_the_tracked_list_covers_every_day_lost_so_far(self):
        # Days lost after 2 November are added to the tracked list by their own change; the 2 November view reads
        # the part of the list that was due then.
        missed = fp.read_missed()
        self.assertEqual(sorted(missed)[: len(LOST)], LOST)
        due_then = {day: reason for day, reason in missed.items() if day in LOST}
        self.assertEqual(fp.unflagged_misses(CAPTURED_ON_2_NOV, NOW, due_then), [])

    def test_a_day_that_is_not_yet_due_is_not_a_miss(self):
        morning = datetime(2026, 11, 3, 14, 0, tzinfo=timezone.utc)  # 09:00 ET: 2 November is not yet lost
        self.assertEqual(fp.unflagged_misses(CAPTURED_ON_2_NOV, morning, {}), LOST)

    def test_a_listed_day_with_a_file_is_refused(self):
        with self.assertRaisesRegex(ValueError, "has a first print"):
            fp.unflagged_misses(CAPTURED_ON_2_NOV, NOW, {date(2026, 10, 27): "x"})

    def test_a_listed_day_that_is_not_yet_lost_is_refused(self):
        with self.assertRaisesRegex(ValueError, "has not passed"):
            fp.unflagged_misses(CAPTURED_ON_2_NOV, NOW, {date(2026, 11, 2): "x"})

    def test_names_in_a_directory_are_read_as_dates(self):
        with _tree(CAPTURED_ON_2_NOV) as root:
            self.assertEqual(fp.captured_days(Path(root)), set(CAPTURED_ON_2_NOV))
        with tempfile.TemporaryDirectory() as root, self.assertRaisesRegex(ValueError, "no sofr/"):
            fp.captured_days(Path(root))  # a failed checkout is not an empty branch
        with _tree([]) as root:
            (Path(root) / "sofr" / "latest.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                fp.captured_days(Path(root))


class ListFileTests(unittest.TestCase):
    def _read(self, document):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            return fp.read_missed(path)

    def test_the_tracked_list_gives_a_reason_for_each_day(self):
        for day, reason in fp.read_missed().items():
            with self.subTest(day=day):
                self.assertTrue(reason)

    def test_malformed_lists_are_refused(self):
        entry = {"effective_date": "2026-10-23", "reason": "late"}
        for bad in (
            {"days": []},
            {"description": "d", "days": [{"effective_date": "2026-10-23"}]},
            {"description": "d", "days": [{**entry, "reason": " "}]},
            {"description": "d", "days": [entry, entry]},
            {"description": "d", "days": [{**entry, "effective_date": "2026-10-24"}]},  # a Saturday
            {"description": "d", "days": [{**entry, "effective_date": "2026-10-12"}]},  # a holiday
            {"description": "d", "days": [{**entry, "effective_date": "2026-10-16"}]},  # before the capture began
            {"description": "d", "days": [{**entry, "effective_date": "soon"}]},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self._read(bad)


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.script = _script()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = self.script.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_an_unlisted_missed_day_fails_and_names_the_date(self):
        with _tree(CAPTURED_ON_2_NOV) as root, tempfile.TemporaryDirectory() as aux:
            listed = _list(Path(aux), [LOST[0]])
            target = Path(aux) / "missed.txt"
            code, out, err = self._run(
                "missing", "--dir", root, "--list", str(listed), "--now", NOW.isoformat(), "--days-out", str(target)
            )
            days = target.read_text(encoding="utf-8").split()
        self.assertEqual(code, 3)
        self.assertIn("2026-10-28", err)
        self.assertIn("2026-10-30", err)
        self.assertNotIn("2026-10-23", err)
        self.assertEqual(days, ["2026-10-28", "2026-10-30"])

    def test_an_unreadable_list_is_refused_not_read_as_empty(self):
        with _tree(CAPTURED_ON_2_NOV) as root:
            code, _, _ = self._run(
                "missing", "--dir", root, "--list", str(fp.MISSED_LIST.with_name("nonexistent.json")), "--now", NOW.isoformat()
            )
        self.assertEqual(code, 2)

    def test_with_every_miss_listed_it_passes(self):
        with _tree(CAPTURED_ON_2_NOV) as root, tempfile.TemporaryDirectory() as aux:
            listed = _list(Path(aux), LOST)
            code, out, _ = self._run("missing", "--dir", root, "--list", str(listed), "--now", NOW.isoformat())
        self.assertEqual(code, 0)
        self.assertIn("no unlisted", out)

    def test_a_listed_day_with_a_file_fails_the_check(self):
        with _tree(CAPTURED_ON_2_NOV + [LOST[0]]) as root:
            code, _, err = self._run("missing", "--dir", root, "--list", str(fp.MISSED_LIST), "--now", NOW.isoformat())
        self.assertEqual(code, 2)
        self.assertIn("2026-10-23", err)

    def test_the_refusal_names_the_day(self):
        """The failing capture run says which day is lost (the message of `check_first_print`)."""
        from test_sofr_first_print import _record, _utc  # noqa: PLC0415

        with self.assertRaises(fp.LookAheadError) as caught:
            _record(retrieved=_utc(15, 0))
        self.assertIn("2026-10-16", str(caught.exception))


def _cron_slots():
    """Every UTC (hour, minute) the workflow's `cron:` lines name, expanded from lists, ranges and single values."""

    out = []
    for minute_field, hour_field in re.findall(r'(?m)^\s*- cron: "([^ ]+) ([^ ]+) \* \* 1-5"\s*$', WORKFLOW.read_text(encoding="utf-8")):
        def expand(field):
            values = []
            for part in field.split(","):
                lo, _, hi = part.partition("-")
                values.extend(range(int(lo), int(hi or lo) + 1))
            return values

        out.extend((h, m) for h in expand(hour_field) for m in expand(minute_field))
    return sorted(out)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_slots_cover_the_safe_window_in_both_time_zones(self):
        """08:00-14:30 ET is 12:00-18:30 UTC in EDT and 13:00-19:30 UTC in EST: 13:00-18:30 UTC is safe in both."""
        slots = [h * 60 + m for h, m in _cron_slots()]
        self.assertTrue(slots)
        inside = [s for s in slots if 13 * 60 <= s <= 18 * 60 + 30]
        # a slot at least every 40 minutes across the whole common window, so one late start does not empty it
        gaps = [b - a for a, b in zip(inside, inside[1:])]
        self.assertGreaterEqual(len(inside), 10)
        self.assertLessEqual(max(gaps), 40)
        self.assertLessEqual(inside[0] - 13 * 60, 40)
        self.assertLessEqual(18 * 60 + 30 - inside[-1], 40)

    def test_no_morning_slot_runs_before_the_earliest_publication_or_after_the_latest_revision(self):
        morning = [h * 60 + m for h, m in _cron_slots() if h * 60 + m <= 19 * 60 + 30]
        self.assertGreaterEqual(min(morning), 12 * 60)  # 08:00 EDT

    def test_an_evening_slot_checks_for_a_lost_day(self):
        evening = [s for s in _cron_slots() if s[0] >= 20]
        self.assertTrue(evening)

    def test_the_refusal_and_the_add_only_commit_are_kept(self):
        self.assertIn("sofr_first_print.py capture --out-dir prints", self.text)
        self.assertNotIn("--now", self.text)
        self.assertIn("git diff --name-status \"$base\" HEAD | grep -v '^A'", self.text)
        self.assertIn("git push --quiet origin HEAD:refs/heads/sofr-first-prints", self.text)
        self.assertNotIn("--force", self.text)

    def test_a_missed_day_fails_the_run_and_is_commented_on_225(self):
        self.assertRegex(self.text, r"(?m)^  issues: write$")
        step = self.text[self.text.index("Flag a business day"):]
        self.assertIn("if: always()", step)
        self.assertIn("sofr_first_print.py missing --dir prints --list main/metadata/sofr_missed_first_prints.json", step)
        self.assertIn("issues/225/comments", step)
        self.assertIn("SOFR first print missed:", step)
        self.assertIn("exit $status", step)


if __name__ == "__main__":
    unittest.main()
