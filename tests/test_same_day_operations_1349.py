"""The decision day's own ON RRP and SRF take-up as extra terms of the state-calendar fit (#1349; H5 step 3; her ruling of 1 November 2026 on
avenue #1337, ledger item 98: "use the same day and test it").

`repo_model.same_day_operations` is a new read path. It reads the Desk's operation results of the *decision day itself*: the overnight Standing Repo
Facility take-up (a 0/1 flag `srf_flag` and its size `srf_size`, USD 100 bn) and the change in the ON RRP amount accepted from the previous
panel day (`on_rrp_change`, USD 100 bn). A figure is public at the decision instant (`repo_model.decision_instant`, 18:00 New York) only when the
last write of every one of its records (`lastUpdated`) is at or before that instant: a record cannot have been written later than it was first
written, and a date rewritten after the decision (the Desk rewrote some on 2023-09-27) has no first publication time we can see, so it is withheld
and reads as no take-up. `SameDayOperationTerms` is the table `spread_mr_state_calendar.walk` calls through its `iorb` argument (`at`, `read`);
`SAMEDAY_ARM` is (s3c-ann-net) with the three terms as extras. The published declaration, the live record and (s3c)'s tables do not read it.

What these tests pin: the day figures (ON RRP summed over Reverse Repo operations, SRF the overnight repo operations since the facility's start,
the kept-operation rules of `ingest._nyfed_srf_rows`), the withholding by last write; the terms at a lead are the decision day's own take-up as of
the decision instant (not the target day's, not a later instant's); a training figure and a forecast figure are the same function of the same
records; `read` refuses, with `LookAheadError`, a figure that counts a record written after the decision instant and, with `StaleReadError`, one
that leaves a public record out; the fit takes the terms beside the net sizes; and the arm is (s3c-ann-net) with the named change only.

Recorded mutation (leakage, #1349): in `same_day_operations.SameDayOperationTerms.at`, the decision instant
`datetime.combine(self.dates[decision], self._time)` was changed to `datetime.combine(self.dates[row], self._time)` (the target day's own instant,
when a record written between the decision and the target is counted). `ReadTests.test_a_record_written_after_the_decision_instant_is_not_read`
then failed with `LookAheadError` (the guard in `read` refused the figure that counted a record written after its decision); restored, it passes.
"""

from __future__ import annotations

import dataclasses
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import same_day_operations as sdo, s3c_announced, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import StaleReadError  # noqa: E402
from repo_model.decision_instant import DECISION_TIME  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DAYS = [date(2026, 3, 2) + timedelta(days=i) for i in range(12)]
DAYS = [d for d in DAYS if d.weekday() < 5]


def op(day, amount, written, kind="Reverse Repo", term="Overnight", op_id=None, note=""):
    return {
        "operationId": op_id or f"{kind[:2]}-{day}-{amount}-{written}", "operationDate": day.isoformat(), "operationType": kind, "term": term,
        "totalAmtAccepted": amount, "lastUpdated": written, "note": note, "details": [],
    }


def stamp(day, hhmm):
    return f"{day.isoformat()} {hhmm}:00"


class DayFigureTests(unittest.TestCase):

    def test_on_rrp_is_the_sum_of_the_reverse_repos_of_the_date_in_billions_and_its_last_write(self):
        d = DAYS[0]
        got = sdo.on_rrp_days([
            op(d, 30_000_000_000, stamp(d, "13:16")), op(d, 5_000_000_000, stamp(d, "13:40")), op(d, 9_000_000_000, stamp(d, "13:20"), kind="Repo"),
        ])
        self.assertEqual(got[d].value, 35.0)
        self.assertEqual(got[d].written, datetime.combine(d, time(13, 40)))

    def test_a_record_served_by_two_snapshots_is_counted_once_at_its_latest_write(self):
        d = DAYS[0]
        first = op(d, 30_000_000_000, stamp(d, "13:16"), op_id="x")
        again = dict(first, lastUpdated="2026-03-20 14:15:30")
        got = sdo.on_rrp_days(sdo.unique_operations([first, again]))
        self.assertEqual(got[d].value, 30.0)
        self.assertEqual(got[d].written, datetime(2026, 3, 20, 14, 15, 30))

    def test_srf_is_the_overnight_repos_since_the_facility_started(self):
        d = DAYS[0]
        got = sdo.srf_days([
            op(d, 12_000_000_000, stamp(d, "13:46"), kind="Repo"), op(d, 8_000_000_000, stamp(d, "08:31"), kind="Repo"),
            op(d, 99_000_000_000, stamp(d, "13:46"), kind="Repo", term="Term"), op(d, 7_000_000_000, stamp(d, "13:46")),
            op(date(2021, 7, 28), 5_000_000_000, "2021-07-28 13:46:00", kind="Repo"),
        ])
        self.assertEqual(got[d].value, 20.0)
        self.assertEqual(got[d].written, datetime.combine(d, time(13, 46)))
        self.assertNotIn(date(2021, 7, 28), got)

    def test_a_day_of_a_test_trade_only_is_a_present_zero(self):
        d = DAYS[0]
        got = sdo.srf_days([op(d, 1_000_000, stamp(d, "13:46"), kind="Repo")])
        self.assertEqual(got[d].value, 0.0)

    def test_an_operation_with_no_readable_last_write_is_an_error(self):
        d = DAYS[0]
        with self.assertRaises(ValueError):
            sdo.on_rrp_days([dict(op(d, 1, stamp(d, "13:16")), lastUpdated="soon")])

    def test_the_srf_series_is_the_one_the_published_reader_builds(self):
        """On the tracked snapshots the values equal `ingest._nyfed_srf_rows` date for date: the kept-operation rules are not restated."""

        import hashlib
        from repo_model import ingest

        directory = ROOT / "tests" / "fixtures" / "snapshots" / "srf_inputs" / "nyfed_srf"
        built = {}
        for manifest in sorted(directory.glob("*.manifest.json")):
            artifact = ingest.load_snapshot_manifest(manifest)
            payload = Path(str(manifest)[: -len(".manifest.json")]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact.sha256)
            for row in ingest._nyfed_srf_rows(artifact, payload):
                built[row.ref_date] = row.value
        mine = sdo.srf_days(sdo.load_operations(directory))
        self.assertEqual({d: f.value for d, f in mine.items() if d in built}, built)
        self.assertEqual(set(built) - set(mine), set())
        self.assertTrue(built)


