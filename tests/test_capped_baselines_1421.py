"""B1'*-cap and B2*-cap, the simple baselines with the candidate's Standing Repo Facility cap (#1421; H5, registration design).

`protocol_benchmarks.capped_forecast`, `capped_exceedance`, `b1_calendar_anchor_capped_forecast` (and `b2_capped_forecast`, B2 standing in for B2*, until #1440 replaced it
with `b2_star_capped_forecast`; its tests moved to `tests/test_capped_baselines_b2star_1434.py`), and the arithmetic of `scripts/capped_baselines_1421.py` (the cells, the decision-day series, the share of the candidate's gain
the cap alone explains). Her ruling of 3 November 2026: the capped baselines are the confirmatory ones, the uncapped versions are reported beside them.

What these tests pin: the cap is the candidate's own (`s3c_candidate.cap_line`, margin 0 bp, full allotment only); a baseline before full allotment is
unchanged element by element; the capped vector is `min(q, line)`, ordered, and never above the line; the probabilities are the candidate's rule (b)
(`capped_law` `open_tail`) and agree with `s3c_candidate.candidate_exceedance` on the same quantiles; the line is read at the decision instant, so a policy
entry announced after it moves nothing and one announced before it does; the share of a gain a cap explains.

Written before the code: the functions did not exist (`AttributeError: module 'repo_model.protocol_benchmarks' has no attribute 'capped_forecast'`;
`FileNotFoundError` for the script).

Recorded mutation (availability guard, the instant at which the line is read): in `protocol_benchmarks.capped_forecast`,
`as_of = datetime.combine(panel[decision_index].date, decision_time)` was replaced with
`as_of = datetime.combine(panel[decision_index].date, time(23, 59, 59))`, so a register entry announced on the decision day after the decision instant is
read. `InformationSetTests.test_an_entry_announced_after_the_decision_instant_moves_nothing` failed with `AssertionError` (the capped forecast moved: a
line of 5.0 bp was read where 10.0 bp was public); restored, it passes. With `srf_line`'s `known_entries` filter and `require_announced` in place the entry
is read on purpose by the mutated instant, so no `LookAheadError` is raised: the instant is the guard.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

import test_protocol_benchmarks as tpb
from repo_model import capped_law as cl
from repo_model import policy_events as pe
from repo_model import protocol_benchmarks as pb
from repo_model import s3c_candidate as s3c
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("capped_baselines_1421_script", ROOT / "scripts" / "capped_baselines_1421.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

REGISTER = pe.load_register()
DECISION = time(18, 0)


def ramp(start, step):
    return [start + step * i for i in range(len(sp.GRID))]


def forecast(q):
    return {h: list(q) for h in sp.HORIZONS}


def entry(ident, kind, announced_at, effective, rate, *, limit="absent"):
    details = {"rate_percent": rate}
    if limit != "absent":
        details["aggregate_operation_limit_bn"] = limit
    return pe.PolicyEntry(ident, kind, "change", ident, announced_at, "stated", effective, "https://example.org", True, details)


def setup():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=DECISION, splits=tpb.SPLITS)


class CapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()
        cls.late = len(cls.panel) - 12  # targets in 2026, at full allotment
        cls.early = next(i for i, r in enumerate(cls.panel) if r.date >= date(2024, 6, 3))

    def test_the_cap_is_the_candidates_line_on_every_lead(self):
        t = self.late
        q = ramp(-5.0, 1.5)  # reaches 28.5 bp, above any line
        got = pb.capped_forecast(forecast(q), self.panel, t, register=REGISTER, decision_time=DECISION)
        for h in sp.HORIZONS:
            as_of = datetime.combine(self.panel[t].date, DECISION)
            line = s3c.cap_line(REGISTER, as_of, self.panel[t + h].date)
            self.assertIsNotNone(line)
            self.assertEqual(got[h], [min(v, line) for v in q])
            self.assertEqual(got[h], sorted(got[h]))
            self.assertLessEqual(got[h][-1], line)

    def test_a_target_before_full_allotment_is_the_baseline_itself(self):
        q = ramp(-5.0, 1.5)
        got = pb.capped_forecast(forecast(q), self.panel, self.early, register=REGISTER, decision_time=DECISION)
        self.assertEqual(got, forecast(q))

    def test_a_cap_above_every_quantile_changes_nothing(self):
        q = ramp(-5.0, 0.1)  # tops out at -2.8 bp, under the line
        got = pb.capped_forecast(forecast(q), self.panel, self.late, register=REGISTER, decision_time=DECISION)
        self.assertEqual(got, forecast(q))

    def test_b1_prime_star_cap_is_b1_prime_star_clipped(self):
        for t in (self.early, self.late - 30, self.late):
            raw = pb.b1_calendar_anchor_forecast(self.panel, t, **self.settings)
            want = pb.capped_forecast(raw, self.panel, t, register=REGISTER, decision_time=DECISION)
            got = pb.b1_calendar_anchor_capped_forecast(self.panel, t, register=REGISTER, **self.settings)
            self.assertEqual(got, want)

    def test_b2_cap_of_1421_is_b2_clipped(self):
        """The study of #1421 builds its B2-cap from `b2_forecast` and `capped_forecast`; the stand-in function is gone (#1440)."""

        for t in (self.early, self.late):
            raw = pb.b2_forecast(self.panel, t, **self.settings)
            got = pb.capped_forecast(raw, self.panel, t, register=REGISTER, decision_time=DECISION)
            for h in sp.HORIZONS:
                self.assertTrue(all(c <= r for c, r in zip(got[h], raw[h])))
        raw = pb.b2_forecast(self.panel, self.early, **self.settings)
        self.assertEqual(pb.capped_forecast(raw, self.panel, self.early, register=REGISTER, decision_time=DECISION), raw)

    def test_a_lead_past_the_panel_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            pb.capped_forecast(forecast(ramp(0.0, 1.0)), self.panel, len(self.panel) - 2, register=REGISTER, decision_time=DECISION)


class ProbabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()
        cls.late = len(cls.panel) - 12
        cls.early = next(i for i, r in enumerate(cls.panel) if r.date >= date(2024, 6, 3))

    def tied_top(self):
        q = ramp(-4.0, 0.5)
        q[-4:] = [11.0, 20.0, 25.0, 40.0]  # four upper levels above a 10 bp line
        return q

    def test_the_probabilities_are_the_candidates_rule_b(self):
        q = self.tied_top()
        t = self.late
        as_of = datetime.combine(self.panel[t].date, DECISION)
        for h in sp.HORIZONS:
            for tau in (5.0, 10.0):
                want = s3c.candidate_exceedance(q, REGISTER, as_of, self.panel[t + h].date, tau)
                got = pb.capped_exceedance(forecast(q), self.panel, t, h, tau, register=REGISTER, decision_time=DECISION)
                self.assertEqual(got, want)

    def test_rule_b_leaves_a_tail_above_the_line_where_the_status_quo_has_none(self):
        q = self.tied_top()
        t = self.late
        line = s3c.cap_line(REGISTER, datetime.combine(self.panel[t].date, DECISION), self.panel[t + 1].date)
        status_quo = cl.exceedance(q, line, line, "status_quo")
        got = pb.capped_exceedance(forecast(q), self.panel, t, 1, line, register=REGISTER, decision_time=DECISION)
        self.assertGreater(got, status_quo)
        self.assertLessEqual(got, 1.0 - sp.GRID[-1] + 1e-12)

    def test_before_full_allotment_it_is_the_uncapped_law(self):
        q = self.tied_top()
        got = pb.capped_exceedance(forecast(q), self.panel, self.early, 1, 5.0, register=REGISTER, decision_time=DECISION)
        self.assertEqual(got, cl.exceedance(q, None, 5.0, "open_tail"))


class InformationSetTests(unittest.TestCase):
    """The line a baseline is capped at is the one public at the decision instant."""

    @classmethod
    def setUpClass(cls):
        cls.panel, _ = setup()
        cls.t = len(cls.panel) - 12
        cls.day = cls.panel[cls.t].date
        base = [
            entry("srf-full", "standing_repo", datetime(2025, 12, 10, 14, 0), date(2025, 12, 11), 4.0, limit=None),
            entry("iorb-base", "iorb_rate", datetime(2025, 12, 10, 14, 0), date(2025, 12, 11), 3.9),
        ]
        cls.base = tuple(base)  # a line of 10 bp

    def capped(self, register):
        q = ramp(-5.0, 1.5)
        return pb.capped_forecast(forecast(q), self.panel, self.t, register=register, decision_time=DECISION)

    def with_cut(self, hour, minute):
        # a cut of the minimum bid by 5 bp, announced on the decision day and effective from the next day
        cut = entry("srf-cut", "standing_repo", datetime.combine(self.day, time(hour, minute)), self.day + timedelta(days=1), 3.95, limit=None)
        return self.base + (cut,)

    def test_the_line_of_the_base_register_is_ten_bp(self):
        self.assertAlmostEqual(self.capped(self.base)[1][-1], 10.0)

    def test_an_entry_announced_after_the_decision_instant_moves_nothing(self):
        self.assertEqual(self.capped(self.with_cut(19, 0)), self.capped(self.base))
        self.assertEqual(self.capped(self.with_cut(18, 1)), self.capped(self.base))

    def test_an_entry_announced_before_the_decision_instant_is_read(self):
        got = self.capped(self.with_cut(17, 59))
        self.assertAlmostEqual(got[1][-1], 5.0)
        self.assertNotEqual(got, self.capped(self.base))


