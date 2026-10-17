#!/usr/bin/env python3
"""Check the research log (#638): `docs/research/log.md` against `docs/research/plan.md`.

Two documents keep the research honest. The plan names the hypotheses H1 to H10; the log has one dated entry per
scored experiment. This check fails when

1. a log entry breaks the format (`ENTRY_FORMAT`);
2. a log entry names a hypothesis the plan does not have;
3. a change adds or changes a result page (`docs/pivot/*-result.md`) or a declaration or candidate under
   `metadata/` and adds no new log entry whose Directive line names the pull request's directive.

The format is one constant so that a change to it is one edit. It is shared with the liquidity repository
(`eleonorabjornberg/repo-market-liquidity`), whose results arrive as a fenced `research-log` block copied
verbatim from its pull request body: `check-block` validates such a block the same way.

    python3 scripts/check_research_log.py check
    python3 scripts/check_research_log.py check --base REF [--head REF] [--body-env PR_BODY]
    python3 scripts/check_research_log.py check-block FILE

`check --base` compares the log at REF with the log in the working tree and looks at the paths changed since the
merge base; the directive comes from the `Closes #N` lines of the pull request body in the environment variable
named by `--body-env`. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "research" / "plan.md"
LOG = ROOT / "docs" / "research" / "log.md"

# The log format, in one place. A heading `### YYYY-MM-DD [H#] step N · owner/repo#PR`, or for groundwork (G1 to G5
# in a hypothesis manual, kept apart from the six steps) `### YYYY-MM-DD [H#] groundwork G<n> · owner/repo#PR`, then
# one `- Name: value` line for each of REQUIRED_LINES.
ENTRY_FORMAT = "### YYYY-MM-DD [H#] step N · owner/repo#PR"
GROUNDWORK_FORMAT = "### YYYY-MM-DD [H#] groundwork G<n> · owner/repo#PR"
HEADING = re.compile(r"^### (?P<date>\d{4}-\d{2}-\d{2}) \[(?P<hyp>H\d+)\] "
                     r"(?:step (?P<step>\d+)|groundwork (?P<groundwork>G[1-9]\d*)) · "
                     r"(?P<ref>[\w.-]+/[\w.-]+#\d+)\s*$")
REQUIRED_LINES = ("Directive", "Step", "Tier", "Pins", "Tried", "Result", "Against kill", "Next")
TIERS = ("development", "confirmation")
STEPS = range(1, 7)

# Paths whose change needs an entry. Result pages sit directly under docs/pivot; declarations and judge
# candidates under metadata/. The metadata files that are not experiment declarations are exempt.
RESULT_PAGE = "docs/pivot/*-result.md"
DECLARATIONS = ("metadata/*.json", "metadata/pressure_judge/*.json", "metadata/pressure_judge/candidates/*.json")
NOT_DECLARATIONS = frozenset(
    "metadata/" + name for name in (
        "events.json", "lockbox.json", "owner_attestations.json", "live_pin.json", "market_holidays.json",
        "policy_events.json", "sources.json", "sources_measurement.json", "funding_panel_manifest.json",
        "evaluation_splits.json"))


def plan_hypotheses(text):
    """The hypotheses the plan names: its `## H<n>` headings."""
    return set(re.findall(r"(?m)^## (H\d+)\b", text))


def parse_log(text):
    """Entries as (line number, heading match or None, heading text, {line name: value})."""
    entries = []
    current = None
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("### "):
            current = [number, HEADING.match(line), line, {}]
            entries.append(current)
        elif current is not None and line.startswith("## "):
            current = None
        elif current is not None:
            match = re.match(r"^- ([A-Za-z ]+): (.*)$", line)
            if match:
                current[3].setdefault(match.group(1), match.group(2))
    return entries


def conflict_markers(text, name):
    """Lines of `text` that are git conflict markers (#795): `<<<<<<< `, `>>>>>>> ` or a bare `=======`."""
    return ["%s line %d: unresolved merge conflict marker %r" % (name, number, line)
            for number, line in enumerate(text.splitlines(), 1)
            if line.startswith(("<<<<<<< ", ">>>>>>> ")) or line == "======="]


def validate_log(text, hypotheses):
    """Every way the log's entries break the format or the plan. Empty when it is sound."""
    errors = conflict_markers(text, "log.md")
    for number, heading, raw, fields in parse_log(text):
        where = "log.md line %d" % number
        if heading is None:
            errors.append("%s: heading is not `%s` or `%s`: %r" % (where, ENTRY_FORMAT, GROUNDWORK_FORMAT, raw))
            continue
        date, hypothesis, step = heading.group("date", "hyp", "step")
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            errors.append("%s: %s is not a date" % (where, date))
        if hypothesis not in hypotheses:
            errors.append("%s: hypothesis %s is not in the plan (docs/research/plan.md)" % (where, hypothesis))
        if step is not None and int(step) not in STEPS:
            errors.append("%s: step %s is not 1 to 6" % (where, step))
        for name in REQUIRED_LINES:
            if not fields.get(name, "").strip():
                errors.append("%s: missing the line `- %s:`" % (where, name))
        if fields.get("Directive") and not re.search(r"#\d+", fields["Directive"]):
            errors.append("%s: the Directive line names no issue (#N)" % where)
        if fields.get("Tier") and fields["Tier"].strip() not in TIERS:
            errors.append("%s: Tier is %r, not one of %s" % (where, fields["Tier"], "/".join(TIERS)))
    return errors


def extract_blocks(body):
    """The fenced `research-log` blocks of a pull request body."""
    return re.findall(r"(?ms)^```research-log\s*\n(.*?)^```", body or "")


def paths_needing_entry(paths):
    needed = []
    for path in paths:
        if fnmatch.fnmatchcase(path, RESULT_PAGE) and path.count("/") == 2:
            needed.append(path)
        elif path not in NOT_DECLARATIONS and any(fnmatch.fnmatchcase(path, p) for p in DECLARATIONS):
            needed.append(path)
    return needed


def _key(entry):
    return (entry[2], tuple(sorted(entry[3].items())))


def new_entries(base_text, head_text):
    seen = {_key(e) for e in parse_log(base_text)}
    return [e for e in parse_log(head_text) if _key(e) not in seen]


def closed_issues(body):
    """The issues a pull request body closes, in order, as `#N`."""
    return ["#" + n for n in re.findall(r"(?i)\bcloses\s+#(\d+)", body or "")]


def check_change(changed, base_text, head_text, directives):
    needed = paths_needing_entry(changed)
    if not needed:
        return []
    shown = ", ".join(needed[:3]) + (" ..." if len(needed) > 3 else "")
    if not directives:
        return ["%s change%s a result page or a declaration, and the pull request body has no `Closes #N` to "
                "name the directive" % (shown, "" if len(needed) > 1 else "s")]
    for entry in new_entries(base_text, head_text):
        named = set(re.findall(r"#\d+", entry[3].get("Directive", "")))
        if named & set(directives):
            return []
    return ["%s changed, but docs/research/log.md adds no new entry whose Directive line names %s"
            % (shown, " or ".join(directives))]


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--base")
    check.add_argument("--head", default="HEAD")
    check.add_argument("--body-env", default="PR_BODY")
    block = sub.add_parser("check-block")
    block.add_argument("file")
    args = parser.parse_args(argv)

    hypotheses = plan_hypotheses(PLAN.read_text())
    if args.command == "check-block":
        errors = validate_log(Path(args.file).read_text(), hypotheses)
    else:
        errors = validate_log(LOG.read_text(), hypotheses)
        for name in _git("ls-files", "*.md").split("\n"):
            if name and name != "docs/research/log.md":
                errors += conflict_markers((ROOT / name).read_text(), name)
        if args.base:
            merge_base = _git("merge-base", args.base, args.head).strip()
            changed = _git("diff", "--name-only", "--diff-filter=AMR", merge_base, args.head).split()
            try:
                base_text = _git("show", "%s:docs/research/log.md" % merge_base)
            except subprocess.CalledProcessError:
                base_text = ""
            head_text = _git("show", "%s:docs/research/log.md" % args.head)
            errors += check_change(changed, base_text, head_text,
                                   closed_issues(os.environ.get(args.body_env, "")))
    for error in errors:
        print(error)
    if not errors:
        print("research log: ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
