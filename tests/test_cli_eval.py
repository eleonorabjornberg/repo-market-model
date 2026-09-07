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

The model is `baseline.climatology_exceedance`, and it is the honest one for a
knowledge holdout: the question the window asks is what a model that saw only
calm history says about a crisis it was never shown. On the fixture panel --
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
import inspect
import io
import json
import re
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import cli, cli_eval
from repo_model.contract import event_window_digest
from repo_model.event_eval import read_journal


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
SOURCE = "nyfed_sofr"
DECISION_TIME = "16:30"


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

    def run_command(self, *extra, events=None, thresholds=None, journal=None):
        """Invoke the real dispatcher. Returns `(exit_code, stdout, stderr)`."""

        argv = [
            "event-holdout",
            "--panel", str(self.panel),
            "--events", str(events or self.events),
            "--thresholds", str(thresholds or THRESHOLDS),
            "--registry", str(REGISTRY),
            "--journal", str(journal or self.journal),
            "--source", SOURCE,
            "--decision-time", DECISION_TIME,
            *extra,
        ]
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
        too short. The gap follows from which sources the features come from, so
        `--source` is how a caller changes it, and that change is legible.
        """

        parser = cli.build_parser()
        options = self._holdout_options(parser)
        for banned in ("--purge", "--purge-days", "--gap"):
            self.assertNotIn(banned, options, msg=f"{banned} is back")
        self.assertIn("--source", options)

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


class SeamTests(unittest.TestCase):
    """The property "Decided: who owns the CLI" was written to get."""

    def test_adding_the_subcommand_required_no_edit_to_the_dispatcher(self):
        dispatcher = inspect.getsource(cli)
        self.assertNotIn("event-holdout", dispatcher)
        self.assertNotIn("event_holdout", dispatcher)

    def test_the_dispatcher_nevertheless_offers_it(self):
        parser = cli.build_parser()
        command = next(a for a in parser._actions if a.dest == "command")
        self.assertIn("event-holdout", command.choices)

    def test_the_handler_is_registered_by_this_track_module(self):
        args = cli.build_parser().parse_args(
            ["event-holdout", "--panel", "p", "--events", "e", "--thresholds", "t",
             "--registry", "r", "--journal", "j", "--source", "s",
             "--decision-time", "16:30"]
        )
        self.assertIs(args.handler, cli_eval._event_holdout)


if __name__ == "__main__":
    unittest.main()
