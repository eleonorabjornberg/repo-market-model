"""The live scorer scores through the lockbox, and a scoring date opens only the days before it (#277).

Eleonora's ruling on #269 item 6: one lockbox mechanism. Before this, live scoring
was gated on a heading in `docs/decisions/lockbox.md`, so once a scoring date had
passed the blind tier would still have read `opened: null` while its results were
public. Now `scripts/live_score.py` calls `lockbox.require_unlocked` for every day
it scores, and `lockbox.split_tier` is the mechanism that opens only the part of
`blind` before a scoring date. It returns a new declaration and writes nothing:
opening a tier is owner-attested (#256) and stays Eleonora's own action.

What is held here:

* a locked scored day raises `LookAheadError` in `score_crps`, `score`, the gap
  block and `assemble`, before any cell is computed (`LiveScoringGuardTests`);
* the tracked declaration still locks every live day, so the scorer refuses the
  real record's days until she opens them (`TrackedDeclarationTests`);
* `split_tier` opens the days before a date and no other, validates its inputs,
  and returns a declaration `load_lockbox` accepts (`SplitTierTests`);
* after a split every caller of `require_unlocked` agrees with it: the live scorer,
  the library guard and the greyed-days reader see the same open and locked days
  (`CallersAgreeTests`), and no script reads the lockbox through a heading in
  `lockbox.md` (`NoHeadingGateTests`).

Recorded mutation (item 1, the new guard): in `scripts/live_score.py`, the body of
`_require_scored_days_unlocked` (`require_unlocked([date.fromisoformat(str(day)) for
day in days], where=where)`) replaced by `pass`. Killed, with `AssertionError:
LookAheadError not raised`: `LiveScoringGuardTests.test_a_locked_day_is_refused_by_every_scoring_function`
(its `score_crps`, `score` and `assemble` subtests), `test_a_split_opens_the_days_before_the_scoring_date_and_only_those`,
`test_the_gap_block_is_guarded_too` and `CallersAgreeTests`. The original restored, all
pass.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from repo_model import lockbox
from repo_model.data import DataContractError
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

from test_live_gap import SHARP, WIDE, _first_live_record, _gap_records, _outcomes
from test_live_record import _scoring_records

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TRACKED = ROOT / "metadata" / "lockbox.json"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
RULING = "https://example.invalid/ruling"


def _script(name):
    spec = importlib.util.spec_from_file_location(f"live_lockbox_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


score = _script("live_score")


def _tracked():
    return json.loads(TRACKED.read_text(encoding="utf-8"))


def _declare(directory, declaration):
    path = Path(directory) / "lockbox.json"
    path.write_text(json.dumps(declaration, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


class SplitTierTests(unittest.TestCase):
    """`split_tier` opens the blind tier before a scoring date and nothing else."""

    def split(self, before=date(2027, 4, 1), tier="blind", declaration=None):
        return lockbox.split_tier(
            declaration or _tracked(), tier, before,
            opened_on=date(2027, 4, 1), ruling=RULING,
        )

    def test_it_opens_the_days_before_the_date_and_locks_the_rest(self):
        result = self.split()
        with tempfile.TemporaryDirectory() as tmp:
            tiers = lockbox.load_lockbox(_declare(tmp, result))
        self.assertEqual(
            [(tier.name, tier.start, tier.end, tier.opened is None) for tier in tiers],
            [
                ("near_blind", date(2026, 1, 1), date(2026, 9, 3), False),
                ("blind_2026-09-04_to_2027-03-31", date(2026, 9, 4), date(2027, 3, 31), False),
                ("blind", date(2027, 4, 1), None, True),
            ],
        )
        self.assertEqual(tiers[1].opened, (date(2027, 4, 1), RULING))

    def test_the_input_is_not_changed_and_the_near_blind_tier_is_untouched(self):
        declaration = _tracked()
        before = json.dumps(declaration, sort_keys=True)
        result = self.split(declaration=declaration)
        self.assertEqual(json.dumps(declaration, sort_keys=True), before)
        self.assertEqual(result["tiers"][0], declaration["tiers"][0])

    def test_the_remainder_keeps_its_name_so_it_can_be_split_again(self):
        first = self.split()
        second = lockbox.split_tier(
            first, "blind", date(2027, 10, 1), opened_on=date(2027, 10, 1), ruling=RULING
        )
        with tempfile.TemporaryDirectory() as tmp:
            tiers = lockbox.load_lockbox(_declare(tmp, second))
        self.assertEqual(
            [(tier.start, tier.end, tier.opened is None) for tier in tiers[1:]],
            [
                (date(2026, 9, 4), date(2027, 3, 31), False),
                (date(2027, 4, 1), date(2027, 9, 30), False),
                (date(2027, 10, 1), None, True),
            ],
        )

    def test_a_split_that_would_open_nothing_or_everything_is_refused(self):
        for day in (date(2026, 9, 4), date(2026, 9, 3), date(2026, 1, 1)):
            with self.subTest(before=day), self.assertRaises(ValueError):
                self.split(before=day)

    def test_a_tier_that_is_already_opened_or_unknown_is_refused(self):
        with self.assertRaises(ValueError):
            self.split(tier="near_blind", before=date(2026, 6, 1))
        with self.assertRaises(ValueError):
            self.split(tier="no_such_tier")

    def test_a_bounded_tier_needs_a_date_inside_it(self):
        declaration = _tracked()
        declaration["tiers"][1]["end"] = "2027-12-31"
        with self.assertRaises(ValueError):
            self.split(before=date(2028, 1, 1), declaration=declaration)
        self.assertEqual(self.split(before=date(2027, 12, 31), declaration=declaration)["tiers"][2]["start"],
                         "2027-12-31")

    def test_a_ruling_is_required(self):
        for ruling in ("", "   "):
            with self.subTest(ruling=ruling), self.assertRaises(DataContractError):
                lockbox.split_tier(_tracked(), "blind", date(2027, 4, 1),
                                   opened_on=date(2027, 4, 1), ruling=ruling)

    def test_the_helper_does_not_write_the_tracked_declaration(self):
        before = TRACKED.read_bytes()
        self.split()
        self.assertEqual(TRACKED.read_bytes(), before)

    def test_the_rendering_matches_the_tracked_file_format(self):
        self.assertEqual(lockbox.render_declaration(_tracked()), TRACKED.read_text(encoding="utf-8"))


class LiveScoringGuardTests(unittest.TestCase):
    """The scorer refuses a locked day, and scores the days a split has opened."""

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)
        cls.records, cls.rows = _scoring_records(
            [0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0]
        )
        cls.day = date(2027, 4, 1)

    def under(self, declaration):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return mock.patch.object(lockbox, "DEFAULT_LOCKBOX", _declare(directory.name, declaration))

    def test_a_locked_day_is_refused_by_every_scoring_function(self):
        calls = {
            "score_crps": lambda: score.score_crps(self.records, self.rows, self.splits, self.day),
            "score": lambda: score.score(self.records, self.rows, self.splits, self.day),
            "assemble": lambda: score.assemble(self.records, self.rows, self.splits, self.day, previous=[]),
        }
        # The tracked declaration: the blind tier, which holds every logged day, is locked.
        for name, call in calls.items():
            with self.subTest(function=name):
                with self.assertRaises(LookAheadError) as caught:
                    call()
                self.assertIn("locked blind tier", str(caught.exception))
                self.assertIn("2026-10-", str(caught.exception))

    def test_a_split_opens_the_days_before_the_scoring_date_and_only_those(self):
        split = lockbox.split_tier(_tracked(), "blind", date(2026, 11, 2),
                                   opened_on=date(2026, 11, 2), ruling=RULING)
        with self.under(split):
            # Scoring on a date inside the opened part scores every target before it.
            cell = score.score_crps(self.records, self.rows, self.splits, date(2026, 11, 2))["crps/h1"]
            self.assertGreater(cell["days"], 0)
            # A later date reaches target days the split left locked.
            with self.assertRaises(LookAheadError) as caught:
                score.score_crps(self.records, self.rows, self.splits, self.day)
            self.assertIn("scored day 2026-11-02", str(caught.exception))

    def test_every_logged_day_scores_once_the_tier_is_opened_through_it(self):
        split = lockbox.split_tier(_tracked(), "blind", date(2100, 1, 1),
                                   opened_on=date(2100, 1, 1), ruling=RULING)
        with self.under(split):
            result = score.assemble(self.records, self.rows, self.splits, self.day, previous=[])
        self.assertEqual(result["headline_status"], "headline_verdict")

    def test_the_gap_block_is_guarded_too(self):
        """A gap day is scored through the same guard: the tracked declaration refuses it."""

        records = _gap_records(SHARP, WIDE)
        rows = _outcomes(date(2026, 8, 3), date(2026, 12, 31))
        with self.assertRaises(LookAheadError):
            score.score_gap(records, _first_live_record(), rows, self.splits, date(2027, 4, 1))


class TrackedDeclarationTests(unittest.TestCase):
    def test_the_tracked_declaration_still_locks_the_blind_tier(self):
        """This PR opens nothing: opening is owner-attested (#256)."""

        tiers = lockbox.load_lockbox(TRACKED)
        self.assertEqual([(tier.name, tier.opened is None) for tier in tiers],
                         [("near_blind", False), ("blind", True)])

    def test_the_real_scorer_refuses_the_first_logged_day_under_it(self):
        with self.assertRaises(LookAheadError):
            lockbox.require_unlocked([date(2026, 10, 5)], where="live_score")


class CallersAgreeTests(unittest.TestCase):
    """After a split, the library guard, the live scorer and the page reader agree (item 4)."""

    @classmethod
    def setUpClass(cls):
        cls.opened_day = date(2026, 11, 1)
        cls.locked_day = date(2026, 11, 2)
        cls.declaration = lockbox.split_tier(_tracked(), "blind", cls.locked_day,
                                             opened_on=cls.locked_day, ruling=RULING)

    def test_every_caller_reads_the_same_open_and_locked_days(self):
        splits = load_split_declaration(SPLITS)
        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        with tempfile.TemporaryDirectory() as tmp:
            path = _declare(tmp, self.declaration)
            with mock.patch.object(lockbox, "DEFAULT_LOCKBOX", path):
                locked = lockbox.locked_tiers(path)
                self.assertEqual([tier.name for tier in locked], ["blind"])
                self.assertIsNone(lockbox.locked_tier(self.opened_day, locked))
                self.assertIsNotNone(lockbox.locked_tier(self.locked_day, locked))
                lockbox.require_unlocked([self.opened_day], where="library")
                with self.assertRaises(LookAheadError):
                    lockbox.require_unlocked([self.locked_day], where="library")
                # The live scorer: a scoring date at the split scores the opened days.
                score.score_crps(records, rows, splits, self.locked_day)
                # A date past it reaches the locked day, and the same guard refuses it.
                with self.assertRaises(LookAheadError):
                    score.score_crps(records, rows, splits, date(2026, 11, 3))


class NoHeadingGateTests(unittest.TestCase):
    """The lockbox is read through `lockbox.json` only (item 3)."""

    def test_the_live_scripts_do_not_read_a_heading_in_lockbox_md(self):
        for name in ("live_score", "live_gap"):
            text = (SCRIPTS / f"{name}.py").read_text(encoding="utf-8")
            with self.subTest(script=name):
                self.assertNotIn("AMENDMENT_HEADING", text)
                self.assertNotIn("require_amendment", text)
                self.assertNotIn('"lockbox.md"', text)
        self.assertFalse(hasattr(score, "require_amendment"))
        self.assertFalse(hasattr(score, "AMENDMENT_HEADING"))

    def test_the_live_scorer_calls_the_shared_guard(self):
        text = (SCRIPTS / "live_score.py").read_text(encoding="utf-8")
        self.assertIn("require_unlocked", text)


if __name__ == "__main__":
    unittest.main()
