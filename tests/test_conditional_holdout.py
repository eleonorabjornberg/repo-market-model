"""The conditional predictor against climatology on the knowledge holdouts (#372).

Reported-only. These tests hold what the study's text rests on, not its scores:
the declaration is the file the script reads and its windows are `events.json`'s,
the pass rule reads intervals the way the declaration says, and the leap level a
curve is read at is the one `onset.LeapTargets` states.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "conditional_holdout.py"
DECLARATION = ROOT / "docs" / "pivot" / "conditional-vs-climatology-declaration.json"


def _load():
    spec = importlib.util.spec_from_file_location("conditional_holdout", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _paired(lower, upper):
    return {"days": 10, "mean": (lower + upper) / 2, "interval": {"lower": lower, "upper": upper}}


class DeclarationTests(unittest.TestCase):
    def test_script_constants_are_the_declaration(self):
        study = _load()
        declared = json.loads(DECLARATION.read_text())
        self.assertEqual(study.DECLARATION_PATH, DECLARATION)
        self.assertEqual(set(declared["predictors"]) - {"note", "fit_failure_rule"}, set(study.PREDICTORS))
        for name, entry in study.PREDICTORS.items():
            self.assertEqual(list(entry), declared["predictors"][name]["features"])
        self.assertEqual(tuple(declared["benchmarks"]), study.BENCHMARKS)
        self.assertEqual(tuple(declared["thresholds"]["pressure_bp"]), study.PRESSURE_TAUS)
        self.assertEqual(declared["interval"]["level"], study.LEVEL)
        self.assertEqual(declared["interval"]["mean_block_length"], study.BLOCK_LENGTH)
        self.assertEqual(declared["interval"]["replications"], study.REPLICATIONS)
        self.assertEqual(declared["panel"]["minimum_history"], study.MINIMUM_HISTORY)

    def test_windows_are_the_events_file_and_before_the_lockbox(self):
        declared = json.loads(DECLARATION.read_text())
        events = json.loads((ROOT / "metadata" / "events.json").read_text())
        self.assertEqual(
            declared["holdout_windows"]["names"], [w["name"] for w in events["windows"]]
        )
        for window in events["windows"]:
            self.assertLess(date.fromisoformat(window["end"]), date(2026, 1, 1))

    def test_a_declaration_naming_a_missing_window_is_refused(self):
        study = _load()
        declared = json.loads(DECLARATION.read_text())
        declared["holdout_windows"]["names"] = ["sep-2019"]
        with self.assertRaises(ValueError):
            study.check_declaration(declared)


class ResultTests(unittest.TestCase):
    def test_the_result_was_scored_under_the_declaration_as_committed(self):
        study = _load()
        result = json.loads(
            (ROOT / "docs" / "pivot" / "studies" / "conditional_vs_climatology_holdout.json").read_text()
        )
        declared = json.loads(DECLARATION.read_text())
        self.assertEqual(result["declaration_sha256"], study.declaration_digest(declared))

    def test_every_scored_day_is_before_the_lockbox(self):
        result = json.loads(
            (ROOT / "docs" / "pivot" / "studies" / "conditional_vs_climatology_holdout.json").read_text()
        )
        self.assertTrue(result["days"])
        self.assertLess(max(result["days"]), "2026-01-01")

    def test_the_page_states_each_verdict_the_result_carries(self):
        result = json.loads(
            (ROOT / "docs" / "pivot" / "studies" / "conditional_vs_climatology_holdout.json").read_text()
        )
        page = (ROOT / "docs" / "pivot" / "conditional-vs-climatology-holdout.md").read_text()
        for target, entry in result["results"].items():
            for name in ("gbm_published_4", "gbm_published_9", "dynamic_logit"):
                verdict = entry[name]["verdict"].replace("_", " ")
                row = [l for l in page.splitlines() if l.startswith("|") and f"| {name} |" in l]
                self.assertTrue(any(l.rstrip().endswith(f"| {verdict} |") for l in row), (target, name))


class PassRuleTests(unittest.TestCase):
    def test_met_needs_both_benchmarks_above_zero_and_no_cell_below(self):
        rule = _load().cell_verdict
        both = {"climatology": _paired(0.01, 0.2), "persistence_logistic": _paired(0.02, 0.3)}
        self.assertEqual(rule(both, []), "met")
        self.assertEqual(rule(both, [_paired(-0.1, 0.4)]), "met")
        self.assertEqual(rule(both, [{"days": 3, "mean": 0.1}]), "met")  # no interval: not counted

    def test_an_interval_including_zero_is_inconclusive(self):
        rule = _load().cell_verdict
        pooled = {"climatology": _paired(-0.01, 0.2), "persistence_logistic": _paired(0.02, 0.3)}
        self.assertEqual(rule(pooled, []), "inconclusive")

    def test_a_cell_wholly_below_zero_fails_the_rule(self):
        rule = _load().cell_verdict
        both = {"climatology": _paired(0.01, 0.2), "persistence_logistic": _paired(0.02, 0.3)}
        self.assertEqual(rule(both, [_paired(-0.3, -0.01)]), "not_met")

    def test_a_pooled_interval_wholly_below_zero_is_not_met(self):
        rule = _load().cell_verdict
        pooled = {"climatology": _paired(-0.3, -0.1), "persistence_logistic": _paired(0.02, 0.3)}
        self.assertEqual(rule(pooled, []), "not_met")


class EarlyWarningMetricTests(unittest.TestCase):
    def test_auroc_counts_ties_as_half_and_needs_both_classes(self):
        study = _load()
        self.assertEqual(study.auroc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0]), 1.0)
        self.assertEqual(study.auroc([0.1, 0.2, 0.8, 0.9], [1, 1, 0, 0]), 0.0)
        self.assertEqual(study.auroc([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0]), 0.5)
        self.assertIsNone(study.auroc([0.3, 0.4], [1, 1]))

    def test_usefulness_is_sarlins_against_the_best_blind_policy(self):
        study = _load()
        perfect = study.usefulness([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0], mu=0.5)
        self.assertEqual(perfect["absolute"], 0.5)
        self.assertEqual(perfect["relative"], 1.0)
        useless = study.usefulness([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0], mu=0.5)
        self.assertEqual(useless["absolute"], 0.0)
        self.assertIsNone(study.usefulness([0.3, 0.4], [1, 1], mu=0.5))

    def test_lead_is_one_when_the_onset_was_flagged_and_empty_without_onsets(self):
        study = _load()
        days = [date(2019, 9, 16), date(2019, 9, 17)]
        found = study.lead_time([0.7, 0.2], days, [days[0]], level=0.5)
        self.assertEqual((found["onsets"], found["flagged"], found["mean_lead_days"]), (1, 1, 1.0))
        none = study.lead_time([0.7, 0.2], days, [], level=0.5)
        self.assertEqual((none["onsets"], none["mean_lead_days"]), (0, None))


class LeapLevelTests(unittest.TestCase):
    def test_a_day_is_a_leap_exactly_when_its_curve_value_is_read_at_the_stated_level(self):
        study = _load()
        # round(s_t) > s_a + 3  <=>  s_t > floor(s_a + 3) + 0.5 (LeapTargets.event_threshold)
        self.assertEqual(study.leap_level(anchor_bp=1.0, jump_bp=3.0), 4.5)
        self.assertEqual(study.leap_level(anchor_bp=-2.0, jump_bp=3.0), 1.5)


if __name__ == "__main__":
    unittest.main()
