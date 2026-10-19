"""Fed repo operations and Standing Repo Facility take-up as measurement fields (#425)."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock
from zoneinfo import ZoneInfo

from repo_model import contract, fed_liquidity, ingest
from repo_model import pressure_judge as pj
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.ingest import SnapshotArtifact, load_snapshot_manifest, parse_snapshots
from repo_model.asof import StaleReadError
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = fed_liquidity.load_registry()
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots" / "repo_ops_inputs"
DECLARATION = ROOT / "metadata" / "pressure_judge.json"
NEW_YORK = ZoneInfo("America/New_York")
BN = 1_000_000_000


def operation(
    day, accepted, *, kind="Repo", term="Overnight", submitted=None, rate=None, written=None, note="",
    settle=None, maturity=None,
):
    """One operation record, in the Desk's shape. Settles on its date and matures the next day unless told."""

    submitted = accepted if submitted is None else submitted
    settle = settle or day
    maturity = maturity or (date.fromisoformat(settle) + timedelta(days=1)).isoformat()
    details = [{"securityType": "Treasury", "amtSubmitted": submitted, "amtAccepted": accepted}]
    if rate is not None:
        details[0]["percentWeightedAverageRate"] = rate
    return {
        "operationId": f"{kind} {day} {term}",
        "operationDate": day,
        "settlementDate": settle,
        "maturityDate": maturity,
        "operationType": kind,
        "term": term,
        "note": note,
        "lastUpdated": written or f"{day} 13:46:19",
        "totalAmtSubmitted": submitted,
        "totalAmtAccepted": accepted,
        "details": details,
    }


def rows_for(*operations, retrieved="2026-10-08T20:51:05+00:00"):
    payload = json.dumps({"repo": {"operations": list(operations)}}).encode()
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "ops.json"
    path.write_bytes(payload)
    artifact = SnapshotArtifact(
        source_id=ingest.NYFED_REPO_OPS_SOURCE_ID,
        path=path,
        retrieved_at=retrieved,
        sha256=hashlib.sha256(payload).hexdigest(),
        url=ingest.NYFED_RP_RESULTS_URL,
        byte_count=len(payload),
    )
    try:
        return ingest._nyfed_repo_ops_rows(artifact, payload)
    finally:
        directory.cleanup()


def by_series(rows):
    out = {}
    for r in rows:
        out.setdefault(r.series_id, {})[r.ref_date] = r
    return out


class ParserTests(unittest.TestCase):
    """`_nyfed_repo_ops_rows`: every repo operation of a date, in USD billions.

    Recorded mutation for the facility start (#659), 13 October 2026, in a disposable copy:
    `src/repo_model/ingest.py`, `_kept_repo_operations`, `if ref_date < REPO_FACILITY_START:` mutated to
    `if False:` (the six test operations of $64-66m kept as take-up).
    `test_an_operation_before_the_facility_is_a_test_not_take_up` then fails with `AssertionError`
    (`Lists differ: [datetime.date(2019, 5, 13), datetime.date(2019, 9, 16), datetime.date(2019, 9, 17)] !=
    [datetime.date(2019, 9, 17)]`).

    Recorded mutation (CLAUDE.md), 8 October 2026, in a disposable copy:
    `src/repo_model/ingest.py`, `_nyfed_repo_ops_rows`,
    `available_at = min(max(declared, published.get(ref_date, declared)), retrieved)` mutated to
    `available_at = min(declared, retrieved)` (the Desk's recorded publication time ignored).
    `test_a_rewritten_record_is_read_after_its_rewrite` then fails with `AssertionError`
    (`datetime(2021, 9, 7, 16, 0) != datetime(2021, 9, 16, 10, 53)`: the rewritten date is read on
    its declaration, nine days before its write), and so does
    `SnapshotTests.test_no_row_is_published_before_its_publication_time_or_its_declaration`.
    """

    def test_a_date_sums_overnight_and_term_repos_and_leaves_reverse_repos(self):
        rows = by_series(
            rows_for(
                operation("2020-03-17", 40 * BN, rate=0.10),
                operation("2020-03-17", 60 * BN, term="Term", rate=0.20),
                operation("2020-03-17", 99 * BN, kind="Reverse Repo"),
                operation("2020-03-17", 0, term="Term"),
            )
        )
        day = date(2020, 3, 17)
        self.assertAlmostEqual(rows["repo_accepted"][day].value, 100.0)
        self.assertAlmostEqual(rows["repo_submitted"][day].value, 100.0)
        self.assertEqual(rows["repo_ops_accepting"][day].value, 2.0)
        self.assertAlmostEqual(rows["repo_rate"][day].value, (0.10 * 40 + 0.20 * 60) / 100.0)

    def test_a_small_value_exercise_is_not_take_up_and_a_date_of_nothing_is_zero(self):
        rows = by_series(
            rows_for(
                operation("2019-12-16", 25_000_000, note="Statement Regarding Repurchase Agreement Small Value Exercise"),
                operation("2019-12-17", 0),
            )
        )
        self.assertNotIn(date(2019, 12, 16), rows["repo_accepted"])
        self.assertEqual(rows["repo_accepted"][date(2019, 12, 17)].value, 0.0)
        self.assertNotIn(date(2019, 12, 17), rows.get("repo_rate", {}))

    def test_an_operation_before_the_facility_is_a_test_not_take_up(self):
        rows = by_series(
            rows_for(
                operation("2019-05-13", 65_000_000),
                operation("2019-09-16", 66_000_000, term="Term", maturity="2019-09-18"),
                operation("2019-09-17", 53 * BN),
            )
        )
        self.assertEqual(sorted(rows["repo_accepted"]), [date(2019, 9, 17)])
        self.assertEqual(ingest.REPO_FACILITY_START, date(2019, 9, 17))
        self.assertEqual(
            sorted(ingest.repo_operation_publication_times(
                json.dumps({"repo": {"operations": [operation("2019-05-13", 65_000_000), operation("2019-09-17", BN)]}}).encode()
            )),
            [date(2019, 9, 17)],
        )

    def test_a_date_is_declared_available_at_four_pm_on_the_next_business_day(self):
        rows = by_series(rows_for(operation("2026-01-16", BN)))
        self.assertEqual(
            rows["repo_accepted"][date(2026, 1, 16)].available_at,
            datetime(2026, 1, 20, 16, 0, tzinfo=NEW_YORK),
        )

    def test_a_rewritten_record_is_read_after_its_rewrite(self):
        rows = by_series(
            rows_for(operation("2021-09-03", 4_000_000, written="2021-09-16 10:53:00"))
        )
        self.assertEqual(
            rows["repo_accepted"][date(2021, 9, 3)].available_at,
            datetime(2021, 9, 16, 10, 53, tzinfo=NEW_YORK),
        )

    def test_a_kept_operation_without_an_amount_is_refused(self):
        broken = operation("2020-03-17", 1)
        broken["totalAmtAccepted"] = None
        with self.assertRaises(ValueError):
            rows_for(broken)


