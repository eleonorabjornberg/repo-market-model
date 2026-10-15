"""Prospective logging for scoring protocol v1: B1, B2, B3, registered candidates and the H7m hook (#656).

`docs/decisions/scoring-protocol.md` §11 and §12 item 2. The live record gains, from record version 3, a
`protocol` block: the 23-quantile forecast for h = 1..5 of B1 and B2, B3 as the incumbent's declared forecast,
every registered candidate (none yet), and the H7m hook. This module covers `repo_model.prospective_log` and the
record format in `scripts/live_record.py`.

**Recorded mutations** (CLAUDE.md), 13 October 2026, each in a disposable copy of the tree, CPython 3.11,
`PYTHONDONTWRITEBYTECODE=1`, applied by `sed` and confirmed by `grep`, the suite run against the copy:

1. `prospective_log.require_written_before_outcome`: the guard `if local >= published_at:` changed to `if False:`.
   `OutcomeGuardTests.test_a_record_written_after_its_outcome_is_published_is_refused` and
   `OutcomeGuardTests.test_the_block_is_refused_when_it_is_written_late` failed with
   `AssertionError: LookAheadError not raised` (the only two failures).
2. `prospective_log._b1_stand_ins`: the stand-in read `block["benchmarks"]["b1"]` changed to `block["benchmarks"]["b2"]`.
   `MissingDayTests.test_a_missing_day_is_scored_as_b1s_forecast_and_counted` failed with `AssertionError`: the
   missing day's forecast was B2's, not B1's (the only failure).
3. `prospective_log.read_h7m_estimate`: the guard `if available_at > decision_instant:` changed to `if False:`.
   `H7mHookTests.test_an_estimate_made_available_after_the_decision_is_refused` failed with
   `AssertionError: LookAheadError not raised`.
4. `prospective_log.read_h7m_estimate`: the digest comparison `if digest != pinned_sha256:` changed to `if False:`.
   `H7mHookTests.test_a_snapshot_whose_digest_is_not_the_pinned_one_is_refused` failed with
   `AssertionError: ValueError not raised`.
5. `prospective_log.require_written_by_decision_day_end` (#740), 14 October 2026, same method: the guard
   `if local >= datetime.combine(decision_day, DECISION_DAY_CUTOFF):` changed to `if False:`. Five
   `DecisionDayCutoffTests` failed with `AssertionError: LookAheadError not raised`
   (`test_a_block_written_from_23_59_on_its_decision_day_is_refused`,
   `test_a_stored_written_at_after_the_cutoff_is_refused_on_validation`, `test_filling_checks_the_commit_times`,
   `test_the_cutoff_is_read_on_the_markets_clock`, `test_the_oracle_block_of_the_finding_is_refused`).
6. `prospective_log.filled_candidate` (#740): the commit-time check `require_written_by_decision_day_end(committed_at[day], day)`
   replaced by `pass`. `DecisionDayCutoffTests.test_filling_checks_the_commit_times` failed with
   `AssertionError: LookAheadError not raised` (the only failure).
"""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from test_protocol_benchmarks import DECISION, REGISTRY, SPLITS, published_panel

from repo_model import prospective_log as pl
from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

EASTERN = ZoneInfo("America/New_York")
#: A decision day deep inside the development period, with five targets in the panel.
T = 1500


def _rows():
    return published_panel()["rows"]


def _at(day, hour, minute=0):
    return datetime.combine(day, time(hour, minute), tzinfo=EASTERN)


class OutcomeGuardTests(unittest.TestCase):
    def setUp(self):
        self.rows = _rows()
        self.dates = [row.date for row in self.rows]
        self.published = pl.outcome_published_at(self.dates, T, REGISTRY, DECISION)

    def test_the_first_outcome_is_published_after_the_decision_instant(self):
        decision = datetime.combine(self.dates[T], DECISION)
        self.assertGreater(self.published, decision)
        self.assertLess(self.published, datetime.combine(self.dates[T + 3], DECISION))

    def test_a_record_written_after_its_outcome_is_published_is_refused(self):
        aware = self.published.replace(tzinfo=EASTERN)
        pl.require_written_before_outcome(aware - timedelta(seconds=1), self.published)
        for late in (aware, aware + timedelta(seconds=1), aware + timedelta(days=3)):
            with self.assertRaises(LookAheadError):
                pl.require_written_before_outcome(late, self.published)

    def test_an_instant_with_no_zone_is_refused(self):
        with self.assertRaises(ValueError):
            pl.require_written_before_outcome(self.published - timedelta(hours=3), self.published)

    def test_the_block_is_refused_when_it_is_written_late(self):
        late = self.published.replace(tzinfo=EASTERN) + timedelta(minutes=1)
        with self.assertRaises(LookAheadError):
            pl.protocol_block(
                self.rows, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS, written_at=late
            )


