"""The reserve-scarcity state (#115): a declared regime state, read as-of.

`repo_model.scarcity` computes the state on each panel row from that row's
`reserve_balances`, `bank_total_assets` (the H.8 first print) and `on_rrp`, and
`contract.RESERVE_SCARCITY_STATE_FIELDS` declares it over every field those
draw on, so `InformationRule` reads it only at a row where all three were
public. The declaration is off in the published map; these tests switch it on
for their own duration (`scarcity_inputs_on`).

The tracked registry, `metadata/sources.json`, is read throughout, so what is
pinned is what a measurement run reads.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from repo_model import contract
from repo_model.asof import InformationRule, StaleReadError
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())
DECISION = time(16, 0)


def scarcity_inputs_on():
    """The off declarations switched on, for one test (#115).

    `on_rrp` from the Desk's operation results, `bank_total_assets` from the H.8
    first prints, and the state over all three
    (`scarcity.measurement_declaration`). Returned unstarted, with `start` and
    `stop`, as `mock.patch` objects are.
    """

    from repo_model.scarcity import measurement_declaration

    class Switch:
        def start(self):
            self._block = measurement_declaration()
            self._block.__enter__()

        def stop(self):
            self._block.__exit__(None, None, None)

    return Switch()


def weekdays(start, count, skip=()):
    out = []
    when = start
    while len(out) < count:
        if when.weekday() < 5 and when not in skip:
            out.append(when)
        when += timedelta(days=1)
    return out


#: Tue 2025-09-02 onward (Labor Day, Monday 1 September, is not a panel date).
DATES = weekdays(date(2025, 9, 2), 30)

#: Week-ending Wednesday -> value. A weekly column carries its Wednesday's value
#: to the rows after it, as `build_daily_panel` rule 10 does.
RESERVES = {
    date(2025, 8, 27): 3000.0,
    date(2025, 9, 3): 3000.0,
    date(2025, 9, 10): 3000.0,
    date(2025, 9, 17): 3000.0,
    date(2025, 9, 24): 3000.0,
    date(2025, 10, 1): 3000.0,
    date(2025, 10, 8): 3000.0,
}
#: 3000 / 23500 is 12.77% of bank assets, inside SR 1019's 12-13% band. The
#: week ending 17 September prints 22000, 13.64%, above it: the state moves on
#: the row that carries that week.
BANK_ASSETS = {
    date(2025, 8, 27): 23500.0,
    date(2025, 9, 3): 23500.0,
    date(2025, 9, 10): 23500.0,
    date(2025, 9, 17): 22000.0,
    date(2025, 9, 24): 22000.0,
    date(2025, 10, 1): 22000.0,
    date(2025, 10, 8): 22000.0,
}
#: Below the $100bn buffer throughout.
ON_RRP = 50.0


def carried(weekly, when):
    return weekly[max(week for week in weekly if week <= when)]


def raw_rows(bank_assets=BANK_ASSETS, reserves=RESERVES):
    """Rows whose spread encodes the row (`spread_bps` on row i is i)."""

    return [
        DailyObservation(
            when,
            {
                "sofr": 2.0 + index / 100.0,
                "iorb": 2.0,
                "reserve_balances": carried(reserves, when),
                "bank_total_assets": carried(bank_assets, when),
                "on_rrp": ON_RRP,
            },
        )
        for index, when in enumerate(DATES)
    ]


def rule(features=("spread_bps", "reserve_scarcity_state"), registry=REGISTRY):
    return InformationRule(registry, tuple(features), decision_time=DECISION)


def read_state(rows, scored_day, registry=REGISTRY):
    information = rule(registry=registry)
    scored = DATES.index(scored_day)
    info = information.information_set(DATES, scored)
    information.check(DATES, info)
    (read,) = [item for item in info.reads if item.feature == "reserve_scarcity_state"]
    return information, info, read, information.observation(rows, info)


class LeakageTests(unittest.TestCase):
    """A reserves or bank-assets release after the decision instant does not change the state.

    Written first, and watched failing: before `repo_model.scarcity` existed
    the module failed at `scarcity_inputs_on` with `ModuleNotFoundError: No
    module named 'repo_model.scarcity'`.

    **Recorded mutation** (CLAUDE.md), 2 October 2026, in a disposable copy:
    `metadata/sources.json`, `frb_h8.release_lag`, `"days": 12` mutated to
    `"days": 1` (a week's H.8 print declared public the Thursday after its
    Wednesday, eight days before the Board releases it).
    `test_a_bank_assets_release_after_the_decision_instant_is_invisible` then
    fails with `AssertionError: datetime.date(2025, 9, 19) not less than
    datetime.date(2025, 9, 17)`: the forecast for Monday 29 September reads the
    row of Friday 19 September, which carries the week ending 17 September --
    released by the Board at 16:15 on Friday 26 September, fifteen minutes
    after that forecast's decision. (`test_once_declared_public_the_new_week_is_read`
    fails with it.)
    """

    def setUp(self):
        switch = scarcity_inputs_on()
        switch.start()
        self.addCleanup(switch.stop)
        from repo_model.scarcity import with_reserve_scarcity_state

        self.with_state = with_reserve_scarcity_state

    def test_the_state_moves_on_the_row_that_carries_the_new_week(self):
        """The teeth: the week ending 17 September does change the state."""

        rows = self.with_state(raw_rows())
        by_date = {row.date: row.values["reserve_scarcity_state"] for row in rows}
        self.assertEqual(by_date[date(2025, 9, 16)], 2)
        self.assertEqual(by_date[date(2025, 9, 17)], 1)

    def test_a_bank_assets_release_after_the_decision_instant_is_invisible(self):
        # Monday 29 September: decision Friday 26 September 16:00. The H.8
        # carrying the week ending 17 September is released at 16:15 that day.
        scored_day = date(2025, 9, 29)
        rows = self.with_state(raw_rows())
        information, info, read, observed = read_state(rows, scored_day)
        self.assertEqual(info.decision_instant, datetime(2025, 9, 26, 16, 0))
        self.assertLess(DATES[read.row], date(2025, 9, 17))
        self.assertEqual(observed.values["reserve_scarcity_state"], 2)

        # Without that week's print at all, the forecast reads the same state.
        unreleased = {week: value for week, value in BANK_ASSETS.items()
                      if week < date(2025, 9, 17)}
        rows_before = self.with_state(raw_rows(bank_assets=unreleased))
        _information, _info, read_before, observed_before = read_state(
            rows_before, scored_day
        )
        self.assertEqual(read_before.row, read.row)
        self.assertEqual(
            observed_before.values["reserve_scarcity_state"],
            observed.values["reserve_scarcity_state"],
        )

        # A read forced onto the Wednesday the new print is dated to is leakage.
        wednesday = DATES.index(date(2025, 9, 17))
        forced = info._replace(
            reads=tuple(
                entry._replace(row=wednesday)
                if entry.feature == "reserve_scarcity_state"
                else entry
                for entry in info.reads
            )
        )
        with self.assertRaises(LookAheadError):
            information.check(DATES, forced)

    def test_once_declared_public_the_new_week_is_read(self):
        """Wednesday 1 October: decision Tuesday 30 September 16:00.

        The declaration is the measured worst case, twelve calendar days
        (`frb_h8.release_lag`), so the week ending 17 September is declared
        public at 16:15 on Monday 29 September, three days after the Friday the
        Board released it: read one decision later than it could have been,
        never one earlier.
        """

        rows = self.with_state(raw_rows())
        _information, _info, before, _observed = read_state(rows, date(2025, 9, 30))
        self.assertLess(DATES[before.row], date(2025, 9, 17))
        _information, _info, read, observed = read_state(rows, date(2025, 10, 1))
        self.assertGreaterEqual(DATES[read.row], date(2025, 9, 17))
        self.assertEqual(observed.values["reserve_scarcity_state"], 1)

    def test_a_reserves_release_after_the_decision_instant_is_invisible(self):
        # The H.4.1 for the week ending 24 September is released Thursday 25
        # September at 16:30. A forecast whose decision precedes it reads the
        # same state whether or not that week's reserves exist, even when they
        # would move the state (1500 / 22000 is below the band).
        scored_day = date(2025, 9, 26)  # decision Thursday 25 September 16:00
        moved = {**RESERVES, date(2025, 9, 24): 1500.0}
        rows = self.with_state(raw_rows(reserves=moved))
        unreleased = {week: value for week, value in RESERVES.items()
                      if week < date(2025, 9, 24)}
        rows_before = self.with_state(raw_rows(reserves=unreleased))
        _i, _info, read, observed = read_state(rows, scored_day)
        _i, _info, read_before, observed_before = read_state(rows_before, scored_day)
        self.assertEqual(read.row, read_before.row)
        self.assertEqual(
            observed.values["reserve_scarcity_state"],
            observed_before.values["reserve_scarcity_state"],
        )
        self.assertNotEqual(
            {row.date: row.values["reserve_scarcity_state"] for row in rows}[date(2025, 9, 24)],
            {row.date: row.values["reserve_scarcity_state"] for row in rows_before}[date(2025, 9, 24)],
        )

    def test_a_read_older_than_the_latest_admissible_row_is_stale(self):
        rows = self.with_state(raw_rows())
        information, info, read, _observed = read_state(rows, date(2025, 9, 30))
        older = info._replace(
            reads=tuple(
                entry._replace(row=read.row - 1)
                if entry.feature == "reserve_scarcity_state"
                else entry
                for entry in info.reads
            )
        )
        with self.assertRaises(StaleReadError):
            information.check(DATES, older)



class CutPointTests(unittest.TestCase):
    """The cut-points are constants from the literature, not derived from the data."""

    def test_the_declared_values(self):
        from repo_model import scarcity

        self.assertEqual(scarcity.SATIATION_BAND, (0.12, 0.13))
        self.assertEqual(scarcity.ON_RRP_BUFFER_BN, 100.0)
        self.assertEqual(scarcity.SENSITIVITY_VARIANTS["declared"], ((0.12, 0.13), 100.0))

    def test_each_cut_point_carries_its_citation(self):
        """The comment block above each constant names its source."""

        import inspect

        from repo_model import scarcity

        source = inspect.getsource(scarcity)
        band = source[: source.index("SATIATION_BAND: Tuple")]
        band = band[band.rindex("\n\n"):]
        self.assertIn("Staff Report 1019", band)
        self.assertIn("Afonso, G., D. Giannone, G. La Spada and J. C. Williams", band)
        self.assertIn("sr1019.pdf", band)
        buffer = source[: source.index("ON_RRP_BUFFER_BN = ")]
        buffer = buffer[buffer.rindex("\n\n"):]
        self.assertIn("docs/advisor/evidence-pack/MEMO.md", buffer)
        self.assertIn("#87", buffer)

    def test_nothing_in_the_module_reads_a_spread_to_place_a_cut(self):
        """The state functions take reserves, assets and ON RRP, never an outcome."""

        import inspect

        from repo_model import scarcity

        for function in (
            scarcity.reserve_scarcity_state,
            scarcity.ratio_level,
            scarcity.buffer_level,
            scarcity.with_reserve_scarcity_state,
        ):
            with self.subTest(function=function.__name__):
                self.assertNotIn("spread", inspect.getsource(function))


class StateTests(unittest.TestCase):
    def test_levels_at_and_around_the_cut_points(self):
        from repo_model.scarcity import buffer_level, ratio_level, reserve_scarcity_state

        self.assertEqual(ratio_level(0.13), 0)
        self.assertEqual(ratio_level(0.1299), 1)
        self.assertEqual(ratio_level(0.12), 1)
        self.assertEqual(ratio_level(0.1199), 2)
        self.assertEqual(buffer_level(100.0), 0)
        self.assertEqual(buffer_level(99.9), 1)
        self.assertEqual(reserve_scarcity_state(3000.0, 20000.0, 500.0), 0)
        self.assertEqual(reserve_scarcity_state(3000.0, 20000.0, 5.0), 1)
        self.assertEqual(reserve_scarcity_state(1500.0, 17000.0, 0.0), 3)

    def test_a_hole_in_any_input_is_a_hole_in_the_state(self):
        from repo_model.scarcity import reserve_scarcity_state

        self.assertIsNone(reserve_scarcity_state(None, 20000.0, 5.0))
        self.assertIsNone(reserve_scarcity_state(3000.0, None, 5.0))
        self.assertIsNone(reserve_scarcity_state(3000.0, 20000.0, None))

    def test_impossible_inputs_raise(self):
        from repo_model.scarcity import ratio_level, reserve_scarcity_state

        with self.assertRaises(ValueError):
            reserve_scarcity_state(3000.0, 0.0, 5.0)
        with self.assertRaises(ValueError):
            reserve_scarcity_state(-1.0, 20000.0, 5.0)
        with self.assertRaises(ValueError):
            reserve_scarcity_state(3000.0, 20000.0, -5.0)
        with self.assertRaises(ValueError):
            ratio_level(0.12, band=(0.13, 0.12))

    def test_the_column_is_computed_from_its_own_row_only(self):
        from repo_model.scarcity import with_reserve_scarcity_state

        rows = raw_rows()
        rows[3] = DailyObservation(rows[3].date, {**rows[3].values, "bank_total_assets": None})
        states = [row.values["reserve_scarcity_state"] for row in with_reserve_scarcity_state(rows)]
        self.assertIsNone(states[3])
        self.assertEqual(states[2], states[4])
        with self.assertRaisesRegex(ValueError, "bank_total_assets"):
            with_reserve_scarcity_state(
                [DailyObservation(DATES[0], {"reserve_balances": 1.0, "on_rrp": 1.0})]
            )


class OffInThePublishedDeclarationTests(unittest.TestCase):
    """No published declaration, panel or record reads the state or its inputs."""

    def test_the_published_map_does_not_carry_them(self):
        self.assertNotIn("bank_total_assets", contract.FEATURE_FIELDS)
        self.assertNotIn("reserve_scarcity_state", contract.FEATURE_FIELDS)
        self.assertEqual(
            contract.FEATURE_FIELDS["on_rrp"], (("fred_macro_latest_vintage", "RRPONTSYD"),)
        )
        self.assertIn("frb_h8", contract.UNMODELLED_SOURCES)

    def test_the_switch_is_undone_on_the_way_out_even_on_a_raise(self):
        from repo_model.scarcity import measurement_declaration

        before = contract.FEATURE_FIELDS, contract.FEATURE_SOURCES
        with self.assertRaises(RuntimeError):
            with measurement_declaration():
                self.assertEqual(
                    contract.FEATURE_FIELDS["reserve_scarcity_state"],
                    contract.RESERVE_SCARCITY_STATE_FIELDS,
                )
                self.assertEqual(
                    contract.FEATURE_SOURCES["reserve_scarcity_state"],
                    ("frb_h8", "fred_macro_latest_vintage", "nyfed_on_rrp"),
                )
                raise RuntimeError("out")
        self.assertIs(contract.FEATURE_FIELDS, before[0])
        self.assertIs(contract.FEATURE_SOURCES, before[1])

    def test_the_published_panel_manifest_does_not_build_them(self):
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text())
        for column in ("bank_total_assets", "reserve_scarcity_state", "on_rrp"):
            self.assertNotIn(column, manifest["built_columns"])

    def test_the_state_reads_every_field_its_three_inputs_read(self):
        from repo_model.scarcity import measurement_feature_fields

        fields = measurement_feature_fields()
        self.assertEqual(
            set(fields["reserve_scarcity_state"]),
            set(fields["reserve_balances"]) | set(fields["bank_total_assets"]) | set(fields["on_rrp"]),
        )


EXTRACT = ROOT / "tests/fixtures/snapshots/h8_inputs/frb_h8/h8_total_assets_first_print.csv"


class TrackedExtractTests(unittest.TestCase):
    """The tracked H.8 first prints agree with the declaration that dates them."""

    def setUp(self):
        import csv

        with EXTRACT.open(newline="", encoding="utf-8") as handle:
            self.rows = list(csv.DictReader(handle))
        self.declared = REGISTRY["frb_h8"]["release_lag"]

    def test_no_week_is_first_printed_later_than_declared(self):
        """The declaration is at least every measured first-print lag.

        A shorter one would date a value before its release: the leakage
        direction. The declaration is the measured maximum, not above it.
        """

        lags = [
            (date.fromisoformat(row["release_date"]) - date.fromisoformat(row["week_ending"])).days
            for row in self.rows
        ]
        self.assertLessEqual(max(lags), self.declared["days"])
        self.assertEqual(max(lags), self.declared["days"])
        self.assertEqual(self.declared["available_time"], "16:15")
        self.assertEqual(self.declared["basis"], "record_date")
        self.assertGreater(time.fromisoformat(self.declared["available_time"]), DECISION)

    def test_weeks_are_consecutive_wednesdays_covering_the_panel(self):
        weeks = [date.fromisoformat(row["week_ending"]) for row in self.rows]
        self.assertTrue(all(week.weekday() == 2 for week in weeks))
        self.assertTrue(all((b - a).days == 7 for a, b in zip(weeks, weeks[1:])))
        self.assertLessEqual(weeks[0], date(2018, 4, 3) - timedelta(days=12))
        self.assertGreaterEqual(weeks[-1], date(2025, 12, 31) - timedelta(days=12))

    def test_every_release_named_is_in_the_page_manifest(self):
        releases = json.loads(
            EXTRACT.with_name("h8_total_assets_first_print.releases.json").read_text()
        )["releases"]
        digests = {(item["public_on"], item["sha256"]) for item in releases}
        for row in self.rows:
            with self.subTest(week=row["week_ending"]):
                self.assertIn((row["release_date"], row["release_sha256"]), digests)

    def test_the_extract_rebuilds_from_the_raw_pages_when_they_are_present(self):
        """`extract_h8_first_prints.py --check`, where `data/raw/frb_h8/` exists.

        The pages are gitignored, so a fresh clone skips this; the run that
        fetched them, and any run after `fetch h8`, checks it.
        """

        raw = ROOT / "data/raw/frb_h8"
        if not raw.is_dir():
            self.skipTest("data/raw/frb_h8 is not present; run `fetch h8` to check the extract")
        import contextlib
        import importlib.util
        import io

        spec = importlib.util.spec_from_file_location(
            "extract_h8_first_prints", ROOT / "scripts/extract_h8_first_prints.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = module.main(["--check"])
        self.assertEqual(code, 0, out.getvalue())


class TabulateTests(unittest.TestCase):
    def day(self, offset, state, spread):
        from repo_model.scarcity import ScoredDay

        when = date(2024, 12, 30) + timedelta(days=offset)
        return ScoredDay(when, state, when, spread)

    def test_frequencies_per_state_and_year_and_the_rise(self):
        from repo_model.scarcity import tabulate

        scored = (
            [self.day(i, 0.0, -5.0) for i in range(10)]
            + [self.day(10 + i, 1.0, 6.0 if i < 2 else 0.5) for i in range(10)]
            + [self.day(20 + i, 3.0, 12.0 if i < 5 else -1.0) for i in range(10)]
            + [self.day(30, None, 50.0)]
        )
        table = tabulate(scored)
        self.assertEqual(table["unknown_state_days"], 1)
        self.assertEqual(sorted(table["by_state"]), ["0", "1", "3"])
        self.assertEqual(table["by_state"]["1"]["gt_5bp"]["pressure_days"], 2)
        self.assertAlmostEqual(table["by_state"]["3"]["gt_10bp"]["frequency"], 0.5)
        self.assertEqual(table["by_state"]["1"]["above_iorb_days"], 10)
        self.assertEqual(table["rises"], {"gt_5bp": True, "gt_10bp": True})
        low, high = table["by_state"]["3"]["gt_5bp"]["interval"]
        self.assertLessEqual(low, 0.5)
        self.assertGreaterEqual(high, 0.5)
        self.assertEqual(table["by_year"]["2024"]["days"], 2)
        self.assertEqual(table["by_year"]["2025"]["unknown_state_days"], 1)

    def test_a_fall_is_reported_as_one(self):
        from repo_model.scarcity import tabulate

        scored = [self.day(i, 0.0, 6.0) for i in range(5)] + [self.day(5 + i, 1.0, 0.0) for i in range(5)]
        self.assertEqual(tabulate(scored)["rises"]["gt_5bp"], False)


class MeasurementPanelTests(unittest.TestCase):
    """The measurement build, from tracked fixtures, as the validation script makes it."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        import tempfile

        spec = importlib.util.spec_from_file_location(
            "scarcity_validation", ROOT / "scripts/scarcity_validation.py"
        )
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        from repo_model.scarcity import measurement_declaration

        with measurement_declaration(), tempfile.TemporaryDirectory() as directory:
            cls.build, cls.digest, _registry, _decision = cls.module.build_measurement_panel(
                ROOT / "metadata/sources.json", Path(directory)
            )

    def test_its_published_columns_are_the_published_panel(self):
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text())
        self.assertEqual(self.digest, manifest["sha256"])

    def test_bank_assets_and_on_rrp_have_no_hole_and_a_state_is_on_every_row(self):
        from repo_model.scarcity import with_reserve_scarcity_state

        self.assertEqual(self.build.holes["bank_total_assets"], 0)
        self.assertEqual(self.build.holes["on_rrp"], 0)
        states = {row.values["reserve_scarcity_state"] for row in with_reserve_scarcity_state(self.build.observations)}
        self.assertLessEqual(states, {0.0, 1.0, 2.0, 3.0})

    def test_a_row_carries_the_latest_wednesday_at_or_before_it(self):
        import csv

        with EXTRACT.open(newline="", encoding="utf-8") as handle:
            prints = {date.fromisoformat(r["week_ending"]): float(r["total_assets"]) for r in csv.DictReader(handle)}
        for row in self.build.observations[::97]:
            with self.subTest(day=row.date):
                week = max(w for w in prints if w <= row.date)
                self.assertEqual(row.values["bank_total_assets"], prints[week])


if __name__ == "__main__":
    unittest.main()
