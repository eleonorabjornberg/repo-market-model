"""The as-of information set: `docs/decisions/information-set.md`, implemented.

Most of these tests read the tracked registry, `metadata/sources.json`, rather
than a synthetic one, so what they pin is what the published runs will read.
A synthetic declaration appears only where a test is about the mechanism
rather than about a source.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model.asof import (
    InformationRule,
    StaleReadError,
    fold_grid,
    refit_blocks,
    validate_scheduled_availability,
)
from repo_model.data import DailyObservation
from repo_model.registry import RegistryContractError
from repo_model.splits import LookAheadError, SplitError

sys.path.insert(0, str(Path(__file__).parent))
from test_contract import on_rrp_from_operation_results

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
        # The declaration `docs/decisions/iorb-availability.md` superseded
        # (record_date + 1 day at 16:15), on a registry copy: the mechanism
        # the as-of PR's acceptance runs measured. Scored Thursday 2026-01-08,
        # decision Wednesday 16:00. SOFR for Tuesday is final Wednesday 15:00,
        # but IORB for Tuesday would be observable Wednesday 16:15 -- fifteen
        # minutes late -- so the latest row whose whole target is observable
        # is Monday.
        registry = copy.deepcopy(REGISTRY)
        for name in ("IORB", "IOER"):
            registry["fred_macro_latest_vintage"]["field_release_lags"][name]["days"] = 1
        scored = index_of(date(2026, 1, 8))
        anchor = rule(["spread_bps"], registry).anchor(DATES, scored)
        self.assertEqual(DATES[anchor], date(2026, 1, 5))

    def test_under_the_tracked_iorb_declaration_the_target_is_two_rows_back(self):
        # `docs/decisions/iorb-availability.md`: IORB and IOER are observable
        # at 16:15 on their own date, so SOFR binds and the target is read two
        # panel rows before the scored day on every day, holidays included.
        current = rule(["spread_bps"])
        for scored in range(3, len(DATES)):
            self.assertEqual(current.anchor(DATES, scored), scored - 2, DATES[scored])

    def test_after_a_weekend_the_target_is_two_rows_back(self):
        # Scored Tuesday 2026-01-13, decision Monday 16:00: Friday's IORB was
        # observable Saturday 16:15 and Friday's SOFR Monday 15:00.
        scored = index_of(date(2026, 1, 13))
        anchor = rule(["spread_bps"]).anchor(DATES, scored)
        self.assertEqual(DATES[anchor], date(2026, 1, 9))

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

    def test_the_settlement_declaration_cites_treasurys_procedure(self):
        """#59 part 2: the note quotes 31 CFR 356.23(a), Treasury's own statement.

        The quote names no clock time, so the 15:00 instant still rests on the
        auction data; the note says so rather than calling it confirmed.
        """

        note = REGISTRY["treasury_auctions"]["scheduled_availability"]["note"]
        self.assertIn("https://www.ecfr.gov/current/title-31/section-356.23", note)
        self.assertIn("After the conclusion of the auction", note)
        self.assertNotIn("unverified", note)

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


class SettlementScheduleGuardTests(unittest.TestCase):
    """The load-time refusal behind the `treasury_auctions` declaration.

    The declaration says a settlement for date d is public at 15:00 New York
    time on the panel day before d. `ingest.check_settlement_schedule` refuses
    any auction settling inside the panel window that closed later than that
    -- which includes one settling on its own auction date -- so the claim is
    checked against every build's own auctions rather than trusted.

    Recorded mutation (CLAUDE.md), run with `-B` and
    `PYTHONDONTWRITEBYTECODE=1`: in `ingest.check_settlement_schedule`, the
    refusal condition `if closed > deadline:` mutated to `if False:`. Three
    tests here then fail with `AssertionError: ValueError not raised`:
    `test_a_same_day_settlement_inside_the_window_is_refused`,
    `test_a_close_after_the_declared_instant_the_day_before_is_refused` and
    `test_a_close_that_leaves_no_panel_day_between_is_measured_on_the_panel`.

    That mutation does not reach the unreadable-closing-time refusal, which
    has its own: in the same function, the `except ValueError:` branch's
    `raise ValueError(...) from None` replaced with `continue`.
    `test_an_auction_with_no_closing_time_is_refused` then fails with
    `AssertionError: ValueError not raised`, and no other test here does.
    """

    BLOCK = REGISTRY["treasury_auctions"]["scheduled_availability"]
    # Mon 5 Jan .. ; the panel skips MLK Monday 19 Jan.
    PANEL = DATES

    @staticmethod
    def auction(held, settled, close="11:30 AM", cusip="TEST00001"):
        return {
            "cusip": cusip,
            "auction_date": held.isoformat(),
            "issue_date": settled.isoformat(),
            "closing_time_comp": close,
        }

    def check(self, *records):
        from repo_model.ingest import check_settlement_schedule

        check_settlement_schedule(list(records), self.PANEL, self.BLOCK)

    def test_an_ordinary_auction_passes(self):
        self.check(self.auction(date(2026, 1, 13), date(2026, 1, 15), "01:00 PM"))

    def test_a_same_day_settlement_inside_the_window_is_refused(self):
        with self.assertRaisesRegex(ValueError, "TEST00001"):
            self.check(self.auction(date(2026, 1, 15), date(2026, 1, 15)))

    def test_a_close_after_the_declared_instant_the_day_before_is_refused(self):
        with self.assertRaisesRegex(ValueError, "15:00"):
            self.check(self.auction(date(2026, 1, 14), date(2026, 1, 15), "03:30 PM"))

    def test_a_close_that_leaves_no_panel_day_between_is_measured_on_the_panel(self):
        # Settles Tuesday 20 January; MLK Monday is not a panel date, so the
        # panel day before is Friday 16 January, and an auction held on the
        # Monday holiday closed after that day's 15:00.
        with self.assertRaises(ValueError):
            self.check(self.auction(date(2026, 1, 19), date(2026, 1, 20)))

    def test_an_auction_settling_outside_the_panel_window_is_not_judged(self):
        # The tracked snapshot's same-day cash management bills of 2017 and
        # early 2018 settle before the panel begins; the declaration makes no
        # claim about them.
        self.check(self.auction(date(2025, 12, 1), date(2025, 12, 1)))
        self.check(self.auction(date(2026, 12, 1), date(2026, 12, 1)))

    def test_an_auction_with_no_closing_time_is_refused(self):
        record = self.auction(date(2026, 1, 13), date(2026, 1, 15))
        record["closing_time_comp"] = "null"
        with self.assertRaisesRegex(ValueError, "closing_time_comp"):
            self.check(record)

    def test_the_build_command_runs_it(self):
        """Wired: `repo_model.cli build` calls it on every build's auctions."""

        from repo_model import cli_data

        source = Path(cli_data.__file__).read_text(encoding="utf-8")
        self.assertIn("check_scheduled_settlements(", source)


