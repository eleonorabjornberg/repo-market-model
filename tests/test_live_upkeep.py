"""Live record upkeep (#263, review finding 10; #228): runway, holiday coverage, late digests.

Three things the live record needs and nothing checked:

* **Runway** (`RunwayTests`): a dated table the live record reads must have at
  least `data.RUNWAY_DAYS` (180) days left after today. `data.require_runway`
  is the guard; the real tables are checked against today's date, so CI goes red
  months before a live run would fail. `metadata/evaluation_splits.json` was
  short and was exempt under #354 until the 2027 regime was added (#362); no
  table is exempt now, and an exemption would expire the day its table is
  extended (the test then demands the exemption be removed).
* **Holiday coverage** (`HolidayCoverageTests`): `metadata/market_holidays.json`
  runs to 2030-12-31, and its rows for 2028-2030 follow the Federal Reserve
  Board's K.8 table. SIFMA has published no list beyond 2027, so the days that
  rest on a SIFMA recommendation (Good Friday, and a Friday observed for a
  Saturday holiday) are not in `closed` and not guessed: they are listed under
  `sifma_not_yet_published`, and must be resolved 30 days before they fall.
* **Late digests** (`ReconcileTests`, `ReconcileWorkflowTests`): a day whose
  record was pushed to `live-log` but whose #225 digest was never posted (the
  post is a separate step) gets its digest from `live_integrity.py reconcile`,
  marked "reconciled late". It reads the log and writes nothing in it.

Written first and watched failing: `RunwayTests` and `HolidayCoverageTests`
with `AttributeError: module 'repo_model.data' has no attribute 'require_runway'`
and `AssertionError: datetime.date(2027, 12, 31) != datetime.date(2030, 12, 31)`;
`ReconcileTests` with `AttributeError: module 'live_integrity_test' has no
attribute 'reconcile'`; `ReconcileWorkflowTests` with `AssertionError: None is
not None : Reconcile digests missing from the digest issue`.

Recorded mutations, each in a disposable copy under /tmp with the mutated line
confirmed applied, each killed by the test named:

* runway: in `data.require_runway`, `if left < minimum_days:` -> `if False:`
  makes `test_a_table_with_less_than_the_runway_left_is_refused` and
  `test_an_exemption_expires_when_the_table_is_extended` fail with
  `AssertionError: ValueError not raised`.
* only the days with no digest: in `live_integrity.reconcile`,
  `if posted is not None:` -> `if False:` makes
  `test_nothing_is_made_when_every_day_has_its_digest` fail with
  `AssertionError: {datetime.date(2026, 10, 5): ...} != {}`, and the command-line
  and late-digest tests fail the same way.
* posted digest equals the file: in `live_integrity.reconcile`,
  `if posted["sha256"] != file_sha256(repo / rel):` -> `if False:` makes
  `test_a_posted_digest_that_differs_from_the_file_is_refused` fail with
  `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from test_live_integrity import (
    WORKFLOW,
    build_log,
    digest_body,
    digests_of,
    git,
    integrity,
    save,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

#: Tables the live record reads whose last covered day is a date, and how to read it.
#: A table short of the runway is exempt only under an issue that rules on it.
EXEMPT: dict = {}


def last_days():
    from repo_model import data
    from repo_model.evaluation_splits import load_split_declaration

    splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
    return {
        "metadata/market_holidays.json": data.market_holidays().last,
        "metadata/evaluation_splits.json": splits.regimes[-1][2],
    }


class RunwayTests(unittest.TestCase):
    def test_a_table_with_less_than_the_runway_left_is_refused(self):
        from repo_model import data

        today = date(2026, 10, 7)
        self.assertEqual(data.RUNWAY_DAYS, 180)
        data.require_runway("t", today + timedelta(days=180), today)
        with self.assertRaisesRegex(ValueError, "179 days"):
            data.require_runway("t", today + timedelta(days=179), today)
        with self.assertRaises(ValueError):
            data.require_runway("t", today - timedelta(days=1), today)

    def test_every_dated_table_the_live_record_reads_has_the_runway_left_today(self):
        from repo_model import data

        today = date.today()
        for name, last in last_days().items():
            with self.subTest(name):
                if name in EXEMPT:
                    continue
                data.require_runway(name, last, today)

    def test_an_exemption_expires_when_the_table_is_extended(self):
        from repo_model import data

        today = date.today()
        for name, issue in EXEMPT.items():
            with self.subTest(name):
                with self.assertRaises(
                    ValueError, msg=f"{name} now has its runway: remove its exemption ({issue})"
                ):
                    data.require_runway(name, last_days()[name], today)


class HolidayCoverageTests(unittest.TestCase):
    TABLE = ROOT / "metadata" / "market_holidays.json"

    def table(self):
        return json.loads(self.TABLE.read_text(encoding="utf-8"))

    def test_the_table_runs_to_the_end_of_2030(self):
        from repo_model import data

        loaded = data.market_holidays()
        self.assertEqual((loaded.first, loaded.last), (date(2018, 1, 1), date(2030, 12, 31)))

    def test_the_federal_reserve_k8_days_are_closed(self):
        """K.8 (federalreserve.gov/aboutthefed/k8.htm, updated 8 July 2026), 2028-2030, observed days."""

        from repo_model import data

        k8 = [
            "2028-01-17", "2028-02-21", "2028-05-29", "2028-06-19", "2028-07-04", "2028-09-04",
            "2028-10-09", "2028-11-23", "2028-12-25",
            "2029-01-01", "2029-01-15", "2029-02-19", "2029-05-28", "2029-06-19", "2029-07-04",
            "2029-09-03", "2029-10-08", "2029-11-12", "2029-11-22", "2029-12-25",
            "2030-01-01", "2030-01-21", "2030-02-18", "2030-05-27", "2030-06-19", "2030-07-04",
            "2030-09-02", "2030-10-14", "2030-11-11", "2030-11-28", "2030-12-25",
        ]
        closed = data.market_holidays().closed
        for day in k8:
            with self.subTest(day):
                self.assertIn(date.fromisoformat(day), closed)

    def test_nothing_unpublished_is_guessed(self):
        """SIFMA's lists stop at 2027: Good Friday 2028-30 and 2028-11-10 are recorded, not closed."""

        from repo_model import data

        pending = {entry["date"] for entry in self.table()["sifma_not_yet_published"]}
        self.assertEqual(pending, {"2028-04-14", "2028-11-10", "2029-03-30", "2030-04-19"})
        closed = data.market_holidays().closed
        for day in pending:
            self.assertNotIn(date.fromisoformat(day), closed)
        for entry in self.table()["sifma_not_yet_published"]:
            self.assertTrue(entry["reason"])
            self.assertFalse(entry["verified"])

    def test_a_pending_day_is_resolved_30_days_before_it_falls(self):
        """SIFMA publishes the next year's list in December; by then the row moves to `closed` or `opened`."""

        today = date.today()
        for entry in self.table()["sifma_not_yet_published"]:
            with self.subTest(entry["date"]):
                self.assertGreater(
                    date.fromisoformat(entry["date"]),
                    today + timedelta(days=30),
                    "SIFMA's list should be out: resolve this row (move it to closed or "
                    "statutory_days_the_market_opened, verified at source)",
                )


