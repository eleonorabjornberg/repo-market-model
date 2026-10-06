"""The live record (#215): the daily script, the scoring script and the workflow.

Eleonora's decision of 3 October 2026 (#215): every business day after the
16:00 ET decision instant, a scheduled GitHub Actions workflow logs the
published pressure model v1's forecast, and its baselines', as one frozen JSON
record on the append-only `live-log` branch. The record is scored only on the
pre-registered dates, and only on days `metadata/lockbox.json` has opened (#277).

These tests pin what the directive fixes before any day is logged:

* the workflow's triggers, permissions and action pins
  (`WorkflowFileTests`);
* the decision-day calendar and the clean exit on any other day
  (`DecisionDayTests`);
* the record's schema, the refusal to overwrite a day and the refusal to log a
  day on or before the panel end, 2026-09-03 (`RecordTests`);
* the scoring dates and the headline-verdict rule (the lockbox guard is in
  `test_live_lockbox.py`) (`ScoringGuardTests`, `HeadlineVerdictTests`);
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
from unittest import mock

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

from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)

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
        "distributions": {
            "levels": list(live.QUANTILE_LEVELS),
            "published": {
                "records": {str(h): live.published_distribution_record(h) for h in live.HORIZONS},
                "declaration_sha256": {str(h): "4" * 64 for h in live.HORIZONS},
                "quantiles_bps": {str(h): [-2.0, 0.0, 1.0, 2.0, 5.0] for h in live.HORIZONS},
            },
            "persistence": {
                "quantiles_bps": {str(h): [-4.0, -1.0, 1.0, 3.0, 8.0] for h in live.HORIZONS},
            },
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

    def test_permissions_are_exactly_contents_issues_and_id_token_write(self):
        # id-token: write is for cosign's keyless signing into Rekor (#254,
        # Eleonora's ruling of 6 October 2026); it holds no secret.
        self.assertEqual(
            self._block("permissions"),
            {"contents": "write", "issues": "write", "id-token": "write"},
        )
        # Declared once, at the workflow level: no job grants itself more.
        declared = [line for line in self.lines if re.match(r"^\s*permissions:", line)]
        self.assertEqual(declared, ["permissions:"])

    def test_every_action_is_pinned_to_a_full_commit_sha(self):
        # The workflow uses none today (Python from the runner's tool cache,
        # git and gh from the runner); one added later is pinned or refused.
        uses = [line.strip() for line in self.lines if re.match(r"^\s*-?\s*uses:", line)]
        for line in uses:
            with self.subTest(line=line):
                self.assertRegex(line, r"uses: [\w.-]+/[\w./-]+@[0-9a-f]{40} # v\d")

    def test_the_ml_extra_is_pinned_to_the_versions_ci_uses(self):
        text = "\n".join(self.lines)
        self.assertIn('"numpy==2.4.6"', text)
        self.assertIn('"scikit-learn==1.9.1"', text)
        ci = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        self.assertIn('"numpy==2.4.6" "scikit-learn==1.9.1"', ci)

    def test_the_record_is_never_a_dry_run(self):
        text = "\n".join(self.lines)
        self.assertIn("scripts/live_record.py run", text)
        self.assertNotIn("--dry-run", text)

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

    def test_the_draft_states_the_not_evidence_label_for_later_horizons(self):
        """Eleonora's ruling of 4 October 2026 (#229): the draft states the label verbatim."""

        draft = ROOT / "docs" / "decisions" / "drafts" / "lockbox-live-record.md"
        text = " ".join(draft.read_text(encoding="utf-8").split())
        self.assertIn(
            "different model from h = 1, and as-of persistence does not widen with horizon, "
            "so this comparison favours the model; not evidence.",
            text,
        )

    def test_the_script_refuses_a_locked_day_and_writes_nothing(self):
        """Under the tracked declaration the first logged day is in the blind tier (#277)."""

        from repo_model import lockbox

        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            lockbox, "DEFAULT_LOCKBOX", ROOT / "metadata" / "lockbox.json"
        ):
            with self.assertRaises(LookAheadError):
                score.assemble(records, rows, load_split_declaration(SPLITS), date(2027, 4, 1),
                               previous=[])
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_the_script_refuses_a_non_scoring_date_before_reading_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                score.main(
                    ["--date", "2027-04-02", "--live-dir", tmp, "--panel", str(Path(tmp) / "p.csv"),
                     "--output", str(Path(tmp) / "out.json")]
                )


