"""`scripts/b4_quantile_regression_1360.py` (#1360; H5, registration design step 4 to 5, development tier): B4, the plain quantile-regression
benchmark, scored against the candidate (s3c-ann-net) and B1, B1' and B2 at the 18:00 decision instant, on both windows of #1255.

Written first, against the declaration. The fit and its guards are in `test_b4_quantile_regression_1360`. What these tests pin: that the declaration
names what the script has (seed, models, references, last day, the cleared register row); the test plan (B4 against the benchmarks, the candidate
against B4 and the benchmarks); the refusal of a walk that lacks a scored day; the refusal of references that differ from #1321's record; the
summary of the fitted coefficients on a hand case; the page (B4's definition, the marked question with numbered options and a default that changes
no claim); and a small run of `score` and `page` end to end on the fixture panel.

Recorded mutation (the check of this study, #1360): in `b4_quantile_regression_1360.require_forecasts`, the comparison
`if day not in forecasts:` was changed to `if False:`. `WalkTests.test_a_scored_day_without_a_forecast_is_refused` then failed with
`AssertionError` (`ValueError` not raised); restored, it passes.
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

from repo_model import b4_quantile_regression as b4
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("b4_quantile_regression_1360", ROOT / "scripts" / "b4_quantile_regression_1360.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["b4_quantile_regression_1360"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

DECLARATION = json.loads((ROOT / "metadata" / "b4_quantile_regression_1360.json").read_text(encoding="utf-8"))


class DeclarationTests(unittest.TestCase):

    def test_the_script_has_what_the_declaration_names(self):
        self.assertEqual(script.SEED, DECLARATION["seed"])
        self.assertEqual(list(script.MODELS), DECLARATION["models"])
        self.assertEqual(script.LAST_DAY, date.fromisoformat(DECLARATION["limits"]["last_day"]))
        self.assertEqual([r["name"] for r in DECLARATION["references"]], [script.ANNNET, "B1", script.B1P, "B2"])

    def test_the_cleared_register_row_exists_and_is_direct(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "b4_quantile_regression_1360.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/b4_quantile_regression_1360.json")
        self.assertEqual(row["script"], "scripts/b4_quantile_regression_1360.py")
        self.assertEqual(row["pairing"], "direct")

    def test_there_is_no_open_amendment_that_changes_a_figure_after_a_score(self):
        for amendment in DECLARATION["amendments"]:
            self.assertFalse(amendment["changes_a_figure"])


class PlanTests(unittest.TestCase):

    def test_b4_is_tested_against_the_three_benchmarks(self):
        self.assertEqual(script.plan(script.B4, "pooled"), ["B1", script.B1P, "B2"])

    def test_the_candidate_is_tested_against_b4_and_the_benchmarks(self):
        self.assertEqual(script.plan(script.ANNNET, "regime"), [script.B4, "B1", script.B1P, "B2"])

    def test_a_benchmark_is_never_a_candidate(self):
        self.assertEqual(script.plan("B1", "pooled"), [])


class WalkTests(unittest.TestCase):

    def test_a_scored_day_without_a_forecast_is_refused(self):
        frame = SimpleNamespace(days=[date(2022, 1, 3), date(2022, 1, 4)])
        with self.assertRaises(ValueError):
            script.require_forecasts(frame, {date(2022, 1, 3): {}})

    def test_every_scored_day_with_a_forecast_is_accepted(self):
        frame = SimpleNamespace(days=[date(2022, 1, 3)])
        script.require_forecasts(frame, {date(2022, 1, 3): {}, date(2022, 1, 4): {}})


class ReferenceTests(unittest.TestCase):

    def window(self, value):
        return {"groups": {"pooled": {"all decision days": {m: {"means": {x: value for x in script.REFERENCES}} for m in script.TESTED}}}}

    def test_references_equal_to_1321_are_accepted(self):
        got = script.compare_references({"development": self.window(1.0)}, {"development": self.window(1.0)})
        self.assertEqual(got["development"]["difference"], 0.0)

    def test_references_that_differ_from_1321_are_refused(self):
        with self.assertRaises(ValueError):
            script.compare_references({"development": self.window(1.0)}, {"development": self.window(1.0 + 1e-6)})


class RecordOf1356Tests(unittest.TestCase):
    """The tracked record the references are checked against (a full run stops at the first window if they differ), read as the script reads it."""

    record = json.loads(script.RECORD_1356.read_text(encoding="utf-8"))["windows"]

    def test_the_record_holds_every_reference_on_every_tested_metric(self):
        for window in script.WINDOWS:
            pooled = self.record[window]["groups"]["pooled"]["all decision days"]
            for metric in script.TESTED:
                for model in script.REFERENCES:
                    self.assertIn(model, pooled[metric]["means"], f"{window}/{metric}")

    def test_references_scored_alike_are_accepted_against_the_record(self):
        for window in script.WINDOWS:
            self.assertEqual(script.compare_references({window: self.record[window]}, self.record)[window]["difference"], 0.0)

    def test_the_reference_check_reads_the_pooled_means_of_the_frames_cells(self):
        from datetime import timedelta

        days = [date(2022, 1, 3) + timedelta(days=i) for i in range(3)]
        frame = SimpleNamespace(days=days)
        window = "development"
        pooled = self.record[window]["groups"]["pooled"]["all decision days"]
        cells = {m: {metric: {(d, h): pooled[metric]["means"][m] for d in days for h in sp.HORIZONS} for metric in script.TESTED}
                 for m in script.REFERENCES}
        args = SimpleNamespace(first=None, windows=None)
        out = script.reference_check(window, frame, cells, args)
        self.assertLess(out["difference"], 1e-9)
        cells["B1"]["grid_crps"] = {key: value + 1e-6 for key, value in cells["B1"]["grid_crps"].items()}
        with self.assertRaises(ValueError):
            script.reference_check(window, frame, cells, args)

    def test_a_subset_run_is_not_checked(self):
        self.assertEqual(script.reference_check("development", SimpleNamespace(days=[]), {}, SimpleNamespace(first=date(2026, 7, 20), windows=None)), {})


class SummaryTests(unittest.TestCase):

    def estimate(self, level, slope):
        return b4.Estimate(
            terms=("quarter_end",), coefficients={0.5: (level, 0.1, 0.2, slope), 0.95: (level + 1, 0.1, 0.2, slope * 2)},
            pairs=100, unknown_reserves=0, flagged={"quarter_end": 9}, iterations={0.5: 4, 0.95: b4.MAX_ITERATIONS}, levels=(0.5, 0.95),
        )

    def test_the_summary_averages_the_refits_and_counts_the_capped_fits(self):
        estimates = {date(2022, 1, 3): {1: self.estimate(2.0, 4.0)}, date(2022, 2, 3): {1: self.estimate(4.0, 6.0)}}
        out = script.fit_summary(estimates, levels=(0.5, 0.95), leads=(1,))
        self.assertAlmostEqual(out["1"]["0.5"]["intercept"]["mean"], 3.0)
        self.assertAlmostEqual(out["1"]["0.5"]["quarter_end"]["mean"], 5.0)
        self.assertAlmostEqual(out["1"]["0.95"]["quarter_end"]["mean"], 10.0)
        self.assertEqual(out["1"]["0.5"]["quarter_end"]["share_of_refits"], 1.0)
        self.assertEqual(out["1"]["0.5"]["month_end"]["share_of_refits"], 0.0)
        self.assertEqual(out["capped_fits"], 2)
        self.assertEqual(out["fits"], 4)


class PageTests(unittest.TestCase):

    def test_the_question_has_numbered_options_and_a_default_that_changes_no_claim(self):
        text = "\n".join(script.question())
        for number in ("1.", "2.", "3."):
            self.assertIn(number, text)
        self.assertIn("default", text)
        self.assertIn("reported beside", text)
        self.assertIn("B1 stays", text)

    def test_the_definition_names_what_b4_reads(self):
        text = "\n".join(script.definition()).lower()
        for needle in ("reserve_balances", "direct", "expanding", "ridge", "target day", "auction-announcement dating"):
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
            self.assertEqual(list(result["windows"]), ["2026"])
            for window in result["windows"]:
                pooled = result["windows"][window]["groups"]["pooled"]["all decision days"]
                for metric in script.TESTED:
                    self.assertIn(script.B4, pooled[metric]["means"])
                    self.assertIn(script.B4, pooled[metric]["vs"][script.ANNNET])
            page = Path(tmp) / "page.md"
            self.assertEqual(script.page(SimpleNamespace(score=str(out), output=str(page))), 0)
            text = page.read_text(encoding="utf-8")
            self.assertIn("Question for Eleonora", text)
            self.assertIn("development data, not a verdict", text.lower().replace("**", ""))


class TrackedPageTests(unittest.TestCase):
    """The tracked result page is what the script renders from the tracked record, and the record is a full run of the declared study."""

    record_path = ROOT / "docs" / "research" / "b4-quantile-regression-1360" / "result.json"
    page_path = ROOT / "docs" / "research" / "b4-quantile-regression-1360-result.md"

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
        self.assertEqual(record["ridge"], DECLARATION["b4"]["estimator"]["ridge"])
        for window, result in record["windows"].items():
            self.assertEqual(result["against_1356"]["difference"], 0.0, window)
            self.assertEqual(result["notes"]["refits_b4"], result["notes"]["refits_candidate"], window)


if __name__ == "__main__":
    unittest.main()
