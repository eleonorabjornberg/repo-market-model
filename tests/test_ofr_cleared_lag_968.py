"""The corrected-lag comparison of the OFR cleared-repo series (#968): its checks and its tables."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ofr_cleared_lag_968", ROOT / "scripts" / "ofr_cleared_lag_968.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)

LEADS = ("1", "2", "3", "5", "10")


def cell(rho, n=100, pressure_days=10):
    return {"n": n, "pressure_days": pressure_days, "rho": rho}


def series(rhos):
    """A screened series whose pooled pressure correlation at each lead is `rhos[lead]`."""

    leads = {}
    for lead in LEADS:
        rho = rhos.get(lead)
        leads[lead] = {
            split: {"pressure": cell(rho), "level": cell(0.1), "change": cell(-0.1)}
            for split in ("all", "regime:ample", "regime:scarce")
        }
    return {
        "kind": "observed",
        "leads": leads,
        "pre_onset": {"all": {"auc": 0.6, "std_diff": 0.3, "n_pre": 5, "n_other": 90}},
    }


def screen():
    out = {}
    for original, copy_name in script.PAIRS:
        rhos = {"1": 0.10, "2": 0.20, "3": 0.30, "5": 0.40, "10": 0.50}
        out[original] = series(rhos)
        # one lead later reads the same row: copy[L] == original[L - 1] where both exist
        shifted = {"1": 0.05, "2": 0.10, "3": 0.20, "5": 0.41, "10": 0.51}
        out[copy_name] = series(shifted)
    out["other"] = series({lead: 0.35 for lead in LEADS})
    return {"series": out, "scope": {"scored_days": 100, "first_day": "2018-06-29", "last_day": "2026-09-03",
                                      "pressure_days": 10, "panel_sha256": "ab" * 32}}


class IdentityTests(unittest.TestCase):
    def test_a_copy_at_lead_L_is_the_original_at_lead_L_minus_1(self):
        data = screen()
        for original, copy_name in script.PAIRS:
            self.assertEqual(script.check_identity(data["series"][original], data["series"][copy_name]), [])

    def test_a_copy_that_reads_a_different_row_is_reported(self):
        data = screen()
        original, copy_name = script.PAIRS[0]
        data["series"][copy_name]["leads"]["2"]["all"]["pressure"]["rho"] = 0.15
        self.assertEqual(len(script.check_identity(data["series"][original], data["series"][copy_name])), 1)

    def test_compare_refuses_a_screen_that_fails_the_identity(self):
        data = screen()
        data["series"][script.PAIRS[1][1]]["leads"]["3"]["all"]["level"]["rho"] = 0.9
        with self.assertRaises(ValueError):
            script.compare(data)


class OtherSeriesTests(unittest.TestCase):
    def test_a_screen_with_the_copies_leaves_every_other_series_alone(self):
        data = screen()
        base = copy.deepcopy(data)
        for _o, copy_name in script.PAIRS:
            del base["series"][copy_name]
        self.assertEqual(script.check_others(base, data), [])
        script.compare(data, base)

    def test_a_series_that_moved_is_named(self):
        data = screen()
        base = copy.deepcopy(data)
        for _o, copy_name in script.PAIRS:
            del base["series"][copy_name]
        data["series"]["other"]["leads"]["1"]["all"]["pressure"]["rho"] = 0.0
        with self.assertRaises(ValueError) as caught:
            script.compare(data, base)
        self.assertIn("other differs", str(caught.exception))


class TableTests(unittest.TestCase):
    def test_ranks_count_the_screens_own_series(self):
        data = screen()
        result = script.compare(data)
        pair = result["pairs"][script.PAIRS[0][0]]
        # strongest |rho| over the leads: originals 0.50, copies 0.51, other 0.35
        self.assertEqual(pair["rank_two_day"][1], pair["rank_one_day"][1])
        self.assertEqual(pair["rank_two_day"][1], 4)  # three originals and 'other'
        self.assertLessEqual(pair["rank_one_day"][0], 3)

    def test_markdown_sets_the_two_readings_side_by_side(self):
        text = script.markdown(script.compare(screen()))
        for original, copy_name in script.PAIRS:
            self.assertIn(f"`{original}` | declared (2 days)", text)
            self.assertIn(f"`{copy_name}` | stated (1 day)", text)
        self.assertIn("panel `abababababab…`", text)


def family(name, mean, p_improve, p_worse=0.9):
    """Every comparison of a reading of the group on the OFR window, all with one mean and p."""

    entries = {}
    for day_set in (script.POOLED, script.ONSET):
        for tau in script.THRESHOLDS:
            for h in script.HORIZONS:
                for bench in script.BENCHMARKS:
                    key = script.comparison_key(name, "brier", day_set, tau, h, bench)
                    entries[key] = {"mean": mean, "p_improve": p_improve, "p_worse": p_worse,
                                    "regimes": {"2018-19": None, "2025-26": mean}}
    entries[script.comparison_key(name, "crps")] = {"mean": mean, "p_improve": p_improve, "p_worse": p_worse}
    return entries


class NarrowFamilyTests(unittest.TestCase):
    def test_holm_runs_over_the_readings_own_comparisons(self):
        name = script.GROUP + "@1d"
        entries = {**family(name, 0.001, 0.0001), **family(script.GROUP, -0.001, 0.5)}
        verdict = script.narrow_family(entries, name)
        own = [e for k, e in entries.items() if k.startswith(name + "|")]
        self.assertEqual(len(own), 41)
        self.assertTrue(all(e["holm_improve"] for e in own))
        self.assertFalse(any("holm_improve" in e for k, e in entries.items() if k.startswith(script.GROUP + "|")))
        # the OFR window holds no 2018-19 episode: never a win (#187, item 4), at best promising
        self.assertEqual(verdict["outcome"], "promising")
        self.assertIsNotNone(verdict["capped"])

    def test_a_reading_that_never_improves_is_no_effect(self):
        entries = family(script.GROUP, -0.001, 0.5)
        self.assertEqual(script.narrow_family(entries, script.GROUP)["outcome"], "no effect")


if __name__ == "__main__":
    unittest.main()
