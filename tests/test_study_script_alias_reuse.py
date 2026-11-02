"""Study scripts that load each other under fixed `sys.modules` aliases must share a process (#1294, finding #1292).

The loaders of #1241's, #1255's, #1265's and #1274's scripts (and the later ones that copy them) registered a fresh module
under the alias on every call, so a second loader replaced the first's `srf_cap_1241_in_1255`; the worker pool then pickled
`_dispatch` by that name and met a different object (`PicklingError`).

Recorded mutation (the guard is the reuse in `_load`): deleting the `if alias in sys.modules ...: return` lines of
`scripts/s3c_candidate_1255.py` made `test_second_load_reuses_the_alias` fail with `AssertionError` and the one-process run
below fail with `PicklingError` inside `test_s3c_candidate_1255_script`.
"""

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOADERS = [
    "s3c_candidate_1255", "s3c_carry_1275", "s3c_gse_1274", "s3c_gse_roll_1287",
    "s3c_net_settlement_1273", "s3c_turn_cap_1265", "srf_cap_2026_1252",
]


def _import(name):
    spec = importlib.util.spec_from_file_location(f"_alias_reuse_{name}", ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AliasReuse(unittest.TestCase):
    def test_second_load_reuses_the_alias(self):
        for name in LOADERS:
            with self.subTest(script=name):
                module = _import(name)
                try:
                    first = module._load("srf_cap_1241", "srf_cap_1241_alias_reuse_probe")
                    second = module._load("srf_cap_1241", "srf_cap_1241_alias_reuse_probe")
                    self.assertIs(first, second)
                    self.assertIs(sys.modules["srf_cap_1241_alias_reuse_probe"], first)
                finally:
                    sys.modules.pop("srf_cap_1241_alias_reuse_probe", None)
                    sys.modules.pop(module.__name__, None)

    def test_1255_and_1265_script_tests_share_one_process(self):
        env = dict(os.environ, PYTHONPATH=f"{ROOT / 'src'}{os.pathsep}{ROOT / 'tests'}", PYTHONDONTWRITEBYTECODE="1")
        done = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "test_s3c_candidate_1255_script", "test_s3c_turn_cap_1265_script"],
            cwd=ROOT, env=env, capture_output=True, text=True,
        )
        self.assertEqual(done.returncode, 0, done.stderr[-3000:])


if __name__ == "__main__":
    unittest.main()
