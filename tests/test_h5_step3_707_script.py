"""The measurement script of #707 (`scripts/h5_step3_707.py`): the parts that decide what is read and what is named.

Recorded mutations (the guards this script adds; the scorer's own lockbox guard is tested with the scorer):

* `require_resolved`, the test `if target >= decision:` replaced by `if False:`: `test_a_cell_not_resolved_before_the_decision_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`).
* `remedy_laws`, `bisect.bisect_left(targets, c.decision)` replaced by `bisect.bisect_right(targets, c.decision)`:
  `test_a_remedy_ignores_cells_resolved_on_or_after_the_decision` fails with `LookAheadError` (raised by `require_resolved` itself: the cell resolved on the
  decision day itself is read, and `require_resolved` refuses it).
* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("h5_step3_707_script", REPO / "scripts" / "h5_step3_707.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

G = len(sp.GRID)


def flat(value: float):
    return [float(value)] * G


def spread_law(median: float, half_width: float):
    """A law whose quantiles run from median - half_width to median + half_width over the grid."""

    return [median + half_width * (2.0 * level - 1.0) for level in sp.GRID]


def days(count: int, start: date = date(2024, 1, 1)):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def cells_of(count: int, make, lead: int = 1):
    """Cells of one lead: decision day i, target day i + lead; `make(i)` returns (law, benchmark law, outcome)."""

    calendar = days(count + lead)
    out = []
    for i in range(count):
        law, bench, outcome = make(i)
        out.append(script.Cell(calendar[i], calendar[i + lead], law, bench, outcome))
    return out


class GuardTests(unittest.TestCase):
    def test_a_cell_not_resolved_before_the_decision_is_refused(self):
        day = date(2024, 5, 7)
        with self.assertRaises(LookAheadError):
            script.require_resolved(day, day, where="test")
        with self.assertRaises(LookAheadError):
            script.require_resolved(day + timedelta(days=1), day, where="test")
        script.require_resolved(day - timedelta(days=1), day, where="test")

    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2026, 9, 4)])


class RemedyTests(unittest.TestCase):
    def test_the_level_remedy_removes_a_constant_bias_once_it_has_history(self):
        cells = cells_of(200, lambda i: (flat(5.0), flat(0.0), 1.0))
        out = script.remedy_laws(cells, "level")
        self.assertEqual(out[cells[10].decision], flat(5.0))  # fewer than 60 resolved cells: the identity
        self.assertEqual(out[cells[150].decision], flat(1.0))  # the median of y - q50 is -4

    def test_the_scale_remedy_narrows_an_over_dispersed_law(self):
        cells = cells_of(200, lambda i: (spread_law(0.0, 8.0), flat(0.0), 0.0))
        out = script.remedy_laws(cells, "scale")
        late = out[cells[150].decision]
        self.assertAlmostEqual(late[-1] - late[0], 0.5 * 16.0 * 0.98, delta=0.5 * 16.0 * 0.02)
        self.assertEqual(out[cells[10].decision], spread_law(0.0, 8.0))

    def test_the_scale_remedy_keeps_a_well_dispersed_law(self):
        # outcomes drawn from the law's own quantiles in rotation: the declared factor 1 is best
        cells = cells_of(300, lambda i: (spread_law(0.0, 4.0), flat(0.0), spread_law(0.0, 4.0)[i % G]))
        out = script.remedy_laws(cells, "scale")
        self.assertEqual(out[cells[250].decision], spread_law(0.0, 4.0))

    def test_the_shrink_remedy_moves_to_the_better_forecast(self):
        bad_model = cells_of(200, lambda i: (flat(9.0), flat(0.0), 0.0))
        self.assertEqual(script.remedy_laws(bad_model, "shrink")[bad_model[150].decision], flat(0.0))
        bad_bench = cells_of(200, lambda i: (flat(0.0), flat(9.0), 0.0))
        self.assertEqual(script.remedy_laws(bad_bench, "shrink")[bad_bench[150].decision], flat(0.0))

    def test_a_remedy_ignores_cells_resolved_on_or_after_the_decision(self):
        cells = cells_of(200, lambda i: (flat(5.0), flat(0.0), 1.0), lead=3)
        decision = cells[150].decision
        before = script.remedy_laws(cells, "level")[decision]
        changed = [
            script.Cell(c.decision, c.target, c.law, c.benchmark, 1000.0 if c.target >= decision else c.outcome)
            for c in cells
        ]
        self.assertEqual(script.remedy_laws(changed, "level")[decision], before)

    def test_an_unknown_remedy_is_refused(self):
        with self.assertRaises(ValueError):
            script.remedy_laws(cells_of(80, lambda i: (flat(0.0), flat(0.0), 0.0)), "tune")


class PitTests(unittest.TestCase):
    def test_pit_brackets_the_outcome_between_levels(self):
        law = [float(i) for i in range(G)]
        self.assertAlmostEqual(script.pit(law, -1.0), sp.GRID[0] / 2.0)
        self.assertAlmostEqual(script.pit(law, float(G) + 5.0), (sp.GRID[-1] + 1.0) / 2.0)
        self.assertAlmostEqual(script.pit(law, 10.5), (sp.GRID[10] + sp.GRID[11]) / 2.0)

    def test_pit_of_a_tie_is_the_midpoint_of_the_tied_levels(self):
        self.assertAlmostEqual(script.pit(flat(2.0), 2.0), (sp.GRID[0] + sp.GRID[-1]) / 2.0)

    def test_pit_bins_have_the_declared_edges(self):
        self.assertEqual(script.pit_bin(0.05), 0)
        self.assertEqual(script.pit_bin(0.10), 1)
        self.assertEqual(script.pit_bin(0.60), 3)
        self.assertEqual(script.pit_bin(0.95), 5)
        self.assertEqual(len(script.PIT_EXPECTED), 6)
        self.assertAlmostEqual(sum(script.PIT_EXPECTED), 1.0)


class SplitTests(unittest.TestCase):
    def test_the_three_parts_add_up_to_the_gap(self):
        cells = cells_of(120, lambda i: (spread_law(3.0, 6.0), flat(0.0), (i % 3) - 1.0))
        split = script.loss_split(cells)
        self.assertAlmostEqual(split["level"] + split["dispersion"] + split["remainder"], split["gap"], places=9)

    def test_a_pure_level_error_is_all_level(self):
        cells = cells_of(120, lambda i: (flat(4.0), flat(0.0), 0.0))
        split = script.loss_split(cells)
        self.assertGreater(split["level"], 0.99 * split["gap"])

    def test_the_component_is_named_only_above_half_the_gap(self):
        self.assertEqual(script.name_component({"gap": 1.0, "level": 0.7, "dispersion": 0.2, "remainder": 0.1}), "level")
        self.assertEqual(script.name_component({"gap": 1.0, "level": 0.4, "dispersion": 0.3, "remainder": 0.3}), "no single component")
        self.assertEqual(script.name_component({"gap": -0.2, "level": 0.0, "dispersion": 0.0, "remainder": -0.2}), "no loss")


class TailReadingTests(unittest.TestCase):
    def test_under_dispersed(self):
        self.assertEqual(script.read_tail(exceed95_lower=0.09, median_pit=0.7, beyond_q99=0.1), "under-dispersed")

    def test_mislocated(self):
        self.assertEqual(script.read_tail(exceed95_lower=0.04, median_pit=0.97, beyond_q99=0.8), "mislocated")

    def test_both(self):
        self.assertEqual(script.read_tail(exceed95_lower=0.09, median_pit=0.97, beyond_q99=0.8), "both")

    def test_neither_resolved(self):
        self.assertEqual(script.read_tail(exceed95_lower=0.03, median_pit=0.7, beyond_q99=0.1), "neither resolved")


class PairedFallbackTests(unittest.TestCase):
    class Stub:
        @staticmethod
        def pair_table(scores, pairs, group, draws):
            if any(scores[b] == scores[c] for b, c in pairs):
                raise sp.ProtocolError("a resampled difference has no long-run variance; it cannot be studentized")
            return {f"{b} -> {c}": {"n": len(group)} for b, c in pairs}

    def test_an_identical_pair_is_reported_as_a_zero_difference(self):
        group = days(30)
        scores = {"A": {d: 1.0 + i for i, d in enumerate(group)}, "B": {d: 1.0 + i for i, d in enumerate(group)}}
        out = script.paired(self.Stub, scores, [("A", "B")], group, 10)
        self.assertTrue(out["A -> B"]["identical"])
        self.assertEqual(out["A -> B"]["mean_difference"], 0.0)

    def test_a_different_pair_beside_it_is_still_tested(self):
        group = days(30)
        scores = {
            "A": {d: 1.0 + i for i, d in enumerate(group)},
            "B": {d: 1.0 + i for i, d in enumerate(group)},
            "C": {d: 2.0 + i for i, d in enumerate(group)},
        }
        out = script.paired(self.Stub, scores, [("A", "B"), ("A", "C")], group, 10)
        self.assertTrue(out["A -> B"]["identical"])
        self.assertEqual(out["A -> C"], {"n": 30})


if __name__ == "__main__":
    unittest.main()
