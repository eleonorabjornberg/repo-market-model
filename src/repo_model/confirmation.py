"""The 2026 confirmation window, pre-registered: the three frozen candidates and the guard that holds them (#585).

`metadata/confirmation_preregistration.json` is the pre-registration and
`docs/decisions/confirmation-preregistration.md` the decision record that goes with it. The file freezes, for each
of the three candidates Eleonora froze on 11 October 2026 (ruling on #567), the hash of every file it is scored
under, and, for the judge, the hash of its declaration (with the one field Eleonora's opening edits left out), of
its code and of the weighted-miss declaration. `verify` recomputes them from the tree.

**Nothing here scores a day.** `require_confirmation_open` is the guard a later scoring script calls with the days
it is about to score, before any model is fitted. It raises `LookAheadError` for a day outside the window, for a
day of a lockbox tier that has not been opened (`docs/decisions/lockbox.md`), for a candidate the judge's
`confirmation.candidates` does not name, and for a frozen file that no longer matches its hash. Naming the three in
`confirmation.candidates` of `metadata/pressure_judge.json` is the opening; it is Eleonora's own attested action
(#256), and no argument, flag or environment variable here stands in for it. The guard reads the tracked files at
call time, as `lockbox.require_unlocked` does.

The near-blind tier (2026-01-01 to 2026-09-03) was opened once for the final test (#151), so `metadata/lockbox.json`
no longer locks the window; the judge's `confirmation.candidates` is the gate that does.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from . import lockbox
from .data import DataContractError
from .splits import LookAheadError


__all__ = [
    "DEFAULT_PREREGISTRATION",
    "JUDGE_DECLARATION",
    "digest_file",
    "frozen_paths",
    "judge_declaration_digest",
    "load_preregistration",
    "require_confirmation_open",
    "verify",
]


#: The repository root; tests point it at a scratch copy, as they do `lockbox.DEFAULT_LOCKBOX`.
REPO = Path(__file__).parents[2]
DEFAULT_PREREGISTRATION = "metadata/confirmation_preregistration.json"
JUDGE_DECLARATION = "metadata/pressure_judge.json"


def digest_file(path: Path) -> str:
    """The sha256 of a file's bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def judge_declaration_digest(document: dict) -> str:
    """The sha256 of the judge's declaration with `confirmation.candidates` emptied.

    The opening is naming the frozen candidates in that one list, so the list is the one thing the freeze cannot
    cover; everything else in the declaration is.
    """

    frozen = copy.deepcopy(document)
    frozen["confirmation"]["candidates"] = []
    text = json.dumps(frozen, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_preregistration(root: Optional[Path] = None) -> dict:
    """Load the pre-registration under `root` (the repository by default).

    Raises:
        DataContractError: if the file is missing or malformed.
    """

    root = REPO if root is None else root
    path = root / DEFAULT_PREREGISTRATION
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataContractError(f"cannot load the confirmation pre-registration: {exc}") from exc
    for key in ("window", "judge", "candidates", "panel", "frozen_at"):
        if key not in document:
            raise DataContractError(f"the confirmation pre-registration has no {key!r}")
    return document


def _hashed_files(document: dict) -> Dict[str, str]:
    files: Dict[str, str] = {}
    files.update(document["judge"]["files"])
    for entry in document["candidates"]:
        files.update(entry["files"])
    return files


def frozen_paths(root: Optional[Path] = None) -> List[str]:
    """Every path the pre-registration reads, sorted: the hashed files, the judge's declaration, the manifest."""

    document = load_preregistration(root)
    paths = set(_hashed_files(document))
    paths.add(document["judge"]["declaration"]["path"])
    paths.add(document["panel"]["manifest"])
    paths.add(DEFAULT_PREREGISTRATION)
    return sorted(paths)


def verify(root: Optional[Path] = None) -> List[str]:
    """Recompute every frozen hash under `root`; return one line per mismatch or missing file (empty when frozen).

    The pre-registration itself is read from `root` too, so a scratch copy is checked against its own file.
    """

    root = REPO if root is None else root
    document = load_preregistration(root)
    problems: List[str] = []
    for path, expected in sorted(_hashed_files(document).items()):
        target = root / path
        if not target.is_file():
            problems.append(f"{path}: missing")
        elif digest_file(target) != expected:
            problems.append(f"{path}: sha256 differs from the pre-registration")
    judge = document["judge"]["declaration"]
    target = root / judge["path"]
    try:
        actual = judge_declaration_digest(json.loads(target.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError) as exc:
        problems.append(f"{judge['path']}: cannot be read ({exc})")
    else:
        if actual != judge["sha256"]:
            problems.append(f"{judge['path']}: digest (confirmation.candidates left out) differs from the pre-registration")
    manifest = document["panel"]
    target = root / manifest["manifest"]
    try:
        actual = json.loads(target.read_text(encoding="utf-8"))["sha256"]
    except (OSError, ValueError, KeyError) as exc:
        problems.append(f"{manifest['manifest']}: cannot be read ({exc})")
    else:
        if actual != manifest["sha256"]:
            problems.append(f"{manifest['manifest']}: panel digest differs from the pre-registration")
    return problems


def require_confirmation_open(candidate: str, scored_days: Iterable[date], *, where: str) -> None:
    """Refuse to score `scored_days` for `candidate` unless the confirmation look is open and the freeze holds.

    `where` names the entry point, for the message.

    Raises:
        ValueError: if `candidate` is not one of the frozen candidates.
        LookAheadError: for a day in a lockbox tier that has not been opened, for a day outside the window, if the
            judge's `confirmation.candidates` does not name `candidate`, or if a frozen file differs from its hash.
        DataContractError: if the pre-registration or the judge's declaration is missing or malformed.
    """

    days = sorted(scored_days)
    document = load_preregistration()
    if candidate not in [entry["name"] for entry in document["candidates"]]:
        raise ValueError(f"{where}: {candidate!r} is not one of the frozen confirmation candidates")
    lockbox.require_unlocked(days, where=where)
    first = date.fromisoformat(document["window"]["first"])
    last = date.fromisoformat(document["window"]["last"])
    for day in days:
        if not first <= day <= last:
            raise LookAheadError(
                f"{where}: scored day {day} is outside the pre-registered confirmation window {first} to {last}"
            )
    try:
        judge = json.loads((REPO / JUDGE_DECLARATION).read_text(encoding="utf-8"))
        named = judge["confirmation"]["candidates"]
    except (OSError, ValueError, KeyError) as exc:
        raise DataContractError(f"{where}: cannot read confirmation.candidates of {JUDGE_DECLARATION}: {exc}") from exc
    if candidate not in named:
        raise LookAheadError(
            f"{where}: {candidate!r} is not in confirmation.candidates of {JUDGE_DECLARATION}; the look is not open "
            f"for it (opening is Eleonora's own attested action, #256)"
        )
    problems = verify(root=REPO)
    if problems:
        raise LookAheadError(
            f"{where}: the frozen declaration no longer matches the pre-registration: " + "; ".join(problems)
        )
