"""The band-coverage split and the sentence that cites it (#265).

`README.md` once said, of the published distribution, "None of these models has
one" (a calibration finding), from the pooled 90% interval. Split by the project's
own rule the 90% band does not hold on tax dates, in 2018-19 and in 2024. These
tests hold the replacement to the split: the sentence is generated from the cells,
a cell under the minimum size is never flagged, and the day-type tags are the
desk's.

Mutation record (disposable copy, `-B`, control green before and after):

1. `scripts/band_coverage.py`, `cells`: `excludes = k in live and not (low <= nominal <= high)`
   -> `excludes = not (low <= nominal <= high)`, so a cell under 20 days could be
   flagged. Kills `test_a_cell_under_the_minimum_is_never_flagged` with
   `TypeError` (`'<=' not supported between 'NoneType' and 'float'`): an
   under-minimum cell has no interval, so the mutated line fails on it.
2. `scripts/emit_results.py`, `coverage_section`: the split sentence not appended
   (`if published:` -> `if False:`). Kills
   `test_the_pooled_sentence_never_stands_while_a_split_cell_excludes` with
   `AssertionError`.
3. `scripts/band_coverage.py`, `tags_for`: `if when.month == 12:` -> `if when.month == 11:`.
   Kills `test_the_day_type_tags_are_the_desks` with `AssertionError` (a year-end
   day without its tag).
4. `scripts/emit_visual.py`, `band_coverage_block`: the sentence left out of the
   fill (`"bc_sentence": sentence` -> `"bc_sentence": ""`). Kills
   `SiteTests.test_the_page_carries_the_readmes_sentence` with `AssertionError`.
"""

from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from repo_model import metrics  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


band = _load("band_coverage")
emit = _load("emit_results")
OLD_SENTENCE = "None of these models has one."


class _Splits:
    regime_labels = ("a", "b")
    month_end_window = 2

    @staticmethod
    def regime(when):
        return "a" if when.day < 16 else "b"


def synthetic(excluded_days):
    """A series of 200 days whose 'tax_date' tag lands on `excluded_days` days, all missed."""

    rng = random.Random(3)
    start = date(2020, 1, 1)
    days = []
    for position in range(200):
        when = start + timedelta(days=position)
        tagged = position < excluded_days
        hit = 0.0 if tagged else (1.0 if rng.random() < 0.9 else 0.0)
        days.append({"date": when.isoformat(), "regime": "a" if when.day < 16 else "b",
                     "tags": ("tax_date",) if tagged else (),
                     "hits": {0.5: hit, 0.9: hit}, "side": "inside" if hit else "above"})
    series = [day["hits"][0.9] for day in days]
    interval = metrics.stationary_bootstrap_interval(
        lambda idx: sum(series[i] for i in idx) / len(idx), len(days),
        block_length=2, seed=11, replications=200)
    record = {"metrics": {"interval_calibration": {"coverage_interval": {
        "block_length": 2, "seed": 11, "replications": 200, "level": 0.9,
        "lower": interval[0], "upper": interval[1]}}}}
    return record, days


class CellSizeTests(unittest.TestCase):
    def test_a_cell_under_the_minimum_is_never_flagged(self):
        record, days = synthetic(band.MINIMUM_DAYS - 1)
        table = {cell["name"]: cell for cell in band.cells(record, days, _Splits)}
        cell = table["tax_date"]
        self.assertEqual(cell["days"], band.MINIMUM_DAYS - 1)
        self.assertFalse(cell["enough"])
        self.assertEqual(band.excluded([cell]), [])

    def test_a_cell_at_the_minimum_with_every_day_missed_is_flagged(self):
        record, days = synthetic(band.MINIMUM_DAYS)
        table = {cell["name"]: cell for cell in band.cells(record, days, _Splits)}
        cell = table["tax_date"]
        self.assertTrue(cell["enough"])
        self.assertEqual(cell["bands"][0.9]["coverage"], 0.0)
        self.assertTrue(cell["bands"][0.9]["excludes"])

    def test_a_pooled_interval_that_does_not_reproduce_the_record_raises(self):
        record, days = synthetic(30)
        record["metrics"]["interval_calibration"]["coverage_interval"]["lower"] -= 0.05
        with self.assertRaises(band.BandError):
            band.cells(record, days, _Splits)


class PublishedSentenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record, cls.table, cls.horizons, cls.days = emit.band_coverage()
        cls.readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    def test_the_pooled_sentence_never_stands_while_a_split_cell_excludes(self):
        self.assertTrue(band.excluded(self.table),
                        "the published split has no excluding cell; the check below proves nothing")
        self.assertNotIn(OLD_SENTENCE, self.readme)
        self.assertIn(band.finding_sentence(self.table), self.readme)
        # And from the generator itself, so a README that was not regenerated cannot hide it.
        _, groups = emit.challenger_section()
        persistence = emit.load(emit.PERSISTENCE)
        text = "\n".join("\n".join(emit.coverage_section(group, persistence)) for group in groups)
        self.assertNotIn(OLD_SENTENCE, text)
        self.assertIn(band.finding_sentence(self.table), text)

    def test_the_sentence_names_every_excluding_cell_from_the_record(self):
        sentence = band.finding_sentence(self.table)
        found = band.excluded(self.table)
        self.assertIn("%d cells" % len(found), sentence)
        for label, cell in found:
            figures = cell["bands"][0.5 if label == "50%" else 0.9]
            self.assertIn("%.1f%%" % (100.0 * figures["coverage"]), sentence)

    def test_with_no_excluding_cell_the_sentence_says_so(self):
        self.assertIn("no cell", band.finding_sentence([]))

    def test_the_split_reproduces_the_reviews_quarter_end_row(self):
        cell = {c["name"]: c for c in self.table}["quarter_end"]
        self.assertEqual((cell["days"], cell["below"], cell["above"]), (31, 0, 7))
        self.assertAlmostEqual(cell["bands"][0.9]["coverage"], 24 / 31)

    def test_h2_to_h5_carry_no_interval(self):
        self.assertEqual({c["horizon"] for c in self.horizons}, {2, 3, 4, 5})
        self.assertTrue(all("lower" not in c for c in self.horizons))


class TagTests(unittest.TestCase):
    def test_the_day_type_tags_are_the_desks(self):
        desk = _load("desk_outputs")
        rows = band.build_panel_rows()
        splits = band.load_split_declaration(band.SPLITS)
        checked = 0
        for iso, row in rows.items():
            if any(row.get(c) in (None, "") for c in ("days_to_month_end", "quarter_end", "tax_date")):
                continue
            when = date.fromisoformat(iso)
            values = {k: (None if v in (None, "") else float(v))
                      for k, v in row.items() if k != "date"}
            self.assertEqual(band.tags_for(row, when, splits.month_end_window),
                             desk.pressure_day_tags(values, when, splits), iso)
            checked += 1
        self.assertGreater(checked, 1000)


class SiteTests(unittest.TestCase):
    """The table is on the published site too (her ruling of 6 October 2026 on #291).

    Generated by `emit_visual.py` from the same cells as `docs/band_coverage_by_split.md`.
    """

    @classmethod
    def setUpClass(cls):
        import html
        import re
        page = (REPO_ROOT / "site" / "index.html").read_text(encoding="utf-8")
        start = page.index('<div id="band-coverage"')
        block = page[start:page.index("<h3 class=\"sub\">Lead time", start)]
        cls.text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", block)))
        cls.record, cls.table, cls.horizons, cls.days = band.compute(REPO_ROOT / "docs" / "runs")

    def test_the_page_carries_the_readmes_sentence(self):
        squash = lambda text: text.replace("`", "").replace(" ", "")  # a <code> tag leaves a space
        self.assertIn(squash(band.finding_sentence(self.table)), squash(self.text))

    def test_every_h1_cell_is_on_the_page_with_its_interval(self):
        for cell in self.table:
            with self.subTest(cell=cell["name"]):
                if not cell["enough"]:
                    self.assertIn("too few days", self.text)
                    continue
                b = cell["bands"][0.9]
                self.assertIn("%s to %s" % (band._pct(b["lower"]), band._pct(b["upper"])), self.text)
                self.assertIn(band._pct(b["coverage"]), self.text)

    def test_h2_to_h5_are_shares_labelled_as_having_no_interval(self):
        self.assertIn("no interval: the record keeps no per-origin data for h = 2\u20135", self.text)
        for cell in self.horizons:
            if cell["days"] >= band.MINIMUM_DAYS:
                self.assertIn("%.1f%%" % cell["band_90"], self.text)


if __name__ == "__main__":
    unittest.main()
