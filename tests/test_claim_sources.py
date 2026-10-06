"""A published page backs a figure with a record, not with a pull request or an issue.

**The defect (directive #192).** A record in `docs/runs/` is the official home of a
figure, and a decision in `docs/decisions/` is the home of a rule. A pull request
body, an issue comment or a scratch note is a working page: it can be edited, and
nothing holds it to the panel. Under Ruling part 5 on PR #169, the correction note in
`docs/PORTFOLIO_CASE_STUDY.md` linked to PR #169's body for the onset-day figures,
because no published record carried them. Nothing stopped the next page from doing
the same with a figure whose record did exist.

**The rule.** Every link from a published page to a pull request or an issue of
this repository is listed here, one by one, under one of two headings:

* `ATTRIBUTION`: the link names the issue or pull request where a change was made
  or a decision was ruled. No figure rests on it: the claim beside it is backed by a
  record or a decision the page also links, or it is a work-tracking link (the
  explorer's source cards list the issues that concern each source);
* `NO_RECORD_YET`: the link *is* the source of a figure or claim, because no
  published record carries it yet. Each entry says why, and the entry is removed
  when the record exists and the link is swapped for it.

A link that is in neither list fails `test_every_link_to_a_working_page_is_listed`,
so a new page that sends a reader to a pull request for a figure is refused until
somebody decides which heading it belongs under. An entry whose link has gone fails
`test_no_listed_link_is_stale`, so the lists do not outlive the pages.

Prose that sends a reader to a working page without a link ("the figures ... are in
the pull request") is matched by `POINTER` and listed the same way, under
`POINTERS_NO_RECORD_YET`.

**Scope.** `README.md`, the Markdown pages it links (files, not folders:
`docs/pivot/` holds working directives and `docs/archive/` is not binding), and the
generated explorer (`site/index.html`, `docs/visual/`). A bare "#N" without a URL
is a reference, not a link, and is not read, except where `POINTER` matches it.

**Written first, and red.** On `main` at `ea2f118`, with every list empty, the
module failed `test_every_link_to_a_working_page_is_listed` with `AssertionError`
naming every link in the scope (in `README.md`, `PLAN.md`,
`docs/PORTFOLIO_CASE_STUDY.md`, `docs/decisions/pressure-probability.md` and
`site/index.html`), and `test_every_pointer_to_a_working_page_is_listed` naming the
onset sentence in the two generated blocks that render it. The lists were then
filled, and three links in the case study's correction note whose records exist
(#134, #136, #130) were swapped for those records.
"""

from __future__ import annotations

import pathlib
import re
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

REPOSITORY = "eleonorabjornberg/repo-market-model"

LINK = re.compile(
    r"https://github\.com/" + re.escape(REPOSITORY) + r"/(?:pull|issues)/(\d+)"
)

#: Prose that sends a reader to a working page for figures, with or without a link.
POINTER = re.compile(
    r"\b(?:are|is)\s+in\s+(?:the\s+)?(?:pull\s+request|PR|issue)\b", re.IGNORECASE
)

#: A Markdown link to a local file: its target, without an anchor.
MARKDOWN_LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")

FRONT_DOOR = "README.md"

EXPLORER = ("site/index.html",)

EXPLORER_DATA = "docs/visual"

_DECISION = "names the ruling that made this decision; the rule is the record itself"

