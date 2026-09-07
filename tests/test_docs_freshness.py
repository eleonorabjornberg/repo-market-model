"""The published documents must not transcribe facts that rot.

Two failures had already happened when this guard was written, and both are this
project's own thesis turned back on its documentation.

**A test count in prose.** `README.md` said 361 tests. `REPRODUCIBILITY.md` said
361 at commit `5dea543`. `docs/PROJECT_STATUS.md` said 409 at `ada77ac`. The suite
ran 417. Every one of those numbers was true when it was typed. A count is a
measurement *of a commit*, and prose does not carry the commit, so a count in
Markdown is not a fact -- it is a fact's decayed remains.

**A date typed by hand.** `docs/PROJECT_STATUS.md` was headed "Measured on 11
September 2026" and `docs/DATA_QUALITY_DECISIONS.md` deferred a decision as of "10
September 2026", while every commit in the repository was authored on 7 September.
A status page dated later than it could possibly have been written is information
dated other than when it was actually available: the exact failure this repository
is built to detect, published on its own front matter, where a reviewer invited by
the README to check provenance will find it first.

Neither is a discipline problem, so neither has an editorial fix. The remedies are
structural and this module enforces both:

* the size of the suite is whatever CI last printed, and no page transcribes it;
* "when" is a commit, which is a timestamp that cannot be typed wrong. A page that
  needs to say when it was measured names the commit and lets the reader run
  `git show -s --format=%ci <sha>`.

Scope is the Markdown a cloner actually receives. The working logs under
`docs/block-*/`, `docs/merge-*/`, `docs/state-of-main-*.md` and
`docs/track-*-decisions-*.md` are gitignored by design and are out of scope --
they are handoffs, not records, and they are allowed to carry the dates they were
written under. `EXCLUDED_PREFIXES` is asserted against `.gitignore` rather than
trusted, because a scope anchored to nothing cannot fail: if those patterns ever
stop being ignored, the working logs become published documents and this guard
must start reading them.
"""

from __future__ import annotations

import datetime
import pathlib
import re
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Gitignored working logs. Each prefix is checked against .gitignore below.
EXCLUDED_PREFIXES = (
    "docs/block-",
    "docs/merge-",
    "docs/state-of-main-",
    "docs/track-",
)

# Present only in the author's checkout, via .git/info/exclude: the stop-work
# pointers that halt an agent opened in the integration folder. A fresh clone
# does not contain them, so seeing them here is a local artifact, not a document.
LOCAL_ONLY = ("CLAUDE.md", "AGENTS.md")

# A digit run standing within two words of "test", "pass" or "assertion". Catches
# "409 tests", "361 standard-library tests", "360 passes". Does not catch prose
# that counts in words ("two implementers"), which does not rot the same way: a
# word is a claim about design, a numeral is a measurement of a commit.
COUNT_CLAIM = re.compile(
    r"\b\d[\d,]*\s+(?:[A-Za-z][A-Za-z-]*\s+){0,2}(?:tests?|passes|assertions?)\b",
    re.IGNORECASE,
)

MONTHS = (
    "January February March April May June "
    "July August September October November December"
).split()
MONTH_INDEX = {name: number for number, name in enumerate(MONTHS, start=1)}

ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
DAY_MONTH_YEAR = re.compile(
    r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{4})\b"
)
MONTH_YEAR = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(\d{4})\b")


def published_markdown():
    """Every Markdown file a clone of this repository would contain."""
    found = []
    for path in sorted(REPO_ROOT.rglob("*.md")):
        relative = path.relative_to(REPO_ROOT).as_posix()
        if relative.startswith(".git/") or "/.git/" in f"/{relative}":
            continue
        if relative.startswith(EXCLUDED_PREFIXES):
            continue
        if relative in LOCAL_ONLY:
            continue
        found.append((relative, path))
    return found


def dates_in(text):
    """Every calendar date the text states, as (date, matched text) pairs.

    A bare "September 2026" is read as the first of that month: the claim it
    makes is that the month had begun, and the first is the earliest reading
    that could be true. Reading it as the last of the month would let a page
    date itself four weeks ahead and pass.
    """
    found = []
    for year, month, day in ISO_DATE.findall(text):
        try:
            found.append(
                (datetime.date(int(year), int(month), int(day)), f"{year}-{month}-{day}")
            )
        except ValueError:
            continue  # not a date; a version string or an identifier
    for day, month, year in DAY_MONTH_YEAR.findall(text):
        try:
            found.append(
                (
                    datetime.date(int(year), MONTH_INDEX[month], int(day)),
                    f"{day} {month} {year}",
                )
            )
        except ValueError:
            continue
    for month, year in MONTH_YEAR.findall(text):
        found.append(
            (datetime.date(int(year), MONTH_INDEX[month], 1), f"{month} {year}")
        )
    return found


class PublishedDocumentTests(unittest.TestCase):
    """Neither a count nor a future date survives in a document a cloner reads."""

    def test_scope_is_anchored_to_gitignore(self):
        """The exclusions are the ignore rules, not a list someone maintains.

        Dropping a pattern from `.gitignore` publishes those working logs. If
        this guard kept its own copy of the list, that change would widen what
        the repository ships without widening what the guard reads, and the
        guard would go on passing about files it no longer covers.
        """
        ignored = (REPO_ROOT / ".gitignore").read_text()
        for prefix in EXCLUDED_PREFIXES:
            self.assertIn(
                prefix,
                ignored,
                f"{prefix!r} is excluded from this guard but is not in .gitignore. "
                f"Either it is now published -- remove it from EXCLUDED_PREFIXES so "
                f"this guard reads it -- or .gitignore lost a rule.",
            )

    def test_something_is_in_scope(self):
        """A guard that reads nothing passes for the wrong reason."""
        found = [relative for relative, _ in published_markdown()]
        self.assertIn("README.md", found)
        self.assertIn("docs/PROJECT_STATUS.md", found)

    def test_no_document_transcribes_a_test_count(self):
        """The suite's size lives in the CI log, which is measured, not typed.

        Four pages carried four different counts and none of them matched the
        suite. The number is not the problem; writing it down where nothing can
        update it is.
        """
        offences = []
        for relative, path in published_markdown():
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                match = COUNT_CLAIM.search(line)
                if match:
                    offences.append(f"{relative}:{number}: {match.group(0)!r}")
        self.assertEqual(
            [],
            offences,
            "A published document transcribes a test count:\n  "
            + "\n  ".join(offences)
            + "\nSay that the suite runs clean and let CI report the size.",
        )

    def test_no_document_is_dated_in_the_future(self):
        """A page cannot have been written after today.

        This is the same check the panel applies to a feature: a value carrying
        an availability later than the moment it is read has not been observed
        yet. Applied to prose, it catches the status page dated 11 September in
        a repository whose newest commit is 7 September.
        """
        today = datetime.date.today()
        offences = []
        for relative, path in published_markdown():
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                for value, text in dates_in(line):
                    if value > today:
                        offences.append(f"{relative}:{number}: {text!r}")
        self.assertEqual(
            [],
            offences,
            "A published document states a date that has not happened:\n  "
            + "\n  ".join(offences)
            + "\nName the commit instead; `git show -s --format=%ci <sha>` is a "
            "timestamp nobody has to type.",
        )


if __name__ == "__main__":
    unittest.main()
