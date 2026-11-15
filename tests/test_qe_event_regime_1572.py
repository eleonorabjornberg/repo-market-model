"""`scripts/qe_event_regime_1572.py` (#1572; H5 step 3, development tier): #1548's quarter-end arm by regime of the event, from the same walk.

What these tests pin: the regime an event belongs to (the declared regime of its quarter-end's calendar date), the partition of the group's cells into
quarter-end turns and year-ends and into regimes (every cell in exactly one cell of the table, no cell dropped or counted twice), the event and cell counts
of a table cell, the "few events" flag, the reproduction check against #1548's record, the table's reproduction of the page's figures (+0.001 group CRPS;
0.586 to 0.668 on the 22 turns; +0.416 twCRPS on the 8 year-ends), and that the tracked page is what the scripts render from the tracked records.

Recorded mutation (the reproduction check, `reproduce`): the comparison `abs(a - b) > TOLERANCE` was changed to `abs(a - b) > 1.0`.
`ReproductionTests.test_a_figure_that_differs_from_1548s_record_is_refused` then failed with `AssertionError` (no `ValueError` was raised); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("qe_event_regime_1572", ROOT / "scripts" / "qe_event_regime_1572.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["qe_event_regime_1572"] = script
_spec.loader.exec_module(script)

RECORD_1548 = ROOT / "docs" / "research" / "qe-event-model-1548" / "result.json"
RECORD = ROOT / "docs" / "research" / "qe-event-regime-1572" / "result.json"
PAGE = ROOT / "docs" / "research" / "qe-event-model-1548-result.md"


def cell(event, h, kind, cand=0.0, arm=0.0):
    vec = [1.0, 0.0, 0.0, 0.0, 0.0, cand, cand] + [1.0, 0.0, 0.0, 0.0, 0.0, arm, arm]
    vec += [b - a for a, b in zip(vec[:7], vec[7:14])]
    return {"event": event, "h": h, "type": kind, "qe1363": True, "in_group": True, "vec": vec}


class PartitionTests(unittest.TestCase):

    def test_an_event_belongs_to_the_regime_of_its_quarter_end_date(self):
        self.assertEqual(script.regime_of_event("2019-12", script.SPLITS), "2018-19")
        self.assertEqual(script.regime_of_event("2020-03", script.SPLITS), "2020")
        self.assertEqual(script.regime_of_event("2023-12", script.SPLITS), "2021-23")
        self.assertEqual(script.regime_of_event("2025-12", script.SPLITS), "2025-26")

    def test_every_cell_is_in_one_scope_cell_and_one_regime_cell(self):
        cells = [cell("2019-03", 1, "quarter_end_turn"), cell("2019-03", 2, "quarter_end_turn"), cell("2019-12", 1, "year_end"),
                 cell("2020-06", 1, "quarter_end_turn"), cell("2024-12", 3, "year_end")]
        table = script.regime_table(cells, script.SPLITS, reps=20)
        self.assertEqual(table["group"]["all"]["cells"], 5)
        for scope in ("group", "quarter_end_turn", "year_end"):
            parts = [v for k, v in table[scope].items() if k != "all" and v is not None]
            self.assertEqual(sum(p["cells"] for p in parts), table[scope]["all"]["cells"], scope)
            self.assertEqual(sum(p["events"] for p in parts), table[scope]["all"]["events"], scope)
        self.assertEqual(table["quarter_end_turn"]["all"]["events"], 2)
        self.assertEqual(table["year_end"]["all"]["events"], 2)
        self.assertEqual(table["year_end"]["2018-19"]["cells"], 1)
        self.assertIsNone(table["year_end"]["2020"])

    def test_a_cell_resting_on_few_events_is_flagged(self):
        self.assertTrue(script.few_events({"events": 2}))
        self.assertTrue(script.few_events({"events": script.FEW - 1}))
        self.assertFalse(script.few_events({"events": script.FEW}))


class ReproductionTests(unittest.TestCase):

    def test_a_figure_that_differs_from_1548s_record_is_refused(self):
        record = json.loads(RECORD_1548.read_text(encoding="utf-8"))
        group = json.loads(json.dumps(record["windows"]["development"]["group"]))
        rows = {"group": {"all": group["pooled"]}, "quarter_end_turn": {"all": group["by_type"]["quarter_end_turn"]},
                "year_end": {"all": group["by_type"]["year_end"]}}
        script.reproduce(rows, group)
        rows["year_end"]["all"] = json.loads(json.dumps(rows["year_end"]["all"]))
        rows["year_end"]["all"]["measures"]["grid_crps"]["diff"] += 0.01
        with self.assertRaises(ValueError):
            script.reproduce(rows, group)


class CommittedRecordTests(unittest.TestCase):

    def setUp(self):
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.theirs = json.loads(RECORD_1548.read_text(encoding="utf-8"))

    def test_the_table_reproduces_the_pages_pooled_and_group_figures(self):
        dev = self.record["windows"]["development"]["table"]
        crps = dev["group"]["all"]["measures"]["grid_crps"]
        self.assertAlmostEqual(crps["diff"], 0.001, places=3)
        turns = dev["quarter_end_turn"]["all"]
        self.assertEqual(turns["events"], 22)
        self.assertAlmostEqual(turns["measures"]["cover90"]["candidate"], 0.586, places=3)
        self.assertAlmostEqual(turns["measures"]["cover90"]["arm"], 0.668, places=3)
        years = dev["year_end"]["all"]
        self.assertEqual(years["events"], 8)
        self.assertAlmostEqual(years["measures"]["upper_tail_twcrps"]["diff"], 0.416, places=3)
        for window, w in self.record["windows"].items():
            script.reproduce(w["table"], self.theirs["windows"][window]["group"])

    def test_the_regime_cells_partition_the_group(self):
        for w in self.record["windows"].values():
            for scope, row in w["table"].items():
                parts = [v for k, v in row.items() if k != "all" and v is not None]
                self.assertEqual(sum(p["cells"] for p in parts), row["all"]["cells"], scope)

    def test_the_record_is_the_full_run_on_the_published_panel(self):
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIn(self.record["panel_sha256"], json.dumps(manifest))
        self.assertEqual(self.record["panel_sha256"], self.theirs["panel_sha256"])
        self.assertIsNone(self.record["subset_from"])
        self.assertEqual((self.record["seed"], self.record["event_reps"]), (self.theirs["seed"], self.theirs["event_reps"]))

    def test_the_tracked_page_is_what_the_scripts_render_from_the_tracked_records(self):
        self.assertEqual(PAGE.read_text(encoding="utf-8"), script.full_page(self.theirs, self.record))

    def test_the_page_says_the_kill_stays_and_does_not_call_the_2026_arm_killed(self):
        text = PAGE.read_text(encoding="utf-8")
        self.assertIn("The kill stays as declared", text)
        i = text.index("## The 2026 development days")
        j = text.index("### The event pools", i)
        self.assertNotIn("killed", text[i:j])
        self.assertIn("+0.187 [-0.418, +0.595]", text[i:j])
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """A small run on the fixture panel with the walk started late and few resamples: the shape, not the figures."""

    FIRST = "2025-09-02"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.held = sys.modules.get("qe_event_model_1548")
        sys.modules["qe_event_model_1548"] = script.m1548  # another test module may have registered its own copy; the worker pool pickles by module name
        cls.tmp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.tmp.name) / "result.json"
        script.main(["score", "--panel", str(panel_cache.published_build()["path"]), "--output", str(cls.output), "--event-reps", "20", "--first", cls.FIRST])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
        if cls.held is not None:
            sys.modules["qe_event_model_1548"] = cls.held

    def test_both_windows_carry_the_three_scopes_and_every_regime(self):
        self.assertEqual(sorted(self.result["windows"]), ["2026", "development"])
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["table"]), ["group", "quarter_end_turn", "year_end"])
            for row in w["table"].values():
                self.assertEqual(sorted(k for k in row if k != "all"), sorted(script.REGIMES))

    def test_the_subset_is_not_checked_against_1548s_full_record(self):
        self.assertEqual(self.result["reproduction"], "not checked: a subset run")


if __name__ == "__main__":
    unittest.main()
