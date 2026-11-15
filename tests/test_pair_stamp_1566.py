"""Pair builders stamp how they built their pairs; the seven fitters of pre-built pairs refuse a mismatch (#1566).

Eleonora's ruling of 11 November 2026 (decision docket, card f1554-2-pairs-1111, option "stamp"), audit item 2 of #1554
(H5 support, the calendar-first guard, #947). The seven fitters took `training_pairs="direct"` on trust for pairs built
elsewhere: a one-step pair set labelled `'direct'` would carry a calendar column past the guard, one row off (#914).
Now `one_step_guard.stamp_pairs` marks what a builder returns, and `guard_pair_stamp` makes each fitter raise
`ValueError` when the stamp disagrees with `training_pairs`, or when the pairs carry no stamp and a calendar or
scheduled column is read.

Recorded mutation (applied to a disposable copy, confirmed by diff, reverted; `PYTHONPATH=src:tests python3.11 -B -m
unittest test_pair_stamp_1566`): in `one_step_guard.check_pair_stamp`, `if built != wanted:` replaced with
`if False:`. Killed by `MislabelledPairsTests.test_a_one_step_stamp_under_a_direct_label_is_refused` on every one of the
seven fitters (subTests), `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import unittest

from repo_model import b4_quantile_regression as b4
from repo_model import one_step_guard as osg
from repo_model import s3c_carry as carry
from repo_model import s3c_pd as pd
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_regime as rg
from repo_model import spread_mr_scale as scale
from repo_model import spread_mr_state_calendar as sc

NONE = {name: 0 for name in cal.ALL_TERMS}
GRID = (0.25, 0.5, 0.75)


def _flags(i):
    return dict(NONE, quarter_end=1 if i % 6 == 0 else 0)


def _calendar_pairs():
    return [cal.PairRow((-1.0) ** i * (1.0 + (i % 3) * 0.5) + (3.0 if i % 6 == 0 else 0.0), 1.0, _flags(i)) for i in range(60)]


def _state_pairs():
    return [sc.StatePair((-1.0) ** i * (1.0 + (i % 3) * 0.5), 1.0, _flags(i), None, {}, i, i + 1, {}, False) for i in range(80)]


def _regime_inputs():
    z = [(-1.0) ** i * (0.5 + (i % 5) * 0.3) for i in range(300)]
    xs = [tuple(1.0 if (i % 7 == 0 and j == 0) else 0.0 for j in range(len(rg.ENTRY_TERMS))) for i in range(300)]
    return z, xs


# Each entry: name, a function of (pairs_wrapper, training_pairs, regressors) that calls the fitter. `wrap` turns the raw
# pair list into what is passed (stamped or not); the regressors are one calendar column, or none.
def _call_calendar(wrap, label, regressors):
    return cal.fit_calendar_terms(
        wrap(_calendar_pairs()), regressors=regressors, location=("quarter_end",), scale_terms=(), training_pairs=label
    )


def _call_state(wrap, label, regressors):
    return sc.fit_state_terms(
        wrap(_state_pairs()), regressors=regressors, terms=("quarter_end",), interact=False, robust=False, training_pairs=label
    )


def _call_scale(wrap, label, regressors):
    pairs = [(1.0, None)] * 30 + [(3.0, "quarter_end")] * 10
    return scale.fit_type_factors(wrap(pairs), regressors=regressors, training_pairs=label)


def _call_regime(wrap, label, regressors):
    z, xs = _regime_inputs()
    return rg.fit_regimes(z, wrap(xs), regressors=regressors, training_pairs=label)


def _call_pd(wrap, label, regressors):
    pairs = wrap(_state_pairs())
    return pd.fit_pd_terms(pairs, [0.5] * len(pairs), regressors=regressors, terms=("quarter_end",), training_pairs=label)


def _call_carry(wrap, label, regressors):
    pairs = wrap(_state_pairs())
    return carry.fit_carry_terms(pairs, [0.5] * len(pairs), regressors=regressors, terms=("quarter_end",), training_pairs=label)


def _call_b4(wrap, label, regressors):
    pairs = [b4.Pair(float(i % 9), 0.0, 1.0, _flags(i)) for i in range(120)]
    return b4.fit_quantile_regression(
        wrap(pairs), regressors=regressors + ("reserve_balances",), terms=("quarter_end",), training_pairs=label, levels=GRID
    )


FITTERS = {
    "fit_calendar_terms": _call_calendar,
    "fit_state_terms": _call_state,
    "fit_type_factors": _call_scale,
    "fit_regimes": _call_regime,
    "fit_pd_terms": _call_pd,
    "fit_carry_terms": _call_carry,
    "fit_quantile_regression": _call_b4,
}
CALENDAR = ("quarter_end",)


def direct(pairs):
    return osg.stamp_pairs(pairs, direct=True)


def one_step(pairs):
    return osg.stamp_pairs(pairs, direct=False)


def plain(pairs):
    return pairs


class MislabelledPairsTests(unittest.TestCase):
    def test_a_one_step_stamp_under_a_direct_label_is_refused(self):
        for name, call in FITTERS.items():
            with self.subTest(fitter=name):
                with self.assertRaisesRegex(ValueError, r"built 'one_step'.*training_pairs='direct'"):
                    call(one_step, "direct", CALENDAR)

    def test_a_one_step_stamp_is_refused_even_with_no_calendar_column(self):
        for name, call in FITTERS.items():
            with self.subTest(fitter=name):
                with self.assertRaisesRegex(ValueError, "built 'one_step'"):
                    call(one_step, "direct", ())

    def test_unstamped_pairs_that_read_a_calendar_column_are_refused(self):
        for name, call in FITTERS.items():
            with self.subTest(fitter=name):
                with self.assertRaisesRegex(ValueError, r"no stamp.*quarter_end"):
                    call(plain, "direct", CALENDAR)

    def test_a_direct_stamp_passes(self):
        for name, call in FITTERS.items():
            with self.subTest(fitter=name):
                self.assertIsNotNone(call(direct, "direct", CALENDAR))

    def test_unstamped_pairs_with_no_calendar_column_pass(self):
        for name, call in FITTERS.items():
            with self.subTest(fitter=name):
                self.assertIsNotNone(call(plain, "direct", ()))


class StampTests(unittest.TestCase):
    def test_a_derived_list_loses_the_stamp_and_stamp_like_restores_it(self):
        pairs = direct([1, 2, 3])
        self.assertEqual(getattr(pairs[:2], "built", ""), "")
        self.assertEqual(osg.stamp_like(pairs[:2], pairs).built, "direct")

    def test_stamp_like_does_not_invent_a_stamp(self):
        self.assertEqual(getattr(osg.stamp_like([1], [2]), "built", ""), "")

    def test_the_builders_stamp_by_their_own_setting(self):
        self.assertEqual(osg.stamp_pairs([], direct=False).built, "one_step")


if __name__ == "__main__":
    unittest.main()
