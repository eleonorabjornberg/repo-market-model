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
import html
import importlib.util
import json
import re
import subprocess
import unittest
from pathlib import Path

from repo_model import lockbox

from lockbox_support import PRE_OPENING_LOCKBOX
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
        """The descriptive chapters read no run record; the model chapters read nothing else.

        The final test's section (#238) reads its one record and nothing else.

        N4's status engine also reads docs/runs/, but only declarations:
        `run_record_declarations` keeps a record's declaration, its derived
        fields and a comparison's verdict, and nothing else (#141 §3).
        """
        for rel, data in self.outputs.items():
            if not rel.endswith(".json"):
                continue
            inputs = json.loads(data)["provenance"]["inputs"]
            with self.subTest(path=rel):
                if rel == f"{emit_visual.DATA_DIR}/model.json":
                    self.assertTrue(inputs)
                    for path in inputs:
                        self.assertTrue(emit_visual.is_published_record(path), path)
                elif rel == f"{emit_visual.DATA_DIR}/final_test.json":
                    self.assertEqual(set(inputs), {emit_visual.FINAL_TEST})
                elif not rel.endswith("/newcomer_n4.json"):
                    for path in inputs:
                        self.assertFalse(path.startswith("docs/runs"), path)
        for rel, kept in emit_visual.run_record_declarations(ROOT).items():
            with self.subTest(record=rel):
                self.assertLessEqual(set(kept), {"declaration", "derived", "comparison"})
                self.assertLessEqual(set(kept.get("comparison", {})), {"loss", "mean_difference_interval"})

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
    test_record_carrying_lead_time_refused then failed with
    AssertionError: VisualError not raised.
    """

    def test_published_records_leave_the_placeholder(self):
        found = emit_visual.pending_figures(published_records())
        self.assertEqual(set(found), {key for key, _, _ in emit_visual.PENDING})

    def test_record_carrying_lead_time_refused(self):
        records = published_records()
        records["docs/runs/pressure_model.json"] = {"metrics": {"lead_time": {"5": 2}}}
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.pending_figures(records)

    def test_record_carrying_scarcity_state_still_generates(self):
        """The page draws no scarcity chapter, so a record naming the state does not stop it.

        Ruling of 2 October 2026 on #181: "Drop chapter 7 and treat #118's
        scarcity item as superseded by #157." The state is shown only as the
        explorer band (#148), so a record from #117 or #128 that names
        `reserve_scarcity_state`, even as an off input, must not stop the page.
        """
        records = published_records()
        records["docs/runs/pressure_model.json"] = {"declaration": {"features": ["reserve_scarcity_state"]}}
        self.assertNotIn("scarcity", emit_visual.pending_figures(records))
        page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")
        self.assertNotIn('id="scarcity"', page)


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
    Since #151 opened the near-blind tier, the published panel reaches no locked
    day, so these tests read `PRE_OPENING_LOCKBOX` (both tiers locked), and only
    the page itself is checked under the tracked declaration. The mutation below
    was re-run then: every test but test_the_panel_reaches_a_locked_tier and
    test_the_page_draws_and_captions_the_held_out_days failed with AssertionError.

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
        cls.locked = lockbox.locked_tiers(PRE_OPENING_LOCKBOX)
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
        # The page is drawn under the tracked declaration, not the pre-opening one.
        tracked = lockbox.locked_tiers(ROOT / emit_visual.LOCKBOX)
        shown = emit_visual.counted(self.rows, tracked)[-1]["date"]
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



# ---------------------------------------------------------------- the newcomer layer (#141, #142)


def newcomer_block(page):
    """The "Start here" block's HTML, between its two markers."""
    start, end = page.index("<!-- start-here -->"), page.index("<!-- /start-here -->")
    return page[start:end]


def term_uses(block, glossary):
    """Scan the block's text for glossary terms.

    Returns {key: (position of first use, the key of the <dfn> it falls in, or None)}.
    Definitions themselves are left out, and so is every tag other than <dfn>.
    """
    block = re.sub(r"<span class=\"def\"[^>]*>.*?</span><!--/def-->", " ", block, flags=re.S)
    block = re.sub(r"<script.*?</script>", " ", block, flags=re.S)
    text, inside = [], []
    pos = 0
    for m in re.finditer(r"<dfn[^>]*data-term=\"(\w+)\"[^>]*>|</dfn>|<[^>]+>", block):
        chunk = block[pos:m.start()]
        text.append((chunk, inside[-1] if inside else None))
        tag = m.group(0)
        if tag.startswith("<dfn"):
            inside.append(m.group(1))
        elif tag == "</dfn>":
            inside.pop()
        text.append((" ", inside[-1] if inside else None))
        pos = m.end()
    text.append((block[pos:], None))
    flat, owner = "", []
    for chunk, key in text:
        flat += chunk
        owner += [key] * len(chunk)
    found = {}
    for entry in glossary["terms"]:
        hits = [m.start() for pattern in entry["match"] for m in re.finditer(pattern, flat)]
        if hits:
            first = min(hits)
            found[entry["key"]] = (first, owner[first])
    return found


class GlossaryTests(unittest.TestCase):
    glossary = json.loads((ROOT / emit_visual.GLOSSARY).read_text(encoding="utf-8"))

    def test_every_term_has_a_definition_and_a_source(self):
        emit_visual.check_glossary(self.glossary)
        for field, value in (("definition", ""), ("src", ""), ("src", "https://example.com/x")):
            broken = copy.deepcopy(self.glossary)
            broken["terms"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(emit_visual.VisualError):
                emit_visual.check_glossary(broken)

    def test_keys_are_unique(self):
        broken = copy.deepcopy(self.glossary)
        broken["terms"].append(copy.deepcopy(broken["terms"][0]))
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.check_glossary(broken)

    def test_the_plan_terms_are_all_defined(self):
        """#141 §2.6 lists the terms the newcomer layer needs at least."""
        keys = {t["key"] for t in self.glossary["terms"]}
        self.assertLessEqual({"repo", "overnight", "sofr", "iorb", "bp", "reserves", "on_rrp", "tga", "dealer",
                              "money_fund", "triparty", "dvp", "gcf", "srf", "effr", "percentile"}, keys)

    def test_each_term_matches_its_own_printed_form(self):
        for entry in self.glossary["terms"]:
            with self.subTest(term=entry["key"]):
                self.assertTrue(any(re.search(p, entry["text"]) for p in entry["match"]))


class NewcomerPageTests(unittest.TestCase):
    """The "Start here" block: <dfn> at first use, generated nav, no hover-only text."""

    page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")
    glossary = json.loads((ROOT / emit_visual.GLOSSARY).read_text(encoding="utf-8"))

    def test_block_sits_above_the_chapters(self):
        self.assertLess(self.page.index("<!-- start-here -->"), self.page.index('<section id="plumbing">'))

    def test_every_glossary_term_is_a_dfn_at_its_first_use(self):
        uses = term_uses(newcomer_block(self.page), self.glossary)
        self.assertTrue(uses, "the block uses no glossary term")
        for key, (_, owner) in uses.items():
            with self.subTest(term=key):
                self.assertEqual(owner, key, f"the first use of {key!r} is not inside its <dfn>")

    def test_a_term_used_before_its_dfn_is_caught(self):
        block = newcomer_block(self.page)
        first_dfn = block.index("<dfn")
        broken = block[:first_dfn] + "<p>SOFR</p>" + block[first_dfn:]
        uses = term_uses(broken, self.glossary)
        self.assertIsNone(uses["sofr"][1])

    def test_every_dfn_names_a_glossary_term(self):
        keys = {t["key"] for t in self.glossary["terms"]}
        used = set(re.findall(r'<dfn[^>]*data-term="(\w+)"', newcomer_block(self.page)))
        self.assertTrue(used)
        self.assertLessEqual(used, keys)

    def test_definitions_are_not_hover_only(self):
        block = newcomer_block(self.page)
        self.assertNotRegex(block, r"\stitle=")
        for key in set(re.findall(r'<dfn[^>]*data-term="(\w+)"', block)):
            with self.subTest(term=key):
                self.assertRegex(block, rf'<span class="term" role="button" tabindex="0" aria-expanded="false" '
                                        rf'aria-controls="def-{key}"')
                self.assertIn(f'id="def-{key}"', block)

    def test_nav_links_only_to_views_on_the_page_in_reading_order(self):
        block = newcomer_block(self.page)
        nav = re.search(r'<nav aria-label="Start here">(.*?)</nav>', block, re.S).group(1)
        targets = re.findall(r'href="#(n\d)"', nav)
        self.assertTrue(targets)
        self.assertEqual(targets, sorted(targets))
        for target in targets:
            self.assertIn(f'<section id="{target}"', block)
        sections = re.findall(r'<section id="(n\d)"', block)
        self.assertEqual(targets, sections)

    def test_nav_skips_a_view_the_template_does_not_carry(self):
        views = emit_visual.newcomer_nav("<section id=\"n1\"></section>")
        self.assertIn('href="#n1"', views)
        self.assertNotIn('href="#n2"', views)

    def test_zero_line_is_the_rate_on_reserves_not_normal(self):
        template = (ROOT / emit_visual.TEMPLATE).read_text(encoding="utf-8")
        self.assertIn("the Fed's rate on bank reserves", template)
        self.assertNotRegex(newcomer_block(self.page).lower(), r"usual range")

    def test_readme_links_to_start_here_under_the_overview_figure(self):
        """#149: the front door. One link, between the overview figure and the first generated block."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        link = "https://eleonorabjornberg.github.io/repo-market-model/#start"
        self.assertEqual(readme.count(link), 1)
        figure = readme.index('srcset="docs/figures/overview-dark.svg"')
        self.assertLess(readme.index("</picture>", figure), readme.index(link))
        self.assertLess(readme.index(link), readme.index("<!-- generated:"))
        self.assertIn('<div id="start">', newcomer_block(self.page))

    def test_every_static_button_has_an_accessible_name(self):
        for attrs, body in re.findall(r"<button([^>]*)>(.*?)</button>", self.page, re.S):
            with self.subTest(button=attrs):
                name = re.sub(r"<[^>]+>", "", body).strip()
                self.assertTrue(name or "aria-label=" in attrs)


def theme_tokens(template):
    """{"light": {...}, "dark-media": {...}, "dark": {...}}: the colour tokens of each theme block."""
    css = template.split("<style>")[1].split("</style>")[0]
    light = re.search(r":root\{(.*?)\}", css, re.S).group(1)
    media = re.search(r'@media \(prefers-color-scheme: dark\)\{ :root:not\(\[data-theme="light"\]\)\{(.*?)\}', css,
                      re.S).group(1)
    dark = re.search(r':root\[data-theme="dark"\]\{(.*?)\}', css, re.S).group(1)

    def tokens(block):
        return dict(re.findall(r"--([\w-]+):(#[0-9A-Fa-f]{6})", block))

    return {"light": tokens(light), "dark-media": tokens(media), "dark": tokens(dark)}


def contrast(a, b):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


#: Every token that carries text, against every surface it is drawn on.
TEXT_ON = {"ink": ("paper", "panel", "band"), "ink-2": ("paper", "panel", "band"),
           "ink-3": ("paper", "panel", "band"), "sofr": ("paper", "panel", "band"),
           "pressure": ("paper", "panel", "band"), "on-hot": ("pressure",)}


class ThemeTests(unittest.TestCase):
    """Shared by every view: one palette, both themes, WCAG AA contrast, visible focus."""

    template = (ROOT / emit_visual.TEMPLATE).read_text(encoding="utf-8")

    def test_both_themes_define_the_same_tokens(self):
        t = theme_tokens(self.template)
        self.assertEqual(set(t["light"]), set(t["dark"]))
        self.assertEqual(t["dark"], t["dark-media"])

    def test_text_tokens_meet_aa_contrast_in_both_themes(self):
        for theme in ("light", "dark"):
            tokens = theme_tokens(self.template)[theme]
            for fg, surfaces in TEXT_ON.items():
                for bg in surfaces:
                    with self.subTest(theme=theme, fg=fg, bg=bg):
                        self.assertGreaterEqual(contrast(tokens[fg], tokens[bg]), 4.5)

    def test_contrast_check_fails_a_faint_token(self):
        self.assertLess(contrast("#B0B8BE", "#F5F7F6"), 4.5)

    def test_every_control_has_a_visible_focus_style(self):
        rule = re.search(r"([^{}]*):focus-visible[^{}]*\{outline:2px solid", self.template)
        self.assertIsNotNone(rule)
        selectors = re.findall(r"([^{},]+):focus-visible", self.template)
        flat = " ".join(selectors)
        for kind in ("button", "summary", "a", "[tabindex]"):
            with self.subTest(kind=kind):
                self.assertIn(kind, flat)

    def test_reduced_motion_is_honoured(self):
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.template)


class NewcomerHeldOutDayTests(unittest.TestCase):
    """Locked days (`metadata/lockbox.json`) change no count or sentence on the newcomer layer.

    N1 reads the tiers through the same `lockbox.locked_tiers` / `counted` as
    chapters 2 and 3 (`HeldOutDayTests`). Perturbing a locked day's SOFR, up
    past every threshold or down below zero, leaves every generated fill and
    the view's data unchanged; perturbing an unlocked day changes them, so the
    test can see a change.

    Recorded mutation: in `newcomer_n1`, `kept = counted(rows, locked)`
    -> `kept = list(rows)`. test_locked_perturbation_changes_nothing then
    failed with AssertionError (the fills and the counts moved).
    """

    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
        cls.rows = list(csv.DictReader(raw.decode().splitlines()))
        cls.locked = lockbox.locked_tiers(PRE_OPENING_LOCKBOX)
        cls.notes = json.loads((ROOT / emit_visual.ANNOTATIONS).read_text(encoding="utf-8"))
        cls.thresholds = json.loads((ROOT / emit_visual.THRESHOLDS).read_text(encoding="utf-8"))

    def run_n1(self, rows, locked=None):
        locked = self.locked if locked is None else locked
        return emit_visual.newcomer_n1(copy.deepcopy(rows), locked, self.thresholds, self.notes)

    def is_locked(self, row):
        return lockbox.locked_tier(emit_visual.date.fromisoformat(row["date"]), self.locked) is not None

    def perturbed(self, index, sofr):
        rows = copy.deepcopy(self.rows)
        rows[index]["sofr"] = sofr
        return rows

    def test_the_panel_reaches_into_a_locked_tier(self):
        self.assertTrue(self.locked)
        self.assertTrue(any(self.is_locked(r) for r in self.rows))

    def test_locked_perturbation_changes_nothing(self):
        base = self.run_n1(self.rows)
        locked = [i for i, r in enumerate(self.rows) if self.is_locked(r)]
        for index in (locked[0], locked[len(locked) // 2], locked[-1]):
            for sofr in ("9.99", "0.01"):
                with self.subTest(date=self.rows[index]["date"], sofr=sofr):
                    self.assertEqual(self.run_n1(self.perturbed(index, sofr)), base)

    def test_unlocked_perturbation_is_seen(self):
        base = self.run_n1(self.rows)
        index = next(i for i, r in enumerate(self.rows)
                     if not self.is_locked(r) and float(r["sofr"]) - float(r["iorb"]) < 0)
        self.assertNotEqual(self.run_n1(self.perturbed(index, "9.99")), base)

    def test_held_spans_come_from_the_lockbox(self):
        data, _ = self.run_n1(self.rows)
        starts = [t.start.isoformat() for t in self.locked]
        self.assertEqual([s["start"] for s in data["held_out"]],
                         [s for s in starts if s <= self.rows[-1]["date"]])

    def test_an_opened_tier_is_not_held(self):
        document = json.loads((ROOT / emit_visual.LOCKBOX).read_text(encoding="utf-8"))
        for tier in document["tiers"]:
            tier["opened"] = {"date": "2026-10-02", "ruling": "a test fixture standing in for her ruling"}
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lockbox.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            opened = lockbox.locked_tiers(path)
        self.assertEqual(opened, ())
        data, fills = self.run_n1(self.rows, opened)
        self.assertEqual(data["held_out"], [])
        self.assertEqual(data["counted"]["n"], len(self.rows))
        self.assertEqual(fills["n1_held_note"], "No day on this chart is held out.")


def panel_rows():
    manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
    return list(csv.DictReader(raw.decode().splitlines()))


class NewcomerN2Tests(unittest.TestCase):
    """N2 "Why is this hard?" (#143): one mark per scored day, binned by the highest threshold crossed.

    The day set is the scored grid (`asof.fold_grid` at the published
    declarations' minimum history), cross-checked here, and only here, against
    the fold dates of `docs/runs/persistence_funding.json` (#141 §2.1): the
    generator reads no run record. Locked days (`metadata/lockbox.json`) are
    drawn as hollow grey marks labelled "held out" and carry no spread, no bin,
    and no weight in any count or sentence (#141 ruling 3).

    Recorded mutation: in `newcomer_n2`, `kept = counted(scored, locked)`
    -> `kept = list(scored)`. test_locked_perturbation_changes_nothing then
    failed with AssertionError (the counts and fills moved), and so did
    test_no_held_day_is_binned_or_counted.
    """

    @classmethod
    def setUpClass(cls):
        cls.rows = panel_rows()
        cls.locked = lockbox.locked_tiers(PRE_OPENING_LOCKBOX)
        cls.registry = json.loads((ROOT / emit_visual.SOURCES).read_text(encoding="utf-8"))
        cls.thresholds = json.loads((ROOT / emit_visual.THRESHOLDS).read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        cls.decision = emit_visual.time.fromisoformat(manifest["decision_time"])
        cls.page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")

    def run_n2(self, rows, locked=None):
        locked = self.locked if locked is None else locked
        return emit_visual.newcomer_n2(copy.deepcopy(rows), self.registry, self.decision, locked, self.thresholds)

    def is_locked(self, iso):
        return lockbox.locked_tier(emit_visual.date.fromisoformat(iso), self.locked) is not None

    def spread(self, row):
        return int((emit_visual.Decimal(row["sofr"]) - emit_visual.Decimal(row["iorb"])) * 100)

    def test_the_day_set_is_the_published_scored_grid(self):
        """#141 §2.1: the fold dates of the published persistence record prove the day set."""
        record = json.loads(AS_OF.read_text(encoding="utf-8"))
        self.assertEqual(record["declaration"]["minimum_history"], emit_visual.N2_MINIMUM_HISTORY)
        data, _ = self.run_n2(self.rows)
        folds = record["folds"]
        self.assertEqual(data["days"][0][0], folds["first"]["scored_date"])
        self.assertEqual(data["days"][-1][0], folds["last"]["scored_date"])
        self.assertEqual(len(data["days"]), folds["count"])
        self.assertEqual(data["scored"]["first"], folds["first"]["scored_date"])
        self.assertEqual(data["scored"]["n"], folds["count"])
        self.assertGreater(data["scored"]["first"], self.rows[0]["date"])  # the start differs from N1's

    def test_bins_are_strict_and_exclusive(self):
        taus = [int(t) for t in self.thresholds["taus_bp"]]
        self.assertEqual(emit_visual.n2_bin(taus[0], taus), 0)  # on the line is not above it
        self.assertEqual(emit_visual.n2_bin(taus[0] + 1, taus), 1)
        self.assertEqual(emit_visual.n2_bin(taus[1], taus), 1)
        self.assertEqual(emit_visual.n2_bin(taus[-1] + 1, taus), len(taus))  # only in the top bin
        self.assertEqual(emit_visual.n2_bin(-30, taus), 0)
        data, _ = self.run_n2(self.rows)
        by_date = {r["date"]: r for r in self.rows}
        for iso, s, b in data["days"]:
            if b is None:
                continue
            self.assertEqual(s, self.spread(by_date[iso]))
            self.assertEqual(b, sum(1 for t in taus if s > t))

    def test_no_held_day_is_binned_or_counted(self):
        data, _ = self.run_n2(self.rows)
        held = [d for d in data["days"] if self.is_locked(d[0])]
        self.assertTrue(held, "the grid reaches no locked tier, so this test would hold vacuously")
        self.assertTrue(all(s is None and b is None for _, s, b in held))
        open_days = [d for d in data["days"] if not self.is_locked(d[0])]
        self.assertTrue(all(b is not None for _, _, b in open_days))
        self.assertEqual(data["counted"]["n"], len(open_days))
        self.assertEqual(sum(data["counted"]["bins"]), len(open_days))
        self.assertTrue(all(not self.is_locked(e["date"]) for e in data["tail"]))

    def test_locked_perturbation_changes_nothing(self):
        base = self.run_n2(self.rows)
        locked = [i for i, r in enumerate(self.rows) if self.is_locked(r["date"])]
        for index in (locked[0], locked[len(locked) // 2], locked[-1]):
            for sofr in ("9.99", "0.01"):
                rows = copy.deepcopy(self.rows)
                rows[index]["sofr"] = sofr
                with self.subTest(date=rows[index]["date"], sofr=sofr):
                    self.assertEqual(self.run_n2(rows), base)

    def test_unlocked_perturbation_is_seen(self):
        base = self.run_n2(self.rows)
        index = next(i for i, r in enumerate(self.rows)
                     if r["date"] >= base[0]["scored"]["first"] and not self.is_locked(r["date"])
                     and self.spread(r) < 0)
        rows = copy.deepcopy(self.rows)
        rows[index]["sofr"] = "9.99"
        moved = self.run_n2(rows)
        self.assertNotEqual(moved[1], base[1])
        self.assertNotEqual(moved[0]["counted"], base[0]["counted"])

    def test_an_opened_tier_is_counted(self):
        document = json.loads((ROOT / emit_visual.LOCKBOX).read_text(encoding="utf-8"))
        for tier in document["tiers"]:
            tier["opened"] = {"date": "2026-10-02", "ruling": "a test fixture standing in for her ruling"}
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lockbox.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            opened = lockbox.locked_tiers(path)
        data, fills = self.run_n2(self.rows, opened)
        self.assertEqual(data["held_out"], [])
        self.assertEqual(data["counted"]["n"], data["scored"]["n"])
        self.assertTrue(all(b is not None for _, _, b in data["days"]))
        self.assertEqual(fills["n2_held_note"], "No scored day is held out.")

    def test_the_upper_thresholds_are_listed_day_by_day_without_a_rate(self):
        """#141 §4 N2: +20 and +50 bp days are drawn and listed, with no rate and no pooled statement."""
        taus = [int(t) for t in self.thresholds["taus_bp"]]
        data, fills = self.run_n2(self.rows)
        expected = [r["date"] for r in self.rows
                    if data["scored"]["first"] <= r["date"] and not self.is_locked(r["date"])
                    and self.spread(r) > taus[2]]
        self.assertTrue(expected)
        self.assertEqual([e["date"] for e in data["tail"]], expected)
        self.assertNotIn("%", fills["n2_tail_list"])
        for key in ("n2_lede", "n2_runs"):
            self.assertNotRegex(fills[key], rf"\+{taus[2]}\b|\+{taus[3]}\b")
        for e in data["tail"]:
            self.assertIn(emit_visual.short_day(e["date"]), fills["n2_tail_list"])

    def test_the_chart_label_counts_only_the_headline_thresholds(self):
        """#141 §4 N2: the chart's aria-label carries no pooled count above +20 or +50 bp."""
        template = (ROOT / emit_visual.TEMPLATE).read_text(encoding="utf-8")
        body = template[template.index("function renderN2()"):]
        body = body[:body.index("\n}\n")]
        labels = [line for line in body.splitlines() if '"aria-label"' in line]
        self.assertEqual(len(labels), 1)
        label = labels[0]
        self.assertNotIn("counted.above.map", label)
        self.assertNotRegex(label, r"counted\.above\[[23]\]")
        self.assertIn("N2.counted.above[0]", label)
        self.assertIn("N2.counted.above[1]", label)
        self.assertIn("listed one by one", label)

    def test_cluster_years_are_read_from_the_counts(self):
        data, fills = self.run_n2(self.rows)
        by_year = {int(y): k for y, k in data["counted"]["by_year"].items()}
        self.assertEqual(data["counted"]["cluster_years"], emit_visual.cluster_years(by_year))
        for year in data["counted"]["cluster_years"]:
            self.assertIn(str(year), fills["n2_lede"])

    def test_the_page_carries_n2_after_n1(self):
        block = newcomer_block(self.page)
        self.assertIn('<section id="n2"', block)
        self.assertLess(block.index('<section id="n1"'), block.index('<section id="n2"'))
        self.assertIn('href="#n2"', block)
        self.assertIn("held out", block[block.index('<section id="n2"'):])


#: Mark colours: graphical objects, WCAG 2.1 non-text contrast (3:1) against the page.
MARKS_ON = {"th1": ("paper",), "th2": ("paper",), "th3": ("paper",), "th4": ("paper",)}


class MarkContrastTests(unittest.TestCase):
    template = (ROOT / emit_visual.TEMPLATE).read_text(encoding="utf-8")

    def test_threshold_marks_meet_non_text_contrast_in_both_themes(self):
        for theme in ("light", "dark"):
            tokens = theme_tokens(self.template)[theme]
            for fg, surfaces in MARKS_ON.items():
                for bg in surfaces:
                    with self.subTest(theme=theme, fg=fg, bg=bg):
                        self.assertGreaterEqual(contrast(tokens[fg], tokens[bg]), 3.0)


# ---------------------------------------------------------------- N3 "When does it happen?" (#141, #147)


class NewcomerN3Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
        cls.rows = list(csv.DictReader(raw.decode().splitlines()))
        cls.locked = lockbox.locked_tiers(PRE_OPENING_LOCKBOX)
        cls.registry = json.loads((ROOT / emit_visual.SOURCES).read_text(encoding="utf-8"))
        cls.thresholds = json.loads((ROOT / emit_visual.THRESHOLDS).read_text(encoding="utf-8"))
        cls.notes = json.loads((ROOT / emit_visual.ANNOTATIONS).read_text(encoding="utf-8"))
        cls.decision = emit_visual.time.fromisoformat(manifest["decision_time"])
        cls.on_rrp, cls.snapshots = emit_visual.on_rrp_results(ROOT)
        cls.base = cls.run_n3(cls.rows)

    @classmethod
    def run_n3(cls, rows, locked=None, on_rrp=None):
        return emit_visual.newcomer_n3(copy.deepcopy(rows), cls.locked if locked is None else locked,
                                       cls.thresholds, cls.registry, cls.decision,
                                       cls.on_rrp if on_rrp is None else on_rrp, cls.notes)

    def is_locked(self, row):
        return lockbox.locked_tier(emit_visual.date.fromisoformat(row["date"]), self.locked) is not None


class NewcomerN3Tests(NewcomerN3Base):
    """N3's 2x2: quarter-end window against scarce or abundant cash, a rate per cell."""

    def test_the_cells_partition_the_counted_days(self):
        data, _ = self.base
        kept = emit_visual.counted(self.rows, self.locked)
        self.assertEqual(len(data["cells"]), 4)
        self.assertEqual({(c["scarce"], c["quarter_end"]) for c in data["cells"]},
                         {(True, True), (True, False), (False, True), (False, False)})
        self.assertEqual(sum(c["n"] for c in data["cells"]), len(kept))
        self.assertEqual(data["counted"]["n"], len(kept))

    def test_quarter_end_is_the_window_in_force(self):
        """#140 has merged, so the 2x2 reads `quarter_end_window`, and the caption names it."""
        from repo_model import data as panel_data
        data, fills = self.base
        self.assertEqual(data["column"], "quarter_end_window")
        self.assertEqual(data["window_business_days"], panel_data.QUARTER_END_WINDOW_BUSINESS_DAYS)
        kept = emit_visual.counted(self.rows, self.locked)
        in_window = sum(1 for r in kept
                        if panel_data.quarter_end_window(emit_visual.date.fromisoformat(r["date"])) == 1.0)
        self.assertEqual(sum(c["n"] for c in data["cells"] if c["quarter_end"]), in_window)
        self.assertIn("quarter_end_window", fills["n3_window_caption"])

    def test_scarce_is_the_declared_on_rrp_break_alone(self):
        from repo_model import contract
        data, _ = self.base
        self.assertEqual(data["break_bn"], contract.ON_RRP_DEPLETION_BREAK_BN)
        source = (ROOT / "scripts" / "emit_visual.py").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"(?m)=\s*100(\.0)?\s*(#.*)?$")
        self.assertNotIn("scarcity", data)

    def test_each_cell_is_a_rate_with_an_interval(self):
        data, _ = self.base
        for cell in data["cells"]:
            for tau in (data["pressure_bp"], data["second_bp"]):
                with self.subTest(cell=(cell["scarce"], cell["quarter_end"]), tau=tau):
                    entry = cell["above"][str(tau)]
                    self.assertLessEqual(entry["k"], cell["n"])
                    self.assertAlmostEqual(entry["rate"], entry["k"] / cell["n"])
                    lo, hi = entry["interval"]
                    self.assertLessEqual(lo, entry["rate"])
                    self.assertGreaterEqual(hi, entry["rate"])

    def test_the_lede_is_a_rate_per_cell_not_a_claim_that_one_cell_spikes(self):
        _, fills = self.base
        for cell in self.base[0]["cells"]:
            self.assertIn(f"{cell['above'][str(self.base[0]['pressure_bp'])]['k']} of {cell['n']}", fills["n3_lede"])
        self.assertNotRegex(fills["n3_lede"].lower(), r"\bonly\b")


class NewcomerN3AsOfReadTests(NewcomerN3Base):
    """The ON RRP reading is the one public at the decision instant, and not stale.

    A result is declared public at 16:00 ET on the next business day
    (`metadata/sources.json`, `nyfed_on_rrp.release_lag`), so a 16:00 reading
    on day d sees the previous business day's operation, never d's own.

    Recorded mutation: in `on_rrp_as_of`, `bisect.bisect_right(times, instant)`
    -> `bisect.bisect_right(times, instant + timedelta(days=1))`.
    test_a_monday_reads_the_friday_result and
    test_no_read_is_public_after_the_decision_instant then failed with
    AssertionError (the day's own operation was read).
    """

    def read(self, iso, on_rrp=None):
        return emit_visual.on_rrp_as_of(self.on_rrp if on_rrp is None else on_rrp,
                                        emit_visual.date.fromisoformat(iso), self.decision, self.registry)

    def test_a_monday_reads_the_friday_result(self):
        ref, _ = self.read("2025-03-03")
        self.assertEqual(ref.isoformat(), "2025-02-28")

    def test_no_read_is_public_after_the_decision_instant(self):
        from zoneinfo import ZoneInfo
        zone = ZoneInfo(self.registry["nyfed_on_rrp"]["release_lag"]["timezone"])
        published = {ref: at for ref, at, _ in self.on_rrp}
        for r in emit_visual.counted(self.rows, self.locked):
            today = emit_visual.date.fromisoformat(r["date"])
            ref, _ = self.read(r["date"])
            with self.subTest(day=r["date"]):
                self.assertLess(ref, today)
                self.assertLessEqual(published[ref], emit_visual.datetime.combine(today, self.decision, zone))


class NewcomerN3StaleReadTests(NewcomerN3Base):
    """A reading older than the registry's worst case is refused, not carried.

    Recorded mutation: in `on_rrp_as_of`, `if (day - ref).days > limit:`
    -> `if False:`. test_a_stale_read_is_refused then failed with
    AssertionError: ValueError not raised.
    """

    def test_a_stale_read_is_refused(self):
        day = emit_visual.date(2025, 3, 14)
        gap = [o for o in self.on_rrp if not (emit_visual.date(2025, 3, 1) <= o[0] < day)]
        with self.assertRaises(ValueError):
            emit_visual.on_rrp_as_of(gap, day, self.decision, self.registry)

    def test_every_counted_day_has_a_fresh_read(self):
        limit = self.registry["nyfed_on_rrp"]["release_lag"]["worst_case_calendar_days"]
        for r in emit_visual.counted(self.rows, self.locked):
            today = emit_visual.date.fromisoformat(r["date"])
            ref, _ = emit_visual.on_rrp_as_of(self.on_rrp, today, self.decision, self.registry)
            self.assertLessEqual((today - ref).days, limit)


class NewcomerN3HeldOutDayTests(NewcomerN3Base):
    """Locked days change no cell, count or sentence in N3 (#141 ruling 3).

    Perturbing a locked day's SOFR, or the ON RRP result its reading would see,
    leaves N3's data and fills unchanged; perturbing an unlocked day moves them.

    Recorded mutation: in `newcomer_n3`, `kept = counted(rows, locked)`
    -> `kept = list(rows)`. test_locked_perturbation_changes_nothing then
    failed with AssertionError (the cell counts and the lede moved).
    """

    def perturbed(self, index, sofr):
        rows = copy.deepcopy(self.rows)
        rows[index]["sofr"] = sofr
        return rows

    def test_the_panel_reaches_into_a_locked_tier(self):
        self.assertTrue(any(self.is_locked(r) for r in self.rows))

    def test_locked_perturbation_changes_nothing(self):
        locked = [i for i, r in enumerate(self.rows) if self.is_locked(r)]
        for index in (locked[0], locked[-1]):
            for sofr in ("9.99", "0.01"):
                with self.subTest(date=self.rows[index]["date"], sofr=sofr):
                    self.assertEqual(self.run_n3(self.perturbed(index, sofr)), self.base)
        first = emit_visual.date.fromisoformat(self.rows[locked[0]]["date"])
        moved = [(ref, at, 0.0 if ref >= first else value) for ref, at, value in self.on_rrp]
        self.assertEqual(self.run_n3(self.rows, on_rrp=moved), self.base)

    def test_unlocked_perturbation_is_seen(self):
        index = next(i for i, r in enumerate(self.rows)
                     if not self.is_locked(r) and float(r["sofr"]) - float(r["iorb"]) < 0)
        self.assertNotEqual(self.run_n3(self.perturbed(index, "9.99")), self.base)

    def test_held_out_days_are_greyed_and_labelled(self):
        data, fills = self.base
        self.assertTrue(data["held_out"])
        self.assertIn("held out", fills["n3_held_note"])
        self.assertIn("class='held'", fills["n3_table"])

    def test_an_opened_tier_is_counted(self):
        data, fills = self.run_n3(self.rows, locked=())
        self.assertEqual(data["held_out"], [])
        self.assertEqual(sum(c["n"] for c in data["cells"]), len(self.rows))
        self.assertNotIn("class='held'", fills["n3_table"])


class NewcomerN3PageTests(unittest.TestCase):
    page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")

    def section(self):
        block = newcomer_block(self.page)
        return block[block.index('<section id="n3"'):]

    def test_n3_is_on_the_page_and_in_the_nav(self):
        self.assertIn('<section id="n3"', newcomer_block(self.page))
        self.assertRegex(newcomer_block(self.page), r'<nav aria-label="Start here">.*href="#n3"')

    def test_the_caption_states_the_quarter_end_definition(self):
        self.assertIn("quarter_end_window", self.section())

    def test_every_claim_link_is_a_primary_source(self):
        section = self.section().split("</section>")[0]
        section = re.sub(r"<span class=\"def\"[^>]*>.*?</span><!--/def-->", " ", section, flags=re.S)
        links = re.findall(r"href=['\"](https?://[^'\"]+)['\"]", section)
        self.assertTrue(links)
        for url in links:
            with self.subTest(url=url):
                self.assertTrue(url.startswith(emit_visual.ALLOWED_SOURCES))

    def test_the_data_file_names_every_on_rrp_snapshot_it_read(self):
        doc = json.loads((ROOT / emit_visual.DATA_DIR / "newcomer_n3.json").read_text(encoding="utf-8"))
        inputs = doc["provenance"]["inputs"]
        snaps = sorted(p for p in (ROOT / emit_visual.ON_RRP).glob("*.json") if not p.name.endswith(".manifest.json"))
        self.assertTrue(snaps)
        for path in snaps:
            rel = str(path.relative_to(ROOT))
            with self.subTest(path=rel):
                self.assertEqual(inputs[rel], emit_visual.sha256(path))


# ---------------------------------------------------------------- the reserve-scarcity band behind N1 and N3 (#148)


class NewcomerBandBase(unittest.TestCase):
    """The #115 state as read on the scored grid, shared by the band's tests (built once: a few seconds)."""

    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
        cls.rows = list(csv.DictReader(raw.decode().splitlines()))
        cls.locked = lockbox.locked_tiers(PRE_OPENING_LOCKBOX)
        cls.registry = json.loads((ROOT / emit_visual.SOURCES).read_text(encoding="utf-8"))
        cls.thresholds = json.loads((ROOT / emit_visual.THRESHOLDS).read_text(encoding="utf-8"))
        cls.notes = json.loads((ROOT / emit_visual.ANNOTATIONS).read_text(encoding="utf-8"))
        cls.decision = emit_visual.time.fromisoformat(manifest["decision_time"])
        cls.on_rrp, _ = emit_visual.on_rrp_results(ROOT)
        cls.scored, cls.snapshots = emit_visual.scarcity_days(ROOT, cls.locked)
        cls.status = {"key": "registered_unused", "icon": "○", "word": "Registered but unused",
                      "reason": "registered, and no published declaration reads it"}
        cls.base = cls.run_band(cls.scored)

    @classmethod
    def run_band(cls, scored, locked=None, status=None):
        return emit_visual.newcomer_band(list(scored), cls.locked if locked is None else locked, cls.thresholds,
                                         cls.registry, cls.decision, cls.on_rrp, cls.status if status is None
                                         else status, cls.notes)

    def locked_days(self):
        return [emit_visual.date.fromisoformat(r["date"]) for r in self.rows
                if lockbox.locked_tier(emit_visual.date.fromisoformat(r["date"]), self.locked) is not None]


class NewcomerBandTests(NewcomerBandBase):
    """The band shades #115's state, read as-of, with the ON RRP buffer as a sub-lane."""

    def test_the_state_is_the_one_115_declared_and_validated(self):
        """Each day's state is `scarcity.pressure_days_by_state`'s, and no cut-point is re-declared here."""
        from repo_model import scarcity
        data, _ = self.base
        days = {d.day.isoformat(): d.state for d in self.scored}
        for start, end, state in data["spans"]:
            for iso in (start, end):
                with self.subTest(day=iso):
                    self.assertEqual(state, None if days[iso] is None else int(days[iso]))
        self.assertEqual(data["labels"], {str(k): v for k, v in scarcity.STATE_LABELS.items()})
        self.assertEqual(data["band"], list(scarcity.SATIATION_BAND))
        self.assertEqual(data["buffer_bn"], scarcity.ON_RRP_BUFFER_BN)
        source = (ROOT / "scripts" / "emit_visual.py").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"0\.1[23]\b")

    def test_spans_cover_the_scored_days_in_order_without_gaps(self):
        data, _ = self.base
        spans = data["spans"]
        days = [d.day.isoformat() for d in self.scored]
        self.assertEqual(spans[0][0], days[0])
        self.assertEqual(spans[-1][1], days[-1])
        position = {iso: i for i, iso in enumerate(days)}
        for (_, end, a), (start, _, b) in zip(spans, spans[1:]):
            self.assertEqual(position[start], position[end] + 1)
            self.assertNotEqual(a, b)

    def test_the_band_stops_before_the_first_locked_day(self):
        first_locked = min(t.start for t in self.locked)
        self.assertLess(max(d.day for d in self.scored), first_locked)
        data, _ = self.base
        self.assertLess(data["counted"]["last"], first_locked.isoformat())

    def test_the_grid_is_the_published_scored_grid(self):
        """The band starts where N2 does: the first day with the published minimum history."""
        n2 = json.loads((ROOT / emit_visual.DATA_DIR / "newcomer_n2.json").read_text(encoding="utf-8"))["data"]
        data, _ = self.base
        self.assertEqual(data["counted"]["first"], n2["days"][0][0])

    def test_frequencies_are_115s_tabulation(self):
        """k of n per state, at both headline thresholds, as `scarcity.tabulate` reports them for #115."""
        from repo_model import scarcity
        table = scarcity.tabulate(self.scored)
        data, _ = self.base
        self.assertEqual(sorted(data["by_state"]), sorted(table["by_state"]))
        for state, cell in table["by_state"].items():
            for tau in (5, 10):
                with self.subTest(state=state, tau=tau):
                    mine = data["by_state"][state]
                    self.assertEqual(mine["n"], cell["days"])
                    self.assertEqual(mine["above"][str(tau)]["k"], cell[f"gt_{tau}bp"]["pressure_days"])
                    self.assertEqual(mine["above"][str(tau)]["interval"], cell[f"gt_{tau}bp"]["interval"])
        self.assertEqual(data["rises"], {str(t): table["rises"][f"gt_{t}bp"] for t in (5, 10)})

    def test_the_sub_lane_is_n3s_scarce_cash(self):
        """The sub-lane marks the days N3's 2x2 calls scarce: ON RRP read at 16:00 below the break."""
        from repo_model import contract
        data, _ = self.base
        below = set()
        for start, end in data["buffer_spans"]:
            below |= {d.day for d in self.scored if start <= d.day.isoformat() <= end}
        for d in self.scored:
            _, value = emit_visual.on_rrp_as_of(self.on_rrp, d.day, self.decision, self.registry)
            with self.subTest(day=d.day.isoformat()):
                self.assertEqual(d.day in below, value < contract.ON_RRP_DEPLETION_BREAK_BN)

    def test_the_caption_says_plainly_when_frequency_does_not_rise(self):
        """Eleonora's ruling on #148: if frequency does not rise with the state, the caption says so."""
        data, fills = self.base
        self.assertFalse(data["rises"]["5"])
        self.assertIn("does not rise step by step", fills["band_caption"])
        self.assertIn("not a working indicator", fills["band_caption"])

    def test_a_monotone_state_is_described_as_rising(self):
        from repo_model.scarcity import ScoredDay
        start = emit_visual.date(2019, 1, 1)
        synthetic = []
        for i in range(400):
            state = i // 100
            spread = 9.0 if (i % 100) < 10 * state else -3.0
            synthetic.append(ScoredDay(start + emit_visual.timedelta(days=i), float(state), start, spread))
        data, fills = self.run_band(synthetic)
        self.assertTrue(data["rises"]["5"])
        self.assertNotIn("does not rise", fills["band_caption"])

    def test_the_legend_carries_the_derived_status(self):
        _, fills = self.base
        self.assertIn("Registered but unused", fills["band_status"])
        other = {"key": "used", "icon": "●", "word": "Used", "reason": "in the published declaration x"}
        _, moved = self.run_band(self.scored, status=other)
        self.assertIn("Used", moved["band_status"])
        self.assertNotIn("Registered but unused", moved["band_status"])

    def test_the_status_is_n4s_for_the_scarcity_tag(self):
        n4 = json.loads((ROOT / emit_visual.DATA_DIR / "newcomer_n4.json").read_text(encoding="utf-8"))["data"]
        tag = next(t for t in n4["tags"] if t["key"] == emit_visual.BAND_TAG)
        band = json.loads((ROOT / emit_visual.DATA_DIR / "newcomer_band.json").read_text(encoding="utf-8"))["data"]
        self.assertEqual(band["status"]["key"], tag["status"])
        self.assertIn("#115", tag["label"])


class NewcomerBandHeldOutDayTests(NewcomerBandBase):
    """Locked days change no span, count or sentence of the band (#141 ruling 3).

    The scored days are read with `end` at the last day before the first
    locked tier, so the lockbox's own guard in `baseline._as_of_folds` is never
    asked to score one. `newcomer_band` also drops any day in a locked tier
    itself; these tests hand it locked days, with every state and a spread far
    above every threshold, and check nothing moves.

    Recorded mutation: in `newcomer_band`,
    `kept = [d for d in scored if locked_tier(d.day, locked) is None]`
    -> `kept = list(scored)`. test_locked_days_change_nothing then failed with
    AssertionError (the spans, the counts and the caption moved).
    """

    def with_locked(self, state, spread):
        from repo_model.scarcity import ScoredDay
        return list(self.scored) + [ScoredDay(d, state, d, spread) for d in self.locked_days()]

    def test_the_panel_reaches_into_a_locked_tier(self):
        self.assertTrue(self.locked_days())

    def test_locked_days_change_nothing(self):
        for state in (0.0, 3.0):
            for spread in (99.0, -20.0):
                with self.subTest(state=state, spread=spread):
                    self.assertEqual(self.run_band(self.with_locked(state, spread)), self.base)

    def test_unlocked_perturbation_is_seen(self):
        from repo_model.scarcity import ScoredDay
        scored = list(self.scored)
        first = scored[0]
        scored[0] = ScoredDay(first.day, 3.0 if first.state != 3.0 else 0.0, first.read_date, 99.0)
        self.assertNotEqual(self.run_band(scored), self.base)

    def test_an_opened_tier_is_counted(self):
        data, _ = self.run_band(self.with_locked(3.0, 99.0), locked=())
        self.assertEqual(data["held_out"], [])
        self.assertEqual(data["counted"]["n"], len(self.scored) + len(self.locked_days()))

    def test_the_held_out_days_are_named(self):
        data, fills = self.base
        self.assertTrue(data["held_out"])
        self.assertIn("held out", fills["band_held_note"])


class NewcomerBandPageTests(unittest.TestCase):
    page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")

    def section(self, view):
        block = newcomer_block(self.page)
        return block[block.index(f'<section id="{view}"'):].split("</section>")[0]

    def test_n1_shades_the_state_behind_a_keyboard_toggle(self):
        n1 = self.section("n1")
        button = re.search(r'<button[^>]*id="n1bandbtn"[^>]*>', n1)
        self.assertIsNotNone(button)
        self.assertIn('aria-pressed="false"', button.group(0))
        self.assertIn('aria-controls="n1bandkey"', button.group(0))
        self.assertIn('id="n1bandkey"', n1)

    def test_n3_draws_the_band_with_its_caption(self):
        n3 = self.section("n3")
        self.assertIn('id="n3band"', n3)
        self.assertIn("does not rise step by step", n3)
        self.assertIn("Reserve-scarcity state (#115)", n3)
        self.assertNotIn("is not shown until its publication is ruled", n3)

    def test_every_band_link_is_a_primary_source(self):
        for view in ("n1", "n3"):
            section = re.sub(r"<span class=\"def\"[^>]*>.*?</span><!--/def-->", " ", self.section(view), flags=re.S)
            for url in re.findall(r"href=['\"](https?://[^'\"]+)['\"]", section):
                with self.subTest(view=view, url=url):
                    self.assertTrue(url.startswith(emit_visual.ALLOWED_SOURCES))

    def test_the_data_file_names_every_snapshot_it_read(self):
        doc = json.loads((ROOT / emit_visual.DATA_DIR / "newcomer_band.json").read_text(encoding="utf-8"))
        inputs = doc["provenance"]["inputs"]
        for root in ("tests/fixtures/snapshots/h8_inputs", emit_visual.ON_RRP):
            files = sorted(p for p in (ROOT / root).rglob("*") if p.is_file() and not p.name.endswith(".manifest.json"))
            self.assertTrue(files)
            for path in files:
                rel = str(path.relative_to(ROOT))
                with self.subTest(path=rel):
                    self.assertEqual(inputs[rel], emit_visual.sha256(path))


# ---------------------------------------------------------------- N4's tag-status engine (#141 §3, #144)


def synthetic(fields=("X",), expect=None, issues=(1,)):
    """A one-tag map, a registry, no published use and a closed directive: the base the tests vary."""
    pairs = [dict({"source": "src_a", "field": f}, **({"expect": expect} if expect else {})) for f in fields]
    tag_map = {"flows": {"f": {"from": "money_funds", "to": "dealers", "kind": "repo", "claim": "triparty_actors"}},
               "tags": [{"key": "t", "label": "Tag", "flow": "f", "fields": pairs, "issues": list(issues),
                         "fixtures": None}]}
    registry = {"src_a": {"fields": ["X", "Y"]}}
    records = {"docs/runs/base.json": {"declaration": {"model": "m", "features": []},
                                       "derived": {"fields": []}}}
    snapshot = {"retrieved_at": "2026-10-02T00:00:00Z",
                "issues": [{"number": n, "title": f"Directive {n}", "state": "closed", "labels": ["directive"],
                            "open_prs": []} for n in issues]}
    return tag_map, registry, records, snapshot


def comparison(extra_b, lower, upper, model_b="m"):
    """A published comparison record: model_b is model_a plus `extra_b` registry fields."""
    return {"comparison": {"loss": "crps_bps", "mean_difference_interval": {"lower": lower, "upper": upper,
                                                                              "level": 0.9}},
            "declaration": {"model_a": {"model": "m", "features": []},
                            "model_b": {"model": model_b, "features": []}},
            "derived": {"model_a": {"fields": []}, "model_b": {"fields": [f"src_a.{f}" for f in extra_b]}}}


class TagStatusTests(unittest.TestCase):
    """The status engine on a synthetic registry: every status, a flip, and "unregistered stays unregistered".

    No status is typed anywhere: each comes from the registry, the published
    declarations, the published comparison records and the issue snapshot.
    """

    def status(self, tag_map, registry, records, snapshot):
        notes = json.loads((ROOT / emit_visual.ANNOTATIONS).read_text(encoding="utf-8"))
        emit_visual.check_map(tag_map, registry, notes)
        manifest = {"built_columns": [], "refused_columns": {}}
        return emit_visual.tag_statuses(tag_map, registry, manifest, records, snapshot, tracked=())[0]

    def test_registered_but_unused(self):
        row = self.status(*synthetic())
        self.assertEqual(row["status"], "registered_unused")
        self.assertIsNone(row["sub"])

    def test_used_when_a_published_declaration_carries_the_field(self):
        tag_map, registry, records, snapshot = synthetic()
        records["docs/runs/base.json"]["derived"]["fields"] = ["src_a.X"]
        row = self.status(tag_map, registry, records, snapshot)
        self.assertEqual(row["status"], "used")
        self.assertIn("docs/runs/base.json", row["reason"])

    def test_used_needs_every_field_in_one_record(self):
        tag_map, registry, records, snapshot = synthetic(fields=("X", "Y"))
        records["docs/runs/base.json"]["derived"]["fields"] = ["src_a.X"]
        self.assertEqual(self.status(tag_map, registry, records, snapshot)["status"], "registered_unused")

    def test_an_archived_record_does_not_make_a_tag_used(self):
        tag_map, registry, records, snapshot = synthetic()
        records["docs/runs/archive/old.json"] = {"declaration": {"features": []}, "derived": {"fields": ["src_a.X"]}}
        self.assertEqual(self.status(tag_map, registry, records, snapshot)["status"], "registered_unused")

    def test_tried_and_hurt_from_a_published_comparison(self):
        tag_map, registry, records, snapshot = synthetic()
        records["docs/runs/compare.json"] = comparison(["X"], -0.3, -0.1)
        row = self.status(tag_map, registry, records, snapshot)
        self.assertEqual(row["status"], "tried_and_hurt")
        self.assertIn("docs/runs/compare.json", row["reason"])

    def test_no_verdict_when_the_interval_spans_zero_or_the_field_helped(self):
        for lower, upper in ((-0.3, 0.1), (0.1, 0.3)):
            with self.subTest(interval=(lower, upper)):
                tag_map, registry, records, snapshot = synthetic()
                records["docs/runs/compare.json"] = comparison(["X"], lower, upper)
                self.assertEqual(self.status(tag_map, registry, records, snapshot)["status"], "registered_unused")

    def test_no_verdict_when_the_models_differ_by_more_than_the_field(self):
        tag_map, registry, records, snapshot = synthetic()
        records["docs/runs/compare.json"] = comparison(["X"], -0.3, -0.1, model_b="other")
        self.assertEqual(self.status(tag_map, registry, records, snapshot)["status"], "registered_unused")

    def test_in_progress_from_the_label_or_an_open_pr(self):
        for labels, prs in ((["directive", "in-progress"], []), (["directive"], [7])):
            with self.subTest(labels=labels, prs=prs):
                tag_map, registry, records, snapshot = synthetic()
                snapshot["issues"][0].update(state="open", labels=labels, open_prs=prs)
                row = self.status(tag_map, registry, records, snapshot)
                self.assertEqual(row["status"], "in_progress")
                self.assertIn("#1", row["reason"])

    def test_in_progress_while_its_publish_question_is_open(self):
        tag_map, registry, records, snapshot = synthetic()
        snapshot["issues"].append({"number": 9, "title": "Publish? Directive 1 (#1)", "state": "open",
                                   "labels": ["needs-eleonora"], "open_prs": []})
        row = self.status(tag_map, registry, records, snapshot)
        self.assertEqual(row["status"], "in_progress")
        self.assertIn("#9", row["reason"])

    def test_queued_directive_keeps_registered_but_unused_with_a_sub_line(self):
        tag_map, registry, records, snapshot = synthetic()
        snapshot["issues"][0].update(state="open")
        row = self.status(tag_map, registry, records, snapshot)
        self.assertEqual(row["status"], "registered_unused")
        self.assertEqual(row["sub"], "queued: #1")

    def test_not_registered(self):
        row = self.status(*synthetic(fields=("Z",), expect="unregistered"))
        self.assertEqual(row["status"], "not_registered")

    def test_registering_the_field_flips_the_status(self):
        tag_map, registry, records, snapshot = synthetic(fields=("Z",))
        registry["src_a"]["fields"].append("Z")
        self.assertEqual(self.status(tag_map, registry, records, snapshot)["status"], "registered_unused")
        records["docs/runs/base.json"]["derived"]["fields"] = ["src_a.Z"]
        self.assertEqual(self.status(tag_map, registry, records, snapshot)["status"], "used")

    def test_a_pair_the_registry_lacks_is_refused_unless_marked_unregistered(self):
        with self.assertRaises(emit_visual.VisualError):
            self.status(*synthetic(fields=("Z",)))
        with self.assertRaises(emit_visual.VisualError):
            tag_map, registry, records, snapshot = synthetic()
            tag_map["tags"][0]["fields"][0]["source"] = "no_such_source"
            self.status(tag_map, registry, records, snapshot)

    def test_unregistered_stays_unregistered(self):
        """A pair marked `expect: "unregistered"` that the registry now carries is refused.

        A directive that registers the field forces the map to be revisited.

        Recorded mutation: in `check_map`, `if pair.get("expect") == "unregistered" and registered:`
        -> `if False:`. This test then failed with AssertionError (VisualError not raised).
        """
        tag_map, registry, records, snapshot = synthetic(fields=("Z",), expect="unregistered")
        self.status(tag_map, registry, records, snapshot)
        registry["src_a"]["fields"].append("Z")
        with self.assertRaises(emit_visual.VisualError):
            self.status(tag_map, registry, records, snapshot)

    def test_an_issue_missing_from_the_snapshot_is_refused(self):
        tag_map, registry, records, snapshot = synthetic(issues=(1, 2))
        snapshot["issues"] = snapshot["issues"][:1]
        with self.assertRaises(emit_visual.VisualError):
            self.status(tag_map, registry, records, snapshot)

    def test_a_flow_without_a_sourced_claim_is_refused(self):
        tag_map, registry, records, snapshot = synthetic()
        tag_map["flows"]["f"]["claim"] = "no_such_claim"
        with self.assertRaises(emit_visual.VisualError):
            self.status(tag_map, registry, records, snapshot)

    def test_tracked_data_needs_a_snapshot_manifest(self):
        tag_map, registry, records, snapshot = synthetic()
        tag_map["tags"][0]["fixtures"] = "tests/fixtures/snapshots/a"
        manifest = {"built_columns": [], "refused_columns": {}}
        for tracked, expected in ((("tests/fixtures/snapshots/a/x.json.manifest.json",), True),
                                  (("tests/fixtures/snapshots/a/x.json",), False),
                                  (("tests/fixtures/snapshots/ab/x.json.manifest.json",), False)):
            with self.subTest(tracked=tracked):
                row = emit_visual.tag_statuses(tag_map, registry, manifest, records, snapshot, tracked)[0]
                self.assertIs(row["data_in_repo"], expected)


class PublishedMapTests(unittest.TestCase):
    """The committed map and issue snapshot, read the way the page reads them."""

    tag_map = json.loads((ROOT / emit_visual.MAP).read_text(encoding="utf-8"))
    page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")

    def test_no_status_is_written_in_the_map(self):
        self.assertNotRegex(json.dumps(self.tag_map), r'"status"')
        for tag in self.tag_map["tags"]:
            self.assertNotIn("status", tag)

    def test_every_tag_is_in_the_generated_table_with_a_derived_status(self):
        data = json.loads((ROOT / emit_visual.DATA_DIR / "newcomer_n4.json").read_text(encoding="utf-8"))["data"]
        self.assertEqual([t["key"] for t in data["tags"]], [t["key"] for t in self.tag_map["tags"]])
        names = {key for key, _, _ in emit_visual.STATUSES}
        block = newcomer_block(self.page)
        for row in data["tags"]:
            with self.subTest(tag=row["key"]):
                self.assertIn(row["status"], names)
                self.assertIn(f'id="tag-{row["key"]}"', block)

    def test_status_is_shown_by_more_than_colour(self):
        block = newcomer_block(self.page)
        for key, icon, word_ in emit_visual.STATUSES:
            for mark, text in re.findall(rf'<span class="status s-{key}"><span aria-hidden="true">(.*?)</span>'
                                         rf'(.*?)</span>', block):
                with self.subTest(status=key):
                    self.assertEqual(mark, icon)
                    self.assertEqual(text.strip(), word_)

    def test_changing_the_snapshot_changes_the_status(self):
        registry = json.loads((ROOT / emit_visual.SOURCES).read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        snapshot = json.loads((ROOT / emit_visual.ISSUES).read_text(encoding="utf-8"))
        records = emit_visual.run_record_declarations(ROOT)
        tag = next(t for t in self.tag_map["tags"] if t["issues"])
        base = emit_visual.tag_statuses({**self.tag_map, "tags": [tag]}, registry, manifest, records, snapshot, ())[0]
        moved = copy.deepcopy(snapshot)
        for entry in moved["issues"]:
            if entry["number"] == tag["issues"][0]:
                entry.update(state="open", labels=["directive", "in-progress"])
        row = emit_visual.tag_statuses({**self.tag_map, "tags": [tag]}, registry, manifest, records, moved, ())[0]
        if base["status"] in ("used", "tried_and_hurt"):
            self.assertEqual(row["status"], base["status"])
        else:
            self.assertEqual(row["status"], "in_progress")

    def test_generation_reads_the_snapshot_and_never_fetches(self):
        def refuse(*args, **kwargs):
            raise AssertionError("generation fetched")

        original = emit_visual.gh_fetch
        emit_visual.gh_fetch = refuse
        try:
            emit_visual.generate(ROOT, committed_commit())
        finally:
            emit_visual.gh_fetch = original


class RefreshIssuesTests(unittest.TestCase):
    """`--refresh-issues` writes the snapshot the page reads; regeneration stays byte-reproducible."""

    PAGES = [
        [{"number": 1, "title": "Directive 1", "state": "open", "labels": [{"name": "in-progress"},
                                                                          {"name": "directive"}], "body": "x"},
         {"number": 2, "title": "Not on the map", "state": "open", "labels": [], "body": ""},
         {"number": 3, "title": "Publish? Directive 1 (#1)", "state": "open", "labels": [{"name": "needs-eleonora"}],
          "body": ""},
         {"number": 4, "title": "A pull request", "state": "open", "labels": [], "pull_request": {},
          "body": "Some text.\n\nCloses #1"},
         {"number": 5, "title": "A closed pull request", "state": "closed", "labels": [], "pull_request": {},
          "body": "Closes #1"}],
        [],
    ]

    def fetch(self, path):
        page = int(re.search(r"[?&]page=(\d+)", path).group(1))
        self.calls.append(path)
        return self.PAGES[page - 1] if page <= len(self.PAGES) else []

    def test_snapshot_keeps_the_map_issues_their_publish_questions_and_open_prs(self):
        self.calls = []
        tag_map = synthetic()[0]
        out = emit_visual.refresh_issues(tag_map, self.fetch, "2026-10-02T12:00:00Z")
        doc = json.loads(out)
        self.assertEqual(doc["retrieved_at"], "2026-10-02T12:00:00Z")
        self.assertEqual([e["number"] for e in doc["issues"]], [1, 3])
        self.assertEqual(doc["issues"][0], {"number": 1, "title": "Directive 1", "state": "open",
                                            "labels": ["directive", "in-progress"], "open_prs": [4]})
        self.assertTrue(all(c.startswith(f"repos/{emit_visual.REPOSITORY}/issues?") for c in self.calls))

    def test_the_same_answers_give_the_same_bytes(self):
        self.calls = []
        tag_map = synthetic()[0]
        self.assertEqual(emit_visual.refresh_issues(tag_map, self.fetch, "2026-10-02T12:00:00Z"),
                         emit_visual.refresh_issues(tag_map, self.fetch, "2026-10-02T12:00:00Z"))

    def test_a_map_issue_the_repository_does_not_have_is_refused(self):
        self.calls = []
        tag_map = synthetic(issues=(1, 99))[0]
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.refresh_issues(tag_map, self.fetch, "2026-10-02T12:00:00Z")

    def test_the_committed_snapshot_covers_every_map_issue(self):
        tag_map = json.loads((ROOT / emit_visual.MAP).read_text(encoding="utf-8"))
        snapshot = json.loads((ROOT / emit_visual.ISSUES).read_text(encoding="utf-8"))
        have = {e["number"] for e in snapshot["issues"]}
        for tag in tag_map["tags"]:
            for n in tag["issues"]:
                self.assertIn(n, have)


# ---------------------------------------------------------------- N4's map and segment chart (#141 §4, #145)


class N4MapTests(unittest.TestCase):
    """The map, its tags as buttons with detail panels, its list form, and chapter 1's remaining half."""

    page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")
    tag_map = json.loads((ROOT / emit_visual.MAP).read_text(encoding="utf-8"))
    notes = json.loads((ROOT / emit_visual.ANNOTATIONS).read_text(encoding="utf-8"))
    glossary = json.loads((ROOT / emit_visual.GLOSSARY).read_text(encoding="utf-8"))

    def section(self):
        start = self.page.index('<section id="n4"')
        return self.page[start:self.page.index("</section>", start)]

    def rows(self, tag_map=None):
        tag_map = tag_map or self.tag_map
        registry = json.loads((ROOT / emit_visual.SOURCES).read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        snapshot = json.loads((ROOT / emit_visual.ISSUES).read_text(encoding="utf-8"))
        records = emit_visual.run_record_declarations(ROOT)
        return emit_visual.tag_statuses(tag_map, registry, manifest, records, snapshot, ())

    def test_the_map_is_an_svg_with_an_accessible_name_naming_every_flow(self):
        svg = re.search(r'<div class="n4map">(<svg.*?</svg>)</div>', self.section(), re.S).group(1)
        self.assertRegex(svg, r'^<svg [^>]*role="img" aria-label="[^"]+"')
        label = html_unescape(re.search(r'aria-label="([^"]+)"', svg).group(1))
        for n, (key, flow) in enumerate(self.tag_map["flows"].items(), 1):
            with self.subTest(flow=key):
                self.assertIn(f'id="n4f-{key}"', svg)
                self.assertIn(f"{n}, {self.tag_map['parties'][flow['from']]} to {self.tag_map['parties'][flow['to']]}", label)
        for name in self.tag_map["parties"].values():
            self.assertIn(name.split()[0], svg)

    def test_the_seventh_party_lends_in_both_markets_with_a_cited_source(self):
        self.assertIn("fhlbs", self.tag_map["parties"])
        kinds = {f["kind"] for f in self.tag_map["flows"].values() if f["from"] == "fhlbs"}
        self.assertEqual(kinds, {"repo", "fed_funds"})
        for flow in self.tag_map["flows"].values():
            if flow["from"] == "fhlbs":
                self.assertTrue(self.notes["claims"][flow["claim"]]["src"].startswith("https://www.federalreserve.gov/"))

    def test_every_tag_is_a_button_in_flow_order_with_its_own_hidden_panel(self):
        block = self.section()
        chips = re.findall(r'<button type="button" class="chip"[^>]*aria-controls="n4d-(\w+)"', block)
        order = [r["key"] for f in self.tag_map["flows"] for r in self.rows() if r["flow"] == f]
        order += [r["key"] for b in self.tag_map["boards"] for r in self.rows() if r["board"] == b]
        self.assertEqual(chips, order)
        self.assertEqual(sorted(chips), sorted(t["key"] for t in self.tag_map["tags"]))
        for key in chips:
            with self.subTest(tag=key):
                panel = re.search(rf'<div class="n4d" id="n4d-{key}"[^>]*>(.*?)</div>', block, re.S)
                self.assertIsNotNone(panel)
                self.assertIn(" hidden>", panel.group(0)[:200])
                self.assertIn('<button type="button" class="n4close">Close</button>', panel.group(1))
        for attrs in re.findall(r'<button type="button" class="chip"([^>]*)>', block):
            self.assertIn('aria-pressed="false"', attrs)
            self.assertIn('aria-expanded="false"', attrs)

    def test_status_is_icon_and_word_on_each_tag(self):
        marks = {w: i for _, i, w in emit_visual.STATUSES}
        for icon, word_ in re.findall(r'class="chip"[^>]*><span aria-hidden="true">(.*?)</span> .*? <small>(.*?)</small>',
                                      self.section()):
            self.assertEqual(marks[word_], icon)

    def test_a_flow_no_registered_series_measures_is_drawn_faint_and_this_is_derived(self):
        parties = self.tag_map["parties"]
        svg = emit_visual.map_svg(self.tag_map, self.rows(), parties)
        self.assertIn('class="fl faint" id="n4f-dealers_hf"', svg)
        registered = copy.deepcopy(self.rows())
        for r in registered:
            if r["flow"] == "dealers_hf":
                r["status"] = "registered_unused"
        self.assertIn('class="fl" id="n4f-dealers_hf"', emit_visual.map_svg(self.tag_map, registered, parties))

    def test_map_text_is_checked(self):
        emit_visual.check_map_text(self.tag_map, self.notes, self.glossary)
        for breaking in (lambda m: m["layout"].pop("fhlbs"),
                         lambda m: m["flows"]["mmf_dealers"].update(kind="teleport"),
                         lambda m: m["tags"][0].update(about={"term": "no_such_term"}),
                         lambda m: m["tags"][0].update(about={"claim": "no_such_claim"}),
                         lambda m: m["boards"].update(nowhere={"label": "x", "claim": "sofr_broad"})):
            broken = copy.deepcopy(self.tag_map)
            breaking(broken)
            with self.assertRaises(emit_visual.VisualError):
                emit_visual.check_map_text(broken, self.notes, self.glossary)

    def test_a_board_tag_must_rest_on_a_known_board(self):
        registry = json.loads((ROOT / emit_visual.SOURCES).read_text(encoding="utf-8"))
        broken = copy.deepcopy(self.tag_map)
        next(t for t in broken["tags"] if t.get("board")).update(board="nowhere")
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.check_map(broken, registry, self.notes)

    def test_the_segments_are_defined_and_bilateral_repo_is_in_none(self):
        block = self.section()
        self.assertIn("Non-centrally cleared bilateral repo", block)
        claim = self.notes["claims"]["segments_none"]
        self.assertTrue(claim["src"].startswith("https://www.newyorkfed.org/markets/reference-rates/"))
        self.assertIn(claim["text"], block)

    def test_chapter_one_keeps_the_nesting_and_the_ladder_under_go_deeper(self):
        start = self.page.index('<section id="plumbing">')
        chapter = self.page[start:self.page.index("</section>", start)]
        fold = chapter[chapter.index('<details class="wide" id="plumbing-deeper">'):]
        for part in ('id="seg-sofr"', 'id="seg-bgcr"', 'id="seg-tgcr"', 'id="corridor"'):
            self.assertIn(part, fold)
        self.assertNotIn("Cash comes from", self.page)
        self.assertIn('href="#n4"', chapter)


def html_unescape(text):
    import html
    return html.unescape(text)


class SegmentDayTests(unittest.TestCase):
    """N4's segment chart: its days come from inputs known in advance, never from a rate or a locked day.

    Recorded mutations, each applied once to `scripts/emit_visual.py`:
    * in `segment_days`, `if r["quarter_end"] == "1" and i > 0:` ->
      `if r["quarter_end"] == "1" and i > 0 and r["sofr"]:`.
      test_the_rule_reads_no_outcome_column then failed with KeyError ('sofr').
    * in `segment_days`, `if r["date"] >= before or locked_tier(today, locked) is not None:` ->
      `if r["date"] >= before:`. test_a_locked_day_is_never_chosen then failed with
      AssertionError (the 2025 days under the synthetic tier were chosen).
    * in `on_rrp_as_of`, `position = bisect.bisect_right(times, instant) - 1` ->
      `position = len(times) - 1`. test_the_on_rrp_reading_was_public_at_the_decision then
      failed with AssertionError (a reading published after the decision was used).
    """

    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
        cls.rows = list(csv.DictReader(raw.decode().splitlines()))
        cls.locked = lockbox.locked_tiers(PRE_OPENING_LOCKBOX)
        cls.registry = json.loads((ROOT / emit_visual.SOURCES).read_text(encoding="utf-8"))
        cls.on_rrp, _ = emit_visual.on_rrp_results(ROOT)
        cls.decision = emit_visual.time.fromisoformat(manifest["decision_time"])
        cls.days = cls.choose(cls.rows)

    @classmethod
    def choose(cls, rows, locked=None):
        return emit_visual.segment_days(rows, cls.locked if locked is None else locked, cls.on_rrp, cls.registry,
                                        cls.decision)

    def test_the_rule_chooses_days_of_both_kinds(self):
        """Otherwise the tests below would hold vacuously."""
        kinds = {w for d in self.days for w in d["why"]}
        self.assertEqual(kinds, {"quarter_end", "tax_coupon"})

    def test_the_rule_reads_no_outcome_column(self):
        stripped = [{k: r[k] for k in emit_visual.SEGMENT_RULE_COLUMNS} for r in self.rows]
        self.assertEqual(self.choose(stripped), self.days)

    def test_perturbing_every_rate_changes_no_day(self):
        moved = copy.deepcopy(self.rows)
        for r in moved:
            for column in ("sofr", "tgcr", "bgcr", "iorb", "sofr_p25", "sofr_p75", "sofr_volume"):
                if r.get(column):
                    r[column] = str(float(r[column]) + 3.0)
        self.assertEqual(self.choose(moved), self.days)

    def test_every_day_meets_a_clause_of_the_rule(self):
        by_date = {r["date"]: r for r in self.rows}
        deadlines = {emit_visual.corporate_tax_deadline(y, m).isoformat()
                     for y in range(2018, 2027) for m in emit_visual.TAX_DEADLINE_MONTHS}
        for d in self.days:
            with self.subTest(day=d["date"]):
                self.assertLess(d["date"], emit_visual.SEGMENT_DAY_RULE["before"])
                r = by_date[d["date"]]
                if "quarter_end" in d["why"]:
                    self.assertEqual(r["quarter_end"], "1")
                    self.assertLess(d["on_rrp"]["bn"], emit_visual.SEGMENT_DAY_RULE["on_rrp_below_bn"])
                if "tax_coupon" in d["why"]:
                    self.assertIn(d["date"], deadlines)
                    self.assertGreater(float(r["treasury_settlement_coupons"]), 0)

    def test_a_locked_day_is_never_chosen(self):
        """Under a tier that starts inside 2025, its days drop out, and perturbing them changes nothing."""
        document = json.loads(PRE_OPENING_LOCKBOX.read_text(encoding="utf-8"))
        document["tiers"][0]["start"] = "2025-07-01"
        import tempfile
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "lockbox.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        locked = lockbox.locked_tiers(path)
        chosen = self.choose(self.rows, locked)
        self.assertTrue(any(d["date"] >= "2025-07-01" for d in self.days))
        self.assertFalse([d["date"] for d in chosen if d["date"] >= "2025-07-01"])
        moved = copy.deepcopy(self.rows)
        for r in moved:
            if "2025-07-01" <= r["date"] < "2026-01-01":
                r["quarter_end"] = "1"
                r["treasury_settlement_coupons"] = "100"
        self.assertEqual(self.choose(moved, locked), chosen)
        self.assertIn("are held out", emit_visual.segment_held_note(locked))

    def test_the_on_rrp_reading_was_public_at_the_decision(self):
        """Each quarter-end reads the result public at 16:00 on the panel day before it, and no later one."""
        dates = [r["date"] for r in self.rows]
        public = {ref.isoformat(): at for ref, at, _ in self.on_rrp}
        zone = emit_visual.ZoneInfo(self.registry[emit_visual.NYFED_ON_RRP_SOURCE_ID]["release_lag"]["timezone"])
        for d in self.days:
            if d["on_rrp"] is None:
                continue
            with self.subTest(day=d["date"]):
                before = emit_visual.date.fromisoformat(dates[dates.index(d["date"]) - 1])
                instant = emit_visual.datetime.combine(before, self.decision, zone)
                self.assertLessEqual(public[d["on_rrp"]["ref"]], instant)
                later = [ref for ref, at, _ in self.on_rrp if at <= instant and ref.isoformat() > d["on_rrp"]["ref"]]
                self.assertEqual(later, [])

    def test_the_caption_states_the_rule(self):
        page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")
        self.assertIn("every quarter-end before 1 January 2026", page)
        self.assertIn(f"below ${emit_visual.SEGMENT_DAY_RULE['on_rrp_below_bn']:,.0f}bn", page)
        self.assertIn("The rule never reads a rate or a spread", page)


# ---------------------------------------------------------------- N5 "A quarter-end squeeze, step by step" (#146)


class NewcomerN5Base(unittest.TestCase):
    """N5's inputs, built once: the panel, the ON RRP, SOFR and EFFR snapshots, and N4's tag statuses."""

    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
        cls.rows = list(csv.DictReader(raw.decode().splitlines()))
        cls.locked = lockbox.locked_tiers(PRE_OPENING_LOCKBOX)
        cls.registry = json.loads((ROOT / emit_visual.SOURCES).read_text(encoding="utf-8"))
        cls.notes = json.loads((ROOT / emit_visual.ANNOTATIONS).read_text(encoding="utf-8"))
        cls.tag_map = json.loads((ROOT / emit_visual.MAP).read_text(encoding="utf-8"))
        cls.decision = emit_visual.time.fromisoformat(manifest["decision_time"])
        cls.on_rrp, _ = emit_visual.on_rrp_results(ROOT)
        cls.snaps, _ = emit_visual.n5_snapshots(ROOT)
        snapshot = json.loads((ROOT / emit_visual.ISSUES).read_text(encoding="utf-8"))
        cls.tags = emit_visual.tag_statuses(cls.tag_map, cls.registry, manifest,
                                            emit_visual.run_record_declarations(ROOT), snapshot,
                                            emit_visual.tracked_snapshots(ROOT))
        cls.chosen = cls.choose(cls.rows)
        cls.base = cls.run_n5(cls.rows)

    @classmethod
    def choose(cls, rows, locked=None):
        return emit_visual.n5_quarter_ends(rows, cls.locked if locked is None else locked, cls.on_rrp,
                                           cls.registry, cls.decision)

    @classmethod
    def run_n5(cls, rows, locked=None, snaps=None, tags=None):
        locked = cls.locked if locked is None else locked
        return emit_visual.newcomer_n5(copy.deepcopy(rows), locked, cls.choose(rows, locked), cls.registry,
                                       cls.decision, cls.snaps if snaps is None else snaps, cls.tag_map,
                                       cls.tags if tags is None else tags, cls.notes)

    def is_locked(self, iso):
        return lockbox.locked_tier(emit_visual.date.fromisoformat(iso), self.locked) is not None


class NewcomerN5RuleTests(NewcomerN5Base):
    """The two worked quarter-ends follow Eleonora's rule (answer 10 on #141), from inputs only.

    Recorded mutation: in `n5_quarter_ends`, `if r["quarter_end"] != "1" or i == 0 or r["date"] >= before:`
    -> `if r["quarter_end"] != "1" or i == 0 or r["date"] >= before or not r["sofr"]:`.
    test_the_rule_reads_no_outcome_column then failed with KeyError ('sofr').
    """

    def test_the_rule_is_a_declared_constant(self):
        from repo_model import contract
        self.assertEqual(emit_visual.N5_QUARTER_END_RULE,
                         {"before": "2026-01-01", "scarce_below_bn": contract.ON_RRP_DEPLETION_BREAK_BN})

    def test_scarce_is_the_most_recent_below_the_break_and_abundant_the_largest(self):
        """Recomputed here from the panel's quarter-end flag and the as-of ON RRP read."""
        readings = []
        for i, r in enumerate(self.rows):
            if r["quarter_end"] == "1" and i and r["date"] < "2026-01-01" and not self.is_locked(r["date"]):
                prev = emit_visual.date.fromisoformat(self.rows[i - 1]["date"])
                readings.append((r["date"], emit_visual.on_rrp_as_of(self.on_rrp, prev, self.decision,
                                                                     self.registry)[1]))
        below = [d for d, v in readings if v < emit_visual.ON_RRP_DEPLETION_BREAK_BN]
        self.assertEqual(self.chosen["scarce"]["date"], below[-1])
        self.assertEqual(self.chosen["abundant"]["date"], max(readings, key=lambda o: o[1])[0])
        self.assertNotEqual(self.chosen["scarce"]["date"], self.chosen["abundant"]["date"])

    def test_the_rule_reads_no_outcome_column(self):
        stripped = [{k: r[k] for k in emit_visual.N5_RULE_COLUMNS} for r in self.rows]
        self.assertEqual(self.choose(stripped), self.chosen)

    def test_perturbing_every_rate_changes_no_choice(self):
        moved = copy.deepcopy(self.rows)
        for r in moved:
            for column in ("sofr", "tgcr", "bgcr", "iorb", "sofr_p25", "sofr_p75", "sofr_volume"):
                if r[column]:
                    r[column] = str(float(r[column]) + 3.0)
        self.assertEqual(self.choose(moved), self.chosen)

    def test_a_locked_day_is_never_chosen(self):
        document = json.loads(PRE_OPENING_LOCKBOX.read_text(encoding="utf-8"))
        document["tiers"][0]["start"] = "2025-07-01"
        import tempfile
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "lockbox.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        chosen = self.choose(self.rows, lockbox.locked_tiers(path))
        self.assertGreaterEqual(self.chosen["scarce"]["date"], "2025-07-01")
        for kind in ("scarce", "abundant"):
            self.assertLess(chosen[kind]["date"], "2025-07-01")

    def test_the_reading_was_public_at_the_decision_the_day_before(self):
        zone = emit_visual.ZoneInfo(self.registry[emit_visual.NYFED_ON_RRP_SOURCE_ID]["release_lag"]["timezone"])
        public = {ref.isoformat(): at for ref, at, _ in self.on_rrp}
        dates = [r["date"] for r in self.rows]
        for kind, q in self.chosen.items():
            with self.subTest(kind=kind):
                self.assertEqual(q["decision_day"], dates[dates.index(q["date"]) - 1])
                instant = emit_visual.datetime.combine(emit_visual.date.fromisoformat(q["decision_day"]),
                                                       self.decision, zone)
                self.assertLessEqual(public[q["on_rrp"]["ref"]], instant)

    def test_the_caption_states_the_rule(self):
        _, fills = self.base
        self.assertIn("the most recent quarter-end before 1 January 2026", fills["n5_rule"])
        self.assertIn("the largest", fills["n5_rule"])
        self.assertIn(f"${emit_visual.ON_RRP_DEPLETION_BREAK_BN:,.0f}bn", fills["n5_rule"])
        self.assertIn("never reads a rate or a spread", fills["n5_rule"])


class NewcomerN5ClockTests(NewcomerN5Base):
    """Each chart marks what was public at the decision instant: the declared time on the day before the quarter-end.

    Recorded mutation: in `n5_series`, `if all(at <= instant for at in ats):`
    -> `if all(at <= instant + timedelta(days=2) for at in ats):`.
    test_a_daily_rate_is_known_two_days_back then failed with AssertionError
    (a later day's rate was marked public).
    """

    def test_a_daily_rate_is_known_two_days_back(self):
        """SOFR and EFFR for a day are public at 15:00 the next business day, so 16:00 on day -1 sees day -2."""
        data, _ = self.base
        for key in ("spread", "sofr_p99", "effr"):
            for kind in ("scarce", "abundant"):
                with self.subTest(series=key, kind=kind):
                    self.assertEqual(data["series"][key]["known"][kind], -2)

    def test_a_scheduled_settlement_is_known_before_the_day(self):
        data, _ = self.base
        for kind in ("scarce", "abundant"):
            self.assertGreaterEqual(data["series"]["treasury_settlement"]["known"][kind], 0)

    def test_every_value_marked_known_was_public(self):
        data, _ = self.base
        for key, s in data["series"].items():
            for kind, q in data["quarter_ends"].items():
                with self.subTest(series=key, kind=kind):
                    known = s["known"][kind]
                    if known is None:  # nothing in the window was public yet, as for the weekly dealer positions
                        self.assertEqual(s["public_offsets"][kind], [])
                        continue
                    self.assertEqual(known, max(s["public_offsets"][kind]))
                    self.assertLess(known, 1, "a value after the quarter-end cannot be public the day before it")
                    self.assertTrue(all(not d["held"] for d in q["days"] if d["offset"] <= known))

    def test_a_snapshot_clock_honours_the_declared_business_day(self):
        """A snapshot read is public no earlier than its registry declaration on the panel's dates (#200 review).

        The NY Fed snapshots declare one business day, as the panel's SOFR does,
        so on 31 December 2025 every one of them is public on the same panel day
        as SOFR, never on the 1 January holiday.

        Recorded mutation: in `n5_available`,
        `return adapter if declared is None else max(adapter, declared)` -> `return adapter`.
        This test then failed with AssertionError ('1 calendar day later' != '2 calendar days later').
        """
        data, _ = self.base
        gap = re.compile(r"(\d+) calendar days? (?:later|before)|the same day")
        sofr = gap.search(data["series"]["spread"]["clock"]["scarce"]).group(0)
        for key in ("on_rrp", "sofr_p99", "effr", "srf"):
            with self.subTest(series=key):
                self.assertEqual(gap.search(data["series"][key]["clock"]["scarce"]).group(0), sofr)

    def test_a_weekly_release_is_older_than_the_window(self):
        """FR 2004 positions are public six business days later, so none in the window was public yet."""
        data, _ = self.base
        for kind in ("scarce", "abundant"):
            self.assertIsNone(data["series"]["dealer_treasury_position"]["known"][kind])


class NewcomerN5HeldOutDayTests(NewcomerN5Base):
    """Locked days change no value, count or sentence in N5 (#141 ruling 3).

    The scarce quarter-end's window runs into the near-blind tier. Those days
    are listed by date, with no value, and the chart draws them greyed and
    labelled "held out". Perturbing every panel value and every snapshot value
    on a locked day leaves N5's data and fills unchanged.

    Recorded mutation: in `newcomer_n5`, `held = locked_tier(today, locked) is not None`
    -> `held = False`. test_locked_perturbation_changes_nothing then failed with
    AssertionError (the window's values and the table moved).
    """

    def test_a_window_reaches_into_a_locked_tier(self):
        data, _ = self.base
        held = [d for q in data["quarter_ends"].values() for d in q["days"] if d["held"]]
        self.assertTrue(held)
        self.assertTrue(all(self.is_locked(d["date"]) for d in held))

    def test_held_days_carry_no_value(self):
        data, _ = self.base
        for key, s in data["series"].items():
            for kind, q in data["quarter_ends"].items():
                for d, v in zip(q["days"], s["values"][kind]):
                    if d["held"]:
                        self.assertIsNone(v, (key, d["date"]))

    def test_locked_perturbation_changes_nothing(self):
        rows = copy.deepcopy(self.rows)
        for r in rows:
            if self.is_locked(r["date"]):
                for column, value in r.items():
                    if column not in ("date", "quarter_end", "tax_date", "days_to_month_end") and value:
                        r[column] = str(float(value) * 3 + 50)
        snaps = {key: dict(s, by_ref={ref: (at, value * 3 + 50 if self.is_locked(ref.isoformat()) else value)
                                      for ref, (at, value) in s["by_ref"].items()})
                 for key, s in self.snaps.items()}
        self.assertEqual(self.run_n5(rows, snaps=snaps), self.base)

    def test_unlocked_perturbation_is_seen(self):
        rows = copy.deepcopy(self.rows)
        index = next(i for i, r in enumerate(rows) if r["date"] == self.chosen["scarce"]["date"])
        rows[index - 1]["sofr"] = "9.99"
        self.assertNotEqual(self.run_n5(rows), self.base)

    def test_the_held_note_says_held_out(self):
        _, fills = self.base
        self.assertIn("held out", fills["n5_held_note"])


class NewcomerN5StepTests(NewcomerN5Base):
    """The steps: the order the plan gives, each sourced, the tail a hypothesis, no data no chart."""

    def test_every_step_rests_on_sourced_claims_and_known_parts(self):
        tags = {t["key"] for t in self.tag_map["tags"]}
        for step in self.tag_map["steps"]:
            with self.subTest(step=step["key"]):
                self.assertTrue(step["claims"])
                for claim in step["claims"]:
                    self.assertTrue(self.notes["claims"][claim]["src"].startswith(emit_visual.ALLOWED_SOURCES))
                self.assertLessEqual(set(step["tags"]), tags)
                self.assertLessEqual(set(step["flows"]), set(self.tag_map["flows"]))
                self.assertLessEqual(set(step["series"]), set(emit_visual.N5_SERIES))

    def test_an_unsourced_claim_is_refused(self):
        notes = copy.deepcopy(self.notes)
        notes["claims"]["tga_reserves"]["src"] = "https://example.com/"
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.check_steps(self.tag_map, notes)

    def test_the_banks_step_comes_after_the_sofr_steps(self):
        keys = [s["key"] for s in self.tag_map["steps"]]
        self.assertLess(keys.index("spread"), keys.index("banks"))
        self.assertLess(keys.index("tail"), keys.index("spread"))

    def test_the_tail_is_a_hypothesis_under_test(self):
        _, fills = self.base
        panel = fills["n5_panels"].split('id="n5p-tail"')[1].split('<div class="n5p"')[0]
        self.assertIn("Hypothesis under test", panel)
        self.assertIn("issues/127", panel)
        self.assertIn("not a finding", panel)

    def without_chart(self, step_key):
        tag_map = copy.deepcopy(self.tag_map)
        next(s for s in tag_map["steps"] if s["key"] == step_key)["series"] = []
        return tag_map

    def test_a_step_with_no_tracked_data_says_so(self):
        """A step whose tags have no tracked data draws no chart and says so, from the tags' own derivation."""
        tags = copy.deepcopy(self.tags)
        next(t for t in tags if t["key"] == "srf")["data_in_repo"] = False
        _, fills = emit_visual.newcomer_n5(copy.deepcopy(self.rows), self.locked, self.chosen, self.registry,
                                           self.decision, self.snaps, self.without_chart("srf"), tags, self.notes)
        panel = fills["n5_panels"].split('id="n5p-srf"')[1]
        self.assertIn("no public series in this repository yet", panel)

    def test_a_step_with_data_but_no_chart_is_refused(self):
        """The SRF take-up is tracked, so its step must draw it."""
        self.assertTrue(next(t for t in self.tags if t["key"] == "srf")["data_in_repo"])
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.newcomer_n5(copy.deepcopy(self.rows), self.locked, self.chosen, self.registry,
                                    self.decision, self.snaps, self.without_chart("srf"), self.tags, self.notes)

    def test_a_tag_that_is_not_used_carries_its_status(self):
        _, fills = self.base
        for t in self.tags:
            if any(t["key"] in s["tags"] for s in self.tag_map["steps"]) and t["status"] != "used":
                word = next(w for k, _, w in emit_visual.STATUSES if k == t["status"])
                with self.subTest(tag=t["key"]):
                    self.assertRegex(fills["n5_panels"], rf"{re.escape(t['label'])}\s*<small>{word}</small>")


class NewcomerN5PageTests(unittest.TestCase):
    page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")

    def section(self):
        block = newcomer_block(self.page)
        return block[block.index('<section id="n5"'):].split("</section>")[0]

    def test_n5_is_on_the_page_and_in_the_nav(self):
        self.assertRegex(newcomer_block(self.page), r'<nav aria-label="Start here">.*href="#n5"')

    def test_the_walkthrough_has_previous_next_and_a_live_region(self):
        section = self.section()
        self.assertRegex(section, r'<button type="button" id="n5prev"[^>]*>Previous')
        self.assertRegex(section, r'<button type="button" id="n5next"[^>]*>Next')
        self.assertIn('aria-live="polite"', section)

    def test_the_map_copy_is_named_and_its_ids_are_its_own(self):
        section = self.section()
        self.assertRegex(section, r'<svg[^>]*role="img" aria-label="Map of who lends')
        ids = re.findall(r'\sid="([^"]+)"', self.page)
        mine = re.findall(r'\sid="([^"]+)"', re.sub(r"<dfn.*?<!--/def-->", " ", section, flags=re.S))
        self.assertTrue(mine)
        for i in mine:
            with self.subTest(id=i):
                self.assertEqual(ids.count(i), 1, f"N5's id {i!r} is used elsewhere on the page")

    def test_every_link_is_a_primary_source(self):
        section = re.sub(r"<span class=\"def\"[^>]*>.*?</span><!--/def-->", " ", self.section(), flags=re.S)
        links = re.findall(r"href=['\"](https?://[^'\"]+)['\"]", section)
        self.assertTrue(links)
        for url in links:
            with self.subTest(url=url):
                self.assertTrue(url.startswith(emit_visual.ALLOWED_SOURCES))

    def test_the_data_file_names_every_snapshot_it_read(self):
        doc = json.loads((ROOT / emit_visual.DATA_DIR / "newcomer_n5.json").read_text(encoding="utf-8"))
        inputs = doc["provenance"]["inputs"]
        for root in (emit_visual.ON_RRP, emit_visual.SOFR_RATES, emit_visual.EFFR, emit_visual.SRF):
            snaps = sorted(p for p in (ROOT / root).glob("*.json") if not p.name.endswith(".manifest.json"))
            self.assertTrue(snaps, root)
            for path in snaps:
                rel = str(path.relative_to(ROOT))
                with self.subTest(path=rel):
                    self.assertEqual(inputs[rel], emit_visual.sha256(path))


# ---------------------------------------------------------------- the final test on the site (#238)


def final_test_block(page):
    """The final test's section on the page, from its opening tag to its close."""
    start = page.index('<section id="final-test"')
    return page[start:page.index("</section>", start)]


def visible_text(block):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", block)))


class FinalTestSectionTests(unittest.TestCase):
    """#238: the final test's result on the site, read off `docs/runs/final_test_near_blind.json`.

    Every figure is read from the record through `from_record`; the committed
    page and data must carry the record's values, so a record that drifts from
    the page fails here as well as in the byte-for-byte regeneration test.
    """

    page = (ROOT / emit_visual.PAGE).read_text(encoding="utf-8")
    record = json.loads((ROOT / "docs/runs/final_test_near_blind.json").read_text(encoding="utf-8"))

    @classmethod
    def setUpClass(cls):
        cls.records = published_records()
        cls.locked = lockbox.locked_tiers(ROOT / emit_visual.LOCKBOX)
        cls.data, cls.fills = emit_visual.final_test(cls.records, cls.locked)
        cls.block = final_test_block(cls.page)
        cls.text = visible_text(cls.block)

    def test_the_record_is_an_input(self):
        self.assertIn(emit_visual.FINAL_TEST, emit_visual.INPUTS)
        doc = json.loads((ROOT / emit_visual.DATA_DIR / "final_test.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["provenance"]["inputs"],
                         {emit_visual.FINAL_TEST: emit_visual.sha256(ROOT / emit_visual.FINAL_TEST)})

    def test_the_figures_are_the_records_values(self):
        cell = self.record["primary"]["cell"]
        doc = json.loads((ROOT / emit_visual.DATA_DIR / "final_test.json").read_text(encoding="utf-8"))
        for data in (self.data, doc["data"]):
            self.assertEqual(data["persistence"], cell["crps_persistence_bps"])
            self.assertEqual(data["published"], cell["crps_published_bps"])
            self.assertEqual(data["mean"], cell["mean_difference_bps"])
            self.assertEqual(data["lower"], cell["interval"]["lower"])
            self.assertEqual(data["upper"], cell["interval"]["upper"])
            self.assertEqual(data["level"], round(100 * cell["interval"]["level"]))
            self.assertEqual(data["days"], cell["days"])
            self.assertEqual(data["result"], cell["result"])
            for row in data["by_day_type"]:
                source = cell["splits"]["by_day_type"][row["key"]]
                with self.subTest(day_type=row["key"]):
                    self.assertEqual(row["count"], source["count"])
                    self.assertEqual(row["mean"], source["mean"])
                    self.assertEqual(row.get("lower"), source.get("interval", {}).get("lower"))
                    self.assertEqual(row.get("upper"), source.get("interval", {}).get("upper"))

    def test_the_page_quotes_the_record(self):
        cell = self.record["primary"]["cell"]
        for value in (cell["crps_published_bps"], cell["crps_persistence_bps"]):
            self.assertIn(f"{value:.2f} bp", self.text)
        lo, hi = cell["interval"]["lower"], cell["interval"]["upper"]
        self.assertIn(f"+{lo:.2f} to +{hi:.2f} bp", self.text)
        self.assertIn(f"{cell['result']}", self.text)
        for key, entry in cell["splits"]["by_day_type"].items():
            with self.subTest(day_type=key):
                self.assertIn(f"<td>{entry['count']}</td>", self.block)

    def test_a_drifted_record_moves_the_section(self):
        records = copy.deepcopy(self.records)
        records[emit_visual.FINAL_TEST]["primary"]["cell"]["crps_published_bps"] = 1.7123
        data, fills = emit_visual.final_test(records, self.locked)
        self.assertEqual(data["published"], 1.7123)
        self.assertIn("1.71 bp", fills["ft_verdict"])
        self.assertNotEqual(fills["ft_verdict"], self.fills["ft_verdict"])

    def test_a_missing_figure_is_refused(self):
        records = copy.deepcopy(self.records)
        del records[emit_visual.FINAL_TEST]["primary"]["cell"]["interval"]
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.final_test(records, self.locked)
        records = copy.deepcopy(self.records)
        del records[emit_visual.FINAL_TEST]
        with self.assertRaises(emit_visual.VisualError):
            emit_visual.final_test(records, self.locked)

    def test_the_claim_is_the_preregistered_one(self):
        self.assertIn(self.record["primary"]["claim"], self.text)
        self.assertNotRegex(self.text.lower(), r"warns? of stress")
        self.assertNotRegex(self.page.lower(), r"warns of stress")

    def test_a_pass_is_never_stated_without_the_near_blind_disclosure(self):
        for paragraph in re.findall(r"<(p|li)[^>]*>(.*?)</\1>", self.block, re.S):
            words = visible_text(paragraph[1])
            if re.search(r"\bpass\b", words):
                with self.subTest(paragraph=words[:80]):
                    self.assertIn("near-blind", words)

    def test_a_failed_test_states_no_claim(self):
        records = copy.deepcopy(self.records)
        records[emit_visual.FINAL_TEST]["primary"]["cell"]["result"] = "fail"
        records[emit_visual.FINAL_TEST]["primary"]["cell"]["interval"]["lower"] = -0.01
        _, fills = emit_visual.final_test(records, self.locked)
        self.assertNotIn(self.record["primary"]["claim"], " ".join(map(str, fills.values())))
        self.assertIn("not shown", fills["ft_verdict"])

    def test_cells_too_small_for_an_interval_say_so(self):
        split = self.record["primary"]["cell"]["splits"]["by_day_type"]
        thin = [k for k, v in split.items() if "interval" not in v]
        self.assertTrue(thin)
        self.assertEqual(self.block.count("too few days for an interval"), len(thin))
        self.assertIn("decides nothing", self.text)

    def test_the_stress_cells_are_named_inconclusive_with_their_events(self):
        h1 = next(d for d in self.record["events_reported_only"] if d["horizon"] == 1)
        for key in ("+5bp", "+10bp"):
            entry = h1["targets"][key]["all_days"]
            with self.subTest(target=key):
                self.assertEqual({p["label"] for p in entry["paired"].values()}, {"inconclusive"})
        self.assertIn("not a warning of stress", self.text)
        self.assertIn(f"{h1['targets']['+5bp']['all_days']['events']} and "
                      f"{h1['targets']['+10bp']['all_days']['events']}", self.text)

    def test_horizons_two_to_five_carry_the_verbatim_label(self):
        label = ("different model from h = 1, and as-of persistence does not widen with horizon, so this "
                 "comparison favours the model; not evidence.")
        cells = self.record["crps_reported_only"]
        self.assertTrue(cells)
        rows = re.findall(r"<tr data-h=\"(\d)\">(.*?)</tr>", self.block, re.S)
        self.assertEqual(sorted(int(h) for h, _ in rows), sorted(c["horizon"] for c in cells))
        for h, row in rows:
            with self.subTest(horizon=h):
                self.assertIn(label, visible_text(row))

    def test_the_section_sits_after_start_here_before_the_chapters(self):
        at = self.page.index('<section id="final-test"')
        self.assertLess(self.page.index("<!-- /start-here -->"), at)
        self.assertLess(at, self.page.index('<section id="plumbing">'))
        self.assertIn('href="#final-test"', self.page[:self.page.index("<!-- start-here -->")])
        self.assertRegex(self.block, r'<svg|id="ftchart"')

    def test_the_nav_item_carries_no_result_marker(self):
        """Review of c39eab4 on #240: a typed check mark beside "The final test" in the nav read as
        "passed" whatever the record said, with no near-blind disclosure beside it. The nav item's
        marker is neutral; the result is stated only in the section, read off the record."""
        template = (ROOT / emit_visual.TEMPLATE).read_text(encoding="utf-8")
        for name, text in (("template", template), ("page", self.page)):
            with self.subTest(source=name):
                item = re.search(r'<li[^>]*><b>([^<]*)</b><span><a href="#final-test">', text)
                self.assertIsNotNone(item)
                marker = html.unescape(item.group(1)).strip()
                self.assertTrue(marker)
                self.assertFalse(set(marker) & set("\u2713\u2714\u2717\u2718\u2715\u2716\u2705\u274c\u2611\u2612"), marker)
                self.assertNotRegex(marker, r"(?i)pass|fail|^x$|[&#;]")

    def test_it_links_the_record_and_its_documents(self):
        for path in (emit_visual.FINAL_TEST, "docs/final-test.md", "docs/decisions/final-test-preregistration.md"):
            with self.subTest(path=path):
                self.assertIn(f"https://github.com/{emit_visual.REPOSITORY}/blob/main/{path}", self.block)

    def test_the_blind_days_are_never_called_the_final_test(self):
        self.assertNotIn("held out for the project's final test", self.page)
        self.assertNotIn("final test period", self.page)
        for fills in (emit_visual.segment_held_note(self.locked),):
            self.assertIn("blind tier", fills)

    def _rests_figures(self, record=None):
        """The post hoc figures, computed here from the record's own window and bootstrap."""
        from repo_model.metrics import stationary_bootstrap_interval
        record = record or self.record
        window = record["primary"]["window_per_origin"]
        iv = record["primary"]["cell"]["interval"]
        diffs = [r["difference_bps"] for r in window]
        top = sorted(range(len(diffs)), key=lambda i: -diffs[i])[:2]
        rest = [v for i, v in enumerate(diffs) if i not in top]
        lower, upper = stationary_bootstrap_interval(
            lambda ix: sum(rest[i] for i in ix) / len(ix), len(rest), block_length=iv["block_length"],
            seed=iv["seed"], replications=iv["replications"], level=iv["level"])
        return {"days": sorted(window[i]["scored_date"] for i in top),
                "share": sum(diffs[i] for i in top) / sum(diffs),
                "mean": sum(rest) / len(rest), "lower": lower, "upper": upper,
                "wins": sum(v > 0 for v in diffs), "n": len(diffs)}

    def test_what_the_pass_rests_on_follows_the_record(self):
        """#238, hold ruling item 1: a generated, post hoc sentence under "What it does not show"."""
        f = self._rests_figures()
        text = visible_text(self.fills["ft_rests"])
        self.assertIn("post hoc", text)
        self.assertIn(f"{100 * f['share']:.1f}%", text)
        self.assertIn(f"{f['wins']} of {f['n']}", text)
        self.assertIn(f"{emit_visual.signed(f['mean'], 3)}", text)
        self.assertIn(f"{emit_visual.signed(f['lower'], 3)}", text)
        self.assertIn(f"{emit_visual.signed(f['upper'], 3)}", text)
        for iso in f["days"]:
            self.assertIn(emit_visual.short_day(iso).split(" ", 1)[0], text)
        self.assertIn("verdict stands", text)
        self.assertIn(self.fills["ft_rests"], self.block)
        self.assertEqual(self.data["rests"]["share"], f["share"])
        self.assertEqual(self.data["rests"]["wins"], f["wins"])

    def test_what_the_pass_rests_on_moves_with_the_record(self):
        records = copy.deepcopy(self.records)
        window = records[emit_visual.FINAL_TEST]["primary"]["window_per_origin"]
        for r in window:
            r["difference_bps"] = 0.1
        data, fills = emit_visual.final_test(records, self.locked)
        self.assertEqual(data["rests"]["wins"], len(window))
        self.assertNotEqual(fills["ft_rests"], self.fills["ft_rests"])
        self.assertIn(f"{100 * data['rests']['share']:.1f}%", fills["ft_rests"])

    def test_the_switch_of_the_primary_cell_is_stated(self):
        """#238, hold ruling item 2: the deciding cell was changed before the test was opened (#221)."""
        self.assertIn("4 October 2026", self.text)
        self.assertIn("plain-leap probability cell", self.text)
        self.assertIn("#216", self.text)
        self.assertRegex(self.block, r"href='[^']*issues/221[^']*'")
        self.assertIn("before the test was opened", self.text)

    def test_no_sentence_says_no_choice_of_model_was_made(self):
        """#238, hold ruling item 3: only the record's own hedge, "by name", may appear."""
        for text in (self.text, visible_text(" ".join(map(str, self.fills.values())))):
            self.assertNotRegex(text.lower(), r"no choice of model")
            self.assertNotRegex(text.lower(), r"no choice was made")
        self.assertIn("by name", self.text)

    def test_the_stress_windows_are_not_said_to_be_kept_out_of_the_score(self):
        """#238, hold ruling item 4: every published record pools those days."""
        template = (ROOT / "site/template.html").read_text(encoding="utf-8")
        for text in (self.page, template):
            self.assertNotIn("kept out of the headline score", text)
            self.assertNotIn("reported on their own", text)

    def test_readme_links_the_section_from_the_explorer_line(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        line = next(l for l in readme.splitlines() if "[the explorer](" in l)
        self.assertIn("https://eleonorabjornberg.github.io/repo-market-model/#final-test", line)


if __name__ == "__main__":
    unittest.main()
