"""H1 step 3, finding #741: does a forecaster that merely declines to copy a calendar spike beat B1 by the MME?

On the simulated panel of #762 (`benchmark_simulation`: an AR(1) spread around levels that depend on the day type),
the forecaster `spike_blind_forecast` is B1 with the anchor's spread replaced by the last ordinary-day spread at or
before the anchor. It has no parameter and no skill on ordinary days: on an ordinary anchor it is B1 exactly.
Nothing about B1, B2, B3 or the MME is changed here; the tests only run them.

**What is asserted.** (a) The forecaster equals B1 on every ordinary anchor and differs from it, by the anchor's
excess over the last ordinary spread, on every spike anchor. (b) It reads nothing after the anchor. (c) On the
process with its declared spikes, its pooled skill against B1 is at or above the MME in the mean over a handful of
panels, and its skill on ordinary anchors is exactly zero. (d) On a process with no spikes (all levels 0) the same
forecaster's pooled skill is below the MME (it is slightly negative over 200 panels: it re-centres on an older row for nothing), so the result is the spikes' and not a flaw of the
forecaster. The full figures with Monte Carlo intervals, over 200 panels, are in
`docs/research/spike-blind-741.md`; this suite runs 4.

Mutation record, in a scratch copy of `tests/benchmark_simulation.py`: `shift = panel[last].spread_bps - panel[anchor].spread_bps`
replaced by `shift = 0.0` (the forecaster copies the spike, i.e. is B1). Failed with `AssertionError`:
`SpikeBlindForecastTests.test_a_spike_anchor_is_re_centred_on_the_last_ordinary_spread` and
`SpikeBlindSkillTests.test_pooled_skill_against_b1_clears_the_mme_when_there_are_spikes`.
"""

from __future__ import annotations

import unittest

import benchmark_simulation as sim
from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp

REGISTRY, SPLITS, DECISION = sim.REGISTRY, sim.SPLITS, sim.DECISION


class SpikeBlindForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = sim.simulate(sim.ProcessSpec(), seed=7410)
        cls.rows = cls.sample.rows

    def decisions(self, step=5):
        start = next(i for i, row in enumerate(self.rows) if row.date >= sim.EVALUATION_FIRST)
        return range(start, len(self.rows) - 5, step)

    def test_on_an_ordinary_anchor_it_is_b1(self):
        checked = 0
        for t in self.decisions():
            if self.sample.kinds[t - 1] != "ordinary":
                continue
            checked += 1
            mine = sim.spike_blind_forecast(self.rows, t)
            b1 = pb.b1_forecast(self.rows, t, registry=REGISTRY, decision_time=DECISION)
            for h in sp.HORIZONS:
                for a, b in zip(mine[h], b1[h]):
                    self.assertAlmostEqual(a, b, places=12)
        self.assertGreater(checked, 50)

    def test_a_spike_anchor_is_re_centred_on_the_last_ordinary_spread(self):
        checked = 0
        for t in self.decisions(step=1):
            if self.sample.kinds[t - 1] == "ordinary":
                continue
            checked += 1
            last = next(s for s in range(t - 1, -1, -1) if self.sample.kinds[s] == "ordinary")
            shift = self.sample.spreads[last] - self.sample.spreads[t - 1]
            mine = sim.spike_blind_forecast(self.rows, t)
            b1 = pb.b1_forecast(self.rows, t, registry=REGISTRY, decision_time=DECISION)
            self.assertNotEqual(shift, 0.0)
            for h in sp.HORIZONS:
                for a, b in zip(mine[h], b1[h]):
                    self.assertAlmostEqual(a, b + shift, places=12)
        self.assertGreater(checked, 20)

    def test_it_reads_nothing_after_the_anchor(self):
        t = next(i for i in self.decisions(step=1) if self.sample.kinds[i - 1] != "ordinary")
        before = sim.spike_blind_forecast(self.rows, t)
        altered = list(self.rows)
        for s in range(t, len(altered)):
            values = dict(altered[s].values)
            values["sofr"] = values["sofr"] + 1.0
            altered[s] = type(altered[s])(altered[s].date, values)
        after = sim.spike_blind_forecast(altered, t)
        self.assertEqual(before, after)


class SpikeBlindSkillTests(unittest.TestCase):
    REPLICATES = 4

    def test_pooled_skill_against_b1_clears_the_mme_when_there_are_spikes(self):
        report = sim.spike_blind_report(self.REPLICATES, seed=7411, decision_step=7)
        self.assertGreaterEqual(report["pooled"]["interval"][0], sp.MME)
        self.assertEqual(report["pooled"]["share_at_mme"], 1.0)
        self.assertAlmostEqual(report["ordinary"]["skill"], 0.0, places=12)
        for group in ("month_end", "tax_date", "quarter_end"):
            self.assertGreater(report[group]["skill"], sp.MME, group)

    def test_with_no_spikes_it_has_no_skill(self):
        flat = sim.ProcessSpec(levels={kind: 0.0 for kind in sim.ProcessSpec().levels})
        report = sim.spike_blind_report(self.REPLICATES, seed=7412, decision_step=7, spec=flat)
        self.assertLess(report["pooled"]["interval"][1], sp.MME)
        self.assertEqual(report["pooled"]["share_at_mme"], 0.0)


if __name__ == "__main__":
    unittest.main()
