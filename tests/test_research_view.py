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

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

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
            for label in ("Question", "Kill criterion", "Owner", "Milestones", "Progress markers",
                          "Development variants"):
                self.assertIn(f"<dt>{label}</dt>", block, f"{hid} lacks {label}")
            self.assertRegex(block, r'<li class="(done|open)"><b>M1</b>')

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
            self.assertEqual(text, f"{hid} {research_view.inline(taglines[hid])}", hid)
            self.assertNotRegex(line, r"<(?:br|p|div|ul|ol|dl|table)\b", hid)
            for label in ("Step", "Kill criterion", "Milestones", "Test"):
                if label == "Test" and "<dt>Test</dt>" not in fold:
                    continue
                self.assertIn(f"<dt>{label}</dt>", fold, hid)

    def test_owner_repository_of_h7_and_h10(self):
        for hid in ("H7", "H10"):
            block = PAGE[at(f'id="{hid.lower()}"'):]
            self.assertIn("repo-market-liquidity", block[:block.find("</article>")])


class Labels(unittest.TestCase):
    def test_development_entries_and_incumbent_carry_the_label(self):
        label = research_view.DEV_LABEL
        best = PAGE[at('id="best-performer"'):at('id="hypotheses"')]
        self.assertIn(label, best)
        for item in re.findall(r'<li><b>\d{4}-\d{2}-\d{2}</b>.*?</li>', PAGE, re.S):
            if "tier development" in item:
                self.assertIn(label, item)

    def test_the_executive_summary_is_prose_without_a_table(self):
        """#893: the summary names the goals and every hypothesis in running text, and holds no table."""
        summary = PAGE[at('id="research-summary"'):at('<nav aria-label="Contents"')]
        self.assertNotIn("<table", summary)
        self.assertNotRegex(summary, r"<(?:ul|ol|dl)\b")
        for hid in PLAN_IDS:
            self.assertRegex(summary, rf'href="#{hid.lower()}">{hid}</a>', hid)
        self.assertIn("development data never gives one", summary)
        self.assertIn("Primary goal", summary)
        self.assertIn("Secondary goal", summary)

    def test_every_key_figure_carries_the_label(self):
        """#893: a pulled-out key number keeps the development marking."""
        callouts = re.findall(r'<aside class="callout"[^>]*>(.*?)</aside>', PAGE, re.S)
        self.assertTrue(callouts)
        for callout in callouts:
            self.assertIn(research_view.DEV_LABEL, callout)

    def test_unmeasured_figures_say_so(self):
        self.assertIn("not measured", PAGE[at('id="h5"'):at('id="h6"')])
        self.assertIn("Verdicts reached", PAGE)
        self.assertIn("none yet", PAGE[at('id="research-summary"'):at('id="best-performer"')])

    def test_question_for_eleonora_is_marked(self):
        self.assertIn("Question for Eleonora", PAGE[at('id="best-performer"'):at('id="hypotheses"')])


class Sources(unittest.TestCase):
    def copy_tree(self, tmp):
        out = Path(tmp)
        for rel in ("docs/research", ):
            for path in (ROOT / rel).rglob("*"):
                if path.is_file():
                    (out / path.relative_to(ROOT)).parent.mkdir(parents=True, exist_ok=True)
                    (out / path.relative_to(ROOT)).write_bytes(path.read_bytes())
        for rel in ("tests/test_scoring_protocol_synthetic.py", "src/repo_model/scoring_protocol.py",
                    "tests/test_scoring_protocol_coverage.py"):
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

    def test_the_step_is_never_below_the_log(self):
        for h in research_view.load(ROOT):
            self.assertGreaterEqual(h["step"], max([1] + [e["step"] for e in h["log"] if e["step"] is not None]))

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
        block = PAGE[at("Next on the critical path"):]
        block = block[:block.find("</div>")]
        for goal in ("H5", "H9"):
            first = next(l for l in links if goal in l["gates"] and l["milestone"] not in done)
            self.assertIn(first["milestone"], block, goal)
        self.assertNotIn("stand-in", block)
        self.assertNotIn("first milestone not yet marked done", block)

    def test_done_comes_only_from_milestones_json(self):
        done = json.loads((ROOT / "docs/research/milestones.json").read_text(encoding="utf-8"))["milestones"]
        for link in self.chain():
            self.assertEqual(link["done"], link["milestone"] in done, link["id"])


if __name__ == "__main__":
    unittest.main()
