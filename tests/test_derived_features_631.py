"""The derived-feature screen and its one model test (#631): `scripts/derived_features_631.py`.

What is covered:

* `StatisticsTests` -- the AUROC, the logistic calibration, the clusters at |rho| >= 0.8 and the interval's reading, to hand-worked values.
* `DeclarationTests` -- `metadata/derived_features_631.json` is committed, lists exactly the columns the script builds, the four
  interactions, the model test's rows and inputs, and the candidate files agree with it; nothing is on the confirmation roster.
* `ReadTests` -- a derived column is read through the as-of rule at the row where its source fields are public, and a locked day is refused.
* `RunTests` -- `run` refuses a panel past 2026-09-03 (#684).

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run alone, each
confirmed applied by `grep` and restored before the next; the readers' own guards are recorded in `tests/test_derived_features.py`):

1. `read_all`: the line `require_unlocked((dates[i] for i in scored), where="derived_features_631")` -> `pass`, so a scored day in a locked
   tier is read. `ReadTests.test_a_locked_day_is_refused` fails with `AssertionError: LookAheadError not raised`.
2. `run_command`: `if rows[-1].date > date.fromisoformat(LAST_DAY):` -> `if False:`, so a panel that runs into the locked tiers is accepted.
   `RunTests.test_a_panel_past_the_last_day_is_refused` errors with `ValueError: the row carries no 'days_to_month_end'` (the run goes on to read the panel instead of exiting).
3. `panel_command`: the line `require_unlocked([last], where="derived_features_631")` -> `pass`; `RunTests.test_the_panel_command_refuses_a_locked_last_day`
   errors with `ValueError: the H.4.1 week of Wednesday 2026-01-07 ... is outside the declared coverage` (the guard is skipped and the build goes on).
"""

from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "tests"))

from repo_model import measurement_fields  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


script = _load("derived_features_631")
from test_source_screen import synthetic_rows  # noqa: E402

DECLARATION = REPO_ROOT / "metadata" / "derived_features_631.json"
CANDIDATES = REPO_ROOT / "metadata" / "pressure_judge" / "candidates"


class StatisticsTests(unittest.TestCase):
    def test_auroc_is_the_hand_worked_value(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        y = [0, 0, 1, 1, 1, 1, 1]
        self.assertAlmostEqual(script.auroc(x, y), 1.0)
        self.assertAlmostEqual(script.auroc(x[::-1], y), 0.0)
        # five pressure days among eight, one tie: ranks of x = 1, 2, 3, 4.5, 4.5, 6, 7, 8; pressure ranks 4.5, 6, 7, 8, 1 -> sum 26.5
        x = [3.0, 5.0, 5.0, 6.0, 7.0, 8.0, 2.0, 1.0]
        y = [0, 1, 0, 1, 1, 1, 0, 1]
        ranks = [3, 4.5, 4.5, 6, 7, 8, 2, 1]
        r1 = sum(r for r, v in zip(ranks, y) if v)
        self.assertAlmostEqual(script.auroc(x, y), (r1 - 5 * 6 / 2) / (5 * 3))

    def test_auroc_needs_enough_pressure_days(self):
        self.assertIsNone(script.auroc([1.0, 2.0, 3.0, 4.0, 5.0], [0, 0, 0, 1, 1]))

    def test_calibration_is_not_formed_for_a_constant_forecast(self):
        self.assertIsNone(script.logistic_calibration([0.0] * 100, [0, 1] * 50))

    def test_calibration_of_a_forecast_equal_to_the_rate_in_each_bin_is_near_the_identity(self):
        p, y = [], []
        for rate, n in ((0.1, 200), (0.3, 200), (0.6, 200)):
            hits = int(round(rate * n))
            p += [rate] * n
            y += [1] * hits + [0] * (n - hits)
        fit = script.logistic_calibration(p, y)
        self.assertAlmostEqual(fit["slope"], 1.0, places=3)
        self.assertAlmostEqual(fit["intercept"], 0.0, places=3)

    def test_clusters_join_series_at_the_threshold_and_name_the_most_central_member(self):
        names = ["a", "b", "c", "d"]
        rho = [
            [1.0, 0.9, 0.5, 0.1],
            [0.9, 1.0, -0.85, 0.2],
            [0.5, -0.85, 1.0, 0.0],
            [0.1, 0.2, 0.0, 1.0],
        ]
        clusters = script.clusters_of(names, rho)
        self.assertEqual(clusters, [{"members": ["a", "b", "c"], "representative": "b"}])
        self.assertEqual(script.clusters_of(names, [[1.0, 0.79, 0, 0], [0.79, 1.0, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]]), [])

    def test_an_interval_reads_above_below_or_around_one_half(self):
        self.assertEqual(script._excludes({"auroc": 0.7, "interval": [0.55, 0.8]}), 1)
        self.assertEqual(script._excludes({"auroc": 0.3, "interval": [0.2, 0.45]}), -1)
        self.assertEqual(script._excludes({"auroc": 0.52, "interval": [0.4, 0.6]}), 0)
        self.assertEqual(script._excludes({"auroc": 0.52, "interval": None}), 0)


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.declared = json.loads(DECLARATION.read_text(encoding="utf-8"))

    def test_it_is_committed_and_the_script_writes_it_unchanged(self):
        self.assertEqual(self.declared, json.loads(json.dumps(script.declaration_document())))
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(DECLARATION)], cwd=REPO_ROOT, capture_output=True)
        self.assertEqual(tracked.returncode, 0)

    def test_it_lists_the_columns_the_script_builds(self):
        features = self.declared["features"]
        declared = set(features["volatility"]["columns"] + features["run_length"]["columns"] + features["days_since_pressure"]["columns"]
                       + features["rate_ranges"]["columns"] + self.declared["lagged_pressure"]["columns"])
        built = set(script.spec_for()) - {"reserve_change_5"}
        self.assertEqual(declared, built)
        self.assertEqual(set(features["calendar"]["columns"]), set(script.CALENDAR) | {"days_to_month_end"})
        self.assertEqual(set(self.declared["interactions"]), set(script.INTERACTIONS))
        self.assertEqual(set(script.INTERACTIONS), {"tail_x_scarcity", "tgachg_x_satdist", "settle_x_scarcity", "netsettle_x_scarcity", "tail_x_reservetrend"})

    def test_it_declares_the_leads_the_directive_asks_for_and_no_day_after_the_exploratory_end(self):
        self.assertEqual(self.declared["leads"], [1, 2, 3, 5, 10])
        # the screen reads to the exploratory end (#684); the model test scores through the judge, which ends 2025-12-31
        self.assertEqual(self.declared["scope"]["last_day"], "2026-09-03")
        self.assertEqual(self.declared["model_test"]["scoring"]["last_day"], "2025-12-31")

    def test_the_model_test_is_one_comparison_and_the_candidates_agree_with_it(self):
        test = self.declared["model_test"]
        self.assertEqual(test["added_inputs"], list(script.MODEL_INPUTS))
        parent = json.loads((CANDIDATES / f"{script.PARENT}.json").read_text(encoding="utf-8"))
        row = json.loads((CANDIDATES / f"{script.TEST}.json").read_text(encoding="utf-8"))
        self.assertEqual([f for f in row["features"] if f not in parent["features"]], list(script.MODEL_INPUTS))
        judge = json.loads((REPO_ROOT / "metadata" / "pressure_judge.json").read_text(encoding="utf-8"))
        self.assertNotIn(script.TEST, judge["confirmation"]["candidates"])
        self.assertNotIn(script.PARENT, judge["confirmation"]["candidates"])


