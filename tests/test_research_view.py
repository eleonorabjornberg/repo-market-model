"""The research sections of the results page (#645): `scripts/research_view.py`, `site/index.html`.

The page reads, top to bottom: executive summary, a contents list, current best performer, H1 to H10, then the
background and detailed records. The executive summary is prose with no table, and each hypothesis is one line (its
id and a tagline from `docs/research/taglines.json`) that opens a native <details> fold holding everything else
(#893). Every figure is parsed from tracked sources (`docs/research/`), and a figure nobody has measured
says so. These tests fix the order, refuse a hypothesis without a question or a milestone list, and check the
labels. They read the committed page; `tests/test_visual.py` refuses a stale one.

Recorded mutation (the order test): in `site/template.html` move the `id="best-performer"` section above the
`id="research-summary"` section, regenerate with `scripts/emit_visual.py`, and run
`PYTHONPATH=src:tests python3 -m unittest test_research_view.PageOrder`: `test_sections_in_order` failed with
AssertionError (the executive summary is not first).
"""

import html
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
import built_outputs

built_outputs.ensure()  # the page, its data and the log are built, not committed (#928)

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("research_view", ROOT / "scripts" / "research_view.py")
research_view = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(research_view)

PAGE = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
PLAN_IDS = re.findall(r"(?m)^## (H\d+)\b", (ROOT / "docs/research/plan.md").read_text(encoding="utf-8"))


def at(marker):
    found = PAGE.find(marker)
    assert found >= 0, f"the page has no {marker}"
    return found


class PageOrder(unittest.TestCase):
    def test_sections_in_order(self):
        order = [at('id="research-summary"'), at('id="best-performer"'), at('id="hypotheses"'),
                 at('id="background"')]
        self.assertEqual(order, sorted(order), "executive summary, best performer, hypotheses, background")
        self.assertLess(PAGE.find("<h1>"), order[0])

    def test_hypotheses_in_plan_order(self):
        found = re.findall(r'<article class="rs-h" id="(h\d+)"', PAGE)
        self.assertEqual(found, [h.lower() for h in PLAN_IDS])
        self.assertEqual(len(PLAN_IDS), 10)

    def test_existing_content_is_below(self):
        background = at('id="background"')
        for marker in ('id="start"', 'id="n1"', 'id="final-test"', 'id="history"', 'id="built"'):
            self.assertGreater(at(marker), background, marker)

    def test_a_contents_list_follows_the_summary_and_links_every_part(self):
        """#893: the tile grids became one contents list, between the executive summary and section 1."""
        contents = at('<nav aria-label="Contents"')
        self.assertLess(at('id="research-summary"'), contents)
        self.assertLess(contents, at('id="best-performer"'))
        nav = PAGE[contents:PAGE.find("</nav>", contents)]
        for target in ("best-performer", "hypotheses", "start", "n1", "n2", "n3", "n4", "n5", "final-test",
                       "forecast-actual", "plumbing", "history", "why", "clock", "forecast", "grading", "built",
                       "next", "terms"):
            self.assertIn(f'href="#{target}"', nav, target)
            self.assertIn(f'id="{target}"', PAGE, target)

    def test_each_hypothesis_has_question_milestones_and_owner(self):
        for hid in PLAN_IDS:
            block = PAGE[at(f'id="{hid.lower()}"'):]
            block = block[:block.find("</article>")]
            for label in ("Question", "How it is tested", "What would end it", "Where it stands"):
                self.assertIn(f"<dt>{label}</dt>", block, f"{hid} lacks {label}")

    def test_each_hypothesis_is_one_tagline_line_over_a_fold(self):
        """#893: the visible line is the id and its tagline; everything else sits inside the native <details>."""
        taglines = json.loads((ROOT / research_view.TAGLINES).read_text(encoding="utf-8"))["taglines"]
        for hid in PLAN_IDS:
            block = PAGE[at(f'<article class="rs-h" id="{hid.lower()}"'):]
            block = block[:block.find("</article>")]
            opened = re.match(r'<article class="rs-h"[^>]*>\s*<details class="rs-fold">\s*<summary>(.*?)</summary>(.*)'
                              r'</details>\s*$', block, re.S)
            self.assertIsNotNone(opened, f"{hid} is not one <details> fold")
            line, fold = opened.groups()
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", line)).strip()
            self.assertEqual(text, research_view.inline(taglines[hid]) + (" main aim" if hid == "H5" else " second aim" if hid == "H9" else ""), hid)
            self.assertNotRegex(line, r"<(?:br|p|div|ul|ol|dl|table)\b", hid)
            for label in ("Question", "How it is tested", "What would end it", "Where it stands"):
                self.assertIn(f"<dt>{label}</dt>", fold, hid)

    def test_owner_repository_of_h7_and_h10(self):
        for hid in ("H7", "H10"):
            block = PAGE[at(f'id="{hid.lower()}"'):]
            self.assertIn("companion project", block[:block.find("</article>")])


