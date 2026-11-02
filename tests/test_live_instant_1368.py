"""The live code reads the decision instant in force, and a 16:00 file is still read at 16:00 (#1368).

Hypothesis and step: H5 groundwork G3 (the live record), the step after #1313 in moving the decision instant to 18:00 ET
(her ruling of 29 October 2026, ledger item 77; #1323's Q2, default 1). `scripts/live_record.py` took its `DECISION`
from the frozen `pressure_model_v1.DECISION` (16:00) and built with `--decision-time 16:00:00`; `scripts/live_raw.py`
and `scripts/live_monitor.py` typed 16:00 too. They now read `repo_model.decision_instant`. A record, a panel or a
file made at 16:00 is a record of that instant: every reader of one takes the instant the file declares, never the one
in force.

Red first: this file was committed before the change and failed on `live.LEGACY_DECISION`, `live.instant_of`,
`live.declared_decision_time` and `raw.decision_time_for_day` (`AttributeError`) and on `live.DECISION == time(16, 0)`.

**Recorded mutations** (2 November 2026), each applied to the tree, confirmed by grep, the class named run, then reverted:

1. `scripts/live_record.py`, `DECISION = di.DECISION_TIME` changed to `DECISION = v1.DECISION`.
   `ConstantTests.test_the_live_code_decides_at_the_instant_in_force` then failed with `AssertionError`
   (`datetime.time(16, 0) != datetime.time(18, 0)`), `ConstantTests.test_a_days_record_declares_eighteen_hundred_new_york`
   with `AssertionError` (`'2026-11-02T16:00:00-05:00' != '2026-11-02T18:00:00-05:00'`), and
   `RuleTests.test_every_rule_the_record_builds_is_at_eighteen_hundred` with `AssertionError` (the recorded rules were at 16:00).
2. `scripts/live_record.py`, `declared_decision_time`: the line `return moment.astimezone(EASTERN).timetz().replace(tzinfo=None)`
   changed to `return DECISION`. `DeclaredInstantTests.test_a_record_made_at_sixteen_hundred_is_read_at_sixteen_hundred`
   then failed with `AssertionError` (`datetime.time(18, 0) != datetime.time(16, 0)`), as did `RawPanelTests` and the
   17:30 subtest of `test_a_published_clock_is_read_at_the_record_but_never_after_it` (`(True, True) != (False, True)`).
3. `scripts/live_raw.py`, `decision_time_for_day`: the line
   `return _script("live_record").declared_decision_time(json.loads(path.read_text(encoding="utf-8")))` replaced by `return None`. `RawPanelTests.test_a_day_logged_at_sixteen_hundred_is_built_at_sixteen_hundred` then failed
   with `AssertionError` (`None != datetime.time(16, 0)`).
"""

from __future__ import annotations

import importlib.util
import io
import json
import contextlib
import shutil
import tempfile
import unittest
from datetime import date, datetime, time
from pathlib import Path
from unittest import mock

from repo_model import asof, decision_instant as di
from repo_model.data import load_daily_panel
from repo_model.evaluation_splits import load_split_declaration

from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REGISTRY = ROOT / "metadata" / "sources.json"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"


