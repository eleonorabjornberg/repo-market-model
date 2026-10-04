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

A recorded change to a newly frozen constant: `PID_GRID_STEPS = (0.01, 0.05,
0.2)` in `src/repo_model/recalibration.py` changed to `(0.01, 0.05, 0.3)`,
confirmed applied by grep; `test_the_crps_checksum_is_the_pinned_one` then
failed with `AssertionError` (the checksum moved to `13f6de82…`), and
`test_the_leap_checksum_is_unchanged` stayed green. Restored, green. Re-run
after Eleonora's ruling of 4 October 2026 on #221 (the labels and the block-10
sensitivity interval, which moved the pin): the checksum then moved to
`d6c3ecec…`, and the leap test stayed green. Re-run after her ruling of
4 October 2026 (16:45) on #221, which made the CRPS cell at h = 1 the one
primary cell and regenerated both checksums (`PrimaryCellTests`, red first
with 6 failures and 13 errors): the checksum then moved to `b06fdaeb…`, and
`test_the_leap_checksum_is_the_regenerated_one` stayed green.

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
import hashlib
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


#: The leap checksum #216 pinned, before the ruling of 4 October 2026 (16:45) on
#: #221 added the cells and their roles to the declaration.
LEAP_CHECKSUM_AT_216 = "5f084e7568f242bc76b6faa34fdcae2cb0ca786d328ca86d1f1ccf00385c0449"
LEAP_CHECKSUM = "28ad819321d50a44b50adf69f78af1fbe28d6c4f6a9a813544e13d06deed4432"
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

    def test_the_leap_checksum_is_the_regenerated_one(self):
        self.assertEqual(_pinned("Declaration checksum"), LEAP_CHECKSUM)
        self.assertEqual(fp.declaration_checksum(), LEAP_CHECKSUM)

    def test_only_the_cells_moved_the_leap_checksum(self):
        """Without the cells, the leap declaration is byte-for-byte the one pinned at #216."""

        frozen = fp.declaration()
        self.assertEqual(frozen.pop("cells"), fp.cells())
        text = json.dumps(frozen, sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), LEAP_CHECKSUM_AT_216)

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

    def test_the_block_10_sensitivity_is_declared_and_pinned(self):
        """Ruling of 4 October on #221 (b): block length 10, a seed declared now, deciding nothing."""

        frozen = fp.crps_declaration()
        self.assertEqual(fp.CRPS_SENSITIVITY_BLOCK_LENGTH, 10)
        self.assertEqual(str(fp.CRPS_SENSITIVITY_SEED), _pinned("CRPS sensitivity seed"))
        self.assertEqual(
            frozen["sensitivity_interval"],
            {"level": baseline_level(), "replications": baseline_replications(),
             "block_length": 10, "seed": fp.CRPS_SENSITIVITY_SEED,
             "method": "stationary_bootstrap", "decides": "nothing"},
        )
        # The primary interval is untouched by the sensitivity report.
        self.assertEqual(frozen["interval"]["block_length"], 2)
        self.assertEqual(frozen["interval"]["seed"], 1970125677)

    def test_the_labels_are_declared(self):
        """Ruling of 4 October on #221 (a): reporting labels that add nothing to the pass rule."""

        self.assertEqual(
            fp.crps_declaration()["labels"],
            {"pass": "mean difference > 0 and 90% lower bound > 0",
             "not distinguishable": "not a pass and not worse: the 90% interval contains 0, "
                                    "or lies above 0 around a mean that is not above 0",
             "worse": "the 90% upper bound is below 0"},
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
            (fp, "CRPS_SENSITIVITY_BLOCK_LENGTH", fp.CRPS_SENSITIVITY_BLOCK_LENGTH + 1),
            (fp, "CRPS_SENSITIVITY_SEED", fp.CRPS_SENSITIVITY_SEED + 1),
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
                    if path == "src/repo_model/ml.py":
                        # ml.py holds the leap test's model too; an edit outside it leaves it.
                        self.assertEqual(fp.declaration_checksum(), LEAP_CHECKSUM)


class PrimaryCellTests(unittest.TestCase):
    """The CRPS cell at h = 1 is the one primary cell (ruling of 4 October 2026 on #221, 16:45).

    Every leap and threshold cell, and CRPS at horizons 2 to 5, is reported only.
    Both checksums cover the cells and their roles.
    """

    def test_the_crps_cell_at_h1_is_the_only_primary_cell(self):
        cells = fp.cells()
        self.assertEqual(cells["primary"], fp.PRIMARY_CELL)
        self.assertEqual([name for name, role in cells["roles"].items() if role == "primary"],
                         [fp.PRIMARY_CELL])
        self.assertEqual(fp.PRIMARY_CELL, "crps, h = 1")
        frozen = fp.crps_declaration()
        self.assertEqual(frozen["horizon"], 1)
        self.assertEqual((frozen["window"]["first"], frozen["window"]["last"]),
                         ("2026-01-01", "2026-09-03"))
        self.assertEqual(frozen["model_a"], {"model": "persistence", "features": ["spread_bps"]})
        self.assertEqual(frozen["model_b"]["calibration"], "conformal_pid_nested")

    def test_every_leap_and_threshold_cell_is_reported_only(self):
        roles = fp.cells()["roles"]
        for name in ("crps, h = 2 to 5", "plain leap, h = 1", "plain leap, h = 2 to 5",
                     "leap onset", "pressure leap", "+5 bp", "+10 bp"):
            with self.subTest(cell=name):
                self.assertEqual(roles[name], "reported only")

    def test_both_declarations_carry_the_cells(self):
        self.assertEqual(fp.declaration()["cells"], fp.cells())
        self.assertEqual(fp.crps_declaration()["cells"], fp.cells())

    def test_a_changed_role_moves_both_checksums(self):
        leap, crps = fp.declaration_checksum(), fp.crps_declaration_checksum()
        moved = {**fp.CELLS, "plain leap, h = 1": "primary"}
        with mock.patch.object(fp, "CELLS", moved):
            self.assertNotEqual(fp.declaration_checksum(), leap)
            self.assertNotEqual(fp.crps_declaration_checksum(), crps)
        with mock.patch.object(fp, "PRIMARY_CELL", "plain leap, h = 1"):
            self.assertNotEqual(fp.declaration_checksum(), leap)
            self.assertNotEqual(fp.crps_declaration_checksum(), crps)

    def test_the_claim_is_declared_and_recorded(self):
        claim = ("the published model's one-day-ahead forecast of the full distribution of "
                 "SOFR \u2212 IORB was more accurate than as-of persistence over January to "
                 "September 2026")
        self.assertEqual(fp.CRPS_CLAIM, claim)
        self.assertEqual(fp.crps_declaration()["claim"], claim)
        record = " ".join(RECORD.read_text(encoding="utf-8").split())
        self.assertIn(claim, record)
        self.assertNotIn("warns of stress", claim)

    def test_the_record_names_the_primary_cell(self):
        self.assertEqual(_pinned("Primary cell"), fp.PRIMARY_CELL)
        text = RECORD.read_text(encoding="utf-8")
        self.assertIn("## Amendment, 4 October 2026: the full-range test is the primary cell", text)


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
        near_blind = fp.lockbox.load_lockbox()[0]
        self.assertEqual((near_blind.name, near_blind.start, near_blind.end),
                         ("near_blind", fp.CRPS_FIRST, fp.CRPS_LAST))

    def test_only_the_date_column_is_read(self):
        with tempfile.TemporaryDirectory() as scratch:
            panel = Path(scratch) / "p.csv"
            with panel.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["sofr", "date", "iorb"])
                for day in ("2025-12-31", "2026-01-02", "2026-09-03", "2026-09-04"):
                    writer.writerow(["not a number", day, ""])
            self.assertEqual(fp.window_dates(panel), [date(2026, 1, 2), date(2026, 9, 3)])


