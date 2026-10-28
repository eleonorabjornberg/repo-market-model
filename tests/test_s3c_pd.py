"""(s3c-pd): (s3c) with primary dealers' reverse repo plus securities borrowed as a state input (#1296; H5 step 3, ledger item 72 on #1116).

`metadata/s3c_pd_1296.json` is the declaration, `metadata/sources_pd_financing_1296.json` declares the source and its availability, and
`repo_model.s3c_pd` is the arithmetic. What these tests pin: the level is the sum of the four declared New York Fed totals in USD billions
and a withheld figure (`*`) is no observation, never 0; the release instant (6 market business days after the as-of Wednesday, 16:30, shifted
by a holiday); that a week released after the decision instant is refused (`LookAheadError`) and that the decision on the release day itself,
at 16:00, reads the week before it while the next business day's reads the new one; the state (the z-score of the latest public level
against the year before it, `None` when fewer than 13 of the 52 weeks before it have a level, or when
their spread is zero; the latest public level is carried over withheld weeks, and the number skipped is reported); that a week nobody could yet read moves no state and no forecast and one that
was public does; that the fit recovers a planted effect, shrunk by the ridge, takes the state in standardised units as it is, and leaves every
other term as (s3)'s fit has it; that where the term is not active the estimate and the forecast are (s3)'s, element for element; that the
effect in bp is the coefficient times the state times the anchor's scale; that a training pair reads the state of its own decision day; that
the one-step guard still refuses a one-step fit; that the snapshot is the one its manifest names; and that the proposed registry entry passes
the registry's own release-lag and provenance checks.

Recorded mutations (each applied to the tree, confirmed by grep, the named test run, and reverted):

* `public_weeks`: `public = [week for week in levels if release_instant(week) <= instant]` replaced with
  `public = [week for week in levels if release_instant(week).date() <= instant.date()]`, so the decision at 16:00 on the release day reads
  the week released at 16:30 the same day. Six tests failed: `StateTests.test_a_week_nobody_could_yet_read_moves_no_state`,
  `StateTests.test_a_day_before_the_snapshot_has_no_state_and_the_last_scored_day_has_one`, `StateTests.test_the_states_table_keys_every_panel_day`
  and the `WalkTests` class set-up all with `LookAheadError` (raised by `read_level`, which `state_at` calls on every week it reads), and
  `ReleaseDayTests.test_the_decision_on_the_release_day_reads_the_week_before` and
  `StateTests.test_a_withheld_latest_week_carries_the_latest_public_level_and_reports_the_weeks_skipped` with `AssertionError`
  (`2026-05-27 != 2026-05-20`, `2025-02-26 != 2025-02-19`).
* `read_level`: `if release_instant(asof) > instant:` replaced with `if release_instant(asof).date() > instant.date():`.
  `ReleaseDayTests.test_a_week_released_at_16_30_is_refused_at_16_00_the_same_day` failed with `AssertionError` (`LookAheadError` not raised).
* `refit`: `values.append(sc.pair_state(states, dates, origin, lag, decision_index))` replaced with
  `values.append(sc.read_state(states, dates, decision_index, decision_index))`, so every training pair reads the state of the day being
  forecast. `RefitTests.test_a_training_pair_reads_the_state_of_its_own_decision_day` failed with `AssertionError` (`497 != 249` at lead 1: the number of pairs with a
  state differs from the independent count).
* `fit_pd_terms`: the `@guard_one_step_fit` line deleted. `FitTests.test_a_one_step_fit_is_refused_by_the_guard` failed with `AssertionError`
  (`'tax_date'` not found in the function's own "trains on direct pairs only" message, so the guard's refusal naming the column was gone).
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import statistics
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model import contract, registry as registry_module
from repo_model import protocol_benchmarks as pb
from repo_model import s3c_pd as pd
from repo_model import spread_mean_reversion as smr
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "tests" / "fixtures" / "snapshots" / "nyfed-pd-financing"
SOURCE_DECLARATION = ROOT / "metadata" / "sources_pd_financing_1296.json"
PANEL = tpb.published_panel()["rows"]
DATES = [row.date for row in PANEL]
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
REFIT = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION)
LEVELS = smr.ordinary_levels(PANEL, tpb.SPLITS)
NONE = {name: 0 for name in cal.ALL_TERMS}
SNAPSHOT_LEVELS = pd.load_levels(SNAPSHOT)


def wednesdays(first: date, n: int):
    return [first + timedelta(days=7 * i) for i in range(n)]


def weekly(values, first=date(2024, 1, 3)):
    """A level table of consecutive Wednesdays from `first` holding `values` (`None` is a withheld week)."""

    return dict(zip(wednesdays(first, len(values)), values))


def days(*iso):
    return [date.fromisoformat(x) for x in iso]


class LevelTests(unittest.TestCase):

    def test_the_level_is_the_sum_of_the_four_totals_in_billions(self):
        raw = {key: {r["asofdate"]: r["value"] for r in json.loads((SNAPSHOT / f"{key}.json").read_text())["pd"]["timeseries"]} for key in pd.SERIES}
        day = "2026-08-26"
        expected = sum(int(raw[key][day]) for key in pd.SERIES) / 1000.0
        self.assertAlmostEqual(SNAPSHOT_LEVELS[date(2026, 8, 26)], expected)
        self.assertGreater(expected, 3000.0)  # trillions of dollars of Treasury financing, in billions

    def test_a_withheld_total_is_no_observation_never_zero(self):
        raw = json.loads((SNAPSHOT / "PDSIRRA-UTSETTOT.json").read_text())["pd"]["timeseries"]
        starred = [date.fromisoformat(r["asofdate"]) for r in raw if r["value"] == "*"]
        self.assertTrue(starred)
        for day in starred:
            self.assertIsNone(SNAPSHOT_LEVELS[day])
        self.assertTrue(all(v is None or v > 0.0 for v in SNAPSHOT_LEVELS.values()))

    def test_the_snapshot_covers_the_decision_window_and_every_week_once(self):
        self.assertLessEqual(min(SNAPSHOT_LEVELS), date(2015, 1, 7))
        self.assertGreaterEqual(max(SNAPSHOT_LEVELS), date(2026, 9, 2))
        self.assertTrue(all(d.weekday() == 2 for d in SNAPSHOT_LEVELS), "every as-of date is a Wednesday")

    def _copy(self):
        tmp = tempfile.TemporaryDirectory()
        for key in pd.SERIES:
            (Path(tmp.name) / f"{key}.json").write_bytes((SNAPSHOT / f"{key}.json").read_bytes())
        return tmp

    def test_a_value_that_is_neither_a_number_nor_a_star_is_refused(self):
        with self._copy() as tmp:
            path = Path(tmp) / pd.SERIES[0]
            path = path.with_suffix(".json")
            body = json.loads(path.read_text())
            body["pd"]["timeseries"][5]["value"] = "n/a"
            path.write_text(json.dumps(body))
            with self.assertRaises(ValueError):
                pd.load_levels(Path(tmp))

    def test_series_over_different_dates_are_refused(self):
        with self._copy() as tmp:
            path = Path(tmp) / f"{pd.SERIES[1]}.json"
            body = json.loads(path.read_text())
            body["pd"]["timeseries"].pop()
            path.write_text(json.dumps(body))
            with self.assertRaises(ValueError):
                pd.load_levels(Path(tmp))

    def test_a_missing_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                pd.load_levels(Path(tmp))


class ReleaseDayTests(unittest.TestCase):
    """The week of Wednesday 2026-08-26 is released on Thursday 2026-09-03 at 16:30 (`metadata/sources.json`, `nyfed_fr2004`)."""

    WEEK = date(2026, 8, 26)

    def test_the_release_is_six_business_days_after_the_wednesday_at_16_30(self):
        self.assertEqual(pd.release_instant(self.WEEK), datetime(2026, 9, 3, 16, 30))

    def test_a_holiday_shifts_the_release(self):
        # Wednesday 18 November 2026: Thanksgiving (the 26th) is closed, so six business days end on Friday the 27th
        self.assertEqual(pd.release_instant(date(2026, 11, 18)), datetime(2026, 11, 27, 16, 30))

    def test_a_week_released_at_16_30_is_refused_at_16_00_the_same_day(self):
        levels = weekly([1.0, 2.0], first=self.WEEK)
        with self.assertRaises(LookAheadError):
            pd.read_level(levels, self.WEEK, date(2026, 9, 3))
        self.assertEqual(pd.read_level(levels, self.WEEK, date(2026, 9, 4)), 1.0)

    def test_a_week_is_refused_before_its_release_and_read_after(self):
        levels = weekly([1.0], first=self.WEEK)
        for day in days("2026-08-26", "2026-08-31", "2026-09-02"):
            with self.assertRaises(LookAheadError):
                pd.read_level(levels, self.WEEK, day)
        self.assertEqual(pd.read_level(levels, self.WEEK, date(2026, 9, 10)), 1.0)

    def test_the_decision_on_the_release_day_reads_the_week_before(self):
        values = [float(i) for i in range(1, 60)]
        levels = weekly(values, first=date(2025, 5, 7))
        thursday, friday = date(2026, 6, 4), date(2026, 6, 5)  # the week of Wednesday 2026-05-27 is released on Thursday 4 June
        self.assertEqual(pd.latest_public_week(levels, thursday), date(2026, 5, 20))
        self.assertEqual(pd.latest_public_week(levels, friday), date(2026, 5, 27))

    def test_a_week_not_in_the_snapshot_is_refused(self):
        with self.assertRaises(ValueError):
            pd.read_level({}, self.WEEK, date(2026, 9, 10))


class StateTests(unittest.TestCase):

    FIRST = date(2024, 1, 3)

    def levels(self, n=70, withhold=()):
        values = [100.0 + (i % 7) * 3.0 + i * 0.5 for i in range(n)]
        for i in withhold:
            values[i] = None
        return weekly(values, first=self.FIRST), values

    def decision_for(self, levels, week):
        return pd.release_instant(week).date() + timedelta(days=1)

    def test_the_state_is_the_z_score_against_the_year_before_the_latest_public_week(self):
        levels, values = self.levels()
        week = wednesdays(self.FIRST, 70)[60]
        day = self.decision_for(levels, week)
        trailing = values[8:60]  # the 52 weeks before week 60
        expected = (values[60] - statistics.fmean(trailing)) / statistics.stdev(trailing)
        self.assertAlmostEqual(pd.state_at(levels, day), expected, places=12)

    def test_a_withheld_latest_week_carries_the_latest_public_level_and_reports_the_weeks_skipped(self):
        levels, values = self.levels(withhold=(59, 60))
        weeks = wednesdays(self.FIRST, 70)
        day = self.decision_for(levels, weeks[60])
        self.assertEqual(pd.latest_public_week(levels, day), weeks[60])
        self.assertEqual(pd.latest_defined_week(levels, day), weeks[58])
        self.assertEqual(pd.skipped_weeks(levels, day), 2)
        trailing = [x for x in values[6:58] if x is not None]  # the 52 weeks before week 58
        expected = (values[58] - statistics.fmean(trailing)) / statistics.stdev(trailing)
        self.assertAlmostEqual(pd.state_at(levels, day), expected, places=12)
        # the day before the withheld week is released, week 60 is not yet public: the same level, two weeks skipped less one
        before = pd.release_instant(weeks[60]).date()
        self.assertEqual(pd.latest_public_week(levels, before), weeks[59])
        self.assertEqual(pd.skipped_weeks(levels, before), 1)

    def test_nothing_is_skipped_when_the_latest_public_week_has_a_level(self):
        levels, _ = self.levels()
        self.assertEqual(pd.skipped_weeks(levels, self.decision_for(levels, wednesdays(self.FIRST, 70)[60])), 0)
        self.assertIsNone(pd.skipped_weeks(levels, date(2020, 1, 1)))

    def test_no_public_level_gives_no_state(self):
        levels = weekly([None] * 70, first=self.FIRST)
        self.assertIsNone(pd.state_at(levels, date(2025, 12, 1)))
        self.assertIsNone(pd.latest_defined_week(levels, date(2025, 12, 1)))

    def test_fewer_than_13_defined_weeks_in_the_year_give_no_state(self):
        levels, _ = self.levels(withhold=tuple(range(9, 48)))  # 39 of the 52 weeks before week 60 withheld: 13 left
        week = wednesdays(self.FIRST, 70)[60]
        self.assertIsNotNone(pd.state_at(levels, self.decision_for(levels, week)))
        fewer, _ = self.levels(withhold=tuple(range(9, 49)))  # 40 withheld: 12 left
        self.assertIsNone(pd.state_at(fewer, self.decision_for(fewer, week)))

    def test_a_flat_year_gives_no_state(self):
        levels = weekly([50.0] * 70, first=self.FIRST)
        self.assertIsNone(pd.state_at(levels, date(2025, 12, 1)))

    def test_no_public_week_gives_no_state(self):
        self.assertIsNone(pd.state_at(weekly([1.0, 2.0], first=date(2026, 6, 3)), date(2026, 6, 4)))

    def test_a_week_nobody_could_yet_read_moves_no_state(self):
        levels, values = self.levels()
        weeks = wednesdays(self.FIRST, 70)
        day = pd.release_instant(weeks[60]).date()  # the release day of week 60 itself, at 16:00 week 60 is not public
        moved = dict(levels)
        moved[weeks[60]] = 1.0e6
        moved[weeks[61]] = -1.0e6
        self.assertEqual(pd.state_at(moved, day), pd.state_at(levels, day))
        later = day + timedelta(days=1)
        self.assertNotEqual(pd.state_at(moved, later), pd.state_at(levels, later))

    def test_the_states_table_keys_every_panel_day(self):
        states = pd.decision_states(SNAPSHOT_LEVELS, DATES)
        self.assertEqual(sorted(states), DATES)
        self.assertTrue(any(v is not None for v in states.values()))

    def test_a_day_before_the_snapshot_has_no_state_and_the_last_scored_day_has_one(self):
        states = pd.decision_states(SNAPSHOT_LEVELS, [date(2013, 5, 1), date(2013, 6, 3), date(2026, 9, 3)])
        self.assertIsNone(states[date(2013, 5, 1)])
        self.assertIsNone(states[date(2013, 6, 3)])  # fewer than 13 earlier weeks
        self.assertIsNotNone(states[date(2026, 9, 3)])


def planted(effect=0.6, n=80, with_state=60, noise=0.3, scale=1.0):
    """Pairs whose standardised residual is `effect * state` plus deterministic noise; `with_state` of them have a state."""

    pairs, values = [], []
    for i in range(n):
        x = (((i * 13) % 17) - 8) / 4.0 if i < with_state else None
        jitter = noise * (((i * 37) % 11) - 5) / 5.0
        pairs.append(sc.StatePair(scale * (effect * (0.0 if x is None else x) + jitter), scale, dict(NONE), None, {}, i, i + 1, {}, False))
        values.append(x)
    return pairs, values


FIT = dict(regressors=(), terms=cal.NO_FOMC_IORB, training_pairs="direct")


class FitTests(unittest.TestCase):

    def test_a_planted_effect_is_recovered_and_shrunk_by_the_ridge(self):
        pairs, values = planted()
        est = pd.fit_pd_terms(pairs, values, **FIT)
        self.assertTrue(est.active)
        self.assertEqual(est.pd_pairs, 60)
        self.assertGreater(est.coefficient, 0.45)
        self.assertLess(est.coefficient, 0.6)  # ridge 5 shrinks toward 0

    def test_the_fit_equals_the_direct_huber_solution_on_the_same_design(self):
        pairs, values = planted()
        est = pd.fit_pd_terms(pairs, values, **FIT)
        design = [[1.0, 0.0 if x is None else x] for x in values]
        beta, _ = sc.huber(design, [p.raw / p.scale for p in pairs], sc.ROBUST_RIDGE)
        self.assertAlmostEqual(est.coefficient, beta[1], places=12)

    def test_the_state_enters_in_its_own_units_while_the_target_is_divided_by_the_scale(self):
        pairs, values = planted(scale=2.0)
        est = pd.fit_pd_terms(pairs, values, **FIT)
        design = [[1.0, 0.0 if x is None else x] for x in values]
        beta, _ = sc.huber(design, [p.raw / p.scale for p in pairs], sc.ROBUST_RIDGE)
        self.assertAlmostEqual(est.coefficient, beta[1], places=12)

    def test_the_pool_is_what_the_term_leaves(self):
        pairs, values = planted()
        est = pd.fit_pd_terms(pairs, values, **FIT)
        residuals = sorted(p.raw / p.scale - est.coefficient * (0.0 if x is None else x) for p, x in zip(pairs, values))
        self.assertEqual(list(est.state.pool), list(pb.empirical_quantiles(residuals)))

    def test_fewer_than_60_pairs_with_a_state_leave_the_estimate_as_s3s(self):
        pairs, values = planted(with_state=59)
        est = pd.fit_pd_terms(pairs, values, **FIT)
        plain = sc.fit_state_terms(pairs, regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=True, training_pairs="direct")
        self.assertFalse(est.active)
        self.assertEqual(est.coefficient, 0.0)
        self.assertEqual(est.state, plain)
        self.assertEqual(est.pd_pairs, 59)

    def test_with_the_state_active_the_calendar_terms_still_enter_and_are_fitted_jointly(self):
        pairs, values = [], []
        for i in range(90):
            flags = dict(NONE)
            flags["quarter_end"] = 1 if 40 <= i < 55 else 0
            x = (((i * 13) % 17) - 8) / 4.0
            pairs.append(sc.StatePair(2.0 * flags["quarter_end"] + 0.5 * x + 0.3 * (((i * 37) % 11) - 5) / 5.0, 1.0, flags, None, {}, i, i + 1, {}, False))
            values.append(x)
        est = pd.fit_pd_terms(pairs, values, **FIT)
        self.assertIn("quarter_end", est.state.effect)
        self.assertGreater(est.state.effect["quarter_end"], 1.0)
        self.assertGreater(est.coefficient, 0.2)
        self.assertEqual(est.state.flagged[pd.PD], 90)

    def test_the_effect_in_bp_is_the_coefficient_times_the_state_times_the_scale(self):
        pairs, values = planted()
        est = pd.fit_pd_terms(pairs, values, **FIT)
        q = [float(i) for i in range(23)]
        out = pd.forecast_leads({1: est, 2: dataclasses.replace(est, coefficient=0.0)}, {1: q, 2: q}, -1.5, 2.0)
        self.assertEqual(out[1], [v + est.coefficient * -1.5 * 2.0 for v in q])
        self.assertEqual(out[2], q)
        self.assertEqual(pd.forecast_leads({1: est}, {1: q}, None, 2.0)[1], q)

    def test_a_one_step_fit_is_refused_by_the_guard(self):
        pairs, values = planted()
        with self.assertRaises(ValueError) as caught:
            pd.fit_pd_terms(pairs, values, regressors=("tax_date",), terms=cal.NO_FOMC_IORB, training_pairs="one_step")
        self.assertIn("tax_date", str(caught.exception))

    def test_one_state_per_pair(self):
        pairs, values = planted()
        with self.assertRaises(ValueError):
            pd.fit_pd_terms(pairs, values[:-1], **FIT)


def index_of(day: str) -> int:
    return next(i for i, row in enumerate(PANEL) if row.date.isoformat() == day)


class RefitTests(unittest.TestCase):

    D = index_of("2024-06-03")

    def setUp(self):
        self.table = cal.TermTable(PANEL, [])
        self.base = smr.fit(PANEL, self.D, levels=LEVELS, **SETTINGS)

    def test_a_training_pair_reads_the_state_of_its_own_decision_day(self):
        # a state defined on the odd rows only: a pair is counted exactly when its decision row (origin + lag) is odd
        states = {d: (1.0 if i % 2 else None) for i, d in enumerate(DATES)}
        mine, _ = pd.refit(PANEL, self.D, self.table, states, levels=LEVELS, base=self.base, **REFIT)
        anchor = pb._anchor(PANEL, self.D, tpb.REGISTRY, tpb.DECISION)
        lag = self.D - anchor
        rows = smr.training_rows(PANEL, self.D, anchor, lag=lag, levels=LEVELS)
        for h in (1, 3):
            expected = sum(1 for origin, _t in rows[h] if (origin + lag) % 2 == 1)
            self.assertGreater(expected, 0)
            self.assertEqual(mine[h].pd_pairs, expected, f"lead {h}")

    def test_a_state_after_the_decision_is_refused(self):
        states = {d: 1.0 for d in DATES}
        with self.assertRaises(LookAheadError):
            sc.pair_state(states, DATES, self.D, 1, self.D)

    def test_without_a_state_every_lead_is_s3s_estimate_exactly(self):
        mine, s3 = pd.refit(PANEL, self.D, self.table, {d: None for d in DATES}, levels=LEVELS, base=self.base, **REFIT)
        for h in (1, 2, 3, 4, 5):
            self.assertFalse(mine[h].active)
            self.assertEqual(mine[h].state, s3[h])


class WalkTests(unittest.TestCase):
    """The walk around the first days of June 2024 on the real snapshot."""

    DAYS = days("2024-05-30", "2024-05-31", "2024-06-03", "2024-06-04", "2024-06-05")

    @classmethod
    def setUpClass(cls):
        cls.table = cal.TermTable(PANEL, [])
        cls.states = pd.decision_states(SNAPSHOT_LEVELS, DATES)
        cls.walk = pd.walk(PANEL, cls.DAYS, cls.table, cls.states, **SETTINGS)

    def test_s3_here_is_the_state_calendar_walks_s3_forecast_for_forecast(self):
        theirs = sc.walk(PANEL, self.DAYS, self.table, {}, (sc.ARMS[2],), **SETTINGS)
        self.assertEqual(self.walk.s3, theirs.forecasts[sc.ARMS[2].name])

    def test_the_walk_reads_each_days_own_state(self):
        for d in self.DAYS:
            self.assertEqual(self.walk.values[d], self.states[d])

    def test_every_forecast_has_23_ordered_quantiles(self):
        for leads in self.walk.forecasts.values():
            for q in leads.values():
                self.assertEqual(len(q), 23)
                self.assertEqual(q, sorted(q))

    def test_with_the_term_active_the_forecast_is_s3s_pool_shape_plus_the_effect_in_bp(self):
        d = date(2024, 6, 3)
        refit_day = self.walk.fit_used[d]
        est = self.walk.estimates[refit_day]
        base = smr.fit(PANEL, index_of(refit_day.isoformat()), levels=LEVELS, **SETTINGS)
        arm = sc.ARMS[2]
        ours, _ = sc.forecast(
            PANEL, index_of(d.isoformat()), {arm.name: {h: e.state for h, e in est.items()}}, self.table, {}, (arm,),
            levels=LEVELS, base=base, **REFIT)
        for h in (1, 3):
            self.assertTrue(est[h].active, f"lead {h}")
            self.assertIsNotNone(self.walk.values[d])
            shift = est[h].coefficient * self.walk.values[d] * self.walk.scales[d]
            self.assertNotEqual(shift, 0.0)
            self.assertEqual(self.walk.forecasts[d][h], [q + shift for q in ours[arm.name][h]])
            self.assertNotEqual(self.walk.forecasts[d][h], self.walk.s3[d][h])

    def test_a_week_released_after_the_decision_moves_no_forecast(self):
        """Changing the levels of the weeks released after the walk's last decision changes no forecast; changing a public one does."""

        last = self.DAYS[-1]
        public = pd.latest_public_week(SNAPSHOT_LEVELS, last)
        moved = dict(SNAPSHOT_LEVELS)
        for week in SNAPSHOT_LEVELS:
            if week > public:
                moved[week] = 1.0e6
        other = pd.walk(PANEL, self.DAYS, self.table, pd.decision_states(moved, DATES), **SETTINGS)
        self.assertEqual(other.forecasts, self.walk.forecasts)
        self.assertEqual(other.values, self.walk.values)
        # the latest public week of the first decision day is public on every later day: moving it moves the state
        first_public = max(w for w, x in SNAPSHOT_LEVELS.items() if x is not None and w <= pd.latest_public_week(SNAPSHOT_LEVELS, self.DAYS[0]))
        public_moved = dict(SNAPSHOT_LEVELS)
        public_moved[first_public] = SNAPSHOT_LEVELS[first_public] + 500.0
        again = pd.walk(PANEL, self.DAYS, self.table, pd.decision_states(public_moved, DATES), **SETTINGS)
        self.assertNotEqual(again.values, self.walk.values)

    def test_the_decision_day_of_the_walk_is_refused_off_the_panel(self):
        from repo_model.scoring_protocol import ProtocolError

        with self.assertRaises(ProtocolError):
            pd.walk(PANEL, [date(2024, 6, 1)], self.table, self.states, **SETTINGS)


