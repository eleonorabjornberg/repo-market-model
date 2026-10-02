"""Early-warning inputs (#127): the pre-declared candidates and their definitions.

The candidate list is fixed before any scoring (#127, step 1), and the onset
signals' definitions are fixed by the issue because they were chosen with
hindsight. These tests pin both: every item the issue names is declared, in
its group, with its formula, and each column is built from its own row and
earlier rows only, so the as-of rule's read of it is a read of what was public.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, early_warning
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.ingest import SRF_INCEPTION
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())


def weekdays(start, count):
    out, current = [], start
    while len(out) < count:
        if current.weekday() < 5:
            out.append(current)
        current += timedelta(days=1)
    return out


def base_rows(dates):
    """Every input column, each a distinct function of its row."""

    rows = []
    for i, when in enumerate(dates):
        rows.append(
            DailyObservation(
                when,
                {
                    "sofr": 4.30 + 0.01 * (i % 7),
                    "iorb": 4.40,
                    "sofr_p1": 4.20 + 0.001 * i,
                    "sofr_p75": 4.35 + 0.01 * (i % 5),
                    "sofr_p99": 4.50 + 0.02 * (i % 3),
                    "tgcr": 4.28 + 0.01 * (i % 4),
                    "bgcr": 4.29 + 0.01 * (i % 6),
                    "effr": 4.33,
                    "tga": 800.0 + 3.0 * i,
                    "on_rrp": 90.0 + 2.0 * i,
                    "srf_take_up": 0.0 if i % 3 else 0.001,
                },
            )
        )
    return rows


class CandidateListTests(unittest.TestCase):
    """The pre-declared list is the issue's, item by item."""

    def test_every_item_the_issue_names_is_declared_once_in_its_group(self):
        by_name = {candidate.name: candidate for candidate in early_warning.CANDIDATES}
        self.assertEqual(len(by_name), len(early_warning.CANDIDATES))
        self.assertEqual(
            {name: candidate.group for name, candidate in by_name.items()},
            {
                "sofr_tail": "registered_unused",
                "sofr_p1": "registered_unused",
                "sofr_tgcr": "registered_unused",
                "bgcr_tgcr": "registered_unused",
                "dealer_positions": "registered_unused",
                "mmf_net_flows": "registered_unused",
                "mmf_repo_holdings": "registered_unused",
                "settlement_x_tga_change": "registered_unused",
                "sofr_above_effr_share": "onset_signal",
                "effr_iorb_change": "onset_signal",
                "sofr_p99_iorb": "onset_signal",
                "on_rrp_below_100bn": "onset_signal",
                "srf_take_up_positive": "onset_signal",
                "issuance_x_dealer_positions": "issuance_dealer",
            },
        )

    def test_every_declared_column_has_declared_fields_or_a_stated_block(self):
        for candidate in early_warning.CANDIDATES:
            with self.subTest(candidate=candidate.name):
                if candidate.blocked:
                    self.assertFalse(candidate.columns)
                    self.assertTrue(candidate.name.startswith("mmf_"))
                    continue
                self.assertTrue(candidate.columns or candidate.products)
                for column in candidate.columns:
                    self.assertTrue(
                        column in early_warning.COLUMN_FIELDS
                        or column in contract.FEATURE_FIELDS,
                        column,
                    )

    def test_the_overlay_is_off_in_the_published_map(self):
        for column in early_warning.COLUMN_FIELDS:
            self.assertNotIn(column, contract.FEATURE_FIELDS)

    def test_the_onset_group_is_the_unblocked_onset_signals(self):
        self.assertEqual(
            early_warning.ONSET_GROUP,
            tuple(
                candidate.name
                for candidate in early_warning.CANDIDATES
                if candidate.group == "onset_signal" and not candidate.blocked
            ),
        )


