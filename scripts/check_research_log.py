#!/usr/bin/env python3
"""Check the research log (#638): `docs/research/log/` against `docs/research/plan.md`.

Two documents keep the research honest. The plan names the hypotheses H1 to H10; the log has one dated entry per
scored experiment. Since #866 each entry is its own file under `docs/research/log/`, so pull requests that add
entries never conflict, and `docs/research/log.md` is generated from the files by `assemble` (never hand-edited).
This check fails when

1. a log entry breaks the format (`ENTRY_FORMAT`);
2. a log entry names a hypothesis the plan does not have;
3. an entry file is badly named, holds more than one entry, or disagrees with its own heading;
4. `log.md` is not the assembly of the entry files, the header and the corrections;
   `docs/research/log/_corrections.md` (#867) corrects only the pull request number in an entry's heading, for an
   entry that exists, once; `assemble` applies it and the entry file stays frozen. A correction line that is
   malformed, names a missing entry, repeats the old reference wrongly or changes more than the number fails;
5. a change edits, renames or deletes an entry file already on the base (the log is append-only);
6. a change adds or changes a result page (`docs/pivot/*-result.md`) or a declaration or candidate under
   `metadata/` and adds no new log entry whose Directive line names the pull request's directive.

The format is one constant so that a change to it is one edit. It is shared with the liquidity repository
(`eleonorabjornberg/repo-market-liquidity`), whose results arrive as a fenced `research-log` block copied
verbatim from its pull request body: `check-block` validates such a block the same way.

    python3 scripts/check_research_log.py check
    python3 scripts/check_research_log.py check --base REF [--head REF] [--body-env PR_BODY]
    python3 scripts/check_research_log.py check-block FILE
    python3 scripts/check_research_log.py assemble [--check]

`check --base` compares the log at REF with the log in the working tree and looks at the paths changed since the
merge base; the directive comes from the `Closes #N` lines of the pull request body in the environment variable
named by `--body-env`. `assemble` writes `docs/research/log.md` from `docs/research/log/_header.md` and the entry
files, in file-name order; with `--check` it writes nothing and exits 1 when `log.md` is stale. Standard library only.
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
LOG_DIR = ROOT / "docs" / "research" / "log"
HEADER_NAME = "_header.md"
CORRECTIONS_NAME = "_corrections.md"

# The log format, in one place. A heading `### YYYY-MM-DD [H#] step N · owner/repo#PR`, or for groundwork (G1 to G5
# in a hypothesis manual, kept apart from the six steps) `### YYYY-MM-DD [H#] groundwork G<n> · owner/repo#PR`, then
# one `- Name: value` line for each of REQUIRED_LINES.
ENTRY_FORMAT = "### YYYY-MM-DD [H#] step N · owner/repo#PR"
GROUNDWORK_FORMAT = "### YYYY-MM-DD [H#] groundwork G<n> · owner/repo#PR"
HEADING = re.compile(r"^### (?P<date>\d{4}-\d{2}-\d{2}) \[(?P<hyp>H\d+)\] "
                     r"(?:step (?P<step>\d+)|groundwork (?P<groundwork>G[1-9]\d*)) · "
                     r"(?P<ref>[\w.-]+/[\w.-]+#\d+)\s*$")
# An entry file is `<date>-<model|liquidity>-<PR, five digits>-<H#>-<step N | G n>.md`, so that a plain sort of the
# names is date, then repository, then pull request number. The entries migrated from the single file (#866) keep
# their old order under a four-digit prefix, `0001-` to `0099-`, which sorts before every date. A second entry for
# the same heading takes `-2`, `-3`, ... before `.md`.
ENTRY_NAME = re.compile(r"^(?:\d{4}-(?=\d{4}-\d{2}-\d{2}-))?(?P<date>\d{4}-\d{2}-\d{2})-(?P<repo>model|liquidity)-"
                        r"(?P<pr>\d{5})-(?P<hyp>H\d+)-(?P<what>step[1-6]|G[1-9]\d*)(?:-[2-9])?\.md$")
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


def name_parts(heading):
    """The parts a valid entry file name must carry, from a heading match; None when the repository is not ours."""
    repo = heading.group("ref").split("#")[0].split("/")[1]
    if not repo.startswith("repo-market-") or repo[len("repo-market-"):] not in ("model", "liquidity"):
        return None
    what = "step%s" % heading.group("step") if heading.group("step") else heading.group("groundwork")
    return {"date": heading.group("date"), "repo": repo[len("repo-market-"):],
            "pr": "%05d" % int(heading.group("ref").split("#")[1]), "hyp": heading.group("hyp"), "what": what}


def heading_matches_name(name, heading):
    """True when the file name `name` says what the entry heading says (date, repository, PR, hypothesis, step)."""
    named = ENTRY_NAME.match(name)
    expected = name_parts(heading)
    if named is None or expected is None:
        return False
    mismatch = [key for key in expected if named.group(key) != expected[key]]
    return not mismatch


def entry_name(heading, sequence=None, taken=()):
    """The file name for an entry; `sequence` gives a migrated entry its order prefix."""
    parts = name_parts(heading)
    stem = "%s-%s-%s-%s-%s" % (parts["date"], parts["repo"], parts["pr"], parts["hyp"], parts["what"])
    if sequence is not None:
        return "%04d-%s.md" % (sequence, stem)
    name, repeat = stem + ".md", 1
    while name in taken:
        repeat += 1
        name = "%s-%d.md" % (stem, repeat)
    return name


CORRECTION = re.compile(r"^- (?P<file>\S+\.md): (?P<old>[\w.-]+/[\w.-]+#\d+) -> (?P<new>[\w.-]+/[\w.-]+#\d+)\s*$")


def parse_corrections(text):
    """The corrections in `_corrections.md` as (line number, file name or None, old ref, new ref, raw line).

    A correction line is `- <entry file name>: <owner/repo#PR> -> <owner/repo#PR>`; any other line starting with
    `- ` is returned with None so that `correction_errors` can refuse it. Headings and prose are ignored.
    """
    found = []
    for number, line in enumerate((text or "").splitlines(), 1):
        if not line.startswith("- "):
            continue
        match = CORRECTION.match(line)
        found.append((number, match.group("file") if match else None,
                      match.group("old") if match else None, match.group("new") if match else None, line))
    return found


def correction_errors(corrections, files):
    """Every way the corrections break the rule (#867): each names an existing entry file, states that entry's own
    heading reference as the old one, changes nothing but the pull request number, and appears once."""
    errors, seen = [], set()
    for number, target, old, new, raw in parse_corrections(corrections):
        where = "%s line %d" % (CORRECTIONS_NAME, number)
        if target is None:
            errors.append("%s: not `- <entry file>: <owner/repo#PR> -> <owner/repo#PR>`: %r" % (where, raw))
            continue
        if target not in files:
            errors.append("%s: %s is not an entry file" % (where, target))
            continue
        if target in seen:
            errors.append("%s: %s is corrected twice" % (where, target))
        seen.add(target)
        heading = HEADING.match(files[target].splitlines()[0]) if files[target].strip() else None
        if heading is None:
            errors.append("%s: the heading of %s is not a valid entry heading" % (where, target))
            continue
        if old != heading.group("ref"):
            errors.append("%s: the heading of %s names %s, not %s" % (where, target, heading.group("ref"), old))
        old_repo, new_repo = old.split("#")[0], new.split("#")[0]
        if old_repo != new_repo:
            errors.append("%s: a correction changes only the pull request number, not the repository (%s -> %s)"
                          % (where, old_repo, new_repo))
        if old == new:
            errors.append("%s: %s is not a correction (old and new are the same)" % (where, old))
    return errors


def apply_correction(text, old, new):
    """An entry with its heading's reference replaced, and a `- Correction:` line that keeps the original visible."""
    head, _, rest = text.partition("\n")
    note = ("- Correction: the heading named %s; corrected to %s (docs/research/log/%s).\n"
            % (old, new, CORRECTIONS_NAME))
    return head.replace("· " + old, "· " + new, 1) + "\n" + note + rest


def assemble(header, entries, corrections=None):
    """`log.md`: the header, then every entry in file-name order, each after one blank line.

    `corrections` is the text of `_corrections.md`: an entry named there is assembled with its heading corrected.
    The entry file itself is never edited."""
    fixes = {target: (old, new) for _, target, old, new, _ in parse_corrections(corrections) if target}
    return header + "".join(
        "\n" + (apply_correction(entries[name], *fixes[name]) if name in fixes else entries[name])
        for name in sorted(entries))


def split_log(text):
    """The one-off migration (#866): a single-file log as (header, [(file name, entry text)]) in its own order."""
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith("### ")]
    if not starts:
        return text, []
    header = "".join(lines[:starts[0]]).rstrip("\n") + "\n"
    files = []
    for number, start in enumerate(starts, 1):
        stop = starts[number] if number < len(starts) else len(lines)
        chunk = "".join(lines[start:stop]).rstrip("\n") + "\n"
        heading = HEADING.match(lines[start].rstrip("\n"))
        if heading is None:
            raise ValueError("log line %d: heading is not `%s`: %r" % (start + 1, ENTRY_FORMAT, lines[start]))
        files.append((entry_name(heading, number), chunk))
    return header, files


