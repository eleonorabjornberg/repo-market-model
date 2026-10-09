"""The same-day nowcast of the unpublished day (#445): its inputs' availability and its walk-forward.

Every availability reading here is a claim about the clock, so each is tested against the declaration
in `metadata/sources_measurement.json` and against the tracked snapshots it rests on. The nowcast
for the row of day `r` is made at the 16:00 decision of `r`; it may read the spread of `r - 1` and
earlier, the day's own reverse repo and Treasury settlement, and the calendar, and nothing of `r`'s
spread or of any later day.
"""

from __future__ import annotations

import json
import math
import random
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, measurement_fields, nowcast
from repo_model.asof import InformationRule, declared_availability
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = measurement_fields.load_registry()
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots"
DECLARATION = nowcast.load_declaration(ROOT / "metadata" / "nowcast.json")
DECISION = time(16, 0)


def operation(day, stamp, amount=1_000_000_000, kind="Reverse Repo"):
    return {
        "operationType": kind,
        "operationDate": day,
        "totalAmtAccepted": amount,
        "lastUpdated": stamp,
        "operationId": f"{kind} {day} {stamp}",
    }


def weekdays(start, count):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def synthetic_rows(count=260, seed=7):
    """Rows with a spread, the same-day reverse repo, a settlement and the calendar columns."""

    rng = random.Random(seed)
    rows, spread = [], 0.0
    previous_rrp = 100.0
    for index, day in enumerate(weekdays(date(2019, 1, 7), count)):
        rrp = max(0.0, previous_rrp + rng.uniform(-30, 30))
        settlement = rng.choice([0.0, 0.0, 40.0, 120.0])
        month_end = 1.0 if (index % 21) >= 19 else 0.0
        move = 0.4 * (rrp - previous_rrp) / 30.0 + 0.02 * settlement + 1.5 * month_end - 0.3 * spread + rng.gauss(0, 0.3)
        spread += move
        previous_rrp = rrp
        rows.append(
            DailyObservation(
                day,
                {
                    "sofr": 2.0 + spread / 100.0,
                    "iorb": 2.0,
                    "treasury_settlement": settlement,
                    "quarter_end": 0.0,
                    "tax_date": 0.0,
                    "days_to_month_end": 0.0 if month_end else 10.0,
                    nowcast.RRP_COLUMN: rrp,
                },
            )
        )
    return rows


def with_values(rows, start, **changes):
    """`rows` with the named columns replaced from row `start` on (sofr, or any column)."""

    out = []
    for index, row in enumerate(rows):
        values = dict(row.values)
        if index >= start:
            for name, function in changes.items():
                values[name] = function(index, values.get(name))
        out.append(DailyObservation(row.date, values))
    return out


