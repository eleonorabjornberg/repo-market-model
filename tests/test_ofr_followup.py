"""The OFR flag and skew-t scaling follow-up (#537, of #477 and PR #496): what is declared, before any score.

No new availability or staleness guard is added: the flag and filled columns are read through the
as-of rule at the OFR source's own lag (`test_ofr_publication`), and the OFR look-ahead guard of #522
is called by the script's `panel` and `run`. These tests pin the declaration (the dealer group plus the
tri-party rate and its flag, the GCF rate out, the scaling on the skew-t candidate and its control
only) and the guard.

Written red first: `metadata/ofr_followup.json` and `unused_inputs.py panel` did not exist.

Recorded mutation (CLAUDE.md), 11 October 2026, in a disposable copy of `scripts/unused_inputs.py`:
the line `dvp_segment.require_ofr_public(rows)` in `run_command` deleted.
`test_run_refuses_a_panel_with_an_ofr_value_before_it_was_public` then fails with `AssertionError`
(`LookAheadError not raised`): the run goes on to fit on the leaked panel.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import contract, ofr_publication, pressure_judge as pj  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

spec = importlib.util.spec_from_file_location("unused_inputs", ROOT / "scripts" / "unused_inputs.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

FOLLOWUP = json.loads((ROOT / "metadata" / "ofr_followup.json").read_text(encoding="utf-8"))
BASE = json.loads((ROOT / "metadata" / "unused_inputs.json").read_text(encoding="utf-8"))
RISK = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text(encoding="utf-8"))


class DeclarationTests(unittest.TestCase):
    def test_five_candidates_are_the_five_passers_with_the_dealer_group(self):
        self.assertEqual(len(FOLLOWUP["candidates"]), 5)
        self.assertEqual(
            {e["passer"] for e in FOLLOWUP["candidates"].values()},
            {e["passer"] for e in BASE["candidates"].values()},
        )
        self.assertEqual({e["group"] for e in FOLLOWUP["candidates"].values()}, {"dealer_ofr"})

    def test_the_group_is_the_dealer_group_plus_the_tri_party_rate_and_its_flag(self):
        columns = FOLLOWUP["groups"]["dealer_ofr"]["columns"]
        self.assertEqual(columns[: len(BASE["groups"]["dealer"]["columns"])], BASE["groups"]["dealer"]["columns"])
        self.assertEqual(columns[len(BASE["groups"]["dealer"]["columns"]):], ["tri_rate_filled", "tri_rate_not_yet_published"])

    def test_the_gcf_rate_and_its_observed_indicator_are_not_inputs(self):
        columns = set(FOLLOWUP["groups"]["dealer_ofr"]["columns"])
        self.assertFalse(columns & {"gcf_rate_filled", "gcf_rate_not_yet_published", "ofr_gcf_rate"})
        self.assertFalse(any("observed" in column for column in ofr_publication.COLUMNS))
        self.assertFalse(FOLLOWUP["ofr_not_yet_published"]["series"]["ofr_gcf_rate"]["scored"])

    def test_the_declared_first_public_date_is_the_modules(self):
        self.assertEqual(date.fromisoformat(FOLLOWUP["ofr_not_yet_published"]["first_public"]), ofr_publication.FIRST_PUBLIC)
        for raw, entry in FOLLOWUP["ofr_not_yet_published"]["series"].items():
            self.assertEqual((entry["filled"], entry["flag"]), ofr_publication.SERIES[raw])

    def test_each_candidate_is_its_passer_plus_the_group_at_every_horizon(self):
        for name, entry in FOLLOWUP["candidates"].items():
            for horizon in FOLLOWUP["horizons"]:
                passer = script.candidate_features(FOLLOWUP, RISK, entry["passer"], horizon)
                got = script.candidate_features(FOLLOWUP, RISK, name, horizon)
                self.assertEqual(got[: len(passer)], passer, (name, horizon))
                self.assertEqual(list(got[len(passer):]), FOLLOWUP["groups"][entry["group"]]["columns"], (name, horizon))

    def test_the_extra_control_is_its_passer_alone(self):
        for horizon in FOLLOWUP["horizons"]:
            self.assertEqual(
                script.candidate_features(FOLLOWUP, RISK, "risk_quantile_skewt_base_minmax", horizon),
                script.candidate_features(FOLLOWUP, RISK, "risk_quantile_skewt_base", horizon),
            )

    def test_the_scaling_is_on_the_skew_t_candidate_and_its_control_only(self):
        self.assertEqual(
            set(FOLLOWUP["input_scaling"]), {"risk_quantile_skewt_base_dealer_ofr", "risk_quantile_skewt_base_minmax"}
        )
        self.assertEqual(set(FOLLOWUP["input_scaling"].values()), {"minmax"})
        self.assertEqual(
            FOLLOWUP["also_against"], {"risk_quantile_skewt_base_dealer_ofr": "risk_quantile_skewt_base_minmax"}
        )
        for name in FOLLOWUP["input_scaling"]:
            self.assertEqual(RISK["candidates"][script.candidate_owner(FOLLOWUP, name)]["kind"], "quantile_skewt")

    def test_the_candidate_files_match_the_declaration(self):
        declaration = pj.load_declaration()
        for name, entry in FOLLOWUP["candidates"].items():
            filed = declaration.candidates[name]
            self.assertEqual(filed["control"], entry["passer"])
            self.assertEqual(list(filed["features"]), list(script.candidate_features(FOLLOWUP, RISK, name, 1)), name)
        filed = declaration.candidates["risk_quantile_skewt_base_minmax"]
        self.assertEqual(filed["control"], "risk_quantile_skewt_base")

    def test_nothing_is_published_and_nothing_scores_a_locked_day(self):
        self.assertLess(FOLLOWUP["scoring"]["last_day"], "2026-01-01")
        declaration = pj.load_declaration()
        for name in list(FOLLOWUP["candidates"]) + list(FOLLOWUP["extra_controls"]):
            self.assertNotIn(name, declaration.document()["confirmation"]["candidates"])
        self.assertFalse(set(ofr_publication.COLUMNS) & set(contract.FEATURE_FIELDS))
        collected = script.all_column_fields()
        for column in ofr_publication.COLUMNS:
            self.assertIn(column, collected)


class GuardTests(unittest.TestCase):
    def write(self, directory, value, columns=("tri_rate_filled",)):
        path = Path(directory) / "panel.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["date", "sofr", "iorb", "reserve_balances", "tga", "ofr_tri_rate"])
            day = date(2019, 9, 2)
            for _ in range(8):
                if day.weekday() < 5:
                    writer.writerow([day.isoformat(), "2.2", "2.1", "1500", "300", value])
                day += timedelta(days=1)
        return path

    def test_run_refuses_a_panel_with_an_ofr_value_before_it_was_public(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, "2.3")
            args = argparse.Namespace(
                panel=path, published=path, horizon=1, output=Path(directory) / "o.json", candidate=None,
                declaration=ROOT / "metadata" / "ofr_followup.json",
            )
            with mock.patch.object(script, "audit_panel"), mock.patch.object(
                script, "committed_declaration", side_effect=lambda path: json.loads(Path(path).read_text(encoding="utf-8"))
            ):
                with self.assertRaises(LookAheadError):
                    script.run_command(args)

    def test_panel_adds_the_columns_and_refuses_a_leaked_value(self):
        with tempfile.TemporaryDirectory() as directory:
            leaked = self.write(directory, "2.3")
            args = argparse.Namespace(panel=leaked, output=Path(directory) / "out.csv")
            with self.assertRaises(LookAheadError):
                script.panel_command(args)
            clean = self.write(directory, "")
            args = argparse.Namespace(panel=clean, output=Path(directory) / "out.csv")
            with mock.patch("builtins.print"):
                script.panel_command(args)
            with (Path(directory) / "out.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertTrue(rows)
            self.assertEqual({r["tri_rate_not_yet_published"] for r in rows}, {"1.0"})
            self.assertEqual({r["tri_rate_filled"] for r in rows}, {"0.0"})


if __name__ == "__main__":
    unittest.main()
