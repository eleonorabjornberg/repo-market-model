"""A hand-written page links to a result; it does not restate one.

**The defect.** On 1 October 2026 the Phase 2 verdict and the event definition
(">" rather than ">=") changed. The hand-written copies had to be found and fixed one by
one in `PLAN.md`, `README.md`, `METHODOLOGY.md`, `docs/PORTFOLIO_CASE_STUDY.md`,
`docs/pivot/plan.md`, the overview figure and a notebook, across PRs #77, #80 and
#81. A figure already has one home, its generated block, rendered from `docs/runs/` by
`scripts/emit_results.py` and held to its records by `test_generated_results`. A
verdict has one home, `PLAN.md`. The headline event has one, too:
`docs/decisions/pressure-probability.md`. Every other copy is a copy that a re-score or a
ruling leaves behind (directive #83).

**The rule, and why this rule.** Outside its generated blocks, a page in `PAGES` may
describe the method, the target and the data. It may not say what a model achieved.
A model result is refused when it takes one of these forms:

* **a comparative claim about a model**: *beats*, *beaten*, *outperforms*,
  *loses to*, *won*, *(in)distinguishable* from a benchmark (or a "distinguishable
  win"), or *skill* used as a finding. "Brier
  skill" names a metric and is allowed. *Wins* is allowed because the decision record's
  rule is stated with it: "whichever candidate wins". These words are how
  the stale copies were worded, and a reader cannot tell a restated claim from a
  current one;
* **a verdict**: *met*, *fails*, *failing*, *failed* or *passes* within one clause of
  *criterion* or *clause*;
* **a figure that only a record can produce**: a decimal percentage or decimal basis-point
  figure, a basis-point figure that is not a threshold declared in
  `metadata/stress_thresholds.json`, a signed or leading-zero decimal (a skill score or
  a loss), or a bracketed numeric interval. A figure inside an inline code span is a
  literal (a structural `0.0`, a version) and is not read.

The list is a set of word and figure patterns, not a reading of meaning, so the rule
is narrower than its intent in both directions. A result phrased in other words gets
past it, and a description that uses one of these words is refused. A refused
description is reworded. The rule does not get an exception list. Declared thresholds
are allowed because they define the target ("more than +5 bp"); they are not a
measurement.

**The event is stated once.** A page in `PAGES` that restates the headline event in
plain words must use the record's strict wording ("more than", never "at least",
">=" or "or more"), and must link to the record.

**What it caught on `main` at `a1c5bc0`**, written first and run red before any page
changed: `AssertionError` from both tests.

* `README.md`: "Status, honestly" restated the verdict ("the model beats persistence
  out of sample, and the tail clause fails"). "The tail clause, measured" described the
  criterion in a result's words ("a model that beats persistence") and still called
  the verdict re-opened.
* `docs/PORTFOLIO_CASE_STUDY.md`: "Results and limitations" restated the key findings
  and the verdict ("beats the benchmark on average", "loses to persistence in
  2021-23", "a smaller but distinguishable win", "has skill at the two smaller
  thresholds", "is beaten at the two larger ones", "not distinguishable", "is met on
  the first half and fails on the second"). One description was refused too, and was
  reworded: "whether a phase has met its exit criterion" now reads "reached".
* `METHODOLOGY.md`: "Reading the pre-as-of records" restated the archived records'
  results ("won on CRPS", "carried skill", "beat it only at the lowest declared
  threshold"). The page also restated the event without linking to its record.

**Mutation, recorded on this branch, Python 3.11.** In a disposable copy, the
sentence "the model beats persistence out of sample, and the tail clause fails" was
put back into `README.md`'s "Status, honestly". It killed
`test_no_hand_written_part_states_a_model_result` alone, with `AssertionError` naming
`README.md` and both matches. The same sentence pasted inside the README's generated
`tail` block was not refused by this module. (`test_generated_results` refuses it
there.) The control was green before and after.
"""

from __future__ import annotations

import json
import pathlib
import re
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = ("README.md", "PROJECT_GUIDE.md", "METHODOLOGY.md", "docs/PORTFOLIO_CASE_STUDY.md")

EVENT_RECORD = "docs/decisions/pressure-probability.md"

GENERATED = re.compile(
    r"<!-- generated: (?P<name>[\w-]+) -->.*?<!-- end generated: (?P=name) -->",
    re.DOTALL,
)

# Comparative claims about a model. `\s+` because published prose is hard-wrapped.
CLAIMS = (
    r"\bbeat(?:s|en|ing)?\b",
    r"\b(?:out|under)perform(?:s|ed|ing)?\b",
    r"\b(?:lose|loses|lost|losing)\s+to\b",
    r"\b(?:in)?distinguishable\s+(?:win|at|from\s+(?:\S+\s+){0,2}?"
    r"(?:persistence|climatology|benchmark|model|zero))\b",
    r"\bwon\b",
)

# "skill" as a finding; "Brier skill" names a metric.
SKILL = re.compile(r"(\S*)\s+skill\b", re.IGNORECASE)

VERDICTS = (
    r"\b(?:criterion|clause)\b[^.;:]{0,80}?\b(?:met|fails|failing|failed|passes)\b",
    r"\b(?:met|fails|failing|failed|passes)\b[^.;:]{0,40}?\b(?:criterion|clause)\b",
)

BASIS_POINTS = re.compile(r"[-+−]?(\d+(?:\.\d+)?)\s*(?:bp\b|basis\s+points?\b)")

FIGURES = (
    r"\d+\.\d+\s*%",
    r"(?<![\w.])[-+−]?0\.\d+(?![\d.])",
    r"(?<![\w.])[-+−]\d+\.\d+(?![\d.])",
    r"\[\s*[-+−]?\d+(?:\.\d+)?\s*,\s*[-+−]?\d+(?:\.\d+)?\s*\]",
)

