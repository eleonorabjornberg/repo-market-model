"""The H5 registration manifest of #1391: `metadata/h5_registration_manifest.json` and its reader `docs/research/h5-registration-manifest.md`.

The manifest is a DRAFT. It lists every frozen choice of the candidate (s3c-ann-net) with its value and the code that implements it, the inventory of
every model, arm and variant tried on the way to it, and its genealogy. Freezing it is the registration, Eleonora's own `GO`. No figure changes here.

What is pinned:

* every choice names where it lives, and the manifest equals the code: a `code` entry (a dotted path into a `repo_model` module, with `[i]`
  indexes and a trailing `#len`) must evaluate to the declared value, a `json` entry (a file and a dotted path) likewise, and a `text` entry (a
  file and a line that must be in it) is a rule written in code that has no constant to compare;
* the required topics of the issue are all present, so a frozen choice cannot be dropped silently;
* the candidate's arm is the manifest's (the terms, the ridge, the Huber settings, the net sizing, direct pairs);
* every inventory row cites a merged pull request, an existing page and declaration, and every study the candidate's evidence names, and every
  declaration of the families on the way to the candidate, is in the inventory;
* the genealogy is a chain of inventory rows that ends at the candidate;
* the current candidate metadata and module prose no longer say that the decision instant is 16:00 (the historical declarations stay as they are).

Recorded mutation (the manifest-equals-code check): `src/repo_model/spread_mean_reversion.py`, the line `LEVEL_DAYS = 10` changed to
`LEVEL_DAYS = 11`: `ManifestEqualsCodeTests.test_every_code_choice_equals_the_code` fails with `AssertionError` (the choice `level_days` reads 11,
the manifest says 10); restored, it passes. A second mutation, in the stale-wording check: the words "(`repo_model.decision_instant`: 18:00 America/New_York," in the
module docstring of `src/repo_model/s3c_announced.py` put back as "(16:00, the published": `StaleWordingTests.test_no_current_text_says_16_00`
fails with `AssertionError` ('16:00' unexpectedly found); restored, it passes.

Recorded mutation (#1415, the candidate's probability rule): `src/repo_model/s3c_candidate.py`, the line `PROBABILITY_RULE = "open_tail"` changed to
`PROBABILITY_RULE = "status_quo"`: `CandidateProbabilityRuleTests.test_the_candidate_names_rule_b_and_the_default_stays_the_status_quo` fails with
`AssertionError` ('status_quo' != 'open_tail'), as do `test_the_candidates_law_exceedance_and_pit_are_rule_b_not_the_status_quo`,
`test_the_manifest_records_rule_b_pinned_to_the_code` and `ManifestEqualsCodeTests.test_every_code_choice_equals_the_code`; restored, they pass. The
content test `InventoryTests.test_every_declaration_that_names_the_candidate_is_a_row_or_not_an_arm` was run first against main's manifest and failed with
`AssertionError`, naming `b4_quantile_regression_1360`, `cap_tail_rule_1389`, `clustering_thinned_1400`, `day_type_scale_1402`, `h41_per_release_1350` and
`h5_robustness_1364` (and the five files now in `not_arms`).
"""

from __future__ import annotations

import importlib
import json
import re
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "metadata" / "h5_registration_manifest.json"
READER = REPO / "docs" / "research" / "h5-registration-manifest.md"
CANDIDATE = REPO / "docs" / "research" / "h5-candidate.json"

#: The topics the issue lists as frozen choices; each must have at least one choice id starting with the name.
REQUIRED_TOPICS = (
    "decision_instant", "level", "ordinary_days", "training_window", "phi", "min_pairs", "refit", "scale", "huber", "ridge", "terms",
    "calendar_term", "direct_pairs", "residual_pool", "announcement", "net", "cap", "probability", "grid", "horizons",
)
ROLES = {"in_candidate", "tried_not_adopted", "incumbent_replaced", "side_check"}


