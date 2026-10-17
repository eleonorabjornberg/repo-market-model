"""The back-fill amendment's admitted list is the one `metadata/backfill_posting.json` declares (#874).

H4 (the information set it trains under); a decision-record correction. Eleonora's ruling on #742 admits TGCR, BGCR
and SOFR from 2018-05-17 and no other series; the amendment in `docs/decisions/information-set.md` must say exactly
that. The record carries one marked line, `<!-- backfill-admitted: SERIES@DATE, ... -->`, and this test compares it
with the `admitted` mapping.

Red first, against main at 507a2fd0: `AssertionError: the amendment carries no marked admitted list` (no line
`<!-- backfill-admitted: ... -->` yet).

Mutation record. In a scratch copy of the tree, CPython 3.11, `python -B`, unmutated control green before and after,
the mutated line confirmed applied by grep. In `docs/decisions/information-set.md` the marked line
`<!-- backfill-admitted: bgcr@2018-05-17, sofr@2018-05-17, tgcr@2018-05-17 -->` was mutated by adding `iorb@2018-05-17`.
Killed: `test_the_record_admits_what_the_declaration_admits` failed with `AssertionError`.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "decisions" / "information-set.md"
DECLARATION = ROOT / "metadata" / "backfill_posting.json"
MARKER = re.compile(r"<!--\s*backfill-admitted:\s*(.*?)\s*-->")


def record_list():
    text = RECORD.read_text(encoding="utf-8")
    start = text.index("## Amendment: back-filled repo-rate history")
    end = text.find("\n## ", start + 1)
    found = MARKER.findall(text[start:end if end != -1 else len(text)])
    if len(found) != 1:
        raise AssertionError(f"the amendment carries no marked admitted list (found {len(found)})")
    pairs = {}
    for item in found[0].split(","):
        series, _, day = item.strip().partition("@")
        pairs[series] = day
    return pairs


class TheRecordMatchesTheDeclaration(unittest.TestCase):
    def test_the_record_admits_what_the_declaration_admits(self):
        declared = {name: instant[:10] for name, instant in json.loads(DECLARATION.read_text())["admitted"].items()}
        self.assertEqual(record_list(), declared)


if __name__ == "__main__":
    unittest.main()
