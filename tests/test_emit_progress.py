"""The progress page `scripts/emit_progress.py` builds from committed evidence (#637; H5 and H9 progress).

It reads figures that are already in `docs/pivot/evidence/` and the candidate files; it scores nothing. A figure
the evidence does not hold is printed as "not measured", never computed here. `--check` refuses a stale page.

Recorded mutations (run on the tests below, then restored):

* `read_ordinary` returning the lead-1 AUROC where the evidence has none, instead of None: `test_missing_figure_is_not_measured`
  failed with AssertionError.
* `render` printing a figure for a candidate the evidence does not name (iterating the candidate files, not the
  evidence): `test_candidate_without_evidence_is_counted_not_tabled` failed with AssertionError.
* `check` comparing only the Markdown page and not the data file: `test_check_fails_on_a_stale_data_file` failed
  with AssertionError.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("emit_progress", ROOT / "scripts" / "emit_progress.py")
emit_progress = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(emit_progress)

NM = emit_progress.NOT_MEASURED


def write(root, rel, obj):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(obj if isinstance(obj, str) else json.dumps(obj))


def group(mean, lo=None, hi=None, days=10):
    return {"days": days, "mean": mean, "interval": None if lo is None else [lo, hi]}


def fixture(root):
    """Three candidates: `a` has every figure, `b` only an ordinary-day AUROC, `c` no evidence at all."""
    for name in ("a", "b", "c"):
        write(root, "metadata/pressure_judge/candidates/%s.json" % name, {"role": "candidate"})
    write(root, "metadata/spread_distribution_900.json", {"variants": {"a": {}}})
    paired = {"pooled": group(0.4, 0.1, 0.8, 100), "regime": {"2018-19": group(1.5, 0.5, 2.0, 40)},
              "day_type": {"ordinary": group(0.2, -0.1, 0.5, 60)}}
    write(root, "docs/pivot/evidence/spread-distribution/distribution.json", {
        "declaration": "metadata/spread_distribution_900.json", "levels": [0.5],
        "horizons": {"1": {"a": {"days": 100, "first": "2018-06-29", "last": "2025-12-31",
                                 "variant": {"crps_bps": 1.0, "mae_median_bps": 1.2},
                                 "as_of_persistence": {"crps_bps": 1.4, "mae_median_bps": 1.5},
                                 "paired": {"as_of_persistence": paired, "published_distribution": paired},
                                 "mae_median": {"as_of_persistence": paired, "published_distribution": paired}}}}})
    lead = {"auroc": 0.8, "auroc_interval": [0.7, 0.9], "reliability": {"slope": 0.9, "intercept": 0.0},
            "slope_interval": [0.6, 1.1], "days": 50, "events": 5}
    write(root, "docs/pivot/evidence/spread-distribution/ordinary.json", {"rows": {
        "a": {"leads": {"1": lead}, "pooled": {"auroc": 0.75, "days": 90, "events": 9}},
        "b": {"leads": {"1": {"auroc": 0.5}}, "pooled": {"auroc": 0.5}}}})
    write(root, "docs/pivot/evidence/spread-distribution/compare.json", {"calibration": {
        "a": {"all": {"days": 9.0, "predicted": 0.05, "realised": 0.07},
              "regime 2018-19": {"days": 3.0, "predicted": 0.2, "realised": 0.27}}}})
    brier = {"1": {"all": {"days": 10, "vs_climatology": {"mean": 0.006, "interval": {"lower": 0.003, "upper": 0.009}}},
                   "regime 2018-19": {"days": 5, "vs_climatology": {"mean": 0.01, "interval": {"lower": 0.0, "upper": 0.02}}}}}
    write(root, "docs/pivot/evidence/all-inputs/compare.json", {"brier": {"a": brier}})
    verdict = {"tier_1_onset_warning": True, "tier_3_no_crying_wolf": False, "tier_5_week_ahead": True, "passes": False}
    write(root, "docs/pivot/evidence/weighted-miss/tier1.json", {"weighted": {"a": {"verdict": verdict}}})


class ReaderTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        fixture(self.root)
        self.model = emit_progress.build(self.root, order=["a", "b", "c"])

    def tearDown(self):
        self.tmp.cleanup()

    def row(self, name):
        return next(r for r in self.model["candidates"] if r["name"] == name)

    def test_full_candidate_carries_every_figure(self):
        a = self.row("a")
        self.assertEqual(a["position"], 1)
        self.assertEqual(a["ordinary"]["pooled_auroc"], 0.75)
        self.assertEqual(a["ordinary"]["lead_1"]["auroc_interval"], [0.7, 0.9])
        self.assertEqual(a["brier"]["pooled"]["mean"], 0.006)
        self.assertEqual(a["brier"]["pooled"]["interval"], [0.003, 0.009])
        self.assertEqual(a["calibration"]["regime 2018-19"]["realised"], 0.27)
        self.assertEqual(a["tiers"], {"tier_1": True, "tier_3": False, "tier_5": True})
        self.assertEqual(a["spread"]["1"]["crps_difference_vs_persistence"]["pooled"]["mean"], 0.4)

    def test_missing_figure_is_not_measured(self):
        b = self.row("b")
        self.assertIsNone(b["ordinary"]["lead_1"]["auroc_interval"])
        self.assertIsNone(b["brier"])
        self.assertIsNone(b["calibration"])
        self.assertIsNone(b["tiers"])
        text = emit_progress.render(self.model)
        self.assertIn(NM, text)

    def test_candidate_without_evidence_is_counted_not_tabled(self):
        self.assertEqual(self.model["variant_count"]["candidate_files"], 3)
        self.assertEqual(self.model["variant_count"]["without_evidence"], ["c"])
        self.assertNotIn("c", [r["name"] for r in self.model["candidates"]])

    def test_spread_declarations_are_counted(self):
        self.assertEqual(self.model["variant_count"]["spread_declarations"], 1)
        self.assertEqual(self.model["variant_count"]["spread_variants"], 1)

    def test_every_figure_is_labelled_development(self):
        self.assertIn("development, not a verdict", emit_progress.render(self.model))
        self.assertEqual(self.model["label"], "development, not a verdict")


class CheckTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_passes_after_write_and_fails_on_a_stale_page(self):
        emit_progress.write_outputs(self.root, order=["a", "b", "c"])
        self.assertEqual(emit_progress.check(self.root, order=["a", "b", "c"]), [])
        page = self.root / emit_progress.PAGE
        page.write_text(page.read_text() + "\nhand edit\n")
        self.assertTrue(emit_progress.check(self.root, order=["a", "b", "c"]))

    def test_check_fails_on_a_stale_data_file(self):
        emit_progress.write_outputs(self.root, order=["a", "b", "c"])
        data = self.root / emit_progress.DATA
        data.write_text(data.read_text().replace('"a"', '"z"', 1))
        self.assertTrue(emit_progress.check(self.root, order=["a", "b", "c"]))

    def test_check_fails_when_evidence_changes(self):
        emit_progress.write_outputs(self.root, order=["a", "b", "c"])
        write(self.root, "docs/pivot/evidence/weighted-miss/tier1.json", {"weighted": {}})
        self.assertTrue(emit_progress.check(self.root, order=["a", "b", "c"]))


class RepositoryTest(unittest.TestCase):

    def test_committed_page_is_current(self):
        import subprocess
        if subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--is-shallow-repository"],
                          capture_output=True, text=True).stdout.strip() != "false":
            self.skipTest("a shallow clone cannot order the candidate files")
        self.assertEqual(emit_progress.check(ROOT), [])

    def test_page_is_linked_from_next_session(self):
        text = (ROOT / "docs" / "pivot" / "next-session.md").read_text()
        self.assertIn("progress.md", text)


if __name__ == "__main__":
    unittest.main()