class DefinitionTests(unittest.TestCase):
    """Each formula is the one the issue fixes."""

    def setUp(self):
        self.dates = weekdays(date(2025, 1, 6), 60)
        self.rows = base_rows(self.dates)
        self.built = early_warning.build_columns(self.rows)

    def value(self, index, column):
        return self.built[index].values[column]

    def test_registered_spreads_are_in_basis_points(self):
        r = self.rows[30].values
        self.assertAlmostEqual(self.value(30, "sofr_p99_p75_bps"), (r["sofr_p99"] - r["sofr_p75"]) * 100)
        self.assertAlmostEqual(self.value(30, "sofr_tgcr_bps"), (r["sofr"] - r["tgcr"]) * 100)
        self.assertAlmostEqual(self.value(30, "bgcr_tgcr_bps"), (r["bgcr"] - r["tgcr"]) * 100)
        self.assertAlmostEqual(self.value(30, "sofr_p99_iorb_bps"), (r["sofr_p99"] - r["iorb"]) * 100)
        self.assertEqual(self.value(30, "sofr_p1"), r["sofr_p1"])

    def test_the_share_of_the_last_20_business_days_with_sofr_above_effr(self):
        window = self.rows[41 - 19 : 42]
        expected = sum(1 for row in window if row.values["sofr"] > row.values["effr"]) / 20
        self.assertEqual(early_warning.ONSET_WINDOW, 20)
        self.assertAlmostEqual(self.value(41, "sofr_above_effr_share_20"), expected)
        # Strictly above: a day level with EFFR does not count.
        level = [
            DailyObservation(row.date, {**row.values, "sofr": row.values["effr"]})
            for row in self.rows
        ]
        built = early_warning.build_columns(level)
        self.assertEqual(built[41].values["sofr_above_effr_share_20"], 0.0)
        # Fewer than 20 rows: no value.
        self.assertIsNone(self.value(18, "sofr_above_effr_share_20"))
        self.assertIsNotNone(self.value(19, "sofr_above_effr_share_20"))

    def test_the_20_business_day_change_in_effr_minus_iorb(self):
        now, then = self.rows[45].values, self.rows[25].values
        expected = ((now["effr"] - now["iorb"]) - (then["effr"] - then["iorb"])) * 100
        self.assertAlmostEqual(self.value(45, "effr_iorb_change_20_bps"), expected)
        self.assertIsNone(self.value(19, "effr_iorb_change_20_bps"))

    def test_the_on_rrp_flag_is_below_100bn_not_the_level(self):
        self.assertEqual(early_warning.ON_RRP_FLAG_BELOW_USD_BN, 100.0)
        for i, row in enumerate(self.rows):
            with self.subTest(on_rrp=row.values["on_rrp"]):
                self.assertEqual(
                    self.value(i, "on_rrp_below_100bn"),
                    1.0 if row.values["on_rrp"] < 100.0 else 0.0,
                )

    def test_the_srf_flag_is_take_up_above_zero(self):
        for i, row in enumerate(self.rows):
            self.assertEqual(
                self.value(i, "srf_take_up_positive"),
                1.0 if row.values["srf_take_up"] > 0 else 0.0,
            )

    def test_before_the_facility_existed_its_flag_is_zero(self):
        dates = weekdays(SRF_INCEPTION - timedelta(days=7), 10)
        rows = [
            DailyObservation(row.date, {k: v for k, v in row.values.items() if k != "srf_take_up" or row.date >= SRF_INCEPTION})
            for row in base_rows(dates)
        ]
        built = early_warning.build_columns(rows)
        for row in built:
            if row.date < SRF_INCEPTION:
                self.assertEqual(row.values["srf_take_up_positive"], 0.0)
        # After the inception a missing take-up is a hole, not a zero.
        hole = [
            DailyObservation(row.date, {k: v for k, v in row.values.items() if k != "srf_take_up"})
            for row in base_rows(weekdays(date(2025, 1, 6), 3))
        ]
        self.assertIsNone(early_warning.build_columns(hole)[1].values["srf_take_up_positive"])

    def test_the_tga_change_is_over_the_design_s_five_rows(self):
        from repo_model.ml import TGA_CHANGE_ROWS  # noqa: F401  (the same window)

        self.assertEqual(early_warning.TGA_CHANGE_ROWS, 5)
        self.assertAlmostEqual(
            self.value(30, "tga_change_5d"),
            self.rows[30].values["tga"] - self.rows[25].values["tga"],
        )

    def test_a_hole_in_a_window_leaves_no_value(self):
        rows = list(self.rows)
        rows[30] = DailyObservation(rows[30].date, {k: v for k, v in rows[30].values.items() if k != "effr"})
        built = early_warning.build_columns(rows)
        self.assertIsNone(built[35].values["sofr_above_effr_share_20"])
        self.assertIsNone(built[50].values["effr_iorb_change_20_bps"])
        # Once the hole leaves the window, the share is back.
        self.assertIsNotNone(built[50].values["sofr_above_effr_share_20"])

    def test_a_column_never_looks_forward(self):
        """Changing every row after `r` leaves every built value at `r` unchanged."""

        cut = 40
        changed = list(self.rows[:cut + 1]) + [
            DailyObservation(row.date, {k: v * 3.0 + 1.0 for k, v in row.values.items()})
            for row in self.rows[cut + 1 :]
        ]
        again = early_warning.build_columns(changed)
        for index in range(cut + 1):
            self.assertEqual(again[index].values, self.built[index].values)


def overlay():
    """The early-warning columns switched on for one test, as the script does."""

    fields = dict(early_warning.COLUMN_FIELDS)
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


class AsOfReadTests(unittest.TestCase):
    """Under the as-of rule each column is read where its every field is public."""

    def setUp(self):
        switch = overlay()
        switch.start()
        self.addCleanup(switch.stop)
        self.dates = weekdays(date(2025, 1, 6), 60)
        self.rows = early_warning.build_columns(base_rows(self.dates))

    def test_every_read_passes_both_guards_at_every_horizon(self):
        columns = tuple(
            column
            for candidate in early_warning.CANDIDATES
            for column in candidate.columns
            if column in early_warning.COLUMN_FIELDS
        )
        for horizon in (1, 3):
            rule = InformationRule(
                REGISTRY, ("spread_bps",) + columns, decision_time=time(16, 0), horizon=horizon
            )
            for scored in range(10, len(self.dates)):
                info = rule.information_set(self.dates, scored)
                rule.check(self.dates, info)

    def test_a_derived_column_is_read_no_later_than_its_slowest_field(self):
        """SOFR and TGCR for a day are published the next business day.

        The forecast of Thursday 13 February is made at 16:00 on Wednesday the
        12th, when Tuesday's SOFR−TGCR spread is the latest public one;
        Wednesday's is published on Thursday. A read forced onto Wednesday's
        row is leakage.
        """

        rule = InformationRule(
            REGISTRY, ("spread_bps", "sofr_tgcr_bps"), decision_time=time(16, 0)
        )
        thursday = self.dates.index(date(2025, 2, 13))
        info = rule.information_set(self.dates, thursday)
        (read,) = [r for r in info.reads if r.feature == "sofr_tgcr_bps"]
        self.assertEqual(self.dates[read.row], date(2025, 2, 11))
        forced = info._replace(
            reads=tuple(
                r._replace(row=thursday - 1) if r.feature == "sofr_tgcr_bps" else r
                for r in info.reads
            )
        )
        with self.assertRaises(LookAheadError):
            rule.check(self.dates, forced)


if __name__ == "__main__":
    unittest.main()
