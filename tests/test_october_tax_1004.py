"""The 15 October tax-date column and its two arms (`scripts/october_tax_1004.py`, #1095, finding #1004; H5 step 3, calendar first).

Eleonora's ruling on #1004 (20 October 2026, corrected): the October label is deferred, not rejected, and is tested again with a candidate that reads
calendar days at the target day. The property under test is the directive's third criterion: `tax_date_october` is read at the target row at every lead
h = 1 to 5 (a calendar column, served by `asof` rule 2 from the scored row), a direct pair trains it from the pair's own target row, and the one-step guard
(#947) refuses it on any one-step fit that the allow-list does not admit. The column is a function of the row's own date and the market holiday table.

Recorded mutations (each applied in the working tree, confirmed by `git diff`, restored from the index before the next; Python 3.11.17, numpy 2.4.6, scikit-learn 1.9.1):

* `target_day_columns`, the line `TARGET_DAY_COLUMNS = ... | BALANCE_SHEET_TARGET_DAY_COLUMNS | OCTOBER_TAX_TARGET_DAY_COLUMNS` changed to drop the last term (the
  one-step guard no longer knows the column is written about the target day): `TargetDayColumnTests.test_a_one_step_fit_on_the_column_is_refused` fails with
  `AssertionError` (`{} != {'tax_date_october': "calendar column 'tax_date_october'"}`), `test_the_column_is_declared_as_written_about_the_target_day` and
  `test_every_column_the_module_writes_is_declared` with `AssertionError` (`'tax_date_october' not found in frozenset(...)`), and
  `test_a_one_step_fit_through_the_fitter_is_refused` with `KeyError` (`'sofr'`: the fit is no longer stopped by the guard and reaches the rows).
* `switched`, the line `calendar = contract.CALENDAR_FEATURES | frozenset((COLUMN,))` changed to `calendar = contract.CALENDAR_FEATURES` (the column is no longer
  served as a calendar column, so `asof` reads it as a source feature): `ReadAtTheTargetRowTests.test_the_column_is_served_from_the_target_row_at_every_lead` and
  `DirectArmTests.test_the_column_is_the_targets_at_every_lead` error with `KeyError` (`'tax_date_october'`: it names no source field), and
  `ReadAtTheTargetRowTests.test_the_switch_is_for_the_run_only` fails with `AssertionError`.
* `arm_fit`, in the aligned branch the line `fields = ac.TARGET_ROW_COLUMNS + (COLUMN,)` changed to `fields = ac.TARGET_ROW_COLUMNS` (the one-step arm would train the column
  from row p, the #914 class): `AlignedArmTests.test_the_column_and_the_target_row_columns_are_the_targets_when_admitted` fails with `AssertionError`
  (`Lists differ: [('tax_date_october', 1, 90000.0, 90001.0), ...] != []`: the design holds row p's value, 90000.0, where the target row's is 90001.0).
* No mutation is recorded for the study window: `require_study_window` is `aligned_calendar_1027`'s own guard and is mutated and tested there; this script adds no
  new window guard (`StudyWindowTests` pins that it uses that window).
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))


def load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


script = load("october_tax_1004")
ac = script.ac

from repo_model import contract, data, measurement_fields, one_step_guard, target_day_columns, tax_date_october as tdo  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402
from test_aligned_calendar_1027 import (  # noqa: E402
    NeedsExtra,
    Recorded,
    business_days,
    design_names,
    offenders,
    panel,
)

COLUMN = "tax_date_october"
ROWS = 90


def october_rows(*days):
    return [DailyObservation(day, {"x": float(i)}) for i, day in enumerate(days)]


class ColumnTests(unittest.TestCase):
    """`tax_date_october.add_columns`: 1.0 on the 15 October deadline (rolled off weekends and DC holidays) and the two market days after it."""

    def values(self, *days):
        return {row.date: row.values[COLUMN] for row in tdo.add_columns(october_rows(*days))}

    def test_the_window_is_the_rolled_deadline_and_the_two_market_days_after_it(self):
        got = self.values(
            date(2019, 10, 14), date(2019, 10, 15), date(2019, 10, 16), date(2019, 10, 17), date(2019, 10, 18),  # a Tuesday deadline
            date(2022, 10, 14), date(2022, 10, 17), date(2022, 10, 19), date(2022, 10, 20),  # 15 October 2022 is a Saturday: rolled to Monday 17
            date(2023, 10, 13), date(2023, 10, 16), date(2023, 10, 18), date(2023, 10, 19),  # a Sunday: rolled to Monday 16
            date(2021, 10, 15), date(2021, 10, 18), date(2021, 10, 19), date(2021, 10, 20),  # a Friday: the window crosses the weekend
        )
        window = {
            date(2019, 10, 15), date(2019, 10, 16), date(2019, 10, 17), date(2022, 10, 17), date(2022, 10, 19), date(2023, 10, 16),
            date(2023, 10, 18), date(2021, 10, 15), date(2021, 10, 18), date(2021, 10, 19),
        }
        self.assertEqual({day for day, value in got.items() if value == 1.0}, window)
        self.assertEqual({value for value in got.values()}, {0.0, 1.0})

    def test_every_day_outside_october_is_zero_and_the_published_tax_date_is_unchanged(self):
        for day in (date(2019, 9, 16), date(2019, 11, 15), date(2019, 12, 16), date(2020, 4, 15), date(2024, 6, 17)):
            self.assertEqual(self.values(day)[day], 0.0)
        self.assertEqual(data.tax_date(date(2019, 10, 15)), 0.0, "the published column does not mark 15 October")
        self.assertEqual(data.tax_date(date(2019, 9, 16)), 1.0)

    def test_the_rows_dates_and_other_values_are_unchanged_and_the_input_is_not_mutated(self):
        rows = october_rows(date(2019, 10, 15), date(2019, 10, 18))
        out = tdo.add_columns(rows)
        self.assertEqual([r.date for r in out], [r.date for r in rows])
        self.assertEqual([r.values["x"] for r in out], [0.0, 1.0])
        self.assertEqual([set(r.values) for r in rows], [{"x"}, {"x"}])

    def test_a_row_reads_nothing_from_the_rows_around_it(self):
        days = [date(2019, 10, 11), date(2019, 10, 15), date(2019, 10, 16), date(2019, 10, 18)]
        whole = [r.values[COLUMN] for r in tdo.add_columns(october_rows(*days))]
        alone = [tdo.add_columns(october_rows(day))[0].values[COLUMN] for day in days]
        self.assertEqual(whole, alone)

    def test_a_row_that_already_has_the_column_is_refused(self):
        with self.assertRaises(ValueError):
            tdo.add_columns(tdo.add_columns(october_rows(date(2019, 10, 15))))

    def test_the_column_name_is_the_one_the_study_reads(self):
        self.assertEqual(tdo.COLUMN, COLUMN)
        self.assertEqual(script.COLUMN, COLUMN)


class TargetDayColumnTests(unittest.TestCase):
    """The column is written about the target day, so the shared declaration lists it and the one-step guard refuses it."""

    def test_the_column_is_declared_as_written_about_the_target_day(self):
        self.assertIn(COLUMN, target_day_columns.OCTOBER_TAX_TARGET_DAY_COLUMNS)
        self.assertIn(COLUMN, target_day_columns.TARGET_DAY_COLUMNS)

    def test_every_column_the_module_writes_is_declared(self):
        before = october_rows(date(2019, 10, 15))
        written = {name for row in tdo.add_columns(before) for name in row.values} - {name for row in before for name in row.values}
        self.assertEqual(written, {COLUMN})
        self.assertLessEqual(written, target_day_columns.TARGET_DAY_COLUMNS)

    def test_a_one_step_fit_on_the_column_is_refused(self):
        self.assertEqual(one_step_guard.one_step_refusals((COLUMN,)), {COLUMN: f"calendar column {COLUMN!r}"})
        with self.assertRaisesRegex(ValueError, COLUMN):
            one_step_guard.check_one_step_regressors("fit_gradient_boosted_quantiles", ("sofr_volume", COLUMN))

    def test_the_published_calendar_features_do_not_gain_the_column(self):
        self.assertNotIn(COLUMN, contract.CALENDAR_FEATURES)

    def test_a_one_step_fit_through_the_fitter_is_refused(self):
        """The real fitter, not the helper: `ml.fit_gradient_boosted_quantiles` on one-step pairs raises before the estimator is built. The direct fit is `DirectArmTests`."""
        from repo_model import ml

        rows = tdo.add_columns([DailyObservation(day, {"sofr_volume": float(i), "spread_bps": float(i % 7)}) for i, day in enumerate(business_days(60))])
        with self.assertRaisesRegex(ValueError, rf"{COLUMN}.*direct.*drop"):
            ml.fit_gradient_boosted_quantiles(rows, ["sofr_volume", COLUMN], minimum_history=20)


class FeatureTests(unittest.TestCase):
    def test_each_arm_is_its_1027_variant_plus_the_column_and_nothing_else(self):
        for arm, base in script.BASE.items():
            for h in ac.HORIZONS:
                features = script.arm_features(arm, h)
                self.assertEqual(features[:-1], ac.variant_features(base, h))
                self.assertEqual(features[-1], COLUMN)
                self.assertEqual(len(features), len(set(features)))

    def test_the_arms_are_the_two_1027_variants_with_the_column(self):
        self.assertEqual(script.BASE, {script.DIRECT_OCTOBER: ac.DIRECT, script.ALIGNED_OCTOBER: ac.ALIGNED})
        self.assertEqual(script.ARMS, (script.DIRECT_OCTOBER, script.ALIGNED_OCTOBER))

    def test_an_unknown_arm_is_refused(self):
        with self.assertRaises(ValueError):
            script.arm_features("gbm_funding", 1)


class ReadAtTheTargetRowTests(unittest.TestCase):
    def setUp(self):
        self.registry = measurement_fields.load_registry()
        self.days = business_days(80)

    def test_the_column_is_served_from_the_target_row_at_every_lead(self):
        for h in ac.HORIZONS:
            with script.switched():
                rule = InformationRule(self.registry, (COLUMN, "tga", "spread_bps"), decision_time=ac.DECISION, horizon=h)
                info = rule.information_set(self.days, 60)
                rule.check(self.days, info)
            reads = {read.feature: read for read in info.reads}
            self.assertEqual(reads[COLUMN].kind, "calendar")
            self.assertEqual(reads[COLUMN].row, 60, f"lead {h}: served from the target row")

    def test_the_switch_is_for_the_run_only(self):
        before = contract.CALENDAR_FEATURES
        with script.switched():
            self.assertIn(COLUMN, contract.CALENDAR_FEATURES)
        self.assertIs(contract.CALENDAR_FEATURES, before)
        self.assertNotIn(COLUMN, contract.CALENDAR_FEATURES)

    def test_a_study_row_dated_in_october_carries_the_flag_on_its_own_date(self):
        rows = tdo.add_columns([DailyObservation(day, {}) for day in (date(2024, 10, 14), date(2024, 10, 15), date(2024, 10, 18))])
        self.assertEqual([r.values[COLUMN] for r in rows], [0.0, 1.0, 0.0])


def design_frame(count=ROWS):
    """`panel()`'s unique-per-row columns, plus the October column with a value unique to each row (so a pair's cell names the row it came from)."""

    return [DailyObservation(r.date, {**r.values, COLUMN: float(90_000 + i)}) for i, r in enumerate(panel(count))]


class DirectArmTests(NeedsExtra):
    """No stand-in: the direct arm passes the #947 guard as it stands (a direct fit is not checked)."""

    def test_the_column_is_the_targets_at_every_lead(self):
        frame = design_frame()
        for h in ac.HORIZONS:
            features = script.arm_features(script.DIRECT_OCTOBER, h)
            registry = measurement_fields.load_registry()
            with ac._load("net_settlement").switched_on(), script.switched():
                rule = InformationRule(registry, tuple(features), decision_time=ac.DECISION, horizon=h)
                fit = script.arm_fit(script.DIRECT_OCTOBER, features)
                with Recorded() as recorded:
                    fit(frame, minimum_history=20, information=rule)
            design, targets, leaf = recorded.calls[0]
            self.assertEqual(leaf, ac.LEAF)
            self.assertGreater(len(design), 30)
            names = tuple(ac.regressors(features))
            columns = ac.target_row_columns(h) + (COLUMN,)
            bad = offenders(design, targets, design_names(names), frame, columns, lambda name, j: j)
            self.assertEqual(bad, [], f"lead {h}: {bad[:3]}")

    def test_the_direct_arm_names_direct_pairs_and_the_leaf_of_its_variant(self):
        fit = script.arm_fit(script.DIRECT_OCTOBER, script.arm_features(script.DIRECT_OCTOBER, 1))
        self.assertEqual(fit.keywords["training_pairs"], "direct")
        self.assertEqual(fit.keywords["min_samples_leaf"], ac.LEAF)


