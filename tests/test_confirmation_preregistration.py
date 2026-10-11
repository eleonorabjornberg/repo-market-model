"""The pre-registration of the three frozen candidates for the 2026 confirmation window (#585, ruling on #567).

`metadata/confirmation_preregistration.json` freezes what is scored; `repo_model.confirmation` checks it. Held here:

* the file says what the judge's declaration and the candidate files say (the window, the three names, their
  features), and every file hash in it matches the tree: a change to a frozen declaration, to the judge, or to the
  code a candidate runs under fails here until the pre-registration is amended by a decision;
* the guard `require_confirmation_open` refuses a confirmation-window day for a frozen candidate until the judge's
  `confirmation.candidates` names it (the owner-attested opening, #256), refuses a day of the blind tier whatever the
  declaration says, refuses a window whose frozen files changed, and refuses any name that is not one of the three;
* nothing here scores a day.

**Recorded mutations** (CLAUDE.md: a new leakage guard carries one). In `repo_model.confirmation.require_confirmation_open`,
replace `if candidate not in named:` by `if False:` (the judge's naming is not required); the failing test was
`test_a_window_day_is_refused_until_the_judge_names_the_candidate`, which raised `AssertionError: LookAheadError not raised`.
Replace `problems = verify(root=REPO)` by `problems = []` (the frozen hashes are not read); the failing test was
`test_a_changed_frozen_file_refuses_the_window`, which raised `AssertionError: LookAheadError not raised`. Replace
`lockbox.require_unlocked(days, where=where)` by `pass` (the lockbox is not asked); the failing test was
`test_a_blind_tier_day_is_refused_even_when_the_judge_names_the_candidate`, which raised
`AssertionError: 'blind' not found in 'test: scored day 2026-09-04 is outside the pre-registered confirmation window ...'`
(the window check alone still refused the day; the lockbox is the second, independent refusal).
"""

import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from repo_model import confirmation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).parents[1]
FROZEN = (
    "risk_gbm+every_day+gate+settle+h41+iorb",
    "risk_gbm+settle+h41",
    "ngboost_laplace",
)


def _preregistration():
    return json.loads((ROOT / "metadata" / "confirmation_preregistration.json").read_text(encoding="utf-8"))


