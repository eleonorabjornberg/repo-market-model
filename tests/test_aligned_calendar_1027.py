"""The aligned-calendar variants (`scripts/aligned_calendar_1027.py`, #1027, H5 step 3/4): what each variant trains every calendar and scheduled column from.

The property under test is the directive's second criterion: in every training pair of each variant, at every lead h = 1 to 5, each calendar or
scheduled column is the value of the *target row of that pair*, the row `asof.py` rule 2 serves it from. The tests read the design matrix the real
`ml.fit_gradient_boosted_quantiles` hands its estimators (`ml._fitted_levels` recorded, not replaced) and identify a pair's target row by its spread,
which is unique per row in the synthetic frame. Both training pairings are fitted for real: one-step pairs on the aligned frame, and direct pairs
through `InformationRule`.

Recorded mutations:

* `align_columns`, the line `values[field] = rows[position + 1].values.get(field)` changed to `rows[position].values.get(field)` (the one-step read of
  #914, the defect under test): `OneStepVariantTests.test_every_calendar_and_scheduled_column_is_the_targets_at_every_lead` fails with
  `AssertionError` (`Lists differ: [('quarter_end', 1, 10000.0, 10001.0), ...] != []`: the design holds row p's value, 10000.0, where the target row's is 10001.0).
* `require_study_window`, the line `if late:` changed to `if False:`: `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with
  `AssertionError` (`LookAheadError not raised`).
"""

from __future__ import annotations

import importlib.util
import os
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aligned_calendar_1027_script", REPO / "scripts" / "aligned_calendar_1027.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import ml, one_step_guard  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

#: the columns each variant reads from the target row, as the directive lists them (net_settlement* are observed columns and are not among them)
TARGET_ROW = ("quarter_end", "days_to_month_end", "tax_date", "treasury_settlement", "treasury_settlement_coupons", "treasury_settlement_bills")
OBSERVED = ("tga", "net_settlement", "net_settlement_due_5d")
ROWS = 90


def business_days(count):
    days, day = [], date(2024, 1, 1)
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def panel(count=ROWS):
    """Every row's every column is unique to its row (the column's index and the row's), and the spread is 1000 + the row."""

    columns = list(TARGET_ROW + OBSERVED)
    for h in script.HORIZONS:  # every other column a variant reads, observed
        columns += [c for c in script.regressors(script.variant_features(script.ALIGNED, h)) if c not in columns]
    out = []
    for i, day in enumerate(business_days(count)):
        values = {"sofr": 15.0 + i / 100.0, "iorb": 5.0}  # spread_bps = 100 * (sofr - iorb) = 1000 + i
        for k, name in enumerate(columns):
            values[name] = float(10_000 * (k + 1) + i)
        out.append(DailyObservation(date=day, values=values))
    return out


class Admitted:
    """Stands in for the allow-list entries Eleonora's decision would add (#947: the list is hers and pinned), for the one-step variant only."""

    def __enter__(self):
        entries = dict(one_step_guard.ONE_STEP_ALLOW_LIST)
        for h in script.HORIZONS:
            names = script.regressors(script.variant_features(script.ALIGNED, h))
            entries[f"stand_in_{h}"] = one_step_guard.FrozenDeclaration("fit_gradient_boosted_quantiles", tuple(names), "test stand-in")
        self._patch = mock.patch.object(one_step_guard, "ONE_STEP_ALLOW_LIST", entries)
        self._patch.start()
        return self

    def __exit__(self, *exc):
        self._patch.stop()


class Recorded:
    """Records the design and targets of every estimator set a fit builds, and lets the fit run."""

    def __init__(self):
        self.calls = []

    def __enter__(self):
        original = ml._fitted_levels

        def record(estimator_class, grid, design, targets, random_state, min_samples_leaf):
            self.calls.append(([list(row) for row in design], list(targets), min_samples_leaf))
            return original(estimator_class, grid, design, targets, random_state, min_samples_leaf)

        self._patch = mock.patch.object(ml, "_fitted_levels", record)
        self._patch.start()
        return self

    def __exit__(self, *exc):
        self._patch.stop()


REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"


class NeedsExtra(unittest.TestCase):
    """The fits below need the optional `ml` extra: skip without it, fail when CI's ml job says it must be there (as tests/test_ml.py does)."""

    def setUp(self):
        if all(importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn")):
            return
        if os.environ.get(REQUIRE_ML):
            self.fail(f"{REQUIRE_ML} is set but the optional 'ml' extra is not importable")
        self.skipTest("the optional 'ml' extra is not installed")


def row_of_target(spread):
    return int(round(spread - 1000.0))


def design_names(regressors):
    """The columns of a design row: the origin's spread, then each regressor in order."""

    return ("spread_bps",) + tuple(regressors)


def offenders(design, targets, names, rows, columns, row_for_column):
    """The (column, pair) cells where the design's value is not the value of the row `row_for_column(column, target row)`."""

    bad = []
    for line, target in zip(design, targets):
        j = row_of_target(target)
        for name in columns:
            expected = rows[row_for_column(name, j)].values[name]
            if line[names.index(name)] != expected:
                bad.append((name, j, line[names.index(name)], expected))
    return bad


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 30), date(2025, 12, 31)])


