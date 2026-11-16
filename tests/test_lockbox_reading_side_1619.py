"""The scoring step of six study scripts refuses a locked day or a day beyond the window on the cells it reads back (#1619, finding #1582).

`walk_command` of each script refuses such a day before it writes a walk file, but `score_command` read the file back and scored its
cells without a check of its own, so a hand-edited or stale walk file holding a day after 2025-12-31 (development) or after
2026-09-03 (the exploratory window's end; the blind tier opens on 2026-09-04) was scored. Each `score_command` now calls
`refuse_beyond` on every decision and target day of the cells it reads, before any other use of the file.

The test writes a walk file holding one cell with a day after the window's end (a locked day, 2026-09-10, for the "2026" window;
2026-01-05 for the "development" window) and runs `score_command`: it must raise `LookAheadError`. The file holds nothing else a
scorer could read, so any other exception shows the guard did not come first.

Written before the guards: every subtest errored (not `LookAheadError`): `KeyError: 'uncapped_quantiles'` for the three capped-law
scripts, `KeyError: 'arms'` for `h5_robustness_1364`, and the same kind of error for the other two, because the scorer read the file
before refusing its cells.

Recorded mutation (a new guard on the reading side): deleting the `m66.refuse_beyond(...)` line that follows `doc = json.loads(raw)`
in `scripts/capped_baselines_1421.py` `score_command` makes both tests error for `capped_baselines_1421` with
`KeyError: 'uncapped_quantiles'` (the scorer went on into the file instead of raising `LookAheadError`); restored, they pass. The
same line removed from each of the other five scripts fails its own subtests.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.splits import LookAheadError  # noqa: E402

SCRIPTS = ("calibration_masking_candidate_1366", "candidate_calibration_1363", "cap_tail_rule_1389",
           "capped_baselines_1421", "capped_baselines_b2star_1434", "h5_robustness_1364")
#: The scripts whose walk cells are triples `[decision, lead, target]`; the others hold dicts with "day" and "target".
TRIPLES = ("candidate_calibration_1363", "h5_robustness_1364")
BEYOND = {"development": date(2026, 1, 5), "2026": date(2026, 9, 10)}


def load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_in_1619", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def walk_doc(name: str, window: str, decision: date, target: date) -> dict:
    cell = ([decision.isoformat(), 1, target.isoformat()] if name in TRIPLES else
            {"key": f"{decision.isoformat()}/1", "day": decision.isoformat(), "lead": 1, "target": target.isoformat()})
    return {"window": window, "panel_sha256": "0" * 64, "cells": [cell], "decision_days": 1}


class ReadingSideGuardTests(unittest.TestCase):
    def run_score(self, name: str, window: str, decision: date, target: date):
        module = load(name)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / f"{window}.json").write_text(json.dumps(walk_doc(name, window, decision, target)), encoding="utf-8")
            args = SimpleNamespace(walks=tmp, output=str(Path(tmp) / "out.json"), draws=10, workers=1)
            return module.score_command(args)

    def test_a_walk_file_with_a_day_beyond_the_window_is_refused(self):
        for name in SCRIPTS:
            for window, beyond in BEYOND.items():
                with self.subTest(script=name, window=window):
                    last = date(2025, 12, 31) if window == "development" else date(2026, 8, 31)
                    with self.assertRaises(LookAheadError):
                        self.run_score(name, window, last, beyond)

    def test_a_decision_day_beyond_the_window_is_refused_too(self):
        for name in SCRIPTS:
            with self.subTest(script=name):
                with self.assertRaises(LookAheadError):
                    self.run_score(name, "2026", BEYOND["2026"], date(2026, 8, 31))


if __name__ == "__main__":
    unittest.main()
