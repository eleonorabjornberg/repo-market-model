"""Pressure model v1.1 (#117): the candidates and the pre-registered win rule.

Eleonora's rulings of 3 October 2026 on #117 fix the rule before any scoring:
one primary candidate (all five inputs together), four primary cells (+5 bp,
horizon 1, all scored days and onset days, against pressure model v1 and the
persistence-logistic), one-sided paired stationary-bootstrap p-values, and Holm
at a 10% family-wise level over those four cells only. These tests pin it.
"""

from __future__ import annotations

import unittest

from repo_model import contract, onset, pressure_v1_1 as v11
from repo_model.data import DailyObservation


def _cells(improve=(), worse=(), p=0.5):
    """Results for the four primary cells: `improve`/`worse` get p = 0.001."""

    out = {}
    for key in v11.primary_cells():
        out[key] = {
            "p_improve": 0.001 if key in improve else p,
            "p_worse": 0.001 if key in worse else p,
        }
    return out


class DeclarationTests(unittest.TestCase):
    def test_the_five_inputs_and_their_columns(self):
        self.assertEqual(
            [(c.name, c.issue, c.columns) for c in v11.CANDIDATES],
            [
                ("announced_iorb", "#38", ("iorb_announced_change_bps", "iorb_days_to_announced_change")),
                ("rrp_conditional", "#88", ("on_rrp_depleted", "reserves_when_depleted")),
                ("settlement_onset", "#97", ("settlement_day", "settlement_day_when_depleted")),
                ("effr_minus_iorb", "#98", ("effr_minus_iorb_bp",)),
                ("scarcity_state", "#115", ("reserve_scarcity_state",)),
            ],
        )

    def test_every_column_is_a_declared_feature(self):
        declared = (
            set(contract.FEATURE_FIELDS)
            | set(contract.DERIVED_FEATURES)
            | set(contract.COMPOSED_FEATURES)
            | {"reserve_scarcity_state"}
        )
        for run in v11.RUNS:
            for column in run.columns:
                self.assertIn(column, declared, run.name)

    def test_one_primary_candidate_all_five_together(self):
        self.assertEqual(v11.PRIMARY, "all_together")
        (primary,) = [run for run in v11.RUNS if run.name == v11.PRIMARY]
        self.assertTrue(primary.primary)
        self.assertEqual(
            primary.columns, tuple(c for candidate in v11.CANDIDATES for c in candidate.columns)
        )
        self.assertEqual([run.name for run in v11.RUNS if run.primary], [v11.PRIMARY])

    def test_the_single_inputs_and_on_rrp_are_exploratory(self):
        names = [run.name for run in v11.RUNS if not run.primary]
        self.assertEqual(
            names, [c.name for c in v11.CANDIDATES] + ["on_rrp_plain"]
        )

    def test_inputs_not_public_beyond_one_day_drop_at_longer_horizons(self):
        (primary,) = [run for run in v11.RUNS if run.primary]
        self.assertEqual(v11.columns_at_horizon(primary, 1), primary.columns)
        self.assertEqual(
            v11.columns_at_horizon(primary, 2),
            ("on_rrp_depleted", "reserves_when_depleted", "effr_minus_iorb_bp", "reserve_scarcity_state"),
        )
        (iorb,) = [run for run in v11.RUNS if run.name == "announced_iorb"]
        self.assertEqual(v11.columns_at_horizon(iorb, 3), ())


class PrimaryFamilyTests(unittest.TestCase):
    def test_four_primary_cells(self):
        self.assertEqual(v11.FAMILY_SIZE, 4)
        self.assertEqual(
            v11.primary_cells(),
            (
                "all_together|brier|all_days|5|1|pressure_model_v1",
                "all_together|brier|all_days|5|1|persistence_logistic",
                "all_together|brier|onset_days|5|1|pressure_model_v1",
                "all_together|brier|onset_days|5|1|persistence_logistic",
            ),
        )
        self.assertEqual(len(v11.primary_cells()), v11.FAMILY_SIZE)

    def test_the_level_and_replications(self):
        self.assertEqual(v11.FAMILY_LEVEL, 0.10)
        # Holm's smallest threshold must be reachable: 1 / (B + 1) <= level / K.
        self.assertLessEqual(1 / (v11.P_VALUE_REPLICATIONS + 1), v11.FAMILY_LEVEL / v11.FAMILY_SIZE)

    def test_onset_days_are_139s(self):
        spreads = [0, 0, 0, 0, 0, 6, 7, 0, 0, 0, 0, 0, 6]
        rows = [
            DailyObservation(__import__("datetime").date(2025, 1, 1 + i), {"sofr": 4.0 + s / 100, "iorb": 4.0})
            for i, s in enumerate(spreads)
        ]
        self.assertEqual(v11.onset_positions(rows, [r.date for r in rows]), [5, 12])
        self.assertEqual(
            [i for i, flag in enumerate(onset.onset_flags(rows)) if flag], [5, 12]
        )


