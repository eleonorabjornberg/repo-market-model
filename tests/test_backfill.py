"""The back-filled repo-rate history is training history only (#430).

Eleonora's ruling of 8 October 2026 on #374: the New York Fed's back-filled SOFR, TGCR and BGCR
history, 2014-08-22 to 2018-03-29, may train a model. It is never an as-of input at a scored decision
instant and no scored day is a back-filled day. `repo_model.backfill.require_training_only` is the
guard; `scripts/backfill_history.py run` calls it after every backtest.

Mutation record
---------------
Red first: the guard tests were written against `require_training_only` before it refused
anything (its body was `return`) and failed with `AssertionError: LookAheadError not raised`. Then,
with the guard in place, one mutation was run in a disposable copy under `PYTHONDONTWRITEBYTECODE=1`,
`python3 -B`, CPython 3.11, unmutated control green before and after, the mutated line confirmed
applied by grep and restored before the next run:

* `src/repo_model/backfill.py`, in `require_training_only`:
  `if day < FIRST_PUBLISHED:` replaced by `if False:`. `RefusesBackfilledDays.test_a_backfilled_scored_day_is_refused`,
  `test_a_backfilled_feature_date_is_refused` and `test_the_day_before_the_first_published_day_is_refused`
  failed with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import hashlib
import io
import json
import unittest
import zipfile
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from repo_model import backfill, ingest
from repo_model.baseline import persistence_logistic_exceedance, rolling_exceedance_backtest
from repo_model.baseline import ScoredFold
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tests" / "fixtures" / "snapshots" / "backfill_2014_2018"


def _snapshot():
    manifests = sorted((SNAPSHOT / backfill.BACKFILL_SOURCE_ID).glob("*.manifest.json"))
    assert len(manifests) == 1
    return ingest.load_snapshot_manifest(manifests[0])


def _workbook(volume_rows, rate_rows) -> bytes:
    """A minimal workbook with the two sheets `parse_workbook` reads (dates as Excel serials)."""

    def sheet(rows):
        body = "".join(
            f'<row r="{n}">' + "".join(f'<c r="{c}{n}"><v>{v}</v></c>' for c, v in zip("ABCD", row)) + "</row>"
            for n, row in enumerate(rows, start=3)
        )
        return (
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
            '<row r="2"><c r="A2" t="s"><v>0</v></c></row>' + body + "</sheetData></worksheet>"
        )

    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as book:
        book.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets>'
            '<sheet name="Volumes" sheetId="1" r:id="rId1"/><sheet name="VWM Rates" sheetId="2" r:id="rId2"/>'
            "</sheets></workbook>",
        )
        book.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Target="worksheets/sheet2.xml"/></Relationships>',
        )
        book.writestr("xl/sharedStrings.xml", f'<sst xmlns="{ns}"><si><t>Date</t></si></sst>')
        book.writestr("xl/worksheets/sheet1.xml", sheet(volume_rows))
        book.writestr("xl/worksheets/sheet2.xml", sheet(rate_rows))
    return buffer.getvalue()


def _serial(day: date) -> int:
    return (day - date(1899, 12, 30)).days


def _fold(scored: date, feature: date, start: date = date(2014, 8, 22)) -> ScoredFold:
    return ScoredFold(
        train_start=start, train_end=feature, train_rows=70, feature_date=feature, scored_date=scored
    )


class TheSavedWorkbook(unittest.TestCase):
    def test_it_matches_its_manifest_and_names_its_origin(self):
        artifact = _snapshot()
        self.assertEqual(hashlib.sha256(artifact.path.read_bytes()).hexdigest(), artifact.sha256)
        self.assertTrue(artifact.url.startswith("https://www.newyorkfed.org/medialibrary/media/markets/"))
        self.assertEqual(artifact.source_id, backfill.BACKFILL_SOURCE_ID)

    def test_it_holds_the_back_filled_days_and_stops_before_the_api(self):
        days = backfill.parse_workbook(_snapshot().path.read_bytes())
        self.assertEqual(days[0].day, date(2014, 8, 22))
        self.assertEqual(days[-1].day, date(2018, 3, 29))
        self.assertLess(days[-1].day, backfill.FIRST_PUBLISHED)
        self.assertEqual(len(days), 899)
        first = days[0]
        self.assertEqual(first.rates, {"tgcr": 0.05, "bgcr": 0.05, "sofr": 0.06})
        self.assertEqual(first.volumes, {"tgcr": 234.0, "bgcr": 316.0, "sofr": 617.0})
        self.assertEqual([d.day for d in days], sorted({d.day for d in days}))


class ReadingTheWorkbook(unittest.TestCase):
    def test_rates_are_whole_basis_points_read_as_percent(self):
        day = date(2016, 9, 30)
        days = backfill.parse_workbook(
            _workbook([(_serial(day), 300, 400, 500)], [(_serial(day), 41, 42, 43)])
        )
        self.assertEqual(days[0].rates, {"tgcr": 0.41, "bgcr": 0.42, "sofr": 0.43})
        self.assertEqual(days[0].volumes, {"tgcr": 300.0, "bgcr": 400.0, "sofr": 500.0})

    def test_a_day_the_api_already_serves_is_not_back_filled(self):
        day = backfill.FIRST_PUBLISHED
        with self.assertRaises(ValueError):
            backfill.parse_workbook(_workbook([(_serial(day), 1, 2, 3)], [(_serial(day), 1, 2, 3)]))

    def test_sheets_that_disagree_on_the_dates_are_refused(self):
        a, b = date(2016, 9, 29), date(2016, 9, 30)
        with self.assertRaises(ValueError):
            backfill.parse_workbook(_workbook([(_serial(a), 1, 2, 3)], [(_serial(b), 1, 2, 3)]))

    def test_a_missing_series_is_refused(self):
        day = date(2016, 9, 30)
        with self.assertRaises(ValueError):
            backfill.parse_workbook(_workbook([(_serial(day), 1, 2)], [(_serial(day), 1, 2, 3)]))

    def test_the_documents_are_read_by_the_standard_parser_with_no_percentile(self):
        days = backfill.parse_workbook(_snapshot().path.read_bytes())
        documents = backfill.nyfed_documents(days)
        self.assertEqual(sorted(documents), [(n, k) for n in ("bgcr", "sofr", "tgcr") for k in ("rate", "volume")])
        retrieved = datetime(2026, 10, 8, tzinfo=timezone.utc).isoformat()
        for (name, kind), payload in documents.items():
            artifact = ingest.SnapshotArtifact(
                source_id=f"nyfed_{name}",
                path=Path("unused"),
                retrieved_at=retrieved,
                sha256=hashlib.sha256(payload).hexdigest(),
                url=f"{ingest.NYFED_BASE}/{name}/search.json?startDate=2014-08-22&endDate=2018-03-29&type={kind}",
                byte_count=len(payload),
            )
            observations = ingest._nyfed_rows(artifact, payload)
            self.assertEqual(len(observations), len(days))
            self.assertEqual({o.series_id for o in observations}, {name.upper() if kind == "rate" else f"{name.upper()}_volume"})
        self.assertIn("percentRate", json.loads(documents[("sofr", "rate")])["refRates"][0])
        self.assertNotIn("percentPercentile25", json.loads(documents[("sofr", "rate")])["refRates"][0])


class ThePrefix(unittest.TestCase):
    def test_it_counts_the_rows_before_the_first_published_day(self):
        dates = [date(2018, 3, 28), date(2018, 3, 29), date(2018, 4, 3), date(2018, 4, 4)]
        self.assertEqual(backfill.prefix_length(dates), 2)
        self.assertEqual(backfill.prefix_length(dates[2:]), 0)

    def test_dates_out_of_order_are_refused(self):
        with self.assertRaises(ValueError):
            backfill.prefix_length([date(2018, 3, 29), date(2018, 3, 28)])


class RefusesBackfilledDays(unittest.TestCase):
    def test_folds_scored_on_published_days_pass_with_a_back_filled_training_window(self):
        folds = [_fold(date(2018, 6, 29), date(2018, 6, 27)), _fold(date(2018, 7, 2), date(2018, 6, 28))]
        backfill.require_training_only(folds, where="test")

    def test_a_backfilled_scored_day_is_refused(self):
        with self.assertRaises(LookAheadError) as caught:
            backfill.require_training_only([_fold(date(2018, 3, 29), date(2018, 3, 27))], where="test")
        self.assertIn("scored day", str(caught.exception))
        self.assertIn("2018-03-29", str(caught.exception))

    def test_a_backfilled_feature_date_is_refused(self):
        with self.assertRaises(LookAheadError) as caught:
            backfill.require_training_only([_fold(date(2018, 4, 5), date(2018, 3, 29))], where="test")
        self.assertIn("feature date", str(caught.exception))

    def test_the_day_before_the_first_published_day_is_refused(self):
        day = backfill.FIRST_PUBLISHED - timedelta(days=1)
        with self.assertRaises(LookAheadError):
            backfill.require_training_only([_fold(date(2018, 6, 29), day)], where="test")
        backfill.require_training_only([_fold(backfill.FIRST_PUBLISHED, backfill.FIRST_PUBLISHED)], where="test")


class RefusesFitsBeforeThePostingInstant(unittest.TestCase):
    """A fit that trains on back-filled values needs the workbook's posting instant declared (#572).

    `docs/decisions/information-set.md` (draft amendment): no back-filled value is used as training
    history before the Bank's first posting of the workbook is established. The posting instant is
    declared in `metadata/backfill_posting.json`, `null` today, so every fit whose training window
    reaches before `FIRST_PUBLISHED` is refused. Once it is declared, a fit is refused when its
    training end is before the start of the day of that instant.

    Red first: written before `require_posting_established` existed (`AttributeError`).

    Mutation record. In a `git archive` copy of the tree under /tmp, CPython 3.11 (`/opt/rmm-venv`),
    this class run alone, unmutated control green before and after, the mutated line confirmed
    applied by grep. In `backfill.require_posting_established` the refusal condition
    `if posting_instant is None or posting_instant > start:` was mutated to `if False:`. Killed, 4 failures, all
    `AssertionError: LookAheadError not raised`: `test_an_undeclared_posting_instant_refuses_every_back_filled_fit`,
    `test_a_fit_ending_before_the_posting_instant_is_refused`,
    `test_a_fit_ending_on_the_day_of_the_posting_is_refused` and `test_one_early_fit_among_many_is_refused`.
    """

    POSTED = datetime(2018, 5, 1, 12, 0)

    def test_an_undeclared_posting_instant_refuses_every_back_filled_fit(self):
        with self.assertRaises(LookAheadError) as caught:
            backfill.require_posting_established(
                [_fold(date(2018, 6, 29), date(2018, 6, 27))], None, where="test"
            )
        self.assertIn("posting instant", str(caught.exception))
        self.assertIn("2018-06-27", str(caught.exception))

    def test_a_fit_ending_before_the_posting_instant_is_refused(self):
        with self.assertRaises(LookAheadError):
            backfill.require_posting_established(
                [_fold(date(2018, 5, 1), date(2018, 4, 30))], self.POSTED, where="test"
            )

    def test_a_fit_ending_on_the_day_of_the_posting_is_refused(self):
        # The instant may fall after that day's decision, so the day itself is not enough.
        with self.assertRaises(LookAheadError):
            backfill.require_posting_established(
                [_fold(date(2018, 5, 2), date(2018, 5, 1))], self.POSTED, where="test"
            )
        backfill.require_posting_established(
            [_fold(date(2018, 5, 2), date(2018, 5, 1))], datetime(2018, 5, 1, 0, 0), where="test"
        )

    def test_a_fit_ending_after_the_posting_day_passes(self):
        backfill.require_posting_established(
            [_fold(date(2018, 6, 29), date(2018, 6, 27))], self.POSTED, where="test"
        )

    def test_one_early_fit_among_many_is_refused(self):
        folds = [_fold(date(2018, 6, 29), date(2018, 6, 27)), _fold(date(2018, 4, 5), date(2018, 4, 4))]
        with self.assertRaises(LookAheadError):
            backfill.require_posting_established(folds, self.POSTED, where="test")

    def test_a_fit_on_published_days_only_needs_no_posting_instant(self):
        published = _fold(date(2018, 6, 29), date(2018, 6, 27), start=backfill.FIRST_PUBLISHED)
        backfill.require_posting_established([published], None, where="test")


    def test_a_declared_instant_is_read_and_a_malformed_one_refused(self):
        import tempfile

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "p.json"
            path.write_text(json.dumps({"posting_instant": "2018-05-01T12:00:00"}), encoding="utf-8")
            self.assertEqual(backfill.load_posting_instant(path), self.POSTED)
            for bad in ({}, {"posting_instant": "May 2018"}, {"posting_instant": 5}):
                path.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(ValueError):
                    backfill.load_posting_instant(path)

    def test_the_run_script_applies_it(self):
        text = (ROOT / "scripts" / "backfill_history.py").read_text(encoding="utf-8")
        self.assertIn("backfill.require_posting_established(report.folds", text)


class TheRuledPostingInstant(unittest.TestCase):
    """The workbook is public from 17 May 2018 (Eleonora, 13 October 2026, #633).

    Her ruling (PR #661, comment 6146010089, relayed by the orchestrating session): every value of the
    TGCR/BGCR/SOFR back-fill workbook is public from 17 May 2018, one `posting_instant` for all three
    series, its source the research comment 6145957978; no value is read as of a decision before that
    date, and pre-May-2018 vintages are not used. `metadata/backfill_posting.json` declares it, and a fit
    whose training ends before 17 May 2018 cannot train on the back-fill.

    Red first: written while the declaration was `null` (`AssertionError: None != datetime(2018, 5, 17, 0, 0)`,
    and the refusal tests read no instant).

    Mutation record. In a copy of the working tree under the session's scratchpad, CPython 3.11
    (`/opt/rmm-venv`), `PYTHONDONTWRITEBYTECODE=1`, `python -B`, this class run alone, unmutated control green before and after, the mutated line confirmed applied by grep.
    In `backfill.require_posting_established` the refusal condition
    `if posting_instant is None or posting_instant > start:` was mutated to `if posting_instant is None:`.
    Killed, 2 failures, both `AssertionError: LookAheadError not raised`:
    `test_a_fit_ending_the_day_before_the_ruled_instant_is_refused` and
    `test_every_fit_ending_in_2018_before_17_may_is_refused`.
    """

    RULED = datetime(2018, 5, 17, 0, 0)

    def _declared(self):
        return backfill.load_posting_instant(ROOT / "metadata" / "backfill_posting.json")

    def test_the_declaration_is_17_may_2018_and_cites_its_source(self):
        self.assertEqual(self._declared(), self.RULED)
        text = (ROOT / "metadata" / "backfill_posting.json").read_text(encoding="utf-8")
        self.assertIn("6145957978", text)
        self.assertIn("6146010089", text)

    def test_a_fit_ending_the_day_before_the_ruled_instant_is_refused(self):
        with self.assertRaises(LookAheadError) as caught:
            backfill.require_posting_established(
                [_fold(date(2018, 5, 17), date(2018, 5, 16))], self._declared(), where="test"
            )
        self.assertIn("2018-05-17", str(caught.exception))

    def test_every_fit_ending_in_2018_before_17_may_is_refused(self):
        day = backfill.FIRST_PUBLISHED
        while day < self.RULED.date():
            if day.weekday() < 5:
                with self.assertRaises(LookAheadError):
                    backfill.require_posting_established(
                        [_fold(day + timedelta(days=1), day)], self._declared(), where="test"
                    )
            day += timedelta(days=1)

    def test_a_fit_ending_on_or_after_17_may_passes(self):
        for end in (date(2018, 5, 17), date(2018, 5, 18), date(2018, 6, 27)):
            backfill.require_posting_established(
                [_fold(end + timedelta(days=2), end)], self._declared(), where="test"
            )

    def test_the_declared_instant_does_not_open_a_back_filled_scored_day_or_feature_row(self):
        with self.assertRaises(LookAheadError):
            backfill.require_training_only([_fold(date(2018, 6, 29), date(2018, 3, 29))], where="test")


class TheShiftKeepsTheScoredDays(unittest.TestCase):
    """Raising `minimum_history` by the prefix scores the very days the published rows score."""

    def _rows(self, start: date, count: int):
        rows, day = [], start
        while len(rows) < count:
            if day.weekday() < 5:
                index = len(rows)
                spike = 0.08 if index % 17 == 0 else 0.0
                rows.append(DailyObservation(day, {"sofr": 1.80 + spike + 0.01 * (index % 3), "iorb": 1.75}))
            day += timedelta(days=1)
        return rows

    def test_scored_days_and_blocks_are_unchanged(self):
        registry = json.loads((ROOT / "metadata" / "sources.json").read_text())
        everything = self._rows(date(2018, 1, 2), 230)
        published = [row for row in everything if row.date >= backfill.FIRST_PUBLISHED]
        prefix = backfill.prefix_length([row.date for row in everything])
        self.assertGreater(prefix, 30)

        def run(rows, minimum_history):
            return rolling_exceedance_backtest(
                rows,
                predictor=persistence_logistic_exceedance(minimum_history=40),
                model_name="persistence_logistic",
                features=("spread_bps",),
                registry=registry,
                decision_time=time(16, 0),
                taus=(5.0, 10.0),
                minimum_history=minimum_history,
                refit_every=21,
            )

        without = run(published, 61)
        with_history = run(everything, 61 + prefix)
        self.assertEqual(without.scored_dates, with_history.scored_dates)
        self.assertEqual(
            [(f.scored_date, f.feature_date) for f in without.folds],
            [(f.scored_date, f.feature_date) for f in with_history.folds],
        )
        self.assertLess(with_history.folds[0].train_start, backfill.FIRST_PUBLISHED)
        self.assertGreater(with_history.folds[0].train_rows, without.folds[0].train_rows)
        backfill.require_training_only(with_history.folds, where="test")


if __name__ == "__main__":
    unittest.main()


class AugmentingTheExtendedPanel(unittest.TestCase):
    """The measurement columns join the extended panel; the back-filled rows carry none of them (#484).

    Mutation record: red first, before `augment_rows` existed
    (`AttributeError: module 'repo_model.backfill' has no attribute 'augment_rows'`). Then, with the function in place, one mutation
    in a disposable copy, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, unmutated control green before
    and after, the line confirmed applied by grep: `src/repo_model/backfill.py`, in `augment_rows`,
    `if not same:` replaced by `if False:`; `test_a_published_row_that_disagrees_is_refused` failed with
    `AssertionError: ValueError not raised`.
    """

    def _rows(self):
        extended = [
            {"date": "2018-03-29", "sofr": "1.75", "reserve_balances": "2200.0"},
            {"date": "2018-04-03", "sofr": "1.83", "reserve_balances": "2113.3"},
            {"date": "2018-04-04", "sofr": "1.76", "reserve_balances": ""},
        ]
        augmented = [
            {"date": "2018-04-03", "sofr": "1.83", "reserve_balances": "2113.3", "tga_daily": "300.0"},
            {"date": "2018-04-04", "sofr": "1.76", "reserve_balances": "", "tga_daily": ""},
        ]
        return extended, augmented

    def test_back_filled_rows_get_blank_measurement_columns_and_published_rows_the_measurements(self):
        extended, augmented = self._rows()
        out = backfill.augment_rows(extended, augmented)
        self.assertEqual([row["date"] for row in out], ["2018-03-29", "2018-04-03", "2018-04-04"])
        self.assertEqual(out[0]["tga_daily"], "")
        self.assertEqual(out[0]["sofr"], "1.75")
        self.assertEqual(out[1]["tga_daily"], "300.0")

    def test_a_published_row_that_disagrees_is_refused(self):
        extended, augmented = self._rows()
        augmented[0]["sofr"] = "1.90"
        with self.assertRaises(ValueError):
            backfill.augment_rows(extended, augmented)

    def test_different_published_days_are_refused(self):
        extended, augmented = self._rows()
        with self.assertRaises(ValueError):
            backfill.augment_rows(extended, augmented[:1])
