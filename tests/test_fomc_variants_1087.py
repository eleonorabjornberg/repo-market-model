"""The FOMC-column arms of the #1027 variants (`scripts/fomc_variants_1087.py`, #1087, H5 step 3, calendar first).

The directive's second criterion: the columns `fomc_meeting_day` and `fomc_days_to_next_meeting` are read at the target day, a scheduled meeting
public from its release instant. Three things carry that here, and each is tested:

1. `with_fomc(rows, h)` writes row T's columns as read at the decision instant of the panel day h rows before T (the lead's own), through
   `fomc_calendar.add_columns`, so a schedule released between two leads' decision instants is seen by the later lead only.
2. `fomc_registry(h)` declares the source as a scheduled field `h` panel days ahead (`asof` rule 2), so `InformationRule` serves the columns from the
   target row and its `check` raises `LookAheadError` for a declaration that claims earlier availability than the lead's decision allows.
3. The direct arm trains every pair's FOMC columns from the pair's target row, and the aligned arm (one-step pairs) from the frame whose row p
   carries row p + 1's, both fitted for real and read off the design matrix the estimators receive.

Recorded mutations (each applied to a scratch copy of the script, confirmed by grep, restored before the next):

* `with_fomc`, the line `return fc.add_columns(rows, calendar, horizon=horizon)` changed to `return fc.add_columns(rows, calendar, horizon=1)` (every lead
  reads the one-day-ahead calendar): `FrameTests.test_a_row_is_read_at_the_decision_instant_of_its_own_lead` fails with `AssertionError` (`0.0 != 1.0`: at
  lead 3 the cancelled meeting of 17 March 2020 is still a meeting day, and the mutated frame has already dropped it). It is the only test that fails.
* `fomc_registry`, the line `"days": horizon,` changed to `"days": 1,` (the scheduled declaration claims availability one day ahead at every lead):
  `RegistryTests.test_the_lead_registry_is_available_at_the_leads_decision_instant` and `DirectArmTests.test_every_fomc_column_is_the_targets_at_every_lead`
  error with `LookAheadError` (`'fomc_meeting_day' for the forecast of 2024-03-25 reads 2024-03-25, first observable at 2024-03-22 16:00:00, after the
  2024-03-21 16:00:00 decision`: the rule refuses a read the lead's decision could not have made), and `test_the_declared_block_is_valid_and_names_both_fields`
  fails with `AssertionError` (`1 != 4`).
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


script = load("fomc_variants_1087")
ac = script.ac

from repo_model import fomc_calendar as fc, measurement_fields, one_step_guard  # noqa: E402
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

FOMC = ("fomc_meeting_day", "fomc_days_to_next_meeting")
ROWS = 90


def march_2020():
    return [DailyObservation(date(2020, 3, d), {"x": float(d)}) for d in (12, 13, 16, 17, 18)]


class FeatureTests(unittest.TestCase):
    def test_each_arm_is_its_1027_variant_plus_the_two_fomc_columns_and_nothing_else(self):
        for arm, base in script.BASE.items():
            for h in ac.HORIZONS:
                features = script.arm_features(arm, h)
                self.assertEqual(features[: -len(FOMC)], ac.variant_features(base, h))
                self.assertEqual(features[-len(FOMC):], FOMC)
                self.assertEqual(len(features), len(set(features)))

    def test_the_arms_are_the_two_1027_variants_with_the_columns(self):
        self.assertEqual(script.BASE, {script.DIRECT_FOMC: ac.DIRECT, script.ALIGNED_FOMC: ac.ALIGNED})
        self.assertEqual(script.FOMC_COLUMNS, FOMC)

    def test_the_columns_are_written_about_the_target_day_so_the_one_step_guard_refuses_them(self):
        """Not in `CALENDAR_FEATURES`, but in `TARGET_DAY_COLUMNS`: a one-step fit given them raises unless the allow-list admits the arm."""
        names = ac.regressors(script.arm_features(script.ALIGNED_FOMC, 2))
        with self.assertRaises(ValueError):
            one_step_guard.check_one_step_regressors("fit_gradient_boosted_quantiles", names)
        listed = {entry.regressors for entry in one_step_guard.ONE_STEP_ALLOW_LIST.values()}
        self.assertNotIn(tuple(names), listed, "the aligned arm is admitted only by her entry; none is added here")


class FrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calendar = fc.load_calendar()

    def test_a_row_is_read_at_the_decision_instant_of_its_own_lead(self):
        rows = march_2020()
        by_lead = {h: {r.date.day: r.values["fomc_meeting_day"] for r in script.with_fomc(rows, h, self.calendar)} for h in (1, 3)}
        # 17 March 2020: the meeting was cancelled at 17:00 on 15 March. Lead 1 decides on 16 March (after it), lead 3 on 12 March (before it)
        self.assertEqual(by_lead[1][17], 0.0)
        self.assertEqual(by_lead[3][17], 1.0)

    def test_a_schedule_released_after_the_leads_decision_is_not_counted_at_that_lead(self):
        """The 2019 schedule was released at 12:00 on 25 May 2018: a lead-1 decision at 16:00 on 24 May cannot count 19 March 2019, one on 25 May does."""
        target = DailyObservation(date(2019, 3, 19), {})
        day_before = script.with_fomc([DailyObservation(date(2018, 5, 24), {}), target], 1, self.calendar)[-1]
        release_day = script.with_fomc([DailyObservation(date(2018, 5, 25), {}), target], 1, self.calendar)[-1]
        self.assertEqual(day_before.values["fomc_meeting_day"], 0.0)
        self.assertEqual(release_day.values["fomc_meeting_day"], 1.0)

    def test_the_input_rows_and_their_other_columns_are_unchanged(self):
        rows = march_2020()
        out = script.with_fomc(rows, 2, self.calendar)
        self.assertEqual([r.values["x"] for r in out], [r.values["x"] for r in rows])
        self.assertEqual([set(r.values) for r in rows], [{"x"}] * len(rows))

    def test_a_row_reads_nothing_from_rows_after_it(self):
        rows = [DailyObservation(day, {}) for day in business_days(40)]
        whole = script.with_fomc(rows, 3, self.calendar)
        prefix = script.with_fomc(rows[:25], 3, self.calendar)
        self.assertEqual([r.values for r in whole[:25]], [r.values for r in prefix])


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = measurement_fields.load_registry()
        self.days = business_days(80)

    def rule(self, h, registry=None):
        registry = script.fomc_registry(h, self.registry) if registry is None else registry
        return InformationRule(registry, FOMC + ("tga", "spread_bps"), decision_time=ac.DECISION, horizon=h)

    def test_the_lead_registry_is_available_at_the_leads_decision_instant(self):
        for h in ac.HORIZONS:
            with script.fomc_fields_on():
                rule = self.rule(h)
                info = rule.information_set(self.days, 60)
                rule.check(self.days, info)
            reads = {read.feature: read for read in info.reads}
            for name in FOMC:
                self.assertEqual(reads[name].kind, "scheduled")
                self.assertEqual(reads[name].row, 60, "served from the target row")
                self.assertEqual(reads[name].available_at, rule.decision_instant(self.days, 60))

    def test_a_declaration_of_earlier_availability_than_the_lead_allows_is_refused(self):
        """The control: one-day-ahead availability at lead 5 is what `asof` rule 2 refuses, the guard the registry above passes."""
        one_day = script.fomc_registry(1, self.registry)
        with script.fomc_fields_on():
            rule = self.rule(5, one_day)
            with self.assertRaises(LookAheadError):
                rule.check(self.days, rule.information_set(self.days, 60))

    def test_the_published_registries_are_not_changed(self):
        before = json.dumps(self.registry, sort_keys=True, default=str)
        script.fomc_registry(3, self.registry)
        self.assertEqual(json.dumps(self.registry, sort_keys=True, default=str), before)
        self.assertNotIn("scheduled_availability", self.registry["fomc_calendar"])

    def test_the_declared_block_is_valid_and_names_both_fields(self):
        block = script.fomc_registry(4, self.registry)["fomc_calendar"]["scheduled_availability"]
        self.assertEqual(block["days"], 4)
        self.assertEqual(block["fields"], list(FOMC))
        self.assertEqual(block["available_time"], "16:00")


def design_panel(h, count=ROWS):
    """`panel()`'s unique-per-row columns, plus the FOMC columns as the lead reads them, on 2024 dates the calendar covers."""

    rows = panel(count)
    return rows, script.with_fomc(rows, h)


