"""`src/repo_model/tail_diagnostics.py`: reading a `--tail gpd` exceedance record (B44).

B43's analysis, ported from its working scripts into a module with tests.

* `TailRecordReadingTests` -- stdlib, on a hand-written record whose numbers
  are chosen so each reading has one right answer and the wrong readings give
  different ones. The fold with `q_top = -4` and an excess of 12 has a ceiling
  of 8 bp: at or below 10 bp as a level, above it as a bare excess. The fold
  with `q_top = 15` and an excess of 40 has a ceiling of 55 bp: above 50 bp as
  a level, at or below it as a bare excess.
* `KnotRefitTests` -- needs the `ml` extra. `test_ml.TailAccountTests`' panel
  through the real `rolling_exceedance_backtest` with `capture_knots` around
  it, then `refit_knots` over some of its folds. What it asserts: the wrapper
  changes no probability the run scored, the class attribute comes back, the
  captured knots reproduce every per-tau Brier score on the record to the bit
  (B43's reproduction check on the real record, made a test), and a refit of
  chosen folds is the scored run's own fits.

Mutation record
---------------

B44, in a disposable copy under `$HOME` built from `git ls-files -z --cached
--others --exclude-standard`, run concurrently with an unmutated control, with
`PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1` and
`REPO_MODEL_REQUIRE_ML=1`, whole suite, on CPython 3.9.6 with numpy 2.0.2 and
scikit-learn 1.6.1 through the mount's `.venv/bin/python` by absolute path.
`repo_model` was confirmed to resolve to the copy's `src/`. Unmutated control
green before and after, zero `expectedFailure`. The target was found exactly
once.

1. **The ceiling taken as the bare excess**: `q_top[when] +
   entry["upper_endpoint_excess"]` -> `entry["upper_endpoint_excess"]` in
   `absolute_ceilings`. `AssertionError` in
   `TailRecordReadingTests.test_the_ceiling_is_the_top_quantile_plus_the_endpoint_excess`
   part 1 (`{12.0, 40.0}` against `{8.0, 55.0}`) and part 2 (`{10: 0, 50: 2}`
   against `{10: 1, 50: 1}`). Nothing else in the suite goes red.
   `KnotRefitTests` reads no ceiling.

The lower-bound refusal's mutations are recorded on
`test_ml.TailLowerBoundRefusalTests`. Under the first two,
`KnotRefitTests` part 4 also fails, because the fixture then has no refused fold.
"""

import json
import re
import unittest
from unittest import mock

import test_ml
from repo_model import baseline, tail_diagnostics


def _record():
    taus = [5.0, 10.0, 20.0, 50.0]
    tail = [
        {"scored_date": "2024-01-01", "state": "no_excesses", "excesses": 0},
        {"scored_date": "2024-01-02", "state": "fallback", "sigma": 1.0, "excesses": 5},
        {"scored_date": "2024-01-03", "state": "refused", "sigma": 2.0, "excesses": 30},
        {"scored_date": "2024-01-04", "state": "fitted", "xi": 0.2, "sigma": 1.5,
         "excesses": 40, "clamped": False},
        {"scored_date": "2024-01-05", "state": "fitted", "xi": -0.25, "sigma": 3.0,
         "excesses": 40, "clamped": False, "upper_endpoint_excess": 12.0},
        {"scored_date": "2024-01-06", "state": "fitted", "xi": -0.125, "sigma": 5.0,
         "excesses": 40, "clamped": False, "upper_endpoint_excess": 40.0},
    ]
    return {
        "declaration": {"taus_bp": taus},
        "folds": {"count": len(tail), "tail": tail},
    }


#: `scored_date -> (q_top, realized_bps, probabilities)`.
_KNOTS = {
    "2024-01-01": (-2.0, 3.0, [0.05, 0.0, 0.0, 0.0]),
    "2024-01-02": (1.0, 12.0, [0.1, 0.0, 0.0, 0.0]),
    "2024-01-03": (2.0, 60.0, [0.05, 0.02, 0.01, 0.001]),
    "2024-01-04": (0.5, 1.0, [0.04, 0.02, 0.01, 0.002]),
    "2024-01-05": (-4.0, 11.0, [0.03, 0.0, 0.0, 0.0]),
    "2024-01-06": (15.0, 51.0, [0.05, 0.04, 0.02, 0.0]),
}


