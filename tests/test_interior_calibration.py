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

Mutation record (`AddendumCandidateTests`, the weighted, ACI and PID candidates' shared label guard):
in `_observable`, `return bisect.bisect_right(dates, d["anchor"], 0, j)` changed to `return j`;
confirmed applied by diff. `test_a_label_after_the_anchor_is_not_read` failed with `AssertionError`
(the day's vector moved with labels scored after its anchor) and
`test_a_stateful_candidate_refuses_an_anchor_that_moves_back` with `AssertionError: ValueError not raised`.
Restored, green.

Mutation record (`AddendumCandidateTests`, the shared anchor guard): in `_observable`,
`if d["anchor"] >= d["date"]:` changed to `if False:`; confirmed applied by diff.
`test_an_anchor_on_or_after_the_scored_day_is_refused` then failed with `AssertionError`
(`LookAheadError not raised`). Restored, green.

Mutation record (`AddendumCandidateTests`, the stateful candidates' monotone-anchor guard): in
`aci_conformal` and `pid_calendar`, `if seen < learned:` changed to `if False:`; confirmed applied by
diff. `test_a_stateful_candidate_refuses_an_anchor_that_moves_back` then failed with
`AssertionError: ValueError not raised`. Restored, green.
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
ADDENDUM = REPO / "docs" / "declarations" / "interior_calibration_243_addendum.json"


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
        declared = set(json.loads(DECLARATION.read_text())["candidates"]) | set(
            json.loads(ADDENDUM.read_text())["candidates"])
        self.assertEqual(set(judge.CANDIDATES), declared)

    def test_an_undeclared_candidate_is_refused(self):
        with self.assertRaises(ValueError):
            judge.require_declared("conformal_secret")

    def test_the_declaration_states_the_directive_test(self):
        d = json.loads(DECLARATION.read_text())
        self.assertIn("above zero", d["test"]["statement"])
        self.assertEqual(d["window"]["last"], "2025-12-31")


class AddendumCandidateTests(unittest.TestCase):
    """The four candidates of docs/declarations/interior_calibration_243_addendum.json."""

    def _with(self, days, regime=lambda k: "r"):
        for k, d in enumerate(days):
            d["regime"] = regime(k)
            d["group"] = d["kind"] + "|" + d["regime"]
        return days

    def test_a_group_with_too_few_residuals_falls_back_to_the_class(self):
        kinds = ["turn" if k % 3 == 0 else "ordinary" for k in range(200)]
        days = self._with(_days(200, y=lambda k: 3.0 + (k % 5), kinds=kinds),
                          regime=lambda k: "late" if k >= 190 else "early")
        by_group = judge.conformal_interior(days, window=250, minimum=60, keys=("group", "kind"))
        by_class = judge.conformal_interior(days, window=250, minimum=60, by_kind=True)
        late = [k for k in range(190, 200)]
        for k in late:
            self.assertEqual(by_group[k], by_class[k])
        self.assertNotEqual(by_group[150], VECTOR)

    def test_a_group_with_enough_residuals_uses_its_own(self):
        kinds = ["ordinary"] * 300
        days = self._with(_days(300, y=lambda k: 5.0 if k < 200 else 1.0, kinds=kinds),
                          regime=lambda k: "a" if k < 200 else "b")
        grouped = judge.conformal_interior(days, window=250, minimum=60, keys=("group", "kind"))
        pooled = judge.conformal_interior(days, window=250, minimum=60)
        # Day 290 is in regime b, whose own residuals (y = 1) are all that the group uses.
        self.assertAlmostEqual(grouped[290][2], 1.0)
        self.assertNotAlmostEqual(pooled[290][2], 1.0)

    def test_recent_residuals_weigh_more(self):
        days = self._with(_days(300, y=lambda k: 0.0 if k < 200 else 5.0))
        weighted = judge.weighted_conformal(days, window=250, minimum=60, half_life=60, off_regime_weight=0.25)
        pooled = judge.conformal_interior(days, window=250, minimum=60)
        self.assertGreater(weighted[299][2], pooled[299][2])

    def test_off_regime_residuals_weigh_less(self):
        days = self._with(_days(300, y=lambda k: 5.0 if k < 250 else 1.0),
                          regime=lambda k: "a" if k < 250 else "b")
        heavy = judge.weighted_conformal(days, window=250, minimum=60, half_life=1e9, off_regime_weight=1.0)
        light = judge.weighted_conformal(days, window=250, minimum=60, half_life=1e9, off_regime_weight=0.05)
        self.assertLess(light[299][2], heavy[299][2])
        self.assertAlmostEqual(light[299][2], 1.0, delta=0.5)

    def test_weighted_with_equal_weights_matches_pooled(self):
        days = self._with(_days(120, y=lambda k: (k % 7) - 3.0))
        weighted = judge.weighted_conformal(days, window=250, minimum=60, half_life=1e12, off_regime_weight=1.0)
        pooled = judge.conformal_interior(days, window=250, minimum=60)
        for a, b in zip(weighted[100:], pooled[100:]):
            for x, y in zip(a, b):
                self.assertAlmostEqual(x, y, delta=0.2)

    def test_aci_raises_the_level_when_the_outcome_keeps_landing_above(self):
        days = self._with(_days(300, y=lambda k: 5.0))
        adapted = judge.aci_conformal(days, window=250, minimum=60, gamma=0.01, clip=(0.02, 0.98))
        # y is always above every issued interior quantile, so each level drifts up and the shift grows.
        pooled = judge.conformal_interior(days, window=250, minimum=60)
        self.assertGreaterEqual(adapted[299][1], pooled[299][1])
        self.assertGreater(adapted[299][1], VECTOR[1])

    def test_aci_level_is_clipped(self):
        days = self._with(_days(2000, y=lambda k: 50.0))
        adapted = judge.aci_conformal(days, window=250, minimum=60, gamma=0.5, clip=(0.02, 0.98))
        for v in adapted:
            self.assertEqual(list(v), sorted(v))

    def test_pid_calendar_corrects_a_calendar_bias(self):
        kinds = ["turn" if k % 10 == 0 else "ordinary" for k in range(400)]
        days = self._with(_days(400, y=lambda k: 4.0 if k % 10 == 0 else 0.0, kinds=kinds))
        pid = judge.pid_calendar(days, window=250, minimum=60, step=0.05)
        plain = judge.pid_calendar(self._with(_days(400, y=lambda k: 4.0 if k % 10 == 0 else 0.0, kinds=["ordinary"] * 400)),
                                   window=250, minimum=60, step=0.05)
        turns = [k for k in range(300, 400) if kinds[k] == "turn"]
        err_pid = sum(abs(4.0 - pid[k][2]) for k in turns)
        err_plain = sum(abs(4.0 - plain[k][2]) for k in turns)
        self.assertLess(err_pid, err_plain)

    def test_every_new_vector_is_sorted(self):
        days = self._with(_days(150, y=lambda k: (k % 9) - 4.0, kinds=["turn" if k % 4 == 0 else "ordinary" for k in range(150)]))
        for vectors in (judge.weighted_conformal(days, window=250, minimum=60, half_life=60, off_regime_weight=0.25),
                        judge.aci_conformal(days, window=250, minimum=60, gamma=0.01, clip=(0.02, 0.98)),
                        judge.pid_calendar(days, window=250, minimum=60, step=0.05)):
            for v in vectors:
                self.assertEqual(list(v), sorted(v))

    def test_a_label_after_the_anchor_is_not_read(self):
        # From day 11 on every anchor is day 10: labels on days 11..79 must not move day 80's vector, whatever they are.
        for run in self._runs():
            vectors = []
            for late in (5.0, -5.0):
                days = self._with(_days(81, y=lambda k: 5.0 if k <= 10 else late))
                for k in range(11, 81):
                    days[k]["anchor"] = days[10]["date"]
                vectors.append(run(days)[80])
            self.assertEqual(vectors[0], vectors[1])

    def test_an_anchor_on_or_after_the_scored_day_is_refused(self):
        for run in self._runs():
            days = self._with(_days(70, y=lambda k: 1.0))
            days[65]["anchor"] = days[65]["date"]
            with self.assertRaises(LookAheadError):
                run(days)

    def test_a_stateful_candidate_refuses_an_anchor_that_moves_back(self):
        for run in self._runs()[2:]:
            days = self._with(_days(90, y=lambda k: 1.0))
            days[70]["anchor"] = days[10]["date"]
            with self.assertRaises(ValueError):
                run(days)

    def _runs(self):
        return (
            lambda d: judge.conformal_interior(d, window=250, minimum=60, keys=("group", "kind")),
            lambda d: judge.weighted_conformal(d, window=250, minimum=60, half_life=60, off_regime_weight=0.25),
            lambda d: judge.aci_conformal(d, window=250, minimum=60, gamma=0.01, clip=(0.02, 0.98)),
            lambda d: judge.pid_calendar(d, window=250, minimum=60, step=0.05),
        )


class TwoDeclarationTests(unittest.TestCase):
    def test_the_addendum_candidates_are_declared_and_the_first_file_is_untouched(self):
        addendum = json.loads(ADDENDUM.read_text())
        self.assertEqual(set(judge.ADDENDUM_CANDIDATES), set(addendum["candidates"]))
        first = json.loads(DECLARATION.read_text())
        self.assertFalse(set(first["candidates"]) & set(addendum["candidates"]))
        self.assertEqual(set(judge.CANDIDATES), set(first["candidates"]) | set(addendum["candidates"]))

    def test_an_addendum_candidate_passes_the_declared_check(self):
        judge.require_declared("conformal_aci")

    def test_the_addendum_says_what_it_leaves_out_and_why(self):
        addendum = json.loads(ADDENDUM.read_text())
        self.assertIn("dtaci_left_out", addendum["candidates"]["conformal_aci"])


@unittest.skipUnless(RECORD.exists(), "the record is made by the judge")
class RecordTests(unittest.TestCase):
    def test_the_record_carries_the_declaration_it_was_scored_under(self):
        record = json.loads(RECORD.read_text())
        self.assertEqual(record["declaration_sha256"], judge.declaration_sha256())
        self.assertEqual(record["addendum_sha256"], judge.addendum_sha256())

    def test_the_record_scores_no_locked_day(self):
        record = json.loads(RECORD.read_text())
        self.assertLessEqual(record["window"]["last"], "2025-12-31")

    def test_the_page_is_rendered_from_the_record(self):
        record = json.loads(RECORD.read_text())
        page = (REPO / "docs" / "interior_calibration_243.md").read_text()
        self.assertEqual(page, judge.render(record))

    def test_the_published_side_reproduces_the_published_crps(self):
        record = json.loads(RECORD.read_text())
        published = json.loads((REPO / "docs/runs/v1_interior_diagnosis.json").read_text())
        self.assertAlmostEqual(record["published"]["crps_bps"],
                               published["reproduction"]["mean_crps_2018_2025_bps"], places=9)


if __name__ == "__main__":
    unittest.main()
