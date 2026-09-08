"""Tests for `repo_model.metrics`.

Three things carry most of the weight here.

The **decomposition identity**. `score = reliability - resolution +
uncertainty` is not decoration: it is what makes the three numbers a
decomposition rather than three separately computed statistics that happen to
be printed together. It is checked on random data, on adversarial data, and on
ties, because an isotonic fit that silently mishandles tied forecasts still
produces plausible-looking components that no longer add up.

The **prohibitions**. The contract forbids fixed-bin ECE and prefers
precision-recall to ROC. A prohibition with no test is a comment, so
`FixedBinECEProhibitionTests` scans every Python source in the repository and
fails the build if the thing reappears -- and has a positive control, because a
scanner that cannot fail is worse than no scanner.

The **required arguments**. `climatology`, `block_length` and `seed` have no
defaults, for the same reason `purge` has none in `repo_model.splits`: each has
a plausible-looking default that quietly produces a wrong number rather than an
error. Their absence is asserted on the signatures, not just exercised.

Mutation record. See `MutationRecordTests` at the foot of the file for the runs;
the record is kept as executable assertions there rather than as prose here,
so that a mutation which stops being caught fails the suite instead of leaving
a paragraph that has quietly become false.
"""

import inspect
import io
import math
import random
import re
import sys
import tokenize
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import metrics
from repo_model.metrics import (
    CorpDecomposition,
    MetricError,
    average_precision,
    brier_score,
    brier_skill_score,
    corp_decomposition,
    corp_reliability_curve,
    crps_from_quantiles,
    crps_on_grid,
    log_score,
    pinball_loss,
    precision_recall_curve,
    stationary_bootstrap_indices,
    stationary_bootstrap_interval,
    threshold_weighted_crps,
)


REPO_ROOT = Path(__file__).parents[1]

# The tau family declared in AGENT_CONTRACT.md, "Decided: stress target and
# event holdouts". A fixture here, not a declaration -- see event_eval.
TAUS = (5.0, 10.0, 20.0, 50.0)


def synthetic(n=400, seed=11, base_rate=0.12):
    """A serially dependent binary series with informative forecasts.

    Stress arrives in runs, which is the property that makes the iid bootstrap
    wrong on this data, so the fixture has to have it or the bootstrap tests
    would be testing nothing.
    """

    rng = random.Random(seed)
    probabilities = []
    outcomes = []
    state = base_rate
    for _ in range(n):
        state = 0.85 * state + 0.15 * rng.random() * 2 * base_rate
        probability = min(0.98, max(0.01, state))
        probabilities.append(probability)
        outcomes.append(1 if rng.random() < probability else 0)
    return probabilities, outcomes


class BrierTests(unittest.TestCase):
    def test_a_perfect_forecast_scores_zero(self):
        self.assertEqual(brier_score([1.0, 0.0, 1.0], [1, 0, 1]), 0.0)

    def test_a_confidently_wrong_forecast_scores_one(self):
        self.assertEqual(brier_score([0.0, 1.0], [1, 0]), 1.0)

    def test_the_score_is_the_mean_squared_error(self):
        self.assertAlmostEqual(brier_score([0.3, 0.6], [0, 1]), (0.09 + 0.16) / 2)

    def test_mismatched_lengths_are_rejected(self):
        with self.assertRaisesRegex(MetricError, "against"):
            brier_score([0.1, 0.2], [1])

    def test_a_soft_label_is_rejected(self):
        """A probabilistic label would silently change what the score means."""

        with self.assertRaisesRegex(MetricError, "must be 0 or 1"):
            brier_score([0.1, 0.2], [0.5, 1])

    def test_a_probability_outside_the_unit_interval_is_rejected(self):
        with self.assertRaisesRegex(MetricError, "not a probability"):
            brier_score([1.2, 0.2], [1, 0])


class BrierSkillTests(unittest.TestCase):
    """Climatology comes from outside. That is the whole point of the argument."""

    def test_climatology_has_no_default(self):
        parameter = inspect.signature(brier_skill_score).parameters["climatology"]
        self.assertIs(
            parameter.default,
            inspect.Parameter.empty,
            msg="climatology acquired a default; estimating it from the scored "
            "rows is a learned parameter fitted on the evaluation window",
        )

    def test_omitting_climatology_is_a_type_error(self):
        with self.assertRaises(TypeError):
            brier_skill_score([0.2, 0.3], [0, 1])

    def test_forecasting_climatology_exactly_scores_zero_skill(self):
        probabilities, outcomes = synthetic()
        climatology = 0.2
        self.assertAlmostEqual(
            brier_skill_score(
                [climatology] * len(outcomes), outcomes, climatology=climatology
            ),
            0.0,
        )

    def test_a_better_forecast_scores_positive_skill(self):
        probabilities, outcomes = synthetic()
        self.assertGreater(
            brier_skill_score(probabilities, outcomes, climatology=0.2), 0.0
        )

    def test_a_degenerate_climatology_is_rejected(self):
        for bad in (0.0, 1.0, -0.1, 1.5):
            with self.subTest(climatology=bad):
                with self.assertRaisesRegex(MetricError, "climatology"):
                    brier_skill_score([0.2, 0.3], [0, 1], climatology=bad)

    def test_the_in_sample_base_rate_gives_a_different_answer(self):
        """Why the argument is required, stated as a number.

        If the in-sample base rate and an honest out-of-sample climatology gave
        the same skill score, the required argument would be ceremony. They do
        not, and the gap is the size of the error the requirement prevents.
        """

        probabilities, outcomes = synthetic()
        in_sample = sum(outcomes) / len(outcomes)
        out_of_sample = 0.20
        self.assertNotAlmostEqual(
            brier_skill_score(probabilities, outcomes, climatology=in_sample),
            brier_skill_score(probabilities, outcomes, climatology=out_of_sample),
            places=3,
        )


