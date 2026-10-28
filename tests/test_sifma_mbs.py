"""`repo_model.sifma_mbs` (#1276; H5 step 3): SIFMA's agency MBS class settlement dates and when each year's calendar was public.

Written first. What these tests pin: that the tracked table is what `scripts/build_sifma_table_1276.py` builds from the tracked captures (a command over
tracked bytes), one date per class per calendar month with every date on a weekday; that the declaration's `public_from` is exactly what the archive's
captures show (each timestamp is a manifest entry whose bytes carry the label or table the declaration cites, and a year without such a capture is `null`);
that the `scheduled_availability` block conforms to `asof.validate_scheduled_availability`; and the availability rule on hand cases: a date is read as 1
only by a decision made at or after the capture that shows its year, never by an earlier decision, never in a year that has no capture, and a date
before its year's capture is not read in that year.

Recorded mutation (the availability rule, #1276): in `sifma_mbs.public_at`, the line `return moment <= instant.replace(tzinfo=_EASTERN).astimezone(UTC)`
was changed to `return True`. Four tests then failed: `PublicAtTests.test_a_decision_before_the_capture_reads_nothing` with `AssertionError: 1 != 0`,
`PublicAtTests.test_the_capture_instant_decides_within_a_day` with `AssertionError: 1 != 0`,
`PublicAtTests.test_a_date_before_its_years_capture_is_not_public_in_that_year` with `AssertionError: Lists differ: [1, 1, 1, 1] != [0, 0, 0, 0]`, and
`ReadTests.test_a_raw_date_of_a_year_not_yet_public_is_refused` with `AssertionError: LookAheadError not raised`; restored, all pass.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
import unittest
from datetime import date, datetime
from pathlib import Path

from repo_model import asof, sifma_mbs
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_sifma_table_1276", ROOT / "scripts" / "build_sifma_table_1276.py")
builder = importlib.util.module_from_spec(_spec)
sys.modules["build_sifma_table_1276"] = builder
_spec.loader.exec_module(builder)

DECLARATION = json.loads((ROOT / "metadata" / "sifma_mbs_1276.json").read_text(encoding="utf-8"))
CAPTURES = {e["capture_timestamp"] + "|" + e["url"]: e for e in json.loads((ROOT / "data" / "sifma-wayback-1276" / "manifest.json").read_text(encoding="utf-8"))}


def at(day: date) -> datetime:
    """The decision instant of `day`, a naive America/New_York wall-clock datetime."""

    return datetime(day.year, day.month, day.day, 16, 0)


class TableTests(unittest.TestCase):
    def test_the_tracked_table_is_a_rebuild_of_the_tracked_captures(self):
        self.assertEqual(builder.main(["--check"]), 0)

    def test_the_manifest_carries_the_checksum_of_the_table_and_of_each_capture(self):
        meta = json.loads(builder.MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(meta["sha256"], hashlib.sha256(builder.TABLE.read_bytes()).hexdigest())
        self.assertEqual(len(meta["inputs"]), 3)
        for item in meta["inputs"]:
            self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])

    def test_one_date_per_class_per_month_on_a_weekday_from_2018_to_2027(self):
        table = sifma_mbs.load_table()
        self.assertEqual(sorted(table), ["A", "B", "C", "D"])
        for klass, days in table.items():
            self.assertEqual(len(days), 120, klass)
            self.assertEqual({(d.year, d.month) for d in days}, {(y, m) for y in range(2018, 2028) for m in range(1, 13)}, klass)
            self.assertTrue(all(d.weekday() < 5 for d in days), klass)

    def test_known_dates_are_read_as_the_sources_state_them(self):
        table = sifma_mbs.load_table()
        # the workbook's first block (2018-01), the 2022 sheet's Juneteenth adjustment, the 2025 and 2026 page tables
        self.assertIn(date(2018, 1, 11), table["A"])
        self.assertIn(date(2022, 6, 22), table["C"])
        self.assertIn(date(2021, 3, 11), table["A"] | table["B"] | table["C"] | table["D"])
        self.assertIn(date(2025, 1, 14), table["A"])
        self.assertIn(date(2026, 1, 27), table["D"])

    def test_the_builder_refuses_a_weekday_that_does_not_match_its_day(self):
        with self.assertRaises(SystemExit):
            builder._weekday_cell("Monday 11", (2018, 1), "test")  # 2018-01-11 is a Thursday
        self.assertEqual(builder._weekday_cell("Thurday 11", (2021, 3), "test"), date(2021, 3, 11))


class DeclarationTests(unittest.TestCase):
    def test_the_scheduled_availability_block_conforms(self):
        self.assertEqual(asof.validate_scheduled_availability(DECLARATION["source_id"], DECLARATION["scheduled_availability"]), [])
        self.assertEqual(sorted(DECLARATION["scheduled_availability"]["fields"]), sorted(DECLARATION["fields"].values()))

    def test_every_year_of_the_table_has_an_entry_and_a_dated_entry_cites_a_captured_file(self):
        self.assertEqual(sorted(DECLARATION["public_from"]), [str(y) for y in range(2018, 2028)])
        for year, entry in DECLARATION["public_from"].items():
            if entry["capture_timestamp"] is None:
                self.assertIn("reason", entry, year)
                continue
            self.assertTrue(entry["evidence"].strip(), year)
            manifest = [e for e in CAPTURES.values() if e["capture_timestamp"] == entry["capture_timestamp"] and entry["capture"].endswith(e["file"])]
            self.assertEqual(len(manifest), 1, year)
            self.assertEqual(hashlib.sha256((ROOT / entry["capture"]).read_bytes()).hexdigest(), manifest[0]["sha256"], year)

    def test_a_dated_year_is_one_the_cited_capture_shows(self):
        """Each dated year's capture carries the label '(updated for <year>)' or the table of that year's dates, as the declaration says; a year
        the declaration leaves `null` is not shown by any earlier capture of the page that carries such a label."""

        def text(name: str) -> str:
            return builder.read_capture(name).decode("utf-8")

        for year, entry in DECLARATION["public_from"].items():
            if entry["capture_timestamp"] is None:
                continue
            page = text(Path(entry["capture"]).name)
            shown = f"(updated for {year})" in page or re.search(rf">[A-Z][a-z]{{2}}-({year}|{year[2:]})<", page)
            self.assertTrue(shown, f"{year}: the capture {entry['capture_timestamp']} does not show it")
        labelled = {}
        for entry in CAPTURES.values():
            if entry["url"].endswith("/") and entry["file"].startswith("2"):
                for found in re.findall(r"\(updated for (\d{4})\)", text(entry["file"])):
                    labelled.setdefault(found, entry["capture_timestamp"])
        for year, entry in DECLARATION["public_from"].items():
            if year in labelled:
                self.assertEqual(entry["capture_timestamp"], labelled[year], f"{year}: the earliest labelled capture is not the declared one")

    def test_the_years_with_a_capture_are_the_ones_the_pages_label_or_tabulate(self):
        public = sifma_mbs.load_public_from()
        self.assertEqual(sorted(y for y, m in public.items() if m is not None), [2020, 2021, 2024, 2025, 2026, 2027])


class PublicAtTests(unittest.TestCase):
    def setUp(self):
        self.table = sifma_mbs.load_table()
        self.public = sifma_mbs.load_public_from()

    def test_a_decision_before_the_capture_reads_nothing(self):
        # the first class A date of 2020; its year is shown from the capture of 2019-08-20, 19:32:52 UTC = 15:32:52 EDT
        target = next(d for d in sorted(self.table["A"]) if d.year == 2020)
        self.assertEqual(sifma_mbs.indicator(self.table, self.public, "A", target, at(date(2019, 8, 19))), 0)
        self.assertEqual(sifma_mbs.indicator(self.table, self.public, "A", target, at(date(2019, 8, 20))), 1)

    def test_the_capture_instant_decides_within_a_day(self):
        target = next(d for d in sorted(self.table["B"]) if d.year == 2020)
        self.assertEqual(sifma_mbs.indicator(self.table, self.public, "B", target, datetime(2019, 8, 20, 15, 32, 51)), 0)
        self.assertEqual(sifma_mbs.indicator(self.table, self.public, "B", target, datetime(2019, 8, 20, 15, 32, 52)), 1)

    def test_a_year_without_a_capture_is_never_public(self):
        for year in (2018, 2019, 2022, 2023):
            target = next(d for d in sorted(self.table["C"]) if d.year == year)
            for instant in (at(date(2017, 1, 3)), at(date(year, 1, 2)), at(date(2026, 9, 3))):
                self.assertEqual(sifma_mbs.indicator(self.table, self.public, "C", target, instant), 0, (year, instant))

    def test_a_date_before_its_years_capture_is_not_public_in_that_year(self):
        # 2025: the page was captured on Sunday 2025-01-19. Class A and B settled on 01-14 and 01-16, before it: every decision that can target them (an
        # earlier day's) was made before the capture, so they read 0; C and D settled on 01-21 and 01-23, and the decision of Monday 01-20 reads them.
        a, b, c, d = date(2025, 1, 14), date(2025, 1, 16), date(2025, 1, 21), date(2025, 1, 23)
        decisions = [date(2025, 1, 13), date(2025, 1, 15), date(2025, 1, 17), date(2025, 1, 17)]
        self.assertEqual([sifma_mbs.indicator(self.table, self.public, k, x, at(i)) for k, x, i in zip("ABCD", (a, b, c, d), decisions)], [0, 0, 0, 0])
        self.assertEqual([sifma_mbs.indicator(self.table, self.public, k, x, at(date(2025, 1, 20))) for k, x in zip("CD", (c, d))], [1, 1])

    def test_a_non_settlement_day_is_zero_at_any_instant(self):
        self.assertEqual(sifma_mbs.indicator(self.table, self.public, "A", date(2025, 3, 3), at(date(2026, 9, 3))), 0)

    def test_flags_reads_all_four_classes(self):
        flags = sifma_mbs.flags(self.table, self.public, date(2025, 2, 13), at(date(2025, 2, 12)))
        self.assertEqual(flags, {"A": 1, "B": 0, "C": 0, "D": 0})  # 2025-02-13 is class A's February settlement date


class ReadTests(unittest.TestCase):
    def setUp(self):
        self.public = sifma_mbs.load_public_from()

    def test_a_raw_date_of_a_year_not_yet_public_is_refused(self):
        with self.assertRaises(LookAheadError):
            sifma_mbs.require_public(date(2020, 3, 12), at(date(2019, 8, 19)), self.public)
        with self.assertRaises(LookAheadError):
            sifma_mbs.require_public(date(2019, 3, 12), at(date(2026, 9, 3)), self.public)  # a year with no capture
        sifma_mbs.require_public(date(2020, 3, 12), at(date(2019, 8, 20)), self.public)

    def test_an_aware_instant_is_refused(self):
        with self.assertRaises(ValueError):
            sifma_mbs.public_at(self.public[2020], datetime(2019, 8, 20, 16, 0, tzinfo=sifma_mbs.UTC))

    def test_a_declaration_with_a_timestamp_that_is_not_an_archive_stamp_is_refused(self):
        with self.assertRaises(ValueError):
            sifma_mbs.parse_public_from({"2020": {"capture_timestamp": "2019-08-20"}})


if __name__ == "__main__":
    unittest.main()