class TestTradeTests(unittest.TestCase):
    """#802: a Fed repo operation is no take-up only if it is a test trade (Eleonora, 15 October 2026, ruling on #802).

    This replaces #743's floor ("under $0.1 bn is no take-up"), which also zeroed about 40 days of $8-97 mn
    take-up that carry no test note. The rule: an operation whose note names a small value exercise is
    dropped (`ingest._is_small_value_exercise`, unchanged); otherwise an operation counts as a test trade
    only if it accepted at most `ingest.TEST_TRADE_MAX` (USD 7 million) and a whole number of millions
    (the Desk's $1 mn test trades are round). Every other operation counts in full. The operation still
    happened, so its date keeps a row at zero. One amount, no date, so the rule builds no regime dummy (#672).

    Recorded mutation (CLAUDE.md), 15 October 2026, in a disposable copy:
    `src/repo_model/ingest.py`, `_is_test_trade`, `accepted <= TEST_TRADE_MAX` mutated to `accepted <= 100_000_000`
    (the old floor back). `test_the_dates_the_finding_lists_keep_their_take_up` then fails with
    `AssertionError` (`0.0 != 0.015`: 2024-09-23 reads as no take-up).

    The Standing Repo Facility total `srf_total_accepted` (`ingest._nyfed_srf_rows`) reads the same rule per
    operation (#787, Eleonora's ruling of 15 October 2026): a test trade adds nothing, and its date keeps a row
    at zero. Recorded mutation (CLAUDE.md), 17 October 2026, in a disposable copy: `src/repo_model/ingest.py`,
    `_nyfed_srf_rows`, `totals.get(ref_date, 0) + _effective_accepted(accepted)` mutated to
    `totals.get(ref_date, 0) + accepted` (the $1 mn test trade counted again).
    `test_the_srf_total_reads_the_test_trade_rule` then fails with `AssertionError` (`0.001 != 0.0`).
    """

    def test_a_test_trade_is_at_most_seven_million_dollars(self):
        self.assertEqual(ingest.TEST_TRADE_MAX, 7_000_000)

    def test_a_round_trade_up_to_the_ceiling_is_no_take_up_in_either_era(self):
        rows = by_series(
            rows_for(
                operation("2019-12-18", 5_000_000, rate=1.60),
                operation("2023-12-18", 1_000_000, rate=5.40),
                operation("2023-12-19", 7_000_000, rate=5.40),
                operation("2023-12-18", 1_000_000, term="Term", rate=5.40, maturity="2023-12-20"),
            )
        )
        for day in (date(2019, 12, 18), date(2023, 12, 18), date(2023, 12, 19)):
            self.assertEqual(rows["repo_accepted"][day].value, 0.0, day)
            self.assertEqual(rows["repo_ops_accepting"][day].value, 0.0, day)
            self.assertNotIn(day, rows.get("repo_rate", {}), day)

    def test_a_trade_above_the_ceiling_or_not_round_is_take_up(self):
        rows = by_series(
            rows_for(
                operation("2022-03-16", 8_000_000, rate=0.50),
                operation("2022-03-17", 7_500_000, rate=0.50),
                operation("2022-03-18", 97_000_000, rate=0.60),
                operation("2022-03-21", 3 * BN, rate=0.60),
            )
        )
        self.assertAlmostEqual(rows["repo_accepted"][date(2022, 3, 16)].value, 0.008)
        self.assertAlmostEqual(rows["repo_accepted"][date(2022, 3, 17)].value, 0.0075)
        self.assertAlmostEqual(rows["repo_accepted"][date(2022, 3, 18)].value, 0.097)
        self.assertAlmostEqual(rows["repo_accepted"][date(2022, 3, 21)].value, 3.0)
        self.assertEqual(rows["repo_ops_accepting"][date(2022, 3, 18)].value, 1.0)

    def test_a_test_trade_beside_real_take_up_is_dropped_alone(self):
        rows = by_series(
            rows_for(
                operation("2025-09-10", 9_000_000, rate=4.20),
                operation("2025-09-10", 3_000_000, rate=4.00, term="Term", maturity="2025-09-12"),
            )
        )
        self.assertAlmostEqual(rows["repo_accepted"][date(2025, 9, 10)].value, 0.009)
        self.assertEqual(rows["repo_ops_accepting"][date(2025, 9, 10)].value, 1.0)
        self.assertAlmostEqual(rows["repo_rate"][date(2025, 9, 10)].value, 4.20)

    def test_the_srf_total_reads_the_test_trade_rule(self):
        operations = [
            operation("2025-10-08", 1_000_000),
            operation("2025-10-09", 7_000_000),
            operation("2025-10-10", 8_000_000),
            operation("2025-10-14", 7_500_000),
            operation("2025-10-15", 1_000_000),
            operation("2025-10-15", 2 * BN),
            operation("2025-10-16", 61_000_000, note="Small Value Exercise (SVE)"),
        ]
        payload = json.dumps({"repo": {"operations": operations}}).encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "srf.json"
            path.write_bytes(payload)
            artifact = SnapshotArtifact(
                source_id=ingest.NYFED_SRF_SOURCE_ID,
                path=path,
                retrieved_at="2026-10-08T20:51:05+00:00",
                sha256=hashlib.sha256(payload).hexdigest(),
                url=ingest.NYFED_RP_RESULTS_URL,
                byte_count=len(payload),
            )
            rows = {row.ref_date: row.value for row in ingest._nyfed_srf_rows(artifact, payload)}
        self.assertEqual(rows[date(2025, 10, 8)], 0.0)
        self.assertEqual(rows[date(2025, 10, 9)], 0.0)
        self.assertAlmostEqual(rows[date(2025, 10, 10)], 0.008)
        self.assertAlmostEqual(rows[date(2025, 10, 14)], 0.0075)
        self.assertAlmostEqual(rows[date(2025, 10, 15)], 2.0)
        self.assertNotIn(date(2025, 10, 16), rows)

    def test_the_dates_the_finding_lists_keep_their_take_up(self):
        series = fed_liquidity.series_from_snapshots(SNAPSHOTS, datetime(2026, 9, 8, 21, 31, 42, tzinfo=ZoneInfo("UTC")))
        accepted = series["repo_accepted"]
        for day, expected in (
            (date(2024, 9, 23), 0.015),
            (date(2024, 9, 24), 0.057),
            (date(2024, 12, 23), 0.050),
            (date(2025, 9, 10), 0.009),
            (date(2025, 9, 22), 0.030),
            (date(2025, 10, 6), 0.020),
        ):
            self.assertAlmostEqual(accepted[day], expected, msg=str(day))

    def test_a_day_of_test_trades_resets_nothing_in_days_since_positive(self):
        panel = [DailyObservation(date(2023, 12, d), {"iorb": 5.4}) for d in (14, 15, 18, 19)]
        ops = [
            operation("2023-12-14", 2 * BN, rate=5.5),
            operation("2023-12-18", 1_000_000, rate=5.5),
        ]
        with mock.patch.object(
            fed_liquidity, "series_from_snapshots",
            return_value=ingest_series(ops),
        ):
            rows, _ = fed_liquidity.assemble(
                panel, SNAPSHOTS, cutoff=datetime(2026, 10, 9, tzinfo=NEW_YORK),
                end=date(2023, 12, 19), coverage_end=date(2026, 1, 1),
            )
        self.assertEqual([r.values["fed_repo_days_since_positive"] for r in rows], [0.0, 1.0, 2.0, 3.0])


def ingest_series(operations):
    """`series_from_snapshots`'s shape, built from operation records as the parser reads them."""

    out = {}
    for row in rows_for(*operations):
        out.setdefault(row.series_id, {})[row.ref_date] = row.value
    return out


