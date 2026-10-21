"""The provisional register (#1028): `metadata/provisional/`, `docs/research/provisional-calendar-register.md`,
`scripts/provisional_register.py`.

A model that does not read calendar days at the target day is wrong (Eleonora, 20 October 2026), so every result produced by
one is provisional until it is re-run (#1027). The register names those results, and the results page marks their figures.

Each row of the register is its own file under `metadata/provisional/` (`producers/<script stem>.json`,
`results/pr_<pull request>.json`, `cleared/<declaration stem>.json`), so a directive that adds a producer adds a file and does
not edit a shared page; the page's three tables are generated from the files (`python3 scripts/provisional_register.py`;
`--check` refuses a stale page). These tests keep the register complete against the tree:

* every `metadata/*.json` declaration that names a calendar or scheduled column is cited by an entry file, as a producer, a
  registered result or a declaration that is read at the target day (or is no model);
* every script that calls a gradient-boosted quantile fitter, whose default pairs are one-step, has its own producer file;
* a declaration cleared as "read at the target day" is never one-step and never calls those fitters;
* the register lists each result once, in the plan's order (H5, then H9, then the rest), and its marks reach the page;
* the page's tables are the ones the files generate.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `TestEveryDeclarationIsClassified.test_every_declaration_naming_a_calendar_column_is_cited`: delete
  `metadata/provisional/results/pr_852.json`; the test failed with AssertionError (the list of uncited declarations was
  `['metadata/exploration_845.json']`).
* `TestEveryDeclarationIsClassified.test_every_one_step_fitter_caller_has_a_producer_file`: delete
  `metadata/provisional/producers/h9_nested_842.json`; the test failed with AssertionError (`['scripts/h9_nested_842.py']` is a
  caller with no producer file).
* `TestThePageIsGenerated.test_the_page_is_current`: on the page change the class of the `scripts/h9_nested_842.py` row to
  `b`; the test failed with AssertionError (the producers table is stale).
* `TestThePageMark.test_a_registered_log_entry_carries_the_mark`: in `scripts/research_view.py` change
  `if e.get("provisional") else ""` in `log_html` to `if False else ""`; the test failed with AssertionError (the mark is not in
  the entry's HTML).
"""

import importlib.util
import json
import re
import shutil
import tempfile
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
ENTRIES = register.entries(ROOT)
TABLES = register.load(ROOT)
DECLARATION = re.compile(r"metadata/[A-Za-z0-9_]+\.json")


def cited(entries):
    """The `metadata/*.json` declarations the given entry files name."""
    return set(DECLARATION.findall(json.dumps([{k: v for k, v in e.items() if k != "_file"} for e in entries])))


ALL_ENTRIES = [entry for kind in ENTRIES.values() for entry in kind]


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
        """H5 first, then H9, then the rest. Each result file carries its own order key; the table numbers the rows 1, 2, ...
        in the order of the keys, so a new result takes a free key and renumbers no other file."""
        rank = {"H5": 0, "H9": 1}
        keys = [entry["order"] for entry in ENTRIES["results"]]
        self.assertEqual(len(set(keys)), len(keys), "two result files share an order key")
        rows = TABLES["results"]
        self.assertEqual([int(row["order"]) for row in rows], list(range(1, len(rows) + 1)))
        ranks = [rank.get(row["hypothesis"], 2) for row in rows]
        self.assertEqual(ranks, sorted(ranks), "H5 before H9 before every other hypothesis")

    def test_a_producer_row_is_complete(self):
        for row in TABLES["producers"]:
            with self.subTest(script=row["script"]):
                self.assertTrue((ROOT / row["script"]).is_file())
                self.assertIn(row["class"], register.CLASSES)
                self.assertIn(row["pairing"], register.PRODUCER_PAIRINGS)


