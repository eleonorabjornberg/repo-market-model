"""Pressure model v2 is logged alongside the unchanged v1 (#245).

The daily file gains `distributions.published_v2` (record version 2); every field v1
writes is written as before, past files still score, and v2's cells are a separate,
labelled block that never reaches v1's verdict.

Mutation record (#245), each in a disposable copy:

* `live_score.v2_crps`: the guard `if not v2_logged(record): raise ValueError(...)` changed to
  `if False:`. `test_v2_is_never_scored_on_a_day_it_was_not_logged` failed, `AssertionError`
  (the message did not name the day as not logged with v2; the file-level error took its place).
* `live_score.score_v2`: the selection `logged = [record for record in records if v2_logged(record)]` changed
  to `logged = list(records)`. `test_only_the_days_v2_was_logged_are_scored` errored, `ValueError`
  (a pre-v2 day reached `v2_crps`).
* `live_score.score_v2`: the `_require_scored_days_unlocked(days, where="live_score.score_v2")` call
  deleted. `test_a_scored_day_in_a_locked_tier_is_refused` failed, `AssertionError`
  (`LookAheadError not raised`).
* `live_record._validate_distributions`: the `if version == RECORD_VERSION_V2:` call of `_validate_v2`
  deleted. `test_each_malformed_v2_block_is_refused` failed, `AssertionError` (`ValueError not raised`).
"""

import copy
import json
import unittest
from datetime import date

from test_live_record import _record, _scoring_records, _script, live, score, SPLITS  # noqa: F401
from test_live_record import setUpModule, tearDownModule  # noqa: F401

from repo_model.contract import QUANTILE_LEVELS
from repo_model.evaluation_splits import load_split_declaration

V2 = [0.6, 0.9, 1.0, 1.1, 1.4]


def _v2_block(quantiles=None):
    return {
        "records": {"1": live.V2_RECORD},
        "declaration_sha256": {"1": "5" * 64},
        "quantiles_bps": {"1": list(quantiles or V2)},
    }


def _record_v2(day="2026-10-02", quantiles=None):
    record = _record(day)
    record["record_version"] = live.RECORD_VERSION_V2
    record["distributions"]["published_v2"] = _v2_block(quantiles)
    return record


class RecordSchemaTests(unittest.TestCase):
    def test_a_version_1_file_and_a_version_2_file_both_validate(self):
        live.validate_record(_record())
        live.validate_record(_record_v2())

    def test_a_version_2_file_without_v2_is_refused(self):
        record = _record()
        record["record_version"] = live.RECORD_VERSION_V2
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_a_version_1_file_with_v2_is_refused(self):
        record = _record()
        record["distributions"]["published_v2"] = _v2_block()
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_each_malformed_v2_block_is_refused(self):
        def edit(change):
            record = _record_v2()
            change(record["distributions"]["published_v2"])
            return record

        cases = {
            "another record": lambda b: b["records"].update({"1": "docs/runs/other.json"}),
            "a missing digest": lambda b: b["declaration_sha256"].clear(),
            "a short digest": lambda b: b["declaration_sha256"].update({"1": "5" * 10}),
            "another horizon": lambda b: b["quantiles_bps"].update({"2": list(V2)}),
            "a short vector": lambda b: b["quantiles_bps"].update({"1": [0.0, 1.0]}),
            "not a number": lambda b: b["quantiles_bps"]["1"].__setitem__(1, None),
            "an extra key": lambda b: b.update({"extra": 1}),
        }
        for name, change in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(ValueError):
                    live.validate_record(edit(change))

    def test_the_format_version_is_bumped_and_v1s_is_kept(self):
        self.assertEqual(live.RECORD_VERSION, 1)
        self.assertEqual(live.RECORD_VERSION_V2, 2)