def _script(name):
    spec = importlib.util.spec_from_file_location(f"instant_1368_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


live = _script("live_record")
raw = _script("live_raw")
monitor = _script("live_monitor")


class ConstantTests(unittest.TestCase):
    def test_the_live_code_decides_at_the_instant_in_force(self):
        self.assertEqual(live.DECISION, di.DECISION_TIME)
        self.assertEqual(live.DECISION, time(18, 0))

    def test_the_earlier_instant_is_named_for_the_readers_of_old_files(self):
        self.assertEqual(live.LEGACY_DECISION, di.LEGACY_DECISION_TIME)
        self.assertEqual(live.LEGACY_DECISION, time(16, 0))

    def test_a_days_record_declares_eighteen_hundred_new_york(self):
        # Before and after the end of daylight saving time on 1 November 2026.
        for day, offset in ((date(2026, 10, 30), "-04:00"), (date(2026, 11, 2), "-05:00")):
            with self.subTest(day=day):
                self.assertEqual(live.instant_of(day).isoformat(), f"{day}T18:00:00{offset}")

    def test_the_panel_is_built_at_the_instant_in_force(self):
        seen = []
        with mock.patch.object(live, "_cli", lambda argv: seen.append(argv) or ""):
            live.build(Path("RAW"), Path("PANEL"), datetime(2026, 11, 2, 23, 5, tzinfo=live.EASTERN))
        self.assertEqual(seen[0][seen[0].index("--decision-time") + 1], di.DECISION_TIME_SECONDS_TEXT)
        self.assertEqual(di.DECISION_TIME_SECONDS_TEXT, "18:00:00")

    def test_the_other_live_readers_hold_no_clock_of_their_own(self):
        self.assertEqual(raw.DECISION_TIME, di.DECISION_TIME_SECONDS_TEXT)
        # The monitor's replay reads the development record, a 16:00 file.
        self.assertEqual(monitor.DECISION_TIME, di.LEGACY_DECISION_TIME)


class DeclaredInstantTests(unittest.TestCase):
    """A file is read at the instant it declares, not the one in force."""

    def test_a_record_made_at_sixteen_hundred_is_read_at_sixteen_hundred(self):
        for text in ("2026-10-07T16:00:00-04:00", "2026-11-02T16:00:00-05:00"):
            with self.subTest(text=text):
                self.assertEqual(live.declared_decision_time({"decision_instant": text}), time(16, 0))

    def test_a_record_made_at_eighteen_hundred_is_read_at_eighteen_hundred(self):
        for text in ("2026-10-07T18:00:00-04:00", "2026-11-02T18:00:00-05:00"):
            with self.subTest(text=text):
                self.assertEqual(live.declared_decision_time({"decision_instant": text}), time(18, 0))

    def test_an_instant_in_another_zone_is_read_in_new_york(self):
        self.assertEqual(live.declared_decision_time({"decision_instant": "2026-11-02T23:00:00+00:00"}), time(18, 0))

    def test_a_record_with_no_instant_is_refused(self):
        with self.assertRaises(ValueError):
            live.declared_decision_time({})

    def test_a_published_clock_is_read_at_the_record_but_never_after_it(self):
        """A field public at 17:30 the day before is read by a record that declares 18:00, not by one that declares 16:00.

        And a field public at 18:01 is read by neither: the record reads nothing published after its own instant.
        """

        eighteen = live.declared_decision_time({"decision_instant": "2026-11-02T18:00:00-05:00"})
        sixteen = live.declared_decision_time({"decision_instant": "2026-10-07T16:00:00-04:00"})
        day = date(2026, 11, 2)
        for stamp, readable_at in ((time(17, 30), (False, True)), (time(18, 1), (False, False)), (time(15, 59), (True, True))):
            with self.subTest(stamp=stamp):
                moment = datetime.combine(day, stamp)
                self.assertEqual(
                    (moment <= datetime.combine(day, sixteen), moment <= datetime.combine(day, eighteen)),
                    readable_at,
                )


class RuleTests(unittest.TestCase):
    """The rules the record builds are at the instant in force."""

    DECISION_DAY = date(2019, 3, 1)
    LAST_ROW = date(2019, 3, 15)

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.panel = Path(cls.tmp) / "funding_panel.csv"
        with contextlib.redirect_stdout(io.StringIO()):
            code = live_cli(["build", "--raw-root", str(FIXTURES), "--output", str(cls.panel),
                             "--build-cutoff", CUTOFF, "--decision-time", di.DECISION_TIME_SECONDS_TEXT])
        if code != 0:
            raise RuntimeError("the fixture panel did not build")
        cls.pit = cls.panel.with_name(cls.panel.stem + "_point_in_time.csv")
        lines = cls.panel.read_text(encoding="utf-8").splitlines(keepends=True)
        column = lines[0].rstrip("\r\n").split(",").index("date")
        short = Path(cls.tmp) / "short.csv"
        short.write_text(lines[0] + "".join(
            line for line in lines[1:] if date.fromisoformat(line.split(",")[column]) <= cls.LAST_ROW),
            encoding="utf-8")
        cls.rows = load_daily_panel(short)
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.splits = load_split_declaration(SPLITS)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_every_rule_the_record_builds_is_at_eighteen_hundred(self):
        made = []
        real = asof.InformationRule

        def recording(*args, **kwargs):
            made.append(kwargs.get("decision_time"))
            return real(*args, **kwargs)

        cut = [row for row in self.rows if row.date < self.DECISION_DAY]
        extended, _ = live.extend_panel(cut, self.DECISION_DAY, 1, self.pit, _auctions())
        with mock.patch.object(live, "InformationRule", recording):
            live.baseline_forecasts(extended, 1, self.registry, self.splits, (5.0, 10.0))
        self.assertTrue(made)
        self.assertEqual(set(made), {time(18, 0)})


class OpenQuestionTests(unittest.TestCase):
    """What the live path does at 18:00 with v1's frozen features: it refuses, and it is not settled here (#1368).

    `treasury_bill_rates` is declared available at 16:30 on its own day (`metadata/sources.json`), so at 18:00 the
    as-of rule serves v1's `tbill_4w` and `tbill_13w` from the decision day's own row. The live panel's real rows end on
    the day before the decision day and the decision row is a placeholder that carries only the calendar and the
    scheduled settlements, so `require_reads_on_real_rows` raises `LookAheadError`: the guard holds and a live run at
    18:00 would stop at it. Making the decision row carry the same-day bill rates changes what the published model
    reads live (#1323's Q3), so it is a question for Eleonora and not settled in code. This test pins the refusal; the
    change that settles the question flips it.
    """

    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.tmp = tempfile.mkdtemp()
        panel = Path(cls.tmp) / "funding_panel.csv"
        with contextlib.redirect_stdout(io.StringIO()):
            code = live_cli(["build", "--raw-root", str(FIXTURES), "--output", str(panel),
                             "--build-cutoff", CUTOFF, "--decision-time", di.DECISION_TIME_SECONDS_TEXT])
        if code != 0:
            raise RuntimeError("the fixture panel did not build")
        cls.rows = load_daily_panel(panel)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_decision_row_is_not_read_for_the_bill_rates_at_eighteen_hundred(self):
        from repo_model.splits import LookAheadError

        index = len(self.rows) - 1
        rule = asof.InformationRule(self.registry, live.V1_FEATURES[1], decision_time=live.DECISION, horizon=1)
        with self.assertRaisesRegex(LookAheadError, "tbill_"):
            live.require_reads_on_real_rows(self.rows, rule, index, index - 2)

    def test_the_same_reads_are_on_real_rows_at_sixteen_hundred(self):
        index = len(self.rows) - 1
        rule = asof.InformationRule(self.registry, live.V1_FEATURES[1], decision_time=live.LEGACY_DECISION, horizon=1)
        live.require_reads_on_real_rows(self.rows, rule, index, index - 2)


class RawPanelTests(unittest.TestCase):
    def test_the_outcome_panel_is_built_at_the_instant_in_force_by_default(self):
        argv = raw.build_argv(Path("R"), Path("P"), "2026-11-02T23:05:00+00:00")
        self.assertEqual(argv[argv.index("--decision-time") + 1], "18:00:00")

    def test_a_given_instant_is_the_one_built_at(self):
        argv = raw.build_argv(Path("R"), Path("P"), "2026-10-06T21:31:00+00:00", decision_time=time(16, 0))
        self.assertEqual(argv[argv.index("--decision-time") + 1], "16:00:00")

    def _log(self, tmp, day, text):
        directory = Path(tmp) / "live"
        directory.mkdir(exist_ok=True)
        (directory / f"{day}.json").write_text(json.dumps({"decision_day": day, "decision_instant": text}), encoding="utf-8")

    def test_a_day_logged_at_sixteen_hundred_is_built_at_sixteen_hundred(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._log(tmp, "2026-10-07", "2026-10-07T16:00:00-04:00")
            self._log(tmp, "2026-11-03", "2026-11-03T18:00:00-05:00")
            self.assertEqual(raw.decision_time_for_day(Path(tmp), date(2026, 10, 7)), time(16, 0))
            self.assertEqual(raw.decision_time_for_day(Path(tmp), date(2026, 11, 3)), time(18, 0))

    def test_a_day_with_no_record_is_built_at_the_instant_in_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(raw.decision_time_for_day(Path(tmp), date(2026, 10, 7)))
            self.assertIsNone(raw.decision_time_for_day(None, date(2026, 10, 7)))


FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
CUTOFF = "2026-09-08T21:31:42+00:00"


def live_cli(argv):
    from repo_model.cli import main

    return main(argv)


_AUCTIONS = []


def _auctions():
    if not _AUCTIONS:
        _AUCTIONS.extend(live.auction_records(FIXTURES))
    return _AUCTIONS


if __name__ == "__main__":
    unittest.main()
