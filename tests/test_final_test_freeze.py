"""The final test's pre-registration is frozen (#150).

`docs/decisions/final-test-preregistration.md` pins the checksum of the
pre-registered model's declaration: its inputs, constants, calibrator and the
source of the code that fits and scores it
(`scripts/final_test_preregistration.py`, `declaration`). A change to any of
them after the record merges fails `FreezeTests`, before #151 opens the
lockbox.

Red first: this file was committed before the record existed, and
`FreezeTests` failed with `FileNotFoundError` on the missing record.

The CRPS test (#220, Eleonora's amendment of 4 October 2026 on #151) has its
own frozen declaration and checksum (`crps_declaration`,
`crps_declaration_checksum`), pinned in the record as "CRPS declaration
checksum". The leap test's checksum does not move. Red first: `CrpsFreezeTests`
and `CrpsCellTests` were committed before the script had a CRPS declaration,
and failed with `AttributeError` on the missing `crps_declaration_checksum`.

Mutation record (`CrpsCellTests`, the CRPS cell's lockbox check):
`lockbox.require_unlocked(window, where="final test CRPS cell")` in
`crps_cell` deleted, confirmed applied by grep; the test
`test_the_cell_refuses_while_the_near_blind_tier_is_locked` then failed with
`AssertionError` ("LookAheadError not raised"). Restored, green.

Mutation record (`RefuseLockedTests`, the selection run's own lockbox check):
`if any(when >= date(2026, 1, 1) ...)` in `_refuse_locked` mutated to
`date(2026, 1, 2)`, confirmed applied by grep; the test
`test_the_first_locked_day_is_refused` then failed with `AssertionError`
("LookAheadError not raised"). Restored, green. (The guard raised `ValueError`
until the ruling of 3 October 2026 on #216 made it a `LookAheadError`, as
CLAUDE.md asks of leakage guards; the mutation was re-run then.)
"""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "final_test_preregistration.py"
RECORD = REPO / "docs" / "decisions" / "final-test-preregistration.md"


