"""The visual layer (directive 06, #118): `scripts/emit_visual.py`, `site/`, `docs/visual/`.

The page is generated, never edited: these tests regenerate it from the PR's
tree and compare bytes, refuse an unfilled placeholder or an unsourced
annotation, and pin the two guards the generator carries.

Each guard carries one recorded mutation, applied to `scripts/emit_visual.py`
and run with `PYTHONPATH=src:tests python3 -m unittest test_visual.<Class>`:
the mutated line, and what the test then raised.
"""

import copy
import csv
import importlib.util
import json
import re
import subprocess
import unittest
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("emit_visual", ROOT / "scripts" / "emit_visual.py")
emit_visual = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(emit_visual)

PRE_AS_OF = ROOT / "docs/runs/archive/pre-asof/backtest_gbm_arx_declared_conformal_mh61.json"
AS_OF = ROOT / "docs/runs/persistence_funding.json"


def committed_commit():
    doc = json.loads((ROOT / emit_visual.DATA_DIR / "history.json").read_text(encoding="utf-8"))
    return doc["provenance"]["commit"]


class RegenerationTests(unittest.TestCase):
    """The committed page and data are exactly what the generator produces."""

    @classmethod
    def setUpClass(cls):
        cls.outputs = emit_visual.generate(ROOT, committed_commit())

    def test_regeneration_reproduces_committed_files_byte_for_byte(self):
        for rel, data in self.outputs.items():
            with self.subTest(path=rel):
                self.assertTrue((ROOT / rel).exists(), f"{rel} is not committed")
                self.assertEqual((ROOT / rel).read_bytes(), data,
                                 f"{rel} is stale: run `python3 scripts/emit_visual.py`")

    def test_no_stray_data_files(self):
        committed = {f"{emit_visual.DATA_DIR}/{p.name}" for p in (ROOT / emit_visual.DATA_DIR).glob("*.json")}
        self.assertEqual(committed, {rel for rel in self.outputs if rel.startswith(emit_visual.DATA_DIR)})

    def test_every_data_file_carries_provenance(self):
        for rel, data in self.outputs.items():
            if not rel.endswith(".json"):
                continue
            with self.subTest(path=rel):
                prov = json.loads(data)["provenance"]
                self.assertRegex(prov["commit"], r"^[0-9a-f]{40}$")
                manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
                self.assertEqual(prov["panel"]["sha256"], manifest["sha256"])
                self.assertTrue(prov["inputs"])

    def test_only_the_model_data_reads_run_records(self):
        """The descriptive chapters read no run record; the model chapters read nothing else."""
        for rel, data in self.outputs.items():
            if not rel.endswith(".json"):
                continue
            inputs = json.loads(data)["provenance"]["inputs"]
            with self.subTest(path=rel):
                if rel == f"{emit_visual.DATA_DIR}/model.json":
                    self.assertTrue(inputs)
                    for path in inputs:
                        self.assertTrue(emit_visual.is_published_record(path), path)
                else:
                    for path in inputs:
                        self.assertFalse(path.startswith("docs/runs"), path)

    def test_commit_stamp_is_the_latest_input_commit(self):
        shallow = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--is-shallow-repository"],
                                 capture_output=True, text=True).stdout.strip()
        if shallow != "false":
            self.skipTest("a shallow clone cannot read which commit last changed an input")
        self.assertEqual(committed_commit(), emit_visual.input_commit(ROOT),
                         "an input changed after the page was generated: run `python3 scripts/emit_visual.py` "
                         "in a commit after the change")


def published_records():
    return emit_visual.run_records(ROOT)


