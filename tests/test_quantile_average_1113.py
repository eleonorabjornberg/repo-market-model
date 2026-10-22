"""The equal-weight quantile average of `spread_mr_ctx` and `gbm_funding_cal_aligned` (`scripts/quantile_average_1113.py`, #1123, H5 step 3; avenue #1113).

What is pinned: the average itself (0.5 / 0.5, level by level, sorted so it stays monotone), the two hit rules of the 95th-percentile exceedance, the
Politis-White block read beside the protocol's 10, the declared reading rules, the committed declaration, and a whole run of `compute_result` on a
synthetic frame whose figures nobody reads. The real walks are `gbm_funding_cal_aligned`'s (#1027) and run on Eleonora's Mac.

Recorded mutations (each applied, the named test run, and reverted):

* `average_laws`, the line `return sorted(mixed)` changed to `return mixed`: `AverageTests.test_the_average_is_sorted_so_it_stays_monotone` fails with
  `AssertionError` (`Lists differ`: the unsorted average holds 4.5 at level 5 and 0.5 at level 6).
* `average_forecasts`, the line `if set(first[day]) != set(second[day]):` changed to `if False:`: `AverageTests.test_parts_with_different_leads_are_refused`
  errors with `KeyError: 5` (the second part has no lead 5) instead of the `ValueError` it asserts.
* `require_study_window` of #1027, which this module's `require_study_window` calls, the line `if late:` changed to `if False:`:
  `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with `AssertionError` (`LookAheadError not raised`).
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("quantile_average_1113_script", REPO / "scripts" / "quantile_average_1113.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

GRID = sp.GRID
LEVELS = len(GRID)


def shape(scale=1.0):
    """A monotone 23-level law: the offsets of GRID from the median, widening with `scale`."""

    return [scale * (level - 0.5) * 8.0 for level in GRID]


def law(center, scale=1.0):
    return [center + offset for offset in shape(scale)]


class AverageTests(unittest.TestCase):
    def test_the_average_is_the_equal_weight_mean_level_by_level(self):
        first, second = law(0.0, 1.0), law(2.0, 3.0)
        got = script.average_laws(first, second)
        self.assertEqual(len(got), LEVELS)
        for level in range(LEVELS):
            self.assertAlmostEqual(got[level], 0.5 * first[level] + 0.5 * second[level], places=12)

    def test_the_weights_are_one_half_each(self):
        self.assertEqual(script.WEIGHTS, (0.5, 0.5))

    def test_the_average_is_sorted_so_it_stays_monotone(self):
        # a part that crosses itself (it is refused by the scorer, so the average sorts what a part leaves out of order)
        self.assertEqual(script.sort_levels([3.0, 2.0, 4.0]), [2.0, 3.0, 4.0])
        crossing = [0.0] * LEVELS
        crossing[5], crossing[6] = 9.0, 1.0
        got = script.average_laws(crossing, [0.0] * LEVELS)
        self.assertEqual(got, sorted(got))

    def test_a_monotone_pair_gives_a_monotone_average_that_sorting_leaves_alone(self):
        got = script.average_laws(law(0.0, 1.0), law(1.0, 2.0))
        self.assertEqual(got, sorted(got))

    def test_the_average_of_a_law_with_itself_is_that_law(self):
        one = law(1.5, 2.0)
        for a, b in zip(script.average_laws(one, one), one):
            self.assertAlmostEqual(a, b, places=12)

    def test_laws_of_different_length_are_refused(self):
        with self.assertRaises(ValueError):
            script.average_laws(law(0.0)[:-1], law(0.0))

    def test_a_law_off_the_grid_is_refused(self):
        with self.assertRaises(ValueError):
            script.average_laws([1.0, 2.0], [1.0, 2.0])

    def test_a_non_finite_quantile_is_refused(self):
        bad = law(0.0)
        bad[3] = float("nan")
        with self.assertRaises(ValueError):
            script.average_laws(bad, law(0.0))

    def forecasts(self, days, leads=(1, 2, 3, 4, 5), center=0.0):
        return {d: {h: law(center + h) for h in leads} for d in days}

    def test_the_forecasts_are_averaged_on_the_days_both_parts_cover(self):
        days = [date(2019, 1, 2) + timedelta(days=i) for i in range(5)]
        first, second = self.forecasts(days[:4]), self.forecasts(days[1:], center=2.0)
        got = script.average_forecasts(first, second)
        self.assertEqual(sorted(got), days[1:4])
        for d in got:
            for h in (1, 2, 3, 4, 5):
                for a, b, c in zip(got[d][h], first[d][h], second[d][h]):
                    self.assertAlmostEqual(a, 0.5 * b + 0.5 * c, places=12)

    def test_parts_with_different_leads_are_refused(self):
        days = [date(2019, 1, 2), date(2019, 1, 3)]
        with self.assertRaises(ValueError):
            script.average_forecasts(self.forecasts(days), self.forecasts(days, leads=(1, 2, 3, 4)))


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 31)])


class HitRuleTests(unittest.TestCase):
    def test_a_tie_is_a_hit_under_one_rule_only(self):
        q = [0.0] * 23
        q[script.LEVEL_95] = 5.0
        self.assertEqual(script.hits([5.0], [q], rule="above"), [0])
        self.assertEqual(script.hits([5.0], [q], rule="at_or_above"), [1])
        self.assertEqual(script.hits([6.0], [q], rule="above"), [1])

    def test_a_float_noise_tie_is_a_tie(self):
        # SOFR 2.00 less IORB 1.95 is 5.000000000000004 bp; the quantile is the whole basis point
        noisy = 5.000000000000004
        self.assertEqual(script.hits([noisy], [[5.0] * 23], rule="above"), [0])
        self.assertEqual(script.hits([noisy], [[5.0] * 23], rule="at_or_above"), [1])
        self.assertEqual(script.hits([5.0], [[5.000000000000004] * 23], rule="at_or_above"), [1])

    def test_the_95th_level_is_read(self):
        self.assertAlmostEqual(GRID[script.LEVEL_95], 0.95)
        q = list(range(23))
        self.assertEqual(script.hits([q[script.LEVEL_95] + 0.5], [q], rule="above"), [1])
        self.assertEqual(script.hits([q[script.LEVEL_95] - 0.5], [q], rule="above"), [0])

    def test_there_are_two_rules_and_no_default(self):
        self.assertEqual(script.HIT_RULES, ("above", "at_or_above"))
        with self.assertRaises(ValueError):
            script.hits([1.0], [[0.0] * 23], rule="beyond")


class BlockTests(unittest.TestCase):
    def test_the_politis_white_block_is_at_least_one(self):
        # an alternating series has a negative long-run variance share: the automatic block is clamped to 1, never below
        self.assertGreaterEqual(script.politis_white_block([(-1.0) ** i + 0.01 * (i % 3) for i in range(80)]), 1.0)

    def test_a_trending_series_gets_a_longer_block_than_noise(self):
        import random
        rng = random.Random(7)
        noise = [rng.gauss(0, 1) for _ in range(400)]
        slow, level = [], 0.0
        for _ in range(400):
            level = 0.95 * level + rng.gauss(0, 1)
            slow.append(level)
        self.assertGreater(script.politis_white_block(slow), script.politis_white_block(noise))

    def test_a_series_too_short_for_a_block_is_undefined_not_a_number(self):
        self.assertIsNone(script.politis_white_block([0.1, 0.2, 0.3]))

    def test_the_protocol_block_is_ten(self):
        self.assertEqual(script.PROTOCOL_BLOCK, 10)
        self.assertEqual(sp.BLOCK_LENGTH, 10)


def row(skill, lo, hi):
    return {"days": 100, "skill": skill, "skill_interval": [lo, hi], "difference": 0.1, "difference_interval": [0.0, 0.2]}


class ReadingRuleTests(unittest.TestCase):
    def rows(self, **over):
        base = {
            "vs_ctx": row(0.02, 0.005, 0.04), "vs_aligned": row(0.01, -0.01, 0.03),
            "calendar_vs_control": row(0.03, 0.01, 0.05), "ordinary_vs_control": row(-0.01, -0.03, 0.01),
            "vs_b1": row(0.05, 0.02, 0.08), "vs_b1_prime": row(0.03, 0.0, 0.06),
        }
        base.update(over)
        return base

    def test_it_says_which_part_the_average_beats_by_the_lower_bound(self):
        text = " ".join(script.reading_rules(self.rows()))
        self.assertIn("beats spread_mr_ctx", text)
        self.assertIn("is not shown to beat gbm_funding_cal_aligned", text)

    def test_it_reads_the_candidate_on_calendar_and_ordinary_days(self):
        text = " ".join(script.reading_rules(self.rows()))
        self.assertIn("beats gbm_funding on calendar days", text)
        self.assertIn("does not lose on ordinary days", text)
        lost = " ".join(script.reading_rules(self.rows(ordinary_vs_control=row(-0.05, -0.08, -0.02))))
        self.assertIn("loses on ordinary days", lost)

    def test_it_reports_b1_and_b1_prime_side_by_side_with_no_rule(self):
        text = " ".join(script.reading_rules(self.rows()))
        self.assertIn("over B1 ", text)
        self.assertIn("over B1'", text)

    def test_a_missing_or_undefined_cut_is_said_and_not_read(self):
        rules = script.reading_rules(self.rows(vs_ctx={"undefined": "no variance"}, calendar_vs_control=None))
        text = " ".join(rules)
        self.assertIn("spread_mr_ctx: undefined", text)
        self.assertIn("not read", text)


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))

    def test_the_committed_declaration_is_what_declare_writes(self):
        self.assertEqual(self.document, json.loads(json.dumps(script.declaration_document())))

    def test_it_declares_the_average_and_the_comparisons_of_the_directive(self):
        self.assertEqual(self.document["issue"], 1123)
        self.assertEqual(self.document["arm"]["weights"], {"spread_mr_ctx": 0.5, "gbm_funding_cal_aligned": 0.5})
        self.assertEqual(self.document["benchmarks"], ["spread_mr_ctx", "gbm_funding_cal_aligned", "gbm_funding", "B1", "B1_prime", "B2"])
        self.assertEqual(self.document["metrics"], ["grid_crps", "upper_tail_twcrps"])
        self.assertEqual(self.document["cuts"]["regimes"], script.ORDER_REGIME)
        self.assertEqual(self.document["bootstrap"]["blocks"], {"protocol": 10, "politis_white": "the automatic block of the pair's own loss differential, at least 1"})
        self.assertEqual(self.document["exceedance"]["hit_rules"], ["above", "at_or_above"])
        self.assertEqual(self.document["exceedance"]["level"], 0.95)

    def test_it_scores_no_locked_or_late_day(self):
        self.assertIn("no lockbox day", self.document["limits"])
        self.assertIn("no day after 2025-12-31", self.document["limits"])

    def test_it_changes_no_candidate(self):
        self.assertIn("gbm_funding stays the H5 candidate", self.document["status"])


# -- a whole run on a synthetic frame ---------------------------------------------------------------------------------


def business_days(count, start=date(2019, 1, 2)):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


class StubFrame:
    """What `compute_result` reads of #686's frame: the days, the target of a lead, the outcomes, the labels, the forecasts."""

    def __init__(self, decisions=130):
        self.dates = business_days(decisions + 6)
        self.position = {d: i for i, d in enumerate(self.dates)}
        self.days = self.dates[:decisions]
        self.outcome = {d: 1.0 + 3.0 * math.sin(i / 5.0) + (i % 4) * 0.5 for i, d in enumerate(self.dates)}
        self.values = {d: {"treasury_settlement_coupons": 0.0, "treasury_settlement_bills": 0.0} for d in self.dates}
        self.forecasts = {}

    def target(self, decision, lead):
        return self.dates[self.position[decision] + lead]

    def regime(self, day):
        return "2018-19" if self.position[day] < 70 else "2020"

    def day_type(self, day):
        return "month_end" if self.position[day] % 10 == 0 else "ordinary"

    def add(self, name, center, scale):
        self.forecasts[name] = {d: {h: law(center, scale) for h in sp.HORIZONS} for d in self.days}


