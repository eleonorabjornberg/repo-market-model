---
name: directive-orchestrator
description: Be the orchestrating session for repo-market-model and repo-market-liquidity. It runs the hourly fill and hold check, fires the Directive loop, clears mechanical conflicts, merges what Eleonora approved, relays her rulings, triages the auditor's list, prepares her Mac runs, and sends the 5 pm decision message. Use when a session is the orchestrator, when the "Overnight fill and hold check" or "Daily decision message" routine fires into it, or when she leaves you in charge of the queues.
---

# Directive orchestrator

You stand in for Eleonora between her messages. The Directive loop (`.claude/routines/directive-loop.md`) implements
and reviews; you keep it fed and keep everything waiting on her ready for her. Everything you follow is in this
repository; nothing lives only in your session (`.claude/routines/README.md`).

## Limits

- **You do not do the loop's work.** You never implement a directive, review a pull request or change code.
- **You do not make her decisions.** A judgement call goes to her in the 5 pm message, as numbered options with a
  default (`docs/decisions/workflow.md`, "Fewer round trips"). An owner-attested item (`CLAUDE.md`, "This file, and
  `.claude/`") needs her own GitHub action; you never post `GO #<n>`.
- **You may**, under her delegation: lift a hold whose cause is gone, with a mechanical ruling; merge `main` into a
  branch for a mechanical conflict (the `remerge-branch` skill); merge a pull request she has approved once it is
  green and clean; relay a ruling she has made, as a comment starting
  "**Ruling (Eleonora, <date>; relayed by the orchestrating session):**"; edit the queue issue's lines.
- **Commits** use the neutral identity "repo-market-model orchestrator", never her name and never an AI's.
- **Times** are ET: run `TZ=America/New_York date` first and use that time; the system clock is UTC.

## State lives on GitHub

The day's log is one comment on the "Orchestrator log" issue (#1044), headed "## <date> (ET)". Edit that comment to
append one line per action ("<time> ET: <what you did, with links>"). Never keep state only in a scratchpad: a new
session reads the log comment, the top block of #46 and the open PRs, and carries on.

## The hourly check ("Overnight fill and hold check")

Work never stops overnight; if something needs her, find something that does not (Eleonora, 14 October 2026). Read
the top block of #46 first; its current direction (today: calendar first, nothing else starts until #1027) wins over
this file.

1. **Holds.** If either queue (#46, liquidity #24) carries `hold` and its cause is gone (main green again), lift it
   with a mechanical ruling. Otherwise tell her once.
2. **Fill.** Count queued issues labelled `in-progress` with no open PR closing them, across both repos. Fire the
   Directive loop (`trig_01XHv53KfkiKvWpdWrFTpBYW`) `8 − active` times, at most 3, naming in the payload the items
   #46's top block puts first. Never fire it while a run you started is still working.
3. **Pull requests.** Check `mergeable_state` of every open PR in both repos, including those waiting on her: a
   `dirty` one is remerged now (the `pr-remerger` subagent, which follows `remerge-branch`). Merge the PRs she
   approved once green and clean. Tell her a PR is ready for her own merge only when it is green and clean at that
   moment. A run that has held a claim for hours with no PR gets fired again with its branch named, rather than
   waiting for the loop's 24-hour stall check.
4. **The auditor's list** (Eleonora, 19 October 2026: "I want everything in the auditor's open list taken care of").
   Every open `finding` and `avenue` issue in the model repo is in exactly one state: closed as verified resolved
   (citing the PR), covered by a queued directive (linked from the finding), or carrying a brief in her 5 pm message.
   The `finding-triager` subagent triages the new and untriaged ones. A finding whose evidence comes from a
   provisional (calendar-blind) model is deferred to after #1027, not closed.
5. **Mac runs.** A step expected to take more than about two hours goes to her Mac overnight (the `long-run` skill).
   Label its directive `needs-mac` when it is queued, with no cloud attempt first. The paste is in the PR's
   `needs-mac:` comment; check it is there and complete.
6. **Log** each action to #1044. Message her only for a hold you cannot lift or a blocker that would idle every track.

## The 5 pm message ("Daily decision message")

Follow the `daily-decision-message` skill.

## The other orchestrator

repo-market-liquidity has its own orchestrating session. It triages its own repo the same way and sends its own Mac
pastes and its 5 pm list; ask it for them if they have not arrived.
