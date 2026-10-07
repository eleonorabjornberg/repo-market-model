"""The declared rule for the ON RRP depletion inputs (#132, `docs/pivot/depleted-inputs-test.md`)."""

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "depleted_inputs_judge", Path(__file__).resolve().parents[1] / "scripts" / "depleted_inputs_judge.py")
judge_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(judge_module)


def cell(count, lower, upper):
    return {"count": count, "interval": {"lower": lower, "upper": upper}, "mean": (lower + upper) / 2}


def splits(**cells):
    return {"by_regime": dict(cells), "by_day_type": {"ordinary": cell(500, -1, 1)}}


class JudgeTests(unittest.TestCase):
    def test_gate_needs_lower_bound_above_zero(self):
        ok = judge_module.judge("x", 0.1, {"lower": 0.01, "upper": 0.2}, splits())
        edge = judge_module.judge("x", 0.1, {"lower": 0.0, "upper": 0.2}, splits())
        self.assertTrue(ok["gate"])
        self.assertFalse(edge["gate"])

    def test_cell_worse_beyond_interval_is_flagged_only_with_enough_days(self):
        figure = judge_module.judge("x", 0.1, {"lower": 0.01, "upper": 0.2},
                                    splits(a=cell(30, -0.5, -0.1), b=cell(10, -0.5, -0.1)))
        self.assertEqual(figure["cells_worse_beyond_interval"], ["by_regime/a"])
        self.assertEqual(figure["cells"]["by_regime/b"], "too few days")

    def test_decision_needs_all_three_figures(self):
        def fig(gate, worse=()):
            return {"gate": gate, "cells_worse_beyond_interval": list(worse)}

        good = {"crps_bps": fig(True), "brier_+5bp": fig(True), "brier_+10bp": fig(True)}
        self.assertTrue(judge_module.decide(good))
        self.assertFalse(judge_module.decide({**good, "brier_+10bp": fig(False)}))
        self.assertFalse(judge_module.decide({**good, "crps_bps": fig(True, ["by_regime/a"])}))


if __name__ == "__main__":
    unittest.main()
