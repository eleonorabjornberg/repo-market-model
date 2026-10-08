"""The 2026 confirmation of the #243 band candidates (#408): its declaration and its guards.

`scripts/interior_confirmation_408.py` scores the candidates listed in
`docs/declarations/interior_confirmation_408.json` on 2026-01-01 to 2026-09-03 only, under the #243 test.
These tests read no panel.

Written before the script: every test was run red against a missing module (`FileNotFoundError`), then green.

Mutation record (`WindowTests`, the scored-day guard): in `check_scored`,
`if first < WINDOW[0] or last > WINDOW[1]:` changed to `if False:`; confirmed applied by grep.
`test_a_day_outside_the_window_is_refused` then failed with `AssertionError` (`LookAheadError not raised`).
Restored, green.

Mutation record (`DeclarationTests`, the candidate guard): in `require_declared`,
`if name not in declared_candidates():` changed to `if False:`; confirmed applied by grep.
`test_an_undeclared_candidate_is_refused` then failed with `AssertionError` (`ValueError not raised`).
Restored, green.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
DECLARATION = REPO / "docs" / "declarations" / "interior_confirmation_408.json"


def _script():
    spec = importlib.util.spec_from_file_location(
        "interior_confirmation_408", REPO / "scripts" / "interior_confirmation_408.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


confirm = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_five_candidates_that_met_the_243_test_are_declared(self):
        d = json.loads(DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(sorted(d["candidates"]), sorted([
            "pressure_model_v2", "conformal_pid_calendar", "conformal_recency_regime",
            "conformal_by_day_type", "conformal_group_regime"]))
        self.assertEqual(d["window"]["first"], "2026-01-01")
        self.assertEqual(d["window"]["last"], "2026-09-03")

    def test_every_declared_candidate_is_one_of_243s(self):
        from_243 = set(confirm.judge.CANDIDATES)
        self.assertLessEqual(set(confirm.declared_candidates()), from_243)

    def test_an_undeclared_candidate_is_refused(self):
        with self.assertRaises(ValueError):
            confirm.require_declared("conformal_aci")
        confirm.require_declared("pressure_model_v2")


class WindowTests(unittest.TestCase):
    def test_a_day_outside_the_window_is_refused(self):
        with self.assertRaises(LookAheadError):
            confirm.check_scored(["2025-12-31", "2026-01-02"])
        with self.assertRaises(LookAheadError):
            confirm.check_scored(["2026-01-02", "2026-09-04"])

    def test_the_window_itself_is_allowed(self):
        confirm.check_scored(["2026-01-02", "2026-09-03"])


class RecordTests(unittest.TestCase):
    def test_the_record_covers_only_the_window_when_it_exists(self):
        path = REPO / "docs" / "runs" / "interior_confirmation_408.json"
        if not path.exists():
            self.skipTest("not scored yet")
        record = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(record["window"]["first"], "2026-01-01")
        self.assertLessEqual(record["window"]["last"], "2026-09-03")
        self.assertEqual(sorted(record["candidates"]), sorted(confirm.declared_candidates()))


if __name__ == "__main__":
    unittest.main()
