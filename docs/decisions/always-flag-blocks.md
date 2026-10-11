# Decision (draft): a flag from an always-flag block is not a warning in tier 1

**Status: DRAFT, for Eleonora's own attested action.** It is in force only once she has merged it, and the option it
describes stays off in the judge in force until she does. The pull request that closes #588 drafts it; it does not change
`metadata/pressure_judge.json`, whose in-force version is unchanged.

**Origin:** Eleonora's owner-attested ruling on #570 (comment 6113212773, 11 October 2026, `performed_via_github_app` null,
#256): "if every day in a 21-day block is flagged, the flag is wrong. A flag from a block whose chosen cut-off is at or
below every probability in it does not count as a warning in tier 1. This applies once the amendment drafted under #588 is
merged." This changes a pre-registered test, so it takes effect only by her own action on GitHub.

## The rule

At each refit the judge chooses one flag cut-off for the next `cutoff_rule.refit_every` scored days (a *block*), at each
threshold and horizon. A block is **always-flag** when the cut-off on its first day is finite and at or below every
probability the row gives in the block, so every day of it flags whatever the model says.

In tier 1 (onset warning), every flag in an always-flag block counts **neither as a warning nor as a false alarm**. The
blocks, the flags dropped and the onsets that only those flags warned are listed beside the tier. Cut-offs are chosen as
before (the rule changes what tier 1 counts, not how a cut-off is chosen); tiers 2 to 5, the bar (recall at least 0.5 with
the interval above climatology, at most 2 false alarms per onset), the weighted miss rule and the bootstrap are unchanged.

## How it is built

`Declaration.always_flag_not_warning` (`src/repo_model/pressure_judge.py`), false in the declaration in force, with
`always_flag_blocks` naming a block. It is read by tier 1 only. The single confirmation look refuses it, because that look
is cut to its window and cannot be read in the development blocks. To put the rule in force, the amendment would load the
switch from a key in `metadata/pressure_judge.json` (`tiers.onset_warning`); that edit is left to the merge of this record.

## What it does on the scored days (2018-06-29 to 2025-12-31)

From `docs/pivot/evidence/always-flag/result.md`, on the judge as it stands after the rulings of 10 October 2026 (false alarms
pooled across horizons), weighted rule in force, tier 1 at lead of at least 1:

| row | option off | option on |
|---|---|---|
| `risk_gbm+every_day+gate+settle+h41+iorb` | 19 of 26, 3.46 false alarms per onset: fails | same: fails |
| `risk_gbm+settle+h41` | 14 of 26, 1.44: passes | same: passes |
| `ngboost_laplace` | 17 of 26, 2.34: **fails** | 13 of 26, 1.81: **passes**, with recall exactly 0.500, interval [0.316, 0.696] |
| `risk_gbm` | 13 of 26, 1.48: passes | same: passes |

The option moves only `ngboost_laplace` among the frozen candidates: it loses 2019-01-15, 2019-01-31, 2019-06-25 and 2019-10-15,
and, because the blanket blocks also carry false alarms that are dropped, it moves from a fail (false alarms 2.34, over the limit
of 2) to a pass on the recall limit. Eleonora should read that pass for what it is: it rests on the dropped false alarms, and its recall
sits exactly on the bar. The benchmarks lose most of their 2019 warnings (calendar climatology 12 to 2, persistence-logistic
12 to 4, `published_v1` 14 to 8).
