"""The pre-SOFR history study's source and its as-of reads (#129).

`frb_ddp` is the Board's Data Download Program: the H.15 effective federal
funds rate and the Policy Rates release's IOER. `repo_model.effr_history` turns
them into EFFR - IOER rows from December 2008 and pairs each label with what a
forecast of it would have read at its own decision instant.
"""

from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
import zipfile
from datetime import date, datetime, time
from pathlib import Path

from repo_model import effr_history, ingest
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((REPO / "metadata" / "sources.json").read_text())
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"


def _package(release: str, series: dict) -> bytes:
    """A DDP release package in the SDMX shape the Board serves."""

    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<message:MessageGroup xmlns:message="m" xmlns:frb="f" xmlns:kf="k">',
            '<frb:DataSet id="X">']
    for name, observations in series.items():
        body.append(f'<kf:Series SERIES_NAME="{name}" UNIT="Percent">')
        for when, value, status in observations:
            body.append(f'<frb:Obs OBS_STATUS="{status}" OBS_VALUE="{value}" TIME_PERIOD="{when}" />')
        body.append("</kf:Series>")
    body += ["</frb:DataSet>", "</message:MessageGroup>"]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(f"{release}_data.xml", "\n".join(body))
    return buffer.getvalue()


class FrbDdpParserTests(unittest.TestCase):
    def test_a_series_is_read_with_not_available_days_as_none(self):
        payload = _package("H15", {
            "RIFSPFF_N.D": [("2009-01-02", "0.10", "A")],
            "RIFSPFF_N.B": [("2009-01-01", "-9999", "ND"), ("2009-01-02", "0.15", "A")],
        })
        self.assertEqual(
            ingest.frb_ddp_series(payload, "H15", "RIFSPFF_N.B"),
            {date(2009, 1, 1): None, date(2009, 1, 2): 0.15},
        )

    def test_a_missing_or_repeated_series_is_refused(self):
        payload = _package("H15", {"RIFSPFF_N.D": [("2009-01-02", "0.10", "A")]})
        with self.assertRaisesRegex(ValueError, "0 times"):
            ingest.frb_ddp_series(payload, "H15", "RIFSPFF_N.B")

    def test_an_unparseable_value_is_refused(self):
        payload = _package("H15", {"RIFSPFF_N.B": [("2009-01-02", "x", "A")]})
        with self.assertRaisesRegex(ValueError, "neither a value"):
            ingest.frb_ddp_series(payload, "H15", "RIFSPFF_N.B")

    def test_an_empty_answer_is_not_saved_as_a_snapshot(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError, "not a zip"):
                ingest.fetch_frb_ddp(Path(root), "H15", downloader=lambda url: b"")
            self.assertEqual(list(Path(root).rglob("*")), [])

    def test_a_fetch_saves_the_package_unmodified_with_its_checksum(self):
        payload = _package("PRATES", {"RESBME_N.D": [("2009-01-02", "0.25", "A")]})
        seen = []
        with tempfile.TemporaryDirectory() as root:
            (artifact,) = ingest.fetch_frb_ddp(
                Path(root), "PRATES", downloader=lambda url: seen.append(url) or payload
            )
            self.assertEqual(artifact.source_id, ingest.FRB_DDP_SOURCE_ID)
            self.assertEqual(artifact.path.read_bytes(), payload)
            self.assertEqual(
                seen, ["https://www.federalreserve.gov/datadownload/Output.aspx?rel=PRATES&filetype=zip"]
            )
            self.assertTrue(artifact.path.with_suffix(".zip.manifest.json").exists())


def _alfred(path: Path) -> dict:
    out = {}
    with path.open() as handle:
        for row in csv.reader(handle):
            if row and row[0][:1].isdigit() and row[1] not in (".", ""):
                out[date.fromisoformat(row[0])] = float(row[1])
    return out


class FrbDdpRevisionTests(unittest.TestCase):
    """The revision statement in `metadata/sources.json` (`frb_ddp`), re-run.

    The tracked DDP packages agree with every tracked ALFRED vintage of DFF and
    IOER on every shared business-day observation: nothing has been restated.
    """

    @classmethod
    def setUpClass(cls):
        cls.effr, cls.ioer = effr_history.load_ddp_series(SNAPSHOTS / ingest.FRB_DDP_SOURCE_ID)

    def test_effr_matches_every_alfred_vintage_of_dff(self):
        paths = sorted((SNAPSHOTS / "alfred-dff").glob("*.csv")) + sorted(
            (SNAPSHOTS / "alfred-dff-first-print").glob("*.csv")
        )
        self.assertEqual(len(paths), 8)
        for path in paths:
            vintage = _alfred(path)
            shared = [day for day, value in self.effr.items() if value is not None and day in vintage]
            self.assertGreater(len(shared), 16000, path.name)
            self.assertEqual([day for day in shared if vintage[day] != self.effr[day]], [], path.name)

    def test_ioer_matches_every_alfred_vintage(self):
        paths = sorted((SNAPSHOTS / "alfred-ioer").glob("*.csv"))
        self.assertEqual(len(paths), 3)
        for path in paths:
            vintage = _alfred(path)
            shared = [day for day in self.ioer if day in vintage]
            self.assertGreater(len(shared), 3000, path.name)
            self.assertEqual([day for day in shared if vintage[day] != self.ioer[day]], [], path.name)


