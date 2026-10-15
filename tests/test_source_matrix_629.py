"""Inter-source correlations and ordinary-day screen of the sources we hold (#629): `scripts/source_matrix_629.py`.

Held to hand-worked values: the statistics (a pairwise Spearman, an AUROC and its bootstrap interval, complete-linkage
clusters, a partial rank correlation), the ordinary-day rule, and the two guards that keep the screen off locked days and off
the back-filled 2014-18 history (`posting_instant` is null, #572).

Recorded mutations, 12 October 2026, in a disposable copy of `scripts/source_matrix_629.py` (control green before and after):
1. in `require_panel_window`, `if rows[-1].date > LAST_DAY:` -> `if False:` (a panel past 2025-12-31 is accepted).
   `PanelGuardTests.test_a_panel_past_the_last_day_is_refused` then fails with `AssertionError: LookAheadError not raised`.
2. in `require_no_backfill`, `if rows[0].date < backfill.FIRST_PUBLISHED:` -> `if False:` (a panel that carries back-filled days is accepted).
   `PanelGuardTests.test_a_panel_with_backfilled_days_is_refused` then fails with `AssertionError: LookAheadError not raised`.
3. in `complete_linkage`, the merge test `link >= threshold` where `link` is the smallest |rho| across the two clusters, replaced by
   the largest (single linkage). `ClusterTests.test_a_chain_is_not_one_group` then fails with
   `AssertionError: [['a', 'b', 'c'], ['d']] != [['a', 'b'], ['c'], ['d']]`.
4. in `risk_dates.non_ordinary_day` (which `is_ordinary` calls since #682), `> 0.0` -> `>= 0.0` on the coupon clause (a day with no coupon settlement is a risk date).
   `OrdinaryTests.test_a_day_with_no_coupon_settlement_is_ordinary` then fails with `AssertionError: False is not true`.
"""

from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def _script():
    spec = importlib.util.spec_from_file_location("source_matrix_629_script", ROOT / "scripts" / "source_matrix_629.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["source_matrix_629_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()
DECLARED = json.loads((ROOT / "metadata" / "source_matrix_629.json").read_text())


def _row(day: date) -> DailyObservation:
    return DailyObservation(day, {"sofr": 1.0, "iorb": 1.0})


class DeclarationTests(unittest.TestCase):
    def test_the_choices_are_the_directives(self):
        self.assertEqual(DECLARED["issue"], 629)
        self.assertEqual(DECLARED["leads"], [1, 2, 3, 5, 10])
        self.assertEqual(DECLARED["cluster"]["threshold"], 0.8)
        self.assertEqual(tuple(DECLARED["leads"]), SCRIPT.LEADS)
        self.assertEqual(DECLARED["cluster"]["threshold"], SCRIPT.CLUSTER_THRESHOLD)
        self.assertEqual(DECLARED["targets"], ["pressure", "level", "change"])
        self.assertEqual(DECLARED["bootstrap"]["level"], 0.9)

    def test_the_series_list_has_no_duplicates(self):
        names = DECLARED["series"]["names"]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(names), DECLARED["series"]["count"])


class PanelGuardTests(unittest.TestCase):
    def test_a_panel_past_the_last_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            SCRIPT.require_panel_window([_row(date(2025, 12, 30)), _row(date(2026, 1, 2))])

    def test_a_panel_ending_on_the_last_day_is_accepted(self):
        SCRIPT.require_panel_window([_row(date(2025, 12, 30)), _row(date(2025, 12, 31))])

    def test_a_panel_with_backfilled_days_is_refused(self):
        with self.assertRaises(LookAheadError):
            SCRIPT.require_no_backfill([_row(date(2014, 1, 2)), _row(date(2018, 4, 3))])

    def test_a_panel_starting_at_the_first_published_day_is_accepted(self):
        SCRIPT.require_no_backfill([_row(date(2018, 4, 3)), _row(date(2018, 4, 4))])


class OrdinaryTests(unittest.TestCase):
    def test_a_plain_day_is_ordinary(self):
        self.assertTrue(SCRIPT.is_ordinary("ordinary", 0.0))

    def test_a_day_with_no_coupon_settlement_is_ordinary(self):
        self.assertTrue(SCRIPT.is_ordinary("ordinary", 0.0))
        self.assertTrue(SCRIPT.is_ordinary("ordinary", None))

    def test_a_coupon_settlement_day_is_a_risk_date(self):
        self.assertFalse(SCRIPT.is_ordinary("ordinary", 12.5))

    def test_a_calendar_risk_date_is_not_ordinary(self):
        for kind in ("quarter_end", "month_end", "tax_date"):
            self.assertFalse(SCRIPT.is_ordinary(kind, 0.0))


