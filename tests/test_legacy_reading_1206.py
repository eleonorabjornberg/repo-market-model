"""The legacy day-type reading (#1206, finding #1205): pages made before #1185 reproduce, and scripts that walk B2 run on main.

Since #1161 (PR #1185, merged 2026-10-24 1:36 pm ET) B2 reads the turn labels and, since #1198 (PR #1202), its thin-pool
fallback; a study script that walks B2 from 2018 stopped with `ProtocolError` on 2018-06-29 and 2018-12-21 to 2018-12-31.
`turn_days.legacy_reading()` switches both back (the plain legacy B2 and the legacy `month_end` / `quarter_end` types) and
every study script of the list below takes `--legacy-day-types`, which runs it under that reading.

Three things are pinned here.

- The helper restores both switches, also when the body raises, and the decorator takes the flag off the argument list.
- Every script under `scripts/` that calls `b2_forecast` either takes the flag or is listed, with its reason, in `EXEMPT`.
- On the published panel built from the tracked fixtures, `scaled_score_967.build_pool` runs under the in-force reading, with a
  B2 forecast on 2018-06-29 and on 2018-12-21 to 2018-12-31, and under the legacy reading reproduces the published pool of
  `docs/research/scaled-score-967-result.md`: 1868 days, mean B2 grid CRPS 2.5143, mean B1 2.3024.

Mutation record (run, killed): in `repo_model.turn_days.legacy_reading`, the line that sets `b2_pool.IN_FORCE = False` removed
makes `test_legacy_reading_reproduces_the_published_pool` fail with `AssertionError` (mean B2 2.5244 against 2.5143; the thin
pool fallback is still on), and three helper tests fail with `AssertionError`.
"""

import importlib.util
import json
import re
import sys
import unittest
from datetime import date, time
from pathlib import Path

from repo_model import b2_pool, turn_days
from repo_model import protocol_benchmarks as pb
from repo_model.data import load_daily_panel
from repo_model.evaluation_splits import load_split_declaration

import panel_cache

ROOT = Path(__file__).resolve().parents[1]

#: Scripts that call `b2_forecast` and take no `--legacy-day-types`, each with the reason.
EXEMPT = {
    "b2_pool_fallback_1155": "its arms name their readings themselves (the legacy type, the turn labels, the fallback)",
    "regime_spells_1182": "its page was made after #1185 under the turn labels and before #1198 (a third reading)",
    "s3_terms_1196": "its page was made after #1185 under the turn labels and before #1198 (a third reading)",
    "live_monitor": "reads the live record, which is frozen on its own declaration",
}


class Helper(unittest.TestCase):
    def test_both_switches_are_off_inside_and_restored_after(self):
        self.assertTrue(turn_days.IN_FORCE and b2_pool.IN_FORCE)
        with turn_days.legacy_reading():
            self.assertFalse(turn_days.IN_FORCE)
            self.assertFalse(b2_pool.IN_FORCE)
        self.assertTrue(turn_days.IN_FORCE and b2_pool.IN_FORCE)

    def test_they_are_restored_when_the_body_raises(self):
        with self.assertRaises(RuntimeError):
            with turn_days.legacy_reading():
                raise RuntimeError("boom")
        self.assertTrue(turn_days.IN_FORCE and b2_pool.IN_FORCE)

    def test_it_nests_and_restores_what_it_found(self):
        with turn_days.legacy_reading():
            with turn_days.legacy_reading():
                self.assertFalse(turn_days.IN_FORCE)
            self.assertFalse(turn_days.IN_FORCE)
            self.assertFalse(b2_pool.IN_FORCE)
        self.assertTrue(turn_days.IN_FORCE and b2_pool.IN_FORCE)

    def test_the_decorator_strips_the_flag_and_runs_legacy(self):
        seen = []

        @turn_days.with_legacy_flag
        def main(argv=None):
            seen.append((list(argv), turn_days.IN_FORCE, b2_pool.IN_FORCE))
            return 0

        self.assertEqual(main(["run", "--legacy-day-types", "--x", "1"]), 0)
        self.assertEqual(main(["run", "--x", "1"]), 0)
        self.assertEqual(seen, [(["run", "--x", "1"], False, False), (["run", "--x", "1"], True, True)])
        self.assertTrue(turn_days.IN_FORCE and b2_pool.IN_FORCE)

    def test_the_decorator_reads_sys_argv_when_given_none(self):
        seen = []

        @turn_days.with_legacy_flag
        def main(argv=None):
            seen.append((argv, turn_days.IN_FORCE))
            return 0

        old = sys.argv
        sys.argv = ["script.py", "go", "--legacy-day-types"]
        try:
            main()
        finally:
            sys.argv = old
        self.assertEqual(seen, [(["go"], False)])


