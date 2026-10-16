"""The tables of `scripts/reliability_regimes_683.py` (#683): what a reader sees when a regime has no slope.

Nothing here is a leakage guard, so no mutation record is required; the figures the script tabulates are read from tracked evidence.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("reliability_regimes_683_script", ROOT / "scripts" / "reliability_regimes_683.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


S = _script()


def _cell(slope, pressure_days, days=100, on_zero=None):
    cell = {"days": days, "pressure_days": pressure_days, "slope": slope}
    if on_zero is not None:
        cell["pressure_days_on_zero"] = on_zero
        cell["positive_days"] = days - on_zero
    return cell


class SlopeTextTests(unittest.TestCase):
    def test_a_regime_with_no_pressure_day_is_undefined_not_a_number(self):
        self.assertEqual(S._slope_text(_cell(None, 0)), "undefined")
        self.assertEqual(S._slope_text(_cell(0.7, 0)), "undefined")

    def test_a_missing_slope_with_pressure_days_is_a_dash(self):
        self.assertEqual(S._slope_text(_cell(None, 12)), "–")
        self.assertEqual(S._slope_text(None), "–")

    def test_a_near_separated_fit_is_called_unstable(self):
        self.assertEqual(S._slope_text(_cell(-99.35, 3)), "unstable")

    def test_a_cell_of_few_pressure_days_is_marked(self):
        self.assertEqual(S._slope_text(_cell(6.2, 3)), "6.20†")
        self.assertEqual(S._slope_text(_cell(0.48, 62)), "0.48")

    def test_the_mark_counts_the_events_in_the_fit_not_the_cells_pressure_days(self):
        # #801: 62 pressure days, 60 on zero forecasts, so the fit rests on 2 events.
        self.assertEqual(S._slope_text(_cell(1.39, 62, on_zero=60)), "1.39†")
        self.assertEqual(S._slope_text(_cell(0.48, 62, on_zero=10)), "0.48")

    def test_a_row_that_forecasts_zero_on_every_pressure_day_reads_uncalibrated_not_not_formed(self):
        self.assertEqual(S._slope_text(_cell(None, 82, on_zero=82)), "uncalibrated: zero on all 82")
        self.assertEqual(S._slope_text(_cell(None, 15, on_zero=15)), "uncalibrated: zero on all 15")

    def test_a_missing_slope_with_some_events_in_the_fit_stays_a_dash(self):
        self.assertEqual(S._slope_text(_cell(None, 12, on_zero=3)), "–")


class TrackedCommandTests(unittest.TestCase):
    def test_the_tracked_cells_keep_the_counts_the_marks_need(self):
        import json
        import tempfile
        from argparse import Namespace

        evidence = {"rows": {"r": {"1": {"cells": {"regime 2018-19": {
            "days": 294, "pressure_days": 62, "slope": 1.39, "positive_days": 16, "pressure_days_on_zero": 60}}}}}}
        with tempfile.TemporaryDirectory() as tmp:
            ev, out = Path(tmp) / "ev.json", Path(tmp) / "out.json"
            ev.write_text(json.dumps(evidence), encoding="utf-8")
            original, S.REPO = S.REPO, Path(tmp)
            try:
                self.assertEqual(S.tracked_command(Namespace(evidence=ev, output=out, markdown=None)), 0)
            finally:
                S.REPO = original
            cell = json.loads(out.read_text(encoding="utf-8"))["rows"]["r"]["1"]["regime 2018-19"]
        self.assertEqual(cell["pressure_days_on_zero"], 60)
        self.assertEqual(cell["positive_days"], 16)


class TrackedTextTests(unittest.TestCase):
    def test_the_pooled_column_comes_first_and_the_reading_is_restated(self):
        result = {
            "source": "x.json",
            "reading": S.READING,
            "rows": {"row": {"1": {
                "all": _cell(0.83, 82, 1469),
                "regime 2018-19": _cell(0.48, 62, 294),
                "regime 2021-23": _cell(None, 0, 586),
            }}},
        }
        text = S.tracked_text(result)
        self.assertIn("Pooled slopes mislead here", text)
        self.assertIn("| lead | all days (pooled) | regime 2018-19 | regime 2020 |", text)
        self.assertIn("| 1 | 0.83 | 0.48 | – | undefined |", text)
        self.assertIn("development, not a verdict".lower(), text.lower())


class RowCellsTests(unittest.TestCase):
    """`_run_rows` is the bootstrap of the `kinked` command, spread over processes (#753): the same cells, whatever the worker count."""

    def _jobs(self):
        import random

        rng = random.Random(7)
        days = 240
        jobs = []
        for key in ("a", "b", "c"):
            p = [min(0.95, max(0.02, rng.random() * 0.4)) for _ in range(days)]
            y = [1 if rng.random() < q * 1.2 else 0 for q in p]
            regime = ["regime 2018-19"] * 80 + ["regime 2020-24"] * 80 + ["regime 2025-26"] * 80
            state = ["scarcity state 0"] * 120 + ["scarcity state 1"] * 120
            jobs.append((key, p, y, regime, state, dict(block_length=2.0, seed=11, replications=40, level=0.9)))
        return jobs

    def test_the_cells_do_not_depend_on_the_number_of_workers(self):
        jobs = self._jobs()
        serial = S._run_rows(jobs, workers=1)
        self.assertEqual(list(serial), ["a", "b", "c"])
        self.assertEqual(serial, S._run_rows(jobs, workers=2))

    def test_each_row_has_a_pooled_cell_in_both_splits(self):
        rows = S._run_rows(self._jobs()[:1], workers=1)
        self.assertIn("pooled", rows["a"]["regime"])
        self.assertIn("pooled", rows["a"]["scarcity_state"])
        self.assertEqual(rows["a"]["regime"]["pooled"], rows["a"]["scarcity_state"]["pooled"])


class SharedColumnsTests(unittest.TestCase):
    """`shared_columns` is how the `derived631` command (#785) gathers #631's rows: the days every named row forecasts, up to the last scored day."""

    def _doc(self, **rows):
        return {"forecasts": {name: {"5": column} for name, column in rows.items()}}

    def test_only_the_shared_days_up_to_the_last_day_are_kept(self):
        a = self._doc(x={"2018-07-02": 0.1, "2018-07-03": 0.2, "2018-07-04": 0.3, "2026-01-02": 0.4})
        b = self._doc(y={"2018-07-02": 0.5, "2018-07-03": 0.6, "2026-01-02": 0.7})
        days, columns = S.shared_columns([a, b], ["x", "y"], "5", S.date(2025, 12, 31))
        self.assertEqual(days, [S.date(2018, 7, 2), S.date(2018, 7, 3)])
        self.assertEqual(columns["x"], [0.1, 0.2])
        self.assertEqual(columns["y"], [0.5, 0.6])

    def test_a_row_no_file_carries_is_refused_by_name(self):
        with self.assertRaisesRegex(ValueError, "'z'"):
            S.shared_columns([self._doc(x={"2018-07-02": 0.1})], ["x", "z"], "5", S.date(2025, 12, 31))

    def test_no_shared_day_is_refused(self):
        a = self._doc(x={"2018-07-02": 0.1}, y={"2018-07-03": 0.2})
        with self.assertRaises(ValueError):
            S.shared_columns([a], ["x", "y"], "5", S.date(2025, 12, 31))


class Derived631TextTests(unittest.TestCase):
    def test_the_page_names_its_days_and_a_kinked_table_keeps_its_title(self):
        cell = {"days": 100, "events": 8, "slope": 0.5, "intercept": -1.0, "slope_interval": [0.2, 0.9], "intercept_interval": [-2.0, 0.0]}
        body = {"days": 100, "events": 8, "rows": {"r": {"regime": {"pooled": cell}, "scarcity_state": {"pooled": cell}}}}
        result = {"level": 0.9, "replications": 40, "block_length": 10, "horizons": {"1": body}}
        self.assertIn("#626's rows on the days that are not risk dates", S.kinked_text(result))
        result["title"] = S.DERIVED631_TITLE
        text = S.kinked_text(result)
        self.assertIn("#631's rows on the ordinary days", text)
        self.assertNotIn("#626", text)


if __name__ == "__main__":
    unittest.main()