class ReadTests(unittest.TestCase):
    def read(self, rows, columns):
        ann = script._modules()[1]
        with mock.patch.object(ann, "arm_inputs", lambda arm, rows_, registry, horizon: (rows_, registry)), script.switched():
            return script.read_all(rows, measurement_fields.load_registry(), list(columns))

    def test_a_calendar_column_is_read_on_the_scored_day_and_a_derived_one_at_the_public_row(self):
        rows = synthetic_rows(date(2018, 4, 3), 130)
        from repo_model.data import DailyObservation

        # the derived column carries its own row number, so the row a read lands on can be seen from its value
        rows = [DailyObservation(r.date, {**r.values, "dow": float(r.date.weekday()), "pressure_last": float(k)}) for k, r in enumerate(rows)]
        scored, series, _hidden, kinds = self.read(rows, ["dow", "pressure_last"])
        self.assertEqual(kinds["dow"], "calendar")
        self.assertEqual(kinds["pressure_last"], "observed")
        self.assertEqual(series[1]["dow"], [float(d.weekday()) for d in scored])
        position = {r.date: i for i, r in enumerate(rows)}
        k = position[scored[0]]
        # the SOFR and IORB legs are public two panel days after their row at the 16:00 decision, as the daily series of the source screen are
        for lead in script.LEADS:
            self.assertEqual(series[lead]["pressure_last"][0], float(k - 1 - lead))

    def test_a_locked_day_is_refused(self):
        rows = synthetic_rows(date(2026, 6, 1), 140)
        self.assertGreater(rows[-1].date, date(2026, 9, 3))
        with mock.patch.object(script, "FIRST_DAY", "2026-08-20"), mock.patch.object(script, "LAST_DAY", rows[-1].date.isoformat()):
            with self.assertRaises(LookAheadError):
                self.read(rows, ["sofr_volume"])


class RunTests(unittest.TestCase):
    def write_panel(self, directory, rows):
        path = Path(directory) / "panel.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["date", "sofr", "iorb"])
            for row in rows:
                writer.writerow([row.date.isoformat(), repr(row.values["sofr"]), repr(row.values["iorb"])])
        return path

    def test_a_panel_past_the_last_day_is_refused(self):
        rows = synthetic_rows(date(2026, 6, 1), 140)  # runs past 2026-09-03 (#684)
        self.assertGreater(rows[-1].date, date(2026, 9, 3))
        with tempfile.TemporaryDirectory() as directory:
            panel = self.write_panel(directory, rows)
            with self.assertRaises(SystemExit):
                script.main(["run", "--panel", str(panel), "--output", str(Path(directory) / "out.json")])

    def test_the_panel_command_refuses_a_locked_last_day(self):
        with tempfile.TemporaryDirectory() as directory:
            panel = self.write_panel(directory, synthetic_rows(date(2025, 8, 1), 140))
            with mock.patch.object(script, "_committed", lambda: {**json.loads(DECLARATION.read_text()), "scope": {"last_day": "2026-12-31"}}):
                with self.assertRaises(LookAheadError):
                    script.main(["panel", "--panel", str(panel), "--output", str(Path(directory) / "out.csv")])


if __name__ == "__main__":
    unittest.main()
