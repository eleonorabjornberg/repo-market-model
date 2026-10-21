"""The balance-sheet flags re-dated onto the turn days, and nested into the calendar-aware candidate (#1031, H5 step 2 / H6 step 1).

What is under test, one class per directive criterion:

* criterion 1 and 2, `FlagDatesTests`: each relabelled flag is a function of the date and the market holiday table alone, pinned here by hand
  for a whole calendar year (2019), with the penultimate and run-up days returned to ordinary and 26 December flagged by no relabelled rule.
  The as-coded flags of `balance_sheet_days.flags` are unchanged ("no other change"). `RelabelledFlagsPublicTests` is the availability guard:
  a rule is used only from the day its source was public.
* criterion 2, `TargetRowTests`: the six columns are written about the target day, so they are declared in
  `target_day_columns.TARGET_DAY_COLUMNS` (a one-step fit on them is refused by #947's guard), `asof` rule 2 reads them from the scored row at
  every lead h = 1 to 5, and a direct-pairs fit trains them from the pair's target row.
* `DeclarationTests` / `ReadingTests`: the committed declaration is what `declare` writes, and the reading rule is the declared sentence.

Recorded mutations (CLAUDE.md; run on CPython 3.11 in `/opt/rmm-venv`, `-B`, applied by diff and reverted, control green before and after):

1. `balance_sheet_days.relabelled_flags`, the loop `for rule in RULES: require_public(rule, decision)` replaced by `pass`: killed by
   `RelabelledFlagsPublicTests.test_a_rule_is_not_used_before_its_source_was_public`, `AssertionError: LookAheadError not raised`.
2. `target_day_columns.TARGET_DAY_COLUMNS = CALENDAR_FEATURES | FOMC_TARGET_DAY_COLUMNS | BALANCE_SHEET_TARGET_DAY_COLUMNS` with the last operand
   dropped: killed by `TargetRowTests.test_a_one_step_fit_on_a_flag_column_is_refused`, `AssertionError: ValueError not raised`, and by
   `test_every_column_the_module_writes_is_declared`, `AssertionError: ... not found in frozenset`.
3. `balance_sheet_days.add_columns`, the call `compute(row.date, row.date)` changed to compute the flags of the day before the row (the one-row-off
   read of #914): killed by `ColumnTests.test_each_arm_writes_three_columns_from_its_own_flags`, `AssertionError: Lists differ: [0.0, 0.0, 0.0] != [1.0, 0.0, 1.0]`.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("balance_sheet_nested_1031_script", REPO / "scripts" / "balance_sheet_nested_1031.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import balance_sheet_days as bsd  # noqa: E402
from repo_model import contract, ml, one_step_guard, target_day_columns  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

D = date
#: 2019, by hand from the Federal Reserve / SIFMA calendar. 2018-12-31 and 2019-12-31 are Mondays/Tuesdays; 1 January is a holiday.
QUARTER_2019 = {D(2019, 1, 2), D(2019, 3, 29), D(2019, 4, 1), D(2019, 6, 28), D(2019, 7, 1), D(2019, 9, 30), D(2019, 10, 1), D(2019, 12, 31)}
MONTH_2019 = {
    D(2019, 1, 31), D(2019, 2, 1), D(2019, 2, 28), D(2019, 3, 1), D(2019, 4, 30), D(2019, 5, 1), D(2019, 5, 31), D(2019, 6, 3),
    D(2019, 7, 31), D(2019, 8, 1), D(2019, 8, 30), D(2019, 9, 3), D(2019, 10, 31), D(2019, 11, 1), D(2019, 11, 29), D(2019, 12, 2),
}
YEAR_2019 = {D(2019, 1, 2), D(2019, 12, 31)}
FLAG_DATES = {
    "foreign_bank_quarter_end": QUARTER_2019,
    "foreign_bank_month_end": MONTH_2019,
    "gsib_year_end": YEAR_2019,
}
DECISION = D(2019, 1, 1)


def year_days(year):
    day = D(year, 1, 1)
    while day.year == year:
        yield day
        day += timedelta(days=1)


class FlagDatesTests(unittest.TestCase):
    def test_each_relabelled_flag_fires_on_exactly_these_days_of_2019(self):
        for name, expected in FLAG_DATES.items():
            with self.subTest(flag=name):
                got = {day for day in year_days(2019) if bsd.relabelled_flags(day, DECISION)[name] == 1.0}
                self.assertEqual(got, expected)

    def test_the_penultimate_and_run_up_days_return_to_ordinary(self):
        # 2019-03-28 and 2019-03-27 were the as-coded run-up; 2019-12-30 the penultimate day of the year-end window
        for day in (D(2019, 3, 27), D(2019, 3, 28), D(2019, 12, 30), D(2019, 1, 30)):
            self.assertEqual(set(bsd.relabelled_flags(day, DECISION).values()), {0.0}, day)
        self.assertEqual(bsd.flags(D(2019, 3, 28), DECISION)["foreign_bank_quarter_end"], 1.0)

    def test_26_december_is_flagged_by_no_relabelled_rule_and_was_by_the_gsib_window(self):
        self.assertEqual(set(bsd.relabelled_flags(D(2019, 12, 26), DECISION).values()), {0.0})
        self.assertEqual(bsd.flags(D(2019, 12, 26), DECISION)["gsib_year_end"], 1.0)

    def test_the_first_business_day_after_rolls_over_a_holiday(self):
        # 2019-08-31 is a Saturday and 2019-09-02 Labor Day: the turn is 30 August and 3 September
        self.assertEqual(bsd.relabelled_flags(D(2019, 9, 3), DECISION)["foreign_bank_month_end"], 1.0)
        self.assertEqual(bsd.relabelled_flags(D(2019, 9, 2), DECISION)["foreign_bank_month_end"], 0.0)
        # 2020-01-01 is a holiday: the year-end turn's second day is 2020-01-02
        got = bsd.relabelled_flags(D(2020, 1, 2), DECISION)
        self.assertEqual((got["gsib_year_end"], got["foreign_bank_quarter_end"]), (1.0, 1.0))

    def test_december_is_its_own_type_beside_the_quarter_flag(self):
        got = bsd.relabelled_flags(D(2019, 12, 31), DECISION)
        self.assertEqual((got["gsib_year_end"], got["foreign_bank_quarter_end"], got["foreign_bank_month_end"]), (1.0, 1.0, 0.0))
        got = bsd.relabelled_flags(D(2019, 6, 28), DECISION)
        self.assertEqual((got["gsib_year_end"], got["foreign_bank_quarter_end"]), (0.0, 1.0))

    def test_a_flag_is_a_function_of_the_date_alone(self):
        """Not of the decision day (any decision after the sources were public), the panel or the other days."""
        for day in (D(2019, 3, 29), D(2019, 6, 3), D(2019, 7, 15)):
            first = bsd.relabelled_flags(day, D(2019, 1, 1))
            self.assertEqual(first, bsd.relabelled_flags(day, D(2026, 1, 1)))
            self.assertEqual(first, bsd.relabelled_flags(day, day))

    def test_the_as_coded_flags_are_unchanged(self):
        """'With no other change': the three as-coded rules of #427 give what they gave."""
        expected = {
            D(2019, 3, 27): (1.0, 0.0, 0.0), D(2019, 3, 29): (1.0, 0.0, 0.0), D(2019, 4, 1): (0.0, 0.0, 0.0),
            D(2019, 1, 31): (0.0, 1.0, 0.0), D(2019, 2, 1): (0.0, 0.0, 0.0),
            D(2019, 12, 24): (0.0, 0.0, 1.0), D(2019, 12, 26): (0.0, 0.0, 1.0), D(2019, 12, 27): (1.0, 0.0, 1.0), D(2019, 12, 31): (1.0, 0.0, 1.0),
            D(2020, 1, 2): (0.0, 0.0, 0.0),
        }
        for day, want in expected.items():
            got = bsd.flags(day, DECISION)
            self.assertEqual(tuple(got[name] for name in bsd.NAMES), want, day)
        self.assertEqual(bsd.NAMES, tuple(rule.name for rule in bsd.RULES))
        self.assertEqual((bsd.RUN_UP_DAYS, bsd.YEAR_END_DAYS), (3, 5))