class Labels(unittest.TestCase):
    def test_development_entries_and_incumbent_carry_the_label(self):
        label = research_view.DEV_LABEL
        best = PAGE[at('id="best-performer"'):at('id="hypotheses"')]
        self.assertIn(label, best)
        for item in re.findall(r'<li><b>\d{4}-\d{2}-\d{2}</b>.*?</li>', PAGE, re.S):
            if "tier development" in item:
                self.assertIn(label, item)

    def test_the_executive_summary_is_prose_without_a_table(self):
        """#893, #1352: the summary states both aims in plain words, in running text, and holds no table."""
        summary = PAGE[at('id="research-summary"'):at('<nav aria-label="Contents"')]
        self.assertNotIn("<table", summary)
        self.assertNotRegex(summary, r"<(?:ul|ol|dl)\b")
        aims = json.loads((ROOT / research_view.SUMMARY).read_text(encoding="utf-8"))["aims"]
        for hid, aim in aims.items():
            self.assertIn(html.escape(aim.rstrip(".")), summary, hid)
        self.assertIn("tests on past data help build and choose a model but never settle the question", summary)
        self.assertIn("The main aim is", summary)
        self.assertIn("The second is", summary)

    def test_the_executive_summary_names_nothing_internal(self):
        """#1352 (Eleonora, 2 November 2026): the summary and its limits line are for a reader, not the project.

        No hypothesis, critical-path link or milestone id, no issue number, no repository file, no code, and no
        link into the repository. Mutation: `summary_html` given back its old `ref(h)` links fails here with
        AssertionError.
        """
        summary = PAGE[at('id="research-summary"'):at('<nav aria-label="Contents"')]
        text = re.sub(r"<[^>]+>", " ", summary)
        self.assertNotRegex(text, research_view.INTERNAL)
        self.assertNotIn("<code>", summary)
        self.assertNotIn("github.com", summary)
        self.assertNotRegex(summary, r'href="#h\d+"')

    def test_a_goal_or_link_without_a_plain_line_is_refused(self):
        """#1352: the summary never falls back to the plan's internal wording."""
        for key, part in (("H5", "aims"), ("H1.M3", "next")):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as tmp:
                out = Sources.copy_tree(self, tmp)
                path = out / research_view.SUMMARY
                data = json.loads(path.read_text(encoding="utf-8"))
                del data[part][key]
                path.write_text(json.dumps(data), encoding="utf-8")
                hypotheses = research_view.load(out)
                with self.assertRaisesRegex(research_view.ResearchError, "no plain"):
                    research_view.load_summary(out, hypotheses, research_view.load_critical_path(out, hypotheses))

    def test_a_plain_line_naming_something_internal_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Sources.copy_tree(self, tmp)
            path = out / research_view.SUMMARY
            data = json.loads(path.read_text(encoding="utf-8"))
            data["next"]["H1.M3"] = "finish H1 (see #768)"
            path.write_text(json.dumps(data), encoding="utf-8")
            hypotheses = research_view.load(out)
            with self.assertRaisesRegex(research_view.ResearchError, "internal"):
                research_view.load_summary(out, hypotheses, research_view.load_critical_path(out, hypotheses))

    def test_every_key_figure_carries_the_label(self):
        """#893: a pulled-out key number keeps the development marking."""
        callouts = re.findall(r'<aside class="callout"[^>]*>(.*?)</aside>', PAGE, re.S)
        self.assertTrue(callouts)
        for callout in callouts:
            self.assertIn(research_view.DEV_LABEL, callout)

    def test_unmeasured_figures_say_so(self):
        self.assertIn(research_view.NOT_MEASURED, research_view.standings_html(None))  # #1355: the folds hold no figures now
        self.assertIn("No conclusions yet", PAGE[at('id="research-summary"'):at('id="best-performer"')])

    def test_question_for_eleonora_is_marked(self):
        self.assertIn("Question for Eleonora", PAGE[at('id="best-performer"'):at('id="hypotheses"')])


def shown(start, end=None):
    """The text a reader sees between two markers of the built page: scripts, styles and tags gone, entities decoded."""
    block = PAGE[at(start):at(end)] if end else PAGE[at(start):]
    block = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", block, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", block)))


