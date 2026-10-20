"""The live-monitoring read (#969): a reported-only reader of the live records and the public outcomes.

It reads outcomes as they print and opens no tier, gives no verdict and is cited only as a trigger. The statistics
(`repo_model.live_monitor`) are checked here on synthetic rows, never on a live record. The one rule that matters
for the lockbox is the gate: a read of live outcomes refuses unless `docs/decisions/live-monitoring.md` is a merged
decision record, a file in `docs/decisions/` itself and not in `drafts/`.

Red first: this file was committed, and run, before `src/repo_model/live_monitor.py` existed; the module import
failed (`ModuleNotFoundError`), so every class failed.

Recorded mutations (each applied by hand, the named class seen failing, then reverted):

* `require_decision_record`: the merged file's path read as `decisions_dir / "drafts" / DECISION_RECORD` instead of
  `decisions_dir / DECISION_RECORD`. `GateTests.test_a_draft_does_not_open_the_read` and
  `GateTests.test_a_merged_record_opens_the_read` failed with `LookAheadError not raised` and an unexpected
  `LookAheadError`.
* `require_development_window`: `day > last` weakened to `day > date(2030, 1, 1)`.
  `GateTests.test_the_replay_refuses_a_day_after_the_study_window` failed with `LookAheadError not raised`.
"""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import live_monitor as lm
from repo_model.splits import LookAheadError

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)


def _rows(outcomes, quantiles=(-4.0, -2.0, 0.0, 2.0, 4.0), start=date(2027, 1, 4)):
    return [
        {"date": start + timedelta(days=i), "outcome": value, "published": list(quantiles)}
        for i, value in enumerate(outcomes)
    ]


