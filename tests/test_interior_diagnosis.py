"""The interior diagnosis (#247): its measures, its guards, its selection rule and its record.

`scripts/interior_diagnosis.py` walks the published distribution and its
variants (that needs the `ml` extra and a panel, so it is not run here) and
assembles `docs/runs/v1_interior_diagnosis.json`. These tests read no panel:
the measures and the rule run on synthetic inputs, and the record is checked
against the published records and against the rule.

Written before the rule was applied: `SelectionRuleTests` was run red against a
`select_candidate` that returned the lowest-CRPS candidate whatever its
coverage, then green on the rule as declared.

Mutation record (`ObservabilityTests`, interior tracking's label guard): in
`interior_tracking`, `seen = bisect.bisect_right(dates, d["anchor"], 0, j)`
changed to `seen = j`, so every earlier day's label updates the trackers
whatever the anchor; confirmed applied by grep. The test
`test_tracking_reads_no_label_after_the_anchor` then failed with
`AssertionError` (the issued vector moved with a label scored after its
anchor). Restored, green.

Mutation record (`ObservabilityTests`, the residual law's label guard): in
`residual_law`, `seen = bisect.bisect_right(dates, d["anchor"], 0, j)` changed
to `seen = j`; confirmed applied by grep. The test
`test_residual_law_reads_no_label_after_the_anchor` then failed with
`AssertionError`. Restored, green.

Mutation record (`WindowGuardTests`, the assembly's last-day guard): in
`assemble_command`, `if max(d["date"] for d in document["days"]) > LAST_READ.isoformat():`
changed to `if False:`; confirmed applied by grep. The test
`test_a_walk_past_the_opened_tier_is_refused` then failed with `AssertionError`
(the walk "reached the assembly", which raised `KeyError`). Restored, green.
"""

from __future__ import annotations

import importlib.util
import json
import random
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
RECORD = REPO / "docs" / "runs" / "v1_interior_diagnosis.json"
CRPS_RECORD = REPO / "docs" / "runs" / "compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
FINAL = REPO / "docs" / "runs" / "final_test_near_blind.json"


