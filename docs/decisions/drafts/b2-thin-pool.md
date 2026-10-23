# Draft: B2's thin-pool fallback (#1155)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1155, from her ruling of 22 October
2026 on PR #1139 (a separate directive drafts the pool fallback for B2's thin pools). It binds nothing until she merges it into
`docs/decisions/b2-thin-pool.md` with her own `GO #1155`. Until then the implementation is inert: `repo_model.b2_pool.IN_FORCE`
is `False`, and `protocol_benchmarks.b2_forecast`, the B2 the protocol scores, is unchanged. This is a §13 change to
`scoring-protocol.md` (§4 and the implementation ruling that B2's day type has no minimum sample), and the rule is hers. It
also depends on `docs/decisions/drafts/month-end-turn.md` (#1135): its types are that record's.

## The problem

B2 pools the trailing year by day type. Under the month-end turn definition a year holds about two `year_end` days, about six
`quarter_end_turn` days, about sixteen `turn` days and eleven `tax_date` days (smallest pools on the published panel:
`year_end` 1, `quarter_end_turn` 4, `turn` 12, `tax_date` 10). The 23 quantiles of two to six values are interpolations of
them, with 1% and 99% at the sample minimum and maximum (Lens C of the five-lens review, #958; the 90% band covered 0.50 on
quarter-ends, #762). The first year-end target of a panel has no earlier year-end, so B2 refuses it with `ProtocolError`.

## The rule drafted

1. **A minimum pool**, `b2_pool.POOL_MIN = 10`: a target's pool is the first step of its chain with at least 10 rows in the
   trailing year, and every day of the year if none has.
2. **The chain**, by the target's type: `year_end` → `quarter_end_turn` → `turn` → all days; `quarter_end_turn` → `turn` → all
   days; `turn` → all days; `tax_date` → all days; `ordinary` → all days. A step *replaces* the pool; it does not add to it.
3. **As of the decision instant.** The type of a row is a function of its date and the holiday table; the rows counted and
   sampled are those from the start of the window to the anchor, the last public row, and `protocol_benchmarks._require_public`
   restates it (`LookAheadError`). No new source, no publication time, no revision.
4. **Why 10.** It is below the smallest pool of the two types that recur monthly (`tax_date` 10 to 13, `turn` 12 to 16 in a
   year), so the rule touches only the two types the turn definition made thin and leaves B2 as it is everywhere else. B1'
   uses 30 (#960); at 30, and at 20, every type but `ordinary` falls to all days and B2 stops being a calendar climatology.
   No number is statistically derived: no pool of one year reaches the tails of a 23-level grid. It is a choice, and hers.
5. **Not changed.** Every published record, `protocol_benchmarks.b2_forecast`, the critical values, B1, B1', B3, the lockbox.
   As §13 says, a change applies only to confirmation days logged after it.

## A development reading (no verdict)

`docs/research/b2-pool-fallback-1155-result.md`: B2 without a minimum, with the fallback at 10, 20 and 30, B1 and B1' beside
it, 1,680 decision days (2019-04-03 to 2025-12-23), by regime and pressure-day type, under both hit rules. At a minimum of 10
the fallback helps the year-end (90% band miss 0.967 to 0.492, q95 exceedance 0.475 to 0.328, rule `y > q`) and hurts the
quarter-end turn (0.405 to 0.600, 0.150 to 0.300), because a quarter-end turn is hotter than the turn days it is now
forecast from. Both stay far from nominal. Minimums of 20 and 30 are the same rule here. B2 is a benchmark and no candidate's
result chose a number.

## Questions for Eleonora

1. **Adopt a minimum pool and a chain for B2?** (a) Yes, as drafted (minimum 10, the chain above). (b) Yes, with a minimum of
   20 or 30: every type but `ordinary` then reads all days, which makes B2 nearly the unconditional trailing year. (c) No:
   B2 stays as it is and the first year-end of a panel is refused. **Default: (a)**, which changes no claim until she merges it
   and touches only the thin types.
2. **Does a step replace the pool, or add to it?** (a) Replace, as drafted. (b) Add: a `year_end` target reads `year_end`,
   `quarter_end_turn` and `turn` rows together until it has 10, so its own rows stay in. Not measured here: the reading found
   that replacing hurts the quarter-end turn, which is the case for (b), and a follow-up directive can measure it. **Default:
   (a)**, the chain as the directive stated it.
3. **Which §13 kind is this?** The change is neither a demonstration (a) nor a reproduced error (b) as §13 words them, unless
   she reads Lens C's coverage of 0.50 and the refusal of the first year-end as a reproduced error in B2's code. (a) A
   reproduced error, justified by #762 and the refusal. (b) A demonstration, to be written first. **Default: (a).**
4. **Which hit rule** reads the coverage of B2 (#993)? Both are reported; no result here turns on it. **Default: both.**
5. **Does B1' keep its own floor of 30,** or take 10 with B2? B1' is a reference, not a benchmark, and this draft does not
   touch it. **Default: it keeps 30.**

## Putting it in force

The pull request that moves this file to `docs/decisions/b2-thin-pool.md` also sets `b2_pool.IN_FORCE = True`
(`tests/test_b2_pool_1155.py` fails if the record and the switch disagree), makes `protocol_benchmarks.b2_forecast` call
`b2_pool.b2_fallback_forecast` or the scorer's callers switch to it, amends §4 and §13 of `scoring-protocol.md`, and carries her
`GO #1155` in `metadata/owner_attestations.json`.