class HeadlineVerdictTests(unittest.TestCase):
    """The primary result's verdict is fixed once, at the first scoring date with a scored day.

    Eleonora's ruling of 4 October 2026 on #215 makes the CRPS cell at h = 1 the
    live record's primary result. CRPS has no minimum event count (every day
    counts, as in the final test), so the verdict is fixed at the first scoring
    date that scores any day.
    """

    def test_a_date_with_no_scored_day_is_inconclusive(self):
        self.assertEqual(score.headline_status(date(2027, 4, 1), days=0, previous=[]), "inconclusive")

    def test_the_first_date_with_a_scored_day_is_the_verdict(self):
        self.assertEqual(
            score.headline_status(date(2027, 4, 1), days=1, previous=[]), "headline_verdict"
        )
        previous = [{"date": "2027-04-01", "headline_status": "inconclusive"}]
        self.assertEqual(
            score.headline_status(date(2027, 10, 1), days=120, previous=previous),
            "headline_verdict",
        )

    def test_every_later_date_is_an_update(self):
        previous = [
            {"date": "2027-04-01", "headline_status": "inconclusive"},
            {"date": "2027-10-01", "headline_status": "headline_verdict"},
        ]
        for days in (0, 400):
            with self.subTest(days=days):
                self.assertEqual(
                    score.headline_status(date(2028, 10, 1), days=days, previous=previous),
                    "update",
                )

    def test_a_previous_result_on_or_after_the_date_is_refused(self):
        previous = [{"date": "2027-10-01", "headline_status": "inconclusive"}]
        with self.assertRaises(ValueError):
            score.headline_status(date(2027, 10, 1), days=30, previous=previous)

    def test_the_primary_result_is_the_crps_cell_at_horizon_one(self):
        self.assertEqual(score.HEADLINE, {"target": "crps", "horizon": 1})


class DistributionRecordTests(unittest.TestCase):
    """Each day's file carries both distributions, and the scorer needs nothing else.

    Eleonora's ruling of 4 October 2026 on #215, point 3: a test fails if a
    day's file lacks either distribution, or if the scorer cannot reproduce a
    day's CRPS from the file alone.
    """

    def test_a_file_without_either_distribution_is_refused(self):
        for side in ("published", "persistence"):
            with self.subTest(side=side):
                record = _record()
                del record["distributions"][side]
                with self.assertRaises(ValueError):
                    live.validate_record(record)

    def test_a_file_missing_a_horizon_or_a_quantile_is_refused(self):
        def missing_horizon():
            record = _record()
            del record["distributions"]["published"]["quantiles_bps"]["4"]
            return record

        def short_vector():
            record = _record()
            record["distributions"]["persistence"]["quantiles_bps"]["1"] = [0.0, 1.0]
            return record

        def other_levels():
            record = _record()
            record["distributions"]["levels"] = [0.1, 0.5, 0.9]
            return record

        def not_a_number():
            record = _record()
            record["distributions"]["published"]["quantiles_bps"]["2"][1] = None
            return record

        for name, make in {
            "a horizon missing": missing_horizon, "a short vector": short_vector,
            "other levels": other_levels, "not a number": not_a_number,
        }.items():
            with self.subTest(case=name):
                with self.assertRaises(ValueError):
                    live.validate_record(make())

    def test_the_scorer_reproduces_a_days_crps_from_the_file_alone(self):
        from repo_model.metrics import crps_from_quantiles

        record = json.loads(json.dumps(_record()))
        for h in live.HORIZONS:
            for side in ("published", "persistence"):
                for outcome in (-3.0, 0.0, 1.4, 12.0):
                    with self.subTest(h=h, side=side, outcome=outcome):
                        expected = crps_from_quantiles(
                            record["distributions"]["levels"],
                            record["distributions"][side]["quantiles_bps"][str(h)],
                            outcome,
                        )
                        self.assertEqual(score.crps_from_record(record, side, h, outcome), expected)

    def test_the_scorer_refuses_a_file_without_a_distribution(self):
        record = _record()
        del record["distributions"]["persistence"]
        with self.assertRaises(ValueError):
            score.crps_from_record(record, "persistence", 1, 0.0)