#: (page, number): why the link is attribution, not the source of a figure.
ATTRIBUTION = {
    ("README.md", 73): (
        "names the issue where the Phase 2 verdict was ruled; the verdict is stated in "
        "PLAN.md, which the same sentence links"
    ),
    ("PLAN.md", 73): "names the issue where Eleonora ruled the verdict this heading states",
    ("PLAN.md", 233): "work-tracking issue: Phase 3's plan; no figure rests on it",
    ("docs/PORTFOLIO_CASE_STUDY.md", 155): (
        "names the correction; what it corrected is stated by "
        "decisions/pressure-probability.md and runs/archive/pre-whole-bp/, both linked "
        "in the same note"
    ),
    ("docs/PORTFOLIO_CASE_STUDY.md", 124): (
        "names the publication whose changes the paragraph lists; each change links "
        "its record or decision"
    ),
    ("docs/decisions/pressure-probability.md", 73): _DECISION,
    ("docs/decisions/pressure-probability.md", 155): _DECISION,
    ("docs/decisions/pressure-probability.md", 124): (
        "names the publication from which the strict event applies; the records it "
        "published are in docs/runs/"
    ),
    ("docs/decisions/pressure-probability.md", 87): _DECISION,
    ("docs/decisions/pressure-probability.md", 91): (
        "names the issue that retires a rule; no figure rests on it"
    ),
    ("docs/decisions/pressure-probability.md", 130): _DECISION,
    ("docs/decisions/pressure-probability.md", 152): _DECISION,
    ("site/index.html", 38): "work-tracking issue on a source card; no figure rests on it",
    ("site/index.html", 88): "work-tracking issue on a source card; no figure rests on it",
    ("site/index.html", 98): "work-tracking issue on a source card; no figure rests on it",
    ("site/index.html", 115): "work-tracking issue on a source card; no figure rests on it",
    ("site/index.html", 127): "work-tracking issue on a source card; no figure rests on it",
}

#: (page, number): the figure or claim the link is the source of, and why no
#: record carries it yet.
NO_RECORD_YET = {
    ("docs/PORTFOLIO_CASE_STUDY.md", 160): (
        "the onset-day comparisons, on #160's definition of an onset day: no published "
        "record carries an onset split (#139 adds one to records published after it)"
    ),
    ("docs/PORTFOLIO_CASE_STUDY.md", 169): (
        "the onset-day paired figures, old and new labels, are in PR #169's body: no "
        "published record carries them, and the old (pre-#155) column never can"
    ),
    ("docs/PORTFOLIO_CASE_STUDY.md", 134): (
        "pressure model v1's earlier measurement on the pre-#155 labels: it was never "
        "published as a record, and the records now published score the new labels"
    ),
}

#: (page, the sentence's opening words): why the figures it points at have no record.
POINTERS_NO_RECORD_YET = {
    ("README.md", "On onset days it does not beat the persistence-logistic"): (
        "rendered from the text of exceedance_gbm_conformal_pid_nested_funding.json, "
        "which points at PR #169 for the onset-day figures; a published record is not "
        "edited in place, and no record carries those figures yet"
    ),
    ("docs/PORTFOLIO_CASE_STUDY.md", "On onset days it does not beat the persistence-logistic"): (
        "the same record text, rendered in the correction note's generated block"
    ),
}


def published_pages(root=REPO_ROOT):
    """The pages in scope, as paths relative to the repository root."""

    pages = {FRONT_DOOR, *EXPLORER}
    front = (root / FRONT_DOOR).read_text(encoding="utf-8")
    for target in MARKDOWN_LINK.findall(front):
        if "://" in target:
            continue
        path = root / target
        if path.is_file() and path.suffix == ".md":
            pages.add(target)
    for path in sorted((root / EXPLORER_DATA).rglob("*")):
        if path.is_file():
            pages.add(path.relative_to(root).as_posix())
    return sorted(pages)


def links_in(root=REPO_ROOT):
    """{(page, number)} for every link to a pull request or an issue."""

    found = set()
    for page in published_pages(root):
        text = (root / page).read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            found.add((page, int(match.group(1))))
    return found


def pointers_in(root=REPO_ROOT):
    """[(page, line, sentence)] for every POINTER match, with its sentence."""

    found = []
    for page in published_pages(root):
        text = (root / page).read_text(encoding="utf-8")
        for match in POINTER.finditer(text):
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            line = text[line_start : len(text) if line_end < 0 else line_end]
            found.append((page, text.count("\n", 0, match.start()) + 1, line))
    return found


