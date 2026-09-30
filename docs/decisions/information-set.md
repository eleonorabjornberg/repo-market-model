# Decision: a forecast uses exactly the information public at its decision instant

**Status: decided, not yet implemented.** The implementing pull request lands the guards, and
every record scored under the previous rule is re-scored or archived.

## The rule

A forecast for scored day `T` is made at the declared decision time on the last panel day before
`T`, called the decision instant.

1. **Each input is read per field, at its latest value whose declared first-observable instant is at
   or before the decision instant.** The declarations are the registry's own `release_lag` blocks,
   read through `baseline._declared_availability`. Under them, the daily NY Fed rates and bill rates
   are read at the row two panel days before `T`, and the H.4.1 weekly series at their latest print.
2. **Values that refer to `T` itself are admissible only as declared scheduled inputs**, meaning a
   value announced before the decision instant. That covers:
   - the calendar columns, which are always known;
   - FOMC schedules, under `docs/decisions/fomc-point-in-time.md`;
   - Treasury settlements, under a `treasury_auctions` availability declaration dated from the
     auction results time. That declaration is approved, and its exact instant is taken from
     Treasury's published auction procedure and recorded as evidence in the declaration.
   Each scheduled input passes the same availability check as any other input.
3. **A training target is admissible only if it was observable by the fold's decision instant.**
   This replaces the purge as the rule for training labels.
4. **The purge does not choose the feature row**, and the fold grid does not depend on which features a
   declaration names. Every declaration is scored on the same grid, so any two are paired by construction.
5. **Both directions are guarded.** Nothing read may be newer than the decision instant (leakage).
   No admissible value may be newer than the one read (staleness). A record reports each field's
   staleness at the decision instant.

## What it replaces, and why

`AGENT_CONTRACT.md`'s own as-of rule already says a row is eligible only if its `available_at` is at
or before the cutoff. The implementation instead converted each source's business-day release lag
into calendar days at its worst case. For SOFR that is one business day becoming six calendar days.
It then used the result as one purge, both to trim training rows and to choose the feature row. So
every forecast read its inputs four or five business days before the scored day, on every day, to
cover the worst holiday week. Declaring a slow series widened the purge further and made every other
input staler with it.

That design was leak-free and needlessly stale. The leakage guards could not see the problem,
because they only ask whether a value read was already public. They never ask whether a newer one
was. This decision supersedes `AGENT_CONTRACT.md`'s "The purge stays a scalar" wherever the purge
chooses what a forecast reads.

## Decided with it

- **Refit cadence:** records are refitted every 21 scored days, and the cadence is declared in each record.
- **Old records:** records scored under the previous rule move to `docs/runs/archive/pre-asof/`,
  with a README naming the rule they were scored under. The move happens in the re-scoring pull
  request, because the generated pages render from `docs/runs/`.
