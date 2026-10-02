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


# ---------------------------------------------------------------- N3 "When does it happen?" (#141, #147)


class NewcomerN3Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / emit_visual.MANIFEST).read_text(encoding="utf-8"))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw, _ = emit_visual.build_panel(ROOT, manifest, tmp)
        cls.rows = list(csv.DictReader(raw.decode().splitlines()))
        cls.locked = lockbox.locked_tiers(ROOT / emit_visual.LOCKBOX)
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


if __name__ == "__main__":
    unittest.main()
