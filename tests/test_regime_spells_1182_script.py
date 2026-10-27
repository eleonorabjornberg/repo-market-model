"""The helpers of `scripts/regime_spells_1182.py` (#1182; H5 step 3, calm and stress spells on (s3), development tier).

Written after the script, which is measurement code. The as-of guards of the arms are recorded in `test_spread_mr_regime`, the scored
days pass `spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`), and
the runs and the base hit tables are `faster_scale_1153`'s. What these tests pin: the declared kill rule (independence off 0.000, or a
mean run cut by more than 15% of (s3)'s), the randomised tie rule (the same sequence as `above` when the tie probability is 0, and a
tie that does count when it is not), the reading on the mean-d bound (#1009), the declaration's names and constants against the
module's, the figure (well-formed, one polyline a panel, the episodes inside it), a small end-to-end run on a late subset of days, and
that the committed page is what the committed record gives.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

from repo_model import coverage_tests as ct
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_regime as rg

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("regime_spells_1182", ROOT / "scripts" / "regime_spells_1182.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["regime_spells_1182"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

DECLARATION = json.loads((ROOT / "metadata" / "regime_spells_1182.json").read_text(encoding="utf-8"))


def cell(p, runs):
    return {"pooled": {"independence": {"p_value": p}}, "runs": runs}


def hits_of(rows):
    out = {"rules": list(script.RULES), "rows": {}}
    for model, by_rule in rows.items():
        for rule, (ps, runs) in by_rule.items():
            out["rows"].setdefault(model, {}).setdefault(rule, {"band90": {}})["band90"] = {
                f"h={h}": cell(ps[h - 1], runs[h - 1]) for h in sp.HORIZONS}
    return out


class KillTests(unittest.TestCase):

    base_runs = [{"runs": 5, "hits": 10, "longest": 4}] * 5          # mean 2.0
    cut10 = [{"runs": 5, "hits": 9, "longest": 4}] * 5               # mean 1.8: a 10% cut
    cut20 = [{"runs": 5, "hits": 8, "longest": 3}] * 5               # mean 1.6: a 20% cut
    zero = [0.0] * 5

    def hits(self, base, arm):
        rows = {script.S3: {r: base for r in script.RULES}}
        for name in script.ARMS:
            rows[name] = {r: arm for r in script.RULES}
        return hits_of(rows)

    def test_the_kill_is_met_when_nothing_moves_against_s3(self):
        kill = script.kill_assessment(self.hits((self.zero, self.base_runs), (self.zero, self.base_runs)))
        self.assertTrue(kill["met"])
        self.assertEqual((kill["arms_off_zero"], kill["arms_cut_runs"]), ([], []))

    def test_a_p_value_off_zero_lifts_the_kill(self):
        hits = self.hits((self.zero, self.base_runs), (self.zero, self.base_runs))
        hits["rows"]["m2_markov"]["above"]["band90"]["h=2"]["pooled"]["independence"]["p_value"] = 0.0007
        kill = script.kill_assessment(hits)
        self.assertFalse(kill["met"])
        self.assertEqual(kill["arms_off_zero"], ["m2_markov"])

    def test_a_p_value_off_zero_under_the_randomised_rule_counts(self):
        hits = self.hits((self.zero, self.base_runs), (self.zero, self.base_runs))
        hits["rows"]["m3_markov_calendar"]["randomised"]["band90"]["h=5"]["pooled"]["independence"]["p_value"] = 0.2
        self.assertEqual(script.kill_assessment(hits)["arms_off_zero"], ["m3_markov_calendar"])

    def test_a_cut_of_ten_percent_is_not_enough_and_twenty_percent_is(self):
        small = script.kill_assessment(self.hits((self.zero, self.base_runs), (self.zero, self.cut10)))
        self.assertTrue(small["met"])
        self.assertEqual(small["arms_cut_runs"], [])
        self.assertAlmostEqual(small["run_cut"]["m1_episode_k3"], 0.10)
        big = script.kill_assessment(self.hits((self.zero, self.base_runs), (self.zero, self.cut20)))
        self.assertFalse(big["met"])
        self.assertEqual(big["arms_cut_runs"], list(script.ARMS))
        self.assertAlmostEqual(big["base_mean_run"], 2.0)

    def test_a_cut_of_exactly_the_threshold_is_not_more_than_it(self):
        exact = [{"runs": 5, "hits": 8.5, "longest": 3}] * 5         # mean 1.7: a cut of 15%
        kill = script.kill_assessment(self.hits((self.zero, self.base_runs), (self.zero, exact)))
        self.assertTrue(kill["met"], kill["run_cut"])


class RandomisedRuleTests(unittest.TestCase):

    def laws(self, n, level_value=5.0):
        return [[level_value + 0.1 * i for i in range(23)] for _ in range(n)]

    def test_with_a_zero_tie_probability_the_randomised_rule_is_the_above_rule(self):
        laws = self.laws(40)
        q95 = laws[0][sp.GRID.index(0.95)]
        outcomes = [q95, q95 + 0.2, q95 - 0.2, q95] * 10          # ties on every first and fourth day
        for kind in ("q95", "q05", "band90", "band98"):
            self.assertEqual(script.hit_sequence(outcomes, laws, kind, "randomised"), script.hit_sequence(outcomes, laws, kind, "above"))
        self.assertNotEqual(script.hit_sequence(outcomes, laws, "q95", "at_or_above"), script.hit_sequence(outcomes, laws, "q95", "above"))

    def test_a_tie_with_a_positive_probability_can_count_as_a_hit(self):
        hits = ct.randomised_hit_sequence([1.0, 1.0], [1.0, 1.0], [1.0, 1.0], [0.0, 0.5])
        self.assertEqual(hits, [1, 1])
        self.assertEqual(ct.randomised_hit_sequence([1.0], [1.0], [0.0], [0.0]), [0])

    def test_the_rules_are_the_two_deterministic_ones_and_the_randomised(self):
        self.assertEqual(script.RULES, tuple(ct.HIT_RULES) + ("randomised",))


class ReadingTests(unittest.TestCase):

    def row(self, skill, diff):
        return {"skill_interval": skill, "difference_interval": diff}

    def test_the_reading_is_the_mean_d_bound_not_the_skill_interval(self):
        self.assertEqual(script.reading(self.row([-0.01, 0.02], [0.001, 0.02])), "gain")
        self.assertEqual(script.reading(self.row([0.001, 0.02], [-0.01, 0.02])), "undecided")
        self.assertEqual(script.reading(self.row([0.001, 0.02], [-0.03, -0.001])), "loss")

    def test_an_undefined_comparison_has_no_reading_not_undecided(self):
        self.assertEqual(script.reading({"undefined": "x"}), "**no reading** (mean-d bound not computed: x)")
        self.assertEqual(script.reading(None), "undecided")


class DeclarationTests(unittest.TestCase):

    def test_the_constants_are_the_modules(self):
        self.assertEqual(script.constants_agree(DECLARATION), [])

    def test_a_changed_constant_is_found(self):
        changed = json.loads(json.dumps(DECLARATION))
        changed["arms"]["constants"]["min_state_pool"] = 30
        changed["arms"]["constants"]["episode_memory"] = [3, 4]
        self.assertEqual(script.constants_agree(changed), ["episode_memory", "min_state_pool"])

    def test_the_arms_are_the_declared_ones(self):
        self.assertEqual(set(DECLARATION["arms"]["listed_in_full"]), set(script.ARMS))
        self.assertEqual(script.models_of(), ("B1", "B1p", "B2", script.A, script.S3) + script.ARMS)

    def test_the_seed_is_declared_once(self):
        self.assertEqual(script.SEED, 1182)
        self.assertEqual(DECLARATION["scoring"]["paired"].count("seed 1182"), 1)

    def test_the_kill_threshold_is_the_issues(self):
        self.assertEqual(script.RUN_CUT, 0.15)
        self.assertIn("15%", DECLARATION["kill_rule"]["text"])

    def test_every_band_is_on_the_grid(self):
        for lo, hi in script.BANDS.values():
            self.assertIn(lo, sp.GRID)
            self.assertIn(hi, sp.GRID)

    def test_the_marked_episodes_are_inside_the_study_and_are_real_intervals(self):
        for ep in DECLARATION["figure"]["episodes"]:
            a, b = date.fromisoformat(ep["start"]), date.fromisoformat(ep["end"])
            self.assertLessEqual(a, b)
            self.assertLessEqual(b, script.LAST_DAY)


class FigureTests(unittest.TestCase):

    def record(self):
        days = [date(2025, 1, 1) + timedelta(days=i) for i in range(0, 300)]
        return {"diagnostics": {"stress_path": {
            "dates": [d.isoformat() for d in days],
            script.M2: [round(0.5 + 0.4 * ((i % 40) / 40 - 0.5), 5) for i in range(len(days))],
            script.M3: [round((i % 25) / 25, 5) for i in range(len(days))]}}}

    def test_the_figure_is_well_formed_with_one_line_and_the_marked_episodes_a_panel(self):
        episodes = [{"label": "Autumn <2025> & more", "start": "2025-10-14", "end": "2025-11-04"},
                    {"label": "Before", "start": "2019-09-16", "end": "2019-09-20"}]
        svg = script.stress_figure(self.record(), episodes)
        root = ET.fromstring(svg)
        ns = {"s": "http://www.w3.org/2000/svg"}
        self.assertEqual(len(root.findall("s:polyline", ns)), 2)
        self.assertEqual(len([r for r in root.findall("s:rect", ns)]), 2)           # the episode inside, shown once a panel
        self.assertIn("Autumn &lt;2025&gt; &amp; more", svg)
        self.assertNotIn("Before", svg)

    def test_every_point_is_inside_the_panels(self):
        svg = script.stress_figure(self.record(), [])
        root = ET.fromstring(svg)
        ns = {"s": "http://www.w3.org/2000/svg"}
        height = float(root.attrib["height"])
        for line in root.findall("s:polyline", ns):
            for pair in line.attrib["points"].split():
                x, y = (float(v) for v in pair.split(","))
                self.assertTrue(0 <= x <= float(root.attrib["width"]) and 0 <= y <= height, pair)


class SubsetRunTests(unittest.TestCase):
    """A late subset of days end to end: the walk, the tests, the page. Not the declared run."""

    @classmethod
    def setUpClass(cls):
        sys.modules["regime_spells_1182"] = script  # another test module may have re-registered the name (pickling by module name)
        import test_protocol_benchmarks as tpb

        cls.directory = tempfile.TemporaryDirectory()
        cls.out = Path(cls.directory.name) / "result.json"
        code = script.main(["score", "--panel", str(tpb.published_panel()["path"]), "--output", str(cls.out), "--first", "2025-11-03",
                            "--draws", "100", "--reps", "20", "--workers", "2"])
        assert code == 0
        cls.record = json.loads(cls.out.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_every_model_is_scored_on_the_same_days_and_the_record_is_labelled(self):
        r = self.record
        self.assertEqual(r["models"], list(script.models_of()))
        self.assertEqual(r["label"], "development, not a verdict")
        self.assertLessEqual(r["notes"]["last_target"], "2025-12-31")
        self.assertEqual(r["subset_from"], "2025-11-03")
        self.assertIn("coincides with `above`", r["randomised_tie_rule"])
        means = r["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]
        self.assertEqual(set(means), set(script.models_of()))

    def test_each_candidate_is_paired_against_the_benchmarks_and_the_other_comparator(self):
        vs = self.record["groups"]["pooled"]["all decision days"]["grid_crps"]["vs"]
        self.assertEqual(set(vs["m2_markov"]), {"B1", "B1p", "B2", script.S3, script.A})
        self.assertEqual(set(vs[script.S3]), {"B1", "B1p", "B2", script.A})
        self.assertEqual(set(vs[script.A]), {"B1", "B1p", "B2", script.S3})

    def test_the_three_hit_rules_are_tabled_and_the_randomised_one_is_the_strict_one(self):
        rows = self.record["hits"]["rows"]
        for model in (script.S3,) + script.ARMS:
            for kind in ("band90", "q95"):
                for h in sp.HORIZONS:
                    self.assertEqual(rows[model]["randomised"][kind][f"h={h}"], rows[model]["above"][kind][f"h={h}"])

    def test_the_stress_path_covers_the_scored_days_and_stays_a_probability(self):
        path = self.record["diagnostics"]["stress_path"]
        n = self.record["notes"]["scored_decision_days"]
        self.assertEqual(len(path["dates"]), n)
        for key in (script.M2, script.M3):
            self.assertEqual(len(path[key]), n)
            self.assertTrue(all(0.0 <= v <= 1.0 for v in path[key]))
        self.assertTrue(all(v in (0, 1) for v in path["m1_episode_k3"]))

    def test_the_groups_are_the_turn_types_in_force(self):
        """#1224: `Frame.day_type` reads `turn_days.reporting_day_type`, so the day-type groups are the turn labels."""

        reading = self.record["day_types"]
        self.assertEqual(reading["reading"], "turn_days")
        self.assertTrue(reading["turn_days_in_force"] and reading["b2_pool_in_force"])
        groups = set(self.record["groups"]["pressure_day_type"])
        self.assertTrue(groups <= set(script.TURN_DAYTYPE_ORDER), groups)
        self.assertFalse(groups & {"month_end", "quarter_end"}, groups)
        page = script.render(self.record, None, str(self.out))
        self.assertIn("split by the turn day types", page)
        self.assertIn("The first page's day-type splits used the retired labels", page)

    def test_the_page_shows_the_mean_d_bound_lens_cs_caveat_the_kill_rule_and_the_figure(self):
        page = script.render(self.record)
        self.assertIn("mean-d bound", page)
        self.assertIn("understated by about 2x", page)
        self.assertIn("The kill rule is", page)
        self.assertIn("regime-spells-1182/stress_probability.svg", page)
        self.assertIn("Development, not a verdict", page)
        self.assertIn("coincides with `above`", page)

    def test_the_page_command_writes_the_figure_beside_the_record(self):
        page = Path(self.directory.name) / "page.md"
        self.assertEqual(script.main(["page", "--score", str(self.out), "--output", str(page)]), 0)
        self.assertEqual(page.read_text(encoding="utf-8"), script.render(self.record, None, str(self.out)))
        ET.fromstring((self.out.parent / "stress_probability.svg").read_text(encoding="utf-8"))


