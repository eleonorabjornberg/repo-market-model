"""The onset diagnostics (#429): where the false alarms fall, and what 26 onsets can prove.

Reported-only measurements on top of the judge of #375 as amended by #407. They change no bar, no
declaration and no published figure. The declaration is `metadata/onset_diagnostics.json`.

Mutation record
---------------
The one guard here is `nearest_pressure_distance`: the distance of a flagged day to the nearest pressure
day is read on the days to the declared last scored day only, and refuses a day or a pressure day after it
(`docs/decisions/lockbox.md`). Applied in a scratch copy, the unmutated suite green before and after:

1. In `repo_model/onset_diagnostics.py`, `nearest_pressure_distance`, replace
   `if position > last_position or late:` with `if False:`. Killed:
   `test_a_pressure_day_after_the_last_scored_day_is_refused` and
   `test_a_flagged_day_after_the_last_scored_day_is_refused`, both with `AssertionError`
   (`LookAheadError not raised`).
"""

import json
import math
import random
import unittest
from pathlib import Path

from repo_model import onset_diagnostics as od
from repo_model import pressure_judge as pj
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "onset_diagnostics.json").read_text())
JUDGE = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())
RESULT = (ROOT / "docs" / "pivot" / "judge-amendment-result.md").read_text()

SPREAD = DECLARED["false_alarms"]["realised_spread_bp"]["buckets"]
DISTANCE = DECLARED["false_alarms"]["distance_to_pressure_day"]["buckets"]


def table_one():
    """{model: (onsets flagged, worst false alarms per onset)} from Table 1 of the re-judge."""

    rows = {}
    inside = False
    for line in RESULT.splitlines():
        if line.startswith("Table 1."):
            inside = True
            continue
        if inside and line.startswith("Table 2."):
            break
        if inside and line.startswith("| ") and not line.startswith("| model") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows[cells[0]] = (int(cells[1].split(" of ")[0]), float(cells[4]))
    return rows


class DeclarationTests(unittest.TestCase):
    def test_the_five_rows_follow_the_declared_rule_from_table_one(self):
        rows = table_one()
        self.assertGreater(len(rows), 20)
        excluded = set(DECLARED["false_alarms"]["rows"]["excluded"])
        ranked = sorted((n for n in rows if n not in excluded), key=lambda n: (-rows[n][0], rows[n][1], n))
        self.assertEqual(DECLARED["false_alarms"]["rows"]["chosen"], ranked[:5])

    def test_the_window_and_threshold_are_the_judges(self):
        self.assertEqual(DECLARED["scoring"]["last_day"], JUDGE["scoring"]["last_day"])
        self.assertEqual(DECLARED["scoring"]["primary_threshold_bp"], JUDGE["primary_threshold_bp"])

    def test_the_buckets_cover_every_non_pressure_spread_once(self):
        for spread in range(-40, 6):
            hits = [b for b in SPREAD if od.in_bucket(spread, b)]
            self.assertEqual(len(hits), 1, spread)
        for spread in range(6, 40):
            self.assertEqual([b for b in SPREAD if od.in_bucket(spread, b)], [], spread)

    def test_the_distance_buckets_cover_every_distance_once(self):
        for distance in range(1, 400):
            self.assertEqual(len([b for b in DISTANCE if od.in_bucket(distance, b)]), 1, distance)

    def test_the_confirmation_window_is_the_lockbox_record_and_no_day_is_read(self):
        window = DECLARED["power"]["confirmation_window"]
        self.assertEqual(window["days"], 169)
        self.assertLessEqual(max(window["onsets"]), 5)
        self.assertIn("| **2026-01-01** | **169** | **5** |", (ROOT / "docs" / "decisions" / "lockbox.md").read_text())


class SpreadBucketTests(unittest.TestCase):
    def test_a_spread_is_read_on_whole_basis_points(self):
        # SOFR 2.00 less IORB 1.95 is 5.000000000000004 bp: on the whole basis point it is +5, not above it.
        self.assertEqual(od.spread_bucket(5.000000000000004, SPREAD), "+4 to +5 bp")
        self.assertEqual(od.spread_bucket(3.6, SPREAD), "+4 to +5 bp")
        self.assertEqual(od.spread_bucket(3.4, SPREAD), "+1 to +3 bp")
        self.assertEqual(od.spread_bucket(0.4, SPREAD), "0 bp or below")
        self.assertEqual(od.spread_bucket(-7.0, SPREAD), "0 bp or below")

    def test_a_pressure_day_has_no_bucket(self):
        with self.assertRaises(ValueError):
            od.spread_bucket(6.2, SPREAD)


