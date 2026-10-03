"""Pressure model v1.1 (#117): the inputs, the primary family and the win rule, fixed before scoring."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from repo_model import contract, pressure_v1_1 as v11
from repo_model.pressure_v1_1 import (
    CANDIDATES,
    FAMILY_LEVEL,
    JOINT,
    ON_RRP_FORMS,
    PRIMARY_CELLS,
    candidate_columns,
    classify_primary,
    columns_at_horizon,
    on_rrp_rule,
    primary_key,
)

ROOT = Path(__file__).resolve().parents[1]


def _cell(mean=0.0, p_improve=0.5, p_worse=0.5):
    return {"mean": mean, "p_improve": p_improve, "p_worse": p_worse}


class InputDeclarationTests(unittest.TestCase):
    def test_the_five_inputs_are_the_directives_in_its_order(self):
        self.assertEqual(
            [c.name for c in CANDIDATES],
            ["announced_iorb", "conditional_scarcity", "depletion_settlement", "effr_iorb", "scarcity_state"],
        )
        self.assertEqual([c.directive for c in CANDIDATES], ["#38", "#88", "#97", "#98", "#115"])

    def test_every_column_is_declared_somewhere_the_as_of_rule_prices(self):
        known = (
            set(contract.FEATURE_FIELDS) | set(contract.DERIVED_FEATURES)
            | set(contract.COMPOSED_FEATURES) | {"reserve_scarcity_state", "on_rrp"}
        )
        for candidate in CANDIDATES:
            for column in candidate.columns:
                with self.subTest(column=column):
                    self.assertIn(column, known)

    def test_the_joint_candidate_is_every_input_together(self):
        self.assertEqual(
            candidate_columns(JOINT),
            tuple(c for candidate in CANDIDATES for c in candidate.columns),
        )

    def test_one_day_ahead_inputs_leave_at_longer_horizons(self):
        at_one = columns_at_horizon(candidate_columns(JOINT), 1)
        at_two = columns_at_horizon(candidate_columns(JOINT), 2)
        self.assertEqual(at_one, candidate_columns(JOINT))
        for column in ("iorb_announced_change_bps", "iorb_days_to_announced_change",
                       "settlement_day", "settlement_day_when_depleted"):
            self.assertIn(column, at_one)
            self.assertNotIn(column, at_two)
        self.assertIn("effr_minus_iorb_bp", at_two)

    def test_no_input_is_on_in_the_published_declaration(self):
        published = set(contract.FEATURE_FIELDS)
        self.assertEqual(contract.FEATURE_FIELDS["on_rrp"], (("fred_macro_latest_vintage", "RRPONTSYD"),))
        self.assertNotIn("reserve_scarcity_state", published)
        self.assertNotIn("bank_total_assets", published)

    def test_the_on_rrp_forms_are_plain_and_the_conditional_input(self):
        self.assertEqual(dict(ON_RRP_FORMS), {
            "on_rrp_plain": ("on_rrp",),
            "conditional_scarcity": candidate_columns("conditional_scarcity"),
        })


class PrimaryFamilyTests(unittest.TestCase):
    def test_four_cells_for_the_joint_candidate_only(self):
        self.assertEqual(len(PRIMARY_CELLS), 4)
        self.assertEqual(
            {primary_key(*cell) for cell in PRIMARY_CELLS},
            {
                "joint|brier|all_days|5|1|pressure_model_v1",
                "joint|brier|all_days|5|1|persistence_logistic",
                "joint|brier|onset_days|5|1|pressure_model_v1",
                "joint|brier|onset_days|5|1|persistence_logistic",
            },
        )
        self.assertEqual(FAMILY_LEVEL, 0.10)

    def _results(self, **overrides):
        out = {primary_key(*cell): _cell() for cell in PRIMARY_CELLS}
        out.update(overrides)
        return out

    def test_a_cell_surviving_holm_is_a_pass(self):
        key = primary_key(*PRIMARY_CELLS[0])
        verdict = classify_primary(self._results(**{key: _cell(0.01, 0.001, 0.999)}))
        self.assertTrue(verdict["passed"])
        self.assertEqual(verdict["improvements"], [key])

    def test_holm_divides_the_level_by_four(self):
        key = primary_key(*PRIMARY_CELLS[0])
        # 0.03 < 0.10 but > 0.10 / 4: it does not survive.
        verdict = classify_primary(self._results(**{key: _cell(0.01, 0.03, 0.97)}))
        self.assertFalse(verdict["passed"])

    def test_a_surviving_deterioration_blocks_a_pass(self):
        good, bad = (primary_key(*cell) for cell in PRIMARY_CELLS[:2])
        verdict = classify_primary(
            self._results(**{good: _cell(0.01, 0.001, 0.999), bad: _cell(-0.01, 0.999, 0.001)})
        )
        self.assertFalse(verdict["passed"])
        self.assertEqual(verdict["deteriorations"], [bad])

    def test_a_missing_cell_is_refused(self):
        results = self._results()
        results.pop(primary_key(*PRIMARY_CELLS[3]))
        with self.assertRaises(ValueError):
            classify_primary(results)

    def test_an_extra_cell_is_refused(self):
        with self.assertRaises(ValueError):
            classify_primary(self._results(**{"joint|brier|all_days|10|1|pressure_model_v1": _cell()}))


class OnRrpRuleTests(unittest.TestCase):
    """Eleonora's ruling on #117, 2 October 2026."""

    @staticmethod
    def _entry(lower, upper, mean=None):
        return {"mean": (lower + upper) / 2 if mean is None else mean, "interval": {"lower": lower, "upper": upper}}

    def _forms(self, plain_crps=1.60, conditional_crps=1.62, **plain):
        flat = self._entry(-0.01, 0.01)
        return {
            "on_rrp_plain": {
                "candidate_crps_bps": plain_crps,
                "crps": plain.get("crps", flat),
                "brier_5": plain.get("brier_5", flat),
                "brier_10": plain.get("brier_10", flat),
            },
            "conditional_scarcity": {
                "candidate_crps_bps": conditional_crps,
                "crps": self._entry(0.01, 0.05),
                "brier_5": flat,
                "brier_10": flat,
            },
        }

    def test_the_form_is_the_lower_pooled_crps_not_the_better_result(self):
        verdict = on_rrp_rule(self._forms())
        self.assertEqual(verdict["form"], "on_rrp_plain")
        self.assertFalse(verdict["met"])

    def test_crps_excluding_zero_meets_it(self):
        verdict = on_rrp_rule(self._forms(crps=self._entry(0.001, 0.02)))
        self.assertTrue(verdict["met"])

    def test_a_brier_excluding_zero_meets_it(self):
        self.assertTrue(on_rrp_rule(self._forms(brier_10=self._entry(0.0001, 0.001)))["met"])

    def test_a_significant_deterioration_fails_it(self):
        verdict = on_rrp_rule(
            self._forms(crps=self._entry(0.001, 0.02), brier_5=self._entry(-0.002, -0.0001))
        )
        self.assertFalse(verdict["met"])

    def test_the_rule_is_committed_in_the_module_text(self):
        source = (ROOT / "src" / "repo_model" / "pressure_v1_1.py").read_text(encoding="utf-8")
        self.assertRegex(source, re.compile(r"Holm", re.M))
        self.assertIn("2 October 2026", source)
        self.assertIn("3 October 2026", source)
        self.assertEqual(v11.P_VALUE_REPLICATIONS, 20000)


if __name__ == "__main__":
    unittest.main()