def _script():
    spec = importlib.util.spec_from_file_location(
        "interior_diagnosis", REPO / "scripts" / "interior_diagnosis.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dx = _script()


def _summary(crps, q25=25.0, q50=50.0, q75=75.0, band=90.0):
    return {"crps": crps, "band_90_half_edge": band,
            "coverage_half_tie": {"0.25": q25, "0.5": q50, "0.75": q75}}


def _interval(lower, upper):
    return lambda name, leader: {"interval": {"lower": lower, "upper": upper}}


class SelectionRuleTests(unittest.TestCase):
    def test_the_bar(self):
        self.assertTrue(dx.eligible(_summary(1.0)))
        self.assertTrue(dx.eligible(_summary(1.0, q25=30.0, q75=70.0, band=87.0)))
        self.assertFalse(dx.eligible(_summary(1.0, q50=55.1)))
        self.assertFalse(dx.eligible(_summary(1.0, q25=19.9)))
        self.assertFalse(dx.eligible(_summary(1.0, band=86.9)))
        self.assertFalse(dx.eligible(_summary(1.0, band=93.1)))

    def test_no_eligible_candidate_recommends_nothing(self):
        out = dx.select_candidate({"ii_regularised_trees": _summary(1.0, q50=40.0),
                                   "i_interior_tracking": _summary(0.9, band=80.0)},
                                  _interval(-1, 1))
        self.assertIsNone(out["recommended"])
        self.assertIn("#244 does not start", out["reason"])

    def test_a_lower_crps_that_misses_the_bar_is_not_chosen(self):
        out = dx.select_candidate({"iii_residual_law": _summary(0.8, q50=60.0),
                                   "iv_regularised_and_tracking": _summary(1.0)},
                                  _interval(0.1, 0.2))
        self.assertEqual(out["recommended"], "iv_regularised_and_tracking")

    def test_a_simpler_candidate_within_the_interval_is_preferred(self):
        summaries = {"iv_regularised_and_tracking": _summary(0.9),
                     "ii_regularised_trees": _summary(1.0)}
        out = dx.select_candidate(summaries, _interval(-0.05, 0.02))
        self.assertEqual(out["leader"], "iv_regularised_and_tracking")
        self.assertEqual(out["recommended"], "ii_regularised_trees")

    def test_a_simpler_candidate_outside_the_interval_is_not(self):
        summaries = {"iv_regularised_and_tracking": _summary(0.9),
                     "ii_regularised_trees": _summary(1.0)}
        out = dx.select_candidate(summaries, _interval(-0.2, -0.01))
        self.assertEqual(out["recommended"], "iv_regularised_and_tracking")

    def test_fixing_the_trees_ranks_before_patching_the_output(self):
        self.assertLess(dx.COMPLEXITY["ii_regularised_trees"], dx.COMPLEXITY["i_interior_tracking"])
        self.assertLess(dx.COMPLEXITY["ii_regularised_trees"], dx.COMPLEXITY["iii_residual_law"])
        summaries = {"i_interior_tracking": _summary(0.9), "ii_regularised_trees": _summary(1.0)}
        out = dx.select_candidate(summaries, _interval(-0.05, 0.02))
        self.assertEqual(out["recommended"], "ii_regularised_trees")

    def test_an_undeclared_candidate_is_refused(self):
        with self.assertRaises(ValueError):
            dx.select_candidate({"something_new": _summary(1.0)}, _interval(-1, 1))


class MeasureTests(unittest.TestCase):
    def test_half_tie(self):
        self.assertEqual(dx.below(1.0, 2.0, half_tie=True), 1.0)
        self.assertEqual(dx.below(2.0, 2.0, half_tie=True), 0.5)
        self.assertEqual(dx.below(2.0, 2.0, half_tie=False), 1.0)
        self.assertEqual(dx.inside(1.0, 1.0, 3.0, mode="half"), 0.5)
        self.assertEqual(dx.inside(1.0, 1.0, 3.0, mode="closed"), 1.0)
        self.assertEqual(dx.inside(1.0, 1.0, 3.0, mode="open"), 0.0)
        self.assertEqual(dx.inside(4.0, 1.0, 3.0, mode="closed"), 0.0)

    def test_pit_bins_carry_unit_weight(self):
        vector = [-2.0, 0.0, 0.0, 0.0, 3.0]
        for value in (-5.0, -2.0, -1.0, 0.0, 1.0, 3.0, 4.0):
            self.assertAlmostEqual(sum(dx.pit_bins(vector, value)), 1.0)
        # Between two quantiles: one bin.
        self.assertEqual(dx.pit_bins(vector, 1.0), [0, 0, 0, 0, 1.0, 0])
        # On one quantile: half either side.
        self.assertEqual(dx.pit_bins(vector, -2.0), [0.5, 0.5, 0, 0, 0, 0])
        # On three tied quantiles (levels .25 to .75): spread over .25 to .75.
        self.assertEqual(dx.pit_bins(vector, 0.0), [0, 0, 0.5, 0.5, 0, 0])

    def test_calibrated_draws_cover_their_levels(self):
        rng = random.Random(1)
        days = []
        for _ in range(4000):
            days.append({"y": rng.gauss(0, 1), "issued": [-1.6449, -0.6745, 0.0, 0.6745, 1.6449]})
        cov = dx.coverage(days)
        self.assertAlmostEqual(cov["band_50_half_edge"], 50.0, delta=2.5)
        self.assertAlmostEqual(cov["band_90_half_edge"], 90.0, delta=1.5)
        self.assertAlmostEqual(cov["coverage_half_tie"]["0.25"], 25.0, delta=2.0)


def _days(n, anchor_lag=1):
    first = date(2020, 1, 1)
    days = []
    rng = random.Random(7)
    for k in range(n):
        when = first + timedelta(days=k)
        anchor = first + timedelta(days=k - anchor_lag)
        days.append({"date": when.isoformat(), "anchor": anchor.isoformat(),
                     "y": float(rng.randint(-3, 3)), "issued": [-4.0, -1.0, 0.0, 1.0, 4.0]})
    return days


class ObservabilityTests(unittest.TestCase):
    """A label scored after a day's anchor never reaches that day's vector."""

    def _future_changed(self, days, j):
        changed = [dict(d) for d in days]
        for k, d in enumerate(days):
            if d["date"] > days[j]["anchor"]:
                changed[k]["y"] = 1e3
        return changed

    def test_tracking_reads_no_label_after_the_anchor(self):
        days = _days(120, anchor_lag=20)
        j = 100
        base, _ = dx.interior_tracking(days)
        moved, _ = dx.interior_tracking(self._future_changed(days, j))
        self.assertEqual(base[j], moved[j])

    def test_residual_law_reads_no_label_after_the_anchor(self):
        days = _days(120, anchor_lag=20)
        rows = {date.fromisoformat(d["date"]): SimpleNamespace(spread_bps=d["y"]) for d in days}
        j = 100
        base = dx.residual_law(days, rows, scaled=False)
        moved = dx.residual_law(self._future_changed(days, j), rows, scaled=False)
        self.assertEqual(base[j], moved[j])


class WindowGuardTests(unittest.TestCase):
    def test_a_walk_past_the_opened_tier_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            panel = Path(tmp) / "panel.csv"
            panel.write_text("x", encoding="utf-8")
            walks = []
            for variant, h in [(v, h) for v in dx.VARIANTS
                               for h in (dx.HORIZONS if v == "v1" else (1,))]:
                path = Path(tmp) / f"{variant}_{h}.json"
                last = "2026-09-04" if (variant, h) == ("v1", 3) else "2026-09-03"
                path.write_text(json.dumps({"variant": variant, "horizon": h, "panel_sha256": "p",
                                            "days": [{"date": last}]}), encoding="utf-8")
                walks.append(path)
            args = SimpleNamespace(panel=panel, walks=walks, output=Path(tmp) / "out.json")
            originals = (dx.load_daily_panel, dx.audit_panel, dx.panel_sha256, dx.fp._frozen_panel_sha256,
                         dx.load_split_declaration)
            dx.load_daily_panel = lambda path: []
            dx.audit_panel = lambda rows: None
            dx.panel_sha256 = lambda path: "p"
            dx.fp._frozen_panel_sha256 = lambda: "p"
            dx.load_split_declaration = lambda path: None
            message = None
            try:
                dx.assemble_command(args)
            except ValueError as error:
                message = str(error)
            except Exception as error:  # past the guard, the assembly fails on its own terms
                message = f"reached the assembly: {error!r}"
            finally:
                (dx.load_daily_panel, dx.audit_panel, dx.panel_sha256, dx.fp._frozen_panel_sha256,
                 dx.load_split_declaration) = originals
            self.assertIn("after the opened tier", message or "nothing was refused")


class ReproductionTests(unittest.TestCase):
    """v1's per-day CRPS at h = 1 reproduces both published records exactly."""

    def setUp(self):
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.days = [{"date": d, "y": y, "issued": v} for d, y, v in self.record["v1_h1_per_day"]]

    def test_the_record_reproduces_the_published_crps_exactly(self):
        published = json.loads(CRPS_RECORD.read_text(encoding="utf-8"))["comparison"]["per_origin"]
        window = json.loads(FINAL.read_text(encoding="utf-8"))["primary"]["window_per_origin"]
        expected = {e["scored_date"]: e["loss_b_bps"] for e in published + window}
        ours = {d["date"]: dx._crps(d["issued"], d["y"]) for d in self.days}
        self.assertEqual(set(ours), set(expected))
        for day, value in ours.items():
            self.assertEqual(value, expected[day], day)
        self.assertTrue(self.record["reproduction"]["exact"])
        self.assertEqual(dx.reproduction_check(self.days)["days"], len(expected))

    def test_a_changed_day_is_refused(self):
        days = [dict(d) for d in self.days]
        days[5] = dict(days[5], y=days[5]["y"] + 1.0)
        with self.assertRaises(ValueError):
            dx.reproduction_check(days)


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_no_day_after_the_opened_tier(self):
        self.assertLessEqual(max(d for d, _, _ in self.record["v1_h1_per_day"]), "2026-09-03")
        self.assertEqual(self.record["windows"]["diagnosis"], ["2018-06-29", "2025-12-31"])

    def test_the_selection_is_the_rule_applied_to_the_record(self):
        q7 = self.record["q7_candidates"]["candidates"]
        summaries = {name: entry["2018_2025"] for name, entry in q7.items()}
        pairs = self.record["selection"]["paired_against_leader"]
        out = dx.select_candidate(summaries, lambda name, leader: pairs[f"{name}_vs_{leader}"])
        for key in ("recommended", "eligible", "leader"):
            self.assertEqual(out[key], self.record["selection"][key])
        self.assertEqual(self.record["selection_rule"], dx.SELECTION_RULE)

    def test_the_selection_reads_only_the_diagnosis_window(self):
        for entry in self.record["q7_candidates"]["candidates"].values():
            self.assertEqual(entry["paired_vs_v1_2018_2025"]["days"],
                             self.record["q7_candidates"]["v1"]["2018_2025"]["days"])
        self.assertEqual(self.record["q7_candidates"]["v1"]["2018_2025"]["days"], 1873)


if __name__ == "__main__":
    unittest.main()