def _knots(record):
    by_date = {entry["scored_date"]: entry for entry in record["folds"]["tail"]}
    return [
        {
            "scored_date": when,
            "q_top": q_top,
            "realized_bps": realized,
            "probabilities": probabilities,
            "tail_account": {k: v for k, v in by_date[when].items() if k != "scored_date"},
        }
        for when, (q_top, realized, probabilities) in _KNOTS.items()
    ]


class TailRecordReadingTests(unittest.TestCase):
    """States, ceilings and zero-on-event cells off a record and its knots."""

    def test_states_are_counted_over_every_tail_state_and_fitted_folds_split_by_endpoint(self):
        counts = tail_diagnostics.state_counts(_record())
        self.assertEqual(
            counts,
            {
                "states": {"fitted": 3, "fallback": 1, "no_excesses": 1, "refused": 1},
                "fitted": 3,
                "fitted_no_endpoint": 1,
                "fitted_with_endpoint": 2,
            },
        )

    def test_the_ceiling_is_the_top_quantile_plus_the_endpoint_excess(self):
        """`Q(top) + upper_endpoint_excess`, a level; never the bare excess."""

        record = _record()
        q_top = tail_diagnostics.top_quantiles(_knots(record))

        with self.subTest("1. per fold, only where there is an endpoint"):
            self.assertEqual(
                tail_diagnostics.absolute_ceilings(record, q_top),
                {"2024-01-05": 8.0, "2024-01-06": 55.0},
            )

        with self.subTest("2. folds at or below each declared tau"):
            self.assertEqual(
                tail_diagnostics.ceilings_at_or_below_taus(record, q_top),
                {5.0: 0, 10.0: 1, 20.0: 1, 50.0: 1},
            )
            self.assertEqual(
                tail_diagnostics.ceilings_at_or_below_taus(record, q_top, taus=(8.0,)),
                {8.0: 1},
            )

        with self.subTest("3. a fold with an endpoint and no Q(top) is refused"):
            with self.assertRaises(ValueError):
                tail_diagnostics.absolute_ceilings(record, {"2024-01-05": -4.0})

    def test_zero_forecasts_on_realised_events_are_found_by_state(self):
        record = _record()
        cells = tail_diagnostics.zero_forecasts_on_events(record, _knots(record))
        self.assertEqual(
            cells,
            {
                "fitted": [
                    {"scored_date": "2024-01-05", "tau_bp": 10.0, "realized_bps": 11.0},
                    {"scored_date": "2024-01-06", "tau_bp": 50.0, "realized_bps": 51.0},
                ],
                "fallback": [
                    {"scored_date": "2024-01-02", "tau_bp": 10.0, "realized_bps": 12.0},
                ],
                "no_excesses": [],
                "refused": [],
            },
        )

    def test_inputs_that_do_not_describe_the_record_are_refused(self):
        with self.subTest("an unknown state"):
            record = _record()
            record["folds"]["tail"][0]["state"] = "clamped"
            with self.assertRaises(ValueError):
                tail_diagnostics.state_counts(record)

        with self.subTest("an endpoint key that disagrees with the sign of xi"):
            record = _record()
            del record["folds"]["tail"][4]["upper_endpoint_excess"]
            with self.assertRaises(ValueError):
                tail_diagnostics.state_counts(record)

        with self.subTest("a record without folds.tail"):
            record = _record()
            del record["folds"]["tail"]
            with self.assertRaises(ValueError):
                tail_diagnostics.state_counts(record)

        with self.subTest("knots from a different fit"):
            record = _record()
            knots = _knots(record)
            knots[2]["tail_account"] = {"state": "fallback", "sigma": 2.0, "excesses": 30}
            with self.assertRaises(ValueError):
                tail_diagnostics.zero_forecasts_on_events(record, knots)

        with self.subTest("knots missing a fold"):
            record = _record()
            with self.assertRaises(ValueError):
                tail_diagnostics.zero_forecasts_on_events(record, _knots(record)[1:])

        with self.subTest("the wrong number of probabilities"):
            record = _record()
            knots = _knots(record)
            knots[0]["probabilities"] = [0.05, 0.0, 0.0]
            with self.assertRaises(ValueError):
                tail_diagnostics.check_knots(record, knots)


