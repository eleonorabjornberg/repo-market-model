"""The declared variant of `scripts/mechanism_encodings_1029.py` (#1029, H5 step 3): which inputs it reads and what its fit is handed.

The encodings' own arithmetic and as-of reads are pinned in `test_mechanism_encodings_1029.py`. Here: the variant is #1027's direct variant with the six raw levels
replaced in place and nothing else changed (same leaf, same pairing, same target-row and observed columns), it passes the #947 guard as it stands (direct pairs), and
the estimator receives, in every training pair, the encoded value of the row the as-of rule reads for that pair's target.

Recorded mutation (CLAUDE.md), 22 October 2026, in a disposable copy: `mechanism_encodings_1029.variant_features`, the line `return me.encode_features(base)`
changed to `return base` (the "encoded" variant reads the raw levels): `VariantTests.test_each_raw_level_is_replaced_in_place_and_nothing_else_changes` fails with
`AssertionError` (`'reserve_balances' != 'reserves_to_median'`: a raw level is still a regressor), and `FitTests.test_the_estimator_is_handed_the_encoded_value_of_the_row_the_rule_reads`
fails with `KeyError: 'tbill_4w_less_iorb_bps'` (the encoded column is not among the reads of the rule built on the variant's features).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mechanism_encodings_1029_script", REPO / "scripts" / "mechanism_encodings_1029.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import mechanism_encodings as me, ml, measurement_fields  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402

ac = script.ac
ROWS = 90


def business_days(count):
    days, day = [], date(2024, 1, 1)
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def raw_panel(count=ROWS):
    """Every column of every row is unique to its row; the raw levels are shaped so that each encoding is unique to its row too."""

    columns = []
    for h in script.HORIZONS:
        columns += [c for c in ac.regressors(script.variant_features(script.BASE, h)) if c not in columns]
    out = []
    for i, day in enumerate(business_days(count)):
        values = {
            "sofr": 15.0 + i / 100.0, "iorb": 5.0, "sofr_p25": 14.0 - i / 1000.0, "sofr_p75": 15.2 + i / 50.0,
            "tbill_4w": 4.0 + i / 100.0, "tbill_13w": 4.5 - i / 100.0, "sofr_volume": 1000.0 + 3 * i, "reserve_balances": 3000.0 - 2 * i,
        }
        for k, name in enumerate(columns):
            values.setdefault(name, float(10_000 * (k + 1) + i))
        out.append(DailyObservation(date=day, values=values))
    return out


class NeedsExtra(unittest.TestCase):
    def setUp(self):
        if all(importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn")):
            return
        if os.environ.get("REPO_MODEL_REQUIRE_ML"):
            self.fail("REPO_MODEL_REQUIRE_ML is set but the optional 'ml' extra is not importable")
        self.skipTest("the optional 'ml' extra is not installed")


class VariantTests(unittest.TestCase):
    def test_each_raw_level_is_replaced_in_place_and_nothing_else_changes(self):
        for h in script.HORIZONS:
            base = script.variant_features(script.BASE, h)
            enc = script.variant_features(script.ENC, h)
            self.assertEqual(len(base), len(enc))
            for before, after in zip(base, enc):
                self.assertEqual(after, me.ENCODED.get(before, before))
            self.assertFalse(set(me.ENCODED) & set(enc), f"lead {h}: a raw level is still a regressor")
            for column in me.ENCODED.values():
                self.assertIn(column, enc)

    def test_the_target_row_and_observed_columns_are_1027s(self):
        for h in script.HORIZONS:
            enc = script.variant_features(script.ENC, h)
            for column in ac.target_row_columns(h) + ac.OBSERVED_COLUMNS:
                self.assertIn(column, enc)
            self.assertIn("tga", enc)

    def test_a_variant_that_is_not_declared_is_refused(self):
        with self.assertRaises(ValueError):
            script.variant_features("gbm_funding", 1)
        with self.assertRaises(ValueError):
            script.variant_fit("gbm_funding", ("spread_bps",))

    def test_the_base_is_1027s_direct_variant_at_every_lead(self):
        for h in script.HORIZONS:
            self.assertEqual(script.variant_features(script.BASE, h), ac.variant_features(ac.DIRECT, h))


class FitTests(NeedsExtra):
    def test_the_fit_is_1027s_direct_fit_over_the_encoded_regressors(self):
        features = script.variant_features(script.ENC, 2)
        fit = script.variant_fit(script.ENC, features)
        self.assertEqual(fit.func, ml.fit_gradient_boosted_quantiles)
        self.assertEqual(fit.keywords["training_pairs"], "direct")
        self.assertEqual(fit.keywords["min_samples_leaf"], ac.LEAF)
        self.assertEqual(tuple(fit.keywords["regressors"]), ac.regressors(features))

    def test_the_estimator_is_handed_the_encoded_value_of_the_row_the_rule_reads(self):
        registry = measurement_fields.load_registry()
        rows = me.build_columns(raw_panel())
        dates = [r.date for r in rows]
        recorded = []
        original = ml._fitted_levels

        def record(estimator_class, grid, design, targets, random_state, min_samples_leaf):
            recorded.append(([list(r) for r in design], list(targets)))
            return original(estimator_class, grid, design, targets, random_state, min_samples_leaf)

        for h in script.HORIZONS:
            features = script.variant_features(script.ENC, h)
            names = ("spread_bps",) + ac.regressors(features)
            with ac._load("net_settlement").switched_on(), me.switched_on(), mock.patch.object(ml, "_fitted_levels", record):
                rule = InformationRule(registry, tuple(features), decision_time=ac.decision_time(), horizon=h)
                recorded.clear()
                script.variant_fit(script.ENC, features)(rows, minimum_history=20, information=rule)
                design, targets = recorded[0]
                self.assertGreater(len(design), 30)
                checked = 0
                by_spread = {round(r.values["sofr"] * 100.0 - r.values["iorb"] * 100.0, 6): i for i, r in enumerate(rows)}
                for line, target in zip(design, targets):
                    j = by_spread[round(target, 6)]
                    info = rule.information_set(dates, j)
                    read = {r.feature: r.row for r in info.reads}
                    for column in me.ENCODED.values():
                        expected = rows[read[column]].values[column]
                        if expected is None:  # a regressor carried as None gets the fit's own imputation (ml.py), not a value of any row
                            continue
                        self.assertEqual(line[names.index(column)], expected, (h, j, column))
                        checked += 1
                self.assertGreater(checked, 100)


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))

    def test_the_committed_declaration_is_what_declare_writes(self):
        self.assertEqual(self.document, json.loads(json.dumps(script.declaration_document())))

    def test_it_names_one_variant_and_its_six_encodings(self):
        self.assertEqual(self.document["issue"], 1029)
        self.assertEqual(list(self.document["variant"]), [script.ENC])
        self.assertEqual(
            {v["column"] for v in self.document["variant"][script.ENC]["encodings"].values()}, set(me.ENCODED.values())
        )

    def test_the_declared_comparators_are_the_directive_s(self):
        self.assertEqual(
            self.document["benchmarks"], ["gbm_funding", "gbm_funding_cal_direct", "B1", "B1_prime", "B2", "spread_mr_ctx"]
        )

    def test_a_declaration_that_is_not_committed_is_refused(self):
        with mock.patch.object(ac.subprocess, "run") as run:
            run.return_value.stdout = " M metadata/mechanism_encodings_1029.json\n"
            with self.assertRaises(SystemExit):
                ac.committed_declaration(script.DECLARATION)


class ReadingTests(unittest.TestCase):
    def row(self, skill, low, high):
        return {"skill": skill, "skill_interval": [low, high]}

    def test_beats_loses_and_not_shown_are_read_from_the_interval(self):
        text = script.reading_rules(
            {
                "gbm_funding": {"pooled": self.row(0.02, 0.005, 0.04), "calendar": self.row(0.01, -0.02, 0.04), "ordinary": self.row(-0.05, -0.08, -0.01)},
            }
        )[0]
        self.assertIn("on all decision days beats it", text)
        self.assertIn("on calendar days is not shown to differ from it", text)
        self.assertIn("on ordinary days loses to it", text)

    def test_an_unscored_or_undefined_cut_is_not_read(self):
        (text,) = script.reading_rules({"gbm_funding_cal_direct": {"pooled": None, "calendar": {"undefined": "x"}, "ordinary": None}})
        self.assertEqual(text.count("not read"), 3)


if __name__ == "__main__":
    unittest.main()
