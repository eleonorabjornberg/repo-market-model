"""The live record's integrity (#254): hash chain, add-only commits and digest checks.

An independent review of 6 October 2026 (review finding 1, #254) found that
the live record's controls did not establish the immutability
`.github/workflows/live-log.yml` claims. Ruleset 24422476 forbids deleting
`live-log` and pushing to it non-fast-forward, but a fast-forward commit could
still change or delete an existing `live/YYYY-MM-DD.json`. Nothing checked the
files against their #225 digests either. This script adds the checks the
directive asks for. Each one raises `ValueError`:

* **The hash chain.** From the first record after #254 merges, each record
  carries `chain`: `prev_date`, `prev_sha256` (the SHA-256 of the previous
  record file's bytes) and `prev_commit` (the live-log commit that added that
  file). The first chained record points at the last unchained one. Files
  logged before then, 2026-10-05 among them, are never edited: their #225
  digests and their commits cover them. `add_chain` inserts the block into the
  day's new file, before it is committed. The file is written by the pinned
  code (`live_record.py pin`), so the forecasting code and its pin do not
  change. Every other byte stays as the pinned code serialised it.
* **The add-only commit.** Before the workflow pushes, `require_append_only`
  checks the one new commit on top of `origin/live-log`. It must only add
  `live/<today>.json`, be authored and committed as `github-actions[bot]`, and
  change no other path.
* **Verification.** `verify` re-checks the whole branch. Every commit only
  adds one dated file, as the bot. Every file's SHA-256 equals its #225 digest,
  and the digest names the commit that added the file. The chain is unbroken.
  The workflow runs it every day, and `live_score.py` runs it before it scores
  anything.

The author check guards against a mistake, not an adversary. Anyone holding
the repository token can set any author name. That is why the digests also
need an anchor outside the repository, which is Eleonora's decision (#254, Do 4).

    python3 scripts/live_integrity.py chain --live-dir LIVE_LOG --date YYYY-MM-DD
    python3 scripts/live_integrity.py check-append --live-dir LIVE_LOG --date YYYY-MM-DD --base SHA|none
    python3 scripts/live_integrity.py verify --live-dir LIVE_LOG --digests DIGESTS.jsonl

`--digests` takes the #225 comments, one JSON object per line, each with
`author` (the commenter's login) and `body`. This module is stdlib only and
imports nothing from the repository. The workflow runs it from main with the
runner's Python, before the pinned code's environment is needed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
#: The comment author whose #225 comments are digests.
DIGEST_AUTHOR = "github-actions[bot]"
CHAIN_KEYS = ("prev_date", "prev_sha256", "prev_commit")
FILE_PATTERN = re.compile(r"^live/(\d{4}-\d{2}-\d{2})\.json$")
#: git's empty tree, the parent a root commit is compared against.
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

_DIGEST_HEAD = re.compile(r"^(\d{4}-\d{2}-\d{2}): `live/(\d{4}-\d{2}-\d{2})\.json`")
_DIGEST_SHA = re.compile(r"^- SHA-256: `([0-9a-f]{64})`$", re.M)
_DIGEST_COMMIT = re.compile(r"^- commit on live-log: ([0-9a-f]{40})$", re.M)


def record_bytes(record) -> bytes:
    """A record's bytes, serialised exactly as `live_record.record_bytes` does."""

    return (json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git(repo: Path, *argv) -> str:
    done = subprocess.run(["git", *argv], cwd=repo, capture_output=True, text=True)
    if done.returncode != 0:
        raise ValueError(f"git {' '.join(argv)} failed in {repo}: {done.stderr.strip()}")
    return done.stdout.strip()


def _has_commits(repo: Path) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=repo, capture_output=True
    ).returncode == 0


def _day_of(rel: str) -> date:
    match = FILE_PATTERN.match(rel)
    if not match:
        raise ValueError(f"{rel} is not a live record path (live/YYYY-MM-DD.json)")
    return date.fromisoformat(match.group(1))


