"""The use limitation (#261) appears where it was ruled to appear, from one source.

`docs/use-limitation.md` holds the statement. The README, `docs/final-test.md` and
the results page carry it, and every copy is generated from that file, so none
can drift from it or be edited by hand.

Mutation record
---------------

Neither generator guard is a leakage, availability or staleness guard, so no
mutation is required. The two recorded here show the tests are not vacuous. Each
was applied to a fresh clone, the generator re-run, and the result read:

1. `scripts/emit_results.py`: the README block's body `"**Use limitation.** " +
   use_limitation(),` replaced by `"",`, then `emit_results.py` re-run. Kills
   `test_readme_carries_the_statement` -- `AssertionError: 0 != 1`.
2. `scripts/emit_visual.py`: `use_limitation_fill` returns `{"use_limitation": ""}`,
   then `emit_visual.py` re-run. Kills `test_results_page_carries_the_statement_twice`
   -- `AssertionError: 0 != 2`.
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
