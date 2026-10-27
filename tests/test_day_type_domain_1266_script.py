"""The helpers of `scripts/day_type_domain_1266.py` (#1266; H5 step 3 reporting, development tier).

Written first. The arithmetic of the studentized domain interval is pinned in `test_studentized_domain_1266`; the walks, the cells and
the reading rule are `s3_terms_1196`'s and `day_type_domain_1228`'s. What these tests pin: the three readings of a cell and the pairs
that change, the tally by pair, that a studentized row carries the group mean the current row has, that the tracked page is what the
script renders from the tracked record, that the record is the declared full run and reproduces #1253's record, and a small run of
`score` and `page` end to end on a late subset of the fixture panel.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("day_type_domain_1266", ROOT / "scripts" / "day_type_domain_1266.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["day_type_domain_1266"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


def row(lo, hi, d=0.1):
    return {"difference": d, "difference_interval": [lo, hi], "skill": 0.0, "skill_interval": [lo, hi]}


class CompareTests(unittest.TestCase):

    def test_a_cell_has_three_readings_and_the_pairs_that_change(self):
        cell = script.compare3({"current": row(0.005, 5.3), "percentile": row(-0.4, 5.0), "studentized": row(0.2, 4.0)})
        self.assertEqual(cell["readings"], {"current": "gain", "percentile": "undecided", "studentized": "gain"})
        self.assertEqual(cell["changes"], {"current>percentile": True, "current>studentized": False, "percentile>studentized": True})
        self.assertAlmostEqual(cell["width_ratio_vs_current"], 3.8 / 5.295)
        self.assertAlmostEqual(cell["width_ratio_vs_percentile"], 3.8 / 5.4)

    def test_a_row_without_an_interval_is_no_reading_and_has_no_width(self):
        cell = script.compare3({"current": {"undefined": "x", "days": 20}, "percentile": row(0.2, 1.0), "studentized": row(0.2, 1.0)})
        self.assertEqual(cell["readings"]["current"], "no reading")
        self.assertTrue(cell["changes"]["current>studentized"])
        self.assertIsNone(cell["width_ratio_vs_current"])

    def test_the_tally_counts_by_pair(self):
        cells = [script.compare3({"current": row(0.1, 2.0), "percentile": row(-1.0, 2.0), "studentized": row(0.1, 1.0)}),
                 script.compare3({"current": row(-1.0, 1.0), "percentile": row(-1.0, 1.0), "studentized": row(0.1, 1.0)})]
        tallies = script.tallies(cells)
        self.assertEqual((tallies["current>percentile"]["cells"], tallies["current>percentile"]["changed"]), (2, 1))
        self.assertEqual(tallies["current>studentized"]["changed"], 1)
        self.assertEqual(tallies["percentile>studentized"]["changed"], 2)
        self.assertEqual(tallies["current>studentized"]["matrix"]["undecided"]["gain"], 1)


class StudentizedRows(unittest.TestCase):

    def test_the_row_carries_the_group_mean_and_the_method(self):
        days = [date(2020, 1, 1) + timedelta(days=i) for i in range(300)]
        d = script.ar1(300, 0.4, 0.2, 3)
        bench = {day: 5.0 for day in days}
        cand = {day: 5.0 - d[i] for i, day in enumerate(days)}
        group = days[5::25]
        out = script.studentized_rows({"g": (bench, cand, group)}, days, seed=1266, draws=200)["g"]
        self.assertAlmostEqual(out["difference"], sum(d[i] for i in range(5, 300, 25)) / len(group), places=12)
        self.assertEqual((out["days"], out["method"]), (len(group), "studentized domain"))
        lo, hi = out["difference_interval"]
        self.assertLess(lo, out["difference"])
        self.assertGreater(hi, out["difference"])

    def test_a_group_day_outside_the_series_is_refused(self):
        days = [date(2020, 1, 1) + timedelta(days=i) for i in range(50)]
        flat = {day: 1.0 for day in days}
        with self.assertRaises(ValueError):
            script.studentized_rows({"g": (flat, flat, [date(1999, 1, 1)])}, days, seed=1, draws=20)

    def test_an_unavailable_group_reads_undefined_with_the_reason(self):
        days = [date(2020, 1, 1) + timedelta(days=i) for i in range(50)]
        flat = {day: 1.0 for day in days}
        out = script.studentized_rows({"g": (flat, flat, days[::5])}, days, seed=1, draws=20)["g"]
        self.assertIn("long-run variance", out["undefined"])


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "day-type-domain-1266" / "result.json"
    PAGE = ROOT / "docs" / "research" / "day-type-domain-1266-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_and_reproduces_1243(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual((record["seed"], record["draws"], record["block_length"]), (script.SEED, sp.DRAWS, sp.BLOCK_LENGTH))
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        self.assertEqual(record["reproduces_1243"]["differing_rows"], 0)
        self.assertEqual(record["tally"], script.tallies(record["rows"]))
        self.assertLessEqual(record["notes"]["last_target"], script.t.LAST_DAY.isoformat())
        self.assertEqual(record["declaration"], "metadata/s3_terms_1196.json")

    def test_every_row_has_the_three_intervals_with_one_group_mean(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for r in record["rows"]:
            means = [r[k]["difference"] for k in script.KINDS if "difference" in r[k]]
            for m in means:
                self.assertAlmostEqual(m, means[0], places=9)

    def test_the_record_carries_the_synthetic_coverage_of_all_three(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(set(record["coverage"]["intervals"]), set(script.KINDS))
        self.assertEqual(record["coverage"]["spacing"], 60)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["day_type_domain_1266"] = script
        sys.modules["day_type_domain_1228"] = script.d1228
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

    def test_every_tested_day_type_has_all_three_intervals_for_both_metrics_arms_and_references(self):
        rows = self.result["rows"]
        self.assertTrue(rows)
        for metric in script.METRICS:
            for arm in script.ARMS:
                seen = {r["reference"] for r in rows if r["metric"] == metric and r["arm"] == arm and r["group"] == "calendar_days"}
                self.assertEqual(seen, set(script.t.pair_plan(arm, ())), (metric, arm))
        for r in rows:
            self.assertEqual(r["percentile"].get("method"), "domain")
            self.assertEqual(r["studentized"].get("method"), "studentized domain")
            self.assertGreaterEqual(r["days"], script.t.MIN_GROUP_DAYS)

    def test_the_domain_point_estimates_are_the_group_mean_the_current_row_has(self):
        for r in self.result["rows"]:
            for k in ("percentile", "studentized"):
                if "difference" in r[k] and "difference" in r["current"]:
                    self.assertAlmostEqual(r[k]["difference"], r["current"]["difference"], places=9, msg=r["group"])

    def test_the_run_is_labelled_development_and_a_subset_does_not_claim_to_reproduce_1243(self):
        self.assertEqual(self.result["label"], "development, not a verdict")
        self.assertNotIn("reproduces_1243", self.result)
        self.assertLessEqual(self.result["notes"]["last_target"], script.t.LAST_DAY.isoformat())

    def test_the_page_names_the_three_intervals_and_the_rows_the_ruling_names(self):
        text = self.page.read_text(encoding="utf-8")
        for needle in ("Development data, not a verdict", "Studentized domain", "Percentile domain", "quarter_end", "iorb_window",
                       "#1262", "Every day-type row"):
            self.assertIn(needle, text)
        self.assertEqual(text, script.render(self.result))


class CoverageTests(unittest.TestCase):

    def test_the_coverage_has_the_three_intervals_and_rates_between_zero_and_one(self):
        out = script.coverage(reps=6, n=600, spacing=30, draws=40, workers=2)
        self.assertEqual(set(out["intervals"]), set(script.KINDS))
        for v in out["intervals"].values():
            self.assertTrue(0.0 <= v["lower_bound_covers"] <= 1.0 and 0.0 <= v["interval_covers"] <= 1.0)
            self.assertGreater(v["mean_width"], 0.0)


if __name__ == "__main__":
    unittest.main()
