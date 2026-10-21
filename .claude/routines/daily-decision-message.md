# Daily decision message: routine instructions

The "Daily decision message" routine's prompt (`trig_01SoQ913yVPgPkG4boyJdgY9`, 4:52 pm ET, fired into the orchestrating
session), copied from the routine on 21 October 2026. See `README.md`.

---

Daily decision message for Eleonora (she asked for one at 5 pm ET on 12 Oct 2026). Run `TZ=America/New_York date` first and use ET times throughout. Read the scratchpad's orchestrator-state.md, the liquidity orchestrator's 5 pm list if it has arrived, and the top block of the queue issue #46 (current direction, scoring protocol gate #640, research plan H1–H10, and the five-lens review #958 as the guiding document).

Collect every item that needs her:
- needs-eleonora issues and PRs;
- attested actions owed (give the link and paste-ready text);
- escalations;
- new `avenue` issues from the auditor.

Batch them into ONE message, in this order:
1. Scoreboard first:
   - H5 (primary): spread-distribution CRPS skill against as-of persistence. Mark it "development, not a verdict" unless it comes from protocol confirmation days.
   - H9 (secondary) status.
2. Decisions, numbered, each with my recommendation first.
3. Tonight's Mac runs (Eleonora, 19 Oct 2026: "You can send things like this straight to mac, I'll run them overnight"): every `needs-mac` directive in either repo whose script is ready and has not yet PUSHED, each with its full paste (scratchpad mac-<N>.sh; the liquidity orchestrator sends its own), in the order to run them, with the expected hours, and which can run side by side. Also check every Mac run sent earlier for a PUSHED commit on its branch, and report any that landed or never ran.
4. Progress per hypothesis: milestones done and open, per the manuals.
5. On business days, the live-log status (#225).

Keep it brief. Do not ping her separately during the day unless something is time-sensitive.

6. Orchestrator log (Eleonora, 20 Oct 2026). After sending the message, post one comment on repo-market-model issue #1044 ("Orchestrator log"):
- Heading: "## <date> (<first time> to <last time> ET)".
- Content: every line of orchestrator-state.md added since the last comment posted there, verbatim.
- End it with the footer line.
Then add a line to orchestrator-state.md: "<time> ET: posted the day's log to #1044 (<comment URL>)". Rulings stay on their own issues and results in the research log; the log comment only records what the orchestrating session did.
