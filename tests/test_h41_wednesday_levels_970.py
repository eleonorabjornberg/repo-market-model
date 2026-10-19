"""Wednesday levels beside the H.4.1 week averages (#970, H5): `scripts/h41_wednesday_levels_970.py`.

A Wednesday level is a line of the same release as the week average of its week, so it must be read at the average's
declared instant and no earlier. The measurement therefore replaces values and nothing else. The tests fix that, the
units, the checksum of the snapshot, the hole rule and the study window.

Recorded mutations (the guards this script adds):

* `substitute`, `available_at=row.available_at` replaced by `available_at=row.available_at - timedelta(days=5)` (the level
  read on its own Wednesday, before its print): `test_a_substituted_row_keeps_the_averages_declared_instant` fails with
  `AssertionError` (the instants differ).
* `read_levels`, the comparison `if digest != expected_sha256:` replaced by `if False:`: `test_a_changed_snapshot_is_refused`
  fails with `AssertionError` (`ValueError not raised`).
* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`).
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("h41_wednesday_levels_970_script", REPO / "scripts" / "h41_wednesday_levels_970.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.data import PointInTimeObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

WED1, WED2, WED3 = date(2024, 1, 3), date(2024, 1, 10), date(2024, 1, 17)


def row(series, ref, value, *, offset=0):
    return PointInTimeObservation(
        series, ref, datetime(2026, 9, 6, 19, 59, tzinfo=timezone.utc) + timedelta(minutes=offset), value, "v1", "sha1"
    )


class SubstituteTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            row("WRESBAL", WED1, 3.0), row("WRESBAL", WED2, 3.1), row("WRESBAL", WED3, 3.2),
            row("WTREGEN", WED1, 0.7), row("IORB", WED1, 5.4),
        ]
        self.levels = {WED1: 3200.0, WED2: 3300.0}  # millions; no level for WED3

    def test_values_are_the_levels_in_billions_and_other_series_are_untouched(self):
        out, counts = script.substitute(self.rows, "WRESBAL", self.levels)
        by_ref = {(r.series_id, r.ref_date): r.value for r in out}
        self.assertAlmostEqual(by_ref[("WRESBAL", WED1)], 3.2)
        self.assertAlmostEqual(by_ref[("WRESBAL", WED2)], 3.3)
        self.assertEqual(by_ref[("WTREGEN", WED1)], 0.7)
        self.assertEqual(by_ref[("IORB", WED1)], 5.4)

    def test_a_week_with_no_level_is_a_hole_never_the_average(self):
        out, counts = script.substitute(self.rows, "WRESBAL", self.levels)
        self.assertNotIn(("WRESBAL", WED3), {(r.series_id, r.ref_date) for r in out})
        self.assertEqual(counts, {"replaced": 2, "dropped": 1, "kept_after_end": 0})

    def test_a_substituted_row_keeps_the_averages_declared_instant(self):
        out, _ = script.substitute(self.rows, "WRESBAL", self.levels)
        before = {r.ref_date: r for r in self.rows if r.series_id == "WRESBAL"}
        for r in out:
            if r.series_id == "WRESBAL":
                self.assertEqual(r.available_at, before[r.ref_date].available_at)
                self.assertEqual((r.vintage_id, r.source_sha), (before[r.ref_date].vintage_id, before[r.ref_date].source_sha))

    def test_a_row_after_the_study_end_keeps_its_average(self):
        late = date(2026, 1, 7)
        out, counts = script.substitute([row("WRESBAL", late, 9.9)], "WRESBAL", {late: 5000.0})
        self.assertEqual([r.value for r in out], [9.9])
        self.assertEqual(counts["kept_after_end"], 1)


class SnapshotTests(unittest.TestCase):
    def write(self, directory: Path, text: str, digest=None):
        (directory / "S.csv").write_text(text, encoding="utf-8")
        digest = digest or hashlib.sha256(text.encode("utf-8")).hexdigest()
        return {"S.csv": digest}

    def test_a_snapshot_is_read_as_served_with_missing_marked(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            expected = self.write(directory, "observation_date,S\n2024-01-03,3200\n2024-01-10,.\n")
            self.assertEqual(script.read_levels(directory / "S.csv", expected["S.csv"]), {WED1: 3200.0})

    def test_a_changed_snapshot_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write(directory, "observation_date,S\n2024-01-03,3200\n")
            with self.assertRaises(ValueError):
                script.read_levels(directory / "S.csv", "0" * 64)

    def test_the_tracked_snapshot_matches_its_declaration(self):
        declared = script.committed_files()
        for name, digest in declared.items():
            levels = script.read_levels(script.SNAPSHOT / name, digest)
            self.assertGreater(len(levels), 1000)
            self.assertTrue(all(d.weekday() == 2 for d in levels), name)  # Wednesdays


class MovementTests(unittest.TestCase):
    def test_changes_up_down_and_the_risky_set_are_counted(self):
        d = [date(2024, 1, 1) + timedelta(days=i) for i in range(5)]
        old = {d[0]: 1.0, d[1]: 1.0, d[2]: 2.0, d[3]: 3.0, d[4]: None}
        new = {d[0]: 1.0, d[1]: 2.0, d[2]: 1.0, d[3]: 3.0, d[4]: None}
        m = script.movement(old, new)
        self.assertEqual((m["days"], m["changed"], m["up"], m["down"]), (5, 2, 1, 1))
        self.assertEqual((m["enter_risky_set"], m["leave_risky_set"]), (1, 1))

    def test_unlike_day_sets_are_refused(self):
        with self.assertRaises(ValueError):
            script.movement({date(2024, 1, 1): 1.0}, {date(2024, 1, 2): 1.0})


class GuardTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2026, 9, 10)])

    def test_the_study_ends_on_the_last_day_before_the_lockbox(self):
        self.assertEqual(script.LAST_DAY, date(2025, 12, 31))


if __name__ == "__main__":
    unittest.main()
