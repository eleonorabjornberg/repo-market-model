"""B2*-cap proper, and the re-run of the capped-baselines study with it (#1440, the finding of #1434; H5, registration design, benchmarks, step 3).

#1422 scored "B2*-cap" with plain B2 standing in, because B2* (#1420) was thought not to be on main. `protocol_benchmarks.b2_star_capped_forecast` is
`b2_star_forecast` clipped at the candidate's Standing Repo Facility line (`capped_forecast`), the rule of B1'*-cap. The stand-in `b2_capped_forecast`
(B2 clipped) is gone: no published page needs it to reproduce, since `scripts/capped_baselines_1421.py` builds its B2-cap from `b2_forecast` and
`capped_forecast` itself.

What these tests pin: B2*-cap clips `b2_star_forecast`, not `b2_forecast` (and the two differ at the days tested, so the test can tell them apart);
before full allotment B2*-cap is B2* itself; the cap only lowers a quantile; the study script builds its B2* column from `b2_star_forecast`; its
reproduction check refuses a B2* mean that is not #1420's.

Written before the code: `AttributeError: module 'repo_model.protocol_benchmarks' has no attribute 'b2_star_capped_forecast'` and `FileNotFoundError` for
the script.

Recorded mutation (a wrong-benchmark guard, not a leakage guard): in `protocol_benchmarks.b2_star_capped_forecast`, `b2_star_forecast(` was replaced with
`b2_forecast(`, which is the stand-in of #1422. `CapTests.test_b2_star_cap_is_b2_star_clipped_not_b2_clipped` failed with `AssertionError` (the capped
vectors differ from `capped_forecast(b2_star_forecast(...))`); restored, it passes. The same swap in the script's `baseline_forecasts` failed
`ScriptTests.test_the_script_builds_b2_star_from_b2_star_forecast` with `AssertionError`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, time
from pathlib import Path

import test_protocol_benchmarks as tpb
from repo_model import policy_events as pe
from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("capped_baselines_b2star_1434_script", ROOT / "scripts" / "capped_baselines_b2star_1434.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

REGISTER = pe.load_register()
DECISION = time(18, 0)


def setup():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=DECISION, splits=tpb.SPLITS)


class CapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()
        cls.late = len(cls.panel) - 12  # targets in 2026, at full allotment
        cls.early = next(i for i, r in enumerate(cls.panel) if r.date >= date(2024, 6, 3))

    def test_b2_star_differs_from_b2_where_it_is_tested(self):
        self.assertNotEqual(pb.b2_star_forecast(self.panel, self.late, **self.settings), pb.b2_forecast(self.panel, self.late, **self.settings))

    def test_b2_star_cap_is_b2_star_clipped_not_b2_clipped(self):
        for t in (self.early, self.late - 30, self.late):
            star = pb.b2_star_forecast(self.panel, t, **self.settings)
            want = pb.capped_forecast(star, self.panel, t, register=REGISTER, decision_time=DECISION)
            got = pb.b2_star_capped_forecast(self.panel, t, register=REGISTER, **self.settings)
            self.assertEqual(got, want)
        t = self.late
        stand_in = pb.capped_forecast(pb.b2_forecast(self.panel, t, **self.settings), self.panel, t, register=REGISTER, decision_time=DECISION)
        self.assertNotEqual(pb.b2_star_capped_forecast(self.panel, t, register=REGISTER, **self.settings), stand_in)

    def test_before_full_allotment_b2_star_cap_is_b2_star(self):
        raw = pb.b2_star_forecast(self.panel, self.early, **self.settings)
        self.assertEqual(pb.b2_star_capped_forecast(self.panel, self.early, register=REGISTER, **self.settings), raw)

    def test_the_cap_only_lowers_a_quantile_and_keeps_the_order(self):
        raw = pb.b2_star_forecast(self.panel, self.late, **self.settings)
        got = pb.b2_star_capped_forecast(self.panel, self.late, register=REGISTER, **self.settings)
        for h in sp.HORIZONS:
            self.assertTrue(all(c <= r for c, r in zip(got[h], raw[h])))
            self.assertEqual(got[h], sorted(got[h]))

    def test_the_stand_in_is_gone(self):
        self.assertFalse(hasattr(pb, "b2_capped_forecast"))


class ScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()
        cls.late = len(cls.panel) - 12

    def test_the_models_are_the_candidate_b1_prime_star_and_b2_star_with_their_caps(self):
        self.assertEqual(set(script.MODELS), {"candidate", "B1p_star", "B1p_star_cap", "B2star", "B2star_cap"})
        self.assertEqual(script.MODELS["B2star_cap"], ("B2star", True))
        self.assertEqual(script.MODELS["B2star"], ("B2star", False))
        self.assertEqual(script.BASES, ("B1p_star", "B2star"))
        self.assertIn(("cap_vs:B2star", "B2star", "B2star_cap"), script.comparisons())
        self.assertIn(("cand_vs:B2star_cap", "B2star_cap", "candidate"), script.comparisons())

    def test_the_script_builds_b2_star_from_b2_star_forecast(self):
        got = script.baseline_forecasts(self.panel, self.late, self.settings)
        self.assertEqual(got["B2star"], pb.b2_star_forecast(self.panel, self.late, **self.settings))
        self.assertNotEqual(got["B2star"], pb.b2_forecast(self.panel, self.late, **self.settings))
        self.assertEqual(got["B1p_star"], pb.b1_calendar_anchor_forecast(self.panel, self.late, **self.settings))

    def test_the_reproduction_check_reads_1420_for_b2_star_and_refuses_a_different_mean(self):
        theirs = json.loads((ROOT / "docs/research/b2-star-1420/result.json").read_text(encoding="utf-8"))
        for window in script.WINDOWS:
            want = theirs["windows"][window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]["B2_star"]
            old = json.loads((ROOT / "docs/research/capped-baselines-1421/result.json").read_text(encoding="utf-8"))["windows"][window]["groups"]["pooled"]["all cells"]
            means = {"candidate": old["metrics"]["grid_crps"]["means"]["candidate"], "B1p_star": old["metrics"]["grid_crps"]["means"]["B1p_star"],
                     "B1p_star_cap": old["metrics"]["grid_crps"]["means"]["B1p_star_cap"], "B2star": want, "B2star_cap": want}
            self.assertEqual(script.reproduce(window, means)["B2star"]["there"], want)
            means["B2star"] = want + 1e-6
            with self.assertRaises(ValueError):
                script.reproduce(window, means)

    def test_the_declaration_names_what_it_supersedes_and_keeps_the_seed(self):
        d = json.loads((ROOT / "metadata/capped_baselines_b2star_1434.json").read_text(encoding="utf-8"))
        self.assertEqual(d["supersedes"]["page"], "docs/research/capped-baselines-1421-result.md")
        self.assertEqual(d["seed"], script.SEED)
        self.assertTrue((ROOT / d["supersedes"]["page"]).is_file())


if __name__ == "__main__":
    unittest.main()
