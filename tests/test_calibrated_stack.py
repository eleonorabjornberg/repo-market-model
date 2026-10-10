"""The calibrated stack of the five tier-1 passers (#475, a track of #374): `repo_model.calibrated_stack`.

What is covered:

* `FitTests` -- `stacking.fit_logit_stack` with a per-column prior: the regime columns are pulled to 0, the member
  columns to 1/M, and the default (no prior) is the equal-weight pool as before.
* `StackTests` -- the walk-forward stack and its isotonic recalibration: a forecast on a block reads no outcome of
  that block, of an earlier block's days inside the horizon gap, or of any later day; a stack and a recalibration
  fitted on out-of-sample base forecasts only (the recalibration on the stack's walk-forward probabilities, not an
  in-sample fit); the equal-weight fallback and the identity recalibration while the window is thin.
* `DeclarationTests` -- the declaration on disk is the one the code reads, and its members and candidates are
  declared in the judge's candidate directory.

**Recorded mutations** (disposable copy of the tree, `PYTHONDONTWRITEBYTECODE=1`, `test_calibrated_stack` run
alone, each mutation confirmed applied by `grep` and restored before the next):

1. `calibrated_stack`: change `pairs = [(days[k], stacked[k], outcomes[k]) for k in window]` to
   `... for k in range(start)]` (the recalibration reads every earlier-block day, including the days inside the
   gap whose outcome was not yet public). `pc.fit` raises `LookAheadError` ("a isotonic curve fitted at
   2020-08-07 was handed the outcome of 2020-08-10"), and seven tests error with it, among them
   `StackTests.test_the_recalibration_reads_no_outcome_inside_the_gap`.
2. `calibrated_stack`: change `training_end = stacking.training_end_of(...)` to the block's own first day
   (`training_end = days[start]`) so the isotonic guard no longer stops a gap day. With mutation 1 applied as well,
   the guard no longer fires and `StackTests.test_the_recalibration_reads_no_outcome_inside_the_gap` fails with
   `AssertionError` (the block's probabilities moved when a gap day's outcome was flipped).
3. `calibrated_stack`: change `window = stacking.training_window(days, calendar, start=start, horizon=horizon)` to
   `window = list(range(start))` (every earlier-block day, gap included). The isotonic step still stops it:
   seven tests error with `LookAheadError` ("a isotonic curve fitted at 2020-07-09 was handed the outcome of
   2020-07-10"), among them `StackTests.test_the_stack_reads_no_outcome_inside_the_gap`. The logistic fit has no
   guard of its own beyond `stacking.training_window`, so this mutation is killed by the recalibration's guard.
"""

from __future__ import annotations

import json
import math
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import calibrated_stack as cs
from repo_model import stacking as st
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
LABELS = ("a", "b", "c")


