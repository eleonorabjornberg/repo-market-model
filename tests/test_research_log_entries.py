"""One file per research-log entry (#866): `docs/research/log/*.md`, assembled into `docs/research/log.md`.

Every merge to main made every open pull request conflict on `docs/research/log.md`, because each appended to the
same file. An entry is now its own file and `log.md` is generated from them by `scripts/check_research_log.py
assemble`. Written before the code: this module failed first on the missing `assemble`, `split_log`,
`validate_entry_files` and `frozen_errors` (`AttributeError`).

Recorded mutations, each killing the named test:

* `if base_text != head.get(name):` replaced by `if False:` in `frozen_errors` fails
  `test_a_changed_entry_file_is_refused` (`AssertionError: [] is not true`);
* `if name not in head:` replaced by `if False:` in `frozen_errors` fails `test_a_deleted_entry_file_is_refused` and
  `test_a_renamed_entry_file_is_refused` (`KeyError: '2026-10-12-model-00700-H5-step3.md'`);
* `return not mismatch` replaced by `return True` in `heading_matches_name` fails
  `test_a_file_name_that_disagrees_with_its_heading_is_refused` (`AssertionError: [] is not true`);
* `for name in sorted(entries)` replaced by `for name in list(entries)` in `assemble` fails
  `test_entries_are_assembled_in_file_name_order` (`AssertionError: '...' != '...'`).

Corrections (#867, option (a), Eleonora 19 October 2026): `docs/research/log/_corrections.md` corrects the PR number in
an entry's heading without touching the frozen entry file; `assemble` applies it and keeps the original heading in a
`- Correction:` line. Written before the code: the `CorrectionTests` failed first on the missing `parse_corrections`
and `correction_errors` (`AttributeError`). Recorded mutations:

* `if target not in files:` replaced by `if False:` in `correction_errors` fails
  `test_a_correction_for_a_missing_entry_is_refused` (`KeyError: '2026-10-12-model-00999-H5-step3.md'`);
* `if old != heading.group("ref"):` replaced by `if False:` in `correction_errors` fails
  `test_a_correction_whose_old_reference_is_not_the_headings_is_refused` (`AssertionError: [] is not true`);
* `if old_repo != new_repo:` replaced by `if False:` in `correction_errors` fails
  `test_a_correction_that_changes_more_than_the_pull_request_number_is_refused` (`AssertionError: [] is not true`);
* `if target in seen:` replaced by `if False:` in `correction_errors` fails `test_two_corrections_of_one_entry_are_refused`
  (`AssertionError: [] is not true`).
"""
import importlib.util
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("check_research_log", ROOT / "scripts" / "check_research_log.py")
crl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crl)

#: The commit whose `docs/research/log.md` the migration split (the base of the migration commit).
MIGRATED_FROM = "80b5ef0a02e2ecb53231f4bc45059c6eae74ef23"

HEADER = "# Research log\n\nintro\n"


def entry(date="2026-10-12", hyp="H5", step=3, pr=700, repo="model", marker=""):
    ref = "eleonorabjornberg/repo-market-%s#%d" % (repo, pr)
    lines = ["### %s [%s] step %s · %s" % (date, hyp, step, ref)]
    for name, value in (("Directive", "#640"), ("Step", str(step)), ("Tier", "development"), ("Pins", "p"),
                        ("Tried", "t" + marker), ("Result", "r"), ("Against kill", "k"), ("Next", "n")):
        lines.append("- %s: %s" % (name, value))
    return "\n".join(lines) + "\n"


NAME = "2026-10-12-model-00700-H5-step3.md"


class AssembleTests(unittest.TestCase):

    def test_entries_are_assembled_in_file_name_order(self):
        first, second = entry(pr=700), entry(date="2026-10-13", pr=701)
        text = crl.assemble(HEADER, {"2026-10-13-model-00701-H5-step3.md": second, NAME: first})
        self.assertEqual(text, HEADER + "\n" + first + "\n" + second)

    def test_no_entries_leave_the_header(self):
        self.assertEqual(crl.assemble(HEADER, {}), HEADER)

    def test_new_names_sort_by_date_then_pull_request_number(self):
        names = ["2026-10-13-model-00701-H5-step3.md", "2026-10-12-model-00700-H5-step3.md",
                 "2026-10-12-model-00099-H5-step3.md", "0003-2026-10-17-model-00001-H5-step3.md"]
        self.assertEqual(sorted(names), [names[3], names[2], names[1], names[0]])


