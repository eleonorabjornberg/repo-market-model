"""The two month-end readings and the scratch shim that switches between them (#883).

The script lists days and changes no definition; these tests pin the arithmetic it reports.
"""

import importlib.util
import os
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from repo_model.evaluation_splits import load_split_declaration

ROOT = Path(__file__).resolve().parents[1]
SHIM = ROOT / "scripts" / "month_end_readings_883_shim"
SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
spec = importlib.util.spec_from_file_location("month_end_readings_883", ROOT / "scripts" / "month_end_readings_883.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)


def row(day, days_to_month_end, spread=0.0, tax_date=0.0):
    values = {"quarter_end": 0.0, "tax_date": tax_date, "days_to_month_end": float(days_to_month_end)}
    return SimpleNamespace(date=day, values=values, spread_bps=spread)


class ReadingTests(unittest.TestCase):
    def test_a_friday_three_days_before_a_monday_month_end_is_month_end_only_by_the_business_day_reading(self):
        friday = row(date(2018, 4, 27), 3)
        self.assertEqual(script.reading_type(SPLITS, script.WINDOW, friday), "ordinary")
        self.assertEqual(script.reading_type(SPLITS, script.REPORTING, friday), "month_end")

    def test_the_tuesday_two_days_before_a_thursday_month_end_is_month_end_only_by_the_window(self):
        tuesday = row(date(2018, 5, 29), 2)
        self.assertEqual(script.reading_type(SPLITS, script.WINDOW, tuesday), "month_end")
        self.assertEqual(script.reading_type(SPLITS, script.REPORTING, tuesday), "ordinary")

    def test_an_unknown_reading_is_refused(self):
        with self.assertRaises(ValueError):
            script.reading_type(SPLITS, "calendar", row(date(2018, 5, 29), 2))


class DisagreementTests(unittest.TestCase):
    def test_only_the_days_that_differ_are_listed_with_their_pressure_flag(self):
        rows = [
            row(date(2018, 4, 27), 3, spread=7.0),
            row(date(2018, 5, 29), 2, spread=1.0),
            row(date(2018, 5, 15), 16),
            row(date(2018, 5, 31), 0),
        ]
        listed = script.disagreeing_days(rows, SPLITS)
        self.assertEqual([d["date"] for d in listed], ["2018-04-27", "2018-05-29"])
        self.assertEqual([d["month_end_by"] for d in listed], ["reporting only", "window only"])
        self.assertEqual([d["pressure_day"] for d in listed], [True, False])

    def test_a_day_after_the_last_scored_day_is_not_read(self):
        self.assertEqual(script.disagreeing_days([row(date(2026, 1, 29), 2)], SPLITS), [])


class ShimTests(unittest.TestCase):
    def _kind(self, reading):
        code = (
            "from datetime import date\n"
            "from repo_model.evaluation_splits import load_split_declaration\n"
            f"s = load_split_declaration({str(ROOT / 'metadata' / 'evaluation_splits.json')!r})\n"
            "v = {'quarter_end': 0.0, 'tax_date': 0.0, 'days_to_month_end': 3.0}\n"
            "print(s.reporting_day_type(date(2018, 4, 27), v))\n"
        )
        env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(ROOT / "src"), str(SHIM)]))
        if reading is not None:
            env["MONTH_END_READING"] = reading
        return subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True).stdout.strip()

    def test_the_default_leaves_the_reporting_reading_alone(self):
        self.assertEqual(self._kind(None), "month_end")
        self.assertEqual(self._kind("reporting"), "month_end")

    def test_the_window_setting_makes_the_reporting_call_read_the_window(self):
        self.assertEqual(self._kind("window"), "ordinary")

    def test_an_unknown_setting_stops_the_process(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self._kind("calendar")


if __name__ == "__main__":
    unittest.main()
