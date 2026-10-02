"""The lockbox guard: no scoring entry point scores a locked day.

`docs/decisions/lockbox.md` locks two tiers, `metadata/lockbox.json` declares
them, and `repo_model.lockbox.require_unlocked` refuses a scored day in a tier
whose `opened` is `null`. This module runs against the **tracked**
declaration: it does not use `lockbox_support`, so every panel below that
reaches 2026 reaches the real near-blind tier.

What is held here:

* the tracked declaration loads, says what the decision record says, and a
  malformed one is a `DataContractError`;
* every scoring entry point raises `LookAheadError` on a panel whose scored
  days reach 2026-01-01, naming the tier and the first offending date, before
  any model is fitted, and scores the same panel when its scored days stop
  before the tier;
* the entry points are enumerated, and the enumeration is checked against the
  code: a new function that selects scored days, or a new CLI subcommand, fails
  here until it is classified;
* an opened tier is allowed, and opening needs a ruling reference.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import tempfile
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from unittest import mock

from repo_model import cli, lockbox
from repo_model.contract import event_window_digest
from repo_model.baseline import (
    climatology_exceedance,
    fit,
    paired_model_comparison,
    rolling_exceedance_backtest,
    rolling_persistence_backtest,
)
from repo_model.data import DailyObservation, DataContractError
from repo_model.event_eval import evaluate_event_window, load_event_windows
from repo_model.splits import LookAheadError
from repo_model.tail_diagnostics import refit_knots

from test_baseline import record_date_registry
from test_cli_eval import EventHoldoutHarness, THRESHOLDS

SRC = Path(__file__).resolve().parents[1] / "src" / "repo_model"
TRACKED = Path(__file__).resolve().parents[1] / "metadata" / "lockbox.json"

FEATURES = ("spread_bps",)
DECISION_TIME = time(16, 0)
TAUS = (5.0, 10.0, 20.0, 50.0)
MINIMUM_HISTORY = 10
FIRST_LOCKED = date(2026, 1, 1)


def crossing_panel(start=date(2025, 12, 1), count=45):
    """Consecutive calendar days from `start`, across 2026-01-01."""

    return [
        DailyObservation(
            start + timedelta(days=index),
            {"sofr": 4.30 + 0.0001 * ((index * 7) % 13), "iorb": 4.30},
        )
        for index in range(count)
    ]


REGISTRY = record_date_registry(0, FEATURES)


#: Every counter made by the entry points below, so a test can read the fits
#: an entry point made before it raised.
COUNTERS = []


class CountingFitter:
    """`baseline.fit`, counting its calls: the refusal comes before any fit."""

    def __init__(self):
        self.calls = 0
        COUNTERS.append(self)

    def __call__(self, train, minimum_history=20):
        self.calls += 1
        return fit(train, minimum_history=minimum_history)


class CountingPredictor:
    """The climatology exceedance predictor, counting its calls."""

    def __init__(self):
        self.calls = 0
        COUNTERS.append(self)
        self._inner = climatology_exceedance(minimum_history=MINIMUM_HISTORY)

    def __call__(self, train, rows, taus):
        self.calls += 1
        return self._inner(train, rows, taus)


def _window(start, end, name="lockbox-window"):
    entry = {
        "name": name,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "checksum": event_window_digest(name, start.isoformat(), end.isoformat()),
    }
    return load_event_windows({"version": 1, "windows": [entry]})[0]


# --------------------------------------------------------------------------
# The library entry points. Each takes the panel and an optional `end`, and
# returns the number of fits it made. Adding a scoring entry point means adding
# it here; `EnumerationTests` fails until it is.
# --------------------------------------------------------------------------


def _persistence(rows, end=None):
    fitter = CountingFitter()
    rolling_persistence_backtest(
        rows,
        features=FEATURES,
        registry=REGISTRY,
        decision_time=DECISION_TIME,
        minimum_history=MINIMUM_HISTORY,
        fit_model=fitter,
        end=end,
    )
    return fitter.calls


def _exceedance(rows, end=None):
    predictor = CountingPredictor()
    rolling_exceedance_backtest(
        rows,
        predictor=predictor,
        model_name="climatology",
        features=FEATURES,
        registry=REGISTRY,
        decision_time=DECISION_TIME,
        taus=TAUS,
        minimum_history=MINIMUM_HISTORY,
        end=end,
    )
    return predictor.calls


def _paired(rows, end=None):
    fit_a, fit_b = CountingFitter(), CountingFitter()
    paired_model_comparison(
        rows,
        model_a="persistence",
        fit_a=fit_a,
        features_a=FEATURES,
        model_b="persistence-again",
        fit_b=fit_b,
        features_b=FEATURES,
        registry=REGISTRY,
        decision_time=DECISION_TIME,
        seed=1,
        minimum_history=MINIMUM_HISTORY,
        end=end,
    )
    return fit_a.calls + fit_b.calls


def _event_window(rows, end=None):
    # Five days across 2026-01-01, or the five days up to `end`.
    if end is None:
        start, last = date(2025, 12, 29), date(2026, 1, 2)
    else:
        start, last = end - timedelta(days=4), end
    predictor = CountingPredictor()
    with tempfile.TemporaryDirectory() as directory:
        evaluate_event_window(
            rows,
            predictor,
            _window(start, last),
            features=FEATURES,
            registry=REGISTRY,
            decision_time=DECISION_TIME,
            taus=TAUS,
            model_config={"model": "climatology"},
            journal_path=Path(directory) / "journal.jsonl",
        )
    return predictor.calls


def _refit_knots(rows, end=None):
    declaration = {
        "features": list(FEATURES),
        "minimum_history": MINIMUM_HISTORY,
        "decision_time": DECISION_TIME.isoformat(timespec="minutes"),
        "refit_every": 1,
        "taus_bp": list(TAUS),
    }
    if end is not None:
        declaration["end"] = end.isoformat()
    predictor = CountingPredictor()
    # The climatology has no knots to capture, so the first fold reached
    # raises `ValueError` -- past the guard, after one fit -- and that is all
    # this needs: its knots are not what is under test.
    try:
        refit_knots(
            {"declaration": declaration, "derived": {}},
            rows,
            registry=REGISTRY,
            predictor=predictor,
        )
    except LookAheadError:
        raise
    except ValueError:
        pass
    return predictor.calls


#: Every library entry point that scores days, by its qualified name.
LIBRARY_ENTRY_POINTS = {
    "baseline.rolling_persistence_backtest": _persistence,
    "baseline.rolling_exceedance_backtest": _exceedance,
    "baseline.paired_model_comparison": _paired,
    "event_eval.evaluate_event_window": _event_window,
    "tail_diagnostics.refit_knots": _refit_knots,
}

#: Every CLI subcommand that scores days. Each is run below.
SCORING_COMMANDS = ("backtest", "compare", "exceedance-backtest", "event-holdout")

#: Every other CLI subcommand, and why it scores nothing.
NON_SCORING_COMMANDS = {
    "audit": "validates and summarises a panel",
    "fetch": "downloads raw snapshots",
    "build": "builds a panel from snapshots",
    "verify-panel": "checks a panel's digest against its manifest",
    "backfill-nmfp": "backfills raw SEC N-MFP snapshots",
}

#: Functions that read an as-of information set but score nothing, and why.
NOT_ENTRY_POINTS = {
    # Holds the guard itself: every entry point above reaches it.
    "baseline._as_of_folds": "the shared fold loop; calls require_unlocked",
    "ml._held_out_read": "a calibration read inside a fit's own training frame",
}


class TrackedDeclarationTests(unittest.TestCase):
    """`metadata/lockbox.json` says what `docs/decisions/lockbox.md` decided."""

    def test_the_tracked_tiers_are_the_decided_ones_and_both_are_locked(self):
        tiers = lockbox.load_lockbox()
        self.assertEqual(lockbox.DEFAULT_LOCKBOX.resolve(), TRACKED)
        self.assertEqual(
            [(tier.name, tier.start, tier.end, tier.opened) for tier in tiers],
            [
                ("near_blind", date(2026, 1, 1), date(2026, 9, 3), None),
                ("blind", date(2026, 9, 4), None, None),
            ],
        )


class MalformedDeclarationTests(unittest.TestCase):
    """A malformed declaration is a `DataContractError`, never a pass."""

    GOOD = json.loads(TRACKED.read_text(encoding="utf-8"))

    def load(self, document):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lockbox.json"
            path.write_text(
                document if isinstance(document, str) else json.dumps(document),
                encoding="utf-8",
            )
            return lockbox.load_lockbox(path)

    def variant(self, change):
        document = json.loads(json.dumps(self.GOOD))
        change(document)
        return document

    def test_the_tracked_shape_loads(self):
        self.assertEqual(len(self.load(self.GOOD)), 2)

    def test_each_malformation_is_refused(self):
        cases = {
            "not json": "{",
            "not an object": [],
            "no version": self.variant(lambda d: d.pop("version")),
            "boolean version": self.variant(lambda d: d.update(version=True)),
            "no tiers": self.variant(lambda d: d.update(tiers=[])),
            "missing opened": self.variant(lambda d: d["tiers"][0].pop("opened")),
            "extra key": self.variant(lambda d: d["tiers"][0].update(extra=1)),
            "bad start": self.variant(lambda d: d["tiers"][0].update(start="2026-13-01")),
            "end before start": self.variant(
                lambda d: d["tiers"][0].update(end="2025-12-31")
            ),
            "a gap between tiers": self.variant(
                lambda d: d["tiers"][1].update(start="2026-09-05")
            ),
            "open-ended before the last": self.variant(
                lambda d: d["tiers"][0].update(end=None)
            ),
            "duplicate name": self.variant(
                lambda d: d["tiers"][1].update(name="near_blind")
            ),
            "opened without a ruling": self.variant(
                lambda d: d["tiers"][0].update(opened={"date": "2027-01-04"})
            ),
            "opened with an empty ruling": self.variant(
                lambda d: d["tiers"][0].update(
                    opened={"date": "2027-01-04", "ruling": " "}
                )
            ),
            "opened as a bare date": self.variant(
                lambda d: d["tiers"][0].update(opened="2027-01-04")
            ),
        }
        for name, document in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(DataContractError):
                    self.load(document)

    def test_a_missing_file_is_refused(self):
        with self.assertRaises(DataContractError):
            lockbox.load_lockbox(Path("/nonexistent/lockbox.json"))


class LockedScoredDayTests(unittest.TestCase):
    """Every library entry point refuses a locked scored day, before any fit.

    **Red before the guard existed.** Written before `require_unlocked` was
    called anywhere, these failed with `AssertionError: LookAheadError not
    raised` at every entry point: each scored the panel through 2026-01-14.

    **Recorded mutation.** In `src/repo_model/lockbox.py`, `require_unlocked`:

        locked = [tier for tier in load_lockbox(DEFAULT_LOCKBOX) if tier.opened is None]

    mutated to `... if tier.opened is not None]`, so that only opened tiers
    are checked and a locked one never is. Kills
    `test_every_entry_point_refuses_a_locked_scored_day`, which raised
    `AssertionError: LookAheadError not raised` at every entry point.
    """

    def test_every_entry_point_refuses_a_locked_scored_day(self):
        rows = crossing_panel()
        for name, entry in LIBRARY_ENTRY_POINTS.items():
            with self.subTest(entry_point=name):
                with self.assertRaises(LookAheadError) as caught:
                    entry(rows)
                message = str(caught.exception)
                self.assertIn("near_blind", message)
                # The first locked day the entry point would have scored.
                self.assertIn(f"scored day {FIRST_LOCKED}", message)

    def test_the_refusal_comes_before_any_fit(self):
        rows = crossing_panel()
        for name, entry in LIBRARY_ENTRY_POINTS.items():
            with self.subTest(entry_point=name):
                COUNTERS.clear()
                with self.assertRaises(LookAheadError):
                    entry(rows)
                self.assertTrue(COUNTERS)
                self.assertEqual([counter.calls for counter in COUNTERS], [0] * len(COUNTERS))

    def test_every_entry_point_scores_the_same_panel_when_it_stops_before_the_tier(self):
        """The locked rows stay in the panel; only scoring them is refused."""

        rows = crossing_panel()
        for name, entry in LIBRARY_ENTRY_POINTS.items():
            with self.subTest(entry_point=name):
                self.assertGreater(entry(rows, end=date(2025, 12, 31)), 0)

    def test_a_panel_that_ends_before_the_tier_needs_no_end(self):
        rows = [row for row in crossing_panel() if row.date < FIRST_LOCKED]
        for name, entry in LIBRARY_ENTRY_POINTS.items():
            with self.subTest(entry_point=name):
                self.assertGreater(entry(rows), 0)

    def test_the_blind_tier_is_refused_too(self):
        rows = crossing_panel(start=date(2026, 9, 4) - timedelta(days=30))
        with self.assertRaises(LookAheadError) as caught:
            _persistence(rows, end=None)
        # The near-blind tier is reached first; past its end, the blind one.
        self.assertIn("near_blind", str(caught.exception))
        with mock.patch.object(lockbox, "DEFAULT_LOCKBOX", self._opened_near_blind()):
            with self.assertRaises(LookAheadError) as caught:
                _persistence(rows)
        self.assertIn("scored day 2026-09-04 is in the locked blind tier", str(caught.exception))

    def test_an_opened_tier_is_scored(self):
        rows = crossing_panel()
        with mock.patch.object(lockbox, "DEFAULT_LOCKBOX", self._opened_near_blind()):
            self.assertGreater(_persistence(rows), 0)

    def _opened_near_blind(self):
        document = json.loads(TRACKED.read_text(encoding="utf-8"))
        document["tiers"][0]["opened"] = {
            "date": "2026-10-02",
            "ruling": "a test fixture standing in for Eleonora's ruling",
        }
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "lockbox.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return path


class CommandTests(EventHoldoutHarness):
    """Every scoring subcommand refuses a locked day; `--end` scores before it.

    The panel is `EventHoldoutHarness`'s: business days from 2025-11-03, its
    event window in January 2026.
    """

    def argv(self, command, end=None):
        report = str(self.tmp / f"{command}.json")
        common = [
            "--registry", str(self.registry),
            "--decision-time", "16:30",
            "--minimum-history", "10",
        ]
        if command == "backtest":
            argv = ["backtest", str(self.panel), *common, "--model", "persistence",
                    "--feature", "spread_bps", "--report", report]
        elif command == "compare":
            argv = ["compare", str(self.panel), *common,
                    "--model-a", "persistence", "--feature-a", "spread_bps",
                    "--model-b", "persistence", "--feature-b", "spread_bps",
                    "--report", report]
        elif command == "exceedance-backtest":
            argv = ["exceedance-backtest", "--panel", str(self.panel),
                    "--thresholds", str(THRESHOLDS), *common,
                    "--model", "climatology", "--feature", "spread_bps",
                    "--report", report]
        else:
            argv = ["event-holdout", "--panel", str(self.panel),
                    "--events", str(self.events), "--thresholds", str(THRESHOLDS),
                    "--registry", str(self.registry), "--journal", str(self.journal),
                    "--decision-time", "16:30", "--model", "climatology",
                    "--feature", "spread_bps"]
        if end is not None:
            argv += ["--end", end]
        return argv, Path(report)

    def invoke(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, err.getvalue()

    def test_every_scoring_command_refuses_a_locked_day_and_writes_nothing(self):
        for command in SCORING_COMMANDS:
            with self.subTest(command=command):
                argv, report = self.argv(command)
                code, err = self.invoke(argv)
                self.assertEqual(code, 2, msg=err)
                self.assertIn("locked near_blind tier", err)
                self.assertFalse(report.exists())

    def test_end_before_the_tier_scores_and_is_declared(self):
        for command in ("backtest", "compare", "exceedance-backtest"):
            with self.subTest(command=command):
                argv, report = self.argv(command, end="2025-12-31")
                code, err = self.invoke(argv)
                self.assertEqual(code, 0, msg=err)
                document = json.loads(report.read_text(encoding="utf-8"))
                self.assertEqual(document["declaration"]["end"], "2025-12-31")
                # The panel is still the whole file.
                self.assertEqual(document["panel"]["last_date"], self.days[-1].isoformat())

    def test_end_inside_the_tier_is_still_refused(self):
        argv, _ = self.argv("backtest", end="2026-01-05")
        code, err = self.invoke(argv)
        self.assertEqual(code, 2)
        self.assertIn("locked near_blind tier", err)

    def test_no_flag_opens_the_tier(self):
        """No option of a scoring command names the lockbox or opens a tier."""

        parser = cli.build_parser()
        subparsers = next(
            action for action in parser._actions if hasattr(action, "choices")
            and isinstance(action.choices, dict)
        )
        for command in SCORING_COMMANDS:
            options = {
                option
                for action in subparsers.choices[command]._actions
                for option in action.option_strings
            }
            with self.subTest(command=command):
                self.assertFalse(
                    [o for o in options if "lock" in o or "open" in o or "unlock" in o]
                )


class EnumerationTests(unittest.TestCase):
    """The entry points above are all of them, checked against the code."""

    def test_every_function_that_selects_scored_days_is_classified(self):
        """A function reading an as-of information set or the fold loop.

        `InformationRule.information_set` is what turns a scored row into its
        reads, and `_as_of_folds` is the fold loop built on it; a function
        that calls either outside `asof.py` selects days to score, or reads
        inside a fit. Each must be an entry point above or be named, with a
        reason, in `NOT_ENTRY_POINTS`.
        """

        found = set()
        for path in sorted(SRC.glob("*.py")):
            if path.name == "asof.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for call in ast.walk(node):
                    if not isinstance(call, ast.Call):
                        continue
                    name = getattr(call.func, "attr", getattr(call.func, "id", None))
                    if name in ("information_set", "_as_of_folds", "fold_grid"):
                        found.add(f"{path.stem}.{node.name}")
        self.assertEqual(
            found, set(LIBRARY_ENTRY_POINTS) | set(NOT_ENTRY_POINTS),
            "classify each new function as a scoring entry point (and add it "
            "to LIBRARY_ENTRY_POINTS) or as NOT_ENTRY_POINTS with a reason",
        )

    def test_every_cli_subcommand_is_classified(self):
        parser = cli.build_parser()
        subparsers = next(
            action for action in parser._actions if hasattr(action, "choices")
            and isinstance(action.choices, dict)
        )
        self.assertEqual(
            set(subparsers.choices),
            set(SCORING_COMMANDS) | set(NON_SCORING_COMMANDS),
            "classify each new subcommand as scoring (and run it in "
            "CommandTests) or as non-scoring with a reason",
        )

    def test_the_scoring_entry_points_take_no_lockbox_argument(self):
        """Opening is by the tracked file only, never by a call's argument."""

        import inspect

        from repo_model import baseline, event_eval, tail_diagnostics

        modules = {
            "baseline": baseline,
            "event_eval": event_eval,
            "tail_diagnostics": tail_diagnostics,
        }
        for name in LIBRARY_ENTRY_POINTS:
            module, function = name.split(".")
            parameters = inspect.signature(getattr(modules[module], function)).parameters
            with self.subTest(entry_point=name):
                self.assertFalse([p for p in parameters if "lock" in p or "open" in p])


if __name__ == "__main__":
    unittest.main()