# An inline code span is a literal (`0.0`, a version), not a measurement.
INLINE_CODE = re.compile(r"`[^`\n]*`")

# The headline event worded more loosely than its record.
LOOSE_EVENT = (
    r"\bat\s+least\s+\+?\d+\s*(?:bp\b|basis\s+points?\b)",
    r"(?:≥|>=)\s*\+?\d+\s*(?:bp\b|basis\s+points?\b)",
    r"\+?\d+\s*(?:bp\b|basis\s+points?\b)\s+or\s+more\b",
)

STRICT_EVENT = re.compile(r"\bmore\s+than\s+\+?\d+\s*(?:bp\b|basis\s+points?\b)")


def declared_thresholds(root=REPO_ROOT):
    """The bp levels `metadata/stress_thresholds.json` declares, as floats."""
    data = json.loads((root / "metadata" / "stress_thresholds.json").read_text())
    return {float(tau) for tau in data["taus_bp"]}


def hand_written(text):
    """The text with every generated block blanked, line numbers kept."""
    return GENERATED.sub(lambda match: "\n" * match.group(0).count("\n"), text)


def _line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def _quoted(match):
    return " ".join(match.group(0).split())


def model_results_in(text, thresholds):
    """(line, matched text) for every model result stated outside a generated block."""
    prose = hand_written(text)
    found = []
    for pattern in CLAIMS + VERDICTS:
        for match in re.finditer(pattern, prose, re.IGNORECASE):
            found.append((_line_of(prose, match.start()), _quoted(match)))
    literal_free = INLINE_CODE.sub(lambda match: " " * len(match.group(0)), prose)
    for pattern in FIGURES:
        for match in re.finditer(pattern, literal_free):
            found.append((_line_of(prose, match.start()), _quoted(match)))
    for match in SKILL.finditer(prose):
        if match.group(1).lower() != "brier":
            found.append((_line_of(prose, match.start()), _quoted(match)))
    for match in BASIS_POINTS.finditer(prose):
        if float(match.group(1)) not in thresholds:
            found.append((_line_of(prose, match.start()), _quoted(match)))
    return sorted(found)


def event_offences(text):
    """Why the page's own statement of the headline event disagrees with its record."""
    prose = hand_written(text)
    offences = []
    for pattern in LOOSE_EVENT:
        for match in re.finditer(pattern, prose, re.IGNORECASE):
            offences.append(
                f"line {_line_of(prose, match.start())}: {_quoted(match)!r} is not the "
                f"record's 'more than'"
            )
    states_it = STRICT_EVENT.search(prose) or offences
    if states_it and EVENT_RECORD.split("/")[-1] not in text:
        offences.append(f"restates the event without linking to {EVENT_RECORD}")
    return offences


class HandWrittenResultsTests(unittest.TestCase):
    """Results live in generated blocks and `PLAN.md`; pages link to them."""

    def test_the_pages_exist(self):
        """A guard over files that are not there passes for the wrong reason."""
        for page in PAGES:
            self.assertTrue((REPO_ROOT / page).is_file(), page)
        self.assertTrue((REPO_ROOT / EVENT_RECORD).is_file(), EVENT_RECORD)

    def test_the_rule_reads_what_it_should(self):
        """The rule refuses each form it names, and passes a generated block and a description."""
        thresholds = declared_thresholds()
        refused = (
            "gbm beats as-of persistence",
            "it is not distinguishable from the persistence-logistic benchmark",
            "keeps a smaller but distinguishable win",
            "the model loses to\npersistence in 2021-23",
            "the conditional model carried skill at the shoulder",
            "the criterion is met on the interval evidence",
            "and the tail clause fails",
            "coverage was 84.3%",
            "a mean absolute error of 3.14 bp",
            "a skill score of 0.12",
            "the difference is [-0.31, -0.12]",
        )
        for sentence in refused:
            with self.subTest(refused=sentence):
                self.assertTrue(model_results_in(sentence, thresholds))
        allowed = (
            "the chance that SOFR is more than +5 bp (and +10 bp) above IORB",
            "CRPS, pinball loss, Brier skill and CORP reliability",
            "whichever candidate wins against the same benchmarks",
            "numpy 2.4.6 and Python 3.11, with a nominal 90% band",
            "structural zeros remain distinguishable; a cell reads `0.0`",
            "a default is indistinguishable from a measurement",
            "<!-- generated: tail -->\ngbm beats persistence by 0.12\n"
            "<!-- end generated: tail -->",
        )
        for sentence in allowed:
            with self.subTest(allowed=sentence):
                self.assertEqual([], model_results_in(sentence, thresholds))

    def test_no_hand_written_part_states_a_model_result(self):
        thresholds = declared_thresholds()
        offences = []
        for page in PAGES:
            text = (REPO_ROOT / page).read_text(encoding="utf-8")
            for line, quoted in model_results_in(text, thresholds):
                offences.append(f"{page}:{line}: {quoted!r}")
        self.assertEqual(
            [],
            offences,
            "A hand-written part of a page states a model result:\n  "
            + "\n  ".join(offences)
            + "\nLink to the generated block (README.md's key findings and tail) or to "
            "PLAN.md's verdict instead of restating it.",
        )

    def test_the_event_is_worded_as_its_record_and_linked(self):
        offences = []
        for page in PAGES:
            text = (REPO_ROOT / page).read_text(encoding="utf-8")
            for offence in event_offences(text):
                offences.append(f"{page}: {offence}")
        self.assertEqual(
            [],
            offences,
            "A page states the headline event other than as "
            f"{EVENT_RECORD} does:\n  " + "\n  ".join(offences),
        )


if __name__ == "__main__":
    unittest.main()
