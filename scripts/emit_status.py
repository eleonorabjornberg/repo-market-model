#!/usr/bin/env python3
"""Emit docs/status.json: the machine-readable status this repository publishes.

Nothing here is typed. The phase numbers, their names, their exit criteria and
which phase is current are all read from PLAN.md, the roadmap this project
already maintains; the figures are measured from the repository.

Two constants used to sit at the top of this file recording which phase was
current and whether it had finished, alongside a transcribed copy of PLAN.md's
phase table. They drifted: three phase names and the current phase itself came
to disagree with PLAN.md while every measured figure beside them stayed
correct. A transcription is a copy that rots, which is the finding this
repository keeps making about other people's numbers, so it does not get to
keep one of its own.

Declaring a phase complete is still a judgement and still a human's. It is now
made once, by editing a heading in PLAN.md, instead of twice.

The date and commit are those of the latest commit that changed one of the
file's inputs (`INPUTS`), never today's date and never the commit that records
the file. A status page that can run ahead of the work it describes is the
failure this repository exists to prevent, and that includes the copy of it
published on a website.

The file is regenerated inside the pull request that changes its inputs, not by
a bot on `main` afterwards (directive 05, #50): a bot commit on `main` left
every open branch one commit behind after each merge. A file cannot name the
commit that contains it, so a pull request that changes an input commits the
change first, then runs this script and commits `docs/status.json` on top.
`--check` is what CI runs: it fails when the committed file is not what the
inputs produce, which is also how a later commit to an input is caught.

It reads git history, so it refuses a shallow clone rather than stamping a
commit that only looks like the latest.

Standard library only.

    python3 scripts/emit_status.py            # writes docs/status.json
    python3 scripts/emit_status.py --check    # writes nothing; fails if it is stale
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

# PLAN.md's phase headings are the source. One looks like
#
#     ## Phase 1 — Public U.S. dataset (in progress)
#
# where the parenthetical is the phase's own statement about itself and is
# optional. Only the exact word "complete" counts as complete: a partial claim
# such as "(evaluation foundation complete)", which Phase 2 carried until
# 11 Sep, read as a finished phase would advance the published status past the
# work.
HEADING = re.compile(r"^## Phase (\d+) — (.+)$")
MARKER = re.compile(r"^(.*?)\s*\(([^()]+)\)$")
CRITERION = re.compile(r"^Exit criterion[^:]*:\s*(.*)$")
# A phase stopped by a human decision with items still open (Eleonora,
# 5 October 2026, #234). It is not complete, and it is not open work beside the
# current phase; the status file lists it on its own.
CLOSED = "closed for now"


class PlanError(RuntimeError):
    """PLAN.md does not say what the status file needs. Do not guess."""


def parse_plan(text):
    """Every phase in PLAN.md: number, name, marker, exit criterion."""
    lines = text.splitlines()
    heads = [(i, HEADING.match(line)) for i, line in enumerate(lines)]
    heads = [(i, match) for i, match in heads if match]
    if not heads:
        raise PlanError("PLAN.md has no '## Phase N — ...' headings")

    phases = []
    for index, match in heads:
        # A phase ends at the next second-level heading of any kind, which is
        # what keeps Milestone A's own exit criterion out of Phase 1's.
        end = next((j for j in range(index + 1, len(lines))
                    if lines[j].startswith("## ")), len(lines))
        title = match.group(2).strip()
        parts = MARKER.match(title)
        name = parts.group(1).strip() if parts else title
        marker = parts.group(2).strip().lower() if parts else ""
        phases.append({
            "number": int(match.group(1)),
            "name": name,
            "marker": marker,
            "exit": exit_criterion(lines[index + 1:end]),
        })

    numbering = [phase["number"] for phase in phases]
    if numbering != list(range(len(phases))):
        raise PlanError("PLAN.md numbers its phases %s; expected %s"
                        % (numbering, list(range(len(phases)))))
    return phases


def exit_criterion(section):
    """The criterion as PLAN.md words it, never a shortened restatement.

    None when the phase does not state one. Phase 7 does not: it describes what
    the European model must represent and stops. The table this parser replaced
    filled that hole with a paraphrase of that sentence, presented as a
    criterion PLAN.md never wrote — which is the whole argument against keeping
    a second copy. An absent criterion is only an error for a phase this file
    actually publishes, and require_exit is where that is enforced.
    """
    for offset, line in enumerate(section):
        match = CRITERION.match(line)
        if not match:
            continue
        collected = [match.group(1)]
        for following in section[offset + 1:]:
            if not following.strip():
                break
            collected.append(following.strip())
        text = " ".join(collected).replace("**Met.**", "").replace("*", "")
        text = re.sub(r"\s+", " ", text).strip().rstrip(".")
        return text or None
    return None


def require_exit(phase, role):
    """A published phase has to carry its own criterion, not a supplied one."""
    if not phase["exit"]:
        raise PlanError(
            "Phase %d is what this status file publishes as %s, and PLAN.md "
            "states no 'Exit criterion:' for it. Write one there rather than "
            "here." % (phase["number"], role))
    return phase["exit"]


def current_phase(phases):
    """The latest phase PLAN.md marks in progress, and its state.

    Phases may overlap (human decision, 11 Sep): the forecasting work of
    Phase 2 is under way while Phase 1's data work is still open, and
    publishing Phase 1 as the current phase understated the work as surely as
    publishing Phase 2 as complete would overstate it. So the current phase is
    the latest one marked "(in progress)"; every phase before it must be marked
    complete, in progress or closed for now; the open ones are published
    beside it by `alongside`, and the closed ones by `closed_for_now`.

    Raising is the point. If PLAN.md will not say that the phase being worked
    is in progress, this file has nothing to publish, and a guess would be the
    hand-written claim the repository exists to refuse.
    """
    done = [phase for phase in phases if phase["marker"] == "complete"]
    outstanding = [phase for phase in phases
                   if phase["marker"] not in ("complete", CLOSED)]
    if not outstanding:
        if any(phase["marker"] == CLOSED for phase in phases):
            raise PlanError(
                "PLAN.md marks every unfinished phase closed for now, so no "
                "phase is in progress. Say which one is being worked.")
        return len(phases) - 1, "complete"

    current = outstanding[0]
    ahead = [phase for phase in done if phase["number"] > current["number"]]
    if ahead:
        raise PlanError(
            "PLAN.md marks phase %d complete while phase %d is not. A phase "
            "cannot finish before the one before it; one of the two headings "
            "is stale." % (ahead[0]["number"], current["number"]))

    if "in progress" not in current["marker"]:
        raise PlanError(
            "Phase %d is the first phase PLAN.md does not mark complete, and "
            "its heading says (%s). Mark it '(in progress)' or '(complete)' — "
            "this file will not decide which."
            % (current["number"], current["marker"] or "nothing"))

    working = [phase for phase in outstanding if "in progress" in phase["marker"]]
    latest = working[-1]
    gap = [phase for phase in outstanding
           if phase["number"] < latest["number"] and phase not in working]
    if gap:
        raise PlanError(
            "PLAN.md marks phase %d in progress while phase %d, before it, is "
            "marked neither complete nor in progress (%s). Say which it is."
            % (latest["number"], gap[0]["number"], gap[0]["marker"] or "nothing"))
    later = [phase for phase in phases
             if phase["marker"] == CLOSED and phase["number"] > latest["number"]]
    if later:
        raise PlanError(
            "PLAN.md marks phase %d closed for now, after phase %d, the latest "
            "in progress. A phase is closed for now only once work has moved past it."
            % (later[0]["number"], latest["number"]))
    return latest["number"], "in progress"


def alongside(phases, number):
    """Earlier phases still open while phase `number` is the one published."""
    return [{"number": phase["number"], "name": phase["name"]}
            for phase in phases
            if phase["number"] < number
            and phase["marker"] not in ("complete", CLOSED)]


def closed_for_now(phases, number):
    """Earlier phases closed for now: neither finished nor worked beside it."""
    return [{"number": phase["number"], "name": phase["name"]}
            for phase in phases
            if phase["number"] < number and phase["marker"] == CLOSED]

ROOT = Path(__file__).resolve().parent.parent


#: What docs/status.json is computed from, as git pathspecs. `docs/runs/*.json`
#: is the top level only (the file lists those names, and `docs/runs/archive/`
#: is not published); `glob` magic keeps `*` from crossing a `/`.
INPUTS = (
    "PLAN.md",
    "pyproject.toml",
    "metadata/events.json",
    ":(glob)docs/runs/*.json",
)


def git(*args):
    return subprocess.run(("git",) + args, cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def input_stamp():
    """The short sha and commit date of the latest commit that changed an input.

    History is simplified the default way, so a merge commit that only brings
    an input in from one side is skipped in favour of the commit that changed
    it. Uncommitted edits to an input are refused: the stamp would name a commit
    that does not carry them.
    """
    if git("rev-parse", "--is-shallow-repository") == "true":
        raise PlanError("docs/status.json is stamped from git history, and this "
                        "clone is shallow. Fetch the full history (in CI, "
                        "actions/checkout with fetch-depth: 0).")
    if git("status", "--porcelain", "--", *INPUTS):
        raise PlanError("An input of docs/status.json has uncommitted changes. "
                        "Commit them first, then emit: the file is stamped with "
                        "the commit that changed its inputs.")
    line = git("log", "-1", "--format=%H %cd", "--date=short", "--", *INPUTS)
    if not line:
        raise PlanError("No commit changes an input of docs/status.json.")
    sha, date = line.split()
    return sha[:7], date


def dependency_count():
    """Count declared runtime dependencies. The claim is zero; measure it."""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^dependencies\s*=\s*\[(.*?)\]", text, re.S | re.M)
    if not match:
        return 0
    return len([item for item in match.group(1).split(",") if item.strip()])


def main():
    manifest = json.loads((ROOT / "docs/runs/funding_panel.manifest.json").read_text(encoding="utf-8"))
    events = json.loads((ROOT / "metadata/events.json").read_text(encoding="utf-8"))

    phases = parse_plan((ROOT / "PLAN.md").read_text(encoding="utf-8"))
    number, state = current_phase(phases)
    phase = phases[number]
    require_exit(phase, "the current phase")
    following = phases[number + 1] if number + 1 < len(phases) else phase

    commit, generated_at = input_stamp()
    status = {
        "generated_at": generated_at,
        "commit": commit,
        "phase": {"number": phase["number"], "name": phase["name"], "state": state},
        "alongside": alongside(phases, number),
        "closed_for_now": closed_for_now(phases, number),
        "next": {"number": following["number"], "name": following["name"],
                 "exit": require_exit(following, "the next phase")},
        "total_phases": len(phases),
        "figures": {
            "panel_start": manifest["start_date"],
            "panel_end": manifest["end_date"],
            "panel_rows": manifest["row_count"],
            "event_holdouts": len(events["windows"]),
            "dependencies": dependency_count(),
        },
        "run_records": sorted(p.name for p in (ROOT / "docs/runs").glob("*.json")),
    }

    text = json.dumps(status, indent=2, sort_keys=True) + "\n"
    target = ROOT / "docs/status.json"
    if "--check" in sys.argv:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current == text:
            print("docs/status.json agrees with its inputs at %s." % commit)
            return
        sys.stdout.writelines(difflib.unified_diff(
            current.splitlines(True), text.splitlines(True),
            "docs/status.json (committed)", "docs/status.json (from inputs)"))
        sys.exit("docs/status.json is stale. Commit the inputs, then run "
                 "python3 scripts/emit_status.py and commit the file.")
    target.write_text(text, encoding="utf-8")
    print("wrote docs/status.json — phase %d of %d (%s), %s, at %s"
          % (phase["number"], len(phases) - 1, phase["name"], state,
             status["generated_at"]))


if __name__ == "__main__":
    main()
