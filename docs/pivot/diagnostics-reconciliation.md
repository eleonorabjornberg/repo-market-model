# Reconciliation of counts and definitions across the diagnostic result pages (#503)

A reading of text, not a measurement. It changes no model, rule, threshold, declaration or published figure, writes nothing
into `docs/runs/`, and scores no day (the evidence it uses is the tracked evidence of the pages themselves, and the published
panel, which it reads only to list its rows). The nine disagreements the directive lists are given below with the value each
page uses, the value the code and the tracked evidence support, and the command that shows it. Where a page stated something
the evidence does not support, the page carries a dated note at that point (10 October 2026, #503). Where a figure differs only
by convention, the page carries a note naming the convention. Pages that need no change are not touched.

The pages: `source-screen-result.md` (#478), `pressure-audit-result.md` (#473), `desk-standard-result.md` (#481),
`construction-gaps-result.md` (#485), `setup-diagnostic-result.md` (#480), `setup-sensitivity-result.md` (#482),
`episode-post-mortem-result.md` (#474) and `weighted-miss-result.md`.

## The conventions to use from now on

These are conventions of wording, so that the next pages and the combined diagnostics summary rest on one set of numbers.
They are proposed by this note for the pages it reconciles; no rule or declaration reads them.

1. **Two scored grids, named.** The *h = 1 grid* is the 1,873 days 2018-06-29 to 2025-12-31 that horizon 1 scores. The *shared
   grid* is the 1,869 days 2018-07-06 to 2025-12-31 that every horizon from 1 to 5 scores; the judge's tier 1, tier 3 and tier 5
   are read on it. A figure with no qualifier means the shared grid. A figure on the h = 1 grid says so ("on the h = 1 grid").
2. **Onsets: 26 on the shared grid, 27 on the h = 1 grid.** The definition is one: SOFR − IORB strictly above +5 bp, with no such day
   on the five panel days before (`pressure.onsets`, `ONSET_QUIET_DAYS = 5`). The 27th is 2018-06-29, scored at h = 1 only.
   Per horizon the counts are 27, 26, 26, 26, 26. "Of 26" is the tier 1 denominator.
3. **2018 has four onsets on the shared grid, five on the h = 1 grid** (the five are 2018-06-29, 11-15, 11-30, 12-17, 12-28).
4. **"Blind" names one thing: the flag cut-off in force on the day is infinite** (`cutoff_rule` in `metadata/pressure_judge.json`:
   `no_onsets` and `none_meets_limit` both `never_flag`), so the row cannot flag whatever its probability. Say "blind (no onset in
   the window)" for the first cause and "blind (no cut-off within the limit)" for the second. Two other things are not called
   blind: a risk-date model's probability of exactly 0 off a risk date is **silent** (the post-mortem's word), and a panel defect
   such as a copied row is an **input defect** (`setup-diagnostic-result.md`'s "would blind a model" flag).
5. **"The tier-1 passers" are the five risk-date severity models of #428** that pass tier 1: `risk_gbm`, `risk_gbm_base`,
   `risk_logistic`, `risk_logistic_base` and `risk_quantile_skewt_base`. The five rows of `setup-sensitivity-result.md` are the
   five *best-recall rows* of the judge's declared candidates (`two_part_gbm`, `ngboost_laplace`, `hierarchical_logistic`,
   `settlement_quantile_timing`, `scarcity_logistic_interactions`); none passes tier 1, and the page should not be read as a
   statement about the passers.
6. **"Episode" is always stated with its calm-day count.** The judge's onset is an episode with five calm panel days before it
   (26 on the shared grid). A maximal run of consecutive pressure days is the one-calm-day episode (46 on the shared grid, 47 on the
   h = 1 grid).

## The nine points

### 1. Onsets: 26 or 27

`source-screen-result.md` says 27, the others 26. Both are right on their own grid. `evidence/desk-standard/desk_standard.json`,
`onset_count`: `onsets_by_horizon` is `{1: 27, 2: 26, 3: 26, 4: 26, 5: 26}` and `onsets_at_h1_not_at_every_horizon` is
`["2018-06-29"]`. The screen scores the h = 1 grid at every lead (`evidence/source-screen/screen.json`, `scope.onsets` lists 27
dates, `scope.scored_days` is 1873), so its 27 and its 140 pressure days are the h = 1 grid's; on the shared grid they are 26 and
138 (below, point 2). Convention: item 2 above. `source-screen-result.md` carries a note.

### 2. First scored day

| page | says | supported |
|---|---|---|
| most pages | 2018-06-29 | the first day of the h = 1 grid, and the declared window start |
| `pressure-audit-result.md`, `setup-diagnostic-result.md` | 2018-07-06 (1,869 days) | the first day of the shared grid |
| `construction-gaps-result.md`, gap 4 | 2018-06-27 | **wrong as stated**: 2018-06-27 is the first *feature* date of the first fold, not a scored day |
| `desk-standard-result.md` | 2018-06-28, 1,874 decision days | **off by one day**: see below |

The evidence: the backtest of `REPRODUCIBILITY.md` (`backtest … --model persistence --minimum-history 61 --refit-every 21 --end
2025-12-31`) writes `folds.first = {feature_date: 2018-06-27, scored_date: 2018-06-29, train_end: 2018-06-27, train_rows: 61}` and
`folds.count = 1873`. A scored day is read two panel rows after its feature date (rule 1 of `information-set.md`: the daily NY Fed
rates are read two panel days before the scored day), so the first scored day at h = 1 is 2018-06-29. The first scored day per
horizon is 2018-06-29, 07-02, 07-03, 07-05 and 07-06 for h = 1 to 5, with 1,873, 1,872, 1,871, 1,870 and 1,869 scored days
(`desk_standard.json`, `onset_count.scored_first_day_by_horizon` and `scored_days_by_horizon`); the shared grid is the last
(`evidence/pressure-audit/score.json`, `provenance.scored_window` and `common_days`; `evidence/setup-diagnostic/setup_diagnostic.json`,
`scored_window`).

`desk-standard-result.md` counts "1874 decision days from 2018-06-28" (`scripts/desk_standard_diagnostic.py:401`: every calendar row
from 2018-06-28). The decision day of the first scored day (2018-06-29) is 2018-06-28, so the start is right, but the count runs to
2025-12-31, and the decision day 2025-12-31 serves a scored day (the next panel day, 2026-01-02) outside the window. The decision days that serve a
scored day at h = 1 are 1,873. The 710 "newer print public and unread" is over 1,874 days; the share it gives would move by at most
one day. `information-set.md` rule 1 counts "795 of 2042 scored days": 2042 is the whole panel, which runs to 2026-09-03 and so
includes the opened near-blind tier; it is a different scope, not a different count of the same days.

The same grid difference puts 2018-19 at 375 days on the h = 1 grid and 371 on the shared grid (`setup_sensitivity.md` Table 10 and
Table 5), and the pressure days at 140 and 138.

### 3. 2018 onsets: four or five

Convention, item 3. `construction-gaps-result.md` says "all five of the 2018 onsets" at h = 1 and, in the same sentence, "the four
of 2018 at h ≥ 2"; it is the h = 1 grid, which includes 2018-06-29. The shared-grid pages say four (`pressure-audit-result.md`
Tables 3 to 5, `desk_standard.json`). A note on the gap 4 page names it.

### 4. What "blind" means for 2018

Three meanings are in use.

* `pressure-audit-result.md` (Tables 4 and 5): the row's cut-off was chosen on a window with nothing it could catch, at every horizon.
  That is both `cutoff_rule` branches: no onset in the training window, or no cut-off within 2.0 false alarms per onset.
* `desk-standard-result.md` §4 counts only the first branch (blocks whose window holds no onset): at h = 1 the first block, at
  h = 2 to 5 the first five blocks, which contain the onsets 2018-11-15 and 2018-11-30. It also uses "blind spots" for the risk-date
  models' probability of exactly 0 off a risk date, a different cause.
* `setup-diagnostic-result.md` ("would blind a model", `data_integrity`) is a panel-defect flag: a copied row or a stale input. It
  has nothing to do with the cut-off.

So 2018-12-17 and 2018-12-28 are blind in the `pressure-audit-result.md` sense (their windows already hold earlier onsets, so by the
second branch) and not in the `desk-standard-result.md` sense; the pages are consistent once the sense is named. Convention, item 4. Notes are on the three pages.

### 5. When a settlement is public (reported, not settled)

`construction-gaps-result.md` gap 2 states "a settlement is public one business day ahead and no earlier (`information-set.md`)".
`desk-standard-result.md` §2 measures Treasury's schedules instead: on the tracked auction snapshot the announcement precedes the
settlement by 4 to 14 panel days for 99.7% of bill dates and 99.2% of coupon dates (a lead of 2 or more), and says the registry's
15:00 on the panel day before is a conservative floor taken from the auction results time, not a publication schedule. Both are
true of different things: the first is what the declaration says (`information-set.md` rule 2; `treasury_auctions.scheduled_availability`),
the second is what the schedules say. **This note does not settle which reading the information set adopts; that is Eleonora's decision
(desk-standard item 1).** The pages and files that depend on the declared reading are:
`construction-gaps-result.md` gap 2 and its `bill_days` sensitivity (nothing moves at h ≥ 2 because the settlement is declared
unavailable there); `risk-date-severity-result.md` and `metadata/risk_date_severity.json` (the coupon clause is h = 1 only for that
reason); `pressure-audit-result.md` (the settlement clause at h = 1 only); `settlement-check.md`;
`metadata/pressure_hazard.json`, `pressure_tail.json`, `rare_event_training.json` and `window_onset.json` (the settlement columns
dropped at h ≥ 2); and the scripts that carry the "one business day ahead" comment. The pages that already measure the other
reading, and so do not depend on the declaration, are `desk-standard-result.md` §2 and the announcement section of `pressure-audit-result.md` (the
announcement-dated measurement field). The gap 2 page carries a note pointing to the desk-standard measurement.

### 6. The tier-1 passers

Convention, item 5. `source-screen-result.md`, `construction-gaps-result.md`, `episode-post-mortem-result.md` and
`desk-standard-result.md` §4 mean the five risk-date models. `setup-sensitivity-result.md` says its "five tier-1 passers of the
directive" are the five rows with the most onsets flagged (Table 1: 15, 15, 15, 15 and 14 of 26, worst false alarms per onset 2.46 to
3.65, every one above the limit of 2), so it scores a different set; its item 5 already says none passes tier 1. A note is added at its
head.