class AlignColumnsTests(unittest.TestCase):
    def test_row_p_carries_the_value_of_row_p_plus_1_for_each_named_column_and_nothing_else_moves(self):
        rows = panel(6)
        aligned = script.align_columns(rows, TARGET_ROW)
        for p in range(5):
            for name in TARGET_ROW:
                self.assertEqual(aligned[p].values[name], rows[p + 1].values[name])
            for name in OBSERVED + ("sofr", "iorb"):
                self.assertEqual(aligned[p].values[name], rows[p].values[name])
        self.assertEqual([r.date for r in aligned], [r.date for r in rows])

    def test_the_last_row_has_no_target_in_the_frame_and_is_a_hole_not_a_value_of_the_wrong_day(self):
        aligned = script.align_columns(panel(6), TARGET_ROW)
        for name in TARGET_ROW:
            self.assertIsNone(aligned[-1].values[name])
        self.assertIsNotNone(aligned[-1].values["tga"])

    def test_the_input_frame_is_not_changed(self):
        rows = panel(6)
        before = [dict(r.values) for r in rows]
        script.align_columns(rows, TARGET_ROW)
        self.assertEqual([dict(r.values) for r in rows], before)

    def test_a_column_the_frame_does_not_carry_is_refused(self):
        with self.assertRaises(ValueError):
            script.align_columns(panel(6), ("quarter_end", "no_such_column"))


class MainsFitIsTheDefectTests(NeedsExtra):
    """The control: `gbm_funding`'s fit as it stands on main trains the same columns one day off (#914). This is what the variants must not do."""

    def test_the_unaligned_one_step_fit_trains_every_target_row_column_from_row_p(self):
        rows = panel()
        names = TARGET_ROW + ("tga",)
        # the unaligned one-step fit trains each such column from row p; with the guard's refusal lifted (a stand-in entry) it does so on every pair
        entries = dict(one_step_guard.ONE_STEP_ALLOW_LIST)
        entries["stand_in"] = one_step_guard.FrozenDeclaration("fit_gradient_boosted_quantiles", names, "test stand-in")
        with mock.patch.object(one_step_guard, "ONE_STEP_ALLOW_LIST", entries), Recorded() as recorded:
            ml.fit_gradient_boosted_quantiles(rows, regressors=names, levels=script.GRID, minimum_history=20)
        design, targets, _ = recorded.calls[0]
        bad = offenders(design, targets, design_names(names), rows, TARGET_ROW, lambda name, j: j)
        self.assertEqual(len(bad), len(design) * len(TARGET_ROW), "main's one-step fit should be off by one day on every pair and column")

    def test_the_947_guard_refuses_that_fit_today(self):
        with self.assertRaises(ValueError):
            ml.fit_gradient_boosted_quantiles(panel(), regressors=TARGET_ROW + ("tga",), levels=script.GRID, minimum_history=20)


class OneStepVariantTests(NeedsExtra):
    """Run with `Admitted`: the #947 guard refuses a calendar regressor on any one-step fit, aligned or not, and its allow-list is Eleonora's."""

    def run(self, result=None):
        with Admitted():
            return super().run(result)

    def test_the_947_guard_refuses_this_variant_until_the_allow_list_admits_it(self):
        features = script.variant_features(script.ALIGNED, 2)
        with mock.patch.object(one_step_guard, "ONE_STEP_ALLOW_LIST", {}):
            with self.assertRaises(ValueError):
                script.variant_fit(script.ALIGNED, features)(panel(), 20)

    def test_every_calendar_and_scheduled_column_is_the_targets_at_every_lead(self):
        rows = panel()
        for h in script.HORIZONS:
            features = script.variant_features(script.ALIGNED, h)
            names = script.regressors(features)
            for column in script.target_row_columns(h):
                self.assertIn(column, names, f"lead {h} does not read {column}")
            fit = script.variant_fit(script.ALIGNED, features)
            with Recorded() as recorded:
                fit(rows, 20)
            design, targets, leaf = recorded.calls[0]
            self.assertEqual(leaf, script.LEAF)
            self.assertGreater(len(design), 50)
            # the fit's own order of columns is the order of `names`; the guard compares by value against the target row's
            bad = offenders(design, targets, design_names(names), rows, script.target_row_columns(h), lambda name, j: j)
            self.assertEqual(bad, [], f"lead {h}: {bad[:3]} are trained from row p, not the target row p + 1")

    def test_the_observed_columns_stay_the_origins_own_as_of_read(self):
        rows = panel()
        features = script.variant_features(script.ALIGNED, 3)
        names = tuple(script.regressors(features))
        with Recorded() as recorded:
            script.variant_fit(script.ALIGNED, features)(rows, 20)
        design, targets, _ = recorded.calls[0]
        observed = [c for c in OBSERVED if c in names]
        self.assertTrue(observed)
        self.assertEqual(offenders(design, targets, design_names(names), rows, observed, lambda name, j: j - 1), [])

    def test_the_fit_names_no_information_so_the_pairs_stay_one_step(self):
        import inspect

        fit = script.variant_fit(script.ALIGNED, script.variant_features(script.ALIGNED, 1))
        self.assertNotIn("information", inspect.signature(fit).parameters)


