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
        self.assertEqual(len(found), 2, "suite and offline each list their shards")
        for entry in found:
            self.assertEqual([int(n) for n in entry.split(",")], expected)
        self.assertIn("'[1]' || '[" + ", ".join(map(str, expected)) + "]'", text, "the ml matrix lists the shards on a push")

    def test_every_shard_job_gets_its_modules_from_the_script(self):
        text = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"scripts/ci_shards\.py modules --shard \$\{\{ matrix\.shard \}\}", text)), 3)


if __name__ == "__main__":
    unittest.main()