class DirectArmTests(NeedsExtra):
    """No stand-in: the direct arm passes the #947 guard as it stands (a direct fit is not checked)."""

    def test_every_fomc_column_is_the_targets_at_every_lead(self):
        for h in ac.HORIZONS:
            rows, framed = design_panel(h)
            frame = [DailyObservation(r.date, {**r.values, **f.values}) for r, f in zip(rows, framed)]
            features = script.arm_features(script.DIRECT_FOMC, h)
            registry = script.fomc_registry(h, measurement_fields.load_registry())
            with ac._load("net_settlement").switched_on(), script.fomc_fields_on():
                rule = InformationRule(registry, tuple(features), decision_time=ac.DECISION, horizon=h)
                fit = script.arm_fit(script.DIRECT_FOMC, features)
                with Recorded() as recorded:
                    fit(frame, minimum_history=20, information=rule)
            design, targets, leaf = recorded.calls[0]
            self.assertEqual(leaf, ac.LEAF)
            self.assertGreater(len(design), 30)
            names = tuple(ac.regressors(features))
            bad = offenders(design, targets, design_names(names), frame, FOMC, lambda name, j: j)
            self.assertEqual(bad, [], f"lead {h}: {bad[:3]}")
            moved = [t for t in targets if frame[int(round(t - 1000.0))].values[FOMC[1]] != frame[int(round(t - 1000.0)) - 1].values[FOMC[1]]]
            self.assertTrue(moved, "the days-to-next column differs between a target row and its origin row, so the check above can tell them apart")

    def test_the_direct_arm_names_direct_pairs_and_the_leaf_of_its_variant(self):
        fit = script.arm_fit(script.DIRECT_FOMC, script.arm_features(script.DIRECT_FOMC, 1))
        self.assertEqual(fit.keywords["training_pairs"], "direct")
        self.assertEqual(fit.keywords["min_samples_leaf"], ac.LEAF)


