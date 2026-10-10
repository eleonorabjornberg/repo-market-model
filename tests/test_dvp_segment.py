"""The cleared-DVP segment test (#187): columns, the family and the win rule."""

from __future__ import annotations

import json
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, dvp_segment
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError
from repo_model.dvp_segment import (
    BENCHMARKS,
    GROUPS,
    HORIZONS,
    ONSET,
    POOLED,
    THRESHOLDS,
    classify,
    comparison_key,
    holm,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())


def switched_on():
    """`dvp_segment.COLUMN_FIELDS` in the feature map, for one test only (off when published)."""

    fields = dict(dvp_segment.COLUMN_FIELDS)
    return mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{
                    column: tuple(sorted({source for source, _f in pairs}))
                    for column, pairs in fields.items()
                },
            }
        ),
    )


def weekdays(start, count):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class BuildColumnsTests(unittest.TestCase):
    def rows(self, dates):
        return [
            DailyObservation(
                when,
                {
                    "sofr_volume": 2000.0 + index,
                    "bgcr_volume": 1000.0,
                    "ofr_dvp_rate": 2.15,
                    "bgcr": 2.10,
                },
            )
            for index, when in enumerate(dates)
        ]

    def test_the_volume_share_and_its_change(self):
        dates = weekdays(date(2021, 1, 4), 25)
        built = dvp_segment.build_columns(self.rows(dates))
        self.assertAlmostEqual(built[0].values["dvp_volume_share"], 0.5)
        self.assertIsNone(built[19].values["dvp_volume_share_chg20"])
        self.assertAlmostEqual(
            built[20].values["dvp_volume_share_chg20"],
            (2020.0 - 1000.0) / 2020.0 - 0.5,
        )

    def test_the_rate_spread_is_whole_basis_points(self):
        built = dvp_segment.build_columns(self.rows(weekdays(date(2021, 1, 4), 2)))
        # 2.15 - 2.10 is 4.999999999999982 bp as floats.
        self.assertEqual(built[0].values["ofr_dvp_minus_bgcr_bp"], 5.0)

    def test_a_missing_input_leaves_the_column_missing(self):
        rows = self.rows(weekdays(date(2021, 1, 4), 1))
        rows[0].values["bgcr_volume"] = None
        rows[0].values["ofr_dvp_rate"] = None
        built = dvp_segment.build_columns(rows)
        self.assertIsNone(built[0].values["dvp_volume_share"])
        self.assertIsNone(built[0].values["ofr_dvp_minus_bgcr_bp"])

    def test_the_rate_is_missing_before_the_ofr_published_in_real_time(self):
        """A backfilled day is never read by the headline column (#187).

        The OFR filled in its values before 2020-09-09 later; at any decision
        instant the as-of rule would read such a row at, the value was not
        public. Only the backfill sensitivity's column keeps it.

        Recorded mutation (CLAUDE.md), 2 October 2026, in a
        disposable copy: `src/repo_model/dvp_segment.py`, `values["ofr_dvp_minus_bgcr_bp"]
        = None if row.date < OFR_REAL_TIME_START else spread` mutated to
        `values["ofr_dvp_minus_bgcr_bp"] = spread`. This test then fails with
        `AssertionError` (`5.0 is not None`).
        """

        dates = [date(2020, 9, 4), date(2020, 9, 8), date(2020, 9, 9)]
        built = dvp_segment.build_columns(self.rows(dates))
        self.assertIsNone(built[0].values["ofr_dvp_minus_bgcr_bp"])
        self.assertIsNone(built[1].values["ofr_dvp_minus_bgcr_bp"])
        self.assertEqual(built[2].values["ofr_dvp_minus_bgcr_bp"], 5.0)
        self.assertEqual(built[0].values["ofr_dvp_minus_bgcr_bp_backfill"], 5.0)