class DistanceTests(unittest.TestCase):
    def test_the_nearest_pressure_day_either_side(self):
        self.assertEqual(od.nearest_pressure_distance(10, [4, 15], 100), 5)
        self.assertEqual(od.nearest_pressure_distance(10, [4, 11], 100), 1)
        self.assertEqual(od.nearest_pressure_distance(0, [7], 100), 7)

    def test_no_pressure_day_has_no_distance(self):
        self.assertIsNone(od.nearest_pressure_distance(3, [], 100))

    def test_a_pressure_day_after_the_last_scored_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            od.nearest_pressure_distance(10, [4, 101], 100)

    def test_a_flagged_day_after_the_last_scored_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            od.nearest_pressure_distance(101, [4], 100)

    def test_a_flagged_day_on_a_pressure_day_is_refused(self):
        with self.assertRaises(ValueError):
            od.nearest_pressure_distance(4, [4], 100)


class FalseAlarmTests(unittest.TestCase):
    def setUp(self):
        # Eight panel days; day 2 and day 6 are pressure days.
        self.args = dict(
            positions=[0, 1, 2, 3, 4, 5, 6, 7],
            flags=[1, 1, 1, 0, 1, 0, 1, 1],
            pressure=[0, 0, 1, 0, 0, 0, 1, 0],
            spreads=[-3.0, 4.2, 7.0, 1.0, 2.2, 0.0, 9.0, 3.0],
            day_types=["ordinary", "month_end", "ordinary", "ordinary", "tax_date", "ordinary", "ordinary", "quarter_end"],
            regimes=["a", "a", "a", "a", "b", "b", "b", "b"],
            pressure_positions=[2, 6],
            last_position=7,
            spread_buckets=SPREAD,
            distance_buckets=DISTANCE,
        )

    def test_a_flag_on_a_pressure_day_is_a_hit_not_a_false_alarm(self):
        records = od.false_alarm_records(**self.args)
        self.assertEqual([r["position"] for r in records], [0, 1, 4, 7])

    def test_each_record_carries_its_bucket_distance_and_group(self):
        records = {r["position"]: r for r in od.false_alarm_records(**self.args)}
        self.assertEqual(records[1]["spread_bucket"], "+4 to +5 bp")
        self.assertEqual(records[1]["distance"], 1)
        self.assertEqual(records[1]["distance_bucket"], "1 day")
        self.assertEqual(records[4]["distance"], 2)
        self.assertEqual(records[4]["day_type"], "tax_date")
        self.assertEqual(records[0]["spread_bucket"], "0 bp or below")
        self.assertEqual(records[0]["distance_bucket"], "2 to 5 days")
        self.assertEqual(records[7]["distance"], 1)

    def test_the_splits_sum_to_the_total(self):
        records = od.false_alarm_records(**self.args)
        for key, labels in (
            ("spread_bucket", [b["label"] for b in SPREAD]),
            ("distance_bucket", [b["label"] for b in DISTANCE]),
            ("day_type", ["month_end", "ordinary", "quarter_end", "tax_date"]),
            ("regime", ["a", "b"]),
        ):
            counts = od.tabulate(records, key, labels)
            self.assertEqual(list(counts), labels)
            self.assertEqual(sum(counts.values()), len(records), key)

    def test_a_label_outside_the_list_is_refused(self):
        records = od.false_alarm_records(**self.args)
        with self.assertRaises(ValueError):
            od.tabulate(records, "regime", ["a"])


