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
* `GradientBoostedAsymmetricConformalTests` -- `calibration=
  "conformal_asymmetric"`: `conformal`'s split with the two edges moved by
  their own score sets at their own ranks, `conformal`'s band and law at equal
  widenings, and the refusals.
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
* `GradientBoostedCrossAsymmetricConformalTests` -- `calibration=
  "cross_conformal_asymmetric"` (B54): `cross_conformal`'s excluding models
  with each CV+ edge taken off its own side's signed scores at its own side's
  exact rank, the full fit's interior, and the refusals.
* `ScaledCrossConformalTests` -- `calibration="cross_conformal_scaled"`
  (B-SCALED): per-regime coverage on a regime-switching fixture where
  `cross_conformal` over-covers the calm regime and under-covers the stressed
  one, a scale that reads nothing after its row's feature row, the floor on a
  flat stretch, the scaled CV+ band rebuilt, `cross_conformal` unchanged, and
  the refusals.
* `PartialCrossConformalTests` -- `calibration="cross_conformal_partial"`
  (B-PARTIAL): `cross_conformal`'s score over the trailing scale to the power
  one half, on the fit's own edges; per-regime misses between
  `cross_conformal`'s and `cross_conformal_scaled`'s on a fixture whose base
  band tracks the regime, `cross_conformal`'s band exactly at exponent zero, no
  leak, a reference scale that cancels, the other two unchanged, and the
  refusals. Its docstring records why B-SCALED's own fixture cannot show the
  interpolation.
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
* `GpdCrossConformalSampleTests` -- B53: the tail stays refused under
  `cross_conformal`, and the reason holds on the fit: the CV+ edge a tail would
  be attached at reads, at every held-out row, excluding models fitted on that
  row.
* `TailShapeFloorTests` -- #63: a negative shape is floored at zero, the
  exponential with the sample's mean excess, recorded as `floored` with the
  raw estimate; the upper clamp is kept. Replaces B44's
  `TailLowerBoundRefusalTests`. Needs no `require_extra`.
* `ExceedanceTailFloorTests` -- #63 end to end: a floored fold's exceedance
  curve is positive at every tau, far above the top knot included.
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

**Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn 1.9.1,
`OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`, `REPO_MODEL_REQUIRE_ML=1`, the
killing test run alone in a disposable copy, control green before and after, each
mutation confirmed applied by diff and reverted). Mutations 1, 3 and 4 each killed
again, on the tests named above, `AssertionError`; mutation 1 still on 20
`crossing_frame` rows. 2 and 5 were not re-run: they are recorded survivors.
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import functools
import importlib.util
import io
import json
import math
import os
import random
import sys
import tempfile
import unittest
from datetime import date, time, timedelta
from fractions import Fraction
from pathlib import Path
from unittest import mock

from repo_model import baseline, cli, cli_eval, ml, recalibration
from repo_model.contract import QUANTILE_LEVELS
from repo_model.data import DailyObservation, load_daily_panel, load_stress_thresholds
from repo_model.contract import event_window_digest
from repo_model.event_eval import (
    EventWindow,
    config_digest,
    evaluate_event_window,
    read_journal,
)
from repo_model.metrics import crps_from_quantiles
from repo_model.asof import StaleReadError
from repo_model.splits import LookAheadError, SplitError

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
from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)
from lockbox_support import PRE_OPENING_LOCKBOX

#: The variable a job that exists to exercise the extra sets. See the module
#: docstring: it is the only way this process can tell "no extra installed, and
#: that is fine" from "no extra installed, and that is the bug".
def gap_rule(days):
    """The as-of rule under every source declared `record_date` + `days`, 00:00.

    What a calibration test hands a fitter where it used to hand
    `purge_days=days`. At a 16:00 decision a row dated `d` is observable from
    midnight on `d + days`, so on a gapless calendar the held-out row `i`
    reads row `i - days - 1` and the fit rows end there -- exactly the rows a
    purge of `days` selected; `days=0` is the zero gap. On a weekday calendar
    the rule counts from the decision day, the panel day before the row,
    where the purge counted from the row itself.
    """

    from repo_model.asof import InformationRule
    from repo_model.contract import FEATURE_FIELDS

    sources = {source for pairs in FEATURE_FIELDS.values() for source, _ in pairs}
    registry = {
        source: {
            "release_lag": {
                "basis": "record_date",
                "unit": "calendar_days",
                "days": days,
                "available_time": "00:00",
                "timezone": "America/New_York",
            }
        }
        for source in sources
    }
    return InformationRule(registry, ("spread_bps",), decision_time=time(16, 0))


REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"


#: Set by CI's ml job on pull requests. A subtest marked with `skip_if_fast`
#: is skipped then, and runs everywhere else: locally, on every push to `main`
#: and on the weekly schedule, where the ml job runs the whole suite
#: (directive 05, "Do 4": a test that must stay slow runs only there).
SKIP_SLOW = "REPO_MODEL_SKIP_SLOW"


def skip_if_fast(case: unittest.TestCase, why: str) -> None:
    """Skip a slow subtest when the job declared it wants the fast set only.

    Only for a subtest whose cost is a sweep of refits and whose property is
    not a leakage, availability or staleness guard: those stay in every run.
    """

    if os.environ.get(SKIP_SLOW):
        case.skipTest(f"slow ({why}); runs on pushes to main and the weekly schedule")


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

#: Boosting iterations per level fit in the fold-loop tests that call
#: `fewer_boosting_iterations`. scikit-learn's default is 100.
FIXTURE_MAX_ITER = 10


def fewer_boosting_iterations(case: unittest.TestCase, max_iter=FIXTURE_MAX_ITER):
    """Fit every level with `max_iter` boosting iterations for the rest of `case`.

    For the classes that refit a gradient-boosted model at every fold of a
    rolling loop and assert what the loop *did* with each fit: which rows it
    read, which fit a record's fold came from, how a calibration was ranked,
    what state a tail was in. None of those depends on how far the boosting
    ran, and each fit's cost does, almost linearly at fixture size, where the
    per-iteration overhead dominates the rows. Before this, those classes were
    most of the ML job's wall time (#29).

    Patched at `ml._estimator_class`, the seam every fit goes through, with
    the real class and every other argument unchanged. Every fit a test in
    `case` makes, including a refit it compares against, uses the same
    estimator. A test whose property depends on the fit converging does not
    call this.
    """

    estimator = functools.partial(ml._estimator_class(), max_iter=max_iter)
    patcher = mock.patch.object(ml, "_estimator_class", return_value=estimator)
    patcher.start()
    case.addCleanup(patcher.stop)


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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All thirteen killed again, on the subtests named above. Where the
    record predates the as-of rule, its equivalent was applied: 4 as `fit_rows =
    rows[:first]` (the refusal now arrives as a `ValueError` naming the missing
    as-of read, since `_feature_index` is gone); 5 as `_fit_at_origin` withholding
    `information=`, a `TypeError` naming `information`; 7f as the share branch's
    `_require_information` call removed, now an `AttributeError` on `None.anchor`
    rather than the recorded `TypeError`. Figures moved with the fitter: mutation
    3's coverage is 0.579.
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
            calibrated = self.fit(train, calibration="conformal", information=gap_rule(0))
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

            def calibrating(train_frame, minimum_history, information):
                model = self.fit(
                    train_frame,
                    minimum_history=minimum_history,
                    calibration="conformal",
                    information=information,
                )
                fits.append((train_frame, information, model))
                return model

            report = baseline.rolling_persistence_backtest(
                panel,
                features=self.FEATURES,
                registry=registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                minimum_history=44,
                fit_model=calibrating,
            )
            self.assertEqual(len(fits), len(report.folds))
            for fold, (frame, information, model) in zip(report.folds, fits):
                with self.subTest(fold=fold.scored_date.isoformat()):
                    # The run's own rule, handed over by the fold loop.
                    self.assertEqual(information.features, self.FEATURES)
                    self.assertEqual(model.calibration_end, frame[-1].date)
                    self.assertLess(model.calibration_end, fold.scored_date)
                    self.assertEqual(
                        sum(row.date >= model.calibration_start for row in frame),
                        int(ml.DEFAULT_CALIBRATION_SHARE * len(frame)),
                        msg="the calibration rows are not the frame's most recent share",
                    )
                    # The fit rows end at the first calibration row's anchor:
                    # the last label observable at its decision, which is not
                    # the row before it.
                    dates = [row.date for row in frame]
                    first = dates.index(model.calibration_start)
                    self.assertEqual(
                        model.fit_end, dates[information.anchor(dates, first)]
                    )
                    self.assertLess(
                        model.fit_end,
                        dates[first - 1],
                        msg=(
                            f"the last fit row {model.fit_end} was not yet "
                            f"observable when the calibration rows open on "
                            f"{model.calibration_start}"
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
                self.fit(rows[:35], calibration="conformal", information=gap_rule(0))
            # And nine is enough: the refusal sits at the edge, not above it.
            self.assertEqual(
                self.fit(rows[:36], calibration="conformal", information=gap_rule(0)).calibration_start,
                rows[27].date,
            )

        with self.subTest("refusal: a share outside (0, 1)"):
            for share in (0.0, 1.0, -0.25, 1.25):
                with self.assertRaisesRegex(ValueError, r"strictly inside \(0, 1\)"):
                    self.fit(
                        train,
                        calibration="conformal",
                        calibration_share=share,
                        information=gap_rule(0),
                    )

        with self.subTest("refusal: an unknown calibration"):
            with self.assertRaisesRegex(ValueError, r"unknown calibration 'isotonic'"):
                self.fit(rows[:36], calibration="isotonic", information=gap_rule(0))

        with self.subTest("refusal: a share given to calibration none"):
            with self.assertRaisesRegex(ValueError, r"'none' holds no rows out"):
                self.fit(rows[:36], calibration_share=0.25)

        with self.subTest("refusal: conformal with no gap"):
            with self.assertRaisesRegex(SplitError, r"needs the run's as-of rule"):
                self.fit(rows[:36], calibration="conformal")

        with self.subTest("refusal: a gap that leaves nothing to fit"):
            with self.assertRaisesRegex(ValueError, r"leaves 0 fit row\(s\) of 40"):
                self.fit(rows[:40], calibration="conformal", information=gap_rule(40))

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


class GradientBoostedAsymmetricConformalTests(unittest.TestCase):
    """`calibration="conformal_asymmetric"`: B51's acceptance criterion and its mutation target.

    **The question.** `cross_conformal` keeps the full fit *and* takes its two
    edges from separate order statistics. Its point forecast is bit-identical
    to `none`'s, so the point half of what it changed is the fit. Its coverage
    half is not attributed: 2022-23 misses below fall from 20.3% under
    `conformal` to 3.8% under `cross_conformal`, and that could be either. This
    calibration keeps `conformal`'s split exactly and separates only the score
    sets, so a scored run of it answers which.

    **Corrected by B54: it does not.** `cross_conformal`'s two order statistics
    are over one pooled score at the band's rate -- where every excluding model
    agrees at `x` its edges are `conformal`'s pooled widening exactly -- so it
    never separated the score sets, and the drop in misses below was its fit's
    alone. This class stays right about what `conformal_asymmetric` *is*; the
    premise above is what was wrong. See the module docstring of
    `repo_model.ml`, "The calibrations, taken apart".

    **What this test asserts, and what it cannot.** That the two edges move by
    the two score sets' own order statistics, at each side's own rank,
    recomputed here from the calibration rows; that equal widenings give
    `conformal`'s band and law bit for bit; and the refusals. It asserts no
    coverage figure: the question is about 2022-23 on the funding panel, which
    no fixture here is, and a fixture coverage figure would answer a question
    nobody asked.

    **Not `conformal`'s figure when the score sets coincide.** The brief asked
    for a reduction to current behaviour when the two score sets do not differ.
    What reduces is the construction -- `(w, w)` moves the band exactly as
    `_calibrated(vector, w)` does -- and not the number: the per-side rank is
    `ceil(0.95 (n + 1))`, `conformal`'s is `ceil(0.90 (n + 1))`, and a
    calibration that reproduced `conformal`'s widening from identical score
    sets would be applying the one-sided rank twice and claiming `1 - 2 alpha`.
    See the module docstring of `repo_model.ml`. For the same reason the floor
    is nineteen calibration rows, not nine.

    Mutation record (B51)
    ---------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B` (the worktree's `.venv`: CPython 3.9.6, numpy 2.0.2,
    scikit-learn 1.6.1), `PYTHONPATH=src:tests` (checked to resolve to the
    copy's `src/` before every run), `REPO_MODEL_REQUIRE_ML=1`. Each mutation
    was applied by exact-string replacement whose anchor was found exactly once
    and confirmed gone, then restored before the next; the file was checked
    byte-identical to the original at the end. **Scored against this class,
    not the whole suite**: the suite runs about seventeen minutes in one
    process, and every mutation touches only code the new name reaches.
    Unmutated control green before and after. **Each mutation failed exactly
    one subtest, its own.**

      * **Clause 1, the score sets pooled back into one** -- the upper score
        set built as `Q_lo - y`. `the edges move by different amounts, off
        separate score sets`, `AssertionError`: `(2.853, 2.853) != (2.853,
        1.490)`.
      * **Clause 1, `conformal`'s rank applied to each side** --
        `_band_probability(levels)` for both side probabilities in
        `_asymmetric_widenings`. The same subtest, `AssertionError`: `(1.683,
        0.700) != (2.853, 1.490)`. This is the one-sided-rank-twice band the
        module docstring refuses to claim, and it is visibly narrower.
      * **Clause 2, the edges moved but the tail knots not** -- `_reported`
        returning `0.0, 0.0` for how far the edges moved. `equal widenings are
        conformal's band and law, bit for bit`, `AssertionError` on
        `law_knots`: the lower tail knot at 1.985 against `conformal`'s -0.659.
        `predict` alone would not have seen it.
      * **Refusal, the neighbour rule bypassed** -- the outer levels set
        straight to `Q_lo - down` and `Q_hi + up` without `_banded`. `a
        negative widening stops each outer level at its neighbour`,
        `AssertionError`: the lower level at 17.381, above its neighbour at
        7.371.
      * **Refusal, `conformal`'s nine-row floor used for the new name** --
        `_minimum_calibration_rows(grid)` in place of
        `_minimum_asymmetric_calibration_rows(grid)`. `refusal: fewer
        calibration rows than either side's rank needs`, `IndexError`: an
        error, not a failure -- at eighteen rows the per-side rank names the
        nineteenth score, which does not exist.
      * **Refusal, the tail accepted** -- the `conformal_asymmetric` tail
        refusal made unreachable. `refusal: a tail`, `AssertionError:
        ValueError not raised`.
      * **The declaration drops the name** -- `model_settings` back to
        `== "conformal"`. `the declaration names the calibration and its
        share`, `AssertionError: {} != {'calibration': 'conformal_asymmetric',
        'calibration_share': 0.25}`: a scored record would have declared the
        uncalibrated model.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All seven killed again, each on its own subtest, `AssertionError`
    except 5 (`IndexError`). Mutation 1 now reads `(2.934, 2.934) != (2.934,
    1.840)`.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    TRAIN_ROWS = 480

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
    def rebuilt(model, calibration, **changes):
        """`model`'s fitted estimators and state under another calibration and widening."""

        return ml.FittedGradientBoostedQuantiles(
            model._estimators,
            model.regressors,
            model.imputations,
            model.residuals,
            model.cutoff,
            model.levels,
            model.random_state,
            ml_libraries=model.ml_libraries,
            calibration=calibration,
            calibration_share=model.calibration_share,
            fit_end=model.fit_end,
            calibration_start=model.calibration_start,
            calibration_end=model.calibration_end,
            **changes,
        )

    def test_each_edge_moves_by_its_own_score_set(self):
        """Two score sets, two ranks, two edges; `conformal`'s band at equal widenings; refusals."""

        rows = heteroscedastic_frame(self.TRAIN_ROWS + 40)
        train = rows[: self.TRAIN_ROWS]
        feature_rows = rows[self.TRAIN_ROWS - 1 : -1]
        model = self.fit(train, calibration="conformal_asymmetric", information=gap_rule(0))

        with self.subTest("the edges move by different amounts, off separate score sets"):
            # Recomputed here: at a zero gap a calibration row's feature row is
            # the row before it, and the model reads it as the fit did.
            first = self.TRAIN_ROWS - int(ml.DEFAULT_CALIBRATION_SHARE * self.TRAIN_ROWS)
            self.assertEqual(model.calibration_start, train[first].date)
            lower_scores, upper_scores = [], []
            for index in range(first, self.TRAIN_ROWS):
                vector = model._quantile_vector(model.design_row(train[index - 1]))
                actual = train[index].spread_bps
                lower_scores.append(vector[0] - actual)
                upper_scores.append(actual - vector[-1])
            self.assertNotEqual(
                sorted(lower_scores),
                sorted(upper_scores),
                msg="the fixture: identical score sets cannot show the edges separating",
            )
            count = len(lower_scores)
            lower_rank = math.ceil(
                (1 - Fraction(repr(QUANTILE_LEVELS[0]))) * (count + 1)
            )
            upper_rank = math.ceil(Fraction(repr(QUANTILE_LEVELS[-1])) * (count + 1))
            down = sorted(lower_scores)[lower_rank - 1]
            up = sorted(upper_scores)[upper_rank - 1]
            self.assertNotEqual(down, up)
            self.assertEqual(model.edge_widenings, (down, up))
            self.assertEqual(model.widening, 0.0)
            for feature in feature_rows:
                fitted = model._quantile_vector(model.design_row(feature))
                reported = model.predict(feature)
                self.assertEqual(reported[1:-1], fitted[1:-1])
                self.assertEqual(reported[0], min(fitted[0] - down, fitted[1]))
                self.assertEqual(reported[-1], max(fitted[-1] + up, fitted[-2]))

        with self.subTest("equal widenings are conformal's band and law, bit for bit"):
            conformal = self.fit(train, calibration="conformal", information=gap_rule(0))
            widening = conformal.widening
            equal = self.rebuilt(
                conformal,
                "conformal_asymmetric",
                edge_widenings=(widening, widening),
            )
            self.assertEqual(
                ml._asymmetric_widenings(lower_scores, lower_scores, QUANTILE_LEVELS)[0],
                ml._asymmetric_widenings(lower_scores, lower_scores, QUANTILE_LEVELS)[1],
            )
            for feature in feature_rows:
                self.assertEqual(equal.predict(feature), conformal.predict(feature))
                self.assertEqual(equal.law_knots(feature), conformal.law_knots(feature))
                self.assertEqual(
                    equal.predict_stress(feature, EXCEEDANCE_TAUS),
                    conformal.predict_stress(feature, EXCEEDANCE_TAUS),
                )

        with self.subTest("a negative widening stops each outer level at its neighbour"):
            feature = feature_rows[0]
            fitted = model._quantile_vector(model.design_row(feature))
            past = -2.0 * (fitted[-1] - fitted[0]) - 1.0
            only_lower = self.rebuilt(
                model, "conformal_asymmetric", edge_widenings=(past, 0.0)
            ).predict(feature)
            self.assertEqual(only_lower, (fitted[1],) + fitted[1:])
            only_upper = self.rebuilt(
                model, "conformal_asymmetric", edge_widenings=(0.0, past)
            ).predict(feature)
            self.assertEqual(only_upper, fitted[:-1] + (fitted[-2],))

        with self.subTest("refusal: fewer calibration rows than either side's rank needs"):
            # 18 is a quarter of 75: enough for conformal's nine, not for nineteen.
            with self.assertRaisesRegex(
                ValueError,
                r"conformal_asymmetric calibration needs at least 19 calibration "
                r"rows, got 18",
            ):
                self.fit(rows[:75], calibration="conformal_asymmetric", information=gap_rule(0))
            self.assertEqual(
                self.fit(
                    rows[:76], calibration="conformal_asymmetric", information=gap_rule(0)
                ).calibration_start,
                rows[57].date,
            )

        with self.subTest("refusal: a tail"):
            with self.assertRaisesRegex(
                ValueError, r"not wired for calibration 'conformal_asymmetric'"
            ):
                self.fit(
                    rows[:120],
                    calibration="conformal_asymmetric",
                    information=gap_rule(0),
                    tail="gpd",
                )

        with self.subTest("the declaration names the calibration and its share"):
            self.assertEqual(
                dict(model.model_settings),
                {"calibration": "conformal_asymmetric", "calibration_share": 0.25},
            )


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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All nine killed again, on the subtests named above, `AssertionError`
    except 4c (`IndexError`). 4d was applied where the guard now lives, in
    `positional_history`.
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

        def fitter(train_frame, minimum_history, information):
            model = self.fit(
                train_frame,
                minimum_history=minimum_history,
                information=information,
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
            self.assertLess(
                dates.index(fold.feature_date),
                dates.index(fold.scored_date) - 1,
                msg="the feature row is the row before the scored day, so the "
                "gap between them is not under test",
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
                ValueError, r"is not a row of the history this model reads"
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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All thirteen killed again. Mutation 1, applied as `train_frame =
    rows[: index + 1]` in the fold loop, now dies before any subtest on the history
    guard's `ValueError` (the history handed over does not begin with the rows the
    model was fitted on); its cross-suite failures were not re-counted. Mutation 3
    was applied as `variances[position + 1]`. Mutation 6 also fails the recovery and
    two refusal subtests.
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

        def fitter(train_frame, minimum_history, information):
            model = self.fit(
                train_frame,
                minimum_history=minimum_history,
                information=information,
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
            information=gap_rule(0),
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
            self.assertLess(
                dates.index(fold.feature_date),
                dates.index(fold.scored_date) - 1,
                msg="the feature row is the row before the scored day, so the "
                "gap between them is not under test",
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
                information=gap_rule(0),
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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All twelve killed again, on the subtests named above,
    `AssertionError` except 5b (`IndexError`). Mutation 2 was applied as `kept`
    dropping the as-of rule on both sides of the block; 5f as the first
    `_require_information` call removed, now an `AttributeError` on `None.anchor`
    rather than a `TypeError`. Mutation 1's coverage is 0.754.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    TRAIN_ROWS = 480
    HELD_OUT_ROWS = 240
    PURGE = 6
    #: The fold loop's panel and minimum: every fold's frame is over a hundred
    #: rows, so its excluding models' trees split. See the class docstring.
    #: Three folds: each is asserted on its own, and a fourth adds fits, not
    #: another kind of fold (#29).
    PANEL_ROWS = 124
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
        cross = self.fit(train, calibration="cross_conformal", information=gap_rule(0))
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

        # From here on no assertion depends on how far the boosting ran: which
        # rows each excluding model trained on, which model scored each row,
        # and whether a moved row moves a model. The coverage subtest above
        # does -- its control needs an uncalibrated band that undercovers --
        # so its fits keep the estimator's default.
        fewer_boosting_iterations(self)

        with self.subTest("every excluding model trains outside its block and its purge gaps"):
            panel = heteroscedastic_frame(self.PANEL_ROWS)
            with tempfile.TemporaryDirectory() as directory:
                registry = json.loads(
                    declared_registry_file(
                        directory, purge=self.PURGE, features=self.FEATURES
                    ).read_text(encoding="utf-8")
                )
            fits = []

            def calibrating(train_frame, minimum_history, information):
                model = self.fit(
                    train_frame,
                    minimum_history=minimum_history,
                    calibration="cross_conformal",
                    information=information,
                )
                fits.append((list(train_frame), information, model))
                return model

            report = baseline.rolling_persistence_backtest(
                panel,
                features=self.FEATURES,
                registry=registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                minimum_history=self.MINIMUM_HISTORY,
                fit_model=calibrating,
            )
            self.assertGreater(len(fits), 1)
            self.assertEqual(len(fits), len(report.folds))
            for fold, (frame, information, model) in zip(report.folds, fits):
                with self.subTest(fold=fold.scored_date.isoformat()):
                    # The run's own rule, handed over by the fold loop; every
                    # boundary below is its label observability on the frame.
                    self.assertEqual(information.features, self.FEATURES)
                    dates = [row.date for row in frame]

                    def anchor(index):
                        return information.anchor(dates, index) if index > 0 else -1

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
                        start = dates.index(block.held_out_start)
                        end = dates.index(block.held_out_end)
                        for when in block.training_dates:
                            position = dates.index(when)
                            self.assertTrue(
                                position <= anchor(start)
                                or (position > end and anchor(position) >= end),
                                msg=(
                                    f"block {number}'s excluding model trained on "
                                    f"{when}, inside its block "
                                    f"{block.held_out_start}..{block.held_out_end} "
                                    f"or a label not observable across it"
                                ),
                            )
                        # Each held-out row is scored by this block's model, at
                        # its anchor, and only rows with one inside the frame
                        # are scored.
                        scored = [
                            index for index in range(start, end + 1)
                            if anchor(index) >= 0
                        ]
                        self.assertEqual(block.scored_dates, tuple(dates[i] for i in scored))
                        rescored, in_sample = [], []
                        for index in scored:
                            feature = anchor(index)
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
            frame, information, model = fits[-1]
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
                    information=information,
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
            # The first row after the block whose own decision already sees
            # the block's last label: the first one the excluding model trains on.
            clear = stop + 1
            while information.anchor(dates, clear) < stop:
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
            three = self.fit(rows[:60], calibration="cross_conformal", calibration_folds=3, information=gap_rule(0))
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
                             calibration_folds=folds, information=gap_rule(0))

        with self.subTest("refusal: a block that leaves its excluding model nothing to fit"):
            with self.assertRaisesRegex(
                ValueError,
                r"cross-conformal block 1 of 2 holds out 20 of 40 rows and leaves "
                r"its excluding model 0 training pair\(s\) after label observability",
            ):
                self.fit(rows[:40], calibration="cross_conformal",
                         calibration_folds=2, information=gap_rule(19))
            # And one pair is enough: the refusal sits at the edge.
            edge = self.fit(rows[:40], calibration="cross_conformal",
                            calibration_folds=2, information=gap_rule(18))
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
                self.fit(rows[:40], calibration="conformal", calibration_folds=3, information=gap_rule(0))

        with self.subTest("refusal: calibration_share with cross_conformal"):
            with self.assertRaisesRegex(
                ValueError, r"calibration_share 0.25 was given, but calibration 'cross_conformal'"
            ):
                self.fit(rows[:40], calibration="cross_conformal",
                         calibration_share=0.25, information=gap_rule(0))

        with self.subTest("refusal: fewer held-out scores than CV+'s ranks need"):
            with self.assertRaisesRegex(
                ValueError, r"needs at least 9 held-out scores, got 8"
            ):
                self.fit(rows[:9], minimum_history=9, calibration="cross_conformal",
                         calibration_folds=2, information=gap_rule(0))
            # And nine is enough.
            self.assertEqual(
                sum(
                    len(block.scores)
                    for block in self.fit(
                        rows[:10], minimum_history=10, calibration="cross_conformal",
                        calibration_folds=2, information=gap_rule(0),
                    ).calibration_blocks
                ),
                9,
            )

        with self.subTest("refusal: cross_conformal with no gap"):
            with self.assertRaisesRegex(SplitError, r"needs the run's as-of rule"):
                self.fit(rows[:40], calibration="cross_conformal")


def masking_frame(count, seed=20261002):
    """Weekday rows whose spread follows `reserve_balances`, a column slower than the target.

    Under the tracked registry `reserve_balances` (H.4.1, `WRESBAL`) is public
    days after the target, so the frame the fold loop hands a fitter carries
    it on rows whose label is already observable: the exposure
    `information-set.md`'s Method notes describe. The spread moves with it so
    the trees split on it, and a moved value can move a model.
    """

    rows = []
    state = seed
    when = date(2024, 1, 2)
    while len(rows) < count:
        if when.weekday() < 5:
            state = (1103515245 * state + 12345) % (2 ** 31)
            reserves = 3000.0 + (state % 500)
            spread = 5.0 + 0.04 * (reserves - 3000.0) + (state % 7) / 3.0
            rows.append(
                DailyObservation(
                    when,
                    {
                        "sofr": 4.30 + spread / 100.0,
                        "iorb": 4.30,
                        "reserve_balances": reserves,
                        "sofr_volume": 2000.0 + (state % 911),
                    },
                )
            )
        when += timedelta(days=1)
    return rows


class CalibrationMaskingTests(unittest.TestCase):
    """`calibration_masking="held_out_row"`: directive #78's option, test first.

    **The bias.** `docs/decisions/information-set.md`, Method notes: a
    cross-conformal fit scores each held-out row as a forecast read at its own
    decision instant, but the excluding model that scores it trains on the
    frame as masked at the **fold's** decision instant. A declared column
    slower than the target can therefore reach that model's training rows
    before the block with a value that was public at the fold's decision but
    not yet at the held-out row's. The option masks those values, per held-out
    row: each held-out row is scored by an excluding model whose training rows
    before the block carry only what was public at that row's own decision.
    Off by default, so every published record is unchanged.

    **What the test sees, and on what.** The tracked registry, under which
    `reserve_balances` is public days after the target, on a weekday frame
    whose spread follows it. For each block, the values exposed to its first
    held-out row are moved by 5000; every held-out row of that block that
    could not yet see any moved value must keep its score bit for bit under
    the option. The control: without the option, at least one such score
    moves, so the fixture can see the bias the option removes.

    Mutation record (#78)
    ---------------------

    Scratch copy under `/tmp` of the branch's tracked files, `PYTHONPATH=src`
    (resolved to the copy), `/opt/rmm-venv` (CPython 3.11, numpy 2.4.6,
    scikit-learn 1.9.1), this class alone. Unmutated control green; the anchor
    found exactly once and confirmed applied.

      * **The held-out row's frame taken unmasked** -- in `_held_out_mask`,
        `seen = information.frame(rows, information.information_set(dates,
        index))` replaced by `seen = list(rows[: info.anchor + 1])` (with
        `info` the same information set), so no value is ever masked and every
        held-out row is scored by the block's one model. `a held-out row never
        trains on a value it could not yet see`, `AssertionError` in blocks 2
        to 5, for example `-1.7636... != -1.7393... : block 2: the held-out row
        2024-02-14 could see none of the moved values, and its score moved
        with them`.
    """

    ROWS = 160
    FOLDS = 5

    def setUp(self):
        require_extra(self)
        from repo_model.asof import InformationRule

        registry = json.loads(
            (Path(__file__).resolve().parents[1] / "metadata" / "sources.json").read_text()
        )
        self.registry = registry
        self.rule = InformationRule(
            registry, ("spread_bps", "reserve_balances"), decision_time=time(16, 0)
        )
        fewer_boosting_iterations(self)

    def frame(self, rows, rule=None):
        rule = rule or self.rule
        dates = [row.date for row in rows]
        return rule.frame(rows, rule.information_set(dates, len(rows) - 1))

    def fit(self, frame, regressors=("reserve_balances",), rule=None, **settings):
        return ml.fit_gradient_boosted_quantiles(
            frame,
            regressors,
            minimum_history=20,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
            calibration="cross_conformal",
            calibration_folds=self.FOLDS,
            information=rule or self.rule,
            **settings,
        )

    @staticmethod
    def scores(fitted):
        out = {}
        for block in fitted.calibration_blocks:
            for when, score in zip(block.scored_dates, block.scores):
                if when in out:
                    raise AssertionError(f"{when} was scored twice")
                out[when] = score
        return out

    def test_a_held_out_row_never_trains_on_a_value_it_could_not_yet_see(self):
        frame = self.frame(masking_frame(self.ROWS))
        dates = [row.date for row in frame]
        bounds = [len(frame) * number // self.FOLDS for number in range(self.FOLDS + 1)]
        observed = self.rule.groups[1:]
        (group,) = [g for g in observed if "reserve_balances" in g.columns]

        def availability(position):
            return self.rule.availability(dates, group.fields, position)

        exercised = 0
        moved_without = 0
        for number in range(1, self.FOLDS):
            start = bounds[number]
            stop = bounds[number + 1]
            before = self.rule.anchor(dates, start)
            deadline = self.rule.decision_instant(dates, start)
            exposed = [
                position
                for position in range(before + 1)
                if frame[position].values.get("reserve_balances") is not None
                and availability(position) > deadline
            ]
            self.assertTrue(
                exposed,
                msg=f"block {number + 1}: the fixture exposes no value, so it cannot see the bias",
            )
            moved = list(frame)
            for position in exposed:
                values = dict(moved[position].values)
                values["reserve_balances"] = values["reserve_balances"] + 5000.0
                moved[position] = DailyObservation(moved[position].date, values)
            blind = [
                dates[index]
                for index in range(start, stop)
                if all(
                    availability(position) > self.rule.decision_instant(dates, index)
                    for position in exposed
                )
            ]
            with self.subTest("a held-out row never trains on a value it could not yet see", block=number + 1):
                masked = self.scores(self.fit(frame, calibration_masking="held_out_row"))
                masked_moved = self.scores(self.fit(moved, calibration_masking="held_out_row"))
                checked = [when for when in blind if when in masked]
                self.assertTrue(checked, msg=f"block {number + 1}: no blind held-out row is scored")
                for when in checked:
                    self.assertEqual(
                        masked[when],
                        masked_moved[when],
                        msg=(
                            f"block {number + 1}: the held-out row {when} could see none "
                            f"of the moved values, and its score moved with them"
                        ),
                    )
                exercised += len(checked)
            plain = self.scores(self.fit(frame))
            plain_moved = self.scores(self.fit(moved))
            moved_without += sum(plain[when] != plain_moved[when] for when in blind if when in plain)
        self.assertGreater(exercised, 0)
        self.assertGreater(
            moved_without,
            0,
            msg=(
                "the control: without the option no blind held-out row's score moves "
                "with the values it could not see, so this fixture cannot see the bias"
            ),
        )

    def test_the_option_scores_the_same_rows_and_is_recorded(self):
        frame = self.frame(masking_frame(self.ROWS))
        plain = self.fit(frame)
        masked = self.fit(frame, calibration_masking="held_out_row")
        self.assertEqual(sorted(self.scores(plain)), sorted(self.scores(masked)))
        self.assertNotIn("calibration_masking", plain.model_settings)
        self.assertEqual(masked.model_settings["calibration_masking"], "held_out_row")
        # The interior is the full fit's, which the option never touches.
        row = frame[-1]
        self.assertEqual(plain.predict(row)[1:-1], masked.predict(row)[1:-1])

    def test_a_declaration_as_fast_as_the_target_is_unchanged_bit_for_bit(self):
        from repo_model.asof import InformationRule

        rule = InformationRule(
            self.registry, ("spread_bps", "sofr_volume"), decision_time=time(16, 0)
        )
        frame = self.frame(masking_frame(self.ROWS), rule)
        plain = self.fit(frame, ("sofr_volume",), rule)
        masked = self.fit(frame, ("sofr_volume",), rule, calibration_masking="held_out_row")
        self.assertEqual(self.scores(plain), self.scores(masked))
        self.assertEqual(
            [block.training_dates for block in plain.calibration_blocks],
            [block.training_dates for block in masked.calibration_blocks],
        )
        for row in frame[-10:]:
            self.assertEqual(plain.predict(row), masked.predict(row))

    def test_refusals(self):
        frame = self.frame(masking_frame(60))
        with self.subTest("an unknown masking"):
            with self.assertRaisesRegex(ValueError, "unknown calibration_masking"):
                self.fit(frame, calibration_masking="fold")
        for calibration in ("none", "conformal", "conformal_asymmetric"):
            with self.subTest("a calibration with no excluding models", calibration=calibration):
                with self.assertRaisesRegex(ValueError, "calibration_masking"):
                    ml.fit_gradient_boosted_quantiles(
                        frame,
                        ("reserve_balances",),
                        minimum_history=20,
                        min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
                        calibration=calibration,
                        information=self.rule,
                        calibration_masking="held_out_row",
                    )
        with self.subTest("direct training pairs"):
            # A direct pair reads only what was public at its own target's
            # decision, earlier than any held-out row's after it: there is
            # nothing to mask, so the combination is refused, not ignored.
            with self.assertRaisesRegex(ValueError, "training_pairs 'direct'"):
                self.fit(frame, calibration_masking="held_out_row", training_pairs="direct")


class GradientBoostedCrossAsymmetricConformalTests(unittest.TestCase):
    """`calibration="cross_conformal_asymmetric"`: B54's acceptance criterion and its mutation target.

    **The question.** Whether the fourth cell of split-vs-CV+ against
    pooled-vs-per-side exists, or `cross_conformal` already fills it. It does
    not: `cross_conformal` ranks one pooled score at the band's `alpha`, which
    is (CV+, pooled). The cell is CV+ with two signed scores per held-out row,
    each edge at its own side's rank, and it needs no sample the fit does not
    already hold -- every excluding model scores its own block, and a signed
    score is read off the same vector the pooled one is. So it is built, not
    declined as B53's tail was. See the module docstring of `repo_model.ml`.

    **What this test asserts, and what it cannot.** That each edge is rebuilt
    here from every excluding model's own outer level at the forecast's row and
    its own side's signed scores, at `floor(lo (n + 1))` and `ceil(hi (n +
    1))`; that the fixture separates it from `cross_conformal`; that the rank is
    exact; and the refusals. No coverage figure: CV+'s per-side guarantee is
    `2 x` the side's miss rate in the worst case, and a fixture figure would
    not be evidence about the funding panel.

    **The exact rank, and why it is tested off the declared grid.** On the
    declared `0.05`-`0.95` grid a float side probability gives the same two
    ranks as the exact one at every count from nineteen to three thousand,
    checked when this block was written: a float-rate mutation there cannot
    die, and would be recorded as surviving for no reason. At `(0.1, 0.5, 0.55)`
    and ninety-nine scores it is off at both ends -- `0.55 x 100` is
    `55.00000000000001`, ceiling `56`, and `(1 - (1 - 0.1)) x 100` is
    `9.999999999999998`, floor `9` -- so the subtest reads the helper there.

    Mutation record (B54)
    ---------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B` (the worktree's `.venv`: CPython 3.9.6), `PYTHONPATH=src:tests`
    (checked to resolve to the copy's `src/`), `REPO_MODEL_REQUIRE_ML=1`,
    `OMP_NUM_THREADS=1`. Each mutation by exact-string replacement whose anchor
    was found exactly once, **asserted applied** -- the anchor gone and the
    replacement present -- then restored, and the file checked byte-identical
    at the end. Scored against this class; unmutated control green before and
    after, and `GradientBoostedCrossConformalTests`,
    `GradientBoostedAsymmetricConformalTests` and
    `GpdCrossConformalSampleTests` green beside it. No threshold was mutated by
    its value: each mutation changes a name read or an operator.

      * **Per side, not pooled** -- the lower edge reading `block.scores` for
        `block.lower_scores` in `_reported`. `each edge is CV+'s ...`,
        `AssertionError`: the lower edge at 2.046 against 3.456, the upper
        unchanged.
      * **Each side's own rate, not the band's** -- `_band_probability` for
        `_side_probabilities` in `_cross_conformal_asymmetric_edges`, which is
        CV+'s pooled ranks on the signed scores. `each edge is CV+'s ...`,
        `AssertionError` (5.240, 11.880 against 3.456, 12.692: narrower at
        both ends), and `the ranks are exact ...`, `AssertionError`.
      * **Exact rates** -- `1 - float(levels[0]), float(levels[-1])` for
        `_side_probabilities(levels)`. `the ranks are exact ...` only,
        `AssertionError: (8.0, 155.0) != (9.0, 154.0)`. On the declared grid
        this mutation is equivalent; see above.
      * **The signed scores themselves** -- `lower_scores` built as
        `y - Q_hi`. `each edge is CV+'s ...`, `AssertionError`: the pooled
        score is no longer their maximum.
      * **The floor** -- `_minimum_calibration_rows` for
        `_minimum_asymmetric_calibration_rows` under the new name. `refusal:
        fewer held-out scores ...`, `AssertionError: ValueError not raised`.
        Not an `IndexError`: the ranks are read at forecast time, so the fit
        with eighteen scores succeeds and would publish a lower edge read at
        index -1, the largest low.
      * **The tail refusal** made unreachable. `refusal: a tail`,
        `AssertionError: ValueError not raised`.
      * **The fitter's dispatch** -- `== "cross_conformal"` for
        `in _CROSS_CALIBRATIONS`. Four subtests, all `AssertionError`: the name
        fell through to the *split* branch and fitted `conformal` under a
        declaration of `cross_conformal_asymmetric` with `calibration_folds`
        `None` -- the silent mis-fit this subtest set exists for.
      * **The declaration** -- `model_settings` reading `== "cross_conformal"`.
        `the declaration names ...`, `AssertionError: {} != {...}`.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All eight killed again, on the subtests named above,
    `AssertionError`. Mutation 3 still reads `(8.0, 155.0) != (9.0, 154.0)`.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    TRAIN_ROWS = 480
    FORECAST_ROWS = 40

    def setUp(self):
        require_extra(self)
        fewer_boosting_iterations(self)

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

    def test_each_cv_plus_edge_is_taken_off_its_own_side_at_its_own_rank(self):
        """Per-side CV+ edges rebuilt here, the full fit's interior, exact ranks, refusals."""

        rows = heteroscedastic_frame(self.TRAIN_ROWS + self.FORECAST_ROWS)
        train = rows[: self.TRAIN_ROWS]
        forecasts = rows[self.TRAIN_ROWS - 1 : -1]
        model = self.fit(train, calibration="cross_conformal_asymmetric", information=gap_rule(0))
        pooled = self.fit(train, calibration="cross_conformal", information=gap_rule(0))

        with self.subTest("each edge is CV+'s over its own side's signed scores, at its own rank"):
            blocks = model.calibration_blocks
            self.assertEqual(len(blocks), ml.DEFAULT_CALIBRATION_FOLDS)
            for block, other in zip(blocks, pooled.calibration_blocks):
                # The same excluding models as cross_conformal's, whose scores
                # `GradientBoostedCrossConformalTests` rescores; the two signed
                # sets are the pooled score taken apart, not pooled again.
                self.assertEqual(block.scores, other.scores)
                self.assertEqual(
                    block.scores,
                    tuple(max(lo, hi) for lo, hi in zip(block.lower_scores, block.upper_scores)),
                )
                self.assertNotEqual(block.lower_scores, block.upper_scores)
            count = sum(len(block.scores) for block in blocks)
            lower_rank = math.floor(Fraction(repr(QUANTILE_LEVELS[0])) * (count + 1))
            upper_rank = math.ceil(Fraction(repr(QUANTILE_LEVELS[-1])) * (count + 1))
            separated = 0
            for row in forecasts:
                lows, highs = [], []
                for block in blocks:
                    excluded = self.sorted_levels(block.estimators, self.design(row))
                    lows.extend(excluded[0] - score for score in block.lower_scores)
                    highs.extend(excluded[-1] + score for score in block.upper_scores)
                fitted = model._quantile_vector(model.design_row(row))
                reported = model.predict(row)
                self.assertEqual(reported[1:-1], fitted[1:-1])
                self.assertEqual(reported[1:-1], pooled.predict(row)[1:-1])
                self.assertEqual(
                    (reported[0], reported[-1]),
                    (
                        min(sorted(lows)[lower_rank - 1], fitted[1]),
                        max(sorted(highs)[upper_rank - 1], fitted[-2]),
                    ),
                    msg=f"the band forecast from {row.date} is not per-side CV+'s",
                )
                other = pooled.predict(row)
                separated += (reported[0], reported[-1]) != (other[0], other[-1])
            self.assertGreater(
                separated,
                0,
                msg="the fixture: every band equals cross_conformal's, so it cannot tell the two apart",
            )

        with self.subTest("the ranks are exact, on a grid where a float rank is one off"):
            # Exact: the 10th smallest low and the 55th smallest high.
            lows = [float(value) for value in range(99)]
            highs = [float(value) + 100.0 for value in range(99)]
            self.assertEqual(
                ml._cross_conformal_asymmetric_edges(lows, highs, (0.1, 0.5, 0.55)),
                (9.0, 154.0),
            )

        with self.subTest("refusal: fewer held-out scores than either side's rank needs"):
            # 18 scores clear cross_conformal's nine and not the per-side nineteen.
            with self.assertRaisesRegex(
                ValueError,
                r"cross_conformal_asymmetric calibration needs at least 19 held-out "
                r"scores, got 18",
            ):
                self.fit(rows[:19], minimum_history=19,
                         calibration="cross_conformal_asymmetric",
                         calibration_folds=2, information=gap_rule(0))
            # And nineteen is enough.
            edge = self.fit(rows[:20], calibration="cross_conformal_asymmetric",
                            calibration_folds=2, information=gap_rule(0))
            self.assertEqual(sum(len(block.scores) for block in edge.calibration_blocks), 19)

        with self.subTest("refusal: a tail"):
            with self.assertRaisesRegex(
                ValueError, r"not wired for calibration 'cross_conformal_asymmetric'"
            ):
                self.fit(rows[:120], calibration="cross_conformal_asymmetric",
                         information=gap_rule(0), tail="gpd")

        with self.subTest("refusal: a calibration_share"):
            with self.assertRaisesRegex(
                ValueError,
                r"calibration_share 0.25 was given, but calibration "
                r"'cross_conformal_asymmetric'",
            ):
                self.fit(rows[:40], calibration="cross_conformal_asymmetric",
                         calibration_share=0.25, information=gap_rule(0))

        with self.subTest("the declaration names the calibration and its folds"):
            self.assertEqual(
                dict(model.model_settings),
                {"calibration": "cross_conformal_asymmetric", "calibration_folds": 5},
            )


#: `regime_frame`'s noise scales, in basis points, and the order its blocks of
#: `REGIME_ROWS` rows take them in: two calm blocks to one stressed.
CALM_SD = 1.0
STRESSED_SD = 4.0
REGIME_PATTERN = (CALM_SD, CALM_SD, STRESSED_SD)
REGIME_ROWS = 100


def regime_sd(index):
    """The noise scale `regime_frame` draws row `index` at."""

    return REGIME_PATTERN[(index // REGIME_ROWS) % len(REGIME_PATTERN)]


def regime_frame(count, seed=20260916, flat=()):
    """Calendar-day rows whose spread is `10 + sd z`, `sd` switching by regime.

    Independent draws about 10 bp, so the only thing that differs between a
    calm row and a stressed one is the noise scale, and a band that is right on
    one is wrong on the other unless it scales. Box-Muller off
    `random.Random(seed).random()`, as `heteroscedastic_frame` draws, so the
    sequence is fixed across the declared Python versions. Rows in `flat`
    carry exactly 10 bp: a flat stretch, every change inside it zero.
    `sofr_volume` moves with nothing and is the declared regressor.
    """

    rng = random.Random(seed)
    rows = []
    for index in range(count):
        first, second = rng.random(), rng.random()
        shock = math.sqrt(-2.0 * math.log(1.0 - first)) * math.cos(2.0 * math.pi * second)
        spread = 10.0 if index in flat else 10.0 + regime_sd(index) * shock
        rows.append(
            DailyObservation(
                date(2020, 1, 1) + timedelta(days=index),
                {
                    "sofr": 4.30 + spread / 100.0,
                    "iorb": 4.30,
                    "sofr_volume": 2000.0 + rng.random(),
                },
            )
        )
    return rows


class ConstantQuantile:
    """A stand-in for `HistGradientBoostingRegressor`: the training targets' `quantile`, on every row.

    Takes the keywords `ml._fitted_levels` passes and ignores all but the
    level. The regime subtests read the *calibration*, and a base model that
    cannot see the regime is the case the calibration exists for -- it is also
    what gbm is on a regime its design carries no column for. And it is fast
    enough to refit at every origin of a rolling loop, which a boosted fit is
    not at this length.
    """

    def __init__(self, *, loss, quantile, early_stopping, random_state, min_samples_leaf):
        self.quantile = quantile
        self.value = None

    def fit(self, design, targets):
        ordered = sorted(targets)
        self.value = ordered[min(len(ordered) - 1, int(self.quantile * len(ordered)))]
        return self

    def predict(self, design):
        return [self.value] * len(design)


class ScaledCrossConformalTests(unittest.TestCase):
    """`calibration="cross_conformal_scaled"`: B-SCALED's acceptance criterion and its mutation target.

    **The defect.** Job 657 read the published
    `docs/runs/backtest_gbm_cross_conformal_mh61.json` apart: 6.87% missed
    against 10% declared, but by a trailing volatility known before each
    origin the calm third missed 3.1% and the stressed third 10.1%. The band's
    width does not move with the regime. This class shows the same defect on a
    fixture built to have it, and the repair.

    **The fixture.** `regime_frame`: independent draws about 10 bp, calm
    (`sd` 1 bp) for two blocks of a hundred rows and stressed (`sd` 4 bp) for
    one, repeated. The regime subtest refits at every origin of a rolling loop
    on a sliding 300-row frame -- always two calm blocks' worth and one
    stressed -- with `ConstantQuantile` for the boosted fit, and scores the
    row `PURGE + 1` days on. An origin is counted for a regime when its scale
    window and its target both lie inside one block of it; the rest are
    forecast and not counted, since their regime is not one thing.

    **The tolerance, from the sample size.** B22's and B25's:
    `3 sqrt(q (1 - q) (1 / T + 1 / (n + 2)))` about the nominal miss rate
    `1 - q = 0.10`, two-sided, with `T` the counted origins of the regime and
    `n` the held-out scores of the last fold's fit. The `1 / T` term is the
    binomial spread of `T` misses; the `1 / (n + 2)` term is the spread of a
    band's coverage given its own `n` calibration scores, taken as if every
    origin shared one set -- conservative, since a sliding frame renews its set
    as it moves. Five periods make `T` 780 calm and 390 stressed origins and
    `n` 278, so the tolerance is about 0.063 calm and 0.071 stressed. CV+'s
    worst case is `2 alpha`; the test holds it to `alpha`, which it attains on
    exchangeable rows, as B25 does. **The defect is asserted on the same
    tolerance**: `cross_conformal` must miss below its lower edge in the calm
    regime and above its upper edge in the stressed one, or this fixture
    cannot tell a scaled band from an unscaled one.

    **The leak, and what can see it.** A scale over the whole frame, or a
    window centred on the feature row, passes the regime subtest as well as the
    trailing one does -- better, since it sees the regime it is forecasting.
    Only a perturbation can tell them apart: moving every spread after a date
    must leave the scale of every held-out row whose target is on or before it
    bit-identical, and must move some later one (the control). At a 6-day gap,
    so a window ending at the target instead of the feature row reads six rows
    it may not.

    Mutation record (B-SCALED)
    --------------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, one sub-copy per mutation,
    `PYTHONDONTWRITEBYTECODE=1`, `python -B` (the `.venv`: CPython 3.9.6,
    numpy 2.0.2, scikit-learn 1.6.1), `PYTHONPATH=src:tests` (checked to
    resolve to each sub-copy), `REPO_MODEL_REQUIRE_ML=1`, `OMP_NUM_THREADS=1`.
    Each mutation by exact-string replacement whose anchor was found exactly
    once, asserted applied, in `repo_model/ml.py`. Scored against this class;
    unmutated control green before and after.

      1. **Scale forced to a constant 1** -- `_trailing_scale` returns `1.0`.
         `each regime misses ...`, `AssertionError`: 0.0000 of 780 calm
         origins against 0.10 +/- 0.0627 -- the scaled band is
         `cross_conformal`'s defect again. Also `AssertionError` in the
         held-out leak subtest (its control: no scale moved), the forecast
         subtest, the floor (`1.0 != 0.2236`) and the rebuilt residuals.
      2. **The window moved off the feature row**, three ways:
          - **centred** on it (`position - SCALE_WINDOW // 2 : position +
            SCALE_WINDOW // 2 + 1`). **The regime subtest passes** -- the
            trap. `a held-out row's scale reads nothing after its feature
            row`, `AssertionError`: block 3's row scored on 2020-05-28 moved
            when only spreads after 2020-05-30 did. The forecast subtest also
            fails, `AssertionError`, but on the rebuilt definition and not
            on the leak: `_origin_scale` hands over no row after the feature
            row, so a centred window there is short, not leaky. Also the floor
            and the rebuilt residuals, `AssertionError`;
          - **the whole frame** (`window = spreads`). The held-out leak
            subtest, `AssertionError` (a row scored on 2020-01-28 moved). **The
            regime subtest fails too** (0.0000 calm): a whole-frame scale is one
            number per frame, which is the constant of mutation 1 per fold,
            not a regime reading. The brief's "passes the regime test
            beautifully" holds for the centred window and not for this one;
          - **seven rows later**, the 6-day gap's worth, so the window ends at
            the target side. The held-out leak subtest, `AssertionError`; the
            regime subtest passes.
      3. **The floor removed** -- `math.sqrt(...)` without the `max`. `a flat
         stretch takes the floor` alone, `AssertionError: 0.0 != 0.2236...: a
         window whose every change is zero is not given the floor`. The named
         failure is the right one: the same fit reached without that
         assertion raises `ZeroDivisionError` out of the scaled residual,
         which reads as an incidental error, and a window that is merely
         nearly flat would raise nothing and publish a band scaled by
         almost zero.
      4. **`cross_conformal` routed through the scale** -- the fitter's
         `scaled` flag and `_reported`'s branch both widened to
         `("cross_conformal", "cross_conformal_scaled")`. This class,
         `AssertionError` three times: `cross_conformal is unchanged ...`
         (its blocks carry scales), the band subtest (`0 != 20`: no band
         separates any more) and the regime subtest's control
         (`cross_conformal` misses 0.0846 calm). Scored beside it:
         `GradientBoostedCrossConformalTests` **errors**, `ValueError` (a
         forecast off the frame has no scale), and
         `tests/test_generated_results.py` **stays green**: it re-scores the
         published records and fits nothing, so it cannot see a fitter
         defect. The equality subtest here is the guard.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All six killed again, `AssertionError`. 2b and 2c now also fail the
    forecast, floor and band-rebuild subtests. Mutation 4 widened the `trailing`
    flag along with `scaled`, which the record predates.
    """

    REGRESSORS = ("sofr_volume",)
    FRAME_ROWS = 300
    PERIODS = 5
    PURGE = 1
    #: The gap the leak subtests are run at: the published declaration's.
    LEAK_PURGE = 6
    #: Where the leak subtests move every later spread, and how far.
    PERTURB_AT = 150
    PERTURB_BPS = 3.0
    #: The boosted fit the band is rebuilt from: long enough that its trees
    #: split, short enough to fit twice.
    TRAIN_ROWS = 240
    FORECAST_ROWS = 20
    NAME = "cross_conformal_scaled"

    def setUp(self):
        require_extra(self)

    def fit(self, frame, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
            "calibration": self.NAME,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(frame, self.REGRESSORS, **options)

    def constant_fit(self, frame, **overrides):
        with mock.patch.object(ml, "_estimator_class", return_value=ConstantQuantile):
            return self.fit(frame, **overrides)

    @staticmethod
    def rms_scale(frame, position):
        """The scale at `frame[position]`, built here from its definition."""

        spreads = [row.spread_bps for row in frame]
        squares = [
            (spreads[k] - spreads[k - 1]) ** 2
            for k in range(position - ml.SCALE_WINDOW + 1, position + 1)
        ]
        return max(
            math.sqrt(math.fsum(squares) / len(squares)),
            1.0 / math.sqrt(ml.SCALE_WINDOW),
        )

    @staticmethod
    def sorted_levels(estimators, frame):
        """Every row of `frame` read at every level and sorted, off the estimators directly."""

        designs = [[float(row.spread_bps), float(row.values["sofr_volume"])] for row in frame]
        columns = [[float(value) for value in estimator.predict(designs)] for estimator in estimators]
        return [sorted(column[index] for column in columns) for index in range(len(designs))]

    @staticmethod
    def perturbed(frame, after, bps):
        """`frame` with every spread after position `after` moved by `+bps` or `-bps`, alternately."""

        return [
            with_spread_shifted(row, bps if index % 2 else -bps) if index > after else row
            for index, row in enumerate(frame)
        ]

    def test_the_scaled_band_covers_each_regime_and_reads_nothing_after_its_decision(self):
        """Per-regime coverage where cross_conformal fails it, no leak, the floor, the band, the declaration."""

        q = Fraction("0.95") - Fraction("0.05")
        nominal = float(1 - q)

        with self.subTest("each regime misses its nominal rate, and cross_conformal's does not"):
            skip_if_fast(self, "a refit at every origin of two regime sweeps")
            count = self.FRAME_ROWS + self.PERIODS * REGIME_ROWS * len(REGIME_PATTERN) + self.PURGE + 1
            rows = regime_frame(count)
            misses = {}
            scores = None
            for calibration in ("cross_conformal", self.NAME):
                tally = {CALM_SD: [0, 0], STRESSED_SD: [0, 0]}
                for origin in range(self.FRAME_ROWS - 1, count - self.PURGE - 1):
                    frame = rows[origin - self.FRAME_ROWS + 1 : origin + 1]
                    model = self.constant_fit(
                        frame, calibration=calibration, information=gap_rule(self.PURGE)
                    )
                    band = model.predict(rows[origin])
                    target = origin + self.PURGE + 1
                    if (origin - ml.SCALE_WINDOW) // REGIME_ROWS != target // REGIME_ROWS:
                        continue
                    outcome = rows[target].spread_bps
                    counted = tally[regime_sd(target)]
                    counted[0] += not band[0] <= outcome <= band[-1]
                    counted[1] += 1
                misses[calibration] = {sd: (m / t, t) for sd, (m, t) in tally.items()}
                if calibration == self.NAME:
                    scores = sum(len(block.scaled_residuals) for block in model.calibration_blocks)
            for sd, label in ((CALM_SD, "calm"), (STRESSED_SD, "stressed")):
                rate, origins = misses[self.NAME][sd]
                before, _ = misses["cross_conformal"][sd]
                tolerance = 3.0 * math.sqrt(
                    nominal * (1.0 - nominal) * (1.0 / origins + 1.0 / (scores + 2))
                )
                self.assertLessEqual(
                    abs(rate - nominal),
                    tolerance,
                    msg=(
                        f"the scaled band misses {rate:.4f} of {origins} {label} "
                        f"origins against {nominal:.2f} +/- {tolerance:.4f} "
                        f"(cross_conformal {before:.4f})"
                    ),
                )
                # The control: the defect, in this fixture, on this tolerance.
                control = (
                    f"the control: cross_conformal misses {before:.4f} of {origins} "
                    f"{label} origins, not outside {nominal:.2f} +/- {tolerance:.4f}"
                )
                if sd == CALM_SD:
                    self.assertLess(before, nominal - tolerance, msg=control)
                else:
                    self.assertGreater(before, nominal + tolerance, msg=control)

        with self.subTest("a held-out row's scale reads nothing after its feature row"):
            frame = regime_frame(self.FRAME_ROWS)
            moved = self.perturbed(frame, self.PERTURB_AT, self.PERTURB_BPS)
            opens = frame[self.PERTURB_AT].date
            before = self.constant_fit(frame, information=gap_rule(self.LEAK_PURGE))
            after = self.constant_fit(moved, information=gap_rule(self.LEAK_PURGE))
            checked = changed = 0
            for number, (one, two) in enumerate(
                zip(before.calibration_blocks, after.calibration_blocks), start=1
            ):
                self.assertEqual(one.scored_dates, two.scored_dates)
                self.assertEqual(len(one.scales), len(one.scored_dates))
                for when, left, right in zip(one.scored_dates, one.scales, two.scales):
                    if when <= opens:
                        checked += 1
                        self.assertEqual(
                            left,
                            right,
                            msg=(
                                f"block {number}: the scale of the row scored on {when} "
                                f"moved when only spreads after {opens} did"
                            ),
                        )
                    else:
                        changed += left != right
            self.assertGreater(checked, 100)
            self.assertGreater(
                changed, 0, msg="the control: moving the later spreads moved no scale at all"
            )
            # And the scale is the trailing window at the feature row, rebuilt
            # here: the row the 6-day gap chooses, seven calendar rows back.
            block = before.calibration_blocks[2]
            for when, scale in zip(block.scored_dates, block.scales):
                index = (when - frame[0].date).days
                self.assertEqual(scale, self.rms_scale(frame, index - self.LEAK_PURGE - 1))

        with self.subTest("a forecast's scale and band read nothing after its feature row"):
            frame = regime_frame(self.FRAME_ROWS)
            model = self.constant_fit(frame, information=gap_rule(self.LEAK_PURGE))
            row = frame[self.PERTURB_AT]
            scale, band = model._origin_scale(row), model.predict(row)
            self.assertEqual(scale, self.rms_scale(frame, self.PERTURB_AT))
            history = model._history_spreads
            model._history_spreads = history[: self.PERTURB_AT + 1] + tuple(
                spread + self.PERTURB_BPS for spread in history[self.PERTURB_AT + 1 :]
            )
            self.assertEqual((model._origin_scale(row), model.predict(row)), (scale, band))
            # The control: a spread inside the window moves both.
            model._history_spreads = (
                history[: self.PERTURB_AT - 3]
                + (history[self.PERTURB_AT - 3] + self.PERTURB_BPS,)
                + history[self.PERTURB_AT - 2 :]
            )
            self.assertNotEqual(model._origin_scale(row), scale)
            self.assertNotEqual(model.predict(row), band)

        with self.subTest("a flat stretch takes the floor"):
            self.assertEqual(ml.SCALE_FLOOR_BPS, 1.0 / math.sqrt(ml.SCALE_WINDOW))
            self.assertEqual(
                ml._trailing_scale([10.0] * 25, 22),
                ml.SCALE_FLOOR_BPS,
                msg="a window whose every change is zero is not given the floor",
            )
            flat = range(120, 160)
            frame = regime_frame(self.FRAME_ROWS, flat=flat)
            model = self.constant_fit(frame, information=gap_rule(self.PURGE))
            floored = 0
            for block in model.calibration_blocks:
                for when, scale, score in zip(block.scored_dates, block.scales, block.scaled_residuals):
                    self.assertTrue(math.isfinite(score))
                    feature = (when - frame[0].date).days - self.PURGE - 1
                    if feature - ml.SCALE_WINDOW >= flat[0] and feature < flat[-1] + 1:
                        floored += 1
                        self.assertEqual(scale, ml.SCALE_FLOOR_BPS)
            self.assertGreater(floored, 10)
            band = model.predict(frame[flat[-1]])
            self.assertEqual(model._origin_scale(frame[flat[-1]]), ml.SCALE_FLOOR_BPS)
            self.assertTrue(all(math.isfinite(value) for value in band))
            self.assertLess(band[0], band[-1])

        rows = heteroscedastic_frame(self.TRAIN_ROWS)
        forecasts = rows[-self.FORECAST_ROWS :]
        model = self.fit(rows, information=gap_rule(0))
        cross = self.fit(rows, calibration="cross_conformal", information=gap_rule(0))

        with self.subTest("the band is CV+'s over scaled residuals, and the interior the full fit's"):
            blocks = model.calibration_blocks
            self.assertEqual(len(blocks), ml.DEFAULT_CALIBRATION_FOLDS)
            for block, other in zip(blocks, cross.calibration_blocks):
                # The same excluding models as cross_conformal's; only the
                # scores differ, and they are rebuilt here.
                self.assertEqual(
                    self.sorted_levels(block.estimators, forecasts),
                    self.sorted_levels(other.estimators, forecasts),
                )
                indices = [(when - rows[0].date).days for when in block.scored_dates]
                levels = self.sorted_levels(block.estimators, [rows[i - 1] for i in indices])
                rebuilt = [
                    abs(rows[i].spread_bps - read[2]) / self.rms_scale(rows, i - 1)
                    for i, read in zip(indices, levels)
                ]
                self.assertEqual(list(block.scaled_residuals), rebuilt)
            count = sum(len(block.scaled_residuals) for block in blocks)
            low_rank = math.floor((1 - q) * (count + 1))
            high_rank = math.ceil(q * (count + 1))
            separated = 0
            reads = [self.sorted_levels(block.estimators, forecasts) for block in blocks]
            for number, row in enumerate(forecasts):
                scale = self.rms_scale(rows, (row.date - rows[0].date).days)
                lows, highs = [], []
                for block, read in zip(blocks, reads):
                    middle = read[number][2]
                    lows.extend(middle - scale * score for score in block.scaled_residuals)
                    highs.extend(middle + scale * score for score in block.scaled_residuals)
                fitted = model._quantile_vector(model.design_row(row))
                reported = model.predict(row)
                self.assertEqual(reported[1:-1], fitted[1:-1])
                self.assertEqual(reported[1:-1], cross.predict(row)[1:-1])
                self.assertEqual(
                    (reported[0], reported[-1]),
                    (
                        min(sorted(lows)[low_rank - 1], fitted[1]),
                        max(sorted(highs)[high_rank - 1], fitted[-2]),
                    ),
                    msg=f"the band forecast from {row.date} is not scaled CV+'s",
                )
                other = cross.predict(row)
                separated += (reported[0], reported[-1]) != (other[0], other[-1])
            self.assertEqual(separated, len(forecasts))

        with self.subTest("cross_conformal is unchanged: no scale, and its band is unscaled CV+'s"):
            count = sum(len(block.scores) for block in cross.calibration_blocks)
            low_rank = math.floor((1 - q) * (count + 1))
            high_rank = math.ceil(q * (count + 1))
            for block in cross.calibration_blocks:
                self.assertEqual((block.scales, block.scaled_residuals), ((), ()))
            reads = [self.sorted_levels(block.estimators, forecasts) for block in cross.calibration_blocks]
            for number, row in enumerate(forecasts):
                lows, highs = [], []
                for block, read in zip(cross.calibration_blocks, reads):
                    excluded = read[number]
                    lows.extend(excluded[0] - score for score in block.scores)
                    highs.extend(excluded[-1] + score for score in block.scores)
                fitted = cross._quantile_vector(cross.design_row(row))
                reported = cross.predict(row)
                self.assertEqual(
                    (reported[0], reported[-1]),
                    (
                        min(sorted(lows)[low_rank - 1], fitted[1]),
                        max(sorted(highs)[high_rank - 1], fitted[-2]),
                    ),
                    msg=f"cross_conformal's band forecast from {row.date} is not CV+'s",
                )

        with self.subTest("the declaration names the calibration, and the command line reaches it"):
            self.assertEqual(
                dict(model.model_settings),
                {"calibration": self.NAME, "calibration_folds": 5},
            )
            self.assertIn(self.NAME, ml.CALIBRATIONS)
            parser = cli.build_parser()
            backtest = parser.parse_args(
                ["backtest", "panel.csv", "--registry", "registry.json",
                 "--decision-time", DECISION_TIME, "--report", "r.json",
                 "--feature", "spread_bps", "--model", "gbm",
                 "--calibration", self.NAME]
            )
            _, fitter = cli_eval._select_fitter(backtest)
            self.assertEqual(fitter.keywords, {"regressors": (), "calibration": self.NAME})

        with self.subTest("refusal: a forecast from a row with no scale, or off the frame"):
            with self.assertRaisesRegex(ValueError, r"has no scale: .* its frame has 10 row\(s\) before it"):
                model.predict(rows[10])
            beyond = heteroscedastic_frame(self.TRAIN_ROWS + 1)[-1]
            with self.assertRaisesRegex(ValueError, r"is not a row of the history"):
                model.predict(beyond)

        with self.subTest("refusal: fewer scaled scores than CV+'s ranks need"):
            # A row is scored only once its feature row has a full window
            # before it: rows 21 to 28 of 29 are eight.
            with self.assertRaisesRegex(
                ValueError, r"cross_conformal_scaled calibration needs at least 9 held-out scores, got 8"
            ):
                self.fit(rows[:29], calibration_folds=2, information=gap_rule(0))
            edge = self.fit(rows[:30], calibration_folds=2, information=gap_rule(0))
            self.assertEqual(sum(len(block.scaled_residuals) for block in edge.calibration_blocks), 9)

        with self.subTest("refusal: a tail, and a calibration_share"):
            with self.assertRaisesRegex(
                ValueError, r"not wired for calibration 'cross_conformal_scaled'"
            ):
                self.fit(rows[:120], information=gap_rule(0), tail="gpd")
            with self.assertRaisesRegex(
                ValueError,
                r"calibration_share 0.25 was given, but calibration 'cross_conformal_scaled'",
            ):
                self.fit(rows[:40], calibration_share=0.25, information=gap_rule(0))


#: How much of a declared band `NarrowRegimeQuantile` fits: the outer levels
#: pulled toward the median to this share of their distance from it.
NARROW_SHARE = 0.6


class NarrowRegimeQuantile:
    """A stand-in for `HistGradientBoostingRegressor` whose band tracks the regime and is too narrow.

    Reads design column 1, a regressor carrying the row's regime, and predicts
    the training targets of that regime at `0.5 + NARROW_SHARE (level - 0.5)`:
    the declared `0.05`-`0.95` band fitted as `0.23`-`0.77`. Its edges move
    with the regime and carry its shape, and its width is wrong in both -- the
    case a correction scaled by the regime is for. See
    `PartialCrossConformalTests` on why `ConstantQuantile` is not that case.
    """

    def __init__(self, *, loss, quantile, early_stopping, random_state, min_samples_leaf):
        self.level = 0.5 + (quantile - 0.5) * NARROW_SHARE
        self.values = {}

    def _quantile(self, targets):
        ordered = sorted(targets)
        return ordered[min(len(ordered) - 1, int(self.level * len(ordered)))]

    def fit(self, design, targets):
        groups = {}
        for row, target in zip(design, targets):
            groups.setdefault(float(row[1]), []).append(target)
        self.values = {regime: self._quantile(group) for regime, group in groups.items()}
        return self

    def predict(self, design):
        return [self.values[float(row[1])] for row in design]


def skewed_frame(count, seed=20260916):
    """Calendar-day rows whose spread is `10 + (1 + x)(E - 1)`, `E` standard exponential.

    `x` is the declared regressor `on_rrp`, uniform on `[0, 1)`, so the
    conditional law is right-skewed with a scale that moves with `x`: its
    `0.05` quantile sits about `0.64 (1 + x)` below the median and its `0.95`
    quantile about `2.3 (1 + x)` above. A band rebuilt about the median loses
    that shape; one built on the fit's own edges keeps it.
    """

    rng = random.Random(seed)
    rows = []
    for index in range(count):
        on_rrp = rng.random()
        spread = 10.0 + (1.0 + on_rrp) * (-math.log(1.0 - rng.random()) - 1.0)
        rows.append(
            DailyObservation(
                date(2020, 1, 1) + timedelta(days=index),
                {"sofr": 4.30 + spread / 100.0, "iorb": 4.30, "on_rrp": on_rrp},
            )
        )
    return rows


class PartialCrossConformalTests(unittest.TestCase):
    """`calibration="cross_conformal_partial"`: B-PARTIAL's acceptance criterion and its mutation target.

    **Why.** Job 662 scored `cross_conformal_scaled` against the published
    `cross_conformal` record: fully proportional scaling over-corrected (calm
    missed 13.4%, stressed 4.1%), and centring on the median lost the gbm's
    lower-tail skew in calm stretches. The ruling of 16 September 2026: keep
    `cross_conformal`'s score and the fit's own edges, and divide the score by
    `sigma ** PARTIAL_SCALE_EXPONENT`, `gamma = 0.5` fixed in advance.

    **The premise, tested and found false on B-SCALED's own fixture.** The
    brief asked for the interpolation on `regime_frame` with
    `ConstantQuantile`. Measured before this class was written, over the same
    five periods (780 calm and 390 stressed origins), per-regime miss rates
    calm / stressed: `cross_conformal` 0.0000 / 0.3179, `cross_conformal_scaled`
    0.0846 / 0.0795, and `cross_conformal_partial` 0.0000 / 0.3462 at
    `gamma = 0.5`, 0.0013 / 0.3487 at 1 and 0.0000 / 0.3564 at 0. Not between,
    at any exponent. The reason is structural, not a tuning miss: a base band
    that does not move with the regime is too wide on every calm row and too
    thin on every stressed one, so `cross_conformal`'s score is negative on the
    first and positive on the second. Dividing by a positive factor keeps every
    sign, so CV+'s rank still lands among the stressed rows' scores and the
    correction cannot shrink a calm band or reach the stressed tail; only a
    score that makes the two regimes exchangeable -- `cross_conformal_scaled`'s
    residual about the median over the scale -- can. A stand-in whose edges
    only half-track the regime (quantiles split on today's spread deviation)
    did no better: stressed 0.2615 at 0.5 against `cross_conformal`'s 0.2462,
    worse as `gamma` grew. **So on the panel, this calibration can only help to
    the extent the gbm's own edges already move with the regime**; the scoring
    run is the measurement of that, and this fixture is not a prediction of it.

    **The fixture used instead.** `regime_frame` with the row's regime carried
    as the regressor `regime_sd`, and `NarrowRegimeQuantile` as the base: edges
    that track the regime, a band too narrow in both. There the correction is
    positive in both regimes and in proportion to the noise, and a partial
    scale lands between none and full. Refitted at every origin of B-SCALED's
    rolling loop (a sliding 300-row frame, the row `PURGE + 1` days on), an
    origin counted for a regime when its scale window and target both lie in
    one block of it. Measured: calm 11 / 38 / 63 misses of 780 for
    `cross_conformal` / partial / scaled, stressed 93 / 75 / 33 of 390.

    **The tolerance, from the sample.** The three bands are scored on the
    same origins, so the comparison is paired: with `D` the origins on which
    exactly one of two bands misses, their miss counts differ by a sign-test
    sum whose standard deviation is `sqrt(D)` when the two rates are equal.
    Each ordering is asserted with a gap of more than `3 sqrt(D)`: measured
    27 against 15.6 and 25 against 18.2 calm, 18 against 12.7 and 42 against
    19.4 stressed. Origins of a sliding frame are not independent, so this is
    a threshold for "not a tie", not a significance level.

    **Edges kept, exactly.** On `skewed_frame` with the real boosted fit, with
    `PARTIAL_SCALE_EXPONENT` patched to `0.0` every factor is `1.0` exactly, so
    each candidate is `Q_lo - 1.0 * (s / 1.0)`, bit-identical to
    `cross_conformal`'s, and the band must equal it with `assertEqual`. Both
    fits carry `spread_change_lags=SCALE_WINDOW`: a held-out row with no scale
    is not scored under the partial calibration, and on a hole-free frame that
    is exactly the row whose lags would reach before the frame, so the two
    score the same rows. The fixture's skew is asserted, not assumed: the
    median over the forecast rows of the fitted upper half-width over the
    lower must exceed 1.5, against about 3.6 in the population (`2.3 / 0.64`)
    and 2.1 measured -- a row-by-row check would not hold, since twenty lag
    columns on 400 rows leave single rows' fitted edges noisy.

    **The reference cancels.** `(s_o / ref) ** g / (s_i / ref) ** g = (s_o /
    s_i) ** g` for one `ref` shared by the held-out rows and the forecast,
    which is how this implementation reads it: `_partial_factor` has no
    reference, and the subtest refits and forecasts with it replaced by
    `(s / ref) ** gamma` for three references and compares bands. The
    tolerance is `1e-9` bp: each edge is `Q - f_o (s / f_i)`, three
    floating-point operations on values under 100 bp on this fixture, each
    off by at most a few units in the last place (about `1e-15` relative), so
    the rounding reaches about `1e-13` bp, and an order statistic moves by no
    more than the values it is chosen from. The control applies a reference
    at the forecast alone, which is the non-shared case, and must move the band.

    **The leak.** As B-SCALED's: at a 6-day gap, moving every spread after a
    date must leave the scale of every held-out row whose target is on or
    before it bit-identical, and move a later one; and moving the frame's
    spreads after a forecast's feature row must leave that row's scale and
    band bit-identical, while a spread inside its window moves both.

    Mutation record (B-PARTIAL)
    ---------------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, one sub-copy per mutation,
    `PYTHONDONTWRITEBYTECODE=1`, `python -B` (the `.venv`: CPython 3.9.6,
    numpy 2.0.2, scikit-learn 1.6.1), `PYTHONPATH=src:tests`,
    `REPO_MODEL_REQUIRE_ML=1`, `OMP_NUM_THREADS=1`. Each mutation by
    exact-string replacement in `repo_model/ml.py` whose anchor was found
    exactly once, asserted applied. Unmutated control green before and after.

      1. **`PARTIAL_SCALE_EXPONENT = 1.0`.** `interpolation`,
         `AssertionError`: calm misses 11 / 63 / 63 -- the partial band is the
         scaled one's, a gap of 0. Also the exponent's own assertion
         (`1.0 != 0.5`).
      2. **`PARTIAL_SCALE_EXPONENT = 0.0`.** `interpolation`,
         `AssertionError`: calm 11 / 10 / 63, a gap of -1. **The exponent-zero
         equality subtest passes**, as it must under its own setting. Also
         `AssertionError` in the band rebuild's separation count (`0 != 20`),
         both controls that need a factor to move (the forecast leak's and
         the reference's), and the exponent's own assertion.
      3. **The median for the edges** -- `excluded[0]` and `excluded[-1]`
         replaced by the median in `_reported`'s partial candidates, B-SCALED's
         centring. `edges kept: at an exponent of zero ...`,
         `AssertionError` (lower edge 8.910 against `cross_conformal`'s
         8.321), and the band rebuild, `AssertionError`. Also
         `interpolation` (calm 179 misses) and the forecast leak's control:
         the band collapsed onto the interior, so moving a spread in the
         window no longer moved it.
      4. **The window centred** in `_trailing_scale`. `leak: a held-out row's
         scale ...`, `AssertionError`: block 3's row scored on 2020-05-28
         moved when only spreads after 2020-05-30 did. The forecast leak
         subtest fails too, `AssertionError`, on the rebuilt scale and not on
         the leak, for B-SCALED's reason. `ScaledCrossConformalTests`, scored
         beside it, fails four subtests, `AssertionError`.
      5. **Another calibration routed through the partial path**, two ways:
          - **`cross_conformal`** -- the fitter's `partial` and `trailing` and
            `_reported`'s `partial` widened to take it. `cross_conformal and
            cross_conformal_scaled are unchanged`, `AssertionError` (its
            blocks carry partial scores), and the exponent-zero equality,
            the band rebuild and `interpolation` (a gap of 0), all
            `AssertionError`. Beside it: `ScaledCrossConformalTests`'
            `cross_conformal is unchanged`, `AssertionError`, and
            `GradientBoostedCrossConformalTests` **errors**, `ValueError` (a
            forecast off the frame has no scale).
          - **`cross_conformal_scaled`** -- its own branch in `_reported`
            disabled and both `partial` flags widened to it. `cross_conformal
            and cross_conformal_scaled are unchanged`, `AssertionError`, and
            `interpolation` (calm 38 / 38, a gap of 0). Beside it:
            `ScaledCrossConformalTests`' regime and band subtests,
            `AssertionError`.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All six killed again, on the subtests named above, `AssertionError`.
    Mutation 1 still reads calm 11/63/63.
    """

    NAME = "cross_conformal_partial"
    FRAME_ROWS = 300
    PERIODS = 5
    PURGE = 1
    LEAK_PURGE = 6
    PERTURB_AT = 150
    PERTURB_BPS = 3.0
    #: The skewed fixture's boosted fit: long enough, and with leaves large
    #: enough, that its edges carry the skew through twenty lag columns.
    TRAIN_ROWS = 400
    SKEW_LEAF = 40
    FORECAST_ROWS = 20
    #: The references the cancellation subtest divides every scale by.
    REFERENCES = (0.25, 3.0, 7.0)
    REFERENCE_TOLERANCE_BPS = 1e-9

    def setUp(self):
        require_extra(self)

    def fit(self, frame, regressors, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
            "calibration": self.NAME,
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(frame, regressors, **options)

    def stand_in_fit(self, base, frame, regressors, **overrides):
        with mock.patch.object(ml, "_estimator_class", return_value=base):
            return self.fit(frame, regressors, **overrides)

    @staticmethod
    def edges(band):
        return band[0], band[-1]

    def test_the_partial_band_lies_between_and_keeps_the_fit_edges(self):
        """Interpolation per regime, the fit's own edges, no leak, ref cancels, the others unchanged."""

        with self.subTest("interpolation: each regime's misses lie between cross_conformal's and scaled's"):
            skip_if_fast(self, "a refit at every origin of three regime sweeps")
            count = self.FRAME_ROWS + self.PERIODS * REGIME_ROWS * len(REGIME_PATTERN) + self.PURGE + 1
            rows = with_column(
                regime_frame(count), "regime_sd", [regime_sd(index) for index in range(count)]
            )
            calibrations = ("cross_conformal", self.NAME, "cross_conformal_scaled")
            missed = {name: {CALM_SD: [], STRESSED_SD: []} for name in calibrations}
            for name in calibrations:
                for origin in range(self.FRAME_ROWS - 1, count - self.PURGE - 1):
                    target = origin + self.PURGE + 1
                    if (origin - ml.SCALE_WINDOW) // REGIME_ROWS != target // REGIME_ROWS:
                        continue
                    model = self.stand_in_fit(
                        NarrowRegimeQuantile,
                        rows[origin - self.FRAME_ROWS + 1 : origin + 1],
                        ("regime_sd",),
                        calibration=name,
                        information=gap_rule(self.PURGE),
                    )
                    low, high = self.edges(model.predict(rows[origin]))
                    outcome = rows[target].spread_bps
                    missed[name][regime_sd(target)].append(not low <= outcome <= high)
            partial = missed[self.NAME]
            for sd, label, fewer, more in (
                (CALM_SD, "calm", "cross_conformal", "cross_conformal_scaled"),
                (STRESSED_SD, "stressed", "cross_conformal_scaled", "cross_conformal"),
            ):
                for below, above in ((missed[fewer][sd], partial[sd]), (partial[sd], missed[more][sd])):
                    discordant = sum(one != two for one, two in zip(below, above))
                    gap = sum(above) - sum(below)
                    self.assertGreater(
                        gap,
                        3.0 * math.sqrt(discordant),
                        msg=(
                            f"{label}: misses {fewer} {sum(missed[fewer][sd])}, partial "
                            f"{sum(partial[sd])}, {more} {sum(missed[more][sd])} of "
                            f"{len(partial[sd])}; a gap of {gap} over {discordant} "
                            f"discordant origins is not an ordering"
                        ),
                    )

        rows = skewed_frame(self.TRAIN_ROWS)
        forecasts = rows[-self.FORECAST_ROWS :]
        skewed = {"information": gap_rule(0), "spread_change_lags": ml.SCALE_WINDOW, "min_samples_leaf": self.SKEW_LEAF}
        cross = self.fit(rows, ("on_rrp",), calibration="cross_conformal", **skewed)
        partial = self.fit(rows, ("on_rrp",), **skewed)

        with self.subTest("edges kept: at an exponent of zero the band is cross_conformal's exactly"):
            with mock.patch.object(ml, "PARTIAL_SCALE_EXPONENT", 0.0):
                flat = self.fit(rows, ("on_rrp",), **skewed)
                bands = [flat.predict(row) for row in forecasts]
            for block, other in zip(flat.calibration_blocks, cross.calibration_blocks):
                self.assertEqual(block.scored_dates, other.scored_dates)
                self.assertEqual(block.partial_scores, other.scores)
            ratios = []
            for row, band in zip(forecasts, bands):
                self.assertEqual(band, cross.predict(row), msg=f"the band forecast from {row.date}")
                fitted = cross._quantile_vector(cross.design_row(row))
                ratios.append((fitted[-1] - fitted[2]) / (fitted[2] - fitted[0]))
            self.assertGreater(
                sorted(ratios)[len(ratios) // 2],
                1.5,
                msg="the fixture: the fitted edges are not right-skewed about the median",
            )

        with self.subTest("edges kept: the band is CV+'s over each model's own edges and the scaled score"):
            model = partial
            q = Fraction("0.95") - Fraction("0.05")
            count = sum(len(block.partial_scores) for block in model.calibration_blocks)
            low_rank = math.floor((1 - q) * (count + 1))
            high_rank = math.ceil(q * (count + 1))
            for block, other in zip(model.calibration_blocks, cross.calibration_blocks):
                self.assertEqual(
                    list(block.partial_scores),
                    [
                        score / scale ** ml.PARTIAL_SCALE_EXPONENT
                        for score, scale in zip(other.scores, block.scales)
                    ],
                )
            separated = 0
            for row in forecasts:
                factor = model._origin_scale(row) ** ml.PARTIAL_SCALE_EXPONENT
                lows, highs = [], []
                for block in model.calibration_blocks:
                    read = ml._rearranged(
                        block.estimators,
                        [model._design_row(row, block.imputations, None, None, None)],
                    )[0]
                    lows.extend(read[0] - factor * score for score in block.partial_scores)
                    highs.extend(read[-1] + factor * score for score in block.partial_scores)
                fitted = model._quantile_vector(model.design_row(row))
                reported = model.predict(row)
                self.assertEqual(reported[1:-1], fitted[1:-1])
                self.assertEqual(
                    self.edges(reported),
                    (
                        min(sorted(lows)[low_rank - 1], fitted[1]),
                        max(sorted(highs)[high_rank - 1], fitted[-2]),
                    ),
                    msg=f"the band forecast from {row.date} is not partial CV+'s",
                )
                separated += self.edges(reported) != self.edges(cross.predict(row))
            self.assertEqual(separated, len(forecasts))

        with self.subTest("leak: a held-out row's scale reads nothing after its feature row"):
            frame = regime_frame(self.FRAME_ROWS)
            moved = ScaledCrossConformalTests.perturbed(frame, self.PERTURB_AT, self.PERTURB_BPS)
            opens = frame[self.PERTURB_AT].date
            before = self.stand_in_fit(ConstantQuantile, frame, ("sofr_volume",), information=gap_rule(self.LEAK_PURGE))
            after = self.stand_in_fit(ConstantQuantile, moved, ("sofr_volume",), information=gap_rule(self.LEAK_PURGE))
            checked = changed = 0
            for number, (one, two) in enumerate(
                zip(before.calibration_blocks, after.calibration_blocks), start=1
            ):
                self.assertEqual(one.scored_dates, two.scored_dates)
                self.assertEqual(len(one.scales), len(one.partial_scores))
                for when, left, right in zip(one.scored_dates, one.scales, two.scales):
                    if when <= opens:
                        checked += 1
                        self.assertEqual(
                            left,
                            right,
                            msg=(
                                f"block {number}: the scale of the row scored on {when} "
                                f"moved when only spreads after {opens} did"
                            ),
                        )
                    else:
                        changed += left != right
            self.assertGreater(checked, 100)
            self.assertGreater(changed, 0, msg="the control: no scale moved at all")

        with self.subTest("leak: a forecast's factor and band read nothing after its decision"):
            frame = regime_frame(self.FRAME_ROWS)
            model = self.stand_in_fit(ConstantQuantile, frame, ("sofr_volume",), information=gap_rule(self.LEAK_PURGE))
            row = frame[self.PERTURB_AT]
            scale, band = model._origin_scale(row), model.predict(row)
            self.assertEqual(scale, ScaledCrossConformalTests.rms_scale(frame, self.PERTURB_AT))
            history = model._history_spreads
            model._history_spreads = history[: self.PERTURB_AT + 1] + tuple(
                spread + self.PERTURB_BPS for spread in history[self.PERTURB_AT + 1 :]
            )
            self.assertEqual((model._origin_scale(row), model.predict(row)), (scale, band))
            model._history_spreads = (
                history[: self.PERTURB_AT - 3]
                + (history[self.PERTURB_AT - 3] + self.PERTURB_BPS,)
                + history[self.PERTURB_AT - 2 :]
            )
            self.assertNotEqual(model._origin_scale(row), scale)
            self.assertNotEqual(model.predict(row), band)

        with self.subTest("ref cancels: one reference shared by the scores and the forecast moves no band"):
            frame = regime_frame(self.FRAME_ROWS)
            points = frame[-self.FORECAST_ROWS :]
            model = self.stand_in_fit(ConstantQuantile, frame, ("sofr_volume",), information=gap_rule(self.PURGE))
            bands = [model.predict(row) for row in points]
            original = ml._partial_factor
            for reference in self.REFERENCES:
                def referenced(scale, reference=reference):
                    return (scale / reference) ** ml.PARTIAL_SCALE_EXPONENT

                with mock.patch.object(ml, "_partial_factor", referenced):
                    other = self.stand_in_fit(ConstantQuantile, frame, ("sofr_volume",), information=gap_rule(self.PURGE))
                    moved = [other.predict(row) for row in points]
                for row, one, two in zip(points, bands, moved):
                    for left, right in zip(self.edges(one), self.edges(two)):
                        self.assertAlmostEqual(
                            left, right, delta=self.REFERENCE_TOLERANCE_BPS,
                            msg=f"ref {reference} moved the band forecast from {row.date}",
                        )
            # The control: a reference at the forecast alone does not cancel.
            with mock.patch.object(ml, "_partial_factor", lambda scale: original(scale / 4.0)):
                unshared = [model.predict(row) for row in points]
            self.assertTrue(
                all(self.edges(one) != self.edges(two) for one, two in zip(bands, unshared))
            )

        with self.subTest("cross_conformal and cross_conformal_scaled are unchanged"):
            frame = regime_frame(self.FRAME_ROWS)
            points = frame[-self.FORECAST_ROWS :]
            scaled = self.stand_in_fit(
                ConstantQuantile, frame, ("sofr_volume",),
                calibration="cross_conformal_scaled", information=gap_rule(self.PURGE),
            )
            plain = self.stand_in_fit(
                ConstantQuantile, frame, ("sofr_volume",),
                calibration="cross_conformal", information=gap_rule(self.PURGE),
            )
            q = Fraction("0.95") - Fraction("0.05")
            for model, reads in ((plain, "scores"), (scaled, "scaled_residuals")):
                blocks = model.calibration_blocks
                for block in blocks:
                    self.assertEqual(block.partial_scores, ())
                self.assertEqual(
                    [block.scales == () for block in blocks],
                    [model is plain] * len(blocks),
                )
                count = sum(len(getattr(block, reads)) for block in blocks)
                low_rank = math.floor((1 - q) * (count + 1))
                high_rank = math.ceil(q * (count + 1))
                for row in points:
                    lows, highs = [], []
                    for block in blocks:
                        read = ml._rearranged(
                            block.estimators,
                            [model._design_row(row, block.imputations, None, None, None)],
                        )[0]
                        if model is plain:
                            lows.extend(read[0] - score for score in block.scores)
                            highs.extend(read[-1] + score for score in block.scores)
                        else:
                            scale = model._origin_scale(row)
                            lows.extend(read[2] - scale * score for score in block.scaled_residuals)
                            highs.extend(read[2] + scale * score for score in block.scaled_residuals)
                    fitted = model._quantile_vector(model.design_row(row))
                    self.assertEqual(
                        self.edges(model.predict(row)),
                        (
                            min(sorted(lows)[low_rank - 1], fitted[1]),
                            max(sorted(highs)[high_rank - 1], fitted[-2]),
                        ),
                        msg=f"{model.calibration}'s band forecast from {row.date} changed",
                    )

        with self.subTest("the declaration, the exponent, and the command line reaching it"):
            self.assertEqual(ml.PARTIAL_SCALE_EXPONENT, 0.5)
            self.assertEqual(ml.CALIBRATIONS[-1], self.NAME)
            self.assertEqual(
                dict(partial.model_settings),
                {"calibration": self.NAME, "calibration_folds": 5, "spread_change_lags": ml.SCALE_WINDOW},
            )
            backtest = cli.build_parser().parse_args(
                ["backtest", "panel.csv", "--registry", "registry.json",
                 "--decision-time", DECISION_TIME, "--report", "r.json",
                 "--feature", "spread_bps", "--model", "gbm",
                 "--calibration", self.NAME]
            )
            _, fitter = cli_eval._select_fitter(backtest)
            self.assertEqual(fitter.keywords, {"regressors": (), "calibration": self.NAME})

        with self.subTest("refusals: a tail, a share, too few scores, a forecast with no scale"):
            with self.assertRaisesRegex(ValueError, r"not wired for calibration 'cross_conformal_partial'"):
                self.fit(rows[:120], ("on_rrp",), information=gap_rule(0), tail="gpd")
            with self.assertRaisesRegex(
                ValueError, r"calibration_share 0.25 was given, but calibration 'cross_conformal_partial'"
            ):
                self.fit(rows[:40], ("on_rrp",), calibration_share=0.25, information=gap_rule(0))
            with self.assertRaisesRegex(
                ValueError, r"cross_conformal_partial calibration needs at least 9 held-out scores, got 8"
            ):
                self.fit(rows[:29], ("on_rrp",), calibration_folds=2, information=gap_rule(0))
            early = self.stand_in_fit(
                ConstantQuantile, regime_frame(self.FRAME_ROWS), ("sofr_volume",), information=gap_rule(self.PURGE)
            )
            with self.assertRaisesRegex(
                ValueError, r"has no scale: calibration 'cross_conformal_partial'"
            ):
                early.predict(regime_frame(self.FRAME_ROWS)[10])


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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All seven killed again, on this class's subtests, `AssertionError`.
    Mutation 1 was applied as `train_frame = rows[: index + 1]`; the record's
    failures elsewhere in the suite were not re-counted.
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
        fewer_boosting_iterations(self)
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

        def fitter(train_frame, minimum_history, information):
            model = self.fit(
                train_frame,
                minimum_history=minimum_history,
                information=information,
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
            information=gap_rule(0),
        )
        cross_frame = arx_frame(self.CROSS_ROWS)
        cross = self.fit(
            cross_frame,
            arx_feature="declared",
            calibration="cross_conformal",
            information=gap_rule(self.PURGE),
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
            self.assertLess(
                dates.index(fold.feature_date),
                dates.index(fold.scored_date) - 1,
                msg="the feature row is the row before the scored day, so the "
                "gap between them is not under test",
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
                information=gap_rule(0),
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
                    information=gap_rule(0),
                ).widening,
                calibrated.widening,
                msg="the control: the widening does not read the calibration rows' ARX column",
            )

        with self.subTest("each block model's ARX is fitted without its block and purge gaps"):
            rows = cross_frame
            cross_dates = [row.date for row in rows]
            # The rule the fit was handed: label observability on this frame.
            rule = gap_rule(self.PURGE)

            def anchor(index):
                return rule.anchor(cross_dates, index) if index > 0 else -1

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
                    start = cross_dates.index(block.held_out_start)
                    end = cross_dates.index(block.held_out_end)
                    kept = [
                        p <= anchor(start) if p < start else p > end and anchor(p) >= end
                        for p in range(len(cross_dates))
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
                        position = anchor(index)
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
                    information=gap_rule(self.PURGE),
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
            while anchor(clear) < stop:
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
                         calibration_share=0.5, information=gap_rule(0))
            # And twenty is enough: the refusal sits at the edge.
            edge = self.fit(panel[:40], arx_feature="declared", calibration="conformal",
                            calibration_share=0.5, information=gap_rule(0))
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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All four killed again, `AssertionError`. Mutation 3's conformance
    siblings were not re-run.
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
    rather than discovering them absent. (The lower end is a floor at zero
    since #63, held by `TailShapeFloorTests`. A floored fit keeps the identity,
    `sigma = a_0` at `xi = 0`.)

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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). Mutations 2 and 3 killed again, `AssertionError`. 1 and 4 were not
    re-run: a recorded survivor and a planted control.
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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). Mutations 1 to 3 killed again, `AssertionError`; 2 still on the one
    subtest, at a margin of 0.00034. 4 kills `FittedTailPwmTests`, as recorded, and
    was not re-run here.

    The floor (#63)
    ---------------

    Since #63 a negative shape is floored at zero, so the two bounded rows no
    longer come back as `xi`. The estimator's raw shape is kept as
    `xi_estimate`, and that is what those rows recover, at the same tolerance.
    Their scale is the floor's, the sample's mean excess, and that is asserted
    instead of the declared `sigma`. The `a_1` limb is still read on every row:
    through `xi_estimate` on the bounded rows, and through `xi` and `sigma` on
    the other three. Mutations 1 to 3 were re-run against this version, as
    recorded in the PR for #63. All three killed again, `AssertionError`. The
    bounded rows now fail on `xi_estimate`, and the heavy rows on `sigma`, as
    before. Mutation 2 still fails on the `xi = 0.4` row's `sigma` alone.
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
        `RELATIVE_SCALE_TOLERANCE` of the declared values. A declared negative
        shape is floored (#63): its raw estimate, `xi_estimate`, is what is
        recovered, and its scale is the sample's mean excess.
        """

        for xi, sigma in self.DECLARED:
            with self.subTest(xi=xi, sigma=sigma):
                sample = self._sample(xi, sigma)
                fit = ml._fit_gpd_pwm(list(reversed(sample)))
                self.assertFalse(fit.clamped)
                self.assertFalse(fit.fallback)
                self.assertEqual(fit.floored, xi < 0.0)
                if fit.floored:
                    self.assertEqual(fit.xi, 0.0)
                    self.assertEqual(fit.sigma, math.fsum(sorted(sample)) / len(sample))
                    self.assertLessEqual(
                        abs(fit.xi_estimate - xi),
                        self.SHAPE_TOLERANCE,
                        msg=f"raw xi {fit.xi_estimate!r} is not the declared "
                        f"{xi!r}; the estimator weights the order statistics "
                        "differently from the plotting positions the law was "
                        "sampled at",
                    )
                    continue
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
    `0.7` leaves 840 calibration rows and a fitted, unclamped, non-fallback
    shape --- more than `GPD_MINIMUM_EXCESSES` excesses, with margin, so the
    `xi != 0` branch of the survival function is what is read. The shape must
    also be positive, an unbounded tail, or part 3 has nothing to read: a
    negative shape puts the tail's ceiling `sigma / -xi` above the threshold,
    and beyond it the tail is `0.0` as the default is.

    **Why `0.7` (#55).** The share was `0.6` until scikit-learn moved from
    1.6.1 to 1.9.1. The sign of a shape fitted on some thirty excesses is not
    something the wiring controls, and it moved with the fitter: on this frame
    at `0.6` the fit went from `xi` about `0.040` to `-0.136`, a ceiling `0.6` bp
    above the top knot, so part 3 read `1.1e-11` at the knot and `0.0` ten bp
    past it. At `0.7` under 1.9.1 it is `0.112` on 29 excesses. The positive
    shape is asserted in the first subtest, so a fitter that flips it again
    fails there, on the premise, and not as a missing tail in part 3. The
    figures quoted in the mutation record below are the `0.6` fixture's under
    1.6.1, as recorded; the re-run under 1.9.1 is recorded after it. A 36-row frame
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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). On the `0.7` fixture: mutations 1 to 7 each killed again,
    `AssertionError`, on the subtests named above (1: parts 2 and 3; 2: part 2; 3a:
    parts 1 and 2; 3b: the sample and no-excess subtests; 4 to 6: part 5; 7: the
    no-excess subtest). 8 and 9 kill other classes and were not re-run here. 10
    cannot be re-run as written: the calibration loop no longer has a local to
    rename. Inserting `tail = range(...)` in that loop instead failed the
    recorded-fit subtest with the record's `range(1198, 1199) != 'gpd'`, on the
    `0.6` fixture.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    ROWS = 1200
    SHARE = 0.7

    def setUp(self):
        require_extra(self)

    def fit(self, frame, **overrides):
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
            "calibration": "conformal",
            "information": gap_rule(0),
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


class GpdCrossConformalSampleTests(unittest.TestCase):
    """B53: the fitted tail stays refused under `cross_conformal`, and why.

    **The question.** The model work moves to `cross_conformal`, and the tail
    was refused there. B53 was to wire it if a coherent sample exists, and to
    say so with its reasoning if not. It does not; see the module docstring of
    `repo_model.ml`, "Why `cross_conformal` cannot simply be wired".

    **What the refusal rests on, checked on a fit.** `conformal`'s sample is
    coherent because one map, fitted on no calibration row, both measures the
    excesses and carries the knot. Under CV+ the knot is the upper edge, read
    off every excluding model at the forecast's row. So the refusal rests on
    one fact about the fitted blocks: at a held-out row's feature row, every
    other block's excluding model --- unless that block holds the feature row
    itself --- was fitted on that row's pair. If that ever stopped being true
    the reason would have moved, and this test says so before a later block
    wires on a premise that has gone.

    The fixture has no lags and no purge, so a block's model trains on exactly
    the rows outside it, a pair of consecutive such rows is one of its training
    pairs, and a held-out row's feature row is the row before it.
    `training_dates` is read for both dates of the pair, and the block's own
    held-out range for neither.

    **One criterion, two clauses:** the refusal is raised on the calibration's
    name, and the premise holds.

    Mutation record
    ---------------

    Run in disposable copies under `$HOME`, one per mutation plus an unmutated
    control, each built from `git ls-files -z --cached --others
    --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, whole suite per run in
    one process, on CPython 3.9.6 with numpy 2.0.2 and scikit-learn 1.6.1
    through the mount's `.venv/bin/python`; `repo_model` confirmed to resolve
    to the copy's `src/`. Unmutated control green before and after, zero
    `expectedFailure`. Each target was found exactly once as an exact substring
    and the replacement confirmed present and the original gone.

    1. **The refusal, by name** --- `calibration == "cross_conformal"` ->
       `calibration == "cross_conformal_unwired"` in the fitter's tail
       refusal. Kills the refusal subtest here and `GpdTailWiringTests` part 5,
       both `AssertionError: ValueError not raised`, and nothing else.
    2. **The premise, by operator** --- in the cross-conformal block plan,
       `position >= stop` -> `position > stop`, so an excluding model no longer
       trains on the first row after its block. Kills the premise subtest here
       alone, `AssertionError`: block 1 did not train on the feature row of
       block 2's first scored row. **Nothing else in the suite sees it**,
       `GradientBoostedCrossConformalTests` included: that class holds that
       no excluding model trains *inside* its block and purge gaps, and this
       mutation only trains on less. It is the safe direction --- no leak ---
       which is why it went unguarded, and it is recorded here as found.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). Both killed again, `AssertionError`, on the subtests named above.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    ROWS = 60

    def setUp(self):
        require_extra(self)

    def test_the_cross_conformal_edge_reads_models_fitted_on_every_held_out_row_so_the_tail_stays_refused(
        self,
    ):
        """The refusal stands, and every held-out row is in-sample to the CV+ edge."""

        rows = heteroscedastic_frame(self.ROWS)
        options = {
            "minimum_history": 20,
            "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF,
            "calibration": "cross_conformal",
            "information": gap_rule(0),
        }

        with self.subTest("the refusal, on the calibration's name"):
            with self.assertRaises(ValueError) as caught:
                ml.fit_gradient_boosted_quantiles(rows, self.REGRESSORS, tail="gpd", **options)
            self.assertIn("not wired for calibration 'cross_conformal'", str(caught.exception))

        fit = ml.fit_gradient_boosted_quantiles(rows, self.REGRESSORS, **options)
        blocks = fit.calibration_blocks
        dates = [row.date for row in rows]
        scored = 0
        with self.subTest("every held-out row's pair trains every other block's model"):
            for number, block in enumerate(blocks):
                for when in block.scored_dates:
                    scored += 1
                    feature = dates[dates.index(when) - 1]
                    trained_on_it = 0
                    for other_number, other in enumerate(blocks):
                        if other_number == number:
                            self.assertNotIn(
                                when,
                                other.training_dates,
                                msg=f"block {number + 1} trained on its own row {when}",
                            )
                            continue
                        if other.held_out_start <= feature <= other.held_out_end:
                            continue
                        self.assertIn(
                            feature,
                            other.training_dates,
                            msg=f"block {other_number + 1} did not train on {feature}, "
                            f"the feature row of block {number + 1}'s held-out {when}",
                        )
                        self.assertIn(
                            when,
                            other.training_dates,
                            msg=f"block {other_number + 1} did not train on {when}, "
                            f"held out by block {number + 1}",
                        )
                        trained_on_it += 1
                    expected = len(blocks) - 1 - (feature < block.held_out_start)
                    self.assertEqual(trained_on_it, expected, msg=f"held-out {when}")
            # Every row but the frame's first has a feature row, so is scored.
            self.assertEqual(scored, len(rows) - 1)


class TailShapeFloorTests(unittest.TestCase):
    """A negative fitted shape is floored at zero, and the record says so (#63).

    **The ruling.** Eleonora, 1 October 2026, on #63: repo pressure has no
    hard ceiling, and the Standing Repo Facility is a soft cap, not a bound.
    So the fitted GPD shape is non-negative: a negative fit is treated as zero,
    and the tail never assigns probability zero above a level.
    `docs/decisions/tail-shape-floor.md` records it.

    **Why the sign needed a rule.** On about thirty excesses the PWM shape
    changes sign with the scikit-learn version (#63's table). A negative shape
    puts a hard ceiling `sigma / -xi` above the threshold, so a fold's ceiling
    turned on a fitter's version as much as on the data.

    **Replaces `TailLowerBoundRefusalTests` (B44).** That class held a shape
    at or below `-0.5` refused, falling back to the exponential, and recorded
    as `refused`, while a negative shape inside `(-0.5, 0)` was kept with its
    ceiling. The floor takes in both cases, so the refusal and that class's
    parts 1 and 4 have nothing left to hold. Its part 2, the upper clamp kept,
    is part 3 here, unchanged. Its part 3, a negative interior shape kept, is
    the opposite of the ruling and is part 1 here, inverted.

    **What is asserted.**
    1. A raw shape inside `(-0.5, 0)` and one at or below `-0.5` are each
       floored: `xi == 0.0`, `sigma == a_0` (the sample's mean excess), the raw
       estimate kept as `xi_estimate`, and the law is the exponential, positive
       however far out it is read.
    2. The record spells a floored fit as its own state, `floored`. It carries
       `sigma`, `excesses` and `xi_estimate`, and no `xi` and no
       `upper_endpoint_excess`.
    3. The upper clamp at `0.5` is kept and is not a floor.
    4. `refused` stays in `TAIL_STATES`, so the published records that carry
       it still read.

    The raw estimate is recomputed here from the estimator's own formulas,
    with the `0.35` offset as a literal. No `require_extra`: these are sorts
    and sums, and the model is built directly.

    Written first and watched failing, on the tree before #63: parts 1 and 3
    raised `AttributeError` (no `floored`), part 2 failed on a `fitted` and a
    `refused` account, and part 4 on the states.

    Mutation record (#63)
    ---------------------

    Run in a disposable copy from `git ls-files -z --cached --others
    --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, on CPython 3.11.15
    with numpy 2.4.6 and scikit-learn 1.9.1. This class and
    `ExceedanceTailFloorTests` were run against an unmutated control, green.
    The target was found exactly once and confirmed applied by diff.

    1. **The floor off**: `if xi < lower:` -> `if False:` in `_fit_gpd_pwm`.
       Part 1 fails with `AssertionError` (`False is not true` on `floored`).
       Part 2 raises `ValueError` from `tail_account`, which refuses the
       unfloored negative shape. `ExceedanceTailFloorTests` raises the same
       `ValueError` on the fixture's first negative fold.
    """

    #: Evenly spaced excesses: bounded above, and the PWM shape of a bounded
    #: sample is well below `-0.5` (a uniform law has `xi = -1`). Not sorted;
    #: the estimator sorts.
    BOUNDED = tuple(0.25 * k for k in range(24, 0, -1))

    @staticmethod
    def raw_shape(sample):
        """The PWM shape before any floor or clamp, as `_fit_gpd_pwm` forms it."""

        ordered = sorted(float(value) for value in sample)
        count = len(ordered)
        a_0 = math.fsum(ordered) / count
        a_1 = (
            math.fsum(
                value * (1.0 - (rank - 0.35) / count)
                for rank, value in enumerate(ordered, start=1)
            )
            / count
        )
        return 2.0 - a_0 / (a_0 - 2.0 * a_1)

    def samples(self):
        """`(name, sample)`: a raw shape inside `(-0.5, 0)`, and one at or below `-0.5`."""

        return (
            ("inside", tuple(GpdRecoveryTests()._sample(-0.2, 1.5))),
            ("at or below -0.5", self.BOUNDED),
        )

    def test_a_negative_shape_is_floored_at_zero_and_recorded_as_floored(self):
        """Every negative shape floored to the exponential; the upper clamp kept."""

        for name, sample in self.samples():
            raw = self.raw_shape(sample)
            mean = math.fsum(sorted(sample)) / len(sample)
            fit = ml._fit_gpd_pwm(sample)

            with self.subTest("1. floored", sample=name):
                self.assertLess(raw, 0.0)
                if name == "inside":
                    self.assertGreater(raw, -0.5)
                else:
                    self.assertLessEqual(raw, -0.5)
                self.assertTrue(fit.floored)
                self.assertEqual(fit.xi, 0.0)
                self.assertEqual(fit.sigma, mean)
                self.assertEqual(fit.xi_estimate, raw)
                self.assertEqual(fit.excesses, len(sample))
                self.assertFalse(fit.fallback)
                self.assertFalse(fit.clamped)
                for far in (max(sample), 10.0 * max(sample), 100.0 * fit.sigma):
                    self.assertEqual(
                        ml._gpd_survival(fit, far), math.exp(-far / fit.sigma)
                    )
                    self.assertGreater(ml._gpd_survival(fit, far), 0.0)

            with self.subTest("2. recorded as floored", sample=name):
                self.assertEqual(
                    TailCeilingTests.account_of(fit),
                    {
                        "state": "floored",
                        "sigma": mean,
                        "excesses": len(sample),
                        "xi_estimate": raw,
                    },
                )

        with self.subTest("3. the upper clamp is kept, not floored"):
            heavy = ml._fit_gpd_pwm(FittedTailPwmTests.CLAMPING)
            self.assertFalse(heavy.floored)
            self.assertIsNone(heavy.xi_estimate)
            self.assertFalse(heavy.fallback)
            self.assertTrue(heavy.clamped)
            self.assertEqual(heavy.xi, ml.GPD_SHAPE_BOUNDS[1])
            self.assertEqual(TailCeilingTests.account_of(heavy)["state"], "fitted")

        with self.subTest("4. the states a reader knows"):
            self.assertEqual(
                set(ml.TAIL_STATES),
                {"fitted", "fallback", "no_excesses", "floored", "refused"},
            )
            self.assertEqual(ml.GPD_SHAPE_BOUNDS[0], 0.0)


class ExceedanceTailFloorTests(unittest.TestCase):
    """A floored fold's exceedance curve is positive at every tau (#63).

    `TailAccountTests`' panel through `rolling_exceedance_backtest` with
    `gbm_exceedance(tail="gpd")`, as `ExceedanceTailAccountTests` runs it, at
    the declared taus plus two far above every fold's top knot. That fixture's
    lower-clamped folds used to be `refused`, and one of its fitted folds had
    an interior negative shape with a ceiling. Both are floored now.

    **What is asserted.** Some fold is floored. Its record entry is `floored`,
    with a negative `xi_estimate` and no `xi`, and no entry anywhere carries
    `upper_endpoint_excess`. Every fold that has a fitted tail (fitted,
    floored or fallback) gives strictly positive probability at every tau,
    the far ones included. A `no_excesses` fold has no tail, keeps the default
    law, and is left out of that check.

    Written first and watched failing, on the tree before #63. Part 1 failed
    because no fold was floored. Part 2 failed with `0.0 not greater than 0.0`
    at 1000 bp on 2021-07-21, a `fitted` fold whose shape was about `-0.216`
    and whose ceiling sat below that tau.
    """

    #: Far above the top knot of every fold of this fixture, whose spikes run
    #: from 150 bp. Not so far that `exp(-x / sigma)` underflows on a scale of
    #: tens of basis points.
    FAR = (1000.0, 2000.0)

    def setUp(self):
        require_extra(self)
        self.case = ExceedanceTailAccountTests(
            "test_an_exceedance_run_with_a_tail_records_what_its_tail_was_at_every_fold"
        )
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.case.taus = tuple(self.case.taus) + self.FAR

    def test_a_floored_fold_assigns_positive_probability_at_every_tau(self):
        case = self.case
        report, document, _ = case.exceedance(case.frame(), case.gbm(tail="gpd"))
        entries = document["folds"]["tail"]
        floored = [entry for entry in entries if entry["state"] == "floored"]

        with self.subTest("1. floored folds, recorded as floored"):
            self.assertTrue(floored)
            for entry in floored:
                self.assertEqual(
                    set(entry),
                    {"scored_date", "state", "sigma", "excesses", "xi_estimate"},
                )
                self.assertLess(entry["xi_estimate"], 0.0)
                self.assertGreaterEqual(entry["excesses"], ml.GPD_MINIMUM_EXCESSES)
            for entry in entries:
                self.assertNotIn("upper_endpoint_excess", entry)
                self.assertNotEqual(entry["state"], "refused")
                if entry["state"] == "fitted":
                    self.assertGreaterEqual(entry["xi"], 0.0)

        with self.subTest("2. no zero at any tau on a fold with a tail"):
            self.assertEqual(document["declaration"]["taus_bp"][-2:], list(self.FAR))
            for entry, curve in zip(entries, report.forecast):
                if entry["state"] == "no_excesses":
                    continue
                for tau, probability in zip(case.taus, curve):
                    self.assertGreater(
                        probability,
                        0.0,
                        msg=f"{entry['scored_date']} ({entry['state']}) at {tau} bp",
                    )


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
    `TailAccountTests` holds that, and `ExceedanceTailAccountTests` holds the
    same account on an `exceedance-backtest` record (B40).

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
            "information": gap_rule(0),
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
                            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF, information=gap_rule(0))
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
    * **fitted** -- the rest. The first few were **clamped** at the lower
      bound (few excesses whose spread is small against the dip-set widening),
      and once the spikes begin to set the widening themselves the later ones
      are not.
    * **refused** (B44) -- those lower-clamped fits. Since B44 a shape at the
      lower end of `ml.GPD_SHAPE_BOUNDS` is refused and falls back, so this
      fixture shows four states and no fitted fold at `xi = -0.5`. Part 2 used
      to assert that the fitted folds carried both `clamped` values; on this
      fixture every clamp was at the lower end, so that assertion became
      "some fold is refused and no fitted fold sits at the bound". The upper
      clamp has no end-to-end fold here; `TailShapeFloorTests` holds it
      on a committed sample.
    * **floored** (#63) -- since the floor, every negative shape: those
      lower-clamped fits and the interior negative ones. The fixture still
      shows four states, now `floored` in place of `refused`, and the last
      fold is floored, not fitted. Part 2 was rewritten to the ruling: the
      states are the four a fit makes now (`refused` is a published records'
      state only), and no fitted fold has a negative shape.

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

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All four killed again, `AssertionError`. Fit counts read 58 against
    29 where the record has 52 against 26: the fixture carries more folds now.
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
        fewer_boosting_iterations(self)
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

        def fitter(train_frame, minimum_history, information):
            model = ml.fit_gradient_boosted_quantiles(
                train_frame,
                self.REGRESSORS,
                minimum_history=minimum_history,
                min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
                calibration="conformal",
                calibration_share=self.SHARE,
                information=information,
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
        if fit.floored:
            return {
                "state": "floored",
                "sigma": fit.sigma,
                "excesses": fit.excesses,
                "xi_estimate": fit.xi_estimate,
            }
        if fit.fallback:
            return {"state": "fallback", "sigma": fit.sigma, "excesses": fit.excesses}
        # No `upper_endpoint_excess` since the floor (#63): a fitted shape is
        # never negative. `TailCeilingTests` holds that.
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

        with self.subTest("2. the four states are told apart"):
            states = [entry["state"] for entry in entries]
            self.assertEqual(states[0], "no_excesses")
            self.assertEqual(
                set(states), {"no_excesses", "fallback", "fitted", "floored"}
            )
            fallbacks = [entry for entry in entries if entry["state"] == "fallback"]
            self.assertEqual(
                sorted(entry["excesses"] for entry in fallbacks),
                list(range(1, ml.GPD_MINIMUM_EXCESSES)),
            )
            for entry in fallbacks:
                self.assertNotIn("xi", entry)
            fitted = [entry for entry in entries if entry["state"] == "fitted"]
            self.assertTrue(all(e["excesses"] >= ml.GPD_MINIMUM_EXCESSES for e in fitted))
            self.assertTrue(all(entry["xi"] >= 0.0 for entry in fitted))
            floored = [entry for entry in entries if entry["state"] == "floored"]
            for entry in floored:
                self.assertEqual(
                    set(entry),
                    {"scored_date", "state", "sigma", "excesses", "xi_estimate"},
                )
                self.assertLess(entry["xi_estimate"], 0.0)
                self.assertGreaterEqual(entry["excesses"], ml.GPD_MINIMUM_EXCESSES)

        with self.subTest("3. without a tail, nothing, and the rest unchanged"):
            self.assertIsNone(plain_report.tail_accounts)
            self.assertNotIn("tail", plain_document["folds"])
            self.assertEqual(set(plain_document["folds"]), {"count", "first", "last"})
            self.assertNotIn("tail", plain_document["declaration"])
            stripped = json.loads(json.dumps(document))
            del stripped["declaration"]["tail"]
            del stripped["folds"]["tail"]
            self.assertEqual(json.loads(json.dumps(plain_document)), stripped)


class ExceedanceTailTests(unittest.TestCase):
    """`exceedance-backtest --model gbm --calibration conformal --tail gpd` (B39).

    **The defect.** Job 350 scored gbm+conformal against gbm+conformal+`--tail
    gpd` with `backtest` and `compare`, and every metric was bit-identical: those
    commands score the quantile vector, which the tail by design never moves.
    The command that scores what the tail moves -- the exceedance curve -- is
    `exceedance-backtest`, and it took no `--calibration` and no `--tail`, and
    `ml.gbm_exceedance` took neither. The tail was unmeasurable by every
    instrument that could be pointed at it.

    **What had to reach the fit, and what was in the way.** The settings, through
    `_select_fitter`'s own resolvers `_calibration` and `_tail` -- and the purge
    gap, which no exceedance predictor was ever handed:
    `rolling_exceedance_backtest` called `predictor(train, feature, taus)`, and a
    conformal fit refuses a defaulted gap. The fold loop now hands the derived
    gap to a predictor that names `purge_days`, by `baseline._reads_purge_days`,
    the rule `backtest`'s loop already follows.

    **The trap is a flag that parses.** So part 2 reads the curves the run
    scored, at every fold: above the reported top declared quantile they differ,
    and where the untailed run is exactly zero the tailed run is not.

    **How the fixture forces it.** A weekday panel of `10 +/- 1` bp, with three
    rows at 35 bp placed inside every fold's calibration rows and outside its fit
    rows, at a calibration share of one half. The spikes are too few to set the
    conformal widening, so each exceeds its calibrated top quantile and every
    fold's tail is fitted on excesses (a fallback shape; the state does not
    matter here, `TailAccountTests` holds the states). The fit rows' residuals
    are small, so the untailed law's top knot sits below 20 bp and it is
    exactly zero at 20 and 50; 5 and 10 sit below the top quantile. Which taus
    fall on which side is computed per fold from the fit, not assumed.

    **Part 4's comparison is against this base's predictor**, written out here
    as `gbm_exceedance` stood before B39: fitted with the fitter's defaults, no
    gap handed over, no settings on the curves. A run asking for neither
    setting must publish that record key for key.

    Mutation record
    ---------------

    Run in a disposable copy per mutation plus an unmutated control under
    `$HOME`, each built from `git ls-files -z --cached --others
    --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, whole suite per run, on
    CPython 3.9.6 with numpy 2.0.2 and scikit-learn 1.6.1 through the mount's
    `.venv/bin/python` by absolute path; `repo_model` confirmed to resolve to
    the copy's `src/`. Unmutated control green before and after, zero
    `expectedFailure`. Each target was counted as an exact substring in Python
    and found exactly once. Every failure is `AssertionError`.

    1. **The tail dropped between resolution and the fit** --- `tail=tail,`
       removed from `gbm_exceedance`'s call to the fitter. Kills **part 2**
       (`0.0 == 0.0` above the top quantile) **and part 1 too** (`None !=
       'gpd'` on the fit's keywords, then no `tail_fit`): part 1 reads the fit,
       and a tail that never reached it is absent there. The brief expected part
       2 alone; part 1 cannot stay green over this defect, because what it
       checks is exactly the fit this drops the tail before.
    2. **The same, one step earlier** --- `**settings` dropped from
       `MODEL_FACTORIES["gbm"].build`, so `_calibration` and `_tail` resolve and
       refuse and nothing is bound. Parts 1 and 2, as mutation 1 (`None !=
       'gpd'`; `0.0327 == 0.0327`, both runs uncalibrated). This is the trap: a
       flag that parses.
    3. **The calibration dropped** --- `calibration=calibration,` removed from
       the fitter call. The run exits 2 on its first fold, the fitter's own
       `calibration_share 0.5 was given, but calibration 'none' holds no rows
       out`, and the test fails at the run's exit code, before part 1.
    4. **The gap not handed over** --- the fold loop calls every predictor
       with three arguments. Exit 2, `purge must be an int, got None`, before
       part 1.
    5. **The settings not carried on the curves** --- `model_settings=` removed
       from `ExceedanceCurves`. Part 1 alone, `None != 'gpd'` on the record's
       declaration: the curves moved and the record did not say why.
    6. **Each refusal removed in turn**, the condition made `if False:`:
       a. *calibration to a model that takes none* (`if given and not
          takes_calibration:`). Part 5's climatology and threshold subtests,
          `0 != 2`; also `GradientBoostedConformalCalibrationTests` and
          `GradientBoostedCrossConformalTests`' own refusal subtests, `SplitError
          not raised`, which read the same resolver on `backtest`.
       b. *a tail to a model that takes none* (`if not takes_tail:`). Part 5's
          arx subtest, by its **message**: the run is still refused, by the
          calibration-none check, for the wrong reason. Also
          `TailDeclarationTests` part 4, as B37 recorded.
       c, d, e. *calibration none*, *cross_conformal*, *the unknown family*,
          each in `_tail`. Part 5's matching subtest, by message: the fitter
          still refuses, from the first fold, in its own words (`tail 'gpd'
          needs held-out calibration rows`, `is not wired for calibration
          'cross_conformal'`, `unknown tail 'pareto'`). Also
          `TailDeclarationTests` part 4, `SplitError not raised`.
       f. *the flags not read at all* --- `settings_flags=True` -> `False` in
          `_exceedance_backtest`. Parts 1 and 2 and every part 5 subtest
          (`0 != 2`): every flag accepted and ignored.
       g. *climatology marked as taking both.* Part 5's climatology subtest
          alone, `0 != 2`: the setting accepted and silently not bound.
    7. **Part 2's comparison moved below the top quantile** --- the probe
       `tau > top` -> `tau <= top` in this test. Part 2, `1.0 == 1.0`: below the
       quantile the two curves are one curve and the test sees no difference.
    8. **The tail attached at a lower knot** --- `threshold = values[-2]` ->
       `values[-3]` in `predict_stress`. Part 3 alone of this test (the run's
       own fits read `0.049` where the untailed law reads `0.15`), and
       `GpdTailWiringTests` parts 1 and 2. **Before part 3 read the run's fits
       between their knots, this test did not see it**: the declared family
       has no tau between the upper two knots on this fixture, so every scored
       curve was unchanged below the top quantile. That is why part 3 reads
       them.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All fourteen killed again, `AssertionError`. Mutation 4 was applied
    as the predictor never handed `information=`; the run now exits 2 on "needs the
    run's as-of rule" rather than on an integer purge.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    PURGE = 6
    MINIMUM_HISTORY = 120
    SCORED = 4
    SPIKES = (100, 107, 113)
    SHARE = "0.5"

    def setUp(self):
        require_extra(self)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.registry = declared_registry_file(
            self.tmp, purge=self.PURGE, features=self.FEATURES
        )
        self.panel = self.write_panel()

    def write_panel(self):
        """The panel the docstring describes."""

        rng = random.Random(20260912)
        path = self.tmp / "panel.csv"
        days = business_days(
            date(2021, 1, 4), self.MINIMUM_HISTORY + self.PURGE + self.SCORED
        )
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["date", "sofr", "iorb", "on_rrp", "sofr_volume"])
            for index, when in enumerate(days):
                spread = 10.0 + 2.0 * (rng.random() - 0.5)
                if index in self.SPIKES:
                    spread = 35.0
                writer.writerow(
                    [when.isoformat(), round(4.30 + spread / 100.0, 6), 4.30,
                     round(100.0 * rng.random(), 4), round(2000.0 + 400.0 * rng.random(), 4)]
                )
        return path

    def run_command(self, *extra, model="gbm", name="run"):
        """`exceedance-backtest` through `cli.main`, and what it fitted and scored.

        The fitter and the backtest are wrapped, not replaced: each wrapper
        calls the real function and returns its value, so the run is the
        command's own and writes the record it would have written.
        """

        fits, reports = [], []
        fitter = ml.fit_gradient_boosted_quantiles
        backtest = cli_eval.rolling_exceedance_backtest

        def fit_spy(*args, **kwargs):
            model = fitter(*args, **kwargs)
            fits.append((model, kwargs))
            return model

        def backtest_spy(*args, **kwargs):
            report = backtest(*args, **kwargs)
            reports.append(report)
            return report

        report_path = self.tmp / f"{name}.json"
        argv = [
            "exceedance-backtest",
            "--panel", str(self.panel),
            "--thresholds", str(THRESHOLDS),
            "--registry", str(self.registry),
            "--decision-time", DECISION_TIME,
            "--minimum-history", str(self.MINIMUM_HISTORY),
            "--model", model,
            "--report", str(report_path),
        ]
        for feature in self.FEATURES:
            argv += ["--feature", feature]
        argv += list(extra)
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(ml, "fit_gradient_boosted_quantiles", fit_spy), \
                mock.patch.object(cli_eval, "rolling_exceedance_backtest", backtest_spy), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        document = (
            json.loads(report_path.read_text(encoding="utf-8"))
            if report_path.exists()
            else None
        )
        return code, " ".join(err.getvalue().split()), fits, reports, document

    def base_document(self):
        """The record this base's `gbm_exceedance` published for this run."""

        regressors, minimum_history = self.REGRESSORS, self.MINIMUM_HISTORY

        def fit_predict(train_rows, feature_rows, taus):
            model = ml.fit_gradient_boosted_quantiles(
                train_rows, regressors, minimum_history=minimum_history
            )
            return baseline.ExceedanceCurves(
                tuple(model.predict_stress(row, taus) for row in feature_rows),
                model.features_read,
                ml_libraries=model.ml_libraries,
            )

        report = baseline.rolling_exceedance_backtest(
            load_daily_panel(self.panel),
            predictor=fit_predict,
            model_name="gbm",
            features=self.FEATURES,
            registry=json.loads(self.registry.read_text(encoding="utf-8")),
            decision_time=time.fromisoformat(DECISION_TIME),
            taus=tuple(float(tau) for tau in load_stress_thresholds(THRESHOLDS)["taus_bp"]),
            minimum_history=minimum_history,
        )
        return json.loads(json.dumps(
            baseline.exceedance_backtest_document(
                report,
                panel_path=self.panel,
                registry_path=self.registry,
                thresholds_path=THRESHOLDS,
            ),
            sort_keys=True,
        ))

    def test_an_exceedance_run_asked_for_a_tail_scores_a_different_curve_above_the_top_quantile(
        self,
    ):
        """The setting reaches the fit, the curve moves above the top quantile and
        only there, the default record is unchanged, and the refusals refuse."""

        conformal = ("--calibration", "conformal", "--calibration-share", self.SHARE)
        code, err, tail_fits, tail_reports, tail_document = self.run_command(
            *conformal, "--tail", "gpd", name="tail"
        )
        self.assertEqual(code, 0, msg=err)
        code, err, plain_fits, plain_reports, plain_document = self.run_command(
            *conformal, name="plain"
        )
        self.assertEqual(code, 0, msg=err)
        (tailed,), (plain,) = tail_reports, plain_reports
        rows = {row.date: row for row in load_daily_panel(self.panel)}

        with self.subTest("1. the setting reaches the fit"):
            self.assertTrue(tailed.folds)
            # Two fits per fold: the declared curves, and the leap levels
            # `exceedance-backtest` asks for in a separate call (#139).
            self.assertEqual(len(tail_fits), 2 * len(tailed.folds))
            self.assertEqual(len(plain_fits), 2 * len(plain.folds))
            for (model, kwargs), (bare, bare_kwargs) in zip(tail_fits, plain_fits):
                self.assertEqual(kwargs.get("tail"), "gpd")
                self.assertEqual(kwargs.get("calibration"), "conformal")
                self.assertEqual(kwargs.get("calibration_share"), float(self.SHARE))
                self.assertEqual(kwargs.get("information").features, tailed.features)
                self.assertIsNotNone(model.tail_fit)
                self.assertIsNone(bare_kwargs.get("tail"))
                self.assertIsNone(bare.tail_fit)
            self.assertEqual(tail_document["declaration"].get("tail"), "gpd")
            self.assertEqual(tail_document["declaration"].get("calibration"), "conformal")
            self.assertNotIn("tail", plain_document["declaration"])
            self.assertEqual(plain_document["declaration"]["calibration"], "conformal")

        pairs = list(zip(tailed.folds, tail_fits, tailed.forecast, plain.forecast))
        with self.subTest("2. above the top declared quantile the curve moves"):
            for fold, (model, _), with_tail, without in pairs:
                feature = rows[fold.feature_date]
                top = model.predict(feature)[-1]
                above = [i for i, tau in enumerate(tailed.taus) if tau > top]
                self.assertTrue(above, msg=f"no declared tau above {top} at {fold.scored_date}")
                for i in above:
                    self.assertNotEqual(with_tail[i], without[i], msg=str(fold.scored_date))
                    self.assertGreater(with_tail[i], 0.0)
                self.assertEqual(without[above[-1]], 0.0)

        with self.subTest("3. at and below it the curve does not"):
            for fold, (model, _), (bare, _), with_tail, without in zip(
                tailed.folds, tail_fits, plain_fits, tailed.forecast, plain.forecast
            ):
                feature = rows[fold.feature_date]
                top = model.predict(feature)[-1]
                below = [i for i, tau in enumerate(tailed.taus) if tau <= top]
                self.assertTrue(below, msg=f"no declared tau at or below {top}")
                for i in below:
                    self.assertEqual(with_tail[i], without[i], msg=str(fold.scored_date))
                # The declared family has no tau between the upper knots on
                # this fixture, so the run's own fits are also read at every
                # knot up to the top quantile and between each pair: a tail
                # attached at a lower knot moves these and no declared tau.
                knots = sorted(set(model.law_knots(feature)[0][:-1]))
                probes = sorted(set(knots + [
                    0.5 * (low + high) for low, high in zip(knots, knots[1:])
                ]))
                self.assertEqual(knots[-1], top)
                self.assertEqual(
                    model.predict_stress(feature, probes),
                    bare.predict_stress(feature, probes),
                    msg=str(fold.scored_date),
                )
            self.assertEqual(
                [(fold.scored_date, fold.feature_date) for fold in tailed.folds],
                [(fold.scored_date, fold.feature_date) for fold in plain.folds],
            )

        with self.subTest("4. a run asking for neither publishes this base's record"):
            code, err, _, _, default_document = self.run_command(name="default")
            self.assertEqual(code, 0, msg=err)
            # The onset view (#139) is added beside the base record, not into it.
            self.assertIn("onset", default_document)
            default_document = {k: v for k, v in default_document.items() if k != "onset"}
            self.assertEqual(default_document, self.base_document())

        with self.subTest("5. refusals"):
            # A report name per refusal: one shared name would let an accepted
            # run's file make every later refusal look as if it wrote one.
            for position, (model, extra, phrase) in enumerate((
                ("climatology", ("--calibration", "conformal"),
                 "--calibration conformal was given, but --model climatology takes no "
                 "band calibration"),
                ("threshold", ("--regime-variable", "on_rrp", "--calibration-share", "0.5"),
                 "--calibration-share 0.5 was given, but --model threshold takes no "
                 "band calibration"),
                ("arx", ("--tail", "gpd"),
                 "--tail gpd was given, but --model arx has no quantile law"),
                ("gbm", ("--tail", "gpd"),
                 "--tail gpd was given with calibration none"),
                ("gbm", ("--calibration", "cross_conformal", "--tail", "gpd"),
                 "cross_conformal, where the tail is not wired"),
                ("gbm", ("--calibration", "conformal", "--tail", "pareto"),
                 "unknown --tail 'pareto'"),
            )):
                with self.subTest(model=model, flags=extra):
                    code, err, fits, _, document = self.run_command(
                        *extra, model=model, name=f"refused-{position}"
                    )
                    self.assertEqual(code, 2, msg=err)
                    self.assertIn(phrase, err)
                    self.assertIsNone(document)
                    self.assertEqual(fits, [])


class ExceedanceTailAccountTests(unittest.TestCase):
    """Each fold's tail on an `exceedance-backtest` record (B40).

    **The gap.** B39 let an exceedance run ask for a tail, and its record said
    which tail it declared and nothing about what the tail was at each fold.
    B38 had built that account for `backtest` alone. On this path it matters
    more: the tail moves the exceedance curve, so a metric here cannot be read
    against a tail that was never fitted unless the record says which folds had
    one.

    **What carries it.** `ml.FittedGradientBoostedQuantiles.tail_account`,
    unchanged. The fitted model stays inside `gbm_exceedance`'s closure, so the
    curves carry its account (`ExceedanceCurves.tail_account`, as they carry
    `model_settings`), the fold loop reads it off the curves that fold scored
    through `baseline._tail_account`, and the record writes it through
    `baseline._tail_document`, the writer `backtest_document` now shares. No
    second mapping.

    **The traps.** The final fold's account for every fold, which part 4
    catches; and an account read off a model the exceedance run never used --
    a `backtest` fit, another fold's fit, or the climatology beside it. So the
    fitter is wrapped only for the duration of this loop, and part 1 asserts
    each captured fit was made on exactly its fold's training rows.

    **How each state is forced.** `TailAccountTests`' panel, shared rather than
    copied, through `rolling_exceedance_backtest` with `gbm_exceedance` at the
    same conformal share: that function's rolling origins, gap and training
    rows are this loop's too, so the same spikes set the same excesses. The
    first fold's frame holds no spike (**no excesses**); each later fold's holds
    one more, one excess each, so the next folds are the exponential
    **fallback** below `ml.GPD_MINIMUM_EXCESSES`; the rest are **fitted**, or
    since #63 **floored** where the raw shape was negative (B44's **refused**
    until then, for a shape at the lower bound). Part 2 asserts all four occur,
    that a fallback or floored fold carries no `xi`, and that no fitted fold
    has a negative shape. The last fold is floored now, not fitted, so part 2
    no longer asserts that it is fitted. Part 3 also makes `ml._fit_gpd_pwm`
    raise under the untailed runs: the floor is inside the estimator, so an
    untailed run that never reaches it cannot be moved by it.

    **Part 3 is absence, not equality.** The tail moves the curves, so a tailed
    record minus its tail keys is not the untailed record, as it was on
    `backtest`. What is asserted is that neither an untailed gbm run nor the
    climatology grows `folds.tail` or `declaration.tail`, that `folds` has
    exactly the keys it had before B40, and that the top-level sections are the
    tailed record's. The published exceedance records -- gbm without a tail,
    ARX and climatology -- are runs of such predictors, which is why this is
    the guard on them; the frozen panel is not in a worktree to re-score them.

    Mutation record
    ---------------

    Run in a disposable copy per mutation plus an unmutated control before and
    after, under `$HOME`, each built from `git ls-files -z --cached --others
    --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, whole suite per run, on
    CPython 3.9.6 with numpy 2.0.2 and scikit-learn 1.6.1 through the mount's
    `.venv/bin/python` by absolute path; `repo_model` confirmed to resolve to
    each copy's `src/`. Both controls green, zero `expectedFailure`. Each
    target was counted as an exact substring in Python and found exactly once.

    1. **The final fold's account for every fold** --- the exceedance report's
       tuple built as `tuple(tail_accounts[-1] for _ in tail_accounts)`.
       `AssertionError` in **part 1** (a `fitted` account against the first
       fold's own `no_excesses`), **part 2** (`'fitted' != 'no_excesses'`) and
       **part 4** (`'fitted' == 'fitted'`, first and last entry). This test and
       nothing else.
    2. **The key made unconditional in the record** --- the writer's `if
       report.tail_accounts is not None:` -> `if True:`, over `tail_accounts or
       ()` so it does not crash. `AssertionError` in **part 3**, both the gbm
       and the climatology subtests (`'tail' unexpectedly found`). This test
       and nothing else: no other test builds an exceedance record of a gbm
       run and reads its `folds` keys.
    3. **The account made unconditional in the model** --- `if self.tail is
       None: return None` deleted from `tail_account`. `AssertionError` in
       **part 3**'s gbm subtest (`tail_accounts` a tuple of `no_excesses`, not
       `None`); also `TailAccountTests` part 3 and `ExceedanceTailTests` part 4
       (the base's record grew `folds.tail`), each by its own assertion.
    4. **The account read off a refit** --- the fold loop appends
       `_tail_account(predictor(train_rows, conditioning, tau_family,
       information=gap_rule(purge)))`, a second fit of the same frame. Every float is the
       scored fit's, so nothing that reads values alone could see it: what
       kills it is **part 1**'s fit count, `52 != 26`, and **part 4**, whose
       `entries[n]`-against-`fits[n]` pairing the doubled fit list misaligns
       (`fallback` against `no_excesses`) --- the same count, read through an
       index, not a second kind of evidence. Also `ExceedanceTailTests` part 1,
       `12 != 6`, which counts fits for its own reason. This is B38's finding
       on this path: a refit is visible only as a fit count.
    5. **A fallback read as a fitted shape of `xi = 0.0`** --- `elif
       fit.fallback:` -> `elif False:` in `tail_account`. `AssertionError` in
       **part 1** (`{'state': 'fitted', 'xi': 0.0, ...} != {'state':
       'fallback', ...}`), **part 2** (`fallback` missing from the states) and
       **part 4**; also `TailAccountTests` parts 1 and 2.
    6. **The account read off the reference** --- `_tail_account(predicted)`
       -> `_tail_account(referenced)`, the climatology fitted beside the scored
       model. **A crash, not coverage:** every account is `None`, the record
       grows no `folds.tail`, and the test stops at `KeyError: 'tail'` before
       its first part. One `KeyError`, in this test alone.

    B49: the brief's premise was false
    ----------------------------------

    B49 was queued as "nothing guards that a tail run records its per-fold
    account", on two pieces of evidence: `docs/runs/exceedance_gbm_conformal_tail_gpd_mh61.json`
    carries only `count`, `first` and `last` under `folds`, and a grep of
    `tests/test_baseline.py` finds no such assertion. Both are true and neither
    shows the defect. The guard is this test, in `tests/test_ml.py`, landed with
    the wiring in B40: part 1 holds `folds.tail` to one entry per fold (the writer
    sets `folds.count` to `len(report.folds)`, the length part 1 reads), part 2
    holds the states to `ml.TAIL_STATES`, and part 3 holds an untailed run to no
    `folds.tail` key at all. The published tail record is simply older than the
    wiring (it was not among the records the nineteen-column republish rescored),
    and re-scoring it needs the frozen panel, which is the human's. No test was
    added: the acceptance criterion and the mutation target are this test.

    Both clauses reproduced on the tree at `b288cc60`, by the protocol above
    (disposable copies from `git ls-files`, whole suite, CPython 3.9.6, numpy
    2.0.2, scikit-learn 1.6.1, `OMP_NUM_THREADS=1`, `REPO_MODEL_REQUIRE_ML=1`),
    each target asserted present exactly once, in `exceedance_backtest_document`
    only, before it was scored. Unmutated control green, zero `expectedFailure`.

    * **Clause 1, the account one entry short** --- the exceedance writer's
      `_tail_document(report.folds, report.tail_accounts)` ->
      `_tail_document(report.folds[:-1], report.tail_accounts)`.
      `AssertionError` in **part 1** (`25 != 26`) and **part 4** (the scored
      dates one short). Also `test_tail_diagnostics.KnotRefitTests`, which reads
      the record: `ValueError: folds.tail has 25 entries for 26 folds`, in two
      of its subtests. A short account was already refused twice.
    * **Clause 2, an empty account where there should be none** --- the
      writer's `if report.tail_accounts is not None:` -> `if True:`, over
      `report.tail_accounts or ()`. `AssertionError` in **part 3**, both the gbm
      and climatology subtests: `'tail' unexpectedly found in {..., 'tail': []}`.
      This test and nothing else.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All eight killed again, `AssertionError` except 6 (`KeyError`).
    B49-1's `KnotRefitTests` subtests raise `ValueError`, as recorded, at 28 entries
    for 29 folds. Mutation 4's recorded text is not source; it was applied as a
    second `_exceedance_at_fold` call read for the account.
    """

    REGRESSORS = TailAccountTests.REGRESSORS
    FEATURES = TailAccountTests.FEATURES
    PURGE = TailAccountTests.PURGE
    MINIMUM_HISTORY = TailAccountTests.MINIMUM_HISTORY
    DIPS_FROM = TailAccountTests.DIPS_FROM
    SPIKES = TailAccountTests.SPIKES
    SHARE = TailAccountTests.SHARE

    #: `TailAccountTests`' panel and its spelling of one account, shared rather
    #: than copied, so the two records are held to one fixture and one mapping.
    frame = TailAccountTests.frame
    expected = staticmethod(TailAccountTests.expected)

    def setUp(self):
        require_extra(self)
        fewer_boosting_iterations(self)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.registry_path = declared_registry_file(
            self.directory.name, purge=self.PURGE, features=self.FEATURES
        )
        self.registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.taus = tuple(
            float(tau) for tau in load_stress_thresholds(THRESHOLDS)["taus_bp"]
        )

    def exceedance(self, panel, predictor):
        """The exceedance fold loop over `panel`, its record, and every fit it made.

        The fitter is wrapped, not replaced, and only for the duration of this
        loop: a fit captured here was made by the exceedance run and by nothing
        else, with the training rows it was handed.
        """

        fits = []
        fitter = ml.fit_gradient_boosted_quantiles

        def fit_spy(train_rows, *args, **kwargs):
            model = fitter(train_rows, *args, **kwargs)
            fits.append((tuple(train_rows), model))
            return model

        with mock.patch.object(ml, "fit_gradient_boosted_quantiles", fit_spy):
            report = baseline.rolling_exceedance_backtest(
                panel,
                predictor=predictor,
                model_name="gbm",
                features=self.FEATURES,
                registry=self.registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                taus=self.taus,
                minimum_history=self.MINIMUM_HISTORY,
            )
        panel_path = self.registry_path.with_name("panel.csv")
        panel_path.write_text("date,sofr,iorb\n", encoding="utf-8")
        document = baseline.exceedance_backtest_document(
            report,
            panel_path=panel_path,
            registry_path=self.registry_path,
            thresholds_path=THRESHOLDS,
        )
        return report, json.loads(json.dumps(document)), fits

    def gbm(self, **settings):
        """The predictor `exceedance-backtest --model gbm --calibration conformal` binds."""

        return ml.gbm_exceedance(
            self.REGRESSORS,
            minimum_history=self.MINIMUM_HISTORY,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
            calibration="conformal",
            calibration_share=self.SHARE,
            **settings,
        )

    def test_an_exceedance_run_with_a_tail_records_what_its_tail_was_at_every_fold(
        self,
    ):
        """Per fold, off the fold's own exceedance fit; states apart; absent without a tail."""

        panel = self.frame()
        report, document, fits = self.exceedance(panel, self.gbm(tail="gpd"))
        entries = document["folds"]["tail"]

        with self.subTest("1. every fold, off the model that fold's curves came from"):
            self.assertTrue(report.folds)
            self.assertEqual(len(fits), len(report.folds))
            self.assertEqual(len(report.tail_accounts), len(report.folds))
            self.assertEqual(len(entries), len(report.folds))
            for fold, (train_rows, model), account, entry in zip(
                report.folds, fits, report.tail_accounts, entries
            ):
                # The fit is this loop's, on this fold's rows -- not a
                # `backtest` fit and not another fold's.
                self.assertEqual(len(train_rows), fold.train_rows)
                self.assertEqual(train_rows[0].date, fold.train_start)
                self.assertEqual(train_rows[-1].date, fold.train_end)
                expected = self.expected(model.tail_fit)
                self.assertEqual(dict(account), expected, msg=str(fold.scored_date))
                self.assertEqual(
                    entry, {"scored_date": fold.scored_date.isoformat(), **expected}
                )

        with self.subTest("2. the states are told apart"):
            states = [entry["state"] for entry in entries]
            self.assertEqual(states[0], "no_excesses")
            self.assertEqual(
                set(states), {"no_excesses", "fallback", "fitted", "floored"}
            )
            for entry in entries:
                self.assertNotIn("upper_endpoint_excess", entry)
                if entry["state"] == "fallback":
                    self.assertNotIn("xi", entry)
                    self.assertTrue(0 < entry["excesses"] < ml.GPD_MINIMUM_EXCESSES)
                elif entry["state"] == "fitted":
                    self.assertGreaterEqual(entry["excesses"], ml.GPD_MINIMUM_EXCESSES)
                    self.assertGreaterEqual(entry["xi"], ml.GPD_SHAPE_BOUNDS[0])
                elif entry["state"] == "floored":
                    self.assertNotIn("xi", entry)
                    self.assertLess(entry["xi_estimate"], 0.0)
                    self.assertGreaterEqual(entry["excesses"], ml.GPD_MINIMUM_EXCESSES)
                else:
                    self.assertEqual(entry, {"scored_date": entry["scored_date"],
                                             "state": "no_excesses", "excesses": 0})

        with self.subTest("3. without a tail, no key -- absent, not null"):
            # #63: the floor lives inside `_fit_gpd_pwm`, as B44's refusal did.
            # An untailed run must never reach the estimator, so the floor
            # cannot move a published untailed figure. Made to raise here, so
            # that is asserted, not assumed.
            def unreachable(*args, **kwargs):
                raise AssertionError("an untailed run reached _fit_gpd_pwm")

            for name, predictor in (
                ("gbm", self.gbm()),
                ("climatology", baseline.climatology_exceedance(self.MINIMUM_HISTORY)),
            ):
                with self.subTest(model=name), mock.patch.object(
                    ml, "_fit_gpd_pwm", unreachable
                ):
                    plain_report, plain_document, _ = self.exceedance(panel, predictor)
                    self.assertIsNone(plain_report.tail_accounts)
                    self.assertNotIn("tail", plain_document["folds"])
                    self.assertEqual(
                        set(plain_document["folds"]), {"count", "first", "last"}
                    )
                    self.assertNotIn("tail", plain_document["declaration"])
                    self.assertEqual(set(plain_document), set(document))

        with self.subTest("4. entry n is fold n's"):
            self.assertEqual(
                [entry["scored_date"] for entry in entries],
                [fold.scored_date.isoformat() for fold in report.folds],
            )
            self.assertNotEqual(entries[0]["state"], entries[-1]["state"])
            for position, (_, model) in enumerate(fits):
                self.assertEqual(
                    {k: v for k, v in entries[position].items() if k != "scored_date"},
                    self.expected(model.tail_fit),
                    msg=f"entry {position}",
                )


class TailCeilingTests(unittest.TestCase):
    """A fitted tail's ceiling, on the account a record carries (B41).

    **The measurement.** The two published exceedance records,
    `docs/runs/exceedance_gbm_conformal_mh61.json` and its `--tail gpd` twin,
    differ only in the tail, and the tail is a trade. At 50 bp it removes the
    zero it was built to remove: the untailed run has no log score, "the
    forecast assigned probability 0 to an event that occurred", and the tailed
    run has one. At 5 bp and 10 bp the same reason string appears in the tailed
    run where the untailed run had a log score. The mechanism is the one
    `ml.GPD_SHAPE_BOUNDS` named in advance: a negative shape puts a hard
    endpoint at `sigma / -xi`, at and beyond which `_gpd_survival` is exactly
    `0.0`, and with the conditional `Q(0.95)` a few basis points below zero on
    most days every declared tau is read in the tail. `xi` and `sigma` were on
    the record already; the ceiling was not, and nobody reads one out of two
    floats by eye.

    **What this is not.** It changes nothing the model does. Whether a fit
    whose ceiling falls inside the declared tau grid should be refused is the
    human's decision and is not taken here.

    **The trap is asserting part 1 alone.** `sigma / -xi` is arithmetic; part 2
    is what ties the field to the law, by probing `_gpd_survival` on either side
    of the value the account reports. The parameters are chosen so that the
    endpoint is exact in binary floating point, which is what lets "exactly
    `0.0` at the endpoint" be asserted rather than approximated, and they are
    three different endpoints, so a field pinned to one of them fails the others.

    The model is constructed directly with a declared `tail_fit`; `tail_account`
    reads nothing else, so no fit and no extra are needed.

    Mutation record
    ---------------

    Run in a disposable copy under `$HOME`, one mutation at a time, built from
    `git ls-files -z --cached --others --exclude-standard`, with
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1` and
    `REPO_MODEL_REQUIRE_ML=1`, through the mount's `.venv/bin/python` by
    absolute path; `repo_model` confirmed to resolve to the copy's `src/`.
    Unmutated control green before and after, zero `expectedFailure`. Each
    target was counted as an exact substring in Python and found exactly once,
    in `ml.FittedGradientBoostedQuantiles.tail_account`.

    1. **The sign dropped** --- `fit.sigma / -fit.xi` -> `fit.sigma / fit.xi`.
       `AssertionError` in **part 1** (`-2.0 != 2.0`) and in **part 2**: the
       negative "ceiling" is an excess below the threshold, where the survival
       is `4.0`, not `0.0` --- part 2 kills it on its own because a sign-flipped
       endpoint is not a place the law stops. Also `AssertionError` in
       `TailAccountTests` part 1 and `ExceedanceTailAccountTests` parts 1 and 4,
       whose `expected` helper spells the endpoint the same way. When this was
       recorded, their fixture had clamped fitted folds at `xi = -0.5`. Since
       B44 those folds are `refused`, and the kill is carried by the one
       unclamped fitted fold of negative shape (`xi` about `-0.208`).
       **Mutations 1 to 3 were re-run under B44** on the same protocol: kill
       sets unchanged, every failure `AssertionError`, except that mutation 2
       now also raises `ValueError` in `test_tail_diagnostics.KnotRefitTests`
       part 4, where `state_counts` refuses an endpoint on a positive shape.
    2. **The endpoint emitted for every fitted shape** --- `if fit.xi < 0.0:`
       -> `if True:`. `AssertionError` in **part 3** at `xi = 0.3` and `xi =
       0.5` (the key unexpectedly found, a negative value); at `xi = 0.0` it is
       a `ZeroDivisionError` from `sigma / -0.0` instead, one incidental
       exception and not a membership failure, which is why each shape is its
       own subtest. Also `AssertionError` in `TailAccountTests` part 1 and
       `ExceedanceTailAccountTests` parts 1 and 4, which carry an unclamped
       fitted fold of positive shape.
    3. **The endpoint pinned to a constant** --- `fit.sigma / -fit.xi` ->
       `2.0`, the first declared pair's true endpoint. `AssertionError` in
       **part 2** (`0.482... != 0.0` at `xi = -0.25, sigma = 3.0`: the law has
       not stopped at the reported ceiling) and in **part 1** (`2.0 != 12.0`).
       Also `AssertionError` in `TailAccountTests` part 1 and
       `ExceedanceTailAccountTests` parts 1 and 4.

    No other test in the suite goes red under any of the three.

    Rewritten to the floor (#63)
    ----------------------------

    Since Eleonora's ruling on #63 a fitted shape is never negative, so no new
    fit has a ceiling and `tail_account` no longer writes
    `upper_endpoint_excess`. The three mutations above target a line that is
    gone. They are kept as the record of what this class held until then.
    Published records still carry the field, and
    `test_tail_diagnostics.TailRecordReadingTests` still reads it.

    What is asserted now:

    1. A negative shape the estimator returns is floored. The account is
       `floored` with no endpoint, and the law is positive past where the
       unfloored ceiling `sigma / -xi` would have been. This replaces old
       part 1, which read that ceiling off the account.
    2. `_gpd_survival` stops at `sigma / -xi` for a negative shape, so the
       zero the floor removes was real. This is old part 2, read off the law
       alone, because no account reports the value any more.
    3. No ceiling for a non-negative shape. Unchanged.
    4. The fallback and no-excess states. Unchanged.
    5. A `tail_fit` with a negative `xi` that is neither floored nor a
       fallback, which `_fit_gpd_pwm` cannot return, is refused by
       `tail_account` (`ValueError`). It is not recorded as `fitted` without a
       ceiling while its law has one. Mutation, run alone in a disposable copy
       with control green before and after, on CPython 3.11.15 with numpy
       2.4.6 and scikit-learn 1.9.1: `elif fit.xi < 0.0:` -> `elif False:` in
       `tail_account`. Kills part 5 alone, `AssertionError: ValueError not
       raised`.
    """

    #: `(xi, sigma)` pairs whose endpoint `sigma / -xi` is exact in binary.
    NEGATIVE = ((-0.5, 1.0), (-0.25, 3.0), (-0.125, 0.5))

    @staticmethod
    def account(xi, sigma, *, excesses=40, clamped=False, fallback=False, fit=True):
        """`tail_account` of a model declared with this tail and nothing fitted."""

        return TailCeilingTests.account_of(
            ml.FittedTail(
                xi=xi,
                sigma=sigma,
                excesses=excesses,
                clamped=clamped,
                fallback=fallback,
            )
            if fit
            else None
        )

    @staticmethod
    def account_of(tail_fit):
        """`tail_account` of a model declared with `tail_fit` and nothing fitted."""

        model = ml.FittedGradientBoostedQuantiles(
            estimators=(None,) * len(QUANTILE_LEVELS),
            regressors=(),
            imputations={},
            residuals=(),
            cutoff=date(2024, 1, 2),
            ml_libraries={},
            tail="gpd",
            tail_fit=tail_fit,
        )
        return dict(model.tail_account)

    def test_no_fitted_tail_reports_a_ceiling_since_the_floor(self):
        """Negative shapes floored, so no ceiling; the law's own endpoint; the rest unchanged."""

        with self.subTest("1. a negative shape is floored: no ceiling on the account"):
            for xi, sigma in self.NEGATIVE:
                sample = GpdRecoveryTests()._sample(xi, sigma)
                fit = ml._fit_gpd_pwm(sample)
                account = self.account_of(fit)
                self.assertEqual(account["state"], "floored")
                self.assertNotIn("upper_endpoint_excess", account)
                beyond = 4.0 * sigma / -fit.xi_estimate
                self.assertGreater(ml._gpd_survival(fit, beyond), 0.0)

        with self.subTest("2. an unfloored negative law stops at sigma / -xi"):
            for xi, sigma in self.NEGATIVE:
                ceiling = sigma / -xi
                tail = ml.FittedTail(
                    xi=xi, sigma=sigma, excesses=40, clamped=False, fallback=False
                )
                below = math.nextafter(ceiling, 0.0)
                above = math.nextafter(ceiling, math.inf)
                msg = f"xi={xi}, sigma={sigma}, ceiling {ceiling!r}"
                self.assertGreater(ml._gpd_survival(tail, below), 0.0, msg=msg)
                self.assertEqual(ml._gpd_survival(tail, ceiling), 0.0, msg=msg)
                self.assertEqual(ml._gpd_survival(tail, above), 0.0, msg=msg)

        for xi, sigma in ((0.3, 2.0), (0.5, 1.0), (0.0, 1.0)):
            with self.subTest("3. no ceiling for a non-negative shape: absent, not None", xi=xi):
                account = self.account(xi, sigma, clamped=xi == 0.5)
                self.assertEqual(account["state"], "fitted")
                self.assertNotIn("upper_endpoint_excess", account)

        with self.subTest("4. the fallback and no-excess states are unchanged"):
            self.assertEqual(
                self.account(0.0, 1.5, excesses=7, fallback=True),
                {"state": "fallback", "sigma": 1.5, "excesses": 7},
            )
            self.assertEqual(
                self.account(0.0, 1.0, fit=False),
                {"state": "no_excesses", "excesses": 0},
            )

        with self.subTest("5. a negative fitted shape is refused, not recorded"):
            for xi, sigma in self.NEGATIVE:
                with self.assertRaises(ValueError):
                    self.account(xi, sigma)


class ExceedanceFeatureSettingsTests(unittest.TestCase):
    """`exceedance-backtest --model gbm` with a feature setting (B42).

    **The gap.** `backtest` and `compare` have taken `--spread-change-lags`,
    `--volatility-feature` and `--arx-feature` since B23, B24 and B26, and
    `exceedance-backtest` took none of them, nor did `ml.gbm_exceedance`. Every
    feature this project has built had been scored on the quantile vector and
    none on the exceedance curve, which is the metric B39 to B41 established as
    the one a change to gbm's law moves.

    **What had to reach the fit.** Each setting, through `_select_fitter`'s own
    resolvers and not a second spelling, into `gbm_exceedance` and from there
    straight into `fit_gradient_boosted_quantiles`. The purge gap already
    reaches it (B39), and the curves already carried `model_settings` (B39),
    which names all three when set and none when not; checked here, not
    assumed, by part 3.

    **The trap is a flag that parses.** Part 1 alone reads the fit's keywords,
    and a setting that resolved and was then dropped between the fit's keywords
    and its design would pass it. Part 2 reads the curves the runs scored: each
    setting's run scores a different curve from the plain run's at a declared
    tau on some fold.

    **The fixture.** A weekday panel whose spread is an AR(1) around 10 bp with
    shocks whose size switches between calm and volatile stretches, so the
    lagged changes, the GARCH variance and the ARX forecast each carry
    information the plain design does not. Calibration is `none` throughout:
    the feature settings are independent of it, and B39's class holds the
    calibrated and tailed paths.

    **Part 3's comparison is against this block's base**, written out here as
    `gbm_exceedance` stood before B42: the fitter's defaults, the gap handed
    over, the curves carrying the fit's settings and tail account. A run asking
    for no feature setting must publish that record key for key, which is the
    fixture-sized statement of the claim that every exceedance record published
    before this block (`docs/runs/exceedance_gbm_mh61.json`,
    `exceedance_arx_mh61.json`, `exceedance_funding_climatology.json` and the
    two conformal records) re-scores unchanged: none of them names a feature
    setting, and a run naming none binds nothing.

    Mutation record
    ---------------

    Run in a disposable copy per mutation plus an unmutated control under
    `$HOME`, each built from `git ls-files -z --cached --others
    --exclude-standard`, with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1` and `REPO_MODEL_REQUIRE_ML=1`, whole suite per run, on
    CPython 3.9.6 with numpy 2.0.2 and scikit-learn 1.6.1 through the mount's
    `.venv/bin/python` by absolute path; `repo_model` confirmed to resolve to
    the copy's `src/`. Unmutated control green before and after, zero
    `expectedFailure`. Each target was counted as an exact substring in Python
    and found exactly once. Every failure is `AssertionError`; none is an
    incidental exception. A subtest stops at its first failed assertion, so
    where every setting is dropped at once (5, 6) each subtest reports the
    first setting in `SETTINGS` and is one failure, not three.

    1, 2, 3. **Each setting dropped between resolution and the fit** ---
       `spread_change_lags=spread_change_lags,`, then
       `volatility_feature=volatility_feature,`, then `arx_feature=arx_feature,`
       removed from `gbm_exceedance`'s call to the fitter. Each kills **part
       2** (`[] is not true : ... scored the plain run's curve at every fold
       and tau`) **and part 1 too** (`None != 2`, `None != 'garch11'`, `None
       != 'declared'` on the fit's keywords), and **part 3** (the same `None`
       on the record's declaration, because `model_settings` is read off the
       fit the setting never reached). Part 1 cannot stay green over this
       defect: it reads exactly the fit the setting is dropped before. Part 2
       is the guard that does not depend on where the drop happens. Nothing
       else in the suite goes red.
    4. **Resolved and never bound** --- `**settings` dropped from
       `MODEL_FACTORIES["gbm"].build`, so every resolver runs and refuses and
       nothing reaches `gbm_exceedance`. Parts 1, 2 and 3 as above, reported on
       the lags setting; also `ExceedanceTailTests` parts 1 and 2 (`None !=
       'gpd'`; `0.0326... == 0.0326...`), which read the same binding. This is
       the trap: a flag that parses.
    5. **The settings never read from the arguments** --- the three
       `settings.update(...)` calls for the feature resolvers removed from
       `_select_model`. Parts 1, 2 and 3 as mutation 4, and all three part 4
       subtests (`0 != 2`: each flag accepted and ignored). Nothing else: the
       B39 settings are still read.
    6, 7, 8. **Each refusal removed in turn**, the condition made `if False:`
       in `_spread_change_lags`, `_volatility_feature` and `_arx_feature`. Each
       kills its own **part 4** subtest alone of this test (`0 != 2`: the run
       completes, the climatology, arx or threshold model silently not handed
       the setting). Also the matching `backtest` refusal subtest of
       `GradientBoostedLaggedSpreadTests`, `GradientBoostedGarchFeatureTests`
       and `GradientBoostedArxFeatureTests` respectively, `SplitError not
       raised`, which read the same resolver.
    9. **`model_settings` not carried on the curves** --- `model_settings=`
       removed from `gbm_exceedance`'s `ExceedanceCurves`. **Part 3 alone** of
       this test (`None != 2` on the record's declaration: the curve moved and
       the record did not say why); part 3's key-for-key comparison of the
       plain run does not see it, because an unset run's settings are empty
       either way, which is why part 3 also reads the set runs. Also
       `ExceedanceTailTests` part 1, `None != 'gpd'`, the same read.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). All nine killed again, on the parts named above, `AssertionError`.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    PURGE = 6
    MINIMUM_HISTORY = 120
    SCORED = 4
    #: `(flags, the fitter keyword, the value it must receive)`, one per setting.
    SETTINGS = (
        (("--spread-change-lags", "2"), "spread_change_lags", 2),
        (("--volatility-feature", "garch11"), "volatility_feature", "garch11"),
        (("--arx-feature", "declared"), "arx_feature", "declared"),
    )

    def setUp(self):
        require_extra(self)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.registry = declared_registry_file(
            self.tmp, purge=self.PURGE, features=self.FEATURES
        )
        self.panel = self.write_panel()

    def write_panel(self):
        """The panel the docstring describes."""

        rng = random.Random(20260913)
        path = self.tmp / "panel.csv"
        days = business_days(
            date(2021, 1, 4), self.MINIMUM_HISTORY + self.PURGE + self.SCORED
        )
        spread = 10.0
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["date", "sofr", "iorb", "on_rrp", "sofr_volume"])
            for index, when in enumerate(days):
                scale = 3.0 if (index // 15) % 2 else 0.5
                on_rrp = 100.0 * rng.random()
                spread = 10.0 + 0.7 * (spread - 10.0) + 0.02 * (on_rrp - 50.0) + rng.gauss(0.0, scale)
                writer.writerow(
                    [when.isoformat(), round(4.30 + spread / 100.0, 6), 4.30,
                     round(on_rrp, 4), round(2000.0 + 400.0 * rng.random(), 4)]
                )
        return path

    def run_command(self, *extra, model="gbm", name="run"):
        """`exceedance-backtest` through `cli.main`, and what it fitted and scored.

        `ExceedanceTailTests.run_command`'s spies: each wraps the real function
        and returns its value, so the run is the command's own.
        """

        fits, reports = [], []
        fitter = ml.fit_gradient_boosted_quantiles
        backtest = cli_eval.rolling_exceedance_backtest

        def fit_spy(*args, **kwargs):
            model = fitter(*args, **kwargs)
            fits.append((model, kwargs))
            return model

        def backtest_spy(*args, **kwargs):
            report = backtest(*args, **kwargs)
            reports.append(report)
            return report

        report_path = self.tmp / f"{name}.json"
        argv = [
            "exceedance-backtest",
            "--panel", str(self.panel),
            "--thresholds", str(THRESHOLDS),
            "--registry", str(self.registry),
            "--decision-time", DECISION_TIME,
            "--minimum-history", str(self.MINIMUM_HISTORY),
            "--model", model,
            "--report", str(report_path),
        ]
        for feature in self.FEATURES:
            argv += ["--feature", feature]
        argv += list(extra)
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(ml, "fit_gradient_boosted_quantiles", fit_spy), \
                mock.patch.object(cli_eval, "rolling_exceedance_backtest", backtest_spy), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        document = (
            json.loads(report_path.read_text(encoding="utf-8"))
            if report_path.exists()
            else None
        )
        return code, " ".join(err.getvalue().split()), fits, reports, document

    def base_document(self):
        """The record this block's base `gbm_exceedance` published for this run."""

        regressors, minimum_history = self.REGRESSORS, self.MINIMUM_HISTORY

        def fit_predict(train_rows, feature_rows, taus, information=None):
            model = ml.fit_gradient_boosted_quantiles(
                train_rows,
                regressors,
                minimum_history=minimum_history,
                information=information,
            )
            return baseline.ExceedanceCurves(
                tuple(model.predict_stress(row, taus) for row in feature_rows),
                model.features_read,
                ml_libraries=model.ml_libraries,
                model_settings=model.model_settings,
                tail_account=model.tail_account,
            )

        report = baseline.rolling_exceedance_backtest(
            load_daily_panel(self.panel),
            predictor=fit_predict,
            model_name="gbm",
            features=self.FEATURES,
            registry=json.loads(self.registry.read_text(encoding="utf-8")),
            decision_time=time.fromisoformat(DECISION_TIME),
            taus=tuple(float(tau) for tau in load_stress_thresholds(THRESHOLDS)["taus_bp"]),
            minimum_history=minimum_history,
        )
        return json.loads(json.dumps(
            baseline.exceedance_backtest_document(
                report,
                panel_path=self.panel,
                registry_path=self.registry,
                thresholds_path=THRESHOLDS,
            ),
            sort_keys=True,
        ))

    def test_an_exceedance_run_carries_its_feature_settings_into_every_fold_and_declares_them(
        self,
    ):
        """Each setting reaches every fold's fit, moves the scored curve, is
        declared on the record when set and absent when not, and is refused for
        a model that takes none."""

        keys = [key for _, key, _ in self.SETTINGS]
        code, err, plain_fits, plain_reports, plain_document = self.run_command(
            name="plain"
        )
        self.assertEqual(code, 0, msg=err)
        (plain,) = plain_reports
        runs = []
        for position, (flags, key, value) in enumerate(self.SETTINGS):
            code, err, fits, reports, document = self.run_command(
                *flags, name=f"setting-{position}"
            )
            self.assertEqual(code, 0, msg=f"{flags}: {err}")
            (report,) = reports
            runs.append((flags, key, value, fits, report, document))

        with self.subTest("1. each setting reaches every fold's fit, and only it"):
            self.assertTrue(plain.folds)
            # Two fits per fold: the declared curves, and the leap levels
            # `exceedance-backtest` asks for in a separate call (#139).
            self.assertEqual(len(plain_fits), 2 * len(plain.folds))
            for model, kwargs in plain_fits:
                for other in keys:
                    self.assertIsNone(kwargs.get(other), msg=other)
                    self.assertIsNone(getattr(model, other), msg=other)
            for flags, key, value, fits, report, _ in runs:
                self.assertEqual(len(fits), 2 * len(report.folds), msg=str(flags))
                self.assertEqual(len(report.folds), len(plain.folds), msg=str(flags))
                for model, kwargs in fits:
                    self.assertEqual(kwargs.get(key), value, msg=str(flags))
                    self.assertEqual(getattr(model, key), value, msg=str(flags))
                    self.assertEqual(kwargs.get("information").features, report.features)
                    for other in keys:
                        if other != key:
                            self.assertIsNone(kwargs.get(other), msg=f"{flags}: {other}")

        with self.subTest("2. each setting's run scores a different curve"):
            for flags, key, value, fits, report, _ in runs:
                self.assertEqual(
                    [(fold.scored_date, fold.feature_date) for fold in report.folds],
                    [(fold.scored_date, fold.feature_date) for fold in plain.folds],
                )
                self.assertEqual(report.taus, plain.taus)
                moved = [
                    (fold.scored_date, tau)
                    for fold, with_setting, without in zip(
                        report.folds, report.forecast, plain.forecast
                    )
                    for tau, a, b in zip(report.taus, with_setting, without)
                    if a != b
                ]
                self.assertTrue(
                    moved,
                    msg=f"{flags} scored the plain run's curve at every fold and tau",
                )

        with self.subTest("3. the record declares each setting, and only when set"):
            for flags, key, value, _, _, document in runs:
                declaration = document["declaration"]
                self.assertEqual(declaration.get(key), value, msg=str(flags))
                for other in keys:
                    if other != key:
                        self.assertNotIn(other, declaration, msg=f"{flags}: {other}")
            for other in keys:
                self.assertNotIn(other, plain_document["declaration"])
            # The onset view (#139) is added beside the base record, not into it.
            self.assertIn("onset", plain_document)
            plain_document = {k: v for k, v in plain_document.items() if k != "onset"}
            self.assertEqual(plain_document, self.base_document())

        with self.subTest("4. refusals"):
            for position, (model, extra, phrase) in enumerate((
                ("climatology", ("--spread-change-lags", "2"),
                 "--spread-change-lags 2 was given, but --model climatology reads "
                 "no lagged spread changes; only gbm does"),
                ("arx", ("--volatility-feature", "garch11"),
                 "--volatility-feature garch11 was given, but --model arx reads no "
                 "volatility feature; only gbm does"),
                ("threshold", ("--regime-variable", "on_rrp", "--arx-feature", "declared"),
                 "--arx-feature declared was given, but --model threshold reads no "
                 "ARX forecast as a feature; only gbm does"),
            )):
                with self.subTest(model=model, flags=extra):
                    code, err, fits, _, document = self.run_command(
                        *extra, model=model, name=f"refused-{position}"
                    )
                    self.assertEqual(code, 2, msg=err)
                    self.assertIn(phrase, err)
                    self.assertIsNone(document)
                    self.assertEqual(fits, [])


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


    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). Mutations 1, 3, 4, 5 and 7 and B19 1 to 4 killed again,
    `AssertionError` except 5 (`ModuleNotFoundError`). 2 and 6 kill other classes
    and were not re-run; B19's plant is a control.
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


class EventHoldoutCalibrationGapTests(unittest.TestCase):
    """A calibrated gbm fit on a knowledge holdout, split on the registry's gap (B52).

    **The defect.** `event-holdout` could only score an uncalibrated, untailed
    gbm, while every published exceedance record is conformal. Its parser
    offers no `--calibration` -- but the flags were not the first thing in the
    way. `evaluate_event_window` called every predictor as `fit_predict(train,
    features, taus)`, so the gap never reached the fit, and
    `fit_gradient_boosted_quantiles` refuses a calibration without one
    (`splits.require_purge_days`). A calibrated fit on this path would not have
    split wrongly; it would not have run. That is B39's shape in
    `rolling_exceedance_backtest`, found again on the other evaluation path.

    **The fix is B39's rule, not a second one.** The evaluator hands the gap it
    derived to a predictor whose signature names `purge_days`, by
    `baseline._reads_purge_days`, and calls every other predictor exactly as
    before. The `--calibration` and `--tail` flags on `event-holdout` are the
    next block; this one makes what they would select runnable.

    **What is asserted is the split, not that a keyword arrived.** The fit's
    `fit_end` is the last training row that clears the registry's purge before
    its `calibration_start`, by the splitter's own `clears_purge`, and its
    calibration rows end on the last row that trained. On consecutive calendar
    days a gap one day short moves `fit_end` by one row, so an off-by-one
    between the derived gap and the handed one is visible here.

    Mutation record (B52)
    ---------------------

    The per-branch, per-commit copy under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B` through the worktree's `.venv` (CPython 3.9.6, numpy 2.0.2,
    scikit-learn 1.6.1), `REPO_MODEL_REQUIRE_ML=1`, whole suite per run.
    Unmutated control green before and after, zero `expectedFailure`. Each
    mutation's anchor was counted as an exact substring of
    `src/repo_model/event_eval.py`, found exactly once, replaced, and the
    replacement confirmed present before the run; the copy was restored before
    the next.

    1. **The gap not handed over** -- the evaluator calls every predictor with
       three arguments (`if _reads_purge_days(fit_predict):` -> `if False:`),
       which is the tree before this block. Kills this test alone, as an
       error: `SplitError: purge must be an int, got None`, the fitter's
       refusal through `require_purge_days`, raised before any assertion.
    2. **The gap handed over one day short** -- `information=gap_rule(purge))` ->
       `information=gap_rule(purge) - 1)`. Kills this test alone, `AssertionError: 5 !=
       6` on the handed gap. Re-run on this test alone with that one assertion
       deleted from the copy, it still dies, `AssertionError` on `fit_end`:
       `2020-04-16 != 2020-04-15`, one calendar day later than the last row
       that clears the declared purge before calibration opens on
       `2020-04-22`. So the split clause stands on its own and is not carried
       by the keyword check.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). Mutation 1, applied as `_reads_information` disabled, killed again,
    now a `SplitError` naming the missing as-of rule. Mutation 2 has no counterpart:
    the evaluator hands an `InformationRule`, not an integer gap, so there is no day
    to drop.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    #: Nonzero, and more than one, so a gap one day short is a different split.
    PURGE = 6
    PANEL_ROWS = 160
    WINDOW_DAYS = 5
    MINIMUM_HISTORY = 40

    def setUp(self):
        require_extra(self)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.registry = json.loads(
            declared_registry_file(
                self.tmp, purge=self.PURGE, features=self.FEATURES
            ).read_text(encoding="utf-8")
        )

    def test_a_calibrated_fit_on_a_knowledge_holdout_splits_on_the_declared_purge(self):
        rows = heteroscedastic_frame(self.PANEL_ROWS)
        start, end = rows[-self.WINDOW_DAYS].date, rows[-1].date
        window = EventWindow(
            "calibrated-window",
            start,
            end,
            event_window_digest("calibrated-window", start.isoformat(), end.isoformat()),
        )
        predictor = ml.gbm_exceedance(
            self.REGRESSORS,
            minimum_history=self.MINIMUM_HISTORY,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
            calibration="conformal",
        )

        fits = []
        fitter = ml.fit_gradient_boosted_quantiles

        def fit_spy(*args, **kwargs):
            model = fitter(*args, **kwargs)
            fits.append((args[0], kwargs, model))
            return model

        journal = self.tmp / "events.jsonl"
        with mock.patch.object(ml, "fit_gradient_boosted_quantiles", fit_spy):
            report = evaluate_event_window(
                rows,
                predictor,
                window,
                features=self.FEATURES,
                registry=self.registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                taus=EXCEEDANCE_TAUS,
                model_config={"model": "gbm", "calibration": "conformal"},
                journal_path=journal,
            )

        self.assertEqual(len(fits), 1, msg="a knowledge holdout is fitted once")
        (frame, kwargs, model), = fits

        self.assertEqual(kwargs.get("calibration"), "conformal")
        information = kwargs.get("information")
        self.assertEqual(information.features, self.FEATURES)
        self.assertEqual(frame[-1].date, report.last_train_date)
        self.assertEqual(model.calibration_end, report.last_train_date)
        dates = [row.date for row in frame]
        first = dates.index(model.calibration_start)
        self.assertEqual(
            model.fit_end,
            dates[information.anchor(dates, first)],
            msg=(
                f"the fit rows end on {model.fit_end}, which is not the last "
                f"label observable at the decision before the calibration rows "
                f"open on {model.calibration_start}"
            ),
        )
        self.assertEqual(
            [line["information_rule"] for line in read_journal(journal)], ["as_of"]
        )


class GpdSampleRefusalTests(unittest.TestCase):
    """`_fit_gpd_pwm` refuses a sample it cannot fit, message for message (D1).

    The PWM estimator needs non-negative finite excesses to form its moments.
    An empty sample has no moments at all; a negative or non-finite excess is
    not an excess above the threshold and would poison `a_0 - 2 a_1` downstream.
    Both are refused with the sample size in the message, because at tail sizes
    the size is the first thing a caller debugging a fold wants to know.

    No `require_extra`, on `FittedTailPwmTests`' precedent: the estimator is
    sorting and sums, and these refusals fire before any moment is formed.

    Mutation record
    ---------------

    Phase 4 (coverage audit specs D1), disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard` at the branch head,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B` through the `.venv`
    (CPython 3.11.16), unmutated control green before and after.

    1. **The empty-sample refusal deleted** -- `if count == 0:` -> `if False:`
       in `_fit_gpd_pwm`. Kills `test_an_empty_sample_is_refused_with_its_size`:
       `ZeroDivisionError: float division by zero` from `math.fsum(ordered) /
       count` where the test requires `ValueError` matching `cannot fit a tail
       to an empty sample`. Mutation confirmed applied by diff.
    2. **The value check deleted** -- `if not math.isfinite(value) or value < 0.0:`
       -> `if False:`. Kills
       `test_a_negative_or_non_finite_excess_is_refused` at every subTest (one
       failure each): `AssertionError: ValueError not raised` -- no exception
       raises and the fit proceeds instead. Mutation confirmed applied by diff.
    """

    def test_an_empty_sample_is_refused_with_its_size(self):
        with self.assertRaises(ValueError) as caught:
            ml._fit_gpd_pwm([])
        self.assertEqual(
            str(caught.exception),
            "cannot fit a tail to an empty sample; sample size 0",
        )

    def test_a_negative_or_non_finite_excess_is_refused(self):
        for bad in (-1.0, float("nan"), float("inf")):
            with self.subTest(excess=bad):
                with self.assertRaises(ValueError) as caught:
                    ml._fit_gpd_pwm([bad, 2.0, 3.0])
                self.assertEqual(
                    str(caught.exception),
                    f"excesses must be non-negative and finite; got {bad!r} in a "
                    f"sample of size 3",
                )


class GarchCriterionGuardTests(unittest.TestCase):
    """`_garch_criterion` skips holes; the parameter search never crosses its constraints (D2).

    Two guards, one seam. `_garch_criterion` is the quasi-likelihood the GARCH
    search minimises; a squared change that is `None` -- the first row, or a
    hole in the panel -- carries no information and must contribute no term.
    And the search's own criterion refuses, with `math.inf`, any vertex outside
    the parameter constraints (`alpha + beta < 1`, `|scale| < 700`), so the
    optimiser treats an explosive or degenerate parameterisation as the worst
    possible fit rather than crashing on it: `math.exp` overflows above 700 and
    `alpha + beta >= 1` has no finite maximum to find.

    No `require_extra`: the criterion, the recursion and the search are
    `math`-only, and a checkout without the extra runs them.

    Mutation record
    ---------------

    Phase 4 (coverage audit spec D2), disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard` at the branch head,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B` through the `.venv`
    (CPython 3.11.16), unmutated control green before and after.

    1. **The hole skip removed** -- `if square is not None:` -> `if True:` in
       `_garch_criterion`. Kills
       `test_a_hole_contributes_no_term_to_the_log_likelihood`: the test errors
       with `TypeError: unsupported operand type(s) for /: 'NoneType' and
       'float'` when it calls the mutated criterion on the None-containing
       squares. The same mutation also takes down
       `test_a_sequence_that_is_all_holes_scores_zero`, which requires an
       all-holes sequence to score a quiet 0.0. Mutation confirmed applied by
       diff.
    2. **The constraint arm removed** -- the two guard lines
       (`if not (alpha >= 0.0 and beta >= 0.0 and alpha + beta < 1.0):` /
       `return math.inf`) replaced by `if False:` in `_fit_garch11`'s local
       `criterion`. Kills
       `test_the_search_never_evaluates_the_criterion_outside_its_constraints`:
       with the arm gone the search's opening simplex evaluates its two axis
       vertices -- `(alpha, beta)` = `(0.1, 0.9)` (`alpha + step`) and
       `(0.05, 0.95)` (`beta + step`), each with `alpha + beta == 1.0` -- so
       the recorder records them and the in-constraint assertion fails with
       `AssertionError: 1.0 not less than 1.0`, twice. Unmutated, the arm
       answers `math.inf` before `_garch_criterion` is reached, so the recorder
       never sees such a vertex. Mutation confirmed applied by diff.

    **Re-run under #55, 1 October 2026** (CPython 3.11.15, numpy 2.4.6, scikit-learn
    1.9.1, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-B`,
    `REPO_MODEL_REQUIRE_ML=1`, the killing test run alone in a disposable copy,
    control green before and after, each mutation confirmed applied by diff and
    reverted). Both killed again: 1 by `TypeError` in both criterion tests, 2 by
    `AssertionError` in the search test.
    """

    SQUARES = (1.0, None, 4.0, 9.0)
    PARAMETERS = (0.1, 0.05, 0.85)
    INITIAL = 2.0

    def test_a_hole_contributes_no_term_to_the_log_likelihood(self):
        squares = list(self.SQUARES)
        variances = ml._garch_variances(squares, self.PARAMETERS, self.INITIAL)

        # Restated in the same arithmetic order rather than read from the
        # module, so agreement is bit for bit (the precedent of
        # `recursion_variances` in this file): the claim under test is which
        # terms the criterion sums, not that Python can add.
        expected = 0.0
        for variance, square in zip(variances, squares[1:]):
            if square is not None:
                expected += math.log(variance) + square / variance

        total = ml._garch_criterion(squares, self.PARAMETERS, self.INITIAL)
        self.assertEqual(total, expected)

        # A hole is skipped, not read as a zero shock: a zero square would
        # still contribute its log-variance term, and a None must not.
        filled = [1.0, 0.0, 4.0, 9.0]
        self.assertNotEqual(
            total, ml._garch_criterion(filled, self.PARAMETERS, self.INITIAL)
        )

    def test_a_sequence_that_is_all_holes_scores_zero(self):
        self.assertEqual(
            ml._garch_criterion(
                [None, None, None], self.PARAMETERS, self.INITIAL
            ),
            0.0,
        )

    def test_the_search_never_evaluates_the_criterion_outside_its_constraints(self):
        """The constraint arm returns `math.inf` without evaluating the criterion.

        The recorder stands in for `_garch_criterion` during a real fit and
        fails the test if the search ever hands it a vertex outside the
        constraints -- the only externally visible effect of the arm, since the
        arm's whole job is that such vertices are never evaluated. The start
        simplex's `beta + step` vertex is `alpha + beta == 1.0`, so a search
        with the arm removed is caught on its first round.
        """

        spreads = garch_spreads(60)
        real = ml._garch_criterion
        evaluated = []

        def recorder(squares, parameters, initial):
            omega, alpha, beta = parameters
            scale = math.log(omega / initial)
            evaluated.append((alpha, beta, scale))
            return real(squares, parameters, initial)

        with mock.patch.object(ml, "_garch_criterion", recorder):
            (omega, alpha, beta), _f_minus1 = ml._fit_garch11(spreads, "fixture")

        self.assertTrue(
            evaluated,
            msg="the search never evaluated the criterion, so the recorder "
            "below asserts nothing",
        )
        for alpha_seen, beta_seen, scale_seen in evaluated:
            with self.subTest(alpha=alpha_seen, beta=beta_seen, scale=scale_seen):
                self.assertGreaterEqual(alpha_seen, 0.0)
                self.assertGreaterEqual(beta_seen, 0.0)
                self.assertLess(alpha_seen + beta_seen, 1.0)
                self.assertGreater(scale_seen, -700.0)
                self.assertLess(scale_seen, 700.0)

        # And the fit the search returns is itself inside the constraints.
        self.assertGreaterEqual(alpha, 0.0)
        self.assertGreaterEqual(beta, 0.0)
        self.assertLess(alpha + beta, 1.0)


class FittedEnsembleShapeRefusalTests(unittest.TestCase):
    """One fitted estimator per declared level, or refuse (D3).

    The reported quantile vector is the per-level fits rearranged; an estimator
    count that disagrees with the level count means some level has no fit or
    some fit has no level, and the "vector" would be read off whatever pairing
    zip happens to produce. The refusal names both counts.

    Mutation record
    ---------------

    Phase 4 (coverage audit spec D3), disposable copy under `$HOME`, control
    green before and after, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`.

    1. **The length check removed** -- `if len(self._estimators) != len(self.levels):`
       -> `if False:` in `FittedGradientBoostedQuantiles.__init__`. Kills
       `test_an_estimator_count_that_disagrees_with_the_level_count_is_refused`
       at both subTests (`AssertionError: ValueError not raised`, two
       failures): no exception raises and the model is constructed with the
       mismatched ensemble. Mutation confirmed applied by diff.
    """

    class _StubEstimator:
        def predict(self, design):
            return [0.0]

    def _construct(self, estimator_count, level_count):
        return ml.FittedGradientBoostedQuantiles(
            estimators=[self._StubEstimator() for _ in range(estimator_count)],
            regressors=("sofr_volume",),
            imputations={"sofr_volume": 1.0},
            residuals=[0.1, 0.2],
            cutoff=date(2026, 1, 1),
            levels=QUANTILE_LEVELS[:level_count],
            ml_libraries={"numpy": "2.0.2", "scikit-learn": "1.6.1"},
        )

    def test_an_estimator_count_that_disagrees_with_the_level_count_is_refused(self):
        for estimator_count, level_count in ((2, 5), (6, 5)):
            with self.subTest(estimators=estimator_count, levels=level_count):
                with self.assertRaises(ValueError) as caught:
                    self._construct(estimator_count, level_count)
                self.assertEqual(
                    str(caught.exception),
                    f"{estimator_count} fitted estimators against "
                    f"{level_count} declared levels; one fit per level is what "
                    f"makes the reported vector a quantile vector",
                )


class GradientBoostedFitRefusalTests(unittest.TestCase):
    """The fitter's own argument refusals, message for message (D4, D5).

    `GradientBoostedQuantileTests` holds two of the fitter's refusals (a level
    outside (0, 1), too few rows) because they are that class's criterion's
    neighbours. These four stand on their own: the median level, the declared
    regressors, and a regressor the training window never observed. Each
    message carries the reasoning -- the median is the point forecast and has
    no honest substitute; an empty regressor list is an omitted decision; a
    column split on itself has no individual importance; an imputation needs
    something to impute from -- so the text is the contract and is asserted
    whole.

    Mutation record
    ---------------

    Phase 4 (coverage audit specs D4, D5), disposable copy under `$HOME`,
    control green before and after, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`.

    1. **The median-level check removed** -- `if _MEDIAN_LEVEL not in grid:` ->
       `if False:` in `fit_gradient_boosted_quantiles`. Kills
       `test_levels_without_the_median_are_refused`: `AssertionError: ValueError
       not raised` -- the fit completes and returns a model where the test
       requires the refusal. Mutation confirmed applied by diff.
    2. **The empty-regressor check removed** -- `if not names:` -> `if False and
       not names:`. Kills `test_no_declared_regressors_is_refused`:
       `AssertionError: ValueError not raised` -- the fitter accepts an empty
       regressor tuple and completes the fit with a zero-column design, where
       the test requires the `no regressors declared` refusal. Mutation
       confirmed applied by diff.
    3. **The duplicate-regressor check removed** -- `if duplicates:` ->
       `if False:`. Kills `test_a_regressor_declared_twice_is_refused`:
       `AssertionError: ValueError not raised` -- the fit completes with both
       design columns carrying the same series. Mutation confirmed applied by
       diff.
    4. **The unobserved-regressor check removed** -- `if not seen:` ->
       `if False and not seen:` in the imputation loop over `names`. Kills
       `test_a_regressor_unobserved_on_every_training_row_is_refused`:
       `ZeroDivisionError: division by zero` from `sum(seen) / len(seen)` on
       the empty list, where the test requires the unobserved-regressor
       refusal. Mutation confirmed applied by diff.
    """

    def test_levels_without_the_median_are_refused(self):
        rows = crossing_frame(30)
        with self.assertRaises(ValueError) as caught:
            ml.fit_gradient_boosted_quantiles(
                rows,
                ("sofr_volume",),
                minimum_history=20,
                levels=(0.05, 0.25, 0.75, 0.95),
            )
        self.assertEqual(
            str(caught.exception),
            "the declared levels [0.05, 0.25, 0.75, 0.95] do not carry 0.5; the "
            "point forecast is the rearranged median and there is no honest "
            "substitute for it -- an average of the two levels straddling the "
            "middle is a centre no fit produced",
        )

    def test_no_declared_regressors_is_refused(self):
        rows = crossing_frame(30)
        with self.assertRaises(ValueError) as caught:
            ml.fit_gradient_boosted_quantiles(rows, (), minimum_history=20)
        self.assertEqual(
            str(caught.exception),
            "no regressors declared; an empty list is how a caller omits the "
            "decision rather than makes it. Name the regressors, even if the "
            "honest answer is one of them",
        )

    def test_a_regressor_declared_twice_is_refused(self):
        rows = crossing_frame(30)
        with self.assertRaises(ValueError) as caught:
            ml.fit_gradient_boosted_quantiles(
                rows, ("sofr_volume", "sofr_volume"), minimum_history=20
            )
        self.assertEqual(
            str(caught.exception),
            "regressors declared more than once: ['sofr_volume']; a column "
            "handed to the ensemble twice splits on itself and its importance "
            "is meaningless individually",
        )

    def test_a_regressor_unobserved_on_every_training_row_is_refused(self):
        """A None on every row is not zero and not imputable: refuse with the window.

        `_raw_regressor` returns `None` for a leg the row carries as `None` --
        an observed hole, distinct from an absent key, which raises its own
        refusal. The message names the training window's dates, so they are
        asserted too: they are `origins`' span, one row short of the frame's
        last (a one-step design has no pair into the final row).
        """

        rows = [
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {
                    "sofr": 4.30 + (index % 7) / 100.0,
                    "iorb": 4.30,
                    "sofr_volume": 2100.0 + index,
                    "on_rrp": None,
                },
            )
            for index in range(40)
        ]
        window = (
            f"{rows[0].date.isoformat()}..{rows[-2].date.isoformat()}"
        )
        with self.assertRaises(ValueError) as caught:
            ml.fit_gradient_boosted_quantiles(
                rows, ("sofr_volume", "on_rrp"), minimum_history=20
            )
        self.assertEqual(
            str(caught.exception),
            "regressor 'on_rrp' is unobserved on every row of the training "
            f"window ({window}); there is nothing to fit an imputation from, "
            "and filling it with 0.0 would be the coercion contract test 5 "
            "prohibits",
        )


class RefitPositionalHistoryTests(unittest.TestCase):
    """Issue #34: gbm's positional reads under `refit_every` above 1.

    **The defect.** `FittedGradientBoostedQuantiles` read a feature row's lags,
    GARCH variance and trailing scale back from the frame it was fitted on, by
    the row's position there. Under a refit every `N` scored rows, the feature
    row of every forecast after a block's first is newer than that frame, and
    the model raised `ValueError` ("not a row of the frame this model was
    fitted on"). Persistence and plain gbm read no history and were unaffected.

    **The fix.** The refit cadence bounds the training labels, not the
    forecast-time reads: the fold loops hand the block's model the as-of
    history at each forecast's own decision instant
    (`FittedGradientBoostedQuantiles.with_history`), and every positional read
    goes through `positional_history`, which this class records.

    **The acceptance criterion**: for each setting that reads history by
    position, every forecast's positional reads under refit `REFIT` equal those
    under refit 1 on the same grid, on the rolling path and the exceedance
    path. **The trap** is clamping the read to the fit frame: it raises nothing
    and is silently stale; the equality sees it, and the fold loop's staleness
    guard refuses it first (`tests/test_baseline.py::PositionalHistoryRefitTests`).

    The mutations run against this class are recorded there, with the ones run
    against that class, because they were run together: the fold loop reading
    from the fit frame's end kills every case here with `StaleReadError`, and
    the trap -- that read clamped, and the guard off -- with `AssertionError`
    on the equality.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    PURGE = 6
    REFIT = 4
    #: `(name, panel rows, minimum history, settings)`: six or seven scored
    #: rows, so refit `REFIT` makes two blocks and the first has forecasts
    #: after its fit. Three calibration folds rather than the records' five
    #: keep the partial CV+ case to seconds; the scale is read the same way
    #: at any number.
    CASES = (
        ("lags", 46, 40, {"spread_change_lags": 2}),
        ("lags, conformal", 54, 48, {"spread_change_lags": 3, "calibration": "conformal"}),
        ("garch11", 46, 40, {"volatility_feature": "garch11"}),
        ("garch11, conformal", 54, 48, {"volatility_feature": "garch11", "calibration": "conformal"}),
        (
            "partial CV+",
            48,
            42,
            {"calibration": "cross_conformal_partial", "calibration_folds": 3},
        ),
    )

    def setUp(self):
        require_extra(self)
        # The assertions are about which rows each forecast read, not how far
        # the boosting ran.
        fewer_boosting_iterations(self)
        with tempfile.TemporaryDirectory() as directory:
            self.registry = json.loads(
                declared_registry_file(
                    directory, purge=self.PURGE, features=self.FEATURES
                ).read_text(encoding="utf-8")
            )

    @contextlib.contextmanager
    def recorded(self):
        """Every positional read a forecast makes, keyed by its feature date."""

        reads = {}
        original = ml.FittedGradientBoostedQuantiles.positional_history

        def spy(model, feature_row):
            spreads = original(model, feature_row)
            reads.setdefault(feature_row.date, set()).add(spreads)
            return spreads

        with mock.patch.object(
            ml.FittedGradientBoostedQuantiles, "positional_history", spy
        ):
            yield reads

    def backtest(self, panel, minimum_history, settings, refit):
        def fitter(train_frame, minimum_history, information):
            return ml.fit_gradient_boosted_quantiles(
                train_frame,
                self.REGRESSORS,
                minimum_history=20,
                min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
                information=information,
                **settings,
            )

        with self.recorded() as reads:
            report = baseline.rolling_persistence_backtest(
                panel,
                features=self.FEATURES,
                registry=self.registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                minimum_history=minimum_history,
                fit_model=fitter,
                refit_every=refit,
            )
        return report, reads

    def exceedance(self, panel, minimum_history, settings, refit):
        predictor = ml.gbm_exceedance(
            self.REGRESSORS,
            minimum_history=20,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
            **settings,
        )
        with self.recorded() as reads:
            report = baseline.rolling_exceedance_backtest(
                panel,
                predictor=predictor,
                model_name="gbm",
                features=self.FEATURES,
                registry=self.registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                taus=EXCEEDANCE_TAUS,
                minimum_history=minimum_history,
                refit_every=refit,
            )
        return report, reads

    def assert_same_reads(self, every, every_reads, blocked, blocked_reads):
        feature_dates = [fold.feature_date for fold in every.folds]
        self.assertEqual([fold.feature_date for fold in blocked.folds], feature_dates)
        self.assertEqual(
            sorted(blocked_reads), sorted(set(feature_dates)),
            msg="a forecast made no positional read, so nothing was compared",
        )
        self.assertEqual(blocked_reads, every_reads)
        for when, spreads in blocked_reads.items():
            # One history per forecast, whichever of the fit's excluding models
            # read it.
            self.assertEqual(len(spreads), 1, msg=str(when))

    def test_positional_reads_under_refit_equal_those_under_refit_one(self):
        """Lags, GARCH and the partial CV+ scale, on the rolling path."""

        for name, rows, minimum, settings in self.CASES:
            with self.subTest(name):
                panel = garch_frame(rows)
                every, every_reads = self.backtest(panel, minimum, settings, 1)
                blocked, blocked_reads = self.backtest(panel, minimum, settings, self.REFIT)
                self.assertEqual(blocked.refit_every, self.REFIT)
                self.assert_same_reads(every, every_reads, blocked, blocked_reads)

    def test_the_exceedance_path_reads_the_same_history(self):
        """`gbm_exceedance` with lags under conformal, the `exceedance_gbm_conformal_lags3` shape."""

        _, rows, minimum, settings = self.CASES[1]
        panel = garch_frame(rows)
        every, every_reads = self.exceedance(panel, minimum, settings, 1)
        blocked, blocked_reads = self.exceedance(panel, minimum, settings, self.REFIT)
        self.assert_same_reads(every, every_reads, blocked, blocked_reads)

    def test_a_history_that_rewrites_the_fitted_frame_is_refused(self):
        """`with_history` refuses rows that are not the fit's own, and is a no-op without history."""

        panel = garch_frame(50)
        model = ml.fit_gradient_boosted_quantiles(
            panel[:40],
            self.REGRESSORS,
            minimum_history=20,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
            spread_change_lags=2,
        )
        self.assertEqual(model.history_end, panel[39].date)
        view = model.with_history(panel[:45])
        self.assertEqual(view.history_end, panel[44].date)
        self.assertEqual(model.history_end, panel[39].date, msg="the fit was changed")
        with self.assertRaises(ValueError):
            model.predict(panel[44])
        view.predict(panel[44])
        rewritten = list(panel[:45])
        rewritten[10] = with_spread_shifted(rewritten[10], 1.0)
        with self.assertRaises(ValueError):
            model.with_history(rewritten)
        plain = ml.fit_gradient_boosted_quantiles(
            panel[:40],
            self.REGRESSORS,
            minimum_history=20,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
        )
        self.assertIsNone(plain.history_end)
        self.assertIs(plain.with_history(panel[:45]), plain)


def one_row_at_a_time(predictor):
    """`predictor`, called once per feature row: the exceedance loop before #57.

    Names `information` and `histories`, so the fold loop hands it both, and
    passes each feature row its own history. The curves and history ends are
    concatenated, so a caller sees one call's shape made of per-row fits.
    """

    def fit_predict(train_rows, feature_rows, taus, information=None, histories=None):
        parts = [
            predictor(
                train_rows,
                (row,),
                taus,
                information=information,
                histories=None if histories is None else (histories[index],),
            )
            for index, row in enumerate(feature_rows)
        ]
        return dataclasses.replace(
            parts[0],
            curves=tuple(curve for part in parts for curve in part.curves),
            history_ends=tuple(end for part in parts for end in part.history_ends),
        )

    return fit_predict


@contextlib.contextmanager
def counted_fits():
    """Every `fit_gradient_boosted_quantiles` call `gbm_exceedance` makes."""

    fits = []
    fitter = ml.fit_gradient_boosted_quantiles

    def spy(train_rows, *args, **kwargs):
        fits.append(train_rows[-1].date)
        return fitter(train_rows, *args, **kwargs)

    with mock.patch.object(ml, "fit_gradient_boosted_quantiles", spy):
        yield fits


class ExceedanceFitPerBlockGbmTests(unittest.TestCase):
    """Issue #57: gbm's exceedance backtest fits once per block, to the same curves.

    `rolling_exceedance_backtest` used to call the predictor once per scored
    row, and `gbm_exceedance` fits inside that call, so a block of `N` rows
    paid for `N` identical fits. It now calls it once per block with the
    block's feature rows and each row's own as-of history. Every scored row's
    probabilities must be what the per-row calls gave: `one_row_at_a_time`
    is that loop, rebuilt as a predictor, on the
    `exceedance_gbm_conformal_lags3` shape (lags 3, conformal).

    The stdlib side -- one predictor call per block -- is
    `tests/test_baseline.py::ExceedanceFitPerBlockTests`.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    PURGE = 6
    REFIT = 4
    PANEL_ROWS = 54
    MINIMUM_HISTORY = 48
    SETTINGS = {"spread_change_lags": 3, "calibration": "conformal"}

    def setUp(self):
        require_extra(self)
        fewer_boosting_iterations(self)
        with tempfile.TemporaryDirectory() as directory:
            self.registry = json.loads(
                declared_registry_file(
                    directory, purge=self.PURGE, features=self.FEATURES
                ).read_text(encoding="utf-8")
            )
        self.panel = garch_frame(self.PANEL_ROWS)

    def exceedance(self, predictor, refit):
        with counted_fits() as fits:
            report = baseline.rolling_exceedance_backtest(
                self.panel,
                predictor=predictor,
                model_name="gbm",
                features=self.FEATURES,
                registry=self.registry,
                decision_time=time.fromisoformat(DECISION_TIME),
                taus=EXCEEDANCE_TAUS,
                minimum_history=self.MINIMUM_HISTORY,
                refit_every=refit,
            )
        return report, fits

    def predictor(self):
        return ml.gbm_exceedance(
            self.REGRESSORS,
            minimum_history=20,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
            **self.SETTINGS,
        )

    def test_one_fit_per_block_and_the_per_row_curves(self):
        blocked, fits = self.exceedance(self.predictor(), self.REFIT)
        per_row, per_row_fits = self.exceedance(
            one_row_at_a_time(self.predictor()), self.REFIT
        )
        rows = len(blocked.folds)
        blocks = -(-rows // self.REFIT)
        self.assertGreater(rows, self.REFIT, msg="one block has nothing to share")
        self.assertEqual(len(fits), blocks)
        self.assertEqual(len(per_row_fits), rows)
        self.assertEqual(
            fits, [blocked.folds[start].train_end for start in range(0, rows, self.REFIT)]
        )
        self.assertEqual(blocked.folds, per_row.folds)
        self.assertEqual(blocked.forecast, per_row.forecast)
        self.assertEqual(blocked.reference, per_row.reference)
        self.assertEqual(blocked.metrics, per_row.metrics)
        self.assertEqual(blocked.model_settings, per_row.model_settings)


@contextlib.contextmanager
def clamped_positional_reads():
    """gbm reading a feature row it does not carry from the end of its history.

    The trap #34 named, put back on purpose: a positional read clamped to
    whatever history the model holds raises nothing and is silently stale, so
    only the evaluator's `history_ends` check can refuse it.
    """

    original = ml.FittedGradientBoostedQuantiles.positional_history

    def clamped(model, feature_row):
        try:
            return original(model, feature_row)
        except ValueError:
            return model._history_spreads + (
                ml._observed_spread(feature_row, "feature row"),
            )

    with mock.patch.object(
        ml.FittedGradientBoostedQuantiles, "positional_history", clamped
    ):
        yield


class EventHoldoutPositionalHistoryTests(unittest.TestCase):
    """Issue #57: the event holdout reads each window day's own as-of history.

    **The defect.** `evaluate_event_window` trains once, on the as-of frame at
    the window's first decision instant, and hands the predictor one feature
    row per window day, each its day's as-of observation and so newer than
    that frame from the second day on. A gbm with lags, GARCH or the scaled
    and partial CV+ scale reads history by position, and was handed none:
    it read the training frame, which does not carry the later days' rows
    (gbm's own `ValueError`), and a model that clamped the read instead would
    have been silently stale. #34 fixed this on the rolling paths.

    **The fix is #34's.** The evaluator hands each day's `rule.frame(rows,
    info)` through `fit_predict(histories=...)` and checks every curve's
    `history_ends` with `baseline._check_history_end`: a read ending before
    the day's anchor is `StaleReadError`, one past it `LookAheadError`. The
    training frame is unchanged.

    Mutation record (#57)
    ---------------------

    A disposable copy from `git ls-files -z --cached --others
    --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    `OMP_NUM_THREADS=1`, `REPO_MODEL_REQUIRE_ML=1`, CPython 3.11.15 with numpy
    2.4.6 and scikit-learn 1.9.1, running this class. Unmutated control green
    before and after; each anchor found exactly once in
    `src/repo_model/event_eval.py`, confirmed applied by diff, and restored
    before the next.

    1. **The guard off** (the required mutation).
       `_check_history_ends(prediction, rows, infos)` -> `pass` in
       `evaluate_event_window`. Kills the stale test with `AssertionError:
       StaleReadError not raised` and the look-ahead test with
       `AssertionError: LookAheadError not raised`.
    2. **No history handed over**, the tree before #57.
       `if _reads_histories(fit_predict):` -> `if False:`. Kills the first
       test with gbm's own `ValueError` (the second window day's feature row
       is not a row of the training frame) and the look-ahead test with
       `TypeError` (its wrapper is handed no history to extend).
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    PURGE = 6
    PANEL_ROWS = 60
    WINDOW_DAYS = 5

    def setUp(self):
        require_extra(self)
        fewer_boosting_iterations(self)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.registry = json.loads(
            declared_registry_file(
                self.tmp, purge=self.PURGE, features=self.FEATURES
            ).read_text(encoding="utf-8")
        )
        self.rows = garch_frame(self.PANEL_ROWS)
        start, end = self.rows[-self.WINDOW_DAYS].date, self.rows[-1].date
        self.window = EventWindow(
            "lagged-window",
            start,
            end,
            event_window_digest("lagged-window", start.isoformat(), end.isoformat()),
        )
        self.gbm = ml.gbm_exceedance(
            self.REGRESSORS,
            minimum_history=20,
            min_samples_leaf=FIXTURE_MIN_SAMPLES_LEAF,
            spread_change_lags=2,
        )

    def evaluate(self, fit_predict):
        return evaluate_event_window(
            self.rows,
            fit_predict,
            self.window,
            features=self.FEATURES,
            registry=self.registry,
            decision_time=time.fromisoformat(DECISION_TIME),
            taus=EXCEEDANCE_TAUS,
            model_config={"model": "gbm", "spread_change_lags": 2},
            journal_path=self.tmp / "events.jsonl",
        )

    def test_each_window_day_reads_history_through_its_own_anchor(self):
        reads = []
        original = ml.FittedGradientBoostedQuantiles.positional_history

        def spy(model, feature_row):
            reads.append((feature_row.date, model.history_end))
            return original(model, feature_row)

        with mock.patch.object(
            ml.FittedGradientBoostedQuantiles, "positional_history", spy
        ):
            report = self.evaluate(self.gbm)
        self.assertEqual(len(report.scored_dates), self.WINDOW_DAYS)
        self.assertGreater(
            len(set(report.feature_dates)), 1, msg="every day read one anchor"
        )
        self.assertLess(report.last_train_date, report.feature_dates[-1])
        self.assertEqual(
            reads, [(when, when) for when in report.feature_dates]
        )

    def test_a_read_from_the_first_days_frame_is_stale(self):
        gbm = self.gbm

        def first_day_frame(train_rows, feature_rows, taus, histories=None):
            return gbm(train_rows, feature_rows, taus, histories=(train_rows,) * len(feature_rows))

        with clamped_positional_reads():
            with self.assertRaises(StaleReadError) as caught:
                self.evaluate(first_day_frame)
        self.assertIn("stale", str(caught.exception))

    def test_a_read_past_the_decision_instant_is_look_ahead(self):
        gbm = self.gbm
        dates = [row.date for row in self.rows]
        rows = self.rows

        def one_row_late(train_rows, feature_rows, taus, histories=None):
            # Each day's history, and the panel row after its end: the scored
            # day or later, not observable at the day's decision.
            late = []
            for history in histories:
                after = dates.index(history[-1].date) + 1
                late.append(tuple(history) + tuple(rows[after:after + 1]))
            return gbm(train_rows, feature_rows, taus, histories=tuple(late))

        with self.assertRaises(LookAheadError):
            self.evaluate(one_row_late)



class RecordingQuantile(ConstantQuantile):
    """`ConstantQuantile` that keeps every design and target it was fitted on.

    `fits` is class-level and in fit order: the full fit's levels first, then
    each excluding model's. Cleared by the test that patches it in.
    """

    fits = []

    def fit(self, design, targets):
        RecordingQuantile.fits.append(
            ([tuple(row) for row in design], list(targets))
        )
        return super().fit(design, targets)


class DirectTrainingPairsTests(unittest.TestCase):
    """`training_pairs="direct"` (#37): horizon-matched training pairs, opt-in.

    **The design.** One-step pairs train each row's own values on the next
    row's spread, and the model is then served the as-of observation, which is
    two or more rows before the scored day. Direct pairs train each target row
    on the observation a forecast of that row reads: the as-of rule's
    `observation` at the target's own decision instant, its lags and variance
    ending at the target's anchor. The served and the trained gaps are then
    the same by construction. One-step stays the default, and a fit that names
    no pairing declares exactly what it declared before.

    The fixture's registry prices `on_rrp` (`RRPONTSYD`) at four calendar days
    and every other field at one, so a direct design row reads `on_rrp` off an
    older row than its spread: what the subtests compare is the rule's own
    per-field read, not the anchor row.

    Mutation record (#37)
    ---------------------

    Run on CPython 3.11, numpy 2.4.6, scikit-learn 1.9.1 (`/opt/rmm-venv`),
    `PYTHONDONTWRITEBYTECODE=1`, `-B`, `REPO_MODEL_REQUIRE_ML=1`, in a
    disposable copy of the branch; unmutated control green before and after;
    each mutation confirmed applied by diff and reverted.

    1. **The one-step row served as the direct feature row** -- in
       `_direct_pairs`, `information.observation(rows, info)` ->
       `rows[target - 1]`. Killed by part 1, `AssertionError` on the design
       rows.
    2. **The as-of guards skipped on a training read** -- the
       `information.check(dates, info)` call in `_direct_pairs` deleted. Killed
       by part 2, `AssertionError: LookAheadError not raised`.
    3. **A pair whose reads reach a held-out block kept** -- the read-row test
       in `_direct_pairs`' `kept` filter removed. Killed by part 3,
       `AssertionError` on an excluding model's training dates.
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    FEATURES = ("on_rrp", "sofr_volume", "spread_bps")
    ROWS = 60

    def setUp(self):
        require_extra(self)
        from repo_model.asof import InformationRule
        from repo_model.contract import sources_for_features

        lag = {
            "basis": "record_date",
            "unit": "calendar_days",
            "days": 1,
            "available_time": "00:00",
            "timezone": "America/New_York",
        }
        registry = {
            source: {"release_lag": dict(lag)}
            for source in sources_for_features(self.FEATURES)
        }
        registry["fred_macro_latest_vintage"]["field_release_lags"] = {
            "RRPONTSYD": {**lag, "days": 4}
        }
        self.rule = InformationRule(
            registry, self.FEATURES, decision_time=time(16, 0)
        )
        self.rows = business_day_frame(self.ROWS)
        self.dates = [row.date for row in self.rows]
        RecordingQuantile.fits = []
        patcher = mock.patch.object(
            ml, "_estimator_class", return_value=RecordingQuantile
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def fit(self, **overrides):
        options = {
            "minimum_history": 20,
            "information": self.rule,
            "training_pairs": "direct",
        }
        options.update(overrides)
        return ml.fit_gradient_boosted_quantiles(self.rows, self.REGRESSORS, **options)

    def has_read(self, index):
        try:
            self.rule.information_set(self.dates, index)
        except SplitError:
            return False
        return True

    def expected_pairs(self, targets):
        design, values = [], []
        for target in targets:
            info = self.rule.information_set(self.dates, target)
            seen = self.rule.observation(self.rows, info)
            design.append(
                (float(seen.spread_bps), seen.values["on_rrp"], seen.values["sofr_volume"])
            )
            values.append(float(self.rows[target].spread_bps))
        return design, values

    def test_direct_pairs_train_each_target_on_its_own_as_of_read(self):
        """Parts 1-4: the read, the guards, the blocks, the declaration."""

        with self.subTest("1. a target's design row is the as-of observation at its decision"):
            fitted = self.fit()
            design, targets = RecordingQuantile.fits[0]
            # The frame's first rows have no read at their decision: no label
            # yet, or no `on_rrp` four days back. They train no pair.
            first = next(index for index in range(1, self.ROWS) if self.has_read(index))
            self.assertGreater(first, 2)
            self.assertEqual((design, targets), self.expected_pairs(range(first, self.ROWS)))
            self.assertEqual(len(RecordingQuantile.fits), len(QUANTILE_LEVELS))
            # And it is not the one-step design: on_rrp is read four days back.
            RecordingQuantile.fits = []
            self.fit(training_pairs=None)
            one_step, _ = RecordingQuantile.fits[0]
            self.assertNotEqual(design, one_step[-len(design):])
            self.assertEqual(fitted.training_pairs, "direct")

        with self.subTest("2. every training read passes the as-of guards"):
            with mock.patch.object(
                type(self.rule), "check", side_effect=LookAheadError("probe")
            ):
                with self.assertRaises(LookAheadError):
                    self.fit()

        with self.subTest("3. no excluding model reads its own block through a feature"):
            RecordingQuantile.fits = []
            fitted = self.fit(calibration="cross_conformal", calibration_folds=3)
            self.assertEqual(len(fitted.calibration_blocks), 3)
            for block in fitted.calibration_blocks:
                inside = [
                    when
                    for when in block.training_dates
                    if block.held_out_start <= when <= block.held_out_end
                ]
                self.assertEqual(inside, [], f"block {block.held_out_start}")

        with self.subTest("4. named when set, absent when not"):
            self.assertEqual(dict(self.fit().model_settings), {"training_pairs": "direct"})
            self.assertEqual(
                dict(baseline._model_settings(self.fit())), {"training_pairs": "direct"}
            )
            self.assertEqual(dict(self.fit(training_pairs=None).model_settings), {})
            self.assertIsNone(self.fit(training_pairs=None).training_pairs)

    def test_refusals(self):
        with self.subTest("an unknown pairing"):
            with self.assertRaisesRegex(ValueError, r"unknown training_pairs 'onestep'"):
                self.fit(training_pairs="onestep")
        with self.subTest("direct pairs with no as-of rule to read them by"):
            with self.assertRaisesRegex(SplitError, r"training_pairs 'direct'"):
                self.fit(information=None)

    def test_the_flag_reaches_the_fitter_and_is_refused_elsewhere(self):
        common = ["--registry", "registry.json", "--decision-time", DECISION_TIME]

        def parse(*argv):
            command, *rest = argv
            return cli.build_parser().parse_args(
                [command, "panel.csv", *common, "--report", "r.json", *rest]
            )

        gbm = ["--feature", "on_rrp", "--feature", "spread_bps", "--model", "gbm"]
        _, fitter = cli_eval._select_fitter(parse("backtest", *gbm, "--training-pairs", "direct"))
        self.assertEqual(fitter.keywords.get("training_pairs"), "direct")
        _, fitter = cli_eval._select_fitter(parse("backtest", *gbm))
        self.assertNotIn("training_pairs", fitter.keywords)

        compare = parse(
            "compare",
            "--model-a", "gbm", "--feature-a", "on_rrp", "--feature-a", "spread_bps",
            "--model-b", "gbm", "--feature-b", "on_rrp", "--feature-b", "spread_bps",
            "--training-pairs-b", "direct",
        )
        _, fit_a = cli_eval._select_fitter(cli_eval._side(compare, "a"), side="-a")
        _, fit_b = cli_eval._select_fitter(cli_eval._side(compare, "b"), side="-b")
        self.assertNotIn("training_pairs", fit_a.keywords)
        self.assertEqual(fit_b.keywords.get("training_pairs"), "direct")

        arx = parse("backtest", "--feature", "on_rrp", "--feature", "spread_bps",
                    "--model", "arx", "--training-pairs", "direct")
        with self.assertRaisesRegex(
            SplitError, r"--training-pairs direct was given, but --model arx"
        ):
            cli_eval._select_fitter(arx)



class MaxDepthSettingTests(unittest.TestCase):
    """`fit_depth_limited_quantiles` (#244): the depth of every tree, a setting declared in `ml.py`.

    Pressure model v2's trees are v1's with a maximum depth of 3 (#247's candidate (iv), `V2_TREE_SETTINGS`). A script
    that swapped the estimator class in its own process applied that setting where nothing declared it; here it is
    declared in this module and applied by a function beside the published fitter. The published fitter's source (and
    every definition it reads) is hashed by the final test's CRPS declaration (#220), so none of it is edited:
    `test_final_test_freeze` holds that. The setting reaches the full fit's estimators and every excluding model's, and
    the estimator class is put back when the fit ends, however it ends.

    Red first: `ml.fit_depth_limited_quantiles` did not exist (`AttributeError`); the first version of this setting,
    a `max_depth` argument of `fit_gradient_boosted_quantiles`, moved the CRPS checksum
    (`test_the_crps_checksum_is_the_pinned_one` failed) and was replaced.

    Mutation record. `/opt/rmm-venv`, CPython 3.11, `PYTHONDONTWRITEBYTECODE=1`, this class run alone, in a disposable
    copy, control green. (1) In `fit_depth_limited_quantiles`, `return published(**kwargs, max_depth=max_depth)` was
    changed to `return published(**kwargs)`, and `diff` confirmed it. `test_every_estimator_carries_the_depth` then
    failed in both subtests (`AssertionError: Items in the first set but not the second`), and so did
    `test_the_depth_is_the_published_fit_with_a_limit_and_nothing_else` (a stump's law equal to the unlimited tree's).
    (2) The `finally:` that puts the estimator class back (`module["_estimator_class"] = original`) was replaced by
    `pass`, and `diff` confirmed it. `test_the_estimator_class_is_put_back_however_the_fit_ends`, run alone, then failed
    with `AssertionError: <function fit_depth_limited_quantiles.<locals>.<lambda> ...> is not <function
    _estimator_class ...>`; the whole class errored in three tests, the leaked wrapper wrapping the next fit's
    estimator. Restored, green.
    """

    ROWS = 70

    def setUp(self):
        require_extra(self)
        self.rows = business_day_frame(self.ROWS)

    def fit(self, **overrides):
        options = {"minimum_history": 20, "calibration": "cross_conformal", "calibration_folds": 3,
                   "information": _depth_rule(self.rows)}
        options.update(overrides)
        return ml.fit_depth_limited_quantiles(self.rows, ("on_rrp", "sofr_volume"), **options)

    def test_every_estimator_carries_the_depth(self):
        fitted = self.fit(max_depth=2)
        with self.subTest("the full fit"):
            self.assertTrue(fitted._estimators)
            self.assertEqual({e.max_depth for e in fitted._estimators}, {2})
        with self.subTest("every excluding model"):
            self.assertEqual(len(fitted.calibration_blocks), 3)
            for block in fitted.calibration_blocks:
                self.assertEqual({e.max_depth for e in block.estimators}, {2})

    def test_the_published_fit_is_untouched(self):
        # Before, between and after a depth-limited fit, the published fitter builds unlimited trees.
        information = _depth_rule(self.rows)

        def published():
            return ml.fit_gradient_boosted_quantiles(
                self.rows, ("on_rrp", "sofr_volume"), minimum_history=20, calibration="cross_conformal",
                calibration_folds=3, information=information)

        before = published()
        self.assertEqual({e.max_depth for e in before._estimators}, {None})
        self.fit(max_depth=2)
        after = published()
        self.assertEqual({e.max_depth for e in after._estimators}, {None})
        self.assertEqual(before.predict(self.rows[-1]), after.predict(self.rows[-1]))

    def test_the_depth_is_the_published_fit_with_a_limit_and_nothing_else(self):
        # Every other setting is `fit_gradient_boosted_quantiles`' own, passed through.
        fitted = self.fit(max_depth=3, spread_change_lags=2)
        self.assertEqual(fitted.model_settings["spread_change_lags"], 2)
        self.assertEqual(fitted.model_settings["calibration"], "cross_conformal")
        # And it is not ignored: a stump cannot equal the unlimited tree's law.
        published = ml.fit_gradient_boosted_quantiles(
            self.rows, ("on_rrp", "sofr_volume"), minimum_history=20, calibration="cross_conformal",
            calibration_folds=3, information=_depth_rule(self.rows))
        self.assertNotEqual(published.predict(self.rows[-1]), self.fit(max_depth=1).predict(self.rows[-1]))

    def test_the_estimator_class_is_put_back_however_the_fit_ends(self):
        original = ml._estimator_class
        self.fit(max_depth=2)
        self.assertIs(ml._estimator_class, original)
        with self.assertRaises(ValueError):  # a refusal from inside the published fitter
            self.fit(max_depth=2, calibration="nope")
        self.assertIs(ml._estimator_class, original)

    def test_the_declared_depth(self):
        self.assertEqual(dict(ml.V2_TREE_SETTINGS), {"max_depth": 3})

    def test_refusals(self):
        original = ml._estimator_class
        for bad in (0, -1, True, 2.5, "3", None):
            with self.subTest(max_depth=bad):
                with self.assertRaisesRegex(ValueError, "max_depth"):
                    self.fit(max_depth=bad)
        self.assertIs(ml._estimator_class, original)
        with self.assertRaises(TypeError):  # required: a depth is a choice, never a default
            ml.fit_depth_limited_quantiles(self.rows, ("on_rrp",), minimum_history=20)


def _depth_rule(rows):
    """An as-of rule for `on_rrp` and `sofr_volume` over `rows`, one calendar day of lag each."""

    from repo_model.asof import InformationRule
    from repo_model.contract import sources_for_features

    lag = {"basis": "record_date", "unit": "calendar_days", "days": 1, "available_time": "00:00",
           "timezone": "America/New_York"}
    features = ("on_rrp", "sofr_volume", "spread_bps")
    registry = {source: {"release_lag": dict(lag)} for source in sources_for_features(features)}
    return InformationRule(registry, features, decision_time=time(16, 0))


# --------------------------------------------------------------------------
# Direct pressure-probability models (#114)
# --------------------------------------------------------------------------

_PRESSURE_REGISTRY = json.loads(
    (Path(__file__).resolve().parents[1] / "metadata" / "sources.json").read_text()
)
_PRESSURE_SPLITS = Path(__file__).resolve().parents[1] / "metadata" / "evaluation_splits.json"
_PRESSURE_CALENDAR = ("spread_bps", "sofr_volume", "days_to_month_end", "quarter_end", "tax_date")
_PRESSURE_FULL = (
    "spread_bps", "reserve_balances", "tga",
    "days_to_month_end", "quarter_end", "tax_date",
)


def _pressure_splits():
    from repo_model.evaluation_splits import load_split_declaration

    return load_split_declaration(_PRESSURE_SPLITS)


def _with_calendar(rows):
    out = []
    for index, row in enumerate(rows):
        values = dict(row.values)
        values["quarter_end"] = 1.0 if index % 11 == 10 else 0.0
        values["days_to_month_end"] = float(index % 7)
        values["tax_date"] = 1.0 if index % 5 == 0 else 0.0
        out.append(DailyObservation(row.date, values))
    return out


def _pressure_panel(count=160):
    """Weekday rows with a spread that rises on month-ends and scarce reserves.

    `reserve_balances` (USD bn) and `tga` move weekly, as the H.4.1 prints do;
    the calendar columns cycle so every pressure-day type occurs.
    """

    rows = []
    when = date(2026, 1, 5)
    state = 20261002
    while len(rows) < count:
        if when.weekday() < 5:
            index = len(rows)
            state = (1103515245 * state + 12345) % (2 ** 31)
            week = index // 5
            reserves = 3200.0 - 40.0 * (week % 9)
            tga = 700.0 + 25.0 * ((week * 7) % 5)
            month_end = index % 21 >= 19
            spread = (
                -3.0 + (state % 7) + (6.0 if month_end else 0.0)
                + (3000.0 - reserves) / 40.0
            )
            rows.append(
                DailyObservation(
                    when,
                    {
                        "sofr": 4.0 + spread / 100.0,
                        "iorb": 4.0,
                        "sofr_volume": 2100.0 + (state % 1301) / 3.0,
                        "reserve_balances": reserves,
                        "tga": tga,
                        "days_to_month_end": float(20 - index % 21),
                        "quarter_end": 1.0 if index % 63 == 62 else 0.0,
                        "tax_date": 1.0 if index % 21 == 10 else 0.0,
                    },
                )
            )
        when += timedelta(days=1)
    return rows


class _PressureConformance(ExceedancePredictorConformance):
    """The conformance suite against a direct pressure model, rule bound."""

    FACTORY = None

    def setUp(self):
        require_extra(self)

    def frame(self):
        from test_baseline import regressor_frame

        return _with_calendar(regressor_frame())

    def make_predictor(self):
        predictor = type(self).FACTORY(
            _PRESSURE_CALENDAR, _pressure_splits(), minimum_history=self.MINIMUM_HISTORY
        )
        rule = ml.InformationRule(
            _PRESSURE_REGISTRY, _PRESSURE_CALENDAR, decision_time=time(16, 0)
        )

        def bound(train_rows, feature_rows, taus):
            return predictor(train_rows, feature_rows, taus, information=rule)

        return bound


class PressureLogisticConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against `ml.pressure_logistic_exceedance`."""

    IMPLEMENTATION = staticmethod(ml.pressure_logistic_exceedance)
    FACTORY = staticmethod(ml.pressure_logistic_exceedance)


class PressureClassifierConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against `ml.pressure_classifier_exceedance`."""

    IMPLEMENTATION = staticmethod(ml.pressure_classifier_exceedance)
    FACTORY = staticmethod(ml.pressure_classifier_exceedance)


class PressureProbitConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against `ml.pressure_probit_exceedance` (#372)."""

    IMPLEMENTATION = staticmethod(ml.pressure_probit_exceedance)
    FACTORY = staticmethod(ml.pressure_probit_exceedance)


class PressureQuantileConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against `ml.pressure_quantile_exceedance` (#372)."""

    IMPLEMENTATION = staticmethod(ml.pressure_quantile_exceedance)
    FACTORY = staticmethod(ml.pressure_quantile_exceedance)


_TWO_PART_FEATURES = tuple(name for name in _PRESSURE_FULL if name != "tga")


class PressureTwoPartLogisticConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against `ml.pressure_two_part_exceedance` (#382), logistic spike part."""

    IMPLEMENTATION = staticmethod(ml.pressure_two_part_exceedance)
    FACTORY = staticmethod(ml.pressure_two_part_exceedance)


class PressureTwoPartClassifierConformanceTests(_PressureConformance, unittest.TestCase):
    """The same suite with the gradient-boosted classifier as the spike part (#382)."""

    IMPLEMENTATION = staticmethod(
        lambda *a, **k: ml.pressure_two_part_exceedance(*a, classifier="gbm_classifier", **k)
    )
    FACTORY = staticmethod(
        lambda *a, **k: ml.pressure_two_part_exceedance(*a, classifier="gbm_classifier", **k)
    )


class TwoPartPressureTests(unittest.TestCase):
    """The two-part model: P(spike) times a conditional size law (#382)."""

    def setUp(self):
        require_extra(self)

    def test_the_geometric_size_law_recovers_a_known_tail(self):
        import numpy

        rng = numpy.random.default_rng(3)
        x = rng.normal(size=(6000, 1))
        mean = 1.0 + numpy.exp(0.5 + 0.5 * x[:, 0])
        # excess over the spike is geometric on 1, 2, ... with mean `mean`
        excess = rng.geometric(1.0 / mean)
        survival = ml._geometric_size_survival(
            x.tolist(), excess.tolist(), [[-1.0], [0.0], [1.0]], (1.0, 5.0)
        )
        for served, row in zip((-1.0, 0.0, 1.0), survival):
            m = 1.0 + float(numpy.exp(0.5 + 0.5 * served))
            for tau_excess, got in zip((1.0, 5.0), row):
                self.assertAlmostEqual(got, (1.0 - 1.0 / m) ** tau_excess, delta=0.07)  # ridge shrinks the slope a little

    def test_the_survival_is_one_at_no_excess_and_falls_with_the_excess(self):
        x = [[float(i % 7)] for i in range(80)]
        excess = [1 + i % 9 for i in range(80)]
        row = ml._geometric_size_survival(x, excess, [[3.0]], (0.0, 1.0, 5.0, 45.0))[0]
        self.assertEqual(row[0], 1.0)
        self.assertEqual(list(row), sorted(row, reverse=True))
        self.assertGreater(row[1], row[3])

    def test_too_few_spike_days_fall_back_to_the_pooled_size_law(self):
        # fewer than TWO_PART_SETTINGS["min_spike_days"] spikes: the slope is not fitted
        x = [[float(i)] for i in range(30)]
        excess = [4, 8, 2]
        low = ml._geometric_size_survival(x[:3], excess, [[0.0], [29.0]], (5.0,))
        self.assertEqual(low[0], low[1])

    def test_the_spike_part_at_the_spike_threshold_is_the_plain_classifier(self):
        """At the spike threshold the two-part curve is the direct classifier's, unchanged."""

        rows = _pressure_panel()
        splits = _pressure_splits()
        rule = ml.InformationRule(_PRESSURE_REGISTRY, _TWO_PART_FEATURES, decision_time=time(16, 0))
        train, served = rows[:150], rows[150:160]
        plain = ml.pressure_logistic_exceedance(_TWO_PART_FEATURES, splits, minimum_history=20)(
            train, served, (5.0,), information=rule
        )
        two = ml.pressure_two_part_exceedance(_TWO_PART_FEATURES, splits, minimum_history=20)(
            train, served, (5.0, 10.0, 20.0, 50.0), information=rule
        )
        for want, got in zip(plain.curves, two.curves):
            self.assertAlmostEqual(want[0], got[0], places=12)
            self.assertEqual(list(got), sorted(got, reverse=True))

    def test_both_parts_are_fitted_on_the_training_pairs_only(self):
        """Both parts learn from `_pressure_pairs(train_rows)`, the as-of-paired labels, and nothing else.

        Mutation recorded (#382): in `_direct_pressure_predictor`'s `fit_predict`, changing
        `_pressure_pairs(design, information, train_rows, cache, positions)` to pass
        `list(train_rows) + list(feature_rows)` as the rows made this fail with AssertionError (the
        pairs were built from rows that included the served days).
        """

        from unittest import mock

        rows = _pressure_panel()
        rule = ml.InformationRule(_PRESSURE_REGISTRY, _TWO_PART_FEATURES, decision_time=time(16, 0))
        train, served = rows[:150], rows[150:155]
        predictor = ml.pressure_two_part_exceedance(_TWO_PART_FEATURES, _pressure_splits(), minimum_history=20)
        seen = []
        real = ml._pressure_pairs

        def spy(design, information, frame, cache, *rest):
            seen.append([row.date for row in frame])
            return real(design, information, frame, cache, *rest)

        with mock.patch.object(ml, "_pressure_pairs", spy):
            predictor(train, served, (5.0, 10.0), information=rule)
        self.assertEqual(seen, [[row.date for row in train]])
        self.assertTrue(all(day < served[0].date for day in seen[0]))

    def test_a_threshold_below_the_spike_is_the_classifier_on_its_own_label(self):
        rows = _pressure_panel()
        splits = _pressure_splits()
        rule = ml.InformationRule(_PRESSURE_REGISTRY, _TWO_PART_FEATURES, decision_time=time(16, 0))
        train, served = rows[:150], rows[150:158]
        two = ml.pressure_two_part_exceedance(_TWO_PART_FEATURES, splits, minimum_history=20)(
            train, served, (2.0, 5.0, 10.0), information=rule
        )
        plain = ml.pressure_logistic_exceedance(_TWO_PART_FEATURES, splits, minimum_history=20)(
            train, served, (2.0, 5.0), information=rule
        )
        for want, got in zip(plain.curves, two.curves):
            self.assertAlmostEqual(want[0], got[0], places=12)
            self.assertEqual(list(got), sorted(got, reverse=True))


class ProbitAndQuantileTests(unittest.TestCase):
    def setUp(self):
        require_extra(self)

    def test_the_probit_recovers_a_probit_law(self):
        import numpy

        rng = numpy.random.default_rng(0)
        x = rng.normal(size=(4000, 1))
        y = (rng.normal(size=4000) < 1.2 * x[:, 0]).astype(int)
        served = [[-1.0], [0.0], [1.0]]
        got = ml._fit_classifier("probit", x.tolist(), y.tolist(), served)
        from math import erf, sqrt

        for value, p in zip((-1.0, 0.0, 1.0), got):
            self.assertAlmostEqual(p, 0.5 * (1 + erf(1.2 * value / sqrt(2))), delta=0.04)

    def test_quantile_exceedance_reads_the_conditional_law_and_is_non_increasing(self):
        import numpy

        rng = numpy.random.default_rng(1)
        x = rng.normal(size=(1500, 1))
        spread = 2.5 + 4.0 * x[:, 0] + rng.normal(size=1500)
        curves = ml._quantile_exceedance(
            x.tolist(), spread.tolist(), [[0.0], [1.0]], (0.5, 2.5, 6.5, 20.0)
        )
        for curve in curves:
            self.assertEqual(list(curve), sorted(curve, reverse=True))
        # at x=0 the spread is N(2.5, 1): P(> 2.5) is about a half; at x=1, N(6.5, 1): P(> 6.5) the same
        self.assertAlmostEqual(curves[0][1], 0.5, delta=0.1)
        self.assertAlmostEqual(curves[1][2], 0.5, delta=0.1)
        self.assertLess(curves[0][3], 0.02)


class SettlementTimingConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the skew-t quantile regression of #379."""

    IMPLEMENTATION = staticmethod(
        lambda features, declaration, minimum_history=20: ml._settlement_timing_predictor(
            "quantile_skewt", features, declaration, minimum_history
        )
    )
    FACTORY = IMPLEMENTATION


class SkewTSmootherTests(unittest.TestCase):
    """The Adrian-Boyarchenko-Giannone smoother of the settlement-timing track (#379)."""

    GRID = (0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99)

    def setUp(self):
        require_extra(self)

    def test_it_recovers_a_student_t_law_from_its_quantiles(self):
        from scipy import stats

        probabilities = list(self.GRID)
        quantiles = stats.t.ppf(probabilities, 4) * 3.0 + 1.0
        got = ml._skew_t_exceedance(quantiles, probabilities, [5.5, 10.5, 20.5])
        want = 1.0 - stats.t.cdf((numpy_array([5.5, 10.5, 20.5]) - 1.0) / 3.0, 4)
        for value, expected in zip(got, want):
            self.assertAlmostEqual(value, float(expected), delta=0.005)

    def test_it_carries_the_skew_the_quantiles_have(self):
        from scipy import stats

        probabilities = list(self.GRID)
        quantiles = stats.skewnorm.ppf(probabilities, 4.0) * 2.0
        got = ml._skew_t_exceedance(quantiles, probabilities, [0.5, 2.5, 4.5])
        want = stats.skewnorm.sf(numpy_array([0.5, 2.5, 4.5]) / 2.0, 4.0)
        for value, expected in zip(got, want):
            self.assertAlmostEqual(value, float(expected), delta=0.02)

    def test_the_curve_does_not_rise_with_the_cut_and_stays_a_probability(self):
        probabilities = list(self.GRID)
        quantiles = [-3.0, -1.5, -1.0, -0.5, 0.0, 0.2, 0.4, 0.7, 1.2, 2.5, 5.0, 8.0, 30.0]
        curve = ml._skew_t_exceedance(quantiles, probabilities, [0.5, 1.5, 5.5, 10.5, 20.5, 50.5])
        self.assertEqual(list(curve), sorted(curve, reverse=True))
        self.assertTrue(all(0.0 <= value <= 1.0 for value in curve))

    def test_a_day_with_equal_quantiles_is_a_point_mass(self):
        self.assertEqual(ml._skew_t_exceedance([2.0] * 13, list(self.GRID), [1.5, 2.5]), (1.0, 0.0))

    def test_a_day_does_not_depend_on_the_days_fitted_before_it(self):
        from scipy import stats

        probabilities = list(self.GRID)
        first = stats.t.ppf(probabilities, 5) * 2.0
        second = stats.t.ppf(probabilities, 3) * 6.0 + 4.0
        alone = ml._skew_t_exceedance(second, probabilities, [5.5, 10.5])
        ml._skew_t_exceedance(first, probabilities, [5.5, 10.5])
        self.assertEqual(ml._skew_t_exceedance(second, probabilities, [5.5, 10.5]), alone)

    def test_it_refuses_quantiles_that_do_not_match_the_grid(self):
        with self.assertRaises(ValueError):
            ml._skew_t_exceedance([0.0, 1.0, 2.0], list(self.GRID), [0.5])

    def test_the_quantile_reading_refuses_an_unknown_smoother(self):
        with self.assertRaises(ValueError):
            ml._quantile_exceedance([[0.0]] * 40, [0.0] * 40, [[0.0]], (5.0,), smoother="spline")

    def test_the_skew_t_reading_of_a_regression_is_a_conditional_law(self):
        import numpy

        rng = numpy.random.default_rng(2)
        x = rng.normal(size=(1500, 1))
        spread = 2.5 + 4.0 * x[:, 0] + rng.normal(size=1500)
        curves = ml._quantile_exceedance(
            x.tolist(), spread.tolist(), [[0.0], [1.0]], (0.5, 2.5, 6.5, 20.0), smoother="skew_t"
        )
        for curve in curves:
            self.assertEqual(list(curve), sorted(curve, reverse=True))
        self.assertAlmostEqual(curves[0][1], 0.5, delta=0.1)
        self.assertAlmostEqual(curves[1][2], 0.5, delta=0.1)
        self.assertLess(curves[0][3], 0.02)

    def test_a_settlement_timing_form_is_one_of_the_two_declared(self):
        with self.assertRaises(ValueError):
            ml._settlement_timing_predictor("logistic", _PRESSURE_CALENDAR, _pressure_splits())


def numpy_array(values):
    import numpy

    return numpy.asarray(values, dtype=float)


class DirectPressureModelTests(unittest.TestCase):
    """The direct pressure models' design, pairs and guards (#114)."""

    def setUp(self):
        require_extra(self)
        self.rows = _pressure_panel()
        self.dates = [row.date for row in self.rows]

    def rule(self, horizon=1, features=_PRESSURE_FULL):
        return ml.InformationRule(
            _PRESSURE_REGISTRY, features, decision_time=time(16, 0), horizon=horizon
        )

    def test_a_product_term_is_the_product_of_its_two_as_of_reads(self):
        """#127's product terms: a scheduled input times an observed one, as read.

        The settlement is the scored day's (scheduled), the TGA change ends at
        the TGA's as-of read; the product is formed from exactly those two
        design values, and every other term is unchanged.
        """

        features = _PRESSURE_FULL + ("treasury_settlement",)
        products = (("treasury_settlement", "tga_change"),)
        design = ml._PressureDesign(features, _pressure_splits(), products=products)
        base = ml._PressureDesign(features, _pressure_splits())
        self.assertEqual(design.names, base.names + ("treasury_settlement_x_tga_change",))
        rule = self.rule(features=features)
        rows = [
            DailyObservation(
                row.date, {**row.values, "treasury_settlement": 10.0 + 5.0 * (index % 4)}
            )
            for index, row in enumerate(self.rows[:120])
        ]
        xs, ys = ml._pressure_pairs(design, rule, rows, {})
        plain, plain_ys = ml._pressure_pairs(base, rule, rows, {})
        self.assertEqual(ys, plain_ys)
        self.assertTrue(xs)
        settlement = base.names.index("treasury_settlement")
        change = base.names.index("tga_change")
        for got, want in zip(xs, plain):
            self.assertEqual(got[:-1], want)
            self.assertAlmostEqual(got[-1], want[settlement] * want[change], places=9)

    def test_a_product_names_declared_terms(self):
        for products in (
            (("treasury_settlement", "tga_change"),),  # settlement not declared
            (("spread_bps", "not_a_column"),),
        ):
            with self.subTest(products=products), self.assertRaisesRegex(ValueError, "product"):
                ml._PressureDesign(_PRESSURE_FULL, _pressure_splits(), products=products)

    def test_the_design_names_every_term_it_builds(self):
        design = ml._PressureDesign(
            _PRESSURE_FULL + ("treasury_settlement",), _pressure_splits()
        )
        self.assertEqual(
            design.names,
            (
                "spread_bps", "reserve_balances",
                "quarter_end", "month_end", "tax_date", "treasury_settlement",
                "quarter_end_x_scarcity", "month_end_x_scarcity",
                "tax_date_x_scarcity", "treasury_settlement_x_scarcity",
                "tga_change", "tga_change_x_scarcity",
            ),
        )

    def test_a_partial_calendar_or_tga_without_reserves_is_refused(self):
        with self.assertRaises(ValueError):
            ml._PressureDesign(("spread_bps", "quarter_end"), _pressure_splits())
        with self.assertRaises(ValueError):
            ml._PressureDesign(("spread_bps", "tga"), _pressure_splits())
        with self.assertRaises(ValueError):
            ml._PressureDesign(("reserve_balances",), _pressure_splits())

    def test_each_label_is_paired_with_what_its_own_decision_read(self):
        """Direct pairs: at horizon 3 the spread is the row four back.

        The calendar terms are the label's own day, the scarcity state the
        reserves print public at the label's decision, and the TGA change ends
        at the TGA print public then.
        """

        design = ml._PressureDesign(_PRESSURE_FULL, _pressure_splits())
        rule = self.rule(horizon=3)
        train = self.rows[:120]
        xs, ys = ml._pressure_pairs(design, rule, train, {})
        dates = [row.date for row in train]
        expected_x, expected_y = [], []
        for target in range(1, len(train)):
            try:
                info = rule.information_set(dates, target)
            except SplitError:
                continue
            tga_row = [r for r in info.reads if r.feature == "tga"][0].row
            reserves_row = [r for r in info.reads if r.feature == "reserve_balances"][0].row
            if tga_row < ml.TGA_CHANGE_ROWS:
                continue
            self.assertEqual(info.anchor, target - 4)
            self.assertLess(reserves_row, target - 3)
            kind = _pressure_splits().day_type(train[target].values)
            state = train[reserves_row].values["reserve_balances"] / 1000.0
            terms = [1.0 if kind == name else 0.0 for name in ("quarter_end", "month_end", "tax_date")]
            change = train[tga_row].values["tga"] - train[tga_row - 5].values["tga"]
            expected_x.append(
                [train[target - 4].spread_bps, state, *terms,
                 *[term * state for term in terms], change, change * state]
            )
            expected_y.append(train[target].spread_bps)
        self.assertEqual(len(xs), len(expected_x))
        for got, want in zip(xs, expected_x):
            for a, b in zip(got, want):
                self.assertAlmostEqual(a, b, places=9)
        self.assertEqual(ys, expected_y)

    def test_the_logistic_is_scikit_learns_on_the_standardized_pairs(self):
        from sklearn.linear_model import LogisticRegression
        import numpy

        design = ml._PressureDesign(_PRESSURE_CALENDAR, _pressure_splits())
        rule = self.rule(features=_PRESSURE_CALENDAR)
        rows = _with_calendar(self.rows)
        train, served = rows[:-1], rows[-1:]
        info = rule.information_set([row.date for row in rows], len(rows) - 1)
        observation = rule.observation(rows, info)
        predictor = ml.pressure_logistic_exceedance(_PRESSURE_CALENDAR, _pressure_splits())
        got = predictor(train, (observation,), (5.0,), information=rule).curves[0][0]

        xs, ys = ml._pressure_pairs(design, rule, train, {})
        x = numpy.asarray(xs)
        centre, scale = x.mean(axis=0), x.std(axis=0)
        scale[scale == 0.0] = 1.0
        model = LogisticRegression(C=1.0, max_iter=5000).fit(
            (x - centre) / scale, [1 if y > 5.0 else 0 for y in ys]
        )
        want = model.predict_proba(
            (numpy.asarray([design.row(observation, None)]) - centre) / scale
        )[0, 1]
        self.assertAlmostEqual(got, float(want), places=12)

    def test_a_backtest_at_horizon_two_runs_under_every_guard(self):
        for factory in (ml.pressure_logistic_exceedance, ml.pressure_classifier_exceedance):
            with self.subTest(factory=factory.__name__):
                report = baseline.rolling_exceedance_backtest(
                    self.rows,
                    predictor=factory(_PRESSURE_FULL, _pressure_splits(), minimum_history=60),
                    model_name=factory.__name__,
                    features=_PRESSURE_FULL,
                    registry=_PRESSURE_REGISTRY,
                    decision_time=time(16, 0),
                    taus=(5.0, 10.0),
                    minimum_history=60,
                    refit_every=21,
                    horizon=2,
                )
                self.assertEqual(report.horizon, 2)
                for fold in report.folds:
                    self.assertLessEqual(fold.feature_date, self.dates[self.dates.index(fold.scored_date) - 3])
                self.assertIn("tga_change_x_scarcity", report.model_settings["design"])
                self.assertEqual(report.model_settings["scarcity_state"], ml.SCARCITY_STATE)

    def test_without_the_rule_it_refuses(self):
        predictor = ml.pressure_logistic_exceedance(_PRESSURE_CALENDAR, _pressure_splits())
        rows = _with_calendar(self.rows)
        with self.assertRaises(ValueError):
            predictor(rows[:-1], rows[-1:], (5.0,))

    def test_a_served_tga_change_must_start_at_the_as_of_read(self):
        """The served TGA change is measured from the TGA value the forecast read.

        Written red first: with the comparison against the observation's read
        absent, the history below (whose latest public TGA is not the value the
        observation read) gave a change and no refusal.

        Recorded mutation (CLAUDE.md), the read check dropped: in
        `ml._served_tga_change`, the condition `position < 0 or read is None or
        float(history[position].values["tga"]) != float(read)` mutated to
        `position < 0 or read is None`. This test then fails, raising
        `AssertionError` ("LookAheadError not raised").
        """

        history = self.rows[:40]
        observation = DailyObservation(
            history[-1].date, {**history[-1].values, "tga": history[-1].values["tga"] + 1.0}
        )
        with self.assertRaises(LookAheadError):
            ml._served_tga_change(history, observation)
        # And the honest read gives the change from the history's own rows.
        self.assertEqual(
            ml._served_tga_change(history, history[-1]),
            history[-1].values["tga"] - history[-6].values["tga"],
        )

    def test_both_are_selectable_by_name_and_read_the_splits(self):
        for name in ("pressure_logistic", "pressure_classifier"):
            choice = cli_eval.MODEL_FACTORIES[name]
            self.assertTrue(choice.takes_splits)
            self.assertTrue(choice.needs_ml_extra)


_SCARCITY_CALENDAR = (
    "spread_bps", "reserve_scarcity_state", "days_to_month_end", "quarter_end", "tax_date",
    "treasury_settlement",
)
_FOUR_LEVEL = {0.0: 0.0, 1.0: 1.0, 2.0: 2.0, 3.0: 3.0}
_TWO_LEVEL = {0.0: 0.0, 1.0: 0.0, 2.0: 1.0, 3.0: 1.0}


def _scarcity_calendar_panel(count=160):
    """`_pressure_panel` with the state's inputs and the state, and a settlement column.

    The state rises as reserves fall (`reserve_balances` cycles weekly), and the
    spread already rises with scarcity there, so the state carries signal.
    """

    from repo_model import scarcity

    rows = []
    for index, row in enumerate(_pressure_panel(count)):
        values = dict(row.values)
        values["bank_total_assets"] = 24000.0
        values["on_rrp"] = 50.0 if values["reserve_balances"] < 3000.0 else 400.0
        values["treasury_settlement"] = 60.0 if index % 10 == 3 else 0.0
        rows.append(DailyObservation(row.date, values))
    return scarcity.with_reserve_scarcity_state(rows)


class ScarcityCalendarDesignTests(unittest.TestCase):
    """The scarcity-conditioned calendar's design and its two forms (#128).

    Written first, and watched failing: before the design existed every test
    here failed with `AttributeError: module 'repo_model.ml' has no attribute
    '_ScarcityCalendarDesign'` (or `'_scarcity_calendar_predictor'`).
    """

    def setUp(self):
        require_extra(self)

    def design(self, features=_SCARCITY_CALENDAR, levels=_FOUR_LEVEL, monotone=False):
        return ml._ScarcityCalendarDesign(features, _pressure_splits(), levels, monotone=monotone)

    def test_every_scheduled_term_enters_only_times_the_state(self):
        self.assertEqual(
            self.design().names,
            (
                "spread_bps", "reserve_scarcity_state",
                "quarter_end_x_state", "month_end_x_state", "tax_date_x_state",
                "treasury_settlement_x_state",
            ),
        )
        measures = _SCARCITY_CALENDAR + ("effr_minus_iorb_bp",)
        self.assertEqual(
            self.design(measures).names,
            (
                "spread_bps", "reserve_scarcity_state", "effr_minus_iorb_bp",
                "quarter_end_x_state", "month_end_x_state", "tax_date_x_state",
                "treasury_settlement_x_state",
            ),
        )
        without_settlement = self.design(_SCARCITY_CALENDAR[:-1])
        self.assertNotIn("treasury_settlement_x_state", without_settlement.names)

    def _observation(self, state, **values):
        base = {
            "sofr": 4.07, "iorb": 4.0, "reserve_scarcity_state": state,
            "days_to_month_end": 12.0, "quarter_end": 0.0, "tax_date": 0.0,
            "treasury_settlement": 0.0,
        }
        base.update(values)
        return DailyObservation(date(2025, 9, 30), base)

    def test_a_row_is_the_mapped_state_times_each_scheduled_term(self):
        observation = self._observation(3.0, quarter_end=1.0, days_to_month_end=0.0, treasury_settlement=80.0)
        got = self.design().row(observation, None)
        self.assertAlmostEqual(got[0], 7.0, places=9)
        self.assertEqual(got[1:], [3.0, 3.0, 0.0, 0.0, 240.0])
        two = self.design(levels=_TWO_LEVEL).row(observation, None)
        self.assertEqual(two[1:], [1.0, 1.0, 0.0, 0.0, 80.0])
        # A quarter-end with abundant reserves adds nothing.
        calm = self.design().row(self._observation(0.0, quarter_end=1.0, treasury_settlement=80.0), None)
        self.assertEqual(calm[1:], [0.0, 0.0, 0.0, 0.0, 0.0])

    def test_a_derived_measure_is_read_off_its_constituents(self):
        """#98's EFFR - IORB is a derived feature: a property of the row, not a value.

        Written red first: the design read `row.values` only, so this raised
        `ValueError` ("the as-of read of 'effr_minus_iorb_bp' is missing") and
        every run with the measures trained no pair.
        """

        design = self.design(_SCARCITY_CALENDAR + ("effr_minus_iorb_bp",))
        got = design.row(self._observation(2.0, effr=3.93), None)
        self.assertEqual(got[2], -7.0)
        with self.assertRaises(ValueError):
            design.row(self._observation(2.0, effr=None), None)

    def test_a_state_off_the_mapping_or_missing_is_refused(self):
        for state in (1.5, 4.0, None):
            with self.subTest(state=state):
                with self.assertRaises(ValueError):
                    self.design().row(self._observation(state), None)

    def test_it_refuses_a_design_without_its_terms(self):
        with self.assertRaises(ValueError):
            self.design(("reserve_scarcity_state", "days_to_month_end", "quarter_end", "tax_date"))
        with self.assertRaises(ValueError):
            self.design(("spread_bps", "days_to_month_end", "quarter_end", "tax_date"))
        with self.assertRaises(ValueError):
            self.design(("spread_bps", "reserve_scarcity_state", "quarter_end", "tax_date"))
        with self.assertRaises(ValueError):
            self.design(levels={0.0: 0.0, 1.0: 1.0})
        with self.assertRaises(ValueError):
            ml._scarcity_calendar_predictor("forest", _SCARCITY_CALENDAR, _pressure_splits(), _FOUR_LEVEL)

    def test_the_gbm_is_constrained_non_decreasing_in_the_state(self):
        measures = _SCARCITY_CALENDAR + ("effr_minus_iorb_bp",)
        self.assertEqual(self.design(measures, monotone=True).monotone, (0, 1, 0, 1, 1, 1, 1))
        self.assertIsNone(self.design(measures).monotone)

    def test_the_constrained_gbm_never_falls_as_the_state_rises(self):
        """Labels that fall with the state on quarter-ends: the constraint still holds."""

        design = self.design(monotone=True)
        xs, labels = [], []
        for index in range(400):
            state = float(index % 4)
            quarter = 1.0 if index % 3 == 0 else 0.0
            observation = self._observation(state, quarter_end=quarter, sofr=4.0 + (index % 9) / 100.0)
            xs.append(design.row(observation, None))
            # Pressure falls with the state on these rows: an unconstrained fit would follow it.
            labels.append(1 if (state <= 1.0 and index % 2 == 0) else 0)
        served = [design.row(self._observation(float(s), quarter_end=1.0), None) for s in range(4)]
        got = ml._fit_classifier("gbm_classifier", xs, labels, served, monotone=design.monotone)
        for earlier, later in zip(got, got[1:]):
            self.assertLessEqual(earlier, later + 1e-12)
        free = ml._fit_classifier("gbm_classifier", xs, labels, served)
        self.assertGreater(free[0], free[-1])

    def test_a_backtest_at_horizon_two_runs_under_every_guard(self):
        from repo_model.scarcity import measurement_declaration

        rows = _scarcity_calendar_panel()
        dates = [row.date for row in rows]
        features = _SCARCITY_CALENDAR[:-1]
        for kind in ("logistic", "gbm"):
            with self.subTest(kind=kind), measurement_declaration():
                report = baseline.rolling_exceedance_backtest(
                    rows,
                    predictor=ml._scarcity_calendar_predictor(
                        kind, features, _pressure_splits(), _TWO_LEVEL, minimum_history=60
                    ),
                    model_name=kind,
                    features=features,
                    registry=_PRESSURE_REGISTRY,
                    decision_time=time(16, 0),
                    taus=(5.0, 10.0),
                    minimum_history=60,
                    refit_every=21,
                    horizon=2,
                )
            self.assertEqual(report.horizon, 2)
            for fold in report.folds:
                self.assertLessEqual(fold.feature_date, dates[dates.index(fold.scored_date) - 3])
            settings = report.model_settings
            self.assertEqual(settings["scarcity_calendar"]["state_levels"], {"0": 0.0, "1": 0.0, "2": 1.0, "3": 1.0})
            self.assertEqual(settings["design"][-1], "tax_date_x_state")
            if kind == "gbm":
                self.assertEqual(settings["monotonic_cst"], [0, 1, 1, 1, 1])
            else:
                self.assertNotIn("monotonic_cst", settings)


class ScarcityEventBarVariantTests(unittest.TestCase):
    """The two variants of the scarcity-conditioned calendar scored under the event bar (#378).

    Written first, and watched failing: before the variants existed every test
    here raised `TypeError: _ScarcityCalendarDesign.__init__() got an
    unexpected keyword argument 'interactions'` (or `'regime_pooled'`).
    """

    def setUp(self):
        require_extra(self)

    def design(self, features=_SCARCITY_CALENDAR, **kwargs):
        return ml._ScarcityCalendarDesign(features, _pressure_splits(), _FOUR_LEVEL, **kwargs)

    def _observation(self, state, **values):
        base = {
            "sofr": 4.07, "iorb": 4.0, "reserve_scarcity_state": state,
            "days_to_month_end": 12.0, "quarter_end": 0.0, "tax_date": 0.0,
            "treasury_settlement": 0.0,
        }
        base.update(values)
        return DailyObservation(date(2025, 9, 16), base)

    def test_the_interaction_crosses_settlement_size_state_and_quarter_end_or_tax_date(self):
        design = self.design(interactions=True)
        self.assertEqual(design.names[-2:], (
            "treasury_settlement_x_state_x_quarter_end", "treasury_settlement_x_state_x_tax_date",
        ))
        tax = design.row(self._observation(2.0, tax_date=1.0, treasury_settlement=70.0), None)
        self.assertEqual(tax[-2:], [0.0, 140.0])
        quarter = design.row(
            self._observation(3.0, quarter_end=1.0, days_to_month_end=0.0, treasury_settlement=50.0), None
        )
        self.assertEqual(quarter[-2:], [150.0, 0.0])
        ordinary = design.row(self._observation(3.0, treasury_settlement=50.0), None)
        self.assertEqual(ordinary[-2:], [0.0, 0.0])
        calm = design.row(self._observation(0.0, tax_date=1.0, treasury_settlement=70.0), None)
        self.assertEqual(calm[-2:], [0.0, 0.0])

    def test_the_interaction_variant_is_the_base_form_without_a_settlement(self):
        without = _SCARCITY_CALENDAR[:-1]
        self.assertEqual(self.design(without, interactions=True).names, self.design(without).names)
        self.assertEqual(
            self.design(interactions=True).names[: len(self.design().names)], self.design().names
        )

    def test_the_gbm_interactions_are_constrained_non_decreasing(self):
        got = self.design(monotone=True, interactions=True).monotone
        self.assertEqual(got, (0, 1, 1, 1, 1, 1, 1, 1))

    def test_a_variant_is_one_variant(self):
        with self.assertRaises(ValueError):
            self.design(interactions=True, regime_pooled=True)
        with self.assertRaises(ValueError):
            self.design(regime_pooled=True, monotone=True)

    def test_the_regime_design_adds_raw_scheduled_columns_and_declares_its_pooling(self):
        design = self.design(regime_pooled=True)
        self.assertEqual(
            design.names[-4:], ("quarter_end", "month_end", "tax_date", "treasury_settlement")
        )
        pooled, deviating, regimes, scale = design.pooling
        self.assertEqual(pooled, tuple(range(6)))
        self.assertEqual(deviating, (0, 6, 7, 8, 9))
        self.assertEqual(regimes, (0.0, 1.0, 2.0, 3.0))
        self.assertEqual(scale, ml.REGIME_POOLING_SCALE)
        got = design.row(self._observation(2.0, tax_date=1.0, treasury_settlement=70.0), None)
        self.assertEqual(got[-4:], [0.0, 0.0, 1.0, 70.0])
        self.assertEqual(got[2:6], [0.0, 0.0, 2.0, 140.0])

    def test_the_regime_fit_is_the_pooled_fit_for_a_regime_with_no_training_day(self):
        """A regime unseen in training is served the pooled model, never an extrapolation."""

        design = self.design(regime_pooled=True)
        xs, labels = [], []
        for index in range(300):
            state = float(index % 3)  # state 3 never appears in training
            observation = self._observation(
                state, quarter_end=1.0 if index % 5 == 0 else 0.0, sofr=4.0 + (index % 9) / 50.0,
                treasury_settlement=float(index % 7) * 10.0,
            )
            xs.append(design.row(observation, None))
            labels.append(1 if (state >= 1.0 and index % 4 == 0) else 0)
        served = [design.row(self._observation(3.0, quarter_end=1.0, treasury_settlement=30.0), None)]
        pooled_only = ml._fit_classifier("logistic", [x[:6] for x in xs], labels, [served[0][:6]])
        got = ml._fit_classifier("logistic", xs, labels, served, pooling=design.pooling)
        self.assertEqual(len(got), 1)
        self.assertTrue(0.0 <= got[0] <= 1.0)
        # Deviation columns of an unseen regime are all zero in training, so its
        # coefficients are exactly zero; the served day differs from the pooled
        # model only by the raw columns the pooled part does not carry.
        self.assertAlmostEqual(got[0], pooled_only[0], delta=0.2)

    def test_stronger_shrinkage_brings_a_regime_nearer_the_pooled_fit(self):
        design = self.design(regime_pooled=True)
        xs, labels = [], []
        for index in range(400):
            state = float(index % 4)
            observation = self._observation(
                state, tax_date=1.0 if index % 6 == 0 else 0.0, sofr=4.0 + (index % 9) / 50.0,
                treasury_settlement=float(index % 7) * 10.0,
            )
            xs.append(design.row(observation, None))
            labels.append(1 if (state == 3.0 and index % 9 < 5) else 0)
        served = [design.row(self._observation(3.0, tax_date=1.0, treasury_settlement=30.0), None)]
        pooled, deviating, regimes, _ = design.pooling
        loose = ml._fit_classifier("logistic", xs, labels, served, pooling=(pooled, deviating, regimes, 1.0))
        tight = ml._fit_classifier("logistic", xs, labels, served, pooling=(pooled, deviating, regimes, 0.01))
        flat = ml._fit_classifier("logistic", [x[:6] for x in xs], labels, [served[0][:6]])
        self.assertLess(abs(tight[0] - flat[0]), abs(loose[0] - flat[0]))

    def test_a_backtest_runs_each_variant_under_every_guard(self):
        from repo_model.scarcity import measurement_declaration

        rows = _scarcity_calendar_panel()
        for name, kwargs, form in (
            ("interactions", {"interactions": True}, "logistic"),
            ("interactions_gbm", {"interactions": True}, "gbm"),
            ("regime_pooled", {"regime_pooled": True}, "logistic"),
        ):
            with self.subTest(name=name), measurement_declaration():
                report = baseline.rolling_exceedance_backtest(
                    rows,
                    predictor=ml._scarcity_calendar_predictor(
                        form, _SCARCITY_CALENDAR, _pressure_splits(), _FOUR_LEVEL,
                        minimum_history=60, **kwargs,
                    ),
                    model_name=name,
                    features=_SCARCITY_CALENDAR,
                    registry=_PRESSURE_REGISTRY,
                    decision_time=time(16, 0),
                    taus=(5.0, 10.0),
                    minimum_history=60,
                    refit_every=21,
                    horizon=1,
                )
            self.assertTrue(report.folds)
            settings = report.model_settings["scarcity_calendar"]
            self.assertEqual(bool(settings["interaction_terms"]), "interactions" in kwargs)
            self.assertEqual(settings["regime_partial_pooling"] is not None, "regime_pooled" in kwargs)


class HierarchicalLogisticTests(unittest.TestCase):
    """The hierarchical logistic of the pressure label, shrinkage by empirical Bayes (#386).

    Written first, and watched failing: before the variant existed every test
    here raised `AttributeError: module 'repo_model.ml' has no attribute
    '_empirical_bayes_scale'` or `TypeError: _ScarcityCalendarDesign.__init__()
    got an unexpected keyword argument 'regime_hierarchical'`.

    Recorded mutations (applied in a scratch copy, run, reverted):

    * `_laplace_log_evidence`: the `- 0.5 * logdet` term deleted (the Occam
      factor): killed by `test_the_evidence_prefers_the_smaller_scale_for_an_irrelevant_deviation`
      (`AssertionError`). The same mutation also failed
      `test_regimes_that_agree_are_pooled_by_the_smallest_scale` and
      `test_regimes_that_differ_are_given_a_larger_scale`.
    * `_empirical_bayes_scale`: `x[:, 1]` (the regime column) replaced by
      `x[:, 0]` in the `_pool_columns` call: killed by
      `test_regimes_that_differ_are_given_a_larger_scale` (`AssertionError`).
    """

    def setUp(self):
        require_extra(self)

    def design(self, **kwargs):
        return ml._ScarcityCalendarDesign(
            _SCARCITY_CALENDAR, _pressure_splits(), _FOUR_LEVEL, regime_hierarchical=True, **kwargs
        )

    def _data(self, differ, rows=480):
        """A pooled design with a regime column, labels that do (or do not) depend on the regime."""

        import numpy

        rng = numpy.random.RandomState(7)
        regime = numpy.arange(rows) % 4
        x = rng.normal(size=(rows, 2))
        logit = -2.0 + 0.8 * x[:, 0]
        if differ:
            logit = logit + numpy.array([-2.0, 0.0, 1.0, 3.0])[regime] + (regime == 3) * 1.5 * x[:, 1]
        y = (rng.uniform(size=rows) < 1.0 / (1.0 + numpy.exp(-logit))).astype(int)
        columns = numpy.column_stack([x[:, 0], regime.astype(float), x[:, 1]])
        return columns, y

    def test_the_variant_is_declared_with_no_fixed_scale(self):
        design = self.design()
        self.assertIsNone(design.pooling[3])
        self.assertEqual(design.names, ml._ScarcityCalendarDesign(
            _SCARCITY_CALENDAR, _pressure_splits(), _FOUR_LEVEL, regime_pooled=True).names)
        self.assertEqual(design.settings()["regime_partial_pooling"]["deviation_scale"], "empirical Bayes")

    def test_the_variant_is_one_variant(self):
        with self.assertRaises(ValueError):
            self.design(interactions=True)
        with self.assertRaises(ValueError):
            self.design(monotone=True)
        with self.assertRaises(ValueError):
            ml._ScarcityCalendarDesign(
                _SCARCITY_CALENDAR, _pressure_splits(), _FOUR_LEVEL, regime_hierarchical=True, regime_pooled=True
            )

    def test_the_evidence_prefers_the_smaller_scale_for_an_irrelevant_deviation(self):
        import numpy

        columns, y = self._data(differ=False)
        pooled = (0, 2), (0, 2), (0.0, 1.0, 2.0, 3.0)
        z = (columns - columns.mean(axis=0)) / columns.std(axis=0)
        small = ml._laplace_log_evidence(ml._pool_columns(z, columns[:, 1], *pooled, 0.05), y)
        large = ml._laplace_log_evidence(ml._pool_columns(z, columns[:, 1], *pooled, 4.0), y)
        self.assertGreater(small, large)
        self.assertTrue(numpy.isfinite(small) and numpy.isfinite(large))

    def test_regimes_that_agree_are_pooled_by_the_smallest_scale(self):
        columns, y = self._data(differ=False)
        got = ml._empirical_bayes_scale(columns, y, (0, 2), (0, 2), (0.0, 1.0, 2.0, 3.0))
        self.assertEqual(got, min(ml.REGIME_SHRINKAGE_GRID))

    def test_regimes_that_differ_are_given_a_larger_scale(self):
        agree, differ = self._data(differ=False), self._data(differ=True)
        base = ml._empirical_bayes_scale(*agree, (0, 2), (0, 2), (0.0, 1.0, 2.0, 3.0))
        got = ml._empirical_bayes_scale(*differ, (0, 2), (0, 2), (0.0, 1.0, 2.0, 3.0))
        self.assertGreater(got, base)

    def test_the_fit_records_the_scale_it_chose_and_is_deterministic(self):
        columns, y = self._data(differ=True)
        pooling = ((0, 2), (0, 2), (0.0, 1.0, 2.0, 3.0), None)
        first, second = [], []
        a = ml._fit_classifier("logistic", columns, y, columns[:20], pooling=pooling, shrinkage_trace=first)
        b = ml._fit_classifier("logistic", columns, y, columns[:20], pooling=pooling, shrinkage_trace=second)
        self.assertEqual(a, b)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 1)
        self.assertIn(first[0], ml.REGIME_SHRINKAGE_GRID)
        self.assertTrue(all(0.0 < p < 1.0 for p in a))

    def test_the_regime_effects_add_the_pooled_coefficient_and_the_shrunk_deviation(self):
        import numpy

        # Columns: pooled 0 and 1; deviating 0 and 2 (column 2 is not pooled); two regimes.
        coefficients = numpy.array([0.5, 2.0, 1.0, 0.1, 0.2, 3.0, 0.4, 0.6])
        scale = numpy.array([2.0, 1.0, 4.0])
        got = ml._regime_effects(coefficients, (0, 1), (0, 2), (0.0, 1.0), 0.5, scale)
        self.assertEqual(got["shrink"], 0.5)
        self.assertEqual(got["pooled"], {0: 0.25, 1: 2.0})
        # regime 0: intercept 0.5 * 1.0; column 0: (0.5 + 0.5 * 0.1) / 2; column 2: 0.5 * 0.2 / 4
        self.assertAlmostEqual(got["regimes"][0.0]["intercept"], 0.5)
        self.assertAlmostEqual(got["regimes"][0.0][0], 0.275)
        self.assertAlmostEqual(got["regimes"][0.0][2], 0.025)
        self.assertEqual(got["regimes"][0.0][1], 2.0)
        # regime 1: intercept 0.5 * 3.0; column 0: (0.5 + 0.5 * 0.4) / 2; column 2: 0.5 * 0.6 / 4
        self.assertAlmostEqual(got["regimes"][1.0]["intercept"], 1.5)
        self.assertAlmostEqual(got["regimes"][1.0][0], 0.35)
        self.assertAlmostEqual(got["regimes"][1.0][2], 0.075)

    def test_a_fixed_scale_is_untouched(self):
        columns, y = self._data(differ=True)
        trace = []
        fixed = ((0, 2), (0, 2), (0.0, 1.0, 2.0, 3.0), 0.5)
        ml._fit_classifier("logistic", columns, y, columns[:5], pooling=fixed, shrinkage_trace=trace)
        self.assertEqual(trace, [])

    def test_a_backtest_runs_the_variant_under_every_guard_and_records_the_shrinkage(self):
        from repo_model.scarcity import measurement_declaration

        rows = _scarcity_calendar_panel()
        with measurement_declaration():
            report = baseline.rolling_exceedance_backtest(
                rows,
                predictor=ml._scarcity_calendar_predictor(
                    "logistic", _SCARCITY_CALENDAR, _pressure_splits(), _FOUR_LEVEL,
                    minimum_history=60, regime_hierarchical=True,
                ),
                model_name="hierarchical_logistic",
                features=_SCARCITY_CALENDAR,
                registry=_PRESSURE_REGISTRY,
                decision_time=time(16, 0),
                taus=(5.0, 10.0),
                minimum_history=60,
                refit_every=21,
                horizon=1,
            )
        self.assertTrue(report.folds)
        chosen = report.model_settings["scarcity_calendar"]["regime_partial_pooling"]
        self.assertEqual(chosen["deviation_scale"], "empirical Bayes")
        self.assertTrue(chosen["grid"])


def _history_rows(start, end):
    """Pre-SOFR history rows (#129) on weekdays, EFFR - IOER cycling through +8 bp."""

    from repo_model import effr_history

    effr, ioer, weekly = {}, {}, {"reserve_balances": {}, "tga": {}}
    when, index = start, 0
    printed_through = date(end.year + 1, 1, 2) if end.month == 12 else end + timedelta(days=100)
    while when <= printed_through:
        if when.weekday() < 5:
            effr[when] = 0.25 + ((index % 13) - 6) / 100.0 + (0.08 if index % 13 == 12 else 0.0)
            index += 1
        ioer[when] = 0.25
        if when.weekday() == 2:
            weekly["reserve_balances"][when] = 1000.0 + 10.0 * (index % 7)
            weekly["tga"][when] = 100.0 + 5.0 * (index % 3)
        when += timedelta(days=1)
    return effr_history.history_rows(effr, ioer, weekly, start=start, end=end)


class PooledHistoryTests(unittest.TestCase):
    """The direct logistic pooled with pre-SOFR history (#129)."""

    def setUp(self):
        require_extra(self)
        self.rows = _pressure_panel()

    def backtest(self, history, horizon=1):
        return baseline.rolling_exceedance_backtest(
            self.rows,
            predictor=ml._direct_pressure_predictor(
                "logistic", _PRESSURE_FULL, _pressure_splits(), 60, history=history
            ),
            model_name="pooled_logistic",
            features=_PRESSURE_FULL,
            registry=_PRESSURE_REGISTRY,
            decision_time=time(16, 0),
            taus=(5.0, 10.0),
            minimum_history=60,
            refit_every=21,
            horizon=horizon,
        )

    def test_the_pool_joins_every_fit_behind_a_market_column(self):
        from repo_model import effr_history

        rule = effr_history.HistoryRule(_PRESSURE_REGISTRY, decision_time=time(16, 0), horizon=1)
        history = _history_rows(date(2025, 6, 2), date(2025, 12, 31))
        report = self.backtest((history, rule))
        plain = self.backtest(None)
        self.assertEqual(report.model_settings["design"][-1], ml.HISTORY_MARKET_COLUMN)
        self.assertEqual(report.model_settings["design"][:-1], plain.model_settings["design"])
        pairs = report.model_settings["pooled_history"]["pairs"]
        self.assertGreater(pairs, 100)
        self.assertEqual(report.scored_dates, plain.scored_dates)
        self.assertNotEqual(report.forecast, plain.forecast)

    def test_a_pooled_label_not_yet_public_is_refused(self):
        from repo_model import effr_history

        rule = effr_history.HistoryRule(_PRESSURE_REGISTRY, decision_time=time(16, 0), horizon=1)
        history = _history_rows(date(2025, 6, 2), date(2026, 6, 30))
        with self.assertRaises(LookAheadError):
            self.backtest((history, rule))

    def test_a_history_read_at_another_horizon_is_refused(self):
        from repo_model import effr_history

        rule = effr_history.HistoryRule(_PRESSURE_REGISTRY, decision_time=time(16, 0), horizon=2)
        history = _history_rows(date(2025, 6, 2), date(2025, 12, 31))
        with self.assertRaisesRegex(ValueError, "horizon"):
            self.backtest((history, rule))


class RecalibrationPartsTests(unittest.TestCase):
    """`cross_conformal_parts` and `law_from_band`: CV+ taken apart, and put back (#116).

    The calibration re-diagnosis rebuilds three bands from one CV+ backtest:
    CV+'s own, conformal PID's from the uncalibrated vector, and Mondrian
    CV+'s from the held-out terms restricted to a group. That is a fair
    comparison only if the pieces put back together are CV+ to the bit, so
    that the control is the published model and not a re-implementation of
    it. Red first: written before either name existed (`AttributeError`).
    """

    REGRESSORS = ("on_rrp", "sofr_volume")
    TRAIN_ROWS = 240

    def setUp(self):
        require_extra(self)
        rows = heteroscedastic_frame(self.TRAIN_ROWS + 30)
        self.train = rows[: self.TRAIN_ROWS]
        self.forecasts = rows[self.TRAIN_ROWS - 1 :]
        options = {"minimum_history": 20, "min_samples_leaf": FIXTURE_MIN_SAMPLES_LEAF}
        self.cross = ml.fit_gradient_boosted_quantiles(
            self.train, self.REGRESSORS, calibration="cross_conformal",
            information=gap_rule(0), **options,
        )
        self.plain = ml.fit_gradient_boosted_quantiles(self.train, self.REGRESSORS, **options)

    def test_the_parts_rebuild_the_reported_vector_and_law_exactly(self):
        levels = self.cross.levels
        for row in self.forecasts:
            parts = self.cross.cross_conformal_parts(row)
            lower, upper = ml._cross_conformal_edges(parts.lows, parts.highs, levels)
            self.assertEqual(ml._banded(parts.vector, lower, upper), self.cross.predict(row))
            self.assertEqual(parts.vector, self.plain.predict(row))
            self.assertEqual(
                ml.law_from_band(
                    parts.vector, lower, upper, parts.residual_low, parts.residual_high, levels
                ),
                self.cross.law_knots(row),
            )

    def test_every_held_out_term_is_dated_in_block_order(self):
        parts = self.cross.cross_conformal_parts(self.forecasts[0])
        dates = tuple(
            when for block in self.cross.calibration_blocks for when in block.scored_dates
        )
        self.assertEqual(parts.held_out_dates, dates)
        self.assertEqual(len(parts.lows), len(dates))
        self.assertEqual(len(parts.highs), len(dates))
        self.assertGreater(len(dates), 100)

    def test_the_uncalibrated_law_is_the_band_left_where_it_is(self):
        row = self.forecasts[3]
        vector = self.plain.predict(row)
        residuals = self.plain.residuals
        self.assertEqual(
            ml.law_from_band(
                vector, vector[0], vector[-1], residuals[0], residuals[-1], self.plain.levels
            ),
            self.plain.law_knots(row),
        )

    def test_any_other_calibration_is_refused(self):
        with self.assertRaises(ValueError):
            self.plain.cross_conformal_parts(self.forecasts[0])



def write_recalibration_panel(path):
    """A synthetic 2025 panel with the calendar the scorecaster reads (#116, #125)."""

    days = business_days(date(2025, 6, 2), 170)
    rng = random.Random(20261002)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["date", "sofr", "iorb", "sofr_volume", "quarter_end", "tax_date",
             "days_to_month_end", "treasury_settlement_coupons"]
        )
        for index, when in enumerate(days):
            last = date(when.year + (when.month == 12), when.month % 12 + 1, 1) - timedelta(days=1)
            writer.writerow(
                [when.isoformat(), round(4.33 + rng.gauss(0.0, 0.04), 6), 4.30,
                 2000 + rng.randrange(300),
                 1 if (when.month % 3 == 0 and (last - when).days < 1) else 0,
                 1 if when.day == 15 else 0, (last - when).days,
                 60 if when.day in (15, 30, 31) else 0]
            )


class CalibrationRediagnosisScriptTests(unittest.TestCase):
    """`scripts/calibration_rediagnosis.py` end to end on a synthetic panel (#116).

    It walks the one fold grid through `rolling_persistence_backtest`, so the
    tracked lockbox refuses a locked scored day before any fit, and `--end`
    before the tier scores. On the days it scores, the CV+ control is the band
    the backtest reported (the script refuses otherwise), and all three
    methods are scored on the same days.
    """

    #: The tracked declaration as it stood before #151 opened the near-blind tier.
    TRACKED_LOCKBOX = PRE_OPENING_LOCKBOX
    SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "calibration_rediagnosis.py"

    def setUp(self):
        require_extra(self)
        fewer_boosting_iterations(self)
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.panel = self.tmp / "panel.csv"
        write_recalibration_panel(self.panel)
        spec = importlib.util.spec_from_file_location("calibration_rediagnosis", self.SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def run_script(self, *extra):
        report = self.tmp / "report.json"
        argv = [
            "--panel", str(self.panel), "--decision-time", "16:00",
            "--minimum-history", "40", "--refit-every", "20", "--calibration-folds", "3",
            "--feature", "spread_bps", "--feature", "sofr_volume",
            "--replications", "20", "--report", str(report), *extra,
        ]
        with mock.patch("repo_model.lockbox.DEFAULT_LOCKBOX", self.TRACKED_LOCKBOX):
            self.assertEqual(self.module.main(argv), 0)
        return json.loads(report.read_text(encoding="utf-8"))

    def test_a_locked_scored_day_is_refused_and_an_end_before_the_tier_scores(self):
        with self.assertRaises(LookAheadError) as caught:
            self.run_script()
        self.assertIn("locked near_blind tier", str(caught.exception))
        result = self.run_script("--end", "2025-12-31")
        self.assertLessEqual(result["window"]["last"], "2025-12-31")
        self.assertTrue(result["control_rebuilt_bit_for_bit"])
        days = result["window"]["days"]
        for method in ("cv_plus", "online_pid", "group_conditional"):
            coverage = result["methods"][method]["coverage"]
            self.assertEqual(coverage["all"]["all"]["count"], days)
            self.assertEqual(
                sum(entry["count"] for entry in coverage["volatility_tercile"].values()), days
            )
            self.assertIn("interval", coverage["all"]["all"])
        self.assertAlmostEqual(
            result["methods"]["cv_plus"]["crps_bps"], result["control_crps_bps"], places=12
        )
        paired = result["paired_cv_plus_minus_method"]
        self.assertEqual(
            set(paired["online_pid"]),
            {"crps_difference_bps", "brier_difference_5bp", "brier_difference_10bp"},
        )
        self.assertEqual(sum(result["group_conditional"]["levels_used"].values()), days)



class PidConstantSelectionScriptTests(unittest.TestCase):
    """`scripts/pid_constant_selection.py` end to end on a synthetic panel (#125).

    It walks the one fold grid as #116's script does, so the lockbox refuses a
    locked scored day and `--end` before the tier scores. #122's constants in
    it are #116's `online_pid` band, the nested scheme is chosen at every
    refit block of the grid, and the three methods are scored on the same days.
    """

    #: The tracked declaration as it stood before #151 opened the near-blind tier.
    TRACKED_LOCKBOX = PRE_OPENING_LOCKBOX
    SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

    def setUp(self):
        require_extra(self)
        fewer_boosting_iterations(self)
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.panel = self.tmp / "panel.csv"
        write_recalibration_panel(self.panel)
        self.modules = {}
        for name in ("pid_constant_selection", "calibration_rediagnosis"):
            spec = importlib.util.spec_from_file_location(name, self.SCRIPTS / f"{name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.modules[name] = module

    def run_script(self, name, *extra):
        report = self.tmp / f"{name}.json"
        argv = [
            "--panel", str(self.panel), "--decision-time", "16:00",
            "--minimum-history", "40", "--refit-every", "20", "--calibration-folds", "3",
            "--feature", "spread_bps", "--feature", "sofr_volume",
            "--replications", "20", "--report", str(report), *extra,
        ]
        with mock.patch("repo_model.lockbox.DEFAULT_LOCKBOX", self.TRACKED_LOCKBOX):
            self.assertEqual(self.modules[name].main(argv), 0)
        return json.loads(report.read_text(encoding="utf-8"))

    def test_a_locked_scored_day_is_refused(self):
        with self.assertRaises(LookAheadError) as caught:
            self.run_script("pid_constant_selection")
        self.assertIn("locked near_blind tier", str(caught.exception))

    def test_the_scheme_on_the_grid_before_the_tier(self):
        from repo_model import recalibration

        result = self.run_script("pid_constant_selection", "--end", "2025-12-31")
        self.assertLessEqual(result["window"]["last"], "2025-12-31")
        days = result["window"]["days"]
        for method in ("nested_pid", "fixed_pid", "cv_plus"):
            scores = result["methods"][method]
            self.assertEqual(scores["coverage"]["all"]["all"]["count"], days)
            self.assertIn("interval", scores["crps_bps"]["all"]["all"])
        self.assertAlmostEqual(
            result["methods"]["cv_plus"]["crps_bps"]["all"]["all"]["mean"],
            result["control_crps_bps"], places=12,
        )
        earlier = self.run_script("calibration_rediagnosis", "--end", "2025-12-31")
        self.assertAlmostEqual(
            result["methods"]["fixed_pid"]["crps_bps"]["all"]["all"]["mean"],
            earlier["methods"]["online_pid"]["crps_bps"], places=12,
        )
        blocks = result["nested_selection"]
        self.assertEqual(len(blocks), -(-days // 20))
        self.assertEqual(blocks[0]["past_days"], 0)
        self.assertEqual(blocks[0]["chosen"], recalibration.DECLARED_PID._asdict())
        for block in blocks:
            self.assertLess(block["anchor"], block["first_scored"])
        self.assertEqual(
            set(result["paired_other_minus_nested"]),
            {"fixed_pid_minus_nested_pid", "cv_plus_minus_nested_pid"},
        )
        self.assertEqual(len(result["full_grid"]["points"]), len(recalibration.PID_GRID))
        self.assertIn("not for selection", result["full_grid"]["label"])
        self.assertIn("never the selection", result["split_sample"]["label"])
        self.assertEqual(result["split_sample"]["evaluation_window"]["days"], days)


class ConformalPidPublishTests(unittest.TestCase):
    """`--calibration conformal_pid` on `backtest`, `compare` and `exceedance-backtest` (#124).

    Eleonora's ruling on #123 publishes the funding declaration's gbm with
    conformal PID and the calendar scorecaster, exactly as #122 scored it, with
    the same constants. So the records the three commands write must carry
    #122's PID figures: on one panel and window, the backtest's CRPS and
    coverage, the comparison's CRPS for the PID side, and the exceedance
    record's Brier at +5 and +10 bp each equal what
    `scripts/calibration_rediagnosis.py` reports for `online_pid`.

    Red first: written before the commands took the name (each run was refused
    by `ml.fit_gradient_boosted_quantiles` as an unknown calibration, exit 2).
    """

    TRACKED = Path(__file__).resolve().parents[1]
    SCRIPT = TRACKED / "scripts" / "calibration_rediagnosis.py"
    SELECTION = TRACKED / "scripts" / "pid_constant_selection.py"
    SPLITS = TRACKED / "metadata" / "evaluation_splits.json"
    REGISTRY = TRACKED / "metadata" / "sources.json"
    THRESHOLDS = TRACKED / "metadata" / "stress_thresholds.json"
    LOCKBOX = TRACKED / "metadata" / "lockbox.json"
    COMMON = ("--decision-time", "16:00", "--minimum-history", "40", "--refit-every", "20",
              "--end", "2025-12-31")

    def setUp(self):
        require_extra(self)
        fewer_boosting_iterations(self)
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.panel = self.tmp / "panel.csv"
        write_recalibration_panel(self.panel)
        lockbox = mock.patch("repo_model.lockbox.DEFAULT_LOCKBOX", self.LOCKBOX)
        lockbox.start()
        self.addCleanup(lockbox.stop)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, " ".join(err.getvalue().split())

    def record(self, name, *argv):
        report = self.tmp / name
        code, err = self.run_cli(*argv, "--report", str(report))
        self.assertEqual(code, 0, err)
        return json.loads(report.read_text(encoding="utf-8"))

    def rediagnosis(self):
        spec = importlib.util.spec_from_file_location("calibration_rediagnosis", self.SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = self.tmp / "rediagnosis.json"
        self.assertEqual(
            module.main([
                "--panel", str(self.panel), "--calibration-folds", "3",
                "--feature", "spread_bps", "--feature", "sofr_volume",
                "--replications", "20", "--report", str(report), *self.COMMON,
            ]),
            0,
        )
        return json.loads(report.read_text(encoding="utf-8"))["methods"]["online_pid"]

    def backtest(self, *extra):
        return self.record(
            "backtest.json", "backtest", str(self.panel), "--registry", str(self.REGISTRY),
            "--model", "gbm", "--feature", "spread_bps", "--feature", "sofr_volume",
            *self.COMMON, *extra,
        )

    def test_the_three_records_carry_the_rediagnosis_pid_figures(self):
        pid = self.rediagnosis()
        backtest = self.backtest("--calibration", "conformal_pid", "--splits", str(self.SPLITS))
        self.assertAlmostEqual(backtest["metrics"]["crps_bps"], pid["crps_bps"], places=12)
        self.assertAlmostEqual(
            backtest["metrics"]["interval_coverage"], pid["coverage"]["all"]["all"]["mean"],
            places=12,
        )
        compare = self.record(
            "compare.json", "compare", str(self.panel), "--registry", str(self.REGISTRY),
            "--model-a", "persistence", "--feature-a", "spread_bps",
            "--model-b", "gbm", "--feature-b", "spread_bps", "--feature-b", "sofr_volume",
            "--calibration-b", "conformal_pid", "--loss", "crps",
            "--splits", str(self.SPLITS), *self.COMMON,
        )
        self.assertAlmostEqual(
            compare["comparison"]["model_b"]["crps_bps"], pid["crps_bps"], places=12
        )
        exceedance = self.record(
            "exceedance.json", "exceedance-backtest", "--panel", str(self.panel),
            "--thresholds", str(self.THRESHOLDS), "--registry", str(self.REGISTRY),
            "--model", "gbm", "--feature", "spread_bps", "--feature", "sofr_volume",
            "--calibration", "conformal_pid", "--splits", str(self.SPLITS), *self.COMMON,
        )
        for tau in ("5", "10"):
            self.assertAlmostEqual(
                exceedance["metrics"]["by_tau"][tau]["brier"], pid["brier"][tau + ".0"],
                places=12,
            )
        for declaration in (
            backtest["declaration"], compare["declaration"]["model_b"], exceedance["declaration"]
        ):
            self.assertEqual(declaration["calibration"], "conformal_pid")
            self.assertNotIn("calibration_folds", declaration)
            constants = declaration["calibration_constants"]
            self.assertEqual(constants["PID_STEP"], recalibration.PID_STEP)
            self.assertEqual(
                constants["SCORECASTER_INDICATORS"], list(recalibration.SCORECASTER_INDICATORS)
            )
        self.assertNotIn("calibration", compare["declaration"]["model_a"])
        # And it is not the uncalibrated model's record.
        plain = self.backtest()
        self.assertNotEqual(plain["metrics"]["crps_bps"], backtest["metrics"]["crps_bps"])

    def selection(self):
        spec = importlib.util.spec_from_file_location("pid_constant_selection", self.SELECTION)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = self.tmp / "selection.json"
        self.assertEqual(
            module.main([
                "--panel", str(self.panel), "--calibration-folds", "3",
                "--feature", "spread_bps", "--feature", "sofr_volume",
                "--replications", "20", "--report", str(report), *self.COMMON,
            ]),
            0,
        )
        return json.loads(report.read_text(encoding="utf-8"))

    def test_the_three_records_carry_the_nested_selection_figures(self):
        """`--calibration conformal_pid_nested` is #125's `nested_pid` (rulings #136, #134).

        The published funding declaration is republished with conformal PID
        whose constants are chosen by nested walk-forward selection. On one
        panel and window, the backtest's CRPS and coverage, the comparison's
        CRPS for its PID side, and the exceedance record's Brier at +5 and
        +10 bp each equal what `scripts/pid_constant_selection.py` reports for
        `nested_pid`, and every record names the point chosen at each refit
        block, as the script does.

        Red first: written before the commands took the name (each run was
        refused by `ml.fit_gradient_boosted_quantiles` as an unknown
        calibration, exit 2).
        """

        selection = self.selection()
        nested = selection["methods"]["nested_pid"]
        chosen = [block["chosen"] for block in selection["nested_selection"]]
        flags = ("--calibration", "conformal_pid_nested", "--splits", str(self.SPLITS))
        backtest = self.backtest(*flags)
        self.assertAlmostEqual(
            backtest["metrics"]["crps_bps"], nested["crps_bps"]["all"]["all"]["mean"], places=12
        )
        self.assertAlmostEqual(
            backtest["metrics"]["interval_coverage"], nested["coverage"]["all"]["all"]["mean"],
            places=12,
        )
        compare = self.record(
            "compare.json", "compare", str(self.panel), "--registry", str(self.REGISTRY),
            "--model-a", "persistence", "--feature-a", "spread_bps",
            "--model-b", "gbm", "--feature-b", "spread_bps", "--feature-b", "sofr_volume",
            "--calibration-b", "conformal_pid_nested", "--loss", "crps",
            "--splits", str(self.SPLITS), *self.COMMON,
        )
        self.assertAlmostEqual(
            compare["comparison"]["model_b"]["crps_bps"],
            nested["crps_bps"]["all"]["all"]["mean"],
            places=12,
        )
        exceedance = self.record(
            "exceedance.json", "exceedance-backtest", "--panel", str(self.panel),
            "--thresholds", str(self.THRESHOLDS), "--registry", str(self.REGISTRY),
            "--model", "gbm", "--feature", "spread_bps", "--feature", "sofr_volume",
            *flags, *self.COMMON,
        )
        for tau in ("5", "10"):
            self.assertAlmostEqual(
                exceedance["metrics"]["by_tau"][tau]["brier"],
                nested["brier"][tau + "bp"]["all"]["all"]["mean"],
                places=12,
            )
        for declaration, account in (
            (backtest["declaration"], backtest["calibration_account"]),
            (compare["declaration"]["model_b"], compare["calibration_account_b"]),
            (exceedance["declaration"], exceedance["calibration_account"]),
        ):
            self.assertEqual(declaration["calibration"], "conformal_pid_nested")
            self.assertNotIn("calibration_folds", declaration)
            self.assertEqual(declaration["calibration_selection"]["refit_every"], 20)
            self.assertEqual([block["chosen"] for block in account["blocks"]], chosen)
        self.assertNotIn("calibration_account_a", compare)

    def test_the_leap_call_runs_beside_an_online_calibration(self):
        """`exceedance-backtest` takes #139's leap call and #124's online calibration together.

        The leap probabilities are read off the predictor's own curves, not the
        calibrated law, and the record says so. The calibrated curves, and every
        figure and calibration account from them, are what the run gives
        without the leap call.

        Red first: before the merge of #124 into #139 wrote the note, the record
        had no `model_curves` key (`KeyError`).
        """

        from repo_model import baseline

        real = baseline.rolling_exceedance_backtest

        def without_leap(*args, **kwargs):
            kwargs["leap_jump_bp"] = None
            return real(*args, **kwargs)

        argv = (
            "exceedance-backtest", "--panel", str(self.panel),
            "--thresholds", str(self.THRESHOLDS), "--registry", str(self.REGISTRY),
            "--model", "gbm", "--feature", "spread_bps", "--feature", "sofr_volume",
            "--calibration", "conformal_pid", "--splits", str(self.SPLITS), *self.COMMON,
        )
        record = self.record("with_leap.json", *argv)
        with mock.patch("repo_model.cli_eval.rolling_exceedance_backtest", without_leap):
            plain = self.record("without_leap.json", *argv)
        self.assertEqual(record["metrics"], plain["metrics"])
        self.assertEqual(record["calibration_account"], plain["calibration_account"])
        self.assertIn("unavailable", plain["onset"]["leap"])
        leap = record["onset"]["leap"]
        self.assertNotIn("unavailable", leap)
        self.assertIn("before the online calibration", leap["model_curves"])

    def test_a_limitation_is_recorded_as_given(self):
        text = "Scored only before 2026-01-01; the 2020 regression is stated in #122."
        backtest = self.backtest(
            "--calibration", "conformal_pid", "--splits", str(self.SPLITS),
            "--limitation", text, "--limitation", "A second one.",
        )
        self.assertEqual(backtest["limitations"], [text, "A second one."])
        self.assertNotIn("limitations", self.backtest())

    def test_what_conformal_pid_cannot_take_is_refused(self):
        base = ("backtest", str(self.panel), "--registry", str(self.REGISTRY),
                "--feature", "spread_bps", "--feature", "sofr_volume", *self.COMMON,
                "--report", str(self.tmp / "refused.json"))
        for extra, phrase in (
            (("--model", "gbm", "--calibration", "conformal_pid"), "--splits"),
            (("--model", "gbm", "--calibration", "conformal_pid", "--splits", str(self.SPLITS),
              "--calibration-folds", "5"), "calibration-folds"),
            (("--model", "persistence", "--calibration", "conformal_pid",
              "--splits", str(self.SPLITS)), "takes no band calibration"),
        ):
            with self.subTest(extra=extra):
                code, err = self.run_cli(*base, *extra)
                self.assertEqual(code, 2)
                self.assertIn(phrase, err)
                self.assertFalse((self.tmp / "refused.json").exists())


class PressureModelPublishTests(unittest.TestCase):
    """`scripts/pressure_model_v1.py publish`: pressure model v1's record (#124, ruling #134).

    The published candidate is `distributional_gbm+recalibrated`: the
    probability read from the funding declaration's distribution, calibrated
    by nested-selection conformal PID, recalibrated out of fold, at one
    horizon, paired with both benchmarks. Its record must state the
    recalibrated forecasts' own metrics (`pressure.recalibrated` keeps the
    metrics of the forecasts it replaces), declare the horizon, the
    calibration and the recalibration, and score no locked day.

    At horizons of 2 or more the scorecaster's coupon-settlement indicator is
    not public at the decision instant under its declaration (one business day
    ahead). Eleonora's ruling on #170 (option A) drops it from the scorecaster
    there, a declared variant the record states; until then the run was
    refused with `LookAheadError`, which this class pinned.
    """

    TRACKED = Path(__file__).resolve().parents[1]
    SCRIPT = TRACKED / "scripts" / "pressure_model_v1.py"
    LOCKBOX = TRACKED / "metadata" / "lockbox.json"

    def setUp(self):
        require_extra(self)
        fewer_boosting_iterations(self)
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.panel = self.tmp / "panel.csv"
        write_recalibration_panel(self.panel)
        spec = importlib.util.spec_from_file_location("pressure_model_v1", self.SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        for name, value in (
            ("GBM_FEATURES", ("spread_bps", "sofr_volume")),
            ("MINIMUM_HISTORY", 40),
            ("REFIT_EVERY", 20),
        ):
            patcher = mock.patch.object(self.module, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        lockbox = mock.patch("repo_model.lockbox.DEFAULT_LOCKBOX", self.LOCKBOX)
        lockbox.start()
        self.addCleanup(lockbox.stop)

    def test_the_record_states_the_recalibrated_forecasts_metrics(self):
        from repo_model import pressure as pressure_module

        report = self.tmp / "pressure.json"
        with contextlib.redirect_stdout(io.StringIO()):
            code = self.module.main([
                "publish", "--panel", str(self.panel), "--horizon", "1",
                "--report", str(report), "--limitation", "Narrow claim.",
            ])
        self.assertEqual(code, 0)
        record = json.loads(report.read_text(encoding="utf-8"))
        declaration = record["declaration"]
        self.assertEqual(declaration["model"], "distributional_gbm+recalibrated")
        self.assertEqual(declaration["horizon"], 1)
        self.assertEqual(declaration["calibration"], "conformal_pid_nested")
        self.assertEqual(declaration["recalibration"], pressure_module.RECALIBRATION)
        self.assertEqual(declaration["end"], "2025-12-31")
        self.assertEqual(record["limitations"], ["Narrow claim."])
        self.assertLessEqual(record["folds"]["last"]["scored_date"], "2025-12-31")
        self.assertEqual(set(record["benchmarks"]), {"calendar_climatology", "persistence_logistic"})
        self.assertTrue(record["calibration_account"]["blocks"])
        # The metrics are the recalibrated forecasts', computed again: the
        # paired comparison reads the same forecasts, so its model Brier and
        # the record's agree.
        for tau in ("5", "10"):
            paired = record["benchmarks"]["persistence_logistic"]["by_tau"][tau]
            self.assertAlmostEqual(
                record["metrics"]["by_tau"][tau]["brier"], paired["model_brier"], places=12
            )

    def test_a_longer_horizon_runs_the_declared_variant(self):
        from repo_model import recalibration

        report = self.tmp / "pressure_h2.json"
        with contextlib.redirect_stdout(io.StringIO()):
            code = self.module.main([
                "publish", "--panel", str(self.panel), "--horizon", "2",
                "--report", str(report),
            ])
        self.assertEqual(code, 0)
        declaration = json.loads(report.read_text(encoding="utf-8"))["declaration"]
        self.assertEqual(declaration["horizon"], 2)
        self.assertEqual(declaration["calibration"], "conformal_pid_nested")
        self.assertEqual(
            declaration["calibration_constants"]["SCORECASTER_INDICATORS"],
            list(recalibration.SCORECASTER_INDICATORS_LONG_HORIZON),
        )
        self.assertEqual(declaration["scorecaster_variant"], recalibration.SCORECASTER_VARIANT)

    def test_the_event_listed_thresholds_carry_no_pooled_figure(self):
        report = self.tmp / "pressure_events.json"
        with contextlib.redirect_stdout(io.StringIO()):
            code = self.module.main([
                "publish", "--panel", str(self.panel), "--horizon", "1", "--report", str(report),
                "--event-list", "20", "--event-list", "50",
            ])
        self.assertEqual(code, 0)
        record = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(record["declaration"]["event_list"]["taus_bp"], [20.0, 50.0])
        for tau in ("20", "50"):
            entry = record["metrics"]["by_tau"][tau]
            self.assertEqual(entry["reporting"], "event_list")
            self.assertNotIn("brier", entry)
            for bench in record["benchmarks"].values():
                self.assertNotIn(tau, bench["by_tau"])
        self.assertIn("brier", record["metrics"]["by_tau"]["5"])

    def test_horizon_one_declares_no_variant(self):
        from repo_model import recalibration

        report = self.tmp / "pressure_h1.json"
        with contextlib.redirect_stdout(io.StringIO()):
            self.module.main([
                "publish", "--panel", str(self.panel), "--horizon", "1", "--report", str(report),
            ])
        declaration = json.loads(report.read_text(encoding="utf-8"))["declaration"]
        self.assertEqual(
            declaration["calibration_constants"]["SCORECASTER_INDICATORS"],
            list(recalibration.SCORECASTER_INDICATORS),
        )
        self.assertNotIn("scorecaster_variant", declaration)


# --------------------------------------------------------------------------
# Dynamic pressure logit, its ordinal version and the stacked combiner (#137)
# --------------------------------------------------------------------------

_DYNAMIC_FEATURES = (
    "spread_bps", "reserve_balances", "days_to_month_end", "quarter_end", "tax_date",
)


class _DynamicConformance(_PressureConformance):
    """The conformance suite against a dynamic pressure model.

    Rule bound like the direct models, and handed each forecast's as-of
    history, which the lagged index is read off: here the training frame.
    """

    def make_predictor(self):
        predictor = type(self).FACTORY(
            _PRESSURE_CALENDAR, _pressure_splits(), minimum_history=self.MINIMUM_HISTORY
        )
        rule = ml.InformationRule(
            _PRESSURE_REGISTRY, _PRESSURE_CALENDAR, decision_time=time(16, 0)
        )

        def bound(train_rows, feature_rows, taus):
            return predictor(
                train_rows, feature_rows, taus, information=rule,
                histories=tuple(train_rows for _ in feature_rows),
            )

        return bound


class DynamicLogitConformanceTests(_DynamicConformance, unittest.TestCase):
    """The conformance suite against `ml.dynamic_logit_exceedance`."""

    IMPLEMENTATION = staticmethod(ml.dynamic_logit_exceedance)
    FACTORY = staticmethod(ml.dynamic_logit_exceedance)


class DynamicOrdinalConformanceTests(_DynamicConformance, unittest.TestCase):
    """The conformance suite against `ml.dynamic_ordinal_exceedance`."""

    IMPLEMENTATION = staticmethod(ml.dynamic_ordinal_exceedance)
    FACTORY = staticmethod(ml.dynamic_ordinal_exceedance)


class DynamicPressureModelTests(unittest.TestCase):
    """The dynamic logit's terms, its lagged index and the ordinal's coherence (#137)."""

    def setUp(self):
        require_extra(self)
        self.rows = _pressure_panel()

    def backtest(self, factory, horizon=1, taus=(5.0, 10.0)):
        return baseline.rolling_exceedance_backtest(
            self.rows,
            predictor=factory(_DYNAMIC_FEATURES, _pressure_splits(), minimum_history=60),
            model_name=factory.__name__,
            features=_DYNAMIC_FEATURES,
            registry=_PRESSURE_REGISTRY,
            decision_time=time(16, 0),
            taus=taus,
            minimum_history=60,
            refit_every=21,
            horizon=horizon,
        )

    def test_every_term_is_declared_in_the_settings(self):
        """The design, the lagged event indicator and the lagged index, by name."""

        report = self.backtest(ml.dynamic_logit_exceedance)
        settings = report.model_settings
        self.assertEqual(
            tuple(settings["design"]),
            (
                "spread_bps", "reserve_balances",
                "quarter_end", "month_end", "tax_date",
                "quarter_end_x_scarcity", "month_end_x_scarcity", "tax_date_x_scarcity",
                "lagged_event",
            ),
        )
        self.assertEqual(settings["lagged_index"], ml.DYNAMIC_LOGIT_SETTINGS["lagged_index"])
        self.assertEqual(
            tuple(settings["persistence_grid"]), ml.DYNAMIC_LOGIT_SETTINGS["persistence_grid"]
        )
        self.assertIn(settings["persistence"], ml.DYNAMIC_LOGIT_SETTINGS["persistence_grid"])

    def test_coupon_settlement_is_a_scheduled_term_interacted_with_scarcity(self):
        design = ml._PressureDesign(
            ("spread_bps", "reserve_balances", "days_to_month_end", "quarter_end",
             "tax_date", "treasury_settlement_coupons"),
            _pressure_splits(),
        )
        self.assertEqual(
            design.names,
            (
                "spread_bps", "reserve_balances",
                "quarter_end", "month_end", "tax_date", "treasury_settlement_coupons",
                "quarter_end_x_scarcity", "month_end_x_scarcity", "tax_date_x_scarcity",
                "treasury_settlement_coupons_x_scarcity",
            ),
        )

    def test_the_lagged_index_is_the_chain_through_each_rows_anchor(self):
        """`index_t = x_t + alpha * index_anchor(t)`; a chain starts stationary."""

        import numpy

        xs = [None, [1.0, 2.0], [3.0, 0.0], [0.5, 1.0], None, [2.0, 2.0]]
        anchors = [-1, -1, 1, 1, 3, 4]
        got = ml._index_chain(xs, anchors, 0.5)
        self.assertIsNone(got[0])
        numpy.testing.assert_allclose(got[1], [2.0, 4.0])  # x / (1 - alpha)
        numpy.testing.assert_allclose(got[2], [3.0 + 1.0, 0.0 + 2.0])
        numpy.testing.assert_allclose(got[3], [0.5 + 1.0, 1.0 + 2.0])
        self.assertIsNone(got[4])
        numpy.testing.assert_allclose(got[5], [4.0, 4.0])  # anchor has no index
        at_zero = ml._index_chain(xs, anchors, 0.0)
        numpy.testing.assert_allclose(at_zero[2], [3.0, 0.0])

    def test_an_anchor_at_or_after_its_own_row_is_refused(self):
        """The chain reads only an earlier row; a row its own anchor is leakage.

        The line carries `pragma: no cover` because `history_ends` always names
        an earlier row; the guard is driven directly all the same.

        Recorded mutation (CLAUDE.md): in `ml._index_chain`, `if anchor >=
        position:` mutated to `if False:`. This test then errors,
        raising `IndexError` ("list index out of range"): the row's index is
        read from a chain not yet built.
        """

        xs = [[1.0, 2.0], [3.0, 0.0], [0.5, 1.0]]
        for anchors in ([0, 0, 1], [-1, 2, 1]):
            with self.subTest(anchors=anchors):
                with self.assertRaisesRegex(LookAheadError, "is not before it"):
                    ml._index_chain(xs, anchors, 0.5)

    def test_a_backtest_at_horizon_three_runs_under_every_guard(self):
        """The lagged index is read off each forecast's own as-of history.

        `history_ends` names each history's last row, so the fold loop checks
        it ends at the forecast's anchor (stale or ahead are both refused).
        """

        for factory in (ml.dynamic_logit_exceedance, ml.dynamic_ordinal_exceedance):
            with self.subTest(factory=factory.__name__):
                report = self.backtest(factory, horizon=3)
                self.assertEqual(report.horizon, 3)
                self.assertGreater(len(report.folds), 40)

    def test_the_ordinal_probabilities_are_coherent_on_every_day(self):
        """P(> +10) <= P(> +5) on every scored day, from the joint fit itself."""

        for horizon in (1, 2):
            report = self.backtest(ml.dynamic_ordinal_exceedance, horizon=horizon)
            for when, (above_5, above_10) in zip(report.scored_dates, report.forecast):
                with self.subTest(horizon=horizon, day=when):
                    self.assertLessEqual(above_10, above_5)
                    self.assertGreater(above_5, 0.0)
                    self.assertLess(above_5, 1.0)

    def test_the_ordinal_thresholds_are_ordered_by_construction(self):
        """The fit's cut points rise with tau whatever the data, so no running minimum is needed."""

        import numpy

        rng = numpy.random.default_rng(137)
        x = rng.normal(size=(200, 3))
        categories = numpy.clip((x[:, 0] * 1.5 + rng.normal(size=200)).round().astype(int) + 1, 0, 2)
        fit = ml._fit_ordinal(x, categories, 2)
        self.assertLess(fit.thresholds[0], fit.thresholds[1])
        p = fit.exceedance(rng.normal(size=(50, 3)) * 5.0)
        self.assertTrue(numpy.all(p[:, 1] <= p[:, 0]))

    def test_without_histories_it_refuses(self):
        rows = _with_calendar(self.rows)
        rule = ml.InformationRule(
            _PRESSURE_REGISTRY, _PRESSURE_CALENDAR, decision_time=time(16, 0)
        )
        for factory in (ml.dynamic_logit_exceedance, ml.dynamic_ordinal_exceedance):
            predictor = factory(_PRESSURE_CALENDAR, _pressure_splits())
            with self.subTest(factory=factory.__name__), self.assertRaises(ValueError):
                predictor(rows[:-1], rows[-1:], (5.0,), information=rule)

    def test_the_ordinal_refuses_taus_out_of_order(self):
        rows = _with_calendar(self.rows)
        rule = ml.InformationRule(
            _PRESSURE_REGISTRY, _PRESSURE_CALENDAR, decision_time=time(16, 0)
        )
        predictor = ml.dynamic_ordinal_exceedance(_PRESSURE_CALENDAR, _pressure_splits())
        with self.assertRaises(ValueError):
            predictor(rows[:-1], rows[-1:], (10.0, 5.0), information=rule, histories=(rows[:-1],))

    def test_both_are_selectable_by_name_and_read_the_splits(self):
        for name in ("dynamic_logit", "dynamic_ordinal"):
            choice = cli_eval.MODEL_FACTORIES[name]
            self.assertTrue(choice.takes_splits)
            self.assertTrue(choice.needs_ml_extra)


def _on_tau_panel():
    """`_pressure_panel` with every spread moved to 0 or exactly +5 bp (#155).

    +5 bp is SOFR 2.00 against IORB 1.95 as two-decimal legs, which binary
    floating point reads as just above five; the last row is +6 bp, a positive
    no fold trains on.
    """

    rows = _pressure_panel()
    out = []
    for index, row in enumerate(rows):
        if index == len(rows) - 1:
            legs = (2.01, 1.95)
        else:
            legs = (2.00, 1.95) if row.spread_bps > 2.0 else (1.95, 1.95)
        out.append(DailyObservation(row.date, {**row.values, "sofr": legs[0], "iorb": legs[1]}))
    return out


class WholeBpLabelTests(unittest.TestCase):
    """The ml models' labels and lagged indicators read whole basis points (#155).

    Written red first: on main the day exactly on +5 bp was labelled above it,
    so each fit had two label values and served a probability above zero, and
    the lagged indicator was 1.
    """

    def setUp(self):
        require_extra(self)
        self.rows = _on_tau_panel()
        on_tau = [row.spread_bps for row in self.rows[:-1] if row.spread_bps > 1.0]
        self.assertTrue(on_tau)
        self.assertTrue(all(value > 5.0 and round(value) == 5 for value in on_tau))

    def test_the_lagged_indicator_is_zero_on_tau(self):
        self.assertEqual(
            ml._with_indicators([[5.000000000000004, 1.0]], (5.0,)),
            [[5.000000000000004, 1.0, 0.0]],
        )
        self.assertEqual(ml._with_indicators([[6.0, 1.0]], (5.0,)), [[6.0, 1.0, 1.0]])

    def test_the_direct_models_label_no_day_on_tau(self):
        rule = ml.InformationRule(
            _PRESSURE_REGISTRY, _PRESSURE_CALENDAR, decision_time=time(16, 0), horizon=1
        )
        rows = _with_calendar(self.rows[:-1])
        info = rule.information_set([row.date for row in rows], len(rows) - 1)
        observation = rule.observation(rows, info)
        for factory in (ml.pressure_logistic_exceedance, ml.pressure_classifier_exceedance):
            with self.subTest(factory=factory.__name__):
                predictor = factory(_PRESSURE_CALENDAR, _pressure_splits())
                got = predictor(rows[:-1], (observation,), (5.0,), information=rule)
                self.assertEqual(got.curves[0][0], 0.0)

    def test_the_dynamic_models_label_no_day_on_tau(self):
        for factory in (ml.dynamic_logit_exceedance, ml.dynamic_ordinal_exceedance):
            with self.subTest(factory=factory.__name__):
                report = baseline.rolling_exceedance_backtest(
                    self.rows,
                    predictor=factory(_DYNAMIC_FEATURES, _pressure_splits(), minimum_history=60),
                    model_name=factory.__name__,
                    features=_DYNAMIC_FEATURES,
                    registry=_PRESSURE_REGISTRY,
                    decision_time=time(16, 0),
                    taus=(5.0, 10.0),
                    minimum_history=60,
                    refit_every=21,
                )
                self.assertEqual({curve[0] for curve in report.forecast}, {0.0})
                self.assertEqual(report.outcomes[-1], (1, 0))


class StackedCombinerTests(unittest.TestCase):
    """The stacked combiner is fitted on out-of-fold base forecasts only (#137)."""

    @classmethod
    def setUpClass(cls):
        from test_pressure import backtest, spreads, weekday_rows
        from repo_model import pressure
        from repo_model.baseline import calendar_climatology_exceedance

        cls.rows = weekday_rows(spreads())
        persistence = backtest(cls.rows, horizon=3)
        calendar = baseline.rolling_exceedance_backtest(
            cls.rows,
            predictor=calendar_climatology_exceedance(_pressure_splits(), minimum_history=40),
            model_name="calendar_climatology",
            features=("spread_bps", "days_to_month_end", "quarter_end", "tax_date"),
            registry=_PRESSURE_REGISTRY,
            decision_time=time(16, 0),
            taus=(5.0, 10.0),
            minimum_history=40,
            refit_every=21,
            horizon=3,
        )
        cls.bases = {
            "persistence_logistic": persistence,
            "calendar_climatology": calendar,
            "recalibrated": pressure.recalibrated(persistence),
        }
        cls.options = {"minimum_pairs": 60, "minimum_events": 5}

    def setUp(self):
        require_extra(self)

    def blocks(self, report):
        folds = report.folds
        starts = [i for i in range(len(folds)) if i == 0 or folds[i].train_end != folds[i - 1].train_end]
        return list(zip(starts, starts[1:] + [len(folds)]))

    def test_the_combiner_never_sees_an_in_sample_base_forecast(self):
        """A base forecast made by a fit whose training labels include its own day is refused.

        The combiner's pairs are base forecasts of days whose outcomes were
        observable at the combiner's fit. Each must be out of fold: made by a
        base fit trained only on labels before the day it forecast. Here one
        base's fold is relabelled as fitted through its own scored day, as an
        in-sample (fitted-value) forecast would be, inside the first fitted
        block's window.

        Written red first: before `_check_out_of_fold` existed the combiner
        fitted on that pair and returned (`AssertionError`, "LookAheadError not
        raised").

        Recorded mutation (CLAUDE.md), the out-of-fold check dropped: in
        `ml._check_out_of_fold`, `if fold.train_end >= fold.scored_date:`
        mutated to `if False:`. This test then fails, raising `AssertionError`
        ("LookAheadError not raised").
        """

        import dataclasses as dc

        base = self.bases["calendar_climatology"]
        folds = list(base.folds)
        folds[5] = dc.replace(folds[5], train_end=folds[5].scored_date)
        bad = {**self.bases, "calendar_climatology": dc.replace(base, folds=tuple(folds))}
        with self.assertRaises(LookAheadError):
            ml.stacked_combiner(bad, **self.options)
        # And the honest bases combine.
        ml.stacked_combiner(self.bases, **self.options)

    def test_the_combiner_never_learns_from_an_outcome_not_yet_observable(self):
        """A pair whose day is scored after the combiner's fit is refused.

        Recorded mutation (CLAUDE.md): in `ml._check_out_of_fold`, `if
        fold.scored_date > fit_end:` mutated to `if False:`. This test then
        fails, raising `AssertionError` ("LookAheadError not raised"): the fold
        here is out of fold, so only this guard can refuse it.
        """

        from types import SimpleNamespace

        fold = SimpleNamespace(scored_date=date(2026, 3, 10), train_end=date(2026, 3, 5))
        bases = {"stub": SimpleNamespace(folds=(fold,))}
        with self.assertRaisesRegex(LookAheadError, "not yet observable"):
            ml._check_out_of_fold(bases, [0], date(2026, 3, 9))
        ml._check_out_of_fold(bases, [0], date(2026, 3, 10))

    def test_each_block_is_the_fit_on_its_observable_out_of_fold_past(self):
        """At horizon 3 a block's last days are not yet observable at the next fit."""

        import numpy

        combined = ml.stacked_combiner(self.bases, **self.options)
        names = list(self.bases)
        floor = ml.STACKED_COMBINER["probability_floor"]

        def logit(p):
            p = min(1 - floor, max(floor, p))
            return math.log(p / (1 - p))

        checked = 0
        report = self.bases[names[0]]
        for start, stop in self.blocks(report):
            end_label = report.folds[start].train_end
            past = [i for i in range(start) if report.folds[i].scored_date <= end_label]
            fits = []
            for position in range(2):
                outcomes = [report.outcomes[i][position] for i in past]
                if len(past) < 60 or not 5 <= sum(outcomes) < len(past):
                    fits.append(None)
                    continue
                x = numpy.asarray(
                    [[logit(self.bases[n].forecast[i][position]) for n in names] for i in past]
                )
                fits.append(ml._fit_logit(x, numpy.asarray(outcomes)))
            if None in fits:
                continue
            for index in range(start, stop):
                want = [
                    float(fit.probability(numpy.asarray(
                        [[logit(self.bases[n].forecast[index][position]) for n in names]]
                    ))[0])
                    for position, fit in enumerate(fits)
                ]
                # The curve is non-increasing in tau by a running minimum.
                self.assertAlmostEqual(combined.forecast[index][0], want[0], places=12)
                self.assertAlmostEqual(combined.forecast[index][1], min(want), places=12)
                checked += 1
        self.assertGreater(checked, 50)
        self.assertEqual(combined.model_name, "stacked_combiner")
        self.assertEqual(combined.scored_dates, report.scored_dates)

    def test_before_the_minimum_it_is_the_mean_logit(self):
        combined = ml.stacked_combiner(self.bases, minimum_pairs=10_000, minimum_events=5)
        floor = ml.STACKED_COMBINER["probability_floor"]

        def logit(p):
            p = min(1 - floor, max(floor, p))
            return math.log(p / (1 - p))

        for index in (0, len(combined.folds) - 1):
            mean = sum(logit(b.forecast[index][0]) for b in self.bases.values()) / len(self.bases)
            self.assertAlmostEqual(combined.forecast[index][0], 1 / (1 + math.exp(-mean)), places=12)

    def test_bases_on_different_grids_are_refused(self):
        import dataclasses as dc

        base = self.bases["calendar_climatology"]
        short = dc.replace(
            base,
            folds=base.folds[1:], scored_dates=base.scored_dates[1:],
            forecast=base.forecast[1:], outcomes=base.outcomes[1:],
        )
        with self.assertRaises(ValueError):
            ml.stacked_combiner({**self.bases, "calendar_climatology": short}, **self.options)


class PairedBootstrapPValueTests(unittest.TestCase):
    """`ml.paired_bootstrap_p_values`: one-sided p-values on shared resamples (#187).

    The cleared-DVP segment test (`repo_model.dvp_segment`) Holm-corrects a
    family of paired comparisons, so each needs a p-value for improvement and
    one for deterioration. Each is the share of null-centred stationary
    bootstrap means at least as extreme as the observed mean, with the usual
    +1 so no p-value is zero.
    """

    def setUp(self):
        require_extra(self)

    def test_a_clear_improvement_and_a_clear_deterioration(self):
        rng = random.Random(7)
        better = [0.5 + rng.gauss(0.0, 0.2) for _ in range(300)]
        worse = [-value for value in better]
        noise = [rng.gauss(0.0, 1.0) for _ in range(300)]
        (b_up, b_down), (w_up, w_down), (n_up, n_down) = ml.paired_bootstrap_p_values(
            [better, worse, noise], block_length=2, seed=11, replications=999
        )
        self.assertEqual(b_up, 1 / 1000)
        self.assertGreater(b_down, 0.99)
        self.assertEqual(w_down, 1 / 1000)
        self.assertGreater(w_up, 0.99)
        self.assertTrue(0.05 < n_up < 0.95 and 0.05 < n_down < 0.95)

    def test_the_resamples_are_shared_and_reproducible(self):
        series = [[0.1, -0.2, 0.3, 0.05, -0.1, 0.2] * 10, [0.0, 0.1, -0.1, 0.2, 0.0, 0.1] * 10]
        first = ml.paired_bootstrap_p_values(series, block_length=3, seed=5, replications=200)
        again = ml.paired_bootstrap_p_values(series, block_length=3, seed=5, replications=200)
        self.assertEqual(first, again)
        alone = ml.paired_bootstrap_p_values(series[1:], block_length=3, seed=5, replications=200)
        self.assertEqual(alone[0], first[1])

    def test_it_matches_a_direct_computation(self):
        """The count matrix is the resample: checked against summing each resample's draws."""

        from repo_model.metrics import stationary_bootstrap_indices

        series = [0.3, -0.1, 0.2, 0.0, -0.4, 0.5, 0.1, -0.2]
        mean = sum(series) / len(series)
        rng = random.Random(3)
        up = down = 0
        for _ in range(50):
            indices = stationary_bootstrap_indices(len(series), 2, rng)
            centred = sum(series[i] for i in indices) / len(series) - mean
            up += centred >= mean - 1e-12
            down += centred <= mean + 1e-12
        ((p_up, p_down),) = ml.paired_bootstrap_p_values([series], block_length=2, seed=3, replications=50)
        self.assertAlmostEqual(p_up, (1 + up) / 51)
        self.assertAlmostEqual(p_down, (1 + down) / 51)

    def test_series_of_different_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            ml.paired_bootstrap_p_values([[0.1, 0.2], [0.1]], block_length=1, seed=1, replications=10)



# --------------------------------------------------------------------------
# Markov-switching regimes (#384)
# --------------------------------------------------------------------------


def _regime_series(count=1500, seed=1, stay_calm=(0.97, 0.97), leave_stress=(0.85, 0.85)):
    """A calm/stressed spread series and its covariate; the covariate picks the persistence."""

    rng = random.Random(seed)
    spreads, covariates, state = [], [], 0
    for index in range(count):
        z = 1 if (index // 250) % 2 else 0
        if state == 0 and rng.random() > stay_calm[z]:
            state = 1
        elif state == 1 and rng.random() > leave_stress[z]:
            state = 0
        spreads.append(rng.gauss((0.0, 8.0)[state], (1.0, 4.0)[state]))
        covariates.append(z)
    return spreads, covariates


class MarkovSwitchingTests(unittest.TestCase):
    def setUp(self):
        require_extra(self)

    def test_em_recovers_a_two_state_law(self):
        spreads, covariates = _regime_series()
        fitted = ml.fit_markov_switching(spreads, [0] * len(spreads), states=2)
        self.assertAlmostEqual(fitted.means[0], 0.0, delta=0.3)
        self.assertAlmostEqual(fitted.means[1], 8.0, delta=1.0)
        self.assertAlmostEqual(fitted.sigmas[0], 1.0, delta=0.2)
        self.assertAlmostEqual(fitted.sigmas[1], 4.0, delta=0.8)
        self.assertAlmostEqual(fitted.transitions[0][0][0], 0.97, delta=0.02)
        self.assertAlmostEqual(fitted.transitions[0][1][0], 0.15, delta=0.06)

    def test_the_covariate_picks_the_transition_matrix(self):
        """Calm is far stickier when the covariate is 0 than when it is 1."""

        spreads, covariates = _regime_series(
            count=6000, seed=2, stay_calm=(0.995, 0.90), leave_stress=(0.5, 0.95)
        )
        fitted = ml.fit_markov_switching(spreads, covariates, states=2)
        self.assertGreater(fitted.transitions[0][0][0], 0.98)
        self.assertLess(fitted.transitions[1][0][0], 0.95)
        self.assertGreater(fitted.transitions[1][1][1], fitted.transitions[0][1][1])

    def test_a_three_state_fit_orders_its_states_by_mean(self):
        spreads, covariates = _regime_series()
        fitted = ml.fit_markov_switching(spreads, covariates, states=3)
        self.assertEqual(list(fitted.means), sorted(fitted.means))
        for matrix in fitted.transitions:
            for row in matrix:
                self.assertAlmostEqual(sum(row), 1.0)

    def test_the_fit_is_deterministic(self):
        spreads, covariates = _regime_series(count=600)
        self.assertEqual(
            ml.fit_markov_switching(spreads, covariates, states=3),
            ml.fit_markov_switching(spreads, covariates, states=3),
        )

    def test_a_bad_state_count_or_covariate_is_refused(self):
        spreads, covariates = _regime_series(count=300)
        with self.assertRaises(ValueError):
            ml.fit_markov_switching(spreads, covariates, states=4)
        with self.assertRaises(ValueError):
            ml.fit_markov_switching(spreads, [2] * len(spreads), states=2)
        with self.assertRaises(ValueError):
            ml.fit_markov_switching(spreads[:8], covariates[:8], states=2)

    def test_the_filter_reads_each_row_and_none_after_it(self):
        """Row t's filtered distribution is the same whatever follows t.

        The filter is forward-only: changing every row after t, or dropping
        them, leaves the distribution at t unchanged. A smoother would move it.
        """

        spreads, covariates = _regime_series(count=400, seed=3)
        fitted = ml.fit_markov_switching(spreads, covariates, states=2)
        cut = 200
        at_cut = ml.filter_markov_switching(fitted, spreads[:cut], covariates[:cut])
        changed = spreads[:cut] + [50.0] * 50
        again = ml.filter_markov_switching(fitted, changed[:cut], covariates[:cut])
        self.assertEqual(at_cut, again)
        later = ml.filter_markov_switching(fitted, spreads[: cut + 50], covariates[: cut + 50])
        self.assertNotEqual(at_cut, later)

    def test_a_missing_spread_informs_no_state(self):
        spreads, covariates = _regime_series(count=300, seed=4)
        fitted = ml.fit_markov_switching(spreads, covariates, states=2)
        filtered = ml.filter_markov_switching(fitted, spreads[:100] + [None], covariates[:101])
        carried = ml.markov_switching_state_probabilities(
            fitted, ml.filter_markov_switching(fitted, spreads[:100], covariates[:100]),
            covariates[99], 1,
        )
        for a, b in zip(filtered, carried):
            self.assertAlmostEqual(a, b)

    def test_the_exceedance_curve_is_the_mixture_tail_on_whole_basis_points(self):
        fitted = ml.FittedMarkovSwitching(
            means=(0.0, 10.0), sigmas=(1.0, 2.0),
            transitions=(((0.9, 0.1), (0.2, 0.8)),) * 2, initial=(0.5, 0.5),
            log_likelihood=0.0, iterations=1,
        )
        curve = ml.markov_switching_exceedance_curve(fitted, (0.25, 0.75), (5.0, 10.0))

        def tail(x, mean, sigma):
            return 0.5 * math.erfc((x - mean) / (sigma * math.sqrt(2.0)))

        self.assertAlmostEqual(
            curve[0], 0.25 * tail(5.5, 0.0, 1.0) + 0.75 * tail(5.5, 10.0, 2.0)
        )
        self.assertGreater(curve[0], curve[1])
        self.assertEqual(ml.markov_switching_exceedance_curve(fitted, (1.0, 0.0), (1e6,)), (0.0,))

    def test_carrying_the_state_forward_follows_the_transition_matrix(self):
        fitted = ml.FittedMarkovSwitching(
            means=(0.0, 10.0), sigmas=(1.0, 2.0),
            transitions=(((0.9, 0.1), (0.2, 0.8)), ((0.5, 0.5), (0.5, 0.5))),
            initial=(0.5, 0.5), log_likelihood=0.0, iterations=1,
        )
        self.assertEqual(ml.markov_switching_state_probabilities(fitted, (1.0, 0.0), 0, 0), (1.0, 0.0))
        one = ml.markov_switching_state_probabilities(fitted, (1.0, 0.0), 0, 1)
        self.assertAlmostEqual(one[1], 0.1)
        two = ml.markov_switching_state_probabilities(fitted, (1.0, 0.0), 0, 2)
        self.assertAlmostEqual(two[1], 0.9 * 0.1 + 0.1 * 0.8)
        held = ml.markov_switching_state_probabilities(fitted, (1.0, 0.0), 1, 5)
        self.assertAlmostEqual(held[1], 0.5)


def _regime_frame(count=140, seed=5):
    spreads, _ = _regime_series(count=count, seed=seed)
    rows, when = [], date(2024, 1, 1)
    for spread in spreads:
        while when.weekday() >= 5:
            when += timedelta(days=1)
        rows.append(
            DailyObservation(
                when,
                {"spread_bps": spread, "sofr": 4.0 + spread / 100.0, "iorb": 4.0},
            )
        )
        when += timedelta(days=1)
    return rows


class MarkovSwitchingPredictorTests(unittest.TestCase):
    def setUp(self):
        require_extra(self)
        self.rows = _regime_frame()
        self.rule = ml.InformationRule(
            _PRESSURE_REGISTRY, ("spread_bps",), decision_time=time(16, 0), horizon=2
        )

    def call(self, predictor, train, feature_rows, histories, taus=(5.0, 10.0)):
        return predictor(train, feature_rows, taus, information=self.rule, histories=histories)

    def test_a_history_past_its_forecast_is_refused(self):
        """The filter is told its anchor and refuses a history that runs past it.

        Recorded mutation (#384): replacing the condition `history[-1].date >
        feature_row.date` in `markov_switching_exceedance`'s `fit_predict` with
        `False` (so the filter reads the row after the anchor) made this test
        fail with `AssertionError: LookAheadError not raised`; restored, it passes.
        """

        predictor = ml.markov_switching_exceedance(states=2, minimum_history=20)
        train, feature_rows = self.rows[:100], self.rows[100:102]
        histories = [self.rows[:101], self.rows[:103]]
        with self.assertRaises(LookAheadError):
            self.call(predictor, train, feature_rows, histories)

    def test_it_will_not_forecast_without_the_rule_or_the_histories(self):
        predictor = ml.markov_switching_exceedance(states=2, minimum_history=20)
        with self.assertRaises(ValueError):
            predictor(self.rows[:100], self.rows[100:101], (5.0,))
        with self.assertRaises(ValueError):
            self.call(predictor, self.rows[:100], self.rows[100:102], [self.rows[:101]])
        with self.assertRaises(ValueError):
            self.call(predictor, self.rows[:100], self.rows[100:101], [[]])

    def test_a_short_frame_is_refused(self):
        predictor = ml.markov_switching_exceedance(states=2, minimum_history=60)
        with self.assertRaises(ValueError):
            self.call(predictor, self.rows[:59], self.rows[59:60], [self.rows[:60]])

    def test_the_curve_depends_on_the_history_and_ends_at_the_anchor(self):
        predictor = ml.markov_switching_exceedance(states=2, minimum_history=20)
        train, feature_rows = self.rows[:100], self.rows[100:102]
        result = self.call(predictor, train, feature_rows, [self.rows[:101], self.rows[:102]])
        self.assertEqual(result.history_ends, (feature_rows[0].date, feature_rows[1].date))
        self.assertEqual(result.features_read, ("spread_bps",))
        self.assertEqual(result.model_settings["states"], 2)
        for curve in result.curves:
            self.assertGreaterEqual(curve[0], curve[1])

    def test_a_stressed_history_raises_the_probability(self):
        predictor = ml.markov_switching_exceedance(states=2, minimum_history=20)
        train, feature_rows = self.rows[:100], self.rows[100:101]
        calm = [DailyObservation(r.date, dict(r.values, sofr=4.0)) for r in self.rows[:101]]
        hot = calm[:-5] + [DailyObservation(r.date, dict(r.values, sofr=4.09)) for r in calm[-5:]]
        low = self.call(predictor, train, feature_rows, [calm]).curves[0][0]
        high = self.call(predictor, train, feature_rows, [hot]).curves[0][0]
        self.assertGreater(high, low)

    def test_the_scarcity_column_moves_the_transition_covariate(self):
        column = "reserve_scarcity_state"
        rows = [
            DailyObservation(r.date, dict(r.values, **{column: 3.0 if i >= 50 else 0.0}))
            for i, r in enumerate(self.rows)
        ]
        self.assertEqual(sum(ml._tight_covariates(rows, column)), len(rows) - 50)
        self.assertEqual(sum(ml._tight_covariates(rows, None)), 0)
        gap = [DailyObservation(r.date, dict(r.values, **{column: None})) for r in rows[:5]]
        self.assertEqual(ml._tight_covariates(gap, column), [0] * 5)
        later = rows[49:51] + gap
        self.assertEqual(ml._tight_covariates(later, column), [0, 1, 1, 1, 1, 1, 1])

    def test_the_declaration_pins_the_settings(self):
        path = Path(__file__).resolve().parents[1] / "metadata" / "pressure_track_m.json"
        document = json.loads(path.read_text())
        self.assertEqual(document["settings"], dict(ml.MARKOV_SWITCHING_SETTINGS))
        self.assertEqual(document["horizons"], [1, 2, 3, 4, 5])
        self.assertEqual(document["thresholds_bp"], [5, 10])
        self.assertLess(document["scoring"]["last_day"], "2026-01-01")
        for candidate in document["candidates"].values():
            self.assertIn(candidate["states"], (2, 3))
            self.assertEqual(sorted(candidate["cutoffs"]), ["10", "5"])


class MarkovSwitchingConformanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `ml.markov_switching_exceedance` (#384)."""

    IMPLEMENTATION = staticmethod(ml.markov_switching_exceedance)

    def setUp(self):
        require_extra(self)

    def make_predictor(self):
        predictor = ml.markov_switching_exceedance(states=2, minimum_history=self.MINIMUM_HISTORY)
        rule = ml.InformationRule(_PRESSURE_REGISTRY, ("spread_bps",), decision_time=time(16, 0))
        full = self.frame()

        def bound(train_rows, feature_rows, taus):
            histories = [[r for r in full if r.date <= f.date] for f in feature_rows]
            return predictor(train_rows, feature_rows, taus, information=rule, histories=histories)

        return bound


def _rare_factory(kind, treatment):
    def factory(features, declaration, minimum_history=20):
        return ml.pressure_rare_event_exceedance(kind, treatment, features, declaration, minimum_history)

    factory.__name__ = f"pressure_{kind}_{treatment}"
    return factory


class PressureLogisticClassWeightConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the class-weighted logistic (#381)."""

    FACTORY = staticmethod(_rare_factory("logistic", "class_weight"))
    IMPLEMENTATION = staticmethod(ml.pressure_rare_event_exceedance)


class PressureClassifierClassWeightConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the class-weighted gradient-boosted classifier (#381)."""

    FACTORY = staticmethod(_rare_factory("gbm_classifier", "class_weight"))
    IMPLEMENTATION = staticmethod(ml.pressure_rare_event_exceedance)


class PressureClassifierFocalConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the focal-loss classifier (#381)."""

    FACTORY = staticmethod(_rare_factory("gbm_classifier", "focal"))
    IMPLEMENTATION = staticmethod(ml.pressure_rare_event_exceedance)


class PressureLogisticBootstrapConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the event-balanced bootstrap logistic (#381)."""

    FACTORY = staticmethod(_rare_factory("logistic", "balanced_bootstrap"))
    IMPLEMENTATION = staticmethod(ml.pressure_rare_event_exceedance)


class PressureClassifierBootstrapConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the event-balanced bootstrap classifier (#381)."""

    FACTORY = staticmethod(_rare_factory("gbm_classifier", "balanced_bootstrap"))
    IMPLEMENTATION = staticmethod(ml.pressure_rare_event_exceedance)


def _onset_factory(kind, treatment):
    def factory(features, declaration, minimum_history=20):
        return ml.pressure_onset_exceedance(kind, treatment, features, declaration, minimum_history)

    factory.__name__ = f"pressure_onset_{kind}_{treatment}"
    return factory


class PressureOnsetLogisticConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the class-weighted onset logistic (#409)."""

    FACTORY = staticmethod(_onset_factory("logistic", "class_weight"))
    IMPLEMENTATION = staticmethod(ml.pressure_onset_exceedance)


class PressureOnsetClassifierConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the class-weighted onset classifier (#409)."""

    FACTORY = staticmethod(_onset_factory("gbm_classifier", "class_weight"))
    IMPLEMENTATION = staticmethod(ml.pressure_onset_exceedance)


class OnsetLabelTests(unittest.TestCase):
    """The onset label (#409): a pressure day with five quiet panel days before it.

    Recorded mutations:

    * `_onset_labels`: the slice `train_rows[target - ONSET_QUIET_DAYS : target]`
      widened to `train_rows[target - ONSET_QUIET_DAYS : target + 1]` (the target
      itself counted among its own quiet days, so no pressure day is an onset):
      `test_the_label_is_the_pressure_onset_rule` fails with `AssertionError`.
    * `_onset_labels`: the slice shortened to `train_rows[target - 4 : target]`
      (four quiet days): the same test fails with `AssertionError`.
    """

    SPREADS = [0, 0, 0, 0, 0, 0, 7, 8, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 6]

    def rows(self):
        from datetime import timedelta

        return [
            DailyObservation(date(2024, 1, 1) + timedelta(days=k), {"sofr": 5.0 + value / 100.0, "iorb": 5.0})
            for k, value in enumerate(self.SPREADS)
        ]

    def test_the_label_is_the_pressure_onset_rule(self):
        from repo_model import pressure
        from repo_model.data import exceeds_bp

        rows = self.rows()
        targets = list(range(ml.ONSET_QUIET_DAYS, len(rows)))
        exceeds = [1 if exceeds_bp(rows[t].spread_bps, 5.0) else 0 for t in targets]
        labels = ml._onset_labels(exceeds, targets, rows, 5.0)
        # Day 6 opens an episode, day 7 continues it, day 15 follows seven quiet days; day 20 has a
        # pressure day exactly five days before it, and day 27 (a 6 bp print) follows seven quiet ones.
        self.assertEqual([t for t, label in zip(targets, labels) if label], [6, 15, 27])
        scored = [row.date for row in rows[ml.ONSET_QUIET_DAYS:]]
        by_rule = pressure.onsets(rows, 5.0, scored)
        self.assertEqual([rows[t].date for t, label in zip(targets, labels) if label], list(by_rule))

    def test_no_threshold_above_the_spreads_gives_no_onset(self):
        rows = self.rows()
        targets = list(range(ml.ONSET_QUIET_DAYS, len(rows)))
        self.assertEqual(sum(ml._onset_labels([0] * len(targets), targets, rows, 50.0)), 0)

    def test_a_quantile_kind_has_no_onset_label(self):
        with self.assertRaises(ValueError):
            ml.pressure_onset_exceedance("probit", None, _PRESSURE_CALENDAR, _pressure_splits())
        with self.assertRaises(ValueError):
            ml.pressure_onset_exceedance("logistic", "focal", _PRESSURE_CALENDAR, _pressure_splits())


class OptionalColumnTests(unittest.TestCase):
    """A declared column that enters with an observed indicator (`ml._OnsetDesign`, #409)."""

    def setUp(self):
        require_extra(self)

    def design(self, **options):
        return ml._OnsetDesign(("spread_bps", "ofr_tri_rate"), _pressure_splits(), **options)

    def test_a_hole_is_a_zero_with_the_indicator_off(self):
        design = self.design(optional=("ofr_tri_rate",))
        self.assertEqual(design.names, ("spread_bps", "ofr_tri_rate", "ofr_tri_rate_observed"))
        seen = DailyObservation(date(2024, 1, 2), {"sofr": 5.1, "iorb": 5.0, "ofr_tri_rate": 5.05})
        hole = DailyObservation(date(2024, 1, 2), {"sofr": 5.1, "iorb": 5.0, "ofr_tri_rate": None})
        self.assertEqual(design.row(seen, None)[1:], [5.05, 1.0])
        self.assertEqual(design.row(hole, None)[1:], [0.0, 0.0])

    def test_without_the_option_a_hole_is_still_refused(self):
        hole = DailyObservation(date(2024, 1, 2), {"sofr": 5.1, "iorb": 5.0, "ofr_tri_rate": None})
        with self.assertRaises(ValueError):
            self.design().row(hole, None)

    def test_an_optional_column_must_be_a_declared_linear_column(self):
        with self.assertRaises(ValueError):
            self.design(optional=("ofr_gcf_rate",))
        with self.assertRaises(ValueError):
            ml._OnsetDesign(("spread_bps", "reserve_balances"), _pressure_splits(), optional=("reserve_balances",))


class RareEventTrainingTests(unittest.TestCase):
    """Rare-event training (#381): reweighted fits learn from the spikes.

    Recorded mutations (the resampling reads the training labels of one fit and
    nothing else; the focal gradient is the loss's derivative):

    * `_balanced_indices`: `rng.choice(events, ...)` replaced by
      `rng.choice(numpy.arange(len(y)), ...)` (events drawn from every row):
      `test_a_balanced_bootstrap_draws_half_its_rows_from_the_events` fails
      with `AssertionError`.
    * `_focal_gradient`: the `y == 1` branch's `- (1.0 - p) ** (gamma + 1.0)`
      deleted: `test_the_focal_gradient_is_the_derivative_of_the_focal_loss`
      fails with `AssertionError`.
    """

    def setUp(self):
        require_extra(self)

    def rare_data(self, n=1500, seed=0):
        import numpy

        rng = numpy.random.default_rng(seed)
        x = rng.normal(size=(n, 2))
        logit = -4.0 + 2.5 * x[:, 0]
        y = (rng.uniform(size=n) < 1.0 / (1.0 + numpy.exp(-logit))).astype(int)
        return x, y

    def test_class_weights_equal_scikit_learn_balanced_weights(self):
        import numpy
        from sklearn.linear_model import LogisticRegression

        x, y = self.rare_data()
        got = ml._fit_rare_event("logistic", "class_weight", x, y, x[:5])
        centre, scale = x.mean(axis=0), x.std(axis=0)
        want = (
            LogisticRegression(C=1.0, max_iter=5000, class_weight="balanced")
            .fit((x - centre) / scale, y)
            .predict_proba((x[:5] - centre) / scale)[:, 1]
        )
        self.assertTrue(numpy.allclose(got, want, atol=1e-12))

    def test_every_treatment_raises_the_average_probability_above_the_plain_fit(self):
        x, y = self.rare_data()
        held_out, _ = self.rare_data(seed=1)
        for kind, treatment in (
            ("logistic", "class_weight"),
            ("logistic", "balanced_bootstrap"),
            ("gbm_classifier", "class_weight"),
            ("gbm_classifier", "balanced_bootstrap"),
        ):
            with self.subTest(kind=kind, treatment=treatment):
                plain = ml._fit_classifier("logistic" if kind == "logistic" else "gbm", x, y, held_out)
                treated = ml._fit_rare_event(kind, treatment, x, y, held_out)
                self.assertGreater(sum(treated) / len(treated), 1.5 * sum(plain) / len(plain))

    def test_every_treatment_ranks_the_events_above_chance(self):
        from repo_model.pressure_judge import auroc

        x, y = self.rare_data()
        test_x, test_y = self.rare_data(seed=1)
        for kind, treatment in (
            ("logistic", "class_weight"),
            ("logistic", "balanced_bootstrap"),
            ("gbm_classifier", "class_weight"),
            ("gbm_classifier", "balanced_bootstrap"),
            ("gbm_classifier", "focal"),
        ):
            with self.subTest(kind=kind, treatment=treatment):
                got = ml._fit_rare_event(kind, treatment, x, y, test_x)
                self.assertGreater(auroc(got, [int(v) for v in test_y]), 0.8)

    def test_the_focal_gradient_is_the_derivative_of_the_focal_loss(self):
        import numpy

        def loss(z, y, gamma, alpha):
            p = 1.0 / (1.0 + numpy.exp(-z))
            return numpy.where(
                y == 1, -alpha * (1 - p) ** gamma * numpy.log(p), -(1 - alpha) * p**gamma * numpy.log(1 - p)
            )

        z = numpy.linspace(-4.0, 4.0, 9)
        for y in (1, 0):
            labels = numpy.full(len(z), y)
            for gamma, alpha in ((2.0, 0.75), (0.0, 0.5), (1.0, 0.3)):
                step = 1e-6
                want = (loss(z + step, labels, gamma, alpha) - loss(z - step, labels, gamma, alpha)) / (2 * step)
                got = ml._focal_gradient(z, labels, gamma, alpha)
                self.assertTrue(numpy.allclose(got, want, atol=1e-6), (y, gamma, alpha))

    def test_the_focal_fit_is_deterministic(self):
        x, y = self.rare_data(n=600)
        first = ml._fit_rare_event("gbm_classifier", "focal", x, y, x[:20])
        second = ml._fit_rare_event("gbm_classifier", "focal", x, y, x[:20])
        self.assertEqual(first, second)

    def test_a_balanced_bootstrap_draws_half_its_rows_from_the_events(self):
        import numpy

        _, y = self.rare_data()
        rows = ml._balanced_indices(y, 7)
        self.assertEqual(len(rows), len(y))
        self.assertTrue(((rows >= 0) & (rows < len(y))).all())
        self.assertEqual(int(y[rows].sum()), round(0.5 * len(y)))
        self.assertTrue(numpy.array_equal(rows, ml._balanced_indices(y, 7)))
        self.assertFalse(numpy.array_equal(rows, ml._balanced_indices(y, 8)))

    def test_a_balanced_bootstrap_uses_the_training_labels_of_its_fit_only(self):
        # Rows the fit is not given cannot appear: indices are positions in the labels passed in.
        x, y = self.rare_data()
        cut = 900
        for seed in range(5):
            self.assertLess(int(ml._balanced_indices(y[:cut], seed).max()), cut)

    def test_a_balanced_bootstrap_of_one_class_is_refused(self):
        import numpy

        with self.assertRaises(ValueError):
            ml._balanced_indices(numpy.zeros(50, dtype=int), 0)

    def test_unsupported_treatments_are_refused_at_construction(self):
        splits = _pressure_splits()
        for kind, treatment in (
            ("logistic", "focal"),
            ("probit", "class_weight"),
            ("gbm_classifier", "oversample"),
        ):
            with self.subTest(kind=kind, treatment=treatment), self.assertRaises(ValueError):
                ml.pressure_rare_event_exceedance(kind, treatment, _PRESSURE_CALENDAR, splits)

    def test_the_declaration_names_the_treatment(self):
        import numpy

        predictor = ml.pressure_rare_event_exceedance(
            "gbm_classifier", "focal", _PRESSURE_CALENDAR, _pressure_splits()
        )
        rule = ml.InformationRule(_PRESSURE_REGISTRY, _PRESSURE_CALENDAR, decision_time=time(16, 0))
        from test_baseline import regressor_frame

        rows = _with_calendar(regressor_frame())
        info = rule.information_set([r.date for r in rows], len(rows) - 1)
        curves = predictor(rows[:-1], (rule.observation(rows, info),), (5.0,), information=rule)
        settings = curves.model_settings["rare_event"]
        self.assertEqual(settings["treatment"], "focal")
        self.assertEqual(settings["focal"]["gamma"], 2.0)
        import json

        json.dumps(dict(curves.model_settings))  # a record, so plain dicts all the way down
        self.assertTrue(numpy.isfinite(curves.curves[0][0]))


def _recency_factory(mode, parameter):
    def factory(features, declaration, minimum_history=20):
        return ml.pressure_rare_event_exceedance(
            "logistic", "class_weight", features, declaration, minimum_history, recency=(mode, parameter)
        )

    factory.__name__ = f"pressure_logistic_{mode}_{parameter}"
    return factory


class PressureLogisticDecayConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the decay-weighted class-weighted logistic (#411)."""

    FACTORY = staticmethod(_recency_factory("decay", 30))
    IMPLEMENTATION = staticmethod(ml.pressure_rare_event_exceedance)


class PressureLogisticWindowConformanceTests(_PressureConformance, unittest.TestCase):
    """The conformance suite against the windowed class-weighted logistic (#411)."""

    FACTORY = staticmethod(_recency_factory("window", 40))
    IMPLEMENTATION = staticmethod(ml.pressure_rare_event_exceedance)


class RecencyTrainingTests(unittest.TestCase):
    """Recency-weighted and windowed fits (#411): recent pairs count more, only the fit's own pairs are read.

    Recorded mutation (the window keeps only the pairs younger than it):
    in `_fit_recency_logistic`, `keep = ages < parameter` replaced by
    `keep = ages >= 0` (every pair kept): `test_a_window_fit_is_the_class_weighted_fit_of_its_pairs`
    fails with `AssertionError`.
    """

    def setUp(self):
        require_extra(self)

    def drifting(self, n=1200, seed=3):
        """Old pairs: the event follows x0. The last 300: it follows -x0. Age 0 is the newest."""

        import numpy

        rng = numpy.random.default_rng(seed)
        x = rng.normal(size=(n, 2))
        sign = numpy.where(numpy.arange(n) < n - 300, 1.0, -1.0)
        y = (rng.uniform(size=n) < 1.0 / (1.0 + numpy.exp(-(-2.5 + 2.5 * sign * x[:, 0])))).astype(int)
        ages = numpy.arange(n)[::-1].astype(float)
        return x, y, ages

    def test_a_very_long_half_life_is_the_class_weighted_fit(self):
        import numpy

        x, y, ages = self.drifting()
        got = ml._fit_recency_logistic(x, y, x[:10], ages, "decay", 1e12)
        want = ml._fit_rare_event("logistic", "class_weight", x, y, x[:10])
        self.assertTrue(numpy.allclose(got, want, atol=1e-6))

    def test_a_short_half_life_follows_the_recent_relation(self):
        import numpy

        x, y, ages = self.drifting()
        probe = numpy.array([[2.0, 0.0], [-2.0, 0.0]])
        flat = ml._fit_recency_logistic(x, y, probe, ages, "decay", 1e12)
        recent = ml._fit_recency_logistic(x, y, probe, ages, "decay", 60)
        self.assertGreater(flat[0], flat[1])  # the old relation dominates
        self.assertLess(recent[0], recent[1])  # the last 300 days' relation

    def test_decay_balances_the_classes_on_the_weighted_totals(self):
        import numpy

        x, y, ages = self.drifting()
        p = numpy.array(ml._fit_recency_logistic(x, y, x, ages, "decay", 90))
        plain = numpy.array(ml._fit_classifier("logistic", x, y, x))
        self.assertGreater(p.mean(), 1.5 * plain.mean())

    def test_a_window_fit_is_the_class_weighted_fit_of_its_pairs(self):
        import numpy

        x, y, ages = self.drifting()
        got = ml._fit_recency_logistic(x, y, x[:10], ages, "window", 300)
        keep = ages < 300
        want = ml._fit_rare_event("logistic", "class_weight", x[keep], y[keep], x[:10])
        # Same pairs; the standardizer and the weights are the window's own.
        self.assertTrue(numpy.allclose(got, want, atol=1e-9))
        whole = ml._fit_rare_event("logistic", "class_weight", x, y, x[:10])
        self.assertFalse(numpy.allclose(got, whole, atol=1e-3))

    def test_a_window_with_too_few_events_falls_back_to_the_whole_history(self):
        import numpy

        x, y, ages = self.drifting()
        y = y.copy()
        y[ages < 100] = 0
        got = ml._fit_recency_logistic(x, y, x[:10], ages, "window", 100)
        want = ml._fit_rare_event("logistic", "class_weight", x, y, x[:10])
        self.assertTrue(numpy.allclose(got, want, atol=1e-9))

    def test_unsupported_recency_is_refused_at_construction(self):
        splits = _pressure_splits()
        for kind, treatment, recency in (
            ("gbm_classifier", "class_weight", ("decay", 60)),
            ("logistic", "balanced_bootstrap", ("decay", 60)),
            ("logistic", "class_weight", ("ewma", 60)),
            ("logistic", "class_weight", ("window", 0)),
        ):
            with self.subTest(kind=kind, treatment=treatment, recency=recency), self.assertRaises(ValueError):
                ml.pressure_rare_event_exceedance(
                    kind, treatment, _PRESSURE_CALENDAR, splits, recency=recency
                )

    def test_the_declaration_names_the_recency(self):
        predictor = ml.pressure_rare_event_exceedance(
            "logistic", "class_weight", _PRESSURE_CALENDAR, _pressure_splits(), recency=("decay", 126)
        )
        rule = ml.InformationRule(_PRESSURE_REGISTRY, _PRESSURE_CALENDAR, decision_time=time(16, 0))
        from test_baseline import regressor_frame

        rows = _with_calendar(regressor_frame())
        info = rule.information_set([r.date for r in rows], len(rows) - 1)
        curves = predictor(rows[:-1], (rule.observation(rows, info),), (5.0,), information=rule)
        self.assertEqual(curves.model_settings["recency"]["mode"], "decay")
        self.assertEqual(curves.model_settings["recency"]["parameter"], 126)
        import json

        json.dumps(dict(curves.model_settings))


if __name__ == "__main__":
    unittest.main()
