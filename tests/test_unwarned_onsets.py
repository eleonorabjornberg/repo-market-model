"""The diagnostic of the onsets no model warns (#560): `scripts/unwarned_onsets.py`.

Descriptive only: these tests check the readings on small series with known answers, that an
input is read as of the decision instant L days before the target day, and that a locked or
post-declared scored day is refused. They test no claim.

Recorded mutations (CLAUDE.md: a new leakage or availability guard carries one that kills it).

* The input at lead L is read as of the decision instant L scored days before the target day.
  Mutation: in `as_of_at_lead` replace `horizon=lead` with `horizon=1`; the failing test was
  `GuardTests.test_an_input_at_lead_five_is_not_read_from_the_four_days_before_the_target`, which
  raised `AssertionError` (a sentinel in a row after the lead-5 origin read back).
* `require_scored_days` is the post-mortem's (#474): a locked day, or a day after 2025-12-31, is
  refused. Mutation: in `unwarned_onsets.check_days` replace the call `pm.require_scored_days(days)`
  with `None`; the failing test was `GuardTests.test_a_day_after_the_last_scored_day_is_refused`,
  which raised `AssertionError` (`LookAheadError` not raised).
"""

from __future__ import annotations

import importlib.util
import math
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


uo = _script("unwarned_onsets")


class ZScoreTests(unittest.TestCase):
    def test_a_z_score_is_against_the_regime_mean_and_sample_sd(self):
        stats = uo.mean_sd([1.0, 2.0, 3.0, 4.0])
        self.assertAlmostEqual(stats[0], 2.5)
        self.assertAlmostEqual(stats[1], math.sqrt(5.0 / 3.0))
        self.assertAlmostEqual(uo.zscore(4.0, *stats), 1.5 / math.sqrt(5.0 / 3.0))

    def test_a_constant_input_has_no_z_score(self):
        self.assertIsNone(uo.zscore(3.0, *uo.mean_sd([3.0, 3.0, 3.0])))

    def test_a_missing_value_or_too_few_days_has_no_z_score(self):
        self.assertIsNone(uo.zscore(None, 0.0, 1.0))
        self.assertEqual(uo.mean_sd([1.0]), (None, None))
        self.assertIsNone(uo.zscore(1.0, None, None))

    def test_the_reference_days_are_the_regime_days_that_are_not_pressure(self):
        values = [1.0, 2.0, 100.0, 3.0, 50.0]
        regime = ["a", "a", "a", "b", "a"]
        pressure = [False, False, True, False, False]
        self.assertEqual(uo.reference_values(values, regime, pressure, "a"), [1.0, 2.0, 50.0])

    def test_none_values_are_left_out_of_the_reference(self):
        self.assertEqual(uo.reference_values([None, 2.0], ["a", "a"], [False, False], "a"), [2.0])


class MovesTests(unittest.TestCase):
    def test_the_largest_moves_are_by_absolute_z_and_ties_break_by_name(self):
        zs = {"c": -4.0, "a": 2.0, "b": 4.0, "d": None, "e": 0.5}
        self.assertEqual([n for n, _ in uo.largest_moves(zs, 3)], ["b", "c", "a"])
        self.assertEqual(len(uo.largest_moves(zs, 10)), 4)


class VerdictTests(unittest.TestCase):
    used = {"tgcr", "tga"}

    def _z(self, **kw):
        return {"tgcr": 0.0, "tga": 0.0, "bgcr": 0.0, **kw}

    def test_an_unused_input_over_the_bar_is_signal_public_and_unused(self):
        out = uo.verdict({1: self._z(bgcr=3.2)}, {}, self.used, {})
        self.assertEqual(out["verdict"], uo.UNUSED)
        self.assertEqual(out["named"][0][:2], ("bgcr", 1))

    def test_a_used_input_over_the_bar_is_too_weak(self):
        out = uo.verdict({2: self._z(tgcr=-3.5)}, {}, self.used, {})
        self.assertEqual(out["verdict"], uo.WEAK)

    def test_a_probability_at_half_the_cutoff_is_too_weak(self):
        out = uo.verdict({1: self._z()}, {"risk_gbm": {1: (0.10, 0.20)}}, self.used, {})
        self.assertEqual(out["verdict"], uo.WEAK)
        self.assertEqual(out["rows_near_cutoff"], ["risk_gbm"])

    def test_nothing_over_the_bar_is_no_public_signal(self):
        out = uo.verdict({1: self._z(bgcr=2.9)}, {"risk_gbm": {1: (0.09, 0.20), 2: (0.0, math.inf)}}, self.used, {})
        self.assertEqual(out["verdict"], uo.NONE)

    def test_the_announced_net_settlement_over_the_bar_counts_as_unused(self):
        out = uo.verdict({1: self._z()}, {}, self.used, {1: 3.4})
        self.assertEqual(out["verdict"], uo.UNUSED)
        self.assertEqual(out["named"][0][0], "net_settlement_ahead")

    def test_unused_outranks_too_weak(self):
        out = uo.verdict({1: self._z(bgcr=3.0, tgcr=9.0)}, {"risk_gbm": {1: (0.2, 0.2)}}, self.used, {})
        self.assertEqual(out["verdict"], uo.UNUSED)


