"""The third-party boundary: `src/repo_model/ml.py` and nothing else.

Human-owned. Decided 10 September 2026: phase 2's candidate models
(gradient-boosted conditional quantiles) need numpy and scikit-learn, declared
as the optional `ml` extra in `pyproject.toml`. Everything else stays
standard-library only, because every record under `docs/runs/` must reproduce
with no install. Before this file, "stdlib only" was a sentence in three
documents and a checkbox in the pull-request template, and nothing in the suite
could see an import.

Two halves, and they fail in different ways:

* **No third-party import outside the boundary.** Every module-level or
  function-level import in `src/repo_model/*.py`, `tests/*.py` and
  `scripts/*.py` resolves to the standard library, to this package, or to a
  sibling test module -- except in `src/repo_model/ml.py` and
  `tests/test_ml.py`.
* **The core does not import the boundary at import time.** A core module may
  reach `repo_model.ml` only from inside a function, so `import repo_model.cli`
  works on an interpreter without the extra. A module-level import would make
  the whole package need numpy while the first half stayed green.

Standard library is decided by where an import *resolves*, not by a list typed
here: built-in and frozen modules, and anything under this interpreter's
`stdlib` path that is not under a `site-packages` directory. A name that does
not resolve at all is not standard library either -- which is how `numpy` fails
on an interpreter that lacks it, and `sklearn` fails on one that has it.
Python 3.9 has no `sys.stdlib_module_names`, so this is also the only answer
that works on both interpreters the declaration admits.

Mutation record
---------------
Red first: on the tree this file landed on there was no live breach to run it
against, so each half was run red against a planted one, in a disposable copy
under `$HOME` with `data/`, `.github/`, `.claude/`, `metadata/`, `.gitignore`,
the root Markdown and `docs/PROJECT_STATUS.md`, `PYTHONDONTWRITEBYTECODE=1`,
`python3 -B`, CPython 3.10.12 -- an interpreter that happens to have numpy
2.2.6 in `dist-packages` and no scikit-learn. Unmutated control green before
and after; each mutation confirmed applied by grep, and restored before the
next.

1. `import numpy` at the top of `src/repo_model/baseline.py`. Kills
   `test_no_third_party_import_outside_the_boundary` alone, `AssertionError`.
   **Nothing else in the suite noticed**, because numpy imported: on a machine
   that has it, a core dependency on numpy is invisible to every other test,
   and it is exactly the machine a developer has. That is the case this guard
   is for.
2. `from . import ml` at module level in `src/repo_model/cli_eval.py`, with an
   empty `src/repo_model/ml.py` beside it. Kills
   `test_the_core_reaches_the_boundary_only_from_inside_a_function` alone,
   `AssertionError`. The first half stays green -- `ml` is this package's own
   name -- which is why the second half exists.
3. Control, expected to survive: the same import moved inside the first
   function body in `cli_eval.py`. Both tests green.

H5 (the boundary's own imports), same disposable-copy protocol, red first
against a planted `src/repo_model/ml.py`; on the real tree the file does not
exist yet and both new tests skip:

4. Planted `ml.py` whose first line after the docstring is `import sklearn`.
   Kills `test_ml_imports_its_third_party_packages_only_inside_functions`,
   `AssertionError` naming `ml.py` and `'sklearn'` -- and the forecast
   conformance walk errors with `ModuleNotFoundError` beside it, which is the
   collateral this guard exists to name before it happens.
5. Planted `ml.py` with module-level `import numpy`. Kills the same test
   alone, `AssertionError`. **Nothing else noticed**: numpy imports on this
   interpreter, so the walk stays green. That is the case the guard is for.
6. Controls, expected to survive: the import inside a function; under
   `if TYPE_CHECKING:`. Green.
7. Planted `tests/test_ml.py` with a bare module-level `import sklearn`.
   Kills `test_the_ml_test_module_imports_without_the_extra`, `AssertionError`
   (discovery also errors). Wrapped in `try: ... except ImportError:` it is
   green, which is the pattern `REPO_MODEL_REQUIRE_ML` needs to skip rather
   than fail.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import sysconfig
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
PACKAGE = "repo_model"
BOUNDARY = frozenset({"src/repo_model/ml.py", "tests/test_ml.py"})
SCANNED = ("src/repo_model/*.py", "tests/*.py", "scripts/*.py")

_STDLIB = Path(sysconfig.get_paths()["stdlib"]).resolve()


def _is_stdlib(name: str) -> bool:
    if name == "__future__" or name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return False
    if spec is None:
        return False
    if spec.origin in ("built-in", "frozen"):
        return True
    locations = [spec.origin] if spec.origin else []
    locations += list(spec.submodule_search_locations or [])
    for location in locations:
        path = Path(location).resolve()
        if "site-packages" in path.parts or "dist-packages" in path.parts:
            return False
        if _STDLIB in path.parents:
            return True
    return False


def _scanned_files():
    for pattern in SCANNED:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if "__pycache__" not in path.parts:
                yield path, path.relative_to(REPO_ROOT).as_posix()


def _imports(tree):
    """Yield (top-level name, is_relative, node, inside_function) per import."""

    def walk(node, in_function):
        for child in ast.iter_child_nodes(node):
            inside = in_function or isinstance(
                child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
            )
            if isinstance(child, ast.Import):
                for alias in child.names:
                    yield alias.name, False, child, in_function
            elif isinstance(child, ast.ImportFrom):
                if child.level:
                    names = (
                        [child.module] if child.module
                        else [alias.name for alias in child.names]
                    )
                    for name in names:
                        yield name, True, child, in_function
                else:
                    yield child.module or "", False, child, in_function
            yield from walk(child, inside)

    yield from walk(tree, False)


class DependencyBoundaryTests(unittest.TestCase):
    def _test_modules(self):
        return {path.stem for path in (REPO_ROOT / "tests").glob("*.py")}

    def test_no_third_party_import_outside_the_boundary(self):
        """Outside ml.py and its test, every import is stdlib or this repo's own."""

        local = self._test_modules() | {PACKAGE}
        breaches = []
        for path, relative in _scanned_files():
            if relative in BOUNDARY:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
            for name, relative_import, node, _ in _imports(tree):
                if relative_import:
                    continue
                top = name.split(".")[0]
                if top in local or _is_stdlib(top):
                    continue
                breaches.append(f"{relative}:{node.lineno} imports {top!r}")
        self.assertEqual(
            breaches,
            [],
            "a third-party import outside src/repo_model/ml.py: the core must "
            "reproduce every published record with no install (AGENT_CONTRACT.md, "
            "working rules) -- " + "; ".join(breaches),
        )

    def test_the_core_reaches_the_boundary_only_from_inside_a_function(self):
        """`import repo_model.<anything>` must not need the ml extra."""

        breaches = []
        for path, relative in _scanned_files():
            if relative in BOUNDARY or not relative.startswith("src/"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
            for name, relative_import, node, in_function in _imports(tree):
                if in_function:
                    continue
                reaches_ml = (
                    (relative_import and name.split(".")[0] == "ml")
                    or name in (f"{PACKAGE}.ml",)
                    or name.startswith(f"{PACKAGE}.ml.")
                    or (
                        isinstance(node, ast.ImportFrom)
                        and (node.module in (PACKAGE, None) or node.level)
                        and any(alias.name == "ml" for alias in node.names)
                    )
                )
                if reaches_ml:
                    breaches.append(f"{relative}:{node.lineno}")
        self.assertEqual(
            breaches,
            [],
            "a core module imports repo_model.ml at import time, so the package "
            "no longer imports without the ml extra; move it inside the function "
            "that needs it -- " + "; ".join(breaches),
        )

    # -- H5: inside the boundary, the extra is reached only when it is used --

    def _module_level_third_party(self, relative):
        """Third-party imports that run when `relative` is imported, with lines.

        An import inside a function runs when the function does. One under
        `if TYPE_CHECKING:` never runs. One inside a `try` whose handlers catch
        `ImportError` runs but cannot fail the import. Everything else at
        module level runs at import and fails it on an interpreter without the
        extra -- and `repo_model`'s conformance walk (B9) and `unittest
        discover` both import every module they find.
        """

        path = REPO_ROOT / relative
        if not path.exists():
            self.skipTest(f"no {relative} yet; the guard waits for the file")
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        local = self._test_modules() | {PACKAGE}
        found = []

        def guarded_try(node):
            for handler in node.handlers:
                names = []
                if handler.type is None:
                    return True
                kinds = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
                for kind in kinds:
                    names.append(getattr(kind, "id", getattr(kind, "attr", "")))
                if {"ImportError", "ModuleNotFoundError", "Exception"} & set(names):
                    return True
            return False

        def type_checking(node):
            test = node.test
            return getattr(test, "id", getattr(test, "attr", None)) == "TYPE_CHECKING"

        def walk(node):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    continue
                if isinstance(child, ast.If) and type_checking(child):
                    walk_body(child.orelse)
                    continue
                if isinstance(child, ast.Try) and guarded_try(child):
                    for part in (child.handlers, child.orelse, child.finalbody):
                        walk_body(part)
                    continue
                if isinstance(child, ast.Import):
                    names = [alias.name for alias in child.names]
                elif isinstance(child, ast.ImportFrom) and not child.level:
                    names = [child.module or ""]
                else:
                    names = []
                for name in names:
                    top = name.split(".")[0]
                    if top not in local and not _is_stdlib(top):
                        found.append(f"{relative}:{child.lineno} imports {top!r}")
                walk(child)

        def walk_body(statements):
            holder = ast.Module(body=list(statements), type_ignores=[])
            walk(holder)

        walk(tree)
        return found

    def test_ml_imports_its_third_party_packages_only_inside_functions(self):
        """`import repo_model.ml` must succeed on an interpreter without the extra.

        AGENT_CONTRACT.md, working rules: `ml.py` imports numpy and
        scikit-learn inside the functions that use them. B9 made forecast
        conformance discovery walk every module of the package, so a
        module-level `import sklearn` there fails the core suite -- not
        `tests/test_ml.py` -- on every interpreter without the extra.
        """
        breaches = self._module_level_third_party("src/repo_model/ml.py")
        self.assertEqual(
            breaches,
            [],
            "src/repo_model/ml.py imports a third-party package at import time; "
            "move it inside the function that uses it -- " + "; ".join(breaches),
        )

    def test_the_ml_test_module_imports_without_the_extra(self):
        """`unittest discover` imports `tests/test_ml.py` whether or not it runs it."""
        breaches = self._module_level_third_party("tests/test_ml.py")
        self.assertEqual(
            breaches,
            [],
            "tests/test_ml.py imports a third-party package at module level with "
            "nothing catching ImportError, so discovery fails without the extra "
            "-- " + "; ".join(breaches),
        )


if __name__ == "__main__":
    unittest.main()
