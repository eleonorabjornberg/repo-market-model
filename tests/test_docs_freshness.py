"""The published documents must not transcribe facts that rot.

Two failures had already happened when this guard was written, and both are this
project's own thesis turned back on its documentation.

**A test count in prose.** `README.md` said 361 tests. `REPRODUCIBILITY.md` said
361 at commit `5dea543`. `docs/PROJECT_STATUS.md` said 409 at `ada77ac`. The suite
ran 417. Every one of those numbers was true when it was typed. A count is a
measurement *of a commit*, and prose does not carry the commit, so a count in
Markdown is not a fact -- it is a fact's decayed remains.

**A date typed by hand.** `docs/PROJECT_STATUS.md` was headed "Measured on 11
September 2026" and `docs/DATA_QUALITY_DECISIONS.md` deferred a decision as of "10
September 2026", while every commit in the repository was authored on 7 September.
A status page dated later than it could possibly have been written is information
dated other than when it was actually available: the exact failure this repository
is built to detect, published on its own front matter, where a reviewer invited by
the README to check provenance will find it first.

**A command that no longer parses.** `REPRODUCIBILITY.md` told readers to run
`backtest data/sample/daily_market.csv` with no further arguments. From `1cd7a9f`
that command exited with *"the following arguments are required"*, and the README
published the same broken invocation. A published command is a claim about the
software in exactly the way a published count is a claim about the suite: true
when it was typed, decaying from that moment, and read by someone who was invited
to check this repository's provenance. The first repair of it was made by hand,
which is not a guard -- the identical rot two files away in `README.md` survived
that repair and was found only by parsing every invocation.

Neither is a discipline problem, so neither has an editorial fix. The remedies are
structural and this module enforces both:

* the size of the suite is whatever CI last printed, and no page transcribes it;
* "when" is a commit, which is a timestamp that cannot be typed wrong. A page that
  needs to say when it was measured names the commit and lets the reader run
  `git show -s --format=%ci <sha>`.

`CLAUDE.md` and `AGENTS.md` were once excluded here, as stop-work pointers that
existed only in the author's checkout. They are tracked from 9 September 2026 --
they carry the standing rules every agent session loads, and a rule that lives in
one checkout is a rule no fresh worktree has. Being tracked makes them published
documents, and everything below applies to them: no transcribed count, no
hand-written date, no command that has stopped parsing, no Python version other
than the declared one. Standing rules decay exactly like the pages they govern.

Scope is the Markdown a cloner actually receives. The working logs under
`docs/block-*/`, `docs/merge-*/`, `docs/state-of-main-*.md` and
`docs/track-*-decisions-*.md` are gitignored by design and are out of scope --
they are handoffs, not records, and they are allowed to carry the dates they were
written under. `EXCLUDED_PREFIXES` is asserted against `.gitignore` rather than
trusted, because a scope anchored to nothing cannot fail: if those patterns ever
stop being ignored, the working logs become published documents and this guard
must start reading them.
"""

from __future__ import annotations

import contextlib
import datetime
import io
import json
import pathlib
import re
import subprocess
import shlex
import sys
import unittest

from repo_model import cli

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Gitignored working logs. Each prefix is checked against .gitignore below.
EXCLUDED_PREFIXES = (
    "docs/block-",
    "docs/merge-",
    "docs/state-of-main-",
    "docs/track-",
)

# A digit run standing within two words of "test", "pass" or "assertion". Catches
# "409 tests", "361 standard-library tests", "360 passes". Does not catch prose
# that counts in words ("two implementers"), which does not rot the same way: a
# word is a claim about design, a numeral is a measurement of a commit.
COUNT_CLAIM = re.compile(
    r"\b\d[\d,]*\s+(?:[A-Za-z][A-Za-z-]*\s+){0,2}(?:tests?|passes|assertions?)\b",
    re.IGNORECASE,
)

MONTHS = (
    "January February March April May June "
    "July August September October November December"
).split()
MONTH_INDEX = {name: number for number, name in enumerate(MONTHS, start=1)}

ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
DAY_MONTH_YEAR = re.compile(
    r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{4})\b"
)
MONTH_YEAR = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(\d{4})\b")


