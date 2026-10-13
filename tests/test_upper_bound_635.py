"""The upper-bound study (#635): `scripts/upper_bound_635.py`.

What is covered:

* `StatisticsTests` -- the AUROC, the Brier score, the interval and the blocks, to hand-worked values.
* `EmbargoTests` -- the walk-forward's training set holds only rows public at the block's first decision instant, and a row after it is a
  `LookAheadError`.
* `DeclarationTests` -- `metadata/upper_bound_635.json` is committed, the script writes it unchanged, it lists the inputs, key columns, settings
  and the reading rule the script uses, and it reads no day after 2025-12-31.
* `ReadingTests` -- the pre-registered reading maps the three cases of the issue to their verdicts.
* `RunTests` -- `fit` refuses a panel past 2025-12-31.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run alone, each confirmed
applied by `grep` and restored before the next):

1. `require_public_labels`: the line `if label_rows[position] > anchor_row:` -> `if label_rows[position] > anchor_row + 5:`, so a label up to five
   rows after the last public row passes the guard. `EmbargoTests.test_a_label_after_the_anchor_is_refused` fails with
   `AssertionError: LookAheadError not raised`.
2. `training_positions`: the line `chosen = [position for position, row in enumerate(label_rows) if row <= anchor_row]` -> `... if row <= anchor_row + 1]`,
   so the selection takes the row after the anchor. `EmbargoTests.test_the_training_set_is_the_rows_at_or_before_the_anchor` errors with
   `LookAheadError` (the guard behind the selection stops it).
3. `read_inputs`: the line `require_unlocked((dates[i] for i in scored), where="upper_bound_635")` -> `pass`, so a scored day in a locked tier is
   read. `ReadingTests.test_a_locked_day_is_refused` fails with `AssertionError: LookAheadError not raised`.
4. `fit_command`: the line `if rows[-1].date > date.fromisoformat(LAST_DAY):` -> `if False:`, so a panel that runs into the locked tiers is
   accepted. `RunTests.test_a_panel_past_the_last_day_is_refused` errors with `ValueError: the row carries no 'days_to_month_end'` (the run goes
   on to read the panel instead of exiting).
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


script = _load("upper_bound_635")
from test_source_screen import synthetic_rows  # noqa: E402

DECLARATION = REPO_ROOT / "metadata" / "upper_bound_635.json"


class StatisticsTests(unittest.TestCase):
    def test_auroc_is_the_hand_worked_value(self):
        # five pressure days (labels 1) at 4, 5, 6, 7, 8 and four others at 1, 2, 3, 5: pairs won 3 + 3 + 4 + 4 + 4, one tie, of 20
        scores = [4, 5, 6, 7, 8, 1, 2, 3, 5]
        labels = [1, 1, 1, 1, 1, 0, 0, 0, 0]
        self.assertAlmostEqual(script.auroc(scores, labels), 18.5 / 20)

    def test_auroc_is_not_formed_under_five_pressure_days(self):
        self.assertIsNone(script.auroc([1, 2, 3, 4, 5], [1, 1, 0, 0, 0]))

    def test_brier_is_the_mean_squared_error(self):
        self.assertAlmostEqual(script.brier([0.5, 1.0, 0.0], [1, 1, 1]), (0.25 + 0.0 + 1.0) / 3)
        self.assertIsNone(script.brier([], []))

    def test_the_interval_is_the_5th_to_95th_percentile(self):
        low, high = script.percentile_interval(list(range(101)))
        self.assertAlmostEqual(low, 5.0)
        self.assertAlmostEqual(high, 95.0)

    def test_blocks_are_runs_of_21_and_the_last_is_short(self):
        self.assertEqual(script.blocks(50), [(0, 21), (21, 42), (42, 50)])


class EmbargoTests(unittest.TestCase):
    def test_the_training_set_is_the_rows_at_or_before_the_anchor(self):
        self.assertEqual(script.training_positions([3, 4, 5, 6, 7, 8], 6), [0, 1, 2, 3])

    def test_a_label_after_the_anchor_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_public_labels([3, 4, 5, 6, 7], [0, 1, 2, 3, 4], 5)
        script.require_public_labels([3, 4, 5, 6, 7], [0, 1, 2], 5)


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.declared = json.loads(DECLARATION.read_text(encoding="utf-8"))

    def test_it_is_committed_and_the_script_writes_it_unchanged(self):
        rebuilt = script.declaration_document(
            self.declared["inputs"]["columns"], self.declared["panel"]["columns_refused_by_the_as_of_rule"], self.declared["panel"]["sha256"]
        )
        self.assertEqual(self.declared, json.loads(json.dumps(rebuilt)))
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(DECLARATION)], cwd=REPO_ROOT, capture_output=True)
        self.assertEqual(tracked.returncode, 0)

    def test_the_inputs_hold_the_interactions_the_last_public_spread_and_the_key_columns(self):
        inputs = self.declared["inputs"]["columns"]
        self.assertEqual(len(inputs), len(set(inputs)))
        for name in list(script.d631.INTERACTIONS) + [script.SPREAD_ASOF] + list(script.KEY_COLUMNS):
            self.assertIn(name, inputs)
        self.assertEqual(self.declared["models"]["key_columns_interacted"], list(script.KEY_COLUMNS))

    def test_it_reads_no_day_after_2025_and_no_lead_beyond_five(self):
        self.assertEqual(self.declared["scope"]["last_day"], "2025-12-31")
        self.assertEqual(self.declared["scope"]["leads"], [1, 2, 3, 4, 5])
        self.assertEqual(self.declared["fits"]["reachable"]["refit_every_scored_days"], script.REFIT_EVERY)
        self.assertEqual(self.declared["fits"]["reachable"]["minimum_training_rows"], script.MINIMUM_TRAIN)

    def test_the_reading_rule_is_the_issues(self):
        rule = self.declared["reading_rule"]
        self.assertIn("persistence-logistic", rule["barely_above"]["indicator"])
        self.assertIn("under 0.6", rule["secondary_indicator_reading"])
        self.assertEqual(set(rule["verdict"]), {"data problem", "model problem", "partly reached"})
        self.assertEqual(script.AUROC_LINE, 0.6)

    def test_the_two_deviations_of_the_ruling_are_declared(self):
        self.assertEqual([d["number"] for d in self.declared["deviations"]], [1, 2])
        for deviation in self.declared["deviations"]:
            self.assertIn("6149433242", deviation["ruling"])
        self.assertIn("memorised", self.declared["fits"])


class ReadingTests(unittest.TestCase):
    @staticmethod
    def document(ceiling_low, reachable_low, ceiling_auc, reachable_auc):
        def spread_cell(low):
            return {"n": 10, "tests": {f"B1 -> {fit} {m}": {"skill": 0.1, "skill_interval_90": [low, 0.2], "n": 10} for fit in ("ceiling", "reachable") for m in script.MODELS}}

        def pair(low):
            return {f"reachable {m} -> ceiling {m}": {"skill": 0.0} for m in script.MODELS}

        def indicator_cell(auc):
            return {m: {"auroc": auc, "auroc_interval_90": [auc - 0.01, auc + 0.01]} for m in ("gbm", "ridge")} | {"persistence_logistic": {"auroc": 0.85}}

        walk = spread_cell(reachable_low)
        walk["tests"].update(pair(0))
        return {
            "spread": {"walk": {"ordinary": {"crps": walk}}, "full": {"ordinary": {"crps": spread_cell(ceiling_low)}}},
            "indicator": {
                "cells": {
                    "ceiling | full | ordinary, pooled": indicator_cell(ceiling_auc),
                    "reachable | walk | ordinary, pooled": indicator_cell(reachable_auc),
                }
            },
        }

    def test_a_ceiling_whose_interval_covers_zero_is_a_data_problem(self):
        out = script.reading(self.document(-0.01, 0.05, 0.9, 0.9))
        self.assertEqual(out["spread"]["verdict"], "data problem")

    def test_a_ceiling_above_and_a_reachable_line_near_the_benchmark_is_a_model_problem(self):
        out = script.reading(self.document(0.05, -0.02, 0.9, 0.9))
        self.assertEqual(out["spread"]["verdict"], "model problem")

    def test_both_above_is_partly_reached(self):
        out = script.reading(self.document(0.05, 0.02, 0.9, 0.9))
        self.assertEqual(out["spread"]["verdict"], "partly reached")

    def test_an_auroc_under_the_line_is_barely_above(self):
        out = script.reading(self.document(0.05, 0.02, 0.59, 0.9))
        self.assertEqual(out["indicator"]["verdict"], "data problem")
        out = script.reading(self.document(0.05, 0.02, 0.9, 0.55))
        self.assertEqual(out["indicator"]["verdict"], "model problem")

    def test_a_locked_day_is_refused(self):
        rows = synthetic_rows(date(2026, 6, 1), 140)
        self.assertGreater(rows[-1].date, date(2026, 9, 3))
        with mock.patch.object(script.ann, "arm_inputs", lambda arm, rows_, registry, horizon: (rows_, registry)), script.d631.switched():
            with mock.patch.object(script, "FIRST_DAY", "2026-08-20"), mock.patch.object(script, "LAST_DAY", rows[-1].date.isoformat()):
                with self.assertRaises(LookAheadError):
                    script.read_inputs(rows, measurement_fields.load_registry(), ["sofr_volume"])


class RunTests(unittest.TestCase):
    def test_a_panel_past_the_last_day_is_refused(self):
        rows = synthetic_rows(date(2025, 8, 1), 140)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "panel.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["date", "sofr", "iorb"])
                for row in rows:
                    writer.writerow([row.date.isoformat(), repr(row.values["sofr"]), repr(row.values["iorb"])])
            declared = json.loads(DECLARATION.read_text(encoding="utf-8")) if DECLARATION.exists() else {}
            with mock.patch.object(script, "committed", lambda: declared):
                with self.assertRaises(SystemExit):
                    script.main(["fit", "--panel", str(path), "--output", str(Path(directory) / "out.json")])


if __name__ == "__main__":
    unittest.main()
