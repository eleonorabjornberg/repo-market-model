"""The live record's integrity (#254): hash chain, add-only commits, digests, and the scorer's refusal.

An independent review of 6 October 2026 found that nothing in the repository
established the live record's immutability (#254, review finding 1). The
ruleset on `live-log` forbids deletion and non-fast-forward pushes, but a
fast-forward commit could still change or delete an existing
`live/YYYY-MM-DD.json`. `scripts/live_integrity.py` adds the controls the
directive asks for. These tests pin them:

* **the hash chain** (`ChainTests`): from the first record after #254 merges,
  each record carries `chain.prev_date`, `chain.prev_sha256` and
  `chain.prev_commit`. The first chained record points at the last unchained
  one. An unchained record after the chain has begun is refused, and so is a
  link that does not match its predecessor's bytes or commit;
* **the add-only commit** (`AppendOnlyTests`): before the workflow pushes, the
  new commit only adds `live/<today>.json`, as `github-actions[bot]`, and
  changes no other path;
* **the digests** (`DigestTests`): every file's SHA-256 equals its digest on
  #225, and the digest names the commit that added the file. Only the bot's
  comments count;
* **the scorer** (`ScorerRefusalTests`): `live_score.py` refuses to score
  unless all of the above hold;
* **the workflow** (`WorkflowIntegrityTests`): the chain, the add-only check
  before `git push`, and a daily integrity step whose failure reaches the
  failed-runs issue.

Red first: this file was committed, and run, before `scripts/live_integrity.py`
existed. Every class failed at import with `FileNotFoundError`.

Recorded mutations, each run in a disposable copy under /tmp with the mutated
line confirmed applied by grep, and each killed by the test named:

* add-only: in `require_add_only_commit`, `if changes != [("A", expected)]:`
  -> `if False:` makes `test_a_commit_that_changes_an_existing_file_is_refused`
  fail with `AssertionError: ValueError not raised`.
* digest match: in `verify`, `if digest["sha256"] != digest_of:` -> `if False:`
  makes `test_a_file_whose_bytes_differ_from_its_digest_is_refused` fail with
  `AssertionError: ValueError not raised`.
* chain: in `require_chain`, `if chain != expected:` -> `if False:` makes
  `test_a_link_that_does_not_match_its_predecessor_is_refused` fail with
  `AssertionError: ValueError not raised`.
* scorer refusal: in `live_score.load_records`, `integrity.verify(live_dir,
  integrity.parse_digests(digests))` -> `pass` makes
  `test_a_tampered_log_is_refused_before_anything_is_scored` fail with
  `AssertionError: ValueError not raised`, and
  `test_the_script_refuses_a_tampered_log` fail with `FileNotFoundError`
  (the scorer went on to read the panel).
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from test_live_record import _record, live, score

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "live-log.yml"


def _load():
    spec = importlib.util.spec_from_file_location(
        "live_integrity_test", ROOT / "scripts" / "live_integrity.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


integrity = _load()

BOT = {
    "GIT_AUTHOR_NAME": "github-actions[bot]",
    "GIT_AUTHOR_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "github-actions[bot]",
    "GIT_COMMITTER_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
}
SOMEONE = {
    "GIT_AUTHOR_NAME": "someone",
    "GIT_AUTHOR_EMAIL": "someone@example.com",
    "GIT_COMMITTER_NAME": "someone",
    "GIT_COMMITTER_EMAIL": "someone@example.com",
}


def git(repo, *argv, env=None):
    full = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", **(env or BOT)}
    return subprocess.run(
        ["git", *argv], cwd=repo, check=True, capture_output=True, text=True, env=full
    ).stdout.strip()


def new_log(tmp) -> Path:
    repo = Path(tmp) / "live-log"
    repo.mkdir()
    git(repo, "init", "--quiet", "-b", "live-log")
    return repo


def write_day(repo: Path, day: str, *, chained=True) -> Path:
    """Write a day's record as the pinned code does, then chain it as the workflow does."""

    path = repo / "live" / f"{day}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(live.record_bytes(_record(day)))
    if chained:
        integrity.add_chain(repo, date.fromisoformat(day))
    return path