class ProtocolBlockTests(unittest.TestCase):
    def setUp(self):
        self.rows = _rows()
        self.written = _at(self.rows[T].date, 17)

    def block(self, **extra):
        return pl.protocol_block(
            self.rows, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS,
            written_at=self.written, **extra
        )

    def test_b1_and_b2_are_the_benchmark_modules_forecasts(self):
        block = self.block()
        b1 = pb.b1_forecast(self.rows, T, registry=REGISTRY, decision_time=DECISION)
        b2 = pb.b2_forecast(self.rows, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS)
        self.assertEqual(block["grid"], list(sp.GRID))
        self.assertEqual(block["benchmarks"]["b1"], {str(h): b1[h] for h in sp.HORIZONS})
        self.assertEqual(block["benchmarks"]["b2"], {str(h): b2[h] for h in sp.HORIZONS})

    def test_no_candidate_is_registered_yet(self):
        block = self.block()
        self.assertEqual(block["candidates"], {})
        self.assertEqual(pl.REGISTERED_CANDIDATES, ())
        self.assertIsNone(block["h7m"])

    def test_b3_is_named_but_not_mapped_onto_the_grid(self):
        b3 = self.block()["benchmarks"]["b3"]
        self.assertFalse(b3["on_grid"])
        self.assertEqual(b3["reference"], "distributions.published.quantiles_bps")

    def test_a_candidate_is_logged_on_the_grid_at_every_lead(self):
        b1 = pb.b1_forecast(self.rows, T, registry=REGISTRY, decision_time=DECISION)
        forecast = {h: [q + 0.5 for q in b1[h]] for h in sp.HORIZONS}
        block = self.block(candidates={"cand": forecast})
        self.assertEqual(set(block["candidates"]["cand"]), {"1", "2", "3", "4", "5"})
        pl.validate_protocol_block(block)

    def test_a_candidate_off_the_grid_or_crossing_is_refused(self):
        b1 = pb.b1_forecast(self.rows, T, registry=REGISTRY, decision_time=DECISION)
        short = {h: b1[h][:-1] for h in sp.HORIZONS}
        with self.assertRaises(ValueError):
            self.block(candidates={"cand": short})
        crossing = {h: list(reversed(b1[h])) for h in sp.HORIZONS}
        with self.assertRaises(ValueError):
            self.block(candidates={"cand": crossing})
        with self.assertRaises(ValueError):
            self.block(candidates={"cand": {h: b1[h] for h in (1, 2, 3)}})

    def test_the_schema_refuses_a_malformed_block(self):
        good = self.block()
        pl.validate_protocol_block(good)
        for mutate in (
            lambda b: b.pop("grid"),
            lambda b: b["benchmarks"].pop("b2"),
            lambda b: b["benchmarks"]["b1"].pop("3"),
            lambda b: b["benchmarks"]["b1"].__setitem__("1", [0.0] * 22),
            lambda b: b.__setitem__("version", 2),
            lambda b: b.__setitem__("extra", 1),
        ):
            bad = copy.deepcopy(good)
            mutate(bad)
            with self.assertRaises(ValueError):
                pl.validate_protocol_block(bad)


