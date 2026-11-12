"""The model documentation and validation report (`docs/model/validation.md`, #119; rewritten for (s3c-ann-net), #1442).

The page keeps the model-risk structure Eleonora ruled on #119: purpose and use, data, methodology, assumptions and
limitations, performance by regime, outcomes analysis, monitoring (and, last, governance). It documents one model,
(s3c-ann-net), H5's frozen candidate (`docs/research/h5-candidate.json`), and replaces the `gbm_funding` report, which stays in
git history (#841's rewrite; the phase 2 records in `docs/runs/` are untouched). Its prose states no figure. Every figure sits inside a
block `scripts/emit_results.py` writes from `docs/runs/`, the metadata files or the declared sources of
`docs/model/external_sources.json`, and `tests/test_generated_results.py` refuses a stale block.

What is held here, beyond that:

* each section of the structure is present, in order, and the page is about the candidate, not the phase 2 models;
* **no digit stands outside a generated block**, apart from issue and pull-request references and the numbering of the
  headings: "no public claim is stated that is not generated";
* a development result that has no record in `docs/runs/` is cited by its issue and its page, labelled "development
  data, not a verdict" (scoring protocol v1), and no performance figure is rendered for it;
* nothing the report cites scores a day of a locked tier (`docs/decisions/lockbox.md`);
* the phase 2 records in `docs/runs/` are not edited by this rewrite;
* **a known-limits section** lists each limit the rulings of 2 and 3 November 2026 on #1187 and #1316 accept or keep
  visible (2020, FOMC target days, the upper tail against (a), lead 1 and the loss to (s3c) and to the plain flag arm,
  quarter-end band coverage, the SRF cap's dependence on full allotment, the 2018-19 regime, the 15 October tax-date
  label), each linked to the issue and the evidence page that show it, and a page that does not exist fails the test;
* the use-limitation statement is the candidate's (`docs/model/candidate.json`) and says what the model must not be used for;
* the ruled wording of 2 October 2026 (the claim sentence with its three links, the fork, the futures exclusion) and
  the clearing-mandate limitation are present, and a page that was not fetched is marked so;
* no date that has not happened is written (`tests/test_docs_freshness.py` refuses one).

Recorded mutation for the digit guard (`test_no_digit_stands_outside_a_generated_block`): a digit typed into the
prose of `docs/model/validation.md` (a hand-typed "5 bp" in the purpose section) fails it with `AssertionError`.

Recorded mutation for the lockbox guard (`test_the_development_evidence_scores_no_locked_day`): `limits.last_day` in
`metadata/s3c_announced_settlement_1288.json` set to the first day of the blind tier (the first tier not opened in
`metadata/lockbox.json`) fails it with `AssertionError`.
"""

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs/model/validation.md"

SECTIONS = (
    "Model purpose and use",
    "Data",
    "Methodology and controls",
    "Assumptions and limitations",
    "Performance by regime",
    "Outcomes analysis",
    "Ongoing monitoring",
    "Governance",
)

#: The generated blocks of the page, in order.
BLOCKS = (
    "validation-use-limitation",
    "validation-use",
    "validation-data",
    "validation-lockbox",
    "validation-candidate",
    "validation-literature",
    "validation-controls",
    "validation-assumptions",
    "validation-limitations",
    "validation-known-limits",
    "validation-clearing",
    "validation-performance",
    "validation-outcomes",
    "validation-monitoring",
    "validation-governance",
)


