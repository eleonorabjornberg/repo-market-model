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
        admitted = {name: datetime(2018, 5, 17) for name in ("tgcr", "bgcr", "sofr", "iorb")}
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
        kept = {"date", "sofr", "iorb", "sofr_p25", "tgcr", "bgcr", "quarter_end", "tax_date", "days_to_month_end"}
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
        self.assertNotIn("sofr_volume", kept)

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
    ADMITTED = {name: datetime(2018, 5, 17) for name in ("tgcr", "bgcr", "sofr", "iorb")}

    def test_an_extended_panel_with_an_unadmitted_back_filled_column_is_refused(self):
        module = _module()
        clean = [_Row(date(2018, 3, 29), {"sofr": 1.5, "iorb": 1.7, "tga": None, "quarter_end": 0.0})]
        published = [_Row(date(2018, 4, 3), {"sofr": 1.5, "iorb": 1.7, "tga": 100.0})]
        module.require_backfilled_admitted(clean + published, self.ADMITTED, where="test")
        dirty = [_Row(date(2018, 3, 29), {"sofr": 1.5, "iorb": 1.7, "tga": 250.0})]
        with self.assertRaises(LookAheadError):
            module.require_backfilled_admitted(dirty + published, self.ADMITTED, where="test")
        volume = [_Row(date(2018, 3, 29), {"sofr": 1.5, "iorb": 1.7, "sofr_volume": 9.0, "tga": None})]
        with self.assertRaises(LookAheadError):
            module.require_backfilled_admitted(volume + published, self.ADMITTED, where="test")
        with self.assertRaises(LookAheadError):
            module.require_backfilled_admitted(clean + published, {"tgcr": datetime(2018, 5, 17)}, where="test")

    def test_the_series_a_fit_reads_are_those_a_back_filled_row_carries(self):
        module = _module()
        rows = [_Row(date(2018, 3, 29), {"sofr": 1.5, "iorb": 1.7, "tga": None}),
                _Row(date(2018, 4, 3), {"sofr": 1.5, "iorb": 1.7, "sofr_volume": 9.0, "tga": 1.0})]
        self.assertEqual(module.series_carried(["spread_bps", "tga"], rows), ("iorb", "sofr"))
        # The SOFR volume is a series of its own (#887): a fit that read it would need it admitted.
        carried = [_Row(date(2018, 3, 29), {"sofr": 1.5, "sofr_volume": 9.0})]
        self.assertEqual(module.series_carried(["sofr_volume"], carried), ("sofr_volume",))


class TheReread(unittest.TestCase):
    def test_a_decision_day_belongs_to_a_half_year_of_2018_19(self):
        module = _module()
        self.assertEqual(module.period_label(date(2018, 6, 29)), "2018 H1")
        self.assertEqual(module.period_label(date(2018, 7, 2)), "2018 H2")
        self.assertEqual(module.period_label(date(2019, 12, 31)), "2019 H2")
        self.assertIsNone(module.period_label(date(2020, 1, 2)))

    def test_a_refit_record_counts_back_filled_rows_and_blank_input_cells(self):
        module = _module()
        frame = [_Row(date(2018, 3, 28), {"a": None, "b": None}), _Row(date(2018, 4, 3), {"a": 1.0, "b": None}),
                 _Row(date(2018, 4, 4), {"a": 1.0, "b": 2.0}), _Row(date(2018, 4, 5), {"a": 1.0, "b": 2.0})]
        record = module.refit_record(frame, ("a", "b"))
        self.assertEqual((record["train_rows"], record["backfilled_rows"], record["imputed_cells"]), (4, 1, 3))
        self.assertAlmostEqual(record["backfilled_share"], 0.25)
        self.assertAlmostEqual(record["imputed_share"], 3 / 8)
        log = []
        module.guarded_fit(lambda f, **k: None, datetime(2018, 5, 17), where="t", log=log, inputs=("a",))(
            [_Row(date(2018, 6, 27), {"a": 1.0})], minimum_history=1
        )
        self.assertEqual(len(log), 1)

    def test_the_ruled_interval_and_the_reading(self):
        module = _module()

        class Test:
            mean_difference, standard_error, draws = 0.1, 0.05, 100
            t_draws = tuple(range(-50, 50))

        lower, upper = module.ruled_interval(Test)
        from repo_model import scoring_protocol as sp

        self.assertAlmostEqual(lower, 0.1 - 0.05 * sp._quantile(Test.t_draws, 0.95), places=9)
        self.assertAlmostEqual(upper, 0.1 - 0.05 * sp._quantile(Test.t_draws, 0.05), places=9)
        self.assertLess(lower, upper)
        self.assertEqual(module.reading(None), "not tested (too few decision days)")
        self.assertEqual(module.reading({"gain": True, "cost": False}), "gain shown")
        self.assertEqual(module.reading({"gain": False, "cost": True}), "cost shown")
        self.assertIn("neither", module.reading({"gain": False, "cost": False}))


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

    def test_the_reread_declaration_names_the_arms_the_interval_the_orientation_and_the_share(self):
        declared = json.loads((ROOT / "metadata" / "backfill_h5_726_reread.json").read_text(encoding="utf-8"))
        self.assertIn("studentized", declared["interval"]["rule"])
        self.assertIn("CRPS(without) - CRPS(with)", declared["difference"])
        self.assertIn("(B)", declared["critical_value"]["orientation"])
        self.assertEqual(declared["mostly_imputed_fits"]["primary_share"], 0.5)
        self.assertIn("development", declared["reading_rule"]["kill_lines"])