class FamilyTests(unittest.TestCase):
    def test_a_row_belongs_to_the_family_of_the_directive_that_made_it(self):
        expect = {
            "risk_gbm": "passer", "risk_quantile_skewt_base": "passer", "risk_quantile_skewt": "other",
            "ngboost_laplace": "ngboost_laplace", "risk_gbm+hurdle_platt": "hurdle",
            "risk_logistic_base+settle+h41": "timing", "risk_gbm+h41": "timing", "structural_liquidity": "structural",
            "risk_gbm+structural": "structural", "latent_factor_logit": "stress_factor",
            "risk_gbm+latent_factor": "stress_factor", "effr_pooled": "pretraining", "risk_gbm+effr_sofr_only": "pretraining",
            "projected_reserves": "projected_reserves", "risk_gbm+projected": "projected_reserves",
            "calendar_climatology": "reference", "persistence_logistic": "reference",
            "risk_gbm+every_day+gate+h41": "other", "published_v1": "other",
        }
        for name, family in expect.items():
            self.assertEqual(uo.family(name), family, name)


class UnflaggableTests(unittest.TestCase):
    def test_cells_with_an_infinite_cutoff_are_counted_and_ranked_by_probability(self):
        cells = {"a": {1: (0.9, math.inf), 2: (0.2, 0.3)}, "b": {1: (0.95, math.inf), 2: (0.1, math.inf)}}
        count, total, top = uo.unflaggable(cells, top=2)
        self.assertEqual((count, total), (3, 4))
        self.assertEqual([(t["row"], t["lead"]) for t in top], [("b", 1), ("a", 1)])


class ShareBelowTests(unittest.TestCase):
    def test_the_share_of_others_strictly_below_the_value(self):
        self.assertEqual(uo.share_below(0.5, [0.1, 0.5, 0.9, 0.2]), 0.5)
        self.assertIsNone(uo.share_below(0.5, []))


class WarnedTests(unittest.TestCase):
    def test_an_onset_is_warned_by_a_row_that_flags_any_lead(self):
        flags = {"a": {1: [0, 0], 2: [0, 1]}, "b": {1: [0, 0], 2: [0, 0]}}
        self.assertEqual(uo.warned_by(flags, 1), ["a"])
        self.assertEqual(uo.warned_by(flags, 0), [])


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile

        from repo_model.scarcity import measurement_declaration, with_reserve_scarcity_state

        validation = _script("scarcity_validation")
        with measurement_declaration(), tempfile.TemporaryDirectory() as directory:
            build, _digest, cls.registry, cls.decision = validation.build_measurement_panel(
                ROOT / "metadata" / "sources.json", Path(directory)
            )
            cls.rows = with_reserve_scarcity_state(build.observations)

    def test_a_day_after_the_last_scored_day_is_refused(self):
        from repo_model.splits import LookAheadError

        with self.assertRaises(LookAheadError):
            uo.check_days([date(2026, 1, 5)])

    def test_an_input_the_rule_refuses_at_a_lead_is_listed_not_read(self):
        from repo_model.scarcity import measurement_declaration

        inputs = ("tgcr", "treasury_settlement")
        with measurement_declaration():
            series, unavailable = uo.as_of_available(self.rows, self.registry, [self.rows[300].date], inputs, 3)
            one, none = uo.as_of_available(self.rows, self.registry, [self.rows[300].date], inputs, 1)
        self.assertEqual(unavailable, ["treasury_settlement"])
        self.assertNotIn("treasury_settlement", series)
        self.assertIn("tgcr", series)
        self.assertEqual(none, [])
        self.assertIn("treasury_settlement", one)

    def test_an_input_at_lead_five_is_not_read_from_the_four_days_before_the_target(self):
        from repo_model.data import DailyObservation
        from repo_model.scarcity import measurement_declaration

        inputs = ("tgcr",)
        with measurement_declaration():
            days = [r.date for r in self.rows]
            target = days[300]
            clean = uo.as_of_at_lead(self.rows, self.registry, [target], inputs, 5)
            marked = []
            for k, row in enumerate(self.rows):
                if 300 - 4 <= k <= 300 + 1:
                    values = dict(row.values)
                    values["tgcr"] = 1e9
                    row = DailyObservation(row.date, values)
                marked.append(row)
            changed = uo.as_of_at_lead(marked, self.registry, [target], inputs, 5)
        self.assertEqual(changed["tgcr"][target], clean["tgcr"][target])
        self.assertNotEqual(clean["tgcr"][target], 1e9)


if __name__ == "__main__":
    unittest.main()