def read_entry_files(directory=None):
    """(header text, {file name: text}) of the entry directory."""
    directory = Path(directory) if directory else LOG_DIR
    header = (directory / HEADER_NAME).read_text(encoding="utf-8")
    files = {p.name: p.read_text(encoding="utf-8") for p in sorted(directory.glob("*.md"))
             if p.name not in (HEADER_NAME, CORRECTIONS_NAME)}
    return header, files


def read_corrections(directory=None):
    """The text of `_corrections.md`, or "" when there is none."""
    path = (Path(directory) if directory else LOG_DIR) / CORRECTIONS_NAME
    return path.read_text(encoding="utf-8") if path.exists() else ""


def validate_entry_files(files, hypotheses):
    """Every way the entry files break the naming, the one-entry rule or the format. Empty when sound."""
    errors = []
    for name in sorted(files):
        text = files[name]
        lines = text.splitlines()
        if ENTRY_NAME.match(name) is None:
            errors.append("%s: not named `<date>-<model|liquidity>-<PR, 5 digits>-<H#>-<step N|G n>.md`" % name)
            continue
        if sum(1 for line in lines if line.startswith("### ")) != 1 or not lines or not lines[0].startswith("### "):
            errors.append("%s: must hold exactly one entry, starting with its `### ` heading" % name)
            continue
        heading = HEADING.match(lines[0])
        if heading is not None and not heading_matches_name(name, heading):
            errors.append("%s: the file name disagrees with its heading %r" % (name, lines[0]))
        errors += ["%s: %s" % (name, e) for e in validate_log(text, hypotheses)]
    return errors


