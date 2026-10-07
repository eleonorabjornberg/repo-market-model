# Decision: a bounded, listed defect is handled, not a reason to refuse a series

**Status: decided by Eleonora, 30 September 2026. This record was drafted by a session to record her decision. In force: merged
in PR #51, 30 September 2026.**

## The rule

A defect confined to a **bounded, listed set of days** is documented and handled. It is not a reason to refuse the
series.

- **Handled** means the listed days become **declared holes**: the value on those days is treated as missing and is
  never guessed, repaired, interpolated or carried from a neighbouring day.
- **The list is closed.** It is written in the record that adopts the series. A new defective day, found later, is not
  absorbed: it re-opens the refusal until a reviewed pull request adds it to the list.
- A defect that is not bounded and listed (a level shift, a rewrite across many days, a change of definition) is
  outside this rule, and the series stays refused.

## First application: daily ON RRP (`RRPONTSYD`)

**The list of declared holes: 2020-02-19 and 2020-11-18.** Nothing else.

**Why these days.** The A45 record (the docstring of `tests/test_registry.py`, item 4 of its findings) restates exactly
two dates over the ALFRED vintages of `RRPONTSYD`, and both are days with two operations: an early small value exercise
and the regular operation (95 + 5054 = 5149 million on 2020-02-19; 103 + 0 = 103 million on 2020-11-18). FRED has
alternated between the sum and one leg. This is FRED's aggregation over a two-operation day, not the Desk revising a
print. A45 also finds no accepted amount amended on any single-operation day in any vintage it carries.

**What the pinned snapshot shows**
(`tests/fixtures/snapshots/funding_inputs/fred-macro-latest-vintage/`, file `daily.csv`, column `RRPONTSYD`, billions
of dollars):

| Date | Value in the snapshot | Reading |
|---|---|---|
| 2020-02-19 | 0.095 | the early small leg only; the sum is 5.149 |
| 2020-11-18 | 0.103 | the sum; the other leg is 0, and FRED has also served 0.000 |

The neighbouring days carry ordinary values (2020-02-18: 9.454; 2020-02-20: 3.600; 2020-11-17: 0.000; 2020-11-19:
2.000). In this snapshot 2020-02-19 carries one leg and so understates the day's total by a factor of about fifty, and
2020-11-18 carries the sum. Which reading a vintage serves is not stable, so both days are listed and neither is
guessed.

**What was not verified here.** The snapshot is one latest vintage, so it cannot show the alternation itself; that
evidence is A45's, over the dated ALFRED vintages. This record did not re-fetch anything.

## Consequences (to be implemented by a later directive, not by this record)

- `RRPONTSYD` may be admitted as an input with the two listed days declared as holes. Until that directive lands,
  nothing in the code changes.
- A hole is handled by the as-of rule and the staleness guard like any other missing value; it is not filled.
- Any test that admits `RRPONTSYD` also asserts that the listed set is exactly these two days.
