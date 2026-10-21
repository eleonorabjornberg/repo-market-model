---
name: daily-decision-message
description: Write Eleonora's one daily decision message (5 pm ET) for repo-market-model and repo-market-liquidity: the scoreboard, her decisions as numbered options with defaults, tonight's Mac runs with their pastes, progress per hypothesis, and the live-log status; then post the day's orchestrator log. Use when the "Daily decision message" routine fires, or when she asks for her batch.
---

# The 5 pm decision message

She asked for one message a day at 5 pm ET (12 October 2026). Run `TZ=America/New_York date` first and use ET times.
Read the top block of #46 (current direction, the scoring protocol gate #640, research plan H1–H10, the five-lens
review #958 as the guiding document), today's comment on the "Orchestrator log" issue (#1044), and the liquidity
orchestrator's 5 pm list if it has arrived.

Collect everything that needs her: `needs-eleonora` issues and PRs; attested actions owed, each with its link and
paste-ready text; escalations; new `avenue` issues from the auditor.

One message, in this order, brief:

1. **Scoreboard.** H5 (primary): spread-distribution CRPS skill against as-of persistence, marked "development, not a
   verdict" unless it comes from protocol confirmation days. H9 (secondary): status. A figure from a provisional
   (calendar-blind) model says so.
2. **Decisions, numbered.** Each with numbered options, your recommendation first, and the default that applies if she
   has not answered by tomorrow's message. The default is never a change to what the project claims
   (`docs/decisions/workflow.md`, "Fewer round trips"). Check each recommendation against the five-lens reports.
3. **Tonight's Mac runs.** Every `needs-mac` directive in either repo whose script is ready and has not yet pushed:
   its full paste (from the PR's `needs-mac:` comment, the `long-run` skill's format), in the order to run them, the
   expected hours, and which can run side by side. Also check every Mac run sent earlier for its results commit on
   its branch, and report any that landed or never ran.
4. **Progress per hypothesis:** milestones done and open, per the manuals in `docs/research/hypotheses/`.
5. **On business days, the live-log status** (#225).

Do not message her separately during the day unless something is time-sensitive.

Then close the day's log: append "<time> ET: sent the 5 pm message" to today's #1044 comment. Rulings stay on their own
issues and results in the research log; the log records only what the orchestrating session did.
