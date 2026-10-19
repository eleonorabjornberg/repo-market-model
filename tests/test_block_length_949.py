"""H1 step 3 (#949): the autocorrelation of H5's paired CRPS loss differentials and the Politis-White block length.

The two new pieces are checked on series with known answers before they touch H5's data: the ACF of white noise is
near zero at every lag and an AR(1) series with coefficient phi has rho(k) = phi ** k; the automatic block length of
white noise is near one day and that of an AR(1) series is Politis and White's closed form,
((2 * phi / ((1 - phi) * (1 + phi))) ** 2) ** (1 / 3) * N ** (1 / 3), with the Patton-Politis-White (2009) correction for
the stationary bootstrap. The script changes no decided value (`BLOCK_LENGTH` stays 10).

No guard is added, so there is no recorded mutation.
"""

import importlib.util
import random
import unittest
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("block_length_949", ROOT / "scripts" / "block_length_949.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

PROTOCOL_BLOCK_BEFORE = sp.BLOCK_LENGTH


def white_noise(n, seed):
    rng = random.Random(seed)
    return [rng.gauss(0.0, 1.0) for _ in range(n)]


def ar1(n, phi, seed):
    rng = random.Random(seed)
    x, out = 0.0, []
    for _ in range(n + 200):  # a burn-in of 200
        x = phi * x + rng.gauss(0.0, 1.0)
        out.append(x)
    return out[200:]


class TestAcf(unittest.TestCase):
    def test_white_noise_has_no_autocorrelation(self):
        rho = script.acf(white_noise(20000, 1), 5)
        self.assertEqual(len(rho), 5)
        for value in rho:
            self.assertLess(abs(value), 0.03)

    def test_ar1_follows_phi_to_the_k(self):
        rho = script.acf(ar1(40000, 0.6, 2), 4)
        for k, value in enumerate(rho, start=1):
            self.assertAlmostEqual(value, 0.6 ** k, delta=0.03)

    def test_a_constant_series_is_refused(self):
        with self.assertRaises(ValueError):
            script.acf([1.0] * 50, 3)


class TestPolitisWhite(unittest.TestCase):
    def test_white_noise_needs_a_block_of_about_one_day(self):
        self.assertLess(script.politis_white(white_noise(20000, 3)), 3.0)

    def test_ar1_matches_the_closed_form(self):
        n, phi = 20000, 0.5
        expected = (2 * phi / ((1 - phi) * (1 + phi))) ** (2 / 3) * n ** (1 / 3)
        got = script.politis_white(ar1(n, phi, 4))
        self.assertAlmostEqual(got, expected, delta=0.3 * expected)

    def test_more_dependence_needs_a_longer_block(self):
        low, high = script.politis_white(ar1(8000, 0.2, 5)), script.politis_white(ar1(8000, 0.7, 5))
        self.assertGreater(high, low)

    def test_a_series_too_short_is_refused(self):
        with self.assertRaises(ValueError):
            script.politis_white([0.1, -0.2, 0.3])


class TestNothingDecidedMoves(unittest.TestCase):
    def test_the_protocols_block_stays_ten(self):
        self.assertEqual(sp.BLOCK_LENGTH, PROTOCOL_BLOCK_BEFORE)
        self.assertEqual(script.PROTOCOL_BLOCK, 10)
        self.assertIn(10, script.BLOCKS)


if __name__ == "__main__":
    unittest.main()