class AlignedArmTests(NeedsExtra):
    def stand_in(self):
        entries = dict(one_step_guard.ONE_STEP_ALLOW_LIST)
        for h in ac.HORIZONS:
            names = tuple(ac.regressors(script.arm_features(script.ALIGNED_OCTOBER, h)))
            entries[f"stand_in_{h}"] = one_step_guard.FrozenDeclaration("fit_gradient_boosted_quantiles", names, "test stand-in")
        return mock.patch.object(one_step_guard, "ONE_STEP_ALLOW_LIST", entries)

    def test_the_guard_refuses_the_aligned_arm_until_the_allow_list_admits_it(self):
        features = script.arm_features(script.ALIGNED_OCTOBER, 2)
        with self.assertRaises(ValueError):
            script.arm_fit(script.ALIGNED_OCTOBER, features)(design_frame(), 20)
        listed = {entry.regressors for entry in one_step_guard.ONE_STEP_ALLOW_LIST.values()}
        self.assertNotIn(tuple(ac.regressors(features)), listed, "the aligned arm is admitted only by her entry; none is added here")

    def test_the_walk_refuses_before_any_work_and_says_whose_decision_it_is(self):
        with self.assertRaises(SystemExit) as raised:
            script.require_admitted(script.ALIGNED_OCTOBER, 2)
        self.assertIn("allow-list", str(raised.exception))
        script.require_admitted(script.DIRECT_OCTOBER, 2)

    def test_the_column_and_the_target_row_columns_are_the_targets_when_admitted(self):
        frame = design_frame()
        with self.stand_in():
            for h in ac.HORIZONS:
                features = script.arm_features(script.ALIGNED_OCTOBER, h)
                names = tuple(ac.regressors(features))
                with Recorded() as recorded:
                    script.arm_fit(script.ALIGNED_OCTOBER, features)(frame, 20)
                design, targets, leaf = recorded.calls[0]
                self.assertEqual(leaf, ac.LEAF)
                columns = tuple(ac.target_row_columns(h)) + (COLUMN,)
                bad = offenders(design, targets, design_names(names), frame, columns, lambda name, j: j)
                self.assertEqual(bad, [], f"lead {h}: {bad[:3]} are trained from row p, not the target row p + 1")

    def test_an_unaligned_frame_is_refused_before_the_fit(self):
        with self.stand_in():
            fit = script.arm_fit(script.ALIGNED_OCTOBER, script.arm_features(script.ALIGNED_OCTOBER, 2))
            with mock.patch.object(ac, "align_columns", lambda frame, fields=ac.TARGET_ROW_COLUMNS: list(frame)):
                with self.assertRaises(ValueError):
                    fit(design_frame(), 20)

    def test_the_fit_names_no_information_so_the_pairs_stay_one_step(self):
        fit = script.arm_fit(script.ALIGNED_OCTOBER, script.arm_features(script.ALIGNED_OCTOBER, 1))
        self.assertNotIn("information", inspect.signature(fit).parameters)


