#!/usr/bin/env python3
"""Run, in one command, the checks CI runs on generated files and the research log, before a pull request asks for review.

Most review round trips were for a failure one of these checks would have caught locally: a stale progress page, a
research-log entry the check refused, a built file committed by mistake. Each check is the command CI runs
(`.github/workflows/tests.yml`); this script only runs them in turn and reports every failure, rather than stopping at
the first. It does not run the test suite: run that in one process as `CLAUDE.md` says.

    python3 scripts/pre_review.py [--base REF]

With `--base` (normally `origin/main`) it also runs the two checks CI runs against the pull request's base:
`check_research_log.py check --base` and `check_built_outputs.py --base`. Exit status 1 when any check fails.

Standard library only.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The checks, as CI runs them, without the base.
CHECKS = (
    ("scripts/emit_visual.py", "--check"),
    ("scripts/emit_progress.py", "--check"),
    ("scripts/emit_status.py", "--check"),
    ("scripts/ci_shards.py", "check"),
    ("scripts/check_research_log.py", "assemble", "--check"),
    ("scripts/check_research_log.py", "check"),
    ("scripts/check_built_outputs.py",),
)


def commands(base=None):
    """The command lines to run, each as a list; the base-relative checks are added when `base` is given."""
    runs = [[sys.executable, "-B", *check] for check in CHECKS]
    if base:
        runs.append([sys.executable, "-B", "scripts/check_research_log.py", "check", "--base", base])
        runs.append([sys.executable, "-B", "scripts/check_built_outputs.py", "--base", base])
    return runs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", help="the pull request's base, normally origin/main")
    args = parser.parse_args(argv)
    failed = []
    for command in commands(args.base):
        shown = " ".join(command[2:])
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if result.returncode == 0:
            print("ok    %s" % shown)
        else:
            failed.append(shown)
            print("FAIL  %s" % shown)
            print((result.stdout + result.stderr).rstrip())
    if failed:
        print("%d check(s) failed: %s" % (len(failed), "; ".join(failed)))
        return 1
    print("all checks ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
