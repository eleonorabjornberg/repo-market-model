"""The study script of #1388: `scripts/b1_anchor_horizon_1388.py` (B1* and B1'* against (s3c-ann-net), development tier).

The forecasts themselves are tested in `test_b1_anchor_horizon_1388`. Pinned here: the declaration agrees with the script (seed, last day, pairs, splits,
metrics, the references), the script refuses to run away from the 18:00 instant, `forecasts_of` returns the module's own forecasts and the lag of each decision
day, the pair tables read the skill of a stored row, the page ends with a marked question with numbered options and a default, and the committed page is the
one `render` makes of the committed record.

Written after the script, which is measurement code (the forecasts it scores were written test-first in `test_b1_anchor_horizon_1388`).

Recorded mutation (the guard this script adds):

* `require_instant`, the test `if instant != INSTANT:` replaced by `if False:`: `GuardTests.test_a_run_away_from_18_00_is_refused` fails with
  `AssertionError` (`SystemExit not raised`); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, time
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("b1_anchor_horizon_1388_script", REPO / "scripts" / "b1_anchor_horizon_1388.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import b1_calendar as b1c  # noqa: E402
from repo_model import protocol_benchmarks as pb  # noqa: E402

import test_protocol_benchmarks as tpb  # noqa: E402

RECORD = REPO / "docs" / "research" / "b1-anchor-horizon-1388" / "result.json"
PAGE = REPO / "docs" / "research" / "b1-anchor-horizon-1388-result.md"


class DeclarationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.declaration = json.loads((REPO / "metadata" / "b1_anchor_horizon_1388.json").read_text(encoding="utf-8"))

    def test_the_declared_pairs_are_the_scripts(self):
        pairs = self.declaration["pairs"]
        declared = [("sc_s3c_ann_net", ref) for ref in pairs["candidate_against"]] + [tuple(p) for p in pairs["correction_against_original"]]
        names = {"B1": "B1", "B1_star": "B1_star", "B1_prime": "B1_prime", "B1_prime_star": "B1_prime_star"}
        self.assertEqual([(a, names.get(b, b)) for a, b in declared], list(script.PAIRS))

    def test_the_declared_seed_last_day_and_splits_are_the_scripts(self):
        self.assertIn(f"seed {script.SEED}", self.declaration["scoring"]["test"])
        self.assertEqual(self.declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(self.declaration["splits"], list(script.SPLITS))

    def test_the_declared_metrics_are_the_scripts(self):
        self.assertEqual(list(self.declaration["metrics"]), list(script.TESTED))

    def test_the_candidate_is_the_named_one(self):
        h5 = json.loads((REPO / "docs" / "research" / "h5-candidate.json").read_text(encoding="utf-8"))
        self.assertEqual(h5["candidate"], script.CANDIDATE)

    def test_the_declaration_has_no_amendments(self):
        self.assertEqual(self.declaration["amendments"], [])


class GuardTests(unittest.TestCase):
    def test_a_run_away_from_18_00_is_refused(self):
        with self.assertRaises(SystemExit):
            script.require_instant(time(16, 0))
        script.require_instant(time(18, 0))


class ForecastTests(unittest.TestCase):
    def test_forecasts_of_are_the_modules_and_the_lag_is_counted(self):
        panel = tpb.published_panel()["rows"]
        days = [panel[i].date for i in (900, 1500)]
        frame = SimpleNamespace(days=days, position={row.date: i for i, row in enumerate(panel)})
        settings = dict(registry=tpb.REGISTRY, decision_time=script.DECISION_TIME)
        star, prime_star, lags = script.forecasts_of(panel, frame, tpb.SPLITS, tpb.REGISTRY)
        self.assertEqual(dict(lags), {1: 2})
        for day, index in zip(days, (900, 1500)):
            self.assertEqual(star[day], pb.b1_anchor_forecast(panel, index, **settings))
            self.assertEqual(prime_star[day], b1c.b1_calendar_anchor_forecast(panel, index, splits=tpb.SPLITS, **settings))


def row(skill, low, high, d=0.1, d_low=0.05, d_high=0.15):
    return {"days": 100, "skill": skill, "skill_interval": [low, high], "difference": d, "difference_interval": [d_low, d_high],
            "benchmark_mean": 2.0, "candidate_mean": 1.9}


class PageTests(unittest.TestCase):
    def test_a_stored_row_is_read_by_its_arm_and_reference(self):
        group = {"grid_crps": {"vs": {"A": {"B": row(0.1, 0.05, 0.15)}}}}
        self.assertIsNone(script.vs(group, "grid_crps", "A", "C"))
        self.assertEqual(script._skill(script.vs(group, "grid_crps", "A", "B")), "+10.0%")
        self.assertEqual(script._skill(None), "n/a")
        self.assertEqual(script._skill({"identical": True}), "n/a")

    def test_the_question_has_numbered_options_and_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("**Question 1.", text)
        self.assertIn("1. ", text)
        self.assertIn("2. ", text)
        self.assertIn("(default", text)
        self.assertIn("B1'* is the mandatory persistence benchmark", text)

    @unittest.skipUnless(RECORD.exists() and PAGE.exists(), "the record and the page are committed with the run")
    def test_the_committed_page_is_the_one_the_record_renders(self):
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.assertEqual(script.render(record), PAGE.read_text(encoding="utf-8"))
        self.assertEqual(record["decision_time"], "18:00")
        self.assertIsNone(record["subset_from"])


if __name__ == "__main__":
    unittest.main()
