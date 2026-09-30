# Decision: IORB and IOER for a date are public before that date

**Status: decided and declared.** `metadata/sources.json` prices `IORB` and `IOER` at a
`record_date` lag of zero days. Records scored under the earlier one-day lag are re-scored under
`docs/decisions/information-set.md`, not edited.

## The rule

The interest rate on reserve balances (`IORB`), and before 29 July 2021 the interest rate on excess
reserves (`IOER`), for date `d` is public before `d`. Both fields are declared with
`"days": 0` against `record_date`, at the unchanged `16:15` America/New_York instant.

This supersedes the declaration of 8 September 2026, which priced both fields one calendar day
after their record date as a deliberately conservative choice.

## The evidence

Every change to these rates is announced in the FOMC's implementation note, which states the new
rate and the date it takes effect. The effective date is always later than the announcement:

- A scheduled meeting's implementation note is released on the meeting's final day and sets the
  rate effective the following day.
- An unscheduled change follows the same pattern. The emergency cut of Sunday 15 March 2020 was
  announced that day and took effect on Monday 16 March.
- The rename itself was announced in advance: IOER's last value is dated 2021-07-28 and IORB's
  first is dated 2021-07-29.

Between announcements the rate does not move, so on any date the value for that date is the value
most recently announced, and it was announced on an earlier date. The ALFRED vintages recorded in
each field's `revision_evidence` agree: a vintage routinely carries an observation dated after the
vintage itself.

## What the declaration still withholds

A zero-day lag at `16:15` still prices the value for `d` later than the announcement shows it was
known. The declaration makes it available at 16:15 on `d`, not at the announcement. That is the
safe direction, and closing the remaining gap is not part of this decision.

## A consistency check, not a reason

With the zero-day lag, the scouting controls of `docs/pivot/lag-assessment.md` reproduce through
the repository's own code: persistence MAE 2.509, and gbm −1.6% against the scouting figure. That
agreement is recorded here because it is consistent with the rule. It is not why the rule holds.
The rule rests on the announcement evidence above and would stand if the controls had not matched.

## What this record does not settle

Whether the announced rate for a date after the decision instant becomes a feature. Such
announced-IORB features are a separate directive, after the re-score.