class SamedayOnRrpTests(unittest.TestCase):
    """A reverse-repo day is admitted only when it is shown to have been written by 15:00 on its own date.

    The Desk states no publication time; `lastUpdated` is the last write. A day whose every record was
    last written on the operation date at or before 15:00 was public by then. A later write, or a
    write after 15:00, proves nothing about the first, so the day is left out.

    Recorded mutation (CLAUDE.md), 9 October 2026, in a disposable copy: `src/repo_model/nowcast.py`,
    `sameday_on_rrp`, the line `elif written.time() > AVAILABLE_BY:` mutated to `elif False:` (a record
    written at 16:50 admitted). `test_a_record_written_after_the_declared_time_is_left_out` then fails with
    `AssertionError` (`datetime.date(2024, 10, 16) unexpectedly found in {datetime.date(2024, 10, 16): 1.0,
    datetime.date(2024, 10, 17): 1.0}`), and three tests on the tracked snapshots fail with it.
    """

    def test_a_record_written_after_the_declared_time_is_left_out(self):
        values, excluded = nowcast.sameday_on_rrp(
            [operation("2024-10-16", "2024-10-16 16:50:30"), operation("2024-10-17", "2024-10-17 13:15:40")]
        )
        self.assertNotIn(date(2024, 10, 16), values)
        self.assertIn(date(2024, 10, 16), excluded)
        self.assertIn(date(2024, 10, 17), values)

    def test_a_record_written_again_on_a_later_date_is_left_out(self):
        values, excluded = nowcast.sameday_on_rrp([operation("2021-09-03", "2021-09-16 10:55:30")])
        self.assertEqual(values, {})
        self.assertIn(date(2021, 9, 3), excluded)

    def test_one_late_record_leaves_the_whole_day_out(self):
        values, _ = nowcast.sameday_on_rrp(
            [operation("2020-02-19", "2020-02-19 13:15:20", 5_000_000_000), operation("2020-02-19", "2020-02-19 16:01:00", 95_000_000)]
        )
        self.assertEqual(values, {})

    def test_the_time_itself_is_admitted(self):
        values, _ = nowcast.sameday_on_rrp([operation("2023-07-17", "2023-07-17 15:00:00")])
        self.assertEqual(values, {date(2023, 7, 17): 1.0})

    def test_a_missing_or_unreadable_stamp_leaves_the_day_out(self):
        for bad in (None, "", "yesterday"):
            record = operation("2022-03-01", bad)
            values, excluded = nowcast.sameday_on_rrp([record])
            self.assertEqual(values, {}, bad)
            self.assertIn(date(2022, 3, 1), excluded)

    def test_the_day_is_the_sum_in_billions_of_the_reverse_repo_operations_only(self):
        values, _ = nowcast.sameday_on_rrp(
            [
                operation("2022-03-01", "2022-03-01 13:15:20", 2_500_000_000),
                operation("2022-03-01", "2022-03-01 13:15:30", 500_000_000),
                operation("2022-03-01", "2022-03-01 13:15:40", 9_000_000_000, kind="Repo"),
            ]
        )
        self.assertEqual(values, {date(2022, 3, 1): 3.0})

    def test_a_reverse_repo_without_an_amount_is_refused_not_summed_around(self):
        with self.assertRaises(ValueError):
            nowcast.sameday_on_rrp([operation("2022-03-01", "2022-03-01 13:15:20", None)])


class DeclarationAgainstTheSnapshotsTests(unittest.TestCase):
    """The declared instants are not earlier than the evidence they rest on.

    Recorded mutation (CLAUDE.md), 9 October 2026, in a disposable copy: `metadata/sources_measurement.json`,
    `nyfed_on_rrp_sameday.release_lag`, `"available_time": "15:00"` mutated to `"13:00"` (earlier than the
    Desk's last writes of 14:43). `test_the_declared_instant_is_not_earlier_than_any_admitted_write`
    then fails with `AssertionError` (`datetime.time(14, 43) not less than or equal to datetime.time(13, 0)`).
    """

    @classmethod
    def setUpClass(cls):
        cls.operations = nowcast.load_operations(SNAPSHOTS / "on_rrp_inputs" / "nyfed_on_rrp")
        cls.values, cls.excluded = nowcast.sameday_on_rrp(cls.operations)

    def test_the_declared_instant_is_not_earlier_than_any_admitted_write(self):
        declared = time.fromisoformat(REGISTRY[nowcast.SAMEDAY_SOURCE_ID]["release_lag"]["available_time"])
        latest = max(
            datetime.fromisoformat(o["lastUpdated"]).time()
            for o in self.operations
            if o["operationType"] == "Reverse Repo" and date.fromisoformat(o["operationDate"]) in self.values
        )
        self.assertLessEqual(latest, declared)

    def test_every_admitted_day_was_written_on_its_own_date(self):
        stamps = {}
        for o in self.operations:
            if o["operationType"] == "Reverse Repo":
                stamps.setdefault(o["operationDate"], []).append(o["lastUpdated"][:10])
        for day in self.values:
            self.assertEqual(set(stamps[day.isoformat()]), {day.isoformat()})

    def test_the_known_late_days_are_left_out(self):
        for day in (date(2024, 10, 16), date(2021, 9, 3), date(2023, 1, 5)):
            self.assertNotIn(day, self.values)
            self.assertIn(day, self.excluded)

    def test_the_admitted_days_are_the_great_majority(self):
        self.assertGreater(len(self.values), 20 * len(self.excluded))

    def test_the_sum_agrees_with_the_published_source_on_the_days_both_have(self):
        panel_sums = {}
        for o in self.operations:
            if o["operationType"] == "Reverse Repo":
                panel_sums[o["operationDate"]] = panel_sums.get(o["operationDate"], 0) + o["totalAmtAccepted"]
        for day, value in self.values.items():
            self.assertAlmostEqual(value, panel_sums[day.isoformat()] / 1e9, places=9)


