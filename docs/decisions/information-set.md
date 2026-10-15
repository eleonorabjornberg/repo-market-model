# Decision: a forecast uses exactly the information public at its decision instant

**Status: decided and implemented** (#27; the guards are `repo_model.asof`). Every record scored
under the previous rule was re-scored or archived.

> **Proposed in #267, for Eleonora to review:** the corrected wording of rule 1 below (the H.4.1
> read lag). A decision is in force only once she merges it.
>
> **Proposed in #541, for Eleonora to review:** the wording of rule 1's H.4.1 sentence and of rule 2's
> Treasury-settlement bullet, which record her ruling of 10 October 2026 (relayed on #541): a settlement
> is dated from the auction announcement, not the auction results, and the H.4.1 is read per release, at
> the release's own publication instant. It was drafted by the pull request that closes #541 and is **not
> in force** until she merges it. Both readings are measured and off in the published registry:
> `metadata/sources.json` is frozen by the final-test pre-registration (bytes), so turning either on is a
> later pull request, with the re-pin that needs, made after her ruling on it.
>
> **Proposed in #586, for Eleonora to review:** the amendment at the end of this record, which records her
> ruling of 11 October 2026 on #571 (relayed by the orchestrating session): the reserve-scarcity state reads each
> of its legs at its own latest public row. It was drafted by the pull request that closes #586 and is **not in
> force** until she merges it.

## The rule

A forecast for scored day `T` is made at the declared decision time on the last panel day before
`T`, called the decision instant.

1. **Each input is read per field, at its latest value whose declared first-observable instant is at
   or before the decision instant.** The declarations are the registry's own `release_lag` blocks,
   read through `baseline._declared_availability`. Under them, the daily NY Fed rates and bill rates
   are read at the row two panel days before `T`. The H.4.1 weekly series are read per release: a
   Wednesday level is first observable at the print of its own release, the Thursday after the Wednesday
   at 16:30 New York time, or the date the Board moved the release to when a holiday moves it (the
   Board's release pages are the evidence, recorded with the declaration). Each Wednesday level is carried
   on the rows after it (`weekly-carry.md`), and a forecast reads it from the first decision at or after
   the print and never before. A newer print that was public at the decision is read, not left unread.
   A record's `hours_observable` counts from the observation row's declared instant and says so.
2. **Values that refer to `T` itself are admissible only as declared scheduled inputs**, meaning a
   value announced before the decision instant. That covers:
   - the calendar columns, which are always known;
   - FOMC schedules, under `docs/decisions/fomc-point-in-time.md`;
   - Treasury settlements, under a `treasury_auctions` availability declaration dated from the
     auction announcement: each settlement's first-observable instant is the announcement time of its
     auction. Treasury publishes no clock time for an individual announcement, so the declared
     instant and what it rests on are recorded as evidence in the declaration. The risk-date calendar then marks a settlement as known at the
     decision instant from the day it is announced.
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
[`docs/pivot/lag-assessment.md`](../pivot/lag-assessment.md). That assessment's §4 verdicts were not re-measured
when the feature set was fixed; re-scoring them belongs with next-version research.

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

## Amendment: back-filled repo-rate history is training history only (#374, #430)

The snapshot and the guard are merged. **Posting instant established: 2018-05-17** (the start of that day, New York
time) for TGCR, BGCR and SOFR, by her ruling of 13 October 2026 on PR #661 (#633); the source is
`metadata/backfill_posting.json`. The amendment is in force from the merge of the pull request that closes #734.
Eleonora ruled on 8 October 2026 (#374) that the New York Fed's
back-filled history of SOFR, TGCR and BGCR may be used as training history. The Bank's reference-rate
API begins on 2018-04-02. For the months before it, the Bank published a workbook of indicative values
of the same three rates and their volumes, computed after the fact on the same method, from 2014-08-22
to 2018-03-29. It carries no percentiles. Its source, checksum and what is known of its publication date
are in `docs/pivot/backfilled-history-result.md`.

1. **A back-filled value is training history.** It may sit in a fold's training frame, for a day before
   2018-04-03, the first day the API serves. Rule 3 above is unchanged: a training target is admissible
   only if it was observable by the fold's decision instant. The workbook's own properties date it May
   2018, before the first scored decision instant; the Bank's original posting date is not recorded in
   the file (see the result page).
2. **It is never an as-of input at a scored decision instant.** No scored day is a back-filled day, and
   no scored forecast is conditioned on a back-filled row (its feature date is a published day).
   `repo_model.backfill.require_training_only` raises `LookAheadError` for a backtest in which either
   is not so.
3. **Nothing published moves.** No declaration in `docs/runs/` reads the back-fill, and the published
   panel (digest in `metadata/funding_panel_manifest.json`) does not carry it. A model that trains on it
   is a scratch measurement until a later decision puts it in a declaration.
4. **The other inputs of the earlier months** (bill rates, Treasury auctions, the Desk's ON RRP results,
   the H.8 first prints; FRED's reserves, TGA and IOER and the FR 2004 extract already reach back) are
   fetched from their own sources for the same dates and carry the same rule. The calendar columns of
   those months use the workbook's own publication days as the business-day schedule, because the market
   holiday table begins on 2018-01-01.

## Amendment: the scarcity state reads each leg at its own latest public row (#571, #586)

**Proposed, for Eleonora to review. Not in force until she has merged it.** Eleonora ruled on 11 October 2026
(#571; the ruling was relayed by the orchestrating session) that the reserve-scarcity state
(`repo_model.scarcity`, #115) may be assembled from more than one row.

1. **Each leg is read at its own latest public row.** The state's three legs are the reserves (the H.4.1's
   WRESBAL), the H.8's total assets and the day's ON RRP. As of a forecast's decision instant, each is read
   at the latest row whose own declared first-observable instant is at or before it (rule 1 above, per
   field), and the state is formed from the three reads. The ratio's legs may then belong to different
   weeks, and the ON RRP leg is no older than the Desk's declared lag; the H.8's lag no longer sets the row
   the other two are read at.
2. **Each read passes the usual guards.** Every leg passes the availability check (`LookAheadError` for a read
   newer than the decision instant) and the staleness check (`StaleReadError` for a read older than the
   latest admissible row), through `InformationRule` (rule 5 above), and `scarcity._require_public_legs`
   restates the first for the three legs. A leg that is a hole at its row leaves the state a hole.
3. **The scope is this indicator only.** This replaces the rule that an indicator is "never assembled from two
   rows" for the scarcity state, and for no other feature. No other input, threshold, cut-point, onset
   definition or availability time changes.
4. **Where it is in force.** `scarcity.own_leg_states` is the state the judge reads (`pressure_judge.py`,
   `_scarcity_states`), and `scarcity.own_leg_composition` reads it as a composed feature in a measurement run,
   which is how a model that takes the state as an input is fed it. `asof.py` and `contract.py` are not edited:
   they are in the final test's pipeline checksum, and the published declaration, the published panel and the
   pre-registered model are unchanged. The same-row read (`with_reserve_scarcity_state`, the column) is kept
   for the published map's off declaration and for the before-and-after count. Whether the own-leg read
   replaces it in `contract.py`, which would move that checksum, is not decided here.