class StatisticTests(unittest.TestCase):
    def test_chi_square_tail(self):
        self.assertAlmostEqual(lm.chi2_sf(3.841458820694124, 1), 0.05, places=9)
        self.assertAlmostEqual(lm.chi2_sf(6.6348966010212145, 1), 0.01, places=9)
        self.assertAlmostEqual(lm.chi2_sf(2 * math.log(20), 2), 0.05, places=12)
        self.assertEqual(lm.chi2_sf(0.0, 1), 1.0)

    def test_kupiec_matches_the_closed_form(self):
        hits = [True] * 10 + [False] * 90
        out = lm.kupiec(hits, 0.05)
        lr = 2 * (10 * math.log(10 / 5) + 90 * math.log(90 / 95))
        self.assertAlmostEqual(out["lr"], lr, places=12)
        self.assertAlmostEqual(out["p_value"], lm.chi2_sf(lr, 1), places=12)
        self.assertEqual((out["n"], out["misses"]), (100, 10))

    def test_kupiec_at_the_expected_rate_is_zero_and_handles_no_misses(self):
        self.assertAlmostEqual(lm.kupiec([True] * 5 + [False] * 95, 0.05)["lr"], 0.0, places=12)
        none = lm.kupiec([False] * 50, 0.05)
        self.assertAlmostEqual(none["lr"], -2 * 50 * math.log(0.95), places=12)
        self.assertAlmostEqual(lm.kupiec([True] * 4, 0.05)["lr"], -2 * (4 * math.log(0.05)), places=12)

    def test_christoffersen_flags_clustered_misses_and_not_spread_ones(self):
        spread = [i % 20 == 0 for i in range(200)]
        clustered = [False] * 95 + [True] * 10 + [False] * 95
        self.assertLess(lm.christoffersen(spread)["lr"], 1.0)
        out = lm.christoffersen(clustered)
        self.assertGreater(out["lr"], 40.0)
        self.assertLess(out["p_value"], 1e-9)
        counts = out["transitions"]
        self.assertEqual((counts["00"], counts["01"], counts["10"], counts["11"]), (188, 1, 1, 9))

    def test_christoffersen_matches_the_closed_form(self):
        hits = [False] * 95 + [True] * 10 + [False] * 95
        n00, n01, n10, n11 = 188, 1, 1, 9
        pi01, pi11 = n01 / (n00 + n01), n11 / (n10 + n11)
        pi = (n01 + n11) / (n00 + n01 + n10 + n11)
        ll0 = (n00 + n10) * math.log(1 - pi) + (n01 + n11) * math.log(pi)
        ll1 = (n00 * math.log(1 - pi01) + n01 * math.log(pi01) + n10 * math.log(1 - pi11) + n11 * math.log(pi11))
        self.assertAlmostEqual(lm.christoffersen(hits)["lr"], -2 * (ll0 - ll1), places=10)

    def test_christoffersen_with_no_misses_has_nothing_to_test(self):
        out = lm.christoffersen([False] * 30)
        self.assertEqual((out["lr"], out["p_value"]), (0.0, 1.0))

    def test_band_coverage_is_inclusive_and_the_tail_is_strict(self):
        rows = _rows([-4.0, 4.0, 4.5, -4.5, 0.0])
        self.assertEqual(lm.band_hits(rows), [True, True, False, False, True])
        self.assertEqual(lm.tail_misses(rows), [False, False, True, False, False])

    def test_pit_bins_count_quantiles_strictly_below_the_outcome(self):
        rows = _rows([-5.0, -4.0, -3.0, 0.5, 2.5, 5.0])
        self.assertEqual(lm.pit_counts(rows), [2, 1, 0, 1, 1, 1])
        shares = lm.pit_shares(rows)
        self.assertAlmostEqual(sum(shares["shares"]), 1.0)
        self.assertAlmostEqual(shares["share_at_or_below_q25"], 3 / 6)

    def test_crps_ratio_is_the_mean_of_the_model_over_the_mean_of_the_benchmark(self):
        rows = _rows([0.0, 0.0])
        for row in rows:
            row["b1"] = [-8.0, -4.0, 0.0, 4.0, 8.0]
        ratio = lm.crps_ratio(rows, "b1")
        wide = sum(lm.crps_from_quantiles(LEVELS, r["b1"], r["outcome"]) for r in rows)
        narrow = sum(lm.crps_from_quantiles(LEVELS, r["published"], r["outcome"]) for r in rows)
        self.assertAlmostEqual(ratio["ratio"], narrow / wide)
        self.assertLess(ratio["ratio"], 1.0)
        self.assertEqual(ratio["days"], 2)

    def test_crps_ratio_skips_rows_without_the_benchmark_and_says_how_many(self):
        rows = _rows([0.0, 0.0, 0.0])
        rows[0]["b1"] = [-8.0, -4.0, 0.0, 4.0, 8.0]
        out = lm.crps_ratio(rows, "b1")
        self.assertEqual((out["days"], out["missing"]), (1, 2))
        self.assertIsNone(lm.crps_ratio(_rows([0.0]), "b2")["ratio"])


