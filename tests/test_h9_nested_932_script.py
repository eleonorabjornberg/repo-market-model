"""The aligned re-run of H9 step 3 (`scripts/h9_nested_932.py`, #932; finding #915): what the plus walks train on.

#842's plus walks fitted on one-step pairs `(p, p + 1)`: row p's column `h9fc_<T>_h<h>` holds the forecast of T for day p + h, and
it trained against the spread of day p + 1. At a lead h >= 2 the model learned the forecast of one day against the label of
another, and was then served the forecast for the very day it predicts. The aligned walks train on direct pairs
(`training_pairs="direct"`): each label day t is paired with the row its own forecast reads, t - h, and that row's column holds
the forecast of T for day t. These tests fit the script's fitter on a frame whose column on row d is the *index of the day it
forecasts* (d + h) and whose spread on row t is t, so a design row aligned with its label has the same number in both.

Recorded mutations (CPython 3.11, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run alone, confirmed applied
by `grep` and reverted afterwards; unmutated control green before and after):

1. `fitter`: `extra = {"training_pairs": "direct"} if direct else {}` replaced by `extra = {}` (the one-step pairs of #842 again).
   `PairingTests.test_a_plus_design_row_holds_the_forecast_of_its_label_day` fails with `AssertionError: Lists differ`
   (lead 2: the design column reads `[2.0, 3.0, ...]` against the label days `[1.0, 2.0, ...]`; lead 3 is two days ahead, lead 5
   four). Before the script existed the whole module failed with `FileNotFoundError` on `scripts/h9_nested_932.py`, and
   `test_the_one_step_design_of_842_is_misaligned_at_lead_2_and_up` records the fault of #842 itself: its design holds the
   forecast of day p + h against the label of day p + 1, `lead - 1` days apart.
2. `check_alignment`: `if settings.get("training_pairs") != "direct":` replaced by `if False:`. A plus walk that was fitted on
   one-step pairs is then scored as an aligned one; `PairingTests.test_a_plus_walk_on_one_step_pairs_is_refused` fails with
   `AssertionError: ValueError not raised`.
3. `refuse_locked`: `require_unlocked(list(days), ...)` replaced by `return`. `LockedDayTests.test_a_locked_day_is_refused` fails
   with `AssertionError: LookAheadError not raised`.
4. `check_target_walk`: `m706.check_pairing(settings_of(document))` replaced by `return`. A target walk fitted on one-step
   pairs is then read as an aligned input; `TargetWalkPairingTests.test_a_target_walk_on_one_step_pairs_or_without_settings_is_refused`
   fails with `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from datetime import date, time
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("h9_nested_932_script", REPO / "scripts" / "h9_nested_932.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import asof, contract, ml, target_forecasts as tf  # noqa: E402
from repo_model.data import DailyObservation, next_business_day  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

TARGET = "on_rrp_change_bn"
ROWS = 90


class RecordingQuantile:
    """Keeps every design and target it is fitted on; predicts the training targets' quantile."""

    fits = []

    def __init__(self, *, loss, quantile, early_stopping, random_state, min_samples_leaf):
        self.quantile = quantile
        self.value = 0.0

    def fit(self, design, targets):
        RecordingQuantile.fits.append(([tuple(row) for row in design], list(targets)))
        ordered = sorted(targets)
        self.value = ordered[min(len(ordered) - 1, int(self.quantile * len(ordered)))]
        return self

    def predict(self, design):
        return [self.value] * len(design)


def _frame(lead: int):
    """Row t holds spread t (bp) and, in the column, t + lead: the index of the day its forecast is for."""

    days = [date(2020, 3, 2)]
    while len(days) < ROWS:
        days.append(next_business_day(days[-1], 1))
    column = tf.column(TARGET, lead)
    return [
        DailyObservation(day, {"sofr": 5.0 + 0.01 * i, "iorb": 5.0, column: float(i + lead)}) for i, day in enumerate(days)
    ], column


def _rule(column: str, lead: int):
    measurement = json.loads((REPO / "metadata" / "sources_measurement.json").read_text(encoding="utf-8"))
    lag = {"basis": "record_date", "unit": "calendar_days", "days": 0, "available_time": "16:00", "timezone": "America/New_York"}
    features = (column, "spread_bps")
    with tf.switched_on():
        sources = contract.sources_for_features(features)
        registry = {source: {"release_lag": dict(lag)} for source in sources if source != tf.SOURCE_ID}
        registry[tf.SOURCE_ID] = measurement[tf.SOURCE_ID]
        return asof.InformationRule(registry, features, decision_time=time(16, 0), horizon=lead)


def _skip_without_ml(test: unittest.TestCase) -> None:
    if importlib.util.find_spec("numpy") is None or importlib.util.find_spec("sklearn") is None:
        test.skipTest("the ml extra is not installed")


