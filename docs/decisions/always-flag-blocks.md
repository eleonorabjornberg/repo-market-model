# Decision (draft): a flag from an always-flag block is not a warning in tier 1, and is still a false alarm

**Status: DRAFT, for Eleonora's own attested action.** It is in force only once she has merged it, and the option it
describes stays off in the judge in force until she does. The pull request that closes #588 drafted it; the pull request
that closes #685 amends the draft to her ruling of 13 October 2026 on #666 (option B, below). Neither changes
`metadata/pressure_judge.json`, whose in-force version is unchanged.

**Origin:** Eleonora's owner-attested ruling on #570 (comment 6113212773, 11 October 2026, `performed_via_github_app` null,
#256): "if every day in a 21-day block is flagged, the flag is wrong. A flag from a block whose chosen cut-off is at or
below every probability in it does not count as a warning in tier 1. This applies once the amendment drafted under #588 is
merged." This changes a pre-registered test, so it takes effect only by her own action on GitHub.

**Amendment (#685).** The first draft went further than the ruling: it also dropped these flags from the false-alarm count
("neither as a warning nor as a false alarm"), which is what turned `ngboost_laplace` from a fail into a pass (#666). Her ruling
of 13 October 2026 on #666, option B: the flag is not a tier 1 warning, as ruled on #570, but it still counts as a false alarm.
That clause is dropped here. The ruling on #666 was relayed by the orchestrating session; the merge of this record is hers.

## The rule

At each refit the judge chooses one flag cut-off for the next `cutoff_rule.refit_every` scored days (a *block*), at each
threshold and horizon. A block is **always-flag** when the cut-off on its first day is finite and at or below every
probability the row gives in the block, so every day of it flags whatever the model says.

In tier 1 (onset warning), every flag in an always-flag block is **not a warning, and is still a false alarm**: it comes out of
the warnings (and so out of the onsets warned) and stays in the false-alarm count, flat and weighted, exactly as with the option
off. The blocks, the flags dropped from the warnings and the onsets that only those flags warned are listed beside the tier. Cut-offs are chosen as
before (the rule changes what tier 1 counts, not how a cut-off is chosen); tiers 2 to 5, the bar (recall at least 0.5 with
the interval above climatology, at most 2 false alarms per onset), the weighted miss rule and the bootstrap are unchanged.

## How it is built

`Declaration.always_flag_not_warning` (`src/repo_model/pressure_judge.py`), false in the declaration in force, with
`always_flag_blocks` naming a block. It is read by tier 1 only. The single confirmation look refuses it, because that look
is cut to its window and cannot be read in the development blocks. To put the rule in force, the amendment would load the
switch from a key in `metadata/pressure_judge.json` (`tiers.onset_warning`); that edit is left to the merge of this record.

## What it does on the scored days (2018-06-29 to 2025-12-31)

From `docs/pivot/evidence/always-flag-685/` (option B, re-scored under #685 on the judge as it stands after the rulings of 10 October
2026: false alarms pooled across horizons, weighted rule in force), tier 1 at lead of at least 1:

| row | option off | option on |
|---|---|---|
| `ngboost_laplace` | 17 of 26, 2.34 false alarms per onset: fails | 13 of 26, 2.34: **fails** (recall 0.500, interval [0.316, 0.696]) |
| `calendar_climatology` | 12 of 26, 3.90: fails | 2 of 26, 3.90: fails |
| `persistence_logistic` | 12 of 26, 4.09: fails | 4 of 26, 4.09: fails |
| `published_v1` | 14 of 26, 3.06: fails | 8 of 26, 3.06: fails |

The other three rows the #588 measurement scored (`risk_gbm` and the two `risk_gbm` variants) are not re-scored: the option left
their warnings unchanged in that measurement, and the false alarms are now the option-off figures, so their tier 1 rows are
the option-off rows of the #588 table (`docs/pivot/evidence/always-flag/`: 19 of 26, 3.46: fails; 14 of 26, 1.44: passes; 13 of 26,
1.48: passes).

The option moves no verdict among the frozen candidates. `ngboost_laplace` loses 2019-01-15, 2019-01-31, 2019-06-25 and 2019-10-15
and stays a fail on the false-alarm limit; under the first draft it passed only because the dropped flags were also removed from the
false alarms (#666). The benchmarks lose most of their 2019 warnings (calendar climatology 12 to 2, persistence-logistic 12 to 4,
`published_v1` 14 to 8). The #588 evidence is left as it was published; the table above supersedes its option-on column.
