"""H1 step 3 (#1022): the block length of the loss differentials after April 2020, with and without 2019-09-18.

The arithmetic is checked on hand cases and on series with known answers, with no walk: the long-run-variance ratio
(Lens C's formula, 1 + 2 sum (1 - k / (L + 1)) rho(k)), the three histories (full, without 2019-09-18, post-2020-04),
the proxy series S(B1) - S(B2) that Lens C read, the wider cap on the Politis-White truncation, and the page being
exactly what the record gives. The script changes no decided value (`BLOCK_LENGTH` stays 10) and adds no guard, so there
is no recorded mutation.
"""

import importlib.util
import json
import random
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = load("block_length_1022")
base = load("block_length_949")


def ar1(n, phi, seed):
    rng = random.Random(seed)
    x, out = 0.0, []
    for _ in range(n + 200):
        x = phi * x + rng.gauss(0.0, 1.0)
        out.append(x)
    return out[200:]


class LongRunRatioTests(unittest.TestCase):
    def test_uncorrelated_series_has_ratio_one(self):
        self.assertEqual(script.lrv_ratio([0.0] * 10, 10), 1.0)

    def test_hand_case(self):
        # rho = (0.5, 0) and L = 2: 1 + 2 * ((1 - 1/3) * 0.5 + (1 - 2/3) * 0) = 1 + 2/3
        self.assertAlmostEqual(script.lrv_ratio([0.5, 0.0], 2), 1.0 + 2.0 / 3.0, places=12)

    def test_ar1_limit(self):
        phi = 0.5
        rho = [phi ** k for k in range(1, 101)]
        self.assertAlmostEqual(script.lrv_ratio(rho, 100), (1 + phi) / (1 - phi), delta=0.1)

    def test_lag_beyond_the_acf_is_refused(self):
        with self.assertRaises(ValueError):
            script.lrv_ratio([0.1, 0.1], 5)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.pairs = [(date(2019, 9, 17), 1.0), (date(2019, 9, 18), 100.0), (date(2019, 9, 19), 2.0),
                      (date(2020, 4, 2), 3.0), (date(2020, 4, 3), 4.0), (date(2020, 4, 6), 5.0)]

    def test_full_keeps_everything(self):
        self.assertEqual(script.history(self.pairs, "full"), [1.0, 100.0, 2.0, 3.0, 4.0, 5.0])

    def test_without_the_day_drops_only_that_day(self):
        self.assertEqual(script.history(self.pairs, "without 2019-09-18"), [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_post_2020_starts_on_the_third_of_april(self):
        self.assertEqual(script.history(self.pairs, "post-2020-04"), [4.0, 5.0])

    def test_post_2020_never_holds_the_day(self):
        self.assertEqual(script.history(self.pairs, "post-2020-04 without 2019-09-18"), [4.0, 5.0])
        self.assertNotIn(100.0, script.history(self.pairs, "post-2020-04"))

    def test_an_unknown_history_is_refused(self):
        with self.assertRaises(ValueError):
            script.history(self.pairs, "since 2021")

    def test_window_variant_drops_the_decision_days_whose_targets_include_the_day(self):
        calendar = [date(2019, 9, 10) + timedelta(days=i) for i in range(12)]  # consecutive stand-in days
        hit = date(2019, 9, 18)
        affected = script.days_reaching(calendar, calendar, hit, leads=(1, 2, 3, 4, 5))
        # the decision days 1 to 5 positions before the day, and the day itself is not among them
        self.assertEqual(affected, {hit - timedelta(days=k) for k in range(1, 6)})


class ProxyTests(unittest.TestCase):
    def test_proxy_is_the_difference_of_the_two_legs(self):
        d_b1 = {date(2021, 1, 4): 0.7, date(2021, 1, 5): 0.2}
        d_b2 = {date(2021, 1, 4): 0.5, date(2021, 1, 6): 9.0}
        # S(B1) - S(B2) = (S(B1) - S(g)) - (S(B2) - S(g)), on the days both legs have
        self.assertEqual(script.proxy(d_b1, d_b2), {date(2021, 1, 4): 0.7 - 0.5})


class WiderCapTests(unittest.TestCase):
    def test_default_is_unchanged(self):
        x = ar1(900, 0.8, 3)
        self.assertEqual(base.politis_white(x), base.politis_white(x, None))

    def test_cap_is_used(self):
        x = ar1(900, 0.9, 5)
        self.assertNotEqual(base.politis_white(x, 2), base.politis_white(x))

    def test_wide_cap_never_asks_for_more_lags_than_the_series_has(self):
        x = ar1(200, 0.9, 7)
        self.assertGreater(script.summarize(x)["politis_white_wide"], 0.0)


class SummaryTests(unittest.TestCase):
    def test_summary_fields_and_lags(self):
        x = ar1(400, 0.6, 11)
        s = script.summarize(x)
        self.assertEqual(s["n"], 400)
        self.assertEqual(list(s["acf"]), [str(k) for k in script.ACF_LAGS])
        self.assertEqual(list(s["lrv_ratio"]), [str(k) for k in script.LRV_LAGS])
        self.assertAlmostEqual(s["acf"]["1"], 0.6, delta=0.12)
        self.assertGreater(s["lrv_ratio"]["100"], s["lrv_ratio"]["10"] * 0.95)

    def test_too_short_a_series_is_thin(self):
        self.assertEqual(script.summarize([0.0, 1.0] * 20), {"n": 40, "thin": True})

    def test_the_decided_block_is_untouched(self):
        self.assertEqual(sp.BLOCK_LENGTH, 10)
        self.assertEqual(script.PROTOCOL_BLOCK, sp.BLOCK_LENGTH)


class PageTests(unittest.TestCase):
    def record(self):
        x = ar1(400, 0.5, 13)
        entry = script.summarize(x)
        rows = {h: entry for h in script.HISTORIES}
        return {
            "reproduces_980": {"days": 10, "recorded_days": 10, "politis_white": {"B1": 4.8, "B2": 73.2},
                               "recorded_politis_white": {"B1": 4.8, "B2": 73.2}},
            "decision_days": {"n": 10, "first": "2018-06-29", "last": "2025-12-23"},
            "first_post_2020_day": "2020-04-03",
            "window_days_dropped": ["2019-09-11"],
            "gbm_funding_missing": {"days": 0, "share": 0.0},
            "regimes": ["2020", "2021-23", "2024", "2025-26"],
            "series": {name: {"all": rows, "regime": {r: entry for r in ("2020", "2021-23", "2024", "2025-26")}} for name in script.SERIES},
        }

    def test_page_is_a_function_of_the_record(self):
        record = self.record()
        self.assertEqual(script.render(record), script.render(json.loads(json.dumps(record))))

    def test_check_fails_when_the_page_differs(self):
        record = self.record()
        with tempfile.TemporaryDirectory() as tmp:
            record_path, page_path = Path(tmp) / "result.json", Path(tmp) / "page.md"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            page_path.write_text("edited by hand\n", encoding="utf-8")
            self.assertEqual(script.check(record_path, page_path), 1)
            page_path.write_text(script.render(record), encoding="utf-8")
            self.assertEqual(script.check(record_path, page_path), 0)


if __name__ == "__main__":
    unittest.main()