class BrierSkillReferenceSeriesTests(unittest.TestCase):
    """A reference refitted per fold is a series, so the argument accepts one.

    The scalar form is a caller that estimated one base rate off data it is not
    scoring. The sequence form is that same caller having refitted the estimate
    at every rolling origin, which is what
    `baseline.rolling_exceedance_backtest` does and the only shape in which
    such a reference can be passed: a rolling run's reference is not one
    number, and collapsing it to one is the asymmetric comparison that path
    exists to avoid.

    Nothing about the scalar form changed. These tests are about the second
    shape and about the one place the two deliberately differ.
    """

    def test_a_constant_series_is_the_scalar_it_repeats(self):
        """The two shapes are one rule, so they must agree where they overlap."""

        probabilities, outcomes = synthetic()
        self.assertEqual(
            brier_skill_score(probabilities, outcomes, climatology=0.2),
            brier_skill_score(
                probabilities, outcomes, climatology=[0.2] * len(outcomes)
            ),
        )

    def test_a_moving_reference_is_not_its_own_mean(self):
        """Why the shape matters, stated as a number.

        If a per-row reference and its average gave the same skill score, the
        second shape would be ceremony and hoisting the climatology out of the
        fold loop would be harmless. They do not agree: the reference enters
        the denominator paired with each row's own outcome, so a reference that
        moves *with* the base rate is a different denominator from a flat one
        at the same mean.
        """

        outcomes = [0] * 10 + [1] * 10
        probabilities = [0.1] * 10 + [0.8] * 10
        moving = [0.05] * 10 + [0.7] * 10
        flat = [sum(moving) / len(moving)] * len(moving)
        self.assertAlmostEqual(sum(moving), sum(flat), places=12)
        self.assertNotAlmostEqual(
            brier_skill_score(probabilities, outcomes, climatology=moving),
            brier_skill_score(probabilities, outcomes, climatology=flat),
            places=3,
        )

    def test_an_element_may_be_zero_where_a_scalar_may_not(self):
        """The one place the two shapes differ, and it is not an oversight.

        A scalar 0 is a declaration that the event is impossible, for which the
        reference score is 0 whenever the declaration holds. An element of 0 is
        an estimate on one fold's training rows, and
        `baseline.climatology_exceedance` returns a hard 0 above everything it
        was fitted on, deliberately -- refusing it would make the honest early
        folds of a rolling run unscoreable. The failure the scalar rule guards
        against is caught where it actually lives: on the pooled reference.
        """

        outcomes = [0, 0, 1, 1]
        reference = [0.0, 0.0, 0.4, 0.6]
        self.assertLess(brier_skill_score([0.1] * 4, outcomes, climatology=reference), 1.0)
        with self.assertRaisesRegex(MetricError, "climatology"):
            brier_skill_score([0.1] * 4, outcomes, climatology=0.0)

    def test_a_reference_that_was_right_about_every_row_has_no_denominator(self):
        with self.assertRaisesRegex(MetricError, "reference Brier score is 0"):
            brier_skill_score([0.3, 0.4], [0, 1], climatology=[0.0, 1.0])

    def test_a_reference_of_the_wrong_length_is_refused(self):
        with self.assertRaisesRegex(MetricError, "climatology values"):
            brier_skill_score([0.3, 0.4, 0.5], [0, 1, 1], climatology=[0.2, 0.2])

    def test_a_reference_element_outside_zero_to_one_is_refused(self):
        for bad in ([0.2, 1.4], [0.2, -0.1], [0.2, float("nan")], [0.2, "x"]):
            with self.subTest(reference=bad):
                with self.assertRaisesRegex(MetricError, "climatology"):
                    brier_skill_score([0.3, 0.4], [0, 1], climatology=bad)

    def test_a_string_is_not_a_reference_series(self):
        """`str` is a sequence, and iterating one would read characters."""

        with self.assertRaisesRegex(MetricError, "climatology"):
            brier_skill_score([0.3, 0.4], [0, 1], climatology="0.2")


