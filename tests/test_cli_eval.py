"""Tests for `repo_model.cli_eval`, and for the `event-holdout` subcommand.

The subcommand is a *caller*, and almost everything worth asserting about a
caller is which declaration it obeys and which one it is tempted to restate.
`AGENT_CONTRACT.md` fixes three numbers this command needs and puts none of them
here: the window boundaries (`metadata/events.json`, Track A's), the tau family
(`metadata/stress_thresholds.json`, Track A's), and the purge gap (a function of
the feature sources, via `registry.max_release_lag_days`). A command that
defaulted any of those paths, or carried any of those values as a literal, would
be model-eval deciding something it does not own -- the boundaries-as-constants
failure the contract names, relocated from an evaluator into a CLI.

So the guards here are mostly about absences, and absences need mutations to
mean anything. See the mutation record below.

The model these fixtures run is `baseline.climatology_exceedance`, and it is the
honest one for a knowledge holdout: the question the window asks is what a model
that saw only calm history says about a crisis it was never shown. Since the
holdout-model-selector block it is *chosen* rather than assumed -- `--model` is
required and has no default, because a default would be this model and this
model is the reference a skill score is measured against. `ModelSelectorTests`
carries that reasoning and its mutation record; the fixtures here pass
`--model climatology` explicitly and the numbers they pin are unchanged. On the fixture panel --
fifty flat days, then a spike inside the window -- the answer is a curve of
zeros beside a realized path in the tens of basis points. That is not a bug in
the fixture. It is the extrapolation check producing its most informative
result, and `test_a_climatology_that_never_saw_the_event_reports_zeros` pins it
so that a later predictor which quietly smooths the zero away has to say so.

Mutation record
---------------

Four leaks planted, each the smallest change that reopens the hole its guard
closes. All stdlib only, run under `-B` with `PYTHONDONTWRITEBYTECODE=1` against
a copy of the tree with `__pycache__` cleared and an unmutated control run
first. `data/` and `.github/` were copied along with `src/`, `tests/` and
`metadata/`: a copy missing `data/` fails fourteen unrelated tests that look
like kills and are not, and one missing `.github/` errors the ownership
tripwire the same way.

  * **A `--purge` argument added, winning over the registry** when supplied. The
    shape a hurry takes: the training set that cleared a six-day gap came back
    too short, and the flag is right there. Fails 1 --
    `test_the_subcommand_offers_no_purge_argument`. Only one, and that is worth
    saying plainly: no behavioural test can catch this, because a flag nobody
    passes changes no output. An absence is only guarded by a test that asserts
    the absence, which is why this one reads the parser rather than the result.

  * **The tau family hard-coded** as the declared four in `_event_holdout`
    instead of read from `--thresholds`. Fails 2:
    `test_the_tau_family_carries_no_literal_in_this_module` on the source, and
    `test_a_thresholds_file_declaring_other_taus_is_refused` on behaviour --
    the second is the one worth having, because it fails on the command
    *accepting a file it should have rejected* rather than on how the module is
    spelled. Note the two together: the literal happens to be correct today, so
    a suite that only compared outputs would stay green while the declaration
    stopped being load-bearing.

  * **`load_events_file` swapped for `load_event_windows(json.loads(...))`**,
    which is the plausible mistake rather than a contrived one: it parses the
    same file and still verifies every digest, so the checksum tests stay green.
    Fails 1 -- `test_an_events_file_without_a_version_is_refused`. A bare list
    and an unversioned document both get through, and the version is the thing
    that says *which* declaration was scored. The digest guard cannot see it,
    which is precisely why the document validator exists alongside it.

  * **The handler moved into the human-owned dispatcher** -- `_orphan` defined
    in `cli.py` and registered from here -- for
    `test_contract.CommandLineOwnershipTests`'s new
    `test_every_registered_command_comes_from_a_track_module`. Fails that test
    by name, plus most of this file, since the command then does nothing.

    **The first version of this mutation did not bite, and the reason is worth
    recording.** It attached a `lambda` to the `cli` module and registered that,
    which *looks* like a handler living in the dispatcher and is not: a
    function's `__module__` is where it was defined, not where it was bound, so
    the lambda still reported `repo_model.cli_eval` and the guard stayed silent
    while every behavioural test failed around it. A mutation that kills a lot
    of tests is not evidence that it killed the one it was aimed at -- check the
    named test appears in the output, not merely that the run went red.

Not a mutation, but recorded here because it is a change to a `SHARED` file:
`test_contract.CommandLineOwnershipTests.test_the_split_preserved_the_three_existing_subcommands`
asserted set *equality* over the registered commands, so it failed the moment a
fourth was added -- a test named for preservation blocking the growth the seam
exists to enable. Loosened to a subset, with the half of the equality worth
keeping (that no command arrives from outside a track-owned module) promoted to
its own test over *every* command rather than by counting three. That is
stronger as commands accumulate, and it is the assertion the fourth mutation
above is aimed at. `tests/test_contract.py` is `SHARED`, so the gate permits the
edit and surfaces it for review, which is the right handling for it.

No mutation was planted in the report shaping or the journal path; those are
`event_eval`'s and are recorded in `tests/test_event_eval.py`.
"""

import contextlib
import csv
import hashlib
import inspect
import io
import json
import math
import re
import sys
import tempfile
import unittest
import unittest.mock
from datetime import date, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import baseline, cli, cli_eval
from repo_model.baseline import (
    BacktestReport,
    Forecast,
    backtest_document,
    rolling_persistence_backtest,
)
from repo_model.contract import (
    QUANTILE_LEVELS,
    event_window_digest,
    sources_for_features,
)
from repo_model.data import load_daily_panel
from repo_model.metrics import (
    crps_from_quantiles,
    pinball_loss,
    stationary_bootstrap_interval,
)
from repo_model.registry import max_release_lag_days
from repo_model.event_eval import config_digest, read_journal


REPO_ROOT = Path(__file__).parents[1]
THRESHOLDS = REPO_ROOT / "metadata" / "stress_thresholds.json"
REGISTRY = REPO_ROOT / "metadata" / "sources.json"

PANEL_COLUMNS = (
    "date", "sofr", "iorb", "sofr_volume", "sofr_p25", "sofr_p75", "tgcr",
    "bgcr", "reserve_balances", "tga", "on_rrp", "treasury_settlement",
    "dealer_treasury_position", "mmf_assets", "quarter_end", "tax_date",
)

#: A source whose `release_lag` is declared in `metadata/sources.json`. Named
#: rather than computed because naming the sources is how a caller sets the gap;
#: the *number* it produces is never written down here.
#: What a caller declares now. `--source` is gone: sources are derived from the
#: feature set, and the gap from the sources. `spread_bps` is what both
#: evaluation paths actually read -- persistence forecasts it and climatology
#: scores exceedances of it -- so it is the honest declaration for both.
FEATURE = "spread_bps"
DECISION_TIME = "16:30"


