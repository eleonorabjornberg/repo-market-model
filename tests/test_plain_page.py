"""The plain-language results page (`site/plain.html`, #120).

The page's hand-written HTML states no figure: every figure, date and count sits inside a block
`scripts/plain_page.py` renders from `docs/runs/`, the metadata files, `docs/use-limitation.md` or
`docs/model/external_sources.json`, and `scripts/emit_results.py --check` refuses a stale block.

Held here, beyond that:

* each section is present, in the order Eleonora ruled (the pressure probability first, then the range on pressure
  days, the turn's contribution, the scarcity state, the limitations), and every section ends with a link to a record
  and to the validation report;
* **no digit stands outside a generated block**;
* every link to a file of this repository points at a file that exists;
* the ruled claim sentence with its three links, the fork note and the futures exclusion are present;
* the use-limitation statement is read from `docs/use-limitation.md`, not retyped;
* the lockbox is named, and the weak test above the highest threshold is stated;
* the README and the visual layer link to the page.

Recorded mutation for the digit guard (`test_no_digit_stands_outside_a_generated_block`): a "5 bp" typed into the
hand-written `<p class="lede">` of `site/plain.html` fails it with `AssertionError`.
Recorded mutation for the dead-link guard (`test_every_repository_link_points_at_a_file`): a block linking to
`docs/runs/does_not_exist.json` makes `plain_page._link` raise `PageError`.
"""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "site/plain.html"
BLOB = "https://github.com/eleonorabjornberg/repo-market-model/blob/main/"

#: The generated blocks, in the order of the page.
BLOCKS = (
    "plain-question",
    "plain-pressure",
    "plain-distribution",
    "plain-turn",
    "plain-scarcity",
    "plain-limits",
    "plain-place",
)


def _emit_results():
    spec = importlib.util.spec_from_file_location("emit_results_for_plain", ROOT / "scripts/emit_results.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["emit_results_for_plain"] = module
    spec.loader.exec_module(module)
    return module


def _text():
    return PAGE.read_text(encoding="utf-8")


def _blocks(text):
    found = {}
    for name in BLOCKS:
        match = re.search(r"<!-- generated: %s -->(.*?)<!-- end generated: %s -->" % (name, name), text, re.S)
        found[name] = match.group(1) if match else None
    return found


def _prose(text):
    text = re.sub(r"<!-- generated: ([\w-]+) -->.*?<!-- end generated: \1 -->", "", text, flags=re.S)
    text = re.sub(r"<style>.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<[^>]*>", " ", text)
    return text


class StructureTests(unittest.TestCase):
    def test_every_block_is_present_in_order(self):
        text = _text()
        found = _blocks(text)
        for name in BLOCKS:
            self.assertIsNotNone(found[name], name)
        positions = [text.index("<!-- generated: %s -->" % name) for name in BLOCKS]
        self.assertEqual(positions, sorted(positions))

    def test_every_section_ends_with_a_record_link_and_the_validation_report(self):
        for name, body in _blocks(_text()).items():
            self.assertIn('class="src"', body, name)
            self.assertIn(BLOB + "docs/model/validation.md", body, name)

    def test_the_results_sections_link_to_records(self):
        blocks = _blocks(_text())
        for name in ("plain-pressure", "plain-distribution", "plain-limits"):
            self.assertIn(BLOB + "docs/runs/", blocks[name], name)

    def test_the_page_is_not_stale(self):
        emit = _emit_results()
        self.assertEqual(emit.main(["--check"]), 0)


class NoHandTypedFigureTests(unittest.TestCase):
    def test_no_digit_stands_outside_a_generated_block(self):
        prose = re.sub(r"https?://\S+", "", _prose(_text()))
        offenders = [line.strip() for line in prose.splitlines() if re.search(r"\d", line)]
        self.assertEqual(offenders, [], "a digit is typed outside a generated block")

    def test_every_repository_link_points_at_a_file(self):
        text = _text()
        links = re.findall(re.escape(BLOB) + r'([^"#]+)', text)
        self.assertTrue(links)
        for rel in links:
            self.assertTrue((ROOT / rel).exists(), rel)


class RuledContentTests(unittest.TestCase):
    def test_the_ruled_claim_wording_and_its_three_links(self):
        block = _blocks(_text())["plain-place"]
        self.assertIn("To our knowledge, no public work forecasts the daily SOFR", block)
        self.assertNotIn("nobody has tried", block.lower())
        for url in ("https://www.federalreserve.gov/monetarypolicy/files/FOMC20190913memo02.pdf",
                    "https://essay.utwente.nl/86418/1/Cornelissen_MA_BMS.pdf",
                    "https://arxiv.org/pdf/2101.04308"):
            self.assertIn(url, block)

    def test_the_fork_and_the_futures_exclusion_are_stated(self):
        block = _blocks(_text())["plain-place"]
        self.assertIn("nicholasberoud/repo-market-model", block)
        self.assertIn("not an independent replication", block)
        self.assertIn("licence", block)
        self.assertIn("Gellert", block)

    def test_the_use_limitation_is_read_not_retyped(self):
        emit = _emit_results()
        self.assertIn(emit.use_limitation().replace("&", "&amp;"), _blocks(_text())["plain-limits"].replace("&#x27;", "'"))

    def test_the_limits_name_the_lockbox_and_the_weak_upper_test(self):
        block = _blocks(_text())["plain-limits"]
        self.assertIn("Days that are locked", block)
        self.assertIn("is weak", block)
        self.assertIn("lockbox.md", block)

    def test_the_headline_is_the_pressure_probability_and_the_page_does_not_claim_stress_warning(self):
        text = _text()
        self.assertLess(text.index('id="pressure"'), text.index('id="range"'))
        self.assertLess(text.index('id="range"'), text.index('id="turn"'))
        self.assertLess(text.index('id="turn"'), text.index('id="scarcity"'))
        self.assertLess(text.index('id="scarcity"'), text.index('id="limits"'))
        self.assertNotIn("warns of stress", text.lower())


class LinkedFromTests(unittest.TestCase):
    def test_the_readme_and_the_visual_layer_link_to_the_page(self):
        self.assertIn("plain.html", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("plain.html", (ROOT / "site/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
