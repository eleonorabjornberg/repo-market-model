"""#471 review: `regime_recalibration.py tables` splits the judge row by regime and by pressure-day type.

The tables only re-read what the judge wrote (`splits.regime`, `splits.day_type`, `tiers.onset_warning.by_regime`);
nothing is computed anew.
"""

import importlib.util
import unittest
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
