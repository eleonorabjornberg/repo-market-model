"""The results page names its model family from one source and refuses to drift from it (#1532).

Eleonora, 9 November 2026: "I have no idea what our current model family is", and the page's staleness "happens
constantly". #1006 and #1020 had each corrected an out-of-date "current best" by editing text once; nothing tied the page
to the candidate's declaration, `docs/research/h5-candidate.json`. This module is the tie. It fails when

1. a candidate that a result record (`docs/research/*/result.json`, key `candidate`) or an `h5-candidate*.json` file
   names is not in the page source, `h5-candidate.json` (`candidate`, `base`, `known_candidates`);
2. section 1's scores come from a record other than `scores.record` of that source (the record is a page input, so the
   page is digested from it, and the table links it);
3. an open failure listed in the source has no line on the built page, or the line does not carry the figures of the
   failure's own `result.json`.

The page's model prose is rendered from the source and `docs/research/summary.json`; it is not typed into
`site/template.html` or `scripts/research_view.py` (`test_the_template_holds_no_model_prose`).

Recorded mutations (run on a tree with the change in, each with
`PYTHONPATH=src:tests python3 -m unittest test_results_page_source_1532`):

* in `scripts/research_view.py`, `failure_lines`, return `[]` before the loop: `test_every_open_failure_has_a_line_on_the_page`
  failed with AssertionError (the failure's line is not on the page);
* in `scripts/research_view.py`, `input_files`, drop `scores_record(repo)` from the returned list:
  `test_the_scores_come_from_the_record_the_source_names` failed with AssertionError (the named record is not a page input);
* in `docs/research/h5-candidate.json`, delete `"sc_s3c_pd"` from `known_candidates`:
  `test_every_named_candidate_is_in_the_page_source` failed with AssertionError (sc_s3c_pd is named by a result record
  and not by the source).
"""

import html
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
import built_outputs

built_outputs.ensure()

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("research_view", ROOT / "scripts" / "research_view.py")
research_view = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(research_view)

SOURCE = "docs/research/h5-candidate.json"
PAGE = (ROOT / "site" / "index.html").read_text(encoding="utf-8")


def source(root=ROOT):
    return json.loads((Path(root) / SOURCE).read_text(encoding="utf-8"))


def visible(text):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)))


