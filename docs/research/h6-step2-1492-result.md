# H6 development step 2, re-run on the mean-d bound (#1492)

**This page is new.** It does not replace or edit `docs/research/h6-step2-724-result.md` (#724), which reads every row on the skill interval and is kept as the record of what was run. Where a reading here differs from it, section 2 says so.

**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), development step 2, re-run under Eleonora's ruling of 6 November 2026 (option 1, #1492). **Development data, not a verdict** (scoring protocol v1, #640): the days were seen before, no confirmation day is scored, nothing is published and no locked day or day after 2025-12-31 is read. Script `scripts/h6_step2_1492.py`, declared in `metadata/h6_step2_1492.json` before any score; every figure below is read from `docs/research/h6-step2-1492/result.json`. Made at the 18:00 decision instant on the published panel (`4ddc3882cd6d...`). H6 step 3 waits on this page.

## 1. What changed against #724

Everything is #724's: the candidate (s3c-ann-net) and its walk, the strata, the one declared variant, the benchmarks, the target days (1425 from 2020-04-13 to 2025-12-24), seed 724, 10000 draws, block 3 events, HAC lag 3, two-sided 90% studentized stationary bootstrap. The run recomputes every row #724 could compute and refuses to write unless it is unchanged; only the rows #724 left `undefined` can differ. Two things changed:

