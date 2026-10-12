"""The rolling satiation distance in the tier-1 passers (#598, follow-up to #587): `repo_model.satiation`'s distance columns
and `scripts/satiation_distance_598.py`.

The rolling level of #587 is not re-tuned: its quantile, window and minimum are read from `metadata/satiation_587.json`. What is new
is two panel columns built from the same as-of ratio and that level, each read by the risk-date passers as one extra input:

* `satiation_dist_roll` (variant a): the reserves ratio minus the rolling level;
* `satiation_hinge_roll` (variants b and c): the percentage points by which the ratio is below the level, 0 at or above it.

What is covered:

* `DistanceTests` -- the arithmetic, and that a hole in either input is no value.
* `BuildDistanceTests` -- the columns on a panel read through the as-of rule: the ratio of the decision's own read, the level of
  #587, and **no later row moves an earlier value** (the criterion).
* `NoFutureDistanceTests` -- the guard that refuses a column built from a row after its own decision.
* `DeclarationTests` -- `metadata/satiation_distance_598.json` is written before any score, is at most three variants, reads #587's
  constants unchanged, and agrees with the module, the registry and the judge's candidate files; the columns are off in the published
  feature map.
* `VariantFeatureTests` -- a variant's features are its parent's with the one column added, nothing else.
* `RunGuardTests` -- `run` refuses a scored day in a locked tier.

**Recorded mutation for #622** (12 October 2026, disposable copy, `/opt/rmm-venv`): in `scripts/satiation_distance_598.py`, `distance_rule`,
`registry = h41_release.release_dated_registry(measurement_fields.load_registry(), ...)` replaced by `registry = measurement_fields.load_registry()`
(the weekly lag again). `ReleaseDatedReadTests.test_the_panel_rule_reads_the_release_dated_registry` fails with `AssertionError: 'release_calendar' not found in {...}`,
`test_a_friday_reads_the_print_of_its_own_wednesday_not_the_weekly_lag` with `AssertionError: [] is not true` and
`test_the_built_columns_follow_the_release_dated_ratio` errors.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run alone, each
confirmed applied by `grep` and restored before the next):

1. `build_distance_columns`: replace `ratio = ratios[i]` by `ratio = ratios[min(i + 1, len(ratios) - 1)]`. The distance at row `i`
   then reads the next row's ratio; `NoFutureDistanceTests.test_no_value_depends_on_a_later_row` errors with
   `LookAheadError: satiation_dist_roll on 2023-03-20 is 0.0162, but the panel cut at that row gives 0.0402; the column depended on a
   later row` (`test_the_columns_pass_when_they_use_nothing_later` and `BuildDistanceTests.test_a_day_after_the_last_scored_day_has_no_value`
   fail too).
2. `check_distance_no_future`: replace `if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-12):` by
   `if False:`. A column that differs from the cut panel's is no longer refused;
   `NoFutureDistanceTests.test_a_column_built_from_a_later_row_is_refused` fails with `AssertionError: LookAheadError not raised`.
3. `run_command`: replace `require_unlocked([last], where="satiation_distance_598")` by `pass`;
   `RunGuardTests.test_run_refuses_a_locked_last_day` fails with `FileNotFoundError` (the guard is skipped and the run goes on to read
   the panel).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, satiation as sat
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

from test_satiation import _Measured

REPO = Path(__file__).resolve().parents[1]
DECLARATION = REPO / "metadata" / "satiation_distance_598.json"
PARENT_DECLARATION = REPO / "metadata" / "satiation_587.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"


def _script():
    sys.path.insert(0, str(REPO / "src"))
    spec = importlib.util.spec_from_file_location("satiation_distance_598_script", REPO / "scripts" / "satiation_distance_598.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["satiation_distance_598_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()
LAST = date(2025, 12, 31)


def _declared():
    """The declaration file as read, without the script's committed-and-unchanged check (a working tree may be dirty)."""

    return json.loads(DECLARATION.read_text())