class SnapshotAndDeclarationTests(unittest.TestCase):

    def test_every_tracked_byte_is_the_manifests(self):
        manifest = json.loads((SNAPSHOT / "manifest.json").read_text())
        names = {item["keyid"] for item in manifest["files"]}
        self.assertEqual(names, set(pd.SERIES) | {"release-page"})
        for item in manifest["files"]:
            raw = (ROOT / item["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), item["sha256"], item["path"])
            self.assertEqual(len(raw), item["byte_count"])
            self.assertTrue(item["url"].startswith("https://"))

    def test_the_release_page_states_the_day_and_time_the_declaration_cites(self):
        text = (SNAPSHOT / "primary-dealers-statistics.html").read_text(encoding="utf-8", errors="replace")
        self.assertIn("Data are updated on Thursdays at approximately 4:15 p.m. with the previous week's statistics", text)

    def test_the_source_declaration_names_the_series_and_the_module_constants(self):
        decl = json.loads(SOURCE_DECLARATION.read_text())
        entry = decl["proposed_registry_entry"]
        self.assertEqual(entry["fields"], list(pd.SERIES))
        self.assertEqual(entry["release_lag"]["days"], pd.RELEASE_LAG_BUSINESS_DAYS)
        self.assertEqual(entry["release_lag"]["available_time"], pd.RELEASE_TIME.strftime("%H:%M"))
        self.assertEqual(decl["transform"]["trailing_weeks"], pd.TRAILING_WEEKS)
        self.assertEqual(decl["transform"]["minimum_trailing_weeks"], pd.MIN_TRAILING)

    def test_the_proposed_registry_entry_passes_the_registrys_own_release_lag_check(self):
        decl = json.loads(SOURCE_DECLARATION.read_text())
        entry = decl["proposed_registry_entry"]
        self.assertEqual(contract.validate_release_lag("nyfed_pd_financing", entry["release_lag"]), [])
        registry = copy.deepcopy(tpb.REGISTRY)
        registry["nyfed_pd_financing"] = entry
        self.assertEqual(contract.validate_registry_release_lags(registry), {})
        registry_module.check_availability_provenance(registry)

    def test_the_registry_itself_is_not_edited(self):
        self.assertNotIn("nyfed_pd_financing", tpb.REGISTRY)

    def test_the_declared_release_equals_the_registered_fr2004_release(self):
        """The same Thursday release: this source declares what `nyfed_fr2004` already declares for the other FR 2004 series."""

        mine = json.loads(SOURCE_DECLARATION.read_text())["proposed_registry_entry"]["release_lag"]
        theirs = tpb.REGISTRY["nyfed_fr2004"]["release_lag"]
        for key in ("available_time", "basis", "days", "timezone", "unit", "worst_case_calendar_days"):
            self.assertEqual(mine[key], theirs[key], key)


if __name__ == "__main__":
    unittest.main()