def _listed_pointer(page, line):
    return [key for key in POINTERS_NO_RECORD_YET if key[0] == page and key[1] in line]


class ClaimSourceTests(unittest.TestCase):
    def test_the_scope_reads_the_pages_it_should(self):
        pages = published_pages()
        for page in (
            "README.md",
            "PLAN.md",
            "docs/PORTFOLIO_CASE_STUDY.md",
            "docs/decisions/pressure-probability.md",
            "site/index.html",
        ):
            self.assertIn(page, pages)
        self.assertFalse([page for page in pages if page.startswith("docs/archive/")])
        self.assertTrue(any(page.startswith("docs/visual/") for page in pages))

    def test_the_patterns_read_what_they_should(self):
        self.assertEqual(
            [int(n) for n in LINK.findall(
                f"[#5](https://github.com/{REPOSITORY}/pull/5) and "
                f"[#6](https://github.com/{REPOSITORY}/issues/6) but not "
                f"https://github.com/{REPOSITORY}/blob/main/README.md"
            )],
            [5, 6],
        )
        self.assertTrue(POINTER.search("the paired figures are in the pull request (#9)"))
        self.assertTrue(POINTER.search("the numbers is in PR #9"))
        self.assertFalse(POINTER.search("the pull request that adds it must say so"))

    def test_the_lists_do_not_overlap(self):
        self.assertFalse(set(ATTRIBUTION) & set(NO_RECORD_YET))
        for reason in (*ATTRIBUTION.values(), *NO_RECORD_YET.values(),
                       *POINTERS_NO_RECORD_YET.values()):
            self.assertTrue(reason.strip())

    def test_every_link_to_a_working_page_is_listed(self):
        unlisted = sorted(links_in() - set(ATTRIBUTION) - set(NO_RECORD_YET))
        self.assertFalse(
            unlisted,
            "a published page links a pull request or an issue that is not listed: "
            + ", ".join(f"{page} -> #{number}" for page, number in unlisted)
            + ". If a figure or claim rests on it, link the record in docs/runs/ (or the "
            "decision in docs/decisions/) instead; list it under NO_RECORD_YET only when "
            "no record carries it, or under ATTRIBUTION when no figure rests on it.",
        )

    def test_no_listed_link_is_stale(self):
        stale = sorted((set(ATTRIBUTION) | set(NO_RECORD_YET)) - links_in())
        self.assertFalse(
            stale,
            "listed links no page carries any more: "
            + ", ".join(f"{page} -> #{number}" for page, number in stale),
        )

    def test_every_pointer_to_a_working_page_is_listed(self):
        unlisted = [
            (page, line_no, line[:160])
            for page, line_no, line in pointers_in()
            if not _listed_pointer(page, line)
        ]
        self.assertFalse(
            unlisted,
            "a published page sends the reader to a working page for figures: "
            + "; ".join(f"{page}:{line_no}: {text}" for page, line_no, text in unlisted),
        )

    def test_no_listed_pointer_is_stale(self):
        seen = {key for page, _, line in pointers_in() for key in _listed_pointer(page, line)}
        self.assertEqual(sorted(set(POINTERS_NO_RECORD_YET) - seen), [])


#: Pages and sources a claim about the event windows is read in (#264). `docs/archive/`
#: and `docs/pivot/` are not binding and are not read.
EXCLUSION_PAGES = (
    "README.md",
    "docs/process/AGENT_CONTRACT.md",
    "src/repo_model/event_eval.py",
    "src/repo_model/baseline.py",
)

