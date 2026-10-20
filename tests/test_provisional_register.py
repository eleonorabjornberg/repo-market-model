"""The provisional register (#1028): `docs/research/provisional-calendar-register.md`, `scripts/provisional_register.py`.

A model that does not read calendar days at the target day is wrong (Eleonora, 20 October 2026), so every result produced by
one is provisional until it is re-run (#1027). The register names those results, and the results page marks their figures.
These tests keep the register complete against the tree:

* every `metadata/*.json` declaration that names a calendar or scheduled column is cited in the register, as a producer, a
  registered result or a declaration that is read at the target day (or is no model);
* every script that calls a gradient-boosted quantile fitter, whose default pairs are one-step, is a producer row;
* a declaration cleared as "read at the target day" is never one-step and never calls those fitters;
* the register lists each result once, in the plan's order (H5, then H9, then the rest), and its marks reach the page.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `TestEveryDeclarationIsClassified.test_every_declaration_naming_a_calendar_column_is_cited`: in the register replace the
  `metadata/exploration_845.json` cell of result row 7 with `none`; the test failed with AssertionError (the list of uncited
  declarations was `['metadata/exploration_845.json']`).
* `TestEveryDeclarationIsClassified.test_every_one_step_fitter_caller_is_a_producer`: delete the `scripts/h9_nested_842.py`
  producer row; the test failed with AssertionError (`['scripts/h9_nested_842.py']` is a caller and not a producer).
* `TestThePageMark.test_a_registered_log_entry_carries_the_mark`: in `scripts/research_view.py` change
  `if e.get("provisional") else ""` in `log_html` to `if False else ""`; the test failed with AssertionError (the mark is not in
  the entry's HTML).
"""

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("provisional_register", ROOT / "scripts" / "provisional_register.py")
register = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(register)

_spec = importlib.util.spec_from_file_location("research_view", ROOT / "scripts" / "research_view.py")
research_view = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(research_view)

TEXT = (ROOT / register.REGISTER).read_text(encoding="utf-8")
TABLES = register.load(ROOT)


class TestTheRegisterIsWellFormed(unittest.TestCase):
    def test_the_three_tables_are_not_empty(self):
        for name in ("producers", "results", "cleared"):
            with self.subTest(table=name):
                self.assertTrue(TABLES[name], f"the {name} table has no row")

    def test_a_result_row_is_complete(self):
        for row in TABLES["results"]:
            with self.subTest(directive=row["directive"], pr=row["pull request"]):
                self.assertRegex(row["order"], r"^\d+$")
                self.assertRegex(row["directive"], r"^#\d+$")
                self.assertRegex(row["pull request"], r"^#\d+$")
                self.assertRegex(row["hypothesis"], r"^H\d+$")
                self.assertIn(row["class"], register.CLASSES)
                self.assertIn(row["pairing"], register.RESULT_PAIRINGS)
                for field in ("result", "model", "what it concluded"):
                    self.assertTrue(row[field].strip(), f"{field} is empty")

    def test_the_page_cells_name_real_log_entries(self):
        for row in TABLES["results"]:
            for stem in register.page_cells(row):
                if stem == register.INCUMBENT:
                    continue
                with self.subTest(entry=stem):
                    self.assertTrue((ROOT / "docs/research/log" / f"{stem}.md").is_file(), f"{stem} is not a log entry file")

    def test_a_log_entry_is_registered_once(self):
        seen = [stem for row in TABLES["results"] for stem in register.page_cells(row) if stem != register.INCUMBENT]
        self.assertEqual(sorted(seen), sorted(set(seen)))

    def test_the_rerun_order_follows_the_plan(self):
        """H5 first, then H9, then the rest; the order numbers rise down the table."""
        rank = {"H5": 0, "H9": 1}
        rows = TABLES["results"]
        orders = [int(row["order"]) for row in rows]
        self.assertEqual(orders, sorted(orders), "the rows are listed in the order of their re-run")
        self.assertEqual(len(set(orders)), len(orders), "an order number is used once")
        ranks = [rank.get(row["hypothesis"], 2) for row in rows]
        self.assertEqual(ranks, sorted(ranks), "H5 before H9 before every other hypothesis")

    def test_a_producer_row_is_complete(self):
        for row in TABLES["producers"]:
            with self.subTest(script=row["script"]):
                self.assertTrue((ROOT / row["script"]).is_file())
                self.assertIn(row["class"], register.CLASSES)
                self.assertIn(row["pairing"], register.PRODUCER_PAIRINGS)


