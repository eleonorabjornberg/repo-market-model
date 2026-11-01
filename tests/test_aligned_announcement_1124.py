"""The announcement-dated settlement arms of the #1027 direct variant (`scripts/aligned_announcement_1124.py`, #1124, H5 step 3).

The directive reads the Treasury settlement columns at leads 2 to 5 from the auction announcement (`metadata/settlement_announcement_dating.json`,
measured and not in force), through a declared, scratch-only path, and leaves the published paths alone. Each part is tested:

1. `arm_inputs` writes row T's settlement columns as public at the 12:00 instant of the panel day h rows before T (`settlement_dating.known_columns`),
   checks them (`check_known_columns`) and declares them to `InformationRule` as a scheduled field available h panel days ahead
   (`result_dated_registry`); it changes neither its input rows nor the registry it is given.
2. The published paths still refuse the columns beyond lead 1: `sources.json` is read for what it declares, `InformationRule` over it raises
   `LookAheadError` at leads 2 to 5, and the published feature list of the live record drops the aggregate there.
3. The arm trains every settlement column from the target row of its pair (direct pairs, fitted for real and read off the design matrix the estimators
   receive), and passes the #947 guard without an allow-list entry. The one-step fit of the same regressors is refused, and the allow-list is the one
   pinned before this directive (adding to it is Eleonora's decision).
4. The settlement day types split coupon from bill-only, and an arm with some leads walked and others not is an error.

Recorded mutations (each applied to a scratch copy of the script, confirmed by grep, restored before the next):

* `arm_inputs`, the line `settlement_dating.check_known_columns(dated, results, horizon, declaration)` replaced by `pass` (the frame is trusted):
  `DatedInputsTests.test_a_frame_that_counts_an_unannounced_auction_is_refused` fails with `AssertionError` (`LookAheadError not raised`) and
  `test_a_frame_that_leaves_out_an_announced_auction_is_refused` with `AssertionError` (`StaleReadError not raised`).
* `arm_inputs`, the line `registry = settlement_dating.result_dated_registry(registry, declaration, horizon)` changed to `registry = dict(registry)` (the
  published block, one day ahead, is kept at every lead): `DirectArmTests.test_every_settlement_column_is_the_targets_at_every_lead` errors with
  `LookAheadError` (`'treasury_settlement' for the forecast of 2024-01-10 reads 2024-01-10, first observable at 2024-01-09 15:00:00, after the 2024-01-08
  16:00:00 decision`) and `RegistryTests.test_the_dated_registry_serves_the_columns_at_the_leads_decision` fails with `AssertionError`
  (`datetime.time(15, 0) != datetime.time(12, 0)`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, time
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


script = load("aligned_announcement_1124")
ac = script.ac

from repo_model import measurement_fields, ml, one_step_guard, settlement_dating  # noqa: E402
from repo_model.asof import InformationRule, StaleReadError  # noqa: E402
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

SETTLEMENT = ("treasury_settlement", "treasury_settlement_coupons", "treasury_settlement_bills")
ROWS = 90
DECLARATION = settlement_dating.load_result_dating(script.DATING)


def auction(settles, column, amount, announced, hour=12):
    return settlement_dating.AuctionResult(settles, column, amount, datetime.combine(announced, time(hour)))


def synthetic_results(days, announce_rows_before=6):
    """One bill and one coupon on every row from `announce_rows_before` on, each with an amount unique to its row, announced that many rows ahead."""

    out = []
    for i in range(announce_rows_before, len(days)):
        out.append(auction(days[i], "treasury_settlement_bills", 1.0 + i / 100.0, days[i - announce_rows_before]))
        out.append(auction(days[i], "treasury_settlement_coupons", 50.0 + i / 100.0, days[i - announce_rows_before]))
    return out


def dated_panel(h, count=ROWS):
    """`panel()` with its settlement columns replaced by what the announcements made public h rows ahead, and the results behind them."""

    rows = panel(count)
    results = synthetic_results([r.date for r in rows])
    dated, registry = script.arm_inputs(rows, measurement_fields.load_registry(), h, results=results, declaration=DECLARATION)
    return rows, dated, registry, results


class FeatureTests(unittest.TestCase):
    def test_each_arm_is_the_direct_variant_plus_its_settlement_columns_and_nothing_else(self):
        for h in ac.HORIZONS:
            base = ac.variant_features(ac.DIRECT, h)
            self.assertEqual(script.arm_features(script.ANN, h), base + tuple(c for c in SETTLEMENT if c not in base))
            self.assertEqual(script.arm_features(script.ANN_COUPONS, h), base + tuple(c for c in ("treasury_settlement_coupons",) if c not in base))

    def test_at_lead_1_an_arm_is_the_direct_variant_because_the_published_columns_are_the_dated_ones_there(self):
        for arm in script.ARMS:
            self.assertEqual(script.arm_features(arm, 1), ac.variant_features(ac.DIRECT, 1))

    def test_from_lead_2_the_arms_read_what_the_direct_variant_does_not(self):
        for h in (2, 3, 4, 5):
            base = set(ac.variant_features(ac.DIRECT, h))
            self.assertTrue(base.isdisjoint(SETTLEMENT))
            self.assertEqual(set(script.arm_features(script.ANN, h)) - base, set(SETTLEMENT))
            self.assertEqual(set(script.arm_features(script.ANN_COUPONS, h)) - base, {"treasury_settlement_coupons"})

    def test_an_undeclared_arm_is_refused(self):
        with self.assertRaises(ValueError):
            script.arm_features("gbm_funding", 2)


class DatedInputsTests(unittest.TestCase):
    """Hand case: two auctions settle on day 10, one announced on day 7, one on day 9 (12:00 each)."""

    def setUp(self):
        self.days = business_days(20)
        self.rows = [DailyObservation(d, {"treasury_settlement": 99.0, "treasury_settlement_bills": 99.0, "treasury_settlement_coupons": 99.0}) for d in self.days]
        self.results = [
            auction(self.days[10], "treasury_settlement_coupons", 30.0, self.days[7]),
            auction(self.days[10], "treasury_settlement_bills", 5.0, self.days[9]),
        ]

    def dated(self, h, results=None):
        rows, _ = script.arm_inputs(self.rows, measurement_fields.load_registry(), h, results=self.results if results is None else results, declaration=DECLARATION)
        return rows[10].values

    def test_a_column_counts_exactly_the_auctions_announced_by_noon_of_the_decision_day(self):
        self.assertEqual(self.dated(1)["treasury_settlement"], 35.0)  # decision day 9, 12:00: both announced
        self.assertEqual(self.dated(2)["treasury_settlement"], 30.0)  # day 8: the bill (announced day 9) is not
        self.assertEqual(self.dated(2)["treasury_settlement_bills"], 0.0)
        self.assertEqual(self.dated(2)["treasury_settlement_coupons"], 30.0)
        self.assertEqual(self.dated(3)["treasury_settlement_coupons"], 30.0)  # day 7, 12:00: announced at that instant
        self.assertEqual(self.dated(4)["treasury_settlement"], 0.0)  # day 6: neither

    def test_a_bill_only_settlement_day_has_a_zero_coupon_leg_and_a_positive_aggregate(self):
        """Lens A: read through the coupon leg alone, a bill-only settlement day looks like a day with no settlement."""
        values = self.dated(2, results=[auction(self.days[10], "treasury_settlement_bills", 5.0, self.days[8])])
        self.assertEqual((values["treasury_settlement"], values["treasury_settlement_bills"], values["treasury_settlement_coupons"]), (5.0, 5.0, 0.0))

    def test_a_frame_that_counts_an_unannounced_auction_is_refused(self):
        """The control of the guard: a dating that counts every auction at every lead raises `LookAheadError`."""

        def leaky(rows, results, horizon, declaration):
            out = []
            for row in rows:
                values = dict(row.values)
                for column in settlement_dating.COLUMNS:
                    values[column] = sum(r.amount for r in results if r.settles == row.date and (column == "treasury_settlement" or r.column == column))
                out.append(DailyObservation(row.date, values))
            return out

        with mock.patch.object(settlement_dating, "known_columns", leaky):
            with self.assertRaises(LookAheadError):
                script.arm_inputs(self.rows, measurement_fields.load_registry(), 3, results=self.results, declaration=DECLARATION)

    def test_a_frame_that_leaves_out_an_announced_auction_is_refused(self):
        def stale(rows, results, horizon, declaration):
            return [DailyObservation(r.date, {**r.values, **{c: 0.0 for c in settlement_dating.COLUMNS}}) for r in rows]

        with mock.patch.object(settlement_dating, "known_columns", stale):
            with self.assertRaises(StaleReadError):
                script.arm_inputs(self.rows, measurement_fields.load_registry(), 1, results=self.results, declaration=DECLARATION)

    def test_a_record_announced_after_its_settlement_is_refused_by_the_loader(self):
        record = {"issue_date": "2024-01-10", "auction_date": "2024-01-09", "announcemt_date": "2024-01-11", "security_type": "Note", "offering_amt": "1000000000"}
        with self.assertRaises(ValueError):
            settlement_dating.auction_results([record], DECLARATION)

    def test_the_input_rows_are_not_changed(self):
        before = [dict(r.values) for r in self.rows]
        self.dated(2)
        self.assertEqual([dict(r.values) for r in self.rows], before)


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = measurement_fields.load_registry()
        self.days = business_days(80)

    def rule(self, h, registry):
        return InformationRule(registry, SETTLEMENT + ("tga", "spread_bps"), decision_time=ac.DECISION, horizon=h)

    def test_the_dated_registry_serves_the_columns_at_the_leads_decision(self):
        for h in ac.HORIZONS:
            _, registry = script.arm_inputs(panel(80), self.registry, h, results=[], declaration=DECLARATION)
            rule = self.rule(h, registry)
            info = rule.information_set(self.days, 60)
            rule.check(self.days, info)
            reads = {read.feature: read for read in info.reads}
            for name in SETTLEMENT:
                self.assertEqual(reads[name].kind, "scheduled")
                self.assertEqual(reads[name].row, 60, "served from the target row")
                self.assertEqual(reads[name].available_at.time(), time(12, 0), "the announcement's noon")
                self.assertLessEqual(reads[name].available_at, rule.decision_instant(self.days, 60))

    def test_the_registry_it_was_given_is_not_changed(self):
        before = json.dumps(self.registry, sort_keys=True, default=str)
        script.arm_inputs(panel(80), self.registry, 3, results=[], declaration=DECLARATION)
        self.assertEqual(json.dumps(self.registry, sort_keys=True, default=str), before)


class PublishedPathsTests(unittest.TestCase):
    """Criterion: the live and published paths still refuse settlement columns beyond lead 1. The arm's path is its own."""

    def setUp(self):
        self.sources = json.loads(ac.SOURCES.read_text(encoding="utf-8"))
        self.days = business_days(80)

    def test_the_published_declaration_dates_a_settlement_one_panel_day_ahead(self):
        block = self.sources["treasury_auctions"]["scheduled_availability"]
        self.assertEqual(block["days"], 1)

    def test_the_published_registry_refuses_each_settlement_column_beyond_lead_1(self):
        for column in SETTLEMENT:
            for h in (2, 3, 4, 5):
                rule = InformationRule(self.sources, (column, "tga", "spread_bps"), decision_time=ac.DECISION, horizon=h)
                with self.assertRaises(LookAheadError, msg=f"{column} at lead {h}"):
                    rule.check(self.days, rule.information_set(self.days, 60))
            rule = InformationRule(self.sources, (column, "tga", "spread_bps"), decision_time=ac.DECISION, horizon=1)
            rule.check(self.days, rule.information_set(self.days, 60))

    def test_the_live_records_published_features_carry_no_settlement_beyond_lead_1(self):
        live = ac._load("live_record")
        for h in (2, 3, 4, 5):
            self.assertTrue(set(SETTLEMENT).isdisjoint(live.published_features(h)), h)
        self.assertIn("treasury_settlement", live.published_features(1))

    def test_building_the_arms_inputs_leaves_the_published_registry_refusing(self):
        script.arm_inputs(panel(40), self.sources, 3, results=[], declaration=DECLARATION)
        rule = InformationRule(self.sources, ("treasury_settlement", "spread_bps"), decision_time=ac.DECISION, horizon=3)
        with self.assertRaises(LookAheadError):
            rule.check(self.days, rule.information_set(self.days, 60))

    def test_the_dating_is_declared_measured_and_not_in_force(self):
        document = json.loads(script.DATING.read_text(encoding="utf-8"))
        # #1327: the status no longer says "measured and off"; it says what "off in the published declarations" means.
        self.assertIn("off in the published declarations at every lead above 1", document["status"])


