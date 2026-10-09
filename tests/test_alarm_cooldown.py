"""The alarm cool-down (#459): repeat flags inside five trading days count as one alarm.

A cool-down is a rule for counting alarms on the flags of a forecast the judge already scores. It refits
nothing and moves no probability or cut-off. A candidate declares it as `alarm_rule` in its file under
`metadata/pressure_judge/candidates/`, with the base candidate whose forecasts it reuses.

Not a leakage guard: the exception ("unless a pressure day starts in the window") reads the days after the
flag, so the rule counts alarms on a scored record and is not one a live forecaster could apply. The strict
form (`keep_when_pressure_starts` false) is the one that could be applied as the days arrive. The tests below
pin that difference: the exception never costs an onset, the strict form can.
"""

from __future__ import annotations

import json
import random
import unittest
from pathlib import Path

from repo_model import pressure_judge as pj
from test_pressure_judge import Series, _declaration, _write

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "metadata" / "pressure_judge" / "candidates"
RULE = {"kind": "cooldown", "base": "sharp", "trading_days": 5, "keep_when_pressure_starts": True}


def cooled(flags, onset, days=5, keep=True):
    return pj.cooldown_flags(flags, onset, days, keep_when_pressure_starts=keep)


class CooldownFlagsTests(unittest.TestCase):
    def test_a_burst_with_no_pressure_day_in_its_window_counts_once(self):
        flags = [0, 1, 1, 1, 1, 1, 0, 0, 0]
        self.assertEqual(cooled(flags, [0] * 9), [0, 1, 0, 0, 0, 0, 0, 0, 0])

    def test_a_flag_after_the_window_is_a_new_alarm(self):
        flags = [1, 0, 0, 0, 0, 0, 1, 1, 0]
        self.assertEqual(cooled(flags, [0] * 9), [1, 0, 0, 0, 0, 0, 1, 0, 0])

    def test_the_window_is_the_five_days_after_the_alarm(self):
        for gap, kept in ((5, 0), (6, 1)):
            flags = [1] + [0] * (gap - 1) + [1]
            self.assertEqual(cooled(flags, [0] * len(flags))[-1], kept, gap)

    def test_a_repeat_does_not_open_a_window_of_its_own(self):
        # Flags at 0 and 4 (a repeat), then 8: 8 is outside the window of 0 (1 to 5), so it is a new alarm.
        flags = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        self.assertEqual(cooled(flags, [0] * 9), [1, 0, 0, 0, 0, 0, 0, 0, 1])

    def test_repeats_stay_when_a_pressure_day_starts_in_the_window(self):
        flags = [1, 1, 1, 1, 0, 0, 0, 0]
        onset = [0, 0, 0, 0, 0, 1, 0, 0]
        self.assertEqual(cooled(flags, onset), flags)
        # The strict form drops them, and an onset flag among them with it.
        self.assertEqual(cooled(flags, onset, keep=False), [1, 0, 0, 0, 0, 0, 0, 0])

    def test_a_pressure_day_before_or_after_the_window_does_not_keep_repeats(self):
        flags = [0, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        for k in (1, 7):
            onset = [0] * 10
            onset[k] = 1
            self.assertEqual(cooled(flags, onset), [0, 1, 0, 0, 0, 0, 0, 0, 0, 0], k)

    def test_it_only_drops_flags_and_keeps_the_first_of_every_burst(self):
        rng = random.Random(459)
        for _ in range(200):
            n = rng.randint(1, 60)
            flags = [rng.randint(0, 1) for _ in range(n)]
            onset = [1 if rng.random() < 0.1 else 0 for _ in range(n)]
            for keep in (True, False):
                out = cooled(flags, onset, keep=keep)
                self.assertTrue(all(o <= f for o, f in zip(out, flags)))
                if 1 in flags:
                    first = flags.index(1)
                    self.assertEqual(out[first], 1)
            # With the exception no flag on an onset day is ever dropped: an onset is a catch, not a repeat.
            with_exception = cooled(flags, onset, keep=True)
            self.assertTrue(all(w == f for w, f, o in zip(with_exception, flags, onset) if o))

    def test_the_series_must_agree_and_the_window_be_positive(self):
        with self.assertRaises(ValueError):
            cooled([1, 0], [0])
        with self.assertRaises(ValueError):
            cooled([1], [0], days=0)


class AlarmRuleDeclarationTests(unittest.TestCase):
    def declared(self, rule):
        document = _declaration()
        document["candidates"]["sharp_cooled"] = {
            "role": "candidate", "features": ["x"], "calibration": "none", "alarm_rule": rule,
        }
        return pj.load_declaration(_write(document))

    def test_a_cooldown_rule_is_read_and_reported(self):
        declaration = self.declared(dict(RULE))
        self.assertEqual(declaration.candidates["sharp_cooled"]["alarm_rule"], RULE)
        self.assertEqual(declaration.document()["candidates"]["sharp_cooled"]["alarm_rule"], RULE)

    def test_a_malformed_rule_is_refused(self):
        for bad in (
            {**RULE, "kind": "debounce"},
            {**RULE, "trading_days": 0},
            {**RULE, "trading_days": "5"},
            {**RULE, "keep_when_pressure_starts": "yes"},
            {**RULE, "base": ""},
            {**RULE, "extra": 1},
            {k: v for k, v in RULE.items() if k != "base"},
            "cooldown",
        ):
            with self.assertRaises(ValueError, msg=str(bad)):
                self.declared(bad)

    def test_the_tracked_cooldown_candidates_are_five_days_and_name_a_tracked_base(self):
        found = {}
        for file in sorted(CANDIDATES.glob("*.json")):
            entry = json.loads(file.read_text())
            if "alarm_rule" in entry:
                found[file.stem] = entry["alarm_rule"]
        self.assertTrue(found)
        for name, rule in found.items():
            self.assertEqual(rule["trading_days"], 5, name)
            self.assertTrue((CANDIDATES / f"{rule['base']}.json").exists(), name)
            self.assertEqual(name, f"{rule['base']}_cooldown5" + ("" if rule["keep_when_pressure_starts"] else "_strict"))


class JudgeCooldownTests(unittest.TestCase):
    """A burst of two false alarms ten days before each onset, beside the onset's own flag."""

    def run_judge(self, burst, rule=None):
        series = Series()
        probabilities = [1.0 if (y or k % 20 in burst) else 0.0 for k, y in enumerate(series.y5)]
        document = _declaration()
        if rule is not None:
            document["candidates"]["sharp"]["alarm_rule"] = rule
        declaration = pj.load_declaration(_write(document))
        grids = {h: series.grid(h) for h in (1, 2)}
        forecasts = []
        for h in (1, 2):
            forecasts.append(series.flat("calendar_climatology", h, 0.1))
            forecasts.append(series.flat("persistence_logistic", h, 0.1))
            forecasts.append(series.forecast("sharp", h, probabilities))
        result = pj.judge(declaration, grids, forecasts, calendar=series.dates)
        return result["candidates"]["sharp"]

    def tier_one(self, result):
        return result["tiers"]["onset_warning"]["lead_at_least_1"]

    def test_a_burst_far_from_an_onset_counts_as_one_false_alarm(self):
        plain = self.tier_one(self.run_judge({10, 11}))
        cooled_ = self.tier_one(self.run_judge({10, 11}, RULE))
        self.assertEqual(cooled_["onsets_flagged"], plain["onsets_flagged"])
        self.assertGreater(plain["worst_false_alarms_per_onset"], cooled_["worst_false_alarms_per_onset"])
        self.assertAlmostEqual(cooled_["worst_false_alarms_per_onset"] * 2, plain["worst_false_alarms_per_onset"])

    def test_a_burst_that_ends_in_an_onset_is_left_alone_with_the_exception(self):
        plain = self.tier_one(self.run_judge({1, 2, 3}))
        kept = self.tier_one(self.run_judge({1, 2, 3}, RULE))
        self.assertEqual(kept["onsets_flagged"], plain["onsets_flagged"])
        self.assertEqual(kept["worst_false_alarms_per_onset"], plain["worst_false_alarms_per_onset"])

    def test_the_strict_form_can_cost_the_onset_it_precedes(self):
        plain = self.tier_one(self.run_judge({2, 3}))
        strict = self.tier_one(self.run_judge({2, 3}, {**RULE, "keep_when_pressure_starts": False}))
        self.assertLess(strict["onsets_flagged"], plain["onsets_flagged"])

    def test_the_rule_cools_the_flags_and_leaves_the_probabilities_and_cutoffs(self):
        cooled_ = self.run_judge({10, 11}, RULE)
        plain = self.run_judge({10, 11})
        self.assertEqual(cooled_["alarm_rule"], RULE)
        self.assertNotIn("alarm_rule", plain)
        row_plain, row_cooled = plain["horizons"]["1"]["5"], cooled_["horizons"]["1"]["5"]
        self.assertLess(row_cooled["flags"]["alarms"], row_plain["flags"]["alarms"])
        for key in ("cutoff", "brier", "auroc", "calibration"):
            if key in row_plain:
                self.assertEqual(row_cooled[key], row_plain[key], key)


DECLARED = json.loads((ROOT / "metadata" / "alarm_cooldown.json").read_text())


class DeclaredRowsTests(unittest.TestCase):
    def test_the_six_rows_follow_the_declared_rule_from_table_one(self):
        from test_onset_diagnostics import table_one

        rows = table_one()
        excluded = set(DECLARED["rows"]["excluded"])
        ranked = sorted((n for n in rows if n not in excluded), key=lambda n: (-rows[n][0], rows[n][1], n))
        self.assertEqual(ranked[:6], DECLARED["rows"]["chosen"])

    def test_every_row_has_both_forms_declared_as_candidates(self):
        self.assertEqual(DECLARED["rule"]["trading_days"], 5)
        for row in DECLARED["rows"]["chosen"]:
            for name, keep in ((f"{row}_cooldown5", True), (f"{row}_cooldown5_strict", False)):
                entry = json.loads((CANDIDATES / f"{name}.json").read_text())
                self.assertEqual(
                    entry["alarm_rule"],
                    {"kind": "cooldown", "base": row, "trading_days": 5, "keep_when_pressure_starts": keep},
                )
            self.assertTrue((CANDIDATES / f"{row}.json").exists(), row)


if __name__ == "__main__":
    unittest.main()