def commit_day(repo: Path, day: str, *, env=None) -> str:
    git(repo, "add", f"live/{day}.json", env=env)
    git(repo, "commit", "--quiet", "-m", f"Live record for {day}", env=env)
    return git(repo, "rev-parse", "HEAD")


def build_log(tmp, days=("2026-10-05", "2026-10-06", "2026-10-07"), unchained=("2026-10-05",)):
    """A live-log with the first day unchained, as on the real branch, and its digests."""

    repo = new_log(tmp)
    for day in days:
        write_day(repo, day, chained=day not in unchained)
        commit_day(repo, day)
    return repo, digests_of(repo)


def digest_body(day, sha256, commit) -> str:
    """A digest comment, in the words `.github/workflows/live-log.yml` posts."""

    return "\n".join(
        [
            f"{day}: `live/{day}.json`",
            "",
            f"- SHA-256: `{sha256}`",
            f"- commit on live-log: {commit}",
            f"- code: {'c' * 40}",
            "- run: https://github.com/eleonorabjornberg/repo-market-model/actions/runs/1",
        ]
    )


def digests_of(repo: Path) -> list:
    comments = []
    for path in sorted((repo / "live").glob("*.json")):
        commit = git(repo, "log", "--format=%H", "--", f"live/{path.name}").splitlines()[-1]
        comments.append(
            {
                "author": "github-actions[bot]",
                "body": digest_body(path.stem, integrity.file_sha256(path), commit),
            }
        )
    return comments


def save(comments, tmp) -> Path:
    path = Path(tmp) / "digests.jsonl"
    path.write_text("".join(json.dumps(c) + "\n" for c in comments), encoding="utf-8")
    return path


