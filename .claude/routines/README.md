# Routine instructions

Eleonora works with this project in cloud sessions only, so everything a session or routine follows lives in this
repository (Eleonora, 21 October 2026): the routines' instructions here, the subagents in `.claude/agents/`, the skills
in `.claude/skills/`, the hooks in `.claude/hooks/` with `.claude/settings.json`, and the rules in `CLAUDE.md` and
`docs/decisions/`. Nothing a session needs may live only in a routine's prompt, a session's first message, a
scratchpad or a local machine.

| Routine | Trigger | Schedule | Instructions |
| --- | --- | --- | --- |
| Directive loop | `trig_01XHv53KfkiKvWpdWrFTpBYW` | hourly at :13 | `directive-loop.md` |
| Forensic auditor | `trig_01TRY6zjtNXYLcZiqCeu3FCp` | daily 7:45 am ET | `forensic-auditor.md` and `.claude/agents/forensic-auditor.md` |
| Overnight fill and hold check | `trig_012y82obhjNX4rtLGSePfp8N` | hourly at :07 ET, into the orchestrating session | `overnight-fill-and-hold-check.md` |
| Daily decision message | `trig_01SoQ913yVPgPkG4boyJdgY9` | 4:52 pm ET, into the orchestrating session | `daily-decision-message.md` |

**The file is the source; the routine points at it.** Once a file here is merged, its routine's prompt is replaced by
one line: "Read `.claude/routines/<file>` on origin/main of eleonorabjornberg/repo-market-model and follow it exactly."
A change to a routine is then a pull request changing its file, owner-attested like every change under `.claude/`.

**Subagents and skills in a routine run.** A run starts in `/home/user`, above the clones, so the Agent and Skill tools
may not offer this repository's subagents and skills. When they do not, a run starts a general-purpose subagent whose
prompt is the agent file's text with its inputs, and follows a skill by reading its `SKILL.md`.

**Still outside the repository (to move here):**
- the Forensic auditor's original instructions, given in the first message of its session
  (`session_01VeJzV2uWnsr5Ct3SwitkDg`);
- the orchestrating session's scratchpad: `orchestrator-state.md`, `tools/remerge2.sh` and the `mac-<N>.sh` pastes
  for her Mac runs.
