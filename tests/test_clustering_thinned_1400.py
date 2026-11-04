"""Clustering at leads 2 to 5 read on thinned days, and the size of the unthinned test (#1400): `scripts/clustering_thinned_1400.py`.

The tests fix the arithmetic on hand cases: which decision days a phase keeps, where a thinned series breaks into runs (a gap in the
scored days, a regime change), that the asymptotic p of a phase series is `coverage_tests.christoffersen_independence`, that the
overlap of consecutive h-step forecasts makes a calibrated forecaster's hits dependent day to day and that thinning removes it, that the
script's constants are the declaration's (`metadata/clustering_thinned_1400.json`), and that the simulation is deterministic and
calibrated by construction.

No leakage, availability or staleness guard is added: the script reads walk files written by `scripts/candidate_calibration_1363.py walk`
and reuses that script's `refuse_beyond` (tested in `tests/test_candidate_calibration_1363.py`, which carries its recorded mutation).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("clustering_thinned_1400_script", REPO / "scripts" / "clustering_thinned_1400.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import coverage_tests  # noqa: E402

DECLARATION = json.loads((REPO / "metadata" / "clustering_thinned_1400.json").read_text(encoding="utf-8"))


class PhaseTests(unittest.TestCase):
    def test_a_phase_keeps_every_hth_index_from_its_offset(self):
        self.assertEqual(script.phase_indices(10, 3, 0), [0, 3, 6, 9])
        self.assertEqual(script.phase_indices(10, 3, 1), [1, 4, 7])
        self.assertEqual(script.phase_indices(10, 3, 2), [2, 5, 8])

    def test_phases_partition_the_sequence(self):
        for h in (2, 3, 4, 5):
            kept = sorted(i for r in range(h) for i in script.phase_indices(23, h, r))
            self.assertEqual(kept, list(range(23)))

    def test_adjacent_kept_values_are_h_panel_days_apart(self):
        # positions 0..5 then a gap of one missing day: 7.. continues; at h = 2 the kept 4 and 7 are not adjacent
        self.assertEqual(script.thinned_runs([0, 2, 4, 7, 9], 2), [3, 2])
        self.assertEqual(script.thinned_runs([0, 3, 6, 9], 3), [4])

    def test_a_break_label_also_starts_a_run(self):
        self.assertEqual(script.thinned_runs([0, 2, 4, 6], 2, ["a", "a", "b", "b"]), [2, 2])

    def test_phase_series_returns_values_and_runs(self):
        positions = list(range(12))
        values = [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1]
        got, runs = script.phase_series(positions, values, 3, 1)
        self.assertEqual(got, [1, 1, 0, 0])  # indices 1, 4, 7, 10
        self.assertEqual(runs, [4])


class IndependenceTests(unittest.TestCase):
    def test_asymptotic_p_is_the_protocol_test_on_one_run(self):
        seq = [0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0]
        expected = coverage_tests.christoffersen_independence(seq).p_value
        self.assertAlmostEqual(script.asymptotic_p(seq, [len(seq)]), expected, places=12)

    def test_no_transition_is_counted_across_a_run_boundary(self):
        seq = [1, 0, 0, 1]
        joined = script.asymptotic_p(seq, [4])
        cut = script.asymptotic_p(seq, [2, 2])
        self.assertNotEqual(joined, cut)

    def test_overlap_pairs_are_dependent_unthinned_and_independent_thinned(self):
        # at h = 2 the outcomes of consecutive forecasts share an innovation: misses come in adjacent pairs.
        n = 400
        seq = [0] * n
        for start in range(10, n - 10, 40):
            seq[start] = seq[start + 1] = 1
        unthinned = script.asymptotic_p(seq, [n])
        self.assertLess(unthinned, 0.01)
        for r in (0, 1):
            values, runs = script.phase_series(list(range(n)), seq, 2, r)
            self.assertGreater(script.asymptotic_p(values, runs), 0.1)


class DeclarationTests(unittest.TestCase):
    def test_constants_are_the_declarations(self):
        sim = DECLARATION["simulation"]
        self.assertEqual(script.PATHS, sim["paths"])
        self.assertEqual(script.SIM_SEED, sim["seed"])
        self.assertEqual(script.SIM_PERMUTATIONS, 1999)
        self.assertEqual(script.SEED, DECLARATION["seed"])
        self.assertEqual(script.PERMUTATIONS, 10_000)
        self.assertEqual(script.SAMPLE_SIZES, (1855, 165))
        self.assertEqual(DECLARATION["issue"], 1400)

    def test_family_sizes_are_the_declared_ones(self):
        self.assertEqual(script.PHASES_2_TO_5, 14)
        self.assertEqual(len(script.SEQUENCES) * script.PHASES_2_TO_5, 112)
        self.assertEqual(script.THINNED_FAMILY_SIM, 4 + 4 * 14)
        self.assertEqual(script.UNTHINNED_FAMILY_SIM, 4 * 5)
        for needle in ("112 p-values", "60 p-values", "20 sequences"):
            self.assertIn(needle, json.dumps(DECLARATION))


class SimulationTests(unittest.TestCase):
    def test_a_path_is_deterministic(self):
        a = script.simulate_path(120, 7, 99)
        b = script.simulate_path(120, 7, 99)
        self.assertEqual(a, b)
        self.assertNotEqual(a, script.simulate_path(120, 8, 99))

    def test_the_ideal_forecaster_is_calibrated_at_every_lead(self):
        for h in script.LEADS:
            hits = script.miss_sequences(3000, 11)[h]["upper"]
            self.assertAlmostEqual(sum(hits) / len(hits), 0.05, delta=0.015)
            hits = script.miss_sequences(3000, 11)[h]["band50"]
            self.assertAlmostEqual(sum(hits) / len(hits), 0.50, delta=0.04)

    def test_overlap_makes_the_unthinned_statistic_larger_than_the_thinned_one(self):
        # the lag-1 dependence of a calibrated h-step forecaster's hits: mean statistic over paths, lead 5
        unthinned, thinned = [], []
        for seed in range(21, 41):
            seq = script.miss_sequences(1500, seed)[5]["band50"]
            n = len(seq)
            unthinned.append(script.lr_statistic(seq, [n]))
            for r in range(5):
                values, runs = script.phase_series(list(range(n)), seq, 5, r)
                thinned.append(script.lr_statistic(values, runs))
        self.assertGreater(sum(unthinned) / len(unthinned), 3 * sum(thinned) / len(thinned))

    def test_rates_are_shares_of_paths(self):
        paths = [script.simulate_path(80, 100 + i, 49) for i in range(4)]
        rates = script.size_rates(paths)
        for h in script.LEADS:
            for ev in script.SIM_EVENTS:
                for key in ("unthinned", "phase0", "any_phase", "mean_phase"):
                    value = rates["by_lead_event"][str(h)][ev][key]
                    self.assertTrue(0.0 <= value <= 1.0)
        for key in ("unthinned_all", "thinned_all", "unthinned_2_to_5", "thinned_2_to_5"):
            self.assertTrue(0.0 <= rates["family"][key] <= 1.0)
        self.assertEqual(rates["paths"], 4)


if __name__ == "__main__":
    unittest.main()