class ChainTests(unittest.TestCase):
    def test_a_well_formed_log_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            days = integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))
            self.assertEqual([d.isoformat() for d in days], ["2026-10-05", "2026-10-06", "2026-10-07"])

    def test_the_first_chained_record_points_at_the_last_unchained_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = build_log(tmp)
            first = repo / "live" / "2026-10-05.json"
            chained = json.loads((repo / "live" / "2026-10-06.json").read_text(encoding="utf-8"))
            self.assertEqual(
                chained["chain"],
                {
                    "prev_date": "2026-10-05",
                    "prev_sha256": integrity.file_sha256(first),
                    "prev_commit": git(repo, "log", "--format=%H", "--", "live/2026-10-05.json"),
                },
            )
            self.assertNotIn("chain", json.loads(first.read_text(encoding="utf-8")))

    def test_the_chained_record_keeps_the_pinned_codes_bytes_otherwise(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            write_day(repo, "2026-10-05", chained=False)
            commit_day(repo, "2026-10-05")
            path = write_day(repo, "2026-10-06")
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(path.read_bytes(), live.record_bytes(record))
            del record["chain"]
            self.assertEqual(record, _record("2026-10-06"))
            # The scorer's schema check accepts a chained record.
            live.validate_record(json.loads(path.read_text(encoding="utf-8")))

    def test_a_link_that_does_not_match_its_predecessor_is_refused(self):
        for field, value in (("prev_sha256", "f" * 64), ("prev_commit", "e" * 40), ("prev_date", "2026-10-02")):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = new_log(tmp)
                    write_day(repo, "2026-10-05", chained=False)
                    commit_day(repo, "2026-10-05")
                    path = write_day(repo, "2026-10-06")
                    record = json.loads(path.read_text(encoding="utf-8"))
                    record["chain"][field] = value
                    path.write_bytes(live.record_bytes(record))
                    commit_day(repo, "2026-10-06")
                    # The digests match the files: only the chain is wrong.
                    with self.assertRaisesRegex(ValueError, "chain"):
                        integrity.verify(repo, integrity.parse_digests(save(digests_of(repo), tmp)))

    def test_an_unchained_record_after_the_chain_began_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = build_log(tmp, days=("2026-10-05", "2026-10-06", "2026-10-07"),
                                unchained=("2026-10-05", "2026-10-07"))
            with self.assertRaisesRegex(ValueError, "chain"):
                integrity.verify(repo, integrity.parse_digests(save(digests_of(repo), tmp)))

    def test_a_record_that_is_already_chained_or_committed_is_not_chained_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            write_day(repo, "2026-10-05", chained=False)
            commit_day(repo, "2026-10-05")
            with self.assertRaises(ValueError):
                integrity.add_chain(repo, date(2026, 10, 5))
            write_day(repo, "2026-10-06")
            with self.assertRaises(ValueError):
                integrity.add_chain(repo, date(2026, 10, 6))

    def test_the_first_record_of_an_empty_log_has_nothing_to_point_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            path = write_day(repo, "2026-10-06")
            self.assertNotIn("chain", json.loads(path.read_text(encoding="utf-8")))

    def test_a_malformed_chain_fails_the_schema(self):
        record = _record("2026-10-06")
        live.validate_record({**record, "chain": {"prev_date": "2026-10-05", "prev_sha256": "a" * 64,
                                                  "prev_commit": "b" * 40}})
        for chain in (
            {"prev_date": "2026-10-05", "prev_sha256": "a" * 64},
            {"prev_date": "2026-10-06", "prev_sha256": "a" * 64, "prev_commit": "b" * 40},
            {"prev_date": "2026-10-05", "prev_sha256": "a" * 63, "prev_commit": "b" * 40},
            {"prev_date": "2026-10-05", "prev_sha256": "a" * 64, "prev_commit": "B" * 40},
        ):
            with self.subTest(chain=chain):
                with self.assertRaises(ValueError):
                    live.validate_record({**record, "chain": chain})


class AppendOnlyTests(unittest.TestCase):
    def test_a_commit_that_only_adds_the_days_file_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            write_day(repo, "2026-10-05", chained=False)
            base = commit_day(repo, "2026-10-05")
            write_day(repo, "2026-10-06")
            commit_day(repo, "2026-10-06")
            integrity.require_append_only(repo, base, date(2026, 10, 6))

    def test_the_first_commit_of_a_new_branch_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            write_day(repo, "2026-10-06")
            commit_day(repo, "2026-10-06")
            integrity.require_append_only(repo, None, date(2026, 10, 6))

    def test_a_commit_that_changes_an_existing_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            first = write_day(repo, "2026-10-05", chained=False)
            base = commit_day(repo, "2026-10-05")
            first.write_bytes(first.read_bytes().replace(b"0.1", b"0.2"))
            git(repo, "add", "live/2026-10-05.json")
            path = write_day(repo, "2026-10-06", chained=False)
            git(repo, "add", "live/2026-10-06.json")
            git(repo, "commit", "--quiet", "-m", "Live record for 2026-10-06")
            self.assertTrue(path.exists())
            with self.assertRaisesRegex(ValueError, "only add"):
                integrity.require_append_only(repo, base, date(2026, 10, 6))

    def test_each_other_change_is_refused(self):
        def modified(repo):
            path = repo / "live" / "2026-10-05.json"
            path.write_bytes(path.read_bytes() + b" ")
            git(repo, "commit", "--quiet", "-am", "edit")

        def deleted(repo):
            git(repo, "rm", "--quiet", "live/2026-10-05.json")
            git(repo, "commit", "--quiet", "-m", "delete")

        def other_day(repo):
            write_day(repo, "2026-10-07")
            commit_day(repo, "2026-10-07")

        def another_path(repo):
            write_day(repo, "2026-10-06")
            (repo / "notes.txt").write_text("x")
            git(repo, "add", "live/2026-10-06.json", "notes.txt")
            git(repo, "commit", "--quiet", "-m", "two paths")

        def by_someone_else(repo):
            write_day(repo, "2026-10-06")
            commit_day(repo, "2026-10-06", env=SOMEONE)

        def two_commits(repo):
            (repo / "notes.txt").write_text("x")
            git(repo, "add", "notes.txt")
            git(repo, "commit", "--quiet", "-m", "first")
            git(repo, "rm", "--quiet", "notes.txt")
            git(repo, "commit", "--quiet", "-m", "second")
            write_day(repo, "2026-10-06")
            commit_day(repo, "2026-10-06")

        for name, change in (("modified", modified), ("deleted", deleted), ("other day", other_day),
                             ("another path", another_path), ("by someone else", by_someone_else),
                             ("two commits", two_commits)):
            with self.subTest(case=name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = new_log(tmp)
                    write_day(repo, "2026-10-05", chained=False)
                    base = commit_day(repo, "2026-10-05")
                    change(repo)
                    with self.assertRaises(ValueError):
                        integrity.require_append_only(repo, base, date(2026, 10, 6))

    def test_verify_refuses_any_commit_in_history_that_is_not_add_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            path = repo / "live" / "2026-10-07.json"
            path.write_bytes(path.read_bytes().replace(b"0.1", b"0.2"))
            git(repo, "commit", "--quiet", "-am", "Live record for 2026-10-07")
            with self.assertRaisesRegex(ValueError, "only add"):
                integrity.verify(repo, integrity.parse_digests(save(digests_of(repo), tmp)))

    def test_verify_refuses_a_file_added_by_someone_else(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = build_log(tmp, days=("2026-10-05",))
            write_day(repo, "2026-10-06")
            commit_day(repo, "2026-10-06", env=SOMEONE)
            with self.assertRaisesRegex(ValueError, "github-actions"):
                integrity.verify(repo, integrity.parse_digests(save(digests_of(repo), tmp)))

    def test_verify_refuses_an_uncommitted_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            path = repo / "live" / "2026-10-07.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))


class DigestTests(unittest.TestCase):
    def test_a_file_whose_bytes_differ_from_its_digest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            # History rewritten from scratch with a different last file: every
            # commit is add-only and the chain holds, but the digest does not.
            rewritten = Path(tmp) / "rewritten"
            rewritten.mkdir()
            other = new_log(rewritten)
            for day in ("2026-10-05", "2026-10-06"):
                write_day(other, day, chained=day != "2026-10-05")
                commit_day(other, day)
            path = other / "live" / "2026-10-07.json"
            record = _record("2026-10-07")
            record["models"]["pressure_model_v1"]["forecasts"]["1"]["+5bp"] = 0.9
            path.write_bytes(live.record_bytes(record))
            integrity.add_chain(other, date(2026, 10, 7))
            commit_day(other, "2026-10-07")
            forged = [c for c in digests_of(other) if not c["body"].startswith("2026-10-07")]
            commit = git(other, "rev-parse", "HEAD")
            original = [c for c in comments if c["body"].startswith("2026-10-07")][0]
            sha = re.search(r"SHA-256: `([0-9a-f]{64})`", original["body"]).group(1)
            forged.append({"author": "github-actions[bot]", "body": digest_body("2026-10-07", sha, commit)})
            with self.assertRaisesRegex(ValueError, "digest"):
                integrity.verify(other, integrity.parse_digests(save(forged, tmp)))

    def test_a_digest_that_names_another_commit_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            comments[-1]["body"] = re.sub(r"live-log: [0-9a-f]{40}", "live-log: " + "a" * 40, comments[-1]["body"])
            with self.assertRaisesRegex(ValueError, "digest"):
                integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))

    def test_a_file_with_no_digest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            with self.assertRaisesRegex(ValueError, "digest"):
                integrity.verify(repo, integrity.parse_digests(save(comments[:-1], tmp)))

    def test_a_digested_day_with_no_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            extra = digest_body("2026-10-08", "a" * 64, "b" * 40)
            comments.append({"author": "github-actions[bot]", "body": extra})
            with self.assertRaisesRegex(ValueError, "no file"):
                integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))

    def test_only_the_bots_comments_are_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            for comment in comments:
                if comment["body"].startswith("2026-10-07"):
                    comment["author"] = "someone"
            with self.assertRaisesRegex(ValueError, "digest"):
                integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))

    def test_two_different_digests_for_one_day_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            comments.append({"author": "github-actions[bot]",
                             "body": digest_body("2026-10-07", "a" * 64, "b" * 40)})
            with self.assertRaises(ValueError):
                integrity.parse_digests(save(comments, tmp))

    def test_the_real_digest_format_parses(self):
        """The digest posted for 2026-10-05 on #225, verbatim."""

        body = (
            "2026-10-05: `live/2026-10-05.json`\n\n"
            "- SHA-256: `3b6aa1651cca0805ce45a6dea9c3a8f8977094fa4359a3ca1232330364d00baf`\n"
            "- commit on live-log: d7025d71a018054de6adeef88b081ce09fbb02a4\n"
            "- code: c69a361965fd601a4e69fdbc92643d669dba8e9e\n"
            "- run: https://github.com/eleonorabjornberg/repo-market-model/actions/runs/37368170164"
        )
        with tempfile.TemporaryDirectory() as tmp:
            parsed = integrity.parse_digests(save([{"author": "github-actions[bot]", "body": body}], tmp))
        self.assertEqual(
            parsed,
            {
                date(2026, 10, 5): {
                    "sha256": "3b6aa1651cca0805ce45a6dea9c3a8f8977094fa4359a3ca1232330364d00baf",
                    "commit": "d7025d71a018054de6adeef88b081ce09fbb02a4",
                }
            },
        )

    def test_a_malformed_bot_digest_is_refused(self):
        body = "2026-10-05: `live/2026-10-05.json`\n\n- SHA-256: `xyz`\n"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                integrity.parse_digests(save([{"author": "github-actions[bot]", "body": body}], tmp))


