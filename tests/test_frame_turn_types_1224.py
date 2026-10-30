"""The shared H5 frame reads the turn day types, and pages made before #1185 still reproduce under the switch (#1224, finding #1211).

Since #1161 the month-end turn record (`docs/decisions/month-end-turn.md`) is in force: B2 pools by `turn_days.reporting_day_type`
(`turn`, `quarter_end_turn`, `year_end`, `tax_date`, `ordinary`). `spread_mean_reversion_686.Frame.day_type`, which every H5 study
script splits its day-type groups by, still called `SplitDeclaration.reporting_day_type` (the retired `month_end` and `quarter_end`),
so a page's B2 and its day-type groups disagreed (#1211). Three things are pinned.

- `Frame.day_type` is `turn_days.reporting_day_type` of the frame's splits: the turn types in force, the legacy ones under
  `turn_days.legacy_reading()` (the switch `--legacy-day-types` sets, #1206).
- Under that switch the frame reproduces the day-type group sizes of a page made before #1185 (`docs/research/fhs-scale-941-result.md`:
  30 `quarter_end`, 150 `month_end`, 89 `tax_date`, 1590 `ordinary` days).
- No study script outside `EXEMPT` calls `reporting_day_type` on a `SplitDeclaration` directly.

Mutation record (run, killed): in `spread_mean_reversion_686.Frame.day_type`, the line `return turn_days.reporting_day_type(self.splits,
day, self.values[day])` put back to `return self.splits.reporting_day_type(day, self.values[day])` makes four tests fail with
`AssertionError`: `test_frame_reads_the_turn_types_in_force` (`'month_end' != 'ordinary'`), the legacy-switch test, the page
reproduction test and the scan of the scripts.
"""

import collections
import importlib.util
import re
import sys
import unittest
from datetime import date
from pathlib import Path

from repo_model import turn_days
from repo_model.evaluation_splits import load_split_declaration

import panel_cache

ROOT = Path(__file__).resolve().parents[1]

#: Scripts that call `reporting_day_type` on a `SplitDeclaration` directly, each with the reason.
EXEMPT = {
    "live_score": "the frozen live declaration (`LIVE_SOURCE`): the live record keeps the reading it was registered under",
    "month_end_readings_883": "compares the two readings of the month end on purpose",
    "turn_day_labels_959": "builds the turn labels from the legacy ones, and compares them",
    "tax_date_october_965": "reads only the `tax_date` label, which both readings share",
    "b2_pool_fallback_1155": "its arms name their readings themselves (the legacy type, the turn labels, the fallback)",
    "h9_nested_932": "a dated study, run on her Mac at 875eb08f on 29 Oct 2026 under the day types then in force; its outputs are the record, so its method is not changed",
    "scaled_score_967": "`KINDS` and the per-type scale are the retired label set; routing it moves the scaled score (question on the pull request)",
    "contiguous_calibration_963": "`STRATA` are the retired labels, so a routed call would match no `month_end` or `quarter_end` day (question on the pull request)",
    "drivers_audit_951": "`CALENDAR_KINDS` and `RARE_GROUPS` are the retired labels, so a routed call would drop the turn days from them (question on the pull request)",
    # Study scripts of the classifier and pressure-judge era, with no `--legacy-day-types` to reproduce their pages under: left on
    # the declared reading, and put to Eleonora as a marked question on the pull request (#1224).
    "b1_alignment_850": "no --legacy-day-types; not routed here (question on the pull request)",
    "backfill_h5_726": "no --legacy-day-types; not routed here (question on the pull request)",
    "backfill_spread_633": "no --legacy-day-types; not routed here (question on the pull request)",
    "blend_equal_491": "no --legacy-day-types; not routed here (question on the pull request)",
    "calibration_reserve_mgmt_845": "no --legacy-day-types; not routed here (question on the pull request)",
    "construction_gaps_485": "no --legacy-day-types; not routed here (question on the pull request)",
    "direct_pairs_twin": "no --legacy-day-types; not routed here (question on the pull request)",
    "model_defects_540": "no --legacy-day-types; not routed here (question on the pull request)",
    "nowcast": "no --legacy-day-types; not routed here (question on the pull request)",
    "power_replay": "no --legacy-day-types; not routed here (question on the pull request)",
    "pressure_audit": "no --legacy-day-types; not routed here (question on the pull request)",
    "pressure_model_v2": "no --legacy-day-types; not routed here (question on the pull request)",
    "pressure_track_q": "no --legacy-day-types; not routed here (question on the pull request)",
    "recalibration_track": "no --legacy-day-types; not routed here (question on the pull request)",
    "richer_targets_639": "no --legacy-day-types; not routed here (question on the pull request)",
    "richer_targets_706": "no --legacy-day-types; not routed here (question on the pull request)",
    "turning_point_variant": "no --legacy-day-types; not routed here (question on the pull request)",
    "twin_diagnosis_865": "no --legacy-day-types; not routed here (question on the pull request)",
}

#: A call of `reporting_day_type` on some object (not `turn_days.reporting_day_type(splits, ...)`, not a `def`).
DIRECT_CALL = re.compile(r"(?<!turn_days)(?<!td)(?<!\bdef )\.reporting_day_type\(")


