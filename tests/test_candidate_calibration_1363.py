"""The candidate's calibration by period and day type, and its clustering of misses (#1363): `scripts/candidate_calibration_1363.py`.

The tests fix the arithmetic on hand cases: the hit definitions with ties, the band flags, the readings, Christoffersen's statistic
from transition counts (equal to `coverage_tests` on one run, and cut at a run boundary), the permutation p-value, the stationary-bootstrap
interval, the randomised PIT of #970, and the refusal of a day after the window's end.

Recorded mutation (the guard this script adds):

* `refuse_beyond`, the test `if day > last:` replaced by `if False:`: `test_a_day_after_the_window_end_is_refused` fails with
  `AssertionError` (`LookAheadError not raised`); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("candidate_calibration_1363_script", REPO / "scripts" / "candidate_calibration_1363.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import coverage_tests, scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

GRID = sp.GRID


def law(offset=0.0):
    """A strictly increasing law: level j has quantile j + offset."""

    return [j + offset for j in range(len(GRID))]


class HitTests(unittest.TestCase):
    def test_strict_and_at_or_below_differ_on_a_tie(self):
        q = law()
        strict, at = script.level_shares(q, 5.0)  # y == q[5]
        self.assertEqual(strict[5], 0)
        self.assertEqual(at[5], 1)
        self.assertEqual((strict[4], at[4]), (0, 0))  # q[4] < y
        self.assertEqual((strict[6], at[6]), (1, 1))  # q[6] > y

    def test_band_closed_and_open_differ_on_the_edge(self):
        q = law()
        lo, hi = GRID.index(0.05), GRID.index(0.95)
        edge = script.band_hits(q, q[lo])
        self.assertEqual((edge["band90_closed"], edge["band90_open"]), (1, 0))
        inside = script.band_hits(q, 10.5)
        self.assertEqual((inside["band90_closed"], inside["band90_open"]), (1, 1))
        self.assertEqual(script.band_hits(q, q[hi] + 1)["band90_closed"], 0)
        self.assertEqual(script.band_hits(q, -1.0)["band50_closed"], 0)

    def test_events_strict_and_weak(self):
        q = law()
        q95 = q[GRID.index(0.95)]
        e = script.event_hits(q, q95)
        self.assertEqual((e["upper/strict"], e["upper/weak"]), (0, 1))
        self.assertEqual((e["band90/strict"], e["band90/weak"]), (0, 1))
        e = script.event_hits(q, q95 + 1)
        self.assertEqual((e["upper/strict"], e["band90/strict"], e["lower/strict"]), (1, 1, 0))


class ReadingTests(unittest.TestCase):
    def test_band_reading(self):
        self.assertEqual(script.read_band([0.92, 0.95], 0.90), "over-covers")
        self.assertEqual(script.read_band([0.80, 0.88], 0.90), "under-covers")
        self.assertEqual(script.read_band([0.85, 0.93], 0.90), "consistent")
        self.assertEqual(script.read_band(None, 0.90), "not tested")

    def test_level_reading_is_tie_aware(self):
        self.assertEqual(script.read_level([0.08, 0.10], [0.09, 0.11], 0.05), "quantile too high")
        self.assertEqual(script.read_level([0.00, 0.02], [0.01, 0.03], 0.05), "quantile too low")
        self.assertEqual(script.read_level([0.03, 0.06], [0.04, 0.07], 0.05), "consistent")

    def test_size(self):
        self.assertAlmostEqual(script.size_of_level(0.08, 0.09, 0.05), 0.03)
        self.assertAlmostEqual(script.size_of_level(0.01, 0.02, 0.05), -0.03)
        self.assertEqual(script.size_of_level(0.04, 0.06, 0.05), 0.0)


class IndependenceTests(unittest.TestCase):
    def test_statistic_from_counts_equals_the_module_on_one_run(self):
        rng = random.Random(3)
        seq = [int(rng.random() < 0.2) for _ in range(300)]
        runs = [len(seq)]
        got = script.lr_independence(*script.transition_counts(seq, runs))
        self.assertAlmostEqual(got, coverage_tests.christoffersen_independence(seq).statistic, places=9)

    def test_a_run_boundary_drops_the_transition(self):
        seq = [1, 1, 0, 0, 1, 1]
        self.assertEqual(script.transition_counts(seq, [6]), (1, 1, 1, 2))
        n00, n01, n10, n11 = script.transition_counts(seq, [3, 3])
        self.assertEqual(n00 + n01 + n10 + n11, 4)

    def test_runs_break_on_gaps_and_labels(self):
        self.assertEqual(script.runs_of([1, 2, 3, 5, 6]), [3, 2])
        self.assertEqual(script.runs_of([1, 2, 3, 4], ["a", "a", "b", "b"]), [2, 2])

    def test_clustered_misses_are_found_and_independent_ones_are_not(self):
        clustered = ([1] * 15 + [0] * 85) * 4
        rng = random.Random(11)
        scattered = [int(rng.random() < 0.15) for _ in range(400)]
        c = script.sequence_report(clustered, [400], permutations=2000)
        s = script.sequence_report(scattered, [400], permutations=2000)
        self.assertLess(c["p_permutation"], 0.01)
        self.assertGreater(s["p_permutation"], 0.05)
        self.assertEqual(c["longest_run"], 15)
        self.assertGreater(c["p_miss_after_miss"], c["p_miss_after_hit"])

    def test_the_permutation_p_is_reproducible_and_one_without_misses(self):
        seq = [0, 1, 1, 0, 0, 1, 0, 0, 0, 1] * 10
        a = script.permutation_p(seq, [100], permutations=500, seed=5)
        b = script.permutation_p(seq, [100], permutations=500, seed=5)
        self.assertEqual(a, b)
        self.assertEqual(script.permutation_p([0] * 50, [50], permutations=50), 1.0)

    def test_the_permutation_statistic_matches_a_direct_count(self):
        # the sampled counts equal transition_counts on the placed sequence
        seq = [0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0]
        runs = [7, 5]
        n = len(seq)
        ok = [False] * n
        start = 0
        for length in runs:
            for p in range(start, start + length - 1):
                ok[p] = True
            start += length
        chosen = [i for i, v in enumerate(seq) if v]
        members = set(chosen)
        prev1 = sum(1 for p in chosen if ok[p])
        today1 = sum(1 for p in chosen if p and ok[p - 1])
        n11 = sum(1 for p in chosen if ok[p] and p + 1 in members)
        n10, n01 = prev1 - n11, today1 - n11
        n00 = sum(ok) - n11 - n10 - n01
        self.assertEqual((n00, n01, n10, n11), script.transition_counts(seq, runs))


class BootstrapAndPitTests(unittest.TestCase):
    def test_the_interval_contains_the_mean_and_is_reproducible(self):
        rng = random.Random(2)
        x = [float(rng.random() < 0.3) for _ in range(200)]
        a = script.series_intervals({"x": x}, reps=300, seed=7)
        b = script.series_intervals({"x": x}, reps=300, seed=7)
        self.assertEqual(a, b)
        lo, hi = a["x"]
        self.assertLessEqual(lo, sum(x) / len(x))
        self.assertGreaterEqual(hi, sum(x) / len(x))

    def test_the_randomised_pit_of_a_perfect_continuous_forecast_is_uniform(self):
        # y ~ N(0, 1) against its own quantiles: the bracket of a cell holds it with the bracket's probability
        from statistics import NormalDist

        q = [NormalDist().inv_cdf(level) for level in GRID]
        rng = random.Random(4)
        cells = [(q, rng.gauss(0.0, 1.0)) for _ in range(8000)]
        summary = script.pit_summary(script.brackets(cells))
        self.assertAlmostEqual(summary["at_or_below_0.10"], 0.10, delta=0.02)
        self.assertAlmostEqual(summary["at_or_above_0.90"], 0.10, delta=0.02)
        for got, want in zip(summary["bins"], summary["expected"]):
            self.assertAlmostEqual(got, want, delta=0.025)

    def test_the_pit_equals_970s_randomised_pit(self):
        m = script._pit_module()
        q = [0.0] * 5 + [1.0] * 13 + [2.0] * 5
        b = script.brackets([(q, 1.0)])
        self.assertEqual(script.pit_values(b, 9)[0], m.randomised_pit(q, 1.0, random.Random(9)))


class GuardTests(unittest.TestCase):
    def test_a_day_after_the_window_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_beyond([date(2025, 12, 31), date(2026, 1, 2)], date(2025, 12, 31))

    def test_a_day_of_the_blind_tier_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_beyond([date(2026, 9, 4)], date(2026, 9, 3))

    def test_the_declared_days_pass(self):
        script.refuse_beyond([date(2025, 12, 31)], date(2025, 12, 31))


def synthetic_doc(days=80, seed=1):
    """A walk file of `days` decision days with four models of a made-up law, for the pipeline."""

    rng = random.Random(seed)
    calendar = [date(2019, 1, 1) + timedelta(days=i) for i in range(days + 10)]
    cells, outcome, targets, regimes, models = [], {}, {}, {}, {m: [] for m in script.MODELS}
    for i in range(days):
        d = calendar[i]
        regimes[d.isoformat()] = "2018-19"
        for h in script.LEADS:
            t = calendar[i + h]
            cells.append([d.isoformat(), h, t.isoformat()])
            y = float(round(rng.gauss(0, 1) * 2))
            outcome[t.isoformat()] = y
            targets.setdefault(t.isoformat(), {"regime": "2018-19", "types": ["ordinary"] if t.day % 5 else ["month_end"],
                                              "pressure": "ordinary"})
            for m in script.MODELS:
                models[m].append([(-2.0 + 4.0 * j / (len(GRID) - 1)) * (1.0 if m == script.CANDIDATE else 1.3) for j in range(len(GRID))])
    return {"window": "development", "calendar": [c.isoformat() for c in calendar], "cells": cells, "outcome": outcome, "targets": targets,
            "regime_of_day": regimes, "models": models, "panel_sha256": "x"}


class PipelineTests(unittest.TestCase):
    def test_the_window_report_has_the_declared_shape(self):
        window = script.Window(synthetic_doc())
        rep = script.window_report(window, reps=50, permutations=50)
        self.assertEqual(rep["cells"], 80 * 5)
        cand = rep["models"][script.CANDIDATE]
        pooled = cand["groups"][0]
        self.assertEqual((pooled["split"], pooled["cells"]), ("pooled", 400))
        self.assertTrue(pooled["tested"])
        self.assertEqual([g["label"] for g in cand["groups"] if g["split"] == "lead"], [f"h={h}" for h in script.LEADS])
        small = [g for g in cand["groups"] if g["split"] == "target_day_type" and g["label"] == "month_end"][0]
        self.assertEqual(small["tested"], small["target_days"] >= 20)
        self.assertEqual(set(cand["clustering"]["all"]), {"1", "2", "3", "4", "5"})
        self.assertEqual(set(cand["clustering"]["all"]["1"]), set(script.SEQUENCES))
        self.assertEqual(len(cand["all_levels"]), len(GRID))
        self.assertTrue(cand["protocol"])

    def test_the_page_renders_from_the_record(self):
        window = script.Window(synthetic_doc())
        rep = script.window_report(window, reps=50, permutations=50)
        record = {"panel_sha256": "x", "b4": "B4 is not compared", "block": 10.0, "reps": 50, "seed": 1363, "windows": {"development": rep}}
        text = script.render(record)
        self.assertIn("Do the misses cluster in time?", text)
        self.assertIn("development, not a verdict".split(",")[0], text)

    def test_the_declaration_is_there_and_names_the_issue(self):
        d = json.loads((REPO / "metadata" / "candidate_calibration_1363.json").read_text(encoding="utf-8"))
        self.assertEqual(d["issue"], 1363)
        self.assertEqual(d["seed"], script.SEED)


if __name__ == "__main__":
    unittest.main()