class TailRecordRefusalMessageTests(unittest.TestCase):
    """The fold/knot consistency refusals, message for message.

    `TailRecordReadingTests.test_inputs_that_do_not_describe_the_record_are_refused`
    holds the refusals in place -- it asserts that they fire. This class pins
    what they *say*, because the message is how a mismatched record gets
    repaired: a reader holding a record and knots that disagree needs to be
    told which fold and which kind of disagreement, not that something was
    "inconsistent". Each assertion is the refusal's full text.

    Stdlib throughout: the fixtures are the hand-written record and knots
    already defined at module level, and no case reaches the `ml` extra.

    Mutation record (E5, coverage audit): disposable copy under `$HOME` built
    from `git ls-files -z --cached --others --exclude-standard` at the branch
    head, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, unmutated control green
    before and after.

    1. **The absent-tail guard removed** -- `if "tail" not in folds:` ->
       `if False:` in `_tail_entries`. Kills
       `test_a_record_without_folds_tail_names_what_is_missing` with
       `KeyError: 'tail'` (the test errors) where it requires the
       `the record has no folds.tail` refusal. Mutation confirmed applied by
       diff.
    2. **The duplicate-knot message reworded** -- `two knots for one fold` ->
       `two knots for a single fold`. Kills
       `test_two_knots_for_one_fold_are_refused` on its exact-string
       assertion. Mutation confirmed applied by diff.
    """

    def test_a_record_without_folds_tail_names_what_is_missing(self):
        with self.assertRaises(ValueError) as caught:
            tail_diagnostics._tail_entries(
                {"declaration": {"taus_bp": [5.0]}, "folds": {"count": 1}}
            )
        self.assertEqual(
            str(caught.exception),
            "the record has no folds.tail; it is not a --tail run, or it was "
            "written before tail accounts were recorded",
        )

        # The same refusal reaches the public readers unchecked, so the
        # message a caller sees is this one and not a KeyError beneath it.
        record = _record()
        del record["folds"]["tail"]
        with self.assertRaisesRegex(
            ValueError, re.escape("the record has no folds.tail")
        ):
            tail_diagnostics.state_counts(record)

    def test_a_tail_not_one_entry_per_fold_is_refused_with_both_counts(self):
        record = _record()
        record["folds"]["count"] = len(record["folds"]["tail"]) + 1
        with self.assertRaises(ValueError) as caught:
            tail_diagnostics._tail_entries(record)
        self.assertEqual(
            str(caught.exception),
            "folds.tail has 6 entries for 7 folds",
        )

    def test_a_knot_for_a_fold_the_record_does_not_have_is_refused(self):
        record = _record()
        knots = _knots(record)
        stray = dict(knots[0], scored_date="2030-01-01")
        with self.assertRaises(ValueError) as caught:
            tail_diagnostics.check_knots(record, [stray])
        self.assertEqual(
            str(caught.exception),
            "2030-01-01: a knot for a fold the record does not have",
        )

    def test_two_knots_for_one_fold_are_refused(self):
        record = _record()
        knots = _knots(record)
        with self.assertRaises(ValueError) as caught:
            tail_diagnostics.check_knots(record, [knots[0], knots[0]])
        self.assertEqual(
            str(caught.exception),
            "2024-01-01: two knots for one fold",
        )

    def test_a_knot_whose_tail_account_is_not_the_recorded_fit_is_refused(self):
        record = _record()
        knots = _knots(record)
        # A `fallback` fold's account carries sigma; moving it makes the knot a
        # different fit than the one the record scored.
        knots[1]["tail_account"] = dict(
            knots[1]["tail_account"], sigma=knots[1]["tail_account"]["sigma"] + 1.0
        )
        with self.assertRaises(ValueError) as caught:
            tail_diagnostics.check_knots(record, knots)
        self.assertEqual(
            str(caught.exception),
            "2024-01-02: the refit is not the fit the record scored",
        )

    def test_the_unmutated_knots_still_pass_the_same_check(self):
        """Control for the refusals above: the module's own fixtures are valid."""

        record = _record()
        tail_diagnostics.check_knots(record, _knots(record))


