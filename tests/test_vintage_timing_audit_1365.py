"""The vintage and release-timing audit of (s3c-ann-net)'s inputs (#1365; H5 registration design).

The audit is a table (`docs/research/vintage-timing-audit-1365/audit.json`) and a page generated from it. This file pins what makes
the table trustworthy: the inventory of what the candidate reads, the declared availability each row quotes (read from
`metadata/sources.json`, so a changed declaration fails here until the audit is rebuilt), the checks it measured, and that the
committed table and page are a rebuild of the tree.

Red first: this file was committed before `docs/research/vintage-timing-audit-1365/audit.json` existed and failed with
`FileNotFoundError`.

**Recorded mutations** (2 November 2026), each applied to the tree, confirmed applied by grep, the test classes named run, then
reverted:

1. `metadata/sources.json`, `nyfed_sofr.release_lag.available_time`: `"15:00"` changed to `"17:00"`.
   `RecordTests.test_the_committed_table_is_a_rebuild_of_the_tree` then failed with `AssertionError` (the committed table quotes 15:00, the rebuild 17:00).
2. `src/repo_model/s3c_announced.py`, `ANN_NET_ARM`: `location=cal.ALL_TERMS` added to the `dataclasses.replace` call (the arm then names
   `iorb_window` and `fomc_day`). `InventoryTests.test_the_arm_reads_exactly_the_audited_terms` then failed with `AssertionError`
   (`Lists differ`).
3. `src/repo_model/s3c_candidate.py`: the line `_PROBE = "tga"` appended (a string constant naming an unread panel column).
   `InventoryTests.test_no_module_of_the_chain_names_an_unaudited_column` then failed with `AssertionError` (`Items in the first set
   but not the second`).
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _audit():
    path = REPO / "scripts" / "vintage_timing_audit_1365.py"
    spec = importlib.util.spec_from_file_location("vintage_timing_audit_1365", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["vintage_timing_audit_1365"] = module
    spec.loader.exec_module(module)
    return module


audit = _audit()
RECORD = json.loads(audit.RECORD.read_text(encoding="utf-8")) if audit.RECORD.exists() else None


def _panel():
    import panel_cache

    return Path(panel_cache.published_build()["path"])


def _string_constants(module_name: str):
    tree = ast.parse((REPO / "src" / "repo_model" / f"{module_name}.py").read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant):
                docstrings.add(id(first.value))
    return {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings}


class InventoryTests(unittest.TestCase):
    def test_the_arm_reads_exactly_the_audited_terms(self):
        inventory = audit._arm_inventory()
        self.assertEqual(
            inventory["terms"],
            ["month_end", "quarter_end", "tax_date", "settlement_coupon", "settlement_bill", "dom_19_23", "post_month_end_window"],
        )
        self.assertEqual(inventory["terms_not_in_the_arm"], ["fomc_day", "iorb_window"])
        self.assertTrue(inventory["sized"])
        self.assertEqual(inventory["extra"], [])
        self.assertFalse(inventory["interact_with_state"])
        self.assertEqual(inventory["training_pairs"], "direct")

    def test_no_module_of_the_chain_names_an_unaudited_column(self):
        for name in audit.CHAIN_MODULES:
            constants = _string_constants(name)
            banned = constants & set(audit.UNREAD_COLUMNS)
            self.assertEqual(banned, set(), f"{name} names a panel column the audit lists as not read: {sorted(banned)}")

    def test_every_audited_column_is_in_a_row_or_is_built_and_unread(self):
        text = json.dumps(audit.ROWS)
        for column in ("quarter_end", "tax_date", "treasury_settlement_coupons", "treasury_settlement_bills"):
            self.assertIn(column, text)

    def test_every_row_has_every_field_and_a_question_when_it_flags(self):
        needed = {"id", "role", "input", "source", "clock", "exceptions", "vintage", "revisions", "meaning", "staleness", "leakage_risk", "question"}
        ids = [row["id"] for row in audit.ROWS]
        self.assertEqual(len(ids), len(set(ids)))
        questions = {q["id"] for q in audit.QUESTIONS}
        for row in audit.ROWS:
            self.assertTrue(needed <= set(row), row["id"])
            flagged = not row["staleness"].startswith("none") or not row["leakage_risk"].startswith("none")
            if flagged:
                self.assertTrue(row["question"], f"{row['id']} is flagged and names no marked question")
            for name in (row["question"] or "").split(", "):
                if name:
                    self.assertIn(name, questions)

    def test_every_question_has_numbered_options_and_a_default(self):
        for q in audit.QUESTIONS:
            self.assertGreaterEqual(len(q["options"]), 2, q["id"])
            self.assertTrue(q["default"].strip(), q["id"])

    def test_the_audit_cites_only_files_that_exist(self):
        text = json.dumps(audit.ROWS) + json.dumps(audit.QUESTIONS)
        for path in ("metadata/sources.json", "metadata/policy_events.json", "metadata/market_holidays.json",
                     "metadata/announcement_release_times_1301.json", "metadata/settlement_announcement_dating.json",
                     "metadata/net_settlement.json", "metadata/srf_cap_1241.json"):
            if path in text:
                self.assertTrue((REPO / path).exists(), path)


class DeclarationTests(unittest.TestCase):
    def test_every_quoted_declaration_is_read_from_the_registry(self):
        registry = audit.registry()
        for row in audit.ROWS:
            for ref in row["declared_refs"]:
                text = audit.declared_text(registry, ref)
                self.assertIn(ref["source"], text)
                self.assertIn(audit.block(registry, ref)["available_time"], text)

    def test_the_decision_keyed_block_is_the_decision_instant(self):
        from repo_model.decision_instant import DECISION_TIME

        registry = audit.registry()
        self.assertEqual(
            audit.block(registry, {"source": "fed_iorb_announcements", "block": "scheduled_availability"})["available_time"],
            DECISION_TIME.isoformat("minutes"),
        )


class CheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checks = audit.checks(_panel())

    def test_the_anchor_is_the_previous_row_at_both_instants(self):
        offsets = self.checks["anchor"]["offset_in_panel_rows_by_decision_instant"]
        self.assertEqual(set(offsets["18:00"]), {"1"})
        self.assertEqual(set(offsets["16:00"]), {"1"})

    def test_the_holiday_table_is_the_sofr_publication_schedule(self):
        holiday = self.checks["holiday_table_vs_sofr"]
        self.assertEqual(holiday["weekdays_without_sofr_not_in_table"], [])
        self.assertEqual(holiday["table_days_with_sofr"], [])

    def test_the_register_and_the_panel_agree_on_iorb(self):
        self.assertEqual(self.checks["policy_register"]["iorb_panel_mismatches"], [])
        self.assertGreater(self.checks["policy_register"]["iorb_panel_days_compared"], 2000)

    def test_no_stated_announcement_time_is_after_the_decision(self):
        self.assertTrue(self.checks["release_times"]["every_stated_time_before_the_decision"])

    def test_no_register_entry_of_the_cap_is_announced_between_the_two_instants_on_a_panel_day(self):
        # the one entry in the window is the Sunday 2020-03-15 note, before the facility existed
        self.assertEqual(self.checks["policy_register"]["announced_after_16_00_and_by_18_00"], ["iorb-20200315"])


class RecordTests(unittest.TestCase):
    def test_the_committed_table_is_a_rebuild_of_the_tree(self):
        record = audit.build_record(_panel())
        self.assertEqual(audit.RECORD.read_text(encoding="utf-8"), audit._json_text(record))

    def test_the_committed_page_is_a_rebuild_of_the_record(self):
        record = json.loads(audit.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(audit.PAGE.read_text(encoding="utf-8"), audit.render_page(record))

    def test_the_record_reads_no_outcome_and_no_locked_day(self):
        record = json.loads(audit.RECORD.read_text(encoding="utf-8"))
        self.assertTrue(record["reads_no_outcome"])
        self.assertEqual(record["last_day_read"], "2026-09-03")


if __name__ == "__main__":
    unittest.main()
