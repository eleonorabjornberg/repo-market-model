"""The before-and-after table of #586 reads tier 1 on the pooled false-alarm count, with the earlier counting beside it (#603).

The judge's tier 1 limit is read on the false alarms pooled over the leads (ruling of 10 October 2026, #509); the worst single lead
is only reported. `own_leg_compare` printed the worst single lead alone, so a reader could not see the figure the verdict was read on.
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("own_leg_compare_pooled_test", ROOT / "scripts" / "own_leg_compare.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


def _candidate(pooled, worst, weighted):
    one = {
        "onsets": 26,
        "onsets_flagged": 19,
        "recall": {"mean": 0.7, "interval": {"lower": 0.5, "upper": 0.9}},
        "worst_false_alarms_per_onset": worst + 1,
        "pooled_false_alarms_per_onset": pooled + 1,
    }
    if weighted:
        one.update(
            weighted_miss_applied=True,
            worst_weighted_false_alarms_per_onset=worst,
            pooled_weighted_false_alarms_per_onset=pooled,
        )
    return {
        "tiers": {"onset_warning": {"lead_at_least_1": one}},
        "verdict": {"tier_1_onset_warning": False, "tier_3_no_crying_wolf": False, "tier_5_week_ahead": False, "passes": False},
    }


class RowTests(unittest.TestCase):
    def test_the_row_carries_the_pooled_count_the_weighted_rule_reads(self):
        row = SCRIPT._row(_candidate(pooled=3.46, worst=1.64, weighted=True))
        self.assertEqual(row["tier1_pooled_false_alarms"], 3.46)
        self.assertEqual(row["tier1_worst_false_alarms"], 1.64)

    def test_the_row_carries_the_flat_pooled_count_when_the_rule_is_not_applied(self):
        row = SCRIPT._row(_candidate(pooled=3.46, worst=1.64, weighted=False))
        self.assertEqual(row["tier1_pooled_false_alarms"], 4.46)
        self.assertEqual(row["tier1_worst_false_alarms"], 2.64)

    def test_the_table_prints_both_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "judge.json"
            path.write_text(json.dumps({"candidates": {"r": _candidate(3.46, 1.64, True)}}))
            out = Path(tmp) / "table.md"
            args = SCRIPT.argparse.Namespace(after=path, before=path, output=out, rows=["r"])
            SCRIPT.table_command(args)
            text = out.read_text()
        self.assertIn("pooled false alarms per onset", text)
        self.assertIn("worst single lead", text)
        self.assertIn("| 3.46 | 1.64 |", text)


if __name__ == "__main__":
    unittest.main()
