"""The fixed robustness set on (s3c-ann-net) (#1364): `scripts/h5_robustness_1364.py`.

The tests fix the arithmetic on hand cases: the reading of a paired test, what counts as a changed reading, the series built from cell
scores, the window setting that restores itself (also on an error), that a longer window reads more training pairs and never a row after
the anchor, and that the declaration names the candidate as run (the premise the declaration corrects: a trailing two-year window refit
every 21 decision days). This study adds no leakage or availability guard of its own: every arm is the candidate's own walk under the
walk's guards, so no mutation is recorded.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("h5_robustness_1364_script", REPO / "scripts" / "h5_robustness_1364.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import spread_mean_reversion as smr  # noqa: E402

DECLARED = json.loads((REPO / "metadata" / "h5_robustness_1364.json").read_text(encoding="utf-8"))


def row(lo, hi, **extra):
    return dict({"difference_interval": [lo, hi]}, **extra)


class ReadingTests(unittest.TestCase):
    def test_an_interval_above_zero_is_a_gain_below_a_loss_and_across_zero_undecided(self):
        self.assertEqual(script.reading(row(0.1, 0.5)), "gain")
        self.assertEqual(script.reading(row(-0.5, -0.1)), "loss")
        self.assertEqual(script.reading(row(-0.1, 0.5)), "undecided")
        self.assertEqual(script.reading(row(0.0, 0.5)), "undecided")  # an end at zero does not exclude it

    def test_identical_and_untestable_pairs_are_named_not_read(self):
        self.assertEqual(script.reading({"identical": True}), "identical")
        self.assertEqual(script.reading({"undefined": "no variance"}), "undefined")
        self.assertEqual(script.reading(None), "undefined")

    def test_a_change_is_a_different_category_and_an_untestable_pair_is_not_a_change(self):
        self.assertTrue(script.changed("gain", "undecided"))
        self.assertTrue(script.changed("undecided", "loss"))
        self.assertFalse(script.changed("gain", "gain"))
        self.assertFalse(script.changed("gain", "undefined"))
        self.assertFalse(script.changed("undefined", "loss"))


class SeriesTests(unittest.TestCase):
    def window(self):
        d0 = date(2024, 1, 2)
        cells = [(d0, 1, d0 + timedelta(1)), (d0, 2, d0 + timedelta(2)), (d0 + timedelta(1), 1, d0 + timedelta(2))]
        return SimpleNamespace(cells=cells), d0

    def test_decision_target_and_lead_series(self):
        w, d0 = self.window()
        scores = [1.0, 3.0, 5.0]
        self.assertEqual(script.series_for(w, scores, "decision"), {d0: 2.0, d0 + timedelta(1): 5.0})
        self.assertEqual(script.series_for(w, scores, "target"), {d0 + timedelta(1): 1.0, d0 + timedelta(2): 4.0})
        self.assertEqual(script.series_for(w, scores, "lead1"), {d0: 1.0, d0 + timedelta(1): 5.0})


class WindowTests(unittest.TestCase):
    def test_the_setting_is_restored_also_after_an_error(self):
        before = smr.TRAIN_YEARS
        with script.training_window(7):
            self.assertEqual(smr.TRAIN_YEARS, 7)
        self.assertEqual(smr.TRAIN_YEARS, before)
        with self.assertRaises(RuntimeError):
            with script.training_window(3):
                raise RuntimeError("x")
        self.assertEqual(smr.TRAIN_YEARS, before)

    def test_a_window_below_one_year_is_refused(self):
        with self.assertRaises(ValueError):
            with script.training_window(0):
                pass

    def test_a_longer_window_reads_more_pairs_and_none_after_the_anchor(self):
        days = []
        d = date(2018, 4, 3)
        while len(days) < 1400:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(1)
        panel = [SimpleNamespace(date=x) for x in days]
        levels = [0.0] * len(panel)
        index = len(panel) - 1
        anchor = index - 1
        counts = {}
        for years in (1, 2, 3, 100):
            with script.training_window(years):
                rows = smr.training_rows(panel, index, anchor, lag=index - anchor, levels=levels)
            counts[years] = len(rows[1])
            self.assertTrue(all(target <= anchor and origin < target for origin, target in rows[1]))
        self.assertLess(counts[1], counts[2])
        self.assertLess(counts[2], counts[3])
        self.assertLess(counts[3], counts[100])
        with script.training_window(100):
            rows = smr.training_rows(panel, index, anchor, lag=index - anchor, levels=levels)
        self.assertEqual(min(target for _o, target in rows[1]), 1 + 1)  # k = h + lag = 2: the first target with an origin


class DeclarationTests(unittest.TestCase):
    def test_the_reference_is_the_candidate_as_run(self):
        plan = script.arm_plan(DECLARED)
        self.assertEqual(plan[0], ("as_run", smr.TRAIN_YEARS, smr.REFIT_EVERY))
        self.assertEqual((smr.TRAIN_YEARS, smr.REFIT_EVERY), (2, 21))

    def test_the_set_is_the_declared_six_and_nothing_else(self):
        plan = {name: (years, every) for name, years, every in script.arm_plan(DECLARED)}
        self.assertEqual(plan, {"as_run": (2, 21), "expanding": (100, 21), "rolling_1y": (1, 21), "rolling_3y": (3, 21),
                                "refit_5": (2, 5), "refit_63": (2, 63)})

    def test_a_declaration_whose_reference_refits_at_another_cadence_is_refused(self):
        bad = json.loads(json.dumps(DECLARED))
        bad["arms"]["as_run"]["refit_every"] = 10
        with self.assertRaises(ValueError):
            script.arm_plan(bad)

    def test_a_declaration_without_a_reference_is_refused(self):
        bad = json.loads(json.dumps(DECLARED))
        del bad["arms"]["as_run"]
        with self.assertRaises(ValueError):
            script.arm_plan(bad)


class FlagTests(unittest.TestCase):
    def result(self, ref_reading, arm_reading, own):
        def vs(kind):
            return {"gain": row(0.1, 0.4), "undecided": row(-0.1, 0.4), "loss": row(-0.4, -0.1)}[kind]
        entry = {"days": 50, "tested": True}
        for metric in script.METRICS:
            entry[metric] = {"means": {}, "vs": {
                "as_run": {b: vs(ref_reading) for b in script.REFERENCES},
                "refit_5": dict({b: vs(arm_reading) for b in script.REFERENCES}, as_run=vs(own)),
            }}
        return {"groups": {"pooled": {"all decision days": entry}}}

    def test_no_change_when_readings_agree_and_the_arm_is_undecided_against_the_reference(self):
        f = script.flags(self.result("gain", "gain", "undecided"))
        self.assertEqual(f["changed"], [])
        self.assertEqual(f["examined"], 2 * 4)

    def test_a_different_category_against_a_benchmark_is_listed_for_each_metric(self):
        f = script.flags(self.result("gain", "undecided", "undecided"))
        self.assertEqual(len(f["changed"]), 3 * 2)
        self.assertEqual({x["arm"] for x in f["changed"]}, {"refit_5"})

    def test_an_arm_that_beats_the_reference_is_listed_even_if_the_benchmark_readings_agree(self):
        f = script.flags(self.result("gain", "gain", "gain"))
        self.assertEqual([x["against"] for x in f["changed"]], ["as_run", "as_run"])

    def test_a_group_below_the_minimum_is_not_examined(self):
        r = {"groups": {"regime": {"2020": {"days": 5}}}}
        self.assertEqual(script.flags(r), {"examined": 0, "unchanged": 0, "changed": []})


if __name__ == "__main__":
    unittest.main()
