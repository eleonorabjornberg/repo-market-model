"""The quarter-end window, its split, and the per-quarter peak table (#140).

Eleonora's request of 2 October 2026: a calendar column `quarter_end_window`,
1.0 on the last business day of the quarter and the two business days either
side; a `quarter_end_window` day type reported alongside the declared day
types; and one peak of SOFR - IORB per quarter over the window, beside the
highest probability each model gave on a window day. She approved it on
2 October 2026; it is recorded in `docs/decisions/quarter-end-window.md`.

Expected windows are written from the market holiday table
(`metadata/market_holidays.json`) and a calendar, not from the code's output:

* 2018 Q4: Monday 2018-12-31 is the last business day; 2019-01-01 is closed,
  so the window runs 2018-12-27, 12-28, 12-31, 2019-01-02, 01-03.
* 2019 Q1: Sunday 2019-03-31, so Friday 03-29; the window runs 03-27 to 04-02.
* 2024 Q1: Good Friday 2024-03-29 is closed, so Thursday 03-28 is the last
  business day, and the window runs 03-26, 03-27, 03-28, 04-01, 04-02.
* 2025 Q4: Wednesday 2025-12-31; 2026-01-01 is closed, so the window ends on
  Monday 2026-01-05, two days inside the locked near-blind tier.
"""

import inspect
import json
import sys
import unittest
import unittest.mock
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import data, evaluation_splits, quarter_peaks  # noqa: E402
from repo_model.contract import CALENDAR_FEATURES  # noqa: E402
from repo_model.data import (  # noqa: E402
    OPT_IN_COLUMNS,
    PANEL_COLUMNS,
    PointInTimeObservation,
    build_daily_panel,
)
from repo_model.splits import LookAheadError  # noqa: E402

SPLITS = ROOT / "metadata" / "evaluation_splits.json"

WINDOWS = {
    (2018, 4): ("2018-12-27", "2018-12-28", "2018-12-31", "2019-01-02", "2019-01-03"),
    (2019, 1): ("2019-03-27", "2019-03-28", "2019-03-29", "2019-04-01", "2019-04-02"),
    (2019, 3): ("2019-09-26", "2019-09-27", "2019-09-30", "2019-10-01", "2019-10-02"),
    (2024, 1): ("2024-03-26", "2024-03-27", "2024-03-28", "2024-04-01", "2024-04-02"),
    (2025, 4): ("2025-12-29", "2025-12-30", "2025-12-31", "2026-01-02", "2026-01-05"),
}


def _days(isos):
    return tuple(date.fromisoformat(iso) for iso in isos)


