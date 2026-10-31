"""Owner attestation (#256): a binding approval counts only when Eleonora made it herself.

Agent sessions post to GitHub under Eleonora's account, with
`author_association: OWNER`, so a comment reading "Ruling (Eleonora; relayed
by the orchestrating session)" proves nothing about her instruction. On #151 a
relayed "go" was posted and then withdrawn as "not a go". What an app cannot
set on her behalf is the REST field `performed_via_github_app`: it names the
app a comment was posted through, and is `null` only on a comment posted
without one.

A comment is **owner-attested** for a phrase when it is by `eleonorabjornberg`,
a `User` account, its `performed_via_github_app` present and `null`, never
edited since it was posted (an app can edit the body of a comment she posted
herself, and the field stays `null`), on the issue it is cited for, and its
body contains the phrase whole and case-sensitively. Anything else raises
`NotOwnerAttested`, a `ValueError`.

**Binding changes** (the draft rule, `docs/decisions/drafts/owner-attestation.md`)
are the ones a pull request may make only with her own approval:

* `lockbox`: any change to the tiers of `metadata/lockbox.json`, opening a tier
  among them;
* `live-pin`: the live record's pinned code: `PINNED_CODE_SHA` or `resolve_pin`
  in `scripts/live_record.py`, or a pin manifest `metadata/live_pin.json`;
* `live-model`: the models the live record logs: the names in its `MODELS`
  and the published records (`docs/runs/...`) it names, so a model joining the
  record (v2, #245) is one;
* `claude-files`: `CLAUDE.md` or any file under `.claude/` (ruling on PR #943, 19 October 2026);
* `registration`: any file under `metadata/registrations/` or `docs/registrations/`, where a candidate's
  registration under `docs/decisions/scoring-protocol.md` section 2 is recorded (the protocol names no path yet;
  these two are the ones the check watches until Eleonora names another);
* `decisions`: any file under `docs/decisions/`, `docs/decisions/drafts/` included, added, changed, deleted or
  moved (ruling on #1068, 21 October 2026; #1074). Moving a draft out of `drafts/` is a delete and an add, both
  listed. The two settlement-dating declarations, `metadata/settlement_announcement_dating.json` and
  `metadata/net_settlement.json`, are bound under this kind too (#1327, her ruling of 30 October 2026): they hold the
  announcement instant the H5 candidate's information set rests on, so a change to either is a decision. One kind, not a
  new one, so that a change to the record and to a declaration together needs one `GO`.

A pull request that makes one cites her approval by appending an entry to
`metadata/owner_attestations.json`: its kind, the issue, the comment id, and the
phrase, which by the "GO" convention is always `GO #<issue>`. The registry is
append-only. CI (`tests.yml`, job `owner-attested`) runs `check` on every pull
request: each binding kind changed needs an entry ADDED by that change, of that kind, for an issue the change
cites (its branch `directive/N-...`, a `Closes #N` line or a `GO #N` phrase in the pull request or commit message),
and every added entry is fetched from the REST API and must be owner-attested, on a comment no earlier entry
cites (#1225; entries already in the registry are grandfathered). An entry already on the base, or for
an issue the change does not cite, covers nothing (#1188). A pull request is checked on its own range (`--merge-ref`
drops the main that the event's merge ref picks up); a push range is checked merge by merge.

    python3 scripts/owner_attested.py find --issue N --phrase "GO #N" [--comments-file F]
    python3 scripts/owner_attested.py check --base REF [--head REF] [--merge-ref] [--pr N] [--cite N]
    python3 scripts/owner_attested.py check --push-before SHA [--head REF]

`find` prints the first owner-attested comment on issue N carrying the phrase,
from the REST API or a recorded payload, and exits 1 if there is none. `check`
compares two commits of this repository. Both read `GH_TOKEN` when they fetch.

Standard library only.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OWNER = "eleonorabjornberg"
DEFAULT_REPOSITORY = "eleonorabjornberg/repo-market-model"
API = "https://api.github.com"

LOCKBOX = "metadata/lockbox.json"
LIVE = "scripts/live_record.py"
PIN_MANIFEST = "metadata/live_pin.json"
REGISTRY = "metadata/owner_attestations.json"
RULE = "docs/decisions/drafts/owner-attestation.md"

#: The binding kinds a registry entry may cite.
KINDS = ("lockbox", "live-pin", "live-model", "claude-files", "registration", "decisions")

#: Binding by path: the exact files and the directories (with their trailing slash) that no pull request may change
#: without her own GitHub action. `CLAUDE.md` is the one at the repository root, not a look-alike elsewhere.
CLAUDE_FILES = ("CLAUDE.md",)
CLAUDE_DIRS = (".claude/",)
REGISTRATION_DIRS = ("metadata/registrations/", "docs/registrations/")
DECISIONS_DIRS = ("docs/decisions/",)
#: Data declarations bound under `decisions` (#1327): the announcement instants of the H5 candidate's settlement terms.
DATING_FILES = ("metadata/settlement_announcement_dating.json", "metadata/net_settlement.json")
ENTRY_KEYS = {"kind", "issue", "comment_id", "phrase", "what"}


class NotOwnerAttested(ValueError):
    """A binding approval that is not Eleonora's own GitHub action."""


