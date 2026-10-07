"""The live scorer's clock guard, provenance and event-cell block rule (#257).

An independent review (6 October 2026, findings 4, 7, 30 and 39) found that
`scripts/live_score.py` enforced its scoring dates only against its own `--date`
argument: with a synthetic record it scored 2027-04-01 on 2026-10-06. Its output
carried no wall-clock time, outcome-panel digest, build command or code SHA, and
a record whose target day was missing from the panel was dropped without a word.
Its Brier event cells used `block_length=h`, where the final test's used the
measured horizon overlap h + 1.

What is held here:

* **the clock guard** (`ClockGuardTests`): `LookAheadError` when today's date in
  America/New_York is before `--date`, in `main`, in `assemble` and in the gap
  block. An override flag is allowed only if the output records it. Tests patch
  the module-level clock `live_score.now_utc`, never a flag or an environment
  variable;
* **provenance** (`ProvenanceTests`): the output carries the start time (UTC), the
  outcome panel's SHA-256, the build command, the code SHA, `sys.version`, the
  dependency lock's digest and every record's digest, and lists, with a reason,
  every record and horizon it did not score. Nothing is skipped silently;
* **the event cells' block rule** (`EventBlockTests`): h + 1, as the final test's;
* **end to end, on ordinary-history fixtures** (`EndToEndTests`): a fixture live log is verified,
  an outcome panel is built from an archived raw root, and `main` writes a result carrying the
  provenance above. No live or blind outcome exists in the fixtures, so none is inspected; a
  panel that is not one `live_raw.py build-panel` built from the archive is refused;
* **the gap's boundaries** (`GapBoundaryProvenanceTests`): the gap block names the
  days it skipped, and its day boundaries are asserted equal to those computed
  from the pinned tree.

Recorded mutations (#257), each applied in a disposable copy outside the tree with the mutated
line confirmed by grep, each killed by the tests named (the exception is what the failing test raised):

* clock guard: in `live_score.require_clock`, `early = today < day` -> `early = False` fails
  `test_a_date_in_the_future_is_refused`, `test_the_clock_is_read_in_new_york_not_utc` and
  `test_the_gap_block_refuses_too` with `AssertionError: LookAheadError not raised`, and
  `test_an_override_is_allowed_only_if_it_is_recorded` with `AssertionError: False is not true`.
* New York, not UTC: in `require_clock`, `today = checked.astimezone(EASTERN).date()` ->
  `today = checked.date()` fails `test_the_clock_is_read_in_new_york_not_utc` with
  `AssertionError: LookAheadError not raised`; nothing else fails.
* override is recorded: in `require_clock`, `"override": early}` -> `"override": False}` fails
  `test_an_override_is_allowed_only_if_it_is_recorded`, `test_the_result_carries_the_clock_it_was_scored_under`
  and `test_the_gap_block_refuses_too` with `AssertionError: False is not true`.
* the guard is in `assemble`: `clock_block = require_clock(day, override=override_clock)` replaced by a
  literal dict fails `test_the_result_carries_the_clock_it_was_scored_under` (`AssertionError`) and
  `test_assemble_refuses_before_computing_a_cell` (`TypeError`: the unguarded run reached the patched cells).
* the guard is in the gap block: in `score_gap`, the same line replaced by `{"override": False}` fails
  `test_the_gap_block_refuses_too` with `AssertionError: LookAheadError not raised`.
* the guard is in `main`, before any read: in `main`, `clock_block = require_clock(day, override=args.override_clock)`
  replaced by a literal dict fails `test_the_script_refuses_before_reading_anything` with `ValueError`
  (the run went on to read a log that is not there, and refused for that instead).
* event block rule: in `live_score._paired`, `block_length=h + 1` -> `block_length=h` fails
  `test_every_event_cell_uses_the_horizon_overlap` with `AssertionError: 1 != 2 : +5bp/h1`.
* nothing skipped silently: in `live_score.skipped_records`, `elif when in by_date: continue` ->
  `elif True: continue` fails `test_a_record_with_no_outcome_is_listed_not_dropped` with
  `AssertionError: [] is not true`.
* a registered panel only: in `main`, `panel_provenance = _raw().require_registered_panel(...)` replaced by a
  literal dict fails `test_a_panel_that_is_not_the_archives_is_refused` with `AssertionError: ValueError not
  raised` and `test_the_result_carries_its_provenance`.
* the gap's boundaries: in `require_gap_boundaries_equal`, `if here != there:` -> `if False:` fails
  `test_the_boundaries_are_asserted_equal_to_the_pinned_trees` and
  `test_a_pinned_tree_with_another_holiday_table_is_refused` with `AssertionError: ValueError not raised`.

Red first: this file was written, and run, before `live_score.py` had `now_utc`, `require_clock`,
`build_provenance`, `skipped_records` or any of the rest. Every clock, provenance and gap test errored
with `AttributeError` on the missing name, and `test_every_event_cell_uses_the_horizon_overlap` failed
with `AssertionError: 1 != 2 : +5bp/h1`.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock

from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)
from test_live_integrity import FIXTURE_MANIFEST, build_log, save
from test_live_gap import SHARP, WIDE, _first_live_record, _gap_records, _live_records, _outcomes
from test_live_record import SPLITS, _scoring_records, live, score

ROOT = Path(__file__).resolve().parents[1]
DAY = date(2027, 4, 1)
FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"


def at(year, month, day, hour=12, minute=0):
    """A patched clock reading that UTC instant."""

    return mock.patch.object(
        score, "now_utc", lambda: datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    )


class ClockGuardTests(unittest.TestCase):
    """The scorer refuses a scoring date that has not come in New York."""

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)
        cls.records, cls.rows = _scoring_records(SHARP, WIDE)

    def test_a_date_in_the_future_is_refused(self):
        with at(2026, 10, 6):
            with self.assertRaises(LookAheadError):
                score.require_clock(DAY)

    def test_the_scoring_date_itself_and_later_pass(self):
        for when in ((2027, 4, 1, 12), (2027, 4, 2, 12), (2030, 1, 1, 12)):
            with self.subTest(when=when), at(*when):
                self.assertFalse(score.require_clock(DAY)["override"])

    def test_the_clock_is_read_in_new_york_not_utc(self):
        # 03:00 UTC on 1 April is 23:00 on 31 March in New York (EDT).
        with at(2027, 4, 1, 3, 0):
            with self.assertRaises(LookAheadError):
                score.require_clock(DAY)
        # 04:30 UTC is 00:30 on 1 April in New York.
        with at(2027, 4, 1, 4, 30):
            self.assertEqual(score.require_clock(DAY)["today_new_york"], "2027-04-01")

    def test_an_override_is_allowed_only_if_it_is_recorded(self):
        with at(2026, 10, 6):
            record = score.require_clock(DAY, override=True)
        self.assertTrue(record["override"])
        self.assertEqual(record["today_new_york"], "2026-10-06")
        with at(2027, 4, 2):
            self.assertFalse(score.require_clock(DAY, override=True)["override"])

    def test_the_result_carries_the_clock_it_was_scored_under(self):
        with at(2026, 10, 6):
            result = score.assemble(self.records, self.rows, self.splits, DAY, previous=[],
                                    override_clock=True)
        self.assertTrue(result["clock"]["override"])
        with at(2027, 4, 2, 15, 0):
            result = score.assemble(self.records, self.rows, self.splits, DAY, previous=[])
        self.assertFalse(result["clock"]["override"])
        self.assertEqual(result["clock"]["checked_at_utc"], "2027-04-02T15:00:00+00:00")

    def test_assemble_refuses_before_computing_a_cell(self):
        with at(2026, 10, 6), mock.patch.object(score, "score_crps") as crps, \
                mock.patch.object(score, "score") as brier:
            with self.assertRaises(LookAheadError):
                score.assemble(self.records, self.rows, self.splits, DAY, previous=[])
        crps.assert_not_called()
        brier.assert_not_called()

    def test_the_gap_block_refuses_too(self):
        gap = _gap_records(SHARP, WIDE)
        rows = _outcomes(date(2026, 8, 3), date(2026, 12, 31))
        with at(2026, 10, 6):
            with self.assertRaises(LookAheadError):
                score.score_gap(gap, _first_live_record(), rows, self.splits, DAY)
            result = None
            with mock.patch.object(score, "_require_scored_days_unlocked"):
                result = score.score_gap(gap, _first_live_record(), rows, self.splits, DAY,
                                         override_clock=True)
        self.assertTrue(result["clock"]["override"])

    def test_the_script_refuses_before_reading_anything(self):
        with tempfile.TemporaryDirectory() as tmp, at(2026, 10, 6):
            out = Path(tmp) / "out.json"
            with self.assertRaises(LookAheadError):
                score.main(["--date", "2027-04-01", "--live-dir", str(Path(tmp) / "none"),
                            "--panel", str(Path(tmp) / "none.csv"), "--archive-dir",
                            str(Path(tmp) / "none"), "--output", str(out)])
            self.assertFalse(out.exists())


class ProvenanceTests(unittest.TestCase):
    """The output says what produced it, and lists what it did not score."""

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)

    def test_the_provenance_block_names_what_produced_the_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            panel = Path(tmp) / "panel.csv"
            panel.write_bytes(b"date,sofr,iorb\n2026-10-06,4.01,4.00\n")
            started = datetime(2027, 4, 2, 15, 0, tzinfo=timezone.utc)
            block = score.build_provenance(
                started_at=started, panel=panel, argv=["live_score.py", "--date", "2027-04-01"],
                panel_provenance={"build_command": "repo_model.cli build --raw-root R"},
                record_digests=[{"decision_day": "2026-10-05", "sha256": "a" * 64}],
                previous=[],
            )
        self.assertEqual(block["started_at_utc"], "2027-04-02T15:00:00+00:00")
        self.assertEqual(block["panel_sha256"], hashlib.sha256(
            b"date,sofr,iorb\n2026-10-06,4.01,4.00\n").hexdigest())
        self.assertEqual(block["scoring_command"], "live_score.py --date 2027-04-01")
        self.assertEqual(block["panel_build_command"], "repo_model.cli build --raw-root R")
        self.assertRegex(block["code_sha"], r"^[0-9a-f]{40}$")
        self.assertEqual(block["python_version"], sys.version)
        self.assertEqual(block["dependency_lock_sha256"], hashlib.sha256(
            (ROOT / "metadata" / "live_requirements.lock").read_bytes()).hexdigest())
        self.assertEqual(block["live_records"], [{"decision_day": "2026-10-05", "sha256": "a" * 64}])
        self.assertEqual(block["previous_scores"], [])

    def test_a_previous_score_is_linked_by_its_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = Path(tmp) / "earlier.json"
            previous.write_bytes(b'{"date": "2027-04-01"}\n')
            panel = Path(tmp) / "panel.csv"
            panel.write_bytes(b"x\n")
            block = score.build_provenance(
                started_at=datetime(2027, 10, 2, tzinfo=timezone.utc), panel=panel, argv=["x"],
                panel_provenance={"build_command": "b"}, record_digests=[], previous=[previous])
        self.assertEqual(block["previous_scores"],
                         [{"date": "2027-04-01", "sha256": hashlib.sha256(
                             b'{"date": "2027-04-01"}\n').hexdigest()}])

    def test_a_record_with_no_outcome_is_listed_not_dropped(self):
        records, rows = _scoring_records(SHARP, WIDE, days=20)
        short = [row for row in rows if row.date <= date(2026, 10, 20)]
        with at(2027, 4, 2):
            result = score.assemble(records, short, self.splits, DAY, previous=[])
        skipped = result["skipped_records"]
        self.assertTrue(skipped)
        missing = [entry for entry in skipped if entry["reason"] == score.NO_OUTCOME]
        self.assertTrue(missing)
        have = {row.date for row in short}
        for entry in missing:
            self.assertNotIn(date.fromisoformat(entry["target_date"]), have)
        # Every (record, horizon) is either scored or listed: the two partition them.
        scored = sum(result["crps"][f"crps/h{h}"]["days"] for h in live.HORIZONS)
        self.assertEqual(scored + len(skipped), len(records) * len(live.HORIZONS))

    def test_a_target_not_before_the_scoring_date_is_listed_with_its_own_reason(self):
        records, rows = _scoring_records(SHARP, WIDE, days=20)
        late = score.skipped_records(records, rows, date(2026, 10, 12))
        reasons = {entry["reason"] for entry in late}
        self.assertIn(score.NOT_YET_DUE, reasons)

    def test_a_result_with_every_record_scored_lists_nothing_skipped(self):
        records, rows = _scoring_records(SHARP, WIDE, days=20)
        with at(2027, 4, 2):
            result = score.assemble(records, rows, self.splits, DAY, previous=[])
        self.assertEqual(result["skipped_records"], [])

    def test_the_provenance_is_carried_into_the_result_untouched(self):
        records, rows = _scoring_records(SHARP, WIDE, days=20)
        block = {"started_at_utc": "2027-04-02T15:00:00+00:00", "panel_sha256": "b" * 64}
        with at(2027, 4, 2):
            result = score.assemble(records, rows, self.splits, DAY, previous=[], provenance=block)
        self.assertEqual(result["provenance"], block)


class EventBlockTests(unittest.TestCase):
    """The Brier event cells use the horizon overlap h + 1, as the final test's do (finding 30)."""

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)

    def test_every_event_cell_uses_the_horizon_overlap(self):
        from repo_model import onset

        records, rows = _scoring_records(SHARP, WIDE, days=60)
        # A +5 bp event on every other day, so each cell clears the minimum.
        for row in rows:
            if row.date.toordinal() % 2:
                row.values["sofr"] = 4.07
        seen = []
        real = onset.paired_difference

        def spy(*args, **kwargs):
            seen.append(kwargs["block_length"])
            return real(*args, **kwargs)

        with mock.patch.object(onset, "paired_difference", spy):
            result = score.score(records, rows, self.splits, DAY)
        cells = {name: cell for name, cell in result["cells"].items() if "models" in cell and cell["models"]}
        self.assertTrue(cells, "the fixture must score at least one event cell")
        for name, cell in cells.items():
            h = int(name.rsplit("/h", 1)[1])
            for entry in cell["models"].values():
                for paired in entry["paired"].values():
                    self.assertEqual(paired["all_days"]["interval"]["block_length"], h + 1, name)

    def test_the_declared_rule_is_stated_in_the_result(self):
        records, rows = _scoring_records(SHARP, WIDE, days=20)
        with at(2027, 4, 2):
            result = score.assemble(records, rows, self.splits, DAY, previous=[])
        self.assertIn("h + 1", result["event_block_rule"])
        self.assertEqual(result["event_seed"], score.EVENT_SEED_RULE)


