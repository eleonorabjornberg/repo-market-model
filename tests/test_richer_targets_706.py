"""H9 step 2: the choice of targets and the label swap (#706).

`choose_targets` applies Eleonora's rule of 13 October 2026 (comment 6149435134 on #639) to step 1's tables; `target_fields` and
`as_target` let #634's model class forecast a richer target in place of SOFR - IORB while the as-of rule reads it under its own
sources. Everything here is a scratch input: nothing joins a published declaration.
"""

from __future__ import annotations

import unittest
from datetime import date, time, timedelta
from types import MappingProxyType
from unittest import mock

from repo_model import contract, measurement_fields, richer_targets
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

REGISTRY = measurement_fields.load_registry()


def weekdays(start: date, count: int):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def screen(**targets):
    """A step 1 screen holding, per target: overlap rho, onsets, the two state AUCs and the lead-1 benchmark CRPS."""

    out = {"overlap": {}, "lead": {"pre_onset": {}}, "forecastability": {}}
    for name, (rho, onsets, ample, scarce, b1, b2) in targets.items():
        out["overlap"][name] = {"all:level": {"rho": rho}}
        out["lead"]["pre_onset"][name] = {
            "all": {"onsets": onsets},
            "regime:ample": {"auc": ample},
            "regime:scarce": {"auc": scarce},
        }
        out["forecastability"][name] = {"1": {"all": {"b1": b1, "b2": b2}}}
    return out


class ChoiceTests(unittest.TestCase):
    def test_a_target_at_the_overlap_limit_in_either_direction_is_dropped(self):
        result = richer_targets.choose_targets(
            screen(
                up=(0.8, 26, 0.9, 0.9, 1.0, 1.0),
                down=(-0.8, 26, 0.9, 0.9, 1.0, 1.0),
                kept=(0.79, 26, 0.5, 0.5, 1.0, 1.0),
            )
        )
        self.assertEqual(result["chosen"], ["kept"])
        self.assertEqual(result["dropped"]["up"][0], "overlap")
        self.assertEqual(result["dropped"]["down"][0], "overlap")

    def test_a_target_with_fewer_than_fifteen_onsets_is_dropped(self):
        result = richer_targets.choose_targets(
            screen(few=(0.0, 14, 0.9, 0.9, 1.0, 1.0), enough=(0.0, 15, 0.5, 0.5, 1.0, 1.0))
        )
        self.assertEqual(result["chosen"], ["enough"])
        self.assertEqual(result["dropped"]["few"][0], "onsets")

    def test_the_rest_are_ranked_by_the_state_averaged_auc_and_the_top_three_are_taken(self):
        result = richer_targets.choose_targets(
            screen(
                a=(0.0, 26, 0.9, 0.3, 1.0, 1.0),  # 0.60
                b=(0.0, 26, 0.5, 0.5, 1.0, 1.0),  # 0.50
                c=(0.0, 26, 0.7, 0.6, 1.0, 1.0),  # 0.65
                d=(0.0, 26, 0.4, 0.4, 1.0, 1.0),  # 0.40
            )
        )
        self.assertEqual(result["chosen"], ["c", "a", "b"])
        self.assertEqual([row["target"] for row in result["ranking"]], ["c", "a", "b", "d"])

    def test_a_tie_in_the_auc_goes_to_the_larger_benchmark_skill(self):
        # `x`: B1 beats B2 by 10%; `y`: B2 beats B1 by 30% (the larger of the two skills is read)
        result = richer_targets.choose_targets(
            screen(x=(0.0, 26, 0.6, 0.6, 0.9, 1.0), y=(0.0, 26, 0.6, 0.6, 1.0, 0.7), z=(0.0, 26, 0.7, 0.7, 1.0, 1.0)),
            take=2,
        )
        self.assertEqual(result["chosen"], ["z", "y"])

    def test_fewer_than_three_survivors_are_all_taken(self):
        result = richer_targets.choose_targets(
            screen(a=(0.0, 26, 0.5, 0.5, 1.0, 1.0), b=(0.9, 26, 0.5, 0.5, 1.0, 1.0))
        )
        self.assertEqual(result["chosen"], ["a"])
        self.assertTrue(result["fewer_than_requested"])

    def test_a_missing_figure_is_an_error_not_a_drop(self):
        broken = screen(a=(0.0, 26, 0.5, 0.5, 1.0, 1.0))
        del broken["lead"]["pre_onset"]["a"]["regime:scarce"]
        with self.assertRaises(ValueError):
            richer_targets.choose_targets(broken)