def stale_errors(log_text, header, files, corrections=None):
    """`log.md` against the assembly of the header, the entry files and the corrections."""
    if log_text == assemble(header, files, corrections):
        return []
    return ["docs/research/log.md is not the assembly of docs/research/log/: run "
            "`python3 scripts/check_research_log.py assemble` (never edit log.md by hand)"]


def frozen_errors(base, head):
    """Entry files on the base ({name: text}) that the head edits, renames or deletes: the log is append-only."""
    errors = []
    for name, base_text in sorted(base.items()):
        if name not in head:
            errors.append("%s: an entry file on the base is deleted or renamed" % name)
        elif base_text != head[name]:
            errors.append("%s: an entry file on the base is edited" % name)
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
    build = sub.add_parser("assemble")
    build.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    hypotheses = plan_hypotheses(PLAN.read_text())
    if args.command == "assemble":
        header, files = read_entry_files()
        if args.check:
            corrections = read_corrections()
            errors = correction_errors(corrections, files)
            errors += stale_errors(LOG.read_text(encoding="utf-8"), header, files, corrections)
            for error in errors:
                print(error)
            if not errors:
                print("research log: log.md is the assembly of the entry files")
            return 1 if errors else 0
        errors = correction_errors(read_corrections(), files)
        if errors:
            for error in errors:
                print(error)
            return 1
        LOG.write_text(assemble(header, files, read_corrections()), encoding="utf-8")
        print("wrote %s from %d entry files" % (LOG.relative_to(ROOT), len(files)))
        return 0
    if args.command == "check-block":
        errors = validate_log(Path(args.file).read_text(), hypotheses)
    else:
        errors = validate_log(LOG.read_text(), hypotheses)
        header, files = read_entry_files()
        errors += validate_entry_files(files, hypotheses)
        errors += correction_errors(read_corrections(), files)
        errors += stale_errors(LOG.read_text(encoding="utf-8"), header, files, read_corrections())
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
            base_files = {}
            for path in _git("ls-tree", "-r", "--name-only", merge_base, "--", "docs/research/log/").split("\n"):
                name = path.rsplit("/", 1)[-1]
                if path and name not in (HEADER_NAME, CORRECTIONS_NAME):
                    base_files[name] = _git("show", "%s:%s" % (merge_base, path))
            errors += frozen_errors(base_files, files)
            errors += check_change(changed, base_text, head_text,
                                   closed_issues(os.environ.get(args.body_env, "")))
    for error in errors:
        print(error)
    if not errors:
        print("research log: ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
