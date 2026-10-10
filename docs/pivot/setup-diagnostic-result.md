# Does the evaluation setup explain the misses? (#480)

A diagnostic on the setup of the pressure-day judge (#375, amended under #407), done before more model work. It changes no
model, no bar, no declaration and no published figure, and it writes nothing into `docs/runs/`. Scored days are 2018-06-29 to
2025-12-31 only; no day of the 2026 window is read (`docs/decisions/lockbox.md`). The measurements, their windows and the rules
for flagging a panel problem are in `metadata/setup_diagnostic.json`, committed before the figures were computed;
`scripts/setup_diagnostic.py` refuses an uncommitted declaration. Two details of the integrity check were reworded in later
commits after a first run showed a rule counted ordinary repeats; they are listed under "Not checked, and for Eleonora".
The full tables are `docs/pivot/evidence/setup-diagnostic/setup_diagnostic.md` (and `.json`); the numbers below are read from
them.

> *Note, 10 October 2026 (#503).* "Scored days 2018-06-29 to 2025-12-31" is the declared window; the 1,869 days and the 26 episodes below are
> the **shared grid** (from 2018-07-06), which every horizon scores. The h = 1 grid starts 2018-06-29 and has 27 onsets. "Would blind a
> model" (Table 7) flags a panel defect, not the infinite flag cut-off that `pressure-audit-result.md` calls blind. See `docs/pivot/diagnostics-reconciliation.md`, points 2 and 4.

## Short answer

* **The 2018 misses are a thin-history problem; the 2020 and 2024 misses are not.** The four 2018 episodes fall where the
  refit in force had seen 2 or 3 episodes (1 or 2 on the scored days the flag cut-off is chosen from), and only 0 or 1 of the seven rows
  could flag at all. From the first 2019 episode on, five to seven of the seven rows can. The two 2020 and two 2024 episodes
  come after 18 to 21 episodes in the cut-off window, every row could flag, and none did.
* **The tier-1 recall is a 2019 and 2025 recall.** No row, benchmark or tier-1 passer warns any episode of 2018, 2020 or 2024.
  Climatology and persistence-logistic warn only 2019 episodes; the five passers warn 10 of 13 in 2019 and 3 to 4 of 5 in 2025.
* **The +5 bp target is not the same event in every year.** SOFR - IORB has a median of +4 bp in 2019 and about -8 to -11 bp
  in 2021 to 2024. A day above +5 bp is an ordinary day in 2019 and a move of about 13 bp from the usual level in 2024.
* **The episode set is fragile to its definition.** The count runs from 12 to 48 across the onset rules and thresholds tried, and
  only four of the 26 survive all 11 other rules.
* **Data integrity does not explain the misses.** No gap, blank or stale weekly value in any episode's 10-day window, and no
  revision among the observations an earlier tracked vintage can compare. Two copied-row flags were checked against the source
  and are real, distinct days.

## 1. Training history at each episode (Table 1)

The judge refits every 21 scored days from the first scored day. Each episode is read at the refit in force on its day: the model is
fitted on the panel from 2018-04-03 to the training end (the business day h + 1 before the block's first day), and the flag
cut-off is chosen on the scored days of that window (`pressure_judge.choose_cutoffs`; a window with no episode never flags).
Table 1 gives, at h = 1 and at h = 5, the refit's first day, the training end, the pressure days and episodes seen, and how many of the seven rows
(climatology, persistence-logistic and the five passers) had a finite cut-off and how many warned.

* **2018 (four episodes: 2018-11-15, 11-30, 12-17, 12-28).** The refits had seen 5 to 7 pressure days and 2 to 3 episodes (1 to 2
  on scored days; 0 to 1 at h = 5). The cut-off was infinite for all seven rows at the first episode and for six of seven at the other three: the
  rule had no window in which to find a cut-off within two false alarms per onset. No row warned any of them. So yes: the 2018
  misses fall where the models had seen few onsets, and the cut-off rule gives them no way to flag.
* **2019.** From 2019-01-15 (6 episodes seen) five of seven rows can flag; from 2019-06-17 all seven can, and the warnings follow.
* **2020 (2020-03-04 and 03-12).** 18 and 19 episodes in the cut-off window, all seven cut-offs finite, no row warned.
  History does not explain these.
* **2024 (2024-09-30 and 12-26).** 20 and 21 episodes in the window, all seven finite, no row warned. History does not explain
  these either.
* **2025.** All seven finite; the rows warn 2, 5, 1, 5 and 5 of the seven for the five episodes.

The five passers fit on risk dates only (`docs/pivot/risk-date-severity-result.md`), so the pressure days they see are a subset of the "seen" columns.

## 2. The target across regimes (Tables 2 and 3)

By year (all panel days up to 2025-12-31, 2018 from 2018-04-03), the share of days above +5 bp and the median of SOFR - IORB:

| year | days > +5 bp | median (bp) | p25 to p75 (bp) | episodes |
|---|---|---|---|---|
| 2018 | 8.6% of the 121 scored days | -1.0 | -4.0 to +1.0 | 4 |
| 2019 | 35.6% | +4.0 | +0.2 to +7.0 | 13 |
| 2020 | 1.6% | -1.0 | -3.0 to 0.0 | 2 |
| 2021 | 0 | -10.0 | -10.0 to -9.0 | 0 |
| 2022 | 0 | -11.0 | -12.0 to -10.0 | 0 |
| 2023 | 0 | -9.0 | -10.0 to -9.0 | 0 |
| 2024 | 2.0% | -8.0 | -9.0 to -6.0 | 2 |
| 2025 | 11.6% | -5.0 | -8.0 to +1.0 | 5 |

* **An episode in 2019 and one in 2024 are not the same event.** In 2019 the +5 bp line sat between the median (+4) and the 75th
  percentile (+7), so a third of days crossed it and an episode is a short run of ordinary days. In 2021 to 2024 the median is
  8 to 11 bp below IORB (the ON RRP floor), and +5 bp is a rise of about 13 to 16 bp over the usual level. The base rate is 0% for three
  years and 35.6% for one. A pooled recall over 26 episodes weights 2019 at half. This is a statement about the measurement, not
  about any model: the threshold is a fixed distance from IORB whatever the typical spread is.
* **Administered-rate changes.** The panel has 28 days on which IOER or IORB moved (Table 3). Six are not multiples of 25 bp, which is
  the declared reading of a technical adjustment (the target range is not in the tracked data, so this is a rule, not a record):
  2018-06-14 (+20), 2018-12-20 (+20), 2019-05-02 (-5), 2019-09-19 (-30), 2020-01-30 (+5) and 2021-06-17 (+5). Each shifts SOFR - IORB mechanically
  by minus its size if SOFR does not follow; SOFR did follow most of the way (net change in the spread between -9 and +1 bp, except
  2019-09-19), and only one of the six is followed by an episode within 15 panel days (2018-12-20). The technical adjustments
  therefore do not manufacture the pressure days. The 2021-07-29 renaming of IOER to IORB (no change in level) moves nothing.

## 3. Episode-definition sensitivity (Tables 4 to 6b)

Episodes on the same scored days, by threshold and by the number of calm panel days required before:

| threshold | 1 calm day | 3 | 5 | 10 |
|---|---|---|---|---|
| +3 bp | 48 | 34 | 24 | 12 |
| +5 bp | 46 | 32 | **26** | 12 |
| +10 bp | 30 | 24 | 24 | 15 |

* **Calm days.** Three calm days at +5 bp keep all 26 and add six; one calm day adds 20 (every burst becomes its own episode; this is
  #160's one-day definition); ten calm days drop 14, among them 2018-11-30, 12-17 and 12-28. The 2018 count goes
  from 4 (five calm days) to 1 (ten).
* **Threshold.** At +3 bp the set keeps 14 of the 26 and adds 10; at +10 bp it keeps 10, adds 14 and drops 16, because an episode opens on the
  first day above the line, and that day is between +5 and +10 bp for most of the 26.
* **Stability.** Only four of the 26 are an episode under all 11 other rules (2019-01-31, 2019-02-28, 2024-12-26, 2025-09-15). Four are an
  episode under only two (2018-11-30, 2018-12-28, 2019-06-25, 2020-03-12). Table 6 lists the dates that appear or disappear under each
  rule.
* So the "26" is one reading of a bursty series, and recall on 26 changes shape with the reading. The 2018 misses are among the least stable
  episodes: the 2018 episodes that survive many rules (2018-12-17: 8 of 11; 2018-11-15: 6) are still missed.

## 4. Data integrity around episodes (Table 7)

For each episode, the 10 panel days before it, on the published panel (digest `4ddc3882…`):

* **Gaps and blanks.** No weekday missing without a holiday, and no empty cell in any window, in any of the 12 columns checked (the nine daily and three weekly ones the declaration names).
* **Forward fills.** A copied row (SOFR, its volume, p25, p75, TGCR and BGCR all equal to the previous day's) occurs in two windows:
  2019-08-29 (the decision day for 2019-08-30) and 2019-12-06. The raw New York Fed file for both days carries a different 1st or 99th percentile
  than the previous day (`nyfed-sofr-rate`, fixture snapshot), so these are two genuine days that repeat in the six columns the panel keeps, not
  forward fills. The 'would blind a model' flag on 2019-08-30 is a false positive of the rule and is read so.
* **Stale weekly values.** Reserve balances, TGA and the dealer position are never more than 7 calendar days old at a decision day.
* **Revisions.** Of the reserve-balance, TGA and IOER observations in each window an earlier tracked ALFRED vintage holds, none differs from the latest tracked vintage (units
  aligned: the 2026 vintage is in millions). The first tracked vintage is 2019-09-16, so these are not first prints, and the 2024 and
  2025 windows have no earlier vintage to compare (3 of 4 observations for 2024-09-30; none for the others).
* **Late publications:** not checked beyond the as-of rule, which the panel is built under.

Nothing in the panel would blind a model before an episode.

## 5. Benchmarks by year (Table 8)

Episodes warned at some horizon h = 1 to 5, +5 bp, the judge's cut-offs. The counts reproduce Table 1 of the re-judge and of
`docs/pivot/weighted-miss-result.md`: climatology 10, persistence-logistic 7, `risk_gbm` 13, `risk_gbm_base` 14, `risk_logistic` 14,
`risk_logistic_base` 13, `risk_quantile_skewt_base` 14.

| row | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|
| calendar_climatology | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 7 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| the five passers | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 to 4 of 5 |

2018, 2020 and 2024 are hard for every method tried, not only ours: nothing warns them. The passers' gain over climatology is in 2025
(3 to 4 of 5 against 0), not in 2019 (equal to climatology's 10 of 13). That is a regime split of the existing tier-1 result, not a new test.

## Reproduce

Published panel `4ddc3882…` from the tracked fixtures; the forecasts as in `docs/pivot/risk-date-severity-result.md`
(`pressure_judge.py forecasts` for the benchmarks, `risk_date_severity.py run` for the passers, h = 1 to 5, run with `/opt/rmm-venv/bin/python`):

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel /tmp/funding_panel.csv --horizon $h --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published /tmp/funding_panel.csv --horizon $h --output OUT/risk_h$h.json
PYTHONPATH=src python3 scripts/setup_diagnostic.py run --panel /tmp/funding_panel.csv --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' --output OUT/setup_diagnostic.json --markdown OUT/setup_diagnostic.md
```

## Not checked, and for Eleonora

* **Declaration changes after a first run.** The integrity rule first counted any repeat of a daily column as a forward fill; the first run showed
  that a rate quoted to the basis point repeats in every window, so the declaration was reworded (before this page) to a copied row across six columns,
  and to count single-column repeats for context only. The text of the blinding rule was also made to match the code. Nothing else was changed after a figure was seen.
* **Technical adjustments** are read by a rule (not a multiple of 25 bp), because the target range is not in the tracked data. A list of the Fed's own
  designations would settle it.
* **Revisions** cannot be measured against first prints for 2018 to 2024: only vintages from 2019-09-16 are tracked for reserve balances and TGA.
* **What this does not say.** It does not say a different threshold, a regime-relative target or a longer burn-in is the right fix; any of those changes the bar or the target and is hers.
  The measurements bear on three of her decisions: whether the +5 bp event should be read relative to the regime's usual spread; whether the 2018 episodes
  belong in a recall that no cut-off rule can score; and the onset rule (the calm-day count) that defines the 26.