# -- one comment ----------------------------------------------------------------


def go_phrase(issue: int) -> str:
    """The "GO" convention: her approval on issue N says `GO #N`."""

    return f"GO #{issue}"


def phrase_in(body: str, phrase: str) -> bool:
    """`phrase` occurs in `body` whole: not inside a longer word or number."""

    return re.search(r"(?<![\w#])" + re.escape(phrase) + r"(?!\w)", body or "") is not None


def verify_comment(comment: dict, phrase: str, issue: int = None, owner: str = OWNER) -> dict:
    """Return `comment` if it is owner-attested for `phrase`; raise otherwise.

    Raises:
        ValueError: on an empty phrase.
        NotOwnerAttested: naming the first test the comment fails.
    """

    if not isinstance(phrase, str) or not phrase.strip():
        raise ValueError("an attestation needs a non-empty phrase")
    where = f"comment {comment.get('id')}"
    user = comment.get("user") or {}
    if user.get("login") != owner:
        raise NotOwnerAttested(f"{where} is by {user.get('login')!r}, not {owner}")
    if user.get("type") != "User":
        raise NotOwnerAttested(f"{where} is by a {user.get('type')!r} account, not a User")
    if "performed_via_github_app" not in comment:
        raise NotOwnerAttested(f"{where} carries no performed_via_github_app field")
    app = comment["performed_via_github_app"]
    if app is not None:
        slug = app.get("slug") if isinstance(app, dict) else app
        raise NotOwnerAttested(f"{where} was posted through the {slug!r} app")
    if comment.get("updated_at") != comment.get("created_at"):
        raise NotOwnerAttested(
            f"{where} was edited at {comment.get('updated_at')}, after it was posted"
        )
    if issue is not None:
        on = str(comment.get("issue_url", "")).rstrip("/").rsplit("/", 1)[-1]
        if on != str(issue):
            raise NotOwnerAttested(f"{where} is on #{on}, not #{issue}")
    if not phrase_in(comment.get("body", ""), phrase):
        raise NotOwnerAttested(f"{where} does not contain {phrase!r}")
    return comment


def find_attested(comments, phrase: str, issue: int = None, owner: str = OWNER) -> dict:
    """The first owner-attested comment carrying `phrase`, in the order given."""

    candidates = [c for c in comments if phrase_in(c.get("body", ""), phrase)]
    if not candidates:
        raise NotOwnerAttested(f"no comment contains {phrase!r}")
    reasons = []
    for comment in candidates:
        try:
            return verify_comment(comment, phrase, issue=issue, owner=owner)
        except NotOwnerAttested as exc:
            reasons.append(str(exc))
    raise NotOwnerAttested(
        f"no comment carrying {phrase!r} is owner-attested: " + "; ".join(reasons)
    )


