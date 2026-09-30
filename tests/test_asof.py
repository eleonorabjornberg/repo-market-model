"""The as-of information set: `docs/decisions/information-set.md`, implemented.

Most of these tests read the tracked registry, `metadata/sources.json`, rather
than a synthetic one, so what they pin is what the published runs will read.
A synthetic declaration appears only where a test is about the mechanism
rather than about a source.
"""

from __future__ import annotations

import copy
import json
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model.asof import (
    FieldRead,
    InformationRule,
    InformationSet,
    StaleReadError,
    fold_grid,
    refit_blocks,
    validate_scheduled_availability,
)
from repo_model.data import DailyObservation
from repo_model.registry import RegistryContractError
from repo_model.splits import LookAheadError, SplitError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())
DECISION = time(16, 0)
#: The published panel's first date (`metadata/funding_panel_manifest.json`).
PANEL_FIRST_DATE = date(2018, 4, 3)
SETTLEMENT_SNAPSHOT = (
    ROOT
    / "tests/fixtures/snapshots/funding_inputs/treasury_auctions"
    / "20260914T051023Z_722359ea9bc7.json"
)


def weekdays(start, count, skip=()):
    """`count` weekdays from `start`, leaving out the dates in `skip`."""

    out = []
    when = start
    while len(out) < count:
        if when.weekday() < 5 and when not in skip:
            out.append(when)
        when += timedelta(days=1)
    return out


def panel(dates):
    """Rows whose every value encodes its own position, so a read is legible.

    `sofr` is `2 + i/100` and `iorb` is `2`, so `spread_bps` on row `i` is `i`.
    Every other column is `1000 * column_number + i`.
    """

    columns = (
        "sofr_volume",
        "sofr_p25",
        "sofr_p75",
        "reserve_balances",
        "tga",
        "tbill_4w",
        "treasury_settlement_bills",
        "treasury_settlement_coupons",
        "treasury_settlement_soma",
        "treasury_settlement",
        "days_to_month_end",
        "quarter_end",
        "tax_date",
    )
    rows = []
    for index, when in enumerate(dates):
        values = {"sofr": 2.0 + index / 100.0, "iorb": 2.0}
        for number, name in enumerate(columns, start=1):
            values[name] = float(1000 * number + index)
        rows.append(DailyObservation(when, values))
    return rows


# Mon 2026-01-05 onward; MLK Monday 2026-01-19 is not a panel date.
DATES = weekdays(date(2026, 1, 5), 40, skip={date(2026, 1, 19)})
ROWS = panel(DATES)


def index_of(when):
    return DATES.index(when)


def rule(features, registry=REGISTRY):
    return InformationRule(registry, tuple(features), decision_time=DECISION)


def read_of(info, feature):
    (found,) = [read for read in info.reads if read.feature == feature]
    return found


class DecisionInstantTests(unittest.TestCase):
    def test_the_decision_is_at_the_declared_time_on_the_panel_day_before(self):
        scored = index_of(date(2026, 1, 20))  # the Tuesday after MLK
        info = rule(["spread_bps"]).information_set(DATES, scored)
        self.assertEqual(info.decision_instant, datetime(2026, 1, 16, 16, 0))

    def test_the_first_row_has_no_decision_instant(self):
        with self.assertRaises(SplitError):
            rule(["spread_bps"]).information_set(DATES, 0)


class TargetAnchorTests(unittest.TestCase):
    """Label observability: the target is `sofr - iorb`, read at one row."""

    def test_iorb_declared_at_1615_holds_the_target_back_a_row_mid_week(self):
        # Scored Thursday 2026-01-08, decision Wednesday 16:00. SOFR for
        # Tuesday is final Wednesday 15:00, but IORB for Tuesday is declared
        # observable Wednesday 16:15 -- fifteen minutes late -- so the latest
        # row whose whole target is observable is Monday.
        scored = index_of(date(2026, 1, 8))
        anchor = rule(["spread_bps"]).anchor(DATES, scored)
        self.assertEqual(DATES[anchor], date(2026, 1, 5))

    def test_after_a_weekend_the_target_is_two_rows_back(self):
        # Scored Tuesday 2026-01-13, decision Monday 16:00: Friday's IORB was
        # observable Saturday 16:15 and Friday's SOFR Monday 15:00.
        scored = index_of(date(2026, 1, 13))
        anchor = rule(["spread_bps"]).anchor(DATES, scored)
        self.assertEqual(DATES[anchor], date(2026, 1, 9))

    def test_with_iorb_known_the_same_day_the_target_is_two_rows_back_always(self):
        registry = copy.deepcopy(REGISTRY)
        for name in ("IORB", "IOER"):
            registry["fred_macro_latest_vintage"]["field_release_lags"][name]["days"] = 0
        current = rule(["spread_bps"], registry)
        for scored in range(3, len(DATES)):
            self.assertEqual(current.anchor(DATES, scored), scored - 2, DATES[scored])

    def test_the_anchor_does_not_depend_on_the_declared_features(self):
        bare = rule(["spread_bps"])
        wide = rule(["spread_bps", "reserve_balances", "tbill_4w", "days_to_month_end"])
        for scored in range(1, len(DATES)):
            self.assertEqual(bare.anchor(DATES, scored), wide.anchor(DATES, scored))