def require_add_only_commit(repo: Path, commit: str, expected: str | None = None) -> date:
    """`commit` adds exactly one live record file, as the bot, and changes nothing else.

    Returns the day it adds. `expected`, if given, is the only path it may add.

    Raises:
        ValueError: a merge, another author or committer, or any change other
            than adding one `live/YYYY-MM-DD.json`.
    """

    fields = _git(repo, "show", "-s", "--format=%an%n%ae%n%cn%n%ce%n%P", commit).split("\n")
    identity, parents = fields[:4], " ".join(fields[4:]).split()
    if len(parents) > 1:
        raise ValueError(f"{commit} is a merge: the live record is written by add-only commits")
    if identity != [BOT_NAME, BOT_EMAIL, BOT_NAME, BOT_EMAIL]:
        raise ValueError(f"{commit} was not authored and committed by {BOT_NAME}: {identity}")
    parent = parents[0] if parents else EMPTY_TREE
    lines = _git(repo, "diff", "--no-renames", "--name-status", parent, commit).splitlines()
    changes = [tuple(line.split("\t", 1)) for line in lines if line]
    if expected is None and len(changes) == 1 and changes[0][0] == "A":
        expected = changes[0][1]
    if changes != [("A", expected)]:
        raise ValueError(f"{commit} must only add {expected or 'one live record file'}; it changes {changes}")
    return _day_of(expected)


def require_append_only(repo: Path, base: str | None, day: date) -> None:
    """HEAD is one commit on top of `base` (`None`: a new branch) that only adds `live/<day>.json`.

    The workflow runs this after its commit and before `git push`.

    Raises:
        ValueError: more than one new commit, or a commit that does anything
            but add the day's file, as the bot.
    """

    head = _git(repo, "rev-parse", "HEAD")
    parents = _git(repo, "show", "-s", "--format=%P", head).split()
    if parents != ([base] if base else []):
        raise ValueError(f"HEAD must be one commit on top of {base or 'nothing'}; its parents are {parents}")
    require_add_only_commit(repo, head, f"live/{day.isoformat()}.json")


def logged_files(repo: Path) -> list:
    """The committed record files, oldest day first, as (day, path relative to the repo)."""

    if not _has_commits(repo):
        return []
    paths = _git(repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    return sorted((_day_of(rel), rel) for rel in paths if rel)


def adding_commit(repo: Path, rel: str) -> str:
    """The one commit that touched `rel`: the one that added it."""

    commits = _git(repo, "log", "--format=%H", "--", rel).splitlines()
    if len(commits) != 1:
        raise ValueError(f"{rel} was touched by {len(commits)} commits; a record is only added, once")
    return commits[0]


def chain_for(repo: Path, day: date):
    """The chain block for `day`'s record: the latest committed record before it, or `None`."""

    earlier = [(d, rel) for d, rel in logged_files(repo) if d < day]
    if not earlier:
        return None
    prev_day, rel = earlier[-1]
    return {
        "prev_date": prev_day.isoformat(),
        "prev_sha256": file_sha256(Path(repo) / rel),
        "prev_commit": adding_commit(repo, rel),
    }


def add_chain(repo: Path, day: date) -> Path:
    """Insert the chain block into `day`'s new, uncommitted record file.

    Raises:
        ValueError: the file is missing, already committed, already chained,
            or not serialised as the pinned code serialises a record.
    """

    rel = f"live/{day.isoformat()}.json"
    path = Path(repo) / rel
    if not path.is_file():
        raise ValueError(f"{path} does not exist")
    if _has_commits(repo) and subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{rel}"], cwd=repo, capture_output=True
    ).returncode == 0:
        raise ValueError(f"{rel} is already committed: a logged file is never edited")
    raw = path.read_bytes()
    record = json.loads(raw)
    if "chain" in record:
        raise ValueError(f"{rel} is already chained")
    if record_bytes(record) != raw:
        raise ValueError(f"{rel} is not serialised as a record: refusing to rewrite it")
    chain = chain_for(repo, day)
    if chain is None:
        return path
    record["chain"] = chain
    path.write_bytes(record_bytes(record))
    return path


def require_chain(repo: Path, files) -> None:
    """Every chained record points at its predecessor's date, bytes and adding commit.

    Records before the first chained one are unchained (logged before #254).
    An unchained record after it is refused.
    """

    begun = False
    for index, (day, rel) in enumerate(files):
        record = json.loads((Path(repo) / rel).read_text(encoding="utf-8"))
        chain = record.get("chain")
        if chain is None:
            if begun:
                raise ValueError(f"{rel} carries no chain, but the chain began before it")
            continue
        begun = True
        if index == 0:
            raise ValueError(f"{rel} is chained to a record the log does not hold")
        prev_day, prev_rel = files[index - 1]
        expected = {
            "prev_date": prev_day.isoformat(),
            "prev_sha256": file_sha256(Path(repo) / prev_rel),
            "prev_commit": adding_commit(repo, prev_rel),
        }
        if chain != expected:
            raise ValueError(f"{rel}'s chain does not match {prev_rel}: {chain} != {expected}")


