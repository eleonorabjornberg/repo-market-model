"""The exploratory source screen (#478): `scripts/source_screen.py`.

The screen reads every series as of the decision instant at leads of 1, 2, 3, 5 and 10 panel days
and correlates it with the spread and with the +5 bp pressure indicator. These tests hold its
statistics to hand-worked values, its reads to the as-of rule, its inventory to the snapshot
directory, and its refusal to read a day in a locked tier.

Mutation record (disposable copy, `-B`, control green before and after):

1. `scripts/source_screen.py`, `read_series`: `except LookAheadError:` -> `except KeyError:`, so a
   scheduled input announced after a longer lead's decision instant is no longer a hole at that lead.
   Kills `ReadTests.test_a_scheduled_input_is_a_hole_at_a_longer_lead` with `LookAheadError`
   (`'treasury_settlement' for the forecast of 2018-06-29 reads 2018-06-29, first observable at
   2018-06-28 15:00:00, after the 2018-06-27 16:00:00 decision`).
2. `scripts/source_screen.py`, `read_series`: the line
   `require_unlocked((dates[index] for index in scored), where="source_screen")` -> `pass`, so a scored
   day in a locked tier is read. Kills `ReadTests.test_a_locked_day_is_refused` with `AssertionError`
   (`LookAheadError not raised`).
3. `scripts/source_screen.py`, `run_command`: `if rows[-1].date > LAST_DAY:` -> `if False:`, so a panel
   that runs into the locked tiers is accepted. Kills `RunTests.test_a_panel_past_the_last_day_is_refused`
   with `AssertionError` (`SystemExit not raised`).
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from repo_model import measurement_fields  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


screen = _load("source_screen")

SNAPSHOTS = REPO_ROOT / "tests" / "fixtures" / "snapshots"
REGISTRY = measurement_fields.load_registry()


def synthetic_rows(first, count, spike_every=7):
    """Weekday rows from `first`: a 3 bp spread, 8 bp (a pressure day) every `spike_every` rows.

    `sofr_volume` and `treasury_settlement` are the row counter, so a read's row can be seen from its value.
    """

    rows, day, counter = [], first, 0
    while len(rows) < count:
        if day.weekday() < 5:
            sofr = 1.83 if counter % spike_every == spike_every - 1 else 1.78
            rows.append(
                DailyObservation(
                    day,
                    {
                        "sofr": sofr,
                        "iorb": 1.75,
                        "sofr_volume": float(counter),
                        "treasury_settlement": float(counter * 10),
                    },
                )
            )
            counter += 1
        day += timedelta(days=1)
    return rows


class StatisticsTests(unittest.TestCase):
    def test_ranks_average_ties(self):
        self.assertEqual(screen.average_ranks([5, 6, 7, 8, 7]), [1.0, 2.0, 3.5, 5.0, 3.5])

    def test_spearman_of_a_monotone_pair_is_one_and_of_a_reversed_pair_minus_one(self):
        self.assertAlmostEqual(screen.spearman([1, 2, 3, 4], [10, 400, 500, 9000]), 1.0)
        self.assertAlmostEqual(screen.spearman([1, 2, 3, 4], [9, 7, 5, 1]), -1.0)

    def test_spearman_with_ties_is_the_hand_worked_value(self):
        # ranks x = 1..5, ranks y = 1, 2, 3.5, 5, 3.5: sum of products 8, sums of squares 10 and 9.5
        self.assertAlmostEqual(screen.spearman([1, 2, 3, 4, 5], [5, 6, 7, 8, 7]), 8 / (95 ** 0.5))

    def test_a_constant_side_has_no_correlation(self):
        self.assertIsNone(screen.spearman([1, 1, 1, 1], [1, 2, 3, 4]))
        self.assertIsNone(screen.spearman([1, 2, 3, 4], [0, 0, 0, 0]))

    def test_the_pre_onset_contrast_is_the_hand_worked_value(self):
        contrast = screen.pre_onset_contrast([3.0, 4.0], [1.0, 2.0, 3.0])
        self.assertEqual((contrast["n_pre"], contrast["n_other"]), (2, 3))
        self.assertAlmostEqual(contrast["mean_pre"], 3.5)
        self.assertAlmostEqual(contrast["mean_other"], 2.0)
        self.assertAlmostEqual(contrast["std_diff"], 1.5)  # the other days' sd is 1
        self.assertAlmostEqual(contrast["auc"], (2 + 0.5 + 3) / 6)

    def test_a_contrast_needs_values_on_both_sides(self):
        self.assertIsNone(screen.pre_onset_contrast([], [1.0, 2.0]))
        self.assertIsNone(screen.pre_onset_contrast([1.0], [2.0]))

    def test_a_cell_under_the_minimum_is_left_empty_not_zero(self):
        n = screen.MINIMUM_DAYS
        x = [float(i) for i in range(n)]
        few = [1.0 if i < screen.MINIMUM_PRESSURE - 1 else 0.0 for i in range(n)]
        enough = [1.0 if i < screen.MINIMUM_PRESSURE else 0.0 for i in range(n)]
        cell = screen.correlate(x, {"level": x, "pressure": few}, range(n))
        self.assertIsNone(cell["pressure"]["rho"])
        self.assertEqual(cell["pressure"]["pressure_days"], screen.MINIMUM_PRESSURE - 1)
        self.assertAlmostEqual(cell["level"]["rho"], 1.0)
        cell = screen.correlate(x, {"pressure": enough}, range(n))
        self.assertLess(cell["pressure"]["rho"], 0.0)
        cell = screen.correlate(x[: n - 1], {"level": x[: n - 1]}, range(n - 1))
        self.assertIsNone(cell["level"]["rho"])

    def test_a_missing_value_drops_the_day(self):
        n = screen.MINIMUM_DAYS + 5
        x = [None] * 5 + [float(i) for i in range(n - 5)]
        cell = screen.correlate(x, {"level": [float(i) for i in range(n)]}, range(n))
        self.assertEqual(cell["level"]["n"], n - 5)

    def test_the_bands_follow_the_group_calibration_split(self):
        self.assertEqual([screen.band(s) for s in (0.0, 1.0, 2.0, 3.0, None)],
                         ["ample", "ample", "scarce", "scarce", "unknown"])


class InventoryTests(unittest.TestCase):
    def test_every_snapshot_directory_is_in_the_inventory(self):
        directories = {path.name for path in SNAPSHOTS.iterdir() if path.is_dir()}
        self.assertEqual(directories, set(screen.SNAPSHOT_INVENTORY))

    def test_every_entry_says_read_or_cannot_and_why(self):
        for name, (status, note) in screen.SNAPSHOT_INVENTORY.items():
            with self.subTest(snapshot=name):
                self.assertIn(status, ("read", "cannot"))
                self.assertTrue(note.strip())

    def test_the_five_passers_are_declared_candidates_and_use_the_lagged_spread(self):
        declared = json.loads(screen.RISK_DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(len(set(screen.TIER_1_PASSERS)), 5)
        self.assertLessEqual(set(screen.TIER_1_PASSERS), set(declared["candidates"]))
        used = screen.tier_one_usage()
        self.assertEqual(set(used["spread_bps"]), set(screen.TIER_1_PASSERS))
        self.assertEqual(set(used["on_rrp"]), {"risk_gbm", "risk_logistic"})  # the 'new' inputs: not the _base twins

    def test_a_raw_input_is_declared_on_its_modules_fields(self):
        declared = screen.declared_features()
        for column in ("bgcr_volume", "ofr_dvp_rate", "srf_take_up", "on_rrp", "reserve_scarcity_state"):
            self.assertIn(column, declared)


class ReadTests(unittest.TestCase):
    def read(self, rows, columns=("sofr_volume", "treasury_settlement")):
        with screen.Switched():
            return screen.read_series(rows, REGISTRY, list(columns))

    def test_a_daily_input_is_read_one_more_row_back_at_each_lead(self):
        rows = synthetic_rows(date(2018, 4, 3), 130)
        scored, series, _hidden, _kinds = self.read(rows)
        self.assertEqual(scored[0], screen.FIRST_DAY)
        position = {row.date: i for i, row in enumerate(rows)}
        k = position[scored[0]]
        # the NY Fed's daily series is public two panel days after its row at the 16:00 decision (information-set.md)
        for lead in screen.LEADS:
            self.assertEqual(series[lead]["sofr_volume"][0], float(k - 1 - lead))

    def test_the_spread_lag_is_the_anchor_rows_spread(self):
        rows = synthetic_rows(date(2018, 4, 3), 130)
        scored, series, _hidden, _kinds = self.read(rows)
        position = {row.date: i for i, row in enumerate(rows)}
        for lead in screen.LEADS:
            for day, value in zip(scored[:20], series[lead][screen.SPREAD_LAG]):
                self.assertLess(value, 100.0 * (1.83 - 1.75) + 1e-9)
                self.assertLess(position[day] - 1 - lead, position[day])

    def test_a_scheduled_input_is_a_hole_at_a_longer_lead(self):
        rows = synthetic_rows(date(2018, 4, 3), 130)
        scored, series, hidden, _kinds = self.read(rows)
        position = {row.date: i for i, row in enumerate(rows)}
        # announced the business day before: public at a lead of 1, not at a lead of 2 or more
        self.assertEqual(series[1]["treasury_settlement"][0], 10.0 * position[scored[0]])
        for lead in (2, 3, 5, 10):
            self.assertEqual(set(series[lead]["treasury_settlement"]), {None})
            self.assertEqual(hidden["treasury_settlement"][lead], len(scored))
        self.assertNotIn(1, hidden.get("treasury_settlement", {}))

    def test_a_locked_day_is_refused(self):
        # the near-blind tier was opened once (#151); the blind tier, after the panel's end, is locked
        rows = synthetic_rows(date(2026, 6, 1), 140)
        self.assertGreater(rows[-1].date, date(2026, 9, 3))
        with mock.patch.object(screen, "FIRST_DAY", date(2026, 8, 20)), mock.patch.object(
            screen, "LAST_DAY", rows[-1].date
        ):
            with self.assertRaises(LookAheadError):
                self.read(rows)


class RunTests(unittest.TestCase):
    def write_panel(self, directory, rows):
        path = Path(directory) / "panel.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["date", "sofr", "iorb", "sofr_volume", "treasury_settlement"])
            for row in rows:
                writer.writerow([row.date.isoformat()] + [repr(row.values[c]) for c in ("sofr", "iorb", "sofr_volume", "treasury_settlement")])
        return path

    def test_a_panel_past_the_last_day_is_refused(self):
        rows = synthetic_rows(date(2025, 8, 1), 140)
        with tempfile.TemporaryDirectory() as directory:
            panel = self.write_panel(directory, rows)
            with self.assertRaises(SystemExit):
                screen.main(["run", "--panel", str(panel), "--output", str(Path(directory) / "out.json")])

    def test_a_panel_with_an_ofr_value_before_it_was_public_is_refused(self):
        """The screen reads no OFR value from before 2020-09-09 (#522, of #508).

        Recorded mutation (CLAUDE.md), 10 October 2026, in a disposable copy:
        `scripts/source_screen.py`, the line `dvp_segment.require_ofr_public(rows)` in `run_command`
        deleted. This test then fails with `AssertionError` (`LookAheadError not raised`).
        """

        rows = synthetic_rows(date(2018, 4, 3), 330)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "panel.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["date", "sofr", "iorb", "ofr_dvp_rate"])
                for row in rows:
                    writer.writerow([row.date.isoformat(), repr(row.values["sofr"]), repr(row.values["iorb"]), "2.1"])
            with self.assertRaises(LookAheadError):
                screen.main(["run", "--panel", str(path), "--output", str(Path(directory) / "out.json")])

    def test_the_panel_command_blanks_ofr_columns_before_they_were_public(self):
        rows = synthetic_rows(date(2020, 9, 1), 12)
        with tempfile.TemporaryDirectory() as directory:
            base = self.write_panel(directory, rows)
            extra = Path(directory) / "extra.csv"
            with extra.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["date", "sofr", "iorb", "ofr_dvp_rate", "ofr_dvp_minus_bgcr_bp_backfill"])
                for row in rows:
                    writer.writerow([row.date.isoformat(), repr(row.values["sofr"]), repr(row.values["iorb"]), "2.1", "5.0"])
            out = Path(directory) / "screen.csv"
            with mock.patch("sys.stdout"):
                screen.main(["panel", "--panel", str(base), "--extra", str(extra), "--output", str(out)])
            with out.open(newline="", encoding="utf-8") as handle:
                table = list(csv.DictReader(handle))
            for line in table:
                for column in ("ofr_dvp_rate", "ofr_dvp_minus_bgcr_bp_backfill"):
                    blank = line[column] == ""
                    self.assertEqual(blank, line["date"] < "2020-09-09", (line["date"], column))

    def test_a_run_and_its_report_are_deterministic_and_complete(self):
        rows = synthetic_rows(date(2018, 4, 3), 330)
        with tempfile.TemporaryDirectory() as directory:
            panel = self.write_panel(directory, rows)
            outputs = []
            for name in ("a.json", "b.json"):
                out = Path(directory) / name
                with mock.patch("sys.stdout"):
                    screen.main(["run", "--panel", str(panel), "--output", str(out)])
                outputs.append(out.read_text(encoding="utf-8"))
            self.assertEqual(outputs[0], outputs[1])
            result = json.loads(outputs[0])
            scope = result["scope"]
            self.assertEqual(scope["leads"], list(screen.LEADS))
            self.assertEqual(scope["first_day"], "2018-06-29")
            self.assertLessEqual(scope["last_day"], "2025-12-31")
            self.assertEqual(scope["series_screened"], 3)  # sofr_volume, treasury_settlement, the lagged spread
            self.assertEqual(scope["correlations_computed"], 3 * len(screen.LEADS) * 3)
            self.assertGreater(scope["pressure_days"], 0)
            self.assertEqual(sorted(result["snapshots"]), sorted(screen.SNAPSHOT_INVENTORY))
            self.assertEqual(set(result["series"]["sofr_volume"]["leads"]), {str(l) for l in screen.LEADS})
            cell = result["series"]["sofr_volume"]["leads"]["1"]["all"]
            self.assertEqual(set(cell), set(screen.TARGETS))
            tables = screen.tables_markdown(result)
            for heading in ("## Ranking", "## Pre-onset window", "## By regime", "## By year"):
                self.assertIn(heading, tables)
            self.assertIn("2018", tables)
            svg = screen.heatmap_svg(result)
            self.assertTrue(svg.startswith("<svg"))
            self.assertIn("sofr_volume", svg)
            self.assertEqual(svg, screen.heatmap_svg(result))


if __name__ == "__main__":
    unittest.main()
