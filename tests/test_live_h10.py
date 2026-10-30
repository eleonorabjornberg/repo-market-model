"""H10 prospective confirmation: the live job detects onsets and attributes them with the registered code (#1322).

H10, prospective confirmation (milestone M3). Eleonora's ruling of 30 October 2026 (option (a'), ledger item 83): the
model repo's live job does the work and repo-market-liquidity runs no schedule. `scripts/live_h10.py` is that job's
step. Each business day it detects the onsets of the live panel with the parent's own rule, attributes each new one with
`repo_liquidity.h10_live.attribute_onset` at the registered commit, and writes one file per day,
`h10/<day>.json`, labelled prospective, on an add-only branch of its own (`live-h10`). The H5 live record, its pin and
its schedule are not touched.

What is held here (the registered code itself runs only in the workflow, in a clean checkout of liquidity at the
registered commit and of the parent at its pin; these tests inject the backend):

* **the pin** (`PinTests`): `metadata/live_h10_pin.json` holds the values of liquidity's registration of 22 October 2026
  on repo-market-liquidity#23;
* **the digest** (`DigestTests`): a row whose `method_digest` is not the registered one, or whose `parent_commit` is not
  the registered parent, or that was made with the parent override or from a dirty parent, is refused: nothing is written
  and the job fails;
* **the lockbox** (`LookAheadTests`): a `LookAheadError` is recorded as a pending row and the day goes on; the job never retries with an
  override and never attributes the onsets after it;
* **the days** (`DayTests`): an onset is reported once, as soon as it is flagged; a "not attributable" row is kept; an
  onset whose report window has closed stays in the record as a miss; a day is recorded once; a day with no onset is
  recorded too, so a missing file means the job did not run;
* **the onset source** (`OnsetSourceTests`): `repo_model.onset` and `pressure.onsets` must agree;
* **the branch** (`AppendOnlyTests`): a day's commit adds `h10/<day>.json` as the bot and nothing else;
* **the workflow** (`WorkflowTests`): the step reads the pin from the manifest, never passes the override, never blocks
  the H5 record, and the run turns its failure red.

Recorded mutations (#1322), each applied in a disposable copy with the mutated line confirmed by grep, each killed by the
test named (the exception is what the failing test raised):

* digest: in `live_h10.check_row`, `if row.get("method_digest") != pin["method_digest"]:` -> `if False:` makes
  `test_a_row_whose_digest_is_not_the_registered_one_is_refused` fail with `AssertionError: DigestMismatch not raised`.
* parent: in `live_h10.check_row`, `if row.get("parent_commit") != pin["parent_commit"]:` -> `if False:` makes
  `test_a_row_from_another_parent_is_refused` fail with `AssertionError: DigestMismatch not raised`.
* lockbox: in `live_h10.run_day`, `except _look_ahead_error() as error:` -> `except ZeroDivisionError as error:` makes
  `test_a_look_ahead_error_is_recorded_as_pending_and_the_day_goes_on` fail with `splits.LookAheadError` propagating out of
  `run_day`.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]

LIQUIDITY_COMMIT = "783848316995d4f2d425abea0c6bd0be3e157c26"
PARENT_COMMIT = "08ff67e27bc3d7e357491cf8e1da59793702b3fb"
DIGEST = "43bf1303164c3c085b33ccf762268b721a5bddc9d7a4dcf68524c67ea33d15bb"

BOT = {
    "GIT_AUTHOR_NAME": "github-actions[bot]",
    "GIT_AUTHOR_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "github-actions[bot]",
    "GIT_COMMITTER_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
}


def _load():
    spec = importlib.util.spec_from_file_location("live_h10_test", ROOT / "scripts" / "live_h10.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


live_h10 = _load()

#: Business days around the registration, as panel days (the fake panel is these dates only).
DAYS = [date(2026, 10, d) for d in (14, 15, 16, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30)] + [
    date(2026, 11, d) for d in (2, 3, 4, 5, 6, 9, 10, 11, 12)
]


def good_row(onset, report, **over):
    row = {
        "onset": onset.isoformat(), "report_day": report.isoformat(), "status": "attributed", "reason": None,
        "under_bar": True, "beats_null": True, "counted": True, "regime": "depleted",
        "method_digest": DIGEST, "parent_commit": PARENT_COMMIT, "parent_override": False,
        "imported_parent_commit": PARENT_COMMIT, "imported_parent_clean": True,
    }
    row.update(over)
    return row


class Fake:
    """An injected backend: the panel's days, the onset days it flags, and an `attribute` that records its calls."""

    def __init__(self, onsets=(), days=DAYS, behaviour=None):
        self.rows = [SimpleNamespace(date=d) for d in days]
        self.flagged = list(onsets)
        self.calls = []
        self.behaviour = behaviour

    def backend(self):
        @contextmanager
        def rule():
            yield "rule"

        def attribute(rows, rule_, onset, report, **kwargs):
            self.calls.append((onset, report, kwargs))
            if self.behaviour is not None:
                return self.behaviour(onset, report)
            return good_row(onset, report)

        return live_h10.Backend(
            load_rows=lambda path: self.rows, onset_days=lambda rows: list(self.flagged),
            rule=rule, attribute=attribute,
        )