def _scoring_records(published, persistence, days=40):
    """`days` records, one a business day from 2026-10-05, with fixed distributions."""

    from repo_model.data import CALENDAR_COLUMN_RULES, DailyObservation

    records, rows = [], []
    day = date(2026, 10, 5)
    while len(records) < days:
        if live.is_decision_day(day):
            record = _record(day.isoformat())
            targets = live.next_decision_days(day, max(live.HORIZONS))
            for h in live.HORIZONS:
                record["targets"][h - 1]["target_date"] = targets[h - 1].isoformat()
                record["distributions"]["published"]["quantiles_bps"][str(h)] = list(published)
                record["distributions"]["persistence"]["quantiles_bps"][str(h)] = list(persistence)
            records.append(record)
        day = day.fromordinal(day.toordinal() + 1)
    last = date.fromisoformat(records[-1]["targets"][-1]["target_date"])
    current = date(2026, 10, 5)
    while current <= last:
        if live.is_decision_day(current):
            # The outcome: a spread of 1 bp (SOFR 4.01 against IORB 4.00).
            values = {"sofr": 4.01, "iorb": 4.00}
            values.update({column: rule(current) for column, rule in CALENDAR_COLUMN_RULES.items()})
            rows.append(DailyObservation(date=current, values=values))
        current = current.fromordinal(current.toordinal() + 1)
    return records, rows


