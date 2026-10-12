"""A second gate on the every-day part, by the tail spread's own trailing history (#601, step 2): the declaration, the candidate files and the cap.

Recorded mutations, 12 October 2026, in a disposable copy of `scripts/every_day_conditioning_601.py`, both in `tail_cap`:
1. the line `earlier = list(range(max(0, k - window), k))` replaced by `earlier = list(range(max(0, k - window), k + 1))` (a day's own reading, taken
   at its own decision instant, now sits in its cut-off's window). The `TailCapTests`, among them `test_a_later_reading_changes_nothing_earlier`,
   then error with `LookAheadError` raised by `_read_only_earlier`.
2. the same line, with the call `_read_only_earlier(k, earlier)` also deleted: `test_a_hole_is_not_kept_and_is_not_an_earlier_reading`,
   `test_a_risk_date_is_not_capped_and_is_not_an_earlier_reading`, `test_fewer_than_the_minimum_of_earlier_readings_is_not_kept` and
   `test_the_window_is_the_previous_window_scored_days` then fail with `AssertionError` (the day's own reading moves its cut-off).
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "every_day_conditioning_601.json").read_text())
CANDIDATES = ROOT / "metadata" / "pressure_judge" / "candidates"


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("every_day_conditioning_601_script", ROOT / "scripts" / "every_day_conditioning_601.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["every_day_conditioning_601_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(), DECLARED)

    def test_two_variants_and_no_more(self):
        self.assertEqual(sorted(DECLARED["variants"]), ["cap50", "cap75"])
        self.assertEqual(set(SCRIPT.VARIANTS), set(DECLARED["variants"]))
        for key, entry in DECLARED["variants"].items():
            self.assertEqual(entry["name"], SCRIPT.VARIANTS[key])
            self.assertTrue(entry["name"].startswith(SCRIPT.ROW + "+"))

    def test_the_quantiles_are_round_numbers_declared_not_read_from_a_score(self):
        self.assertEqual(DECLARED["variants"]["cap75"]["cap"], {"quantile": 0.75, "window": 250, "minimum_earlier": 60})
        self.assertEqual(DECLARED["variants"]["cap50"]["cap"], {"quantile": 0.5, "window": 250, "minimum_earlier": 60})

    def test_the_window_is_the_gates(self):
        self.assertEqual({k: v for k, v in SCRIPT.GATE.items() if k != "quantile"}, {"window": 250, "minimum_earlier": 60})

    def test_the_trigger_is_step_1s_committed_result(self):
        step_one = json.loads((ROOT / "docs" / "pivot" / "evidence" / "every-day-separation" / "separation.json").read_text())
        self.assertEqual(sorted(step_one["triggering_inputs"]), ["tail_spread_level"])
        self.assertEqual(DECLARED["trigger"]["inputs"], sorted(step_one["triggering_inputs"]))

    def test_the_scoring_ends_before_the_lockbox_and_nothing_is_published(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")
        published = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())
        for name in SCRIPT.VARIANTS.values():
            self.assertNotIn(name, json.dumps(published.get("confirmation", {})))
        self.assertIn("nothing", DECLARED["published"])


class CandidateFileTests(unittest.TestCase):
    def test_each_variant_has_a_candidate_file_naming_the_row_as_parent(self):
        for name in SCRIPT.VARIANTS.values():
            entry = json.loads((CANDIDATES / f"{name}.json").read_text())
            self.assertEqual(entry["role"], "candidate")
            self.assertEqual(entry["track"], "#601")
            self.assertEqual(entry["parent"], SCRIPT.ROW)
            self.assertIn("metadata/every_day_conditioning_601.json", entry["calibration"])
        self.assertEqual({n: json.loads((CANDIDATES / f"{n}.json").read_text()) for n in SCRIPT.VARIANTS.values()}, SCRIPT.candidate_entries())


def _caps(levels, off=None, **cap):
    params = dict(quantile=0.5, window=10, minimum_earlier=2)
    params.update(cap)
    return SCRIPT.tail_cap(levels, off or [True] * len(levels), **params)


class TailCapTests(unittest.TestCase):
    def test_a_day_is_kept_when_its_level_is_at_or_below_the_cut_of_its_trailing_readings(self):
        # earlier readings 1, 2, 3 -> the 0.5 nearest-rank cut is 2
        keep = _caps([1.0, 2.0, 3.0, 2.0, 2.5])
        self.assertEqual(keep, [False, False, False, True, False])

    def test_fewer_than_the_minimum_of_earlier_readings_is_not_kept(self):
        self.assertEqual(_caps([1.0, 1.0, 1.0], minimum_earlier=2), [False, False, True])

    def test_a_hole_is_not_kept_and_is_not_an_earlier_reading(self):
        self.assertEqual(_caps([1.0, None, 1.0, 1.0], minimum_earlier=2), [False, False, False, True])

    def test_a_risk_date_is_not_capped_and_is_not_an_earlier_reading(self):
        keep = _caps([5.0, 5.0, 9.0, 1.0, 1.0], off=[True, True, False, True, True], minimum_earlier=2)
        self.assertEqual(keep, [False, False, True, True, True])

    def test_the_window_is_the_previous_window_scored_days(self):
        # the small readings are older than the window of 2, so the cut is the recent large ones
        levels = [1.0, 1.0, 5.0, 5.0, 5.0]
        self.assertEqual(_caps(levels, window=2, minimum_earlier=2), [False, False, False, False, True])
        self.assertEqual(_caps(levels, window=10, minimum_earlier=2), [False, False, False, False, False])

    def test_a_later_reading_changes_nothing_earlier(self):
        base = [1.0, 2.0, 3.0, 2.0, 2.0, 9.0]
        changed = base[:-1] + [0.0]
        self.assertEqual(_caps(base)[:-1], _caps(changed)[:-1])

    def test_a_day_is_capped_by_its_own_trailing_history_only(self):
        a = _caps([1.0, 1.0, 1.0, 2.0])
        b = _caps([1.0, 1.0, 1.0, 2.0, 0.0, 0.0, 0.0])
        self.assertEqual(a, b[:4])

    def test_the_window_never_holds_the_day_itself_or_a_later_day(self):
        with self.assertRaises(LookAheadError):
            SCRIPT._read_only_earlier(3, [1, 2, 3])
        with self.assertRaises(LookAheadError):
            SCRIPT._read_only_earlier(3, [4])
        SCRIPT._read_only_earlier(3, [0, 1, 2])

    def test_apply_zeroes_a_forecast_that_is_not_kept_and_keeps_the_curve_non_increasing(self):
        forecasts = {"5": {"d0": 0.5, "d1": 0.5, "d2": 0.5}, "10": {"d0": 0.4, "d1": 0.4, "d2": 0.4}}
        out = SCRIPT.apply_cap(forecasts, ["d0", "d1", "d2"], [False, True, False])
        self.assertEqual(out["5"], {"d0": 0.0, "d1": 0.5, "d2": 0.0})
        self.assertEqual(out["10"], {"d0": 0.0, "d1": 0.4, "d2": 0.0})
        out = SCRIPT.apply_cap({"5": {"d0": 0.1}, "10": {"d0": 0.4}}, ["d0"], [True])
        self.assertLessEqual(out["10"]["d0"], out["5"]["d0"])


if __name__ == "__main__":
    unittest.main()
