"""The pressure-day judge (#375): the declared bar, applied to walk-forward probabilities.

`pressure_judge.judge` reads a declaration (`metadata/pressure_judge.json`), the
shared grid and each candidate's probabilities at +5 and +10 bp, and returns the
evidence of Eleonora's replacement bar (#375, 7 October 2026): tier 1 (onset
warning), tier 2 (risky dates, reported), tier 3 (no crying wolf), tier 4
(continuation, reported), tier 5 (week-ahead window) and the pass rule. These
tests build small synthetic series so each rule has a known answer.

**Recorded mutations** (CLAUDE.md: each new leakage guard carries one that kills it).

* A flag cut-off is chosen from a refit's training window alone (#407; the fixed,
  declared cut-off of #375 is gone). `select_cutoff` refuses a window that reaches
  past the refit's training end. Mutation 1: in `pressure_judge.select_cutoff`,
  replace `if late:` with `if False:`; the failing tests were
  `test_a_window_that_reaches_past_the_training_end_is_refused` and
  `test_a_window_with_a_day_but_no_training_end_is_refused`, which raised
  `AssertionError` (`LookAheadError not raised`).
  Mutation 2: in `pressure_judge.choose_cutoffs`, replace
  `last_known = position[block[0]] - forecast.horizon - 1` with
  `last_known = position[block[0]] - forecast.horizon` (the training window
  then reaches the day before the first decision instant, whose outcome is not
  yet published); the failing test was
  `test_training_ends_the_business_day_before_the_first_decision_instant`
  (`AssertionError: False is not true`). Mutation 3: in
  `pressure_judge._check_forecasts`, replace
  `if forecast.cutoff_rule != declaration.sha256:` with `if False:`; the failing
  test was `test_refuses_cutoffs_that_were_not_chosen_under_this_declaration`
  (`AssertionError: ValueError not raised`).
* `require_scored_days` refuses a day the lockbox holds.
  Mutation: delete the `lockbox.require_unlocked(...)` call in
  `pressure_judge.require_scored_days`. The failing tests were
  `test_refuses_a_day_in_a_locked_tier` and
  `test_judge_refuses_a_grid_with_a_locked_day`, which raised `AssertionError`
  (`LookAheadError not raised`).
* `require_scored_days` refuses a development day after the declared last
  scored day, even in a tier that is open. Mutation: replace
  `elif day > declaration.last_day:` with `elif False:` in
  `pressure_judge.require_scored_days`. The failing test was
  `test_refuses_a_day_after_the_declared_last_scored_day`, which raised
  `AssertionError` (`LookAheadError not raised`).
* `require_scored_days` refuses, in the single look, a day outside the declared
  confirmation window (a development day, or one past the window). Mutation:
  replace `if not declaration.confirmation_first <= day <= declaration.confirmation_last:`
  with `if False:`. The failing tests were
  `test_the_look_refuses_a_development_day` and
  `test_the_look_refuses_a_day_past_the_window`, which raised `AssertionError`
  (`LookAheadError not raised`).
* The look scores only candidates the declaration names for it. Mutation: in
  `pressure_judge._check_forecasts`, replace
  `and forecast.name not in declaration.confirmation_candidates` with
  `and False`. The failing test was
  `test_the_look_refuses_a_candidate_not_named_for_it`, which raised
  `AssertionError` (`ValueError not raised`).
* The judge scores only a committed declaration, candidate files included (#446).
  Mutation: in `scripts/pressure_judge.require_committed_declaration`, delete the line
  `relatives.append(str(directory.resolve().relative_to(repo)))` (the candidates'
  directory is then never checked). The failing tests, five in `CommittedDeclarationTests`
  (`test_an_uncommitted_new_candidate_file_is_refused`,
  `test_a_staged_but_uncommitted_candidate_file_is_refused`,
  `test_a_candidate_file_edited_after_its_commit_is_refused`,
  `test_a_candidate_file_deleted_without_a_commit_is_refused` and
  `test_the_commit_named_is_the_latest_to_touch_any_of_the_files`), raised
  `AssertionError` (`SystemExit not raised`; the last, `... == ...`).
"""

from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import pressure_judge as pj
from repo_model.splits import LookAheadError


def _weekdays(count, start=date(2019, 1, 1)):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def _declaration(**overrides):
    document = {
        "status": "test",
        "scoring": {"last_day": "2025-12-31"},
        "confirmation": {"first": "2026-01-01", "last": "2026-09-03", "candidates": ["sharp"]},
        "thresholds_bp": [5, 10],
        "primary_threshold_bp": 5,
        "horizons": [1, 2],
        "bootstrap": {"level": 0.9, "replications": 200, "block_length": 5, "seed": 375},
        "cutoff_rule": {
            "false_alarms_per_onset_at_most": 2.0, "refit_every": 20,
            "no_onsets": "never_flag", "none_meets_limit": "never_flag",
        },
        "tiers": {
            "onset_warning": {
                "lead_at_least": 1, "recall_at_least": 0.5, "false_alarms_per_onset_at_most": 2.0,
                "far_lead_at_least": 2, "far_recall_at_least": 0.3,
            },
            "risky_dates": {"scarcity_state_at_least": 2, "lead": 2, "auroc_at_least": 0.75},
            "no_crying_wolf": {
                "abundant_scarcity_state": 0, "abundant_regime": "b",
                "flags_per_year_at_most": 21, "business_days_per_year": 252,
            },
            "week_ahead": {"days": 2, "combine": "independence"},
        },
        "early_warning": {"usefulness_preference": 0.5},
        "groupings": ["regime", "day_type"],
        "benchmarks": {"climatology": "calendar_climatology", "persistence": "persistence_logistic"},
        "candidates": {
            "calendar_climatology": {
                "role": "benchmark", "features": ["day_type"], "calibration": "none",
            },
            "persistence_logistic": {
                "role": "benchmark", "features": ["spread_bps"], "calibration": "none",
            },
            "sharp": {
                "role": "candidate", "features": ["x"], "calibration": "none",
            },
            "published": {
                "role": "baseline", "features": ["x"], "calibration": "none",
            },
        },
    }
    document.update(overrides)
    return document


def _write(document):
    """The declaration as the judge reads it: the file, and each candidate in a file of its own."""

    document = dict(document)
    candidates = document.pop("candidates", {})
    root = Path(tempfile.mkdtemp())
    directory = root / "pressure_judge" / "candidates"
    directory.mkdir(parents=True)
    for name, entry in candidates.items():
        (directory / f"{name}.json").write_text(json.dumps(entry))
    path = root / "pressure_judge.json"
    path.write_text(json.dumps(document))
    return path


def _load(**overrides):
    return pj.load_declaration(_write(_declaration(**overrides)))


