"""At-risk days by scarcity state and coupon settlement (#218): `scripts/at_risk_by_state.py`.

Descriptive only: these tests check that the table counts the days and onsets
it says it counts, reads them as #214's post-mortem reads them, and refuses a
locked day. They do not test a claim, because it makes none.

Recorded mutation (CLAUDE.md, a leakage guard's call site): deleting the line
`require_unlocked(scored_dates, where="at_risk_by_state.at_risk_days")` in
`at_risk_days` makes
`AtRiskByStateTests.test_at_risk_days_refuses_a_locked_scored_day` fail with
`AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from repo_model import onset
from repo_model.data import exceeds_bp
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
END = date(2025, 12, 31)
LOCKED = date(2026, 1, 5)


def _script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AtRiskByStateTests(unittest.TestCase):
    """On the measurement panel built from tracked fixtures, as #214's post-mortem builds it."""

    @classmethod
    def setUpClass(cls):
        from repo_model.scarcity import measurement_declaration, with_reserve_scarcity_state

        cls.table = _script("at_risk_by_state")
        cls.pm = cls.table.pm
        validation = _script("scarcity_validation")
        cls.declaration = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
        with measurement_declaration(), tempfile.TemporaryDirectory() as directory:
            build, _digest, cls.registry, cls.decision = validation.build_measurement_panel(
                ROOT / "metadata" / "sources.json", Path(directory)
            )
            cls.rows = with_reserve_scarcity_state(build.observations)
            cls.reads = cls.pm.as_of_reads(
                cls.rows,
                cls.registry,
                decision_time=cls.decision,
                minimum_history=cls.pm.gauge_history(cls.rows, cls.registry, decision_time=cls.decision),
                end=END,
            )
            cls.scored = sorted(
                cls.pm.as_of_reads(
                    cls.rows,
                    cls.registry,
                    decision_time=cls.decision,
                    minimum_history=cls.pm.MINIMUM_HISTORY,
                    end=END,
                )
            )

    def _forecasts(self, v1=0.25, persistence=0.5):
        """Constant forecasts on the scored grid, in the post-mortem's cache shape."""

        n = len(self.scored)
        return {
            "scored_dates": [d.isoformat() for d in self.scored],
            self.pm.V1: {"5": [v1] * n},
            self.pm.PERSISTENCE: {"5": [persistence] * n},
        }

    # -- the lockbox ---------------------------------------------------------

    def test_main_refuses_an_end_in_the_locked_tier_before_anything_is_built(self):
        with mock.patch.object(self.pm, "load", side_effect=AssertionError("built")):
            with self.assertRaisesRegex(LookAheadError, r"^at_risk_by_state: scored day 2026-01-05"):
                self.table.main(["--end", LOCKED.isoformat()])

    def test_at_risk_days_refuses_a_locked_scored_day(self):
        locked = [row.date for row in self.rows if END < row.date <= LOCKED]
        self.assertTrue(locked)
        with self.assertRaises(LookAheadError):
            self.table.at_risk_days(self.rows, self.scored + locked, self.declaration)

    def test_no_day_is_locked(self):
        days, onsets = self.table.at_risk_days(self.rows, self.scored, self.declaration)
        self.assertLessEqual(max(days), END)
        self.assertLessEqual(max(onsets), END)

    # -- the days ------------------------------------------------------------

    def test_the_at_risk_days_are_day_groups_onset_group(self):
        days, _onsets = self.table.at_risk_days(self.rows, self.scored, self.declaration)
        groups = onset.day_groups(self.rows, self.scored, self.declaration)
        self.assertEqual(days, [self.scored[k] for k in groups[onset.GROUP_ONSET]])
        self.assertTrue(days)

    def test_the_onsets_are_the_at_risk_days_above_five_bp_and_the_post_mortems(self):
        days, onsets = self.table.at_risk_days(self.rows, self.scored, self.declaration)
        position = {row.date: index for index, row in enumerate(self.rows)}
        self.assertEqual(
            onsets,
            [d for d in days if exceeds_bp(self.rows[position[d]].spread_bps, onset.ONSET_THRESHOLD_BP)],
        )
        self.assertEqual(onsets, self.pm.onset_days(self.rows, self.scored, self.declaration)[self.pm.PRIMARY])
        flags = onset.onset_flags(self.rows)
        scored = set(self.scored)
        self.assertEqual(onsets, [row.date for row, flag in zip(self.rows, flags) if flag and row.date in scored])

    # -- the reads -----------------------------------------------------------

    def test_a_day_is_placed_by_its_as_of_state_and_its_coupon_settlement(self):
        days, _onsets = self.table.at_risk_days(self.rows, self.scored, self.declaration)
        for day in days[::17]:
            read = self.reads[day]
            state, coupon = self.table.cell_of(read)
            with self.subTest(day=day):
                self.assertEqual(state, read["state"])
                self.assertLess(read["state_read_date"], day)
                coupons = read[self.pm.COUPONS]
                self.assertEqual(coupon, coupons is not None and float(coupons) > 0.0)

    def test_the_cells_add_up_to_every_at_risk_day_and_onset(self):
        days, onsets = self.table.at_risk_days(self.rows, self.scored, self.declaration)
        document = self.table.tabulate(days, onsets, self.reads, self._forecasts())
        cells = [cell for row in document["cells"].values() for cell in row.values()]
        self.assertEqual(sum(cell["days"] for cell in cells), len(days))
        self.assertEqual(sum(cell["onsets"] for cell in cells), len(onsets))
        self.assertEqual(document["total"]["days"], len(days))
        self.assertEqual(document["total"]["onsets"], len(onsets))
        self.assertEqual(document["total"]["v1_mean"], 0.25)
        self.assertEqual(document["total"]["persistence_logistic_mean"], 0.5)

    # -- the table -----------------------------------------------------------

    def test_each_cell_counts_rates_and_averages_its_own_days(self):
        days = [date(2025, 1, d) for d in range(2, 8)]
        states = [0, 2, 2, 3, 3, 3]
        coupons = [0.0, 5.0, 0.0, 5.0, 5.0, None]
        reads = {
            d: {"state": s, self.pm.COUPONS: c} for d, s, c in zip(days, states, coupons)
        }
        forecasts = {
            "scored_dates": [d.isoformat() for d in days],
            self.pm.V1: {"5": [0.1, 0.2, 0.3, 0.4, 0.6, 0.8]},
            self.pm.PERSISTENCE: {"5": [0.0, 0.1, 0.1, 0.2, 0.4, 0.5]},
        }
        onsets = [days[1], days[3]]
        document = self.table.tabulate(days, onsets, reads, forecasts)
        cells = document["cells"]
        self.assertEqual(cells[3][True], {
            "days": 2, "onsets": 1, "rate": 0.5,
            "v1_mean": (0.4 + 0.6) / 2, "persistence_logistic_mean": (0.2 + 0.4) / 2,
        })
        self.assertEqual(cells[2][True]["onsets"], 1)
        self.assertEqual(cells[2][True]["rate"], 1.0)
        self.assertEqual(cells[3][False]["days"], 1)
        self.assertEqual(cells[1][True], {
            "days": 0, "onsets": 0, "rate": None, "v1_mean": None, "persistence_logistic_mean": None,
        })
        self.assertEqual(document["row_totals"][3]["days"], 3)
        self.assertEqual(document["row_totals"][3]["onsets"], 1)
        self.assertAlmostEqual(document["row_totals"][3]["v1_mean"], (0.4 + 0.6 + 0.8) / 3)
        self.assertEqual(document["column_totals"][True]["days"], 3)
        self.assertEqual(document["column_totals"][True]["onsets"], 2)
        self.assertEqual(document["column_totals"][False]["days"], 3)
        self.assertEqual(document["total"]["days"], 6)
        self.assertEqual(document["total"]["onsets"], 2)
        self.assertEqual(sorted(document["cells"]), [0, 1, 2, 3])

    def test_a_day_with_no_state_gets_its_own_row(self):
        days = [date(2025, 1, 2), date(2025, 1, 3)]
        reads = {
            days[0]: {"state": None, self.pm.COUPONS: 0.0},
            days[1]: {"state": 1, self.pm.COUPONS: 0.0},
        }
        forecasts = {
            "scored_dates": [d.isoformat() for d in days],
            self.pm.V1: {"5": [0.1, 0.2]},
            self.pm.PERSISTENCE: {"5": [0.1, 0.2]},
        }
        document = self.table.tabulate(days, [], reads, forecasts)
        self.assertEqual(document["cells"][None][False]["days"], 1)
        self.assertEqual(document["total"]["days"], 2)

    def test_an_empty_cell_is_shown_empty_not_as_zero(self):
        days = [date(2025, 1, 2)]
        reads = {days[0]: {"state": 2, self.pm.COUPONS: 5.0}}
        forecasts = {
            "scored_dates": [days[0].isoformat()],
            self.pm.V1: {"5": [0.125]},
            self.pm.PERSISTENCE: {"5": [0.25]},
        }
        text = self.table.markdown(self.table.tabulate(days, [days[0]], reads, forecasts))
        state_zero = [line for line in text.splitlines() if line.startswith("| 0 ")]
        self.assertEqual(len(state_zero), 1)
        self.assertNotRegex(state_zero[0], r"\d+ of \d+")
        self.assertNotIn("0.000", state_zero[0])
        state_two = [line for line in text.splitlines() if line.startswith("| 2 ")][0]
        self.assertIn("1 of 1 (1.00)", state_two)
        self.assertIn("0.125", state_two)
        self.assertIn("0.250", state_two)

    # -- the forecast check --------------------------------------------------

    def test_main_stops_when_the_forecasts_do_not_reproduce_the_record(self):
        fake = {
            "model_name": self.pm.V1,
            "scored_dates": [d.isoformat() for d in self.scored],
            "outcomes": {"5": [0] * len(self.scored)},
            "taus": [5.0, 10.0, 20.0, 50.0],
        }
        for name in (self.pm.V1, self.pm.PERSISTENCE):
            fake[name] = {key: [0.0] * len(self.scored) for key in ("5", "10", "20", "50")}
        with mock.patch.object(self.pm, "v1_and_persistence", return_value=fake):
            with self.assertRaisesRegex(ValueError, "differ from the record"):
                self.table.main(["--end", END.isoformat()])


if __name__ == "__main__":
    unittest.main()
