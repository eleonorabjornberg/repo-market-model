"""EFFR - IORB as a reserve-scarcity input: the adapter, the declaration, the feature.

Directive #98. The effective federal funds rate is fetched from the New York
Fed (`markets.newyorkfed.org`, `/api/rates/unsecured/effr/search.json`), not
from FRED, one snapshot per calendar year, and tracked under
`tests/fixtures/snapshots/nyfed_effr_inputs/`. It is declared in
`metadata/sources.json` as `nyfed_effr`, read through the as-of rule of
`docs/decisions/information-set.md` like every other field, and enters a model
only as `effr_minus_iorb_bp`, in whole basis points. It does not join the
published declaration: that is Eleonora's decision on the PR's evidence.
"""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

from repo_model.asof import InformationRule
from repo_model.contract import DERIVED_FEATURES, FEATURE_FIELDS, field_sources_for_features
from repo_model.data import OPT_IN_COLUMNS, PANEL_COLUMNS, DailyObservation
from repo_model.ingest import (
    fetch_nyfed_effr,
    load_snapshot_manifest,
    parse_snapshots,
)
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())
EFFR_INPUTS = ROOT / "tests" / "fixtures" / "snapshots" / "nyfed_effr_inputs"
DECISION = time(16, 0)
FEATURE = "effr_minus_iorb_bp"


def weekdays(start, count):
    out = []
    when = start
    while len(out) < count:
        if when.weekday() < 5:
            out.append(when)
        when += timedelta(days=1)
    return out


#: Mon 2026-01-05 onward, three weeks of panel days.
DATES = weekdays(date(2026, 1, 5), 15)


def rows(planted_at=None, planted=99.0):
    """Rows with `effr` 3.60 + i/100 and `iorb` 3.65, so the feature on row `i` is i - 5.

    `planted_at` overwrites one row's `effr` with `planted`, a value no
    admissible read can produce.
    """

    out = []
    for index, when in enumerate(DATES):
        values = {
            "sofr": 3.70 + index / 100.0,
            "iorb": 3.65,
            "effr": 3.60 + index / 100.0,
        }
        if when == planted_at:
            values["effr"] = planted
        out.append(DailyObservation(when, values))
    return out


def rule(features, registry=REGISTRY):
    return InformationRule(registry, tuple(features), decision_time=DECISION)


def read_of(info, feature):
    (found,) = [read for read in info.reads if read.feature == feature]
    return found


class EffrDeclarationTests(unittest.TestCase):
    """What the panel and the registry say EFFR is."""

    def test_effr_is_an_opt_in_column_drawn_from_the_new_york_fed(self):
        # Built only when asked for by name, so the published panel's
        # documented build, which names no columns, keeps its bytes.
        self.assertIn("effr", OPT_IN_COLUMNS)
        self.assertNotIn("effr", PANEL_COLUMNS)
        self.assertEqual(FEATURE_FIELDS["effr"], (("nyfed_effr", "EFFR"),))

    def test_a_build_builds_effr_only_when_named(self):
        from repo_model.cli_data import _requested_columns

        self.assertEqual(
            _requested_columns(["effr", "iorb", "sofr"]), ("sofr", "iorb", "effr")
        )

    def test_the_feature_is_effr_less_the_as_of_iorb(self):
        self.assertEqual(DERIVED_FEATURES[FEATURE], ("effr", "iorb"))
        self.assertEqual(
            set(field_sources_for_features((FEATURE,))),
            {
                ("nyfed_effr", "EFFR"),
                ("fred_macro_latest_vintage", "IORB"),
                ("fred_macro_latest_vintage", "IOER"),
            },
        )

    def test_the_source_is_the_new_york_fed_and_not_fred(self):
        entry = REGISTRY["nyfed_effr"]
        self.assertEqual(entry["provider"], "Federal Reserve Bank of New York")
        self.assertEqual(
            entry["url"],
            "https://markets.newyorkfed.org/api/rates/unsecured/effr/search.json",
        )
        lag = entry["release_lag"]
        self.assertEqual(
            (lag["basis"], lag["unit"], lag["days"], lag["available_time"]),
            ("ref_date", "business_days", 1, "15:00"),
        )
        self.assertIn("publication", entry["availability_provenance"])

    def test_the_feature_is_in_whole_basis_points(self):
        row = DailyObservation(date(2026, 1, 5), {"effr": 3.64, "iorb": 3.65, "sofr": 3.7})
        self.assertEqual(row.effr_minus_iorb_bp, -1.0)
        self.assertIsInstance(row.effr_minus_iorb_bp, float)
        # 4.33 - 4.40 is -7.000000000000028 in binary floating point.
        row = DailyObservation(date(2026, 1, 5), {"effr": 4.33, "iorb": 4.40, "sofr": 4.4})
        self.assertEqual(row.effr_minus_iorb_bp, -7.0)

    def test_an_unobserved_leg_is_an_unobserved_feature(self):
        row = DailyObservation(date(2026, 1, 5), {"effr": None, "iorb": 3.65, "sofr": 3.7})
        self.assertIsNone(row.effr_minus_iorb_bp)