def resolve(path: str):
    """`module.attr.attr[i]#len` to a value: the module is the longest importable `repo_model.<name>` prefix."""

    length = path.endswith("#len")
    if length:
        path = path[: -len("#len")]
    parts = path.split(".")
    module = importlib.import_module(".".join(parts[:2]))
    value = module
    for part in parts[2:]:
        match = re.fullmatch(r"(\w+)((?:\[\d+\])*)", part)
        value = getattr(value, match.group(1))
        for index in re.findall(r"\[(\d+)\]", match.group(2)):
            value = value[int(index)]
    return len(value) if length else value


def plain(value):
    """Tuples as lists, so that a code constant compares with its JSON."""

    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    return value


def lookup(data, path: str):
    for part in path.split("."):
        if isinstance(data, list) and part.startswith("id="):
            data = next(item for item in data if item["id"] == part[3:])
        else:
            data = data[int(part)] if isinstance(data, list) else data[part]
    return data


class ManifestShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_it_says_it_is_a_draft_and_names_its_issue_and_step(self):
        self.assertEqual(self.m["issue"], 1391)
        self.assertIn("draft", self.m["status"].lower())
        self.assertIn("GO", self.m["status"])
        self.assertIn("H5", self.m["serves"])
        self.assertEqual(self.m["candidate"]["name"], json.loads(CANDIDATE.read_text(encoding="utf-8"))["candidate"])

    def test_choice_ids_are_unique_and_each_choice_has_one_source(self):
        ids = [c["id"] for c in self.m["choices"]]
        self.assertEqual(len(ids), len(set(ids)))
        for c in self.m["choices"]:
            sources = [k for k in ("code", "json", "text") if k in c]
            self.assertEqual(len(sources), 1, c["id"])
            for key in ("what", "value"):
                self.assertIn(key, c, c["id"])

    def test_every_required_topic_has_a_choice(self):
        ids = [c["id"] for c in self.m["choices"]]
        for topic in REQUIRED_TOPICS:
            self.assertTrue(any(i.startswith(topic) for i in ids), f"no choice for the topic {topic!r}")

    def test_the_reader_exists_links_the_manifest_and_says_draft(self):
        text = READER.read_text(encoding="utf-8")
        self.assertIn("metadata/h5_registration_manifest.json", text)
        self.assertIn("draft", text.lower())
        self.assertIn("#1391", text)


class ManifestEqualsCodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_every_code_choice_equals_the_code(self):
        checked = 0
        for c in self.m["choices"]:
            if "code" in c:
                checked += 1
                self.assertEqual(plain(resolve(c["code"])), c["value"], f"{c['id']}: {c['code']}")
        self.assertGreater(checked, 20)

    def test_every_json_choice_equals_its_file(self):
        checked = 0
        for c in self.m["choices"]:
            if "json" in c:
                checked += 1
                data = json.loads((REPO / c["json"]["file"]).read_text(encoding="utf-8"))
                self.assertEqual(lookup(data, c["json"]["path"]), c["value"], c["id"])
        self.assertGreater(checked, 2)

    def test_every_text_choice_is_found_in_its_file(self):
        for c in self.m["choices"]:
            if "text" in c:
                body = (REPO / c["text"]["file"]).read_text(encoding="utf-8")
                self.assertIn(c["text"]["contains"], body, c["id"])

    def test_the_candidate_arm_is_the_manifests(self):
        from repo_model import s3c_announced as ann
        from repo_model import spread_mr_calendar as cal
        from repo_model import spread_mr_state_calendar as sc

        arm = ann.ANN_NET_ARM
        self.assertEqual(arm.name, self.m["candidate"]["walk_arm"])
        self.assertEqual(list(arm.location), list(cal.NO_FOMC_IORB))
        self.assertTrue(arm.robust and arm.sized)
        self.assertFalse(arm.interact)
        self.assertEqual((arm.ridge, arm.extra, arm.calendar_k), (None, (), None))
        self.assertEqual(sc.ridge_of(arm), 5.0)
        self.assertEqual(ann.TRAINING_PAIRS, "direct")
        self.assertEqual(self.m["candidate"]["scored_as"], "sc_s3c_ann_net")

    def test_the_candidate_file_and_the_manifest_agree_on_the_instant_and_the_dating(self):
        h5 = json.loads(CANDIDATE.read_text(encoding="utf-8"))
        self.assertEqual(h5["dating"]["declaration"], self.m["candidate"]["dating_declaration"])
        self.assertEqual(h5["sizing"]["declaration"], self.m["candidate"]["sizing_declaration"])
        self.assertEqual(h5["cap"]["declaration"], self.m["candidate"]["cap_declaration"])


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.rows = cls.m["inventory"]
        cls.by_id = {r["id"]: r for r in cls.rows}

    def test_ids_are_unique_and_roles_are_known(self):
        self.assertEqual(len(self.by_id), len(self.rows))
        for r in self.rows:
            self.assertIn(r["role"], ROLES, r["id"])

    def test_every_row_cites_a_pull_request_a_date_an_outcome_and_files_that_exist(self):
        for r in self.rows:
            self.assertIsInstance(r["pr"], int, r["id"])
            date.fromisoformat(r["merged"])
            for key in ("label", "change", "outcome"):
                self.assertTrue(r[key].strip(), f"{r['id']}: empty {key}")
            for key in ("page", "declaration", "log"):
                if r.get(key):
                    self.assertTrue((REPO / r[key]).is_file(), f"{r['id']}: {key} {r[key]} is not a file")
            self.assertTrue(r.get("page") or r.get("declaration"), f"{r['id']}: neither a page nor a declaration")

    def test_a_row_without_a_page_says_why(self):
        for r in self.rows:
            if not r.get("page"):
                self.assertTrue(r.get("no_page_because"), r["id"])

    def test_the_parent_of_every_row_is_in_the_inventory_or_a_named_reference(self):
        refs = set(self.m["references"])
        for r in self.rows:
            parent = r.get("parent")
            if parent:
                self.assertTrue(parent in self.by_id or parent in refs, f"{r['id']}: parent {parent}")

    def test_the_genealogy_is_a_chain_of_adopted_rows_ending_at_the_candidate(self):
        chain = self.m["genealogy"]
        self.assertEqual(chain[-1], self.m["candidate"]["inventory_id"])
        for step in chain:
            self.assertIn(step, self.by_id)
            self.assertEqual(self.by_id[step]["role"], "in_candidate", step)
        for earlier, later in zip(chain, chain[1:]):
            self.assertEqual(self.by_id[later]["parent"], earlier, later)

    def test_every_study_the_candidate_file_names_is_in_the_inventory(self):
        evidence = {e["issue"] for e in json.loads(CANDIDATE.read_text(encoding="utf-8"))["evidence"]}
        listed = {r["issue"] for r in self.rows} | {r["pr"] for r in self.rows}
        self.assertFalse(evidence - listed, f"evidence studies missing from the inventory: {sorted(evidence - listed)}")

    def test_every_declaration_of_the_families_on_the_way_is_in_the_inventory(self):
        patterns = ("s3c_*_[0-9]*.json", "s3_*_[0-9]*.json", "state_calendar_1145.json", "calendar_mr_1115.json", "fhs_scale_941.json",
                    "faster_scale_1153.json", "sofr_dispersion_1175.json", "regime_spells_1182.json", "walk_calibration_1133.json",
                    "srf_cap_*.json", "spread_distribution_686.json", "spread_distribution_761.json", "spread_distribution_634.json",
                    "aligned_pairs_931.json", "aligned_calendar_1027.json", "aligned_announcement_1124.json", "dom_level_term_1032.json")
        listed = {r.get("declaration") for r in self.rows} | set(self.m["not_arms"])
        found = set()
        for pattern in patterns:
            found |= {str(p.relative_to(REPO)) for p in (REPO / "metadata").glob(pattern)}
        self.assertTrue(found)
        self.assertFalse(found - listed, f"declarations not in the inventory or in `not_arms`: {sorted(found - listed)}")

    def test_every_declaration_that_names_the_candidate_is_a_row_or_not_an_arm(self):
        """Found by content (#1415): a metadata file whose text names the candidate or its builder is an inventory row or a reasoned `not_arms`."""

        names = ("s3c-ann-net", "s3c_ann_net", "s3c_announced")
        listed = {r.get("declaration") for r in self.rows} | set(self.m["not_arms"])
        found = {str(p.relative_to(REPO)) for p in sorted((REPO / "metadata").glob("*.json"))
                 if any(name in p.read_text(encoding="utf-8") for name in names)}
        self.assertTrue(found)
        self.assertFalse(found - listed, f"declarations that name the candidate and are neither a row nor in `not_arms`: {sorted(found - listed)}")
        for path in ("metadata/h5_registration_manifest.json", "metadata/net_settlement.json", "metadata/owner_attestations.json",
                     "metadata/settlement_announcement_dating.json", "metadata/sources.json"):
            self.assertIn(path, self.m["not_arms"])

    def test_the_six_studies_of_1415_are_rows_with_the_right_roles(self):
        expected = {"h5_robustness_1364": ("tried_not_adopted", 1364, 1382), "h41_per_release_1350": ("tried_not_adopted", 1350, 1379),
                    "day_type_scale_1402": ("tried_not_adopted", 1402, 1407), "b4_quantile_regression_1360": ("side_check", 1360, 1380),
                    "cap_tail_rule_1389": ("side_check", 1389, 1395), "clustering_thinned_1400": ("side_check", 1400, 1406)}
        by_decl = {r.get("declaration"): r for r in self.rows}
        for stem, (role, issue, pr) in expected.items():
            row = by_decl.get(f"metadata/{stem}.json")
            self.assertIsNotNone(row, stem)
            self.assertEqual((row["role"], row["issue"], row["pr"]), (role, issue, pr), stem)
            self.assertTrue(row.get("page") and row.get("log"), stem)

    def test_not_arms_names_files_that_exist_and_says_why(self):
        for path, why in self.m["not_arms"].items():
            self.assertTrue((REPO / path).is_file(), path)
            self.assertTrue(why.strip(), path)


