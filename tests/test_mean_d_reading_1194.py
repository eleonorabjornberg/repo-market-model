"""H5 reporting (#1194): the #1145 page is read on the studentized bound on mean d, not the skill interval.

Her ruling on #1009 (comment 6291059408, 20 October 2026): a development page reports both intervals and reads the mean-d bound;
her ruling on finding #1187 (24 October 2026, relayed): (s3) stays the candidate, the pages are corrected, and its two upper-tail
losses (2020, FOMC days) are an open question before any H5 registration. This module pins: `scripts/state_calendar_1145.py` reads
the mean-d bound (the first page is what `reading="skill"` gives); `scripts/mean_d_reading_1194.py` reads every paired row of the
committed `docs/research/state-calendar-1145/result.json` without a re-run and lists the readings that change, among them (s3)
against (a) on upper-tail twCRPS in 2020 and on FOMC days; #1172's reading section carries the twCRPS readings; every page states
Lens C's caveat; `docs/research/h5-candidate.json` links the mean-d pages; and the tracked page and record are what the script writes.

Red on main: `scripts/mean_d_reading_1194.py` does not exist there, `verdict` of the 1145 script reads the skill interval, #1172's
reading section reads grid CRPS only, and the candidate record links no mean-d page.

Recorded mutation (2026-10-24), for `scripts/mean_d_reading_1194.py`: in `candidate_readings`, replacing
`mean_d_reading_1167.verdict_words(row)` with `mean_d_reading_1167.skill_words(row)` made
`test_the_candidate_reads_a_loss_on_upper_tail_twcrps_in_2020_and_on_fomc_days` fail with AssertionError (Lists differ: [('undecided', 'undecided')] != [('undecided', 'loss')]),
and `test_the_tracked_page_and_record_are_what_the_script_writes` fail with AssertionError (1 != 0: the page differed from the one written).
Restored, both pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    if name in sys.modules:  # keep the object another module registered (a worker pool pickles functions by module name)
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


script = load("mean_d_reading_1194", "mean_d_reading_1194.py")
base = load("mean_d_reading_1167", "mean_d_reading_1167.py")


def record():
    return json.loads(script.SOURCE.read_text(encoding="utf-8"))


def cell(split, label, metric, ref):
    return record()["groups"][split][label][metric]["vs"]["sc_s3_robust"][ref]


class CandidateReadingTests(unittest.TestCase):

    def test_the_candidate_reads_a_loss_on_upper_tail_twcrps_in_2020_and_on_fomc_days(self):
        for split, label in (("regime", "2020"), ("target_day_type", "fomc_day")):
            row = cell(split, label, "upper_tail_twcrps", "mr_cal_a_base")
            self.assertEqual(base.skill_words(row), "undecided", label)
            self.assertEqual(base.verdict_words(row), "loss", label)
            found = [c for c in script.candidate_readings(record())
                     if (c["split"], c["label"], c["metric"]) == (split, label, "upper_tail_twcrps")]
            self.assertEqual([(c["was"], c["now"]) for c in found], [("undecided", "loss")], label)

    def test_the_other_changes_the_finding_names(self):
        quarter = cell("target_day_type", "quarter_end", "upper_tail_twcrps", "mr_cal_a_base")
        self.assertEqual((base.skill_words(quarter), base.verdict_words(quarter)), ("gain", "undecided"))
        for metric in ("grid_crps", "upper_tail_twcrps"):
            row = cell("regime", "2018-19", metric, "mr_cal_a_base")
            self.assertEqual((base.skill_words(row), base.verdict_words(row)), ("undecided", "gain"), metric)

    def test_the_regime_line_is_the_one_on_the_mean_d_bound(self):
        line = script.regime_line(record())
        self.assertEqual(line["grid_crps"], {"2018-19": "gain", "2020": "undecided", "2021-23": "gain", "2024": "gain", "2025-26": "gain"})
        self.assertEqual(line["upper_tail_twcrps"]["2020"], "loss")
        self.assertEqual(line["upper_tail_twcrps"]["2018-19"], "gain")


class RecordTests(unittest.TestCase):

    def test_every_paired_row_is_read_with_both_intervals_and_nothing_is_dropped(self):
        rows = base.collect(record())
        self.assertGreater(len(rows), 1000)
        built = json.loads(script.build()["record"])
        self.assertEqual(built["paired_rows"], len(rows))
        self.assertEqual(built["rows_changed"], sum(r["changed"] for r in rows))
        self.assertGreater(built["rows_changed"], 0)

    def test_the_regime_and_pooled_readings_changed_are_the_findings_fifty(self):
        """Finding #1187: of 319 regime and pooled readings, 50 change side."""

        built = json.loads(script.build()["record"])
        self.assertEqual((built["regime_and_pooled_rows"], built["regime_and_pooled_changed"]), (319, 50))


