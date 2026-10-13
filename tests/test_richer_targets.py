"""The H9 targets and their as-of benchmarks (#639, step 1).

Every column below is a scratch input: it is off in every published declaration (`OffTests`), and the screen that reads
it (`scripts/richer_targets_639.py`) scores no day after 2025-12-31.
"""

from __future__ import annotations

import json
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, measurement_fields, protocol_benchmarks, richer_targets
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.scoring_protocol import GRID
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots"
REGISTRY = measurement_fields.load_registry()
CUTOFF = datetime(2026, 9, 8, 21, 31, 42).astimezone()


def weekdays(start: date, count: int):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def row(day, **values):
    return DailyObservation(day, {"spread_bps": 0.0, **values})


class BuildColumnsTests(unittest.TestCase):
    def one(self, **values):
        return richer_targets.build_columns([row(date(2024, 1, 3), **values)])[0].values

    def test_each_rate_target_is_in_basis_points_above_iorb(self):
        values = self.one(
            iorb=5.40, sofr_p1=5.30, sofr_p99=5.50, tgcr=5.31, bgcr=5.32, effr=5.33,
            tgcr_p1=5.20, tgcr_p99=5.45, bgcr_p1=5.21, bgcr_p99=5.46,
        )
        self.assertAlmostEqual(values["sofr_p99_iorb_bps"], 10.0)
        self.assertAlmostEqual(values["sofr_dispersion_bps"], 20.0)
        self.assertAlmostEqual(values["tgcr_iorb_bps"], -9.0)
        self.assertAlmostEqual(values["bgcr_iorb_bps"], -8.0)
        self.assertAlmostEqual(values["effr_iorb_bps"], -7.0)
        self.assertAlmostEqual(values["tgcr_dispersion_bps"], 25.0)
        self.assertAlmostEqual(values["bgcr_dispersion_bps"], 25.0)

    def test_a_missing_input_leaves_the_target_missing(self):
        values = self.one(iorb=5.40, sofr_p1=5.30, sofr_p99=None, tgcr=5.31)
        self.assertIsNone(values["sofr_p99_iorb_bps"])
        self.assertIsNone(values["sofr_dispersion_bps"])
        self.assertAlmostEqual(values["tgcr_iorb_bps"], -9.0)
        self.assertIsNone(values["bgcr_iorb_bps"])
        self.assertIsNone(values["tgcr_dispersion_bps"])

    def test_the_facility_columns_are_levels_in_billions_and_the_daily_change(self):
        days = weekdays(date(2024, 1, 2), 3)
        rows = richer_targets.build_columns(
            [row(days[0], on_rrp=100.0, srf_take_up=0.0), row(days[1], on_rrp=130.0, srf_take_up=2.5),
             row(days[2], on_rrp=None, srf_take_up=None)]
        )
        self.assertEqual([r.values["on_rrp_bn"] for r in rows], [100.0, 130.0, None])
        self.assertEqual([r.values["on_rrp_change_bn"] for r in rows], [None, 30.0, None])
        self.assertEqual([r.values["srf_take_up_bn"] for r in rows], [0.0, 2.5, None])

    def test_a_row_never_depends_on_a_later_one(self):
        days = weekdays(date(2024, 1, 2), 6)
        full = [row(d, iorb=5.4, tgcr=5.3 + 0.01 * i, on_rrp=50.0 + i) for i, d in enumerate(days)]
        head = richer_targets.build_columns(full[:4])
        whole = richer_targets.build_columns(full)
        for a, b in zip(head, whole):
            self.assertEqual(a.values, b.values)

    def test_every_declared_target_is_built(self):
        values = self.one()
        for target in richer_targets.TARGETS:
            self.assertIn(target.column, values)
            self.assertIn(target.column, richer_targets.COLUMN_FIELDS)


class TrackedSnapshotTests(unittest.TestCase):
    def test_the_secured_rate_percentiles_are_snapshotted_and_ordered(self):
        parsed = richer_targets.percentile_series(SNAPSHOTS, CUTOFF)
        for column in richer_targets.RAW_SERIES:
            self.assertGreater(len(parsed[column]), 2000, column)
        for name in ("tgcr", "bgcr"):
            low, high = parsed[f"{name}_p1"], parsed[f"{name}_p99"]
            common = sorted(set(low) & set(high))
            self.assertTrue(common)
            self.assertTrue(all(low[d] <= high[d] for d in common))

    def test_the_registry_declares_every_field_a_column_draws_on(self):
        for column, fields in richer_targets.COLUMN_FIELDS.items():
            for source, field in fields:
                self.assertIn(field, REGISTRY[source]["field_frequencies"], f"{column}: {source}.{field}")

    def test_the_assembled_panel_carries_the_raw_columns_and_stops_at_the_end_date(self):
        days = weekdays(date(2019, 3, 4), 5)
        base = [row(d, sofr=2.4, iorb=2.4) for d in days]
        built, summary = richer_targets.assemble(base, SNAPSHOTS, cutoff=CUTOFF, end=days[2])
        self.assertEqual([r.date for r in built], days[:3])
        self.assertIsNotNone(built[0].values["tgcr_p99"])
        self.assertIn("holes", summary)