class AlignedArmTests(NeedsExtra):
    def stand_in(self):
        entries = dict(one_step_guard.ONE_STEP_ALLOW_LIST)
        for h in ac.HORIZONS:
            names = tuple(ac.regressors(script.arm_features(script.ALIGNED_FOMC, h)))
            entries[f"stand_in_{h}"] = one_step_guard.FrozenDeclaration("fit_gradient_boosted_quantiles", names, "test stand-in")
        return mock.patch.object(one_step_guard, "ONE_STEP_ALLOW_LIST", entries)

    def frame(self, h):
        rows, framed = design_panel(h)
        return [DailyObservation(r.date, {**r.values, **f.values}) for r, f in zip(rows, framed)]

    def test_the_guard_refuses_the_aligned_arm_until_the_allow_list_admits_it(self):
        features = script.arm_features(script.ALIGNED_FOMC, 2)
        with self.assertRaises(ValueError):
            script.arm_fit(script.ALIGNED_FOMC, features)(self.frame(2), 20)

    def test_the_walk_refuses_before_any_work_and_says_whose_decision_it_is(self):
        with self.assertRaises(SystemExit) as raised:
            script.require_admitted(script.ALIGNED_FOMC, 2)
        self.assertIn("allow-list", str(raised.exception))
        script.require_admitted(script.DIRECT_FOMC, 2)

    def test_every_fomc_and_target_row_column_is_the_targets_when_admitted(self):
        with self.stand_in():
            for h in ac.HORIZONS:
                frame = self.frame(h)
                features = script.arm_features(script.ALIGNED_FOMC, h)
                names = tuple(ac.regressors(features))
                with Recorded() as recorded:
                    script.arm_fit(script.ALIGNED_FOMC, features)(frame, 20)
                design, targets, leaf = recorded.calls[0]
                self.assertEqual(leaf, ac.LEAF)
                columns = tuple(ac.target_row_columns(h)) + FOMC
                bad = offenders(design, targets, design_names(names), frame, columns, lambda name, j: j)
                self.assertEqual(bad, [], f"lead {h}: {bad[:3]} are trained from row p, not the target row p + 1")

    def test_an_unaligned_frame_is_refused_before_the_fit(self):
        """Mutation: `align_columns` returning the frame unchanged makes the fit raise ValueError from `require_aligned`."""
        with self.stand_in():
            fit = script.arm_fit(script.ALIGNED_FOMC, script.arm_features(script.ALIGNED_FOMC, 2))
            with mock.patch.object(ac, "align_columns", lambda frame, fields=ac.TARGET_ROW_COLUMNS: list(frame)):
                with self.assertRaises(ValueError):
                    fit(self.frame(2), 20)

    def test_the_fit_names_no_information_so_the_pairs_stay_one_step(self):
        fit = script.arm_fit(script.ALIGNED_FOMC, script.arm_features(script.ALIGNED_FOMC, 1))
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
        scored, not_run = script.scored_arms(self.walks([script.DIRECT_FOMC, script.ALIGNED_FOMC]))
        self.assertEqual(scored, [script.DIRECT_FOMC, script.ALIGNED_FOMC])
        self.assertEqual(not_run, {})

    def test_the_aligned_arm_not_admitted_is_reported_not_run_with_the_reason(self):
        scored, not_run = script.scored_arms(self.walks([script.DIRECT_FOMC]))
        self.assertEqual(scored, [script.DIRECT_FOMC])
        self.assertIn("allow-list", not_run[script.ALIGNED_FOMC])

    def test_the_direct_arm_missing_is_an_error(self):
        with self.assertRaises(ValueError):
            script.scored_arms(self.walks([script.ALIGNED_FOMC]))

    def test_an_arm_with_some_leads_walked_is_an_error_not_a_silent_drop(self):
        root = self.walks([script.DIRECT_FOMC])
        (root / f"{script.ALIGNED_FOMC}_h1.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            script.scored_arms(root)


class DayTypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calendar = fc.load_calendar()

    def test_a_meeting_day_is_an_fomc_day_whatever_its_other_type_and_both_days_of_a_two_day_meeting_are(self):
        self.assertTrue(script.is_fomc_day(date(2019, 1, 29), self.calendar))
        self.assertTrue(script.is_fomc_day(date(2019, 1, 30), self.calendar))
        self.assertFalse(script.is_fomc_day(date(2019, 1, 31), self.calendar))

    def test_a_cancelled_meeting_is_not_an_fomc_day_and_an_unscheduled_one_is(self):
        self.assertFalse(script.is_fomc_day(date(2020, 3, 17), self.calendar))
        self.assertTrue(script.is_fomc_day(date(2019, 10, 4), self.calendar), "labelled after the fact: the day did hold a meeting")

    def test_the_overlapping_cuts_are_declared_and_split_a_list_of_target_days(self):
        types = {date(2019, 1, 29): "ordinary", date(2019, 1, 30): "month_end", date(2019, 1, 31): "ordinary", date(2019, 2, 1): "ordinary"}
        cuts = script.fomc_cuts(types, self.calendar)
        self.assertEqual(cuts["fomc_day"], [date(2019, 1, 29), date(2019, 1, 30)])
        self.assertEqual(cuts["fomc_ordinary"], [date(2019, 1, 29)])
        self.assertEqual(cuts["ordinary_non_fomc"], [date(2019, 1, 31), date(2019, 2, 1)])


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))

    def test_the_declaration_names_exactly_two_arms_on_the_1027_variants(self):
        self.assertEqual(self.document["issue"], 1087)
        self.assertEqual(sorted(self.document["arms"]), sorted([script.DIRECT_FOMC, script.ALIGNED_FOMC]))
        self.assertEqual({a: v["base"] for a, v in self.document["arms"].items()}, script.BASE)

    def test_the_committed_declaration_is_what_declare_writes(self):
        self.assertEqual(self.document, json.loads(json.dumps(script.declaration_document())))

    def test_the_declaration_keeps_the_study_window_and_the_lockbox(self):
        self.assertIn("no day after 2025-12-31", self.document["limits"])
        self.assertIn("no lockbox day", self.document["limits"])
        self.assertEqual(script.LAST_TARGET, date(2025, 12, 31))

    def test_every_declared_comparison_is_an_arm_against_its_variant_or_the_control(self):
        self.assertEqual(
            self.document["comparisons"],
            ["each arm over its #1027 variant without the columns", "each arm over gbm_funding"],
        )