class PlainLanguageSections(unittest.TestCase):
    """#1355 (Eleonora, 2 November 2026, after #1352): the sections below the summary are for a reader, not the project.

    The masthead, section 1, section 2, the final-test, forecast and why-it-happens sections, view N6 and the
    source lines of view N4's cards show no hypothesis, link, milestone or issue id, no repository file, no code name
    of a model or arm, no benchmark label (B1, B2, B3), no `<code>`, and no ledger or "tracked directive" wording
    (`research_view.INTERNAL_PAGE`). A link may still lead to a file; its visible words are plain.

    Recorded mutation: in `scripts/research_view.py`, `hypothesis_html`, put `{h["id"]} ` back in front of the
    tagline inside `<summary>` (the old `rs-id` span) and run
    `PYTHONPATH=src:tests python3 -m unittest test_research_view.PlainLanguageSections`:
    `test_no_fold_line_starts_with_an_id` failed with AssertionError.
    """

    SECTIONS = {
        "masthead": ('<header class="masthead">', '<div class="prose intro">'),
        "section 1": ('id="best-performer"', 'id="hypotheses"'),
        "section 2": ('id="hypotheses"', 'id="background"'),
        "view N6": ('id="n6"', 'id="final-test"'),
        "section 4": ('id="final-test"', 'id="forecast-actual"'),
        "section 5": ('id="forecast-actual"', 'id="plumbing"'),
        "section 8": ('id="why"', 'id="clock"'),
    }

    def test_no_changed_section_shows_an_internal_reference(self):
        for name, (start, end) in self.SECTIONS.items():
            with self.subTest(section=name):
                text = shown(start, end)
                hit = research_view.INTERNAL_PAGE.search(text)
                self.assertIsNone(hit, f"{name}: {text[max(0, hit.start() - 60):hit.end() + 60] if hit else ''!r}")
                block = PAGE[at(start):at(end)]
                self.assertNotIn("<code>", re.sub(r"<script\b.*?</script>", "", block, flags=re.S), name)

    def test_the_view_n4_source_lines_name_no_file(self):
        """The status line and the stored-copy row of each card say it in words."""
        cards = re.findall(r'<p class="st">.*?</p>', PAGE, re.S)
        self.assertTrue(cards)
        for card in cards:
            self.assertNotRegex(re.sub(r"<[^>]+>", " ", card), research_view.INTERNAL_PAGE)
            self.assertNotIn("<code>", card)
        self.assertNotIn("Data in this repository", PAGE)

    def test_no_fold_line_starts_with_an_id(self):
        """Section 2 keeps no id in front of the line (her point 4 on #1355): a reader meets the plain line first."""
        for hid in PLAN_IDS:
            block = PAGE[at(f'<article class="rs-h" id="{hid.lower()}"'):]
            summary = re.search(r"<summary>(.*?)</summary>", block, re.S).group(1)
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", summary)).strip()
            self.assertNotRegex(text, r"\bH\d+\b", hid)
            self.assertNotIn("rs-id", summary)

    def test_a_question_without_a_plain_fold_is_refused(self):
        for hid in ("H1", "H10"):
            with self.subTest(hid=hid), tempfile.TemporaryDirectory() as tmp:
                out = Sources.copy_tree(self, tmp)
                path = out / research_view.SUMMARY
                data = json.loads(path.read_text(encoding="utf-8"))
                del data["questions"][hid]
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(research_view.ResearchError, "no plain"):
                    research_view.hypotheses_html(research_view.load(out), research_view.load_plain(out))

    def test_a_plain_text_naming_something_internal_is_refused(self):
        for section, edit in (("questions", lambda d: d["questions"]["H2"].update(test="the tests of H2 (see #629)")),
                              ("models", lambda d: d["models"]["B1"].update(name="B1, persistence")),
                              ("candidate", lambda d: d["candidate"].update(description="sc_s3c_ann_net, a model"))):
            with self.subTest(section=section), tempfile.TemporaryDirectory() as tmp:
                out = Sources.copy_tree(self, tmp)
                path = out / research_view.SUMMARY
                data = json.loads(path.read_text(encoding="utf-8"))
                edit(data)
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(research_view.ResearchError, "internal"):
                    research_view.load_plain(out)

    def test_the_guard_catches_what_it_is_for(self):
        for bad in ("H5", "CP2", "M3", "#1352", "docs/runs/x.json", "sc_s3c_ann_net", "(s3c-ann-net)", "B1", "B1\u2032",
                    "MME", "twCRPS", "Lens C", "a tracked directive", "ledger item 77", "phase 2 models", "spread_mr_ctx"):
            with self.subTest(bad=bad):
                self.assertRegex(f"as in {bad} here", research_view.INTERNAL_PAGE)
        for fine in ("The scorer ranks forecasts correctly.", "SOFR minus IORB, in basis points", "the H.8 release",
                     "a model that learns from many inputs at once"):
            with self.subTest(fine=fine):
                self.assertNotRegex(fine, research_view.INTERNAL_PAGE)