def _load_686():
    spec = importlib.util.spec_from_file_location("spread_mean_reversion_686_1224", ROOT / "scripts" / "spread_mean_reversion_686.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["spread_mean_reversion_686_1224"] = module
    spec.loader.exec_module(module)
    return module


class FrameDayType(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_686()
        cls.rows = panel_cache.published_build()["rows"]
        cls.splits = load_split_declaration(cls.module.SPLITS)
        cls.frame = cls.module.Frame(cls.rows, cls.splits, None, None)
        decisions = [d for d in cls.frame.dates if date(2018, 7, 19) <= d <= date(2025, 12, 23)]
        cls.targets = sorted({cls.frame.target(d, h) for d in decisions for h in range(1, 6)})

    def counts(self):
        return collections.Counter(self.frame.day_type(t) for t in self.targets)

    def test_frame_reads_the_turn_types_in_force(self):
        self.assertTrue(turn_days.IN_FORCE)
        for day in self.targets:
            self.assertEqual(self.frame.day_type(day), turn_days.reporting_day_type(self.splits, day, self.frame.values[day]), day)
        kinds = set(self.counts())
        self.assertTrue(kinds <= set(turn_days.LABELS), kinds)
        self.assertFalse(kinds & {"month_end", "quarter_end"}, kinds)
        # 29 June 2018 is the last business day of the quarter, 2 July the first after it; 28 June is the penultimate day.
        self.assertEqual(self.frame.day_type(date(2018, 6, 29)), "quarter_end_turn")
        self.assertEqual(self.frame.day_type(date(2018, 7, 2)), "quarter_end_turn")
        self.assertIn(self.frame.day_type(date(2018, 6, 28)), ("ordinary", "tax_date"))

    def test_the_legacy_switch_gives_the_retired_labels(self):
        with turn_days.legacy_reading():
            self.assertEqual(self.frame.day_type(date(2018, 6, 28)), "month_end")
            self.assertEqual(self.frame.day_type(date(2018, 6, 29)), "quarter_end")
        self.assertEqual(self.frame.day_type(date(2018, 6, 29)), "quarter_end_turn")

    def test_a_page_made_before_1185_reproduces_under_the_switch(self):
        page = (ROOT / "docs" / "research" / "fhs-scale-941-result.md").read_text(encoding="utf-8")
        published = {m.group(1): int(m.group(2))
                     for m in re.finditer(r"^\*\*(quarter_end|month_end|tax_date|ordinary)\*\* \((\d+) days\)$", page, re.M)}
        self.assertEqual(set(published), {"quarter_end", "month_end", "tax_date", "ordinary"})
        with turn_days.legacy_reading():
            self.assertEqual(dict(self.counts()), published)
        self.assertNotEqual(dict(self.counts()), published)


class ScaledScoreKinds(unittest.TestCase):
    """`scaled_score_967.trailing_scales` takes every label the frame can produce: a run on the turn labels did not stop on `KeyError: 'turn'`."""

    def test_every_turn_label_and_every_retired_label_is_a_kind(self):
        module = importlib.util.spec_from_file_location("scaled_score_967_1224", ROOT / "scripts" / "scaled_score_967.py")
        loaded = importlib.util.module_from_spec(module)
        sys.modules["scaled_score_967_1224"] = loaded
        module.loader.exec_module(loaded)
        self.assertTrue(set(turn_days.LABELS) <= set(loaded.KINDS))
        self.assertTrue({"month_end", "quarter_end", "tax_date", "ordinary"} <= set(loaded.KINDS))
        days = [date(2020, 1, 1) + __import__("datetime").timedelta(days=i) for i in range(30)]
        targets = [[d] * 5 for d in days]
        kinds = [["turn"] * 5 for _ in days]
        scores = [[1.0 + i % 3] * 5 for i, _ in enumerate(days)]
        # targets must precede the decision: shift the decisions a year on, as the pool's are never earlier than their cells
        decisions = [d.replace(year=2021) for d in days]
        scales = loaded.trailing_scales(decisions, targets, kinds, scores, trailing=10, lag=2, minimum=3)
        self.assertIsNone(scales[0])
        last = scales[-1]
        self.assertEqual(set(last), set(loaded.KINDS))
        self.assertEqual(last["quarter_end_turn"], last["turn"])  # no cell of its own: the median of all
        self.assertGreater(last["turn"], 0.0)


class NoDirectCalls(unittest.TestCase):
    def test_study_scripts_route_through_turn_days_or_are_exempt(self):
        direct = {}
        for path in sorted((ROOT / "scripts").glob("*.py")):
            hits = [n for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
                    if DIRECT_CALL.search(line) and not line.lstrip().startswith("#")]
            if hits:
                direct[path.stem] = hits
        unrouted = sorted(name for name in direct if name not in EXEMPT)
        self.assertEqual(unrouted, [], f"scripts that call reporting_day_type directly: {unrouted}")
        stale = sorted(name for name in EXEMPT if name not in direct)
        self.assertEqual(stale, [], f"EXEMPT names a script with no direct call: {stale}")


if __name__ == "__main__":
    unittest.main()
