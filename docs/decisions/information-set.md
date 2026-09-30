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

## What it supersedes

`docs/process/AGENT_CONTRACT.md`'s "The purge stays a scalar", wherever the purge chooses what a forecast reads. The contract's own
as-of rule is unchanged, and this decision is what implements it. The evidence and the alternatives considered are in
[`docs/pivot/lag-assessment.md`](../pivot/lag-assessment.md).

## Decided with it

- **Refit cadence:** records are refitted every 21 scored days, and the cadence is declared in each record.
- **Old records:** records scored under the previous rule move to `docs/runs/archive/pre-asof/`,
  with a README naming the rule they were scored under. The move happens in the re-scoring pull
  request, because the generated pages render from `docs/runs/`.

## Method notes

- **Calibration masking is a calibration bias, not leakage.** A calibrated fit (conformal or
  cross-conformal) scores held-out rows of its own training frame as forecasts, each read as-of its own
  decision instant. The excluding models it trains for them, though, train on the frame as masked at
  the fold's decision instant, not at each held-out row's. A declared column that was public by the
  fold's decision but not yet by a held-out row's can therefore reach an excluding model's training
  rows. No value the forecast itself reads is affected, and nothing public after the fold's decision
  instant is used anywhere. The effect is a possible optimism in the calibration scores, and it is
  limited to declared columns slower than the target (the H.4.1 weeklies, for example). It is
  bounded to those rows and left as is.