class OfrRealTimeGuardTests(unittest.TestCase):
    """No OFR value is read from before the OFR published in real time (#522, of #508).

    `ofr_dvp_rate` and `ofr_dvp_minus_bgcr_bp_backfill` carry the OFR's values
    for days before 2020-09-09, which the OFR filled in after it began
    publishing: nobody had them at the time. The guard refuses a panel that
    holds a value in any `ofr_` column on such a day.

    Written red first: `require_ofr_public` did not exist (`AttributeError`).

    Recorded mutation (CLAUDE.md), 10 October 2026, in a disposable copy:
    `src/repo_model/dvp_segment.py`, `if column.startswith("ofr_") and value is not None:`
    in `require_ofr_public` mutated to `if column.startswith("ofr_") and value is not None and False:`.
    `test_a_value_before_the_real_time_start_is_refused` then fails with
    `AssertionError` (`LookAheadError not raised`), and so does
    `test_every_ofr_column_is_covered`.
    """

    def rows(self, dates, value=5.0):
        return [
            DailyObservation(when, {"spread_bps": 3.0, "ofr_dvp_rate": value, "ofr_dvp_minus_bgcr_bp_backfill": value})
            for when in dates
        ]

    def test_a_value_before_the_real_time_start_is_refused(self):
        rows = self.rows([date(2020, 9, 8), date(2020, 9, 9)])
        with self.assertRaises(LookAheadError):
            dvp_segment.require_ofr_public(rows)

    def test_every_ofr_column_is_covered(self):
        for column in ("ofr_dvp_rate", "ofr_dvp_minus_bgcr_bp", "ofr_dvp_minus_bgcr_bp_backfill", "ofr_tri_rate"):
            rows = [DailyObservation(date(2019, 9, 16), {column: 1.0})]
            with self.assertRaises(LookAheadError, msg=column):
                dvp_segment.require_ofr_public(rows)

    def test_a_panel_blanked_or_read_from_the_start_passes(self):
        dvp_segment.require_ofr_public(self.rows([date(2020, 9, 9), date(2020, 9, 10)]))
        blanked = [
            DailyObservation(date(2019, 9, 16), {"ofr_dvp_rate": None, "ofr_dvp_minus_bgcr_bp_backfill": None})
        ]
        dvp_segment.require_ofr_public(blanked)

    def test_blanking_clears_only_ofr_values_before_the_start(self):
        rows = self.rows([date(2020, 9, 8), date(2020, 9, 9)])
        blanked = dvp_segment.blank_ofr_before_real_time(rows)
        self.assertIsNone(blanked[0].values["ofr_dvp_rate"])
        self.assertIsNone(blanked[0].values["ofr_dvp_minus_bgcr_bp_backfill"])
        self.assertEqual(blanked[0].values["spread_bps"], 3.0)
        self.assertEqual(blanked[1].values["ofr_dvp_rate"], 5.0)
        self.assertEqual(rows[0].values["ofr_dvp_rate"], 5.0, "the input rows are not changed")
        dvp_segment.require_ofr_public(blanked)

    def test_the_start_is_the_ofr_real_time_start(self):
        self.assertEqual(dvp_segment.OFR_REAL_TIME_START, date(2020, 9, 9))


