"""The parallel test shards run every test module exactly once (#927).

`tests.yml` runs the suite as parallel jobs, each one running the modules `scripts/ci_shards.py`
assigns it. A module that fell into no shard would silently stop running in CI, so these tests fail on
that, on a module in two shards, on a shard count that differs from the workflow's matrix, and on a
workflow job that runs a shard without the module list.

**Recorded mutation**, 19 October 2026: in `scripts/ci_shards.py`, `assign` made to `continue` past the
module `test_workflows` (a module dropped from every shard): `test_every_module_is_in_exactly_one_shard`
fails with `ValueError: modules in no shard: ['test_workflows']`. The same function with
`out[n].append(module)` run twice for `test_alarm_cooldown`: the same test fails with
`ValueError: test_alarm_cooldown is in shards 6 and 6`.

**The ml pull-request job runs every module that skips without the extra** (#1018, from finding #1007). `ci_shards.py
ml-modules` finds them by reading the test sources, and the workflow's pull-request branch runs that list. Before it, the
branch named three modules, and `test_pressure_hazard.PairTests` (whose `setUp` calls `_require_extra`) skipped on every
pull-request job that had no extra, with its `LookAheadError` guard test among the skipped.

**Recorded mutations**, 20 October 2026 (the killing test run alone, each mutation confirmed applied by `grep`):
`ml_extra_modules` made to `return set()` fails `test_the_scan_finds_the_modules_that_skip_without_the_extra` with
`AssertionError: 'test_ml' not found in set()`; the pull-request command of `tests.yml` put back to
`python3 -B -m unittest test_ml test_tail_diagnostics test_cli_eval -v` fails
`test_the_pull_request_ml_job_runs_the_modules_that_skip_without_the_extra` with `AssertionError: 'unittest test_ml
test_tail_diagnostics test_cli_eval' unexpectedly found in ...`. The guard test moved to `test_pressure_hazard.LabelGuardTests`
is killed, without the extra, by `last_label >= rows` changed to `last_label > rows` in `require_labels_inside`
(`AssertionError: LookAheadError not raised`).
"""

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ci_shards", ROOT / "scripts" / "ci_shards.py")
ci_shards = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ci_shards)


class ShardTests(unittest.TestCase):
    def setUp(self):
        self.modules = ci_shards.all_modules()
        self.weights = ci_shards.load_weights()

    def test_every_module_is_in_exactly_one_shard(self):
        split = ci_shards.assign(self.modules, self.weights)
        ci_shards.check(self.modules, split)
        self.assertEqual(sorted(m for mods in split.values() for m in mods), self.modules)

    def test_a_module_in_no_shard_or_two_is_refused(self):
        split = ci_shards.assign(self.modules, self.weights)
        dropped = {n: [m for m in mods if m != self.modules[0]] for n, mods in split.items()}
        with self.assertRaises(ValueError):
            ci_shards.check(self.modules, dropped)
        doubled = {n: list(mods) for n, mods in split.items()}
        doubled[1].append(self.modules[0])
        doubled[2].append(self.modules[0])
        with self.assertRaises(ValueError):
            ci_shards.check(self.modules, doubled)

    def test_a_new_module_without_a_weight_still_lands_in_a_shard(self):
        modules = self.modules + ["test_a_module_added_later"]
        split = ci_shards.assign(modules, self.weights)
        ci_shards.check(modules, split)

    def test_the_split_is_deterministic(self):
        self.assertEqual(ci_shards.assign(self.modules, self.weights), ci_shards.assign(list(reversed(self.modules)), self.weights))

    def test_the_weights_name_only_existing_modules(self):
        self.assertEqual(sorted(set(self.weights) - set(self.modules)), [])

    def test_the_workflow_matrices_list_exactly_the_shards(self):
        text = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        expected = list(range(1, ci_shards.SHARDS + 1))
        found = re.findall(r"^\s+shard:\s*\[([\d, ]+)\]\s*$", text, flags=re.M)
        self.assertEqual(len(found), 1, "the suite lists its shards; the networking-off check waits on the same shards")
        for entry in found:
            self.assertEqual([int(n) for n in entry.split(",")], expected)
        pull_request = "[" + ", ".join(map(str, range(1, ci_shards.ML_SHARDS + 1))) + "]"
        self.assertIn(f"'{pull_request}' || '[" + ", ".join(map(str, expected)) + "]'", text, "the ml matrix lists its shards on a pull request and the suite's on a push")

    def test_every_shard_job_gets_its_modules_from_the_script(self):
        text = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"scripts/ci_shards\.py modules --shard \$\{\{ matrix\.shard \}\}", text)), 2)