class BuildColumnsTests(unittest.TestCase):
    def rows(self, amounts):
        days = [date(2024, 1, 1) + timedelta(days=i) for i in range(len(amounts))]
        return [DailyObservation(d, {"fed_repo_accepted": a}) for d, a in zip(days, amounts)]

    def test_the_level_is_logged_and_its_change_is_the_difference(self):
        built = fed_liquidity.build_columns(self.rows([0.0, 2.0, 2.0, 0.5]))
        self.assertEqual(built[0].values["fed_repo_log_accepted"], 0.0)
        self.assertAlmostEqual(built[1].values["fed_repo_log_accepted"], 1.0986122886681098)
        self.assertEqual(built[0].values["fed_repo_log_accepted_change"], 0.0)
        self.assertAlmostEqual(built[1].values["fed_repo_log_accepted_change"], 1.0986122886681098)
        self.assertEqual(built[2].values["fed_repo_log_accepted_change"], 0.0)
        self.assertLess(built[3].values["fed_repo_log_accepted_change"], 0.0)

    def test_days_since_a_non_zero_take_up_counts_rows_and_is_capped(self):
        cap = fed_liquidity.DAYS_SINCE_CAP
        built = fed_liquidity.build_columns(self.rows([0.0, 1.0, 0.0, 0.0, 3.0]))
        self.assertEqual(
            [r.values["fed_repo_days_since_positive"] for r in built], [float(cap), 0.0, 1.0, 2.0, 0.0]
        )
        long = fed_liquidity.build_columns(self.rows([1.0] + [0.0] * (cap + 5)))
        self.assertEqual(long[-1].values["fed_repo_days_since_positive"], float(cap))

    def test_a_derived_value_does_not_move_with_what_follows(self):
        short = fed_liquidity.build_columns(self.rows([0.0, 1.0, 0.0]))
        longer = fed_liquidity.build_columns(self.rows([0.0, 1.0, 0.0, 9.0, 9.0]))
        for a, b in zip(short, longer):
            for name in fed_liquidity.DERIVED_COLUMNS:
                self.assertEqual(a.values[name], b.values[name])

    def test_a_missing_day_is_missing_in_every_derived_column_when_the_caller_allows_it(self):
        built = fed_liquidity.build_columns(self.rows([1.0, None, 0.0, 2.0]), allow_missing=True)
        for name in ("fed_repo_log_accepted", "fed_repo_log_accepted_change"):
            self.assertIsNone(built[1].values[name])
        # The change needs the previous row too, so the day after a missing one has none.
        self.assertIsNone(built[2].values["fed_repo_log_accepted_change"])
        self.assertAlmostEqual(built[3].values["fed_repo_log_accepted_change"], 1.0986122886681098)
        # Rows since a positive take-up: a missing row is not a positive one.
        self.assertEqual([r.values["fed_repo_days_since_positive"] for r in built], [0.0, 1.0, 2.0, 0.0])

    def test_a_missing_or_negative_take_up_is_refused_not_guessed(self):
        for bad in (None, -1.0, float("nan")):
            with self.assertRaises(ValueError):
                fed_liquidity.build_columns(self.rows([bad]))


def weekdays(start, count):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def switched_on():
    fields = dict(fed_liquidity.ALL_COLUMN_FIELDS)
    return mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
            }
        ),
    )


class AsOfTests(unittest.TestCase):
    """A value published after the decision instant is invisible (#425, acceptance criterion 2).

    A date's repo results are declared available at 16:00 New York time on the next business
    day (`nyfed_repo_ops.release_lag`). A forecast made at the 16:00 decision of Thursday
    2026-01-22 therefore reads Wednesday the 21st's take-up (public at 16:00 that very day) and
    never Thursday's own, public at 16:00 on the Friday.

    Recorded mutation (CLAUDE.md), 8 October 2026, in a disposable copy:
    `metadata/sources_measurement.json`, `nyfed_repo_ops.release_lag`, `"days": 1` mutated to
    `"days": 0` (a date's results public at 16:00 on the date itself).
    `test_a_value_published_after_the_decision_is_invisible` then fails with `AssertionError`
    (`datetime.date(2026, 1, 22) != datetime.date(2026, 1, 21)`): the forecast reads the take-up
    of its own decision day, public only afterwards.
    """

    DATES = weekdays(date(2026, 1, 5), 40)
    DECISION = datetime(2026, 1, 1, 16, 0).time()

    def rule(self, features):
        return InformationRule(REGISTRY, tuple(features), decision_time=self.DECISION)

    def test_a_value_published_after_the_decision_is_invisible(self):
        with switched_on():
            information = self.rule(["spread_bps", "fed_repo_accepted"])
            scored = self.DATES.index(date(2026, 1, 23))
            info = information.information_set(self.DATES, scored)
            (read,) = [r for r in info.reads if r.feature == "fed_repo_accepted"]
            self.assertEqual(self.DATES[read.row], date(2026, 1, 21))
            self.assertEqual(read.available_at, datetime(2026, 1, 22, 16, 0))
            thursday = self.DATES.index(date(2026, 1, 22))
            self.assertGreater(
                information.availability(self.DATES, read.fields, thursday), info.decision_instant
            )
            forced = info._replace(
                reads=tuple(r._replace(row=thursday) if r.feature == "fed_repo_accepted" else r for r in info.reads)
            )
            with self.assertRaises(LookAheadError):
                information.check(self.DATES, forced)

    def test_every_column_passes_both_guards(self):
        with switched_on():
            information = self.rule(["spread_bps", *fed_liquidity.COLUMN_FIELDS])
            for scored in range(15, len(self.DATES)):
                information.check(self.DATES, information.information_set(self.DATES, scored))

    def test_a_rate_spread_waits_for_its_slowest_field(self):
        with switched_on():
            information = self.rule(["spread_bps", "fed_repo_accepted", "fed_repo_rate_iorb_bps"])
            scored = self.DATES.index(date(2026, 1, 30))
            info = information.information_set(self.DATES, scored)
            accepted = [r for r in info.reads if r.feature == "fed_repo_accepted"][0]
            rate = [r for r in info.reads if r.feature == "fed_repo_rate_iorb_bps"][0]
            self.assertLessEqual(rate.row, accepted.row)


