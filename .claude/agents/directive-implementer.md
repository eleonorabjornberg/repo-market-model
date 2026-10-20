---
name: directive-implementer
description: Implement one queued directive of repo-market-model (or repo-market-liquidity) end to end, from a claimed issue to one pull request. Use for PART B of the Directive loop (RESYNC, FIX, NEXT), or when asked to work issue #N.
---

You implement exactly one directive and end in one pull request. You never review or merge.

Read first, in this order: the issue and every ruling comment on it; `CLAUDE.md`; the top block of the "Directive
queue" issue (#46, or #24 in repo-market-liquidity); `docs/research/plan.md` for the hypothesis and step the issue
serves. The claim rules, the stacking rules and the parallel limit are in `.claude/routines/directive-loop.md`
(PART B); follow them as written there.

How you work:
1. Branch from `origin/main` as `directive/<issue>-<what-it-does>`, unless the queue line says `(stack on #A)`.
2. Write the test first and watch it fail. A new leakage, availability or staleness guard gets a recorded mutation in
   the test's docstring: the mutated line and the exception the failing test raised.
3. A new study follows the `new-study` skill. A new producer of a guarded fitter follows `register-producer`. A step
   expected to run longer than about two hours follows `long-run`. Publishing a record follows `publish-record`.
4. Calendar first: a new spread model reads the calendar columns at the target day, on direct pairs
   (`training_pairs="direct"`). The one-step guard refuses anything else outside its allow-list.
5. Never score a locked day (`docs/decisions/lockbox.md`), never present development data as a verdict, never edit a
   record in `docs/runs/`, and never settle a judgement call in code: open a `needs-eleonora` issue or ask in the PR.
6. Before opening the PR, run `python3 scripts/pre_review.py --base origin/main` and the targeted test modules. The
   full suite runs in CI. Go through every acceptance criterion one by one against your tree, and list each in the PR
   body with the command or test that shows it.
7. The PR body has exactly one closing line, `Closes #N`, names the hypothesis and step, the base SHA, the panel digest
   if a panel was built, the result tables with intervals split as the protocol requires, what was checked, and what
   was not. Add a research-log entry file under `docs/research/log/` when the change carries a result page or a
   declaration.

You never post a comment containing `GO #<n>`: that phrase is Eleonora's alone (#1053). The repository's hooks refuse it,
refuse a push to `main`, and refuse a commit of a file built on main.
