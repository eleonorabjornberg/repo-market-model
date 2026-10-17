"""The audit of the partly announced bill-class rules (#679, finding #665): `scripts/partly_announced_679.py`.

Pins the figures #665 reported, which the script reproduces on the tracked fixture, and that the rule in force
(`net_settlement.net_for_day`) is the audit's `left_out_pit`: `left_out` as #679 audited it, with a cash management
bill read only from its own announcement (#738). The audit's recorded `left_out` figures are the earlier reading and
are not recomputed, so the audit and the code cannot drift apart without this test failing.
"""


from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import datetime, time
from pathlib import Path

from repo_model import net_settlement as ns

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("partly_announced_679", ROOT / "scripts" / "partly_announced_679.py")
audit = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = audit
_spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.build()

    def test_it_reproduces_665s_figures(self):
        table = self.result["day_lead_cases"]["by_rule_leads_2_to_5"]
        self.assertEqual(table["old"]["n"], 117)
        got = {rule: (round(table[rule]["mean_error"], 1), round(table[rule]["mae"], 1)) for rule in audit.RULES}
        self.assertEqual(got, {"old": (-50.6, 50.6), "announced": (83.2, 85.7), "left_out": (-28.4, 37.2)})

    def test_the_partial_cases_are_concentrated_in_2018_at_long_leads(self):
        by_year = self.result["day_lead_cases"]["by_year_leads_4_5"]
        self.assertEqual(by_year["2018"]["n"], 80)
        self.assertEqual(sum(v["n"] for v in by_year.values()), 109)

    def test_the_recorded_output_is_the_script_output(self):
        recorded = json.loads((audit.OUT / "audit.json").read_text(encoding="utf-8"))
        self.assertEqual(recorded, json.loads(json.dumps(self.result, sort_keys=True)))
        self.assertEqual((audit.OUT / "audit.md").read_text(encoding="utf-8"), audit.markdown(self.result))

    def test_the_left_out_rule_is_the_rule_in_force(self):
        declaration = ns.load_declaration(audit.DECLARATION)
        auctions = ns.load_snapshot(audit.SNAPSHOT, declaration)
        by_day = {}
        for auction in auctions:
            by_day.setdefault(auction.settles, []).append(auction)
        checked = 0
        for settles, day in sorted(by_day.items()):
            for announced in sorted({a.announced_at for a in day}):
                instant = datetime.combine(announced.date(), time(12))
                self.assertAlmostEqual(ns.net_for_day(day, instant)[0], audit.net(day, instant, "left_out_pit"), places=9)
                checked += 1
        self.assertGreater(checked, 1000)


if __name__ == "__main__":
    unittest.main()
