"""The helpers of `scripts/ranking_765.py` (#765; H8 step 2, development tier).

Written after the script, which is measurement code; its guards are in `repo_model.ranking_daytype`
(tests/test_ranking_daytype.py) and its bootstrap helpers are step 1's (tests/test_ranking_694_script.py).
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ranking_765", ROOT / "scripts" / "ranking_765.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


class DeclarationTests(unittest.TestCase):

    def test_the_seed_and_blocks_are_the_declared_ones(self):
        declaration = json.loads((ROOT / "metadata" / "ranking_765.json").read_text(encoding="utf-8"))
        text = declaration["scores"]["paired"]
        self.assertIn(f"seed {script.SEED}", text)
        self.assertIn(f"mean block {int(script.BLOCK)} business days", text)
        self.assertIn(f"mean block of {int(script.SENSITIVITY_BLOCK)}", text)
        self.assertEqual(script.base.SEED, 765)

    def test_the_compared_benchmarks_are_the_three_and_the_reference(self):
        self.assertEqual(script.COMPARED, ("persistence", "climatology", "calendar", "model_prob"))

    def test_the_page_ends_with_one_line_per_ranker(self):
        gain = {"days": 10, "benchmark_mean": 0.2, "candidate_mean": 0.3, "gain": 0.1, "gain_interval": [0.05, 0.15]}
        primary = {c: {**gain, "interval_wholly_above_zero": True, "kill_condition_met": False, "loses": []}
                   for c in script.rd.CANDIDATES}
        means = {r: {"3": {"precision_all_windows": 0.1, "recall_windows_with_a_pressure_day": 0.2},
                     "5": {"precision_all_windows": 0.1, "recall_windows_with_a_pressure_day": 0.2}} for r in script.rd.RANKERS}
        cell = {b: gain for b in script.COMPARED}
        paired = {c: {m: cell for m in ("precision@3", "precision@5", "recall@3", "recall@5")} for c in script.rd.CANDIDATES}
        result = {
            "notes": {"scored_decision_days": 10, "first": "2020-01-01", "last": "2020-02-01", "last_target": "2020-03-01",
                      "skipped_for_history_or_type": 0},
            "panel_sha256": "ab" * 32, "block_length": 20.0, "draws": 10, "seed": 765,
            "base": {"share_of_windows_with_a_pressure_day": 0.2, "pressure_days_per_window": 1.0,
                     "share_of_window_days_on_a_scheduled_risk_date": 0.1, "share_of_pressure_days_on_a_scheduled_risk_date": 0.3},
            "tail_by_type": {"share_of_target_leads_on_the_fallback": 0.0},
            "blend": {"refits": 1, "refits_on_the_default": 1, "weights_chosen": {"0.5": 1}, "mean_weight_in_force": 0.5},
            "means": means, "composition": {r: {"5": {"share_of_top_k_on_a_scheduled_risk_date": 0.5}} for r in script.rd.RANKERS},
            "paired": {"all": paired, "pressure_windows_precision": {c: {"precision@3": cell, "precision@5": cell} for c in script.rd.CANDIDATES}},
            "sensitivity_block": {"block_length": 10.0, "paired": paired},
            "splits": {"year": {}, "regime": {}, "scarcity": {}},
            "fit": {"phi": {"min": 0.1, "median": 0.5, "max": 0.9}},
            "primary": primary,
        }
        self.result = result
        lines = script.render(result).rstrip().splitlines()
        tail = [line for line in lines[-3:]]
        self.assertEqual(len(tail), 3)
        for line, cand in zip(tail, script.rd.CANDIDATES):
            self.assertIn(script.NAMES[cand], line)
            self.assertIn("lies wholly above zero", line)

    def test_a_rescore_page_carries_its_own_title_and_note_before_the_figures(self):
        self.test_the_page_ends_with_one_line_per_ranker()
        lines = script.render(self.result, title="Re-scored (#924)", note="NOTE-LINE").splitlines()
        self.assertEqual(lines[0], "# Re-scored (#924)")
        self.assertEqual(lines[2], "NOTE-LINE")
        self.assertNotIn("(#765)", lines[0])
        self.assertEqual(script.render(self.result).splitlines()[0], script.render(self.result, title=None).splitlines()[0])


if __name__ == "__main__":
    unittest.main()
