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
* `GradientBoostedArxFeatureTests` -- `arx_feature="declared"`: the column is
  `baseline.fit_arx`'s own one-step forecast, fitted per fold on the fit rows,
  read from rows at or before its row, never refitted on calibration rows,
  fitted apart for every cross-conformal block, named in the declaration, and
  its refusals.
* `GradientBoostedForecastInterfaceTests` -- `ForecastInterfaceConformance` from
  `tests/test_contract.py`, against `FittedGradientBoostedQuantiles`. Not a
  bespoke test class: `ForecastInterfaceCoverageTests` discovers the fitted
  models by walking the package, so this model was *required* to arrive with a
  conformance case the moment it was written, and it did -- block 9's walk
  doing its job on the module it was written for.
* `GbmExceedanceTests` -- `ExceedancePredictorConformance` from
  `tests/test_baseline.py`, against `gbm_exceedance`, required by block 10's
  walk for the same reason.
* `LawKnotsTests` -- `law_knots`: the knots `predict_stress` inverts, handed
  out so a scoring job can record *where* a tau fell and not only what came
  out, and guarded to be that one evaluation rather than a second opinion
  about it.
* `FittedTailPwmTests` -- `_fit_gpd_pwm`: a generalised Pareto fitted to
  residual excesses by probability-weighted moments, held to its own first
  moment condition. Read only under the opt-in `tail="gpd"` (see
  `GpdTailWiringTests`): no record carries it, and nothing published can move. It is also the one class here that needs
  no `require_extra` --- sorting and sums, no array library.
* `GpdRecoveryTests` -- `_fit_gpd_pwm` again, recovering a declared shape and
  scale from a sample built through the law's quantile function: the guard on
  the plotting position, which the first moment condition cannot see. Also
  needs no `require_extra`.
* `GpdTailWiringTests` -- `tail="gpd"`: the fitted tail continues the law above
  the reported top quantile without a jump, is the GPD survival function of the
  recorded fit, is fitted to the calibration rows' excesses above that same
  quantile, attaches nothing when there are none, leaves the default law
  saturating, and its three refusals.
* `TailDeclarationTests` -- `tail` named in `model_settings` when set and absent
  when not, `--tail` reaching the fitter from `backtest` and either side of
  `compare`, and refused at selection for a model or calibration that carries
  no tail.

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


def arx_frame(count, seed=20260911):
    """Weekday rows whose next spread is linear in today's spread and both regressors.

    `s_(t+1) = 1 + 0.6 s_t + 0.08 on_rrp_t - 0.004 (sofr_volume_t - 2200) + e_t`,
    with `e_t`'s scale growing in `on_rrp_t`. The ARX's forecast is then a
    better single predictor of the target than any one column the design
    already carries, so a tree has a reason to split on it -- which the test
    asserts on each frame it relies on rather than assuming it.
    """

    rng = random.Random(seed)
    shocks = standard_normals(random.Random(seed + 1))
    rows, spread = [], 5.0
    for when in business_days(date(2020, 1, 1), count):
        on_rrp = 100.0 * rng.random()
        volume = 2000.0 + 400.0 * rng.random()
        rows.append(
            DailyObservation(
                when,
                {
                    "sofr": 4.30 + spread / 100.0,
                    "iorb": 4.30,
                    "on_rrp": on_rrp,
                    "sofr_volume": volume,
                },
            )
        )
        spread = (
            1.0
            + 0.6 * spread
            + 0.08 * on_rrp
            - 0.004 * (volume - 2200.0)
            + (1.0 + 0.02 * on_rrp) * next(shocks)
        )
    return rows


