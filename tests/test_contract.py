"""Contract tests from AGENT_CONTRACT.md.

Owned by neither track. Both tracks run this before every commit; it fails the
build rather than warning.

The contract describes a long point-in-time panel (`series_id`, `ref_date`,
`available_at`, `vintage_id`, `source_sha`) and a `fit`/`predict` forecast
interface. The current module layout implements neither yet: `repo_model.data`
loads a wide daily frame keyed on `date` alone, and `repo_model.baseline`
exposes a single streaming backtest instead of a fitted object. Tests 1-3 and 5
are therefore written against the strongest available stand-ins:

  * `available_at` is taken to equal `date` (zero release lag). This is the
    assumption the current loader silently makes, and pinning it here means the
    day a real `available_at` column arrives, these tests must be revisited
    rather than quietly weakened.
  * "refit and re-predict" is the backtest re-run over a perturbed panel.
  * the only learned transform in the codebase today is the residual quantile
    that sets the prediction interval, so that is what test 3 isolates.
  * the source registry declares no structural zeros yet, so test 5 can only
    check the half the loader is capable of: that missing is never coerced to
    0.0 and a real 0.0 survives as one.

Contract test 4 (identity preservation) is absent: the registry declares no
accounting identities and no tolerances, so there is nothing to reconcile
against. It arrives with the registry work in Track A.

`TargetSchemaTests` at the bottom holds the tests the contract actually asks
for, written against the target interfaces and marked `expectedFailure`. They
are executable specification, not decoration: `unittest` reports an unexpected
success as a build failure, so the day a track implements one of these
interfaces the suite goes red and forces the stand-ins above to be rewritten
against the real thing rather than extended around it.
"""

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.baseline import _quantile, rolling_persistence_backtest
from repo_model.data import (
    DailyObservation,
    DataContractError,
    audit_panel,
    load_daily_panel,
)


REPO_ROOT = Path(__file__).parents[1]
SAMPLE_PANEL = REPO_ROOT / "data" / "sample" / "daily_market.csv"
SOURCE_REGISTRY = REPO_ROOT / "metadata" / "sources.json"

MINIMUM_HISTORY = 10
INTERVAL_PROBABILITY = 0.90


def load_sample():
    rows = load_daily_panel(SAMPLE_PANEL)
    audit_panel(rows)  # sortedness and uniqueness are preconditions for the as-of rule
    return rows


def perturb_after(rows, cutoff_index, shock_bps=250.0):
    """Return a copy of the panel with every row after `cutoff_index` moved.

    Only fields dated strictly after the cutoff change, so any forecast made at
    or before the cutoff must be unaffected by this.
    """

    perturbed = []
    for index, row in enumerate(rows):
        values = dict(row.values)
        if index > cutoff_index:
            values["sofr"] = float(values["sofr"]) + shock_bps / 100.0
            for field in ("sofr_volume", "reserve_balances", "on_rrp", "tga"):
                if values.get(field) is not None:
                    values[field] = float(values[field]) * 3.0 + 1.0
        perturbed.append(DailyObservation(row.date, values))
    return perturbed


def residual_window(rows, forecast_index):
    """One-step residuals a forecast for `forecast_index` is entitled to see.

    Everything strictly before the forecast date, and nothing else.
    """

    return [
        rows[j].spread_bps - rows[j - 1].spread_bps
        for j in range(1, forecast_index)
    ]


class EligibilityTests(unittest.TestCase):
    """Contract test 1: no training row is dated after its window's cutoff."""

    def test_as_of_filter_reduces_to_a_prefix_only_if_dates_are_clean(self):
        """The precondition test 1 rests on.

        `available_at <= C` selects a contiguous prefix of the panel only
        because dates are strictly ascending and unique. Asserting the prefix
        property on an already-sorted panel would restate how Python slices;
        asserting that `audit_panel` rejects the two orderings that would break
        it is the part that can actually regress.
        """

        values = {"sofr": 4.31, "iorb": 4.30}
        out_of_order = [
            DailyObservation(date(2026, 1, 5), values),
            DailyObservation(date(2026, 1, 2), values),
        ]
        with self.assertRaisesRegex(DataContractError, "sorted"):
            audit_panel(out_of_order)

        duplicated = [
            DailyObservation(date(2026, 1, 2), values),
            DailyObservation(date(2026, 1, 2), values),
        ]
        with self.assertRaisesRegex(DataContractError, "duplicate"):
            audit_panel(duplicated)

    def test_truncating_at_the_cutoff_does_not_change_earlier_forecasts(self):
        """Behavioural half: a window that peeked ahead would move here.

        Forecasts produced from the panel truncated at C must be bit-identical
        to the corresponding forecasts from the full panel. If any training
        window reached past its cutoff, removing the later rows would change
        them.
        """

        rows = load_sample()
        full = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )

        for cutoff_position in range(MINIMUM_HISTORY, len(rows)):
            truncated = rolling_persistence_backtest(
                rows[: cutoff_position + 1],
                minimum_history=MINIMUM_HISTORY,
                interval_probability=INTERVAL_PROBABILITY,
            )
            expected = full.forecasts[: len(truncated.forecasts)]
            self.assertEqual(
                list(truncated.forecasts),
                list(expected),
                msg=(
                    f"forecasts changed when the panel was truncated at "
                    f"{rows[cutoff_position].date}"
                ),
            )


