"""The announced IORB change in the control row's every-day component (#579): the declaration, the candidate file and the run's guards.

Recorded mutation, 11 October 2026, in a disposable copy: `scripts/iorb_every_day_579.py`, the line
`require_unlocked([last], where="iorb_every_day_579")` replaced by `pass` in `run_command`.
`RunGuardTests.test_run_refuses_a_locked_last_day` then errors with `FileNotFoundError` (the guard is skipped and the run goes on to
read the parent's forecasts).
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

from repo_model import ml
from repo_model import pressure_judge as pj
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "iorb_every_day_579.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
CANDIDATES = ROOT / "metadata" / "pressure_judge" / "candidates"


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("iorb_every_day_579_script", ROOT / "scripts" / "iorb_every_day_579.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["iorb_every_day_579_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(PARENTS), DECLARED)

    def test_one_row_and_its_parent_only(self):
        self.assertEqual(DECLARED["row"]["name"], SCRIPT.NEW)
        self.assertEqual(DECLARED["parent"]["row"], SCRIPT.PARENT)
        self.assertEqual(SCRIPT.NEW, SCRIPT.PARENT + "+iorb")
        self.assertEqual(DECLARED["row"]["read_at_horizons"], [1])

    def test_the_only_change_is_the_one_input_in_the_every_day_component(self):
        self.assertEqual(DECLARED["parent"]["every_day_inputs"], list(ml.EVERY_DAY_COMPONENT_INPUTS))
        self.assertEqual(DECLARED["row"]["every_day_inputs"], list(ml.EVERY_DAY_COMPONENT_INPUTS) + ["iorb_announced_change_bps"])

    def test_the_scoring_is_the_parents_and_ends_before_the_lockbox(self):
        self.assertEqual(DECLARED["scoring"], PARENTS["scoring"])
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_the_input_is_off_in_every_published_declaration(self):
        published = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())
        self.assertNotIn(SCRIPT.NEW, json.dumps(published.get("confirmation", {})))
        self.assertNotIn("iorb_announced_change_bps", json.dumps(PARENTS))


class CandidateTests(unittest.TestCase):
    def test_the_row_is_a_judge_candidate_with_a_file_of_its_own(self):
        declared = dict(pj.load_declaration().candidates)
        self.assertIn(SCRIPT.NEW, declared)
        entry = json.loads((CANDIDATES / f"{SCRIPT.NEW}.json").read_text())
        self.assertEqual(entry["role"], "candidate")
        self.assertEqual(entry["parent"], SCRIPT.PARENT)

    def test_the_row_differs_from_its_parent_by_the_one_input(self):
        parent = json.loads((CANDIDATES / f"{SCRIPT.PARENT}.json").read_text())
        entry = json.loads((CANDIDATES / f"{SCRIPT.NEW}.json").read_text())
        self.assertEqual(entry["features"], parent["features"] + ["iorb_announced_change_bps"])

    def test_the_row_is_not_in_the_confirmation_look(self):
        self.assertNotIn(SCRIPT.NEW, set(pj.load_declaration().confirmation_candidates))


class RunGuardTests(unittest.TestCase):
    def args(self, **changes):
        import argparse

        base = dict(horizon=1, end=None, panel=ROOT / "no-such-panel.csv", published=ROOT / "no-such-panel.csv",
                    parent=ROOT / "no-such-parent.json", output=ROOT / "no-such-output.json")
        base.update(changes)
        return argparse.Namespace(**base)

    def test_run_refuses_a_locked_last_day(self):
        declared = json.loads(json.dumps(DECLARED))
        declared["scoring"]["last_day"] = "2026-09-10"
        with mock.patch.object(SCRIPT.rds, "committed_declaration", return_value=declared):
            with self.assertRaises(LookAheadError):
                SCRIPT.run_command(self.args())

    def test_the_declared_last_day_is_not_refused(self):
        with mock.patch.object(SCRIPT.rds, "committed_declaration", return_value=DECLARED):
            with self.assertRaises(FileNotFoundError):  # past the guard, into the parent's forecasts
                SCRIPT.run_command(self.args())

    def test_a_horizon_that_is_not_declared_is_refused(self):
        with mock.patch.object(SCRIPT.rds, "committed_declaration", return_value=DECLARED):
            with self.assertRaises(SystemExit):
                SCRIPT.run_command(self.args(horizon=9))


class SummaryTests(unittest.TestCase):
    def judged(self, flagged, passes):
        tier = {"onsets_flagged": flagged, "onsets": 26, "recall": {"mean": flagged / 26.0, "interval": {"lower": 0.1, "upper": 0.9}},
                "worst_false_alarms_per_onset": 2.5, "worst_weighted_false_alarms_per_onset": 1.5}
        verdict = {"tier_1_onset_warning": True, "tier_3_no_crying_wolf": False, "tier_5_week_ahead": False, "passes": passes}
        return {"tiers": {"onset_warning": {"lead_at_least_1": tier, "lead_at_least_3": tier}}, "verdict": verdict}

    def test_a_row_for_the_parent_and_the_new_row_under_each_rule_and_the_weighted_false_alarms_under_the_weighted_rule(self):
        judged = {rule: {SCRIPT.PARENT: self.judged(18, False), SCRIPT.NEW: self.judged(19, False)} for rule in ("flat", "weighted")}
        lines = SCRIPT.summary_rows(judged)
        self.assertEqual(len(lines), 2 + 4)
        self.assertIn("19 of 26", [l for l in lines if l.startswith(f"| {SCRIPT.NEW} | weighted")][0])
        self.assertIn("1.50", [l for l in lines if l.startswith(f"| {SCRIPT.NEW} | weighted")][0])
        self.assertIn("2.50", [l for l in lines if l.startswith(f"| {SCRIPT.NEW} | flat")][0])


if __name__ == "__main__":
    unittest.main()
