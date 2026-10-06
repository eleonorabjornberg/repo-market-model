"""The model documentation and validation report (`docs/model/validation.md`, #119).

The page is written in the model-risk structure Eleonora ruled on 4 October 2026: purpose and use,
conceptual soundness, data, implementation and controls, performance and outcomes analysis, limitations and
assumptions, ongoing monitoring, governance. Its prose states no figure. Every figure sits inside a block
`scripts/emit_results.py` writes from `docs/runs/`, the metadata files or the declared sources of
`docs/model/external_sources.json`, and `tests/test_generated_results.py` refuses a stale block.

What is held here, beyond that:

* each section of the structure is present, and so is each deliverable the directive names (the pressure
  probability, the next-day distribution, the reserve-scarcity indicator, the calibration method, the four desk
  outputs, the lag finding, the lockbox);
* **no digit stands outside a generated block**, apart from issue and pull-request references and the numbering of
  the headings. This is the acceptance criterion "no public claim is stated that is not generated";
* the use-limitation statement is the one in `docs/use-limitation.md`, read, not retyped;
* the ruled wording of 2 October 2026 (the claim sentence with its three links, the fork, the futures exclusion) and
  the clearing-mandate limitation are present, and a page that was not fetched is marked so;
* the lockbox block names the tiers of `metadata/lockbox.json` and says headline results score only earlier days;
* no date that has not happened is written (`tests/test_docs_freshness.py` refuses one), so the clearing dates and
  the first scoring dates are stated by year and by the fetched wording;
* a result that is only a scratch measurement is cited by its issue and carries no number.

Recorded mutation for the digit guard (`test_no_digit_stands_outside_a_generated_block`): a digit typed into the
prose of `docs/model/validation.md` (a hand-typed "5 bp" in the purpose section) fails it with `AssertionError`.
"""

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs/model/validation.md"

SECTIONS = (
    "Model purpose and use",
    "Conceptual soundness",
    "Data",
    "Implementation and controls",
    "Performance and outcomes analysis",
    "Limitations and assumptions",
    "Ongoing monitoring",
    "Governance",
)

#: The generated blocks of the page, in order.
BLOCKS = (
    "validation-use-limitation",
    "validation-use",
    "validation-literature",
    "validation-data",
    "validation-lockbox",
    "validation-controls",
    "validation-distribution",
    "validation-pressure",
    "validation-final-test",
    "validation-calibration",
    "validation-lag",
    "validation-desk",
    "validation-limitations",
    "validation-clearing",
    "validation-monitoring",
    "validation-governance",
)


