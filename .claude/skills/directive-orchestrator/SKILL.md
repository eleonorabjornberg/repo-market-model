---
name: directive-orchestrator
description: Run the directive queue while Eleonora is away. Fire the "Directive loop" routine early when work is waiting, and stop and tell her when the queue needs her. Use when she says she is stepping away, going offline or leaving you in charge of the routines, or asks you to orchestrate or babysit the directive queue.
---

# Directive orchestrator

One routine, "Directive loop", does both jobs: each run first reviews a queued pull request waiting for review, in
either repository, and, if it merges one, implements the next directive (its instructions are in
`.claude/routines/directive-loop.md`). It runs every hour at :13 on its own. You stand in for Eleonora by firing it
early when work is waiting, so a pull request does not sit until the next hour. Routine sessions have no
`fire_trigger`, so a run cannot start the next. Until the loop has GitHub event triggers, that is your whole job.

**Two limits you never cross:**
- **You do not do the routines' work.** You never implement, review, merge or edit code or docs.
- **You do not make her decisions.** You never settle a `needs-eleonora` question or lift a `hold`.

Everything that decides what happens next stays with the routines and with `docs/decisions/workflow.md`
("Delegated review").

## Setup, once per session

1. **Find the routines.** Call `list_triggers` (claude-code-remote MCP server; load it with ToolSearch if it is
   deferred) and take the id of the routine named exactly "Directive loop". Use whatever id you find, since
   recreating a routine changes its id. If it is missing or disabled, tell Eleonora and stop.
2. **Read the state** with the commands below.
3. **Act once** by the table.
4. **Arm the first check-in** with `send_later` (initiation `human_request`, since she asked for this). Put the routine
   id and the session id of any run you fired in the message, so the next check-in knows what it is waiting on.

## Reading the state

GraphQL is blocked in cloud sessions, so porcelain `gh issue` / `gh pr` commands fail with 403. Use REST:

```
R=repos/eleonorabjornberg/repo-market-model
gh api "$R/issues?state=open&per_page=100" -q '.[] | select(.pull_request|not) | select(.title=="Directive queue") | {number, labels: [.labels[].name], body}'
gh api "$R/pulls?state=open&per_page=100" -q '.[] | {number, draft, head: .head.sha, labels: [.labels[].name], closes: ((.body // "") | [scan("(?i)closes #([0-9]+)")[0]])}'
gh api "$R/issues/N" -q '{state, labels: [.labels[].name]}'
gh api "$R/issues/PR/comments?per_page=100" -q '.[] | select(.body | startswith("Review of")) | .body[0:80]'
gh run list --workflow tests.yml --branch main -L 1
```

**Queue items:** the lines `- #N` in the queue body, in order. The *current item* is the first one whose issue is
open.

**Checking on a run you fired:** call `get_session` on the session id that `fire_trigger` returned.

- **Still running:** `status_bucket` is working.
- **Ended:** anything else. Read its closing lines with `list_events` (kinds `assistant` and `result`) before you
  act. The run's own summary often names a blocker the labels do not show yet.

## What to do: the first matching row wins

| State | Action |
|---|---|
| Queue issue closed | Tell her the queue is complete. Stop, without re-arming. |
| Queue labelled `hold`, or any queued PR labelled `needs-eleonora` | Tell her once what is waiting on her, quoting the latest routine comment that explains it. Stop, without re-arming. |
| A run you fired is still running, or the loop's hourly run is due within 10 minutes | Nothing. Re-arm in 15 min. |
| A queued PR is labelled `changes-requested` | Fire the loop. |
| An open, non-draft PR closes a queued issue and has no comment starting `Review of <its head SHA>` | Fire the loop, with the text "PR #n is ready for review". |
| A draft PR closes a queued issue | Fire the loop; it escalates drafts. |
| The current item is open, has no PR and is not `in-progress` | Fire the loop. |
| The current item is `in-progress` with no PR | Nothing: it is being worked, possibly in Eleonora's own session. Idle check-in. |
| Anything else | Idle check-in. |

**Guards on firing:**
- Fire the loop at most once per check-in.
- Never fire it while a run you started is still running.
- If `fire_trigger` is refused, tell her and stop.

## Check-in rhythm

- **After firing, or while a run is going:** re-arm in about 15 minutes.
- **Idle:** re-arm in about 60 minutes.
- **Stop after three idle check-ins in a row,** and tell her in one line that you have stopped and why, for example
  "waiting on #34's PR". Any action or state change resets the count.
- **Stop at once** when she says so, or when she has given the loop GitHub event triggers. Then the
  events do this job.

## Reporting

**Stay quiet** while things move: a fired run, a merge that leads to the next directive.

**Message her only for:**
- something waiting on her;
- the queue finishing;
- a refused tool;
- stopping.

**Keep each message short:** what happened, the PR or issue links, and what she needs to do, if anything.

**If she asks for status,** give:
- the current item;
- the last run and its outcome;
- the next check-in.
