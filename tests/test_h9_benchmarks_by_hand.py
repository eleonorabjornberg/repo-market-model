"""B1 and B2 of the three H9 targets of #706, reproduced by hand on 20 sampled development days each (#994).

H1 step 3 for H9. `tests/test_protocol_benchmarks.py` does this for H5's spread; nothing did it for
`richer_targets.b1_quantiles` and `b2_quantiles`, which #706 scores the chosen targets against
(`bgcr_dispersion_bps`, `on_rrp_change_bn`, `sofr_dispersion_bps`).

"By hand" is `_Hand` below. It reads the H9 panel CSV with `csv` alone, rebuilds each target from the
raw columns the CSV carries (the percentiles of the secured rates and the ON RRP level), takes the last public
row as the row before the decision day (every source of the three targets declares a lag of one business
day), reads the day type from the calendar columns and the panel's own month ends, and interpolates the
quantiles in its own words. It shares no code with `repo_model.richer_targets`. The module's side is the
same calls `scripts/richer_targets_706.py` makes: `as_of_rows`, `window_first`, `b1_quantiles`, `b2_quantiles`.

The H9 panel is built here, in a temporary directory, from the tracked fixtures by the commands of
`scripts/richer_targets_639.py`'s docstring (`early_warning_inputs.py panel`, then `richer_targets_639.py panel`)
over the published panel. It ends on 2025-12-31 (`LAST_DAY`), so no day after it, and no locked day, is read
(`SamplingTests`). It is not the panel #706 declared (digest `26c51093…`, which also carries the
measurement-field columns): the three targets do not read those columns, and the test asserts the hand
target equals the CSV's own target column.

The sample is the 20 positions drawn by `random.Random(SAMPLE_SEED)` from the decision days from 2019-07-01 on
(by then both benchmarks can always be formed), per target. A disagreement between the hand and the module is not
fixed in `richer_targets`: it goes into `DISAGREEMENTS` below and into the pull request as a marked question.

Recorded mutation (CLAUDE.md asks for one only for a guard; this test guards no input, so this one shows that the test
can fail), 20 October 2026, in a disposable copy: `src/repo_model/richer_targets.py`, `b2_quantiles`,
`if kinds[s] == kind and values[s] is not None` changed to `if values[s] is not None`. `B2Tests` then fails with
`AssertionError` (the climatology is no longer the same-type days').
"""

from __future__ import annotations

import contextlib
import csv
import importlib.util
import io
import random
import tempfile
import unittest
from datetime import date, time
from pathlib import Path
from types import SimpleNamespace

import panel_cache
from repo_model import measurement_fields, richer_targets
from repo_model.data import load_daily_panel
from repo_model.evaluation_splits import load_split_declaration

ROOT = Path(__file__).resolve().parents[1]
SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
DECISION = time(16, 0)
LAST_TARGET = date(2025, 12, 31)
SAMPLE_FIRST = date(2019, 7, 1)
SAMPLE_SEED = 994
SAMPLE_SIZE = 20
LEADS = (1, 2, 3, 4, 5)
TARGETS = ("bgcr_dispersion_bps", "on_rrp_change_bn", "sofr_dispersion_bps")

#: Where the hand and the module differ, as `{target: reason}`; empty when they agree everywhere.
DISAGREEMENTS: dict = {}


