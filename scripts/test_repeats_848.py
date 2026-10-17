"""List the builds, walks and bootstraps that more than one test module repeats (#848).

Evaluation only: nothing is scored and no development or lockbox day is read. It wraps every
public `repo_model` function whose name says build, walk, bootstrap, fit, load or parse,
runs the suite the way CI does, and records each outermost call with a digest of its
arguments and the seconds it took. A repeat is the same function with the same argument
digest called in more than one test module.

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B scripts/test_repeats_848.py OUT.json

`--table OUT.json` prints the repeats that cost the most, as Markdown.
"""

import functools
import hashlib
import importlib
import json
import pkgutil
import re
import sys
import time
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"(build|walk|bootstrap|fit|load|parse)", re.I)
CALLS = []
STATE = {"test": None, "depth": 0}


def _digest(args, kwargs):
    return hashlib.sha256(repr((args, sorted(kwargs.items()))).encode("utf-8", "replace")).hexdigest()[:12]


def _wrap(module, name, fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if STATE["depth"]:
            return fn(*args, **kwargs)
        STATE["depth"] += 1
        started = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            STATE["depth"] -= 1
            test = STATE["test"] or "<fixture>"
            CALLS.append((f"{module}.{name}", _digest(args, kwargs), test, time.perf_counter() - started))

    setattr(sys.modules[module], name, wrapper)


def install():
    import repo_model

    for info in pkgutil.iter_modules(repo_model.__path__):
        if info.name.startswith("_"):  # __main__ runs the CLI on import
            continue
        mod = importlib.import_module(f"repo_model.{info.name}")
        for name, fn in list(vars(mod).items()):
            if (
                not name.startswith("_")
                and callable(fn)
                and getattr(fn, "__module__", None) == mod.__name__
                and not isinstance(fn, type)
                and NAME.search(name)
            ):
                _wrap(mod.__name__, name, fn)


class Result(unittest.TextTestResult):
    def startTest(self, test):
        STATE["test"] = test.id()
        super().startTest(test)

    def stopTest(self, test):
        super().stopTest(test)
        STATE["test"] = None


def run(out):
    sys.path.insert(0, str(ROOT / "tests"))
    install()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT / "tests"))
    result = unittest.TextTestRunner(resultclass=Result, verbosity=0).run(suite)
    groups = defaultdict(list)
    for func, digest, test, secs in CALLS:
        groups[(func, digest)].append((test, secs))
    repeats = []
    for (func, digest), calls in groups.items():
        modules = {t.split(".")[0] for t, _ in calls}
        if len(modules) > 1:
            total = sum(s for _, s in calls)
            first = calls[0][1]
            repeats.append(
                {
                    "function": func,
                    "args_digest": digest,
                    "calls": len(calls),
                    "modules": sorted(modules),
                    "total_seconds": round(total, 2),
                    "avoidable_seconds": round(total - first, 2),
                }
            )
    repeats.sort(key=lambda r: -r["avoidable_seconds"])
    Path(out).write_text(json.dumps({"ok": result.wasSuccessful(), "repeats": repeats}, indent=1) + "\n")
    return 0 if result.wasSuccessful() else 1


def table(path, top=25):
    data = json.loads(Path(path).read_text())
    lines = ["| function | calls | modules | total s | repeat s |", "|---|---:|---|---:|---:|"]
    for r in data["repeats"][:top]:
        lines.append(
            f"| {r['function']} ({r['args_digest']}) | {r['calls']} | {', '.join(r['modules'])} "
            f"| {r['total_seconds']:.1f} | {r['avoidable_seconds']:.1f} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.argv[1] == "--table":
        print(table(sys.argv[2]))
    else:
        sys.exit(run(sys.argv[1]))