def _script():
    spec = importlib.util.spec_from_file_location("final_test_preregistration", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fp = _script()


def _pinned(field):
    text = RECORD.read_text(encoding="utf-8")
    found = re.findall(rf"^- \*\*{re.escape(field)}:\*\* `([^`]+)`", text, flags=re.MULTILINE)
    if len(found) != 1:
        raise AssertionError(f"the record pins {field!r} {len(found)} times, not once")
    return found[0]


class FreezeTests(unittest.TestCase):
    """The pinned checksum is the declaration's, and the record names the chosen model."""

    def test_the_declaration_checksum_is_the_pinned_one(self):
        self.assertEqual(fp.declaration_checksum(), _pinned("Declaration checksum"))

    def test_the_record_names_the_chosen_model_and_calibrator(self):
        self.assertEqual(_pinned("Model"), fp.CHOSEN)
        self.assertEqual(_pinned("Calibrator"), fp.CHOSEN_CALIBRATOR)
        self.assertIn(fp.CHOSEN, fp.CANDIDATES)

    def test_a_changed_constant_moves_the_checksum(self):
        before = fp.declaration_checksum()
        moved = {**fp.onset.LEAP_JUMP_BP, 1: fp.onset.LEAP_JUMP_BP[1] + 1}
        with mock.patch.object(fp.onset, "LEAP_JUMP_BP", moved):
            self.assertNotEqual(fp.declaration_checksum(), before)
        with mock.patch.object(fp.pc, "MINIMUM_PAIRS", fp.pc.MINIMUM_PAIRS + 1):
            self.assertNotEqual(fp.declaration_checksum(), before)

    def test_changed_code_moves_the_checksum(self):
        """The checksum reads each pinned definition's source, so an edit to one moves it."""

        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            for path, _names in fp._SHARED_SOURCE + fp._MODEL_SOURCE[fp.CHOSEN]:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((REPO / path).read_text(encoding="utf-8"), encoding="utf-8")
            with mock.patch.object(fp, "REPO", root):
                self.assertEqual(fp.declaration_checksum(), _pinned("Declaration checksum"))
                walk = root / "src/repo_model/probability_calibration.py"
                text = walk.read_text(encoding="utf-8")
                walk.write_text(
                    text.replace("def walk_forward(", "def walk_forward(  # edited\n", 1),
                    encoding="utf-8",
                )
                self.assertNotEqual(fp.declaration_checksum(), _pinned("Declaration checksum"))

    def test_a_missing_definition_is_refused(self):
        with self.assertRaises(ValueError):
            fp._top_level_source("src/repo_model/onset.py", ("no_such_definition",))


LEAP_CHECKSUM = "5f084e7568f242bc76b6faa34fdcae2cb0ca786d328ca86d1f1ccf00385c0449"
PUBLISHED_CRPS = REPO / "docs" / "runs" / "compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"


def _published_declaration():
    """The published CRPS record's declaration and interval settings, never its losses."""

    record = json.loads(PUBLISHED_CRPS.read_text(encoding="utf-8"))
    interval = dict(record["comparison"]["mean_difference_interval"])
    for key in ("lower", "upper"):
        interval.pop(key)
    return record["declaration"], interval, record["panel"]["sha256"]


class CrpsFreezeTests(unittest.TestCase):
    """The CRPS test is frozen: the published distribution and the CRPS path (#220)."""

    def test_the_crps_checksum_is_the_pinned_one(self):
        self.assertEqual(fp.crps_declaration_checksum(), _pinned("CRPS declaration checksum"))

    def test_the_leap_checksum_is_unchanged(self):
        self.assertEqual(_pinned("Declaration checksum"), LEAP_CHECKSUM)
        self.assertEqual(fp.declaration_checksum(), LEAP_CHECKSUM)

    def test_the_distribution_is_the_published_one(self):
        """Both sides, the fold grid and the decision time, exactly as #169 published them."""

        published, interval, panel = _published_declaration()
        frozen = fp.crps_declaration()
        for key in ("model_a", "model_b", "minimum_history", "refit_every", "decision_time"):
            self.assertEqual(frozen[key], published[key], key)
        self.assertEqual(frozen["end"], "2026-09-03")
        self.assertEqual(frozen["panel_sha256"], panel)
        self.assertEqual(
            frozen["interval"],
            {"level": interval["level"], "replications": interval["replications"],
             "block_length": interval["block_length"], "seed": interval["seed"],
             "method": interval["method"]},
        )

    def test_the_command_parses_and_says_what_the_declaration_says(self):
        from repo_model.cli import build_parser

        argv = list(fp.CRPS_COMMAND)
        args = build_parser().parse_args(argv)
        frozen = fp.crps_declaration()
        self.assertEqual(args.command, "compare")
        self.assertEqual(args.loss, "crps")
        self.assertEqual(args.end, date(2026, 9, 3))
        self.assertEqual(args.model_a, frozen["model_a"]["model"])
        self.assertEqual(args.model_b, frozen["model_b"]["model"])
        self.assertEqual(args.feature_a, frozen["model_a"]["features"])
        self.assertEqual(sorted(args.feature_b), frozen["model_b"]["features"])
        self.assertEqual(args.calibration_b, frozen["model_b"]["calibration"])
        self.assertIsNone(args.calibration_a)
        self.assertEqual(args.minimum_history, frozen["minimum_history"])
        self.assertEqual(args.refit_every, frozen["refit_every"])
        self.assertEqual(args.decision_time, frozen["decision_time"])
        self.assertEqual(frozen["command"], argv)
        # The record names the command the opening run types, flag for flag.
        record = " ".join(RECORD.read_text(encoding="utf-8").replace("\\\n", " ").split())
        self.assertIn(" ".join(argv[1:]), record)

    def test_a_changed_constant_moves_the_crps_checksum(self):
        before = fp.crps_declaration_checksum()
        for module, name, value in (
            (fp.recalibration, "PID_GRID_STEPS", (0.01, 0.05)),
            (fp.recalibration, "PID_STEP_WINDOW", fp.recalibration.PID_STEP_WINDOW + 1),
            (fp.baseline, "BOOTSTRAP_REPLICATIONS", fp.baseline.BOOTSTRAP_REPLICATIONS + 1),
            (fp.baseline, "BOOTSTRAP_LEVEL", 0.95),
            (fp, "CRPS_BLOCK_LENGTH", fp.CRPS_BLOCK_LENGTH + 1),
            (fp, "CRPS_WINDOW_DAYS", fp.CRPS_WINDOW_DAYS + 1),
        ):
            with self.subTest(name=name), mock.patch.object(module, name, value):
                self.assertNotEqual(fp.crps_declaration_checksum(), before)

    def test_changed_code_moves_the_crps_checksum(self):
        """An edit to the CRPS, the bootstrap, the gbm or nested PID moves it; the leap's stays."""

        edits = (
            ("src/repo_model/metrics.py", "def crps_from_quantiles("),
            ("src/repo_model/metrics.py", "def stationary_bootstrap_interval("),
            ("src/repo_model/ml.py", "def fit_gradient_boosted_quantiles("),
            ("src/repo_model/recalibration.py", "class NestedFoldPid("),
            ("src/repo_model/baseline.py", "def paired_model_comparison("),
            ("src/repo_model/cli_eval.py", "def _compare("),
            ("scripts/final_test_preregistration.py", "def crps_cell("),
        )
        paths = {path for path, _names in fp._SHARED_SOURCE + fp._MODEL_SOURCE[fp.CHOSEN]}
        paths |= {path for path, _names in fp._CRPS_SOURCE}
        for path, marker in edits:
            with self.subTest(path=path, marker=marker), tempfile.TemporaryDirectory() as scratch:
                root = Path(scratch)
                for each in paths:
                    target = root / each
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text((REPO / each).read_text(encoding="utf-8"), encoding="utf-8")
                with mock.patch.object(fp, "REPO", root):
                    self.assertEqual(fp.crps_declaration_checksum(),
                                     _pinned("CRPS declaration checksum"))
                    edited = root / path
                    text = edited.read_text(encoding="utf-8")
                    self.assertIn(marker, text)
                    edited.write_text(text.replace(marker, marker + "  # edited\n", 1),
                                      encoding="utf-8")
                    self.assertNotEqual(fp.crps_declaration_checksum(),
                                        _pinned("CRPS declaration checksum"))
                    if path != "scripts/final_test_preregistration.py":
                        self.assertEqual(fp.declaration_checksum(), LEAP_CHECKSUM)


class WindowDaysTests(unittest.TestCase):
    """The window is 169 panel dates, counted from the date column only (#220, point 3)."""

    def test_the_window_holds_169_panel_dates(self):
        with tempfile.TemporaryDirectory() as scratch:
            panel = Path(scratch) / "PUB.csv"
            subprocess.run(
                [sys.executable, "-m", "repo_model.cli", "build",
                 "--raw-root", str(REPO / "tests/fixtures/snapshots/funding_inputs"),
                 "--output", str(panel), "--build-cutoff", "2026-09-08T21:31:42+00:00",
                 "--decision-time", "16:00:00"],
                check=True, cwd=REPO, capture_output=True,
                env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin"},
            )
            self.assertEqual(fp.panel_sha256(panel), fp.crps_declaration()["panel_sha256"])
            days = fp.window_dates(panel)
        self.assertEqual(len(days), fp.CRPS_WINDOW_DAYS)
        self.assertEqual(fp.CRPS_WINDOW_DAYS, 169)
        self.assertEqual((days[0], days[-1]), (date(2026, 1, 2), date(2026, 9, 3)))

    def test_only_the_date_column_is_read(self):
        with tempfile.TemporaryDirectory() as scratch:
            panel = Path(scratch) / "p.csv"
            with panel.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["sofr", "date", "iorb"])
                for day in ("2025-12-31", "2026-01-02", "2026-09-03", "2026-09-04"):
                    writer.writerow(["not a number", day, ""])
            self.assertEqual(fp.window_dates(panel), [date(2026, 1, 2), date(2026, 9, 3)])


