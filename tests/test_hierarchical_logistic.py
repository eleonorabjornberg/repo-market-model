"""Track H of #374 (#386): the hierarchical logistic's declaration.

What is pinned here is what was declared before any score: the candidate, its
features, calibration and flagging cut-off in `metadata/pressure_judge.json`.
The estimator's own guards and recorded mutations are in
`tests/test_ml.py::HierarchicalLogisticTests`.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from repo_model import hierarchical_logistic as hl
from repo_model import pressure_judge as pj
from repo_model import scarcity_calendar as sc

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = ROOT / "metadata" / "pressure_judge.json"


class CandidateTests(unittest.TestCase):
    def test_it_is_128s_state_alone_logistic_design(self):
        for horizon in (1, 2, 5):
            self.assertEqual(hl.features_at_horizon(horizon), sc.features_at_horizon("logistic_four_level", horizon))

    def test_the_settlement_leaves_at_longer_horizons(self):
        self.assertIn("treasury_settlement", hl.features_at_horizon(1))
        self.assertNotIn("treasury_settlement", hl.features_at_horizon(2))


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_carries_the_candidate_as_defined_here(self):
        got = json.loads(DECLARATION.read_text(encoding="utf-8"))["candidates"][hl.NAME]
        for key, value in hl.declaration_entry().items():
            self.assertEqual(got[key], value, key)

    def test_the_candidate_declares_no_fixed_cutoff(self):
        got = json.loads(DECLARATION.read_text(encoding="utf-8"))["candidates"][hl.NAME]
        self.assertNotIn("cutoffs", got)
        pj.load_declaration(DECLARATION)


if __name__ == "__main__":
    unittest.main()
