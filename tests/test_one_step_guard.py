"""`src/repo_model/one_step_guard.py`: a one-step fit refuses a calendar column or a scheduled field (#947).

Eleonora's ruling of 19 October 2026: `asof` rule 2 serves the calendar columns (`contract.CALENDAR_FEATURES`) and every
field in a source's `scheduled_availability` from the scored row. A fitter that trains on one-step pairs (row `p`
against the spread of `p + 1`) learns such a column one row off (finding #914). It raises `ValueError`. The only
exemptions are the frozen declarations in `ONE_STEP_ALLOW_LIST`; a test pins them. There is no switch.

Mutation record (#947)
----------------------

Run on CPython 3.11 (`/opt/rmm-venv`), `PYTHONDONTWRITEBYTECODE=1`, `-B`, in a disposable copy of the branch; each
mutation confirmed applied by diff and reverted; unmutated control green before and after.

1. **The calendar leg of the guard removed** -- in `one_step_refusals`, `if leaf in CALENDAR_FEATURES:` ->
   `if False:`. Killed by `test_a_calendar_column_is_refused`, `AssertionError: ValueError not raised`.
2. **The scheduled leg removed** -- in `one_step_refusals`, `if pairs:` -> `if False:`. Killed by
   `test_a_scheduled_field_is_refused`, `AssertionError: ValueError not raised`.
3. **The threshold variable left unchecked** -- in `baseline.fit_threshold`, `names + (selector_name,)` -> `names`.
   Killed by `test_a_calendar_threshold_variable_is_refused`, `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import one_step_guard
from repo_model.baseline import fit_arx, fit_threshold
from repo_model.data import DailyObservation

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

PUBLISHED_AT_H1 = (
    "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "tbill_13w", "tbill_4w", "tga", "treasury_settlement",
)


def frame(count=40):
    rows = []
    state = 20261019
    for index in range(count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        rows.append(
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {
                    "sofr": 4.30 + 0.0001 * (state % 9973),
                    "iorb": 4.30,
                    "sofr_volume": 2100.0 + (state % 1301) / 3.0,
                    "on_rrp": 90.0 + (state % 211) / 10.0,
                    "quarter_end": 1.0 if index % 13 == 12 else 0.0,
                    "treasury_settlement": float(state % 50),
                },
            )
        )
    return rows


class OneStepGuardTests(unittest.TestCase):
    def test_a_calendar_column_is_refused(self):
        with self.assertRaisesRegex(ValueError, r"quarter_end.*calendar.*direct.*drop"):
            fit_arx(frame(), ("on_rrp", "quarter_end"), minimum_history=20)

    def test_a_scheduled_field_is_refused(self):
        with self.assertRaisesRegex(ValueError, r"treasury_settlement.*treasury_auctions"):
            fit_arx(frame(), ("on_rrp", "treasury_settlement"), minimum_history=20)

    def test_a_calendar_threshold_variable_is_refused(self):
        with self.assertRaisesRegex(ValueError, "quarter_end"):
            fit_threshold(frame(), ("on_rrp",), "quarter_end", minimum_history=20)

    def test_a_calendar_threshold_regressor_is_refused(self):
        with self.assertRaisesRegex(ValueError, "quarter_end"):
            fit_threshold(frame(), ("quarter_end",), "on_rrp", minimum_history=20)

    def test_other_regressors_are_unchanged(self):
        model = fit_arx(frame(), ("on_rrp", "sofr_volume"), minimum_history=20)
        self.assertEqual(model.regressors, ("on_rrp", "sofr_volume"))

    def test_a_derived_feature_over_a_scheduled_field_is_refused(self):
        refused = one_step_guard.one_step_refusals(("settlement_day",))
        self.assertEqual(list(refused), ["settlement_day"])

    def test_no_refusal_for_plain_fields(self):
        self.assertEqual(one_step_guard.one_step_refusals(PUBLISHED_AT_H1[:-1]), {})


class AllowListTests(unittest.TestCase):
    def test_the_allow_list_is_exactly_these_declarations(self):
        entries = one_step_guard.ONE_STEP_ALLOW_LIST
        self.assertEqual(set(entries), {"published_distribution_crps", "gbm_funding_634"})
        for entry in entries.values():
            self.assertEqual(entry.fitter, "fit_gradient_boosted_quantiles")
            self.assertEqual(entry.regressors, PUBLISHED_AT_H1)
            self.assertTrue(entry.reason)

    def test_the_published_entry_is_the_frozen_command_less_the_target(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "final_test_preregistration.py"
        spec = importlib.util.spec_from_file_location("final_test_preregistration", script)
        fp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fp)

        self.assertEqual(
            tuple(name for name in fp.CRPS_FEATURES if name != "spread_bps"), PUBLISHED_AT_H1
        )

    def test_an_exempt_declaration_passes_and_another_fitter_does_not(self):
        one_step_guard.check_one_step_regressors("fit_gradient_boosted_quantiles", PUBLISHED_AT_H1)
        with self.assertRaises(ValueError):
            one_step_guard.check_one_step_regressors("fit_arx", PUBLISHED_AT_H1)

    def test_a_changed_regressor_set_is_not_exempt(self):
        with self.assertRaises(ValueError):
            one_step_guard.check_one_step_regressors(
                "fit_gradient_boosted_quantiles", PUBLISHED_AT_H1 + ("quarter_end",)
            )
        with self.assertRaises(ValueError):
            one_step_guard.check_one_step_regressors(
                "fit_gradient_boosted_quantiles", tuple(reversed(PUBLISHED_AT_H1))
            )


if __name__ == "__main__":
    unittest.main()
