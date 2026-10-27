"""`scripts/srf_cap_2026_1252.py` (#1252; H5 step 3, development tier): the SRF cap of #1241 on the 2026 development days, and the
check of whether the facility has capped SOFR and its 99th percentile since full allotment.

Written first, against the declaration. The line, the cap arms and the scoring helpers are #1241's and are tested in
`test_srf_line` and `test_srf_cap_1241_script`; the walk and the span guard are #1229's (`test_s3_2026_check_1222_script`). What these tests
pin: that the declaration names what the module has (window, periods, seed, series, the three arms and the primary of #1241); the exact
binomial interval; the arithmetic of a period's table on hand cases (strictly above on whole basis points, the gap quantiles, the days within
1 bp, the largest exceedances); the two rules the declaration states before any count (a change from full allotment only when the exact
intervals do not overlap, the ceiling pattern only when all four conditions hold); the new guard of this study, that the realised read
refuses a day after the last day; that the page opens with the one sentence, states the cross-check's missing days and ends with the marked
question; and a small run of `score` and `page` end to end on the fixture panel.

Recorded mutation (leakage guard, #1252): in `srf_cap_2026_1252.realised_days`, the call `s686.require_scored_days(...)` over the days read
was commented out. `RealisedReadTests.test_a_realised_day_after_the_last_day_is_refused` then failed with `AssertionError`
(`LookAheadError` not raised for a day on 2026-09-04); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from repo_model import policy_events as pe
from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("srf_cap_2026_1252", ROOT / "scripts" / "srf_cap_2026_1252.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["srf_cap_2026_1252"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


def days_of(values, line=10.0, first=date(2026, 3, 2)):
    """Hand days: consecutive dates from `first`, the given whole-bp values, one line."""

    return [{"date": date.fromordinal(first.toordinal() + i), "value": v, "line": line} for i, v in enumerate(values)]


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1252)
        self.assertEqual(script.SEED, 1252)
        self.assertIn("seed 1252", declaration["measures"]["3_score"])
        self.assertEqual(declaration["window"]["last_target_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["window"]["first_target_day"], script.FIRST_TARGET.isoformat())
        self.assertEqual((script.FIRST_TARGET, script.LAST_DAY), (date(2026, 1, 2), date(2026, 9, 3)))
        self.assertEqual(declaration["limits"]["arms"], 0)
        self.assertEqual(declaration["primary"]["arm"], script.PRIMARY)
        self.assertEqual([a["name"] for a in declaration["arms"]], ["sc_s3_robust", "srf_cap_m0", "srf_cap_m5", "srf_cap_m10"])
        self.assertEqual({a["name"]: a["margin_bp"] for a in declaration["arms"] if a["margin_bp"] is not None}, script.MARGINS)
        self.assertEqual(declaration["amendments"], [])

    def test_the_periods_are_the_three_the_directive_names_and_do_not_overlap(self):
        declaration = script.committed_declaration()
        named = [(p["name"], date.fromisoformat(p["first"]), date.fromisoformat(p["last"])) for p in declaration["periods"]]
        self.assertEqual(named, [(n, f, l) for n, f, l in script.PERIODS])
        self.assertEqual(named[0][1], date(2021, 7, 29))
        self.assertEqual(named[0][2], date(2025, 12, 10))
        self.assertEqual((named[1][1], named[1][2]), (date(2025, 12, 11), date(2025, 12, 31)))
        self.assertEqual((named[2][1], named[2][2]), (script.FIRST_TARGET, script.LAST_DAY))
        for before, after in zip(named, named[1:]):
            self.assertLess(before[2], after[1])

    def test_the_cap_machinery_is_1241s_unchanged(self):
        self.assertEqual(script.k.MARGINS, {"srf_cap_m0": 0.0, "srf_cap_m5": 5.0, "srf_cap_m10": 10.0})
        self.assertEqual(script.k.SEED, 1252)  # the shared paired-test and interval tasks read this module's seed
        self.assertEqual(script.k.S3, "sc_s3_robust")

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "srf_cap_2026_1252.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/srf_cap_2026_1252.json", "scripts/srf_cap_2026_1252.py", "direct"))


class ExactIntervalTests(unittest.TestCase):

    def test_no_day_above_has_the_closed_form_upper_bound(self):
        low, high = script.clopper_pearson(0, 10)
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 1 - 0.05 ** (1 / 10), places=9)

    def test_every_day_above_has_the_closed_form_lower_bound(self):
        low, high = script.clopper_pearson(10, 10)
        self.assertEqual(high, 1.0)
        self.assertAlmostEqual(low, 0.05 ** (1 / 10), places=9)

    def test_the_interval_solves_its_defining_equations_and_is_symmetric_at_a_half(self):
        low, high = script.clopper_pearson(5, 10)
        self.assertAlmostEqual(low + high, 1.0, places=9)
        self.assertAlmostEqual(script.binom_cdf(4, 10, low), 0.95, places=7)  # P(X >= 5 | low) = 0.05
        self.assertAlmostEqual(script.binom_cdf(5, 10, high), 0.05, places=7)
        self.assertTrue(0.2 < low < 0.25 and 0.75 < high < 0.8)

    def test_a_long_series_does_not_underflow(self):
        low, high = script.clopper_pearson(19, 1104)
        self.assertTrue(0.0 < low < 19 / 1104 < high < 0.05)

    def test_n_zero_is_refused(self):
        with self.assertRaises(ValueError):
            script.clopper_pearson(0, 0)


class PeriodTableTests(unittest.TestCase):

    def test_a_day_is_above_only_when_strictly_above_the_line_on_whole_basis_points(self):
        stats = script.period_stats(days_of([8, 9, 10, 11, 12]))
        self.assertEqual((stats["days"], stats["above"]), (5, 2))
        self.assertAlmostEqual(stats["share"], 0.4)

    def test_the_gap_quantiles_and_the_maximum(self):
        stats = script.period_stats(days_of([4, 6, 8, 10, 12]))  # gaps -6 -4 -2 0 +2
        self.assertEqual(stats["gap_median"], -2.0)
        self.assertEqual(stats["gap_max"], 2.0)
        self.assertAlmostEqual(stats["gap_p90"], 1.2)  # type 7: rank 0.9 * 4 = 3.6, between 0 and +2
        self.assertAlmostEqual(stats["gap_p99"], 1.92)

    def test_days_within_one_bp_count_both_sides_and_the_ones_at_or_below_separately(self):
        stats = script.period_stats(days_of([7, 9, 10, 11, 12]))  # gaps -3 -1 0 +1 +2
        self.assertEqual(stats["within_1bp"], 3)
        self.assertEqual(stats["within_1bp_at_or_below"], 2)

    def test_the_largest_exceedances_are_in_order_with_their_dates(self):
        stats = script.period_stats(days_of([12, 15, 10, 15, 9]))
        top = stats["largest"]
        self.assertEqual([x["excess"] for x in top], [5, 5, 2])
        self.assertEqual(top[0]["date"], "2026-03-03")  # ties go to the earlier date
        self.assertEqual(top[1]["date"], "2026-03-05")
        self.assertEqual(len(script.period_stats(days_of(list(range(30))))["largest"]), 10)

    def test_the_line_range_is_reported(self):
        days = days_of([1, 2], line=10.0) + days_of([3], line=20.0, first=date(2026, 4, 1))
        stats = script.period_stats(days)
        self.assertEqual((stats["line_min"], stats["line_max"]), (10.0, 20.0))

    def test_the_interval_is_the_exact_one(self):
        stats = script.period_stats(days_of([12] * 3 + [5] * 17))
        self.assertEqual(stats["interval"], list(script.clopper_pearson(3, 20)))

    def test_an_empty_period_is_refused(self):
        with self.assertRaises(ValueError):
            script.period_stats([])


class RuleTests(unittest.TestCase):
    """The two rules the declaration states before any count."""

    def stats(self, above, days, gap_max):
        return {"days": days, "above": above, "interval": list(script.clopper_pearson(above, days)), "gap_max": gap_max}

    def test_a_change_needs_intervals_that_do_not_overlap(self):
        before = self.stats(19, 1000, 6.0)
        self.assertFalse(script.changed(before, self.stats(2, 100, 1.0)))  # few days: intervals overlap
        self.assertTrue(script.changed(self.stats(50, 100, 3.0), self.stats(0, 100, 0.0)))  # 50% against 0% of 100 days
        self.assertFalse(script.changed(self.stats(5, 100, 3.0), self.stats(5, 100, 3.0)))

    def test_the_pattern_needs_all_four_conditions(self):
        sofr, p99 = self.stats(0, 100, -3.0), self.stats(0, 100, 0.0)
        self.assertTrue(script.ceiling_pattern(sofr, p99))
        self.assertFalse(script.ceiling_pattern(sofr, self.stats(1, 100, 2.0)))  # the 99th percentile crossed
        self.assertFalse(script.ceiling_pattern(sofr, self.stats(0, 100, -5.0)))  # it never reached the line
        self.assertFalse(script.ceiling_pattern(self.stats(1, 100, 1.0), p99))  # SOFR crossed
        self.assertFalse(script.ceiling_pattern(self.stats(0, 100, 0.0), p99))  # SOFR as high as the percentile
        self.assertTrue(script.ceiling_pattern(sofr, self.stats(0, 100, -1.0)))  # within 1 bp counts as reaching it


class RealisedReadTests(unittest.TestCase):
    """The guard this study adds: a realised read passes the scored-days check."""

    def register(self):
        def entry(ident, kind, announced, rate):
            return pe.PolicyEntry(ident, kind, "change", ident, __import__("datetime").datetime.combine(announced, __import__("datetime").time(14, 0)),
                                  "stated", announced, "https://example.org", True, {"rate_percent": rate})
        return [entry("s", "standing_repo", date(2025, 12, 10), 3.75), entry("i", "iorb_rate", date(2025, 12, 10), 3.65)]

    def test_a_realised_day_after_the_last_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.realised_days({date(2026, 9, 4): 8}, self.register(), date(2026, 9, 4), date(2026, 9, 4))

    def test_a_realised_day_inside_the_window_gets_the_line_in_force_that_day(self):
        rows = script.realised_days({date(2026, 3, 2): 8, date(2026, 3, 3): 11}, self.register(), date(2026, 3, 1), date(2026, 3, 31))
        self.assertEqual([(r["date"], r["value"], r["line"]) for r in rows], [(date(2026, 3, 2), 8, 10.0), (date(2026, 3, 3), 11, 10.0)])

    def test_only_the_days_of_the_period_are_read_and_a_day_before_the_facility_has_no_line(self):
        values = {date(2026, 2, 27): 1, date(2026, 3, 2): 2, date(2026, 4, 1): 3}
        rows = script.realised_days(values, self.register(), date(2026, 3, 1), date(2026, 3, 31))
        self.assertEqual([r["date"] for r in rows], [date(2026, 3, 2)])
        self.assertEqual(script.realised_days({date(2025, 6, 2): 1}, self.register(), date(2025, 6, 1), date(2025, 6, 30)), [])


class Percentile99Tests(unittest.TestCase):

    def test_the_percentile_is_read_from_the_snapshot_less_the_panels_iorb_in_whole_bp(self):
        import panel_cache

        panel = {r.date: r for r in __import__("repo_model.data", fromlist=["load_daily_panel"]).load_daily_panel(Path(panel_cache.published_build()["path"]))}
        values, missing = script.p99_minus_iorb(panel, script.SNAPSHOTS, script.BUILD_CUTOFF)
        day = date(2026, 9, 3)
        self.assertIn(day, values)
        self.assertIsInstance(values[day], int)
        self.assertEqual(values[day], 9)  # SOFR_p99 3.74 less IORB 3.65
        self.assertIn(date(2021, 8, 5), missing)  # a hole in the snapshot is dropped and listed, never filled
        self.assertNotIn(date(2021, 8, 5), values)


class CrossCheckTests(unittest.TestCase):

    def test_months_report_the_mean_and_the_maximum_with_its_date(self):
        values = {date(2026, 3, 2): 6, date(2026, 3, 3): 10, date(2026, 4, 1): 4}
        by_month = script.monthly_p99(values)
        self.assertEqual(by_month["2026-03"], {"days": 2, "mean": 8.0, "max": 10, "max_date": "2026-03-03"})
        self.assertEqual(by_month["2026-04"]["days"], 1)

    def test_the_october_days_are_missing_when_the_panel_ends_on_the_last_day(self):
        check = script.cross_check({date(2026, 9, 3): 9}, line_on_23_october=10.0)
        self.assertEqual(check["panel_last_day"], "2026-09-03")
        self.assertEqual(check["october_2026_days_in_panel"], 0)
        self.assertEqual(check["missing_from"], "2026-09-04")
        self.assertEqual(check["register_line_2026_10_23"], 10.0)


class AnswerTests(unittest.TestCase):

    def record(self, a, since, ceiling):
        def stats(above, days):
            return {"days": days, "above": above, "share": above / days, "interval": list(script.clopper_pearson(above, days)),
                    "gap_max": -1.0}
        return {"realised": {s: {"a": stats(*a[s]), "since": stats(*since[s])} for s in ("SOFR", "SOFR_p99")},
                "rules": {"changed": {s: script.changed(stats(*a[s]), stats(*since[s])) for s in a},
                          "ceiling_pattern": {"since": ceiling}}}

    def test_the_sentence_says_a_change_only_when_the_rule_holds(self):
        fewer = self.record({"SOFR": (400, 1000), "SOFR_p99": (500, 1000)}, {"SOFR": (0, 200), "SOFR_p99": (0, 200)}, True)
        text = script.answer_sentence(fewer)
        self.assertIn("changed how often", text)
        self.assertIn("firm ceiling", text)
        same = self.record({"SOFR": (19, 1000), "SOFR_p99": (30, 1000)}, {"SOFR": (2, 100), "SOFR_p99": (3, 100)}, False)
        text = script.answer_sentence(same)
        self.assertIn("do not show", text)
        self.assertNotIn("changed how often", text)
        self.assertEqual(text.count("\n"), 0)
        self.assertEqual(text.count(". "), 0)  # one sentence


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "srf-cap-2026-1252" / "result.json"
    PAGE = ROOT / "docs" / "research" / "srf-cap-2026-1252-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/srf_cap_2026_1252.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["primary"], script.PRIMARY)
        self.assertGreaterEqual(record["notes"]["first_target"], script.FIRST_TARGET.isoformat())
        self.assertLessEqual(record["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertIn(record["panel_sha256"], json.dumps(manifest))

    def test_the_two_scores_move_by_the_same_amount_because_the_cap_acts_only_above_zero(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        pooled = record["groups"]["pooled"]["all decision days"]
        for arm in script.CAPS:
            a = pooled["grid_crps"]["means"]
            b = pooled["upper_tail_twcrps"]["means"]
            self.assertAlmostEqual(a[script.S3] - a[arm], b[script.S3] - b[arm], places=9)

    def test_the_page_says_what_the_directive_requires(self):
        text = self.PAGE.read_text(encoding="utf-8")
        self.assertTrue(text.split("\n", 2)[2].lstrip().startswith("**Does the facility cap SOFR"))
        for phrase in ("already seen by #845", "a check, not evidence for a verdict or a choice", "current method", "#1221", "Lens C",
                       "mean-d bound", "Panel digest", "October 2026", "spillovers", "exact", "Question for Eleonora", "default"):
            self.assertIn(phrase, text)
        self.assertNotIn("GO #", text)

    def test_the_line_in_the_record_is_the_registers(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertTrue(record["line"])
        self.assertEqual(record["line"][0]["from"] >= script.FIRST_TARGET.isoformat(), True)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["srf_cap_2026_1252"] = script
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["score", "--panel", str(cls.panel_path), "--output", str(cls.output), "--draws", "20", "--reps", "5",
                     "--workers", "2", "--first", cls.FIRST])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_only_the_2026_development_days_are_scored(self):
        n = self.result["notes"]
        self.assertGreaterEqual(n["first_target"], "2026-01-02")
        self.assertLessEqual(n["last_target"], "2026-09-03")

    def test_every_cap_arm_is_scored_against_s3_and_the_benchmarks(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
        for arm in script.CAPS:
            self.assertEqual(sorted(cell["vs"][arm]), sorted(["B1", "B1_prime", "B2", script.S3]))
            self.assertIn("difference_interval", cell["vs"][arm][script.S3])

    def test_the_splits_the_directive_names_are_there_and_there_is_no_regime_split(self):
        groups = self.result["groups"]
        for split in ("pooled", "lead", "month", "pressure_day_type", "target_day_type"):
            self.assertIn(split, groups)
        self.assertNotIn("regime", groups)

    def test_the_realised_tables_have_both_series_and_every_period(self):
        for series in ("SOFR", "SOFR_p99"):
            entry = self.result["realised"][series]
            self.assertEqual(sorted(entry), ["a", "b", "c", "since"])
            for period in entry.values():
                self.assertEqual(len(period["interval"]), 2)
                self.assertLessEqual(period["interval"][0], period["share"])
        self.assertEqual(self.result["realised"]["SOFR"]["since"]["days"],
                         self.result["realised"]["SOFR"]["b"]["days"] + self.result["realised"]["SOFR"]["c"]["days"])

    def test_the_forecast_table_is_by_lead_with_the_binding_shares(self):
        pooled = self.result["forecast"]["splits"]["pooled"]
        self.assertEqual(sorted(pooled), ["1", "2", "3", "4", "5", "all"])
        self.assertIn("srf_cap_m0", pooled["all"]["binds"])

    def test_the_cross_check_says_the_october_days_are_missing(self):
        check = self.result["cross_check"]
        self.assertEqual(check["october_2026_days_in_panel"], 0)
        self.assertEqual(check["panel_last_day"], "2026-09-03")

    def test_no_day_after_the_last_scored_day_is_read(self):
        for series in self.result["realised"].values():
            for period in series.values():
                for x in period["largest"]:
                    self.assertLessEqual(x["date"], script.LAST_DAY.isoformat())

    def test_the_page_opens_with_the_one_sentence_and_ends_with_the_marked_question(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertTrue(text.split("\n", 2)[2].lstrip().startswith("**Does the facility cap SOFR"))
        self.assertIn("## Question for Eleonora", text)
        self.assertIn("**Options**", text)


if __name__ == "__main__":
    unittest.main()
