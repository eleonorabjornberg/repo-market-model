"""The H4 step 3 nested test of the back-fill against H5's candidate (#726): its fixed parts.

`scripts/backfill_h5_726.py` is exploration on development data. These tests pin what does not depend on a fit: a
back-filled row carries only the established series, an arm is refused on the wrong panel, the with arm's panel agrees
with the published one on the published days, every fit passes the posting guard, and the declaration names the arms
and the reading rule.

Recorded mutations (each applied, the named test run, then reverted):

* `kept_columns` keeps every column (a back-filled row would carry an unestablished FRED level):
  `TheEstablishedRows.test_a_back_filled_row_keeps_only_the_admitted_series` fails with `AssertionError`.
* `require_backfilled_admitted` stops raising (`bad = backfill.unadmitted_columns(seen, admitted)` becomes `bad = []`; #870, finding #862):
  `TheAdmittedGuard.test_an_extended_panel_with_an_unadmitted_back_filled_column_is_refused` fails with
  `AssertionError` (`LookAheadError` not raised).
* `guarded_fit` stops calling `backfill.require_posting_established` (a fit before the instant would run):
  `ThePostingGuard.test_a_fit_before_the_posting_instant_is_refused` fails with `AssertionError` (`LookAheadError` not raised).
* `require_same_published_days` compares nothing (`return` first line):
  `TheEstablishedRows.test_the_arms_agree_on_the_published_days` fails with `AssertionError` (`ValueError` not raised).
"""

from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "backfill_h5_726.py"


def _module():
    spec = importlib.util.spec_from_file_location("backfill_h5_726_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FIELDS = ["date", "sofr", "iorb", "sofr_volume", "tgcr", "bgcr", "reserve_balances", "tga", "tbill_4w", "sofr_p25",
          "quarter_end", "tax_date", "days_to_month_end"]


def _row(day: str, fill: str) -> dict:
    return {name: (day if name == "date" else fill) for name in FIELDS}


class TheEstablishedRows(unittest.TestCase):
    def test_a_back_filled_row_keeps_only_the_admitted_series(self):
        module = _module()
        admitted = {name: datetime(2018, 5, 17) for name in ("tgcr", "bgcr", "sofr")}
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "ext.csv", Path(tmp) / "est.csv"
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerow(_row("2018-03-29", "1.5"))
                writer.writerow(_row("2018-04-03", "1.5"))
            blanked = module.established_panel(source, target, admitted)
            rows = list(csv.DictReader(target.read_text(encoding="utf-8").splitlines()))
        self.assertEqual(blanked, 1)
        old, new = rows
        kept = {"date", "sofr", "iorb", "sofr_volume", "sofr_p25", "tgcr", "bgcr", "quarter_end", "tax_date", "days_to_month_end"}
        self.assertEqual(set(module.kept_columns(FIELDS, admitted)), kept)
        for name in FIELDS:
            if name not in kept:
                self.assertEqual(old[name], "", name)
                self.assertEqual(new[name], "1.5", name)
            else:
                self.assertNotEqual(old[name], "", name)

    def test_the_kept_columns_follow_the_admitted_list(self):
        module = _module()
        only_sofr = {"sofr": datetime(2018, 5, 17)}
        kept = set(module.kept_columns(FIELDS, only_sofr))
        self.assertNotIn("tgcr", kept)
        self.assertNotIn("bgcr", kept)
        self.assertIn("sofr_volume", kept)

    def test_the_arms_agree_on_the_published_days(self):
        module = _module()
        published = [(date(2018, 4, 3), {"tga": 1.0, "spread": 2.0}), (date(2018, 4, 4), {"tga": 1.5, "spread": 2.5})]
        extended = [(date(2018, 3, 29), {"tga": None, "spread": 1.0})] + published
        module.require_same_published_days(published, extended)
        changed = extended[:1] + [(date(2018, 4, 3), {"tga": 1.0, "spread": 9.0}), published[1]]
        with self.assertRaises(ValueError):
            module.require_same_published_days(published, changed)


class TheArms(unittest.TestCase):
    def test_an_arm_on_the_wrong_panel_is_refused(self):
        module = _module()
        module.require_arm("without", 0)
        module.require_arm("with", 899)
        for arm, prefix in (("without", 899), ("with", 0)):
            with self.assertRaises(ValueError):
                module.require_arm(arm, prefix)
        with self.assertRaises(ValueError):
            module.require_arm("both", 0)


