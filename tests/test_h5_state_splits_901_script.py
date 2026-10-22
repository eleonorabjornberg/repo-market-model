"""The cuts of `scripts/h5_state_splits_901.py` (#901, H5 step 3): #634's walks scored by the as-of scarcity state of the decision day.

The script re-reads #634's walks unchanged and reports each skill headline against B1 and B2 for the days whose scarcity
state, public at the decision instant, is ample (states 0 and 1) or scarce (2 and 3), as #706 and #850 group it (ruling on
#515). These tests pin the one new rule, that the state is the one read at the decision instant, and the helpers that
cut the days.

Recorded mutation (CLAUDE.md), 22 October 2026, in a disposable copy: `scripts/h5_state_splits_901.py`, `decision_states`,
`scored = [position[d] + 1 for d in days]` mutated to `[position[d] + 2 for d in days]` (the state is then the one public a day
after the decision instant). `test_the_state_is_the_one_public_at_the_decision_instant` then fails with `AssertionError`
("'scarce' != 'ample'": the day reads the state posted after it).
The lockbox guard is the repository's own (`require_unlocked`, tested in `test_lockbox`);
`test_a_locked_day_is_refused_before_anything_is_read` pins that this script calls it.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, time, timedelta
from pathlib import Path

from repo_model import measurement_fields, scarcity
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "h5_state_splits_901.py"
REGISTRY = measurement_fields.load_registry()
DECISION = time(16, 0)


def _module():
    spec = importlib.util.spec_from_file_location("h5_state_splits_901_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def weekdays(start: date, count: int):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


DATES = weekdays(date(2024, 3, 4), 80)


def panel(state_of):
    return [DailyObservation(d, {"spread_bps": 0.0, scarcity.RESERVE_SCARCITY_STATE: state_of(i)}) for i, d in enumerate(DATES)]


def read_row(index: int) -> int:
    """The row the state is public at for a decision made the day before `index`, by the rule itself (not the script)."""

    with scarcity.measurement_declaration():
        rule = InformationRule(
            REGISTRY, ("spread_bps", scarcity.RESERVE_SCARCITY_STATE), decision_time=DECISION, horizon=1
        )
        info = rule.information_set(DATES, index)
    return {r.feature: r.row for r in info.reads}[scarcity.RESERVE_SCARCITY_STATE]


class DecisionStateTests(unittest.TestCase):
    def test_the_state_is_the_one_public_at_the_decision_instant(self):
        module = _module()
        # a decision day whose successor sees a newer state row: the day must read the older one
        index = next(i for i in range(40, len(DATES) - 3) if read_row(i + 2) > read_row(i + 1))
        cut = read_row(index + 1)
        rows = panel(lambda i: 0.0 if i <= cut else 3.0)
        position = {d: i for i, d in enumerate(DATES)}
        states = module.decision_states(rows, REGISTRY, [DATES[index]], position, DECISION)
        self.assertEqual(states[DATES[index]], "ample")
        later = module.decision_states(rows, REGISTRY, [DATES[index + 1]], position, DECISION)
        self.assertEqual(later[DATES[index + 1]], "scarce")

    def test_a_state_posted_after_the_decision_does_not_move_the_day(self):
        module = _module()
        position = {d: i for i, d in enumerate(DATES)}
        days = DATES[45:60]
        base = module.decision_states(panel(lambda i: float(i % 4)), REGISTRY, days, position, DECISION)
        # every row after the last decision day is rewritten: no decision day may notice
        last = position[days[-1]]
        changed = module.decision_states(panel(lambda i: float(i % 4) if i <= last else 3.0), REGISTRY, days, position, DECISION)
        self.assertEqual(base, changed)

    def test_ample_is_states_zero_and_one_and_scarce_two_and_three(self):
        module = _module()
        position = {d: i for i, d in enumerate(DATES)}
        for value, band in ((0.0, "ample"), (1.0, "ample"), (2.0, "scarce"), (3.0, "scarce")):
            states = module.decision_states(panel(lambda i, v=value: v), REGISTRY, [DATES[60]], position, DECISION)
            self.assertEqual(states[DATES[60]], band)

    def test_a_hole_in_the_state_is_unknown_and_not_a_band(self):
        module = _module()
        position = {d: i for i, d in enumerate(DATES)}
        states = module.decision_states(panel(lambda i: None), REGISTRY, [DATES[60]], position, DECISION)
        self.assertEqual(states[DATES[60]], "unknown")

    def test_a_locked_day_is_refused_before_anything_is_read(self):
        module = _module()
        locked = date(2026, 9, 10)
        with self.assertRaises(LookAheadError):
            module.decision_states([], REGISTRY, [locked], {locked: 0}, DECISION)


class CutTests(unittest.TestCase):
    DAYS = [date(2019, 9, 16), date(2019, 9, 17), date(2019, 9, 18), date(2019, 9, 19)]

    def test_the_cuts_are_pooled_without_the_day_and_each_state(self):
        module = _module()
        states = {self.DAYS[0]: "ample", self.DAYS[1]: "scarce", self.DAYS[2]: "scarce", self.DAYS[3]: "unknown"}
        cuts = module.state_cuts(self.DAYS, states)
        self.assertEqual(cuts["pooled"], self.DAYS)
        self.assertEqual(cuts["without_2019-09-18"], [self.DAYS[0], self.DAYS[1], self.DAYS[3]])
        self.assertEqual(cuts["state:ample"], [self.DAYS[0]])
        self.assertEqual(cuts["state:scarce"], [self.DAYS[1], self.DAYS[2]])
        self.assertEqual(cuts["state:scarce without_2019-09-18"], [self.DAYS[1]])
        self.assertEqual(cuts["state:unknown"], [self.DAYS[3]])
        self.assertNotIn("state:ample without_2019-09-18", cuts)

    def test_every_decision_day_is_in_exactly_one_state_cut(self):
        module = _module()
        states = {d: ("ample" if i % 2 else "scarce") for i, d in enumerate(self.DAYS)}
        cuts = module.state_cuts(self.DAYS, states)
        members = [d for label, group in cuts.items() if label in ("state:ample", "state:scarce") for d in group]
        self.assertEqual(sorted(members), self.DAYS)


class VariantForecastTests(unittest.TestCase):
    """The #1027 variants join #634's candidates on #634's decision days; a day they do not cover stops the run."""

    DAYS = weekdays(date(2024, 3, 4), 40)
    B1 = {d: {h: [0.0] for h in range(1, 6)} for d in DAYS}

    def test_a_variant_is_filled_with_b1_at_a_missing_lead(self):
        module = _module()
        full = {h: [float(h)] for h in range(1, 6)}
        decisions = {d: full for d in self.DAYS}
        decisions[self.DAYS[0]] = {1: [1.0]}
        out = module.variant_forecasts("v", decisions, self.B1, self.DAYS)
        self.assertEqual(out[self.DAYS[0]], {1: [1.0], **{h: [0.0] for h in range(2, 6)}})
        self.assertEqual(out[self.DAYS[1]], full)

    def test_a_decision_day_the_variant_does_not_cover_is_a_data_error(self):
        module = _module()
        with self.assertRaises(ValueError):
            module.variant_forecasts("v", {self.DAYS[0]: {h: [0.0] for h in range(1, 6)}}, self.B1, self.DAYS)


class ReproduceTests(unittest.TestCase):
    TRACKED = {"B1 -> gbm_funding": {"skill": 0.2, "n": 10}}

    def test_a_pooled_figure_that_matches_the_tracked_one_passes(self):
        module = _module()
        module.check_pooled({"B1 -> gbm_funding": {"skill": 0.2, "n": 10}}, self.TRACKED)

    def test_a_pooled_figure_that_differs_is_a_data_error(self):
        module = _module()
        with self.assertRaises(ValueError):
            module.check_pooled({"B1 -> gbm_funding": {"skill": 0.21, "n": 10}}, self.TRACKED)

    def test_a_pair_the_tracked_page_lacks_is_a_data_error(self):
        module = _module()
        with self.assertRaises(ValueError):
            module.check_pooled({"B2 -> gbm_funding": {"skill": 0.2, "n": 10}}, self.TRACKED)


if __name__ == "__main__":
    unittest.main()