class TermTests(unittest.TestCase):

    def table(self, srf, rrp, names=sdo.OPS_EXTRAS):
        return sdo.SameDayOperationTerms(DAYS, srf, rrp, names=names)

    def test_the_terms_are_the_decision_days_own_take_up_in_units_of_100_bn(self):
        d = DAYS[4]
        t = self.table({d: sdo.DayFigure(25.0, datetime.combine(d, time(13, 46)))},
                       {DAYS[3]: sdo.DayFigure(40.0, datetime.combine(DAYS[3], time(13, 20))),
                        d: sdo.DayFigure(10.0, datetime.combine(d, time(13, 20)))})
        # The target of the decision on DAYS[4] at lead 3 is DAYS[7]; the figure is the decision day's, whatever the lead.
        for lead in (1, 2, 3, 4, 5):
            got = t.at(lead, 4 + lead)
            self.assertEqual(got[sc.SRF_FLAG], 1.0)
            self.assertAlmostEqual(got[sc.SRF_SIZE], 0.25)
            self.assertAlmostEqual(got[sc.RRP_CHANGE], -0.30)

    def test_no_take_up_is_a_zero_flag_and_size(self):
        t = self.table({}, {})
        self.assertEqual(t.at(2, 6), {sc.SRF_FLAG: 0.0, sc.SRF_SIZE: 0.0, sc.RRP_CHANGE: 0.0})

    def test_a_row_with_no_decision_row_reads_zero(self):
        d = DAYS[1]
        t = self.table({d: sdo.DayFigure(25.0, datetime.combine(d, time(13, 46)))}, {})
        self.assertEqual(t.at(5, 3), {sc.SRF_FLAG: 0.0, sc.SRF_SIZE: 0.0, sc.RRP_CHANGE: 0.0})

    def test_the_change_needs_both_days_public_at_the_decision(self):
        d, p = DAYS[4], DAYS[3]
        rewritten = {p: sdo.DayFigure(40.0, datetime.combine(d, time(19, 0))), d: sdo.DayFigure(10.0, datetime.combine(d, time(13, 20)))}
        self.assertEqual(self.table({}, rewritten).at(1, 5)[sc.RRP_CHANGE], 0.0)

    def test_a_subset_of_names_serves_only_those(self):
        t = self.table({}, {}, names=(sc.SRF_FLAG,))
        self.assertEqual(set(t.at(1, 5)), {sc.SRF_FLAG})
        with self.assertRaises(ValueError):
            self.table({}, {}, names=("net_coupon",))

    def test_a_record_written_up_to_the_decision_instant_is_public_at_it(self):
        d = DAYS[4]
        on = {d: sdo.DayFigure(25.0, datetime.combine(d, DECISION_TIME))}
        self.assertEqual(self.table(on, {}).at(1, 5)[sc.SRF_FLAG], 1.0)
        after = {d: sdo.DayFigure(25.0, datetime.combine(d, DECISION_TIME) + timedelta(seconds=1))}
        self.assertEqual(self.table(after, {}).at(1, 5)[sc.SRF_FLAG], 0.0)

    def test_the_decision_instant_is_the_declared_one(self):
        self.assertEqual(DECISION_TIME, time(18, 0))
        self.assertEqual(self.table({}, {})._time, DECISION_TIME)


