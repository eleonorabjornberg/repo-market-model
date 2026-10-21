# Forensic auditor: routine instructions

The "Forensic auditor" routine's prompt (`trig_01TRY6zjtNXYLcZiqCeu3FCp`, daily 7:45 am ET, `rmm` environment). Its
instructions, including those first given in its session's first message, are in `.claude/agents/forensic-auditor.md`
(copied there on 21 October 2026). See `README.md`.

---

Run today's forensic audit of eleonorabjornberg/repo-market-model and eleonorabjornberg/repo-market-liquidity exactly as `.claude/agents/forensic-auditor.md` on origin/main of repo-market-model says, including part 2, "Untried avenues". All times in ET. Run it through the `forensic-auditor` subagent (the Agent tool). If the Agent tool does not offer it (a run starts in /home/user, above the clones), start a general-purpose subagent whose prompt is that file's text, or do the audit yourself. Say in the digest's last line which of the three ran it. If GitHub returns 403, say so in one line and stop.
