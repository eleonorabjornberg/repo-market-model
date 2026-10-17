# Research log

One entry per scored experiment, newest last. The plan is [`plan.md`](plan.md); the format is the constant
`ENTRY_FORMAT` in `scripts/check_research_log.py`, which `python3 scripts/check_research_log.py check` enforces in
CI. The same format serves both repositories (`repo-market-liquidity` results arrive as a fenced `research-log`
block copied verbatim from that repository's pull request body).

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