def baseline_level():
    return fp.baseline.BOOTSTRAP_LEVEL


def baseline_replications():
    return fp.baseline.BOOTSTRAP_REPLICATIONS


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
        self.assertEqual(cell["verdict"], "pass")
        self.assertEqual(cell["result"], "pass")
        self.assertEqual((cell["cell"], cell["horizon"]), (fp.PRIMARY_CELL, 1))
        # The block-10 sensitivity interval is reported beside it and decides nothing.
        sensitivity = cell["sensitivity_interval"]
        self.assertEqual((sensitivity["block_length"], sensitivity["seed"], sensitivity["decides"]),
                         (10, fp.CRPS_SENSITIVITY_SEED, "nothing"))
        self.assertLess(sensitivity["lower"], cell["mean_difference_bps"])
        self.assertGreater(sensitivity["upper"], cell["mean_difference_bps"])
        with mock.patch.dict(sensitivity, {"lower": -1.0, "upper": -0.5}):
            self.assertEqual(fp.crps_verdict(cell), "pass")

    def test_with_the_panel_rows_the_cell_is_split_by_regime_and_day_type(self):
        from repo_model.data import DailyObservation

        days = self._days()
        rows = [DailyObservation(day, {"quarter_end": float(i == 60), "tax_date": 0.0,
                                       "days_to_month_end": float(10 + i % 3)})
                for i, day in enumerate(self.PRE + days)]
        record = _synthetic_record(self.PRE + days, [0.0, 0.0] + [0.1] * len(days))
        with tempfile.TemporaryDirectory() as scratch, \
                mock.patch.object(fp.lockbox, "DEFAULT_LOCKBOX", _opened_lockbox(scratch)):
            cell = fp.crps_cell(record, rows)
        self.assertEqual(cell["splits"]["by_regime"]["2025-26"]["count"], fp.CRPS_WINDOW_DAYS)
        self.assertEqual(cell["splits"]["by_day_type"]["quarter_end"]["count"], 1)

    def test_an_interval_reaching_zero_does_not_pass(self):
        """Pass is unchanged; a non-pass is labelled (ruling of 4 October on #221, (a))."""

        cases = (
            (0.2, -0.01, 0.4, "not distinguishable"),
            (-0.2, -0.4, 0.01, "not distinguishable"),
            (0.2, 0.0, 0.4, "not distinguishable"),
            (-0.2, -0.4, 0.0, "not distinguishable"),
            (-0.2, -0.4, -0.01, "worse"),
            (0.2, 0.01, 0.4, "pass"),
            # The edge case (ruling of 4 October 16:45 on #221): an interval above 0
            # around a mean that is not above 0 fails, labelled "not distinguishable".
            (0.0, 0.01, 0.4, "not distinguishable"),
            (-0.1, 0.01, 0.4, "not distinguishable"),
        )
        for mean, lower, upper, label in cases:
            cell = {"mean_difference_bps": mean, "interval": {"lower": lower, "upper": upper}}
            with self.subTest(mean=mean, lower=lower, upper=upper):
                self.assertEqual(fp.crps_verdict(cell), label)
                self.assertEqual(fp.crps_result(label), "pass" if label == "pass" else "fail")

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