class ModelChapterTests(unittest.TestCase):
    """Chapters 5 to 7 (#118): every figure comes from a published record in docs/runs/."""

    @classmethod
    def setUpClass(cls):
        cls.records = published_records()
        thresholds = json.loads((ROOT / emit_visual.THRESHOLDS).read_text(encoding="utf-8"))
        cls.taus = thresholds["taus_bp"][:2]
        cls.data, cls.fills = emit_visual.model_chapters(cls.records, cls.taus)
        cls.model = json.loads((ROOT / emit_visual.DATA_DIR / "model.json").read_text(encoding="utf-8"))

    def test_every_figure_names_a_published_record_and_its_checksum(self):
        inputs = self.model["provenance"]["inputs"]
        self.assertTrue(self.data["models"])
        for entry in self.data["models"]:
            with self.subTest(record=entry["record"]):
                self.assertTrue(emit_visual.is_published_record(entry["record"]))
                self.assertEqual(inputs[entry["record"]], emit_visual.sha256(ROOT / entry["record"]))

    def test_every_exceedance_record_is_drawn(self):
        drawn = {entry["record"] for entry in self.data["models"]}
        on_disk = {f"docs/runs/{p.name}" for p in (ROOT / "docs/runs").glob("exceedance_*.json")}
        self.assertEqual(drawn, on_disk)

    def test_figures_are_the_records_values(self):
        for entry in self.data["models"]:
            record = self.records[entry["record"]]
            for tau in self.taus:
                key = f"{tau:g}"
                row = record["metrics"]["by_tau"][key]
                drawn = entry["by_tau"][key]
                with self.subTest(record=entry["record"], tau=key):
                    self.assertEqual(drawn["brier"], row["brier"])
                    self.assertEqual(drawn["base_rate"], row["base_rate"])
                    self.assertEqual(drawn["reliability"], row["decomposition"]["reliability"])
                    for name, paired in drawn["vs"].items():
                        source = record["benchmarks"][name]["by_tau"][key]["paired_brier_difference"]
                        self.assertEqual(paired["mean"], source["mean"])
                        self.assertEqual(paired["lower"], source["interval"]["lower"])
                        self.assertEqual(paired["upper"], source["interval"]["upper"])

    def test_scored_models_face_both_benchmarks(self):
        scored = [e for e in self.data["models"] if not e["benchmark"]]
        self.assertTrue(scored)
        for entry in scored:
            for tau in self.taus:
                self.assertEqual(set(entry["by_tau"][f"{tau:g}"]["vs"]),
                                 {name for name, _ in emit_visual.BENCHMARKS})

    def test_headline_thresholds_only(self):
        self.assertEqual(self.data["taus"], [f"{tau:g}" for tau in self.taus])

    def test_placeholders_are_generated_not_typed(self):
        page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")
        template = (ROOT / emit_visual.TEMPLATE).read_text(encoding="utf-8")
        for key, _, what in emit_visual.PENDING:
            with self.subTest(pending=key):
                self.assertIn(what, page)
                self.assertNotIn(what, template)


class FigureWithoutRecordTests(unittest.TestCase):
    """The generator refuses a model figure that no published record carries.

    Recorded mutation: in `from_record`, `if rel not in records:` -> `if False:`.
    test_absent_record_refused then errored with KeyError:
    'docs/runs/exceedance_absent.json', not the VisualError the guard raises. A
    second, `if not is_published_record(rel):` -> `if False:`, failed both
    subtests of test_record_outside_docs_runs_refused with AssertionError:
    VisualError not raised.
    """

    def setUp(self):
        self.records = copy.deepcopy(published_records())

    def test_absent_record_refused(self):
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.from_record(self.records, "docs/runs/exceedance_absent.json", "metrics")

    def test_missing_benchmark_refused(self):
        rel = "docs/runs/exceedance_gbm.json"
        del self.records[rel]["benchmarks"]["persistence_logistic"]
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.model_chapters(self.records, [5.0, 10.0])

    def test_missing_threshold_refused(self):
        rel = "docs/runs/exceedance_gbm.json"
        del self.records[rel]["metrics"]["by_tau"]["10"]
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.model_chapters(self.records, [5.0, 10.0])

    def test_record_outside_docs_runs_refused(self):
        for rel in ("docs/runs/archive/pre-asof/exceedance_gbm.json", "scratch/exceedance_gbm.json"):
            with self.subTest(rel=rel), self.assertRaises(emit_visual.VisualError):
                emit_visual.from_record({rel: self.records["docs/runs/exceedance_gbm.json"]}, rel, "metrics")

    def test_no_exceedance_record_refused(self):
        records = {rel: r for rel, r in self.records.items() if "exceedance_" not in rel}
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.model_chapters(records, [5.0, 10.0])

    def test_pre_as_of_exceedance_record_refused(self):
        self.records["docs/runs/exceedance_gbm.json"]["derived"]["information_set"]["rule"] = "purge"
        with self.assertRaises(LookAheadError):
            emit_visual.model_chapters(self.records, [5.0, 10.0])