class RollingTests(unittest.TestCase):
    THRESHOLDS = {
        "band_coverage_60d": {"amber_below": 0.80, "amber_above": 0.98, "stop_below": 0.70},
        "kupiec_q95_125d": {"amber_p_below": 0.01},
        "christoffersen_q95_125d": {"amber_p_below": 0.01},
        "pit_share_at_or_below_q25": {"amber_outside": [0.15, 0.35]},
        "crps_ratio_to_b1_125d": {"amber_above": 1.0, "stop_above": 1.1},
    }

    def test_a_window_that_is_not_full_is_labelled_too_few_days(self):
        series = lm.rolling(_rows([0.0] * 10), self.THRESHOLDS, coverage_days=60, calibration_days=125)
        self.assertEqual(len(series), 10)
        self.assertEqual(series[-1]["coverage_60"], None)
        self.assertEqual(series[-1]["window"], lm.TOO_FEW_DAYS)
        self.assertEqual(series[-1]["flags"], [])

    def test_a_run_of_outside_the_band_days_goes_amber_then_stop(self):
        rows = _rows([0.0] * 58 + [9.0] * 22)
        series = lm.rolling(rows, self.THRESHOLDS, coverage_days=60, calibration_days=125)
        self.assertAlmostEqual(series[59]["coverage_60"], 58 / 60)
        self.assertEqual(series[59]["flags"], [])
        last = series[-1]
        self.assertAlmostEqual(last["coverage_60"], 38 / 60)
        self.assertIn("band_coverage_stop", last["flags"])
        flagged = [s for s in series if "band_coverage_amber" in s["flags"]]
        self.assertTrue(flagged)
        self.assertEqual(flagged[0]["date"], rows[60 + 10]["date"])

    def test_a_window_with_every_day_inside_is_flagged_as_over_covering(self):
        series = lm.rolling(_rows([0.0] * 60), self.THRESHOLDS, coverage_days=60, calibration_days=125)
        self.assertEqual(series[59]["flags"], ["band_coverage_amber"])

    def test_the_series_reads_each_day_from_the_days_up_to_it_only(self):
        rows = _rows([0.0] * 70 + [9.0] * 10)
        short = lm.rolling(rows[:75], self.THRESHOLDS, coverage_days=60, calibration_days=125)
        full = lm.rolling(rows, self.THRESHOLDS, coverage_days=60, calibration_days=125)
        self.assertEqual(short[74], full[74])

    def test_flags_are_labelled_as_proposals_never_verdicts(self):
        report = lm.report(_rows([0.0] * 70 + [9.0] * 10), self.THRESHOLDS, coverage_days=60, calibration_days=125)
        self.assertEqual(report["decides"], "nothing")
        self.assertIn("proposed", report["thresholds_status"])


class GateTests(unittest.TestCase):
    def test_a_draft_does_not_open_the_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp)
            (decisions / "drafts").mkdir()
            (decisions / "drafts" / lm.DECISION_RECORD).write_text("# draft\n", encoding="utf-8")
            with self.assertRaises(LookAheadError):
                lm.require_decision_record(decisions)

    def test_a_merged_record_opens_the_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp)
            (decisions / lm.DECISION_RECORD).write_text("# decision\n", encoding="utf-8")
            lm.require_decision_record(decisions)

    def test_the_repository_gate_is_closed_until_the_record_is_merged(self):
        root = Path(__file__).resolve().parents[1]
        merged = (root / "docs" / "decisions" / lm.DECISION_RECORD).exists()
        if merged:
            lm.require_decision_record()
        else:
            with self.assertRaises(LookAheadError):
                lm.require_decision_record()

    def test_the_replay_refuses_a_day_after_the_study_window(self):
        lm.require_development_window([date(2025, 12, 31)])
        with self.assertRaises(LookAheadError):
            lm.require_development_window([date(2025, 12, 31), date(2026, 1, 2)])

    def test_the_monitor_refuses_rows_before_the_gate_opens(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LookAheadError):
                lm.require_decision_record(Path(tmp))