class CrpsScoringTests(unittest.TestCase):
    """The live record's primary result: CRPS at h = 1, under the final test's pass rule."""

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)
        cls.final = _script("final_test_preregistration")

    def _cell(self, published, persistence, h=1):
        records, rows = _scoring_records(published, persistence)
        return score.score_crps(records, rows, self.splits, date(2027, 4, 1))[f"crps/h{h}"]

    def test_a_sharper_distribution_at_the_outcome_passes(self):
        cell = self._cell([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        self.assertGreater(cell["mean_difference_bps"], 0)
        self.assertEqual(cell["verdict"], "pass")
        self.assertEqual(cell["result"], "pass")
        self.assertEqual(cell["role"], "primary")

    def test_a_worse_distribution_is_labelled_worse(self):
        cell = self._cell([-6.0, -2.0, 1.0, 4.0, 9.0], [0.5, 0.8, 1.0, 1.2, 1.5])
        self.assertEqual(cell["verdict"], "worse")
        self.assertEqual(cell["result"], "fail")

    def test_identical_distributions_are_not_distinguishable(self):
        cell = self._cell([0.0, 0.5, 1.0, 1.5, 2.0], [0.0, 0.5, 1.0, 1.5, 2.0])
        self.assertEqual(cell["verdict"], "not distinguishable")
        self.assertEqual(cell["result"], "fail")

    def test_the_rule_and_labels_are_the_final_tests(self):
        import inspect

        # The scorer loads the final test's own file and uses its functions.
        self.assertEqual(Path(score.final_test.__file__), SCRIPTS / "final_test_preregistration.py")
        for name in ("crps_verdict", "crps_result"):
            with self.subTest(function=name):
                self.assertIs(getattr(score, name), getattr(score.final_test, name))
                self.assertEqual(inspect.getsource(getattr(score, name)),
                                 inspect.getsource(getattr(self.final, name)))
        cell = self._cell([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        self.assertEqual(cell["interval"]["level"], 0.9)
        self.assertEqual(cell["interval"]["block_length"], self.final.CRPS_BLOCK_LENGTH)
        self.assertEqual(cell["sensitivity_interval"]["block_length"],
                         self.final.CRPS_SENSITIVITY_BLOCK_LENGTH)
        self.assertEqual(cell["sensitivity_interval"]["seed"], cell["interval"]["seed"])

    def test_the_sensitivity_interval_decides_nothing(self):
        cell = self._cell([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        cell["sensitivity_interval"]["lower"] = -100.0
        cell["sensitivity_interval"]["upper"] = -50.0
        self.assertEqual(score.crps_verdict(cell), "pass")

    def test_the_integral_companion_is_reported_only_and_moves_nothing(self):
        """#259: the trapezoid-weighted sensitivity rides beside the primary cell and decides nothing."""

        cell = self._cell([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        companion = cell["integral_sensitivity"]
        self.assertEqual(companion["role"], "reported only")
        self.assertEqual(companion["interval"]["block_length"], cell["interval"]["block_length"])
        self.assertGreater(companion["mean_difference_bps"], 0)
        self.assertNotEqual(companion["crps_integral_published_bps"], cell["crps_published_bps"])
        before = (cell["verdict"], cell["result"])
        companion["interval"]["lower"] = -100.0
        companion["interval"]["upper"] = -50.0
        companion["mean_difference_bps"] = -75.0
        self.assertEqual((score.crps_verdict(cell), score.crps_result(score.crps_verdict(cell))), before)

    def test_every_other_horizon_is_reported_only(self):
        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        cells = score.score_crps(records, rows, self.splits, date(2027, 4, 1))
        self.assertEqual(sorted(cells), [f"crps/h{h}" for h in live.HORIZONS])
        for h in live.HORIZONS[1:]:
            with self.subTest(h=h):
                self.assertEqual(cells[f"crps/h{h}"]["role"], "reported only")
                self.assertNotIn("result", cells[f"crps/h{h}"])

    def test_every_later_horizon_carries_the_not_evidence_label(self):
        """Eleonora's ruling of 4 October 2026 (#229): every h = 2-5 CRPS cell is labelled.

        The label is written here verbatim, not read from the script, so a
        paraphrase in `live_score.py` fails. It sits next to the cell's verdict
        label (`verdict_label`, adjacent to `verdict` in the sorted output), on
        a scored cell and on one with no scored day alike. The h = 1 cell does
        not carry it.

        Red first: run before `live_score.py` wrote the label, this test failed
        with a `KeyError` on `verdict_label`.
        """

        label = ("different model from h = 1, and as-of persistence does not widen with "
                 "horizon, so this comparison favours the model; not evidence.")
        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        first = date.fromisoformat(records[0]["targets"][0]["target_date"])
        for name, day in (("scored", date(2027, 4, 1)), ("no scored day", first)):
            cells = score.score_crps(records, rows, self.splits, day)
            for h in live.HORIZONS[1:]:
                with self.subTest(case=name, h=h):
                    cell = cells[f"crps/h{h}"]
                    self.assertEqual(cell["verdict_label"], label)
                    # A reported-only cell cannot pass or fail, so it carries no verdict (#267).
                    self.assertNotIn("verdict", cell)
                    if name == "scored":
                        self.assertIn("served stale", cell["design"])
                    else:
                        self.assertEqual(cell["days"], 0)
            with self.subTest(case=name, h=1):
                self.assertNotIn("verdict_label", cells["crps/h1"])
                self.assertNotIn("not evidence", json.dumps(cells["crps/h1"]))

    def test_the_brier_cells_are_reported_only(self):
        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        result = score.score(records, rows, self.splits, date(2027, 4, 1))
        for name, cell in result["cells"].items():
            with self.subTest(cell=name):
                self.assertEqual(cell["role"], "reported only")

    def test_a_target_day_on_or_after_the_scoring_date_is_not_scored(self):
        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0])
        cutoff = date.fromisoformat(records[10]["targets"][0]["target_date"])
        cell = score.score_crps(records, rows, self.splits, cutoff)["crps/h1"]
        self.assertEqual(cell["days"], 10)
        self.assertLess(date.fromisoformat(cell["last"]), cutoff)


class MinimumCellSizeTests(unittest.TestCase):
    """A regime or day-type cell gets an interval by a fixed rule, not by the bootstrap (#276).

    Eleonora's ruling of 6 October 2026 (#269 item 14). A cell below
    `MINIMUM_CELL_DAYS` carries its mean and "too few days" and no interval; a
    cell at the minimum carries an interval. The number is proposed, not decided.

    Red first: run before the rule, a 5-day cell carried an interval
    (`AssertionError: 'interval' unexpectedly found`), because only a cell of
    fewer than 2 days was refused. Recorded mutation: `if len(positions) >=
    MINIMUM_CELL_DAYS:` in `_small_cell` replaced by `if len(positions) >= 2:` ->
    `AssertionError` on the 5-day cell in `test_a_cell_below_the_minimum_has_no_interval`.
    """

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)

    def _cells(self):
        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0], days=60)
        return score.score_crps(records, rows, self.splits, date(2027, 4, 1))["crps/h1"], records, rows

    def test_the_minimum_is_the_final_tests(self):
        self.assertEqual(score.MINIMUM_CELL_DAYS, 20)

    def test_a_cell_below_the_minimum_has_no_interval(self):
        cell, _, _ = self._cells()
        small = [entry for group in ("by_regime", "by_day_type") for entry in cell[group].values()
                 if entry["days"] < score.MINIMUM_CELL_DAYS]
        self.assertTrue(small, "the fixture must hold a small cell")
        for entry in small:
            with self.subTest(days=entry["days"]):
                self.assertNotIn("interval", entry)
                self.assertEqual(entry["note"], "too few days")
                self.assertEqual(entry["minimum_days"], score.MINIMUM_CELL_DAYS)
                self.assertIn("mean", entry)

    def test_a_cell_at_the_minimum_has_an_interval(self):
        cell, _, _ = self._cells()
        big = [entry for group in ("by_regime", "by_day_type") for entry in cell[group].values()
               if entry["days"] >= score.MINIMUM_CELL_DAYS]
        self.assertTrue(big, "the fixture must hold a large cell")
        for entry in big:
            self.assertIn("interval", entry)
            self.assertNotIn("note", entry)

    def test_the_rule_does_not_depend_on_the_seed(self):
        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0], days=60)
        flags = set()
        for day in (date(2027, 4, 1), date(2027, 4, 2), date(2027, 4, 3)):
            cell = score.score_crps(records, rows, self.splits, day)["crps/h1"]
            flags.add(tuple((group, key, "interval" in entry) for group in ("by_regime", "by_day_type")
                            for key, entry in sorted(cell[group].items())))
        self.assertEqual(len(flags), 1)

    def test_the_brier_cells_follow_the_same_rule(self):
        records, rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0], days=60)
        result = score.score(records, rows, self.splits, date(2027, 4, 1))
        for cell in result["cells"].values():
            for entry in cell.get("models", {}).values():
                for paired in entry["paired"].values():
                    for group in ("by_regime", "by_day_type"):
                        for part in paired[group].values():
                            self.assertEqual("interval" in part, part["days"] >= score.MINIMUM_CELL_DAYS)


