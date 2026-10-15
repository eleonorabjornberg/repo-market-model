"""The research log's check (#638): `scripts/check_research_log.py`.

`docs/research/plan.md` names the hypotheses and `docs/research/log.md` keeps one dated entry per scored
experiment. The check refuses (1) a log entry whose heading or lines break the format, (2) a log entry that
names a hypothesis the plan does not have, and (3) a change to a result page (`docs/pivot/*-result.md`) or to a
declaration or candidate under `metadata/` that adds no new log entry naming the pull request's directive.

Written before the script: this module failed on the missing script first (`FileNotFoundError`).
Recorded mutations, each killing the named test:

* `if hypothesis not in hypotheses:` replaced by `if False:` in `validate_log` fails
  `test_a_hypothesis_the_plan_lacks_is_refused` (`AssertionError: False is not true : []`);
* `needed = paths_needing_entry(changed)` replaced by `needed = []` in `check_change` fails
  `test_a_result_page_without_a_new_entry_is_refused` (`AssertionError: [] is not true`);
* `new_entries` returning every entry of the head log, not those absent from the base, fails
  `test_an_entry_already_in_the_base_does_not_count` (`AssertionError: [] is not true`);
* groundwork headings (#701; the tests failed first on the old `HEADING`): `G[1-9]\d*` replaced by `G\d*` in
  `HEADING` fails `test_a_malformed_groundwork_heading_is_refused` for `groundwork G` and `groundwork G0`
  (`AssertionError: [] is not true`).
"""
import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_research_log.py"
_spec = importlib.util.spec_from_file_location("check_research_log", SCRIPT)
crl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crl)

PLAN = "# Plan\n\n## H1. The scorer\n\ntext\n\n## H5 (primary goal). The spread\n\n## H10. Attribution\n"


def entry(date="2026-10-12", hyp="H5", step=3, ref="eleonorabjornberg/repo-market-model#700", directive="#640",
          tier="development", drop=(), extra=()):
    lines = ["### %s [%s] step %s · %s" % (date, hyp, step, ref)]
    fields = [("Directive", directive), ("Step", str(step)), ("Tier", tier), ("Pins", "panel 4ddc3882"),
              ("Tried", "2 variants"), ("Result", "CRPS skill 0.01 [-0.02, 0.04]"),
              ("Against kill", "plan.md H5"), ("Next", "register")]
    for name, value in fields:
        if name not in drop:
            lines.append("- %s: %s" % (name, value))
    lines.extend(extra)
    return "\n".join(lines) + "\n"


def log(*entries):
    return "# Research log\n\nintro\n\n" + "\n".join(entries)


class FormatTests(unittest.TestCase):

    def test_a_well_formed_entry_passes(self):
        self.assertEqual(crl.validate_log(log(entry()), {"H5"}), [])

    def test_the_hypotheses_come_from_the_plan_headings(self):
        self.assertEqual(crl.plan_hypotheses(PLAN), {"H1", "H5", "H10"})

    def test_a_hypothesis_the_plan_lacks_is_refused(self):
        errors = crl.validate_log(log(entry(hyp="H11")), {"H1", "H5"})
        self.assertTrue(any("H11" in e and "plan" in e for e in errors), errors)

    def test_a_malformed_heading_is_refused(self):
        text = log(entry().replace("### 2026-10-12 [H5] step 3 · ", "### October 12 H5 "))
        self.assertTrue(crl.validate_log(text, {"H5"}))

    def test_a_groundwork_heading_is_accepted(self):
        text = log(entry().replace("step 3 · ", "groundwork G3 · "))
        self.assertEqual(crl.validate_log(text, {"H5"}), [])

    def test_a_malformed_groundwork_heading_is_refused(self):
        for bad in ("groundwork 3", "groundwork G", "groundwork g3", "groundwork G3/G4", "groundwork G0",
                    "groundwork G3 step 3", "groundwork"):
            with self.subTest(heading=bad):
                text = log(entry().replace("step 3 · ", bad + " · "))
                self.assertTrue(crl.validate_log(text, {"H5"}))

    def test_a_groundwork_entry_still_needs_its_lines_and_a_known_hypothesis(self):
        text = log(entry(hyp="H11", drop=("Result",)).replace("step 3 · ", "groundwork G3 · "))
        errors = crl.validate_log(text, {"H5"})
        self.assertTrue(any("H11" in e for e in errors), errors)
        self.assertTrue(any("Result" in e for e in errors), errors)

    def test_an_impossible_date_is_refused(self):
        self.assertTrue(crl.validate_log(log(entry(date="2026-13-40")), {"H5"}))

    def test_a_step_outside_one_to_six_is_refused(self):
        self.assertTrue(crl.validate_log(log(entry(step=7)), {"H5"}))

    def test_every_required_line_is_required(self):
        for name in crl.REQUIRED_LINES:
            with self.subTest(line=name):
                errors = crl.validate_log(log(entry(drop=(name,))), {"H5"})
                self.assertTrue(any(name in e for e in errors), errors)

    def test_the_directive_line_must_name_an_issue(self):
        self.assertTrue(crl.validate_log(log(entry(directive="the scorer")), {"H5"}))

    def test_the_tier_is_development_or_confirmation(self):
        self.assertTrue(crl.validate_log(log(entry(tier="exploration")), {"H5"}))
        self.assertEqual(crl.validate_log(log(entry(tier="confirmation")), {"H5"}), [])

    def test_a_log_with_no_entries_passes(self):
        self.assertEqual(crl.validate_log("# Research log\n\nnothing yet\n", {"H5"}), [])

    def test_a_liquidity_repo_entry_is_accepted(self):
        text = log(entry(hyp="H10", ref="eleonorabjornberg/repo-market-liquidity#20"))
        self.assertEqual(crl.validate_log(text, {"H10"}), [])

    def test_blocks_are_read_from_a_pull_request_body(self):
        body = "text\n```research-log\n%s```\nmore\n" % entry(hyp="H10", ref="o/r#20")
        blocks = crl.extract_blocks(body)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(crl.validate_log(blocks[0], {"H10"}), [])