class ScorerRefusalTests(unittest.TestCase):
    def test_an_intact_log_is_loaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            records = score.load_records(repo, save(comments, tmp))
            self.assertEqual([r["decision_day"] for r in records], ["2026-10-05", "2026-10-06", "2026-10-07"])

    def test_a_tampered_log_is_refused_before_anything_is_scored(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            comments = [c for c in comments if not c["body"].startswith("2026-10-06")]
            with self.assertRaises(ValueError):
                score.load_records(repo, save(comments, tmp))

    def test_no_digests_no_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = build_log(tmp)
            with self.assertRaises(ValueError):
                score.load_records(repo, None)

    def test_the_script_refuses_a_tampered_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            comments = [c for c in comments if not c["body"].startswith("2026-10-06")]
            lockbox = Path(tmp) / "lockbox.md"
            lockbox.write_text(score.AMENDMENT_HEADING + "\n", encoding="utf-8")
            out = Path(tmp) / "out.json"
            with mock.patch.object(score, "LOCKBOX", lockbox):
                with self.assertRaisesRegex(ValueError, "digest"):
                    score.main(
                        ["--date", "2027-10-01", "--live-dir", str(repo), "--digests",
                         str(save(comments, tmp)), "--panel", str(Path(tmp) / "missing.csv"),
                         "--output", str(out)]
                    )
            self.assertFalse(out.exists())


class WorkflowIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def _step(self, name):
        match = re.search(rf"\n      - name: {re.escape(name)}\n(.*?)(?=\n      - name: |\Z)", self.text, re.S)
        self.assertIsNotNone(match, name)
        return match.group(1)

    def test_the_record_is_chained_and_checked_add_only_before_it_is_pushed(self):
        step = self._step("Append it to live-log")
        chain = step.index("live_integrity.py chain")
        commit = step.index("commit --quiet")
        check = step.index("live_integrity.py check-append")
        push = step.index("git push")
        self.assertLess(chain, commit)
        self.assertLess(commit, check)
        self.assertLess(check, push)

    def test_every_logged_file_is_verified_daily_and_a_failure_reaches_the_failed_runs_issue(self):
        step = self._step("Verify every logged file")
        self.assertIn("id: integrity", step)
        self.assertIn("if: always()", step)
        self.assertIn("live_integrity.py verify", step)
        self.assertIn('"Live record: daily digests"', step)
        failed = self._step("Open or update the failed-runs issue")
        self.assertIn("integrity=${{ steps.integrity.outcome }}", failed)
        self.assertLess(self.text.index("- name: Verify every logged file"),
                        self.text.index("- name: Open or update the failed-runs issue"))

    def test_the_workflow_writes_no_existing_path(self):
        # Only the day's file is ever staged.
        adds = re.findall(r"git add (\S+)", self.text)
        self.assertEqual(adds, ['"$file"'])


if __name__ == "__main__":
    unittest.main()
