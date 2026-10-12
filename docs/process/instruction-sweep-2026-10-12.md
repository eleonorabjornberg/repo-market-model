# Instruction sweep, 12 October 2026 (#641)

Eleonora's order of 12 October 2026: remove antiquated instructions, so that every directive, track, routine and
judge is current. The current direction is the top block of the "Directive queue" issue (#46):

- primary goal H5, the SOFR − IORB spread distribution in bp; secondary goal H9, richer targets;
- the research plan H1–H10;
- the scoring protocol (#640) gates all new scoring;
- new +5 bp classification variants are paused.

This page lists every instruction-bearing document that was read, each statement in it that conflicts with that
direction or points at superseded work, what supersedes the statement, and the action taken. "Drafted" means the change
is not made in the tree: it is a patch under `docs/process/drafts-2026-10-12/` for Eleonora to review and apply,
because the file is hers (`CLAUDE.md`, `.claude/`, `docs/decisions/`).

## Inventory

| Document | Statement | Superseded by | Action |
|---|---|---|---|
| `docs/pivot/next-session.md` | Reading order points to `docs/pivot/plan.md`, `docs/pivot/directives/` and `lag-assessment.md` "why every published record is being re-scored" | #46's top block; the research plan (#638); the scoring protocol (#640) | Rewritten. The order starts with the direction, the plan, the protocol, then `CLAUDE.md`, the information-set rule and the lockbox |
| `docs/pivot/next-session.md` | "The directives, in order": directives 01–06 and "the rest of plan.md §7" | The "Directive queue" issue (#46) | Section replaced by a pointer to the queue |
| `docs/pivot/next-session.md` | "Open for Eleonora": the public pages "corrected from records after directive 03" | Her decisions are batched into one message at 5 pm ET | Section replaced by the batching rule |
| `docs/pivot/next-session.md` | Opening line addresses sessions "in the `rmm` cloud environment" only | The queue is worked by the "Directive loop" routine | Reworded |
| `docs/pivot/plan.md` | "The project's current plan": the headline target is P(SOFR − IORB > +5 bp) and > +10 bp at 1–5 days; §7 is "the sequence" | H1–H10, with H5 primary and H9 secondary; +5 bp variants paused | Moved to `docs/archive/pivot-plan-2026-09-30.md` with a dated note |
| `docs/pivot/directives/01…06` | Briefs for steps of plan.md §7; 01–06 are done | Directives are issues in the queue; a long brief lives in the issue or in the research manuals (#638) | Moved to `docs/archive/directives-2026-09/` with a dated note |
| `docs/pivot/README.md` | "The project's current plan and status"; lists `plan.md` and `directives/` as current | This sweep | Rewritten; the table lists what is in the folder now |
| `docs/archive/README.md` | Says the current state is in `docs/pivot/` | This sweep | Rows added for the moved documents; pointer updated |
| `PLAN.md` | Status block says the current sequence is `docs/pivot/plan.md` and that the page "is revised once the re-score lands" | #46's top block, as Eleonora's decision of 12 October 2026 | Status lines rewritten to record the direction. Phase headings unchanged, so the generated status is unchanged except by its stamp |
| `PLAN.md` | Phase 3 text is silent on H1–H10 and on which repo owns what (#643) | The ruling on #643 and the orchestrator note of 12 October (12:27 pm ET): this repository ingests all data except the H.8 bank groups, the ON RRP offering rate, the SRF rate, the runoff caps and SLR headroom | One paragraph under Phase 3, with the ingestion exception and the both-queues note |
| `docs/decisions/workflow.md` | "Longer briefs live in `docs/pivot/directives/`"; "`docs/pivot/plan.md` §7 is the sequence"; "Directive reviewer" routine; `rmm` environment as the only way to start | The "Directive loop" routine; the research plan | **Drafted**: patch `workflow.patch`. Also adds that a directive names its hypothesis and step, the split by aim (#643) with the data-ingestion exception (12:27 pm ET note), and that the loop works both queues once the liquidity repo's delegated-review change is merged (12:34 pm ET note) |
| `CLAUDE.md` | "Directive reviewer" routine; no pointer to the research plan or to #640 | The "Directive loop" routine | **Drafted**: patch `claude-md.patch`, with the ownership line's ingestion exception and the both-queues note |
| `.claude/skills/directive-orchestrator/SKILL.md` | Starts the "Directive implementer" and "Directive reviewer" routines, which no longer exist; its queue-reading table predates the stacking, claim and hold rules and the current direction | The "Directive loop" routine; #46's top block | **Drafted**: patch `directive-orchestrator.patch` |
| `.github/ISSUE_TEMPLATE/directive.md` | Brief is "a file under docs/pivot/directives/"; no hypothesis field | The research plan | Template edited: brief inline or in `docs/research/`, and a **Hypothesis and step** field |
| `PROJECT_GUIDE.md` | "Still in progress: the pressure model and the scarcity indicator (`docs/pivot/plan.md` §7)"; "Directive reviewer" routine | #46; the "Directive loop" routine | The in-progress bullet repointed to the research plan and the queue; the routine name changed in the sentence about delegated review |
| `README.md` | "This project asks one question: the chance that tomorrow SOFR is more than 5 bp above IORB" | H5 primary; +5 bp variants paused | One sentence added after the question, naming the current primary goal. The generated blocks are untouched |
| `docs/pivot/lag-assessment.md` | Link to `plan.md` §7 | Archive path | Link repointed; the assessment is a finding and a record, kept |
| `docs/pivot/scouting/README.md`, `docs/pivot/*-result.md` | Research records | none | Kept: records of what was measured, not instructions |
| `REPRODUCIBILITY.md` | Build and verify commands | none | Read; no statement conflicts with the direction. Kept |
| `docs/process/AGENT_CONTRACT.md` | Panel schema, the as-of rule, forecast and splitter interfaces | none | Read; the one mention of "headline metric" concerns the scoring holdout and does not conflict. Kept |

## Kept, untouched, and why

- `docs/decisions/information-set.md`: the as-of rule with its leakage and staleness guards.
- `docs/decisions/lockbox.md` and `metadata/lockbox.json`: no comparison scores a locked day.
- The owner-attestation rule (#256), in `docs/decisions/workflow.md` and the loop's prompt.
- The no-AI-attribution rule (6 October 2026).
- `docs/runs/` and `docs/runs/archive/`: published records. They are never edited in place.
- `docs/DATA_QUALITY_DECISIONS.md` and `docs/process/AGENT_CONTRACT.md`: point-in-time data rules, unchanged.
- `METHODOLOGY.md`, `docs/model/validation.md`, `docs/final-test.md` and the pages rendered from records: they describe
  what was measured and cite `lag-assessment.md`, which stays.

## Not done

- No document was deleted. Nothing is scored or published.
- Statements inside `docs/pivot/*-result.md` that call the +5 bp probability "the headline" are records of the
  time. They are not edited.
- `docs/research/plan.md` and the hypothesis manuals (#638) have not merged. `next-session.md` points to the plan
  block at the top of #46 until they do, and says so.
