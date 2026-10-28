"""(s3c-mbs): (s3c) with indicators for the settlement days of the agency MBS classes A to D (#1276; H5 step 3).

`metadata/s3c_mbs_1276.json` is the declaration and `metadata/sifma_mbs_1276.json` the source's availability declaration; `repo_model.s3c_mbs` is the arm's
arithmetic and `repo_model.sifma_mbs` the source (`test_sifma_mbs`). What these tests pin: the term table (an indicator is 1 on a class's settlement day
only if the day's year was public at the decision instant of the row `lead` rows before, so a decision before the archive's capture reads 0 and a
training pair reads what its own decision could read); the pooling rule (a class with fewer than 20 settlement days in the window pools the four classes
into one indicator); that the fit recovers planted class effects, equals the direct Huber solution on the same design, leaves every other term as (s3)'s
fit has it, and is (s3)'s estimate element for element where no indicator enters; that the effect in bp is the coefficient times the indicator times the
scale at the anchor; that the one-step guard still refuses a one-step fit; and, in the walk, that (s3) re-forecast inside it is the state-calendar walk's,
that a calendar nobody could yet read moves no forecast and one that was public does, and that no future spread moves a forecast.

Recorded mutations (each applied to the tree, confirmed by grep, the named tests run, and reverted):

* `MbsTable._value`: `instant = datetime.combine(self.dates[decision_row], self._time)` replaced with
  `instant = datetime.combine(self.dates[target_row], self._time)`, so a row reads the calendar as of its own day instead of the decision `lead` rows
  before it. Failed with `AssertionError`: `TableTests.test_a_decision_before_the_capture_reads_zero_and_the_next_one_reads_the_day` (1 != 0 at lead 5)
  and `TableTests.test_a_training_pair_reads_what_its_own_decision_could_read` (lists differ: [1, 1, 1, 1, 1] != [1, 1, 1, 1, 0]), `TableTests.
  test_the_capture_day_itself_is_read_from_the_16_00_decision` (1 != 0), and in the walk `WalkTests.test_the_flags_are_read_only_where_the_year_was_public_at_the_decision`
  and `WalkTests.test_a_calendar_nobody_could_yet_read_moves_no_forecast_and_one_that_was_public_does` (1 != 0): five failures, all `AssertionError`.
* `fit_mbs_terms`: the `@guard_one_step_fit` line deleted. `FitTests.test_a_one_step_fit_is_refused_by_the_guard` failed with `AssertionError` (`'tax_date'`
  not found in the function's own "direct pairs only" message, so the guard's refusal naming the column was gone).
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model import protocol_benchmarks as pb
from repo_model import s3c_mbs as mm
from repo_model import sifma_mbs
from repo_model import spread_mean_reversion as smr
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
PANEL = tpb.published_panel()["rows"]
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
REFIT = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION)
LEVELS = smr.ordinary_levels(PANEL, tpb.SPLITS)
NONE = {name: 0 for name in cal.ALL_TERMS}
SIFMA = sifma_mbs.load_table()
PUBLIC = sifma_mbs.load_public_from()


def index_of(day: str, panel=PANEL) -> int:
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def with_sofr(panel, day: str, sofr_percent: float):
    out = list(panel)
    i = index_of(day, panel)
    out[i] = DailyObservation(panel[i].date, {**panel[i].values, "sofr": sofr_percent})
    return out


def days(*iso):
    return [date.fromisoformat(x) for x in iso]


def business_panel(first: date, n: int):
    out, day = [], first
    while len(out) < n:
        if day.weekday() < 5:
            out.append(DailyObservation(day, {"sofr": 5.0, "iorb": 5.0}))
        day += timedelta(days=1)
    return out


class TableTests(unittest.TestCase):
    """A hand calendar: class A settles on Wed 2020-01-15 and Fri 2020-02-14, B on 2020-01-17; the year 2020 is public from 2019-08-20 19:32:52 UTC."""

    def setUp(self):
        self.panel = business_panel(date(2019, 8, 12), 220)
        self.dates = [r.date for r in self.panel]
        self.sifma = {"A": frozenset({date(2020, 1, 15), date(2020, 2, 14)}), "B": frozenset({date(2020, 1, 17)}), "C": frozenset(), "D": frozenset()}
        self.public = {2020: datetime(2019, 8, 20, 19, 32, 52, tzinfo=sifma_mbs.UTC), 2019: None}
        self.table = mm.MbsTable(self.panel, self.sifma, self.public)

    def row(self, iso):
        return self.dates.index(date.fromisoformat(iso))

    def test_the_terms_are_the_four_classes(self):
        self.assertEqual(self.table.terms, ("mbs_a", "mbs_b", "mbs_c", "mbs_d"))

    def test_a_decision_before_the_capture_reads_zero_and_the_next_one_reads_the_day(self):
        target = self.row("2020-01-15")
        self.assertEqual(self.table.flags_at(5, target)["mbs_a"], 1)  # the decision 5 rows earlier is 2020-01-08, after the capture
        early = business_panel(date(2019, 8, 12), 220)
        late = {2020: datetime(2020, 1, 9, 12, 0, tzinfo=sifma_mbs.UTC)}
        table = mm.MbsTable(early, self.sifma, late)
        self.assertEqual(table.flags_at(5, target)["mbs_a"], 0)  # decision 2020-01-08, before 2020-01-09 12:00 UTC
        self.assertEqual(table.flags_at(4, target)["mbs_a"], 1)  # decision 2020-01-09 at 16:00 ET = 21:00 UTC, after it
        self.assertEqual(table.flags_at(1, target)["mbs_a"], 1)

    def test_the_capture_day_itself_is_read_from_the_16_00_decision(self):
        # captured 2019-08-20 19:32:52 UTC = 15:32:52 EDT: the 16:00 decision of that day reads the year, the decision of the day before does not
        target = self.row("2020-01-15")
        table = mm.MbsTable(self.panel, {**self.sifma, "A": frozenset({self.dates[self.row("2019-08-21")]})}, {2019: self.public[2020]})
        target = self.row("2019-08-21")
        self.assertEqual(table.flags_at(1, target)["mbs_a"], 1)   # decision 2019-08-20, 16:00
        self.assertEqual(table.flags_at(2, target)["mbs_a"], 0)   # decision 2019-08-19

    def test_a_year_without_a_capture_reads_zero_at_every_lead(self):
        sifma = {**self.sifma, "A": frozenset({self.dates[self.row("2019-10-16")]})}
        table = mm.MbsTable(self.panel, sifma, self.public)
        for lead in (1, 2, 3, 4, 5):
            self.assertEqual(table.flags_at(lead, self.row("2019-10-16")), {"mbs_a": 0, "mbs_b": 0, "mbs_c": 0, "mbs_d": 0})

    def test_a_non_settlement_day_is_zero(self):
        self.assertEqual(sum(self.table.flags_at(1, self.row("2020-01-16")).values()), 0)

    def test_the_forecast_read_is_the_target_rows_flags_as_the_decision_could_read_them(self):
        d = self.row("2020-01-14")
        self.assertEqual(self.table.read(1, d), self.table.flags_at(1, d + 1))
        self.assertEqual(self.table.read(3, d), self.table.flags_at(3, d + 3))
        self.assertEqual(self.table.read(3, d)["mbs_b"], 1)  # 2020-01-17 is three rows after 2020-01-14

    def test_a_training_pair_reads_what_its_own_decision_could_read(self):
        """A pair of lead h with target row r reads the figure of the decision at row r - h, whatever origin the pair has."""

        table = mm.MbsTable(self.panel, self.sifma, {2020: datetime(2020, 1, 9, 12, 0, tzinfo=sifma_mbs.UTC)})
        r = self.row("2020-01-15")
        self.assertEqual([table.flags_at(h, r)["mbs_a"] for h in (1, 2, 3, 4, 5)], [1, 1, 1, 1, 0])

    def test_the_pooled_table_is_one_indicator_that_is_the_union_of_the_classes(self):
        table = mm.MbsTable(self.panel, self.sifma, self.public, pooled=True)
        self.assertEqual(table.terms, ("mbs_any",))
        self.assertEqual(table.flags_at(1, self.row("2020-01-15")), {"mbs_any": 1})
        self.assertEqual(table.flags_at(1, self.row("2020-01-17")), {"mbs_any": 1})
        self.assertEqual(table.flags_at(1, self.row("2020-01-16")), {"mbs_any": 0})

    def test_a_row_outside_the_panel_is_refused(self):
        with self.assertRaises(ValueError):
            self.table.flags_at(1, len(self.panel))
        with self.assertRaises(ValueError):
            self.table.flags_at(5, 2)


class CountTests(unittest.TestCase):
    def test_counts_are_settlement_days_on_panel_rows_read_at_lead_one_up_to_the_last_day(self):
        panel = business_panel(date(2019, 8, 12), 220)
        sifma = {"A": frozenset({date(2020, 1, 15), date(2020, 2, 14), date(2019, 10, 16)}), "B": frozenset({date(2020, 1, 17)}), "C": frozenset(), "D": frozenset()}
        public = {2020: datetime(2019, 8, 20, 19, 32, 52, tzinfo=sifma_mbs.UTC)}
        counts = mm.class_counts(panel, sifma, public, last=date(2020, 2, 13))
        self.assertEqual(counts, {"A": 1, "B": 1, "C": 0, "D": 0})

    def test_a_class_with_fewer_than_20_days_pools_the_classes(self):
        self.assertFalse(mm.must_pool({"A": 20, "B": 20, "C": 31, "D": 22}))
        self.assertTrue(mm.must_pool({"A": 20, "B": 19, "C": 31, "D": 22}))
        self.assertEqual(mm.MIN_CLASS_DAYS, 20)

    def test_the_published_panel_counts_under_the_declaration(self):
        counts = mm.class_counts(PANEL, SIFMA, PUBLIC, last=date(2025, 12, 31))
        self.assertEqual(sorted(counts), ["A", "B", "C", "D"])
        self.assertTrue(all(v > 0 for v in counts.values()))
        # 2020, 2021, 2024 and (from 2025-01-19) 2025 are public; 2018, 2019, 2022 and 2023 are not
        self.assertTrue(all(v <= 48 for v in counts.values()))


NO_MBS = ("mbs_a", "mbs_b", "mbs_c", "mbs_d")


def planted(effects=(0.8, 0.0, -0.6, 0.0), n=120, noise=0.3, scale=1.0, quarter=False):
    """Pairs whose standardised residual is `effect_k` on a day of class k, and deterministic noise elsewhere; each class settles on 10 of the 120 days."""

    pairs, mbs = [], []
    for i in range(n):
        flags = dict(NONE)
        if quarter:
            flags["quarter_end"] = 1 if 70 <= i < 85 else 0
        m = {name: 0 for name in NO_MBS}
        if i % 3 == 0:
            m[NO_MBS[(i // 3) % 4]] = 1
        jitter = noise * (((i * 37) % 11) - 5) / 5.0
        y = sum(e * m[name] for e, name in zip(effects, NO_MBS)) + jitter + (2.0 * flags["quarter_end"])
        pairs.append(sc.StatePair(scale * y, scale, flags, None, {}, i, i + 1, {}, False))
        mbs.append(m)
    return pairs, mbs


FIT = dict(regressors=(), terms=cal.NO_FOMC_IORB, training_pairs="direct")


class FitTests(unittest.TestCase):
    def test_planted_class_effects_are_recovered_and_shrunk_by_the_ridge(self):
        pairs, mbs = planted()
        est = mm.fit_mbs_terms(pairs, mbs, mbs_terms=NO_MBS, **FIT)
        self.assertEqual(est.active, NO_MBS)
        self.assertGreater(est.coefficient["mbs_a"], 0.3)
        self.assertLess(est.coefficient["mbs_a"], 0.8)
        self.assertLess(est.coefficient["mbs_c"], -0.2)
        self.assertLess(abs(est.coefficient["mbs_b"]), 0.2)

    def test_the_fit_equals_the_direct_huber_solution_on_the_same_design(self):
        pairs, mbs = planted()
        est = mm.fit_mbs_terms(pairs, mbs, mbs_terms=NO_MBS, **FIT)
        design = [[1.0] + [float(m[n]) for n in NO_MBS] for m in mbs]
        beta, _ = sc.huber(design, [p.raw / p.scale for p in pairs], sc.ROBUST_RIDGE)
        for name, b in zip(NO_MBS, beta[1:]):
            self.assertAlmostEqual(est.coefficient[name], b, places=12)

    def test_the_pool_is_what_the_terms_leave(self):
        pairs, mbs = planted()
        est = mm.fit_mbs_terms(pairs, mbs, mbs_terms=NO_MBS, **FIT)
        residuals = sorted(p.raw / p.scale - sum(est.coefficient[n] * m[n] for n in NO_MBS) for p, m in zip(pairs, mbs))
        self.assertEqual(list(est.state.pool), list(pb.empirical_quantiles(residuals)))

    def test_an_indicator_with_fewer_than_three_days_does_not_enter(self):
        pairs, mbs = planted()
        for m in mbs:
            m["mbs_d"] = 0
        for i in (1, 2):
            mbs[i]["mbs_d"] = 1
        est = mm.fit_mbs_terms(pairs, mbs, mbs_terms=NO_MBS, **FIT)
        self.assertNotIn("mbs_d", est.active)
        self.assertEqual(est.coefficient["mbs_d"], 0.0)
        self.assertEqual(est.counts["mbs_d"], 2)

    def test_where_no_indicator_enters_the_estimate_is_s3s_element_for_element(self):
        pairs, mbs = planted()
        zero = [{name: 0 for name in NO_MBS} for _ in mbs]
        est = mm.fit_mbs_terms(pairs, zero, mbs_terms=NO_MBS, **FIT)
        plain = sc.fit_state_terms(pairs, regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=True, training_pairs="direct")
        self.assertEqual(est.active, ())
        self.assertEqual(est.state, plain)
        self.assertEqual(est.coefficient, {name: 0.0 for name in NO_MBS})

    def test_the_other_terms_still_enter_and_are_fitted_jointly(self):
        pairs, mbs = planted(quarter=True)
        est = mm.fit_mbs_terms(pairs, mbs, mbs_terms=NO_MBS, **FIT)
        self.assertIn("quarter_end", est.state.effect)
        self.assertGreater(est.state.effect["quarter_end"], 1.0)
        self.assertGreater(est.coefficient["mbs_a"], 0.3)
        self.assertEqual(est.state.flagged["mbs_a"], 10)

    def test_the_pooled_fit_has_one_coefficient(self):
        pairs, mbs = planted(effects=(0.7, 0.7, 0.7, 0.7))
        pooled = [{"mbs_any": 1 if any(m.values()) else 0} for m in mbs]
        est = mm.fit_mbs_terms(pairs, pooled, mbs_terms=("mbs_any",), **FIT)
        self.assertEqual(est.active, ("mbs_any",))
        self.assertGreater(est.coefficient["mbs_any"], 0.4)

    def test_the_effect_in_bp_is_the_coefficient_times_the_indicator_times_the_scale(self):
        pairs, mbs = planted()
        est = mm.fit_mbs_terms(pairs, mbs, mbs_terms=NO_MBS, **FIT)
        q = [float(i) for i in range(23)]
        flags = {"mbs_a": 1, "mbs_b": 0, "mbs_c": 0, "mbs_d": 1}
        none = dataclasses.replace(est, coefficient={n: 0.0 for n in NO_MBS})
        out = mm.forecast_leads({1: est, 2: none}, {1: q, 2: q}, {1: flags, 2: flags}, {1: 2.5, 2: 2.5})
        shift = 2.5 * (est.coefficient["mbs_a"] + est.coefficient["mbs_d"])
        self.assertEqual(out[1], [v + shift for v in q])
        self.assertEqual(out[2], q)
        self.assertEqual(mm.effect_bp(est, flags, 2.5), shift)

    def test_a_one_step_fit_is_refused_by_the_guard(self):
        pairs, mbs = planted()
        with self.assertRaises(ValueError) as caught:
            mm.fit_mbs_terms(pairs, mbs, mbs_terms=NO_MBS, regressors=("tax_date",), terms=cal.NO_FOMC_IORB, training_pairs="one_step")
        self.assertIn("tax_date", str(caught.exception))

    def test_one_row_of_indicators_per_pair(self):
        pairs, mbs = planted()
        with self.assertRaises(ValueError):
            mm.fit_mbs_terms(pairs, mbs[:-1], mbs_terms=NO_MBS, **FIT)


class WalkTests(unittest.TestCase):
    """The walk around Monday 2025-01-20 (Martin Luther King Day, no row) and the week of 2025-01-21: the 2025 calendar was captured on Sunday 2025-01-19."""

    DAYS = days("2024-06-03", "2025-01-16", "2025-01-17", "2025-01-21", "2025-01-22")

    @classmethod
    def setUpClass(cls):
        cls.base = cal.TermTable(PANEL, [])
        cls.mbs = mm.MbsTable(PANEL, SIFMA, PUBLIC)
        cls.walk = mm.walk(PANEL, cls.DAYS, cls.base, cls.mbs, **SETTINGS)

    def test_s3_here_is_the_state_calendar_walks_s3_forecast_for_forecast(self):
        theirs = sc.walk(PANEL, self.DAYS, self.base, {}, (sc.ARMS[2],), **SETTINGS)
        self.assertEqual(self.walk.s3, theirs.forecasts[sc.ARMS[2].name])

    def test_the_flags_are_read_only_where_the_year_was_public_at_the_decision(self):
        v = self.walk.values
        # Class C settles on 2025-01-21 and D on 2025-01-23. The 2025 calendar is shown by the capture of Sunday 2025-01-19.
        self.assertEqual(sum(v[date(2025, 1, 17)][1].values()), 0)           # target 2025-01-21 read on Friday the 17th: before the capture
        self.assertEqual(sum(v[date(2025, 1, 17)][4].values()), 0)           # target 2025-01-24 is no settlement day
        self.assertEqual(v[date(2025, 1, 21)][2]["mbs_d"], 1)                # target 2025-01-23 read on the 21st: after the capture
        self.assertEqual(v[date(2025, 1, 16)][3]["mbs_c"], 0)                # target 2025-01-21 read on the 16th, lead 3: before the capture

    def test_a_calendar_nobody_could_yet_read_moves_no_forecast_and_one_that_was_public_does(self):
        # the same walk with the 2025 calendar public from long before: the decision of the 17th then reads class C on the 21st
        early = dict(PUBLIC)
        early[2025] = datetime(2024, 11, 1, tzinfo=sifma_mbs.UTC)
        walk_early = mm.walk(PANEL, days("2025-01-17"), self.base, mm.MbsTable(PANEL, SIFMA, early), **SETTINGS)
        self.assertEqual(walk_early.values[date(2025, 1, 17)][1]["mbs_c"], 1)
        self.assertEqual(self.walk.values[date(2025, 1, 17)][1]["mbs_c"], 0)
        # a calendar that is never public leaves every flag at 0 and every forecast (s3)'s
        none = {year: None for year in PUBLIC}
        walk_none = mm.walk(PANEL, self.DAYS, self.base, mm.MbsTable(PANEL, SIFMA, none), **SETTINGS)
        self.assertEqual(walk_none.forecasts, walk_none.s3)
        for d in self.DAYS:
            for h in range(1, 6):
                self.assertEqual(sum(walk_none.values[d][h].values()), 0)

    def test_where_the_flags_are_zero_the_forecast_is_the_fits_without_the_effect(self):
        for d in self.DAYS:
            for h in range(1, 6):
                if sum(self.walk.values[d][h].values()) == 0:
                    est = self.walk.estimates[self.walk.fit_used[d]][h]
                    self.assertEqual(mm.effect_bp(est, self.walk.values[d][h], 1.0), 0.0)

    def test_every_forecast_has_23_ordered_quantiles(self):
        for leads in self.walk.forecasts.values():
            for q in leads.values():
                self.assertEqual(len(q), 23)
                self.assertEqual(q, sorted(q))

    def test_a_future_spread_moves_no_forecast(self):
        later = with_sofr(PANEL, "2025-02-07", 15.0)
        other = mm.walk(later, self.DAYS, cal.TermTable(later, []), mm.MbsTable(later, SIFMA, PUBLIC), **SETTINGS)
        self.assertEqual(other.forecasts, self.walk.forecasts)

    def test_the_decision_day_of_the_walk_is_refused_off_the_panel(self):
        from repo_model.scoring_protocol import ProtocolError

        with self.assertRaises(ProtocolError):
            mm.walk(PANEL, [date(2025, 1, 18)], self.base, self.mbs, **SETTINGS)


if __name__ == "__main__":
    unittest.main()
