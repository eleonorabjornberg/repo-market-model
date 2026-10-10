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
  code (`src/repo_model/` and `scripts/`): a new function that selects scored
  days, or a new CLI subcommand, fails here until it is classified;
* an opened tier is allowed, and opening needs a ruling reference.

**Since #151 opened the near-blind tier** (2026-10-05, Eleonora's "GO #151"),
the tracked declaration locks the blind tier only. `TrackedDeclarationTests`
and `TrackedGuardTests` hold that. The guard tests (`LockedScoredDayTests`,
`CommandTests`, `ScriptTests`) keep their synthetic panels, dated around
2026-01-01, and score them under `relocked_declaration`: the tracked file with
every tier's `opened` set back to `null`, as it stood before #151. Their
refusals and mutation records are unchanged.
"""

from __future__ import annotations

import ast
import contextlib
import csv
import importlib.util
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
from test_cli_eval import EventHoldoutHarness, PANEL_COLUMNS, THRESHOLDS, business_days

SRC = Path(__file__).resolve().parents[1] / "src" / "repo_model"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
TRACKED = Path(__file__).resolve().parents[1] / "metadata" / "lockbox.json"

FEATURES = ("spread_bps",)
DECISION_TIME = time(16, 0)


def relocked_declaration(testcase):
    """The tracked declaration with every tier locked, as it stood before #151.

    Patched in as `lockbox.DEFAULT_LOCKBOX` for the rest of `testcase`.
    """

    document = json.loads(TRACKED.read_text(encoding="utf-8"))
    for tier in document["tiers"]:
        tier["opened"] = None
    directory = tempfile.TemporaryDirectory()
    testcase.addCleanup(directory.cleanup)
    path = Path(directory.name) / "lockbox.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    patcher = mock.patch.object(lockbox, "DEFAULT_LOCKBOX", path)
    patcher.start()
    testcase.addCleanup(patcher.stop)
    return path
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


class CountingDays:
    """The scored days `scarcity.pressure_days_by_state` returned, as a count.

    It fits nothing, so what is counted is the days it paired with a state:
    zero when the lockbox refused it, which it does before reading any.
    """

    def __init__(self):
        self.calls = 0
        COUNTERS.append(self)


def _scarcity_pressure_days(rows, end=None):
    from repo_model.scarcity import measurement_declaration, pressure_days_by_state

    counter = CountingDays()
    with measurement_declaration():
        features = ("spread_bps", "reserve_scarcity_state")
        registry = record_date_registry(0, features)
        rows = [
            DailyObservation(row.date, {**row.values, "reserve_scarcity_state": 0.0})
            for row in rows
        ]
        scored = pressure_days_by_state(
            rows,
            registry=registry,
            decision_time=DECISION_TIME,
            minimum_history=MINIMUM_HISTORY,
            end=end,
        )
    counter.calls = len(scored)
    return counter.calls


#: Every library entry point that scores days, by its qualified name.
LIBRARY_ENTRY_POINTS = {
    "baseline.rolling_persistence_backtest": _persistence,
    "baseline.rolling_exceedance_backtest": _exceedance,
    "baseline.paired_model_comparison": _paired,
    "event_eval.evaluate_event_window": _event_window,
    "tail_diagnostics.refit_knots": _refit_knots,
    "scarcity.pressure_days_by_state": _scarcity_pressure_days,
}

#: Every tracked script function that walks the fold grid to score, as
#: `scripts/<file>.<function>`. Each reaches the guard through `_as_of_folds`
#: and is run below (`ScriptTests`).
SCRIPT_ENTRY_POINTS = (
    "scripts/spread_change_autocorrelation.main",
    "scripts/threshold_regime_sizes.main",
)

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
    "scripts/pressure_judge._scarcity_states": (
        "reads the reserve-scarcity state on the fold grid, to label the judge's groups "
        "(#375); scores nothing, it ends at the declared last scored day through "
        "_as_of_folds, which calls require_unlocked, and pressure_judge.judge guards the "
        "scored days itself"
    ),
    "scripts/pressure_audit.inputs_command": (
        "tabulates what each input reads at the 16:00 decision and how the value read ranks the +5 bp "
        "onsets, on the judge's scored days (#473); scores no forecast, it ends at the declared last "
        "scored day, calls require_unlocked on it before the first read, and refuses a scratch panel "
        "whose spread is not the published panel's"
    ),
    "scripts/pressure_track_m.states_command": (
        "tabulates the filtered state against #115's state on the fold grid (#384); scores "
        "nothing, it ends at the declared last scored day through _as_of_folds, which calls "
        "require_unlocked, and drops every row after that day before it starts"
    ),
    "pressure_hazard._decisions": (
        "reads each training decision's as-of covariates inside a fit's own training "
        "frame (#387), as ml._pressure_pairs does; scores nothing, the backtest that "
        "calls the predictor guards the scored days"
    ),
    "pressure_hazard.gap_to_anchor": (
        "measures the rule's scored-day-to-anchor distance on a synthetic run of "
        "business days (#387); reads no panel row and scores nothing"
    ),
    "ml._held_out_read": "a calibration read inside a fit's own training frame",
    "ml._pressure_pairs": (
        "builds the direct pressure models' training pairs inside a fit's own "
        "training frame (#114); scores nothing, the backtest that calls the "
        "predictor guards the scored days"
    ),
    "ml._dynamic_rows": (
        "builds the dynamic pressure models' design rows and anchors inside a "
        "fit's own as-of frames (#137); scores nothing, the backtest that calls "
        "the predictor guards the scored days"
    ),
    "ml._held_out_mask": (
        "lists the training values before a calibration block that a held-out "
        "row could not yet see, inside a fit's own training frame (#78); "
        "selects and scores nothing, the held-out rows come from _held_out_read"
    ),
    "ml._direct_pairs": (
        "builds direct training pairs inside a fit's own training frame (#37); "
        "scores nothing, the backtest that calls the forecaster guards the scored days"
    ),
    "scripts/reserves_sensitivity.measure": (
        "fits the published gbm at fixed folds on days before 2026 and re-reads one "
        "feature row, scoring nothing (#267); refuses any day on or after 2026-01-01 itself"
    ),
    "scripts/calibration_masking_exposure.exposure": (
        "counts masked training pairs per refit block; scores nothing"
    ),
    "scripts/live_record.forecast_run": (
        "the live record's forecast loop (#215): trains and forecasts as the as-of "
        "information set allows, computes no metric and scores no day "
        "(docs/decisions/lockbox.md); scripts/live_score.py scores the record, "
        "through `lockbox.require_unlocked` on days `metadata/lockbox.json` has opened (#277)"
    ),
    "scripts/live_record.distribution_run": (
        "the live record's distribution loop (#215): trains and forecasts the published "
        "distribution and as-of persistence as the as-of information set allows, "
        "computes no loss and scores no day (docs/decisions/lockbox.md); "
        "scripts/live_score.py scores the record, through `lockbox.require_unlocked` on days `metadata/lockbox.json` has opened (#277)"
    ),
    "scripts/live_record.require_reads_on_real_rows": (
        "checks one live forecast's reads against the placeholder rows (#215); "
        "selects and scores nothing"
    ),
    "scripts/source_screen.read_series": (
        "reads each series as of the decision instant on the lead-1 fold grid, for the exploratory "
        "source screen (#478); selects no model and scores no forecast, calls "
        "lockbox.require_unlocked on every day before it reads one, and the screen's `run` refuses "
        "a panel that runs past 2025-12-31 (tests/test_source_screen.py)"
    ),
    "scripts/source_screen.probe": (
        "asks the as-of rule, on the one middle row of the panel, whether a column has a "
        "row-relative availability; reads one row, scores and selects nothing (#478)"
    ),
    "scripts/emit_visual.newcomer_n2": (
        "draws the scored grid on the explorer's N2 (#143); scores and compares "
        "nothing, and leaves locked days out of every count through `counted` "
        "(tests/test_visual.py, NewcomerN2Tests)"
    ),
    "scripts/onset_post_mortem.as_of_reads": (
        "reads each scored day's as-of state and calendar for the descriptive "
        "onset post-mortem (#214); compares nothing, and walks _as_of_folds, "
        "which refuses a locked day (tests/test_onset_post_mortem.py)"
    ),
    "scripts/final_test_opening.distribution_walk": (
        "the final test opening's walk of the published distribution and as-of "
        "persistence at h = 2 to 5 (#151), reported only; it refuses a locked "
        "scored day itself before any fit (tests/test_final_test_opening.py, "
        "WindowGuardTests)"
    ),
    "scripts/onset_post_mortem.gauge_history": (
        "finds the first fold-grid day whose state is public (#214); reads no "
        "outcome and scores nothing, as_of_reads walks the guarded grid"
    ),
    "scripts/desk_outputs.distribution_history": (
        "the desk outputs' walk of the published distribution and as-of "
        "persistence at h = 1 to 5 (#232), reporting only; it refuses a locked "
        "scored day itself before any fit (tests/test_desk_outputs.py, "
        "DistributionHistoryLockboxTests, which calls the walk across a blind-tier "
        "day with the fit stubbed unreachable)"
    ),
    "scripts/desk_outputs.scarcity_at": (
        "reads the declared scarcity state as of one forecast's decision instant "
        "(#232) for display beside it; reads no outcome and scores nothing"
    ),
}


class TrackedDeclarationTests(unittest.TestCase):
    """`metadata/lockbox.json` says what `docs/decisions/lockbox.md` decided."""

    def test_the_tracked_tiers_are_the_decided_ones_and_only_the_blind_one_is_locked(self):
        tiers = lockbox.load_lockbox()
        self.assertEqual(lockbox.DEFAULT_LOCKBOX.resolve(), TRACKED)
        self.assertEqual(
            [(tier.name, tier.start, tier.end) for tier in tiers],
            [
                ("near_blind", date(2026, 1, 1), date(2026, 9, 3)),
                ("blind", date(2026, 9, 4), None),
            ],
        )
        # Opened once, by #151, on Eleonora's go; the blind tier stays locked.
        opened_on, ruling = tiers[0].opened
        self.assertEqual(opened_on, date(2026, 10, 5))
        self.assertIn("GO #151", ruling)
        self.assertIsNone(tiers[1].opened)


class PreOpeningFixtureTests(unittest.TestCase):
    """`lockbox_support.PRE_OPENING_LOCKBOX` is the tracked declaration with both tiers locked."""

    def test_it_differs_from_the_tracked_file_only_in_opened(self):
        from lockbox_support import PRE_OPENING_LOCKBOX

        tracked = json.loads(TRACKED.read_text(encoding="utf-8"))
        fixture = json.loads(PRE_OPENING_LOCKBOX.read_text(encoding="utf-8"))
        self.assertEqual(fixture["version"], tracked["version"])
        self.assertEqual(
            [{k: v for k, v in tier.items() if k != "opened"} for tier in fixture["tiers"]],
            [{k: v for k, v in tier.items() if k != "opened"} for tier in tracked["tiers"]],
        )
        self.assertEqual([tier["opened"] for tier in fixture["tiers"]], [None, None])
        self.assertEqual([tier.name for tier in lockbox.locked_tiers(PRE_OPENING_LOCKBOX)],
                         ["near_blind", "blind"])


class TrackedGuardTests(unittest.TestCase):
    """Under the tracked declaration a near-blind day scores and a blind-tier day is refused."""

    def test_a_near_blind_day_is_ordinary_history(self):
        lockbox.require_unlocked([date(2026, 1, 2), date(2026, 9, 3)], where="test")

    def test_a_blind_tier_day_is_refused(self):
        with self.assertRaises(LookAheadError) as caught:
            lockbox.require_unlocked([date(2026, 9, 3), date(2026, 9, 4)], where="test")
        self.assertIn("scored day 2026-09-04 is in the locked blind tier", str(caught.exception))


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

    Scored under `relocked_declaration` since #151 opened the near-blind tier.
    """

    def setUp(self):
        relocked_declaration(self)

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


