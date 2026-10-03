"""The scarcity-conditioned calendar (#128): forms, state mappings and the win rule, fixed before scoring."""

from __future__ import annotations

import unittest
from pathlib import Path

from repo_model import contract, scarcity, scarcity_calendar as sc
from repo_model.scarcity_calendar import (
    CANDIDATES,
    CONTROL,
    FAMILY_LEVEL,
    PRIMARY_CANDIDATES,
    PRIMARY_CELLS,
    SCARCITY_MEASURES,
    STATE_FORMS,
    classify_primary,
    features_at_horizon,
    primary_key,
)

ROOT = Path(__file__).resolve().parents[1]


def _cell(p_improve=0.5, p_worse=0.5):
    return {"p_improve": p_improve, "p_worse": p_worse}


class StateFormTests(unittest.TestCase):
    """Eleonora's scope addition of 2 October 2026 on #128: two declared state forms."""

    def test_form_a_is_the_four_level_state_as_built(self):
        self.assertEqual(dict(STATE_FORMS["four_level"]), {0.0: 0.0, 1.0: 1.0, 2.0: 2.0, 3.0: 3.0})
        self.assertEqual(set(STATE_FORMS["four_level"]), {float(level) for level in scarcity.STATE_LABELS})

    def test_form_b_is_states_zero_one_against_two_three(self):
        self.assertEqual(dict(STATE_FORMS["two_level"]), {0.0: 0.0, 1.0: 0.0, 2.0: 1.0, 3.0: 1.0})

    def test_form_b_is_recorded_as_added_after_seeing_157(self):
        source = (ROOT / "src" / "repo_model" / "scarcity_calendar.py").read_text(encoding="utf-8")
        self.assertIn("(b) was added after\n  seeing #157", source)
        self.assertIn("not a blind specification", source)

    def test_the_cut_points_are_115s_as_merged(self):
        self.assertEqual(scarcity.SATIATION_BAND, (0.12, 0.13))
        self.assertEqual(scarcity.ON_RRP_BUFFER_BN, 100.0)
        self.assertEqual(sc.STATE_COLUMN, scarcity.RESERVE_SCARCITY_STATE)


class CandidateTests(unittest.TestCase):
    def test_eight_candidates_two_forms_two_states_with_and_without_measures(self):
        self.assertEqual(len(CANDIDATES), 8)
        self.assertEqual(
            {(c.form, c.state, c.measures) for c in CANDIDATES},
            {(f, s, m) for f in ("logistic", "gbm") for s in ("four_level", "two_level") for m in (False, True)},
        )

    def test_the_measures_are_88s_and_98s_inputs(self):
        self.assertEqual(SCARCITY_MEASURES, ("on_rrp_depleted", "reserves_when_depleted", "effr_minus_iorb_bp"))
        for name in SCARCITY_MEASURES:
            self.assertIn(name, set(contract.COMPOSED_FEATURES) | set(contract.DERIVED_FEATURES))

    def test_the_settlement_leaves_at_longer_horizons(self):
        at_one = features_at_horizon("logistic_four_level", 1)
        at_two = features_at_horizon("logistic_four_level", 2)
        self.assertEqual(
            at_one,
            ("spread_bps", "reserve_scarcity_state", "days_to_month_end", "quarter_end", "tax_date",
             "treasury_settlement"),
        )
        self.assertEqual(at_two, at_one[:-1])
        self.assertEqual(features_at_horizon("gbm_two_level_measures", 3), at_two + SCARCITY_MEASURES)

    def test_an_unknown_candidate_or_horizon_is_refused(self):
        with self.assertRaises(ValueError):
            features_at_horizon("logistic_three_level", 1)
        with self.assertRaises(ValueError):
            features_at_horizon("logistic_four_level", 0)

    def test_no_input_is_on_in_the_published_declaration(self):
        published = set(contract.FEATURE_FIELDS)
        self.assertNotIn("reserve_scarcity_state", published)
        self.assertNotIn("bank_total_assets", published)
        self.assertEqual(contract.FEATURE_FIELDS["on_rrp"], (("fred_macro_latest_vintage", "RRPONTSYD"),))


class PrimaryFamilyTests(unittest.TestCase):
    """Eleonora's rulings of 3 October 2026 on #128."""

    def test_eight_cells_two_forms_with_the_state_alone(self):
        self.assertEqual(PRIMARY_CANDIDATES, ("logistic_four_level", "gbm_four_level"))
        self.assertEqual(len(PRIMARY_CELLS), 8)
        self.assertEqual(
            {primary_key(*cell) for cell in PRIMARY_CELLS},
            {
                f"{name}|brier|{day_set}|5|1|{bench}"
                for name in PRIMARY_CANDIDATES
                for day_set in ("all_days", "onset_days")
                for bench in ("pressure_model_v1_1", "persistence_logistic")
            },
        )
        self.assertEqual(FAMILY_LEVEL, 0.10)
        self.assertEqual(sc.P_VALUE_REPLICATIONS, 20000)

    def test_the_control_is_v1_1_because_117_passed(self):
        self.assertEqual(CONTROL, "pressure_model_v1_1")
        source = (ROOT / "src" / "repo_model" / "scarcity_calendar.py").read_text(encoding="utf-8")
        self.assertIn("PR #204", source)

    def _results(self, **overrides):
        out = {primary_key(*cell): _cell() for cell in PRIMARY_CELLS}
        out.update(overrides)
        return out

    def test_holm_runs_over_all_eight_cells(self):
        key = primary_key("logistic_four_level", "all_days", 5.0, 1, CONTROL)
        # 0.02 < 0.10 / 4 but > 0.10 / 8: it survives a family of four, not of eight.
        verdict = classify_primary(self._results(**{key: _cell(0.02, 0.98)}))
        self.assertFalse(verdict["by_form"]["logistic_four_level"]["passed"])
        verdict = classify_primary(self._results(**{key: _cell(0.01, 0.99)}))
        self.assertTrue(verdict["by_form"]["logistic_four_level"]["passed"])
        self.assertFalse(verdict["by_form"]["gbm_four_level"]["passed"])
        self.assertEqual(verdict["family_size"], 8)

    def test_a_deterioration_blocks_only_its_own_form(self):
        good = primary_key("logistic_four_level", "all_days", 5.0, 1, "persistence_logistic")
        bad = primary_key("logistic_four_level", "onset_days", 5.0, 1, CONTROL)
        other = primary_key("gbm_four_level", "all_days", 5.0, 1, "persistence_logistic")
        verdict = classify_primary(
            self._results(**{good: _cell(0.001, 0.999), bad: _cell(0.999, 0.001), other: _cell(0.001, 0.999)})
        )
        self.assertFalse(verdict["by_form"]["logistic_four_level"]["passed"])
        self.assertEqual(verdict["by_form"]["logistic_four_level"]["deteriorations"], [bad])
        self.assertTrue(verdict["by_form"]["gbm_four_level"]["passed"])

    def test_a_missing_or_extra_cell_is_refused(self):
        results = self._results()
        results.pop(primary_key(*PRIMARY_CELLS[0]))
        with self.assertRaises(ValueError):
            classify_primary(results)
        with self.assertRaises(ValueError):
            classify_primary(self._results(**{primary_key("logistic_two_level", "all_days", 5.0, 1, CONTROL): _cell()}))


if __name__ == "__main__":
    unittest.main()
