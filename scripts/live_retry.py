#!/usr/bin/env python3
"""Run the live record's `run` command again when its fetch step failed (#1148).

The 21 October record was lost to two failures at `record (fetch)`, 85 minutes apart, FRED's
graph endpoint answering with something that was not its CSV bundle. The record's fetch is
all-or-nothing and writes nothing to the log until the whole build has passed, so a failed fetch
leaves nothing behind but the work directory: it can be tried again, inside the day's window,
without touching the pinned code, the pin or any record.

    python3 scripts/live_retry.py --status status.json --work-dir work --attempts 4 --wait 120 -- CMD ...

Only a failure whose status file still reads `fetch` is retried. A failure at any later step (the
build, the audit, the forecast) is a result about the code or the data and fails at once, as
before. The work directory is emptied between attempts, so a retry never reads half of a
previous fetch. The retry stops, and the last exit code stands, at `--stop-after` Eastern time
(the record's cut-off is 23:59 ET, `prospective_log.DECISION_DAY_CUTOFF`).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time as clock
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/New_York")
RETRY_STEP = "fetch"


def failed_step(status: Path):
    try:
        return json.loads(status.read_text(encoding="utf-8")).get("step")
    except (OSError, ValueError, AttributeError):
        return None


def run_with_retry(
    command,
    status: Path,
    work_dir: Path,
    attempts: int = 4,
    wait: float = 120.0,
    stop_after: time = time(23, 30),
    now=lambda: datetime.now(EASTERN),
    sleep=clock.sleep,
) -> int:
    """The command's exit code after at most `attempts` tries; waits `wait`, `2*wait`, ... between them."""

    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    code = 0
    for attempt in range(1, attempts + 1):
        code = subprocess.call(list(command))
        if code == 0:
            return 0
        step = failed_step(status)
        if step != RETRY_STEP:
            return code
        if attempt == attempts:
            break
        pause = wait * 2 ** (attempt - 1)
        if now().timetz().replace(tzinfo=None) >= stop_after:
            print(f"live_retry: past {stop_after} ET; not trying again", file=sys.stderr)
            break
        print(
            f"live_retry: attempt {attempt} failed at {step}; trying again in {pause:.0f} s",
            file=sys.stderr,
        )
        sleep(pause)
        shutil.rmtree(work_dir, ignore_errors=True)
        status.unlink(missing_ok=True)
    return code


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--status", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--attempts", type=int, default=4)
    parser.add_argument("--wait", type=float, default=120.0)
    parser.add_argument("--stop-after", default="23:30", help="Eastern HH:MM")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    return run_with_retry(
        command,
        Path(args.status),
        Path(args.work_dir),
        attempts=args.attempts,
        wait=args.wait,
        stop_after=time.fromisoformat(args.stop_after),
    )


if __name__ == "__main__":
    sys.exit(main())