class CorpDecompositionTests(unittest.TestCase):
    """The identity, and the properties that make the components mean something."""

    def test_the_identity_holds_on_synthetic_data(self):
        probabilities, outcomes = synthetic()
        decomposition = corp_decomposition(probabilities, outcomes)
        self.assertAlmostEqual(decomposition.identity_residual(), 0.0, places=12)

    def test_the_identity_holds_across_many_random_samples(self):
        for seed in range(20):
            with self.subTest(seed=seed):
                probabilities, outcomes = synthetic(n=120, seed=seed)
                if len(set(outcomes)) < 2:
                    continue
                decomposition = corp_decomposition(probabilities, outcomes)
                self.assertAlmostEqual(
                    decomposition.identity_residual(), 0.0, places=12
                )

    def test_the_identity_holds_when_forecasts_tie(self):
        """Ties are where an isotonic fit goes wrong quietly.

        Tied forecasts must be pooled before the fit. Without that the fit can
        order them arbitrarily, the components stop adding up, and the three
        numbers are no longer a decomposition of the score printed beside them.
        """

        probabilities = [0.3] * 20 + [0.7] * 20
        outcomes = [0] * 15 + [1] * 5 + [0] * 4 + [1] * 16
        decomposition = corp_decomposition(probabilities, outcomes)
        self.assertAlmostEqual(decomposition.identity_residual(), 0.0, places=12)

    def test_the_decomposition_does_not_depend_on_row_order(self):
        """A statistic that moved when the rows were shuffled would be a bug."""

        probabilities, outcomes = synthetic(n=150, seed=5)
        first = corp_decomposition(probabilities, outcomes)
        pairs = list(zip(probabilities, outcomes))
        random.Random(99).shuffle(pairs)
        shuffled = corp_decomposition([p for p, _ in pairs], [y for _, y in pairs])
        self.assertAlmostEqual(first.score, shuffled.score, places=12)
        self.assertAlmostEqual(first.reliability, shuffled.reliability, places=12)
        self.assertAlmostEqual(first.resolution, shuffled.resolution, places=12)

    def test_a_calibrated_forecast_has_near_zero_reliability(self):
        """Reliability is a distance from the forecast's own recalibration."""

        probabilities = [0.25] * 40 + [0.75] * 40
        outcomes = [1] * 10 + [0] * 30 + [1] * 30 + [0] * 10
        decomposition = corp_decomposition(probabilities, outcomes)
        self.assertAlmostEqual(decomposition.reliability, 0.0, places=12)

    def test_a_miscalibrated_forecast_has_positive_reliability(self):
        probabilities = [0.9] * 40 + [0.95] * 40
        outcomes = [1] * 10 + [0] * 30 + [1] * 12 + [0] * 28
        self.assertGreater(corp_decomposition(probabilities, outcomes).reliability, 0.0)

    def test_reliability_is_never_negative(self):
        """The recalibrated forecast cannot score worse than the raw one."""

        for seed in range(15):
            with self.subTest(seed=seed):
                probabilities, outcomes = synthetic(n=100, seed=seed)
                if len(set(outcomes)) < 2:
                    continue
                self.assertGreaterEqual(
                    corp_decomposition(probabilities, outcomes).reliability, -1e-12
                )

    def test_an_uninformative_forecast_has_near_zero_resolution(self):
        outcomes = [1 if index % 4 == 0 else 0 for index in range(80)]
        # Constant forecasts are refused outright, so vary them negligibly and
        # independently of the outcome: still no information about it.
        probabilities = [0.25 + 1e-9 * index for index in range(80)]
        self.assertLess(corp_decomposition(probabilities, outcomes).resolution, 0.01)

    def test_uncertainty_is_the_base_rate_brier_score(self):
        probabilities, outcomes = synthetic()
        decomposition = corp_decomposition(probabilities, outcomes)
        base_rate = sum(outcomes) / len(outcomes)
        self.assertAlmostEqual(decomposition.base_rate, base_rate, places=12)
        self.assertAlmostEqual(
            decomposition.uncertainty, base_rate * (1.0 - base_rate), places=12
        )

    def test_reliability_and_resolution_are_reported_separately(self):
        """The contract's actual requirement, as a fact about the return type."""

        fields = set(CorpDecomposition.__dataclass_fields__)
        self.assertIn("reliability", fields)
        self.assertIn("resolution", fields)
        self.assertIn("uncertainty", fields)


class DegenerateSampleTests(unittest.TestCase):
    """Where the contract's no-aggregate-on-one-event-window rule surfaces."""

    def test_a_single_outcome_class_is_refused(self):
        with self.assertRaisesRegex(MetricError, "degenerate on a single-class"):
            corp_decomposition([0.1, 0.4, 0.8], [1, 1, 1])

    def test_the_refusal_points_at_the_event_window_rule(self):
        with self.assertRaisesRegex(MetricError, "exceedance curve and realized path"):
            corp_decomposition([0.1, 0.4, 0.8], [1, 1, 1])

    def test_a_single_distinct_forecast_is_refused(self):
        with self.assertRaisesRegex(MetricError, "zero by construction"):
            corp_decomposition([0.4, 0.4, 0.4], [0, 1, 1])

    def test_a_ten_day_all_stressed_window_is_refused(self):
        """The shape an event window actually has."""

        with self.assertRaises(MetricError):
            corp_decomposition([0.5 + 0.01 * i for i in range(10)], [1] * 10)


class ReliabilityCurveTests(unittest.TestCase):
    def test_the_curve_is_non_decreasing_in_the_forecast(self):
        probabilities, outcomes = synthetic()
        curve = corp_reliability_curve(probabilities, outcomes)
        for position in range(1, len(curve.recalibrated)):
            self.assertGreaterEqual(
                curve.recalibrated[position] + 1e-12,
                curve.recalibrated[position - 1],
            )

    def test_the_curve_is_sorted_by_forecast(self):
        probabilities, outcomes = synthetic()
        curve = corp_reliability_curve(probabilities, outcomes)
        self.assertEqual(list(curve.forecast), sorted(curve.forecast))

    def test_a_band_needs_both_a_block_length_and_a_seed(self):
        probabilities, outcomes = synthetic(n=80)
        with self.assertRaisesRegex(MetricError, "both block_length and seed"):
            corp_reliability_curve(probabilities, outcomes, block_length=5)
        with self.assertRaisesRegex(MetricError, "both block_length and seed"):
            corp_reliability_curve(probabilities, outcomes, seed=1)

    def test_no_band_is_returned_when_none_was_asked_for(self):
        probabilities, outcomes = synthetic(n=80)
        curve = corp_reliability_curve(probabilities, outcomes)
        self.assertEqual(curve.lower, ())
        self.assertEqual(curve.upper, ())

    def test_the_band_is_reproducible_from_the_seed(self):
        probabilities, outcomes = synthetic(n=80)
        kwargs = dict(block_length=5, seed=7, replications=60)
        first = corp_reliability_curve(probabilities, outcomes, **kwargs)
        second = corp_reliability_curve(probabilities, outcomes, **kwargs)
        self.assertEqual(first.lower, second.lower)
        self.assertEqual(first.upper, second.upper)

    def test_the_band_brackets_and_has_width(self):
        probabilities, outcomes = synthetic(n=120)
        curve = corp_reliability_curve(
            probabilities, outcomes, block_length=5, seed=3, replications=120
        )
        self.assertEqual(len(curve.lower), curve.n)
        for lower, upper in zip(curve.lower, curve.upper):
            self.assertLessEqual(lower, upper)
        self.assertGreater(
            max(u - l for l, u in zip(curve.lower, curve.upper)),
            0.0,
            msg="the band has zero width everywhere; it is not a band",
        )


