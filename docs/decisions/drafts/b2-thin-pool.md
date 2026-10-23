# Draft: B2's thin-pool fallback (#1155)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1155, from her ruling of 22 October
2026 on PR #1139 (a separate directive drafts the pool fallback for B2's thin pools). Her ruling of 23 October 2026 on its five questions is recorded under "Answers and the question still open". It binds nothing until she merges it into
`docs/decisions/b2-thin-pool.md` with her own `GO #1155`. Until then the implementation is inert: `repo_model.b2_pool.IN_FORCE`
is `False`, and `protocol_benchmarks.b2_forecast`, the B2 the protocol scores, is unchanged. This is a §13 change to
`scoring-protocol.md` (§4 and the implementation ruling that B2's day type has no minimum sample), and the rule is hers. It
also depends on `docs/decisions/month-end-turn.md` (#1135, in force): its types are that record's.

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
4. **Why 10** (the drafted default; question 1 below re-asks it beside 4). It is below the smallest pool of the two types that recur monthly (`tax_date` 10 to 13, `turn` 12 to 16 in a
   year), so the rule touches only the two types the turn definition made thin and leaves B2 as it is everywhere else. B1'
   uses 30 (#960); at 30, and at 20, every type but `ordinary` falls to all days and B2 stops being a calendar climatology.
   No number is statistically derived: no pool of one year reaches the tails of a 23-level grid. It is a choice, and hers.
5. **Not changed.** Every published record, `protocol_benchmarks.b2_forecast`, the critical values, B1, B1', B3, the lockbox.
   As §13 says, a change applies only to confirmation days logged after it.

## A development reading (no verdict)

`docs/research/b2-pool-fallback-1155-result.md`: B2 without a minimum, with the fallback at 4, 10, 20 and 30, B1 and B1' beside
it, 1,680 decision days (2019-04-03 to 2025-12-23), by regime and pressure-day type, under both hit rules. A minimum of 4 was
added at her ruling of 23 October 2026 (declaration amended before its score). Rates are pooled over the five leads, hit rule
`y > q` (the rule `y >= q` has the same direction, see the page):

| target type (cells) | measure | B2 no minimum | min 4 | min 10 | min 20 = 30 | B1' |
|---|---|---|---|---|---|---|
| year_end (61) | 90% band miss | 0.967 | 0.508 | 0.492 | 0.426 | 0.279 |
| year_end (61) | q95 exceedance | 0.475 | 0.344 | 0.328 | 0.426 | 0.230 |
| quarter_end_turn (200) | 90% band miss | 0.405 | 0.405 | 0.600 | 0.550 | 0.410 |
| quarter_end_turn (200) | q95 exceedance | 0.150 | 0.150 | 0.300 | 0.375 | 0.390 |

At a minimum of 4 only `year_end` changes pool (it reads the `quarter_end_turn` rows, 6 on each scored day);
`quarter_end_turn`, `turn`, `tax_date` and `ordinary` are B2 without a minimum, exactly. It keeps most of the year-end gain
of 10 and none of its harm to the quarter-end turn, because a quarter-end turn is hotter than the turn days that a minimum
of 10 sends it to. Pooled mean grid CRPS: B2 without a minimum 2.531, min 4 2.452, min 10 2.452, min 20 and 30 2.418, B1' 1.715.
All stay far from nominal. The paired test of 4 against B2 without a minimum is `undefined` (the two differ on year-end targets
only). A year-end pool of 6 rows is itself thin, so the minimum of 4 trades a pool of 1 to 2 rows for one of 6. B2 is a
benchmark and no candidate's result chose a number.

## Answers and the question still open

Her ruling of 23 October 2026 (relayed by the orchestrating session), recorded as the text's answers:

2. **Does a step replace the pool, or add to it?** **Answered: (a) replace**, as drafted. (Adding, the union chain, is not
   measured here; a follow-up can.)
3. **Which section 13 kind is this?** **Answered: (a) a reproduced error** in B2's code, justified by Lens C's coverage of
   0.50 on quarter-ends (#762) and the refusal of the first year-end of a panel.
4. **Which hit rule** reads the coverage of B2 (#993)? **Answered: both** are reported; no result here turns on it.
5. **Does B1' keep its own floor of 30,** or take 10 with B2? **Answered: B1' keeps 30.** This draft does not touch it.

Question 1 was answered with the default (a), a minimum of 10 with the chain, and then re-opened on the table above:

1. **Which minimum pool does B2 take, with the chain year_end, quarter_end_turn, turn, all days?** (a) 10, as drafted: it
   helps the year-end and hurts the quarter-end turn (90% band miss 0.405 to 0.600). (b) 4: only the year-end changes pool, the
   quarter-end turn stays as B2 is, and the year-end gain is nearly that of 10 (90% band miss 0.508 against 0.492); its
   year-end pool is 6 rows. (c) 20 or 30: every type but `ordinary` reads all days, which makes B2 nearly the
   unconditional trailing year. (d) No fallback: B2 stays as it is and the first year-end of a panel is refused. **Default:
   (a)**, her earlier ruling, which changes no claim until she merges this text. The table is for her to read; nothing here
   settles it. If she picks (b), `POOL_MIN` and the rule's text change to 4 in the pull request that puts it in force.

## Putting it in force

The pull request that moves this file to `docs/decisions/b2-thin-pool.md` also sets `b2_pool.IN_FORCE = True`
(`tests/test_b2_pool_1155.py` fails if the record and the switch disagree), makes `protocol_benchmarks.b2_forecast` call
`b2_pool.b2_fallback_forecast` or the scorer's callers switch to it, amends §4 and §13 of `scoring-protocol.md`, and carries her
`GO #1155` in `metadata/owner_attestations.json`.