class GapBoundaryProvenanceTests(unittest.TestCase):
    """The gap block lists what it skipped, and its day boundaries are the pinned tree's."""

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)

    def test_a_gap_record_with_no_outcome_is_listed(self):
        gap = _gap_records(SHARP, WIDE)
        rows = _outcomes(date(2026, 8, 3), date(2026, 9, 20))
        with at(2027, 4, 2), mock.patch.object(score, "_require_scored_days_unlocked"):
            block = score.score_gap(gap, _first_live_record(), rows, self.splits, DAY)
        self.assertTrue(block["skipped_records"])
        self.assertTrue(all(entry["reason"] == score.NO_OUTCOME for entry in block["skipped_records"]))

    def test_the_boundaries_are_asserted_equal_to_the_pinned_trees(self):
        targets = score.first_live_targets(_first_live_record())
        pinned = {h: [day.isoformat() for day in score.gap_target_days(h, targets)]
                  for h in live.HORIZONS}
        score.require_gap_boundaries_equal(pinned, targets)
        pinned[1] = pinned[1][:-1]
        with self.assertRaises(ValueError):
            score.require_gap_boundaries_equal(pinned, targets)

    def test_a_pinned_tree_with_another_holiday_table_is_refused(self):
        """The pinned tree is asked for its own decision days, not main's table (finding 39)."""

        targets = score.first_live_targets(_first_live_record())
        pinned = {h: [day.isoformat() for day in score.gap_target_days(h, targets)]
                  for h in live.HORIZONS}
        pinned[2] = ["2026-09-07"] + pinned[2][1:]
        with self.assertRaisesRegex(ValueError, "pinned"):
            score.require_gap_boundaries_equal(pinned, targets)

    def test_the_pinned_tree_is_asked_for_its_own_days(self):
        """`pinned_gap_days` computes the gap with the pinned checkout's own `live_record.py`."""

        import subprocess

        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
        targets = score.first_live_targets(_first_live_record())
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / "pinned"
            subprocess.run(["git", "worktree", "add", "--quiet", "--detach", str(tree), head],
                           cwd=ROOT, check=True, capture_output=True)
            try:
                with mock.patch.object(score._pins(), "load_manifest", return_value={"current": head}):
                    days = score.pinned_gap_days(tree, targets)
                score.require_gap_boundaries_equal(days, targets)
                with mock.patch.object(score._pins(), "load_manifest",
                                       return_value={"current": "1" * 40}):
                    with self.assertRaisesRegex(ValueError, "not a checkout of the pinned code"):
                        score.pinned_gap_days(tree, targets)
            finally:
                subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT,
                               capture_output=True)