class PinTests(unittest.TestCase):
    def test_the_manifest_holds_the_registered_values(self):
        pin = json.loads((ROOT / "metadata" / "live_h10_pin.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["liquidity_commit"], LIQUIDITY_COMMIT)
        self.assertEqual(pin["parent_commit"], PARENT_COMMIT)
        self.assertEqual(pin["method_digest"], DIGEST)
        self.assertEqual(pin["registered_on"], "2026-10-22")
        self.assertEqual(pin["report_days"], 10)
        self.assertEqual(live_h10.load_pin(), pin)

    def test_a_pin_that_is_not_a_full_commit_or_digest_is_refused(self):
        pin = live_h10.load_pin()
        for key in ("liquidity_commit", "parent_commit", "method_digest"):
            with self.assertRaises(ValueError, msg=key):
                live_h10.require_wellformed_pin({**pin, key: pin[key][:12]})


class DigestTests(unittest.TestCase):
    def setUp(self):
        self.pin = live_h10.load_pin()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)

    def _run(self, behaviour):
        fake = Fake(onsets=[date(2026, 10, 28)], behaviour=behaviour)
        return fake, live_h10.run_day(date(2026, 10, 30), Path("panel.csv"), self.out, fake.backend(), self.pin)

    def test_a_row_whose_digest_is_not_the_registered_one_is_refused(self):
        with self.assertRaises(live_h10.DigestMismatch):
            self._run(lambda o, r: good_row(o, r, method_digest="0" * 64))
        self.assertEqual(list(self.out.rglob("*.json")), [], "a refused row writes no file")

    def test_a_row_with_no_digest_is_refused(self):
        def behaviour(o, r):
            row = good_row(o, r)
            del row["method_digest"]
            return row

        with self.assertRaises(live_h10.DigestMismatch):
            self._run(behaviour)
        self.assertEqual(list(self.out.rglob("*.json")), [])

    def test_a_row_from_another_parent_is_refused(self):
        with self.assertRaises(live_h10.DigestMismatch):
            self._run(lambda o, r: good_row(o, r, parent_commit="1" * 40))
        self.assertEqual(list(self.out.rglob("*.json")), [])

    def test_a_row_made_with_the_parent_override_or_a_dirty_parent_is_refused(self):
        for over in ({"parent_override": True}, {"imported_parent_clean": False},
                     {"imported_parent_commit": "2" * 40}):
            with self.subTest(over=over), self.assertRaises(live_h10.DigestMismatch):
                self._run(lambda o, r, over=over: good_row(o, r, **over))
        self.assertEqual(list(self.out.rglob("*.json")), [])

    def test_one_bad_row_writes_none_of_the_days_rows(self):
        fake = Fake(onsets=[date(2026, 10, 27), date(2026, 10, 28)],
                    behaviour=lambda o, r: good_row(o, r, **({"method_digest": "0" * 64} if o.day == 28 else {})))
        with self.assertRaises(live_h10.DigestMismatch):
            live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin)
        self.assertEqual(list(self.out.rglob("*.json")), [])

    def test_the_override_is_never_passed(self):
        fake, _ = self._run(None)
        self.assertEqual(fake.calls[0][2], {})


