"""The nested measurement of #842 (`scripts/h9_nested_842.py`): the parts that decide what is walked, scored and read.

Recorded mutation (the guards this script adds; the column's own guard is tested in `tests/test_target_forecasts.py`):

* `decision_forecasts`, the check `if set(forecasts) != set(fits):` replaced by `if False:`: a walk read against a fold grid
  it was not made on is then accepted; `DecisionForecastTests.test_a_walk_off_the_fold_grid_is_refused` fails with
  `AssertionError: ValueError not raised`.
* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `LockedDayTests.test_a_locked_day_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`; the blind tier is every day after 2026-09-03, `metadata/lockbox.json`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("h9_nested_842_script", REPO / "scripts" / "h9_nested_842.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402


class LockedDayTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2026, 9, 4)])

    def test_a_development_day_passes(self):
        script.refuse_locked([date(2025, 12, 31)])


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_names_the_candidate_and_the_706_targets(self):
        declared = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(declared["issue"], 842)
        self.assertEqual(declared["candidate"]["name"], "gbm_funding")
        chosen = json.loads(script.m706.DECLARATION.read_text(encoding="utf-8"))["choice"]["chosen"]
        self.assertEqual(declared["targets"]["chosen"], chosen)
        self.assertEqual(sorted(script.TARGETS), sorted(chosen))
        self.assertEqual(set(declared["variants"]) - {"count"}, set(script.VARIANTS))

    def test_the_declaration_pins_the_706_declaration_and_panel(self):
        declared = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        pinned = json.loads(script.m706.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(declared["targets"]["scratch_panel_sha256"], pinned["panel"]["sha256"])

    def test_an_uncommitted_declaration_is_refused(self):
        class Done:
            stdout = " M metadata/h9_nested_842.json\n"

        with mock.patch("subprocess.run", return_value=Done()):
            with self.assertRaises(SystemExit):
                script.committed_declaration()


class VariantTests(unittest.TestCase):
    def test_a_variant_names_its_target_or_none(self):
        self.assertIsNone(script.variant_target("base"))
        self.assertEqual(script.variant_target("plus_on_rrp_change_bn"), "on_rrp_change_bn")

    def test_an_undeclared_variant_is_refused(self):
        with self.assertRaises(ValueError):
            script.variant_target("plus_tgcr_dispersion_bps")
        with self.assertRaises(ValueError):
            script.variant_target("combined")


class HolmTests(unittest.TestCase):
    def test_holm_steps_down_and_keeps_the_input_order(self):
        self.assertEqual(script.holm([0.04, 0.01, 0.03]), [0.06, 0.03, 0.06])

    def test_holm_is_capped_at_one(self):
        self.assertEqual(script.holm([0.6, 0.9]), [1.0, 1.0])


class FinishedWalkTests(unittest.TestCase):
    def test_a_walk_is_finished_only_for_its_own_variant_lead_panels_and_target_walk(self):
        with tempfile.TemporaryDirectory() as directory:
            published, panel = Path(directory) / "pub.csv", Path(directory) / "scratch.csv"
            published.write_text("date,sofr\n2024-03-04,5.3\n", encoding="utf-8")
            panel.write_text("date,sofr\n2024-03-04,5.3\n", encoding="utf-8")
            digest = script.hashlib.sha256(panel.read_bytes()).hexdigest()
            document = {
                "variant": "plus_on_rrp_change_bn", "horizon": 2, "panel_sha256": script.panel_sha256(published),
                "scratch_panel_sha256": digest, "target_walk_sha256": "w", "laws": {},
            }
            path = Path(directory) / "walk.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            kw = dict(published=published, panel=panel)
            self.assertTrue(script.finished_walk(path, variant="plus_on_rrp_change_bn", horizon=2, target_walk="w", **kw))
            self.assertFalse(script.finished_walk(path, variant="base", horizon=2, target_walk="w", **kw))
            self.assertFalse(script.finished_walk(path, variant="plus_on_rrp_change_bn", horizon=3, target_walk="w", **kw))
            self.assertFalse(script.finished_walk(path, variant="plus_on_rrp_change_bn", horizon=2, target_walk="v", **kw))
            self.assertFalse(script.finished_walk(Path(directory) / "missing.json", variant="base", horizon=2, target_walk=None, **kw))


class TargetWalkTests(unittest.TestCase):
    def document(self, **change):
        base = {
            "target": "on_rrp_change_bn", "horizon": 1, "panel_sha256": "s", "levels": list(script.GRID), "laws": {},
            "declaration_sha256": script.hashlib.sha256(script.m706.DECLARATION.read_bytes()).hexdigest(),
        }
        return {**base, **change}

    def read(self, document, digest="s"):
        declared_706 = {"panel": {"sha256": "s"}}
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "on_rrp_change_bn_h1.json").write_text(json.dumps(document), encoding="utf-8")
            return script.target_walk_document(Path(directory), "on_rrp_change_bn", 1, declared_706, digest)

    def test_the_walk_of_the_declared_panel_and_declaration_is_read(self):
        self.assertEqual(self.read(self.document())["horizon"], 1)

    def test_another_panel_or_another_declaration_or_another_lead_is_refused(self):
        for change in ({"panel_sha256": "x"}, {"declaration_sha256": "x"}, {"horizon": 2}, {"target": "bgcr_dispersion_bps"}, {"levels": [0.5]}):
            with self.assertRaises(ValueError, msg=str(change)):
                self.read(self.document(**change))


class DecisionForecastTests(unittest.TestCase):
    """`decision_forecasts` on a panel of 100 business days with the walk's fold grid and fits stubbed."""

    def run_it(self, laws, grid):
        from repo_model.data import DailyObservation, next_business_day

        days = [date(2024, 1, 2)]
        while len(days) < 100:
            days.append(next_business_day(days[-1], 1))
        rows = [DailyObservation(d, {"tgt": 1.0}) for d in days]

        class Sd:
            class ann:
                @staticmethod
                def arm_inputs(arm, panel_rows, registry, horizon):
                    return panel_rows, registry

            class measurement_fields:
                @staticmethod
                def load_registry():
                    return {}

        document = {"laws": {days[i].isoformat(): law for i, law in laws.items()}}
        declared_706 = {"model": {"minimum_history": 61, "refit_every": 21}}
        with mock.patch.object(script.m634, "_load", return_value=Sd), mock.patch.object(
            script.m706, "panel_rows", return_value=rows
        ), mock.patch.object(script, "fold_grid", return_value=tuple(grid)):
            return days, script.decision_forecasts(document, "on_rrp_change_bn", 2, Path("unused"), declared_706)

    def test_a_law_is_keyed_by_the_decision_day_h_rows_before_its_target(self):
        days, (forecasts, fits) = self.run_it({70: [1.0], 71: None, 72: [3.0]}, [70, 71, 72])
        self.assertEqual(forecasts, {days[68]: [1.0], days[69]: None, days[70]: [3.0]})
        self.assertEqual(fits, {days[68]: days[68], days[69]: days[68], days[70]: days[68]})

    def test_a_walk_off_the_fold_grid_is_refused(self):
        with self.assertRaises(ValueError):
            self.run_it({70: [1.0], 72: [3.0]}, [70, 71, 72])


if __name__ == "__main__":
    unittest.main()