class Series:
    """A 400-day series: a pressure day every 20th day (k = 4, 24, ...), each an onset.

    The first 200 days are scarcity state 0, the rest state 2. Regime "a" is
    2019, regime "b" the rest. Every 10th day (k = 4, 14, ...) is a scheduled risk
    date. With the declaration's refit every 20 days, the first refit has no
    training window and flags nothing, so a candidate that flags every pressure
    day it has seen misses the first onset only.
    """

    def __init__(self, count=400, start=date(2019, 1, 1)):
        self.dates = tuple(_weekdays(count, start))
        self.y5 = tuple(1 if k % 20 == 4 else 0 for k in range(count))
        self.y10 = tuple(1 if k % 40 == 24 else 0 for k in range(count))
        self.groups = {
            "regime": tuple("a" if d.year == 2019 else "b" for d in self.dates),
            "day_type": tuple("quarter_end" if k % 10 == 4 else "ordinary" for k in range(count)),
            "scarcity_state": tuple("0" if k < 200 else "2" for k in range(count)),
            "risk_date": tuple("1" if k % 10 == 4 else "0" for k in range(count)),
        }

    def grid(self, horizon):
        return pj.Grid(
            horizon=horizon,
            dates=self.dates,
            outcomes={5.0: self.y5, 10.0: self.y10},
            groups=self.groups,
            onset=self.y5,
            onsets={5.0: self.y5, 10.0: self.y10},
        )

    def forecast(self, name, horizon, p5, p10=None):
        return pj.Forecast(
            name=name, horizon=horizon, dates=self.dates,
            probabilities={5.0: tuple(p5), 10.0: tuple(p10 if p10 is not None else p5)},
        )

    def perfect(self, horizon, name="sharp"):
        return self.forecast(
            name, horizon,
            [1.0 if y else 0.0 for y in self.y5],
            [1.0 if y else 0.0 for y in self.y10],
        )

    def flat(self, name, horizon, level):
        return self.forecast(name, horizon, [level] * len(self.dates))

    def everything(self, candidate):
        grids = {h: self.grid(h) for h in (1, 2)}
        forecasts = []
        for h in (1, 2):
            forecasts.append(self.flat("calendar_climatology", h, 0.1))
            forecasts.append(self.flat("persistence_logistic", h, 0.1))
            forecasts.append(candidate(h))
        return grids, forecasts

    def judged(self, candidate, **options):
        grids, forecasts = self.everything(candidate)
        return pj.judge(_load(), grids, forecasts, calendar=self.dates, **options)


class DeclarationTests(unittest.TestCase):
    def test_a_valid_declaration_loads_with_its_digest(self):
        declaration = _load()
        self.assertEqual(declaration.horizons, (1, 2))
        self.assertEqual(len(declaration.sha256), 64)
        self.assertEqual(declaration.week_days, 2)

    def test_the_cutoff_rule_is_declared_and_read(self):
        declaration = _load()
        self.assertEqual(declaration.cutoff_false_alarms_at_most, 2.0)
        self.assertEqual(declaration.cutoff_refit_every, 20)
        self.assertEqual(pj.load_declaration().cutoff_false_alarms_at_most, 2.0)
        self.assertEqual(pj.load_declaration().cutoff_refit_every, 21)

    def test_a_declaration_without_a_cutoff_rule_does_not_load(self):
        document = _declaration()
        del document["cutoff_rule"]
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))

    def test_the_rules_for_a_window_without_onsets_must_be_declared_as_never_flag(self):
        for key in ("no_onsets", "none_meets_limit"):
            document = _declaration()
            document["cutoff_rule"][key] = "flag_everything"
            with self.assertRaises(ValueError, msg=key):
                pj.load_declaration(_write(document))
            del document["cutoff_rule"][key]
            with self.assertRaises(ValueError, msg=key):
                pj.load_declaration(_write(document))

    def test_a_candidate_may_not_declare_a_fixed_cutoff(self):
        document = _declaration()
        document["candidates"]["sharp"]["cutoffs"] = {"5": 0.2, "10": 0.2}
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))

    def test_the_benchmarks_must_be_declared_candidates(self):
        document = _declaration()
        document["benchmarks"]["climatology"] = "missing"
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))

    def test_the_confirmation_window_must_follow_the_scored_days(self):
        with self.assertRaises(ValueError):
            _load(confirmation={"first": "2025-12-31", "last": "2026-09-03", "candidates": []})

    def test_the_look_may_name_only_declared_candidates(self):
        with self.assertRaises(ValueError):
            _load(confirmation={"first": "2026-01-01", "last": "2026-09-03", "candidates": ["nobody"]})
        with self.assertRaises(ValueError):
            _load(confirmation={"first": "2026-01-01", "last": "2026-09-03", "candidates": ["published"]})

    def test_the_tier_leads_must_be_judged_horizons_and_cover_the_week(self):
        document = _declaration()
        document["tiers"]["risky_dates"]["lead"] = 5
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))
        document = _declaration()
        document["tiers"]["week_ahead"]["days"] = 3
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))
        document = _declaration()
        document["tiers"]["week_ahead"]["combine"] = "mean"
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))

    def test_the_tracked_declaration_loads(self):
        declaration = pj.load_declaration()
        self.assertEqual(declaration.last_day, date(2025, 12, 31))
        self.assertEqual(declaration.confirmation_first, date(2026, 1, 1))
        self.assertEqual(declaration.confirmation_last, date(2026, 9, 3))
        self.assertEqual(declaration.onset_recall_at_least, 0.5)
        self.assertEqual(declaration.onset_false_alarms_at_most, 2.0)
        self.assertEqual(declaration.flags_per_year_at_most, 21)
        self.assertEqual(declaration.week_days, 5)
        self.assertIn(declaration.climatology, declaration.candidates)


class CandidateFileTests(unittest.TestCase):
    """Each candidate is a file of its own (#446): the judge loads the union."""

    def test_the_candidates_are_the_files_in_the_directory(self):
        declaration = _load()
        self.assertEqual(
            sorted(declaration.candidates),
            ["calendar_climatology", "persistence_logistic", "published", "sharp"],
        )
        self.assertEqual(declaration.candidates["sharp"]["role"], "candidate")

    def test_a_candidate_added_as_a_file_joins_the_declaration_and_its_digest(self):
        path = _write(_declaration())
        before = pj.load_declaration(path)
        (pj.candidates_directory(path) / "newcomer.json").write_text(
            json.dumps({"role": "candidate", "features": ["x"], "calibration": "none"})
        )
        after = pj.load_declaration(path)
        self.assertIn("newcomer", after.candidates)
        self.assertNotEqual(before.sha256, after.sha256)

    def test_a_candidate_file_changes_the_digest(self):
        path = _write(_declaration())
        before = pj.load_declaration(path).sha256
        (pj.candidates_directory(path) / "sharp.json").write_text(
            json.dumps({"role": "candidate", "features": ["y"], "calibration": "none"})
        )
        self.assertNotEqual(before, pj.load_declaration(path).sha256)

    def test_the_declaration_may_not_also_list_candidates(self):
        path = _write(_declaration())
        document = json.loads(path.read_text())
        document["candidates"] = {"sharp": {"role": "candidate", "features": [], "calibration": "none"}}
        path.write_text(json.dumps(document))
        with self.assertRaises(ValueError):
            pj.load_declaration(path)

    def test_a_declaration_without_candidate_files_does_not_load(self):
        path = _write(_declaration(candidates={}))
        with self.assertRaises(ValueError):
            pj.load_declaration(path)

    def test_a_candidate_file_must_be_an_object_with_its_fields(self):
        path = _write(_declaration())
        directory = pj.candidates_directory(path)
        (directory / "sharp.json").write_text("[1]")
        with self.assertRaises(ValueError):
            pj.load_declaration(path)
        (directory / "sharp.json").write_text("{not json")
        with self.assertRaises(ValueError):
            pj.load_declaration(path)
        (directory / "sharp.json").write_text(json.dumps({"role": "candidate", "features": []}))
        with self.assertRaises(ValueError):
            pj.load_declaration(path)

    def test_the_tracked_candidates_are_the_files_of_the_tracked_directory(self):
        names = sorted(f.stem for f in pj.candidates_directory().glob("*.json"))
        self.assertEqual(sorted(pj.load_declaration().candidates), names)
        self.assertIn(pj.load_declaration().persistence, names)


def _git(repo, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=repo, check=True, capture_output=True,
    )