class LockedTierTests(unittest.TestCase):
    """`locked_tiers` and `locked_tier`: the helper a page uses to hold locked days out of its counts.

    Not a scoring entry point: it selects nothing and refuses nothing. It tells
    a descriptive page (`scripts/emit_visual.py`) which days to grey and leave
    out of every count, read from a declaration the caller names.
    """

    def declaration(self, opened=()):
        document = json.loads(TRACKED.read_text(encoding="utf-8"))
        for tier in document["tiers"]:
            tier["opened"] = None
            if tier["name"] in opened:
                tier["opened"] = {"date": "2026-10-02",
                                  "ruling": "a test fixture standing in for Eleonora's ruling"}
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "lockbox.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def test_the_tracked_declaration_locks_the_blind_tier_only(self):
        self.assertEqual([tier.name for tier in lockbox.locked_tiers()], ["blind"])

    def test_an_opened_tier_is_ordinary_history(self):
        tiers = lockbox.locked_tiers(self.declaration(opened=("near_blind",)))
        self.assertEqual([tier.name for tier in tiers], ["blind"])
        self.assertIsNone(lockbox.locked_tier(date(2026, 3, 2), tiers))
        self.assertEqual(lockbox.locked_tier(date(2026, 9, 4), tiers).name, "blind")

    def test_each_day_is_placed_in_its_tier(self):
        tiers = lockbox.locked_tiers(self.declaration())
        self.assertIsNone(lockbox.locked_tier(date(2025, 12, 31), tiers))
        self.assertEqual(lockbox.locked_tier(date(2026, 1, 1), tiers).name, "near_blind")
        self.assertEqual(lockbox.locked_tier(date(2026, 9, 3), tiers).name, "near_blind")
        self.assertEqual(lockbox.locked_tier(date(2026, 9, 4), tiers).name, "blind")
        self.assertEqual(lockbox.locked_tier(date(2031, 1, 1), tiers).name, "blind")

    def test_no_locked_tier_locks_nothing(self):
        tiers = lockbox.locked_tiers(self.declaration(opened=("near_blind", "blind")))
        self.assertEqual(tiers, ())
        self.assertIsNone(lockbox.locked_tier(date(2026, 1, 1), tiers))


