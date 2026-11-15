"""`scripts/coverage_test_delay_power_1528.py` (#1528; H5, step M5, development tier): the study around `repo_model.coverage_delay_sim`.

The simulator itself is pinned in `test_coverage_delay_sim.py`. What these tests pin is the study:

- the walk file's calendar, regimes, target-day types and outcomes become a `Structure` and a calibration, and the declaration round-trips to the
  same structure (so the score reads exactly the days the calibration saw);
- a forecaster whose scale is confined to some classes changes only those target days' PITs, and a path's result carries the three rules;
- the aggregation: Wilson intervals on hand cases, the size-adjusted threshold, and the page renders the size table, the power table and the
  read-out from a small run, with the rule names the ruling uses;
- a declaration that is not committed is refused (a rate is never computed before the declaration);
- the window guard: the study reads the development window only, and refuses a decision, target or calendar day after 2025-12-31.

Recorded mutation for the window guard (a new leakage guard): deleting the `sim.require_development(...)` call in `series_from_walk` makes
`WindowGuardTests.test_a_target_day_after_the_last_day_is_refused` fail with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import coverage_delay_sim as sim
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("coverage_test_delay_power_1528", ROOT / "scripts" / "coverage_test_delay_power_1528.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["coverage_test_delay_power_1528"] = script  # the worker pool pickles the script's functions by module name
_spec.loader.exec_module(script)


def business_days(start: date, n: int):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def walk_doc(n_decisions: int = 240, last: date = date(2025, 12, 31), seed: int = 4):
    """A small walk file: calendar ending at `last` + 5 days of 2026 (as the real one runs on), regimes in three runs, day types, spreads."""

    cal_days = business_days(date(2025, 12, 31) - timedelta(days=int(1.45 * (n_decisions + 12))), 10_000)
    cal_days = [d for d in cal_days if d <= last][-(n_decisions + 12):]
    extra = business_days(last + timedelta(days=1), 6)
    calendar = cal_days + extra
    rng = random.Random(seed)
    types = ["quarter_end" if i % 30 == 0 else "bill_settlement" if i % 7 == 0 else "ordinary" for i in range(len(calendar))]
    spread, prev = {}, 0.0
    for d, t in zip(calendar, types):
        prev = 0.6 * prev + rng.gauss(0, 1) * (3.0 if t == "quarter_end" else 1.0)
        spread[d] = prev
    first = 6
    decisions = calendar[first:first + n_decisions]
    regime_of_day = {d.isoformat(): ("a" if i < n_decisions // 3 else "b" if i < 2 * n_decisions // 3 else "c") for i, d in enumerate(decisions)}
    target_days = calendar[first + 1:first + n_decisions + 5]
    regime = {d.isoformat(): regime_of_day.get(d.isoformat(), "c") for d in calendar}
    targets = {d.isoformat(): {"regime": regime[d.isoformat()], "types": [types[calendar.index(d)]], "pressure": "ordinary"} for d in target_days}
    return {
        "window": "development", "panel_sha256": "x" * 64, "calendar": [d.isoformat() for d in calendar],
        "regime_of_day": regime_of_day, "targets": targets, "outcome": {d.isoformat(): spread[d] for d in target_days},
    }


class SeriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = walk_doc()
        cls.series = script.series_from_walk(cls.doc)

    def test_the_calendar_stops_at_the_last_day_and_decisions_have_room_for_five_leads(self):
        s = self.series
        self.assertLessEqual(max(s["calendar"]), script.LAST_DAY)
        self.assertLess(max(s["positions"]) + 5, len(s["calendar"]))
        self.assertEqual(len(s["positions"]), 240)

    def test_classes_follow_the_day_types(self):
        s = self.series
        by_date = {d: c for d, c in zip(s["calendar"], s["classes"])}
        for iso, v in self.doc["targets"].items():
            d = date.fromisoformat(iso)
            if d in by_date:
                self.assertEqual(by_date[d], sim.day_class(v["types"]))

    def test_declaration_round_trips_to_the_same_structure(self):
        decl = script.build_declaration(self.doc)
        st, cal = script.structure_from_declaration(json.loads(json.dumps(decl)))
        s = self.series
        self.assertEqual(st.calendar, s["calendar"])
        self.assertEqual(st.classes, s["classes"])
        self.assertEqual(st.positions, s["positions"])
        self.assertEqual(st.regimes, s["regimes"])
        self.assertEqual(cal.as_dict(), decl["calibration"])
        self.assertEqual(decl["structure"]["regime_runs"], [["a", 80], ["b", 80], ["c", 80]])

    def test_the_declaration_names_every_forecaster_and_rule_before_a_score(self):
        decl = script.build_declaration(self.doc)
        self.assertEqual([f["name"] for f in decl["forecasters"]], list(script.FORECASTERS))
        self.assertEqual(set(decl["rules"]), set(sim.RULES))
        self.assertNotIn("results", decl)


class WindowGuardTests(unittest.TestCase):
    def test_a_target_day_after_the_last_day_is_refused(self):
        doc = walk_doc()
        late = date(2026, 1, 5)
        doc["targets"][late.isoformat()] = {"regime": "c", "types": ["ordinary"], "pressure": "ordinary"}
        doc["outcome"][late.isoformat()] = 0.0
        with self.assertRaises(LookAheadError):
            script.series_from_walk(doc)

    def test_a_decision_day_after_the_last_day_is_refused(self):
        doc = walk_doc()
        doc["regime_of_day"]["2026-01-05"] = "c"
        with self.assertRaises(LookAheadError):
            script.series_from_walk(doc)

    def test_another_window_is_refused(self):
        doc = walk_doc()
        doc["window"] = "2026"
        with self.assertRaises(ValueError):
            script.series_from_walk(doc)

    def test_a_declaration_with_a_late_calendar_day_is_refused(self):
        decl = script.build_declaration(walk_doc())
        decl["structure"]["calendar"][-1] = "2026-02-02"
        with self.assertRaises(LookAheadError):
            script.structure_from_declaration(decl)


class DeclarationCommitTests(unittest.TestCase):
    def test_an_uncommitted_declaration_is_refused(self):
        path = ROOT / "tests" / "_uncommitted_declaration_1528.json"
        path.write_text("{}", encoding="utf-8")
        try:
            with self.assertRaises(SystemExit):
                script.committed_declaration(path)
        finally:
            path.unlink()


class PathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        decl = script.build_declaration(walk_doc())
        cls.st, cls.cal = script.structure_from_declaration(decl)
        cls.fcs = script.forecasters_from_declaration(decl)

    def setUp(self):
        script._STATE.update(cal=self.cal, st=self.st, fcs=self.fcs, seed=7)

    def test_a_class_confined_scale_changes_only_those_target_days(self):
        x, z = sim.simulate_latent(self.cal, len(self.st.calendar), random.Random(1))
        truth = sim.pit_columns(self.cal, x, z, self.st, self.fcs["truth"])
        cols = script.columns_for(self.cal, x, z, self.st, self.fcs["a_qe75"], truth)
        changed = 0
        for h in sim.LEADS:
            for i, p in enumerate(self.st.positions):
                if self.st.classes[p + h] == "quarter_end":
                    changed += cols[h][i] != truth[h][i]
                else:
                    self.assertEqual(cols[h][i], truth[h][i])
        self.assertGreater(changed, 0)
        full = sim.pit_columns(self.cal, x, z, self.st, self.fcs["a_qe75"])
        self.assertEqual(full, cols)

    def test_a_path_carries_every_forecaster_and_rule(self):
        out = script.one_path(0)
        self.assertEqual(set(out), set(script.FORECASTERS))
        for rec in out.values():
            self.assertEqual(set(rec["rules"]), set(sim.RULES))
            self.assertEqual(len(rec["raw"]), 5 * 3 * 4)
        self.assertEqual(out["truth"]["band"][1], 5 * 240)
        self.assertGreater(out["a_qe75"]["band"][1], 0)
        self.assertLess(out["a_qe75"]["band"][1], out["b_70"]["band"][1])

    def test_a_path_is_reproducible_from_its_index(self):
        self.assertEqual(script.one_path(3), script.one_path(3))
        self.assertNotEqual(script.one_path(3)["b_70"]["band"], script.one_path(4)["b_70"]["band"])


class AggregateTests(unittest.TestCase):
    def test_wilson_hand_cases(self):
        lo, hi = script.wilson(50, 1000)
        self.assertAlmostEqual(lo, 0.0381, places=3)
        self.assertAlmostEqual(hi, 0.0654, places=3)
        self.assertEqual(script.wilson(0, 0), [0.0, 1.0])
        self.assertEqual(script.wilson(0, 100)[0], 0.0)

    def test_the_page_renders_from_a_small_run(self):
        decl = script.build_declaration(walk_doc(120))
        st, cal = script.structure_from_declaration(decl)
        script._STATE.update(cal=cal, st=st, fcs=script.forecasters_from_declaration(decl), seed=9)
        results = [script.one_path(p) for p in range(12)]
        agg = script.aggregate(results, st, decl)
        self.assertEqual(agg["paths"], 12)
        t = agg["forecasters"]["truth"]["rules"]["h"]
        self.assertGreaterEqual(t["family_wise"], 0.0)
        self.assertLessEqual(t["size_adjusted"], 0.25)  # about 5% by construction, at most a few of 12 paths
        doc = {
            "calibration": decl["calibration"], "decision_days": len(st.positions), "last_day": decl["last_day"], "regimes": ["a", "b", "c"],
            "regime_days": {"a": 40, "b": 40, "c": 40}, "rules": decl["rules"], "class_days": {c: 1 for c in sim.CLASSES}, "decision_target_pairs": 600,
            "results": agg,
        }
        page = script.render(doc)
        for needle in ("## Size:", "## Power:", "## Read-out", "indep h+1", "Development data, not a verdict", "size-adjusted"):
            self.assertIn(needle, page)
        self.assertNotIn("nan", page.lower())


if __name__ == "__main__":
    unittest.main()