class OfrAvailabilityTests(unittest.TestCase):
    """`ofr_dvp_minus_bgcr_bp` is read two business days after its date (#187).

    The OFR's API states no publication time and keeps no vintages: its one
    timestamp, the series' `last_update`, is a last-write time (2026-10-02
    13:49:37 when fetched, with 2026-10-01 the latest observation). That is
    one observation of a next-business-day release, not a history of them, so
    `ofr_stfm_repo.release_lag` is declared conservatively, as #187 directs:
    a day's rate is available at 16:00 ET two business days after it. At the
    16:00 decision on Wednesday 21 January 2026, Monday's rate is the latest
    public one; Tuesday's is not, though Tuesday's BGCR is.

    Written red first: before `ofr_stfm_repo` was in `metadata/sources.json`,
    `InformationRule` raised `RegistryContractError` ("the registry declares
    no source 'ofr_stfm_repo'"), and two of these tests errored.

    Recorded mutation (CLAUDE.md), 2 October 2026, in a disposable copy:
    `metadata/sources.json`, `ofr_stfm_repo.release_lag`, `"days": 2` mutated
    to `"days": 1` (a rate public at 16:00 on the next business day).
    `test_a_rate_two_days_old_is_the_latest_read` then fails with
    `AssertionError` (`datetime.date(2026, 1, 20) != datetime.date(2026, 1,
    19)`): the forecast reads Tuesday's rate at Wednesday's decision.
    """

    FEATURES = ("spread_bps", "ofr_dvp_minus_bgcr_bp")

    def setUp(self):
        switch = switched_on()
        switch.start()
        self.addCleanup(switch.stop)
        self.dates = weekdays(date(2026, 1, 5), 20)

    def rule(self, horizon=1):
        return InformationRule(REGISTRY, self.FEATURES, decision_time=time(16, 0), horizon=horizon)

    def test_a_rate_two_days_old_is_the_latest_read(self):
        """The leakage test: Tuesday's rate is not read at Wednesday's decision."""

        rule = self.rule()
        thursday = self.dates.index(date(2026, 1, 22))  # decision Wed 21st 16:00
        info = rule.information_set(self.dates, thursday)
        (read,) = [r for r in info.reads if r.feature == "ofr_dvp_minus_bgcr_bp"]
        self.assertEqual(self.dates[read.row], date(2026, 1, 19))
        self.assertEqual(read.available_at, datetime(2026, 1, 21, 16, 0))
        tuesday = self.dates.index(date(2026, 1, 20))
        self.assertGreater(
            rule.availability(self.dates, dvp_segment.COLUMN_FIELDS["ofr_dvp_minus_bgcr_bp"], tuesday),
            info.decision_instant,
        )
        forced = info._replace(
            reads=tuple(
                r._replace(row=tuesday) if r.feature == "ofr_dvp_minus_bgcr_bp" else r
                for r in info.reads
            )
        )
        with self.assertRaises(LookAheadError):
            rule.check(self.dates, forced)

    def test_every_read_passes_both_guards_at_every_horizon(self):
        columns = tuple(dvp_segment.COLUMN_FIELDS)
        for horizon in (1, 3, 5):
            rule = InformationRule(
                REGISTRY, ("spread_bps",) + columns, decision_time=time(16, 0), horizon=horizon
            )
            for scored in range(8, len(self.dates)):
                rule.check(self.dates, rule.information_set(self.dates, scored))

    def test_the_volume_share_is_read_with_sofr_and_bgcr(self):
        """Both volumes print with their rates the next business day."""

        rule = InformationRule(
            REGISTRY, ("spread_bps", "dvp_volume_share"), decision_time=time(16, 0)
        )
        thursday = self.dates.index(date(2026, 1, 22))
        info = rule.information_set(self.dates, thursday)
        (read,) = [r for r in info.reads if r.feature == "dvp_volume_share"]
        self.assertEqual(self.dates[read.row], date(2026, 1, 20))


