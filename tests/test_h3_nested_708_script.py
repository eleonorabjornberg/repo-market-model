"""The nested test of #708 (`scripts/h3_nested_708.py`, H3 step 3): the parts that decide what is scored.

Recorded mutation (the one guard this script adds: the family columns are readable only inside its own switched-on
declaration, with their registered sources, so the as-of rule governs them; nothing joins `contract.FEATURE_FIELDS`):

* `switched_on`, the `mock.patch.multiple(contract, FEATURE_FIELDS=..., FEATURE_SOURCES=...)` replaced by a bare
  `yield`: `test_the_family_columns_resolve_to_their_registered_sources_inside_the_run` errors with
  `contract.UndeclaredFeatureError` (feature 'dts_debt_net_bn' is not in contract.FEATURE_FIELDS ...): the columns are
  unknown to the as-of rule inside the run.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("h3_nested_708_script", REPO / "scripts" / "h3_nested_708.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import contract, new_sources  # noqa: E402
from repo_model.baseline import _resolve_fields  # noqa: E402


class DeclarationTests(unittest.TestCase):
    def test_the_declared_families_are_the_registered_source_families_and_cover_every_column_once(self):
        families = script.family_columns(script.DECLARATION_DATA)
        self.assertEqual(sorted(families), sorted(new_sources.SOURCES))
        declared = [c for columns in families.values() for c in columns]
        self.assertEqual(sorted(declared), sorted(new_sources.COLUMN_FIELDS))
        for family, columns in families.items():
            for column in columns:
                self.assertEqual({source for source, _f in new_sources.COLUMN_FIELDS[column]}, {family})

    def test_a_family_run_reads_the_candidates_features_and_the_family_columns_only(self):
        live = script.s634._load("live_record")
        for h in (1, 2):
            base = set(live.published_features(h))
            for family, columns in script.family_columns(script.DECLARATION_DATA).items():
                self.assertEqual(set(script.family_features(h, family)), base | set(columns))
        self.assertEqual(script.family_features(3, None), tuple(sorted(live.published_features(3))))

    def test_the_candidate_is_gbm_funding_and_reads_none_of_634s_new_inputs(self):
        """Eleonora's rulings of 15 and 17 October 2026: the base is the published features, in the new declaration file."""
        self.assertEqual(script.DECLARATION.name, "h3_nested_708_gbm.json")
        self.assertIn("gbm_funding", script.DECLARATION_DATA["candidate"]["is"])
        extra = set(script.s634.new_features(1)) - set(script.s634._load("live_record").published_features(1))
        self.assertTrue(extra)
        self.assertFalse(extra & set(script.family_features(1, None)))

    def test_the_variants_are_the_base_and_one_per_family(self):
        self.assertEqual(script.VARIANTS[0], "base")
        self.assertEqual(len(script.VARIANTS), 1 + len(new_sources.SOURCES))
        self.assertEqual(script.family_of("plus_treasury_dts_debt_cash"), "treasury_dts_debt_cash")
        self.assertIsNone(script.family_of("base"))
        with self.assertRaises(ValueError):
            script.family_of("plus_nothing")


class OffByDefaultTests(unittest.TestCase):
    def test_the_family_columns_are_off_outside_the_run_and_nothing_is_published_with_them(self):
        for column in new_sources.COLUMN_FIELDS:
            self.assertNotIn(column, contract.FEATURE_FIELDS)

    def test_the_family_columns_resolve_to_their_registered_sources_inside_the_run(self):
        columns = tuple(new_sources.COLUMN_FIELDS)
        with self.assertRaises(ValueError):
            _resolve_fields(columns)
        with script.switched_on():
            _fields, sources = _resolve_fields(columns)
        self.assertTrue(set(new_sources.SOURCES) <= set(sources))
        for column in columns:  # and the run leaves nothing behind
            self.assertNotIn(column, contract.FEATURE_FIELDS)


class HolmTests(unittest.TestCase):
    def test_holm_steps_up_the_sorted_p_values_and_keeps_them_monotone(self):
        adjusted = script.holm([0.01, 0.04, 0.03, 0.2])
        self.assertAlmostEqual(adjusted[0], 0.04)
        self.assertAlmostEqual(adjusted[2], 0.09)
        self.assertAlmostEqual(adjusted[1], 0.09)
        self.assertAlmostEqual(adjusted[3], 0.2)

    def test_holm_never_exceeds_one(self):
        self.assertEqual(script.holm([0.6, 0.7]), [1.0, 1.0])


class ResumeTests(unittest.TestCase):
    def test_a_walk_is_finished_only_for_its_own_variant_lead_and_panels(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            published, panel, out = tmp / "p.csv", tmp / "s.csv", tmp / "w.json"
            published.write_text("date,x\n2020-01-01,1\n")
            panel.write_text("date,x\n2020-01-01,2\n")
            document = {
                "variant": "plus_treasury_dts_debt_cash", "horizon": 2, "laws": {},
                "panel_sha256": script.s634.panel_sha256(published), "scratch_panel_sha256": script.s634.panel_sha256(panel),
            }
            out.write_text(json.dumps(document))
            self.assertTrue(script.finished_walk(out, variant="plus_treasury_dts_debt_cash", horizon=2, published=published, panel=panel))
            self.assertFalse(script.finished_walk(out, variant="base", horizon=2, published=published, panel=panel))
            self.assertFalse(script.finished_walk(out, variant="plus_treasury_dts_debt_cash", horizon=3, published=published, panel=panel))
            panel.write_text("date,x\n2020-01-01,3\n")
            self.assertFalse(script.finished_walk(out, variant="plus_treasury_dts_debt_cash", horizon=2, published=published, panel=panel))


class LockboxTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        from datetime import date

        from repo_model.splits import LookAheadError

        with self.assertRaises(LookAheadError):
            script.s634.refuse_locked([date(2026, 9, 4)])


if __name__ == "__main__":
    unittest.main()
