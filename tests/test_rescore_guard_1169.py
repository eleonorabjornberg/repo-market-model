"""#1169: the Mac re-score must not move any existing figure of #1023's result.json; only `studentized` entries may be new.

Recorded mutation: in `differences`, replacing `if key not in new:` with `if False:` let a removed value pass, and
`test_removed_value_is_a_difference` errored with KeyError.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_rescore_unchanged_1169.py"
spec = importlib.util.spec_from_file_location("check_rescore_unchanged_1169", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

OLD = {"walks": {"1": {"cells": {"a": {"auroc": 0.61, "interval": [0.5, 0.7], "n": 4}}}}}


def with_studentized(extra=None):
    new = json.loads(json.dumps(OLD))
    cell = new["walks"]["1"]["cells"]["a"]
    cell["studentized"] = {"lower_bound": 0.01}
    cell.update(extra or {})
    return new


class DifferencesTest(unittest.TestCase):
    def test_added_studentized_only_is_clean(self):
        self.assertEqual(guard.differences(OLD, with_studentized()), [])

    def test_changed_point_value_is_a_difference(self):
        self.assertEqual(len(guard.differences(OLD, with_studentized({"auroc": 0.62}))), 1)

    def test_changed_interval_bound_is_a_difference(self):
        self.assertEqual(len(guard.differences(OLD, with_studentized({"interval": [0.5, 0.71]}))), 1)

    def test_removed_value_is_a_difference(self):
        new = with_studentized()
        del new["walks"]["1"]["cells"]["a"]["interval"]
        self.assertEqual(len(guard.differences(OLD, new)), 1)

    def test_other_added_key_is_a_difference(self):
        self.assertEqual(len(guard.differences(OLD, with_studentized({"extra": 1}))), 1)

    def test_list_length_change_is_a_difference(self):
        self.assertEqual(len(guard.differences(OLD, with_studentized({"interval": [0.5, 0.7, 0.9]}))), 1)


class CommandTest(unittest.TestCase):
    def run_cli(self, old, new):
        with tempfile.TemporaryDirectory() as d:
            po, pn = Path(d, "old.json"), Path(d, "new.json")
            po.write_text(json.dumps(old))
            pn.write_text(json.dumps(new))
            return subprocess.run([sys.executable, str(SCRIPT), "--old", str(po), "--new", str(pn)], capture_output=True, text=True)

    def test_exit_zero_when_only_studentized_added(self):
        self.assertEqual(self.run_cli(OLD, with_studentized()).returncode, 0)

    def test_exit_nonzero_when_a_value_moved(self):
        result = self.run_cli(OLD, with_studentized({"auroc": 0.62}))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("auroc", result.stderr)


if __name__ == "__main__":
    unittest.main()