class DeclarationTests(unittest.TestCase):
    def test_the_three_candidates_are_the_ones_eleonora_froze(self):
        self.assertEqual(tuple(c["name"] for c in _preregistration()["candidates"]), FROZEN)

    def test_the_window_is_the_judges_confirmation_window(self):
        judge = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text(encoding="utf-8"))
        window = _preregistration()["window"]
        self.assertEqual((window["first"], window["last"]), (judge["confirmation"]["first"], judge["confirmation"]["last"]))
        self.assertEqual((window["first"], window["last"]), ("2026-01-01", "2026-09-03"))

    def test_each_candidate_is_a_declared_candidate_with_the_features_the_file_states(self):
        for entry in _preregistration()["candidates"]:
            declared = json.loads(
                (ROOT / "metadata" / "pressure_judge" / "candidates" / f"{entry['name']}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(declared["role"], "candidate", entry["name"])
            self.assertEqual(entry["features"], declared["features"], entry["name"])
            self.assertEqual(entry["declaration"], f"metadata/pressure_judge/candidates/{entry['name']}.json")

    def test_every_candidate_names_its_inputs_availability_declarations(self):
        for entry in _preregistration()["candidates"]:
            self.assertTrue(entry["availability_declarations"], entry["name"])
            for path in entry["availability_declarations"]:
                self.assertTrue((ROOT / path).is_file(), path)
                self.assertIn(path, entry["files"], path)

    def test_the_frozen_commit_is_a_full_sha(self):
        commit = _preregistration()["frozen_at"]["commit"]
        self.assertRegex(commit, r"^[0-9a-f]{40}$")

    def test_the_pending_amendments_are_named_and_not_applied(self):
        pending = _preregistration()["judge"]["pending_amendments"]
        self.assertTrue(pending)
        for amendment in pending:
            self.assertFalse(amendment["applied"], amendment)

    def test_the_comparison_corrects_for_three_candidates(self):
        comparison = _preregistration()["comparison"]
        self.assertEqual(comparison["family_size"], 3)
        self.assertIn("Bonferroni", comparison["correction"])
        self.assertEqual(comparison["benchmarks"], ["calendar_climatology", "persistence_logistic"])


class FreezeTests(unittest.TestCase):
    def test_the_tree_matches_every_frozen_hash(self):
        self.assertEqual(confirmation.verify(), [])

    def test_the_panel_digest_is_the_manifests(self):
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(_preregistration()["panel"]["sha256"], manifest["sha256"])

    def test_the_judge_declaration_digest_ignores_only_the_confirmation_candidates(self):
        path = ROOT / "metadata" / "pressure_judge.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        named = json.loads(path.read_text(encoding="utf-8"))
        named["confirmation"]["candidates"] = list(FROZEN)
        self.assertEqual(confirmation.judge_declaration_digest(document), confirmation.judge_declaration_digest(named))
        named["thresholds_bp"] = [5, 11]
        self.assertNotEqual(confirmation.judge_declaration_digest(document), confirmation.judge_declaration_digest(named))

    def test_a_changed_frozen_file_is_named(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            self._copy_frozen(root)
            self.assertEqual(confirmation.verify(root=root), [])
            target = root / "metadata" / "pressure_judge" / "candidates" / "ngboost_laplace.json"
            target.write_text(target.read_text(encoding="utf-8") + " ", encoding="utf-8")
            problems = confirmation.verify(root=root)
            self.assertEqual(len(problems), 1)
            self.assertIn("ngboost_laplace.json", problems[0])

    def test_a_missing_frozen_file_is_named(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            self._copy_frozen(root)
            (root / "metadata" / "weighted_miss.json").unlink()
            self.assertTrue(any("weighted_miss.json" in problem for problem in confirmation.verify(root=root)))

    @staticmethod
    def _copy_frozen(root):
        for path in confirmation.frozen_paths():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)


class GuardTests(unittest.TestCase):
    """The guard reads the judge's declaration and the frozen files at call time, as `lockbox.require_unlocked` does."""

    WINDOW_DAY = date(2026, 2, 2)

    def _opened(self, scratch, names=FROZEN):
        root = Path(scratch)
        FreezeTests._copy_frozen(root)
        path = root / "metadata" / "pressure_judge.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["confirmation"]["candidates"] = list(names)
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        return root

    def test_a_window_day_is_refused_until_the_judge_names_the_candidate(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            FreezeTests._copy_frozen(root)
            with mock.patch.object(confirmation, "REPO", root):
                for name in FROZEN:
                    with self.assertRaises(LookAheadError, msg=name) as caught:
                        confirmation.require_confirmation_open(name, [self.WINDOW_DAY], where="test")
                    self.assertIn("confirmation.candidates", str(caught.exception))

    def test_a_window_day_is_scored_once_the_judge_names_the_candidate(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = self._opened(scratch)
            with mock.patch.object(confirmation, "REPO", root):
                for name in FROZEN:
                    confirmation.require_confirmation_open(name, [self.WINDOW_DAY, date(2026, 9, 3)], where="test")

    def test_naming_one_candidate_opens_only_that_one(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = self._opened(scratch, names=("ngboost_laplace",))
            with mock.patch.object(confirmation, "REPO", root):
                confirmation.require_confirmation_open("ngboost_laplace", [self.WINDOW_DAY], where="test")
                with self.assertRaises(LookAheadError):
                    confirmation.require_confirmation_open("risk_gbm+settle+h41", [self.WINDOW_DAY], where="test")

    def test_a_changed_frozen_file_refuses_the_window(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = self._opened(scratch)
            target = root / "metadata" / "weighted_miss.json"
            target.write_text(target.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with mock.patch.object(confirmation, "REPO", root):
                with self.assertRaises(LookAheadError) as caught:
                    confirmation.require_confirmation_open("ngboost_laplace", [self.WINDOW_DAY], where="test")
                self.assertIn("weighted_miss.json", str(caught.exception))

    def test_a_blind_tier_day_is_refused_even_when_the_judge_names_the_candidate(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = self._opened(scratch)
            with mock.patch.object(confirmation, "REPO", root):
                with self.assertRaises(LookAheadError) as caught:
                    confirmation.require_confirmation_open("ngboost_laplace", [date(2026, 9, 4)], where="test")
                self.assertIn("blind", str(caught.exception))

    def test_a_day_before_the_window_is_refused(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = self._opened(scratch)
            with mock.patch.object(confirmation, "REPO", root):
                with self.assertRaises(LookAheadError):
                    confirmation.require_confirmation_open("ngboost_laplace", [date(2025, 12, 31)], where="test")

    def test_a_name_that_is_not_frozen_is_refused(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = self._opened(scratch)
            with mock.patch.object(confirmation, "REPO", root):
                with self.assertRaises(ValueError):
                    confirmation.require_confirmation_open("risk_gbm", [self.WINDOW_DAY], where="test")


if __name__ == "__main__":
    unittest.main()
