---
name: directive-orchestrator
description: Run the directive queue while Eleonora is away. Start the "Directive implementer" and "Directive reviewer" routines in turn, and stop and tell her when the queue needs her. Use when she says she is stepping away, going offline or leaving you in charge of the routines, or asks you to orchestrate or babysit the directive queue.
---

# Directive orchestrator

You stand in for Eleonora as the one who starts the two directive routines. They cannot start each other: routine
sessions have no `fire_trigger`. Until the routines have GitHub event triggers, someone has to notice when a run ends
and start the next. That is your whole job.

**Two limits you never cross:**
- **You do not do the routines' work.** You never implement, review, merge or edit code or docs.
- **You do not make her decisions.** You never settle a `needs-eleonora` question or lift a `hold`.

Everything that decides what happens next stays with the routines and with `docs/decisions/workflow.md`
("Delegated review").

## Setup, once per session

1. **Find the routines.** Call `list_triggers` (claude-code-remote MCP server; load it with ToolSearch if it is
   deferred) and take the ids of the routines named exactly "Directive implementer" and "Directive reviewer". Use
   whatever ids you find, since recreating a routine changes its id. If either is missing or disabled, tell Eleonora
   and stop.
2. **Read the state** with the commands below.
3. **Act once** by the table.
4. **Arm the first check-in** with `send_later` (initiation `human_request`, since she asked for this). Put the routine
   ids and the session id of any run you fired in the message, so the next check-in knows what it is waiting on.

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
| A run you fired is still running | Nothing. Re-arm in 15 min. |
| A queued PR is labelled `changes-requested` | Fire the implementer. |
| An open, non-draft PR closes a queued issue and has no comment starting `Review of <its head SHA>` | Fire the reviewer, with the text "PR #n is ready for review". |
| A draft PR closes a queued issue | Fire the reviewer; it escalates drafts. |
| The current item is open, has no PR and is not `in-progress` | Fire the implementer. |
| The current item is `in-progress` with no PR | Nothing: it is being worked, possibly in Eleonora's own session. Idle check-in. |
| Anything else | Idle check-in. |

**Guards on firing:**
- Fire at most one routine per check-in.
- Never fire a routine while a run of it that you started is still running.
- If `fire_trigger` is refused, tell her and stop.

## Check-in rhythm

- **After firing, or while a run is going:** re-arm in about 15 minutes.
- **Idle:** re-arm in about 60 minutes.
- **Stop after three idle check-ins in a row,** and tell her in one line that you have stopped and why, for example
  "waiting on #34's PR". Any action or state change resets the count.
- **Stop at once** when she says so, or when she has recreated the routines with GitHub event triggers. Then the
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
