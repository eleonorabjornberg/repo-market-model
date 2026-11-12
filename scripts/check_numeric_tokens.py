#!/usr/bin/env python3
"""Prove that a prose rewrite of a Markdown page left every number byte-identical (#1574).

The rule: every number on every page stays byte-identical, and a test proves it by comparing the sets of numeric
tokens before and after. `snapshot` stores the distinct tokens of a page at a git ref under
`tests/fixtures/numeric_tokens_1574/`; `check` compares the working-tree page with that file (it needs no git, so CI
can run it); `diff` compares the working-tree page straight against a git ref.

    python3 scripts/check_numeric_tokens.py snapshot --ref origin/main PAGE [PAGE ...]
    python3 scripts/check_numeric_tokens.py check [PAGE ...]
    python3 scripts/check_numeric_tokens.py diff --ref origin/main [--source FILE ...] [--cite N ...] PAGE [PAGE ...]
    python3 scripts/check_numeric_tokens.py allow PAGE TOKEN --source FILE --why TEXT

A token is a number as it is written: an ISO date, a 40-64 character lowercase hex digest, or digits with optional
thousands commas, decimal part, exponent and trailing `%`, and a leading sign only when it is attached to the digits and
does not follow a digit, letter or closing bracket (so `1-5` is `1` and `5`). Exit status is 1 when a token was removed
or added.

A new number is accepted only when it is traced to a record (Eleonora's ruling of 11 November 2026 on #1575, which let
that pull request add figures of merged records). `allow` stores the token in the page's baseline with the file it was
copied from, and `check` accepts it only while that file still carries the same token. `diff --source FILE` accepts an
added token that one of the named files carries; `diff --cite N` accepts the number of an issue that has no page yet,
and only where the page writes it as `#N`. Nothing is accepted because it is listed alone, and a removed token always
fails.

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


def unsourced(added, source_texts):
    """The tokens of `added` that none of the source texts carries, sorted."""
    carried = set()
    for text in source_texts:
        carried |= set(tokens(text))
    return sorted(set(added) - carried)


def uncited(added, page_text, cites):
    """The tokens of `added` that are not an issue number of `cites` written as `#N` at every place the page has them."""
    counts = tokens(page_text)
    out = []
    for token in sorted(added):
        as_issue = len(re.findall(r"#%s(?!\d)" % re.escape(token), page_text))
        if token not in cites or as_issue != counts[token]:
            out.append(token)
    return out


def _read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def check_record(record, page_text, read=_read):
    """A stored baseline against the page: an added token passes only when the baseline lists it under `added` with a
    `source` file that carries the same token."""
    result = _compare_sets(set(record["tokens"]), page_text)
    listed = record.get("added", {})
    still = []
    for token in result["added"]:
        entry = listed.get(token)
        try:
            traced = bool(entry) and not unsourced({token}, [read(entry["source"])])
        except OSError:
            traced = False
        if not traced:
            still.append(token)
    result["sourced"] = sorted(set(result["added"]) - set(still))
    result["added"] = still
    return result


def allow(path, token, source, why):
    file = _baseline_file(path)
    record = json.loads(file.read_text(encoding="utf-8"))
    if unsourced({token}, [_read(source)]):
        print("%s does not carry the token %s" % (source, token))
        return 1
    record.setdefault("added", {})[token] = {"source": source, "why": why}
    file.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("%s: %s allowed, traced to %s" % (path, token, source))
    return 0


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
        result = check_record(record, page.read_text(encoding="utf-8"))
        print(_line(record["path"], result, ", traced to a source %s" % result["sourced"] if result["sourced"] else ""))
        failed |= bool(result["removed"] or result["added"])
    return 1 if failed else 0


def diff(ref, paths, sources=(), cites=()):
    failed = False
    source_texts = [_read(rel) for rel in sources]
    for path in paths:
        page_text = _read(path)
        result = compare(_git("show", "%s:%s" % (ref, path)), page_text)
        still = unsourced(result["added"], source_texts)
        still = uncited(still, page_text, set(cites))
        traced = sorted(set(result["added"]) - set(still))
        result["added"] = still
        tail = ", total %d -> %d" % (result["before_total"], result["after_total"])
        print(_line(path, result, tail + (", traced to a source or cited as an issue %s" % traced if traced else "")))
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
    dif.add_argument("--source", action="append", default=[], help="a file an added token may be traced to")
    dif.add_argument("--cite", action="append", default=[], help="an issue number accepted where the page writes it as #N")
    dif.add_argument("paths", nargs="+", metavar="path")
    alw = sub.add_parser("allow", help="store one added token in a page's baseline, traced to the file that carries it")
    alw.add_argument("path")
    alw.add_argument("token")
    alw.add_argument("--source", required=True)
    alw.add_argument("--why", required=True)
    args = parser.parse_args(argv)
    if args.command == "snapshot":
        return snapshot(args.ref, args.paths)
    if args.command == "check":
        return check(args.paths)
    if args.command == "allow":
        return allow(args.path, args.token, args.source, args.why)
    return diff(args.ref, args.paths, args.source, args.cite)


if __name__ == "__main__":
    sys.exit(main())
