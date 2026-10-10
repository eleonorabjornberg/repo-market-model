"""The desk-standard diagnostic (#481): its calendar, its windows, its lockbox guards and the findings it recorded.

`scripts/desk_standard_diagnostic.py` compares the declared availability of each input with the earliest public time its
primary source states, and measures what the leading models cannot see. The tests pin the pieces of logic a result rests
on (which decision first reads a value, how long a settlement is known before it settles, which onsets a cut-off window
leaves blind), the lockbox guards, and the findings in `docs/pivot/evidence/desk-standard/desk_standard.json`.

Recorded mutations for the read guards (the lockbox, `docs/decisions/lockbox.md`):

* `scored_days`: the comparison `days[-1] > LAST` was changed to `days[-1] > date(2099, 1, 1)`;
  `ScoredDayGuardTests.test_a_scored_day_after_the_last_read_day_is_refused` then failed with `AssertionError`
  (`LookAheadError not raised`). Restored.
* `read_panel`: the filter `r.date <= LAST` was dropped; `ScoredDayGuardTests.test_rows_after_the_last_read_day_are_dropped`
  then failed with `AssertionError` (a 2026 row in the result). Restored.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from datetime import date, time
from pathlib import Path
from unittest import mock

from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "pivot" / "evidence" / "desk-standard"


def _load():
    spec = importlib.util.spec_from_file_location("desk_standard_under_test", ROOT / "scripts" / "desk_standard_diagnostic.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ds = _load()


def _week(start: date, count: int) -> list:
    """`count` weekdays from `start`: a panel without holidays."""

    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day = date.fromordinal(day.toordinal() + 1)
    return days


class CalendarTests(unittest.TestCase):
    def setUp(self):
        self.calendar = ds.Calendar(_week(date(2024, 3, 4), 15))  # Monday 4 March 2024

    def test_a_value_public_at_the_decision_is_read_that_day_and_one_after_it_the_next(self):
        monday = date(2024, 3, 4)
        self.assertEqual(self.calendar.decision_index(monday, time(15, 0)), 0)
        self.assertEqual(self.calendar.decision_index(monday, time(16, 0)), 0)  # the registry's <= test
        self.assertEqual(self.calendar.decision_index(monday, time(16, 30)), 1)

    def test_a_value_public_on_a_day_off_the_panel_is_read_by_the_next_panel_day(self):
        saturday = date(2024, 3, 9)
        self.assertEqual(self.calendar.days[self.calendar.decision_index(saturday, time(9, 0))], date(2024, 3, 11))
        self.assertEqual(self.calendar.days[self.calendar.decision_index(saturday, time(23, 59))], date(2024, 3, 11))

    def test_the_h41_print_is_two_panel_days_later_than_it_could_be(self):
        wednesday = date(2024, 3, 6)
        block = {"available_time": "16:30", "days": 5, "unit": "calendar_days"}
        ours = ds._ours_instant(self.calendar, block, wednesday)  # Monday 11 March, 16:30
        true = ds._truth_instant(self.calendar, ds.TRUTH["h41_weekly"], wednesday)  # Thursday 7 March, 16:30
        self.assertEqual(ours, (date(2024, 3, 11), time(16, 30)))
        self.assertEqual(true, (date(2024, 3, 7), time(16, 30)))
        late = self.calendar.decision_index(*ours) - self.calendar.decision_index(*true)
        self.assertEqual(late, 2)  # read on Tuesday 12 March rather than Friday 8 March

    def test_a_business_day_lag_counts_panel_days(self):
        block = {"available_time": "16:00", "days": 1, "unit": "business_days"}
        friday = date(2024, 3, 8)
        self.assertEqual(ds._ours_instant(self.calendar, block, friday), (date(2024, 3, 11), time(16, 0)))


class SettlementLeadTests(unittest.TestCase):
    def test_lead_is_the_panel_days_from_the_announcement_to_the_settlement(self):
        calendar = ds.Calendar(_week(date(2024, 3, 4), 15))
        # announced Tuesday 5 March, settles Tuesday 12 March: five panel days
        self.assertEqual(ds.lead_days(calendar, date(2024, 3, 12), date(2024, 3, 5)), 5)
        # an announcement on a day off the panel counts from the next panel day
        self.assertEqual(ds.lead_days(calendar, date(2024, 3, 12), date(2024, 3, 9)), 1)

    def test_the_table_keeps_the_earliest_and_latest_announcement_of_a_settlement_date(self):
        calendar = ds.Calendar(_week(date(2024, 3, 4), 15))
        auctions = [
            {"issue_date": "2024-03-12", "announcemt_date": "2024-03-05", "auction_date": "2024-03-07", "security_type": "Bill"},
            {"issue_date": "2024-03-12", "announcemt_date": "2024-03-07", "auction_date": "2024-03-11", "security_type": "Bill"},
            {"issue_date": "2024-03-12", "announcemt_date": "2024-03-01", "auction_date": "2024-03-07", "security_type": "Note"},
            {"issue_date": "2024-03-09", "announcemt_date": "2024-03-01", "auction_date": "2024-03-05", "security_type": "Note"},  # off the panel
        ]
        table = ds.settlement_table(calendar, auctions)
        self.assertEqual(table["by_date"]["bill"][date(2024, 3, 12)], (date(2024, 3, 5), date(2024, 3, 7)))
        self.assertEqual(table["by_date"]["coupon"][date(2024, 3, 12)], (date(2024, 3, 1), date(2024, 3, 1)))
        self.assertEqual(table["auction_dates"]["bill"][date(2024, 3, 12)], (date(2024, 3, 7), date(2024, 3, 11)))
        self.assertEqual(table["issue_dates_off_the_panel"], 1)


class CutoffWindowTests(unittest.TestCase):
    def test_a_block_whose_training_window_holds_no_onset_is_blind(self):
        days = _week(date(2024, 1, 1), 120)
        calendar = ds.Calendar(days)
        scored = days[10:]
        onsets = {scored[50]}  # inside the third block (21 scored days each)
        blocks = ds.cutoff_windows(calendar, scored, onsets, 1)
        self.assertEqual([b["window_onsets"] for b in blocks][:4], [0, 0, 0, 1])
        self.assertEqual(blocks[0]["window_days"], 0)  # the first block has no window at all
        self.assertEqual(blocks[2]["first_day"], scored[42])

    def test_the_training_window_ends_the_business_day_before_the_first_decision(self):
        days = _week(date(2024, 1, 1), 120)
        calendar = ds.Calendar(days)
        scored = days[10:]
        h = 3
        blocks = ds.cutoff_windows(calendar, scored, set(), h)
        second = blocks[1]
        self.assertEqual(second["training_end"], days[calendar.position[scored[21]] - h - 1])


class ScoredDayGuardTests(unittest.TestCase):
    def _document(self, last: str) -> dict:
        return {"forecasts": {"calendar_climatology": {"5": {"2025-12-30": 0.1, last: 0.1}}}}

    def test_a_scored_day_after_the_last_read_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            ds.scored_days(self._document("2026-01-02"), 1)

    def test_the_last_read_day_itself_is_read(self):
        self.assertEqual(ds.scored_days(self._document("2025-12-31"), 1)[-1], date(2025, 12, 31))

    def test_rows_after_the_last_read_day_are_dropped(self):
        rows = [DailyObservation(date(2025, 12, 31), {}), DailyObservation(date(2026, 1, 2), {})]
        with mock.patch.object(ds, "load_daily_panel", return_value=rows):
            kept = ds.read_panel(Path("unused.csv"))
        self.assertEqual([r.date for r in kept], [date(2025, 12, 31)])


class WeekAverageProxyTests(unittest.TestCase):
    """#516: the reserves proxy is built on the H.4.1's own definition, a Thursday-to-Wednesday seven-calendar-day average.

    The page's first proxy compared Wednesday levels of the TGA and the reverse repo with changes in WRESBAL, a week average.
    """

    def test_a_week_average_carries_the_last_statement_over_days_without_one(self):
        wednesday = date(2024, 3, 6)
        daily = {date(2024, 2, 29): 10.0, date(2024, 3, 1): 20.0, date(2024, 3, 6): 90.0}  # Thu 29 Feb, Fri 1 Mar, Wed 6 Mar
        # Thu 10, Fri 20, Sat 20, Sun 20, Mon 20, Tue 20, Wed 90
        self.assertAlmostEqual(ds.week_average(daily, wednesday), (10 + 20 * 5 + 90) / 7)

    def test_a_week_with_no_statement_to_carry_is_not_averaged(self):
        self.assertIsNone(ds.week_average({date(2024, 3, 6): 1.0}, date(2024, 3, 6)))

    def test_a_series_that_starts_inside_the_week_is_not_averaged(self):
        self.assertIsNone(ds.week_average({date(2024, 3, 4): 1.0, date(2024, 3, 6): 2.0}, date(2024, 3, 6)))

    def _world(self):
        """Reserves are exactly 1000 less the week-average TGA and reverse repo; the daily series swing inside the week."""

        tga, rrp, reserves = {}, {}, {}
        day = date(2024, 1, 1)
        while day <= date(2024, 3, 27):
            if day.weekday() < 5:
                tga[day] = 300.0 + 40.0 * ((day.toordinal() * 7) % 5)
                rrp[day] = 100.0 + 30.0 * ((day.toordinal() * 3) % 4)
            day = date.fromordinal(day.toordinal() + 1)
        wednesday = date(2024, 1, 10)
        while wednesday <= date(2024, 3, 27):
            reserves[wednesday] = 1000.0 - ds.week_average(tga, wednesday) - ds.week_average(rrp, wednesday)
            wednesday = date.fromordinal(wednesday.toordinal() + 7)
        return reserves, tga, rrp

    def test_the_matched_proxy_is_exact_when_reserves_are_the_balance_sheet_residual(self):
        reserves, tga, rrp = self._world()
        result = ds.week_average_proxy(reserves, tga, rrp)["base_1_weeks_earlier"]
        self.assertGreater(result["wednesdays"], 8)
        self.assertAlmostEqual(result["mae_proxy_billions"], 0.0, places=9)
        self.assertAlmostEqual(result["correlation_of_changes"], 1.0, places=9)

    def test_the_level_proxy_on_the_same_data_is_not_exact(self):
        reserves, tga, rrp = self._world()
        result = ds.level_proxy(reserves, tga, rrp)["base_1_weeks_earlier"]
        self.assertGreater(result["mae_proxy_billions"], 1.0)


class EvidenceTests(unittest.TestCase):
    """The findings recorded in the evidence file. A change to the script or the inputs shows up here."""

    @classmethod
    def setUpClass(cls):
        cls.text = (EVIDENCE / "desk_standard.json").read_text(encoding="utf-8")
        cls.evidence = json.loads(cls.text)

    def test_no_2026_day_is_in_the_evidence(self):
        self.assertNotIn('"2026-', self.text)

    def test_the_27th_onset_is_the_first_scored_day_at_horizon_1(self):
        count = self.evidence["onset_count"]
        self.assertEqual(count["onsets_at_h1_not_at_every_horizon"], ["2018-06-29"])
        self.assertEqual(count["scored_first_day_by_horizon"]["1"], "2018-06-29")
        self.assertEqual(count["scored_first_day_by_horizon"]["2"], "2018-07-02")
        self.assertEqual(count["onsets_by_horizon"], {"1": 27, "2": 26, "3": 26, "4": 26, "5": 26})
        self.assertEqual(len(self.evidence["onsets_used_elsewhere"]), 26)

    def test_a_settlement_is_announced_days_before_it_settles(self):
        distribution = self.evidence["settlements"]["distribution"]
        for kind in ("bill", "coupon"):
            self.assertGreater(distribution[kind]["share_with_lead_at_least_2"], 0.99)
        known = self.evidence["settlements"]["onsets_known_by_horizon"]
        for h in ("2", "3", "4", "5"):
            self.assertEqual(known[h]["declared"], {"any": 0, "bill": 0, "coupon": 0})
            self.assertGreater(known[h]["announced_same_day"]["coupon"], 0)
        self.assertEqual(known["1"]["declared"], known["1"]["announced_same_day"])

    def test_the_h41_is_read_later_than_it_was_public(self):
        rows = {r["input"]: r for r in self.evidence["timeline"]}
        reserves = rows["H.4.1 reserves, WRESBAL (weekly)"]
        self.assertEqual(reserves["later_by_panel_days_most_common"], 2)
        self.assertEqual(set(reserves["later_by_panel_days"]), {"1", "2"})
        # the secured rates are read on the same decision as their 08:00 publication: no cost at a 16:00 decision
        self.assertEqual(rows["SOFR (daily)"]["later_by_panel_days"], {"0": rows["SOFR (daily)"]["reference_days"]})

    def test_the_risk_date_models_cannot_warn_the_off_calendar_onsets(self):
        blind = self.evidence["blind_spots"]
        self.assertEqual(len(blind["by_horizon"]["2"]["risk_date_models"]["onsets_off_the_risk_dates"]), 13)
        self.assertEqual(blind["by_horizon"]["1"]["cut_off_rule"]["onsets_in_a_refit_block_whose_training_window_holds_no_onset"], ["2018-06-29"])
        self.assertEqual(
            blind["by_horizon"]["2"]["cut_off_rule"]["onsets_in_a_refit_block_whose_training_window_holds_no_onset"],
            ["2018-11-15", "2018-11-30"],
        )
        self.assertEqual(len(blind["risk_date_models_cannot_warn_at_any_horizon"]), 6)

    def test_the_nowcast_figures_of_445_are_reproduced(self):
        nowcast = self.evidence["nowcast"]
        self.assertAlmostEqual(nowcast["reproduces_the_published_figures"]["naive_mae_bp"], 1.82, places=2)
        self.assertAlmostEqual(nowcast["reproduces_the_published_figures"]["primary_mae_bp"], 3.46, places=2)
        self.assertTrue(nowcast["alignment"]["naive_is_the_previous_panel_rows_spread_on_every_scored_day"])

    def test_the_sources_manifest_matches_the_saved_extracts(self):
        manifest = json.loads((EVIDENCE / "sources" / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["pages"])
        for page in manifest["pages"]:
            data = (EVIDENCE / "sources" / page["extract"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), page["extract_sha256"], page["name"])

    def test_every_quoted_source_is_a_saved_page(self):
        names = {p["name"] for p in json.loads((EVIDENCE / "sources" / "manifest.json").read_text(encoding="utf-8"))["pages"]}
        for row in self.evidence["timeline"]:
            source = row["true"]["source"]
            if source is not None:
                self.assertIn(source, names)


if __name__ == "__main__":
    unittest.main()
