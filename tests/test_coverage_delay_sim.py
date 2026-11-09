"""`repo_model.coverage_delay_sim` (#1528; H5, step M5): the simulator behind the size-and-power study of amendment 4's coverage design.

The simulator makes a latent AR(1) with a two-state Markov volatility (volatility clustering), observed through a calendar-class scale, and a
forecaster that reads the last PUBLISHED day, D - 1, for a target D + h (the one-day publication delay: n = h + 1 steps ahead). The forecaster's
distribution is the exact mixture over the volatility paths it cannot see. What these tests pin:

- the mixture's weights and variances on hand cases (one and two steps), and that its CDF is a proper one;
- a correctly specified forecaster's PIT is uniform at every lead, and, with the delay, PITs of decision days h + 1 apart are independent while
  those h apart are not (the reason the spacing matters), on a long seeded path;
- a misspecified forecaster differs from the true one only where it is misspecified (a scale on calendar classes changes those target days only;
  a lag of zero is the truth; a narrower scale makes more PITs fall in the tails);
- the engine's p-values equal `scoring_protocol.coverage_cells` (method "thinned") on a world with continuous outcomes, and its Holm count
  equals `scoring_protocol.holm`;
- the fit recovers a known AR coefficient, volatility states and class scales from a long simulated series;
- the window guard: `require_development` refuses a day after the window's last day.

Recorded mutation for the window guard (a new leakage guard): changing `if day > last:` to `if day > last + timedelta(days=4000):` in
`coverage_delay_sim.require_development` makes `WindowGuardTests.test_a_day_after_the_last_day_is_refused` fail with `AssertionError:
LookAheadError not raised`.

Recorded mutation for the delay (the information set): reading the forecast's starting point from `x[position]` instead of
`x[last_published]` in `coverage_delay_sim.pit` makes `DelayTests.test_pits_h_plus_one_apart_are_independent_and_h_apart_are_not` fail with
`AssertionError: 0.1113... not less than 0.03` (the PITs h + 1 apart are then dependent), and `PitTests.test_the_true_forecaster_is_uniform` and
`PitTests.test_a_narrow_forecaster_has_too_many_tail_pits_and_a_wide_one_too_few` fail with `AssertionError` too (the forecast then reads the day it
forecasts).
"""

from __future__ import annotations

import random
import unittest
from datetime import date, timedelta
from statistics import NormalDist

from repo_model import coverage_delay_sim as sim
from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

N = NormalDist()
CAL = sim.Calibration(
    phi=0.8, sigma=(0.5, 1.5), stay=(0.95, 0.9),
    scale={"ordinary": 1.0, "quarter_end": 2.0, "month_end": 1.3, "tax_date": 1.2, "settlement": 1.1, "policy": 1.0},
)