class TheSecondReread(unittest.TestCase):
    """#935: the re-read without the workbook SOFR volume, the kill read at 75% back-filled."""

    def test_the_935_declaration_reads_the_kill_at_75_percent_and_keeps_50_and_90_for_reference(self):
        declared = json.loads((ROOT / "metadata" / "backfill_h5_935.json").read_text(encoding="utf-8"))
        self.assertEqual(declared["issue"], 935)
        self.assertEqual(declared["mostly_imputed_fits"]["primary_share"], 0.75)
        self.assertEqual(declared["mostly_imputed_fits"]["sensitivity_shares"], [0.5, 0.9])
        self.assertIn("studentized", declared["interval"]["rule"])
        self.assertIn("development", declared["reading_rule"]["kill_lines"])

    def test_the_volume_is_blank_on_every_back_filled_row_and_kept_on_published_rows(self):
        module = _module()
        admitted = {name: datetime(2018, 5, 17) for name in ("tgcr", "bgcr", "sofr")}
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "ext.csv", Path(tmp) / "est.csv"
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerow(_row("2018-03-30", "1.5"))
                writer.writerow(_row("2018-04-03", "1.5"))
            module.established_panel(source, target, admitted)
            rows = list(csv.DictReader(target.open(newline="", encoding="utf-8")))
        self.assertEqual(module.backfilled_volume_cells(rows_as_panel(rows)), 0)
        self.assertEqual(rows[1]["sofr_volume"], "1.5")

    def test_a_back_filled_volume_cell_is_counted(self):
        module = _module()
        rows = [_panel_row("2018-03-30", sofr_volume=3.0), _panel_row("2018-04-03", sofr_volume=3.0)]
        self.assertEqual(module.backfilled_volume_cells(rows), 1)

    def test_the_comparison_with_895_lines_up_the_groups_and_marks_a_missing_one(self):
        module = _module()
        new = {"period 2018 H2": {"mean_d": -0.1, "interval_90": [-0.2, -0.05]}, "pooled": {"mean_d": 0.0, "interval_90": [-0.04, 0.04]}}
        old = {"period 2018 H2": {"mean_d": -0.229, "interval_90": [-0.359, -0.114]}, "regime 2024": {"mean_d": -0.03, "interval_90": [-0.077, -0.005]}}
        table = module.compare_with_previous(new, old, ["period 2018 H2", "regime 2024"])
        self.assertEqual(table[0]["group"], "period 2018 H2")
        self.assertAlmostEqual(table[0]["moved_by"], 0.129)
        self.assertIsNone(table[1]["new"])
        self.assertEqual(table[1]["previous"]["mean_d"], -0.03)

    def test_the_markdown_names_the_issue_of_its_declaration(self):
        module = _module()
        document = {"issue": 935, "decision_days": ["2018-06-29", "2025-12-31", 3], "groups": {}, "group_sizes": {},
                    "refits_lead_1": [], "kill_lines": [], "comparison": []}
        self.assertIn("#935", module.reread_markdown(document).splitlines()[0])


class _PanelRow:
    def __init__(self, day: str, values: dict):
        self.date, self.values = date.fromisoformat(day), values


def _panel_row(day: str, **values) -> "_PanelRow":
    return _PanelRow(day, values)


def rows_as_panel(rows):
    return [_PanelRow(r["date"], {k: (float(v) if v != "" else None) for k, v in r.items() if k != "date"}) for r in rows]


if __name__ == "__main__":
    unittest.main()
