"""`scripts/h9_nested_1800_1345.py` (#1345; H9 step 3, development tier): the nested test on (s3c-ann-net) at the 18:00 decision instant.

Written first, against `metadata/h9_nested_1800_1345.json`. The study re-uses #1321's frame and #706's target walk, so what it adds is pinned here: the
decision instant of the whole chain (the family's and the H9 chain's, which type their own 16:00), the refusal of a target walk that is not the 18:00 walk of the
declared scratch panel on direct pairs, the plus arm (the base with one extra term and nothing else changed), the instant of the scratch-panel build, and
the reading and Holm arithmetic.

**Recorded mutation** (1 November 2026), in `instant_pinned` (the H9 chain types `DECISION` / `DECISION_TIME` itself, so a run at 18:00 must set them):
the line

    if getattr(module, name, None) == LEGACY_DECISION_TIME:

was changed to `if False:`. `InstantTests.test_the_h9_chain_reads_the_declared_instant_inside_and_the_old_one_after` then failed with `ValueError`
(`spread_distribution_634.DECISION is 16:00:00, not the declared instant 18:00:00`, the script's own check, which refuses the run); restored, it
passes. Second mutation, in `check_target_walk` (a 16:00 walk of the targets must not be read as the 18:00 one): the line

    if document.get("decision_time") != INSTANT_TEXT:

was changed to `if False:`. `TargetWalkTests.test_a_walk_made_at_another_instant_is_refused` then failed with `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from datetime import time
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("h9_nested_1800_1345", ROOT / "scripts" / "h9_nested_1800_1345.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["h9_nested_1800_1345"] = script
_spec.loader.exec_module(script)

from repo_model import s3c_announced, spread_mr_state_calendar as sc  # noqa: E402


class InstantTests(unittest.TestCase):
    def test_the_declared_instant_is_eighteen_hundred(self):
        self.assertEqual(script.DECISION_TIME, time(18, 0))
        self.assertEqual(script.INSTANT_TEXT, "18:00")

    def test_the_h9_chain_reads_the_declared_instant_inside_and_the_old_one_after(self):
        before = (script.m634.DECISION, script.m706.DECISION, script.s639.DECISION_TIME, script.m842.DECISION)
        self.assertEqual(before, (time(16, 0),) * 4)
        with script.instant_pinned() as instant:
            self.assertEqual(instant, time(18, 0))
            inside = (script.m634.DECISION, script.m706.DECISION, script.s639.DECISION_TIME, script.m842.DECISION)
            self.assertEqual(inside, (time(18, 0),) * 4)
            self.assertEqual(script.k.DECISION_TIME, time(18, 0))
        self.assertEqual((script.m634.DECISION, script.m706.DECISION, script.s639.DECISION_TIME, script.m842.DECISION), before)

    def test_the_instant_is_put_back_when_the_block_raises(self):
        with self.assertRaises(RuntimeError), script.instant_pinned():
            raise RuntimeError("stop")
        self.assertEqual(script.m634.DECISION, time(16, 0))

    def test_the_scratch_build_reads_the_instant_from_the_environment(self):
        sd = script.m634._load("satiation_distance_598")
        with mock.patch.dict(os.environ, clear=False):
            os.environ.pop("RMM_DECISION_TIME", None)
            self.assertEqual(sd._decision_time(), time(16, 0))
        with mock.patch.dict(os.environ, {"RMM_DECISION_TIME": "18:00"}):
            self.assertEqual(sd._decision_time(), time(18, 0))
        with mock.patch.dict(os.environ, {"RMM_DECISION_TIME": "17:00"}):
            with self.assertRaises(ValueError):
                sd._decision_time()


def walk(**changes):
    document = {
        "target": "sofr_dispersion_bps", "horizon": 2, "levels": list(script.GRID), "panel_sha256": "abc", "decision_time": "18:00",
        "declaration_sha256": __import__("hashlib").sha256(script.DECLARATION.read_bytes()).hexdigest(), "settings": {"training_pairs": "direct"},
    }
    document.update(changes)
    return document


class TargetWalkTests(unittest.TestCase):
    def check(self, document):
        script.check_target_walk(document, "sofr_dispersion_bps", 2, "abc")

    def test_the_declared_walk_is_read(self):
        self.check(walk())

    def test_a_walk_made_at_another_instant_is_refused(self):
        with self.assertRaises(ValueError):
            self.check(walk(decision_time="16:00"))

    def test_a_walk_of_another_target_or_lead_is_refused(self):
        with self.assertRaises(ValueError):
            self.check(walk(target="bgcr_dispersion_bps"))
        with self.assertRaises(ValueError):
            self.check(walk(horizon=3))

    def test_a_walk_on_another_panel_is_refused(self):
        with self.assertRaises(ValueError):
            self.check(walk(panel_sha256="26c51093"))

    def test_a_walk_under_another_declaration_is_refused(self):
        with self.assertRaises(ValueError):
            self.check(walk(declaration_sha256="0" * 64))

    def test_a_walk_not_on_direct_pairs_is_refused(self):
        with self.assertRaises(ValueError):
            self.check(walk(settings={"training_pairs": None}))
        with self.assertRaises(ValueError):
            self.check(walk(settings={}))


class ArmTests(unittest.TestCase):
    def test_the_plus_arm_is_the_base_with_one_extra_term_and_nothing_else(self):
        base = s3c_announced.ANN_NET_ARM
        for target in script.TARGETS:
            arm = script.plus_arm(target)
            self.assertEqual(arm.extra, (sc.H9_FORECAST,))
            self.assertNotEqual(arm.name, base.name)
            for field in ("location", "interact", "robust", "scale", "ridge", "sized", "calendar_k"):
                self.assertEqual(getattr(arm, field), getattr(base, field), field)
        self.assertEqual(base.extra, ())

    def test_one_model_per_target_beside_the_base_and_s3c(self):
        self.assertEqual(len(script.MODELS), 2 + len(script.TARGETS))
        self.assertEqual(len(set(script.PLUS.values())), len(script.TARGETS))


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_names_the_panels_and_the_targets_the_script_uses(self):
        import json

        declared = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(tuple(declared["targets"]["chosen"]), script.TARGETS)
        self.assertEqual(declared["panels"]["published_sha256"], "4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999")
        self.assertNotEqual(declared["panels"]["scratch_1800_sha256"], declared["panels"]["scratch_1600_sha256"])
        self.assertEqual(declared["horizons"], list(script.LEADS))
        self.assertEqual(len(declared["variants"]) - 1, 1 + len(script.TARGETS))  # the base, the plus arms, and the count note

    def test_the_input_units_match_the_declaration(self):
        import json

        text = json.loads(script.DECLARATION.read_text(encoding="utf-8"))["input"]["form"]
        for target, unit in script.s3c_h9.UNITS.items():
            self.assertIn(target, text)
        self.assertIn("on_rrp_change_bn 100", text)


class ReadingTests(unittest.TestCase):
    def test_a_lower_bound_above_zero_improves_the_candidate(self):
        self.assertEqual(script.reading({"difference": 0.02, "difference_interval": [0.01, None]}), "improves the candidate")

    def test_a_lower_bound_at_or_below_zero_does_not(self):
        self.assertEqual(script.reading({"difference": 0.02, "difference_interval": [-0.001, None]}), "no improvement beyond its interval")

    def test_identical_forecasts_are_said_to_be(self):
        self.assertEqual(script.reading({"identical": True, "days": 40}), "identical forecasts")

    def test_holm_steps_down_and_keeps_the_order(self):
        self.assertEqual(script.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])

    def test_holm_block_adjusts_the_targets_that_have_a_p_value(self):
        doc = {"groups": {"pooled": {"all decision days": {"grid_crps": {"nested": {
            "bgcr_dispersion_bps": {"dm_p_value": 0.01}, "on_rrp_change_bn": {"dm_p_value": 0.5}, "sofr_dispersion_bps": {"identical": True}}}}}}}
        block = script.holm_block(doc)["all decision days"]
        self.assertEqual(set(block), {"bgcr_dispersion_bps", "on_rrp_change_bn"})
        self.assertAlmostEqual(block["bgcr_dispersion_bps"]["holm_p"], 0.02)


class FinishedWalkTests(unittest.TestCase):
    def test_a_missing_or_foreign_file_is_not_a_finished_walk(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "w.json"
            self.assertFalse(script.finished_target_walk(path, "sofr_dispersion_bps", 1, "abc"))
            path.write_text("{}", encoding="utf-8")
            self.assertFalse(script.finished_target_walk(path, "sofr_dispersion_bps", 1, "abc"))


if __name__ == "__main__":
    unittest.main()
