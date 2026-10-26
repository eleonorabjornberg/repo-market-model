"""Per-field staleness and imputation flags join the live record at record version 4 (#1132, from #984 part 4).

The daily file gains `field_flags` (`repo_model.field_flags`); every field a version 1, 2 or 3 file has is written as
before, past files still validate and score, and the new block is a separate, labelled addition. This module covers the
record format and `live_record.field_flags_for`. The block's own guards are in `tests/test_field_flags.py`. Nothing
here moves the live pin: the new version reaches the live record only when Eleonora's own `GO` moves it
(`docs/research/live-record-v4-draft-1132.md`).

**Recorded mutations** (CLAUDE.md), 22 October 2026, each in a disposable copy of the tree, CPython 3.11, applied by
`sed` and confirmed by `grep`:

1. `live_record.validate_record`: the check `if (record["record_version"] == RECORD_VERSION_V4) != ("field_flags" in record):`
   changed to `if False:`. `RecordSchemaTests.test_a_version_4_file_without_the_block_is_refused` failed with
   `AssertionError: ValueError not raised` (and `test_a_block_on_an_older_version_is_refused` with the same).
2. `live_record.field_flags_for`: the term `V1_FEATURES[h]` changed to `V1_FEATURES[1]`. `FieldFlagsForTests.test_the_block_is_the_one_the_forecasts_read`
   errored with `LookAheadError` (`field_flags.flag_read` refused the h = 1 settlement read at h = 2, first observable after the decision).
"""

import copy
import json
import unittest
from datetime import time

from test_field_flags import FEATURES, _extended
from test_live_record import _record, live, setUpModule, tearDownModule  # noqa: F401
from test_live_v2 import _record_v2
from test_live_v3 import REGISTRY, _record_v3

from repo_model import field_flags as ff

DECISION = time(16, 0)


def _flags():
    return ff.field_flags_block(
        {h: _extended(h) for h in (1, 2)}, {h: FEATURES for h in (1, 2)}, registry=REGISTRY, decision_time=DECISION
    )


def _record_v4(day="2026-10-02"):
    record = _record_v3(day)
    record["record_version"] = live.RECORD_VERSION_V4
    record["field_flags"] = _flags()
    return record


class RecordSchemaTests(unittest.TestCase):
    def test_versions_1_to_4_all_validate(self):
        for record in (_record(), _record_v2(), _record_v3(), _record_v4()):
            live.validate_record(record)

    def test_the_versions(self):
        self.assertEqual(live.RECORD_VERSION_V4, 4)
        self.assertEqual(live.READABLE_VERSIONS, (1, 2, 3, 4))
        self.assertIn(live.RECORD_VERSION_V4, live.V2_VERSIONS)

    def test_a_version_4_file_without_the_block_is_refused(self):
        record = _record_v4()
        del record["field_flags"]
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_a_block_on_an_older_version_is_refused(self):
        for record in (_record(), _record_v2(), _record_v3()):
            record["field_flags"] = _flags()
            with self.assertRaises(ValueError):
                live.validate_record(record)

    def test_a_version_4_file_still_carries_the_protocol_block(self):
        record = _record_v4()
        del record["protocol"]
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_a_malformed_block_is_refused(self):
        record = _record_v4()
        record["field_flags"]["horizons"]["1"]["spread_bps"]["imputed"] = "no"
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_every_field_an_older_file_has_is_written_as_before(self):
        v3, v4 = _record_v3(), _record_v4()
        stripped = copy.deepcopy(v4)
        del stripped["field_flags"]
        stripped["record_version"] = live.RECORD_VERSION_V3
        self.assertEqual(live.record_bytes(stripped), live.record_bytes(v3))

    def test_the_bytes_are_deterministic_json(self):
        record = _record_v4()
        self.assertEqual(json.loads(live.record_bytes(record).decode("utf-8")), record)


class FieldFlagsForTests(unittest.TestCase):
    """`live_record.field_flags_for` on extended panels as the live run has them."""

    def test_the_block_is_the_one_the_forecasts_read(self):
        extended = {h: (_extended(h), []) for h in live.HORIZONS}
        block = live.field_flags_for(extended, REGISTRY)
        self.assertEqual(set(block["horizons"]), {str(h) for h in live.HORIZONS})
        for h in live.HORIZONS:
            expected = set(live.V1_FEATURES[h]) | set(live.CALENDAR_FEATURES) | {"spread_bps"} | set(live.published_features(h))
            self.assertEqual(set(block["horizons"][str(h)]), expected)
        direct = ff.field_flags_block(
            {h: extended[h][0] for h in live.HORIZONS},
            {h: live.V1_FEATURES[h] + live.CALENDAR_FEATURES + ("spread_bps",) + live.published_features(h) for h in live.HORIZONS},
            registry=REGISTRY, decision_time=live.DECISION,
        )
        self.assertEqual(block, direct)


if __name__ == "__main__":
    unittest.main()