def _script(name):
    spec = importlib.util.spec_from_file_location(name + "_994", ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BUILT = {}


def h9_panel():
    """The H9 panel CSV, built once per process from the tracked fixtures (see the module docstring)."""

    if not _BUILT:
        published = panel_cache.published_build()["path"]
        directory = Path(tempfile.mkdtemp())
        early = directory / "EW.csv"
        h9 = directory / "H9.csv"
        s639 = _script("richer_targets_639")
        with contextlib.redirect_stdout(io.StringIO()):
            _script("early_warning_inputs").panel_command(SimpleNamespace(panel=published, output=early, end=None))
            s639.panel_command(SimpleNamespace(panel=published, extra=[early], output=h9))
        _BUILT.update(path=h9, s639=s639)
    return _BUILT


class _Hand:
    """B1 and B2 of one target from the CSV alone, written without reference to the module."""

    GRID = (0.01, 0.025, 0.05) + tuple(round(0.10 + 0.05 * k, 2) for k in range(17)) + (0.95, 0.975, 0.99)
    MIN_CHANGES = 60
    MIN_CLIMATE = 4

    def __init__(self, path, target):
        raw = []
        with open(path, newline="", encoding="utf-8") as handle:
            for r in csv.DictReader(handle):
                raw.append(r)
        cell = lambda r, name: float(r[name]) if r[name] != "" else None
        series = []
        for k, r in enumerate(raw):
            if target == "on_rrp_change_bn":
                now, before = cell(r, "on_rrp"), cell(raw[k - 1], "on_rrp") if k else None
                value = None if now is None or before is None else now - before
            else:
                prefix = target.split("_")[0]
                high, low = cell(r, prefix + "_p99"), cell(r, prefix + "_p1")
                value = None if high is None or low is None else (high - low) * 100.0
            written = cell(r, target)
            if (value is None) != (written is None) or (value is not None and abs(value - written) > 1e-9):
                raise AssertionError(f"{target} on {r['date']}: the hand's {value} is not the CSV's {written}")
            series.append(
                (date.fromisoformat(r["date"]), value, float(r["quarter_end"]), float(r["tax_date"]))
            )
        drop = 0
        while series[drop][1] is None:
            drop += 1
        assert drop <= 1
        self.rows = series[drop:]

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

    def b1(self, i):
        """Per lead, the last public value plus the lead's own changes of the trailing two years, or None."""

        anchor = i - 1
        last = self.rows[anchor][1]
        first = self.first_after(self.back(self.rows[i][0], 2))
        out = {}
        for h in LEADS:
            changes = [
                self.rows[s][1] - self.rows[s - h][1]
                for s in range(max(first, h), anchor + 1)
                if self.rows[s][1] is not None and self.rows[s - h][1] is not None
            ]
            ok = last is not None and len(changes) >= self.MIN_CHANGES
            out[h] = [last + self.quantile(changes, p) for p in self.GRID] if ok else None
        return anchor, out

    def b2(self, i):
        """Per lead, the trailing year's values on days of the target day's type, or None."""

        anchor = i - 1
        first = self.first_after(self.back(self.rows[i][0], 1))
        kinds = {s: self.kind(s) for s in range(first, anchor + 1)}
        out, meta = {}, {}
        for h in LEADS:
            kind = self.kind(i + h)
            sample = [self.rows[s][1] for s, k in kinds.items() if k == kind and self.rows[s][1] is not None]
            out[h] = [self.quantile(sample, p) for p in self.GRID] if len(sample) >= self.MIN_CLIMATE else None
            meta[h] = (kind, len(sample))
        return out, meta


def sampled_positions(hand):
    candidates = [
        i for i, row in enumerate(hand.rows) if row[0] >= SAMPLE_FIRST and i + max(LEADS) < len(hand.rows)
    ]
    return sorted(random.Random(SAMPLE_SEED).sample(candidates, SAMPLE_SIZE))


class _OnePanel(unittest.TestCase):
    """Per target: the hand, the sampled decision days and the module's inputs, as the 706 script forms them."""

    @classmethod
    def setUpClass(cls):
        built = h9_panel()
        cls.path = built["path"]
        cls.registry = measurement_fields.load_registry()
        cls.hands = {t: _Hand(cls.path, t) for t in TARGETS}
        cls.positions = {t: sampled_positions(cls.hands[t]) for t in TARGETS}
        cls.module = {}
        for t in TARGETS:
            drop = 0
            rows = load_daily_panel(cls.path)
            while rows[drop].values.get(t) is None:
                drop += 1
            rows = rows[drop:]
            dates = [row.date for row in rows]
            values = [float(row.values[t]) for row in rows]
            kinds = [SPLITS.reporting_day_type(row.date, row.values) for row in rows]
            scored = [i + 1 for i in cls.positions[t]]
            with built["s639"].switched():
                reads = richer_targets.as_of_rows(
                    rows, cls.registry, [t], leads=(1,), scored=scored, decision_time=DECISION
                )
            cls.module[t] = SimpleNamespace(
                rows=rows, dates=dates, values=values, kinds=kinds, anchors=dict(zip(cls.positions[t], reads[1][t]))
            )


class SamplingTests(_OnePanel):
    def test_the_sample_is_twenty_days_per_target_and_reads_nothing_past_the_last_target_day(self):
        for t in TARGETS:
            positions = self.positions[t]
            hand = self.hands[t]
            with self.subTest(target=t):
                self.assertEqual(len(set(positions)), SAMPLE_SIZE)
                self.assertTrue(all(i + max(LEADS) < len(hand.rows) for i in positions))
                days = [hand.rows[i + h][0] for i in positions for h in (0,) + LEADS]
                self.assertLessEqual(max(days), LAST_TARGET)
                self.assertGreaterEqual(min(hand.rows[i][0] for i in positions), SAMPLE_FIRST)

    def test_the_panel_stops_on_the_last_target_day(self):
        for t in TARGETS:
            self.assertEqual(self.hands[t].rows[-1][0], LAST_TARGET)

    def test_the_sample_is_the_recorded_one(self):
        recorded = {t: [self.hands[t].rows[i][0].isoformat() for i in self.positions[t]] for t in TARGETS}
        for t in TARGETS:
            with self.subTest(target=t):
                self.assertEqual(recorded[t], RECORDED_DAYS[t])


class AnchorTests(_OnePanel):
    def test_the_last_public_row_is_the_day_before_the_decision_day(self):
        for t in TARGETS:
            for i in self.positions[t]:
                with self.subTest(target=t, day=self.hands[t].rows[i][0]):
                    self.assertEqual(self.module[t].anchors[i], i - 1)


class B1Tests(_OnePanel):
    @unittest.skipIf("b1" in DISAGREEMENTS, "see DISAGREEMENTS")
    def test_b1_matches_the_hand_on_every_lead_and_level(self):
        formed = {t: 0 for t in TARGETS}
        for t in TARGETS:
            m = self.module[t]
            for i in self.positions[t]:
                anchor, expected = self.hands[t].b1(i)
                first = richer_targets.window_first(m.dates, i, 2)
                for h in LEADS:
                    got = richer_targets.b1_quantiles(m.values, m.dates, m.anchors[i], h, first=first)
                    with self.subTest(target=t, day=m.dates[i], h=h):
                        self.assertEqual(got is None, expected[h] is None)
                        if got is not None:
                            formed[t] += 1
                            for a, b in zip(got, expected[h]):
                                self.assertAlmostEqual(a, b, places=9)
        for t in TARGETS:
            self.assertEqual(formed[t], SAMPLE_SIZE * len(LEADS), t)


class B2Tests(_OnePanel):
    @unittest.skipIf("b2" in DISAGREEMENTS, "see DISAGREEMENTS")
    def test_b2_matches_the_hand_on_every_lead_and_level(self):
        for t in TARGETS:
            m = self.module[t]
            for i in self.positions[t]:
                expected, meta = self.hands[t].b2(i)
                first = richer_targets.window_first(m.dates, i, 1)
                for h in LEADS:
                    got = richer_targets.b2_quantiles(m.values, m.kinds, m.dates, m.anchors[i], m.kinds[i + h], first=first)
                    with self.subTest(target=t, day=m.dates[i], h=h):
                        self.assertEqual(m.kinds[i + h], meta[h][0])
                        self.assertEqual(got is None, expected[h] is None)
                        if got is not None:
                            for a, b in zip(got, expected[h]):
                                self.assertAlmostEqual(a, b, places=9)


#: The sampled decision days, computed by `_Hand` on the panel built from the fixtures, 20 October 2026. The three targets
#: share them: the same seed draws the same ordinal among the same dates, and the one row `on_rrp_change_bn` lacks is before the first.
_DAYS = (
    "2019-08-12", "2019-12-10", "2020-04-20", "2020-05-21",
    "2020-06-24", "2020-07-15", "2020-08-17", "2021-10-26",
    "2021-11-16", "2022-07-12", "2022-08-09", "2022-09-07",
    "2023-09-20", "2024-01-12", "2024-11-06", "2025-03-07",
    "2025-07-31", "2025-09-23", "2025-11-10", "2025-11-21",
)
RECORDED_DAYS = {t: list(_DAYS) for t in TARGETS}


if __name__ == "__main__":
    unittest.main()