class PerFieldReadTests(unittest.TestCase):
    FEATURES = (
        "spread_bps",
        "sofr_volume",
        "tbill_4w",
        "reserve_balances",
        "days_to_month_end",
        "treasury_settlement_bills",
    )

    def setUp(self):
        self.scored = index_of(date(2026, 1, 22))  # Thursday; decision Wed 21st
        self.info = rule(self.FEATURES).information_set(DATES, self.scored)

    def test_a_sofr_field_is_read_two_rows_back(self):
        read = read_of(self.info, "sofr_volume")
        self.assertEqual(read.row, self.scored - 2)
        self.assertEqual(read.available_at, datetime(2026, 1, 21, 15, 0))

    def test_a_bill_rate_is_read_two_rows_back(self):
        # Observable 16:30 on its own date, so Wednesday's is not, Tuesday's is.
        read = read_of(self.info, "tbill_4w")
        self.assertEqual(DATES[read.row], date(2026, 1, 20))

    def test_a_weekly_field_is_read_at_its_latest_declared_print(self):
        # record_date + 5 calendar days at 16:30, against Wed 21st 16:00: the
        # latest row dated on or before Thu 15th qualifies.
        read = read_of(self.info, "reserve_balances")
        self.assertEqual(DATES[read.row], date(2026, 1, 15))

    def test_a_calendar_field_is_read_at_the_scored_day(self):
        read = read_of(self.info, "days_to_month_end")
        self.assertEqual(read.row, self.scored)
        self.assertEqual(read.kind, "calendar")
        self.assertIsNone(read.available_at)

    def test_a_settlement_is_scheduled_under_the_auction_results_declaration(self):
        read = read_of(self.info, "treasury_settlement_bills")
        self.assertEqual(read.kind, "scheduled")
        self.assertEqual(read.row, self.scored)
        # One panel day before the settlement, at the declared results time.
        self.assertEqual(read.available_at, datetime(2026, 1, 21, 15, 0))

    def test_without_the_scheduled_declaration_a_settlement_is_an_ordinary_read(self):
        registry = copy.deepcopy(REGISTRY)
        del registry["treasury_auctions"]["scheduled_availability"]
        info = rule(self.FEATURES, registry).information_set(DATES, self.scored)
        read = read_of(info, "treasury_settlement_bills")
        self.assertEqual(read.kind, "observed")
        # record_date + 0 at 23:59: Tuesday's is the latest before Wed 16:00.
        self.assertEqual(DATES[read.row], date(2026, 1, 20))

    def test_staleness_is_reported_in_rows_and_hours(self):
        read = read_of(self.info, "sofr_volume")
        self.assertEqual(read.rows, 2)
        self.assertEqual(read.hours, 1.0)  # final at 15:00, read at 16:00

    def test_the_target_is_read_at_the_anchor(self):
        read = read_of(self.info, "spread_bps")
        self.assertEqual(read.row, self.info.anchor)


class ObservationTests(unittest.TestCase):
    FEATURES = PerFieldReadTests.FEATURES

    def test_the_observation_carries_each_field_from_its_own_row(self):
        scored = index_of(date(2026, 1, 22))
        current = rule(self.FEATURES)
        info = current.information_set(DATES, scored)
        observed = current.observation(ROWS, info)
        self.assertEqual(observed.date, DATES[info.anchor])
        self.assertAlmostEqual(observed.spread_bps, float(info.anchor))
        for feature in ("sofr_volume", "tbill_4w", "reserve_balances",
                        "days_to_month_end", "treasury_settlement_bills"):
            row = read_of(info, feature).row
            self.assertEqual(observed.values[feature], ROWS[row].values[feature], feature)

    def test_an_undeclared_column_is_the_anchor_rows_and_is_guarded_elsewhere(self):
        """An undeclared column is left as the anchor row carries it.

        No model reads it and passes: the fold loops refuse any model whose
        `features_read` leaves the declaration
        (`baseline._check_fitter_stayed_inside`), so the value is never used.
        """

        scored = index_of(date(2026, 1, 22))
        current = rule(["spread_bps"])
        info = current.information_set(DATES, scored)
        observed = current.observation(ROWS, info)
        self.assertEqual(observed.values["tga"], ROWS[info.anchor].values["tga"])


