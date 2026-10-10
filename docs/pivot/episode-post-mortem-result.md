# Episode post-mortem of the 26 pressure episodes (#474, of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and reads
no day after 2025-12-31 (`docs/decisions/lockbox.md`). It decides nothing: the readings below are descriptive, and the three
operational readings it had to choose are listed at the end for Eleonora.

## What it is

The 26 episodes are the +5 bp onsets of tier 1 at lead >= 1, the days scored at every horizon h = 1 to 5, as the judge counts them.
The five models are the tier-1 passers of #428 (`risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`,
`risk_quantile_skewt_base`), under the judge's own cut-offs (#407). "Warned at lead >= 1" is a flag for the start day at some
horizon h = 1 to 5; the warned counts equal the judge's tier-1 table (`evidence/risk-date-severity/tables.md`).

Per episode and model, `evidence/episode-post-mortem/episodes.json` holds the h = 1 probability and the cut-off in force on each
of the 10 scored days before the start and on the start day, the probability, cut-off and flag at h = 1 to 5 for the start day,
and, for a miss, the cause. Every input is read as of the decision instant of its scored day (`asof.InformationRule`), never from
that day's own row. `summary.md` has the tables; there is one figure per pressure-day type (`figure_month_end.svg`,
`figure_ordinary.svg`, `figure_quarter_end.svg`, `figure_tax_date.svg`): a panel per episode, each model's h = 1 path, cut-offs
dashed. The first episodes (2018) have fewer than 10 scored days before them, and their paths are shorter.

## Reproduce

Published panel `4ddc3882…`; scratch panel from `pressure_v1_1.py panel`, then `measurement_fields.py panel`. Set `OMP_NUM_THREADS=1`
when several scoring jobs share a machine (numpy threads oversubscribe and the jobs stall).

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5, each of the five models: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --candidate MODEL --output OUT/risk_MODEL_h$h.json
PYTHONPATH=src python3 scripts/episode_post_mortem.py run --panel PUBLISHED.csv --scratch-panel AUG2.csv --output-dir docs/pivot/evidence/episode-post-mortem OUT/bench_h?.json OUT/risk_*_h?.json
```

## Result

* **15 of 26 episodes are warned by at least one of the five; 11 are missed by all five.** Each model warns 13 or 14.
* **Where the misses are.** By regime, 2018-19: 7 of 17 missed by all five; 2020: both; 2024: both; 2025-26: none. By type, ordinary
  days: 7 of 12; month-end 2 of 6; quarter-end 1 of 3; tax date 1 of 5. Six of the 7 ordinary-day all-five misses (2019-05-28, 2019-06-25, 2019-08-13,
  2020-03-04, 2020-03-12, 2024-12-26) are days on which the models were silent (probability exactly 0: not a calendar risk date at the
  horizon). These models cannot warn of such a day by construction.
* **Cause of the 11 all-five misses** (best of the five, readings below): signal present but under the cut-off, 1 (2018-11-30, a month
  end, `risk_quantile_skewt_base`); signal too late for the lead rule, 5 (2019-05-28, 2019-06-25, 2019-08-13, 2020-03-12, and 2024-12-26 for
  `risk_quantile_skewt_base`); no signal in the panel, 5 (2018-11-15, 2018-12-17, 2018-12-28, 2020-03-04, 2024-09-30). Per model the split
  is in Table 1 of `summary.md`; one episode, 2025-10-15, is warned by one model and missed with the signal under the cut-off by three.

  *Correction, 10 October 2026 (#503).* "No signal in the panel" is reading 1 below applied to the five models' own probabilities (under half the
  cut-off at every horizon), not a statement about the panel. For 2024-09-30 it is too strong: the quarter-end is a calendar risk date, and
  the walk-forward calendar rule of `pressure-audit-result.md` §4 warns it at every horizon; the five models' h = 1 probabilities on the day
  (0.00 to 0.13) sit under cut-offs of 0.12 to 0.27, a regime and calibration effect on a calendar day. Read the label as "the five models'
  probabilities stayed under half their cut-offs". The other four episodes under this label are not warned by that calendar rule. See `docs/pivot/diagnostics-reconciliation.md`, point 9.
* **Inputs.** In the 10 scored days before a miss the inputs that moved (at least 2 trailing sd of 10-day changes) are few: none for
  4 of the 13 episodes missed by at least one model; `tbill_4w`, `sofr_volume` and `tgcr` account for most of the rest, and they moved before the 2020-03
  and 2024 episodes with no flag. Against the false alarms of the same regime (67 flagged non-pressure days across regimes), the
  number of inputs whose start-day level lies outside the false alarms' range is at or below the count expected by chance for 11 of the 13
  episodes (two of them, in 2024, have only 2 false alarms to compare with, and none separates); 2020-03-04 (2 against 0.9) and 2020-03-12 (3 against 0.9, including the as-of spread itself and `sofr_p75_iorb_bps`) are the
  exceptions, and both are the March 2020 stress, whose inputs were already extreme when the day came. **Nothing in the panel separates the
  2018-19 and 2024 misses from the same regime's false alarms beyond chance.**
* **The comparison is confounded for ordinary days.** The five models flag almost only risk dates, so the false alarms are mostly risk
  dates, and an ordinary-day episode differs from them on the settlement and calendar inputs for that reason alone
  (2018-11-15 on `treasury_settlement`, for instance). Those "separating" inputs are not evidence of a usable signal.

## Readings made by this pull request, for Eleonora

The directive leaves these open; the script's constants, listed in its docstring, name each. None changes a declaration or figure.

1. "Signal present, under the cut-off": the start day's probability at some horizon is at least half the cut-off in force (`UNDER_RATIO`).
2. "Too late for the lead rule": the model flags the day after the start day or the one after that at h = 1 (the pressure itself is then in
   the as-of spread); checked after reading 1.
3. "Moved": a 10-scored-day change of at least 2 standard deviations (`MOVE_Z`) of the input's 10-day changes over the 250 scored days
   ending 10 days before the start; "separates": the start-day level lies outside the range over at least 5 false alarms of the regime.
   A false alarm is a non-pressure day flagged at h = 1 by any of the five models.
