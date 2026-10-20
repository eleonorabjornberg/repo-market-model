"""H1 step 2 (#967), re-read in the ruled orientation (#1013): the row check against #999 and the page's wording.

The calibration itself is tested in `test_scaled_score_967.TestTheCalibrationOrientation` (recorded mutation there). Here:
the row check passes only when D0 and D4 calibrated on `-e` reproduce #999's recorded figures, and the page states the
orientation it was calibrated in.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


script = load("scaled_score_1013")


def row(size, p3, p10):
    return {"size": size, "power_3": p3, "power_10": p10}


def record(figures, critical):
    return {"previous_orientation": {d: {"critical": dict(critical), "post_2020": row(*figures[d])} for d in script.ROW_CHECK}}


def previous(figures, critical):
    return {"designs": {d: {"critical": dict(critical), "post_2020": row(*figures[d])} for d in script.ROW_CHECK}}


class TestTheRowCheck(unittest.TestCase):
    FIGURES = {"D0": (0.011, 0.013, 0.014), "D4": (0.0, 0.0, 0.001)}
    CRITICAL = {"125": 15.66, "250": 4.32}

    def test_it_passes_when_the_old_orientation_reproduces_999(self):
        check = script.row_check(record(self.FIGURES, self.CRITICAL), previous(self.FIGURES, self.CRITICAL))
        self.assertTrue(check["all_reproduce"])

    def test_it_fails_when_a_figure_differs(self):
        moved = dict(self.FIGURES, D4=(0.0, 0.0, 0.002))
        check = script.row_check(record(moved, self.CRITICAL), previous(self.FIGURES, self.CRITICAL))
        self.assertFalse(check["all_reproduce"])
        self.assertFalse(check["designs"]["D4"]["reproduces"])
        self.assertTrue(check["designs"]["D0"]["reproduces"])

    def test_it_fails_when_a_critical_value_differs(self):
        check = script.row_check(record(self.FIGURES, {"125": 15.66, "250": 4.0}), previous(self.FIGURES, self.CRITICAL))
        self.assertFalse(check["all_reproduce"])


class TestTheNewPageIsSeparate(unittest.TestCase):
    def test_999s_record_and_page_stand_beside_the_new_ones(self):
        self.assertNotEqual(script.RECORD, script.PREVIOUS)
        self.assertNotEqual(script.PAGE, script.base.PAGE)


if __name__ == "__main__":
    unittest.main()
