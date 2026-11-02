"""The calibration-masking sensitivity on the candidate's bands (#1366): `scripts/calibration_masking_candidate_1366.py`.

The tests fix the arithmetic on hand cases: the honest filter (a training pair whose target row is after the last row observable at the
refit's decision is dropped, and counted), the closure audit (a forbidden import or token is found, a clean module is not), the import
closure of a small synthetic package, the recorder that wraps `spread_mean_reversion.training_rows` (it records every call, and in
the honest mode it filters), the paired difference of two sets of cells, and the refusal of a day after the window's end.

Recorded mutations (the guards this script adds):

* `observable_pairs`, the test `if target <= honest_anchor` replaced by `if target <= honest_anchor + 1`:
  `HonestFilterTests.test_a_pair_past_the_honest_anchor_is_dropped` fails with `AssertionError` (`[(1, 5), (2, 6)] != [(1, 5)]`);
  restored, it passes.
* `refuse_beyond`, the test `if day > last:` replaced by `if False:`: `WindowGuardTests.test_a_day_after_the_window_end_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`); restored, it passes.
* `forbidden_hits`, the token loop replaced by `for token in ():`: `ClosureTests.test_a_forbidden_token_is_found` fails with
  `AssertionError` (`[] != ['calibration_masking']`); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("calibration_masking_candidate_1366_script", REPO / "scripts" / "calibration_masking_candidate_1366.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


class HonestFilterTests(unittest.TestCase):
    def test_a_pair_past_the_honest_anchor_is_dropped(self):
        kept, dropped = script.observable_pairs([(0, 4), (1, 5), (2, 6)], honest_anchor=5)
        self.assertEqual(kept, [(0, 4), (1, 5)])
        self.assertEqual(dropped, [(2, 6)])

    def test_the_boundary_pair_is_kept(self):
        kept, dropped = script.observable_pairs([(1, 5)], honest_anchor=5)
        self.assertEqual((kept, dropped), ([(1, 5)], []))

    def test_nothing_is_dropped_when_every_target_is_observable(self):
        pairs = [(0, 1), (1, 2), (2, 3)]
        kept, dropped = script.observable_pairs(pairs, honest_anchor=3)
        self.assertEqual((kept, dropped), (pairs, []))


class WrapperTests(unittest.TestCase):
    """`Recorder` wraps `training_rows`: every call is recorded, and the honest mode filters by the per-lead honest anchor."""

    def fake_rows(self, *args, **kwargs):
        return {1: [(0, 1), (1, 2), (2, 3)], 2: [(0, 2), (1, 3)]}

    def test_the_as_run_mode_passes_rows_through_and_records_them(self):
        recorder = script.Recorder(honest=False, honest_anchor=lambda index, lead: 2)
        out = recorder.wrap(self.fake_rows)(None, 10, 9, lag=1, levels=None)
        self.assertEqual(out, self.fake_rows())
        record = recorder.calls[10]
        self.assertEqual(record["pairs"], {1: 3, 2: 2})
        self.assertEqual(record["would_drop"], {1: 1, 2: 1})
        self.assertEqual(record["dropped"], {1: 0, 2: 0})

    def test_the_honest_mode_filters_and_counts(self):
        recorder = script.Recorder(honest=True, honest_anchor=lambda index, lead: 2)
        out = recorder.wrap(self.fake_rows)(None, 10, 9, lag=1, levels=None)
        self.assertEqual(out, {1: [(0, 1), (1, 2)], 2: [(0, 2)]})
        self.assertEqual(recorder.calls[10]["dropped"], {1: 1, 2: 1})

    def test_repeated_calls_of_one_refit_agree(self):
        recorder = script.Recorder(honest=False, honest_anchor=lambda index, lead: 9)
        wrapped = recorder.wrap(self.fake_rows)
        wrapped(None, 10, 9, lag=1, levels=None)
        wrapped(None, 10, 9, lag=1, levels=None)
        self.assertEqual(sorted(recorder.calls), [10])
        self.assertEqual(recorder.calls[10]["calls"], 2)

    def test_a_refit_whose_calls_disagree_is_refused(self):
        recorder = script.Recorder(honest=False, honest_anchor=lambda index, lead: 9)
        rows = iter([{1: [(0, 1)]}, {1: [(0, 1), (1, 2)]}])
        wrapped = recorder.wrap(lambda *a, **k: next(rows))
        wrapped(None, 10, 9, lag=1, levels=None)
        with self.assertRaises(ValueError):
            wrapped(None, 10, 9, lag=1, levels=None)


class ClosureTests(unittest.TestCase):
    def test_a_forbidden_token_is_found(self):
        hits = script.forbidden_hits({"m": "settings['calibration_masking'] = 'held_out_row'\n"})
        self.assertEqual([hit.split(": ")[1] for hit in hits], ["calibration_masking"])

    def test_a_docstring_or_comment_that_names_a_token_is_not_code(self):
        source = '"""cross_conformal is mentioned here."""\n\ndef f():\n    """calibration_masking too."""\n    return 1  # cross_conformal\n'
        self.assertEqual(script.forbidden_hits({"m": source}), [])

    def test_a_keyword_argument_is_code(self):
        self.assertEqual(script.forbidden_hits({"m": "f(x, calibration_masking='held_out_row')\n"}), ["m: calibration_masking"])

    def test_a_clean_module_is_clean(self):
        self.assertEqual(script.forbidden_hits({"m": "def f():\n    return 1\n"}), [])

    def test_a_forbidden_module_name_is_found(self):
        self.assertEqual(script.forbidden_modules({"a", "ml", "walk_calibration"}), ["ml", "walk_calibration"])

    def test_the_import_closure_follows_relative_and_absolute_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("from . import b\nfrom .c import thing\nimport os\n", encoding="utf-8")
            (root / "b.py").write_text("from repo_model import d\n", encoding="utf-8")
            (root / "c.py").write_text("x = 1\n", encoding="utf-8")
            (root / "d.py").write_text("import repo_model.e\n", encoding="utf-8")
            (root / "e.py").write_text("", encoding="utf-8")
            (root / "unreached.py").write_text("", encoding="utf-8")
            self.assertEqual(script.import_closure(["a"], root), ["a", "b", "c", "d", "e"])


class DifferenceTests(unittest.TestCase):
    GRID = sp.GRID

    def law(self, offset=0.0):
        return [float(j) + offset for j in range(len(self.GRID))]

    def test_identical_cells_differ_by_exactly_zero(self):
        cells = [(self.law(), 7.0), (self.law(1.0), 3.0)]
        summary = script.paired_difference(cells, cells)
        self.assertEqual(summary["cells"], 2)
        self.assertEqual(summary["cells_differing"], 0)
        self.assertEqual(summary["max_abs_quantile_difference"], 0.0)
        self.assertEqual(summary["grid_crps"]["difference"], 0.0)
        self.assertEqual(summary["twcrps"]["difference"], 0.0)

    def test_a_shifted_forecast_has_a_signed_difference(self):
        as_run = [(self.law(), 7.0)]
        honest = [(self.law(2.0), 7.0)]
        summary = script.paired_difference(as_run, honest)
        self.assertEqual(summary["cells_differing"], 1)
        self.assertEqual(summary["max_abs_quantile_difference"], 2.0)
        expected = sp.grid_crps(honest[0][0], 7.0) - sp.grid_crps(as_run[0][0], 7.0)
        self.assertAlmostEqual(summary["grid_crps"]["difference"], expected)
        self.assertGreater(summary["grid_crps"]["difference"], 0.0)

    def test_the_band_coverage_is_the_closed_share(self):
        q = self.law()
        lo, hi = self.GRID.index(0.05), self.GRID.index(0.95)
        inside = script.band_coverage([(q, q[lo]), (q, 10.5), (q, q[hi] + 1.0)])
        self.assertAlmostEqual(inside["band90"], 2 / 3)
        self.assertEqual(script.band_coverage([])["band90"], None)

    def test_mismatched_cells_are_refused(self):
        with self.assertRaises(ValueError):
            script.paired_difference([(self.law(), 1.0)], [])


class WindowGuardTests(unittest.TestCase):
    def test_a_day_after_the_window_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_beyond([date(2025, 12, 31), date(2026, 1, 2)], date(2025, 12, 31))

    def test_the_last_day_itself_is_read(self):
        script.refuse_beyond([date(2025, 12, 30), date(2025, 12, 31)], date(2025, 12, 31))


if __name__ == "__main__":
    unittest.main()
