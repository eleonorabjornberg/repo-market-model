"""The settled-questions register (`docs/research/settled-questions.md`, #1529).

The register has one entry per question a study already answered. Eleonora's ruling on #1529 (9 November
2026) gives each classified entry exactly one of four statuses, because they carry different implications and
collapsing them is what made earlier recommendations too broad:

* failed: tried and lost, or killed, with the evidence;
* parked: she deferred it, with the condition that reopens it;
* excluded: she ruled it out, with the ruling;
* untested: never run.

A study that ran but read undecided, or only partly covered its question, fits none of the four cleanly. Those
entries sit in a separate section, "Awaiting her classification", with no status line, and the pull request
raises each as a question for her. The register never settles one by itself.

What this module checks:

1. every classified entry carries exactly one status line, and its value is one of the four;
2. every entry (classified or awaiting) has the fields the issue asks for and cites at least one issue (`#N`);
3. an awaiting entry carries no status line, and says what is missing under "Open";
4. every repository path an entry cites in backticks exists in this tree (a path in another repository is
   written `repo-market-liquidity:<path>` and is not looked up here);
5. the seed citations of #1529 and its ruling comments are all present, so a seed cannot be dropped silently;

Recorded mutations. The mutated line is in the register, the exception is the failing test's:

* Mutation 1, a second status line added to a classified entry (`- **Status:** failed` followed by
  `- **Status:** parked`): `test_every_classified_entry_has_exactly_one_status` raised `AssertionError`
  naming the entry.
* Mutation 2, a classified entry's status set to `undecided`: `test_every_classified_entry_has_exactly_one_status`
  raised `AssertionError` ("not one of the four").
* Mutation 3, the `#1356` citation deleted from the register: `test_every_seed_citation_is_present` raised
  `AssertionError` naming `#1356`.
* Mutation 4, an entry's issue citations all removed: `test_every_entry_cites_an_issue` raised `AssertionError`
  naming the entry.
* Mutation 5, a status line added to an awaiting entry: `test_an_awaiting_entry_carries_no_status` raised
  `AssertionError` naming the entry.
"""

from __future__ import annotations

import pathlib
import re
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTER = REPO_ROOT / "docs" / "research" / "settled-questions.md"

STATUSES = ("failed", "parked", "excluded", "untested")
FIELDS = ("Question", "Studies", "Answer", "Would reopen it")
AWAITING_FIELDS = ("Question", "Studies", "Answer so far", "Open")

CLASSIFIED_HEADING = "## Classified"
AWAITING_HEADING = "## Awaiting her classification"

# The citations the issue and its ruling comments name. Each must stay in the register.
SEED_CITATIONS = (
    "#1153", "#1175", "#1182", "#1363", "#1400", "#1402", "#1523", "#1525",  # runs of misses, lead-1 dependence
    "#1356",                                                                # the CMB term
    "#914", "#947",                                                         # calendar at the target day
    "#1273", "#1321", "#1227",                                              # signed net settlement, IORB sign
    "#1156", "#1516", "#1528",                                              # the coverage test
    "#1133",                                                                # pooled recalibration
    "#1436",                                                                # B2* upper-tail blend
    "#1360",                                                                # B4
    "#1364",                                                                # training window
    "#1350", "#1483",                                                       # the scarcity state in the candidate
    "#243", "#408",                                                         # conformal, gbm era
)
SEED_WORDS = (
    "Lens D",          # the 19 October five-lens review
    "H7m",             # liquidity
    "H10",             # liquidity
    "2020",            # the 2020 losses
)

ISSUE = re.compile(r"#\d+")
STATUS_LINE = re.compile(r"^- \*\*Status:\*\*\s*(.*?)\s*$", re.MULTILINE)
BACKTICKED = re.compile(r"`([^`\n]+)`")


def _sections(text: str):
    """Split the register into (classified_text, awaiting_text). Raises if either heading is missing."""
    classified = text.find(CLASSIFIED_HEADING)
    awaiting = text.find(AWAITING_HEADING)
    if classified < 0 or awaiting < 0 or awaiting < classified:
        raise AssertionError(
            "the register needs the headings %r then %r" % (CLASSIFIED_HEADING, AWAITING_HEADING)
        )
    return text[classified:awaiting], text[awaiting:]


def _entries(section: str):
    """(title, body) per `### ` entry of a section."""
    parts = re.split(r"^### ", section, flags=re.MULTILINE)[1:]
    entries = []
    for part in parts:
        title, _, body = part.partition("\n")
        # An entry ends at the next `## ` heading, which the split above does not cut at.
        body = re.split(r"^## ", body, flags=re.MULTILINE)[0]
        entries.append((title.strip(), body))
    return entries


def _field(body: str, name: str):
    match = re.search(r"^- \*\*%s:\*\*\s*(.+?)(?=^- \*\*|\Z)" % re.escape(name), body,
                      re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else None


class RegisterTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not REGISTER.exists():
            raise AssertionError("docs/research/settled-questions.md does not exist")
        cls.text = REGISTER.read_text(encoding="utf-8")
        cls.classified_text, cls.awaiting_text = _sections(cls.text)
        cls.classified = _entries(cls.classified_text)
        cls.awaiting = _entries(cls.awaiting_text)

    def test_the_register_has_entries_in_both_sections(self):
        self.assertTrue(self.classified, "no classified entry")
        self.assertTrue(self.awaiting, "no awaiting entry")

    def test_every_classified_entry_has_exactly_one_status(self):
        for title, body in self.classified:
            lines = STATUS_LINE.findall(body)
            self.assertEqual(len(lines), 1, "%s: %d status lines, want exactly one" % (title, len(lines)))
            self.assertIn(
                lines[0], STATUSES,
                "%s: status %r is not one of the four %s" % (title, lines[0], STATUSES),
            )

    def test_every_classified_entry_has_its_fields(self):
        for title, body in self.classified:
            for name in FIELDS:
                self.assertTrue(_field(body, name), "%s: field %r is missing or empty" % (title, name))

    def test_an_awaiting_entry_carries_no_status(self):
        for title, body in self.awaiting:
            self.assertEqual(
                STATUS_LINE.findall(body), [],
                "%s: an awaiting entry must not carry a status; the classification is hers" % title,
            )
            for name in AWAITING_FIELDS:
                self.assertTrue(_field(body, name), "%s: field %r is missing or empty" % (title, name))

    def test_every_entry_cites_an_issue(self):
        for title, body in self.classified + self.awaiting:
            studies = _field(body, "Studies") or ""
            self.assertTrue(
                ISSUE.search(studies),
                "%s: the Studies field cites no issue (#N)" % title,
            )

    def test_every_cited_path_exists(self):
        for title, body in self.classified + self.awaiting:
            for token in BACKTICKED.findall(body):
                if not token.startswith(("docs/", "metadata/", "scripts/", "src/", "tests/")):
                    continue
                path = token.split()[0].rstrip(".,;:")
                self.assertTrue(
                    (REPO_ROOT / path).exists(),
                    "%s: cites %s, which is not in this tree" % (title, path),
                )

    def test_every_seed_citation_is_present(self):
        for citation in SEED_CITATIONS:
            self.assertRegex(
                self.text, re.escape(citation) + r"(?!\d)",
                "the seed citation %s is missing from the register" % citation,
            )
        for word in SEED_WORDS:
            self.assertIn(word, self.text, "the seed term %r is missing from the register" % word)

    def test_the_four_statuses_are_all_defined_in_the_register(self):
        for status in STATUSES:
            self.assertRegex(self.text, r"\*\*%s\*\*" % status)


if __name__ == "__main__":
    unittest.main()
