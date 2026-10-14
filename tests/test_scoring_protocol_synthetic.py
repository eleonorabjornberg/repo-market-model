"""H1: the synthetic suite of scoring protocol v1, written before the scorer (#655).

`docs/decisions/scoring-protocol.md` §9 makes H1 a pass-or-fail test, run before any
registration: the scorer must recover the known order of forecasts of known quality.
This module states that order and checks `repo_model.scoring_protocol` against it.

**The world.** A spread in bp follows a Gaussian AR(1), `y[t] = PHI * y[t-1] + e[t]` with
`e ~ N(0, SIGMA^2)`, on a weekday calendar of unlocked days. A forecast is made on decision
day `t`, knowing `y[t]`, for leads h = 1..5 (the target is the h-th calendar day after `t`).
Every forecast is a vector of the protocol's 23 quantiles per lead.

**The forecasts, and the order expected of them** (a smaller score is better; `<` reads "is
expected to score lower than"):

1. *oracle* (every quantile at the realised outcome) `<` every other forecast. It scores 0.
2. *ideal* (the true conditional law, `N(PHI^h y[t], V_h)`) `<` every forecast below except the
   noisy-truth ones, which know something about the future. This is propriety: grid CRPS is
   a sum of quantile scores, each minimised in expectation by the true quantile.
3. *shifted* ideal, by +k and -k bp for k = 1, 2, 5: ideal `<` shift 1 `<` shift 2 `<` shift 5,
   for each sign separately. No order is claimed between +k and -k: the law is symmetric.
4. *dispersed* ideal, every quantile moved away from the median by x0.5 and x2:
   ideal `<` x0.5 `<` x2.
5. *persistence* (`y[t]` plus the unconditional law of the h-day change,
   `N(0, 2 (1 - PHI^h) VAR)`) and *climatology* (the unconditional law, `N(0, VAR)`):
   ideal `<` persistence `<` climatology.
6. *lead-misaligned* ideal: lead h served the ideal forecast of lead h + 1 ("off by one"), and
   lead h served that of lead 6 - h ("reversed"): ideal `<` each.
7. *noisy truth* at five graded skill levels: the forecaster also sees `y[t+h] + u`, with
   `u ~ N(0, s^2)` for s = 0.5, 1, 2, 4 and 8 bp, and issues its exact Bayesian posterior:
   oracle `<` s = 0.5 `<` 1 `<` 2 `<` 4 `<` 8 `<` ideal.

Orders 3 to 5 are not consequences of propriety. Each is checked here against the expected
score computed in closed form (`expected_score`), independent of the scorer: for a quantile
`q` of a truth `N(m, v)`, the expected pinball loss is `(m - q)(tau - Phi(z)) + sqrt(v) phi(z)`
with `z = (q - m) / sqrt(v)`. Where the forecast depends on `y[t]`, the expectation over
`y[t] ~ N(0, VAR)` is taken by quadrature. A calibrated posterior's expected score is exactly
`2 * mean over tau of sd * phi(z_tau)`, which falls with its sd, which falls with s.

**What "recovers" means.** For every ordered pair (better, worse), the protocol's paired test,
with the worse forecast as benchmark and the better as candidate, gives a positive mean daily
difference `d = S(worse) - S(better)`, and its one-sided 95% studentized stationary-bootstrap
lower bound (mean block 10, HAC lag 10; ruling of 13 October 2026, PR #660) is above zero. The
same holds with the upper-tail twCRPS, for the pairs where its order is known (stated in
`TWCRPS_ORDERS`).

**Draws.** Studentizing costs a long-run variance per resample per pair, and on 5,000 days and
every pair that is too slow at the protocol's 10,000 draws for the suite. Every pair is therefore
checked at `SUITE_DRAWS`, and the closest pair (ideal against the off-by-one lead, under the
twCRPS) is checked again at the protocol's 10,000 (`test_the_closest_pair_at_the_protocols_draws`).
"""

from __future__ import annotations

import math
import random
import unittest
from datetime import date, timedelta
from statistics import NormalDist

from repo_model import scoring_protocol as sp