# -- what is binding ---------------------------------------------------------------


def _module(text):
    return ast.parse(text) if text is not None else None


def _assigned(tree, name):
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                return node.value
    return None


def live_pin_state(text):
    """What decides the live record's pinned code, in `scripts/live_record.py`."""

    tree = _module(text)
    if tree is None:
        return None
    value = _assigned(tree, "PINNED_CODE_SHA")
    resolver = next(
        (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "resolve_pin"), None
    )
    if resolver is not None and ast.get_docstring(resolver) is not None:
        resolver = ast.FunctionDef(
            name=resolver.name, args=resolver.args, body=resolver.body[1:],
            decorator_list=resolver.decorator_list, returns=resolver.returns,
            type_comment=None, type_params=[],
        )
    return {
        "PINNED_CODE_SHA": None if value is None else ast.literal_eval(value),
        "resolve_pin": None if resolver is None else ast.dump(resolver),
    }


def live_model_state(text):
    """The models the live record logs: `MODELS` names and the records it names."""

    tree = _module(text)
    if tree is None:
        return None
    models = set()
    value = _assigned(tree, "MODELS")
    for node in ast.walk(value) if value is not None else ():
        if isinstance(node, ast.Dict):
            for key, item in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "name" and isinstance(
                    item, ast.Constant
                ):
                    models.add(item.value)
    records = {
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and node.value.startswith("docs/runs/")
    }
    return {"models": sorted(models), "records": sorted(records)}


def _json(text):
    return None if text is None else json.loads(text)


def _tiers(text):
    data = _json(text)
    return None if data is None else data.get("tiers")


def path_kinds(paths) -> set:
    """The path-bound kinds among `paths`: """

    kinds = set()
    for path in paths:
        if path in CLAUDE_FILES or path.startswith(CLAUDE_DIRS):
            kinds.add("claude-files")
        if path.startswith(REGISTRATION_DIRS):
            kinds.add("registration")
        if path.startswith(DECISIONS_DIRS) or path in DATING_FILES:
            kinds.add("decisions")
    return kinds


def binding_kinds(read_base, read_head, changed_paths=None) -> set:
    """The binding kinds that differ between two trees; `read(path)` gives text or None.

    `changed_paths()` lists the paths the change touches; without it the path-bound kinds are not looked at.
    """

    kinds = path_kinds(changed_paths()) if changed_paths is not None else set()
    if _tiers(read_base(LOCKBOX)) != _tiers(read_head(LOCKBOX)):
        kinds.add("lockbox")
    base_live, head_live = read_base(LIVE), read_head(LIVE)
    if live_pin_state(base_live) != live_pin_state(head_live) or _json(
        read_base(PIN_MANIFEST)
    ) != _json(read_head(PIN_MANIFEST)):
        kinds.add("live-pin")
    if live_model_state(base_live) != live_model_state(head_live):
        kinds.add("live-model")
    return kinds


# -- the registry -------------------------------------------------------------------


def load_registry(text) -> list:
    """The entries of `metadata/owner_attestations.json`, validated; `[]` if absent."""

    if text is None:
        return []
    data = json.loads(text)
    if not isinstance(data, dict) or data.get("version") != 1 or isinstance(
        data.get("version"), bool
    ):
        raise ValueError(f"{REGISTRY} needs version 1")
    entries = data.get("attestations")
    if not isinstance(entries, list):
        raise ValueError(f"{REGISTRY} needs an attestations list")
    for position, entry in enumerate(entries):
        where = f"{REGISTRY} attestations[{position}]"
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            raise ValueError(f"{where} needs exactly {sorted(ENTRY_KEYS)}")
        if entry["kind"] not in KINDS:
            raise ValueError(f"{where}: kind {entry['kind']!r} is not one of {KINDS}")
        for key in ("issue", "comment_id"):
            value = entry[key]
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{where}: {key} must be a positive integer")
        if entry["phrase"] != go_phrase(entry["issue"]):
            raise ValueError(
                f"{where}: the phrase must be {go_phrase(entry['issue'])!r} (the GO convention)"
            )
        if not isinstance(entry["what"], str) or not entry["what"].strip():
            raise ValueError(f"{where}: say what the approval covers")
    return entries