class ReadTests(unittest.TestCase):
    """A forecast reads the take-up as of its own decision, and refuses a figure that is not."""

    def setUp(self):
        self.d = DAYS[4]
        late = datetime.combine(self.d, time(19, 0))
        self.late_srf = {self.d: sdo.DayFigure(25.0, late)}
        self.on_time_srf = {self.d: sdo.DayFigure(25.0, datetime.combine(self.d, time(13, 46)))}

    def table(self, srf, rrp=None):
        return sdo.SameDayOperationTerms(DAYS, srf, rrp or {})

    @staticmethod
    def serving(table, **fixed):
        """`table` with `at` serving `fixed` terms in place of its own: a figure the check of `read` has to catch."""

        real = table.at
        table.at = lambda lead, row: {**real(lead, row), **fixed}
        return table

    def test_a_record_written_after_the_decision_instant_is_not_read(self):
        # Recorded mutation: see the module docstring (`SameDayOperationTerms.at`).
        t = self.table(self.late_srf)
        for lead in (1, 2, 3):
            self.assertEqual(t.read(lead, 4)[sc.SRF_FLAG], 0.0)

    def test_a_record_written_before_the_decision_instant_is_read(self):
        got = self.table(self.on_time_srf).read(2, 4)
        self.assertEqual(got[sc.SRF_FLAG], 1.0)
        self.assertAlmostEqual(got[sc.SRF_SIZE], 0.25)

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        t = self.table(self.on_time_srf, {DAYS[3]: sdo.DayFigure(40.0, datetime.combine(DAYS[3], time(13, 20))),
                                          self.d: sdo.DayFigure(10.0, datetime.combine(self.d, time(13, 20)))})
        for lead in (1, 2, 3, 4, 5):
            self.assertEqual(t.at(lead, 4 + lead), t.read(lead, 4))

    def test_a_figure_that_counts_a_record_written_after_the_decision_is_refused(self):
        t = self.serving(self.table(self.late_srf), **{sc.SRF_SIZE: 0.25, sc.SRF_FLAG: 1.0})
        with self.assertRaises(LookAheadError):
            t.read(3, 4)

    def test_a_figure_that_leaves_out_a_public_record_is_refused(self):
        t = self.serving(self.table(self.on_time_srf), **{sc.SRF_SIZE: 0.0, sc.SRF_FLAG: 0.0})
        with self.assertRaises(StaleReadError):
            t.read(3, 4)

    def test_a_flag_that_disagrees_with_its_size_is_refused(self):
        t = self.serving(self.table(self.on_time_srf), **{sc.SRF_FLAG: 0.0})
        with self.assertRaises(StaleReadError):
            t.read(3, 4)


class FitTests(unittest.TestCase):

    def pairs(self):
        out = []
        for target in range(5, 17):
            take = 0.4 if target % 3 == 0 else 0.0
            flags = {name: 0 for name in cal.ALL_TERMS}
            out.append(sc.StatePair(3.0 * take, 1.0, flags, 0.0, {"settlement_coupon": 0.0, "settlement_bill": 0.0}, -1, -1,
                                    {sc.SRF_FLAG: 1.0 if take else 0.0, sc.SRF_SIZE: take, sc.RRP_CHANGE: 0.0}))
        return out

    def test_the_terms_enter_the_fit_and_the_shift(self):
        estimate = sc.fit_state_terms(
            self.pairs(), regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=False, training_pairs="direct", min_flagged=3,
            sized=True, extra=sdo.OPS_EXTRAS)
        self.assertIn(sc.SRF_SIZE, estimate.effect)
        self.assertIn(sc.SRF_FLAG, estimate.effect)
        self.assertNotIn(sc.RRP_CHANGE, estimate.effect)  # never non-zero: the term is out of the fit
        self.assertGreater(sc.standardised_shift(estimate, {}, 0.0, {}, {sc.SRF_FLAG: 1.0, sc.SRF_SIZE: 0.4}), 0.0)

    def test_the_terms_are_extra_terms(self):
        for name in sdo.OPS_EXTRAS:
            self.assertIn(name, sc.EXTRA_TERMS)


class ArmTests(unittest.TestCase):

    def test_the_arm_is_the_net_arm_with_the_three_terms_and_nothing_else(self):
        arm, ref = sdo.SAMEDAY_ARM, s3c_announced.ANN_NET_ARM
        self.assertEqual(arm.extra, sdo.OPS_EXTRAS)
        self.assertEqual(dataclasses.replace(arm, name=ref.name, role=ref.role, extra=ref.extra), ref)
        self.assertTrue(arm.sized)

    def test_no_existing_arm_reads_the_new_terms(self):
        for existing in (*sc.ARMS, s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM, s3c_announced.FLAGNET_ARM, s3c_announced.GROSS_ARM):
            self.assertFalse(set(existing.extra) & set(sdo.OPS_EXTRAS))


if __name__ == "__main__":
    unittest.main()
