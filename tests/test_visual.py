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

from repo_model import lockbox
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


class HeldOutDayTests(unittest.TestCase):
    """Locked days are drawn greyed and counted nowhere (#141 ruling 3, #182).

    The tiers are read from `metadata/lockbox.json` through
    `repo_model.lockbox.locked_tiers`; a tier marked opened is ordinary history.

    Recorded mutation: `return [r for r in rows if locked_tier(...) is None]`
    -> `return list(rows)` in `counted`. Every test below except
    test_the_panel_reaches_a_locked_tier then failed with AssertionError,
    among them test_no_counted_day_is_locked (the 2026 days were counted) and
    test_perturbing_a_locked_day_changes_no_count_or_sentence ("111 days"
    became "238 days").
    """

    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
        cls.rows = list(csv.DictReader(raw.decode().splitlines()))
        cls.inputs = [emit_visual.read_json(rel, ROOT) for rel in
                      (emit_visual.ANNOTATIONS, emit_visual.THRESHOLDS)]
        cls.inputs += [emit_visual.read_json(emit_visual.SPLITS, ROOT)["regimes"],
                       emit_visual.read_json(emit_visual.EVENTS, ROOT)["windows"]]
        cls.locked = lockbox.locked_tiers(ROOT / emit_visual.LOCKBOX)
        cls.page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")

    def history(self, rows, locked):
        return emit_visual.history(copy.deepcopy(rows), *self.inputs, locked)

    def is_locked(self, row, locked):
        return lockbox.locked_tier(emit_visual.date.fromisoformat(row["date"]), locked) is not None

    def opened(self):
        document = json.loads((ROOT / emit_visual.LOCKBOX).read_text(encoding="utf-8"))
        for tier in document["tiers"]:
            tier["opened"] = {"date": "2026-10-02", "ruling": "a test fixture standing in for her ruling"}
        import tempfile
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "lockbox.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return lockbox.locked_tiers(path)

    @staticmethod
    def table_counts(table):
        """[(pressure days, days)] for every cell of the day-type x year table that carries counts."""
        return [(int(k), int(n)) for k, n in re.findall(r"<b>(\d+)</b><span> of (\d+)</span>", table)]

    def test_the_panel_reaches_a_locked_tier(self):
        """Otherwise the tests below would hold vacuously."""
        self.assertTrue(any(self.is_locked(r, self.locked) for r in self.rows))

    def test_no_counted_day_is_locked(self):
        kept = emit_visual.counted(self.rows, self.locked)
        self.assertFalse([r["date"] for r in kept if self.is_locked(r, self.locked)])
        self.assertEqual(len(kept), sum(1 for r in self.rows if not self.is_locked(r, self.locked)))
        data, fills = self.history(self.rows, self.locked)
        self.assertEqual(sum(n for _, n in self.table_counts(fills["heat_table"])), len(kept))
        held = {r["date"] for r in self.rows if self.is_locked(r, self.locked)}
        spans = data["held_out"]
        self.assertTrue(spans)
        self.assertTrue(all(any(s["start"] <= d <= s["end"] for s in spans) for d in held))

    def test_perturbing_a_locked_day_changes_no_count_or_sentence(self):
        """Every held-out day made a far-off-scale spike on scarce reserves: no figure or sentence moves."""
        perturbed = copy.deepcopy(self.rows)
        for r in perturbed:
            if self.is_locked(r, self.locked):
                r["sofr"] = str(float(r["sofr"]) + 1.0)
                r["reserve_balances"] = str(float(r["reserve_balances"]) / 2)
                r["sofr_p25"] = r["sofr_p75"] = ""
        base, fills = self.history(self.rows, self.locked)
        moved, moved_fills = self.history(perturbed, self.locked)
        self.assertEqual(fills, moved_fills)
        drawn = ("rows", "views", "res_domain")
        self.assertEqual({k: v for k, v in base.items() if k not in drawn},
                         {k: v for k, v in moved.items() if k not in drawn})
        self.assertEqual(emit_visual.counted(self.rows, self.locked)[-1],
                         emit_visual.counted(perturbed, self.locked)[-1])

    def test_opening_the_tier_brings_the_days_back(self):
        opened = self.opened()
        self.assertEqual(opened, ())
        self.assertEqual(len(emit_visual.counted(self.rows, opened)), len(self.rows))
        _, fills = self.history(self.rows, opened)
        _, locked_fills = self.history(self.rows, self.locked)
        self.assertEqual(sum(n for _, n in self.table_counts(fills["heat_table"])), len(self.rows))
        self.assertNotIn("held out", fills["heat_table"])
        self.assertEqual(fills["held_out_note"], "")
        self.assertNotEqual(fills["above_late"], locked_fills["above_late"])
        last_year = self.rows[-1]["date"][:4]
        self.assertIn(f"{last_year} (to ", fills["heat_table"])

    def test_the_held_out_year_is_greyed_without_counts(self):
        _, fills = self.history(self.rows, self.locked)
        held_years = {r["date"][:4] for r in self.rows} - {r["date"][:4] for r in
                                                           emit_visual.counted(self.rows, self.locked)}
        self.assertTrue(held_years)
        for year in held_years:
            self.assertIn(f"<th scope='col' class='held'>{year}<br>held out</th>", fills["heat_table"])

    def test_period_labels_name_only_counted_years(self):
        _, fills = self.history(self.rows, self.locked)
        last_counted_year = max(int(r["date"][:4]) for r in self.rows if not self.is_locked(r, self.locked))
        for key in ("early", "late", "ample"):
            years = [int(y) for y in re.findall(r"\d{4}", fills[key])]
            years += [int(fills[key][:2] + y) for y in re.findall(r"–(\d{2})\b", fills[key])]
            with self.subTest(key=key, label=fills[key]):
                self.assertTrue(all(y <= last_counted_year for y in years))

    def test_the_page_draws_and_captions_the_held_out_days(self):
        self.assertIn("held out", self.page)
        self.assertIn("docs/decisions/lockbox.md", self.page)
        shown = emit_visual.counted(self.rows, self.locked)[-1]["date"]
        self.assertIn(f"Rates on {emit_visual.day(shown)}", self.page)


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
