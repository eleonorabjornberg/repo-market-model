"""IORB on back-filled rows is checked like any admitted series (#1230).

H4 groundwork (data admission). Eleonora's ruling of 26 October 2026 (ledger item 56 on #1223, relayed by the
orchestrating session): IOER/IORB on back-filled rows is admitted as training history only, on the same terms as the
back-filled SOFR. `backfill.NOT_A_SERIES` had exempted `iorb`, so a fit reading it on back-filled rows was never
checked. Now `metadata/backfill_posting.json` lists `iorb@2018-05-17` and `iorb` stands for itself like any series.

Red first, against main at 943530b0: three failures and one error (`ValueError` in the refusal test): `AssertionError: Tuples differ: ('sofr',) != ('iorb', 'sofr')` in
`test_series_read_follows_the_spread_to_iorb`, `AssertionError: LookAheadError not raised` in
`test_a_fit_reading_iorb_is_refused_when_it_is_not_admitted`, and `AssertionError: 'iorb' not found in {...}` in
`test_the_declaration_admits_iorb_from_the_same_instant_as_sofr`.

Mutation record. In a copy of the working tree, CPython 3.11, `python -B`, this file run alone, unmutated control green
before and after, the mutated line confirmed applied by grep. In `backfill.py` the line
`NOT_A_SERIES = contract.CALENDAR_FEATURES` was mutated to `NOT_A_SERIES = contract.CALENDAR_FEATURES | {"iorb"}` (the
exemption as it was). Killed: `test_a_fit_reading_iorb_is_refused_when_it_is_not_admitted` raised `ValueError` (the
exempt `iorb` left `series_read` empty, so the guard saw a back-filled fit that names no series instead of the
`LookAheadError` the test expects), `test_iorb_column_is_blank_unless_admitted` failed with
`AssertionError: Lists differ: [] != ['iorb']`, and `test_series_read_follows_the_spread_to_iorb` with
`AssertionError: Tuples differ: ('sofr',) != ('iorb', 'sofr')`.
"""

from __future__ import annotations

import unittest
from datetime import date, datetime
from pathlib import Path

from repo_model import backfill
from repo_model.baseline import ScoredFold
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
POSTING = ROOT / "metadata" / "backfill_posting.json"
INSTANT = datetime(2018, 5, 17)


def _fold(train_end: date) -> ScoredFold:
    return ScoredFold(
        train_start=date(2014, 8, 22), train_end=train_end, train_rows=70,
        feature_date=train_end, scored_date=date(2018, 6, 29),
    )


class IorbIsCheckedLikeAnyAdmittedSeries(unittest.TestCase):
    WITHOUT = {name: INSTANT for name in ("tgcr", "bgcr", "sofr")}
    WITH = {**WITHOUT, "iorb": INSTANT}

    def test_the_declaration_admits_iorb_from_the_same_instant_as_sofr(self):
        admitted = backfill.load_admitted_series(POSTING)
        self.assertIn("iorb", admitted)
        self.assertEqual(admitted["iorb"], admitted["sofr"])

    def test_calendar_columns_stay_no_series(self):
        self.assertEqual(backfill.series_read(("quarter_end", "tax_date", "days_to_month_end")), ())

    def test_series_read_follows_the_spread_to_iorb(self):
        self.assertEqual(backfill.series_read(("spread_bps",)), ("iorb", "sofr"))
        self.assertEqual(backfill.series_read(("quarter_end", "iorb")), ("iorb",))

    def test_iorb_column_is_blank_unless_admitted(self):
        self.assertEqual(backfill.unadmitted_columns(["iorb", "sofr"], self.WITHOUT), ["iorb"])
        self.assertEqual(backfill.unadmitted_columns(["iorb", "sofr"], self.WITH), [])

    def test_a_fit_reading_iorb_is_refused_when_it_is_not_admitted(self):
        reads = backfill.series_read(["iorb"])
        with self.assertRaises(LookAheadError) as caught:
            backfill.require_series_admitted([_fold(date(2018, 6, 27))], reads, self.WITHOUT, where="test")
        self.assertIn("iorb", str(caught.exception))

    def test_a_fit_reading_iorb_before_its_instant_is_refused(self):
        reads = backfill.series_read(["spread_bps"])
        with self.assertRaises(LookAheadError):
            backfill.require_series_admitted([_fold(date(2018, 5, 16))], reads, self.WITH, where="test")

    def test_a_fit_reading_iorb_after_its_instant_passes(self):
        reads = backfill.series_read(["spread_bps"])
        backfill.require_series_admitted([_fold(date(2018, 6, 27))], reads, self.WITH, where="test")


if __name__ == "__main__":
    unittest.main()