def ignored_by_git(root):
    """What git would leave out of a clone of `root`, or None if git cannot say.

    Untracked, ignored entries, with an ignored directory reported once as
    `dir/` rather than file by file. None when `root` is not a git work tree --
    a disposable mutation copy is not one -- and the caller then reads what it
    always read: the walk, less `EXCLUDED_PREFIXES`.
    """
    try:
        listed = subprocess.run(
            [
                "git", "-C", str(root), "ls-files", "-z", "--others",
                "--ignored", "--exclude-standard", "--directory",
            ],
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return tuple(
        entry for entry in listed.decode("utf-8", "surrogateescape").split("\0")
        if entry
    )


def published_markdown(root=REPO_ROOT):
    """Every Markdown file a clone of this repository would contain.

    The walk alone answers a different question -- every Markdown file on this
    disk -- and the two came apart when a worktree grew a `.venv/`: this guard
    then read the READMEs of installed packages as published pages, and a
    package's release date or its own test count would have failed the suite of
    a repository that never shipped it. See `PublishedScopeTests`.
    """
    ignored = ignored_by_git(root) or ()
    found = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(".git/") or "/.git/" in f"/{relative}":
            continue
        if relative.startswith(EXCLUDED_PREFIXES):
            continue
        if any(
            relative == entry or (entry.endswith("/") and relative.startswith(entry))
            for entry in ignored
        ):
            continue
        found.append((relative, path))
    return found


def dates_in(text):
    """Every calendar date the text states, as (date, matched text) pairs.

    A bare "September 2026" is read as the first of that month: the claim it
    makes is that the month had begun, and the first is the earliest reading
    that could be true. Reading it as the last of the month would let a page
    date itself four weeks ahead and pass.
    """
    found = []
    for year, month, day in ISO_DATE.findall(text):
        try:
            found.append(
                (datetime.date(int(year), int(month), int(day)), f"{year}-{month}-{day}")
            )
        except ValueError:
            continue  # not a date; a version string or an identifier
    for day, month, year in DAY_MONTH_YEAR.findall(text):
        try:
            found.append(
                (
                    datetime.date(int(year), MONTH_INDEX[month], int(day)),
                    f"{day} {month} {year}",
                )
            )
        except ValueError:
            continue
    for month, year in MONTH_YEAR.findall(text):
        found.append(
            (datetime.date(int(year), MONTH_INDEX[month], 1), f"{month} {year}")
        )
    return found


# A published *invocation* of this package's command line: `-m repo_model.cli`,
# or the `repo-model` console script pyproject declares. Subcommand names are
# deliberately not part of the marker -- a subcommand this guard has not heard of
# is the one most likely to have been published and then renamed.
#
# It matches an invocation rather than the bare module path because prose names
# the module too. `CLAUDE.md` entered this guard's scope on 9 September and the
# first thing it caught was the sentence "a `repo_model.cli` command that no
# longer parses", reported as a command that does not parse. It does not parse;
# it is also not a command. A guard that cannot tell a mention from an invocation
# reports a defect in its own documentation.
CLI_MARKER = re.compile(r"-m\s+repo_model\.cli\b|(?:^|\s)repo-model(?:\s|$)")

FENCE = re.compile(r"^\s*```")
INLINE_CODE = re.compile(r"`([^`]+)`")

# A leading environment assignment, not an argument: PYTHONPATH=src, and so on.
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

# Text that stands for a value rather than being one, so the command cannot be
# parsed as written: a substitution the shell would compute, or an `<angle>`
# placeholder a reader is meant to replace. Both are skipped rather than guessed
# at -- substituting a value here would check a command nobody published -- and
# a skip is kept distinguishable from a parse all the way up to the assertion.
UNRUNNABLE = re.compile(r"\$\(|\$\{|\$[A-Za-z_]|`|<[A-Za-z][A-Za-z0-9_-]*>")


class Unlexable(str):
    """A command the shell itself could not read, carrying the lexer's complaint.

    Not a skip. An unbalanced quote or a dangling continuation is a defect in the
    published text, and it is also what a dropped continuation join looks like
    from in here -- so it is reported as an offence naming the document, rather
    than raising a traceback out of the extractor.
    """


def _argv(command):
    """The arguments `repo_model.cli` would receive.

    Returns a token list; `None` for a command *skipped* because it stands for a
    value rather than being one -- a shell substitution, or an `<angle>`
    placeholder -- which is a different outcome from parsing and is kept
    distinguishable all the way up to the assertion; or `Unlexable` if the shell
    lexer refused the text.
    """
    if UNRUNNABLE.search(command):
        return None
    try:
        tokens = shlex.split(command)
    except ValueError as error:
        return Unlexable(str(error))
    while tokens and ASSIGNMENT.match(tokens[0]):
        tokens.pop(0)
    if tokens and pathlib.PurePath(tokens[0]).name.startswith("python"):
        tokens.pop(0)
    while tokens and tokens[0].startswith("-") and tokens[0] != "-m":
        tokens.pop(0)  # interpreter flags: -B and friends
    if tokens[:1] == ["-m"]:
        tokens.pop(0)
        if tokens:
            tokens.pop(0)  # the module path itself
    return tokens


def published_cli_commands():
    """Every `repo_model.cli` invocation a cloner is told to run.

    Continuations are joined before anything is matched. These documents wrap
    commands across lines, and a line-by-line extractor sees a fragment, parses
    the fragment and passes -- the quietest way for this guard to check nothing.

    Scope is `published_markdown()`, not a walk of its own. A guard with its own
    idea of which documents are published is a guard that can disagree with the
    one beside it.

    Returns:
        `(document, command, argv)` triples, `argv` None for a skipped command.
    """
    found = []
    for relative, path in published_markdown():
        text = re.sub(r"\\\n\s*", " ", path.read_text())
        fenced = False
        for line in text.splitlines():
            if FENCE.match(line):
                fenced = not fenced
                continue
            candidates = [line] if fenced else INLINE_CODE.findall(line)
            for candidate in candidates:
                if not CLI_MARKER.search(candidate):
                    continue
                command = candidate.strip()
                found.append((relative, command, _argv(command)))
    return found


def cli_subcommands():
    """Every subcommand `cli.build_parser()` defines, asked of the parser.

    Asked of the parser and not of a list kept beside it: a list is a second
    declaration of what this package ships, and two declarations agree until
    they do not. `_name_parser_map` is argparse's own record of the choices a
    subparsers action accepts.
    """
    names = set()
    for action in cli.build_parser()._actions:
        mapping = getattr(action, "_name_parser_map", None)
        if mapping:
            names |= set(mapping)
    return names


def published_subcommands():
    """The subcommand each published invocation actually runs, by document.

    The first non-flag token of the argv `published_cli_commands` extracted,
    which is where argparse reads the choice from. Skipped and unlexable
    commands carry no subcommand and are not counted as publishing one -- a
    template teaching the *shape* of a command has not told anybody how to run
    it, and that is the distinction this whole extractor keeps.
    """
    running = {}
    for document, _command, argv in published_cli_commands():
        if argv is None or isinstance(argv, Unlexable):
            continue
        for token in argv:
            if token.startswith("-"):
                break
            running.setdefault(token, set()).add(document)
            break
    return running


# Every subcommand this package ships, and whether a reader is told how to run
# it. `PUBLISHED` means some document in scope publishes an invocation of it.
# Anything else is the reason it deliberately ships unpublished, and that reason
# is checked in the other direction too: an exemption whose command has since
# been published is wrong in exactly the way a published command that stopped
# parsing is wrong, and it is the half nobody would look at.
PUBLISHED = None

CLI_PUBLICATION = {
    "audit": PUBLISHED,
    "backfill-nmfp": (
        "requires SEC_CONTACT_EMAIL and a route to the SEC, and writes archives "
        "under the gitignored data/raw/. Run as written in a clone it exits on "
        "the missing contact address, so a published invocation would be a "
        "recipe whose first outcome is a refusal"
    ),
    "backtest": PUBLISHED,
    "build": (
        "reads data/raw/, which is gitignored. Run as written in a clone it "
        "exits with 'no raw snapshot manifests under data/raw'. This is "
        "Milestone A's open reproduction clause seen from the command line: "
        "what would make it publishable is committing the inputs or a digest, "
        "not a differently worded invocation"
    ),
    "compare": PUBLISHED,
    "event-holdout": (
        "the declared event windows are 2019 and 2020 and the shipped fixture "
        "is 2026, so on the only panel a clone receives it exits with 'no "
        "training row clears a 6-day gap before 2019-09-16'. A runnable "
        "invocation needs the frozen panel, which is gitignored"
    ),
    "exceedance-backtest": PUBLISHED,
    "fetch": PUBLISHED,
}

# A stated interpreter version in prose: "Python 3.10". Two components only --
# a patch level is not a support claim anybody could keep true.
PYTHON_VERSION = re.compile(r"\bPython (\d+\.\d+)\b")

# `requires-python` out of pyproject.toml. Read by regex rather than by a TOML
# parser because `tomllib` arrived in 3.11 and this repository does not run there,
# which is the very fact this guard exists to keep published.
REQUIRES_PYTHON = re.compile(r"^requires-python\s*=\s*[\"']([^\"']+)[\"']", re.MULTILINE)


def declared_python():
    """The `requires-python` string, the single declaration of the interpreter."""
    text = (REPO_ROOT / "pyproject.toml").read_text()
    match = REQUIRES_PYTHON.search(text)
    if match is None:
        raise AssertionError(
            "pyproject.toml declares no requires-python. It is the one place the "
            "supported interpreter is stated; without it the published documents "
            "have nothing to agree with."
        )
    return match.group(1)


def _padded(text, width):
    """`"3.10"` as a tuple of ints, zero-filled to `width` components."""
    parts = [int(part) for part in text.split(".")]
    return tuple(parts + [0] * (width - len(parts)))


def _clause_admits(operator, bound, version):
    """One comparison of a `requires-python` specifier, against a `major.minor`."""
    if bound.endswith(".*"):
        if operator not in ("==", "!="):
            raise ValueError(
                f"requires-python clause {operator}{bound!r} puts a wildcard behind "
                f"an operator that cannot carry one."
            )
        prefix = bound[:-2]
        matched = version == prefix or version.startswith(prefix + ".")
        return matched if operator == "==" else not matched

    if operator == "~=":
        components = bound.split(".")
        if len(components) < 2:
            raise ValueError(
                f"requires-python clause ~={bound!r} names one component. A "
                f"compatible release needs a series to be compatible with."
            )
        ceiling = _padded(".".join(components[:-1]), len(components) - 1)
        ceiling = ceiling[:-1] + (ceiling[-1] + 1,)
        width = max(len(components), len(version.split(".")))
        return (
            _padded(version, width) >= _padded(bound, width)
            and _padded(version, len(ceiling)) < ceiling
        )

    width = max(len(bound.split(".")), len(version.split(".")))
    left = _padded(version, width)
    right = _padded(bound, width)
    return {
        ">=": left >= right,
        "<=": left <= right,
        "==": left == right,
        "!=": left != right,
        ">": left > right,
        "<": left < right,
    }[operator]


# Longest first: ">=" must be tried before ">", or ">=3.9" reads as ">" of "=3.9".
_OPERATORS = ("~=", ">=", "<=", "==", "!=", ">", "<")


def python_version_admitted(requirement, version):
    """Does `requires-python` admit an interpreter, read as the specifier it is?

    `version` is two components, `"3.10"`, as both prose and `sys.version_info`
    give it, and it is compared as `3.10.0` -- the first release of the series,
    the weakest thing a two-component claim can mean.

    **Substring containment stood here, and it is not this.** It admitted 3.1 under
    `~=3.10.0`; it refused 3.10 under `>=3.9,<3.11`; and under that same range it
    admitted 3.11, the one version this package provably does not import on, because
    the exclusion `<3.11` contains the digits it excludes. A check that reads a
    bound as an endorsement is worse than no check, and the only declaration it
    evaluated correctly was one naming a single series -- which is how the supported
    set came to be one minor version wide, and this machine outside it.
    """
    for clause in requirement.split(","):
        clause = clause.strip()
        if not clause:
            continue
        for operator in _OPERATORS:
            if clause.startswith(operator):
                bound = clause[len(operator):].strip()
                break
        else:
            raise ValueError(
                f"requires-python clause {clause!r} states no comparison operator. "
                f"An unreadable declaration is not a permissive one."
            )
        if not _clause_admits(operator, bound, version):
            return False
    return True



class PublishedScopeTests(unittest.TestCase):
    """Scope is what a clone receives, and a gitignored directory is not in it.

    **The defect.** `published_markdown()` walked the disk. A worktree that grew
    a `.venv/` -- which the optional `ml` extra requires -- put every installed
    package's Markdown in scope. Shown red on `1bef17a` by planting
    `.venv/lib/python3.9/site-packages/fakepkg/README.md` carrying a release
    date years ahead and a four-digit test count: two failures, both
    `AssertionError`, from `test_no_document_is_dated_in_the_future` and
    `test_no_document_transcribes_a_test_count`, each naming the planted path.
    The same plant also turned `tests/test_metrics.py`'s fixed-bin ECE scan red
    (`UnicodeDecodeError` on a latin-1 `.py`); that scanner is Track B's and is
    not changed here. Track B found the metrics case on a real virtualenv; this
    one it did not name, because no Markdown in that virtualenv happened to
    carry a date or a count. Latent is not absent.

    **The repair.** Git says what it would leave out; paths under an ignored
    entry are dropped. Where git cannot answer (a copy that is not a work
    tree), the walk is what it was, so the repair narrows no existing scope.

    **Mutation, recorded on `1bef17a`, Python 3.10.12.** Filter removed from
    `published_markdown` (the `any(...)` clause reduced to `False`): kills
    `test_a_directory_git_ignores_is_not_published` alone, `AssertionError`
    naming the planted README. Unmutated control green before and after. The
    in-repo plant under that mutation reproduces the two failures above.
    """

    def test_a_directory_git_ignores_is_not_published(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            try:
                subprocess.run(
                    ["git", "init", "-q", str(root)], check=True, capture_output=True
                )
            except (OSError, subprocess.CalledProcessError):
                self.skipTest("git is not available to say what it ignores")
            (root / ".gitignore").write_text(".venv/\n")
            package = root / ".venv" / "lib" / "python3.9" / "site-packages" / "pkg"
            package.mkdir(parents=True)
            (package / "README.md").write_text("# pkg\n")
            (root / "NOTES.md").write_text("# notes\n")
            found = [relative for relative, _ in published_markdown(root)]
            # The anchor: a scope that reads nothing would also exclude the plant.
            self.assertIn("NOTES.md", found)
            self.assertNotIn(".venv/lib/python3.9/site-packages/pkg/README.md", found)


class PublishedDocumentTests(unittest.TestCase):
    """Neither a count nor a future date survives in a document a cloner reads."""

    def test_scope_is_anchored_to_gitignore(self):
        """The exclusions are the ignore rules, not a list someone maintains.

        Dropping a pattern from `.gitignore` publishes those working logs. If
        this guard kept its own copy of the list, that change would widen what
        the repository ships without widening what the guard reads, and the
        guard would go on passing about files it no longer covers.
        """
        ignored = (REPO_ROOT / ".gitignore").read_text()
        for prefix in EXCLUDED_PREFIXES:
            self.assertIn(
                prefix,
                ignored,
                f"{prefix!r} is excluded from this guard but is not in .gitignore. "
                f"Either it is now published -- remove it from EXCLUDED_PREFIXES so "
                f"this guard reads it -- or .gitignore lost a rule.",
            )

    def test_something_is_in_scope(self):
        """A guard that reads nothing passes for the wrong reason."""
        found = [relative for relative, _ in published_markdown()]
        self.assertIn("README.md", found)
        self.assertIn("docs/PROJECT_STATUS.md", found)

    def test_no_document_transcribes_a_test_count(self):
        """The suite's size lives in the CI log, which is measured, not typed.

        Four pages carried four different counts and none of them matched the
        suite. The number is not the problem; writing it down where nothing can
        update it is.
        """
        offences = []
        for relative, path in published_markdown():
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                match = COUNT_CLAIM.search(line)
                if match:
                    offences.append(f"{relative}:{number}: {match.group(0)!r}")
        self.assertEqual(
            [],
            offences,
            "A published document transcribes a test count:\n  "
            + "\n  ".join(offences)
            + "\nSay that the suite runs clean and let CI report the size.",
        )

    def test_no_document_is_dated_in_the_future(self):
        """A page cannot have been written after today.

        This is the same check the panel applies to a feature: a value carrying
        an availability later than the moment it is read has not been observed
        yet. Applied to prose, it catches the status page dated 11 September in
        a repository whose newest commit is 7 September.
        """
        today = datetime.date.today()
        offences = []
        for relative, path in published_markdown():
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                for value, text in dates_in(line):
                    if value > today:
                        offences.append(f"{relative}:{number}: {text!r}")
        self.assertEqual(
            [],
            offences,
            "A published document states a date that has not happened:\n  "
            + "\n  ".join(offences)
            + "\nName the commit instead; `git show -s --format=%ci <sha>` is a "
            "timestamp nobody has to type.",
        )


class PublishedCommandTests(unittest.TestCase):
    """Every command a published document tells a reader to run still parses.

    Mutation record. Disposable clone under `$HOME` with `data/`, `.github/`,
    `metadata/`, `.gitignore`, the root Markdown and `docs/PROJECT_STATUS.md`
    present -- this module reads the last three and their absence is a false
    kill. `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`. Control green before and
    after each mutation, module alone and whole suite.

    1. **The historical bug, replayed.** `REPRODUCIBILITY.md`'s `backtest`
       invocation reverted to its pre-repair form, the bare
       `backtest data/sample/daily_market.csv`. Not a hypothetical: this is what
       shipped at `1cd7a9f` and stood for four commits. Killed the parse
       assertion -- `AssertionError: Lists differ: [] != ['REPRODUCIBILITY.md:
       ...']`, carrying argparse's own *"the following arguments are required:
       --registry, --feature, --decision-time, --model, --report"*.
    2. **The continuation join removed**, so a wrapped command is read as its
       first line. Killed the parse assertion, naming both wrapped commands and
       the shell lexer's complaint, *"No escaped character"* -- a line ending in
       a bare backslash is not a command. **This mutation changed the guard.**
       Run before `Unlexable` existed, `shlex.split` raised `ValueError` straight
       out of the extractor: the test died with a traceback that named no
       document, which is the failure mode the brief warns about one level down.
       An unreadable command is now an offence that names its document.
    3. **`CLI_MARKER` tightened** so the extractor matches nothing. Killed the
       document assertion -- `AssertionError: 'REPRODUCIBILITY.md' not found in
       set()` -- and the parse assertion did **not** fire, because with nothing
       extracted there is nothing to fail. That is the whole reason the document
       assertion exists. An extractor is the part of this guard that can go
       quiet, so its silence is made a failure rather than a pass.
    4. **The `<angle>` placeholder dropped from `UNRUNNABLE`**, so a template is
       parsed as though it were a command. Killed the parse assertion, naming
       `CLAUDE.md`'s `... cli <subcommand>` and argparse's *"invalid choice:
       '<subcommand>'"*. The skip is load-bearing: without it a document may not
       teach the shape of a command, only run one.

    All four were re-run when `CLAUDE.md` and `AGENTS.md` entered scope and the
    marker changed, by the rule that a mutation whose kill list names a fixture
    you have changed is re-run rather than assumed. **Mutation 3 was where that
    mattered**: the first attempt applied it with a `sed` whose pattern did not
    match, the suite stayed green, and a mutation that never applied is
    indistinguishable from a mutation that killed nothing -- both print `OK`.
    The mutation was confirmed in the file before its result was believed.

    A count of commands would have been the obvious second assertion and would
    have been wrong twice: it is a transcribed number in the one module that
    exists to refuse transcribed numbers, and it breaks for anyone who correctly
    adds a command. A named document that is known to publish several does the
    same work and stays true.
    """

    def test_every_published_cli_command_parses_against_the_real_parser(self):
        """A published command is a claim about the software, and it decays.

        Parsed, not executed. Parsing catches the whole class of defect that
        occurred -- an argument added, renamed or made required, a subcommand
        removed -- with no network, no writes, and no panel. It does not catch
        an argument whose *value* went stale: a feature name the registry no
        longer carries, or a decision time the panel has no rows for, parses
        perfectly and fails on execution. That gap is a larger block.
        """
        commands = published_cli_commands()
        skipped = [
            f"{relative}: {command}"
            for relative, command, argv in commands
            if argv is None
        ]
        parsed_from = {
            relative
            for relative, _, argv in commands
            if argv is not None and not isinstance(argv, Unlexable)
        }
        self.assertIn(
            "REPRODUCIBILITY.md",
            parsed_from,
            "The reproduction page published no command this guard could parse. "
            "It publishes several, so either the extractor stopped matching -- a "
            "changed fence, a continuation it no longer joins -- or every command "
            "on the page stands for a value rather than being one."
            + ("\n  skipped:\n    " + "\n    ".join(skipped) if skipped else ""),
        )

        parser = cli.build_parser()
        offences = []
        for relative, command, argv in commands:
            if argv is None:
                continue
            if isinstance(argv, Unlexable):
                offences.append(
                    f"{relative}: {command}\n      -> the shell could not read "
                    f"this command: {argv}"
                )
                continue
            captured = io.StringIO()
            try:
                with contextlib.redirect_stderr(captured):
                    parser.parse_args(argv)
            except SystemExit:
                complaint = captured.getvalue().strip().splitlines()
                offences.append(
                    f"{relative}: {command}\n      -> "
                    + (complaint[-1] if complaint else "argparse exited")
                )
        self.assertEqual(
            [],
            offences,
            "A published document tells a reader to run a command that no longer "
            "parses:\n  "
            + "\n  ".join(offences)
            + "\nFix the document, or the flag, whichever moved.",
        )


class PublishedPythonVersionTests(unittest.TestCase):
    """No document states an interpreter version other than the declared one.

    `README.md` and `REPRODUCIBILITY.md` both published *"Python 3.9 or newer"*, and
    `pyproject.toml` declared `>=3.9` beside them. All three agreed with each other
    and none of them was true: the package does not import on 3.11 -- `baseline.py`
    carries a `mappingproxy` default on a frozen dataclass field, which 3.11 refuses
    as a mutable default -- and 3.9 had never been run. Every module parses under
    3.9 syntax, which is a different claim from working there and was the only
    evidence the number ever had.

    3.9 has since been run whole, and the declaration is a range taken from that
    measurement rather than from a pin: both admitted versions run the entire suite
    and the excluded one still fails at import. Until then the declaration was also
    shaped by its own guard -- containment could evaluate a single-series pin and
    nothing else, so `~=3.10.0` was the only honest string it was able to check.
    See `SpecifierEvaluationTests`.

    **Three documents agreeing is not verification.** What this guard can enforce is
    that there is one declaration and that nothing restates it differently, which is
    the drift that let one hand-repaired page sit beside an unrepaired one for four
    commits in the command case. What licenses the declaration itself is measurement,
    and it is recorded in `pyproject.toml` beside the value.

    Mutation record. Disposable clone under `$HOME`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B`, control green before and after, module alone and whole suite.

    1. `README.md`'s stated version changed to 3.9, the historical value. Killed the
       agreement assertion -- `AssertionError: [] != ['README.md:67: Python 3.9 ...']`
       -- naming the document, the line and the declaration it disagrees with.
    2. The version sentence deleted from `REPRODUCIBILITY.md` outright. Killed the
       named-document assertion -- `AssertionError: 'REPRODUCIBILITY.md' not found in
       {'README.md': ['3.10']}` -- while the agreement list stayed empty, because a
       document that says nothing agrees with every declaration. Deleting the claim is
       the cheapest way to make this guard pass, and it is what that assertion refuses.
    3. `requires-python` set to `~=3.12.0`, excluding the running interpreter. Killed
       **both** tests. Re-run after the specifier evaluator replaced containment, as a
       mutation whose fixture this block changed: the interpreter assertion now reports
       `AssertionError: False is not true` and carries the declaration in its message
       rather than in the diff line, and the agreement assertion named every stated
       version in all three documents at once, `CLAUDE.md` included. That is the shape
       to expect -- moving the single declaration moves what every document is checked
       against, which is the point of there being one.
    """

    def test_every_published_python_version_is_the_declared_one(self):
        """A version number in prose is a measurement of an interpreter, not a fact."""
        requirement = declared_python()

        stated_by = {}
        offences = []
        for relative, path in published_markdown():
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                for version in PYTHON_VERSION.findall(line):
                    stated_by.setdefault(relative, []).append(version)
                    if not python_version_admitted(requirement, version):
                        offences.append(f"{relative}:{number}: Python {version}")

        for document in ("README.md", "REPRODUCIBILITY.md"):
            self.assertIn(
                document,
                stated_by,
                f"{document} states no Python version. It is where a reader looks "
                f"before running anything, and a document that states nothing agrees "
                f"with every declaration -- which is the cheapest way to make this "
                f"guard pass.",
            )

        self.assertEqual(
            [],
            offences,
            f"A published document states a Python version that "
            f"pyproject.toml's requires-python = {requirement!r} does not:\n  "
            + "\n  ".join(offences)
            + "\nOne declaration, in pyproject.toml. Change it there, or the document.",
        )

    def test_the_interpreter_running_this_suite_is_the_declared_one(self):
        """A green suite on an unsupported interpreter says nothing about the claim."""
        requirement = declared_python()
        running = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.assertTrue(
            python_version_admitted(requirement, running),
            f"This suite is running on Python {running}, which "
            f"requires-python = {requirement!r} does not admit. Either the project "
            f"supports it and the declaration is stale, or it does not and this run "
            f"proves nothing.",
        )


class SpecifierEvaluationTests(unittest.TestCase):
    """A declaration is evaluated as a specifier, not searched for as a substring.

    `requires-python` was checked with `version in requirement` -- containment in a
    string. It agreed with the specifier only for a declaration naming exactly one
    series, which is how the supported set came to be one minor version wide: the
    declaration was shaped to fit its guard. Three divergences, all live:

    * `~=3.10.0` **admitted 3.1**, a version that has never run this package, because
      `3.1` is a substring of `3.10.0`.
    * `>=3.9,<3.11` **refused 3.10**, a version measured green, because `3.10` appears
      nowhere in that string.
    * `>=3.9,<3.11` **admitted 3.11**, the one version that provably fails at import,
      because an exclusion contains the digits it excludes. A check that reads a bound
      as an endorsement is worse than no check.

    The third is why this could not wait on the interpreter question being settled some
    other way. Widening the declaration without replacing the check would have published
    a range whose upper bound the guard read as permission.

    Run red first against containment, which is what the module carried: the criterion
    failed naming all three cases above, `AssertionError`, before the evaluator existed.

    Mutation record. Disposable copy under `$HOME`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B`, control green before and after, criterion alone and whole suite.

    1. `<` made unconditionally true. Killed the criterion -- `AssertionError: [] !=
       ["'>=3.9,<3.11' vs Python 3.11: expected False, got True"]` -- and killed nothing
       else in the suite.
    2. `~=` reduced to its floor, dropping the series ceiling. Killed the criterion on
       `'~=3.10.0' vs Python 3.11`, same exception type, one test.
    3. The zero-fill removed from `_padded`, so tuples of unequal length compare. Killed
       the criterion on `'~=3.10.0' vs Python 3.10` -- `(3, 10)` is less than
       `(3, 10, 0)` -- one test.

    A fourth attempt is recorded because it proved nothing. Comparing versions as strings
    rather than integers, to test the ordering, raised `TypeError: can only concatenate
    str (not "int") to str` out of the `~=` ceiling arithmetic before any comparison
    happened: red, and about something else entirely. Mutation 3 is the ordering
    hypothesis actually tested.

    What this cannot see. A document may state a version the range admits and still be
    wrong about it. `PYTHON_VERSION` reads every `Python X.Y` in prose as a claim of
    support, so a page cannot name an unsupported version in that form, and both pages
    state the exclusion without the keyword -- a hole, not a style choice. And the
    unreadable-clause branch of `python_version_admitted`, which refuses a declaration
    stating no operator rather than admitting everything, is exercised by nothing here.
    """

    CASES = (
        ("~=3.10.0", "3.1", False,
         "containment admits it: '3.1' is a substring of '~=3.10.0'"),
        (">=3.9,<3.11", "3.10", True,
         "containment refuses it: '3.10' is not a substring of '>=3.9,<3.11'"),
        (">=3.9,<3.11", "3.9", True, "the floor is inclusive"),
        (">=3.9,<3.11", "3.11", False, "the ceiling is exclusive"),
        (">=3.9,<3.11", "3.8", False, "below the floor"),
        ("~=3.10.0", "3.10", True, "the declared series"),
        ("~=3.10.0", "3.11", False, "~= caps the minor series"),
    )

    def test_a_declaration_is_evaluated_as_a_specifier_not_as_a_substring(self):
        """Containment agrees with the specifier only for a single-series pin."""
        wrong = []
        for requirement, version, expected, why in self.CASES:
            got = python_version_admitted(requirement, version)
            if got is not expected:
                wrong.append(
                    f"{requirement!r} vs Python {version}: expected {expected}, "
                    f"got {got} -- {why}"
                )
        self.assertEqual(
            [],
            wrong,
            "requires-python is a PEP 440 specifier and these cases are where "
            "substring containment and the specifier disagree:\n  "
            + "\n  ".join(wrong),
        )


if __name__ == "__main__":
    unittest.main()


def registry():
    """The source registry, read fresh: a mutation must be able to move it."""
    return json.loads(
        (REPO_ROOT / "metadata" / "sources.json").read_text(encoding="utf-8")
    )


def _coverage_floor_is_one_number():
    """One declared floor for the whole published history."""
    cross_section = registry()["sec_nmfp"]["cross_section"]
    return len(cross_section.get("eras", ())) <= 1


def _split_month_end_divides_the_universe():
    """Two REPORTDATEs inside one calendar month are two cross-sections.

    Evaluated by asking the code, not by reading a test name: 29 and 31 July
    2011 is the split this limitation was written about.
    """
    from repo_model.ingest import _nmfp_cross_section

    return _nmfp_cross_section(datetime.date(2011, 7, 29)) != _nmfp_cross_section(
        datetime.date(2011, 7, 31)
    )


def _treasury_settlement_is_one_aggregate():
    """The settlement series is declared as one field, with no split components."""
    for source in registry().values():
        fields = source.get("fields", ())
        if "treasury_settlement" in fields:
            return not any(
                str(field).startswith("treasury_settlement_") for field in fields
            )
    return False


def _part_of_the_cli_is_unpublished():
    """A subcommand the parser defines that no published document invokes.

    Evaluated against `cli.build_parser()` and the documents themselves, never
    against `CLI_PUBLICATION`: a predicate over that table would be a claim
    about the exemption list rather than about the software, and recording one
    more exemption would silently repair the limitation it is supposed to
    disclose.
    """
    return bool(cli_subcommands() - set(published_subcommands()))


def _nmfp_absence_is_indistinguishable_from_parse_failure():
    """No source declares a structural zero, and nothing in the package reads one.

    `7b8f0c9` corrected both pages about `mmf_on_rrp` -- the field is derived and
    it produces the facility -- and left one half standing: an absent value and a
    parse failure still have the same representation, so "money funds held no Fed
    ON RRP" and "we never found it" are the same row, which is nothing.

    **Two clauses, and the second is the load-bearing one.** A predicate over
    `structural_zeros` alone would let one entry in `metadata/sources.json` -- a
    track's file -- silently repair a limitation about the software, which is the
    hazard `_part_of_the_cli_is_unpublished` refuses two screens up. A declaration
    nothing reads cannot distinguish anything. So the limitation holds until the
    package actually reads the declaration, and no edit to the registry alone can
    end it.

    **The second clause is now satisfied, and the first is gated on a review.**
    Block 4b (`d8675d2`) added the reader -- `declared_structural_zeros` in
    `data.py` -- and a record of a derived field that matched nothing in a table
    it read. The brief for it said this guard would fire; it could not, and
    Track A said so before anyone asked. `tests/test_contract.py` refuses any
    `structural_zeros` entry while `structural_zeros_reviewed` is false, so no
    block can land the first clause without a review nobody has done. The row is
    therefore a `declaration` row now, not a `software` one, and it names the
    review as its blocker. A review recorded before a declaration's `when` has a
    grammar would let one period's zero stand for every month, 2026-07-31
    included -- the reader answers "declared at all", not "declared for this
    month".

    Mutation record
    ---------------

    Disposable copy under `$HOME`, `-B` with `PYTHONDONTWRITEBYTECODE=1`, control
    green before and after (702, on 3.10.12), each applied to a restored copy.

    1. The published sentence deleted from `docs/PROJECT_STATUS.md`. Kills
       `test_every_limitation_that_still_holds_is_still_published`,
       `AssertionError`, naming the limitation and the document.
    2. A structural zero added to the registry and nothing else. Kills nothing,
       **as intended**: the field is declared and still unread, so the software
       has not changed and neither has the limitation. This is the mutation that
       proves the second clause is doing work rather than decorating the first.
    3. The same registry entry plus a reader of `structural_zeros` in
       `src/repo_model/`. Kills `test_no_published_limitation_outlives_its_repair`,
       `AssertionError` -- the limitation is repaired and the page still
       publishes it, which is the stop-and-report this table exists to force.
    """

    declared = any(source.get("structural_zeros") for source in registry().values())
    read = any(
        "structural_zeros" in path.read_text(encoding="utf-8")
        for path in sorted((REPO_ROOT / "src" / "repo_model").glob("*.py"))
    )
    return not (declared and read)



def _sec_nmfp_structural_zeros_are_unreviewed():
    """Nobody has reviewed Form N-MFP's structural zeros, so none may be declared.

    The blocker for `nmfp_absence_indistinguishable` since block 4b landed its
    reader. When a review is recorded this goes false, and the limitation is
    then either repaired -- a declaration exists and is read, so
    `test_no_published_limitation_outlives_its_repair` fires until the page
    changes -- or it still holds with no blocker, so
    `test_no_published_limitation_claims_a_blocker_that_has_cleared` fires. Either
    way the page is made to say what the review found.
    """
    return not registry()["sec_nmfp"]["structural_zeros_reviewed"]

def _identity_tolerance_is_a_single_absolute():
    """Every declared identity tolerance is an absolute bound and nothing else."""
    identities = registry()["sec_nmfp"]["identities"]
    return all(
        set(identity["tolerance"]) <= {"absolute", "unit"} for identity in identities
    )


# A limitation the repository publishes, the exact words it publishes it in, and
# a predicate that says whether it still holds. The predicate is evaluated
# against the registry or the code -- never against another document, and never
# against the presence of a test class, which is a claim about the suite rather
# than about the software.
def _a_clone_does_not_receive_the_frozen_panel():
    """The panel is not in a clone, so no runnable invocation can publish `build`.

    `docs/PROJECT_STATUS.md` states the blocker in prose: the three unpublished
    subcommands "each exit on something a clone does not have, and `build`'s is
    the same missing thing as Milestone A's open reproduction clause." This is
    that sentence made evaluable.

    Asked of git rather than of the filesystem: the panel exists in the
    integration checkout, which is exactly the checkout where asking the
    filesystem would answer the wrong question. Returns True while a clone
    would not receive it, and therefore while the limitation is blocked rather
    than merely open.
    """
    try:
        listed = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "data/processed/funding_panel.csv"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return True
    return listed.returncode != 0


#: Where a limitation lives, and therefore **who is able to close it**. This is
#: the field the table could not previously carry, and its absence has cost
#: this repository real rounds: a block was once queued to a track whose three
#: files were all human-owned, and every stated precondition passed because
#: each described the state of the tree and none described who was allowed to
#: change it. A limitation's kind is that question asked one level earlier.
#:
#:   `software`      the package cannot do the thing; repaired under src/
#:   `declaration`   metadata declares one thing where reality has several;
#:                   repaired in metadata/, which is Track A's
#:   `documentation` the software is fine and nothing published says so;
#:                   repaired on a HUMAN_ONLY page, so no track can close it
KINDS = ("software", "declaration", "documentation")

#: Each entry: a name, its kind, the document that discloses it, the sentences
#: it is published in, a predicate that is true while the limitation holds, and
#: a predicate that is true while a *stated blocker* still blocks -- or None
#: where nothing is claimed to block it, which is itself a claim: a limitation
#: with no blocker is one nobody has an excuse for leaving open.
LIMITATIONS = (
    (
        "nmfp_per_era_floor",
        "declaration",
        "docs/PROJECT_STATUS.md",
        (
            "**The coverage floor is declared for one era.**",
            "the coverage floor is still one number for every era.",
        ),
        _coverage_floor_is_one_number,
        None,
    ),
    (
        "nmfp_split_month_end",
        "software",
        "docs/PROJECT_STATUS.md",
        ("a split month-end still divides one reporting universe",),
        _split_month_end_divides_the_universe,
        None,
    ),
    (
        "nmfp_identity_tolerance",
        "declaration",
        "docs/PROJECT_STATUS.md",
        ("**The N-MFP identity tolerance is a single absolute bound**",),
        _identity_tolerance_is_a_single_absolute,
        None,
    ),
    (
        "treasury_settlement_aggregate",
        "declaration",
        "docs/PROJECT_STATUS.md",
        (
            "aggregates decisions it does not implement.** Security type, tenor, and "
            "Fed SOMA add-ons are summed into one series.",
        ),
        _treasury_settlement_is_one_aggregate,
        None,
    ),
    (
        "cli_partially_unpublished",
        "documentation",
        "docs/PROJECT_STATUS.md",
        ("**Part of the command line is unpublished.**",),
        _part_of_the_cli_is_unpublished,
        _a_clone_does_not_receive_the_frozen_panel,
    ),
    (
        "nmfp_absence_indistinguishable",
        "declaration",
        "docs/PROJECT_STATUS.md",
        # The trailing comma is part of the published token: the matcher is a
        # word stream and "representation" is not "representation,". The same
        # punctuation trap failed the corrected bullet at 2ced98e.
        ("an absent value and a parse failure still have the same representation,",),
        _nmfp_absence_is_indistinguishable_from_parse_failure,
        _sec_nmfp_structural_zeros_are_unreviewed,
    ),
)


def _words(path):
    """Whitespace-separated words with the line each came from.

    Published prose is hard-wrapped, so a sentence is not a line and a claim
    quoted from one is not a substring of any line in the file.
    """
    found = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        for word in line.split():
            found.append((word, number))
    return found


def _line_stating(path, claim):
    """The line the claim starts on, or None if the document does not state it."""
    wanted = claim.split()
    words = _words(path)
    for start in range(len(words) - len(wanted) + 1):
        if [word for word, _ in words[start : start + len(wanted)]] == wanted:
            return words[start][1]
    return None


class PublishedLimitationTests(unittest.TestCase):
    """A published limitation must not outlive the work that repaired it.

    Every other guard in this module watches a claim that decays on its own: a
    count drifts, a date recedes, a command stops parsing. A limitation decays
    the opposite way -- it is falsified by *success*, at the moment the thing it
    describes gets fixed, which is the moment nobody is looking for it. The page
    that says "not yet" is read as the honest half of a status page and is the
    half with no reader watching it.

    Two of them went stale here within one day and neither commit was wrong to
    leave them. `346d4ff` made the calendar month the assembly unit while
    `docs/PROJECT_STATUS.md` went on publishing *"a split month-end still divides
    one reporting universe across two reference dates"*; a per-era coverage floor
    landed the same evening under a heading reading **"The coverage floor is
    declared for one era."** Both are HUMAN_ONLY pages that no track may edit, so
    each track did the correct thing and the page stayed wrong. `PROJECT_STATUS.md`
    is published as a *measured* file, and what is measured about it is the counts,
    the dates, the commands and the interpreter. Everything it says about what the
    software cannot yet do is prose, and prose is what went stale.

    So each limitation is declared once here with the words it is published in
    and a predicate over the registry or the code, and the two are required to
    agree in both directions. A repaired limitation may not still be published,
    and a live one may not have quietly stopped being. The second half is what
    stops the cheap pass: deleting the sentence would otherwise satisfy the
    first assertion exactly as removing the limitation does.

    **What this cannot do is find a limitation nobody declared here**, the same
    honest bound `PublishedPythonVersionTests` carries: it enforces that there is
    one declaration and that nothing disagrees with it, not that everything true
    has been declared. A limitation added to a published page and not added to
    this table is invisible to it. `test_ingest.py` and `test_data.py` are where
    a new limitation earns an entry -- a block that closes one is the block that
    should be deleting a row's worth of prose.

    Mutation record. Disposable copy under `$HOME`, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B`, `__pycache__` cleared before each run, control green before and after,
    module alone and whole suite. Every kill below is an `AssertionError`.

    **The copy list in `CLAUDE.md` does not produce a green control.** It names `data/`,
    `.github/`, `metadata/`, `.gitignore`, the root Markdown and `docs/PROJECT_STATUS.md`,
    and omits `.claude/`, which has held the ownership hook since 9 September. Without it
    `test_ownership_hook` contributes seven errors to the control -- a red control that
    looks like a finding and is a missing directory, which is the exact trap the same
    paragraph warns about. Copied `.claude/` too; reported for a human edit.

    1. **The repaired sentences restored to the page.** Both N-MFP claims re-inserted
       into `docs/PROJECT_STATUS.md` with the code left repaired. Killed
       `test_no_published_limitation_outlives_its_repair`, one test in the whole suite.
       This is the acceptance criterion and its own mutation target: the defect restated
       must not pass.
    2. **The registry reverted and the page not.** `cross_section.eras` truncated to its
       first entry, so the per-era floor "holds" again while the page no longer says so.
       Killed `test_every_limitation_that_still_holds_is_still_published` in this module.
       **It is a coarse mutation and the record should not overstate it:** across the
       whole suite it took down eighteen tests carrying `KeyError` and `ValueError` as
       well, because truncating the era list breaks ingestion outright. The kill that
       counts is the single `AssertionError` in this module; the rest is collateral and
       is recorded as collateral.
    3. **The live claim deleted from the page.** The Treasury-settlement sentence removed
       while the limitation still holds. Killed
       `test_every_limitation_that_still_holds_is_still_published`, one test in the whole
       suite. Deleting the sentence is the cheapest way to pass assertion 1, and this is
       the assertion that refuses it.
    4. **Claim matching made line-local** -- `_line_stating` searching each line for the
       claim as a substring instead of matching across the document's word stream. Killed
       the same assertion, one test in the whole suite, because the Treasury-settlement
       claim spans a line break.

       **This mutation killed nothing when the guard was first committed, and that was
       measured rather than assumed.** Re-run against the table as it then stood -- two
       repaired entries and one live one whose sentence happened to fit on a single line
       -- it returns `OK`. Assertion 1 only ever requires a claim to be *absent*, and
       narrower matching cannot make an absent claim present, so nothing there could see
       it. The word-stream matching was unexercised code in a published guard until a
       live entry with a wrapped sentence existed. A guard needs at least one live entry
       per code path it claims to have, and counting entries is not the same as covering
       paths.
    5. **The live predicate forced to "repaired."** `_treasury_settlement_is_one_aggregate`
       reduced to `return False` while the page still states the limitation. Killed
       `test_no_published_limitation_outlives_its_repair`, one test in the whole suite --
       the mirror of mutation 1, moving the predicate rather than the prose, so both
       halves of the agreement are shown to be load-bearing from both sides.

    **Two fields added 10 September, and what they are for.** Until then this table
    said whether a limitation still held and nothing else. It could not say *who is
    able to close a row*, and it could not say *why a row is still open* -- and the
    second of those decays exactly like the first. A limitation is falsified by
    success; a stated blocker is falsified by success one level up, in the reason
    rather than in the claim, and nothing was watching that at all. A row can sit
    at the bottom of a queue for four rounds reading "blocked on X" while X cleared
    in round two.

    `kind` answers the first. It is not a taxonomy for its own sake: this
    repository once queued a block to a track whose three files were all
    human-owned, and every stated precondition passed, because each described the
    state of the tree and none described who was permitted to change it. A
    `declaration` row is closed in `metadata/` and is Track A's; a `software` row is
    closed under `src/`; a `documentation` row is closed on a HUMAN_ONLY page and no
    track can close it however well it does its block.

    `blocked_by` answers the second, and only rows with a checkable blocker carry
    one. `cli_partially_unpublished` is blocked by something checkable -- a clone
    does not receive the frozen panel, so no runnable invocation can publish
    `build` -- and so, since block 4b, is `nmfp_absence_indistinguishable`, by the
    unreviewed `sec_nmfp` structural zeros. The other four carry `None`, which is not an exemption but the assertion that
    nothing is claimed to block them. Both branches are live, which is the standing
    requirement mutation 4 above established: a guard needs at least one live entry
    per code path it claims to have.

    6. **The blocker cleared.** `_a_clone_does_not_receive_the_frozen_panel` reduced
       to `return False` while the limitation still holds and the page still states
       it. Killed `test_no_published_limitation_claims_a_blocker_that_has_cleared`,
       `AssertionError`, one test in the whole suite. This is the new acceptance
       criterion and its own mutation target.
    7. **The blocker dropped to `None`.** `cli_partially_unpublished`'s `blocked_by`
       replaced with `None`. **Survived, and was expected to:** every assertion here
       iterates the table, so a row that declares nothing is a row with nothing to
       contradict. It is the same hole recorded one class down for `QUOTATIONS`, and
       it cannot be closed the same way `CLI_PUBLICATION` closed its own -- there is
       no enumerable universe of blockers to check the table against. Recorded as
       the standing limit rather than left to be rediscovered.
    8. **A kind misspelled.** `"documentation"` written `"docmentation"`. Killed
       `test_every_limitation_declares_a_kind_this_module_knows`, `AssertionError`,
       one test in the whole suite. A closed vocabulary that admits a typo is a
       field that reads as data and behaves as free text.

    Control green before and after all three, 704 tests, run in a disposable copy
    under `$HOME` with `__pycache__` cleared between runs and each mutation applied
    to a restored copy rather than on top of the last.

    9. **The review recorded** (added with the second blocker, after block 4b):
       `sec_nmfp`'s `structural_zeros_reviewed` set true, `structural_zeros` left
       empty. Killed `test_no_published_limitation_claims_a_blocker_that_has_cleared`,
       `AssertionError` naming `nmfp_absence_indistinguishable`, one test in the
       whole suite. Against the table as it stood before the blocker was added,
       the same mutation -- all six sources flipped -- killed nothing: a review
       could land and the page would go on saying the gap was the software's.
       Control green before and after, 721 tests on 3.10.12, disposable copy.
    """

    def test_no_published_limitation_outlives_its_repair(self):
        """A limitation the code no longer has is not a limitation."""
        stale = []
        for name, _kind, document, claims, still_holds, _blocked_by in LIMITATIONS:
            if still_holds():
                continue
            for claim in claims:
                line = _line_stating(REPO_ROOT / document, claim)
                if line is not None:
                    stale.append(f"{document}:{line}: {name}: {claim!r}")

        self.assertEqual(
            [],
            stale,
            "A published document still states a limitation this repository has "
            "already repaired:\n  "
            + "\n  ".join(stale)
            + "\nThe block that closed it did not close the page. Edit the "
            "document, or the predicate is wrong about the repair.",
        )

    def test_every_limitation_that_still_holds_is_still_published(self):
        """A limitation that stops being disclosed has not stopped being one."""
        unstated = []
        for name, _kind, document, claims, still_holds, _blocked_by in LIMITATIONS:
            if not still_holds():
                continue
            if all(
                _line_stating(REPO_ROOT / document, claim) is None for claim in claims
            ):
                unstated.append(f"{document}: {name}: {claims[0]!r}")

        self.assertEqual(
            [],
            unstated,
            "A limitation this repository still has is no longer stated in the "
            "document that declared it:\n  "
            + "\n  ".join(unstated)
            + "\nDeleting the sentence is the cheapest way to pass the "
            "companion assertion, and it is what this one refuses.",
        )

    def test_every_limitation_declares_a_kind_this_module_knows(self):
        """A limitation that does not say where it lives does not say who can close it."""
        wrong = [
            f"{name}: {kind!r}"
            for name, kind, _document, _claims, _holds, _blocked in LIMITATIONS
            if kind not in KINDS
        ]
        self.assertEqual(
            [],
            wrong,
            "A limitation declares a kind this module does not know:\n  "
            + "\n  ".join(wrong)
            + f"\nKnown kinds are {KINDS}. The kind is what says whether a "
            "track can close the row or only a human can.",
        )

    def test_no_published_limitation_claims_a_blocker_that_has_cleared(self):
        """A limitation whose stated blocker is gone is open, not blocked.

        The other two assertions both ask whether the limitation still holds.
        Neither can see the case this one exists for: the limitation holds, the
        page is right to state it, and the reason it was left alone stopped
        being true several rounds ago. That is how a row sits at the bottom of
        a queue with "blocked on X" beside it while nobody re-reads X -- the
        same decay as a stale limitation, one level up, in the reason rather
        than in the claim.

        A `None` blocker is not exempt from anything; it is the assertion that
        nothing is claimed to block the row, which is what makes leaving it
        open a queue decision rather than an external constraint.
        """
        cleared = []
        for name, kind, document, _claims, still_holds, blocked_by in LIMITATIONS:
            if blocked_by is None or not still_holds():
                continue
            if not blocked_by():
                cleared.append(f"{name} ({kind}, disclosed in {document})")

        self.assertEqual(
            [],
            cleared,
            "A published limitation still names a blocker that has cleared:\n  "
            + "\n  ".join(cleared)
            + "\nThe limitation is still real and the page is still right to "
            "state it. What is no longer true is the reason it is open. It is "
            "actionable now: either close it or record a blocker that blocks.",
        )


class PublishedCommandCoverageTests(unittest.TestCase):
    """A command nobody publishes is the half the parse guard cannot see.

    `PublishedCommandTests` above checks that every command a document tells a
    reader to run still parses. It validates in the direction the defect it was
    born from ran: a published command decayed, and the guard was written to
    catch a published command decaying. The other direction was never checked,
    and it does not decay -- it accumulates. A subcommand added to the parser
    and published nowhere is invisible to a guard whose scope is the set of
    published invocations, because it is the complement of that set.

    Run red first against the live defect, before any repair: with every
    subcommand declared published it named five --
    `backfill-nmfp, build, compare, event-holdout, exceedance-backtest` -- out of
    the eight `build_parser` defines. `compare` had landed in the same round and
    the other four had accumulated over many. Two of the five were published
    against the shipped fixture in the same commit, after checking that they run
    there and not only that they parse; the three that remain each exit on
    something a clone does not have, and each carries that reason here.

    **The exemption is the cheap pass, so it is checked in both directions.**
    Recording a reason is how a subcommand leaves the set the second assertion
    reads, and an exemption is the one claim in this module that nothing else
    would ever contradict: the command it exempts is by definition absent from
    the documents, so the guard sees nothing either way. The third assertion is
    what bites when a recorded exemption stops being true.

    `CLI_PUBLICATION` is not a list of what this package ships -- `cli_subcommands`
    asks the parser for that -- and the first assertion is the seam between them.
    Without it the other two are assertions about a subset somebody chose.

    Mutation record
    ---------------

    Clone under `$HOME`, never the mount, with the working-tree copies of the
    three files this commit changes laid over it and `.claude/` copied in --
    `CLAUDE.md`'s copy list predates the ownership hook and omits it, which costs
    seven errors in an otherwise green control. `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B`, `__pycache__` cleared between runs, control green before and
    after all four. Every mutation confirmed present in the file before its
    result was read: a `sed` that does not match prints `OK` exactly like a
    mutation that killed nothing. Exception types recorded, not counts.

    1. **`build`'s exemption removed**, declared `PUBLISHED` -- the live defect
       replayed for one command. Kills exactly 1 --
       `test_every_command_declared_published_is_published_somewhere`,
       `AssertionError: Lists differ: [] != ['build']`.
    2. **`compare` recorded as unpublished** with the reason *"no recipe has been
       written for it yet"*, while `REPRODUCIBILITY.md` publishes it. Kills
       exactly 1 -- `test_a_command_recorded_as_unpublished_is_not_published_anywhere`,
       `AssertionError`, naming the command, the reason and the document that
       contradicts it. This is the cheapest way to pass assertion 2 and this is
       what refuses it.
    3. **`compare` dropped from `CLI_PUBLICATION` altogether.** Kills exactly 1 --
       `test_the_registry_classifies_exactly_the_commands_the_parser_defines`,
       `AssertionError: Tuples differ: (set(), set()) != ({'compare'}, set())`.
       **Assertion 2 did not fire**, and that is the finding this mutation
       records rather than a weakness in it: an unclassified command is outside
       the set assertion 2 iterates, so dropping the entry is quieter than
       lying in it. The same shape as `PublishedCommandTests`' mutation 3, where
       a silenced extractor made the parse assertion pass by having nothing to
       fail.
    4. **The limitation sentence deleted from `docs/PROJECT_STATUS.md`.** Kills
       exactly 1 -- `PublishedLimitationTests.test_every_limitation_that_still_holds_is_still_published`,
       `AssertionError`, naming `cli_partially_unpublished`. Recorded here rather
       than there because it is this block's registry entry that it validates:
       the gap is disclosed on the status page and `_part_of_the_cli_is_unpublished`
       is evaluated against the parser and the documents, so publishing the
       remaining three is the only thing that may remove the sentence.

    **Not run as a mutation, because it cannot be one.** Evaluating
    `_part_of_the_cli_is_unpublished` over `CLI_PUBLICATION` instead of over the
    parser and the documents returns the same answer on this tree and kills
    nothing. It is wrong anyway, and the docstring there says why: the two
    disagree exactly when someone records one more exemption, which is the
    moment the limitation would be silently repaired. A mutation that cannot
    separate the two on the tree it is run against is recorded as an argument,
    not dressed up as evidence.
    """

    def test_the_registry_classifies_exactly_the_commands_the_parser_defines(self):
        """A command added to the parser cannot be ignored by not classifying it."""
        defined = cli_subcommands()
        classified = set(CLI_PUBLICATION)
        self.assertEqual(
            (set(), set()),
            (defined - classified, classified - defined),
            "CLI_PUBLICATION and cli.build_parser() disagree about what this "
            "package ships. Unclassified: "
            + repr(sorted(defined - classified))
            + "; classified but no longer defined: "
            + repr(sorted(classified - defined))
            + ". Every subcommand is either published or carries the reason it "
            "is not; a new one may not arrive unclassified, which is how the "
            "other two assertions here are kept from being about a subset "
            "somebody chose.",
        )

    def test_every_command_declared_published_is_published_somewhere(self):
        """A command declared published must have an invocation to point at."""
        running = published_subcommands()
        missing = sorted(
            name
            for name, reason in CLI_PUBLICATION.items()
            if reason is PUBLISHED and name not in running
        )
        self.assertEqual(
            [],
            missing,
            "These subcommands are declared published and no document in scope "
            "publishes an invocation of them: "
            + ", ".join(missing)
            + ".\nA reader who is invited to check this repository's provenance "
            "is told how to run some of what it ships and left to read argparse "
            "for the rest.",
        )

    def test_a_command_recorded_as_unpublished_is_not_published_anywhere(self):
        """An exemption that has stopped being true is a stale claim like any other."""
        running = published_subcommands()
        contradicted = sorted(
            f"{name}: recorded as unpublished ({reason!r}) but published in "
            + ", ".join(sorted(running[name]))
            for name, reason in CLI_PUBLICATION.items()
            if reason is not PUBLISHED and name in running
        )
        self.assertEqual(
            [],
            contradicted,
            "A subcommand recorded here as deliberately unpublished is published "
            "after all:\n  "
            + "\n  ".join(contradicted)
            + "\nRecording an exemption is the cheapest way to pass the "
            "assertion above, and this is what stops one from outliving the "
            "documentation that made it false.",
        )



# A quotation is a third kind of published claim. A count rots because the suite
# grows; a limitation is falsified by success; a quotation is falsified by
# someone editing the *other* document. `docs/DATA_QUALITY_DECISIONS.md` quotes
# `metadata/sources.json` to argue from it, and the registry is a track's file
# while the document is HUMAN_ONLY -- so the correct action on one side leaves
# the other side wrong, and no assertion in this module could see it.


def _nmfp_identity_tolerance_note():
    """The `tolerance_note` on the N-MFP balance-sheet identity, read fresh."""
    for identity in registry()["sec_nmfp"]["identities"]:
        if identity["name"] == "series_assets_reconcile_to_liabilities_and_net_assets":
            return identity.get("tolerance_note", "")
    return ""


#: Each entry: a name, the document that quotes, the sentence the document
#: publishes the quotation in, the words attributed to the registry, and the
#: registry field they are attributed to.
QUOTATIONS = (
    (
        "nmfp_tolerance_note",
        "docs/DATA_QUALITY_DECISIONS.md",
        "The `tolerance_note` records the outcome in those terms, as \"an ingestion "
        "check that currently fails on a majority of the population it checks\", and "
        "declines to widen the bound into a description of that population.",
        "an ingestion check that currently fails on a majority of the population it "
        "checks",
        _nmfp_identity_tolerance_note,
    ),
)


def _collapsed(text):
    """Whitespace collapsed, so a hard-wrapped quotation matches a JSON string."""
    return " ".join(text.split())


class RegistryQuotationTests(unittest.TestCase):
    """A document that quotes the registry must still be quoting it.

    A count rots because the suite grows; a limitation is falsified by success;
    a quotation is falsified by someone editing the *other* document. The
    registry is a track's file and `docs/DATA_QUALITY_DECISIONS.md` is
    `HUMAN_ONLY`, so the correct action on one side leaves the other side
    wrong and no assertion in this module could see it.

    Mutation record
    ---------------

    Run in a disposable copy under `$HOME`, `-B` with
    `PYTHONDONTWRITEBYTECODE=1`, control green before and after all four (702
    tests, OK, on 3.10.12). Each mutation was confirmed present before its
    result was read, and each was applied to a restored copy rather than on top
    of the last.

    1. **A track edits the registry and the page's quotation goes stale.** The
       `tolerance_note`'s "fails on a majority of the population it checks"
       reworded to "fails on most of the population it checks" -- a change no
       reviewer of `metadata/sources.json` would think twice about. Kills
       `test_every_quoted_registry_claim_is_still_in_the_registry`,
       `AssertionError`, naming the entry and the document. This is the failure
       the guard exists for, in the direction it actually runs.
    2. **The page stops publishing the sentence.** "The `tolerance_note` records
       the outcome" reworded to "The registry note records the outcome". Kills
       `test_every_declared_quotation_is_still_published`, `AssertionError`. The
       reverse direction: a declaration left behind by the document it describes
       would otherwise pass by absence.

    Two mutations survived, and only one of them was expected to.

    3. **The `QUOTATIONS` entry dropped entirely.** Kills nothing: both
       assertions iterate the table, so an empty table satisfies both. Expected,
       and it is the same hole this repository closed one file away at
       `2ced98e`, where dropping a `CLI_PUBLICATION` entry was quieter than
       lying in one. **It cannot be closed the same way here.** That guard could
       assert its registry against `cli.build_parser()`, an enumerable universe
       of commands; there is no enumerable universe of quotations in a Markdown
       page, so nothing can say this table is complete. The table is a
       declaration, and its completeness rests on whoever adds a quotation
       adding a row. Recorded as the standing limit of this guard rather than
       left to be rediscovered.
    4. **`_collapsed` replaced with the identity function.** Kills nothing, and
       this one was expected to kill. Its docstring says it exists so a
       hard-wrapped quotation matches a JSON string -- but the only entry in the
       table today is a single-line implicit concatenation, the registry value
       it is compared against is a single-line JSON string, and the document
       side goes through `_line_stating`, which does its own word-stream
       matching. So the helper is defensive against a registry value containing
       a newline and **no current input exercises it**. Not wrong; unexercised,
       which in this repository is a thing worth saying out loud rather than a
       thing to leave looking tested.
    """

    def test_every_quoted_registry_claim_is_still_in_the_registry(self):
        wrong = []
        for name, document, _published, quoted, field in QUOTATIONS:
            if _collapsed(quoted) not in _collapsed(field()):
                wrong.append(f"{name}: {document} attributes to the registry: {quoted!r}")
        self.assertEqual(
            [],
            wrong,
            "A published document quotes the registry saying something the "
            "registry does not say:\n  " + "\n  ".join(wrong),
        )

    def test_every_declared_quotation_is_still_published(self):
        missing = []
        for name, document, published, _quoted, _field in QUOTATIONS:
            path = REPO_ROOT / document
            if _line_stating(path, published) is None:
                missing.append(f"{name}: {document} no longer states it")
        self.assertEqual(
            [],
            missing,
            "A quotation is declared here that its document no longer "
            "publishes; remove the declaration deliberately rather than "
            "leaving it to pass by absence:\n  " + "\n  ".join(missing),
        )