class SnapshotTests(unittest.TestCase):
    """The tracked snapshots are the Desk's responses, saved with their checksums (#425, criterion 1)."""

    def manifests(self):
        return [load_snapshot_manifest(path) for path in sorted(SNAPSHOTS.rglob("*.manifest.json"))]

    def test_every_year_from_2018_to_2026_is_saved_and_checksummed(self):
        manifests = self.manifests()
        self.assertEqual(
            sorted(m.url.split("startDate=")[1][:4] for m in manifests), [str(y) for y in range(2018, 2027)]
        )
        for m in manifests:
            self.assertEqual(m.source_id, ingest.NYFED_REPO_OPS_SOURCE_ID)
            self.assertEqual(hashlib.sha256(m.path.read_bytes()).hexdigest(), m.sha256)

    def test_the_september_2019_and_march_2020_operations_are_read(self):
        series = fed_liquidity.series_from_snapshots(SNAPSHOTS, datetime(2026, 9, 8, 21, 31, 42, tzinfo=ZoneInfo("UTC")))
        self.assertAlmostEqual(series["repo_accepted"][date(2019, 9, 17)], 53.15)
        self.assertGreater(series["repo_accepted"][date(2020, 3, 17)], 100.0)

    def test_no_row_is_published_before_its_publication_time_or_its_declaration(self):
        artifacts = self.manifests()
        rows = parse_snapshots(artifacts).rows
        for r in rows:
            declared = datetime.combine(
                ingest._next_business_day(r.ref_date, 1), datetime.min.time().replace(hour=16), tzinfo=NEW_YORK
            )
            self.assertGreaterEqual(r.available_at, min(declared, datetime.fromisoformat("2026-10-08T20:51:05+00:00")))
        publication = {}
        for artifact in artifacts:
            publication.update(ingest.repo_operation_publication_times(artifact.path.read_bytes()))
        accepted = {r.ref_date: r for r in rows if r.series_id == "repo_accepted"}
        for day, written in publication.items():
            self.assertGreaterEqual(accepted[day].available_at, written)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_carries_each_candidate_as_defined_here(self):
        document = dict(pj.load_declaration(DECLARATION).candidates)
        for name in fed_liquidity.CANDIDATES:
            for key, value in fed_liquidity.declaration_entry(name).items():
                self.assertEqual(document[name][key], value, f"{name}.{key}")
            self.assertNotIn("cutoffs", document[name])
        pj.load_declaration(DECLARATION)

    def test_the_columns_are_off_in_every_published_declaration(self):
        for column in fed_liquidity.ALL_COLUMN_FIELDS:
            self.assertNotIn(column, contract.FEATURE_FIELDS)
        published = json.loads((ROOT / "metadata" / "sources.json").read_text())
        self.assertNotIn(ingest.NYFED_REPO_OPS_SOURCE_ID, published)
        self.assertNotIn(fed_liquidity.SAME_DAY_SOURCE_ID, published)

    def test_the_control_is_the_same_classifier_without_the_inputs(self):
        control = fed_liquidity.features_at_horizon("hierarchical_logistic_srf", 1)
        base = set(dict(pj.load_declaration(DECLARATION).candidates)["hierarchical_logistic"]["features"])
        self.assertEqual(set(control) - base, set(fed_liquidity.CANDIDATES["hierarchical_logistic_srf"]))
        self.assertTrue(base <= set(control))


class SameDayAvailabilityTests(unittest.TestCase):
    """The same-day reading of a repo operation date's availability (#442, criterion 1).

    A date is available at 16:00 ET on its own date, unless its record was written later: then
    at the write time rounded up to the next decision instant (16:00 ET on a business day). A
    record written after the conservative declaration (16:00 on the next business day) stays on
    the conservative reading, at its write time, because a rewrite cannot show when the first
    publication was.

    Recorded mutation (CLAUDE.md), 9 October 2026, in a disposable copy:
    `src/repo_model/ingest.py`, `repo_operation_same_day_available_at`,
    `if written is None or written <= decision:` mutated to
    `if written is None or written <= decision + timedelta(minutes=30):` (a record written at
    16:10 read at that day's 16:00). `test_a_row_written_at_ten_past_four_is_invisible_to_that_days_decision`
    then fails with `AssertionError` (`datetime(2021, 12, 28, 16, 0) != datetime(2021, 12, 29, 16, 0)`),
    and so does `AssemblyTests.test_a_row_written_after_the_decision_reads_as_zero_that_day`.
    """

    def at(self, day, clock, *, zone=NEW_YORK):
        return datetime.combine(date.fromisoformat(day), datetime.strptime(clock, "%H:%M:%S").time(), tzinfo=zone)

    def test_a_row_written_at_the_close_is_available_at_four_on_its_own_date(self):
        got = ingest.repo_operation_same_day_available_at(date(2026, 1, 16), self.at("2026-01-16", "13:46:19"))
        self.assertEqual(got, self.at("2026-01-16", "16:00:00"))
        self.assertEqual(
            ingest.repo_operation_same_day_available_at(date(2026, 1, 16), self.at("2026-01-16", "16:00:00")),
            self.at("2026-01-16", "16:00:00"),
        )
        self.assertEqual(
            ingest.repo_operation_same_day_available_at(date(2026, 1, 16), None), self.at("2026-01-16", "16:00:00")
        )

    def test_a_row_written_at_ten_past_four_is_invisible_to_that_days_decision(self):
        got = ingest.repo_operation_same_day_available_at(date(2021, 12, 28), self.at("2021-12-28", "16:10:30"))
        self.assertEqual(got, self.at("2021-12-29", "16:00:00"))
        self.assertGreater(got, self.at("2021-12-28", "16:00:00"))

    def test_a_late_row_is_rounded_up_to_the_next_business_days_decision(self):
        evening = ingest.repo_operation_same_day_available_at(date(2023, 3, 22), self.at("2023-03-22", "17:22:00"))
        self.assertEqual(evening, self.at("2023-03-23", "16:00:00"))
        next_morning = ingest.repo_operation_same_day_available_at(date(2023, 5, 11), self.at("2023-05-12", "09:29:30"))
        self.assertEqual(next_morning, self.at("2023-05-12", "16:00:00"))
        friday = ingest.repo_operation_same_day_available_at(date(2026, 1, 16), self.at("2026-01-16", "17:00:00"))
        self.assertEqual(friday, self.at("2026-01-20", "16:00:00"))  # the Monday between is a holiday

    def test_a_rewrite_after_the_conservative_declaration_stays_conservative(self):
        for day, written in (("2021-09-03", "2021-09-16 10:53:00"), ("2021-09-10", "2021-09-16 10:46:30")):
            stamp = datetime.fromisoformat(written).replace(tzinfo=NEW_YORK)
            self.assertEqual(ingest.repo_operation_same_day_available_at(date.fromisoformat(day), stamp), stamp)

    def test_the_tracked_snapshots_have_exactly_the_five_late_dates_the_provenance_names(self):
        late = {}
        for path in sorted(SNAPSHOTS.rglob("*.manifest.json")):
            artifact = load_snapshot_manifest(path)
            for day, written in ingest.repo_operation_publication_times(artifact.path.read_bytes()).items():
                if ingest.repo_operation_same_day_available_at(day, written) > self.at(day.isoformat(), "16:00:00"):
                    late[day] = written
        self.assertEqual(
            sorted(late),
            [date(2021, 9, 3), date(2021, 9, 10), date(2021, 12, 28), date(2023, 3, 22), date(2023, 5, 11)],
        )