class DirectVariantTests(NeedsExtra):
    """No stand-in: the direct variant passes the #947 guard as it stands (a direct fit is not checked)."""

    def test_every_calendar_and_scheduled_column_is_the_targets_at_every_lead(self):
        from repo_model import measurement_fields

        with script._load("net_settlement").switched_on():
            self.check(measurement_fields.load_registry())

    def check(self, registry):
        rows = panel(ROWS)
        for h in script.HORIZONS:
            features = script.variant_features(script.DIRECT, h)
            rule = InformationRule(registry, tuple(features), decision_time=script.DECISION, horizon=h)
            fit = script.variant_fit(script.DIRECT, features)
            names = tuple(script.regressors(features))
            with Recorded() as recorded:
                fit(rows, minimum_history=20, information=rule)
            design, targets, leaf = recorded.calls[0]
            self.assertEqual(leaf, script.LEAF)
            self.assertGreater(len(design), 30)
            bad = offenders(design, targets, design_names(names), rows, script.target_row_columns(h), lambda name, j: j)
            self.assertEqual(bad, [], f"lead {h}: {bad[:3]}")


class LeadAvailabilityTests(unittest.TestCase):
    """The directive reads every column at every lead; the information set does not allow the scheduled settlement columns beyond lead 1."""

    def setUp(self):
        self.registry = json.loads(script.SOURCES.read_text(encoding="utf-8"))
        self.days = business_days(60)

    def info(self, column, h):
        rule = InformationRule(self.registry, (column, "tga", "spread_bps"), decision_time=script.DECISION, horizon=h)
        target = 40
        return rule, rule.information_set(self.days, target)

    def test_a_settlement_column_is_served_from_the_target_row_at_lead_1(self):
        rule, info = self.info("treasury_settlement", 1)
        rule.check(self.days, info)

    def test_a_settlement_column_is_refused_at_a_longer_lead(self):
        for h in (2, 5):
            rule, info = self.info("treasury_settlement", h)
            with self.assertRaises(LookAheadError):
                rule.check(self.days, info)
        self.assertNotIn("treasury_settlement", script.target_row_columns(2))

    def test_a_calendar_column_is_served_from_the_target_row_at_every_lead(self):
        for h in script.HORIZONS:
            rule, info = self.info("quarter_end", h)
            rule.check(self.days, info)
            self.assertIn("quarter_end", script.target_row_columns(h))


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))

    def test_the_declaration_names_exactly_two_variants(self):
        self.assertEqual(self.document["issue"], 1027)
        self.assertEqual(list(self.document["variants"]), [script.ALIGNED, script.DIRECT])

    def test_both_variants_read_the_same_inputs_at_every_lead(self):
        for h in script.HORIZONS:
            self.assertEqual(script.variant_features(script.ALIGNED, h), script.variant_features(script.DIRECT, h))

    def test_the_declared_target_row_columns_are_served_from_the_target_by_rule_2(self):
        served = script.served_columns()
        for column in script.TARGET_ROW_COLUMNS:
            self.assertIn(column, served, f"{column} is not served from the target row by asof.py rule 2")
        for column in script.OBSERVED_COLUMNS:
            self.assertNotIn(column, served)

    def test_the_committed_declaration_is_what_declare_writes(self):
        self.assertEqual(self.document, json.loads(json.dumps(script.declaration_document())))


if __name__ == "__main__":
    unittest.main()


class ScoredVariantsTests(unittest.TestCase):
    """Score what was walked: the aligned variant may be absent (refused by #947's guard), the direct one may not (Eleonora, 21 October 2026)."""

    def walks(self, names):
        import tempfile
        root = Path(tempfile.mkdtemp())
        for name in names:
            for h in script.HORIZONS:
                (root / f"{name}_h{h}.json").write_text("{}", encoding="utf-8")
        return root

    def test_both_walked_scores_both(self):
        scored, not_run = script.scored_variants(self.walks([script.ALIGNED, script.DIRECT]))
        self.assertEqual(scored, [script.ALIGNED, script.DIRECT])
        self.assertEqual(not_run, {})

    def test_the_aligned_variant_refused_by_the_guard_is_reported_not_run(self):
        scored, not_run = script.scored_variants(self.walks([script.DIRECT]))
        self.assertEqual(scored, [script.DIRECT])
        self.assertIn("947", not_run[script.ALIGNED])

    def test_the_direct_variant_missing_is_an_error(self):
        with self.assertRaises(ValueError):
            script.scored_variants(self.walks([script.ALIGNED]))

    def test_a_variant_with_some_leads_walked_is_an_error_not_a_silent_drop(self):
        root = self.walks([script.DIRECT])
        (root / f"{script.ALIGNED}_h1.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            script.scored_variants(root)