class ScoredArmsTests(unittest.TestCase):
    """The aligned arm runs only if she admits it: absent, it is reported not run. The direct arm must be there."""

    def walks(self, names):
        import tempfile

        root = Path(tempfile.mkdtemp())
        for name in names:
            for h in ac.HORIZONS:
                (root / f"{name}_h{h}.json").write_text("{}", encoding="utf-8")
        return root

    def test_both_walked_scores_both(self):
        scored, not_run = script.scored_arms(self.walks([script.DIRECT_OCTOBER, script.ALIGNED_OCTOBER]))
        self.assertEqual(scored, [script.DIRECT_OCTOBER, script.ALIGNED_OCTOBER])
        self.assertEqual(not_run, {})

    def test_the_aligned_arm_not_admitted_is_reported_not_run_with_the_reason(self):
        scored, not_run = script.scored_arms(self.walks([script.DIRECT_OCTOBER]))
        self.assertEqual(scored, [script.DIRECT_OCTOBER])
        self.assertIn("allow-list", not_run[script.ALIGNED_OCTOBER])

    def test_the_direct_arm_missing_is_an_error(self):
        with self.assertRaises(ValueError):
            script.scored_arms(self.walks([script.ALIGNED_OCTOBER]))

    def test_an_arm_with_some_leads_walked_is_an_error_not_a_silent_drop(self):
        root = self.walks([script.DIRECT_OCTOBER])
        (root / f"{script.ALIGNED_OCTOBER}_h1.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            script.scored_arms(root)


class CutTests(unittest.TestCase):
    """The October cuts label target days after the fact, for scoring only: never an input."""

    def targets(self):
        out = []
        for year in range(2018, 2026):
            out += [d for d in (date(year, 10, n) for n in range(10, 24)) if d.weekday() < 5]
        return out + [date(2026, 2, 3), date(2025, 12, 30)]

    def test_the_window_cut_is_every_year_and_the_reading_without_2019_and_2025_drops_exactly_those(self):
        cuts = script.october_cuts(self.targets())
        self.assertEqual(len(cuts["october_window"]), 24)
        self.assertEqual({d.year for d in cuts["october_window"]}, set(range(2018, 2026)))
        self.assertEqual({d.year for d in cuts["october_without_2019_2025"]}, {2018, 2020, 2021, 2022, 2023, 2024})
        self.assertEqual(len(cuts["october_without_2019_2025"]), 18)
        self.assertTrue(set(cuts["october_without_2019_2025"]) <= set(cuts["october_window"]))
        self.assertEqual(set(script.LEFT_OUT_YEARS), {2019, 2025})

    def test_the_outside_cut_is_every_ordinary_day_not_in_the_window(self):
        types = {date(2019, 10, 15): "ordinary", date(2019, 10, 22): "ordinary", date(2019, 11, 4): "ordinary", date(2019, 11, 15): "tax_date"}
        cuts = script.october_cuts(sorted(types), types)
        self.assertEqual(cuts["ordinary_outside_october"], [date(2019, 10, 22), date(2019, 11, 4)])

    def test_the_2026_reading_is_empty_on_this_panel_and_says_why(self):
        scored = [d for d in self.targets() if d.year < 2026]
        reading = script.reading_2026(scored)
        self.assertEqual(reading["october_window_days"], 0)
        self.assertEqual(reading["scored_open_2026_days"], 0)
        self.assertEqual(reading["october_2026_window"], ["2026-10-15", "2026-10-16", "2026-10-19"])
        self.assertEqual(reading["open_2026_days"], ["2026-01-01", "2026-09-03"])
        self.assertIn("blind", reading["why"])
        # an open 2026 day among the scored targets is counted, and none of them is in an October window
        counted = script.reading_2026(self.targets())
        self.assertEqual((counted["scored_open_2026_days"], counted["october_window_days"]), (1, 0))

    def test_a_2026_day_in_the_scored_targets_is_refused_by_the_study_window(self):
        with self.assertRaises(LookAheadError):
            ac.require_study_window([date(2026, 1, 2)])


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))

    def test_the_declaration_names_exactly_two_arms_on_the_1027_variants(self):
        self.assertEqual(self.document["issue"], 1095)
        self.assertEqual(sorted(self.document["arms"]), sorted([script.DIRECT_OCTOBER, script.ALIGNED_OCTOBER]))
        self.assertEqual({a: v["base"] for a, v in self.document["arms"].items()}, script.BASE)

    def test_the_committed_declaration_is_what_declare_writes(self):
        self.assertEqual(self.document, json.loads(json.dumps(script.declaration_document())))

    def test_the_declaration_keeps_the_study_window_the_lockbox_and_what_it_leaves_unchanged(self):
        self.assertIn("no day after 2025-12-31", self.document["limits"])
        self.assertIn("no lockbox day", self.document["limits"])
        self.assertEqual(script.LAST_TARGET, date(2025, 12, 31))
        unchanged = " ".join(self.document["limits"])
        for name in ("tax_date", "B2", "every existing declaration"):
            self.assertIn(name, unchanged)

    def test_the_declared_comparisons_include_the_three_benchmarks(self):
        text = json.dumps(self.document["comparisons"])
        for name in ("B1", "B2", "B3", "without the column"):
            self.assertIn(name, text)

    def test_the_october_cuts_are_declared_both_ways(self):
        cuts = self.document["cuts"]
        self.assertIn("october_without_2019_2025", cuts)
        self.assertIn("october_2026", cuts)