def business_days(start: date, n: int):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def structure(n_days: int, classes_cycle=("ordinary",) * 9 + ("quarter_end",)):
    """Decision days at positions 1 .. n_days (position 0 is the first published day), three regimes, a class every tenth day."""

    calendar = business_days(date(2019, 1, 2), n_days + 8)
    classes = [classes_cycle[i % len(classes_cycle)] for i in range(len(calendar))]
    positions = list(range(1, n_days + 1))
    regimes = ["a" if i < n_days // 3 else "b" if i < 2 * n_days // 3 else "c" for i in range(n_days)]
    return sim.Structure(calendar=calendar, classes=classes, positions=positions, regimes=regimes)


class MixtureTests(unittest.TestCase):
    def test_one_step_from_each_state_is_the_two_state_mixture(self):
        for z0, stay in ((0, 0.95), (1, 0.9)):
            w, v = sim.components(CAL.phi, CAL.sigma, CAL.stay, z0, 1)
            self.assertAlmostEqual(sum(w), 1.0)
            by_var = {round(var, 9): wt for wt, var in zip(w, v)}
            # one step from z0: the next state is z0 with `stay`, the other with 1 - stay; variance sigma^2 of the state reached
            low, high = CAL.sigma[0] ** 2, CAL.sigma[1] ** 2
            self.assertAlmostEqual(by_var[round(low, 9)], stay if z0 == 0 else 1 - stay)
            self.assertAlmostEqual(by_var[round(high, 9)], 1 - stay if z0 == 0 else stay)

    def test_two_steps_from_the_calm_state_by_hand(self):
        w, v = sim.components(CAL.phi, CAL.sigma, CAL.stay, 0, 2)
        phi, (s0, s1), (a, b) = CAL.phi, CAL.sigma, CAL.stay
        # paths (z1, z2) from z0 = 0; variance = phi^2 s(z1)^2 + s(z2)^2
        expected = {
            (0, 0): a * a, (0, 1): a * (1 - a), (1, 0): (1 - a) * (1 - b), (1, 1): (1 - a) * b,
        }
        sigma = (s0, s1)
        got = sorted(zip(v, w))
        want = sorted((phi ** 2 * sigma[p[0]] ** 2 + sigma[p[1]] ** 2, wt) for p, wt in expected.items())
        for (gv, gw), (wv, ww) in zip(got, want):
            self.assertAlmostEqual(gv, wv)
            self.assertAlmostEqual(gw, ww)

    def test_the_cdf_is_proper_and_symmetric_about_the_mean(self):
        w, v = sim.components(CAL.phi, CAL.sigma, CAL.stay, 1, 3)
        self.assertAlmostEqual(sim.mixture_cdf(2.0, 2.0, w, v), 0.5)
        self.assertLess(sim.mixture_cdf(-50.0, 0.0, w, v), 1e-12)
        self.assertGreater(sim.mixture_cdf(50.0, 0.0, w, v), 1 - 1e-12)
        grid = [sim.mixture_cdf(x / 4, 0.0, w, v) for x in range(-40, 41)]
        self.assertEqual(grid, sorted(grid))
        self.assertAlmostEqual(sim.mixture_cdf(1.0, 0.0, w, v) + sim.mixture_cdf(-1.0, 0.0, w, v), 1.0)

    def test_a_scale_widens_the_mixture(self):
        w, v = sim.components(CAL.phi, CAL.sigma, CAL.stay, 0, 2)
        self.assertLess(sim.mixture_cdf(1.0, 0.0, w, v, 2.0), sim.mixture_cdf(1.0, 0.0, w, v, 1.0))


class PitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.struct = structure(30000)
        cls.x, cls.z = sim.simulate_latent(CAL, len(cls.struct.calendar), random.Random(11))
        cls.truth = sim.pit_columns(CAL, cls.x, cls.z, cls.struct, sim.Forecaster("truth"))

    def test_the_true_forecaster_is_uniform(self):
        for h in sp.HORIZONS:
            u = self.truth[h]
            for level in (0.01, 0.05, 0.5, 0.95, 0.99):
                share = sum(1 for v in u if v < level) / len(u)
                se = (level * (1 - level) / len(u)) ** 0.5
                self.assertLess(abs(share - level), 4.5 * se * 2.5, (h, level, share))

    def test_a_lag_of_zero_and_a_scale_of_one_are_the_truth(self):
        same = sim.pit_columns(CAL, self.x, self.z, self.struct, sim.Forecaster("same", scale=1.0, lag=0))
        self.assertEqual(same, self.truth)

    def test_a_scale_on_a_class_changes_those_target_days_only(self):
        fc = sim.Forecaster("qe", scale=0.5, on=frozenset({"quarter_end"}))
        cols = sim.pit_columns(CAL, self.x, self.z, self.struct, fc)
        for h in (1, 3):
            for i, pos in enumerate(self.struct.positions[:2000]):
                if self.struct.classes[pos + h] == "quarter_end":
                    self.assertNotEqual(cols[h][i], self.truth[h][i])
                else:
                    self.assertEqual(cols[h][i], self.truth[h][i])

    def test_a_narrow_forecaster_has_too_many_tail_pits_and_a_wide_one_too_few(self):
        narrow = sim.pit_columns(CAL, self.x, self.z, self.struct, sim.Forecaster("n", scale=0.7))
        wide = sim.pit_columns(CAL, self.x, self.z, self.struct, sim.Forecaster("w", scale=1.4))
        out = lambda col: sum(1 for v in col if v < 0.05 or v > 0.95) / len(col)
        self.assertGreater(out(narrow[2]), 0.14)
        self.assertLess(out(wide[2]), 0.06)
        self.assertAlmostEqual(out(self.truth[2]), 0.10, delta=0.012)

    def test_a_lagged_volatility_state_differs_from_the_truth_but_stays_a_proper_pit(self):
        cols = sim.pit_columns(CAL, self.x, self.z, self.struct, sim.Forecaster("lag", lag=5))
        self.assertNotEqual(cols[1], self.truth[1])
        self.assertTrue(all(0.0 <= v <= 1.0 for v in cols[1]))


class DelayTests(unittest.TestCase):
    def test_pits_h_plus_one_apart_are_independent_and_h_apart_are_not(self):
        cal = sim.Calibration(phi=0.9, sigma=(1.0, 1.0), stay=(0.9, 0.9), scale={c: 1.0 for c in sim.CLASSES})
        n = 60000
        st = structure(n, ("ordinary",))
        x, z = sim.simulate_latent(cal, len(st.calendar), random.Random(5))
        u = sim.pit_columns(cal, x, z, st, sim.Forecaster("truth"))
        for h in (1, 2):
            col = u[h]

            def corr(gap):
                a, b = col[:-gap], col[gap:]
                ma, mb = sum(a) / len(a), sum(b) / len(b)
                cov = sum((p - ma) * (q - mb) for p, q in zip(a, b))
                return cov / (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** 0.5

            self.assertGreater(corr(h), 0.1, (h, corr(h)))  # h apart: the next forecast's horizon contains this target's innovation
            self.assertLess(abs(corr(h + 1)), 0.03, (h, corr(h + 1)))
            self.assertLess(abs(corr(h + 2)), 0.03, (h, corr(h + 2)))


class EngineTests(unittest.TestCase):
    def _world(self, n_days=180, seed=3):
        rng = random.Random(seed)
        st = structure(n_days, ("ordinary",))
        # outcomes ~ N(0, 1.2) and the forecast N(0, 1): a PIT is N.cdf(y); the quantile vector is the forecast's own
        y = {d: rng.gauss(0, 1.2) for d in st.calendar}
        for i in range(1, len(st.calendar)):
            y[st.calendar[i]] += 0.5 * y[st.calendar[i - 1]]
        return st, y

    def test_p_values_equal_coverage_cells_thinned(self):
        st, y = self._world()
        decisions = [st.calendar[p] for p in st.positions]
        forecasts = {d: {h: [N.inv_cdf(level) for level in sp.GRID] for h in sp.HORIZONS} for d in decisions}
        regimes = {d: r for d, r in zip(decisions, st.regimes)}
        cells = sp.coverage_cells(forecasts, y, st.calendar, regimes, method="thinned")
        u = {h: [N.cdf(y[st.calendar[p + h]]) for p in st.positions] for h in sp.HORIZONS}
        table = sim.cell_p_values(st, u)
        checked = 0
        for c in cells:
            if c.rule != "strict" or c.level not in sim.LEVELS:
                continue
            row = table[(c.lead, c.regime, c.level)]
            self.assertAlmostEqual(row["kupiec_h"], c.kupiec_p, places=12)
            self.assertAlmostEqual(row["indep_h"], c.independence_p, places=12)
            checked += 1
        self.assertEqual(checked, len(sp.HORIZONS) * 3 * len(sim.LEVELS))

    def test_the_h_plus_one_spacing_thins_by_h_plus_one(self):
        st, y = self._world()
        u = {h: [N.cdf(y[st.calendar[p + h]]) for p in st.positions] for h in sp.HORIZONS}
        table = sim.cell_p_values(st, u)
        for h in (1, 3):
            kept = [i for i, r in enumerate(st.regimes) if r == "b" and i % (h + 1) == 0]
            hits = [int(u[h][i] > 0.95) for i in kept]
            from repo_model import coverage_tests as ct

            self.assertAlmostEqual(table[(h, "b", 0.95)]["indep_h1"], ct.christoffersen_independence(hits).p_value, places=12)
            self.assertAlmostEqual(table[(h, "b", 0.95)]["kupiec_h1"], ct.kupiec(hits, 0.05).p_value, places=12)

    def test_holm_count_is_the_protocols(self):
        rng = random.Random(1)
        for _ in range(300):
            m = rng.randint(1, 40)
            ps = [rng.random() ** rng.choice((1, 3, 6)) for _ in range(m)]
            theirs = sum(sp.holm({str(i): p for i, p in enumerate(ps)}, 0.05).values())
            self.assertEqual(len(sim.holm_rejected(ps, 0.05)), theirs)

    def test_rules_name_the_two_p_values_each_reads(self):
        self.assertEqual(sim.RULES["h"], ("kupiec_h", "indep_h"))
        self.assertEqual(sim.RULES["indep_h1"], ("kupiec_h", "indep_h1"))
        self.assertEqual(sim.RULES["h1"], ("kupiec_h1", "indep_h1"))

    def test_a_family_has_two_tests_per_cell(self):
        st, y = self._world()
        u = {h: [N.cdf(y[st.calendar[p + h]]) for p in st.positions] for h in sp.HORIZONS}
        table = sim.cell_p_values(st, u)
        ps, who = sim.family(table, "h")
        self.assertEqual(len(ps), 2 * len(sp.HORIZONS) * 3 * len(sim.LEVELS))
        self.assertEqual(len(who), len(ps))


class FitTests(unittest.TestCase):
    def test_the_fit_recovers_the_process(self):
        true = sim.Calibration(
            phi=0.6, sigma=(0.6, 2.4), stay=(0.97, 0.93),
            scale={"ordinary": 1.0, "quarter_end": 3.0, "month_end": 1.0, "tax_date": 1.0, "settlement": 1.0, "policy": 1.0},
        )
        n = 6000
        classes = [("quarter_end" if i % 40 == 0 else "ordinary") for i in range(n)]
        x, _z = sim.simulate_latent(true, n, random.Random(2))
        series = [3.0 * v if c == "quarter_end" else v for v, c in zip(x, classes)]
        regimes = ["r"] * n
        fit = sim.fit_calibration(series, classes, regimes)
        self.assertAlmostEqual(fit.phi, 0.6, delta=0.06)
        self.assertAlmostEqual(fit.scale["quarter_end"], 3.0, delta=0.9)
        # the states are identified up to the common scale of the standardised series
        self.assertGreater(fit.sigma[1] / fit.sigma[0], 2.5)
        self.assertAlmostEqual(fit.stay[0], 0.97, delta=0.03)
        self.assertAlmostEqual(fit.stay[1], 0.93, delta=0.05)

    def test_a_class_with_no_days_gets_a_scale_of_one(self):
        series = [random.Random(i).gauss(0, 1) for i in range(300)]
        fit = sim.fit_calibration(series, ["ordinary"] * 300, ["r"] * 300)
        self.assertEqual(fit.scale["tax_date"], 1.0)


class ClassTests(unittest.TestCase):
    def test_a_day_takes_the_highest_priority_class(self):
        self.assertEqual(sim.day_class(["bill_settlement", "quarter_end"]), "quarter_end")
        self.assertEqual(sim.day_class(["coupon_settlement", "month_end"]), "month_end")
        self.assertEqual(sim.day_class(["fomc_day"]), "policy")
        self.assertEqual(sim.day_class(["dom_19_23", "post_month_end_window"]), "ordinary")
        self.assertEqual(sim.day_class(["ordinary"]), "ordinary")


class WindowGuardTests(unittest.TestCase):
    def test_a_day_after_the_last_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            sim.require_development([date(2025, 12, 31), date(2026, 1, 2)], date(2025, 12, 31), where="test")

    def test_the_last_day_itself_is_allowed(self):
        sim.require_development([date(2025, 12, 30), date(2025, 12, 31)], date(2025, 12, 31), where="test")


if __name__ == "__main__":
    unittest.main()