class SplitTests(unittest.TestCase):

    def test_a_log_splits_into_its_header_and_one_file_per_entry_and_assembles_back(self):
        text = HEADER + "\n" + entry(pr=701, date="2026-10-13") + "\n" + entry(pr=700)
        header, files = crl.split_log(text)
        self.assertEqual(header, HEADER)
        self.assertEqual([n for n, _ in files], ["0001-2026-10-13-model-00701-H5-step3.md",
                                                 "0002-2026-10-12-model-00700-H5-step3.md"])
        self.assertEqual(crl.assemble(header, dict(files)), text)

    def test_a_groundwork_entry_and_a_repeated_heading_get_distinct_names(self):
        groundwork = entry(hyp="H7", pr=44, repo="liquidity").replace("step 3 · ", "groundwork G5 · ")
        text = HEADER + "\n" + groundwork + "\n" + entry() + "\n" + entry(marker="again")
        names = [n for n, _ in crl.split_log(text)[1]]
        self.assertEqual(len(set(names)), 3)
        self.assertIn("0001-2026-10-12-liquidity-00044-H7-G5.md", names)

    def test_the_log_on_main_at_the_migration_assembles_back_byte_identical(self):
        shown = subprocess.run(["git", "show", "%s:docs/research/log.md" % MIGRATED_FROM], cwd=ROOT,
                               capture_output=True, text=True)
        if shown.returncode:
            self.skipTest("the migration's parent commit is not in this clone")
        header, files = crl.split_log(shown.stdout)
        self.assertEqual(crl.assemble(header, dict(files)), shown.stdout)


class EntryFileTests(unittest.TestCase):
    HYP = {"H5", "H7"}

    def test_a_well_formed_file_passes(self):
        self.assertEqual(crl.validate_entry_files({NAME: entry()}, self.HYP), [])

    def test_a_file_name_that_disagrees_with_its_heading_is_refused(self):
        for bad in ("2026-10-13-model-00700-H5-step3.md", "2026-10-12-liquidity-00700-H5-step3.md",
                    "2026-10-12-model-00701-H5-step3.md", "2026-10-12-model-00700-H7-step3.md",
                    "2026-10-12-model-00700-H5-step2.md"):
            with self.subTest(name=bad):
                self.assertTrue(crl.validate_entry_files({bad: entry()}, self.HYP))

    def test_a_file_may_be_named_by_its_directive_issue_instead_of_its_pull_request(self):
        # The directive issue exists before the branch is pushed; the pull request number does not, so naming by it
        # forced a rename commit and a second CI run once the pull request was opened (02fbde05, 7271509a).
        self.assertEqual(crl.validate_entry_files({"2026-10-12-model-00640-H5-step3.md": entry()}, self.HYP), [])

    def test_a_directive_named_file_matches_any_issue_its_directive_line_names(self):
        text = entry().replace("- Directive: #640", "- Directive: #640 (follow-up of #611)")
        self.assertEqual(crl.validate_entry_files({"2026-10-12-model-00611-H5-step3.md": text}, self.HYP), [])

    def test_a_number_that_is_neither_the_pull_request_nor_the_directive_is_refused(self):
        for bad in ("2026-10-12-model-00641-H5-step3.md", "2026-10-12-model-00000-H5-step3.md"):
            with self.subTest(name=bad):
                self.assertTrue(crl.validate_entry_files({bad: entry()}, self.HYP))

    def test_a_directive_named_file_must_still_agree_on_date_repository_hypothesis_and_step(self):
        for bad in ("2026-10-13-model-00640-H5-step3.md", "2026-10-12-liquidity-00640-H5-step3.md",
                    "2026-10-12-model-00640-H7-step3.md", "2026-10-12-model-00640-H5-step2.md"):
            with self.subTest(name=bad):
                self.assertTrue(crl.validate_entry_files({bad: entry()}, self.HYP))

    def test_a_badly_named_file_is_refused(self):
        self.assertTrue(crl.validate_entry_files({"notes.md": entry()}, self.HYP))

    def test_a_file_with_two_entries_is_refused(self):
        self.assertTrue(crl.validate_entry_files({NAME: entry() + "\n" + entry(pr=701)}, self.HYP))

    def test_a_file_that_does_not_start_with_its_heading_is_refused(self):
        self.assertTrue(crl.validate_entry_files({NAME: "text\n" + entry()}, self.HYP))

    def test_a_malformed_entry_is_refused_by_name(self):
        errors = crl.validate_entry_files({NAME: entry().replace("- Result: r\n", "")}, self.HYP)
        self.assertTrue(any("Result" in e for e in errors), errors)

    def test_a_groundwork_file_is_named_by_its_g_number(self):
        text = entry(hyp="H7", pr=44, repo="liquidity").replace("step 3 · ", "groundwork G5 · ")
        self.assertEqual(crl.validate_entry_files({"2026-10-12-liquidity-00044-H7-G5.md": text}, self.HYP), [])

    def test_conflict_markers_in_an_entry_file_are_refused(self):
        self.assertTrue(crl.validate_entry_files({NAME: entry() + "<<<<<<< HEAD\n"}, self.HYP))