class OfrBackfillFloorTests(unittest.TestCase):
    """A value the OFR dated before 2020-09-09 is not available before the start (#187).

    The OFR began publishing the repo collection in real time on 2020-09-09
    (`ingest.OFR_STFM_REAL_TIME_START`); earlier values were filled in later.
    `_ofr_stfm_rows` therefore declares such a value available no earlier
    than the start's own declared instant, 16:00 New York time on Friday
    2020-09-11, while a value dated on or after the start keeps its own
    two-business-day instant.

    Recorded mutation (CLAUDE.md), 3 October 2026, in a disposable copy:
    `src/repo_model/ingest.py`, `_ofr_stfm_rows`, the two lines
    `if ref_date < OFR_STFM_REAL_TIME_START:` /
    `declared = max(declared, earliest)` deleted.
    `test_a_backfilled_value_waits_for_the_real_time_start` then fails with
    `AssertionError` (the 2020-09-04 value is declared available at
    2020-09-08 16:00 New York time, not 2020-09-11 16:00).
    """

    def rows(self, pairs, retrieved="2026-10-02T23:00:21Z"):
        import hashlib
        import tempfile

        from repo_model import ingest
        from repo_model.ingest import SnapshotArtifact

        payload = json.dumps(pairs).encode("utf-8")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "timeseries.json"
        path.write_bytes(payload)
        artifact = SnapshotArtifact(
            source_id=ingest.OFR_STFM_SOURCE_ID,
            path=path,
            retrieved_at=retrieved,
            sha256=hashlib.sha256(payload).hexdigest(),
            url=f"{ingest.OFR_STFM_TIMESERIES_URL}?mnemonic=REPO-DVP_AR_OO-P",
            byte_count=len(payload),
        )
        return {row.ref_date: row for row in ingest._ofr_stfm_rows(artifact, payload)}

    def test_a_backfilled_value_waits_for_the_real_time_start(self):
        from zoneinfo import ZoneInfo

        zone = ZoneInfo("America/New_York")
        rows = self.rows([["2020-09-04", 0.11], ["2020-09-10", 0.09]])
        start = datetime(2020, 9, 11, 16, 0, tzinfo=zone)
        self.assertEqual(rows[date(2020, 9, 4)].available_at, start)
        self.assertEqual(
            rows[date(2020, 9, 10)].available_at, datetime(2020, 9, 14, 16, 0, tzinfo=zone)
        )



class HolmTests(unittest.TestCase):
    def test_step_down(self):
        # m = 4, level 0.1: thresholds 0.025, 0.0333, 0.05, 0.1.
        verdict = holm({"a": 0.01, "b": 0.03, "c": 0.04, "d": 0.5})
        self.assertEqual(verdict, {"a": True, "b": True, "c": True, "d": False})

    def test_the_first_failure_stops_it(self):
        # 0.02 passes 0.025; 0.04 fails 0.0333, so 0.045 is kept although it is below 0.05.
        verdict = holm({"a": 0.02, "b": 0.04, "c": 0.045, "d": 0.9})
        self.assertEqual(verdict, {"a": True, "b": False, "c": False, "d": False})

    def test_a_p_value_out_of_range_is_refused(self):
        with self.assertRaises(ValueError):
            holm({"a": 1.5})


class FamilyTests(unittest.TestCase):
    def test_the_family_is_every_reported_comparison_but_the_sensitivities(self):
        expected = (
            len(GROUPS) * len(THRESHOLDS) * len(HORIZONS) * len(BENCHMARKS) * 2 + len(GROUPS)
        )
        self.assertEqual(dvp_segment.family_size(), expected)
        sensitivity_groups = {s.group for s in dvp_segment.SENSITIVITIES}
        self.assertTrue(sensitivity_groups <= {g.name for g in GROUPS})

    def test_every_window_ends_before_the_lockbox(self):
        for group in GROUPS:
            self.assertLess(group.window[1], date(2026, 1, 1))
        for sensitivity in dvp_segment.SENSITIVITIES:
            self.assertLess(sensitivity.window[1], date(2026, 1, 1))

    def test_a_group_on_the_ofr_window_is_capped(self):
        for group in GROUPS:
            uses_ofr = "ofr_dvp_minus_bgcr_bp" in group.inputs
            self.assertEqual(group.window == dvp_segment.OFR_WINDOW, uses_ofr)
            self.assertEqual(group.capped is not None, uses_ofr)


def entry(mean=0.01, p=0.0001, holm_improve=True, holm_worse=False, regimes=None):
    out = {
        "mean": mean,
        "p_improve": p,
        "p_worse": 1.0 - p,
        "holm_improve": holm_improve,
        "holm_worse": holm_worse,
    }
    if regimes is not None:
        out["regimes"] = regimes
    return out


