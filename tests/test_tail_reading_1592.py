"""The per-tail reading rule with both intervals (#1592): `repo_model.tail_reading`.

A tail is "in line" only when the 90% interval of its ratio holds 1 and the 90% interval of its strict miss share holds the
nominal rate (Eleonora, 12 November 2026, #1592). The cases below include the one that motivated it: the q05 of the
post-month-end days of #1547 (ratio 1.01 [0.82, 1.31], miss share 0.091 [0.056, 0.128] against 0.05), which #1547 called in line.

Recorded mutation (the rule this module adds):

* `tail_call`, the line `if not miss_holds_nominal:` replaced by `if False:`:
  `test_the_post_month_end_q05_is_not_in_line` fails with `AssertionError` ('in line' != 'miss share off') and
  `test_the_real_1547_result_reads_post_month_end_q05_as_off` fails the same way; restored, both pass.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from repo_model.tail_reading import NOMINAL, tail_call

REPO = Path(__file__).resolve().parents[1]


class TailCallTests(unittest.TestCase):
    def test_in_line_needs_both_intervals(self):
        self.assertEqual(tail_call([1.0, 0.9, 1.1], [0.05, 0.04, 0.06], 0.05), "in line")

    def test_the_post_month_end_q05_is_not_in_line(self):
        self.assertEqual(tail_call([1.012, 0.822, 1.314], [0.091, 0.056, 0.128], 0.05), "miss share off")

    def test_the_ratio_call_comes_first(self):
        self.assertEqual(tail_call([1.66, 1.31, 2.24], [0.126, 0.086, 0.175], 0.05), "too thin")
        self.assertEqual(tail_call([0.53, 0.36, 0.67], [0.008, 0.002, 0.016], 0.05), "too wide")

    def test_a_miss_share_below_nominal_is_off_too(self):
        self.assertEqual(tail_call([1.0, 0.9, 1.1], [0.01, 0.005, 0.02], 0.05), "miss share off")

    def test_no_miss_interval_is_not_in_line(self):
        self.assertEqual(tail_call([1.0, 0.9, 1.1], None, 0.05), "ratio holds 1, miss share not read")

    def test_the_nominal_rates(self):
        self.assertEqual(NOMINAL, {"0.01": 0.01, "0.05": 0.05, "0.95": 0.05, "0.99": 0.01})

    def test_the_real_1547_result_reads_post_month_end_q05_as_off(self):
        d = json.loads((REPO / "docs/research/calendar-tail-diagnostic-1547/result.json").read_text(encoding="utf-8"))
        g = d["windows"]["development"]["groups"]["post_month_end_window"]
        call = tail_call(g["ratio"]["0.05"], g["paired"]["miss_q05_low"], NOMINAL["0.05"])
        self.assertEqual(call, "miss share off")
        self.assertEqual(g["reading"]["tails"]["0.05"], "in line")  # what #1547 said, under its own rule


if __name__ == "__main__":
    unittest.main()