class PendingFigureTests(unittest.TestCase):
    """A chapter whose record is not published shows a generated placeholder, and only then.

    Recorded mutation: in `pending_figures`, `if carriers:` -> `if False:`.
    test_record_carrying_lead_time_refused and
    test_record_carrying_scarcity_state_refused then failed with
    AssertionError: VisualError not raised.
    """

    def test_published_records_leave_both_placeholders(self):
        found = emit_visual.pending_figures(published_records())
        self.assertEqual(set(found), {key for key, _, _ in emit_visual.PENDING})

    def test_record_carrying_lead_time_refused(self):
        records = published_records()
        records["docs/runs/pressure_model.json"] = {"metrics": {"lead_time": {"5": 2}}}
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.pending_figures(records)

    def test_record_carrying_scarcity_state_refused(self):
        records = published_records()
        records["docs/runs/pressure_model.json"] = {"declaration": {"features": ["reserve_scarcity_state"]}}
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.pending_figures(records)


class PageTests(unittest.TestCase):
    page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")

    def test_no_unfilled_placeholders(self):
        self.assertEqual(re.findall(r"\{\{\w+\}\}", self.page), [])
        self.assertNotIn("/*__DATA__*/null", self.page)

    def test_fill_refuses_a_placeholder_left_over(self):
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.fill("<p>{{known}} and {{unknown}}</p>", {"known": "x"})

    def test_external_resources_are_only_the_pinned_ones(self):
        found = set(re.findall(r'(?:src|href)="(https://[^"]+)"', self.page.split("<body>")[0]))
        self.assertEqual(found, {
            "https://fonts.googleapis.com",
            "https://fonts.gstatic.com",
            "https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap",
            "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js",
        })

    def test_every_chart_has_an_aria_label(self):
        template = (ROOT / emit_visual.TEMPLATE).read_text(encoding="utf-8")
        statements = re.findall(r'append\("svg"\)[^;]*;', template)
        self.assertTrue(statements)
        for statement in statements:
            self.assertIn('"aria-label"', statement)
            self.assertIn('.attr("role", "img")', statement)


class AnnotationTests(unittest.TestCase):
    notes = json.loads((ROOT / emit_visual.ANNOTATIONS).read_text(encoding="utf-8"))

    def test_every_annotation_has_a_source_url(self):
        emit_visual.check_annotations(self.notes)
        broken = copy.deepcopy(self.notes)
        broken["claims"]["quarter_end"]["src"] = ""
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.check_annotations(broken)

    def test_metadata_carries_no_annotations(self):
        for path in (ROOT / "metadata").glob("*.json"):
            self.assertNotIn("annotations", path.read_text(encoding="utf-8"), path.name)

    def test_implementation_note_matches_its_checksum(self):
        meta = self.notes["implementation_note"]
        self.assertEqual(emit_visual.sha256(ROOT / meta["path"]), meta["sha256"])


class ReserveUnitGuardTests(unittest.TestCase):
    """The reserve-unit guard fires on a rescaled panel.

    Recorded mutation: `if low < RESERVE_BILLIONS[0] or high >= RESERVE_BILLIONS[1]:`
    -> `if False:`. test_millions_refused and test_trillions_refused then failed
    with AssertionError: VisualError not raised.
    """

    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
        cls.rows = list(csv.DictReader(raw.decode().splitlines()))

    def rescaled(self, factor):
        rows = copy.deepcopy(self.rows)
        for r in rows:
            r["reserve_balances"] = str(float(r["reserve_balances"]) * factor)
        return rows

    def test_published_panel_passes(self):
        emit_visual.check_reserve_units(self.rows)

    def test_millions_refused(self):
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.check_reserve_units(self.rescaled(1e3))

    def test_trillions_refused(self):
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.check_reserve_units(self.rescaled(1e-3))


class FailClosedGateTests(unittest.TestCase):
    """A model chapter renders only records that declare the as-of information rule.

    Recorded mutation: `if not found:` -> `if False:` in `require_as_of`.
    test_pre_as_of_record_refused then failed with AssertionError:
    LookAheadError not raised. A second, `if other:` -> `if False:`, failed
    test_other_rule_refused the same way.
    """

    def test_pre_as_of_record_refused(self):
        with self.assertRaises(LookAheadError):
            emit_visual.load_run_record(PRE_AS_OF)

    def test_other_rule_refused(self):
        record = json.loads(AS_OF.read_text(encoding="utf-8"))
        record["derived"]["information_set"]["rule"] = "purge"
        with self.assertRaises(LookAheadError):
            emit_visual.require_as_of(record)

    def test_as_of_record_accepted(self):
        emit_visual.load_run_record(AS_OF)


if __name__ == "__main__":
    unittest.main()