class ScriptArithmeticTests(unittest.TestCase):
    def test_a_capped_cell_is_scored_on_the_capped_vector_and_rule_b(self):
        q = ramp(-4.0, 0.5)
        q[-4:] = [11.0, 20.0, 25.0, 40.0]
        capped = script.model_cell(q, 10.0, 12.0, capped=True)
        self.assertEqual(capped["vector"], cl.cap(q, 10.0))
        self.assertAlmostEqual(capped["grid_crps"], sp.grid_crps(cl.cap(q, 10.0), 12.0))
        self.assertAlmostEqual(capped["upper_tail_twcrps"], sp.upper_tail_twcrps(cl.cap(q, 10.0), 12.0))
        self.assertAlmostEqual(capped["brier_gt5"], (cl.exceedance(q, 10.0, 5.0, "open_tail") - 1.0) ** 2)

    def test_an_uncapped_cell_ignores_the_line(self):
        q = ramp(-4.0, 0.5)
        q[-4:] = [11.0, 20.0, 25.0, 40.0]
        uncapped = script.model_cell(q, 10.0, 2.0, capped=False)
        self.assertEqual(uncapped["vector"], q)
        self.assertAlmostEqual(uncapped["brier_gt5"], cl.exceedance(q, None, 5.0, "open_tail") ** 2)

    def test_a_cell_without_a_line_is_the_same_capped_or_not(self):
        q = ramp(-4.0, 0.5)
        self.assertEqual(script.model_cell(q, None, 3.0, capped=True), script.model_cell(q, None, 3.0, capped=False))

    def test_the_event_is_strict_and_on_whole_basis_points(self):
        q = ramp(-4.0, 0.5)
        self.assertEqual(script.model_cell(q, None, 5.4, capped=False)["event5"], 0)
        self.assertEqual(script.model_cell(q, None, 5.6, capped=False)["event5"], 1)

    def test_the_share_of_the_gain_the_cap_explains(self):
        # uncapped 10, capped 7, candidate 4: the candidate gains 6, the cap alone 3
        self.assertAlmostEqual(script.share_explained(uncapped=10.0, capped=7.0, candidate=4.0), 0.5)
        self.assertAlmostEqual(script.share_explained(uncapped=10.0, capped=10.0, candidate=4.0), 0.0)
        self.assertAlmostEqual(script.share_explained(uncapped=10.0, capped=4.0, candidate=4.0), 1.0)
        # a cap that helps more than the whole gain explains more than all of it
        self.assertAlmostEqual(script.share_explained(uncapped=10.0, capped=3.0, candidate=4.0), 7.0 / 6.0)

    def test_no_share_where_the_candidate_does_not_gain(self):
        self.assertIsNone(script.share_explained(uncapped=4.0, capped=3.0, candidate=4.0))
        self.assertIsNone(script.share_explained(uncapped=4.0, capped=3.0, candidate=5.0))

    def test_day_series_is_the_mean_over_a_days_member_cells(self):
        cells = [{"day": "2026-01-02", "line": 10.0}, {"day": "2026-01-02", "line": None}, {"day": "2026-01-05", "line": None}]
        series = script.day_series(cells, [1.0, 3.0, 5.0], lambda c: True)
        self.assertEqual(series, {date(2026, 1, 2): 2.0, date(2026, 1, 5): 5.0})
        only = script.day_series(cells, [1.0, 3.0, 5.0], lambda c: c["line"] is not None)
        self.assertEqual(only, {date(2026, 1, 2): 1.0})


if __name__ == "__main__":
    unittest.main()