PHI = 0.9
SIGMA = 1.5
VAR = SIGMA**2 / (1.0 - PHI**2)
#: Decision days. The closest stated pair, ideal against the off-by-one lead under the
#: twCRPS, has an expected Diebold-Mariano z of about 4 on this many days (measured on
#: longer paths), so its one-sided 95% bound is resolved on all but a small share of paths.
#: The same pair needs about 2,000 days for an expected z of 2.5: a lead slip of one day
#: is not something the protocol's 250 days can see in a world like this one.
DECISION_DAYS = 5000
SEED = 655
#: Bootstrap draws for the all-pairs check; see "Draws" above.
SUITE_DRAWS = 500
START = date(2001, 1, 2)
STANDARD = NormalDist()
NOISE_LEVELS = (0.5, 1.0, 2.0, 4.0, 8.0)
SHIFTS = (1.0, 2.0, 5.0)


def weekdays(start, count):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def ahead_variance(h):
    return SIGMA**2 * (1.0 - PHI ** (2 * h)) / (1.0 - PHI**2)


def gaussian_quantiles(mean, sd):
    return [mean + sd * STANDARD.inv_cdf(level) for level in sp.GRID]


# --------------------------------------------------------------------------
# The forecasters: each maps (y[t], h, extra) to 23 quantiles
# --------------------------------------------------------------------------


def ideal(y, h):
    return gaussian_quantiles(PHI**h * y, math.sqrt(ahead_variance(h)))


def shifted(k):
    return lambda y, h: [q + k for q in ideal(y, h)]


def dispersed(c):
    def forecast(y, h):
        median = PHI**h * y
        return [median + c * (q - median) for q in ideal(y, h)]

    return forecast


def persistence(y, h):
    return gaussian_quantiles(y, math.sqrt(2.0 * (1.0 - PHI**h) * VAR))


def climatology(y, h):
    return gaussian_quantiles(0.0, math.sqrt(VAR))


def off_by_one(y, h):
    return ideal(y, h + 1)


def reversed_leads(y, h):
    return ideal(y, 6 - h)


DETERMINISTIC = {
    "ideal": ideal,
    **{f"shift+{k:g}": shifted(k) for k in SHIFTS},
    **{f"shift-{k:g}": shifted(-k) for k in SHIFTS},
    "dispersed x0.5": dispersed(0.5),
    "dispersed x2": dispersed(2.0),
    "persistence": persistence,
    "climatology": climatology,
    "misaligned off-by-one": off_by_one,
    "misaligned reversed": reversed_leads,
}


def posterior(y, h, signal, noise):
    prior_mean, prior_var = PHI**h * y, ahead_variance(h)
    var = 1.0 / (1.0 / prior_var + 1.0 / noise**2)
    return gaussian_quantiles(var * (prior_mean / prior_var + signal / noise**2), math.sqrt(var))


# --------------------------------------------------------------------------
# The stated orders
# --------------------------------------------------------------------------


def _chain(names):
    return [(better, worse) for position, better in enumerate(names) for worse in names[position + 1:]]


ORDERS = (
    [("oracle", name) for name in list(DETERMINISTIC) + [f"noisy s={s:g}" for s in NOISE_LEVELS]]
    + [("ideal", name) for name in DETERMINISTIC if name != "ideal"]
    + _chain(["ideal", "shift+1", "shift+2", "shift+5"])
    + _chain(["ideal", "shift-1", "shift-2", "shift-5"])
    + _chain(["ideal", "dispersed x0.5", "dispersed x2"])
    + _chain(["ideal", "persistence", "climatology"])
    + _chain([f"noisy s={s:g}" for s in NOISE_LEVELS] + ["ideal"])
)
ORDERS = list(dict.fromkeys(ORDERS))

#: The pairs whose order under the upper-tail twCRPS is also known. Propriety carries over:
#: the twCRPS with weight 1{z > 0} is the CRPS of the forecast and outcome both mapped
#: through max(., 0), and the ideal forecast's image is the truth's image. The oracle is
#: still 0. The graded orders are not claimed: a shift or a spread change below zero is
#: partly invisible to it.
TWCRPS_ORDERS = [pair for pair in ORDERS if pair[0] in ("oracle", "ideal")]


# --------------------------------------------------------------------------
# Expected scores in closed form, independent of the scorer
# --------------------------------------------------------------------------


