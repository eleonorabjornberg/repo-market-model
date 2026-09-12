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
`FixedBinECEProhibitionTests` scans every Python source a clone of this
repository would contain -- not every one on the disk, which in a worktree with
a `.venv/` is somebody else's code -- and fails the build if the thing
reappears. It has a positive control too, because a scanner that cannot fail is
worse than no scanner.

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
import subprocess
import sys
import tempfile
import tokenize
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import metrics
from repo_model.metrics import (
    REPORTED_PRECISION_PLACES,
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
        # Varied negligibly and independently of the outcome: still no
        # information about it. A truly constant set would do as well now that
        # the decomposition reports rather than refuses it, but this fixture is
        # the near-constant case, which is the one a fitted model produces.
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

    def test_a_single_distinct_forecast_is_refused_by_the_reliability_curve(self):
        """The refusal that used to be `corp_decomposition`'s as well.

        It is now only the curve's. A constant forecast set is not degenerate
        arithmetic -- uncertainty is positive and reliability is
        `(p - base_rate) ** 2`, which is real -- so the decomposition reports it
        and names the zero share instead, and
        `RealizedDiscriminationTests` is where that is asserted. A reliability
        diagram of one point with a bootstrap band around it is still nothing,
        so here the refusal stands.
        """

        with self.assertRaisesRegex(MetricError, "zero by construction"):
            corp_reliability_curve([0.4, 0.4, 0.4], [0, 1, 1], block_length=2, seed=1)

    def test_a_ten_day_all_stressed_window_is_refused(self):
        """The shape an event window actually has."""

        with self.assertRaises(MetricError):
            corp_decomposition([0.5 + 0.01 * i for i in range(10)], [1] * 10)


def _two_group_sample(low_positives, high_positives, size):
    """A sample whose realised share of achievable discrimination is computable.

    Two equally sized forecast groups with rates `r_low` and `r_high`. The
    isotonic fit is then the two group rates, so

        uncertainty = b * (1 - b),  b = (r_low + r_high) / 2
        resolution  = ((r_high - r_low) / 2) ** 2

    and the share follows in closed form. That is what makes these fixtures
    usable for pinning the naming threshold: the share is chosen, not
    discovered, so a fixture that lands on the wrong side of it is a fixture
    error rather than a finding.
    """

    probabilities = [0.1] * size + [0.2] * size
    outcomes = (
        [1] * low_positives
        + [0] * (size - low_positives)
        + [1] * high_positives
        + [0] * (size - high_positives)
    )
    return probabilities, outcomes


class RealizedDiscriminationTests(unittest.TestCase):
    """How much of the achievable discrimination the forecasts actually realised.

    `resolution` is not readable on its own, because its ceiling is
    `uncertainty` and that moves with the base rate. On the published
    conditional run resolution falls four orders of magnitude from 5bp to 50bp
    while uncertainty falls two, and from the pair as published a reader cannot
    tell a model that stopped discriminating from a sample that stopped
    offering anything to discriminate. `realized_discrimination` is
    `resolution / uncertainty`, which is the same finding stated in a way that
    does not depend on how rare the event is.

    The naming is the other half and is not decoration. A share printed at the
    precision the terms are published at can itself round to `0.0000`, which is
    exactly the reading failure this number exists to fix one level up, so a
    share that rounds away is named in the returned value with its reason
    instead.

    Mutation record
    ---------------

    Every mutation below was planted in `src/repo_model/metrics.py` in a
    disposable copy under `$HOME`, built from `git ls-files`, run stdlib-only
    with `PYTHONDONTWRITEBYTECODE=1` under `python3 -B`. The unmutated control
    was green before and after. The acceptance test and the mutation target are
    the same test -- `test_a_decomposition_reports_what_share_of_the_achievable
    _discrimination_was_realised` -- and it is in every count below.

      1. `_discrimination_note` returns `None` unconditionally
         (the cheap implementation: divide, return a float, name nothing)
                                          -> 1 failure, `AssertionError`
      2. the division moved above `_require_scoreable_outcomes`
         in `corp_decomposition`          -> 28 errors, every one a
                                             `ZeroDivisionError`
      3. the share computed as `resolution / score`
         instead of `resolution / uncertainty`
                                          -> 1 failure, `AssertionError`
      4. `_require_scoreable_outcomes` dropped from `corp_decomposition`
         and the forecast refusal dropped from `_require_decomposable`
         (mutation 7 of `MutationRecordTests`, re-run because this block
         changed the fixture that record names)
                                          -> 1 failure and 28 errors:
                                             28 `ZeroDivisionError`, one
                                             `AssertionError`

    Mutation 2 is the one the block was written around, and its record is the
    reason exception types are worth writing down. It is not a wrong number; it
    is a right number computed a line too early, and what it costs is the *name*
    of the failure. `MetricError("all 3 outcomes are 1; a decomposition against
    climatology is degenerate on a single-class sample. If this is one event
    window, the contract asks for the exceedance curve and realized path ...")`
    becomes `ZeroDivisionError("float division by zero")`, which tells a caller
    nothing about event windows and nothing about what to do instead. The
    acceptance test catches it by asserting the type and the message, not merely
    that something raised.

    Twenty-eight of those errors is also a finding rather than a count: the
    single-class sample is not a hypothetical here. `test_baseline`'s rolling
    exceedance suite and `test_cli_eval`'s command tests reach it on ordinary
    fixtures, so the refusal that names it is on a path real callers take.

    Mutation 3 is worth reading because it is nearly invisible on a good model
    and wrong everywhere. `score` and `uncertainty` are the same order of
    magnitude at these base rates, so the mutated share stays plausible; it just
    stops being bounded by 1 and stops being a share of anything. The
    ratio assertion catches it first, which is why the observed exception is an
    `AssertionError` and not the `ZeroDivisionError` the perfect forecast set
    would raise under it -- `score` is 0 there, and the mutated denominator with
    it. Both were checked; only the first is reached.
    """

    def test_a_decomposition_reports_what_share_of_the_achievable_discrimination_was_realised(self):
        # 1. The share is resolution over uncertainty, on a middling sample.
        probabilities, outcomes = synthetic(n=300, seed=13)
        middling = corp_decomposition(probabilities, outcomes)
        self.assertAlmostEqual(
            middling.realized_discrimination,
            middling.resolution / middling.uncertainty,
            places=12,
        )

        # 2. The two ends. A forecast set that discriminates perfectly realises
        #    all of it; a constant one realises none.
        perfect = corp_decomposition([0.0] * 10 + [1.0] * 10, [0] * 10 + [1] * 10)
        self.assertAlmostEqual(perfect.realized_discrimination, 1.0, places=12)
        self.assertIsNone(perfect.discrimination_note)

        constant = corp_decomposition([0.4, 0.4, 0.4], [0, 1, 1])
        self.assertEqual(constant.realized_discrimination, 0.0)

        # Constant forecasts over varying outcomes return a decomposition. They
        # are the case the share exists to describe, and they still carry a real
        # reliability: the squared distance from the rate they should have been.
        # The refusal this replaced claimed reliability was "zero by
        # construction" here, and that was false -- only resolution is.
        self.assertAlmostEqual(constant.reliability, (0.4 - 2 / 3) ** 2, places=12)
        self.assertGreater(constant.reliability, 0.0)
        self.assertEqual(constant.resolution, 0.0)

        # 3. A share that rounds to nothing at the reported precision is named
        #    in the returned value, with a reason.
        for named in (constant, corp_decomposition(*_two_group_sample(497, 503, 1000))):
            self.assertIsNotNone(named.discrimination_note)
            self.assertEqual(
                "%.*f" % (REPORTED_PRECISION_PLACES, named.realized_discrimination),
                "%.*f" % (REPORTED_PRECISION_PLACES, 0.0),
            )
            self.assertIn("no discrimination", named.discrimination_note)
            self.assertIn("rounding artefact", named.discrimination_note)
            self.assertIn(repr(named.resolution), named.discrimination_note)
            self.assertIn(repr(named.uncertainty), named.discrimination_note)

        # The second of those is named while being strictly positive, so the
        # naming is a statement about legibility at the reported precision and
        # not a test for exact zero.
        nonzero_but_named = corp_decomposition(*_two_group_sample(497, 503, 1000))
        self.assertGreater(nonzero_but_named.realized_discrimination, 0.0)

        # 4. And the converse: a share small enough that `resolution` alone
        #    prints as a rounding artefact, but which the share still reports as
        #    a real quantity, is not named. This is the published 50bp row's
        #    magnitude, reconstructed rather than read off the record.
        legible = corp_decomposition(*_two_group_sample(489, 511, 1000))
        self.assertEqual("%.*f" % (REPORTED_PRECISION_PLACES, legible.resolution), "0.0001")
        self.assertEqual(
            "%.*f" % (REPORTED_PRECISION_PLACES, legible.realized_discrimination),
            "0.0005",
        )
        self.assertIsNone(legible.discrimination_note)

        # 5. The share is a share: bounded in [0, 1] and always finite. Neither
        #    holds of `resolution / score`.
        for seed in range(15):
            with self.subTest(seed=seed):
                sample, labels = synthetic(n=120, seed=seed)
                if len(set(labels)) < 2:
                    continue
                share = corp_decomposition(sample, labels).realized_discrimination
                self.assertTrue(math.isfinite(share))
                self.assertGreaterEqual(share, -1e-12)
                self.assertLessEqual(share, 1.0 + 1e-12)

        # 6. The refusal, which must run before the division. A single-class
        #    sample has uncertainty 0, so dividing first yields an infinity, a
        #    NaN or a ZeroDivisionError -- none of which names its cause. The
        #    assertion is on the type and the message, because a
        #    ZeroDivisionError escaping here is the mutation, not a pass.
        for degenerate in (([0.1, 0.4, 0.8], [1, 1, 1]), ([0.1, 0.4, 0.8], [0, 0, 0])):
            with self.subTest(outcomes=degenerate[1]):
                with self.assertRaises(MetricError) as caught:
                    corp_decomposition(*degenerate)
                self.assertIn("degenerate on a single-class", str(caught.exception))
                self.assertNotIsInstance(caught.exception, ZeroDivisionError)


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


class _CountingSequence:
    """A sequence that counts every element access, indexed or iterated.

    It deliberately defines no `__iter__`. An implementation that iterates
    rather than indexes then falls back to the old `__getitem__` protocol,
    which this counts, so a reinstated linear scan cannot walk the sequence
    without the counter seeing it. A counter wired to nothing reads exactly
    like a fast implementation, which is why the test below proves it fires
    before it trusts that it stayed low.
    """

    def __init__(self, items):
        self._items = list(items)
        self.accesses = 0

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise AssertionError(
                "sliced rather than indexed; a slice is one access here and "
                "would hide the cost this fixture exists to measure"
            )
        if index < 0:
            index += len(self._items)
        if not 0 <= index < len(self._items):
            raise IndexError(index)
        self.accesses += 1
        return self._items[index]


class StepLookupCostTests(unittest.TestCase):
    """`_step_lookup` bisects, and its cost is asserted rather than trusted.

    The scan this replaced was *correct*. It was a linear walk over a list its
    own docstring said was sorted, called `replications * n` times inside
    `corp_reliability_curve`, so the curve cost `O(replications * n^2)`.
    Profiled on a 500-row panel at 2000 replications it was 3.90 s of 5.36 s
    -- 73% of the curve, 1,000,000 calls -- and on the frozen 2104-row funding
    panel the exceedance backtest it sits under took about fourteen minutes.
    The suite could not see any of that, because it exercises the metric on
    twenty-five rows, where quadratic and logarithmic are indistinguishable.

    So the single test below asserts two things that fail apart:

      1. **Agreement** with a brute-force right-continuous scan written here as
         an oracle rather than imported, over a fixture with `x` below the
         first key, above the last, exactly equal to several keys, and strictly
         between keys, with duplicate keys present. The exact-equality cases
         carry the test: they are the only ones that separate `bisect_right`
         from `bisect_left`.
      2. **Cost**, via a sequence that counts element accesses. Logarithmic and
         linear differ by three orders of magnitude at n = 4096, so the bound
         does not have to be tight to be decisive.

    They are subtests rather than two tests because neither alone is the
    criterion -- correct-and-slow and fast-and-wrong are both failures -- and
    subtests so that a mutation killing one is seen not to have killed the
    other.

    Mutation record
    ---------------

    Both planted in `src/repo_model/metrics.py` in a disposable copy under
    `$HOME`, never in the mount, stdlib only, run with `-B` and
    `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared first. The unmutated
    control was green before and after both runs: 623 tests, OK, 5 skipped,
    zero `expectedFailure`.

      1. **The linear scan restored** -- the pre-block body, iterating
         `zip(keys, values)` and breaking on the first key past `x`. One
         failure, `AssertionError`, in the **cost** subtest: 2735 accesses
         against a bound of 40. The **agreement** subtest stayed green, as it
         must -- the scan is correct, it is only slow, and a test that cannot
         tell those apart is not measuring cost. Nothing else in the suite
         moved: 622 other tests green under a quadratic implementation, which
         is the gap this block closes.
      2. **`bisect_right` -> `bisect_left`** -- the plausible off-by-one, one
         token, and the reason this block records two mutations rather than
         one. One failure, `AssertionError`, in the **agreement** subtest, at
         `x=0.1`, an exact and duplicated key: 1.0 where the scan gives 2.0.
         The **cost** subtest stayed green -- bisecting to the wrong side is
         just as fast. Again nothing else in the suite moved.

    The first draft of the cost subtest queried an exact key, and mutation 2
    killed both halves. That looked like a stronger test and was a weaker one:
    two assertions that always fail together cannot show which property broke,
    and the pairing above is the entire point of recording two mutations. The
    cost query is now strictly between keys on purpose, and the comment at that
    line says so, because it looks like an arbitrary choice and is not.

    Mutation 2 is the one this test exists for. It is invisible on data with no
    exact ties, it does not raise, and it silently makes the step function
    left-continuous -- which moves a published reliability curve without moving
    any test that existed before this block.
    """

    # `bisect_right` probes ceil(log2(n + 1)) = 13 elements at n = 4096, and
    # the lookup then reads one value. 40 leaves room for a different but still
    # logarithmic implementation -- a couple of probes either way, a bounds
    # read -- while staying two orders of magnitude below 4096, which is the
    # only distinction being drawn. An exact count would pin the implementation
    # rather than the cost and would break on a correct refactor.
    MAX_ACCESSES = 40

    # Ascending, with duplicate runs at 0.10, 0.40 and 0.70. The values are
    # distinct so that landing on the wrong member of a run is visible.
    PAIRS = (
        (0.10, 1.0),
        (0.10, 2.0),
        (0.25, 3.0),
        (0.40, 4.0),
        (0.40, 5.0),
        (0.40, 6.0),
        (0.55, 7.0),
        (0.70, 8.0),
        (0.70, 9.0),
        (0.90, 10.0),
    )

    QUERIES = (
        0.05,   # below the first key -- the fallback branch
        0.10,   # exactly the first key, and a duplicated one
        0.17,   # strictly between keys
        0.25,   # exactly a singleton key
        0.33,   # strictly between keys
        0.40,   # exactly a triplicated key
        0.47,   # strictly between keys
        0.55,   # exactly a singleton key
        0.62,   # strictly between keys
        0.70,   # exactly a duplicated key
        0.80,   # strictly between keys
        0.90,   # exactly the last key
        0.99,   # above the last key
    )

    @staticmethod
    def _oracle(pairs, x):
        """Brute-force right-continuous step lookup. The specification, slowly.

        Written here rather than imported from `metrics`, so that a mutation of
        the implementation cannot mutate its own oracle.
        """

        best = pairs[0][1]
        for key, value in pairs:
            if key <= x:
                best = value
            else:
                break
        return best

    def test_the_lookup_does_not_visit_every_pair_and_agrees_with_the_scan_it_replaces(
        self,
    ):
        keys = [key for key, _ in self.PAIRS]
        values = [value for _, value in self.PAIRS]

        with self.subTest("agreement with the scan it replaces"):
            for x in self.QUERIES:
                self.assertEqual(
                    metrics._step_lookup(keys, values, x),
                    self._oracle(self.PAIRS, x),
                    msg=(
                        f"the lookup disagrees with the brute-force scan at "
                        f"x={x!r}; on an exact key this is bisect_left where "
                        f"bisect_right is required, which makes the step "
                        f"function left-continuous"
                    ),
                )

        with self.subTest("cost is logarithmic, not linear"):
            size = 4096
            big_keys = [index / size for index in range(size)]
            big_values = [float(index) for index in range(size)]

            # The counter has to be shown to fire before a low count means
            # anything, and it has to see iteration as well as indexing, or a
            # reinstated scan reads as fast. Walking a wrapper with the old
            # `__getitem__` protocol proves both.
            control = _CountingSequence(big_keys)
            for _ in control:
                pass
            self.assertGreaterEqual(
                control.accesses,
                size,
                msg="the access counter does not see iteration; a scan would "
                "read as free and this assertion would prove nothing",
            )

            counted_keys = _CountingSequence(big_keys)
            counted_values = _CountingSequence(big_values)
            # Strictly between two keys, deliberately. The exact-key cases
            # belong to the agreement subtest; querying one here would make
            # this subtest fail on the bisect_left off-by-one too, and then a
            # cost assertion and a correctness assertion could not be seen to
            # fail apart -- which is the whole reason there are two of them.
            index = size // 3
            x = (big_keys[index] + big_keys[index + 1]) / 2.0
            result = metrics._step_lookup(counted_keys, counted_values, x)

            self.assertEqual(
                result,
                self._oracle(list(zip(big_keys, big_values)), x),
                msg="the counted call did not return the right value, so the "
                "access count below is measuring the wrong thing",
            )
            accesses = counted_keys.accesses + counted_values.accesses
            self.assertGreater(
                accesses,
                0,
                msg="no accesses were counted at all; the counter is not "
                "wired to the sequences the lookup reads",
            )
            self.assertLessEqual(
                accesses,
                self.MAX_ACCESSES,
                msg=(
                    f"{accesses} element accesses to answer one lookup over "
                    f"{size} pairs. That is a linear scan, not a bisection; "
                    f"inside corp_reliability_curve it is O(replications * n^2)"
                ),
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


def git_ignored(root):
    """What git would leave out of a clone of `root`, or None if git cannot say.

    Untracked ignored entries, with an ignored directory reported once as
    `dir/` rather than file by file. `None` when `root` is not a git work tree
    -- a disposable mutation copy is not one -- and the caller then reads the
    whole walk, which is what it read before this existed.

    Asking git rather than keeping a list of directories is the whole point.
    A list that named `.venv/` would pass today and let the next ignored
    directory back in: `build/`, `.tox/`, a virtualenv someone called `env`.
    """

    try:
        listed = subprocess.run(
            [
                "git", "-C", str(root), "ls-files", "-z", "--others",
                "--ignored", "--exclude-standard", "--directory",
            ],
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return tuple(
        entry for entry in listed.decode("utf-8", "surrogateescape").split("\0")
        if entry
    )


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

    **Scope, and the defect it fixes.** `python_sources` walked the whole disk
    under `REPO_ROOT`. A worktree that grows a `.venv/` -- which the optional
    `ml` extra requires -- then put every installed package's source in scope,
    and two things followed. The visible one: the suite went red with
    `UnicodeDecodeError` on a latin-1 `.py` inside joblib, reproduced on
    `80c4311` by running this class in a worktree with a real virtualenv. The
    one that matters more: the prohibition is a claim about *this* repository,
    and a walk of the disk held it responsible for any fixed-bin ECE some
    third-party package happens to define. `tests/test_docs_freshness.py`
    found the same defect in its own scope one file over and repaired it at
    `d316bce`; the shape here is the same and the helper is not shared, because
    a guard whose implementation lives in another track's module cannot be the
    target of this track's mutation.

    **The repair.** Scope is what a clone receives: `git_ignored` asks git what
    it would leave out and paths under those entries are dropped. No exclusion
    list names a directory, so the next ignored directory is covered without an
    edit. Where git cannot answer -- a mutation copy is not a work tree -- the
    walk is what it always was, so nothing that was in scope leaves it.

    **Mutation, recorded on `80c4311`, Python 3.9.6, in a copy made by
    `CLAUDE.md`'s `git ls-files` recipe.** The ignore filter removed from
    `python_sources` (the `any(...)` clause reduced to `False`): kills
    `test_the_scan_reads_only_what_a_clone_would_contain` alone,
    `AssertionError` naming the planted path. Unmutated control green before
    and after, zero `expectedFailure`. The mutation is invisible to the other
    tests in this class because the copy contains nothing git ignores, which
    is exactly why the acceptance test plants its own tree.
    """

    def python_sources(self, root=REPO_ROOT):
        """Every Python source a clone of `root` would contain.

        `root` is a parameter so the scope rule can be exercised on a planted
        tree instead of on this one.
        """

        ignored = git_ignored(root) or ()
        for path in sorted(root.rglob("*.py")):
            if ".git" in path.parts or path.resolve() == SCANNER:
                continue
            relative = path.relative_to(root).as_posix()
            if any(
                relative == entry or (entry.endswith("/") and relative.startswith(entry))
                for entry in ignored
            ):
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

    def test_the_scan_reads_only_what_a_clone_would_contain(self):
        """A gitignored directory is not this repository's code to answer for.

        The planted directory is named nothing an exclusion list would have
        anticipated, on purpose: if this passed only for `.venv/` it would say
        nothing about `build/`, `.tox/` or a virtualenv called `env`. The
        planted file is both undecodable as UTF-8 and a fixed-bin ECE
        implementation, because those are the two ways an out-of-scope file
        broke this guard -- an error the suite showed, and an accusation it
        would have made.
        """

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            try:
                subprocess.run(
                    ["git", "init", "-q", str(root)], check=True, capture_output=True
                )
            except (OSError, subprocess.CalledProcessError):
                self.skipTest("git is not available to say what it ignores")
            (root / ".gitignore").write_text("pergamon-scratch/\n")
            vendored = root / "pergamon-scratch" / "site-packages" / "pkg"
            vendored.mkdir(parents=True)
            (vendored / "calibration.py").write_bytes(
                b"def expected_calibration_error(p, o, n_bins=10):\n"
                b"    edges = [i / n_bins for i in range(n_bins + 1)]  # \xa4\xe9\n"
                b"    return sum(edges)\n"
            )
            (root / "kept.py").write_text("value = 1\n")

            scanned = {
                path.relative_to(root).as_posix()
                for path in self.python_sources(root)
            }
            # The anchor: a scan that reads nothing would also exclude the plant.
            self.assertIn("kept.py", scanned)
            self.assertNotIn("pergamon-scratch/site-packages/pkg/calibration.py", scanned)

            # And the guard's own loop over that tree neither raises on the
            # plant nor reports it as this repository's fixed-bin ECE.
            offenders = {}
            for path in self.python_sources(root):
                found = scan_for_fixed_bin_ece(path.read_text(encoding="utf-8"))
                if found:
                    offenders[path.relative_to(root).as_posix()] = found
            self.assertEqual(offenders, {})

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
          re-run after the single-forecast half moved to
          `corp_reliability_curve`                     -> 1 failure, 28 errors

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

        **Re-run when the single-forecast half moved.** That refusal is now
        `corp_reliability_curve`'s alone: `corp_decomposition` reports a
        constant forecast set and names the zero share, per
        `RealizedDiscriminationTests`. This test's second assertion was
        re-pointed at the function that still refuses, and the mutation re-run
        against the new fixture -- `CLAUDE.md` requires that of a record whose
        fixture changed, and the earlier version of this assertion would have
        gone green over a refusal that had been deleted from the caller it
        named. The counts in the class docstring are from the re-run.
        """

        with self.assertRaises(MetricError):
            corp_decomposition([0.5 + 0.01 * i for i in range(10)], [1] * 10)
        with self.assertRaises(MetricError):
            corp_reliability_curve([0.4, 0.4, 0.4], [0, 1, 1], block_length=2, seed=1)


if __name__ == "__main__":
    unittest.main()