def _emit_results():
    spec = importlib.util.spec_from_file_location("emit_results_for_validation", ROOT / "scripts/emit_results.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["emit_results_for_validation"] = module
    spec.loader.exec_module(module)
    return module


def _text():
    return PAGE.read_text(encoding="utf-8")


def _blocks(text):
    """`{name: inner text}` for every `<!-- generated: NAME -->` block."""

    found = {}
    for match in re.finditer(r"<!-- generated: ([\w-]+) -->(.*?)<!-- end generated: \1 -->", text, re.S):
        found[match.group(1)] = match.group(2)
    return found


def _prose(text):
    """The page with every generated block removed."""

    return re.sub(r"<!-- generated: ([\w-]+) -->.*?<!-- end generated: \1 -->", "", text, flags=re.S)


class StructureTests(unittest.TestCase):
    def test_the_page_exists_and_has_every_section_of_the_model_risk_structure(self):
        text = _text()
        headings = re.findall(r"^## (?:\d+\. )?(.+)$", text, re.M)
        for section in SECTIONS:
            self.assertIn(section, headings, "section missing: %s" % section)
        self.assertEqual([h for h in headings if h in SECTIONS], list(SECTIONS), "sections out of order")

    def test_every_generated_block_is_present_once_and_in_order(self):
        text = _text()
        names = re.findall(r"<!-- generated: ([\w-]+) -->", text)
        self.assertEqual(names, list(BLOCKS))
        for name in names:
            self.assertEqual(text.count("<!-- end generated: %s -->" % name), 1, name)

    def test_the_deliverables_the_directive_names_are_each_covered(self):
        text = _text()
        for needle in ("pressure probability", "next-day distribution", "reserve-scarcity indicator",
                       "calibration method", "lag", "lockbox", "benchmark"):
            self.assertIn(needle, text.lower(), needle)
        for desk in ("scheduled pressure days", "turn", "scarcity regime state"):
            self.assertIn(desk, text.lower(), desk)

    def test_the_four_desk_outputs_are_part_of_intended_use_and_monitoring(self):
        blocks = _blocks(_text())
        for name in ("validation-use", "validation-monitoring"):
            for output in ("pressure probability", "spread quantiles", "expected contribution", "regime state"):
                self.assertIn(output, blocks[name].lower(), "%s lacks %s" % (name, output))


class NoFigureTypedTests(unittest.TestCase):
    #: What prose may carry digits for: issue and pull-request references, the numbering of a heading.
    ALLOWED = (r"(?:PR )?#\d+", r"^#{1,6} \d+\.", r"\(#\d+(?:, #\d+)*\)")

    def test_no_digit_stands_outside_a_generated_block(self):
        prose = _prose(_text())
        for pattern in self.ALLOWED:
            prose = re.sub(pattern, "", prose, flags=re.M)
        prose = re.sub(r"https?://\S+", "", prose)
        prose = re.sub(r"`[^`]*`", "", prose)
        offenders = [line.strip() for line in prose.splitlines() if re.search(r"\d", line)]
        self.assertEqual(offenders, [], "a digit is typed outside a generated block")

    def test_a_scratch_measurement_is_cited_by_issue_not_by_number(self):
        scratch = _blocks(_text())["validation-desk"]
        for issue in ("#232", "#115", "#214"):
            self.assertIn(issue, scratch)


class UseLimitationTests(unittest.TestCase):
    def test_the_statement_is_the_one_in_the_use_limitation_file(self):
        emit = _emit_results()
        block = _blocks(_text())["validation-use-limitation"]
        self.assertIn(emit.use_limitation(), block)

    def test_the_page_says_what_the_model_must_not_be_used_for(self):
        use = _blocks(_text())["validation-use"].lower()
        self.assertIn("not a stress-warning system", use)
        self.assertIn("never claimed", use)


class LiteratureTests(unittest.TestCase):
    CLAIM = ("To our knowledge, no public work forecasts the daily SOFR − IORB spread with strictly point-in-time "
             "public data and scores its exceedance probabilities with proper scoring rules against persistence "
             "baselines.")

    def test_the_ruled_claim_wording_and_its_three_links(self):
        block = _blocks(_text())["validation-literature"]
        self.assertIn(self.CLAIM, block)
        self.assertNotIn("nobody has tried", block.lower())
        for url in ("https://www.federalreserve.gov/monetarypolicy/files/FOMC20190913memo02.pdf",
                    "https://essay.utwente.nl/86418/1/Cornelissen_MA_BMS.pdf",
                    "https://arxiv.org/pdf/2101.04308"):
            self.assertIn(url, block)

    def test_the_fork_is_named_as_not_an_independent_replication(self):
        block = _blocks(_text())["validation-literature"]
        self.assertIn("nicholasberoud/repo-market-model", block)
        self.assertIn("not an independent replication", block)

    def test_futures_are_left_out_and_the_reason_is_stated(self):
        text = _text().lower()
        self.assertIn("futures", text)
        self.assertIn("licence", text)
        self.assertIn("over-anticipate", text)

    def test_a_source_that_was_not_fetched_says_so(self):
        sources = json.loads((ROOT / "docs/model/external_sources.json").read_text(encoding="utf-8"))
        flagged = [s for s in sources["sources"] if not s["fetched"]]
        self.assertTrue(flagged, "the declared sources should record the hosts this environment refused")
        text = _text()
        for source in flagged:
            line = next(l for l in text.splitlines() if source["url"] in l)
            self.assertIn("not fetched", line, source["url"])
        for source in sources["sources"]:
            if source["fetched"]:
                line = next(l for l in text.splitlines() if source["url"] in l)
                self.assertNotIn("not fetched", line, source["url"])


class ClearingMandateTests(unittest.TestCase):
    def test_the_limitation_paragraph_carries_its_dates_effect_and_place(self):
        block = _blocks(_text())["validation-clearing"]
        for needle in ("end of 2026", "mid-2027", "34-102487", "2026-09-03", "SOFR_volume",
                       "tails", "tri-party"):
            self.assertIn(needle, block)

    def test_a_claim_from_a_host_this_environment_refused_is_marked_not_fetched(self):
        block = _blocks(_text())["validation-clearing"]
        for host in ("sec.gov", "financialresearch.gov"):
            line = next(l for l in block.splitlines() if host in l)
            self.assertIn("not fetched", line, host)


class LockboxTests(unittest.TestCase):
    def test_the_block_names_the_declared_tiers_and_states_which_records_scored_which_days(self):
        block = _blocks(_text())["validation-lockbox"]
        tiers = json.loads((ROOT / "metadata/lockbox.json").read_text(encoding="utf-8"))["tiers"]
        for tier in tiers:
            self.assertIn(tier["start"], block)
        flat = block.replace("**", "")
        self.assertNotIn("Headline results score only days before", flat)
        self.assertIn("older pooled distribution tables scored days through", flat)
        self.assertIn("records published since score only days before %s" % tiers[0]["start"], flat)


class MonitoringTests(unittest.TestCase):
    def test_monitoring_is_the_live_record_and_names_its_dates(self):
        block = _blocks(_text())["validation-monitoring"]
        for needle in ("live record", "digests", "interim", "first_scoring_dates", "leap verdict"):
            self.assertIn(needle, block.lower())


class ControlsTests(unittest.TestCase):
    def test_every_control_names_a_guard_test_that_records_its_mutation(self):
        controls = json.loads((ROOT / "docs/model/controls.json").read_text(encoding="utf-8"))["controls"]
        self.assertTrue(controls)
        kinds = {c["kind"] for c in controls}
        for kind in ("leakage", "staleness", "lockbox", "freeze"):
            self.assertIn(kind, kinds)
        for control in controls:
            test = ROOT / control["test"]
            self.assertTrue(test.exists(), control["test"])
            self.assertRegex(test.read_text(encoding="utf-8"), r"(?i)recorded mutation|mutation record",
                             control["test"])
            self.assertTrue((ROOT / control["guard"]).exists(), control["guard"])


if __name__ == "__main__":
    unittest.main()
