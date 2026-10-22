"""The day-of-month level term (`src/repo_model/dom_calendar.py`, `scripts/dom_level_term_1032.py`, #1032, H5 step 2, Lens A of #958).

The property under test is the directive's second criterion: the term `dom_bucket`, the bucket of the *target* day's day of month, is read from the
target row at every lead h = 1 to 5. In every direct training pair of the variant it is the bucket of that pair's target date (not the origin's), and a
forecast is served it from the target row by the as-of rule (a calendar column). The tests read the design matrix the real
`ml.fit_gradient_boosted_quantiles` hands its estimators (`ml._fitted_levels` recorded, not replaced), through `InformationRule`, and identify a pair's
target row by its spread, which is unique per row in the synthetic frame.

Recorded mutations (run on the tree at the time of writing; the exception is the one the failing test raised):

* `dom_calendar.add_columns`, the line `values[COLUMN] = bucket(row.date)` changed to `values[COLUMN] = bucket(rows[max(index - 1, 0)].date)` (the term
  written one row off, the #914 defect): three tests fail with `AssertionError`. `TargetRowTests.test_the_term_is_the_targets_at_every_lead`:
  `Lists differ: [(10, 1.0, 2.0), (14, 2.0, 3.0), ...] != []` (the design holds the previous row's bucket where the target's is expected);
  `ServedFromTheTargetRowTests.test_the_term_is_read_at_the_target_row_at_every_lead`: `3.0 != 4.0 : 1`;
  `AddColumnsTests.test_a_row_carries_the_bucket_of_its_own_date`: `0.0 != 1.0`.
* `dom_level_term_1032.variant_fit`, the argument `training_pairs="direct"` changed to `training_pairs=None` (a one-step fit of the term):
  `TargetRowTests.test_the_term_is_the_targets_at_every_lead` fails with `ValueError` (`repo_model.one_step_guard` refuses the calendar column
  `dom_bucket` as served from the scored row, #947), and `TargetRowTests.test_the_variant_fit_demands_direct_pairs` fails with `AssertionError`
  (`None != 'direct'`).
* `dom_level_term_1032.walk_rows`, the line `m().require_study_window([row.date for row in rows])` removed:
  `StudyWindowTests.test_a_walk_over_a_day_after_the_study_end_is_refused` errors with `repo_model.splits.SplitError` (the walk goes on and fails
  elsewhere) instead of raising `LookAheadError`, so the test does not pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dom_level_term_1032_script", REPO / "scripts" / "dom_level_term_1032.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import dom_calendar, ml, one_step_guard, target_day_columns  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

from test_aligned_calendar_1027 import (  # noqa: E402
    ROWS, NeedsExtra, Recorded, business_days, design_names, panel, row_of_target,
)

m = script.m()


def with_term(count=ROWS):
    return dom_calendar.add_columns(panel(count))


class BucketTests(unittest.TestCase):
    def test_the_declared_buckets_partition_the_days_of_a_month(self):
        days = [day for lo, hi in dom_calendar.BUCKETS for day in range(lo, hi + 1)]
        self.assertEqual(days, list(range(1, 32)))

    def test_the_edges_fall_where_declared(self):
        expected = {1: 0, 5: 0, 6: 1, 14: 1, 15: 2, 18: 2, 19: 3, 23: 3, 24: 4, 31: 4}
        for day, bucket in expected.items():
            self.assertEqual(dom_calendar.bucket(date(2024, 1, day)), float(bucket), day)

    def test_the_trough_is_one_bucket(self):
        self.assertEqual({dom_calendar.bucket(date(2024, 3, d)) for d in range(19, 24)}, {3.0})
        self.assertNotEqual(dom_calendar.bucket(date(2024, 3, 18)), 3.0)
        self.assertNotEqual(dom_calendar.bucket(date(2024, 3, 24)), 3.0)


class AddColumnsTests(unittest.TestCase):
    def test_a_row_carries_the_bucket_of_its_own_date(self):
        for row in with_term():
            self.assertEqual(row.values[dom_calendar.COLUMN], dom_calendar.bucket(row.date))

    def test_it_is_a_function_of_the_date_alone(self):
        rows = panel()
        whole = dom_calendar.add_columns(rows)
        part = dom_calendar.add_columns(rows[:40])
        self.assertEqual([r.values[dom_calendar.COLUMN] for r in part], [r.values[dom_calendar.COLUMN] for r in whole[:40]])

    def test_nothing_else_moves_and_the_input_is_not_changed(self):
        rows = panel()
        before = [dict(r.values) for r in rows]
        out = dom_calendar.add_columns(rows)
        self.assertEqual([dict(r.values) for r in rows], before)
        for new, old in zip(out, before):
            self.assertEqual({k: v for k, v in new.values.items() if k != dom_calendar.COLUMN}, old)

    def test_a_panel_that_already_carries_the_column_is_refused(self):
        with self.assertRaises(ValueError):
            dom_calendar.add_columns(with_term(10))


class DeclaredTests(unittest.TestCase):
    def test_the_column_is_declared_a_target_day_column(self):
        self.assertIn(dom_calendar.COLUMN, target_day_columns.TARGET_DAY_COLUMNS)

    def test_the_guard_refuses_it_in_a_one_step_fit(self):
        self.assertIn(dom_calendar.COLUMN, one_step_guard.one_step_refusals((dom_calendar.COLUMN, "tga")))

    def test_it_is_not_a_published_calendar_feature(self):
        from repo_model import contract

        self.assertNotIn(dom_calendar.COLUMN, contract.CALENDAR_FEATURES)

    def test_switched_on_serves_it_as_a_calendar_column_and_restores(self):
        from repo_model import asof, contract

        with dom_calendar.switched_on():
            self.assertIn(dom_calendar.COLUMN, contract.CALENDAR_FEATURES)
            self.assertIn(dom_calendar.COLUMN, asof.CALENDAR_FEATURES)
        self.assertNotIn(dom_calendar.COLUMN, contract.CALENDAR_FEATURES)
        self.assertNotIn(dom_calendar.COLUMN, asof.CALENDAR_FEATURES)


class TargetRowTests(NeedsExtra):
    """The term, in each lead's direct pairs, is the bucket of the pair's target date."""

    def test_the_term_is_the_targets_at_every_lead(self):
        from repo_model import measurement_fields

        rows = with_term()
        dates = [r.date for r in rows]
        with m._load("net_settlement").switched_on(), dom_calendar.switched_on():
            registry = measurement_fields.load_registry()
            for h in script.HORIZONS:
                features = script.variant_features(h)
                rule = InformationRule(registry, tuple(features), decision_time=m.DECISION, horizon=h)
                fit = script.variant_fit(features)
                names = tuple(m.regressors(features))
                with Recorded() as recorded:
                    fit(rows, minimum_history=20, information=rule)
                design, targets, leaf = recorded.calls[0]
                self.assertEqual(leaf, m.LEAF)
                self.assertGreater(len(design), 30)
                column = design_names(names).index(dom_calendar.COLUMN)
                bad, differs = [], 0
                for line, target in zip(design, targets):
                    j = row_of_target(target)
                    if line[column] != dom_calendar.bucket(dates[j]):
                        bad.append((j, line[column], dom_calendar.bucket(dates[j])))
                    differs += dom_calendar.bucket(dates[j - h]) != dom_calendar.bucket(dates[j])
                self.assertEqual(bad, [], f"lead {h}: {bad[:3]}")
                self.assertGreater(differs, 0, "the control is empty: no pair's origin and target buckets differ")

    def test_a_one_step_fit_of_the_term_is_refused(self):
        rows = with_term()
        features = script.variant_features(1)
        with self.assertRaises(ValueError):
            ml.fit_gradient_boosted_quantiles(rows, regressors=tuple(m.regressors(features)), levels=m.GRID, minimum_history=20)

    def test_the_variant_fit_demands_direct_pairs(self):
        fit = script.variant_fit(script.variant_features(1))
        self.assertEqual(fit.keywords["training_pairs"], "direct")
        self.assertEqual(fit.keywords["min_samples_leaf"], m.LEAF)


class ServedFromTheTargetRowTests(unittest.TestCase):
    """Rule 2: a forecast for day T reads the term from the target row, at every lead, as of the decision instant (a calendar column needs no lag)."""

    def test_the_term_is_read_at_the_target_row_at_every_lead(self):
        from repo_model import measurement_fields

        rows = with_term()
        dates = [r.date for r in rows]
        with dom_calendar.switched_on():
            registry = measurement_fields.load_registry()
            for h in script.HORIZONS:
                rule = InformationRule(registry, (dom_calendar.COLUMN, "tga", "spread_bps"), decision_time=m.DECISION, horizon=h)
                target = 60
                info = rule.information_set(dates, target)
                rule.check(dates, info)
                feature_row = rule.observation(rows, info)
                self.assertEqual(feature_row[dom_calendar.COLUMN] if isinstance(feature_row, dict) else dict(feature_row.values)[dom_calendar.COLUMN],
                                 dom_calendar.bucket(dates[target]), h)


class VariantTests(unittest.TestCase):
    def test_the_inputs_are_the_direct_variants_plus_the_term_at_every_lead(self):
        for h in script.HORIZONS:
            self.assertEqual(script.variant_features(h), m.variant_features(m.DIRECT, h) + (dom_calendar.COLUMN,))

    def test_the_term_is_the_only_difference(self):
        self.assertEqual(script.DOM, "gbm_funding_cal_direct_dom")
        self.assertEqual(script.CONTROLS, (m.CONTROL, m.DIRECT, m.ALIGNED))

    def test_the_declaration_is_what_declare_writes(self):
        document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(document, json.loads(json.dumps(script.declaration_document())))
        self.assertEqual(document["issue"], 1032)
        self.assertEqual(list(document["variants"]), [script.DOM])

    def test_the_declaration_names_the_term_and_its_buckets(self):
        document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(document["term"]["column"], dom_calendar.COLUMN)
        self.assertEqual(document["term"]["buckets"], [list(b) for b in dom_calendar.BUCKETS])


class StudyWindowTests(NeedsExtra):
    def test_a_walk_over_a_day_after_the_study_end_is_refused(self):
        rows = [DailyObservation(date=d, values={}) for d in business_days(3)]
        late = rows + [DailyObservation(date=date(2026, 1, 5), values={})]
        with self.assertRaises(LookAheadError):
            script.walk_rows(late, 1, minimum_history=20, refit_every=21)


class ReadingTests(unittest.TestCase):
    @staticmethod
    def row(skill, lo, hi):
        return {"skill": skill, "skill_interval": [lo, hi], "days": 100}

    def test_the_term_helps_when_the_pooled_lower_bound_is_above_zero(self):
        out = script.reading({"pooled": self.row(0.02, 0.005, 0.03), "trough": self.row(0.05, 0.01, 0.09), "ordinary": self.row(0.0, -0.01, 0.01)})
        self.assertIn("helps", out[0])
        self.assertNotIn("is not shown", out[0])

    def test_the_term_is_not_shown_to_help_when_the_bound_straddles_zero(self):
        out = script.reading({"pooled": self.row(0.01, -0.02, 0.04), "trough": self.row(0.05, 0.01, 0.09), "ordinary": self.row(0.0, -0.01, 0.01)})
        self.assertIn("is not shown to help", out[0])
        self.assertIn("helps", out[1])

    def test_a_loss_is_an_interval_wholly_below_zero(self):
        out = script.reading({"pooled": self.row(-0.03, -0.05, -0.01), "trough": self.row(0.0, -0.1, 0.1), "ordinary": self.row(-0.03, -0.05, -0.01)})
        self.assertIn("loses", " ".join(out))

    def test_an_undefined_cut_is_not_read(self):
        out = script.reading({"pooled": {"undefined": "x"}, "trough": self.row(0.0, -0.1, 0.1), "ordinary": self.row(0.0, -0.1, 0.1)})
        self.assertIn("not read", out[0])

    def test_the_bucket_label_of_a_target_day(self):
        self.assertEqual(script.bucket_label(date(2025, 3, 21)), "19-23")
        self.assertEqual(script.bucket_label(date(2025, 3, 31)), "24-31")
        self.assertEqual(script.bucket_label(date(2025, 3, 3)), "1-5")


if __name__ == "__main__":
    unittest.main()