class OnRrpAvailabilityTests(unittest.TestCase):
    """`on_rrp` is read at the next business day's decision instant (#45, step 3).

    The Desk's operation closes at 13:15 ET and its results are published at no
    stated clock time (A45, Route B, item 2). `nyfed_on_rrp.release_lag` takes
    the conservative reading #45 offered instead of establishing one: a result
    is available at 16:00 ET on the next panel business day. So at the 16:00
    decision on Wednesday 21 January the Wednesday result, closed at 13:15 that
    day, is invisible, and the latest read is Tuesday's.

    Recorded mutation (CLAUDE.md), 2 October 2026, in a disposable copy:
    `metadata/sources.json`, `nyfed_on_rrp.release_lag`, `"days": 1` mutated to
    `"days": 0` (a result public at 16:00 on its own operation date).
    `test_a_result_after_the_decision_instant_is_invisible` then fails with
    `AssertionError` (`datetime.date(2026, 1, 21) != datetime.date(2026, 1,
    20)`): the forecast reads the operation that closed the afternoon of its
    own decision.
    """

    FEATURES = ("spread_bps", "on_rrp")
    FIELDS = (("nyfed_on_rrp", "reverse_repo_total_accepted"),)

    def setUp(self):
        # Off in the published map (`contract.ON_RRP_OPERATION_RESULTS_FIELDS`);
        # switched on for these tests.
        switch = on_rrp_from_operation_results()
        switch.start()
        self.addCleanup(switch.stop)

    def rows(self):
        # `on_rrp` encodes its own row, 500 + i, so a read is legible.
        return [
            DailyObservation(row.date, {**row.values, "on_rrp": 500.0 + index})
            for index, row in enumerate(ROWS)
        ]

    def test_a_result_after_the_decision_instant_is_invisible(self):
        """The leakage test: Wednesday's result is not read at Wednesday's decision."""

        information = rule(self.FEATURES)
        scored = index_of(date(2026, 1, 22))  # Thursday; decision Wed 21st 16:00
        info = information.information_set(DATES, scored)
        read = read_of(info, "on_rrp")

        self.assertEqual(read.fields, self.FIELDS)
        self.assertEqual(DATES[read.row], date(2026, 1, 20))
        self.assertEqual(read.available_at, datetime(2026, 1, 21, 16, 0))
        # The result placed after the decision instant: Wednesday's, available
        # Thursday at 16:00.
        wednesday = scored - 1
        self.assertEqual(DATES[wednesday], date(2026, 1, 21))
        self.assertGreater(
            information.availability(DATES, self.FIELDS, wednesday),
            info.decision_instant,
        )
        observed = information.observation(self.rows(), info)
        self.assertEqual(observed.values["on_rrp"], 500.0 + read.row)
        self.assertNotEqual(observed.values["on_rrp"], 500.0 + wednesday)
        # And a read forced onto it is leakage.
        forced = info._replace(
            reads=tuple(
                entry._replace(row=wednesday) if entry.feature == "on_rrp" else entry
                for entry in info.reads
            )
        )
        with self.assertRaises(LookAheadError):
            information.check(DATES, forced)

    def test_across_a_holiday_the_prior_operation_is_read(self):
        """#45, step 4: the holiday carry, through the as-of rule.

        MLK Monday, 19 January, is not a panel date and the facility does not
        operate. At the 16:00 decision on Tuesday the 20th, the latest
        published result is Friday the 16th's, available at Tuesday 16:00, and
        that is the row the rule reads: no hole, and no special case.
        """

        information = rule(self.FEATURES)
        scored = index_of(date(2026, 1, 21))  # decision Tue 20th 16:00
        info = information.information_set(DATES, scored)
        read = read_of(info, "on_rrp")
        self.assertEqual(DATES[read.row], date(2026, 1, 16))
        self.assertEqual(read.available_at, datetime(2026, 1, 20, 16, 0))
        information.check(DATES, info)
        self.assertEqual(
            information.observation(self.rows(), info).values["on_rrp"],
            500.0 + index_of(date(2026, 1, 16)),
        )

    def test_every_on_rrp_read_passes_both_guards(self):
        information = rule(self.FEATURES)
        for scored in range(3, len(DATES)):
            information.check(DATES, information.information_set(DATES, scored))