class TestEveryDeclarationIsClassified(unittest.TestCase):
    def test_every_declaration_naming_a_calendar_column_is_cited(self):
        cited = set(re.findall(r"metadata/[A-Za-z0-9_]+\.json", TEXT))
        named = register.declarations_naming_a_calendar_column(ROOT)
        self.assertTrue(named, "no declaration names a calendar column: the scan is broken")
        missing = sorted(set(named) - cited)
        self.assertEqual(missing, [], f"declarations that name a calendar or scheduled column and are not in the register: {missing}")

    def test_every_cited_declaration_exists(self):
        for path in sorted(set(re.findall(r"metadata/[A-Za-z0-9_]+\.json", TEXT))):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), f"{path} is cited and not tracked")

    def test_every_one_step_fitter_caller_is_a_producer(self):
        callers = register.one_step_fitter_callers(ROOT)
        self.assertIn("scripts/spread_distribution_634.py", callers)
        listed = {row["script"] for row in TABLES["producers"]}
        self.assertEqual(sorted(set(callers) - listed), [],
                         "scripts that call a gradient-boosted quantile fitter and are not a producer row")
        self.assertEqual(sorted(listed - set(callers)), [], "producer rows whose script no longer calls such a fitter")

    def test_a_cleared_declaration_is_read_at_the_target_day_and_calls_no_one_step_fitter(self):
        callers = set(register.one_step_fitter_callers(ROOT))
        for row in TABLES["cleared"]:
            with self.subTest(declaration=row["declaration"]):
                self.assertTrue((ROOT / row["declaration"]).is_file())
                self.assertIn(row["pairing"], register.CLEARED_PAIRINGS)
                self.assertNotEqual(row["pairing"], "one_step")
                script = row["script"].strip("`")
                if script and script != "none":
                    self.assertTrue((ROOT / script).is_file(), f"{script} does not exist")
                    self.assertNotIn(script, callers, f"{script} calls a one-step-capable fitter")
                self.assertTrue(row["why"].strip())

    def test_a_declaration_is_in_one_table_only_as_cleared(self):
        cleared = {row["declaration"] for row in TABLES["cleared"]}
        elsewhere = set(re.findall(r"metadata/[A-Za-z0-9_]+\.json",
                                   "\n".join("|".join(row.values()) for name in ("producers", "results") for row in TABLES[name])))
        self.assertEqual(sorted(cleared & elsewhere), [], "a declaration is either in the class or cleared, not both")


class TestThePageMark(unittest.TestCase):
    ENTRY = {"date": "2026-10-19", "step": 3, "groundwork": None, "ref": "eleonorabjornberg/repo-market-model#984", "line": 1,
             "fields": {"Tier": "development", "Result": "a figure", "Against kill": "none"}, "file": "x.md"}

    def hypothesis(self, **extra):
        return {"id": "H5", "log": [dict(self.ENTRY, **extra)]}

    def test_a_registered_log_entry_carries_the_mark(self):
        html = research_view.log_html(self.hypothesis(provisional=True))
        self.assertIn(research_view.PROVISIONAL_LABEL, html)
        self.assertIn(register.REGISTER, html)

    def test_an_unregistered_log_entry_carries_no_mark(self):
        self.assertNotIn(research_view.PROVISIONAL_LABEL, research_view.log_html(self.hypothesis()))

    def test_the_mark_names_no_issue_number(self):
        """The results page is for a lay reader (`LayReaderPageTests`): the label carries no `#<digits>`."""
        self.assertNotRegex(research_view.PROVISIONAL_LABEL, r"#\d+")

    def test_load_marks_exactly_the_registered_entries(self):
        stems = {stem for row in TABLES["results"] for stem in register.page_cells(row) if stem != register.INCUMBENT}
        marked = set()
        unmarked = set()
        for h in research_view.load(ROOT):
            for e in h["log"]:
                stem = Path(e["file"]).stem
                (marked if e["provisional"] else unmarked).add(stem)
        self.assertEqual(marked, stems)
        self.assertTrue(unmarked, "every entry is marked: the register has swallowed the log")

    def test_the_incumbent_is_marked_when_the_register_registers_it(self):
        self.assertTrue(register.marks_incumbent(TABLES))
        final = {"days": 10, "first": "2018-01-01", "last": "2018-02-01", "published": 1.0, "persistence": 2.0, "mean": 1.0,
                 "level": 90, "lower": 0.5, "upper": 1.5, "record": "docs/runs/x.json"}
        self.assertEqual(research_view.best_html(final, provisional=True).count(research_view.PROVISIONAL_LABEL), 3)
        self.assertNotIn(research_view.PROVISIONAL_LABEL, research_view.best_html(final))


if __name__ == "__main__":
    unittest.main()
