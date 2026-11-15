"""Amendment 4 reads Kupiec and independence at spacing h + 1 (#1527, H5, step M5).

Her rulings of 8 November 2026 (#1525, "spacing") and 10 November 2026 (#1545, "both"): a forecast for D + h reads data only to the
panel day D - 1, so two forecasts kept h days apart share one unknown innovation and their hits are dependent; forecasts h + 1 days
apart do not. `scoring_protocol.coverage_cells(method="spaced")` therefore reads both tests on every (h + 1)-th decision day, and
`method="spaced_hac"` reads Kupiec on every day with a Newey-West variance at lag h (lead-h errors overlap for h days) and
independence on every (h + 1)-th day. `thinned` and `hac` (the design as set by #1522, spacing h, lag h - 1) stay as reported
designs: #1512, #1516 and #1528 reproduce on them. The requirement reads `COVERAGE_REQUIREMENT_METHOD`, which the record names.

The control is the world of #1525 in miniature: a Gaussian AR(1) whose forecast for D + h uses the series to D - 1 only, so it is
calibrated by construction and its hits h days apart are dependent.

**Recorded mutation (spacing).** In `coverage_cells`, `spacing = h + 1 if method in ("spaced", "spaced_hac") else h` -> `spacing = h` fails
`SpacingTests.test_spaced_keeps_every_h_plus_1th_decision_day` with `AssertionError` (`300 != 150 : lead 1`) and
`ControlTests.test_the_calibrated_control_passes_at_h_plus_1` with `CoverageRequirementFailed` (an error in each of seeds 1 to 3).
**Recorded mutation (HAC lag).** In `coverage_cells`, `lag = h if method == "spaced_hac" else h - 1` -> `lag = h - 1` fails `SpacingTests.test_spaced_hac_reads_lag_h` with `AssertionError`.
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from statistics import NormalDist
from unittest import mock

from repo_model import scoring_protocol as sp

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("coverage_spacing_1527_script", REPO / "scripts" / "coverage_spacing_1527.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)
sys.path.insert(0, str(REPO / "tests"))
import test_coverage_report_1512 as t1512  # noqa: E402

RECORD = Path(__file__).resolve().parents[1] / "docs" / "decisions" / "scoring-protocol.md"
HEADING = "## Draft amendment 4: passing the coverage tests is a registration requirement (#1130)"


def business_days(count, start=date(2005, 1, 3)):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def ar1_world(n, seed, phi=0.9):
    """A calibrated forecaster with the one-day information lag: the lead-h forecast made on decision index i reads y[<= i - 1]."""

    calendar = business_days(n + 8)
    rng = random.Random(seed)
    y, prev = [], 0.0
    for _ in range(len(calendar)):
        prev = phi * prev + rng.gauss(0.0, 1.0)
        y.append(prev)
    z = [NormalDist().inv_cdf(level) for level in sp.GRID]
    forecasts = {}
    for i in range(1, n):
        forecasts[calendar[i]] = {}
        for h in sp.HORIZONS:
            mean = phi ** (h + 1) * y[i - 1]
            sd = (sum(phi ** (2 * j) for j in range(h + 1))) ** 0.5
            forecasts[calendar[i]][h] = [mean + sd * zz for zz in z]
    outcomes = {day: y[k] for k, day in enumerate(calendar)}
    labels = {day: "all" for day in forecasts}
    return forecasts, outcomes, calendar, labels


def flat_world(n, outcome):
    calendar = business_days(n + 6)
    q = [(level - 0.5) * 10.0 for level in sp.GRID]
    forecasts = {day: {h: list(q) for h in sp.HORIZONS} for day in calendar[:n]}
    return forecasts, {day: outcome(day) for day in calendar}, calendar, {day: "all" for day in calendar[:n]}


def cell(cells, **keys):
    found = [c for c in cells if all(getattr(c, k) == v for k, v in keys.items())]
    assert len(found) == 1, (keys, found)
    return found[0]


class SpacingTests(unittest.TestCase):
    def test_spaced_keeps_every_h_plus_1th_decision_day(self):
        forecasts, outcomes, calendar, labels = flat_world(300, lambda day: 0.0)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="spaced")
        for h, expected in ((1, 150), (2, 100), (3, 75), (4, 60), (5, 50)):
            self.assertEqual(cell(cells, level=0.05, lead=h, regime="all", rule="strict").n, expected, msg=f"lead {h}")
        self.assertEqual({c.method for c in cells}, {"spaced"})

    def test_thinned_still_keeps_every_hth_day(self):
        forecasts, outcomes, calendar, labels = flat_world(300, lambda day: 0.0)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        self.assertEqual(cell(cells, level=0.05, lead=3, regime="all", rule="strict").n, 100)

    def test_spaced_hac_reads_lag_h(self):
        runs = {}

        def outcome(day):
            block = (day - date(2005, 1, 3)).days // 7
            runs.setdefault(block, random.Random(block).random() < 0.05)
            return 4.9 if runs[block] else 0.0

        forecasts, outcomes, calendar, labels = flat_world(500, outcome)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="spaced_hac")
        for h in (1, 3, 5):
            got = cell(cells, level=0.95, lead=h, regime="all", rule="strict")
            hits = [int(outcomes[calendar[i + h]] > 4.5) for i in range(500)]
            self.assertEqual(got.n, 500)
            self.assertAlmostEqual(got.kupiec_p, sp._hac_kupiec_p(hits, 0.05, h), places=12, msg=f"lead {h}")
        # independence is on every (h + 1)-th day, as for "spaced"
        spaced = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="spaced")
        for h in (2, 4):
            self.assertEqual(
                cell(cells, level=0.95, lead=h, regime="all", rule="strict").independence_p,
                cell(spaced, level=0.95, lead=h, regime="all", rule="strict").independence_p,
            )

    def test_the_methods_are_the_four(self):
        self.assertEqual(set(sp.COVERAGE_METHODS), {"thinned", "hac", "spaced", "spaced_hac"})
        forecasts, outcomes, calendar, labels = flat_world(30, lambda day: 0.0)
        with self.assertRaises(sp.ProtocolError):
            sp.coverage_cells(forecasts, outcomes, calendar, labels, method="spacing")


class ControlTests(unittest.TestCase):
    """The calibrated control: spacing h fails it, spacing h + 1 passes it."""

    def cells(self, method, seed):
        forecasts, outcomes, calendar, labels = ar1_world(1500, seed)
        return sp.coverage_cells(forecasts, outcomes, calendar, labels, method=method)

    def test_a_spacing_of_h_fails_the_calibrated_control(self):
        failed = 0
        for seed in (1, 2, 3, 4):
            try:
                sp.enforce_coverage_requirement(self.cells("thinned", seed), alpha=0.05, family="holm", rule="strict")
            except sp.CoverageRequirementFailed as raised:
                failed += 1
                self.assertIn("independence", str(raised))
        self.assertGreaterEqual(failed, 3)

    def test_the_calibrated_control_passes_at_h_plus_1(self):
        # Fixed seeds: the design's size on this world is about 4% (8 rejections of 200 paths, seeds 100-299), so a given seed
        # may reject; these three do not.
        for seed in (1, 2, 3):
            with self.subTest(seed=seed):
                self.assertEqual(
                    sp.enforce_coverage_requirement(self.cells("spaced", seed), alpha=0.05, family="holm", rule="strict"), []
                )

    def test_the_flag_is_respected(self):
        cells = self.cells("thinned", 1)
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", False):
            self.assertEqual(sp.enforce_coverage_requirement(cells, alpha=0.05, family="holm", rule="strict"), [])
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
            with self.assertRaises(sp.CoverageRequirementFailed):
                sp.enforce_coverage_requirement(cells, alpha=0.05, family="holm", rule="strict")

    def test_a_too_narrow_forecast_still_fails_at_h_plus_1(self):
        forecasts, outcomes, calendar, labels = ar1_world(1500, 1)
        narrow = {d: {h: [0.5 * q for q in qs] for h, qs in leads.items()} for d, leads in forecasts.items()}
        cells = sp.coverage_cells(narrow, outcomes, calendar, labels, method="spaced")
        with self.assertRaises(sp.CoverageRequirementFailed):
            sp.enforce_coverage_requirement(cells, alpha=0.05, family="holm", rule="strict")


class StudyTests(unittest.TestCase):
    """`scripts/coverage_spacing_1527.py`: the three designs on one walk, the module's METHOD restored, the page from the result."""

    def test_the_report_runs_all_three_designs_and_restores_the_method(self):
        window = script.m12.load_window_doc(t1512.doc(120))
        before = script.m12.METHOD
        by = script.report_all(window)
        self.assertEqual(script.m12.METHOD, before)
        self.assertEqual(list(by), ["spaced", "thinned", "spaced_hac"])
        self.assertEqual({m: by[m]["method"] for m in by}, {m: m for m in by})
        # the spaced design keeps fewer days than the thinned one at every lead
        key = lambda rep, h: next(c["n"] for c in rep["cells"] if c["lead"] == h and c["rule"] == "strict" and c["level"] == 0.05 and c["regime"] == "calm")
        for h in (1, 2, 3):
            self.assertLess(key(by["spaced"], h), key(by["thinned"], h))

    def test_the_page_is_made_from_the_result_only(self):
        window = script.m12.load_window_doc(t1512.doc(120))
        by = script.report_all(window)
        result = {
            "alpha": 0.05, "family": "holm", "rules": list(script.m12.RULES), "regimes": by["spaced"]["regimes"], "decision_days": 120,
            "last_target": "x", "ties": {"0.05": 0}, "methods": by, "panel_sha256": "x",
            "reproduction": {"models": {script.CANDIDATE: {"ok": True}}},
        }
        page = script.render(json.loads(json.dumps(result)))
        self.assertIn("spacing h + 1", page)
        self.assertIn("Rejections under `spaced`", page)
        self.assertIn("Rejections under `thinned`", page)

    def test_a_walk_after_the_development_window_is_refused(self):
        late = t1512.doc(60)
        late["window"] = "confirmation"
        with self.assertRaises(ValueError):
            script.m12.load_window_doc(late)


def record_section():
    text = RECORD.read_text(encoding="utf-8")
    start = text.index(HEADING)
    end = text.find("\n## ", start + len(HEADING))
    return " ".join(text[start:end if end != -1 else None].split())


class RecordTests(unittest.TestCase):
    def test_the_requirement_reads_the_method_the_record_names(self):
        self.assertEqual(sp.COVERAGE_REQUIREMENT_METHOD, "spaced")
        section = record_section()
        self.assertIn("`scoring_protocol.COVERAGE_REQUIREMENT_METHOD`, which is `\"spaced\"`", section)
        self.assertIn("spacing h + 1", section)

    def test_the_record_cites_the_simulations_and_the_size(self):
        section = record_section()
        for cited in ("#1525", "#1528", "1.1%", "99.3%", "#1545", "GO #1527"):
            self.assertIn(cited, section)

    def test_the_record_keeps_section_7_and_says_it_is_a_draft_until_merged(self):
        section = record_section()
        self.assertIn("Quarter-end coverage is reported, not gated", section)
        self.assertIn("in force only when she merges", section)


if __name__ == "__main__":
    unittest.main()