class CommittedDeclarationTests(unittest.TestCase):
    """The judge scores only a declaration that is committed, candidate files included (#446)."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "pressure_judge_script", Path(__file__).parents[1] / "scripts" / "pressure_judge.py"
        )
        cls.script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.script)

    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        _git(self.repo, "init", "-q")
        metadata = self.repo / "metadata"
        metadata.mkdir()
        self.path = metadata / "pressure_judge.json"
        self.path.write_text("{}")
        self.directory = pj.candidates_directory(self.path)
        self.directory.mkdir(parents=True)
        (self.directory / "sharp.json").write_text("{}")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", "declare")

    def guard(self):
        return self.script.require_committed_declaration(self.path, repo=self.repo)

    def test_a_committed_declaration_is_accepted_and_names_its_commit(self):
        self.assertEqual(len(self.guard()), 40)

    def test_an_uncommitted_new_candidate_file_is_refused(self):
        (self.directory / "newcomer.json").write_text("{}")
        with self.assertRaises(SystemExit):
            self.guard()

    def test_a_staged_but_uncommitted_candidate_file_is_refused(self):
        (self.directory / "newcomer.json").write_text("{}")
        _git(self.repo, "add", "-A")
        with self.assertRaises(SystemExit):
            self.guard()

    def test_a_candidate_file_edited_after_its_commit_is_refused(self):
        (self.directory / "sharp.json").write_text('{"role": "candidate"}')
        with self.assertRaises(SystemExit):
            self.guard()

    def test_a_candidate_file_deleted_without_a_commit_is_refused(self):
        (self.directory / "sharp.json").unlink()
        with self.assertRaises(SystemExit):
            self.guard()

    def test_an_edited_declaration_is_refused(self):
        self.path.write_text('{"status": "edited"}')
        with self.assertRaises(SystemExit):
            self.guard()

    def test_the_commit_named_is_the_latest_to_touch_any_of_the_files(self):
        first = self.guard()
        (self.directory / "newcomer.json").write_text("{}")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", "add newcomer")
        self.assertNotEqual(first, self.guard())


class GuardTests(unittest.TestCase):
    def test_refuses_a_day_in_a_locked_tier(self):
        # The declared last day is moved past the lockbox's blind tier so only
        # the lockbox can refuse the scored day.
        declaration = _load(
            scoring={"last_day": "2027-12-31"},
            confirmation={"first": "2028-01-01", "last": "2028-02-01", "candidates": []},
        )
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2026, 9, 4)], where="test")

    def test_refuses_a_day_after_the_declared_last_scored_day(self):
        # 2026-02-02 is in the near-blind tier, which is open: only the judge's
        # own declared last day refuses it in development.
        declaration = _load()
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2026, 2, 2)], where="test")
        pj.require_scored_days(declaration, [date(2025, 12, 31)], where="test")

    def test_the_look_refuses_a_development_day(self):
        declaration = _load()
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2025, 12, 31)], where="test", confirmation=True)
        pj.require_scored_days(declaration, [date(2026, 2, 2)], where="test", confirmation=True)

    def test_the_look_refuses_a_day_past_the_window(self):
        declaration = _load(confirmation={"first": "2026-01-01", "last": "2026-03-31", "candidates": []})
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2026, 4, 15)], where="test", confirmation=True)
        pj.require_scored_days(declaration, [date(2026, 3, 31)], where="test", confirmation=True)

    def test_judge_refuses_a_grid_with_a_locked_day(self):
        series = Series(count=40, start=date(2026, 8, 20))
        declaration = _load(
            scoring={"last_day": "2027-12-31"},
            confirmation={"first": "2028-01-01", "last": "2028-02-01", "candidates": []},
        )
        grids = {h: series.grid(h) for h in (1, 2)}
        forecasts = [
            series.flat(name, h, 0.1)
            for h in (1, 2)
            for name in ("calendar_climatology", "persistence_logistic", "sharp")
        ]
        with self.assertRaises(LookAheadError):
            pj.judge(declaration, grids, forecasts, calendar=series.dates)

    def test_the_look_refuses_a_candidate_not_named_for_it(self):
        series = Series(count=60, start=date(2026, 1, 5))
        named = _load()
        unnamed = _load(confirmation={"first": "2026-01-01", "last": "2026-09-03", "candidates": []})
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        chosen = pj.choose_cutoffs(named, grids, forecasts, series.dates)
        result = pj.judge(named, grids, chosen, calendar=series.dates, confirmation=True)
        self.assertEqual(result["mode"], "confirmation")
        chosen = pj.choose_cutoffs(unnamed, grids, forecasts, series.dates)
        with self.assertRaises(ValueError):
            pj.judge(unnamed, grids, chosen, calendar=series.dates, confirmation=True)
        # In development the same declaration scores the candidate without a list.
        development = Series()
        grids, forecasts = development.everything(lambda h: development.perfect(h))
        pj.judge(unnamed, grids, forecasts, calendar=development.dates)

    def test_the_look_needs_cutoffs_chosen_on_the_days_before_its_window(self):
        series = Series(count=60, start=date(2026, 1, 5))
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates, confirmation=True)

    def test_refuses_cutoffs_that_were_not_chosen_under_this_declaration(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        declaration = _load()
        chosen = pj.choose_cutoffs(declaration, grids, forecasts, series.dates)
        pj.judge(declaration, grids, chosen, calendar=series.dates)
        forged = [
            pj.Forecast(
                name=f.name, horizon=f.horizon, dates=f.dates, probabilities=f.probabilities,
                cutoffs={tau: (0.2,) * len(f.dates) for tau in f.probabilities}, cutoff_rule="0" * 64,
            )
            for f in forecasts
        ]
        with self.assertRaises(ValueError):
            pj.judge(declaration, grids, forged, calendar=series.dates)

    def test_refuses_a_candidate_that_is_not_declared(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h, name="undeclared"))
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_refuses_forecasts_on_other_days_than_the_grid(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        shifted = forecasts[-1]
        forecasts[-1] = pj.Forecast(
            name=shifted.name, horizon=shifted.horizon,
            dates=shifted.dates[1:] + (shifted.dates[-1] + timedelta(days=3),),
            probabilities=shifted.probabilities,
        )
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_refuses_a_probability_outside_zero_one(self):
        series = Series()
        grids, forecasts = series.everything(
            lambda h: series.forecast("sharp", h, [1.2] + [0.1] * (len(series.dates) - 1))
        )
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_refuses_a_grid_missing_a_declared_grouping(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        for dropped in ("day_type", "risk_date"):
            groups = {k: v for k, v in series.groups.items() if k != dropped}
            grids[1] = pj.Grid(
                horizon=1, dates=series.dates, outcomes={5.0: series.y5, 10.0: series.y10},
                groups=groups, onset=series.y5,
            )
            with self.assertRaises(ValueError, msg=dropped):
                pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_refuses_a_run_without_the_declared_climatology(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        forecasts = [f for f in forecasts if f.name != "calendar_climatology"]
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)


class CutoffTests(unittest.TestCase):
    """The flag cut-off is chosen from a refit's training window alone (#407)."""

    def days(self, count):
        return _weekdays(count)

    def test_picks_the_cutoff_with_the_most_onset_recall_within_the_false_alarm_limit(self):
        # Onsets at p = .9 and .5; non-pressure days at .7, .6, .4, .3 (limit: 2 per onset = 4 in all).
        days = self.days(8)
        p = [0.9, 0.7, 0.6, 0.5, 0.4, 0.3, 0.1, 0.1]
        pressure = [1, 0, 0, 1, 0, 0, 0, 0]
        onset = [1, 0, 0, 1, 0, 0, 0, 0]
        declaration = _load()
        got = pj.select_cutoff(
            declaration, days=days, probabilities=p, pressure=pressure, onset=onset, training_end=days[-1]
        )
        # At 0.5 both onsets are caught with 2 false alarms (1 per onset); at 0.3 also two, with 4
        # false alarms (2 per onset, within the limit) -- the same recall, so the higher cut-off wins.
        self.assertEqual(got, 0.5)

    def test_a_lower_cutoff_that_buys_recall_within_the_limit_is_taken(self):
        days = self.days(6)
        p = [0.9, 0.8, 0.7, 0.6, 0.2, 0.1]
        pressure = [0, 0, 1, 0, 1, 0]
        onset = [0, 0, 1, 0, 1, 0]
        got = pj.select_cutoff(
            _load(), days=days, probabilities=p, pressure=pressure, onset=onset, training_end=days[-1]
        )
        # 0.7: one of two onsets, 2 false alarms (1 per onset). 0.2: both onsets, 3 false alarms (1.5 per onset).
        self.assertEqual(got, 0.2)

    def test_stops_at_the_limit(self):
        days = self.days(4)
        p = [0.9, 0.8, 0.7, 0.6]
        pressure = [0, 0, 0, 1]
        onset = [0, 0, 0, 1]
        got = pj.select_cutoff(
            _load(), days=days, probabilities=p, pressure=pressure, onset=onset, training_end=days[-1]
        )
        # The one onset is reached only after 3 false alarms (3 per onset), over the limit of 2.
        self.assertEqual(got, math.inf)
        # With a second onset to share them (1.5 per onset), it is reached.
        five = self.days(5)
        got = pj.select_cutoff(
            _load(), days=five, probabilities=[0.95, 0.9, 0.8, 0.7, 0.6],
            pressure=[1, 0, 0, 0, 1], onset=[1, 0, 0, 0, 1], training_end=five[-1],
        )
        self.assertEqual(got, 0.6)

    def test_a_window_with_no_onset_never_flags(self):
        days = self.days(4)
        got = pj.select_cutoff(
            _load(), days=days, probabilities=[0.9, 0.8, 0.1, 0.1], pressure=[0, 0, 0, 0],
            onset=[0, 0, 0, 0], training_end=days[-1],
        )
        self.assertEqual(got, math.inf)

    def test_an_empty_window_never_flags(self):
        self.assertEqual(
            pj.select_cutoff(
                _load(), days=[], probabilities=[], pressure=[], onset=[], training_end=None
            ),
            math.inf,
        )

    def test_a_window_that_reaches_past_the_training_end_is_refused(self):
        """Guard: a cut-off is not chosen from a day after the refit's training end.

        Mutation: in `pressure_judge.select_cutoff`, replace `if late:` with `if False:`; the failing
        tests were `test_a_window_that_reaches_past_the_training_end_is_refused` and
        `test_a_window_with_a_day_but_no_training_end_is_refused`, which raised `AssertionError`
        (`LookAheadError not raised`).
        """

        days = self.days(5)
        kwargs = dict(
            probabilities=[0.1, 0.2, 0.3, 0.4, 0.9], pressure=[0, 0, 0, 0, 1], onset=[0, 0, 0, 0, 1]
        )
        with self.assertRaises(LookAheadError):
            pj.select_cutoff(_load(), days=days, training_end=days[3], **kwargs)
        # The same window is fine once the training end reaches its last day.
        self.assertEqual(pj.select_cutoff(_load(), days=days, training_end=days[4], **kwargs), 0.9)

    def test_a_window_with_a_day_but_no_training_end_is_refused(self):
        days = self.days(2)
        with self.assertRaises(LookAheadError):
            pj.select_cutoff(
                _load(), days=days, probabilities=[0.1, 0.9], pressure=[0, 1], onset=[0, 1],
                training_end=None,
            )

    def test_the_window_lengths_must_agree(self):
        days = self.days(3)
        with self.assertRaises(ValueError):
            pj.select_cutoff(
                _load(), days=days, probabilities=[0.1, 0.9], pressure=[0, 1, 0], onset=[0, 1, 0],
                training_end=days[-1],
            )


