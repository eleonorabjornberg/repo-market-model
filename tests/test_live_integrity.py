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
* **the anchor** (`AnchorTests`, Eleonora's ruling of 6 October 2026: Sigstore
  Rekor): each anchored day carries `live/<day>.rekor`; `verify` checks it
  offline (a `hashedrekord` over the file's SHA-256, a Merkle inclusion proof,
  a signing certificate naming this repository's workflow on main), and a
  missing anchor never fails it. The Rekor response is built to the shape of
  Rekor's v1 API, not fetched: this environment cannot reach it;
* **the workflow** (`WorkflowIntegrityTests`): the chain, the add-only check
  before `git push`, a daily integrity step whose failure reaches the
  failed-runs issue, and the anchor step: after the push, before the digest,
  never failing the run, with a pinned and checksummed cosign.

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

The anchor (`AnchorTests`) was written against the previous `live_integrity.py`
and failed there (`AttributeError`/`ValueError` on every test), then passed.
Mutations, each in a disposable copy under /tmp, one match confirmed by an
`assert`, each killed by the tests named:

* anchored bytes: in `verify_entry`, `if data["algorithm"] != "sha256" or
  data["value"] != sha256:` -> `if False:` makes
  `test_an_entry_over_other_bytes_is_refused` and
  `test_an_entry_that_is_not_a_hashedrekord_over_sha256_is_refused` fail with
  `AssertionError: ValueError not raised`.
* inclusion proof: `if not _inclusion_ok(index, size, leaf, hashes, root):` ->
  `if False:` makes `test_a_proof_that_does_not_rebuild_the_root_is_refused`
  fail with `AssertionError: ValueError not raised`.
* signer: `if identity != IDENTITY or issuer != OIDC_ISSUER:` -> `if False:`
  makes `test_another_signer_is_refused`,
  `test_another_oidc_issuer_is_refused` and
  `test_the_anchor_is_found_among_other_entries_and_only_the_workflows_counts`
  fail with `AssertionError: ValueError not raised`.
* anchor file against its record: in `require_anchor`, `if anchor.get("date")
  != day.isoformat() or anchor.get("sha256") != record_sha256:` -> `if False:`
  makes `test_an_anchor_file_that_misstates_its_day_or_digest_is_refused` fail
  with `AssertionError: ValueError not raised`; `if (anchor.get("uuid"),
  anchor.get("log_index")) != (found["uuid"], found["log_index"]):` ->
  `if False:` makes
  `test_an_anchor_file_whose_uuid_or_index_differs_from_its_entry_is_refused`
  fail the same way.
* anchor after its record: in `require_add_only_commit`, `if parent ==
  EMPTY_TREE or subprocess.run(` -> `if False and subprocess.run(` makes
  `test_an_anchor_for_a_day_with_no_record_is_refused` fail with
  `AssertionError: 'does not yet hold' not found in ...` (`verify`'s second check
  still refuses the log, with another message, so only the commit-level guard is
  killed here).
* proof placed by its own index (#328): re-adding `if index != int(entry["logIndex"]):
  raise ValueError(...)` before the leaf is hashed in `verify_entry` makes
  `test_a_sharded_entry_whose_global_index_is_not_its_proofs_tree_index_anchors_the_digest`
  error with `ValueError`, as the 2026-10-05 anchor did (and
  `test_a_proof_for_another_leaf_position_is_still_refused` fail with `AssertionError`).
* a bad entry skipped, not fatal (#328): in `write_anchor`, `problems.append(str(error))` +
  `continue` -> `raise` makes
  `test_an_older_entry_for_the_same_bytes_does_not_stop_the_new_one_anchoring_the_day`
  and `test_the_anchor_is_found_among_other_entries_and_only_the_workflows_counts`
  error with `ValueError`.
* anchoring a committed record only: in `write_anchor`, `if (day, rel) not in
  logged_files(repo):` -> `if False:` makes
  `test_the_anchor_file_is_never_replaced_and_needs_a_committed_record` error
  with `FileNotFoundError`.
"""

from __future__ import annotations

import hashlib
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

#: A manifest registering the fixtures' `pinned_sha` (#255): the scorer refuses any other.
FIXTURE_MANIFEST = {
    "version": 1,
    "current": "0" * 40,
    "transitions": [{"id": "t0", "sha": "0" * 40, "record": "docs/decisions/live-pin.md"}],
}

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


def write_day(repo: Path, day: str, *, chained=True, pinned_sha="0" * 40) -> Path:
    """Write a day's record as the pinned code does, then chain it as the workflow does."""

    path = repo / "live" / f"{day}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(live.record_bytes(_record(day, pinned_sha)))
    if chained:
        integrity.add_chain(repo, date.fromisoformat(day))
    return path


def commit_day(repo: Path, day: str, *, env=None) -> str:
    git(repo, "add", f"live/{day}.json", env=env)
    git(repo, "commit", "--quiet", "-m", f"Live record for {day}", env=env)
    return git(repo, "rev-parse", "HEAD")


def build_log(tmp, days=("2026-10-05", "2026-10-06", "2026-10-07"), unchained=("2026-10-05",), pinned_sha="0" * 40):
    """A live-log with the first day unchained, as on the real branch, and its digests."""

    repo = new_log(tmp)
    for day in days:
        write_day(repo, day, chained=day not in unchained, pinned_sha=pinned_sha)
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
            records = score.load_records(repo, save(comments, tmp), FIXTURE_MANIFEST)
            self.assertEqual([r["decision_day"] for r in records], ["2026-10-05", "2026-10-06", "2026-10-07"])

    def test_a_tampered_log_is_refused_before_anything_is_scored(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            comments = [c for c in comments if not c["body"].startswith("2026-10-06")]
            with self.assertRaises(ValueError):
                score.load_records(repo, save(comments, tmp), FIXTURE_MANIFEST)

    def test_no_digests_no_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = build_log(tmp)
            with self.assertRaises(ValueError):
                score.load_records(repo, None, FIXTURE_MANIFEST)

    def test_the_script_refuses_a_tampered_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            comments = [c for c in comments if not c["body"].startswith("2026-10-06")]
            out = Path(tmp) / "out.json"
            with self.assertRaisesRegex(ValueError, "digest"):
                score.main(
                    ["--date", "2027-10-01", "--live-dir", str(repo), "--digests",
                     str(save(comments, tmp)), "--panel", str(Path(tmp) / "missing.csv"),
                     "--archive-dir", str(Path(tmp) / "no-archive"), "--output", str(out)]
                )
            self.assertFalse(out.exists())


# ---- the Rekor anchor ------------------------------------------------------
# A synthetic Rekor response, built to the shape of Rekor's v1 API: this
# environment cannot reach rekor.sigstore.dev. It exercises our checks, not
# Sigstore's: the certificate is a bare DER structure, not one Fulcio signed.

def _der(tag, content: bytes) -> bytes:
    n = len(content)
    head = bytes([n]) if n < 0x80 else bytes([0x82]) + n.to_bytes(2, "big")
    return bytes([tag]) + head + content


def _oid(dotted: str) -> bytes:
    nums = [int(p) for p in dotted.split(".")]
    out = bytearray([nums[0] * 40 + nums[1]])
    for num in nums[2:]:
        chunk = [num & 0x7F]
        num >>= 7
        while num:
            chunk.append(0x80 | (num & 0x7F))
            num >>= 7
        out += bytes(reversed(chunk))
    return _der(0x06, bytes(out))


ISSUER_V1 = "1.3.6.1.4.1.57264.1.1"  # deprecated: the raw string
ISSUER_V2 = "1.3.6.1.4.1.57264.1.8"  # current: a DER UTF8String (tag 0x0c, length, string)


def fake_certificate(identity=None, issuer=None, uris=1, issuer_oid=ISSUER_V2) -> str:
    identity = identity or integrity.IDENTITY
    issuer = issuer or integrity.OIDC_ISSUER
    issuer_value = issuer.encode() if issuer_oid == ISSUER_V1 else _der(0x0C, issuer.encode())
    names = b"".join(_der(0x86, identity.encode()) for _ in range(uris))
    san = _der(0x30, _oid("2.5.29.17") + _der(0x04, _der(0x30, names)))
    iss = _der(0x30, _oid(issuer_oid) + _der(0x04, issuer_value))
    tbs = _der(0x30, _der(0xA0, _der(0x02, b"\x02")) + _der(0x02, b"\x01") + _der(0x30, b"")
               + _der(0x30, b"") + _der(0x30, b"") + _der(0x30, b"") + _der(0x30, b"")
               + _der(0xA3, _der(0x30, san + iss)))
    der = _der(0x30, tbs + _der(0x30, b"") + _der(0x03, b"\x00"))
    b64 = __import__("base64").b64encode(der).decode()
    return "-----BEGIN CERTIFICATE-----\n" + b64 + "\n-----END CERTIFICATE-----\n"


def _h(data: bytes) -> bytes:
    return __import__("hashlib").sha256(data).digest()


def _mth(leaves):
    if len(leaves) == 1:
        return leaves[0]
    k = 1
    while k * 2 < len(leaves):
        k *= 2
    return _h(b"\x01" + _mth(leaves[:k]) + _mth(leaves[k:]))


def _path(m, leaves):
    if len(leaves) == 1:
        return []
    k = 1
    while k * 2 < len(leaves):
        k *= 2
    if m < k:
        return _path(m, leaves[:k]) + [_mth(leaves[k:])]
    return _path(m - k, leaves[k:]) + [_mth(leaves[:k])]


def rekor_response(sha256, *, identity=None, issuer=None, algorithm="sha256", value=None, uris=1,
                   size=7, index=3, kind="hashedrekord", offset=0, issuer_oid=ISSUER_V2):
    """A Rekor v1 `{uuid: entry}` response for `sha256`, with a real Merkle inclusion proof.

    `offset` is the sharded log's: the entry's `logIndex` is global, the proof's is the active tree's.
    """

    import base64
    body = {
        "apiVersion": "0.0.1", "kind": kind,
        "spec": {
            "data": {"hash": {"algorithm": algorithm, "value": value or sha256}},
            "signature": {"content": "MEUCIQ==", "publicKey": {"content": base64.b64encode(
                fake_certificate(identity, issuer, uris, issuer_oid).encode()).decode()}},
        },
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    leaves = [_h(b"\x00" + bytes([i]) * 8) for i in range(size)]
    leaves[index] = _h(b"\x00" + raw)
    return {"24296fb24b8ad77a" + leaves[index].hex(): {
        "body": base64.b64encode(raw).decode(), "integratedTime": 1790000000,
        "logID": "c0d23d6a" * 8, "logIndex": index + offset,
        "verification": {"inclusionProof": {
            "logIndex": index, "treeSize": size, "rootHash": _mth(leaves).hex(),
            "hashes": [h.hex() for h in _path(index, leaves)]}},
    }}


class AnchorTests(unittest.TestCase):
    """Eleonora's ruling of 6 October 2026 (#254, Do 4): the daily digest is anchored in Sigstore Rekor.

    The Rekor response is a recorded-shape fixture, not a live fetch; the online path
    is `integrity.ONLINE_COMMAND`.
    """

    def setUp(self):
        self.sha = "ab" * 32

    def test_a_well_formed_entry_anchors_the_digest(self):
        found = integrity.verify_entry(rekor_response(self.sha, index=0, size=1), self.sha)
        self.assertEqual(found["identity"], integrity.IDENTITY)
        self.assertEqual(found["log_index"], 0)

    def test_proofs_hold_at_every_position_of_trees_of_several_sizes(self):
        for size in (1, 2, 3, 5, 7, 8):
            for index in range(size):
                with self.subTest(size=size, index=index):
                    integrity.verify_entry(rekor_response(self.sha, size=size, index=index), self.sha)

    def test_an_entry_over_other_bytes_is_refused(self):
        with self.assertRaises(ValueError):
            integrity.verify_entry(rekor_response(self.sha, value="cd" * 32), self.sha)

    def test_an_entry_that_is_not_a_hashedrekord_over_sha256_is_refused(self):
        for kwargs in ({"kind": "intoto"}, {"algorithm": "sha512"}):
            with self.subTest(**kwargs), self.assertRaises(ValueError):
                integrity.verify_entry(rekor_response(self.sha, **kwargs), self.sha)

    def test_a_proof_that_does_not_rebuild_the_root_is_refused(self):
        response = rekor_response(self.sha)
        entry = next(iter(response.values()))
        entry["verification"]["inclusionProof"]["hashes"][0] = "00" * 32
        with self.assertRaises(ValueError) as caught:
            integrity.verify_entry(response, self.sha)
        self.assertIn("inclusion proof", str(caught.exception))

    def test_a_body_that_is_not_the_leaf_the_uuid_names_is_refused(self):
        response = rekor_response(self.sha)
        uuid, entry = next(iter(response.items()))
        self.assertTrue(integrity.verify_entry(response, self.sha))
        with self.assertRaises(ValueError):
            integrity.verify_entry({"24296fb24b8ad77a" + "11" * 32: entry}, self.sha)

    def test_another_signer_is_refused(self):
        wrong = (
            "https://github.com/someone/else/.github/workflows/live-log.yml@refs/heads/main",
            "https://github.com/eleonorabjornberg/repo-market-model/.github/workflows/live-log.yml@refs/heads/other",
            "https://github.com/eleonorabjornberg/repo-market-model/.github/workflows/tests.yml@refs/heads/main",
        )
        for identity in wrong:
            with self.subTest(identity=identity), self.assertRaises(ValueError) as caught:
                integrity.verify_entry(rekor_response(self.sha, identity=identity), self.sha)
            self.assertIn("not " + integrity.IDENTITY, str(caught.exception))

    def test_the_current_der_encoded_issuer_extension_is_accepted(self):
        """The live failure of 2026-10-05 to 07 (#371): no day anchored.

        Fulcio's current issuer extension (1.3.6.1.4.1.57264.1.8) is a DER UTF8String, and the
        parser kept its tag and length, reading `\\x0c+https://token.actions.githubusercontent.com`.
        The certificate here is constructed (rekor.sigstore.dev is unreachable from this
        environment), to the shape of the three real entries: that extension, DER-encoded, and the
        workflow identity on main. The real-world confirmation is the next live run, which must
        anchor 5, 6 and 7 October late.

        Recorded mutation: in `certificate_identity`, replacing the DER decoding of 1.8 with
        `issuer = octets.decode("utf-8", "replace")` made this test and the two below fail with
        `ValueError` (the entry "was signed by ... via \\x0c+https://token..."), the exception
        `verify_entry` and `write_anchor` raise.
        """

        response = rekor_response(self.sha)
        self.assertEqual(integrity.verify_entry(response, self.sha)["identity"], integrity.IDENTITY)
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, sha = self._anchored_log(tmp)
            path = integrity.write_anchor(repo, date(2026, 10, 7), [rekor_response(sha)])
            self.assertEqual(json.loads(path.read_text())["identity"], integrity.IDENTITY)

    def test_the_der_encoded_issuer_is_compared_after_decoding(self):
        for issuer in ("https://accounts.google.com", integrity.OIDC_ISSUER + "x"):
            with self.subTest(issuer=issuer), self.assertRaises(ValueError):
                integrity.verify_entry(rekor_response(self.sha, issuer=issuer), self.sha)
        with self.assertRaises(ValueError):
            integrity.verify_entry(rekor_response(self.sha, identity=integrity.IDENTITY + "x"), self.sha)

    def test_the_raw_legacy_issuer_extension_is_still_accepted_and_still_checked(self):
        found = integrity.verify_entry(rekor_response(self.sha, issuer_oid=ISSUER_V1), self.sha)
        self.assertEqual(found["identity"], integrity.IDENTITY)
        with self.assertRaises(ValueError):
            integrity.verify_entry(
                rekor_response(self.sha, issuer="https://accounts.google.com", issuer_oid=ISSUER_V1), self.sha)

    def test_a_der_issuer_that_is_not_one_utf8string_is_refused(self):
        for bad in (b"\x04\x05abcde", b"\x0c\x7fshort", b"\x0c\x01ab", integrity.OIDC_ISSUER.encode()):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                integrity._der_utf8(bad)

    def test_another_oidc_issuer_is_refused(self):
        with self.assertRaises(ValueError):
            integrity.verify_entry(rekor_response(self.sha, issuer="https://accounts.google.com"), self.sha)

    def test_a_certificate_without_exactly_one_identity_is_refused(self):
        for uris in (0, 2):
            with self.subTest(uris=uris), self.assertRaises(ValueError):
                integrity.verify_entry(rekor_response(self.sha, uris=uris), self.sha)

    def test_a_malformed_response_is_refused(self):
        for bad in ({}, {"a": 1}, {"a": {}, "b": {}}, [], {"x" * 80: {"body": "!!"}}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                integrity.verify_entry(bad, self.sha)

    def _anchored_log(self, tmp, **kwargs):
        repo, comments = build_log(tmp)
        sha = integrity.file_sha256(repo / "live" / "2026-10-07.json")
        return repo, comments, sha

    def _commit_anchor(self, repo, day, response):
        path = integrity.write_anchor(repo, date.fromisoformat(day), [response])
        git(repo, "add", f"live/{day}.rekor")
        git(repo, "commit", "--quiet", "-m", f"Rekor anchor for {day}")
        return path

    def _commit_forged_anchor(self, repo, day, sha, field, value):
        """An anchor file, added as the bot in its own commit, with one field changed after writing."""

        path = integrity.write_anchor(repo, date.fromisoformat(day), [rekor_response(sha)])
        anchor = json.loads(path.read_text())
        anchor[field] = value
        path.write_text(json.dumps(anchor))
        git(repo, "add", f"live/{day}.rekor")
        git(repo, "commit", "--quiet", "-m", "forged anchor")

    def test_an_anchored_log_verifies_and_the_anchor_is_not_a_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments, sha = self._anchored_log(tmp)
            self._commit_anchor(repo, "2026-10-07", rekor_response(sha))
            days = integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))
            self.assertEqual([d.isoformat() for d in days], ["2026-10-05", "2026-10-06", "2026-10-07"])
            self.assertEqual([d.isoformat() for d in integrity.unanchored(repo)], ["2026-10-05", "2026-10-06"])
            self.assertEqual(sorted(p.name for p in (repo / "live").glob("*.json")),
                             ["2026-10-05.json", "2026-10-06.json", "2026-10-07.json"])

    def test_a_missing_anchor_never_fails_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments, _ = self._anchored_log(tmp)
            integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))
            self.assertEqual(len(integrity.unanchored(repo)), 3)

    def test_a_later_run_anchors_a_day_it_missed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments, _ = self._anchored_log(tmp)
            sha = integrity.file_sha256(repo / "live" / "2026-10-06.json")
            self._commit_anchor(repo, "2026-10-06", rekor_response(sha))
            self.assertEqual([d.isoformat() for d in integrity.unanchored(repo)], ["2026-10-05", "2026-10-07"])

    def test_the_anchor_is_found_among_other_entries_and_only_the_workflows_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, sha = self._anchored_log(tmp)
            foreign = rekor_response(sha, identity="https://github.com/someone/else/x.yml@refs/heads/main")
            path = integrity.write_anchor(repo, date(2026, 10, 7), [foreign, rekor_response(sha)])
            self.assertEqual(json.loads(path.read_text())["identity"], integrity.IDENTITY)
            with self.assertRaises(ValueError):
                integrity.write_anchor(repo, date(2026, 10, 6), [foreign])

    def test_a_sharded_entry_whose_global_index_is_not_its_proofs_tree_index_anchors_the_digest(self):
        # The live failure of 2026-10-05 (#328): the entry's logIndex was 3116266281 and its
        # inclusion proof's 2994362019, the proof being relative to the active shard's tree.
        found = integrity.verify_entry(rekor_response(self.sha, offset=121903000), self.sha)
        self.assertEqual(found["log_index"], 3 + 121903000)

    def test_a_proof_for_another_leaf_position_is_still_refused(self):
        response = rekor_response(self.sha, index=3, size=7)
        next(iter(response.values()))["verification"]["inclusionProof"]["logIndex"] = 2
        with self.assertRaises(ValueError) as caught:
            integrity.verify_entry(response, self.sha)
        self.assertIn("inclusion proof", str(caught.exception))

    def test_an_older_entry_for_the_same_bytes_does_not_stop_the_new_one_anchoring_the_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, sha = self._anchored_log(tmp)
            older = rekor_response(sha, index=2, size=7)
            next(iter(older.values()))["verification"]["inclusionProof"]["hashes"][0] = "00" * 32
            newer = rekor_response(sha, index=4, size=9, offset=121903000)
            path = integrity.write_anchor(repo, date(2026, 10, 7), [older, newer])
            self.assertEqual(json.loads(path.read_text())["log_index"], 4 + 121903000)
            other = integrity.file_sha256(repo / "live" / "2026-10-06.json")
            path = integrity.write_anchor(repo, date(2026, 10, 6),
                                          [rekor_response(other, index=4, size=9, offset=121903000), older])
            self.assertEqual(json.loads(path.read_text())["log_index"], 4 + 121903000)

    def test_the_anchor_file_is_never_replaced_and_needs_a_committed_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, sha = self._anchored_log(tmp)
            self._commit_anchor(repo, "2026-10-07", rekor_response(sha))
            with self.assertRaises(ValueError):
                integrity.write_anchor(repo, date(2026, 10, 7), [rekor_response(sha)])
            with self.assertRaises(ValueError):
                integrity.write_anchor(repo, date(2026, 10, 9), [rekor_response(sha)])

    def test_an_anchor_for_other_bytes_than_the_record_is_refused_by_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments, sha = self._anchored_log(tmp)
            self._commit_anchor(repo, "2026-10-07", rekor_response(sha))
            path = repo / "live" / "2026-10-07.rekor"
            anchor = json.loads(path.read_text())
            anchor["entry"] = rekor_response("cd" * 32)
            anchor["sha256"] = "cd" * 32
            path.write_text(json.dumps(anchor))
            git(repo, "add", "-A")
            git(repo, "commit", "--quiet", "-m", "tamper")
            with self.assertRaises(ValueError):
                integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))

    def test_an_anchor_file_that_misstates_its_day_or_digest_is_refused(self):
        for field, value in (("sha256", "cd" * 32), ("date", "2026-10-06")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                repo, comments, sha = self._anchored_log(tmp)
                self._commit_forged_anchor(repo, "2026-10-07", sha, field, value)
                with self.assertRaises(ValueError):
                    integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))

    def test_an_anchor_file_whose_uuid_or_index_differs_from_its_entry_is_refused(self):
        for field, value in (("uuid", "f" * 80), ("log_index", 99)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                repo, comments, sha = self._anchored_log(tmp)
                self._commit_forged_anchor(repo, "2026-10-07", sha, field, value)
                with self.assertRaises(ValueError):
                    integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))

    def test_an_anchor_commit_that_is_not_add_only_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments, sha = self._anchored_log(tmp)
            self._commit_anchor(repo, "2026-10-07", rekor_response(sha))
            (repo / "live" / "2026-10-07.rekor").write_text("{}")
            git(repo, "commit", "--quiet", "-am", "edit the anchor")
            with self.assertRaises(ValueError):
                integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))

    def test_an_anchor_for_a_day_with_no_record_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments, sha = self._anchored_log(tmp)
            (repo / "live" / "2026-10-09.rekor").write_text("{}")
            git(repo, "add", "-A")
            git(repo, "commit", "--quiet", "-m", "anchor with no record")
            with self.assertRaises(ValueError) as caught:
                integrity.verify(repo, integrity.parse_digests(save(comments, tmp)))
            self.assertIn("does not yet hold", str(caught.exception))

    def test_the_anchor_commit_is_checked_add_only_before_it_is_pushed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, sha = self._anchored_log(tmp)
            base = git(repo, "rev-parse", "HEAD")
            self._commit_anchor(repo, "2026-10-07", rekor_response(sha))
            integrity.require_append_only(repo, base, date(2026, 10, 7), anchor=True)
            with self.assertRaises(ValueError):
                integrity.require_append_only(repo, base, date(2026, 10, 7))
            with self.assertRaises(ValueError):
                integrity.require_append_only(repo, base, date(2026, 10, 6), anchor=True)

    def test_the_command_line_writes_the_anchor_and_lists_unanchored_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, sha = self._anchored_log(tmp)
            entries = Path(tmp) / "entries.json"
            entries.write_text(json.dumps([rekor_response(sha)]))
            script = str(ROOT / "scripts" / "live_integrity.py")
            run = lambda *a: subprocess.run(["python3", "-B", script, *a], capture_output=True, text=True)
            done = run("anchor-file", "--live-dir", str(repo), "--date", "2026-10-07", "--entries", str(entries))
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(json.loads(done.stdout)["log_index"], 3)
            git(repo, "add", "-A")
            git(repo, "commit", "--quiet", "-m", "anchor")
            done = run("unanchored", "--live-dir", str(repo))
            self.assertEqual(json.loads(done.stdout), {"unanchored": ["2026-10-05", "2026-10-06"]})
            done = run("check-append", "--live-dir", str(repo), "--date", "2026-10-07",
                       "--base", git(repo, "rev-parse", "HEAD~1"), "--anchor")
            self.assertEqual(done.returncode, 0, done.stderr)



class PanelTests(unittest.TestCase):
    """The day's panel is committed beside its record (#275).

    `live/<day>.panel.csv` is added in the record's own commit. The record's
    `inputs.panel_sha256` names its bytes, so the record's digest on #225 and
    its Rekor anchor cover the panel through that field.

    Recorded mutations (each applied, `PanelTests` run, then reverted):

    * `verify`'s `if file_sha256(repo / rel) != named:` replaced by `if False:`:
      `test_a_panel_that_is_not_the_one_the_record_names_is_refused` raised
      `AssertionError: ValueError not raised`.
    * `require_add_only_commit`'s `elif require_panel:` replaced by `elif False:`:
      `test_a_record_commit_without_its_panel_is_refused_when_the_panel_is_required` and
      `test_the_command_line_requires_the_panel_with_a_flag` raised
      `AssertionError: ValueError not raised`.
    """

    PANEL = b"date,spread_bps\n2026-10-05,1.0\n2026-10-06,2.0\n"

    def _commit(self, repo, day, panel=PANEL, *, sha=None, with_panel=True):
        record = _record(day)
        record["inputs"]["panel_sha256"] = sha or hashlib.sha256(panel).hexdigest()
        path = repo / "live" / f"{day}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(live.record_bytes(record))
        integrity.add_chain(repo, date.fromisoformat(day))
        git(repo, "add", f"live/{day}.json")
        if with_panel:
            (repo / "live" / f"{day}.panel.csv").write_bytes(panel)
            git(repo, "add", f"live/{day}.panel.csv")
        git(repo, "commit", "--quiet", "-m", f"Live record for {day}")
        return git(repo, "rev-parse", "HEAD")

    def _verify(self, repo, tmp):
        return integrity.verify(repo, integrity.parse_digests(save(digests_of(repo), tmp)))

    def test_a_record_and_its_panel_added_together_pass_and_the_log_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            base = self._commit(repo, "2026-10-05")
            self._commit(repo, "2026-10-06")
            integrity.require_append_only(repo, base, date(2026, 10, 6), panel=True)
            days = self._verify(repo, tmp)
            self.assertEqual([d.isoformat() for d in days], ["2026-10-05", "2026-10-06"])
            self.assertEqual(integrity.unanchored(repo), days)

    def test_a_record_commit_without_its_panel_is_refused_when_the_panel_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            self._commit(repo, "2026-10-06", with_panel=False)
            integrity.require_append_only(repo, None, date(2026, 10, 6))
            with self.assertRaisesRegex(ValueError, "panel"):
                integrity.require_append_only(repo, None, date(2026, 10, 6), panel=True)

    def test_a_panel_that_is_not_the_one_the_record_names_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            self._commit(repo, "2026-10-06", sha="f" * 64)
            with self.assertRaisesRegex(ValueError, "panel"):
                self._verify(repo, tmp)

    def test_a_panel_replaced_in_a_later_commit_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            self._commit(repo, "2026-10-06")
            (repo / "live" / "2026-10-06.panel.csv").write_bytes(self.PANEL + b"2026-10-07,3.0\n")
            git(repo, "add", "live/2026-10-06.panel.csv")
            git(repo, "commit", "--quiet", "-m", "edit")
            with self.assertRaises(ValueError):
                self._verify(repo, tmp)

    def test_a_panel_for_another_day_or_alone_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            self._commit(repo, "2026-10-06")
            (repo / "live" / "2026-10-07.panel.csv").write_bytes(self.PANEL)
            git(repo, "add", "live/2026-10-07.panel.csv")
            git(repo, "commit", "--quiet", "-m", "orphan panel")
            with self.assertRaises(ValueError):
                self._verify(repo, tmp)
            with self.assertRaises(ValueError):
                integrity.require_append_only(repo, git(repo, "rev-parse", "HEAD~1"), date(2026, 10, 7))

    def test_the_command_line_requires_the_panel_with_a_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_log(tmp)
            self._commit(repo, "2026-10-06", with_panel=False)
            argv = ["check-append", "--live-dir", str(repo), "--date", "2026-10-06", "--base", "none"]
            self.assertEqual(integrity.main(argv), 0)
            with self.assertRaises(ValueError):
                integrity.main(argv + ["--panel"])


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
        self.assertIn("$DIGEST_ISSUE", step)
        failed = self._step("Open or update the failed-runs issue")
        self.assertIn("integrity=${{ steps.integrity.outcome }}", failed)
        self.assertLess(self.text.index("- name: Verify every logged file"),
                        self.text.index("- name: Open or update the failed-runs issue"))

    def test_the_workflow_writes_no_existing_path(self):
        # Only the day's record and its panel (one commit) and its anchor (another) are ever staged.
        # `"raw/$DAY"` is staged in a different clone, of the `live-raw` branch (#257).
        adds = re.findall(r'git add ("[^"]*"(?: "[^"]*")*)', self.text)
        self.assertEqual(adds, ['"$file" "$panel"', '"raw/$DAY"', '"live/$day.rekor"'])

    def test_the_days_panel_is_copied_beside_its_record_and_required_by_the_append_check(self):
        step = self._step("Append it to live-log")
        self.assertIn('panel="live/$DAY.panel.csv"', step)
        self.assertIn('cp ../work/panel.csv "$panel"', step)
        self.assertLess(step.index("cp ../work/panel.csv"), step.index("git add"))
        self.assertRegex(step, r"check-append[^\n]*--panel")

    def test_the_anchor_follows_the_push_and_precedes_the_digest_and_never_fails_the_run(self):
        step = self._step("Anchor the digests in Sigstore Rekor")
        self.assertIn("id: anchor", step)
        self.assertIn("continue-on-error: true", step)
        self.assertIn("cosign sign-blob --yes", step)
        self.assertIn("live_integrity.py unanchored", step)
        self.assertLess(step.index("sha256sum -c"), step.index("sign-blob"))
        self.assertLess(step.index("commit --quiet"), step.index("check-append"))
        self.assertLess(step.index("check-append"), step.index("git push"))
        self.assertIn("--anchor", step)
        names = [m.group(1) for m in re.finditer(r"\n      - name: (.*)", self.text)]
        self.assertLess(names.index("Append it to live-log"), names.index("Anchor the digests in Sigstore Rekor"))
        self.assertLess(names.index("Anchor the digests in Sigstore Rekor"), names.index("Post the digest outside the repository"))

    def test_a_day_that_fails_to_anchor_does_not_stop_the_later_days(self):
        step = self._step("Anchor the digests in Sigstore Rekor")
        self.assertIn("anchor_day()", step)
        self.assertRegex(step, r'if ! anchor_day "\$day"; then')
        failed = step[step.index('if ! anchor_day "$day"; then'):]
        self.assertIn('git reset --quiet --hard "$start"', failed)
        self.assertLess(failed.index("git reset"), failed.index("done"))
        self.assertRegex(step, r'\[ -z "\$failed" \]')

    def test_the_anchor_step_leaves_nothing_untracked_in_live_log(self):
        """The late-anchor note is written outside the live-log checkout (#437).

        Run 37851656637 anchored 5, 6 and 7 October late. The step runs inside
        `live-log/` and wrote `late.md` there, then read `../late.md`: the note
        was never posted and the untracked file made `verify` refuse the clean
        checkout ("live-log has uncommitted changes"), failing a sound record.
        Recorded mutation: `} > ../late.md` back to `} > late.md` made this
        test fail with AssertionError.
        """

        step = self._step("Anchor the digests in Sigstore Rekor")
        self.assertIn("} > ../late.md", step)
        self.assertNotRegex(step, r"> late\.md")
        self.assertIn("-F body=@../late.md", step)

    def test_cosign_is_a_pinned_release_checked_against_its_sha256(self):
        step = self._step("Anchor the digests in Sigstore Rekor")
        self.assertRegex(step, r"COSIGN_VERSION: v\d+\.\d+\.\d+")
        self.assertRegex(step, r"COSIGN_SHA256: [0-9a-f]{64}")
        self.assertIn("releases/download/${COSIGN_VERSION}/cosign-linux-amd64", step)

    def test_an_anchor_failure_goes_to_the_failed_runs_issue_and_the_digest_carries_the_log_index(self):
        failed = self._step("Report an anchor that failed")
        self.assertIn("steps.anchor.outcome == 'failure'", failed)
        self.assertIn("$FAILED_RUNS_ISSUE", failed)
        digest = self._step("Post the digest outside the repository")
        self.assertIn("Rekor log index", digest)
        self.assertIn("Rekor entry", digest)
        # A failed anchor leaves the digest step to run: the record is still written.
        self.assertNotIn("steps.anchor", digest)


if __name__ == "__main__":
    unittest.main()
