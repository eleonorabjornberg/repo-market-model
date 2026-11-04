"""The day-type rows report the studentized domain interval beside the current one (#1454; H5, development pages; her ruling of
4 November 2026 on finding #1221, option (a)).

Written first and watched fail (`ModuleNotFoundError: No module named 'repo_model.day_type_interval'`). What these tests pin:

* the floor and the thin label: a day type of fewer than 20 days gets no interval, one of fewer than 60 carries the thin label, one
  of 60 or more neither (the edges 19, 20, 59 and 60 are tested);
* the studentized domain interval of a row is #1266's method (`domain_intervals.studentized_domain_estimates`, the whole aligned
  series resampled, each resample's group mean over its own HAC standard error) on a fixed seed: the row's bounds equal a direct call
  of the estimator, and the group mean and day count are the row's;
* the page record: `domain_rows_of` takes the studentized rows of #1266's record for a re-score's page, and refuses a record whose
  current rows or panel are not the page's; and a day type of fewer than 20 days prints no interval and says so, one of fewer than 60 is labelled thin, and both
  intervals are printed and labelled; a page of a record without domain rows renders as it did.

Mutation (the floor): in `day_type_interval.status`, replacing `days < FLOOR_DAYS` by `days <= FLOOR_DAYS` made
`test_the_edges_of_the_floor_and_of_the_thin_label` fail with `AssertionError: Lists differ: ['none', 'none', 'none', 'thin', 'ok', 'ok'] != ['none', 'none', 'thin', 'thin', 'ok', 'ok']` (20 days).
"""

from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import day_type_interval as dti
from repo_model.domain_intervals import studentized_domain_estimates

ROOT = Path(__file__).resolve().parent.parent


def _load(name):
    """A script as a module, leaving `sys.modules` as it was: other tests' worker pools pickle functions by module name."""

    before = dict(sys.modules)
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        for key in set(sys.modules) - set(before):
            del sys.modules[key]
        for key, value in before.items():
            sys.modules[key] = value
    return module


def series(n, seed):
    rng = random.Random(seed)
    x, out = 0.0, []
    for _ in range(n):
        x = 0.5 * x + rng.gauss(0.0, 1.0)
        out.append(0.3 + x)
    return out


class FloorAndThin(unittest.TestCase):

    def test_the_edges_of_the_floor_and_of_the_thin_label(self):
        self.assertEqual([dti.status(n) for n in (0, 19, 20, 59, 60, 61)], ["none", "none", "thin", "thin", "ok", "ok"])

    def test_a_day_type_under_the_floor_gets_no_interval(self):
        cell = dti.cell(19, {"difference": 0.1, "difference_interval": [0.0, 0.2]}, {"difference": 0.1, "difference_interval": [0.0, 0.2]})
        self.assertEqual(cell, {"days": 19, "status": "none"})

    def test_a_thin_day_type_keeps_both_intervals_and_the_label(self):
        cur = {"difference": 0.1, "difference_interval": [0.0, 0.2]}
        dom = {"difference": 0.1, "difference_interval": [0.01, 0.19]}
        cell = dti.cell(59, cur, dom)
        self.assertEqual((cell["status"], cell["current"], cell["domain"]), ("thin", cur, dom))
        self.assertEqual(dti.cell(60, cur, dom)["status"], "ok")


class StudentizedRows(unittest.TestCase):

    def test_a_row_is_the_studentized_domain_estimate_on_a_fixed_seed(self):
        n = 240
        days = [date(2020, 1, 1) + timedelta(days=i) for i in range(n)]
        d = series(n, 14)
        bench = {day: 5.0 for day in days}
        cand = {day: 5.0 - d[i] for i, day in enumerate(days)}
        group = days[5::24]
        kw = dict(block_length=10, seed=1454, replications=300, level=0.90)
        row = dti.studentized_rows({"g": (bench, cand, group)}, days, seed=1454, draws=300)["g"]
        direct = studentized_domain_estimates({"g": (d, list(range(5, n, 24)))}, n, **kw)["g"]
        self.assertEqual(row["method"], "studentized domain")
        self.assertEqual(row["days"], len(group))
        # d is rebuilt as benchmark - candidate, so the match is to rounding
        self.assertAlmostEqual(row["difference"], direct["mean"], places=12)
        self.assertAlmostEqual(row["difference_interval"][0], direct["interval"]["lower"], places=10)
        self.assertAlmostEqual(row["difference_interval"][1], direct["interval"]["upper"], places=10)
        self.assertAlmostEqual(row["standard_error"], direct["standard_error"], places=10)

    def test_the_script_of_1266_uses_the_same_function(self):
        script = _load("day_type_domain_1266")
        self.assertIs(script.studentized_rows, dti.studentized_rows)

    def test_a_group_day_outside_the_series_is_refused(self):
        days = [date(2020, 1, 1) + timedelta(days=i) for i in range(30)]
        flat = {day: 1.0 for day in days}
        with self.assertRaises(ValueError):
            dti.studentized_rows({"g": (flat, flat, [date(2021, 1, 1)])}, days)