class FrameTests(unittest.TestCase):
    def test_the_frame_ends_at_the_anchor(self):
        scored = index_of(date(2026, 1, 22))
        current = rule(["spread_bps"])
        info = current.information_set(DATES, scored)
        frame = current.frame(ROWS, info)
        self.assertEqual(frame[-1].date, DATES[info.anchor])
        self.assertEqual(len(frame), info.anchor + 1)

    def test_a_value_not_yet_observable_is_a_hole_in_the_frame(self):
        scored = index_of(date(2026, 1, 22))
        current = rule(["spread_bps", "reserve_balances"])
        info = current.information_set(DATES, scored)
        frame = current.frame(ROWS, info)
        weekly = read_of(info, "reserve_balances").row
        for position, row in enumerate(frame):
            expected = None if position > weekly else ROWS[position].values["reserve_balances"]
            self.assertEqual(row.values["reserve_balances"], expected, row.date)
            self.assertEqual(row.spread_bps, ROWS[position].spread_bps)


class GridTests(unittest.TestCase):
    def test_one_grid_whatever_the_declaration(self):
        registry = copy.deepcopy(REGISTRY)
        self.assertEqual(
            fold_grid(DATES, registry, decision_time=DECISION, minimum_history=5),
            fold_grid(DATES, registry, decision_time=DECISION, minimum_history=5),
        )
        first = fold_grid(DATES, registry, decision_time=DECISION, minimum_history=5)[0]
        self.assertEqual(rule(["spread_bps"]).anchor(DATES, first) + 1, 5)
        self.assertLess(rule(["spread_bps"]).anchor(DATES, first - 1) + 1, 5)

    def test_the_grid_runs_to_the_last_row(self):
        grid = fold_grid(DATES, REGISTRY, decision_time=DECISION, minimum_history=5)
        self.assertEqual(grid, tuple(range(grid[0], len(DATES))))

    def test_too_little_history_is_refused(self):
        with self.assertRaises(SplitError):
            fold_grid(DATES, REGISTRY, decision_time=DECISION, minimum_history=len(DATES))

    def test_refit_blocks_tile_the_grid(self):
        grid = tuple(range(10, 33))
        blocks = refit_blocks(grid, 7)
        self.assertEqual([block[0] for block in blocks], [10, 17, 24, 31])
        self.assertEqual(sum(blocks, ()), grid)
        self.assertEqual(refit_blocks(grid, 1), tuple((i,) for i in grid))

    def test_a_refit_cadence_below_one_is_refused(self):
        for bad in (0, -1, True, 1.5, None):
            with self.assertRaises(ValueError, msg=repr(bad)):
                refit_blocks((1, 2), bad)


class GuardTests(unittest.TestCase):
    FEATURES = ("spread_bps", "sofr_volume", "reserve_balances", "treasury_settlement_bills")

    def setUp(self):
        self.rule = rule(self.FEATURES)
        self.scored = index_of(date(2026, 1, 22))
        self.info = self.rule.information_set(DATES, self.scored)

    def replaced(self, feature, row):
        reads = tuple(
            read._replace(row=row) if read.feature == feature else read
            for read in self.info.reads
        )
        return self.info._replace(reads=reads)

    def test_every_read_the_rule_makes_passes_both_guards(self):
        """Leakage and staleness both hold on every read the rule makes.

        Recorded mutation (CLAUDE.md), the p - 1 read: in
        `asof.InformationRule._latest`, `return position` mutated to
        `return position - 1`, so every observed read lands one row older than
        the latest admissible. This test then fails, raising `StaleReadError`
        from `InformationRule.check` (the first on the target, `spread_bps`).
        """

        # From the first row with a weekly print observable before it.
        for scored in range(8, len(DATES)):
            self.rule.check(DATES, self.rule.information_set(DATES, scored))

    def test_a_read_newer_than_the_decision_is_leakage(self):
        read = read_of(self.info, "sofr_volume")
        with self.assertRaises(LookAheadError):
            self.rule.check(DATES, self.replaced("sofr_volume", read.row + 1))

    def test_a_read_older_than_the_latest_admissible_is_stale(self):
        """The staleness guard, driven directly with a read one row too old."""

        read = read_of(self.info, "sofr_volume")
        with self.assertRaises(StaleReadError):
            self.rule.check(DATES, self.replaced("sofr_volume", read.row - 1))

    def test_a_stale_target_is_caught(self):
        with self.assertRaises(StaleReadError):
            self.rule.check(DATES, self.replaced("spread_bps", self.info.anchor - 1))

    def test_a_stale_weekly_print_is_caught(self):
        read = read_of(self.info, "reserve_balances")
        with self.assertRaises(StaleReadError):
            self.rule.check(DATES, self.replaced("reserve_balances", read.row - 1))

    def test_a_scheduled_input_read_off_its_day_is_refused(self):
        with self.assertRaises(StaleReadError):
            self.rule.check(DATES, self.replaced("treasury_settlement_bills", self.scored - 1))
        with self.assertRaises(LookAheadError):
            self.rule.check(DATES, self.replaced("treasury_settlement_bills", self.scored + 1))

    def test_stale_read_error_is_not_a_leakage_error(self):
        # Staleness is a correctness guard, not a leakage guard: a stale read
        # never flatters a result, so it must not be caught as one.
        self.assertFalse(issubclass(StaleReadError, LookAheadError))