class DistanceTests(unittest.TestCase):
    def test_distance_is_the_ratio_minus_the_level(self):
        self.assertAlmostEqual(sat.distance(0.10, 0.12), -0.02)
        self.assertAlmostEqual(sat.distance(0.15, 0.12), 0.03)
        self.assertEqual(sat.distance(0.12, 0.12), 0.0)

    def test_a_hole_in_either_input_is_no_value(self):
        self.assertIsNone(sat.distance(None, 0.12))
        self.assertIsNone(sat.distance(0.1, None))

    def test_the_hinge_column_is_the_hinge_of_the_same_pair(self):
        self.assertEqual(sat.hinge_value(0.15, 0.12), 0.0)
        self.assertAlmostEqual(sat.hinge_value(0.10, 0.12), sat.hinge(0.10, 0.12))
        self.assertIsNone(sat.hinge_value(None, 0.12))


class _Distance(_Measured):
    def setUp(self):
        super().setUp()
        fields = dict(sat.DISTANCE_COLUMN_FIELDS)
        patch = mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
            FEATURE_SOURCES=MappingProxyType({
                **contract.FEATURE_SOURCES,
                **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
            }),
        )
        patch.start()
        self.addCleanup(patch.stop)

    def built_distance(self, rows=None):
        return sat.build_distance_columns(
            self.rows if rows is None else rows, self.rule(), last_day=LAST, q=0.1, window=100, minimum=20
        )


class ReleaseDatedReadTests(_Distance):
    """The distance columns read reserves per H.4.1 release, as the +h41 rows they join do (#622, ruling on #541)."""

    def ratios(self, rule):
        from repo_model import h41_release

        with h41_release.release_dating():
            return sat.asof_ratios(self.rows, rule, last_day=LAST)

    def test_the_panel_rule_reads_the_release_dated_registry(self):
        rule = SCRIPT.distance_rule()
        self.assertIn("release_calendar", rule.registry["fred_macro_latest_vintage"])

    def test_a_friday_reads_the_print_of_its_own_wednesday_not_the_weekly_lag(self):
        old = self.ratios(self.rule())
        new = self.ratios(SCRIPT.distance_rule())
        moved = [i for i, (a, b) in enumerate(zip(old, new)) if a is not None and b is not None and abs(a - b) > 1e-12]
        self.assertTrue(moved)

    def test_the_built_columns_follow_the_release_dated_ratio(self):
        end = LAST
        built = SCRIPT.distance_rows(self.rows, end, check_every=40)
        new = self.ratios(SCRIPT.distance_rule())
        rolling = SCRIPT.rolling_constants()
        level = sat.rolling_level(
            new, 300, q=rolling["quantile"], window=rolling["window_rows"], minimum=rolling["minimum_rows"]
        )
        self.assertAlmostEqual(built[300].values[sat.DISTANCE_COLUMN], new[300] - level)


class BuildDistanceTests(_Distance):
    def test_the_columns_are_the_ratio_the_rule_reads_against_the_rolling_level(self):
        ratios = sat.asof_ratios(self.rows, self.rule(), last_day=LAST)
        out = self.built_distance()
        level = sat.rolling_level(ratios, 200, q=0.1, window=100, minimum=20)
        self.assertAlmostEqual(out[200].values[sat.DISTANCE_COLUMN], ratios[200] - level)
        self.assertAlmostEqual(out[200].values[sat.HINGE_COLUMN], sat.hinge(ratios[200], level))

    def test_the_rolling_level_of_587_is_the_level_used(self):
        levels = sat.build_columns(self.rows, self.rule(), last_day=LAST, q=0.1, window=100, minimum=20)
        out = self.built_distance()
        ratios = sat.asof_ratios(self.rows, self.rule(), last_day=LAST)
        for i in (50, 120, 250):
            self.assertAlmostEqual(out[i].values[sat.DISTANCE_COLUMN] + levels[i].values[sat.ROLLING_COLUMN], ratios[i])

    def test_the_hinge_is_zero_when_the_ratio_is_at_or_above_the_level_and_the_distance_is_not(self):
        out = self.built_distance()
        above = [r for r in out if (r.values[sat.DISTANCE_COLUMN] or 0.0) > 0]
        below = [r for r in out if (r.values[sat.DISTANCE_COLUMN] or 0.0) < 0]
        self.assertTrue(above and below)
        self.assertTrue(all(r.values[sat.HINGE_COLUMN] == 0.0 for r in above))
        self.assertTrue(all(r.values[sat.HINGE_COLUMN] > 0.0 for r in below))

    def test_a_day_after_the_last_scored_day_has_no_value(self):
        out = sat.build_distance_columns(self.rows, self.rule(), last_day=self.rows[150].date)
        self.assertIsNone(out[151].values[sat.DISTANCE_COLUMN])
        self.assertIsNone(out[151].values[sat.HINGE_COLUMN])
        self.assertIsNotNone(out[150].values[sat.DISTANCE_COLUMN])

    def test_a_later_rows_values_do_not_move_an_earlier_value(self):
        full = self.built_distance()
        changed = [DailyObservation(r.date, dict(r.values)) for r in self.rows]
        for later in changed[201:]:
            later.values["reserve_balances"] = 9999.0
        again = self.built_distance(changed)
        for name in (sat.DISTANCE_COLUMN, sat.HINGE_COLUMN):
            self.assertEqual(full[200].values[name], again[200].values[name])
        # the weekly step in the planted ratio means some row inside the checked span changes its read
        self.assertNotEqual(self.built_distance(changed)[260].values[sat.DISTANCE_COLUMN], full[260].values[sat.DISTANCE_COLUMN])


