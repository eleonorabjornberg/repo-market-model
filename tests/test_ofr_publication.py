"""The OFR "not yet published" flag and fill (#537, follow-up to #477 and PR #496).

The OFR repo-segment rates have no value before 2020-09-09, the day the OFR began publishing in real
time (#508, #522). A column that is missing there drops every scored day before September 2020 from a
fit that needs it. `ofr_publication` gives each rate a flag that depends on the row's date alone and a
value that is filled with 0.0 on a flagged row only, so those days stay in the comparison. The flag is
never a function of whether a value exists: the GCF "observed" indicator is not an admissible input
(ruling on #520).

Written red first: `repo_model.ofr_publication` did not exist (`ModuleNotFoundError`).

Recorded mutations (CLAUDE.md), 11 October 2026, in a disposable copy of `src/repo_model/ofr_publication.py`:
* `flagged = row.date < FIRST_PUBLIC` in `add_columns` mutated to
  `flagged = all(row.values.get(r) is None for r in SERIES)`: the flag now tracks whether a value exists. `test_the_flag_depends_on_the_date_alone` then fails with `AssertionError`.
* `dvp_segment.require_ofr_public(rows)` deleted from `add_columns`: a value before 2020-09-09 is no
  longer refused. `test_a_value_before_the_first_public_date_is_refused` then fails with `AssertionError`
  (`LookAheadError not raised`).
* `before = rows[position - 1].values.get(raw)` in `add_columns` mutated to `rows[position + 1]`: a hole would
  take the value of the row after it, which was not yet public. `test_a_one_row_hole_in_the_tri_party_rate_takes_the_row_before_and_is_not_carried_twice`
  then fails with `AssertionError` (`None != 0.1`).
"""

from __future__ import annotations

import unittest
from datetime import date

from repo_model import contract, ofr_publication
from repo_model.splits import LookAheadError
from repo_model.data import DailyObservation


def row(when, tri=None, gcf=None):
    return DailyObservation(when, {"spread_bps": 1.0, "ofr_tri_rate": tri, "ofr_gcf_rate": gcf})


class OfrPublicationTests(unittest.TestCase):
    def test_the_first_public_date_is_the_ofr_real_time_start(self):
        self.assertEqual(ofr_publication.FIRST_PUBLIC, date(2020, 9, 9))

    def test_the_flag_is_one_before_the_first_public_date_and_zero_from_it(self):
        built = ofr_publication.add_columns([row(date(2020, 9, 8)), row(date(2020, 9, 9), 0.1, 0.2)])
        self.assertEqual(built[0].values["tri_rate_not_yet_published"], 1.0)
        self.assertEqual(built[0].values["gcf_rate_not_yet_published"], 1.0)
        self.assertEqual(built[1].values["tri_rate_not_yet_published"], 0.0)
        self.assertEqual(built[1].values["gcf_rate_not_yet_published"], 0.0)

    def test_the_flag_depends_on_the_date_alone(self):
        """A published row with no value is not flagged; a row before the date is, whatever is in it."""

        built = ofr_publication.add_columns([row(date(2019, 1, 2)), row(date(2021, 3, 1), 0.1, None), row(date(2021, 3, 2))])
        self.assertEqual(built[0].values["gcf_rate_not_yet_published"], 1.0)
        self.assertEqual(built[1].values["gcf_rate_not_yet_published"], 0.0)
        self.assertEqual(built[2].values["tri_rate_not_yet_published"], 0.0)

    def test_the_value_is_filled_with_zero_on_a_flagged_row_only(self):
        built = ofr_publication.add_columns([row(date(2019, 1, 2)), row(date(2021, 3, 1), 0.1, None)])
        self.assertEqual(built[0].values["tri_rate_filled"], 0.0)
        self.assertEqual(built[0].values["gcf_rate_filled"], 0.0)
        self.assertEqual(built[1].values["tri_rate_filled"], 0.1)
        self.assertIsNone(built[1].values["gcf_rate_filled"], "a gap after publication is not filled")

    def test_a_one_row_hole_in_the_tri_party_rate_takes_the_row_before_and_is_not_carried_twice(self):
        built = ofr_publication.add_columns(
            [row(date(2021, 3, 1), 0.1), row(date(2021, 3, 2)), row(date(2021, 3, 3)), row(date(2021, 3, 4), 0.2)]
        )
        self.assertEqual(built[1].values["tri_rate_filled"], 0.1)
        self.assertIsNone(built[2].values["tri_rate_filled"], "a second hole in a row is left")
        self.assertEqual(built[3].values["tri_rate_filled"], 0.2)

    def test_the_gcf_rate_is_never_carried(self):
        built = ofr_publication.add_columns([row(date(2021, 3, 1), 0.1, 0.3), row(date(2021, 3, 2), 0.1, None)])
        self.assertIsNone(built[1].values["gcf_rate_filled"])
        self.assertEqual(ofr_publication.CARRY_ONE_ROW_HOLES, ("ofr_tri_rate",))

    def test_the_first_published_row_with_no_row_before_is_left(self):
        built = ofr_publication.add_columns([row(date(2020, 9, 9))])
        self.assertIsNone(built[0].values["tri_rate_filled"])

    def test_a_value_before_the_first_public_date_is_refused(self):
        with self.assertRaises(LookAheadError):
            ofr_publication.add_columns([row(date(2019, 1, 2), tri=0.1)])

    def test_the_input_rows_are_not_changed(self):
        rows = [row(date(2019, 1, 2))]
        ofr_publication.add_columns(rows)
        self.assertNotIn("tri_rate_filled", rows[0].values)

    def test_every_column_has_the_source_field_of_its_series(self):
        self.assertEqual(
            set(ofr_publication.COLUMN_FIELDS), set(ofr_publication.COLUMNS)
        )
        for column in ("tri_rate_filled", "tri_rate_not_yet_published"):
            self.assertEqual(ofr_publication.COLUMN_FIELDS[column], ofr_publication.RAW_FIELDS["ofr_tri_rate"])
        for column in ("gcf_rate_filled", "gcf_rate_not_yet_published"):
            self.assertEqual(ofr_publication.COLUMN_FIELDS[column], ofr_publication.RAW_FIELDS["ofr_gcf_rate"])

    def test_the_columns_are_off_in_the_published_declaration(self):
        self.assertFalse(set(ofr_publication.COLUMNS) & set(contract.FEATURE_FIELDS))
        self.assertFalse(any(column.startswith("ofr_") for column in ofr_publication.COLUMNS))


if __name__ == "__main__":
    unittest.main()
