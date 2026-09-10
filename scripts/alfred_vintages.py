"""Compare ALFRED vintages of one series: was any observation ever restated?

    python3 scripts/alfred_vintages.py tests/fixtures/snapshots/alfred-ioer/*.csv

Each file is one vintage as ALFRED serves it
(`https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<SERIES>&vintage_date=<DATE>`):
a header naming the date column and `<SERIES>_<YYYYMMDD>`, then one row per
observation, `.` for a missing value. Prints each vintage's span and, for every
pair, how many reference dates both carry and how many of those agree exactly.
Exits 1 if any shared observation differs, so the never-revised claim in
`metadata/sources.json` is a command, not prose.

Standard library only. Values are compared as the strings ALFRED wrote, so a
restatement from 0.10 to 0.1 would count as a difference: that is deliberate,
and none has been seen.
"""

import argparse
import csv
import itertools
import re
import sys
from datetime import date
from pathlib import Path


def read_vintage(path):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if not rows or len(rows[0]) != 2:
        raise SystemExit(f"{path}: expected a two-column ALFRED CSV, got {rows[:1]}")
    match = re.fullmatch(r"(\w+?)_(\d{8})", rows[0][1].strip())
    if not match:
        raise SystemExit(f"{path}: value column {rows[0][1]!r} is not <SERIES>_<YYYYMMDD>")
    series, stamp = match.groups()
    vintage = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
    observations = {}
    for ref, value in rows[1:]:
        if value.strip() in ("", "."):
            continue
        observations[date.fromisoformat(ref.strip())] = value.strip()
    if not observations:
        raise SystemExit(f"{path}: no observations")
    return series, vintage, observations


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)
    if len(args.files) < 2:
        parser.error("give at least two vintages")

    vintages = sorted((read_vintage(path) for path in args.files), key=lambda item: item[1])
    if len({series for series, _v, _o in vintages}) != 1:
        raise SystemExit("the files are not vintages of one series")

    restated = False
    for series, vintage, obs in vintages:
        last = max(obs)
        print(
            f"{series} vintage {vintage}: {len(obs)} observations, "
            f"{min(obs)} to {last} (last observation {(last - vintage).days:+d} days "
            f"from the vintage date)"
        )
    for (_s, v1, o1), (_s2, v2, o2) in itertools.combinations(vintages, 2):
        shared = sorted(set(o1) & set(o2))
        differ = [ref for ref in shared if o1[ref] != o2[ref]]
        restated = restated or bool(differ)
        span = f", {shared[0]} to {shared[-1]}" if shared else ""
        print(f"{v1} vs {v2}: {len(shared)} shared{span}; {len(shared) - len(differ)} identical")
        for ref in differ[:10]:
            print(f"  restated {ref}: {o1[ref]} -> {o2[ref]}")
    return 1 if restated else 0


if __name__ == "__main__":
    sys.exit(main())
