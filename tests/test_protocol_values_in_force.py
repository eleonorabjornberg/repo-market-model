"""The protocol record states the critical values in force, and they are the code's (#1073).

`docs/decisions/scoring-protocol.md` carries a status block, "Critical values in force", quoting Eleonora's rulings of
21 October 2026 on #1064 and #1065. Its value lines are read here and compared with
`scoring_protocol.CRITICAL_VALUES` and `B2_LEG_CRITICAL_VALUES`, so a change to either that the record does not state
(or a record that states values the code does not use) fails.

Recorded mutation: `CRITICAL_VALUES[GRID_COMPARISON][250]` 2.4257 -> 2.4 in `scoring_protocol.py` fails
`test_the_record_states_the_values_the_code_uses` with `AssertionError`.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from repo_model import scoring_protocol as sp

RECORD = Path(__file__).resolve().parents[1] / "docs" / "decisions" / "scoring-protocol.md"
HEADING = "## Critical values in force"
RULINGS = (
    "https://github.com/eleonorabjornberg/repo-market-model/issues/1064#issuecomment-6318943223",
    "https://github.com/eleonorabjornberg/repo-market-model/issues/1065#issuecomment-6318943641",
)
LINE = re.compile(r"^- `(?P<comparison>[^`]+)`, (?P<days>\d+) days: (?P<value>\d+\.\d+|none)\s*$", re.M)


def status_block() -> str:
    text = RECORD.read_text(encoding="utf-8")
    start = text.index(HEADING)
    end = text.find("\n## ", start + len(HEADING))
    return text[start:end if end != -1 else None]


class ValuesInForceTests(unittest.TestCase):
    def test_the_record_has_the_status_block_near_the_top(self):
        text = RECORD.read_text(encoding="utf-8")
        self.assertIn(HEADING, text)
        self.assertLess(text.index(HEADING), text.index("## Rulings on the implementation"))

    def test_the_block_quotes_both_rulings(self):
        block = status_block()
        for url in RULINGS:
            self.assertIn(url, block)

    def test_the_record_states_the_values_the_code_uses(self):
        stated = {(m["comparison"], int(m["days"])): m["value"] for m in LINE.finditer(status_block())}
        used = {
            (comparison, days): value
            for comparison, looks in sp.CRITICAL_VALUES.items()
            for days, value in looks.items()
        }
        self.assertEqual(set(stated), set(used))
        for key, value in used.items():
            if value is None:
                self.assertEqual(stated[key], "none", key)
            else:
                self.assertEqual(stated[key], f"{value:.3f}", key)

    def test_no_per_leg_value_is_in_force(self):
        self.assertEqual(sp.B2_LEG_CRITICAL_VALUES, {})
        self.assertIn("no per-leg value", status_block())


if __name__ == "__main__":
    unittest.main()