class LogScoreTests(unittest.TestCase):
    def test_a_perfect_confident_forecast_scores_zero(self):
        self.assertEqual(log_score([1.0, 0.0], [1, 0]), 0.0)

    def test_a_confidently_wrong_forecast_is_infinite_and_not_clipped(self):
        """Clipping would replace an infinite loss with an arbitrary number.

        The clip value is chosen by whoever writes it, which makes the score
        tunable after the fact -- and it hides the failure worth seeing.
        """

        self.assertEqual(log_score([0.0], [1]), math.inf)
        self.assertEqual(log_score([1.0], [0]), math.inf)

    def test_one_impossible_call_dominates_the_mean(self):
        self.assertEqual(log_score([0.5, 0.5, 0.0], [1, 0, 1]), math.inf)

    def test_a_coin_flip_scores_log_two(self):
        self.assertAlmostEqual(log_score([0.5, 0.5], [1, 0]), math.log(2))

    def test_a_sharper_correct_forecast_scores_better(self):
        self.assertLess(log_score([0.9], [1]), log_score([0.6], [1]))


class ContinuousTargetTests(unittest.TestCase):
    """Pinball, CRPS from quantiles, and the threshold-weighted score."""

    def test_pinball_is_asymmetric_around_the_level(self):
        self.assertAlmostEqual(pinball_loss(0.9, 10.0, 20.0), 0.9 * 10.0)
        self.assertAlmostEqual(pinball_loss(0.9, 20.0, 10.0), 0.1 * 10.0)

    def test_pinball_is_zero_on_an_exact_hit(self):
        self.assertEqual(pinball_loss(0.5, 7.0, 7.0), 0.0)

    def test_a_level_outside_the_open_unit_interval_is_rejected(self):
        for bad in (0.0, 1.0, -0.5):
            with self.subTest(level=bad):
                with self.assertRaisesRegex(MetricError, "level"):
                    pinball_loss(bad, 1.0, 1.0)

    def test_crps_from_quantiles_rewards_a_tighter_correct_forecast(self):
        levels = (0.1, 0.5, 0.9)
        tight = crps_from_quantiles(levels, (9.0, 10.0, 11.0), 10.0)
        loose = crps_from_quantiles(levels, (0.0, 10.0, 20.0), 10.0)
        self.assertLess(tight, loose)

    def test_crossing_quantiles_are_rejected(self):
        with self.assertRaisesRegex(MetricError, "quantiles cross"):
            crps_from_quantiles((0.1, 0.9), (10.0, 5.0), 7.0)

    def test_threshold_weighted_crps_requires_weights(self):
        """An unweighted score under a weighted name would be the wrong metric."""

        signature = inspect.signature(threshold_weighted_crps)
        self.assertIs(signature.parameters["weights"].default, inspect.Parameter.empty)
        with self.assertRaises(TypeError):
            threshold_weighted_crps(TAUS, (0.9, 0.7, 0.4, 0.1), 12.0)
        with self.assertRaisesRegex(MetricError, "weights are required"):
            threshold_weighted_crps(TAUS, (0.9, 0.7, 0.4, 0.1), 12.0, None)

    def test_weighting_the_tail_changes_which_model_wins(self):
        """Why the contract asks for the weighted score rather than plain CRPS.

        Two models: one good at the low thresholds and bad at 50bp, one the
        reverse. Unweighted they are close; weighted toward the tail the second
        wins clearly. A metric that could not separate them would not be
        measuring the thing the project cares about.
        """

        observed = 60.0  # a genuine tail day: above every declared tau
        good_low = (0.99, 0.60, 0.20, 0.02)
        good_high = (0.99, 0.95, 0.85, 0.70)
        tail_weights = (0.0, 0.0, 1.0, 1.0)

        self.assertLess(
            crps_on_grid(TAUS, good_high, observed),
            crps_on_grid(TAUS, good_low, observed),
        )
        weighted_high = threshold_weighted_crps(TAUS, good_high, observed, tail_weights)
        weighted_low = threshold_weighted_crps(TAUS, good_low, observed, tail_weights)
        self.assertLess(weighted_high, weighted_low)
        self.assertGreater(weighted_low - weighted_high, 0.0)

    def test_a_non_monotone_exceedance_curve_is_rejected(self):
        with self.assertRaisesRegex(MetricError, "exceedance rises"):
            crps_on_grid(TAUS, (0.1, 0.4, 0.7, 0.9), 12.0)

    def test_a_zero_weight_vector_is_rejected(self):
        with self.assertRaisesRegex(MetricError, "all weights are 0"):
            threshold_weighted_crps(TAUS, (0.9, 0.7, 0.4, 0.1), 12.0, (0, 0, 0, 0))

    def test_a_negative_weight_is_rejected(self):
        with self.assertRaisesRegex(MetricError, "must be finite and >= 0"):
            threshold_weighted_crps(TAUS, (0.9, 0.7, 0.4, 0.1), 12.0, (1, 1, 1, -1))

    def test_a_single_threshold_cannot_be_integrated_over(self):
        with self.assertRaisesRegex(MetricError, "at least two thresholds"):
            crps_on_grid((5.0,), (0.5,), 12.0)

    def test_a_perfect_step_forecast_scores_near_zero(self):
        """Certainty that the value is above every threshold, and it is."""

        self.assertAlmostEqual(
            crps_on_grid(TAUS, (1.0, 1.0, 1.0, 1.0), 60.0), 0.0, places=12
        )