class CandidateProbabilityRuleTests(unittest.TestCase):
    """The candidate's probability and PIT path reads rule (b), `open_tail`, from `repo_model.capped_law` (#1415; her ruling of 2 November 2026 on #1395)."""

    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        from datetime import datetime

        from repo_model import policy_events as pe

        cls.register = pe.load_register()
        cls.as_of = datetime(2026, 3, 2, 18, 0)
        cls.target = date(2026, 3, 3)

    def uncapped(self):
        from repo_model.scoring_protocol import GRID

        return [-2.0 + 14.0 * g for g in GRID]

    def line(self):
        from repo_model import s3c_candidate as cand

        line = cand.cap_line(self.register, self.as_of, self.target)
        self.assertIsNotNone(line)
        return line

    def test_the_candidate_names_rule_b_and_the_default_stays_the_status_quo(self):
        from repo_model import capped_law as cl
        from repo_model import s3c_candidate as cand

        self.assertEqual(cand.PROBABILITY_RULE, "open_tail")
        self.assertIn(cand.PROBABILITY_RULE, cl.RULES)
        self.assertEqual(cl.DEFAULT_RULE, "status_quo")

    def test_the_candidates_law_exceedance_and_pit_are_rule_b_not_the_status_quo(self):
        from repo_model import capped_law as cl
        from repo_model import s3c_candidate as cand

        q = self.uncapped()
        line = self.line()
        self.assertGreater(q[-1], line)  # the cap binds on this vector
        law = cand.candidate_law(q, self.register, self.as_of, self.target)
        wanted = cl.emitted_law(q, line, "open_tail", cand.MARGIN_BP)
        status_quo = cl.emitted_law(q, line, "status_quo", cand.MARGIN_BP)
        self.assertEqual(law.points, wanted.points)
        self.assertNotEqual(law.points, status_quo.points)
        for tau in (5.0, 10.0, line - 0.5):
            self.assertEqual(cand.candidate_exceedance(q, self.register, self.as_of, self.target, tau),
                             cl.exceedance(q, line, tau, "open_tail", cand.MARGIN_BP))
        self.assertNotEqual(cand.candidate_exceedance(q, self.register, self.as_of, self.target, line - 0.5),
                            cl.exceedance(q, line, line - 0.5, "status_quo", cand.MARGIN_BP))
        self.assertEqual(cand.candidate_pit_interval(q, self.register, self.as_of, self.target, line),
                         cl.pit_interval(wanted, line))

    def test_without_a_cap_rule_b_and_the_status_quo_coincide(self):
        """No line, no cap: the uncapped secondary (#1361, #1376) reads the same law under either rule."""

        from datetime import datetime

        from repo_model import capped_law as cl
        from repo_model import s3c_candidate as cand

        q = self.uncapped()
        early = datetime(2025, 6, 2, 18, 0)
        self.assertIsNone(cand.cap_line(self.register, early, date(2025, 6, 3)))
        self.assertEqual(cand.candidate_law(q, self.register, early, date(2025, 6, 3)).points,
                         cl.emitted_law(q, None, "status_quo").points)

    def test_no_published_script_reads_the_candidates_rule(self):
        """Scripts that read `capped_law` pass their rule explicitly or take the default (the status quo); none reads the candidate's frozen rule."""

        for path in sorted((REPO / "scripts").glob("*.py")):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("PROBABILITY_RULE", text, path.name)
            self.assertNotIn("candidate_exceedance", text, path.name)

    def test_the_manifest_records_rule_b_pinned_to_the_code(self):
        by_id = {c["id"]: c for c in self.m["choices"]}
        rule, tail = by_id["probability_rule"], by_id["probability_tail_completion"]
        for choice in (rule, tail):
            self.assertNotIn("OPEN:", choice["what"])
        self.assertEqual(rule["value"], "open_tail")
        self.assertEqual(rule["code"], "repo_model.s3c_candidate.PROBABILITY_RULE")
        self.assertEqual(resolve(rule["code"]), "open_tail")
        self.assertIn(resolve(rule["code"]), resolve("repo_model.capped_law.RULES"))
        self.assertEqual(tail["code"], "repo_model.capped_law.OPEN_TAIL_NO_SLOPE")
        self.assertEqual(tail["value"], "bounded")
        self.assertEqual(self.m["open_items"][2].split()[0], "SETTLED")
        self.assertNotIn("OPEN", json.dumps(self.m["open_items"]))
        reader = READER.read_text(encoding="utf-8")
        self.assertIn("open_tail", reader)
        self.assertNotIn("run on at the outer", reader.split("7. **Probability.**")[1].split("\n")[0])


class StaleWordingTests(unittest.TestCase):
    #: Current candidate metadata and module prose. A dated declaration (`metadata/s3c_candidate_1255.json`, `metadata/srf_cap_1241.json`)
    #: is a record of the instant it was made at and keeps its 16:00.
    CURRENT = (
        "docs/research/h5-candidate.json",
        "src/repo_model/s3c_announced.py",
        "src/repo_model/s3c_candidate.py",
        "src/repo_model/s3c_net.py",
        "src/repo_model/net_settlement.py",
    )

    def test_no_current_text_says_16_00(self):
        for path in self.CURRENT:
            text = (REPO / path).read_text(encoding="utf-8")
            self.assertNotIn("16:00", text, path)

    def test_the_srf_line_module_prose_says_the_decision_instant_and_keeps_its_declared_constant(self):
        text = (REPO / "src" / "repo_model" / "srf_line.py").read_text(encoding="utf-8")
        docstring = text.split('"""')[1]
        self.assertNotIn("16:00", docstring)
        self.assertIn("DECISION_TIME = LEGACY_DECISION_TIME", text)


if __name__ == "__main__":
    unittest.main()