class DomainRowsOf(unittest.TestCase):

    def pair(self):
        cur = {"days": 40, "difference": 0.3, "difference_interval": [0.1, 0.5]}
        stu = {"days": 40, "method": "studentized domain", "difference": 0.3, "difference_interval": [0.0, 0.6]}
        record = {"panel_sha256": "abc", "rows": [{"group": "tax_date", "metric": "grid_crps", "arm": "a", "reference": "B1",
                                                   "current": cur, "studentized": stu}]}
        page = {"panel_sha256": "abc", "groups": {"target_day_type": {"tax_date": {"days": 40, "grid_crps": {"vs": {"a": {"B1": cur}}}}}}}
        return page, record

    def test_the_studentized_rows_are_taken_by_type_metric_arm_and_reference(self):
        page, record = self.pair()
        got = _load("s3_terms_1196").domain_rows_of(page, record)
        self.assertEqual(got["target_day_type"]["tax_date"]["grid_crps"]["a"]["B1"]["difference_interval"], [0.0, 0.6])

    def test_a_record_whose_current_row_differs_from_the_page_is_refused(self):
        page, record = self.pair()
        record["rows"][0]["current"] = dict(record["rows"][0]["current"], difference=0.31)
        with self.assertRaises(ValueError):
            _load("s3_terms_1196").domain_rows_of(page, record)

    def test_a_record_on_another_panel_is_refused(self):
        page, record = self.pair()
        record["panel_sha256"] = "def"
        with self.assertRaises(ValueError):
            _load("s3_terms_1196").domain_rows_of(page, record)


class Page(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script = _load("s3_terms_1196")

    def record(self, days_by_label):
        s = self.script
        vs = {s.A: {"B1": {"days": 1, "difference": 0.3, "difference_interval": [0.1, 0.5], "skill": 0.1, "skill_interval": [0.0, 0.2]}}}
        dom = {s.A: {"B1": {"days": 1, "method": "studentized domain", "difference": 0.3, "difference_interval": [-0.05, 0.65]}}}
        means = {m: 1.0 for m in list(s.BENCHMARKS) + list(s.ARMS)}
        groups = {label: {"days": n, **{m: {"means": means, "vs": vs} for m in s.METRIC_NAMES}} for label, n in days_by_label.items()}
        return {"groups": {"target_day_type": groups}, "gbm": {}, "skipped_groups": {}, "domain_vs": {
            "target_day_type": {label: {m: dom for m in s.METRIC_NAMES} for label in days_by_label}}}

    def test_both_intervals_are_printed_and_labelled_and_a_thin_type_says_so(self):
        r = self.record({"quarter_end": 30, "month_end": 180})
        text = "\n".join(self.script.day_type_interval_lines(r))
        self.assertIn("studentized domain", text)
        self.assertIn("current", text)
        self.assertIn("+0.300 [-0.050, +0.650]", text)
        self.assertIn("+0.300 [+0.100, +0.500]", text)
        label_line = {x.split("**")[1]: x for x in text.splitlines() if x.startswith("**")}
        self.assertIn("thin", label_line["quarter_end"])
        self.assertNotIn("thin", label_line["month_end"])

    def test_a_day_type_under_the_floor_prints_no_interval_and_says_so(self):
        r = self.record({"quarter_end": 19})
        text = "\n".join(self.script.day_type_interval_lines(r))
        self.assertIn("no interval", text)
        self.assertNotIn("[", text.split("**quarter_end**")[1])

    def test_a_record_without_domain_rows_adds_nothing(self):
        r = self.record({"month_end": 180})
        del r["domain_vs"]
        self.assertEqual(self.script.day_type_interval_lines(r), [])


if __name__ == "__main__":
    unittest.main()