class ReadingRuleTests(unittest.TestCase):
    def row(self, skill, low, high):
        return {"skill": skill, "skill_interval": [low, high], "days": 100}

    def test_helps_needs_a_lower_end_above_zero_and_loses_needs_an_upper_end_below_zero(self):
        rows = {
            script.DIRECT_FOMC: {"fomc_day": self.row(0.04, 0.01, 0.07), "ordinary_non_fomc": self.row(-0.01, -0.03, 0.01)},
            script.ALIGNED_FOMC: {"fomc_day": self.row(0.04, -0.01, 0.09), "ordinary_non_fomc": self.row(-0.05, -0.09, -0.01)},
        }
        direct, aligned = script.reading_rules(rows)
        self.assertIn("gbm_funding_cal_direct_fomc helps over gbm_funding_cal_direct on FOMC days", direct)
        self.assertIn("does not lose", direct)
        self.assertIn("gbm_funding_cal_aligned_fomc is not shown to help over gbm_funding_cal_aligned", aligned)
        self.assertIn("and loses on ordinary non-FOMC days", aligned)

    def test_an_unscored_or_undefined_cut_is_not_read(self):
        rows = {script.DIRECT_FOMC: {"fomc_day": {"undefined": "x"}, "ordinary_non_fomc": self.row(0.0, -0.1, 0.1)}}
        self.assertIn("not read", script.reading_rules(rows)[0])
        self.assertIn("not read", script.reading_rules({script.DIRECT_FOMC: {}})[0])


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            ac.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])


if __name__ == "__main__":
    unittest.main()
