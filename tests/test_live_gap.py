"""The blind gap (#235): the days between the final test and the live record.

Eleonora's ruling of 5 October 2026 on #235 ("Option 2", and "keep reported
only"): the blind-tier target days after the panel end (2026-09-03) and before
the first target day the live record carries at each horizon have been scored
by no record and seen by no model choice. They are scored **once**, on the
first scoring date (2027-04-01), alongside the live record's first scoring,
**reported only**, and labelled "blind but not live".

These tests pin, before any gap day is scored:

* the gap's boundaries at each horizon, read from the first live record's
  targets (`GapBoundaryTests`);
* that no target day is in both the gap and the live record at the same
  horizon (`GapBoundaryTests`);
* that scoring a gap day refuses before 2027-04-01, after it, or while the
  amendment heading is absent from `lockbox.md` (`GapGuardTests`);
* that every gap cell carries its labels verbatim and never reaches the
  verdict (`GapScoringTests`);
* that a reconstructed forecast is never a live record and is never written
  into the live log (`GapRecordTests`).

Red first: this file was committed, and run, before `live_score.py` had any
gap code and before `scripts/live_gap.py` existed; every class failed, at
import (`AttributeError` on `score.GAP_LABEL`) or on the missing script.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from repo_model.data import CALENDAR_COLUMN_RULES, DailyObservation
from repo_model.evaluation_splits import load_split_declaration

from test_live_record import ROOT, SPLITS, _record, _script, live, score

gap = _script("live_gap")

#: Eleonora's label (#235), written here verbatim, not read from the scripts,
#: so that a paraphrase in either script fails.
LABEL = ("blind but not live: forecasts reconstructed after the fact by the frozen code from "
         "inputs fetched at scoring time (latest vintage); reported only, not evidence")
#: Eleonora's label of 4 October 2026 (#229), verbatim.
NOT_EVIDENCE = ("different model from h = 1, and as-of persistence does not widen with "
                "horizon, so this comparison favours the model; not evidence.")
#: `live/2026-10-05.json`'s targets, as logged on `live-log`.
FIRST_LIVE_TARGETS = {1: "2026-10-06", 2: "2026-10-07", 3: "2026-10-08",
                      4: "2026-10-09", 5: "2026-10-13"}


def _first_live_record():
    record = _record("2026-10-05")
    for h, day in FIRST_LIVE_TARGETS.items():
        record["targets"][h - 1]["target_date"] = day
    return record


def _amended_lockbox(tmp):
    path = Path(tmp) / "lockbox.md"
    path.write_text(
        (ROOT / "docs" / "decisions" / "lockbox.md").read_text(encoding="utf-8")
        + "\n" + score.AMENDMENT_HEADING + "\n\nText.\n",
        encoding="utf-8",
    )
    return path


def _gap_record(day, published, persistence):
    """A reconstructed record for decision day `day`, with fixed distributions."""

    record = _record(day.isoformat())
    for h, target in enumerate(live.next_decision_days(day, max(live.HORIZONS)), start=1):
        record["targets"][h - 1]["target_date"] = target.isoformat()
        record["distributions"]["published"]["quantiles_bps"][str(h)] = list(published)
        record["distributions"]["persistence"]["quantiles_bps"][str(h)] = list(persistence)
    record["reconstruction"] = {
        "label": LABEL,
        "scoring_date": "2027-04-01",
        "fetched_at": "2027-04-01T12:00:00+00:00",
    }
    return record


def _outcomes(first, last, spread_bp=1.0):
    rows, current = [], first
    while current <= last:
        if live.is_decision_day(current):
            values = {"sofr": 4.00 + spread_bp / 100, "iorb": 4.00}
            values.update({column: rule(current) for column, rule in CALENDAR_COLUMN_RULES.items()})
            rows.append(DailyObservation(date=current, values=values))
        current = date.fromordinal(current.toordinal() + 1)
    return rows


def _gap_records(published, persistence):
    targets = score.first_live_targets(_first_live_record())
    return [_gap_record(day, published, persistence)
            for day in sorted(score.gap_decision_days(targets))]


def _live_records(published, persistence, days=30):
    out, day = [], date(2026, 10, 5)
    while len(out) < days:
        if live.is_decision_day(day):
            record = _record(day.isoformat())
            for h, target in enumerate(live.next_decision_days(day, max(live.HORIZONS)), start=1):
                record["targets"][h - 1]["target_date"] = target.isoformat()
                record["distributions"]["published"]["quantiles_bps"][str(h)] = list(published)
                record["distributions"]["persistence"]["quantiles_bps"][str(h)] = list(persistence)
            out.append(record)
        day = date.fromordinal(day.toordinal() + 1)
    return out


SHARP = [0.5, 0.8, 1.0, 1.2, 1.5]
WIDE = [-6.0, -2.0, 1.0, 4.0, 9.0]


class GapBoundaryTests(unittest.TestCase):
    """The gap at each horizon: after 2026-09-03, before the first live target day."""

    def test_the_label_is_eleonoras_verbatim(self):
        self.assertEqual(score.GAP_LABEL, LABEL)

    def test_the_gap_runs_from_the_day_after_the_panel_end(self):
        targets = score.first_live_targets(_first_live_record())
        for h in live.HORIZONS:
            with self.subTest(h=h):
                self.assertEqual(score.gap_target_days(h, targets)[0], date(2026, 9, 4))

    def test_the_gap_ends_the_day_before_the_first_live_target(self):
        """h = 1: to 2026-10-05; h = 2 to 5: to the decision day before 10-07, 10-08, 10-09, 10-13."""

        targets = score.first_live_targets(_first_live_record())
        last = {1: date(2026, 10, 5), 2: date(2026, 10, 6), 3: date(2026, 10, 7),
                4: date(2026, 10, 8), 5: date(2026, 10, 9)}
        for h, day in last.items():
            with self.subTest(h=h):
                self.assertEqual(score.gap_target_days(h, targets)[-1], day)

    def test_the_gap_holds_only_decision_days(self):
        targets = score.first_live_targets(_first_live_record())
        days = score.gap_target_days(1, targets)
        self.assertNotIn(date(2026, 9, 7), days)  # Labor Day
        self.assertNotIn(date(2026, 9, 5), days)  # a Saturday
        self.assertTrue(all(live.is_decision_day(day) for day in days))
        self.assertEqual(len(days), len(set(days)))

    def test_the_first_live_targets_are_read_from_the_first_logged_day_only(self):
        with self.assertRaises(ValueError):
            score.first_live_targets(_record("2026-10-06"))

    def test_no_target_day_is_in_both_the_gap_and_the_live_record(self):
        targets = score.first_live_targets(_first_live_record())
        records = _live_records(SHARP, WIDE)
        for h in live.HORIZONS:
            with self.subTest(h=h):
                logged = {date.fromisoformat(record["targets"][h - 1]["target_date"])
                          for record in records}
                in_gap = set(score.gap_target_days(h, targets))
                self.assertEqual(in_gap & logged, set())
                # Together they leave no decision day out: the gap meets the record.
                self.assertEqual(
                    live.next_decision_days(max(in_gap), 1)[0], min(logged)
                )

    def test_every_gap_decision_day_is_before_the_first_logged_day(self):
        targets = score.first_live_targets(_first_live_record())
        days = score.gap_decision_days(targets)
        self.assertLess(max(days), date(2026, 10, 5))
        for h in live.HORIZONS:
            with self.subTest(h=h):
                reached = sorted(
                    live.next_decision_days(day, h)[-1] for day, horizons in days.items()
                    if h in horizons
                )
                self.assertEqual(reached, score.gap_target_days(h, targets))


class GapGuardTests(unittest.TestCase):
    """Scoring a gap day refuses before 2027-04-01, after it, or without the amendment heading.

    The refusal is a `ValueError`, the type the live score's lockbox guard
    (`require_amendment`) raises.

    Mutation record (#235). In a disposable copy, `live_score.require_gap_scoring`'s
    date check (`if day != GAP_SCORING_DATE:`) changed to `if day > GAP_SCORING_DATE:`,
    so a date before 2027-04-01 passes. Killed
    `test_a_date_before_the_first_scoring_date_is_refused` (`AssertionError`:
    `ValueError not raised`) and `test_the_scorer_refuses_before_reading_a_cell`;
    the rest of this module stayed green.
    """

    def test_a_date_before_the_first_scoring_date_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            lockbox = _amended_lockbox(tmp)
            for day in (date(2026, 10, 6), date(2027, 3, 31)):
                with self.subTest(day=day):
                    with self.assertRaises(ValueError):
                        score.require_gap_scoring(day, lockbox)

    def test_a_later_scoring_date_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            lockbox = _amended_lockbox(tmp)
            for day in (date(2027, 4, 2), date(2027, 10, 1), date(2028, 10, 1)):
                with self.subTest(day=day):
                    with self.assertRaises(ValueError):
                        score.require_gap_scoring(day, lockbox)

    def test_the_tracked_lockbox_has_no_amendment_so_the_gap_is_refused(self):
        with self.assertRaises(ValueError):
            score.require_gap_scoring(date(2027, 4, 1), ROOT / "docs" / "decisions" / "lockbox.md")

    def test_the_first_scoring_date_with_the_amendment_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            score.require_gap_scoring(date(2027, 4, 1), _amended_lockbox(tmp))

    def test_the_scorer_refuses_before_reading_a_cell(self):
        records = _gap_records(SHARP, WIDE)
        rows = _outcomes(date(2026, 8, 3), date(2026, 10, 30))
        splits = load_split_declaration(SPLITS)
        with tempfile.TemporaryDirectory() as tmp:
            lockbox = _amended_lockbox(tmp)
            for day, path in ((date(2027, 3, 31), lockbox), (date(2027, 10, 1), lockbox),
                              (date(2027, 4, 1), ROOT / "docs" / "decisions" / "lockbox.md")):
                with self.subTest(day=day, lockbox=path.name):
                    with self.assertRaises(ValueError):
                        score.score_gap(records, _first_live_record(), rows, splits, day,
                                        lockbox=path)

    def test_the_draft_carries_the_gap_bullet_and_its_label(self):
        draft = ROOT / "docs" / "decisions" / "drafts" / "lockbox-live-record.md"
        text = " ".join(draft.read_text(encoding="utf-8").split())
        self.assertIn(LABEL, text)
        self.assertIn("#235", text)


class GapScoringTests(unittest.TestCase):
    """Every gap cell is reported only, carries its labels verbatim and never reaches the verdict."""

    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.lockbox = _amended_lockbox(cls.tmp.name)
        cls.rows = _outcomes(date(2026, 8, 3), date(2026, 12, 31))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _gap(self, published=SHARP, persistence=WIDE):
        return score.score_gap(_gap_records(published, persistence), _first_live_record(),
                               self.rows, self.splits, date(2027, 4, 1), lockbox=self.lockbox)

    def test_each_horizon_scores_exactly_its_gap(self):
        block = self._gap()
        targets = score.first_live_targets(_first_live_record())
        for h in live.HORIZONS:
            with self.subTest(h=h):
                cell = block["crps"][f"crps/h{h}"]
                days = score.gap_target_days(h, targets)
                self.assertEqual(cell["days"], len(days))
                self.assertEqual((cell["first"], cell["last"]),
                                 (days[0].isoformat(), days[-1].isoformat()))

    def test_every_gap_cell_carries_the_label_verbatim(self):
        block = self._gap()
        self.assertEqual(block["label"], LABEL)
        cells = {**block["crps"], **block["cells"]}
        self.assertTrue(cells)
        for name, cell in cells.items():
            with self.subTest(cell=name):
                self.assertEqual(cell["gap_label"], LABEL)

    def test_the_later_horizon_crps_cells_carry_the_not_evidence_label_too(self):
        block = self._gap()
        for h in live.HORIZONS[1:]:
            with self.subTest(h=h):
                self.assertEqual(block["crps"][f"crps/h{h}"]["verdict_label"], NOT_EVIDENCE)
        self.assertNotIn("verdict_label", block["crps"]["crps/h1"])

    def test_every_gap_cell_is_reported_only_and_cannot_pass_or_fail(self):
        block = self._gap()
        for name, cell in {**block["crps"], **block["cells"]}.items():
            with self.subTest(cell=name):
                self.assertEqual(cell["role"], "reported only")
                self.assertNotIn("result", cell)
        self.assertNotIn("primary_result", block)
        self.assertNotIn("headline_status", block)

    def test_the_gap_never_reaches_the_verdict(self):
        """The same live records give the same verdict, whatever the gap shows, or without it."""

        live_records = _live_records(SHARP, WIDE, days=60)
        rows = _outcomes(date(2026, 8, 3), date(2027, 3, 31))
        results = []
        for gap_records in (None, _gap_records(SHARP, WIDE), _gap_records(WIDE, SHARP)):
            result = score.assemble(
                live_records, rows, self.splits, date(2027, 4, 1), previous=[],
                gap_records=gap_records, lockbox=self.lockbox,
            )
            results.append(result)
        verdicts = [(r["primary_result"], r["headline_status"], r["crps"]["crps/h1"]["verdict"])
                    for r in results]
        self.assertEqual(verdicts[0], ("pass", "headline_verdict", "pass"))
        self.assertEqual(len(set(verdicts)), 1)
        for result in results:
            self.assertEqual(result["crps"], results[0]["crps"])
            self.assertEqual(result["cells"], results[0]["cells"])
        # The gap itself moved: the two gap blocks disagree.
        self.assertNotEqual(results[1]["gap"]["crps"]["crps/h1"]["verdict"],
                            results[2]["gap"]["crps"]["crps/h1"]["verdict"])
        self.assertNotIn("gap", results[0])

    def test_the_scoring_output_carries_the_reconstructed_forecasts_and_their_digests(self):
        records = _gap_records(SHARP, WIDE)
        block = self._gap()
        self.assertEqual([entry["decision_day"] for entry in block["forecasts"]],
                         [record["decision_day"] for record in records])
        for entry, record in zip(block["forecasts"], records):
            with self.subTest(day=entry["decision_day"]):
                self.assertEqual(entry["inputs"], record["inputs"])
                self.assertEqual(entry["distributions"], record["distributions"])
                self.assertEqual(entry["models"], record["models"])

    def test_a_live_day_is_never_a_gap_record(self):
        records = _gap_records(SHARP, WIDE)
        late = _gap_record(date(2026, 10, 5), SHARP, WIDE)
        with self.assertRaises(ValueError):
            score.score_gap(records + [late], _first_live_record(), self.rows, self.splits,
                            date(2027, 4, 1), lockbox=self.lockbox)

    def test_the_first_scoring_date_requires_the_gap_and_no_later_date_takes_it(self):
        live_records = _live_records(SHARP, WIDE, days=60)
        rows = _outcomes(date(2026, 8, 3), date(2027, 3, 31))
        with self.assertRaises(ValueError):
            score.assemble(live_records, rows, self.splits, date(2027, 4, 1), previous=[],
                           gap_records=None, lockbox=self.lockbox, require_gap=True)
        with self.assertRaises(ValueError):
            score.assemble(live_records, rows, self.splits, date(2027, 10, 1),
                           previous=[{"date": "2027-04-01", "headline_status": "headline_verdict"}],
                           gap_records=_gap_records(SHARP, WIDE), lockbox=self.lockbox)


class GapRecordTests(unittest.TestCase):
    """A reconstructed forecast is never a live record and never lands in the live log."""

    def test_a_gap_record_validates_as_one(self):
        for record in _gap_records(SHARP, WIDE):
            with self.subTest(day=record["decision_day"]):
                score.validate_gap_record(record)

    def test_a_gap_record_is_never_a_live_record(self):
        record = _gap_records(SHARP, WIDE)[-1]
        with self.assertRaises(ValueError):
            live.validate_record(record)

    def test_a_gap_record_without_the_label_verbatim_is_refused(self):
        for label in (None, LABEL.replace("latest vintage", "latest")):
            with self.subTest(label=label):
                record = _gap_records(SHARP, WIDE)[0]
                if label is None:
                    del record["reconstruction"]
                else:
                    record["reconstruction"]["label"] = label
                with self.assertRaises(ValueError):
                    score.validate_gap_record(record)

    def test_reconstructed_records_are_never_written_into_the_live_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            live_dir = Path(tmp) / "live-log"
            (live_dir / "live").mkdir(parents=True)
            for out in (live_dir, live_dir / "live", live_dir / "gap"):
                with self.subTest(out=out):
                    with self.assertRaises(ValueError):
                        gap.require_outside_live_log(out, live_dir)
            gap.require_outside_live_log(Path(tmp) / "gap-work", live_dir)

    def test_a_gap_record_is_written_once_under_gap_not_live(self):
        record = _gap_records(SHARP, WIDE)[0]
        with tempfile.TemporaryDirectory() as tmp:
            path = gap.write_gap_record(Path(tmp), record, score.validate_gap_record)
            self.assertEqual(path, Path(tmp) / "gap" / f"{record['decision_day']}.json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), record)
            with self.assertRaises(ValueError):
                gap.write_gap_record(Path(tmp), record, score.validate_gap_record)

    def test_the_decision_instant_is_16_00_new_york_time(self):
        self.assertEqual(gap.decision_instant(date(2026, 9, 3)).isoformat(),
                         "2026-09-03T20:00:00+00:00")
        self.assertEqual(gap.decision_instant(date(2026, 11, 2)).isoformat(),
                         "2026-11-02T21:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
