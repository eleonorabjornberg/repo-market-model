"""The final test's pre-registration is frozen (#150).

`docs/decisions/final-test-preregistration.md` pins the checksum of the
pre-registered model's declaration: its inputs, constants, calibrator and the
source of the code that fits and scores it
(`scripts/final_test_preregistration.py`, `declaration`). A change to any of
them after the record merges fails `FreezeTests`, before #151 opens the
lockbox.

Red first: this file was committed before the record existed, and
`FreezeTests` failed with `FileNotFoundError` on the missing record.

Mutation record (`RefuseLockedTests`, the selection run's own lockbox check):
`if any(when >= date(2026, 1, 1) ...)` in `_refuse_locked` mutated to
`date(2026, 1, 2)`, confirmed applied by grep; the test
`test_the_first_locked_day_is_refused` then failed with `AssertionError`
("ValueError not raised"). Restored, green.
"""

from __future__ import annotations

import importlib.util
import re
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "final_test_preregistration.py"
RECORD = REPO / "docs" / "decisions" / "final-test-preregistration.md"


def _script():
    spec = importlib.util.spec_from_file_location("final_test_preregistration", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fp = _script()


def _pinned(field):
    text = RECORD.read_text(encoding="utf-8")
    found = re.findall(rf"^- \*\*{re.escape(field)}:\*\* `([^`]+)`", text, flags=re.MULTILINE)
    if len(found) != 1:
        raise AssertionError(f"the record pins {field!r} {len(found)} times, not once")
    return found[0]


class FreezeTests(unittest.TestCase):
    """The pinned checksum is the declaration's, and the record names the chosen model."""

    def test_the_declaration_checksum_is_the_pinned_one(self):
        self.assertEqual(fp.declaration_checksum(), _pinned("Declaration checksum"))

    def test_the_record_names_the_chosen_model_and_calibrator(self):
        self.assertEqual(_pinned("Model"), fp.CHOSEN)
        self.assertEqual(_pinned("Calibrator"), fp.CHOSEN_CALIBRATOR)
        self.assertIn(fp.CHOSEN, fp.CANDIDATES)

    def test_a_changed_constant_moves_the_checksum(self):
        before = fp.declaration_checksum()
        moved = {**fp.onset.LEAP_JUMP_BP, 1: fp.onset.LEAP_JUMP_BP[1] + 1}
        with mock.patch.object(fp.onset, "LEAP_JUMP_BP", moved):
            self.assertNotEqual(fp.declaration_checksum(), before)
        with mock.patch.object(fp.pc, "MINIMUM_PAIRS", fp.pc.MINIMUM_PAIRS + 1):
            self.assertNotEqual(fp.declaration_checksum(), before)

    def test_changed_code_moves_the_checksum(self):
        """The checksum reads each pinned definition's source, so an edit to one moves it."""

        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            for path, _names in fp._SHARED_SOURCE + fp._MODEL_SOURCE[fp.CHOSEN]:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((REPO / path).read_text(encoding="utf-8"), encoding="utf-8")
            with mock.patch.object(fp, "REPO", root):
                self.assertEqual(fp.declaration_checksum(), _pinned("Declaration checksum"))
                walk = root / "src/repo_model/probability_calibration.py"
                text = walk.read_text(encoding="utf-8")
                walk.write_text(
                    text.replace("def walk_forward(", "def walk_forward(  # edited\n", 1),
                    encoding="utf-8",
                )
                self.assertNotEqual(fp.declaration_checksum(), _pinned("Declaration checksum"))

    def test_a_missing_definition_is_refused(self):
        with self.assertRaises(ValueError):
            fp._top_level_source("src/repo_model/onset.py", ("no_such_definition",))


class RuleTests(unittest.TestCase):
    """The two pre-stated rules, on synthetic cells."""

    @staticmethod
    def _paired(mean, lower, upper):
        return {"mean": mean, "interval": {"lower": lower, "upper": upper}}

    def test_platt_is_the_default_calibrator(self):
        cell = {"vs_platt": {
            "isotonic": self._paired(0.002, -0.001, 0.004),
            "beta": self._paired(-0.001, -0.002, 0.0),
            "platt_recency": self._paired(0.001, 0.0, 0.002),
        }}
        self.assertEqual(fp.choose_calibrator(cell), "platt")

    def test_a_gain_whose_interval_excludes_zero_replaces_platt_and_the_largest_wins(self):
        cell = {"vs_platt": {
            "isotonic": self._paired(0.002, 0.0001, 0.004),
            "beta": self._paired(0.003, -0.001, 0.007),
            "platt_recency": self._paired(0.0015, 0.0005, 0.0025),
        }}
        self.assertEqual(fp.choose_calibrator(cell), "isotonic")

    def test_the_highest_ranked_candidate_within_the_interval_is_chosen(self):
        scores = {name: {"within": False} for name in fp.CANDIDATES}
        scores["published_v1"]["within"] = True
        scores["stacked_combiner"]["within"] = True
        self.assertEqual(fp.choose_model(scores), "published_v1")
        scores["scarcity_calendar"]["within"] = True
        self.assertEqual(fp.choose_model(scores), "scarcity_calendar")

    def test_the_ranking_is_the_amendment_s(self):
        self.assertEqual(
            fp.CANDIDATES,
            ("scarcity_calendar", "dynamic_logit", "direct_logistic_sofr_p1",
             "published_v1", "v1_1", "stacked_combiner"),
        )


class RefuseLockedTests(unittest.TestCase):
    """The selection run refuses a locked day (`docs/decisions/lockbox.md`)."""

    def test_the_first_locked_day_is_refused(self):
        with self.assertRaises(ValueError):
            fp._refuse_locked([date(2025, 12, 31), date(2026, 1, 1)])

    def test_the_last_open_day_is_not(self):
        fp._refuse_locked([date(2025, 12, 30), date(2025, 12, 31)])


if __name__ == "__main__":
    unittest.main()
