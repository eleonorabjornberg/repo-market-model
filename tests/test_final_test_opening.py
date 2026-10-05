"""The final test's opening (#151): its reported-only cells and its record.

`scripts/final_test_opening.py` scores every cell of the final test other than
the primary one, which the frozen command and `final_test_preregistration.py
crps` score. These tests read no panel: the labels and guards run on synthetic
inputs, and the record is checked against itself and the frozen declaration.

Written after the script: the script had to score the opening run before its
record existed. The two lockbox checks below are its new guards, each with a
recorded mutation.

Mutation record (`WindowGuardTests`, the window's lockbox check):
`lockbox.require_unlocked(days, where="final test opening")` in
`_window_positions` deleted, confirmed applied by grep; the test
`test_a_locked_window_is_refused` then failed with `AssertionError`
("LookAheadError not raised"). Restored, green.

Mutation record (`WindowGuardTests`, the distribution walk's lockbox check):
`lockbox.require_unlocked([dates[index] for index in grid], ...)` in
`distribution_walk` deleted, confirmed applied by grep; the test
`test_the_walk_refuses_a_blind_tier_day_before_any_fit` then failed with
`AssertionError` ("a fit was reached before the lockbox check"). Restored, green.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
RECORD = REPO / "docs" / "runs" / "final_test_near_blind.json"


def _script():
    spec = importlib.util.spec_from_file_location(
        "final_test_opening", REPO / "scripts" / "final_test_opening.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


op = _script()
fp = op.fp


def _window_days():
    days, day = [], date(2026, 1, 2)
    while len(days) < fp.CRPS_WINDOW_DAYS:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def _locked_lockbox(scratch):
    """The tracked declaration with the near-blind tier locked again."""

    path = Path(scratch) / "lockbox.json"
    document = json.loads((REPO / "metadata" / "lockbox.json").read_text(encoding="utf-8"))
    for tier in document["tiers"]:
        tier["opened"] = None
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


class LabelTests(unittest.TestCase):
    """The second amendment's three labels, and "inconclusive" below the minimum."""

    @staticmethod
    def _paired(mean, lower, upper):
        return {"mean": mean, "interval": {"lower": lower, "upper": upper}}

    def test_the_three_labels(self):
        cases = (
            ((0.2, 0.01, 0.4), "shown better"),
            ((0.2, -0.01, 0.4), "not shown"),
            ((-0.2, -0.4, 0.01), "not shown"),
            ((-0.2, -0.4, -0.01), "shown worse"),
            # An interval above 0 around a mean that is not above 0 is not a pass.
            ((0.0, 0.01, 0.4), "not shown"),
        )
        for args, expected in cases:
            with self.subTest(args=args):
                self.assertEqual(op.label(self._paired(*args), events=op.onset.MINIMUM_EVENTS),
                                 expected)

    def test_below_the_minimum_event_count_every_cell_is_inconclusive(self):
        clear = self._paired(0.2, 0.1, 0.3)
        self.assertEqual(op.label(clear, events=op.onset.MINIMUM_EVENTS - 1), "inconclusive")
        self.assertEqual(op.label(clear, events=op.onset.MINIMUM_EVENTS), "shown better")
        self.assertEqual(op.label(clear), "shown better")


class WindowGuardTests(unittest.TestCase):
    """No locked day is scored: the window's and the walk's own lockbox checks."""

    def test_the_window_is_the_near_blind_tier(self):
        days = [date(2025, 12, 31)] + _window_days() + [date(2026, 9, 4)]
        positions = op._window_positions(days)
        self.assertEqual(positions, list(range(1, 1 + fp.CRPS_WINDOW_DAYS)))

    def test_a_window_of_the_wrong_length_is_refused(self):
        with self.assertRaises(ValueError):
            op._window_positions(_window_days()[:-1])

    def test_a_locked_window_is_refused(self):
        with tempfile.TemporaryDirectory() as scratch, \
                mock.patch.object(op.lockbox, "DEFAULT_LOCKBOX", _locked_lockbox(scratch)):
            with self.assertRaises(LookAheadError):
                op._window_positions(_window_days())

    def test_the_walk_refuses_a_blind_tier_day_before_any_fit(self):
        rows = [SimpleNamespace(date=day) for day in (date(2026, 9, 3), date(2026, 9, 4))]

        def unreachable(*args, **kwargs):
            raise AssertionError("a fit was reached before the lockbox check")

        stub = SimpleNamespace(
            DECISION=fp.DECISION,
            _resolve_fields=lambda declared: ({}, ()),
            InformationRule=lambda *args, **kwargs: None,
            require_refit_every=lambda refit: refit,
            fold_grid=lambda dates, registry, **kwargs: [0, 1],
            _reads_information=unreachable,
            refit_blocks=unreachable,
        )
        with mock.patch.object(op, "live_record", stub):
            with self.assertRaises(LookAheadError):
                op.distribution_walk(rows, fit=None, features=("spread_bps",),
                                     online_calibration=None, registry={}, horizon=2,
                                     minimum_history=61, refit_every=21)