class ThinPoolSwitchTests(unittest.TestCase):
    """`score --b2-thin-pool off` scores B2 as the first page's was (#1224), records it, and puts the switch back."""

    def test_off_is_recorded_and_restored(self):
        sys.modules["regime_spells_1182"] = script  # another test module may have re-registered the name (pickling by module name)
        import test_protocol_benchmarks as tpb
        from repo_model import b2_pool

        self.assertTrue(b2_pool.IN_FORCE)
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "result.json"
            code = script.main(["score", "--panel", str(tpb.published_panel()["path"]), "--output", str(out), "--first", "2025-11-03",
                                "--draws", "50", "--reps", "10", "--workers", "2", "--b2-thin-pool", "off"])
            self.assertEqual(code, 0)
            record = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(record["day_types"]["b2_pool_in_force"])
        self.assertTrue(record["day_types"]["turn_days_in_force"])
        self.assertTrue(b2_pool.IN_FORCE)


class DayTypeOrderTests(unittest.TestCase):

    def test_the_turn_labels_are_listed_in_the_turn_order_and_the_retired_ones_in_theirs(self):
        self.assertEqual(script.daytype_order({"turn", "ordinary"}), script.TURN_DAYTYPE_ORDER)
        self.assertEqual(script.daytype_order({"quarter_end", "month_end", "ordinary"}), script.LEGACY_DAYTYPE_ORDER)
        self.assertEqual(script._ordered("pressure_day_type", {"ordinary": 1, "year_end": 1, "turn": 1, "tax_date": 1}),
                         ["year_end", "turn", "tax_date", "ordinary"])
        self.assertEqual(script._ordered("pressure_day_type", {"ordinary": 1, "month_end": 1, "quarter_end": 1}),
                         ["quarter_end", "month_end", "ordinary"])