class AsOfTests(unittest.TestCase):
    """The same-day inputs are read on the day of the decision, the bill rates are not.

    A forecast for `T` is made at 16:00 on `T - 1`. It reads the same-day reverse repo and the nowcast
    from row `T - 1`, the published spread from row `T - 2`, and no same-day bill rate at all: its
    declared instant is the end of the day, after the decision.

    Recorded mutation (CLAUDE.md), 9 October 2026, in a disposable copy: `metadata/sources_measurement.json`,
    `treasury_bill_rates_sameday.release_lag`, `"available_time": "23:59"` mutated to `"15:30"` (a bill rate
    public at the time its quotes are struck). `test_a_same_day_bill_rate_is_not_readable_at_the_decision`
    then fails with `AssertionError` (`datetime.datetime(2026, 1, 20, 15, 30) not greater than
    datetime.datetime(2026, 1, 20, 16, 0)`).
    """

    DATES = [d for d in weekdays(date(2026, 1, 5), 40) if d != date(2026, 1, 19)]

    def rows(self):
        return [
            DailyObservation(
                day,
                {"sofr": 3.6, "iorb": 3.65, nowcast.RRP_COLUMN: 100.0 + i, nowcast.NOWCAST_COLUMN: -5.0},
            )
            for i, day in enumerate(self.DATES)
        ]

    def read_rows(self, features):
        fields = {name: nowcast.COLUMN_FIELDS[name] for name in features if name in nowcast.COLUMN_FIELDS}
        with mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
            FEATURE_SOURCES=MappingProxyType(
                {
                    **contract.FEATURE_SOURCES,
                    **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
                }
            ),
        ):
            rule = InformationRule(REGISTRY, tuple(features), decision_time=DECISION)
            scored = self.DATES.index(date(2026, 1, 22))
            info = rule.information_set(self.DATES, scored)
            rule.check(self.DATES, info)
            return {read.feature: self.DATES[read.row] for read in info.reads}

    def test_the_same_day_reverse_repo_and_the_nowcast_are_read_from_the_decision_day(self):
        read = self.read_rows(["spread_bps", nowcast.RRP_COLUMN, nowcast.NOWCAST_COLUMN])
        self.assertEqual(read[nowcast.RRP_COLUMN], date(2026, 1, 21))
        self.assertEqual(read[nowcast.NOWCAST_COLUMN], date(2026, 1, 21))
        self.assertEqual(read["spread_bps"], date(2026, 1, 20))

    def test_the_published_reverse_repo_is_still_a_day_later(self):
        lag = REGISTRY["nyfed_on_rrp"]["release_lag"]
        self.assertEqual((lag["days"], lag["available_time"]), (1, "16:00"))

    def test_a_same_day_bill_rate_is_not_readable_at_the_decision(self):
        dates = self.DATES
        for field in REGISTRY["treasury_bill_rates_sameday"]["fields"]:
            moment = declared_availability(REGISTRY, "treasury_bill_rates_sameday", field, dates, 10)
            self.assertGreater(moment, datetime.combine(dates[10], DECISION))

    def test_the_excluded_input_builds_no_column(self):
        for pairs in nowcast.COLUMN_FIELDS.values():
            self.assertNotIn("treasury_bill_rates_sameday", [source for source, _field in pairs])

    def test_the_auction_calendar_for_the_nowcast_day_is_public_before_its_decision(self):
        # treasury_settlement on row r is announced a panel day earlier, at 15:00 (scheduled_availability).
        scheduled = json.loads((ROOT / "metadata" / "sources.json").read_text())["treasury_auctions"]["scheduled_availability"]
        self.assertEqual((scheduled["days"], scheduled["available_time"]), (1, "15:00"))
        dates = self.DATES
        moment = declared_availability(
            json.loads((ROOT / "metadata" / "sources.json").read_text()),
            "treasury_auctions", "treasury_settlement", dates, 10,
        )
        self.assertLess(moment, datetime.combine(dates[10], DECISION))