class GradientBoostedArxFeatureTests(unittest.TestCase):
    """`arx_feature="declared"`: B26's acceptance criterion and its mutation target.

    **The traps.** An ARX fitted once on the panel (every fold then reads
    coefficients estimated on its own future); a training row's column read
    from its successor, which is its target; a second ARX fitter, subtly
    different from the one `--model arx` runs; calibration rows scored with an
    ARX refitted on them; and cross-conformal block models lent the full fit's
    ARX, which saw their held-out block.

    **What the leakage probe can and cannot see.** As B23 and B24 found, the
    probe -- every row after the feature date changed, forecast and ARX
    coefficients bit-identical -- holds by construction: the fold loop hands
    the fitter a frame that ends at the feature row. The leak that remains is
    inside the training design, so the gbm is fitted a second time with the
    column computed *here*, off `baseline.fit_arx`, declared as an ordinary
    regressor: the two must agree bit for bit, residual sample included. On
    `DESIGN_ROWS` rows, with two controls: the gbm without the column is a
    different model (the trees split on it), and the column carried one row
    late is a different model again (a shifted design would be seen).

    **What a training row shares with its target.** The coefficients, fitted
    on pairs that include it: the in-sample property the GARCH parameters and
    every imputation mean already have, and the one the brief asks for ("fit
    the ARX on the fold's fit rows only"). The column reads nothing after its
    row; the coefficients are the fit rows'.

    **Why `fit_arx` grew `origins`.** A middle cross-conformal block's
    excluding model trains on the rows either side of the block. Handed those
    rows as one frame, `fit_arx` regresses the first row after the block on the
    last row before it -- a pair weeks apart, read as one step, which is a
    subtly different ARX from the full fit's. The subtest shows it is:
    `fit_arx` on the kept rows as one frame differs from the block's ARX for a
    middle block, and equals it for the first, which has no rows before it.

    Mutation record (B26)
    ---------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, one sub-copy per mutation,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B` (the worktree's `.venv`: CPython
    3.9.6, numpy 2.0.2, scikit-learn 1.6.1), `PYTHONPATH=src` (checked to
    resolve to each sub-copy), `REPO_MODEL_REQUIRE_ML=1`, `OMP_NUM_THREADS=1`,
    whole suite per run. Unmutated control green before and after, zero
    `expectedFailure`; each anchor found exactly once and confirmed applied by
    diff. Every failure below is `AssertionError` unless named otherwise.

      * **ARX fitted on all frame rows including the scored row** -- the fold
        loop hands the fitter `rows[: index + 1]` in place of the purged
        training rows (`baseline.rolling_persistence_backtest`), B24's
        mutation: the fitter is handed a frame and never a panel, so this is
        the only door a whole-panel fit has. `leakage`: the ARX state and the
        forecast move when only rows after the feature date change.
        Twenty-six other failures across `test_baseline`, `test_contract`,
        `test_generated_results` and the earlier gbm classes, because the frame
        is every model's.
      * **The forecast shifted one row forward** -- a training row's column is
        the ARX forecast from its successor (`_training_design`). `leakage`
        (the residual sample against the column declared here) and the
        calibration subtest (the widening against the same reference). This
        test and nothing else.
      * **Calibration rows refitted** -- the ARX fitted on the whole frame
        under `conformal`. The calibration subtest (the ARX is not the fit
        rows'), and `refusal: too few fit rows for the ARX`, `ValueError not
        raised`: handed the frame's 38 rows, the ARX clears its minimum. This
        test and nothing else.
      * **The full fit's ARX reused by every cross-conformal block model** --
        each block's ARX fitted on the fit rows rather than on its own training
        pairs. Every block of the cross-conformal subtest (the block's ARX is
        not `fit_arx` at its own origins), and the behavioural probe (a row
        inside the gap before the block moved the block's ARX). This test and
        nothing else. **Found on the first run:** the CV+ edge check collected
        its inputs after the per-block assertions, so a failing block left
        them empty and the check died on an `IndexError`, an error that said
        nothing about the defect; the inputs are now collected first and the
        whole record was re-run on the final test.
      * **Each refusal removed**, separately:
          - an unknown value: `ValueError not raised` -- `spread_only` fitted
            as today's gbm under a declaration naming an ARX. This test alone;
          - the setting on a model other than gbm (`cli_eval._arx_feature`):
            `SplitError not raised`. This test alone;
          - too few fit rows for the ARX -- `fit_arx`'s own minimum deleted:
            `ValueError not raised`, and
            `test_baseline.ArxExceedanceTests::test_a_training_frame_below_the_minimum_is_refused`,
            the same refusal reached through the ARX's exceedance interface.

    **Runtime, measured** on this interpreter: `fit_arx` is its leave-one-out
    law as well as its coefficients, `n` solves per fit, 0.005 s at 83 rows,
    0.15 s at 500 and 2.6 s at 2100 on this fixture. This test runs in about
    twenty-five seconds.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    PANEL_ROWS = 100
    MINIMUM_HISTORY = 90
    PURGE = 6
    DESIGN_ROWS = 240
    CALIBRATION_ROWS = 120
    CROSS_ROWS = 100
    #: A middle block, with a purge gap on both sides and rows on both sides.
    PROBE_BLOCK = 2
    SHIFT_BPS = 25.0

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

    @staticmethod
    def arx_state(arx):
        """Everything an ARX fitted: coefficients, imputations, residual sample."""

        return arx.coefficients, dict(arx.imputations), arx.residuals

    def design(self, row, arx):
        """A row as the design reads it, built here: spread, regressors, the ARX forecast."""

        return (
            [float(row.spread_bps)]
            + [float(row.values[name]) for name in self.REGRESSORS]
            + [arx.point_forecast(row)]
        )

    @staticmethod
    def sorted_levels(estimators, design):
        return sorted(float(estimator.predict([design])[0]) for estimator in estimators)

    def test_the_arx_forecast_is_fitted_per_fold_on_rows_at_or_before_the_feature_date(self):
        """One fitter, leakage, per fold, calibration, cross-conformal, the declaration, refusals.

        One criterion: an ARX forecast fitted on the wrong rows, read one row
        late, refitted on the rows it is calibrated against, lent to a block
        model that may not see its block, unnamed in the record, or produced by
        a second fitter is a column that is not the ARX's forecast from what
        was known on the day.
        """

        panel = arx_frame(self.PANEL_ROWS)
        dates = [row.date for row in panel]
        report, frames, fits = self.backtest(panel, arx_feature="declared")
        fold = report.folds[0]
        feature = dates.index(fold.feature_date)

        calibration_frame = arx_frame(self.CALIBRATION_ROWS)
        calibrated = self.fit(
            calibration_frame,
            arx_feature="declared",
            calibration="conformal",
            purge_days=0,
        )
        cross_frame = arx_frame(self.CROSS_ROWS)
        cross = self.fit(
            cross_frame,
            arx_feature="declared",
            calibration="cross_conformal",
            purge_days=self.PURGE,
        )

        with self.subTest("the feature is baseline's own ARX one-step forecast"):
            for frame, model in (
                (frames[0], fits[0]),
                (frames[-1], fits[-1]),
            ):
                own = baseline.fit_arx(frame, self.REGRESSORS)
                self.assertIsInstance(model.arx, baseline.FittedArx)
                self.assertEqual(self.arx_state(model.arx), self.arx_state(own))
                self.assertEqual(
                    [model.design_row(row)[-1] for row in frame],
                    [own.point_forecast(row) for row in frame],
                    msg="the column is not fit_arx's own point forecast at each row",
                )

        with self.subTest("leakage"):
            self.assertGreater(
                report.purge_days, 0, msg="at a zero gap the scored day is the next row"
            )
            later = panel[: feature + 1] + [
                with_spread_shifted(row, self.SHIFT_BPS) for row in panel[feature + 1 :]
            ]
            again, _, again_fits = self.backtest(later, arx_feature="declared")
            self.assertEqual(again.folds[0], fold)
            self.assertEqual(
                (
                    self.arx_state(again_fits[0].arx),
                    again.forecasts[0].predicted_bps,
                    again.forecasts[0].quantiles_bps,
                ),
                (
                    self.arx_state(fits[0].arx),
                    report.forecasts[0].predicted_bps,
                    report.forecasts[0].quantiles_bps,
                ),
                msg=f"the fold from {fold.feature_date} moved when only later rows changed",
            )
            back = (
                panel[: feature - 1]
                + [with_spread_shifted(panel[feature - 1], self.SHIFT_BPS)]
                + panel[feature:]
            )
            moved, _, moved_fits = self.backtest(back, arx_feature="declared")
            self.assertNotEqual(moved_fits[0].arx.coefficients, fits[0].arx.coefficients)
            self.assertNotEqual(
                moved.forecasts[0].quantiles_bps, report.forecasts[0].quantiles_bps
            )

            # Inside the design: the gbm with the column computed here and
            # declared as an ordinary regressor is the same model, down to the
            # residual sample every training design row contributes to.
            rows = arx_frame(self.DESIGN_ROWS)
            whole = self.fit(rows, arx_feature="declared")
            expected = [baseline.fit_arx(rows, self.REGRESSORS).point_forecast(row) for row in rows]
            declared = self.REGRESSORS + ("arx_check",)
            checked = with_column(rows, "arx_check", expected)
            reference = self.fit(checked, regressors=declared)
            self.assertEqual(reference.residuals, whole.residuals)
            self.assertEqual(reference.predict(checked[-1]), whole.predict(rows[-1]))
            # The controls. The gbm without the column is a different model on
            # this frame, so the trees split on it...
            self.assertNotEqual(
                self.fit(rows).residuals,
                whole.residuals,
                msg="the control: the gbm does not read the ARX column on this frame",
            )
            # ...and each row carrying its successor's forecast -- a training
            # row reading its target's spread -- is a different model again.
            late = self.fit(
                with_column(rows, "arx_check", expected[1:] + expected[-1:]),
                regressors=declared,
            )
            self.assertNotEqual(
                late.residuals,
                reference.residuals,
                msg="the control: a column one row late fits the same trees",
            )

        with self.subTest("per fold"):
            self.assertGreater(len(fits), 1)
            self.assertLess(fits[0].cutoff, fits[-1].cutoff)
            self.assertNotEqual(
                fits[0].arx.coefficients,
                fits[-1].arx.coefficients,
                msg="two folds with different training ends fitted one ARX",
            )
            for frame, model in zip(frames, fits):
                with self.subTest(train_end=frame[-1].date.isoformat()):
                    self.assertEqual(model.arx.cutoff, frame[-1].date)
                    self.assertEqual(
                        self.arx_state(model.arx),
                        self.arx_state(baseline.fit_arx(frame, self.REGRESSORS)),
                        msg="the fold's ARX is not the fit on the fold's own rows",
                    )

        with self.subTest("calibration rows use the fit rows' ARX"):
            rows = calibration_frame
            fit_rows = [row for row in rows if row.date <= calibrated.fit_end]
            self.assertLess(len(fit_rows), len(rows))
            own = baseline.fit_arx(fit_rows, self.REGRESSORS)
            refitted = baseline.fit_arx(rows, self.REGRESSORS)
            self.assertEqual(
                self.arx_state(calibrated.arx),
                self.arx_state(own),
                msg="the ARX was not fitted on the fit rows alone",
            )
            self.assertNotEqual(
                own.coefficients,
                refitted.coefficients,
                msg="the fixture: fit rows and frame fit the same ARX",
            )
            expected = [own.point_forecast(row) for row in rows]
            self.assertEqual([calibrated.design_row(row)[-1] for row in rows], expected)
            # The widening is scored off exactly those forecasts...
            declared = self.REGRESSORS + ("arx_check",)
            reference = self.fit(
                with_column(rows, "arx_check", expected),
                regressors=declared,
                calibration="conformal",
                purge_days=0,
            )
            self.assertEqual(reference.widening, calibrated.widening)
            # ...which the widening does read: the control moves the
            # calibration rows' column by 25 bp and the widening moves. (An ARX
            # refitted on the frame forecasts too close to the fit rows' to
            # move this one order statistic on this fixture, measured; the
            # coefficient assertion above is what sees a refit.)
            mixed = expected[: len(fit_rows)] + [
                value + self.SHIFT_BPS for value in expected[len(fit_rows) :]
            ]
            self.assertNotEqual(
                self.fit(
                    with_column(rows, "arx_check", mixed),
                    regressors=declared,
                    calibration="conformal",
                    purge_days=0,
                ).widening,
                calibrated.widening,
                msg="the control: the widening does not read the calibration rows' ARX column",
            )

        with self.subTest("each block model's ARX is fitted without its block and purge gaps"):
            rows = cross_frame
            cross_dates = [row.date for row in rows]
            gap = timedelta(days=self.PURGE)
            self.assertEqual(
                self.arx_state(cross.arx), self.arx_state(baseline.fit_arx(rows, self.REGRESSORS))
            )
            blocks = cross.calibration_blocks
            self.assertEqual(len(blocks), ml.DEFAULT_CALIBRATION_FOLDS)
            full = self.sorted_levels(cross._estimators, self.design(rows[-1], cross.arx))
            lows, highs = [], []
            for number, block in enumerate(blocks, start=1):
                # CV+'s inputs first, so the edge check below does not depend on
                # every block's assertions passing.
                excluded = self.sorted_levels(
                    block.estimators, self.design(rows[-1], block.arx)
                )
                lows.extend(excluded[0] - score for score in block.scores)
                highs.extend(excluded[-1] + score for score in block.scores)
                with self.subTest(block=number):
                    kept = [
                        when + gap < block.held_out_start or block.held_out_end + gap < when
                        for when in cross_dates
                    ]
                    origins = [
                        p for p in range(len(rows) - 1) if kept[p] and kept[p + 1]
                    ]
                    self.assertEqual(
                        self.arx_state(block.arx),
                        self.arx_state(
                            baseline.fit_arx(rows, self.REGRESSORS, origins=origins)
                        ),
                        msg=f"block {number}'s ARX is not fit_arx on its own training pairs",
                    )
                    self.assertNotEqual(block.arx.coefficients, cross.arx.coefficients)
                    one_frame = baseline.fit_arx(
                        [row for row, keep in zip(rows, kept) if keep], self.REGRESSORS
                    )
                    if number == 1:
                        # No rows before the block: its training rows are one
                        # run, and fit_arx on them as a frame is the same ARX.
                        self.assertEqual(self.arx_state(block.arx), self.arx_state(one_frame))
                    elif number == self.PROBE_BLOCK + 1:
                        self.assertNotEqual(
                            block.arx.coefficients,
                            one_frame.coefficients,
                            msg="a pair spanning the block changes nothing on this fixture",
                        )
                    # Every held-out score is this block's estimators read at a
                    # design carrying this block's ARX forecast.
                    rescored = []
                    for when in block.scored_dates:
                        index = cross_dates.index(when)
                        position = max(
                            p for p in range(index) if cross_dates[p] + gap < when
                        )
                        levels = self.sorted_levels(
                            block.estimators, self.design(rows[position], block.arx)
                        )
                        target = rows[index].spread_bps
                        rescored.append(max(levels[0] - target, target - levels[-1]))
                    self.assertEqual(list(block.scores), rescored)
            # A forecast reads every block's own ARX for CV+'s edges.
            q = Fraction("0.95") - Fraction("0.05")
            count = len(lows)
            reported = cross.predict(rows[-1])
            self.assertEqual(
                (reported[0], reported[-1]),
                (
                    min(sorted(lows)[math.floor((1 - q) * (count + 1)) - 1], full[1]),
                    max(sorted(highs)[math.ceil(q * (count + 1)) - 1], full[-2]),
                ),
            )

            # By behaviour: a row the probe block's model may not train on
            # leaves its ARX bit-identical, and moves the full fit's.
            block = blocks[self.PROBE_BLOCK]
            start = cross_dates.index(block.held_out_start)
            stop = cross_dates.index(block.held_out_end)

            def moved(position):
                shifted = list(rows)
                shifted[position] = with_spread_shifted(rows[position], self.SHIFT_BPS)
                return self.fit(
                    shifted,
                    arx_feature="declared",
                    calibration="cross_conformal",
                    purge_days=self.PURGE,
                )

            for label, position in (
                ("inside the gap before the block", start - 1),
                ("inside the block", start + 1),
                ("inside the gap after the block", stop + 1),
            ):
                refit = moved(position)
                self.assertEqual(
                    self.arx_state(refit.calibration_blocks[self.PROBE_BLOCK].arx),
                    self.arx_state(block.arx),
                    msg=f"a row {label} ({cross_dates[position]}) moved the block's ARX",
                )
                self.assertNotEqual(
                    refit.arx.coefficients,
                    cross.arx.coefficients,
                    msg=f"the control: the full fit's ARX does not read the row {label}",
                )
            clear = stop + 1
            while not cross_dates[stop] + gap < cross_dates[clear]:
                clear += 1
            self.assertNotEqual(
                moved(clear + 1).calibration_blocks[self.PROBE_BLOCK].arx.coefficients,
                block.arx.coefficients,
                msg="the control: a row the block's model trains on moves nothing in its ARX",
            )

        with self.subTest("the declaration names arx_feature; absent when not set"):
            self.assertEqual(dict(report.model_settings), {"arx_feature": "declared"})
            self.assertEqual(
                dict(baseline._model_settings(calibrated)),
                {"calibration": "conformal", "calibration_share": 0.25, "arx_feature": "declared"},
            )
            self.assertEqual(
                dict(baseline._model_settings(cross)),
                {"calibration": "cross_conformal", "calibration_folds": 5, "arx_feature": "declared"},
            )
            self.assertEqual(
                fits[0].design_names, ("spread_bps",) + self.REGRESSORS + ("arx_forecast",)
            )
            # Read off spread_bps and the declared regressors; not a panel column.
            self.assertEqual(fits[0].features_read, ("spread_bps",) + self.REGRESSORS)
            composed = self.fit(
                panel[:40],
                arx_feature="declared",
                spread_change_lags=2,
                volatility_feature="garch11",
            )
            self.assertEqual(
                composed.design_names,
                ("spread_bps",)
                + self.REGRESSORS
                + ("spread_change_lag_1", "spread_change_lag_2", "garch11_variance", "arx_forecast"),
            )
            self.assertEqual(
                dict(baseline._model_settings(composed)),
                {"spread_change_lags": 2, "volatility_feature": "garch11", "arx_feature": "declared"},
            )
            plain = self.fit(panel[:30])
            self.assertEqual(dict(baseline._model_settings(plain)), {})
            self.assertEqual(plain.design_names, ("spread_bps",) + self.REGRESSORS)
            self.assertIsNone(plain.arx)
            parser = cli.build_parser()
            common = ["--registry", "registry.json", "--decision-time", DECISION_TIME]
            backtest = parser.parse_args(
                ["backtest", "panel.csv", *common, "--report", "r.json",
                 "--feature", "on_rrp", "--feature", "spread_bps", "--model", "gbm",
                 "--arx-feature", "declared"]
            )
            _, fitter = cli_eval._select_fitter(backtest)
            self.assertEqual(
                fitter.keywords, {"regressors": ("on_rrp",), "arx_feature": "declared"}
            )

        with self.subTest("refusal: an unknown value"):
            with self.assertRaisesRegex(ValueError, r"unknown arx_feature 'spread_only'"):
                self.fit(panel[:40], arx_feature="spread_only")

        with self.subTest("refusal: the setting on a model other than gbm"):
            parser = cli.build_parser()
            common = ["--registry", "registry.json", "--decision-time", DECISION_TIME]
            backtest = parser.parse_args(
                ["backtest", "panel.csv", *common, "--report", "r.json",
                 "--feature", "on_rrp", "--feature", "spread_bps", "--model", "arx",
                 "--arx-feature", "declared"]
            )
            with self.assertRaisesRegex(
                SplitError, r"--arx-feature declared was given, but --model arx"
            ):
                cli_eval._select_fitter(backtest)
            compare = parser.parse_args(
                ["compare", "panel.csv", *common, "--report", "r.json",
                 "--model-a", "persistence", "--feature-a", "spread_bps",
                 "--arx-feature-a", "declared",
                 "--model-b", "gbm", "--feature-b", "on_rrp", "--feature-b", "spread_bps",
                 "--arx-feature-b", "declared", "--calibration-b", "cross_conformal"]
            )
            with self.assertRaisesRegex(
                SplitError, r"--arx-feature-a declared was given, but --model-a persistence"
            ):
                cli_eval._select_fitter(cli_eval._side(compare, "a"), side="-a")
            _, fitter = cli_eval._select_fitter(cli_eval._side(compare, "b"), side="-b")
            self.assertEqual(
                fitter.keywords,
                {
                    "regressors": ("on_rrp",),
                    "calibration": "cross_conformal",
                    "arx_feature": "declared",
                },
            )

        with self.subTest("refusal: too few fit rows for the ARX"):
            # fit_arx's own minimum, on the fit rows and not the frame: 38 rows
            # clear gbm's minimum and half of them are held out.
            with self.assertRaisesRegex(
                ValueError, r"arx needs at least 20 training rows, got 19"
            ):
                self.fit(panel[:38], arx_feature="declared", calibration="conformal",
                         calibration_share=0.5, purge_days=0)
            # And twenty is enough: the refusal sits at the edge.
            edge = self.fit(panel[:40], arx_feature="declared", calibration="conformal",
                            calibration_share=0.5, purge_days=0)
            self.assertEqual(edge.arx.cutoff, panel[19].date)
            with self.assertRaisesRegex(
                ValueError, r"arx needs at least 20 training rows, got 19"
            ):
                self.fit(panel[:19], minimum_history=10, arx_feature="declared")


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


class LawKnotsTests(unittest.TestCase):
    """`law_knots`: the law `predict_stress` inverts, handed out and guarded.

    **Why the knots had to come out.** `gbm_exceedance`'s curve is nearly flat
    at the wide thresholds, and that is not a gbm artefact -- `arx_exceedance`,
    scored identically, flattens the same way. The live question is no longer
    whether the learner is wrong but what the *law* can express out there, and
    that question cannot be asked of this object: `_law` is private, and
    `predict_stress` returns floats and throws its knots away. A scoring job
    that wants to record which segment each tau landed in has nothing to read.
    This class is that read, and the guard on it.

    **What it is not.** Nothing here measures the tail. No fold count, no
    pooled mean, no claim about where a 50 bp tau falls on the panel -- the
    measurement is a jobs-lane run against this method, and a version of it
    fabricated on a forty-eight-row fixture would answer a different question
    than the one asked.

    **The trap, and why the count assertion is the whole point.** Every
    equality in this test passes under an implementation whose `law_knots`
    evaluates `_law` a second time, because two evaluations of a deterministic
    fit agree to the last bit. Nothing a caller can assert *afterwards*
    distinguishes derived from re-derived; the distinction lives in the call
    graph. So the test counts entries into `_reported` for a row whose knots
    and exceedance are both asked for, and requires one. That is
    `predict_stress`' own "not a second opinion about it" rule, one level down,
    and it is what stops a published record's knots and its probabilities from
    being able to disagree later.

    The counting subtest asks about a row **no earlier subtest touched**, and
    has to: `_shared_law` remembers one row, so a row already asked about
    enters `_reported` zero times and the count would pass for the wrong
    reason. The row is named there rather than here because that is where the
    dependency is.

    Mutation record
    ---------------

    Run in a disposable copy under `$HOME` built from `git ls-files -z --cached
    --others --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3
    -B` and `OMP_NUM_THREADS=1`, on CPython 3.9.6 with numpy 2.0.2 and
    scikit-learn 1.6.1. Unmutated control green before and after; each mutation
    confirmed applied by grep, and restored before the next. Every target was
    checked to appear exactly once in its file first.

    1. **`law_knots` re-evaluates the law instead of sharing the one
       evaluation.** `return self._shared_law(feature_row)` ->
       `return self._law(feature_row)` in
       `FittedGradientBoostedQuantiles.law_knots`. Kills this test and nothing
       else, `AssertionError`: two entries into `_reported` where the record
       claims one. Every other subtest here stays green under it, and that is
       the trap demonstrated rather than asserted -- the knots are still
       correct, still non-decreasing, still inverted by `predict_stress`
       element for element. They are simply not the knots those floats came
       from, and no assertion about their values can say so.
    2. **The top level of the returned grid is the top declared level.**
       `(0.0,) + self.levels + (1.0,)` -> `(0.0,) + self.levels + (0.95,)` in
       `FittedGradientBoostedQuantiles._law`. Kills this test alone, two
       subtests, both `AssertionError`: the grid, and the tau read inside the
       final segment, whose exceedance becomes exactly `0.05` at every point of
       `[Q(0.95), high]` instead of falling across it.

       **A finding, and the reason this subtest exists.** The conformance
       cases do *not* see this. `test_the_exceedance_is_strictly_above_the_
       threshold` stays green on all five implementers, because
       `_exceedance_from_law` returns `0.0` from its `tau >= values[-1]` branch
       without consulting the level at all -- so saturation at the top knot
       survives a grid that places five per cent of its mass beyond it. What
       breaks under the mutation is only the interior of the final segment: the
       law goes flat exactly where the wide taus are read. The closure at `1.0`
       was unguarded until this test, and it is unguarded precisely in the
       region the tail measurement this block exists to enable would report.
    3. **The empty-tau-family refusal removed.** `if not family: raise
       ValueError("no stress thresholds declared")` deleted from
       `baseline._validate_taus_bp`. Kills this test, `AssertionError` ("no
       exception raised"; `predict_stress` returns an empty tuple), together
       with `test_a_tau_family_that_is_not_ascending_is_refused` on all five
       `ForecastInterfaceConformance` cases -- `ForecastInterfaceTests`,
       `ArxForecastInterfaceTests`, `ThresholdForecastInterfaceTests`,
       `RollingResidualLawForecastInterfaceTests` and
       `GradientBoostedForecastInterfaceTests` -- same type. The refusal is
       `baseline`'s and is reached rather than reimplemented here; what this
       test adds is the refusal on the route this block newly exposes, where a
       caller holding knots beside an empty curve would record a law nothing
       was read off.
    4. **The memo key dropped to the row's date alone.** `key =
       (feature_row.date, tuple(sorted(feature_row.values.items(), ...)))` ->
       `key = feature_row.date` in `_shared_law`. Kills this test alone,
       `AssertionError`: two rows sharing a date, differing in `on_rrp`, get
       the same knots, because the second read the first's memo.

       This was written as a control expected to survive, and it did -- until
       the subtest that kills it was added. **It survived for an ordering
       reason, not a correctness one**: with the columns out of the key the
       only row that could have exposed the collision was the missing-regressor
       row, which carries `rows[-1]`'s date, and by the time it is asked the
       memo holds `rows[-2]`. A guard that passes because of the order its own
       subtests run in is not a guard, so the collision is now asserted
       directly. The finding is about the memo generally: new state whose
       failure mode is returning another row's answer cannot be left to a
       fixture that happens not to collide.
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

    def test_the_exposed_knots_are_the_law_predict_stress_inverts(self):
        """The knots are the grid, they are the law, and there is one of them.

        Six claims, one criterion. The shape of the returned grid, the
        element-for-element inversion, the saturation the docstring promises,
        the single evaluation, and the two refusals are each meaningless
        alone: knots that were not what `predict_stress` read are a second
        opinion however well-formed, an inversion that agrees with re-derived
        knots proves nothing about the ones a record would carry, and a knot
        set handed out for a row the model cannot read is a fabrication.
        """

        rows = crossing_frame()
        model = self.fit(rows)
        row = rows[-1]
        values, levels = model.law_knots(row)

        with self.subTest("the grid is the declared levels closed at 0 and 1"):
            self.assertEqual(levels, (0.0,) + QUANTILE_LEVELS + (1.0,))
            self.assertEqual(len(values), len(levels))
        with self.subTest("the values are non-decreasing"):
            self.assertEqual(
                list(values),
                sorted(values),
                msg="a knot set that is not increasing is not a distribution",
            )

        # A tau family placed off the knots themselves: below the lowest, one
        # inside every segment including the final `[Q(0.95), high]`, at the
        # top knot and above it. Strictly ascending, which `predict_stress`
        # requires, because the knots on this fixture are strictly ascending --
        # asserted here rather than assumed, since a tie would silently collapse
        # two of the placements onto one value and stop testing a segment.
        self.assertTrue(
            all(lower < upper for lower, upper in zip(values, values[1:])),
            msg=f"the fixture's knots are not strictly ascending: {values}",
        )
        interior_taus = tuple(
            0.5 * (lower + upper) for lower, upper in zip(values, values[1:])
        )
        taus = (values[0] - 1.0,) + interior_taus + (values[-1], values[-1] + 1.0)

        with self.subTest("predict_stress inverts exactly these knots"):
            self.assertEqual(
                model.predict_stress(row, taus),
                tuple(ml._exceedance_from_law(values, levels, tau) for tau in taus),
            )
        with self.subTest("a tau above the top declared level is read in one segment"):
            # The reason the knots are worth exposing: everything above Q(0.95)
            # is read inside the single straight segment `[Q(0.95), high]`, so
            # its exceedance lies strictly between 0.0 and 1 - 0.95 and carries
            # no distributional shape of its own. A job that recorded only the
            # float could not tell that from a learner with nothing to say.
            above = ml._exceedance_from_law(values, levels, interior_taus[-1])
            self.assertGreater(above, 0.0)
            self.assertLess(above, 1.0 - QUANTILE_LEVELS[-1])
        with self.subTest("the law saturates outside its knots, exactly"):
            self.assertEqual(
                model.predict_stress(row, (values[-1],)),
                (0.0,),
                msg="a tau at the top knot must be exactly zero, not nearly",
            )
            self.assertEqual(model.predict_stress(row, (values[-1] + 1.0,)), (0.0,))
            self.assertEqual(model.predict_stress(row, (values[0] - 1.0,)), (1.0,))

        with self.subTest("the knots and the curve come from one evaluation"):
            # `rows[-2]`, which nothing above asked about: `_shared_law`
            # remembers one row, so a row already evaluated would enter
            # `_reported` zero times and pass this for the wrong reason.
            fresh = rows[-2]
            entered = []
            reported = ml.FittedGradientBoostedQuantiles._reported

            def counting(self, feature_row):
                entered.append(feature_row.date)
                return reported(self, feature_row)

            with mock.patch.object(
                ml.FittedGradientBoostedQuantiles, "_reported", counting
            ):
                recorded_values, recorded_levels = model.law_knots(fresh)
                curve = model.predict_stress(fresh, taus)
            self.assertEqual(
                len(entered),
                1,
                msg=(
                    "the knots and the probabilities a record would carry came "
                    "from two evaluations of the fit; they agree here because "
                    "the fit is deterministic, and nothing downstream could "
                    "tell if they stopped agreeing"
                ),
            )
            self.assertEqual(
                curve,
                tuple(
                    ml._exceedance_from_law(recorded_values, recorded_levels, tau)
                    for tau in taus
                ),
            )

        with self.subTest("two rows sharing a date are two rows"):
            # `_shared_law` remembers one row, and a row is its date *and* its
            # columns. Keyed on the date alone the memo would hand this row the
            # previous one's knots -- a wrong law, silently, for a caller
            # scoring two vintages of the same day. `on_rrp` is moved between
            # the fixture's own two regimes so the laws certainly differ.
            twin = DailyObservation(fresh.date, dict(fresh.values, on_rrp=20.0))
            self.assertNotEqual(model.law_knots(twin), model.law_knots(fresh))

        with self.subTest("a row missing a declared regressor is not answered"):
            blind = DailyObservation(
                row.date, {"sofr": 4.60, "iorb": 4.30, "sofr_volume": 2200.0}
            )
            with self.assertRaises(baseline.MissingRegressorError) as caught:
                model.law_knots(blind)
            self.assertIn("on_rrp", str(caught.exception))
        with self.subTest("an empty tau family is refused"):
            with self.assertRaises(ValueError) as caught:
                model.predict_stress(row, ())
            self.assertIn("no stress thresholds declared", str(caught.exception))


class FittedTailPwmTests(unittest.TestCase):
    """`_fit_gpd_pwm`: a generalised Pareto tail fitted by moments, and nothing wired.

    **Why a fitted tail exists to be built.** `LawKnotsTests` above handed the
    law out so a scoring job could record where a tau fell, and the job then
    ran: over the folds of the panel the conditional `Q(0.95)` sits a couple of
    basis points *below* zero, so every declared threshold --- 5 bp included ---
    is read inside the single straight segment that runs from `Q(0.95)` to the
    largest residual the fit ever saw, and beyond that segment's top the law
    gives a wide move probability exactly zero. A piecewise-linear law has no
    tail to read; it has a last knot. This estimator is the shape that goes
    above `Q(0.95)` instead.

    **What this class is not.** Nothing here is wired to anything. No caller
    reads `_fit_gpd_pwm`, `predict_stress` is untouched, no record carries a
    `FittedTail`, and no published figure can move --- deliberately, so that the
    estimator can be got right before the law changes shape underneath the
    records that were produced with it. (Wired two blocks later, behind the
    opt-in `tail="gpd"`: `GpdTailWiringTests` below. The default law, and so
    every published figure, still does not read it, and no record carries it.)

    **Residual space, and why it is not a choice made here.** The excesses are
    residual excesses above the conditional `Q(0.95)`, never level excesses. The
    measurement is what settles it: the law's top knot has an enormous spread
    across folds and takes a nearly distinct value on each, which is the anchor
    translating from feature row to feature row rather than the tail's shape
    changing. Residuals are the part that is exchangeable across folds; a
    level-space excess would spend its hundred-odd points re-learning an anchor
    the model already reports.

    **No `require_extra`.** Alone among the classes in this file, this one runs
    on a checkout without the `ml` extra: the estimator is sorting and sums, and
    reaches no third-party package. That is a property worth having rather than
    an oversight --- an estimator with no array library behind it is one
    `tests/test_dependency_boundary.py` never has to arbitrate, and one the core
    suite exercises on every interpreter rather than skipping.

    The criterion, and why it is this one
    -------------------------------------

    The estimator inverts the fitted law's own first two probability-weighted
    moments, so `sigma / (1 - xi)` is `a_0` by construction, and `a_0` is the
    arithmetic mean of the excesses. The test asserts that equality on a
    committed sample, together with `clamped` and `fallback` both false. It
    needs no RNG, no drawn sample and no distributional tolerance, and it is
    exact rather than approximate --- a recovery test against a draw would be
    neither.

    **It is also what makes the clamp honest, and that is why the second sample
    is here.** Clamping `xi` breaks the identity, so an estimator that clamps
    and does not say so cannot pass: on the first sample a clamp applied where
    none was needed and hidden moves `sigma / (1 - xi)` off the mean, and on the
    second --- a sample carrying one residual many times the others, which is
    exactly the fit `GPD_SHAPE_BOUNDS` exists to take back --- `clamped` is
    required to be true. The identity is deliberately *not* asserted on the
    second sample. It does not hold there, and asserting a loosened version of
    it would be asserting that the clamp did nothing.

    A finding: the criterion cannot see the plotting position
    ---------------------------------------------------------

    The brief for this block expected the first-moment condition to fail under
    "the wrong plotting position". **It does not, and it cannot.** Writing
    `d = a_0 - 2 a_1`, the estimator is `xi = 2 - a_0 / d` and
    `sigma = 2 a_0 a_1 / d`, so `1 - xi = 2 a_1 / d` and

        sigma / (1 - xi) = (2 a_0 a_1 / d) * (d / 2 a_1) = a_0

    for *any* value of `a_1` whatever. `a_1` enters the numerator and the
    denominator identically and cancels. The identity pins `xi` and `sigma`
    against each other and against `a_0`; it says nothing at all about how `a_1`
    was formed, and the plotting position lives entirely inside `a_1`. Mutation
    1 below confirms it on both committed samples: the left-hand side is
    unchanged to the last bit and neither sample's clamp state moves.

    This generalises past this one mutation, which is the part worth recording.
    **No assertion that compares the fit against moments the test computes by
    the same convention can see the convention.** The second moment condition
    has the same blindness for the same reason --- `a_1 = sigma / (2 (2 - xi))`
    is just the other half of the inverse map, and it would be checked against
    the same wrongly-weighted `a_1`. What would see it is a committed expected
    `xi`, which is a regression pin and a different criterion, or a recovery
    test against a drawn sample, which the brief declined for reasons that still
    hold. Per `CLAUDE.md`, a mutation that survives is reported here rather than
    answered with a second test; which of those two the tail is eventually
    pinned with is a decision, not a gap to be filled in quietly. (Decided in
    the next block: neither. `GpdRecoveryTests` below recovers a declared law
    from a sample built through its quantile function, which is not a draw and
    not a pin, and kills mutation 1.)

    What is deliberately unpinned
    -----------------------------

    The exponential fallback below `GPD_MINIMUM_EXCESSES`, the three refusals,
    and the lower end of `GPD_SHAPE_BOUNDS` have no assertion here. One block,
    one criterion; they are named so that a later block adds them knowingly
    rather than discovering them absent.

    Mutation record
    ---------------

    Run in a disposable copy under `$HOME` built from `git ls-files -z --cached
    --others --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`
    and `OMP_NUM_THREADS=1`, on CPython 3.9.6. The copy is gitignore-clean and
    so carries no `.venv`, so the suite is run there with the mount's
    `.venv/bin/python` by absolute path --- otherwise the `ml` extra is absent,
    every other class in this file skips, and a mutation "survives" a suite that
    never ran. Unmutated control green before and after; each mutation confirmed
    applied by grep, and restored before the next.

    1. **The plotting position dropped.** `_GPD_PLOTTING_OFFSET = 0.35` ->
       `0.0` in `ml.py`. **Survives**, here and across the whole suite. The
       algebra above says why, and the numbers agree: on the first committed
       sample `xi` moves from about `0.154` to about `0.248` and `sigma` from
       about `1.433` to about `1.274`, while `sigma / (1 - xi)` is `1.69375`
       either way --- the sample mean, unmoved --- and the fit stays unclamped.
       On the second sample `xi` moves from about `0.786` to about `0.831` and
       the clamp binds under both. This is the finding recorded above, not a
       mutation that merely happened to miss.
    2. **The factor of two in the denominator.** `denominator = a_0 - 2.0 * a_1`
       -> `a_0 - 1.0 * a_1` in `ml._fit_gpd_pwm`. Kills this test and nothing
       else, two subtests, both `AssertionError`, and by both halves of the
       criterion at once. With `d' = a_0 - a_1` the algebra gives `1 - xi =
       a_1 / d'`, so the identity would return `2 a_0` --- `3.3875` against a
       mean of `1.69375` --- but the *observed* left-hand side is `2.0143`,
       because the mutation also lifts the first sample's `xi` to about `0.703`
       and the clamp takes it to `0.5` before the identity is read. So the
       clamp subtest fails first and the identity subtest fails on a number the
       clamp shaped. Recorded as observed rather than as predicted: the two
       guards in this estimator interact, and the clean factor of two is what
       an unclamped estimator would have shown.
    3. **The clamp applied without being recorded.** `clamped = not lower <= xi
       <= upper` -> `clamped = False` in `ml._fit_gpd_pwm`, leaving the clamp
       itself in place behind `if clamped:` --- so the shape is silently
       unbounded, which is the more dangerous half of the defect and the one
       the flag exists to stop. Kills this test alone, `AssertionError`: the
       second sample's fit reports `clamped` false over a `xi` of about `0.786`.
       This is the mutation the brief named as the one that matters, and it
       kills.
    4. **Control, expected to survive**: `GPD_MINIMUM_EXCESSES` 20 -> 5. Green
       throughout, as recorded under "what is deliberately unpinned" --- both
       committed samples are above either value, so no assertion here reaches
       the fallback branch. Recorded rather than covered by an assertion
       invented for it.
    """

    #: Residual excesses above a conditional `Q(0.95)`, in basis points, in the
    #: order a caller would have collected them --- not sorted. The estimator
    #: sorts, and `a_0` is `math.fsum`, so the identity below is exact whatever
    #: order these arrive in; a pre-sorted literal would have let an estimator
    #: that forgot to sort pass for the wrong reason.
    #:
    #: Chosen to fit unclamped and to fit unclamped *comfortably*: `xi` is about
    #: `0.154`, near the middle of `GPD_SHAPE_BOUNDS` rather than beside an end.
    #: A sample sitting just inside the clamp would make more mutations red, and
    #: would make them red by tipping over a boundary --- a fixture whose
    #: unclamped-ness is marginal reports "clamped" for reasons that have
    #: nothing to do with the defect under test.
    UNCLAMPED = (
        0.39, 1.17, 0.67, 1.39, 1.48, 0.10, 0.02, 2.92,
        0.43, 0.38, 11.76, 0.93, 2.91, 0.95, 1.54, 0.23,
        1.52, 3.31, 1.10, 2.10, 1.70, 0.09, 2.22, 1.34,
    )

    #: A sample that clamps, and the shape of sample that does: ordinary
    #: excesses of a basis point or two with one residual of about 83, which
    #: drags the PWM shape to about `0.786` --- past `0.5`, so an infinite
    #: variance inferred from a single point. The identity is not asserted on
    #: this one. It does not hold, and that is the clamp working.
    CLAMPING = (
        13.97, 12.02, 0.06, 0.09, 4.05, 2.38, 1.78, 0.43,
        1.38, 1.39, 1.26, 0.18, 0.71, 0.61, 2.24, 82.97,
        12.35, 1.09, 0.75, 0.35, 0.04, 0.03,
    )

    def test_the_unclamped_fit_satisfies_its_own_first_moment_condition(self):
        """`sigma / (1 - xi)` is the mean of the excesses, and the clamp says so.

        Two claims, one criterion, and they are one because either alone is
        satisfiable by an estimator that is wrong. The identity holds for the
        *clamped* pair too if the clamp never binds, so it proves something
        about a fit only alongside the record's own statement that this fit was
        not clamped and was not the fallback; and `clamped=False` on its own is
        a boolean any implementation can return. Together they say: this pair of
        numbers is the probability-weighted-moment solution for this sample, and
        nothing intervened between the moments and the pair.

        The mean is recomputed here from the committed literal rather than read
        off `a_0`, with `math.fsum` as the estimator uses, so the two agree
        independently of the order the excesses were written in.
        """

        fit = ml._fit_gpd_pwm(self.UNCLAMPED)
        mean = math.fsum(self.UNCLAMPED) / len(self.UNCLAMPED)

        with self.subTest("the record says the fit is the sample's own"):
            self.assertFalse(
                fit.clamped,
                msg="the sample was chosen to fit inside GPD_SHAPE_BOUNDS; a "
                "clamped fit here means the estimator moved xi, and the "
                "identity below would be asserted over a pair no sample "
                "produced",
            )
            self.assertFalse(
                fit.fallback,
                msg="the sample carries more than GPD_MINIMUM_EXCESSES "
                "excesses, so a shape was fitted; a fallback here is an "
                "exponential being reported as a fit",
            )
            self.assertEqual(fit.excesses, len(self.UNCLAMPED))

        with self.subTest("sigma / (1 - xi) is the arithmetic mean"):
            self.assertAlmostEqual(
                fit.sigma / (1.0 - fit.xi),
                mean,
                delta=abs(mean) * 1e-14,
                msg="the fitted law's own first moment is not the mean of the "
                "excesses it was fitted to; the estimator is not the PWM "
                "solution of this sample",
            )

        with self.subTest("a sample whose shape the clamp takes back says so"):
            heavy = ml._fit_gpd_pwm(self.CLAMPING)
            self.assertTrue(
                heavy.clamped,
                msg="a sample whose PWM shape lands outside GPD_SHAPE_BOUNDS "
                "was clamped without the record saying so; the reported xi is "
                "then a bound presented as an estimate",
            )


class GpdRecoveryTests(unittest.TestCase):
    """`_fit_gpd_pwm` returns a declared generalised Pareto from its own quantiles.

    **Why this class exists beside `FittedTailPwmTests`.** That class holds the
    fit to its first moment condition, and its own docstring records that the
    condition cannot see the plotting position. Written out once more, because
    the two tests read the same fit and must not be mistaken for duplicates:
    with `d = a_0 - 2 a_1`,

        1 - xi = 2 a_1 / d,   sigma = 2 a_0 a_1 / d,
        sigma / (1 - xi) = (2 a_0 a_1 / d) * (d / 2 a_1) = a_0

    for *any* `a_1`. `a_1` cancels, `a_0` is the plain mean, and
    `_GPD_PLOTTING_OFFSET` lives entirely inside `a_1` --- so before this class
    the whole `a_1` limb of the estimator could be changed without a test
    moving. This class reads `a_1`: the sample is built *through* a set of
    plotting positions from a declared `(xi, sigma)`, so the recovered pair
    depends on how the estimator weights each order statistic, and a wrong
    weighting moves it off the declared truth.

    **The anchor is the declared distribution, not today's output.** Nothing
    here is a committed fitted value. The expected `xi` and `sigma` are the ones
    the sample was generated from; a regression pin would kill the same
    mutations and would assert only that the code does what it did.

    **The design reads `0.35` as a literal, not `ml._GPD_PLOTTING_OFFSET`.** The
    positions `(j - 0.35) / n` are Hosking and Wallis' convention, declared here
    as a property of the sample. Reading the module constant instead would move
    the sample with the mutation it is meant to catch --- a check anchored to
    the thing it checks --- and at an offset of `0.0` it would place the last
    point at `p = 1`, where a positive shape's quantile is infinite, so the
    "kill" would be an incidental `ZeroDivisionError` rather than a failed
    recovery.

    Choosing `n` and the tolerance
    ------------------------------

    The sample is a deterministic quadrature of the law, not a draw, so the
    correct estimator does not recover it exactly: `mean(Q(p_j))` at these
    positions is not the integral of `Q`, and both moments carry a bias of order
    `1 / n`. A mutated offset moves `a_1` by an amount also of order `1 / n`, so
    their ratio does not improve with `n` --- a larger sample shrinks both
    together and buys no resolution. `n = 100` is therefore chosen for scale,
    not for power: it is the "about a hundred excesses" `GPD_SHAPE_BOUNDS` is
    reasoned about in `ml.py`.

    Measured at `n = 100` over the table below, the correct estimator's worst
    error is `0.0153` in `xi` (at `xi = -0.4`) and `0.0067` in `sigma / sigma_0
    - 1`. The tolerances are twice those, rounded up to the next `0.005`:
    **`0.035` in `xi` and `0.015` relative in `sigma`.** The rule was fixed
    before the mutations below were scored against it, and no tolerance was
    moved afterwards. Under the offset `0.0` the worst row errs by `0.0545` in
    `xi` and `0.0344` in `sigma`, each more than half again over its tolerance.

    A finding: the guard is one-sided
    ---------------------------------

    **An offset moved *up* towards `0.5` is not an error this design can see
    through `xi`, and very nearly not through `sigma` either.** On an exact
    quantile design the midpoint offset `0.5` is the better quadrature, so it
    recovers the declared shape *more* closely than `0.35` does: worst `xi`
    error `0.0111` against `0.0153`. Hosking and Wallis chose `0.35` for the
    bias of the estimator over random samples, not for a deterministic grid, and
    no recovery tolerance on this design can prefer `0.35` to `0.5` in `xi`
    without being tuned to today's output. What `0.5` does move is `sigma` on the
    heaviest row, to `0.0153` relative against a tolerance of `0.015` --- so it
    fails, by `0.0003`, on one row. **That margin is recorded as a kill because
    it is one, and is not counted as resolution:** a table edit that dropped
    `xi = 0.4` would let it through. Measured on the same rule, offsets from
    `0.20` downwards and from `0.60` upwards fail with margin; `0.25` to `0.40`
    pass. The guard's honest resolution is an offset error of about `0.15`
    downwards and `0.25` upwards.

    Mutation record
    ---------------

    Run in a disposable copy under `$HOME` built from `git ls-files -z --cached
    --others --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, whole suite per run, on
    CPython 3.9.6 through the mount's `.venv/bin/python` by absolute path (the
    copy carries no `.venv`). Unmutated control green before and after; each
    target confirmed present exactly once by `grep -cF` before, and the
    replacement present and the original gone after, and restored before the
    next.

    1. **The plotting position dropped.** `_GPD_PLOTTING_OFFSET = 0.35` ->
       `0.0` in `ml.py`. **Kills this test and nothing else**, all five
       subtests, `AssertionError` each. The three bounded and near-exponential
       rows fail on `xi` (errors `0.0545`, `0.0479`, `0.0406` against `0.035`);
       the two heavy rows stay inside the `xi` tolerance (`0.0315`, `0.0145`)
       and fail on `sigma` (`0.0329`, `0.0271` against `0.015`). This is the
       mutation `FittedTailPwmTests` records as surviving; it no longer does.
    2. **The plotting position moved up.** `0.35` -> `0.5`. **Kills this test
       and nothing else, on one subtest only** --- `xi = 0.4, sigma = 0.8`,
       `AssertionError`, relative `sigma` error `0.01534` against `0.015`. See
       "the guard is one-sided" above: this is a kill by `0.0003` on the
       heaviest row, and is recorded as observed, not as resolution.
    3. **The same limb, reached through the weight.** `(1.0 - (rank -
       _GPD_PLOTTING_OFFSET) / count)` -> `(1.0 - rank / count)` in
       `ml._fit_gpd_pwm`. Kills this test and nothing else, all five subtests,
       `AssertionError`, **with errors identical to mutation 1 to the last
       digit** --- as they must be: the offset appears nowhere in the estimator
       but that weight, so the two mutations are one program.
    4. **B34's clamp mutation, re-run.** `clamped = not lower <= xi <= upper`
       -> `clamped = False`. Kills `FittedTailPwmTests` alone, one subtest ("a
       sample whose shape the clamp takes back says so"), `AssertionError`.
       **This class stays green under it**: every declared shape sits well
       inside `GPD_SHAPE_BOUNDS`, so no fit here is clamped and the flag's
       assertion never meets a `True`. The two guards hold separate things ---
       the clamp's honesty there, the `a_1` limb here.
    """

    #: The plotting positions the sample is built at: Hosking and Wallis'
    #: `(j - 0.35) / n`, declared here rather than read from `ml` --- see the
    #: class docstring.
    DESIGN_OFFSET = 0.35

    #: One hundred points. Chosen for the scale the fit will see in use, not for
    #: resolution, which does not improve with `n` on this design.
    SAMPLE_SIZE = 100

    #: Twice the correct estimator's worst measured error on this table at
    #: `SAMPLE_SIZE`, rounded up to the next `0.005`.
    SHAPE_TOLERANCE = 0.035
    RELATIVE_SCALE_TOLERANCE = 0.015

    #: `(xi, sigma)`, all inside `GPD_SHAPE_BOUNDS`: two bounded tails, one
    #: nearly exponential, two heavy. `0.01` rather than `0.0` so the sample is
    #: built by the same formula as every other row, not by the exponential
    #: limit a special case would need. The scales differ so that a defect
    #: which confused scale with a unit could not pass on all five.
    DECLARED = (
        (-0.4, 2.0),
        (-0.2, 1.5),
        (0.01, 1.0),
        (0.2, 3.0),
        (0.4, 0.8),
    )

    def _sample(self, xi, sigma):
        count = self.SAMPLE_SIZE
        return [
            sigma * ((1.0 - (j - self.DESIGN_OFFSET) / count) ** -xi - 1.0) / xi
            for j in range(1, count + 1)
        ]

    def test_the_fit_recovers_a_declared_shape_and_scale_from_its_own_quantile_function(
        self,
    ):
        """A sample built from a declared law's inverse CDF fits back to that law.

        For each declared `(xi, sigma)`, `x_j = sigma ((1 - p_j) ** -xi - 1) /
        xi` at `p_j = (j - 0.35) / n`, reversed so the estimator's sort is
        exercised. The fit must be unclamped and not the fallback --- a clamped
        `xi` near a declared one would be the bound agreeing, not the fit --- and
        must return `xi` within `SHAPE_TOLERANCE` and `sigma` within
        `RELATIVE_SCALE_TOLERANCE` of the declared values.
        """

        for xi, sigma in self.DECLARED:
            with self.subTest(xi=xi, sigma=sigma):
                fit = ml._fit_gpd_pwm(list(reversed(self._sample(xi, sigma))))
                self.assertFalse(fit.clamped)
                self.assertFalse(fit.fallback)
                self.assertLessEqual(
                    abs(fit.xi - xi),
                    self.SHAPE_TOLERANCE,
                    msg=f"fitted xi {fit.xi!r} is not the declared {xi!r}; the "
                    "estimator weights the order statistics differently from "
                    "the plotting positions the law was sampled at",
                )
                self.assertLessEqual(
                    abs(fit.sigma / sigma - 1.0),
                    self.RELATIVE_SCALE_TOLERANCE,
                    msg=f"fitted sigma {fit.sigma!r} is not the declared "
                    f"{sigma!r}",
                )


class GpdTailWiringTests(unittest.TestCase):
    """`tail="gpd"`: the fitted tail wired in above the top declared quantile.

    **The defect.** Above the law's top knot `_exceedance_from_law` returns
    exactly `0.0`, so every declared threshold is read inside the one straight
    segment from `Q(0.95)` to the largest residual the fit saw and beyond it the
    model is certain nothing happens. B34 built the estimator and B35 guarded
    it; nothing called it.

    **The anchor is the GPD survival function, written out here** from the
    recorded fit's `xi` and `sigma` --- not `ml._gpd_survival`, and not a
    committed float. A pin of the tail model's output would kill every mutation
    below and assert only that the code does what it did.

    **The join is exact, not nearly.** At the threshold the knot law returns
    `1.0 - (levels[-2] + 0.0 * ...)`, which is `1.0 - 0.95` to the bit, and
    `(1 - levels[-1]) * S(0)` is `(1.0 - 0.95) * 1.0`, the same float; a tail
    attached anywhere else puts `S` of a nonzero excess there instead.

    **The sample is checked by construction, not by count alone.** Each
    calibration row's excess is recomputed from `predict` at its feature row ---
    the row before it, at a purge of zero --- and the fit on that sample must be
    the recorded fit. A tail collected above a different threshold than the one
    it is attached at would otherwise pass parts 1 to 3: they read `xi` and
    `sigma` off the record, whatever sample produced them.

    **Three states.** `heteroscedastic_frame(1200)` at a calibration share of
    `0.6` leaves 720 calibration rows and a fitted, unclamped, non-fallback
    shape --- more than `GPD_MINIMUM_EXCESSES` excesses, with margin, so the
    `xi != 0` branch of the survival function is what is read. A 36-row frame
    at the default share leaves nine calibration rows, the conformal minimum,
    where the rank names the largest score, no target exceeds its calibrated top
    quantile, and there is **no tail to attach**: `tail` says `"gpd"`,
    `tail_fit` is `None`, and the law is the default's.

    A defect found while building it
    --------------------------------

    The fitter already had two locals named `tail` --- the index range handed
    to `_feature_index` in the conformal calibration loop and in each
    cross-conformal block --- and the new keyword was shadowed by the first of
    them: every conformal fit, default included, came back with `tail` a
    `range` and a fitted tail attached. The default's exceedance above the top
    knot was non-zero. Both locals are now `recent`. Mutation 10 puts the
    calibration loop's name back and records what sees it.

    Mutation record
    ---------------

    Run in twelve disposable copies under `$HOME`, one per mutation plus an
    unmutated control, each built from `git ls-files -z --cached --others
    --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, whole suite per run, on
    CPython 3.9.6 with numpy 2.0.2 and scikit-learn 1.6.1 through the mount's
    `.venv/bin/python` by absolute path; `repo_model` confirmed to resolve to
    the copy's `src/`. Unmutated control green before and after, zero
    `expectedFailure`. Each target was counted as an exact substring in Python
    and found exactly once, and the replacement confirmed present and the
    original gone. **Every mutation 1 to 7 and 10 killed this test and nothing
    else**, `AssertionError` in every subtest named.

    1. **The tail short-circuited** --- `if self.tail_fit is None:` -> `if
       True:` in `predict_stress`, so the law saturates as it did. Kills parts 2
       and 3: the tail model returns the knot law's `0.0375, 0.025, 0.0, 0.0`
       where the survival function gives `0.00719, 0.00119, ...`, and `0.0 not
       greater than 0.0` at the top knot. Part 1 stays green, as it must: the
       two laws agree at the join.
    2. **The `(1 - levels[-1])` scaling dropped.** Kills **part 2** alone: the
       unscaled survival `0.1439, 0.0238, ...` against `0.00719, 0.00119, ...`.
       Part 1 cannot see it --- at the threshold the knot law answers, not the
       tail --- and part 3 stays green because the unscaled survival at the top
       knot is still below `1 - levels[-1]` on this fixture.
    3. **The threshold moved to the uncalibrated top quantile**, in two places,
       because the trap has two halves:
       a. *attached* there --- `threshold = values[-2]` -> the uncalibrated
          vector's last entry in `predict_stress`. Kills **part 1**, `0.01461`
          against `0.050000000000000044` at the calibrated threshold --- the
          jump at the join --- and part 2.
       b. *collected* there --- `top = _calibrated(vector, widening)[-1]` ->
          `top = vector[-1]` in the fitter, attached at the calibrated knot.
          **Parts 1 to 5 do not see this one**, and cannot: they read `xi` and
          `sigma` off the record, whatever sample produced them, and the join
          stays exact because the tail is still attached at the reported knot.
          It is killed by the sample subtest (the recorded fit is `xi` about
          `0.103` against `0.040` on the sample recomputed from `predict`) and
          by the no-excess subtest (two excesses above the uncalibrated
          quantile, and a fallback attached where none belongs). The brief
          expected part 1 to catch it; part 1 catches the attachment half
          only, and that is the finding that put the sample subtest here.
    4. **The unknown-family refusal removed.** Part 5, `ValueError not
       raised`: `"pareto"` fitted as a GPD.
    5. **The `none` refusal removed.** Part 5, `ValueError not raised`: an
       uncalibrated fit with the tail silently absent.
    6. **The `cross_conformal` refusal removed.** Part 5, `ValueError not
       raised`: a cross-conformal fit with the tail silently absent.
    7. **The third state given a shape** --- an empty sample recorded as
       `FittedTail(xi=0.0, sigma=1.0, excesses=0, fallback=True)` rather than
       `None`. The no-excess subtest, `... is not None`.
    8. **B35's `_GPD_PLOTTING_OFFSET` 0.35 -> 0.0, re-run.** Kills
       `GpdRecoveryTests` alone, all five subtests, as B35 recorded. This test
       stays green: it reads the fit off the record and recomputes its sample
       through the same estimator, so it holds the wiring and not the
       estimator. Kill set unchanged.
    9. **B34's clamp flag, `clamped = False`, re-run.** Kills
       `FittedTailPwmTests` alone, one subtest, as B34 recorded. This fixture's
       fit is unclamped. Kill set unchanged.
    10. **The shadowing restored** --- the calibration loop's `recent` back to
        `tail`. Kills the recorded-fit subtest (`range(1198, 1199) != 'gpd'`),
        part 4 (the default's `0.0` above the top knot is gone) and the
        no-excess subtest. `ForecastInterfaceConformance::
        test_predict_stress_agrees_with_the_quantiles_predict_reports` stays
        green: it fits under `calibration="none"`, where that loop never runs.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    ROWS = 1200
    SHARE = 0.6

    def setUp(self):
        require_extra(self)

    def fit(self, frame, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
            "calibration": "conformal",
            "purge_days": 0,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(frame, self.REGRESSORS, **options)

    @staticmethod
    def survival(xi, sigma, excess):
        """The generalised Pareto survival function, from its definition."""

        if xi == 0.0:
            return math.exp(-excess / sigma)
        base = 1.0 + xi * excess / sigma
        return 0.0 if base <= 0.0 else base ** (-1.0 / xi)

    def test_above_the_top_declared_quantile_the_gpd_tail_continues_the_law_and_the_default_still_saturates(
        self,
    ):
        """Join, shape, no zero, default unmoved, the sample, three refusals.

        One criterion: a tail that joined the law but was never read above it,
        or read above it but moved the default, or was fitted to rows the
        estimators saw, is each the defect in another form.
        """

        rows = heteroscedastic_frame(self.ROWS)
        feature = rows[-1]
        tailed = self.fit(rows, calibration_share=self.SHARE, tail="gpd")
        default = self.fit(rows, calibration_share=self.SHARE)
        fit = tailed.tail_fit
        top_level = QUANTILE_LEVELS[-1]
        mass = 1.0 - top_level

        with self.subTest("the fit is recorded, and is a fitted shape"):
            self.assertEqual(tailed.tail, "gpd")
            self.assertIsNone(default.tail)
            self.assertIsNone(default.tail_fit)
            self.assertIsNotNone(fit)
            self.assertFalse(fit.fallback)
            self.assertFalse(fit.clamped)
            self.assertGreater(fit.xi, 0.0)

        values, levels = default.law_knots(feature)
        threshold = values[-2]
        high = values[-1]
        self.assertEqual(threshold, default.predict(feature)[-1])
        self.assertEqual(tailed.law_knots(feature), (values, levels))
        above = (
            threshold + 0.25 * (high - threshold),
            threshold + 0.5 * (high - threshold),
            high,
            high + 10.0,
        )
        taus = (threshold,) + above

        with self.subTest("1. the join"):
            self.assertEqual(tailed.predict_stress(feature, (threshold,)), (mass,))
            self.assertEqual(default.predict_stress(feature, (threshold,)), (mass,))

        with self.subTest("2. the shape"):
            self.assertEqual(
                tailed.predict_stress(feature, above),
                tuple(
                    mass * self.survival(fit.xi, fit.sigma, tau - threshold)
                    for tau in above
                ),
            )

        with self.subTest("3. the zero is gone"):
            for tau in (high, high + 10.0):
                (tail_value,) = tailed.predict_stress(feature, (tau,))
                self.assertGreater(tail_value, 0.0)
                self.assertLess(tail_value, mass)

        with self.subTest("4. the default did not move"):
            expected = []
            for tau in taus:
                if tau >= high:
                    expected.append(0.0)
                else:
                    weight = (tau - threshold) / (high - threshold)
                    expected.append(
                        1.0 - (levels[-2] + weight * (levels[-1] - levels[-2]))
                    )
            self.assertEqual(default.predict_stress(feature, taus), tuple(expected))
            self.assertEqual(default.predict_stress(feature, (high,)), (0.0,))

        with self.subTest("the sample is the calibration rows' excesses above the reported top"):
            first = len(rows) - int(Fraction(repr(self.SHARE)) * len(rows))
            excesses = []
            for index in range(first, len(rows)):
                top = tailed.predict(rows[index - 1])[-1]
                if rows[index].spread_bps > top:
                    excesses.append(rows[index].spread_bps - top)
            self.assertGreater(len(excesses), ml.GPD_MINIMUM_EXCESSES)
            self.assertEqual(fit, ml._fit_gpd_pwm(excesses))

        with self.subTest("no excesses: no tail attached, and the default law"):
            small = heteroscedastic_frame(36)
            bare = self.fit(small, tail="gpd")
            plain = self.fit(small)
            self.assertEqual(bare.tail, "gpd")
            self.assertIsNone(bare.tail_fit)
            knots, _ = plain.law_knots(small[-1])
            probes = (knots[-2], 0.5 * (knots[-2] + knots[-1]), knots[-1], knots[-1] + 10.0)
            self.assertEqual(
                bare.predict_stress(small[-1], probes),
                plain.predict_stress(small[-1], probes),
            )

        with self.subTest("5. refusals"):
            with self.assertRaises(ValueError) as caught:
                self.fit(rows, calibration_share=self.SHARE, tail="pareto")
            self.assertIn("unknown tail 'pareto'", str(caught.exception))
            self.assertIn("gpd", str(caught.exception))
            with self.assertRaises(ValueError) as caught:
                ml.fit_gradient_boosted_quantiles(
                    rows,
                    self.REGRESSORS,
                    min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
                    tail="gpd",
                )
            self.assertIn("in-sample tail", str(caught.exception))
            with self.assertRaises(ValueError) as caught:
                self.fit(rows, calibration="cross_conformal", tail="gpd")
            self.assertIn("not wired for calibration 'cross_conformal'", str(caught.exception))


class TailDeclarationTests(unittest.TestCase):
    """`tail` in `model_settings`, and `--tail` on the command line (B37).

    **The defect.** After B36 a fit with `tail="gpd"` and a fit without one
    declared the same mapping, and nothing on the command line could ask for
    the tail: a record built from a tailed model was indistinguishable from one
    built without, and no record could be built from one at all.

    **The trap is part 2.** The key named unconditionally -- `tail: None` on
    every gbm fit -- changes the declaration of every published gbm record,
    which is re-scored by a human and never rewritten inside a block. So part 2
    asserts membership, not a `None` value, and asserts the whole untailed
    mapping is the tailed one with `tail` taken out.

    **What the declaration is not.** `tail` is what the command declared. What
    each fold's tail *fit* found -- `xi`, `sigma`, `excesses` -- is not in the
    declaration, by design, and nothing here asserts it is. Since B38 a
    `backtest` record carries it per fold under `folds.tail`;
    `TailAccountTests` holds that.

    Mutation record
    ---------------

    Run in nine disposable copies under `$HOME`, one per mutation plus an
    unmutated control, each built from `git ls-files -z --cached --others
    --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, whole suite per run, on
    CPython 3.9.6 with numpy 2.0.2 and scikit-learn 1.6.1 through the mount's
    `.venv/bin/python` by absolute path; `repo_model` confirmed to resolve to
    the copy's `src/`. Unmutated control green before and after, zero
    `expectedFailure`. Each target was counted as an exact substring in Python
    and found exactly once, and the original confirmed gone.

    1. **The key dropped** --- the `if self.tail is not None:` guard and its
       assignment deleted from `model_settings`. Kills part 1 (`AssertionError:
       'tail' not found`), part 2 (the tailed mapping equals the untailed one
       with no `tail` added, `AssertionError`) and part 3 (`KeyError: 'tail'`
       on the CLI-built fit). Nothing else in the suite.
    2. **The key made unconditional** --- `settings["tail"] = self.tail`
       outside the guard. Kills part 2 (`AssertionError: 'tail' unexpectedly
       found`) and, `AssertionError` each, the declaration subtests of
       `GradientBoostedConformalCalibrationTests`,
       `GradientBoostedCrossConformalTests`, `GradientBoostedLaggedSpreadTests`,
       `GradientBoostedGarchFeatureTests` and `GradientBoostedArxFeatureTests`:
       every sibling's declaration grows `'tail': None`. **It does not redden
       `tests/test_generated_results.py`**, and cannot: that module renders
       the README and notebook from the committed `docs/runs/` records and
       refits nothing, so a declaration that would change on a re-run is
       invisible to it until a human re-scores. The published-record
       consequence is held here and by the five sibling subtests, not there.
    3. **The flag not passed through** --- `settings.update(_tail(...))` ->
       `_tail(...)` in `_select_fitter`, so the refusals still run. Kills part
       3 alone, `AssertionError` on `fitter.keywords` missing `tail`.
    4. **Each refusal removed in turn**, the condition made `if False:`:
       a. *the model refusal* (`if not takes_tail:`). Kills part 4, but as
          `AssertionError: "--tail gpd was given, but --model arx" does not
          match`, **not** `... not raised`: `--model arx` takes no
          calibration, so the next refusal, calibration `none`, still stops the
          run with the wrong reason. The kill is the message check.
       b. *calibration `none`*. Part 4, `AssertionError: SplitError not raised`.
       c. *calibration `cross_conformal`*. Part 4, `SplitError not raised`.
       d. *the unknown family* (`if tail not in ml.TAIL_FAMILIES:`). Part 4,
          `SplitError not raised`.
       Each killed this test and nothing else.
    5. **B36's short circuit re-run** --- `if self.tail_fit is None:` -> `if
       True:` in `predict_stress`. Kills `GpdTailWiringTests` parts 2 and 3
       alone (`Tuples differ`, `0.0 not greater than 0.0`), as B36 recorded.
       This test stays green: it reads the declaration and the flag, not the
       law. Kill set unchanged; the two classes still divide the tail.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")

    def setUp(self):
        require_extra(self)

    def fit(self, frame, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
            "calibration": "conformal",
            "purge_days": 0,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(frame, self.REGRESSORS, **options)

    def parse(self, *argv):
        common = ["--registry", "registry.json", "--decision-time", DECISION_TIME]
        command, *rest = argv
        return cli.build_parser().parse_args(
            [command, "panel.csv", *common, "--report", "r.json", *rest]
        )

    def test_a_tail_run_declares_its_tail_and_a_run_without_one_declares_exactly_what_it_declared_before(
        self,
    ):
        """Named when set, absent when not, reachable from the flag, refused early."""

        rows = heteroscedastic_frame(1200)
        tailed = self.fit(rows, calibration_share=0.6, tail="gpd")
        plain = self.fit(rows, calibration_share=0.6)
        small = heteroscedastic_frame(36)
        gbm = ["--feature", "on_rrp", "--feature", "sofr_volume", "--feature", "spread_bps",
               "--model", "gbm"]

        with self.subTest("1. named when set"):
            self.assertIsNotNone(tailed.tail_fit)
            self.assertIn("tail", tailed.model_settings)
            self.assertEqual(tailed.model_settings["tail"], "gpd")
            self.assertEqual(baseline._model_settings(tailed)["tail"], "gpd")

        with self.subTest("2. absent when not, and the rest unchanged"):
            self.assertIsNone(plain.tail)
            self.assertNotIn("tail", plain.model_settings)
            self.assertNotIn("tail", baseline._model_settings(plain))
            expected = {
                "calibration": plain.calibration,
                "calibration_share": plain.calibration_share,
            }
            self.assertEqual(dict(plain.model_settings), expected)
            self.assertEqual(dict(tailed.model_settings), {**expected, "tail": "gpd"})
            # The model every published gbm record was produced with.
            uncalibrated = self.fit(small, calibration="none")
            self.assertNotIn("tail", uncalibrated.model_settings)
            self.assertEqual(dict(baseline._model_settings(uncalibrated)), {})

        with self.subTest("3. the flag reaches the fitter"):
            backtest = self.parse("backtest", *gbm, "--calibration", "conformal", "--tail", "gpd")
            _, fitter = cli_eval._select_fitter(backtest)
            self.assertEqual(
                fitter.keywords,
                {"regressors": ("on_rrp", "sofr_volume"), "calibration": "conformal",
                 "tail": "gpd"},
            )
            fitted = fitter(small, minimum_history=20,
                            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF, purge_days=0)
            self.assertEqual(fitted.tail, "gpd")
            self.assertEqual(dict(fitted.model_settings)["tail"], "gpd")

            compare = self.parse(
                "compare",
                "--model-a", "gbm", "--feature-a", "on_rrp", "--feature-a", "spread_bps",
                "--calibration-a", "conformal", "--tail-a", "gpd",
                "--model-b", "gbm", "--feature-b", "on_rrp", "--feature-b", "spread_bps",
                "--calibration-b", "conformal",
            )
            _, fit_a = cli_eval._select_fitter(cli_eval._side(compare, "a"), side="-a")
            _, fit_b = cli_eval._select_fitter(cli_eval._side(compare, "b"), side="-b")
            self.assertEqual(fit_a.keywords.get("tail"), "gpd")
            self.assertNotIn("tail", fit_b.keywords)
            compare = self.parse(
                "compare",
                "--model-a", "persistence", "--feature-a", "spread_bps",
                "--model-b", "gbm", "--feature-b", "on_rrp", "--feature-b", "spread_bps",
                "--calibration-b", "conformal", "--tail-b", "gpd",
            )
            _, fit_b = cli_eval._select_fitter(cli_eval._side(compare, "b"), side="-b")
            self.assertEqual(fit_b.keywords.get("tail"), "gpd")

        with self.subTest("4. refusals, at selection"):
            arx = self.parse("backtest", "--feature", "on_rrp", "--feature", "spread_bps",
                             "--model", "arx", "--tail", "gpd")
            with self.assertRaisesRegex(SplitError, r"--tail gpd was given, but --model arx"):
                cli_eval._select_fitter(arx)
            compare = self.parse(
                "compare",
                "--model-a", "persistence", "--feature-a", "spread_bps", "--tail-a", "gpd",
                "--model-b", "gbm", "--feature-b", "on_rrp", "--feature-b", "spread_bps",
            )
            with self.assertRaisesRegex(
                SplitError, r"--tail-a gpd was given, but --model-a persistence"
            ):
                cli_eval._select_fitter(cli_eval._side(compare, "a"), side="-a")
            for calibration in ((), ("--calibration", "none")):
                with self.assertRaises(SplitError) as caught:
                    cli_eval._select_fitter(self.parse("backtest", *gbm, *calibration,
                                                       "--tail", "gpd"))
                self.assertIn("with calibration none", str(caught.exception))
                self.assertIn("only by --calibration conformal", str(caught.exception))
            with self.assertRaises(SplitError) as caught:
                cli_eval._select_fitter(
                    self.parse("backtest", *gbm, "--calibration", "cross_conformal",
                               "--tail", "gpd")
                )
            self.assertIn("cross_conformal, where the tail is not wired", str(caught.exception))
            self.assertIn("only by --calibration conformal", str(caught.exception))
            with self.assertRaises(SplitError) as caught:
                cli_eval._select_fitter(
                    self.parse("backtest", *gbm, "--calibration", "conformal",
                               "--tail", "pareto")
                )
            self.assertIn("unknown --tail 'pareto'", str(caught.exception))
            self.assertIn("gpd", str(caught.exception))


class TailAccountTests(unittest.TestCase):
    """Each fold's tail on a `backtest` record, and nothing without one (B38).

    **The defect.** After B37 a record declared `tail: gpd` and said nothing
    about what the tail did. A rolling backtest refits at every origin, so one
    field cannot hold the answer, and the answer differs by fold in the way
    that matters: an expanding window's early folds have too few excesses to
    fit a shape, and a metric that moved cannot be read against a tail that
    was never fitted unless the record says which folds had one.

    **The trap is part 2.** The last fold's tail, or `report.model`'s, recorded
    as the run's. On this fixture the last fold has a fitted shape and the
    first has no excesses, so a single answer copied across the folds cannot
    show all three states.

    **How each state is forced.** `frame` is a weekday panel whose spread is
    `10 +/- 1` bp, with two kinds of row added. From `DIPS_FROM` every sixth
    row is a dip to `-40` bp: always among the calibration rows (the fit rows
    end before it at every fold), and more of them than the conformal rank
    leaves above the widening, so the widening is a dip's score and no
    ordinary row exceeds its calibrated top quantile. From the first scored
    row on, every row is a spike far above that top quantile, and each fold's
    training frame holds one more of them than the fold before. So:

    * **no excesses** -- the first fold, whose frame holds no spike;
    * **fallback** -- the next folds, one excess per spike, up to one short of
      `ml.GPD_MINIMUM_EXCESSES`;
    * **fitted** -- the rest. The first few are **clamped** (few excesses
      whose spread is small against the dip-set widening), and once the
      spikes begin to set the widening themselves the later ones are not.
      Both are asserted, because a clamped shape is not a fitted one and the
      record must say so.

    The states are asserted against each fold's own fitted model, captured as
    the fold loop fitted it, and spelled here from that model's `tail_fit` ---
    not pinned floats. The fold loop's fit count is asserted too: an account
    read off a second fit of the same frame would have the same floats and
    would still be a second fit.

    **Part 3's comparison is against the tailed run on this base.** The tail
    changes `predict_stress` above the top knot and nothing `backtest` scores,
    so the untailed record is the tailed record with `declaration.tail` and
    `folds.tail` taken out, key for key and value for value.

    Mutation record
    ---------------

    Run in five disposable copies under `$HOME`, one per mutation plus an
    unmutated control, each built from `git ls-files -z --cached --others
    --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, whole suite per run, on
    CPython 3.9.6 with numpy 2.0.2 and scikit-learn 1.6.1 through the mount's
    `.venv/bin/python` by absolute path; `repo_model` confirmed to resolve to
    the copy's `src/`. Unmutated control green before and after, zero
    `expectedFailure`. Each target was counted as an exact substring in Python
    and found exactly once. Every failure is `AssertionError`.

    1. **The final fold's answer for every fold** --- the report's tuple built
       as `tuple(_tail_account(model) for _ in tail_accounts)`, `model` being
       the last fold's. Kills **part 1** (the first fold's `fitted` account
       against its own model's `no_excesses`) and **part 2** (`'fitted' !=
       'no_excesses'` on the first entry). This test and nothing else.
    2. **The account made unconditional** --- `if self.tail is None: return
       None` deleted from `ml.FittedGradientBoostedQuantiles.tail_account`, so
       an untailed fit reports `no_excesses` and every gbm `backtest` record
       grows `folds.tail`. Kills **part 3** (`plain_report.tail_accounts` is a
       tuple of `no_excesses`, not `None`). This test and nothing else: **no
       sibling declaration subtest goes red**, and none can --- they read
       `model_settings`, which this does not touch, and no other test builds a
       gbm `backtest` document and reads its `folds` keys. B37's five sibling
       subtests guard the declaration; the fold account's absence is guarded
       here alone.
    3. **A fallback read as a fitted shape of `xi = 0.0`** --- `elif
       fit.fallback:` -> `elif False:` in `tail_account`. Kills **part 1**
       (`{'state': 'fitted', 'xi': 0.0, ...} != {'state': 'fallback', ...}`)
       and **part 2** (`'fallback'` missing from the recorded states). This
       test and nothing else.
    4. **The account read off a refit** --- the fold loop appends
       `_tail_account(_fit_at_origin(fitter, ...))` on the same training frame
       instead of the scored model's. The fit is deterministic, so every float
       is the scored model's and parts 1 to 3 would pass on values alone;
       what kills it is **part 1**'s fit count, `52 != 26`. Also
       `GradientBoostedConformalCalibrationTests::test_the_calibrated_band_covers_its_nominal_probability_out_of_sample`
       (`16 != 8`) and
       `GradientBoostedCrossConformalTests::test_the_cross_conformal_band_covers_its_nominal_probability_and_keeps_the_full_fit`
       (`8 != 4`), which count fits per fold for their own reasons. Inside
       the model no refit is expressible: the excesses are not kept, so
       `tail_account` can only read `tail_fit`.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    PURGE = 6
    MINIMUM_HISTORY = 380
    DIPS_FROM = 170
    SPIKES = 24
    SHARE = 0.6

    def setUp(self):
        require_extra(self)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.registry_path = declared_registry_file(
            self.directory.name, purge=self.PURGE, features=self.FEATURES
        )
        self.registry = json.loads(self.registry_path.read_text(encoding="utf-8"))

    def frame(self):
        """The panel the docstring describes, and a file for its digest."""

        rng = random.Random(20260912)
        count = self.MINIMUM_HISTORY + self.PURGE + self.SPIKES
        rows = []
        for index, when in enumerate(business_days(date(2020, 1, 1), count)):
            spread = 10.0 + 2.0 * (rng.random() - 0.5)
            if index >= self.MINIMUM_HISTORY:
                spread = 150.0 + 60.0 * -math.log(1.0 - rng.random())
            elif index >= self.DIPS_FROM and index % 6 == 0:
                spread = -40.0
            rows.append(
                DailyObservation(
                    when,
                    {
                        "sofr": 4.30 + spread / 100.0,
                        "iorb": 4.30,
                        "on_rrp": 100.0 * rng.random(),
                        "sofr_volume": 2000.0 + 400.0 * rng.random(),
                    },
                )
            )
        return rows

    def backtest(self, panel, **settings):
        """The fold loop over `panel`, its record, and every model it fitted."""

        fits = []

        def fitter(train_frame, minimum_history, purge_days):
            model = ml.fit_gradient_boosted_quantiles(
                train_frame,
                self.REGRESSORS,
                minimum_history=minimum_history,
                min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
                calibration="conformal",
                calibration_share=self.SHARE,
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
        panel_path = self.registry_path.with_name("panel.csv")
        panel_path.write_text("date,sofr,iorb\n", encoding="utf-8")
        document = baseline.backtest_document(
            report,
            panel_path=panel_path,
            registry_path=self.registry_path,
            model="gbm",
        )
        return report, document, fits

    @staticmethod
    def expected(fit):
        """What a record should say of one fold, spelled from its `tail_fit`."""

        if fit is None:
            return {"state": "no_excesses", "excesses": 0}
        if fit.fallback:
            return {"state": "fallback", "sigma": fit.sigma, "excesses": fit.excesses}
        return {
            "state": "fitted",
            "xi": fit.xi,
            "sigma": fit.sigma,
            "excesses": fit.excesses,
            "clamped": fit.clamped,
        }

    def test_a_tail_run_records_what_its_tail_was_at_every_fold_and_a_run_without_one_records_nothing(
        self,
    ):
        """Per fold, off the fold's own model; three states apart; absent without a tail."""

        panel = self.frame()
        report, document, fits = self.backtest(panel, tail="gpd")
        plain_report, plain_document, _ = self.backtest(panel)
        entries = document["folds"]["tail"]

        with self.subTest("1. every fold, off the model that fold scored"):
            self.assertEqual(len(fits), len(report.folds))
            self.assertEqual(len(entries), len(report.folds))
            for fold, model, account, entry in zip(
                report.folds, fits, report.tail_accounts, entries
            ):
                expected = self.expected(model.tail_fit)
                self.assertEqual(dict(account), expected, msg=str(fold.scored_date))
                self.assertEqual(
                    entry,
                    {"scored_date": fold.scored_date.isoformat(), **expected},
                )

        with self.subTest("2. the three states are told apart"):
            states = [entry["state"] for entry in entries]
            self.assertEqual(states[0], "no_excesses")
            self.assertEqual(states[-1], "fitted")
            self.assertEqual(set(states), set(ml.TAIL_STATES))
            fallbacks = [entry for entry in entries if entry["state"] == "fallback"]
            self.assertEqual(
                sorted(entry["excesses"] for entry in fallbacks),
                list(range(1, ml.GPD_MINIMUM_EXCESSES)),
            )
            for entry in fallbacks:
                self.assertNotIn("xi", entry)
            fitted = [entry for entry in entries if entry["state"] == "fitted"]
            self.assertTrue(all(e["excesses"] >= ml.GPD_MINIMUM_EXCESSES for e in fitted))
            self.assertEqual({entry["clamped"] for entry in fitted}, {True, False})

        with self.subTest("3. without a tail, nothing, and the rest unchanged"):
            self.assertIsNone(plain_report.tail_accounts)
            self.assertNotIn("tail", plain_document["folds"])
            self.assertEqual(set(plain_document["folds"]), {"count", "first", "last"})
            self.assertNotIn("tail", plain_document["declaration"])
            stripped = json.loads(json.dumps(document))
            del stripped["declaration"]["tail"]
            del stripped["folds"]["tail"]
            self.assertEqual(json.loads(json.dumps(plain_document)), stripped)


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