class DirectArmTests(NeedsExtra):
    """No stand-in: the arms pass the #947 guard as it stands (a direct fit is not checked)."""

    def test_every_settlement_column_is_the_targets_at_every_lead(self):
        for h in (2, 3, 4, 5):
            rows, dated, registry, _ = dated_panel(h)
            for arm, columns in ((script.ANN, SETTLEMENT), (script.ANN_COUPONS, ("treasury_settlement_coupons",))):
                features = script.arm_features(arm, h)
                frame = dated
                with ac._load("net_settlement").switched_on():
                    rule = InformationRule(registry, tuple(features), decision_time=ac.DECISION, horizon=h)
                    fit = script.arm_fit(arm, features)
                    with Recorded() as recorded:
                        fit(frame, minimum_history=20, information=rule)
                design, targets, leaf = recorded.calls[0]
                self.assertEqual(leaf, ac.LEAF)
                self.assertGreater(len(design), 30)
                names = tuple(ac.regressors(features))
                bad = offenders(design, targets, design_names(names), frame, columns, lambda name, j: j)
                self.assertEqual(bad, [], f"{arm} lead {h}: {bad[:3]}")
                moved = [t for t in targets if frame[int(round(t - 1000.0))].values[columns[0]] != frame[int(round(t - 1000.0)) - 1].values[columns[0]]]
                self.assertTrue(moved, "the column differs between a target row and its origin row, so the check above can tell them apart")

    def test_the_arms_name_direct_pairs_and_the_leaf_of_their_variant(self):
        for arm in script.ARMS:
            fit = script.arm_fit(arm, script.arm_features(arm, 2))
            self.assertEqual(fit.keywords["training_pairs"], "direct")
            self.assertEqual(fit.keywords["min_samples_leaf"], ac.LEAF)

    def test_the_one_step_fit_of_the_same_regressors_is_refused_and_the_allow_list_is_unchanged(self):
        names = ac.regressors(script.arm_features(script.ANN, 2))
        with self.assertRaises(ValueError):
            ml.fit_gradient_boosted_quantiles(panel(), regressors=names, levels=ac.GRID, minimum_history=20)
        self.assertEqual(
            sorted(one_step_guard.ONE_STEP_ALLOW_LIST),
            ["aligned_calendar_1027_h1", "aligned_calendar_1027_h2_to_h5", "gbm_funding_634", "pressure_model_v2", "published_distribution_crps"],
        )
        arm_regressors = {tuple(ac.regressors(script.arm_features(a, h))) for a in script.ARMS for h in (2, 3, 4, 5)}
        listed = {e.regressors for e in one_step_guard.ONE_STEP_ALLOW_LIST.values()}
        self.assertTrue(arm_regressors.isdisjoint(listed), "no allow-list entry admits an arm: they run on direct pairs")


