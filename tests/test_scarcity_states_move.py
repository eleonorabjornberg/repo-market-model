"""Stage 1 of #1055: the scarcity-state read moved from `scripts/pressure_judge.py` to `scripts/scarcity_states.py`.

The H5, H3 and H9 scripts that need the state load the new script, not the +5 bp judge. The judge keeps a forwarding
`_scarcity_states` until stage 2 archives its other callers.
"""

import ast
import importlib.util
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_CALLERS = ("h5_step3_707", "h3_nested_708", "spread_mr_variants_761", "ranking_765")


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_move_test", ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScarcityStatesMoveTests(unittest.TestCase):
    def test_the_current_scripts_do_not_load_the_judge(self):
        for name in CURRENT_CALLERS:
            with self.subTest(script=name):
                source = (ROOT / "scripts" / f"{name}.py").read_text(encoding="utf-8")
                self.assertNotIn('_load("pressure_judge")', source)
                self.assertNotIn("._scarcity_states(", source.replace("def _scarcity_states", ""))
                self.assertIn("scarcity_states", source)

    def test_the_judge_holds_no_copy_of_the_read(self):
        tree = ast.parse((ROOT / "scripts" / "pressure_judge.py").read_text(encoding="utf-8"))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_scarcity_states")
        names = {n.id for n in ast.walk(function) if isinstance(n, ast.Name)} | {
            n.attr for n in ast.walk(function) if isinstance(n, ast.Attribute)
        }
        self.assertNotIn("own_leg_states", names)
        self.assertNotIn("build_measurement_panel", names)

    def test_the_forwarder_and_the_new_read_agree(self):
        judge = _load("pressure_judge")
        moved = _load("scarcity_states")
        last = date(2024, 12, 31)
        self.assertEqual(judge._scarcity_states(1, last), moved.scarcity_states(1, last))


if __name__ == "__main__":
    unittest.main()