class ReadingRuleTests(unittest.TestCase):
    def row(self, difference, low, high, skill=0.0, skill_low=-0.1, skill_high=0.1):
        return {"difference": difference, "difference_interval": [low, high], "skill": skill, "skill_interval": [skill_low, skill_high], "days": 18}

    def test_helps_needs_the_lower_end_of_the_mean_difference_above_zero_and_loses_needs_the_upper_end_below_zero(self):
        rows = {
            script.DIRECT_OCTOBER: {"october_without_2019_2025": self.row(0.3, 0.1, 0.5), "ordinary_outside_october": self.row(-0.01, -0.03, 0.01)},
            script.ALIGNED_OCTOBER: {"october_without_2019_2025": self.row(0.3, -0.1, 0.7), "ordinary_outside_october": self.row(-0.05, -0.09, -0.01)},
        }
        direct, aligned = script.reading_rules(rows)
        self.assertIn("gbm_funding_cal_direct_october helps over gbm_funding_cal_direct in the October window without 2019 and 2025", direct)
        self.assertIn("does not lose", direct)
        self.assertIn("gbm_funding_cal_aligned_october is not shown to help", aligned)
        self.assertIn("and loses outside October", aligned)

    def test_an_unscored_or_undefined_cut_is_not_read(self):
        rows = {script.DIRECT_OCTOBER: {"october_without_2019_2025": {"undefined": "x"}, "ordinary_outside_october": self.row(0.0, -0.1, 0.1)}}
        self.assertIn("not read (x)", script.reading_rules(rows)[0], "the scorer's reason is carried to the page")
        self.assertIn("not read", script.reading_rules({script.DIRECT_OCTOBER: {}})[0])

    def test_days_differing_counts_the_days_the_column_can_have_mattered_on(self):
        a, b, c = date(2019, 10, 15), date(2019, 10, 16), date(2019, 10, 17)
        self.assertEqual(script.days_differing({a: 1.0, b: 2.0, c: 3.0}, {a: 1.0, b: 2.5, c: 3.0}, [a, b, c]), 1)
        self.assertEqual(script.days_differing({a: 1.0}, {a: 1.0}, [a]), 0)


class FiveLevelTests(unittest.TestCase):
    def test_the_b3_levels_are_the_incumbents_and_all_on_the_grid(self):
        levels = script.b3_levels()
        self.assertEqual(levels, (0.05, 0.25, 0.5, 0.75, 0.95))

    def test_a_23_level_forecast_is_read_at_the_five_levels_for_b3(self):
        quantiles = [float(i) for i in range(23)]
        five = script.at_b3_levels(quantiles)
        self.assertEqual(len(five), 5)
        self.assertEqual(five, [quantiles[ac.GRID.index(level)] for level in (0.05, 0.25, 0.5, 0.75, 0.95)])


class StudyWindowTests(unittest.TestCase):
    def test_the_script_uses_the_1027_window_and_refuses_a_later_day(self):
        self.assertIs(script.LAST_TARGET, ac.LAST_TARGET)
        with self.assertRaises(LookAheadError):
            ac.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])


if __name__ == "__main__":
    unittest.main()