class V1UnchangedTests(unittest.TestCase):
    """Both versions on the same inputs: v1's distributions and every other field are identical."""

    LEVELS = list(QUANTILE_LEVELS)

    @staticmethod
    def _forecast(rows, h, registry):
        return {"levels": list(QUANTILE_LEVELS), "published": [-2.0, 0.0, 1.0, 2.0, 5.0 + h],
                "persistence": [-4.0, -1.0, 1.0, 3.0, 8.0 + h]}

    @staticmethod
    def _v2_forecast(rows, registry):
        return {"levels": list(QUANTILE_LEVELS), "quantiles": list(V2), "declaration_sha256": "6" * 64}

    def test_v1s_block_is_byte_identical_with_and_without_v2(self):
        from unittest import mock

        extended = {h: ([], []) for h in live.HORIZONS}
        with mock.patch.object(live, "published_declaration_sha256", return_value="4" * 64):
            both = live.distributions_block(
                extended, {}, forecast=self._forecast, v2_forecast=self._v2_forecast)
        without = {key: value for key, value in both.items() if key != "published_v2"}
        self.assertEqual(set(both) - set(without), {"published_v2"})
        # What v1 wrote before this change: exactly levels, published and persistence.
        self.assertEqual(set(without), {"levels", "published", "persistence"})
        self.assertEqual(without["published"]["quantiles_bps"]["3"], [-2.0, 0.0, 1.0, 2.0, 8.0])
        self.assertEqual(both["published_v2"]["quantiles_bps"], {"1": list(V2)})
        self.assertEqual(both["published_v2"]["records"], {"1": live.V2_RECORD})

    def test_the_file_bytes_differ_only_by_the_version_and_the_v2_block(self):
        v1 = _record()
        v2 = _record_v2()
        stripped = copy.deepcopy(v2)
        del stripped["distributions"]["published_v2"]
        stripped["record_version"] = live.RECORD_VERSION
        self.assertEqual(live.record_bytes(stripped), live.record_bytes(v1))

    def test_v2s_forecast_is_asked_only_at_its_horizon(self):
        from unittest import mock

        asked = []

        def v2_forecast(rows, registry):
            asked.append(rows)
            return self._v2_forecast(rows, registry)

        extended = {h: ([h], []) for h in live.HORIZONS}
        with mock.patch.object(live, "published_declaration_sha256", return_value="4" * 64):
            live.distributions_block(extended, {}, forecast=self._forecast, v2_forecast=v2_forecast)
        self.assertEqual(asked, [[1]])


def _with_v2(records, quantiles, first=0):
    """`records` with v2 logged from the `first`th record on; the rest are pre-v2 (version 1) files."""

    out = []
    for position, record in enumerate(records):
        record = copy.deepcopy(record)
        if position >= first:
            record["record_version"] = live.RECORD_VERSION_V2
            record["distributions"]["published_v2"] = _v2_block(quantiles)
        out.append(record)
    return out


