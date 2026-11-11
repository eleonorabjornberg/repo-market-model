#!/usr/bin/env python3
"""Prove that a prose rewrite of a Markdown page left every number byte-identical (#1574).

The rule: every number on every page stays byte-identical, and a test proves it by comparing the sets of numeric
tokens before and after. `snapshot` stores the distinct tokens of a page at a git ref under
`tests/fixtures/numeric_tokens_1574/`; `check` compares the working-tree page with that file (it needs no git, so CI
can run it); `diff` compares the working-tree page straight against a git ref.

    python3 scripts/check_numeric_tokens.py snapshot --ref origin/main PAGE [PAGE ...]
    python3 scripts/check_numeric_tokens.py check [PAGE ...]
    python3 scripts/check_numeric_tokens.py diff --ref origin/main PAGE [PAGE ...]

A token is a number as it is written: an ISO date, a 40-64 character lowercase hex digest, or digits with optional
thousands commas, decimal part, exponent and trailing `%`, and a leading sign only when it is attached to the digits and
does not follow a digit, letter or closing bracket (so `1-5` is `1` and `5`). Exit status is 1 when a token was removed
or added.

Standard library only.
"""
import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Where the stored baselines live, relative to the repository root.
BASELINES = "tests/fixtures/numeric_tokens_1574"

#: Each character belongs to at most one token; the alternatives are tried in this order at every position.
_TOKEN = re.compile(
    r"(?P<hex>(?<![0-9A-Za-z])[0-9a-f]{40,64}(?![0-9A-Za-z]))"
    r"|(?P<date>(?<!\d)\d{4}-\d{2}-\d{2}(?!\d))"
    r"|(?P<num>(?:(?<![0-9A-Za-z)\]}])[+-])?"
    r"\d+(?:,\d{3}(?!\d))*(?:\.\d+)?(?:[eE][+-]?\d+)?%?)"
)


def tokens(text):
    """`collections.Counter` of the numeric tokens of `text`."""
    return collections.Counter(m.group(0) for m in _TOKEN.finditer(text))


def compare(before_text, after_text):
    """The difference between the numeric tokens of two texts, as a dict."""
    before, after = tokens(before_text), tokens(after_text)
    return {
        "removed": sorted(set(before) - set(after)),
        "added": sorted(set(after) - set(before)),
        "before_distinct": len(before),
        "after_distinct": len(after),
        "before_total": sum(before.values()),
        "after_total": sum(after.values()),
    }


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def _baseline_file(path):
    return ROOT / BASELINES / (path.replace("/", "__") + ".json")


def _line(path, result, tail=""):
    ok = not result["removed"] and not result["added"]
    return "%s: before %d distinct, after %d distinct, removed %s, added %s%s  %s" % (
        path, result["before_distinct"], result["after_distinct"], result["removed"], result["added"], tail,
        "OK" if ok else "FAIL")


def _compare_sets(before, after_text):
    after = set(tokens(after_text))
    return {"removed": sorted(before - after), "added": sorted(after - before),
            "before_distinct": len(before), "after_distinct": len(after)}


def snapshot(ref, paths):
    sha = _git("rev-parse", ref).strip()
    out = ROOT / BASELINES
    out.mkdir(parents=True, exist_ok=True)
    for path in paths:
        found = sorted(tokens(_git("show", "%s:%s" % (ref, path))))
        record = {"path": path, "ref": sha, "tokens": found}
        _baseline_file(path).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("%s: %d distinct tokens at %s" % (path, len(found), sha[:12]))
    return 0


def check(paths):
    directory = ROOT / BASELINES
    if paths:
        files = [_baseline_file(p) for p in paths]
    else:
        files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    failed = False
    for file in files:
        record = json.loads(file.read_text(encoding="utf-8"))
        page = ROOT / record["path"]
        result = _compare_sets(set(record["tokens"]), page.read_text(encoding="utf-8"))
        print(_line(record["path"], result))
        failed |= bool(result["removed"] or result["added"])
    return 1 if failed else 0


def diff(ref, paths):
    failed = False
    for path in paths:
        result = compare(_git("show", "%s:%s" % (ref, path)), (ROOT / path).read_text(encoding="utf-8"))
        print(_line(path, result, ", total %d -> %d" % (result["before_total"], result["after_total"])))
        failed |= bool(result["removed"] or result["added"])
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    snap = sub.add_parser("snapshot", help="store the distinct tokens of pages as they are at a git ref")
    snap.add_argument("--ref", required=True)
    snap.add_argument("paths", nargs="+", metavar="path")
    chk = sub.add_parser("check", help="compare working-tree pages with their stored baselines")
    chk.add_argument("paths", nargs="*", metavar="path")
    dif = sub.add_parser("diff", help="compare working-tree pages with a git ref, with no stored baseline")
    dif.add_argument("--ref", required=True)
    dif.add_argument("paths", nargs="+", metavar="path")
    args = parser.parse_args(argv)
    if args.command == "snapshot":
        return snapshot(args.ref, args.paths)
    if args.command == "check":
        return check(args.paths)
    return diff(args.ref, args.paths)


if __name__ == "__main__":
    sys.exit(main())