class DayTypeTests(unittest.TestCase):
    class Frame:
        def __init__(self, kinds, values):
            self.kinds, self.values = kinds, values

        def day_type(self, day):
            return self.kinds[day]

    def frame(self):
        d = [date(2024, 1, n) for n in (2, 3, 4, 5, 8, 9)]
        kinds = {d[0]: "ordinary", d[1]: "ordinary", d[2]: "ordinary", d[3]: "ordinary", d[4]: "month_end", d[5]: "ordinary"}
        values = {
            d[0]: {"treasury_settlement_coupons": 20.0, "treasury_settlement_bills": 5.0},  # coupon (with a bill)
            d[1]: {"treasury_settlement_coupons": 0.0, "treasury_settlement_bills": 5.0},  # bill only
            d[2]: {"treasury_settlement_coupons": 0.0, "treasury_settlement_bills": 0.0},  # none
            d[3]: {"treasury_settlement_coupons": None, "treasury_settlement_bills": None},  # a hole reads as none
            d[4]: {"treasury_settlement_coupons": 20.0, "treasury_settlement_bills": 5.0},  # month-end keeps its own type
            d[5]: {"treasury_settlement_coupons": 7.0, "treasury_settlement_bills": 0.0},
        }
        return self.Frame(kinds, values), d

    def test_settlement_days_split_into_coupon_and_bill_only_and_other_types_are_kept(self):
        frame, d = self.frame()
        self.assertEqual([script.target_type(frame, day) for day in d], ["settlement_coupon", "settlement_bill", "ordinary", "ordinary", "month_end", "settlement_coupon"])

    def test_the_union_of_the_two_settlement_types_is_the_1027_settlement_type(self):
        frame, d = self.frame()
        for day in d:
            ours = script.target_type(frame, day)
            theirs = ac.target_type(frame, day)
            self.assertEqual(theirs == "settlement", ours in ("settlement_coupon", "settlement_bill"))


