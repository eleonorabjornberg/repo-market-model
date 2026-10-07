"""The band-coverage split and the sentence that cites it (#265), extended to h = 2 to 5 (#290).

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
5. `scripts/band_coverage.py`, `daily_day_table` (#290): `if iso > last:` -> `if False:`, the
   refusal of a day after the h = 1 record's last scored day. Kills
   `LaterHorizonTests.test_a_day_after_the_window_is_refused` with `AssertionError`
   (`BandError not raised`).
6. `scripts/band_coverage.py`, `check_against_diagnosis`, in `require`:
   `if not opened - 1e-9 <= value <= closed + 1e-9:` -> `if False:`, so a walk that does not
   reproduce the diagnosis passes. Kills
   `LaterHorizonTests.test_a_horizon_that_does_not_reproduce_the_diagnosis_is_refused` with
   `AssertionError` (`BandError not raised`).
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
        cls.record, cls.table, cls.later, cls.days = emit.band_coverage()
        cls.readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    def test_the_pooled_sentence_never_stands_while_a_split_cell_excludes(self):
        self.assertTrue(band.excluded(self.table),
                        "the published split has no excluding cell; the check below proves nothing")
        self.assertNotIn(OLD_SENTENCE, self.readme)
        self.assertIn(band.finding_sentence(self.table, self.later), self.readme)
        # And from the generator itself, so a README that was not regenerated cannot hide it.
        _, groups = emit.challenger_section()
        persistence = emit.load(emit.PERSISTENCE)
        text = "\n".join("\n".join(emit.coverage_section(group, persistence)) for group in groups)
        self.assertNotIn(OLD_SENTENCE, text)
        self.assertIn(band.finding_sentence(self.table, self.later), text)

    def test_the_sentence_names_every_excluding_cell_from_the_record(self):
        sentence = band.finding_sentence(self.table, self.later)
        horizons = [(1, self.table)] + [(e["horizon"], e["table"]) for e in self.later]
        self.assertIn("%d cells" % sum(len(band.excluded(t)) for _, t in horizons), sentence)
        for horizon, table in horizons:
            part = sentence.split("at h = %d, " % horizon)[1].split("; at h = ")[0]
            for label, cell in band.excluded(table):
                figures = cell["bands"][0.5 if label == "50%" else 0.9]
                with self.subTest(horizon=horizon, cell=cell["name"], band=label):
                    self.assertIn("%s band on %s" % (label, "all days" if cell["kind"] == "all" else
                                                     "%s %s" % (cell["kind"], band.cell_label(cell))), part)
                    self.assertIn("(%s, %s to %s)" % (band._pct(figures["coverage"]), band._pct(figures["lower"]),
                                                     band._pct(figures["upper"])), part)

    def test_with_no_excluding_cell_the_sentence_says_so(self):
        self.assertIn("no cell", band.finding_sentence([]))
        self.assertIn("h = 1 to 2", band.finding_sentence([], [{"horizon": 2, "table": []}]))

    def test_the_split_reproduces_the_reviews_quarter_end_row(self):
        cell = {c["name"]: c for c in self.table}["quarter_end"]
        self.assertEqual((cell["days"], cell["below"], cell["above"]), (31, 0, 7))
        self.assertAlmostEqual(cell["bands"][0.9]["coverage"], 24 / 31)

    def test_h2_to_h5_carry_an_interval_and_a_day_count_in_every_live_cell(self):
        self.assertEqual([e["horizon"] for e in self.later], [2, 3, 4, 5])
        for entry in self.later:
            for cell in entry["table"]:
                with self.subTest(horizon=entry["horizon"], cell=cell["name"]):
                    self.assertGreater(cell["days"], 0)
                    if not cell["enough"]:
                        self.assertEqual(band.excluded([cell]), [])
                        continue
                    for nominal in (0.5, 0.9):
                        figures = cell["bands"][nominal]
                        self.assertLessEqual(figures["lower"], figures["coverage"])
                        self.assertLessEqual(figures["coverage"], figures["upper"])


class LaterHorizonTests(unittest.TestCase):
    """h = 2 to 5 (#290): the daily records, their window, and their reproduction of the diagnosis."""

    @classmethod
    def setUpClass(cls):
        import json
        cls.runs = REPO_ROOT / "docs" / "runs"
        cls.record, cls.table, cls.later, cls.days = band.compute(cls.runs)
        cls.daily = {h: json.loads((cls.runs / (band.DAILY % h)).read_text(encoding="utf-8"))
                     for h in band.LATER_HORIZONS}
        cls.diagnosis = json.loads((cls.runs / band.DIAGNOSIS).read_text(encoding="utf-8"))

    def test_every_record_stays_inside_the_h1_window_and_no_locked_day(self):
        for horizon, daily in self.daily.items():
            with self.subTest(horizon=horizon):
                dates = [day["date"] for day in daily["days"]]
                self.assertEqual(dates, sorted(set(dates)))
                self.assertLessEqual(dates[-1], self.days[-1]["date"])
                self.assertLessEqual(dates[-1], "2025-12-31")
                self.assertEqual(daily["horizon"], horizon)
                self.assertEqual(daily["reproduces"]["exact"], True)

    def test_the_pooled_and_regime_shares_are_the_diagnosis_shares(self):
        for entry in self.later:
            pooled = self.diagnosis["q1_calibration"]["h%d_2018_2025" % entry["horizon"]]["issued"]
            cell = entry["table"][0]
            with self.subTest(horizon=entry["horizon"]):
                self.assertEqual(cell["days"], pooled["days"])
                # The diagnosis counts an outcome within 1e-9 bp of an edge as on it; here it is
                # on it only if exactly there. So the exact share lies between its open and closed.
                for nominal, key in ((0.5, "band_50"), (0.9, "band_90")):
                    value = 100.0 * cell["bands"][nominal]["coverage"]
                    self.assertGreaterEqual(value, pooled[key + "_open"] - 1e-9)
                    self.assertLessEqual(value, pooled[key + "_closed"] + 1e-9)

    def test_a_day_after_the_window_is_refused(self):
        rows = band.build_panel_rows()
        splits = band.load_split_declaration(band.SPLITS)
        daily = {"horizon": 2, "levels": band.LEVELS,
                 "days": [dict(day) for day in self.daily[2]["days"][-2:]]}
        last = daily["days"][0]["date"]
        with self.assertRaises(band.BandError):
            band.daily_day_table(daily, rows, splits, last)
        daily["days"] = daily["days"][:1]
        self.assertEqual(len(band.daily_day_table(daily, rows, splits, last)), 1)

    def test_a_horizon_that_does_not_reproduce_the_diagnosis_is_refused(self):
        entry = [e for e in self.later if e["horizon"] == 3][0]
        days = [dict(day, hits=dict(day["hits"])) for day in entry["days"]]
        band.check_against_diagnosis(3, days, self.diagnosis)
        for day in days[:30]:
            day["hits"][0.9] = 1.0 - day["hits"][0.9]
        with self.assertRaises(band.BandError):
            band.check_against_diagnosis(3, days, self.diagnosis)

    def test_each_horizon_is_the_published_distribution_on_the_published_panel(self):
        import json
        manifest = json.loads(band.MANIFEST.read_text(encoding="utf-8"))
        for horizon, daily in self.daily.items():
            with self.subTest(horizon=horizon):
                self.assertEqual(daily["panel_sha256"], manifest["sha256"])
                self.assertEqual(daily["published_record"], "docs/runs/pressure_model_v1_h%d.json" % horizon)
                self.assertEqual(daily["decides"], "nothing")
                self.assertEqual(daily["directive"], "#290")


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
        block = page[start:page.index("</section>", start)]
        cls.text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", block)))
        cls.record, cls.table, cls.later, cls.days = band.compute(REPO_ROOT / "docs" / "runs")

    def test_the_page_carries_a_plain_sentence_from_the_same_cells(self):
        """#314: the page states the all-days shares and the count of missed groups; the README keeps the long sentence."""
        everything = next(c for c in self.table if c["kind"] == "all")
        self.assertIn("The central 50%% range held on %d%% of days" % round(100 * everything["bands"][0.5]["coverage"]),
                      self.text)
        self.assertIn("the 90%% range on %d%%" % round(100 * everything["bands"][0.9]["coverage"]), self.text)

    def test_every_h1_cell_is_on_the_page_with_its_interval(self):
        for cell in self.table:
            with self.subTest(cell=cell["name"]):
                if not cell["enough"]:
                    self.assertIn("too few days", self.text)
                    continue
                b = cell["bands"][0.9]
                self.assertIn("%s to %s" % (band._pct(b["lower"]), band._pct(b["upper"])), self.text)
                self.assertIn(band._pct(b["coverage"]), self.text)

    def test_every_h2_to_h5_cell_is_on_the_page_with_its_interval(self):
        self.assertNotIn("no interval", self.text)
        for entry in self.later:
            self.assertIn("%d days ahead" % entry["horizon"], self.text)
            for cell in entry["table"]:
                with self.subTest(horizon=entry["horizon"], cell=cell["name"]):
                    if not cell["enough"]:
                        continue
                    b = cell["bands"][0.9]
                    self.assertIn("%s to %s" % (band._pct(b["lower"]), band._pct(b["upper"])), self.text)


if __name__ == "__main__":
    unittest.main()