class OnRrpDepletionTests(unittest.TestCase):
    """The conditional scarcity features (#88), composed from per-field reads.

    `on_rrp_depleted` is `1(on_rrp < 100bn)` and `reserves_when_depleted` is
    `reserve_balances * on_rrp_depleted`. Each input is read as-of on its own
    declaration and the product is formed at the decision instant, so neither
    feature sees a value of either input later than the input's own read.

    At the 16:00 decision on Wednesday 21 January, `on_rrp` is read at Tuesday
    the 20th (Wednesday's result is public Thursday at 16:00) and
    `reserve_balances` at Thursday the 15th (record date plus five calendar
    days at 16:15).

    Written first: before `contract.COMPOSED_FEATURES` existed, every test here
    raised `UndeclaredFeatureError` ('on_rrp_depleted' is not in
    contract.FEATURE_FIELDS, ...).

    Recorded mutation (CLAUDE.md), 2 October 2026, in a disposable copy of
    `src/` and `tests/`: in `asof.InformationRule.observation`, the line
    `return DailyObservation(anchor.date, self._composed(values))` mutated to
    `return DailyObservation(anchor.date,
    self._composed(dict(rows[info.scored_index - 1].values)))`, the features
    formed from the decision day's own row. `test_a_result_after_the_decision_
    instant_crossing_the_break_changes_neither_feature` then fails with
    `AssertionError` (`1.0 != 0.0`): Wednesday's result, below the break and not
    public until Thursday, turned the indicator on. Three other tests here fail
    with it.
    """

    FEATURES = (
        "spread_bps",
        "reserve_balances",
        "on_rrp",
        "on_rrp_depleted",
        "reserves_when_depleted",
    )
    COMPOSED = ("on_rrp_depleted", "reserves_when_depleted")

    def setUp(self):
        switch = on_rrp_from_operation_results()
        switch.start()
        self.addCleanup(switch.stop)
        self.information = rule(self.FEATURES)
        self.scored = index_of(date(2026, 1, 22))  # decision Wed 21st 16:00
        self.info = self.information.information_set(DATES, self.scored)

    def rows(self, **on_rrp):
        """`ROWS` with `on_rrp` at 500bn, but for the dates named in `on_rrp`."""

        overrides = {date.fromisoformat(key[1:].replace("_", "-")): value
                     for key, value in on_rrp.items()}
        return [
            DailyObservation(
                row.date, {**row.values, "on_rrp": overrides.get(row.date, 500.0)}
            )
            for row in ROWS
        ]

    def composed(self, rows):
        observed = self.information.observation(rows, self.info)
        return {name: observed.values[name] for name in self.COMPOSED}

    def test_a_result_after_the_decision_instant_crossing_the_break_changes_neither_feature(self):
        """The leakage test (#88, step 3)."""

        wednesday = index_of(date(2026, 1, 21))
        self.assertGreater(
            self.information.availability(
                DATES, (("nyfed_on_rrp", "reverse_repo_total_accepted"),), wednesday
            ),
            self.info.decision_instant,
        )
        above = self.composed(self.rows())
        crossed = self.composed(self.rows(d2026_01_21=50.0))
        self.assertEqual(above, {"on_rrp_depleted": 0.0, "reserves_when_depleted": 0.0})
        self.assertEqual(crossed["on_rrp_depleted"], above["on_rrp_depleted"])
        self.assertEqual(
            crossed["reserves_when_depleted"], above["reserves_when_depleted"]
        )

    def test_a_crossing_public_by_the_decision_turns_both_on(self):
        """Tuesday's result is public at Wednesday 16:00: the features read it."""

        composed = self.composed(self.rows(d2026_01_20=50.0))
        reserves = ROWS[index_of(date(2026, 1, 15))].values["reserve_balances"]
        self.assertEqual(composed["on_rrp_depleted"], 1.0)
        # The weekly read, not Tuesday's row: each input is read on its own
        # declaration, never both at one row.
        self.assertEqual(composed["reserves_when_depleted"], reserves)
        self.assertNotEqual(
            reserves, ROWS[index_of(date(2026, 1, 20))].values["reserve_balances"]
        )

    def test_a_later_reserves_print_changes_nothing(self):
        later = [
            DailyObservation(
                row.date,
                {**row.values, "reserve_balances": -1.0}
                if row.date > date(2026, 1, 15)
                else row.values,
            )
            for row in self.rows(d2026_01_20=50.0)
        ]
        self.assertEqual(
            self.composed(later), self.composed(self.rows(d2026_01_20=50.0))
        )

    def test_the_break_is_strict(self):
        self.assertEqual(
            self.composed(self.rows(d2026_01_20=100.0))["on_rrp_depleted"], 0.0
        )
        self.assertEqual(
            self.composed(self.rows(d2026_01_20=99.999))["on_rrp_depleted"], 1.0
        )

    def test_the_constituents_are_read_and_guarded_as_their_own_fields(self):
        groups = [group.feature for group in self.information.groups]
        self.assertEqual(groups, ["spread_bps", "reserve_balances", "on_rrp"])
        alone = rule(("spread_bps", "reserves_when_depleted"))
        self.assertEqual(
            [group.feature for group in alone.groups],
            ["spread_bps", "reserve_balances", "on_rrp"],
        )
        # From the first decision with a weekly reserves print behind it.
        for scored in range(index_of(date(2026, 1, 13)), len(DATES)):
            alone.check(DATES, alone.information_set(DATES, scored))

    def test_the_frame_composes_each_row_from_what_was_observable(self):
        rows = self.rows(d2026_01_16=50.0, d2026_01_20=50.0)
        frame = self.information.frame(rows, self.info)
        self.assertEqual(frame[-1].date, date(2026, 1, 20))
        for position, row in enumerate(frame):
            on_rrp = rows[position].values["on_rrp"]
            depleted = 1.0 if on_rrp < 100.0 else 0.0
            self.assertEqual(row.values["on_rrp_depleted"], depleted, row.date)
            reserves = row.values["reserve_balances"]
            if row.date > date(2026, 1, 15):
                # Not yet printed at the decision: a hole, and so is the product.
                self.assertIsNone(reserves, row.date)
                self.assertIsNone(row.values["reserves_when_depleted"], row.date)
            else:
                self.assertEqual(
                    row.values["reserves_when_depleted"], reserves * depleted, row.date
                )

    def test_a_hole_in_on_rrp_is_a_hole_in_both(self):
        rows = self.rows()
        tuesday = index_of(date(2026, 1, 20))
        rows[tuesday] = DailyObservation(
            rows[tuesday].date, {**rows[tuesday].values, "on_rrp": None}
        )
        self.assertEqual(
            self.composed(rows),
            {"on_rrp_depleted": None, "reserves_when_depleted": None},
        )