class EndToEndTests(unittest.TestCase):
    """The whole path on fixtures: verified log, archived raw root, panel built from it, result."""

    @classmethod
    def setUpClass(cls):
        from test_live_raw import raw as live_raw

        cls.raw = live_raw
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        root = Path(cls.tmp.name)
        cls.archive = root / "live-raw"
        live_raw.archive_day(FIXTURES, cls.archive, date(2026, 10, 8))
        cls.panel = root / "panel.csv"
        live_raw.build_panel(cls.archive, date(2026, 10, 8), cls.panel)
        cls.repo, cls.comments = build_log(root)
        cls.digests = save(cls.comments, root)

    def run_main(self, name, *, panel=None, extra=()):
        out = Path(self.tmp.name) / name
        argv = ["--date", "2027-10-01", "--live-dir", str(self.repo), "--digests", str(self.digests),
                "--panel", str(panel or self.panel), "--archive-dir", str(self.archive),
                "--output", str(out), *extra]
        with at(2027, 10, 1, 15, 0), mock.patch.object(score._pins(), "load_manifest",
                                                      return_value=FIXTURE_MANIFEST):
            score.main(argv)
        return json.loads(out.read_text(encoding="utf-8")), argv

    def test_the_result_carries_its_provenance(self):
        result, argv = self.run_main("one.json")
        block = result["provenance"]
        self.assertEqual(block["started_at_utc"], "2027-10-01T15:00:00+00:00")
        self.assertEqual(block["panel_sha256"], hashlib.sha256(self.panel.read_bytes()).hexdigest())
        self.assertIn("repo_model.cli build", block["panel_build_command"])
        self.assertTrue(block["panel_inputs"])
        self.assertEqual(block["scoring_command"], "scripts/live_score.py " + " ".join(argv))
        self.assertRegex(block["code_sha"], r"^[0-9a-f]{40}$")
        self.assertEqual([r["decision_day"] for r in block["live_records"]],
                         ["2026-10-05", "2026-10-06", "2026-10-07"])
        self.assertEqual(block["raw_archive"], {"archived": [],
                                                "unarchived": ["2026-10-05", "2026-10-06", "2026-10-07"]})
        self.assertFalse(result["clock"]["override"])

    def test_no_day_is_scored_and_every_record_is_listed_as_skipped(self):
        result, _ = self.run_main("two.json")
        self.assertEqual(result["headline_status"], "inconclusive")
        self.assertEqual({entry["reason"] for entry in result["skipped_records"]}, {score.NO_OUTCOME})
        self.assertEqual(len(result["skipped_records"]), 3 * len(live.HORIZONS))

    def test_a_panel_that_is_not_the_archives_is_refused(self):
        arbitrary = Path(self.tmp.name) / "arbitrary.csv"
        arbitrary.write_bytes(self.panel.read_bytes())
        out = Path(self.tmp.name) / "three.json"
        with self.assertRaises(ValueError):
            self.run_main("three.json", panel=arbitrary)
        self.assertFalse(out.exists())

    def test_a_date_that_has_not_come_is_refused_before_anything_is_read(self):
        out = Path(self.tmp.name) / "four.json"
        with at(2027, 9, 30, 15, 0):
            with self.assertRaises(LookAheadError):
                score.main(["--date", "2027-10-01", "--live-dir", str(self.repo), "--digests",
                            str(self.digests), "--panel", str(self.panel), "--archive-dir",
                            str(self.archive), "--output", str(out)])
        self.assertFalse(out.exists())

    def test_an_override_is_recorded_in_the_output(self):
        out = Path(self.tmp.name) / "five.json"
        with at(2027, 9, 30, 15, 0), mock.patch.object(score._pins(), "load_manifest",
                                                      return_value=FIXTURE_MANIFEST):
            score.main(["--date", "2027-10-01", "--live-dir", str(self.repo), "--digests",
                        str(self.digests), "--panel", str(self.panel), "--archive-dir",
                        str(self.archive), "--output", str(out), "--override-clock"])
        result = json.loads(out.read_text(encoding="utf-8"))
        self.assertTrue(result["clock"]["override"])
        self.assertEqual(result["clock"]["today_new_york"], "2027-09-30")

    def test_the_gap_scoring_date_needs_the_pinned_tree(self):
        with at(2027, 4, 2), mock.patch.object(score._pins(), "load_manifest",
                                               return_value=FIXTURE_MANIFEST):
            with self.assertRaisesRegex(ValueError, "pinned"):
                score.main(["--date", "2027-04-01", "--live-dir", str(self.repo), "--digests",
                            str(self.digests), "--panel", str(self.panel), "--archive-dir",
                            str(self.archive), "--output", str(Path(self.tmp.name) / "six.json"),
                            "--gap-dir", str(self.tmp.name)])


if __name__ == "__main__":
    unittest.main()