class RelabelledFlagsPublicTests(unittest.TestCase):
    def test_a_rule_is_not_used_before_its_source_was_public(self):
        with self.assertRaises(LookAheadError):
            bsd.relabelled_flags(D(2018, 9, 28), D(2015, 8, 13))
        bsd.relabelled_flags(D(2018, 9, 28), D(2015, 8, 14))


def panel_rows(count=90, start=D(2024, 1, 2)):
    """Weekday rows whose every non-flag column is unique to its row; the spread is 1000 + the row."""

    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    columns = ["quarter_end", "days_to_month_end", "tax_date", "treasury_settlement", "treasury_settlement_coupons", "treasury_settlement_bills",
               "net_settlement", "net_settlement_due_5d", "tga"]
    for h in script.HORIZONS:
        columns += [c for c in script.a1027.regressors(script.a1027.variant_features(script.BASE, h)) if c not in columns]
    rows = []
    for i, when in enumerate(days):
        values = {"sofr": 15.0 + i / 100.0, "iorb": 5.0}
        for k, name in enumerate(columns):
            values[name] = float(10_000 * (k + 1) + i)
        rows.append(DailyObservation(date=when, values=values))
    return rows


REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"


class NeedsExtra(unittest.TestCase):
    def setUp(self):
        if all(importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn")):
            return
        if os.environ.get(REQUIRE_ML):
            self.fail(f"{REQUIRE_ML} is set but the optional 'ml' extra is not importable")
        self.skipTest("the optional 'ml' extra is not installed")


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


class ColumnTests(unittest.TestCase):
    def test_each_arm_writes_three_columns_from_its_own_flags(self):
        self.assertEqual(len(script.arm_columns(script.CODED)), 3)
        self.assertEqual(len(script.arm_columns(script.TURN)), 3)
        self.assertFalse(set(script.arm_columns(script.CODED)) & set(script.arm_columns(script.TURN)))
        rows = script.with_flags(panel_rows(), script.TURN)
        for row in rows:
            want = bsd.relabelled_flags(row.date, row.date)
            self.assertEqual([row.values[c] for c in script.arm_columns(script.TURN)], [want[n] for n in bsd.NAMES])
        coded = script.with_flags(panel_rows(), script.CODED)
        for row in coded:
            want = bsd.flags(row.date, row.date)
            self.assertEqual([row.values[c] for c in script.arm_columns(script.CODED)], [want[n] for n in bsd.NAMES])

    def test_a_flag_does_not_depend_on_which_other_rows_are_in_the_frame(self):
        rows = panel_rows()
        whole = {r.date: tuple(r.values[c] for c in script.arm_columns(script.TURN)) for r in script.with_flags(rows, script.TURN)}
        part = {r.date: tuple(r.values[c] for c in script.arm_columns(script.TURN)) for r in script.with_flags(rows[17:41], script.TURN)}
        for day, values in part.items():
            self.assertEqual(values, whole[day])

    def test_no_other_value_of_a_row_moves(self):
        rows = panel_rows(20)
        out = script.with_flags(rows, script.TURN)
        for before, after in zip(rows, out):
            self.assertEqual(before.date, after.date)
            self.assertEqual({k: v for k, v in after.values.items() if k not in script.arm_columns(script.TURN)}, before.values)

    def test_an_arm_that_is_not_declared_is_refused(self):
        with self.assertRaises(ValueError):
            script.arm_columns("gbm_funding")


class TargetRowTests(NeedsExtra):
    def test_every_column_the_module_writes_is_declared(self):
        written = set()
        for arm in script.ARMS:
            written |= {name for row in script.with_flags(panel_rows(5), arm) for name in row.values} - {name for row in panel_rows(5) for name in row.values}
        self.assertEqual(written, set(bsd.CODED_COLUMNS) | set(bsd.TURN_COLUMNS))
        for name in written:
            self.assertIn(name, target_day_columns.TARGET_DAY_COLUMNS)
        self.assertLessEqual(contract.CALENDAR_FEATURES, target_day_columns.TARGET_DAY_COLUMNS)

    def test_a_one_step_fit_on_a_flag_column_is_refused(self):
        for arm in script.ARMS:
            for column in script.arm_columns(arm):
                with self.subTest(column=column):
                    with self.assertRaisesRegex(ValueError, rf"{column}.*direct.*drop"):
                        ml.fit_gradient_boosted_quantiles(script.with_flags(panel_rows(), arm), ["tga", column], minimum_history=20)

    def test_rule_2_reads_every_flag_from_the_scored_row_at_every_lead(self):
        rows = panel_rows(60)
        days = [r.date for r in rows]
        for arm in script.ARMS:
            for h in script.HORIZONS:
                features = script.arm_features(arm, h)
                with script.switched(arm):
                    rule = InformationRule(script.registry(), tuple(features), decision_time=script.DECISION, horizon=h)
                    info = rule.information_set(days, 40)
                    rule.check(days, info)
                    reads = {read.feature: read for read in info.reads}
                    for column in script.arm_columns(arm):
                        self.assertEqual(reads[column].kind, "calendar", (arm, h, column))
                        self.assertEqual(reads[column].row, 40, (arm, h, column))
                        self.assertEqual(reads[column].rows, 0)

    def test_the_fit_trains_every_flag_from_the_pairs_target_row(self):
        """Every direct pair's flags are the flags of its target day; a fit that read the day before would differ on the turn's edges."""
        for arm in script.ARMS:
            rows = script.with_flags(panel_rows(), arm)
            columns = script.arm_columns(arm)
            by_spread = {1000 + i: i for i in range(len(rows))}
            for h in script.HORIZONS:
                features = script.arm_features(arm, h)
                names = ("spread_bps",) + tuple(script.a1027.regressors(features))
                with script.switched(arm), Recorded() as recorded:
                    rule = InformationRule(script.registry(), tuple(features), decision_time=script.DECISION, horizon=h)
                    script.arm_fit(arm, features)(rows, minimum_history=20, information=rule)
                design, targets, leaf = recorded.calls[0]
                self.assertEqual(leaf, script.a1027.LEAF)
                bad, moved = [], 0
                for line, target in zip(design, targets):
                    j = by_spread[int(round(target))]
                    for column in columns:
                        value = line[names.index(column)]
                        if value != rows[j].values[column]:
                            bad.append((arm, h, column, j, value, rows[j].values[column]))
                        if rows[j].values[column] != rows[j - 1].values[column]:
                            moved += 1
                self.assertEqual(bad, [])
                self.assertGreater(moved, 0, "no pair would tell a target-row read from a read one row early")


class ArmTests(unittest.TestCase):
    def test_both_arms_nest_the_1027_direct_candidate_and_add_only_their_three_columns(self):
        for h in script.HORIZONS:
            base = script.a1027.variant_features(script.BASE, h)
            for arm in script.ARMS:
                self.assertEqual(script.arm_features(arm, h), base + script.arm_columns(arm))

    def test_the_base_is_the_direct_variant_that_passes_the_947_guard(self):
        self.assertEqual(script.BASE, script.a1027.DIRECT)
        self.assertNotIn(script.BASE, [name for name in one_step_guard.ONE_STEP_ALLOW_LIST])

    def test_an_arm_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.a1027.require_study_window([date(2026, 1, 2)])


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))

    def test_the_committed_declaration_is_what_declare_writes(self):
        self.assertEqual(self.document, json.loads(json.dumps(script.declaration_document())))

    def test_the_declaration_names_two_arms_and_leaves_the_relabel_unadopted(self):
        self.assertEqual(self.document["issue"], 1031)
        self.assertEqual(list(self.document["arms"]), list(script.ARMS))
        self.assertIn("not adopted", self.document["adoption"])

    def test_the_declared_columns_are_the_modules(self):
        self.assertEqual(self.document["arms"][script.CODED]["columns"], list(bsd.CODED_COLUMNS))
        self.assertEqual(self.document["arms"][script.TURN]["columns"], list(bsd.TURN_COLUMNS))