class BootstrapTests(unittest.TestCase):
    def test_a_block_counts_the_onsets_it_covers_wrapping_at_the_end(self):
        positions = [1, 5, 8]
        caught = [1, 0, 1]
        # A block from day 7 of length 5 covers days 7, 8, 9 (n = 10), then 0, 1.
        onsets, flagged = od.block_totals(positions, caught, 10, 7, 5)
        self.assertEqual((onsets, flagged), (2, 2))
        onsets, flagged = od.block_totals(positions, caught, 10, 2, 4)
        self.assertEqual((onsets, flagged), (1, 0))

    def test_blocks_cover_exactly_n_days(self):
        rng = random.Random(1)
        for n in (7, 40, 169):
            blocks = list(od.stationary_blocks(n, 10, rng))
            self.assertEqual(sum(length for _, length in blocks), n)
            self.assertTrue(all(0 <= start < n and length >= 1 for start, length in blocks))

    def test_blocks_match_the_judges_resample_in_distribution(self):
        n, positions = 60, [3, 4, 20, 41, 42, 55]
        caught = [1, 0, 1, 1, 0, 0]
        vector = [0] * n
        for p in positions:
            vector[p] = 1
        rng_a, rng_b = random.Random(5), random.Random(6)
        reference, mine = [], []
        from repo_model.metrics import stationary_bootstrap_indices

        for _ in range(6000):
            reference.append(sum(vector[i] for i in stationary_bootstrap_indices(n, 10, rng_a)))
            mine.append(sum(od.block_totals(positions, caught, n, s, l)[0] for s, l in od.stationary_blocks(n, 10, rng_b)))
        mean_a, mean_b = sum(reference) / 6000, sum(mine) / 6000
        var_a = sum((x - mean_a) ** 2 for x in reference) / 6000
        var_b = sum((x - mean_b) ** 2 for x in mine) / 6000
        self.assertAlmostEqual(mean_a, mean_b, delta=4 * math.sqrt(var_a / 6000) * 1.5)
        self.assertAlmostEqual(math.sqrt(var_a), math.sqrt(var_b), delta=0.1 * math.sqrt(var_a))

    def test_the_interval_quantile_is_the_judges(self):
        data = sorted(random.Random(2).random() for _ in range(101))
        for p in (0.05, 0.5, 0.95):
            self.assertEqual(od.quantile(data, p), pj._quantile(data, p))

    def test_all_flagged_gives_a_degenerate_interval_at_one(self):
        rng = random.Random(3)
        point, lower, upper, undefined = od.recall_interval(
            list(range(0, 100, 5)), [1] * 20, 100, block_length=10, replications=300, level=0.9, rng=rng
        )
        self.assertEqual((point, lower, upper, undefined), (1.0, 1.0, 1.0, 0))

    def test_a_resample_without_an_onset_leaves_the_interval_unavailable(self):
        rng = random.Random(4)
        point, lower, upper, undefined = od.recall_interval(
            [5], [1], 400, block_length=2, replications=300, level=0.9, rng=rng
        )
        self.assertEqual(point, 1.0)
        self.assertGreater(undefined, 0)
        self.assertIsNone(lower)
        self.assertIsNone(upper)


class PowerTests(unittest.TestCase):
    SETTINGS = dict(block_length=10, replications=200, level=0.9)

    def test_the_point_condition_is_the_binomial_tail(self):
        # P(Binomial(26, r) >= 13), checked against a direct sum.
        for r in (0.55, 0.6, 0.7, 0.8):
            direct = sum(math.comb(26, k) * r**k * (1 - r) ** (26 - k) for k in range(13, 27))
            self.assertAlmostEqual(od.binomial_at_least(26, r, 0.5), direct, places=12)

    def test_power_rises_with_the_true_recall(self):
        positions = [20 * k + 7 for k in range(26)]
        out = od.recall_power(
            positions, 520, true_recalls=(0.3, 0.9), climatology_recalls=(0.2,), experiments=60, seed=1, **self.SETTINGS
        )
        low, high = out["0.3"], out["0.9"]
        self.assertLess(low["point_at_least"], high["point_at_least"])
        self.assertLess(low["both"]["0.2"], high["both"]["0.2"])
        self.assertEqual(high["experiments"], 60)

    def test_both_conditions_are_never_likelier_than_either(self):
        positions = [20 * k + 7 for k in range(26)]
        out = od.recall_power(
            positions, 520, true_recalls=(0.6,), climatology_recalls=(0.1, 0.4), experiments=60, seed=2, **self.SETTINGS
        )["0.6"]
        for c in ("0.1", "0.4"):
            self.assertLessEqual(out["both"][c], out["point_at_least"])
            self.assertLessEqual(out["both"][c], out["lower_above"][c])
        self.assertLessEqual(out["lower_above"]["0.4"], out["lower_above"]["0.1"])

    def test_the_same_seed_gives_the_same_figures(self):
        positions = [20 * k + 7 for k in range(26)]
        kwargs = dict(true_recalls=(0.6,), climatology_recalls=(0.2,), experiments=30, seed=7, **self.SETTINGS)
        self.assertEqual(od.recall_power(positions, 520, **kwargs), od.recall_power(positions, 520, **kwargs))

    def test_a_short_window_with_few_onsets_cannot_pass(self):
        positions = od.evenly_spaced(3, 169)
        out = od.recall_power(
            positions, 169, true_recalls=(1.0,), climatology_recalls=(0.1,), experiments=20, seed=3,
            block_length=10, replications=2000, level=0.9,
        )["1"]
        self.assertGreater(out["interval_unavailable"], 0.9)
        self.assertEqual(out["both"]["0.1"], 0.0)

    def test_evenly_spaced_onsets(self):
        positions = od.evenly_spaced(5, 169)
        self.assertEqual(len(positions), 5)
        self.assertEqual(positions, sorted(set(positions)))
        self.assertTrue(all(0 <= p < 169 for p in positions))
        with self.assertRaises(ValueError):
            od.evenly_spaced(0, 169)


if __name__ == "__main__":
    unittest.main()