#: Wording that says an event window or crisis date is kept out of a headline score.
EXCLUSION_CLAIM = re.compile(
    r"(?:kept\s+out\s+of|excluded\s+from|held\s+out\s+of|left\s+out\s+of)\s+(?:the\s+|any\s+)?"
    r"(?:headline|published)\s+(?:score|metric|number|result)"
    r"|crisis\s+dates\s+excluded"
    r"|frozen\s+as\s+knowledge\s+holdouts?,?\s+so\s+no\s+model\s+is\s+tuned",
    re.IGNORECASE,
)


def _declares_exclusion(node):
    """True when any key under a record's declaration names an exclusion."""
    if isinstance(node, dict):
        return any("exclu" in key.lower() or _declares_exclusion(value) for key, value in node.items())
    if isinstance(node, list):
        return any(_declares_exclusion(value) for value in node)
    return False


def published_records_declare_exclusion():
    import json

    for path in sorted((REPO_ROOT / "docs/runs").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if _declares_exclusion(record.get("declaration") or {}):
            return True
    return False


def exclusion_claims_in(pages):
    found = []
    for page in pages:
        text = (REPO_ROOT / page).read_text(encoding="utf-8")
        text = re.sub(r"\s+", " ", re.sub(r"(?m)^\s*(?:#|-|\*|>)+\s?", "", text))
        for match in EXCLUSION_CLAIM.finditer(text):
            found.append((page, match.group(0)))
    return found


def _pages_for_exclusion_claims():
    pages = list(EXCLUSION_PAGES)
    pages += sorted(p.relative_to(REPO_ROOT).as_posix() for p in (REPO_ROOT / "docs").glob("*.md"))
    pages += sorted(p.relative_to(REPO_ROOT).as_posix() for p in (REPO_ROOT / "site").glob("*.html"))
    return pages


class EventWindowExclusionClaimTests(unittest.TestCase):
    """No page says the stress windows are kept out of a headline score (#264).

    **The defect.** `site/template.html` said the 2019 and 2020 stress windows "are
    kept out of the headline score", and `docs/PORTFOLIO_CASE_STUDY.md` said they
    are "frozen as knowledge holdouts, so no model is tuned on the episodes". The
    records say otherwise: `compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json`
    scores all 15 window days and they carry 43.3% of the pre-2026 paired gain.
    `AGENT_CONTRACT.md` defined a "scoring holdout" as crisis dates "excluded from
    the headline metric", which `baseline.py` never did.

    **The rule.** A page may say a window is excluded from a headline score only
    when a published record's declaration carries an exclusion. None does.

    Mutation (6 Oct 2026, a disposable copy): the old template sentence ("They are
    kept out of the headline score and reported on their own") put back into
    `site/template.html` kills `test_no_page_says_the_windows_are_excluded` with
    `AssertionError` naming the page; the same wording in the case study kills it
    the same way. Written first, on `main` at `0c0a561`, it failed with
    `AssertionError` naming `docs/PORTFOLIO_CASE_STUDY.md`, `docs/process/AGENT_CONTRACT.md`,
    `src/repo_model/event_eval.py` and `src/repo_model/baseline.py`.
    """

    def test_the_pattern_reads_the_wording_it_was_written_for(self):
        for sentence in (
            "They are kept out of the headline score and reported on their own.",
            "crisis dates excluded from the headline metric",
            "the stress windows kept out of the headline score",
            "frozen as knowledge holdouts, so no model is tuned on the episodes",
        ):
            self.assertTrue(EXCLUSION_CLAIM.search(sentence), sentence)
        self.assertFalse(EXCLUSION_CLAIM.search("Their days are scored and pooled in the headline."))

    def test_no_page_says_the_windows_are_excluded(self):
        if published_records_declare_exclusion():
            self.skipTest("a published record declares an exclusion; the wording may be true")
        found = exclusion_claims_in(_pages_for_exclusion_claims())
        self.assertFalse(
            found,
            "a page says event windows are excluded from a headline score, but no record "
            "declares an exclusion: " + "; ".join(f"{page}: {text!r}" for page, text in found),
        )


if __name__ == "__main__":
    unittest.main()