class AssemblyTests(unittest.TestCase):
    """The panel columns of the two readings, from a snapshot directory (#442)."""

    def directory(self, *operations):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        root = Path(holder.name)
        (root / "nyfed_repo_ops").mkdir()
        payload = json.dumps({"repo": {"operations": list(operations)}}).encode()
        (root / "nyfed_repo_ops" / "ops.json").write_bytes(payload)
        manifest = {
            "byte_count": len(payload),
            "path": "nyfed_repo_ops/ops.json",
            "retrieved_at": "2026-10-08T20:51:05+00:00",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "source_id": ingest.NYFED_REPO_OPS_SOURCE_ID,
            "url": ingest.NYFED_RP_RESULTS_URL,
        }
        (root / "nyfed_repo_ops" / "ops.json.manifest.json").write_text(json.dumps(manifest))
        return root

    DAYS = weekdays(date(2026, 1, 5), 6)
    CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=ZoneInfo("UTC"))

    def panel(self):
        return [DailyObservation(d, {"iorb": 3.65}) for d in self.DAYS]

    def operations(self):
        return (
            operation("2026-01-05", 2 * BN, rate=3.70),
            operation("2026-01-06", 3 * BN, rate=3.70, written="2026-01-06 16:10:30"),
            operation("2026-01-07", 4 * BN, rate=3.70, written="2026-01-08 09:29:30"),
            operation("2026-01-08", 5 * BN, rate=3.70, written="2026-01-16 10:53:00"),
        )

    def assemble(self, reading):
        return fed_liquidity.assemble(
            self.panel(), self.directory(*self.operations()), cutoff=self.CUTOFF, end=date(2026, 12, 31), reading=reading,
            coverage_end=date(2026, 12, 31),
        )

    def test_the_conservative_reading_is_unchanged_by_the_second_one(self):
        rows, summary = self.assemble(fed_liquidity.CONSERVATIVE)
        self.assertEqual([r.values["fed_repo_accepted"] for r in rows[:4]], [2.0, 3.0, 4.0, 5.0])
        self.assertNotIn("fed_repo_accepted_sameday", rows[0].values)
        self.assertNotIn("dates_withheld", summary)

    def test_a_row_written_after_the_decision_reads_as_zero_that_day(self):
        rows, summary = self.assemble(fed_liquidity.SAME_DAY)
        sameday = [r.values["fed_repo_accepted_sameday"] for r in rows[:5]]
        # 5 Jan written at the close: public at that day's 16:00. 6 Jan written at 16:10, 7 Jan the
        # next morning and 8 Jan nine days later: none public at its own date's 16:00.
        self.assertEqual(sameday, [2.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(rows[1].values["fed_repo_log_accepted_sameday"], 0.0)
        self.assertEqual(rows[1].values["fed_repo_ops_sameday"], 0.0)
        self.assertEqual(rows[1].values["fed_repo_rate_iorb_bps_sameday"], 0.0)
        self.assertEqual(summary["dates_with_an_operation"], 1)
        self.assertEqual(summary["dates_withheld_from_the_same_day_reading"], 3)
        self.assertAlmostEqual(rows[0].values["fed_repo_rate_iorb_bps_sameday"], (3.70 - 3.65) * 100.0)

    def test_the_two_readings_share_a_panel(self):
        rows, _ = self.assemble(fed_liquidity.CONSERVATIVE)
        both, _ = fed_liquidity.assemble(
            rows, self.directory(*self.operations()), cutoff=self.CUTOFF, end=date(2026, 12, 31),
            reading=fed_liquidity.SAME_DAY, coverage_end=date(2026, 12, 31),
        )
        self.assertEqual(both[0].values["fed_repo_accepted"], both[0].values["fed_repo_accepted_sameday"])
        self.assertEqual(both[1].values["fed_repo_accepted"], 3.0)
        self.assertEqual(both[1].values["fed_repo_accepted_sameday"], 0.0)


class SameDayAsOfTests(unittest.TestCase):
    """Both guards hold under the same-day reading (#442, criterion 1).

    `nyfed_repo_ops_sameday` declares a date's results public at 16:00 on the date itself, so the
    forecast of 23 January (decided at 16:00 on the 22nd) reads the 22nd's take-up, one row later
    than the conservative reading, and never the 23rd's own.

    Recorded mutation (CLAUDE.md), 9 October 2026, in a disposable copy:
    `metadata/sources_measurement.json`, `nyfed_repo_ops_sameday.release_lag`, `"days": 0` mutated to
    `"days": 1` (the conservative lag). `test_the_forecast_reads_the_decision_days_take_up` then fails
    with `AssertionError` (`datetime.date(2026, 1, 21) != datetime.date(2026, 1, 22)`).
    """

    DATES = weekdays(date(2026, 1, 5), 40)
    DECISION = datetime(2026, 1, 1, 16, 0).time()

    def rule(self, features):
        return InformationRule(REGISTRY, tuple(features), decision_time=self.DECISION)

    def test_the_forecast_reads_the_decision_days_take_up(self):
        with switched_on():
            information = self.rule(["spread_bps", "fed_repo_accepted_sameday"])
            info = information.information_set(self.DATES, self.DATES.index(date(2026, 1, 23)))
            (read,) = [r for r in info.reads if r.feature == "fed_repo_accepted_sameday"]
            self.assertEqual(self.DATES[read.row], date(2026, 1, 22))
            self.assertEqual(read.available_at, datetime(2026, 1, 22, 16, 0))

    def test_leakage_guard_a_read_of_the_scored_day_raises(self):
        with switched_on():
            information = self.rule(["spread_bps", "fed_repo_accepted_sameday"])
            scored = self.DATES.index(date(2026, 1, 23))
            info = information.information_set(self.DATES, scored)
            forced = info._replace(
                reads=tuple(
                    r._replace(row=scored) if r.feature == "fed_repo_accepted_sameday" else r for r in info.reads
                )
            )
            with self.assertRaises(LookAheadError):
                information.check(self.DATES, forced)

    def test_staleness_guard_an_older_read_raises(self):
        with switched_on():
            information = self.rule(["spread_bps", "fed_repo_accepted_sameday"])
            scored = self.DATES.index(date(2026, 1, 23))
            info = information.information_set(self.DATES, scored)
            older = info._replace(
                reads=tuple(
                    r._replace(row=r.row - 1) if r.feature == "fed_repo_accepted_sameday" else r for r in info.reads
                )
            )
            with self.assertRaises(StaleReadError):
                information.check(self.DATES, older)

    def test_every_same_day_column_passes_both_guards(self):
        with switched_on():
            information = self.rule(["spread_bps", *fed_liquidity.COLUMN_FIELDS_SAME_DAY])
            for scored in range(15, len(self.DATES)):
                information.check(self.DATES, information.information_set(self.DATES, scored))


class SameDayDeclarationTests(unittest.TestCase):
    def test_the_published_srf_declaration_is_not_changed(self):
        published = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))["nyfed_srf"]["release_lag"]
        self.assertEqual((published["days"], published["available_time"]), (1, "16:00"))
        self.assertEqual(REGISTRY["nyfed_repo_ops"]["release_lag"]["days"], 1)
        self.assertEqual(REGISTRY[fed_liquidity.SAME_DAY_SOURCE_ID]["release_lag"]["days"], 0)

    def test_each_same_day_candidate_differs_from_its_counterpart_only_in_the_reading(self):
        document = dict(pj.load_declaration(DECLARATION).candidates)
        for name, counterpart in (
            ("hierarchical_logistic_srf_sameday", "hierarchical_logistic_srf"),
            ("hierarchical_logistic_fed_repo_sameday", "hierarchical_logistic_fed_repo"),
        ):
            self.assertIn(name, fed_liquidity.CANDIDATES)
            for key, value in fed_liquidity.declaration_entry(name).items():
                self.assertEqual(document[name][key], value, f"{name}.{key}")
            renamed = {
                f"{c}{fed_liquidity.SAME_DAY_SUFFIX}" if c in fed_liquidity.CANDIDATES[counterpart] else c
                for c in document[counterpart]["features"]
            }
            self.assertEqual(set(document[name]["features"]), renamed)
            self.assertEqual(document[name]["calibration"], document[counterpart]["calibration"])
            self.assertNotIn("cutoffs", document[name])


