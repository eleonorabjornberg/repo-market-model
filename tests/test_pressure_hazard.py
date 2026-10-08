"""The time-to-pressure hazard model (#387, track Z of #374): `repo_model.pressure_hazard`.

The model builds the pressure-day probability from a discrete-time first-passage
hazard (`lambda_k`: the first pressure day after the decision is lead `k`) and a
persistence term (`q_m`: the pressure still holds `m` days past the first
pressure day). What is covered:

* `ClosedFormTests` -- the algebra, standard library only. The per-day
  probability is checked against an explicit enumeration of every path of a
  first-passage process, and the window probability against the enumerated
  no-pressure path.
* `CalendarTests` -- a lead's calendar is a function of the date alone and
  reproduces the panel's own columns; the gap between a scored day and its
  anchor is measured on the rule.
* `PairTests` -- the training pairs: a lead is at risk only until the first
  pressure day, the persistence pairs follow the first pressure day, and no
  pair reads a label outside the training frame (`LookAheadError`).
* `PredictorTests` -- the fitted predictor under the fold loop's guards, on a
  panel whose pressure falls on the quarter end: it is found at every horizon,
  the window run is refused except at horizon 1, and a served row whose
  scored-day calendar is not the date worked out is refused.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, numpy 2.4.6
and scikit-learn 1.9.1, `PYTHONDONTWRITEBYTECODE=1`, the killing test run alone,
each mutation confirmed applied by `grep` and restored before the next):

1. `hazard_pairs`: delete the line `if label_row >= rows: break` that stops the
   lead loop at the end of the training frame. The next line,
   `require_labels_inside(label_row, rows, ...)`, then raises `LookAheadError`
   on the first decision near the end of the frame, and
   `PairTests.test_no_pair_reads_a_label_outside_the_frame` fails.
2. `_served_kinds`: replace `if read is None or abs(float(read) - expected[name]) > 1e-9:`
   by `if False:`. The served row's calendar is no longer tied to the date
   worked out, a wrong anchor-to-scored-day gap would put every lead on the
   wrong day unnoticed, and `PredictorTests.test_a_served_row_whose_calendar_is_not_the_scored_days_is_refused`
   fails (no `ValueError` raised).
3. `require_labels_inside`: change `last_label >= rows` to `last_label > rows`.
   `PairTests.test_the_label_guard_refuses_a_row_past_the_frame` fails
   (no `LookAheadError` for `last_label == rows`).

Each of the three is a guard on what a fit may read: 1 and 3 that a label must
be inside the training frame, 2 that a lead's calendar is the scored day's.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import os
import unittest
from datetime import date, time, timedelta
from pathlib import Path

from repo_model import pressure_hazard as hz
from repo_model.asof import InformationRule
from repo_model.data import (
    CALENDAR_COLUMN_RULES,
    DailyObservation,
    market_holidays,
    next_business_day,
)
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((REPO / "metadata" / "sources.json").read_text())
SPLITS = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
FEATURES = (
    "spread_bps", "days_to_month_end", "quarter_end", "tax_date", "reserve_balances", "tga",
)
REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"


def _require_extra(case: unittest.TestCase) -> None:
    ok = all(importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn"))
    if ok:
        return
    if os.environ.get(REQUIRE_ML):
        case.fail(f"{REQUIRE_ML} is set but the optional 'ml' extra is not importable")
    case.skipTest("the optional 'ml' extra is not installed")


def _business_days(first: date, count: int):
    out = [first]
    while len(out) < count:
        out.append(next_business_day(out[-1], 1))
    return out


def _panel(count=330, *, pressure="quarter_end"):
    """Business days from 2024-01-02, real calendar columns, pressure on a chosen day type.

    `pressure="quarter_end"`: +8 bp on the quarter end, -1 bp otherwise, so the
    hazard's calendar term has something to find. `"none"`: never above +5 bp.
    """

    rows = []
    for index, day in enumerate(_business_days(date(2024, 1, 2), count)):
        calendar = {name: float(rule(day)) for name, rule in CALENDAR_COLUMN_RULES.items()
                    if name in ("days_to_month_end", "quarter_end", "tax_date")}
        spread = -1.0 + 0.1 * (index % 3)
        if pressure == "quarter_end" and calendar["quarter_end"] == 1.0:
            spread = 8.0
        week = index // 5
        rows.append(
            DailyObservation(
                day,
                {
                    "sofr": 4.0 + spread / 100.0,
                    "iorb": 4.0,
                    "sofr_volume": 2100.0 + index % 11,
                    "reserve_balances": 3200.0 - 20.0 * (week % 9),
                    "tga": 700.0 + 25.0 * ((week * 7) % 5),
                    **calendar,
                },
            )
        )
    return rows


def _rule(horizon=1, features=FEATURES):
    return InformationRule(REGISTRY, features, decision_time=time(16, 0), horizon=horizon)


class ClosedFormTests(unittest.TestCase):
    def test_the_first_passage_probabilities_and_the_survival_sum_to_one(self):
        hazards = [0.1, 0.3, 0.05, 0.4]
        total = sum(hz.first_passage_probabilities(hazards)) + hz.survival(hazards)[-1]
        self.assertAlmostEqual(total, 1.0, places=12)

    def test_the_window_probability_is_one_minus_the_enumerated_clear_path(self):
        hazards = [0.1, 0.3, 0.05, 0.4, 0.2]
        for window in range(1, 6):
            clear = 1.0
            for value in hazards[:window]:
                clear *= 1.0 - value
            self.assertAlmostEqual(hz.window_probability(hazards, window), 1.0 - clear, places=12)

    def test_the_day_probability_is_the_marginal_of_the_enumerated_paths(self):
        # A first-passage process: the first pressure day is lead j with hazard
        # lambda_j given a clear path, and each later day is a pressure day
        # independently with probability q_m, m days past the first.
        hazards = [0.12, 0.2, 0.15, 0.3]
        persistence = [0.6, 0.35, 0.2]
        for horizon in range(1, 5):
            marginal = 0.0
            for path in itertools.product((0, 1), repeat=horizon):
                probability = 1.0
                first = None
                for lead, y in enumerate(path, start=1):
                    if first is None:
                        probability *= hazards[lead - 1] if y else 1.0 - hazards[lead - 1]
                        if y:
                            first = lead
                    else:
                        q = persistence[lead - first - 1]
                        probability *= q if y else 1.0 - q
                if path[-1]:
                    marginal += probability
            self.assertAlmostEqual(
                hz.day_probability(hazards, persistence, horizon), marginal, places=12
            )

    def test_refusals(self):
        with self.assertRaises(ValueError):
            hz.window_probability([0.1, 0.2], 3)
        with self.assertRaises(ValueError):
            hz.day_probability([0.1, 0.2], [], 2)
        with self.assertRaises(ValueError):
            hz.first_passage_probabilities([0.1, 1.2])
        with self.assertRaises(ValueError):
            hz.survival([float("nan")])


class CalendarTests(unittest.TestCase):
    def test_a_leads_calendar_reproduces_the_panels_columns(self):
        for row in _panel(260):
            want = {name: row.values[name] for name in ("days_to_month_end", "quarter_end", "tax_date")}
            self.assertEqual(hz.calendar_values(row.date), want)

    def test_the_lead_dates_are_business_days_after_the_decision(self):
        # Anchor Thursday 2024-02-29; a gap of 3 and a horizon of 2 put the decision
        # one business day on (Friday 2024-03-01), and leads 1 and 2 on 4 and 5 March.
        anchor = date(2024, 2, 29)
        days = hz.lead_days(anchor, 3, 2)
        self.assertEqual(days, [date(2024, 3, 4), date(2024, 3, 5)])
        self.assertEqual(days[-1], next_business_day(anchor, 3))
        self.assertEqual(hz.lead_days(anchor, 3, 1, 5)[0], next_business_day(anchor, 3))
        with self.assertRaises(ValueError):
            hz.lead_days(anchor, 1, 2)

    def test_the_gap_is_the_rules_scored_day_to_anchor_distance(self):
        one = hz.gap_to_anchor(_rule(1))
        for horizon in (2, 3, 5):
            self.assertEqual(hz.gap_to_anchor(_rule(horizon)), one + horizon - 1)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_loads_and_agrees_with_the_judges(self):
        declaration = hz.load_declaration()
        judge = json.loads((REPO / "metadata" / "pressure_judge.json").read_text())
        entry = judge["candidates"][declaration.candidate]
        self.assertEqual(entry["role"], "candidate")
        self.assertEqual(tuple(entry["features"]), declaration.features)
        # The judge chooses the flag cut-off itself (#407); the judge's entry declares none.
        self.assertNotIn("cutoffs", entry)
        self.assertEqual(declaration.thresholds, tuple(float(t) for t in judge["thresholds_bp"]))
        self.assertEqual(declaration.horizons, tuple(judge["horizons"]))
        self.assertEqual(declaration.last_day.isoformat(), judge["scoring"]["last_day"])
        self.assertEqual(declaration.features, FEATURES)

    def test_a_cutoff_must_be_a_probability(self):
        document = json.loads(hz.DEFAULT_DECLARATION.read_text())
        for bad in (0.0, 1.0, 1.5, True, "0.2", None):
            with self.subTest(cutoff=bad):
                broken = dict(document, cutoffs={"5": bad, "10": 0.2})
                path = Path(self._tmp) / "bad.json"
                path.write_text(json.dumps(broken))
                with self.assertRaises(ValueError):
                    hz.load_declaration(path)

    def test_a_window_longer_than_the_horizons_is_refused(self):
        document = json.loads(hz.DEFAULT_DECLARATION.read_text())
        document["window"]["days"] = 9
        path = Path(self._tmp) / "long.json"
        path.write_text(json.dumps(document))
        with self.assertRaises(ValueError):
            hz.load_declaration(path)

    def setUp(self):
        import tempfile

        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self._tmp = self._dir.name


class PairTests(unittest.TestCase):
    def setUp(self):
        _require_extra(self)
        self.rows = _panel(120)
        self.design = hz._Design(FEATURES, SPLITS, 4)

    def decisions(self, rows, horizon=1):
        return hz._decisions(self.design, _rule(horizon), rows, {})

    def test_a_lead_is_at_risk_only_until_the_first_pressure_day(self):
        rows = _panel(80, pressure="none")
        # A pressure day at row 40 (+8 bp) and nowhere else.
        values = dict(rows[40].values)
        values["sofr"] = 4.08
        rows[40] = DailyObservation(rows[40].date, values)
        decisions = {38: [0.0, 3.2, 0.0, 0.0]}
        hx, hy, px, py, highest = hz.hazard_pairs(self.design, rows, decisions, 5.0, 4)
        # Decision 38: leads 1 (row 39, clear) and 2 (row 40, pressure); stops there.
        self.assertEqual(hy, [0, 1])
        self.assertEqual(highest, 43)
        # Persistence: steps 1 to 3 past row 40 are rows 41, 42, 43.
        self.assertEqual(py, [0, 0, 0])
        # A decision with no pressure in four leads contributes four clear leads.
        hx, hy, px, py, _ = hz.hazard_pairs(self.design, rows, {10: [0.0, 3.2, 0.0, 0.0]}, 5.0, 4)
        self.assertEqual(hy, [0, 0, 0, 0])
        self.assertEqual(px, [])

    def test_no_pair_reads_a_label_outside_the_frame(self):
        rows = self.rows
        decisions = self.decisions(rows, horizon=3)
        _, _, _, _, highest = hz.hazard_pairs(self.design, rows, decisions, 5.0, 4)
        self.assertEqual(highest, len(rows) - 1)
        # A decision on the very last rows reads only the labels that exist.
        last = max(decisions)
        hx, hy, _, _, _ = hz.hazard_pairs(self.design, rows, {last: decisions[last]}, 5.0, 4)
        self.assertLessEqual(len(hy), 4)

    def test_the_label_guard_refuses_a_row_past_the_frame(self):
        hz.require_labels_inside(9, 10, what="x")
        with self.assertRaises(LookAheadError):
            hz.require_labels_inside(10, 10, what="x")

    def test_decisions_are_read_under_the_rule_at_their_own_instant(self):
        rows = self.rows
        decisions = self.decisions(rows, horizon=2)
        self.assertTrue(decisions)
        self.assertLessEqual(max(decisions), len(rows) - 3)
        for state in decisions.values():
            self.assertEqual(len(state), 4)


class PredictorTests(unittest.TestCase):
    def setUp(self):
        _require_extra(self)
        self.rows = _panel(330)

    def run_backtest(self, horizon, window=None, taus=(5.0, 10.0)):
        from repo_model.baseline import rolling_exceedance_backtest

        return rolling_exceedance_backtest(
            self.rows,
            predictor=hz.pressure_hazard_exceedance(
                FEATURES, SPLITS, minimum_history=61, window=window
            ),
            model_name="pressure_hazard",
            features=FEATURES,
            registry=REGISTRY,
            decision_time=time(16, 0),
            taus=taus,
            minimum_history=61,
            refit_every=21,
            horizon=horizon,
        )

    def test_the_hazard_finds_pressure_that_falls_on_the_quarter_end(self):
        for horizon in (1, 3, 5):
            with self.subTest(horizon=horizon):
                report = self.run_backtest(horizon, taus=(5.0,))
                hits = [
                    p[0] for when, p, o in zip(report.scored_dates, report.forecast, report.outcomes)
                    if o[0] == 1 and when > date(2024, 9, 1)
                ]
                others = [
                    p[0] for when, p, o in zip(report.scored_dates, report.forecast, report.outcomes)
                    if o[0] == 0 and when > date(2024, 9, 1)
                ]
                self.assertTrue(hits)
                self.assertGreater(min(hits), 0.5)
                self.assertLess(sum(others) / len(others), 0.05)
                for curve in report.forecast:
                    self.assertTrue(0.0 <= curve[0] <= 1.0)

    def test_the_thresholds_are_nested(self):
        report = self.run_backtest(2)
        for curve in report.forecast:
            self.assertLessEqual(curve[1], curve[0])

    def test_the_window_forecast_is_at_least_the_day_forecast(self):
        day = self.run_backtest(1, taus=(5.0,))
        window = self.run_backtest(1, window=5, taus=(5.0,))
        self.assertEqual(day.scored_dates, window.scored_dates)
        mean_day = sum(c[0] for c in day.forecast) / len(day.forecast)
        mean_window = sum(c[0] for c in window.forecast) / len(window.forecast)
        self.assertGreater(mean_window, mean_day)
        self.assertEqual(window.model_settings["target"], "window")
        self.assertEqual(window.model_settings["window"], 5)

    def test_the_window_is_refused_beyond_horizon_one(self):
        with self.assertRaises(ValueError):
            self.run_backtest(2, window=5)

    def test_without_the_rule_it_refuses(self):
        predictor = hz.pressure_hazard_exceedance(FEATURES, SPLITS, minimum_history=61)
        with self.assertRaises(ValueError):
            predictor(self.rows[:100], self.rows[100:101], (5.0,))

    def test_a_served_row_whose_calendar_is_not_the_scored_days_is_refused(self):
        rule = _rule(3)
        dates = [row.date for row in self.rows]
        index = 200
        info = rule.information_set(dates, index)
        observation = rule.observation(self.rows, info)
        values = dict(observation.values)
        values["days_to_month_end"] = (values["days_to_month_end"] + 3.0) % 30
        wrong = DailyObservation(observation.date, values)
        predictor = hz.pressure_hazard_exceedance(FEATURES, SPLITS, minimum_history=61)
        frame = rule.frame(self.rows, info)
        with self.assertRaisesRegex(ValueError, "calendar|days_to_month_end"):
            predictor(self.rows[:150], (wrong,), (5.0,), information=rule, histories=(frame,))
        right = predictor(self.rows[:150], (observation,), (5.0,), information=rule, histories=(frame,))
        self.assertEqual(len(right.curves), 1)

    def test_the_window_benchmarks_forecast_the_same_window(self):
        from repo_model.baseline import rolling_exceedance_backtest

        calendar = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")
        day = self.run_backtest(1, window=5, taus=(5.0,))
        for kind in ("climatology", "persistence"):
            with self.subTest(kind=kind):
                report = rolling_exceedance_backtest(
                    self.rows,
                    predictor=hz.window_benchmark_exceedance(
                        kind, calendar, SPLITS, minimum_history=61
                    ),
                    model_name=kind,
                    features=calendar,
                    registry=REGISTRY,
                    decision_time=time(16, 0),
                    taus=(5.0,),
                    minimum_history=61,
                    refit_every=21,
                    horizon=1,
                )
                self.assertEqual(report.scored_dates, day.scored_dates)
                self.assertTrue(all(0.0 <= c[0] <= 1.0 for c in report.forecast))
        with self.assertRaises(ValueError):
            hz.window_benchmark_exceedance("nope", calendar, SPLITS, minimum_history=61)

    def test_the_design_refuses_what_it_cannot_read(self):
        with self.assertRaises(ValueError):
            hz._Design(("days_to_month_end", "quarter_end", "tax_date"), SPLITS, 2)
        with self.assertRaises(ValueError):
            hz._Design(("spread_bps", "quarter_end"), SPLITS, 2)
        with self.assertRaises(ValueError):
            hz._Design(("spread_bps", "days_to_month_end", "quarter_end", "tax_date", "tga"), SPLITS, 2)
        with self.assertRaises(ValueError):
            hz.pressure_hazard_exceedance(FEATURES, SPLITS, minimum_history=61, window=9)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