class QuarterEndWindowColumnTests(unittest.TestCase):
    """`data.quarter_end_window`: the column, from the date and the holiday table alone."""

    def test_the_windows_from_the_holiday_table(self):
        for (year, quarter), isos in WINDOWS.items():
            with self.subTest(quarter=f"{year} Q{quarter}"):
                self.assertEqual(data.quarter_end_window_days(year, quarter), _days(isos))

    def test_the_column_reads_one_on_the_window_and_zero_beside_it(self):
        for (year, quarter), isos in WINDOWS.items():
            window = _days(isos)
            for day in window:
                self.assertEqual(data.quarter_end_window(day), 1.0, day)
                self.assertEqual(data.quarter_end_window_quarter(day), (year, quarter), day)
            # The business day before the window and the one after it.
            before = window[0] - timedelta(days=1)
            while before.weekday() >= 5 or before in data.market_holidays().closed:
                before -= timedelta(days=1)
            after = window[-1] + timedelta(days=1)
            while after.weekday() >= 5 or after in data.market_holidays().closed:
                after += timedelta(days=1)
            for day in (before, after):
                self.assertEqual(data.quarter_end_window(day), 0.0, day)
                self.assertIsNone(data.quarter_end_window_quarter(day), day)

    def test_a_closed_day_inside_the_span_is_not_in_the_window(self):
        self.assertEqual(data.quarter_end_window(date(2019, 1, 1)), 0.0)
        self.assertEqual(data.quarter_end_window(date(2024, 3, 29)), 0.0)
        self.assertEqual(data.quarter_end_window(date(2019, 3, 30)), 0.0)

    def test_the_window_is_centred_on_quarter_end(self):
        """Every window from 2018 Q1 to 2027 Q3 has five days, with `quarter_end` the middle one."""

        for year in range(2018, 2028):
            for quarter in range(1, 5):
                if (year, quarter) == (2027, 4):
                    continue
                window = data.quarter_end_window_days(year, quarter)
                self.assertEqual(len(window), 5)
                self.assertEqual(
                    [data.quarter_end(day) for day in window], [0.0, 0.0, 1.0, 0.0, 0.0]
                )

    def test_quarter_end_is_unchanged(self):
        """The existing column still marks only the last business day of the quarter.

        Written from its definition: the last weekday of the quarter not in the
        holiday table, checked on every day the table covers.
        """

        closed = data.market_holidays().closed
        day = date(2018, 1, 1)
        while day <= date(2027, 12, 31):
            month = 3 * ((day.month - 1) // 3) + 3
            last = date(day.year + month // 12, month % 12 + 1, 1) - timedelta(days=1)
            while last.weekday() >= 5 or last in closed:
                last -= timedelta(days=1)
            self.assertEqual(data.quarter_end(day), float(day == last), day)
            day += timedelta(days=1)

    def test_a_window_the_table_does_not_cover_is_refused(self):
        with self.assertRaises(ValueError):
            data.quarter_end_window_days(2027, 4)
        with self.assertRaises(ValueError):
            data.quarter_end_window_days(2017, 4)
        with self.assertRaises(ValueError):
            data.quarter_end_window(date(2018, 1, 2))

    def test_it_is_a_declared_opt_in_calendar_column(self):
        """Declared, buildable with `--column`, and not in the published panel's default build."""

        self.assertIn("quarter_end_window", CALENDAR_FEATURES)
        self.assertIs(data.CALENDAR_COLUMN_RULES["quarter_end_window"], data.quarter_end_window)
        self.assertIn("quarter_end_window", OPT_IN_COLUMNS)
        self.assertNotIn("quarter_end_window", PANEL_COLUMNS)
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text())
        self.assertNotIn("quarter_end_window", manifest["built_columns"])

    def test_it_uses_no_outcome_data(self):
        """The rule takes a date and nothing else, and no observed value moves it.

        Two builds whose SOFR prints differ on every day, one of them missing a
        window day from its grid, give the same column on every shared day.
        """

        self.assertEqual(list(inspect.signature(data.quarter_end_window).parameters), ["day"])
        registry = {
            "nyfed_sofr": {
                "release_lag": {
                    "basis": "ref_date",
                    "unit": "business_days",
                    "days": 1,
                    "worst_case_calendar_days": 6,
                    "available_time": "15:00",
                    "timezone": "America/New_York",
                    "note": "fixture",
                }
            }
        }

        def build(dates, value):
            return build_daily_panel(
                [
                    PointInTimeObservation(
                        series_id="SOFR",
                        ref_date=day,
                        available_at=datetime.combine(
                            day + timedelta(days=1), time(19, 0), tzinfo=timezone.utc
                        ),
                        value=value(day),
                        vintage_id=f"v{day.isoformat()}",
                        source_sha="a" * 64,
                    )
                    for day in dates
                ],
                registry,
                build_cutoff=datetime(2026, 3, 1, tzinfo=timezone.utc),
                decision_time=time.fromisoformat("15:00"),
                columns=("sofr", "quarter_end_window"),
            )

        grid = [date(2019, 9, 20) + timedelta(days=offset) for offset in range(20)]
        grid = [day for day in grid if day.weekday() < 5]
        calm = build(grid, lambda day: 2.0)
        stressed = build(
            [day for day in grid if day != date(2019, 9, 30)],
            lambda day: 2.0 + 0.5 * day.day,
        )
        self.assertEqual(calm.built_columns, ("sofr", "quarter_end_window"))
        calm_values = {row.date: row.values["quarter_end_window"] for row in calm.observations}
        for row in stressed.observations:
            self.assertEqual(row.values["quarter_end_window"], calm_values[row.date], row.date)
        self.assertEqual(
            sorted(day for day, value in calm_values.items() if value == 1.0),
            list(_days(WINDOWS[(2019, 3)])),
        )


class QuarterEndWindowSplitTests(unittest.TestCase):
    """The `quarter_end_window` day type, reported alongside the declared ones."""

    def test_the_declared_precedence_and_file_are_unchanged(self):
        declaration = evaluation_splits.load_split_declaration(SPLITS)
        self.assertEqual(
            evaluation_splits.DAY_TYPES, ("quarter_end", "month_end", "tax_date", "ordinary")
        )
        document = json.loads(SPLITS.read_text())
        self.assertEqual(
            document["day_types"]["precedence"], ["quarter_end", "month_end", "tax_date", "ordinary"]
        )
        self.assertNotIn("quarter_end_window", document["day_types"]["precedence"])
        # The day type of a quarter-end window day that is not quarter end is
        # whatever it was: 2019-10-01 is ordinary... by the declared types.
        self.assertEqual(
            declaration.day_type({"days_to_month_end": 30.0, "quarter_end": 0.0, "tax_date": 0.0}),
            "ordinary",
        )

    def test_the_window_label_is_read_from_the_date(self):
        self.assertEqual(
            evaluation_splits.quarter_end_window_label(date(2019, 10, 1)), "quarter_end_window"
        )
        self.assertEqual(
            evaluation_splits.quarter_end_window_label(date(2019, 10, 3)),
            "outside_quarter_end_window",
        )
        self.assertEqual(
            evaluation_splits.QUARTER_END_WINDOW_GROUPS,
            ("quarter_end_window", "outside_quarter_end_window"),
        )

    def test_split_document_reports_it_beside_the_day_types(self):
        from repo_model.baseline import split_document
        from repo_model.data import DailyObservation

        declaration = evaluation_splits.load_split_declaration(SPLITS)
        days = [date(2019, 9, 23) + timedelta(days=offset) for offset in range(14)]
        days = [day for day in days if day.weekday() < 5]
        rows = [
            DailyObservation(
                date=day,
                values={
                    "days_to_month_end": data.days_to_month_end(day),
                    "quarter_end": data.quarter_end(day),
                    "tax_date": data.tax_date(day),
                },
            )
            for day in days
        ]
        series = [float(position) for position in range(len(days))]
        document = split_document(declaration, rows, days, series, block_length=2, seed=1)
        self.assertEqual(sorted(document), ["by_day_type", "by_quarter_end_window", "by_regime"])
        window = document["by_quarter_end_window"]
        self.assertEqual(list(window), list(evaluation_splits.QUARTER_END_WINDOW_GROUPS))
        inside = [
            value for day, value in zip(days, series) if data.quarter_end_window(day) == 1.0
        ]
        self.assertEqual(window["quarter_end_window"]["count"], 5)
        self.assertAlmostEqual(window["quarter_end_window"]["mean"], sum(inside) / 5)
        self.assertEqual(window["outside_quarter_end_window"]["count"], len(days) - 5)
        # The declared day types are what they were: one quarter_end day.
        self.assertEqual(document["by_day_type"]["quarter_end"]["count"], 1)


class QuarterPeakTableTests(unittest.TestCase):
    """`quarter_peaks.quarter_peak_table`."""

    def spreads(self):
        out = {}
        day = date(2019, 9, 2)
        while day <= date(2019, 10, 15):
            if day.weekday() < 5:
                out[day] = 1.0
            day += timedelta(days=1)
        out[date(2019, 9, 17)] = 300.0  # outside the window: never the peak
        out[date(2019, 9, 30)] = 9.0
        out[date(2019, 10, 1)] = 10.0  # on +10 bp: not above it
        return out

    def forecasts(self, spreads):
        return {
            "model": {
                5.0: {day: (0.9 if day == date(2019, 9, 26) else 0.1) for day in spreads},
                10.0: {day: (0.4 if day == date(2019, 10, 2) else 0.05) for day in spreads},
            }
        }

    def test_one_row_per_quarter_with_the_window_peak(self):
        spreads = self.spreads()
        table = quarter_peaks.quarter_peak_table(
            spreads, self.forecasts(spreads), first=(2019, 3), last=(2019, 3),
            end=date(2019, 12, 31), taus=(5.0, 10.0),
        )
        self.assertEqual(len(table), 1)
        row = table[0]
        self.assertEqual(row["quarter"], "2019 Q3")
        self.assertEqual(row["window"], list(WINDOWS[(2019, 3)]))
        self.assertEqual(row["peak_bps"], 10.0)
        self.assertEqual(row["peak_day"], "2019-10-01")
        self.assertFalse(row["peak_on_quarter_end"])
        self.assertEqual(row["above"], {"5": True, "10": False})
        peaks = row["forecast_peaks"]["model"]
        self.assertEqual(peaks["5"], {"max": 0.9, "day": "2019-09-26", "days_forecast": 5})
        self.assertEqual(peaks["10"], {"max": 0.4, "day": "2019-10-02", "days_forecast": 5})
        self.assertEqual(row["window_days_after_end"], 0)
        self.assertEqual(row["window_days_without_spread"], 0)

    def test_a_window_day_after_end_is_not_read(self):
        spreads = self.spreads()
        table = quarter_peaks.quarter_peak_table(
            spreads, self.forecasts(spreads), first=(2019, 3), last=(2019, 3),
            end=date(2019, 9, 30), taus=(5.0, 10.0),
        )
        row = table[0]
        self.assertEqual(row["window_days_after_end"], 2)
        self.assertEqual(row["peak_bps"], 9.0)
        self.assertEqual(row["peak_day"], "2019-09-30")
        self.assertTrue(row["peak_on_quarter_end"])
        self.assertEqual(row["forecast_peaks"]["model"]["10"]["max"], 0.05)
        self.assertEqual(row["forecast_peaks"]["model"]["10"]["days_forecast"], 3)

    def test_a_model_without_a_forecast_in_the_window_reads_none(self):
        spreads = self.spreads()
        table = quarter_peaks.quarter_peak_table(
            spreads, {"model": {5.0: {}, 10.0: {}}}, first=(2019, 3), last=(2019, 3),
            end=date(2019, 12, 31), taus=(5.0, 10.0),
        )
        self.assertEqual(
            table[0]["forecast_peaks"]["model"]["5"], {"max": None, "day": None, "days_forecast": 0}
        )

    def test_a_locked_window_day_is_refused(self):
        """A table read into a locked tier raises `LookAheadError` (`docs/decisions/lockbox.md`).

        2025 Q4's window ends on 2026-01-05. Read to 2025-12-31 it stops before
        the near-blind tier; read to 2026-01-05 it would read two locked days.

        Mutation record, 2 October 2026, Python 3.11.15, in a disposable copy
        of the tree built from `git ls-files -z --cached --others
        --exclude-standard`, the target confirmed present exactly once: the
        line `require_unlocked(read, where="quarter_peaks.quarter_peak_table")`
        in `quarter_peaks.quarter_peak_table` replaced by `pass`. Killed by
        this test, `AssertionError: LookAheadError not raised`, and by no
        other test in this module.
        """

        spreads = {day: 1.0 for day in _days(WINDOWS[(2025, 4)])}
        forecasts = {"model": {5.0: {}, 10.0: {}}}
        table = quarter_peaks.quarter_peak_table(
            spreads, forecasts, first=(2025, 4), last=(2025, 4),
            end=date(2025, 12, 31), taus=(5.0, 10.0),
        )
        self.assertEqual(table[0]["window_days_after_end"], 2)
        with self.assertRaises(LookAheadError):
            quarter_peaks.quarter_peak_table(
                spreads, forecasts, first=(2025, 4), last=(2025, 4),
                end=date(2026, 1, 5), taus=(5.0, 10.0),
            )


if __name__ == "__main__":
    unittest.main()