class RidgeTests(unittest.TestCase):
    def test_a_small_penalty_recovers_a_noiseless_line(self):
        x = [[float(i), float((i * 7) % 5)] for i in range(40)]
        y = [3.0 + 2.0 * a - 1.5 * b for a, b in x]
        model = nowcast.fit_ridge(x, y, penalty=1e-9)
        for row, target in zip(x, y):
            self.assertAlmostEqual(model.predict(row), target, places=5)

    def test_a_large_penalty_shrinks_to_the_mean(self):
        x = [[float(i)] for i in range(40)]
        y = [float(i) for i in range(40)]
        model = nowcast.fit_ridge(x, y, penalty=1e12)
        for row in x:
            self.assertAlmostEqual(model.predict(row), sum(y) / len(y), places=3)

    def test_a_constant_column_is_harmless(self):
        x = [[1.0, float(i)] for i in range(30)]
        y = [2.0 * i for i in range(30)]
        model = nowcast.fit_ridge(x, y, penalty=1e-9)
        self.assertAlmostEqual(model.predict([1.0, 10.0]), 20.0, places=4)

    def test_nothing_to_fit_is_refused(self):
        with self.assertRaises(ValueError):
            nowcast.fit_ridge([], [], penalty=1.0)


class WalkForwardTests(unittest.TestCase):
    """The nowcast of row `r` reads no spread from `r` on and no label that was not public at `r`.

    Recorded mutation (CLAUDE.md), 9 October 2026, in a disposable copy: `src/repo_model/nowcast.py`,
    `check_labels_observable`, the line `if pair >= origin:` mutated to `if pair > origin:` (a label of
    the nowcast row itself admitted to the fit). `test_a_label_of_the_nowcast_row_is_refused` then fails
    with `AssertionError` (`LookAheadError not raised`).
    """

    SPEC = DECLARATION.candidates["rrp_settlement"]

    def run_series(self, rows, spec=None):
        spec = spec or self.SPEC
        return nowcast.walk_forward(
            rows, spec.features, penalty=DECLARATION.penalty, min_pairs=DECLARATION.min_pairs,
            refit_every=DECLARATION.refit_every,
        )

    def test_a_label_of_the_nowcast_row_is_refused(self):
        with self.assertRaises(LookAheadError):
            nowcast.check_labels_observable([3, 4, 5], origin=5)
        nowcast.check_labels_observable([3, 4], origin=5)

    def test_the_naive_nowcast_is_the_spread_of_the_day_before(self):
        rows = synthetic_rows()
        result = nowcast.walk_forward(rows, (), penalty=1.0, min_pairs=40, refit_every=21)
        self.assertIsNone(result.values[0])
        for r in range(1, len(rows)):
            self.assertEqual(result.values[r], rows[r - 1].spread_bps)

    def test_the_nowcast_does_not_move_when_the_spread_from_its_row_on_changes(self):
        rows = synthetic_rows()
        base = self.run_series(rows).values
        for r in (45, 90, 140, 199):
            changed = with_values(rows, r, sofr=lambda i, v: v + 0.37 * math.sin(i) + 0.5)
            self.assertEqual(self.run_series(changed).values[: r + 1], base[: r + 1], r)

    def test_the_nowcast_does_not_move_when_the_inputs_after_its_row_change(self):
        rows = synthetic_rows()
        base = self.run_series(rows).values
        for r in (45, 90, 140, 199):
            changed = with_values(
                rows, r + 1,
                sofr=lambda i, v: v + 0.9,
                **{nowcast.RRP_COLUMN: lambda i, v: v + 500.0, "treasury_settlement": lambda i, v: v + 70.0},
            )
            self.assertEqual(self.run_series(changed).values[: r + 1], base[: r + 1], r)

    def test_the_nowcast_does_read_the_same_day_inputs(self):
        rows = synthetic_rows()
        base = self.run_series(rows).values
        changed = with_values(rows, 150, **{nowcast.RRP_COLUMN: lambda i, v: v + 400.0 if i == 150 else v})
        self.assertNotEqual(self.run_series(changed).values[150], base[150])

    def test_the_model_is_idle_until_enough_pairs_and_then_refitted_on_the_cadence(self):
        rows = synthetic_rows()
        result = self.run_series(rows)
        first = result.first_fitted
        self.assertIsNotNone(first)
        self.assertGreaterEqual(first, DECLARATION.min_pairs)
        for r in range(1, first):
            self.assertEqual(result.values[r], rows[r - 1].spread_bps)
            self.assertEqual(result.status[r], "naive: not fitted")
        self.assertEqual(result.refits[0], first)
        self.assertEqual([b - a for a, b in zip(result.refits, result.refits[1:])], [DECLARATION.refit_every] * (len(result.refits) - 1))

    def test_a_missing_input_falls_back_to_the_naive_nowcast_and_is_counted(self):
        rows = synthetic_rows()
        rows = with_values(rows, 150, **{nowcast.RRP_COLUMN: lambda i, v: None if i == 150 else v})
        result = self.run_series(rows)
        self.assertEqual(result.values[150], rows[149].spread_bps)
        self.assertEqual(result.status[150], "naive: input missing")
        self.assertEqual(result.counts["naive: input missing"], sum(1 for s in result.status if s == "naive: input missing"))

    def test_a_missing_day_in_the_past_drops_only_the_pairs_that_need_it(self):
        rows = synthetic_rows()
        rows = with_values(rows, 100, **{nowcast.RRP_COLUMN: lambda i, v: None if i == 100 else v})
        result = self.run_series(rows)
        self.assertEqual(result.status[100], "naive: input missing")
        self.assertEqual(result.status[101], "naive: input missing")  # its change needs the day before
        self.assertEqual(result.status[102], "model")

    def test_the_calendar_columns_are_read_from_the_nowcast_row(self):
        rows = synthetic_rows()
        spec = DECLARATION.candidates["rrp_settlement_calendar"]
        base = self.run_series(rows, spec).values
        changed = with_values(rows, 150, days_to_month_end=lambda i, v: 0.0 if i == 150 else v, quarter_end=lambda i, v: 1.0 if i == 150 else v)
        self.assertNotEqual(self.run_series(changed, spec).values[150], base[150])
        self.assertEqual(self.run_series(changed, spec).values[149], base[149])

    def test_with_the_same_day_inputs_the_nowcast_beats_the_naive_on_data_that_depend_on_them(self):
        rows = synthetic_rows()
        result = self.run_series(rows)
        naive = nowcast.walk_forward(rows, (), penalty=1.0, min_pairs=40, refit_every=21).values
        fitted = range(result.first_fitted + 21, len(rows))
        error = lambda values: sum(abs(values[r] - rows[r].spread_bps) for r in fitted)
        self.assertLess(error(result.values), 0.7 * error(naive))


