"""Every model declaration under `metadata/` names its hypothesis and declares its variants (#732; H5 step 5).

The progress page's variant count (`scripts/emit_progress.py`, #637) reads declarations by content, not by file
name, and §2 of the protocol publishes that count with every registration, so a declaration the count cannot see
makes the selection look cleaner than it was. A model declaration is a `metadata/*.json` object with a `variants`
block (top level, or under `model`), or one that has both `model` and `scoring`. It must have a `hypothesis` key and
a `variants` block. `LEGACY` lists the declarations that predate the rule (11 to 14 October 2026); the test refuses a
new one that is missing either, and refuses a `LEGACY` entry that no longer needs the exemption. Converting a legacy
declaration is not part of #732 (they are published pre-registrations).

Recorded mutations (run on the tests below, then restored):

* `declared_variants` ignoring `model.variants`: `test_nested_variants_are_seen` failed with AssertionError.
* `is_model_declaration` dropping the `model`+`scoring` clause: `test_declaration_without_variants_is_refused`
  failed with AssertionError.
* `problems` skipping the `hypothesis` check: `test_declaration_without_hypothesis_is_refused` failed with
  AssertionError.
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("emit_progress", ROOT / "scripts" / "emit_progress.py")
emit_progress = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(emit_progress)

LEGACY = {
    "backfill_spread_633.json",
    "combined_model_561.json",
    "dist_roll_606.json",
    "effr_pretrain.json",
    "every_day_conditioning_601.json",
    "hindsight_regimes.json",
    "hurdle_dating.json",
    "identified_level_689.json",
    "kinked_626.json",
    "latent_factor.json",
    "model_defects_540.json",
    "near_threshold_688.json",
    "off_risk_day_624.json",
    "pooled_gate_595.json",
    "pressure_hazard.json",
    "pressure_tail.json",
    "projected_reserves.json",
    "richer_targets_706.json",
    "risk_date_every_day.json",
    "risk_date_hurdle.json",
    "satiation_distance_598.json",
    "spread_distribution_632.json",
    "state_recalibration_589.json",
    "tailcap_floor_610.json",
}


def problems(decl):
    """What a model declaration lacks: a list of "hypothesis" and "variants"; empty for a good one."""
    out = []
    if "hypothesis" not in decl:
        out.append("hypothesis")
    if emit_progress.declared_variants(decl) is None:
        out.append("variants")
    return out


class ModelDeclarations(unittest.TestCase):
    def test_nested_variants_are_seen(self):
        self.assertEqual(emit_progress.declared_variants({"model": {"variants": {"a": 1, "b": 2}}}), {"a": 1, "b": 2})
        self.assertEqual(emit_progress.declared_variants({"variants": [1, 2, 3]}), [1, 2, 3])
        self.assertIsNone(emit_progress.declared_variants({"variants": "none"}))

    def test_declaration_without_variants_is_refused(self):
        decl = {"hypothesis": "H5", "model": {"control": "x"}, "scoring": {}}
        self.assertTrue(emit_progress.is_model_declaration(decl))
        self.assertEqual(problems(decl), ["variants"])

    def test_declaration_without_hypothesis_is_refused(self):
        self.assertEqual(problems({"variants": {"a": {}}}), ["hypothesis"])
        self.assertEqual(problems({"hypothesis": "H5", "variants": {"a": {}}}), [])

    def test_other_metadata_is_not_a_model_declaration(self):
        self.assertFalse(emit_progress.is_model_declaration({"status": "x", "rows": []}))
        self.assertFalse(emit_progress.is_model_declaration([1, 2]))

    def test_every_committed_declaration_is_complete_or_legacy(self):
        seen = set()
        for path in sorted((ROOT / "metadata").glob("*.json")):
            decl = json.loads(path.read_text())
            if not emit_progress.is_model_declaration(decl):
                continue
            lacking = problems(decl)
            if path.name in LEGACY:
                seen.add(path.name)
                self.assertTrue(lacking, "%s is complete: remove it from LEGACY" % path.name)
            else:
                self.assertEqual(lacking, [], "%s is a model declaration lacking %s" % (path.name, lacking))
        self.assertEqual(sorted(LEGACY - seen), [], "LEGACY names a file that is gone or no longer a declaration")


if __name__ == "__main__":
    unittest.main()
