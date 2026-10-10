"""#471 review: `regime_recalibration.py tables` splits the judge row by regime and by pressure-day type.

The tables only re-read what the judge wrote (`splits.regime`, `splits.day_type`, `tiers.onset_warning.by_regime`);
nothing is computed anew.
"""

import importlib.util
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("regime_recalibration_script", ROOT / "scripts" / "regime_recalibration.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _interval(mean, low, high):
    return {"mean": mean, "interval": {"lower": low, "upper": high}}


def _cell(events):
    return {
        "days": 10,
        "events": events,
        "flags": {"recall": 0.5 if events else None, "alarms": 3, "hits": 1},
        "brier_difference_vs_climatology": _interval(0.01, -0.02, 0.04),
        "realised_minus_predicted": _interval(0.1, 0.05, 0.15),
    }


def _result():
    row = {"splits": {"regime": {"2018-19": _cell(4), "2021-23": _cell(0)}, "day_type": {"ordinary": _cell(7), "tax_date": _cell(2)}}}
    onset = {"by_regime": {"2018-19": {"onsets": 17, "onsets_flagged": 10}, "2021-23": {"onsets": 0, "onsets_flagged": 0}}}
    candidate = {"horizons": {"1": {"5": row}}, "tiers": {"onset_warning": {"lead_at_least_1": onset}}}
    return {"candidates": {"m": candidate}}


def _judged(flat_worst, weighted_worst, own_flat_count):
    """A judge result with one candidate: under the weighted rule the flat count and the weighted count differ."""

    near = {
        "onsets": 26,
        "onsets_flagged": 13,
        "worst_false_alarms_per_onset": flat_worst,
        "recall": {"mean": 0.5, "interval": {"lower": 0.3, "upper": 0.7}},
    }
    if weighted_worst is not None:
        near["worst_weighted_false_alarms_per_onset"] = weighted_worst
    verdict = {"tier_1_onset_warning": True, "tier_3_no_crying_wolf": False, "tier_5_week_ahead": False, "passes": False}
    return {"candidates": {"m": {"tiers": {"onset_warning": {"lead_at_least_1": near}}, "verdict": verdict}}}


class FalseAlarmColumnTests(unittest.TestCase):
    """#519: the column headed `(weighted count)` prints the weighted count, not the flat one.

    Recorded mutation: reading `worst_false_alarms_per_onset` in the weighted run (the original line) fails
    `test_the_weighted_rule_column_prints_the_weighted_count` with AssertionError.
    """

    def _row(self):
        flat = _judged(3.50, None, None)
        weighted = _judged(3.81, 1.38, None)
        lines = _script().judge_rows(flat, weighted, ["m"]).splitlines()
        header, row = lines[0], lines[2]
        return [c.strip() for c in header.strip("|").split("|")], [c.strip() for c in row.strip("|").split("|")]

    def test_the_weighted_rule_column_prints_the_weighted_count(self):
        header, row = self._row()
        cell = row[header.index("worst FA per onset (weighted count)")]
        self.assertEqual(cell, "1.38")

    def test_the_flat_rule_column_prints_the_flat_count(self):
        header, row = self._row()
        self.assertEqual(row[header.index("worst FA per onset (flat count)")], "3.50")

    def test_the_flat_count_under_the_weighted_cut_offs_is_labelled_as_such(self):
        header, row = self._row()
        self.assertEqual(row[header.index("worst FA per onset (flat count, weighted-rule cut-offs)")], "3.81")


class GroupingTests(unittest.TestCase):
    """#515: the recalibration's group is the declared regime, nothing (one pooled curve), or the as-of scarcity state."""

    class _Splits:
        def regime(self, day):
            return "2018-19" if day.year < 2020 else "2020"

    days = [date(2019, 5, 1), date(2020, 5, 1)]

    def test_the_regime_grouping_is_the_calendars_labels(self):
        self.assertEqual(_script().group_labels("regime", self.days, self._Splits(), {}), ["2018-19", "2020"])

    def test_no_grouping_is_one_group(self):
        self.assertEqual(_script().group_labels("none", self.days, self._Splits(), {}), ["all", "all"])

    def test_the_scarcity_grouping_is_the_state_of_the_day_and_unknown_when_there_is_none(self):
        states = {self.days[0]: 3.0}
        self.assertEqual(_script().group_labels("scarcity", self.days, self._Splits(), states), ["3", "unknown"])

    def test_an_unknown_grouping_is_refused(self):
        with self.assertRaises(ValueError):
            _script().group_labels("hindsight", self.days, self._Splits(), {})

    def test_the_variants_are_named_for_the_judge_candidates(self):
        self.assertEqual(_script().form_name("risk_gbm", "regime"), "risk_gbm+regime_recal")
        self.assertEqual(_script().form_name("risk_gbm", "none"), "risk_gbm+regime_recal_none")
        self.assertEqual(_script().form_name("risk_gbm", "scarcity"), "risk_gbm+regime_recal_scarcity")


class SplitTableTests(unittest.TestCase):
    def test_tier_1_by_regime_lists_onsets_flagged_for_both_rules(self):
        text = _script().onsets_by_regime(_result(), _result(), ["m"])
        self.assertIn("10 of 17", text)
        self.assertIn("0 of 0", text)

    def test_tier_3_by_day_type_carries_the_interval_and_the_event_count(self):
        text = _script().split_gap(_result(), ["m"], "day_type", "1")
        self.assertIn("+0.100 [+0.050, +0.150] (7)", text)
        self.assertIn("tax_date", text)

    def test_tier_5_brier_split_by_regime_and_day_type(self):
        text = _script().split_brier(_result(), ["m"], "1")
        for label in ("2018-19", "2021-23", "ordinary", "tax_date"):
            self.assertIn(label, text)
        self.assertIn("+0.010 [-0.020, +0.040] (4)", text)

    def test_a_group_with_no_event_is_marked_not_read(self):
        text = _script().split_brier(_result(), ["m"], "1")
        self.assertIn("no event", text)


if __name__ == "__main__":
    unittest.main()