class MissingDayTests(unittest.TestCase):
    """§11: a missing forecast is scored as B1's, and counted; more than 5% missing voids the registration."""

    def setUp(self):
        self.rows = _rows()
        self.days = [self.rows[t].date for t in range(T, T + 21)]
        self.blocks = {}
        for t in range(T, T + 21):
            block = pl.protocol_block(
                self.rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS,
                written_at=_at(self.rows[t].date, 17),
            )
            b1 = {int(h): q for h, q in block["benchmarks"]["b1"].items()}
            block["candidates"]["cand"] = {h: [v - 0.4 for v in q] for h, q in ((str(h), b1[h]) for h in b1)}
            self.blocks[self.rows[t].date] = block

    @staticmethod
    def commits(blocks):
        """Each logged day committed at 17:30 ET on its own decision day, as the scheduled live-log run does."""
        return {day: _at(day, 17, 30) for day in blocks}

    def test_a_missing_day_is_scored_as_b1s_forecast_and_counted(self):
        missing = self.days[7]
        blocks = copy.deepcopy(self.blocks)
        blocks[missing]["candidates"] = {}
        filled = pl.filled_candidate(blocks, "cand", self.days, committed_at=self.commits(blocks))
        self.assertEqual(filled.missing_days, (missing,))
        self.assertAlmostEqual(filled.missing_share, 1 / 21)
        b1 = {int(h): q for h, q in self.blocks[missing]["benchmarks"]["b1"].items()}
        self.assertEqual({h: list(q) for h, q in filled.forecasts[missing].items()}, b1)
        # the day scores exactly as B1 does, so the candidate cannot gain on it
        outcomes = {row.date: row.spread_bps for row in self.rows}
        calendar = [row.date for row in self.rows]
        candidate = sp.day_scores({missing: filled.forecasts[missing]}, outcomes, calendar)
        own = sp.day_scores({missing: b1}, outcomes, calendar)
        self.assertEqual(candidate, own)
        # and a day it did log is not replaced
        kept = self.days[3]
        self.assertNotEqual(
            {h: list(q) for h, q in filled.forecasts[kept].items()},
            {int(h): q for h, q in self.blocks[kept]["benchmarks"]["b1"].items()},
        )

    def test_more_than_five_percent_missing_voids_the_registration(self):
        blocks = copy.deepcopy(self.blocks)
        for day in self.days[:2]:
            blocks[day]["candidates"] = {}
        with self.assertRaises(sp.RegistrationVoid):
            pl.filled_candidate(blocks, "cand", self.days, committed_at=self.commits(blocks))

    def test_a_day_whose_block_has_no_such_candidate_is_missing(self):
        blocks = copy.deepcopy(self.blocks)
        blocks[self.days[5]]["candidates"] = {}
        filled = pl.filled_candidate(blocks, "cand", self.days, committed_at=self.commits(blocks))
        self.assertEqual(filled.missing_days, (self.days[5],))

    def test_a_decision_day_with_no_record_at_all_still_needs_b1(self):
        blocks = {day: block for day, block in self.blocks.items() if day != self.days[0]}
        with self.assertRaises(ValueError):
            pl.filled_candidate(blocks, "cand", self.days, committed_at=self.commits(blocks), b1_by_day=None)
        # B1 is a function of the panel as of that day, so it can be rebuilt for a day whose record was never written
        lost = self.days[0]
        rebuilt = {int(h): q for h, q in self.blocks[lost]["benchmarks"]["b1"].items()}
        filled = pl.filled_candidate(blocks, "cand", self.days, committed_at=self.commits(blocks), b1_by_day={lost: rebuilt})
        self.assertEqual(filled.missing_days, (lost,))
        self.assertEqual({h: list(q) for h, q in filled.forecasts[lost].items()}, rebuilt)


class DecisionDayCutoffTests(unittest.TestCase):
    """Eleonora's ruling on #740 (14 October 2026): a block is written and committed before 23:59 ET on its decision day.

    Her reading of protocol §1, not a change to it. Reads stay guarded at 16:00 by `InformationRule`.
    """

    def setUp(self):
        self.rows = _rows()
        self.day = self.rows[T].date

    def test_a_block_written_before_the_cutoff_on_its_decision_day_is_accepted(self):
        pl.require_written_by_decision_day_end(_at(self.day, 17, 30), self.day)
        pl.require_written_by_decision_day_end(_at(self.day, 23, 58), self.day)

    def test_a_block_written_from_23_59_on_its_decision_day_is_refused(self):
        for late in (_at(self.day, 23, 59), _at(self.day + timedelta(days=1), 8), _at(self.day + timedelta(days=1), 23)):
            with self.assertRaises(LookAheadError):
                pl.require_written_by_decision_day_end(late, self.day)

    def test_the_cutoff_is_read_on_the_markets_clock(self):
        utc = ZoneInfo("UTC")
        # 23:30 ET is 03:30 UTC the next day (or 04:30 in winter), still inside the cutoff
        pl.require_written_by_decision_day_end(_at(self.day, 23, 30).astimezone(utc), self.day)
        with self.assertRaises(LookAheadError):
            pl.require_written_by_decision_day_end(_at(self.day + timedelta(days=1), 0, 30).astimezone(utc), self.day)

    def test_an_instant_with_no_zone_is_refused(self):
        with self.assertRaises(ValueError):
            pl.require_written_by_decision_day_end(datetime.combine(self.day, time(12)), self.day)

    def test_the_oracle_block_of_the_finding_is_refused(self):
        """#740: written the evening after the decision day, before the 15:00 outcome instant, it was accepted."""
        evening_after = _at(self.day + timedelta(days=1), 23)
        with self.assertRaises(LookAheadError):
            pl.protocol_block(
                self.rows, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS, written_at=evening_after
            )

    def test_the_block_stores_when_it_was_written(self):
        written = _at(self.day, 17, 30)
        block = pl.protocol_block(
            self.rows, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS, written_at=written
        )
        self.assertEqual(datetime.fromisoformat(block["written_at"]), written)
        pl.validate_protocol_block(block)
        del block["written_at"]
        with self.assertRaises(ValueError):
            pl.validate_protocol_block(block)

    def test_a_stored_written_at_after_the_cutoff_is_refused_on_validation(self):
        block = pl.protocol_block(
            self.rows, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS, written_at=_at(self.day, 17)
        )
        block["written_at"] = _at(self.day + timedelta(days=1), 9).isoformat()
        with self.assertRaises(LookAheadError):
            pl.validate_protocol_block(block, decision_day=self.day)

    def test_filling_checks_the_commit_times(self):
        days = [self.rows[t].date for t in range(T, T + 21)]
        blocks = {}
        for t in range(T, T + 21):
            block = pl.protocol_block(
                self.rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS,
                written_at=_at(self.rows[t].date, 17),
            )
            b1 = {int(h): q for h, q in block["benchmarks"]["b1"].items()}
            block["candidates"]["cand"] = {str(h): q for h, q in b1.items()}
            blocks[self.rows[t].date] = block
        commits = {day: _at(day, 17, 30) for day in days}
        pl.filled_candidate(blocks, "cand", days, committed_at=commits)
        # committed the next morning: the block may have been made with the outcome in view
        late = dict(commits)
        late[days[4]] = _at(days[4] + timedelta(days=1), 9)
        with self.assertRaises(LookAheadError):
            pl.filled_candidate(blocks, "cand", days, committed_at=late)
        # a logged day with no commit time cannot be checked
        unknown = dict(commits)
        del unknown[days[4]]
        with self.assertRaises(ValueError):
            pl.filled_candidate(blocks, "cand", days, committed_at=unknown)
        # a stored written_at after the cutoff is refused even when the commit time is on time
        forged = copy.deepcopy(blocks)
        forged[days[2]]["written_at"] = _at(days[2] + timedelta(days=1), 9).isoformat()
        with self.assertRaises(LookAheadError):
            pl.filled_candidate(forged, "cand", days, committed_at=commits)