class PrecisionRecallTests(unittest.TestCase):
    def test_a_perfect_ranking_has_average_precision_one(self):
        probabilities = [0.9, 0.8, 0.7, 0.2, 0.1]
        outcomes = [1, 1, 1, 0, 0]
        self.assertAlmostEqual(average_precision(probabilities, outcomes), 1.0)

    def test_recall_reaches_one_at_the_lowest_threshold(self):
        probabilities, outcomes = synthetic(n=100)
        curve = precision_recall_curve(probabilities, outcomes)
        self.assertAlmostEqual(curve.recall[-1], 1.0)

    def test_recall_is_non_decreasing_down_the_thresholds(self):
        probabilities, outcomes = synthetic(n=100)
        curve = precision_recall_curve(probabilities, outcomes)
        for position in range(1, len(curve.recall)):
            self.assertGreaterEqual(curve.recall[position], curve.recall[position - 1])

    def test_the_base_rate_is_reported_beside_the_curve(self):
        """Average precision is meaningless without the no-skill reference."""

        probabilities, outcomes = synthetic(n=100)
        curve = precision_recall_curve(probabilities, outcomes)
        self.assertAlmostEqual(curve.base_rate, sum(outcomes) / len(outcomes))

    def test_a_random_forecast_scores_near_the_base_rate(self):
        rng = random.Random(4)
        outcomes = [1 if rng.random() < 0.1 else 0 for _ in range(3000)]
        probabilities = [rng.random() for _ in outcomes]
        base_rate = sum(outcomes) / len(outcomes)
        self.assertAlmostEqual(
            average_precision(probabilities, outcomes), base_rate, delta=0.05
        )

    def test_one_point_per_distinct_threshold(self):
        probabilities = [0.5, 0.5, 0.5, 0.2]
        outcomes = [1, 0, 1, 0]
        curve = precision_recall_curve(probabilities, outcomes)
        self.assertEqual(len(curve.thresholds), 2)

    def test_a_sample_with_no_positives_is_refused(self):
        with self.assertRaisesRegex(MetricError, "no positive outcomes"):
            precision_recall_curve([0.1, 0.2], [0, 0])


class NoRocTests(unittest.TestCase):
    """"Precision-recall, not ROC." A prohibition needs a test."""

    def test_the_module_exposes_no_roc_or_auc_symbol(self):
        for name in dir(metrics):
            lowered = name.lower()
            for forbidden in ("roc", "auroc", "auc"):
                self.assertNotIn(
                    forbidden,
                    lowered,
                    msg=f"metrics exposes {name!r}; the contract asks for "
                    "precision-recall, because at these base rates the false "
                    "positive rate has a denominator large enough to hide a "
                    "model going from useless to useful",
                )

    def test_average_precision_is_the_exported_summary(self):
        self.assertIn("average_precision", metrics.__all__)


# --------------------------------------------------------------------------
# The fixed-bin ECE prohibition
# --------------------------------------------------------------------------

#: Identifiers that betray a binned calibration statistic. Matched against
#: Python *identifiers only* -- see `identifiers_in` for why prose is exempt.
FORBIDDEN_IDENTIFIERS = (
    r"^ece$",
    r"^.*expected_calibration_error.*$",
    r"^.*calibration_error.*$",
    r"^n_?bins$",
    r"^num_bins$",
    r"^bin_edges$",
    r"^bin_count$",
    r"^bin_centres?$",
    r"^bin_centers$",
    r"^calibration_bins$",
    r"^.*equal_width_bins.*$",
    r"^.*equal_mass_bins.*$",
    r"^.*binned_calibration.*$",
)

FORBIDDEN = tuple(re.compile(pattern) for pattern in FORBIDDEN_IDENTIFIERS)

#: This file must name what it forbids, so it cannot scan itself.
SCANNER = Path(__file__).resolve()


def identifiers_in(source):
    """Every identifier in `source`, ignoring strings and comments.

    Tokenizing rather than grepping is what lets this coexist with the contract.
    `AGENT_CONTRACT.md` prohibits fixed-bin ECE *by name*, and
    `repo_model.metrics` explains at length why it is absent -- a plain text
    search would flag both, so the prohibition would be unenforceable in any
    codebase that documented it. Identifiers are the thing an implementation
    cannot avoid having.

    The limit is real and worth stating: someone could implement ECE with
    uninformative names and this would not catch it. It is a tripwire against
    the mistake being made openly, which is how it would actually be made.
    """

    names = set()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.NAME:
            names.add(token.string.lower())
    return names


def scan_for_fixed_bin_ece(source):
    """Forbidden identifiers found in `source`, as a sorted list."""

    return sorted(
        name
        for name in identifiers_in(source)
        if any(pattern.match(name) for pattern in FORBIDDEN)
    )


