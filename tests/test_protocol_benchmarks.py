"""The benchmarks of scoring protocol v1, on the published panel (#655).

B1 and B2 are reproduced by hand on 20 development days, sampled with a fixed seed from the
decision days whose five targets fall on or before 2026-09-03. "By hand" is `_Hand` below: it
reads the panel CSV with `csv` alone, takes the last public spread as the row before the
decision day (the information-set rule's read for the daily NY Fed rates), reads the day type
from the calendar columns and the panel's own month ends, and interpolates quantiles in its
own words. It shares no code with `repo_model.protocol_benchmarks`. Its summary of each day
is recorded in `RECORDED`, so neither side can move without this test noticing.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import random
import tempfile
import unittest
from datetime import date, time
from pathlib import Path

from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp
from repo_model.cli import main as cli_main
from repo_model.data import load_daily_panel, load_point_in_time_panel
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
#: The published panel's build (`metadata/funding_panel_manifest.json`).
CUTOFF = "2026-09-08T21:31:42+00:00"
DECISION = time(16, 0)
DEVELOPMENT_FIRST = date(2018, 6, 29)
DEVELOPMENT_LAST = date(2026, 9, 3)
SAMPLE_SEED = 655

_PANEL = {}


def published_panel():
    """The published panel and its point-in-time rows, built once from the tracked fixtures."""

    if not _PANEL:
        tmp = tempfile.mkdtemp()
        path = Path(tmp) / "funding_panel.csv"
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli_main(
                ["build", "--raw-root", str(FIXTURES), "--output", str(path),
                 "--build-cutoff", CUTOFF, "--decision-time", "16:00:00"]
            )
        if code != 0:
            raise RuntimeError("the fixture panel did not build")
        _PANEL["path"] = path
        _PANEL["rows"] = load_daily_panel(path)
        _PANEL["pit"] = path.with_name(path.stem + "_point_in_time.csv")
    return _PANEL


class _Hand:
    """B1 and B2 from the CSV alone, written without reference to the module."""

    GRID = (0.01, 0.025, 0.05) + tuple(round(0.10 + 0.05 * k, 2) for k in range(17)) + (0.95, 0.975, 0.99)

    def __init__(self, path):
        self.rows = []
        with open(path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                self.rows.append(
                    (
                        date.fromisoformat(row["date"]),
                        100.0 * (float(row["sofr"]) - float(row["iorb"])),
                        float(row["quarter_end"]),
                        float(row["tax_date"]),
                    )
                )

    @staticmethod
    def quantile(values, p):
        ordered = sorted(values)
        x = p * (len(ordered) - 1)
        lo = int(x)
        w = x - lo
        return ordered[lo] if w == 0 else ordered[lo] * (1 - w) + ordered[lo + 1] * w

    @staticmethod
    def back(day, years):
        try:
            return day.replace(year=day.year - years)
        except ValueError:
            return day.replace(year=day.year - years, day=28)

    def first_after(self, day):
        return next(i for i, row in enumerate(self.rows) if row[0] > day)

    def kind(self, i):
        day, _, quarter_end, tax = self.rows[i]
        if quarter_end == 1.0:
            return "quarter_end"
        month = [row[0] for row in self.rows if (row[0].year, row[0].month) == (day.year, day.month)]
        if day in month[-2:]:
            return "month_end"
        return "tax_date" if tax == 1.0 else "ordinary"

    def b1(self, t):
        anchor = t - 1
        first = self.first_after(self.back(self.rows[t][0], 2))
        out, counts = {}, {}
        for h in range(1, 6):
            ends = range(max(first, h), anchor + 1)
            changes = [self.rows[s][1] - self.rows[s - h][1] for s in ends]
            out[h] = [self.rows[anchor][1] + self.quantile(changes, p) for p in self.GRID]
            counts[h] = len(changes)
        return anchor, out, counts

    def b2(self, t):
        anchor = t - 1
        first = self.first_after(self.back(self.rows[t][0], 1))
        kinds = {s: self.kind(s) for s in range(first, anchor + 1)}
        out, meta = {}, {}
        for h in range(1, 6):
            kind = self.kind(t + h)
            sample = [self.rows[s][1] for s, value in kinds.items() if value == kind]
            out[h] = [self.quantile(sample, p) for p in self.GRID]
            meta[h] = (kind, len(sample))
        return out, meta


#: Per sampled decision day: the anchor (last public row), its spread, B1's count of 1-day
#: changes, B1's lead-1 median, B1's lead-5 5% quantile, B2's lead-1 day type, sample size
#: and median. Computed by `_Hand` on the published panel, 12 October 2026.
RECORDED = (
    ("2018-07-02", "2018-06-29", 17.0, 62, 16.0, 6.85, "ordinary", 51, -3.0),
    ("2018-08-15", "2018-08-14", -2.0, 93, -2.0, -13.0, "ordinary", 80, -3.5),
    ("2018-09-17", "2018-09-14", 0.0, 115, 0.0, -10.5, "tax_date", 6, -3.0),
    ("2018-10-16", "2018-10-15", 1.0, 135, 1.0, -8.5, "ordinary", 115, -3.0),
    ("2020-01-17", "2020-01-16", 0.0, 447, 0.0, -11.9, "ordinary", 213, 3.0),
    ("2020-02-26", "2020-02-25", -1.0, 473, -1.0, -12.0, "month_end", 20, 4.5),
    ("2020-11-03", "2020-11-02", 1.0, 498, 1.0, -9.0, "ordinary", 214, -1.0),
    ("2021-03-09", "2021-03-08", -8.0, 499, -8.0, -17.0, "ordinary", 213, -2.0),
    ("2022-03-07", "2022-03-04", -10.0, 499, -10.0, -13.0, "ordinary", 214, -10.0),
    ("2022-11-30", "2022-11-29", -9.0, 499, -9.0, -12.0, "ordinary", 214, -11.0),
    ("2023-05-01", "2023-04-28", -9.0, 498, -9.0, -11.0, "ordinary", 212, -10.0),
    ("2023-11-14", "2023-11-13", -8.0, 499, -8.0, -11.0, "ordinary", 213, -10.0),
    ("2024-01-08", "2024-01-05", -9.0, 497, -9.0, -12.0, "ordinary", 213, -10.0),
    ("2025-01-21", "2025-01-17", -11.0, 498, -11.0, -15.0, "ordinary", 213, -8.0),
    ("2025-03-21", "2025-03-20", -11.0, 499, -11.0, -16.0, "ordinary", 212, -7.0),
    ("2025-06-17", "2025-06-16", -8.0, 498, -8.0, -14.0, "tax_date", 11, -7.0),
    ("2025-10-08", "2025-10-07", -1.0, 499, -1.0, -8.1, "ordinary", 213, -7.0),
    ("2026-04-24", "2026-04-23", 0.0, 497, 0.0, -9.0, "ordinary", 212, -1.0),
    ("2026-06-23", "2026-06-22", -4.0, 497, -4.0, -13.0, "ordinary", 212, 0.0),
    ("2026-07-15", "2026-07-14", -2.0, 497, -2.0, -12.0, "ordinary", 212, -1.0),
)


def sampled_positions(rows):
    days = [row.date for row in rows]
    candidates = [
        i for i, day in enumerate(days)
        if DEVELOPMENT_FIRST <= day and i + 5 < len(days) and days[i + 5] <= DEVELOPMENT_LAST
    ]
    return sorted(random.Random(SAMPLE_SEED).sample(candidates, 20))


class HandReproductionTests(unittest.TestCase):
    """B1 and B2 reproduced by hand on 20 sampled development days."""

    @classmethod
    def setUpClass(cls):
        panel = published_panel()
        cls.rows = panel["rows"]
        cls.hand = _Hand(panel["path"])
        cls.positions = sampled_positions(cls.rows)

    def test_the_sample_is_the_recorded_one(self):
        self.assertEqual(
            [self.rows[t].date.isoformat() for t in self.positions], [r[0] for r in RECORDED]
        )

    def test_the_hand_computation_is_the_recorded_one(self):
        for t, recorded in zip(self.positions, RECORDED):
            anchor, b1, counts = self.hand.b1(t)
            b2, meta = self.hand.b2(t)
            got = (
                self.hand.rows[t][0].isoformat(),
                self.hand.rows[anchor][0].isoformat(),
                round(self.hand.rows[anchor][1], 6),
                counts[1],
                round(b1[1][11], 6),
                round(b1[5][2], 6),
                meta[1][0],
                meta[1][1],
                round(b2[1][11], 6),
            )
            with self.subTest(day=recorded[0]):
                self.assertEqual(got, recorded)

    def test_b1_matches_the_hand_on_every_lead_and_level(self):
        for t in self.positions:
            _, expected, _ = self.hand.b1(t)
            got = pb.b1_forecast(self.rows, t, registry=REGISTRY, decision_time=DECISION)
            for h in sp.HORIZONS:
                with self.subTest(day=self.rows[t].date, h=h):
                    for a, b in zip(got[h], expected[h]):
                        self.assertAlmostEqual(a, b, places=9)

    def test_b2_matches_the_hand_on_every_lead_and_level(self):
        for t in self.positions:
            expected, _ = self.hand.b2(t)
            got = pb.b2_forecast(
                self.rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS
            )
            for h in sp.HORIZONS:
                with self.subTest(day=self.rows[t].date, h=h):
                    for a, b in zip(got[h], expected[h]):
                        self.assertAlmostEqual(a, b, places=9)


class InformationTests(unittest.TestCase):
    """Nothing after the last public row moves a benchmark."""

    @classmethod
    def setUpClass(cls):
        cls.rows = published_panel()["rows"]
        cls.t = [row.date for row in cls.rows].index(date(2019, 9, 13))

    def scrambled(self):
        """The panel with every spread from the decision day on set far away."""

        out = list(self.rows)
        for i in range(self.t, len(out)):
            values = dict(out[i].values)
            values["sofr"] = float(values["iorb"]) + 3.0
            out[i] = type(out[i])(out[i].date, values)
        return out

    def test_the_last_public_row_is_the_day_before_the_decision_day(self):
        b1 = pb.b1_forecast(self.rows, self.t, registry=REGISTRY, decision_time=DECISION)
        median = b1[1][sp.GRID.index(0.5)]
        anchor = self.rows[self.t - 1].spread_bps
        changes = sorted(
            self.rows[s].spread_bps - self.rows[s - 1].spread_bps for s in range(1, self.t)
            if self.rows[s].date > date(2017, 9, 13)
        )
        self.assertAlmostEqual(median, anchor + _Hand.quantile(changes, 0.5))

    def test_b1_and_b2_do_not_read_the_decision_day_or_later(self):
        for benchmark, settings in (
            (pb.b1_forecast, {}),
            (pb.b2_forecast, {"splits": SPLITS}),
        ):
            with self.subTest(benchmark=benchmark.__name__):
                before = benchmark(self.rows, self.t, registry=REGISTRY, decision_time=DECISION, **settings)
                after = benchmark(self.scrambled(), self.t, registry=REGISTRY, decision_time=DECISION, **settings)
                self.assertEqual(before, after)


class GuardTests(unittest.TestCase):
    def test_a_row_past_the_anchor_is_refused(self):
        """Mutation record: see `protocol_benchmarks._require_public`."""

        dates = [date(2019, 1, d) for d in range(2, 12)]
        pb._require_public([3, 4, 5], 5, dates, "here")
        with self.assertRaises(LookAheadError) as caught:
            pb._require_public([3, 6], 5, dates, "here")
        self.assertIn(str(dates[6]), str(caught.exception))

    def test_the_quantiles_never_cross(self):
        """Interpolating between equal values gives the value exactly."""

        values = sorted([5.000000000000004, 5.000000000000004, 5.000000000000004, 1.0])
        out = pb.empirical_quantiles(values, 0.1)
        self.assertEqual(out, sorted(out))
        sp.grid_crps(out, 0.0)

    def test_a_target_past_the_panel_is_refused(self):
        rows = published_panel()["rows"]
        with self.assertRaises(sp.ProtocolError):
            pb.b1_forecast(rows, len(rows) - 3, registry=REGISTRY, decision_time=DECISION)


class IncumbentTests(unittest.TestCase):
    def test_the_incumbent_is_the_published_declaration_on_five_levels(self):
        incumbent = pb.incumbent()
        self.assertEqual(incumbent["levels"], (0.05, 0.25, 0.5, 0.75, 0.95))
        record = json.loads((ROOT / incumbent["record"]).read_text(encoding="utf-8"))
        self.assertIn("declaration", record)

    def test_b3_is_refused_off_the_grid(self):
        five = {h: [0.0, 1.0, 2.0, 3.0, 4.0] for h in sp.HORIZONS}
        with self.assertRaises(sp.ProtocolError):
            pb.b3_forecast(pb.incumbent()["levels"], five)

    def test_b3_is_admitted_on_the_grid(self):
        forecast = {h: [float(k) for k in range(23)] for h in sp.HORIZONS}
        self.assertEqual(pb.b3_forecast(sp.GRID, forecast), forecast)


class OutcomeTests(unittest.TestCase):
    def test_the_panels_sofr_is_the_first_published_value_in_its_snapshot(self):
        """The published panel carries one vintage per day, so this checks consistency only.

        Whether that vintage is the first publication is not something one snapshot shows.
        """

        panel = published_panel()
        first = sp.first_published(load_point_in_time_panel(panel["pit"]), "SOFR")
        for row in panel["rows"]:
            if DEVELOPMENT_FIRST <= row.date <= DEVELOPMENT_LAST:
                self.assertAlmostEqual(first[row.date], row.values["sofr"])


if __name__ == "__main__":
    unittest.main()