class MlModuleTests(unittest.TestCase):
    """The pull-request ml job runs every module that skips without the extra (#1018)."""

    def test_the_scan_finds_the_modules_that_skip_without_the_extra(self):
        found = ci_shards.ml_extra_modules()
        # one of each way a module skips: its own `_require_extra`, `test_ml.require_extra`, a `skipUnless(find_spec(...))`
        # decorator, an inline `find_spec` call, and a helper imported from another test module
        for module in (
            "test_ml",
            "test_pressure_hazard",
            "test_satiation",
            "test_tail_diagnostics",
            "test_spread_distribution_632",
            "test_off_risk_day_624",
            "test_spread_distribution_634_script",
            "test_live_v2",
            "test_identified_level_689",
        ):
            self.assertIn(module, found)
        self.assertNotIn("test_ci_shards", found)

    def test_a_module_that_only_names_the_libraries_is_not_one(self):
        # `test_dependency_boundary` lists "numpy" and "sklearn" to forbid importing them; it never skips for want of them
        self.assertNotIn("test_dependency_boundary", ci_shards.ml_extra_modules())

    def test_the_scan_reads_code_not_prose(self):
        import ast

        prose = ast.parse('"""find_spec("numpy") and require_extra(self) in a docstring"""\nx = 1\n')
        self.assertFalse(ci_shards.skips_without_the_extra(prose))
        code = ast.parse('import importlib.util\nok = importlib.util.find_spec("numpy") is not None\n')
        self.assertTrue(ci_shards.skips_without_the_extra(code))

    def test_the_pull_request_ml_job_runs_the_modules_that_skip_without_the_extra(self):
        text = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/ci_shards.py ml-modules", text)
        self.assertNotIn("unittest test_ml test_tail_diagnostics test_cli_eval", text)
        self.assertNotIn("Every other module runs identically with or without it", text)

    def test_each_ml_module_runs_in_exactly_one_ml_shard(self):
        """The pull-request ml job is sharded (#1096): the scan's modules are split with the suite's weights."""
        modules = sorted(ci_shards.ml_extra_modules())
        split = ci_shards.assign(modules, ci_shards.load_weights(), ci_shards.ML_SHARDS)
        self.assertEqual(len(split), ci_shards.ML_SHARDS)
        ci_shards.check(modules, split)
        self.assertEqual(sorted(m for mods in split.values() for m in mods), modules)

    def test_the_ml_shard_command_prints_one_shard_and_the_shards_together_print_the_scan(self):
        import contextlib
        import io

        def run(*argv):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(ci_shards.main(list(argv)), 0)
            return out.getvalue().split()

        together = []
        for n in range(1, ci_shards.ML_SHARDS + 1):
            together += run("ml-modules", "--shard", str(n))
        self.assertEqual(sorted(together), sorted(ci_shards.ml_extra_modules()))
        self.assertEqual(len(together), len(set(together)))
        with self.assertRaises(ValueError):
            ci_shards.main(["ml-modules", "--shard", str(ci_shards.ML_SHARDS + 1)])

    def test_the_pull_request_ml_job_runs_its_shard_and_keeps_the_slow_skip(self):
        text = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/ci_shards.py ml-modules --shard ${{ matrix.shard }}", text)
        self.assertEqual(len(re.findall(r"REPO_MODEL_SKIP_SLOW=1 python3", text)), 1, "the slow skip is on the pull-request command only")
        self.assertIn("REPO_MODEL_SKIP_SLOW=1 python3 -B -m unittest $(python3 scripts/ci_shards.py ml-modules --shard", text)

    def test_the_command_prints_the_scan(self):
        import contextlib
        import io

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(ci_shards.main(["ml-modules"]), 0)
        self.assertEqual(out.getvalue().split(), sorted(ci_shards.ml_extra_modules()))


if __name__ == "__main__":
    unittest.main()