class RecordTests(unittest.TestCase):
    def _record(self, day, snapshots, pinned="a" * 40, panel_last="2027-01-07"):
        return {
            "decision_day": day,
            "decision_instant": f"{day}T16:00:00-05:00",
            "code": {"sha": "b" * 40, "pinned_sha": pinned},
            "inputs": {"snapshots": snapshots, "panel_last_date": panel_last},
        }

    def test_staleness_compares_each_source_with_its_declared_bound(self):
        registry = {
            "nyfed_sofr": {"release_lag": {"worst_case_calendar_days": 6}},
            "frb_h8": {"field_release_lags": {"A": {"worst_case_calendar_days": 12}, "B": {"worst_case_calendar_days": 9}}},
            "nyfed_srf": {},
        }
        record = self._record("2027-01-08", [
            {"source_id": "nyfed_sofr", "sha256": "0" * 64, "retrieved_at": "2027-01-08T20:30:00+00:00", "url": "u"},
            {"source_id": "frb_h8", "sha256": "0" * 64, "retrieved_at": "2026-12-20T20:30:00+00:00", "url": "u"},
            {"source_id": "nyfed_srf", "sha256": "0" * 64, "retrieved_at": "2026-12-01T20:30:00+00:00", "url": "u"},
        ])
        rows = {row["source_id"]: row for row in lm.staleness(record, registry)["sources"]}
        self.assertEqual(rows["nyfed_sofr"]["age_days"], 0)
        self.assertFalse(rows["nyfed_sofr"]["stale"])
        self.assertEqual(rows["frb_h8"]["bound_days"], 12)
        self.assertTrue(rows["frb_h8"]["stale"])
        self.assertIsNone(rows["nyfed_srf"]["bound_days"])
        self.assertIsNone(rows["nyfed_srf"]["stale"])

    def test_the_panel_lag_is_read_against_the_sofr_bound(self):
        registry = {"nyfed_sofr": {"release_lag": {"worst_case_calendar_days": 6}}}
        out = lm.staleness(self._record("2027-01-08", [], panel_last="2026-12-20"), registry)
        self.assertEqual(out["panel"]["lag_days"], 19)
        self.assertTrue(out["panel"]["stale"])

    def test_the_pin_check_names_unregistered_records(self):
        records = [self._record("2027-01-08", [], pinned="a" * 40), self._record("2027-01-11", [], pinned="c" * 40)]
        out = lm.pin_check(records, {"a" * 40})
        self.assertEqual(out["unregistered"], ["2027-01-11"])
        self.assertEqual(out["checked"], 2)

    def test_rows_are_built_from_records_and_outcomes_for_one_lead(self):
        record = {
            "decision_day": "2027-01-08",
            "targets": [{"horizon": h, "target_date": f"2027-01-{8 + h:02d}"} for h in (1, 2, 3, 4, 5)],
            "distributions": {
                "levels": list(LEVELS),
                "published": {"quantiles_bps": {str(h): [-4.0, -2.0, 0.0, 2.0, 4.0] for h in (1, 2, 3, 4, 5)}},
                "persistence": {"quantiles_bps": {str(h): [-8.0, -4.0, 0.0, 4.0, 8.0] for h in (1, 2, 3, 4, 5)}},
            },
        }
        outcomes = {date(2027, 1, 9): 1.0}
        rows = lm.rows_from_records([record], outcomes, lead=1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], date(2027, 1, 9))
        self.assertEqual(rows[0]["outcome"], 1.0)
        self.assertEqual(rows[0]["b1"], [-8.0, -4.0, 0.0, 4.0, 8.0])
        self.assertEqual(lm.rows_from_records([record], {}, lead=1), [])
        with self.assertRaises(ValueError):
            lm.rows_from_records([record], outcomes, lead=7)


class ScriptTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def _script(self):
        from importlib.util import module_from_spec, spec_from_file_location

        spec = spec_from_file_location("live_monitor_script", self.ROOT / "scripts" / "live_monitor.py")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_the_live_read_refuses_before_it_touches_the_log(self):
        module = self._script()
        if (self.ROOT / "docs" / "decisions" / lm.DECISION_RECORD).exists():
            self.skipTest("the decision record is merged")
        with self.assertRaises(LookAheadError):
            module.live_run(Path("/nonexistent"), [], Path("/nonexistent"))

    def test_the_declaration_and_the_replay_record_agree(self):
        module = self._script()
        declaration = module.load_declaration()
        self.assertEqual(declaration["replay"]["last_day"], "2025-12-31")
        record = json.loads((self.ROOT / "docs/research/live-monitoring-969/replay.json").read_text())
        self.assertEqual(record["decides"], "nothing")
        self.assertLessEqual(date.fromisoformat(record["last_day"]), lm.DEV_LAST)
        self.assertEqual(len(record["series"]), record["days"])
        self.assertLessEqual(max(point["date"] for point in record["series"]), "2025-12-31")
        thresholds = declaration["proposed_thresholds"]
        self.assertIn("amber_below", thresholds["band_coverage_60d"])

    def test_the_draft_stays_a_draft_until_she_moves_it(self):
        decisions = self.ROOT / "docs" / "decisions"
        draft, merged = decisions / "drafts" / lm.DECISION_RECORD, decisions / lm.DECISION_RECORD
        self.assertTrue(draft.is_file() or merged.is_file())
        if draft.is_file() and not merged.is_file():
            self.assertIn("not in force", draft.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
