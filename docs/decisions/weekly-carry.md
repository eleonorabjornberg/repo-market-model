# Decision: a weekly column carries its last print forward, under a bound

**Status: decided and implemented.** The guard is
`tests/test_data.WeeklyCarryForwardTests`, and the rule is `build_daily_panel` rule 10. This
record is written after that guard exists, not before it.

## The rule

A grid date with no observation for a **declared carry column** takes the value of the nearest
earlier `ref_date` that has one. The carry never overwrites an observation, stops at the next
one, and stops after a declared maximum staleness, beyond which the cell stays a hole. Carried
cells are counted separately from `holes` and from `settlement_zeros`, because they are a third
fact: a carried cell holds a value, so it is not a hole, but nothing was published for its date,
so it is not an observation of that date either.

## Why this is not the thing rule 4 forbids

Rule 4 says "No forward fill. Absent is not zero and is not yesterday." It is aimed at a series
that should have printed and did not: inventing a value there is inventing data.

A weekly stock variable is a different object. Between prints there is no missing observation —
there is simply the most recent one, which remains the latest published state of the world. The
dealer position does not become unknown on a Thursday; it is what the last print said. Recording
that is not a fill, and refusing to record it does not make the panel more honest, only emptier:
the column was absent on four rows in five.

The bound is what keeps this true. Without one, a feed that stops publishing would carry its last
value indefinitely and the column would silently become fiction. With one, a gap longer than a
tolerated missed print reverts to holes, which is the correct description of not knowing.

## Why the carry is by `ref_date` and not by availability

The first design required a carried cell to post-date its observation's `available_at`, so that
the panel could never show a value before it was published. That was withdrawn, because rule 2
already settles it and settles it the other way: the join does **not** subtract the release lag,
because `splits.rolling_origin` and `event_eval.evaluate_event_window` hold the training rows a
full lag clear of the scored day. Rule 2 names the failure directly — a join that shifted values
by the lag as well "would apply the gap twice". An availability test inside the carry is that
double application wearing a different hat.

Measured, the availability version also failed on its own terms. With FR 2004's six-business-day
lag it filled almost nothing, and where it did fill, the column alternated between a fresh
`ref_date` value and a stale carried one — two time conventions inside one column.

So the carry is uniform with every other column in the panel: indexed by `ref_date`, with
point-in-time discipline enforced where this repository already enforces it, in the purge.

## The bound, and why the release lag is not in it

Thirteen days: seven for the publication interval, doubled to tolerate one missed print, less
one. A Wednesday print carries through the Tuesday before the second Wednesday after it; if
nothing prints on that second Wednesday, the cell is a hole.

One missed print is tolerated because otherwise a single absent print costs a week of holes. Two
are not, because two in a row is a feed with a gap, and a panel should say so rather than paper
over it.

The release lag is deliberately absent from the bound. The carry compares one `ref_date` with an
earlier `ref_date`; adding `worst_case_calendar_days` would bring the lag back into the join
through the bound, which is the same double application in a quieter form.

## What it applies to

The columns the registry declares weekly: `dealer_treasury_position`, and `reserve_balances` and
`tga` when a build prices them. The declaration lives beside the rule in `data.py`, next to
`SETTLEMENT_ZERO_COLUMNS`, because a rule about which columns may carry is a property of the
build and not of the registry.

## What this record does not settle

Whether a carried value should be a *feature* is a separate question from whether the panel
should record it. No published comparison declares this column, and this record makes no claim
about whether one should.
