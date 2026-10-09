"""The live scorer is frozen the way the final test's CRPS functions are (#282, ruling on #269 item 5).

`scripts/live_score.py` carries its own declaration (`live_declaration`) and checksum
(`live_declaration_checksum`): the SHA-256 of every top-level definition the scoring functions
reach, in `live_score.py` and in the modules they call into. It covers the cells (`score`,
`score_crps`, the group cells), the intervals (`_paired`, `_paired_cell`, `stationary_bootstrap_interval`,
the seeds), the minimum-cell rule (`_small_cell`), the regime and month-end splits
(`_regime`, `SplitDeclaration`, `MONTH_END_RULE`) and the gap scoring (`score_gap` and its
helpers). The checksum is pinned in the draft amendment `docs/decisions/drafts/lockbox-live-record.md`
(for her to merge), with the commit it was taken at.

What is held here:

* the checksum is the pinned one (`PinnedTests`);
* every top-level definition of `live_score.py` is either covered or on an explicit list of the
  ones that score nothing, so a new scoring function cannot be added outside the checksum
  (`CoverageTests`);
* an edit to any covered function, or to the one it calls in another module, moves the checksum
  (`EditTests`); a changed constant moves it too;
* the final test's two checksums are not touched (`test_the_final_test_checksums_are_untouched`).

Recorded mutations, each confirmed applied (`git diff`) and restored afterwards:

* in `scripts/live_score.py`, `_small_cell`'s `if len(positions) >= MINIMUM_CELL_DAYS:` changed to `>` ->
  the checksum moves to `d94baa29\u2026` and `test_the_checksum_is_the_pinned_one` fails with
  `AssertionError` (so do the per-function edit tests that compare against the pin);
* a new `def extra_cell(x): return x` appended to `live_score.py`, covered by nothing ->
  `test_every_definition_of_the_scorer_is_covered_or_scores_nothing` fails with `AssertionError`
  (`['extra_cell'] != []`).

Red first: before the change the module had no `live_declaration`, and the tests failed with
`AttributeError`.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "live_score.py"
DRAFT = ROOT / "docs" / "decisions" / "drafts" / "lockbox-live-record.md"


def _script(name):
    spec = importlib.util.spec_from_file_location(f"live_freeze_{name}", ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ls = _script("live_score")

#: Top-level names of live_score.py that score nothing: the clock and scoring-date guards, the
#: live-log integrity and pin loaders, provenance and the command line. They are guarded and
#: tested elsewhere; every other definition is a scoring function and is in the checksum.
NOT_SCORING = {
    "_live", "_integrity", "_pins", "load_records", "_final_test", "now_utc", "today_new_york",
    "require_clock", "is_scoring_date", "require_scoring_date", "_code_sha", "_sha256_bytes",
    "build_provenance", "_raw", "main", "live_declaration", "live_declaration_checksum",
    "_LIVE", "_INTEGRITY", "_PINS", "_RAW", "_OPENING", "REPO", "SPLITS", "LOCK", "EASTERN",
    "FIRST_SCORING_DATES", "FIRST_LIVE_DAY", "LIVE_SOURCE",
}

#: What the directive names: the cells, the intervals, the minimum-cell rule, the regime and
#: month-end splits and the gap scoring.
REQUIRED = {
    "scripts/live_score.py": {
        "score", "score_crps", "_group_cell", "_event_groups", "_paired_cell", "_paired", "_small_cell",
        "_regime", "MINIMUM_CELL_DAYS", "score_gap", "_as_gap_cell", "gap_target_days",
        "gap_decision_days", "first_live_targets", "validate_gap_record",
        "require_gap_boundaries_equal", "pinned_gap_days", "require_gap_scoring",
        "crps_from_record", "integral_crps_from_record", "headline_status", "assemble",
    },
    "src/repo_model/metrics.py": {"stationary_bootstrap_interval", "crps_from_quantiles",
                                  "crps_trapezoid_from_quantiles"},
    "src/repo_model/evaluation_splits.py": {"SplitDeclaration", "MONTH_END_RULE"},
    "src/repo_model/baseline.py": {"_seed_from"},
    "src/repo_model/onset.py": {"paired_difference", "day_groups", "leap_onset_group", "LeapTargets",
                                "GROUP_ONSET", "GROUP_LEAP_ONSET"},
    "scripts/live_record.py": {"next_decision_days", "previous_decision_day"},
}


def _pinned(field):
    text = DRAFT.read_text(encoding="utf-8")
    found = re.findall(rf"^- \*\*{re.escape(field)}:\*\* `([^`]+)`", text, flags=re.MULTILINE)
    if len(found) != 1:
        raise AssertionError(f"the draft pins {field!r} {len(found)} times, not once")
    return found[0]


def _top_level_names(path):
    names = set()
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            names.add(node.targets[0].id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


class PinnedTests(unittest.TestCase):
    def test_the_checksum_is_the_pinned_one(self):
        self.assertEqual(ls.live_declaration_checksum(), _pinned("Live scorer checksum"))

    def test_the_commit_it_was_taken_at_is_recorded(self):
        self.assertRegex(_pinned("Live scorer checksum taken at"), r"^[0-9a-f]{40}$")

    def test_the_declaration_lists_every_covered_file_and_name(self):
        source = ls.live_declaration()["source_sha256"]
        for path, names in REQUIRED.items():
            with self.subTest(path=path):
                self.assertLessEqual(names, set(source[path]))

    def test_the_final_test_checksums_are_untouched(self):
        fp = ls.final_test
        text = (ROOT / "docs" / "decisions" / "final-test-preregistration.md").read_text(encoding="utf-8")
        self.assertIn(fp.declaration_checksum(), text)
        self.assertIn(fp.crps_declaration_checksum(), text)


class CoverageTests(unittest.TestCase):
    def test_every_definition_of_the_scorer_is_covered_or_scores_nothing(self):
        covered = set(ls.live_declaration()["source_sha256"]["scripts/live_score.py"])
        uncovered = _top_level_names(SCRIPT) - covered - NOT_SCORING
        # Constants and helpers only a non-scoring function reads are not scoring; a function is.
        functions = {node.name for node in ast.parse(SCRIPT.read_text(encoding="utf-8")).body
                     if isinstance(node, ast.FunctionDef)}
        self.assertEqual(sorted(uncovered & functions), [])

    def test_the_not_scoring_list_names_only_definitions_that_exist(self):
        self.assertLessEqual(NOT_SCORING - {"LIVE_SOURCE"}, _top_level_names(SCRIPT))


class EditTests(unittest.TestCase):
    def _copy(self, root):
        paths = {path for path, _ in ls.LIVE_SOURCE}
        for each in paths:
            target = root / each
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / each).read_text(encoding="utf-8"), encoding="utf-8")

    def test_an_edit_to_each_covered_function_moves_the_checksum(self):
        pinned = _pinned("Live scorer checksum")
        for path, names in ls.LIVE_SOURCE:
            text = (ROOT / path).read_text(encoding="utf-8")
            definitions = {node.name: node for node in ast.parse(text).body
                           if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
            for name in names:
                if name not in definitions:
                    continue
                with self.subTest(path=path, name=name), tempfile.TemporaryDirectory() as scratch:
                    root = Path(scratch)
                    self._copy(root)
                    with mock.patch.object(ls.final_test, "REPO", root):
                        self.assertEqual(ls.live_declaration_checksum(), pinned)
                        lines = (root / path).read_text(encoding="utf-8").split("\n")
                        node = definitions[name]
                        last = node.body[-1].end_lineno - 1
                        indent = " " * node.body[-1].col_offset
                        lines[last] = lines[last] + f"\n{indent}_edited = 1"
                        (root / path).write_text("\n".join(lines), encoding="utf-8")
                        self.assertNotEqual(ls.live_declaration_checksum(), pinned)

    def test_an_edit_to_the_calendar_helpers_or_group_labels_moves_the_checksum(self):
        """The decision-day calendar and the group labels are frozen too (#370).

        Recorded mutation, confirmed applied: in `scripts/live_record.py`, `previous_decision_day`'s
        `current = day - timedelta(days=1)` changed to `days=2` -> the checksum moves to `875a2a5a\u2026`
        and `test_the_checksum_is_the_pinned_one` fails with `AssertionError`. Before the names were
        added to `LIVE_SOURCE`, the same edit left the checksum alone (the red run: `KeyError` on
        `scripts/live_record.py` and an `AssertionError` on the onset names).
        """

        pinned = _pinned("Live scorer checksum")
        edits = (
            ("scripts/live_record.py", "next_decision_days", "while len(out) < count:\n        current += timedelta(days=1)\n",
             "while len(out) < count:\n        current += timedelta(days=2)\n"),
            ("scripts/live_record.py", "previous_decision_day", "current = day - timedelta(days=1)",
             "current = day - timedelta(days=2)"),
            ("src/repo_model/onset.py", "GROUP_ONSET", 'GROUP_ONSET = "onset_days"\n',
             'GROUP_ONSET = "onset_days_x"\n'),
            ("src/repo_model/onset.py", "GROUP_LEAP_ONSET", 'GROUP_LEAP_ONSET = "leap_onset_days"',
             'GROUP_LEAP_ONSET = "leap_onset_days_x"'),
        )
        for path, name, old, replacement in edits:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as scratch:
                root = Path(scratch)
                self._copy(root)
                with mock.patch.object(ls.final_test, "REPO", root):
                    self.assertEqual(ls.live_declaration_checksum(), pinned)
                    text = (root / path).read_text(encoding="utf-8")
                    self.assertEqual(text.count(old), 1, old)
                    (root / path).write_text(text.replace(old, replacement), encoding="utf-8")
                    self.assertNotEqual(ls.live_declaration_checksum(), pinned)

    def test_an_edit_outside_the_covered_definitions_leaves_the_checksum(self):
        pinned = _pinned("Live scorer checksum")
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            self._copy(root)
            with mock.patch.object(ls.final_test, "REPO", root):
                text = (root / "scripts" / "live_score.py").read_text(encoding="utf-8")
                self.assertIn("def _sha256_bytes(", text)
                (root / "scripts" / "live_score.py").write_text(
                    text.replace("def _sha256_bytes(", "def _sha256_bytes_edited(", 1), encoding="utf-8")
                self.assertEqual(ls.live_declaration_checksum(), pinned)

    def test_a_changed_constant_moves_the_checksum(self):
        before = ls.live_declaration_checksum()
        self.assertEqual(before, _pinned("Live scorer checksum"))
        for module, name, value in (
            (ls.onset, "MINIMUM_EVENTS", ls.onset.MINIMUM_EVENTS + 1),
            (ls.onset, "REPLICATIONS", ls.onset.REPLICATIONS + 1),
            (ls.onset, "LEVEL", 0.95),
            (ls, "HORIZONS", (1, 2, 3, 4)),
            (ls, "MINIMUM_CELL_DAYS", ls.MINIMUM_CELL_DAYS + 1),
        ):
            with self.subTest(name=name):
                # The hash is of source text, so a patched value alone does not move it: the
                # declaration also records the values it reads.
                with mock.patch.object(module, name, value):
                    self.assertNotEqual(ls.live_declaration_checksum(), before)


if __name__ == "__main__":
    unittest.main()
