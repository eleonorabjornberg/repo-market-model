"""`scripts/b2_star_1420.py` (#1420; H5, registration design, benchmarks, development tier): B2* and B2 scored against the candidate (s3c-ann-net)
at the 18:00 decision instant on both windows of #1255.

Written first, against the declaration. What these tests pin: that the declaration names what the script has (seed, models, references, last day, the
cleared register row, the `variants` block of #803); the test plan (the candidate against B2* and the benchmarks, B2* against B2 only); the refusal of
a frame day without a B2* forecast; the count of fallback cells on hand cases; the page (B2*'s definition, the marked question with numbered options and a
default); and a small run of `score` and `page` end to end on the fixture panel.

Recorded mutation (the check of this study, #1420): in `b2_star_1420.add_b2_star`, the guard `require_forecasts(frame, star)` was deleted and a frame day
dropped from `star`; `WalkTests.test_a_scored_day_without_a_forecast_is_refused` exercises the guard itself: with the body of `m1360.require_forecasts`
changed from `if day not in forecasts:` to `if False:` it failed with `AssertionError` (`ValueError` not raised); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("b2_star_1420", ROOT / "scripts" / "b2_star_1420.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["b2_star_1420"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

DECLARATION = json.loads((ROOT / "metadata" / "b2_star_1420.json").read_text(encoding="utf-8"))


class DeclarationTests(unittest.TestCase):

    def test_the_script_has_what_the_declaration_names(self):
        self.assertEqual(script.SEED, DECLARATION["seed"])
        self.assertEqual(list(script.MODELS), DECLARATION["models"])
        self.assertEqual(script.LAST_DAY, date.fromisoformat(DECLARATION["limits"]["last_day"]))
        self.assertEqual([r["name"] for r in DECLARATION["references"]], [script.ANNNET, "B1", script.B1P, "B2"])

    def test_the_declaration_has_a_variants_block_with_one_new_arm(self):
        self.assertEqual(set(DECLARATION["variants"]), {"sc_s3c_ann_net", "B1", "B1_prime", "B2", "B2_star"})

    def test_the_cleared_register_row_exists_and_is_direct(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "b2_star_1420.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/b2_star_1420.json")
        self.assertEqual(row["script"], "scripts/b2_star_1420.py")
        self.assertEqual(row["pairing"], "direct")

    def test_there_is_no_amendment_that_changes_a_figure_after_a_score(self):
        for amendment in DECLARATION["amendments"]:
            self.assertFalse(amendment.get("changes_a_figure", False))


class PlanTests(unittest.TestCase):

    def test_the_candidate_is_tested_against_b2_star_and_the_benchmarks(self):
        self.assertEqual(script.plan(script.ANNNET, "regime"), [script.B2STAR, "B1", script.B1P, "B2"])

    def test_b2_star_is_tested_against_b2_only(self):
        self.assertEqual(script.plan(script.B2STAR, "pooled"), ["B2"])

    def test_a_benchmark_is_never_a_candidate(self):
        self.assertEqual(script.plan("B1", "pooled"), [])
        self.assertEqual(script.plan("B2", "pooled"), [])


class WalkTests(unittest.TestCase):

    def test_a_scored_day_without_a_forecast_is_refused(self):
        frame = SimpleNamespace(days=[date(2022, 1, 3), date(2022, 1, 4)])
        with self.assertRaises(ValueError):
            script.require_forecasts(frame, {date(2022, 1, 3): {}})

    def test_every_scored_day_with_a_forecast_is_accepted(self):
        frame = SimpleNamespace(days=[date(2022, 1, 3)])
        script.require_forecasts(frame, {date(2022, 1, 3): {}, date(2022, 1, 4): {}})


class FallbackTests(unittest.TestCase):

    def test_cells_on_a_fallback_pool_are_those_not_on_the_types_own_pool(self):
        entry = {"cells": 10, "pools": {"year_end": 3, "quarter_end_turn": 7}}
        self.assertEqual(script.fell_back("year_end", entry), 7)
        self.assertEqual(script.fell_back("turn", {"cells": 4, "pools": {"turn": 4}}), 0)
        self.assertEqual(script.fell_back("tax_date", {"cells": 4, "pools": {"all_days": 4}}), 4)


class PageTests(unittest.TestCase):

    def test_the_question_has_numbered_options_and_a_default(self):
        text = "\n".join(script.question())
        for number in ("1.", "2.", "3."):
            self.assertIn(number, text)
        self.assertIn("default", text)

    def test_the_definition_names_the_pools_lookback_minimum_and_fallback(self):
        text = "\n".join(script.definition()).lower()
        for needle in ("pools", "two calendar years", "minimum pool", "fallback", "no shrinkage", "not searched"):
            self.assertIn(needle, text)


class EndToEndTests(unittest.TestCase):
    """A small run of `score` and `page` on the fixture panel, on the 2026 window from late July; no figure of it is read."""

    def test_score_and_page_run_end_to_end(self):
        import panel_cache

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "result.json"
            args = SimpleNamespace(panel=panel_cache.published_build()["path"], output=str(out), draws=40, reps=40, workers=2,
                                   first=date(2026, 7, 20), windows=("2026",))
            self.assertEqual(script.score(args), 0)
            result = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(result["models"], list(script.MODELS))
            self.assertEqual(result["label"], "development, not a verdict")
            for window in result["windows"]:
                w = result["windows"][window]
                pooled = w["groups"]["pooled"]["all decision days"]
                for metric in script.TESTED:
                    self.assertIn(script.B2STAR, pooled[metric]["means"])
                    self.assertIn(script.B2STAR, pooled[metric]["vs"][script.ANNNET])
                self.assertEqual(sorted(w["fallback"]), ["B2", script.B2STAR])
            page = Path(tmp) / "page.md"
            self.assertEqual(script.page(SimpleNamespace(score=str(out), output=str(page))), 0)
            text = page.read_text(encoding="utf-8")
            self.assertIn("Question for Eleonora", text)
            self.assertIn("development data, not a verdict", text.lower().replace("**", ""))


class TrackedPageTests(unittest.TestCase):
    """The tracked result page is what the script renders from the tracked record, and the record is a full run of the declared study."""

    record_path = ROOT / "docs" / "research" / "b2-star-1420" / "result.json"
    page_path = ROOT / "docs" / "research" / "b2-star-1420-result.md"

    def test_the_page_is_what_the_script_renders_from_the_record(self):
        record = json.loads(self.record_path.read_text(encoding="utf-8"))
        self.assertEqual(self.page_path.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_a_full_run_of_the_declared_study(self):
        record = json.loads(self.record_path.read_text(encoding="utf-8"))
        self.assertEqual(record["models"], DECLARATION["models"])
        self.assertEqual(record["seed"], DECLARATION["seed"])
        self.assertEqual(record["draws"], sp.DRAWS)
        self.assertIsNone(record["subset_from"])
        self.assertEqual(sorted(record["windows"]), sorted(script.WINDOWS))
        self.assertEqual(record["label"], "development, not a verdict")
        self.assertEqual(record["b2_star"], {"years": 2, "pool_min": 10})
        for window, result in record["windows"].items():
            self.assertEqual(result["against_1356"]["difference"], 0.0, window)


if __name__ == "__main__":
    unittest.main()
