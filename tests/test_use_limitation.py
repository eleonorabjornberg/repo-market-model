"""The use limitation (#261) appears where it was ruled to appear, from one source.

`docs/use-limitation.md` holds the statement. The README, `docs/final-test.md` and
the results page carry it, and every copy is generated from that file, so none
can drift from it or be edited by hand.

Mutation record
---------------

Recorded for the one guard this module adds, `statement()` in
`scripts/emit_results.py`, which refuses a source file with no statement:

1. In `scripts/emit_results.py`, the README block's entry removed from `pages`
   (the `USE_LIMITATION_BEGIN` line). Kills `test_readme_carries_the_statement`
   -- `AssertionError`.
2. In `scripts/emit_visual.py`, the `use_limitation` fill set to `""`. Kills
   `test_results_page_carries_the_statement_twice` -- `AssertionError`.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "use-limitation.md"
RULED = ("A research forecast of the SOFR − IORB spread. It is not a stress-warning system and "
         "not a basis for VaR, limits, liquidity or capital, or desk sizing. Its central quantiles "
         "are not yet calibrated (#243), its tail coverage is weaker on quarter-ends and turns, and "
         "it has little history in the current scarce-reserve regime. It needs revalidation after a "
         "material policy or regime change.")


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


class UseLimitationTests(unittest.TestCase):
    def test_source_is_the_ruled_wording(self):
        self.assertEqual(re.findall(r"^> (.*)$", SOURCE.read_text(encoding="utf-8"), re.M), [RULED])

    def test_readme_carries_the_statement(self):
        text = read("README.md")
        self.assertIn("<!-- generated: use-limitation -->", text)
        self.assertEqual(text.count(RULED), 1)
        self.assertLess(text.index(RULED), text.index("## Key findings"))

    def test_final_test_page_carries_the_statement(self):
        text = read("docs/final-test.md")
        start, end = text.index("<!-- generated: final-test -->"), text.index("<!-- end generated: final-test -->")
        self.assertIn(RULED, text[start:end])

    def test_results_page_carries_the_statement_twice(self):
        page = read("site/index.html")
        self.assertEqual(page.count(RULED), 2)
        self.assertLess(page.index(RULED), page.index('id="start"'))
        final = page[page.index('<section id="final-test"'):]
        self.assertIn(RULED, final[:final.index("</section>")])

    def test_triggers_are_listed_and_marked_proposed(self):
        text = SOURCE.read_text(encoding="utf-8")
        for trigger in ("QT restart", "ON RRP", "IORB", "scarcity-state change"):
            self.assertIn(trigger, text)
        self.assertIn("None of the thresholds is decided", text)


if __name__ == "__main__":
    unittest.main()
