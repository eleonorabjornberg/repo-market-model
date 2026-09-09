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

The date is the commit date of HEAD, never today's date. A status page that can
run ahead of the work it describes is the failure this repository exists to
prevent, and that includes the copy of it published on a website.

Standard library only.

    python3 scripts/emit_status.py            # writes docs/status.json
    python3 scripts/emit_status.py --check    # prints it, writes nothing
"""
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
# optional. Only the exact word "complete" counts as complete: Phase 2 reads
# "(evaluation foundation complete)", which is a partial claim, and reading it
# as a finished phase would advance the published status past the work.
HEADING = re.compile(r"^## Phase (\d+) — (.+)$")
MARKER = re.compile(r"^(.*?)\s*\(([^()]+)\)$")
CRITERION = re.compile(r"^Exit criterion[^:]*:\s*(.*)$")


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
    """The first phase PLAN.md does not call complete, and its state.

    Raising is the point. If PLAN.md will not say that the phase being worked
    is in progress, this file has nothing to publish, and a guess would be the
    hand-written claim the repository exists to refuse.
    """
    done = [phase for phase in phases if phase["marker"] == "complete"]
    outstanding = [phase for phase in phases if phase["marker"] != "complete"]
    if not outstanding:
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
    return current["number"], "in progress"

ROOT = Path(__file__).resolve().parent.parent


def git(*args):
    return subprocess.run(("git",) + args, cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


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

    status = {
        "generated_at": git("log", "-1", "--format=%cd", "--date=short"),
        "commit": git("rev-parse", "--short", "HEAD"),
        "phase": {"number": phase["number"], "name": phase["name"], "state": state},
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
    if "--check" in sys.argv:
        sys.stdout.write(text)
        return
    (ROOT / "docs/status.json").write_text(text, encoding="utf-8")
    print("wrote docs/status.json — phase %d of %d (%s), %s, at %s"
          % (phase["number"], len(phases) - 1, phase["name"], state,
             status["generated_at"]))


if __name__ == "__main__":
    main()
