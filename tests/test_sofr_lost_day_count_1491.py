"""The count of lost SOFR first prints at the confirmation's operational checks (#1491).

Eleonora's ruling on #1491 (6 November 2026, option 1): a lost first print drops that lead alone for every model, as
`docs/decisions/scoring-protocol.md` already says; lost days are counted and reported at the 60, 125 and 250-day
checks; no ceiling is set and nothing that is scored changes. `fp.lost_day_report` is the count; the script's
`report` command prints it.

Not a leakage, availability or staleness guard: it only reads the tracked list, so no mutation is recorded.
"""

from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime, timezone
from pathlib import Path

from repo_model import sofr_first_print as fp

ROOT = Path(__file__).resolve().parents[1]
START = date(2026, 10, 19)
MISSED = {date(2026, 10, 23): "a", date(2026, 10, 28): "b", date(2026, 10, 30): "c", date(2026, 11, 4): "d"}
# 19 October is day 1; 5 November is business day 14; its revision instant passed at 14:30 ET on 6 November.
AFTER_5_NOV = datetime(2026, 11, 6, 20, 0, tzinfo=timezone.utc)


def _script():
    spec = importlib.util.spec_from_file_location("sofr_first_print_script_1491", ROOT / "scripts" / "sofr_first_print.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReportTests(unittest.TestCase):
    def test_a_checkpoint_counts_the_lost_days_in_its_window(self):
        rows = fp.lost_day_report(MISSED, START, AFTER_5_NOV, checkpoints=(5, 10, 13))
        self.assertEqual([r["checkpoint"] for r in rows], [5, 10, 13])
        self.assertEqual([r["lost"] for r in rows], [1, 3, 4])
        self.assertEqual(rows[0]["lost_days"], [date(2026, 10, 23)])

    def test_the_share_is_of_the_window(self):
        rows = fp.lost_day_report(MISSED, START, AFTER_5_NOV, checkpoints=(10,))
        self.assertEqual(rows[0]["window_days"], 10)
        self.assertAlmostEqual(rows[0]["share"], 0.3)

    def test_a_checkpoint_not_yet_reached_is_marked_and_counts_what_is_due(self):
        rows = fp.lost_day_report(MISSED, START, AFTER_5_NOV, checkpoints=(60,))
        self.assertFalse(rows[0]["reached"])
        self.assertEqual(rows[0]["lost"], 4)
        self.assertEqual(rows[0]["window_days"], 14)  # the days due so far, not 60

    def test_the_protocols_checkpoints_are_the_default(self):
        from repo_model import scoring_protocol

        rows = fp.lost_day_report(MISSED, START, AFTER_5_NOV)
        self.assertEqual([r["checkpoint"] for r in rows], list(scoring_protocol.CHECKPOINTS))

    def test_a_lost_day_drops_one_lead_never_the_origin(self):
        rows = fp.lost_day_report(MISSED, START, AFTER_5_NOV, checkpoints=(10,))
        self.assertEqual(rows[0]["rule"], "a lost first print drops that lead alone, for every model")

    def test_the_count_does_not_touch_what_is_scored(self):
        # the report reads the list only; it takes no scores and returns no weights
        rows = fp.lost_day_report(MISSED, START, AFTER_5_NOV, checkpoints=(10,))
        self.assertEqual(
            set(rows[0]),
            {"checkpoint", "reached", "window_days", "lost", "share", "lost_days", "rule"},
        )

    def test_a_start_that_is_not_a_business_day_is_refused(self):
        with self.assertRaises(ValueError):
            fp.lost_day_report(MISSED, date(2026, 10, 24), AFTER_5_NOV)

    def test_the_tracked_list_is_reported(self):
        rows = fp.lost_day_report(fp.read_missed(), START, AFTER_5_NOV, checkpoints=(14,))
        self.assertGreaterEqual(rows[0]["lost"], 4)


class ScriptTests(unittest.TestCase):
    def test_the_report_command_prints_each_checkpoint(self):
        script = _script()
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = script.main(["report", "--now", AFTER_5_NOV.isoformat()])
        self.assertEqual(code, 0, err.getvalue())
        text = out.getvalue()
        for checkpoint in ("60", "125", "250"):
            self.assertIn(f"check at {checkpoint} days", text)
        self.assertIn("lost", text)
        self.assertIn("2026-10-23", text)


if __name__ == "__main__":
    unittest.main()