class TestEachRowIsItsOwnFile(unittest.TestCase):
    def test_each_file_is_named_after_its_key(self):
        for kind, rows in ENTRIES.items():
            for entry in rows:
                with self.subTest(kind=kind, file=entry["_file"]):
                    self.assertEqual(entry["_file"], register.entry_path(kind, entry))

    def _copy(self, tmp):
        repo = Path(tmp)
        shutil.copytree(ROOT / register.ENTRIES, repo / register.ENTRIES)
        (repo / register.REGISTER).parent.mkdir(parents=True)
        shutil.copy(ROOT / register.REGISTER, repo / register.REGISTER)
        return repo

    def test_a_file_with_a_missing_or_unknown_field_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy(tmp)
            path = repo / register.ENTRIES / "producers" / "h9_nested_842.json"
            entry = json.loads(path.read_text(encoding="utf-8"))
            entry["colour"] = "red"
            path.write_text(json.dumps(entry), encoding="utf-8")
            with self.assertRaises(register.RegisterError):
                register.entries(repo)
            del entry["colour"], entry["class"]
            path.write_text(json.dumps(entry), encoding="utf-8")
            with self.assertRaises(register.RegisterError):
                register.entries(repo)

    def test_a_file_with_an_unknown_class_or_pairing_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy(tmp)
            path = repo / register.ENTRIES / "producers" / "h9_nested_842.json"
            entry = json.loads(path.read_text(encoding="utf-8"))
            path.write_text(json.dumps(dict(entry, **{"class": "c"})), encoding="utf-8")
            with self.assertRaises(register.RegisterError):
                register.entries(repo)
            path.write_text(json.dumps(dict(entry, pairing="direct")), encoding="utf-8")
            with self.assertRaises(register.RegisterError):
                register.entries(repo)

    def test_a_file_named_after_another_key_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy(tmp)
            folder = repo / register.ENTRIES / "producers"
            (folder / "h9_nested_842.json").rename(folder / "h9_nested.json")
            with self.assertRaises(register.RegisterError):
                register.entries(repo)

    def test_a_new_producer_is_a_new_file_and_reaches_the_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._copy(tmp)
            self.assertEqual(register.stale(repo), [])
            entry = {"script": "scripts/new_model_9999.py", "declarations": ["metadata/new_model_9999.json"],
                     "model": "a new model", "calendar_inputs": "none", "pairing": "one_step", "class": "a"}
            (repo / register.ENTRIES / "producers" / "new_model_9999.json").write_text(json.dumps(entry), encoding="utf-8")
            self.assertEqual(register.stale(repo), ["producers"])
            register.write(repo)
            self.assertEqual(register.stale(repo), [])
            self.assertIn("scripts/new_model_9999.py", {row["script"] for row in register.load(repo)["producers"]})
            self.assertIn("| `scripts/new_model_9999.py` | `metadata/new_model_9999.json` | a new model | none | one_step | a |",
                          (repo / register.REGISTER).read_text(encoding="utf-8"))


class TestThePageIsGenerated(unittest.TestCase):
    def test_the_page_is_current(self):
        self.assertEqual(register.stale(ROOT), [], "run `python3 scripts/provisional_register.py` and commit the page")

    def test_each_table_is_one_generated_block(self):
        for name in register.TABLES:
            with self.subTest(table=name):
                self.assertEqual(TEXT.count(register.begin(name)), 1)
                self.assertEqual(TEXT.count(register.end(name)), 1)

    def test_the_page_tables_parse_back_to_the_files(self):
        self.assertEqual(register.parse_page(TEXT), TABLES)


class TestEveryDeclarationIsClassified(unittest.TestCase):
    def test_every_declaration_naming_a_calendar_column_is_cited(self):
        named = register.declarations_naming_a_calendar_column(ROOT)
        self.assertTrue(named, "no declaration names a calendar column: the scan is broken")
        missing = sorted(set(named) - cited(ALL_ENTRIES))
        self.assertEqual(missing, [], f"declarations that name a calendar or scheduled column and are not in the register: {missing}")

    def test_the_scan_reads_the_shared_target_day_declaration(self):
        """#1070: the FOMC columns are written about the target day, so a declaration naming one is classified."""
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from repo_model import contract
        self.assertLessEqual(set(contract.TARGET_DAY_COLUMNS), set(register.CALENDAR_COLUMNS))
        self.assertIn("fomc_meeting_day", register.CALENDAR_COLUMNS)
        self.assertIn("metadata/sources_measurement.json", register.declarations_naming_a_calendar_column(ROOT))

    def test_every_cited_declaration_exists(self):
        for path in sorted(cited(ALL_ENTRIES) | set(DECLARATION.findall(TEXT))):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), f"{path} is cited and not tracked")

    def test_every_one_step_fitter_caller_has_a_producer_file(self):
        callers = register.one_step_fitter_callers(ROOT)
        self.assertIn("scripts/spread_distribution_634.py", callers)
        listed = {entry["script"] for entry in ENTRIES["producers"]}
        self.assertEqual(sorted(set(callers) - listed), [],
                         f"scripts that call a gradient-boosted quantile fitter and have no file under "
                         f"{register.ENTRIES}/producers/")
        self.assertEqual(sorted(listed - set(callers)), [], "producer files whose script no longer calls such a fitter")
        for script in callers:
            with self.subTest(script=script):
                self.assertTrue((ROOT / register.ENTRIES / "producers" / f"{Path(script).stem}.json").is_file())

    def test_the_frozen_exemptions_of_the_one_step_guard_are_named_in_the_register(self):
        """#947's guard refuses a calendar or scheduled regressor in a one-step fit, except two frozen declarations: both are
        class b, and both are named on the register page."""
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from repo_model import one_step_guard
        for name in one_step_guard.ONE_STEP_ALLOW_LIST:
            with self.subTest(exemption=name):
                self.assertIn(f"`{name}`", TEXT)
        for path in register.GUARDS:
            self.assertTrue((ROOT / path).is_file(), f"{path} is a guard no longer")

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
        elsewhere = cited(ENTRIES["producers"] + ENTRIES["results"])
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