class H7mHookTests(unittest.TestCase):
    """The hook accepts a registered estimate read from a liquidity-repo snapshot pinned by digest (L-repo #20, Q4)."""

    DAY = date(2026, 10, 14)
    INSTANT = datetime.combine(DAY, time(16, 0), tzinfo=EASTERN)

    def snapshot(self, available="2026-10-14T08:00:00-04:00", day="2026-10-14"):
        rows = [
            {"day": "2026-10-13", "available_at": "2026-10-13T08:00:00-04:00",
             "deployable": 0.031, "lower": 0.020, "upper": 0.044, "state": 1},
            {"day": day, "available_at": available,
             "deployable": 0.027, "lower": 0.018, "upper": 0.040, "state": 2},
        ]
        data = (json.dumps({"estimates": rows}, sort_keys=True) + "\n").encode("utf-8")
        return data, hashlib.sha256(data).hexdigest()

    def test_nothing_is_registered_yet(self):
        self.assertEqual(pl.REGISTERED_H7M, ())

    def test_an_estimate_pinned_by_digest_and_public_at_the_decision_is_read(self):
        data, digest = self.snapshot()
        got = pl.read_h7m_estimate(data, digest, self.DAY, self.INSTANT)
        self.assertEqual(got["snapshot_sha256"], digest)
        self.assertEqual(got["day"], "2026-10-14")
        self.assertEqual(got["deployable"], 0.027)
        self.assertEqual(got["state"], 2)

    def test_a_snapshot_whose_digest_is_not_the_pinned_one_is_refused(self):
        data, digest = self.snapshot()
        with self.assertRaises(ValueError):
            pl.read_h7m_estimate(data, "0" * 64, self.DAY, self.INSTANT)
        with self.assertRaises(ValueError):
            pl.read_h7m_estimate(data + b" ", digest, self.DAY, self.INSTANT)

    def test_an_estimate_made_available_after_the_decision_is_refused(self):
        data, digest = self.snapshot(available="2026-10-14T16:00:01-04:00")
        with self.assertRaises(LookAheadError):
            pl.read_h7m_estimate(data, digest, self.DAY, self.INSTANT)
        data, digest = self.snapshot(available="2026-10-15T08:00:00-04:00")
        with self.assertRaises(LookAheadError):
            pl.read_h7m_estimate(data, digest, self.DAY, self.INSTANT)

    def test_a_snapshot_with_no_row_for_the_day_is_refused(self):
        data, digest = self.snapshot(day="2026-10-12")
        with self.assertRaises(ValueError):
            pl.read_h7m_estimate(data, digest, self.DAY, self.INSTANT)

    def test_the_estimate_joins_the_block_beside_the_benchmarks(self):
        rows = _rows()
        data, digest = self.snapshot()
        got = pl.read_h7m_estimate(data, digest, self.DAY, self.INSTANT)
        block = pl.protocol_block(
            rows, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS,
            written_at=_at(rows[T].date, 17), h7m=got,
        )
        self.assertEqual(block["h7m"], got)
        pl.validate_protocol_block(block)


if __name__ == "__main__":
    unittest.main()
