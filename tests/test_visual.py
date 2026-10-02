"""The visual layer (directive 06): `scripts/emit_visual.py`, `site/`, `docs/visual/`.

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

    def test_no_run_record_is_read(self):
        """No figure from a run record: no input under docs/runs/, and no record chapter yet."""
        self.assertEqual(emit_visual.MODEL_RECORDS, ())
        for rel, data in self.outputs.items():
            if rel.endswith(".json"):
                for path in json.loads(data)["provenance"]["inputs"]:
                    self.assertFalse(path.startswith("docs/runs"), path)

    def test_commit_stamp_is_the_latest_input_commit(self):
        shallow = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--is-shallow-repository"],
                                 capture_output=True, text=True).stdout.strip()
        if shallow != "false":
            self.skipTest("a shallow clone cannot read which commit last changed an input")
        self.assertEqual(committed_commit(), emit_visual.input_commit(ROOT),
                         "an input changed after the page was generated: run `python3 scripts/emit_visual.py` "
                         "in a commit after the change")


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
