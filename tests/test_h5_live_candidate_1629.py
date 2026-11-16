"""The live producer of (s3c-ann-net) (#1629; H5, registration follow-through; finding #1625).

`repo_model.h5_live.candidate_forecast` makes the registered candidate's 23 quantiles at h = 1..5 at the 18:00 New York decision instant,
from the panel as the live record has it on the decision day (real rows to the day before, placeholder rows for the decision day and its five
targets, `scripts/live_record.extend_panel`). What is pinned:

* **the frozen code's forecast, quantile for quantile.** At a fixed fixture day (2025-12-22, before the lockbox) the live forecast equals what
  the frozen walk of #1288 issues for that day and the SRF cap of #1255 puts on it: `spread_mr_state_calendar.walk` over the published panel
  with `AnnouncedTermTable`, `AnnouncedNetSizeTable` and `constant_states`, both arms as `scripts/s3c_announced_settlement_1288.extra_walks`
  runs them, then `s3c_candidate.capped_quantiles` at each target. Exact equality, no tolerance. The same walk, the same refit days, the same
  fit: the live producer adds no model of its own.
* **no look-ahead.** The forecast of a day does not move when every row after the decision day is changed (the published panel's later rows
  are not read), and the placeholder rows' own spreads are never read (`LookAheadError` from the as-of rule otherwise).
* **staleness of the IORB table.** The table of announced IORB changes is a tracked file; a rate change it does not list would be read as no
  change. `require_iorb_table_current` refuses (`StaleReadError`) a table whose rate in force on the last real day is not the rate the panel
  observed that day.
* **the candidate is logged.** `prospective_log.REGISTERED_CANDIDATES` names it, and a protocol block written for a day carries it
  on the 23-level grid for every lead (`live_record.protocol_for`).

Recorded mutation (the staleness guard is a new guard): in `h5_live.require_iorb_table_current`, the line
`if rate_bps != observed_bps:` changed to `if False:`. `StaleTableTests.test_a_table_that_misses_a_change_is_refused` then failed with
`AssertionError: StaleReadError not raised`. The look-ahead pin is the as-of rule's own guard (`asof.InformationRule`), not a new one.

The test was run first against a tree without `repo_model.h5_live` and failed with `ImportError: cannot import name 'h5_live' from 'repo_model'`.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import announced_iorb, h5_live, policy_events, prospective_log, s3c_announced, s3c_candidate, s3c_net  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import StaleReadError  # noqa: E402
from repo_model.cli import main as cli_main  # noqa: E402
from repo_model.data import DailyObservation, load_daily_panel  # noqa: E402
from repo_model.decision_instant import DECISION_TIME  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)

FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
CUTOFF = "2026-09-08T21:31:42+00:00"
REGISTRY = ROOT / "metadata" / "sources.json"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
#: Its five targets (2025-12-23 to 2025-12-30) fall before the lockbox; the SRF is at full allotment from 2025-12-11, so the cap binds on them.
DECISION_DAY = date(2025, 12, 22)


def _script(name):
    spec = importlib.util.spec_from_file_location(f"h5_live_test_{name}", ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Setup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live = _script("live_record")
        cls.frozen = _script("s3c_announced_settlement_1288")
        cls.tmp = tempfile.mkdtemp()
        panel = Path(cls.tmp) / "funding_panel.csv"
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli_main(["build", "--raw-root", str(FIXTURES), "--output", str(panel), "--build-cutoff", CUTOFF,
                             "--decision-time", DECISION_TIME.isoformat(timespec="seconds")])
        if code != 0:
            raise RuntimeError("the fixture panel did not build")
        cls.pit = panel.with_name(panel.stem + "_point_in_time.csv")
        cls.rows = load_daily_panel(panel)
        cls.records = cls.live.auction_records(FIXTURES)
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.splits = load_split_declaration(SPLITS)
        cls.real = [row for row in cls.rows if row.date < DECISION_DAY]
        cls.extended, cls.targets = cls.live.extend_panel(cls.real, DECISION_DAY, max(sp.HORIZONS), cls.pit, cls.records)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def forecast(self, extended=None, **kwargs):
        if extended is None and not kwargs:
            if "_made" not in Setup.__dict__:  # one walk for the tests that read the same day
                Setup._made = self._forecast()
            return Setup._made
        return self._forecast(extended, **kwargs)

    def _forecast(self, extended=None, **kwargs):
        return h5_live.candidate_forecast(
            self.extended if extended is None else extended, DECISION_DAY, registry=self.registry, splits=self.splits,
            auction_records=self.records, **kwargs)


class FrozenAgreementTests(Setup):
    def test_the_live_forecast_is_the_frozen_walks_quantile_for_quantile(self):
        f = self.frozen
        panel = [row for row in self.rows if row.date <= f.LAST_DAY]
        register = policy_events.load_register()
        results = f.load_results()
        auctions = f.m1273.load_auctions()
        iorb = announced_iorb.load_announcements(f.c.IORB_TABLE)
        days = [row.date for row in panel if row.date <= DECISION_DAY]
        walk = sc.walk(
            panel, days, s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=DECISION_TIME),
            s3c_net.constant_states(panel), (s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM),
            sizes=s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=DECISION_TIME),
            registry=self.registry, decision_time=DECISION_TIME, splits=self.splits)
        raw = walk.forecasts[s3c_announced.ANN_NET_ARM.name][DECISION_DAY]
        position = {row.date: i for i, row in enumerate(panel)}
        instant = datetime.combine(DECISION_DAY, DECISION_TIME)
        expected = {h: s3c_candidate.capped_quantiles(raw[h], register, instant, panel[position[DECISION_DAY] + h].date)
                    for h in sp.HORIZONS}
        got = self.forecast()
        self.assertEqual(set(got), set(sp.HORIZONS))
        for h in sp.HORIZONS:
            self.assertEqual(len(got[h]), len(sp.GRID))
            with self.subTest(h=h):
                self.assertEqual(got[h], expected[h])
        # the cap is live on this day: at least one lead differs from the uncapped (s3)
        self.assertTrue(any(expected[h] != list(raw[h]) for h in sp.HORIZONS), "the fixture day does not exercise the cap")


class NoLookAheadTests(Setup):
    def test_rows_after_the_decision_day_are_not_read(self):
        # change the spread of every placeholder row: a read of one would move the forecast, or the as-of rule would raise
        index = [row.date for row in self.extended].index(DECISION_DAY)
        moved = list(self.extended)
        for i in range(index + 1, len(moved)):
            moved[i] = DailyObservation(date=moved[i].date, values=dict(moved[i].values, spread_bps=moved[i].values.get("spread_bps", 0.0) + 40.0))
        self.assertEqual(self.forecast(moved), self.forecast())

    def test_a_panel_that_misses_the_day_before_is_refused(self):
        with self.assertRaises(ValueError):
            self.forecast(self.extended[:len(self.real) - 1] + self.extended[len(self.real):])


class StaleTableTests(Setup):
    def table(self):
        return announced_iorb.load_announcements(h5_live.IORB_TABLE)

    def test_the_tracked_table_is_current_on_every_day_of_the_published_panel(self):
        table = self.table()
        for i in range(1, len(self.rows), 37):
            h5_live.require_iorb_table_current(self.rows[: i + 1], table)

    def test_a_table_that_misses_a_change_is_refused(self):
        """The 2025-12-10 cut takes effect on 2025-12-11: a table that stops before it reads the old rate on the day the panel saw the new one."""
        table = tuple(a for a in self.table() if a.announced_at.date() < date(2025, 12, 10))
        with self.assertRaises(StaleReadError):
            h5_live.require_iorb_table_current(self.real, table)

    def test_the_forecast_refuses_a_stale_table(self):
        table = tuple(a for a in self.table() if a.announced_at.date() < date(2025, 12, 10))
        with self.assertRaises(StaleReadError):
            self.forecast(iorb_table=table)


class LoggedTests(Setup):
    def test_the_candidate_is_registered_for_logging(self):
        self.assertEqual(prospective_log.REGISTERED_CANDIDATES, ("sc_s3c_ann_net",))
        self.assertEqual(h5_live.CANDIDATE_ID, "sc_s3c_ann_net")

    def test_a_protocol_block_carries_the_candidate_on_the_grid(self):
        written_at = datetime.combine(DECISION_DAY, time(19, 0), tzinfo=self.live.EASTERN)
        got = {"sc_s3c_ann_net": self.forecast()}
        block = self.live.protocol_for(self.extended, DECISION_DAY, self.registry, self.splits, written_at, candidates=got)
        self.assertEqual(set(block["candidates"]), {"sc_s3c_ann_net"})
        for h in sp.HORIZONS:
            self.assertEqual(block["candidates"]["sc_s3c_ann_net"][str(h)], got["sc_s3c_ann_net"][h])
        prospective_log.validate_protocol_block(block, DECISION_DAY)

    def test_a_block_without_a_registered_candidate_is_refused(self):
        written_at = datetime.combine(DECISION_DAY, time(19, 0), tzinfo=self.live.EASTERN)
        with self.assertRaises(ValueError):
            self.live.protocol_for(self.extended, DECISION_DAY, self.registry, self.splits, written_at)


if __name__ == "__main__":
    unittest.main()