class LookAheadTests(unittest.TestCase):
    def setUp(self):
        self.pin = live_h10.load_pin()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)

    def test_a_look_ahead_error_is_recorded_as_pending_and_the_day_goes_on(self):
        def behaviour(onset, report):
            if onset.day == 28:
                raise LookAheadError("attribution: scored day 2026-09-04 is in the locked blind tier")
            return good_row(onset, report)

        fake = Fake(onsets=[date(2026, 10, 27), date(2026, 10, 28), date(2026, 10, 29)], behaviour=behaviour)
        code = live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin)
        self.assertEqual(code, 0)
        self.assertEqual([c[0].day for c in fake.calls], [27, 28, 29], "the other onsets are still attributed")
        record = json.loads((self.out / "h10" / "2026-10-30.json").read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "pending")
        self.assertEqual([(r["onset"], r["status"]) for r in record["rows"]],
                         [("2026-10-27", "attributed"), ("2026-10-28", "pending"), ("2026-10-29", "attributed")])
        pending = record["rows"][1]
        self.assertIn("awaiting the new registration", pending["reason"])
        self.assertIn("locked blind tier", pending["refusal"]["error"])
        self.assertEqual(pending["refusal"]["type"], "LookAheadError")
        self.assertFalse(pending["counted"])
        self.assertEqual(pending["label"], "prospective")
        self.assertEqual(record["label"], "prospective")

    def test_a_refused_onset_is_tried_again_the_next_day_not_lost(self):
        refuse = Fake(onsets=[date(2026, 10, 28)], behaviour=lambda o, r: (_ for _ in ()).throw(LookAheadError("locked")))
        live_h10.run_day(date(2026, 10, 29), Path("p"), self.out, refuse.backend(), self.pin)
        again = Fake(onsets=[date(2026, 10, 28)])
        live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, again.backend(), self.pin)
        self.assertEqual(len(again.calls), 1, "a pending onset is not attributed, so it is still open")