class EffrLeakageTests(unittest.TestCase):
    """EFFR for day d is invisible at a decision before its publication instant.

    The New York Fed publishes EFFR for business day d on the morning of the
    next business day; `metadata/sources.json` declares it at 15:00 ET on that
    day, the conservative instant the secured rates carry. A forecast for
    Thursday is made at 16:00 on Wednesday, when Wednesday's EFFR has not been
    published. A value planted on Wednesday's row must therefore reach neither
    the forecast's feature row nor its training frame.

    Mutation record
    ---------------

    Red before the code existed: written first, the module failed to import
    (`ImportError: cannot import name 'fetch_nyfed_effr'`), and nothing it
    asserts had an implementation.

    Disposable copy under /tmp built from `git ls-files` plus the untracked
    files of this change, `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`, Python
    3.11.15, control green before and after.

    1. `metadata/sources.json`, `nyfed_effr.release_lag`: `"days": 1` changed to
       `"days": 0`, so EFFR for d is declared public at 15:00 on d (confirmed
       applied: the loaded registry reads 0). Kills
       `test_a_value_published_after_the_decision_is_invisible_to_the_forecast`
       with `AssertionError: 99.0 == 99.0` -- the value planted on Wednesday is
       read for Thursday's forecast. It also kills
       `test_reading_the_unpublished_row_is_refused_as_leakage`
       (`AssertionError: LookAheadError not raised`) and
       `test_after_a_weekend_fridays_value_is_read_on_monday`. It does not kill
       `test_the_derived_feature_never_reads_the_unpublished_row`, and should
       not: IORB's own 16:15 instant on d still holds the derived read back a
       row. The field-level declaration is the guard; the derived feature
       inherits it.
    """

    def setUp(self):
        self.wednesday = date(2026, 1, 14)
        self.scored = DATES.index(date(2026, 1, 15))  # Thursday; decision Wed 16:00

    def test_a_value_published_after_the_decision_is_invisible_to_the_forecast(self):
        current = rule(["spread_bps", "effr"])
        panel = rows(planted_at=self.wednesday)
        info = current.information_set(DATES, self.scored)
        current.check(DATES, info)
        observed = current.observation(panel, info)
        self.assertNotEqual(observed.values["effr"], 99.0)
        for row in current.frame(panel, info):
            self.assertNotEqual(row.values["effr"], 99.0, row.date)
        # What it reads instead: Tuesday's, published Wednesday morning.
        read = read_of(info, "effr")
        self.assertEqual(DATES[read.row], date(2026, 1, 13))
        self.assertEqual(read.available_at, datetime(2026, 1, 14, 15, 0))
        self.assertEqual(observed.values["effr"], panel[read.row].values["effr"])

    def test_reading_the_unpublished_row_is_refused_as_leakage(self):
        current = rule(["spread_bps", "effr"])
        info = current.information_set(DATES, self.scored)
        leaked = info._replace(
            reads=tuple(
                read._replace(row=self.scored - 1) if read.feature == "effr" else read
                for read in info.reads
            )
        )
        with self.assertRaises(LookAheadError):
            current.check(DATES, leaked)

    def test_the_derived_feature_never_reads_the_unpublished_row(self):
        current = rule(["spread_bps", FEATURE])
        panel = rows(planted_at=self.wednesday)
        info = current.information_set(DATES, self.scored)
        current.check(DATES, info)
        read = read_of(info, FEATURE)
        # One row with the target: EFFR and SOFR share a publication instant.
        self.assertEqual(read.row, info.anchor)
        self.assertEqual(DATES[read.row], date(2026, 1, 13))
        observed = current.observation(panel, info)
        self.assertEqual(observed.effr_minus_iorb_bp, float(DATES.index(date(2026, 1, 13)) - 5))

    def test_after_a_weekend_fridays_value_is_read_on_monday(self):
        # Scored Tuesday 2026-01-13, decision Monday 16:00: Friday's EFFR was
        # published Monday morning and is declared at Monday 15:00.
        scored = DATES.index(date(2026, 1, 13))
        info = rule(["spread_bps", "effr"]).information_set(DATES, scored)
        self.assertEqual(DATES[read_of(info, "effr").row], date(2026, 1, 9))