class _Row:
    def __init__(self, day: date, values=None):
        self.date = day
        self.values = values or {}


class ThePostingGuard(unittest.TestCase):
    def test_a_fit_before_the_posting_instant_is_refused(self):
        module = _module()
        calls = []
        fit = module.guarded_fit(lambda frame, **kwargs: calls.append(len(frame)), datetime(2018, 5, 17), where="test")
        late = [_Row(date(2018, 3, 29)), _Row(date(2018, 5, 17)), _Row(date(2018, 6, 27))]
        fit(late, minimum_history=3)
        self.assertEqual(calls, [3])
        early = [_Row(date(2018, 3, 29)), _Row(date(2018, 5, 16))]
        with self.assertRaises(LookAheadError):
            fit(early, minimum_history=2)
        self.assertEqual(calls, [3])
        undeclared = module.guarded_fit(lambda frame, **kwargs: None, None, where="test")
        with self.assertRaises(LookAheadError):
            undeclared(late, minimum_history=3)

    def test_a_fit_on_published_days_only_is_not_affected(self):
        module = _module()
        fit = module.guarded_fit(lambda frame, **kwargs: "fitted", None, where="test")
        self.assertEqual(fit([_Row(date(2018, 4, 3)), _Row(date(2018, 4, 4))], minimum_history=2), "fitted")


class TheAdmittedGuard(unittest.TestCase):
    ADMITTED = {name: datetime(2018, 5, 17) for name in ("tgcr", "bgcr", "sofr")}

    def test_an_extended_panel_with_an_unadmitted_back_filled_column_is_refused(self):
        module = _module()
        clean = [_Row(date(2018, 3, 29), {"sofr": 1.5, "iorb": 1.7, "sofr_volume": 9.0, "tga": None, "quarter_end": 0.0})]
        published = [_Row(date(2018, 4, 3), {"sofr": 1.5, "iorb": 1.7, "tga": 100.0})]
        module.require_backfilled_admitted(clean + published, self.ADMITTED, where="test")
        dirty = [_Row(date(2018, 3, 29), {"sofr": 1.5, "iorb": 1.7, "tga": 250.0})]
        with self.assertRaises(LookAheadError):
            module.require_backfilled_admitted(dirty + published, self.ADMITTED, where="test")
        with self.assertRaises(LookAheadError):
            module.require_backfilled_admitted(clean + published, {"tgcr": datetime(2018, 5, 17)}, where="test")

    def test_the_series_a_fit_reads_are_those_a_back_filled_row_carries(self):
        module = _module()
        rows = [_Row(date(2018, 3, 29), {"sofr": 1.5, "iorb": 1.7, "sofr_volume": 9.0, "tga": None}),
                _Row(date(2018, 4, 3), {"sofr": 1.5, "iorb": 1.7, "sofr_volume": 9.0, "tga": 1.0})]
        self.assertEqual(module.series_carried(["spread_bps", "sofr_volume", "tga"], rows), ("sofr",))


class TheDeclaration(unittest.TestCase):
    def test_it_names_the_arms_the_candidate_and_the_reading_rule(self):
        declared = json.loads((ROOT / "metadata" / "backfill_h5_726.json").read_text(encoding="utf-8"))
        self.assertEqual(set(declared["arms"]), {"with", "without"})
        self.assertEqual(declared["candidate"]["name"], "gbm_funding")
        self.assertIn("lower bound", declared["reading_rule"]["gain"])
        self.assertIn("development, not a verdict", declared["reading_rule"]["kill"])

    def test_the_script_applies_both_back_fill_guards_and_reads_the_declared_instant(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("backfill.require_training_only(", text)
        self.assertIn("backfill.require_posting_established(", text)
        self.assertIn("backfill.load_posting_instant(POSTING)", text)

    def test_the_admitted_list_is_read_from_the_posting_declaration_not_copied(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("backfill.load_admitted_series(POSTING)", text)
        self.assertIn("backfill.require_series_admitted(", text)
        self.assertIn("require_backfilled_admitted(", text.split("def forecasts_command")[1])
        self.assertNotIn("ESTABLISHED", text)


if __name__ == "__main__":
    unittest.main()