class HorizonTests(unittest.TestCase):
    """A forecast `horizon` panel days ahead (#114).

    The decision instant is the declared time on the panel day `horizon` rows
    before the scored day; `horizon=1` is the rule every published record was
    scored under. Every read follows from that instant by the same per-field
    rule, so a longer horizon reads older rows and nothing else changes.
    """

    FEATURES = ("spread_bps", "sofr_volume", "reserve_balances", "days_to_month_end")

    def rule(self, horizon, features=FEATURES, registry=REGISTRY):
        return InformationRule(
            registry, tuple(features), decision_time=DECISION, horizon=horizon
        )

    def test_the_decision_is_horizon_panel_days_before_the_scored_day(self):
        scored = index_of(date(2026, 1, 22))
        for horizon in (1, 2, 3, 5):
            info = self.rule(horizon).information_set(DATES, scored)
            self.assertEqual(
                info.decision_instant, datetime.combine(DATES[scored - horizon], DECISION)
            )

    def test_horizon_one_is_the_published_rule(self):
        scored = index_of(date(2026, 1, 22))
        self.assertEqual(
            self.rule(1).information_set(DATES, scored),
            rule(self.FEATURES).information_set(DATES, scored),
        )

    def test_the_target_is_read_horizon_plus_one_rows_back(self):
        current = self.rule(3)
        for scored in range(5, len(DATES)):
            self.assertEqual(current.anchor(DATES, scored), scored - 4, DATES[scored])

    def test_a_calendar_field_is_still_read_at_the_scored_day(self):
        scored = index_of(date(2026, 1, 22))
        info = self.rule(4).information_set(DATES, scored)
        self.assertEqual(read_of(info, "days_to_month_end").row, scored)

    def test_a_row_without_horizon_rows_before_it_has_no_decision(self):
        with self.assertRaises(SplitError):
            self.rule(3).information_set(DATES, 2)

    def test_a_horizon_below_one_is_refused(self):
        for bad in (0, -1, True, 1.5, None):
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.rule(bad)

    def test_every_read_at_a_long_horizon_passes_the_independent_guard(self):
        """The rule's reads at horizon 3 clear `_check_decision_relative_availability` at 3.

        That guard predates the rule and computes its own deadline, so it
        checks the rule's horizon rather than trusting it.

        Recorded mutation (CLAUDE.md), the horizon dropped from the decision:
        in `asof.InformationRule.decision_instant`,
        `dates[scored_index - self.horizon]` mutated to
        `dates[scored_index - 1]`, so a horizon-3 forecast reads what was public
        the day before the scored day. This test then fails, raising
        `LookAheadError` from `baseline._check_decision_relative_availability`
        (the first on the target's `fred_macro_latest_vintage.IOER`).
        """

        from repo_model.baseline import _check_decision_relative_availability

        current = self.rule(3)
        for scored in range(10, len(DATES)):
            info = current.information_set(DATES, scored)
            current.check(DATES, info)
            for read in info.reads:
                _check_decision_relative_availability(
                    REGISTRY, read.fields, DATES, read.row, scored,
                    decision_time=DECISION, horizon=3,
                )

    def test_the_independent_guard_refuses_a_read_too_new_for_the_horizon(self):
        """A read public by the day before, but not by `horizon` days before.

        Recorded mutation (CLAUDE.md), the guard's own deadline: in
        `baseline._check_decision_relative_availability`,
        `dates[scored_index - horizon]` mutated to `dates[scored_index - 1]`.
        This test then fails, raising `AssertionError` ("LookAheadError not
        raised"): the guard accepts a horizon-1 read at horizon 3.
        """

        from repo_model.baseline import _check_decision_relative_availability

        scored = index_of(date(2026, 1, 22))
        one_day = rule(self.FEATURES).information_set(DATES, scored)
        read = read_of(one_day, "sofr_volume")
        _check_decision_relative_availability(
            REGISTRY, read.fields, DATES, read.row, scored, decision_time=DECISION
        )
        with self.assertRaises(LookAheadError):
            _check_decision_relative_availability(
                REGISTRY, read.fields, DATES, read.row, scored,
                decision_time=DECISION, horizon=3,
            )

    def test_the_rule_check_refuses_a_horizon_one_read_at_horizon_three(self):
        scored = index_of(date(2026, 1, 22))
        current = self.rule(3)
        info = current.information_set(DATES, scored)
        newer = rule(self.FEATURES).information_set(DATES, scored)
        reads = tuple(
            mine._replace(row=theirs.row) if mine.feature == "sofr_volume" else mine
            for mine, theirs in zip(info.reads, newer.reads)
        )
        with self.assertRaises(LookAheadError):
            current.check(DATES, info._replace(reads=reads))

    def test_a_settlement_announced_one_day_ahead_is_not_public_two_days_ahead(self):
        # `treasury_auctions` declares a settlement public one panel day before
        # it, at 15:00. At horizon 2 the decision is a day earlier than that.
        scored = index_of(date(2026, 1, 22))
        current = self.rule(2, ("spread_bps", "treasury_settlement"))
        with self.assertRaises(LookAheadError):
            current.check(DATES, current.information_set(DATES, scored))
        one = self.rule(1, ("spread_bps", "treasury_settlement"))
        one.check(DATES, one.information_set(DATES, scored))

    def test_the_grid_starts_where_the_horizon_leaves_enough_labels(self):
        one = fold_grid(DATES, REGISTRY, decision_time=DECISION, minimum_history=5)
        three = fold_grid(
            DATES, REGISTRY, decision_time=DECISION, minimum_history=5, horizon=3
        )
        self.assertEqual(three[0], one[0] + 2)
        self.assertEqual(three[-1], len(DATES) - 1)
        self.assertEqual(self.rule(3).anchor(DATES, three[0]) + 1, 5)
