# Decision: what a cancelled FOMC meeting contributes, and when it stops

**Status: decided, and prospective.** `fomc_scheduled` is not a declared column, so no published
distribution is built on either reading. This record governs the column's construction before it
exists rather than correcting anything that does.

## The rule

A scheduled meeting of the Federal Open Market Committee contributes to `fomc_scheduled` on every
date from which it was publicly scheduled, and **stops contributing from the moment its cancellation
was publicly known**. A meeting that was scheduled, then cancelled, is therefore present in the
column for part of its life and absent for the rest, and the boundary is the announcement, not the
date the meeting would have been held.

**All eight irregular entries are carried.** There is no selection rule separating regular from
unscheduled meetings, because any such rule would itself be a claim about which meetings the market
was pricing, and the panel has no evidence for that claim.

## The failure it removes

The alternative — a meeting counts for its whole originally scheduled window regardless of what
happened later — prices information no participant had. On any date after a cancellation was
announced, the column would assert a meeting that everyone reading a screen already knew was not
going to happen. That is lookahead in its plainest form, and it is the exact failure the release-lag
machinery exists to prevent everywhere else in the panel; the calendar columns should not be the one
place it is permitted because the calendar feels like something known in advance.

## Why this rule rather than the obvious one

The obvious rule is to drop cancelled meetings entirely. It is wrong in the other direction. Before
the cancellation was announced, the meeting *was* scheduled, and a participant pricing funding
stress that week was pricing a meeting. Dropping it retroactively erases information that was
genuinely available, which is the same sin as adding information that was not — just harder to
notice, because the resulting series looks tidier.

Carrying the meeting up to the announcement and not beyond is the only reading under which every
value in the column is a fact about what was knowable at its own decision time.

## What it decides downstream

This is what makes 2020 usable. A year containing a cancelled-but-scheduled meeting is unusable
under neither of the two clean rules and usable under this one, because this one is the only rule
that can represent a meeting whose status changed mid-life. That is a consequence of the rule, not
a reason for it; the rule would be right if it cost us the year instead.

## Evidence behind the transcription

All eighty scheduled meetings in the transcription match the Federal Reserve's own published
calendar at federalreserve.gov. The availability bound was checked against seven dated announcement
releases and holds on each. The transcription is verified; this record settles only how the verified
material is read.

## What this record does not settle

Whether `fomc_scheduled` earns a place in a declared comparison at all. It has never been scored.
The calendar columns that have been scored are a separate result, recorded with their run, and this
column is not among them.