class DeclarationTests(unittest.TestCase):
    def test_the_primary_is_a_declared_candidate_and_the_column_is_its_nowcast(self):
        self.assertIn(DECLARATION.primary, DECLARATION.candidates)
        self.assertEqual(DECLARATION.primary, "rrp_settlement")

    def test_every_feature_has_a_definition(self):
        for spec in DECLARATION.candidates.values():
            for name in spec.features:
                self.assertIn(name, nowcast.FEATURES)

    def test_an_undefined_feature_is_refused(self):
        document = json.loads((ROOT / "metadata" / "nowcast.json").read_text())
        document["nowcast"]["candidates"]["rrp"]["features"].append("vix")
        with self.assertRaises(ValueError):
            nowcast.parse_declaration(document)

    def test_a_primary_that_is_not_a_candidate_is_refused(self):
        document = json.loads((ROOT / "metadata" / "nowcast.json").read_text())
        document["nowcast"]["primary"] = "best"
        with self.assertRaises(ValueError):
            nowcast.parse_declaration(document)

    def test_the_excluded_bill_rates_are_declared_excluded(self):
        document = json.loads((ROOT / "metadata" / "nowcast.json").read_text())
        self.assertIn("treasury_bill_rates_sameday", document["inputs"]["excluded"])
        for spec in DECLARATION.candidates.values():
            self.assertFalse([name for name in spec.features if "tbill" in name or "bill" in name])


