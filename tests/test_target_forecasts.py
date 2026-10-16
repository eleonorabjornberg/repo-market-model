"""The target-forecast columns of H9 step 3 (#842): a walk-forward forecast of a richer target as an input of H5's candidate.

A column on the row of decision day d holds the median of the lead-h law that a model fitted at or before d's decision
instant gave for the target day h business days later. Its availability is declared in `metadata/sources_measurement.json`
(zero lag: the value is public at 16:00 ET on its own date, the decision instant). The guard is `attach`, which refuses,
with `LookAheadError`, a forecast whose fit was made at a later decision instant than the forecast's own.

**Recorded mutation** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run
alone, confirmed applied by `grep` and restored afterwards):

1. `attach`: replace `if fit_date > decision:` by `if False:`. A forecast whose fit is made after its decision day is then
   written into the column; `AttachTests.test_a_forecast_from_a_later_fit_is_refused` fails with
   `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import json
import unittest
from datetime import date, time
from pathlib import Path

from repo_model import asof, target_forecasts as tf
from repo_model.data import DailyObservation, next_business_day
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
LEVELS = tuple(i / 24 for i in range(1, 24))


def _law(centre: float):
    return [centre + 0.1 * (i - 11) for i in range(23)]


def _days(n: int, start: date = date(2020, 3, 2)):
    out = [start]
    while len(out) < n:
        out.append(next_business_day(out[-1], 1))
    return out


def _rows(n: int):
    return [DailyObservation(d, {"x": float(i)}) for i, d in enumerate(_days(n))]


class MedianTests(unittest.TestCase):
    def test_the_median_is_the_middle_level_of_the_grid(self):
        self.assertEqual(tf.median_of(_law(5.0), tf.GRID), 5.0)

    def test_a_law_off_the_grid_is_refused(self):
        with self.assertRaises(ValueError):
            tf.median_of([1.0, 2.0, 3.0], tf.GRID)


class ColumnTests(unittest.TestCase):
    def test_a_column_names_its_target_and_its_lead(self):
        self.assertEqual(tf.column("sofr_dispersion_bps", 3), "h9fc_sofr_dispersion_bps_h3")

    def test_every_target_and_lead_has_a_column_and_a_field(self):
        self.assertEqual(len(tf.COLUMNS), len(tf.TARGETS) * len(tf.HORIZONS))
        self.assertEqual(set(tf.COLUMN_FIELDS), set(tf.COLUMNS))
        for fields in tf.COLUMN_FIELDS.values():
            self.assertEqual({source for source, _field in fields}, {tf.SOURCE_ID})


class OriginTests(unittest.TestCase):
    def test_a_block_is_fitted_at_the_decision_instant_of_its_first_row(self):
        dates = _days(30)
        out = tf.fit_decision_dates(dates, [[10, 11, 12], [13, 14]], horizon=2)
        self.assertEqual(out[dates[8]], dates[8])
        self.assertEqual(out[dates[10]], dates[8])
        self.assertEqual(out[dates[11]], dates[11])
        self.assertEqual(out[dates[12]], dates[11])


class AttachTests(unittest.TestCase):
    def setUp(self):
        self.rows = _rows(40)
        self.dates = [row.date for row in self.rows]

    def forecasts(self, days):
        return {d: _law(float(i)) for i, d in enumerate(days)}

    def test_the_median_goes_on_the_decision_row_and_nowhere_else(self):
        days = self.dates[10:14]
        fits = {d: d for d in days}
        out = tf.attach(self.rows, self.forecasts(days), fits, target="on_rrp_change_bn", horizon=2)
        column = tf.column("on_rrp_change_bn", 2)
        self.assertEqual([row.values.get(column) for row in out[10:14]], [0.0, 1.0, 2.0, 3.0])
        self.assertTrue(all(row.values.get(column) is None for row in out[:10] + out[14:]))
        self.assertTrue(all(row.values["x"] == float(i) for i, row in enumerate(out)))
        self.assertNotIn(column, self.rows[10].values)

    def test_a_missing_law_is_a_hole(self):
        days = self.dates[10:12]
        out = tf.attach(self.rows, {days[0]: None, days[1]: _law(4.0)}, {d: d for d in days}, target="on_rrp_change_bn", horizon=1)
        column = tf.column("on_rrp_change_bn", 1)
        self.assertIsNone(out[10].values.get(column))
        self.assertEqual(out[11].values[column], 4.0)

    def test_a_forecast_from_a_later_fit_is_refused(self):
        days = self.dates[10:12]
        fits = {days[0]: days[0], days[1]: self.dates[12]}
        with self.assertRaises(LookAheadError):
            tf.attach(self.rows, self.forecasts(days), fits, target="on_rrp_change_bn", horizon=1)

    def test_a_forecast_with_no_recorded_fit_is_refused(self):
        days = self.dates[10:12]
        with self.assertRaises(LookAheadError):
            tf.attach(self.rows, self.forecasts(days), {days[0]: days[0]}, target="on_rrp_change_bn", horizon=1)

    def test_a_forecast_for_a_day_off_the_panel_is_a_data_error(self):
        with self.assertRaises(ValueError):
            tf.attach(self.rows, {date(2020, 3, 7): _law(1.0)}, {date(2020, 3, 7): date(2020, 3, 6)}, target="on_rrp_change_bn", horizon=1)

    def test_an_unknown_target_is_a_data_error(self):
        with self.assertRaises(ValueError):
            tf.attach(self.rows, {}, {}, target="tgcr_dispersion_bps", horizon=1)

    def test_a_forecast_on_a_locked_day_is_refused(self):
        rows = [DailyObservation(d, {"x": 0.0}) for d in _days(5, date(2026, 9, 8))]
        day = rows[2].date
        with self.assertRaises(LookAheadError):
            tf.attach(rows, {day: _law(1.0)}, {day: day}, target="on_rrp_change_bn", horizon=1)


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((REPO / "metadata" / "sources_measurement.json").read_text(encoding="utf-8"))

    def test_the_registry_declares_the_columns_with_no_lag(self):
        entry = self.registry[tf.SOURCE_ID]
        self.assertEqual(sorted(entry["fields"]), sorted(tf.COLUMNS))
        self.assertEqual(entry["release_lag"]["days"], 0)
        self.assertEqual(entry["release_lag"]["available_time"], "16:00")

    def test_the_rule_reads_a_column_at_the_decision_row_and_never_later(self):
        # a value on the row of day t is public at 16:00 on t, so the decision at 16:00 on t reads row t, not t + 1
        column = tf.column("on_rrp_change_bn", 1)
        registry = json.loads((REPO / "metadata" / "sources.json").read_text(encoding="utf-8"))
        registry = {**registry, tf.SOURCE_ID: self.registry[tf.SOURCE_ID]}
        dates = _days(60)
        with tf.switched_on():
            rule = asof.InformationRule(registry, (column,), decision_time=time(16, 0), horizon=1)
            info = rule.information_set(dates, 40)
            rule.check(dates, info)
        read = [r for r in info.reads if r.feature == column]
        self.assertEqual([r.row for r in read], [39])


if __name__ == "__main__":
    unittest.main()
