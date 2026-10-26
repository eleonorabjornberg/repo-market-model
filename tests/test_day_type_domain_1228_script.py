"""The helpers of `scripts/day_type_domain_1228.py` (#1228; H5 step 3 reporting, development tier).

Written first. The arithmetic of the domain interval is pinned in `test_domain_intervals_1228`; the walks, the cells and the reading
rule are `s3_terms_1196`'s (its tests pin them). What these tests pin: how a cell is compared (both readings from the bound on mean
d, whether it changes, the width ratio), the tally, that the page names the quarter-end and IORB-window rows and says the two
intervals differ in two ways, and a small run of `score` and `page` end to end on a late subset of the fixture panel, in which
the point estimate of a domain row is the group mean of the paired difference and the current row is the one `run_pairs` gives.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("day_type_domain_1228", ROOT / "scripts" / "day_type_domain_1228.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["day_type_domain_1228"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


def row(lo, hi, d=0.1):
    return {"difference": d, "difference_interval": [lo, hi], "skill": 0.0, "skill_interval": [lo, hi]}


class CompareTests(unittest.TestCase):

    def test_a_reading_is_taken_from_the_bound_on_mean_d(self):
        self.assertEqual(script.reading(row(0.1, 2.0)), "gain")
        self.assertEqual(script.reading(row(-2.0, -0.1)), "loss")
        self.assertEqual(script.reading(row(-0.1, 2.0)), "undecided")
        self.assertEqual(script.reading({"undefined": "no long-run variance", "days": 20}), "no reading")
        self.assertEqual(script.reading(None), "undecided")

    def test_a_cell_records_both_readings_the_change_and_the_width_ratio(self):
        cell = script.compare(row(0.005, 5.3), row(-0.4, 5.0))
        self.assertEqual((cell["current_reading"], cell["domain_reading"], cell["changes"]), ("gain", "undecided", True))
        self.assertAlmostEqual(cell["width_ratio"], 5.4 / 5.295)
        self.assertAlmostEqual(cell["lower_shift"], -0.405)
        same = script.compare(row(0.1, 2.0), row(0.2, 1.0))
        self.assertFalse(same["changes"])
        none = script.compare({"undefined": "x", "days": 20}, row(0.2, 1.0))
        self.assertEqual((none["current_reading"], none["domain_reading"], none["changes"]), ("no reading", "gain", True))
        self.assertIsNone(none["width_ratio"])

    def test_the_tally_counts_cells_by_current_and_domain_reading(self):
        cells = [script.compare(row(0.1, 2.0), row(-1.0, 2.0)), script.compare(row(0.1, 2.0), row(0.1, 1.0)),
                 script.compare(row(-1.0, 1.0), row(0.1, 1.0))]
        tally = script.tally(cells)
        self.assertEqual((tally["cells"], tally["changed"]), (3, 2))
        self.assertEqual(tally["matrix"]["gain"]["undecided"], 1)
        self.assertEqual(tally["matrix"]["gain"]["gain"], 1)
        self.assertEqual(tally["matrix"]["undecided"]["gain"], 1)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "day-type-domain-1228" / "result.json"
    PAGE = ROOT / "docs" / "research" / "day-type-domain-1228-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_and_reproduces_1196(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual((record["seed"], record["draws"], record["block_length"]), (script.SEED, sp.DRAWS, sp.BLOCK_LENGTH))
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        self.assertEqual(record["reproduces_1196"]["differing_rows"], 0)
        self.assertEqual(record["tally"], script.tally(record["rows"]))
        self.assertLessEqual(record["notes"]["last_target"], script.t.LAST_DAY.isoformat())
        self.assertEqual(record["declaration"], "metadata/s3_terms_1196.json")

    def test_every_row_keeps_the_group_mean_in_both_intervals(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for r in record["rows"]:
            if "difference" in r["current"] and "difference" in r["domain"]:
                self.assertAlmostEqual(r["current"]["difference"], r["domain"]["difference"], places=9)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["day_type_domain_1228"] = script
        sys.modules["s3_terms_1196"] = script.t  # another test module may have re-registered the name (pickling by module name)
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["score", "--draws", "30", "--workers", "2", "--first", cls.FIRST, "--panel", str(cls.panel_path),
                     "--output", str(cls.output)])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_tested_day_type_has_both_intervals_for_both_metrics_arms_and_references(self):
        rows = self.result["rows"]
        self.assertTrue(rows)
        for metric in script.METRICS:
            for arm in script.ARMS:
                seen = {r["reference"] for r in rows if r["metric"] == metric and r["arm"] == arm and r["group"] == "calendar_days"}
                self.assertEqual(seen, set(script.t.pair_plan(arm, ())), (metric, arm))
        for r in rows:
            self.assertEqual(r["domain"].get("method"), "domain")
            self.assertGreaterEqual(r["days"], script.t.MIN_GROUP_DAYS)

    def test_the_domain_point_estimate_is_the_group_mean_the_current_row_has(self):
        for r in self.result["rows"]:
            if "difference" in r["domain"] and "difference" in r["current"]:
                self.assertAlmostEqual(r["domain"]["difference"], r["current"]["difference"], places=9, msg=r["group"])

    def test_the_run_is_labelled_development_and_a_subset_does_not_claim_to_reproduce_1196(self):
        self.assertEqual(self.result["label"], "development, not a verdict")
        self.assertNotIn("reproduces_1196", self.result)
        self.assertLessEqual(self.result["notes"]["last_target"], script.t.LAST_DAY.isoformat())

    def test_the_page_says_what_differs_and_names_the_rows_the_ruling_names(self):
        text = self.page.read_text(encoding="utf-8")
        for needle in ("Development data, not a verdict", "Two things differ at once", "not studentized", "quarter_end", "iorb_window",
                       "#1221", "follow-up directive"):
            self.assertIn(needle, text)
        self.assertEqual(text, script.render(self.result))


if __name__ == "__main__":
    unittest.main()