def snapshot_directory(case, *files, urls=None, retrieved="2026-10-08T20:51:05+00:00"):
    """A snapshot directory with one `nyfed_repo_ops` file per list of operations."""

    holder = tempfile.TemporaryDirectory()
    case.addCleanup(holder.cleanup)
    root = Path(holder.name)
    (root / "nyfed_repo_ops").mkdir()
    for number, operations in enumerate(files):
        payload = json.dumps({"repo": {"operations": list(operations)}}).encode()
        name = f"ops{number}.json"
        (root / "nyfed_repo_ops" / name).write_bytes(payload)
        manifest = {
            "byte_count": len(payload),
            "path": f"nyfed_repo_ops/{name}",
            "retrieved_at": retrieved,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "source_id": ingest.NYFED_REPO_OPS_SOURCE_ID,
            "url": (urls or {}).get(number, ingest.NYFED_RP_RESULTS_URL),
        }
        (root / "nyfed_repo_ops" / f"{name}.manifest.json").write_text(json.dumps(manifest))
    return root


def outstanding_rows(case, *files):
    root = snapshot_directory(case, *files)
    parsed = parse_snapshots([load_snapshot_manifest(p) for p in sorted(root.rglob("*.manifest.json"))])
    return by_series(parsed.rows)


class TermOutstandingTests(unittest.TestCase):
    """`repo_term_outstanding`: the term repos settled and not yet matured, per business day (#659, item 3).

    USD billions of term repos with settlement <= d < maturity on each business day d the
    snapshots cover, small-value exercises and the operations before the facility excluded as for
    `repo_accepted`; 0.0 on a covered business day with nothing outstanding. It is read across the
    snapshot files, since a term repo struck in December matures in January's file. Its
    `available_at` is the date's own (the later of the declaration and the Desk's recorded
    publication time) and never earlier than that of any operation that contributes to it.

    Recorded mutation (CLAUDE.md), 13 October 2026, in a disposable copy:
    `src/repo_model/ingest.py`, `_nyfed_repo_term_outstanding_rows`,
    `available_at = max([instant(day)] + [instant(t[0]) for t in contributing])` mutated to
    `available_at = instant(day)` (a rewritten earlier operation ignored).
    `test_an_outstanding_amount_is_never_public_before_a_rewritten_contributor` then fails with
    `AssertionError` (`datetime(2020, 3, 19, 16, 0) != datetime(2020, 4, 1, 9, 0)`): the amount that
    includes a record rewritten on 1 April is read on 19 March.
    """

    OVERNIGHT = ("2020-03-16", "2020-04-02")

    def ops(self, *extra):
        return [operation(day, BN) for day in self.OVERNIGHT] + list(extra)

    def test_the_amount_is_what_has_settled_and_not_matured(self):
        rows = outstanding_rows(
            self,
            self.ops(
                operation("2020-03-17", 60 * BN, term="Term", settle="2020-03-17", maturity="2020-03-31"),
                operation("2020-03-18", 40 * BN, term="Term", settle="2020-03-19", maturity="2020-03-26"),
                operation("2020-03-17", 99 * BN),  # overnight: not a term repo
                operation("2020-03-17", 98 * BN, kind="Reverse Repo", term="Term", maturity="2020-04-17"),
                operation("2020-03-17", 25_000_000, term="Term", maturity="2020-04-14", note="Small Value Exercise"),
            ),
        )["repo_term_outstanding"]
        got = {d.isoformat(): r.value for d, r in rows.items()}
        self.assertEqual(got["2020-03-16"], 0.0)
        self.assertEqual(got["2020-03-17"], 60.0)
        self.assertEqual(got["2020-03-18"], 60.0)  # the 40bn is struck but not yet settled
        self.assertEqual(got["2020-03-19"], 100.0)
        self.assertEqual(got["2020-03-25"], 100.0)
        self.assertEqual(got["2020-03-26"], 60.0)  # matures on the 26th: not outstanding on it
        self.assertEqual(got["2020-03-30"], 60.0)
        self.assertEqual(got["2020-03-31"], 0.0)
        self.assertEqual(got["2020-04-02"], 0.0)
        self.assertNotIn("2020-03-21", got)  # a Saturday
        self.assertEqual(sorted(got)[0], "2020-03-16")
        self.assertEqual(sorted(got)[-1], "2020-04-02")

    def test_a_term_repo_struck_in_one_file_is_outstanding_in_the_next(self):
        december = [operation("2020-12-28", BN), operation("2020-12-29", 28 * BN, term="Term", maturity="2021-01-26")]
        january = [operation("2021-01-04", BN), operation("2021-01-29", BN)]
        rows = outstanding_rows(self, december, january)["repo_term_outstanding"]
        self.assertEqual(rows[date(2020, 12, 30)].value, 28.0)
        self.assertEqual(rows[date(2021, 1, 4)].value, 28.0)
        self.assertEqual(rows[date(2021, 1, 25)].value, 28.0)
        self.assertEqual(rows[date(2021, 1, 26)].value, 0.0)

    def test_an_operation_before_the_facility_is_not_outstanding(self):
        rows = outstanding_rows(
            self,
            [
                operation("2019-05-08", 65_000_000, term="Term", maturity="2019-05-10"),
                operation("2019-09-17", BN),
                operation("2019-09-19", BN),
            ],
        )["repo_term_outstanding"]
        self.assertEqual(min(rows), date(2019, 9, 17))
        self.assertEqual({r.value for r in rows.values()}, {0.0})

    def test_an_outstanding_amount_is_published_with_its_date(self):
        files = [self.ops(operation("2020-03-17", 60 * BN, term="Term", maturity="2020-03-31"))]
        parsed = outstanding_rows(self, *files)
        for day, row in parsed["repo_term_outstanding"].items():
            if day in parsed["repo_accepted"]:
                self.assertEqual(row.available_at, parsed["repo_accepted"][day].available_at, day)

    def test_an_outstanding_amount_is_never_public_before_a_rewritten_contributor(self):
        rewritten = operation(
            "2020-03-17", 60 * BN, term="Term", maturity="2020-03-31", written="2020-04-01 09:00:00"
        )
        rows = outstanding_rows(self, self.ops(rewritten, operation("2020-03-18", BN)))
        self.assertEqual(rows["repo_accepted"][date(2020, 3, 17)].available_at, datetime(2020, 4, 1, 9, 0, tzinfo=NEW_YORK))
        # The 18th's own results were public at 16:00 on the 19th, but the 60bn in it was not.
        self.assertEqual(rows["repo_accepted"][date(2020, 3, 18)].available_at, datetime(2020, 3, 19, 16, 0, tzinfo=NEW_YORK))
        self.assertEqual(
            rows["repo_term_outstanding"][date(2020, 3, 18)].available_at, datetime(2020, 4, 1, 9, 0, tzinfo=NEW_YORK)
        )
        self.assertEqual(rows["repo_term_outstanding"][date(2020, 3, 18)].value, 60.0)

    def test_a_term_operation_without_valid_dates_is_refused(self):
        for settle, maturity in (("not a date", "2020-03-31"), ("2020-03-17", "2020-03-17"), ("2020-03-17", "2020-03-16")):
            broken = operation("2020-03-17", BN, term="Term")
            broken["settlementDate"], broken["maturityDate"] = settle, maturity
            with self.assertRaises(ValueError):
                outstanding_rows(self, self.ops(broken))