### 7. False alarms per onset for `risk_gbm` at h = 1

1.35 (`pressure-audit-result.md`) and 1.30 (`construction-gaps-result.md`, declared column) are the same 35 false alarms over
different denominators: 35 / 26 = 1.346 on the shared grid (`score.json`, `summaries.risk_gbm.by_horizon.1`: `false_alarms` 35,
`onsets` 26, `onsets_flagged` 13) and 35 / 27 = 1.296 on the h = 1 grid (`report.json`, `declared.risk_gbm.1`: `false_alarms` 35,
`false_alarms_per_onset` 1.2963, 13 onsets flagged). The 27th onset, 2018-06-29, is not flagged, so the 13 flagged is the same in both.
The tier 1 bar is read on the shared grid, so the figure to quote against it is 1.35. Convention, item 2; the gap pages carry a note.

### 8. 2018–19: 17 onsets or 32 episodes

Different definitions of an episode (convention, item 6). In `setup-sensitivity-result.md` Table 5 (`scripts/setup_sensitivity.py`,
`period_profile`) "episodes" are maximal runs of consecutive pressure days on the h = 1 grid, which is the one-calm-day episode; the
onsets of the same row are counted on the shared grid. The supported counts: 2018-19 holds 17 onsets (five calm days, shared grid) and
32 maximal runs of pressure days (one calm day, h = 1 grid); over the whole window the runs are 47 on the h = 1 grid and 46 on the
shared grid (`setup-diagnostic-result.md` §3, the "+5 bp, 1 calm day" cell, is the shared-grid figure, 46). The two pages agree. A
note is added at the sensitivity page's Table 5 sentence.