class CommandTests(EventHoldoutHarness):
    """Every scoring subcommand refuses a locked day; `--end` scores before it.

    The panel is `EventHoldoutHarness`'s: business days from 2025-11-03, its
    event window in January 2026. Scored under `relocked_declaration` since
    #151 opened the near-blind tier.
    """

    def setUp(self):
        super().setUp()
        relocked_declaration(self)

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


def _load_script(name):
    """A tracked script as a module, without running it."""

    spec = importlib.util.spec_from_file_location(
        f"lockbox_script_{name}", SCRIPTS / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScriptTests(EventHoldoutHarness):
    """Every script in `SCRIPT_ENTRY_POINTS` walks its folds as far as the guard.

    The panel is business days from 2025-06-02 into January 2026, read under
    the tracked registry. Run
    whole, each script's fold walk reaches the guard and is refused; with
    `--end` before the tier, it walks to its end and reports. So a change to
    `_as_of_folds`'s signature, or a script that stops reaching the guard,
    fails here rather than on the next hand run. Scored under
    `relocked_declaration` since #151 opened the near-blind tier.
    """

    def setUp(self):
        super().setUp()
        relocked_declaration(self)
        # Long enough before the tier for a two-regime fit at the first origin.
        self.days = business_days(date(2025, 6, 2), 170)
        self.panel = self.write_panel()

    def write_panel(self, path=None):
        """Business days into 2026, with spread and volume that move every day.

        The scripts estimate autocorrelations and fit a threshold, so a
        constant stretch would divide by zero; the values are otherwise
        arbitrary, and nothing here pins a number.
        """

        path = path or self.tmp / "panel.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(PANEL_COLUMNS)
            for index, when in enumerate(self.days):
                spread = 3.0 + ((index * 7) % 11) * 0.5
                volume = 2000 + ((index * 5) % 13) * 25
                writer.writerow(
                    [when.isoformat(), round(4.30 + spread / 100.0, 6), 4.30,
                     volume, 4.30 + (index % 3) * 0.001, 4.32, 4.30, 4.31,
                     3200, 720, 115, "", "", "", 0, 0]
                )
        return path

    #: The tracked registry: the scripts read theirs through
    #: `load_source_registry`, which refuses the harness's unevidenced one.
    REGISTRY = Path(__file__).resolve().parents[1] / "metadata" / "sources.json"

    def argv(self, entry, end=None):
        argv = [
            "--panel", str(self.panel),
            "--registry", str(self.REGISTRY),
            "--decision-time", "16:00",
            "--minimum-history", "60",
        ]
        if entry == "scripts/spread_change_autocorrelation.main":
            argv += ["--feature", "spread_bps", "--lags", "2"]
        else:
            argv += [
                "--feature", "spread_bps", "--feature", "sofr_volume",
                "--feature", "sofr_p25", "--regime-variable", "sofr_volume", "--every", "1000",
            ]
        if end is not None:
            argv += ["--end", end]
        return argv

    def run_script(self, entry, end=None):
        name, function = entry[len("scripts/"):].split(".")
        main = getattr(_load_script(name), function)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(self.argv(entry, end))
        return code, out.getvalue()

    def test_every_script_refuses_a_locked_scored_day(self):
        for entry in SCRIPT_ENTRY_POINTS:
            with self.subTest(entry_point=entry):
                with self.assertRaises(LookAheadError) as caught:
                    self.run_script(entry)
                message = str(caught.exception)
                self.assertIn("locked near_blind tier", message)
                self.assertIn(entry.split(".")[0], message)

    def test_every_script_walks_to_an_end_before_the_tier(self):
        for entry in SCRIPT_ENTRY_POINTS:
            with self.subTest(entry_point=entry):
                code, out = self.run_script(entry, end="2025-12-31")
                self.assertEqual(code, 0)
                self.assertTrue(json.loads(out))

    def test_end_inside_the_tier_is_still_refused(self):
        for entry in SCRIPT_ENTRY_POINTS:
            with self.subTest(entry_point=entry):
                with self.assertRaises(LookAheadError):
                    self.run_script(entry, end="2026-01-05")


#: What a function that computes a CRPS (or the live scorer's guard) is, as the lockbox scan sees it
#: (#257, second review finding 4). `"guard"`: the function calls a guard itself, so it refuses a
#: locked scored day. `"delegates"`: it computes a loss on days some other function chose; the reason
#: names the function that chose them and refuses a locked day. Added with the live scorer's own
#: guard, which `LIBRARY_ENTRY_POINTS` and `SCRIPT_ENTRY_POINTS` do not see: the scan above looks for
#: `information_set` and the fold loop, and `live_score.score` and `score_crps` read neither.
CRPS_CALLERS = frozenset({"crps_from_quantiles", "crps_trapezoid_from_quantiles",
                          "crps_from_record", "integral_crps_from_record",
                          "_require_scored_days_unlocked"})
GUARD_CALLS = frozenset({"require_unlocked", "_require_scored_days_unlocked", "_as_of_folds"})
_WALK = "scores the days `final_test_opening.distribution_walk` walks, which calls lockbox.require_unlocked before any fit"
_FOLDS = "scores the days `baseline.rolling_persistence_backtest` walks, which refuses a locked day through `_as_of_folds`"
CRPS_SCORERS = {
    "scripts/live_score.score_crps": ("guard", "the live CRPS cells: `_require_scored_days_unlocked` before any cell is computed (#277)"),
    "scripts/live_score.score": ("guard", "the live Brier event cells: `_require_scored_days_unlocked` before any cell is computed (#277)"),
    "baseline.rolling_persistence_backtest": ("guard", "the CRPS fold loop: `_as_of_folds` refuses a locked scored day"),
    "scripts/live_score.score_v2": ("guard", "v2's live CRPS cells: `_require_scored_days_unlocked` before any cell is computed (#245)"),
    "scripts/nowcast.score_command": ("guard", "scores the nowcast walks' CRPS after `require_unlocked` on the last scored day (2025-12-31), and refuses a walk or panel that runs past it (#445)"),
    "scripts/live_score.v2_crps": ("delegates", "one v2 record's loss at an outcome `score_v2` supplies, after its guard"),
    "scripts/live_score.crps_from_record": ("delegates", "one record's loss at an outcome `score_crps` supplies, after its guard"),
    "scripts/live_score.integral_crps_from_record": ("delegates", "one record's integral loss at an outcome `score_crps` supplies, after its guard"),
    "baseline._crps_at": ("delegates", "the loss callback of `paired_model_comparison`, which walks `_as_of_folds`"),
    "interior.record": ("delegates", "a label the online calibrator takes from the walk that calls it; scores no day itself"),
    "recalibration.label": ("delegates", "a label the online calibrator takes from the walk that calls it; scores no day itself"),
    "onset.twcrps_above_from_quantiles": ("delegates", "a pure metric of one vector and one outcome; chooses no day"),
    "scripts/calibration_masking_effect.score": ("delegates", _FOLDS),
    "scripts/calibration_rediagnosis.rediagnose": ("delegates", _FOLDS),
    "scripts/pid_constant_selection.select": ("delegates", _FOLDS),
    "scripts/pid_constant_selection.per_day": ("delegates", "a per-day loss of the walk `select` runs; " + _FOLDS),
    "scripts/final_test_opening.crps_horizon_command": ("delegates", _WALK + ", and `_window_positions` guards the window"),
    "scripts/direct_pairs_twin.score_command": ("guard", "scores the twin walks' CRPS after `require_unlocked` on the last scored day (2025-12-31), and refuses a walk that is not on the published record's days, which stop there (#450)"),
    "scripts/turning_point_variant.score_command": ("guard", "scores the variants' CRPS after `require_unlocked` on the last scored day (2025-12-31), and refuses a walk that is not on the published record's days, which stop there (#453)"),
    "scripts/settlement_flag_candidate.crps_side": ("delegates", _WALK),
    "scripts/forecast_daily.reproduction_check": ("delegates", "compares the published series with " + _WALK),
    "scripts/forecast_daily.reproduction_check_horizon": ("delegates", "compares the final test's cell with " + _WALK),
    "scripts/calendar_bands_418.mean_crps": ("delegates", "the mean loss of a published daily record's days, which `score` builds from `_WALK`'s records and refuses after the panel end"),
    "scripts/interior_diagnosis._crps": ("delegates", "one loss; " + _WALK),
    "scripts/pressure_model_v2._crps": ("delegates", "one loss; " + _WALK),
    "scripts/interior_calibration_judge._crps": ("delegates", "one loss; `score_command` calls `check_window` (which calls lockbox.require_unlocked) on every day before any is scored"),
    "scripts/pressure_model_v2.paired_against": ("delegates", "pairs the losses of `window_block`'s days; " + _WALK),
    "scripts/pressure_model_v2.window_block": ("delegates", "a block over days " + _WALK),
    "scripts/pressure_model_v2.assemble_command": ("delegates", "assembles blocks over days " + _WALK),
    "scripts/quarter_end_remedy._crps": ("delegates", "one loss; " + _WALK),
    "scripts/desk_outputs.check_against_published": ("delegates", "compares the days `history_command` chose, after its `require_unlocked`"),
    "scripts/desk_outputs._series": ("delegates", "the series of days `history_command` chose, after its `require_unlocked`"),
}


class CrpsScorerScanTests(unittest.TestCase):
    """Every function that computes a CRPS, or calls the live scorer's guard, is classified (#257).

    `EnumerationTests` finds the functions that read an as-of information set; the live scorer's
    cells read none, so its `score` and `score_crps` were in neither list. This scan finds the
    callers of `crps_from_quantiles` and its siblings too, in `src/repo_model/*.py` and the tracked
    `scripts/*.py`, and requires each to be classified in `CRPS_SCORERS` with a reason.

    Recorded mutations (#257), each applied in a disposable copy outside the tree: renaming the
    `"scripts/live_score.score_crps"` key in `CRPS_SCORERS` makes
    `test_every_function_that_computes_a_crps_is_classified` fail with `AssertionError: Items in the
    first set but not the second` (the scan finds the function, the table does not), and
    `test_a_guard_entry_calls_a_guard_itself` error with `KeyError`; replacing the
    `_require_scored_days_unlocked(days, where=f"live_score.score {cell_name} h={h}")` line in
    `live_score.score` with `pass` makes `test_a_guard_entry_calls_a_guard_itself` fail with
    `AssertionError: set() is not true : scripts/live_score.score calls no guard`.
    Written with its table in one pass; not run red first.
    """

    @staticmethod
    def functions():
        paths = [(path, path.stem) for path in sorted(SRC.glob("*.py"))]
        paths += [(path, f"scripts/{path.stem}") for path in sorted(SCRIPTS.glob("*.py"))]
        for path, module in paths:
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    called = {getattr(call.func, "attr", getattr(call.func, "id", None))
                              for call in ast.walk(node) if isinstance(call, ast.Call)}
                    yield f"{module}.{node.name}", called

    def test_every_function_that_computes_a_crps_is_classified(self):
        found = {name for name, called in self.functions() if called & CRPS_CALLERS}
        self.assertEqual(found, set(CRPS_SCORERS),
                         "classify each new function that computes a CRPS in CRPS_SCORERS, with a reason")

    def test_a_guard_entry_calls_a_guard_itself(self):
        called = dict(self.functions())
        for name, (kind, reason) in CRPS_SCORERS.items():
            with self.subTest(function=name):
                self.assertIn(kind, ("guard", "delegates"))
                self.assertTrue(reason.strip())
                if kind == "guard":
                    self.assertTrue(called[name] & GUARD_CALLS, f"{name} calls no guard")

    def test_the_live_scorers_cells_are_classified_as_guards(self):
        for name in ("scripts/live_score.score_crps", "scripts/live_score.score"):
            self.assertEqual(CRPS_SCORERS[name][0], "guard")


class EnumerationTests(unittest.TestCase):
    """The entry points above are all of them, checked against the code."""

    def test_every_function_that_selects_scored_days_is_classified(self):
        """A function reading an as-of information set or the fold loop.

        `InformationRule.information_set` is what turns a scored row into its
        reads, and `_as_of_folds` is the fold loop built on it; a function
        that calls either outside `asof.py` selects days to score, or reads
        inside a fit. The scan covers `src/repo_model/*.py` and the tracked
        `scripts/*.py`. Each must be an entry point above or be named, with a
        reason, in `NOT_ENTRY_POINTS`.
        """

        found = set()
        paths = [(path, path.stem) for path in sorted(SRC.glob("*.py"))]
        paths += [(path, f"scripts/{path.stem}") for path in sorted(SCRIPTS.glob("*.py"))]
        for path, module in paths:
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
                        found.add(f"{module}.{node.name}")
        self.assertEqual(
            found,
            set(LIBRARY_ENTRY_POINTS) | set(SCRIPT_ENTRY_POINTS) | set(NOT_ENTRY_POINTS),
            "classify each new function as a scoring entry point (add it to "
            "LIBRARY_ENTRY_POINTS, or SCRIPT_ENTRY_POINTS for scripts/) or as "
            "NOT_ENTRY_POINTS with a reason",
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

        from repo_model import baseline, event_eval, scarcity, tail_diagnostics

        modules = {
            "baseline": baseline,
            "event_eval": event_eval,
            "scarcity": scarcity,
            "tail_diagnostics": tail_diagnostics,
        }
        for name in LIBRARY_ENTRY_POINTS:
            module, function = name.split(".")
            parameters = inspect.signature(getattr(modules[module], function)).parameters
            with self.subTest(entry_point=name):
                self.assertFalse([p for p in parameters if "lock" in p or "open" in p])


class SamplePanelTests(unittest.TestCase):
    """The synthetic sample panel scores under the tracked declaration (#113).

    `data/sample/daily_market.csv` is what README's quick-start,
    `REPRODUCIBILITY.md`, `examples/walkthrough.py` and the walkthrough notebook
    score. Dated January and February 2026 it lay wholly inside the near-blind
    tier and every one of those commands exited 2 (#103); #113 moved it back 52
    weeks, values untouched. Run against the tracked declaration, with no
    override, so a sample that drifts back into a locked tier fails here rather
    than in a reader's first command.
    """

    SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample" / "daily_market.csv"
    REGISTRY = Path(__file__).resolve().parents[1] / "metadata" / "sources.json"

    def dates(self):
        with self.SAMPLE.open(newline="") as handle:
            return [date.fromisoformat(row["date"]) for row in csv.DictReader(handle)]

    def test_no_sample_date_lies_in_a_tier(self):
        dates = self.dates()
        self.assertTrue(dates)
        self.assertLess(max(dates), date(2026, 1, 1))
        tiers = lockbox.load_lockbox(TRACKED)
        self.assertEqual(
            [(day, tier.name) for day in dates for tier in tiers if tier.contains(day)], []
        )

    def test_the_published_sample_commands_run(self):
        """`backtest`, `compare` and `exceedance-backtest` as `REPRODUCIBILITY.md` prints them."""

        with tempfile.TemporaryDirectory() as tmp:
            common = ["--registry", str(self.REGISTRY), "--decision-time", "16:00"]
            commands = {
                "backtest": [
                    "backtest", str(self.SAMPLE), *common, "--feature", "spread_bps",
                    "--model", "persistence", "--report", f"{tmp}/backtest.json",
                ],
                "compare": [
                    "compare", str(self.SAMPLE), *common,
                    "--model-a", "persistence", "--feature-a", "spread_bps",
                    "--model-b", "arx", "--feature-b", "spread_bps",
                    "--feature-b", "sofr_volume", "--report", f"{tmp}/compare.json",
                ],
                "exceedance-backtest": [
                    "exceedance-backtest", "--panel", str(self.SAMPLE),
                    "--thresholds", str(THRESHOLDS), *common,
                    "--feature", "spread_bps", "--model", "climatology",
                    "--report", f"{tmp}/exceedance.json",
                ],
            }
            for name, argv in commands.items():
                with self.subTest(command=name):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        code = cli.main(argv)
                    self.assertEqual(code, 0, err.getvalue())


if __name__ == "__main__":
    unittest.main()