class FrozenTests(unittest.TestCase):
    """Append-only (#638): an entry already on the base is never edited, renamed or deleted."""

    def test_a_new_entry_file_is_allowed(self):
        self.assertEqual(crl.frozen_errors({NAME: entry()}, {NAME: entry(), "2026-10-13-model-00701-H5-step3.md": "x"}), [])

    def test_a_changed_entry_file_is_refused(self):
        self.assertTrue(crl.frozen_errors({NAME: entry()}, {NAME: entry(marker="edited")}))

    def test_a_deleted_entry_file_is_refused(self):
        self.assertTrue(crl.frozen_errors({NAME: entry()}, {}))

    def test_a_renamed_entry_file_is_refused(self):
        self.assertTrue(crl.frozen_errors({NAME: entry()}, {"2026-10-13-model-00700-H5-step3.md": entry()}))


REPO = "eleonorabjornberg/repo-market-model"


def correction(name=NAME, old=700, new=737, repo=REPO, new_repo=None):
    return "- %s: %s#%d -> %s#%d\n" % (name, repo, old, new_repo or repo, new)


class CorrectionTests(unittest.TestCase):
    """The heading of a frozen entry is corrected by a line in `_corrections.md`, never by editing the entry (#867)."""

    def test_a_correction_changes_the_assembled_heading_and_keeps_the_original_visible(self):
        text = crl.assemble(HEADER, {NAME: entry(pr=700)}, correction())
        self.assertIn("### 2026-10-12 [H5] step 3 · %s#737\n" % REPO, text)
        self.assertNotIn("### 2026-10-12 [H5] step 3 · %s#700\n" % REPO, text)
        self.assertIn("- Correction: the heading named %s#700; corrected to %s#737 "
                      "(docs/research/log/_corrections.md).\n" % (REPO, REPO), text)

    def test_the_corrected_assembly_still_passes_the_log_format(self):
        text = crl.assemble(HEADER, {NAME: entry(pr=700)}, correction())
        self.assertEqual(crl.validate_log(text, {"H5"}), [])

    def test_without_corrections_the_assembly_is_unchanged(self):
        self.assertEqual(crl.assemble(HEADER, {NAME: entry()}, ""), crl.assemble(HEADER, {NAME: entry()}))

    def test_a_sound_correction_passes(self):
        self.assertEqual(crl.correction_errors(correction(), {NAME: entry(pr=700)}), [])

    def test_a_correction_for_a_missing_entry_is_refused(self):
        self.assertTrue(crl.correction_errors(correction(name="2026-10-12-model-00999-H5-step3.md"), {NAME: entry()}))

    def test_a_correction_whose_old_reference_is_not_the_headings_is_refused(self):
        self.assertTrue(crl.correction_errors(correction(old=701), {NAME: entry(pr=700)}))

    def test_a_correction_that_changes_more_than_the_pull_request_number_is_refused(self):
        self.assertTrue(crl.correction_errors(correction(new_repo="eleonorabjornberg/repo-market-liquidity"),
                                              {NAME: entry(pr=700)}))

    def test_two_corrections_of_one_entry_are_refused(self):
        self.assertTrue(crl.correction_errors(correction() + correction(new=738), {NAME: entry(pr=700)}))

    def test_a_malformed_correction_line_is_refused(self):
        self.assertTrue(crl.correction_errors("- not a correction\n", {NAME: entry()}))

    def test_the_corrections_file_is_not_an_entry_file(self):
        header, files = crl.read_entry_files()
        self.assertNotIn(crl.CORRECTIONS_NAME, files)

    def test_the_corrections_file_is_not_frozen_as_an_entry(self):
        self.assertEqual(crl.frozen_errors({NAME: entry()}, {NAME: entry()}), [])


class RepositoryTests(unittest.TestCase):

    def test_there_are_entry_files_and_log_md_is_not_tracked(self):
        """`log.md` is built on main and never committed (#928): the entry files are the log."""
        header, files = crl.read_entry_files()
        self.assertTrue(files)
        tracked = subprocess.run(["git", "ls-files", "docs/research/log.md"], cwd=ROOT, capture_output=True,
                                 text=True, check=True).stdout.split()
        self.assertEqual(crl.tracked_errors(tracked), [])

    def test_every_correction_in_the_repository_is_sound(self):
        header, files = crl.read_entry_files()
        self.assertEqual(crl.correction_errors(crl.read_corrections(), files), [])

    def test_the_heading_of_the_785_entry_names_837_and_its_file_is_untouched(self):
        header, files = crl.read_entry_files()
        name = "0094-2026-10-16-model-00830-H5-step3.md"
        self.assertIn("model#830\n", files[name].splitlines()[0] + "\n")
        self.assertIn("### 2026-10-16 [H5] step 3 · eleonorabjornberg/repo-market-model#837\n",
                      crl.assemble(header, files, crl.read_corrections()))

    def test_every_entry_file_passes(self):
        header, files = crl.read_entry_files()
        plan = (ROOT / "docs" / "research" / "plan.md").read_text()
        self.assertEqual(crl.validate_entry_files(files, crl.plan_hypotheses(plan)), [])

    def test_the_assembled_check_fails_on_a_tracked_log(self):
        self.assertTrue(crl.tracked_errors(["docs/research/log.md"]))
        self.assertEqual(crl.tracked_errors([]), [])


if __name__ == "__main__":
    unittest.main()