class MissingAndCoverageTests(unittest.TestCase):
    """Missing days, the facility's start and the snapshots' last date (#659, items 1, 2 and 4).

    * Before 2019-09-17 no Fed repo was offered to the market: a date with no operation is a
      structural zero, and the six test operations of $64-66m are not take-up.
    * From 2019-09-17 to the day before the Standing Repo Facility (2021-07-28) a panel date with
      no operation is **missing**, not zero. From the facility's first day a date with none is zero.
    * A panel date after the snapshots' last date (`nyfed_repo_ops.coverage_end`) is refused
      (`StaleReadError`), never read as zero.

    Recorded mutation (CLAUDE.md), 13 October 2026, in a disposable copy:
    `src/repo_model/fed_liquidity.py`, `assemble`, `if row.date > coverage_end:` mutated to
    `if False:` (a date past the coverage read as zero take-up).
    `test_a_date_after_the_snapshots_last_date_is_refused_not_read_as_zero` then fails with
    `AssertionError: StaleReadError not raised`.

    Recorded mutation, same day, `assemble`:
    `if in_window and row.date not in full[NYFED_REPO_OPS_ACCEPTED]:` mutated to `if False:` (a window
    date with no operation read as zero).
    `test_a_day_with_no_operation_between_the_facility_start_and_the_srf_is_missing` then fails with
    `AssertionError: 0.0 is not None : fed_repo_accepted`.
    """

    CUTOFF = datetime(2026, 9, 8, 21, 31, 42, tzinfo=ZoneInfo("UTC"))
    COVERAGE_END = date(2025, 12, 31)

    def directory(self, *operations):
        return snapshot_directory(self, list(operations))

    def assemble(self, days, *operations, **kwargs):
        panel = [DailyObservation(d, {"iorb": 1.55}) for d in days]
        kwargs.setdefault("end", date(2030, 12, 31))
        kwargs.setdefault("coverage_end", self.COVERAGE_END)
        return fed_liquidity.assemble(panel, self.directory(*operations), cutoff=self.CUTOFF, **kwargs)

    def test_a_day_with_no_operation_between_the_facility_start_and_the_srf_is_missing(self):
        days = weekdays(date(2020, 3, 16), 5)
        rows, summary = self.assemble(days, operation("2020-03-16", 2 * BN, rate=1.6), operation("2020-03-19", BN, rate=1.6))
        missing = rows[1]
        for name in ("fed_repo_accepted", "fed_repo_submitted", "fed_repo_rate_iorb_bps", "fed_repo_ops",
                     "fed_repo_log_accepted", "fed_repo_log_accepted_change"):
            self.assertIsNone(missing.values[name], name)
        self.assertEqual(rows[0].values["fed_repo_accepted"], 2.0)
        self.assertEqual(rows[3].values["fed_repo_accepted"], 1.0)
        self.assertIsNone(rows[3].values["fed_repo_log_accepted_change"])  # needs the previous row, which is missing
        self.assertEqual(summary["dates_read_as_missing"], 3)

    def test_a_day_with_no_operation_before_the_facility_is_a_structural_zero(self):
        rows, summary = self.assemble([date(2018, 6, 4), date(2019, 6, 3), date(2019, 9, 13)], operation("2020-03-16", BN))
        for row in rows:
            self.assertEqual(row.values["fed_repo_accepted"], 0.0)
            self.assertEqual(row.values["fed_repo_ops"], 0.0)
        self.assertEqual(summary["dates_read_as_missing"], 0)

    def test_a_day_with_no_operation_from_the_srf_on_is_zero(self):
        rows, summary = self.assemble([date(2021, 7, 27), date(2021, 7, 28), date(2021, 7, 29), date(2022, 1, 17)], operation("2020-03-16", BN))
        self.assertEqual([r.values["fed_repo_accepted"] for r in rows], [None, None, 0.0, 0.0])
        self.assertEqual(summary["dates_read_as_missing"], 2)

    def test_the_facility_dates_are_the_published_ones(self):
        self.assertEqual(ingest.REPO_FACILITY_START, date(2019, 9, 17))
        self.assertEqual(ingest.SRF_INCEPTION, date(2021, 7, 29))
        for source in ("nyfed_repo_ops", fed_liquidity.SAME_DAY_SOURCE_ID):
            self.assertEqual(REGISTRY[source]["facility_start"], "2019-09-17")

    def test_a_date_after_the_snapshots_last_date_is_refused_not_read_as_zero(self):
        with self.assertRaises(StaleReadError):
            self.assemble([date(2025, 12, 31), date(2026, 1, 2)], operation("2025-12-31", BN))
        with self.assertRaises(StaleReadError):
            self.assemble([date(2026, 1, 2)], operation("2025-12-31", BN), end=date(2026, 1, 2))
        rows, _ = self.assemble([date(2025, 12, 31), date(2026, 1, 2)], operation("2025-12-31", BN), end=date(2025, 12, 31))
        self.assertEqual([r.date for r in rows], [date(2025, 12, 31)])

    def test_the_default_coverage_end_is_the_declared_one(self):
        panel = [DailyObservation(date(2026, 9, 4), {"iorb": 1.55})]
        with self.assertRaises(StaleReadError):
            fed_liquidity.assemble(panel, self.directory(operation("2026-09-03", BN)), cutoff=self.CUTOFF, end=date(2026, 12, 31))
        self.assertEqual(fed_liquidity.declared_coverage_end(), date(2026, 9, 3))

    def test_the_declared_coverage_end_is_the_tracked_snapshots_last_date(self):
        manifests = [load_snapshot_manifest(p) for p in sorted(SNAPSHOTS.rglob("*.manifest.json"))]
        last_requested = max(date.fromisoformat(m.url.split("endDate=")[1]) for m in manifests)
        last_operation = max(
            date.fromisoformat(str(op["operationDate"]))
            for m in manifests
            for op in json.loads(m.path.read_bytes())["repo"]["operations"]
        )
        for source in ("nyfed_repo_ops", fed_liquidity.SAME_DAY_SOURCE_ID):
            declared = date.fromisoformat(REGISTRY[source]["coverage_end"])
            self.assertEqual(declared, last_requested, source)
            self.assertLessEqual(last_operation, declared, source)

    def business_days(self, first, last):
        from repo_model.data import next_business_day

        out, day = [], first
        while day <= last:
            if next_business_day(day - timedelta(days=1), 1) == day:
                out.append(day)
            day += timedelta(days=1)
        return out

    def test_no_business_day_of_the_tracked_snapshots_is_missing(self):
        # The Desk operated on every business day from 2019-09-17, so the missing rule binds no
        # date of the tracked history: nothing that read these columns for 2019-09-17 on changes
        # through it. The six dates before the facility are the only values that moved.
        days = self.business_days(date(2018, 5, 9), self.COVERAGE_END)
        panel = [DailyObservation(d, {"iorb": 1.55}) for d in days]
        rows, summary = fed_liquidity.assemble(panel, SNAPSHOTS, cutoff=self.CUTOFF, end=self.COVERAGE_END)
        self.assertEqual(summary["dates_read_as_missing"], 0)
        self.assertTrue(all(r.values["fed_repo_accepted"] is not None for r in rows))
        self.assertEqual(
            [d.isoformat() for d in days if d < ingest.REPO_FACILITY_START and rows[days.index(d)].values["fed_repo_accepted"]],
            [],
        )

    def test_the_material_use_dates_through_2025_are_unchanged(self):
        # The liquidity repo's H7 stress days are the dates with $1bn or more accepted. The set was
        # taken from the module before #659 and is pinned here by its digest.
        days = self.business_days(date(2018, 5, 9), self.COVERAGE_END)
        panel = [DailyObservation(d, {"iorb": 1.55}) for d in days]
        rows, _ = fed_liquidity.assemble(panel, SNAPSHOTS, cutoff=self.CUTOFF, end=self.COVERAGE_END)
        events = [r.date.isoformat() for r in rows if r.values["fed_repo_accepted"] >= 1.0]
        self.assertEqual(len(events), 221)
        self.assertEqual(
            hashlib.sha256(",".join(events).encode()).hexdigest(),
            "f0c02e01288311993608fd27f937a569f852ec9cde0da90a2b84a2c2ddb4dfaf",
        )