class ScoringTests(unittest.TestCase):
    DAY = date(2027, 4, 1)
    PUBLISHED = [0.5, 0.8, 1.0, 1.2, 1.5]
    PERSISTENCE = [-6.0, -2.0, 1.0, 4.0, 9.0]

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)
        cls.records, cls.rows = _scoring_records(cls.PUBLISHED, cls.PERSISTENCE)

    def test_past_files_still_score(self):
        for record in self.records:
            live.validate_record(record)
        result = score.assemble(self.records, self.rows, self.splits, self.DAY, previous=[],
                                gap_records=None)
        self.assertGreater(result["crps"]["crps/h1"]["days"], 0)
        self.assertNotIn("v2", result)

    def test_a_v2_cell_scores_from_the_file_alone(self):
        from repo_model.metrics import crps_from_quantiles

        record = _record_v2()
        for outcome in (-3.0, 0.0, 1.4, 12.0):
            self.assertEqual(score.v2_crps(record, outcome),
                             crps_from_quantiles(list(QUANTILE_LEVELS), V2, outcome))

    def test_v2_is_never_scored_on_a_day_it_was_not_logged(self):
        with self.assertRaises(ValueError) as caught:
            score.v2_crps(_record(), 1.0)
        self.assertIn("not logged with pressure model v2", str(caught.exception))

    def test_only_the_days_v2_was_logged_are_scored(self):
        records = _with_v2(self.records, self.PUBLISHED, first=10)
        block = score.score_v2(records, self.rows, self.splits, self.DAY)
        self.assertEqual(block["first_logged_day"], records[10]["decision_day"])
        self.assertEqual(len(block["logged_days"]), len(records) - 10)
        self.assertLessEqual(block["crps/h1"]["days"], len(records) - 10)
        self.assertGreater(block["crps/h1"]["days"], 0)
        self.assertEqual(block["v2_vs_v1/h1"]["days"], block["crps/h1"]["days"])
        self.assertGreaterEqual(block["crps/h1"]["first"], records[10]["targets"][0]["target_date"])

    def test_a_sharper_v2_passes_under_the_final_tests_rule(self):
        records = _with_v2(self.records, self.PUBLISHED)
        block = score.score_v2(records, self.rows, self.splits, self.DAY)
        cell = block["crps/h1"]
        self.assertGreater(cell["mean_difference_bps"], 0)
        self.assertEqual(cell["verdict"], score.crps_verdict(cell))
        self.assertEqual(cell["result"], "pass")
        self.assertEqual(cell["role"], "primary (v2)")
        self.assertEqual(cell["interval"]["level"], score.onset.LEVEL)
        self.assertEqual(cell["interval"]["replications"], score.onset.REPLICATIONS)
        self.assertIn("by_regime", cell)
        self.assertIn("by_day_type", cell)

    def test_a_worse_v2_is_labelled_worse(self):
        records = _with_v2(self.records, [-9.0, -4.0, 0.0, 6.0, 14.0])
        cell = score.score_v2(records, self.rows, self.splits, self.DAY)["crps/h1"]
        self.assertLess(cell["mean_difference_bps"], 0)
        self.assertNotEqual(cell["result"], "pass")

    def test_v2_against_v1_is_reported_only_and_has_no_verdict(self):
        records = _with_v2(self.records, self.PUBLISHED)
        against = score.score_v2(records, self.rows, self.splits, self.DAY)["v2_vs_v1/h1"]
        self.assertEqual(against["role"], "reported only")
        self.assertNotIn("verdict", against)
        self.assertNotIn("result", against)
        # v2 equals v1's published distribution here, so the paired difference is zero.
        self.assertEqual(against["mean_difference_bps"], 0.0)

    def test_v1s_cells_verdict_and_status_do_not_move_when_v2_is_logged(self):
        plain = score.assemble(self.records, self.rows, self.splits, self.DAY, previous=[])
        for quantiles in (self.PUBLISHED, [-9.0, -4.0, 0.0, 6.0, 14.0]):
            logged = score.assemble(_with_v2(self.records, quantiles), self.rows, self.splits,
                                    self.DAY, previous=[])
            with self.subTest(quantiles=quantiles):
                self.assertEqual({k: v for k, v in logged.items() if k != "v2"}, plain)
                self.assertIn("v2", logged)
        self.assertNotIn("v2", plain)

    def test_v2s_block_is_labelled_and_separate(self):
        logged = score.assemble(_with_v2(self.records, self.PUBLISHED), self.rows, self.splits,
                                self.DAY, previous=[])
        self.assertEqual(logged["v2"]["label"], score.V2_LABEL)
        self.assertIn("never enters v1's verdict", score.V2_LABEL)
        self.assertEqual(logged["v2"]["headline_status"], "headline_verdict")

    def test_v2s_verdict_is_fixed_once_at_its_first_scoring_date(self):
        records = _with_v2(self.records, self.PUBLISHED)
        first = score.assemble(records, self.rows, self.splits, self.DAY, previous=[])
        later = score.assemble(records, self.rows, self.splits, date(2027, 10, 1), previous=[first])
        self.assertEqual(first["v2"]["headline_status"], "headline_verdict")
        self.assertEqual(later["v2"]["headline_status"], "update")

    def test_a_scored_day_in_a_locked_tier_is_refused(self):
        from unittest import mock

        from repo_model.splits import LookAheadError

        records = _with_v2(self.records, self.PUBLISHED)
        seen = []

        def refuse(days, *, where):
            seen.append((list(days), where))
            raise LookAheadError("locked")

        with mock.patch.object(score, "_require_scored_days_unlocked", refuse):
            with self.assertRaises(LookAheadError):
                score.score_v2(records, self.rows, self.splits, self.DAY)
        self.assertTrue(seen[0][0])
        self.assertIn("score_v2", seen[0][1])

    def test_the_draft_amendment_covers_v2(self):
        text = (score.REPO / "docs" / "decisions" / "drafts" / "lockbox-live-record.md").read_text(
            encoding="utf-8")
        for phrase in ("pressure model v2", "FIRST_SCORING_DATES", "2018–2025", "#243"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()


class V2AgreementTests(unittest.TestCase):
    """The daily script's v2 vector is the one v2's walk published for that target day.

    The fixture panel is cut at 2019-03-15 and the daily script's v2 forecast is made at the
    decision day 2019-03-01 (target 2019-03-04, h = 1), on the panel cut the day before and
    extended by placeholders. `docs/runs/pressure_model_v2_distribution_h1.json` holds v2's
    walk vector for 2019-03-04, from the full walk; the two agree.
    """

    DECISION_DAY = date(2019, 3, 1)
    LAST_ROW = date(2019, 3, 15)

    @classmethod
    def setUpClass(cls):
        import tempfile
        from pathlib import Path

        from test_live_record import REGISTRY, _auctions, _fixture_panel
        from repo_model.data import load_daily_panel

        cls.tmp = tempfile.mkdtemp()
        panel, pit = _fixture_panel(cls.tmp)
        lines = panel.read_text(encoding="utf-8").splitlines(keepends=True)
        column = lines[0].rstrip("\r\n").split(",").index("date")
        short = Path(cls.tmp) / "short.csv"
        short.write_text(lines[0] + "".join(
            line for line in lines[1:]
            if date.fromisoformat(line.split(",")[column]) <= cls.LAST_ROW), encoding="utf-8")
        rows = load_daily_panel(short)
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cut = [row for row in rows if row.date < cls.DECISION_DAY]
        cls.extended, cls.targets = live.extend_panel(cut, cls.DECISION_DAY, 1, pit, _auctions())
        cls.got = live.v2_distribution_forecast(cls.extended, cls.registry)
        cls.again = live.v2_distribution_forecast(cls.extended, cls.registry)

    @classmethod
    def tearDownClass(cls):
        import shutil

        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_it_is_the_walks_vector_for_the_target_day(self):
        record = json.loads((score.REPO / live.V2_RECORD).read_text(encoding="utf-8"))
        rows = {row[0]: row for row in record["per_day_h1"]["rows"]}
        walk = rows[self.targets[0].isoformat()][record["per_day_h1"]["columns"].index("v2")]
        self.assertEqual(len(walk), len(self.got["quantiles"]))
        for ours, theirs in zip(self.got["quantiles"], walk):
            self.assertAlmostEqual(ours, theirs, places=9)

    def test_the_levels_and_the_digest_are_stable(self):
        self.assertEqual(tuple(self.got["levels"]), live.QUANTILE_LEVELS)
        self.assertEqual(self.got["declaration_sha256"], self.again["declaration_sha256"])
        self.assertEqual(len(self.got["declaration_sha256"]), 64)

    def test_it_differs_from_v1s_published_distribution(self):
        v1 = live.distribution_forecasts(self.extended, 1, self.registry)
        self.assertNotEqual(self.got["declaration_sha256"], v1["declaration_sha256"])
        self.assertNotEqual(self.got["quantiles"], v1["published"])
