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

    def test_no_run_record_result_is_read(self):
        """No figure from a run record: only N4's status engine reads docs/runs/, and only declarations.

        `run_record_declarations` keeps a record's declaration, its derived
        fields and a comparison's verdict, and nothing else (#141 §3).
        """
        self.assertEqual(emit_visual.MODEL_RECORDS, ())
        for rel, data in self.outputs.items():
            if rel.endswith(".json") and not rel.endswith("/newcomer_n4.json"):
                for path in json.loads(data)["provenance"]["inputs"]:
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
        cls.locked = lockbox.locked_tiers(ROOT / emit_visual.LOCKBOX)
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
        cls.locked = lockbox.locked_tiers(ROOT / emit_visual.LOCKBOX)
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


if __name__ == "__main__":
    unittest.main()
