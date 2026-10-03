"""The live record (#215): the daily script, the scoring script and the workflow.

Eleonora's decision of 3 October 2026 (#215): every business day after the
16:00 ET decision instant, a scheduled GitHub Actions workflow logs the
published pressure model v1's forecast, and its baselines', as one frozen JSON
record on the append-only `live-log` branch. The record is scored only on the
pre-registered dates, and only once the drafted lockbox amendment is merged.

These tests pin what the directive fixes before any day is logged:

* the workflow's triggers, permissions and action pins
  (`WorkflowFileTests`);
* the decision-day calendar and the clean exit on any other day
  (`DecisionDayTests`);
* the record's schema, the refusal to overwrite a day and the refusal to log a
  day on or before the panel end, 2026-09-03 (`RecordTests`);
* the scoring dates, the refusal while the lockbox amendment is unmerged, and
  the headline-verdict rule (`ScoringGuardTests`, `HeadlineVerdictTests`);
* that a forecast read off placeholder rows is refused (`PlaceholderGuardTests`);
* that the baselines' forecasts in a record are the repository's baseline
  functions' on the same panel (`BaselineAgreementTests`).

Red first: this file was committed, and run, before `scripts/live_record.py`,
`scripts/live_score.py` and `.github/workflows/live-log.yml` existed; every
class failed at import or on the missing workflow file.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import shutil
import tempfile
import unittest
from datetime import date, time
from pathlib import Path

from repo_model import onset
from repo_model.asof import InformationRule
from repo_model.baseline import (
    calendar_climatology_exceedance,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.cli import main as cli_main
from repo_model.data import load_daily_panel, load_stress_thresholds
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WORKFLOW = ROOT / ".github" / "workflows" / "live-log.yml"
REGISTRY = ROOT / "metadata" / "sources.json"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
#: The published panel's build (`metadata/funding_panel_manifest.json`).
CUTOFF = "2026-09-08T21:31:42+00:00"


def _script(name):
    spec = importlib.util.spec_from_file_location(f"live_test_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


live = _script("live_record")
score = _script("live_score")


def _record(day="2026-10-02"):
    """A well-formed record, with made-up numbers, for the schema tests."""

    targets = []
    forecasts = {}
    for h in live.HORIZONS:
        targets.append(
            {
                "horizon": h,
                "target_date": "2026-10-09",
                "anchor_date": "2026-10-01",
                "anchor_spread_bp": 1,
                "leap_threshold_bp": onset.LEAP_JUMP_BP[h],
                "train_end": "2026-09-25",
            }
        )
        forecasts[str(h)] = {name: 0.1 for name in live.TARGET_NAMES}
    leap_only = {str(h): {name: 0.1 for name in live.LEAP_TARGETS} for h in live.HORIZONS}
    pressure_only = {
        str(h): {name: 0.1 for name in live.PRESSURE_TARGETS} for h in live.HORIZONS
    }
    return {
        "record_version": live.RECORD_VERSION,
        "decision_day": day,
        "decision_instant": f"{day}T16:00:00-04:00",
        "code": {"sha": "0" * 40, "pinned_sha": "0" * 40},
        "packages": {"python": "3.11.15", "numpy": "2.4.6", "scikit-learn": "1.9.1"},
        "inputs": {
            "snapshots": [
                {
                    "source_id": "nyfed_sofr",
                    "sha256": "1" * 64,
                    "retrieved_at": f"{day}T21:31:00+00:00",
                    "url": "https://markets.newyorkfed.org/",
                }
            ],
            "build_cutoff": f"{day}T21:31:00+00:00",
            "panel_sha256": "2" * 64,
            "panel_last_date": "2026-10-01",
        },
        "targets": targets,
        "models": {
            "pressure_model_v1": {
                "declaration_sha256": {str(h): "3" * 64 for h in live.HORIZONS},
                "forecasts": forecasts,
            }
        },
        "baselines": {
            "persistence_logistic": {"forecasts": pressure_only},
            "calendar_climatology": {"forecasts": pressure_only},
            onset.LEAP_PERSISTENCE_LOGISTIC: {"forecasts": leap_only},
            onset.LEAP_CALENDAR_CLIMATOLOGY: {"forecasts": leap_only},
        },
        "run": {
            "started_at": f"{day}T21:30:00+00:00",
            "finished_at": f"{day}T22:00:00+00:00",
            "durations_seconds": {step: 1.0 for step in live.STEPS},
        },
    }


class WorkflowFileTests(unittest.TestCase):
    """The workflow's triggers, permissions and pins, read off the file.

    Stdlib only, so no YAML parser: the file is read as indented lines, and
    the checks below are on its top-level `on:` and `permissions:` blocks and
    on every `uses:` line.
    """

    @classmethod
    def setUpClass(cls):
        cls.lines = WORKFLOW.read_text(encoding="utf-8").splitlines()

    def _block(self, key):
        """The keys directly under the top-level `key:`, and their values."""

        out = {}
        inside = False
        for line in self.lines:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line.startswith(" "):
                inside = line.split("#")[0].strip() == f"{key}:"
                continue
            if inside and re.match(r"^  [^ ]", line):
                name, _, value = line.strip().partition(":")
                out[name.strip().strip('"')] = value.split("#")[0].strip()
        return out

    def test_triggers_are_schedule_and_dispatch_only(self):
        self.assertEqual(set(self._block("on")), {"schedule", "workflow_dispatch"})

    def test_permissions_are_exactly_contents_and_issues_write(self):
        self.assertEqual(self._block("permissions"), {"contents": "write", "issues": "write"})
        # Declared once, at the workflow level: no job grants itself more.
        declared = [line for line in self.lines if re.match(r"^\s*permissions:", line)]
        self.assertEqual(declared, ["permissions:"])

    def test_every_action_is_pinned_to_a_full_commit_sha(self):
        uses = [line.strip() for line in self.lines if re.match(r"^\s*-?\s*uses:", line)]
        self.assertTrue(uses, "the workflow uses no action at all")
        for line in uses:
            with self.subTest(line=line):
                self.assertRegex(line, r"uses: [\w.-]+/[\w./-]+@[0-9a-f]{40} # v\d")

    def test_the_ml_extra_is_pinned_to_the_versions_ci_uses(self):
        text = "\n".join(self.lines)
        self.assertIn('"numpy==2.4.6"', text)
        self.assertIn('"scikit-learn==1.9.1"', text)
        ci = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        self.assertIn('"numpy==2.4.6" "scikit-learn==1.9.1"', ci)

    def test_it_runs_after_the_decision_instant_on_weekdays(self):
        schedule = [line for line in self.lines if "cron:" in line]
        self.assertEqual(len(schedule), 1)
        self.assertIn('"30 21 * * 1-5"', schedule[0])


class DecisionDayTests(unittest.TestCase):
    def test_a_weekday_with_sofr_is_a_decision_day(self):
        self.assertTrue(live.is_decision_day(date(2026, 10, 2)))

    def test_weekends_and_market_holidays_are_not(self):
        for day in (date(2026, 10, 3), date(2026, 10, 4), date(2026, 10, 12), date(2026, 11, 26)):
            with self.subTest(day=day):
                self.assertFalse(live.is_decision_day(day))

    def test_a_day_the_holiday_table_does_not_cover_is_refused(self):
        with self.assertRaises(ValueError):
            live.is_decision_day(date(2028, 1, 3))

    def test_the_target_days_skip_holidays(self):
        self.assertEqual(
            live.next_decision_days(date(2026, 10, 9), 2), [date(2026, 10, 13), date(2026, 10, 14)]
        )

    def test_a_non_decision_day_writes_nothing_and_exits_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = live.main(
                    ["run", "--date", "2026-10-03", "--out-dir", tmp,
                     "--raw-root", str(Path(tmp) / "never-read")]
                )
            self.assertEqual(code, 0)
            self.assertEqual(list(Path(tmp).iterdir()), [])
            self.assertIn("not a decision day", out.getvalue())


class RecordTests(unittest.TestCase):
    def test_a_well_formed_record_passes(self):
        live.validate_record(_record())

    def test_each_malformation_is_refused(self):
        def without(key):
            record = _record()
            del record[key]
            return record

        def bad_probability():
            record = _record()
            record["models"]["pressure_model_v1"]["forecasts"]["1"]["+5bp"] = 1.5
            return record

        def missing_horizon():
            record = _record()
            del record["baselines"]["persistence_logistic"]["forecasts"]["3"]
            return record

        def no_v1():
            record = _record()
            record["models"] = {}
            return record

        cases = {f"no {key}": without(key) for key in live.RECORD_KEYS}
        cases.update(
            {
                "probability above 1": bad_probability(),
                "a horizon missing": missing_horizon(),
                "no model": no_v1(),
            }
        )
        for name, record in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(ValueError):
                    live.validate_record(record)

    def test_a_day_is_written_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = live.write_record(Path(tmp), _record())
            self.assertEqual(path, Path(tmp) / "live" / "2026-10-02.json")
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                live.write_record(Path(tmp), _record())
            self.assertEqual(path.read_bytes(), before)

    def test_no_day_on_or_before_the_panel_end_is_written(self):
        for day in ("2026-09-03", "2025-12-31"):
            with self.subTest(day=day):
                with tempfile.TemporaryDirectory() as tmp:
                    with self.assertRaises(ValueError):
                        live.write_record(Path(tmp), _record(day))
                    with self.assertRaises(ValueError):
                        live.main(["run", "--date", day, "--out-dir", tmp])
                    self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_the_first_loggable_day_follows_the_panel_end(self):
        self.assertEqual(live.PANEL_END, date(2026, 9, 3))
        live.require_loggable(date(2026, 9, 4))


class ScoringGuardTests(unittest.TestCase):
    def test_the_scoring_dates_are_the_pre_registered_ones(self):
        for day in (date(2027, 4, 1), date(2027, 10, 1), date(2028, 10, 1), date(2035, 10, 1)):
            with self.subTest(day=day):
                score.require_scoring_date(day)

    def test_any_other_date_is_refused(self):
        for day in (
            date(2026, 10, 1), date(2027, 3, 31), date(2027, 4, 2),
            date(2028, 4, 1), date(2027, 9, 30),
        ):
            with self.subTest(day=day):
                with self.assertRaises(ValueError):
                    score.require_scoring_date(day)

    def test_the_tracked_lockbox_has_no_amendment_so_scoring_is_refused(self):
        with self.assertRaises(ValueError):
            score.require_amendment(ROOT / "docs" / "decisions" / "lockbox.md")

    def test_a_merged_amendment_lets_scoring_through_the_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lockbox.md"
            path.write_text(
                (ROOT / "docs" / "decisions" / "lockbox.md").read_text(encoding="utf-8")
                + "\n" + score.AMENDMENT_HEADING + "\n\nText.\n",
                encoding="utf-8",
            )
            score.require_amendment(path)

    def test_the_draft_carries_the_heading_the_guard_reads(self):
        draft = ROOT / "docs" / "decisions" / "drafts" / "lockbox-live-record.md"
        self.assertIn(score.AMENDMENT_HEADING, draft.read_text(encoding="utf-8"))

    def test_the_script_refuses_to_run_while_the_amendment_is_unmerged(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                score.main(
                    ["--date", "2027-04-01", "--live-dir", tmp, "--panel", str(Path(tmp) / "p.csv"),
                     "--output", str(Path(tmp) / "out.json")]
                )
            self.assertFalse((Path(tmp) / "out.json").exists())

    def test_the_script_refuses_a_non_scoring_date_before_reading_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                score.main(
                    ["--date", "2027-04-02", "--live-dir", tmp, "--panel", str(Path(tmp) / "p.csv"),
                     "--output", str(Path(tmp) / "out.json")]
                )


class HeadlineVerdictTests(unittest.TestCase):
    """The verdict is fixed at the first date the headline cell has enough events."""

    def test_before_the_minimum_every_date_is_inconclusive(self):
        self.assertEqual(
            score.headline_status(date(2027, 4, 1), events=onset.MINIMUM_EVENTS - 1, previous=[]),
            "inconclusive",
        )

    def test_the_first_date_that_meets_the_minimum_is_the_verdict(self):
        previous = [{"date": "2027-04-01", "headline_status": "inconclusive"}]
        self.assertEqual(
            score.headline_status(date(2027, 10, 1), events=onset.MINIMUM_EVENTS, previous=previous),
            "headline_verdict",
        )

    def test_every_later_date_is_an_update(self):
        previous = [
            {"date": "2027-04-01", "headline_status": "inconclusive"},
            {"date": "2027-10-01", "headline_status": "headline_verdict"},
        ]
        for events in (onset.MINIMUM_EVENTS - 1, onset.MINIMUM_EVENTS + 50):
            with self.subTest(events=events):
                self.assertEqual(
                    score.headline_status(date(2028, 10, 1), events=events, previous=previous),
                    "update",
                )

    def test_a_previous_result_on_or_after_the_date_is_refused(self):
        previous = [{"date": "2027-10-01", "headline_status": "inconclusive"}]
        with self.assertRaises(ValueError):
            score.headline_status(date(2027, 10, 1), events=30, previous=previous)

    def test_the_headline_cell_is_the_plain_leap_at_horizon_one(self):
        self.assertEqual(score.HEADLINE, {"target": "leap", "horizon": 1})


def _fixture_panel(tmp):
    """The published panel, built from the tracked fixtures, and its point-in-time rows."""

    panel = Path(tmp) / "funding_panel.csv"
    with contextlib.redirect_stdout(io.StringIO()):
        code = cli_main(
            ["build", "--raw-root", str(FIXTURES), "--output", str(panel),
             "--build-cutoff", CUTOFF, "--decision-time", "16:00:00"]
        )
    if code != 0:
        raise RuntimeError("the fixture panel did not build")
    return panel, panel.with_name(panel.stem + "_point_in_time.csv")


class PlaceholderGuardTests(unittest.TestCase):
    """An observed read on a placeholder row is refused (`LookAheadError`).

    Mutation record (#215). In a disposable copy, `live_record.require_reads_on_real_rows`'s
    comparison `read.row > last_real` changed to `read.row > last_real + 1`, so an
    observed read one row into the placeholders passes. Killed
    `test_an_observed_read_on_a_placeholder_is_refused` alone, `AssertionError`
    (`LookAheadError not raised`); the rest of this module stayed green.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        panel, _ = _fixture_panel(cls.tmp)
        cls.rows = load_daily_panel(panel)
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _rule(self, h):
        features = live.V1_FEATURES[h]
        return InformationRule(self.registry, features, decision_time=time(16), horizon=h)

    def test_reads_on_real_rows_pass(self):
        index = len(self.rows) - 1
        for h in live.HORIZONS:
            with self.subTest(h=h):
                live.require_reads_on_real_rows(self.rows, self._rule(h), index, index - h)

    def test_an_observed_read_on_a_placeholder_is_refused(self):
        # Pretend the panel's real rows stopped one row earlier than they do:
        # the spread the forecast reads (published the day before the
        # decision) then sits on a "placeholder".
        index = len(self.rows) - 1
        with self.assertRaises(LookAheadError):
            live.require_reads_on_real_rows(self.rows, self._rule(1), index, index - 2)


class BaselineAgreementTests(unittest.TestCase):
    """A record's baseline forecasts are the repository's baseline functions'.

    The daily script makes its forecast on the panel as built at the decision
    day, the rows up to the day before it, extended by placeholder rows for the
    decision day and the target days. Here that is replayed on the published
    panel at a decision day before the lockbox: the panel cut at the day
    before, extended, and the script's baselines compared with the repository's
    own functions run over the uncut panel, scoring the same target day.
    """

    DECISION_DAY = date(2025, 12, 29)

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        panel, cls.pit = _fixture_panel(cls.tmp)
        cls.rows = load_daily_panel(panel)
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.splits = load_split_declaration(SPLITS)
        cls.taus = tuple(
            float(t) for t in load_stress_thresholds(ROOT / "metadata" / "stress_thresholds.json")["taus_bp"]
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _cut(self):
        return [row for row in self.rows if row.date < self.DECISION_DAY]

    def test_the_extension_follows_the_market_calendar(self):
        extended, targets = live.extend_panel(
            self._cut(), self.DECISION_DAY, max(live.HORIZONS), self.pit
        )
        real = [row.date for row in self.rows if row.date >= self.DECISION_DAY][: 1 + max(live.HORIZONS)]
        self.assertEqual([row.date for row in extended[-len(real):]], real)
        self.assertEqual(targets, real[1:])

    def test_the_extension_carries_the_calendar_and_the_settlements(self):
        extended, _ = live.extend_panel(self._cut(), self.DECISION_DAY, max(live.HORIZONS), self.pit)
        truth = {row.date: row for row in self.rows}
        for row in extended[len(self._cut()):]:
            for column in live.PLACEHOLDER_COLUMNS:
                with self.subTest(day=row.date, column=column):
                    self.assertEqual(row.values.get(column), truth[row.date].values.get(column))

    def test_a_panel_that_misses_the_day_before_is_refused(self):
        with self.assertRaises(ValueError):
            live.extend_panel(self._cut()[:-1], self.DECISION_DAY, 1, self.pit)

    def test_the_baselines_match_the_repository_functions(self):
        for h in (1, 3):
            extended, targets = live.extend_panel(self._cut(), self.DECISION_DAY, h, self.pit)
            target = targets[h - 1]
            got = live.baseline_forecasts(extended, h, self.registry, self.splits, self.taus)
            for name, predictor, features in (
                (
                    "calendar_climatology",
                    calendar_climatology_exceedance(self.splits, minimum_history=live.MINIMUM_HISTORY),
                    live.CALENDAR_FEATURES,
                ),
                (
                    "persistence_logistic",
                    persistence_logistic_exceedance(minimum_history=live.MINIMUM_HISTORY),
                    ("spread_bps",),
                ),
            ):
                report = rolling_exceedance_backtest(
                    self.rows, predictor=predictor, model_name=name, features=features,
                    registry=self.registry, decision_time=time(16), taus=self.taus,
                    minimum_history=live.MINIMUM_HISTORY, refit_every=live.REFIT_EVERY,
                    end=target, horizon=h,
                )
                self.assertEqual(report.scored_dates[-1], target)
                for position, tau in enumerate(self.taus):
                    if tau not in live.TAUS:
                        continue
                    with self.subTest(h=h, baseline=name, tau=tau):
                        self.assertEqual(
                            got[name][f"+{tau:g}bp"], report.forecast[-1][position]
                        )
            # The leap baselines, fitted on the same refit block.
            train_end = got["train_end"]
            report_train_end = report.folds[-1].train_end
            self.assertEqual(train_end, report_train_end)
            rule = InformationRule(self.registry, ("spread_bps",), decision_time=time(16), horizon=h)
            targets_full = onset.LeapTargets(self.rows, rule, onset.LEAP_JUMP_BP[h])
            for kind in live.LEAP_TARGETS:
                expected = {
                    onset.LEAP_CALENDAR_CLIMATOLOGY: onset.leap_calendar_climatology(
                        targets_full, kind, [target], [report_train_end], self.splits
                    )[0],
                    onset.LEAP_PERSISTENCE_LOGISTIC: onset.leap_persistence_logistic(
                        targets_full, kind, [target], [report_train_end]
                    )[0],
                }
                for name, value in expected.items():
                    with self.subTest(h=h, baseline=name, target=kind):
                        self.assertEqual(got[name][kind], value)


if __name__ == "__main__":
    unittest.main()