class StatisticsTests(unittest.TestCase):
    def test_spearman_drops_holes_and_counts_the_days(self):
        rho, n = SCRIPT.spearman_pairwise([1.0, 2.0, None, 4.0, 5.0], [10.0, 20.0, 99.0, 40.0, None])
        self.assertEqual(n, 3)
        self.assertAlmostEqual(rho, 1.0)

    def test_spearman_is_none_for_a_constant_side(self):
        rho, n = SCRIPT.spearman_pairwise([1.0, 1.0, 1.0], [1.0, 2.0, 3.0])
        self.assertIsNone(rho)
        self.assertEqual(n, 3)

    def test_auc_of_a_perfect_ranking(self):
        self.assertEqual(SCRIPT.auc([1.0, 2.0, 3.0, 4.0], [0, 0, 1, 1]), 1.0)
        self.assertEqual(SCRIPT.auc([4.0, 3.0, 2.0, 1.0], [0, 0, 1, 1]), 0.0)

    def test_auc_counts_a_tie_as_half(self):
        self.assertEqual(SCRIPT.auc([1.0, 1.0], [0, 1]), 0.5)
        # events 3 and 1, others 2 and 1: pairs (3,2) 1, (3,1) 1, (1,2) 0, (1,1) .5 -> 2.5 / 4
        self.assertAlmostEqual(SCRIPT.auc([3.0, 1.0, 2.0, 1.0], [1, 1, 0, 0]), 0.625)

    def test_auc_skips_holes_and_is_none_without_both_classes(self):
        self.assertEqual(SCRIPT.auc([1.0, None, 3.0], [0, 1, 1]), 1.0)
        self.assertIsNone(SCRIPT.auc([1.0, 2.0], [1, 1]))

    def test_the_identity_resample_gives_a_point_interval(self):
        values = [1.0, 2.0, 3.0, 4.0, 2.5, 3.5]
        labels = [0, 0, 1, 1, 0, 1]
        identity = tuple(range(6))
        low, high = SCRIPT.bootstrap_interval(values, labels, [identity] * 5, level=0.9)
        self.assertAlmostEqual(low, SCRIPT.auc(values, labels))
        self.assertAlmostEqual(high, SCRIPT.auc(values, labels))

    def test_the_bootstrap_auc_agrees_with_the_direct_one_on_a_resample(self):
        rng = random.Random(7)
        values = [rng.gauss(0, 1) for _ in range(60)]
        labels = [1 if rng.random() < 0.3 else 0 for _ in range(60)]
        resample = tuple(rng.randrange(60) for _ in range(60))
        direct = SCRIPT.auc([values[i] for i in resample], [labels[i] for i in resample])
        self.assertAlmostEqual(SCRIPT.resampled_auc(values, labels, resample), direct)


class ClusterTests(unittest.TestCase):
    NAMES = ["a", "b", "c", "d"]

    def _rho(self):
        table = {("a", "b"): 0.9, ("b", "c"): 0.85, ("a", "c"): 0.5}
        return lambda x, y: table.get((x, y), table.get((y, x), 0.0))

    def test_a_chain_is_not_one_group(self):
        groups = SCRIPT.complete_linkage(self.NAMES, self._rho(), 0.8)
        self.assertEqual(groups, [["a", "b"], ["c"], ["d"]])

    def test_the_sign_does_not_matter(self):
        groups = SCRIPT.complete_linkage(["a", "b"], lambda x, y: -0.95, 0.8)
        self.assertEqual(groups, [["a", "b"]])

    def test_a_missing_correlation_never_joins(self):
        groups = SCRIPT.complete_linkage(["a", "b"], lambda x, y: None, 0.8)
        self.assertEqual(groups, [["a"], ["b"]])

    def test_the_representative_is_the_medoid(self):
        table = {("a", "b"): 0.95, ("a", "c"): 0.85, ("b", "c"): 0.9}
        rho = lambda x, y: table.get((x, y), table.get((y, x)))
        # mean |rho| to the others: a .90, b .925, c .875
        self.assertEqual(SCRIPT.medoid(["a", "b", "c"], rho), "b")
        self.assertEqual(SCRIPT.medoid(["z"], rho), "z")


class PartialTests(unittest.TestCase):
    def test_one_control_matches_the_textbook_formula(self):
        x = [1.0, 3.0, 2.0, 4.0, 6.0, 5.0, 8.0, 7.0]
        y = [2.0, 1.0, 4.0, 3.0, 6.0, 8.0, 5.0, 7.0]
        c = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        rxy, _ = SCRIPT.spearman_pairwise(x, y)
        rxc, _ = SCRIPT.spearman_pairwise(x, c)
        ryc, _ = SCRIPT.spearman_pairwise(y, c)
        expected = (rxy - rxc * ryc) / math.sqrt((1 - rxc**2) * (1 - ryc**2))
        self.assertAlmostEqual(SCRIPT.partial_spearman(x, y, [c]), expected)

    def test_a_series_that_is_its_control_has_nothing_left(self):
        c = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertIsNone(SCRIPT.partial_spearman(c, [2.0, 1.0, 4.0, 3.0, 5.0], [c]))

    def test_collinear_controls_are_refused_with_none(self):
        c = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        self.assertIsNone(SCRIPT.partial_spearman([1.0, 3.0, 2.0, 5.0, 4.0, 6.0], [2.0, 1.0, 4.0, 3.0, 6.0, 5.0], [c, c]))

    def test_holes_in_any_series_drop_the_day(self):
        x = [1.0, 3.0, 2.0, 4.0, 6.0, 5.0, None, 7.0]
        y = [2.0, 1.0, 4.0, 3.0, 6.0, 8.0, 5.0, 7.0]
        c = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, None]
        a = SCRIPT.partial_spearman(x, y, [c])
        b = SCRIPT.partial_spearman(x[:6], y[:6], [c[:6]])
        self.assertAlmostEqual(a, b)


if __name__ == "__main__":
    unittest.main()