class ChangeTests(unittest.TestCase):

    def test_which_paths_need_an_entry(self):
        needs = crl.paths_needing_entry
        self.assertEqual(needs(["docs/pivot/foo-result.md"]), ["docs/pivot/foo-result.md"])
        self.assertEqual(needs(["metadata/pressure_judge/candidates/x.json"]),
                         ["metadata/pressure_judge/candidates/x.json"])
        self.assertEqual(needs(["metadata/structural_liquidity.json"]), ["metadata/structural_liquidity.json"])
        self.assertEqual(needs(["metadata/lockbox.json", "metadata/events.json", "README.md",
                                "docs/pivot/evidence/x/summary.md", "docs/pivot/plan.md"]), [])

    def test_a_result_page_without_a_new_entry_is_refused(self):
        errors = crl.check_change(["docs/pivot/foo-result.md"], log(), log(), ["#700"])
        self.assertTrue(errors)

    def test_a_result_page_with_a_new_entry_naming_the_directive_passes(self):
        head = log(entry(directive="#700"))
        self.assertEqual(crl.check_change(["docs/pivot/foo-result.md"], log(), head, ["#700"]), [])

    def test_an_entry_naming_another_directive_does_not_count(self):
        head = log(entry(directive="#641"))
        self.assertTrue(crl.check_change(["metadata/x.json"], log(), head, ["#700"]))

    def test_an_entry_already_in_the_base_does_not_count(self):
        base = log(entry(directive="#700"))
        self.assertTrue(crl.check_change(["metadata/x.json"], base, base, ["#700"]))

    def test_a_change_needing_no_entry_passes_without_a_directive(self):
        self.assertEqual(crl.check_change(["README.md"], log(), log(), []), [])

    def test_a_change_needing_an_entry_with_no_directive_is_refused(self):
        self.assertTrue(crl.check_change(["docs/pivot/foo-result.md"], log(), log(entry()), []))

    def test_the_directives_are_read_from_closes_lines(self):
        body = "Closes #638\n\nfixes #5 and Closes #7"
        self.assertEqual(crl.closed_issues(body), ["#638", "#7"])


class RepositoryTests(unittest.TestCase):

    def test_the_committed_plan_and_log_pass(self):
        plan = (ROOT / "docs" / "research" / "plan.md").read_text()
        text = (ROOT / "docs" / "research" / "log.md").read_text()
        self.assertEqual(crl.validate_log(text, crl.plan_hypotheses(plan)), [])

    def test_the_plan_has_all_ten_hypotheses_and_a_manual_each(self):
        plan = (ROOT / "docs" / "research" / "plan.md").read_text()
        self.assertEqual(crl.plan_hypotheses(plan), {"H%d" % n for n in range(1, 11)})
        for n in range(1, 11):
            self.assertTrue((ROOT / "docs" / "research" / "hypotheses" / ("H%d.md" % n)).is_file())

    def test_the_command_passes_on_the_tree(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        done = subprocess.run([sys.executable, "-B", str(SCRIPT), "check"], cwd=ROOT, env=env,
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
