# Drafts for Eleonora, 12 October 2026 (#641)

These three patches change files that are hers: `CLAUDE.md`, `docs/decisions/workflow.md` and
`.claude/skills/directive-orchestrator/SKILL.md`. They are **drafts**. Nothing here is in force until she applies them
herself. `docs/process/instruction-sweep-2026-10-12.md` is the inventory that led to them.

Apply from the repository root, after reviewing:

```
git apply docs/process/drafts-2026-10-12/claude-md.patch
git apply docs/process/drafts-2026-10-12/workflow.patch
git apply docs/process/drafts-2026-10-12/directive-orchestrator.patch
```

| Patch | What it changes |
|---|---|
| `claude-md.patch` | Adds a "Direction" section (the top block of #46, the research plan, the scoring protocol, the split by aim, #643); names the "Directive loop" routine in place of "Directive reviewer" |
| `workflow.patch` | A directive names its hypothesis and step; the roadmap is the research plan; the "Directive loop" routine in place of "Directive reviewer"; a "Split by aim" record (#643) |
| `directive-orchestrator.patch` | Rewrites the orchestrator skill for the "Directive loop" routine, the top block of #46, the 5 pm ET decision message, the no-attribution rule and the attested-action relay format |

If the patches no longer apply because the files moved on, regenerate them from the inventory.