class ScarceCutoffTests(unittest.TestCase):
    """`choose_cutoffs(scarce_at_least=2)` (#461): a separate cut-off on days whose as-of scarcity state is at least 2.

    That cut-off is chosen by `select_cutoff`, the same rule and limit, on the refit's training days in that
    state only. Days in a lower state keep the cut-off chosen on all training days.

    **Recorded mutation** (CLAUDE.md): in `pressure_judge.choose_cutoffs`, replace
    `scarce_window = [k for k in window if _state_at_least(states[k], scarce_at_least)]` with
    `scarce_window = [k for k in range(start) if _state_at_least(states[k], scarce_at_least)]` (the
    state's window then reaches days whose outcome was not yet known at the refit); four tests failed,
    among them `test_the_scarce_window_ends_where_the_pooled_window_ends`, which raised `LookAheadError`
    (`cut-off chosen from 1 day(s) from ... on, after the refit's training end`).
    """

    def series_and_forecast(self):
        # Onsets every 20th day. Days 0-199 are state 0, from 200 state 2. The model scores an onset 0.5
        # in state 0 and 0.9 in state 2, and nothing else: one pooled cut-off (0.5) is not the scarce one.
        series = Series()
        p = [(0.5 if k < 200 else 0.9) if y else 0.0 for k, y in enumerate(series.y5)]
        return series, series.forecast("stronger_when_scarce", 1, p)

    def chosen(self, series, forecast, **options):
        (out,) = pj.choose_cutoffs(_load(), {1: series.grid(1)}, [forecast], series.dates, **options)
        return out.cutoffs[5.0]

    def test_days_below_the_state_keep_the_pooled_cutoff(self):
        series, forecast = self.series_and_forecast()
        self.assertEqual(self.chosen(series, forecast, scarce_at_least=2)[:200], self.chosen(series, forecast)[:200])

    def test_scarce_days_take_the_cutoff_chosen_on_scarce_training_days_alone(self):
        series, forecast = self.series_and_forecast()
        pooled = self.chosen(series, forecast)
        scarce = self.chosen(series, forecast, scarce_at_least=2)
        # Block at day 300: training days 0..298 (h = 1). The state-2 days among them are 200..298.
        window = list(range(200, 299))
        declaration = _load()
        expected = pj.select_cutoff(
            declaration,
            days=[series.dates[k] for k in window],
            probabilities=[forecast.probabilities[5.0][k] for k in window],
            pressure=[series.y5[k] for k in window],
            onset=[series.y5[k] for k in window],
            training_end=series.dates[298],
        )
        self.assertEqual(scarce[300], expected)
        self.assertEqual(expected, 0.9)
        # The pooled cut-off, chosen with the state-0 onsets in the window, is lower.
        self.assertEqual(pooled[300], 0.5)

    def test_the_scarce_window_ends_where_the_pooled_window_ends(self):
        # An onset on day 199 is the last state-0 day; a state-2 onset on day 299 is the day before the
        # block at day 300 starts and is not yet published. The block must not read it.
        series = Series()
        y = [1 if k in (210, 299) else 0 for k in range(400)]
        series.y5 = tuple(y)
        series.y10 = tuple(0 for _ in y)
        forecast = series.forecast("sharp", 1, [0.9 if v else 0.0 for v in y])
        scarce = self.chosen(series, forecast, scarce_at_least=2)
        # Block at 220 reads state-2 day 210 only: cut-off 0.9. Block at 300: day 299 is not read, but 210 is.
        self.assertEqual(scarce[220], 0.9)
        series2 = Series()
        y2 = [1 if k == 299 else 0 for k in range(400)]
        series2.y5 = tuple(y2)
        series2.y10 = tuple(0 for _ in y2)
        forecast2 = series2.forecast("sharp", 1, [0.9 if v else 0.0 for v in y2])
        self.assertTrue(math.isinf(self.chosen(series2, forecast2, scarce_at_least=2)[300]))

    def test_a_scarce_state_with_no_onset_flags_nothing(self):
        series = Series()
        y = [1 if k == 10 else 0 for k in range(400)]  # the only onset is in state 0
        series.y5 = tuple(y)
        series.y10 = tuple(0 for _ in y)
        forecast = series.forecast("sharp", 1, [0.9 if v else 0.0 for v in y])
        scarce = self.chosen(series, forecast, scarce_at_least=2)
        self.assertEqual(scarce[100], 0.9)
        self.assertTrue(all(math.isinf(c) for c in scarce[220:]))

    def test_an_unknown_state_is_not_scarce(self):
        series, forecast = self.series_and_forecast()
        series.groups = dict(series.groups, scarcity_state=tuple("unknown" for _ in range(400)))
        self.assertEqual(self.chosen(series, forecast, scarce_at_least=2), self.chosen(series, forecast))

    def test_a_grid_without_the_state_is_refused(self):
        series, forecast = self.series_and_forecast()
        grid = series.grid(1)
        grid = pj.Grid(
            horizon=1, dates=grid.dates, outcomes=grid.outcomes, onset=grid.onset, onsets=grid.onsets,
            groups={k: v for k, v in grid.groups.items() if k != "scarcity_state"},
        )
        with self.assertRaises(ValueError):
            pj.choose_cutoffs(_load(), {1: grid}, [forecast], series.dates, scarce_at_least=2)


