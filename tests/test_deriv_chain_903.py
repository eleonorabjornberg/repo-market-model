"""The chain that builds H2's scratch panel `DERIV.csv` (#903, H2 step 3, finding #900).

`scripts/deriv_chain_903.py` is the chain of `docs/pivot/derived-features-result.md` (Reproduce) as code: the steps, their
order and their arguments, and a digest for every step's output. Two things are pinned here.

* The order and the `--end` of every step (the page `docs/pivot/deriv-chain-903-result.md` states the same chain).
* A step rebuilt twice from the tracked fixtures in two fresh directories gives identical bytes, so a digest that moves
  between two runs of one commit is a defect and one that moves between two commits is code drift (#900 found the latter).

No look-ahead, availability or staleness guard is added, so no mutation is recorded.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import deriv_chain_903 as chain  # noqa: E402


class ChainShapeTests(unittest.TestCase):
    def test_the_order_is_the_one_the_issue_names(self):
        self.assertEqual(
            [step.name for step in chain.STEPS],
            ["AUG", "AUG2", "AUG2D", "AUG3", "AUG4", "AUG5", "AUG6", "DVP", "EW", "SCREEN", "DERIV"],
        )

    def test_end_goes_only_to_the_steps_that_take_it(self):
        commands = dict((step.name, argv) for step, argv in chain.commands(Path("w"), end="2025-12-31"))
        for name in ("AUG", "AUG2", "AUG2D", "AUG3", "AUG5", "AUG6", "DVP", "EW"):
            self.assertIn("--end", commands[name], name)
        for name in ("AUG4", "SCREEN", "DERIV"):
            self.assertNotIn("--end", commands[name], name)

    def test_without_end_no_step_gets_one(self):
        for step, argv in chain.commands(Path("w")):
            self.assertNotIn("--end", argv, step.name)

    def test_compare_names_the_first_step_that_moves(self):
        a = {"PUB": "1", "AUG": "2", "AUG2": "3", "DERIV": "4"}
        self.assertIsNone(chain.first_difference(a, dict(a)))
        self.assertEqual(chain.first_difference(a, {**a, "AUG2": "x", "DERIV": "y"}), "AUG2")


class RebuildTests(unittest.TestCase):
    def test_the_steps_up_to_net_settlement_rebuild_to_identical_bytes(self):
        digests = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as tmp:
                digests.append(chain.run(Path(tmp), stop_after="AUG3"))
        self.assertEqual(digests[0], digests[1])
        self.assertEqual(list(digests[0])[-1], "AUG3")


if __name__ == "__main__":
    unittest.main()