class OffTests(unittest.TestCase):
    def test_no_published_feature_map_carries_a_target_column(self):
        for column in richer_targets.COLUMN_FIELDS:
            self.assertNotIn(column, contract.FEATURE_FIELDS)


def switched_on():
    fields = dict(richer_targets.COLUMN_FIELDS)
    return mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
            }
        ),
    )


class AsOfTests(unittest.TestCase):
    """A secured-rate percentile is read after its release lag, not on the day it describes (#639).

    A registry whose `nyfed_tgcr` source is released five business days after its reference date and whose other
    sources are released one day after: the dispersion of TGCR's percentiles, read for a scored day, must come from a
    row at least five business days back, however fresh SOFR's own percentiles are.

    Recorded mutation (CLAUDE.md), 13 October 2026, in a disposable copy: `src/repo_model/richer_targets.py`,
    `COLUMN_FIELDS["tgcr_dispersion_bps"]`, `_TGCR_P99 + _TGCR_P1` mutated to `_SOFR_P99 + _SOFR_P1` (the column
    would be gated on SOFR's lag). `test_a_slow_source_gates_its_dispersion` then fails with `AssertionError`
    (`57 not less than or equal to 53`: the dispersion is read at the row SOFR's lag allows, not TGCR's).
    """

    DATES = weekdays(date(2024, 3, 4), 60)
    DECISION = time(16, 0)

    def registry(self):
        registry = {name: dict(spec) for name, spec in REGISTRY.items()}
        slow = dict(registry["nyfed_tgcr"])
        slow["release_lag"] = {**slow["release_lag"], "days": 5}
        registry["nyfed_tgcr"] = slow
        return registry

    def rule(self, columns, horizon=1):
        return InformationRule(self.registry(), tuple(columns), decision_time=self.DECISION, horizon=horizon)

    def test_a_slow_source_gates_its_dispersion(self):
        with switched_on():
            rule = self.rule(["spread_bps", "tgcr_dispersion_bps", "sofr_dispersion_bps"])
            scored = len(self.DATES) - 1
            info = rule.information_set(self.DATES, scored)
            rows = {r.feature: r.row for r in info.reads}
            self.assertLessEqual(rows["tgcr_dispersion_bps"], scored - 1 - 5)
            self.assertGreater(rows["sofr_dispersion_bps"], rows["tgcr_dispersion_bps"])
            rule.check(self.DATES, info)

    def test_every_target_column_passes_both_guards(self):
        with switched_on():
            rule = self.rule(["spread_bps", *richer_targets.COLUMN_FIELDS])
            for scored in range(15, len(self.DATES)):
                rule.check(self.DATES, rule.information_set(self.DATES, scored))

    def test_a_row_forced_past_the_decision_is_refused(self):
        with switched_on():
            rule = self.rule(["spread_bps", "tgcr_dispersion_bps"])
            scored = len(self.DATES) - 1
            info = rule.information_set(self.DATES, scored)
            forced = info._replace(
                reads=tuple(r._replace(row=scored - 1) if r.feature == "tgcr_dispersion_bps" else r for r in info.reads)
            )
            with self.assertRaises(LookAheadError):
                rule.check(self.DATES, forced)


class AsOfRowsTests(unittest.TestCase):
    """`as_of_rows`: the latest row each column is public at, for each lead."""

    DATES = weekdays(date(2024, 3, 4), 60)

    def rows(self):
        return [row(d, tgcr_dispersion_bps=float(i)) for i, d in enumerate(self.DATES)]

    def test_each_lead_reads_one_row_further_back(self):
        with switched_on():
            read = richer_targets.as_of_rows(
                self.rows(), REGISTRY, ["tgcr_dispersion_bps"], leads=(1, 2, 5), scored=[40, 41]
            )
        one, two, five = (read[h]["tgcr_dispersion_bps"] for h in (1, 2, 5))
        self.assertTrue(all(b < a for a, b in zip(one, two)))
        self.assertTrue(all(b < a for a, b in zip(two, five)))
        self.assertTrue(all(r < s for r, s in zip(one, [40, 41])))


