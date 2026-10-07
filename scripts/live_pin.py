"""The live record's code pin: a registered literal in `metadata/live_pin.json` (#255).

The pin was `PINNED_CODE_SHA = None`, resolved at run time by main's own
`resolve_pin`, which ran with a write token on an unprotected branch. A change
on main could repoint the commit that records the forecast without the dated
version bump the record promises, and no test enforced the policy (review
findings 2 and 6, 6 October 2026).

`metadata/live_pin.json` replaces it:

    {"version": 1, "current": SHA, "transitions": [{"id", "sha", "record"}, ...],
     "environment": {"runner", "python", "lock", "lock_sha256"}}

`current` is the last transition's `sha`. Each transition is one registered
pin: its `record` is a decision record in `docs/decisions/` that names the SHA,
and the SHA is an ancestor of main. The workflow reads `current` with `jq` and
checks that commit out before any repository Python runs; `verify` re-checks
the whole registry afterwards; and `live_score.py` refuses a record whose
`code.pinned_sha` is not a registered transition (`require_registered`).

`environment` fixes what the pinned code runs on: the runner image, the Python
patch release, and a lock file of every resolved package with its hashes, whose
SHA-256 the manifest holds. The workflow installs only from that lock
(`--require-hashes --no-deps`), and each record carries the environment it ran
in (`environment_block`), which must be exactly the lock's packages.

Changing the manifest changes which commit records the live forecast, so it is
an owner-attested change (`scripts/owner_attested.py`, kind `live-pin`, #256):
a pull request that edits it cites Eleonora's own `GO #N` comment in
`metadata/owner_attestations.json`, and CI checks that. Every check here is a
data guard and raises `ValueError`.

    python3 scripts/live_pin.py current [--manifest FILE]
    python3 scripts/live_pin.py verify [--manifest FILE] [--repo DIR] [--ref REF]

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "metadata" / "live_pin.json"
TOP_KEYS = {"version", "current", "transitions", "environment"}
ENVIRONMENT_KEYS = {"runner", "python", "lock", "lock_sha256"}
TRANSITION_KEYS = {"id", "sha", "record"}
SHA = re.compile(r"^[0-9a-f]{40}$")


def load_manifest(path: Path = MANIFEST) -> dict:
    """The manifest at `path`, shape-checked."""

    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    check_shape(manifest)
    return manifest


def check_shape(manifest) -> None:
    """Raises `ValueError` unless the manifest has the documented shape."""

    if not isinstance(manifest, dict) or set(manifest) != TOP_KEYS:
        raise ValueError(f"the live pin manifest holds exactly {sorted(TOP_KEYS)}")
    if manifest["version"] != 1:
        raise ValueError("the live pin manifest's version must be 1")
    transitions = manifest["transitions"]
    if not isinstance(transitions, list) or not transitions:
        raise ValueError("the live pin manifest needs at least one transition")
    seen = set()
    for transition in transitions:
        if not isinstance(transition, dict) or set(transition) != TRANSITION_KEYS:
            raise ValueError(f"each transition holds exactly {sorted(TRANSITION_KEYS)}")
        if not isinstance(transition["sha"], str) or not SHA.match(transition["sha"]):
            raise ValueError(f"transition {transition['id']!r}: sha must be 40 lowercase hex digits")
        if not isinstance(transition["id"], str) or not transition["id"] or transition["id"] in seen:
            raise ValueError(f"transition ids must be distinct non-empty strings: {transition['id']!r}")
        seen.add(transition["id"])
    if manifest["current"] != transitions[-1]["sha"]:
        raise ValueError("current must be the last transition's sha")
    _check_environment_shape(manifest["environment"])


def _check_environment_shape(env) -> None:
    if not isinstance(env, dict) or set(env) != ENVIRONMENT_KEYS:
        raise ValueError(f"environment holds exactly {sorted(ENVIRONMENT_KEYS)}")
    if not isinstance(env["runner"], str) or not re.match(r"^ubuntu-\d\d\.\d\d$", env["runner"]):
        raise ValueError("environment.runner must name one runner image, such as ubuntu-24.04, never a moving label")
    if not isinstance(env["python"], str) or not re.match(r"^3\.11\.\d+$", env["python"]):
        raise ValueError("environment.python must be an exact 3.11 patch release")
    if not isinstance(env["lock"], str) or not re.match(r"^metadata/[\w.-]+$", env["lock"]):
        raise ValueError("environment.lock must be a file in metadata/")
    if not isinstance(env["lock_sha256"], str) or not re.match(r"^[0-9a-f]{64}$", env["lock_sha256"]):
        raise ValueError("environment.lock_sha256 must be 64 lowercase hex digits")


def parse_lock(text: str) -> dict:
    """The lock's packages, `{name: version}`. Every requirement is `name==version` with at least one hash.

    Raises:
        ValueError: a requirement that is not an exact version, or has no hash.
    """

    packages = {}
    for block in re.split(r"\n(?=\S)", text.strip()):
        head = block.split("\\")[0].strip()
        if not block.strip() or block.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)==([A-Za-z0-9_.!+-]+)$", head)
        if not match:
            raise ValueError(f"lock requirement {head!r} is not an exact name==version")
        if "--hash=sha256:" not in block:
            raise ValueError(f"lock requirement {head!r} carries no hash")
        packages[match.group(1).lower()] = match.group(2)
    if not packages:
        raise ValueError("the lock names no package")
    return packages


def verify_environment(manifest: dict, repo: Path = REPO) -> dict:
    """The lock file is the one the manifest names, byte for byte, and is fully hashed. Returns its packages."""

    check_shape(manifest)
    env = manifest["environment"]
    raw = (Path(repo) / env["lock"]).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != env["lock_sha256"]:
        raise ValueError(f"{env['lock']} is not the lock the manifest names: sha256 {digest}")
    return parse_lock(raw.decode("utf-8"))


def environment_block(manifest: dict, lock_text: str, freeze_text: str, python: str) -> dict:
    """What a record carries as `environment`: the runner, the Python patch, the lock's digest and the packages.

    The installed packages (`pip freeze`) must be exactly the lock's, and the
    interpreter must be the manifest's patch release.

    Raises:
        ValueError: an installed environment that is not the locked one.
    """

    env = manifest["environment"]
    locked = parse_lock(lock_text)
    if hashlib.sha256(lock_text.encode("utf-8")).hexdigest() != env["lock_sha256"]:
        raise ValueError("environment: the lock is not the one the manifest names")
    installed = {}
    for line in freeze_text.splitlines():
        if line.strip():
            name, _, version = line.strip().partition("==")
            installed[name.lower()] = version
    if installed != locked:
        raise ValueError(f"environment: installed packages differ from the lock: {sorted(set(installed.items()) ^ set(locked.items()))}")
    if python != env["python"]:
        raise ValueError(f"environment: Python {python} is not the pinned {env['python']}")
    return {
        "runner": env["runner"],
        "python": python,
        "lock_sha256": env["lock_sha256"],
        "packages": dict(sorted(locked.items())),
    }


def registered(manifest: dict) -> set:
    """The SHAs of every registered transition."""

    return {transition["sha"] for transition in manifest["transitions"]}


def require_registered(sha, manifest: dict) -> None:
    """Raises `ValueError` unless `sha` is a registered transition's full SHA."""

    if sha not in registered(manifest):
        raise ValueError(f"code.pinned_sha {sha!r} is not a registered live pin transition")