class KnotRefitTests(unittest.TestCase):
    """`capture_knots` and `refit_knots` on a real tailed exceedance run."""

    def setUp(self):
        test_ml.require_extra(self)
        self.case = test_ml.ExceedanceTailAccountTests(
            "test_an_exceedance_run_with_a_tail_records_what_its_tail_was_at_every_fold"
        )
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)

    def test_captured_knots_are_the_scored_run_and_a_refit_of_chosen_folds_reproduces_them(self):
        from repo_model import ml

        case = self.case
        panel = case.frame()
        original = ml.FittedGradientBoostedQuantiles.predict_stress
        with tail_diagnostics.capture_knots() as captured:
            report, document, _ = case.exceedance(panel, case.gbm(tail="gpd"))

        with self.subTest("1. the wrapper is removed and changed nothing scored"):
            self.assertIs(ml.FittedGradientBoostedQuantiles.predict_stress, original)
            self.assertEqual(len(captured), len(report.folds))
            for fold, curve, knot in zip(report.folds, report.forecast, captured):
                self.assertEqual(tuple(knot["probabilities"]), curve)
                self.assertEqual(knot["feature_date"], fold.feature_date.isoformat())
                self.assertEqual(knot["q_top"], knot["values"][-2])

        realized = {row.date.isoformat(): row.spread_bps for row in panel}
        knots = [
            {"scored_date": fold.scored_date.isoformat(),
             "realized_bps": realized[fold.scored_date.isoformat()], **knot}
            for fold, knot in zip(report.folds, captured)
        ]

        with self.subTest("2. the knots reproduce the record's Brier scores to the bit"):
            tail_diagnostics.check_knots(document, knots, require_all=True)
            self.assertEqual(
                tail_diagnostics.brier_by_tau(document, knots),
                {
                    float(tau): document["metrics"]["by_tau"][f"{float(tau):g}"]["brier"]
                    for tau in document["declaration"]["taus_bp"]
                },
            )

        with self.subTest("3. a refit of chosen folds is those folds' scored fits"):
            chosen = [knot["scored_date"] for knot in knots[-8:]]
            refit = tail_diagnostics.refit_knots(
                document,
                panel,
                registry=case.registry,
                predictor=case.gbm(tail="gpd"),
                scored_dates=chosen,
            )
            self.assertEqual([knot["scored_date"] for knot in refit], chosen)
            self.assertEqual(json.loads(json.dumps(refit)), json.loads(json.dumps(knots[-8:])))
            self.assertIs(ml.FittedGradientBoostedQuantiles.predict_stress, original)

        with self.subTest("4. the record's states, refusals included, are counted"):
            counts = tail_diagnostics.state_counts(document)
            self.assertEqual(sum(counts["states"].values()), len(report.folds))
            self.assertGreater(counts["states"]["refused"], 0)

        with self.subTest("5. a predictor that never reaches predict_stress is refused"):
            def silent(train_rows, feature_rows, taus, purge_days=None):
                return baseline.ExceedanceCurves(((0.0,) * len(taus),), ())

            with mock.patch.object(tail_diagnostics, "_reads_purge_days", lambda p: True):
                with self.assertRaises(ValueError):
                    tail_diagnostics.refit_knots(
                        document, panel, registry=case.registry, predictor=silent,
                        scored_dates=chosen[-1:],
                    )


if __name__ == "__main__":
    unittest.main()