class ReconcileTests(unittest.TestCase):
    def posted(self, tmp, comments):
        return integrity.parse_digests(save(comments, tmp))

    def test_a_day_with_no_digest_gets_one_marked_reconciled_late(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            digests = self.posted(tmp, comments[:-1])
            made = integrity.reconcile(repo, digests, run_url="https://example.test/run/9")
            self.assertEqual(list(made), [date(2026, 10, 7)])
            body = made[date(2026, 10, 7)]
            self.assertIn("reconciled late", body)
            self.assertIn("https://example.test/run/9", body)
            # It is a digest: posted, it parses to the file's SHA-256 and its adding commit,
            # and the whole log then verifies.
            comments.append({"author": "github-actions[bot]", "body": body})
            full = self.posted(tmp, comments[:-2] + comments[-1:])
            self.assertEqual(
                full[date(2026, 10, 7)]["sha256"],
                integrity.file_sha256(repo / "live" / "2026-10-07.json"),
            )
            self.assertEqual(len(integrity.verify(repo, full)), 3)

    def test_nothing_is_made_when_every_day_has_its_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            self.assertEqual(integrity.reconcile(repo, self.posted(tmp, comments)), {})

    def test_a_posted_digest_that_differs_from_the_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            comments[0]["body"] = re.sub(r"SHA-256: `[0-9a-f]{64}`", "SHA-256: `" + "a" * 64 + "`", comments[0]["body"])
            with self.assertRaisesRegex(ValueError, "differs"):
                integrity.reconcile(repo, self.posted(tmp, comments))

    def test_a_digest_that_names_another_commit_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            comments[0]["body"] = re.sub(r"live-log: [0-9a-f]{40}", "live-log: " + "b" * 40, comments[0]["body"])
            with self.assertRaisesRegex(ValueError, "commit"):
                integrity.reconcile(repo, self.posted(tmp, comments))

    def test_it_touches_nothing_in_the_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            before = {p.name: p.read_bytes() for p in (repo / "live").glob("*")}
            head = git(repo, "rev-parse", "HEAD")
            integrity.reconcile(repo, self.posted(tmp, comments[:1]))
            self.assertEqual({p.name: p.read_bytes() for p in (repo / "live").glob("*")}, before)
            self.assertEqual(git(repo, "rev-parse", "HEAD"), head)
            self.assertEqual(git(repo, "status", "--porcelain", "--untracked-files=all"), "")

    def test_the_command_line_writes_one_body_per_missing_day_outside_the_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, comments = build_log(tmp)
            digests = save(comments[:1], tmp)
            out = Path(tmp) / "out"
            argv = ["reconcile", "--live-dir", str(repo), "--digests", str(digests), "--out-dir", str(out)]
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(integrity.main(argv), 0)
            self.assertEqual(json.loads(buffer.getvalue()), {"reconciled": ["2026-10-06", "2026-10-07"]})
            self.assertEqual(sorted(p.name for p in out.glob("*")), ["2026-10-06.md", "2026-10-07.md"])
            self.assertEqual(git(repo, "status", "--porcelain", "--untracked-files=all"), "")
            subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "live_integrity.py"), *argv],
                           check=True, capture_output=True)


class ReconcileWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def step(self, name):
        match = re.search(rf"\n      - name: {re.escape(name)}\n(.*?)(?=\n      - name: |\Z)", self.text, re.S)
        self.assertIsNotNone(match, name)
        return match.group(1)

    def test_every_run_posts_the_missing_digests_before_the_log_is_verified(self):
        step = self.step("Reconcile digests missing from the digest issue")
        self.assertIn("id: reconcile", step)
        self.assertIn("if: always() && steps.branch.outcome == 'success'", step)
        self.assertIn("live_integrity.py reconcile", step)
        self.assertIn("$DIGEST_ISSUE", step)
        names = [m.group(1) for m in re.finditer(r"\n      - name: (.*)", self.text)]
        self.assertLess(names.index("Post the digest outside the repository"),
                        names.index("Reconcile digests missing from the digest issue"))
        self.assertLess(names.index("Reconcile digests missing from the digest issue"),
                        names.index("Verify every logged file"))

    def test_it_stages_and_pushes_nothing(self):
        step = self.step("Reconcile digests missing from the digest issue")
        for word in ("git add", "git commit", "git push", "git -c"):
            self.assertNotIn(word, step)

    def test_its_failure_reaches_the_failed_runs_issue(self):
        failed = self.step("Open or update the failed-runs issue")
        self.assertIn("reconcile=${{ steps.reconcile.outcome }}", failed)


if __name__ == "__main__":
    unittest.main()
