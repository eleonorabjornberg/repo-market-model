"""CRPS at h = 2 to 5 is reported, labelled as chosen after opening (#223).

Eleonora's ruling of 6 October 2026 on #223: the lockbox was opened before a method was declared for these
cells, so the page says plainly that the method was chosen after the 2026 days were seen, and the cells stay
reported only. `docs/final-test.md` (written by `scripts/emit_results.py`) carries the statement beside the
h = 2 to 5 table, and `docs/decisions/lockbox.md` records it.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATEMENT = "chosen after the 2026 days were seen"


class AfterOpeningLabelTests(unittest.TestCase):
    def test_final_test_page_states_the_method_was_chosen_after_opening(self):
        page = (REPO / "docs" / "final-test.md").read_text(encoding="utf-8")
        head, _, rest = page.partition("**Five-quantile score at horizons 2 to 5, reported only.**")
        self.assertTrue(rest, "the h = 2 to 5 block is missing")
        block = rest.split("**The event cells", 1)[0]
        self.assertIn(STATEMENT, block)
        self.assertIn("never change the final test's verdict", block)

    def test_lockbox_record_states_it(self):
        text = (REPO / "docs" / "decisions" / "lockbox.md").read_text(encoding="utf-8")
        self.assertIn(STATEMENT, text)


if __name__ == "__main__":
    unittest.main()