class Standings(unittest.TestCase):
    """#1020: the page shows the development standings of the candidate the committed record names.

    It used to print "not measured" for the development leader while `docs/pivot/evidence/h5-step4/score.json` named
    `gbm_funding`. The page reads that record, `docs/pivot/evidence/b1-calendar-960/score.json` and its declaration, and
    computes nothing.

    Recorded mutation: in `scripts/research_view.py`, `best_html`, restore the old branch (render the development leader
    as `NOT_MEASURED` whatever `standings` holds) and run
    `PYTHONPATH=src:tests python3 -m unittest test_research_view.Standings`: `test_a_named_candidate_is_not_reported_as_not_measured`
    failed with AssertionError.
    """

    STEP4 = "docs/pivot/evidence/h5-step4/score.json"
    SCORE = "docs/pivot/evidence/b1-calendar-960/score.json"
    DECLARATION = "metadata/b1_calendar_960.json"

    def record(self, rel=None):
        return json.loads((ROOT / (rel or self.SCORE)).read_text(encoding="utf-8"))

    def best(self):
        """The standings as the page renders them when no candidate record exists (#1152 keeps this fallback)."""
        with tempfile.TemporaryDirectory() as tmp:
            for rel in (self.STEP4, self.SCORE, self.DECLARATION):
                (Path(tmp) / rel).parent.mkdir(parents=True, exist_ok=True)
                (Path(tmp) / rel).write_bytes((ROOT / rel).read_bytes())
            return research_view.standings_html(research_view.standings(tmp))

    def leader(self):
        block = self.best()
        start = block.find("The development standings")
        self.assertGreaterEqual(start, 0, "the page has no development standings paragraph")
        return block[start:block.find("</table>", start) + 8]

    def test_a_named_candidate_is_not_reported_as_not_measured(self):
        name = self.record(self.STEP4)["best_candidate"]
        self.assertTrue(name, "the step 4 record names no candidate")
        block = self.best()
        self.assertNotIn("The development leader.</span> <span class=\"rs-nm\">", block)
        self.assertIn(name, self.leader())
        self.assertNotIn(research_view.NOT_MEASURED + "</span>: no committed record", block)

    def test_it_sets_the_candidate_against_all_three_and_names_no_single_leader(self):
        leader = self.leader()
        for model in ("B1", "B1&prime;", "spread_mr_ctx", "gbm_funding"):
            self.assertIn(model, leader)
        self.assertNotRegex(leader, r"(?i)\bleads\b|\bbest against\b|\bbeats B1\b")
        # the reading rules are the record's own words, so the page does not call the gbm a winner
        for rule in self.record()["reading_rules"]:
            self.assertIn(research_view.esc(rule), self.best())

    def test_it_is_labelled_and_marked_provisional_with_its_interval_type(self):
        leader = self.leader()
        self.assertIn(research_view.DEV_LABEL, leader)
        self.assertIn(research_view.PROVISIONAL_LABEL, leader)
        interval = self.record(self.DECLARATION)["scoring"]["interval"]
        self.assertIn(research_view.esc(interval), self.best())

    def test_every_number_is_in_the_record(self):
        record = self.record()
        allowed = set()

        def collect(x):
            if isinstance(x, dict):
                for v in x.values():
                    collect(v)
            elif isinstance(x, list):
                for v in x:
                    collect(v)
            elif isinstance(x, float):
                allowed.update({f"{x:.2f}", f"{x:+.2f}", f"{100 * x:.1f}", f"{100 * x:+.1f}"})
            elif isinstance(x, int) and not isinstance(x, bool):
                allowed.add(str(x))

        for key, label in (("pooled", "all decision days"), ("target_type", "ordinary")):
            group = record["groups"][key][label]
            grid = group["metrics"]["grid_crps"]
            collect(group["days"])
            collect(grid["means"])
            for pair in grid["pairs"].values():
                collect([pair["skill"], pair["skill_interval"]])
        interval = research_view.esc(self.record(self.DECLARATION)["scoring"]["interval"])
        text = re.sub(r"<code>.*?</code>", " ", self.leader().replace(interval, " "))
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"B1(?:&prime;)?|spread_mr_ctx|gbm_funding|[Ss]tep 4|\d{4}-\d{2}-\d{2}", " ", text)
        found = re.findall(r"[+-]?\d+(?:\.\d+)?", text.replace("\u2212", "-").replace("&minus;", "-"))
        self.assertTrue(found)
        for number in found:
            self.assertIn(number, allowed, f"{number} is on the page and in no committed record")

    def test_it_reads_the_records_not_a_constant(self):
        with tempfile.TemporaryDirectory() as tmp:
            for rel in (self.STEP4, self.SCORE, self.DECLARATION):
                (Path(tmp) / rel).parent.mkdir(parents=True, exist_ok=True)
                (Path(tmp) / rel).write_bytes((ROOT / rel).read_bytes())
            score = Path(tmp) / self.SCORE
            doc = json.loads(score.read_text(encoding="utf-8"))
            doc["groups"]["pooled"]["all decision days"]["metrics"]["grid_crps"]["means"]["B1"] = 9.87
            score.write_text(json.dumps(doc), encoding="utf-8")
            self.assertIn("9.87", research_view.standings_html(research_view.standings(tmp)))

    def test_no_record_naming_a_candidate_reads_not_measured(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(research_view.standings(tmp))
            self.assertIn(research_view.NOT_MEASURED, research_view.standings_html(None))


class CandidateStandings(unittest.TestCase):
    """#1152, #1173: the page names the H5 candidate from `docs/research/h5-candidate.json`, not from the step 4 record.

    Eleonora ruled (22 October 2026, #1115) that #941's scaled mean reversion, `spread_mr_fhs_mad20_f0.5`, replaces
    `gbm_funding`, and (23 October 2026, #1151, option 2) that (s3) of #1145, `sc_s3_robust`, replaces that. The
    standings read the candidate from that small committed record, score it from #1145's `result.json` (beside B1,
    B1', B2, the replaced (a) and spread_mr_ctx), show the mean-d interval and read it as the protocol does (#1009),
    carry Lens C's caveat, and fall back to the step 4 record only when the file is absent.

    Recorded mutation: in `scripts/research_view.py`, `standings`, replace `if (root / CANDIDATE).exists():` with
    `if False:` (the step 4 record names the candidate whatever the file holds) and run
    `PYTHONPATH=src:tests python3 -m unittest test_research_view.CandidateStandings`:
    `test_the_page_names_the_record_candidate_not_the_step4_one` failed with AssertionError.
    """

    CANDIDATE = "docs/research/h5-candidate.json"
    STEP4 = "docs/pivot/evidence/h5-step4/score.json"

    def record(self):
        return json.loads((ROOT / self.CANDIDATE).read_text(encoding="utf-8"))

    def scores(self):
        return json.loads((ROOT / self.record()["scores"]["record"]).read_text(encoding="utf-8"))

    def best(self):
        return PAGE[at('id="best-performer"'):at('id="hypotheses"')]

    def block(self):
        text = self.best()
        start = text.find("The development standings")
        self.assertGreaterEqual(start, 0)
        end = text.find('<aside class="rs-q">', start)
        return text[start:end]

    def copy_tree(self, tmp, skip=()):
        for rel in (self.CANDIDATE, self.STEP4, "docs/pivot/evidence/b1-calendar-960/score.json",
                    "metadata/b1_calendar_960.json", self.record()["scores"]["record"], research_view.SUMMARY):
            if rel in skip:
                continue
            (Path(tmp) / rel).parent.mkdir(parents=True, exist_ok=True)
            (Path(tmp) / rel).write_bytes((ROOT / rel).read_bytes())

    def test_the_page_says_post_2020_intervals_are_about_twice_too_narrow_under_the_standings(self):
        """#1458 (her ruling of 4 November 2026 on #1112): one plain sentence under the standings, with a link.

        Recorded mutation: in `scripts/research_view.py`, `candidate_standings_html`, delete the
        `INTERVAL_CAVEAT` paragraph from the returned string; this test fails with AssertionError (the sentence is
        not on the page).
        """
        block = self.block()
        self.assertIn(research_view.esc(research_view.INTERVAL_CAVEAT_TEXT), block)
        self.assertGreater(block.find(research_view.esc(research_view.INTERVAL_CAVEAT_TEXT)), block.rfind("</table>"),
                           "the sentence is not under the standings")
        self.assertIn(research_view.BLOB + research_view.INTERVAL_CAVEAT_PAGE, block)
        self.assertTrue((ROOT / research_view.INTERVAL_CAVEAT_PAGE).is_file())

    def test_the_record_names_the_ruled_candidate_and_its_evidence(self):
        rec = self.record()
        self.assertEqual(rec["scores"]["model"], "sc_s3_robust")
        self.assertEqual(rec["candidate"], "sc_s3c_ann_net")  # #1310: (s3c-ann-net), (s3c) with announced settlement terms sized by the net; the record still scores (s3), its base's base
        self.assertEqual(rec["base"], "sc_s3c")
        self.assertEqual(rec["cap"]["margin_bp"], 0)
        self.assertEqual(rec["replaces"], "sc_s3c, (s3c): (s3) of the state-scaled calendar study capped at the SRF line")
        self.assertEqual(rec["date"], "2026-10-29")
        self.assertTrue(rec["earlier_ruling"]["url"].startswith("https://github.com/eleonorabjornberg/repo-market-model/issues/1151#issuecomment-"))
        self.assertEqual(rec["scores"]["record"], "docs/research/state-calendar-1145/result.json")
        self.assertEqual(rec["ruling"], "https://github.com/eleonorabjornberg/repo-market-model/issues/1310")
        self.assertEqual({e["issue"] for e in rec["evidence"]}, {1145, 1115, 1141, 1255, 1288})
        for e in rec["evidence"]:
            self.assertTrue((ROOT / e["page"]).is_file(), e["page"])
            self.assertTrue((ROOT / e["record"]).is_file(), e["record"])
        self.assertIn(rec["scores"]["model"], self.scores()["models"])

    def test_the_page_names_the_record_candidate_not_the_step4_one(self):
        step4 = json.loads((ROOT / self.STEP4).read_text(encoding="utf-8"))["best_candidate"]
        self.assertEqual(step4, "gbm_funding")
        block = self.block()
        plain = json.loads((ROOT / research_view.SUMMARY).read_text(encoding="utf-8"))["candidate"]
        self.assertIn(html.escape(plain["description"]), block)  # #1355: described in words, never by its code name
        self.assertNotIn(self.record()["candidate"], block)
        self.assertNotIn("names <b>gbm_funding</b> as its best candidate", block)
        for e in self.record()["evidence"]:
            self.assertIn(e["page"], block)
            if e.get("mean_d_page"):  # #1194: each evidence page is linked beside its reading on the mean-d bound (#1255's page is its own)
                self.assertIn(e["mean_d_page"], block)
        self.assertNotRegex(block, r"(?<![&\w])#\d+")
        self.assertIn("2026-10-29", block)
        self.assertIn(html.escape(plain["base"]), block)  # #1259, #1310: the tables are the base's, and the page says so

    def test_it_is_scored_beside_all_five_and_labelled(self):
        block = self.block()
        models = json.loads((ROOT / research_view.SUMMARY).read_text(encoding="utf-8"))["models"]
        for key in ("B1", "B1_prime", "B2", "mr_cal_a_base", "spread_mr_ctx"):
            self.assertIn(f'<th scope="row">{html.escape(models[key]["name"])}</th>', block)
        self.assertNotIn(f'<th scope="row">{models["gbm_funding"]["name"]}</th>', block)
        self.assertIn(research_view.DEV_LABEL, block)
        self.assertNotIn(research_view.PROVISIONAL_LABEL, block)  # it reads the calendar at the target day
        self.assertNotRegex(block, r"(?i)\bleads\b|\bbeats B1\b|\bregistered candidate\b")

    def test_it_shows_the_mean_d_interval_and_reads_its_bound(self):
        grid = self.scores()["groups"]["pooled"]["all decision days"]["grid_crps"]
        pair = grid["vs"]["sc_s3_robust"]["B1_prime"]
        lo, hi = pair["difference_interval"]
        self.assertGreater(lo, 0)
        block = self.block()
        self.assertIn(f"{pair['difference']:+.2f}", block)
        self.assertIn(f"{lo:+.2f}", block)
        self.assertIn(f"{hi:+.2f}", block)
        self.assertIn("better", block)
        self.assertIn("ruling on which interval is read", block)

    def test_it_shows_the_skill_over_the_replaced_candidate_with_its_interval(self):
        pair = self.scores()["groups"]["pooled"]["all decision days"]["grid_crps"]["vs"]["sc_s3_robust"]["mr_cal_a_base"]
        lo, hi = pair["skill_interval"]
        self.assertEqual((f"{100 * pair['skill']:+.1f}%", f"{100 * lo:+.1f}%", f"{100 * hi:+.1f}%"),
                         ("+4.3%", "+1.8%", "+6.4%"))
        self.assertIn("+4.3% [+1.8%, +6.4%]", self.block())

    def test_the_provisional_mark_follows_the_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.copy_tree(tmp)
            path = Path(tmp) / self.CANDIDATE
            doc = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(doc["provisional"])
            doc["provisional"] = True
            path.write_text(json.dumps(doc), encoding="utf-8")
            self.assertIn(research_view.PROVISIONAL_LABEL, research_view.standings_html(research_view.standings(tmp)))

    def test_a_reading_follows_the_bound_on_mean_d(self):
        read = research_view.read_mean_d
        self.assertEqual(read([0.1, 0.5]), "better")
        self.assertEqual(read([-0.5, -0.1]), "worse")
        self.assertEqual(read([-0.1, 0.5]), "no difference")
        self.assertEqual(read(None), research_view.NOT_MEASURED)

    def test_it_carries_lens_cs_caveat(self):
        block = self.block()
        self.assertIn("A caution on the baselines", block)  # #1355: was "Lens C's caveat"
        self.assertIn("Plain persistence stays the scoring rules", block)
        self.assertRegex(block, r"(?i)by regime")
        self.assertRegex(block, r"(?i)by (target-day|day) type")
        days = json.loads((ROOT / research_view.SUMMARY).read_text(encoding="utf-8"))["day_types"]
        for regime in self.scores()["groups"]["regime"]:
            self.assertIn(f"<th scope=\"row\">{regime}</th>", block)
        for kind in self.scores()["groups"]["target_day_type"]:
            self.assertIn(f"<th scope=\"row\">{html.escape(days[kind])}</th>", block)

    def test_every_number_is_in_the_record(self):
        scores = self.scores()
        allowed = set()

        def add(x):
            if isinstance(x, (list, tuple)):
                for v in x:
                    add(v)
            elif isinstance(x, float):
                allowed.update({f"{x:.2f}", f"{x:+.2f}", f"{100 * x:.1f}", f"{100 * x:+.1f}"})
            elif isinstance(x, int) and not isinstance(x, bool):
                allowed.add(str(x))

        def walk(group):
            add(group["days"])
            grid = group["grid_crps"]
            add(list(grid["means"].values()))
            for per in grid["vs"].values():
                for pair in per.values():
                    add([pair["difference"], pair["difference_interval"], pair["skill"], pair["skill_interval"]])

        walk(scores["groups"]["pooled"]["all decision days"])
        for kind in ("regime", "target_day_type"):
            for group in scores["groups"][kind].values():
                walk(group)
        text = re.sub(r"<code>.*?</code>|<a [^>]*>|<th scope=\"row\">.*?</th>", " ", self.block())
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"#\d+|\d{4}-\d{2}(?:-\d{2})?|B1(?:&prime;)?|B2|mad20|f0\.5|v1|[Pp]ost-2020|(?<![\d.])\d+%", " ", text)
        text = text.replace("\u2212", "-").replace("&minus;", "-")
        found = re.findall(r"(?<![\w.])[+-]?\d+(?:\.\d+)?", text)
        self.assertTrue(found)
        for number in found:
            self.assertIn(number, allowed, f"{number} is on the page and in no committed record")

    def test_it_reads_the_records_not_a_constant(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.copy_tree(tmp)
            score = Path(tmp) / self.record()["scores"]["record"]
            doc = json.loads(score.read_text(encoding="utf-8"))
            doc["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]["B1"] = 9.87
            score.write_text(json.dumps(doc), encoding="utf-8")
            st = research_view.standings(tmp)
            self.assertEqual(st["candidate"], self.record()["candidate"])
            self.assertIn("9.87", research_view.standings_html(st))

    def test_it_falls_back_to_the_step4_record_when_the_file_is_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.copy_tree(tmp, skip=(self.CANDIDATE,))
            st = research_view.standings(tmp)
            self.assertEqual(st["candidate"], "gbm_funding")

    def test_a_record_naming_an_unscored_model_is_refused_not_guessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.copy_tree(tmp)
            path = Path(tmp) / self.CANDIDATE
            doc = json.loads(path.read_text(encoding="utf-8"))
            doc["scores"]["model"] = "no_such_model"
            path.write_text(json.dumps(doc), encoding="utf-8")
            self.assertIsNone(research_view.standings(tmp))

    def test_the_page_says_development_not_a_verdict_and_nothing_is_registered(self):
        block = self.block()
        self.assertIn("Nothing is registered", block)
        self.assertIn(research_view.esc(research_view.DEV_LABEL), block)

    def test_the_candidate_file_is_a_page_input(self):
        self.assertIn(self.CANDIDATE, research_view.INPUTS)
        self.assertIn("docs/research/state-calendar-1145/result.json", research_view.INPUTS)


class Sources(unittest.TestCase):
    def copy_tree(self, tmp):
        out = Path(tmp)
        for rel in ("docs/research", ):
            for path in (ROOT / rel).rglob("*"):
                if path.is_file():
                    (out / path.relative_to(ROOT)).parent.mkdir(parents=True, exist_ok=True)
                    (out / path.relative_to(ROOT)).write_bytes(path.read_bytes())
        cited = {item["evidence"] for item in json.loads(
            (ROOT / "docs/research/milestones.json").read_text(encoding="utf-8"))["milestones"].values()}
        for rel in sorted(cited | {"tests/test_scoring_protocol_coverage.py"}):
            (out / rel).parent.mkdir(parents=True, exist_ok=True)
            (out / rel).write_bytes((ROOT / rel).read_bytes())
        return out

    def test_the_real_tree_loads(self):
        hypotheses = research_view.load(ROOT)
        self.assertEqual([h["id"] for h in hypotheses], PLAN_IDS)

    def test_a_manual_without_a_question_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            manual = out / "docs/research/hypotheses/H3.md"
            manual.write_text(re.sub(r"(?m)^\*\*Question\.\*\*.*$", "", manual.read_text(encoding="utf-8")),
                              encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "H3.md has no"):
                research_view.load(out)

    def test_a_manual_without_milestones_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            manual = out / "docs/research/hypotheses/H4.md"
            manual.write_text(re.sub(r"(?m)^- M\d+\..*$", "", manual.read_text(encoding="utf-8")),
                              encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "no milestone list"):
                research_view.load(out)

    def test_a_done_milestone_needs_tracked_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            path = out / "docs/research/milestones.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["milestones"]["H1.M1"]["evidence"] = "tests/no_such_file.py"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "not tracked"):
                research_view.load(out)

    def test_a_milestone_the_manual_lacks_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            path = out / "docs/research/milestones.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["milestones"]["H1.M9"] = {"evidence": "docs/research/plan.md"}
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "not milestones"):
                research_view.load(out)

    def test_a_hypothesis_without_a_tagline_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            path = out / research_view.TAGLINES
            data = json.loads(path.read_text(encoding="utf-8"))
            del data["taglines"]["H6"]
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "H6 has no tagline"):
                research_view.load(out)

    def test_a_tagline_for_no_hypothesis_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            path = out / research_view.TAGLINES
            data = json.loads(path.read_text(encoding="utf-8"))
            data["taglines"]["H11"] = "Something new."
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "H11"):
                research_view.load(out)

    def test_the_phase_is_the_plans_six_step_scale_and_comes_from_milestones_json(self):
        """A log entry's step is the manual's own step (H5 has six); the phase shown is one of the plan's six."""
        steps = json.loads((ROOT / "docs/research/milestones.json").read_text(encoding="utf-8"))["steps"]
        for h in research_view.load(ROOT):
            self.assertIn(h["id"], steps, h["id"])
            self.assertEqual(h["step"], steps[h["id"]])
            self.assertIn(h["step"], range(1, len(research_view.STEPS) + 1))
            logged = [e["step"] for e in h["log"] if e["step"] is not None]
            self.assertEqual(h["manual_step"], max(logged) if logged else None)

    def test_a_log_entry_with_a_high_manual_step_does_not_move_the_phase(self):
        """Mutation: `step = max([floor] + log steps)` in `load` (the old rule): this failed, AssertionError (H1 read 6)."""
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            # The log is its entry files (#928): the high-step entry is one more file.
            (out / "docs/research/log/2026-10-17-model-00009-H1-step6.md").write_text(
                "### 2026-10-17 [H1] step 6 · o/r#9\n- Directive: #9\n", encoding="utf-8")
            before = {h["id"]: h["step"] for h in research_view.load(ROOT)}
            after = {h["id"]: h["step"] for h in research_view.load(out)}
            self.assertEqual(before, after)

    def test_a_hypothesis_without_a_phase_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            path = out / "docs/research/milestones.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            del data["steps"]["H5"]
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "H5"):
                research_view.load(out)

    def test_a_lettered_milestone_such_as_h5_m5a_is_read(self):
        h5 = next(h for h in research_view.load(ROOT) if h["id"] == "H5")
        self.assertIn("M5a", [mid for mid, _ in h5["manual"]["milestones"]])

    def test_every_done_milestone_cites_a_pull_request(self):
        done = json.loads((ROOT / "docs/research/milestones.json").read_text(encoding="utf-8"))["milestones"]
        for key, item in done.items():
            self.assertRegex(item.get("pr", ""), r"^eleonorabjornberg/repo-market-(model|liquidity)#\d+$", key)

    def test_a_groundwork_entry_is_listed_and_moves_no_step(self):
        text = ("### 2026-10-13 [H5] groundwork G3 · o/r#1\n- Directive: #1\n\n"
                "### 2026-10-14 [H5] step 2 · o/r#2\n- Directive: #2\n")
        entries = research_view.parse_log_entries(text)["H5"]
        self.assertEqual([(e["step"], e["groundwork"]) for e in entries], [(None, "G3"), (2, None)])