def _synthetic_record(days, differences, **changes):
    published, interval, panel = _published_declaration()
    declaration = {**published, "end": "2026-09-03"}
    per_origin = [
        {"scored_date": day.isoformat(), "difference_bps": diff,
         "loss_a_bps": 1.0 + diff, "loss_b_bps": 1.0}
        for day, diff in zip(days, differences)
    ]
    record = {
        "declaration": declaration,
        "panel": {"sha256": panel},
        "comparison": {"loss": "crps_bps", "mean_difference_interval": dict(interval),
                       "per_origin": per_origin},
    }
    for key, value in changes.items():
        record[key] = value
    return record


def _opened_lockbox(scratch):
    path = Path(scratch) / "lockbox.json"
    document = json.loads((REPO / "metadata" / "lockbox.json").read_text(encoding="utf-8"))
    document["tiers"][0]["opened"] = {"date": "2026-10-04", "ruling": "synthetic, a test"}
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


class CrpsCellTests(unittest.TestCase):
    """The CRPS cell and its pass rule, on synthetic records; no 2026 outcome is read."""

    PRE = [date(2025, 12, 30), date(2025, 12, 31)]

    def _days(self):
        from datetime import timedelta

        days, day = [], date(2026, 1, 2)
        while len(days) < fp.CRPS_WINDOW_DAYS:
            if day.weekday() < 5:
                days.append(day)
            day += timedelta(days=1)
        return days

    def test_the_cell_refuses_while_the_near_blind_tier_is_locked(self):
        days = self._days()
        record = _synthetic_record(self.PRE + days, [0.0] * (2 + len(days)))
        with self.assertRaises(LookAheadError):
            fp.crps_cell(record)

    def test_the_cell_scores_only_the_window_and_a_clear_gain_passes(self):
        days = self._days()
        record = _synthetic_record(self.PRE + days, [-50.0, -50.0] + [0.5 + 0.01 * (i % 7)
                                                                       for i in range(len(days))])
        with tempfile.TemporaryDirectory() as scratch, \
                mock.patch.object(fp.lockbox, "DEFAULT_LOCKBOX", _opened_lockbox(scratch)):
            cell = fp.crps_cell(record)
        self.assertEqual(cell["days"], fp.CRPS_WINDOW_DAYS)
        self.assertEqual(cell["first"], "2026-01-02")
        self.assertGreater(cell["mean_difference_bps"], 0.5)
        self.assertGreater(cell["interval"]["lower"], 0.0)
        self.assertEqual(fp.crps_verdict(cell), "pass")

    def test_an_interval_reaching_zero_does_not_pass(self):
        cell = {"mean_difference_bps": 0.2, "interval": {"lower": -0.01, "upper": 0.4}}
        self.assertEqual(fp.crps_verdict(cell), "fail")
        cell = {"mean_difference_bps": -0.2, "interval": {"lower": -0.4, "upper": -0.01}}
        self.assertEqual(fp.crps_verdict(cell), "fail")
        cell = {"mean_difference_bps": 0.2, "interval": {"lower": 0.01, "upper": 0.4}}
        self.assertEqual(fp.crps_verdict(cell), "pass")

    def test_a_record_that_is_not_the_frozen_run_is_refused(self):
        days = self._days()
        good = _synthetic_record(self.PRE + days, [0.0] * (2 + len(days)))
        bad_declaration = {**good["declaration"], "refit_every": 5}
        bad_interval = {**good["comparison"]["mean_difference_interval"], "seed": 1}
        cases = (
            _synthetic_record(self.PRE + days, [0.0] * (2 + len(days)),
                              declaration=bad_declaration),
            _synthetic_record(self.PRE + days, [0.0] * (2 + len(days)),
                              panel={"sha256": "0" * 64}),
            {**good, "comparison": {**good["comparison"],
                                    "mean_difference_interval": bad_interval}},
            _synthetic_record(self.PRE + days[:-1], [0.0] * (1 + len(days))),
        )
        with tempfile.TemporaryDirectory() as scratch, \
                mock.patch.object(fp.lockbox, "DEFAULT_LOCKBOX", _opened_lockbox(scratch)):
            for record in cases:
                with self.subTest(), self.assertRaises(ValueError):
                    fp.crps_cell(record)