def _grid_rows(start: date, end: date, printed_through: date = None):
    """History rows on business days, EFFR rising a basis point a day.

    The H.15 prints through `printed_through` (default: the end of `end`'s
    quarter), so `quarter_end` can be read on every row.
    """

    if printed_through is None:
        month = 3 * ((end.month - 1) // 3) + 3
        printed_through = date(end.year + (month == 12), 1 if month == 12 else month + 1, 1)
    effr, ioer = {}, {}
    day = start
    level = 0.10
    while day <= printed_through:
        if day.weekday() < 5:
            effr[day] = round(level, 4)
            level += 0.01
        else:
            effr[day] = None
        ioer[day] = 0.25
        day = date.fromordinal(day.toordinal() + 1)
    weekly = {"reserve_balances": {}, "tga": {}}
    day = start
    while day <= end:
        if day.weekday() == 2:
            weekly["reserve_balances"][day] = 800.0 + day.toordinal() % 100
            weekly["tga"][day] = 100.0 + day.toordinal() % 50
        day = date.fromordinal(day.toordinal() + 1)
    return effr_history.history_rows(effr, ioer, weekly, start=start, end=end)


class HistoryRowsTests(unittest.TestCase):
    def test_a_row_is_a_business_day_with_its_spread_in_basis_points(self):
        rows = _grid_rows(date(2009, 6, 1), date(2009, 6, 12))
        self.assertEqual([row.date.weekday() for row in rows], [0, 1, 2, 3, 4] * 2)
        self.assertAlmostEqual(rows[0].spread_bps, -15.0)
        self.assertAlmostEqual(rows[1].spread_bps, -14.0)

    def test_weekly_inputs_carry_by_their_reference_date_only(self):
        rows = _grid_rows(date(2009, 6, 1), date(2009, 6, 12))
        by_day = {row.date: row for row in rows}
        # Mon and Tue of the first week precede any print.
        self.assertIsNone(by_day[date(2009, 6, 1)].values["reserve_balances"])
        wednesday = by_day[date(2009, 6, 3)].values["reserve_balances"]
        self.assertIsNotNone(wednesday)
        self.assertEqual(by_day[date(2009, 6, 9)].values["reserve_balances"], wednesday)
        self.assertNotEqual(by_day[date(2009, 6, 10)].values["reserve_balances"], wednesday)

    def test_calendar_columns_are_the_panels(self):
        from repo_model import data

        rows = _grid_rows(date(2009, 6, 1), date(2009, 6, 30))
        for row in rows:
            self.assertEqual(row.values["days_to_month_end"], data.days_to_month_end(row.date))
            self.assertEqual(row.values["tax_date"], data.tax_date(row.date))
        self.assertEqual([row.date for row in rows if row.values["quarter_end"]], [date(2009, 6, 30)])

    def test_quarter_end_on_the_print_calendar_agrees_with_the_panels_where_both_exist(self):
        from repo_model import data

        rows = _grid_rows(date(2018, 4, 2), date(2018, 12, 31))
        self.assertEqual(
            [row.date for row in rows if row.values["quarter_end"]],
            [row.date for row in rows if data.quarter_end(row.date)],
        )
        self.assertEqual(sum(row.values["quarter_end"] for row in rows), 3)

    def test_a_print_calendar_short_of_the_quarter_is_refused(self):
        with self.assertRaisesRegex(ValueError, "does not reach"):
            _grid_rows(date(2009, 6, 1), date(2009, 6, 26), printed_through=date(2009, 6, 26))


class HistoryReadTests(unittest.TestCase):
    """The as-of read of the history rows: the leakage test of `frb_ddp`.

    Written red first, before `effr_history` existed (ImportError). Recorded
    mutation: in `HistoryRule._latest`, `if self.availability(dates, fields,
    position) <= deadline:` mutated to `if True:`, so the read is the row before
    the scored day whatever its declared availability. Applied in a scratch
    copy: `test_every_history_pair_passes_the_independent_check` failed with
    `LookAheadError`, raised by the independent `HistoryRule.check` ("spread_bps
    for 2009-05-01 is public at 2009-05-04 16:15:00, after the 2009-05-01
    16:00:00 decision"); `test_effr_is_read_only_once_the_h15_has_posted_it` and
    `test_a_longer_horizon_moves_every_read_back` failed with `AssertionError`
    (the read was 2009-06-16); `test_the_independent_check_refuses_a_read_too_new`
    still passed.
    """

    def setUp(self):
        self.rows = _grid_rows(date(2009, 5, 1), date(2009, 7, 31))
        self.dates = [row.date for row in self.rows]

    def test_effr_is_read_only_once_the_h15_has_posted_it(self):
        rule = effr_history.HistoryRule(REGISTRY, decision_time=time(16, 0), horizon=1)
        scored = self.dates.index(date(2009, 6, 17))  # a Wednesday
        read = rule.read(self.dates, scored)
        self.assertEqual(read.decision_instant, datetime(2009, 6, 16, 16, 0))
        # Monday's EFFR posts on Tuesday at 16:15, after the 16:00 decision;
        # Friday's posted on Monday.
        self.assertEqual(self.dates[read.rows["spread_bps"]], date(2009, 6, 12))
        rule.check(self.dates, read)

    def test_a_longer_horizon_moves_every_read_back(self):
        rule = effr_history.HistoryRule(REGISTRY, decision_time=time(16, 0), horizon=3)
        scored = self.dates.index(date(2009, 6, 17))
        read = rule.read(self.dates, scored)
        self.assertEqual(read.decision_instant, datetime(2009, 6, 12, 16, 0))
        self.assertEqual(self.dates[read.rows["spread_bps"]], date(2009, 6, 10))
        rule.check(self.dates, read)

    def test_the_independent_check_refuses_a_read_too_new(self):
        rule = effr_history.HistoryRule(REGISTRY, decision_time=time(16, 0), horizon=1)
        scored = self.dates.index(date(2009, 6, 17))
        read = rule.read(self.dates, scored)
        rows = dict(read.rows)
        rows["spread_bps"] = self.dates.index(date(2009, 6, 15))
        with self.assertRaises(LookAheadError):
            rule.check(self.dates, read._replace(rows=rows))

    def test_every_history_pair_passes_the_independent_check(self):
        rule = effr_history.HistoryRule(REGISTRY, decision_time=time(16, 0), horizon=1)
        pool = effr_history.history_pairs(_StubDesign(), rule, self.rows)
        self.assertGreater(len(pool.xs), 30)
        for when, available in zip(pool.dates, pool.available_at):
            # A label is public when the H.15 posts it, a business day later.
            self.assertGreater(available, datetime.combine(when, time(16, 0)))


class _StubDesign:
    """The duck type `history_pairs` needs: the v1 design reads these."""

    tga = True

    def row(self, observation, tga_change):
        values = observation.values
        for name in ("reserve_balances", "tga", "days_to_month_end"):
            if values.get(name) is None:
                raise ValueError(name)
        return [observation.spread_bps, values["reserve_balances"], tga_change]


class PoolPublicTests(unittest.TestCase):
    """A pooled label must be public before the fit that reads it.

    Recorded mutation: in `require_pool_public`, `if latest >= cutoff:`
    mutated to `if False:`. Applied in a scratch copy,
    `test_a_label_not_public_before_the_last_training_day_is_refused` failed
    with `AssertionError` ("LookAheadError not raised").
    """

    def test_a_label_not_public_before_the_last_training_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            effr_history.require_pool_public(
                [datetime(2018, 4, 2, 16, 15), datetime(2018, 6, 1, 16, 15)], date(2018, 6, 1)
            )

    def test_a_pool_public_before_the_last_training_day_passes(self):
        effr_history.require_pool_public(
            [datetime(2018, 4, 2, 16, 15), datetime(2018, 4, 3, 16, 15)], date(2018, 6, 1)
        )


class EpisodeTests(unittest.TestCase):
    def test_an_episode_is_a_run_of_days_above_the_threshold(self):
        rows = _grid_rows(date(2009, 6, 1), date(2009, 6, 30))
        # The spread rises from -15 bp a basis point a business day.
        episodes = effr_history.episodes(rows, 5.0)
        self.assertEqual(len(episodes), 1)
        (episode,) = episodes
        self.assertEqual(episode["start"], "2009-06-30")
        self.assertEqual(episode["days"], 1)
        self.assertAlmostEqual(episode["peak_bps"], 6.0)

    def test_the_tracked_history_has_no_episode_at_either_headline_threshold(self):
        rows = effr_history.load_history_rows(SNAPSHOTS / ingest.FRB_DDP_SOURCE_ID, None)
        self.assertEqual(rows[0].date, effr_history.HISTORY_START)
        self.assertEqual(rows[-1].date, effr_history.HISTORY_END)
        self.assertEqual(effr_history.episodes(rows, 5.0), [])
        self.assertEqual(effr_history.episodes(rows, 10.0), [])
        self.assertLessEqual(max(row.spread_bps for row in rows), 0.0)


if __name__ == "__main__":
    unittest.main()