class SubstitutionTests(unittest.TestCase):
    def row(self, **extra):
        return DailyObservation(date(2020, 3, 3), {"sofr": 1.55, "iorb": 1.60, "tga": 300.0, **extra})

    def test_the_spread_of_the_row_becomes_the_nowcast(self):
        row = self.row(**{nowcast.NOWCAST_COLUMN: 7.5})
        self.assertAlmostEqual(nowcast.substitute_latest_spread(row).spread_bps, 7.5, places=9)

    def test_nothing_else_in_the_row_changes(self):
        row = self.row(**{nowcast.NOWCAST_COLUMN: -3.0})
        out = nowcast.substitute_latest_spread(row)
        self.assertEqual(out.date, row.date)
        self.assertEqual({k: v for k, v in out.values.items() if k != "sofr"}, {k: v for k, v in row.values.items() if k != "sofr"})

    def test_a_row_without_a_nowcast_is_returned_unchanged(self):
        row = self.row(**{nowcast.NOWCAST_COLUMN: None})
        self.assertIs(nowcast.substitute_latest_spread(row), row)
        self.assertAlmostEqual(row.spread_bps, -5.0, places=9)

    def test_the_naive_nowcast_gives_back_the_published_spread(self):
        row = self.row(**{nowcast.NOWCAST_COLUMN: -5.0})
        self.assertAlmostEqual(nowcast.substitute_latest_spread(row).spread_bps, row.spread_bps, places=9)


class AnalysisTests(unittest.TestCase):
    def test_a_turning_point_is_a_peak_or_trough_of_at_least_the_move_on_both_sides(self):
        series = [0.0, 0.0, 3.0, 0.0, 0.5, 0.0, -3.0, 0.0, 5.0]
        flags = nowcast.turning_points(series, minimum_move=2.0)
        self.assertEqual(flags, [None, False, True, False, False, False, True, False, None])

    def test_a_move_of_less_than_the_minimum_on_one_side_is_not_a_turning_point(self):
        self.assertEqual(nowcast.turning_points([0.0, 3.0, 2.0, 1.0], minimum_move=2.0), [None, False, False, None])

    def test_a_move_equal_to_the_minimum_counts(self):
        self.assertEqual(nowcast.turning_points([0.0, 2.0, 0.0], minimum_move=2.0), [None, True, None])

    def test_the_best_lag_of_a_series_that_trails_by_two_days_is_two(self):
        rng = random.Random(3)
        actual = [rng.gauss(0, 1) for _ in range(300)]
        median = [None, None] + actual[:-2]
        days = list(range(2, 300))
        table = nowcast.lag_correlations([median[i] for i in days], actual, days, lags=range(-3, 6))
        self.assertEqual(nowcast.best_lag(table), 2)
        self.assertAlmostEqual(table[2], 1.0, places=9)

    def test_the_best_lag_of_a_series_that_is_current_is_zero(self):
        rng = random.Random(4)
        actual = [rng.gauss(0, 1) for _ in range(300)]
        days = list(range(5, 295))
        table = nowcast.lag_correlations([actual[i] for i in days], actual, days, lags=range(-3, 6))
        self.assertEqual(nowcast.best_lag(table), 0)


if __name__ == "__main__":
    unittest.main()
