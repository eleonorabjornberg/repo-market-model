"""The before/after comparison of the Fed repo re-screen (#692).

Exploration on development data. The comparison reads two runs of the same screen on the same tree, one with the
take-up columns as they were and one as #659 corrected them, and reports what moved. It scores nothing and reads no
2026 day.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("fed_rescreen_692", ROOT / "scripts" / "fed_rescreen_692.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["fed_rescreen_692"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class LeafDiffs(unittest.TestCase):
    def test_equal_documents_have_no_difference(self):
        doc = {"a": {"x": 1.0, "y": [1, 2, {"z": None}]}}
        self.assertEqual(SCRIPT.leaf_diffs(doc, {"a": {"x": 1.0, "y": [1, 2, {"z": None}]}}), [])

    def test_a_moved_number_is_named_by_its_path(self):
        diffs = SCRIPT.leaf_diffs({"a": {"x": 1.0, "w": 2.0}}, {"a": {"x": 1.5, "w": 2.0}})
        self.assertEqual([d[0] for d in diffs], [("a", "x")])

    def test_a_tolerance_below_1e_12_is_equal(self):
        self.assertEqual(SCRIPT.leaf_diffs({"x": 1.0}, {"x": 1.0 + 1e-14}), [])

    def test_a_key_present_on_one_side_only_is_a_difference(self):
        diffs = SCRIPT.leaf_diffs({"a": 1}, {"a": 1, "b": 2})
        self.assertEqual([d[0] for d in diffs], [("b",)])

    def test_none_against_a_number_is_a_difference(self):
        self.assertEqual(len(SCRIPT.leaf_diffs({"x": None}, {"x": 0.0})), 1)


class SeriesThatMoved(unittest.TestCase):
    def test_the_series_of_a_screen_are_read_from_the_second_path_element(self):
        diffs = [(("series", "fed_repo_ops", "leads", "1"), 1, 2), (("series", "tga", "kind"), "a", "b"), (("scope", "x"), 1, 2)]
        self.assertEqual(SCRIPT.series_of(diffs, "series"), {"fed_repo_ops", "tga"})

    def test_the_incremental_cells_are_read_from_the_third_path_element(self):
        diffs = [(("incremental", "cells", "tga", "1"), 1, 2), (("incremental", "top"), 1, 2)]
        self.assertEqual(SCRIPT.series_of(diffs, "incremental"), {"tga"})

    def test_a_series_outside_the_changed_columns_is_reported(self):
        self.assertEqual(SCRIPT.outside({"fed_repo_ops", "tga"}, SCRIPT.FED_PREFIX), {"tga"})
        self.assertEqual(SCRIPT.outside({"fed_repo_ops_sameday"}, SCRIPT.FED_PREFIX), set())


class Ranking(unittest.TestCase):
    def test_rank_by_strongest_absolute_correlation_over_the_leads(self):
        series = {"a": {"leads": {"1": {"all": {"pressure": {"rho": 0.1}}}, "5": {"all": {"pressure": {"rho": -0.4}}}}},
                  "b": {"leads": {"1": {"all": {"pressure": {"rho": 0.3}}}}},
                  "c": {"leads": {"1": {"all": {"pressure": {"rho": None}}}}}}
        self.assertEqual(SCRIPT.screen_ranks(series), {"a": 1, "b": 2})


if __name__ == "__main__":
    unittest.main()