def _sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def _business_days(count, start=date(2020, 1, 6)):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def _world(n=420, seed=3):
    rng = random.Random(seed)
    calendar = _business_days(n + 30)
    days = tuple(calendar[10 : 10 + n])
    outcomes, members = [], {"m1": [], "m2": []}
    regimes = []
    for k in range(n):
        latent = rng.uniform(-3.5, 0.5)
        y = 1 if rng.random() < _sigmoid(latent) else 0
        outcomes.append(y)
        for name in members:
            members[name].append(min(max(_sigmoid(latent + rng.gauss(0, 0.8)), 0.001), 0.999))
        regimes.append(LABELS[(k * len(LABELS)) // n])
    return calendar, days, members, regimes, outcomes


def _run(world, **overrides):
    calendar, days, members, regimes, outcomes = world
    args = dict(
        regime_labels=LABELS, horizon=2, step=21, ridge=1.0, clip=1e-4,
        fallback=st.Fallback(minimum_days=126, minimum_each_class=5),
    )
    args.update(overrides)
    return cs.calibrated_stack(days, calendar, members, regimes, outcomes, **args)


class FitTests(unittest.TestCase):
    def test_the_regime_columns_are_pulled_to_zero(self):
        rng = random.Random(4)
        rows = [(rng.uniform(-3, 1), 1.0 if rng.random() < 0.5 else 0.0) for _ in range(400)]
        y = [1 if rng.random() < _sigmoid(a) else 0 for a, _ in rows]
        _, tight = st.fit_logit_stack(rows, y, ridge=1e6, prior=[1.0, 0.0])
        self.assertAlmostEqual(tight[0], 1.0, delta=1e-3)
        self.assertAlmostEqual(tight[1], 0.0, delta=1e-3)

    def test_without_a_prior_the_pull_is_towards_the_equal_weight_pool(self):
        rows = [(0.0, 1.0), (1.0, -1.0), (-1.0, 0.5), (0.5, 0.5)] * 30
        y = [0, 1, 0, 1] * 30
        _, weights = st.fit_logit_stack(rows, y, ridge=1e6)
        for weight in weights:
            self.assertAlmostEqual(weight, 0.5, delta=1e-3)

    def test_a_prior_of_the_wrong_length_is_refused(self):
        with self.assertRaises(ValueError):
            st.fit_logit_stack([(0.0, 0.0)], [1], ridge=1.0, prior=[0.5])


class RegimeTests(unittest.TestCase):
    def test_one_indicator_per_label(self):
        self.assertEqual(cs.regime_indicators(LABELS, ["b", "a"]), [(0.0, 1.0, 0.0), (1.0, 0.0, 0.0)])

    def test_an_undeclared_regime_is_refused(self):
        with self.assertRaises(ValueError):
            cs.regime_indicators(LABELS, ["z"])


class NoRegimeTests(unittest.TestCase):
    """#515: the stack with its regime term removed (`regime_labels=()`), the control for the hindsight labels."""

    def test_no_labels_means_no_indicator_and_no_check_of_the_regimes(self):
        self.assertEqual(cs.regime_indicators((), ["anything", "else"]), [(), ()])

    def test_the_stack_without_labels_does_not_read_the_regimes(self):
        world = _world()
        calendar, days, members, regimes, outcomes = world
        flipped = [LABELS[(LABELS.index(r) + 1) % len(LABELS)] for r in regimes]
        a = _run(world, regime_labels=())
        b = _run((calendar, days, members, flipped, outcomes), regime_labels=())
        self.assertEqual(a.stacked, b.stacked)
        self.assertEqual(a.recalibrated, b.recalibrated)
        self.assertEqual(a.trace[-1]["regime_coefficients"], {})
        self.assertEqual(len(a.trace[-1]["weights"]), 2)

    def test_the_stack_with_labels_does_read_them(self):
        world = _world()
        calendar, days, members, regimes, outcomes = world
        flipped = [LABELS[(LABELS.index(r) + 1) % len(LABELS)] for r in regimes]
        self.assertNotEqual(_run(world).stacked, _run((calendar, days, members, flipped, outcomes)).stacked)


class RegimeTermTests(unittest.TestCase):
    """#515: the stack's regime term as declared, removed, or replaced by the as-of scarcity state."""

    class _Splits:
        def regime(self, day):
            return "a" if day.year < 2020 else "b"

    days = [date(2019, 5, 1), date(2020, 5, 1), date(2020, 5, 4)]

    def test_declared_is_the_calendars_regime_and_the_declared_labels(self):
        labels, regimes = cs.regime_term("declared", ("a", "b"), self.days, self._Splits(), {})
        self.assertEqual((labels, regimes), (("a", "b"), ["a", "b", "b"]))

    def test_none_has_no_label(self):
        labels, regimes = cs.regime_term("none", ("a", "b"), self.days, self._Splits(), {})
        self.assertEqual(labels, ())

    def test_scarcity_is_one_indicator_per_state_with_no_state_unknown(self):
        labels, regimes = cs.regime_term("scarcity", ("a", "b"), self.days, self._Splits(), {self.days[0]: 3.0, self.days[1]: 0.0})
        self.assertEqual(labels, ("0", "1", "2", "3", "unknown"))
        self.assertEqual(regimes, ["3", "0", "unknown"])

    def test_an_unknown_mode_is_refused(self):
        with self.assertRaises(ValueError):
            cs.regime_term("hindsight", ("a",), self.days, self._Splits(), {})

    def test_the_variants_are_named_for_the_judge_candidates(self):
        self.assertEqual(cs.variant_name("calibrated_stack_logistic", "declared"), "calibrated_stack_logistic")
        self.assertEqual(cs.variant_name("calibrated_stack_logistic", "none"), "calibrated_stack_logistic+no_regime")
        self.assertEqual(cs.variant_name("calibrated_stack_isotonic", "scarcity"), "calibrated_stack_isotonic+scarcity")


class HindsightEvidence(unittest.TestCase):
    """The findings recorded in `evidence/hindsight-regimes/hindsight.json` (#515)."""

    @classmethod
    def setUpClass(cls):
        path = REPO / "docs" / "pivot" / "evidence" / "hindsight-regimes" / "hindsight.json"
        cls.evidence = json.loads(path.read_text(encoding="utf-8"))

    def test_the_regime_term_is_zero_before_2020_and_the_controls_reproduce_the_stack_page(self):
        trace = self.evidence["declared_stack_regime_coefficients_h1_5bp"]
        self.assertLess(trace["largest_absolute_coefficient_before_2020"], 1e-9)
        mean = trace["mean_over_fitted_refits"]
        self.assertAlmostEqual(mean["2018-19"], 1.88, places=2)
        self.assertAlmostEqual(mean["2021-23"], -1.26, places=2)
        row = self.evidence["rows"]["calibrated_stack_logistic"]
        self.assertAlmostEqual(row["flat"]["worst_false_alarms_per_onset"], 3.88, places=2)
        self.assertAlmostEqual(row["weighted"]["worst_weighted_false_alarms_per_onset"], 2.50, places=2)

    def test_the_stacks_2019_recall_is_the_same_without_the_regime_term(self):
        rows = self.evidence["rows"]
        for kind in ("calibrated_stack_logistic", "calibrated_stack_isotonic"):
            declared = rows[kind]["flat"]["by_year"]["2019"]["onsets_flagged"]
            for suffix in ("+no_regime", "+scarcity"):
                self.assertEqual(rows[kind + suffix]["flat"]["by_year"]["2019"]["onsets_flagged"], declared)

    def test_no_form_passes_the_full_rule_and_no_2026_day_is_in_the_evidence(self):
        self.assertFalse(any(cell[rule]["passes"] for cell in self.evidence["rows"].values() for rule in ("flat", "weighted")))
        self.assertNotIn('"2026-', json.dumps(self.evidence))

    def test_the_recalibrations_weighted_tier_1_is_kept_only_with_the_declared_regime(self):
        rows = self.evidence["rows"]
        kept = {"risk_gbm_base", "risk_logistic_base", "risk_quantile_skewt_base"}
        for base in ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base"):
            self.assertEqual(rows[base + "+regime_recal"]["weighted"]["tier_1"], base in kept, base)
            self.assertFalse(rows[base + "+regime_recal_none"]["weighted"]["tier_1"], base)
            self.assertFalse(rows[base + "+regime_recal_scarcity"]["weighted"]["tier_1"], base)


class StackTests(unittest.TestCase):
    def setUp(self):
        self.world = _world()

    def test_the_first_blocks_are_the_equal_weight_pool_and_the_identity(self):
        result = _run(self.world)
        self.assertEqual(result.trace[0]["mode"], "equal")
        first = result.trace[0]
        self.assertEqual(first["regime_coefficients"], {label: 0.0 for label in LABELS})
        for k in range(21):
            self.assertEqual(result.stacked[k], result.recalibrated[k])
        later = [t for t in result.trace if t["mode"] == "fitted"]
        self.assertTrue(later)

    def test_the_recalibration_changes_the_fitted_blocks(self):
        result = _run(self.world)
        self.assertNotEqual(result.stacked[-21:], result.recalibrated[-21:])
        for p in result.recalibrated:
            self.assertTrue(1e-4 <= p <= 1 - 1e-4)

    def _flip(self, world, positions):
        calendar, days, members, regimes, outcomes = world
        flipped = list(outcomes)
        for k in positions:
            flipped[k] = 1 - flipped[k]
        return calendar, days, members, regimes, flipped

    def test_the_stack_reads_no_outcome_inside_the_gap(self):
        base = _run(self.world)
        start = 252
        gap = [start - 1, start - 2]  # inside the horizon + 1 business days before the block (h = 2)
        moved = _run(self._flip(self.world, gap))
        self.assertEqual(base.stacked[start : start + 21], moved.stacked[start : start + 21])

    def test_the_recalibration_reads_no_outcome_inside_the_gap(self):
        base = _run(self.world)
        start = 252
        moved = _run(self._flip(self.world, [start - 1, start - 2]))
        self.assertEqual(base.recalibrated[start : start + 21], moved.recalibrated[start : start + 21])

    def test_a_block_reads_no_outcome_of_its_own_or_later_days(self):
        base = _run(self.world)
        start = 252
        moved = _run(self._flip(self.world, list(range(start, start + 60))))
        self.assertEqual(base.recalibrated[: start + 21], moved.recalibrated[: start + 21])
        self.assertEqual(base.stacked[: start + 21], moved.stacked[: start + 21])

    def test_an_earlier_outcome_does_move_a_later_block(self):
        base = _run(self.world)
        moved = _run(self._flip(self.world, list(range(130, 190))))
        self.assertNotEqual(base.stacked[300:321], moved.stacked[300:321])

    def test_the_recalibration_is_fitted_on_the_stacks_walk_forward_probabilities(self):
        # Replacing the members of the *training* days by their in-sample refit would change nothing here; what
        # is checked is that the recalibrated value of a block is a step of the earlier days' stacked values.
        result = _run(self.world)
        calendar, days, members, regimes, outcomes = self.world
        start = 252
        window = st.training_window(days, calendar, start=start, horizon=2)
        steps = {round(result.stacked[k], 12) for k in window}
        self.assertTrue(steps)
        values = {round(v, 9) for v in result.recalibrated[start : start + 21]}
        self.assertTrue(all(0.0 < v < 1.0 for v in values))

    def test_a_late_pair_is_refused_by_the_isotonic_guard(self):
        from repo_model import probability_calibration as pc

        calendar = _business_days(10)
        with self.assertRaises(LookAheadError):
            pc.fit("isotonic", [(calendar[5], 0.2, 1)], calendar[3])

    def test_lengths_must_agree(self):
        calendar, days, members, regimes, outcomes = self.world
        with self.assertRaises(ValueError):
            cs.calibrated_stack(
                days, calendar, members, regimes[:-1], outcomes, regime_labels=LABELS, horizon=1, step=21,
                ridge=1.0, clip=1e-4, fallback=st.Fallback(126, 5),
            )


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_on_disk_is_the_one_the_code_reads(self):
        declaration = cs.load_declaration()
        raw = json.loads((REPO / "metadata" / "calibrated_stack.json").read_text(encoding="utf-8"))
        self.assertEqual(list(declaration.members), raw["members"])
        self.assertEqual(len(declaration.members), 5)
        self.assertEqual(declaration.thresholds, (5.0, 10.0))

    def test_the_members_and_candidates_are_declared_for_the_judge(self):
        declaration = cs.load_declaration()
        directory = REPO / "metadata" / "pressure_judge" / "candidates"
        for name in (*declaration.members, declaration.logistic, declaration.isotonic):
            self.assertTrue((directory / f"{name}.json").is_file(), name)
        for name in (declaration.logistic, declaration.isotonic):
            entry = json.loads((directory / f"{name}.json").read_text(encoding="utf-8"))
            self.assertEqual(entry["members"], list(declaration.members))

    def test_the_regime_labels_are_the_splits_labels(self):
        declaration = cs.load_declaration()
        splits = json.loads((REPO / "metadata" / "evaluation_splits.json").read_text(encoding="utf-8"))
        known = {r["label"] for r in splits["regimes"]}
        self.assertTrue(set(declaration.regime_labels) <= known)


if __name__ == "__main__":
    unittest.main()
