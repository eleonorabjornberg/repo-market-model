# Decision: the judge's rules, as amended by the rulings of 10 October 2026

**Status: DRAFT, for Eleonora to review and merge.** A decision is in force only once she has merged this record. The
pull request that closes #536 drafts it and puts the amended rules into `metadata/pressure_judge.json` and
`src/repo_model/pressure_judge.py`; the rulings below were relayed by the orchestrating session on #509, #510 and #514,
and listed in #536 (a relay posted through the Claude app, not an owner-attested comment). Under the rule of 6 October 2026
(#256), changing a pre-registered primary test is hers alone to attest: a review that finds no attested merge of this
record escalates rather than merges.

The rulings are Eleonora's, of 10 October 2026. This record puts them into the judge's declaration and changes nothing
else.

## The rules, amended

### 1. Tier 1 counts false alarms the way it counts warnings (#509)

Tier 1 at lead at least `L` counts an onset as warned when some horizon `h >= L` flags it. A **false alarm** is now a day
that is not a pressure day and is flagged at some horizon `h >= L`. A day flagged at two horizons is one false alarm. The
limit of 2 false alarms per onset is read on that pooled count: the flat count, or the weighted count while the weighted
rule is in force (`docs/decisions/weighted-miss.md`), each day at its own weight.

The count at each horizon alone (`false_alarms_by_horizon`, `worst_false_alarms_per_onset`) is still reported, and is no
longer the count the tier's limit reads.

Tier 1 is also reported **per lead time**, that is, at each horizon alone: the onsets that horizon flags, with the recall
and its interval, against the false alarms that horizon raises. The per-horizon reading counts false alarms per horizon.
The pass rule reads the pooled reading at lead at least 1, as before.

The flag cut-off rule (`cutoff_rule`) is unchanged: it chooses each horizon's cut-off on that horizon's own false
alarms per onset in the training window, as `docs/decisions/weighted-miss.md` says. This ruling is about tier 1.

The climatology reference of the pooled reading is matched, as before, to the number of false alarms raised: it is now
the pooled flat count, with the climatology forecast of the first horizon at or above the lead.

### 2. The pass rule does not require a pass outside 2018-19 (#510)

The pass rule (tier 1 at lead at least 1, tier 3 at every lead, tier 5) is unchanged and requires nothing of the days
outside 2018-19. Every judge table adds, beside tier 1, **recall and false alarms per onset inside and outside 2018-19**
as a line of its own, each with a 90% stationary-bootstrap interval where the onset count allows one. The years are
declared in `metadata/pressure_judge.json` (`tiers.onset_warning.split_years`: 2018 and 2019). The line is reported, never
a tier. An interval the bootstrap cannot give (no onset drawn on a resample) is shown as unavailable; replicates are never
dropped.

### 3. Regime scoring

* **Tier 3 checks calibration only in regimes with at least 20 pressure days** (`+5 bp`, in the scored window, at the
  horizon scored). It tested every regime with at least one before (ruling of 8 October 2026, #407). A regime with fewer
  is reported, with its interval and the number of pressure days, and does not decide tier 3. The number is
  `tiers.no_crying_wolf.calibration_min_pressure_days`.
* **Every judge table adds an equal-weight-per-regime recall line:** the mean, over the regimes that have an onset, of the
  share of that regime's onsets that are warned (pooled across horizons at lead at least 1). It has no interval and is
  reported, not a tier.
* The `+5 bp` threshold is unchanged.

### 4. The weighted rule stays as adopted (#514)

Alarms before and after an episode are discounted alike, as `docs/decisions/weighted-miss.md` adopts them. Nothing in
that record changes.

## What stays unchanged

The thresholds, the horizons, the bootstrap, the cut-off rule and its limit, the tiers' other limits, tiers 2, 4 and 5,
the confirmation look, and every record in `docs/runs/`. No 2026 day is read or scored (`docs/decisions/lockbox.md`); the
confirmation tier is not opened.

## What it changes in the published figures

Nothing in `docs/runs/`. The judge's table is re-scored under the amended rules and published anew in
`docs/pivot/judge-rulings-rescore-result.md`, which states which rows pass tier 1 (pooled and per lead) and which pass
the full rule.

## Left open

* Which of the per-lead readings, if any, should be a tier of its own is not ruled.
* The equal-weight-per-regime line has no interval; whether it should have one is not ruled.
* Opening the 2026 confirmation tier is a separate act of hers.