class YearRegimeTests(unittest.TestCase):
    """Each calendar year from 2027 is its own regime (#276, ruling #269 item 4).

    `metadata/evaluation_splits.json` declares regimes to 2026-12-31 and is left
    as it is, so the scorer labels a later target day with its year rather than
    "undeclared". A day before 2027 that no regime covers stays "undeclared".

    Red first: before the rule, a 2027 target day was labelled "undeclared"
    (`AssertionError: 'undeclared' != '2027'`). Recorded mutation: `when.year >=
    FIRST_YEAR_REGIME` in `_regime` replaced by `False` -> the same failure.
    """

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)

    def test_a_2027_day_is_its_own_year(self):
        self.assertEqual(score._regime(self.splits, date(2027, 1, 4)), "2027")
        self.assertEqual(score._regime(self.splits, date(2028, 6, 1)), "2028")

    def test_a_declared_day_keeps_its_declared_regime(self):
        self.assertEqual(score._regime(self.splits, date(2026, 12, 31)), self.splits.regime(date(2026, 12, 31)))

    def test_an_earlier_uncovered_day_stays_undeclared(self):
        self.assertEqual(score._regime(self.splits, date(2017, 6, 1)), "undeclared")


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
                # The live panel: real rows to the day before the decision
                # day, then placeholders from the decision day on.
                live.require_reads_on_real_rows(self.rows, self._rule(h), index, index - h - 1)

    def test_an_observed_read_on_a_placeholder_is_refused(self):
        # Pretend the real rows stopped one row earlier than they do: the
        # spread the forecast reads (the day before the decision day's) then
        # sits on a "placeholder".
        index = len(self.rows) - 1
        with self.assertRaises(LookAheadError):
            live.require_reads_on_real_rows(self.rows, self._rule(1), index, index - 3)


class BaselineAgreementTests(unittest.TestCase):
    """A record's baseline forecasts are the repository's baseline functions'.

    The daily script makes its forecast on the panel as built at the decision
    day, the rows up to the day before it, extended by placeholder rows for the
    decision day and the target days. Here that is replayed on the published
    panel at a decision day before the lockbox: the panel cut at the day
    before, extended, and the script's baselines compared with the repository's
    own functions run over the uncut panel, scoring the same target day.
    """

    #: Its targets at h = 1 and h = 3 (2025-12-23, 2025-12-26) fall before the lockbox.
    DECISION_DAY = date(2025, 12, 22)

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



