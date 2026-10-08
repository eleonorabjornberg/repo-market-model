"""Track S of #374 (#378): the scarcity-conditioned calendar's candidates under the event bar.

What is pinned here is what was declared before any score: the five candidates,
their features, calibration and flagging cut-off in `metadata/pressure_judge.json`,
and the availability rule for the interaction variant's settlement.

Recorded mutation (the one availability guard this track adds). In
`ml._ScarcityCalendarDesign.__init__`, `_INTERACTION_DAY_TYPES if interactions
and self.settlement else ()` replaced by `_INTERACTION_DAY_TYPES if interactions
else ()`: the interaction variant then asks for the settlement's size at
horizons where it is not public. `test_the_interaction_variant_is_the_base_form_without_a_settlement`
(tests/test_ml.py) failed with `AssertionError`: the names differ by the two interaction columns.
Applied and run in a scratch copy, then reverted.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from repo_model import pressure_judge as pj
from repo_model import scarcity_calendar as sc
from repo_model import scarcity_event_bar as eb

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = ROOT / "metadata" / "pressure_judge.json"


class CandidateTests(unittest.TestCase):
    def test_the_five_candidates_are_128s_two_forms_and_three_variants(self):
        self.assertEqual(
            [(c.name, c.form, c.variant) for c in eb.CANDIDATES],
            [
                ("scarcity_logistic", "logistic", "base"),
                ("scarcity_gbm", "gbm", "base"),
                ("scarcity_logistic_interactions", "logistic", "interactions"),
                ("scarcity_gbm_interactions", "gbm", "interactions"),
                ("scarcity_logistic_regime_pooled", "logistic", "regime_pooled"),
            ],
        )

    def test_every_candidate_is_128s_state_alone_design(self):
        for entry in eb.CANDIDATES:
            with self.subTest(entry.name):
                for horizon in (1, 2, 5):
                    self.assertEqual(
                        eb.features_at_horizon(entry.name, horizon),
                        sc.features_at_horizon(f"{entry.form}_four_level", horizon),
                    )

    def test_the_interaction_variant_does_not_read_the_settlement_at_longer_horizons(self):
        for horizon in (2, 3, 4, 5):
            self.assertNotIn("treasury_settlement", eb.features_at_horizon("scarcity_logistic_interactions", horizon))
        self.assertIn("treasury_settlement", eb.features_at_horizon("scarcity_logistic_interactions", 1))

    def test_an_unknown_candidate_is_refused(self):
        with self.assertRaises(ValueError):
            eb.candidate("scarcity_forest")


class DeclarationTests(unittest.TestCase):
    """`metadata/pressure_judge.json` carries each candidate as this module defines it."""

    def test_the_declaration_carries_every_candidate_as_defined_here(self):
        declared = json.loads(DECLARATION.read_text(encoding="utf-8"))["candidates"]
        for entry in eb.CANDIDATES:
            with self.subTest(entry.name):
                want = eb.declaration_entry(entry.name)
                got = declared[entry.name]
                for key in want:
                    self.assertEqual(got[key], want[key], key)

    def test_no_candidate_declares_a_fixed_cutoff(self):
        # The flag cut-off is chosen from each refit's training window (`cutoff_rule`, #407).
        declaration = pj.load_declaration(DECLARATION)
        for entry in eb.CANDIDATES:
            self.assertNotIn("cutoffs", declaration.candidates[entry.name])


if __name__ == "__main__":
    unittest.main()
