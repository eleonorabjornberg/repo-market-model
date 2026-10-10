"""The false-alarm controls on the every-day component (#532) agree with their declaration and are causal.

Recorded mutations (the controls that read earlier forecasts are a leakage guard: a forecast must not read
a later day's). In `scripts/risk_date_false_alarm_controls.py`:

* `_persist` read the next day's forecast (`row[k + 1]`) instead of the previous day's (`row[k - 1]`):
  `CausalityTests.test_a_control_reads_no_later_forecast` failed with an AssertionError (the control's
  output on an earlier day moved when a later day's raw forecast changed).
* `_gate` took its window as `range(max(0, k - window), min(len(off), k + 2))` instead of
  `range(max(0, k - window), k)`, so that it read the day itself and the next day's forecast:
  `CausalityTests.test_the_gate_cut_is_set_by_earlier_days_only` failed with an AssertionError
  (`0.0 != 0.25`).
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model import pressure_judge as pj

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "risk_date_false_alarm_controls.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
JUDGE_CANDIDATES = dict(pj.load_declaration().candidates)


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location(
        "risk_date_false_alarm_controls_script", ROOT / "scripts" / "risk_date_false_alarm_controls.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(PARENTS), DECLARED)

    def test_at_most_four_controls(self):
        self.assertLessEqual(len(DECLARED["controls"]), 4)
        self.assertEqual(set(DECLARED["controls"]), set(SCRIPT.CONTROLS))

    def test_the_parents_are_the_five_risk_date_passers_and_unchanged(self):
        for name, spec in DECLARED["parents"].items():
            self.assertEqual(spec, PARENTS["candidates"][name])
        self.assertEqual(len(DECLARED["parents"]), 5)

    def test_every_variant_is_a_judge_candidate_with_the_every_day_variants_features(self):
        for parent in DECLARED["parents"]:
            base = JUDGE_CANDIDATES[parent + "+every_day"]
            for control in DECLARED["controls"]:
                entry = JUDGE_CANDIDATES[f"{parent}+every_day+{control}"]
                self.assertEqual(entry["role"], "candidate")
                self.assertEqual(entry["parent"], parent)
                self.assertEqual(entry["features"], base["features"])

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_nothing_is_published(self):
        self.assertIn("nothing", DECLARED["published"])


RAW = [
    [0.0, 0.2, 0.3, 0.1, 0.4, 0.5, 0.0, 0.2],
    [0.0, 0.1, 0.2, 0.05, 0.3, 0.2, 0.0, 0.1],
]
OFF = [False, True, True, True, True, True, False, True]
STATE = [None, 0, 1, 2, 1, 0, 3, 3]


def _apply(name, raw=RAW, off=OFF, state=STATE, params=None):
    return SCRIPT.apply_control(name, params or DECLARED["controls"][name], raw, off, state)


class ControlTests(unittest.TestCase):
    def test_a_risk_date_keeps_the_forecast_under_every_control(self):
        for name in DECLARED["controls"]:
            out = _apply(name)
            for j in range(len(RAW)):
                for k, off in enumerate(OFF):
                    if not off:
                        self.assertEqual(out[j][k], RAW[j][k], (name, j, k))

    def test_shrunk_scales_only_days_that_are_not_risk_dates(self):
        out = _apply("shrunk", params={"weight": 0.5})
        self.assertEqual(out[0][1], 0.1)
        self.assertEqual(out[0][5], 0.25)
        self.assertEqual(out[0][0], 0.0)

    def test_scarce_zeroes_a_day_whose_state_is_below_the_minimum_or_unread(self):
        out = _apply("scarce", params={"minimum_state": 1})
        self.assertEqual([out[0][k] for k in (1, 2, 3, 4, 5, 7)], [0.0, 0.3, 0.1, 0.4, 0.0, 0.2])

    def test_scarce_leaves_a_day_with_no_state_at_zero(self):
        out = SCRIPT.apply_control("scarce", {"minimum_state": 1}, [[0.5, 0.5]], [True, True], [None, 1])
        self.assertEqual(out[0], [0.0, 0.5])

    def test_persist_takes_the_smaller_of_two_consecutive_days_and_needs_a_first_day(self):
        out = _apply("persist", params={"days": 2})
        self.assertEqual(out[0][1], 0.0)  # the previous day (a risk date) forecast 0.0
        self.assertEqual(out[0][2], 0.2)
        self.assertEqual(out[0][3], 0.1)
        self.assertEqual(out[0][4], 0.1)
        first = SCRIPT.apply_control("persist", {"days": 2}, [[0.4, 0.4]], [True, True], [1, 1])
        self.assertEqual(first[0], [0.0, 0.4])

    def test_gate_passes_only_a_forecast_above_the_trailing_quantile_of_earlier_off_risk_forecasts(self):
        params = {"quantile": 0.5, "window": 4, "minimum_earlier": 2}
        raw = [[0.1, 0.2, 0.3, 0.05, 0.9, 0.2]]
        off = [True] * 6
        out = SCRIPT.apply_control("gate", params, raw, off, [None] * 6)
        # earlier off-risk forecasts, window 4: day 2 sees {0.1, 0.2} -> median (nearest rank) 0.1, 0.3 > 0.1 passes
        self.assertEqual(out[0][0], 0.0)
        self.assertEqual(out[0][1], 0.0)  # fewer than 2 earlier values
        self.assertEqual(out[0][2], 0.3)
        self.assertEqual(out[0][3], 0.0)  # 0.05 is not above the median of {0.1, 0.2, 0.3}
        self.assertEqual(out[0][4], 0.9)

    def test_the_curve_across_thresholds_stays_non_increasing(self):
        raw = [[0.4, 0.4, 0.4, 0.4, 0.4, 0.4], [0.4, 0.4, 0.4, 0.4, 0.4, 0.4]]
        for name, params in DECLARED["controls"].items():
            out = SCRIPT.apply_control(name, params, raw, [True] * 6, [1] * 6)
            for k in range(6):
                self.assertGreaterEqual(out[0][k], out[1][k], (name, k))
        # a gate that passes the 5 bp forecast but not the 10 bp one cannot invert the curve either
        raw = [[0.1, 0.1, 0.1, 0.1, 0.2], [0.1, 0.1, 0.1, 0.1, 0.5]]
        out = SCRIPT.apply_control("gate", {"quantile": 0.5, "window": 4, "minimum_earlier": 2}, raw, [True] * 5, [1] * 5)
        self.assertLessEqual(out[1][4], out[0][4])

    def test_an_unknown_control_is_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.apply_control("nope", {}, RAW, OFF, STATE)


class CausalityTests(unittest.TestCase):
    def test_the_gate_cut_is_set_by_earlier_days_only(self):
        params = {"quantile": 0.5, "window": 4, "minimum_earlier": 2}
        out = SCRIPT.apply_control("gate", params, [[0.1, 0.2, 0.3, 0.25, 0.99]], [True] * 5, [None] * 5)
        self.assertEqual(out[0][3], 0.25)  # the cut is 0.2 from {0.1, 0.2, 0.3}; the later 0.99 and its own 0.25 do not move it

    def test_a_control_reads_no_later_forecast(self):
        steps = [0.37, 0.81, 0.12, 0.55, 0.93, 0.26, 0.68, 0.44, 0.07, 0.75, 0.31, 0.62, 0.19, 0.88, 0.5, 0.24]
        base = [list(steps), [0.5 * x for x in steps]]
        n = len(steps)
        off = [k % 4 != 0 for k in range(n)]
        state = [k % 4 for k in range(n)]
        params = {
            "shrunk": {"weight": 0.5},
            "scarce": {"minimum_state": 1},
            "persist": {"days": 2},
            "gate": {"quantile": 0.5, "window": 5, "minimum_earlier": 2},
        }
        for name, p in params.items():
            ref = SCRIPT.apply_control(name, p, base, off, state)
            for change in range(3, n):
                for value in (0.0, 0.99):
                    moved = [list(row) for row in base]
                    for row in moved:
                        row[change] = value
                    out = SCRIPT.apply_control(name, p, moved, off, state)
                    for j in range(2):
                        self.assertEqual(out[j][:change], ref[j][:change], (name, change, value))


if __name__ == "__main__":
    unittest.main()