class CriticalPath(unittest.TestCase):
    """The plan's "Critical path" section (#704): parsed, checked against the manuals, shown on the page."""

    copy_tree = Sources.copy_tree

    def chain(self, root=ROOT):
        return research_view.load_critical_path(root, research_view.load(root))

    def test_the_real_plan_has_a_chain_for_each_goal(self):
        links = self.chain()
        for goal in ("H5", "H9"):
            self.assertTrue([l for l in links if goal in l["gates"]], goal)
        self.assertEqual([l["id"] for l in links], [f"CP{i}" for i in range(1, len(links) + 1)])

    def test_every_link_names_a_milestone_of_a_manual(self):
        manuals = {h["id"]: {m for m, _ in h["manual"]["milestones"]} for h in research_view.load(ROOT)}
        for link in self.chain():
            hid, mid = link["milestone"].split(".")
            self.assertIn(mid, manuals[hid], link["id"])

    def test_a_milestone_no_manual_has_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            plan = out / "docs/research/plan.md"
            plan.write_text(plan.read_text(encoding="utf-8").replace("- CP1. H1.M3 ", "- CP1. H1.M9 "), encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "H1.M9"):
                self.chain(out)

    def test_a_plan_without_the_section_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            plan = out / "docs/research/plan.md"
            plan.write_text(plan.read_text(encoding="utf-8").replace("## Critical path", "## Something else"),
                            encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "Critical path"):
                self.chain(out)

    def test_a_link_cannot_wait_on_a_later_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.copy_tree(tmp)
            plan = out / "docs/research/plan.md"
            plan.write_text(re.sub(r"(- CP1\. [^\n]*Waits on: )", r"\1CP2; ", plan.read_text(encoding="utf-8"), count=1),
                            encoding="utf-8")
            with self.assertRaisesRegex(research_view.ResearchError, "CP1 waits on CP2"):
                self.chain(out)

    def test_the_page_shows_the_first_open_link_of_each_goal(self):
        hypotheses = research_view.load(ROOT)
        links = research_view.load_critical_path(ROOT, hypotheses)
        done = {h["id"] + "." + m for h in hypotheses for m in h["done"]}
        nexts = json.loads((ROOT / research_view.SUMMARY).read_text(encoding="utf-8"))["next"]
        block = PAGE[at("What comes next"):]
        block = block[:block.find("</div>")]
        for goal in ("H5", "H9"):
            first = next(l for l in links if goal in l["gates"] and l["milestone"] not in done)
            self.assertIn(html.escape(nexts[first["milestone"]].rstrip(".")), block, goal)
        self.assertNotIn("stand-in", block)
        self.assertNotIn("first milestone not yet marked done", block)

    def test_done_comes_only_from_milestones_json(self):
        done = json.loads((ROOT / "docs/research/milestones.json").read_text(encoding="utf-8"))["milestones"]
        for link in self.chain():
            self.assertEqual(link["done"], link["milestone"] in done, link["id"])


class DeclaredInputs(unittest.TestCase):
    """#1059: the page's inputs are declared once, in `research_view.INPUTS`; `emit_visual.py` digests that list."""

    def test_load_reads_only_declared_inputs(self):
        read = []
        original = research_view.read
        research_view.read = lambda repo, rel: (read.append(rel), original(repo, rel))[1]
        try:
            research_view.load(ROOT)
        finally:
            research_view.read = original
        self.assertTrue(read)
        directories = tuple(p + "/" for p in research_view.INPUTS)
        for rel in read:
            self.assertTrue(rel in research_view.INPUTS or rel.startswith(directories), f"{rel} is read but not in INPUTS")

    def test_every_declared_input_is_digested_by_the_page(self):
        spec = importlib.util.spec_from_file_location("emit_visual", ROOT / "scripts" / "emit_visual.py")
        emit_visual = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(emit_visual)
        digested = set(emit_visual.research_inputs(ROOT))
        for rel in research_view.INPUTS:
            self.assertTrue(rel in digested or any(d.startswith(rel + "/") or d == rel + ".md" for d in digested), rel)
        self.assertEqual(set(research_view.input_files(ROOT)) | {"docs/research/log.md"}, digested)


if __name__ == "__main__":
    unittest.main()
