#!/usr/bin/env python3
"""Split the test modules into the parallel shards `tests.yml` runs (#927).

Every `tests/test_*.py` module belongs to exactly one shard, so the shards together run the same
suite that `python3 -B -m unittest discover -s tests` runs in one process. Nothing is skipped here;
the split only decides which job runs which module.

The split is deterministic: modules are sorted by their weight in `tests/ci_shard_weights.json`
(seconds measured once, a module missing from the file gets `DEFAULT_WEIGHT`), heaviest first, and each
goes to the lightest shard so far, ties broken by shard number. A new module therefore falls into a
shard without anyone editing a list; `tests/test_ci_shards.py` fails if any module is in no shard or in
two, or if the shard count here differs from the one in the workflow.

    python3 scripts/ci_shards.py modules --shard 2        # module names for shard 2 of SHARDS
    python3 scripts/ci_shards.py check                    # every module in exactly one shard
    python3 scripts/ci_shards.py ml-modules               # the modules that skip without the ml extra (#1018)
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
WEIGHTS = TESTS / "ci_shard_weights.json"

#: The number of shards. `tests.yml` lists the same shard numbers in its matrices.
SHARDS = 6
#: Seconds assumed for a module that has no recorded weight.
DEFAULT_WEIGHT = 5.0


def all_modules(tests_dir=TESTS):
    """The test module names that `unittest discover -s tests` would load."""
    return sorted(path.stem for path in Path(tests_dir).glob("test*.py"))


#: The libraries the optional `ml` extra installs.
EXTRA_LIBRARIES = ("numpy", "sklearn")
#: A call to one of these is a skip (or a failure under `REPO_MODEL_REQUIRE_ML`) for want of the extra.
REQUIRE_CALLS = ("require_extra", "_require_extra")
#: A helper imported from another test module under one of these names carries that module's skip with it.
HELPER_NAME = re.compile(r"require_extra|have_ml", re.IGNORECASE)


def _called(node):
    func = node.func
    return func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None


def skips_without_the_extra(tree):
    """True if the parsed module skips its tests for want of the ml extra: it calls `require_extra`, or probes
    `find_spec` with the extra's libraries named in code, or imports such a helper from another test module. Docstrings and
    comments are not code, so a module that only names the libraries (`test_dependency_boundary`) is not one."""
    nodes = list(ast.walk(tree))
    calls = {_called(n) for n in nodes if isinstance(n, ast.Call)}
    if calls & set(REQUIRE_CALLS):
        return True
    named = any(isinstance(n, ast.Constant) and n.value in EXTRA_LIBRARIES for n in nodes)
    if "find_spec" in calls and named:
        return True
    return any(
        isinstance(n, ast.ImportFrom) and (n.module or "").startswith("test_") and any(HELPER_NAME.search(a.name) for a in n.names)
        for n in nodes
    )


def ml_extra_modules(tests_dir=TESTS):
    """The test modules that skip without the ml extra, read from their sources. The pull-request ml job runs these."""
    found = set()
    for module in all_modules(tests_dir):
        tree = ast.parse((Path(tests_dir) / f"{module}.py").read_text(encoding="utf-8"), filename=module)
        if skips_without_the_extra(tree):
            found.add(module)
    return found


def load_weights(path=WEIGHTS):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def assign(modules, weights, shards=SHARDS):
    """`{shard number from 1: [module, ...]}`: greedy, heaviest module first onto the lightest shard."""
    if shards < 1:
        raise ValueError("shards must be at least 1")
    load = {n: 0.0 for n in range(1, shards + 1)}
    out = {n: [] for n in load}
    for module in sorted(modules, key=lambda m: (-weights.get(m, DEFAULT_WEIGHT), m)):
        n = min(load, key=lambda k: (load[k], k))
        out[n].append(module)
        load[n] += weights.get(module, DEFAULT_WEIGHT)
    return {n: sorted(mods) for n, mods in out.items()}


def check(modules, split):
    """Raise `ValueError` unless every module is in exactly one shard and no shard is empty."""
    seen = {}
    for n, mods in split.items():
        if not mods:
            raise ValueError(f"shard {n} has no module")
        for module in mods:
            if module in seen:
                raise ValueError(f"{module} is in shards {seen[module]} and {n}")
            seen[module] = n
    missing = sorted(set(modules) - set(seen))
    extra = sorted(set(seen) - set(modules))
    if missing or extra:
        raise ValueError(f"modules in no shard: {missing}; shard entries without a module: {extra}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    mods = sub.add_parser("modules", help="print the module names of one shard, space separated")
    mods.add_argument("--shard", type=int, required=True, help="1 to SHARDS")
    sub.add_parser("check", help="fail unless every test module is in exactly one shard")
    sub.add_parser("ml-modules", help="print the module names that skip without the ml extra, space separated")
    args = parser.parse_args(argv)

    if args.command == "ml-modules":
        print(" ".join(sorted(ml_extra_modules())))
        return 0

    modules = all_modules()
    split = assign(modules, load_weights())
    check(modules, split)
    if args.command == "check":
        print(f"ci shards: ok ({len(modules)} modules in {len(split)} shards)")
        return 0
    if args.shard not in split:
        raise ValueError(f"--shard must be 1 to {SHARDS}")
    print(" ".join(split[args.shard]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