def declared_registry_file(directory, purge=6, features=(FEATURE,)):
    """Write a registry that prices the sources `features` uses at `purge` days.

    A fixture, and the commands need one because these tests pin *numbers*.
    The real `metadata/sources.json` now prices `spread_bps` -- since the gap
    is sized per field and `fred_macro_latest_vintage.IORB` declares its own
    lag -- so a run against it is no longer refused; `RealRegistryTests` covers
    that run and the field that is still refused beside it. What the real file
    cannot give these tests is a gap they chose, and a test about ordering or
    interval width needs one. So the other tests declare their own registry,
    exactly as they already declare their own panel, events file and
    thresholds.

    It declares **no** `field_release_lags`, deliberately. Every number pinned
    against it is therefore blind to whether the gap was sized over sources or
    over fields, which is what makes those numbers the control: the
    field-priced-purge block changes where the gap comes from, and on this
    registry nothing downstream of the gap may move.
    """

    from repo_model.contract import sources_for_features

    path = Path(directory) / "registry.json"
    path.write_text(
        json.dumps(
            {
                source: {
                    "release_lag": {
                        "basis": "record_date",
                        "unit": "calendar_days",
                        "days": purge,
                        "available_time": "00:00",
                        "timezone": "America/New_York",
                    }
                }
                for source in sources_for_features(features)
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def business_days(start, count):
    days, cursor = [], start
    while len(days) < count:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


class EventHoldoutHarness(unittest.TestCase):
    """A panel that is calm for fifty days and then is not, and a window on it."""

    CALM_BPS = 3.0
    EVENT_BPS = 35.0

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.journal = self.tmp / "journal.jsonl"

        self.registry = declared_registry_file(self.tmp)
        self.days = business_days(date(2025, 11, 3), 60)
        self.window_start, self.window_end = self.days[52], self.days[56]
        self.panel = self.write_panel()
        self.events = self.write_events()

    def write_panel(self, path=None):
        path = path or self.tmp / "panel.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(PANEL_COLUMNS)
            for index, when in enumerate(self.days):
                stressed = self.window_start <= when <= self.window_end
                spread = self.EVENT_BPS if stressed else self.CALM_BPS
                writer.writerow(
                    [when.isoformat(), round(4.30 + spread / 100.0, 6), 4.30,
                     2100, 4.30, 4.32, 4.30, 4.31, 3200, 720, 115, "", "", "", 0, 0]
                )
        return path

    def window_entry(self, name="smoke-window", start=None, end=None, checksum=None):
        start = (start or self.window_start).isoformat() if not isinstance(start, str) else start
        end = (end or self.window_end).isoformat() if not isinstance(end, str) else end
        return {
            "name": name,
            "start": start,
            "end": end,
            "checksum": checksum or event_window_digest(name, start, end),
        }

    def write_events(self, document=None, path=None):
        path = path or self.tmp / "events.json"
        if document is None:
            document = {"version": 1, "windows": [self.window_entry()]}
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")
        return path

    #: What this harness runs when a test does not say. The climatology is the
    #: honest model for a knowledge holdout -- the question the window asks is
    #: what a model that saw only calm history says about a crisis it was never
    #: shown -- and it is what every test here scored before `--model` existed,
    #: so the numbers they pin are unchanged.
    #:
    #: **It is passed explicitly, not defaulted by the command.** That is the
    #: whole point of the flag: a default that is the comparison baseline is
    #: how a run meaning to score a conditional model publishes the baseline's
    #: numbers under that model's name. The fixture chooses; the CLI does not.
    MODEL = "climatology"

    def run_command(self, *extra, events=None, thresholds=None, journal=None,
                    model=None, features=None):
        """Invoke the real dispatcher. Returns `(exit_code, stdout, stderr)`."""

        argv = [
            "event-holdout",
            "--panel", str(self.panel),
            "--events", str(events or self.events),
            "--thresholds", str(thresholds or THRESHOLDS),
            "--registry", str(self.registry),
            "--journal", str(journal or self.journal),
            "--decision-time", DECISION_TIME,
        ]
        for feature in (features if features is not None else (FEATURE,)):
            argv += ["--feature", feature]
        if model is not False:
            argv += ["--model", model or self.MODEL]
        argv += [*extra]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue(), err.getvalue()

    def scored(self, *extra, **kwargs):
        code, out, err = self.run_command(*extra, **kwargs)
        self.assertEqual(code, 0, msg=f"command failed: {err.strip()}")
        return json.loads(out)


class EventHoldoutReportTests(EventHoldoutHarness):
    """What the command scores, and what it reports having scored."""

    def test_a_declared_window_is_scored_and_its_realized_path_reported(self):
        report = self.scored()
        self.assertEqual(len(report), 1)
        entry = report[0]
        self.assertEqual(entry["window"]["name"], "smoke-window")
        self.assertEqual(entry["window"]["start"], self.window_start.isoformat())
        self.assertEqual(entry["holdout_role"], "knowledge")

        scored_days = [day["date"] for day in entry["days"]]
        expected = [
            when.isoformat()
            for when in self.days
            if self.window_start <= when <= self.window_end
        ]
        self.assertEqual(scored_days, expected)
        for day in entry["days"]:
            self.assertAlmostEqual(day["realized_bps"], self.EVENT_BPS, places=6)

    def test_training_stops_clear_of_the_purge_gap_the_registry_sized(self):
        """The gap is the registry's number, and the boundary is strict.

        The purge is not asserted as a literal -- that would be this file
        restating `metadata/sources.json`. What is asserted is the relation the
        contract states: the last training row plus the reported gap still falls
        before the window opens.
        """

        entry = self.scored()[0]
        gap = entry["purge_days"]
        self.assertGreater(gap, 0)
        last_train = date.fromisoformat(entry["last_train_date"])
        self.assertLess(last_train + timedelta(days=gap), self.window_start)
        self.assertEqual(entry["train_rows"], sum(1 for d in self.days if d <= last_train))

    def test_a_climatology_that_never_saw_the_event_reports_zeros(self):
        """The extrapolation check producing its most informative answer.

        Fifty calm days put no weight above 5bp, and the window realizes 35.
        Pinned so that a later predictor which smooths the zero into a small
        number has to change this test and say why: a `1/(n+2)` here would turn
        "put no weight where it went" into "forecast it poorly", which are
        different findings.
        """

        entry = self.scored()[0]
        for day in entry["days"]:
            self.assertEqual(day["exceedance"], [0.0, 0.0, 0.0, 0.0])
            self.assertGreater(day["realized_bps"], entry["taus_bp"][0])

    def test_the_exceedance_curve_never_rises_with_tau(self):
        for day in self.scored()[0]["days"]:
            curve = day["exceedance"]
            self.assertEqual(curve, sorted(curve, reverse=True))

    def test_no_aggregate_number_is_reported(self):
        """`AGENT_CONTRACT.md`, "Metrics": the curve and the path, nothing else.

        Ten stressed days cannot support a calibration statistic, and one
        printed beside a scoring-holdout number gets averaged into the main
        table by whoever reads the two as the same kind of thing.
        """

        code, out, _ = self.run_command()
        self.assertEqual(code, 0)
        rendered = out.lower()
        for forbidden in ("brier", "skill", "reliability", "mae", "coverage", "auc"):
            self.assertNotIn(forbidden, rendered)


class DeclarationTests(EventHoldoutHarness):
    """Every number somebody else declared is read, not restated."""

    def test_the_subcommand_offers_no_purge_argument(self):
        """The absence is the guard, so the test reads the parser.

        A flag setting the gap by hand would be reached for at exactly the
        moment it must not be: when the training set that cleared it came back
        too short. The gap follows from the sources, and the sources follow from
        the declared feature set, so `--feature` is how a caller changes it and
        that change is legible.
        """

        parser = cli.build_parser()
        options = self._holdout_options(parser)
        for banned in ("--purge", "--purge-days", "--gap", "--source"):
            self.assertNotIn(banned, options, msg=f"{banned} is back")
        self.assertIn("--feature", options)

    def test_no_path_this_command_reads_carries_a_default(self):
        parser = self._holdout_parser(cli.build_parser())
        for action in parser._actions:
            if action.dest in ("panel", "events", "thresholds", "registry", "journal"):
                self.assertTrue(
                    action.required,
                    msg=f"--{action.dest} became optional; the path is the caller's",
                )
                self.assertIsNone(action.default, msg=f"--{action.dest} acquired a default")

    def test_the_tau_family_carries_no_literal_in_this_module(self):
        source = inspect.getsource(cli_eval)
        found = re.findall(r"\b(?:5|10|20|50)\.0\b", source)
        self.assertEqual(
            found, [], msg=f"tau literals in cli_eval: {found}; they are declared, not ours"
        )

    def test_the_reported_taus_are_the_declared_ones(self):
        declared = json.loads(THRESHOLDS.read_text(encoding="utf-8"))["taus_bp"]
        self.assertEqual(self.scored()[0]["taus_bp"], declared)

    def test_a_thresholds_file_declaring_other_taus_is_refused(self):
        """The behavioural half: the file is read and validated, not decorative."""

        declaration = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
        declaration["taus_bp"] = [5.0, 10.0, 20.0, 40.0]
        other = self.tmp / "thresholds.json"
        other.write_text(json.dumps(declaration), encoding="utf-8")

        code, _, err = self.run_command(thresholds=other)
        self.assertEqual(code, 2)
        self.assertIn("stress thresholds", err.lower())
        self.assertEqual(read_journal(self.journal), ())

    def _holdout_parser(self, parser):
        action = next(a for a in parser._actions if a.dest == "command")
        return action.choices["event-holdout"]

    def _holdout_options(self, parser):
        return {
            option
            for action in self._holdout_parser(parser)._actions
            for option in action.option_strings
        }


class DeclaredWindowTests(EventHoldoutHarness):
    """A window that cannot be shown to be the declared one is never scored."""

    def test_an_events_file_whose_digest_does_not_match_is_refused(self):
        """The edge moved and the digest did not. Nothing is scored, nothing journalled."""

        entry = self.window_entry()
        entry["start"] = self.days[51].isoformat()  # boundary moved, checksum stale
        bad = self.write_events(
            {"version": 1, "windows": [entry]}, path=self.tmp / "bad.json"
        )
        code, _, err = self.run_command(events=bad)
        self.assertEqual(code, 2)
        self.assertIn("does not match its boundaries", err)
        self.assertEqual(read_journal(self.journal), ())

    def test_an_events_file_without_a_version_is_refused(self):
        """What the digest guard cannot see.

        Every checksum in this document verifies. What is missing is the thing
        that says *which* declaration was scored, and a journal line naming a
        window from an unversioned file records less than it appears to. This is
        the assertion that separates `load_events_file` from
        `load_event_windows` on a decoded payload -- the latter would take it.
        """

        unversioned = self.write_events(
            {"windows": [self.window_entry()]}, path=self.tmp / "unversioned.json"
        )
        code, _, err = self.run_command(events=unversioned)
        self.assertEqual(code, 2)
        self.assertIn("version", err)
        self.assertEqual(read_journal(self.journal), ())

    def test_naming_an_undeclared_window_is_refused_and_names_what_is_declared(self):
        code, _, err = self.run_command("--window", "mar-2020")
        self.assertEqual(code, 2)
        self.assertIn("mar-2020", err)
        self.assertIn("smoke-window", err)
        self.assertEqual(read_journal(self.journal), ())

    def test_selecting_one_of_several_declared_windows_scores_only_that_one(self):
        second_start, second_end = self.days[20], self.days[24]
        document = {
            "version": 1,
            "windows": [
                self.window_entry(
                    name="early-window",
                    start=second_start.isoformat(),
                    end=second_end.isoformat(),
                ),
                self.window_entry(),
            ],
        }
        both = self.write_events(document, path=self.tmp / "two.json")
        report = self.scored("--window", "smoke-window", events=both)
        self.assertEqual([e["window"]["name"] for e in report], ["smoke-window"])


class JournalTests(EventHoldoutHarness):
    """Run-once discipline is recorded, not enforced here."""

    def test_each_scored_window_appends_exactly_one_record(self):
        self.scored()
        entries = read_journal(self.journal)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["window_name"], "smoke-window")
        self.assertEqual(entries[0]["holdout_role"], "knowledge")

    def test_a_rerun_appends_a_second_record_rather_than_being_blocked(self):
        """The command does not invent an authorisation rule it was not given.

        `event_eval`'s docstring is explicit that whether a second run was
        permitted is a question for the human reading the journal. A CLI that
        refused the second run would be answering it.
        """

        self.scored()
        self.scored()
        entries = read_journal(self.journal)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["window_checksum"], entries[1]["window_checksum"])

    def test_the_record_carries_the_checksum_the_file_declared(self):
        self.scored()
        declared = json.loads(self.events.read_text(encoding="utf-8"))
        self.assertEqual(
            read_journal(self.journal)[0]["window_checksum"],
            declared["windows"][0]["checksum"],
        )


class ConditionalModelHarness(EventHoldoutHarness):
    """A panel a conditional model can actually be fitted on.

    `EventHoldoutHarness`' panel is fifty flat days and then a spike, which is
    the right fixture for the climatology and an impossible one for an ARX: a
    constant spread makes the lagged target collinear with the intercept and
    `fit_arx` refuses the design as singular. So this widens the fixture rather
    than the models -- the spread and the covariate both move, on different
    frequencies, and a third column carries a regime.

    The declaration is `spread_bps` and `on_rrp`, plus `tgcr` where a regime is
    read. All three are declared through `--feature`, which is what sizes the
    purge and what `evaluate_event_window` checks the predictor's
    `features_read` against; the regressors are what the selector takes out of
    that set, never a second list beside it.
    """

    #: Declared for every run here, so two runs differ only in `--model`.
    #: `on_rrp` is the exogenous regressor; `spread_bps` is declared because
    #: every model reads it and is *not* a regressor, because the fitter
    #: supplies it as the autoregressive term.
    FEATURES = (FEATURE, "on_rrp")

    #: `tgcr` resolves to `nyfed_tgcr`, a source neither `spread_bps` nor
    #: `on_rrp` draws on, so declaring it widens the source set rather than
    #: only the feature list -- the same reason `tests/test_event_eval.py`
    #: reads its regime off that column.
    REGIME_VARIABLE = "tgcr"
    REGIME_FEATURES = FEATURES + (REGIME_VARIABLE,)

    #: Passed explicitly on every invocation rather than left to the parser's
    #: default, so the expected `model_config` this file rebuilds carries a
    #: number the test supplied instead of one it transcribed from argparse.
    MINIMUM_HISTORY = 25

    def setUp(self):
        super().setUp()
        # Wide enough to price every source the three declarations resolve to.
        # The panel is this class's; the registry is the base fixture's shape.
        self.registry = declared_registry_file(
            self.tmp, features=self.REGIME_FEATURES
        )

    def write_panel(self, path=None):
        """The base panel with a moving spread, covariate and regime column.

        Nothing is random. The spread carries a trend and a cycle so the lagged
        target identifies a coefficient; `on_rrp` cycles at a different rate so
        it is not collinear with it; `tgcr` moves through a band wide enough
        that the training rows fall on both sides of a fitted cutoff. Inside the
        window the spread is the base fixture's event level, so the realized
        path is still a crisis the training set never saw.
        """

        path = path or self.tmp / "panel.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(PANEL_COLUMNS)
            state = 20260908
            for index, when in enumerate(self.days):
                state = (1103515245 * state + 12345) % (2 ** 31)
                stressed = self.window_start <= when <= self.window_end
                spread = (
                    self.EVENT_BPS
                    if stressed
                    else 8.0 + 4.0 * math.sin(index * 0.9) + 0.1 * index
                )
                on_rrp = 300.0 + 50.0 * math.cos(index * 0.41)
                tgcr = 4.28 + (state % 97) / 1000.0
                writer.writerow(
                    [when.isoformat(), round(4.30 + spread / 100.0, 6), 4.30,
                     2100, 4.30, 4.32, round(tgcr, 6),
                     4.31, 3200, 720, round(on_rrp, 6), "", "", "", 0, 0]
                )
        return path

    def run_command(self, *extra, features=None, **kwargs):
        return super().run_command(
            "--minimum-history", str(self.MINIMUM_HISTORY),
            *extra,
            features=self.FEATURES if features is None else features,
            **kwargs,
        )

    def expected_config(self, model, features, regime_variable=None):
        """The `model_config` a run under this declaration must hash.

        Rebuilt from the declarations rather than copied from a run: the taus
        come out of the thresholds file, the sources out of
        `contract.sources_for_features`, and the model name is the string this
        test passed on the command line. Nothing here is read back from the
        command under test, which is what makes the digest comparison a claim
        about what the command recorded.
        """

        config = {
            "model": model,
            "minimum_history": self.MINIMUM_HISTORY,
            "taus_bp": list(
                json.loads(THRESHOLDS.read_text(encoding="utf-8"))["taus_bp"]
            ),
            "features": sorted(features),
            "sources": sorted(sources_for_features(features)),
        }
        if regime_variable is not None:
            config["regime_variable"] = regime_variable
        return config


class ModelSelectorTests(ConditionalModelHarness):
    """Which exceedance predictor ran, and whether the record says so.

    `baseline` has three implementers of `ExceedancePredictor`. Until this block
    `_event_holdout` constructed one of them unconditionally --
    `climatology_exceedance`, the **unconditional** predictor, which is the
    reference a skill score is measured *against*. So the only exceedance
    predictor reachable from outside the test suite was the null model;
    `arx_exceedance` and `threshold_exceedance` existed only where a test built
    them, and `PLAN.md`'s Phase 2 exit criterion -- a conditional model scored
    against climatology -- had no path at all.

    Why `--model` is required rather than defaulted
    ===============================================

    Because the default a convenience would pick is the climatology, and the
    climatology is the baseline the comparison is against. `AGENT_CONTRACT.md`,
    "Metrics": "Brier skill score against climatology". A run meaning to score
    the ARX, launched with the flag forgotten or misspelled, would then fit the
    climatology, produce real curves, append a real journal record, and hash a
    `model_config` with the word `climatology` in it -- and a reader comparing
    that record to the ARX's would be comparing the baseline to itself. Every
    number in it is correct. The only thing wrong is which model produced them,
    and nothing in the artifact disagrees.

    `--events` and `--thresholds` are already required with the reasoning "no
    default, it is not ours to name". This is the same argument about a
    different kind of choice, and it is why the selector **refuses** an unknown
    name rather than falling back: a fallback is a default that arrives at the
    moment a caller has most reason to believe they chose something else.

    **No aggregate is computed here**, and none may be. The contract gives event
    windows the exceedance curve and the realized path and forbids an aggregate
    Brier or reliability number on a single window. This block makes conditional
    models runnable and their runs correctly recorded, and stops there.

    Mutation record
    ===============

    Unmutated control first, green before and after every run below -- OK, zero
    `expectedFailure`. Stdlib only, run from a copy under `$HOME` rather than
    the mount, carrying `data/`, `.github/`, `metadata/`, `.gitignore`, the root
    Markdown and `docs/PROJECT_STATUS.md`, because `tests/test_docs_freshness.py`
    reads those and their absence is kills that look real and are not. `-B` with
    `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` cleared before each run.

    1. **`model_config["model"]` restored to the literal `"climatology"`** while
       the selector stays wired to the factory. The command still runs, still
       selects the ARX, still produces ARX curves, still writes a journal
       record; only the record's name for what ran is the old constant.
       **2 tests fail, both `AssertionError`:**

       * `test_the_journal_names_the_model_that_produced_the_curves` -- the
         acceptance criterion, on the rebuilt digest: the ARX run's
         `config_sha256` is the climatology's. **Criterion and mutation target,
         and they did not come apart.**
       * `test_a_threshold_run_declares_its_regime_variable_and_is_recorded` --
         the same failure on the third model, which is worth having because it
         says the mutation is about the field and not about one name.

       Nothing else in the suite sees it. That is the finding, not a weakness:
       the curves, the gap, the train rows, the realized path and the digest's
       every other component are all still right, so no assertion about *what
       was scored* can tell. Only an assertion about what the record *claims*
       can, and it has to know what an honest record would hash to -- which is
       why `expected_config` rebuilds it from the declarations rather than
       reading it back off the command.

    2. **An unknown `--model` resolving to the climatology instead of raising.**
       `MODEL_FACTORIES.get(name)` became
       `MODEL_FACTORIES.get(name, MODEL_FACTORIES["climatology"])` with the
       refusal branch made unreachable. **1 test fails:**

       * `test_the_journal_names_the_model_that_produced_the_curves` --
         `AssertionError: 0 != 2`. `--model arxx` runs to completion and is
         journalled. The refusal half of the criterion is exercised, which is
         what this mutation was run to find out.

    3. **The regime variable admitted when it is not in `--feature`.** The
       membership check made unreachable, so `--model threshold
       --regime-variable tgcr` with `tgcr` undeclared reaches the fitter.
       **1 test fails:**

       * `test_the_regime_variable_must_be_one_of_the_declared_features` --
         `AssertionError: '--regime-variable' not found in ...`, the message
         being `9484e99`'s `LookAheadError` from
         `baseline._check_fitter_stayed_inside`: "the fitted model reads
         ['tgcr'], which the declared feature set ['spread_bps', 'on_rrp'] does
         not contain."

       **The two guards fire on this, and the interesting half is how nearly
       indistinguishable they are.** The downstream one gives the same exit
       code, the same empty stdout and the same empty journal as the argument
       check. Run with the message assertions stripped out, this mutation
       **killed nothing at all** -- verified, not assumed. So the test was
       strengthened rather than left resting on wording: it now also runs the
       same refusal with `--panel` pointing at a file that does not exist. An
       argument-level refusal does not need a panel; a guard inside the
       evaluator cannot be reached without reading one. With that assertion in
       place the mutation fails on
       `AssertionError: 'no-such-panel.csv' unexpectedly found in ...` even with
       every message check removed, which is the structural distinction the
       wording was standing in for.

    4. **The boring one, and it was boring.** No mutation: the claim is that
       `--model climatology` reproduces the command as it stood with no flag at
       all. The same fixture -- fifty calm days, a spike in the window, a
       six-day registry, the declared thresholds file -- was run against a
       pristine `git archive HEAD` checkout without the flag and against the
       working tree with `--model climatology`. The exceedance curves, the
       realized path, the feature dates, the journal record (every field but
       `evaluated_at` and `git_rev`, which are a timestamp and a checkout) and
       `config_sha256` are **byte-identical**: `ec0a01a3...f608f` both times.
       **0 tests fail.** Every existing journal record stays readable as a
       comparison.

       The one difference, and it is in the console report rather than in any
       of the four: the per-window entry gains a `"model"` key. Diffed in full,
       that is the whole change -- one added line. It is added for the reason
       `features` and `sources` are reported there: a reader of stdout should
       not have to open the journal to see which model produced the curves, and
       here they could not, because the journal carries the *hash* of
       `model_config` and not `model_config` itself.

    The discovery guard was extended, not duplicated
    ================================================

    `tests/test_baseline.py::ExceedancePredictorCoverageTests` already discovers
    every `ExceedancePredictor` in `baseline` by its return annotation and
    asserts the covered set equals the discovered set. It gained one assertion
    over that same set -- every implementer is reachable by name from
    `cli_eval.MODEL_FACTORIES`, by factory identity rather than by key
    spelling -- so a fourth implementer the command line cannot run fails an
    existing guard. No second guard was added beside it; the cover sheet for
    this block is explicit that the discovery-guard gap is closed and that the
    one that exists is the one to extend.
    """

    def test_the_journal_names_the_model_that_produced_the_curves(self):
        """The acceptance criterion, and the mutation target.

        Two runs of one window under one declaration, differing only in
        `--model`. The curves must differ, because the models differ -- and the
        journal must be able to tell which run was which, which it can only do
        through `config_sha256`, since the record carries the hash of
        `model_config` and not `model_config` itself.

        That is why the digest is rebuilt here from the declarations rather than
        read back off the command. A run that selected the ARX and recorded
        `"model": "climatology"` still fits, still produces ARX curves, still
        appends a record, still hashes to something -- and every field in that
        record is correct except the one naming what ran. Nothing in the
        artifact disagrees with itself, so the only assertion that can see it is
        one that knows what the digest of an honest record would be.

        The refusal is the other half, and it is here rather than in its own
        test because it is the same claim: a `--model` the mapping does not know
        must not resolve to anything. A fallback to the climatology would run to
        completion and write a record whose every number is right, which is the
        same failure arriving by a different route.
        """

        arx = self.scored(model="arx")[0]
        climatology = self.scored(model="climatology")[0]

        # Both scored the same window, over the same declaration and the same
        # gap, so nothing but the model can account for a difference.
        self.assertEqual(arx["window"], climatology["window"])
        self.assertEqual(arx["features"], climatology["features"])
        self.assertEqual(arx["purge_days"], climatology["purge_days"])
        self.assertEqual(arx["train_rows"], climatology["train_rows"])
        self.assertEqual(arx["model"], "arx")
        self.assertEqual(climatology["model"], "climatology")

        arx_curves = [day["exceedance"] for day in arx["days"]]
        flat_curves = [day["exceedance"] for day in climatology["days"]]
        self.assertNotEqual(
            arx_curves,
            flat_curves,
            msg="the two models produced identical curves; the selector is "
            "constructing one predictor under both names",
        )
        # And the ARX conditioned on something: its curve moves across scored
        # days, which the climatology's cannot. Without this the assertion
        # above would also hold for a second unconditional predictor.
        self.assertGreater(len(set(map(tuple, arx_curves))), 1)
        self.assertEqual(len(set(map(tuple, flat_curves))), 1)

        first, second = read_journal(self.journal)
        self.assertEqual(
            first["config_sha256"],
            config_digest(self.expected_config("arx", self.FEATURES)),
            msg="the record for the ARX run does not hash the config an ARX "
            "run produces; the name in model_config is not the selected one",
        )
        self.assertEqual(
            second["config_sha256"],
            config_digest(self.expected_config("climatology", self.FEATURES)),
        )
        # The two runs are distinguishable in the journal at all. A literal
        # model name makes these equal, and then a reader comparing the two
        # records is comparing the baseline to itself.
        self.assertNotEqual(first["config_sha256"], second["config_sha256"])

        # An unrecognised name is refused, naming the value and the names that
        # exist, and nothing is appended for the refused run.
        code, out, err = self.run_command(model="arxx")
        self.assertEqual(code, 2)
        self.assertIn("arxx", err)
        for known in ("climatology", "arx", "threshold"):
            self.assertIn(known, err)
        self.assertEqual(out, "", msg="the refused run scored something first")
        self.assertEqual(len(read_journal(self.journal)), 2)

    def test_the_model_flag_is_required_and_carries_no_default(self):
        """A default here is the null model, so there is no default.

        `climatology_exceedance` is the reference a skill score is measured
        against. A `--model` that defaulted to it would let a run meaning to
        score a conditional model publish the baseline's numbers under that
        model's name, in a journal record whose every other field is correct --
        which is worse than an unrecorded scoring, because it is recorded.

        The absence is the guard, so the test reads the parser: no invocation
        exercises a default nobody passes.
        """

        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        holdout = command.choices["event-holdout"]
        model = next(a for a in holdout._actions if a.dest == "model")
        self.assertTrue(model.required)
        self.assertIsNone(model.default)

        # And omitting it is argparse's refusal, which exits rather than
        # returning: the command cannot be reached without naming a model.
        with self.assertRaises(SystemExit) as raised:
            self.run_command(model=False)
        self.assertEqual(raised.exception.code, 2)
        self.assertEqual(read_journal(self.journal), ())

    def test_the_regime_variable_must_be_one_of_the_declared_features(self):
        """Refused by argument handling, naming the column, before any fold.

        `event_eval` would also catch this: a threshold model reports its regime
        variable in `features_read`, and `_check_fitter_stayed_inside` raises
        `LookAheadError` when that exceeds the declaration. That guard is
        correct and stays. But a CLI that leans on a downstream guard to
        validate its own arguments stops validating them the moment the call
        site moves, and the message a caller should get names the flag they
        typed rather than a fitted model they never held.

        So the refusal arrives before the panel is read, and the two are
        distinguishable. **Both halves of that are asserted, and the second one
        is here because the first is not enough.** Removing this guard leaves
        the downstream one firing with the same exit code, the same empty
        stdout and the same empty journal -- verified, and recorded in the
        mutation record on this class -- so the only thing separating them by
        behaviour is that an argument-level refusal does not need a panel. This
        run points `--panel` at a file that does not exist: the argument check
        still refuses and still names the flag, while a guard that fires inside
        the evaluator could not have been reached without reading the panel
        first.
        """

        code, out, err = self.run_command(
            "--regime-variable", self.REGIME_VARIABLE,
            model="threshold",
            features=self.FEATURES,
        )
        self.assertEqual(code, 2)
        self.assertIn(self.REGIME_VARIABLE, err)
        self.assertIn("--regime-variable", err)
        self.assertIn("--feature", err)
        self.assertEqual(out, "")
        self.assertEqual(read_journal(self.journal), ())

        absent = self.tmp / "no-such-panel.csv"
        self.assertFalse(absent.exists())
        code, out, err = self.run_command(
            "--regime-variable", self.REGIME_VARIABLE,
            "--panel", str(absent),
            model="threshold",
            features=self.FEATURES,
        )
        self.assertEqual(code, 2)
        self.assertIn("--regime-variable", err)
        self.assertNotIn(
            absent.name,
            err,
            msg="the command read the panel before validating its own "
            "arguments; the refusal is coming from somewhere downstream",
        )
        self.assertEqual(read_journal(self.journal), ())

    def test_a_threshold_run_declares_its_regime_variable_and_is_recorded(self):
        """The declared case, so the refusal above is not the only path tested.

        The regime variable is one of `--feature`, so what the predictor is
        handed and what the run declared are the same set by construction. The
        run completes, and its record hashes a `model_config` that names both
        the model and the column the regime was read off -- which is the one
        thing about a threshold run that the feature set alone cannot recover.
        """

        report = self.scored(
            "--regime-variable", self.REGIME_VARIABLE,
            model="threshold",
            features=self.REGIME_FEATURES,
        )[0]
        self.assertEqual(report["model"], "threshold")
        self.assertEqual(report["features"], sorted(self.REGIME_FEATURES))

        record, = read_journal(self.journal)
        self.assertEqual(
            record["config_sha256"],
            config_digest(
                self.expected_config(
                    "threshold",
                    self.REGIME_FEATURES,
                    regime_variable=self.REGIME_VARIABLE,
                )
            ),
        )
        # Two threshold runs over one feature set reading different regime
        # columns must not hash alike, which is the reason the column is in
        # `model_config` rather than left implied by `features`.
        self.assertNotEqual(
            record["config_sha256"],
            config_digest(
                self.expected_config(
                    "threshold", self.REGIME_FEATURES, regime_variable="on_rrp"
                )
            ),
        )

    def test_a_regime_variable_is_refused_for_a_model_that_reads_none(self):
        """A flag accepted and ignored is read as a setting that took effect."""

        code, out, err = self.run_command(
            "--regime-variable", self.REGIME_VARIABLE,
            model="arx",
            features=self.REGIME_FEATURES,
        )
        self.assertEqual(code, 2)
        self.assertIn("--regime-variable", err)
        self.assertIn("arx", err)
        self.assertEqual(read_journal(self.journal), ())

    def test_a_threshold_model_without_a_regime_variable_is_refused(self):
        code, _, err = self.run_command(model="threshold")
        self.assertEqual(code, 2)
        self.assertIn("--regime-variable", err)
        self.assertEqual(read_journal(self.journal), ())

    def test_the_regressors_are_the_declaration_minus_what_the_fitter_supplies(self):
        """One declaration, and the regressors taken out of it.

        A second list beside `--feature` could disagree with it, and the purge
        is sized over `--feature` alone -- so a regressor outside the
        declaration would be read under a gap that never priced its source. The
        selector therefore derives the regressors rather than accepting them,
        and this pins what it derives: the declaration, less the autoregressive
        term the fitter supplies itself, less the regime variable, which is not
        a term at all.
        """

        parser = cli.build_parser()
        args = parser.parse_args(
            ["event-holdout", "--panel", "p", "--events", "e", "--thresholds", "t",
             "--registry", "r", "--journal", "j", "--decision-time", DECISION_TIME,
             "--model", "threshold", "--regime-variable", self.REGIME_VARIABLE]
            + [flag for name in self.REGIME_FEATURES for flag in ("--feature", name)]
        )

        seen = {}

        def spy(regressors, threshold_variable, minimum_history=20):
            seen["regressors"] = tuple(regressors)
            seen["threshold_variable"] = threshold_variable
            return baseline.threshold_exceedance(
                regressors, threshold_variable, minimum_history=minimum_history
            )

        choice = cli_eval.MODEL_FACTORIES["threshold"]
        patched = type(choice)(
            factory=spy, build=choice.build, needs_regime_variable=True
        )
        original = dict(cli_eval.MODEL_FACTORIES)
        original["threshold"] = patched
        with unittest.mock.patch.object(
            cli_eval, "MODEL_FACTORIES", original
        ):
            name, _ = cli_eval._select_model(args)

        self.assertEqual(name, "threshold")
        self.assertEqual(seen["threshold_variable"], self.REGIME_VARIABLE)
        self.assertEqual(seen["regressors"], ("on_rrp",))

    def test_the_autoregressive_term_is_the_one_the_fitter_supplies(self):
        """`_AUTOREGRESSIVE_TERM` is pinned against the design it names.

        The selector takes that column out of the regressors because `fit_arx`
        puts it into the design itself. If the two ever disagreed, every
        conditional run would carry the same column twice and be refused as
        singular -- a total failure, but one that would arrive at the far end of
        a fit rather than here. A rename in `baseline` fails this instead.
        """

        rows = load_daily_panel(self.panel)
        model = baseline.fit_arx(
            rows[: self.MINIMUM_HISTORY + 5], ("on_rrp",),
            minimum_history=self.MINIMUM_HISTORY,
        )
        self.assertIn(cli_eval._AUTOREGRESSIVE_TERM, model.design_names)
        self.assertNotIn(cli_eval._AUTOREGRESSIVE_TERM, model.regressors)


class RollingBacktestHarness(unittest.TestCase):
    """The sample panel, one registry pricing two feature sets differently.

    Split out of `RollingBacktestCommandTests` when `PublishedReportTests`
    arrived and needed the same fixture. Inheriting the *tests* to get the
    fixture would have run them twice under a second name, which inflates a
    suite without strengthening it -- and this file already keeps a fixture in
    its own class, `EventHoldoutHarness`, for exactly this reason.
    """

    PANEL = REPO_ROOT / "data" / "sample" / "daily_market.csv"
    MINIMUM_HISTORY = "10"

    #: Two declarations, the slower a superset of the faster. Both contain
    #: `spread_bps`, because every model here reads it -- a declaration that
    #: omitted it is refused by the fitter check, which is that check working.
    #: So the only way to widen the gap is to declare more, which is the shape
    #: the design intends: sources follow features, gap follows sources.
    FAST_FEATURES = ("spread_bps",)
    SLOW_FEATURES = ("spread_bps", "treasury_settlement")

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        # One registry pricing both feature sets, at different lags, so a run
        # can name either and the gap has to follow the naming.
        self.registry = self.tmp / "registry.json"
        self.registry.write_text(
            json.dumps(
                {
                    "nyfed_sofr": self._lag(1),
                    "fred_macro_latest_vintage": self._lag(1),
                    "treasury_auctions": self._lag(6),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _lag(days):
        return {
            "release_lag": {
                "basis": "record_date",
                "unit": "calendar_days",
                "days": days,
                "available_time": "00:00",
                "timezone": "America/New_York",
            }
        }

    def run_backtest(
        self, *features, decision_time=DECISION_TIME, registry=None, report=None
    ):
        """Run the command. `report` names the artifact; one is always written.

        `--report` is required now, so every caller supplies one. The default
        is a fresh path per call, named after the declaration so a test that
        runs two feature sets does not have the second overwrite the first --
        which would make the acceptance test below compare a report against
        itself and pass on any mutation at all.
        """

        self.last_report = Path(
            report or self.tmp / f"report-{'-'.join(features) or 'none'}.json"
        )
        argv = [
            "backtest", str(self.PANEL),
            "--minimum-history", self.MINIMUM_HISTORY,
            "--registry", str(registry or self.registry),
            "--decision-time", decision_time,
            "--report", str(self.last_report),
        ]
        for feature in features:
            argv += ["--feature", feature]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue(), err.getvalue()

    def scored(self, *features, **kwargs):
        code, out, err = self.run_backtest(*features, **kwargs)
        self.assertEqual(code, 0, msg=f"command failed: {err.strip()}")
        return json.loads(out)

    def published(self, *features, **kwargs):
        """The artifact the run wrote, parsed. The run must have succeeded."""

        self.scored(*features, **kwargs)
        return json.loads(self.last_report.read_text(encoding="utf-8"))


class RollingBacktestCommandTests(RollingBacktestHarness):
    """The rolling path, sized the way the event path has always been sized.

    `_event_holdout`'s docstring already claimed the property: "The two
    evaluation paths mean the same thing by a gap and take the number from the
    same place." Until this block that was true of one path. The `backtest`
    command ran an unpurged walk and had no `--source` to size a gap with, so
    every benchmark number the project published came out of a backtest with no
    gap at all while the sentence describing the design sat one function away.

    The two tests here are the pair that keeps it true: one that the number
    reaches the run and follows from the named sources, one that the absence of
    a way to set it by hand is still an absence.

    The fixture is `RollingBacktestHarness`'s; `PublishedReportTests` uses the
    same one.
    """

    def test_the_rolling_command_takes_its_purge_from_the_declared_features(self):
        """The gap follows from `--feature`, and it reaches the reported numbers.

        Asserted as a relation between two feature sets rather than against a
        literal. The two resolve to sources the registry prices differently, so
        naming the slower one must widen the gap; a wider gap costs origins and
        moves the metrics. A command that reported a `purge_days` it did not
        pass on -- the plausible mistake, since the field would still look right
        -- would hold the first assertion and fail the second.
        """

        slow = self.scored(*self.SLOW_FEATURES)
        fast = self.scored(*self.FAST_FEATURES)

        self.assertGreater(fast["purge_days"], 0)
        self.assertGreater(slow["purge_days"], fast["purge_days"])

        # The gap reached the run: a wider one leaves fewer origins and a
        # different benchmark, not merely a different field in the report.
        self.assertLess(slow["forecast_count"], fast["forecast_count"])
        self.assertNotEqual(slow["mae_bps"], fast["mae_bps"])

        # The wider declaration takes the maximum over the union of its
        # sources, which is what "the purge for a backtest is the maximum over
        # the sources the feature set uses" means. Declaring more never narrows
        # the gap.
        self.assertEqual(
            slow["sources"],
            sorted(set(fast["sources"]) | {"treasury_auctions"}),
        )

    def test_both_commands_report_the_features_and_the_sources_they_derived(self):
        """Derived facts, reported as such. An auditor must be able to follow it.

        The old report echoed the `--source` list back, which said only that
        argparse worked. These three fields now say what the command *decided*:
        the declaration it was given, the sources that declaration resolved to,
        and the gap those sources produced. `sources` in particular is a fact
        the caller never supplied and cannot have mistyped.
        """

        report = self.scored(*self.FAST_FEATURES)
        self.assertEqual(report["features"], sorted(self.FAST_FEATURES))
        # Not echoed: `spread_bps` is one name and resolves to two sources.
        self.assertEqual(
            report["sources"],
            ["fred_macro_latest_vintage", "nyfed_sofr"],
        )
        self.assertEqual(report["purge_days"], 1)

        # And the same three on the event path, per scored window.
        holdout = EventHoldoutHarness("run_command")
        holdout.setUp()
        self.addCleanup(holdout.doCleanups)
        window = holdout.scored()[0]
        self.assertEqual(window["features"], [FEATURE])
        self.assertEqual(
            window["sources"], ["fred_macro_latest_vintage", "nyfed_sofr"]
        )
        self.assertEqual(window["purge_days"], 6)

    def test_an_undeclared_feature_is_refused_before_any_fold_is_built(self):
        """A name the map does not classify is refused, naming the column.

        The silent-zero failure, one level up from the registry: a feature set
        that resolved to an empty source set would produce a zero-day gap and a
        perfectly ordinary-looking benchmark. `contract.sources_for_features`
        raises instead, and the command must let that reach the caller rather
        than defaulting around it.

        The refusal has to arrive before the run, not after -- a benchmark that
        printed numbers and then complained would have scored something.
        """

        code, out, err = self.run_backtest("no_such_column")
        self.assertEqual(code, 2)
        self.assertIn("no_such_column", err)
        self.assertEqual(out, "", msg="the run produced output before refusing")

        # A declared column with no ingesting source is refused with its reason,
        # rather than purging zero days over an empty source set.
        code, out, err = self.run_backtest("dealer_treasury_position")
        self.assertEqual(code, 2)
        self.assertIn("dealer_treasury_position", err)
        self.assertEqual(out, "")

    def test_there_is_no_source_flag(self):
        """Sources are derived, never supplied. The absence is the guard.

        A caller who could name the sources by hand could name a set that did
        not cover what the model reads. The purge would then be computed
        correctly, by the right function, over the wrong evidence -- and every
        number would look reasonable, because the arithmetic was never the
        problem. That is the failure this block closed, and a `--source` added
        back "for the conservative case" reopens it.

        Checked on both commands: the event path had `--source` too, and a hole
        reopened on one path is a hole.
        """

        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        for name in ("backtest", "event-holdout"):
            with self.subTest(command=name):
                options = {
                    option
                    for action in command.choices[name]._actions
                    for option in action.option_strings
                }
                self.assertNotIn("--source", options, msg="--source is back")
                self.assertIn("--feature", options)

    def test_there_is_no_purge_flag(self):
        """The absence is the guard, so the test reads the parser.

        No behavioural test can catch a flag nobody passes. And this path is
        where it would be reached for: the purge drops training rows, a short
        panel then yields fewer origins or none, and a `--purge` sitting beside
        `--minimum-history` would turn "the gap starved the backtest" into "the
        gap is whatever gets a number out".
        """

        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        backtest = command.choices["backtest"]
        options = {
            option
            for action in backtest._actions
            for option in action.option_strings
        }

        for banned in ("--purge", "--purge-days", "--gap"):
            self.assertNotIn(banned, options, msg=f"{banned} is back")
        self.assertIn("--feature", options)
        self.assertIn("--decision-time", options)

        # `--feature`, `--registry` and `--decision-time` are required, not
        # defaulted: a default decision time is a silent assumption about when
        # the forecast is made, and a default feature set is a silent claim
        # about which sources the model draws on.
        required = {
            action.dest for action in backtest._actions if getattr(action, "required", False)
        }
        self.assertLessEqual({"feature", "registry", "decision_time"}, required)
        for action in backtest._actions:
            if action.dest in ("feature", "registry", "decision_time"):
                self.assertIsNone(
                    action.default, msg=f"--{action.dest} acquired a default"
                )


class PublishedReportTests(RollingBacktestHarness):
    """The benchmark as a file, and the conditions travelling with the numbers.

    `PLAN.md` Milestone A ends in a *published* pinball loss and interval
    coverage, and its exit criterion says the published figures are generated
    output rather than prose. Before this block nothing wrote any of it:
    `metrics.pinball_loss` and `metrics.crps_from_quantiles` had been
    implemented, tested and called by nothing on this path, and `BacktestReport`
    carried an MAE and a coverage and no quantile loss at all. The numbers
    existed for the length of a terminal session.

    Shares `RollingBacktestHarness` with the command tests above: the same
    panel, the same registry, and the same two declarations, one of which
    resolves to a source the registry prices further out. What is added is that
    the run now leaves something behind, and that what it left behind is about
    the run that left it.

    The schema
    ----------

    `baseline.backtest_document` holds the field-by-field reasoning; the shape
    is four questions and their answers. **`declaration`** -- the feature set,
    the decision time, the minimum history -- is the only thing the caller
    chose. **`derived`** -- the sources and the purge gap -- is what that
    choice produced, read off the report rather than recomputed, so the
    artifact cannot publish a gap the run did not use. **`panel`** is path,
    `sha256`, row count and date range: the path says which file was asked for
    and the digest says which bytes answered, and without the second a report
    is a claim about a file that may since have changed. **`folds`** is the
    count plus the first and last origin in full, which is where an
    off-by-one in the gap would show, and which does not grow with the panel.
    **`metrics`** is every number, unrounded.

    Two omissions are deliberate. There is **no per-forecast dump**, so the
    losses cannot be recomputed from this file alone -- they can be recomputed
    from the panel, which the file identifies by digest, and that is what makes
    the digest load-bearing rather than decorative. And there is **no event
    aggregate**: `AGENT_CONTRACT.md` forbids an aggregate Brier or reliability
    number on a single event window, and a benchmark artifact that carried one
    would be the place somebody averaged it into the main table.

    The bootstrap block size
    ------------------------

    The interval around the headline MAE comes through
    `metrics.stationary_bootstrap_interval`, as every interval in this project
    does. Its mean block length is **measured, not declared**: it is the
    largest number of scored days whose forecast horizons overlap at any one
    point, swept off this run's own folds by `baseline._maximum_horizon_over-
    lap`. The reasoning is the standard one -- overlapping h-step forecast
    errors are MA(h-1), so blocks must be long enough to carry that dependence
    -- and the measurement matters because the alternative arithmetic is in the
    wrong units. The gap is in calendar days and the panel is in rows; a
    weekend inside a six-day gap makes the horizon span seven calendar days and
    five panel rows, so `purge + 1` would be a number that looks about right
    and is not. On the sample panel the two declarations give block lengths of
    2 and 5, and the wider gap gets the longer blocks, which is the dependence
    the gap creates being carried by the resample that reports it. With no
    purge no two horizons overlap, the sweep returns 1, and the resample is the
    iid bootstrap -- which is the correct answer for one-step errors over
    disjoint days, arrived at rather than special-cased.

    The seed is derived from the run's identity -- panel digest, feature set,
    gap, decision time -- and recorded. A literal would have satisfied the
    signature and broken this block's one rule, and would also have made every
    run in the project share a resample stream.

    Mutation record
    ---------------

    Unmutated control first, green before and after. Copied under `$HOME`,
    never the mount, with `data/`, `.github/`, `metadata/` and also
    `.gitignore`, the root Markdown and `docs/PROJECT_STATUS.md` -- the
    freshness guard reads those and their absence is two kills that look real.
    Run with `-B` and `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` cleared
    between mutations.

      * **The purge emitted as a constant** rather than read off the report the
        run returned -- `"purge_days": 1` in `backtest_document`, the fast
        run's own value, so the fast report still reads correctly and only the
        slow one is silently wrong. Fails 1:
        `test_the_report_carries_the_gap_the_numbers_were_produced_under`, on
        "both reports published the same gap". **This is the acceptance
        criterion and the mutation target, and they did not come apart.** That
        exactly one test dies is the intended result and not a weak spot: the
        criterion is a property of two runs compared to each other, and no
        single-run assertion can express it.

      * **The pinball losses zipped against a reversed loss vector**, so the
        0.05 loss is published under `0.95`. Fails 1:
        `test_the_pinball_losses_are_the_ones_the_run_computed_at_each_level`.
        Worth noting what did *not* die: the acceptance test compares the two
        runs' loss mappings and they still differ, because both runs are
        reversed consistently. Five levels and five plausible numbers look
        entirely well behaved, so nothing but recomputing a loss at a named
        level from the run's own quantile vectors can tell. The keys are not
        decoration, and it takes a test that recomputes only the labelling to
        say so.

      * **The bootstrap replaced by a fixed width** around the point estimate.
        **The first attempt found a real gap and the test was strengthened
        because of it.** As first written, this killed only
        `test_the_report_carries_no_number_the_document_did_not_compute`, the
        source-level guard -- the behavioural interval test passed, because a
        fixed width still brackets the MAE, is still ordered, still reproduces
        across runs (a constant always does), and leaves the recorded block
        length still moving with the gap. Every structural property held while
        the number meant nothing. A source guard catching what a behavioural
        test misses is the wrong way round: it fails on how the code is spelled
        rather than on what it published, and it would go quiet the moment
        somebody wrote the same mutation without a float literal. So
        `test_the_headline_carries_an_interval_and_it_is_bootstrapped` now
        re-drives `stationary_bootstrap_interval` from the seed, block length,
        replication count and level the *artifact* records, and holds the
        published bounds to it -- which is also the check a reader of the file
        can run, and the reason those four fields are in the file at all. With
        that assertion in place the mutation fails 2, the behavioural test
        included, and so does a literal-free variant that scales the width by
        the point estimate.

      * **The boring one, and it was boring.** `mae_bps` and
        `interval_coverage` on the sample panel, measured on `HEAD` before this
        block and on the working tree after, at full `repr` precision under
        both declarations: bit-identical, fold counts included. This block
        publishes existing numbers and does not change them.

        The half worth recording is that the numbers are *pinned*, not merely
        unchanged. Dividing the MAE by `n - 1` fails 5 -- four in
        `test_baseline` (`test_persistence_remains_the_default_with_unchanged_-
        numbers`, `test_rolling_backtest_is_time_ordered`, `test_the_arx_-
        reports_the_numbers_it_reported_before_a_third_model_existed`,
        `test_the_backtest_derives_its_purge_from_the_declared_feature_set`)
        plus `test_the_purge_moves_the_reported_numbers_and_the_move_is_kept`
        -- all of them pre-existing. A silent change to the headline during
        this block would not have been silent.

    What publishing surfaced
    ------------------------

    Two things the console output had hidden, both of them the block working.

    **`INTERVAL_PROBABILITY` is not 0.90.** It is `0.95 - 0.05` in binary
    floating point, which is `0.8999999999999999`, and the artifact publishes
    that because the artifact does not round. The console never showed it at
    all -- it printed a coverage and no target -- and any place it *had* shown
    it would have applied `round(..., 4)` and displayed `0.9`. The value is
    correct and the derivation is right; what was hidden is that the number is
    a computed float and not the decimal a reader would assume. It is left
    unrounded on purpose: rounding it here would publish a figure nobody
    computed, which is the failure this whole artifact exists to prevent, and
    the repair -- if one is wanted -- belongs in `contract.py`, which is
    human-owned.

    **The interval is badly calibrated on the sample panel, and the artifact is
    the first place that is legible.** Coverage comes out near 0.57 against a
    declared 0.90 predictive interval. Both numbers existed before; they never
    appeared together, because the console printed `interval_coverage` with
    nothing beside it to compare against. Putting the target next to the
    realization is a one-field change and it turns a number that read as
    unremarkable into an obvious miscalibration. It is a short sample fixture
    scored over a handful of origins, so it is not yet evidence about the model
    -- but it is the shape of finding this block was built to make possible,
    and it arrived on the first run.
    """

    def test_the_report_carries_the_gap_the_numbers_were_produced_under(self):
        """The acceptance criterion, and the mutation target.

        Two runs on one panel, differing only in the declared feature set, and
        therefore in the gap that set derives. Both publish. The reports must
        carry **different** gaps and **different** metrics, and each report's
        metrics must be the ones *that* run produced.

        The last clause is what the test is for, and it is what a weaker
        version would leave out. A reporter that emitted the purge as a
        constant, or that shaped the document from a run other than the one it
        just executed, still writes two files with plausible contents -- and a
        test that only checked "the two files differ" or "the gap is an int"
        would pass on it. So the gaps are cross-checked against the console
        summary of the same invocation, which is read off the returned report
        object, and the metrics are cross-checked against the numbers that
        invocation printed. A figure detached from the conditions that produced
        it is exactly the object this block exists to prevent, and it is
        detached silently: every field still looks like a number.

        Direction, not magnitude. The wider declaration purges further, which
        costs origins; a shorter benchmark on this panel scores harder days.
        Asserting *that the gap moved and the numbers moved with it* is a
        property of the derivation, while asserting either value is a fixture
        transcription that would have to be rewritten the next time the sample
        panel does.
        """

        # Each run is a full invocation: the console summary and the artifact
        # come out of the same command, so a report that carried another run's
        # numbers disagrees with the summary printed beside it.
        slow_summary = self.scored(*self.SLOW_FEATURES)
        slow = json.loads(self.last_report.read_text(encoding="utf-8"))
        fast_summary = self.scored(*self.FAST_FEATURES)
        fast = json.loads(self.last_report.read_text(encoding="utf-8"))

        self.assertNotEqual(
            slow["derived"]["purge_days"],
            fast["derived"]["purge_days"],
            msg="both reports published the same gap; a constant would do this",
        )
        self.assertGreater(
            slow["derived"]["purge_days"], fast["derived"]["purge_days"]
        )
        self.assertGreater(fast["derived"]["purge_days"], 0)

        # Each report's gap is its own run's, not the other's and not a fixed
        # one: it agrees with what that invocation reported to the console.
        self.assertEqual(slow["derived"]["purge_days"], slow_summary["purge_days"])
        self.assertEqual(fast["derived"]["purge_days"], fast_summary["purge_days"])

        # The gap reached the run rather than only the record. A wider gap
        # leaves fewer origins, so a report whose gap was stamped on afterwards
        # would hold the assertions above and fail here.
        self.assertLess(slow["folds"]["count"], fast["folds"]["count"])
        # One fold per scored forecast, in each report. A fold count that had
        # been stamped on rather than counted could disagree with the metrics
        # computed beside it.
        self.assertEqual(slow["folds"]["count"], slow["metrics"]["forecast_count"])
        self.assertEqual(fast["folds"]["count"], fast["metrics"]["forecast_count"])

        # And the metrics moved with it -- every one of them, not only the
        # headline. A report that carried one run's metrics under another run's
        # gap is the failure this test is named for.
        for metric in ("mae_bps", "interval_coverage", "crps_bps"):
            with self.subTest(metric=metric):
                self.assertNotEqual(
                    slow["metrics"][metric],
                    fast["metrics"][metric],
                    msg=f"{metric} did not move with the gap",
                )
        self.assertNotEqual(
            slow["metrics"]["pinball_loss"], fast["metrics"]["pinball_loss"]
        )

        # Each set of metrics belongs to the run that emitted it. The console
        # summary rounds and the artifact does not, so this is the comparison
        # the two can be held to.
        for report, summary in ((slow, slow_summary), (fast, fast_summary)):
            with self.subTest(purge=report["derived"]["purge_days"]):
                self.assertEqual(
                    round(report["metrics"]["mae_bps"], 4), summary["mae_bps"]
                )
                self.assertEqual(
                    round(report["metrics"]["interval_coverage"], 4),
                    summary["interval_coverage"],
                )
                self.assertEqual(
                    report["metrics"]["forecast_count"], summary["forecast_count"]
                )
                self.assertEqual(report["derived"]["sources"], summary["sources"])
                self.assertEqual(
                    report["declaration"]["features"], summary["features"]
                )

        # The gap is visible on the calendar, on the fold where it applies.
        # This is the gap as a fact about dates rather than as a field: a
        # report that named a wider purge while scoring the day after its
        # feature row would pass every assertion above.
        for report in (slow, fast):
            purge = report["derived"]["purge_days"]
            with self.subTest(purge=purge):
                for position in ("first", "last"):
                    fold = report["folds"][position]
                    span = (
                        date.fromisoformat(fold["scored_date"])
                        - date.fromisoformat(fold["feature_date"])
                    ).days
                    self.assertGreater(
                        span,
                        purge,
                        msg=f"the {position} fold scored a day only {span} "
                        f"days after the row it was conditioned on, under a "
                        f"declared gap of {purge}",
                    )
                    self.assertEqual(fold["train_end"], fold["feature_date"])

    def test_the_pinball_losses_are_the_ones_the_run_computed_at_each_level(self):
        """Keys are not decoration: each loss is the loss at the level naming it.

        The report keys a loss by its quantile level, and a mapping built by
        zipping two tuples can be built backwards. Nothing about the resulting
        file looks wrong -- five levels, five plausible numbers, monotone in
        neither direction by nature -- so the only thing that can catch it is
        recomputing a loss from the forecasts the run produced.

        So this runs the backtest in process, computes the mean pinball loss at
        each level straight from `metrics.pinball_loss` over the returned
        forecasts' own quantile vectors, and holds the published file to it. It
        does not recompute the *forecasts*: those come from the run, which is
        the thing under test. It recomputes only the labelling.
        """

        published = self.published(*self.FAST_FEATURES)
        report = rolling_persistence_backtest(
            load_daily_panel(self.PANEL),
            features=self.FAST_FEATURES,
            registry=json.loads(self.registry.read_text(encoding="utf-8")),
            decision_time=time.fromisoformat(DECISION_TIME),
            minimum_history=int(self.MINIMUM_HISTORY),
        )

        self.assertEqual(report.quantile_levels, QUANTILE_LEVELS)
        expected = {
            f"{level:.2f}": sum(
                pinball_loss(level, item.quantiles_bps[position], item.actual_bps)
                for item in report.forecasts
            )
            / len(report.forecasts)
            for position, level in enumerate(QUANTILE_LEVELS)
        }
        self.assertEqual(published["metrics"]["pinball_loss"], expected)

        # The losses at the outer levels are not equal on this panel, which is
        # what makes the assertion above able to fail: a swap between two equal
        # numbers is invisible, and a test that could not tell them apart would
        # be checking nothing.
        self.assertNotEqual(
            published["metrics"]["pinball_loss"]["0.05"],
            published["metrics"]["pinball_loss"]["0.95"],
        )

        # And CRPS is the pinball identity over the same grid, computed by
        # calling the metric rather than by doubling the average here.
        self.assertAlmostEqual(
            published["metrics"]["crps_bps"],
            sum(
                crps_from_quantiles(
                    QUANTILE_LEVELS, item.quantiles_bps, item.actual_bps
                )
                for item in report.forecasts
            )
            / len(report.forecasts),
        )

    def test_the_headline_carries_an_interval_and_it_is_bootstrapped(self):
        """The MAE is reported with a sampling interval, not alone.

        A benchmark that fits in a sample panel has few enough origins that a
        difference between two models is as likely to be resampling noise as
        signal, and a bare point estimate invites a reader to believe
        otherwise. The interval brackets the point
        estimate, its resample structure is recorded, and the block length is
        measured off this run's fold horizons rather than declared -- so a run
        with a wider gap, whose errors overlap over more days, resamples in
        longer blocks.

        The interval is not asserted to any width. What is asserted is that it
        is an interval around this run's number, that it is reproducible, and
        that its structure moved with the gap.
        """

        fast = self.published(*self.FAST_FEATURES)
        slow = self.published(*self.SLOW_FEATURES)

        for report in (fast, slow):
            interval = report["metrics"]["mae_bps_interval"]
            with self.subTest(purge=report["derived"]["purge_days"]):
                self.assertLessEqual(interval["lower"], report["metrics"]["mae_bps"])
                self.assertLessEqual(report["metrics"]["mae_bps"], interval["upper"])
                self.assertLess(interval["lower"], interval["upper"])
                self.assertEqual(interval["method"], "stationary_bootstrap")
                self.assertGreaterEqual(interval["block_length"], 1)
                self.assertIsInstance(interval["seed"], int)
                self.assertGreaterEqual(interval["replications"], 2)

        # Longer horizons, longer blocks. The gap creates the dependence, so
        # the resample that reports the uncertainty has to carry it.
        self.assertGreater(
            slow["metrics"]["mae_bps_interval"]["block_length"],
            fast["metrics"]["mae_bps_interval"]["block_length"],
        )

        # Reproducible: the seed is derived from the run's own identity, so the
        # same declaration against the same panel bytes gives the same interval
        # to the last digit. An interval that cannot be reproduced cannot be
        # checked, which is why `stationary_bootstrap_interval` demands a seed.
        again = self.published(*self.FAST_FEATURES, report=self.tmp / "again.json")
        self.assertEqual(
            again["metrics"]["mae_bps_interval"],
            fast["metrics"]["mae_bps_interval"],
        )

        # And the recorded parameters reproduce the recorded interval, driving
        # `metrics.stationary_bootstrap_interval` from the artifact alone.
        #
        # **This is the assertion that makes the block above mean something,
        # and it was added because a mutation got past the block above.**
        # Replacing the bootstrap with a fixed half-basis-point width around
        # the point estimate satisfies every structural check here -- it
        # brackets the MAE, it is ordered, its recorded block length still
        # moves with the gap, and it reproduces across runs because a constant
        # always does. The only thing that can tell a bootstrap from a made-up
        # width is redoing the bootstrap, so this redoes it: the forecasts come
        # from the run, and the resample is driven by the seed, block length,
        # replication count and level the artifact published.
        interval = fast["metrics"]["mae_bps_interval"]
        report = rolling_persistence_backtest(
            load_daily_panel(self.PANEL),
            features=self.FAST_FEATURES,
            registry=json.loads(self.registry.read_text(encoding="utf-8")),
            decision_time=time.fromisoformat(DECISION_TIME),
            minimum_history=int(self.MINIMUM_HISTORY),
        )
        errors = [
            abs(item.actual_bps - item.predicted_bps) for item in report.forecasts
        ]
        lower, upper = stationary_bootstrap_interval(
            lambda indices: sum(errors[i] for i in indices) / len(indices),
            len(errors),
            block_length=interval["block_length"],
            seed=interval["seed"],
            replications=interval["replications"],
            level=interval["level"],
        )
        self.assertEqual((lower, upper), (interval["lower"], interval["upper"]))

        # A percentile interval from a real resample is not centred on the
        # point estimate. Stated so that a symmetric width -- the shape a
        # made-up interval takes -- is a failure rather than a curiosity.
        self.assertNotAlmostEqual(
            fast["metrics"]["mae_bps"] - interval["lower"],
            interval["upper"] - fast["metrics"]["mae_bps"],
        )

    def test_the_report_identifies_the_bytes_it_was_computed_from(self):
        """Path and digest, from one read. A path alone is a decaying claim.

        A report naming `data/sample/daily_market.csv` says which file was
        asked for. It does not say which bytes answered, and the bytes are what
        the numbers came from -- so a panel edited after publication leaves a
        figure that reads as current and is not, which is the decay this
        project's freshness guard forbids in prose and would otherwise permit
        in its own output.

        The extent is here for a second reason: a digest identifies a file, and
        the row count and date range identify what was actually scored out of
        it.
        """

        published = self.published(*self.FAST_FEATURES)
        panel = published["panel"]

        self.assertEqual(panel["path"], str(self.PANEL))
        self.assertEqual(
            panel["sha256"],
            hashlib.sha256(self.PANEL.read_bytes()).hexdigest(),
        )
        rows = load_daily_panel(self.PANEL)
        self.assertEqual(panel["row_count"], len(rows))
        self.assertEqual(panel["first_date"], rows[0].date.isoformat())
        self.assertEqual(panel["last_date"], rows[-1].date.isoformat())

    def test_no_field_in_the_report_is_defaulted_into_existence(self):
        """A field that cannot be computed is absent, not filled in.

        The rule the whole artifact rests on. A defaulted field is read as a
        measurement, and a zero that means "not computed" is the same failure
        as a typed number: right-looking, and detached from any run.

        `BacktestReport` is constructible without the conditions -- the
        longhand reproduction in `tests/test_baseline.py` does exactly that,
        deliberately, so it keeps reproducing the walk as it stood. A document
        built from such a report must omit what it does not know rather than
        publish `null`, `0`, or a plausible default.
        """

        bare = BacktestReport(
            forecasts=[Forecast(1.0, 0.5, 0.0, 2.0, (0.0, 0.25, 0.5, 1.0, 2.0))],
            mae_bps=0.5,
            interval_coverage=1.0,
        )
        document = backtest_document(bare, panel_path=self.PANEL)

        self.assertNotIn("decision_time", document["declaration"])
        self.assertNotIn("minimum_history", document["declaration"])
        for absent in ("row_count", "first_date", "last_date"):
            self.assertNotIn(absent, document["panel"])
        self.assertNotIn("first", document["folds"])
        self.assertNotIn("last", document["folds"])
        self.assertNotIn("pinball_loss", document["metrics"])
        self.assertNotIn("crps_bps", document["metrics"])

        # Nothing anywhere in the document is null. An omitted field makes a
        # reader ask; a null one makes them believe a run answered.
        self.assertNotIn("null", json.dumps(document))

        # A full report omits none of them.
        full = self.published(*self.FAST_FEATURES)
        self.assertIn("decision_time", full["declaration"])
        self.assertIn("minimum_history", full["declaration"])
        self.assertIn("pinball_loss", full["metrics"])
        self.assertIn("first", full["folds"])

    def test_the_artifact_is_not_optional_and_the_numbers_are_not_rounded(self):
        """`--report` is required, and the file publishes what was computed.

        Two halves of one decision. A benchmark whose artifact is optional is a
        benchmark that mostly does not produce one, and the figures go back to
        living in scrollback -- which is the state this block was written to
        end. And an artifact that rounded would publish a number nobody
        computed, and would make two runs that genuinely differ read as
        identical.
        """

        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        backtest = command.choices["backtest"]
        required = {
            action.dest
            for action in backtest._actions
            if getattr(action, "required", False)
        }
        self.assertIn("report", required)

        summary = self.scored(*self.FAST_FEATURES)
        published = json.loads(self.last_report.read_text(encoding="utf-8"))

        # The same number, at two precisions: the console rounds for a human,
        # the artifact does not. Asserting the file carries *more* digits than
        # the console is what makes this a claim about the artifact rather than
        # a restatement of the summary.
        self.assertEqual(round(published["metrics"]["mae_bps"], 4), summary["mae_bps"])
        self.assertNotEqual(
            published["metrics"]["mae_bps"],
            summary["mae_bps"],
            msg="the published MAE is already rounded to the console's precision",
        )
        # And the console says where the artifact went, so a reader of the
        # terminal can find the record the run published.
        self.assertEqual(summary["report"], str(self.last_report))

    def test_the_report_carries_no_number_the_document_did_not_compute(self):
        """No metric literal in the reporting code. Read as source, not output.

        The behavioural tests above all compare the artifact to another
        computation, so a reporter that hard-coded a value equal to today's
        would pass them until the panel changed. This reads
        `baseline.backtest_document` and its helpers and asserts that the only
        numbers in them are the declared bootstrap parameters and the format
        widths -- not a basis point anywhere.
        """

        source = "".join(
            inspect.getsource(function)
            for function in (
                baseline.backtest_document,
                baseline._fold_document,
                baseline._level_key,
                baseline.mae_bootstrap_interval,
                baseline._report_seed,
            )
        )
        # Strip docstrings: they discuss the design in prose and a prose
        # numeral is not a published figure.
        stripped = re.sub(r'"""(?:.|\n)*?"""', "", source)
        literals = set(re.findall(r"(?<![\w.])\d+\.\d+", stripped))
        self.assertEqual(
            literals,
            set(),
            msg=f"{sorted(literals)} appear as float literals in the reporter; "
            "every value it publishes must come from the run",
        )


class RealRegistryTests(unittest.TestCase):
    """What the commands do against `metadata/sources.json` as it stands today.

    **What this class claimed before the field-priced-purge block.** That the
    commands refuse to run at all, and that the refusal is correct. `iorb` is a
    required panel column, `spread_bps` is computed from it, and every model in
    this repository reads `spread_bps` -- so every honest feature set resolved
    to `fred_macro_latest_vintage`, whose declared basis is
    `snapshot_retrieved_at`. `AGENT_CONTRACT.md` is explicit that such a source
    contributes no purge and MUST NOT be mapped to zero, and
    `max_release_lag_days` raises unless every row carries `available_at`,
    which `DailyObservation` does not.

    **What it claims now.** That the refusal is a fact about a *field*. The gap
    is priced over `(source, field)` pairs, `fred_macro_latest_vintage.IORB`
    declares a `record_date` lag with a revision policy, and `spread_bps`
    therefore runs against the real file -- which is the first benchmark in
    this project's life sized from the registry it ships. The H.4.1 weeklies on
    that same source declare nothing and are still refused, by name.

    The basis-level fact is unchanged and so is the guard: an exemption, a
    fabricated `available_at`, or a basis mapped to zero would still make these
    tests go green while making every number meaningless. What narrowed is the
    scope of the refusal, not its strength -- and the remaining refusal is
    still pinned rather than skipped, because it goes red the day the weeklies
    are declared or the panel carries `available_at`, which is the right alarm.
    """

    PANEL = REPO_ROOT / "data" / "sample" / "daily_market.csv"

    def _run(self, *features):
        """`backtest` against the real registry, with a report path under a temp dir."""

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.json"
            argv = [
                "backtest", str(self.PANEL),
                "--minimum-history", "10",
                "--registry", str(REGISTRY),
                "--decision-time", DECISION_TIME,
                "--report", str(report),
            ]
            for feature in features:
                argv += ["--feature", feature]
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = cli.main(argv)
            written = (
                json.loads(report.read_text(encoding="utf-8"))
                if report.exists()
                else None
            )
            return code, out.getvalue(), err.getvalue(), written

    def test_the_backtest_refuses_a_real_field_with_no_revision_policy(self):
        """**Before:** any feature set was refused, and the message named the
        source. **Now:** a feature set reading an H.4.1 weekly is refused, and
        the message names the source *and the field* -- `WRESBAL`, which
        declares no revision policy on a `snapshot_retrieved_at` source.

        Everything else this test asserted is unchanged and still load-bearing:
        exit 2, nothing on stdout, and no report file. A report on disk is a
        claim that a benchmark ran, and a refused run that left one would
        outlive the console message that explained it.

        The invocation gained `--report` in the published-benchmark block. That
        is the second thing that changed about this test in one edit and it is
        a separate claim: the flag is required now, so a refusal has an
        artifact path it must decline to write rather than no artifact to speak
        of.
        """

        code, out, err, written = self._run(FEATURE, "reserve_balances")

        self.assertEqual(code, 2)
        self.assertIn("fred_macro_latest_vintage", err)
        self.assertIn("WRESBAL", err)
        self.assertIn("available_at", err)
        self.assertEqual(
            out,
            "",
            msg="the command printed a benchmark and then refused; the gap it "
            "could not size had already reached the folds",
        )
        self.assertIsNone(written, msg="a refused run published a report")

    def test_the_backtest_runs_on_the_real_registry_over_declared_fields(self):
        """The other half, and the reason this block exists.

        `spread_bps` reads `fred_macro_latest_vintage.IORB` and
        `nyfed_sofr.SOFR`, both of which declare a release lag, so the command
        runs against the file this repository ships rather than against a
        fixture. Same source as the test above, opposite verdict.

        Asserted on the artifact, not on the console: `--report` is required
        now, and the artifact is what a later reader has. The console summary
        is checked against it, because a benchmark whose file and whose
        scrollback disagree about what sized the gap is worse than one that
        refused.
        """

        code, out, err, written = self._run(FEATURE)

        self.assertEqual(code, 0, msg=err)
        self.assertIsNotNone(written, msg="a run that returned 0 published nothing")
        self.assertEqual(
            written["derived"]["fields"],
            ["fred_macro_latest_vintage.IORB", "nyfed_sofr.SOFR"],
        )
        self.assertEqual(written["derived"]["sources"], sorted(written["derived"]["sources"]))
        self.assertGreater(written["derived"]["purge_days"], 0)

        summary = json.loads(out)
        self.assertEqual(summary["fields"], written["derived"]["fields"])
        self.assertEqual(summary["purge_days"], written["derived"]["purge_days"])
        self.assertEqual(summary["sources"], written["derived"]["sources"])

    def test_the_refusal_is_the_snapshot_source_and_not_the_whole_registry(self):
        """A feature set clear of the snapshot sources runs against the real file.

        Without this, the test above would also pass if the command refused
        every feature set for some unrelated reason, and the finding it records
        would be about nothing in particular.

        `sofr` alone is not an honest declaration for any model here -- nothing
        forecasts SOFR in levels -- so no fold is built from it. The parser and
        the derivation are what this exercises, which is why it asserts on the
        gap rather than on a benchmark.
        """

        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(
            max_release_lag_days(
                registry,
                sources_for_features(("sofr",)),
                decision_time=time.fromisoformat(DECISION_TIME),
            ),
            6,
        )


class ExceedanceBacktestHarness(unittest.TestCase):
    """A panel that shifts regime, so the pooled table has something in it.

    The `event-holdout` fixture is calm-then-spiked *inside a window*, which is
    the shape a knowledge holdout needs. This command pools every origin over
    the whole panel, so what it needs instead is a panel whose base rate
    changes as the window advances -- otherwise the climatology reference is
    the same number at every fold and the block's whole subject, that the
    reference is refitted per fold, has nothing to show.

    Sixty business days: the first thirty around 2bp, the rest around 9bp. The
    lowest declared tau separates the two regimes; the three above it separate
    nothing, so the artifact has to report three absences with their reasons
    and one real skill score, which is exactly the mix a real run produces.
    """

    LOW_BPS = 2.0
    HIGH_BPS = 9.0
    MINIMUM_HISTORY = "20"

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.registry = declared_registry_file(self.tmp, features=(FEATURE,))
        self.days = business_days(date(2025, 11, 3), 60)
        self.panel = self.write_panel()
        self.report_path = self.tmp / "exceedance.json"

    def write_panel(self, path=None):
        path = path or self.tmp / "panel.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(PANEL_COLUMNS)
            for index, when in enumerate(self.days):
                spread = self.LOW_BPS if index < 30 else self.HIGH_BPS
                # A little jitter so the pooled forecasts are not one repeated
                # value, which the CORP decomposition refuses outright.
                spread += (index % 7) / 100.0
                writer.writerow(
                    [when.isoformat(), round(4.30 + spread / 100.0, 6), 4.30,
                     2100 + index, 4.30, 4.32, 4.30, 4.31, 3200, 720,
                     # `on_rrp` moves so a two-regime model has a cutoff to
                     # find; a constant column has no split and the fitter
                     # refuses it, correctly.
                     115 + (index % 11),
                     "", "", "", 0, 0]
                )
        return path

    def run_command(self, *extra, model="climatology", features=None,
                    thresholds=None, report=None):
        argv = [
            "exceedance-backtest",
            "--panel", str(self.panel),
            "--thresholds", str(thresholds or THRESHOLDS),
            "--registry", str(self.registry),
            "--decision-time", DECISION_TIME,
            "--minimum-history", self.MINIMUM_HISTORY,
            "--report", str(report or self.report_path),
        ]
        for feature in (features if features is not None else (FEATURE,)):
            argv += ["--feature", feature]
        if model is not False:
            argv += ["--model", model]
        argv += [*extra]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue(), err.getvalue()

    def scored(self, *extra, **kwargs):
        code, out, err = self.run_command(*extra, **kwargs)
        self.assertEqual(code, 0, msg=f"command failed: {err.strip()}")
        return json.loads(out)

    def published(self, *extra, **kwargs):
        self.scored(*extra, **kwargs)
        return json.loads(self.report_path.read_text(encoding="utf-8"))


class ExceedanceBacktestCommandTests(ExceedanceBacktestHarness):
    """The headline metric, reachable by name from the command line.

    The packet this block came from put it plainly: the contract's headline
    metric was implemented, unit-tested and wired to nothing. These tests are
    about the wiring -- that the command runs, that it publishes, that it takes
    every declaration from where the declaration lives, and that it is the
    scoring holdout rather than a second way to score an event window.

    Mutation record
    ===============

    The three mutations this command's guards were planted against are recorded
    in full in `tests/test_baseline.py::RollingExceedanceTests`, where the code
    they mutate lives. Two of them reach this file and are recorded there with
    the tests they killed here: the purge dropped from the exceedance path
    kills
    `test_the_gap_follows_from_the_declared_features_and_reaches_the_numbers`,
    and the outcomes taken one tau along kill
    `test_the_command_publishes_the_headline_metric` with a `KeyError` on the
    decomposition the shifted column can no longer support.

    Two mutations belong to this file rather than to that one, and both are
    about absences, so both had to be planted here:

      * **A `--model` default of `climatology` added to the subparser.** The
        command runs, publishes, and reports a skill score of exactly zero --
        the reference scored against itself -- under whatever name a caller
        thought they were running. Fails 1, `test_the_model_has_no_default`,
        and only one, which is the point: a default changes no output for any
        caller who passes the flag, and every other test in this class passes
        it. **On its first run this mutation killed nothing.** The class had a
        test for an unknown `--model` being refused, which a default does not
        touch, and no test for the absence itself. `test_the_model_has_no_default`
        was written because of that run, not before it, and it is the reason
        this mutation is worth recording rather than merely worth doing.

      * **The tau family hard-coded as the declared four** in
        `_exceedance_backtest` instead of read from `--thresholds`. Fails 2:
        `test_the_taus_come_from_the_thresholds_file_and_nowhere_else` on
        behaviour -- the command accepts a thresholds file it should have
        refused -- and `DeclarationTests::test_the_tau_family_carries_no_literal_in_this_module`
        on the source, an existing guard from the `event-holdout` block that
        turns out to cover the second command for free because it reads the
        module rather than a call site. The literal happens to be correct
        today, which is exactly why a suite that only compared outputs would
        stay green while the declaration stopped being load-bearing.

    Control green before and after each, zero `expectedFailure`, run from a
    copy under `$HOME` with `data/`, `.github/`, `metadata/`, `.gitignore`, the
    root Markdown and `docs/PROJECT_STATUS.md` carried across, `-B` with
    `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared before each run.
    """

    def test_the_command_publishes_the_headline_metric(self):
        """A skill score exists, it is in the artifact, and it is labelled.

        The one assertion the whole packet was written for. Not pinned to a
        value: what is asserted is that the number is finite, in range, and
        computed at the threshold the panel actually crosses.
        """

        summary = self.scored()
        document = self.published()

        self.assertEqual(summary["holdout_role"], "scoring")
        self.assertEqual(document["holdout_role"], "scoring")

        skill = document["metrics"]["by_tau"]["5"]["brier_skill_score"]
        self.assertTrue(-10.0 < skill <= 1.0)
        self.assertEqual(summary["brier_skill_score"]["5"], round(skill, 4))

        # Murphy: reliability and resolution reported separately, which is what
        # the contract asks the decomposition for.
        decomposition = document["metrics"]["by_tau"]["5"]["decomposition"]
        self.assertIn("reliability", decomposition)
        self.assertIn("resolution", decomposition)
        self.assertNotIn("ece", json.dumps(document))

    def test_every_selectable_model_runs_on_this_command(self):
        """One mapping, and this command reaches all of it.

        `MODEL_FACTORIES` is block 1's, shared rather than copied, so a fourth
        implementer becomes runnable here by being added there. Running each
        name end to end is what turns that from a claim about a dict into a
        claim about the command.
        """

        for name in sorted(cli_eval.MODEL_FACTORIES):
            with self.subTest(model=name):
                features = [FEATURE, "sofr_volume"]
                extra = []
                if cli_eval.MODEL_FACTORIES[name].needs_regime_variable:
                    features.append("on_rrp")
                    extra = ["--regime-variable", "on_rrp"]
                # The registry has to price whatever this run declares: the
                # gap is the maximum over the declared set's fields, and a
                # source the file does not carry is a refusal rather than a
                # zero.
                self.registry = declared_registry_file(
                    self.tmp, features=tuple(features)
                )
                report = self.tmp / f"{name}.json"
                code, _out, err = self.run_command(
                    *extra, model=name, features=features, report=report
                )
                self.assertEqual(code, 0, msg=f"{name} failed: {err.strip()}")
                document = json.loads(report.read_text(encoding="utf-8"))
                self.assertEqual(document["declaration"]["model"], name)

    def test_an_unknown_model_is_refused_and_writes_no_report(self):
        """A refusal must leave no artifact: a report on disk claims a run.

        And there is no fallback. A misspelled `--model` resolving to the
        climatology would publish a skill score of exactly zero -- the
        reference scored against itself -- under the name of a conditional
        model, with every other field correct.
        """

        code, _out, err = self.run_command(model="arxx")
        self.assertEqual(code, 2)
        self.assertIn("unknown --model", err)
        self.assertFalse(self.report_path.exists())

    def test_the_taus_come_from_the_thresholds_file_and_nowhere_else(self):
        """The declared family is Track A's, and this module carries no tau.

        Behavioural half: a thresholds file declaring something else is
        refused, so the flag is load-bearing rather than decorative. Source
        half: the literal is nowhere in the module, so a run cannot agree with
        the file by coincidence.
        """

        other = self.tmp / "other-thresholds.json"
        declared = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
        declared["taus_bp"] = [5, 10, 20, 60]
        other.write_text(json.dumps(declared), encoding="utf-8")

        code, _out, err = self.run_command(thresholds=other)
        self.assertEqual(code, 2)
        self.assertIn("5, 10, 20, and 50", err)
        self.assertFalse(self.report_path.exists())

        document = self.published()
        self.assertEqual(document["declaration"]["taus_bp"], [5.0, 10.0, 20.0, 50.0])

    def test_the_command_offers_no_purge_no_source_and_no_taus(self):
        """Three absences, and an absence is only guarded by a test asserting it.

        No behavioural test can catch a flag nobody passes, so this reads the
        parser. The gap follows from the declared features, the sources follow
        from the features, and the tau family comes from the file that declares
        it -- none of the three is a caller's to set by hand.
        """

        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        exceedance = command.choices["exceedance-backtest"]
        options = {
            option
            for action in exceedance._actions
            for option in action.option_strings
        }
        for banned in ("--purge", "--source", "--taus", "--tau", "--climatology"):
            self.assertNotIn(banned, options)

    def test_the_gap_follows_from_the_declared_features_and_reaches_the_numbers(self):
        """A wider gap costs origins and moves the pooled table.

        A relation between two runs rather than a literal: a command that
        reported a `purge_days` it did not pass on would hold the first
        assertion and fail the rest.
        """

        narrow = self.published()
        wide_path = self.tmp / "wide.json"
        self.registry = declared_registry_file(
            self.tmp, purge=9, features=(FEATURE,)
        )
        self.report_path = wide_path
        wide = self.published()

        self.assertGreater(wide["derived"]["purge_days"], narrow["derived"]["purge_days"])
        self.assertLess(wide["folds"]["count"], narrow["folds"]["count"])
        self.assertNotEqual(
            wide["metrics"]["by_tau"]["5"]["brier"],
            narrow["metrics"]["by_tau"]["5"]["brier"],
        )

    def test_the_artifact_is_the_publication_and_parses_strictly(self):
        """Required, written only on success, and readable by a strict reader.

        `log_score` is `inf` whenever a forecast put probability 0 on something
        that happened, which this panel produces. `json.dumps` writes that as
        `Infinity` and no strict reader accepts it, so the field is absent with
        its reason -- the number is unrepresentable, not uncomputed.
        """

        document = self.published()
        text = self.report_path.read_text(encoding="utf-8")
        self.assertNotIn("Infinity", text)
        self.assertNotIn("NaN", text)
        json.loads(text, parse_constant=self._no_constants)

        upper = document["metrics"]["by_tau"]["50"]
        self.assertNotIn("brier_skill_score", upper)
        self.assertIn("brier_skill_score", upper["unavailable"])
        self.assertEqual(upper["positives"], 0)

    @staticmethod
    def _no_constants(name):
        raise AssertionError(f"the artifact carries {name}, which is not JSON")

    def test_the_report_is_required(self):
        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        exceedance = command.choices["exceedance-backtest"]
        report = next(a for a in exceedance._actions if a.dest == "report")
        self.assertTrue(report.required)

    def test_the_model_has_no_default(self):
        """The sharpest instance of the rule, on the command it is sharpest on.

        On `event-holdout` a `--model` default would publish the baseline's
        numbers under a conditional model's name. Here it is worse: the
        climatology is *the reference the reported number is a ratio against*,
        so a run that fell back to it would report a skill score of exactly
        zero -- the reference scored against itself -- with every other field
        in the artifact correct and nothing disagreeing.

        Asserted on the parser, because a default changes no output for any
        caller who passes the flag, and every test in this class passes it. A
        mutation that gave `--model` a default of `climatology` left the whole
        suite green until this test existed.
        """

        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        for name in ("exceedance-backtest", "event-holdout"):
            with self.subTest(command=name):
                model = next(
                    a for a in command.choices[name]._actions if a.dest == "model"
                )
                self.assertTrue(model.required)
                self.assertIsNone(model.default)

    def test_this_command_reads_no_events_file(self):
        """It is the scoring holdout, so it knows nothing about event windows.

        The knowledge holdout is `event-holdout`'s, is scored once per window,
        and is never averaged into this table. A command that grew an
        `--events` flag would be one that could pool a window into an
        aggregate, which the contract forbids.
        """

        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        exceedance = command.choices["exceedance-backtest"]
        options = {
            option
            for action in exceedance._actions
            for option in action.option_strings
        }
        self.assertNotIn("--events", options)
        self.assertNotIn("--window", options)
        self.assertNotIn("--journal", options)


class SeamTests(unittest.TestCase):
    """The property "Decided: who owns the CLI" was written to get."""

    def test_adding_the_subcommand_required_no_edit_to_the_dispatcher(self):
        dispatcher = inspect.getsource(cli)
        for name in ("event-holdout", "event_holdout",
                     "exceedance-backtest", "exceedance_backtest"):
            self.assertNotIn(name, dispatcher)

    def test_the_dispatcher_nevertheless_offers_it(self):
        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        self.assertIn("event-holdout", command.choices)
        self.assertIn("exceedance-backtest", command.choices)

    def test_the_second_track_b_subcommand_landed_the_same_way(self):
        """The property is not that the file got an owner once.

        `exceedance-backtest` is the first command added since the split that
        is not the one the split was written for, so it is the first evidence
        that the seam holds for the next command rather than for the example.
        """

        args = cli.build_parser().parse_args(
            ["exceedance-backtest", "--panel", "p", "--thresholds", "t",
             "--registry", "r", "--feature", "spread_bps",
             "--decision-time", "16:30", "--model", "climatology",
             "--report", "o"]
        )
        self.assertIs(args.handler, cli_eval._exceedance_backtest)

    def test_the_handler_is_registered_by_this_track_module(self):
        args = cli.build_parser().parse_args(
            ["event-holdout", "--panel", "p", "--events", "e", "--thresholds", "t",
             "--registry", "r", "--journal", "j", "--feature", "spread_bps",
             "--decision-time", "16:30", "--model", "climatology"]
        )
        self.assertIs(args.handler, cli_eval._event_holdout)


if __name__ == "__main__":
    unittest.main()