class DayTests(unittest.TestCase):
    def setUp(self):
        self.pin = live_h10.load_pin()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)

    def _record(self, day):
        return json.loads((self.out / "h10" / f"{day}.json").read_text(encoding="utf-8"))

    def test_a_day_with_no_onset_is_recorded(self):
        fake = Fake()
        self.assertEqual(live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin), 0)
        record = self._record("2026-10-30")
        self.assertEqual(record["rows"], [])
        self.assertEqual(record["onsets_found"], [])
        self.assertEqual(record["status"], "ok")
        self.assertEqual(record["label"], "prospective")
        self.assertEqual(record["hypothesis"], "H10")
        self.assertEqual(record["registered"]["method_digest"], DIGEST)
        self.assertEqual(record["registered"]["liquidity_commit"], LIQUIDITY_COMMIT)
        self.assertEqual(record["panel_last_day"], "2026-10-29")
        self.assertEqual(fake.calls, [])

    def test_the_panel_is_cut_at_the_decision_day(self):
        fake = Fake()
        live_h10.run_day(date(2026, 10, 28), Path("p"), self.out, fake.backend(), self.pin)
        self.assertEqual(self._record("2026-10-28")["panel_last_day"], "2026-10-27")

    def test_an_onset_is_attributed_on_the_day_it_is_flagged(self):
        fake = Fake(onsets=[date(2026, 10, 29)])
        live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin)
        self.assertEqual([(c[0], c[1]) for c in fake.calls], [(date(2026, 10, 29), date(2026, 10, 29))])
        record = self._record("2026-10-30")
        self.assertEqual(record["onsets_found"], ["2026-10-29"])
        self.assertEqual(record["rows"][0]["status"], "attributed")
        self.assertEqual(record["rows"][0]["label"], "prospective")

    def test_an_onset_is_reported_once(self):
        live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, Fake(onsets=[date(2026, 10, 29)]).backend(), self.pin)
        later = Fake(onsets=[date(2026, 10, 29)])
        live_h10.run_day(date(2026, 11, 2), Path("p"), self.out, later.backend(), self.pin)
        self.assertEqual(later.calls, [])
        self.assertEqual(self._record("2026-11-02")["rows"], [])

    def test_a_not_attributable_row_is_kept_with_its_reason(self):
        fake = Fake(onsets=[date(2026, 10, 29)], behaviour=lambda o, r: good_row(
            o, r, status="not attributable", reason="an input is missing", under_bar=False, beats_null=False,
            counted=False))
        self.assertEqual(live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin), 0)
        row = self._record("2026-10-30")["rows"][0]
        self.assertEqual((row["status"], row["reason"], row["counted"]), ("not attributable", "an input is missing", False))

    def test_an_onset_before_the_registration_is_not_this_jobs(self):
        fake = Fake(onsets=[date(2026, 10, 21)])
        live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin)
        self.assertEqual(fake.calls, [])
        self.assertEqual(self._record("2026-10-30")["onsets_found"], [])

    def test_an_onset_on_the_registration_day_counts(self):
        fake = Fake(onsets=[date(2026, 10, 22)])
        live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin)
        self.assertEqual(len(fake.calls), 1)

    def test_an_onset_whose_window_has_closed_is_a_miss_not_a_call(self):
        # 22 October + 10 panel days is 5 November; the 6 November record is one panel day too late.
        fake = Fake(onsets=[date(2026, 10, 22)])
        code = live_h10.run_day(date(2026, 11, 9), Path("p"), self.out, fake.backend(), self.pin)
        self.assertEqual(fake.calls, [])
        self.assertEqual(code, 0)
        row = self._record("2026-11-09")["rows"][0]
        self.assertEqual((row["status"], row["counted"]), ("not attributable", False))
        self.assertIn("10 panel days", row["reason"])
        self.assertEqual(row["onset"], "2026-10-22")
        self.assertEqual(row["label"], "prospective")

    def test_the_last_day_of_the_window_still_reports(self):
        fake = Fake(onsets=[date(2026, 10, 22)])
        live_h10.run_day(date(2026, 11, 6), Path("p"), self.out, fake.backend(), self.pin)
        self.assertEqual([(c[0], c[1]) for c in fake.calls], [(date(2026, 10, 22), date(2026, 11, 5))])

    def test_a_day_is_recorded_once(self):
        fake = Fake()
        live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin)
        with self.assertRaises(ValueError):
            live_h10.run_day(date(2026, 10, 30), Path("p"), self.out, fake.backend(), self.pin)

    def test_the_report_deadline_is_ten_panel_days_after_the_onset(self):
        deadline = live_h10.report_deadline([r.date for r in Fake().rows], date(2026, 10, 22))
        self.assertEqual(deadline, date(2026, 11, 5))


class OnsetSourceTests(unittest.TestCase):
    def test_the_two_onset_sources_must_agree(self):
        a = [date(2026, 10, 28)]
        self.assertEqual(live_h10.agreed_onsets(a, tuple(a)), a)
        with self.assertRaises(ValueError):
            live_h10.agreed_onsets(a, ())
        with self.assertRaises(ValueError):
            live_h10.agreed_onsets([], (date(2026, 10, 28),))


def git(repo, *argv, env=None):
    done = subprocess.run(["git", *argv], cwd=repo, capture_output=True, text=True,
                          env={**os.environ, **(env or BOT)})
    if done.returncode != 0:
        raise AssertionError(done.stderr)
    return done.stdout.strip()


class AppendOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q", "-b", "live-h10")

    def _commit(self, files, env=None):
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "h10", env=env)
        return git(self.repo, "rev-parse", "HEAD")

    def test_one_new_day_file_by_the_bot_is_accepted(self):
        first = self._commit({"h10/2026-10-29.json": "{}\n"})
        live_h10.require_add_only(self.repo, None, date(2026, 10, 29))
        self._commit({"h10/2026-10-30.json": "{}\n"})
        live_h10.require_add_only(self.repo, first, date(2026, 10, 30))

    def test_a_change_to_an_earlier_day_is_refused(self):
        first = self._commit({"h10/2026-10-29.json": "{}\n"})
        self._commit({"h10/2026-10-29.json": '{"x": 1}\n', "h10/2026-10-30.json": "{}\n"})
        with self.assertRaises(ValueError):
            live_h10.require_add_only(self.repo, first, date(2026, 10, 30))

    def test_a_file_outside_the_day_is_refused(self):
        first = self._commit({"h10/2026-10-29.json": "{}\n"})
        self._commit({"h10/2026-10-30.json": "{}\n", "other.txt": "x"})
        with self.assertRaises(ValueError):
            live_h10.require_add_only(self.repo, first, date(2026, 10, 30))

    def test_another_author_is_refused(self):
        self._commit({"h10/2026-10-30.json": "{}\n"},
                     env={**BOT, "GIT_AUTHOR_NAME": "someone", "GIT_AUTHOR_EMAIL": "s@example.com"})
        with self.assertRaises(ValueError):
            live_h10.require_add_only(self.repo, None, date(2026, 10, 30))


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / ".github" / "workflows" / "live-log.yml").read_text(encoding="utf-8")
        start = cls.text.index("- name: Attribute the day's H10 onsets")
        end = cls.text.index("- name: Anchor the digests in Sigstore Rekor")
        cls.step = cls.text[start:end]

    def test_the_step_runs_after_the_record_and_never_blocks_it(self):
        self.assertLess(self.text.index("- name: Append it to live-log"), self.text.index("- name: Attribute the day's H10"))
        self.assertIn("continue-on-error: true", self.step)
        self.assertIn("env.WROTE == '1'", self.step)

    def test_it_reads_the_pin_from_the_manifest_and_never_overrides_the_parent(self):
        self.assertIn("metadata/live_h10_pin.json", self.step)
        self.assertNotIn("allow_unpinned_parent", self.text)
        self.assertNotIn("allow-unpinned", self.text)
        for literal in (LIQUIDITY_COMMIT, PARENT_COMMIT, DIGEST):
            self.assertNotIn(literal, self.text, "the pin is the manifest's, not a copy in the workflow")

    def test_it_runs_the_pinned_trees_not_mains_or_liquiditys_main(self):
        self.assertIn("git -C h10-liquidity checkout --quiet --detach", self.step)
        self.assertIn('test "$(git -C h10-liquidity rev-parse HEAD)" = "$h10_liq"', self.step)
        self.assertIn('test "$(git -C h10-parent rev-parse HEAD)" = "$h10_parent"', self.step)
        self.assertIn("PYTHONPATH=../h10-liquidity/src:../h10-parent/src", self.step)
        self.assertNotIn("PYTHONPATH=src", self.step)

    def test_it_pushes_only_to_its_own_branch_with_the_add_only_check(self):
        self.assertIn("live_h10.py check-append", self.step)
        self.assertIn("HEAD:refs/heads/live-h10", self.step)
        self.assertNotIn("refs/heads/live-log", self.step)

    def test_a_failure_turns_the_run_red_and_reaches_the_failed_runs_issue(self):
        self.assertIn("steps.h10.outcome == 'failure'", self.text)
        tail = self.text[self.text.index("- name: Report an H10 step that failed"):]
        self.assertIn("FAILED_RUNS_ISSUE", tail)
        self.assertIn("exit 1", tail)

    def test_the_h5_record_steps_do_not_depend_on_the_h10_step(self):
        start = self.text.index("- name: Append it to live-log")
        before = self.text[start:self.text.index("- name: Attribute the day's H10")]
        self.assertNotIn("steps.h10", before)
        for name in ("Anchor the digests in Sigstore Rekor", "Post the digest outside the repository"):
            start = self.text.index(f"- name: {name}")
            body = self.text[start:self.text.index("- name:", start + 10)]
            self.assertNotIn("steps.h10", body, name)


if __name__ == "__main__":
    unittest.main()
