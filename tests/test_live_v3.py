"""The protocol block joins the live record at record version 3 (#656).

The daily file gains `protocol` (`repo_model.prospective_log`: B1, B2, B3's note, registered candidates, the H7m
hook); every field a version 1 or 2 file has is written as before, past files still validate and score, and the new
block is a separate, labelled addition. This module covers the record format and `live_record.protocol_for`.
The block's own guards are in `tests/test_prospective_log.py`.

**Recorded mutations** (CLAUDE.md), 13 October 2026, each in a disposable copy of the tree, CPython 3.11,
`PYTHONDONTWRITEBYTECODE=1`, applied by `sed` and confirmed by `grep`:

1. `live_record.validate_record`: the check `if (record["record_version"] == RECORD_VERSION_V3) != ("protocol" in record):`
   changed to `if False:`. `RecordSchemaTests.test_a_version_3_file_without_the_block_is_refused` and
   `RecordSchemaTests.test_a_block_on_an_older_version_is_refused` failed with `AssertionError: ValueError not raised`.
2. `live_record.protocol_for`: the argument `written_at=written_at` changed to
   `written_at=written_at.replace(year=1999)`. `ProtocolForTests.test_a_record_made_after_its_outcome_is_refused`
   failed with `AssertionError: LookAheadError not raised`.
"""

import copy
import json
import unittest
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from test_live_record import _record, live, setUpModule, tearDownModule  # noqa: F401
from test_live_v2 import _record_v2
from test_protocol_benchmarks import DECISION, REGISTRY, SPLITS, published_panel

from repo_model import prospective_log as pl
from repo_model.data import CALENDAR_COLUMN_RULES, DailyObservation
from repo_model.splits import LookAheadError

EASTERN = ZoneInfo("America/New_York")
T = 1500


def _protocol_block():
    rows = published_panel()["rows"]
    return pl.protocol_block(
        rows, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS,
        written_at=datetime.combine(rows[T].date, time(17, 0), tzinfo=EASTERN),
    )


def _record_v3(day="2026-10-02"):
    record = _record_v2(day)
    record["record_version"] = live.RECORD_VERSION_V3
    record["protocol"] = _protocol_block()
    return record


class RecordSchemaTests(unittest.TestCase):
    def test_versions_1_2_and_3_all_validate(self):
        live.validate_record(_record())
        live.validate_record(_record_v2())
        live.validate_record(_record_v3())

    def test_the_versions(self):
        self.assertEqual((live.RECORD_VERSION, live.RECORD_VERSION_V2, live.RECORD_VERSION_V3), (1, 2, 3))
        self.assertEqual(live.READABLE_VERSIONS, (1, 2, 3))

    def test_a_version_3_file_without_the_block_is_refused(self):
        record = _record_v3()
        del record["protocol"]
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_a_block_on_an_older_version_is_refused(self):
        for record in (_record(), _record_v2()):
            record["protocol"] = _protocol_block()
            with self.assertRaises(ValueError):
                live.validate_record(record)

    def test_a_version_3_file_still_carries_pressure_model_v2(self):
        record = _record_v3()
        del record["distributions"]["published_v2"]
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_a_malformed_block_is_refused(self):
        record = _record_v3()
        record["protocol"]["benchmarks"]["b1"]["2"] = [0.0] * 5
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_every_field_an_older_file_has_is_written_as_before(self):
        v2, v3 = _record_v2(), _record_v3()
        stripped = copy.deepcopy(v3)
        del stripped["protocol"]
        stripped["record_version"] = live.RECORD_VERSION_V2
        self.assertEqual(live.record_bytes(stripped), live.record_bytes(v2))

    def test_the_bytes_are_deterministic_json(self):
        record = _record_v3()
        self.assertEqual(json.loads(live.record_bytes(record).decode("utf-8")), record)


def _placeholder(day, last):
    """What `extend_panel` appends: the calendar columns only, and the last real row's spread."""

    values = {"sofr": last["sofr"], "iorb": last["iorb"]}
    for column, rule in CALENDAR_COLUMN_RULES.items():
        if column in live.CALENDAR_COLUMNS:
            values[column] = rule(day)
    return DailyObservation(date=day, values=values)


class ProtocolForTests(unittest.TestCase):
    """`live_record.protocol_for` on the panel as the live run has it: real rows to the day before, then placeholders."""

    def setUp(self):
        self.full = published_panel()["rows"]
        self.real = self.full[:T]
        self.day = self.full[T].date
        # the live run's extended panel: the real rows, then the decision day and five targets as placeholders
        self.extended = list(self.real) + [_placeholder(row.date, self.real[-1].values) for row in self.full[T:T + 6]]
        self.written = datetime.combine(self.day, time(16, 40), tzinfo=EASTERN)

    def test_the_block_reads_nothing_off_a_placeholder(self):
        live_block = live.protocol_for(
            self.extended, self.day, REGISTRY, SPLITS, self.written
        )
        full_block = pl.protocol_block(
            self.full, T, registry=REGISTRY, decision_time=DECISION, splits=SPLITS, written_at=self.written
        )
        self.assertEqual(live_block, full_block)

    def test_no_candidate_is_logged_until_one_is_registered(self):
        self.assertEqual(live.protocol_for(self.extended, self.day, REGISTRY, SPLITS, self.written)["candidates"], {})

    def test_a_record_made_after_its_outcome_is_refused(self):
        published = pl.outcome_published_at([r.date for r in self.extended], T, REGISTRY, DECISION)
        late = published.replace(tzinfo=EASTERN) + timedelta(minutes=5)
        with self.assertRaises(LookAheadError):
            live.protocol_for(self.extended, self.day, REGISTRY, SPLITS, late)


if __name__ == "__main__":
    unittest.main()
