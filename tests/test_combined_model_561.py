"""The combined model (#561): the declaration, the judge's candidate files and the script's rules.

The ordinary-day component itself (its blocks, its factor read at the anchor, its guards) is tested in
`test_ml.CombinedOrdinaryTests`; this file checks what the script declares and how it combines the pieces.

Recorded mutation, 11 October 2026, in a disposable copy: `scripts/combined_model_561.py`, the line
`require_unlocked([last], where="combined_model_561")` replaced by `pass` in `run_command`.
`RunGuardTests.test_run_refuses_a_locked_last_day` then errors with `FileNotFoundError` (the guard is skipped and the
run goes on to read the panel).
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

from repo_model import pressure_judge as pj
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "combined_model_561.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
JUDGE_CANDIDATES = dict(pj.load_declaration().candidates)


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("combined_model_561_script", ROOT / "scripts" / "combined_model_561.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["combined_model_561_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(PARENTS), DECLARED)

    def test_at_most_four_variants_and_the_ablations_are_the_blocks_dropped_in_turn(self):
        self.assertLessEqual(len(DECLARED["variants"]), 4)
        self.assertEqual(set(DECLARED["variants"]), set(SCRIPT.variant_names()))
        self.assertEqual(set(DECLARED["ablations"]), set(SCRIPT.ablation_names()))
        self.assertEqual(len(DECLARED["ablations"]), 3)

    def test_the_parents_are_the_two_risk_date_passers_and_unchanged(self):
        self.assertEqual(set(DECLARED["parents"]), {"risk_gbm", "risk_logistic"})
        for name, spec in DECLARED["parents"].items():
            self.assertEqual(spec, PARENTS["candidates"][name])

    def test_the_parents_run_with_settlement_and_h41_timing_on(self):
        self.assertEqual(DECLARED["parent_timing"], "both")

    def test_the_gate_is_the_one_532_declared_and_applies_to_the_every_day_component_only(self):
        controls = json.loads((ROOT / "metadata" / "risk_date_false_alarm_controls.json").read_text())["controls"]
        gate = controls["gate"]
        for key in ("quantile", "window", "minimum_earlier"):
            self.assertEqual(DECLARED["gate"][key], gate[key])
        self.assertIn("not a risk date", DECLARED["gate"]["applies_to"])

    def test_the_calibration_is_declared_and_conditioned_on_no_hindsight_regime(self):
        self.assertIn(DECLARED["ordinary_days"]["calibration"], ("platt", "isotonic"))
        self.assertIn("never", DECLARED["ordinary_days"]["conditioning"])
        self.assertIn("regime", DECLARED["ordinary_days"]["conditioning"])

    def test_the_selection_is_stated_plainly(self):
        self.assertIn("after seeing", DECLARED["selection"])
        self.assertIn("2026", DECLARED["selection"])

    def test_every_row_is_a_judge_candidate_with_a_file_of_its_own(self):
        rows = list(DECLARED["variants"]) + list(DECLARED["ablations"])
        for name in rows:
            entry = JUDGE_CANDIDATES[name]
            self.assertEqual(entry["role"], "candidate")
            self.assertEqual(entry["parent"], name.split("+")[0] + "+settle+h41")
            self.assertTrue((ROOT / "metadata" / "pressure_judge" / "candidates" / f"{name}.json").is_file())

    def test_no_row_is_in_the_confirmation_look(self):
        confirmation = set(pj.load_declaration().confirmation_candidates)
        for name in list(DECLARED["variants"]) + list(DECLARED["ablations"]):
            self.assertNotIn(name, confirmation)

    def test_the_scoring_window_ends_before_the_lockbox_and_nothing_is_published(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")
        self.assertIn("nothing", DECLARED["published"])

    def test_the_declared_blocks_are_the_models(self):
        from repo_model import ml

        self.assertEqual(tuple(DECLARED["ordinary_days"]["blocks"]), ml.COMBINED_BLOCKS)
        self.assertEqual(DECLARED["ordinary_days"]["calibration"], ml.COMBINED_CALIBRATION)


class FeatureTests(unittest.TestCase):
    def test_the_full_model_reads_the_structural_terms_the_projected_distance_and_the_factors_series(self):
        from repo_model import ml

        design, backtest = SCRIPT.component_features(2, ml.COMBINED_BLOCKS)
        self.assertIn("net_settlement_due_5d", design)
        self.assertNotIn("net_settlement", design)
        self.assertIn("proj_dist_h2", design)
        self.assertTrue(set(ml.LATENT_FACTOR_COLUMNS) <= set(backtest))
        self.assertFalse(set(ml.LATENT_FACTOR_COLUMNS) - {"on_rrp"} & set(design))

    def test_at_horizon_one_the_scored_days_own_settlement_is_read(self):
        design, _backtest = SCRIPT.component_features(1, ("structural",))
        self.assertIn("net_settlement", design)
        self.assertNotIn("net_settlement_due_5d", design)

    def test_dropping_a_block_drops_its_columns_and_only_its_columns(self):
        from repo_model import ml

        for dropped, mark in (("factor", "sofr_p99"), ("structural", "bank_total_assets"), ("projected", "proj_dist_h3")):
            blocks = tuple(b for b in ml.COMBINED_BLOCKS if b != dropped)
            design, backtest = SCRIPT.component_features(3, blocks)
            self.assertNotIn(mark, backtest, dropped)
            full_design, full_backtest = SCRIPT.component_features(3, ml.COMBINED_BLOCKS)
            self.assertIn(mark, full_backtest)


class CombineTests(unittest.TestCase):
    def column(self, values):
        return {"5": dict(values), "10": {day: p / 2 for day, p in values.items()}}

    def test_a_risk_date_takes_the_passer_and_any_other_day_takes_the_component(self):
        parent = self.column({"2020-01-01": 0.4, "2020-01-02": 0.0})
        own = self.column({"2020-01-01": 0.9, "2020-01-02": 0.3})
        out = SCRIPT.combine(parent, own, {"2020-01-01": False, "2020-01-02": True})
        self.assertEqual(out["5"], {"2020-01-01": 0.4, "2020-01-02": 0.3})
        self.assertEqual(out["10"], {"2020-01-01": 0.2, "2020-01-02": 0.15})

    def test_the_passer_must_be_zero_off_the_risk_dates(self):
        parent = self.column({"2020-01-01": 0.4})
        own = self.column({"2020-01-01": 0.9})
        with self.assertRaises(ValueError):
            SCRIPT.combine(parent, own, {"2020-01-01": True})

    def test_mismatched_days_are_refused(self):
        parent = self.column({"2020-01-01": 0.4})
        own = self.column({"2020-01-02": 0.9})
        with self.assertRaises(ValueError):
            SCRIPT.combine(parent, own, {"2020-01-01": False})

    def test_the_gate_leaves_a_risk_date_unchanged_and_zeroes_a_quiet_day_early_in_the_history(self):
        days = [f"2020-01-{k:02d}" for k in range(1, 6)]
        column = {"5": dict(zip(days, [0.5, 0.2, 0.3, 0.1, 0.4])), "10": dict(zip(days, [0.2] * 5))}
        off = {day: day != days[0] for day in days}
        out = SCRIPT.apply_gate(column, off)
        self.assertEqual(out["5"][days[0]], 0.5)  # a risk date keeps its forecast
        for day in days[1:]:
            self.assertEqual(out["5"][day], 0.0)  # fewer than 60 earlier days off a risk date: the gate is closed

    def test_the_gate_is_the_one_532_built(self):
        days = [f"d{k:03d}" for k in range(400)]
        column = {"5": {day: (k % 17) / 17.0 for k, day in enumerate(days)}}
        off = {day: True for day in days}
        out = SCRIPT.apply_gate(column, off)
        raw = [[column["5"][day] for day in days]]
        again = SCRIPT.fa.apply_control("gate", SCRIPT.fa.CONTROLS["gate"], raw, [True] * 400, [None] * 400)
        self.assertEqual([out["5"][day] for day in days], again[0])


class RunGuardTests(unittest.TestCase):
    def args(self, **changes):
        import argparse

        base = dict(horizon=1, panel=ROOT / "no-such-panel.csv", published=ROOT / "no-such-panel.csv",
                    parents=ROOT / "no-such-parents.json", output=ROOT / "no-such-output.json")
        base.update(changes)
        return argparse.Namespace(**base)

    def test_run_refuses_a_locked_last_day(self):
        declared = json.loads(json.dumps(DECLARED))
        declared["scoring"]["last_day"] = "2026-09-10"
        with mock.patch.object(SCRIPT, "declared_document", return_value=declared):
            with self.assertRaises(LookAheadError):
                SCRIPT.run_command(self.args())

    def test_the_declared_last_day_is_not_refused(self):
        with mock.patch.object(SCRIPT, "load_daily_panel", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):  # past the guard, into the panel
                SCRIPT.run_command(self.args())


class SummaryTests(unittest.TestCase):
    def judged(self, flagged, flat_false, weighted_false, tiers=(True, False, False)):
        verdict = dict(zip(("tier_1_onset_warning", "tier_3_no_crying_wolf", "tier_5_week_ahead"), tiers), passes=False)
        tier = {
            "onsets_flagged": flagged,
            "onsets": 26,
            "recall": {"mean": flagged / 26.0, "interval": {"lower": 0.1, "upper": 0.9}},
            "worst_false_alarms_per_onset": flat_false,
            "worst_weighted_false_alarms_per_onset": weighted_false,
        }
        return {"tiers": {"onset_warning": {"lead_at_least_1": tier}}, "verdict": verdict}

    def test_the_table_has_a_row_for_every_combined_row_control_and_benchmark(self):
        rows = SCRIPT.summary_rows(DECLARED)
        self.assertEqual(rows[:7], SCRIPT.all_rows())
        for name in ("ngboost_laplace", "calendar_climatology", "persistence_logistic", "risk_gbm+every_day+gate+settle+h41"):
            self.assertIn(name, rows)
        entries = {name: self.judged(10, 1.5, 1.0) for name in rows}
        text = SCRIPT.summary_table(DECLARED, entries, entries)
        self.assertEqual(len(text.strip().splitlines()), len(rows) + 2)
        self.assertIn("| risk_gbm+combined | 10/26 / 10/26 |", text)
        self.assertIn("yes / no / no", text)


if __name__ == "__main__":
    unittest.main()
