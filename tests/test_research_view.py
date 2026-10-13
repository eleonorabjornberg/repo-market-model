"""The research sections of the results page (#645): `scripts/research_view.py`, `site/index.html`.

The page reads, top to bottom: executive summary, current best performer, H1 to H10, then the background and
detailed records. Every figure is parsed from tracked sources (`docs/research/`), and a figure nobody has measured
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
        for marker in ('id="start"', 'aria-label="Chapters"', 'id="n1"', 'id="final-test"', 'id="history"',
                       'id="built"'):
            self.assertGreater(at(marker), background, marker)

    def test_each_hypothesis_has_question_milestones_and_owner(self):
        for hid in PLAN_IDS:
            block = PAGE[at(f'id="{hid.lower()}"'):]
            block = block[:block.find("</article>")]
            for label in ("Question", "Kill criterion", "Owner", "Milestones", "Progress markers",
                          "Development variants"):
                self.assertIn(f"<dt>{label}</dt>", block, f"{hid} lacks {label}")
            self.assertRegex(block, r'<li class="(done|open)"><b>M1</b>')

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

    def test_the_step_is_never_below_the_log(self):
        for h in research_view.load(ROOT):
            self.assertGreaterEqual(h["step"], max([1] + [e["step"] for e in h["log"]]))


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