def parse_digests(path) -> dict:
    """The #225 digests, by day: {"sha256", "commit"}. Only the bot's comments count.

    Raises:
        ValueError: a bot comment that opens like a digest but lacks its fields,
            or two different digests for one day.
    """

    text = Path(path).read_text(encoding="utf-8").strip()
    if text.startswith("["):
        comments = json.loads(text)
    else:
        comments = [json.loads(line) for line in text.splitlines() if line.strip()]
    digests = {}
    for comment in comments:
        if comment.get("author") != DIGEST_AUTHOR:
            continue
        body = comment.get("body") or ""
        head = _DIGEST_HEAD.match(body)
        if not head:
            continue
        if head.group(1) != head.group(2):
            raise ValueError(f"a digest names two days: {body.splitlines()[0]}")
        sha = _DIGEST_SHA.search(body)
        commit = _DIGEST_COMMIT.search(body)
        if not sha or not commit:
            raise ValueError(f"the digest for {head.group(1)} lacks its SHA-256 or its commit")
        day = date.fromisoformat(head.group(1))
        entry = {"sha256": sha.group(1), "commit": commit.group(1)}
        if digests.get(day, entry) != entry:
            raise ValueError(f"two different digests for {day}")
        digests[day] = entry
    return digests


def verify(repo: Path, digests: dict) -> list:
    """Check the whole live log. Returns the logged days, oldest first.

    Raises:
        ValueError: an uncommitted change; a commit that is not add-only by the
            bot; a file whose SHA-256 or adding commit differs from its digest;
            a file with no digest, or a digest with no file; a broken chain.
    """

    repo = Path(repo)
    if _has_commits(repo):
        if _git(repo, "status", "--porcelain", "--untracked-files=all"):
            raise ValueError(f"{repo} has uncommitted changes: verify a clean checkout")
        for commit in _git(repo, "rev-list", "HEAD").splitlines():
            require_add_only_commit(repo, commit)
    files = logged_files(repo)
    for day, rel in files:
        digest = digests.get(day)
        if digest is None:
            raise ValueError(f"{rel} has no digest on #225")
        digest_of = file_sha256(repo / rel)
        if digest["sha256"] != digest_of:
            raise ValueError(f"{rel}'s SHA-256 {digest_of} differs from its digest {digest['sha256']}")
        if digest["commit"] != adding_commit(repo, rel):
            raise ValueError(f"{rel}'s digest names commit {digest['commit']}, not the one that added it")
    missing = sorted(set(digests) - {day for day, _ in files})
    if missing:
        raise ValueError(f"days digested on #225 with no file in the log: {[d.isoformat() for d in missing]}")
    require_chain(repo, files)
    return [day for day, _ in files]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    chain = sub.add_parser("chain", help="insert the chain block into the day's new record")
    chain.add_argument("--live-dir", required=True, type=Path)
    chain.add_argument("--date", required=True)
    check = sub.add_parser("check-append", help="the new commit only adds the day's record")
    check.add_argument("--live-dir", required=True, type=Path)
    check.add_argument("--date", required=True)
    check.add_argument("--base", required=True, help="origin/live-log's SHA, or 'none' for a new branch")
    every = sub.add_parser("verify", help="check every logged file, commit, digest and link")
    every.add_argument("--live-dir", required=True, type=Path)
    every.add_argument("--digests", required=True, type=Path)
    args = parser.parse_args(argv)
    day = date.fromisoformat(args.date) if getattr(args, "date", None) else None
    if args.command == "chain":
        path = add_chain(args.live_dir, day)
        record = json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps({"file": str(path), "chain": record.get("chain")}))
    elif args.command == "check-append":
        require_append_only(args.live_dir, None if args.base == "none" else args.base, day)
        print(json.dumps({"append_only": f"live/{day.isoformat()}.json"}))
    else:
        days = verify(args.live_dir, parse_digests(args.digests))
        print(json.dumps({"verified": [d.isoformat() for d in days]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