class EveryScriptThatWalksB2(unittest.TestCase):
    def test_each_takes_the_flag_or_is_exempt_with_a_reason(self):
        walkers = {}
        for path in sorted((ROOT / "scripts").glob("*.py")):
            text = path.read_text(encoding="utf-8")
            if "b2_forecast" in text:
                walkers[path.stem] = "@turn_days.with_legacy_flag" in text
        self.assertTrue(walkers)
        missing = sorted(name for name, flagged in walkers.items() if not flagged and name not in EXEMPT)
        self.assertEqual(missing, [], f"scripts that walk B2 without --legacy-day-types: {missing}")
        flagged_and_exempt = sorted(name for name in EXEMPT if walkers.get(name))
        self.assertEqual(flagged_and_exempt, [], "an exempt script that takes the flag: drop it from EXEMPT")
        stale = sorted(name for name in EXEMPT if name not in walkers)
        self.assertEqual(stale, [], f"EXEMPT names a script that no longer calls b2_forecast: {stale}")

    def test_the_four_named_scripts_take_it(self):
        for name in ("scaled_score_967", "scaled_score_1013", "state_calendar_1145", "s3_decomposition_1172"):
            text = (ROOT / "scripts" / f"{name}.py").read_text(encoding="utf-8")
            self.assertIn("@turn_days.with_legacy_flag", text, name)

    def test_the_reproducibility_note_exists(self):
        text = (ROOT / "REPRODUCIBILITY.md").read_text(encoding="utf-8")
        self.assertIn("--legacy-day-types", text)


def _load_967():
    spec = importlib.util.spec_from_file_location("scaled_score_967_1206", ROOT / "scripts" / "scaled_score_967.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["scaled_score_967_1206"] = module
    spec.loader.exec_module(module)
    return module


class RealPanel(unittest.TestCase):
    """`scaled_score_967.build_pool` on the published panel, under each reading."""

    @classmethod
    def setUpClass(cls):
        cls.module = _load_967()
        cls.build = panel_cache.published_build()
        cls.rows = cls.build["rows"]
        cls.splits = load_split_declaration(cls.module.SPLITS_PATH)
        cls.registry = json.loads(cls.module.SOURCES.read_text(encoding="utf-8"))

    def pool(self):
        return self.module.build_pool(self.rows, self.splits, self.registry)

    def test_it_runs_under_the_in_force_reading(self):
        self.assertTrue(turn_days.IN_FORCE and b2_pool.IN_FORCE)
        pool = self.pool()
        self.assertEqual(pool.decisions[0], date(2018, 6, 29))
        self.assertIn(date(2018, 12, 21), set(pool.decisions))
        self.assertTrue(all(len(per) == 5 for per in pool.s2))

    def test_b2_forecasts_the_early_turn_days_in_force(self):
        index = {row.date: i for i, row in enumerate(self.rows)}
        settings = {"registry": self.registry, "decision_time": time(16)}
        for day in [date(2018, 6, 29)] + [date(2018, 12, d) for d in range(21, 32)]:
            if day not in index:
                continue
            forecasts = pb.forecasts(pb.b2_forecast, self.rows, [day], splits=self.splits, **settings)
            self.assertEqual(sorted(forecasts[day]), [1, 2, 3, 4, 5], day)

    def test_legacy_reading_reproduces_the_published_pool(self):
        with turn_days.legacy_reading():
            pool = self.pool()
        n = len(pool.decisions)
        mean2 = sum(sum(r) / 5 for r in pool.s2) / n
        mean1 = sum(sum(r) / 5 for r in pool.s1) / n
        self.assertEqual(n, 1868)
        self.assertEqual(round(mean2, 4), 2.5143)
        self.assertEqual(round(mean1, 4), 2.3024)


if __name__ == "__main__":
    unittest.main()
