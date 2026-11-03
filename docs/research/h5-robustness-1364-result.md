# A fixed robustness set on (s3c-ann-net): the length of its history and its refit cadence (#1364)

**Development evidence, not a verdict.** H5 (primary goal), registration design, step 3. The declaration (`metadata/h5_robustness_1364.json`) was committed before any arm was walked. Nothing here is registered, nothing is chosen, and no arm replaces the candidate. The development window decides what is read; the 2026 days are shown apart and decide nothing. B4 (#1360) is not on main and is not compared.

## What was measured

The candidate (s3c-ann-net) is walked again at the 18:00 decision instant under six settings, all fixed in advance:

| arm | training history | refit every |
|---|---|---:|
| as run (2 years, every 21) | trailing 2 years (TRAIN_YEARS = 2) | 21 decision days |
| expanding (all history, every 21) | every panel row from the start of the panel (2018-04-03) up to the anchor, no trailing limit | 21 decision days |
| 2 years, refit every 5 | trailing 2 years (as run) | 5 decision days |
| 2 years, refit every 63 | trailing 2 years (as run) | 63 decision days |
| rolling 1 year, every 21 | trailing 1 year | 21 decision days |
| rolling 3 years, every 21 | trailing 3 years | 21 decision days |

**The premise of the directive is not what the code does.** The directive calls the candidate's history 'expanding, as now'. Every fit of the candidate takes its training pairs from a trailing window of two years (`spread_mean_reversion.TRAIN_YEARS`); only in the first two years of the panel is that the whole history. So the candidate as run is the rolling two-year setting, which is the reference here, and the two contrasts are read both ways: all history (expanding) and one and three years (the two rolling lengths). **Question 1 for Eleonora, below.**

Each arm is compared with the candidate as run, and every arm (the candidate included) with B1, B1' and B2, on grid CRPS averaged over h = 1..5 and on upper-tail twCRPS, by scoring protocol v1's studentized stationary bootstrap (seed 1364). Positive favours the arm. a gain or loss is read from the 90% studentized interval of mean d excluding zero (the one-sided 95% bound), otherwise undecided; a point estimate alone is not read (the rule of the pages since #1009).

## Answer

Does any choice of history or cadence change a reading of the candidate? The pooled lines first; the groups follow in the tables below, and the cells that change a reading are listed under each window. The skill and interval printed are those of relative skill; the reading itself uses the 90% interval of mean d (a group can read 'undecided' on mean d while the skill interval excludes zero).

**development window (decides).** The pooled reading of every arm against B1, B1' and B2, on both metrics, is the candidate's own reading.

| arm | pooled grid CRPS against the candidate as run | pooled twCRPS against the candidate as run | cells where the reading against B1, B1' or B2 differs | of which pooled |
|---|---|---|---:|---:|
| expanding (all history, every 21) | -2.0% [-4.2%, -0.3%] loss | -0.4% [-1.3%, +0.2%] undecided | 3 | 0 |
| 2 years, refit every 5 | +0.1% [-0.2%, +0.4%] undecided | -0.0% [-0.4%, +0.3%] undecided | 3 | 0 |
| 2 years, refit every 63 | -0.6% [-1.3%, -0.2%] loss | -0.5% [-1.1%, +0.0%] loss | 1 | 0 |
| rolling 1 year, every 21 | +0.9% [-0.2%, +2.0%] undecided | +0.9% [+0.0%, +1.9%] gain | 13 | 0 |
| rolling 3 years, every 21 | -2.3% [-4.6%, -0.9%] loss | -0.6% [-2.1%, -0.1%] loss | 1 | 0 |

**2026 days (decide nothing).** A pooled reading against B1, B1' or B2 differs from the candidate's in the cells listed below.

| arm | pooled grid CRPS against the candidate as run | pooled twCRPS against the candidate as run | cells where the reading against B1, B1' or B2 differs | of which pooled |
|---|---|---|---:|---:|
| expanding (all history, every 21) | -1.6% [-8.9%, +3.1%] undecided | +4.1% [-2.0%, +12.8%] undecided | 9 | 1 |
| 2 years, refit every 5 | -0.2% [-0.6%, +0.1%] undecided | -0.1% [-0.7%, +0.2%] undecided | 1 | 0 |
| 2 years, refit every 63 | -0.6% [-1.5%, +0.1%] undecided | -1.4% [-3.4%, -0.1%] loss | 5 | 0 |
| rolling 1 year, every 21 | -1.8% [-2.6%, -0.9%] loss | -1.7% [-3.7%, -0.1%] undecided | 5 | 0 |
| rolling 3 years, every 21 | -0.6% [-2.0%, +0.2%] undecided | -1.9% [-6.1%, +0.7%] undecided | 9 | 1 |

## Development window (targets to 2025-12-31): decides

Reproduction: the mean grid CRPS of the as-run arm and of B1, B1' and B2 equals the 18:00 record of #1314 to 1e-9.

### grid CRPS, averaged over h = 1..5 (primary)

Mean over all days, pooled:

| as run (2 years, every 21) | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 | B1 | B1' | B2 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.6012 | 1.6338 | 1.5997 | 1.6113 | 1.5871 | 1.6379 | 2.2889 | 1.8506 | 2.5144 |

Each arm against the candidate as run (relative skill, 90% interval, reading), pooled, by lead, by regime and by pressure-day type:

| group | days | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 |
|---|---:|---|---|---|---|---|
| pooled: all decision days | 1855 | -2.0% [-4.2%, -0.3%] loss | +0.1% [-0.2%, +0.4%] undecided | -0.6% [-1.3%, -0.2%] loss | +0.9% [-0.2%, +2.0%] undecided | -2.3% [-4.6%, -0.9%] loss |
| lead: h=1 | 1855 | -3.0% [-6.4%, -0.6%] loss | +0.1% [-0.3%, +0.4%] undecided | -0.7% [-1.4%, -0.2%] loss | +1.1% [+0.2%, +2.2%] gain | -3.3% [-7.5%, -1.3%] loss |
| lead: h=2 | 1855 | -2.0% [-4.7%, +0.2%] undecided | +0.1% [-0.3%, +0.4%] undecided | -0.5% [-1.3%, -0.0%] loss | +1.1% [+0.1%, +2.3%] gain | -2.9% [-6.0%, -1.1%] loss |
| lead: h=3 | 1855 | -2.0% [-4.3%, -0.1%] loss | +0.1% [-0.2%, +0.4%] undecided | -0.7% [-1.4%, -0.2%] loss | +1.0% [-0.2%, +2.2%] undecided | -2.2% [-4.6%, -0.8%] loss |
| lead: h=4 | 1855 | -1.9% [-3.8%, -0.2%] loss | +0.1% [-0.3%, +0.3%] undecided | -0.7% [-1.4%, -0.2%] loss | +0.6% [-0.5%, +1.8%] undecided | -1.8% [-3.5%, -0.7%] loss |
| lead: h=5 | 1855 | -1.4% [-3.0%, +0.2%] undecided | +0.1% [-0.2%, +0.4%] undecided | -0.6% [-1.2%, -0.0%] loss | +0.6% [-0.6%, +1.8%] undecided | -1.4% [-2.6%, -0.4%] loss |
| regime: 2018-19 | 361 | identical | -0.1% [-0.6%, +0.2%] undecided | -0.5% [-1.3%, +0.2%] undecided | +0.0% [-0.7%, +1.1%] undecided | identical |
| regime: 2020 | 251 | -0.5% [-1.6%, -0.1%] loss | +0.2% [-0.2%, +0.6%] undecided | -0.5% [-1.2%, +0.2%] loss | +5.0% [+1.9%, +11.3%] gain | -0.5% [-1.6%, -0.1%] loss |
| regime: 2021-23 | 748 | -9.6% [-18.8%, -2.1%] loss | +0.3% [-0.2%, +0.8%] undecided | -2.0% [-7.7%, -0.1%] loss | +1.5% [-2.8%, +5.4%] undecided | -10.4% [-20.3%, -4.1%] loss |
| regime: 2024 | 250 | +5.3% [-1.9%, +14.5%] undecided | +1.4% [+0.6%, +3.5%] gain | -0.6% [-1.5%, +0.1%] undecided | +4.5% [+1.4%, +8.9%] gain | -6.6% [-11.5%, -2.2%] loss |
| regime: 2025-26 | 249 | -5.0% [-9.9%, -0.2%] loss | -0.3% [-1.3%, +0.0%] undecided | +0.2% [-0.6%, +0.8%] undecided | -2.1% [-4.6%, +0.3%] undecided | +0.1% [-1.0%, +1.4%] undecided |
| pressure_day_type: ordinary | 1591 | -0.2% [-2.6%, +2.4%] undecided | +0.1% [-0.3%, +0.4%] undecided | -0.6% [-1.5%, -0.1%] loss | +0.2% [-0.9%, +1.4%] undecided | -1.8% [-4.3%, -0.2%] loss |
| pressure_day_type: quarter_end_turn | 44 | -12.1% [-34.1%, +8.7%] loss | -0.2% [-1.6%, +0.2%] undecided | -0.2% [-1.3%, +0.6%] undecided | +3.8% [-6.7%, +22.4%] undecided | -6.6% [-16.8%, +2.4%] loss |
| pressure_day_type: tax_date | 89 | -2.0% [-22.8%, +2.6%] undecided | +0.1% [-0.1%, +0.3%] undecided | -0.3% [-1.4%, +1.1%] undecided | +1.1% [+0.4%, +2.1%] undecided | -2.0% [-25.9%, +2.8%] undecided |
| pressure_day_type: turn | 120 | -11.4% [-31.1%, +1.0%] loss | +0.8% [+0.1%, +2.8%] gain | -1.0% [-2.3%, -0.2%] loss | +3.7% [-1.7%, +17.4%] undecided | -3.9% [-11.5%, +0.4%] loss |
| pressure_day_type: year_end | 15 | not tested | not tested | not tested | not tested | not tested |

Readings against B1 / B1' / B2 (G gain, L loss, U undecided; the interval rule above), the candidate as run beside each arm:

| group | days | as run (2 years, every 21) | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 |
|---|---:|---|---|---|---|---|---|
| pooled: all decision days | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=1 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=2 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=3 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=4 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=5 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| regime: 2018-19 | 361 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| regime: 2020 | 251 | U/U/G | U/U/G | U/U/G | U/U/G | G/U/G | U/U/G |
| regime: 2021-23 | 748 | G/U/G | U/U/G | G/U/G | G/U/G | G/U/G | U/U/G |
| regime: 2024 | 250 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| regime: 2025-26 | 249 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| pressure_day_type: ordinary | 1591 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| pressure_day_type: quarter_end_turn | 44 | U/U/U | U/U/U | U/U/U | U/U/G | G/G/U | U/U/U |
| pressure_day_type: tax_date | 89 | U/U/G | U/U/G | U/U/G | U/U/G | G/G/G | U/U/G |
| pressure_day_type: turn | 120 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| pressure_day_type: year_end | 15 | not tested | not tested | not tested | not tested | not tested | not tested |

### upper-tail twCRPS (key secondary)

Mean over all days, pooled:

| as run (2 years, every 21) | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 | B1 | B1' | B2 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.8447 | 0.8484 | 0.8450 | 0.8491 | 0.8371 | 0.8498 | 1.3750 | 0.9991 | 1.1328 |

Each arm against the candidate as run (relative skill, 90% interval, reading), pooled, by lead, by regime and by pressure-day type:

| group | days | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 |
|---|---:|---|---|---|---|---|
| pooled: all decision days | 1855 | -0.4% [-1.3%, +0.2%] undecided | -0.0% [-0.4%, +0.3%] undecided | -0.5% [-1.1%, +0.0%] loss | +0.9% [+0.0%, +1.9%] gain | -0.6% [-2.1%, -0.1%] loss |
| lead: h=1 | 1855 | +0.3% [-0.3%, +1.1%] undecided | -0.0% [-0.7%, +0.4%] undecided | -0.4% [-0.8%, +0.1%] undecided | +1.0% [+0.3%, +1.9%] gain | -0.6% [-1.8%, -0.1%] loss |
| lead: h=2 | 1855 | -0.0% [-0.8%, +0.8%] undecided | -0.1% [-0.6%, +0.4%] undecided | -0.2% [-0.7%, +0.3%] undecided | +1.0% [+0.3%, +2.0%] gain | -0.5% [-2.0%, -0.1%] loss |
| lead: h=3 | 1855 | -0.7% [-1.8%, +0.1%] undecided | -0.0% [-0.5%, +0.2%] undecided | -0.6% [-1.2%, -0.0%] loss | +1.0% [+0.1%, +2.1%] gain | -0.7% [-2.7%, -0.1%] loss |
| lead: h=4 | 1855 | -0.8% [-2.1%, -0.0%] loss | -0.0% [-0.4%, +0.2%] undecided | -0.7% [-1.6%, -0.0%] loss | +0.8% [-0.2%, +1.9%] undecided | -0.7% [-2.4%, -0.1%] loss |
| lead: h=5 | 1855 | -0.9% [-2.3%, -0.1%] loss | -0.0% [-0.4%, +0.2%] undecided | -0.7% [-1.6%, +0.2%] loss | +0.8% [-0.3%, +2.1%] undecided | -0.5% [-1.5%, -0.1%] loss |
| regime: 2018-19 | 361 | identical | -0.1% [-0.5%, +0.3%] undecided | -0.5% [-1.2%, +0.2%] undecided | -0.0% [-0.9%, +1.3%] undecided | identical |
| regime: 2020 | 251 | -1.1% [-3.9%, +0.2%] loss | +0.5% [-0.4%, +1.5%] undecided | -1.4% [-3.8%, +0.9%] loss | +9.6% [-3.2%, +21.8%] gain | -1.1% [-3.9%, +0.2%] loss |
| regime: 2021-23 | 748 | -12.3% [-28.1%, +1.6%] loss | +4.3% [+1.1%, +9.9%] gain | -15.5% [-45.9%, -8.7%] loss | +25.9% [-11.5%, +50.6%] gain | -6.7% [-32.7%, +1.9%] undecided |
| regime: 2024 | 250 | -1.7% [-20.1%, +9.7%] undecided | +1.4% [-0.0%, +15.3%] undecided | +0.2% [-0.1%, +0.8%] undecided | +1.8% [-0.7%, +10.8%] undecided | -11.5% [-30.8%, -7.6%] loss |
| regime: 2025-26 | 249 | -2.0% [-7.0%, +3.1%] undecided | -0.6% [-2.8%, +0.2%] undecided | +0.0% [-0.5%, +0.5%] undecided | -0.6% [-5.0%, +2.4%] undecided | -1.2% [-3.5%, +0.0%] undecided |
| pressure_day_type: ordinary | 1591 | +1.2% [+0.1%, +3.6%] gain | -0.2% [-0.8%, +0.3%] undecided | -0.6% [-1.5%, +0.2%] undecided | +0.1% [-1.0%, +1.0%] undecided | -0.6% [-2.1%, -0.1%] loss |
| pressure_day_type: quarter_end_turn | 44 | -3.7% [-23.8%, +1.1%] loss | gain (mean d +0.0031) | undecided (mean d -0.0053) | undecided (mean d +0.1162) | loss (mean d -0.0319) |
| pressure_day_type: tax_date | 89 | -0.1% [-1.1%, +0.2%] undecided | +0.1% [-0.1%, +0.4%] gain | undecided (mean d +0.0012) | +1.1% [+0.6%, +1.7%] undecided | +0.1% [-0.3%, +0.7%] gain |
| pressure_day_type: turn | 120 | -9.1% [-89.7%, +10.1%] undecided | +0.5% [-0.1%, +1.6%] gain | -1.0% [-1.9%, -0.4%] loss | +2.3% [-1.5%, +15.3%] undecided | -1.2% [-8.0%, +0.5%] undecided |
| pressure_day_type: year_end | 15 | not tested | not tested | not tested | not tested | not tested |

Readings against B1 / B1' / B2 (G gain, L loss, U undecided; the interval rule above), the candidate as run beside each arm:

| group | days | as run (2 years, every 21) | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 |
|---|---:|---|---|---|---|---|---|
| pooled: all decision days | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=1 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=2 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=3 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=4 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| lead: h=5 | 1855 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| regime: 2018-19 | 361 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| regime: 2020 | 251 | U/U/G | U/U/G | U/U/G | U/U/G | G/G/G | U/U/G |
| regime: 2021-23 | 748 | U/U/U | U/U/L | G/U/U | U/U/U | G/G/U | U/U/U |
| regime: 2024 | 250 | G/U/U | G/G/U | G/G/U | G/U/U | G/G/U | G/U/U |
| regime: 2025-26 | 249 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| pressure_day_type: ordinary | 1591 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| pressure_day_type: quarter_end_turn | 44 | U/U/U | U/U/U | U/U/U | U/U/U | G/G/U | U/U/U |
| pressure_day_type: tax_date | 89 | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G | G/G/G |
| pressure_day_type: turn | 120 | U/G/G | U/G/G | G/G/G | U/G/G | G/G/G | U/G/G |
| pressure_day_type: year_end | 15 | not tested | not tested | not tested | not tested | not tested | not tested |

### Cells that change a reading

600 cells examined (group, metric, arm and comparator); 92 change a reading or show an arm against the reference; 508 do not. At 90% intervals some flags are expected by chance.

| arm | group | metric | against | reference reads | arm reads | days |
|---|---|---|---|---|---|---:|
| expanding (all history, every 21) | pooled: all decision days | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 3 years, every 21 | pooled: all decision days | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | pooled: all decision days | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 1 year, every 21 | pooled: all decision days | upper tail twcrps | as run (2 years, every 21) | - | gain | 1855 |
| rolling 3 years, every 21 | pooled: all decision days | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | pooled: all decision days | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| expanding (all history, every 21) | lead: h=1 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 1 year, every 21 | lead: h=1 | grid crps | as run (2 years, every 21) | - | gain | 1855 |
| rolling 3 years, every 21 | lead: h=1 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | lead: h=1 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 1 year, every 21 | lead: h=1 | upper tail twcrps | as run (2 years, every 21) | - | gain | 1855 |
| rolling 3 years, every 21 | lead: h=1 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 1 year, every 21 | lead: h=2 | grid crps | as run (2 years, every 21) | - | gain | 1855 |
| rolling 3 years, every 21 | lead: h=2 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | lead: h=2 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 1 year, every 21 | lead: h=2 | upper tail twcrps | as run (2 years, every 21) | - | gain | 1855 |
| rolling 3 years, every 21 | lead: h=2 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| expanding (all history, every 21) | lead: h=3 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 3 years, every 21 | lead: h=3 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | lead: h=3 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 1 year, every 21 | lead: h=3 | upper tail twcrps | as run (2 years, every 21) | - | gain | 1855 |
| rolling 3 years, every 21 | lead: h=3 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | lead: h=3 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| expanding (all history, every 21) | lead: h=4 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 3 years, every 21 | lead: h=4 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | lead: h=4 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| expanding (all history, every 21) | lead: h=4 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 3 years, every 21 | lead: h=4 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | lead: h=4 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 3 years, every 21 | lead: h=5 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | lead: h=5 | grid crps | as run (2 years, every 21) | - | loss | 1855 |
| expanding (all history, every 21) | lead: h=5 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| rolling 3 years, every 21 | lead: h=5 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| 2 years, refit every 63 | lead: h=5 | upper tail twcrps | as run (2 years, every 21) | - | loss | 1855 |
| expanding (all history, every 21) | regime: 2020 | grid crps | as run (2 years, every 21) | - | loss | 251 |
| rolling 1 year, every 21 | regime: 2020 | grid crps | B1 | undecided | gain | 251 |
| rolling 1 year, every 21 | regime: 2020 | grid crps | as run (2 years, every 21) | - | gain | 251 |
| rolling 3 years, every 21 | regime: 2020 | grid crps | as run (2 years, every 21) | - | loss | 251 |
| 2 years, refit every 63 | regime: 2020 | grid crps | as run (2 years, every 21) | - | loss | 251 |
| expanding (all history, every 21) | regime: 2020 | upper tail twcrps | as run (2 years, every 21) | - | loss | 251 |
| rolling 1 year, every 21 | regime: 2020 | upper tail twcrps | B1 | undecided | gain | 251 |
| rolling 1 year, every 21 | regime: 2020 | upper tail twcrps | B1' | undecided | gain | 251 |
| rolling 1 year, every 21 | regime: 2020 | upper tail twcrps | as run (2 years, every 21) | - | gain | 251 |
| rolling 3 years, every 21 | regime: 2020 | upper tail twcrps | as run (2 years, every 21) | - | loss | 251 |
| 2 years, refit every 63 | regime: 2020 | upper tail twcrps | as run (2 years, every 21) | - | loss | 251 |
| expanding (all history, every 21) | regime: 2021-23 | grid crps | B1 | gain | undecided | 748 |
| expanding (all history, every 21) | regime: 2021-23 | grid crps | as run (2 years, every 21) | - | loss | 748 |
| rolling 3 years, every 21 | regime: 2021-23 | grid crps | B1 | gain | undecided | 748 |
| rolling 3 years, every 21 | regime: 2021-23 | grid crps | as run (2 years, every 21) | - | loss | 748 |
| 2 years, refit every 63 | regime: 2021-23 | grid crps | as run (2 years, every 21) | - | loss | 748 |
| expanding (all history, every 21) | regime: 2021-23 | upper tail twcrps | B2 | undecided | loss | 748 |
| expanding (all history, every 21) | regime: 2021-23 | upper tail twcrps | as run (2 years, every 21) | - | loss | 748 |
| rolling 1 year, every 21 | regime: 2021-23 | upper tail twcrps | B1 | undecided | gain | 748 |
| rolling 1 year, every 21 | regime: 2021-23 | upper tail twcrps | B1' | undecided | gain | 748 |
| rolling 1 year, every 21 | regime: 2021-23 | upper tail twcrps | as run (2 years, every 21) | - | gain | 748 |
| 2 years, refit every 5 | regime: 2021-23 | upper tail twcrps | B1 | undecided | gain | 748 |
| 2 years, refit every 5 | regime: 2021-23 | upper tail twcrps | as run (2 years, every 21) | - | gain | 748 |
| 2 years, refit every 63 | regime: 2021-23 | upper tail twcrps | as run (2 years, every 21) | - | loss | 748 |
| rolling 1 year, every 21 | regime: 2024 | grid crps | as run (2 years, every 21) | - | gain | 250 |
| rolling 3 years, every 21 | regime: 2024 | grid crps | as run (2 years, every 21) | - | loss | 250 |
| 2 years, refit every 5 | regime: 2024 | grid crps | as run (2 years, every 21) | - | gain | 250 |
| expanding (all history, every 21) | regime: 2024 | upper tail twcrps | B1' | undecided | gain | 250 |
| rolling 1 year, every 21 | regime: 2024 | upper tail twcrps | B1' | undecided | gain | 250 |
| rolling 3 years, every 21 | regime: 2024 | upper tail twcrps | as run (2 years, every 21) | - | loss | 250 |
| 2 years, refit every 5 | regime: 2024 | upper tail twcrps | B1' | undecided | gain | 250 |
| expanding (all history, every 21) | regime: 2025-26 | grid crps | as run (2 years, every 21) | - | loss | 249 |
| rolling 3 years, every 21 | pressure_day_type: ordinary | grid crps | as run (2 years, every 21) | - | loss | 1591 |
| 2 years, refit every 63 | pressure_day_type: ordinary | grid crps | as run (2 years, every 21) | - | loss | 1591 |
| expanding (all history, every 21) | pressure_day_type: ordinary | upper tail twcrps | as run (2 years, every 21) | - | gain | 1591 |
| rolling 3 years, every 21 | pressure_day_type: ordinary | upper tail twcrps | as run (2 years, every 21) | - | loss | 1591 |
| expanding (all history, every 21) | pressure_day_type: quarter_end_turn | grid crps | as run (2 years, every 21) | - | loss | 44 |
| rolling 1 year, every 21 | pressure_day_type: quarter_end_turn | grid crps | B1 | undecided | gain | 44 |
| rolling 1 year, every 21 | pressure_day_type: quarter_end_turn | grid crps | B1' | undecided | gain | 44 |
| rolling 3 years, every 21 | pressure_day_type: quarter_end_turn | grid crps | as run (2 years, every 21) | - | loss | 44 |
| 2 years, refit every 63 | pressure_day_type: quarter_end_turn | grid crps | B2 | undecided | gain | 44 |
| expanding (all history, every 21) | pressure_day_type: quarter_end_turn | upper tail twcrps | as run (2 years, every 21) | - | loss | 44 |
| rolling 1 year, every 21 | pressure_day_type: quarter_end_turn | upper tail twcrps | B1 | undecided | gain | 44 |
| rolling 1 year, every 21 | pressure_day_type: quarter_end_turn | upper tail twcrps | B1' | undecided | gain | 44 |
| rolling 3 years, every 21 | pressure_day_type: quarter_end_turn | upper tail twcrps | as run (2 years, every 21) | - | loss | 44 |
| 2 years, refit every 5 | pressure_day_type: quarter_end_turn | upper tail twcrps | as run (2 years, every 21) | - | gain | 44 |
| rolling 1 year, every 21 | pressure_day_type: tax_date | grid crps | B1 | undecided | gain | 89 |
| rolling 1 year, every 21 | pressure_day_type: tax_date | grid crps | B1' | undecided | gain | 89 |
| rolling 3 years, every 21 | pressure_day_type: tax_date | upper tail twcrps | as run (2 years, every 21) | - | gain | 89 |
| 2 years, refit every 5 | pressure_day_type: tax_date | upper tail twcrps | as run (2 years, every 21) | - | gain | 89 |
| expanding (all history, every 21) | pressure_day_type: turn | grid crps | as run (2 years, every 21) | - | loss | 120 |
| rolling 3 years, every 21 | pressure_day_type: turn | grid crps | as run (2 years, every 21) | - | loss | 120 |
| 2 years, refit every 5 | pressure_day_type: turn | grid crps | as run (2 years, every 21) | - | gain | 120 |
| 2 years, refit every 63 | pressure_day_type: turn | grid crps | as run (2 years, every 21) | - | loss | 120 |
| rolling 1 year, every 21 | pressure_day_type: turn | upper tail twcrps | B1 | undecided | gain | 120 |
| 2 years, refit every 5 | pressure_day_type: turn | upper tail twcrps | B1 | undecided | gain | 120 |
| 2 years, refit every 5 | pressure_day_type: turn | upper tail twcrps | as run (2 years, every 21) | - | gain | 120 |
| 2 years, refit every 63 | pressure_day_type: turn | upper tail twcrps | as run (2 years, every 21) | - | loss | 120 |

Groups of fewer than 20 days were not tested: pressure_day_type/year_end (15).

## 2026 days (targets 2026-01-02 to 2026-09-03): shown apart, decides nothing

Reproduction: the mean grid CRPS of the as-run arm and of B1, B1' and B2 equals the 18:00 record of #1314 to 1e-9.

### grid CRPS, averaged over h = 1..5 (primary)

Mean over all days, pooled:

| as run (2 years, every 21) | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 | B1 | B1' | B2 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.6685 | 1.6949 | 1.6726 | 1.6787 | 1.6981 | 1.6794 | 2.1597 | 1.8689 | 2.1546 |

Each arm against the candidate as run (relative skill, 90% interval, reading), pooled, by lead, by regime and by pressure-day type:

| group | days | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 |
|---|---:|---|---|---|---|---|
| pooled: all decision days | 165 | -1.6% [-8.9%, +3.1%] undecided | -0.2% [-0.6%, +0.1%] undecided | -0.6% [-1.5%, +0.1%] undecided | -1.8% [-2.6%, -0.9%] loss | -0.6% [-2.0%, +0.2%] undecided |
| lead: h=1 | 165 | -5.9% [-17.3%, +1.9%] undecided | +0.1% [-0.1%, +0.4%] undecided | -0.2% [-0.8%, +0.4%] undecided | -1.8% [-2.4%, -1.2%] loss | -0.0% [-1.2%, +0.8%] undecided |
| lead: h=2 | 165 | -2.0% [-10.9%, +4.5%] undecided | -0.2% [-0.5%, +0.2%] undecided | -0.3% [-1.1%, +0.4%] undecided | -2.5% [-3.4%, -1.6%] loss | -0.7% [-1.9%, +0.2%] undecided |
| lead: h=3 | 165 | -0.6% [-7.4%, +4.0%] undecided | -0.2% [-0.4%, +0.1%] undecided | -0.6% [-1.7%, +0.2%] undecided | -1.5% [-2.6%, -0.5%] loss | -0.7% [-2.3%, +0.4%] undecided |
| lead: h=4 | 165 | -0.4% [-6.7%, +3.6%] undecided | -0.5% [-1.0%, -0.0%] undecided | -0.9% [-1.8%, -0.1%] loss | -1.8% [-3.0%, -0.6%] loss | -0.9% [-2.4%, +0.1%] undecided |
| lead: h=5 | 165 | +0.3% [-5.3%, +4.3%] undecided | -0.5% [-1.2%, +0.1%] undecided | -1.0% [-2.1%, -0.1%] loss | -1.3% [-2.7%, +0.3%] undecided | -0.9% [-2.2%, -0.0%] undecided |
| regime: 2025-26 | 169 | -1.1% [-7.7%, +3.8%] undecided | -0.2% [-0.6%, +0.1%] undecided | -0.6% [-1.4%, +0.1%] undecided | -1.7% [-2.6%, -0.9%] loss | -0.7% [-2.0%, +0.1%] undecided |
| pressure_day_type: ordinary | 146 | +0.7% [-4.1%, +5.4%] undecided | -0.2% [-0.6%, +0.1%] undecided | -0.7% [-1.6%, +0.1%] undecided | -1.6% [-2.4%, -0.7%] loss | -0.7% [-1.9%, +0.1%] undecided |
| pressure_day_type: quarter_end_turn | 4 | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: tax_date | 6 | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: turn | 12 | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: year_end | 1 | not tested | not tested | not tested | not tested | not tested |

Readings against B1 / B1' / B2 (G gain, L loss, U undecided; the interval rule above), the candidate as run beside each arm:

| group | days | as run (2 years, every 21) | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 |
|---|---:|---|---|---|---|---|---|
| pooled: all decision days | 165 | G/U/G | G/U/G | G/U/G | G/U/G | G/U/G | G/U/G |
| lead: h=1 | 165 | G/U/G | U/U/G | G/U/G | G/U/G | U/U/G | G/U/G |
| lead: h=2 | 165 | G/U/G | U/U/G | G/U/G | G/U/G | G/U/G | G/U/G |
| lead: h=3 | 165 | G/U/G | G/U/U | G/U/G | G/U/G | G/U/G | G/U/G |
| lead: h=4 | 165 | G/U/G | G/U/U | G/U/U | G/U/U | G/U/U | G/U/U |
| lead: h=5 | 165 | G/U/U | G/U/U | G/U/U | G/U/U | G/U/U | G/U/U |
| regime: 2025-26 | 169 | G/U/G | G/U/G | G/U/G | G/U/G | G/U/G | G/U/G |
| pressure_day_type: ordinary | 146 | G/U/G | U/U/U | G/U/G | U/U/G | U/U/U | U/U/U |
| pressure_day_type: quarter_end_turn | 4 | not tested | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: tax_date | 6 | not tested | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: turn | 12 | not tested | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: year_end | 1 | not tested | not tested | not tested | not tested | not tested | not tested |

### upper-tail twCRPS (key secondary)

Mean over all days, pooled:

| as run (2 years, every 21) | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 | B1 | B1' | B2 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.5142 | 0.4930 | 0.5150 | 0.5216 | 0.5230 | 0.5238 | 0.8254 | 0.6213 | 0.6358 |

Each arm against the candidate as run (relative skill, 90% interval, reading), pooled, by lead, by regime and by pressure-day type:

| group | days | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 |
|---|---:|---|---|---|---|---|
| pooled: all decision days | 165 | +4.1% [-2.0%, +12.8%] undecided | -0.1% [-0.7%, +0.2%] undecided | -1.4% [-3.4%, -0.1%] loss | -1.7% [-3.7%, -0.1%] undecided | -1.9% [-6.1%, +0.7%] undecided |
| lead: h=1 | 165 | +0.8% [-7.5%, +10.6%] undecided | +0.3% [-0.1%, +0.6%] undecided | -0.9% [-2.5%, -0.0%] undecided | -2.9% [-4.5%, -0.7%] loss | -0.4% [-2.8%, +1.7%] undecided |
| lead: h=2 | 165 | +5.7% [-1.7%, +18.1%] undecided | -0.2% [-0.6%, +0.1%] undecided | -1.2% [-3.4%, +0.1%] undecided | -3.0% [-5.8%, -0.5%] loss | -1.7% [-5.3%, +0.9%] undecided |
| lead: h=3 | 165 | +5.3% [-2.0%, +16.2%] undecided | -0.3% [-0.6%, +0.0%] undecided | -1.5% [-4.2%, -0.1%] loss | -0.4% [-2.6%, +1.7%] undecided | -1.9% [-6.5%, +1.1%] undecided |
| lead: h=4 | 165 | +3.4% [-4.1%, +11.6%] undecided | -0.3% [-0.9%, +0.2%] undecided | -1.8% [-4.0%, -0.2%] loss | -1.6% [-3.9%, +0.5%] undecided | -2.6% [-8.1%, +0.5%] loss |
| lead: h=5 | 165 | +5.0% [-3.0%, +13.3%] undecided | -0.2% [-1.1%, +0.4%] undecided | -1.6% [-3.7%, -0.1%] loss | -0.9% [-3.4%, +1.8%] undecided | -2.6% [-7.2%, +0.1%] loss |
| regime: 2025-26 | 169 | +5.5% [-1.5%, +17.5%] undecided | -0.1% [-0.6%, +0.3%] undecided | -1.4% [-3.1%, -0.3%] loss | -1.6% [-3.4%, +0.0%] undecided | -2.1% [-5.6%, +0.3%] loss |
| pressure_day_type: ordinary | 146 | +8.6% [-0.1%, +24.6%] gain | -0.2% [-0.8%, +0.2%] undecided | -1.7% [-3.9%, -0.1%] loss | -1.2% [-3.9%, +1.2%] undecided | -1.6% [-4.8%, +0.7%] undecided |
| pressure_day_type: quarter_end_turn | 4 | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: tax_date | 6 | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: turn | 12 | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: year_end | 1 | not tested | not tested | not tested | not tested | not tested |

Readings against B1 / B1' / B2 (G gain, L loss, U undecided; the interval rule above), the candidate as run beside each arm:

| group | days | as run (2 years, every 21) | expanding (all history, every 21) | 2 years, refit every 5 | 2 years, refit every 63 | rolling 1 year, every 21 | rolling 3 years, every 21 |
|---|---:|---|---|---|---|---|---|
| pooled: all decision days | 165 | G/G/U | G/G/G | G/G/U | G/G/U | G/G/U | G/U/U |
| lead: h=1 | 165 | G/U/G | G/U/G | G/U/G | G/U/G | G/U/G | G/U/G |
| lead: h=2 | 165 | G/G/U | G/G/G | G/G/U | G/U/U | G/U/U | G/U/U |
| lead: h=3 | 165 | G/G/U | G/G/U | G/G/U | G/G/U | G/G/U | G/U/U |
| lead: h=4 | 165 | G/G/U | G/G/U | G/G/U | G/G/U | G/G/U | G/U/U |
| lead: h=5 | 165 | G/G/U | G/G/U | G/G/U | G/U/U | G/G/U | G/U/U |
| regime: 2025-26 | 169 | G/G/U | G/G/G | G/G/U | G/U/U | G/G/U | G/U/U |
| pressure_day_type: ordinary | 146 | G/U/U | G/U/U | G/U/U | G/U/U | G/U/U | G/U/U |
| pressure_day_type: quarter_end_turn | 4 | not tested | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: tax_date | 6 | not tested | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: turn | 12 | not tested | not tested | not tested | not tested | not tested | not tested |
| pressure_day_type: year_end | 1 | not tested | not tested | not tested | not tested | not tested | not tested |

### Cells that change a reading

320 cells examined (group, metric, arm and comparator); 50 change a reading or show an arm against the reference; 270 do not. At 90% intervals some flags are expected by chance.

| arm | group | metric | against | reference reads | arm reads | days |
|---|---|---|---|---|---|---:|
| rolling 1 year, every 21 | pooled: all decision days | grid crps | as run (2 years, every 21) | - | loss | 165 |
| expanding (all history, every 21) | pooled: all decision days | upper tail twcrps | B2 | undecided | gain | 165 |
| rolling 3 years, every 21 | pooled: all decision days | upper tail twcrps | B1' | gain | undecided | 165 |
| 2 years, refit every 63 | pooled: all decision days | upper tail twcrps | as run (2 years, every 21) | - | loss | 165 |
| expanding (all history, every 21) | lead: h=1 | grid crps | B1 | gain | undecided | 165 |
| rolling 1 year, every 21 | lead: h=1 | grid crps | B1 | gain | undecided | 165 |
| rolling 1 year, every 21 | lead: h=1 | grid crps | as run (2 years, every 21) | - | loss | 165 |
| rolling 1 year, every 21 | lead: h=1 | upper tail twcrps | as run (2 years, every 21) | - | loss | 165 |
| expanding (all history, every 21) | lead: h=2 | grid crps | B1 | gain | undecided | 165 |
| rolling 1 year, every 21 | lead: h=2 | grid crps | as run (2 years, every 21) | - | loss | 165 |
| expanding (all history, every 21) | lead: h=2 | upper tail twcrps | B2 | undecided | gain | 165 |
| rolling 1 year, every 21 | lead: h=2 | upper tail twcrps | B1' | gain | undecided | 165 |
| rolling 1 year, every 21 | lead: h=2 | upper tail twcrps | as run (2 years, every 21) | - | loss | 165 |
| rolling 3 years, every 21 | lead: h=2 | upper tail twcrps | B1' | gain | undecided | 165 |
| 2 years, refit every 63 | lead: h=2 | upper tail twcrps | B1' | gain | undecided | 165 |
| expanding (all history, every 21) | lead: h=3 | grid crps | B2 | gain | undecided | 165 |
| rolling 1 year, every 21 | lead: h=3 | grid crps | as run (2 years, every 21) | - | loss | 165 |
| rolling 3 years, every 21 | lead: h=3 | upper tail twcrps | B1' | gain | undecided | 165 |
| 2 years, refit every 63 | lead: h=3 | upper tail twcrps | as run (2 years, every 21) | - | loss | 165 |
| expanding (all history, every 21) | lead: h=4 | grid crps | B2 | gain | undecided | 165 |
| rolling 1 year, every 21 | lead: h=4 | grid crps | B2 | gain | undecided | 165 |
| rolling 1 year, every 21 | lead: h=4 | grid crps | as run (2 years, every 21) | - | loss | 165 |
| rolling 3 years, every 21 | lead: h=4 | grid crps | B2 | gain | undecided | 165 |
| 2 years, refit every 5 | lead: h=4 | grid crps | B2 | gain | undecided | 165 |
| 2 years, refit every 63 | lead: h=4 | grid crps | B2 | gain | undecided | 165 |
| 2 years, refit every 63 | lead: h=4 | grid crps | as run (2 years, every 21) | - | loss | 165 |
| rolling 3 years, every 21 | lead: h=4 | upper tail twcrps | B1' | gain | undecided | 165 |
| rolling 3 years, every 21 | lead: h=4 | upper tail twcrps | as run (2 years, every 21) | - | loss | 165 |
| 2 years, refit every 63 | lead: h=4 | upper tail twcrps | as run (2 years, every 21) | - | loss | 165 |
| 2 years, refit every 63 | lead: h=5 | grid crps | as run (2 years, every 21) | - | loss | 165 |
| rolling 3 years, every 21 | lead: h=5 | upper tail twcrps | B1' | gain | undecided | 165 |
| rolling 3 years, every 21 | lead: h=5 | upper tail twcrps | as run (2 years, every 21) | - | loss | 165 |
| 2 years, refit every 63 | lead: h=5 | upper tail twcrps | B1' | gain | undecided | 165 |
| 2 years, refit every 63 | lead: h=5 | upper tail twcrps | as run (2 years, every 21) | - | loss | 165 |
| rolling 1 year, every 21 | regime: 2025-26 | grid crps | as run (2 years, every 21) | - | loss | 169 |
| expanding (all history, every 21) | regime: 2025-26 | upper tail twcrps | B2 | undecided | gain | 169 |
| rolling 3 years, every 21 | regime: 2025-26 | upper tail twcrps | B1' | gain | undecided | 169 |
| rolling 3 years, every 21 | regime: 2025-26 | upper tail twcrps | as run (2 years, every 21) | - | loss | 169 |
| 2 years, refit every 63 | regime: 2025-26 | upper tail twcrps | B1' | gain | undecided | 169 |
| 2 years, refit every 63 | regime: 2025-26 | upper tail twcrps | as run (2 years, every 21) | - | loss | 169 |
| expanding (all history, every 21) | pressure_day_type: ordinary | grid crps | B1 | gain | undecided | 146 |
| expanding (all history, every 21) | pressure_day_type: ordinary | grid crps | B2 | gain | undecided | 146 |
| rolling 1 year, every 21 | pressure_day_type: ordinary | grid crps | B1 | gain | undecided | 146 |
| rolling 1 year, every 21 | pressure_day_type: ordinary | grid crps | B2 | gain | undecided | 146 |
| rolling 1 year, every 21 | pressure_day_type: ordinary | grid crps | as run (2 years, every 21) | - | loss | 146 |
| rolling 3 years, every 21 | pressure_day_type: ordinary | grid crps | B1 | gain | undecided | 146 |
| rolling 3 years, every 21 | pressure_day_type: ordinary | grid crps | B2 | gain | undecided | 146 |
| 2 years, refit every 63 | pressure_day_type: ordinary | grid crps | B1 | gain | undecided | 146 |
| expanding (all history, every 21) | pressure_day_type: ordinary | upper tail twcrps | as run (2 years, every 21) | - | gain | 146 |
| 2 years, refit every 63 | pressure_day_type: ordinary | upper tail twcrps | as run (2 years, every 21) | - | loss | 146 |

Groups of fewer than 20 days were not tested: pressure_day_type/quarter_end_turn (4), pressure_day_type/tax_date (6), pressure_day_type/turn (12), pressure_day_type/year_end (1).

## Questions for Eleonora

1. **Which reading of 'expanding' did you mean?** (a) The set as run here: the as-run two-year window is the reference, with all history, one year and three years as the alternatives (default). (b) Only all-history against two rolling lengths, leaving the two-year window out of the table. (c) Change the candidate's window itself; that is a different directive and is not done here.

## What this does not show

Development data on seen days; the intervals of the regime and day-type groups use the current method (#1221). The window and the cadence are varied one at a time. No combination, no other term, input, cap or scale window. Five alternatives over many groups mean some flags are chance flags. Nothing is adopted.
