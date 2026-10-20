"""Kupiec and Christoffersen coverage tests, stdlib only (#993).

A forecast quantile `q` at nominal exceedance probability `p` is hit on a day when the outcome lands beyond it. If the
forecast is calibrated the hits are independent Bernoulli(`p`) draws. Three likelihood-ratio tests ask that:

* `kupiec` (Kupiec 1995), unconditional coverage: is the hit rate `p`? Chi-square, 1 degree of freedom;
* `christoffersen_independence` (Christoffersen 1998): does a hit today change the chance of one tomorrow? A
  first-order Markov chain against a constant hit probability. Chi-square, 1 degree of freedom;
* `christoffersen_conditional_coverage`: the sum of the two statistics, 2 degrees of freedom. The Kupiec term uses
  every observation and the independence term the transitions between consecutive ones, the usual convention.

**Reporting only.** Nothing here sets a gate, level or threshold; a caller decides what a p-value means.

**Hit definition (open question, Eleonora's).** Whole-bp targets tie with the forecast quantile, so "beyond" is
`y > q` or `y >= q`, and the two give different hit rates. `hit_sequence` takes the rule as a required argument with
no default; this module does not choose. The tests themselves take a 0/1 sequence and do not care how it was made.

**Degenerate sequences.** The likelihoods use the convention 0 * ln 0 = 0, so no sequence needs a special case in
the statistic:

* no hits, or all hits: the unrestricted Kupiec likelihood is 1 and the statistic is `-2 N ln(1 - p)` or
  `-2 N ln(p)`; the independence statistic is 0 and its p-value 1 (a constant sequence has no transition to
  contradict independence);
* a previous-day state that never occurs (no transitions out of "hit", or out of "no hit"): that row of the Markov
  likelihood is 1 and the statistic uses the remaining row;
* fewer than two observations, so no transition at all: the independence test is undefined and raises `ValueError`.

Data guards raise `ValueError`: a hit must be 0, 1, `False` or `True`; the sequence must be non-empty; `p` must lie
strictly between 0 and 1.
"""

from __future__ import annotations

import math
from typing import NamedTuple, Sequence


class CoverageResult(NamedTuple):
    """A likelihood-ratio statistic, its chi-square p-value, the observations used and the hits among them."""

    statistic: float
    p_value: float
    n: int
    hits: int

HIT_RULES = ("above", "at_or_above")


def chi2_sf(statistic: float, df: int) -> float:
    """P(X > statistic) for a chi-square variable with 1 or 2 degrees of freedom, exactly, from the stdlib."""

    if df not in (1, 2):
        raise ValueError("chi2_sf supports 1 or 2 degrees of freedom, got %r" % (df,))
    if not (statistic >= 0.0) or math.isinf(statistic):
        raise ValueError("a likelihood-ratio statistic is finite and non-negative, got %r" % (statistic,))
    if df == 1:
        return math.erfc(math.sqrt(statistic / 2.0))
    return math.exp(-statistic / 2.0)


def _loglik(zeros: int, ones: int, p: float) -> float:
    """Bernoulli log-likelihood of `zeros` failures and `ones` successes, with 0 * ln 0 = 0."""

    out = 0.0
    if zeros:
        out += zeros * math.log(1.0 - p)
    if ones:
        out += ones * math.log(p)
    return out


def _hits(sequence: Sequence) -> list:
    out = []
    for h in sequence:
        if isinstance(h, bool) or (isinstance(h, int) and h in (0, 1)):
            out.append(int(h))
        else:
            raise ValueError("a hit is 0, 1, False or True, got %r" % (h,))
    if not out:
        raise ValueError("a coverage test needs at least one observation")
    return out


def _check_p(p: float) -> None:
    if not (0.0 < p < 1.0):
        raise ValueError("the nominal hit probability must lie strictly between 0 and 1, got %r" % (p,))


def _positive(statistic: float) -> float:
    """A likelihood ratio is non-negative; round-off can leave -1e-16 where the true value is 0."""

    return 0.0 if statistic < 0.0 else statistic


def kupiec(sequence: Sequence, p: float) -> CoverageResult:
    """Kupiec's proportion-of-failures test of a hit rate `p` on a 0/1 sequence."""

    _check_p(p)
    hits = _hits(sequence)
    n, x = len(hits), sum(hits)
    pi = x / n
    stat = _positive(-2.0 * (_loglik(n - x, x, p) - _loglik(n - x, x, pi)))
    return CoverageResult(stat, chi2_sf(stat, 1), n, x)


def transition_counts(sequence: Sequence) -> tuple:
    """(n00, n01, n10, n11): consecutive pairs by previous-day state then today's state."""

    hits = _hits(sequence)
    counts = [[0, 0], [0, 0]]
    for prev, today in zip(hits, hits[1:]):
        counts[prev][today] += 1
    return counts[0][0], counts[0][1], counts[1][0], counts[1][1]


def christoffersen_independence(sequence: Sequence) -> CoverageResult:
    """Christoffersen's independence test: a first-order Markov chain against a constant hit probability."""

    hits = _hits(sequence)
    if len(hits) < 2:
        raise ValueError("the independence test needs at least two observations (one transition)")
    n00, n01, n10, n11 = transition_counts(hits)
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)
    pi01 = n01 / (n00 + n01) if n00 + n01 else 0.0
    pi11 = n11 / (n10 + n11) if n10 + n11 else 0.0
    restricted = _loglik(n00 + n10, n01 + n11, pi)
    markov = _loglik(n00, n01, pi01) + _loglik(n10, n11, pi11)
    stat = _positive(-2.0 * (restricted - markov))
    return CoverageResult(stat, chi2_sf(stat, 1), len(hits), sum(hits))


def christoffersen_conditional_coverage(sequence: Sequence, p: float) -> CoverageResult:
    """Unconditional coverage plus independence, on 2 degrees of freedom."""

    uc = kupiec(sequence, p)
    ind = christoffersen_independence(sequence)
    stat = uc.statistic + ind.statistic
    return CoverageResult(stat, chi2_sf(stat, 2), uc.n, uc.hits)


def hit_sequence(outcomes: Sequence[float], quantiles: Sequence[float], *, rule: str) -> list:
    """0/1 hits of `outcomes` beyond `quantiles`; `rule` is "above" (y > q) or "at_or_above" (y >= q), no default."""

    if rule not in HIT_RULES:
        raise ValueError("rule must be one of %r, got %r" % (HIT_RULES, rule))
    if len(outcomes) != len(quantiles):
        raise ValueError("outcomes and quantiles differ in length: %d and %d" % (len(outcomes), len(quantiles)))
    out = []
    for y, q in zip(outcomes, quantiles):
        if not (math.isfinite(y) and math.isfinite(q)):
            raise ValueError("an outcome or quantile is not finite: %r, %r" % (y, q))
        out.append(int(y > q) if rule == "above" else int(y >= q))
    return out
