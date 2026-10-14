"""The candidate declarations of the satiation (#587) and kinked (#626) rows name the inputs their scripts read (#691, finding #673).

After #618 and #679 the structural model reads the scored day's own announced settlement as `net_settlement_ahead_{h}d` and
`net_settlement_ahead_{h-1}d` at h >= 2, not the five-day sum `net_settlement_due_5d`. Each candidate file's
`features_at_horizon_2_or_more` has to say so, and the columns it names have to be the ones the code reads, so a later change of
input cannot pass silently.

* `StructuralCandidateTests` -- for the structural rows, the columns the declaration names at each horizon 2 to 5 are exactly the
  drain columns of `structural_liquidity.features_at_horizon` for the row's form.
* `CombinedCandidateTests` -- the same for the three `risk_gbm+combined_*` rows against `combined_model_561.component_features`.

**Recorded mutation** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, applied and confirmed by `grep`):
`structural_liquidity.drain_columns`: replace `(_DRAIN_COLUMNS[horizon - 2],) if horizon > 1 else ()` by `() if horizon > 1 else ()`
(the second drain column dropped); `StructuralCandidateTests.test_the_named_columns_are_the_ones_read` fails with `AssertionError`
(the declaration names two columns, the code reads one).
"""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

from repo_model import ml, structural_liquidity as sl

REPO = Path(__file__).resolve().parents[1]
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"
FIELD = "features_at_horizon_2_or_more"
STRUCTURAL = {
    "structural_rolling": "rolling",
    "structural_fitted": "fitted",
    "structural_liquidity+h41": "fixed",
    "structural_kinked_rolling": "kinked_rolling",
    "structural_kinked_fitted": "kinked_fitted",
}
COMBINED = ("risk_gbm+combined_rolling", "risk_gbm+combined_fitted", "risk_gbm+combined_hinge_fixed")
TOKEN = re.compile(r"net_settlement_ahead_\{h(-1)?\}d")


def _declared(name: str) -> str:
    return json.loads((CANDIDATES / f"{name}.json").read_text())[FIELD]


def _named_at(name: str, horizon: int) -> set:
    """The drain columns the declaration names at `horizon`, from its `{h}` and `{h-1}` placeholders."""

    return {
        f"net_settlement_ahead_{horizon - 1 if match.group(1) else horizon}d" for match in TOKEN.finditer(_declared(name))
    }


def _combined_module():
    spec = importlib.util.spec_from_file_location("combined_model_561", REPO / "scripts" / "combined_model_561.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StructuralCandidateTests(unittest.TestCase):
    def test_no_declaration_names_the_five_day_sum(self) -> None:
        for name in list(STRUCTURAL) + list(COMBINED):
            with self.subTest(name=name):
                text = _declared(name)
                self.assertNotIn("due_5d in place of", text)
                self.assertNotIn("net_settlement_due_5d in place", text)

    def test_the_named_columns_are_the_ones_read(self) -> None:
        for name, form in STRUCTURAL.items():
            for horizon in range(2, 6):
                with self.subTest(name=name, horizon=horizon):
                    read = set(sl.features_at_horizon(horizon, form)) & set(sl._DRAIN_COLUMNS)
                    self.assertEqual(_named_at(name, horizon), read)


class CombinedCandidateTests(unittest.TestCase):
    def test_the_named_columns_are_the_ones_read(self) -> None:
        cm = _combined_module()
        for name in COMBINED:
            for horizon in range(2, 6):
                with self.subTest(name=name, horizon=horizon):
                    design, _ = cm.component_features(horizon, ml.COMBINED_BLOCKS)
                    read = set(design) & set(sl._DRAIN_COLUMNS)
                    self.assertEqual(_named_at(name, horizon), read)


if __name__ == "__main__":
    unittest.main()
