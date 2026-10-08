"""The flattening diagnosis (#373): its measures, its guards and its record.

`scripts/exceedance_flattening_diagnosis.py` walks the published pressure model v1
(that needs the `ml` extra and a panel, so it is not run here) and assembles
`docs/runs/exceedance_flattening_diagnosis.json`. These tests read no panel: the
measures and the guards run on synthetic inputs, and the record is checked against
the published pressure-model records.

Written before the record existed: `RecordTests` was run red with no record, then
green on the record the script wrote.

Mutation record (`WindowGuardTests`, the assembly's last-day guard): in
`assemble_command`, `if days[-1]["date"] > LAST_DAY:` changed to `if False:`;
confirmed applied by grep. The test `test_a_walk_past_the_compared_days_is_refused`
then failed with `AssertionError` (nothing was refused: the assembly went on and raised
`AttributeError`, which the test reports as "reached the assembly"). Restored, green.

Mutation record (`ReproductionTests`, the published-record check): in
`assemble_command`, `if abs(mine - entry["brier"]) > TOLERANCE:` changed to
`if False:`; confirmed applied by grep. The test
`test_a_walk_that_is_not_the_published_record_is_refused` then failed with
`AssertionError` (the one-day walk went past the check and the assembly stopped
on its own `ValueError`, "10.0 is not in list", not on the published-record
message). Restored, green.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
RECORD = REPO / "docs" / "runs" / "exceedance_flattening_diagnosis.json"
LAST_COMPARED = "2025-12-31"


def _script():
    spec = importlib.util.spec_from_file_location(
        "exceedance_flattening_diagnosis", REPO / "scripts" / "exceedance_flattening_diagnosis.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fd = _script()


class MeasureTests(unittest.TestCase):
    def test_auc_of_a_perfect_ranking(self):
        self.assertEqual(fd._auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]), 1.0)

    def test_auc_of_a_reversed_ranking(self):
        self.assertEqual(fd._auc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]), 0.0)

    def test_tied_scores_count_one_half(self):
        self.assertEqual(fd._auc([0.5, 0.5, 0.5, 0.5], [0, 1, 0, 1]), 0.5)

    def test_auc_is_undefined_without_both_outcomes(self):
        self.assertIsNone(fd._auc([0.1, 0.2], [0, 0]))

    def test_reliability_bins_hold_every_day_once(self):
        days = [{"final": [p], "outcomes": [int(p > 0.3)]} for p in (0.0, 0.005, 0.03, 0.07, 0.15, 0.3, 0.9, 1.0)]
        bins = fd._reliability_bins(days, 0, "final")
        self.assertEqual(sum(b["days"] for b in bins), len(days))
        self.assertEqual(sum(b["events"] for b in bins), 2)

    def test_skill_against_the_reference(self):
        self.assertAlmostEqual(fd._skill(0.9, 1.0), 0.1)
        self.assertIsNone(fd._skill(0.9, 0.0))


class WindowGuardTests(unittest.TestCase):
    def _run(self, last_day):
        with tempfile.TemporaryDirectory() as tmp:
            panel = Path(tmp) / "panel.csv"
            panel.write_text("x", encoding="utf-8")
            walk = Path(tmp) / "walk_h1.json"
            walk.write_text(json.dumps({"horizon": 1, "taus_bp": [5.0], "panel_sha256": "p",
                                        "days": [{"date": last_day}]}), encoding="utf-8")
            args = SimpleNamespace(panel=panel, walks=[walk], output=Path(tmp) / "out.json")
            script = fd
            originals = (script._script,)
            import repo_model.data as data
            import repo_model.evaluation_splits as splits
            saved = (data.load_daily_panel, data.audit_panel, splits.load_split_declaration)
            data.load_daily_panel = lambda path: []
            data.audit_panel = lambda rows: None
            splits.load_split_declaration = lambda path: SimpleNamespace(regimes=())
            try:
                script.assemble_command(args)
            except ValueError as error:
                return str(error)
            except Exception as error:  # past the guard, the assembly fails on its own terms
                return f"reached the assembly: {error!r}"
            finally:
                data.load_daily_panel, data.audit_panel, splits.load_split_declaration = saved
            return None

    def test_a_walk_past_the_compared_days_is_refused(self):
        message = self._run("2026-01-02")
        self.assertIn("locked", message or "nothing was refused")


class ReproductionTests(unittest.TestCase):
    def test_a_walk_that_is_not_the_published_record_is_refused(self):
        published = json.loads((REPO / "docs" / "runs" / "pressure_model_v1_h1.json").read_text())
        self.assertIn("brier", published["metrics"]["by_tau"]["5"])
        # one synthetic day cannot have the published Brier, so the check must refuse it
        day = {"date": "2018-06-29", "outcomes": [1], "raw": [0.5], "final": [0.5], "reference": [0.5],
               "persistence_logistic": [0.5], "train_end": "2018-06-27", "knots_bps": [0, 1, 2, 3, 4, 5, 6]}
        with tempfile.TemporaryDirectory() as tmp:
            walk = Path(tmp) / "walk_h1.json"
            walk.write_text(json.dumps({"horizon": 1, "taus_bp": [5.0], "panel_sha256": "p", "days": [day]}),
                            encoding="utf-8")
            args = SimpleNamespace(panel=Path(tmp) / "panel.csv", walks=[walk], output=Path(tmp) / "out.json")
            import repo_model.data as data
            import repo_model.evaluation_splits as splits
            saved = (data.load_daily_panel, data.audit_panel, splits.load_split_declaration)
            row = SimpleNamespace(values={"quarter_end": 0.0, "days_to_month_end": 9.0, "tax_date": 0.0},
                                  date=__import__("datetime").date(2018, 6, 29), spread_bps=1.0)
            data.load_daily_panel = lambda path: [row]
            data.audit_panel = lambda rows: None
            splits.load_split_declaration = lambda path: SimpleNamespace(
                regimes=(("2018-19", None, None),), regime=lambda when: "2018-19",
                day_type=lambda values: "ordinary")
            message = None
            try:
                fd.assemble_command(args)
            except ValueError as error:
                message = str(error)
            finally:
                data.load_daily_panel, data.audit_panel, splits.load_split_declaration = saved
            self.assertIn("is not the published", message or "nothing was refused")


@unittest.skipUnless(RECORD.exists(), "the record is made by the script")
class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text())

    def test_no_day_after_the_compared_days(self):
        for horizon, section in self.record["horizons"].items():
            self.assertLessEqual(section["last"], LAST_COMPARED, horizon)

    def test_the_record_reproduces_the_published_brier_exactly(self):
        for horizon, section in self.record["horizons"].items():
            published = json.loads((REPO / "docs" / "runs" / f"pressure_model_v1_h{horizon}.json").read_text())
            self.assertTrue(section["reproduces_published_record"], horizon)
            for tau, pair in section["reproduces_published_record"].items():
                self.assertEqual(pair["published"], published["metrics"]["by_tau"][tau]["brier"])
                self.assertAlmostEqual(pair["walk"], pair["published"], places=12)

    def test_it_is_on_the_published_panel(self):
        manifest = json.loads((REPO / "metadata" / "funding_panel_manifest.json").read_text())
        self.assertEqual(self.record["panel_sha256"], manifest["sha256"])

    def test_it_decides_nothing(self):
        self.assertEqual(self.record["decides"], "nothing")

    def test_every_threshold_carries_its_event_count(self):
        for section in self.record["horizons"].values():
            for tau, entry in section["by_threshold"].items():
                self.assertIn("events", entry, tau)


if __name__ == "__main__":
    unittest.main()
