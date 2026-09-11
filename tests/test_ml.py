"""`src/repo_model/ml.py`: gradient-boosted conditional quantiles.

The other half of the third-party boundary. `tests/test_dependency_boundary.py`
names this file and `src/repo_model/ml.py` as the only two places in the
repository that may reach numpy or scikit-learn, and it fails this file for a
module-level `import sklearn` that nothing catches: `unittest discover` imports
every test module it finds whether or not it runs it, so a bare import here
would turn the *core* suite red on a checkout without the extra instead of
skipping this file. Every third-party name below is therefore reached from
inside a test, through the package.

**Skip without the extra; fail when `REPO_MODEL_REQUIRE_ML` is set.** A skip is
the right answer on a core checkout and the wrong answer on a job that exists to
run these tests, and the two cannot be told apart from inside the process. The
environment variable is how the job says which one it is: CI's `ml` matrix entry
sets it, so an extra that failed to install becomes a red build rather than a
green one with an invisible skip. `unittest`'s skip count is not load-bearing --
`CLAUDE.md` says so and `tests/test_docs_freshness.py` refuses a transcribed one
-- which is exactly why the absence of a run has to be reportable some other
way.

What is covered here
--------------------

* `GradientBoostedQuantileTests` -- the model's own criterion: the
  rearrangement, reproducibility, and the two refusals. What the *law* is.
* `GradientBoostedCompareTests` -- the wiring criterion: `compare --model-b
  gbm --loss crps` through the command line, scoring that law and not another
  one. What the *command* does with it. The division is load-bearing and is
  demonstrated by a mutation, not asserted: a defect inside `predict` moves
  this file's expectation with the run and only the first class sees it, and a
  defect in what `FITTER_FACTORIES` registers leaves `predict` alone and only
  the second class sees it.
* `GradientBoostedEventHoldoutTests` -- `event-holdout --model gbm`: the
  journal line names the library versions the window's fit was made with, and
  the config hash does not move with them.
* `GradientBoostedConformalCalibrationTests` -- `calibration="conformal"`: the
  band covers its nominal probability on held-out rows where the uncalibrated
  band does not, the fit and calibration slices of every fold are purged apart,
  and the calibration's refusals.
* `GradientBoostedLaggedSpreadTests` -- `spread_change_lags`: the lagged spread
  changes read only rows at or before the feature date, by row, never across a
  hole, named in the declaration, and the lags' refusals.
* `GradientBoostedGarchFeatureTests` -- `volatility_feature="garch11"`: the
  GARCH(1,1) recovers a simulated truth, is fitted per fold on the fit rows,
  filters the calibration rows rather than refitting on them, reads nothing
  after a row for that row's variance, is named in the declaration, and its
  refusals.
* `GradientBoostedCrossConformalTests` -- `calibration="cross_conformal"`: the
  CV+ band covers its nominal probability where the fitted band does not, the
  interior is the full fit's bit for bit, every excluding model trains only
  outside its block and the purge gaps around it and scores only its own
  block, and the refusals.
* `GradientBoostedForecastInterfaceTests` -- `ForecastInterfaceConformance` from
  `tests/test_contract.py`, against `FittedGradientBoostedQuantiles`. Not a
  bespoke test class: `ForecastInterfaceCoverageTests` discovers the fitted
  models by walking the package, so this model was *required* to arrive with a
  conformance case the moment it was written, and it did -- block 9's walk
  doing its job on the module it was written for.
* `GbmExceedanceTests` -- `ExceedancePredictorConformance` from
  `tests/test_baseline.py`, against `gbm_exceedance`, required by block 10's
  walk for the same reason.

Both walks read `ForecastInterfaceConformance.__subclasses__()` and
`ExceedancePredictorConformance.__subclasses__()`, so the cases have to be
*imported* for the coverage guards to see them. Under this repository's own
command -- `python3 -m unittest discover -s tests` -- they are. Running
`tests/test_contract.py` on its own now fails its coverage guard, because the
walk finds a model in `repo_model.ml` and the case naming it lives here. That is
a property of the discovery, not of this file, and it is written up in the block
report rather than worked around with a second list.

The residual sample, and what this model does not claim
-------------------------------------------------------

`FittedPersistence`, `FittedArx`, `FittedThreshold` and
`FittedRollingResidualLaw` are all one anchor plus one fixed residual law, so
their predictive distribution is a location shift of a single shape and
`residuals` *is* that law. This model is the first that is not: its band is
fitted at each level separately, so the width moves with the feature row and no
row-independent sample can carry it.
`ForecastInterfaceConformance::test_the_exceedance_is_strictly_above_the_threshold`
reads `residuals` for where the law runs out, so the two are still tied
together, and `FittedGradientBoostedQuantiles.predict_stress` honours that tie
by reading the residual sample for its two tail knots and the rearranged
quantile vector for everything between. That the assertion survived a model
shaped unlike the four it was written against is the finding worth recording:
the interface generalises, and the one sentence that had to give was "the
residual sample is the whole law".

Mutation record
---------------

Run in a disposable copy under `$HOME` built from `git ls-files -z --cached
--others --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`,
on CPython 3.9.6 with numpy 2.0.2 and scikit-learn 1.6.1. Unmutated control
green before and after (779 tests); each mutation confirmed applied by grep, and
restored before the next.

1. **The rearrangement dropped.** `tuple(sorted(column[index] for column in
   columns))` -> `tuple(column[index] for column in columns)` in
   `ml._rearranged`. Kills
   `test_the_quantiles_are_ordered_and_reproducible_at_every_contract_level`,
   `AssertionError`, on twenty of `crossing_frame`'s forty-eight rows -- the
   criterion, and the required kill. **Nothing else in the suite noticed**, and
   that is the finding rather than a gap: the conformance cases fit on
   `distinct_residual_frame` at scikit-learn's own `min_samples_leaf`, where no
   fit crosses at the scored row, so a crossed model passes every conformance
   assertion. The acceptance test and the mutation target are the same test
   because nothing else can be.
2. **`random_state` removed with early stopping on.** `random_state=random_state`
   dropped from the estimator and `early_stopping=False` ->
   `early_stopping="auto"`. **Survives.** `"auto"` turns early stopping on only
   above 10 000 rows, and every fixture here is under fifty, so the validation
   split that would move between fits is never drawn and the fit stays
   deterministic. Dropping the seed alone, with `early_stopping=False` kept,
   also survives -- for the same reason and more plainly: with early stopping
   off this estimator draws nothing. The finding is that the reproducibility
   half of the acceptance test cannot see either defect at fixture size. What
   would see it is a fit on a panel-sized frame, which this block does not have
   and will not fabricate. Both settings stay, because the default they replace
   changes behaviour with the size of the input and a fixture is the one size
   at which that is invisible.
3. **The level refusal made a no-op.** `grid = _validate_levels(levels)` ->
   `grid = tuple(float(level) for level in levels)` in
   `fit_gradient_boosted_quantiles`. Kills the acceptance test alone,
   `AssertionError` -- but on the *phrase*, not on the refusal: scikit-learn
   raises `ValueError: quantile == 0.0, must be > 0.` from inside the estimator
   constructor, so a level of `0.0` is still refused. What the guard adds is
   that the refusal is this repository's sentence, is the same sentence every
   other model gives, and arrives **before** `_estimator_class()` -- so a caller
   on a checkout without the extra is told which argument is wrong rather than
   which package is missing.
4. **The minimum-history refusal deleted.** Kills the acceptance test and
   `GbmExceedanceTests::test_a_training_frame_below_the_minimum_is_refused`,
   both `AssertionError` -- the same refusal reached through the fitter and
   through the exceedance interface, which is the pair the interface exists to
   keep in step.
5. **Control, expected to survive**: `_TAIL_SHARE` 0.2 -> 0.25. Green
   throughout. The tail width is only reached when a row's own band escapes the
   fitted residual range, which no fixture here does -- so the constant is
   currently unpinned by any test, and that is recorded rather than papered
   over with an assertion invented to cover it.
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import random
import sys
import tempfile
import unittest
from datetime import date, time, timedelta
from fractions import Fraction
from unittest import mock

from repo_model import baseline, cli, cli_eval, ml
from repo_model.contract import QUANTILE_LEVELS
from repo_model.data import DailyObservation, load_daily_panel, load_stress_thresholds
from repo_model.event_eval import config_digest, read_journal
from repo_model.metrics import crps_from_quantiles
from repo_model.splits import SplitError

from test_baseline import (
    EXCEEDANCE_TAUS,
    ExceedancePredictorConformance,
    REGRESSORS,
)
from test_cli_eval import (
    DECISION_TIME,
    THRESHOLDS,
    ConditionalModelHarness,
    ContinuousModelHarness,
    business_days,
    declared_registry_file,
)
from test_contract import CONFORMANCE_REGRESSORS, ForecastInterfaceConformance

#: The variable a job that exists to exercise the extra sets. See the module
#: docstring: it is the only way this process can tell "no extra installed, and
#: that is fine" from "no extra installed, and that is the bug".
REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"


def _extra_installed() -> bool:
    """Is the `ml` extra importable here?

    `find_spec` rather than an import, because this module must import on an
    interpreter that has neither name -- see `tests/test_dependency_boundary.py`
    -- and the question is only whether the tests below can run.
    """

    return all(
        importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn")
    )


def require_extra(case: unittest.TestCase) -> None:
    """Skip, or fail if the caller declared the extra must be there."""

    if _extra_installed():
        return
    if os.environ.get(REQUIRE_ML):
        case.fail(
            f"{REQUIRE_ML} is set but the optional 'ml' extra (numpy, "
            f"scikit-learn) is not importable; a job that declares it must run "
            f"these tests fails rather than skipping them, because a skip count "
            f"is not something anything in this repository is allowed to read"
        )
    case.skipTest("the optional 'ml' extra is not installed")


def crossing_frame(count=48, seed=20260911):
    """A frame the per-level fits cross on, and how it is built to.

    Independent quantile fits are not constrained to be ordered. What makes them
    cross is a conditional distribution whose *shape* changes across a covariate
    while each level's fit is free to split the covariate somewhere else, so the
    rows near a split boundary are priced by different pieces of different
    trees.

    So: `on_rrp` takes two well-separated bands, one of them carrying a third of
    the rows, and the skew of the next-day spread **reverses** between them --
    a heavy left tail in the sparse low-`on_rrp` band, a heavy right tail in the
    dense high one. The 0.05 and 0.25 fits then have their evidence in one band
    and the 0.75 and 0.95 fits in the other, they split `on_rrp` at different
    thresholds, and on the rows between those thresholds the lower level's fit
    lands above the higher level's. `sofr_volume` moves with nothing and is
    there because the model, like the ARX, is fitted on a declared regressor set
    of more than one column.

    The crossing is *asserted* rather than assumed --
    `test_the_quantiles_are_ordered_and_reproducible_at_every_contract_level`
    reads the fits before rearrangement and fails if none of them cross -- for
    the reason `distinct_residual_frame` checks its own property: a fixture that
    stopped exhibiting the thing under test would leave the test green and
    empty.
    """

    rows = []
    state = seed
    for index in range(count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        draw = (state % 1000) / 1000.0
        stressed = (index % 6) in (0, 1)
        if stressed:
            on_rrp = 20.0 + (state % 37) / 10.0
            shock = -18.0 if draw < 0.30 else 1.0 + 2.0 * draw
        else:
            on_rrp = 120.0 + (state % 37) / 10.0
            shock = 16.0 if draw > 0.75 else -1.0 - 2.0 * draw
        spread = 30.0 + shock + 0.4 * (state % 97)
        rows.append(
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {
                    "sofr": 4.30 + spread / 100.0,
                    "iorb": 4.30,
                    "sofr_volume": 2100.0 + (state % 1301) / 3.0,
                    "on_rrp": on_rrp,
                },
            )
        )
    return rows


#: Small enough that a fixture-sized frame can be split at all. scikit-learn's
#: default of 20 needs 40 rows to make one split and every frame here is under
#: fifty, so at the default every level fit is a single leaf, every predicted
#: vector is the same on every row, and nothing about a *conditional* quantile
#: model would be under test. Not a tuned value -- tuning is not this block's.
FIXTURE_MIN_SAMPLES_LEAF = 3


class GradientBoostedQuantileTests(unittest.TestCase):
    """What the law is: block 9's acceptance criterion, and its mutation target.

    Paired with `GradientBoostedCompareTests`, which is a later block's and
    covers what the command does with this law rather than what the law is.
    Neither subsumes the other; the mutation record on that class says so with
    a mutation each of them sees alone.
    """

    REGRESSORS = ("sofr_volume", "on_rrp")
    MINIMUM_HISTORY = 20

    def setUp(self):
        require_extra(self)

    def fit(self, frame, **overrides):
        options = {
            "minimum_history": self.MINIMUM_HISTORY,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(frame, self.REGRESSORS, **options)

    def raw_vectors(self, model, rows):
        """Every row's per-level fits **before** rearrangement.

        Read off the fitted estimators directly, which is the only view of the
        model in which a crossing is still visible: everything the object
        reports goes through `_rearranged` and is sorted by the time a caller
        sees it.
        """

        vectors = []
        for row in rows:
            design = [float(value) for value in model.design_row(row)]
            vectors.append(
                tuple(
                    float(estimator.predict([design])[0])
                    for estimator in model._estimators
                )
            )
        return vectors

    def test_the_quantiles_are_ordered_and_reproducible_at_every_contract_level(self):
        """Crossing fits, rearranged; one seed, one answer; two refusals.

        Four claims, and they are one criterion rather than four because each is
        load-bearing only in the presence of the others. A model that never
        crossed would make the rearrangement untestable; a rearrangement that
        sorted a vector nobody could reproduce would order noise; and a fitter
        that accepted a level of `0.0` or a frame of nineteen rows would report
        an ordered, reproducible vector that means nothing.
        """

        rows = crossing_frame()
        model = self.fit(rows)

        # 1. The fixture does what it was built to do. Asserted, not assumed:
        #    a fixture that stopped crossing would leave claim 2 vacuous.
        raw = self.raw_vectors(model, rows)
        crossed = [
            vector
            for vector in raw
            if any(vector[i] > vector[i + 1] for i in range(len(vector) - 1))
        ]
        self.assertTrue(
            crossed,
            msg=(
                "no row's per-level fits cross before rearrangement, so the "
                "rearrangement below is not under test. See crossing_frame() "
                "for what the fixture is built to produce"
            ),
        )

        # 2. Every reported vector is non-decreasing across levels -- including
        #    on the rows that crossed, which is the whole of the claim.
        for row, before in zip(rows, raw):
            reported = model.predict(row)
            with self.subTest(day=row.date):
                self.assertEqual(len(reported), len(QUANTILE_LEVELS))
                for position in range(1, len(reported)):
                    self.assertLessEqual(
                        reported[position - 1],
                        reported[position],
                        msg=(
                            f"quantile {position} falls below quantile "
                            f"{position - 1} at {row.date}; the fits were "
                            f"{before} and the rearrangement did not order them"
                        ),
                    )
                self.assertEqual(reported, tuple(sorted(before)))

        # 3. Two fits with the same seed give identical predictions -- bit for
        #    bit, not nearly. A published record is re-scored by rerunning the
        #    fit, so "close" is a record that cannot be reproduced.
        again = self.fit(rows)
        self.assertEqual(
            [model.predict(row) for row in rows],
            [again.predict(row) for row in rows],
            msg=(
                "two fits of one model on one frame at one seed disagree; see "
                "ml.py on early_stopping='auto', which draws a validation split "
                "and moves the answer when nothing pins it"
            ),
        )
        self.assertEqual(model.residuals, again.residuals)

        # 4a. A level outside (0, 1), by its own phrase. The phrase is
        #     `metrics._validate_levels`' rather than a second one written here:
        #     what a quantile level may be is stated once in this repository.
        with self.assertRaisesRegex(ValueError, r"must be in \(0, 1\)"):
            self.fit(rows, levels=(0.0, 0.50, 0.95))
        with self.assertRaisesRegex(ValueError, r"must be in \(0, 1\)"):
            self.fit(rows, levels=(0.05, 0.50, 1.0))

        # 4b. Fewer rows than the model can fit, by its own phrase.
        with self.assertRaisesRegex(
            ValueError, r"gbm needs at least 20 training rows, got 19"
        ):
            self.fit(rows[:19])


def heteroscedastic_frame(count, seed=20260911):
    """A stationary spread whose next-day noise scale is today's `on_rrp`.

    `spread` is an AR(1) about 10 bp, and the shock that moves it from day `t`
    to day `t + 1` has scale `0.5 + 6 x^2`, where `x` is the uniform draw
    carried as day `t`'s `on_rrp`. So the conditional band is narrow on most
    rows and many times wider on a few, and it is *predictable* from the
    feature row -- which is what a conditional quantile model is for, and what
    lets boosted fits chase the in-sample tails on exactly the rows where the
    band is wide. `sofr_volume` moves with nothing.

    Stationary on purpose: the conformal guarantee is for calibration rows
    exchangeable with the rows scored, and a drifting series would make a
    miss here the fixture's fault rather than the calibration's. Drawn through
    `random.Random(seed).random()`, whose sequence is fixed across the Python
    versions `pyproject.toml` declares, with the normal shock by Box-Muller
    rather than `gauss`, so nothing depends on how a version turns uniforms
    into normals.
    """

    rng = random.Random(seed)
    rows = []
    spread = 10.0
    scale = rng.random()
    for index in range(count):
        first, second = rng.random(), rng.random()
        shock = math.sqrt(-2.0 * math.log(1.0 - first)) * math.cos(2.0 * math.pi * second)
        spread = 10.0 + 0.5 * (spread - 10.0) + (0.5 + 6.0 * scale * scale) * shock
        scale = rng.random()
        rows.append(
            DailyObservation(
                date(2020, 1, 1) + timedelta(days=index),
                {
                    "sofr": 4.30 + spread / 100.0,
                    "iorb": 4.30,
                    "on_rrp": scale,
                    "sofr_volume": 2000.0 + rng.random(),
                },
            )
        )
    return rows


class GradientBoostedConformalCalibrationTests(unittest.TestCase):
    """`calibration="conformal"`: B22's acceptance criterion and its mutation target.

    **The defect.** `FittedGradientBoostedQuantiles` reports each level as
    fitted, and boosted quantile fits are tight on the rows they were fitted
    on, so the `0.05`-`0.95` band under-covers out of sample. The published
    `docs/runs/backtest_gbm_mh61.json` is the measurement. Conformalized
    quantile regression (Romano, Patterson and Candes, 2019) is the repair,
    and its traps are all ways of calibrating on rows the fit already saw:
    scoring the fit rows (today's in-sample tail again), scoring the rows being
    forecast, refitting on the union after calibrating, and no purge between
    the fit and calibration slices.

    **The coverage tolerance, stated.** On held-out rows the realized coverage
    of a conformal band is a binomial count of `T` held-out rows whose success
    probability is itself random: given its `n` calibration scores the band's
    coverage is Beta-distributed about the nominal `q`, with variance near
    `q (1 - q) / (n + 2)`. The two add, so the tolerance is three standard
    deviations of both, `3 sqrt(q (1 - q) (1 / T + 1 / (n + 2)))`. Two-sided,
    because a band widened by too much covers too often and is as wrong as
    one widened by too little. **The control must fail it**: the uncalibrated
    band's coverage is asserted to be below the tolerance's lower edge, so a
    fixture on which the in-sample band already covered could not leave this
    test green and empty.

    **Where the gap comes from.** The fitter cannot derive the purge: it is
    handed rows, not a registry. `cli_eval` does not bind it either, because
    that module never holds the number. The fold loop derived it, so the fold
    loop hands it over -- `baseline._fit_at_origin`, to a fitter whose
    signature names `purge_days` -- and the slices subtest runs through
    `rolling_persistence_backtest` for that reason.

    Mutation record (B22)
    ---------------------

    Two per-branch, per-commit copies under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B` (the worktree's `.venv`: CPython 3.9.6, numpy 2.0.2,
    scikit-learn 1.6.1), `REPO_MODEL_REQUIRE_ML=1`, whole suite per run.
    `repo_model` was checked to resolve to the copy's `src/` before every run:
    the `.venv` also carries an installed, non-editable `repo_model` in
    `site-packages`, and a run without `PYTHONPATH=src` scores that copy
    instead of the tree. Unmutated control green before and after in each
    copy, zero `expectedFailure`; each mutation's anchor found exactly once,
    confirmed gone once applied, and restored before the next. **Every
    mutation killed this test and nothing else.**

      * **The widening set to 0.** `widening = 0.0` in place of the conformal
        score. `coverage on held-out rows`, `AssertionError`: the band covers
        0.650, the uncalibrated figure exactly.
      * **Calibration scores computed on the fit rows** -- the in-sample
        one-step pairs the estimators were fitted on, scored in place of the
        calibration rows. `coverage on held-out rows`, `AssertionError`:
        widening 0.004, coverage 0.650. This is today's in-sample residual
        tail, and a widening that small is the reason it under-covers.
      * **The conformal rank replaced by the median score.** `coverage on
        held-out rows`, `AssertionError`: widening -0.203, coverage 0.608 --
        below the uncalibrated band, because the median score narrows it.
      * **The purge between slices removed** -- the fit rows every row before
        the calibration slice. Every fold of `the slices of every fold`,
        `AssertionError` (`the last fit row 2020-02-02 is inside the 6-day gap
        before the calibration rows open on 2020-02-03`), and `refusal: a gap
        that leaves nothing to fit`, `AssertionError` on the phrase: with no
        purge there are fit rows, and the refusal that fires instead is
        `_feature_index`'s `LookAheadError` for a calibration row with no
        feature row behind the gap. Coverage stays green, as it must at a
        zero gap; that is why the slices are a subtest of their own.
      * **The fold loop withholds the gap** -- `_fit_at_origin` never passes
        `purge_days`. `the slices of every fold`, `TypeError: calibrating()
        missing 1 required positional argument: 'purge_days'`, and the
        declaration subtest after it, `UnboundLocalError` on `report` --
        collateral from the order of the subtests, not a second finding.
      * **The settings not read off an ml fit** -- the `model_settings` line
        dropped from `baseline._model_settings`. `the declaration names the
        calibration`, `AssertionError: {} != {'calibration': 'conformal',
        'calibration_share': 0.25}`.
      * **Each refusal removed**, separately:
          - fewer than 9 calibration rows: `IndexError` out of the rank, an
            error rather than a failure -- the rank names a score that does
            not exist, which is the infinite quantile the refusal names;
          - a share outside `(0, 1)`: `AssertionError` on the phrase, since a
            share of 0 then falls through to the calibration-row refusal;
          - an unknown calibration: `AssertionError: ValueError not raised`,
            the misspelt name fitted as `conformal`;
          - calibration settings for a model other than gbm (`cli_eval.
            _calibration`): `AssertionError: SplitError not raised`;
          - a share given to `none`: `AssertionError: ValueError not raised`;
          - `conformal` with no gap: `TypeError: unsupported type for
            timedelta days component: NoneType`, out of `clears_purge`;
          - a gap that leaves fewer than two fit rows: `IndexError`, out of the
            imputation's refusal reaching for a first origin that is not there.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    #: The declaration the fold-loop subtest sizes its gap over: the
    #: autoregressive term and both regressors.
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    TRAIN_ROWS = 480
    HELD_OUT_ROWS = 240
    #: A gap the registry fixture prices in calendar days. Nonzero, or the
    #: purge between slices is not under test.
    PURGE = 6

    def setUp(self):
        require_extra(self)

    def fit(self, frame, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(frame, self.REGRESSORS, **options)

    @staticmethod
    def held_out_coverage(model, rows, first_held_out):
        """Share of held-out rows inside the model's outer band, one step ahead.

        Each held-out row is forecast from the row before it, through the
        model's own `predict` -- the vector a backtest reads its interval off.
        """

        covered = 0
        for index in range(first_held_out, len(rows)):
            vector = model.predict(rows[index - 1])
            covered += vector[0] <= rows[index].spread_bps <= vector[-1]
        return covered / (len(rows) - first_held_out)

    def test_the_calibrated_band_covers_its_nominal_probability_out_of_sample(self):
        """Covers where the fitted band does not; purged slices; six refusals.

        One criterion. A coverage figure from a calibration that could see its
        fit rows would be the defect with a better number, and a calibration
        that accepted eight calibration rows or a share of 1.0 would report a
        band with no guarantee behind it at all.
        """

        rows = heteroscedastic_frame(self.TRAIN_ROWS + self.HELD_OUT_ROWS)
        train = rows[: self.TRAIN_ROWS]
        nominal = QUANTILE_LEVELS[-1] - QUANTILE_LEVELS[0]

        with self.subTest("coverage on held-out rows"):
            uncalibrated = self.fit(train)
            calibrated = self.fit(train, calibration="conformal", purge_days=0)
            scores = int(ml.DEFAULT_CALIBRATION_SHARE * self.TRAIN_ROWS)
            tolerance = 3.0 * math.sqrt(
                nominal * (1.0 - nominal) * (1.0 / self.HELD_OUT_ROWS + 1.0 / (scores + 2))
            )
            before = self.held_out_coverage(uncalibrated, rows, self.TRAIN_ROWS)
            after = self.held_out_coverage(calibrated, rows, self.TRAIN_ROWS)
            self.assertLess(
                before,
                nominal - tolerance,
                msg=(
                    f"the control: the uncalibrated band covers {before:.3f} of "
                    f"{self.HELD_OUT_ROWS} held-out rows, inside the tolerance "
                    f"{nominal:.2f} +/- {tolerance:.3f}, so this fixture cannot "
                    f"tell a calibration from its absence"
                ),
            )
            self.assertLessEqual(
                abs(after - nominal),
                tolerance,
                msg=(
                    f"the conformal band covers {after:.3f} of "
                    f"{self.HELD_OUT_ROWS} held-out rows against a nominal "
                    f"{nominal:.2f} +/- {tolerance:.3f} (widening "
                    f"{calibrated.widening:.3f}; uncalibrated {before:.3f})"
                ),
            )

        with self.subTest("the slices of every fold"):
            # Through the rolling fold loop, so the gap is the one the loop
            # derived from the registry and handed over -- not one this test
            # chose and passed in.
            panel = heteroscedastic_frame(58)
            with tempfile.TemporaryDirectory() as directory:
                registry = json.loads(
                    declared_registry_file(
                        directory, purge=self.PURGE, features=self.FEATURES
                    ).read_text(encoding="utf-8")
                )
            fits = []

            def calibrating(train_frame, minimum_history, purge_days):
                model = self.fit(
                    train_frame,
                    minimum_history=minimum_history,
                    calibration="conformal",
                    purge_days=purge_days,
                )
                fits.append((train_frame, purge_days, model))
                return model

            report = baseline.rolling_persistence_backtest(
                panel,
                features=self.FEATURES,
                registry=registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                minimum_history=44,
                fit_model=calibrating,
            )
            self.assertGreater(
                report.purge_days, 0, msg="at a zero gap the purge is not under test"
            )
            self.assertEqual(len(fits), len(report.folds))
            for fold, (frame, purge, model) in zip(report.folds, fits):
                with self.subTest(fold=fold.scored_date.isoformat()):
                    self.assertEqual(purge, report.purge_days)
                    self.assertEqual(model.calibration_end, frame[-1].date)
                    self.assertLess(model.calibration_end, fold.scored_date)
                    self.assertEqual(
                        sum(row.date >= model.calibration_start for row in frame),
                        int(ml.DEFAULT_CALIBRATION_SHARE * len(frame)),
                        msg="the calibration rows are not the frame's most recent share",
                    )
                    self.assertLess(
                        model.fit_end + timedelta(days=report.purge_days),
                        model.calibration_start,
                        msg=(
                            f"the last fit row {model.fit_end} is inside the "
                            f"{report.purge_days}-day gap before the calibration "
                            f"rows open on {model.calibration_start}"
                        ),
                    )

            # The fit rows are what the model says: a fit on the frame up to
            # `fit_end` reports the same interior levels bit for bit. A refit on
            # the union after calibrating would not.
            frame, _, model = fits[-1]
            feature_row = next(row for row in panel if row.date == report.folds[-1].feature_date)
            refit = self.fit([row for row in frame if row.date <= model.fit_end])
            self.assertEqual(
                model.predict(feature_row)[1:-1], refit.predict(feature_row)[1:-1]
            )

        with self.subTest("the declaration names the calibration, and only when there is one"):
            # What `backtest_document` and `paired_comparison_document` publish
            # is the report's `model_settings`, read off the first fit.
            self.assertEqual(
                dict(report.model_settings),
                {"calibration": "conformal", "calibration_share": 0.25},
            )
            # Absent, not "none": an uncalibrated gbm declares what every gbm
            # record published before calibration existed declares.
            self.assertEqual(dict(baseline._model_settings(uncalibrated)), {})

        with self.subTest("refusal: fewer calibration rows than the quantile needs"):
            with self.assertRaisesRegex(
                ValueError, r"needs at least 9 calibration rows, got 8"
            ):
                self.fit(rows[:35], calibration="conformal", purge_days=0)
            # And nine is enough: the refusal sits at the edge, not above it.
            self.assertEqual(
                self.fit(rows[:36], calibration="conformal", purge_days=0).calibration_start,
                rows[27].date,
            )

        with self.subTest("refusal: a share outside (0, 1)"):
            for share in (0.0, 1.0, -0.25, 1.25):
                with self.assertRaisesRegex(ValueError, r"strictly inside \(0, 1\)"):
                    self.fit(
                        train,
                        calibration="conformal",
                        calibration_share=share,
                        purge_days=0,
                    )

        with self.subTest("refusal: an unknown calibration"):
            with self.assertRaisesRegex(ValueError, r"unknown calibration 'isotonic'"):
                self.fit(rows[:36], calibration="isotonic", purge_days=0)

        with self.subTest("refusal: a share given to calibration none"):
            with self.assertRaisesRegex(ValueError, r"'none' holds no rows out"):
                self.fit(rows[:36], calibration_share=0.25)

        with self.subTest("refusal: conformal with no gap"):
            with self.assertRaisesRegex(SplitError, r"purge must be an int, got None"):
                self.fit(rows[:36], calibration="conformal")

        with self.subTest("refusal: a gap that leaves nothing to fit"):
            with self.assertRaisesRegex(ValueError, r"leaves 0 fit row\(s\) of 40"):
                self.fit(rows[:40], calibration="conformal", purge_days=40)

        with self.subTest("refusal: calibration settings for a model other than gbm"):
            parser = cli.build_parser()
            common = ["--registry", "registry.json", "--decision-time", DECISION_TIME]
            backtest = parser.parse_args(
                ["backtest", "panel.csv", *common, "--report", "r.json",
                 "--feature", "spread_bps", "--model", "arx",
                 "--calibration", "conformal"]
            )
            with self.assertRaisesRegex(
                SplitError, r"--calibration conformal was given, but --model arx"
            ):
                cli_eval._select_fitter(backtest)

            compare = parser.parse_args(
                ["compare", "panel.csv", *common, "--report", "r.json",
                 "--model-a", "persistence", "--feature-a", "spread_bps",
                 "--calibration-share-a", "0.3",
                 "--model-b", "gbm", "--feature-b", "spread_bps",
                 "--calibration-b", "conformal"]
            )
            with self.assertRaisesRegex(
                SplitError,
                r"--calibration-share-a 0.3 was given, but --model-a persistence",
            ):
                cli_eval._select_fitter(cli_eval._side(compare, "a"), side="-a")
            # The same flags on the gbm side are taken, and reach the fitter.
            _, fitter = cli_eval._select_fitter(cli_eval._side(compare, "b"), side="-b")
            self.assertEqual(fitter.keywords.get("calibration"), "conformal")


def business_day_frame(count, seed=20260911):
    """`heteroscedastic_frame`'s rows, re-dated onto weekdays.

    Weekdays so that a row's predecessor is not always the calendar day before
    it: a lag read by calendar day and a lag read by row then disagree on every
    window that spans a weekend, and the test below asserts its window does.
    """

    return [
        DailyObservation(when, row.values)
        for when, row in zip(
            business_days(date(2020, 1, 1), count), heteroscedastic_frame(count, seed)
        )
    ]


def with_spread_shifted(row, bps):
    """`row` with its spread moved by `bps`, through `sofr`, the leg it is read off."""

    values = dict(row.values)
    values["sofr"] = values["sofr"] + bps / 100.0
    return DailyObservation(row.date, values)


class GradientBoostedLaggedSpreadTests(unittest.TestCase):
    """`spread_change_lags`: B23's acceptance criterion and its mutation target.

    **The design problem.** The forecast interface hands a model one feature
    row, and a lagged change needs the rows before it. They are the training
    frame's own: the fitted model keeps the frame's dates and spreads and reads
    a feature row's lags back by that row's position in the frame. The fold
    loop's feature row is always the frame's last row, so the probe below --
    every row after the feature date changed, the forecast bit-identical --
    holds because nothing after the feature date reaches the model at all. The
    leak that remains possible is *inside* the design, where a training row's
    successor is its target; the design-row subtest reads the lag values off the
    fitted model against changes computed here from rows at or before the
    feature row, and that is what sees it.

    **A finding about holes.** A spread hole cannot reach this model through any
    published path: `load_daily_panel` refuses a row without `sofr` or `iorb`,
    and build rule 6 does not make such a date a row. In a frame built by hand,
    a hole is readable only where nothing but the lag reader reads the row --
    among the first `k`, which start changes and are not design rows. Anywhere
    later the same row is a target and an autoregressive term, which gbm reads
    as it always has, lags or none. The hole subtest is therefore placed there,
    with observed rows on both sides, so a difference across the hole is a
    number and not a missing one.

    Mutation record (B23)
    ---------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B` (the worktree's `.venv`: CPython 3.9.6, numpy 2.0.2,
    scikit-learn 1.6.1), `PYTHONPATH=src` (checked to resolve to the copy),
    `REPO_MODEL_REQUIRE_ML=1`, `OMP_NUM_THREADS=1`, whole suite per run.
    Unmutated control green before and after, zero `expectedFailure`; each
    mutation's anchor found exactly once, confirmed applied, and restored and
    confirmed restored before the next. **Every mutation killed this test and
    nothing else.**

      * **Lag 1 read from the scored row** -- `spreads[position + 1] -
        spreads[position]`, `None` where there is no next row. `the design
        names carry the lags in lag order`, `AssertionError` on the lag
        columns. **The leakage probe survives it, and that is the design's
        finding, not a gap:** the fold loop's feature row is the frame's last
        row, so the next row is not there to read and the mutant's lag 1 is
        imputed at the forecast. The leak lives in the training design, where
        every row's next row is its target, and only the values of the design
        row see that.
      * **Difference taken across a hole** -- the earlier end of each change
        the last observed spread at or before it. `a hole one row back is a
        missing change`, `AssertionError`: lag 1 is the difference across the
        hole, not its imputation.
      * **The declaration key dropped** from `model_settings`. `the
        declaration names spread_change_lags, and only when set`,
        `AssertionError: {} != {'spread_change_lags': 5}`.
      * **Each refusal removed**, separately:
          - a lag below 1: `AssertionError: ValueError not raised` -- a lag of
            0 fits a model with no lag columns that declares one;
          - lags for a model other than gbm (`cli_eval._spread_change_lags`):
            `AssertionError: SplitError not raised`;
          - no training row with every lag defined: `IndexError`, an error
            rather than a failure, out of the regressor imputation's own
            refusal message reaching for the first of no origins;
          - a feature row the fitted frame does not carry (extra):
            `AssertionError: ValueError not raised` -- a row dated after the
            frame is handed the frame's last rows as its lags;
          - a position with fewer rows before it than lags (extra, in
            `_spread_changes`): `AssertionError: ValueError not raised` on the
            same subtest. A negative index wraps to the end of the frame, so
            without it the oldest lags of an early row are read off the latest
            rows, silently.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    #: Five, so a lag window of six rows spans a weekend wherever it falls.
    LAGS = 5
    PANEL_ROWS = 50
    MINIMUM_HISTORY = 40
    #: Nonzero, so the scored day is not the row after the feature row and the
    #: probe's changed rows include the gap as well as the scored day.
    PURGE = 6

    def setUp(self):
        require_extra(self)
        with tempfile.TemporaryDirectory() as directory:
            self.registry = json.loads(
                declared_registry_file(
                    directory, purge=self.PURGE, features=self.FEATURES
                ).read_text(encoding="utf-8")
            )

    def fit(self, frame, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(frame, self.REGRESSORS, **options)

    def backtest(self, panel, **settings):
        """The rolling fold loop over `panel`, and every model it fitted."""

        fits = []

        def fitter(train_frame, minimum_history, purge_days):
            model = self.fit(
                train_frame,
                minimum_history=minimum_history,
                purge_days=purge_days,
                **settings,
            )
            fits.append(model)
            return model

        report = baseline.rolling_persistence_backtest(
            panel,
            features=self.FEATURES,
            registry=self.registry,
            decision_time=time.fromisoformat(DECISION_TIME),
            minimum_history=self.MINIMUM_HISTORY,
            fit_model=fitter,
        )
        return report, fits

    def test_lagged_spread_changes_read_only_rows_at_or_before_the_feature_date(self):
        """A probe, the design row, a hole, the declaration and the refusals.

        One criterion: a lag column that leaked, bridged a hole, went unnamed
        in the record or accepted a lag of zero would each be a model reading
        something other than the spread's path up to the day it forecasts from.
        """

        panel = business_day_frame(self.PANEL_ROWS)
        dates = [row.date for row in panel]
        report, fits = self.backtest(panel, spread_change_lags=self.LAGS)
        fold = report.folds[0]
        feature = dates.index(fold.feature_date)

        with self.subTest("leakage probe"):
            self.assertGreater(
                report.purge_days, 0, msg="at a zero gap the scored day is the next row"
            )
            self.assertLess(fold.feature_date, fold.scored_date)
            # Every row after the feature date: the gap, the scored day, and
            # every later row.
            later = panel[: feature + 1] + [
                with_spread_shifted(row, 25.0) for row in panel[feature + 1 :]
            ]
            again, _ = self.backtest(later, spread_change_lags=self.LAGS)
            self.assertEqual(again.folds[0], fold)
            self.assertEqual(
                (again.forecasts[0].predicted_bps, again.forecasts[0].quantiles_bps),
                (report.forecasts[0].predicted_bps, report.forecasts[0].quantiles_bps),
                msg=(
                    f"the forecast from {fold.feature_date} moved when only rows "
                    f"after it changed"
                ),
            )
            back = (
                panel[: feature - 1]
                + [with_spread_shifted(panel[feature - 1], 25.0)]
                + panel[feature:]
            )
            moved, _ = self.backtest(back, spread_change_lags=self.LAGS)
            self.assertNotEqual(
                moved.forecasts[0].quantiles_bps,
                report.forecasts[0].quantiles_bps,
                msg="the row one lag back changed and the forecast did not move",
            )

        with self.subTest("the design names carry the lags in lag order"):
            model = fits[0]
            self.assertEqual(
                model.design_names,
                ("spread_bps",)
                + self.REGRESSORS
                + tuple(f"spread_change_lag_{lag}" for lag in range(1, self.LAGS + 1)),
            )
            # The lag columns read `spread_bps`, which is already declared; a
            # lag name here would be a column no source prices.
            self.assertEqual(model.features_read, ("spread_bps",) + self.REGRESSORS)
            # By row: the window spans a weekend, so calendar-day lags differ.
            self.assertGreater(
                (dates[feature] - dates[feature - self.LAGS]).days, self.LAGS
            )
            spreads = [row.spread_bps for row in panel[: feature + 1]]
            expected = tuple(
                spreads[feature - lag + 1] - spreads[feature - lag]
                for lag in range(1, self.LAGS + 1)
            )
            self.assertEqual(
                model.design_row(panel[feature])[-self.LAGS :],
                expected,
                msg="the lag columns are not the changes ending at the feature row",
            )

        with self.subTest("a hole one row back is a missing change"):
            frame = business_day_frame(24)
            hole = dict(frame[1].values)
            hole["sofr"] = None
            holed = [frame[0], DailyObservation(frame[1].date, hole)] + frame[2:]
            model = self.fit(holed, spread_change_lags=2)
            design = model.design_row(holed[2])
            self.assertEqual(
                design[-2:],
                (
                    model.imputations["spread_change_lag_1"],
                    model.imputations["spread_change_lag_2"],
                ),
            )
            self.assertNotEqual(
                design[-2],
                holed[2].spread_bps - holed[0].spread_bps,
                msg="lag 1 was differenced across the hole",
            )

        with self.subTest("the declaration names spread_change_lags, and only when set"):
            self.assertEqual(
                dict(report.model_settings), {"spread_change_lags": self.LAGS}
            )
            calibrated, _ = self.backtest(
                panel, spread_change_lags=self.LAGS, calibration="conformal"
            )
            self.assertEqual(
                dict(calibrated.model_settings),
                {
                    "calibration": "conformal",
                    "calibration_share": 0.25,
                    "spread_change_lags": self.LAGS,
                },
            )
            plain = self.fit(panel[:30])
            self.assertEqual(dict(baseline._model_settings(plain)), {})
            self.assertEqual(plain.design_names, ("spread_bps",) + self.REGRESSORS)

        with self.subTest("refusal: a lag below 1"):
            with self.assertRaisesRegex(
                ValueError, r"spread_change_lags must be an int of at least 1, got 0"
            ):
                self.fit(panel[:30], spread_change_lags=0)
            with self.assertRaisesRegex(
                ValueError, r"spread_change_lags must be an int of at least 1, got -1"
            ):
                self.fit(panel[:30], spread_change_lags=-1)

        with self.subTest("refusal: lags for a model other than gbm"):
            parser = cli.build_parser()
            common = ["--registry", "registry.json", "--decision-time", DECISION_TIME]
            backtest = parser.parse_args(
                ["backtest", "panel.csv", *common, "--report", "r.json",
                 "--feature", "spread_bps", "--model", "arx",
                 "--spread-change-lags", "1"]
            )
            with self.assertRaisesRegex(
                SplitError, r"--spread-change-lags 1 was given, but --model arx"
            ):
                cli_eval._select_fitter(backtest)
            compare = parser.parse_args(
                ["compare", "panel.csv", *common, "--report", "r.json",
                 "--model-a", "persistence", "--feature-a", "spread_bps",
                 "--spread-change-lags-a", "5",
                 "--model-b", "gbm", "--feature-b", "spread_bps",
                 "--spread-change-lags-b", "5", "--calibration-b", "conformal"]
            )
            with self.assertRaisesRegex(
                SplitError,
                r"--spread-change-lags-a 5 was given, but --model-a persistence",
            ):
                cli_eval._select_fitter(cli_eval._side(compare, "a"), side="-a")
            # On the gbm side it is taken, and composes with --calibration.
            _, fitter = cli_eval._select_fitter(cli_eval._side(compare, "b"), side="-b")
            self.assertEqual(
                fitter.keywords,
                {
                    "regressors": (),
                    "calibration": "conformal",
                    "spread_change_lags": 5,
                },
            )

        with self.subTest("refusal: no training row with every lag defined"):
            with self.assertRaisesRegex(
                ValueError,
                r"spread_change_lags 23 leaves no training row with every lag defined",
            ):
                self.fit(panel[:24], spread_change_lags=23)

        with self.subTest("refusal: a feature row the fitted frame does not carry"):
            model = self.fit(panel[:30], spread_change_lags=self.LAGS)
            with self.assertRaisesRegex(
                ValueError, r"is not a row of the frame this model was fitted on"
            ):
                model.design_row(panel[30])
            with self.assertRaisesRegex(
                ValueError, r"need 5 rows before it and its frame has 3"
            ):
                model.design_row(panel[3])


#: The GARCH(1,1) the fixtures below simulate: persistence 0.95, unconditional
#: variance 1 bp squared.
GARCH_TRUTH = (0.05, 0.10, 0.85)


def standard_normals(rng):
    """Box-Muller off `rng.random()`, for `heteroscedastic_frame`'s reason."""

    while True:
        first, second = rng.random(), rng.random()
        yield math.sqrt(-2.0 * math.log(1.0 - first)) * math.cos(2.0 * math.pi * second)


def garch_spreads(changes, parameters=GARCH_TRUTH, seed=20260911):
    """`changes + 1` spreads whose changes are a zero-mean GARCH(1,1) path.

    Started at the unconditional variance, so the path has no transient for the
    fit's own starting variance to disagree with.
    """

    omega, alpha, beta = parameters
    variance = omega / (1.0 - alpha - beta)
    spreads = [10.0]
    shocks = standard_normals(random.Random(seed))
    for _ in range(changes):
        change = math.sqrt(variance) * next(shocks)
        spreads.append(spreads[-1] + change)
        variance = omega + alpha * change * change + beta * variance
    return spreads


def garch_frame(count, seed=20260911):
    """Weekday rows whose spread follows `garch_spreads`; two inert regressors."""

    rng = random.Random(seed + 1)
    return [
        DailyObservation(
            when,
            {
                "sofr": 4.30 + spread / 100.0,
                "iorb": 4.30,
                "on_rrp": rng.random(),
                "sofr_volume": 2000.0 + rng.random(),
            },
        )
        for when, spread in zip(
            business_days(date(2020, 1, 1), count), garch_spreads(count - 1, seed=seed)
        )
    ]


def recursion_variances(frame, parameters, initial):
    """`f_t` for every row of `frame`, computed here from rows at or before `t`.

    Written out rather than read from `ml`, in the same arithmetic order, so a
    value that agrees with it bit for bit is the recursion the module docstring
    states and not whatever the module's helper happens to do.
    """

    omega, alpha, beta = parameters
    variances = []
    previous = initial
    for position, row in enumerate(frame):
        if position == 0:
            shock = previous
        else:
            change = row.spread_bps - frame[position - 1].spread_bps
            shock = change * change
        previous = omega + alpha * shock + beta * previous
        variances.append(previous)
    return variances


def with_column(frame, name, values):
    """`frame` with `values` carried as the panel column `name`."""

    return [
        DailyObservation(row.date, dict(row.values, **{name: value}))
        for row, value in zip(frame, values)
    ]


class GradientBoostedGarchFeatureTests(unittest.TestCase):
    """`volatility_feature="garch11"`: B24's acceptance criterion and its mutation target.

    **The traps.** A GARCH fitted once on the panel (every fold then reads
    parameters estimated on its own future); a variance at row `t` that reads
    the change into `t + 1`, which for a training row is its target; and a
    constant variance quietly standing in for a fit that failed.

    **What the leakage probe can and cannot see.** As B23 found for the lags,
    the probe -- every row after the feature date changed, the forecast and the
    parameters bit-identical -- holds by construction: the fold loop hands the
    fitter a frame that ends at the feature row. The leak that remains possible
    is inside the training design, where a row's successor is its target. So
    the leakage subtest also fits the gbm a second time with the variance
    computed *here*, from rows at or before each row, declared as an ordinary
    regressor: the two models must agree bit for bit, residual sample included,
    and the residual sample is read off every training design row.

    **The recovery tolerance, stated.** `RECOVERY_CHANGES` changes of
    `GARCH_TRUTH`. Measured across twenty seeds at that length the estimates'
    standard deviations are about 0.012 (omega), 0.011 (alpha) and 0.020
    (beta), and every seed fell within `RECOVERY_TOLERANCE` -- roughly three of
    them. The stationarity half of the subtest is on a series whose variance
    steps up sixfold halfway: the quasi-likelihood's unconstrained maximum there
    is explosive, and the control asserts the fitted `alpha + beta` sits on the
    boundary, so a series on which the constraint did not bind could not leave
    it green and empty.

    **The minimum.** `ml.GARCH_MINIMUM_CHANGES`, thirty observed changes among
    the fit rows: ten per parameter.

    Mutation record (B24)
    ---------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, one sub-copy per mutation,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B` (the worktree's `.venv`: CPython
    3.9.6, numpy 2.0.2, scikit-learn 1.6.1), `PYTHONPATH=src` (checked to
    resolve to each copy), `REPO_MODEL_REQUIRE_ML=1`, `OMP_NUM_THREADS=1`,
    whole suite per run. Unmutated control green before and after, zero
    `expectedFailure`; each anchor found exactly once and confirmed applied.
    Every failure below is `AssertionError` unless named otherwise, and
    **every mutation but the first killed this test and nothing else.**

      * **GARCH fitted on the frame through the scored row** -- the fold loop
        hands the fitter `rows[: index + 1]` in place of the purged training
        rows (`baseline.rolling_persistence_backtest`). `leakage`: the
        parameters and the forecast move when only rows after the feature date
        change. Twenty-one other failures across `test_contract`,
        `test_baseline`, `test_generated_results` and both earlier gbm classes,
        because the frame is every model's. The fitter is handed a frame and
        never a panel, so this is the only door a whole-panel fit has.
      * **The variance recursion shifted one row forward** -- `f_p` reads the
        change into `p + 1` (`_garch_variances`). `recovery` (omega 0.0005
        against 0.05), `leakage` and the calibration subtest (the design-row
        variances against the recursion computed here).
      * **The training design reads the target row's variance** --
        `variances[index]` for `variances[index - 1]` (extra; the trap as the
        brief states it). `leakage` (the residual sample against the declared
        reference) and the calibration subtest (the widening). **Found on the
        first run:** with the reference fitted on a fold's forty-row frame,
        `leakage` did not see this -- no level's trees split on the column, so
        a late column fitted the same trees. The reference moved to the
        eighty-row frame, with a control that the late column changes the fit
        there, and the whole record was re-run on the final test.
      * **Calibration rows refitted** -- the GARCH fitted on the whole frame
        under `conformal`. The calibration subtest: the parameters are not the
        fit rows' own.
      * **The stationarity constraint dropped.** `recovery`: `alpha + beta`
        1.080 on the stepped series. No fold's optimum is outside, so nothing
        else sees it.
      * **A single global fit** -- the first fit's parameters cached for the
        process (extra). `per fold` (two folds, one GARCH; a later fold's
        parameters not its own frame's), `leakage` and the calibration subtest.
      * **The declaration key dropped** from `model_settings`. `the
        declaration names volatility_feature; absent when not set`,
        `{} != {'volatility_feature': 'garch11'}`.
      * **Each refusal removed**, separately:
          - an unknown value: `ValueError not raised` -- `garch12` fitted as
            today's gbm under a declaration naming a volatility model;
          - the setting on a model other than gbm (`cli_eval.
            _volatility_feature`): `SplitError not raised`;
          - fewer than 30 observed changes: `ValueError not raised`;
          - a search that does not converge: `ValueError not raised` -- the
            parameters where the fifth iteration left them are used;
          - every observed change zero (extra): `AssertionError` on the phrase.
            The fit is still refused, by `ValueError: math domain error` out of
            `math.log` on a zero variance; what the guard adds is that the
            refusal says why, before a logarithm does.

    **A finding about short frames.** On the forty- to sixty-row frames here,
    drawn from `GARCH_TRUTH`, the quasi-likelihood's maximum sits at omega of
    order 1e-15 with alpha near zero and beta just below one: the variance is
    a slow decay from `f_-1`, not a clustering estimate. Converged, inside the
    constraints, and what the estimator says at that length; recorded because
    the first folds of a `--minimum-history 61` run are frames of that size.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    PANEL_ROWS = 50
    MINIMUM_HISTORY = 40
    PURGE = 6
    RECOVERY_CHANGES = 5000
    RECOVERY_TOLERANCE = (0.04, 0.04, 0.07)
    CALIBRATION_ROWS = 80

    def setUp(self):
        require_extra(self)
        with tempfile.TemporaryDirectory() as directory:
            self.registry = json.loads(
                declared_registry_file(
                    directory, purge=self.PURGE, features=self.FEATURES
                ).read_text(encoding="utf-8")
            )

    def fit(self, frame, regressors=None, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(
            frame, self.REGRESSORS if regressors is None else regressors, **options
        )

    def backtest(self, panel, **settings):
        """The rolling fold loop over `panel`, and every frame and model it fitted."""

        frames, fits = [], []

        def fitter(train_frame, minimum_history, purge_days):
            model = self.fit(
                train_frame,
                minimum_history=minimum_history,
                purge_days=purge_days,
                **settings,
            )
            frames.append(list(train_frame))
            fits.append(model)
            return model

        report = baseline.rolling_persistence_backtest(
            panel,
            features=self.FEATURES,
            registry=self.registry,
            decision_time=time.fromisoformat(DECISION_TIME),
            minimum_history=self.MINIMUM_HISTORY,
            fit_model=fitter,
        )
        return report, frames, fits

    def test_the_garch_variance_is_fitted_per_fold_on_rows_at_or_before_the_feature_date(self):
        """Recovery, leakage, per fold, calibration, the declaration, four refusals.

        One criterion: a variance fitted on the wrong rows, read one row late,
        refitted on the rows it is calibrated against, unnamed in the record, or
        standing in for a fit that failed is each a column that is not the
        spread's conditional variance up to the day it forecasts from.
        """

        panel = garch_frame(self.PANEL_ROWS)
        dates = [row.date for row in panel]
        report, frames, fits = self.backtest(panel, volatility_feature="garch11")
        fold = report.folds[0]
        feature = dates.index(fold.feature_date)

        calibration_frame = garch_frame(self.CALIBRATION_ROWS)
        calibrated = self.fit(
            calibration_frame,
            volatility_feature="garch11",
            calibration="conformal",
            purge_days=0,
        )

        with self.subTest("recovery"):
            fitted, _ = ml._fit_garch11(
                garch_spreads(self.RECOVERY_CHANGES), "fit rows"
            )
            for name, estimate, truth, tolerance in zip(
                ("omega", "alpha", "beta"), fitted, GARCH_TRUTH, self.RECOVERY_TOLERANCE
            ):
                self.assertLessEqual(
                    abs(estimate - truth),
                    tolerance,
                    msg=(
                        f"{name} fitted {estimate:.4f} on {self.RECOVERY_CHANGES} "
                        f"simulated changes against a true {truth} +/- {tolerance}"
                    ),
                )
            # Stationarity, on a series whose unconstrained maximum is explosive.
            shocks = standard_normals(random.Random(7))
            stepped = [0.0]
            for index in range(200):
                stepped.append(stepped[-1] + (1.0 if index < 100 else 6.0) * next(shocks))
            omega, alpha, beta = ml._fit_garch11(stepped, "fit rows")[0]
            self.assertGreater(
                alpha + beta,
                0.999,
                msg=(
                    "the control: the stationarity constraint does not bind on "
                    "this series, so it is not under test"
                ),
            )
            self.assertLess(alpha + beta, 1.0)
            self.assertGreater(omega, 0.0)
            self.assertGreaterEqual(min(alpha, beta), 0.0)

        with self.subTest("leakage"):
            self.assertGreater(
                report.purge_days, 0, msg="at a zero gap the scored day is the next row"
            )
            later = panel[: feature + 1] + [
                with_spread_shifted(row, 25.0) for row in panel[feature + 1 :]
            ]
            again, _, again_fits = self.backtest(later, volatility_feature="garch11")
            self.assertEqual(again.folds[0], fold)
            self.assertEqual(
                (
                    again_fits[0].garch_parameters,
                    again_fits[0].garch_initial_variance,
                    again.forecasts[0].predicted_bps,
                    again.forecasts[0].quantiles_bps,
                ),
                (
                    fits[0].garch_parameters,
                    fits[0].garch_initial_variance,
                    report.forecasts[0].predicted_bps,
                    report.forecasts[0].quantiles_bps,
                ),
                msg=f"the fold from {fold.feature_date} moved when only later rows changed",
            )
            back = (
                panel[: feature - 1]
                + [with_spread_shifted(panel[feature - 1], 25.0)]
                + panel[feature:]
            )
            moved, _, moved_fits = self.backtest(back, volatility_feature="garch11")
            self.assertNotEqual(moved_fits[0].garch_parameters, fits[0].garch_parameters)
            self.assertNotEqual(
                moved.forecasts[0].quantiles_bps, report.forecasts[0].quantiles_bps
            )

            # Inside the design. Every row's variance is the recursion over rows
            # at or before it...
            model, frame = fits[0], frames[0]
            expected = recursion_variances(
                frame, model.garch_parameters, model.garch_initial_variance
            )
            self.assertEqual([model.design_row(row)[-1] for row in frame], expected)
            # ...and the training design is those values: the gbm with that
            # column declared as an ordinary regressor is the same model, down
            # to the residual sample every training design row contributes to.
            # On the larger frame, because at a fold's forty rows no level's
            # trees split on the column and a design that read it one row late
            # fits the same trees.
            whole = self.fit(calibration_frame, volatility_feature="garch11")
            expected = recursion_variances(
                calibration_frame, whole.garch_parameters, whole.garch_initial_variance
            )
            declared = self.REGRESSORS + ("garch_check",)
            reference = self.fit(
                with_column(calibration_frame, "garch_check", expected),
                regressors=declared,
            )
            self.assertEqual(reference.residuals, whole.residuals)
            self.assertEqual(
                reference.predict(
                    with_column(calibration_frame, "garch_check", expected)[-1]
                ),
                whole.predict(calibration_frame[-1]),
            )
            # The control: each row carrying its successor's variance -- a
            # training row reading the change into its target -- is a
            # different model on this frame, so the equality above is not the
            # trees ignoring the column.
            late = self.fit(
                with_column(calibration_frame, "garch_check", expected[1:] + expected[-1:]),
                regressors=declared,
            )
            self.assertNotEqual(
                late.residuals,
                reference.residuals,
                msg="the control: the gbm does not read the variance column on this frame",
            )

        with self.subTest("per fold"):
            self.assertGreater(len(fits), 1)
            self.assertLess(fits[0].cutoff, fits[-1].cutoff)
            self.assertNotEqual(
                fits[0].garch_parameters,
                fits[-1].garch_parameters,
                msg="two folds with different training ends fitted one GARCH",
            )
            for frame, model in zip(frames, fits):
                with self.subTest(train_end=frame[-1].date.isoformat()):
                    self.assertEqual(
                        (model.garch_parameters, model.garch_initial_variance),
                        ml._fit_garch11([row.spread_bps for row in frame], "fit rows"),
                        msg="the fold's GARCH is not the fit on the fold's own rows",
                    )
                    omega, alpha, beta = model.garch_parameters
                    self.assertGreater(omega, 0.0)
                    self.assertGreaterEqual(min(alpha, beta), 0.0)
                    self.assertLess(alpha + beta, 1.0)

        with self.subTest("calibration rows are filtered, not refitted"):
            rows = calibration_frame
            fit_rows = [row for row in rows if row.date <= calibrated.fit_end]
            self.assertLess(len(fit_rows), len(rows))
            self.assertEqual(
                (calibrated.garch_parameters, calibrated.garch_initial_variance),
                ml._fit_garch11([row.spread_bps for row in fit_rows], "fit rows"),
                msg="the GARCH was not fitted on the fit rows alone",
            )
            self.assertNotEqual(
                calibrated.garch_parameters,
                ml._fit_garch11([row.spread_bps for row in rows], "fit rows")[0],
                msg="the fixture: fit rows and frame fit the same GARCH",
            )
            # Filtered: the fit rows' recursion run on through the calibration
            # rows, and the widening scored off exactly those variances.
            expected = recursion_variances(
                rows, calibrated.garch_parameters, calibrated.garch_initial_variance
            )
            self.assertEqual(
                [calibrated.design_row(row)[-1] for row in rows], expected
            )
            reference = self.fit(
                with_column(rows, "garch_check", expected),
                regressors=self.REGRESSORS + ("garch_check",),
                calibration="conformal",
                purge_days=0,
            )
            self.assertEqual(reference.widening, calibrated.widening)

        with self.subTest("the declaration names volatility_feature; absent when not set"):
            self.assertEqual(dict(report.model_settings), {"volatility_feature": "garch11"})
            self.assertEqual(
                dict(baseline._model_settings(calibrated)),
                {
                    "calibration": "conformal",
                    "calibration_share": 0.25,
                    "volatility_feature": "garch11",
                },
            )
            self.assertEqual(
                fits[0].design_names,
                ("spread_bps",) + self.REGRESSORS + ("garch11_variance",),
            )
            # Read off spread_bps, already declared; not a panel column.
            self.assertEqual(fits[0].features_read, ("spread_bps",) + self.REGRESSORS)
            plain = self.fit(panel[:30])
            self.assertEqual(dict(baseline._model_settings(plain)), {})
            self.assertEqual(plain.design_names, ("spread_bps",) + self.REGRESSORS)
            self.assertIsNone(plain.garch_parameters)

        with self.subTest("refusal: an unknown value"):
            with self.assertRaisesRegex(ValueError, r"unknown volatility_feature 'garch12'"):
                self.fit(panel[:40], volatility_feature="garch12")

        with self.subTest("refusal: the setting on a model other than gbm"):
            parser = cli.build_parser()
            common = ["--registry", "registry.json", "--decision-time", DECISION_TIME]
            backtest = parser.parse_args(
                ["backtest", "panel.csv", *common, "--report", "r.json",
                 "--feature", "spread_bps", "--model", "arx",
                 "--volatility-feature", "garch11"]
            )
            with self.assertRaisesRegex(
                SplitError, r"--volatility-feature garch11 was given, but --model arx"
            ):
                cli_eval._select_fitter(backtest)
            compare = parser.parse_args(
                ["compare", "panel.csv", *common, "--report", "r.json",
                 "--model-a", "persistence", "--feature-a", "spread_bps",
                 "--volatility-feature-a", "garch11",
                 "--model-b", "gbm", "--feature-b", "spread_bps",
                 "--volatility-feature-b", "garch11", "--calibration-b", "conformal"]
            )
            with self.assertRaisesRegex(
                SplitError,
                r"--volatility-feature-a garch11 was given, but --model-a persistence",
            ):
                cli_eval._select_fitter(cli_eval._side(compare, "a"), side="-a")
            _, fitter = cli_eval._select_fitter(cli_eval._side(compare, "b"), side="-b")
            self.assertEqual(
                fitter.keywords,
                {
                    "regressors": (),
                    "calibration": "conformal",
                    "volatility_feature": "garch11",
                },
            )

        with self.subTest("refusal: too few fit rows for a GARCH fit"):
            with self.assertRaisesRegex(
                ValueError,
                r"needs at least 30 observed spread changes among the fit rows, got 29",
            ):
                self.fit(panel[:30], volatility_feature="garch11")
            # And thirty is enough: the refusal sits at the edge.
            self.assertIsNotNone(
                self.fit(panel[:31], volatility_feature="garch11").garch_parameters
            )

        with self.subTest("refusal: a fit that does not converge"):
            with mock.patch.object(ml, "_GARCH_MAX_ITERATIONS", 5):
                with self.assertRaisesRegex(
                    ValueError, r"did not converge in 5 Nelder-Mead iterations"
                ):
                    self.fit(panel[:40], volatility_feature="garch11")
            flat = [
                DailyObservation(row.date, dict(row.values, sofr=4.40))
                for row in panel[:40]
            ]
            with self.assertRaisesRegex(
                ValueError,
                r"did not converge: every one of its 39 observed spread changes is zero",
            ):
                self.fit(flat, volatility_feature="garch11")


class GradientBoostedCrossConformalTests(unittest.TestCase):
    """`calibration="cross_conformal"`: B25's acceptance criterion and its mutation target.

    **The defect.** Split-conformal gbm (B22) covers far more of its 90% band
    than the uncalibrated model, and the published
    `docs/runs/compare_persistence_vs_gbm_conformal_mh61_crps.json` shows what
    it paid: every level is fitted on the frame less a quarter and the purge,
    and its CRPS difference with persistence is no longer distinguishable from
    zero. CV+ (Barber, Candes, Ramdas and Tibshirani, 2021) on conformalized
    quantile regression keeps the full fit and calibrates its band with
    out-of-block scores. Its traps: scoring a held-out row with a model that
    saw it, no purge around the held-out block, reporting the interior from a
    block model, and blocks of shuffled rows.

    **The coverage tolerance, stated.** B22's, with `n` the held-out scores
    pooled over every block: `3 sqrt(q (1 - q) (1 / T + 1 / (n + 2)))` about
    the nominal `q`, two-sided, for `T` held-out rows. CV+'s finite-sample
    guarantee is only `1 - 2 alpha`; the test holds it to `1 - alpha`, the
    coverage it attains in practice on exchangeable rows, and this fixture is
    stationary for that reason. **The control must fail it**: the uncalibrated
    band is asserted below the tolerance's lower edge.

    **What the leakage subtest can see, and on what.** The fold loop hands the
    fitter a frame that ends at the feature row, so "trained at or before the
    fold's train end" holds by construction and is asserted off the dates each
    excluding model carries. The purge is not by construction, and a dated
    claim is only a claim, so it is also probed by behaviour, on the last
    fold's frame of well over a hundred rows -- the B24 lesson, a leak a
    forty-row frame could not show because no tree split: a row inside a
    block, and one inside the purge gap on either side of it, each moved by
    25 bp, leave that block's excluding model's predictions bit-identical; the
    control, a row that clears the gap, moves them. Every score is recomputed
    here from its own block's estimators at the feature row the purge chooses,
    with the control that the full fit's estimators score the same rows
    differently.

    **The minimum a block must leave.** One held-out row, and one training
    pair for its excluding model after the purge -- the minimum the split
    calibration already applies to its fit rows, "one origin and its
    successor". Not `minimum_history`: at `--minimum-history 61` an excluding
    model trains on four fifths of the frame less two purge gaps, so the first
    folds of the published declaration would be refused.

    Mutation record (B25)
    ---------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, one sub-copy per mutation,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B` (the worktree's `.venv`: CPython
    3.9.6, numpy 2.0.2, scikit-learn 1.6.1), `PYTHONPATH=src` (checked to
    resolve to each sub-copy), `REPO_MODEL_REQUIRE_ML=1`, `OMP_NUM_THREADS=1`,
    whole suite per run. Unmutated control green before and after, zero
    `expectedFailure`; each anchor found exactly once and confirmed applied.
    **Every mutation killed this test and nothing else.**

      * **Held-out scores computed with the full-fit model** --
        `_rearranged(estimators, ...)` for `_rearranged(block_estimators,
        ...)`. `coverage on held-out rows`, `AssertionError`: the band covers
        0.771 against 0.90 +/- 0.071 -- the in-sample score tail, as B22's
        record found for scores on the fit rows -- and every fold of the
        leakage subtest, `AssertionError`: the scores are not the excluding
        model's.
      * **The purge around held-out blocks removed** -- every row outside the
        block trains. Every fold, `AssertionError: ... block 1's excluding
        model trained on 2020-01-25, inside its block 2020-01-01..2020-01-24
        or the 6-day gap around it`; the behavioural probe, `AssertionError`
        (a row inside the gap before the block moved its model); and `refusal:
        a block that leaves its excluding model nothing to fit`, `ValueError
        not raised`. Coverage stays green, as it must at a zero gap.
      * **Interior levels taken from block model 0.** `the interior levels
        are the full fit's, bit for bit`, `AssertionError: Tuples differ`.
      * **The CV+ ranks replaced by split-conformal's single widening** -- the
        `ceil(q (n + 1))`-th smallest of the pooled out-of-block scores, added
        to both of the full fit's outer levels. `coverage on held-out rows`,
        `AssertionError: Tuples differ: (4.1315..., 13.8680...) != (4.1700...,
        13.5339...)` -- on the band-is-CV+'s check. **The coverage assertions
        before it passed**: on this stationary fixture a pooled widening of
        out-of-block scores covers inside the tolerance too, so coverage alone
        cannot tell the two apart, and that is why the edges are rebuilt here.
      * **Each refusal removed**, separately:
          - fewer than two blocks: `AssertionError` on the phrase -- one block
            falls through to the block refusal, `block 1 of 1 holds out 40 of
            40 rows and leaves its excluding model 0 training pair(s)`;
          - a block that leaves its excluding model nothing to fit:
            `IndexError`, out of the imputation refusal reaching for a first
            origin that is not there -- an error, not a failure;
          - `calibration_folds` without `cross_conformal`: `AssertionError:
            ValueError not raised`, the folds ignored by `none`;
          - `calibration_share` with `cross_conformal`: `AssertionError:
            ValueError not raised`, the share ignored;
          - fewer held-out scores than CV+'s ranks need (extra): `AssertionError:
            ValueError not raised` -- at eight scores `floor(0.1 x 9)` is 0,
            and the lower edge silently reads index -1, the largest low;
          - `cross_conformal` with no gap (extra): `TypeError: unsupported
            type for timedelta days component: NoneType`, out of
            `clears_purge`.
      * **`--calibration-folds` not bound** -- dropped from `cli_eval.
        _calibration` (extra). The declaration subtest, `AssertionError`: the
        fitter's keywords lack `calibration_folds`.
      * **The declaration key dropped** from `model_settings` (extra). The
        declaration subtest, `AssertionError: {'calibration':
        'cross_conformal'} != {'calibration': 'cross_conformal',
        'calibration_folds': 5}`.

    **Runtime, measured** on this interpreter, `OMP_NUM_THREADS=1`, gbm's
    production `min_samples_leaf` of 20, heteroscedastic frames and a 6-day
    gap: per fold of the rolling loop, 0.056 s uncalibrated, 0.046 s
    split-conformal and 0.269 s cross-conformal at `--minimum-history 61` (23
    folds of 61- to 83-row frames), and 0.188 s, 0.066 s and 0.420 s at 120 to
    123 rows, where the uncalibrated figure carries the process's first fit.
    On the 480-row frame above, with this file's `min_samples_leaf`, fitting
    took 0.92 s uncalibrated and 3.11 s cross-conformal, and forecasting 240
    rows 0.30 s and 1.83 s: five blocks plus the full fit, and every forecast
    reads each excluding model once more.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    TRAIN_ROWS = 480
    HELD_OUT_ROWS = 240
    PURGE = 6
    #: The fold loop's panel and minimum: every fold's frame is over a hundred
    #: rows, so its excluding models' trees split. See the class docstring.
    PANEL_ROWS = 130
    MINIMUM_HISTORY = 120
    #: The block the behavioural probe moves rows around: a middle one, with a
    #: purge gap on both sides.
    PROBE_BLOCK = 2
    SHIFT_BPS = 25.0

    def setUp(self):
        require_extra(self)

    def fit(self, frame, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(frame, self.REGRESSORS, **options)

    def design(self, row):
        """A row as the design reads it, built here: the spread, then each regressor."""

        return [float(row.spread_bps)] + [float(row.values[name]) for name in self.REGRESSORS]

    @staticmethod
    def sorted_levels(estimators, design):
        """One design row read at every level and sorted, off the estimators directly."""

        return sorted(float(estimator.predict([design])[0]) for estimator in estimators)

    def probe_predictions(self, block, frame):
        """An excluding model's per-level predictions on every row of `frame`."""

        designs = [self.design(row) for row in frame]
        return [
            tuple(float(value) for value in estimator.predict(designs))
            for estimator in block.estimators
        ]

    def test_the_cross_conformal_band_covers_its_nominal_probability_and_keeps_the_full_fit(self):
        """Coverage, the full fit's interior, purged excluding models, the declaration, refusals.

        One criterion. A CV+ band read off models that saw their held-out rows
        is the split calibration's defect with a better number; a band that
        covers by reporting a block model's interior is the accuracy B22 gave
        up, given up again; and a calibration that accepted one block or a
        block its purge had emptied would report a band with no guarantee
        behind it.
        """

        rows = heteroscedastic_frame(self.TRAIN_ROWS + self.HELD_OUT_ROWS)
        train = rows[: self.TRAIN_ROWS]
        forecasts = [rows[index - 1] for index in range(self.TRAIN_ROWS, len(rows))]
        outcomes = [row.spread_bps for row in rows[self.TRAIN_ROWS :]]
        uncalibrated = self.fit(train)
        cross = self.fit(train, calibration="cross_conformal", purge_days=0)
        plain = [uncalibrated.predict(row) for row in forecasts]
        banded = [cross.predict(row) for row in forecasts]

        with self.subTest("coverage on held-out rows"):
            q = Fraction("0.95") - Fraction("0.05")
            nominal = float(q)
            scores = sum(len(block.scores) for block in cross.calibration_blocks)
            tolerance = 3.0 * math.sqrt(
                nominal * (1.0 - nominal) * (1.0 / self.HELD_OUT_ROWS + 1.0 / (scores + 2))
            )
            before = sum(v[0] <= y <= v[-1] for v, y in zip(plain, outcomes)) / self.HELD_OUT_ROWS
            after = sum(v[0] <= y <= v[-1] for v, y in zip(banded, outcomes)) / self.HELD_OUT_ROWS
            self.assertLess(
                before,
                nominal - tolerance,
                msg=(
                    f"the control: the uncalibrated band covers {before:.3f} of "
                    f"{self.HELD_OUT_ROWS} held-out rows, inside the tolerance "
                    f"{nominal:.2f} +/- {tolerance:.3f}, so this fixture cannot "
                    f"tell a calibration from its absence"
                ),
            )
            self.assertLessEqual(
                abs(after - nominal),
                tolerance,
                msg=(
                    f"the cross-conformal band covers {after:.3f} of "
                    f"{self.HELD_OUT_ROWS} held-out rows against a nominal "
                    f"{nominal:.2f} +/- {tolerance:.3f} (uncalibrated {before:.3f})"
                ),
            )
            # And it is CV+'s band: built here from each excluding model's own
            # outer levels at the forecast's feature row and its own block's
            # scores, at CV+'s two ranks -- not one widening of the full fit.
            low_rank = math.floor((1 - q) * (scores + 1))
            high_rank = math.ceil(q * (scores + 1))
            for row, reported, fitted in list(zip(forecasts, banded, plain))[::4]:
                lows, highs = [], []
                for block in cross.calibration_blocks:
                    excluded = self.sorted_levels(block.estimators, self.design(row))
                    lows.extend(excluded[0] - score for score in block.scores)
                    highs.extend(excluded[-1] + score for score in block.scores)
                self.assertEqual(
                    (reported[0], reported[-1]),
                    (
                        min(sorted(lows)[low_rank - 1], fitted[1]),
                        max(sorted(highs)[high_rank - 1], fitted[-2]),
                    ),
                    msg=f"the band forecast from {row.date} is not CV+'s",
                )

        with self.subTest("the interior levels are the full fit's, bit for bit"):
            for row, reported, fitted in zip(forecasts, banded, plain):
                self.assertEqual(
                    reported[1:-1],
                    fitted[1:-1],
                    msg=f"the interior forecast from {row.date} is not calibration none's",
                )
            self.assertEqual(cross.residuals, uncalibrated.residuals)
            self.assertEqual(cross.fit_end, train[-1].date)
            # The control: an excluding model's interior differs from the full
            # fit's, so the equality above is not every fit agreeing.
            first = cross.calibration_blocks[0]
            self.assertNotEqual(
                [tuple(self.sorted_levels(first.estimators, self.design(row))[1:-1]) for row in forecasts],
                [fitted[1:-1] for fitted in plain],
                msg="the control: block 1's excluding model reports the full fit's interior",
            )

        with self.subTest("every excluding model trains outside its block and its purge gaps"):
            panel = heteroscedastic_frame(self.PANEL_ROWS)
            with tempfile.TemporaryDirectory() as directory:
                registry = json.loads(
                    declared_registry_file(
                        directory, purge=self.PURGE, features=self.FEATURES
                    ).read_text(encoding="utf-8")
                )
            fits = []

            def calibrating(train_frame, minimum_history, purge_days):
                model = self.fit(
                    train_frame,
                    minimum_history=minimum_history,
                    calibration="cross_conformal",
                    purge_days=purge_days,
                )
                fits.append((list(train_frame), purge_days, model))
                return model

            report = baseline.rolling_persistence_backtest(
                panel,
                features=self.FEATURES,
                registry=registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                minimum_history=self.MINIMUM_HISTORY,
                fit_model=calibrating,
            )
            gap = timedelta(days=report.purge_days)
            self.assertGreater(report.purge_days, 0, msg="at a zero gap the purge is not under test")
            self.assertGreater(len(fits), 1)
            self.assertEqual(len(fits), len(report.folds))
            for fold, (frame, purge, model) in zip(report.folds, fits):
                with self.subTest(fold=fold.scored_date.isoformat()):
                    self.assertEqual(purge, report.purge_days)
                    dates = [row.date for row in frame]
                    blocks = model.calibration_blocks
                    self.assertEqual(len(blocks), ml.DEFAULT_CALIBRATION_FOLDS)
                    # Contiguous date blocks, in order, covering the frame: no
                    # row shuffled into another block, none left out.
                    self.assertEqual(
                        [when for block in blocks for when in dates
                         if block.held_out_start <= when <= block.held_out_end],
                        dates,
                    )
                    for earlier, later in zip(blocks, blocks[1:]):
                        self.assertLess(earlier.held_out_end, later.held_out_start)
                    for number, block in enumerate(blocks, start=1):
                        self.assertTrue(block.training_dates)
                        self.assertLessEqual(block.training_dates[-1], dates[-1])
                        self.assertLess(block.training_dates[-1], fold.scored_date)
                        for when in block.training_dates:
                            self.assertTrue(
                                when + gap < block.held_out_start
                                or block.held_out_end + gap < when,
                                msg=(
                                    f"block {number}'s excluding model trained on "
                                    f"{when}, inside its block "
                                    f"{block.held_out_start}..{block.held_out_end} "
                                    f"or the {report.purge_days}-day gap around it"
                                ),
                            )
                        # Each held-out row is scored by this block's model, at
                        # the feature row the purge chooses, and only rows
                        # with one inside the frame are scored.
                        scored = [
                            index for index, when in enumerate(dates)
                            if block.held_out_start <= when <= block.held_out_end
                            and dates[0] + gap < when
                        ]
                        self.assertEqual(block.scored_dates, tuple(dates[i] for i in scored))
                        rescored, in_sample = [], []
                        for index in scored:
                            feature = max(p for p in range(index) if dates[p] + gap < dates[index])
                            target = frame[index].spread_bps
                            for estimators, out in (
                                (block.estimators, rescored),
                                (model._estimators, in_sample),
                            ):
                                levels = self.sorted_levels(estimators, self.design(frame[feature]))
                                out.append(max(levels[0] - target, target - levels[-1]))
                        self.assertEqual(
                            list(block.scores),
                            rescored,
                            msg=f"block {number}'s scores are not its own excluding model's",
                        )
                        self.assertNotEqual(
                            rescored,
                            in_sample,
                            msg="the control: the full fit scores this block identically",
                        )

            # By behaviour, on the last fold's frame: a row the probe block's
            # model may not train on moves nothing in it, and a row it may,
            # does.
            frame, purge, model = fits[-1]
            self.assertGreater(len(frame), 100)
            dates = [row.date for row in frame]
            block = model.calibration_blocks[self.PROBE_BLOCK]
            start = dates.index(block.held_out_start)
            stop = dates.index(block.held_out_end)
            baseline_predictions = self.probe_predictions(block, frame)

            def moved(position):
                shifted = list(frame)
                shifted[position] = with_spread_shifted(frame[position], self.SHIFT_BPS)
                refit = self.fit(
                    shifted,
                    minimum_history=self.MINIMUM_HISTORY,
                    calibration="cross_conformal",
                    purge_days=purge,
                )
                return self.probe_predictions(refit.calibration_blocks[self.PROBE_BLOCK], frame)

            for label, position in (
                ("inside the gap before the block", start - 1),
                ("inside the block", start + 1),
                ("inside the gap after the block", stop + 1),
            ):
                self.assertEqual(
                    moved(position),
                    baseline_predictions,
                    msg=f"a row {label} ({dates[position]}) moved the block's excluding model",
                )
            clear = stop + 1
            while not dates[stop] + gap < dates[clear]:
                clear += 1
            self.assertNotEqual(
                moved(clear + 1),
                baseline_predictions,
                msg="the control: a row the excluding model trains on moves nothing in it",
            )

        with self.subTest("the declaration names calibration and calibration_folds"):
            self.assertEqual(
                dict(report.model_settings),
                {"calibration": "cross_conformal", "calibration_folds": 5},
            )
            three = self.fit(rows[:60], calibration="cross_conformal", calibration_folds=3, purge_days=0)
            self.assertEqual(
                dict(baseline._model_settings(three)),
                {"calibration": "cross_conformal", "calibration_folds": 3},
            )
            self.assertEqual(len(three.calibration_blocks), 3)
            parser = cli.build_parser()
            common = ["--registry", "registry.json", "--decision-time", DECISION_TIME]
            backtest = parser.parse_args(
                ["backtest", "panel.csv", *common, "--report", "r.json",
                 "--feature", "spread_bps", "--model", "gbm",
                 "--calibration", "cross_conformal", "--calibration-folds", "3"]
            )
            _, fitter = cli_eval._select_fitter(backtest)
            self.assertEqual(
                fitter.keywords,
                {"regressors": (), "calibration": "cross_conformal", "calibration_folds": 3},
            )
            compare = parser.parse_args(
                ["compare", "panel.csv", *common, "--report", "r.json",
                 "--model-a", "persistence", "--feature-a", "spread_bps",
                 "--calibration-folds-a", "3",
                 "--model-b", "gbm", "--feature-b", "spread_bps",
                 "--calibration-b", "cross_conformal", "--calibration-folds-b", "4"]
            )
            with self.assertRaisesRegex(
                SplitError, r"--calibration-folds-a 3 was given, but --model-a persistence"
            ):
                cli_eval._select_fitter(cli_eval._side(compare, "a"), side="-a")
            _, fitter = cli_eval._select_fitter(cli_eval._side(compare, "b"), side="-b")
            self.assertEqual(fitter.keywords.get("calibration_folds"), 4)

        with self.subTest("refusal: fewer than two blocks"):
            for folds in (1, 0, -3, True, 2.5):
                with self.assertRaisesRegex(
                    ValueError, r"calibration_folds must be an int of at least 2"
                ):
                    self.fit(rows[:40], calibration="cross_conformal",
                             calibration_folds=folds, purge_days=0)

        with self.subTest("refusal: a block that leaves its excluding model nothing to fit"):
            with self.assertRaisesRegex(
                ValueError,
                r"cross-conformal block 1 of 2 holds out 20 of 40 rows and leaves "
                r"its excluding model 0 training pair\(s\) after a 19-day purge",
            ):
                self.fit(rows[:40], calibration="cross_conformal",
                         calibration_folds=2, purge_days=19)
            # And one pair is enough: the refusal sits at the edge.
            edge = self.fit(rows[:40], calibration="cross_conformal",
                            calibration_folds=2, purge_days=18)
            self.assertEqual(
                [len(block.training_dates) for block in edge.calibration_blocks], [2, 2]
            )

        with self.subTest("refusal: calibration_folds without cross_conformal"):
            with self.assertRaisesRegex(
                ValueError, r"calibration_folds 3 was given, but calibration 'none'"
            ):
                self.fit(rows[:40], calibration_folds=3)
            with self.assertRaisesRegex(
                ValueError, r"calibration_folds 3 was given, but calibration 'conformal'"
            ):
                self.fit(rows[:40], calibration="conformal", calibration_folds=3, purge_days=0)

        with self.subTest("refusal: calibration_share with cross_conformal"):
            with self.assertRaisesRegex(
                ValueError, r"calibration_share 0.25 was given, but calibration 'cross_conformal'"
            ):
                self.fit(rows[:40], calibration="cross_conformal",
                         calibration_share=0.25, purge_days=0)

        with self.subTest("refusal: fewer held-out scores than CV+'s ranks need"):
            with self.assertRaisesRegex(
                ValueError, r"needs at least 9 held-out scores, got 8"
            ):
                self.fit(rows[:9], minimum_history=9, calibration="cross_conformal",
                         calibration_folds=2, purge_days=0)
            # And nine is enough.
            self.assertEqual(
                sum(
                    len(block.scores)
                    for block in self.fit(
                        rows[:10], minimum_history=10, calibration="cross_conformal",
                        calibration_folds=2, purge_days=0,
                    ).calibration_blocks
                ),
                9,
            )

        with self.subTest("refusal: cross_conformal with no gap"):
            with self.assertRaisesRegex(SplitError, r"purge must be an int, got None"):
                self.fit(rows[:40], calibration="cross_conformal")


class GradientBoostedForecastInterfaceTests(
    ForecastInterfaceConformance, unittest.TestCase
):
    """The conformance suite against `FittedGradientBoostedQuantiles`.

    The fourth implementer, and the first whose predictive *width* moves with
    the feature row rather than only its centre. Every assertion in the mixin
    was written against models that are one anchor plus one fixed residual law;
    what this case establishes is that they were assertions about the interface
    and not about that construction. Two of them could only be exercised by a
    model shaped like this:
    `test_predict_stress_agrees_with_the_quantiles_predict_reports` is now a
    statement about inverting a *declared grid* rather than an empirical sample,
    and `test_the_exceedance_is_strictly_above_the_threshold` is the reason
    `predict_stress` reads the fitted residual sample for its tail knots at all.

    On the same rows as the other four cases, so a difference between the cases
    is a difference between the models. `FIXTURE_MIN_SAMPLES_LEAF` is not used
    here: `distinct_residual_frame` is long enough for scikit-learn's own
    default to split, and a case that changed two things at once about the
    shared fixture would not be on the same rows as the others in the way that
    matters.
    """

    MODEL_CLASS = ml.FittedGradientBoostedQuantiles

    def setUp(self):
        require_extra(self)
        super().setUp()

    def fit_model(self, train_frame, cutoff=None):
        return ml.fit_gradient_boosted_quantiles(
            train_frame,
            CONFORMANCE_REGRESSORS,
            cutoff=cutoff,
            minimum_history=self.MINIMUM_HISTORY,
        )


class GbmExceedanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `gbm_exceedance`, on the same rows.

    The fourth implementer of the exceedance interface. `arx_exceedance`'s curve
    moves because its centre does; `threshold_exceedance` adds a second reason
    by switching which fitted relationship produces that centre. This one's
    curve moves for a third: the band itself is fitted level by level, so two
    rows with the same centre can still be given different curves.
    """

    IMPLEMENTATION = staticmethod(ml.gbm_exceedance)

    def setUp(self):
        require_extra(self)

    def make_predictor(self):
        return ml.gbm_exceedance(
            REGRESSORS,
            minimum_history=self.MINIMUM_HISTORY,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
        )

    def test_the_curve_moves_across_scored_days(self):
        """Conditional, and on this frame demonstrably so.

        The claim the mixin cannot make, because the climatology satisfies every
        assertion in it with one flat curve. A gradient-boosted quantile model
        whose curve did not move would be a climatology fitted the expensive
        way, and nothing else here would notice.
        """

        curves = self.curves(EXCEEDANCE_TAUS).curves
        self.assertGreater(
            len(set(curves)),
            1,
            msg="every scored day got the same curve; nothing was conditioned on",
        )


class GradientBoostedCompareTests(ContinuousModelHarness):
    """`compare --model-b gbm --loss crps`: the one ML model reaching the criterion.

    **What was missing.** `gbm` was in `cli_eval.MODEL_FACTORIES` and not in
    `cli_eval.FITTER_FACTORIES`, so the exceedance path could run it and
    `backtest` and `compare` could not construct it at all --
    `compare ... --model-b gbm` exited 2 with *"unknown --model-b 'gbm'; this
    command can run arx, persistence, rolling-residual, threshold"*. The
    criterion `PLAN.md`'s Phase 2 states is *"a model that beats persistence
    out of sample"*, and `compare` is the command that answers it, so the one
    model this repository builds with the `ml` extra had no route to the
    question it was built for.

    **The fixture is `ContinuousModelHarness`', not a new one**, and the
    invocation is its `run_compare`. Both were already there for the ARX and
    the trailing-window law; a panel and an argv written again here would make
    a difference between this model's run and theirs indistinguishable from a
    difference between two fixtures. `run_compare` moved down onto the harness
    in this block for that reason and is otherwise unchanged.

    **A finding: the earliest folds are unconditional, and there the trap is
    invisible.** `FITTER_FACTORIES` binds no `min_samples_leaf` -- there is no
    flag for it and tuning is not this block's -- so a run uses scikit-learn's
    default of 20. The first fold here trains on `--minimum-history` rows,
    which leaves 24 design rows, and at that size every level fit is a single
    leaf: the predicted vector is the same on every feature row, and the
    model's own law is then *bit for bit* the same as its median wrapped in its
    own residual sample. Measured, not reasoned about -- the two CRPS values at
    the first origin are equal to the last digit. So an origin there satisfies
    the equality below under the defect as well as under the fix, and the
    origins chosen are the middle one and the last, where the fits do split and
    the two laws differ. What this says about a run on the frozen panel is that
    its early folds are a gradient-boosted climatology; it is not a defect in
    the wiring, and it is the reason `--minimum-history` matters more to this
    model than to persistence.

    **Why the report object and not only the artifact.** Since B18 the record
    does carry the per-origin series, under `comparison.per_origin`, but as
    what the run published: `paired_comparison_document` writes it from the
    report. The claim below is about what the run *computed*, so the run's own
    `PairedComparisonReport` is captured on its way into the document by
    wrapping the name `cli_eval` calls, and a defect in how the document lays
    the series out cannot move this test's reading of it. Nothing about the
    run changes: the command is entered through `cli.main`, the document is
    built by the real function, and the file is written. What is read is the
    run's own object rather than a second comparison built beside it.


    Mutation record
    ---------------

    Disposable copy under `$HOME`, taken from `git ls-files -z --cached
    --others --exclude-standard` at the per-branch, per-commit path
    `CLAUDE.md` now names, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B` and
    `REPO_MODEL_REQUIRE_ML=1`, on CPython 3.9.6 with numpy 2.0.2 and
    scikit-learn 1.6.1. Unmutated control green before and after, zero
    `expectedFailure` throughout; each mutation confirmed applied by grep and
    restored before the next.

      * **gbm's law replaced by a residual law.** `FITTER_FACTORIES["gbm"]`
        wrapped so the fitted model's `predict` returns its own median plus its
        own residual sample, everything else -- the name in the record, the
        features read, the folds, the digest -- unchanged. This is the trap the
        criterion exists for: the run completes, the record says `gbm`, and the
        CRPS it publishes is not gbm's. Kills the acceptance test at **both**
        chosen origins, `AssertionError`, on the per-origin equality. It also
        kills
        `test_contract.ForecastInterfaceCoverageTests::test_every_implementation_in_baseline_runs_the_conformance_suite`,
        `AssertionError`, because the wrapper is a new predictive-law class in
        the package and block 9's walk discovers it -- collateral from how this
        mutation had to be written, and the walk doing its job.
      * **The same law swap written inside the model instead.**
        `FittedGradientBoostedQuantiles.predict` returns the residual law
        directly. **The acceptance test survives**, and that is the finding
        rather than a gap: this test's expectation *is* a directly fitted
        model's `predict`, so a defect inside `predict` moves the run and the
        expectation together. What kills it is
        `GradientBoostedQuantileTests::test_the_quantiles_are_ordered_and_reproducible_at_every_contract_level`,
        on every row of `crossing_frame`. The two classes divide the claim:
        that the law is the law, and that the command scores it.
      * **Each refusal a no-op**, run separately. The `--regime-variable{side}`
        branch in `cli_eval._regressors_and_regime` made `pass`: kills this
        test's `flag='regime_variable_b'` subtest with `AssertionError: 0 != 2`,
        alongside the two single-model tests that already covered the same rule
        on their own commands. The `--residual-window{side}` refusal in
        `cli_eval._residual_window` deleted: kills `flag='residual_window_b'`
        the same way, alongside
        `ContinuousModelSelectorTests::test_the_residual_window_is_required_for_the_model_that_reads_one`.
        Both refusals are shared with `backtest`, which is why neither kill is
        this test's alone -- and why the subtests assert the message names
        `--model-b`, which is the half only `compare` can get wrong.
      * **The deferred import bypassed.** The `try/except ImportError ->
        MissingMLExtraError` in `ml._estimator_class` reduced to a bare `from
        sklearn.ensemble import ...`. Kills the acceptance test as an **error**
        and not a failure: `ModuleNotFoundError: import of sklearn.ensemble
        halted; None in sys.modules`, out of the fit and through `cli.main`
        uncaught. Recorded as an error deliberately -- the defect is precisely
        that a caller without the extra gets a traceback instead of exit 2 and
        a sentence, so the shape of the kill is the claim.
      * **A second deferral mechanism**, expected to survive here and to be
        killed elsewhere: the `gbm` entry declared as a module-level function
        that imports `repo_model.ml` inside itself, instead of
        `_DeferredFactory`. This test stays **green** -- the refusal still
        names the extra, because it still comes from `ml` -- and
        `test_cli_eval.ContinuousModelSelectorTests::test_every_selectable_name_is_a_fitter_this_package_exports`
        kills it on identity. That pair is what "through the one deferred
        mechanism, not a second one" means mechanically: this file cannot see
        the difference and the mapping's own guard can.
      * **Re-run, because this block moved a fixture an existing record
        names.** `run_compare` moved from `PairedComparisonCommandTests` onto
        `ContinuousModelHarness`, so that record's `--loss` mutation was run
        again over the moved helper: `loss=args.loss` dropped from `_compare`'s
        `paired_model_comparison` call. Still kills
        `test_the_loss_flag_reaches_the_record_and_defaults_to_the_point_loss`,
        `AssertionError: 'absolute_error_bps' != 'crps_bps'`, and now kills
        this test too, on the same assertion.

    Cost, reported and not asserted
    -------------------------------

    On this fixture -- 61 origins, training windows of 25 to 89 rows -- a
    `compare` run with `gbm` on one side takes about 0.21 seconds per origin,
    of which a single five-level fit is nearly all. The cost grows with the
    training window, roughly `0.2 + 0.002 * rows` seconds per fit measured out
    to 2 100 rows. The published `compare` records under `docs/runs/` are two
    populations over one expanding window that reaches 2 099 rows: the two
    absolute-error records, at `--minimum-history 20`, carry 2 080 origins, and
    the `--minimum-history 61` CRPS records -- gbm's among them -- carry 2 039.
    Either puts a real run at something over an hour of wall clock on eight
    cores. It fits in an evening; it does not fit in a test.

    The library versions a record names
    ------------------------------------

    Every record a run with an ml side publishes -- `compare` with `gbm` on
    either side, `exceedance-backtest` with `gbm_exceedance`, and `backtest
    --model gbm`, which reaches the same fitter through the same
    `FITTER_FACTORIES` entry -- carries `provenance.ml_libraries`,
    `{"numpy": ..., "scikit-learn": ...}`. The record published before this
    existed named neither, and the versions were read off the environment
    after the run, which says what is installed now and not what fitted then.

    The value is the imported modules' `__version__`, read by
    `ml._library_versions` at the fit and carried out of it on the fitted model
    and on `ExceedanceCurves`; `baseline` never reads a version, because it
    cannot import either package. The key is written by `_run_provenance`, the
    one builder all three documents share, and only when a fit reported one:
    a run with no ml side has no key -- absent, not `null` -- because a
    record naming libraries that did not run claims a dependency the result
    does not have.

    `test_a_record_with_an_ml_side_names_the_library_versions_that_fitted_it`
    is the acceptance test and the mutation target. It runs at
    `--minimum-history 84` for cost alone: a record's provenance does not
    depend on how many origins were scored.

    Mutation record (B19). Same protocol as above: the per-branch, per-commit
    copy under `$HOME` from `git ls-files -z --cached --others
    --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `REPO_MODEL_REQUIRE_ML=1`, CPython 3.9.6, numpy 2.0.2, scikit-learn 1.6.1,
    whole suite per run. Unmutated control green before and after, zero
    `expectedFailure`; each mutation asserted applied and restored by the
    driver before the next.

      * **Control for the plant, expected to survive.** The first mutation
        needs a module whose `__version__` differs from its installed
        metadata, which a clean install never has. So a guarded
        `import sklearn` at the top of this module appends `+planted` to
        `sklearn.__version__` at discovery, before any fit. With nothing else
        changed the suite is **green**: the fit reads the planted value and so
        does this test. The plant alone reddens nothing.
      * **Versions read through `importlib.metadata`**, with the plant in
        place. Kills this test's three ml subtests (compare, exceedance-
        backtest, backtest), `AssertionError: {'numpy': '2.0.2',
        'scikit-learn': '1.6.1'} != {... '1.6.1+planted'}`. On a clean
        install this defect is invisible, since the two sources agree. That
        is why the plant exists, and why the source of the version is named
        in `ml._library_versions` and not left to whichever lookup is nearer.
      * **The key written for non-ml runs.** `_run_provenance` always writes
        it, from `ml._library_versions()` when the report carries none. Kills
        the `persistence vs rolling-residual` subtest alone,
        `AssertionError: 'ml_libraries' unexpectedly found`. **Nothing else
        in the suite noticed.** The existing "no `null` in provenance" check
        in `tests/test_baseline.py` is satisfied by a real dict, so a record
        claiming a dependency that did not run is visible only here.
      * **The key written only in the compare document.** The write removed
        from `_run_provenance` and done instead in
        `paired_comparison_document`. Kills the exceedance-backtest and
        backtest subtests, `AssertionError: None != {...}`. The compare
        subtest stays green, as it should. That is the shared-builder claim
        mechanically: one document getting it right says nothing about the
        others.
      * **scikit-learn's version taken from numpy's.** Kills the three ml
        subtests, `AssertionError: {'numpy': '2.0.2', 'scikit-learn':
        '2.0.2'} != {...'1.6.1'}`.

    Every mutation killed this test and nothing else. That is the finding:
    before this block no test read a record's provenance for anything an ml
    fit could put there.

    """

    def setUp(self):
        require_extra(self)
        super().setUp()

    def declared_regressors(self, features):
        """`--feature-b` minus the term the fitter supplies itself.

        Derived through `cli_eval._AUTOREGRESSIVE_TERM` rather than spelled, so
        the expectation below is built from the same rule the command applies
        and not from a copy of it that agrees until one of them is edited.
        """

        return tuple(
            column
            for column in sorted(features)
            if column != cli_eval._AUTOREGRESSIVE_TERM
        )

    def run_gbm_compare(self, **overrides):
        """Run `compare` with `gbm` on side b; return the run's own report too.

        See the class docstring on why the report object is captured. The
        wrapper calls the real `paired_comparison_document` and returns its
        value, so a run that reaches this point still writes the artifact it
        would have written.
        """

        captured = []
        publish = cli_eval.paired_comparison_document

        def spy(comparison, **kwargs):
            captured.append(comparison)
            return publish(comparison, **kwargs)

        options = {"model_b": "gbm", "loss": "crps"}
        options.update(overrides)
        with mock.patch.object(cli_eval, "paired_comparison_document", spy):
            code, out, err = self.run_compare(**options)
        return code, out, err, (captured[0] if captured else None)

    def fitted_directly(self, fold, features):
        """A gbm fitted on one fold's own training window, outside the command.

        The window is rebuilt from the fold the run recorded -- `train_start`
        through `train_end` inclusive -- so the frame is the one the run fitted
        on rather than one reconstructed from the purge arithmetic a second
        time. Every other argument is the fitter's own default, which is what
        `FITTER_FACTORIES` binds: `random_state` and `early_stopping=False`
        make the two fits identical bit for bit, which is why the assertion
        below is an equality and not a tolerance.
        """

        rows = load_daily_panel(self.PANEL)
        window = [
            row for row in rows if fold.train_start <= row.date <= fold.train_end
        ]
        return ml.fit_gradient_boosted_quantiles(
            window,
            self.declared_regressors(features),
            minimum_history=int(self.MINIMUM_HISTORY),
        )

    def test_compare_scores_gbm_against_persistence_under_crps_from_its_own_law(self):
        """Four claims about one command, and they hold together or not at all.

        A run that exits 0 and names `gbm` while scoring somebody else's law is
        the defect this test exists for, so the naming claim and the arithmetic
        claim cannot be separated; and a model reachable by name that quietly
        accepted flags it does not read, or that failed with an `ImportError`
        on a checkout without the extra, would be reachable in the sense that
        matters to a table and not in the sense that matters to a caller.
        """

        code, out, err, comparison = self.run_gbm_compare()

        # 1. The command runs, and the record says which model produced the
        #    challenger's numbers and under which loss. The heading is read
        #    too: a mean CRPS published under `mae_bps` parses, reads correctly
        #    and means something else.
        self.assertEqual(code, 0, msg=f"command failed: {err.strip()}")
        record = json.loads(self.last_report.read_text(encoding="utf-8"))
        self.assertEqual(record["declaration"]["model_b"]["model"], "gbm")
        self.assertEqual(record["comparison"]["model_b"]["model"], "gbm")
        self.assertEqual(record["comparison"]["loss"], "crps_bps")
        self.assertIn("crps_bps", record["comparison"]["model_b"])
        self.assertEqual(json.loads(out)["model_b"], "gbm")

        # 2. The published loss is **this model's own law**. At each chosen
        #    origin the run's per-origin CRPS equals the CRPS of the quantile
        #    vector a gbm fitted directly on that origin's training window
        #    reports -- and, so the equality is not vacuous, differs from what
        #    the same model's median wrapped in its own residual sample would
        #    have scored. That second law is what a point prediction registered
        #    under persistence's construction produces: it runs, it names gbm,
        #    and it publishes a CRPS that is not gbm's.
        rows = {row.date: row for row in load_daily_panel(self.PANEL)}
        self.assertTrue(comparison.folds, msg="the run scored no origins")
        # The middle origin and the last, and **not the first**; see
        # `EARLY_FOLDS_ARE_UNCONDITIONAL` in this class's docstring for why an
        # origin there cannot tell the two laws apart.
        chosen = sorted({len(comparison.folds) // 2, len(comparison.folds) - 1})
        for index in chosen:
            fold = comparison.folds[index]
            with self.subTest(origin=fold.scored_date):
                model = self.fitted_directly(fold, self.FEATURES)
                feature_row = rows[fold.feature_date]
                actual = rows[fold.scored_date].spread_bps
                own_law = crps_from_quantiles(
                    QUANTILE_LEVELS, model.predict(feature_row), actual
                )
                self.assertEqual(
                    comparison.losses_b[index],
                    own_law,
                    msg=(
                        f"the run's CRPS at {fold.scored_date} is not the CRPS "
                        f"of the law a gbm fitted on "
                        f"{fold.train_start}..{fold.train_end} reports"
                    ),
                )

                centre = model.point_forecast(feature_row)
                residual_law = tuple(
                    centre + baseline._quantile(model.residuals, level)
                    for level in QUANTILE_LEVELS
                )
                self.assertNotAlmostEqual(
                    crps_from_quantiles(QUANTILE_LEVELS, residual_law, actual),
                    own_law,
                    places=6,
                    msg=(
                        "this model's own conditional law and its median "
                        "wrapped in its residual sample score the same at "
                        f"{fold.scored_date}, so the equality above cannot "
                        "tell them apart on this fixture"
                    ),
                )

        # 3. The two flags this model does not read are refused, on the side
        #    they were given on, before anything is fitted -- so each refusal
        #    also leaves no artifact behind.
        for flag, value, phrase in (
            (
                "regime_variable_b",
                self.REGIME_VARIABLE,
                "--model-b gbm reads no regime variable",
            ),
            (
                "residual_window_b",
                5,
                "--model-b gbm reads its residual law from the whole training "
                "frame",
            ),
        ):
            with self.subTest(flag=flag):
                refused = self.tmp / f"refused-{flag}.json"
                code, _, err = self.run_compare(
                    model_b="gbm", loss="crps", report=refused, **{flag: value}
                )
                self.assertEqual(code, 2, msg=f"{flag} was accepted")
                self.assertIn(phrase, " ".join(err.split()))
                self.assertFalse(
                    refused.exists(),
                    msg="a refused run wrote a report",
                )

        # 4. Without the extra the refusal is this repository's sentence and
        #    exit 2, not an `ImportError` out of a fit four frames down. The
        #    deferred import is `ml._estimator_class`', reached through the
        #    same `_DeferredFactory` `MODEL_FACTORIES` uses; blocking
        #    `sklearn` in `sys.modules` is how an interpreter without the extra
        #    is simulated on one that has it.
        blocked = self.tmp / "compare-without-the-extra.json"
        with mock.patch.dict(
            sys.modules, {"sklearn": None, "sklearn.ensemble": None}
        ):
            code, _, err = self.run_compare(
                model_b="gbm", loss="crps", report=blocked
            )
        self.assertEqual(code, 2, msg="the missing extra did not refuse")
        self.assertIn("'ml' extra", err)
        self.assertNotIn("Traceback", err)
        self.assertFalse(blocked.exists())

    def test_a_record_with_an_ml_side_names_the_library_versions_that_fitted_it(self):
        """`provenance.ml_libraries` on every record an ml fit reached, and no other.

        See "The library versions a record names" in the class docstring. The
        expectation is the imported modules' own `__version__`, imported here
        rather than read through the package, so a record built from anything
        else -- an installer's metadata, one package's version under the
        other's name -- disagrees with it.
        """

        import numpy
        import sklearn

        fitted_with = {
            "numpy": numpy.__version__,
            "scikit-learn": sklearn.__version__,
        }
        # Cost only; see the class docstring. The record's provenance does not
        # depend on how many origins were scored, and at the harness's own
        # minimum history each gbm run below is sixty-odd five-level fits.
        self.MINIMUM_HISTORY = "84"
        minimum_history = int(self.MINIMUM_HISTORY)

        with self.subTest(record="compare, gbm on side b"):
            code, _, err = self.run_compare(model_b="gbm")
            self.assertEqual(code, 0, msg=f"command failed: {err.strip()}")
            record = json.loads(self.last_report.read_text(encoding="utf-8"))
            self.assertEqual(record["provenance"].get("ml_libraries"), fitted_with)

        with self.subTest(record="exceedance-backtest, gbm_exceedance"):
            report = baseline.rolling_exceedance_backtest(
                load_daily_panel(self.PANEL),
                predictor=ml.gbm_exceedance(
                    self.declared_regressors(self.FEATURES),
                    minimum_history=minimum_history,
                ),
                model_name="gbm",
                features=self.FEATURES,
                registry=json.loads(self.registry.read_text(encoding="utf-8")),
                decision_time=time.fromisoformat(DECISION_TIME),
                taus=load_stress_thresholds(THRESHOLDS)["taus_bp"],
                minimum_history=minimum_history,
            )
            record = baseline.exceedance_backtest_document(
                report,
                panel_path=self.PANEL,
                registry_path=self.registry,
                thresholds_path=THRESHOLDS,
            )
            self.assertEqual(record["provenance"].get("ml_libraries"), fitted_with)

        with self.subTest(record="backtest, gbm"):
            code, _, err = self.run_backtest(*self.FEATURES, model="gbm")
            self.assertEqual(code, 0, msg=f"command failed: {err.strip()}")
            record = json.loads(self.last_report.read_text(encoding="utf-8"))
            self.assertEqual(record["provenance"].get("ml_libraries"), fitted_with)

        with self.subTest(record="compare, persistence vs rolling-residual"):
            code, _, err = self.run_compare(
                model_a="persistence", model_b="rolling-residual", residual_window_b=5
            )
            self.assertEqual(code, 0, msg=f"command failed: {err.strip()}")
            record = json.loads(self.last_report.read_text(encoding="utf-8"))
            self.assertNotIn(
                "ml_libraries",
                record["provenance"],
                msg="a run no ml model took part in names library versions it never used",
            )


class GradientBoostedEventHoldoutTests(ConditionalModelHarness):
    """`event-holdout --model gbm`: the journal line names what fitted it.

    **What was missing.** B19 put `ml_libraries` on every record a rolling run
    with an ml side publishes, through `baseline._run_provenance`. The
    knowledge holdout does not publish a record; it appends an
    `EvaluationRecord` to the append-only journal, and `evaluate_event_window`
    never goes through `_run_provenance`. So `event-holdout --model gbm` fitted
    gbm and wrote a line that named neither numpy nor scikit-learn. A window is
    scored once, so that line is the only provenance the scoring has.

    **Not `GradientBoostedCompareTests`.** Its harness is
    `ContinuousModelHarness`, which has no events file, no journal, no
    `event-holdout` invocation and no rebuilt `model_config`.
    `ConditionalModelHarness` has all four, and is the fixture
    `ModelSelectorTests` already scores gbm's three siblings on. A second
    spelling of the argv or of `expected_config` here would make a difference
    between this run and theirs indistinguishable from a difference between
    two fixtures.

    **The versions stay out of `config_sha256`.** The hash identifies the
    scoring configuration. A knowledge-holdout window is scored once and a
    rerun is meant to be visible; a hash that moved with the installed
    scikit-learn would make a re-scoring under a new version look like a
    different configuration, which is the rerun the journal exists to show.
    So the expectation is `expected_config`, rebuilt from the declarations and
    carrying no version, exactly as `ModelSelectorTests` rebuilds it.

    Mutation record (B20)
    ---------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B` (the worktree's `.venv`: CPython 3.9.6, numpy 2.0.2,
    scikit-learn 1.6.1), whole suite per run. `REPO_MODEL_REQUIRE_ML` was not
    set; the extra was installed and this test ran, which every kill below
    shows. Unmutated control green before and after, zero `expectedFailure`;
    each mutation asserted applied (its anchor found exactly once in
    `event_eval.py`) and restored by the driver before the next. All four are
    in `evaluate_event_window` or `EvaluationRecord`.

      * **The versions added to `model_config` before hashing.** The digest
        taken over `model_config` plus `ml_libraries` whenever the curves
        carry them. Kills the `gbm config_sha256 carries no versions` subtest
        alone, `AssertionError: '8b7d…' != 'f24b…'`. The climatology line's
        hash does not move, which is why the expectation is gbm's.
      * **The key written as `null` for non-ml fits.** `as_json_line` keeps
        the `None`. Kills `climatology has no ml_libraries key` alone,
        `AssertionError: 'ml_libraries' unexpectedly found`. **Nothing else in
        the suite noticed**: no journal test in `tests/test_cli_eval.py` or
        `tests/test_event_eval.py` went red over a `null` on every
        climatology line.
      * **The key dropped.** `ml_libraries` never set from the curves, so the
        field keeps its default. Kills `gbm carries both versions` alone,
        `AssertionError: None != {'numpy': '2.0.2', 'scikit-learn': '1.6.1'}`.
        This is the tree before this block.
      * **scikit-learn's version taken from numpy's** on the curves' way into
        the record. Kills `gbm carries both versions` alone,
        `AssertionError: {'numpy': '2.0.2', 'scikit-learn': '2.0.2'} !=
        {... '1.6.1'}`.

    Every mutation killed this test and nothing else, each with
    `AssertionError`. The `read_journal` subtest is killed by none of them, as
    expected: it guards that a file mixing the two kinds of line still reads,
    and no mutation here makes a line unreadable.
    """

    def setUp(self):
        require_extra(self)
        super().setUp()

    def test_an_event_holdout_journal_line_from_an_ml_fit_names_its_library_versions(self):
        """`ml_libraries` on a gbm line, absent on a climatology line, and not hashed.

        The expectation is the imported modules' own `__version__`, imported
        here, for the reason the compare test gives: a line built from
        anything else disagrees with it. Both runs score the same window into
        one journal, gbm first, so the file under the last subtest holds one
        line of each kind.
        """

        import numpy
        import sklearn

        fitted_with = {
            "numpy": numpy.__version__,
            "scikit-learn": sklearn.__version__,
        }

        self.scored(model="gbm")
        self.scored(model="climatology")
        lines = self.journal.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2, msg="each run appends exactly one line")
        gbm_line, climatology_line = (json.loads(line) for line in lines)

        with self.subTest(line="gbm carries both versions"):
            self.assertEqual(gbm_line.get("ml_libraries"), fitted_with)

        with self.subTest(line="climatology has no ml_libraries key"):
            self.assertNotIn(
                "ml_libraries",
                climatology_line,
                msg="a line no ml fit produced names library versions; absent, not null",
            )
            self.assertNotIn("null", lines[1])

        with self.subTest(line="gbm config_sha256 carries no versions"):
            self.assertEqual(
                gbm_line["config_sha256"],
                config_digest(self.expected_config("gbm", self.FEATURES)),
                msg="the gbm line's hash is not the hash of the model_config the "
                "command built; the versions moved it",
            )

        with self.subTest(line="read_journal reads one line of each kind"):
            entries = read_journal(self.journal)
            self.assertEqual(entries, (gbm_line, climatology_line))
            self.assertEqual(
                [entry["window_name"] for entry in entries],
                ["smoke-window", "smoke-window"],
            )


if __name__ == "__main__":
    unittest.main()