class ReSplitPageTests(unittest.TestCase):
    """The page of the re-split (#1224) is what its committed record gives, beside the first page, which is not edited."""

    directory = ROOT / "docs" / "research" / "regime-spells-1182-turn-types"
    page = ROOT / "docs" / "research" / "regime-spells-1182-turn-types-result.md"
    first = ROOT / "docs" / "research" / "regime-spells-1182" / "result.json"

    def setUp(self):
        if not (self.directory / "result.json").exists():
            self.skipTest("the record is not committed yet")
        self.record = json.loads((self.directory / "result.json").read_text(encoding="utf-8"))
        self.first_record = json.loads(self.first.read_text(encoding="utf-8"))

    def test_the_committed_page_is_what_the_committed_records_give(self):
        source = "docs/research/regime-spells-1182-turn-types/result.json"
        self.assertEqual(script.render(self.record, self.first_record, source), self.page.read_text(encoding="utf-8"))
        self.assertEqual(script.stress_figure(self.record, self.record["episodes"]),
                         (self.directory / "stress_probability.svg").read_text(encoding="utf-8"))

    def test_the_groups_are_the_turn_types_and_the_declaration_is_the_first_pages(self):
        self.assertEqual(self.record["day_types"]["reading"], "turn_days")
        self.assertEqual(set(self.record["groups"]["pressure_day_type"]) - set(script.TURN_DAYTYPE_ORDER), set())
        self.assertEqual(self.record["declaration"], self.first_record["declaration"])
        self.assertEqual(self.record["panel_sha256"], self.first_record["panel_sha256"])
        for key in ("seed", "draws", "reps"):
            self.assertEqual(self.record[key], self.first_record[key], key)
        self.assertNotIn("day_types", self.first_record)

    def test_the_pooled_kill_reading_is_the_first_pages(self):
        for key in ("met", "arms_off_zero", "arms_cut_runs"):
            self.assertEqual(self.record["kill"][key], self.first_record["kill"][key], key)

    def test_the_page_names_what_the_first_page_got_wrong(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("The first page's day-type splits used the retired labels", text)
        self.assertIn("#1221", text)
        self.assertIn("Readings that change.", text)


class PageTests(unittest.TestCase):

    record = ROOT / "docs" / "research" / "regime-spells-1182" / "result.json"
    page = ROOT / "docs" / "research" / "regime-spells-1182-result.md"
    figure = ROOT / "docs" / "research" / "regime-spells-1182" / "stress_probability.svg"

    def test_the_committed_page_is_what_the_committed_record_gives(self):
        if not self.record.exists():
            self.skipTest("the record is not committed yet")
        r = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(script.render(r), self.page.read_text(encoding="utf-8"))
        self.assertEqual(script.stress_figure(r, r["episodes"]), self.figure.read_text(encoding="utf-8"))

    def test_the_record_is_labelled_development_and_stops_at_the_last_day(self):
        if not self.record.exists():
            self.skipTest("the record is not committed yet")
        data = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(data["label"], "development, not a verdict")
        self.assertLessEqual(data["notes"]["last_target"], "2025-12-31")
        self.assertIsNone(data["subset_from"])
        self.assertEqual(data["seed"], 1182)


if __name__ == "__main__":
    unittest.main()
