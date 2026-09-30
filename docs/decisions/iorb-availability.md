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

Every change to these rates is announced in an FOMC implementation note, which states the new rate
and the date it takes effect. The case that tests the rule hardest is the unscheduled cut of Sunday
15 March 2020, when the rate was IOER:

- The FOMC statement was released at 5:00 p.m. EDT on 15 March 2020.
  <https://www.federalreserve.gov/newsevents/pressreleases/monetary20200315a.htm>
- The implementation note of the same day set IOER to 0.10 percent, effective 16 March 2020.
  <https://www.federalreserve.gov/newsevents/pressreleases/monetary20200315a1.htm>

Even an emergency weekend cut was announced the day before it took effect. That the effective date
always falls after the announcement is stated here from the form of the implementation notes, not
from a check of each one. The dated IORB table of the later announced-IORB directive checks it row by
row.

Between announcements the rate does not move. On any date, then, the value for that date is the
value most recently announced, and it was announced on an earlier date. The ALFRED vintages recorded
in each field's `revision_evidence` are consistent with this: a vintage routinely carries an
observation dated after the vintage itself.

## What the declaration still withholds

A zero-day lag at `16:15` still prices the value for `d` later than the announcement shows it was
known. The declaration makes it available at 16:15 on `d`, not at the announcement. That is the
safe direction, and closing the remaining gap is not part of this decision.

## A consistency check, not a reason

PR #31's counterfactual run used a registry that differs from `main` only in `IORB.days` and
`IOER.days`, both set to zero. On that run the scouting controls of `docs/pivot/lag-assessment.md`
reproduce: persistence MAE 2.509, and gbm −1.6% against the scouting figure. That agreement is
consistent with the rule, but it is not why the rule holds. The rule rests on the announcement
evidence above and would stand if the controls had not matched.

## What this record does not settle

Whether the announced rate for a date after the decision instant becomes a feature. Such
announced-IORB features are a separate directive, after the re-score.
