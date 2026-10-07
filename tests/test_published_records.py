"""No published record scores a day in a locked tier (#268, finding 12).

`lockbox.require_unlocked` guards the scoring entry points. A record that was
scored before a rule, or by a script that forgot the call, would still sit in
`docs/runs/` and feed the results page, so this module walks what was
*published* and refuses a locked scored day in it.

What counts as a scored day: every value under a `scored_date`, `first_scored`
or `last_scored` key in a run record, and the first element of each row under a
`*_per_day` key. In `docs/visual/data/` every ISO date that is not on the small
allowlist below, since those files are the page's own series and a new date
there should be looked at; the allowlisted ones are announcements and the
held-out span the page draws as such, not scored days.

The tiers are read from the tracked declaration at call time, so a tier opened
later stops being locked here without an edit.

**Recorded mutation**, 6 October 2026: in `check_published`, the line
`require_unlocked(days, where=where)` replaced by `pass` (confirmed applied by
grep). `test_a_blind_tier_day_in_a_record_is_refused` then fails with
`AssertionError: LookAheadError not raised`. Restored, all green.
"""

from __future__ import annotations

import copy
import json
import re
import unittest
from datetime import date
from pathlib import Path

from repo_model.lockbox import require_unlocked
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
RUNS = sorted((ROOT / "docs" / "runs").glob("*.json"))
VISUAL = sorted((ROOT / "docs" / "visual" / "data").glob("*.json"))

ISO = re.compile(r"\d{4}-\d{2}-\d{2}$")
SCORED_KEYS = {"scored_date", "first_scored", "last_scored"}
#: Dates on the page that are not scored days: the held-out span it draws as
#: held out, and the announcement a note reports.
VISUAL_ALLOWED = ("/data/held_out[]/", "/data/note/")


def scored_days(node, path=""):
    """The (path, day) pairs of a run record that are scored days."""

    if isinstance(node, dict):
        for key, value in node.items():
            if key in SCORED_KEYS and isinstance(value, str) and ISO.match(value):
                yield f"{path}/{key}", date.fromisoformat(value)
            elif key.endswith("_per_day") and isinstance(value, list):
                for row in value:
                    if isinstance(row, list) and row and isinstance(row[0], str) and ISO.match(row[0]):
                        yield f"{path}/{key}[]", date.fromisoformat(row[0])
            else:
                yield from scored_days(value, f"{path}/{key}")
    elif isinstance(node, list):
        for item in node:
            yield from scored_days(item, f"{path}[]")


def visual_days(node, path=""):
    """Every ISO date in a visual data file, but the allowlisted paths."""

    if isinstance(node, dict):
        for key, value in node.items():
            yield from visual_days(value, f"{path}/{key}")
    elif isinstance(node, list):
        for item in node:
            yield from visual_days(item, f"{path}[]")
    elif isinstance(node, str) and ISO.match(node):
        if not path.startswith(VISUAL_ALLOWED):
            yield path, date.fromisoformat(node)


def check_published(days, *, where):
    """Raise `LookAheadError` if any of `days` is in a locked tier."""

    days = list(days)
    require_unlocked(days, where=where)


class PublishedRecordTests(unittest.TestCase):
    def test_there_are_records_to_walk(self):
        self.assertTrue(RUNS)
        self.assertTrue(VISUAL)

    def test_no_run_record_scores_a_locked_day(self):
        for path in RUNS:
            days = [day for _, day in scored_days(json.loads(path.read_text(encoding="utf-8")))]
            check_published(days, where=f"published record {path.name}")

    def test_no_visual_series_holds_a_locked_day(self):
        for path in VISUAL:
            days = [day for _, day in visual_days(json.loads(path.read_text(encoding="utf-8")))]
            check_published(days, where=f"published page data {path.name}")

    def test_the_walk_finds_scored_days_in_the_records(self):
        record = json.loads((ROOT / "docs" / "runs" / "backtest_gbm.json").read_text(encoding="utf-8"))
        self.assertGreater(len(list(scored_days(record))), 1000)
        diagnosis = json.loads((ROOT / "docs" / "runs" / "v1_interior_diagnosis.json").read_text(encoding="utf-8"))
        self.assertGreater(len(list(scored_days(diagnosis))), 1000)

    def test_a_blind_tier_day_in_a_record_is_refused(self):
        record = json.loads((ROOT / "docs" / "runs" / "backtest_gbm.json").read_text(encoding="utf-8"))
        fixture = copy.deepcopy(record)
        fixture["metrics"]["interval_calibration"]["origins"][-1]["scored_date"] = "2026-09-04"
        with self.assertRaises(LookAheadError):
            check_published([day for _, day in scored_days(fixture)], where="fixture")
        check_published([day for _, day in scored_days(record)], where="the real record")

    def test_a_blind_tier_day_in_page_data_is_refused(self):
        data = json.loads((ROOT / "docs" / "visual" / "data" / "history.json").read_text(encoding="utf-8"))
        fixture = copy.deepcopy(data)
        fixture["data"]["views"][0]["x"][-1] = "2026-09-04"
        with self.assertRaises(LookAheadError):
            check_published([day for _, day in visual_days(fixture)], where="fixture")


if __name__ == "__main__":
    unittest.main()