class NoFutureDistanceTests(_Distance):
    """The guard that refuses a distance column built from a row after its own decision.

    Recorded mutation (#598): in `check_distance_no_future`, the comparison `if (have is None) != (want is None) or ...` -> `if False:`;
    `test_a_column_built_from_a_later_row_is_refused` then fails with `AssertionError: LookAheadError not raised`.
    """

    def test_the_columns_pass_when_they_use_nothing_later(self):
        sat.check_distance_no_future(
            self.rows, self.built_distance(), self.rule(), last_day=LAST, indices=range(60, 120, 15), q=0.1, window=100, minimum=20
        )

    def test_no_value_depends_on_a_later_row(self):
        # every third row of the span the weekly steps land in: a value at row i equals the one rebuilt from the panel cut at i
        sat.check_distance_no_future(
            self.rows, self.built_distance(), self.rule(), last_day=LAST, indices=range(40, 300, 3), q=0.1, window=100, minimum=20
        )

    def test_a_column_that_differs_from_the_cut_panels_is_refused(self):
        bent = [DailyObservation(r.date, dict(r.values)) for r in self.built_distance()]
        bent[100].values[sat.HINGE_COLUMN] += 0.5
        with self.assertRaises(LookAheadError):
            sat.check_distance_no_future(
                self.rows, bent, self.rule(), last_day=LAST, indices=[100], q=0.1, window=100, minimum=20
            )

    def test_a_column_built_from_a_later_row_is_refused(self):
        ratios = sat.asof_ratios(self.rows, self.rule(), last_day=LAST)
        level = sat.build_columns(self.rows, self.rule(), last_day=LAST, q=0.1, window=100, minimum=20)
        leaked = []
        for i, row in enumerate(self.rows):
            values = dict(row.values)
            ahead = min(i + 1, len(ratios) - 1)
            values[sat.DISTANCE_COLUMN] = sat.distance(ratios[ahead], level[i].values[sat.ROLLING_COLUMN])
            values[sat.HINGE_COLUMN] = sat.hinge_value(ratios[ahead], level[i].values[sat.ROLLING_COLUMN])
            leaked.append(DailyObservation(row.date, values))
        with self.assertRaises(LookAheadError):
            sat.check_distance_no_future(
                self.rows, leaked, self.rule(), last_day=LAST, indices=range(60, 200, 3), q=0.1, window=100, minimum=20
            )


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(DECLARATION.read_text())
        self.parent = json.loads(PARENT_DECLARATION.read_text())

    def test_at_most_three_variants_and_each_has_a_candidate_file(self):
        variants = self.document["variants"]
        self.assertLessEqual(len(variants), 3)
        self.assertEqual(set(variants), set(self.document["rows"]["new"]))
        for name in variants:
            entry = json.loads((CANDIDATES / f"{name}.json").read_text())
            self.assertEqual(entry["role"], "candidate", name)
            self.assertEqual(entry["parent"], variants[name]["parent"], name)
            self.assertIn(variants[name]["column"], entry["features"], name)

    def test_the_rolling_levels_constants_are_587s_not_retuned(self):
        rolling = self.parent["forms"]["rolling"]
        self.assertEqual(self.document["rolling_level"]["quantile"], rolling["quantile"])
        self.assertEqual(self.document["rolling_level"]["window_rows"], rolling["window_rows"])
        self.assertEqual(self.document["rolling_level"]["minimum_rows"], rolling["minimum_rows"])
        self.assertEqual(
            (rolling["quantile"], rolling["window_rows"], rolling["minimum_rows"]),
            (sat.ROLLING_QUANTILE, sat.ROLLING_WINDOW, sat.ROLLING_MINIMUM),
        )

    def test_the_declaration_says_what_the_module_computes(self):
        self.assertEqual(self.document["columns"]["distance"], sat.DISTANCE_COLUMN)
        self.assertEqual(self.document["columns"]["hinge"], sat.HINGE_COLUMN)
        self.assertEqual(
            {v["column"] for v in self.document["variants"].values()}, {sat.DISTANCE_COLUMN, sat.HINGE_COLUMN}
        )

    def test_the_registry_declares_both_columns_with_no_lag(self):
        registry = json.loads((REPO / "metadata" / "sources_measurement.json").read_text())
        entry = registry[sat.DISTANCE_SOURCE_ID]
        self.assertEqual(sorted(entry["fields"]), sorted([sat.DISTANCE_COLUMN, sat.HINGE_COLUMN]))
        self.assertEqual(entry["release_lag"]["days"], 0)
        self.assertEqual(sorted(sat.DISTANCE_COLUMN_FIELDS), sorted([sat.DISTANCE_COLUMN, sat.HINGE_COLUMN]))

    def test_the_columns_are_off_in_the_published_feature_map(self):
        for name in (sat.DISTANCE_COLUMN, sat.HINGE_COLUMN):
            self.assertNotIn(name, contract.FEATURE_FIELDS)

    def test_nothing_is_published_and_no_2026_day_is_scored(self):
        self.assertEqual(date.fromisoformat(self.document["scoring"]["last_day"]), LAST)
        self.assertIn("Nothing is published", self.document["status"])


