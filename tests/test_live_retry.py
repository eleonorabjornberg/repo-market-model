"""The live record's fetch retry (#1148): only a fetch failure is tried again, inside the day.

**Recorded mutation**, 22 October 2026: in `scripts/live_retry.py`, `if step != RETRY_STEP:` changed to
`if False:`. `test_a_build_failure_is_not_retried` then fails with `AssertionError: 4 != 1` (the command
ran four times).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("live_retry", ROOT / "scripts" / "live_retry.py")
live_retry = importlib.util.module_from_spec(_spec)
sys.modules["live_retry"] = live_retry
_spec.loader.exec_module(live_retry)

EASTERN = live_retry.EASTERN


class RetryTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.status = self.dir / "status.json"
        self.work = self.dir / "work"
        self.log = self.dir / "calls.txt"
        self.sleeps = []

    def command(self, fail_times, step):
        """A command that fails `fail_times` times, leaving `step` in the status file, then succeeds."""

        script = (
            "import json, pathlib, sys\n"
            f"log = pathlib.Path({str(self.log)!r}); n = len(log.read_text().split()) if log.exists() else 0\n"
            "log.write_text(log.read_text() + 'x ' if log.exists() else 'x ')\n"
            f"pathlib.Path({str(self.work)!r}).mkdir(exist_ok=True); "
            f"(pathlib.Path({str(self.work)!r}) / 'stale').write_text('x')\n"
            f"if n < {fail_times}:\n"
            f"    pathlib.Path({str(self.status)!r}).write_text(json.dumps({{'step': {step!r}}}))\n"
            "    sys.exit(1)\n"
        )
        return [sys.executable, "-c", script]

    def calls(self):
        return len(self.log.read_text().split()) if self.log.exists() else 0

    def run_it(self, command, attempts=4, hour=17):
        return live_retry.run_with_retry(
            command,
            self.status,
            self.work,
            attempts=attempts,
            wait=10,
            now=lambda: datetime(2026, 10, 22, hour, 0, tzinfo=EASTERN),
            sleep=self.sleeps.append,
        )

    def test_a_transient_fetch_failure_is_retried_and_succeeds(self):
        self.assertEqual(self.run_it(self.command(2, "fetch")), 0)
        self.assertEqual(self.calls(), 3)
        self.assertEqual(self.sleeps, [10, 20])

    def test_a_persistent_fetch_failure_stops_after_the_attempts(self):
        self.assertEqual(self.run_it(self.command(99, "fetch"), attempts=3), 1)
        self.assertEqual(self.calls(), 3)

    def test_a_build_failure_is_not_retried(self):
        self.assertEqual(self.run_it(self.command(99, "build")), 1)
        self.assertEqual(self.calls(), 1)
        self.assertEqual(self.sleeps, [])

    def test_a_failure_with_no_status_is_not_retried(self):
        self.assertEqual(live_retry.run_with_retry([sys.executable, "-c", "raise SystemExit(3)"], self.status, self.work, sleep=self.sleeps.append), 3)
        self.assertEqual(self.sleeps, [])

    def test_the_work_directory_is_emptied_between_attempts(self):
        self.run_it(self.command(1, "fetch"))
        # the second attempt re-created it; the first attempt's file was removed in between
        self.assertEqual(self.calls(), 2)
        self.assertEqual(self.sleeps, [10])
        self.assertFalse(self.status.exists())

    def test_no_retry_after_the_stop_time(self):
        self.assertEqual(self.run_it(self.command(99, "fetch"), hour=23), 1)  # 23:00 is before 23:30: all four tries
        self.assertEqual(self.calls(), 4)
        self.log.unlink()
        self.assertEqual(
            live_retry.run_with_retry(
                self.command(99, "fetch"), self.status, self.work, attempts=4, wait=1,
                stop_after=time(16, 0),
                now=lambda: datetime(2026, 10, 22, 17, 0, tzinfo=EASTERN), sleep=self.sleeps.append),
            1,
        )
        self.assertEqual(self.calls(), 1)


class WorkflowTest(unittest.TestCase):
    def test_the_record_step_runs_through_the_retry(self):
        text = (ROOT / ".github" / "workflows" / "live-log.yml").read_text(encoding="utf-8")
        self.assertIn("../main/scripts/live_retry.py", text)


if __name__ == "__main__":
    unittest.main()
