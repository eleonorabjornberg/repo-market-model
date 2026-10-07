"""The live record's raw inputs are archived, and an outcome panel is built only from archived bytes (#257).

An independent review (6 October 2026) found the evidence path was not reproducible
end to end: the live records keep only each input's URL, retrieval time and digest
(`REPRODUCIBILITY.md` says a later download may differ), nothing archived the bytes,
`--panel` could name arbitrary bytes, and the scoring result kept neither the panel's
digest nor its sources'. `scripts/live_raw.py` archives each day's raw root, content
addressed by the digests the record already carries, on an append-only branch of its
own (`live-raw`); builds the outcome panel from that archive only; and gives the scorer
the check that refuses a panel that is not one of those.

What is held here:

* **the archive** (`ArchiveTests`): every file's bytes must equal the digest its
  manifest records; a day is archived once; an unlisted or altered file fails
  `verify_archive`;
* **the add-only branch** (`AppendOnlyTests`): a day's commit adds files under
  `raw/<day>/` as the bot, and changes, deletes and adds nothing else;
* **the record's inputs** (`RecordInputTests`): every snapshot digest a record carries is in
  that day's archive; a day with no archive is listed, never counted as checked;
* **the workflows** (`WorkflowTests`): the daily run archives the raw root after the record, never
  blocking it; the scoring workflow is started by hand, never overrides the clock, verifies the
  log and the archive, builds the panel from the archive and only then scores, and archives the
  blind gap's inputs before it reconstructs from them;
* **the outcome panel** (`PanelTests`): it is rebuilt from the archive alone, and the scorer
  refuses a panel with no build manifest, one whose bytes differ from its manifest's, one
  with no provenance sidecar, and one built from a digest the archive does not hold. The
  published panel's own fixtures round-trip: archive, restore, build, same digest.

Recorded mutations (#257), each applied in a disposable copy under /tmp with the mutated
line confirmed by grep, each killed by the test named (the exception is what the failing test raised):

* archived bytes: in `live_raw.archive_day`, `if digest != manifest["sha256"]:` ->
  `if False:` makes `test_bytes_that_differ_from_their_manifests_digest_are_refused` fail
  with `AssertionError: ValueError not raised`.
* add-only: in `live_raw.require_add_only`, the line `if not changes or any(status != "A" or not
  path.startswith(prefix) for status, path in changes):` -> `if False:` makes
  `test_a_commit_that_changes_an_archived_file_is_refused` and `test_each_other_change_is_refused`
  fail with `AssertionError: ValueError not raised`.
* registered panel: in `live_raw.require_registered_panel`, `if digest not in archived:` ->
  `if False:` makes `test_a_panel_built_from_bytes_the_archive_does_not_hold_is_refused`
  fail with `AssertionError: ValueError not raised`.
* panel bytes: in `live_raw.require_registered_panel`, `verify_daily_panel(panel, manifest_path)`
  -> `pass` makes `test_a_panel_whose_bytes_differ_from_its_manifest_is_refused` fail with
  `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"

BOT = {
    "GIT_AUTHOR_NAME": "github-actions[bot]",
    "GIT_AUTHOR_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "github-actions[bot]",
    "GIT_COMMITTER_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
}
SOMEONE = {**BOT, "GIT_AUTHOR_NAME": "someone", "GIT_AUTHOR_EMAIL": "someone@example.com",
           "GIT_COMMITTER_NAME": "someone", "GIT_COMMITTER_EMAIL": "someone@example.com"}


def _load():
    spec = importlib.util.spec_from_file_location("live_raw_test", ROOT / "scripts" / "live_raw.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


raw = _load()


def git(repo, *argv, env=None):
    full = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", **(env or BOT)}
    return subprocess.run(["git", *argv], cwd=repo, check=True, capture_output=True, text=True,
                          env=full).stdout.strip()


def snapshot(root: Path, source: str, name: str, payload: bytes, *, retrieved="2026-10-06T21:31:00+00:00"):
    """A snapshot as `ingest._save_snapshot` lays it out: the file, and `<file>.manifest.json`."""

    path = root / source / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    manifest = {
        "byte_count": len(payload), "path": f"{source}/{name}", "retrieved_at": retrieved,
        "sha256": hashlib.sha256(payload).hexdigest(), "source_id": source,
        "url": f"https://example.invalid/{source}",
    }
    path.with_suffix(path.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def raw_root(tmp, payload=b"a,b\n1,2\n") -> Path:
    root = Path(tmp) / "raw"
    snapshot(root, "nyfed-sofr-rate", "20261006T213100Z_aaaaaaaaaaaa.json", payload)
    snapshot(root, "fred-macro", "20261006T213101Z_bbbbbbbbbbbb.zip", b"PK-zip-bytes")
    return root


def new_branch(tmp) -> Path:
    repo = Path(tmp) / "live-raw"
    repo.mkdir()
    git(repo, "init", "--quiet", "-b", "live-raw")
    return repo


def commit(repo: Path, message: str, env=None) -> str:
    git(repo, "add", "-A", env=env)
    git(repo, "commit", "--quiet", "-m", message, env=env)
    return git(repo, "rev-parse", "HEAD")


class ArchiveTests(unittest.TestCase):
    def test_a_days_raw_root_is_archived_with_an_index_of_its_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = raw_root(tmp)
            out = Path(tmp) / "archive"
            raw.archive_day(root, out, date(2026, 10, 6))
            index = json.loads((out / "raw" / "2026-10-06" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual([entry["path"] for entry in index["files"]],
                             ["fred-macro/20261006T213101Z_bbbbbbbbbbbb.zip",
                              "nyfed-sofr-rate/20261006T213100Z_aaaaaaaaaaaa.json"])
            for entry in index["files"]:
                data = (out / "raw" / "2026-10-06" / entry["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
                self.assertEqual(len(data), entry["byte_count"])
            self.assertEqual(raw.verify_archive(out), ["2026-10-06"])

    def test_bytes_that_differ_from_their_manifests_digest_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = raw_root(tmp)
            (root / "nyfed-sofr-rate" / "20261006T213100Z_aaaaaaaaaaaa.json").write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                raw.archive_day(root, Path(tmp) / "archive", date(2026, 10, 6))
            self.assertFalse((Path(tmp) / "archive" / "raw").exists())

    def test_a_day_is_archived_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = raw_root(tmp)
            out = Path(tmp) / "archive"
            raw.archive_day(root, out, date(2026, 10, 6))
            with self.assertRaises(ValueError):
                raw.archive_day(root, out, date(2026, 10, 6))

    def test_an_empty_raw_root_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                raw.archive_day(Path(tmp) / "nothing", Path(tmp) / "archive", date(2026, 10, 6))

    def test_an_altered_or_unlisted_file_fails_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "archive"
            raw.archive_day(raw_root(tmp), out, date(2026, 10, 6))
            target = out / "raw" / "2026-10-06" / "fred-macro" / "20261006T213101Z_bbbbbbbbbbbb.zip"
            target.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                raw.verify_archive(out)
            target.write_bytes(b"PK-zip-bytes")
            raw.verify_archive(out)
            (out / "raw" / "2026-10-06" / "extra.txt").write_text("x")
            with self.assertRaises(ValueError):
                raw.verify_archive(out)

    def test_a_restored_root_is_the_archived_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = raw_root(tmp)
            out = Path(tmp) / "archive"
            raw.archive_day(root, out, date(2026, 10, 6))
            restored = Path(tmp) / "restored"
            raw.restore_day(out, date(2026, 10, 6), restored)
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    self.assertEqual((restored / path.relative_to(root)).read_bytes(), path.read_bytes())

    def test_restoring_a_day_that_was_not_archived_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "archive"
            raw.archive_day(raw_root(tmp), out, date(2026, 10, 6))
            with self.assertRaises(ValueError):
                raw.restore_day(out, date(2026, 10, 7), Path(tmp) / "restored")

    def test_a_second_root_of_a_day_is_archived_under_its_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "archive"
            raw.archive_day(raw_root(Path(tmp) / "a"), out, date(2027, 4, 1))
            raw.archive_day(raw_root(Path(tmp) / "b", payload=b"gap"), out, date(2027, 4, 1), "gap")
            self.assertEqual(raw.verify_archive(out), ["2027-04-01", "2027-04-01-gap"])
            restored = Path(tmp) / "restored"
            raw.restore_day(out, date(2027, 4, 1), restored, "gap")
            self.assertEqual((restored / "nyfed-sofr-rate" / "20261006T213100Z_aaaaaaaaaaaa.json").read_bytes(),
                             b"gap")
            with self.assertRaises(ValueError):
                raw.archive_day(raw_root(Path(tmp) / "c"), out, date(2027, 4, 1), "gap")


class AppendOnlyTests(unittest.TestCase):
    def archive(self, tmp, repo, day, env=None):
        root = Path(tmp) / f"raw-{day}"
        raw_root_for = raw_root(Path(tmp) / f"w-{day}")
        raw.archive_day(raw_root_for, repo, date.fromisoformat(day))
        return commit(repo, f"Raw inputs for {day}", env=env)

    def test_a_commit_that_only_adds_the_days_directory_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_branch(tmp)
            self.archive(tmp, repo, "2026-10-06")
            base = git(repo, "rev-parse", "HEAD")
            self.archive(tmp, repo, "2026-10-07")
            raw.require_add_only(repo, base, date(2026, 10, 7))

    def test_the_first_commit_of_a_new_branch_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_branch(tmp)
            self.archive(tmp, repo, "2026-10-06")
            raw.require_add_only(repo, None, date(2026, 10, 6))

    def test_a_commit_that_changes_an_archived_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_branch(tmp)
            self.archive(tmp, repo, "2026-10-06")
            base = git(repo, "rev-parse", "HEAD")
            (repo / "raw" / "2026-10-06" / "index.json").write_text("{}")
            commit(repo, "tamper")
            with self.assertRaises(ValueError):
                raw.require_add_only(repo, base, date(2026, 10, 6))
            with self.assertRaises(ValueError):
                raw.require_add_only(repo, base, date(2026, 10, 7))

    def test_each_other_change_is_refused(self):
        def another_day(repo, tmp):
            raw.archive_day(raw_root(Path(tmp) / "w-other"), repo, date(2026, 10, 9))

        def another_path(repo, tmp):
            (repo / "notes.txt").write_text("x")

        def deleted(repo, tmp):
            shutil.rmtree(repo / "raw" / "2026-10-06")

        for name, change in (("another day", another_day), ("another path", another_path),
                             ("a deletion", deleted)):
            with self.subTest(change=name), tempfile.TemporaryDirectory() as tmp:
                repo = new_branch(tmp)
                self.archive(tmp, repo, "2026-10-06")
                base = git(repo, "rev-parse", "HEAD")
                change(repo, tmp)
                commit(repo, "x")
                with self.assertRaises(ValueError):
                    raw.require_add_only(repo, base, date(2026, 10, 7))

    def test_a_commit_by_someone_else_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_branch(tmp)
            self.archive(tmp, repo, "2026-10-06", env=SOMEONE)
            with self.assertRaises(ValueError):
                raw.require_add_only(repo, None, date(2026, 10, 6))

    def test_two_commits_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = new_branch(tmp)
            self.archive(tmp, repo, "2026-10-06")
            base = git(repo, "rev-parse", "HEAD")
            self.archive(tmp, repo, "2026-10-07")
            (repo / "raw" / "2026-10-07" / "again.txt").write_text("x")
            commit(repo, "second")
            with self.assertRaises(ValueError):
                raw.require_add_only(repo, base, date(2026, 10, 7))


class RecordInputTests(unittest.TestCase):
    def record(self, day, manifests):
        return {"decision_day": day, "inputs": {"snapshots": [
            {"source_id": m["source_id"], "sha256": m["sha256"], "retrieved_at": m["retrieved_at"],
             "url": m["url"]} for m in manifests]}}

    def live_dir(self, tmp, records):
        live = Path(tmp) / "live-log" / "live"
        live.mkdir(parents=True)
        for record in records:
            (live / f"{record['decision_day']}.json").write_text(json.dumps(record), encoding="utf-8")
        return live.parent

    def manifests(self, root):
        return [json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(root.glob("*/*.manifest.json"))]

    def test_every_digest_a_record_carries_is_in_its_days_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = raw_root(tmp)
            out = Path(tmp) / "archive"
            raw.archive_day(root, out, date(2026, 10, 6))
            live = self.live_dir(tmp, [self.record("2026-10-06", self.manifests(root))])
            report = raw.verify_records(out, live)
        self.assertEqual(report, {"archived": ["2026-10-06"], "unarchived": []})

    def test_a_digest_the_archive_does_not_hold_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = raw_root(tmp)
            out = Path(tmp) / "archive"
            raw.archive_day(root, out, date(2026, 10, 6))
            other = raw_root(Path(tmp) / "other", payload=b"different")
            live = self.live_dir(tmp, [self.record("2026-10-06", self.manifests(other))])
            with self.assertRaises(ValueError):
                raw.verify_records(out, live)

    def test_a_day_with_no_archive_is_listed_not_counted_as_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = raw_root(tmp)
            out = Path(tmp) / "archive"
            raw.archive_day(root, out, date(2026, 10, 6))
            live = self.live_dir(tmp, [self.record("2026-10-05", self.manifests(root)),
                                       self.record("2026-10-06", self.manifests(root))])
            report = raw.verify_records(out, live)
        self.assertEqual(report, {"archived": ["2026-10-06"], "unarchived": ["2026-10-05"]})


class PanelTests(unittest.TestCase):
    """The published panel's tracked fixtures, as a day's raw root: archive, restore, build."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.archive = Path(cls.tmp.name) / "archive"
        raw.archive_day(FIXTURES, cls.archive, date(2026, 10, 6))
        cls.panel = Path(cls.tmp.name) / "panel.csv"
        cls.provenance = raw.build_panel(cls.archive, date(2026, 10, 6), cls.panel)

    def registered(self, panel=None, archive=None):
        return raw.require_registered_panel(panel or self.panel, archive or self.archive)

    def test_the_panel_is_built_from_the_archive_alone(self):
        self.assertEqual(self.provenance["panel_sha256"], hashlib.sha256(self.panel.read_bytes()).hexdigest())
        self.assertEqual(self.provenance["raw_day"], "2026-10-06")
        self.assertIn("repo_model.cli build", self.provenance["build_command"])
        self.assertIn("--build-cutoff", self.provenance["build_command"])
        self.assertTrue(self.provenance["inputs"])
        for entry in self.provenance["inputs"]:
            self.assertTrue({"path", "sha256", "retrieved_at", "url"} <= set(entry))

    def test_the_build_command_is_the_live_records(self):
        """`build_panel` builds with the columns and decision time the live record builds with."""

        live = _live_record()
        argv = raw.build_argv(Path("R"), Path("P"), "2026-10-06T21:31:00+00:00")
        self.assertEqual(argv[0], "build")
        self.assertEqual([argv[i + 1] for i, a in enumerate(argv) if a == "--column"],
                         list(live.BUILD_COLUMNS))
        self.assertEqual(argv[argv.index("--decision-time") + 1], "16:00:00")

    def test_an_archived_panel_is_registered(self):
        self.assertEqual(self.registered()["panel_sha256"], self.provenance["panel_sha256"])

    def test_a_panel_with_no_build_manifest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            bare = Path(tmp) / "panel.csv"
            shutil.copy(self.panel, bare)
            shutil.copy(str(self.panel) + ".provenance.json", str(bare) + ".provenance.json")
            with self.assertRaises(ValueError):
                self.registered(bare)

    def test_a_panel_whose_bytes_differ_from_its_manifest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "panel.csv"
            for suffix in ("", ".manifest.json", ".provenance.json"):
                shutil.copy(str(self.panel) + suffix, str(copy) + suffix)
            copy.write_text(copy.read_text(encoding="utf-8").replace("\n", "\n", 1) + "2099-01-01\n",
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                self.registered(copy)

    def test_a_panel_with_no_provenance_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "panel.csv"
            for suffix in ("", ".manifest.json"):
                shutil.copy(str(self.panel) + suffix, str(copy) + suffix)
            with self.assertRaises(ValueError):
                self.registered(copy)

    def test_a_panel_built_from_bytes_the_archive_does_not_hold_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            other = Path(tmp) / "archive"
            partial = Path(tmp) / "partial"
            shutil.copytree(FIXTURES, partial)
            victim = next(partial.glob("treasury_bill_rates/*.csv"))
            victim.unlink()
            victim.with_suffix(".csv.manifest.json").unlink()
            raw.archive_day(partial, other, date(2026, 10, 6))
            with self.assertRaises(ValueError):
                self.registered(archive=other)

    def test_a_sidecar_naming_another_panels_digest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "panel.csv"
            for suffix in ("", ".manifest.json", ".provenance.json"):
                shutil.copy(str(self.panel) + suffix, str(copy) + suffix)
            sidecar = Path(str(copy) + ".provenance.json")
            data = json.loads(sidecar.read_text(encoding="utf-8"))
            data["panel_sha256"] = "0" * 64
            sidecar.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                self.registered(copy)

    def test_a_sidecar_naming_a_path_outside_the_archive_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "panel.csv"
            for suffix in ("", ".manifest.json", ".provenance.json"):
                shutil.copy(str(self.panel) + suffix, str(copy) + suffix)
            sidecar = Path(str(copy) + ".provenance.json")
            data = json.loads(sidecar.read_text(encoding="utf-8"))
            data["raw_day"] = "../.."
            sidecar.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                self.registered(copy)


class WorkflowTests(unittest.TestCase):
    """The workflows archive the bytes, and the scoring workflow can only score what they hold."""

    @classmethod
    def setUpClass(cls):
        import re

        cls.re = re
        cls.log = (ROOT / ".github" / "workflows" / "live-log.yml").read_text(encoding="utf-8")
        cls.score = (ROOT / ".github" / "workflows" / "live-score.yml").read_text(encoding="utf-8")

    def step(self, text, name):
        match = self.re.search(rf"\n      - name: {self.re.escape(name)}\n(.*?)(?=\n      - name: |\Z)", text, self.re.S)
        self.assertIsNotNone(match, name)
        return match.group(1)

    def names(self, text):
        return [m.group(1) for m in self.re.finditer(r"\n      - name: (.*)", text)]

    def test_the_daily_run_archives_the_raw_root_after_the_record_and_never_blocks_it(self):
        step = self.step(self.log, "Archive the raw inputs on live-raw")
        self.assertIn("continue-on-error: true", step)
        self.assertIn("steps.push.outcome == 'success'", step)
        self.assertIn("--raw-root work/raw", step)
        self.assertLess(step.index("live_raw.py archive"), step.index("commit --quiet"))
        self.assertLess(step.index("commit --quiet"), step.index("live_raw.py check-append"))
        self.assertLess(step.index("live_raw.py check-append"), step.index("git push"))
        names = self.names(self.log)
        self.assertLess(names.index("Append it to live-log"), names.index("Archive the raw inputs on live-raw"))
        self.assertLess(names.index("Archive the raw inputs on live-raw"), names.index("Post the digest outside the repository"))

    def test_a_failed_archive_reaches_the_failed_runs_issue(self):
        step = self.step(self.log, "Report a raw archive that failed")
        self.assertIn("steps.raw.outcome == 'failure'", step)
        self.assertIn("$FAILED_RUNS_ISSUE", step)

    def test_the_scoring_workflow_is_started_by_hand_and_never_overrides_the_clock(self):
        head = self.score.split("\njobs:")[0]
        self.assertIn("workflow_dispatch:", head)
        for trigger in ("schedule:", "push:", "pull_request"):
            self.assertNotIn(trigger, head)
        code = "\n".join(line for line in self.score.splitlines() if not line.lstrip().startswith("#"))
        self.assertNotIn("--override-clock", code)

    def test_the_scoring_workflow_verifies_then_builds_from_the_archive_then_scores(self):
        names = self.names(self.score)
        order = ["Verify the pin is a registered transition",
                 "Verify the log, the raw archive and every record's inputs",
                 "Build the outcome panel from the archive", "Score"]
        positions = [names.index(name) for name in order]
        self.assertEqual(positions, sorted(positions))
        verify = self.step(self.score, "Verify the log, the raw archive and every record's inputs")
        self.assertIn("live_integrity.py verify", verify)
        self.assertIn("live_raw.py verify", verify)
        panel = self.step(self.score, "Build the outcome panel from the archive")
        self.assertIn("live_raw.py build-panel", panel)
        score = self.step(self.score, "Score")
        self.assertIn("--archive-dir", score)
        self.assertIn("--panel", score)
        self.assertNotIn("curl", self.score)

    def test_the_gap_inputs_are_archived_before_the_reconstruction_reads_them(self):
        step = self.step(self.score, "Reconstruct the blind gap (first scoring date only)")
        self.assertIn("if: inputs.date == '2027-04-01'", step)
        self.assertLess(step.index("live_gap.py\" fetch"), step.index("live_raw.py archive"))
        self.assertLess(step.index("live_raw.py archive"), step.index("live_raw.py check-append"))
        self.assertLess(step.index("live_raw.py check-append"), step.index("git push"))
        self.assertLess(step.index("git push"), step.index("live_gap.py reconstruct"))
        self.assertIn("--label gap", step)

    def test_every_action_is_pinned_to_a_commit(self):
        uses = self.re.findall(r"uses: (\S+)", self.score + self.log)
        for use in uses:
            self.assertRegex(use, r"@[0-9a-f]{40}$")


def _live_record():
    spec = importlib.util.spec_from_file_location("live_record_for_raw", ROOT / "scripts" / "live_record.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    unittest.main()