class FixedBinECEProhibitionTests(unittest.TestCase):
    """"Fixed-bin ECE is prohibited at these base rates." Enforced, not assumed.

    The estimator's bias depends on the bin count, so the number moves when the
    bins move, which makes it tunable after the fact by whoever picks them. At
    exceedance rates for 20bp and 50bp most bins hold a handful of points or
    none. `repo_model.metrics` reports the CORP decomposition instead, whose
    partition is chosen by the pool-adjacent violators algorithm.
    """

    def python_sources(self):
        for path in sorted(REPO_ROOT.rglob("*.py")):
            if ".git" in path.parts or path.resolve() == SCANNER:
                continue
            yield path

    def test_no_python_source_defines_a_fixed_bin_calibration_statistic(self):
        offenders = {}
        for path in self.python_sources():
            found = scan_for_fixed_bin_ece(path.read_text(encoding="utf-8"))
            if found:
                offenders[str(path.relative_to(REPO_ROOT))] = found
        self.assertEqual(
            offenders,
            {},
            msg="fixed-bin ECE reappeared: "
            + "; ".join(f"{path} -> {names}" for path, names in offenders.items())
            + ". The contract prohibits it; use corp_decomposition, whose "
            "partition has nothing to tune.",
        )

    def test_the_scan_actually_covers_the_metrics_module(self):
        """A scanner that silently covered nothing would always pass."""

        scanned = {path.name for path in self.python_sources()}
        self.assertIn("metrics.py", scanned)
        self.assertIn("event_eval.py", scanned)
        self.assertIn("splits.py", scanned)
        self.assertGreater(len(scanned), 5)

    def test_the_scanner_catches_a_planted_implementation(self):
        """Positive control. A scanner that cannot fail is worse than none."""

        planted = (
            "def expected_calibration_error(probabilities, outcomes, n_bins=10):\n"
            "    edges = [i / n_bins for i in range(n_bins + 1)]\n"
            "    return sum(edges)\n"
        )
        found = scan_for_fixed_bin_ece(planted)
        self.assertIn("expected_calibration_error", found)
        self.assertIn("n_bins", found)

    def test_the_scanner_catches_each_forbidden_name_individually(self):
        for name in ("ece", "n_bins", "nbins", "num_bins", "bin_edges", "bin_count"):
            with self.subTest(name=name):
                self.assertEqual(scan_for_fixed_bin_ece(f"{name} = 1\n"), [name])

    def test_prose_naming_the_prohibition_is_not_flagged(self):
        """The contract and the module docstring must be free to say the words.

        Without this, documenting the prohibition would violate it, and the
        honest response would be to delete the explanation -- leaving a codebase
        that avoids fixed-bin ECE for no recorded reason.
        """

        prose = (
            '"""Fixed-bin ECE is prohibited at these base rates.\n\n'
            "Expected calibration error over fixed probability bins is biased,\n"
            'and its bias depends on n_bins."""\n'
            "value = 1\n"
        )
        self.assertEqual(scan_for_fixed_bin_ece(prose), [])

    def test_a_comment_naming_it_is_not_flagged(self):
        self.assertEqual(scan_for_fixed_bin_ece("# no ece here, see n_bins\nx = 1\n"), [])

    def test_similar_words_are_not_false_positives(self):
        source = "piece = 1\nrecent = 2\nbinary = 3\nbisect_left = 4\ncombine = 5\n"
        self.assertEqual(scan_for_fixed_bin_ece(source), [])


class StationaryBootstrapTests(unittest.TestCase):
    def test_a_resample_has_the_right_length_and_range(self):
        rng = random.Random(1)
        indices = stationary_bootstrap_indices(50, 5, rng)
        self.assertEqual(len(indices), 50)
        self.assertTrue(all(0 <= index < 50 for index in indices))

    def test_blocks_are_contiguous_runs_of_about_the_requested_length(self):
        """The property that distinguishes this from an iid bootstrap.

        Mean run length should sit near `block_length`. If it were near 1 the
        resample would be iid and every interval computed from it would be too
        narrow on serially dependent data -- which is the failure this whole
        machinery exists to avoid.
        """

        rng = random.Random(2)
        runs = []
        for _ in range(200):
            indices = stationary_bootstrap_indices(200, 10, rng)
            length = 1
            for position in range(1, len(indices)):
                if indices[position] == (indices[position - 1] + 1) % 200:
                    length += 1
                else:
                    runs.append(length)
                    length = 1
            runs.append(length)
        mean_run = sum(runs) / len(runs)
        self.assertGreater(mean_run, 5.0)
        self.assertLess(mean_run, 20.0)

    def test_a_block_length_of_one_is_the_iid_bootstrap(self):
        """Legal, but it has to be chosen. That is why there is no default."""

        rng = random.Random(3)
        indices = stationary_bootstrap_indices(300, 1, rng)
        consecutive = sum(
            1
            for position in range(1, len(indices))
            if indices[position] == (indices[position - 1] + 1) % 300
        )
        self.assertLess(consecutive, 30)

    def test_a_block_length_below_one_is_rejected(self):
        with self.assertRaisesRegex(MetricError, "at least 1"):
            stationary_bootstrap_indices(10, 0.5, random.Random(0))

    def test_the_interval_requires_a_block_length_and_a_seed(self):
        for name in ("block_length", "seed"):
            with self.subTest(argument=name):
                self.assertIs(
                    inspect.signature(stationary_bootstrap_interval)
                    .parameters[name]
                    .default,
                    inspect.Parameter.empty,
                    msg=f"{name} acquired a default",
                )

    def test_omitting_the_block_length_is_a_type_error(self):
        with self.assertRaises(TypeError):
            stationary_bootstrap_interval(lambda idx: 0.0, 10, seed=1)

    def test_an_unseeded_interval_is_refused(self):
        with self.assertRaisesRegex(MetricError, "not\\s+reproducible"):
            stationary_bootstrap_interval(
                lambda idx: 0.0, 10, block_length=2, seed=None
            )

    def test_the_interval_is_reproducible_from_the_seed(self):
        probabilities, outcomes = synthetic(n=150)

        def statistic(indices):
            return brier_score(
                [probabilities[i] for i in indices], [outcomes[i] for i in indices]
            )

        kwargs = dict(block_length=5, seed=42, replications=200)
        self.assertEqual(
            stationary_bootstrap_interval(statistic, 150, **kwargs),
            stationary_bootstrap_interval(statistic, 150, **kwargs),
        )

    def test_the_interval_brackets_the_point_estimate(self):
        probabilities, outcomes = synthetic(n=200)

        def statistic(indices):
            return brier_score(
                [probabilities[i] for i in indices], [outcomes[i] for i in indices]
            )

        lower, upper = stationary_bootstrap_interval(
            statistic, 200, block_length=5, seed=8, replications=400
        )
        point = brier_score(probabilities, outcomes)
        self.assertLessEqual(lower, point)
        self.assertLessEqual(point, upper)
        self.assertLess(lower, upper)

    def test_dependence_widens_the_interval(self):
        """The number the block length actually changes.

        On a serially dependent series a block bootstrap gives a wider interval
        than the iid one, because it does not pretend each day is fresh
        evidence. If these came out equal, the block structure would be
        decorative and the contract's rule would buy nothing.
        """

        probabilities, outcomes = synthetic(n=300, seed=17)

        def statistic(indices):
            return sum(outcomes[i] for i in indices) / len(indices)

        iid = stationary_bootstrap_interval(
            statistic, 300, block_length=1, seed=5, replications=600
        )
        blocked = stationary_bootstrap_interval(
            statistic, 300, block_length=20, seed=5, replications=600
        )
        self.assertGreater(blocked[1] - blocked[0], iid[1] - iid[0])

    def test_a_non_finite_statistic_raises_rather_than_being_dropped(self):
        """Dropping such replicates would silently narrow the interval."""

        with self.assertRaisesRegex(MetricError, "bootstrap replication"):
            stationary_bootstrap_interval(
                lambda indices: math.inf, 20, block_length=3, seed=1, replications=5
            )

    def test_the_paired_resample_keeps_forecasts_with_their_outcomes(self):
        """Why the callback takes indices rather than two resampled series.

        Resampling forecasts and outcomes independently would destroy the
        pairing every score here is computed from, and would do it silently --
        the numbers would still come out, and they would be noise.
        """

        probabilities = [0.0, 1.0] * 50
        outcomes = [0, 1] * 50

        def statistic(indices):
            return brier_score(
                [probabilities[i] for i in indices], [outcomes[i] for i in indices]
            )

        lower, upper = stationary_bootstrap_interval(
            statistic, 100, block_length=4, seed=2, replications=100
        )
        self.assertEqual((lower, upper), (0.0, 0.0))