class ReadingTests(unittest.TestCase):
    def row(self, skill, low, high):
        return {"skill": skill, "skill_interval": [low, high]}

    def test_an_arm_that_beats_its_base_on_its_flagged_days_and_does_not_lose_elsewhere_is_so_read(self):
        cells = {script.TURN: {"flagged": self.row(0.04, 0.01, 0.07), "unflagged": self.row(-0.01, -0.03, 0.01)}}
        text = script.reading_rules(cells)[0]
        self.assertIn("beats", text)
        self.assertNotIn("is not shown to beat", text)
        self.assertIn("does not lose", text)

    def test_a_lower_bound_at_zero_is_not_a_beat_and_an_interval_wholly_below_zero_is_a_loss(self):
        cells = {script.CODED: {"flagged": self.row(0.04, 0.0, 0.07), "unflagged": self.row(-0.05, -0.08, -0.01)}}
        text = script.reading_rules(cells)[0]
        self.assertIn("is not shown to beat", text)
        self.assertIn("loses", text)
        self.assertNotIn("does not lose", text)

    def test_an_undefined_or_unscored_cut_is_not_read(self):
        cells = {script.TURN: {"flagged": {"undefined": "no variance"}, "unflagged": None}}
        self.assertIn("not read", script.reading_rules(cells)[0])


class GroupTests(unittest.TestCase):
    def test_the_day_groups_are_the_declared_ones_and_overlap_as_declared(self):
        days = [D(2019, 3, 27), D(2019, 3, 28), D(2019, 3, 29), D(2019, 4, 1), D(2019, 4, 2), D(2019, 12, 24), D(2019, 12, 26), D(2019, 12, 31), D(2020, 1, 2)]
        got = script.day_flags(days)
        self.assertEqual({d for d in days if got[d]["turn_days"]}, {D(2019, 3, 29), D(2019, 4, 1), D(2019, 12, 31), D(2020, 1, 2)})
        self.assertEqual({d for d in days if got[d]["coded_days"]}, {D(2019, 3, 27), D(2019, 3, 28), D(2019, 3, 29), D(2019, 12, 24), D(2019, 12, 26), D(2019, 12, 31)})
        self.assertEqual({d for d in days if got[d]["unflagged"]}, {D(2019, 4, 2)})
        self.assertEqual({d for d in days if got[d]["december_26"]}, {D(2019, 12, 26)})
        self.assertEqual({d for d in days if got[d]["penultimate"]}, {D(2019, 3, 28)})


if __name__ == "__main__":
    unittest.main()