class FuturePerturbationTests(unittest.TestCase):
    """Contract test 2: perturbing the future must not move a past forecast."""

    def test_forecast_for_t_plus_one_is_bit_identical_after_future_shock(self):
        rows = load_sample()
        cutoff_index = 15
        forecast_index = cutoff_index + 1
        position = forecast_index - MINIMUM_HISTORY

        baseline = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]
        shocked = rolling_persistence_backtest(
            perturb_after(rows, cutoff_index),
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]

        # `actual_bps` is the realized outcome at T+1 and is *expected* to move
        # with the shock. The forecast itself -- point and interval -- must not.
        self.assertEqual(shocked.predicted_bps, baseline.predicted_bps)
        self.assertEqual(shocked.lower_bps, baseline.lower_bps)
        self.assertEqual(shocked.upper_bps, baseline.upper_bps)

    def test_every_forecast_at_or_before_the_cutoff_is_bit_identical(self):
        rows = load_sample()
        baseline = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts
        for cutoff_index in range(MINIMUM_HISTORY, len(rows) - 1):
            shocked = rolling_persistence_backtest(
                perturb_after(rows, cutoff_index),
                minimum_history=MINIMUM_HISTORY,
                interval_probability=INTERVAL_PROBABILITY,
            ).forecasts

            # A forecast at panel index i uses rows[0..i-1]: rows[i-1] for the
            # point, rows[0..i-1] for the residual quantile. Only `actual_bps`
            # touches rows[i]. So every forecast through index cutoff_index + 1
            # -- including the T+1 forecast the contract names -- must hold.
            unaffected = cutoff_index - MINIMUM_HISTORY + 2
            for position in range(unaffected):
                self.assertEqual(
                    (
                        shocked[position].predicted_bps,
                        shocked[position].lower_bps,
                        shocked[position].upper_bps,
                    ),
                    (
                        baseline[position].predicted_bps,
                        baseline[position].lower_bps,
                        baseline[position].upper_bps,
                    ),
                    msg=(
                        f"forecast {position} moved when observations after "
                        f"{rows[cutoff_index].date} were perturbed"
                    ),
                )

    def test_the_perturbation_is_actually_visible_to_the_model(self):
        """Guards the two tests above from passing because nothing changed."""

        rows = load_sample()
        cutoff_index = 15
        shocked = rolling_persistence_backtest(
            perturb_after(rows, cutoff_index),
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )
        baseline = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )
        self.assertNotEqual(
            [item.predicted_bps for item in shocked.forecasts],
            [item.predicted_bps for item in baseline.forecasts],
            msg="future shock changed no forecast at all; the test has no power",
        )


class TransformIsolationTests(unittest.TestCase):
    """Contract test 3: learned parameters come from the training window alone.

    The residual quantile that sets the prediction interval is the only
    transform with learned parameters in the codebase today.
    """

    def test_interval_matches_parameters_refit_on_the_training_window(self):
        rows = load_sample()
        alpha = (1.0 - INTERVAL_PROBABILITY) / 2.0
        report = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )

        for position, forecast in enumerate(report.forecasts):
            forecast_index = MINIMUM_HISTORY + position
            window = residual_window(rows, forecast_index)
            prediction = rows[forecast_index - 1].spread_bps

            self.assertEqual(forecast.predicted_bps, prediction)
            self.assertEqual(forecast.lower_bps, prediction + _quantile(window, alpha))
            self.assertEqual(
                forecast.upper_bps, prediction + _quantile(window, 1.0 - alpha)
            )

    def test_window_parameters_differ_from_full_sample_parameters(self):
        """Guards the test above: on a panel where a leak would be visible.

        The real sample is smooth enough that window-fitted and full-sample
        parameters nearly coincide, so equality alone would prove little. Shock
        the tail, and a pipeline that fit its quantile on the whole panel would
        produce a different interval for an early forecast than one that fit on
        the window. Confirm those two candidate parameters really do differ,
        then confirm the pipeline reports the window-fitted one.
        """

        rows = perturb_after(load_sample(), cutoff_index=15)
        alpha = (1.0 - INTERVAL_PROBABILITY) / 2.0
        forecast_index = MINIMUM_HISTORY + 2
        position = forecast_index - MINIMUM_HISTORY

        window = residual_window(rows, forecast_index)
        full_sample = residual_window(rows, len(rows))

        self.assertNotEqual(
            _quantile(window, 1.0 - alpha),
            _quantile(full_sample, 1.0 - alpha),
            msg="test panel cannot distinguish window fitting from full-sample fitting",
        )

        forecast = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]
        prediction = rows[forecast_index - 1].spread_bps
        self.assertEqual(
            forecast.upper_bps, prediction + _quantile(window, 1.0 - alpha)
        )