class MutationRecordTests(unittest.TestCase):
    """The mutation record, as assertions rather than as prose.

    `CLAUDE.md` requires a mutation for every new guard. A record written as a
    paragraph goes stale silently -- the mutation stops being caught and the
    paragraph still says it is. These re-run the mutations against the real
    implementations on every suite run, so a guard that stops working fails the
    build instead of leaving a false claim in a docstring.

    Each test states the mutation, then asserts the observable difference the
    correct implementation produces. Guards that are structural rather than
    numerical -- the required `climatology`, `block_length` and `seed` -- are
    mutated by removing the requirement, which is a signature change, and those
    are covered by the `has no default` tests above.

    Every mutation below was planted in `src/repo_model/metrics.py` and the full
    suite run against it, stdlib only, under `-B` with
    `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared first. Observed:

      1a. PAV monotonicity dropped, group means kept  -> 3 failures
      1b. recalibration returns the forecasts unchanged -> 2 failures
      2.  tie pooling removed from `_recalibrate`      -> 1 failure
      3.  `block_length` ignored (iid bootstrap)       -> 3 failures
      4.  log score clipped at 1e-15                   -> 3 failures
      5.  twCRPS `weights` defaulted to ones           -> 1 failure
      6.  exceedance monotonicity check removed        -> 2 failures
      7.  degenerate-sample guard removed              -> 4 failures

    Two of those are worth reading rather than counting.

    1a and 1b are different mutations and the first draft of this record
    conflated them. Replacing the *PAV routine* with the identity leaves the
    recalibration as a per-forecast-value group mean -- the binned calibration
    curve, minus the monotonicity -- which still differs from the raw forecast,
    so reliability stays positive and only the ordering breaks. Replacing the
    *recalibration* with the identity is the mutation that zeroes reliability.
    The two are caught by different tests, which is the useful part:
    monotonicity by the curve tests, the recalibration itself by the
    miscalibrated-sample test, and neither of those sees the other mutation. The
    record test below covers both, but only after its monotonicity fixture was
    changed -- on the miscalibrated fixture the raw group means happen to ascend,
    so the assertion had no power against 1a until it was given a sample whose
    group means actually invert. That is the failure mode of a mutation record
    written from what the code looks like rather than from a run.

    Mutation 2 is caught by exactly one test -- the tie-pooling record test
    below -- and not by `test_the_identity_holds_when_forecasts_tie`. That is
    not a gap in the identity test but a fact about the identity: it holds under
    unpooled ties too, because the components are all computed from the same
    recalibrated vector whatever that vector is. What unpooled ties break is
    order-invariance, which is why the guard needs its own test and why that
    test shuffles.
    """

    def test_mutation_isotonic_fit_replaced_by_the_identity(self):
        """Mutation 1b: `_recalibrate` returns the forecasts unchanged.

        Reliability is then 0 for every model, including a badly miscalibrated
        one, and the decomposition reports perfect calibration everywhere --
        the most flattering failure available to this module, and a silent one,
        since the identity still holds and the numbers still look like a
        decomposition. Caught here and by
        `test_a_miscalibrated_forecast_has_positive_reliability`.

        Mutation 1a, dropping monotonicity from PAV while keeping the group
        means, is a different and weaker change: reliability stays positive and
        what breaks is the ordering. It is also caught by
        `ReliabilityCurveTests.test_the_curve_is_non_decreasing_in_the_forecast`
        and by `test_an_uninformative_forecast_has_near_zero_resolution`, both
        of which stay green under 1b -- so neither mutation is covered by the
        other's dedicated tests, which is why both were run.
        """

        probabilities = [0.9] * 40 + [0.95] * 40
        outcomes = [1] * 10 + [0] * 30 + [1] * 12 + [0] * 28
        decomposition = corp_decomposition(probabilities, outcomes)
        self.assertGreater(decomposition.reliability, 0.01)
        self.assertAlmostEqual(decomposition.identity_residual(), 0.0, places=12)

        # Mutation 1a's property: the fit is non-decreasing in the forecast.
        # The fixture has to be one where the raw group means actually invert,
        # or the assertion has no power -- on the miscalibrated fixture above
        # they happen to ascend, so dropping PAV changes nothing visible here.
        # Here the low-forecast group outcomes at 0.75 and the high-forecast
        # group at 0.25, so an isotonic fit must pool them and an identity fit
        # leaves the curve going downhill.
        inverted_forecasts = [0.3] * 20 + [0.7] * 20
        inverted_outcomes = [1] * 15 + [0] * 5 + [1] * 5 + [0] * 15
        inverted = corp_reliability_curve(inverted_forecasts, inverted_outcomes)
        for position in range(1, len(inverted.recalibrated)):
            self.assertGreaterEqual(
                inverted.recalibrated[position] + 1e-12,
                inverted.recalibrated[position - 1],
                msg="the recalibrated curve goes downhill; the isotonic "
                "constraint is not being applied",
            )

    def test_mutation_tie_pooling_removed_from_the_recalibration(self):
        """Mutation 2: ties no longer pooled before the isotonic fit.

        The fit then depends on the order tied rows arrive in, so shuffling the
        input changes the reported reliability. This test is the *only* one that
        catches it -- see the class docstring: the decomposition identity holds
        under unpooled ties as well, so the identity tests cannot see this. What
        unpooled ties break is order-invariance, which is why this shuffles.
        """

        probabilities = [0.3] * 20 + [0.7] * 20
        outcomes = [0] * 15 + [1] * 5 + [0] * 4 + [1] * 16
        first = corp_decomposition(probabilities, outcomes)
        pairs = list(zip(probabilities, outcomes))
        random.Random(1234).shuffle(pairs)
        shuffled = corp_decomposition([p for p, _ in pairs], [y for _, y in pairs])
        self.assertAlmostEqual(first.reliability, shuffled.reliability, places=12)
        self.assertAlmostEqual(first.resolution, shuffled.resolution, places=12)

    def test_mutation_block_length_ignored_in_the_bootstrap(self):
        """`block_length` read but not used, giving the iid bootstrap.

        Intervals on a serially dependent series would then be too narrow, which
        is the failure that makes a model look significant when it is not.
        Caught by the blocked interval being strictly wider than the iid one.
        """

        probabilities, outcomes = synthetic(n=300, seed=17)

        def statistic(indices):
            return sum(outcomes[i] for i in indices) / len(indices)

        iid = stationary_bootstrap_interval(
            statistic, 300, block_length=1, seed=5, replications=600
        )
        blocked = stationary_bootstrap_interval(
            statistic, 300, block_length=20, seed=5, replications=600
        )
        self.assertGreater((blocked[1] - blocked[0]) / (iid[1] - iid[0]), 1.2)

    def test_mutation_log_score_clipped_at_a_small_epsilon(self):
        """`likelihood = max(likelihood, 1e-15)` instead of returning inf.

        A model that called a stress day impossible would score a large finite
        number that averages away against its good days. Caught: the score is
        exactly `inf`, and a mean containing it stays `inf`.
        """

        self.assertEqual(log_score([0.0], [1]), math.inf)
        self.assertEqual(log_score([0.5, 0.5, 0.0], [1, 0, 1]), math.inf)

    def test_mutation_twcrps_weights_defaulted_to_one(self):
        """Weights defaulting to all-ones, i.e. plain CRPS under a weighted name.

        Caught two ways: the signature has no default, so the call is a
        `TypeError`; and a tail-weighted score is numerically different from the
        unweighted one on the same inputs, so the substitution would change
        every reported number.
        """

        observed = 60.0
        curve = (0.99, 0.60, 0.20, 0.02)
        self.assertNotAlmostEqual(
            threshold_weighted_crps(TAUS, curve, observed, (0.0, 0.0, 1.0, 1.0)),
            crps_on_grid(TAUS, curve, observed),
        )

    def test_mutation_exceedance_monotonicity_check_removed(self):
        """`P(Y > tau)` allowed to rise with tau.

        A broken predictive distribution would be integrated over and reported
        as a score rather than refused. Caught by the explicit rejection, which
        matches the check `repo_model.event_eval` already applies to the same
        curve -- the two agree on what a valid exceedance curve is.
        """

        with self.assertRaisesRegex(MetricError, "exceedance rises"):
            crps_on_grid(TAUS, (0.1, 0.4, 0.7, 0.9), 12.0)

    def test_mutation_degenerate_sample_guard_removed(self):
        """The single-class and single-forecast refusals deleted.

        A ten-day all-stressed event window would then produce a Brier
        decomposition -- exactly the aggregate the contract prohibits on a
        single event window -- with uncertainty 0 and a resolution measured
        against a baseline that is already perfect. Caught by the refusal.
        """

        with self.assertRaises(MetricError):
            corp_decomposition([0.5 + 0.01 * i for i in range(10)], [1] * 10)
        with self.assertRaises(MetricError):
            corp_decomposition([0.4, 0.4, 0.4], [0, 1, 1])


if __name__ == "__main__":
    unittest.main()