def named_candidates(root=ROOT):
    """Every candidate id a result record or a candidate file names."""
    found = {}
    for path in sorted(Path(root, "docs/research").glob("*/result.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(doc, dict) and isinstance(doc.get("candidate"), str):
            found.setdefault(doc["candidate"], str(path.relative_to(root)))
    for path in sorted(Path(root, "docs/research").glob("h5-candidate*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for key in ("candidate", "base"):
            if isinstance(doc.get(key), str):
                found.setdefault(doc[key], str(path.relative_to(root)))
    return found


class OneSource(unittest.TestCase):
    def test_every_named_candidate_is_in_the_page_source(self):
        src = source()
        in_source = {src["candidate"], src["base"], *src.get("known_candidates", ())}
        for name, where in named_candidates().items():
            self.assertIn(name, in_source, f"{where} names the candidate {name}, which {SOURCE} does not")

    def test_a_new_candidate_in_a_result_record_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(ROOT / "docs/research", Path(tmp) / "docs/research",
                            ignore=shutil.ignore_patterns("log", "*.md"))
            fresh = Path(tmp) / "docs/research/some-study-9999"
            fresh.mkdir()
            (fresh / "result.json").write_text(json.dumps({"candidate": "sc_brand_new"}), encoding="utf-8")
            src = source(tmp)
            self.assertNotIn("sc_brand_new", {src["candidate"], src["base"], *src.get("known_candidates", ())})
            self.assertIn("sc_brand_new", named_candidates(tmp))

    def test_the_scores_come_from_the_record_the_source_names(self):
        record = source()["scores"]["record"]
        self.assertIn(record, research_view.input_files(ROOT))
        self.assertFalse(hasattr(research_view, "CANDIDATE_SCORES"), "a second, typed path to the scores")
        st = research_view.standings(ROOT)
        self.assertEqual(st["record"], record)
        self.assertIn(research_view.BLOB + record, PAGE)

    def test_the_scores_follow_the_source_when_it_names_another_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            for rel in (SOURCE, research_view.SUMMARY, source()["scores"]["record"]):
                (Path(tmp) / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / rel, Path(tmp) / rel)
            other = "docs/research/elsewhere/result.json"
            (Path(tmp) / other).parent.mkdir(parents=True)
            shutil.copy(ROOT / source()["scores"]["record"], Path(tmp) / other)
            doc = source(tmp)
            doc["scores"]["record"] = other
            (Path(tmp) / SOURCE).write_text(json.dumps(doc), encoding="utf-8")
            self.assertEqual(research_view.standings(tmp)["record"], other)
            self.assertIn(other, research_view.scores_record(tmp))

    def test_every_open_failure_has_a_line_on_the_page(self):
        failures = source().get("open_failures")
        self.assertTrue(failures, f"{SOURCE} lists no open failure")
        text = visible(PAGE)
        lines = research_view.failure_lines(ROOT)
        self.assertEqual([f["key"] for f in failures], [key for key, _ in lines])
        for key, line in lines:
            self.assertIn(visible(line), text, f"the open failure {key} has no line on the page")
        for f in failures:
            self.assertTrue((ROOT / f["result_json"]).is_file(), f["result_json"])
            self.assertIn(f["page"], PAGE, f"the line for {f['key']} does not link its result page")

    def test_a_failure_line_carries_the_figures_of_its_result_json(self):
        for f in source()["open_failures"]:
            record = json.loads((ROOT / f["result_json"]).read_text(encoding="utf-8"))
            for name, path in f["values"].items():
                node = record
                for step in path:
                    node = node[step]
                shown = research_view.format_value(node)
                self.assertIn(shown, dict(research_view.failure_lines(ROOT))[f["key"]], name)

    def test_every_passed_check_has_a_line_with_the_figures_of_its_records(self):
        """#1574: a check the candidate passes is shown from records too, and a figure of another record is read
        from that record."""
        passed = source().get("passed", ())
        lines = dict(research_view.passed_lines(ROOT, links=True))
        self.assertEqual([p["key"] for p in passed], list(lines))
        text = visible(PAGE)
        for p in passed:
            self.assertIn(visible(dict(research_view.passed_lines(ROOT))[p["key"]]), text)
            self.assertIn(p["page"], lines[p["key"]])
            for name, spec in p["values"].items():
                rel, path = (spec["result_json"], spec["path"]) if isinstance(spec, dict) else (p["result_json"], spec)
                self.assertIn(rel, research_view.input_files(ROOT), "the record is not a page input")
                node = json.loads((ROOT / rel).read_text(encoding="utf-8"))
                for step in path:
                    node = node[step]
                percent = isinstance(spec, dict) and spec.get("percent")
                shown = f"{100 * node:.1f}%" if percent else research_view.format_value(node)
                self.assertIn(shown, lines[p["key"]], name)

    def test_a_check_is_not_both_passed_and_failing(self):
        src = source()
        self.assertFalse({p["key"] for p in src.get("passed", ())} & {f["key"] for f in src["open_failures"]})

    def test_the_page_names_the_incumbent_the_candidate_and_whether_it_is_registered(self):
        src = source()
        plain = json.loads((ROOT / research_view.SUMMARY).read_text(encoding="utf-8"))
        text = visible(PAGE)
        self.assertIn(html.unescape(plain["candidate"]["description"]), text)
        self.assertIn(plain["models"][src["incumbent"]["id"]]["name"], text)
        self.assertFalse(src["state"]["registered"])
        self.assertIn("is not registered", text)
        self.assertIn(research_view.long_date(src["state"]["frozen"]), text)
        # the same current-model paragraph opens the executive summary and section 1
        self.assertEqual(PAGE.count('class="rs-current"'), 2)
        self.assertLess(PAGE.find('class="rs-current"'), PAGE.find('id="best-performer"'))

    def test_the_template_holds_no_model_prose(self):
        template = (ROOT / "site/template.html").read_text(encoding="utf-8")
        self.assertIn("{{research_limits}}", template)
        for stale in ("not yet fully calibrated", "still too narrow", "near-blind, since its days"):
            self.assertNotIn(stale, template)  # carried by `current_model.limits` of the plain wording instead
        view = (ROOT / "scripts/research_view.py").read_text(encoding="utf-8")
        for stale in ("No candidate has been registered yet", "the incumbent stands: the project"):
            self.assertNotIn(stale, view)

    def test_a_failure_without_a_plain_line_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            for rel in (SOURCE, research_view.SUMMARY):
                (Path(tmp) / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / rel, Path(tmp) / rel)
            for f in source()["open_failures"]:
                (Path(tmp) / f["result_json"]).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / f["result_json"], Path(tmp) / f["result_json"])
            plain = json.loads((Path(tmp) / research_view.SUMMARY).read_text(encoding="utf-8"))
            plain["current_model"]["failures"].pop(source()["open_failures"][0]["key"])
            (Path(tmp) / research_view.SUMMARY).write_text(json.dumps(plain), encoding="utf-8")
            with self.assertRaises(research_view.ResearchError):
                research_view.failure_lines(tmp)


if __name__ == "__main__":
    unittest.main()
