"""The workflows, read off the files: pins, timeouts and the checks CI runs (#268, finding 21).

Stdlib only, so no YAML parser: each file is read as indented lines. What is
held, for **every** file in `.github/workflows/`:

* every `uses:` line names a full 40-hex commit SHA, with the tag in a trailing
  comment, except the actions in `PENDING_PINS`, which is empty;
* every job has `timeout-minutes`;
* `tests.yml` checks out the whole history in each job (the results page and
  `docs/status.json` are stamped from git history, and the commit-stamp test
  skips on a shallow clone) and runs `emit_visual.py --check`.

**The SHA pins** were resolved on 6 October 2026 by the orchestrating session, under
Eleonora's delegation, with `git ls-remote https://github.com/<action> refs/tags/<tag>
'refs/tags/<tag>^{}'` (all five are lightweight tags, so the tag's commit is the SHA), and
read again by the fix run with the same command. `PENDING_PINS` is kept as an empty set: a
new unpinned action fails here unless it is listed on purpose.

**Recorded mutation**, 6 October 2026: in `tests.yml`, the first
`timeout-minutes: 60` line deleted. `test_every_job_has_a_timeout` then fails
with `AssertionError: ... has no timeout-minutes`. Separately, `fetch-depth: 0`
deleted from a checkout: `test_tests_yml_checks_out_the_whole_history` fails with
`AssertionError`.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

WORKFLOWS = sorted((Path(__file__).resolve().parents[1] / ".github" / "workflows").glob("*.yml"))

#: Actions still used by tag. Empty: every action is pinned to its commit SHA.
PENDING_PINS = set()

USES = re.compile(r"^\s*-?\s*uses:\s*(\S+)(.*)$")
PINNED = re.compile(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}$")


def lines_of(path):
    return path.read_text(encoding="utf-8").splitlines()


def jobs(path):
    """`{job id: its lines}` for the jobs under the top-level `jobs:`."""

    out, inside, current = {}, False, None
    for line in lines_of(path):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            inside = line.split("#")[0].strip() == "jobs:"
            current = None
            continue
        match = re.match(r"^  ([\w-]+):\s*$", line)
        if inside and match:
            current = match.group(1)
            out[current] = []
        elif inside and current:
            out[current].append(line)
    return out


class WorkflowFileTests(unittest.TestCase):
    def test_there_are_workflows(self):
        self.assertEqual({path.name for path in WORKFLOWS},
                         {"live-log.yml", "pages.yml", "status.yml", "tests.yml"})

    def test_every_action_is_pinned_to_a_full_commit_sha_or_pending(self):
        found = set()
        for path in WORKFLOWS:
            for line in lines_of(path):
                match = USES.match(line)
                if not match:
                    continue
                action, rest = match.groups()
                with self.subTest(file=path.name, action=action):
                    if action in PENDING_PINS:
                        found.add(action)
                        continue
                    self.assertRegex(action, PINNED)
                    self.assertRegex(rest.strip(), r"^# v?\d")
        self.assertEqual(found, PENDING_PINS, "PENDING_PINS lists an action no workflow uses, or one is missing")

    def test_every_job_has_a_timeout(self):
        for path in WORKFLOWS:
            for job, body in jobs(path).items():
                with self.subTest(file=path.name, job=job):
                    self.assertTrue(
                        any(re.match(r"^    timeout-minutes: \d+\s*$", line) for line in body),
                        f"{path.name} job {job} has no timeout-minutes",
                    )

    def test_jobs_are_found(self):
        self.assertEqual(set(jobs(next(p for p in WORKFLOWS if p.name == "tests.yml"))), {"suite", "ml", "owner-attested"})

    def test_tests_yml_checks_out_the_whole_history(self):
        path = next(p for p in WORKFLOWS if p.name == "tests.yml")
        for job, body in jobs(path).items():
            text = "\n".join(body)
            for match in re.finditer(r"- uses: actions/checkout@\S+\n(\s+with:\n(?:\s+\S.*\n)*)?", text + "\n"):
                with self.subTest(job=job):
                    self.assertIn("fetch-depth: 0", match.group(1) or "")

    def test_tests_yml_runs_the_results_page_check(self):
        path = next(p for p in WORKFLOWS if p.name == "tests.yml")
        text = "\n".join(jobs(path)["suite"])
        self.assertIn("scripts/emit_visual.py --check", text)


if __name__ == "__main__":
    unittest.main()