class PageTests(unittest.TestCase):

    def test_the_page_shows_both_intervals_the_caveat_and_every_changed_reading(self):
        page = script.render(record())
        self.assertIn("understated about 2×", page)
        self.assertIn("optimistic", page)
        self.assertIn("skill [90%]", page)
        self.assertIn("mean d [90%]", page)
        rows = base.collect(record())
        changed = [r for r in rows if r["changed"]]
        body = page.split("## Readings that change", 1)[1].split("## All paired rows", 1)[0]
        self.assertEqual(body.count("\n| "), len(changed) + 1)
        self.assertIn("## The candidate (s3) against (a)", page)
        self.assertIn("open question", page.lower())

    def test_the_first_page_stands_and_is_not_written(self):
        self.assertNotEqual(script.PAGE.name, "state-calendar-1145-result.md")
        self.assertTrue(script.PAGE.name.endswith("-mean-d-1194-result.md"))

    def test_the_tracked_page_and_record_are_what_the_script_writes(self):
        self.assertEqual(script.main(["check"]), 0)


class ReadingSectionOf1172Tests(unittest.TestCase):
    """Loaded when the tests run, not at import: another test module registers the 1172 script's helpers by module name first."""

    @classmethod
    def setUpClass(cls):
        global s1172
        # the 1172 script re-registers the 1115, 967, 1145 and scarcity scripts under their module names as it loads, which
        # breaks the worker pool of the module that registered them first (the shard order puts this module before it):
        # put every name back as it was found.
        before = dict(sys.modules)
        try:
            s1172 = load("s3_decomposition_1172", "s3_decomposition_1172.py")
        finally:
            for name in [n for n in sys.modules if n not in before]:
                del sys.modules[name]
            for name, module in before.items():
                if sys.modules.get(name) is not module:
                    sys.modules[name] = module

    def test_the_reading_section_adds_the_twcrps_readings(self):
        data = json.loads((ROOT / "docs/research/s3-decomposition-1172/result.json").read_text(encoding="utf-8"))
        page = s1172.render(data)
        section = page.split("## Reading under the declared rules", 1)[1].split("\n## ", 1)[0]
        self.assertIn("upper-tail twCRPS", section)
        s3_lines = [l for l in section.splitlines() if l.startswith("- **(s3)") and "against (a)" in l and "twCRPS" in l]
        self.assertEqual(len(s3_lines), 1)
        self.assertIn("2020: loss (skill interval: undecided)", s3_lines[0])
        self.assertIn("fomc_day: loss (skill interval: undecided)", s3_lines[0])

    def test_the_tracked_page_is_what_the_script_gives(self):
        data = json.loads((ROOT / "docs/research/s3-decomposition-1172/result.json").read_text(encoding="utf-8"))
        self.assertEqual(s1172.render(data), (ROOT / "docs/research/s3-decomposition-1172-result.md").read_text(encoding="utf-8"))


class CandidateRecordTests(unittest.TestCase):

    def test_the_evidence_links_the_mean_d_pages(self):
        rec = json.loads((ROOT / "docs/research/h5-candidate.json").read_text(encoding="utf-8"))
        pages = {e["issue"]: e["mean_d_page"] for e in rec["evidence"] if e.get("mean_d_page")}  # #1255's page is its own reading
        self.assertEqual(pages, {1145: "docs/research/state-calendar-1145-mean-d-1194-result.md",
                                 1115: "docs/research/calendar-mr-1115-mean-d-1167-result.md",
                                 1141: "docs/research/walk-calibration-1133-mean-d-1167-result.md"})
        for page in pages.values():
            self.assertTrue((ROOT / page).is_file(), page)
        self.assertIn("mean d", rec["note"])


if __name__ == "__main__":
    unittest.main()