- **The fallback (#1215, #1239).** A row whose skill is undefined (the benchmark scores zero on a resample) keeps its mean-d bound, instead of reading `undefined`. Where a resample has no long-run variance the bound is read with those resamples dropped and counted, as `spread_mr_variants_761.run_pairs` does.
- **The reading (#1009).** Every reading is taken from the lower end of the studentized 90% interval on mean(d), `d = S(benchmark) - S(model)`, positive favouring the model, so its lower end is the one-sided 95% bound. A row reads `gain` if that lower end is above zero, `loss` if the upper end is below zero, `undecided` otherwise. Skill and its interval are shown beside it; d is in bp.

**Caveat (Lens C, #958; #1215):** the HAC standard error that studentizes the bound is understated about 2x after 2020 (measured for the daily lag-10 series, not for this page's event series at lag 3), so an interval that excludes zero is narrower than it should be. A reading here is evidence for a question.

## 2. The readings, and which of them move

Kill rule, as #724 declared it in words: (s3c-ann-net) shows skill on the union without the bill stratum if the lower end is above zero against B1 and against B2 both. #724 took the lower end from the skill interval; here it is the mean-d lower end. Development readings, not verdicts.

| cut | #724 (skill interval): candidate | now (mean-d bound): candidate | #724: variant | now: variant | #724: variant adds, grid / twCRPS | now: variant adds, grid / twCRPS |
|---|---|---|---|---|---|---|
| union without the bill stratum (primary) | skill | skill | skill | skill | no / no | no / no |
| ordinary | skill | skill | skill | skill | no / no | no / no |
| quarter_end_turn **(moves)** | no skill shown | no skill shown | no skill shown | skill | yes / no | yes / yes |
| tax_date | no skill shown | no skill shown | no skill shown | no skill shown | no / no | no / no |
| turn | skill | skill | skill | skill | no / no | no / no |
| year_end | undefined | undefined | undefined | undefined | no / no | no / no |
| 2020 | no skill shown | no skill shown | no skill shown | no skill shown | no / no | no / no |
| 2021-23 | no skill shown | no skill shown | no skill shown | no skill shown | no / no | no / no |
| 2024 | skill | skill | skill | skill | no / no | no / no |
| 2025-26 | skill | skill | skill | skill | no / no | no / no |

On the union without the bill stratum the candidate's grid CRPS skill against B1 is +26.6% [+19.2%, +34.7%] with d +0.410 [+0.242, +0.648] bp, and against B2 +53.9% [+44.7%, +63.2%] with d +1.323 [+0.907, +2.011] bp: the reading is **skill** (#724: skill). B1' (+20.3% [+13.2%, +27.7%]; d +0.288 [+0.156, +0.469]; **gain**) and B2*-cap (+64.0% [+57.1%, +70.3%]; d +2.008 [+1.541, +2.730]; **gain**) do not decide. The variant against the candidate: grid CRPS -0.4% [-2.1%, +1.7%]; d -0.005 [-0.021, +0.021]; **undecided**; twCRPS -2.0% [-7.1%, +4.5%]; d -0.006 [-0.017, +0.016]; **undecided**.

## 3. The rows that change reading

Every row #724 defined whose skill-interval lower end and mean-d lower end fall on opposite sides of zero. Under a lower-bound reading each one reads differently on the mean-d bound than on the skill interval; the column `feeds a reading` marks those a stated reading in section 2 is taken from (the kill rule on the union without the bill stratum, on a regime or a pressure-day type, and the variant rule). Skill and mean d are #724's own figures for the row.

| row | events | skill (#724) | mean d (bp) | #724 reading | now | feeds a reading |
|---|---|---|---|---|---|---|
| ordinary, upper-tail twCRPS, (s3c-ann-net) vs B2 | 206 | +44.2% [+18.8%, +69.3%] | +0.174 [-0.008, +1.097] | gain | undecided (loses on the mean-d bound) | no |
| ordinary, upper-tail twCRPS, spread_mr_ctx vs B2 | 206 | +30.7% [+8.0%, +60.4%] | +0.121 [-0.017, +0.788] | gain | undecided (loses on the mean-d bound) | no |
| ordinary, upper-tail twCRPS, risk-date variant vs B1 | 206 | +15.9% [+2.5%, +31.0%] | +0.043 [-0.005, +0.182] | gain | undecided (loses on the mean-d bound) | no |
| ordinary, upper-tail twCRPS, risk-date variant vs B2 | 206 | +41.9% [+12.2%, +69.9%] | +0.165 [-0.019, +1.086] | gain | undecided (loses on the mean-d bound) | no |
| quarter_end_turn, grid CRPS, spread_mr_ctx vs B2*-cap | 34 | +34.4% [-34.3%, +65.2%] | +1.571 [+0.047, +2.776] | not shown | gain (gains on the mean-d bound) | no |
| quarter_end_turn, grid CRPS, risk-date variant vs B2 | 34 | +39.0% [-12.4%, +59.6%] | +1.357 [+0.102, +2.239] | not shown | gain (gains on the mean-d bound) | yes |
| quarter_end_turn, upper-tail twCRPS, risk-date variant vs B2*-cap | 34 | +46.9% [-22.5%, +98.4%] | +0.766 [+0.179, +1.736] | not shown | gain (gains on the mean-d bound) | no |
| tax_date, upper-tail twCRPS, (s3c-ann-net) vs B1 | 71 | +35.3% [+1.0%, +62.8%] | +0.105 [-0.038, +0.700] | gain | undecided (loses on the mean-d bound) | no |
| turn, upper-tail twCRPS, (s3c-ann-net) vs B1 | 92 | +45.9% [+17.4%, +95.2%] | +0.271 [-0.085, +4.251] | gain | undecided (loses on the mean-d bound) | no |
| turn, upper-tail twCRPS, risk-date variant vs B1 | 92 | +43.4% [+10.4%, +103.6%] | +0.256 [-0.102, +3.955] | gain | undecided (loses on the mean-d bound) | no |
| turn, upper-tail twCRPS, risk-date variant vs B2 | 92 | +70.9% [+58.9%, +80.2%] | +0.812 [-0.015, +9.501] | gain | undecided (loses on the mean-d bound) | no |
| 2024, grid CRPS, spread_mr_ctx vs B1' | 69 | +7.3% [+0.1%, +12.7%] | +0.142 [-0.001, +0.302] | gain | undecided (loses on the mean-d bound) | no |
| 2024, upper-tail twCRPS, (s3c-ann-net) vs B1 | 69 | +22.3% [-19.2%, +95.9%] | +0.106 [+0.005, +3.950] | not shown | gain (gains on the mean-d bound) | no |
| 2024, upper-tail twCRPS, (s3c-ann-net) vs B1' | 69 | +22.0% [-20.1%, +95.7%] | +0.105 [+0.004, +4.241] | not shown | gain (gains on the mean-d bound) | no |
| 2025-26, upper-tail twCRPS, spread_mr_ctx vs B1 | 69 | +16.5% [-6.9%, +31.8%] | +0.321 [+0.032, +0.822] | not shown | gain (gains on the mean-d bound) | no |
| 2025-26, upper-tail twCRPS, spread_mr_ctx vs B2 | 69 | +39.0% [+15.9%, +58.9%] | +1.036 [-0.013, +4.556] | gain | undecided (loses on the mean-d bound) | no |
| large bill settlement, grid CRPS, spread_mr_ctx vs risk-date calendar (#693) | 33 | +37.2% [-2.1%, +69.6%] | +1.295 [+0.381, +3.798] | not shown | gain (gains on the mean-d bound) | no |
| coupon settlement, upper-tail twCRPS, (s3c-ann-net) vs B1 | 186 | +38.8% [+15.4%, +63.8%] | +0.227 [-0.016, +1.121] | gain | undecided (loses on the mean-d bound) | no |
| coupon settlement, upper-tail twCRPS, spread_mr_ctx vs B2 | 186 | +29.3% [+4.2%, +53.0%] | +0.257 [-0.036, +1.297] | gain | undecided (loses on the mean-d bound) | no |
| coupon settlement, upper-tail twCRPS, spread_mr_ctx vs risk-date calendar (#693) | 111 | +32.8% [+7.5%, +52.3%] | +0.398 [-0.067, +2.006] | gain | undecided (loses on the mean-d bound) | no |
| coupon settlement, upper-tail twCRPS, risk-date variant vs B1 | 186 | +38.2% [+14.1%, +62.8%] | +0.223 [-0.020, +1.090] | gain | undecided (loses on the mean-d bound) | no |
| FOMC meeting day, upper-tail twCRPS, risk-date variant vs B2 | 92 | +41.0% [+13.1%, +56.6%] | +0.173 [-0.008, +0.893] | gain | undecided (loses on the mean-d bound) | no |
| month-end turn, upper-tail twCRPS, (s3c-ann-net) vs B1 | 92 | +45.9% [+17.4%, +95.2%] | +0.271 [-0.085, +4.251] | gain | undecided (loses on the mean-d bound) | no |
| month-end turn, upper-tail twCRPS, risk-date variant vs B1 | 92 | +43.4% [+10.4%, +103.6%] | +0.256 [-0.102, +3.955] | gain | undecided (loses on the mean-d bound) | no |
| month-end turn, upper-tail twCRPS, risk-date variant vs B2 | 92 | +70.9% [+58.9%, +80.2%] | +0.812 [-0.015, +9.501] | gain | undecided (loses on the mean-d bound) | no |
| month-end turn, upper-tail twCRPS, risk-date variant vs risk-date calendar (#693) | 92 | +70.9% [+58.9%, +80.2%] | +0.812 [-0.015, +9.501] | gain | undecided (loses on the mean-d bound) | no |
| IORB-change window (two days after a meeting), upper-tail twCRPS, (s3c-ann-net) vs B1 | 92 | +28.7% [+2.6%, +58.4%] | +0.094 [-0.029, +0.839] | gain | undecided (loses on the mean-d bound) | no |
| IORB-change window (two days after a meeting), upper-tail twCRPS, (s3c-ann-net) vs B1' | 92 | +22.9% [+4.4%, +38.4%] | +0.069 [-0.011, +0.497] | gain | undecided (loses on the mean-d bound) | no |
| IORB-change window (two days after a meeting), upper-tail twCRPS, (s3c-ann-net) vs B1'*-cap | 92 | +22.1% [+4.5%, +35.8%] | +0.066 [-0.008, +0.436] | gain | undecided (loses on the mean-d bound) | no |
| IORB-change window (two days after a meeting), upper-tail twCRPS, spread_mr_ctx vs B2 | 92 | +40.0% [+17.2%, +58.5%] | +0.264 [-0.037, +2.884] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, grid CRPS, (s3c-ann-net) vs B2 | 44 | +34.7% [-4.9%, +53.0%] | +1.127 [+0.004, +1.866] | not shown | gain (gains on the mean-d bound) | no |
| quarter-end and year-end, grid CRPS, spread_mr_ctx vs B2*-cap | 44 | +36.0% [-4.8%, +58.5%] | +1.559 [+0.611, +2.338] | not shown | gain (gains on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, (s3c-ann-net) vs B1 | 44 | +23.8% [+11.8%, +40.9%] | +0.269 [-0.028, +1.445] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, (s3c-ann-net) vs B1' | 44 | +23.9% [+11.9%, +41.3%] | +0.269 [-0.026, +1.479] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, (s3c-ann-net) vs B1'*-cap | 44 | +23.2% [+11.5%, +40.6%] | +0.259 [-0.027, +1.438] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, (s3c-ann-net) vs B2*-cap | 44 | +43.2% [-17.7%, +83.9%] | +0.652 [+0.143, +1.481] | not shown | gain (gains on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, risk-date variant vs B1 | 44 | +30.2% [+17.7%, +43.2%] | +0.341 [-0.036, +1.674] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, risk-date variant vs B1' | 44 | +30.3% [+18.0%, +43.4%] | +0.341 [-0.033, +1.668] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, risk-date variant vs B1'*-cap | 44 | +29.6% [+17.5%, +42.7%] | +0.331 [-0.033, +1.626] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, risk-date variant vs B2 | 44 | +22.4% [+0.5%, +38.9%] | +0.228 [-0.032, +0.875] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, risk-date variant vs risk-date calendar (#693) | 44 | +28.6% [+5.7%, +47.8%] | +0.316 [-0.018, +1.405] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end and year-end, upper-tail twCRPS, risk-date variant vs (s3c-ann-net) | 44 | +8.4% [+1.7%, +14.1%] | +0.072 [-0.006, +0.409] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end turn (Mar, Jun, Sep), grid CRPS, spread_mr_ctx vs B2*-cap | 34 | +34.4% [-34.3%, +65.2%] | +1.571 [+0.047, +2.776] | not shown | gain (gains on the mean-d bound) | no |
| quarter-end turn (Mar, Jun, Sep), grid CRPS, risk-date variant vs B2 | 34 | +39.0% [-12.4%, +59.6%] | +1.357 [+0.102, +2.239] | not shown | gain (gains on the mean-d bound) | no |
| quarter-end turn (Mar, Jun, Sep), grid CRPS, risk-date variant vs risk-date calendar (#693) | 34 | +39.0% [-12.4%, +59.6%] | +1.357 [+0.102, +2.239] | not shown | gain (gains on the mean-d bound) | no |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, risk-date variant vs B1'*-cap | 34 | +24.9% [+11.9%, +41.4%] | +0.288 [-0.038, +1.679] | gain | undecided (loses on the mean-d bound) | no |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, risk-date variant vs B2*-cap | 34 | +46.9% [-22.5%, +98.4%] | +0.766 [+0.179, +1.736] | not shown | gain (gains on the mean-d bound) | no |
| tax date, upper-tail twCRPS, (s3c-ann-net) vs B1 | 71 | +35.3% [+1.0%, +62.8%] | +0.105 [-0.038, +0.700] | gain | undecided (loses on the mean-d bound) | no |
| union of the strata, upper-tail twCRPS, spread_mr_ctx vs risk-date calendar (#693) | 207 | +32.5% [+5.9%, +54.9%] | +0.343 [-0.002, +1.248] | gain | undecided (loses on the mean-d bound) | no |
| union without the bill stratum (primary), upper-tail twCRPS, spread_mr_ctx vs risk-date calendar (#693) | 207 | +32.5% [+5.9%, +54.9%] | +0.343 [-0.002, +1.248] | gain | undecided (loses on the mean-d bound) | no |

**Of these, the rows a stated reading is taken from** (and so change what section 2 says): quarter_end_turn, grid CRPS, risk-date variant vs B2 (not shown on the skill interval, gain on the mean-d bound). Every other row in the table moves a cell of the tables below, not a stated reading.

## 4. The rows that have a bound now

#724 left these `undefined`: the benchmark scores zero on some resample, so skill has no interval. The mean-d bound is computed (#1215) and the row is read on it. A row that stays without a bound says why.

| row | events | mean d (bp) | reading | feeds a reading | resamples dropped |
|---|---|---|---|---|---|
| quarter_end_turn, upper-tail twCRPS, (s3c-ann-net) vs B1 | 34 | +0.191 [-0.041, +1.080] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, (s3c-ann-net) vs B1' | 34 | +0.181 [-0.039, +1.016] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, (s3c-ann-net) vs B2 | 34 | +0.174 [-0.142, +0.632] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, (s3c-ann-net) vs B2*-cap | 34 | +0.645 [+0.081, +1.876] | gain | no | 0 |
| quarter_end_turn, upper-tail twCRPS, spread_mr_ctx vs B1 | 34 | -0.078 [-0.480, +0.193] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, spread_mr_ctx vs B1' | 34 | -0.088 [-0.500, +0.165] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, spread_mr_ctx vs B2 | 34 | -0.095 [-0.504, +0.159] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, risk-date variant vs B1 | 34 | +0.311 [-0.040, +1.799] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, risk-date variant vs B1' | 34 | +0.301 [-0.038, +1.751] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, risk-date variant vs B2 | 34 | +0.294 [-0.015, +1.007] | undecided | no | 0 |
| quarter_end_turn, upper-tail twCRPS, risk-date variant vs (s3c-ann-net) | 34 | +0.120 [+0.002, +0.977] | gain | yes | 0 |
| tax_date, upper-tail twCRPS, (s3c-ann-net) vs B2 | 71 | +0.721 [+0.125, +2.093] | gain | no | 0 |
| tax_date, upper-tail twCRPS, spread_mr_ctx vs B2 | 71 | +0.463 [+0.002, +1.579] | gain | no | 0 |
| tax_date, upper-tail twCRPS, risk-date variant vs B2 | 71 | +0.686 [+0.106, +2.014] | gain | no | 0 |
| 2024, upper-tail twCRPS, (s3c-ann-net) vs B2 | 69 | +0.085 [+0.004, +2.572] | gain | no | 0 |
| 2024, upper-tail twCRPS, (s3c-ann-net) vs B2*-cap | 69 | +0.109 [+0.003, +4.320] | gain | no | 0 |
| 2024, upper-tail twCRPS, spread_mr_ctx vs B2 | 69 | -0.022 [-0.301, +0.006] | undecided | no | 0 |
| 2024, upper-tail twCRPS, spread_mr_ctx vs B2*-cap | 69 | +0.003 [-0.003, +0.019] | undecided | no | 0 |
| 2024, upper-tail twCRPS, risk-date variant vs B2 | 69 | +0.111 [+0.002, +2.227] | gain | no | 0 |
| 2024, upper-tail twCRPS, risk-date variant vs B2*-cap | 69 | +0.136 [+0.006, +3.122] | gain | no | 0 |
| large bill settlement, upper-tail twCRPS, (s3c-ann-net) vs risk-date calendar (#693) | 33 | +0.859 [+0.107, +9.457] | gain | no | 0 |
| large bill settlement, upper-tail twCRPS, spread_mr_ctx vs risk-date calendar (#693) | 33 | +0.493 [-0.015, +4.346] | undecided | no | 3 |
| large bill settlement, upper-tail twCRPS, risk-date variant vs risk-date calendar (#693) | 33 | +0.902 [+0.152, +5.166] | gain | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, (s3c-ann-net) vs B1 | 34 | +0.191 [-0.041, +1.080] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, (s3c-ann-net) vs B1' | 34 | +0.181 [-0.039, +1.016] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, (s3c-ann-net) vs B1'*-cap | 34 | +0.168 [-0.039, +0.923] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, (s3c-ann-net) vs B2 | 34 | +0.174 [-0.142, +0.632] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, (s3c-ann-net) vs B2*-cap | 34 | +0.645 [+0.081, +1.876] | gain | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, (s3c-ann-net) vs risk-date calendar (#693) | 34 | +0.174 [-0.142, +0.632] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, spread_mr_ctx vs B1 | 34 | -0.078 [-0.480, +0.193] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, spread_mr_ctx vs B1' | 34 | -0.088 [-0.500, +0.165] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, spread_mr_ctx vs B2 | 34 | -0.095 [-0.504, +0.159] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, spread_mr_ctx vs risk-date calendar (#693) | 34 | -0.095 [-0.504, +0.159] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, risk-date variant vs B1 | 34 | +0.311 [-0.040, +1.799] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, risk-date variant vs B1' | 34 | +0.301 [-0.038, +1.751] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, risk-date variant vs B2 | 34 | +0.294 [-0.015, +1.007] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, risk-date variant vs risk-date calendar (#693) | 34 | +0.294 [-0.015, +1.007] | undecided | no | 0 |
| quarter-end turn (Mar, Jun, Sep), upper-tail twCRPS, risk-date variant vs (s3c-ann-net) | 34 | +0.120 [+0.002, +0.977] | gain | no | 0 |
| tax date, upper-tail twCRPS, (s3c-ann-net) vs B2 | 71 | +0.721 [+0.125, +2.093] | gain | no | 0 |
| tax date, upper-tail twCRPS, (s3c-ann-net) vs risk-date calendar (#693) | 71 | +0.721 [+0.125, +2.093] | gain | no | 0 |
| tax date, upper-tail twCRPS, spread_mr_ctx vs B2 | 71 | +0.463 [+0.002, +1.579] | gain | no | 0 |
| tax date, upper-tail twCRPS, spread_mr_ctx vs risk-date calendar (#693) | 71 | +0.463 [+0.002, +1.579] | gain | no | 0 |
| tax date, upper-tail twCRPS, risk-date variant vs B2 | 71 | +0.686 [+0.106, +2.014] | gain | no | 0 |
| tax date, upper-tail twCRPS, risk-date variant vs risk-date calendar (#693) | 71 | +0.686 [+0.106, +2.014] | gain | no | 0 |

**Of these, the rows a stated reading is taken from:** quarter_end_turn, upper-tail twCRPS, risk-date variant vs (s3c-ann-net) (gain).

## 5. The strata

| stratum | events | per year | by calendar year | B1 | B1' | B2 | risk-date calendar (#693) | B2*-cap | B1'*-cap |
|---|---|---|---|---|---|---|---|---|---|
| union without the bill stratum (primary) | 413 | 72.5 | 2020: 55, 2021: 72, 2022: 75, 2023: 73, 2024: 69, 2025: 69 | 413 | 413 | 413 | 207 | 413 | 413 |
| union of the strata | 589 | 103.4 | 2020: 81, 2021: 78, 2022: 91, 2023: 133, 2024: 106, 2025: 100 | 589 | 589 | 589 | 207 | 589 | 589 |
| coupon settlement | 186 | 32.6 | 2020: 26, 2021: 35, 2022: 33, 2023: 31, 2024: 32, 2025: 29 | 186 | 186 | 186 | 111 | 186 | 186 |
| large bill settlement | 245 | 43.0 | 2020: 35, 2021: 9, 2022: 21, 2023: 86, 2024: 53, 2025: 41 | 245 | 245 | 245 | 33 | 245 | 245 |
| month-end turn | 92 | 16.1 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | 92 | 92 | 92 | 92 | 92 | 92 |
| quarter-end turn (Mar, Jun, Sep) | 34 | 6.0 | 2020: 4, 2021: 6, 2022: 6, 2023: 6, 2024: 6, 2025: 6 | 34 | 34 | 34 | 34 | 34 | 34 |
| year-end (thin) | 10 | 1.8 | 2020: 1, 2021: 2, 2022: 2, 2023: 2, 2024: 2, 2025: 1 | 10 | 10 | 10 | 10 | 10 | 10 |
| quarter-end and year-end | 44 | 7.7 | 2020: 5, 2021: 8, 2022: 8, 2023: 8, 2024: 8, 2025: 7 | 44 | 44 | 44 | 44 | 44 | 44 |
| tax date | 71 | 12.5 | 2020: 12, 2021: 12, 2022: 12, 2023: 12, 2024: 12, 2025: 11 | 71 | 71 | 71 | 71 | 71 | 71 |
| FOMC meeting day | 92 | 16.1 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | 92 | 92 | 92 | 26 | 92 | 92 |
| IORB-change window (two days after a meeting) | 92 | 16.1 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | 92 | 92 | 92 | 25 | 92 | 92 |

Columns after the year split: events each benchmark covers. The calendar benchmark exists only on a day typed as one of its four risk types at all five leads.

## 6. Skill by stratum: grid CRPS (primary)

Each cell: skill with its 90% interval; mean d (bp) with its 90% interval; the reading, from the mean-d lower end. Development data, not a verdict.

| stratum | benchmark | events | (s3c-ann-net) | risk-date variant | spread_mr_ctx |
|---|---|---|---|---|---|
| union without the bill stratum (primary) | B1 | 413 | +26.6% [+19.2%, +34.7%]; d +0.410 [+0.242, +0.648]; **gain** | +26.3% [+18.7%, +34.4%]; d +0.405 [+0.232, +0.649]; **gain** | +3.0% [-5.5%, +11.2%]; d +0.046 [-0.079, +0.191]; **undecided** |
| union without the bill stratum (primary) | B1' | 413 | +20.3% [+13.2%, +27.7%]; d +0.288 [+0.156, +0.469]; **gain** | +20.0% [+12.6%, +27.5%]; d +0.283 [+0.146, +0.472]; **gain** | -5.4% [-12.9%, +1.6%]; d -0.076 [-0.169, +0.020]; **undecided** |
| union without the bill stratum (primary) | B2 | 413 | +53.9% [+44.7%, +63.2%]; d +1.323 [+0.907, +2.011]; **gain** | +53.7% [+44.8%, +62.9%]; d +1.318 [+0.904, +2.005]; **gain** | +39.1% [+27.9%, +49.3%]; d +0.959 [+0.587, +1.514]; **gain** |
| union without the bill stratum (primary) | risk-date calendar (#693) | 207 | +59.0% [+47.4%, +69.5%]; d +1.857 [+1.221, +2.942]; **gain** | +59.2% [+48.5%, +69.5%]; d +1.866 [+1.237, +2.945]; **gain** | +41.5% [+28.0%, +52.6%]; d +1.307 [+0.750, +2.132]; **gain** |
| union without the bill stratum (primary) | B2*-cap | 413 | +64.0% [+57.1%, +70.3%]; d +2.008 [+1.541, +2.730]; **gain** | +63.8% [+57.3%, +70.0%]; d +2.003 [+1.534, +2.720]; **gain** | +52.4% [+44.0%, +59.4%]; d +1.644 [+1.219, +2.251]; **gain** |
| union without the bill stratum (primary) | B1'*-cap | 413 | +19.7% [+12.6%, +26.9%]; d +0.276 [+0.151, +0.448]; **gain** | +19.3% [+12.1%, +26.7%]; d +0.271 [+0.142, +0.451]; **gain** | -6.2% [-13.4%, +0.5%]; d -0.088 [-0.176, +0.002]; **undecided** |
| union of the strata | B1 | 589 | +25.6% [+19.7%, +31.8%]; d +0.393 [+0.260, +0.574]; **gain** | +25.1% [+19.1%, +31.4%]; d +0.385 [+0.250, +0.568]; **gain** | +6.7% [-0.2%, +13.6%]; d +0.103 [-0.004, +0.230]; **undecided** |
| union of the strata | B1' | 589 | +18.8% [+13.1%, +24.6%]; d +0.264 [+0.162, +0.397]; **gain** | +18.2% [+12.5%, +24.0%]; d +0.255 [+0.151, +0.389]; **gain** | -1.9% [-8.0%, +3.7%]; d -0.027 [-0.106, +0.053]; **undecided** |
| union of the strata | B2 | 589 | +51.3% [+43.4%, +58.6%]; d +1.201 [+0.866, +1.668]; **gain** | +50.9% [+43.3%, +58.1%]; d +1.192 [+0.859, +1.662]; **gain** | +38.9% [+29.4%, +47.2%]; d +0.910 [+0.605, +1.317]; **gain** |
| union of the strata | risk-date calendar (#693) | 207 | +59.0% [+47.4%, +69.5%]; d +1.857 [+1.221, +2.942]; **gain** | +59.2% [+48.5%, +69.5%]; d +1.866 [+1.237, +2.945]; **gain** | +41.5% [+28.0%, +52.6%]; d +1.307 [+0.750, +2.132]; **gain** |
| union of the strata | B2*-cap | 589 | +60.9% [+54.8%, +66.2%]; d +1.776 [+1.390, +2.296]; **gain** | +60.6% [+54.8%, +65.9%]; d +1.767 [+1.382, +2.289]; **gain** | +50.9% [+43.8%, +57.1%]; d +1.485 [+1.131, +1.946]; **gain** |
| union of the strata | B1'*-cap | 589 | +18.1% [+12.6%, +23.9%]; d +0.252 [+0.155, +0.378]; **gain** | +17.5% [+12.0%, +23.2%]; d +0.244 [+0.145, +0.372]; **gain** | -2.7% [-8.7%, +2.7%]; d -0.038 [-0.114, +0.037]; **undecided** |
| coupon settlement | B1 | 186 | +35.7% [+23.4%, +47.4%]; d +0.640 [+0.285, +1.203]; **gain** | +36.3% [+24.1%, +47.7%]; d +0.650 [+0.291, +1.213]; **gain** | +8.8% [-2.6%, +18.2%]; d +0.157 [-0.053, +0.417]; **undecided** |
| coupon settlement | B1' | 186 | +31.6% [+20.0%, +42.3%]; d +0.532 [+0.237, +0.989]; **gain** | +32.2% [+20.8%, +42.6%]; d +0.541 [+0.248, +0.997]; **gain** | +2.9% [-6.5%, +10.6%]; d +0.049 [-0.097, +0.216]; **undecided** |
| coupon settlement | B2 | 186 | +57.1% [+46.1%, +68.1%]; d +1.534 [+0.929, +2.748]; **gain** | +57.5% [+46.9%, +68.3%]; d +1.544 [+0.939, +2.755]; **gain** | +39.2% [+25.7%, +50.3%]; d +1.052 [+0.559, +1.883]; **gain** |
| coupon settlement | risk-date calendar (#693) | 111 | +60.3% [+48.5%, +71.8%]; d +2.042 [+1.207, +3.780]; **gain** | +60.9% [+49.7%, +72.0%]; d +2.062 [+1.235, +3.800]; **gain** | +40.3% [+25.6%, +52.1%]; d +1.365 [+0.700, +2.462]; **gain** |
| coupon settlement | B2*-cap | 186 | +67.2% [+60.0%, +74.3%]; d +2.363 [+1.669, +3.616]; **gain** | +67.5% [+60.6%, +74.4%]; d +2.373 [+1.680, +3.626]; **gain** | +53.5% [+44.1%, +61.4%]; d +1.881 [+1.295, +2.815]; **gain** |
| coupon settlement | B1'*-cap | 186 | +30.8% [+19.5%, +41.2%]; d +0.512 [+0.231, +0.944]; **gain** | +31.4% [+20.3%, +41.5%]; d +0.521 [+0.241, +0.954]; **gain** | +1.8% [-6.9%, +9.0%]; d +0.029 [-0.102, +0.175]; **undecided** |
| large bill settlement | B1 | 245 | +23.6% [+16.1%, +31.8%]; d +0.370 [+0.205, +0.620]; **gain** | +23.2% [+15.4%, +31.5%]; d +0.363 [+0.195, +0.619]; **gain** | +11.2% [+2.9%, +19.3%]; d +0.176 [+0.040, +0.354]; **gain** |
| large bill settlement | B1' | 245 | +15.7% [+8.7%, +23.4%]; d +0.224 [+0.103, +0.395]; **gain** | +15.2% [+8.4%, +22.5%]; d +0.217 [+0.096, +0.384]; **gain** | +2.1% [-4.6%, +8.4%]; d +0.030 [-0.060, +0.128]; **undecided** |
| large bill settlement | B2 | 245 | +46.7% [+35.0%, +57.8%]; d +1.048 [+0.593, +1.785]; **gain** | +46.3% [+34.9%, +57.5%]; d +1.041 [+0.584, +1.777]; **gain** | +38.0% [+25.5%, +50.0%]; d +0.854 [+0.442, +1.519]; **gain** |
| large bill settlement | risk-date calendar (#693) | 33 | +54.6% [+20.1%, +87.5%]; d +1.898 [+0.828, +5.723]; **gain** | +56.2% [+29.5%, +87.3%]; d +1.954 [+0.891, +5.277]; **gain** | +37.2% [-2.1%, +69.6%]; d +1.295 [+0.381, +3.798]; **gain** |
| large bill settlement | B2*-cap | 245 | +52.9% [+43.5%, +61.6%]; d +1.348 [+0.846, +2.135]; **gain** | +52.7% [+43.3%, +61.4%]; d +1.341 [+0.839, +2.130]; **gain** | +45.3% [+35.1%, +54.7%]; d +1.154 [+0.703, +1.885]; **gain** |
| large bill settlement | B1'*-cap | 245 | +14.8% [+7.9%, +22.3%]; d +0.209 [+0.095, +0.367]; **gain** | +14.3% [+7.7%, +21.4%]; d +0.202 [+0.088, +0.357]; **gain** | +1.1% [-5.5%, +7.1%]; d +0.015 [-0.073, +0.105]; **undecided** |
| month-end turn | B1 | 92 | +40.9% [+25.1%, +57.5%]; d +0.778 [+0.287, +1.812]; **gain** | +40.4% [+24.8%, +57.2%]; d +0.769 [+0.281, +1.807]; **gain** | +9.8% [-13.1%, +25.0%]; d +0.187 [-0.199, +0.619]; **undecided** |
| month-end turn | B1' | 92 | +33.4% [+19.5%, +48.8%]; d +0.564 [+0.224, +1.280]; **gain** | +32.9% [+19.2%, +48.4%]; d +0.555 [+0.217, +1.279]; **gain** | -1.6% [-13.2%, +8.7%]; d -0.028 [-0.204, +0.148]; **undecided** |
| month-end turn | B2 | 92 | +58.5% [+40.3%, +78.0%]; d +1.586 [+0.598, +4.972]; **gain** | +58.2% [+39.8%, +78.0%]; d +1.577 [+0.588, +4.991]; **gain** | +36.7% [+15.4%, +57.6%]; d +0.995 [+0.222, +3.237]; **gain** |
| month-end turn | risk-date calendar (#693) | 92 | +58.5% [+40.3%, +78.0%]; d +1.586 [+0.598, +4.972]; **gain** | +58.2% [+39.8%, +78.0%]; d +1.577 [+0.588, +4.991]; **gain** | +36.7% [+15.4%, +57.6%]; d +0.995 [+0.222, +3.237]; **gain** |
| month-end turn | B2*-cap | 92 | +68.8% [+58.3%, +78.5%]; d +2.475 [+1.390, +5.287]; **gain** | +68.5% [+57.9%, +78.5%]; d +2.466 [+1.379, +5.295]; **gain** | +52.4% [+40.9%, +62.3%]; d +1.884 [+1.019, +3.907]; **gain** |
| month-end turn | B1'*-cap | 92 | +32.1% [+18.0%, +47.3%]; d +0.530 [+0.199, +1.185]; **gain** | +31.5% [+17.7%, +46.9%]; d +0.521 [+0.195, +1.180]; **gain** | -3.7% [-14.4%, +6.3%]; d -0.061 [-0.223, +0.101]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | B1 | 34 | +26.6% [+18.1%, +34.7%]; d +0.851 [+0.153, +2.394]; **gain** | +33.5% [+23.7%, +43.0%]; d +1.073 [+0.193, +3.278]; **gain** | +6.4% [-8.3%, +15.0%]; d +0.206 [-0.382, +0.668]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | B1' | 34 | +24.6% [+15.0%, +33.5%]; d +0.766 [+0.090, +2.221]; **gain** | +31.7% [+20.5%, +42.0%]; d +0.988 [+0.138, +3.093]; **gain** | +3.9% [-14.0%, +13.0%]; d +0.121 [-0.493, +0.558]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | B2 | 34 | +32.6% [-33.1%, +57.3%]; d +1.135 [-0.444, +2.069]; **undecided** | +39.0% [-12.4%, +59.6%]; d +1.357 [+0.102, +2.239]; **gain** | +14.1% [-79.1%, +47.7%]; d +0.490 [-1.660, +1.711]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | risk-date calendar (#693) | 34 | +32.6% [-33.1%, +57.3%]; d +1.135 [-0.444, +2.069]; **undecided** | +39.0% [-12.4%, +59.6%]; d +1.357 [+0.102, +2.239]; **gain** | +14.1% [-79.1%, +47.7%]; d +0.490 [-1.660, +1.711]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | B2*-cap | 34 | +48.6% [+11.1%, +74.6%]; d +2.216 [+1.111, +3.349]; **gain** | +53.4% [+23.6%, +75.6%]; d +2.438 [+1.490, +3.482]; **gain** | +34.4% [-34.3%, +65.2%]; d +1.571 [+0.047, +2.776]; **gain** |
| quarter-end turn (Mar, Jun, Sep) | B1'*-cap | 34 | +23.4% [+13.7%, +32.4%]; d +0.717 [+0.085, +2.085]; **gain** | +30.7% [+19.4%, +41.1%]; d +0.939 [+0.132, +2.997]; **gain** | +2.4% [-15.0%, +11.3%]; d +0.073 [-0.485, +0.464]; **undecided** |
| year-end | B1 | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B1' | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B2 | 10 | thin (10) | thin (10) | thin (10) |
| year-end | risk-date calendar (#693) | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B2*-cap | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B1'*-cap | 10 | thin (10) | thin (10) | thin (10) |
| quarter-end and year-end | B1 | 44 | +30.2% [+19.4%, +43.6%]; d +0.920 [+0.175, +2.606]; **gain** | +35.4% [+23.7%, +48.3%]; d +1.076 [+0.214, +3.062]; **gain** | +8.9% [-5.1%, +18.8%]; d +0.272 [-0.252, +0.851]; **undecided** |
| quarter-end and year-end | B1' | 44 | +28.6% [+16.7%, +43.3%]; d +0.851 [+0.122, +2.540]; **gain** | +33.9% [+21.0%, +48.0%]; d +1.008 [+0.161, +2.997]; **gain** | +6.9% [-9.0%, +17.6%]; d +0.204 [-0.318, +0.773]; **undecided** |
| quarter-end and year-end | B2 | 44 | +34.7% [-4.9%, +53.0%]; d +1.127 [+0.004, +1.866]; **gain** | +39.5% [+7.5%, +55.3%]; d +1.284 [+0.330, +2.045]; **gain** | +14.8% [-41.8%, +43.2%]; d +0.480 [-1.026, +1.451]; **undecided** |
| quarter-end and year-end | risk-date calendar (#693) | 44 | +43.3% [+8.2%, +62.6%]; d +1.620 [+0.488, +2.489]; **gain** | +47.5% [+18.8%, +64.1%]; d +1.777 [+0.789, +2.631]; **gain** | +26.0% [-25.2%, +54.2%]; d +0.973 [-0.553, +2.079]; **undecided** |
| quarter-end and year-end | B2*-cap | 44 | +51.0% [+26.8%, +67.7%]; d +2.206 [+1.433, +3.046]; **gain** | +54.6% [+35.4%, +69.0%]; d +2.362 [+1.673, +3.212]; **gain** | +36.0% [-4.8%, +58.5%]; d +1.559 [+0.611, +2.338]; **gain** |
| quarter-end and year-end | B1'*-cap | 44 | +27.6% [+15.5%, +42.6%]; d +0.809 [+0.111, +2.458]; **gain** | +32.9% [+20.1%, +47.5%]; d +0.966 [+0.157, +2.923]; **gain** | +5.5% [-10.1%, +16.4%]; d +0.162 [-0.319, +0.690]; **undecided** |
| tax date | B1 | 71 | +19.6% [-3.2%, +37.7%]; d +0.243 [-0.008, +0.609]; **undecided** | +14.9% [-7.9%, +35.6%]; d +0.185 [-0.072, +0.579]; **undecided** | -15.7% [-44.7%, +10.9%]; d -0.194 [-0.459, +0.092]; **undecided** |
| tax date | B1' | 71 | +12.5% [-7.1%, +30.1%]; d +0.143 [-0.053, +0.415]; **undecided** | +7.3% [-13.0%, +27.1%]; d +0.084 [-0.117, +0.374]; **undecided** | -25.9% [-53.3%, -0.4%]; d -0.295 [-0.521, -0.058]; **loss** |
| tax date | B2 | 71 | +70.2% [+58.1%, +82.3%]; d +2.355 [+1.446, +3.807]; **gain** | +68.5% [+57.2%, +80.1%]; d +2.296 [+1.398, +3.728]; **gain** | +57.2% [+44.9%, +67.4%]; d +1.917 [+1.134, +3.093]; **gain** |
| tax date | risk-date calendar (#693) | 71 | +70.2% [+58.1%, +82.3%]; d +2.355 [+1.446, +3.807]; **gain** | +68.5% [+57.2%, +80.1%]; d +2.296 [+1.398, +3.728]; **gain** | +57.2% [+44.9%, +67.4%]; d +1.917 [+1.134, +3.093]; **gain** |
| tax date | B2*-cap | 71 | +73.6% [+63.8%, +82.2%]; d +2.788 [+1.733, +3.946]; **gain** | +72.1% [+63.0%, +80.2%]; d +2.730 [+1.692, +3.875]; **gain** | +62.1% [+51.9%, +69.9%]; d +2.351 [+1.431, +3.350]; **gain** |
| tax date | B1'*-cap | 71 | +12.4% [-7.5%, +29.2%]; d +0.142 [-0.051, +0.395]; **undecided** | +7.3% [-12.7%, +26.0%]; d +0.083 [-0.112, +0.351]; **undecided** | -26.0% [-51.6%, -1.4%]; d -0.296 [-0.514, -0.073]; **loss** |
| FOMC meeting day | B1 | 92 | +14.1% [+0.8%, +26.4%]; d +0.187 [+0.020, +0.394]; **gain** | +12.3% [-1.0%, +24.8%]; d +0.163 [-0.009, +0.381]; **undecided** | +0.2% [-14.5%, +14.6%]; d +0.002 [-0.180, +0.195]; **undecided** |
| FOMC meeting day | B1' | 92 | +0.6% [-11.9%, +12.2%]; d +0.007 [-0.127, +0.144]; **undecided** | -1.5% [-14.6%, +10.5%]; d -0.017 [-0.152, +0.125]; **undecided** | -15.4% [-29.7%, -1.6%]; d -0.177 [-0.350, -0.028]; **loss** |
| FOMC meeting day | B2 | 92 | +45.8% [+28.2%, +61.2%]; d +0.964 [+0.439, +1.811]; **gain** | +44.6% [+27.4%, +60.1%]; d +0.940 [+0.426, +1.794]; **gain** | +37.0% [+17.3%, +52.5%]; d +0.779 [+0.289, +1.497]; **gain** |
| FOMC meeting day | risk-date calendar (#693) | 26 | thin (26) | thin (26) | thin (26) |
| FOMC meeting day | B2*-cap | 92 | +57.8% [+43.9%, +70.2%]; d +1.565 [+0.880, +2.645]; **gain** | +56.9% [+43.1%, +69.2%]; d +1.541 [+0.861, +2.623]; **gain** | +51.0% [+34.6%, +63.7%]; d +1.380 [+0.703, +2.337]; **gain** |
| FOMC meeting day | B1'*-cap | 92 | +0.1% [-12.3%, +11.7%]; d +0.001 [-0.133, +0.134]; **undecided** | -2.1% [-14.8%, +9.8%]; d -0.023 [-0.155, +0.113]; **undecided** | -16.1% [-30.0%, -2.6%]; d -0.184 [-0.356, -0.040]; **loss** |
| IORB-change window (two days after a meeting) | B1 | 92 | +19.0% [+5.2%, +33.0%]; d +0.244 [+0.049, +0.630]; **gain** | +16.3% [+2.2%, +30.5%]; d +0.210 [+0.019, +0.576]; **gain** | -8.6% [-26.8%, +7.2%]; d -0.110 [-0.317, +0.081]; **undecided** |
| IORB-change window (two days after a meeting) | B1' | 92 | +9.8% [-2.7%, +22.7%]; d +0.113 [-0.021, +0.348]; **undecided** | +6.8% [-5.9%, +20.2%]; d +0.079 [-0.053, +0.295]; **undecided** | -20.9% [-38.9%, -8.4%]; d -0.241 [-0.459, -0.104]; **loss** |
| IORB-change window (two days after a meeting) | B2 | 92 | +57.4% [+40.3%, +71.0%]; d +1.400 [+0.697, +3.067]; **gain** | +56.0% [+38.8%, +70.0%]; d +1.365 [+0.668, +3.013]; **gain** | +42.9% [+15.2%, +57.8%]; d +1.045 [+0.369, +2.228]; **gain** |
| IORB-change window (two days after a meeting) | risk-date calendar (#693) | 25 | thin (25) | thin (25) | thin (25) |
| IORB-change window (two days after a meeting) | B2*-cap | 92 | +65.1% [+49.9%, +75.4%]; d +1.942 [+1.073, +3.583]; **gain** | +64.0% [+48.9%, +74.5%]; d +1.907 [+1.041, +3.535]; **gain** | +53.2% [+29.1%, +65.6%]; d +1.587 [+0.721, +2.895]; **gain** |
| IORB-change window (two days after a meeting) | B1'*-cap | 92 | +9.8% [-2.5%, +21.6%]; d +0.113 [-0.017, +0.322]; **undecided** | +6.8% [-5.6%, +19.1%]; d +0.078 [-0.047, +0.273]; **undecided** | -21.0% [-38.8%, -9.3%]; d -0.242 [-0.470, -0.103]; **loss** |

## 6. Skill by stratum: upper-tail twCRPS (key secondary)

Each cell: skill with its 90% interval; mean d (bp) with its 90% interval; the reading, from the mean-d lower end. Development data, not a verdict.

| stratum | benchmark | events | (s3c-ann-net) | risk-date variant | spread_mr_ctx |
|---|---|---|---|---|---|
| union without the bill stratum (primary) | B1 | 413 | +30.3% [+15.5%, +50.1%]; d +0.133 [+0.031, +0.395]; **gain** | +29.0% [+13.9%, +47.5%]; d +0.127 [+0.021, +0.379]; **gain** | -12.7% [-41.2%, +8.8%]; d -0.056 [-0.134, +0.037]; **undecided** |
| union without the bill stratum (primary) | B1' | 413 | +28.1% [+17.1%, +42.1%]; d +0.119 [+0.040, +0.293]; **gain** | +26.7% [+15.7%, +39.7%]; d +0.113 [+0.030, +0.278]; **gain** | -16.3% [-37.0%, -1.1%]; d -0.069 [-0.127, -0.016]; **loss** |
| union without the bill stratum (primary) | B2 | 413 | +57.4% [+39.7%, +71.4%]; d +0.411 [+0.149, +1.067]; **gain** | +56.6% [+40.0%, +70.7%]; d +0.405 [+0.144, +1.059]; **gain** | +31.1% [+9.7%, +52.0%]; d +0.223 [+0.024, +0.725]; **gain** |
| union without the bill stratum (primary) | risk-date calendar (#693) | 207 | +63.1% [+38.3%, +78.2%]; d +0.667 [+0.199, +1.937]; **gain** | +62.8% [+41.4%, +77.5%]; d +0.663 [+0.198, +1.940]; **gain** | +32.5% [+5.9%, +54.9%]; d +0.343 [-0.002, +1.248]; **undecided** |
| union without the bill stratum (primary) | B2*-cap | 413 | +65.2% [+53.3%, +73.6%]; d +0.572 [+0.305, +1.259]; **gain** | +64.5% [+54.2%, +72.6%]; d +0.566 [+0.300, +1.255]; **gain** | +43.7% [+32.2%, +54.4%]; d +0.384 [+0.183, +0.934]; **gain** |
| union without the bill stratum (primary) | B1'*-cap | 413 | +27.3% [+16.8%, +40.7%]; d +0.114 [+0.040, +0.274]; **gain** | +25.8% [+15.3%, +38.3%]; d +0.108 [+0.030, +0.261]; **gain** | -17.7% [-37.5%, -3.0%]; d -0.074 [-0.132, -0.024]; **loss** |
| union of the strata | B1 | 589 | +32.5% [+21.9%, +44.7%]; d +0.154 [+0.066, +0.324]; **gain** | +31.4% [+21.1%, +43.4%]; d +0.149 [+0.058, +0.318]; **gain** | +2.5% [-14.7%, +18.1%]; d +0.012 [-0.057, +0.110]; **undecided** |
| union of the strata | B1' | 589 | +25.3% [+15.8%, +36.6%]; d +0.108 [+0.048, +0.222]; **gain** | +24.0% [+15.1%, +34.6%]; d +0.103 [+0.041, +0.215]; **gain** | -8.0% [-22.1%, +3.7%]; d -0.034 [-0.081, +0.015]; **undecided** |
| union of the strata | B2 | 589 | +53.2% [+41.1%, +63.9%]; d +0.364 [+0.181, +0.722]; **gain** | +52.4% [+40.9%, +63.1%]; d +0.359 [+0.175, +0.717]; **gain** | +32.4% [+17.9%, +46.5%]; d +0.221 [+0.074, +0.507]; **gain** |
| union of the strata | risk-date calendar (#693) | 207 | +63.1% [+38.3%, +78.2%]; d +0.667 [+0.199, +1.937]; **gain** | +62.8% [+41.4%, +77.5%]; d +0.663 [+0.198, +1.940]; **gain** | +32.5% [+5.9%, +54.9%]; d +0.343 [-0.002, +1.248]; **undecided** |
| union of the strata | B2*-cap | 589 | +59.9% [+50.3%, +67.5%]; d +0.478 [+0.290, +0.864]; **gain** | +59.2% [+50.6%, +66.5%]; d +0.473 [+0.283, +0.860]; **gain** | +42.0% [+32.4%, +50.7%]; d +0.336 [+0.190, +0.646]; **gain** |
| union of the strata | B1'*-cap | 589 | +24.3% [+15.0%, +35.3%]; d +0.103 [+0.046, +0.208]; **gain** | +23.0% [+14.3%, +33.3%]; d +0.097 [+0.039, +0.200]; **gain** | -9.5% [-23.0%, +1.9%]; d -0.040 [-0.086, +0.006]; **undecided** |
| coupon settlement | B1 | 186 | +38.8% [+15.4%, +63.8%]; d +0.227 [-0.016, +1.121]; **undecided** | +38.2% [+14.1%, +62.8%]; d +0.223 [-0.020, +1.090]; **undecided** | -5.8% [-50.0%, +23.2%]; d -0.034 [-0.168, +0.195]; **undecided** |
| coupon settlement | B1' | 186 | +38.5% [+22.1%, +56.7%]; d +0.224 [+0.019, +0.854]; **gain** | +38.0% [+21.2%, +56.1%]; d +0.221 [+0.015, +0.838]; **gain** | -6.2% [-36.3%, +13.9%]; d -0.036 [-0.130, +0.090]; **undecided** |
| coupon settlement | B2 | 186 | +59.1% [+40.5%, +77.4%]; d +0.517 [+0.083, +2.173]; **gain** | +58.7% [+40.1%, +77.6%]; d +0.514 [+0.079, +2.190]; **gain** | +29.3% [+4.2%, +53.0%]; d +0.257 [-0.036, +1.297]; **undecided** |
| coupon settlement | risk-date calendar (#693) | 111 | +64.6% [+45.8%, +78.8%]; d +0.784 [+0.097, +3.391]; **gain** | +64.2% [+45.9%, +78.7%]; d +0.780 [+0.093, +3.413]; **gain** | +32.8% [+7.5%, +52.3%]; d +0.398 [-0.067, +2.006]; **undecided** |
| coupon settlement | B2*-cap | 186 | +67.2% [+56.5%, +79.0%]; d +0.733 [+0.280, +2.411]; **gain** | +66.9% [+56.7%, +79.2%]; d +0.730 [+0.279, +2.445]; **gain** | +43.3% [+32.0%, +54.7%]; d +0.473 [+0.163, +1.689]; **gain** |
| coupon settlement | B1'*-cap | 186 | +37.5% [+21.7%, +54.9%]; d +0.215 [+0.021, +0.796]; **gain** | +37.0% [+20.8%, +54.3%]; d +0.212 [+0.016, +0.782]; **gain** | -7.9% [-36.7%, +11.0%]; d -0.045 [-0.131, +0.057]; **undecided** |
| large bill settlement | B1 | 245 | +34.6% [+19.3%, +49.6%]; d +0.206 [+0.078, +0.472]; **gain** | +35.2% [+21.5%, +48.8%]; d +0.210 [+0.078, +0.470]; **gain** | +18.8% [+3.8%, +34.1%]; d +0.112 [+0.019, +0.290]; **gain** |
| large bill settlement | B1' | 245 | +21.8% [+7.2%, +42.1%]; d +0.109 [+0.026, +0.309]; **gain** | +22.6% [+10.0%, +39.9%]; d +0.113 [+0.030, +0.299]; **gain** | +3.0% [-8.7%, +15.0%]; d +0.015 [-0.036, +0.085]; **undecided** |
| large bill settlement | B2 | 245 | +49.3% [+34.6%, +62.3%]; d +0.379 [+0.171, +0.806]; **gain** | +49.8% [+36.9%, +61.8%]; d +0.383 [+0.173, +0.812]; **gain** | +37.1% [+24.0%, +49.5%]; d +0.285 [+0.119, +0.601]; **gain** |
| large bill settlement | risk-date calendar (#693) | 33 | skill undefined; d +0.859 [+0.107, +9.457]; **gain** | skill undefined; d +0.902 [+0.152, +5.166]; **gain** | skill undefined; d +0.493 [-0.015, +4.346]; **undecided** |
| large bill settlement | B2*-cap | 245 | +50.6% [+36.8%, +61.4%]; d +0.399 [+0.180, +0.902]; **gain** | +51.1% [+39.2%, +61.0%]; d +0.402 [+0.182, +0.907]; **gain** | +38.7% [+27.1%, +48.5%]; d +0.305 [+0.134, +0.677]; **gain** |
| large bill settlement | B1'*-cap | 245 | +20.5% [+6.0%, +40.0%]; d +0.100 [+0.024, +0.283]; **gain** | +21.3% [+9.0%, +37.9%]; d +0.104 [+0.028, +0.272]; **gain** | +1.3% [-10.2%, +12.8%]; d +0.006 [-0.042, +0.066]; **undecided** |
| month-end turn | B1 | 92 | +45.9% [+17.4%, +95.2%]; d +0.271 [-0.085, +4.251]; **undecided** | +43.4% [+10.4%, +103.6%]; d +0.256 [-0.102, +3.955]; **undecided** | -18.5% [-147.3%, +108.7%]; d -0.109 [-0.385, +0.193]; **undecided** |
| month-end turn | B1' | 92 | +47.6% [+30.1%, +68.4%]; d +0.290 [+0.029, +1.876]; **gain** | +45.2% [+29.1%, +67.4%]; d +0.276 [+0.014, +1.956]; **gain** | -14.7% [-46.7%, +42.2%]; d -0.089 [-0.196, -0.004]; **loss** |
| month-end turn | B2 | 92 | +72.1% [+62.3%, +80.6%]; d +0.827 [+0.003, +9.640]; **gain** | +70.9% [+58.9%, +80.2%]; d +0.812 [-0.015, +9.501]; **undecided** | +39.0% [-5.4%, +65.3%]; d +0.447 [-0.153, +4.391]; **undecided** |
| month-end turn | risk-date calendar (#693) | 92 | +72.1% [+62.3%, +80.6%]; d +0.827 [+0.003, +9.640]; **gain** | +70.9% [+58.9%, +80.2%]; d +0.812 [-0.015, +9.501]; **undecided** | +39.0% [-5.4%, +65.3%]; d +0.447 [-0.153, +4.391]; **undecided** |
| month-end turn | B2*-cap | 92 | +77.1% [+69.9%, +83.9%]; d +1.073 [+0.214, +6.366]; **gain** | +76.0% [+69.5%, +82.9%]; d +1.059 [+0.202, +6.499]; **gain** | +49.8% [+37.2%, +60.6%]; d +0.694 [+0.093, +5.893]; **gain** |
| month-end turn | B1'*-cap | 92 | +46.5% [+28.2%, +66.7%]; d +0.278 [+0.032, +1.612]; **gain** | +44.1% [+27.6%, +65.3%]; d +0.263 [+0.018, +1.673]; **gain** | -17.0% [-45.7%, +27.2%]; d -0.102 [-0.210, -0.029]; **loss** |
| quarter-end turn (Mar, Jun, Sep) | B1 | 34 | skill undefined; d +0.191 [-0.041, +1.080]; **undecided** | skill undefined; d +0.311 [-0.040, +1.799]; **undecided** | skill undefined; d -0.078 [-0.480, +0.193]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | B1' | 34 | skill undefined; d +0.181 [-0.039, +1.016]; **undecided** | skill undefined; d +0.301 [-0.038, +1.751]; **undecided** | skill undefined; d -0.088 [-0.500, +0.165]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | B2 | 34 | skill undefined; d +0.174 [-0.142, +0.632]; **undecided** | skill undefined; d +0.294 [-0.015, +1.007]; **undecided** | skill undefined; d -0.095 [-0.504, +0.159]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | risk-date calendar (#693) | 34 | skill undefined; d +0.174 [-0.142, +0.632]; **undecided** | skill undefined; d +0.294 [-0.015, +1.007]; **undecided** | skill undefined; d -0.095 [-0.504, +0.159]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | B2*-cap | 34 | skill undefined; d +0.645 [+0.081, +1.876]; **gain** | +46.9% [-22.5%, +98.4%]; d +0.766 [+0.179, +1.736]; **gain** | +23.1% [-54.9%, +78.4%]; d +0.377 [-0.059, +1.503]; **undecided** |
| quarter-end turn (Mar, Jun, Sep) | B1'*-cap | 34 | skill undefined; d +0.168 [-0.039, +0.923]; **undecided** | +24.9% [+11.9%, +41.4%]; d +0.288 [-0.038, +1.679]; **undecided** | -8.8% [-64.7%, +11.1%]; d -0.101 [-0.540, +0.133]; **undecided** |
| year-end | B1 | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B1' | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B2 | 10 | thin (10) | thin (10) | thin (10) |
| year-end | risk-date calendar (#693) | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B2*-cap | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B1'*-cap | 10 | thin (10) | thin (10) | thin (10) |
| quarter-end and year-end | B1 | 44 | +23.8% [+11.8%, +40.9%]; d +0.269 [-0.028, +1.445]; **undecided** | +30.2% [+17.7%, +43.2%]; d +0.341 [-0.036, +1.674]; **undecided** | -3.7% [-42.5%, +14.9%]; d -0.042 [-0.358, +0.271]; **undecided** |
| quarter-end and year-end | B1' | 44 | +23.9% [+11.9%, +41.3%]; d +0.269 [-0.026, +1.479]; **undecided** | +30.3% [+18.0%, +43.4%]; d +0.341 [-0.033, +1.668]; **undecided** | -3.7% [-40.8%, +15.1%]; d -0.042 [-0.347, +0.272]; **undecided** |
| quarter-end and year-end | B2 | 44 | +15.3% [-13.6%, +35.9%]; d +0.155 [-0.100, +0.568]; **undecided** | +22.4% [+0.5%, +38.9%]; d +0.228 [-0.032, +0.875]; **undecided** | -15.3% [-50.3%, +10.5%]; d -0.156 [-0.454, +0.056]; **undecided** |
| quarter-end and year-end | risk-date calendar (#693) | 44 | +22.1% [-6.4%, +46.9%]; d +0.244 [-0.065, +1.058]; **undecided** | +28.6% [+5.7%, +47.8%]; d +0.316 [-0.018, +1.405]; **undecided** | -6.1% [-48.0%, +19.8%]; d -0.067 [-0.371, +0.191]; **undecided** |
| quarter-end and year-end | B2*-cap | 44 | +43.2% [-17.7%, +83.9%]; d +0.652 [+0.143, +1.481]; **gain** | +47.9% [+0.5%, +82.9%]; d +0.724 [+0.198, +1.522]; **gain** | +22.6% [-29.6%, +68.5%]; d +0.341 [-0.025, +1.172]; **undecided** |
| quarter-end and year-end | B1'*-cap | 44 | +23.2% [+11.5%, +40.6%]; d +0.259 [-0.027, +1.438]; **undecided** | +29.6% [+17.5%, +42.7%]; d +0.331 [-0.033, +1.626]; **undecided** | -4.6% [-42.2%, +14.4%]; d -0.052 [-0.352, +0.245]; **undecided** |
| tax date | B1 | 71 | +35.3% [+1.0%, +62.8%]; d +0.105 [-0.038, +0.700]; **undecided** | +23.5% [-44.6%, +79.5%]; d +0.070 [-0.086, +0.538]; **undecided** | -51.5% [-291.6%, +126.5%]; d -0.153 [-0.465, +0.062]; **undecided** |
| tax date | B1' | 71 | +28.0% [-6.2%, +58.9%]; d +0.075 [-0.031, +0.556]; **undecided** | +14.8% [-54.7%, +76.9%]; d +0.040 [-0.079, +0.362]; **undecided** | -68.6% [-300.3%, +166.8%]; d -0.183 [-0.493, +0.003]; **undecided** |
| tax date | B2 | 71 | skill undefined; d +0.721 [+0.125, +2.093]; **gain** | skill undefined; d +0.686 [+0.106, +2.014]; **gain** | skill undefined; d +0.463 [+0.002, +1.579]; **gain** |
| tax date | risk-date calendar (#693) | 71 | skill undefined; d +0.721 [+0.125, +2.093]; **gain** | skill undefined; d +0.686 [+0.106, +2.014]; **gain** | skill undefined; d +0.463 [+0.002, +1.579]; **gain** |
| tax date | B2*-cap | 71 | +80.6% [+58.8%, +91.8%]; d +0.803 [+0.297, +1.552]; **gain** | +77.1% [+61.3%, +87.1%]; d +0.768 [+0.284, +1.490]; **gain** | +54.7% [+41.1%, +64.4%]; d +0.545 [+0.222, +1.042]; **gain** |
| tax date | B1'*-cap | 71 | +27.2% [-4.9%, +55.7%]; d +0.072 [-0.027, +0.473]; **undecided** | +13.9% [-52.5%, +73.1%]; d +0.037 [-0.076, +0.330]; **undecided** | -70.4% [-296.0%, +169.3%]; d -0.186 [-0.499, -0.006]; **loss** |
| FOMC meeting day | B1 | 92 | +6.5% [-16.4%, +26.7%]; d +0.016 [-0.031, +0.099]; **undecided** | +0.1% [-38.9%, +38.3%]; d +0.000 [-0.061, +0.091]; **undecided** | -30.5% [-77.2%, +18.0%]; d -0.076 [-0.211, +0.000]; **undecided** |
| FOMC meeting day | B1' | 92 | -8.2% [-39.9%, +20.8%]; d -0.018 [-0.065, +0.021]; **undecided** | -15.6% [-74.2%, +36.8%]; d -0.034 [-0.101, +0.017]; **undecided** | -51.0% [-114.9%, +34.2%]; d -0.110 [-0.318, -0.024]; **loss** |
| FOMC meeting day | B2 | 92 | +44.8% [+22.0%, +57.9%]; d +0.189 [+0.010, +0.916]; **gain** | +41.0% [+13.1%, +56.6%]; d +0.173 [-0.008, +0.893]; **undecided** | +23.0% [-5.0%, +38.5%]; d +0.097 [-0.028, +0.435]; **undecided** |
| FOMC meeting day | risk-date calendar (#693) | 26 | thin (26) | thin (26) | thin (26) |
| FOMC meeting day | B2*-cap | 92 | +56.8% [+35.9%, +66.6%]; d +0.306 [+0.101, +0.974]; **gain** | +53.9% [+37.8%, +61.8%]; d +0.290 [+0.088, +1.014]; **gain** | +39.7% [+14.5%, +49.4%]; d +0.214 [+0.070, +0.617]; **gain** |
| FOMC meeting day | B1'*-cap | 92 | -7.9% [-37.4%, +17.3%]; d -0.017 [-0.065, +0.020]; **undecided** | -15.3% [-69.8%, +32.4%]; d -0.033 [-0.100, +0.015]; **undecided** | -50.6% [-110.5%, +29.5%]; d -0.109 [-0.321, -0.024]; **loss** |
| IORB-change window (two days after a meeting) | B1 | 92 | +28.7% [+2.6%, +58.4%]; d +0.094 [-0.029, +0.839]; **undecided** | +23.1% [-9.5%, +70.9%]; d +0.075 [-0.041, +0.711]; **undecided** | -21.6% [-100.3%, +39.5%]; d -0.070 [-0.210, +0.008]; **undecided** |
| IORB-change window (two days after a meeting) | B1' | 92 | +22.9% [+4.4%, +38.4%]; d +0.069 [-0.011, +0.497]; **undecided** | +16.8% [-7.6%, +40.2%]; d +0.051 [-0.025, +0.375]; **undecided** | -31.6% [-89.2%, +22.6%]; d -0.095 [-0.240, -0.033]; **loss** |
| IORB-change window (two days after a meeting) | B2 | 92 | +64.8% [+53.2%, +73.4%]; d +0.428 [+0.022, +3.893]; **gain** | +62.1% [+47.7%, +72.0%]; d +0.410 [+0.010, +3.720]; **gain** | +40.0% [+17.2%, +58.5%]; d +0.264 [-0.037, +2.884]; **undecided** |
| IORB-change window (two days after a meeting) | risk-date calendar (#693) | 25 | thin (25) | thin (25) | thin (25) |
| IORB-change window (two days after a meeting) | B2*-cap | 92 | +69.7% [+57.7%, +76.1%]; d +0.534 [+0.130, +2.899]; **gain** | +67.3% [+55.9%, +73.4%]; d +0.516 [+0.119, +2.859]; **gain** | +48.3% [+36.3%, +55.0%]; d +0.370 [+0.082, +2.180]; **gain** |
| IORB-change window (two days after a meeting) | B1'*-cap | 92 | +22.1% [+4.5%, +35.8%]; d +0.066 [-0.008, +0.436]; **undecided** | +15.9% [-7.1%, +37.1%]; d +0.048 [-0.022, +0.330]; **undecided** | -33.0% [-85.1%, +15.8%]; d -0.098 [-0.257, -0.033]; **loss** |

## 7. The variant against (s3c-ann-net)

Paired on the same events, same bootstrap; positive favours the variant. d is in bp.

| cut | events | grid CRPS: variant over (s3c-ann-net) | upper-tail twCRPS: variant over (s3c-ann-net) |
|---|---|---|---|
| union without the bill stratum (primary) | 413 | -0.4% [-2.1%, +1.7%]; d -0.005 [-0.021, +0.021]; **undecided** | -2.0% [-7.1%, +4.5%]; d -0.006 [-0.017, +0.016]; **undecided** |
| union of the strata | 589 | -0.7% [-2.0%, +0.8%]; d -0.008 [-0.021, +0.009]; **undecided** | -1.7% [-5.3%, +2.7%]; d -0.005 [-0.014, +0.010]; **undecided** |
| coupon settlement | 186 | +0.8% [-0.3%, +2.3%]; d +0.010 [-0.004, +0.028]; **undecided** | -0.9% [-3.8%, +2.9%]; d -0.003 [-0.012, +0.015]; **undecided** |
| large bill settlement | 245 | -0.6% [-2.2%, +1.9%]; d -0.007 [-0.023, +0.022]; **undecided** | +1.0% [-3.1%, +6.8%]; d +0.004 [-0.009, +0.038]; **undecided** |
| month-end turn | 92 | -0.8% [-2.3%, +0.4%]; d -0.009 [-0.024, +0.004]; **undecided** | -4.5% [-15.6%, +4.1%]; d -0.014 [-0.034, -0.005]; **loss** |
| quarter-end turn (Mar, Jun, Sep) | 34 | +9.5% [+5.1%, +14.2%]; d +0.222 [+0.037, +0.753]; **gain** | skill undefined; d +0.120 [+0.002, +0.977]; **gain** |
| year-end | 10 | thin (10) | thin (10) |
| quarter-end and year-end | 44 | +7.4% [+3.8%, +11.4%]; d +0.156 [+0.043, +0.439]; **gain** | +8.4% [+1.7%, +14.1%]; d +0.072 [-0.006, +0.409]; **undecided** |
| tax date | 71 | -5.9% [-15.3%, -1.0%]; d -0.059 [-0.132, -0.018]; **loss** | -18.3% [-57.0%, +8.7%]; d -0.035 [-0.102, -0.010]; **loss** |
| FOMC meeting day | 92 | -2.1% [-5.2%, +0.2%]; d -0.024 [-0.049, -0.000]; **loss** | -6.8% [-28.2%, +13.1%]; d -0.016 [-0.041, +0.002]; **undecided** |
| IORB-change window (two days after a meeting) | 92 | -3.3% [-5.9%, -1.5%]; d -0.035 [-0.064, -0.015]; **loss** | -7.8% [-19.4%, +0.3%]; d -0.018 [-0.042, -0.007]; **loss** |

## 8. By regime and by pressure-day type (the union without the bill stratum)

The pressure-day-type rows bootstrap each group's own days, as #724 did; they are not the studentized domain interval she ruled for H5 day-type rows (#1454). Whether that ruling also covers H6 pages is for her; this page does not change it (question in the pull request).

### Regime: grid CRPS

| stratum | benchmark | events | (s3c-ann-net) | risk-date variant | spread_mr_ctx |
|---|---|---|---|---|---|
| 2020 | B1 | 55 | +10.8% [-3.6%, +24.2%]; d +0.114 [-0.039, +0.260]; **undecided** | +3.4% [-11.7%, +18.2%]; d +0.035 [-0.119, +0.195]; **undecided** | -52.6% [-73.5%, -35.4%]; d -0.552 [-0.731, -0.396]; **loss** |
| 2020 | B1' | 55 | +12.0% [-5.7%, +28.5%]; d +0.128 [-0.054, +0.324]; **undecided** | +4.6% [-15.1%, +24.1%]; d +0.049 [-0.148, +0.275]; **undecided** | -50.6% [-73.1%, -31.8%]; d -0.538 [-0.720, -0.377]; **loss** |
| 2020 | B2 | 55 | +68.5% [+44.8%, +88.4%]; d +2.038 [+0.612, +4.906]; **gain** | +65.9% [+39.9%, +88.5%]; d +1.959 [+0.530, +4.889]; **gain** | +46.2% [+11.0%, +79.5%]; d +1.372 [+0.019, +4.254]; **gain** |
| 2020 | B2*-cap | 55 | +68.5% [+54.5%, +83.1%]; d +2.032 [+1.126, +3.666]; **gain** | +65.8% [+50.7%, +82.9%]; d +1.953 [+1.041, +3.664]; **gain** | +46.1% [+27.6%, +71.5%]; d +1.366 [+0.549, +3.132]; **gain** |
| 2021-23 | B1 | 220 | -0.2% [-13.8%, +8.2%]; d -0.001 [-0.102, +0.059]; **undecided** | -1.1% [-14.3%, +7.0%]; d -0.008 [-0.103, +0.051]; **undecided** | -13.7% [-28.8%, -2.6%]; d -0.101 [-0.208, -0.021]; **loss** |
| 2021-23 | B1' | 220 | -3.0% [-13.8%, +5.9%]; d -0.021 [-0.102, +0.040]; **undecided** | -4.0% [-14.3%, +4.8%]; d -0.028 [-0.104, +0.033]; **undecided** | -16.9% [-28.0%, -7.7%]; d -0.120 [-0.206, -0.056]; **loss** |
| 2021-23 | B2 | 220 | +58.7% [+48.3%, +68.7%]; d +1.042 [+0.715, +1.451]; **gain** | +58.3% [+48.2%, +68.0%]; d +1.035 [+0.712, +1.439]; **gain** | +53.1% [+44.6%, +60.6%]; d +0.943 [+0.661, +1.292]; **gain** |
| 2021-23 | B2*-cap | 220 | +72.4% [+64.0%, +79.9%]; d +1.921 [+1.399, +2.554]; **gain** | +72.1% [+64.1%, +79.5%]; d +1.914 [+1.395, +2.540]; **gain** | +68.6% [+61.8%, +74.6%]; d +1.822 [+1.349, +2.388]; **gain** |
| 2024 | B1 | 69 | +35.9% [+28.0%, +44.5%]; d +0.804 [+0.399, +1.536]; **gain** | +37.8% [+30.8%, +45.1%]; d +0.846 [+0.404, +1.650]; **gain** | +18.9% [+12.8%, +24.7%]; d +0.424 [+0.261, +0.642]; **gain** |
| 2024 | B1' | 69 | +26.7% [+17.8%, +38.5%]; d +0.523 [+0.197, +1.232]; **gain** | +28.8% [+19.3%, +39.4%]; d +0.565 [+0.205, +1.351]; **gain** | +7.3% [+0.1%, +12.7%]; d +0.142 [-0.001, +0.302]; **undecided** |
| 2024 | B2 | 69 | +27.0% [+16.6%, +35.3%]; d +0.533 [+0.217, +0.934]; **gain** | +29.2% [+17.7%, +37.1%]; d +0.575 [+0.225, +1.049]; **gain** | +7.7% [-11.6%, +21.7%]; d +0.152 [-0.199, +0.468]; **undecided** |
| 2024 | B2*-cap | 69 | +42.8% [+32.1%, +50.4%]; d +1.076 [+0.704, +1.561]; **gain** | +44.5% [+35.1%, +50.9%]; d +1.119 [+0.713, +1.666]; **gain** | +27.7% [+5.9%, +40.4%]; d +0.696 [+0.301, +1.032]; **gain** |
| 2025-26 | B1 | 69 | +41.1% [+30.0%, +52.5%]; d +1.562 [+0.953, +2.428]; **gain** | +41.4% [+31.5%, +52.0%]; d +1.575 [+0.973, +2.417]; **gain** | +16.1% [+1.0%, +28.0%]; d +0.610 [+0.019, +1.166]; **gain** |
| 2025-26 | B1' | 69 | +34.2% [+24.8%, +43.6%]; d +1.165 [+0.698, +1.763]; **gain** | +34.6% [+25.9%, +43.2%]; d +1.178 [+0.714, +1.764]; **gain** | +6.3% [-7.5%, +16.4%]; d +0.213 [-0.252, +0.584]; **undecided** |
| 2025-26 | B2 | 69 | +52.1% [+26.5%, +72.5%]; d +2.438 [+0.577, +6.639]; **gain** | +52.4% [+28.4%, +73.0%]; d +2.452 [+0.599, +6.760]; **gain** | +31.8% [-0.5%, +56.5%]; d +1.487 [-0.178, +4.659]; **undecided** |
| 2025-26 | B2*-cap | 69 | +58.8% [+38.1%, +75.3%]; d +3.197 [+1.023, +7.863]; **gain** | +59.1% [+39.8%, +75.5%]; d +3.210 [+1.052, +7.913]; **gain** | +41.3% [+15.7%, +61.2%]; d +2.246 [+0.308, +6.033]; **gain** |

### Regime: the variant against (s3c-ann-net)

| cut | events | grid CRPS: variant over (s3c-ann-net) | upper-tail twCRPS: variant over (s3c-ann-net) |
|---|---|---|---|
| 2020 | 55 | -8.4% [-14.9%, -3.6%]; d -0.079 [-0.138, -0.034]; **loss** | -18.1% [-31.8%, -8.0%]; d -0.066 [-0.107, -0.039]; **loss** |
| 2021-23 | 220 | -1.0% [-2.8%, +0.7%]; d -0.007 [-0.018, +0.005]; **undecided** | -46.1% [-71.1%, -22.0%]; d -0.004 [-0.016, -0.001]; **loss** |
| 2024 | 69 | +2.9% [-1.0%, +12.5%]; d +0.042 [-0.010, +0.264]; **undecided** | +7.1% [-16.3%, +35.2%]; d +0.026 [-0.016, +0.500]; **undecided** |
| 2025-26 | 69 | +0.6% [-1.9%, +5.0%]; d +0.014 [-0.038, +0.128]; **undecided** | +0.2% [-2.9%, +5.0%]; d +0.002 [-0.031, +0.086]; **undecided** |

### Pressure-day type: grid CRPS

| stratum | benchmark | events | (s3c-ann-net) | risk-date variant | spread_mr_ctx |
|---|---|---|---|---|---|
| ordinary | B1 | 206 | +16.7% [+6.1%, +26.7%]; d +0.194 [+0.058, +0.381]; **gain** | +15.1% [+4.7%, +25.0%]; d +0.175 [+0.043, +0.360]; **gain** | +1.5% [-9.9%, +12.2%]; d +0.017 [-0.104, +0.148]; **undecided** |
| ordinary | B1' | 206 | +8.9% [-2.5%, +19.5%]; d +0.094 [-0.021, +0.255]; **undecided** | +7.1% [-4.2%, +18.1%]; d +0.075 [-0.038, +0.235]; **undecided** | -7.8% [-19.1%, +2.3%]; d -0.082 [-0.188, +0.017]; **undecided** |
| ordinary | B2 | 206 | +48.0% [+34.4%, +61.7%]; d +0.892 [+0.491, +1.661]; **gain** | +47.0% [+33.3%, +61.1%]; d +0.873 [+0.473, +1.645]; **gain** | +38.5% [+21.9%, +52.9%]; d +0.715 [+0.334, +1.360]; **gain** |
| ordinary | B2*-cap | 206 | +60.7% [+49.6%, +70.4%]; d +1.488 [+0.961, +2.369]; **gain** | +59.9% [+48.7%, +69.8%]; d +1.469 [+0.942, +2.351]; **gain** | +53.5% [+39.2%, +64.5%]; d +1.312 [+0.794, +2.087]; **gain** |
| quarter_end_turn | B1 | 34 | +26.6% [+18.1%, +34.7%]; d +0.851 [+0.153, +2.394]; **gain** | +33.5% [+23.7%, +43.0%]; d +1.073 [+0.193, +3.278]; **gain** | +6.4% [-8.3%, +15.0%]; d +0.206 [-0.382, +0.668]; **undecided** |
| quarter_end_turn | B1' | 34 | +24.6% [+15.0%, +33.5%]; d +0.766 [+0.090, +2.221]; **gain** | +31.7% [+20.5%, +42.0%]; d +0.988 [+0.138, +3.093]; **gain** | +3.9% [-14.0%, +13.0%]; d +0.121 [-0.493, +0.558]; **undecided** |
| quarter_end_turn | B2 | 34 | +32.6% [-33.1%, +57.3%]; d +1.135 [-0.444, +2.069]; **undecided** | +39.0% [-12.4%, +59.6%]; d +1.357 [+0.102, +2.239]; **gain** | +14.1% [-79.1%, +47.7%]; d +0.490 [-1.660, +1.711]; **undecided** |
| quarter_end_turn | B2*-cap | 34 | +48.6% [+11.1%, +74.6%]; d +2.216 [+1.111, +3.349]; **gain** | +53.4% [+23.6%, +75.6%]; d +2.438 [+1.490, +3.482]; **gain** | +34.4% [-34.3%, +65.2%]; d +1.571 [+0.047, +2.776]; **gain** |
| tax_date | B1 | 71 | +19.6% [-3.2%, +37.7%]; d +0.243 [-0.008, +0.609]; **undecided** | +14.9% [-7.9%, +35.6%]; d +0.185 [-0.072, +0.579]; **undecided** | -15.7% [-44.7%, +10.9%]; d -0.194 [-0.459, +0.092]; **undecided** |
| tax_date | B1' | 71 | +12.5% [-7.1%, +30.1%]; d +0.143 [-0.053, +0.415]; **undecided** | +7.3% [-13.0%, +27.1%]; d +0.084 [-0.117, +0.374]; **undecided** | -25.9% [-53.3%, -0.4%]; d -0.295 [-0.521, -0.058]; **loss** |
| tax_date | B2 | 71 | +70.2% [+58.1%, +82.3%]; d +2.355 [+1.446, +3.807]; **gain** | +68.5% [+57.2%, +80.1%]; d +2.296 [+1.398, +3.728]; **gain** | +57.2% [+44.9%, +67.4%]; d +1.917 [+1.134, +3.093]; **gain** |
| tax_date | B2*-cap | 71 | +73.6% [+63.8%, +82.2%]; d +2.788 [+1.733, +3.946]; **gain** | +72.1% [+63.0%, +80.2%]; d +2.730 [+1.692, +3.875]; **gain** | +62.1% [+51.9%, +69.9%]; d +2.351 [+1.431, +3.350]; **gain** |
| turn | B1 | 92 | +40.9% [+25.1%, +57.5%]; d +0.778 [+0.287, +1.812]; **gain** | +40.4% [+24.8%, +57.2%]; d +0.769 [+0.281, +1.807]; **gain** | +9.8% [-13.1%, +25.0%]; d +0.187 [-0.199, +0.619]; **undecided** |
| turn | B1' | 92 | +33.4% [+19.5%, +48.8%]; d +0.564 [+0.224, +1.280]; **gain** | +32.9% [+19.2%, +48.4%]; d +0.555 [+0.217, +1.279]; **gain** | -1.6% [-13.2%, +8.7%]; d -0.028 [-0.204, +0.148]; **undecided** |
| turn | B2 | 92 | +58.5% [+40.3%, +78.0%]; d +1.586 [+0.598, +4.972]; **gain** | +58.2% [+39.8%, +78.0%]; d +1.577 [+0.588, +4.991]; **gain** | +36.7% [+15.4%, +57.6%]; d +0.995 [+0.222, +3.237]; **gain** |
| turn | B2*-cap | 92 | +68.8% [+58.3%, +78.5%]; d +2.475 [+1.390, +5.287]; **gain** | +68.5% [+57.9%, +78.5%]; d +2.466 [+1.379, +5.295]; **gain** | +52.4% [+40.9%, +62.3%]; d +1.884 [+1.019, +3.907]; **gain** |
| year_end | B1 | 10 | thin (10) | thin (10) | thin (10) |
| year_end | B1' | 10 | thin (10) | thin (10) | thin (10) |
| year_end | B2 | 10 | thin (10) | thin (10) | thin (10) |
| year_end | B2*-cap | 10 | thin (10) | thin (10) | thin (10) |

### Pressure-day type: the variant against (s3c-ann-net)

| cut | events | grid CRPS: variant over (s3c-ann-net) | upper-tail twCRPS: variant over (s3c-ann-net) |
|---|---|---|---|
| ordinary | 206 | -2.0% [-3.4%, -0.5%]; d -0.019 [-0.031, -0.007]; **loss** | -4.1% [-9.3%, +1.2%]; d -0.009 [-0.015, -0.003]; **loss** |
| quarter_end_turn | 34 | +9.5% [+5.1%, +14.2%]; d +0.222 [+0.037, +0.753]; **gain** | skill undefined; d +0.120 [+0.002, +0.977]; **gain** |
| tax_date | 71 | -5.9% [-15.3%, -1.0%]; d -0.059 [-0.132, -0.018]; **loss** | -18.3% [-57.0%, +8.7%]; d -0.035 [-0.102, -0.010]; **loss** |
| turn | 92 | -0.8% [-2.3%, +0.4%]; d -0.009 [-0.024, +0.004]; **undecided** | -4.5% [-15.6%, +4.1%]; d -0.014 [-0.034, -0.005]; **loss** |
| year_end | 10 | thin (10) | thin (10) |

## 9. What the variant did

| label | cells | cells with k not 1 | geometric mean k | cells by k |
|---|---|---|---|---|
| bill_settlement_large | 1225 | 903 | 0.983 | 0.67: 204, 0.8: 226, 1.0: 322, 1.25: 444, 1.5: 29 |
| coupon_settlement | 96 | 0 | 1.000 | 1.0: 96 |
| fomc_meeting | 336 | 196 | 1.229 | 0.8: 10, 1.0: 140, 1.25: 37, 1.5: 139, 2.0: 10 |
| month_end_turn | 600 | 330 | 1.142 | 0.8: 30, 1.0: 270, 1.25: 210, 1.5: 80, 2.0: 10 |
| none | 5928 | 0 | 1.000 | 1.0: 5928 |
| post_fomc_window | 354 | 145 | 1.024 | 0.67: 30, 0.8: 20, 1.0: 209, 1.25: 75, 1.5: 20 |
| quarter_and_year_end | 291 | 231 | 1.717 | 1.0: 60, 1.5: 10, 2.0: 221 |
| tax_date | 445 | 297 | 1.455 | 1.0: 148, 1.25: 27, 1.5: 91, 2.0: 179 |

A label is the cell's first stratum in the declared order; `none` is a cell in no stratum, which keeps k = 1. Unchanged from #724.

## What this shows, and does not

- It shows how the frozen candidate and the declared variant read on #1131's event-day strata on 2020-2025 development days when every row, including the rows #724 could not bound, is read on the mean-d bound. Nothing about the scores moved: the rows #724 defined are the same rows.
- It does not show skill on any confirmation day, does not change the candidate and sets no rule. The bound carries the caveat above (the HAC standard error that studentizes the bound is understated about 2x after 2020 (measured for the daily lag-10 series, not for this page's event series at lag 3), so an interval that excludes zero is narrower than it should be. A reading here is evidence for a question).
- The strata overlap and the days within a stratum are dependent; the intervals use #1131's block of 3 events. The reported cuts carry no multiplicity correction (default 7). One variant was declared and scored.
- Not changed: the pressure-day-type rows still bootstrap their own days (above); the calendar-benchmark cover; the 2026 days (#1394's confirmation, not this step).

**Does the specialised variant add skill over (s3c-ann-net) on the union (without the bill stratum), read on the mean-d bound? It adds no skill that this data can show on grid CRPS: -0.4% [-2.1%, +1.7%]; d -0.005 [-0.021, +0.021]; **undecided** over 413 events (twCRPS -2.0% [-7.1%, +4.5%]; d -0.006 [-0.017, +0.016]; **undecided**). Development data, not a verdict.**