def expected_pinball(level, q, mean, var):
    sd = math.sqrt(var)
    z = (q - mean) / sd
    return (mean - q) * (level - STANDARD.cdf(z)) + sd * STANDARD.pdf(z)


def expected_grid_crps(quantiles, mean, var):
    return 2.0 * sum(
        expected_pinball(level, q, mean, var) for level, q in zip(sp.GRID, quantiles)
    ) / len(sp.GRID)


def expected_score(forecaster, nodes=801, span=8.0):
    """E over y[t] ~ N(0, VAR) of the day score (mean over h = 1..5), by Simpson's rule."""

    sd = math.sqrt(VAR)
    step = 2.0 * span / (nodes - 1)
    total = 0.0
    for node in range(nodes):
        x = -span + node * step
        weight = (1 if node in (0, nodes - 1) else (4 if node % 2 else 2)) * step / 3.0
        y = x * sd
        day = sum(
            expected_grid_crps(forecaster(y, h), PHI**h * y, ahead_variance(h))
            for h in sp.HORIZONS
        ) / len(sp.HORIZONS)
        total += weight * STANDARD.pdf(x) * day
    return total


def expected_posterior_score(noise):
    total = 0.0
    for h in sp.HORIZONS:
        var = 1.0 / (1.0 / ahead_variance(h) + 1.0 / noise**2)
        total += 2.0 * sum(
            math.sqrt(var) * STANDARD.pdf(STANDARD.inv_cdf(level)) for level in sp.GRID
        ) / len(sp.GRID)
    return total / len(sp.HORIZONS)


def expected_scores():
    out = {name: expected_score(forecaster) for name, forecaster in DETERMINISTIC.items()}
    out.update({f"noisy s={s:g}": expected_posterior_score(s) for s in NOISE_LEVELS})
    out["oracle"] = 0.0
    return out


# --------------------------------------------------------------------------
# One simulated world
# --------------------------------------------------------------------------


def simulate(decision_days=DECISION_DAYS, seed=SEED):
    """The calendar, the outcomes, and every forecaster's forecasts on one path."""

    rng = random.Random(seed)
    days = weekdays(START, decision_days + max(sp.HORIZONS) + 1)
    y = [rng.gauss(0.0, math.sqrt(VAR))]
    for _ in days[1:]:
        y.append(PHI * y[-1] + rng.gauss(0.0, SIGMA))
    outcomes = dict(zip(days, y))
    forecasts = {name: {} for name in list(DETERMINISTIC) + ["oracle"]}
    forecasts.update({f"noisy s={s:g}": {} for s in NOISE_LEVELS})
    for t in range(1, decision_days + 1):
        day = days[t]
        for name, forecaster in DETERMINISTIC.items():
            forecasts[name][day] = {h: forecaster(y[t], h) for h in sp.HORIZONS}
        forecasts["oracle"][day] = {h: [y[t + h]] * len(sp.GRID) for h in sp.HORIZONS}
        for s in NOISE_LEVELS:
            forecasts[f"noisy s={s:g}"][day] = {
                h: posterior(y[t], h, y[t + h] + rng.gauss(0.0, s), s) for h in sp.HORIZONS
            }
    return days, outcomes, forecasts


class StatedOrderTests(unittest.TestCase):
    """The orders this module states are the ones the closed form gives."""

    @classmethod
    def setUpClass(cls):
        cls.expected = expected_scores()

    def test_the_grid_is_the_protocols(self):
        self.assertEqual(len(sp.GRID), 23)
        self.assertEqual(
            sp.GRID,
            (0.01, 0.025, 0.05)
            + tuple(round(0.10 + 0.05 * k, 2) for k in range(17))
            + (0.95, 0.975, 0.99),
        )
        self.assertEqual(sp.HORIZONS, (1, 2, 3, 4, 5))

    def test_every_stated_order_holds_in_expectation(self):
        for better, worse in ORDERS:
            with self.subTest(better=better, worse=worse):
                self.assertLess(self.expected[better], self.expected[worse])

    def test_the_closed_form_agrees_with_the_scorer_on_one_day(self):
        """The independent expectation and the scorer read the same score."""

        rng = random.Random(1)
        quantiles = ideal(2.0, 3)
        mean, var = PHI**3 * 2.0, ahead_variance(3)
        draws = [rng.gauss(mean, math.sqrt(var)) for _ in range(40000)]
        simulated = sum(sp.grid_crps(quantiles, y) for y in draws) / len(draws)
        self.assertAlmostEqual(simulated, expected_grid_crps(quantiles, mean, var), delta=0.03)


