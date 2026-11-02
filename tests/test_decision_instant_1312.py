"""The decision instant is 18:00 New York time, and one declared constant (#1312, step 1 of 3).

Her ruling of 29 October 2026 (relayed on #1312, ledger item 77): a forecast is made at 18:00 on the last panel day
before the scored day, not at 16:00. `repo_model.decision_instant.DECISION_TIME` is the one place the clock is typed;
every default and constant in `src/` that means "the decision instant" takes it. The source audit is
`scripts/decision_instant_1312.py`: which declared availabilities fall in the window 16:00 to 18:00, which scored days
read a later row because of it, and that nothing the target day's spread is computed from becomes visible.

Red first: this file was committed before `repo_model.decision_instant` existed and failed with `ModuleNotFoundError`.

**Recorded mutations** (29 October 2026), each applied to the tree, confirmed applied by grep, the test classes named run,
then reverted:

1. `scripts/decision_instant_1312.py`, `target_day_leaks`: the line `if moment is not None and moment <= deadline:`
   changed to `if moment is not None and moment <= deadline.replace(hour=0, minute=0):`. `TargetDayTests.
   test_a_value_announced_at_seventeen_hundred_the_day_before_is_a_leak_at_eighteen_hundred` then failed with
   `AssertionError: LookAheadError not raised`.
2. `metadata/sources.json`, `nyfed_fr2004.release_lag.available_time`: `"16:30"` changed to `"18:30"`.
   `WindowTests.test_the_window_holds_exactly_the_audited_declarations` then failed with `AssertionError` (the
   FR 2004 fields left the window), and `test_the_committed_audit_describes_the_registry` with `AssertionError: 1 != 0`.
3. `metadata/sources.json`, `fed_iorb_announcements.scheduled_availability.available_time`: `"18:00"` changed to
   `"16:00"`. `DecisionKeyedTests.test_the_declaration_keyed_on_the_decision_instant_equals_it` then failed with
   `AssertionError` (the audit reported the declaration), and the two window tests failed too.
4. `src/repo_model/gcf_index.py`, `check_record`: the line
   `decision = datetime.fromisoformat(record["decision_instant"])` changed to `decision = decision_instant(effective)`.
   `GcfLegacyTests.test_a_record_made_at_sixteen_hundred_is_judged_against_its_own_instant` then failed with
   `AssertionError: LookAheadError not raised` (a 16:05 fetch of a record that declares 16:00 was no longer late).
5. `src/repo_model/data.py`, `_priceable_columns`: the line `if str(exc) == ZERO_PURGE_REFUSAL:` changed to `if False:`.
   `RegistryTests.test_the_panel_build_prices_the_h15_columns_at_the_new_instant` then failed with `AssertionError`
   (`['sofr'] != ['iorb', 'tbill_4w', 'tbill_13w', 'sofr']`: the three same-day columns were refused with "selected sources
   must produce a nonzero purge") and `PanelTests.test_the_panel_built_at_eighteen_hundred_keeps_every_column_and_its_digest`
   errored (the build's manifest no longer carried the columns).
6. `src/repo_model/decision_instant.py`: `DECISION_TIME = time(18, 0)` changed to `time(19, 0)`.
   `BoundaryTests.test_a_value_public_at_eighteen_oh_one_is_not_read_at_the_decision` then failed with
   `AssertionError: 2093 != 2092` (the 18:01 print was read at the decision), and `ConstantTests.test_the_instant_is_eighteen_hundred`
   failed with `AssertionError`.
"""

from __future__ import annotations

