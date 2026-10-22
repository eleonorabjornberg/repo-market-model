"""Mechanism-consistent encodings of `gbm_funding`'s raw-level inputs (`repo_model.mechanism_encodings`, #1029, H5 step 3).

The encodings are derived columns: each is a function of its own panel row and earlier ones, declared on the union of the source fields of its
constituents, so `asof.InformationRule` reads it at the latest row on which every constituent was public. The directive's second criterion is that no
encoding introduces a publication instant of its own: the tests below pin each column's as-of read against its constituents' reads, at every lead
h = 1 to 5, through the real rule and the real registry, and run both guards on every information set.

Recorded mutations (CLAUDE.md), 22 October 2026, in a disposable copy:

* `src/repo_model/mechanism_encodings.py`, `COLUMN_FIELDS["tbill_4w_less_iorb_bps"]`, `_BILL_4W + _IORB` changed to `_BILL_4W` (the announced IORB no
  longer gates the column): `AsOfTests.test_each_column_is_declared_on_the_union_of_its_constituents` fails with `AssertionError` (the column's
  fields are not the union of the bill's and IORB's).
* `mechanism_encodings._causal_median`, the window `series[start : position + 1]` changed to `series[start : position + 2]` (the median looks one row
  ahead): `ArithmeticTests.test_a_ratio_never_reads_a_later_row` fails with `AssertionError` (the ratio on the truncated panel differs from the one
  on the full panel).
* `mechanism_encodings.COLUMN_FIELDS`, `"reserves_to_median": _RESERVES` changed to `_VOLUME` (the reserves ratio declared on a faster source than
  the reserves it divides): `AsOfTests.test_each_column_is_read_at_the_row_of_its_slowest_constituent` fails with `AssertionError`
  (`18 not less than or equal to 15 : (1, 20, 'reserves_to_median')`: the column is read at row 18, newer than the reserves' row 15).
"""

from __future__ import annotations

import unittest
from datetime import date, time, timedelta
from types import MappingProxyType
from unittest import mock

from repo_model import contract, mechanism_encodings as me, measurement_fields
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

REGISTRY = measurement_fields.load_registry()
DECISION = time(16, 0)


def weekdays(count, start=date(2026, 1, 5)):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def row(day, i, **over):
    values = {
        "spread_bps": 1.0, "sofr": 4.00 + i / 1000.0, "iorb": 3.90, "sofr_p25": 3.95, "sofr_p75": 4.10 + i / 1000.0,
        "sofr_volume": 1000.0 + i, "reserve_balances": 3000.0 + i, "tbill_4w": 3.80, "tbill_13w": 3.85,
    }
    values.update(over)
    return DailyObservation(day, values)