def results(group, **overrides):
    """Every comparison of `group`, a clear win unless `overrides` says otherwise."""

    out = {}
    for tau in THRESHOLDS:
        for h in HORIZONS:
            for bench in BENCHMARKS:
                for day_set in (POOLED, ONSET):
                    key = comparison_key(group, "brier", day_set, tau, h, bench)
                    regimes = {"2018-19": 0.02, "2025-26": 0.01} if day_set == POOLED else None
                    out[key] = entry(regimes=regimes)
    out[comparison_key(group, "crps")] = entry()
    for key, value in overrides.items():
        out[key] = {**out[key], **value}
    return out


class ClassifyTests(unittest.TestCase):
    GROUP = GROUPS[0]

    def test_a_clear_win(self):
        verdict = classify(self.GROUP, results(self.GROUP.name))
        self.assertEqual(verdict["outcome"], "win")

    def test_a_group_on_the_ofr_window_is_never_a_win(self):
        (capped,) = [g for g in GROUPS if g.name == "ofr_dvp_minus_bgcr_bp"]
        verdict = classify(capped, results(capped.name))
        self.assertEqual(verdict["outcome"], "promising")

    def test_survival_at_two_horizons_is_not_enough(self):
        name = self.GROUP.name
        overrides = {
            comparison_key(name, "brier", POOLED, tau, h, "persistence_logistic"): {
                "holm_improve": False, "p_improve": 0.5,
            }
            for tau in THRESHOLDS
            for h in (3, 4, 5)
        }
        verdict = classify(self.GROUP, results(name, **overrides))
        self.assertFalse(verdict["by_threshold"]["5"]["conditions"]["a_survives_correction"])
        # It misses one condition only: promising.
        self.assertEqual(verdict["outcome"], "promising")

    def test_one_horizon_with_a_worse_point_estimate_misses_b(self):
        name = self.GROUP.name
        key = comparison_key(name, "brier", POOLED, 5.0, 4, "pressure_model_v1")
        verdict = classify(self.GROUP, results(name, **{key: {"mean": -0.001}}))
        self.assertFalse(verdict["by_threshold"]["5"]["conditions"]["b_improves_every_horizon"])
        self.assertEqual(verdict["by_threshold"]["10"]["outcome"], "win")

    def test_one_stress_episode_cannot_carry_it(self):
        name = self.GROUP.name
        key = comparison_key(name, "brier", POOLED, 5.0, 2, "persistence_logistic")
        verdict = classify(
            self.GROUP, results(name, **{key: {"regimes": {"2018-19": 0.05, "2025-26": -0.001}}})
        )
        self.assertFalse(
            verdict["by_threshold"]["5"]["conditions"]["c_improves_in_both_stress_regimes"]
        )

    def test_a_significantly_worse_onset_comparison_blocks_every_threshold(self):
        name = self.GROUP.name
        key = comparison_key(name, "brier", ONSET, 10.0, 1, "persistence_logistic")
        verdict = classify(self.GROUP, results(name, **{key: {"holm_worse": True}}))
        self.assertEqual(verdict["significantly_worse"], [key])
        for tau in ("5", "10"):
            self.assertFalse(
                verdict["by_threshold"][tau]["conditions"]["d_nothing_significantly_worse"]
            )
        self.assertEqual(verdict["outcome"], "promising")

    def test_nothing_significant_and_mixed_signs_is_no_effect(self):
        name = self.GROUP.name
        overrides = {}
        for tau in THRESHOLDS:
            for h in HORIZONS:
                for bench in BENCHMARKS:
                    key = comparison_key(name, "brier", POOLED, tau, h, bench)
                    overrides[key] = {
                        "holm_improve": False, "p_improve": 0.4,
                        "mean": 0.001 if h % 2 else -0.001,
                        "regimes": {"2018-19": -0.01, "2025-26": 0.01},
                    }
        verdict = classify(self.GROUP, results(name, **overrides))
        self.assertEqual(verdict["outcome"], "no effect")


if __name__ == "__main__":
    unittest.main()
