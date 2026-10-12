"""Where the best row's pooled false alarms come from, and three declared gates on its every-day part (#595): the declaration, the candidate files and the lead gate.

Recorded mutations, 12 October 2026, in a disposable copy of `scripts/pooled_gate_595.py`, both in `lead_gate`:
1. the line `farther = [x for x in leads if x > lead]` replaced by `farther = [x for x in leads if x != lead]` (a forecast now reads the same day's
   forecast at a nearer lead, which is issued after its decision instant). Five `LeadGateTests`, among them `test_changing_a_nearer_lead_changes_nothing_farther`
   and `test_a_day_is_kept_at_a_lead_only_if_every_farther_lead_cleared_it`, then error with `LookAheadError` raised by `_read_only_farther`.
2. the same line, with the call `_read_only_farther(lead, farther)` also deleted: `test_a_day_is_kept_at_a_lead_only_if_every_farther_lead_cleared_it`
   and `test_changing_a_nearer_lead_changes_nothing_farther` then fail with `AssertionError` (a nearer lead's forecast changes a farther lead's output).
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model import ml
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "pooled_gate_595.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
CANDIDATES = ROOT / "metadata" / "pressure_judge" / "candidates"


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("pooled_gate_595_script", ROOT / "scripts" / "pooled_gate_595.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["pooled_gate_595_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(PARENTS), DECLARED)

    def test_three_variants_and_no_more(self):
        self.assertEqual(sorted(DECLARED["variants"]), ["gate95", "leadgate", "tail"])
        self.assertEqual(set(SCRIPT.VARIANTS), set(DECLARED["variants"]))
        for key, entry in DECLARED["variants"].items():
            self.assertEqual(entry["name"], SCRIPT.VARIANTS[key])
            self.assertTrue(entry["name"].startswith(SCRIPT.ROW + "+"))

    def test_the_stricter_gate_is_one_declared_value(self):
        self.assertEqual(DECLARED["variants"]["gate95"]["gate"], dict(SCRIPT.GATE, quantile=0.95))
        self.assertEqual(SCRIPT.GATE, {"quantile": 0.9, "window": 250, "minimum_earlier": 60})

    def test_the_tail_variant_drops_the_75th_percentile_and_reads_the_announced_change_at_h1_only(self):
        self.assertEqual(SCRIPT.tail_inputs(1), ("spread_bps", "sofr_p99_iorb_bps", "iorb_announced_change_bps"))
        for h in (2, 3, 4, 5):
            self.assertEqual(SCRIPT.tail_inputs(h), ("spread_bps", "sofr_p99_iorb_bps"))
        self.assertEqual(SCRIPT.row_inputs(1), ml.EVERY_DAY_COMPONENT_INPUTS + ("iorb_announced_change_bps",))
        self.assertEqual(SCRIPT.row_inputs(3), ml.EVERY_DAY_COMPONENT_INPUTS)

    def test_the_scoring_is_the_parents_and_ends_before_the_lockbox(self):
        self.assertEqual(DECLARED["scoring"], PARENTS["scoring"])
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_the_literal_reading_of_the_nearest_lead_gate_is_declared_inadmissible(self):
        self.assertIn("information-set.md", DECLARED["variants"]["leadgate"]["reading"])

    def test_nothing_joins_a_published_declaration(self):
        published = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())
        for name in SCRIPT.VARIANTS.values():
            self.assertNotIn(name, json.dumps(published.get("confirmation", {})))
        self.assertIn("nothing", DECLARED["published"])


class CandidateFileTests(unittest.TestCase):
    def test_each_variant_has_a_candidate_file_naming_the_row_as_parent(self):
        for name in SCRIPT.VARIANTS.values():
            entry = json.loads((CANDIDATES / f"{name}.json").read_text())
            self.assertEqual(entry["role"], "candidate")
            self.assertEqual(entry["track"], "#595")
            self.assertEqual(entry["parent"], SCRIPT.ROW)
            self.assertIn("metadata/pooled_gate_595.json", entry["calibration"])
        self.assertEqual({n: json.loads((CANDIDATES / f"{n}.json").read_text()) for n in SCRIPT.VARIANTS.values()}, SCRIPT.candidate_entries())


def _forecasts(values):
    """{lead: {"5": {day: p}}} from {lead: [p, ...]} over days d0, d1, ..."""

    return {lead: {"5": {f"d{k}": p for k, p in enumerate(ps)}} for lead, ps in values.items()}


def _every_day(forecasts):
    return {lead: {day: True for day in by["5"]} for lead, by in forecasts.items()}


class LeadGateTests(unittest.TestCase):
    def test_a_day_is_kept_at_a_lead_only_if_every_farther_lead_cleared_it(self):
        forecasts = _forecasts({1: [0.5, 0.5, 0.5], 2: [0.4, 0.0, 0.4], 3: [0.3, 0.3, 0.0]})
        out = SCRIPT.lead_gate(forecasts, _every_day(forecasts))
        self.assertEqual(out[3]["5"], {"d0": 0.3, "d1": 0.3, "d2": 0.0})
        self.assertEqual(out[2]["5"], {"d0": 0.4, "d1": 0.0, "d2": 0.0})
        self.assertEqual(out[1]["5"], {"d0": 0.5, "d1": 0.0, "d2": 0.0})

    def test_a_risk_date_keeps_its_forecast(self):
        forecasts = _forecasts({1: [0.5, 0.5], 2: [0.0, 0.0]})
        not_risk = _every_day(forecasts)
        not_risk[1]["d0"] = False
        out = SCRIPT.lead_gate(forecasts, not_risk)
        self.assertEqual(out[1]["5"], {"d0": 0.5, "d1": 0.0})

    def test_a_day_not_scored_at_a_farther_lead_is_not_conditioned_on_it(self):
        forecasts = {1: {"5": {"d0": 0.5, "d1": 0.5}}, 2: {"5": {"d1": 0.0}}}
        out = SCRIPT.lead_gate(forecasts, {1: {"d0": True, "d1": True}, 2: {"d1": True}})
        self.assertEqual(out[1]["5"], {"d0": 0.5, "d1": 0.0})

    def test_a_forecast_never_reads_a_nearer_lead(self):
        with self.assertRaises(LookAheadError):
            SCRIPT._read_only_farther(3, [1, 4])
        SCRIPT._read_only_farther(3, [4, 5])

    def test_changing_a_nearer_lead_changes_nothing_farther(self):
        base = _forecasts({1: [0.5, 0.5, 0.5], 2: [0.4, 0.0, 0.4], 3: [0.3, 0.3, 0.0]})
        changed = _forecasts({1: [0.0, 0.9, 0.0], 2: [0.4, 0.0, 0.4], 3: [0.3, 0.3, 0.0]})
        one = SCRIPT.lead_gate(base, _every_day(base))
        two = SCRIPT.lead_gate(changed, _every_day(changed))
        for lead in (2, 3):
            self.assertEqual(one[lead], two[lead])

    def test_the_curve_across_thresholds_stays_non_increasing(self):
        forecasts = {1: {"5": {"d0": 0.5}, "10": {"d0": 0.4}}, 2: {"5": {"d0": 0.0}, "10": {"d0": 0.4}}}
        out = SCRIPT.lead_gate(forecasts, {1: {"d0": True}, 2: {"d0": True}})
        self.assertLessEqual(out[1]["10"]["d0"], out[1]["5"]["d0"])
        self.assertEqual(out[1]["10"]["d0"], 0.0)


class RunGuardTests(unittest.TestCase):
    def test_the_scoring_ends_before_the_locked_days(self):
        from repo_model.lockbox import require_unlocked
        from datetime import date

        require_unlocked([date.fromisoformat(DECLARED["scoring"]["last_day"])], where="test")
        with self.assertRaises(Exception):
            require_unlocked([date(2026, 9, 4)], where="test")


if __name__ == "__main__":
    unittest.main()
