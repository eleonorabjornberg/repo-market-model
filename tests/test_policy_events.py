"""The point-in-time register of policy and legislation (#376).

`metadata/policy_events.json` is read by `repo_model.policy_events`, keyed on
each entry's announcement instant and never on its effective date. No published
declaration reads either.

Mutation record
---------------
Run in a scratch copy of the tree, with the mutated line confirmed applied by
grep and restored before the next.

1. `require_announced`: `if entry.announced_at > as_of:` mutated to
   `if entry.effective is not None and entry.effective > as_of.date():` (the
   effective-date key). Four tests fail, all as errors from the mutated guard
   itself: `test_using_an_entry_before_its_announcement_raises` (the guard now
   raises `LookAheadError` at the 17:00 announcement instant, where the
   announcement admits it), `test_the_sunday_cut_is_unknown_on_friday_and_in_force_on_monday`,
   `test_an_entry_effective_the_day_it_is_announced_is_not_seen_before_the_release`
   and `test_a_scheduled_reinstatement_is_known_from_the_act_and_in_force_only_on_its_date`
   (`LookAheadError` on a known entry that is not yet effective).
2. `known_entries`: `e.announced_at <= as_of` mutated to
   `(e.effective or e.announced_at.date()) <= as_of.date()`. Three tests
   fail with `AssertionError` (`test_a_date_only_source_is_not_seen_on_its_own_day`,
   `test_a_scheduled_reinstatement_is_known_from_the_act_and_in_force_only_on_its_date`,
   `test_the_sunday_cut_is_unknown_on_friday_and_in_force_on_monday`) and one
   with `LookAheadError`
   (`test_an_entry_effective_the_day_it_is_announced_is_not_seen_before_the_release`).
3. `load_register`: the `effective < day` refusal removed. Kills
   `test_an_entry_in_force_before_it_is_announced_is_refused` with
   `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import policy_events as pe  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

REGISTER = ROOT / "metadata" / "policy_events.json"
IORB_TABLE = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"


def by_id(register):
    return {e.id: e for e in register}


class RegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.register = pe.load_register(REGISTER)
        cls.by_id = by_id(cls.register)

    def test_every_entry_has_a_primary_source_and_a_valid_kind(self):
        for entry in self.register:
            self.assertTrue(entry.source_url.startswith("https://"), entry.id)
            self.assertIn(entry.kind, pe.KINDS, entry.id)

    def test_the_required_topics_are_covered(self):
        kinds = {e.kind for e in self.register}
        self.assertEqual(kinds, set(pe.KINDS))
        actions = {(e.kind, e.action) for e in self.register}
        for needed in [
            ("standing_repo", "establish"), ("on_rrp", "change"), ("balance_sheet", "qt_start"),
            ("balance_sheet", "qt_taper"), ("balance_sheet", "qt_end"), ("reserve_management", "bill_purchases"),
            ("treasury_buyback", "program_launch"), ("debt_ceiling", "suspension"),
            ("debt_ceiling", "reinstatement"), ("slr", "exclusion_start"), ("slr", "eslr_final"),
        ]:
            self.assertIn(needed, actions)
        self.assertTrue(any(e.kind == "iorb_rate" and e.details["technical_adjustment"] for e in self.register))

    def test_qt_ends_on_1_december_2025(self):
        end = self.by_id["balance_sheet-20251029"]
        self.assertEqual((end.action, end.effective), ("qt_end", date(2025, 12, 1)))

    def test_iorb_entries_match_the_fetched_announcement_table_row_for_row(self):
        with IORB_TABLE.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        entries = [e for e in self.register if e.kind == "iorb_rate"]
        self.assertEqual(len(entries), len(rows))
        for entry, row in zip(entries, rows):
            self.assertEqual(entry.announced_at, datetime.fromisoformat(f"{row['announcement_date']}T{row['announcement_time']}"))
            self.assertEqual(entry.effective, date.fromisoformat(row["effective_date"]))
            self.assertAlmostEqual(entry.details["rate_percent"], float(row["rate_percent"]))
            self.assertEqual(entry.source_url, row["implementation_note_url"])

    def test_a_date_only_source_carries_the_not_stated_basis(self):
        entry = self.by_id["treasury_buyback-20240501"]
        self.assertEqual(entry.time_basis, "not_stated")
        self.assertEqual(entry.announced_at, datetime(2024, 5, 1, 23, 59, 59))

    def test_an_entry_in_force_before_it_is_announced_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "register.json"
            document = json.loads(REGISTER.read_text(encoding="utf-8"))
            document["entries"][0]["effective_date"] = "2000-01-01"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(ValueError):
                pe.load_register(path)

    def test_a_malformed_register_is_refused(self):
        document = json.loads(REGISTER.read_text(encoding="utf-8"))
        for mutate in (
            lambda d: d["entries"].append(dict(d["entries"][0])),  # duplicate id
            lambda d: d["entries"][0].update(kind="nonsense"),
            lambda d: d["entries"][0].update(source_url="http://x"),
            lambda d: d["entries"][0].update(announced_time=None),
        ):
            copy = json.loads(json.dumps(document))
            mutate(copy)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "register.json"
                path.write_text(json.dumps(copy), encoding="utf-8")
                with self.assertRaises(ValueError):
                    pe.load_register(path)


class PointInTimeTests(unittest.TestCase):
    """Policy is read from announcement, never from the effective date in hindsight."""

    @classmethod
    def setUpClass(cls):
        cls.register = pe.load_register(REGISTER)
        cls.by_id = by_id(cls.register)

    def test_using_an_entry_before_its_announcement_raises(self):
        entry = self.by_id["on_rrp-20200315"]  # announced Sunday 17:00
        with self.assertRaises(LookAheadError):
            pe.require_announced(entry, datetime(2020, 3, 13, 16, 0))
        with self.assertRaises(LookAheadError):
            pe.require_announced(entry, datetime(2020, 3, 15, 16, 59))
        self.assertIs(pe.require_announced(entry, datetime(2020, 3, 15, 17, 0)), entry)

    def test_the_sunday_cut_is_unknown_on_friday_and_in_force_on_monday(self):
        friday = pe.policy_state(self.register, datetime(2020, 3, 13, 16, 0))
        self.assertEqual(friday.latest("iorb_rate").id, "iorb-20200303")
        self.assertNotIn("iorb-20200315", {e.id for e in friday.in_force + friday.pending})
        sunday = pe.policy_state(self.register, datetime(2020, 3, 15, 18, 0))
        self.assertIn("iorb-20200315", {e.id for e in sunday.pending})  # known, not yet in force
        monday = pe.policy_state(self.register, datetime(2020, 3, 16, 16, 0))
        self.assertEqual(monday.latest("iorb_rate").id, "iorb-20200315")

    def test_an_entry_effective_the_day_it_is_announced_is_not_seen_before_the_release(self):
        entry = self.by_id["slr-20200401"]  # announced 16:45, effective the same day
        self.assertEqual(entry.effective, date(2020, 4, 1))
        at_decision = pe.policy_state(self.register, datetime(2020, 4, 1, 16, 0))
        self.assertNotIn(entry.id, {e.id for e in at_decision.in_force + at_decision.pending})
        with self.assertRaises(LookAheadError):
            pe.require_announced(entry, datetime(2020, 4, 1, 16, 0))
        self.assertIn(entry.id, {e.id for e in pe.policy_state(self.register, datetime(2020, 4, 2, 16, 0)).in_force})

    def test_a_date_only_source_is_not_seen_on_its_own_day(self):
        entry = self.by_id["debt_ceiling-20230603"]
        self.assertEqual(entry.time_basis, "not_stated")
        self.assertNotIn(entry.id, {e.id for e in pe.known_entries(self.register, datetime(2023, 6, 3, 16, 0))})
        self.assertIn(entry.id, {e.id for e in pe.known_entries(self.register, datetime(2023, 6, 4, 16, 0))})

    def test_a_scheduled_reinstatement_is_known_from_the_act_and_in_force_only_on_its_date(self):
        act, back = self.by_id["debt_ceiling-20230603"], self.by_id["debt_ceiling-20230603r"]
        during = pe.policy_state(self.register, datetime(2024, 6, 3, 16, 0))
        self.assertIn(back.id, {e.id for e in during.pending})
        self.assertEqual(during.latest("debt_ceiling").id, act.id)
        after = pe.policy_state(self.register, datetime(2025, 1, 2, 16, 0))
        self.assertEqual(after.latest("debt_ceiling").id, back.id)

    def test_a_proposal_is_known_but_never_in_force(self):
        proposal = self.by_id["slr-20250627"]
        state = pe.policy_state(self.register, datetime(2025, 7, 1, 16, 0))
        self.assertIn(proposal.id, {e.id for e in state.pending})
        self.assertNotIn(proposal.id, {e.id for e in state.in_force})

    def test_the_instant_must_be_a_naive_datetime(self):
        entry = self.register[0]
        with self.assertRaises(ValueError):
            pe.known_entries(self.register, date(2020, 1, 1))
        with self.assertRaises(ValueError):
            pe.require_announced(entry, datetime(2020, 1, 1, tzinfo=__import__("datetime").timezone.utc))


if __name__ == "__main__":
    unittest.main()
