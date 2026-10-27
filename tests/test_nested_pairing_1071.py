"""A nested input test runs both arms on one pairing (#1071, finding #1067; calendar first, H3 and H5).

A test of "the published features plus X against the published features" differs in X only if the two arms are
trained alike. With the control on one-step pairs (the frozen fit) and the candidate on direct pairs, the paired
difference also carries the change of pairing, so it measures neither. `cli compare` therefore refuses a nested
comparison whose arms name different training pairs, and `scripts/dvp_segment_inputs.py crps` takes one
`--training-pairs` that applies to both arms.

Mutation record
---------------

Run on this branch's tree, `PYTHONPATH=src:tests`, unmutated control green before and after.

  * **The refusal removed** -- the `_refuse_mixed_nested_pairing(args)` call in `_compare_nested_checked` replaced by `pass`. Kills
    `test_mixed_pairing_in_a_nested_comparison_is_refused`, both subtests, `AssertionError: 0 != 2` (the mixed comparison
    ran and exited 0).
  * **The nesting test dropped** -- `if not columns_a < columns_b:` replaced by `if False:`. Kills
    `test_a_comparison_that_is_not_nested_is_not_refused`, `AssertionError: ReachedPanel not raised` (the refusal
    fired on a comparison that is no input test).
  * **The flag applied to the candidate only** -- `crps_argv` adding `--training-pairs-` for side b only. Kills
    `test_the_crps_command_gives_both_arms_the_one_pairing`, `ValueError: '--training-pairs-a' is not in list`.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

from repo_model import cli, cli_eval
from repo_model.splits import SplitError  # noqa: F401  (the refusal's type, named in the docstring above)

from test_cli_eval import ContinuousModelHarness, DECISION_TIME
from test_ml import require_extra

REPO = Path(__file__).resolve().parents[1]


def _load_script(name):
    sys.path.insert(0, str(REPO / "src"))
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReachedPanel(Exception):
    pass


class NestedPairingTests(ContinuousModelHarness):
    """`compare` on a nested pair of gbm declarations, by training pairs."""

    MINIMUM_HISTORY = "84"  # for cost alone, as the provenance test of test_ml does
    CONTROL = ContinuousModelHarness.FEATURES
    CANDIDATE = ContinuousModelHarness.REGIME_FEATURES  # the control's columns plus tgcr

    def compare(self, pairs_a=None, pairs_b=None, features_a=None, features_b=None):
        self.last_report = self.tmp / "nested.json"
        if self.last_report.exists():
            self.last_report.unlink()
        argv = [
            "compare", str(self.PANEL),
            "--minimum-history", self.MINIMUM_HISTORY,
            "--registry", str(self.registry),
            "--decision-time", DECISION_TIME,
            "--model-a", "gbm", "--model-b", "gbm",
            "--loss", "crps",
            "--report", str(self.last_report),
        ]
        for feature in (self.CONTROL if features_a is None else features_a):
            argv += ["--feature-a", feature]
        for feature in (self.CANDIDATE if features_b is None else features_b):
            argv += ["--feature-b", feature]
        if pairs_a is not None:
            argv += ["--training-pairs-a", pairs_a]
        if pairs_b is not None:
            argv += ["--training-pairs-b", pairs_b]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, err.getvalue()

    def test_mixed_pairing_in_a_nested_comparison_is_refused(self):
        """A one-step control against a direct candidate that adds a column is refused, naming both pairings.

        Recorded mutation: see the module docstring (`AssertionError: 0 != 2`).
        """

        for pairs_a, pairs_b in ((None, "direct"), ("direct", None)):
            with self.subTest(a=pairs_a, b=pairs_b):
                code, err = self.compare(pairs_a, pairs_b)
                self.assertEqual(code, 2, msg=err)
                self.assertIn("one-step", err)
                self.assertIn("direct", err)
                self.assertIn("--training-pairs-a", err)
                self.assertIn("--training-pairs-b", err)
                self.assertFalse(self.last_report.exists(), "a refused comparison leaves no report")

    def assert_reaches_the_panel(self, *args, **kwargs):
        """The refusal did not fire: the command went on to read the panel (which this stops, for speed)."""

        with mock.patch.object(cli_eval, "load_daily_panel", side_effect=ReachedPanel):
            with self.assertRaises(ReachedPanel):
                self.compare(*args, **kwargs)

    def test_a_comparison_that_is_not_nested_is_not_refused(self):
        """Two arms with different pairing and unrelated columns are no nested test; the refusal is not wider than that.

        The pairing itself may be the thing compared (#931's aligned-pairs study), and a candidate that drops a
        column is not "published features plus X". Recorded mutation: the nesting test `columns_a < columns_b`
        replaced by `False`-branch; this test then fails with `AssertionError: ReachedPanel not raised`.
        """

        self.assert_reaches_the_panel(None, "direct", features_a=self.CANDIDATE, features_b=self.CONTROL)
        self.assert_reaches_the_panel(None, "direct", features_a=self.CONTROL, features_b=self.CONTROL)

    def test_both_arms_one_step_is_not_refused_as_mixed(self):
        """Equal pairing is not mixed, whichever pairing it is; the one-step guard is a separate rule."""

        self.assert_reaches_the_panel(None, None)
        self.assert_reaches_the_panel("direct", "direct")

    def test_both_arms_direct_runs(self):
        """The same nested comparison with both arms direct runs and says so in the record."""

        require_extra(self)
        code, err = self.compare("direct", "direct")
        self.assertEqual(code, 0, msg=err)
        record = json.loads(self.last_report.read_text(encoding="utf-8"))
        self.assertEqual(record["declaration"]["model_a"]["training_pairs"], "direct")
        self.assertEqual(record["declaration"]["model_b"]["training_pairs"], "direct")


class CrpsCommandPairingTests(unittest.TestCase):
    """`dvp_segment_inputs.py crps --training-pairs`: one flag, both arms."""

    @classmethod
    def setUpClass(cls):
        cls.script = _load_script("dvp_segment_inputs")

    def argv(self, pairs):
        return self.script.crps_argv(
            Path("panel.csv"), Path("sources.json"), Path("out.json"),
            self.script.v1.GBM_FEATURES, ("extra_column",), pairs,
        )

    def test_the_crps_command_gives_both_arms_the_one_pairing(self):
        """`--training-pairs direct` becomes `--training-pairs-a direct` and `--training-pairs-b direct`.

        Recorded mutation: see the module docstring (`ValueError`).
        """

        argv = self.argv("direct")
        for side in ("a", "b"):
            index = argv.index(f"--training-pairs-{side}")
            self.assertEqual(argv[index + 1], "direct")

    def test_the_default_leaves_both_arms_as_they_were(self):
        """Unset, neither flag is passed: every published invocation means what it meant."""

        argv = self.argv(None)
        self.assertNotIn("--training-pairs-a", argv)
        self.assertNotIn("--training-pairs-b", argv)

    def test_the_command_line_takes_one_flag(self):
        argv = ["crps", "--panel", "p.csv", "--run", "ofr_dvp_minus_bgcr_bp", "--output", "o.json", "--training-pairs", "direct"]
        with mock.patch.object(self.script, "crps_command", side_effect=lambda a: seen.append(a.training_pairs) or 0):
            seen = []
            self.script.main(argv)
        self.assertEqual(seen, ["direct"])


if __name__ == "__main__":
    unittest.main()
