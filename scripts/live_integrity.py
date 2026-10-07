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

* **The panel** (#275). Each record's commit also adds `live/<day>.panel.csv`, the
  panel the day's run built. The record names it (`inputs.panel_sha256`), so its
  digest on #225 and its Rekor anchor cover the panel through that field.
  `check-append --panel` refuses a record's commit without it, and `verify`
  refuses a panel that is not the one its record names, or was not added in its
  record's commit. Days logged before #275 have none, and that passes.

* **The anchor** (Eleonora's ruling of 6 October 2026: Sigstore Rekor). After
  each day's record is pushed, the workflow signs the file's SHA-256 keylessly
  (cosign, under the workflow's GitHub OIDC identity) into the public Rekor
  log, and adds `live/<day>.rekor` in a second add-only commit: the Rekor log
  index, the entry UUID and the entry itself, with its inclusion proof.
  `verify` checks every such file offline (`verify_entry`): the entry is a
  `hashedrekord` over the file's SHA-256, its inclusion proof rebuilds the
  stated root, and its signing certificate names this repository's
  `live-log.yml` on `main` and GitHub's OIDC issuer. A missing anchor never
  blocks a record or fails `verify`; a later run anchors the day (`unanchored`).
  What the offline check does not do (the Fulcio chain, the entry's signature,
  the log's signed tree head) is cosign's, online: see `ONLINE_COMMAND`.

The author check guards against a mistake, not an adversary. Anyone holding
the repository token can set any author name. The anchor is the control the
token cannot touch: the entry sits in Rekor's public log.

    python3 scripts/live_integrity.py chain --live-dir LIVE_LOG --date YYYY-MM-DD
    python3 scripts/live_integrity.py environment --live-dir LIVE_LOG --date YYYY-MM-DD --block BLOCK.json
    python3 scripts/live_integrity.py check-append --live-dir LIVE_LOG --date YYYY-MM-DD --base SHA|none [--panel]
    python3 scripts/live_integrity.py verify --live-dir LIVE_LOG --digests DIGESTS.jsonl
    python3 scripts/live_integrity.py reconcile --live-dir LIVE_LOG --digests DIGESTS.jsonl --out-dir OUT [--run-url URL]
    python3 scripts/live_integrity.py unanchored --live-dir LIVE_LOG
    python3 scripts/live_integrity.py anchor-file --live-dir LIVE_LOG --date YYYY-MM-DD --entries ENTRIES.json

`--digests` takes the #225 comments, one JSON object per line, each with
`author` (the commenter's login) and `body`. This module is stdlib only and
imports nothing from the repository. The workflow runs it from main with the
runner's Python, before the pinned code's environment is needed.
"""

from __future__ import annotations

import argparse
import base64
import binascii
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
#: The anchor file. Not `.json`, so no reader of `live/*.json` mistakes it for a record.
ANCHOR_PATTERN = re.compile(r"^live/(\d{4}-\d{2}-\d{2})\.rekor$")
#: The only identity whose Rekor entry anchors a day: this repository's workflow, on main.
#: The day's panel, committed in the record's own commit (#275). Not `.json`, for the same reason.
PANEL_PATTERN = re.compile(r"^live/(\d{4}-\d{2}-\d{2})\.panel\.csv$")

IDENTITY = "https://github.com/eleonorabjornberg/repo-market-model/.github/workflows/live-log.yml@refs/heads/main"
OIDC_ISSUER = "https://token.actions.githubusercontent.com"
#: Fulcio's certificate extension for the OIDC issuer (v1: the raw string; v2: a DER UTF8String).
_ISSUER_OIDS = ("1.3.6.1.4.1.57264.1.1", "1.3.6.1.4.1.57264.1.8")
#: The online check, for a day D (cosign checks the Fulcio chain, the signature and the tree head):
ONLINE_COMMAND = f"""\
uuid=$(jq -r .uuid live/D.rekor)
curl -fsS https://rekor.sigstore.dev/api/v1/log/entries/$uuid | jq -r '.[].body' | base64 -d > body.json
jq -r .spec.signature.publicKey.content body.json | base64 -d > cert.pem
jq -r .spec.signature.content body.json | base64 -d > sig.bin
cosign verify-blob --certificate cert.pem --signature sig.bin \\
  --certificate-identity '{IDENTITY}' \\
  --certificate-oidc-issuer {OIDC_ISSUER} live/D.json"""
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
    match = FILE_PATTERN.match(rel) or ANCHOR_PATTERN.match(rel) or PANEL_PATTERN.match(rel)
    if not match:
        raise ValueError(
            f"{rel} is not a live record path (live/YYYY-MM-DD.json, .panel.csv or .rekor)"
        )
    return date.fromisoformat(match.group(1))


def require_add_only_commit(
    repo: Path, commit: str, expected: str | None = None, require_panel: bool = False
) -> date:
    """`commit` adds one live record (and its panel) or one anchor file, as the bot, and changes nothing else.

    Returns the day it adds. `expected`, if given, is the record or anchor path
    it must add. A record's commit may also add that day's `live/YYYY-MM-DD.panel.csv`
    (#275), and must with `require_panel`. An anchor may only follow its day's record.

    Raises:
        ValueError: a merge, another author or committer, any change other
            than adding one `live/YYYY-MM-DD.json` (with its panel) or `.rekor`,
            a panel on its own, a missing panel when one is required, or an
            anchor for a day whose record is not already in the log.
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
    added = [path for status, path in changes if status == "A"]
    if expected is None:
        candidates = [path for path in added if not PANEL_PATTERN.match(path)]
        if len(candidates) == 1:
            expected = candidates[0]
    day = _day_of(expected) if expected is not None else None
    allowed = [expected]
    panel_rel = None
    if expected is not None and FILE_PATTERN.match(expected):
        panel_rel = f"live/{day.isoformat()}.panel.csv"
        if panel_rel in added:
            allowed.append(panel_rel)
        elif require_panel:
            raise ValueError(f"{commit} adds {expected} without its panel {panel_rel}")
    if sorted(changes) != sorted(("A", path) for path in allowed if path):
        raise ValueError(f"{commit} must only add {expected or 'one live record file'}; it changes {changes}")
    if ANCHOR_PATTERN.match(expected):
        record = f"live/{day.isoformat()}.json"
        if parent == EMPTY_TREE or subprocess.run(
            ["git", "cat-file", "-e", f"{parent}:{record}"], cwd=repo, capture_output=True
        ).returncode != 0:
            raise ValueError(f"{commit} anchors {record}, which the log does not yet hold")
    return day


def require_append_only(
    repo: Path, base: str | None, day: date, anchor: bool = False, panel: bool = False
) -> None:
    """HEAD is one commit on top of `base` (`None`: a new branch) that only adds `live/<day>.json`
    (`live/<day>.rekor` with `anchor`), and with `panel` also `live/<day>.panel.csv`.

    The workflow runs this after each commit and before `git push`.

    Raises:
        ValueError: more than one new commit, or a commit that does anything
            but add the day's file, as the bot.
    """

    head = _git(repo, "rev-parse", "HEAD")
    parents = _git(repo, "show", "-s", "--format=%P", head).split()
    if parents != ([base] if base else []):
        raise ValueError(f"HEAD must be one commit on top of {base or 'nothing'}; its parents are {parents}")
    require_add_only_commit(
        repo, head, f"live/{day.isoformat()}.{'rekor' if anchor else 'json'}", require_panel=panel
    )


def _paths(repo: Path) -> list:
    if not _has_commits(repo):
        return []
    return [rel for rel in _git(repo, "ls-tree", "-r", "--name-only", "HEAD").splitlines() if rel]


def logged_files(repo: Path) -> list:
    """The committed record files, oldest day first, as (day, path relative to the repo).

    Raises:
        ValueError: a path that is neither a record nor an anchor.
    """

    paths = _paths(repo)
    for rel in paths:
        _day_of(rel)
    return sorted((_day_of(rel), rel) for rel in paths if FILE_PATTERN.match(rel))


def panel_files(repo: Path) -> list:
    """The committed panel files, oldest day first, as (day, path relative to the repo)."""

    return sorted((_day_of(rel), rel) for rel in _paths(repo) if PANEL_PATTERN.match(rel))


def anchor_files(repo: Path) -> list:
    """The committed anchor files, oldest day first, as (day, path relative to the repo)."""

    return sorted((_day_of(rel), rel) for rel in _paths(repo) if ANCHOR_PATTERN.match(rel))


def unanchored(repo: Path) -> list:
    """The logged days with no anchor yet, oldest first."""

    anchored = {day for day, _ in anchor_files(repo)}
    return [day for day, _ in logged_files(repo) if day not in anchored]


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


def add_environment(repo: Path, day: date, block: dict) -> Path:
    """Insert the `environment` block (`live_pin.environment_block`) into `day`'s new, uncommitted record (#255).

    Raises:
        ValueError: the file is missing, already committed, already carries an
            environment, or is not serialised as the pinned code serialises a record.
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
    if "environment" in record:
        raise ValueError(f"{rel} already carries an environment")
    if record_bytes(record) != raw:
        raise ValueError(f"{rel} is not serialised as a record: refusing to rewrite it")
    record["environment"] = block
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


def _der(buf: bytes, pos: int):
    """One DER element at `pos`: (tag, content start, content end)."""

    if pos + 2 > len(buf):
        raise ValueError("the certificate is truncated")
    tag, first = buf[pos], buf[pos + 1]
    pos += 2
    if first < 0x80:
        length = first
    else:
        count = first & 0x7F
        if count == 0 or count > 4 or pos + count > len(buf):
            raise ValueError("the certificate has a malformed length")
        length = int.from_bytes(buf[pos:pos + count], "big")
        pos += count
    if pos + length > len(buf):
        raise ValueError("the certificate is truncated")
    return tag, pos, pos + length


def _children(buf: bytes, start: int, end: int) -> list:
    out, pos = [], start
    while pos < end:
        tag, begin, stop = _der(buf, pos)
        out.append((tag, begin, stop))
        pos = stop
    return out


def _oid(content: bytes) -> str:
    parts = [content[0] // 40, content[0] % 40]
    value = 0
    for byte in content[1:]:
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            parts.append(value)
            value = 0
    return ".".join(str(p) for p in parts)


def certificate_identity(pem: str):
    """The signing certificate's identity (a SAN URI) and its OIDC issuer, from the DER.

    Raises:
        ValueError: not a certificate, or one without a single SAN URI.
    """

    body = "".join(line for line in pem.splitlines() if line and not line.startswith("-----"))
    try:
        der = base64.b64decode(body, validate=True)
        cert = _der(der, 0)
        tbs = _children(der, cert[1], cert[2])[0]
        fields = _children(der, tbs[1], tbs[2])
    except (binascii.Error, ValueError, IndexError) as error:
        raise ValueError(f"the signing certificate cannot be read: {error}") from error
    extensions = [f for f in fields if f[0] == 0xA3]
    if len(extensions) != 1:
        raise ValueError("the signing certificate has no extensions")
    uris, issuer = [], None
    seq = _children(der, extensions[0][1], extensions[0][2])[0]
    for ext in _children(der, seq[1], seq[2]):
        parts = _children(der, ext[1], ext[2])
        oid = _oid(der[parts[0][1]:parts[0][2]])
        value = parts[-1]
        octets = der[value[1]:value[2]]
        if oid == "2.5.29.17":
            names = _der(octets, 0)
            for tag, begin, stop in _children(octets, names[1], names[2]):
                if tag == 0x86:
                    uris.append(octets[begin:stop].decode("utf-8", "replace"))
        elif oid in _ISSUER_OIDS:
            issuer = octets.decode("utf-8", "replace")
    if len(uris) != 1:
        raise ValueError(f"the signing certificate must carry exactly one SAN URI, not {len(uris)}")
    return uris[0], issuer


def _inclusion_ok(index: int, size: int, leaf: bytes, proof: list, root: bytes) -> bool:
    """RFC 9162 section 2.1.3.2: does `proof` take `leaf` at `index` in a tree of `size` to `root`?"""

    if index >= size:
        return False
    fn, sn, node = index, size - 1, leaf
    for sibling in proof:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            node = hashlib.sha256(b"\x01" + sibling + node).digest()
            while not fn & 1 and fn != 0:
                fn >>= 1
                sn >>= 1
        else:
            node = hashlib.sha256(b"\x01" + node + sibling).digest()
        fn >>= 1
        sn >>= 1
    return sn == 0 and node == root


def verify_entry(response: dict, sha256: str) -> dict:
    """Check one Rekor entry (the API's `{uuid: entry}`) as an anchor of `sha256`, offline.

    Checks that the entry is a `hashedrekord` over exactly `sha256`; that its
    inclusion proof rebuilds the stated root from the entry's body; and that
    its signing certificate names `IDENTITY` and `OIDC_ISSUER`. Not checked
    here, and cosign's (`ONLINE_COMMAND`): the Fulcio chain, the signature
    over the digest, and the signed tree head that authenticates the root.

    Raises:
        ValueError: any of those fails, or the entry is malformed.
    """

    if not isinstance(response, dict) or len(response) != 1:
        raise ValueError("a Rekor response holds exactly one entry, keyed by its UUID")
    uuid, entry = next(iter(response.items()))
    try:
        raw = base64.b64decode(entry["body"], validate=True)
        body = json.loads(raw)
        if body["kind"] != "hashedrekord":
            raise ValueError(f"entry {uuid} is a {body['kind']}, not a hashedrekord")
        data = body["spec"]["data"]["hash"]
        if data["algorithm"] != "sha256" or data["value"] != sha256:
            raise ValueError(f"entry {uuid} is over {data['algorithm']}:{data['value']}, not sha256:{sha256}")
        proof = entry["verification"]["inclusionProof"]
        index, size = int(proof["logIndex"]), int(proof["treeSize"])
        # `logIndex` is the sharded log's global index; the proof's is the active tree's own
        # (#328), so the two differ. The proof places the leaf by the proof's index alone.
        leaf = hashlib.sha256(b"\x00" + raw).digest()
        if not uuid.endswith(leaf.hex()):
            raise ValueError(f"entry {uuid} is not the leaf its body hashes to")
        hashes = [bytes.fromhex(h) for h in proof["hashes"]]
        root = bytes.fromhex(proof["rootHash"])
        pem = base64.b64decode(body["spec"]["signature"]["publicKey"]["content"], validate=True).decode("ascii")
    except (KeyError, TypeError, binascii.Error, UnicodeDecodeError) as error:
        raise ValueError(f"entry {uuid} is malformed: {error!r}") from error
    if not _inclusion_ok(index, size, leaf, hashes, root):
        raise ValueError(f"entry {uuid}'s inclusion proof does not rebuild its root hash")
    identity, issuer = certificate_identity(pem)
    if identity != IDENTITY or issuer != OIDC_ISSUER:
        raise ValueError(f"entry {uuid} was signed by {identity} via {issuer}, not {IDENTITY}")
    return {"uuid": uuid, "log_index": int(entry["logIndex"]), "identity": identity}


def write_anchor(repo: Path, day: date, entries: list) -> Path:
    """Write `live/<day>.rekor` from the first of `entries` that anchors the committed record.

    `entries` are Rekor responses found for the record's SHA-256: others may
    have signed the same bytes, and only this workflow's counts.

    Raises:
        ValueError: the record is not committed, the day is already anchored,
            or no entry anchors it.
    """

    repo = Path(repo)
    rel = f"live/{day.isoformat()}.json"
    if (day, rel) not in logged_files(repo):
        raise ValueError(f"{rel} is not committed: nothing to anchor")
    target = repo / f"live/{day.isoformat()}.rekor"
    if target.exists() or any(d == day for d, _ in anchor_files(repo)):
        raise ValueError(f"{day} is already anchored: an anchor is never replaced")
    sha256 = file_sha256(repo / rel)
    problems = []
    for response in entries:
        try:
            found = verify_entry(response, sha256)
        except ValueError as error:
            problems.append(str(error))
            continue
        anchor = {"date": day.isoformat(), "sha256": sha256, **found, "entry": response}
        target.write_text(json.dumps(anchor, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return target
    raise ValueError(f"no Rekor entry anchors {rel}: {problems or 'none found'}")


def require_anchor(repo: Path, day: date, rel: str, record_sha256: str) -> dict:
    """An anchor file is for its record's bytes, and its stored entry passes `verify_entry`."""

    anchor = json.loads((Path(repo) / rel).read_text(encoding="utf-8"))
    if anchor.get("date") != day.isoformat() or anchor.get("sha256") != record_sha256:
        raise ValueError(f"{rel} anchors {anchor.get('date')} {anchor.get('sha256')}, not {day} {record_sha256}")
    found = verify_entry(anchor.get("entry"), record_sha256)
    if (anchor.get("uuid"), anchor.get("log_index")) != (found["uuid"], found["log_index"]):
        raise ValueError(f"{rel}'s stated UUID or log index differs from its entry's")
    return found


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


def reconcile(repo: Path, digests: dict, run_url: str = "") -> dict:
    """The digests the #225 issue lacks, by day: each logged file with no posted digest (#263).

    A push to `live-log` and the digest post are separate steps, so a failed
    post leaves a record with no digest. This returns the comment to post for
    each such day, in the format `parse_digests` reads, marked "reconciled
    late". It reads the log and writes nothing in it.

    Raises:
        ValueError: a posted digest whose SHA-256 or commit differs from the
            file's, which no late digest can repair.
    """

    repo = Path(repo)
    made = {}
    for day, rel in logged_files(repo):
        posted = digests.get(day)
        if posted is not None:
            if posted["sha256"] != file_sha256(repo / rel):
                raise ValueError(f"{rel}'s posted digest {posted['sha256']} differs from the file's SHA-256")
            if posted["commit"] != adding_commit(repo, rel):
                raise ValueError(f"{rel}'s posted digest names commit {posted['commit']}, not the one that added it")
            continue
        lines = [
            f"{day.isoformat()}: `{rel}`",
            "",
            f"- SHA-256: `{file_sha256(repo / rel)}`",
            f"- commit on live-log: {adding_commit(repo, rel)}",
            "- reconciled late: the record was pushed, and its digest was not posted by the run that wrote it",
        ]
        if run_url:
            lines.append(f"- run: {run_url}")
        made[day] = "\n".join(lines)
    return made


def verify(repo: Path, digests: dict) -> list:
    """Check the whole live log. Returns the logged days, oldest first.

    Raises:
        ValueError: an uncommitted change; a commit that is not add-only by the
            bot; a file whose SHA-256 or adding commit differs from its digest;
            a file with no digest, or a digest with no file; a broken chain; an
            anchor that fails `require_anchor`. A day with no anchor passes.
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
    logged = {day: rel for day, rel in files}
    for day, rel in panel_files(repo):
        if day not in logged:
            raise ValueError(f"{rel} is the panel of a day the log holds no record for")
        named = json.loads((repo / logged[day]).read_text(encoding="utf-8"))["inputs"]["panel_sha256"]
        if file_sha256(repo / rel) != named:
            raise ValueError(f"{rel} is not the panel its record names: SHA-256 {named}")
        if adding_commit(repo, rel) != adding_commit(repo, logged[day]):
            raise ValueError(f"{rel} was not added in its record's commit")
    for day, rel in anchor_files(repo):
        if day not in logged:
            raise ValueError(f"{rel} anchors a day the log holds no record for")
        require_anchor(repo, day, rel, file_sha256(repo / logged[day]))
    return [day for day, _ in files]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    chain = sub.add_parser("chain", help="insert the chain block into the day's new record")
    chain.add_argument("--live-dir", required=True, type=Path)
    chain.add_argument("--date", required=True)
    env = sub.add_parser("environment", help="insert the environment block into the day's new record")
    env.add_argument("--live-dir", required=True, type=Path)
    env.add_argument("--date", required=True)
    env.add_argument("--block", required=True, type=Path, help="`live_pin.py environment`'s output")
    check = sub.add_parser("check-append", help="the new commit only adds the day's record")
    check.add_argument("--live-dir", required=True, type=Path)
    check.add_argument("--date", required=True)
    check.add_argument("--base", required=True, help="origin/live-log's SHA, or 'none' for a new branch")
    check.add_argument("--anchor", action="store_true", help="the commit adds the day's .rekor file")
    check.add_argument("--panel", action="store_true", help="the record's commit must add the day's panel too")
    missing = sub.add_parser("unanchored", help="the logged days with no anchor yet")
    missing.add_argument("--live-dir", required=True, type=Path)
    anchor = sub.add_parser("anchor-file", help="write the day's .rekor file from Rekor entries")
    anchor.add_argument("--live-dir", required=True, type=Path)
    anchor.add_argument("--date", required=True)
    anchor.add_argument("--entries", required=True, type=Path, help="a JSON list of Rekor responses")
    every = sub.add_parser("verify", help="check every logged file, commit, digest and link")
    every.add_argument("--live-dir", required=True, type=Path)
    every.add_argument("--digests", required=True, type=Path)
    late = sub.add_parser("reconcile", help="write the #225 digest of every logged file that has none")
    late.add_argument("--live-dir", required=True, type=Path)
    late.add_argument("--digests", required=True, type=Path)
    late.add_argument("--out-dir", required=True, type=Path, help="outside the log: one DAY.md per comment to post")
    late.add_argument("--run-url", default="")
    args = parser.parse_args(argv)
    day = date.fromisoformat(args.date) if getattr(args, "date", None) else None
    if args.command == "chain":
        path = add_chain(args.live_dir, day)
        record = json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps({"file": str(path), "chain": record.get("chain")}))
    elif args.command == "environment":
        path = add_environment(args.live_dir, day, json.loads(args.block.read_text(encoding="utf-8")))
        print(json.dumps({"file": str(path)}))
    elif args.command == "check-append":
        require_append_only(
            args.live_dir, None if args.base == "none" else args.base, day, args.anchor, args.panel
        )
        print(json.dumps({"append_only": f"live/{day.isoformat()}.{'rekor' if args.anchor else 'json'}"}))
    elif args.command == "unanchored":
        print(json.dumps({"unanchored": [d.isoformat() for d in unanchored(args.live_dir)]}))
    elif args.command == "anchor-file":
        path = write_anchor(args.live_dir, day, json.loads(args.entries.read_text(encoding="utf-8")))
        anchor = json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps({"file": str(path), "uuid": anchor["uuid"], "log_index": anchor["log_index"]}))
    elif args.command == "reconcile":
        made = reconcile(args.live_dir, parse_digests(args.digests), args.run_url)
        args.out_dir.mkdir(parents=True, exist_ok=True)
        for made_day, body in made.items():
            (args.out_dir / f"{made_day.isoformat()}.md").write_text(body + "\n", encoding="utf-8")
        print(json.dumps({"reconciled": [d.isoformat() for d in made]}))
    else:
        days = verify(args.live_dir, parse_digests(args.digests))
        print(json.dumps({"verified": [d.isoformat() for d in days]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