class BenchmarkTests(unittest.TestCase):
    """B1 and B2 for a series, drawing only on rows at or before the last public one.

    Recorded mutation (CLAUDE.md), 13 October 2026, in a disposable copy: `src/repo_model/richer_targets.py`,
    `b1_quantiles`, `range(max(first, h), anchor + 1)` mutated to `range(max(first, h), anchor + 2)` (a change that
    ends one row after the anchor). `test_a_later_row_does_not_move_the_forecast` then fails with `LookAheadError`
    ("B1 at lead 1 reads 2023-05-23, after 2023-05-22": B1 reads a row after the anchor).
    """

    N = 120
    DATES = weekdays(date(2023, 1, 2), N)

    def values(self):
        return [10.0 + (i % 7) for i in range(self.N)]

    def test_persistence_is_the_last_public_value_plus_the_h_day_changes(self):
        values = self.values()
        anchor = 100
        quantiles = richer_targets.b1_quantiles(values, self.DATES, anchor, 1, first=0)
        self.assertEqual(len(quantiles), len(GRID))
        changes = sorted(values[s] - values[s - 1] for s in range(1, anchor + 1))
        self.assertEqual(quantiles, protocol_benchmarks.empirical_quantiles(changes, values[anchor]))

    def test_a_later_row_does_not_move_the_forecast(self):
        values = self.values()
        changed = values[:101] + [1.0e6] * (self.N - 101)
        a = richer_targets.b1_quantiles(values, self.DATES, 100, 3, first=0)
        b = richer_targets.b1_quantiles(changed, self.DATES, 100, 3, first=0)
        self.assertEqual(a, b)
        kinds = ["x" if i % 2 else "y" for i in range(self.N)]
        a = richer_targets.b2_quantiles(values, kinds, self.DATES, 100, "x", first=0)
        b = richer_targets.b2_quantiles(changed, kinds, self.DATES, 100, "x", first=0)
        self.assertEqual(a, b)

    def test_the_climatology_is_the_same_type_days_only(self):
        values = [0.0 if i % 2 else 100.0 for i in range(self.N)]
        kinds = ["x" if i % 2 else "y" for i in range(self.N)]
        quantiles = richer_targets.b2_quantiles(values, kinds, self.DATES, 100, "x", first=0)
        self.assertEqual(set(quantiles), {0.0})

    def test_a_missing_value_is_skipped_and_too_little_history_is_none(self):
        values = self.values()
        values[50] = None
        self.assertIsNotNone(richer_targets.b1_quantiles(values, self.DATES, 100, 2, first=0))
        self.assertIsNone(richer_targets.b1_quantiles(values, self.DATES, 100, 2, first=95))
        self.assertIsNone(richer_targets.b1_quantiles(values, self.DATES, 50, 2, first=0))
        kinds = ["x"] * self.N
        self.assertIsNone(richer_targets.b2_quantiles(values, kinds, self.DATES, 100, "z", first=0))

    def test_the_window_starts_the_day_after_the_years_back(self):
        dates = weekdays(date(2021, 1, 4), 900)
        decision = dates.index(date(2023, 6, 1))
        first = richer_targets.window_first(dates, decision, 2)
        self.assertEqual(dates[first], date(2021, 6, 2))


class ScoreTests(unittest.TestCase):
    def test_a_point_forecast_scores_its_absolute_error_and_a_wide_one_more(self):
        sharp = [5.0] * len(GRID)
        wide = [5.0 + 10.0 * (g - 0.5) for g in GRID]
        s = richer_targets.crps(sharp, 7.0)
        self.assertAlmostEqual(s, 2.0)
        self.assertGreater(richer_targets.crps(wide, 9.0), 0.0)
        self.assertAlmostEqual(richer_targets.median_error(sharp, 7.0), 2.0)

    def test_the_median_is_the_half_level(self):
        self.assertIn(0.5, GRID)
        quantiles = [float(i) for i in range(len(GRID))]
        self.assertEqual(richer_targets.median(quantiles), quantiles[GRID.index(0.5)])


class StatisticTests(unittest.TestCase):
    def test_spearman_of_a_monotone_pair_is_one_and_ties_are_averaged(self):
        self.assertAlmostEqual(richer_targets.spearman([1, 2, 3, 4], [10, 20, 30, 41]), 1.0)
        self.assertAlmostEqual(richer_targets.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertIsNone(richer_targets.spearman([1, 1, 1], [1, 2, 3]))

    def test_the_rank_correlation_interval_brackets_the_estimate_and_is_reproducible(self):
        x = [float(i) for i in range(200)]
        y = [v + (7 * i % 13) for i, v in enumerate(x)]
        a = richer_targets.spearman_interval(x, y, seed=1, draws=300)
        b = richer_targets.spearman_interval(x, y, seed=1, draws=300)
        self.assertEqual(a, b)
        self.assertLessEqual(a["low"], a["rho"] + 1e-9)
        self.assertGreaterEqual(a["high"], a["rho"] - 1e-9)

    def test_the_pre_onset_contrast_has_an_auc_above_half_for_higher_values(self):
        pre = [[5.0, 6.0], [7.0], [6.5, 5.5]]
        other = [float(i % 5) for i in range(100)]
        out = richer_targets.pre_onset_interval(pre, other, seed=3, draws=300)
        self.assertGreater(out["auc"], 0.9)
        self.assertGreater(out["std_diff"], 1.0)
        self.assertLessEqual(out["auc_low"], out["auc"])
        self.assertGreaterEqual(out["auc_high"], out["auc"])


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_names_every_target_and_the_leads(self):
        declared = json.loads((ROOT / "metadata" / "richer_targets_639.json").read_text())
        self.assertEqual(
            [t["column"] for t in declared["targets"]], [t.column for t in richer_targets.TARGETS]
        )
        self.assertEqual(declared["leads"], list(richer_targets.LEADS))
        self.assertEqual(declared["hypothesis"], "H9")


if __name__ == "__main__":
    unittest.main()
