# Input attribution for `gbm_funding` (#964)

**Development data, not a verdict (scoring protocol v1).** Hypothesis H5, step 4 (why the known drivers add nothing; scopes #951's follow-up) and the
validation report (`docs/model/validation.md`, sensitivity analysis). Nothing is published: no declaration, model, record, pin or figure moves, and no
day after 2025-12-31 and no lockbox day is read.

**Status: declared, and the walks have not been run.** Refitting `gbm_funding` at every refit block of the #634 fold grid, at five leads, and
re-forecasting each scored day under about eighty perturbations is long (a lead-1 smoke run over 125 scored days took about six minutes in the cloud,
so a lead is roughly an hour and a half and the five leads about seven hours). By the rule on #46 it runs on Eleonora's Mac. The tables below are filled in
by the results commit on the same branch.

## What is measured

`metadata/gbm_attribution_964.json` declares everything before any score. `gbm_funding` is refitted exactly as `metadata/spread_distribution_634.json`
declares it; the attribution adds no setting. For each refit block, with that block's own fitted model and its scored days:

- **Permutation importance** of each design column (`spread_bps` and the published regressors; `treasury_settlement` is not read at leads 2 to 5): its
  values are shuffled among the block's scored days (five seeded shuffles), each day is re-forecast and scored against its own outcome, and the
  importance is the rise in grid CRPS. Cut by regime (2018-19, 2020, 2021-23, 2024, 2025) and by lead, with the protocol's studentized stationary
  bootstrap on the difference of the shuffled and unshuffled day scores.
- **Partial dependence** of q50 and q95 on `reserve_balances`, `tbill_4w`, `tga`, `sofr_volume` and `spread_bps`: the input is set, for every scored day,
  to each of five declared points (its 10th, 30th, 50th, 70th and 90th percentiles over the panel's rows to 2025-12-31), the others as read.
- **A one-sigma shock** table of q50 and q95: each of the five inputs moved by plus and minus its standard deviation over the block's training frame.

## The declared reading

For each of the five inputs, in each regime, the median's partial dependence *reads* the input when it moves by at least 0.5 bp across the five points;
its sign is that of the move from the first to the last point. The dependence is **regime-coded** when the regimes that read it do not all share one
sign; the report also records, for reserves, whether the median moves only between the points at or below $1.7 tn.

- If a level input is regime-coded, the next declared variant is the relative encodings of Lens D (`tbill - iorb`, `sofr_p75 - sofr` and `sofr - sofr_p25`
  in bp, volume over its trailing 60-row median, reserves as the as-of ratio).
- If the dependence is stable across regimes, the encoding avenue is dead.

**Marked for Eleonora:** the 0.5 bp floor and the sign rule are the author's choice, not a ruling. They decide only which sentence the page reaches; every
table is reported either way.

## Commands

See the docstring of `scripts/gbm_attribution_964.py`. The walks (`walk --horizon 1` to `5`) are the long step and are independent, so the five leads can
run in parallel; `score` and `report` take minutes.
