# Draft: a start-up cut-off for the pressure-day judge (#584)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #584, as that directive asks. It
changes a pre-registered test (the judge's flag cut-off rule), so it takes effect only when she acts herself on GitHub: a
comment, review or label by her whose `performed_via_github_app` is null (`docs/decisions/workflow.md`, owner-attested items;
#256). A relayed ruling does not put it in force. **This pull request does not change `metadata/pressure_judge.json`; the
in-force judge, its cut-off rule and its version are exactly as they were.** The measurement behind the draft is
[`docs/pivot/startup-cutoff-result.md`](../../pivot/startup-cutoff-result.md); the declaration of the two rules measured is
`metadata/startup_cutoff_584.json`, committed before any score under them.

## The problem

The judge chooses each refit block's flag cut-off from the forecast's own earlier walk-forward probabilities and the outcomes
known at the block's first decision instant (`cutoff_rule`, `training_window`). A block whose training window holds no onset
flags nothing (`no_onsets: never_flag`). In 2018 almost every block has no onset in its window, so no 2018 onset can be warned
whatever the forecast: 36 percent of the 2018-19 model-row cells have no cut-off (#560, PR #564). All four 2018 onsets are
therefore missed by every row, by construction, and the 2018 recall says nothing about a model.

## What would be amended

In `cutoff_rule`, one new key, `startup`, and a sentence in `no_onsets`. Everything else in the rule (the refit every 21 days,
the training window, the limit of 2 false alarms per onset, the weights of the weighted miss rule) is unchanged.

```json
"cutoff_rule": {
  "...": "unchanged",
  "no_onsets": "startup",
  "startup": { "...": "ONE of the two options below, or none" }
}
```

The start-up rule applies to a block, at a threshold, only while the block's training window holds no onset. The moment the
window holds one onset the cut-off rule above takes over for that block and every later one, and its result stands even when it
is `never_flag` (no cut-off within the limit reaches an onset). The two options measured:

* **Option A, climatology rate.** The block's cut-off is the share of the window's scored days that are pressure days (the
  probability a climatology fitted to the window gives); a window with no pressure day flags nothing, as now. Code:
  `pressure_judge.StartupRule("climatology_rate")`. It reads the window's pressure-day labels, all known at the refit, and
  `startup_cutoff` refuses (`LookAheadError`) a day after the training end.
* **Option B, fixed probability.** The block's cut-off is a constant, 0.2 (the placeholder the judge was first declared with
  before any candidate was scored, #375), read from no outcome. Code: `pressure_judge.StartupRule("fixed_probability", 0.2)`.
  The directive's alternative, a probability chosen from the 2014-2018 back-filled history, is not offered: the guard of #572
  refuses a fit trained on a back-filled value while the workbook's posting instant is unestablished
  (`metadata/backfill_posting.json`, `posting_instant` null), and `docs/decisions/information-set.md` bars its use as
  training history until that date is established.

`choose_cutoffs` takes the rule as an optional argument (`startup=`), and the default is none, so merging the code changes no
figure. Putting a rule in force is a second, separate act: setting `startup` in `metadata/pressure_judge.json` and re-scoring
the records that the change moves (a published record is never edited in place: `CLAUDE.md`).

## What the measurement says (details and tables on the result page)

The result page gives the numbers; the draft states the reading it supports and what it does not.

* The rule matters only for 2018 and only for the cut-off. Nothing after 2018 changes under either option. Under the
  weighted rule in force no tier verdict changes under either option; tier 3 and tier 5 fail for all three frozen rows. Under
  the flat rule both options take `risk_gbm+settle+h41` out of tier 1 (pooled false alarms per onset 2.00 to 2.54 and 2.12),
  because the false alarms added in 2018 are pooled into the count.
* **A pass on these days is not a confirmation** (Eleonora's ruling of 11 October 2026 on #567): the 2018 onsets were seen when
  the rules were chosen, the three rows were frozen on 2018-2025, and neither option can be confirmed except on the blind tier.
* Neither option is a measure of a model's skill on those onsets. Under Option A the benchmarks flag the same two 2018 onsets
  as the two risk-date rows (with 58 and 68 false alarms added), and the one frozen row that gains nothing, `ngboost_laplace`,
  loses ground against them. Option A applies at one horizon (h = 2) and rests on one pressure day (2018-07-02); Option B warns
  no 2018 onset and adds false alarms.

## What is for Eleonora

1. Whether to adopt Option A, Option B, or neither. This is a change to a pre-registered test.
2. If adopted, the judge version and the records to be re-scored (the live record and the pin are not touched by this draft).
3. Whether 2018 should instead be reported as "no cut-off available" and left out of tier 1's recall (the other way to remove
   the artefact), which needs no new rule but changes what the 26 onsets are.

Nothing in this draft moves a published figure. It does not open any part of the lockbox.
