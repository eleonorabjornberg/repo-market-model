"""Time one full one-process run of the unit suite, per module and per class (#848).

Evaluation only: nothing is scored and no development or lockbox day is read. It runs
`unittest discover -s tests` the way CI does and attributes wall time to the class of the
test that follows it, so a class's `setUpClass` is counted with that class.

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B scripts/test_timing_848.py OUT.json

OUT.json holds the per-module, per-class and per-test seconds. `--table OUT.json` prints the
Markdown table that docs/pivot/ci-duration-848.md quotes.
"""

import json
import sys
import time
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TimingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mark = time.perf_counter()
        self.per_test = {}
        self.per_class = defaultdict(float)
        self._start = None

    def startTest(self, test):
        now = time.perf_counter()
        # The gap since the last test ended is fixture time for this test's class.
        cls = f"{type(test).__module__}.{type(test).__name__}"
        self.per_class[cls] += now - self.mark
        self._start = now
        super().startTest(test)

    def stopTest(self, test):
        super().stopTest(test)
        now = time.perf_counter()
        cls = f"{type(test).__module__}.{type(test).__name__}"
        self.per_class[cls] += now - self._start
        self.per_test[test.id()] = now - self._start
        self.mark = now


def run(out):
    sys.path.insert(0, str(ROOT / "tests"))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT / "tests"))
    runner = unittest.TextTestRunner(resultclass=TimingResult, verbosity=0)
    t0 = time.perf_counter()
    result = runner.run(suite)
    wall = time.perf_counter() - t0
    per_module = defaultdict(float)
    for cls, secs in result.per_class.items():
        per_module[cls.rsplit(".", 1)[0]] += secs
    Path(out).write_text(
        json.dumps(
            {
                "wall_seconds": round(wall, 1),
                "ok": result.wasSuccessful(),
                "per_module": {k: round(v, 2) for k, v in sorted(per_module.items(), key=lambda kv: -kv[1])},
                "per_class": {k: round(v, 2) for k, v in sorted(result.per_class.items(), key=lambda kv: -kv[1])},
                "per_test": {k: round(v, 2) for k, v in sorted(result.per_test.items(), key=lambda kv: -kv[1])[:60]},
            },
            indent=1,
        )
        + "\n"
    )
    return 0 if result.wasSuccessful() else 1


def table(path, top=25):
    data = json.loads(Path(path).read_text())
    total = data["wall_seconds"]
    lines = [f"Wall time {total:.0f} s, ok={data['ok']}.", "", "| module | seconds | share |", "|---|---:|---:|"]
    for mod, secs in list(data["per_module"].items())[:top]:
        lines.append(f"| {mod} | {secs:.1f} | {100 * secs / total:.1f}% |")
    lines += ["", "| class | seconds | share |", "|---|---:|---:|"]
    for cls, secs in list(data["per_class"].items())[:top]:
        lines.append(f"| {cls} | {secs:.1f} | {100 * secs / total:.1f}% |")
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.argv[1] == "--table":
        print(table(sys.argv[2]))
    else:
        sys.exit(run(sys.argv[1]))
