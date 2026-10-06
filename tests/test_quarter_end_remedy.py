"""Quarter-end remedies, layered on pressure model v2 (#327).

v2's 50% band covers about 30% of quarter-end days (`docs/pivot/quarter-end-diagnosis.md`). The
remedies of `scripts/quarter_end_remedy.py` are turn layers on v2's vectors, each estimated across every
earlier quarter-end rather than learned by trees from 23 days. These tests hold them to the declaration:

* `DeclarationTests`: at least three candidates declared before anything is scored, a declared choice
  rule, a layer that touches quarter-end days only, and the lockbox (no day after 2025-12-31).
* `LayerTests`: each remedy issues the vector its definition gives, leaves every other day alone, and
  never crosses its quantiles.
* `ObservabilityTests`: a quarter-end whose label was not public at the decision anchor never reaches
  the estimate (`LookAheadError`).

Red first: `scripts/quarter_end_remedy.py` did not exist (`FileNotFoundError` on import).

Mutation record (`ObservabilityTests`, the remedy's label guard). Disposable copy of the tree, CPython
3.11, `PYTHONDONTWRITEBYTECODE=1`, the class run alone, control green. In `quarter_end_remedy._adjusted`,
`if past["date"] > day["anchor"]:` was changed to `if False:`, and `diff` against the tree confirmed it was
applied. `test_a_label_after_the_anchor_is_refused` then failed with `AssertionError: LookAheadError not
raised`. Restored, green.

Mutation record (`DeclarationTests`, the lockbox). Same copy and setup. In `quarter_end_remedy.require_read_window`,
`if end > LAST_READ:` was changed to `if False:`, and `diff` confirmed it was applied.
`test_a_day_after_the_last_read_day_is_refused` (of `DeclarationTests`) then failed with `AssertionError:
ValueError not raised`. Restored, green.
"""

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.splits import LookAheadError  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("quarter_end_remedy_under_test",
                                                  REPO / "scripts" / "quarter_end_remedy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qe = _load()

BASE_VECTOR = [-4.0, -2.0, 0.0, 2.0, 4.0]


def _day(when, kind, residual=0.0, vector=None):
    """A scored day: v2's vector, and an outcome `residual` bp above its median."""

    vector = list(vector or BASE_VECTOR)
    return {"date": when.isoformat(), "anchor": (when - timedelta(days=1)).isoformat(),
            "y": vector[2] + residual, "v2": vector, "type": kind}


def _history(residuals, kind="quarter_end"):
    start = date(2019, 3, 29)
    return [_day(start + timedelta(days=91 * k), kind, r) for k, r in enumerate(residuals)]


class DeclarationTests(unittest.TestCase):
    def test_at_least_three_remedies_are_declared_besides_the_base(self):
        built = [name for name in qe.CANDIDATES if name != "base"]
        self.assertGreaterEqual(len(built), 3)
        for name, spec in qe.CANDIDATES.items():
            self.assertIn("what", spec)
            self.assertIn("complexity", spec)

    def test_the_choice_rule_and_the_blocks_are_declared(self):
        self.assertEqual(qe.INNER, (date(2018, 6, 29), date(2022, 12, 31)))
        self.assertEqual(qe.OUTER, (date(2023, 1, 1), date(2025, 12, 31)))
        self.assertEqual(qe.LAST_READ, date(2025, 12, 31))
        for key in ("window", "rule", "eligible", "none_eligible", "outer"):
            self.assertIn(key, qe.SELECTION)

    def test_the_market_calendar_column_is_declared_not_built(self):
        self.assertIn("days_to_quarter_end_market_calendar", qe.NOT_BUILT)

    def test_a_day_after_the_last_read_day_is_refused(self):
        qe.require_read_window(date(2025, 12, 31))
        with self.assertRaises(ValueError):
            qe.require_read_window(date(2026, 1, 2))


class LayerTests(unittest.TestCase):
    def test_base_returns_v2_unchanged(self):
        days = _history([5.0] * 6) + [_day(date(2021, 3, 31), "quarter_end", 5.0)]
        out = qe.walk(days, "base")
        self.assertEqual(out, [d["v2"] for d in days])

    def test_every_remedy_leaves_non_quarter_end_days_alone(self):
        past = _history([6.0] * 12)
        ordinary = _day(date(2021, 5, 12), "ordinary", 1.0)
        tax = _day(date(2021, 6, 15), "tax_date", 1.0)
        month = _day(date(2021, 4, 30), "month_end", 1.0)
        for name in qe.CANDIDATES:
            out = qe.walk(past + [month, tax, ordinary], name)
            self.assertEqual(out[-3:], [BASE_VECTOR] * 3, name)

    def test_qe_shift_adds_the_median_past_residual_to_every_quantile(self):
        past = _history([4.0, 6.0, 8.0, 10.0, 100.0])
        target = _day(date(2021, 6, 30), "quarter_end", 0.0)
        out = qe.walk(past + [target], "qe_shift")[-1]
        self.assertEqual(out, [q + 8.0 for q in BASE_VECTOR])

    def test_too_few_past_quarter_ends_leave_the_vector_alone(self):
        past = _history([9.0, 9.0, 9.0])
        target = _day(date(2020, 3, 31), "quarter_end", 0.0)
        for name in qe.CANDIDATES:
            self.assertEqual(qe.walk(past + [target], name)[-1], BASE_VECTOR, name)

    def test_qe_shift_width_widens_about_the_shifted_median(self):
        # The median residual is 2 bp; |e - 2| has median 8 against v2's half-IQR of 2, so the scale is 4.
        past = _history([-6.0, 2.0, 2.0, 10.0, 10.0])
        target = _day(date(2021, 6, 30), "quarter_end", 0.0)
        out = qe.walk(past + [target], "qe_shift_width")[-1]
        self.assertEqual(out, [2.0 + 4.0 * q for q in BASE_VECTOR])

    def test_the_recent_shift_reads_the_last_four_quarter_ends_only(self):
        # Early quarter-ends at +20 bp, the last four at -10 bp: the all-history median is still +20.
        past = _history([20.0] * 6 + [-10.0] * 4)
        target = _day(date(2023, 6, 30), "quarter_end", 0.0)
        recent = qe.walk(past + [target], "qe_shift_recent")[-1]
        whole = qe.walk(past + [target], "qe_shift")[-1]
        self.assertEqual(recent, [q - 10.0 for q in BASE_VECTOR])
        self.assertEqual(whole, [q + 20.0 for q in BASE_VECTOR])

    def test_the_recent_width_remedy_widens_by_the_last_four_only(self):
        # Last four residuals -6, -6, 10, 10: median 2, |e - 2| all 8 (the earlier 0s are not read), scale 4.
        past = _history([0.0, 0.0, 0.0, -6.0, -6.0, 10.0, 10.0])
        target = _day(date(2023, 6, 30), "quarter_end", 0.0)
        out = qe.walk(past + [target], "qe_shift_width_recent")[-1]
        self.assertEqual(out, [2.0 + 4.0 * q for q in BASE_VECTOR])

    def test_the_scale_never_narrows_the_band(self):
        past = _history([1.0, -1.0, 1.0, -1.0, 1.0])
        target = _day(date(2021, 6, 30), "quarter_end", 0.0)
        out = qe.walk(past + [target], "qe_shift_width")[-1]
        spread = [b - a for a, b in zip(out, out[1:])]
        self.assertTrue(all(s >= 2.0 - 1e-12 for s in spread))

    def test_turn_pool_shrinks_the_quarter_end_median_toward_the_month_end_median(self):
        quarter = _history([10.0] * 4)
        month = _history([2.0] * 8, kind="month_end")
        month = [dict(d, date=(date.fromisoformat(d["date"]) + timedelta(days=30)).isoformat(),
                      anchor=(date.fromisoformat(d["date"]) + timedelta(days=29)).isoformat()) for d in month]
        target = _day(date(2022, 1, 31), "quarter_end", 0.0)
        out = qe.walk(sorted(quarter + month, key=lambda d: d["date"]) + [target], "turn_pool")[-1]
        shift = (4 * 10.0 + qe.POOL_WEIGHT * 2.0) / (4 + qe.POOL_WEIGHT)
        self.assertEqual(out, [q + shift for q in BASE_VECTOR])

    def test_the_empirical_model_takes_the_past_residual_quantiles_about_the_median(self):
        residuals = [float(k) for k in range(-4, 5)]  # nine residuals, -4 .. 4
        past = _history(residuals)
        target = _day(date(2022, 3, 31), "quarter_end", 0.0)
        out = qe.walk(past + [target], "qe_empirical")[-1]
        self.assertEqual(out[2], 0.0)
        self.assertEqual(out[0], qe._quantile(residuals, 0.05))
        self.assertEqual(out[4], qe._quantile(residuals, 0.95))

    def test_no_remedy_crosses_its_quantiles(self):
        past = _history([-7.0, 3.0, 9.0, 0.0, 14.0, -2.0, 5.0, 11.0, 1.0, 6.0])
        target = _day(date(2022, 3, 31), "quarter_end", 0.0)
        for name in qe.CANDIDATES:
            out = qe.walk(past + [target], name)[-1]
            self.assertEqual(out, sorted(out), name)

    def test_the_estimate_reads_residuals_against_v2_not_against_an_earlier_remedy(self):
        past = _history([8.0] * 6)
        target = _day(date(2021, 9, 30), "quarter_end", 0.0)
        one = qe.walk(past + [target], "qe_shift")
        # an earlier day's remedied vector does not feed the next day's estimate
        self.assertEqual(one[5], [q + 8.0 for q in BASE_VECTOR])
        self.assertEqual(one[-1], [q + 8.0 for q in BASE_VECTOR])


class ObservabilityTests(unittest.TestCase):
    def test_a_label_after_the_anchor_is_refused(self):
        past = _history([5.0] * 6)
        target = _day(date(2021, 6, 30), "quarter_end", 0.0)
        late = dict(past[-1], date=date(2021, 6, 30).isoformat())  # the target's own label, on its own day
        with self.assertRaises(LookAheadError):
            qe._adjusted(target, past[:-1] + [late], "qe_shift")

    def test_a_quarter_end_labelled_by_the_anchor_is_used(self):
        past = _history([5.0] * 6)
        target = dict(_day(date(2021, 6, 30), "quarter_end", 0.0), anchor=past[-1]["date"])
        out = qe._adjusted(target, past, "qe_shift")
        self.assertEqual(out, [q + 5.0 for q in BASE_VECTOR])

    def test_the_walk_uses_only_days_labelled_by_the_anchor(self):
        # The last past quarter-end is public only after the target's anchor: it must not count.
        past = _history([5.0] * 5 + [500.0])
        target = _day(date(2021, 6, 30), "quarter_end", 0.0)
        target["anchor"] = (date.fromisoformat(past[-1]["date"]) - timedelta(days=1)).isoformat()
        out = qe.walk(past + [target], "qe_shift")[-1]
        self.assertEqual(out, [q + 5.0 for q in BASE_VECTOR])


if __name__ == "__main__":
    unittest.main()