class ChooseCutoffsTests(unittest.TestCase):
    """`choose_cutoffs`: one cut-off per refit block, from the days known at the block's first decision."""

    def one_onset(self, position):
        """A 60-day series with a single pressure day (an onset) at `position`, flagged with p = 1."""

        series = Series(count=60)
        series.y5 = tuple(1 if k == position else 0 for k in range(60))
        series.y10 = tuple(0 for _ in range(60))
        forecast = series.forecast(
            "sharp", 1, [1.0 if k == position else 0.0 for k in range(60)], [0.0] * 60
        )
        return series, forecast

    def cutoffs(self, series, forecast, horizon=1):
        declaration = _load()
        grid = series.grid(horizon)
        forecast = pj.Forecast(
            name=forecast.name, horizon=horizon, dates=forecast.dates, probabilities=forecast.probabilities
        )
        (chosen,) = pj.choose_cutoffs(declaration, {horizon: grid}, [forecast], series.dates)
        return chosen.cutoffs[5.0]

    def test_the_first_refit_has_no_training_window_and_flags_nothing(self):
        series, forecast = self.one_onset(4)
        cutoffs = self.cutoffs(series, forecast)
        self.assertTrue(all(math.isinf(c) for c in cutoffs[:20]))
        self.assertEqual(cutoffs[20:40], (1.0,) * 20)
        self.assertEqual(cutoffs[40:], (1.0,) * 20)

    def test_the_cutoff_is_constant_within_a_refit_block(self):
        series, forecast = self.one_onset(4)
        cutoffs = self.cutoffs(series, forecast)
        for start in (0, 20, 40):
            self.assertEqual(len(set(cutoffs[start : start + 20])), 1)

    def test_training_ends_the_business_day_before_the_first_decision_instant(self):
        # Block 1 starts at day 20; at horizon 1 its first decision instant is day 19, and a day's
        # outcome is read from the next morning, so day 18 is the last training day. An onset on
        # day 18 is read; one on day 19 is not.
        series, forecast = self.one_onset(18)
        self.assertEqual(self.cutoffs(series, forecast)[20], 1.0)
        series, forecast = self.one_onset(19)
        self.assertTrue(math.isinf(self.cutoffs(series, forecast)[20]))
        # At horizon 2 the decision instant is day 18 and the last training day 17.
        series, forecast = self.one_onset(17)
        self.assertEqual(self.cutoffs(series, forecast, horizon=2)[20], 1.0)
        series, forecast = self.one_onset(18)
        self.assertTrue(math.isinf(self.cutoffs(series, forecast, horizon=2)[20]))

    def test_no_day_of_the_block_or_after_it_is_read(self):
        series = Series()
        base = series.perfect(1)
        reference = self.cutoffs(series, base)
        # Rewrite every probability and outcome from day 220 on: blocks starting by day 220
        # (their windows end by day 218) are unchanged.
        late = [0.3 if k >= 220 else p for k, p in enumerate(base.probabilities[5.0])]
        series.y5 = tuple(0 if k >= 220 else y for k, y in enumerate(series.y5))
        changed = self.cutoffs(series, series.forecast("sharp", 1, late, late))
        self.assertEqual(changed[:221], reference[:221])
        self.assertEqual(changed[220], reference[220])

    def test_each_threshold_uses_its_own_pressure_days_and_onsets(self):
        series = Series()
        forecast = series.forecast(
            "sharp", 1,
            [0.8 if y else 0.0 for y in series.y5],
            [0.6 if y else 0.0 for y in series.y10],
        )
        declaration = _load()
        (chosen,) = pj.choose_cutoffs(declaration, {1: series.grid(1)}, [forecast], series.dates)
        # +5 bp: onsets every 20 days, flagged at 0.8. +10 bp: every 40 days, at 0.6.
        self.assertEqual(chosen.cutoffs[5.0][100], 0.8)
        self.assertEqual(chosen.cutoffs[10.0][100], 0.6)
        self.assertEqual(chosen.cutoff_rule, declaration.sha256)

    def test_a_grid_without_onsets_at_a_threshold_is_refused(self):
        series = Series()
        grid = series.grid(1)
        grid = pj.Grid(
            horizon=1, dates=grid.dates, outcomes=grid.outcomes, groups=grid.groups, onset=grid.onset
        )
        with self.assertRaises(ValueError):
            pj.choose_cutoffs(_load(), {1: grid}, [series.perfect(1)], series.dates)

    def test_forecasts_must_be_on_the_grids_days(self):
        series = Series()
        shorter = pj.Forecast(
            name="sharp", horizon=1, dates=series.dates[:-1],
            probabilities={tau: column[:-1] for tau, column in series.perfect(1).probabilities.items()},
        )
        with self.assertRaises(ValueError):
            pj.choose_cutoffs(_load(), {1: series.grid(1)}, [shorter], series.dates)

    def test_a_forecast_cut_to_the_look_window_keeps_the_cutoffs_chosen_before_it(self):
        series = Series()
        declaration = _load()
        (chosen,) = pj.choose_cutoffs(declaration, {1: series.grid(1)}, [series.perfect(1)], series.dates)
        cut = pj.restrict_forecast(chosen, series.dates[100], series.dates[199])
        self.assertEqual(cut.cutoffs[5.0], chosen.cutoffs[5.0][100:200])
        self.assertEqual(cut.cutoff_rule, declaration.sha256)


class MetricTests(unittest.TestCase):
    def test_auroc_counts_ties_as_half(self):
        self.assertEqual(pj.auroc([0.9, 0.8, 0.1, 0.2], [1, 1, 0, 0]), 1.0)
        self.assertEqual(pj.auroc([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0]), 0.5)
        self.assertEqual(pj.auroc([0.1, 0.9], [1, 0]), 0.0)
        self.assertIsNone(pj.auroc([0.1, 0.9], [0, 0]))

    def test_usefulness_is_the_loss_saved_against_the_best_default(self):
        # theta = 0.5: loss = 0.5 FNR + 0.5 FPR; the default loss is 0.5.
        # 3 of 4 events caught, 1 of 4 non-events flagged: FNR .25, FPR .25.
        flags = [1, 1, 1, 0, 1, 0, 0, 0]
        y = [1, 1, 1, 1, 0, 0, 0, 0]
        got = pj.usefulness(flags, y, 0.5)
        self.assertAlmostEqual(got["absolute"], 0.5 - 0.25)
        self.assertAlmostEqual(got["relative"], 0.5)

    def test_matched_false_alarm_weights_reach_the_target_count_exactly(self):
        p = [0.9, 0.8, 0.8, 0.8, 0.1, 0.1]
        y = [1, 0, 0, 1, 0, 1]
        weights = pj.matched_false_alarm_weights(p, y, 1)
        raised = sum(w for w, t in zip(weights, y) if not t)
        self.assertAlmostEqual(raised, 1.0)
        self.assertEqual(weights[0], 1.0)
        self.assertEqual(weights[4], 0.0)
        # The tied group at 0.8 (2 false alarms of 3 days) is flagged in part.
        self.assertTrue(0.0 < weights[1] < 1.0)
        self.assertEqual(weights[1], weights[2])

    def test_a_pressure_day_costs_no_false_alarm(self):
        weights = pj.matched_false_alarm_weights([0.9, 0.8, 0.1], [1, 1, 0], 0)
        self.assertEqual(weights, (1.0, 1.0, 0.0))

    def test_a_flat_forecast_is_matched_by_flagging_every_day_in_proportion(self):
        weights = pj.matched_false_alarm_weights([0.1] * 10, [1, 0] * 5, 2)
        self.assertTrue(all(abs(w - 0.4) < 1e-12 for w in weights))