### 9. 2024-09-30

`episode-post-mortem-result.md` files it as "no signal in the panel" for the best of the five models. That label is the post-mortem's
operational reading 1 (the start day's probability is under half the cut-off in force at every horizon). It describes the five
models' own probabilities, not the panel: `pressure-audit-result.md` §4 shows the walk-forward calendar rule warns 2024-09-30 at every
horizon, and gives the five models' h = 1 probabilities on the day as 0.00, 0.00, 0.01 and 0.13 against cut-offs of 0.12 to 0.27, "a
regime and calibration effect on a calendar day, not a missing input". The post-mortem's label does not support "the panel carries
no information about it". A correction note is added where the label is first used. The post-mortem's other "no signal" episodes
(2018-11-15, 2018-12-17, 2018-12-28, 2020-03-04) are not warned by the audit's calendar rule either, so only 2024-09-30 changes.

### 10. How old the weekly inputs are (correction, 10 October 2026, #517)

Three pages gave three ages for reserves, TGA and the dealer position, and the first measured the wrong thing.

| page | says | supported |
|---|---|---|
| `setup-diagnostic-result.md` §4 | never more than 7 calendar days old at a decision day | **wrong for what the forecast reads**: it counted how long a value stayed unchanged on the panel rows, which a weekly series carried by its Wednesday cannot exceed by construction |
| `pressure-audit-result.md`, Table 2 | 4 to 6 panel days before (reserves, TGA), 8 (dealer position) | right, in panel rows |
| `construction-gaps-result.md`, gap 5 | 6 to 12 days old | right, in calendar days from the Wednesday, around the 26 onsets |

Over all scored days, read through the as-of rule (`scripts/setup_reads.py`, `evidence/setup-diagnostic/setup_reads.md`): reserves and TGA are 6 to 13 calendar days
old at the decision (median 8; older than 7 on 1,110 of 1,873 scored days at h = 1), the dealer position 9 to 19 (older than 7 on every scored day). The
convention for the next pages: state the unit, and state whether the age is of the row or of the observation's Wednesday.

## Commands that show the supported values

```
# the panel (REPRODUCIBILITY.md) and the fold grid at h = 1
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 -m repo_model.cli backtest /tmp/funding_panel.csv --registry metadata/sources.json --feature spread_bps --decision-time 16:00 --model persistence --minimum-history 61 --refit-every 21 --end 2025-12-31 --report /tmp/persistence.json
python3 -c "import json; print(json.load(open('/tmp/persistence.json'))['folds'])"   # first fold and count
# onsets and scored days per horizon, and the shared grid
python3 -c "import json; print(json.load(open('docs/pivot/evidence/desk-standard/desk_standard.json'))['onset_count'])"
python3 -c "import json; print(json.load(open('docs/pivot/evidence/pressure-audit/score.json'))['provenance']['scored_window'])"
# false alarms of risk_gbm at h = 1 on both grids
python3 -c "import json; print(json.load(open('docs/pivot/evidence/pressure-audit/score.json'))['summaries']['risk_gbm']['by_horizon']['1'])"
python3 -c "import json; r=json.load(open('docs/pivot/evidence/construction-gaps/report.json'))['declared']['risk_gbm']['1']; print(r['days'], r['false_alarms'], r['false_alarms_per_onset'])"
```

The count of maximal runs of pressure days (47 from 2018-06-29, 46 from 2018-07-06, 32 in 2018-19) is a count over the panel's
spread column: `exceeds_bp(spread, 5.0)` on consecutive panel rows, split at the period edges 2019-12-31, 2020-12-31, 2023-12-31 and
2024-12-31.

## Not checked, or for Eleonora

* Point 5 is hers: which reading of when a settlement is public the information set adopts. Nothing here moves it.
* The conventions above are wording rules for the pages; whether the combined diagnostics summary adopts them is hers to confirm.
* The `docs/runs/` records and `information-set.md` are not edited. The "795 of 2042" in `information-set.md` is a scope difference
  noted above, not a correction.
* No forecast was rebuilt: every model figure is read from the tracked evidence of its page. The page-level numbers (for example the
  1.35 and the 1.30) were reproduced from those files, not re-scored.