class EffrAdapterTests(unittest.TestCase):
    """`fetch_nyfed_effr`: one request per calendar year, saved unmodified."""

    PAYLOAD = (
        b'{ "refRates": [ { "effectiveDate": "2025-12-31", "type": "EFFR" ,'
        b'"percentRate": 3.64 ,"percentPercentile1": 3.60 ,"percentPercentile25": 3.64 ,'
        b'"percentPercentile75": 3.65 ,"percentPercentile99": 3.69 ,"targetRateFrom": 3.50 ,'
        b'"targetRateTo": 3.75 ,"revisionIndicator": "" } ] }'
    )

    def test_one_snapshot_per_year_from_the_unsecured_endpoint(self):
        requested = []

        def downloader(url):
            requested.append(url)
            return self.PAYLOAD

        with tempfile.TemporaryDirectory() as root:
            artifacts = fetch_nyfed_effr(
                Path(root), "2024-06-01", "2025-12-31", downloader=downloader
            )
            self.assertEqual(len(artifacts), 2)
            self.assertEqual({a.source_id for a in artifacts}, {"nyfed_effr"})
        windows = []
        for url in requested:
            parsed = urlparse(url)
            self.assertEqual(parsed.netloc, "markets.newyorkfed.org")
            self.assertEqual(parsed.path, "/api/rates/unsecured/effr/search.json")
            query = parse_qs(parsed.query)
            self.assertEqual(query["type"], ["rate"])
            windows.append((query["startDate"][0], query["endDate"][0]))
        self.assertEqual(
            windows, [("2024-06-01", "2024-12-31"), ("2025-01-01", "2025-12-31")]
        )

    def test_a_response_without_a_rate_list_is_refused(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                fetch_nyfed_effr(
                    Path(root), "2025-01-01", "2025-12-31", downloader=lambda url: b"{}"
                )

    def test_a_parsed_value_is_dated_to_the_next_business_day_at_1500(self):
        with tempfile.TemporaryDirectory() as root:
            (artifact,) = fetch_nyfed_effr(
                Path(root), "2025-01-01", "2025-12-31", downloader=lambda url: self.PAYLOAD
            )
            parsed = parse_snapshots([artifact])
        (effr,) = [row for row in parsed.rows if row.series_id == "EFFR"]
        self.assertEqual(effr.ref_date, date(2025, 12, 31))
        self.assertEqual(effr.value, 3.64)
        self.assertEqual(
            effr.available_at,
            datetime(2026, 1, 2, 15, 0, tzinfo=ZoneInfo("America/New_York")),
        )


class TrackedEffrSnapshotTests(unittest.TestCase):
    """The tracked snapshot is what its sidecars say, and covers the panel."""

    def manifests(self):
        return sorted(EFFR_INPUTS.glob("*/*.manifest.json"))

    def test_every_snapshot_matches_its_checksum(self):
        manifests = self.manifests()
        self.assertTrue(manifests, f"no EFFR snapshot under {EFFR_INPUTS}")
        for manifest in manifests:
            artifact = load_snapshot_manifest(manifest)
            with self.subTest(snapshot=artifact.path.name):
                self.assertEqual(artifact.source_id, "nyfed_effr")
                self.assertEqual(
                    hashlib.sha256(artifact.path.read_bytes()).hexdigest(), artifact.sha256
                )
                self.assertTrue(
                    artifact.url.startswith(REGISTRY["nyfed_effr"]["url"] + "?")
                )

    def test_the_snapshot_covers_the_published_panel(self):
        artifacts = [load_snapshot_manifest(path) for path in self.manifests()]
        parsed = parse_snapshots(artifacts)
        effr = {row.ref_date: row.value for row in parsed.rows if row.series_id == "EFFR"}
        self.assertLessEqual(min(effr), date(2018, 4, 3))
        self.assertGreaterEqual(max(effr), date(2026, 9, 3))
        # Two spot values, as the New York Fed publishes them.
        self.assertEqual(effr[date(2026, 1, 5)], 3.64)
        self.assertEqual(effr[date(2025, 12, 31)], 3.64)


class GbmReadsTheDerivedFeatureTests(unittest.TestCase):
    """A derived feature declared as a regressor is read off its constituents."""

    def test_the_regressor_is_the_property_and_a_hole_is_a_hole(self):
        from repo_model.baseline import _raw_regressor

        row = DailyObservation(date(2026, 1, 5), {"effr": 3.64, "iorb": 3.65, "sofr": 3.7})
        self.assertEqual(_raw_regressor(row, FEATURE, "row"), -1.0)
        row = DailyObservation(date(2026, 1, 5), {"effr": None, "iorb": 3.65, "sofr": 3.7})
        self.assertIsNone(_raw_regressor(row, FEATURE, "row"))


if __name__ == "__main__":
    unittest.main()
