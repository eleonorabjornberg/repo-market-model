"""The H.8 extract refuses a page that states an undeclared release time (#271).

`scripts/extract_h8_first_prints.py` reads the H.8 as public at the declared
16:15 release time (`ingest.FRB_H8_RELEASE_TIME`). A page stating a later time
would make that declaration early, which is the direction that leaks, so the
extract refuses it before writing. The refusal is `check_stated_release_time`,
factored out of `cut` so it can be tested without an archive of snapshots.

Recorded mutation (CLAUDE.md): in `check_stated_release_time`, `stated_time !=
FRB_H8_RELEASE_TIME` mutated to `False`. `test_a_page_stating_another_time_is_refused`
then fails, raising `AssertionError` ("ValueError not raised").
"""

from __future__ import annotations

import importlib.util
import unittest
from datetime import date, time
from pathlib import Path

from repo_model.ingest import FRB_H8_RELEASE_TIME

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "extract_h8_first_prints", ROOT / "scripts" / "extract_h8_first_prints.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StatedReleaseTimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.check = staticmethod(_load().check_stated_release_time)

    def test_a_page_stating_another_time_is_refused(self):
        for stated in (time(16, 30), time(15, 0), time(17, 15)):
            with self.subTest(stated=stated):
                with self.assertRaisesRegex(ValueError, "not the declared"):
                    self.check(date(2024, 5, 3), stated)

    def test_the_declared_time_and_a_page_stating_none_pass(self):
        self.check(date(2024, 5, 3), FRB_H8_RELEASE_TIME)
        self.check(date(2018, 1, 5), None)


if __name__ == "__main__":
    unittest.main()
