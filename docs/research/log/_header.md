# Research log

<!-- generated: docs/research/log.md is assembled by `python3 scripts/check_research_log.py assemble` from this
header and the entry files in docs/research/log/. Never edit it by hand. -->

One entry per scored experiment, in the order of the file names under [`log/`](log/) (the entries from before 17
October 2026 first, in the order they were merged; later ones by date, repository and the number in the file name). The plan
is [`plan.md`](plan.md); the format is the constant `ENTRY_FORMAT` in `scripts/check_research_log.py`, which
`python3 scripts/check_research_log.py check` enforces in CI. The same format serves both repositories
(`repo-market-liquidity` results arrive as a fenced `research-log` block copied verbatim from that repository's pull
request body).

**To add an entry (#866), add a file; never edit this page.** Create
`docs/research/log/<YYYY-MM-DD>-<model|liquidity>-<directive issue number, five digits>-<H#>-<step<N>|G<n>>.md`, for
example `2026-10-20-model-01014-H1-step2.md` for directive #1014, holding only the entry: its `### ` heading and its
lines. The directive is an issue its `- Directive:` line names; it exists before the branch is pushed, so the file
never has to be renamed once the pull request is opened. The pull request number in the same place is also accepted
(older entries use it). A liquidity entry copied from that repository's pull request body is a file in the same way,
named `liquidity` and its directive or PR number. A
second entry with the same heading takes `-2` before `.md`. Then run `python3 scripts/check_research_log.py
assemble`, which rewrites this page, and commit it with the regeneration commit like the other generated pages.
Two pull requests that add different files never conflict; a conflict in this page alone is resolved by running
`assemble` again. An entry file already on `main` is never edited, renamed or deleted: the check refuses it.
A wrong pull request number in a frozen entry's heading is corrected in
[`log/_corrections.md`](log/_corrections.md) (#867): `assemble` applies it and keeps the original heading in a
`- Correction:` line.

Heading: `### YYYY-MM-DD [H#] step N · owner/repo#PR` (the date is Eastern time). Groundwork (G1 to G5 in a
hypothesis manual, kept apart from the six steps) has its own heading,
`### YYYY-MM-DD [H#] groundwork G<n> · owner/repo#PR`; an item that covers two pieces of groundwork has one entry each.
Lines: Directive, Step, Tier (`development` or `confirmation`), Pins, Tried, Result, Against kill, Next.

**Backfill, 12 October 2026.** The entries from 10 to 12 October were written after the fact from the pull request
bodies and result pages; every figure is copied as published and nothing is recomputed. They predate the
hypotheses, so the `[H#]` tag and the step are assigned retrospectively (these are the +5 bp classification
experiments that the plan pauses). The "variants" count is the count in that pull request only: no running
count existed before the progress page (#637). Every one of them is development evidence, none is a verdict.
Pull requests #612 and #647 are open and are not backfilled.
