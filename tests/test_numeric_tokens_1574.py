"""Every number on a rewritten page stays byte-identical (#1574).

`scripts/check_numeric_tokens.py` tokenises the numbers of a Markdown page. The first class pins the tokeniser; the second
compares each stored baseline under `tests/fixtures/numeric_tokens_1574/` with the page in the working tree. It needs
neither git nor the network, and passes when the directory holds no baseline.

This is not a leakage, availability or staleness guard, so it carries no recorded mutation.
"""
import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_numeric_tokens", ROOT / "scripts" / "check_numeric_tokens.py")
cnt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cnt)


def toks(text):
    return sorted(cnt.tokens(text))


class TokeniserTest(unittest.TestCase):
    def test_range_is_two_unsigned_numbers(self):
        self.assertEqual(toks("h = 1-5"), ["1", "5"])

    def test_signs_attached_to_digits_are_kept(self):
        self.assertEqual(toks("[+0.004, -0.087]"), ["+0.004", "-0.087"])

    def test_sign_after_closing_bracket_letter_or_digit_is_dropped(self):
        self.assertEqual(toks("(a)-3 x-4 5+6"), ["3", "4", "5", "6"])

    def test_thousands_commas_are_one_token(self):
        self.assertEqual(toks("n = 2,000 rows"), ["2,000"])
        self.assertEqual(toks("1,234,567"), ["1,234,567"])

    def test_comma_separated_list_is_not_thousands(self):
        self.assertEqual(toks("1, 2, 3"), ["1", "2", "3"])
        self.assertEqual(toks("1,2"), ["1", "2"])

    def test_identifiers_and_names(self):
        self.assertEqual(toks("k = 20"), ["20"])
        self.assertEqual(toks("#1531"), ["1531"])
        self.assertEqual(toks("s3c"), ["3"])
        self.assertEqual(toks("B1'"), ["1"])
        self.assertEqual(toks("q05"), ["05"])

    def test_percent_and_exponent(self):
        self.assertEqual(toks("12.5% and 1e-9 and 3E+4"), ["12.5%", "1e-9", "3E+4"])

    def test_trailing_full_stop_or_comma_is_not_part_of_the_token(self):
        self.assertEqual(toks("It was 3.5. Then 4, then 2."), ["2", "3.5", "4"])

    def test_iso_date_is_one_token(self):
        self.assertEqual(toks("on 2026-10-20 and 2026-10-21."), ["2026-10-20", "2026-10-21"])

    def test_hex_digest_is_one_token(self):
        sha = "8e870a0bfddb72e1e2a33089c4f2b075a8e4f487"
        digest = "ab12" * 16
        self.assertEqual(toks("base %s, digest %s" % (sha, digest)), sorted([sha, digest]))

    def test_short_hex_is_not_a_digest(self):
        self.assertEqual(toks("abc1234"), ["1234"])

    def test_counts_repeats(self):
        self.assertEqual(cnt.tokens("1 1 2"), Counter({"1": 2, "2": 1}))

    def test_compare(self):
        result = cnt.compare("a 1 2 2 3", "b 2 3 3 4")
        self.assertEqual(result["removed"], ["1"])
        self.assertEqual(result["added"], ["4"])
        self.assertEqual((result["before_distinct"], result["after_distinct"]), (3, 3))
        self.assertEqual((result["before_total"], result["after_total"]), (4, 4))

    def test_compare_ignores_prose_and_order(self):
        result = cnt.compare("The score was 0.5 at h = 1-5.", "At h = 1-5 we saw 0.5, as a score.")
        self.assertEqual((result["removed"], result["added"]), ([], []))


class SourcedAdditionTest(unittest.TestCase):
    """A new number is accepted only when a cited source carries it (Eleonora's ruling of 11 November 2026 on #1575)."""

    def test_a_token_its_source_carries_is_accepted(self):
        self.assertEqual(cnt.unsourced({"99.3%", "7"}, ["a 99.3% b", "c 7 d"]), [])

    def test_a_token_no_source_carries_is_refused(self):
        self.assertEqual(cnt.unsourced({"99.3%", "98.1%"}, ["a 99.3% b"]), ["98.1%"])

    def test_a_near_miss_is_refused(self):
        self.assertEqual(cnt.unsourced({"99.3%"}, ["0.993 and 99.30% and 99.3"]), ["99.3%"])

    def test_an_issue_number_counts_only_where_it_is_cited_as_one(self):
        self.assertEqual(cnt.uncited({"1572"}, "see #1572, then #1572.", {"1572"}), [])
        self.assertEqual(cnt.uncited({"1572"}, "see #1572 and 1572 rows", {"1572"}), ["1572"])
        self.assertEqual(cnt.uncited({"1572"}, "see #1572", set()), ["1572"])

    def test_a_stored_addition_must_name_a_source_that_carries_it(self):
        record = {"tokens": ["1"], "added": {"2": {"source": "s.md", "why": "w"}}}
        ok = cnt.check_record(record, "1 and 2", lambda rel: "table: 2")
        self.assertEqual((ok["removed"], ok["added"]), ([], []))
        bad = cnt.check_record(record, "1 and 2", lambda rel: "table: 3")
        self.assertEqual(bad["added"], ["2"])
        unlisted = cnt.check_record(record, "1 and 2 and 4", lambda rel: "table: 2 4")
        self.assertEqual(unlisted["added"], ["4"])


class BaselineTest(unittest.TestCase):
    def test_every_page_keeps_its_numbers(self):
        directory = ROOT / cnt.BASELINES
        files = sorted(directory.glob("*.json")) if directory.is_dir() else []
        for file in files:
            record = json.loads(file.read_text(encoding="utf-8"))
            with self.subTest(page=record["path"]):
                result = cnt.check_record(record, (ROOT / record["path"]).read_text(encoding="utf-8"))
                self.assertEqual((result["removed"], result["added"]), ([], []))


if __name__ == "__main__":
    unittest.main()