class ComputeResultTests(unittest.TestCase):
    def frame(self):
        frame = StubFrame()
        for name, center, scale in (("B1", 0.0, 1.0), ("B1_prime", 0.5, 1.0), ("B2", 1.0, 1.5), (script.CTX, 1.5, 1.2),
                                     (script.CONTROL, 2.0, 1.1), (script.ALIGNED, 2.5, 1.0)):
            frame.add(name, center, scale)
        frame.forecasts[script.AVG] = script.average_forecasts(frame.forecasts[script.CTX], frame.forecasts[script.ALIGNED])
        return frame

    def result(self):
        return script.compute_result(self.frame(), draws=120, workers=1)

    def test_every_declared_pair_is_scored_at_both_blocks(self):
        result = self.result()
        pooled = result["groups"]["pooled"]["all decision days"]["metrics"]["grid_crps"]["pairs"]
        wanted = {f"{script.AVG} vs {b}" for b in (script.CTX, script.ALIGNED, script.CONTROL, "B1", "B1_prime", "B2")}
        self.assertEqual(set(pooled), wanted)
        for cell in pooled.values():
            self.assertIn("block_10", cell)
            self.assertIn("block_politis_white", cell)
            self.assertEqual(cell["block_10"]["days"], 130)
            self.assertGreaterEqual(cell["politis_white_block"], 1.0)

    def test_both_metrics_and_the_declared_cuts_are_there(self):
        result = self.result()
        self.assertEqual(sorted(result["groups"]["pooled"]["all decision days"]["metrics"]), ["grid_crps", "upper_tail_twcrps"])
        self.assertEqual(sorted(result["groups"]["regime"]), ["2018-19", "2020"])
        self.assertIn("ordinary", result["groups"]["target_type"])
        tested = set(result["groups"]["target_type"]) | {k.split("/", 1)[1] for k in result["skipped_groups"] if k.startswith("target_type/")}
        self.assertIn("month_end", tested)

    def test_a_group_of_fewer_than_twenty_days_is_listed_and_not_tested(self):
        frame = self.frame()
        result = script.compute_result(frame, draws=120, workers=1)
        for key, count in result["skipped_groups"].items():
            self.assertLess(count, script.MIN_GROUP_DAYS, key)

    def test_the_exceedance_is_reported_under_both_hit_rules_for_every_model(self):
        result = self.result()
        pooled = result["exceedance"]["pooled"]["all decision days"]
        self.assertEqual(sorted(pooled), sorted(result["models"]))
        for model, rules in pooled.items():
            self.assertEqual(sorted(rules), ["above", "at_or_above"], model)
            for rule, entry in rules.items():
                self.assertEqual(entry["nominal"], 0.05)
                self.assertTrue(0.0 <= entry["rate"] <= 1.0)
                self.assertEqual(entry["cells"], 130 * 5)
            self.assertGreaterEqual(rules["at_or_above"]["rate"], rules["above"]["rate"])

    def test_the_means_cover_every_model_and_b1_prime_sits_beside_b1(self):
        result = self.result()
        self.assertEqual(result["models"], ["B1", "B1_prime", "B2", script.CTX, script.CONTROL, script.ALIGNED, script.AVG])
        for metric in ("grid_crps", "upper_tail_twcrps"):
            self.assertEqual(sorted(result["means"][metric]), sorted(result["models"]))

    def test_the_run_is_deterministic(self):
        first, second = self.result(), self.result()
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_the_report_names_every_model_and_both_blocks(self):
        result = self.result()
        result.update({"panel_sha256": "p" * 64, "scratch_panel_sha256": "s" * 64, "declaration": "metadata/quantile_average_1113.json",
                       "notes": {"scored_decision_days": 130}, "declared_reading_rules": {}, "reading_rules": ["a sentence."], "not_run": {}})
        page = script.render_report(result)
        for name in result["models"]:
            self.assertIn(name, page)
        self.assertIn("Politis-White", page)
        self.assertIn("block 10", page)
        self.assertIn("at_or_above", page)
        self.assertIn("development data, not a verdict", page)


if __name__ == "__main__":
    unittest.main()