class ExtensionTo2026Tests(unittest.TestCase):
    """The repo-operation snapshots end on 2026-09-03; nothing before 2026 moved (#766, items 2 and 3).

    The 2026 file is the Desk's response for 2026-01-01 to 2026-09-03, fetched on 2026-10-14. Each
    of its dates is available as the earlier years' are (the Desk's write time and the declared
    lag). The published panel stops at 2025-12-31 (`scripts/fed_liquidity.py`, `END`), so no
    published figure moves.

    Recorded mutation, `fed_liquidity.assemble`: `if row.date > coverage_end:` mutated to
    `if row.date > date.fromordinal(coverage_end.toordinal() + 1):`. `test_the_day_after_the_new_last_date_is_refused`
    then fails with `AssertionError: StaleReadError not raised`.
    """

    FETCHED = datetime(2026, 10, 15, 0, 0, tzinfo=ZoneInfo("UTC"))
    LAST = date(2026, 9, 3)
    NEW_SHA = "b9924c1ba41788d9c171ea0150b04fa47fbf5a981ce177601981c2b16bfcd082"

    def manifests(self):
        return [load_snapshot_manifest(p) for p in sorted(SNAPSHOTS.rglob("*.manifest.json"))]

    def test_both_sources_declare_the_new_coverage_end(self):
        for source in ("nyfed_repo_ops", fed_liquidity.SAME_DAY_SOURCE_ID):
            self.assertEqual(REGISTRY[source]["coverage_end"], "2026-09-03", source)
            self.assertEqual(fed_liquidity.declared_coverage_end(source), self.LAST, source)

    def test_the_new_file_is_the_desks_response_with_its_own_manifest(self):
        new = [m for m in self.manifests() if m.url.endswith("startDate=2026-01-01&endDate=2026-09-03")]
        self.assertEqual(len(new), 1)
        self.assertEqual(new[0].sha256, self.NEW_SHA)
        self.assertEqual(hashlib.sha256(new[0].path.read_bytes()).hexdigest(), self.NEW_SHA)
        self.assertEqual(new[0].source_id, "nyfed_repo_ops")
        self.assertEqual(len(self.manifests()), 9)

    def test_a_2026_day_is_read_only_from_its_declared_instant(self):
        # Availability follows the Desk's recorded write time and the declared lag (16:00 ET on the
        # next business day), as for every earlier year; the fetch instant does not set it.
        accepted = fed_liquidity.NYFED_REPO_OPS_ACCEPTED
        early = datetime(2026, 9, 4, 12, 0, tzinfo=NEW_YORK)
        late = datetime(2026, 9, 4, 17, 0, tzinfo=NEW_YORK)
        self.assertNotIn(self.LAST, fed_liquidity.series_from_snapshots(SNAPSHOTS, early)[accepted])
        self.assertIn(self.LAST, fed_liquidity.series_from_snapshots(SNAPSHOTS, late)[accepted])

    def test_2026_days_are_read_after_the_fetch_and_the_last_date_is_readable(self):
        series = fed_liquidity.series_from_snapshots(SNAPSHOTS, self.FETCHED)
        days = [d for d in series[fed_liquidity.NYFED_REPO_OPS_ACCEPTED] if d >= date(2026, 1, 1)]
        self.assertTrue(days)
        self.assertEqual(max(days), self.LAST)
        panel = [DailyObservation(self.LAST, {"iorb": 1.55})]
        rows, _ = fed_liquidity.assemble(panel, SNAPSHOTS, cutoff=self.FETCHED, end=self.LAST)
        self.assertEqual([r.date for r in rows], [self.LAST])

    def test_the_day_after_the_new_last_date_is_refused(self):
        panel = [DailyObservation(date(2026, 9, 4), {"iorb": 1.55})]
        with self.assertRaises(StaleReadError):
            fed_liquidity.assemble(panel, SNAPSHOTS, cutoff=self.FETCHED, end=date(2026, 9, 4))
        with self.assertRaises(StaleReadError):
            fed_liquidity.assemble(
                panel, SNAPSHOTS, cutoff=self.FETCHED, end=date(2026, 9, 4), reading=fed_liquidity.SAME_DAY
            )

    def test_rows_before_2026_read_the_same_without_the_new_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "nyfed_repo_ops"
            root.mkdir()
            for manifest in self.manifests():
                if manifest.sha256 != self.NEW_SHA:
                    (root / manifest.path.name).write_bytes(manifest.path.read_bytes())
                    source = manifest.path.parent / (manifest.path.name + ".manifest.json")
                    (root / source.name).write_bytes(source.read_bytes())
            for reading in (fed_liquidity.CONSERVATIVE, fed_liquidity.SAME_DAY):
                old = fed_liquidity.series_from_snapshots(Path(tmp), self.FETCHED, reading)
                new = fed_liquidity.series_from_snapshots(SNAPSHOTS, self.FETCHED, reading)
                for name, values in old.items():
                    kept = {d: v for d, v in new[name].items() if d < date(2026, 1, 1)}
                    self.assertEqual(kept, {d: v for d, v in values.items() if d < date(2026, 1, 1)}, (reading, name))


class MeaningTests(unittest.TestCase):
    """The accepted amount is a take-up demand signal, not cash in the system (#659, item 3)."""

    def test_the_declaration_labels_each_measure_for_what_it_is(self):
        meanings = REGISTRY["nyfed_repo_ops"]["field_meanings"]
        self.assertIn("demand", meanings["repo_accepted"])
        self.assertIn("not the amount outstanding", meanings["repo_accepted"])
        self.assertIn("outstanding", meanings["repo_term_outstanding"])
        self.assertEqual(set(meanings), set(REGISTRY["nyfed_repo_ops"]["fields"]))
        self.assertIn("repo_term_outstanding", REGISTRY["nyfed_repo_ops"]["fields"])

    def test_the_outstanding_series_is_off_the_panel_and_off_the_published_declaration(self):
        for columns in (fed_liquidity.ALL_COLUMN_FIELDS, contract.FEATURE_FIELDS):
            for pairs in columns.values():
                self.assertNotIn("repo_term_outstanding", [field for _source, field in pairs])
        self.assertNotIn("repo_term_outstanding", json.dumps(json.loads((ROOT / "metadata" / "sources.json").read_text())))
        self.assertEqual(ingest.NYFED_REPO_TERM_OUTSTANDING, "repo_term_outstanding")


if __name__ == "__main__":
    unittest.main()
