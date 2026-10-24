#!/usr/bin/env python3
"""#1169 guard: the re-score may add `studentized` entries to #1023's result.json and nothing else.

Compares every existing value (point values, percentile interval bounds, everything) of the committed result with the new
one, exactly. Exits 1 and prints each difference if any value moved, was removed, or any key other than `studentized` was
added.
"""
from __future__ import annotations

import argparse
import json
import sys

ALLOWED_NEW_KEY = "studentized"


def differences(old, new, path: str = "") -> list:
    """Return a list of 'path: what' strings; empty when `new` is `old` plus `studentized` entries."""
    out: list = []
    if isinstance(old, dict) and isinstance(new, dict):
        for key in old:
            if key not in new:
                out.append(f"{path}/{key}: removed")
            else:
                out += differences(old[key], new[key], f"{path}/{key}")
        for key in new:
            if key not in old and key != ALLOWED_NEW_KEY:
                out.append(f"{path}/{key}: added")
    elif isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            out.append(f"{path}: length {len(old)} -> {len(new)}")
        else:
            for i, (a, b) in enumerate(zip(old, new)):
                out += differences(a, b, f"{path}[{i}]")
    elif type(old) is not type(new) or old != new:
        out.append(f"{path}: {old!r} -> {new!r}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    args = parser.parse_args()
    with open(args.old) as f:
        old = json.load(f)
    with open(args.new) as f:
        new = json.load(f)
    found = differences(old, new)
    if found:
        print(f"{len(found)} existing value(s) differ from the committed result; nothing will be committed:", file=sys.stderr)
        for line in found[:50]:
            print("  " + line, file=sys.stderr)
        return 1
    print("only studentized entries were added; existing values are unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
