"""The three market findings of #1177 (context for H5; development evidence, descriptive, not a forecast or a verdict).

`scripts/market_findings_1177.py` computes findings 1 and 3 from the published panel and writes
`docs/research/market-findings-1177/result.json`; finding 2 is read from `docs/research/state-calendar-1145/result.json`.
The plain page (`site/plain.html`, block `plain-market`) and the explorer (`site/index.html`, view N6) render all three from
those records and type no figure.

Recorded mutation (2026-10-23), for the lockbox guard `require_unlocked_rows` (a locked day must never be read, even to
describe it): deleting its `lockbox.require_unlocked(...)` call made
`test_a_locked_day_is_refused` fail with AssertionError ("LookAheadError not raised"). Restored, it passes.
"""

import importlib.util
import json
import re
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

import built_outputs
from panel_cache import published_build
from repo_model.splits import LookAheadError

built_outputs.ensure()  # the explorer is built, not committed (#928)

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("market_findings_1177", ROOT / "scripts" / "market_findings_1177.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


def row(day, spread, **values):
    base = {"quarter_end": 0.0, "tax_date": 0.0, "treasury_settlement_coupons": 0.0}
    base.update(values)
    return SimpleNamespace(date=day, spread_bps=spread, values=base)


def weekdays(first, count):
    out, day = [], first
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class StatsTests(unittest.TestCase):
    def test_stats_are_count_mean_median_and_the_share_strictly_above_the_line(self):
        got = script.stats([1.0, 2.0, 3.0, 10.0])
        self.assertEqual((got["n"], got["mean"], got["median"]), (4, 4.0, 2.5))
        self.assertEqual(got["share_above"], 0.25)
        self.assertEqual(script.stats([5.0])["share_above"], 0.0)  # exactly +5 bp is not above the line

    def test_an_empty_group_is_a_value_error(self):
        with self.assertRaises(ValueError):
            script.stats([])


class RoleTests(unittest.TestCase):
    def test_the_turn_of_a_month_that_is_not_a_quarters_last(self):
        self.assertEqual(script.turn_role(date(2019, 5, 31)), "last")
        self.assertEqual(script.turn_role(date(2019, 6, 3)), "first")
        self.assertIsNone(script.turn_role(date(2019, 5, 30)))  # the penultimate day is ordinary

    def test_a_quarters_last_month_is_not_in_this_table(self):
        self.assertIsNone(script.turn_role(date(2019, 3, 29)))
        self.assertIsNone(script.turn_role(date(2019, 4, 1)))

    def test_the_penultimate_day_and_the_mid_month_ordinary_day(self):
        self.assertTrue(script.is_penultimate(date(2019, 5, 30)))
        self.assertFalse(script.is_penultimate(date(2019, 3, 28)))  # a quarter-end month
        self.assertTrue(script.is_mid_month_ordinary(date(2019, 5, 14)))
        self.assertFalse(script.is_mid_month_ordinary(date(2019, 5, 21)))
        self.assertFalse(script.is_mid_month_ordinary(date(2019, 5, 31)))

    def test_the_role_table_groups_by_regime_and_role(self):
        days = [date(2019, 5, 30), date(2019, 5, 31), date(2019, 6, 3), date(2019, 6, 12), date(2019, 6, 13)]
        rows = [row(d, s) for d, s in zip(days, (0.0, 12.0, 8.0, 1.0, 3.0))]
        table = script.role_table(rows, lambda d: "2018-19")
        self.assertEqual(table["2018-19"]["last"]["mean"], 12.0)
        self.assertEqual(table["2018-19"]["first"]["mean"], 8.0)
        self.assertEqual(table["2018-19"]["penultimate"]["mean"], 0.0)
        self.assertEqual(table["2018-19"]["ordinary"]["mean"], 2.0)
        self.assertEqual(table["all"]["last"]["n"], 1)


class EpisodeTests(unittest.TestCase):
    def series(self):
        days = weekdays(date(2025, 9, 1), 80)
        rows = [row(d, 0.0) for d in days]
        by = {r.date: r for r in rows}
        by[date(2025, 9, 15)].spread_bps = 6.0
        by[date(2025, 9, 15)].values.update(tax_date=1.0, treasury_settlement_coupons=1.0)
        by[date(2025, 9, 16)].spread_bps = 7.0  # the same episode
        by[date(2025, 10, 8)].spread_bps = 9.0  # a second, with no calendar date near it
        return rows

    def test_a_new_episode_starts_after_more_than_the_gap_below_the_line(self):
        found = script.episodes(self.series(), threshold=5.0, gap=10, since=date(2020, 4, 1))
        self.assertEqual([e["start"] for e in found["episodes"]], ["2025-09-15", "2025-10-08"])

    def test_an_episode_is_near_a_known_date_within_one_business_day(self):
        first, second = script.episodes(self.series(), threshold=5.0, gap=10, since=date(2020, 4, 1))["episodes"]
        self.assertTrue(first["near"])
        self.assertIn("tax date", first["dates"])
        self.assertIn("mid-month settlement", first["dates"])
        self.assertFalse(second["near"])

    def test_episodes_before_the_window_are_counted_not_listed(self):
        rows = [row(d, 0.0) for d in weekdays(date(2020, 2, 3), 60)]
        rows[5].spread_bps = 9.0
        found = script.episodes(rows, threshold=5.0, gap=10, since=date(2020, 4, 1))
        self.assertEqual((found["episodes"], found["earlier"]), ([], 1))

    def test_the_base_rate_is_the_share_of_window_days_near_a_known_date(self):
        found = script.episodes(self.series(), threshold=5.0, gap=10, since=date(2020, 4, 1))
        self.assertTrue(0.0 < found["base_rate"] < 1.0)
        self.assertEqual(found["window_days"], len(self.series()))


class GuardTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_unlocked_rows([row(date(2026, 9, 4), 0.0)])

    def test_an_opened_day_is_read(self):
        script.require_unlocked_rows([row(date(2026, 9, 3), 0.0)])


class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(script.RECORD.read_text(encoding="utf-8"))
        build = published_build()
        cls.rebuilt = script.build_record(build["rows"], build["path"])

    def test_the_committed_record_is_what_the_panel_gives(self):
        self.assertEqual(self.record, self.rebuilt)

    def test_the_record_is_labelled_development_evidence(self):
        self.assertEqual(self.record["label"], "development data, not a verdict")

    def test_the_second_last_day_is_ordinary_and_the_turn_is_not(self):
        early = self.record["turn"]["2018-19"]
        self.assertGreater(early["last"]["mean"], early["ordinary"]["mean"] + 5)
        self.assertLess(abs(early["penultimate"]["mean"] - early["ordinary"]["mean"]), 5)

    def test_the_page_of_the_study_is_not_stale(self):
        self.assertEqual(script.PAGE.read_text(encoding="utf-8"),
                         script.render_page(self.record, script.load_state_calendar()))


class FindingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = script.load_findings()
        cls.calendar = json.loads((ROOT / "docs/research/state-calendar-1145/result.json").read_text(encoding="utf-8"))

    def test_finding_two_is_read_from_the_state_calendar_record(self):
        arm = self.calendar["term_effect_intervals"]["sc_s1_standardised"]
        for term in ("month_end", "settlement_coupon"):
            for regime, got in self.data["calendar"][term].items():
                self.assertEqual(got["mean"], arm[term][regime]["bp"]["mean"])
                self.assertEqual(got["interval"], arm[term][regime]["bp"]["interval"])

    def test_the_directives_own_figures_for_finding_two_hold(self):
        month_end = {k: round(v["mean"], 1) for k, v in self.data["calendar"]["month_end"].items()}
        self.assertEqual((month_end["2018-19"], month_end["2021-23"], month_end["2025-26"]), (5.8, 0.3, 4.3))
        coupon = {k: round(v["mean"], 1) for k, v in self.data["calendar"]["settlement_coupon"].items()}
        self.assertEqual((coupon["2018-19"], coupon["2021-23"], coupon["2025-26"]), (8.5, 0.5, 3.8))

    def test_the_directives_own_figures_for_finding_one_hold(self):
        early = self.data["turn"]["2018-19"]
        self.assertEqual(round(early["last"]["mean"], 1), 11.5)
        self.assertEqual(round(early["penultimate"]["mean"], 1), 0.3)

    def test_a_record_without_the_arm_is_a_value_error(self):
        broken = json.loads(json.dumps(self.calendar))
        broken["term_effect_intervals"].pop("sc_s1_standardised")
        with self.assertRaises(ValueError):
            script.calendar_terms(broken)


def block(text, name):
    match = re.search(r"<!-- generated: %s -->(.*?)<!-- end generated: %s -->" % (name, name), text, re.S)
    return match.group(1) if match else ""


class PagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = script.load_findings()
        cls.plain = block((ROOT / "site/plain.html").read_text(encoding="utf-8"), "plain-market")
        cls.explorer = (ROOT / "site/index.html").read_text(encoding="utf-8")

    def figures(self):
        early = self.data["turn"]["2018-19"]
        return ["%+.1f" % early["last"]["mean"], "%+.1f" % early["penultimate"]["mean"],
                "%+.1f" % self.data["calendar"]["month_end"]["2018-19"]["mean"],
                "%+.1f" % self.data["calendar"]["settlement_coupon"]["2025-26"]["mean"]]

    def test_the_plain_page_carries_the_section_with_its_three_findings(self):
        self.assertTrue(self.plain)
        for figure in self.figures():
            self.assertIn(figure, self.plain)
        self.assertEqual(self.plain.count("<h3"), 3)

    def test_the_plain_page_labels_it_development_evidence_and_defines_its_terms(self):
        lowered = self.plain.lower()
        self.assertIn("not a forecast", lowered)
        self.assertIn("development", lowered)
        self.assertIn("basis point", lowered)

    def test_the_explorer_carries_view_n6_with_the_same_figures(self):
        self.assertIn('<section id="n6"', self.explorer)
        view = self.explorer.split('<section id="n6"', 1)[1].split("</section>", 1)[0]
        for figure in self.figures():
            self.assertIn(figure, view)
        self.assertIn("not a forecast", view.lower())

    def test_the_explorer_nav_lists_the_view(self):
        self.assertIn('href="#n6"', self.explorer)

    def test_a_figure_changed_in_the_record_changes_the_rendered_page(self):
        altered = json.loads(json.dumps(self.data))
        altered["turn"]["2018-19"]["last"]["mean"] = 99.9
        text = "".join(script.plain_lines(altered, lambda path, label=None: label or path))
        self.assertIn("+99.9", text)


if __name__ == "__main__":
    unittest.main()