class RecoveryTests(unittest.TestCase):
    """The scorer recovers the stated order on every pair, at the protocol's settings."""

    @classmethod
    def setUpClass(cls):
        cls.days, cls.outcomes, cls.forecasts = simulate()
        cls.crps = {
            name: sp.day_scores(forecast, cls.outcomes, cls.days)
            for name, forecast in cls.forecasts.items()
        }
        cls.twcrps = {
            name: sp.day_scores(forecast, cls.outcomes, cls.days, score=sp.upper_tail_twcrps)
            for name, forecast in cls.forecasts.items()
        }

        pairs = [(cls.crps[worse], cls.crps[better]) for better, worse in ORDERS]
        pairs += [(cls.twcrps[worse], cls.twcrps[better]) for better, worse in TWCRPS_ORDERS]
        # One resample stream for every pair, as the protocol reads them.
        results = sp.paired_tests(pairs, seed=SEED, draws=SUITE_DRAWS, with_skill=False)
        cls.crps_tests = dict(zip(ORDERS, results[: len(ORDERS)]))
        cls.twcrps_tests = dict(zip(TWCRPS_ORDERS, results[len(ORDERS):]))

    def test_one_score_per_decision_day(self):
        for name, scores in self.crps.items():
            with self.subTest(forecast=name):
                self.assertEqual(sorted(scores), self.days[1 : DECISION_DAYS + 1])

    def test_the_oracle_scores_zero(self):
        self.assertTrue(all(value == 0.0 for value in self.crps["oracle"].values()))
        self.assertTrue(all(value == 0.0 for value in self.twcrps["oracle"].values()))

    def test_the_protocol_settings_are_the_ones_used(self):
        test = next(iter(self.crps_tests.values()))
        self.assertEqual(test.draws, SUITE_DRAWS)
        self.assertEqual(test.block_length, sp.BLOCK_LENGTH)
        self.assertEqual(test.alpha, sp.ALPHA)

    def test_the_closest_pair_at_the_protocols_draws(self):
        test = sp.paired_test(
            self.twcrps["misaligned off-by-one"], self.twcrps["ideal"], seed=SEED, with_skill=False
        )
        self.assertEqual(test.draws, 10_000)
        self.assertGreater(test.lower_mean_difference(), 0.0)

    def test_grid_crps_recovers_every_stated_order(self):
        for (better, worse), test in self.crps_tests.items():
            with self.subTest(better=better, worse=worse):
                self.assertGreater(test.mean_difference, 0.0)
                self.assertGreater(test.lower_mean_difference(), 0.0)

    def test_upper_tail_twcrps_recovers_its_stated_orders(self):
        for (better, worse), test in self.twcrps_tests.items():
            with self.subTest(better=better, worse=worse):
                self.assertGreater(test.mean_difference, 0.0)
                self.assertGreater(test.lower_mean_difference(), 0.0)

    def test_the_sign_convention_is_one_way_round(self):
        """d = S(benchmark) - S(candidate): a better candidate has positive d and skill."""

        good, bad = self.crps["ideal"], self.crps["climatology"]
        forward = sp.paired_tests([(bad, good)], seed=SEED, draws=50)[0]
        backward = sp.paired_tests([(good, bad)], seed=SEED, draws=50)[0]
        self.assertGreater(forward.mean_difference, 0.0)
        self.assertGreater(forward.skill, 0.0)
        self.assertAlmostEqual(forward.mean_difference, -backward.mean_difference)
        self.assertLess(backward.skill, 0.0)

    def test_diebold_mariano_agrees_on_every_stated_order(self):
        for (better, worse), test in self.crps_tests.items():
            with self.subTest(better=better, worse=worse):
                self.assertGreater(test.dm_statistic, 0.0)
                self.assertLess(test.dm_p_value, 0.05)


if __name__ == "__main__":
    unittest.main()
