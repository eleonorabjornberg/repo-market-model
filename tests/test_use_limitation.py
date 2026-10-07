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
   (renamed in #316, and in #314 to `test_results_page_carries_the_plain_version_once`: the page now says it once) -- `AssertionError: 0 != 1`.

#316 added the plain-English version, which the page now carries instead (the page test
counts it, and no longer the technical statement). Two more, applied the same way:

3. `scripts/emit_visual.py`: `use_limitation_fill` reads `## The statement` instead of
   `## Plain-English version`, then `emit_visual.py` re-run. Kills
   `test_results_page_carries_the_plain_version_once` -- `AssertionError: 0 != 1`.
4. `docs/use-limitation.md`: "market" in the plain version replaced by "regime". Kills
   `test_plain_version_is_one_short_blockquote_without_jargon` -- `AssertionError: 'regime'
   unexpectedly found in ...`.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "use-limitation.md"
RULED = ("A research forecast of the SOFR − IORB spread. It is not a stress-warning system and "
         "not a basis for VaR, limits, liquidity or capital, or desk sizing. Its central quantiles "
         "are not yet calibrated, its tail coverage is weaker on quarter-ends and turns, and "
         "it has little history in the current scarce-reserve regime. It needs revalidation after a "
         "material policy or regime change.")


#: What the plain version may not contain (#316): the technical vocabulary of the statement.
BANNED = ("VaR", "desk", "quantile", "turns", "regime", "quarter-end", "conformal", "coverage", "calibrat",
          "scarce", "ON RRP", "IORB", "SOFR")


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def section(heading):
    """The body of `## <heading>` in `docs/use-limitation.md`, up to the next `## `."""
    text = SOURCE.read_text(encoding="utf-8")
    start = text.index("\n## %s\n" % heading) + 1
    nxt = text.find("\n## ", start + 1)
    return text[start:] if nxt < 0 else text[start:nxt]


def plain():
    """The one blockquote under `## Plain-English version`: the marker another repository reads (#316)."""
    return re.findall(r"^> (.*)$", section("Plain-English version"), re.M)


class UseLimitationTests(unittest.TestCase):
    def test_source_is_the_ruled_wording(self):
        self.assertEqual(re.findall(r"^> (.*)$", section("The statement"), re.M), [RULED])

    def test_readme_carries_the_statement(self):
        text = read("README.md")
        self.assertIn("<!-- generated: use-limitation -->", text)
        self.assertEqual(text.count(RULED), 1)
        self.assertLess(text.index(RULED), text.index("## Key findings"))

    def test_final_test_page_carries_the_statement(self):
        text = read("docs/final-test.md")
        start, end = text.index("<!-- generated: final-test -->"), text.index("<!-- end generated: final-test -->")
        self.assertIn(RULED, text[start:end])

    def test_results_page_carries_the_plain_version_once(self):
        page = read("site/index.html")
        (version,) = plain()
        self.assertEqual(page.count(version), 1)
        self.assertEqual(page.count(RULED), 0)
        self.assertLess(page.index(version), page.index('id="start"'))

    def test_plain_version_is_one_short_blockquote_without_jargon(self):
        found = plain()
        self.assertEqual(len(found), 1, "the section must hold exactly one blockquote")
        text = found[0]
        self.assertIsNone(re.search(r"#\d", text), "an issue number in the plain version")
        for term in BANNED:
            self.assertNotIn(term.lower(), text.lower(), term)
        sentences = [x for x in re.split(r"(?<=[.!?])\s+", text) if x]
        self.assertLessEqual(len(sentences), 2)
        for sentence in sentences:
            self.assertLessEqual(len(sentence.split()), 30, sentence)

    def test_the_marker_is_documented_in_the_file(self):
        text = SOURCE.read_text(encoding="utf-8")
        self.assertIn("first blockquote under `## Plain-English version`", text)
        self.assertIn("## The statement", text)
        self.assertEqual(len(re.findall(r"^## Plain-English version$", text, re.M)), 1)

    def test_triggers_are_listed_and_marked_proposed(self):
        text = SOURCE.read_text(encoding="utf-8")
        for trigger in ("QT restart", "ON RRP", "IORB", "scarcity-state change"):
            self.assertIn(trigger, text)
        self.assertIn("None of the thresholds is decided", text)


if __name__ == "__main__":
    unittest.main()