class VariantFeatureTests(unittest.TestCase):
    def test_a_variant_is_its_parents_features_with_the_one_column(self):
        with mock.patch.object(SCRIPT, "declared_document", return_value=_declared()):
            for name, spec in _declared()["variants"].items():
                for h in (1, 2, 5):
                    parent = SCRIPT.parent_features(spec["parent"], h)
                    mine = SCRIPT.variant_features(name, h)
                    self.assertEqual(mine, parent + (spec["column"],), (name, h))
                    self.assertEqual(len(set(mine)), len(mine))
                    self.assertNotIn(spec["column"], parent)


class RunGuardTests(unittest.TestCase):
    def args(self, **changes):
        base = dict(horizon=1, panel=REPO / "no-such-panel.csv", published=REPO / "no-such-panel.csv",
                    output=REPO / "no-such-output.json")
        base.update(changes)
        return argparse.Namespace(**base)

    def test_run_refuses_a_locked_last_day(self):
        declared = _declared()
        declared["scoring"]["last_day"] = "2026-09-10"
        with mock.patch.object(SCRIPT, "declared_document", return_value=declared):
            with self.assertRaises(LookAheadError):
                SCRIPT.run_command(self.args())

    def test_the_declared_last_day_is_not_refused(self):
        with mock.patch.object(SCRIPT, "declared_document", return_value=_declared()), mock.patch.object(
            SCRIPT, "load_daily_panel", side_effect=FileNotFoundError
        ):
            with self.assertRaises(FileNotFoundError):  # past the guard, into the panel
                SCRIPT.run_command(self.args())

    def test_panel_refuses_a_locked_last_day(self):
        declared = _declared()
        declared["scoring"]["last_day"] = "2026-09-10"
        with mock.patch.object(SCRIPT, "declared_document", return_value=declared):
            with self.assertRaises(LookAheadError):
                SCRIPT.panel_command(argparse.Namespace(panel=REPO / "x.csv", output=REPO / "y.csv", check_every=40))


if __name__ == "__main__":
    unittest.main()
