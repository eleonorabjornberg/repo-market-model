"""The desk outputs (#232): reporting read from the published model, not a model.

Eleonora's ruling on #232 ("I want Nicholas's outputs"): beside the pressure
probability, the published distribution's quantile grid on scheduled pressure
days, the turn's expected contribution to the period average, and the declared
reserve-scarcity state (#115) read as of each forecast's decision instant.
`scripts/desk_outputs.py` computes them. These tests hold:

* the mean-from-quantiles rule (`mean_from_quantiles`), kept as ruled
  (Q3 on PR #241) and labelled wherever the mean is shown (`MEAN_LABEL`);
* the turn-contribution arithmetic (`calendar_days_carried`,
  `turn_contribution`), calendar-day weighted as ruled (Q2 on PR #241);
* the "not yet calibrated (#243)" label beside the published 25-75 band;
* the scheduled pressure-day tags, read from the repository's own calendar
  columns and the split declaration;
* the scarcity state's as-of read (`scarcity_at`), which reuses
  `InformationRule`'s read and both of its guards;
* the history's lockbox refusal (`require_unlocked` before any fit).

Written first, and watched failing: before `scripts/desk_outputs.py` existed
every class failed in `setUpClass` with `FileNotFoundError` on the script's path.
The rulings' tests (`TurnContributionTests`, `LabelTests`, the labelled
statements) were written before the code they hold, and failed with
`AttributeError` on `calendar_days_carried`, `MEAN_LABEL` and `BAND_25_75_LABEL`,
and on the unlabelled statement.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, datetime, time
from pathlib import Path

from repo_model.contract import QUANTILE_LEVELS
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

from test_scarcity import DATES, raw_rows, scarcity_inputs_on

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "desk_outputs.py"
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")


def _desk():
    spec = importlib.util.spec_from_file_location("desk_outputs_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MeanFromQuantilesTests(unittest.TestCase):
    """The stated rule: the piecewise-linear quantile function, flat beyond the outer levels."""

    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def test_the_weights_are_the_rule_and_sum_to_one(self):
        weights = self.desk.mean_weights(QUANTILE_LEVELS)
        for got, expected in zip(weights, (0.15, 0.225, 0.25, 0.225, 0.15)):
            self.assertAlmostEqual(got, expected)
        self.assertAlmostEqual(sum(weights), 1.0)

    def test_a_symmetric_grid_has_its_median_as_mean(self):
        self.assertAlmostEqual(
            self.desk.mean_from_quantiles(QUANTILE_LEVELS, (0.0, 1.0, 2.0, 3.0, 4.0)), 2.0
        )

    def test_a_right_tail_pulls_the_mean_up_by_the_top_weight(self):
        # Only the 95% quantile is off zero: the mean is its weight times it.
        self.assertAlmostEqual(
            self.desk.mean_from_quantiles(QUANTILE_LEVELS, (0.0, 0.0, 0.0, 0.0, 10.0)), 1.5
        )

    def test_a_point_mass_is_its_own_mean(self):
        self.assertAlmostEqual(
            self.desk.mean_from_quantiles(QUANTILE_LEVELS, (-3.0,) * 5), -3.0
        )

    def test_a_malformed_grid_raises(self):
        with self.assertRaises(ValueError):
            self.desk.mean_from_quantiles(QUANTILE_LEVELS, (0.0, 1.0, 2.0))
        with self.assertRaises(ValueError):
            self.desk.mean_from_quantiles(QUANTILE_LEVELS, (0.0, 2.0, 1.0, 3.0, 4.0))
        with self.assertRaises(ValueError):
            self.desk.mean_from_quantiles((0.5, 0.25), (0.0, 1.0))


class TurnContributionTests(unittest.TestCase):
    """Calendar-day weighting, as SOFR averages are computed (Eleonora's ruling on PR #241, Q2).

    A weekend or holiday carries the previous business day's rate, so the
    day's forecast mean counts once for each calendar day of its month it
    carries, over the calendar days in the month. Business days come from
    `metadata/market_holidays.json`.
    """

    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def test_a_midweek_day_carries_itself(self):
        self.assertEqual(self.desk.calendar_days_carried(date(2025, 12, 31)), 1)
        self.assertEqual(self.desk.calendar_days_in_month(date(2025, 12, 31)), 31)
        self.assertAlmostEqual(self.desk.turn_contribution(31.0, date(2025, 12, 31)), 1.0)
        self.assertAlmostEqual(self.desk.turn_contribution(-6.2, date(2025, 12, 31)), -0.2)

    def test_a_friday_month_end_counts_three_days(self):
        # Friday 29 August 2025 carries Saturday 30 and Sunday 31 August.
        self.assertEqual(self.desk.calendar_days_carried(date(2025, 8, 29)), 3)
        self.assertAlmostEqual(self.desk.turn_contribution(31.0, date(2025, 8, 29)), 3.0)

    def test_a_holiday_is_carried_by_the_business_day_before_it(self):
        # Christmas 2025 is a Thursday, closed in the market holiday table.
        self.assertEqual(self.desk.calendar_days_carried(date(2025, 12, 24)), 2)
        # Friday 29 May 2026 carries the weekend in May; Memorial Day (25 May)
        # is carried by Friday 22 May with its weekend.
        self.assertEqual(self.desk.calendar_days_carried(date(2026, 5, 22)), 4)

    def test_days_past_the_month_end_count_in_the_next_months_average(self):
        # Friday 31 October 2025: Saturday 1 and Sunday 2 November carry its
        # rate in November's average, not October's.
        self.assertEqual(self.desk.calendar_days_carried(date(2025, 10, 31)), 1)
        self.assertAlmostEqual(self.desk.turn_contribution(31.0, date(2025, 10, 31)), 1.0)

    def test_a_day_that_is_not_a_business_day_raises(self):
        with self.assertRaises(ValueError):
            self.desk.calendar_days_carried(date(2025, 12, 25))
        with self.assertRaises(ValueError):
            self.desk.calendar_days_carried(date(2025, 8, 30))

    def test_a_day_the_table_does_not_cover_raises(self):
        with self.assertRaises(ValueError):
            self.desk.calendar_days_carried(date(2030, 1, 15))


class LabelTests(unittest.TestCase):
    """Eleonora's rulings on PR #241: the mean rule's label (Q3) and the #243 band label."""

    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def test_the_labels_are_the_rulings_words(self):
        self.assertEqual(
            self.desk.MEAN_LABEL,
            "flat beyond the 5th and 95th percentiles, so it understates a right-skewed turn",
        )
        self.assertEqual(self.desk.BAND_25_75_LABEL, "not yet calibrated (#243)")

    def test_the_markdown_labels_the_expected_value_and_turn_contribution(self):
        days = SummaryTests.days()
        tables = {1: self.desk.summarise(days, horizon=1, splits=SPLITS)}
        markdown = self.desk._markdown(tables, "2025-01-02", "2025-01-29")
        self.assertIn(self.desk.MEAN_LABEL, markdown)


class PressureDayTagTests(unittest.TestCase):
    """Scheduled pressure days, from the repository's calendar columns."""

    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def _values(self, **override):
        values = {
            "days_to_month_end": 10.0,
            "quarter_end": 0.0,
            "tax_date": 0.0,
            "treasury_settlement_coupons": 0.0,
        }
        values.update(override)
        return values

    def test_an_ordinary_day_carries_no_tag(self):
        self.assertEqual(self.desk.pressure_day_tags(self._values(), date(2025, 7, 9), SPLITS), ())

    def test_the_year_end_is_a_quarter_end_and_a_month_end(self):
        tags = self.desk.pressure_day_tags(
            self._values(days_to_month_end=0.0, quarter_end=1.0), date(2025, 12, 31), SPLITS
        )
        self.assertEqual(tags, ("month_end", "quarter_end", "year_end"))

    def test_a_march_quarter_end_is_not_a_year_end(self):
        tags = self.desk.pressure_day_tags(
            self._values(days_to_month_end=0.0, quarter_end=1.0), date(2025, 3, 31), SPLITS
        )
        self.assertEqual(tags, ("month_end", "quarter_end"))

    def test_the_month_end_window_is_the_split_declarations(self):
        window = SPLITS.month_end_window
        inside = self.desk.pressure_day_tags(
            self._values(days_to_month_end=float(window)), date(2025, 7, 29), SPLITS
        )
        outside = self.desk.pressure_day_tags(
            self._values(days_to_month_end=float(window + 1)), date(2025, 7, 28), SPLITS
        )
        self.assertEqual(inside, ("month_end",))
        self.assertEqual(outside, ())

    def test_tax_dates_and_coupon_settlements(self):
        tags = self.desk.pressure_day_tags(
            self._values(tax_date=1.0, treasury_settlement_coupons=52.0), date(2025, 9, 15), SPLITS
        )
        self.assertEqual(tags, ("tax_date", "coupon_settlement"))

    def test_an_unknown_settlement_is_not_read_as_none(self):
        values = self._values()
        del values["treasury_settlement_coupons"]
        tags = self.desk.pressure_day_tags(values, date(2025, 9, 15), SPLITS)
        self.assertEqual(tags, ())
        self.assertIsNone(self.desk.coupon_settlement_known(values))


class UpperTailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def test_the_plain_statement(self):
        self.assertEqual(
            self.desk.upper_tail_statement(QUANTILE_LEVELS, (-2.0, 0.0, 1.0, 2.0, 20.0)),
            "expected +3.4 bp (flat beyond the 5th and 95th percentiles, so it understates a "
            "right-skewed turn), 5% chance above +20.0 bp",
        )

    def test_a_negative_expectation_keeps_its_sign(self):
        self.assertEqual(
            self.desk.upper_tail_statement(QUANTILE_LEVELS, (-9.0, -8.0, -7.0, -6.0, -5.0)),
            "expected -7.0 bp (flat beyond the 5th and 95th percentiles, so it understates a "
            "right-skewed turn), 5% chance above -5.0 bp",
        )


class ScarcityAsOfTests(unittest.TestCase):
    """The state beside each forecast is the one public at its decision instant.

    `scarcity_at` reads `reserve_scarcity_state` through `InformationRule` at
    the forecast's horizon, and runs `InformationRule.check` on the read
    before it returns a value: a read past the decision instant raises
    `LookAheadError`.

    **Recorded mutation** (CLAUDE.md), 6 October 2026, in a disposable copy
    under /tmp: in `scripts/desk_outputs.py`, `scarcity_from`, the line
    `rule.check(dates, info)` deleted (confirmed applied by grep).
    `test_a_read_past_the_decision_instant_raises` then fails with
    `AssertionError: LookAheadError not raised`; the other tests here stay
    green, because an unforced read is already as-of. Restored, all green.
    """

    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def setUp(self):
        switch = scarcity_inputs_on()
        switch.start()
        self.addCleanup(switch.stop)
        from repo_model.scarcity import with_reserve_scarcity_state

        self.rows = with_reserve_scarcity_state(raw_rows())

    def test_the_state_and_its_buffer_leg_at_the_decision_instant(self):
        # Monday 29 September at h = 1: decision Friday 26 September 16:00,
        # before the H.8 carrying the week ending 17 September (16:15 that day).
        rule = self.desk.scarcity_rule(REGISTRY, horizon=1)
        read = self.desk.scarcity_at(self.rows, rule, DATES.index(date(2025, 9, 29)))
        self.assertEqual(read["decision_instant"], datetime(2025, 9, 26, 16, 0).isoformat())
        self.assertLess(date.fromisoformat(read["read_date"]), date(2025, 9, 17))
        self.assertEqual(read["state"], 2)
        self.assertEqual(read["label"], "tight")
        self.assertEqual(read["buffer"], "buffer gone")
        self.assertEqual(read["on_rrp_bn"], 50.0)

    def test_a_longer_horizon_reads_an_earlier_instant(self):
        # Wednesday 1 October: at h = 1 the new week is public (decision 30
        # September); at h = 3 the decision is Friday 26 September, and it is not.
        index = DATES.index(date(2025, 10, 1))
        short = self.desk.scarcity_at(self.rows, self.desk.scarcity_rule(REGISTRY, horizon=1), index)
        long = self.desk.scarcity_at(self.rows, self.desk.scarcity_rule(REGISTRY, horizon=3), index)
        self.assertEqual(short["state"], 1)
        self.assertEqual(long["state"], 2)
        self.assertEqual(long["decision_instant"], datetime(2025, 9, 26, 16, 0).isoformat())

    def test_rows_on_and_after_the_decision_day_do_not_move_the_read(self):
        from repo_model.data import DailyObservation

        index = DATES.index(date(2025, 9, 29))
        rule = self.desk.scarcity_rule(REGISTRY, horizon=1)
        before = self.desk.scarcity_at(self.rows, rule, index)
        decision_day = DATES.index(date(2025, 9, 26))
        tampered = list(self.rows[:decision_day]) + [
            DailyObservation(row.date, {**row.values, "reserve_scarcity_state": 0.0, "on_rrp": 900.0})
            for row in self.rows[decision_day:]
        ]
        self.assertEqual(self.desk.scarcity_at(tampered, rule, index), before)

    def test_a_read_past_the_decision_instant_raises(self):
        rule = self.desk.scarcity_rule(REGISTRY, horizon=1)
        dates = [row.date for row in self.rows]
        index = dates.index(date(2025, 9, 29))
        info = rule.information_set(dates, index)
        wednesday = dates.index(date(2025, 9, 17))
        forced = info._replace(
            reads=tuple(
                entry._replace(row=wednesday)
                if entry.feature == "reserve_scarcity_state"
                else entry
                for entry in info.reads
            )
        )
        with self.assertRaises(LookAheadError):
            self.desk.scarcity_from(self.rows, rule, dates, forced)


class HistoryLockboxTests(unittest.TestCase):
    """The history scores no day in a locked tier, and refuses before any fit.

    **Recorded mutation**, 6 October 2026, same protocol: in
    `scripts/desk_outputs.py`, `require_history_unlocked`, the line
    `require_unlocked(days, where="desk_outputs.history")` replaced by `pass`
    (confirmed applied by grep). `test_a_blind_tier_day_is_refused` then fails
    with `AssertionError: LookAheadError not raised`. Restored, all green.
    """

    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    def test_a_blind_tier_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            self.desk.require_history_unlocked([date(2025, 12, 31), date(2026, 9, 4)])

    def test_opened_and_pre_2026_days_pass(self):
        self.desk.require_history_unlocked([date(2025, 12, 31), date(2026, 9, 3)])


class SummaryTests(unittest.TestCase):
    """The tables: paired against persistence, split by tag, regime and state."""

    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()

    @staticmethod
    def days():
        days = []
        for position, when in enumerate(
            # Business days only: Martin Luther King Jr. Day (20 January) is closed.
            [date(2025, 1, 2 + offset) for offset in range(0, 28)
             if date(2025, 1, 2 + offset).weekday() < 5 and offset != 18]
        ):
            days.append(
                {
                    "date": when.isoformat(),
                    "tags": ["month_end"] if position % 3 == 0 else [],
                    "regime": "2025-26",
                    "state": position % 2,
                    "published": [-1.0, 0.0, 1.0, 2.0, 3.0],
                    "persistence": [-3.0, -1.0, 1.0, 3.0, 5.0],
                    "outcome_bps": 1.0 if position % 4 else 4.0,
                }
            )
        return days

    def test_a_tag_cell_counts_its_days_and_pairs_the_two_sides(self):
        days = self.days()
        table = self.desk.summarise(days, horizon=1, splits=SPLITS)
        cell = table["by_tag"]["month_end"]
        tagged = [day for day in days if day["tags"]]
        self.assertEqual(cell["days"], len(tagged))
        self.assertEqual(cell["published_coverage"]["count"], len(tagged))
        self.assertIn("interval", cell["crps_persistence_minus_published"])
        self.assertEqual(set(table["by_tag_and_regime"]["month_end"]), {"2025-26"})
        self.assertEqual(set(table["by_tag_and_state"]["month_end"]), {"0", "1"})
        expected_coverage = sum(-1.0 <= day["outcome_bps"] <= 3.0 for day in tagged) / len(tagged)
        self.assertAlmostEqual(cell["published_coverage"]["mean"], expected_coverage)


class LiveOutputsTests(unittest.TestCase):
    """One frozen live file, read at report time; the file itself is untouched."""

    @classmethod
    def setUpClass(cls):
        cls.desk = _desk()
        from test_live_record import _record

        record = _record("2026-09-25")
        targets = ("2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02")
        for target, when in zip(record["targets"], targets):
            target["target_date"] = when
        cls.record = record

    def setUp(self):
        switch = scarcity_inputs_on()
        switch.start()
        self.addCleanup(switch.stop)
        from datetime import timedelta

        from repo_model.data import DailyObservation
        from repo_model.scarcity import with_reserve_scarcity_state

        days, when = [], date(2026, 7, 1)
        while when <= date(2026, 10, 2):
            if when.weekday() < 5 and when != date(2026, 9, 7):
                days.append(when)
            when += timedelta(days=1)
        # 2900 / 23000 is 12.6%, inside the band; ON RRP above the buffer until
        # the decision day, and gone on every row after it.
        self.rows = with_reserve_scarcity_state([
            DailyObservation(day, {
                "sofr": 4.0, "iorb": 4.0, "reserve_balances": 2900.0,
                "bank_total_assets": 23000.0,
                "on_rrp": 150.0 if day <= date(2026, 9, 25) else 5.0,
            })
            for day in days
        ])

    def test_the_four_outputs_per_target(self):
        before = json.dumps(self.record, sort_keys=True)
        report = self.desk.live_outputs(self.record, self.rows, REGISTRY, SPLITS)
        self.assertEqual(json.dumps(self.record, sort_keys=True), before)
        self.assertEqual([t["horizon"] for t in report["targets"]], [1, 2, 3, 4, 5])
        quarter_end = report["targets"][2]
        self.assertEqual(quarter_end["target_date"], "2026-09-30")
        self.assertEqual(quarter_end["tags"], ["month_end", "quarter_end"])
        self.assertEqual(quarter_end["p_above_5bp"], 0.1)
        grid = self.record["distributions"]["published"]["quantiles_bps"]["3"]
        self.assertEqual(quarter_end["statement"], self.desk.upper_tail_statement(QUANTILE_LEVELS, grid))
        # Wednesday 30 September 2026 carries itself, over September's 30 days.
        self.assertAlmostEqual(
            quarter_end["expected_turn_contribution_bps"],
            self.desk.mean_from_quantiles(QUANTILE_LEVELS, grid) / 30,
        )
        self.assertEqual(quarter_end["mean_label"], self.desk.MEAN_LABEL)
        self.assertIsNone(report["targets"][4]["expected_turn_contribution_bps"])
        for target in report["targets"]:
            self.assertEqual(target["published_band_25_75"], "not yet calibrated (#243)")

    def test_the_state_is_read_as_of_the_decision_and_ignores_later_rows(self):
        report = self.desk.live_outputs(self.record, self.rows, REGISTRY, SPLITS)
        states = {json.dumps(t["scarcity"], sort_keys=True) for t in report["targets"]}
        self.assertEqual(len(states), 1)
        state = report["targets"][0]["scarcity"]
        self.assertEqual(state["decision_instant"], datetime(2026, 9, 25, 16, 0).isoformat())
        self.assertLess(date.fromisoformat(state["read_date"]), date(2026, 9, 25))
        self.assertEqual(state["state"], 1)
        self.assertEqual(state["buffer"], "buffer present")


if __name__ == "__main__":
    unittest.main()
