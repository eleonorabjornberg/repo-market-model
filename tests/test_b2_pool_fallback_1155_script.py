"""The helpers of `scripts/b2_pool_fallback_1155.py` (#1155; H5 step 2, development tier).

Written after the script, which is measurement code. The fallback itself and its as-of guard are tested in
`test_b2_pool_1155` (with the recorded mutation); the scored days pass `spread_mean_reversion_686.require_scored_days`. What
these tests pin: the exceedance and band-miss sequences on hand cases under both hit rules (the lower side is the mirror), that
the legacy reference stays legacy whatever `turn_days.IN_FORCE` says, the declaration's arms against the script's, and that the
committed page is what the committed record gives.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from repo_model import scoring_protocol as sp
from repo_model import turn_days
from repo_model.evaluation_splits import load_split_declaration

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("b2_pool_fallback_1155", ROOT / "scripts" / "b2_pool_fallback_1155.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["b2_pool_fallback_1155"] = script
_spec.loader.exec_module(script)


def law(low, high):
    """A law whose q05 and below sit at `low`, q95 and above at `high`, the body at the midpoint."""

    return [low if level <= 0.05 else high if level >= 0.95 else (low + high) / 2.0 for level in sp.GRID]


class HitTests(unittest.TestCase):
    def test_q95_exceedance_under_both_rules(self):
        laws = [law(-1, 1)] * 3
        outcomes = [1.0, 2.0, 0.0]
        self.assertEqual(script.hit_sequence(outcomes, laws, "q95", "above"), [0, 1, 0])
        self.assertEqual(script.hit_sequence(outcomes, laws, "q95", "at_or_above"), [1, 1, 0])

    def test_a_band_miss_is_either_tail_and_the_lower_side_is_the_mirror(self):
        laws = [law(-1, 1)] * 4
        outcomes = [-1.0, -2.0, 0.0, 2.0]
        self.assertEqual(script.hit_sequence(outcomes, laws, "band90", "above"), [0, 1, 0, 1])
        self.assertEqual(script.hit_sequence(outcomes, laws, "band90", "at_or_above"), [1, 1, 0, 1])

    def test_the_nominal_rates_are_the_kinds(self):
        self.assertEqual({k: v[2] for k, v in script.KINDS.items()}, {"q95": 0.05, "band90": 0.10, "band50": 0.50})

    def test_a_small_group_gets_no_p_value(self):
        self.assertIsNone(script.coverage_row([0] * 19, 0.1)["kupiec_p"])
        self.assertIsNotNone(script.coverage_row([0] * 19 + [1], 0.1)["kupiec_p"])


class LabelTests(unittest.TestCase):
    def test_the_legacy_reference_stays_legacy_when_the_turn_record_is_in_force(self):
        splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
        values = {"days_to_month_end": 1.0, "quarter_end": 0.0, "tax_date": 0.0, "treasury_settlement_coupons": 0.0}
        penultimate = date(2019, 5, 30)
        with mock.patch.object(turn_days, "IN_FORCE", True):
            self.assertEqual(script.Legacy(splits).reporting_day_type(penultimate, values), "month_end")
            self.assertEqual(turn_days.TurnLabels(splits).reporting_day_type(penultimate, values), "ordinary")

    def test_the_cache_returns_the_first_label_of_a_date(self):
        class Inner:
            calls = 0

            def reporting_day_type(self, when, values):
                Inner.calls += 1
                return "turn"

        cached = script.Cached(Inner())
        self.assertEqual(cached.reporting_day_type(date(2020, 1, 2), {}), "turn")
        self.assertEqual(cached.reporting_day_type(date(2020, 1, 2), {}), "turn")
        self.assertEqual(Inner.calls, 1)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_names_the_scripts_arms_and_chains(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(set(declaration["arms"]), set(script.MODELS))
        self.assertEqual({k: tuple(v[:-1]) for k, v in declaration["chains"].items()}, dict(script.b2_pool.CHAINS))
        self.assertEqual(declaration["warm_up_rows"], script.WARM_UP_ROWS)
        self.assertEqual(declaration["seed"], script.SEED)
        self.assertEqual(declaration["variants"], len(script.POOL_MINS))

    def test_the_drafted_minimum_is_one_of_the_arms(self):
        self.assertIn(script.b2_pool.POOL_MIN, script.POOL_MINS)


class PageTests(unittest.TestCase):
    def test_the_committed_page_is_what_the_committed_record_gives(self):
        record = ROOT / "docs" / "research" / "b2-pool-fallback-1155" / "result.json"
        page = ROOT / "docs" / "research" / "b2-pool-fallback-1155-result.md"
        result = json.loads(record.read_text(encoding="utf-8"))
        self.assertEqual(page.read_text(encoding="utf-8"), script.render_page(result))
        self.assertEqual(result["label"], "development, not a verdict")
        self.assertLessEqual(date.fromisoformat(result["notes"]["last_target"]), script.LAST_DAY)


if __name__ == "__main__":
    unittest.main()