class DeclarationTests(unittest.TestCase):
    def test_a_field_with_no_declared_availability_is_refused(self):
        registry = copy.deepcopy(REGISTRY)
        del registry["fred_macro_latest_vintage"]["field_release_lags"]["WRESBAL"]
        with self.assertRaises(RegistryContractError):
            rule(["spread_bps", "reserve_balances"], registry).information_set(
                DATES, index_of(date(2026, 1, 22))
            )

    def test_the_tracked_scheduled_declaration_validates(self):
        self.assertEqual(
            validate_scheduled_availability(
                "treasury_auctions", REGISTRY["treasury_auctions"]["scheduled_availability"]
            ),
            [],
        )

    def test_a_scheduled_declaration_must_carry_its_evidence(self):
        block = copy.deepcopy(REGISTRY["treasury_auctions"]["scheduled_availability"])
        del block["evidence"]
        self.assertTrue(validate_scheduled_availability("treasury_auctions", block))
        registry = copy.deepcopy(REGISTRY)
        registry["treasury_auctions"]["scheduled_availability"] = block
        with self.assertRaises(RegistryContractError):
            rule(["spread_bps", "treasury_settlement_bills"], registry)

    def test_a_scheduled_declaration_names_only_its_own_fields(self):
        block = copy.deepcopy(REGISTRY["treasury_auctions"]["scheduled_availability"])
        block["fields"] = ["not_a_field"]
        registry = copy.deepcopy(REGISTRY)
        registry["treasury_auctions"]["scheduled_availability"] = block
        with self.assertRaises(RegistryContractError):
            rule(["spread_bps"], registry)

    def test_the_settlement_evidence_holds_on_the_tracked_snapshot(self):
        """The declaration's claim, checked against the auctions it describes.

        Every auction in the tracked snapshot that settles on or after the
        panel's first date settles on a later date than it was held, and every
        auction closed for competitive bids no later than 14:30 New York time,
        which is before the declared 15:00. So on the business day before any
        settlement date the panel carries, every auction settling that date
        had closed.

        The snapshot also holds three cash management bills auctioned and
        settled on the same day, all before the panel begins (2017-09-08,
        2017-12-08, 2018-01-19). They are pinned here so that the claim's
        boundary is visible: a same-day settlement inside the panel would make
        the declaration false for that day.
        """

        declared = time.fromisoformat(
            REGISTRY["treasury_auctions"]["scheduled_availability"]["available_time"]
        )
        rows = json.loads(SETTLEMENT_SNAPSHOT.read_text())["data"]
        self.assertTrue(rows)
        same_day = []
        for row in rows:
            held = date.fromisoformat(row["auction_date"])
            settled = date.fromisoformat(row["issue_date"])
            if settled < PANEL_FIRST_DATE:
                if held >= settled:
                    same_day.append(settled.isoformat())
                continue
            self.assertLess(held, settled, row["cusip"])
            closed = datetime.strptime(row["closing_time_comp"], "%I:%M %p").time()
            self.assertLess(closed, declared, row["cusip"])
        self.assertEqual(same_day, ["2017-09-08", "2017-12-08", "2018-01-19"])


if __name__ == "__main__":
    unittest.main()