import ast
import copy
import importlib.util
import json
import sys
import unittest
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from repo_model import asof, decision_instant as di, gcf_index as gi
from repo_model.registry import ZERO_PURGE_REFUSAL, RegistryContractError, max_release_lag_days
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((REPO / "metadata" / "sources.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((REPO / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))


def _audit():
    path = REPO / "scripts" / "decision_instant_1312.py"
    spec = importlib.util.spec_from_file_location("decision_instant_1312", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["decision_instant_1312"] = module
    spec.loader.exec_module(module)
    return module


audit = _audit()


def _dates():
    import panel_cache

    return audit.panel_dates(panel_cache.published_build()["path"])


class ConstantTests(unittest.TestCase):
    def test_the_instant_is_eighteen_hundred(self):
        self.assertEqual(di.DECISION_TIME, time(18, 0))
        self.assertEqual(di.DECISION_TIME_TEXT, "18:00")
        self.assertEqual(di.DECISION_TIME_SECONDS_TEXT, "18:00:00")
        self.assertEqual(di.DECISION_TIMEZONE, "America/New_York")

    def test_the_earlier_instant_is_kept_for_the_records_made_at_it(self):
        self.assertEqual(di.LEGACY_DECISION_TIME, time(16, 0))
        self.assertEqual(di.LEGACY_DECISION_TIME_TEXT, "16:00")

    def test_the_published_manifest_states_it(self):
        self.assertEqual(MANIFEST["decision_time"], di.DECISION_TIME_SECONDS_TEXT)

    def test_the_final_test_takes_it(self):
        spec = importlib.util.spec_from_file_location("ftp_1312", REPO / "scripts" / "final_test_preregistration.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertIs(module.DECISION, di.DECISION_TIME)
        self.assertEqual(module.crps_declaration()["decision_time"], di.DECISION_TIME_TEXT)
        self.assertEqual(module.declaration()["fold_grid"]["decision_time"], di.DECISION_TIME_TEXT)
        self.assertEqual(module.CRPS_COMMAND[module.CRPS_COMMAND.index("--decision-time") + 1], di.DECISION_TIME_TEXT)


class OneSourceTests(unittest.TestCase):
    """No module of `src/repo_model/` types the decision clock again."""

    #: `ingest.py` writes sources' own declared availability instants (SRF, ON RRP and OFR at 16:00 on the next business
    #: day, the H.8's 16:15, the bill rates' 16:30); they are what `metadata/sources.json` declares and not the decision.
    SOURCE_INSTANTS = {"ingest.py"}
    #: Modules whose `DECISION_TIME` is a dated declaration's 16:00 and says so, as `LEGACY_DECISION_TIME`.
    KEEP_LEGACY = {"fed_liquidity.py", "srf_line.py"}

    def _trees(self):
        for path in sorted((REPO / "src" / "repo_model").glob("*.py")):
            if path.name == "decision_instant.py":
                continue
            yield path, ast.parse(path.read_text(encoding="utf-8"))

    def test_no_module_types_the_clock_for_the_decision(self):
        found = []
        for path, tree in self._trees():
            if path.name in self.SOURCE_INSTANTS:
                continue
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "time"
                        and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 16
                        and all(isinstance(a, ast.Constant) and a.value == 0 for a in node.args[1:])):
                    found.append(f"{path.name}:{node.lineno}")
        self.assertEqual(found, [])

    def test_every_decision_time_default_is_the_constant(self):
        bad = []
        for path, tree in self._trees():
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                args = node.args
                names = [a.arg for a in args.posonlyargs + args.args]
                defaults = [None] * (len(names) - len(args.defaults)) + list(args.defaults)
                pairs = list(zip(names, defaults)) + list(zip([a.arg for a in args.kwonlyargs], args.kw_defaults))
                for name, default in pairs:
                    if name == "decision_time" and default is not None and not (
                            isinstance(default, ast.Constant) and default.value is None
                        ):
                        if not (isinstance(default, ast.Name) and default.id == "DECISION_TIME"):
                            bad.append(f"{path.name}:{node.name}")
        self.assertEqual(bad, [])

    def test_a_module_level_decision_time_is_the_constant_or_a_declared_legacy(self):
        for path, tree in self._trees():
            for node in tree.body:
                if (isinstance(node, ast.Assign) and len(node.targets) == 1
                        and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "DECISION_TIME"):
                    want = "LEGACY_DECISION_TIME" if path.name in self.KEEP_LEGACY else "DECISION_TIME"
                    self.assertTrue(isinstance(node.value, ast.Name) and node.value.id == want, path.name)

    def test_the_modules_that_read_it_hold_the_constant(self):
        from repo_model import (fomc_calendar, gcf_index, policy_features, richer_targets, s3c_announced, s3c_gse,
                                s3c_gse_roll, s3c_net, s3c_pd, spread_mr_calendar, spread_mr_state_calendar)

        self.assertIs(gcf_index.DECISION_TIME, di.DECISION_TIME)
        for module in (fomc_calendar, policy_features, richer_targets, s3c_announced, s3c_gse, s3c_gse_roll, s3c_net,
                       s3c_pd, spread_mr_calendar, spread_mr_state_calendar):
            self.assertIs(module.DECISION_TIME, di.DECISION_TIME, module.__name__)

    def test_the_two_legacy_readers_keep_the_instant_their_dated_declarations_record(self):
        from repo_model import fed_liquidity, srf_line

        self.assertEqual(srf_line.DECISION_TIME, di.LEGACY_DECISION_TIME)
        self.assertEqual(fed_liquidity.DECISION_TIME, di.LEGACY_DECISION_TIME)


class DecisionKeyedTests(unittest.TestCase):
    def test_the_declaration_keyed_on_the_decision_instant_equals_it(self):
        self.assertEqual(audit.decision_keyed_problems(REGISTRY), [])
        block = REGISTRY["fed_iorb_announcements"]["scheduled_availability"]
        self.assertEqual(time.fromisoformat(block["available_time"]), di.DECISION_TIME)

    def test_a_declaration_left_at_sixteen_hundred_is_reported(self):
        stale = copy.deepcopy(REGISTRY)
        stale["fed_iorb_announcements"]["scheduled_availability"]["available_time"] = "16:00"
        self.assertEqual(len(audit.decision_keyed_problems(stale)), 1)


class WindowTests(unittest.TestCase):
    """The declared availabilities that fall after 16:00 and at or before 18:00: audited, and pinned here."""

    #: (source, clock) -> the fields, as the audit found them on 29 October 2026.
    AUDITED = {
        ("frb_ddp", "16:15"): ["EFFR", "IOER", "IORB"],
        ("frb_h8", "16:15"): ["total_assets"],
        ("fred_macro_latest_vintage", "16:15"): ["DFF", "IOER", "IORB"],
        ("fred_macro_latest_vintage", "16:30"): ["WLRRAOL", "WRESBAL", "WTREGEN"],
        ("nyfed_fr2004", "16:30"): [
            "PDPOSGS-B", "PDPOSGS-BFRN", "PDPOSGSC-G11", "PDPOSGSC-G11L21", "PDPOSGSC-G21", "PDPOSGSC-G2L3",
            "PDPOSGSC-G3L6", "PDPOSGSC-G6L7", "PDPOSGSC-G7L11", "PDPOSGSC-L2", "PDPOSGST-TOT", "PDPOSTIPS-G11",
            "PDPOSTIPS-G2", "PDPOSTIPS-G6L11", "PDPOSTIPS-L2"],
        ("treasury_bill_rates", "16:30"): [
            f"tbill_{n}w_{kind}" for n in ("4", "6", "8", "13", "17", "26", "52")
            for kind in ("bank_discount", "coupon_equivalent")],
        ("fed_iorb_announcements", "18:00"): ["iorb_announced_change_bps", "iorb_days_to_announced_change"],
    }

    def test_the_window_holds_exactly_the_audited_declarations(self):
        found = {}
        for entry in audit.window_declarations(REGISTRY):
            found.setdefault((entry["source"], entry["available_time"]), []).append(entry["field"])
        self.assertEqual({k: sorted(v) for k, v in found.items()}, {k: sorted(v) for k, v in self.AUDITED.items()})

    def test_a_new_declaration_inside_the_window_is_found(self):
        grown = copy.deepcopy(REGISTRY)
        grown["nyfed_sofr"]["release_lag"]["available_time"] = "17:00"
        sources = {e["source"] for e in audit.window_declarations(grown)}
        self.assertIn("nyfed_sofr", sources)
        self.assertNotIn("nyfed_sofr", {e["source"] for e in audit.window_declarations(REGISTRY)})

    def test_the_window_is_after_the_old_instant_and_up_to_the_new_one_inclusive(self):
        edge = copy.deepcopy(REGISTRY)
        edge["nyfed_sofr"]["release_lag"]["available_time"] = "16:00"
        self.assertNotIn("nyfed_sofr", {e["source"] for e in audit.window_declarations(edge)})
        edge["nyfed_sofr"]["release_lag"]["available_time"] = "18:00"
        self.assertIn("nyfed_sofr", {e["source"] for e in audit.window_declarations(edge)})
        edge["nyfed_sofr"]["release_lag"]["available_time"] = "18:01"
        self.assertNotIn("nyfed_sofr", {e["source"] for e in audit.window_declarations(edge)})

    def test_the_committed_audit_describes_the_registry(self):
        self.assertEqual(audit.check_command(None), 0)


class MovesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dates = _dates()
        cls.moved = {(m["source"], m["field"]): m for m in audit.moves(REGISTRY, cls.dates)}

    def test_a_same_day_print_is_read_one_row_fresher(self):
        for key in (("fred_macro_latest_vintage", "IORB"), ("treasury_bill_rates", "tbill_13w_bank_discount"),
                    ("treasury_bill_rates", "tbill_4w_bank_discount"), ("frb_ddp", "EFFR")):
            entry = self.moved[key]
            self.assertEqual(entry["rows_later"], {"1": entry["days_moved"]}, key)
            self.assertGreaterEqual(entry["days_moved"], len(self.dates) - 5, key)

    def test_the_secured_rates_and_the_settlement_schedule_do_not_move(self):
        for key in (("nyfed_sofr", "SOFR"), ("nyfed_tgcr", "TGCR"), ("nyfed_bgcr", "BGCR"), ("nyfed_effr", "EFFR"),
                    ("treasury_auctions", "treasury_settlement"), ("nyfed_on_rrp", "reverse_repo_total_accepted"),
                    ("nyfed_srf", "srf_total_accepted"), ("fed_iorb_announcements", "iorb_announced_change_bps")):
            self.assertEqual(self.moved[key]["days_moved"], 0, key)

    def test_the_weekly_levels_move_on_the_days_a_print_falls_in_the_window(self):
        entry = self.moved[("fred_macro_latest_vintage", "WRESBAL")]
        self.assertGreater(entry["days_moved"], 0)
        self.assertEqual(set(entry["rows_later"]), {"1"})


class TargetDayTests(unittest.TestCase):
    """Nothing the target day's spread is computed from is public at the decision on the day before it."""

    @classmethod
    def setUpClass(cls):
        cls.dates = _dates()

    def test_no_value_of_the_target_day_is_public_at_eighteen_hundred(self):
        self.assertEqual(audit.target_day_leaks(REGISTRY, self.dates), [])
        audit.require_no_target_leak(REGISTRY, self.dates)

    def test_the_target_components_are_sofr_and_iorb(self):
        from repo_model.contract import field_sources_for_features

        pairs = {field for _source, field in field_sources_for_features((asof.TARGET,))}
        self.assertEqual(pairs, {"SOFR", "IORB", "IOER"})  # IOER is the administered rate before 2021-07-29

    def test_a_value_announced_at_seventeen_hundred_the_day_before_is_a_leak_at_eighteen_hundred(self):
        leaky = copy.deepcopy(REGISTRY)
        leaky["nyfed_sofr"][asof.SCHEDULED_AVAILABILITY_KEY] = {
            "basis": "announced_before_ref_date", "unit": "business_days", "days": 1, "available_time": "17:00",
            "timezone": "America/New_York", "fields": ["SOFR"]}
        with self.assertRaises(LookAheadError):
            audit.require_no_target_leak(leaky, self.dates)
        # The same declaration was not a leak at the old instant: the move is what makes it one.
        self.assertEqual(audit.target_day_leaks(leaky, self.dates, clock=di.LEGACY_DECISION_TIME), [])


class BoundaryTests(unittest.TestCase):
    """The as-of rule at the new instant reads what is public by it and nothing after it."""

    @classmethod
    def setUpClass(cls):
        cls.dates = _dates()

    def _registry(self, clock: str):
        registry = copy.deepcopy(REGISTRY)
        registry["treasury_bill_rates"]["release_lag"]["available_time"] = clock
        return registry

    def _row(self, clock: str, scored: int, decision: time = di.DECISION_TIME) -> int:
        rule = asof.InformationRule(self._registry(clock), ("tbill_13w",), decision_time=decision)
        info = rule.information_set(self.dates, scored)
        rule.check(self.dates, info)
        return next(read.row for read in info.reads if read.feature == "tbill_13w")

    def test_a_value_public_at_seventeen_fifty_nine_is_read_at_the_decision(self):
        scored = len(self.dates) - 10
        self.assertEqual(self._row("17:59", scored), scored - 1)

    def test_a_value_public_at_eighteen_oh_one_is_not_read_at_the_decision(self):
        scored = len(self.dates) - 10
        self.assertEqual(self._row("18:01", scored), scored - 2)

    def test_a_value_public_at_eighteen_hundred_is_read_at_the_decision(self):
        scored = len(self.dates) - 10
        self.assertEqual(self._row("18:00", scored), scored - 1)

    def test_the_published_registry_reads_the_bill_rate_of_the_decision_day(self):
        scored = len(self.dates) - 10
        self.assertEqual(self._row("16:30", scored), scored - 1)
        self.assertEqual(self._row("16:30", scored, decision=di.LEGACY_DECISION_TIME), scored - 2)

    def test_every_scored_day_of_the_published_panel_passes_both_guards_at_the_new_instant(self):
        features = ("spread_bps", "tbill_4w", "tbill_13w", "reserve_balances", "tga", "dealer_treasury_position",
                    "sofr_volume", "sofr_p25", "sofr_p75")
        rule = asof.InformationRule(REGISTRY, features, decision_time=di.DECISION_TIME)
        for scored in range(70, len(self.dates)):
            rule.check(self.dates, rule.information_set(self.dates, scored))

    def test_the_decision_instant_of_a_scored_day_is_the_previous_panel_day_at_the_constant(self):
        rule = asof.InformationRule(REGISTRY, ("spread_bps",), decision_time=di.DECISION_TIME)
        self.assertEqual(rule.decision_instant(self.dates, 100), datetime.combine(self.dates[99], time(18, 0)))


class RegistryTests(unittest.TestCase):
    """A same-day print prices to a zero purge; only the panel build accepts that."""

    def _registry(self):
        return {"print": {"release_lag": {
            "basis": "record_date", "unit": "calendar_days", "days": 0, "available_time": "09:00",
            "timezone": "America/New_York"}}}

    def test_everyone_else_still_gets_the_zero_purge_refusal(self):
        with self.assertRaises(RegistryContractError) as caught:
            max_release_lag_days(self._registry(), ["print"], decision_time=time(15))
        self.assertEqual(str(caught.exception), ZERO_PURGE_REFUSAL)

    def test_the_other_refusals_are_not_the_zero_one(self):
        with self.assertRaisesRegex(RegistryContractError, "unknown source"):
            max_release_lag_days({}, ["nothing"], decision_time=time(15))
        with self.assertRaisesRegex(RegistryContractError, "at least one"):
            max_release_lag_days({}, [], decision_time=time(15))

    def test_the_panel_build_prices_the_h15_columns_at_the_new_instant(self):
        from repo_model.data import _priceable_columns

        for decision in (di.DECISION_TIME, di.LEGACY_DECISION_TIME):
            with self.subTest(decision=decision):
                built, refused = _priceable_columns(["iorb", "tbill_4w", "tbill_13w", "sofr"], REGISTRY, decision)
                self.assertEqual(built, ["iorb", "tbill_4w", "tbill_13w", "sofr"])
                self.assertEqual(refused, {})

    def test_the_other_refusals_of_the_build_stand_at_the_new_instant(self):
        from repo_model.data import _priceable_columns

        built, refused = _priceable_columns(["mmf_assets", "sofr"], REGISTRY, di.DECISION_TIME)
        self.assertEqual(built, ["sofr"])
        self.assertIn("mmf_assets", refused)
        self.assertNotIn(ZERO_PURGE_REFUSAL, refused["mmf_assets"])


class PanelTests(unittest.TestCase):
    def test_the_panel_built_at_eighteen_hundred_keeps_every_column_and_its_digest(self):
        import panel_cache

        build = panel_cache.published_build()
        manifest = json.loads(Path(str(build["path"]) + ".manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["decision_time"], "18:00:00")
        self.assertEqual(manifest["built_columns"], MANIFEST["built_columns"])
        self.assertEqual(manifest["sha256"], MANIFEST["sha256"])
        for column in ("iorb", "tbill_4w", "tbill_13w"):
            self.assertNotIn(column, manifest["refused_columns"])

    def test_the_cached_build_uses_the_manifests_instant(self):
        import panel_cache

        self.assertEqual(panel_cache.DECISION_TIME, di.DECISION_TIME_SECONDS_TEXT)


def _utc(day: date, hour: int, minute: int = 0) -> datetime:
    """An aware UTC instant for an Eastern wall-clock time on `day` (EDT, as 26 October 2026 is)."""

    return (datetime(day.year, day.month, day.day, hour, minute) - timedelta(hours=-4)).replace(tzinfo=timezone.utc)


class GcfLegacyTests(unittest.TestCase):
    DAY = date(2026, 10, 26)
    URL = "https://cms-prod.dtcc.com/data/gcfindex.csv?v=1793049000000"

    def _payload(self):
        return (
            "Date,MBS Total PAR Value,MBS Weighted Average,Treasury Total PAR Value,Treasury Weighted Average\r\n"
            "10/26/2026,136692000000,  3.967,65840000000,  3.946 \r\nTRAILER,1,,,,,\r\n"
        ).encode("utf-8")

    def _record(self, hour, minute):
        return gi.captured_record(self._payload(), url=self.URL, fetched_at=_utc(self.DAY, hour, minute), effective=self.DAY)

    def test_the_decision_instant_is_eighteen_hundred_and_the_legacy_one_sixteen_hundred(self):
        self.assertEqual(gi.decision_instant(self.DAY).hour, 18)
        self.assertEqual(gi.legacy_decision_instant(self.DAY).hour, 16)

    def test_a_fetch_between_sixteen_and_eighteen_hundred_is_kept_under_the_new_instant(self):
        record = self._record(16, 5)
        self.assertEqual(record["status"], "captured")
        self.assertEqual(record["decision_instant"], gi.decision_instant(self.DAY).isoformat())
        gi.check_record(record)

    def test_a_fetch_after_eighteen_hundred_is_refused(self):
        with self.assertRaises(LookAheadError):
            self._record(18, 5)

    def test_a_record_made_at_sixteen_hundred_is_judged_against_its_own_instant(self):
        legacy = self._record(15, 40)
        legacy["decision_instant"] = gi.legacy_decision_instant(self.DAY).isoformat()
        gi.check_record(legacy)  # a record of the old instant still reads
        late = self._record(16, 5)
        late["decision_instant"] = gi.legacy_decision_instant(self.DAY).isoformat()
        with self.assertRaises(LookAheadError):
            gi.check_record(late)  # 16:05 is late for a record that declares 16:00

    def test_a_declared_instant_that_is_neither_is_refused(self):
        record = self._record(15, 40)
        record["decision_instant"] = _utc(self.DAY, 17, 0).astimezone(gi.EASTERN).isoformat()
        with self.assertRaises(ValueError):
            gi.check_record(record)

    def test_the_run_fetches_until_eighteen_hundred(self):
        now = lambda h, m: _utc(self.DAY, h, m)  # noqa: E731
        self.assertEqual(gi.plan(now(16, 30), set()).action, "fetch")
        self.assertEqual(gi.plan(now(18, 0), set()).action, "fetch")
        self.assertEqual(gi.plan(now(18, 1), set()).action, "late")
        self.assertEqual(gi.plan(now(15, 29), set()).action, "wait")


if __name__ == "__main__":
    unittest.main()