class TierTests(unittest.TestCase):
    def test_a_sharp_candidate_passes_every_tier_of_the_pass_rule(self):
        result = Series().judged(lambda h: Series().perfect(h))
        sharp = result["candidates"]["sharp"]
        near = sharp["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertEqual(near["onsets"], 20)
        # The first refit has no training window and flags nothing: 19 of 20 onsets are flagged.
        self.assertEqual(near["onsets_flagged"], 19)
        self.assertEqual(near["recall"]["mean"], 0.95)
        self.assertEqual(near["climatology_recall"], 0.0)
        self.assertEqual(near["worst_false_alarms_per_onset"], 0.0)
        self.assertTrue(all(near["criteria"].values()))
        self.assertTrue(near["passes"])
        for horizon in ("1", "2"):
            self.assertTrue(sharp["tiers"]["no_crying_wolf"][horizon]["ok"])
        week = sharp["tiers"]["week_ahead"]
        self.assertTrue(week["criteria"]["calibrated"])
        self.assertTrue(week["criteria"]["beats_climatology_brier"])
        verdict = sharp["verdict"]
        self.assertTrue(verdict["tier_1_onset_warning"])
        self.assertTrue(verdict["tier_3_no_crying_wolf"])
        self.assertTrue(verdict["tier_5_week_ahead"])
        self.assertTrue(verdict["passes"])
        row = sharp["horizons"]["1"]["5"]
        self.assertEqual(row["auroc"], 1.0)
        # Loss 0.5 * (1 missed onset of 20) against a default of 0.5.
        self.assertAlmostEqual(row["usefulness"]["relative"], 0.95)

    def test_the_cutoff_is_chosen_from_training_days_not_declared(self):
        series = Series()
        # Probabilities of 0.4 on events and 0 elsewhere: a fixed 0.5 would flag nothing, the
        # training windows put the cut-off at 0.4.
        weak = lambda h: series.forecast("sharp", h, [0.4 if y else 0.0 for y in series.y5])
        grids, forecasts = series.everything(weak)
        result = pj.judge(_load(), grids, forecasts, calendar=series.dates)
        sharp = result["candidates"]["sharp"]
        cutoff = sharp["horizons"]["1"]["5"]["cutoff"]
        self.assertEqual((cutoff["minimum"], cutoff["median"], cutoff["maximum"]), (0.4, 0.4, 0.4))
        # The first refit (days 0-19) has no training window.
        self.assertEqual(cutoff["days_never_flag"], 20)
        self.assertEqual(sharp["horizons"]["1"]["5"]["flags"]["alarms"], 19)
        self.assertEqual(sharp["tiers"]["onset_warning"]["lead_at_least_1"]["onsets_flagged"], 19)

    def test_a_noisy_candidate_is_muted_by_its_own_training_window(self):
        series = Series()
        # Flags 12 days of every 20, the onset among them: 11 false alarms per onset in training, over
        # the limit of 2, so the rule never flags it.
        noisy = lambda h: series.forecast(
            "sharp", h, [1.0 if k % 20 < 12 else 0.0 for k in range(len(series.dates))]
        )
        sharp = series.judged(noisy)["candidates"]["sharp"]
        self.assertEqual(sharp["tiers"]["onset_warning"]["lead_at_least_1"]["onsets_flagged"], 0)
        self.assertEqual(sharp["horizons"]["1"]["5"]["flags"]["alarms"], 0)
        self.assertEqual(sharp["horizons"]["1"]["5"]["cutoff"]["days_never_flag"], 400)

    def test_false_alarms_over_the_tier_limit_fail_tier_one(self):
        series = Series()
        # One false alarm the day before each onset: within the training limit of 2 per onset, so it
        # is flagged, and over a tier limit of 0.5.
        noisy = lambda h: series.forecast(
            "sharp", h, [1.0 if (y or k % 20 == 3) else 0.0 for k, y in enumerate(series.y5)]
        )
        strict = _declaration()
        strict["tiers"]["onset_warning"]["false_alarms_per_onset_at_most"] = 0.5
        grids, forecasts = series.everything(noisy)
        near = pj.judge(pj.load_declaration(_write(strict)), grids, forecasts, calendar=series.dates)[
            "candidates"]["sharp"]["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertEqual(near["onsets_flagged"], 19)
        self.assertAlmostEqual(near["worst_false_alarms_per_onset"], 19 / 20)
        self.assertFalse(near["criteria"]["false_alarms"])
        self.assertFalse(near["passes"])
        near = series.judged(noisy)["candidates"]["sharp"]["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertTrue(near["criteria"]["false_alarms"])

    def test_a_candidate_that_only_matches_climatology_fails(self):
        series = Series()
        result = series.judged(lambda h: series.flat("sharp", h, 0.1))
        sharp = result["candidates"]["sharp"]
        self.assertFalse(sharp["tiers"]["week_ahead"]["criteria"]["beats_climatology_brier"])
        self.assertFalse(sharp["verdict"]["passes"])
        self.assertFalse(result["candidates"]["calendar_climatology"]["verdict"]["passes"])

    def test_recall_must_beat_climatology_at_the_same_false_alarm_rate(self):
        series = Series()
        grids = {h: series.grid(h) for h in (1, 2)}
        forecasts = []
        for h in (1, 2):
            # A climatology that already ranks every pressure day first catches them
            # all at zero false alarms: matching it is not enough.
            forecasts.append(series.perfect(h, name="calendar_climatology"))
            forecasts.append(series.flat("persistence_logistic", h, 0.1))
            forecasts.append(series.perfect(h))
        result = pj.judge(_load(), grids, forecasts, calendar=series.dates)
        near = result["candidates"]["sharp"]["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertEqual(near["recall"]["mean"], 0.95)
        self.assertEqual(near["climatology_recall"], 1.0)
        self.assertTrue(near["criteria"]["recall"])
        self.assertFalse(near["criteria"]["recall_above_climatology"])
        self.assertFalse(near["passes"])

    def test_the_climatology_is_matched_on_false_alarms_not_on_flags(self):
        series = Series()
        # A candidate that flags each onset and the two days before it raises 2 false alarms per
        # onset; a flat climatology that spends the same budget flags in proportion and so
        # catches few onsets.
        noisy = lambda h: series.forecast(
            "sharp", h, [1.0 if k % 20 in (2, 3, 4) else 0.0 for k in range(len(series.dates))]
        )
        near = series.judged(noisy)["candidates"]["sharp"]["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertEqual(near["recall"]["mean"], 0.95)
        self.assertEqual(near["worst_false_alarms_per_onset"], 38 / 20)
        # 38 false alarms of 380 non-pressure days at each of two horizons: a flat climatology
        # that spends the same budget flags a tenth of the days at each, and misses an onset
        # only when it misses at both.
        self.assertAlmostEqual(near["climatology_recall"], 1.0 - 0.9 ** 2, places=6)

    def test_lead_at_least_reads_the_longest_horizon_that_flagged_the_onset(self):
        series = Series()
        # Flags the onsets at h = 1 only: caught at lead >= 1, not at lead >= 2.
        one_day = lambda h: series.perfect(h) if h == 1 else series.flat("sharp", h, 0.0)
        tiers = series.judged(one_day)["candidates"]["sharp"]["tiers"]["onset_warning"]
        self.assertEqual(tiers["lead_at_least_1"]["recall"]["mean"], 0.95)
        self.assertEqual(tiers["lead_at_least_2"]["recall"]["mean"], 0.0)
        self.assertFalse(tiers["lead_at_least_2"]["meets_far_recall"])
        # Flags at h = 2 only: caught at lead >= 1 as well, and at lead >= 2.
        two_days = lambda h: series.perfect(h) if h == 2 else series.flat("sharp", h, 0.0)
        tiers = series.judged(two_days)["candidates"]["sharp"]["tiers"]["onset_warning"]
        self.assertEqual(tiers["lead_at_least_1"]["recall"]["mean"], 0.95)
        self.assertEqual(tiers["lead_at_least_2"]["recall"]["mean"], 0.95)
        self.assertTrue(tiers["lead_at_least_2"]["meets_far_recall"])
        self.assertTrue(tiers["lead_at_least_2"]["reported_only"])

    def _wolf(self, series, h=None):
        """Flags each onset and the two days before it, until day 200, then the onsets only."""

        return series.forecast(
            "sharp", h, [1.0 if (y or (k < 200 and k % 20 in (2, 3))) else 0.0 for k, y in enumerate(series.y5)]
        )

    def test_a_flag_on_every_abundant_day_is_crying_wolf(self):
        series = Series()
        result = series.judged(lambda h: self._wolf(series, h))["candidates"]["sharp"]
        tier = result["tiers"]["no_crying_wolf"]["1"]
        stretch = tier["abundant_stretches"]["scarcity_state_0"]
        self.assertEqual(stretch["days"], 200)
        # 9 refits of 3 flags in the 200 abundant days.
        self.assertEqual(stretch["flags"], 27)
        self.assertGreater(stretch["flags_per_year"], 21)
        self.assertFalse(stretch["ok"])
        self.assertFalse(tier["ok"])
        self.assertFalse(result["verdict"]["tier_3_no_crying_wolf"])
        self.assertFalse(result["verdict"]["passes"])

    def test_the_alarm_rate_is_per_252_business_days(self):
        series = Series()
        result = series.judged(lambda h: series.perfect(h))["candidates"]["sharp"]
        stretch = result["tiers"]["no_crying_wolf"]["1"]["abundant_stretches"]["scarcity_state_0"]
        # Nine of the ten pressure days of the 200 days are flagged (the first refit flags nothing).
        self.assertAlmostEqual(stretch["flags_per_year"], 9 / 200 * 252)
        regime = result["tiers"]["no_crying_wolf"]["1"]["abundant_stretches"]["regime_b"]
        self.assertTrue(regime["days"] > 0)

    def test_a_miscalibrated_regime_fails_tier_three(self):
        series = Series()
        # Never flags (below the cut-off) but predicts 10% where pressure runs at 5%.
        high = lambda h: series.flat("sharp", h, 0.1)
        result = series.judged(high)["candidates"]["sharp"]
        calibrated = result["tiers"]["no_crying_wolf"]["1"]["calibrated_by_regime"]
        self.assertEqual(set(calibrated), {"a", "b"})
        self.assertFalse(calibrated["a"])
        self.assertTrue(result["tiers"]["no_crying_wolf"]["1"]["abundant_stretches"]["scarcity_state_0"]["ok"])
        self.assertFalse(result["tiers"]["no_crying_wolf"]["1"]["ok"])

    def test_calibration_is_tested_only_in_regimes_with_a_pressure_day(self):
        series = Series()
        # Pressure only from day 261 on, the start of regime "b": regime "a" has no pressure day.
        series.y5 = tuple(1 if (k >= 261 and k % 20 == 4) else 0 for k in range(400))
        series.y10 = tuple(0 for _ in range(400))
        # Regime "a" is predicted at 10% where nothing happens (miscalibrated); regime "b" at the
        # 5% it runs at.
        forecast = lambda h: series.forecast(
            "sharp", h, [0.1 if k < 261 else 0.05 for k in range(400)], [0.0] * 400
        )
        result = series.judged(forecast)["candidates"]["sharp"]
        wolf = result["tiers"]["no_crying_wolf"]["1"]
        self.assertEqual(wolf["calibrated_by_regime"], {"b": True})
        self.assertEqual(set(wolf["calibration_reported_regimes"]), {"a"})
        self.assertFalse(wolf["calibration_reported_regimes"]["a"]["covers_zero"])
        self.assertEqual(wolf["calibration_reported_regimes"]["a"]["events"], 0)
        # The untested regime does not decide tier 3.
        self.assertTrue(wolf["ok"])

    def test_tier_three_needs_every_lead(self):
        series = Series()
        wolf_at_two = lambda h: series.perfect(h) if h == 1 else self._wolf(series, h)
        verdict = series.judged(wolf_at_two)["candidates"]["sharp"]["verdict"]
        self.assertTrue(verdict["tier_3_no_crying_wolf_by_horizon"]["1"])
        self.assertFalse(verdict["tier_3_no_crying_wolf_by_horizon"]["2"])
        self.assertFalse(verdict["passes"])

    def test_the_scarce_regime_pass_is_reported_beside_the_pass_rule(self):
        series = Series()
        verdict = series.judged(lambda h: series.perfect(h))["candidates"]["sharp"]["verdict"]
        scarce = verdict["scarce_regime"]
        self.assertTrue(scarce["reported_only"])
        self.assertEqual(scarce["scarcity_state_at_least"], 2)
        # Days 200-399 are state 2: ten onsets, none missed (every refit from day 200 has seen onsets).
        self.assertEqual(scarce["days_by_horizon"], {"1": 200, "2": 200})
        self.assertEqual(scarce["onsets"], 10)
        self.assertEqual(scarce["recall"]["mean"], 1.0)
        self.assertTrue(scarce["tier_1_onset_warning"])
        self.assertTrue(scarce["tier_3_no_crying_wolf"])
        self.assertTrue(scarce["tier_5_week_ahead"])
        self.assertTrue(scarce["passes"])

    def test_the_scarce_regime_pass_is_not_part_of_the_pass_rule(self):
        series = Series()
        # Pressure only in the first 200 days (all abundant): the scarce regime has no onset, so it
        # cannot pass, and the pass rule on all days does not care.
        series.y5 = tuple(1 if (k < 200 and k % 20 == 4) else 0 for k in range(400))
        series.y10 = tuple(0 for _ in range(400))
        perfect = lambda h: series.forecast(
            "sharp", h, [1.0 if y else 0.0 for y in series.y5], [0.0] * 400
        )
        verdict = series.judged(perfect)["candidates"]["sharp"]["verdict"]
        self.assertFalse(verdict["scarce_regime"]["passes"])
        self.assertFalse(verdict["scarce_regime"]["tier_1_onset_warning"])
        self.assertTrue(verdict["passes"])

    def test_the_scarce_regime_is_unavailable_with_no_scarce_day(self):
        series = Series()
        series.groups = {**series.groups, "scarcity_state": tuple("0" for _ in range(400))}
        verdict = series.judged(lambda h: series.perfect(h))["candidates"]["sharp"]["verdict"]
        self.assertFalse(verdict["scarce_regime"]["passes"])
        self.assertIn("unavailable", verdict["scarce_regime"])

    def test_risky_dates_are_scored_in_scarcity_state_two_or_more(self):
        series = Series()
        risky = series.judged(lambda h: series.perfect(h))["candidates"]["sharp"]["tiers"]["risky_dates"]
        # Days 200..399 are state 2; every 10th is a risk date; half of those are pressure days.
        self.assertEqual(risky["days"], 20)
        self.assertEqual(risky["events"], 10)
        self.assertEqual(risky["auroc"], 1.0)
        self.assertEqual(risky["climatology_auroc"], 0.5)
        self.assertEqual(risky["auroc_difference"]["mean"], 0.5)
        self.assertTrue(risky["meets_auroc"])
        self.assertTrue(risky["reported_only"])

    def test_the_week_ahead_window_is_one_if_any_of_the_next_days_is_a_pressure_day(self):
        series = Series()
        week = series.judged(lambda h: series.perfect(h))["candidates"]["sharp"]["tiers"]["week_ahead"]
        # Decision days 0..397 have both targets: pressure days at 4, 24, ... flag the
        # two days before them.
        self.assertEqual(week["days"], 398)
        self.assertEqual(week["events"], 40)
        self.assertEqual(week["brier"], 0.0)
        self.assertEqual(week["combine"], "independence")

    def test_the_published_baseline_may_cover_fewer_horizons_and_cannot_then_pass(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        forecasts.append(series.perfect(1, name="published"))
        result = pj.judge(_load(), grids, forecasts, calendar=series.dates)
        published = result["candidates"]["published"]
        self.assertEqual(published["scored_horizons"], [1])
        self.assertEqual(list(published["horizons"]), ["1"])
        self.assertIn("unavailable", published["tiers"]["week_ahead"])
        self.assertFalse(published["tiers"]["onset_warning"]["lead_at_least_1"]["complete"])
        self.assertFalse(published["verdict"]["passes"])
        self.assertEqual(published["verdict"]["not_scored"], [2])

    def test_a_candidate_that_is_not_a_baseline_must_cover_every_horizon(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        forecasts = [f for f in forecasts if not (f.name == "sharp" and f.horizon == 2)]
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_splits_by_every_declared_grouping_and_the_holdouts(self):
        series = Series()
        holdouts = {"window": (series.dates[100], series.dates[130])}
        result = series.judged(lambda h: series.perfect(h), holdouts=holdouts)
        row = result["candidates"]["sharp"]["horizons"]["1"]["5"]
        self.assertEqual(set(row["splits"]), {"regime", "day_type"})
        self.assertEqual(set(row["splits"]["regime"]), {"a", "b"})
        cell = row["splits"]["regime"]["a"]
        # Regime "a" (2019) holds 13 onsets; the first falls in the refit with no training window.
        self.assertEqual(cell["flags"]["recall"], 12 / 13)
        self.assertIn("brier_difference_vs_climatology", cell)
        self.assertIn("realised_minus_predicted", cell)
        held = row["holdouts"]["window"]
        self.assertEqual(held["days"], 31)
        self.assertEqual(held["flags"]["recall"], 1.0)

    def test_the_benchmarks_are_judged_too(self):
        result = Series().judged(lambda h: Series().perfect(h))
        self.assertIn("calendar_climatology", result["candidates"])
        self.assertIn("persistence_logistic", result["candidates"])
        self.assertEqual(result["candidates"]["calendar_climatology"]["role"], "benchmark")
        self.assertFalse(result["candidates"]["calendar_climatology"]["verdict"]["passes"])

    def test_the_result_carries_the_declaration_digest(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        declaration = _load()
        result = pj.judge(declaration, grids, forecasts, calendar=series.dates)
        self.assertEqual(result["declaration"]["sha256"], declaration.sha256)
        self.assertEqual(result["declaration"]["last_scored_day"], "2025-12-31")
        self.assertEqual(result["mode"], "development")


class InputTests(unittest.TestCase):
    def test_forecasts_are_read_from_a_horizon_document(self):
        document = {
            "horizon": 2,
            "forecasts": {
                "m": {
                    "5": {"2019-01-03": 0.1, "2019-01-02": 0.2},
                    "10": {"2019-01-02": 0.05, "2019-01-03": 0.01},
                }
            },
        }
        (forecast,) = pj.forecasts_from_horizon_document(document)
        self.assertEqual(forecast.horizon, 2)
        self.assertEqual(forecast.dates, (date(2019, 1, 2), date(2019, 1, 3)))
        self.assertEqual(forecast.probabilities[5.0], (0.2, 0.1))
        self.assertEqual(forecast.probabilities[10.0], (0.05, 0.01))

    def test_a_report_becomes_a_forecast_at_its_own_thresholds(self):
        class Report:
            horizon = 3
            scored_dates = (date(2019, 1, 2), date(2019, 1, 3))
            taus = (5.0, 10.0)
            forecast = ((0.3, 0.1), (0.2, 0.05))

        forecast = pj.report_forecast("m", Report)
        self.assertEqual(forecast.horizon, 3)
        self.assertEqual(forecast.probabilities, {5.0: (0.3, 0.2), 10.0: (0.1, 0.05)})

    def test_a_forecast_is_cut_to_the_look_window_with_its_values_unchanged(self):
        forecast = pj.Forecast(
            name="m", horizon=1, dates=(date(2025, 12, 30), date(2026, 1, 2), date(2026, 1, 5)),
            probabilities={5.0: (0.1, 0.2, 0.3), 10.0: (0.01, 0.02, 0.03)},
        )
        cut = pj.restrict_forecast(forecast, date(2026, 1, 1), date(2026, 9, 3))
        self.assertEqual(cut.dates, (date(2026, 1, 2), date(2026, 1, 5)))
        self.assertEqual(cut.probabilities, {5.0: (0.2, 0.3), 10.0: (0.02, 0.03)})

    def test_the_grid_reads_outcomes_onsets_and_the_declared_groupings(self):
        from repo_model.data import DailyObservation
        from repo_model.evaluation_splits import load_split_declaration

        splits = load_split_declaration(Path(__file__).parents[1] / "metadata" / "evaluation_splits.json")
        # Six calm days, then +7 (an onset: nothing above +5 before it) and +8 (not one).
        spreads = [0.0] * 6 + [7.0, 8.0, 11.0]
        days = _weekdays(len(spreads), date(2019, 1, 2))
        rows = [
            DailyObservation(
                day,
                {
                    "sofr": 4.0 + value / 100.0, "iorb": 4.0, "days_to_month_end": 20.0,
                    "quarter_end": 1.0 if k == 6 else 0.0, "tax_date": 0.0,
                    "treasury_settlement_coupons": 1.0 if k == 8 else 0.0,
                },
            )
            for k, (day, value) in enumerate(zip(days, spreads))
        ]
        grid = pj.build_grid(
            _load(groupings=["regime", "scarcity_state", "day_type"]),
            1, rows, days, splits,
            scarcity_state={days[6]: 2.0, days[7]: None},
        )
        # Whole basis points, strictly above: a day on +5 is not above +5.
        self.assertEqual(grid.outcomes[5.0], (0,) * 6 + (1, 1, 1))
        self.assertEqual(grid.outcomes[10.0], (0,) * 8 + (1,))
        self.assertEqual(grid.onset, (0,) * 6 + (1, 0, 0))
        # Onsets at every declared threshold, for the cut-off rule: +10 bp opens on the 11.
        self.assertEqual(grid.onsets[5.0], grid.onset)
        self.assertEqual(grid.onsets[10.0], (0,) * 8 + (1,))
        self.assertEqual(grid.groups["scarcity_state"][6:8], ("2", "unknown"))
        self.assertEqual(grid.groups["regime"], ("2018-19",) * 9)
        self.assertEqual(grid.groups["risk_date"], ("0",) * 6 + ("1", "0", "1"))
        with self.assertRaises(ValueError):
            pj.build_grid(
                _load(), 1, rows, [date(2019, 2, 7)], splits, scarcity_state={},
            )


if __name__ == "__main__":
    unittest.main()