def added_entries(base_text, head_text) -> list:
    """Entries the head appends to the base registry; refuses any other change."""

    base, head = load_registry(base_text), load_registry(head_text)
    if head[: len(base)] != base:
        raise ValueError(f"{REGISTRY} is append-only: an existing entry was changed or removed")
    return head[len(base):]


CLOSING = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+#(\d+)", re.IGNORECASE)
GO_MENTION = re.compile(r"(?<![\w#])GO #(\d+)(?!\w)")
BRANCH_ISSUE = re.compile(r"(?:^|[/\s])directive/(\d+)-")


def cited_issues(*texts) -> set:
    """The issues a change cites: the directive branch (`directive/N-...`), a closing line (`Closes #N`) and a
    `GO #N` phrase, in the texts given (a pull request's branch, title and body, a commit message).

    A bare `#N` mention does not cite: a pull request that names an issue in passing does not borrow its
    attestation (#1188).
    """

    found = set()
    for text in texts:
        for pattern in (BRANCH_ISSUE, CLOSING, GO_MENTION):
            found.update(int(n) for n in pattern.findall(text or ""))
    return found


def check(read_base, read_head, fetch_comment, changed_paths=None, cited=None) -> list:
    """Every binding change cites an owner-attested comment; return those comments.

    A binding kind is covered only by an entry ADDED in this range whose kind is that kind and whose issue is
    one the change cites (`cited`, see `cited_issues`). An entry already on the base, or for another issue,
    covers nothing (#1188). `fetch_comment(comment_id)` returns the REST payload of an issue comment.
    Nothing is fetched when nothing is added.
    """

    kinds = binding_kinds(read_base, read_head, changed_paths)
    added = added_entries(read_base(REGISTRY), read_head(REGISTRY))
    if kinds and cited is None:
        raise ValueError("check needs the issues the change cites when it is binding")
    cited = set(cited or ())
    covered = {entry["kind"] for entry in added if entry["issue"] in cited}
    missing = sorted(kinds - covered)
    if missing:
        have = ", ".join(f"{e['kind']} #{e['issue']}" for e in added) or "none"
        raise NotOwnerAttested(
            f"this change is binding ({', '.join(missing)}) and no entry added by it covers that kind for an "
            f"issue it cites (cites: {', '.join('#%d' % n for n in sorted(cited)) or 'no issue'}; "
            f"entries added: {have}). Append an entry of that kind to {REGISTRY} citing Eleonora's own "
            f"'GO #N' comment, and cite #N in the pull request (branch directive/N-, 'Closes #N' or 'GO #N') "
            f"(rule: {RULE})"
        )
    held = {entry["comment_id"] for entry in load_registry(read_base(REGISTRY))}
    reused = sorted(
        {e["comment_id"] for i, e in enumerate(added)
         if e["comment_id"] in held or any(o["comment_id"] == e["comment_id"] for o in added[:i])}
    )
    if reused:
        raise NotOwnerAttested(
            f"comment {', '.join(map(str, reused))} is already in the registry (or cited twice by this change): "
            f"each binding change needs a fresh 'GO #N' comment from Eleonora (#1225)"
        )
    verified = []
    for entry in added:
        comment = fetch_comment(entry["comment_id"])
        if comment.get("id") != entry["comment_id"]:
            raise NotOwnerAttested(
                f"fetched comment id {comment.get('id')}, not the cited {entry['comment_id']}"
            )
        verified.append(verify_comment(comment, entry["phrase"], issue=entry["issue"]))
    return verified


# -- GitHub and git -----------------------------------------------------------------