class RecordTests(unittest.TestCase):
    """The published record is the frozen run's, and its primary cell recomputes."""

    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.cell = cls.record["primary"]["cell"]

    def test_it_was_scored_under_both_frozen_declarations(self):
        self.assertEqual(self.record["crps_declaration_sha256"], fp.crps_declaration_checksum())
        self.assertEqual(self.record["declaration_sha256"], fp.declaration_checksum())
        self.assertEqual(self.record["primary"]["command"], list(fp.CRPS_COMMAND))
        self.assertEqual(self.record["primary"]["compare_record"]["panel"]["sha256"],
                         fp._frozen_panel_sha256())
        self.assertEqual(self.record["cells"], fp.cells())

    def test_the_opening_is_the_tracked_one(self):
        tracked = json.loads((REPO / "metadata" / "lockbox.json").read_text(encoding="utf-8"))
        near_blind = next(t for t in tracked["tiers"] if t["name"] == "near_blind")
        blind = next(t for t in tracked["tiers"] if t["name"] == "blind")
        self.assertEqual(self.record["opened"], near_blind["opened"])
        self.assertIsNone(blind["opened"])

    def test_the_primary_cell_recomputes_from_its_window(self):
        from repo_model import baseline, metrics

        window = self.record["primary"]["window_per_origin"]
        self.assertEqual(len(window), fp.CRPS_WINDOW_DAYS)
        self.assertEqual((window[0]["scored_date"], window[-1]["scored_date"]),
                         (self.cell["first"], self.cell["last"]))
        differences = [float(entry["difference_bps"]) for entry in window]
        mean = sum(differences) / len(differences)
        self.assertAlmostEqual(mean, self.cell["mean_difference_bps"], places=12)
        lower, upper = metrics.stationary_bootstrap_interval(
            lambda idx: sum(differences[i] for i in idx) / len(idx), len(differences),
            block_length=fp.CRPS_BLOCK_LENGTH, seed=fp._crps_seed(),
            replications=baseline.BOOTSTRAP_REPLICATIONS, level=baseline.BOOTSTRAP_LEVEL,
        )
        self.assertAlmostEqual(lower, self.cell["interval"]["lower"], places=12)
        self.assertAlmostEqual(upper, self.cell["interval"]["upper"], places=12)
        self.assertEqual(fp.crps_verdict(self.cell), self.cell["verdict"])
        self.assertEqual(fp.crps_result(self.cell["verdict"]), self.cell["result"])

    def test_the_claim_is_stated_only_on_a_pass(self):
        expected = fp.CRPS_CLAIM if self.cell["result"] == "pass" else None
        self.assertEqual(self.record["primary"]["claim"], expected)

    def test_every_reported_cell_is_reported_only(self):
        self.assertEqual([d["horizon"] for d in self.record["events_reported_only"]],
                         list(op.HORIZONS))
        self.assertEqual([d["horizon"] for d in self.record["crps_reported_only"]],
                         list(op.HORIZONS[1:]))
        for document in self.record["events_reported_only"]:
            self.assertEqual(document["cell_role"], "reported only")
            self.assertEqual(document["window"]["days"], fp.CRPS_WINDOW_DAYS)
        for cell in self.record["crps_reported_only"]:
            self.assertEqual(cell["cell_role"], "reported only")
            self.assertEqual(cell["verdict_label"], op.NOT_EVIDENCE)
            self.assertEqual(cell["days"], fp.CRPS_WINDOW_DAYS)

    def test_assemble_refuses_a_cell_scored_under_another_declaration(self):
        with tempfile.TemporaryDirectory() as scratch:
            scratch = Path(scratch)
            (scratch / "cell.json").write_text(json.dumps(
                {"crps_declaration_sha256": "0" * 64, "cell": self.cell}), encoding="utf-8")
            (scratch / "compare.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                op.main(["assemble", "--cell", str(scratch / "cell.json"),
                         "--compare", str(scratch / "compare.json"),
                         "--events", str(scratch / "none.json"),
                         "--crps", str(scratch / "none.json"),
                         "--output", str(scratch / "out.json")])


if __name__ == "__main__":
    unittest.main()
