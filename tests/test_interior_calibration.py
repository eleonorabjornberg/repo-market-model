"""The interior-calibration judge (#243): its candidates, its guards, its declared test.

`scripts/interior_calibration_judge.py` scores the candidates declared in
`docs/declarations/interior_calibration_243.json` against the published
distribution on days before 2026-01-01 and writes `docs/runs/interior_calibration_243.json`.
These tests read no panel: the candidates and the test run on synthetic days, and the
record is checked against the declaration and the published records.

Written before the judge: every test below was run red against an empty module
(`ImportError`), then green.

Mutation record (`ObservabilityTests`, the conformal candidates' label guard): in
`conformal_interior`, `seen = bisect.bisect_right(dates, d["anchor"], 0, j)` changed to
`seen = j`, so every earlier day's label feeds the residuals whatever the anchor; confirmed
applied by grep. `test_a_label_after_the_anchor_is_not_read` then failed with `AssertionError`
(the offset moved with a label scored after the anchor). Restored, green.

Mutation record (`ObservabilityTests`, the anchor guard): in `conformal_interior`,
`if d["anchor"] >= d["date"]:` changed to `if False:`; confirmed applied by grep.
`test_an_anchor_on_or_after_the_scored_day_is_refused` then failed with `AssertionError`
(`LookAheadError not raised`). Restored, green.

Mutation record (`WindowGuardTests`): in `check_window`, `if last > WINDOW[1]:` changed to
`if False:`; confirmed applied by grep. `test_a_day_after_the_window_is_refused` then failed with
`AssertionError` (`LookAheadError not raised`). Restored, green.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
DECLARATION = REPO / "docs" / "declarations" / "interior_calibration_243.json"
RECORD = REPO / "docs" / "runs" / "interior_calibration_243.json"


def _script():
    spec = importlib.util.spec_from_file_location(
        "interior_calibration_judge", REPO / "scripts" / "interior_calibration_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


judge = _script()
VECTOR = [-4.0, -1.0, 0.0, 1.0, 4.0]


def _days(n, *, y=lambda k: 0.0, lag=1, start=date(2018, 6, 29), kinds=None):
    out = []
    for k in range(n):
        when = start + timedelta(days=k)
        out.append({"date": when.isoformat(), "anchor": (when - timedelta(days=lag)).isoformat(),
                    "y": y(k), "issued": list(VECTOR), "kind": (kinds[k] if kinds else "ordinary")})
    return out


class ConformalTests(unittest.TestCase):
    def test_nothing_moves_before_the_minimum_is_observable(self):
        days = _days(70, y=lambda k: 3.0)
        vectors = judge.conformal_interior(days, window=250, minimum=60)
        for k in range(60):
            self.assertEqual(vectors[k], VECTOR)
        self.assertNotEqual(vectors[69], VECTOR)

    def test_the_offsets_are_the_residual_quantiles(self):
        # y is always 3: every residual y - q_tau is 3 - q_tau, so the tau-quantile of them is the same.
        days = _days(100, y=lambda k: 3.0)
        vector = judge.conformal_interior(days, window=250, minimum=60)[99]
        self.assertEqual(vector[0], VECTOR[0])
        self.assertEqual(vector[4], VECTOR[4])
        self.assertAlmostEqual(vector[1], 3.0)   # q25 + (3 - q25)
        self.assertAlmostEqual(vector[2], 3.0)
        self.assertAlmostEqual(vector[3], 3.0)

    def test_the_vector_never_crosses(self):
        days = _days(120, y=lambda k: (k % 7) - 3.0)
        for vector in judge.conformal_interior(days, window=250, minimum=60):
            self.assertEqual(list(vector), sorted(vector))

    def test_a_class_with_too_few_residuals_uses_the_pooled_ones(self):
        kinds = ["turn" if k % 30 == 0 else "ordinary" for k in range(100)]
        days = _days(100, y=lambda k: 3.0, kinds=kinds)
        by_class = judge.conformal_interior(days, window=250, minimum=60, by_kind=True)
        pooled = judge.conformal_interior(days, window=250, minimum=60)
        turn = [k for k in range(70, 100) if kinds[k] == "turn"]
        self.assertTrue(turn)
        for k in turn:
            self.assertEqual(by_class[k], pooled[k])


class ObservabilityTests(unittest.TestCase):
    def test_a_label_after_the_anchor_is_not_read(self):
        # Labels scored on days 0..79 are all large, but the anchor of day 80 is day 10: only the first
        # 11 labels (under the minimum) are observable, so day 80's vector must be the base vector.
        days = _days(81, y=lambda k: 5.0)
        days[80]["anchor"] = days[10]["date"]
        self.assertEqual(judge.conformal_interior(days, window=250, minimum=60)[80], VECTOR)

    def test_an_anchor_on_or_after_the_scored_day_is_refused(self):
        days = _days(70, y=lambda k: 1.0)
        days[65]["anchor"] = days[65]["date"]
        with self.assertRaises(LookAheadError):
            judge.conformal_interior(days, window=250, minimum=60)


class WindowGuardTests(unittest.TestCase):
    def test_a_day_after_the_window_is_refused(self):
        with self.assertRaises(LookAheadError):
            judge.check_window(["2025-12-31", "2026-01-02"])

    def test_the_last_window_day_is_allowed(self):
        judge.check_window(["2018-06-29", "2025-12-31"])


class VerdictTests(unittest.TestCase):
    def _cell(self, low, high, days=50):
        return {"days": days, "mean": (low + high) / 2, "interval": {"lower": low, "upper": high}}

    def test_met_when_the_pooled_interval_is_above_zero_and_no_cell_is_worse(self):
        v = judge.verdict(self._cell(0.01, 0.05), {"a": self._cell(-0.02, 0.04), "b": self._cell(0.0, 0.1)})
        self.assertTrue(v["met"])

    def test_not_met_when_the_pooled_interval_includes_zero(self):
        v = judge.verdict(self._cell(-0.01, 0.05), {"a": self._cell(0.01, 0.04)})
        self.assertFalse(v["met"])
        self.assertTrue(v["pooled_above_zero"] is False)

    def test_not_met_when_a_cell_is_worse_beyond_its_interval(self):
        v = judge.verdict(self._cell(0.01, 0.05), {"a": self._cell(-0.09, -0.01)})
        self.assertFalse(v["met"])
        self.assertEqual(v["worse_cells"], ["a"])

    def test_a_small_cell_is_never_flagged(self):
        v = judge.verdict(self._cell(0.01, 0.05), {"a": self._cell(-0.09, -0.01, days=19)})
        self.assertTrue(v["met"])


class DeclarationTests(unittest.TestCase):
    def test_every_candidate_the_judge_scores_is_declared(self):
        declared = set(json.loads(DECLARATION.read_text())["candidates"])
        self.assertEqual(set(judge.CANDIDATES), declared)

    def test_an_undeclared_candidate_is_refused(self):
        with self.assertRaises(ValueError):
            judge.require_declared("conformal_secret")

    def test_the_declaration_states_the_directive_test(self):
        d = json.loads(DECLARATION.read_text())
        self.assertIn("above zero", d["test"]["statement"])
        self.assertEqual(d["window"]["last"], "2025-12-31")


@unittest.skipUnless(RECORD.exists(), "the record is made by the judge")
class RecordTests(unittest.TestCase):
    def test_the_record_carries_the_declaration_it_was_scored_under(self):
        record = json.loads(RECORD.read_text())
        self.assertEqual(record["declaration_sha256"], judge.declaration_sha256())

    def test_the_record_scores_no_locked_day(self):
        record = json.loads(RECORD.read_text())
        self.assertLessEqual(record["window"]["last"], "2025-12-31")

    def test_the_published_side_reproduces_the_published_crps(self):
        record = json.loads(RECORD.read_text())
        published = json.loads((REPO / "docs/runs/v1_interior_diagnosis.json").read_text())
        self.assertAlmostEqual(record["published"]["crps_bps"],
                               published["reproduction"]["mean_crps_2018_2025_bps"], places=9)


if __name__ == "__main__":
    unittest.main()