class HolmTests(unittest.TestCase):
    def test_step_down(self):
        rejected = v11.holm({"a": 0.01, "b": 0.03, "c": 0.04, "d": 0.2}, level=0.10)
        # thresholds 0.025, 0.0333, 0.05, 0.1: a, b, c rejected; d stops.
        self.assertEqual(rejected, {"a": True, "b": True, "c": True, "d": False})

    def test_stops_at_the_first_kept(self):
        rejected = v11.holm({"a": 0.03, "b": 0.031, "c": 0.032, "d": 0.033}, level=0.10)
        self.assertEqual(rejected, {"a": False, "b": False, "c": False, "d": False})


class ClassifyTests(unittest.TestCase):
    def test_one_surviving_improvement_and_no_deterioration_passes(self):
        cell = v11.primary_cells()[2]
        verdict = v11.classify(_cells(improve={cell}))
        self.assertTrue(verdict["passed"])
        self.assertEqual(verdict["improving_cells"], [cell])
        self.assertEqual(verdict["deteriorating_cells"], [])

    def test_nothing_surviving_fails(self):
        verdict = v11.classify(_cells(p=0.04))
        self.assertFalse(verdict["passed"])
        self.assertEqual(verdict["improving_cells"], [])

    def test_a_surviving_deterioration_fails_even_with_an_improvement(self):
        cells = v11.primary_cells()
        verdict = v11.classify(_cells(improve={cells[0]}, worse={cells[3]}))
        self.assertFalse(verdict["passed"])
        self.assertEqual(verdict["deteriorating_cells"], [cells[3]])

    def test_the_results_must_be_exactly_the_primary_cells(self):
        results = _cells()
        results["scarcity_state|brier|all_days|5|1|pressure_model_v1"] = {"p_improve": 0.0, "p_worse": 1.0}
        with self.assertRaises(ValueError):
            v11.classify(results)
        with self.assertRaises(ValueError):
            v11.classify({k: v for k, v in _cells().items() if k != v11.primary_cells()[0]})


class OnRrpRuleTests(unittest.TestCase):
    @staticmethod
    def _entry(lower, upper):
        return {"mean": (lower + upper) / 2, "interval": {"lower": lower, "upper": upper}}

    def test_met_on_crps_alone(self):
        ok = self._entry(0.001, 0.01)
        flat = self._entry(-0.01, 0.01)
        self.assertTrue(v11.on_rrp_rule(crps=ok, brier_5=flat, brier_10=flat)["met"])

    def test_met_on_a_brier(self):
        ok = self._entry(0.0001, 0.001)
        flat = self._entry(-0.01, 0.01)
        self.assertTrue(v11.on_rrp_rule(crps=flat, brier_5=flat, brier_10=ok)["met"])

    def test_not_met_when_one_is_significantly_worse(self):
        ok = self._entry(0.001, 0.01)
        worse = self._entry(-0.01, -0.001)
        self.assertFalse(v11.on_rrp_rule(crps=ok, brier_5=ok, brier_10=worse)["met"])

    def test_not_met_without_an_improvement(self):
        flat = self._entry(-0.01, 0.01)
        self.assertFalse(v11.on_rrp_rule(crps=flat, brier_5=flat, brier_10=flat)["met"])

    def test_the_form_is_the_best_on_pooled_crps(self):
        self.assertEqual(v11.ON_RRP_FORMS, {"plain": "on_rrp_plain", "conditional": "rrp_conditional"})
        self.assertEqual(
            v11.on_rrp_form({"on_rrp_plain": 0.002, "rrp_conditional": 0.008}), "rrp_conditional"
        )
        self.assertEqual(v11.on_rrp_form({"on_rrp_plain": 0.01, "rrp_conditional": 0.008}), "on_rrp_plain")


if __name__ == "__main__":
    unittest.main()
