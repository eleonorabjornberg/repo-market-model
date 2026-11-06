"""The FR 2004 half of the availability poll reads the declared source's CSV (#1493, Eleonora's ruling of 6 Nov 2026).

The release page carries no release date (it loads the data in the browser), so the poll could only ever record
"1998-01-28". From 12 November it reads `https://markets.newyorkfed.org/api/pd/get/all/timeseries.csv` and keeps its
hash and the latest `As Of Date`, never the file. No test fetches.

Mutation (recorded for the reviewer, not a leakage guard): in `latest_date`, the FR2004 branch changed to
`return min(found)` made `test_latest_as_of_date_is_the_maximum` fail with
`AssertionError: datetime.date(2026, 8, 19) != datetime.date(2026, 9, 2)`.
"""

from __future__ import annotations

import hashlib
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from repo_model import availability_poll as ap

ROOT = Path(__file__).resolve().parents[1]
CSV = (
    b'"As Of Date","Time Series","Value (millions)"\n'
    b'"2026-08-26","PDPOSGS-B","69687"\n'
    b'"2026-09-02","PDPOSGS-B","70001"\n'
    b'"2026-08-19","PDPOSGS-B","1998-01-28"\n'
)
NOW = datetime(2026, 11, 12, 21, 10, tzinfo=timezone.utc)


class Fr2004Csv(unittest.TestCase):
    def test_url_is_the_declared_source_csv(self):
        self.assertEqual(ap.url_for(ap.FR2004, date(2026, 11, 12)),
                         "https://markets.newyorkfed.org/api/pd/get/all/timeseries.csv")

    def test_url_matches_the_source_declaration(self):
        declared = (ROOT / "metadata/sources.json").read_text()
        self.assertIn(ap.FR2004_RELEASE_URL, declared)

    def test_latest_as_of_date_is_the_maximum(self):
        self.assertEqual(ap.latest_date(ap.FR2004, CSV), date(2026, 9, 2))

    def test_only_the_as_of_column_counts(self):
        # a date inside a value column is not an As Of Date
        self.assertEqual(ap.latest_date(ap.FR2004, CSV.replace(b'"70001"', b'"2030-01-01"')), date(2026, 9, 2))

    def test_page_dates_are_not_read(self):
        self.assertIsNone(ap.latest_date(ap.FR2004, b"<p>January 28, 1998 1914-11-16</p>"))

    def test_tracked_snapshot(self):
        body = (ROOT / "tests/fixtures/snapshots/fr2004/pdposgst_tot_and_components.csv").read_bytes()
        self.assertEqual(ap.latest_date(ap.FR2004, body), date(2026, 8, 26))

    def test_record_keeps_hash_and_date_not_the_body(self):
        rec = ap.poll_record(ap.FR2004, NOW, lambda url: (200, CSV, None), clock=lambda: NOW)
        self.assertEqual(rec["sha256"], hashlib.sha256(CSV).hexdigest())
        self.assertEqual((rec["latest_date"], rec["bytes"]), ("2026-09-02", len(CSV)))
        self.assertEqual(rec["url"], ap.FR2004_RELEASE_URL)
        self.assertNotIn(b"PDPOSGS", repr(rec).encode())
        ap.check_record(rec)


if __name__ == "__main__":
    unittest.main()