class ArithmeticTests(unittest.TestCase):
    def test_the_spread_encodings_are_in_basis_points(self):
        (out,) = me.build_columns([row(date(2026, 1, 5), 0, sofr=4.00, iorb=3.90, sofr_p25=3.95, sofr_p75=4.10, tbill_4w=3.80, tbill_13w=3.95)])
        v = out.values
        self.assertAlmostEqual(v["tbill_4w_less_iorb_bps"], -10.0)
        self.assertAlmostEqual(v["tbill_13w_less_iorb_bps"], 5.0)
        self.assertAlmostEqual(v["p75_less_sofr_bps"], 10.0)
        self.assertAlmostEqual(v["sofr_less_p25_bps"], 5.0)

    def test_a_missing_constituent_leaves_the_column_missing_and_the_others_alone(self):
        (out,) = me.build_columns([row(date(2026, 1, 5), 0, sofr_p75=None)])
        self.assertIsNone(out.values["p75_less_sofr_bps"])
        self.assertIsNotNone(out.values["sofr_less_p25_bps"])

    def test_a_ratio_is_the_value_over_the_median_of_the_trailing_window(self):
        days = weekdays(me.MINIMUM_ROWS + 5)
        rows = me.build_columns([row(d, i, sofr_volume=float(100 + i), reserve_balances=500.0) for i, d in enumerate(days)])
        last = len(rows) - 1
        window = [100.0 + i for i in range(0, last + 1)]  # fewer rows than the window: all of them
        window.sort()
        median = (window[len(window) // 2 - 1] + window[len(window) // 2]) / 2.0 if len(window) % 2 == 0 else window[len(window) // 2]
        self.assertAlmostEqual(rows[last].values["sofr_volume_to_median"], (100.0 + last) / median)
        self.assertAlmostEqual(rows[last].values["reserves_to_median"], 1.0)

    def test_the_window_is_a_year_of_rows_and_forgets_older_ones(self):
        count = me.WINDOW_ROWS + 30
        days = weekdays(count)
        volumes = [10_000.0] * 30 + [100.0] * me.WINDOW_ROWS  # the first 30 rows are outside the last row's window
        rows = me.build_columns([row(d, i, sofr_volume=volumes[i]) for i, d in enumerate(days)])
        self.assertAlmostEqual(rows[-1].values["sofr_volume_to_median"], 1.0)

    def test_fewer_rows_than_the_minimum_leave_a_ratio_missing(self):
        days = weekdays(me.MINIMUM_ROWS)
        rows = me.build_columns([row(d, i) for i, d in enumerate(days)])
        self.assertIsNone(rows[me.MINIMUM_ROWS - 2].values["sofr_volume_to_median"])
        self.assertIsNotNone(rows[me.MINIMUM_ROWS - 1].values["sofr_volume_to_median"])

    def test_a_ratio_never_reads_a_later_row(self):
        """The column on a row is the same whether or not later rows exist."""

        days = weekdays(me.MINIMUM_ROWS + 40)
        full = me.build_columns([row(d, i * i % 97) for i, d in enumerate(days)])
        for cut in (me.MINIMUM_ROWS, me.MINIMUM_ROWS + 17, len(days) - 1):
            part = me.build_columns([row(d, i * i % 97) for i, d in enumerate(days[:cut])])
            for name in me.ENCODED.values():
                self.assertEqual([r.values[name] for r in part], [r.values[name] for r in full[:cut]], name)

    def test_the_input_rows_are_not_changed(self):
        original = [row(d, i) for i, d in enumerate(weekdays(5))]
        snapshot = [dict(r.values) for r in original]
        me.build_columns(original)
        self.assertEqual([dict(r.values) for r in original], snapshot)

    def test_a_zero_median_leaves_a_ratio_missing(self):
        days = weekdays(me.MINIMUM_ROWS)
        rows = me.build_columns([row(d, i, sofr_volume=0.0) for i, d in enumerate(days)])
        self.assertIsNone(rows[-1].values["sofr_volume_to_median"])


class MapTests(unittest.TestCase):
    def test_every_raw_level_has_one_encoding_and_every_encoding_a_declaration(self):
        self.assertEqual(
            set(me.ENCODED), {"tbill_4w", "tbill_13w", "sofr_p25", "sofr_p75", "sofr_volume", "reserve_balances"}
        )
        self.assertEqual(set(me.ENCODED.values()), set(me.COLUMN_FIELDS))
        self.assertEqual(len(set(me.ENCODED.values())), len(me.ENCODED))

    def test_the_features_are_replaced_in_place_and_nothing_else_moves(self):
        base = ("spread_bps", "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "tbill_13w", "tbill_4w", "tga", "treasury_settlement")
        self.assertEqual(
            me.encode_features(base),
            ("spread_bps", "reserves_to_median", "sofr_less_p25_bps", "p75_less_sofr_bps", "sofr_volume_to_median",
             "tbill_13w_less_iorb_bps", "tbill_4w_less_iorb_bps", "tga", "treasury_settlement"),
        )

    def test_the_published_feature_map_does_not_carry_an_encoding(self):
        self.assertFalse(set(me.COLUMN_FIELDS) & set(contract.FEATURE_FIELDS))

    def test_switched_on_adds_the_columns_and_restores_the_map(self):
        before = contract.FEATURE_FIELDS
        with me.switched_on():
            self.assertTrue(set(me.COLUMN_FIELDS) <= set(contract.FEATURE_FIELDS))
            self.assertTrue(set(me.COLUMN_FIELDS) <= set(contract.FEATURE_SOURCES))
        self.assertIs(contract.FEATURE_FIELDS, before)
        self.assertFalse(set(me.COLUMN_FIELDS) & set(contract.FEATURE_SOURCES))


class AsOfTests(unittest.TestCase):
    """Each encoding is read at the row its slowest constituent allows, and no later (the directive's second criterion)."""

    DATES = [d for d in weekdays(70) if d != date(2026, 1, 19)]
    CONSTITUENTS = {
        "tbill_4w_less_iorb_bps": ("tbill_4w", "iorb"),
        "tbill_13w_less_iorb_bps": ("tbill_13w", "iorb"),
        "sofr_less_p25_bps": ("sofr", "sofr_p25"),
        "p75_less_sofr_bps": ("sofr_p75", "sofr"),
        "sofr_volume_to_median": ("sofr_volume",),
        "reserves_to_median": ("reserve_balances",),
    }

    def rows(self):
        return me.build_columns([row(d, i) for i, d in enumerate(self.DATES)])

    def rule(self, features, horizon=1):
        return InformationRule(REGISTRY, tuple(features), decision_time=DECISION, horizon=horizon)

    def test_each_column_is_declared_on_the_union_of_its_constituents(self):
        """Mutation 1 of the module docstring: drop the IORB fields from the bill column and the union no longer holds."""

        for column, parts in self.CONSTITUENTS.items():
            union = set()
            for part in parts:
                union |= set(contract.FEATURE_FIELDS[part])
            self.assertEqual(set(me.COLUMN_FIELDS[column]), union, column)

    def test_each_column_is_read_at_the_row_of_its_slowest_constituent(self):
        for h in range(1, 6):
            with me.switched_on():
                information = self.rule(["spread_bps", *self.CONSTITUENTS, *{p for ps in self.CONSTITUENTS.values() for p in ps}], h)
                for scored in range(15, len(self.DATES)):
                    info = information.information_set(self.DATES, scored)
                    rows = {r.feature: r.row for r in info.reads}
                    for column, parts in self.CONSTITUENTS.items():
                        slowest = min(rows[p] for p in parts)
                        self.assertLessEqual(rows[column], slowest, (h, scored, column))
                        self.assertEqual(rows[column], slowest, (h, scored, column))
                    information.check(self.DATES, info)

    def test_a_column_declared_on_a_faster_leg_than_it_divides_is_caught(self):
        """The reserves ratio declared on the volume's fields (a faster source) would be read at a row the reserves are not yet public at."""

        wrong = MappingProxyType({**me.COLUMN_FIELDS, "reserves_to_median": tuple(contract.FEATURE_FIELDS["sofr_volume"])})
        with mock.patch.object(me, "COLUMN_FIELDS", wrong), me.switched_on():
            information = self.rule(["spread_bps", "reserve_balances", "reserves_to_median"], 1)
            newer = 0
            for scored in range(15, len(self.DATES)):
                rows = {r.feature: r.row for r in information.information_set(self.DATES, scored).reads}
                newer += rows["reserves_to_median"] > rows["reserve_balances"]
            self.assertGreater(newer, 0)

    def test_a_forced_newer_read_is_refused(self):
        with me.switched_on():
            information = self.rule(["spread_bps", "tbill_4w_less_iorb_bps"], 1)
            scored = len(self.DATES) - 1
            info = information.information_set(self.DATES, scored)
            forced = info._replace(reads=tuple(r._replace(row=scored) if r.feature == "tbill_4w_less_iorb_bps" else r for r in info.reads))
            with self.assertRaises(LookAheadError):
                information.check(self.DATES, forced)


if __name__ == "__main__":
    unittest.main()