class PairingTests(unittest.TestCase):
    def setUp(self):
        _skip_without_ml(self)
        RecordingQuantile.fits = []
        patcher = mock.patch.object(ml, "_estimator_class", return_value=RecordingQuantile)
        patcher.start()
        self.addCleanup(patcher.stop)

    def design_and_labels(self, fit, lead: int):
        rows, column = _frame(lead)
        rule = _rule(column, lead)
        with tf.switched_on():
            fit(rows, information=rule, minimum_history=40)
        design, labels = RecordingQuantile.fits[0]
        return [round(row[-1], 6) for row in design], [round(v, 6) for v in labels], column

    def test_a_plus_design_row_holds_the_forecast_of_its_label_day(self):
        for lead in (1, 2, 3, 5):
            with self.subTest(lead=lead):
                RecordingQuantile.fits = []
                column = tf.column(TARGET, lead)
                fit = script.fitter(("spread_bps", column), direct=True)
                held, labels, _ = self.design_and_labels(fit, lead)
                self.assertTrue(labels)
                self.assertEqual(held, labels)

    def test_the_one_step_design_of_842_is_misaligned_at_lead_2_and_up(self):
        for lead in (2, 3, 5):
            with self.subTest(lead=lead):
                RecordingQuantile.fits = []
                column = tf.column(TARGET, lead)
                fit = script.fitter(("spread_bps", column), direct=False)
                held, labels, _ = self.design_and_labels(fit, lead)
                self.assertEqual([round(h - label, 6) for h, label in zip(held, labels)], [lead - 1.0] * len(labels))

    def test_the_two_designs_agree_at_lead_1(self):
        column = tf.column(TARGET, 1)
        held_one, labels_one, _ = self.design_and_labels(script.fitter(("spread_bps", column), direct=False), 1)
        RecordingQuantile.fits = []
        held_direct, labels_direct, _ = self.design_and_labels(script.fitter(("spread_bps", column), direct=True), 1)
        self.assertEqual(held_one, labels_one)
        self.assertEqual(held_direct, labels_direct)

    def test_a_plus_walk_on_one_step_pairs_is_refused(self):
        with self.assertRaises(ValueError):
            script.check_alignment("plus_direct_" + TARGET, {})
        with self.assertRaises(ValueError):
            script.check_alignment("base_direct", {"training_pairs": "other"})

    def test_an_aligned_walk_and_the_one_step_base_pass(self):
        script.check_alignment("plus_direct_" + TARGET, {"training_pairs": "direct"})
        script.check_alignment("base_direct", {"training_pairs": "direct"})
        script.check_alignment("base", {})

    def test_the_one_step_base_must_not_name_a_pairing(self):
        with self.assertRaises(ValueError):
            script.check_alignment("base", {"training_pairs": "direct"})


class TargetWalkPairingTests(unittest.TestCase):
    """The 15 target walks of #706 are read only if they were fitted on direct pairs.

    A walk file records its fit settings with `default=str`, so the Mac run's files hold them as the string
    `"{'training_pairs': 'direct'}"` (found by smoke-testing a full walk: a `.get` on the string raised `AttributeError`).
    """

    def test_a_target_walk_fitted_on_direct_pairs_passes_in_both_recorded_forms(self):
        script.check_target_walk({"settings": {"training_pairs": "direct"}})
        script.check_target_walk({"settings": "{'training_pairs': 'direct'}"})

    def test_a_target_walk_on_one_step_pairs_or_without_settings_is_refused(self):
        for document in ({"settings": {}}, {"settings": "{}"}, {}, {"settings": {"training_pairs": "one_step"}}):
            with self.subTest(document=document):
                with self.assertRaises(ValueError):
                    script.check_target_walk(document)


class VariantTests(unittest.TestCase):
    def test_a_variant_names_its_target_and_its_pairing(self):
        self.assertEqual(script.variant_parts("base"), (None, False))
        self.assertEqual(script.variant_parts("base_direct"), (None, True))
        self.assertEqual(script.variant_parts("plus_direct_on_rrp_change_bn"), ("on_rrp_change_bn", True))

    def test_an_undeclared_variant_is_refused(self):
        for name in ("plus_on_rrp_change_bn", "plus_direct_tgcr_dispersion_bps", "direct", "combined"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    script.variant_parts(name)


class LockedDayTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2026, 9, 4)])

    def test_a_development_day_passes(self):
        script.refuse_locked([date(2025, 12, 31)])


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.declared = json.loads(script.DECLARATION.read_text(encoding="utf-8"))

    def test_the_declaration_names_its_directive_and_the_842_it_re_runs(self):
        self.assertEqual(self.declared["issue"], 932)
        self.assertEqual(self.declared["re_runs"], "metadata/h9_nested_842.json")
        base = json.loads(script.m842.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(self.declared["targets"]["scratch_panel_sha256"], base["targets"]["scratch_panel_sha256"])
        # #706's declaration was amended for this directive (direct pairs for the target walks): the pin follows the file as it stands
        self.assertEqual(
            self.declared["targets"]["declaration_706_sha256"], hashlib.sha256(script.m706.DECLARATION.read_bytes()).hexdigest()
        )
        self.assertNotEqual(self.declared["targets"]["declaration_706_sha256"], base["targets"]["declaration_706_sha256"])
        self.assertEqual(json.loads(script.m706.DECLARATION.read_text(encoding="utf-8"))["model"]["training_pairs"], "direct")
        self.assertEqual(self.declared["published_panel_sha256"], base["published_panel_sha256"])

    def test_the_declared_variants_are_the_scripts(self):
        self.assertEqual(set(self.declared["variants"]) - {"count"}, set(script.VARIANTS))

    def test_the_primary_comparison_holds_the_pairing_fixed(self):
        primary = self.declared["comparisons"]["primary"]
        self.assertEqual(primary, [["base_direct", "plus_direct_" + t] for t in script.TARGETS])

    def test_an_uncommitted_declaration_is_refused(self):
        class Done:
            stdout = " M metadata/h9_nested_932.json\n"

        with mock.patch("subprocess.run", return_value=Done()):
            with self.assertRaises(SystemExit):
                script.committed_declaration()


if __name__ == "__main__":
    unittest.main()