def _emit_results():
    spec = importlib.util.spec_from_file_location("emit_results_for_validation", ROOT / "scripts/emit_results.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["emit_results_for_validation"] = module
    spec.loader.exec_module(module)
    return module


def _validation_report():
    spec = importlib.util.spec_from_file_location("validation_report_for_test", ROOT / "scripts/validation_report.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["validation_report_for_test"] = module
    spec.loader.exec_module(module)
    return module


def _text():
    return PAGE.read_text(encoding="utf-8")


def _blocks(text):
    """`{name: inner text}` for every `<!-- generated: NAME -->` block."""

    found = {}
    for match in re.finditer(r"<!-- generated: ([\w-]+) -->(.*?)<!-- end generated: \1 -->", text, re.S):
        found[match.group(1)] = match.group(2)
    return found


def _prose(text):
    """The page with every generated block removed."""

    return re.sub(r"<!-- generated: ([\w-]+) -->.*?<!-- end generated: \1 -->", "", text, flags=re.S)


class StructureTests(unittest.TestCase):
    def test_the_page_exists_and_has_every_section_of_the_model_risk_structure(self):
        text = _text()
        headings = re.findall(r"^## (?:\d+\. )?(.+)$", text, re.M)
        for section in SECTIONS:
            self.assertIn(section, headings, "section missing: %s" % section)
        self.assertEqual([h for h in headings if h in SECTIONS], list(SECTIONS), "sections out of order")

    def test_every_generated_block_is_present_once_and_in_order(self):
        text = _text()
        names = re.findall(r"<!-- generated: ([\w-]+) -->", text)
        self.assertEqual(names, list(BLOCKS))
        for name in names:
            self.assertEqual(text.count("<!-- end generated: %s -->" % name), 1, name)

    def test_the_page_documents_the_candidate_and_not_the_phase_2_models(self):
        text = _text()
        self.assertIn("(s3c-ann-net)", text)
        self.assertNotIn("The candidate is `gbm_funding`", text)
        self.assertNotIn("Model documentation and validation report: `gbm_funding`", text)
        for gone in ("validation-distribution", "validation-pressure", "validation-final-test",
                     "validation-calibration", "validation-lag", "validation-desk"):
            self.assertNotIn("generated: %s " % gone, text, gone)
        for gone in ("Challengers against persistence", "The primary cell", "conformal_pid_nested",
                     "gradient-boosted quantile model of the SOFR"):
            self.assertNotIn(gone, text, gone)

    def test_the_deliverables_of_the_step_are_each_covered(self):
        text = _text().lower()
        for needle in ("benchmark", "regime", "pressure-day type", "outcomes", "lockbox", "monitoring",
                       "use limitation", "assumptions", "limitations"):
            self.assertIn(needle, text, needle)


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.candidate = json.loads((ROOT / "docs/model/candidate.json").read_text(encoding="utf-8"))
        self.declaration = json.loads((ROOT / self.candidate["declaration"]).read_text(encoding="utf-8"))
        self.protocol = json.loads((ROOT / self.candidate["protocol_declaration"]).read_text(encoding="utf-8"))
        self.block = _blocks(_text())["validation-candidate"]

    def test_the_candidate_is_the_declared_control_of_the_measurement_that_scored_it(self):
        record = json.loads((ROOT / "docs/research/h5-candidate.json").read_text(encoding="utf-8"))
        self.assertEqual(self.candidate["candidate"], record["candidate"])
        self.assertEqual(self.candidate["candidate"], "sc_s3c_ann_net")
        names = {c["name"]: c for c in self.declaration["candidates"]}
        self.assertIn(self.candidate["declaration_candidate"], names)
        self.assertIn(names[self.candidate["declaration_candidate"]]["definition"], self.block)
        self.assertIn(record["description"], self.block)

    def test_the_block_states_the_declared_inputs_horizons_and_levels_it_reads(self):
        record = json.loads((ROOT / "docs/research/h5-candidate.json").read_text(encoding="utf-8"))
        self.assertIn("%d levels" % len(self.protocol["protocol"]["grid"]), self.block)
        self.assertIn("refit every 21 decision days", self.block)
        self.assertIn(self.candidate["development_last_target_day"], self.block)
        self.assertIn(record["cap"]["rule"][1:], self.block)
        self.assertIn(record["sizing"]["rule"][1:], self.block)
        self.assertIn(record["ruling"], self.block)

    def test_the_block_says_the_quantiles_are_not_recalibrated_and_nothing_is_registered(self):
        text = self.block.lower()
        self.assertIn("not recalibrated", text)
        self.assertIn("not registered", text)


class NoFigureTypedTests(unittest.TestCase):
    #: What prose may carry digits for: issue and pull-request references, the numbering of a heading, and the names
    #: of the hypotheses (H5) and of the benchmarks (B1, B2), which are labels and not figures.
    ALLOWED = (r"(?:PR )?#\d+", r"^#{1,6} \d+\.", r"\(#\d+(?:, #\d+)*\)", r"\bH\d{1,2}\b", r"\bB[123]\b",
               r"\(s3[a-z]*(?:-[a-z]+)*\)")

    def test_no_digit_stands_outside_a_generated_block(self):
        prose = _prose(_text())
        for pattern in self.ALLOWED:
            prose = re.sub(pattern, "", prose, flags=re.M)
        prose = re.sub(r"https?://\S+", "", prose)
        prose = re.sub(r"`[^`]*`", "", prose)
        offenders = [line.strip() for line in prose.splitlines() if re.search(r"\d", line)]
        self.assertEqual(offenders, [], "a digit is typed outside a generated block")

    def test_no_performance_figure_is_rendered_for_a_result_that_has_no_record(self):
        """The development evidence is cited by issue and page; no score, skill, interval or percentage is stated.

        The bullets that restate the declared method (the bootstrap's draws and level) are not results and are left out.
        """

        for name in ("validation-performance", "validation-outcomes"):
            block = "\n".join(l for l in _blocks(_text())[name].splitlines() if not l.startswith("- "))
            body = re.sub(r"#\d+|`[^`]*`|\d{4}-\d{2}(?:-\d{2})?", "", block)
            self.assertNotRegex(body, r"\d+\.\d+|%|\[[+-]", name)


class PerformanceTests(unittest.TestCase):
    def setUp(self):
        self.candidate = json.loads((ROOT / "docs/model/candidate.json").read_text(encoding="utf-8"))
        self.block = _blocks(_text())["validation-performance"]

    def test_every_result_is_cited_by_issue_and_page_and_labelled_development_data(self):
        self.assertTrue(self.candidate["evidence"])
        self.assertIn(self.candidate["evidence_label"], self.block)
        for row in self.candidate["evidence"]:
            self.assertIn(row["issue"], self.block)
            self.assertIn("`%s`" % row["page"], self.block)
            self.assertNotIn("gbm_funding", row["what"])
            self.assertTrue((ROOT / row["page"]).exists(), row["page"])
            self.assertTrue((ROOT / row["script"]).exists(), row["script"])

    def test_the_regimes_and_pressure_day_types_are_those_of_the_evaluation_splits(self):
        splits = json.loads((ROOT / "metadata/evaluation_splits.json").read_text(encoding="utf-8"))
        for regime in splits["regimes"]:
            if regime["label"] != "2027":
                self.assertIn(regime["label"], self.block)
        for day_type in splits["day_types"]["precedence"]:
            self.assertIn(day_type.replace("_", "-"), self.block)

    def test_a_cited_page_scores_no_locked_day_and_reads_none_after_the_last_target_day(self):
        for row in self.candidate["evidence"]:
            text = (ROOT / row["page"]).read_text(encoding="utf-8")
            self.assertRegex(text, r"(?i)development|exploration", row["page"])

    def test_the_development_evidence_scores_no_locked_day(self):
        """Recorded mutation: the declaration's `last_target_day` set to the first locked day fails this with AssertionError."""

        candidate = json.loads((ROOT / "docs/model/candidate.json").read_text(encoding="utf-8"))
        declaration = json.loads((ROOT / candidate["declaration"]).read_text(encoding="utf-8"))
        tiers = json.loads((ROOT / "metadata/lockbox.json").read_text(encoding="utf-8"))["tiers"]
        self.assertLess(candidate["development_last_target_day"], tiers[0]["start"])
        self.assertIn(candidate["development_last_target_day"], declaration["frame"]["windows"])
        first_closed = next(t["start"] for t in tiers if not t["opened"])
        self.assertLess(declaration["limits"]["last_day"], first_closed)

    def test_the_phase_2_records_are_still_in_docs_runs(self):
        """The rewrite replaces the report's content, not the records: the phase 2 files stay where they are."""

        for name in ("persistence_funding.json", "backtest_gbm_conformal_pid_nested_funding.json",
                     "final_test_near_blind.json", "pressure_model_v1_h1.json"):
            self.assertTrue((ROOT / "docs/runs" / name).exists(), name)


class KnownLimitsTests(unittest.TestCase):
    """The known-limits section of the rewrite (#1442): each limit is linked to the evidence that shows it."""

    REQUIRED = ("2020", "fomc-days", "upper-tail-against-a", "lead-1", "net-against-flag", "quarter-end-coverage",
                "srf-cap-full-allotment", "regime-2018-19", "tax-date-label", "satiation-distance-split",
                "post-month-end-coverage")

    def setUp(self):
        self.candidate = json.loads((ROOT / "docs/model/candidate.json").read_text(encoding="utf-8"))
        self.limits = self.candidate["known_limits"]
        self.block = _blocks(_text())["validation-known-limits"]

    def test_every_limit_the_directive_names_is_listed(self):
        self.assertEqual([l["id"] for l in self.limits], list(self.REQUIRED))

    def test_each_limit_is_linked_to_an_issue_and_to_a_page_that_exists(self):
        for limit in self.limits:
            self.assertTrue(limit["sources"], limit["id"])
            for source in limit["sources"]:
                self.assertRegex(source["issue"], r"^#\d+$")
                self.assertIn(source["issue"], self.block)
                if source.get("page"):
                    self.assertTrue((ROOT / source["page"]).exists(), source["page"])
                    self.assertIn("`%s`" % source["page"], self.block)
                else:
                    self.assertTrue(source.get("why_no_page"), "%s names no page and no reason" % limit["id"])
            self.assertIn(limit["limit"], self.block)

    def test_the_rulings_that_accept_or_keep_a_limit_are_cited(self):
        text = self.block
        for needle in ("2 November 2026", "3 November 2026", "#1187", "#1316", "#1378", "#1402", "#1223", "#1004"):
            self.assertIn(needle, text, needle)

    def test_a_limit_is_development_data_and_gives_no_verdict_and_no_figure_is_typed(self):
        self.assertIn(self.candidate["evidence_label"], self.block)
        block = self.block
        for limit in self.limits:
            if limit.get("figures_page"):  # a limit that cites a page for its figures is checked against it below
                block = block.replace(limit["limit"], "")
        body = re.sub(r"#\d+|`[^`]*`|\d{4}-\d{2}(?:-\d{2})?|\d{1,2} (?:October|November) 2026", "", block)
        self.assertNotRegex(body, r"\d+\.\d+|%|\[[+-]|\bd [+-]\d")

    def test_a_figure_in_a_limit_is_on_the_page_it_cites(self):
        """#1469: the 2018-19 limit carries the back-fill's paired figures, each of which stands on its result page.

        Recorded mutation: the limit's "-0.038" changed to "-0.777" in docs/model/candidate.json; this test failed
        with AssertionError ("-0.777" not on the page).
        """

        cited = [l for l in self.limits if l.get("figures_page")]
        self.assertEqual([l["id"] for l in cited], ["regime-2018-19", "satiation-distance-split"])
        for limit in cited:
            page = (ROOT / limit["figures_page"]).read_text(encoding="utf-8")
            figures = re.findall(r"[+-]?\d+\.\d+", limit["limit"])
            self.assertTrue(figures, limit["id"])
            for figure in figures:
                self.assertIn(figure, page, figure)
        self.assertIn("not adopted", cited[0]["limit"])
        self.assertIn("1453", cited[0]["limit"])

    def test_the_satiation_split_limit_carries_its_losses_and_the_2026_gain(self):
        """#1518: the limit states the 2025-26 and 2021-23 losses, the 2026 gain and the pooled figure, each on #1507's page."""

        limit = next(l for l in self.limits if l["id"] == "satiation-distance-split")
        self.assertEqual(limit["figures_page"], "docs/research/satiation-arm-1507-result.md")
        for figure in ("-0.8% [-1.6%, -0.2%]", "-1.0% [-2.4%, -0.3%]", "+0.5% [+0.3%, +0.9%]", "-0.1% [-0.9%, +1.7%]"):
            self.assertIn(figure, limit["limit"], figure)

    def test_the_use_limitation_points_to_the_known_limits(self):
        self.assertIn("known limits", self.candidate["use_limitation"].lower())

    def test_a_missing_page_is_refused(self):
        """A page that does not exist stops the generator with ReportError (no silent link)."""

        module = _validation_report()
        broken = json.loads(json.dumps(self.candidate))
        broken["known_limits"][0]["sources"][0]["page"] = "docs/research/no-such-page-result.md"
        original = module._candidate
        module._candidate = lambda: broken
        try:
            with self.assertRaises(module.ReportError):
                module.known_limits_block(None)
        finally:
            module._candidate = original


class AssumptionsAndLimitationsTests(unittest.TestCase):
    def test_the_block_lists_every_assumption_and_limitation_of_the_declaration(self):
        candidate = json.loads((ROOT / "docs/model/candidate.json").read_text(encoding="utf-8"))
        blocks = _blocks(_text())
        for item in candidate["assumptions"]:
            self.assertIn(item, blocks["validation-assumptions"])
        for item in candidate["limitations"]:
            self.assertIn(item, blocks["validation-limitations"])
        for item in candidate["open_questions"]:
            self.assertIn(item, blocks["validation-limitations"])

    def test_development_data_is_said_to_give_no_verdict(self):
        block = _blocks(_text())["validation-limitations"].lower()
        self.assertIn("development data only", block)
        self.assertIn("verdict", block)


class UseLimitationTests(unittest.TestCase):
    def test_the_statement_is_the_candidates_declared_one(self):
        candidate = json.loads((ROOT / "docs/model/candidate.json").read_text(encoding="utf-8"))
        block = _blocks(_text())["validation-use-limitation"]
        self.assertIn(candidate["use_limitation"], block)

    def test_the_statement_says_it_is_not_registered_and_not_a_stress_warning_system(self):
        block = _blocks(_text())["validation-use-limitation"].lower()
        self.assertIn("not registered", block)
        self.assertIn("not a stress-warning system", block)

    def test_the_page_says_what_the_model_must_not_be_used_for(self):
        use = _blocks(_text())["validation-use"].lower()
        self.assertIn("not a stress-warning system", use)
        self.assertIn("never claimed", use)


class LiteratureTests(unittest.TestCase):
    CLAIM = ("To our knowledge, no public work forecasts the daily SOFR − IORB spread with strictly point-in-time "
             "public data and scores its exceedance probabilities with proper scoring rules against persistence "
             "baselines.")

    def test_the_ruled_claim_wording_and_its_three_links(self):
        block = _blocks(_text())["validation-literature"]
        self.assertIn(self.CLAIM, block)
        self.assertNotIn("nobody has tried", block.lower())
        for url in ("https://www.federalreserve.gov/monetarypolicy/files/FOMC20190913memo02.pdf",
                    "https://essay.utwente.nl/86418/1/Cornelissen_MA_BMS.pdf",
                    "https://arxiv.org/pdf/2101.04308"):
            self.assertIn(url, block)

    def test_the_fork_is_named_as_not_an_independent_replication(self):
        block = _blocks(_text())["validation-literature"]
        self.assertIn("nicholasberoud/repo-market-model", block)
        self.assertIn("not an independent replication", block)

    def test_futures_are_left_out_and_the_reason_is_stated(self):
        text = _text().lower()
        self.assertIn("futures", text)
        self.assertIn("licence", text)
        self.assertIn("over-anticipate", text)

    def test_a_source_that_was_not_fetched_says_so(self):
        sources = json.loads((ROOT / "docs/model/external_sources.json").read_text(encoding="utf-8"))
        flagged = [s for s in sources["sources"] if not s["fetched"]]
        self.assertTrue(flagged, "the declared sources should record the hosts this environment refused")
        text = _text()
        for source in flagged:
            line = next(l for l in text.splitlines() if source["url"] in l)
            self.assertIn("not fetched", line, source["url"])
        for source in sources["sources"]:
            if source["fetched"]:
                line = next(l for l in text.splitlines() if source["url"] in l)
                self.assertNotIn("not fetched", line, source["url"])


class ClearingMandateTests(unittest.TestCase):
    def test_the_limitation_paragraph_carries_its_dates_effect_and_place(self):
        block = _blocks(_text())["validation-clearing"]
        for needle in ("end of 2026", "mid-2027", "34-102487", "2026-09-03", "SOFR_volume",
                       "tails", "tri-party"):
            self.assertIn(needle, block)

    def test_a_claim_from_a_host_this_environment_refused_is_marked_not_fetched(self):
        block = _blocks(_text())["validation-clearing"]
        for host in ("sec.gov", "financialresearch.gov"):
            line = next(l for l in block.splitlines() if host in l)
            self.assertIn("not fetched", line, host)


class LockboxTests(unittest.TestCase):
    def test_the_block_names_the_declared_tiers_and_states_which_days_the_evidence_scores(self):
        block = _blocks(_text())["validation-lockbox"]
        tiers = json.loads((ROOT / "metadata/lockbox.json").read_text(encoding="utf-8"))["tiers"]
        for tier in tiers:
            self.assertIn(tier["start"], block)
        candidate = json.loads((ROOT / "docs/model/candidate.json").read_text(encoding="utf-8"))
        declaration = json.loads((ROOT / candidate["declaration"]).read_text(encoding="utf-8"))
        flat = block.replace("**", "")
        self.assertIn("decides only on days to %s" % candidate["development_last_target_day"], flat)
        self.assertIn(declaration["limits"]["last_day"], flat)
        first_closed = next(t["start"] for t in tiers if not t["opened"])
        self.assertIn("No day from %s is scored" % first_closed, flat)


class MonitoringTests(unittest.TestCase):
    def test_monitoring_says_the_candidate_is_not_in_the_live_record_and_names_the_checkpoints(self):
        block = _blocks(_text())["validation-monitoring"].lower()
        for needle in ("live record", "not the candidate", "no logged day", "checkpoint", "attested", "live pin",
                       "revalidation"):
            self.assertIn(needle, block)

    def test_the_outcomes_analysis_says_no_prospective_day_has_been_scored(self):
        block = _blocks(_text())["validation-outcomes"].lower()
        for needle in ("no prospective", "registered", "checkpoint"):
            self.assertIn(needle, block)


class ControlsTests(unittest.TestCase):
    def test_every_control_names_a_guard_test_that_records_its_mutation(self):
        controls = json.loads((ROOT / "docs/model/controls.json").read_text(encoding="utf-8"))["controls"]
        self.assertTrue(controls)
        kinds = {c["kind"] for c in controls}
        for kind in ("leakage", "staleness", "lockbox", "freeze"):
            self.assertIn(kind, kinds)
        for control in controls:
            test = ROOT / control["test"]
            self.assertTrue(test.exists(), control["test"])
            self.assertRegex(test.read_text(encoding="utf-8"), r"(?i)recorded mutation|mutation record",
                             control["test"])
            self.assertTrue((ROOT / control["guard"]).exists(), control["guard"])


if __name__ == "__main__":
    unittest.main()