class ScoredArmsTests(unittest.TestCase):
    """Both arms are walked together, with the reference walks of #1027 beside them; an arm with some leads only is an error."""

    def walks(self, names):
        root = Path(tempfile.mkdtemp())
        for name in names:
            for h in ac.HORIZONS:
                (root / f"{name}_h{h}.json").write_text("{}", encoding="utf-8")
        return root

    def test_both_walked_scores_both(self):
        self.assertEqual(script.scored_arms(self.walks(script.ARMS)), list(script.ARMS))

    def test_an_arm_missing_is_an_error(self):
        with self.assertRaises(ValueError):
            script.scored_arms(self.walks([script.ANN]))

    def test_an_arm_with_some_leads_walked_is_an_error_not_a_silent_drop(self):
        root = self.walks(script.ARMS)
        (root / f"{script.ANN}_h5.json").unlink()
        with self.assertRaises(ValueError):
            script.scored_arms(root)

    def test_lead_1_is_the_direct_variants_by_construction_and_the_check_reports_a_difference(self):
        arms, ref = self.walks([]), self.walks([])
        for root, name, laws in ((arms, script.ANN, {"2024-01-02": [1.0]}), (ref, ac.DIRECT, {"2024-01-02": [1.0]})):
            (root / f"{name}_h1.json").write_text(json.dumps({"laws": laws}), encoding="utf-8")
        self.assertTrue(script.lead_1_identical(arms, ref, script.ANN))
        (arms / f"{script.ANN}_h1.json").write_text(json.dumps({"laws": {"2024-01-02": [1.5]}}), encoding="utf-8")
        self.assertFalse(script.lead_1_identical(arms, ref, script.ANN))


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))

    def test_the_committed_declaration_is_what_declare_writes(self):
        self.assertEqual(self.document, json.loads(json.dumps(script.declaration_document())))

    def test_the_declaration_names_two_arms_on_direct_pairs_and_no_aligned_one_step_arm(self):
        self.assertEqual(self.document["issue"], 1124)
        self.assertEqual(list(self.document["arms"]), list(script.ARMS))
        for arm in script.ARMS:
            self.assertEqual(self.document["arms"][arm]["training_pairs"], "direct")
        self.assertIn("allow-list", self.document["one_step_guard"])

    def test_the_declaration_keeps_the_study_window_the_lockbox_and_the_published_files(self):
        limits = " ".join(self.document["limits"])
        for text in ("2025-12-31", "lockbox", "sources.json", "information-set.md"):
            self.assertIn(text, limits)

    def test_the_declared_comparisons_are_the_issues(self):
        self.assertEqual(
            self.document["comparisons"]["against"],
            ["gbm_funding_cal_aligned", "gbm_funding", "B1", "B1_prime", "B2", "gbm_funding_cal_direct"],
        )
        self.assertEqual(self.document["comparisons"]["between_arms"], [script.ANN_COUPONS, script.ANN])

    def test_the_dating_the_arms_read_is_the_committed_one_and_unchanged_by_this_study(self):
        self.assertEqual(self.document["dating"]["file"], "metadata/settlement_announcement_dating.json")
        self.assertEqual(settlement_dating.load_result_dating(script.DATING)["basis"], "auction_announcement")


class ReadingRuleTests(unittest.TestCase):
    def row(self, skill, low, high):
        return {"skill": skill, "skill_interval": [low, high]}

    def test_helps_needs_a_lower_end_above_zero_and_loses_needs_an_upper_end_below_zero(self):
        rows = {
            script.ANN: {
                "settlement_coupon": self.row(0.05, 0.01, 0.09),
                "settlement_bill": self.row(0.02, -0.03, 0.07),
                "ordinary": self.row(-0.04, -0.06, -0.01),
            }
        }
        text = " ".join(script.reading_rules(rows))
        self.assertIn("helps", text)
        self.assertIn("is not shown to help", text)
        self.assertIn("loses", text)

    def test_an_unscored_or_undefined_cut_is_not_read(self):
        out = script.reading_rules({script.ANN: {"settlement_coupon": None, "settlement_bill": {"undefined": True}, "ordinary": self.row(0, -1, 1)}})
        self.assertIn("not read", out[0])


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            ac.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        ac.require_study_window([date(2025, 12, 31)])


if __name__ == "__main__":
    unittest.main()