class TargetFieldsTests(unittest.TestCase):
    def test_each_chosen_kind_has_its_own_sources_and_none_of_iorbs(self):
        for column in ("sofr_dispersion_bps", "tgcr_dispersion_bps", "bgcr_dispersion_bps", "on_rrp_change_bn"):
            fields = richer_targets.target_fields(column)
            self.assertTrue(fields)
            self.assertFalse(set(fields) & set(contract.FEATURE_FIELDS["iorb"]))

    def test_an_unknown_target_is_refused(self):
        with self.assertRaises(ValueError):
            richer_targets.target_fields("spread_bps")


class AsTargetTests(unittest.TestCase):
    def rows(self, count=10):
        out = []
        for i, day in enumerate(weekdays(date(2024, 3, 4), count)):
            out.append(
                DailyObservation(day, {"sofr": 5.35, "iorb": 5.40, "sofr_p99": 5.5, "sofr_p1": 5.3, "on_rrp_change_bn": float(i)})
            )
        return out

    def test_the_target_column_is_what_the_model_reads_as_the_spread(self):
        swapped = richer_targets.as_target(self.rows(), "on_rrp_change_bn")
        for r, i in zip(swapped, range(10)):
            self.assertAlmostEqual(r.spread_bps, float(i), places=9)
        self.assertTrue(all(r.values["iorb"] == 0.0 for r in swapped))  # no leg of the real spread is a carrier of the label

    def test_a_missing_target_value_is_an_error(self):
        rows = self.rows()
        rows[3] = DailyObservation(rows[3].date, {**rows[3].values, "on_rrp_change_bn": None})
        with self.assertRaises(ValueError):
            richer_targets.as_target(rows, "on_rrp_change_bn")


class SwappedAvailabilityTests(unittest.TestCase):
    """The swapped target is read under its own sources' release lag, not SOFR's (#706).

    A registry in which `nyfed_sofr` is released five business days after its reference date and the ON RRP operation
    results one business day after: with the label swapped to the ON RRP change, the model's target (and its lag, `spread_bps`)
    must be read from the row the ON RRP results allow, not from five rows back.

    Recorded mutation (CLAUDE.md), 14 October 2026, in a disposable copy: `src/repo_model/richer_targets.py`,
    `swap_target_fields`, `{"sofr": fields, "iorb": fields}` mutated to `{"sofr": contract.FEATURE_FIELDS["sofr"], "iorb":
    contract.FEATURE_FIELDS["sofr"]}` (the swap would leave the label under SOFR's sources). `test_the_swapped_label_is_read_at_its_own_lag` then fails with `AssertionError`
    (`53 != 57`: the ON RRP change is read five rows further back than its own lag allows;
    `test_the_swap_is_gone_outside_the_context` fails with it).
    """

    DATES = weekdays(date(2024, 3, 4), 60)
    DECISION = time(16, 0)

    def registry(self):
        registry = {name: dict(spec) for name, spec in REGISTRY.items()}
        slow = dict(registry["nyfed_sofr"])
        slow["release_lag"] = {**slow["release_lag"], "days": 5}
        registry["nyfed_sofr"] = slow
        return registry

    def read_rows(self, column):
        with richer_targets.swap_target_fields(column):
            rule = InformationRule(self.registry(), ("spread_bps",), decision_time=self.DECISION, horizon=1)
            scored = len(self.DATES) - 1
            info = rule.information_set(self.DATES, scored)
            rule.check(self.DATES, info)
            return scored, {r.feature: r.row for r in info.reads}

    def test_the_swapped_label_is_read_at_its_own_lag(self):
        scored, swapped = self.read_rows("on_rrp_change_bn")
        _scored, own = self.read_rows("sofr_dispersion_bps")
        self.assertEqual(swapped["spread_bps"], scored - 2)  # the registry declares a result public at 16:00 the next business day
        self.assertLessEqual(own["spread_bps"], scored - 1 - 5)  # SOFR's percentiles wait out the registry's five days

    def test_the_swap_is_gone_outside_the_context(self):
        before = contract.FEATURE_FIELDS["sofr"]
        with richer_targets.swap_target_fields("on_rrp_change_bn"):
            self.assertNotEqual(contract.FEATURE_FIELDS["sofr"], before)
        self.assertEqual(contract.FEATURE_FIELDS["sofr"], before)

    def test_a_row_forced_past_the_decision_is_refused(self):
        with richer_targets.swap_target_fields("sofr_dispersion_bps"):
            rule = InformationRule(self.registry(), ("spread_bps",), decision_time=self.DECISION, horizon=1)
            scored = len(self.DATES) - 1
            info = rule.information_set(self.DATES, scored)
            forced = info._replace(reads=tuple(r._replace(row=scored - 1) if r.feature == "spread_bps" else r for r in info.reads))
            with self.assertRaises(LookAheadError):
                rule.check(self.DATES, forced)


if __name__ == "__main__":
    unittest.main()
