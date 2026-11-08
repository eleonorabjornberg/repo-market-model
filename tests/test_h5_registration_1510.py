"""The H5 registration draft of #1510: `metadata/registrations/h5_s3c_ann_net.json` and its reader `docs/registrations/h5-s3c-ann-net.md`.

The record is a DRAFT for Eleonora. Registering (s3c-ann-net) is her own `GO #1510` and her merge; a session never posts the `GO`. What is pinned:

* the record says it is a draft, is not registered, and carries no attestation (the `owner_attestations.json` entry is appended only from her own comment);
* it names the candidate the manifest names and points at files that exist (the manifest, the validation report, the design, the power page);
* the confirmation design it states equals `docs/decisions/h5-confirmation-design.md` (500 origins, at least 24 months, a 30-month ceiling, one final
  analysis, mean block 50, 50,000 replications, the claim against B1'*-cap alone with B2*-cap and B4 beside it), and invents no value of its own;
* the power it states beside the design equals #1392's full-mode `result-full.json` (10% skill with B1'* binding, 10% on both baselines, and
  development-level skill, on both bootstraps, at 500 origins), recomputed here from the pass counts and not copied;
* every marked question has numbered options and a default and appears in the reader;
* it scores no day and moves no pin.

Mutation: not a leakage, availability or staleness guard, so no recorded mutation. The test was run first against a tree without the record and failed with
`FileNotFoundError`.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "metadata" / "registrations" / "h5_s3c_ann_net.json"
READER = ROOT / "docs" / "registrations" / "h5-s3c-ann-net.md"
DESIGN = ROOT / "docs" / "decisions" / "h5-confirmation-design.md"
POWER = ROOT / "docs" / "research" / "confirmation-size-power-1392" / "result-full.json"
MANIFEST = ROOT / "metadata" / "h5_registration_manifest.json"


def load(path):
    return json.loads(path.read_text())


class RecordShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = load(RECORD)
        cls.reader = READER.read_text()

    def test_it_is_a_draft_that_registers_nothing(self):
        self.assertTrue(self.record["status"].startswith("DRAFT"))
        self.assertIs(self.record["registered"], False)
        self.assertIsNone(self.record["owner_attestation"])
        self.assertEqual(self.record["issue"], 1510)
        self.assertIn("H5", self.record["serves"])

    def test_it_names_the_candidate_of_the_manifest(self):
        self.assertEqual(self.record["candidate"]["name"], load(MANIFEST)["candidate"]["name"])
        self.assertEqual(self.record["candidate"]["label"], "(s3c-ann-net)")

    def test_every_file_it_points_at_exists(self):
        for key, path in self.record["attached"].items():
            self.assertTrue((ROOT / path).exists(), (key, path))

    def test_the_freeze_of_2_november_is_stated(self):
        freeze = self.record["frozen_choices"]
        self.assertEqual(freeze["probability_rule"], "open_tail")
        self.assertEqual(freeze["srf_cap"], "kept, margin 0 bp")
        self.assertIn("secondary", freeze["uncapped"])

    def test_the_reader_links_the_record_and_says_draft(self):
        self.assertIn("metadata/registrations/h5_s3c_ann_net.json", self.reader)
        self.assertIn("draft", self.reader.lower())
        self.assertIn("GO #1510", self.reader)

    def test_every_question_has_numbered_options_and_a_default(self):
        questions = self.record["questions"]
        self.assertTrue(questions)
        for q in questions:
            self.assertGreaterEqual(len(q["options"]), 2, q["id"])
            self.assertIn(q["default"], range(1, len(q["options"]) + 1), q["id"])
            self.assertIn(q["id"], self.reader, q["id"])


class DesignIsTheDesignInForceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = load(RECORD)["confirmation_design"]
        cls.text = " ".join(DESIGN.read_text().split())

    def test_the_stated_numbers_are_in_the_decision_record(self):
        d = self.design
        for phrase in (
            f"{d['origins']} eligible decision origins",
            f"at least {d['minimum_months']} calendar months",
            f"a {d['ceiling_months']}-month ceiling",
            "One final efficacy analysis",
            f"mean block {d['bootstrap_mean_block']} origins",
            f"{d['bootstrap_replications']:,} replications",
            "B1′*-cap alone",
            "B2*-cap is reported beside it",
            "B4 (#1360",
            "0.97 the 3% practical-meaning threshold",
        ):
            self.assertIn(phrase, self.text, phrase)

    def test_the_record_invents_no_value_of_its_own(self):
        d = self.design
        self.assertEqual((d["origins"], d["minimum_months"], d["ceiling_months"]), (500, 24, 30))
        self.assertEqual((d["bootstrap_mean_block"], d["bootstrap_replications"]), (50, 50000))
        self.assertEqual(d["practical_threshold"], 0.97)
        self.assertEqual(d["primary_claim_against"], "B1'*-cap")
        self.assertEqual(d["final_analyses"], 1)


class PowerIsTheMeasuredPowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.power = load(RECORD)["power_beside_the_design"]
        cls.cells = load(POWER)["cells"]

    def rate(self, group, scheme, effects, n=500):
        hit = [c for c in self.cells if c["group"] == group and c["scheme"] == scheme and c["n"] == n
               and c["ell"] == 50 and c["flag_effect"] is None and c["effects"] == effects]
        self.assertEqual(len(hit), 1, (group, scheme, effects))
        return round(100 * hit[0]["main"]["pass"] / hit[0]["count"], 1)

    def test_the_stated_rates_are_recomputed_from_the_1392_cells(self):
        for scheme in ("block", "regime"):
            row = self.power[scheme]
            self.assertEqual(row["b1_binding_10pct"], self.rate("binding_observed", scheme, [0.1, None]), scheme)
            self.assertEqual(row["both_10pct"], self.rate("main", scheme, [0.1, 0.1]), scheme)
            self.assertEqual(row["development_level"], self.rate("observed", scheme, [None, None]), scheme)

    def test_the_power_says_it_is_development_data_and_short_of_80(self):
        self.assertIn("not a verdict", self.power["reading"])
        self.assertIn("500 origins is short of 80%", self.power["reading"])
        self.assertEqual(self.power["source"], "docs/research/confirmation-size-power-1392-full-result.md")


class NothingElseMovesTests(unittest.TestCase):
    def test_it_scores_no_locked_day_and_moves_no_pin(self):
        record = load(RECORD)
        self.assertIs(record["lockbox"]["scores_any_day"], False)
        self.assertIs(record["live_pin"]["moved"], False)
        self.assertEqual(record["lockbox"]["decision"], "docs/decisions/lockbox.md")


if __name__ == "__main__":
    unittest.main()
