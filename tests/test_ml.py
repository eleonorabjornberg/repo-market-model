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
import os
import sys
import unittest
from datetime import date, timedelta
from unittest import mock

from repo_model import baseline, cli_eval, ml
from repo_model.contract import QUANTILE_LEVELS
from repo_model.data import DailyObservation, load_daily_panel
from repo_model.metrics import crps_from_quantiles

from test_baseline import (
    EXCEEDANCE_TAUS,
    ExceedancePredictorConformance,
    REGRESSORS,
)
from test_cli_eval import ContinuousModelHarness
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

    **Why the report object and not only the artifact.** The record carries
    each side's *mean* loss and its first and last fold; it does not carry the
    per-origin series, deliberately -- `paired_comparison_document` publishes
    what a reader interprets and `PairedComparisonReport` holds what the run
    computed. The claim below is per origin, so the run's own
    `PairedComparisonReport` is captured on its way into the document by
    wrapping the name `cli_eval` calls. Nothing about the run changes: the
    command is entered through `cli.main`, the document is built by the real
    function, and the file is written. What is read is the run's own object
    rather than a second comparison built beside it.


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
    to 2 100 rows. The published `compare` records under `docs/runs/` carry
    2 080 origins over an expanding window that reaches 2 099 rows, which puts
    a real run at something over an hour of wall clock on eight cores. It fits
    in an evening; it does not fit in a test.

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


if __name__ == "__main__":
    unittest.main()