class RuleTests(unittest.TestCase):
    """The two pre-stated rules, on synthetic cells."""

    @staticmethod
    def _paired(mean, lower, upper):
        return {"mean": mean, "interval": {"lower": lower, "upper": upper}}

    def test_platt_is_the_default_calibrator(self):
        cell = {"vs_platt": {
            "isotonic": self._paired(0.002, -0.001, 0.004),
            "beta": self._paired(-0.001, -0.002, 0.0),
            "platt_recency": self._paired(0.001, 0.0, 0.002),
        }}
        self.assertEqual(fp.choose_calibrator(cell), "platt")

    def test_a_gain_whose_interval_excludes_zero_replaces_platt_and_the_largest_wins(self):
        cell = {"vs_platt": {
            "isotonic": self._paired(0.002, 0.0001, 0.004),
            "beta": self._paired(0.003, -0.001, 0.007),
            "platt_recency": self._paired(0.0015, 0.0005, 0.0025),
        }}
        self.assertEqual(fp.choose_calibrator(cell), "isotonic")

    def test_the_highest_ranked_candidate_within_the_interval_is_chosen(self):
        scores = {name: {"within": False} for name in fp.CANDIDATES}
        scores["published_v1"]["within"] = True
        scores["stacked_combiner"]["within"] = True
        self.assertEqual(fp.choose_model(scores), "published_v1")
        scores["scarcity_calendar"]["within"] = True
        self.assertEqual(fp.choose_model(scores), "scarcity_calendar")

    def test_the_ranking_is_the_amendment_s(self):
        self.assertEqual(
            fp.CANDIDATES,
            ("scarcity_calendar", "dynamic_logit", "direct_logistic_sofr_p1",
             "published_v1", "v1_1", "stacked_combiner"),
        )


class RefuseLockedTests(unittest.TestCase):
    """The selection run refuses a locked day (`docs/decisions/lockbox.md`)."""

    def test_the_first_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            fp._refuse_locked([date(2025, 12, 31), date(2026, 1, 1)])

    def test_the_last_open_day_is_not(self):
        fp._refuse_locked([date(2025, 12, 30), date(2025, 12, 31)])


if __name__ == "__main__":
    unittest.main()
