"""Group-conditional recalibration of a pressure probability (#380, track C of #374).

`group_calibration` recalibrates a forecast walk-forward like
`probability_calibration`, but the curve may depend on the day's group (the
reserve-scarcity state band and the pressure-day type, both read as of the
decision instant): `group` fits a Platt curve on the group's own earlier pairs
and falls back to the pooled curve when the group is thin; `weighted` fits one
Platt curve on every earlier pair, weighting the target group's pairs more
(a regime-weighted calibration after Barber et al., 2023).

The guard is the one `probability_calibration.fit` has: no curve sees an
outcome after its fitting date.
"""

from __future__ import annotations

import random
import unittest
from datetime import date, timedelta

from repo_model import group_calibration as gc, probability_calibration as pc
from repo_model.splits import LookAheadError


def _series(count=900, seed=11, block=21, horizon=1):
    rng = random.Random(seed)
    start = date(2018, 1, 1)
    dates = [start + timedelta(days=k) for k in range(count)]
    train_ends = [dates[(k // block) * block] - timedelta(days=horizon) for k in range(count)]
    groups = ["scarce|scheduled" if k % 10 == 0 else "ample|ordinary" for k in range(count)]
    forecasts, outcomes = [], []
    for g in groups:
        p = min(0.95, max(0.01, rng.betavariate(0.6, 4.0)))
        # The scarce group's outcomes run far above the forecast: a pooled
        # curve cannot fix both groups, a group-conditional one can.
        q = min(0.99, p * 3.0) if g.startswith("scarce") else p * 0.5
        forecasts.append(p)
        outcomes.append(1 if rng.random() < q else 0)
    return dates, train_ends, forecasts, outcomes, groups


class GroupLabelTests(unittest.TestCase):
    def test_label_is_state_band_by_day_type(self):
        self.assertEqual(gc.group_label(0, "ordinary"), "ample|ordinary")
        self.assertEqual(gc.group_label(1, "month_end"), "ample|scheduled")
        self.assertEqual(gc.group_label(2, "ordinary"), "scarce|ordinary")
        self.assertEqual(gc.group_label(3, "quarter_end"), "scarce|scheduled")
        self.assertEqual(gc.group_label(None, "ordinary"), "unknown|ordinary")

    def test_label_refuses_a_state_outside_zero_to_three(self):
        with self.assertRaises(ValueError):
            gc.group_label(4, "ordinary")


class ScarcityStateLabelTests(unittest.TestCase):
    """#515: the as-of scarcity state as a group, in place of the hindsight regime."""

    def test_a_state_is_its_digit_and_no_state_is_unknown(self):
        self.assertEqual([gc.scarcity_state_label(s) for s in (0, 1.0, 2, 3.0)], ["0", "1", "2", "3"])
        self.assertEqual(gc.scarcity_state_label(None), "unknown")

    def test_a_state_outside_zero_to_three_is_refused(self):
        for bad in (-1, 4, 1.5):
            with self.assertRaises(ValueError):
                gc.scarcity_state_label(bad)


class LeakageGuardTests(unittest.TestCase):
    """A group curve never sees an outcome after its fitting date.

    Recorded mutation (#380): in `group_calibration.require_observable`, the guard
    line `if late:` mutated to `if False:`. `test_a_late_pair_is_refused` then
    failed with `AssertionError: LookAheadError not raised` for both modes.
    """

    def test_a_late_pair_is_refused(self):
        dates, _, forecasts, outcomes, groups = _series(400)
        fitted_at = dates[299]
        pairs = list(zip(dates[:301], forecasts[:301], outcomes[:301], groups[:301]))
        for mode in gc.MODES:
            with self.subTest(mode=mode):
                with self.assertRaises(LookAheadError):
                    gc.fit(mode, pairs, fitted_at, target_group="ample|ordinary")

    def test_pairs_up_to_the_fitting_date_are_accepted(self):
        dates, _, forecasts, outcomes, groups = _series(400)
        pairs = list(zip(dates[:300], forecasts[:300], outcomes[:300], groups[:300]))
        for mode in gc.MODES:
            with self.subTest(mode=mode):
                curve = gc.fit(mode, pairs, dates[299], target_group="ample|ordinary")
                self.assertTrue(0.0 < curve(0.3) < 1.0)

    def test_walk_forward_uses_only_observable_pairs(self):
        """Changing an outcome the block cannot yet see leaves its forecasts unchanged."""

        dates, ends, forecasts, outcomes, groups = _series()
        for mode in gc.MODES:
            base = gc.walk_forward(mode, forecasts, outcomes, dates, ends, groups)
            start = next(s for s, _, _ in pc.blocks(dates, ends) if s > 400)
            stop = next(e for s, e, _ in pc.blocks(dates, ends) if s == start)
            altered = list(outcomes)
            for k in range(start, len(outcomes)):
                altered[k] = 1 - altered[k]
            again = gc.walk_forward(mode, forecasts, altered, dates, ends, groups)
            self.assertEqual(base[:stop], again[:stop], mode)


class WalkForwardTests(unittest.TestCase):
    def test_identity_before_the_pooled_gate(self):
        dates, ends, forecasts, outcomes, groups = _series()
        for mode in gc.MODES:
            out = gc.walk_forward(mode, forecasts, outcomes, dates, ends, groups)
            first = next(s for s, _, _ in pc.blocks(dates, ends)
                         if len(pc.past_positions(dates, ends, s)) >= pc.MINIMUM_PAIRS)
            self.assertEqual(out[:first], tuple(forecasts[:first]))

    def test_group_mode_falls_back_to_pooled_for_a_thin_group(self):
        dates, ends, forecasts, outcomes, groups = _series()
        groups = ["rare|ordinary" if k in (500, 700) else g for k, g in enumerate(groups)]
        pooled = pc.walk_forward("platt", forecasts, outcomes, dates, ends)
        out = gc.walk_forward("group", forecasts, outcomes, dates, ends, groups)
        self.assertEqual(out[500], pooled[500])
        self.assertEqual(out[700], pooled[700])

    def test_group_mode_beats_pooled_when_groups_miscalibrate_in_opposite_ways(self):
        dates, ends, forecasts, outcomes, groups = _series(1800)
        pooled = pc.walk_forward("platt", forecasts, outcomes, dates, ends)
        grouped = gc.walk_forward("group", forecasts, outcomes, dates, ends, groups)
        scored = range(1000, 1800)

        def brier(column):
            return sum((column[k] - outcomes[k]) ** 2 for k in scored) / len(scored)

        self.assertLess(brier(grouped), brier(pooled))

    def test_weighted_mode_with_equal_weights_is_pooled_platt(self):
        dates, ends, forecasts, outcomes, groups = _series()
        pairs = list(zip(dates[:600], forecasts[:600], outcomes[:600], groups[:600]))
        curve = gc.fit("weighted", pairs, dates[599], target_group="ample|ordinary", other_weight=1.0)
        pooled = pc.fit("platt", [(d, p, y) for d, p, y, _ in pairs], dates[599])
        for p in (0.02, 0.1, 0.4, 0.8):
            self.assertAlmostEqual(curve(p), pooled(p), places=4)

    def test_weighted_mode_leans_toward_the_target_group(self):
        dates, ends, forecasts, outcomes, groups = _series(1500)
        pairs = list(zip(dates[:1400], forecasts[:1400], outcomes[:1400], groups[:1400]))
        scarce = gc.fit("weighted", pairs, dates[1399], target_group="scarce|scheduled")
        ample = gc.fit("weighted", pairs, dates[1399], target_group="ample|ordinary")
        self.assertGreater(scarce(0.3), ample(0.3))

    def test_unknown_mode_and_length_mismatch_are_refused(self):
        dates, ends, forecasts, outcomes, groups = _series(300)
        with self.assertRaises(ValueError):
            gc.walk_forward("magic", forecasts, outcomes, dates, ends, groups)
        with self.assertRaises(ValueError):
            gc.walk_forward("group", forecasts, outcomes, dates, ends, groups[:-1])

    def test_curves_stay_in_the_unit_interval(self):
        dates, ends, forecasts, outcomes, groups = _series()
        for mode in gc.MODES:
            out = gc.walk_forward(mode, forecasts, outcomes, dates, ends, groups)
            self.assertTrue(all(0.0 <= p <= 1.0 for p in out))


def _regime_series(count=1000, seed=5, block=21):
    """Daily pairs from 2018-01-01 whose forecast is too low in the first regime and too high in the second."""

    rng = random.Random(seed)
    start = date(2018, 1, 1)
    dates = [start + timedelta(days=k) for k in range(count)]
    train_ends = [dates[(k // block) * block] - timedelta(days=1) for k in range(count)]
    forecasts, outcomes = [], []
    for day in dates:
        p = min(0.95, max(0.01, rng.betavariate(0.7, 5.0)))
        q = min(0.99, p * 3.0) if day.year < 2020 else p * 0.3
        forecasts.append(p)
        outcomes.append(1 if rng.random() < q else 0)
    return dates, train_ends, forecasts, outcomes


def _splits():
    from repo_model.evaluation_splits import load_split_declaration
    from pathlib import Path

    return load_split_declaration(Path(__file__).parents[1] / "metadata" / "evaluation_splits.json")


class RegimeRecalibrationTests(unittest.TestCase):
    """The per-regime remedy of #471: a Platt curve per declared regime, from that regime's earlier pairs only.

    The regime of a day is read off the declared calendar (`metadata/evaluation_splits.json`), so it is
    known at the decision instant. A label that is not the calendar's (one assigned from realised
    outcomes) is a look-ahead and is refused.

    Recorded mutation (#471): in `group_calibration.require_regimes_asof`, the guard line
    `if wrong:` mutated to `if False:`. `test_a_label_not_read_from_the_calendar_is_refused` then
    failed with `AssertionError: LookAheadError not raised`.
    """

    def test_a_label_not_read_from_the_calendar_is_refused(self):
        dates, train_ends, forecasts, outcomes = _regime_series(400)
        by_outcome = ["hit" if y else "calm" for y in outcomes]
        with self.assertRaises(LookAheadError):
            gc.regime_walk_forward(forecasts, outcomes, dates, train_ends, by_outcome, _splits())

    def test_calendar_labels_are_accepted(self):
        dates, train_ends, forecasts, outcomes = _regime_series(400)
        splits = _splits()
        labels = [splits.regime(day) for day in dates]
        column = gc.regime_walk_forward(forecasts, outcomes, dates, train_ends, labels, splits)
        self.assertEqual(len(column), len(forecasts))

    def test_a_block_does_not_move_when_later_outcomes_change(self):
        dates, train_ends, forecasts, outcomes = _regime_series(900)
        splits = _splits()
        labels = [splits.regime(day) for day in dates]
        base = gc.regime_walk_forward(forecasts, outcomes, dates, train_ends, labels, splits)
        cut = 600
        flipped = [y if k < cut else 1 - y for k, y in enumerate(outcomes)]
        moved = gc.regime_walk_forward(forecasts, flipped, dates, train_ends, labels, splits)
        # Outcomes from index `cut` on are unobservable to every block starting at or before it.
        first_late_block = next(k for k in range(cut, len(dates)) if train_ends[k] >= dates[cut])
        self.assertEqual(base[:first_late_block], moved[:first_late_block])

    def test_a_new_regime_starts_on_the_pooled_curve(self):
        dates, train_ends, forecasts, outcomes = _regime_series(1000)
        splits = _splits()
        labels = [splits.regime(day) for day in dates]
        regime = gc.regime_walk_forward(forecasts, outcomes, dates, train_ends, labels, splits)
        pooled = pc.walk_forward("platt", forecasts, outcomes, dates, train_ends)
        first_2020 = next(k for k, day in enumerate(dates) if day.year == 2020)
        self.assertEqual(regime[first_2020], pooled[first_2020])

    def test_a_regime_curve_beats_pooled_where_regimes_miscalibrate_oppositely(self):
        dates, train_ends, forecasts, outcomes = _regime_series(1000)
        splits = _splits()
        labels = [splits.regime(day) for day in dates]
        regime = gc.regime_walk_forward(forecasts, outcomes, dates, train_ends, labels, splits)
        pooled = pc.walk_forward("platt", forecasts, outcomes, dates, train_ends)
        late = [k for k, day in enumerate(dates) if day >= date(2020, 7, 1)]

        def brier(column):
            return sum((column[k] - outcomes[k]) ** 2 for k in late) / len(late)

        self.assertLess(brier(regime), brier(pooled))

    def test_label_and_length_mismatches_are_refused(self):
        dates, train_ends, forecasts, outcomes = _regime_series(300)
        with self.assertRaises(ValueError):
            gc.regime_walk_forward(forecasts, outcomes, dates, train_ends, ["2018-19"], _splits())


class DeclarationTests(unittest.TestCase):
    def test_declaration_names_every_constant(self):
        d = gc.declaration()
        for key in ("modes", "group_minimum_pairs", "group_minimum_events", "other_group_weight", "groups"):
            self.assertIn(key, d)


class JudgeDeclarationTests(unittest.TestCase):
    """The track's candidates are declared in the judge's file, and none declares a cut-off: the judge's rule chooses it from the refit's training window."""

    def test_every_recalibration_candidate_is_declared_before_scoring(self):
        from repo_model import pressure_judge as pj

        declaration = pj.load_declaration()
        for name in ("recal_isotonic", "recal_platt", "recal_platt_group", "recal_platt_weighted"):
            with self.subTest(name=name):
                self.assertEqual(declaration.candidates[name]["role"], "candidate")
                self.assertNotIn("cutoffs", declaration.candidates[name])


class RegimeDeclarationTests(unittest.TestCase):
    """#471's remedy is declared in `metadata/regime_recalibration.json` and one candidate file per base, before any score."""

    def test_every_base_has_a_recalibrated_candidate_and_no_cutoff(self):
        import json
        from pathlib import Path

        from repo_model import pressure_judge as pj

        root = Path(__file__).parents[1] / "metadata"
        declared = json.loads((root / "regime_recalibration.json").read_text())
        risk = json.loads((root / "risk_date_severity.json").read_text())
        suffix = declared["remedy"]["judged_form"]
        declaration = pj.load_declaration()
        self.assertEqual(len(declared["bases"]), 5)
        for base in declared["bases"]:
            with self.subTest(base=base):
                self.assertIn(base, risk["candidates"])
                entry = declaration.candidates[base + suffix]
                self.assertEqual(entry["role"], "candidate")
                self.assertNotIn("cutoffs", entry)
                self.assertEqual(entry["features"], declaration.candidates[base]["features"])


if __name__ == "__main__":
    unittest.main()
