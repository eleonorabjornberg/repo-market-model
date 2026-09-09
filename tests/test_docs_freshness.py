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
import pathlib
import re
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

# Present only in the author's checkout, via .git/info/exclude: the stop-work
# pointers that halt an agent opened in the integration folder. A fresh clone
# does not contain them, so seeing them here is a local artifact, not a document.
LOCAL_ONLY = ("CLAUDE.md", "AGENTS.md")

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


def published_markdown():
    """Every Markdown file a clone of this repository would contain."""
    found = []
    for path in sorted(REPO_ROOT.rglob("*.md")):
        relative = path.relative_to(REPO_ROOT).as_posix()
        if relative.startswith(".git/") or "/.git/" in f"/{relative}":
            continue
        if relative.startswith(EXCLUDED_PREFIXES):
            continue
        if relative in LOCAL_ONLY:
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


# A published invocation of this package's command line. The marker is the module
# path rather than the subcommand names: a subcommand this guard has not heard of
# is exactly the one most likely to have been published and then renamed.
CLI_MARKER = "repo_model.cli"

FENCE = re.compile(r"^\s*```")
INLINE_CODE = re.compile(r"`([^`]+)`")

# A leading environment assignment, not an argument: PYTHONPATH=src, and so on.
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

# A value the shell would compute. Such a command cannot be parsed as written,
# because a type converter would receive the literal text of the substitution.
SUBSTITUTION = re.compile(r"\$\(|\$\{|\$[A-Za-z_]|`")


class Unlexable(str):
    """A command the shell itself could not read, carrying the lexer's complaint.

    Not a skip. An unbalanced quote or a dangling continuation is a defect in the
    published text, and it is also what a dropped continuation join looks like
    from in here -- so it is reported as an offence naming the document, rather
    than raising a traceback out of the extractor.
    """


def _argv(command):
    """The arguments `repo_model.cli` would receive.

    Returns a token list; `None` for a command *skipped* because it contains a
    shell substitution, which is a different outcome from parsing and is kept
    distinguishable all the way up to the assertion -- substituting a value here
    would check a command nobody published; or `Unlexable` if the shell lexer
    refused the text.
    """
    if SUBSTITUTION.search(command):
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
                if CLI_MARKER not in candidate:
                    continue
                command = candidate.strip()
                found.append((relative, command, _argv(command)))
    return found


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
            "on the page was skipped for a shell substitution."
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
       **both** tests: the interpreter assertion, `AssertionError: '3.10' not found in
       '~=3.12.0'`, and the agreement assertion, which then named both documents at
       once. That is the shape to expect -- moving the single declaration moves what
       every document is checked against, which is the point of there being one.
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
                    if version not in requirement:
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
        self.assertIn(
            running,
            requirement,
            f"This suite is running on Python {running}, which "
            f"requires-python = {requirement!r} does not admit. Either the project "
            f"supports it and the declaration is stale, or it does not and this run "
            f"proves nothing.",
        )


if __name__ == "__main__":
    unittest.main()