def _get(path, token):
    request = urllib.request.Request(f"{API}/{path}")
    request.add_header("Accept", "application/vnd.github+json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_comment(repository, comment_id, token):
    return _get(f"repos/{repository}/issues/comments/{int(comment_id)}", token)


def fetch_issue_comments(repository, issue, token):
    comments, page = [], 1
    while True:
        batch = _get(f"repos/{repository}/issues/{int(issue)}/comments?per_page=100&page={page}", token)
        if not batch:
            return comments
        comments.extend(batch)
        page += 1


def git_reader(ref):
    """`read(path)` at commit `ref` of this repository: its text, or None if absent."""

    def read(path):
        result = subprocess.run(
            ["git", "show", f"{ref}:{path}"], cwd=REPO, capture_output=True, text=True,
        )
        return result.stdout if result.returncode == 0 else None

    return read


def git_changed(base, head):
    """`changed_paths()` for a pull request: the paths `head` changed since it left `base`."""

    def changed():
        result = subprocess.run(
            ["git", "diff", "--name-only", "--no-renames", f"{base}...{head}"],
            cwd=REPO, capture_output=True, text=True, check=True,
        )
        return result.stdout.splitlines()

    return changed


ZERO_SHA = "0" * 40


def resolve_push_base(before, head):
    """The base of a push range: `before`, or `head`'s first parent when `before` is absent or unreachable.

    A push that creates a ref has an all-zero `before`, and a force-push can leave one this clone lacks.
    """

    if before and before != ZERO_SHA:
        found = subprocess.run(
            ["git", "cat-file", "-e", f"{before}^{{commit}}"], cwd=REPO, capture_output=True,
        )
        if found.returncode == 0:
            return before
    return f"{head}^"


def git_lines(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout.splitlines()


def push_commits(base, head) -> list:
    """The commits a push range holds, first-parent, oldest first: each merge (or commit) is one unit."""

    return git_lines("rev-list", "--first-parent", "--reverse", f"{base}..{head}")


def pr_number(subject):
    """The pull request a merge or squash subject names: `Merge pull request #N ...` or `... (#N)`."""

    found = re.match(r"Merge pull request #(\d+)\b", subject) or re.search(r"\(#(\d+)\)\s*$", subject)
    return int(found.group(1)) if found else None


def fetch_pull(repository, number, token):
    return _get(f"repos/{repository}/pulls/{int(number)}", token)


def pull_texts(pull) -> list:
    """Branch, title and body of a pull request payload, as texts `cited_issues` reads."""

    return [pull["head"]["ref"], pull.get("title") or "", pull.get("body") or ""]


def push_range_report(base, head) -> str:
    """One line per commit in `base..head` that touches a binding path: its short SHA, subject and those files."""

    log = subprocess.run(
        ["git", "log", "--no-merges", "--first-parent", "--format=%H%x09%s", f"{base}..{head}"],
        cwd=REPO, capture_output=True, text=True,
    ).stdout.splitlines()
    log += subprocess.run(
        ["git", "log", "--merges", "--first-parent", "--format=%H%x09%s", f"{base}..{head}"],
        cwd=REPO, capture_output=True, text=True,
    ).stdout.splitlines()
    lines = []
    for row in log:
        sha, _, subject = row.partition("\t")
        files = subprocess.run(
            ["git", "diff", "--name-only", "--no-renames", f"{sha}^", sha],
            cwd=REPO, capture_output=True, text=True,
        ).stdout.splitlines()
        bound = [path for path in files if path_kinds([path])]
        if bound:
            lines.append(f"  {sha[:8]} {subject}: {', '.join(bound)}")
    return "\n".join(lines)


# -- commands -----------------------------------------------------------------------


def _find(args):
    if args.comments_file:
        loaded = json.loads(Path(args.comments_file).read_text(encoding="utf-8"))
        comments = loaded if isinstance(loaded, list) else [loaded]
    else:
        comments = fetch_issue_comments(args.repo, args.issue, os.environ.get("GH_TOKEN"))
    found = find_attested(comments, args.phrase, issue=args.issue)
    print(json.dumps({k: found.get(k) for k in ("id", "html_url", "created_at")}))


def _commit_texts(sha):
    return ["\n".join(git_lines("log", "-1", "--format=%B", sha))]


def _check_range(args, base, head, token, texts):
    cited = cited_issues(*texts)
    cited.update(args.cite)
    return check(
        git_reader(base), git_reader(head),
        lambda comment_id: fetch_comment(args.repo, comment_id, token),
        changed_paths=git_changed(base, head), cited=cited,
    )


def _check(args):
    token = os.environ.get("GH_TOKEN")
    verified = []
    if args.push_before is not None:
        # Each merge (or commit) of the pushed range is checked on its own range: an entry another merge in the
        # range added covers nothing here (#1188).
        base = resolve_push_base(args.push_before, args.head)
        for sha in push_commits(base, args.head):
            subject = git_lines("log", "-1", "--format=%s", sha)[0]
            texts = _commit_texts(sha)
            number = pr_number(subject)
            if number is not None and not args.no_fetch_pull:
                texts += pull_texts(fetch_pull(args.repo, number, token))
            try:
                verified += _check_range(args, f"{sha}^", sha, token, texts)
            except NotOwnerAttested as exc:
                report = push_range_report(f"{sha}^", sha)
                raise NotOwnerAttested(f"{sha[:8]} {subject}: {exc}" + (f"\nbinding paths:\n{report}" if report else "")) from exc
    else:
        base, head = args.base, args.head
        texts = []
        if args.merge_ref:
            # The pull_request event checks out a merge ref, whose first parent is main as it is now. The pull
            # request's own change is the range from the merge base to its second parent.
            head = f"{args.head}^2"
            base = git_lines("merge-base", args.base, head)[0]
        else:
            texts += _commit_texts(head)
        if args.pr is not None:
            texts += pull_texts(fetch_pull(args.repo, args.pr, token))
        try:
            verified = _check_range(args, base, head, token, texts)
        except NotOwnerAttested as exc:
            report = push_range_report(base, head)
            if report:
                raise NotOwnerAttested(f"{exc}\nbinding paths changed in {base[:8]}..{head[:8]}:\n{report}") from exc
            raise
    if not verified:
        print("owner-attested: no binding change and no new attestation")
    for comment in verified:
        print(f"owner-attested: {comment['html_url']}")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    sub = parser.add_subparsers(dest="command", required=True)
    find = sub.add_parser("find", help="the owner-attested comment on an issue carrying a phrase")
    find.add_argument("--issue", type=int, required=True)
    find.add_argument("--phrase", required=True)
    find.add_argument("--comments-file", help="a recorded REST payload instead of a fetch")
    find.set_defaults(func=_find)
    chk = sub.add_parser("check", help="binding changes between two commits cite her approval")
    chk.add_argument("--base", help="the commit the change leaves from (a pull request's base)")
    chk.add_argument("--push-before", help="a push's `before` SHA, used as the base; an all-zero or unknown SHA "
                     "falls back to the head's first parent")
    chk.add_argument("--head", default="HEAD")
    chk.add_argument("--pr", type=int, help="the pull request number: its branch, title and body say which issues "
                     "the change cites")
    chk.add_argument("--merge-ref", action="store_true", help="--head is the merge ref a pull_request event checks out; "
                     "check the pull request's own range (merge base .. second parent)")
    chk.add_argument("--cite", type=int, action="append", default=[], help="an issue the change cites, when no "
                     "pull request is fetched")
    chk.add_argument("--no-fetch-pull", action="store_true", help="on a push range, read only commit messages")
    chk.set_defaults(func=_check)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "check" and (args.base is None) == (args.push_before is None):
        build_parser().error("check needs exactly one of --base and --push-before")
    try:
        args.func(args)
    except NotOwnerAttested as exc:
        print(f"not owner-attested: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
