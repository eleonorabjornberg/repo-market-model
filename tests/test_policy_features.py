"""Policy-register features (#412, track P of #374): read from announcements, never from hindsight.

`repo_model.policy_features` turns `metadata/policy_events.json` into columns read at
each row's decision instant. Off in every published declaration.

Mutation record
---------------
Run in a scratch copy of the tree, with the mutated line confirmed applied by grep and
restored before the next.

1. `policy_feature_values`: `state = policy_state(register, as_of)` mutated to
   `state = policy_state(register, as_of + timedelta(days=30))` (announcements up to a
   month ahead admitted). Eight tests fail: six with `LookAheadError` from the explicit
   `require_announced` loop (for example
   `test_an_entry_announced_after_the_decision_time_is_not_seen_that_day`,
   `test_a_date_only_source_is_not_seen_on_its_own_day`), and two with `AssertionError`
   (`test_the_column_values_on_a_known_decision_day`,
   `test_the_debt_limit_binds_only_from_its_effective_date`).
2. `policy_feature_values`: the explicit loop `for entry in state.in_force + state.pending:
   require_announced(entry, as_of)` deleted. Kills
   `test_a_register_that_leaks_is_refused_by_the_explicit_guard` with
   `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model import measurement_fields, policy_events, policy_features  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = ROOT / "metadata" / "policy_features.json"


def entry(id_, kind, action, announced, effective, details=None, time_basis="stated"):
    """A register entry; `announced` is a naive datetime, `effective` a date or None."""

    return policy_events.PolicyEntry(
        id_, kind, action, id_, announced, time_basis, effective, "https://example.test/x", False, dict(details or {})
    )


REGISTER = (
    entry("qt_start", "balance_sheet", "qt_start", datetime(2018, 1, 10, 14), date(2018, 2, 1)),
    entry("iorb_a", "iorb_rate", "set_rate", datetime(2018, 6, 13, 14), date(2018, 6, 14),
          {"offset_from_range_bottom_bps": 20}),
    entry("debt_r", "debt_ceiling", "reinstatement", datetime(2018, 7, 2, 23, 59, 59), date(2018, 8, 1),
          time_basis="not_stated"),
    entry("qt_end", "balance_sheet", "qt_end", datetime(2018, 9, 12, 14), date(2018, 9, 13)),
    entry("slr_x", "slr", "exclusion_start", datetime(2018, 9, 20, 16, 45), date(2018, 9, 20)),
    entry("eslr", "slr", "eslr_proposal", datetime(2018, 9, 21, 11), None),
)


def values(as_of, register=REGISTER):
    return policy_features.policy_feature_values(register, as_of)


class ColumnTests(unittest.TestCase):
    def test_the_column_values_on_a_known_decision_day(self):
        got = values(datetime(2018, 7, 10, 16))
        self.assertEqual(got["policy_days_since_known"], 8.0)  # the 2 July act, public 23:59:59
        self.assertEqual(got["policy_days_until_effective"], 22.0)  # reinstatement effective 1 August
        self.assertEqual(got["policy_pending_count"], 1.0)
        self.assertEqual(got["policy_iorb_offset_bp"], 20.0)
        self.assertEqual(got["policy_qt_in_force"], 1.0)
        self.assertEqual(got["policy_slr_exclusion_in_force"], 0.0)
        self.assertEqual(got["policy_debt_limit_reinstated"], 0.0)  # announced, not yet in force

    def test_the_debt_limit_binds_only_from_its_effective_date(self):
        self.assertEqual(values(datetime(2018, 7, 31, 16))["policy_debt_limit_reinstated"], 0.0)
        self.assertEqual(values(datetime(2018, 8, 1, 16))["policy_debt_limit_reinstated"], 1.0)

    def test_runoff_ends_when_its_end_is_in_force(self):
        self.assertEqual(values(datetime(2018, 9, 12, 16))["policy_qt_in_force"], 1.0)  # announced, not effective
        self.assertEqual(values(datetime(2018, 9, 13, 16))["policy_qt_in_force"], 0.0)

    def test_a_proposal_is_pending_and_counts_in_no_waiting_time(self):
        got = values(datetime(2018, 9, 22, 16))
        self.assertEqual(got["policy_pending_count"], 1.0)
        self.assertEqual(got["policy_days_until_effective"], float(policy_features.DAYS_CAP))

    def test_days_are_capped_and_never_missing(self):
        got = values(datetime(2019, 6, 1, 16))
        self.assertEqual(got["policy_days_since_known"], float(policy_features.DAYS_CAP))
        self.assertEqual(set(got), set(policy_features.COLUMNS))
        self.assertTrue(all(v is not None for v in got.values()))

    def test_an_empty_register_reads_the_defaults(self):
        got = values(datetime(2018, 7, 10, 16), ())
        self.assertEqual(got["policy_days_since_known"], float(policy_features.DAYS_CAP))
        self.assertEqual(got["policy_pending_count"], 0.0)
        self.assertEqual(got["policy_iorb_offset_bp"], 0.0)

    def test_an_aware_datetime_is_refused(self):
        from datetime import timezone

        with self.assertRaises(ValueError):
            values(datetime(2018, 7, 10, 16, tzinfo=timezone.utc))


class PointInTimeTests(unittest.TestCase):
    def test_an_entry_announced_after_the_decision_instant_changes_nothing(self):
        as_of = datetime(2018, 7, 10, 16)
        base = values(as_of)
        future = [e for e in REGISTER if e.announced_at > as_of]
        self.assertTrue(future)
        for victim in future:
            altered = tuple(
                e if e.id != victim.id else e._replace(kind="slr", action="exclusion_start", effective=date(2018, 1, 1))
                for e in REGISTER
            )
            self.assertEqual(values(as_of, altered), base, victim.id)
        self.assertEqual(values(as_of, tuple(e for e in REGISTER if e.announced_at <= as_of)), base)

    def test_an_entry_announced_the_same_day_before_the_decision_is_seen(self):
        self.assertEqual(values(datetime(2018, 6, 13, 16))["policy_iorb_offset_bp"], 0.0)  # in force only 14 June
        self.assertEqual(values(datetime(2018, 6, 13, 16))["policy_pending_count"], 1.0)
        self.assertEqual(values(datetime(2018, 6, 13, 13))["policy_pending_count"], 0.0)  # before 14:00

    def test_an_entry_announced_after_the_decision_time_is_not_seen_that_day(self):
        self.assertEqual(values(datetime(2018, 9, 20, 16))["policy_slr_exclusion_in_force"], 0.0)  # 16:45
        self.assertEqual(values(datetime(2018, 9, 21, 16))["policy_slr_exclusion_in_force"], 1.0)

    def test_a_date_only_source_is_not_seen_on_its_own_day(self):
        self.assertEqual(values(datetime(2018, 7, 2, 16))["policy_pending_count"], 0.0)
        self.assertEqual(values(datetime(2018, 7, 3, 16))["policy_pending_count"], 1.0)

    def test_a_register_that_leaks_is_refused_by_the_explicit_guard(self):
        everything = lambda register, as_of: policy_events.PolicyState(as_of, tuple(register), ())  # noqa: E731
        with mock.patch.object(policy_features, "policy_state", everything):
            with self.assertRaises(LookAheadError):
                values(datetime(2018, 1, 1, 16))

    def test_the_real_register_columns_do_not_move_when_a_later_entry_is_removed(self):
        register = policy_events.load_register()
        as_of = datetime(2020, 3, 13, 16)
        kept = tuple(e for e in register if e.announced_at <= as_of)
        self.assertLess(len(kept), len(register))
        self.assertEqual(values(as_of, register), values(as_of, kept))


class PanelTests(unittest.TestCase):
    def rows(self):
        return [DailyObservation(date(2018, 7, 9) + timedelta(days=i), {"sofr": 1.9}) for i in range(3)]

    def test_columns_are_added_per_row_at_its_own_instant(self):
        out = policy_features.add_columns(self.rows(), REGISTER)
        self.assertEqual(len(out), 3)
        for row in out:
            self.assertEqual(row.values["sofr"], 1.9)
            expected = values(datetime.combine(row.date, time(16)))
            self.assertEqual({c: row.values[c] for c in policy_features.COLUMNS}, expected)

    def test_a_row_does_not_depend_on_the_rows_after_it(self):
        rows = self.rows()
        self.assertEqual(
            policy_features.add_columns(rows, REGISTER)[0].values, policy_features.add_columns(rows[:1], REGISTER)[0].values
        )

    def test_the_decision_time_moves_what_a_row_reads(self):
        row = [DailyObservation(date(2018, 6, 13), {})]
        early = policy_features.add_columns(row, REGISTER, decision_time=time(13))[0].values
        late = policy_features.add_columns(row, REGISTER, decision_time=time(16))[0].values
        self.assertNotEqual(early["policy_pending_count"], late["policy_pending_count"])


class SourceTests(unittest.TestCase):
    def test_every_column_is_a_field_of_the_declared_source(self):
        registry = measurement_fields.load_registry()
        source = registry[policy_features.SOURCE_ID]
        self.assertEqual(sorted(source["fields"]), sorted(policy_features.COLUMNS))
        self.assertEqual(sorted(policy_features.COLUMN_FIELDS), sorted(policy_features.COLUMNS))
        for column, pairs in policy_features.COLUMN_FIELDS.items():
            self.assertEqual(pairs, ((policy_features.SOURCE_ID, column),))

    def test_the_source_is_off_in_the_published_registry_and_feature_map(self):
        from repo_model import contract

        published = json.loads((ROOT / "metadata" / "sources.json").read_text())
        self.assertNotIn(policy_features.SOURCE_ID, published)
        for column in policy_features.COLUMNS:
            self.assertNotIn(column, contract.FEATURE_FIELDS)

    def test_the_source_is_available_at_the_decision_instant_of_its_own_row(self):
        lag = measurement_fields.load_registry()[policy_features.SOURCE_ID]["release_lag"]
        self.assertEqual((lag["days"], lag["available_time"], lag["timezone"]), (0, "16:00", "America/New_York"))


JUDGE = {**json.loads((ROOT / "metadata" / "pressure_judge.json").read_text()), "candidates": dict(pj.load_declaration().candidates)}
DECLARED = json.loads(DECLARATION.read_text())


def _script():
    import importlib.util

    spec = importlib.util.spec_from_file_location("policy_features_script", ROOT / "scripts" / "policy_features.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeclarationTests(unittest.TestCase):
    def test_the_declared_columns_are_the_modules(self):
        self.assertEqual(DECLARED["policy_columns"], list(policy_features.COLUMNS))

    def test_every_candidate_and_control_is_declared_to_the_judge_in_its_judged_form(self):
        for name, spec in DECLARED["candidates"].items():
            entry = JUDGE["candidates"][name + DECLARED["judged_form"]]
            self.assertEqual(entry["role"], "candidate")
            self.assertEqual(spec["policy"], name.endswith("_policy"))
            if spec["policy"]:
                self.assertEqual(entry["track"], spec["track"])

    def test_the_judge_lists_the_features_the_script_reads_at_horizon_one(self):
        script = _script()
        for name, spec in DECLARED["candidates"].items():
            read, _optional = script.features_of(DECLARED, spec, 1)
            self.assertEqual(list(read), JUDGE["candidates"][name + DECLARED["judged_form"]]["features"], name)

    def test_a_policy_candidate_is_its_control_plus_the_register_columns(self):
        script = _script()
        for name, spec in DECLARED["candidates"].items():
            if not spec["policy"]:
                continue
            control = DECLARED["candidates"][name[: -len("_policy")]]
            for h in range(1, 6):
                with_register, _ = script.features_of(DECLARED, spec, h)
                without, _ = script.features_of(DECLARED, control, h)
                self.assertEqual(with_register, without + tuple(policy_features.COLUMNS))

    def test_the_settlement_column_leaves_at_horizon_two_or_more_and_the_register_stays(self):
        script = _script()
        for spec in DECLARED["candidates"].values():
            self.assertIn("treasury_settlement", script.features_of(DECLARED, spec, 1)[0])
            for h in range(2, 6):
                read = script.features_of(DECLARED, spec, h)[0]
                self.assertNotIn("treasury_settlement", read)
                self.assertEqual(spec["policy"], "policy_qt_in_force" in read)

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertEqual(DECLARED["scoring"]["last_day"], JUDGE["scoring"]["last_day"])
        self.assertEqual(DECLARED["horizons"], JUDGE["horizons"])
        self.assertEqual(DECLARED["thresholds_bp"], JUDGE["thresholds_bp"])

    def test_the_controls_are_the_rows_the_best_rule_names_in_the_tracks_tables(self):
        for track, name in (("docs/pivot/judge-amendment-result.md", "rare_gbm_balanced_bootstrap"),
                            ("docs/pivot/onset-classifier-result.md", "onset_logistic")):
            self.assertEqual(DECLARED["candidates"][name]["role"], "control")
            self.assertIn(name + "+recalibrated", (ROOT / track).read_text())


if __name__ == "__main__":
    unittest.main()
