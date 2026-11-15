"""`scripts/qe_vs_calendar_gbm_1593.py` (#1593; H5 step 3, development tier): the frozen candidate (s3c-ann-net) against `gbm_funding_cal_direct`
on quarter-end turns and year-ends, from walks that already exist (the candidate's regenerates, the GBM's are on Eleonora's Mac), no refit.

What these tests pin, without the walks: the guards (no day after 2025-12-31, the day types in force, the pairing on common decision days and on the
same targets and outcomes, the candidate reproducing #1548's figures before anything is paired), the orientation of every difference (the GBM minus the
candidate), the partition of the paired cells into turn type and regime, the day-level interval's arithmetic, and the page and log entry rendered from a
record. The walk itself is run on the Mac (`scripts/mac_score_1593.sh`).

Recorded mutations (a new guard each):
* `require_study_window`: `if late:` changed to `if False:`. `GuardTests.test_a_day_after_the_study_end_is_refused` then failed with
  `AssertionError: LookAheadError not raised`; restored, it passes.
* `require_current_day_types`: `if not turn_days.in_force():` changed to `if False:`. `GuardTests.test_the_retired_flags_are_refused` then failed with
  `AssertionError: ValueError not raised`; restored, it passes.
* `require_same_outcomes`: the comparison `a != b` changed to `a == b`. `PairingTests.test_a_different_outcome_is_refused` then errored with
  `ValueError: 2022-03-01 lead 1: the outcome at 2022-03-02 is 1.0 in the walks' frame and 1.0 in the candidate's` (it refused the equal case); restored, it passes.
* `reproduce_candidate`: `abs(a - b) > TOLERANCE` changed to `abs(a - b) > 1.0`. `ReproductionTests.test_a_candidate_figure_that_differs_is_refused` then
  failed with `AssertionError: ValueError not raised`; restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("qe_vs_calendar_gbm_1593", ROOT / "scripts" / "qe_vs_calendar_gbm_1593.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["qe_vs_calendar_gbm_1593"] = script
_spec.loader.exec_module(script)

from repo_model import turn_days  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

RECORD_1548 = ROOT / "docs" / "research" / "qe-event-model-1548" / "result.json"


def cell(event, h, kind, cand=0.0, gbm=0.0, covered_cand=1.0, covered_gbm=1.0):
    """One group cell as `qe_event_model_1548.group_cells` writes it: 5 rates, grid CRPS, twCRPS for the candidate, the same for the arm (here the GBM), then arm minus candidate."""

    c = [covered_cand, 0.0, 0.0, 0.0, 0.0, cand, cand]
    g = [covered_gbm, 0.0, 0.0, 0.0, 0.0, gbm, gbm]
    return {"event": event, "h": h, "type": kind, "qe1363": True, "in_group": True, "vec": c + g + [b - a for a, b in zip(c, g)]}


class GuardTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 31)])

    def test_the_retired_flags_are_refused(self):
        with turn_days.legacy_reading():
            with self.assertRaises(ValueError):
                script.require_current_day_types()

    def test_the_turn_labels_in_force_are_read(self):
        script.require_current_day_types()


class PairingTests(unittest.TestCase):
    def test_the_common_days_are_those_both_cover_and_whose_last_target_is_in_the_study(self):
        days = [date(2025, 12, 22) + timedelta(days=k) for k in range(10)]
        walked = {d: {} for d in days[2:]}
        target = lambda d, h: d + timedelta(days=h)  # noqa: E731
        out = script.common_days(days, walked, target)
        self.assertEqual(out, [d for d in days[2:] if d + timedelta(days=5) <= script.LAST_TARGET])
        self.assertNotIn(days[0], out)

    def test_a_different_target_is_refused(self):
        days = [date(2022, 3, 1)]
        same = lambda d, h: d + timedelta(days=h)  # noqa: E731
        other = lambda d, h: d + timedelta(days=h + (1 if h == 3 else 0))  # noqa: E731
        outcome = {d + timedelta(days=h): 1.0 for d in days for h in range(1, 7)}
        script.require_same_outcomes(days, same, same, outcome, outcome)
        with self.assertRaises(ValueError):
            script.require_same_outcomes(days, same, other, outcome, outcome)

    def test_a_different_outcome_is_refused(self):
        days = [date(2022, 3, 1)]
        target = lambda d, h: d + timedelta(days=h)  # noqa: E731
        a = {d + timedelta(days=h): 1.0 for d in days for h in range(1, 6)}
        b = dict(a)
        script.require_same_outcomes(days, target, target, a, b)
        b[date(2022, 3, 3)] = 1.5
        with self.assertRaises(ValueError):
            script.require_same_outcomes(days, target, target, a, b)


class ReproductionTests(unittest.TestCase):
    def setUp(self):
        theirs = json.loads(RECORD_1548.read_text(encoding="utf-8"))
        self.group = theirs["windows"]["development"]["group"]

    def rows(self):
        group = json.loads(json.dumps(self.group))
        return {"group": group["pooled"], "quarter_end_turn": group["by_type"]["quarter_end_turn"], "year_end": group["by_type"]["year_end"]}

    def test_the_candidate_of_the_record_reproduces_itself(self):
        script.reproduce_candidate(self.rows(), self.group)

    def test_a_candidate_figure_that_differs_is_refused(self):
        rows = self.rows()
        rows["year_end"]["measures"]["grid_crps"]["candidate"] += 0.01
        with self.assertRaises(ValueError):
            script.reproduce_candidate(rows, self.group)

    def test_the_arm_is_not_compared(self):
        rows = self.rows()
        rows["group"]["measures"]["grid_crps"]["arm"] += 5.0
        script.reproduce_candidate(rows, self.group)


class TableTests(unittest.TestCase):
    CELLS = [cell("2019-03", 1, "quarter_end_turn", 4.0, 3.0), cell("2019-03", 2, "quarter_end_turn", 6.0, 3.0), cell("2019-12", 1, "year_end", 5.0, 9.0),
             cell("2020-06", 1, "quarter_end_turn", 2.0, 2.0), cell("2024-12", 3, "year_end", 8.0, 4.0)]

    def test_every_cell_is_in_one_scope_and_one_regime(self):
        table = script.regime_table(self.CELLS, reps=20)
        for scope in ("group", "quarter_end_turn", "year_end"):
            parts = [v for k, v in table[scope].items() if k != "all" and v is not None]
            self.assertEqual(sum(p["cells"] for p in parts), table[scope]["all"]["cells"], scope)
        self.assertEqual(table["group"]["all"]["cells"], 5)
        self.assertEqual(table["quarter_end_turn"]["all"]["events"], 2)

    def test_the_difference_is_the_gbm_minus_the_candidate(self):
        entry = script.regime_table(self.CELLS, reps=20)["quarter_end_turn"]["2018-19"]
        crps = entry["measures"]["grid_crps"]
        self.assertAlmostEqual(crps["candidate"], 5.0)
        self.assertAlmostEqual(crps["arm"], 3.0)
        self.assertAlmostEqual(crps["diff"], -2.0)

    def test_a_day_level_group_is_the_gbm_minus_the_candidate_per_target_day(self):
        start = date(2019, 3, 20)
        rows = {start + timedelta(days=k): {"type": "quarter_end_turn", "event": "2019-03", "cand": (4.0, 4.0), "arm": (3.0 + 0.01 * (k % 3), 3.0 + 0.02 * (k % 4))} for k in range(15)}
        out = script.day_level(rows, seed=3, draws=200)
        crps = out["quarter_end_turn"]["2018-19"]["grid_crps"]
        self.assertEqual(crps["days"], 15)
        self.assertAlmostEqual(crps["excess"], -0.99, delta=0.02)
        self.assertLess(crps["upper"], 0.0)
        self.assertIsNone(out["year_end"]["2018-19"])

    def test_a_difference_that_never_changes_carries_no_interval_and_no_error(self):
        start = date(2019, 3, 1)
        rows = {start + timedelta(days=k): {"type": "year_end", "event": "2019-12", "cand": (4.0, 4.0), "arm": (3.0, 3.0)} for k in range(15)}
        entry = script.day_level(rows, seed=3, draws=200)["year_end"]["2018-19"]["grid_crps"]
        self.assertIsNone(entry["lower"])
        self.assertIn("no long-run variance", entry["note"])
        self.assertAlmostEqual(entry["excess"], -1.0)

    def test_a_day_level_group_of_few_days_carries_no_interval(self):
        start = date(2019, 3, 25)
        rows = {start + timedelta(days=k): {"type": "year_end", "event": "2019-12", "cand": (4.0, 4.0), "arm": (3.0, 3.0)} for k in range(3)}
        out = script.day_level(rows, seed=3, draws=200)
        entry = out["year_end"]["2018-19"]["grid_crps"]
        self.assertIsNone(entry["lower"])
        self.assertAlmostEqual(entry["excess"], -1.0)


class PageTests(unittest.TestCase):
    def record(self):
        table = script.regime_table(TableTests.CELLS, reps=20)
        return {"issue": 1593, "label": "development, not a verdict", "seed": script.SEED, "event_reps": 20, "draws": 200, "few_events_below": script.FEW,
                "panel_sha256": "4ddc3882" + "0" * 56, "scratch_panel_sha256": "f9fae9dc" + "0" * 56, "regimes": list(script.REGIMES),
                "pair": {"candidate": script.CANDIDATE, "other": script.DIRECT},
                "days": {"candidate_decision_days": 1855, "walked_decision_days": 1855, "common_decision_days": 1855, "first": "2018-06-01", "last": "2025-12-24"},
                "cells": {"group": 5}, "reproduction": "the candidate's figures equal #1548's to 1e-9",
                "table": table, "day_level": script.day_level({}, seed=3, draws=200)}

    def test_the_page_carries_the_orientation_the_no_combination_and_no_verdict(self):
        page = script.render(self.record())
        for phrase in ("#1593", "H5", "Q9", "not a verdict", "no combination", "GBM minus the candidate", "decision instant", "quarter-end turns", "year-ends",
                       "2018-19", "2025-26", "few events"):
            self.assertIn(phrase, page, msg=phrase)

    def test_the_log_entry_passes_the_log_checker(self):
        import subprocess
        entry = script.log_entry(self.record(), "2026-11-13")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-11-13-model-01593-H5-step3.md"
            path.write_text(entry, encoding="utf-8")
            done = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "check_research_log.py"), "check-block", str(path)], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(done.returncode, 0, msg=done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