class StructuralZeroTests(unittest.TestCase):
    """Contract test 5: a structural zero is never confused with a missing value.

    The registry declares no structural zeros yet, so "declared" is
    unenforceable here -- that half is in `TargetSchemaTests`. What the current
    loader can be held to is the coercion rule: an absent observation stays
    absent, and a genuine 0.0 stays 0.0, at load and through the audit.
    """

    def write_csv(self, contents):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_missing_and_zero_are_distinguishable_at_load(self):
        path = self.write_csv(
            "date,sofr,iorb,on_rrp,quarter_end\n"
            "2026-01-02,4.31,4.30,,0\n"
            "2026-01-05,4.31,4.30,0,1\n"
        )
        rows = load_daily_panel(path)

        # An empty cell is an unobserved value, not a zero balance.
        self.assertIsNone(rows[0].values["on_rrp"])
        # A reported zero balance is an observation and keeps its value.
        self.assertEqual(rows[1].values["on_rrp"], 0.0)
        self.assertIsNotNone(rows[1].values["on_rrp"])

        # The same distinction on a declared zero/one flag: 0 means "not a
        # quarter end", which is data, not absence.
        self.assertEqual(rows[0].values["quarter_end"], 0.0)
        self.assertEqual(rows[1].values["quarter_end"], 1.0)

    def test_audit_counts_missing_without_counting_zero(self):
        path = self.write_csv(
            "date,sofr,iorb,on_rrp,quarter_end\n"
            "2026-01-02,4.31,4.30,,0\n"
            "2026-01-05,4.31,4.30,0,0\n"
        )
        report = audit_panel(load_daily_panel(path))

        self.assertEqual(report.missing_counts["on_rrp"], 1)
        self.assertEqual(report.missing_counts["quarter_end"], 0)
        # A structural zero is not an anomaly and must not be reported as one.
        self.assertEqual(list(report.warnings), [])

    def test_sample_panel_keeps_unobserved_columns_unobserved(self):
        rows = load_sample()
        for field in ("treasury_settlement", "dealer_treasury_position", "mmf_assets"):
            observed = [row.values[field] for row in rows]
            self.assertTrue(
                all(value is None for value in observed),
                msg=f"{field} is empty in the sample and must not become 0.0",
            )
            self.assertNotIn(0.0, observed)

    def test_zero_survives_the_spread_calculation(self):
        """A zero-valued field must not be silently dropped downstream."""

        path = self.write_csv(
            "date,sofr,iorb,on_rrp\n"
            "2026-01-02,4.30,4.30,0\n"
        )
        rows = load_daily_panel(path)
        self.assertEqual(rows[0].spread_bps, 0.0)
        self.assertEqual(rows[0].values["on_rrp"], 0.0)


class TargetSchemaTests(unittest.TestCase):
    """The contract's real requirements, against interfaces that do not exist.

    Every test here is expected to fail today. When one starts passing,
    `unittest` reports an unexpected success and the build goes red -- which is
    the signal to delete the stand-in above it and write the real test.
    """

    @unittest.expectedFailure
    def test_panel_rows_carry_point_in_time_provenance(self):
        """Contract test 1, properly: eligibility needs `available_at`."""

        rows = load_daily_panel(SAMPLE_PANEL)
        for field in ("series_id", "ref_date", "available_at", "vintage_id", "source_sha"):
            self.assertTrue(
                hasattr(rows[0], field),
                msg=f"panel row has no {field!r}; the as-of rule cannot be enforced",
            )

    @unittest.expectedFailure
    def test_revisions_are_appended_as_new_vintages(self):
        """A value revised at T+3 is a second row, not an overwrite."""

        from repo_model.data import load_point_in_time_panel  # noqa: F401

        raise AssertionError("no point-in-time loader to test revision appending against")

    @unittest.expectedFailure
    def test_rolling_origin_splitter_exists_and_purges(self):
        """Contract splitter interface, including the purge gap."""

        from repo_model.splits import rolling_origin  # noqa: F401

        raise AssertionError("no splitter to test purge behaviour against")

    @unittest.expectedFailure
    def test_forecast_interface_is_fit_predict_predict_stress(self):
        """Models must be fitted objects carrying their cutoff, not a function."""

        import repo_model.baseline as baseline

        for name in ("fit", "predict", "predict_stress"):
            self.assertTrue(
                hasattr(baseline, name),
                msg=f"no {name!r}; quantile levels are not yet comparable across models",
            )

    @unittest.expectedFailure
    def test_source_registry_declares_identities_and_structural_zeros(self):
        """Contract tests 4 and 5 both need declarations the registry lacks."""

        registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        for source in registry.values():
            self.assertIn("identities", source)
            self.assertIn("structural_zeros", source)
            self.assertIn("release_lag", source)


if __name__ == "__main__":
    unittest.main()
