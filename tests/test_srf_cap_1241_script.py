"""The helpers of `scripts/srf_cap_1241.py` (#1241; H5 step 3, development tier).

Written first, against the declaration. The line and the cap are tested in `test_srf_line`; what these tests pin: that the declaration
names the arms the script has and the primary before any score; that the cap arms are (s3)'s forecast transformed and (s3) itself is
untouched; that the line a forecast reads is the one public at its decision instant (`lines_of`); that a cap arm equal to (s3) on every
day of a group reads "identical" and is not tested; the arithmetic of the realised and forecast tables on hand cases; that the page says
what the directive requires; and a small run of `score` and `page` end to end on a late subset of the fixture panel.

Recorded mutation (leakage guard, #1241): in `srf_cap_1241.lines_of`, `srf_line.srf_line_bps(register, decision_instant(d), ...)` mutated
to `srf_line.srf_line_bps(register, datetime.combine(frame.target(d, h), time(23, 59, 59)), ...)`, reading the line as of the end of the
target day. `test_the_line_a_forecast_reads_is_the_one_public_at_its_decision_instant` then failed with `AssertionError` (a cell whose
target day is the day after an announcement read 30.0 where 10.0 was public at the decision).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from unittest import mock
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model import policy_events as pe
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("srf_cap_1241", ROOT / "scripts" / "srf_cap_1241.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["srf_cap_1241"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


def row(skill_low, skill_high, d_low, d_high):
    return {"skill": 0.01, "skill_interval": [skill_low, skill_high], "difference": 0.01, "difference_interval": [d_low, d_high]}


def entry(ident, kind, announced, effective, rate):
    return pe.PolicyEntry(ident, kind, "change", ident, datetime.combine(announced, time(14, 0)), "stated", effective,
                          "https://example.org", True, {"rate_percent": rate})


class ReadingTests(unittest.TestCase):

    def test_a_reading_is_taken_from_the_mean_d_bound(self):
        self.assertEqual(script.verdict(row(0.01, 0.05, 0.001, 0.05)), "gain")
        self.assertEqual(script.verdict(row(0.01, 0.05, -0.001, 0.05)), "undecided")
        self.assertEqual(script.verdict(row(-0.05, 0.01, -0.05, -0.001)), "loss")
        self.assertEqual(script.reading_words(row(0.01, 0.05, -0.001, 0.05)), "undecided (skill interval: gain)")

    def test_a_group_the_cap_leaves_unchanged_reads_identical_and_not_a_loss_or_a_gain(self):
        same = {"identical": True, "days": 40}
        self.assertEqual(script.verdict(same), "identical to (s3)")
        self.assertEqual(script.skill_verdict(same), "identical to (s3)")
        self.assertEqual(script.reading_words(same), "identical to (s3)")
        self.assertEqual(script._fmt(same), "identical")

    def test_the_regime_tally_counts_identical_apart_from_undecided(self):
        regimes = list(script.REGIMES)
        groups = {"regime": {regimes[0]: {"grid_crps": {"vs": {"arm": {script.S3: {"identical": True, "days": 30}}}}},
                             regimes[1]: {"grid_crps": {"vs": {"arm": {script.S3: row(-1, 1, -0.1, 0.1)}}}},
                             regimes[2]: {"grid_crps": {"vs": {"arm": {script.S3: row(0.01, 0.05, 0.001, 0.05)}}}},
                             regimes[3]: {"grid_crps": {"vs": {"arm": {script.S3: {"undefined": "x", "days": 5}}}}}}}
        count = script.tally({"groups": groups}, "arm")
        self.assertEqual((count["identical"], count["undecided"], count["gain"], count["loss"], count["no reading"]), (1, 1, 1, 0, 1))


class PlanTests(unittest.TestCase):

    def test_the_pair_plan_is_the_benchmarks_and_s3_for_the_cap_arms(self):
        for arm in script.CAPS:
            self.assertEqual(script.pair_plan(arm), ["B1", "B1_prime", "B2", script.S3], arm)
        self.assertEqual(script.pair_plan(script.S3), ["B1", "B1_prime", "B2"])
        self.assertEqual(script.block_plan(script.S3), [])
        self.assertEqual(script.block_plan("srf_cap_m0"), [script.S3])

    def test_identical_series_are_found_exactly(self):
        d1, d2 = date(2025, 1, 2), date(2025, 1, 3)
        series = {script.S3: {d1: 1.0, d2: 2.0}, "cap": {d1: 1.0, d2: 2.0}}
        self.assertTrue(script._identical(series, "cap", [d1, d2]))
        series["cap"][d2] = 1.999
        self.assertFalse(script._identical(series, "cap", [d1, d2]))
        self.assertTrue(script._identical(series, "cap", [d1]))


class BlockTaskTests(unittest.TestCase):

    def test_a_cap_that_moves_a_few_days_leaves_a_block_row_that_says_it_is_undefined_not_a_crash(self):
        """The first full run died here: with a few days changed, a resample at the Politis-White block has no long-run variance and
        `paired_tests` raised `ProtocolError` out of the worker pool."""

        days = [date(2022, 1, 3) + timedelta(days=i) for i in range(300)]
        s3 = {d: 1.0 + 0.01 * (i % 7) for i, d in enumerate(days)}
        cap = dict(s3)
        for d in days[100:103]:
            cap[d] = s3[d] + 0.5
        saved = dict(script._STATE)
        try:
            script._STATE.update(series={("decision", "grid_crps"): {"B1": s3, "srf_cap_m0": cap, script.S3: s3}}, draws=200, reps=5)
            ident, out = script._block_task(("pooled", "all decision days", "decision", "grid_crps", "srf_cap_m0", tuple(days)))
        finally:
            script._STATE.clear()
            script._STATE.update(saved)
        self.assertEqual(ident, ("pooled", "all decision days", "grid_crps", "srf_cap_m0"))
        entry = out[script.S3]
        self.assertIn("at_block", entry)
        self.assertTrue("row" in entry or "undefined" in entry)

    def test_a_group_the_cap_leaves_unchanged_has_no_block_entry(self):
        days = [date(2022, 1, 3) + timedelta(days=i) for i in range(30)]
        s3 = {d: 1.0 + 0.01 * i for i, d in enumerate(days)}
        saved = dict(script._STATE)
        try:
            script._STATE.update(series={("decision", "grid_crps"): {"srf_cap_m0": dict(s3), script.S3: s3}}, draws=20, reps=5)
            _ident, out = script._block_task(("pooled", "all decision days", "decision", "grid_crps", "srf_cap_m0", tuple(days)))
        finally:
            script._STATE.clear()
            script._STATE.update(saved)
        self.assertEqual(out, {script.S3: None})


class UnstudentizedTests(unittest.TestCase):

    def setUp(self):
        self.days = [date(2022, 1, 3) + timedelta(days=i) for i in range(300)]
        self.s3 = {d: 1.0 + 0.01 * (i % 7) for i, d in enumerate(self.days)}
        self.cap = dict(self.s3)
        for d in self.days[100:103]:
            self.cap[d] = self.s3[d] + 0.5  # the cap scores worse on three days only
        self.saved = dict(script._STATE)
        script._STATE.update(series={("decision", "grid_crps"): {"B1": self.s3, "B1_prime": self.s3, "B2": self.s3,
                                                                   "srf_cap_m0": self.cap, script.S3: self.s3}}, draws=200, reps=50)

    def tearDown(self):
        script._STATE.clear()
        script._STATE.update(self.saved)

    def test_the_direction_of_mean_d_is_shown_where_the_studentized_bound_cannot_be_computed(self):
        """d = S((s3)) - S(cap), positive favours the cap: a cap that scores worse on three days has a negative mean d."""

        out = script.unstudentized_mean_d(script._STATE["series"][("decision", "grid_crps")], "srf_cap_m0", self.days)
        self.assertAlmostEqual(out["mean_d"], -1.5 / 300, places=12)
        self.assertEqual(out["days"], 300)
        self.assertLessEqual(out["interval"][0], out["interval"][1])
        self.assertLessEqual(out["interval"][1], 0.0 + 1e-12)

    def test_a_row_with_no_variance_resamples_has_a_bound_and_the_dropped_count_and_no_unstudentized_part(self):
        """#1239 (her ruling on #1236): a resample with no long-run variance is dropped and counted, so a cap that moves three days
        has a mean-d bound, not `undefined`. The row keeps `dropped_resamples` and `draws`, takes a reading, and needs no unstudentized part."""

        _ident, out = script._pairs_task(("pooled", "all decision days", "decision", "grid_crps", "srf_cap_m0", tuple(self.days)))
        row = out[script.S3]
        self.assertNotIn("undefined", row)
        self.assertNotIn("unstudentized", row)
        self.assertGreater(row["dropped_resamples"], 0)
        self.assertEqual(row["draws"], 200)
        self.assertLess(row["difference"], 0.0)
        text = script._fmt(row)
        self.assertIn(f"({row['dropped_resamples']} of 200 resamples dropped)", text)
        self.assertNotIn("studentized bound not computed", text)
        self.assertFalse(script.verdict(row).startswith("**no reading**"))

    def test_a_row_that_is_still_undefined_carries_the_unstudentized_interval_and_no_reading(self):
        """Undefined now means the series itself, or every resample, has no long-run variance (#1239); the row keeps the unstudentized
        interval of mean d beside it and takes no reading."""

        undefined = {"undefined": "every one of the 200 resamples has no long-run variance; it cannot be studentized", "days": 300}
        with mock.patch.object(script.s761, "run_pairs", side_effect=lambda benchmarks, *a, **k: {n: dict(undefined) for n in benchmarks}):
            _ident, out = script._pairs_task(("pooled", "all decision days", "decision", "grid_crps", "srf_cap_m0", tuple(self.days)))
        row = out[script.S3]
        self.assertIn("undefined", row)
        self.assertIn("unstudentized", row)
        text = script._fmt(row)
        self.assertIn("unstudentized d -0.005", text)
        self.assertIn("studentized bound not computed", text)
        self.assertTrue(script.verdict(row).startswith("**no reading**"))

    def test_the_cell_of_a_defined_row_is_the_protocols_and_has_no_unstudentized_part(self):
        self.assertNotIn("unstudentized", script._fmt(row(0.01, 0.05, 0.001, 0.05)))


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_the_arms_and_the_primary_the_script_has(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(script.committed_declaration()["issue"], 1241)
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.S3] + list(script.CAPS))
        self.assertEqual({a["name"]: a["margin_bp"] for a in declaration["arms"][1:]}, script.MARGINS)
        self.assertEqual(sorted(script.MARGINS.values()), [0.0, 5.0, 10.0])
        self.assertEqual(declaration["primary"]["arm"], script.PRIMARY)
        self.assertEqual(script.PRIMARY, "srf_cap_m0")
        self.assertEqual(declaration["limits"]["arms"], len(script.CAPS))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["scoring"]["reading"].count("#1009"), 1)
        self.assertIn("seed 1241", declaration["measures"]["3_score"])
        self.assertEqual(script.SEED, 1241)
        self.assertEqual(declaration["amendments"], [])

    def test_s3_is_the_candidate_of_1145_unchanged(self):
        self.assertEqual(script.S3, "sc_s3_robust")
        self.assertEqual(sc.ARMS[2].name, script.S3)
        self.assertTrue(sc.ARMS[2].robust)
        self.assertFalse(sc.ARMS[2].interact)

    def test_the_cap_is_one_declared_margin_per_arm_and_no_other_value_is_used(self):
        self.assertEqual(script.CAPS, ("srf_cap_m0", "srf_cap_m5", "srf_cap_m10"))
        self.assertEqual([script.MARGINS[a] for a in script.CAPS], [0.0, 5.0, 10.0])


class CapTests(unittest.TestCase):
    Q = [-2.0, 1.0, 4.0, 9.0, 12.0, 20.0]

    def test_the_cap_arms_are_s3_with_each_cell_clipped_and_s3_is_not_touched(self):
        forecasts = {date(2025, 6, 2): {1: list(self.Q), 2: list(self.Q)}}
        lines = {(date(2025, 6, 2), 1): 10.0, (date(2025, 6, 2), 2): None}
        out = script.capped(forecasts, lines, 0.0)
        self.assertEqual(out[date(2025, 6, 2)][1], [-2.0, 1.0, 4.0, 9.0, 10.0, 10.0])
        self.assertEqual(out[date(2025, 6, 2)][2], self.Q)  # no line: unchanged
        self.assertEqual(forecasts[date(2025, 6, 2)][1], self.Q)

    def test_the_ceiling_rises_with_the_margin_and_the_capped_forecast_is_never_below_s3_at_a_lower_margin(self):
        forecasts = {date(2025, 6, 2): {1: list(self.Q)}}
        lines = {(date(2025, 6, 2), 1): 10.0}
        tight, mid, wide = (script.capped(forecasts, lines, m)[date(2025, 6, 2)][1] for m in (0.0, 5.0, 10.0))
        for a, b, c_, q in zip(tight, mid, wide, self.Q):
            self.assertLessEqual(a, b)
            self.assertLessEqual(b, c_)
            self.assertLessEqual(c_, q)


class LineTests(unittest.TestCase):

    class Frame:
        """Business days around a change announced on a Wednesday at 14:00 and effective on the Thursday."""

        def __init__(self):
            self.dates = [date(2022, 3, 14) + timedelta(days=i) for i in range(10) if (date(2022, 3, 14) + timedelta(days=i)).weekday() < 5]
            self.position = {d: i for i, d in enumerate(self.dates)}
            self.days = [self.dates[0], self.dates[1], self.dates[2]]

        def target(self, d, h):
            return self.dates[self.position[d] + h]

    def test_the_line_a_forecast_reads_is_the_one_public_at_its_decision_instant(self):
        register = pe.known_entries([
            entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 0.25),
            entry("iorb-0", "iorb_rate", date(2021, 6, 16), date(2021, 6, 17), 0.15),
            entry("srf-1", "standing_repo", date(2022, 3, 16), date(2022, 3, 17), 0.45),
        ], datetime(2030, 1, 1))
        frame = self.Frame()
        lines = script.lines_of(frame, register)
        tuesday, wednesday, monday = date(2022, 3, 15), date(2022, 3, 16), date(2022, 3, 14)
        thursday = date(2022, 3, 17)
        self.assertEqual(frame.target(tuesday, 2), thursday)
        # Tuesday's decision does not know Wednesday's announcement: the Thursday target reads 10; Wednesday's decision does: 30
        self.assertAlmostEqual(lines[(tuesday, 2)], 10.0, places=6)
        self.assertAlmostEqual(lines[(wednesday, 1)], 30.0, places=6)
        self.assertAlmostEqual(lines[(monday, 3)], 10.0, places=6)
        # the ex post line on the target day knows it, and is not what a forecast could read
        self.assertAlmostEqual(script.realised_line(register, thursday), 30.0, places=6)

    def test_the_line_segments_are_the_runs_of_the_value(self):
        register = pe.known_entries([
            entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 0.25),
            entry("iorb-0", "iorb_rate", date(2021, 6, 16), date(2021, 6, 17), 0.15),
            entry("srf-1", "standing_repo", date(2022, 3, 16), date(2022, 3, 17), 0.45),
        ], datetime(2030, 1, 1))
        frame = self.Frame()
        frame.days = [frame.dates[0]]
        segments = script.line_segments(register, frame)
        self.assertEqual([(s["bp"], s["days"]) for s in segments], [(10.0, 2), (30.0, 3)])


class TableTests(unittest.TestCase):

    def test_the_99th_percentile_is_linear_between_order_statistics(self):
        self.assertEqual(script.quantile7([1.0, 2.0, 3.0, 4.0, 5.0], 0.5), 3.0)
        self.assertAlmostEqual(script.quantile7([0.0, 10.0], 0.99), 9.9)
        self.assertEqual(script.quantile7([7.0], 0.99), 7.0)
        with self.assertRaises(ValueError):
            script.quantile7([], 0.5)

    def test_the_realised_table_counts_a_day_above_only_on_whole_basis_points_strictly(self):
        base = date(2025, 10, 1)
        rows = [{"date": base + timedelta(days=i), "spread": s, "line": 10.0, "excess": round(s) - 10.0, "regime": "2025-26", "type": "ordinary"}
                for i, s in enumerate([9.0, 10.0, 10.4, 11.0, 32.0])]
        jobs = []
        out = script.realised_tables(rows, jobs)["pooled"]
        self.assertEqual((out["days"], out["above"]), (5, 2))  # 10.4 reads 10 on whole basis points: on the line, not above it
        self.assertEqual(out["largest"][0]["excess"], 22.0)
        self.assertEqual(out["excess_max"], 22.0)
        self.assertEqual(jobs, [])  # under 20 days: no interval
        longer = [dict(rows[0], date=base + timedelta(days=i)) for i in range(25)]
        more = []
        script.realised_tables(longer, more)
        self.assertEqual(len([j for j in more if j[0] == "interval"]), 3)  # pooled, the regime, the type

    def test_the_forecast_table_counts_a_level_above_the_line_strictly(self):
        grid = sp.GRID
        q = [0.0] * len(grid)
        for i, p in enumerate(grid):
            q[i] = 10.0 if p <= 0.9 else 12.0  # exactly on the line up to the 0.9 level, above it beyond
        cells = [{"d": date(2025, 6, 2), "h": 1, "line": 10.0, "q": q, "regime": "2025-26", "type": "ordinary"}]
        out = script.forecast_tables(cells, [])
        shares = out["splits"]["pooled"]["1"]["share_above"]
        self.assertEqual(shares["0.9"], 0.0)
        self.assertEqual(shares["0.95"], 1.0)
        binds = out["splits"]["pooled"]["all"]["binds"]
        self.assertEqual((binds["srf_cap_m0"]["q95"], binds["srf_cap_m5"]["q95"], binds["srf_cap_m0"]["q99"], binds["srf_cap_m5"]["q99"]), (1.0, 0.0, 1.0, 0.0))


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "srf-cap-1241" / "result.json"
    PAGE = ROOT / "docs" / "research" / "srf-cap-1241-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_not_a_subset(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/srf_cap_1241.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["primary"], script.PRIMARY)
        self.assertLessEqual(record["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertIn(record["panel_sha256"], json.dumps(manifest))

    def test_a_cap_arm_is_identical_to_s3_on_the_regimes_before_the_facility(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for regime in ("2018-19", "2020"):
            entry_ = record["groups"]["regime"].get(regime)
            if entry_ is None:
                continue
            for arm in script.CAPS:
                self.assertTrue(entry_["grid_crps"]["vs"][arm][script.S3].get("identical"), (regime, arm))
                self.assertEqual(entry_["grid_crps"]["means"][arm], entry_["grid_crps"]["means"][script.S3])

    def test_the_two_scores_move_by_the_same_amount_because_the_cap_acts_only_above_zero(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        checked = 0
        for split, labels in record["groups"].items():
            for label, entry_ in labels.items():
                if "grid_crps" not in entry_:
                    continue
                for arm in script.CAPS:
                    one = entry_["grid_crps"]["vs"].get(arm, {}).get(script.S3, {})
                    two = entry_["upper_tail_twcrps"]["vs"].get(arm, {}).get(script.S3, {})
                    if "difference" in one and "difference" in two:
                        self.assertAlmostEqual(one["difference"], two["difference"], places=9, msg=(split, label, arm))
                        checked += 1
        self.assertGreater(checked, 0)

    def test_the_line_in_the_record_is_the_registers_and_starts_with_the_facility(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(record["line"][0]["from"], "2021-07-29")
        for segment in record["line"]:
            self.assertAlmostEqual(segment["bp"], 10.0, places=6)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["srf_cap_1241"] = script  # another test module may have re-registered the name (pickling by module name)
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["score", "--draws", "20", "--reps", "5", "--workers", "2", "--first", cls.FIRST, "--panel", str(cls.panel_path),
                     "--output", str(cls.output)])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_cap_arm_is_scored_against_s3_and_the_benchmarks(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"]), sorted(script.ARMS))
        for arm in script.CAPS:
            for name in ("B1", "B1_prime", "B2", script.S3):
                self.assertIn(name, cell["vs"][arm], (arm, name))
        self.assertNotIn(script.S3, cell["vs"][script.S3])
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_rows_carry_the_mean_d_interval_beside_the_skill_interval(self):
        one = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]["vs"]["srf_cap_m0"][script.S3]
        self.assertIn("skill_interval", one)
        self.assertIn("difference_interval", one)

    def test_the_splits_the_directive_names_are_there(self):
        groups = self.result["groups"]
        self.assertIn("pooled", groups)
        self.assertIn("srf_days", groups["facility"])
        self.assertEqual(sorted(groups["lead"]), [f"h={h}" for h in sp.HORIZONS])
        self.assertIn("2025-26", groups["regime"])
        self.assertIn("ordinary", groups["pressure_day_type"])
        self.assertIn("ordinary", groups["target_day_type"])

    def test_the_realised_and_forecast_measures_are_pooled_by_regime_and_by_pressure_day_type(self):
        realised = self.result["realised"]
        for key in ("pooled", "regime/2025-26", "pressure_day_type/ordinary"):
            self.assertIn(key, realised)
        self.assertEqual(realised["pooled"]["days"], sum(realised[k]["days"] for k in realised if k.startswith("regime/")))
        self.assertLessEqual(realised["pooled"]["above"], realised["pooled"]["days"])
        self.assertGreaterEqual(realised["pooled"]["excess_max"], realised["pooled"]["excess_p99"])
        forecast = self.result["forecast"]
        for lead in ("all", "1", "2", "3", "4", "5"):
            self.assertIn(lead, forecast["splits"]["pooled"])
        shares = forecast["splits"]["pooled"]["all"]["share_above"]
        values = [shares[str(p)] for p in forecast["levels"]]
        self.assertEqual(values, sorted(values))  # a higher level is above the line at least as often

    def test_the_calibration_is_pooled_and_on_the_facility_cells_for_every_model(self):
        self.assertIn("pooled/all cells", self.result["q95"])
        self.assertIn("facility/srf cells", self.result["q95"])
        for model in script.MODELS:
            entry_ = self.result["q95"]["pooled/all cells"][model]
            for rule in script.RATES:
                self.assertTrue(0.0 <= entry_[rule]["rate"] <= 1.0, (model, rule))
                self.assertEqual(len(entry_[rule]["interval"]), 2)
            self.assertLessEqual(entry_["hit_above"]["rate"], entry_["hit_at_or_above"]["rate"])

    def test_the_cap_can_only_raise_the_q95_exceedance_rate(self):
        pooled = self.result["q95"]["facility/srf cells"]
        # clipping a quantile down can only move the outcome from below it to above it
        self.assertGreaterEqual(pooled["srf_cap_m0"]["hit_above"]["rate"], pooled[script.S3]["hit_above"]["rate"])

    def test_the_politis_white_block_is_against_s3(self):
        pooled = self.result["politis_white"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(pooled), sorted(script.CAPS))
        self.assertEqual(sorted(pooled["srf_cap_m0"]), [script.S3])

    def test_no_day_after_the_last_scored_day_is_read(self):
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["subset_from"], self.FIRST)

    def test_the_page_states_what_the_directive_requires(self):
        text = self.page.read_text(encoding="utf-8")
        for needle in ("Development data, not a verdict", "Lens C", "mean d", "B1' (#960)", "Politis-White", "the primary, named in the declaration",
                       "before any score", "## 1. Realised", "## 2. Forecast", "## 3. Score", "pressure-day type", "regime",
                       "understated about 2x", "Nothing is adopted"):
            self.assertIn(needle.lower(), text.lower(), needle)

    def test_the_page_ends_with_the_marked_question_its_options_and_a_default(self):
        text = self.page.read_text(encoding="utf-8")
        tail = text[text.index("## Question for Eleonora"):]
        self.assertIn("Nothing is adopted here and no claim changes", tail)
        for option in ("1. **Keep (s3)", "2. **Take a cap", "3. **Ask for a further step"):
            self.assertIn(option, tail)
        self.assertIn("(default)", tail)
        self.assertEqual(text.count("## Question for Eleonora"), 1)


if __name__ == "__main__":
    unittest.main()