def _is_ancestor(repo: Path, sha: str, ref: str) -> bool:
    done = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, ref],
        capture_output=True, text=True,
    )
    return done.returncode == 0


def verify_manifest(manifest: dict, repo: Path = REPO, ref: str = "origin/main") -> None:
    """Every transition's SHA is an ancestor of `ref` and is named in the decision record it cites."""

    check_shape(manifest)
    repo = Path(repo)
    for transition in manifest["transitions"]:
        sha, record = transition["sha"], transition["record"]
        path = (repo / record).resolve()
        decisions = (repo / "docs" / "decisions").resolve()
        if decisions not in path.parents or path.suffix != ".md":
            raise ValueError(f"transition {transition['id']!r}: {record} is not a record in docs/decisions/")
        if not path.is_file():
            raise ValueError(f"transition {transition['id']!r}: {record} does not exist")
        if sha not in path.read_text(encoding="utf-8"):
            raise ValueError(f"transition {transition['id']!r}: {record} names no such sha {sha}")
        if not _is_ancestor(repo, sha, ref):
            raise ValueError(f"transition {transition['id']!r}: {sha} is not an ancestor of {ref}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("current", "verify", "environment"):
        command = sub.add_parser(name)
        command.add_argument("--manifest", type=Path, default=MANIFEST)
        if name in ("verify", "environment"):
            command.add_argument("--repo", type=Path, default=REPO)
        if name == "verify":
            command.add_argument("--ref", default="origin/main")
        if name == "environment":
            command.add_argument("--freeze", type=Path, required=True, help="`pip freeze` of the installed environment")
            command.add_argument("--python", required=True, help="the interpreter's patch release")
    args = parser.parse_args(argv)
    manifest = load_manifest(args.manifest)
    if args.command == "current":
        print(manifest["current"])
    elif args.command == "verify":
        verify_manifest(manifest, args.repo, args.ref)
        verify_environment(manifest, args.repo)
        print(json.dumps({"verified": [t["id"] for t in manifest["transitions"]]}))
    else:
        lock = (args.repo / manifest["environment"]["lock"]).read_text(encoding="utf-8")
        block = environment_block(manifest, lock, args.freeze.read_text(encoding="utf-8"), args.python)
        print(json.dumps(block, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
