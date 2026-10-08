"""The settlement-timing candidates (#379): their declaration is the one the judge reads.

`repo_model.settlement_timing` names six candidates (a probit and a skew-t quantile
regression, on three nested sets of inputs) and `metadata/pressure_judge.json` carries each
one's features and flagging cut-off, committed before any score. These tests keep the two
the same: a candidate the judge does not declare could not be scored, and a declared one
whose inputs differ from the module's would be judged for a model that was not run.
"""

from __future__ import annotations

import unittest

from repo_model import pressure_judge, settlement_timing as st


class SettlementTimingDeclarationTests(unittest.TestCase):
    def setUp(self):
        self.declaration = pressure_judge.load_declaration()

    def test_every_candidate_is_declared_to_the_judge_with_its_inputs(self):
        for entry in st.CANDIDATES:
            declared = self.declaration.candidates[entry.name]
            self.assertEqual(declared["role"], "candidate")
            self.assertEqual(declared["form"], entry.form)
            self.assertEqual(declared["inputs"], entry.inputs)
            self.assertEqual(tuple(declared["features"]), st.INPUT_SETS[entry.inputs])

    def test_no_candidate_declares_a_fixed_cutoff(self):
        # The flag cut-off is chosen from each refit's training window (`cutoff_rule`, #407).
        for entry in st.CANDIDATES:
            self.assertNotIn("cutoffs", self.declaration.candidates[entry.name])

    def test_the_input_sets_are_nested(self):
        timing, scarcity, tga = (st.INPUT_SETS[k] for k in ("timing", "scarcity", "tga"))
        self.assertTrue(set(timing) < set(scarcity) < set(tga))

    def test_a_settlement_amount_leaves_the_inputs_at_horizons_of_two_or_more(self):
        for entry in st.CANDIDATES:
            one = st.features_at_horizon(entry.name, 1)
            two = st.features_at_horizon(entry.name, 2)
            self.assertEqual(one, st.INPUT_SETS[entry.inputs])
            self.assertEqual(set(one) - set(two), set(st.SETTLEMENTS))
            self.assertEqual(st.features_at_horizon(entry.name, 5), two)

    def test_an_unknown_candidate_or_a_horizon_below_one_is_refused(self):
        with self.assertRaises(ValueError):
            st.candidate("settlement_logit_timing")
        with self.assertRaises(ValueError):
            st.features_at_horizon("settlement_probit_timing", 0)


if __name__ == "__main__":
    unittest.main()
