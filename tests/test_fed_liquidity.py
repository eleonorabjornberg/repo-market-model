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


def operation(day, accepted, *, kind="Repo", term="Overnight", submitted=None, rate=None, written=None, note=""):
    """One operation record, in the Desk's shape."""

    submitted = accepted if submitted is None else submitted
    details = [{"securityType": "Treasury", "amtSubmitted": submitted, "amtAccepted": accepted}]
    if rate is not None:
        details[0]["percentWeightedAverageRate"] = rate
    return {
        "operationId": f"{kind} {day} {term}",
        "operationDate": day,
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

    def test_every_year_from_2018_to_2025_is_saved_and_checksummed(self):
        manifests = self.manifests()
        self.assertEqual(
            sorted(m.url.split("startDate=")[1][:4] for m in manifests), [str(y) for y in range(2018, 2026)]
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
            self.panel(), self.directory(*self.operations()), cutoff=self.CUTOFF, end=date(2026, 12, 31), reading=reading
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
            reading=fed_liquidity.SAME_DAY,
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
        document = json.loads(DECLARATION.read_text(encoding="utf-8"))["candidates"]
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


if __name__ == "__main__":
    unittest.main()
