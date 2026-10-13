"""The spread on announced risk dates: the day set, the calendar benchmark and the type x state model (#693; H6, development tier).

`metadata/risk_date_spread_693.json` is the declaration; `repo_model.risk_date_spread` is its arithmetic. Stdlib only.

What these tests pin: the day-type precedence against a hand reading of the calendar columns; the risk-date calendar benchmark
(the trailing year's spreads on days of the target's risk type) against a hand reading of the panel; the type x scarcity-state
model (a cell of at least `MIN_CELL` days of the target's type and state group in the trailing two years, else the type alone);
the as-of guard (a sample row after the anchor is refused, and a change to every spread after the anchor moves no forecast); and
the state group labels.

Recorded mutation (the new leakage guard; run on `test_a_future_spread_moves_no_forecast` and
`test_the_sample_stops_at_the_anchor`, then restored):

* `sample_rows`: `range(first, anchor + 1)` replaced with `range(first, anchor + 2)`, so the row after the anchor, whose spread
  was not public at the decision instant, is sampled. Both tests failed with `LookAheadError` ("... reads ..., after ..., the
  last row public at the decision instant", raised by `protocol_benchmarks._require_public`); restored, both pass.
"""

from __future__ import annotations

import dataclasses
import unittest

from repo_model import protocol_benchmarks as pb
from repo_model import risk_date_spread as rds
from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb


def panel_and_settings():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)


def index_of(panel, day):
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


def synthetic_states(panel, modulus=4):
    """A state for every row and lead that depends only on the date, so a test can hand-count a cell."""
    return {h: {row.date: float(row.date.toordinal() % modulus) for row in panel} for h in sp.HORIZONS}


class DayTypeTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()

    def type_of(self, row):
        return rds.risk_day_type(row.date, row.values, tpb.SPLITS)

    def test_the_precedence_is_quarter_end_month_end_tax_date_settlement(self):
        seen = {}
        for row in self.panel:
            kind = self.type_of(row)
            reporting = tpb.SPLITS.reporting_day_type(row.date, row.values)
            coupons = float(row.values.get("treasury_settlement_coupons") or 0.0)
            if reporting in ("quarter_end", "month_end", "tax_date"):
                self.assertEqual(kind, reporting)
            elif coupons > 0.0:
                self.assertEqual(kind, "settlement")
            else:
                self.assertIsNone(kind)
            seen[kind] = seen.get(kind, 0) + 1
        self.assertEqual(set(seen) - {None}, set(rds.RISK_TYPES))

    def test_a_coupon_settlement_on_an_ordinary_day_is_a_settlement_day(self):
        row = next(
            r for r in self.panel
            if tpb.SPLITS.reporting_day_type(r.date, r.values) == "ordinary"
            and float(r.values.get("treasury_settlement_coupons") or 0.0) > 0.0
        )
        self.assertEqual(self.type_of(row), "settlement")

    def test_an_ordinary_day_with_no_coupon_settlement_is_not_a_risk_date(self):
        row = next(
            r for r in self.panel
            if tpb.SPLITS.reporting_day_type(r.date, r.values) == "ordinary"
            and not float(r.values.get("treasury_settlement_coupons") or 0.0) > 0.0
        )
        self.assertIsNone(self.type_of(row))


class StateGroupTests(unittest.TestCase):

    def test_states_zero_and_one_are_low_and_two_and_three_high(self):
        self.assertEqual([rds.state_group(s) for s in (0.0, 1.0, 2.0, 3.0)], ["low", "low", "high", "high"])

    def test_a_missing_state_is_unknown(self):
        self.assertEqual(rds.state_group(None), "unknown")

    def test_a_state_outside_zero_to_three_is_refused(self):
        for bad in (-1.0, 4.0, 1.5):
            with self.subTest(state=bad):
                with self.assertRaises(ValueError):
                    rds.state_group(bad)


class CalendarBenchmarkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()

    def hand_sample(self, t, kind):
        """The spreads, sorted, of the trailing year's rows at or before the anchor whose risk type is `kind`."""
        anchor = pb._anchor(self.panel, t, tpb.REGISTRY, tpb.DECISION)
        start = pb.years_before(self.panel[t].date, 1)
        return sorted(
            r.spread_bps for r in self.panel[: anchor + 1]
            if r.date > start and rds.risk_day_type(r.date, r.values, tpb.SPLITS) == kind
        )

    def test_it_is_the_trailing_years_spreads_on_days_of_the_targets_type(self):
        t = index_of(self.panel, "2022-03-28")
        out = rds.calendar_forecast(self.panel, t, **self.settings)
        self.assertTrue(out)
        for h, quantiles in out.items():
            target = self.panel[t + h]
            kind = rds.risk_day_type(target.date, target.values, tpb.SPLITS)
            with self.subTest(lead=h, kind=kind):
                self.assertIsNotNone(kind)
                self.assertEqual(quantiles, pb.empirical_quantiles(self.hand_sample(t, kind)))
                self.assertEqual(len(quantiles), len(sp.GRID))

    def test_leads_whose_target_is_not_a_risk_date_have_no_forecast(self):
        t = index_of(self.panel, "2022-03-28")
        out = rds.calendar_forecast(self.panel, t, **self.settings)
        for h in sp.HORIZONS:
            target = self.panel[t + h]
            risk = rds.risk_day_type(target.date, target.values, tpb.SPLITS) is not None
            self.assertEqual(h in out, risk)

    def test_the_median_is_the_point_forecast(self):
        quantiles = list(range(len(sp.GRID)))
        self.assertEqual(sp.GRID[rds.MEDIAN_AT], 0.5)
        self.assertEqual(rds.median(quantiles), rds.MEDIAN_AT)


class TypeStateModelTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.states = synthetic_states(cls.panel)
        cls.t = index_of(cls.panel, "2022-03-28")
        cls.anchor = pb._anchor(cls.panel, cls.t, tpb.REGISTRY, tpb.DECISION)

    def hand_cell(self, h, kind, group, years=2):
        start = pb.years_before(self.panel[self.t].date, years)
        return sorted(
            r.spread_bps for r in self.panel[: self.anchor + 1]
            if r.date > start and rds.risk_day_type(r.date, r.values, tpb.SPLITS) == kind
            and (group is None or rds.state_group(self.states[h][r.date]) == group)
        )

    def test_a_full_cell_is_the_types_and_state_groups_days_of_the_trailing_two_years(self):
        out = rds.type_state_forecast(self.panel, self.t, self.states, min_cell=1, **self.settings)
        self.assertTrue(out.quantiles)
        for h, quantiles in out.quantiles.items():
            target = self.panel[self.t + h]
            kind = rds.risk_day_type(target.date, target.values, tpb.SPLITS)
            group = rds.state_group(self.states[h][target.date])
            with self.subTest(lead=h, kind=kind, group=group):
                self.assertEqual(out.basis[h], "cell")
                self.assertEqual(quantiles, pb.empirical_quantiles(self.hand_cell(h, kind, group)))

    def test_a_thin_cell_falls_back_to_the_type_alone_and_says_so(self):
        out = rds.type_state_forecast(self.panel, self.t, self.states, min_cell=10_000, **self.settings)
        for h, quantiles in out.quantiles.items():
            target = self.panel[self.t + h]
            kind = rds.risk_day_type(target.date, target.values, tpb.SPLITS)
            with self.subTest(lead=h):
                self.assertEqual(out.basis[h], "type")
                self.assertEqual(quantiles, pb.empirical_quantiles(self.hand_cell(h, kind, None)))

    def test_an_unknown_state_at_the_target_uses_the_type_alone(self):
        states = {h: dict(by_day) for h, by_day in self.states.items()}
        for h in sp.HORIZONS:
            states[h][self.panel[self.t + h].date] = None
        out = rds.type_state_forecast(self.panel, self.t, states, min_cell=1, **self.settings)
        self.assertTrue(out.quantiles)
        self.assertEqual(set(out.basis.values()), {"type"})

    def test_the_default_minimum_cell_is_declared(self):
        self.assertEqual(rds.MIN_CELL, 10)
        self.assertEqual(rds.CELL_YEARS, pb.B1_YEARS)

    def test_the_forecast_covers_the_risk_date_leads_only(self):
        out = rds.type_state_forecast(self.panel, self.t, self.states, **self.settings)
        calendar = rds.calendar_forecast(self.panel, self.t, **self.settings)
        self.assertEqual(set(out.quantiles), set(calendar))


class AsOfTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.states = synthetic_states(cls.panel)
        cls.t = index_of(cls.panel, "2022-03-28")
        cls.anchor = pb._anchor(cls.panel, cls.t, tpb.REGISTRY, tpb.DECISION)

    def shocked(self):
        panel = list(self.panel)
        for i in range(self.anchor + 1, len(panel)):
            panel[i] = with_spread(panel[i], 250.0 + i)
        return panel

    def test_a_future_spread_moves_no_forecast(self):
        panel = self.shocked()
        self.assertEqual(
            rds.calendar_forecast(self.panel, self.t, **self.settings),
            rds.calendar_forecast(panel, self.t, **self.settings),
        )
        self.assertEqual(
            rds.type_state_forecast(self.panel, self.t, self.states, **self.settings),
            rds.type_state_forecast(panel, self.t, self.states, **self.settings),
        )

    def test_the_sample_stops_at_the_anchor(self):
        for years in (rds.CALENDAR_YEARS, rds.CELL_YEARS):
            rows = rds.sample_rows(self.panel, self.t, self.anchor, years=years)
            with self.subTest(years=years):
                self.assertTrue(rows)
                self.assertLessEqual(max(rows), self.anchor)

    def test_a_row_after_the_anchor_is_refused_by_the_guard(self):
        late = self.anchor + 1
        with self.assertRaises(LookAheadError):
            pb._require_public([late], self.anchor, [r.date for r in self.panel], "a test read")

    def test_the_anchor_spread_does_move_the_calendar_forecast_not_at_all_and_the_persistence_one(self):
        # the calendar benchmark is a distribution of past spreads of one type: moving the anchor's spread moves it only when
        # the anchor row is itself of the target's type; the sample of a quarter-end target excludes an ordinary anchor
        panel = list(self.panel)
        panel[self.anchor] = with_spread(panel[self.anchor], 400.0)
        base = rds.calendar_forecast(self.panel, self.t, **self.settings)
        moved = rds.calendar_forecast(panel, self.t, **self.settings)
        anchor_row = self.panel[self.anchor]
        kind = rds.risk_day_type(anchor_row.date, anchor_row.values, tpb.SPLITS)
        for h in base:
            target = self.panel[self.t + h]
            same = rds.risk_day_type(target.date, target.values, tpb.SPLITS) == kind
            self.assertEqual(base[h] != moved[h], same)

    def test_a_decision_without_the_target_rows_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            rds.calendar_forecast(self.panel[:-1], len(self.panel) - 2, **self.settings)

    def test_no_sample_of_the_targets_type_in_the_window_is_refused(self):
        # a window of zero years has no row after the decision day less zero years but the anchor chain: force it empty
        with self.assertRaises(sp.ProtocolError):
            rds.require_sample([], "quarter_end", self.panel[self.t].date)


if __name__ == "__main__":
    unittest.main()