def _have_ml():
    """`find_spec`, not an import: `tests/test_dependency_boundary.py` forbids one here."""

    return all(importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn"))


@unittest.skipUnless(_have_ml(), "the published distribution needs the ml extra")
class DistributionAgreementTests(unittest.TestCase):
    """A record's distributions are the ones `compare` scores CRPS from.

    The final test's frozen command (`CRPS_COMMAND`: as-of persistence against
    the gbm on the nine funding features with nested conformal PID) is run by
    the repository's own `compare` on the fixture panel cut short (to keep the
    nested-PID replay quick), ending on the target day of a decision day before
    the lockbox. The daily script's distributions, made on that panel cut at
    the day before the decision day and extended by placeholders, must give
    exactly `compare`'s CRPS on that target day, on each side.
    """

    #: A Friday; its h = 1 target is Monday 2019-03-04.
    DECISION_DAY = date(2019, 3, 1)
    LAST_ROW = date(2019, 3, 15)

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        panel, cls.pit = _fixture_panel(cls.tmp)
        lines = panel.read_text(encoding="utf-8").splitlines(keepends=True)
        column = lines[0].rstrip("\r\n").split(",").index("date")
        cls.short = Path(cls.tmp) / "short.csv"
        cls.short.write_text(
            lines[0] + "".join(
                line for line in lines[1:]
                if date.fromisoformat(line.split(",")[column]) <= cls.LAST_ROW
            ),
            encoding="utf-8",
        )
        cls.rows = load_daily_panel(cls.short)
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.splits = load_split_declaration(SPLITS)
        cut = [row for row in cls.rows if row.date < cls.DECISION_DAY]
        cls.extended, cls.targets = live.extend_panel(cut, cls.DECISION_DAY, 1, cls.pit)
        cls.got = live.distribution_forecasts(cls.extended, 1, cls.registry, cls.splits)
        final = _script("final_test_preregistration")
        argv = [str(cls.short) if part == "PUB.csv" else part for part in final.CRPS_COMMAND]
        argv[argv.index("--end") + 1] = cls.targets[0].isoformat()
        argv[argv.index("--report") + 1] = str(Path(cls.tmp) / "compare.json")
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli_main(argv)
        if code != 0:
            raise RuntimeError("compare did not run")
        cls.compare = json.loads((Path(cls.tmp) / "compare.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_each_side_gives_compares_crps_on_the_target_day(self):
        from repo_model.metrics import crps_from_quantiles

        last = self.compare["comparison"]["per_origin"][-1]
        self.assertEqual(last["scored_date"], self.targets[0].isoformat())
        actual = {row.date: row for row in self.rows}[self.targets[0]].spread_bps
        for side, key in (("persistence", "loss_a_bps"), ("published", "loss_b_bps")):
            with self.subTest(side=side):
                crps = crps_from_quantiles(self.got["levels"], self.got[side], actual)
                self.assertAlmostEqual(crps, float(last[key]), places=9)

    def test_the_placeholders_spread_never_reaches_the_distribution(self):
        moved = []
        for row in self.extended:
            if row.date >= self.DECISION_DAY:
                values = dict(row.values)
                values["sofr"] = float(values["sofr"]) + 0.37
                row = type(row)(date=row.date, values=values)
            moved.append(row)
        again = live.distribution_forecasts(moved, 1, self.registry, self.splits)
        for side in ("published", "persistence"):
            with self.subTest(side=side):
                self.assertEqual(again[side], self.got[side])

    def test_the_distribution_is_the_published_records(self):
        self.assertEqual(self.got["declaration_sha256"], live.published_declaration_sha256(1))
        self.assertEqual(tuple(self.got["levels"]), live.QUANTILE_LEVELS)


class PublishedDistributionDeclarationTests(unittest.TestCase):
    """At each horizon the published distribution is a declaration #169 published.

    At h = 1 it is the CRPS record's (the final test's frozen `compare`). At
    h = 2 to 5 that declaration would read a Treasury settlement not yet
    scheduled at the decision, which the as-of rule refuses (`LookAheadError`);
    there it is pressure model v1's published declaration at that horizon: the
    same gbm and nested PID, without the settlement read (`_at_horizon`).
    """

    def test_horizon_one_is_the_crps_record(self):
        self.assertEqual(live.published_distribution_record(1), live.CRPS_RECORD)
        self.assertEqual(live.published_features(1), tuple(live.CRPS_FEATURES))

    def test_later_horizons_are_v1s_published_declarations(self):
        for h in live.HORIZONS[1:]:
            with self.subTest(h=h):
                path = live.published_distribution_record(h)
                self.assertEqual(path, f"docs/runs/pressure_model_v1_h{h}.json")
                declared = json.loads((ROOT / path).read_text(encoding="utf-8"))["declaration"]
                self.assertEqual(sorted(live.published_features(h)), sorted(declared["features"]))
                self.assertNotIn("treasury_settlement", live.published_features(h))

    def test_the_command_side_reads_the_horizons_features(self):
        for h in live.HORIZONS:
            with self.subTest(h=h):
                sides, _args = live._compare_sides(h)
                self.assertEqual(sides["published"][2], live.published_features(h))
                self.assertEqual(sides["persistence"][2], ("spread_bps",))


if __name__ == "__main__":
    unittest.main()
