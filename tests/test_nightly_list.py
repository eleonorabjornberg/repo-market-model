"""A test class is marked nightly only if `tests/nightly.py` declares it (#869).

CI skips the declared classes on a pull request and runs them on every push to `main` and on
the nightly schedule (`.github/workflows/tests.yml`). The list is one tuple in one file, so it
cannot grow quietly: a class decorated `@nightly` that is not on `nightly.DECLARED` fails here,
and so does a declared class that no longer exists or is no longer marked. The scan reads the
source with `ast`, so it needs no import of the marked modules (some need the `ml` extra).
Nothing is scored; no data is read.
"""

import ast
import unittest
from pathlib import Path

import nightly

TESTS = Path(__file__).resolve().parent


def marked_classes():
    """Every `(module, class)` under `tests/` whose class carries the `@nightly` decorator."""
    found = set()
    for path in sorted(TESTS.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for decorator in node.decorator_list:
                    name = decorator.attr if isinstance(decorator, ast.Attribute) else getattr(decorator, "id", None)
                    if name == "nightly":
                        found.add((path.stem, node.name))
    return found


class NightlyListTests(unittest.TestCase):
    def test_the_marked_classes_are_exactly_the_declared_ones(self):
        marked = marked_classes()
        declared = set(nightly.DECLARED)
        self.assertEqual(marked - declared, set(), "a class is marked nightly without being declared in tests/nightly.py")
        self.assertEqual(declared - marked, set(), "tests/nightly.py declares a class that is not marked @nightly")

    def test_the_declared_list_has_no_repeats(self):
        self.assertEqual(len(nightly.DECLARED), len(set(nightly.DECLARED)))

    def test_a_marked_class_is_skipped_with_its_reason_when_asked_and_runs_otherwise(self):
        import os
        from unittest import mock

        class Probe(unittest.TestCase):
            def test_it(self):
                pass

        with mock.patch.dict(os.environ, {nightly.SKIP_NIGHTLY: "1"}):
            skipped = nightly.nightly(type("Skipped", (Probe,), {}))
        self.assertTrue(skipped.__unittest_skip__)
        self.assertIn("nightly", skipped.__unittest_skip_why__)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(nightly.SKIP_NIGHTLY, None)
            kept = nightly.nightly(type("Kept", (Probe,), {}))
        self.assertFalse(getattr(kept, "__unittest_skip__", False))


if __name__ == "__main__":
    unittest.main()
