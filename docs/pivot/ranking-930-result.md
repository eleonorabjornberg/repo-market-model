# H8 step 2's blend re-scored with the default weight when the windows hold no pressure day (#930)

**Hypothesis and step.** H8 (ranking beats calibrating for desk use), step 2 re-scored a second time (#930, finding #925, Eleonora's ruling on #925). The page of #924 (`docs/pivot/ranking-924-result.md`) stands as published and is not edited. Development data, exploration: not a verdict (scoring protocol v1, #640).

**What changed, and only this.** When none of the trailing windows the blend (c) chooses its weight on holds a pressure day, every grid weight ties at zero precision, and the declared tie-break ("a tie goes to the smaller w") sent the weight to 0.0, the pure tail ranker with no calendar in it. The weight is now the declared default 0.5 in that case (`choose_weight`, `src/repo_model/ranking_daytype.py`; the rule text in `metadata/ranking_765.json` carries the exception). Every other declared value is unchanged: the grid, the 252 trailing windows, the 60 minimum, top 5, the tie-break when the windows do hold a pressure day, the rankers (a) and (b), the days, the seed (765), the 10,000 draws and the panel (`4ddc3882…`). (a), (b) and every benchmark are therefore the figures of #924 to the last digit; only (c) moves.

**Refits on the default weight.** 46 of the 87 refits use 0.5: 4 for want of 60 trailing windows (as before) and 42 because no trailing window held a pressure day (the finding counted 42 of 87 refits at w = 0.0 from 2021-04-21 to 2024-09-30). The mean weight in force moves from 0.36 to 0.60.

**How (c) moves against the calendar** (precision@5, gain with its 95% interval): pooled -0.1 pp [-1.2 pp, +1.0 pp] on #924's page, +0.0 pp [-1.1 pp, +1.1 pp] here; 2024 -1.8 pp [-3.6 pp, -0.3 pp] before, -0.8 pp [-1.9 pp, +0.0 pp] now, so the interval no longer lies wholly below zero; 2018-19 and 2025-26 are unchanged to the digit (their refits were not in the no-pressure stretch); 2021-23 has no pressure day. The finding's -1.44 pp to -0.22 pp was computed on 208 days of 2024 from a refit log; the page scores all 250.

**Hypothesis and step.** H8 (ranking beats calibrating for desk use), step 2: rank by tail probability combined with the day type. Development data, exploration: not a verdict (scoring protocol v1, #640). Declaration: `metadata/ranking_765.json`, committed before any score. The +5 bp level is only the ranking quantity carried over from step 1; nothing is fitted to the +5 bp event.

**Days.** 1825 decision days, 2018-08-09 to 2025-12-02 (targets to 2025-12-31); 90 offered days skipped for want of history. Panel `4ddc3882…`. Bootstrap: stationary, mean block 20 days, 10,000 draws, seed 765; intervals are the 5th and 95th percentile. A positive gain favours the ranker. Same windows and days as step 1 (#722).

## What a window holds

- Windows with at least one pressure day (> +5 bp): 23.9%; mean 1.47 pressure days per window.
- Scheduled risk dates are 6.9% of window days and 15.7% of the pressure days.
- (b) took the all-type fallback on 0.7% of target leads (pool under 30).
- (c) weights chosen at 87 refits (46 on the default 0.5: 4 for want of 60 trailing windows, the rest with no pressure day among them): w = 0.0: 1, w = 0.25: 3, w = 0.5: 46, w = 0.75: 35, w = 1.0: 2; mean weight in force 0.60.

## Top-k precision and recall (all decision days; recall on windows with a pressure day)

| Ranker | P@3 | P@5 | R@3 | R@5 | share of top 5 on a risk date |
|---|---|---|---|---|---|
| (a) calendar first, tail within | 10.9% | 9.9% | 26.8% | 41.0% | 27.6% |
| (b) tail probability by day type | 10.9% | 9.7% | 27.7% | 39.5% | 14.5% |
| (c) blend of calendar and tail ranks | 10.3% | 9.5% | 25.5% | 39.3% | 26.0% |
| persistence | 8.0% | 7.7% | 16.1% | 26.3% | 6.6% |
| climatology by day type | 11.0% | 9.5% | 28.4% | 38.3% | 12.4% |
| calendar of risk dates | 10.5% | 9.4% | 26.3% | 37.7% | 27.6% |
| step 1: model, P(> +5 bp) (reference) | 8.0% | 7.9% | 17.0% | 28.2% | 6.8% |

## Paired gains over each benchmark (all decision days)

| Ranker | Metric | vs persistence | vs climatology | vs calendar | vs step 1 |
|---|---|---|---|---|---|
| (a) calendar first, tail within | precision@3 | +2.9 pp [+1.2 pp, +4.8 pp] | -0.1 pp [-1.3 pp, +1.1 pp] | +0.3 pp [-0.6 pp, +1.3 pp] | +2.8 pp [+1.3 pp, +4.7 pp] |
| (a) calendar first, tail within | precision@5 | +2.2 pp [+1.1 pp, +3.5 pp] | +0.4 pp [-0.4 pp, +1.3 pp] | +0.5 pp [-0.4 pp, +1.5 pp] | +2.1 pp [+1.1 pp, +3.2 pp] |
| (a) calendar first, tail within | recall@3 | +10.7 pp [+5.2 pp, +17.5 pp] | -1.6 pp [-9.4 pp, +6.3 pp] | +0.6 pp [-2.8 pp, +3.7 pp] | +9.8 pp [+5.2 pp, +15.4 pp] |
| (a) calendar first, tail within | recall@5 | +14.8 pp [+8.2 pp, +22.3 pp] | +2.7 pp [-4.7 pp, +10.7 pp] | +3.3 pp [-1.0 pp, +7.8 pp] | +12.9 pp [+7.3 pp, +19.3 pp] |
| (b) tail probability by day type | precision@3 | +2.9 pp [+1.2 pp, +4.7 pp] | -0.1 pp [-0.9 pp, +0.7 pp] | +0.4 pp [-0.9 pp, +1.8 pp] | +2.8 pp [+1.2 pp, +4.6 pp] |
| (b) tail probability by day type | precision@5 | +2.0 pp [+0.9 pp, +3.1 pp] | +0.2 pp [-0.4 pp, +0.8 pp] | +0.2 pp [-0.8 pp, +1.4 pp] | +1.8 pp [+0.8 pp, +2.9 pp] |
| (b) tail probability by day type | recall@3 | +11.6 pp [+6.4 pp, +17.1 pp] | -0.8 pp [-2.6 pp, +0.9 pp] | +1.4 pp [-5.5 pp, +8.2 pp] | +10.7 pp [+5.3 pp, +16.4 pp] |
| (b) tail probability by day type | recall@5 | +13.2 pp [+7.5 pp, +19.5 pp] | +1.2 pp [-1.2 pp, +3.7 pp] | +1.8 pp [-7.3 pp, +10.3 pp] | +11.4 pp [+5.7 pp, +17.6 pp] |
| (c) blend of calendar and tail ranks | precision@3 | +2.3 pp [+1.0 pp, +3.7 pp] | -0.7 pp [-2.2 pp, +0.7 pp] | -0.2 pp [-1.5 pp, +0.9 pp] | +2.2 pp [+1.0 pp, +3.6 pp] |
| (c) blend of calendar and tail ranks | precision@5 | +1.7 pp [+0.8 pp, +2.8 pp] | -0.1 pp [-1.0 pp, +0.9 pp] | +0.0 pp [-1.1 pp, +1.1 pp] | +1.6 pp [+0.8 pp, +2.5 pp] |
| (c) blend of calendar and tail ranks | recall@3 | +9.4 pp [+4.2 pp, +15.8 pp] | -3.0 pp [-11.1 pp, +4.9 pp] | -0.8 pp [-4.6 pp, +2.7 pp] | +8.5 pp [+4.2 pp, +13.7 pp] |
| (c) blend of calendar and tail ranks | recall@5 | +13.1 pp [+6.7 pp, +20.4 pp] | +1.1 pp [-6.6 pp, +9.0 pp] | +1.7 pp [-3.5 pp, +6.7 pp] | +11.2 pp [+5.7 pp, +17.5 pp] |

## Sensitivity: the protocol's block of 10 days instead of the declared 20

Same draws and seed, only the mean block changes (ruling on #722, item 2). Labelled a sensitivity.

| Ranker | Metric | vs persistence | vs climatology | vs calendar | vs step 1 |
|---|---|---|---|---|---|
| (a) calendar first, tail within | precision@3 | +2.9 pp [+1.4 pp, +4.6 pp] | -0.1 pp [-1.3 pp, +1.1 pp] | +0.3 pp [-0.6 pp, +1.3 pp] | +2.8 pp [+1.4 pp, +4.5 pp] |
| (a) calendar first, tail within | precision@5 | +2.2 pp [+1.2 pp, +3.4 pp] | +0.4 pp [-0.4 pp, +1.3 pp] | +0.5 pp [-0.5 pp, +1.5 pp] | +2.1 pp [+1.2 pp, +3.1 pp] |
| (a) calendar first, tail within | recall@3 | +10.7 pp [+5.7 pp, +16.6 pp] | -1.6 pp [-8.7 pp, +5.2 pp] | +0.6 pp [-3.0 pp, +3.9 pp] | +9.8 pp [+5.6 pp, +14.6 pp] |
| (a) calendar first, tail within | recall@5 | +14.8 pp [+8.8 pp, +21.3 pp] | +2.7 pp [-4.0 pp, +9.6 pp] | +3.3 pp [-1.3 pp, +8.1 pp] | +12.9 pp [+7.7 pp, +18.6 pp] |
| (b) tail probability by day type | precision@3 | +2.9 pp [+1.5 pp, +4.4 pp] | -0.1 pp [-0.9 pp, +0.7 pp] | +0.4 pp [-0.9 pp, +1.7 pp] | +2.8 pp [+1.4 pp, +4.3 pp] |
| (b) tail probability by day type | precision@5 | +2.0 pp [+1.0 pp, +3.0 pp] | +0.2 pp [-0.4 pp, +0.7 pp] | +0.2 pp [-0.9 pp, +1.4 pp] | +1.8 pp [+0.9 pp, +2.8 pp] |
| (b) tail probability by day type | recall@3 | +11.6 pp [+6.8 pp, +16.7 pp] | -0.8 pp [-2.6 pp, +0.9 pp] | +1.4 pp [-5.0 pp, +7.9 pp] | +10.7 pp [+5.7 pp, +16.1 pp] |
| (b) tail probability by day type | recall@5 | +13.2 pp [+7.8 pp, +19.1 pp] | +1.2 pp [-1.2 pp, +3.7 pp] | +1.8 pp [-6.2 pp, +9.8 pp] | +11.4 pp [+6.1 pp, +17.1 pp] |
| (c) blend of calendar and tail ranks | precision@3 | +2.3 pp [+1.0 pp, +3.7 pp] | -0.7 pp [-2.1 pp, +0.6 pp] | -0.2 pp [-1.5 pp, +0.9 pp] | +2.2 pp [+1.1 pp, +3.5 pp] |
| (c) blend of calendar and tail ranks | precision@5 | +1.7 pp [+0.9 pp, +2.7 pp] | -0.1 pp [-1.0 pp, +0.8 pp] | +0.0 pp [-1.1 pp, +1.2 pp] | +1.6 pp [+0.9 pp, +2.4 pp] |
| (c) blend of calendar and tail ranks | recall@3 | +9.4 pp [+4.6 pp, +15.0 pp] | -3.0 pp [-10.2 pp, +4.0 pp] | -0.8 pp [-4.7 pp, +2.9 pp] | +8.5 pp [+4.5 pp, +13.1 pp] |
| (c) blend of calendar and tail ranks | recall@5 | +13.1 pp [+7.2 pp, +19.6 pp] | +1.1 pp [-5.9 pp, +8.1 pp] | +1.7 pp [-3.6 pp, +7.0 pp] | +11.2 pp [+6.2 pp, +16.9 pp] |

Primary under block 10: (a) calendar first, tail within [-0.5 pp, +1.5 pp]; (b) tail probability by day type [-0.9 pp, +1.4 pp]; (c) blend of calendar and tail ranks [-1.1 pp, +1.2 pp].

## Precision on the windows that held a pressure day

| Ranker | Metric | vs persistence | vs climatology | vs calendar | vs step 1 |
|---|---|---|---|---|---|
| (a) calendar first, tail within | precision@3 | +12.1 pp [+6.3 pp, +18.4 pp] | -0.4 pp [-5.2 pp, +4.3 pp] | +1.5 pp [-2.3 pp, +5.2 pp] | +11.8 pp [+6.5 pp, +17.9 pp] |
| (a) calendar first, tail within | precision@5 | +9.3 pp [+5.5 pp, +13.2 pp] | +1.8 pp [-1.7 pp, +5.2 pp] | +2.1 pp [-1.6 pp, +5.9 pp] | +8.7 pp [+5.6 pp, +12.2 pp] |
| (b) tail probability by day type | precision@3 | +12.1 pp [+6.4 pp, +17.3 pp] | -0.4 pp [-3.7 pp, +2.9 pp] | +1.5 pp [-4.1 pp, +7.2 pp] | +11.9 pp [+6.3 pp, +17.1 pp] |
| (b) tail probability by day type | precision@5 | +8.2 pp [+4.6 pp, +11.6 pp] | +0.6 pp [-1.7 pp, +3.1 pp] | +1.0 pp [-3.9 pp, +5.9 pp] | +7.6 pp [+4.5 pp, +10.8 pp] |
| (c) blend of calendar and tail ranks | precision@3 | +9.6 pp [+4.9 pp, +14.3 pp] | -2.9 pp [-8.7 pp, +2.3 pp] | -1.0 pp [-6.2 pp, +3.6 pp] | +9.4 pp [+5.3 pp, +13.5 pp] |
| (c) blend of calendar and tail ranks | precision@5 | +7.3 pp [+4.2 pp, +10.3 pp] | -0.2 pp [-4.1 pp, +3.3 pp] | +0.2 pp [-4.6 pp, +4.6 pp] | +6.8 pp [+4.4 pp, +9.1 pp] |

## Precision@5 of (a) calendar first, tail within, by calendar year of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018 | 97 | 50 | 23.7% | 22.3% | +1.4 pp [-4.5 pp, +7.6 pp] | +5.6 pp [-0.2 pp, +12.0 pp] | +12.5 pp [+2.0 pp, +23.9 pp] |
| 2019 | 250 | 239 | 44.5% | 43.0% | +1.5 pp [-3.6 pp, +6.6 pp] | -1.4 pp [-5.4 pp, +2.7 pp] | +6.7 pp [+2.3 pp, +11.1 pp] |
| 2020 | 251 | 29 | 1.8% | 1.4% | +0.4 pp [-1.4 pp, +2.4 pp] | +0.6 pp [-0.3 pp, +1.9 pp] | +0.0 pp [-0.2 pp, +0.3 pp] |
| 2021 | 250 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2022 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2023 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 3.9% | 4.2% | -0.3 pp [-0.8 pp, +0.1 pp] | +0.7 pp [-0.6 pp, +2.2 pp] | +2.0 pp [+0.5 pp, +3.7 pp] |
| 2025 | 229 | 74 | 14.4% | 12.7% | +1.7 pp [-1.3 pp, +5.6 pp] | +1.1 pp [-2.6 pp, +4.9 pp] | +2.8 pp [-0.2 pp, +6.5 pp] |

## Precision@5 of (b) tail probability by day type, by calendar year of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018 | 97 | 50 | 16.5% | 22.3% | -5.8 pp [-15.3 pp, +3.1 pp] | -1.6 pp [-6.0 pp, +2.4 pp] | +5.3 pp [+0.1 pp, +10.9 pp] |
| 2019 | 250 | 239 | 45.2% | 43.0% | +2.2 pp [-3.0 pp, +7.2 pp] | -0.7 pp [-2.4 pp, +0.9 pp] | +7.4 pp [+2.6 pp, +11.7 pp] |
| 2020 | 251 | 29 | 1.4% | 1.4% | +0.1 pp [-1.4 pp, +1.6 pp] | +0.3 pp [-0.3 pp, +1.1 pp] | -0.3 pp [-1.1 pp, +0.4 pp] |
| 2021 | 250 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2022 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2023 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 2.8% | 4.2% | -1.4 pp [-3.1 pp, -0.0 pp] | -0.4 pp [-1.0 pp, +0.0 pp] | +0.9 pp [+0.0 pp, +2.1 pp] |
| 2025 | 229 | 74 | 16.2% | 12.7% | +3.5 pp [-1.3 pp, +9.2 pp] | +2.8 pp [+0.1 pp, +6.1 pp] | +4.6 pp [+0.3 pp, +9.6 pp] |

## Precision@5 of (c) blend of calendar and tail ranks, by calendar year of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018 | 97 | 50 | 16.8% | 22.3% | -5.5 pp [-18.0 pp, +6.0 pp] | -1.3 pp [-9.6 pp, +6.5 pp] | +5.6 pp [+0.0 pp, +11.7 pp] |
| 2019 | 250 | 239 | 44.2% | 43.0% | +1.2 pp [-3.8 pp, +6.3 pp] | -1.7 pp [-5.7 pp, +2.4 pp] | +6.5 pp [+2.1 pp, +10.7 pp] |
| 2020 | 251 | 29 | 1.8% | 1.4% | +0.4 pp [-1.4 pp, +2.4 pp] | +0.6 pp [-0.3 pp, +1.9 pp] | +0.0 pp [-0.2 pp, +0.3 pp] |
| 2021 | 250 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2022 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2023 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 3.4% | 4.2% | -0.8 pp [-1.9 pp, +0.0 pp] | +0.2 pp [-1.6 pp, +2.0 pp] | +1.5 pp [+0.3 pp, +3.0 pp] |
| 2025 | 229 | 74 | 14.4% | 12.7% | +1.7 pp [-1.3 pp, +5.6 pp] | +1.1 pp [-2.6 pp, +4.9 pp] | +2.8 pp [-0.2 pp, +6.5 pp] |

## Precision@5 of (a) calendar first, tail within, by regime of the decision day (2021-23 is the one called out)

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018-19 | 347 | 289 | 38.7% | 37.2% | +1.5 pp [-2.4 pp, +5.5 pp] | +0.6 pp [-3.0 pp, +4.3 pp] | +8.3 pp [+3.8 pp, +13.1 pp] |
| 2020 | 251 | 29 | 1.8% | 1.4% | +0.4 pp [-1.4 pp, +2.4 pp] | +0.6 pp [-0.3 pp, +1.9 pp] | +0.0 pp [-0.2 pp, +0.3 pp] |
| 2021-23 | 748 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 3.9% | 4.2% | -0.3 pp [-0.8 pp, +0.1 pp] | +0.7 pp [-0.6 pp, +2.2 pp] | +2.0 pp [+0.5 pp, +3.7 pp] |
| 2025-26 | 229 | 74 | 14.4% | 12.7% | +1.7 pp [-1.3 pp, +5.6 pp] | +1.1 pp [-2.6 pp, +4.9 pp] | +2.8 pp [-0.2 pp, +6.5 pp] |

## Precision@5 of (b) tail probability by day type, by regime of the decision day (2021-23 is the one called out)

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018-19 | 347 | 289 | 37.2% | 37.2% | -0.1 pp [-4.4 pp, +4.1 pp] | -1.0 pp [-2.8 pp, +0.7 pp] | +6.8 pp [+2.9 pp, +10.4 pp] |
| 2020 | 251 | 29 | 1.4% | 1.4% | +0.1 pp [-1.4 pp, +1.6 pp] | +0.3 pp [-0.3 pp, +1.1 pp] | -0.3 pp [-1.1 pp, +0.4 pp] |
| 2021-23 | 748 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 2.8% | 4.2% | -1.4 pp [-3.1 pp, -0.0 pp] | -0.4 pp [-1.0 pp, +0.0 pp] | +0.9 pp [+0.0 pp, +2.1 pp] |
| 2025-26 | 229 | 74 | 16.2% | 12.7% | +3.5 pp [-1.3 pp, +9.2 pp] | +2.8 pp [+0.1 pp, +6.1 pp] | +4.6 pp [+0.3 pp, +9.6 pp] |

## Precision@5 of (c) blend of calendar and tail ranks, by regime of the decision day (2021-23 is the one called out)

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018-19 | 347 | 289 | 36.6% | 37.2% | -0.7 pp [-5.7 pp, +4.2 pp] | -1.6 pp [-5.5 pp, +2.2 pp] | +6.2 pp [+2.7 pp, +9.7 pp] |
| 2020 | 251 | 29 | 1.8% | 1.4% | +0.4 pp [-1.4 pp, +2.4 pp] | +0.6 pp [-0.3 pp, +1.9 pp] | +0.0 pp [-0.2 pp, +0.3 pp] |
| 2021-23 | 748 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 3.4% | 4.2% | -0.8 pp [-1.9 pp, +0.0 pp] | +0.2 pp [-1.6 pp, +2.0 pp] | +1.5 pp [+0.3 pp, +3.0 pp] |
| 2025-26 | 229 | 74 | 14.4% | 12.7% | +1.7 pp [-1.3 pp, +5.6 pp] | +1.1 pp [-2.6 pp, +4.9 pp] | +2.8 pp [-0.2 pp, +6.5 pp] |

## Precision@5 of (a) calendar first, tail within, by as-of reserve scarcity state of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| abundant | 1041 | 43 | 0.9% | 1.0% | -0.0 pp [-0.2 pp, +0.0 pp] | +0.2 pp [-0.1 pp, +0.6 pp] | +0.5 pp [+0.1 pp, +1.0 pp] |
| ample | 313 | 17 | 1.4% | 1.5% | -0.1 pp [-0.3 pp, +0.0 pp] | +1.0 pp [-0.0 pp, +2.6 pp] | +1.1 pp [+0.0 pp, +2.6 pp] |
| scarce | 430 | 342 | 34.7% | 33.4% | +1.3 pp [-2.1 pp, +4.7 pp] | +0.0 pp [-3.2 pp, +3.2 pp] | +7.0 pp [+3.2 pp, +11.1 pp] |
| tight | 41 | 34 | 44.9% | 33.7% | +11.2 pp [-4.4 pp, +27.3 pp] | +6.5 pp [+0.1 pp, +13.0 pp] | +5.3 pp [-6.9 pp, +17.3 pp] |

## Precision@5 of (b) tail probability by day type, by as-of reserve scarcity state of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| abundant | 1041 | 43 | 0.7% | 1.0% | -0.3 pp [-0.8 pp, +0.0 pp] | -0.1 pp [-0.2 pp, +0.0 pp] | +0.2 pp [+0.0 pp, +0.5 pp] |
| ample | 313 | 17 | 0.4% | 1.5% | -1.1 pp [-2.7 pp, +0.0 pp] | -0.0 pp [-0.1 pp, +0.0 pp] | +0.0 pp [-0.0 pp, +0.1 pp] |
| scarce | 430 | 342 | 34.5% | 33.4% | +1.1 pp [-2.8 pp, +4.9 pp] | -0.1 pp [-1.8 pp, +1.5 pp] | +6.8 pp [+3.4 pp, +10.2 pp] |
| tight | 41 | 34 | 49.3% | 33.7% | +15.6 pp [-1.0 pp, +32.2 pp] | +10.9 pp [+6.5 pp, +15.7 pp] | +9.7 pp [+1.3 pp, +18.0 pp] |

## Precision@5 of (c) blend of calendar and tail ranks, by as-of reserve scarcity state of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| abundant | 1041 | 43 | 0.8% | 1.0% | -0.2 pp [-0.4 pp, +0.0 pp] | +0.0 pp [-0.4 pp, +0.5 pp] | +0.4 pp [+0.0 pp, +0.8 pp] |
| ample | 313 | 17 | 1.4% | 1.5% | -0.1 pp [-0.3 pp, +0.0 pp] | +1.0 pp [-0.0 pp, +2.6 pp] | +1.1 pp [+0.0 pp, +2.6 pp] |
| scarce | 430 | 342 | 33.0% | 33.4% | -0.4 pp [-4.8 pp, +3.7 pp] | -1.7 pp [-5.1 pp, +1.6 pp] | +5.3 pp [+2.4 pp, +8.3 pp] |
| tight | 41 | 34 | 44.9% | 33.7% | +11.2 pp [-4.4 pp, +27.3 pp] | +6.5 pp [+0.1 pp, +13.0 pp] | +5.3 pp [-6.9 pp, +17.3 pp] |

## Reading

- (a) puts every scheduled risk date above every other day, so its top 5 are the calendar's whenever the window holds five; the tail probability only chooses among them and fills the places when fewer than five are scheduled. (b) and (c) are the two ways of letting the day type move the probability or the rank.
- A window with no pressure day scores zero precision for every ranker, so years with none (2021-23) add decision days and no information; recall is taken on the windows that have one.
- The risk-date definition is `pressure_judge._scheduled_risk_date`, as in step 1. The calendar benchmark breaks its ties by date; the other rankers by their expected value.
- Development data only, nothing registered, no published figure moves. Whether any ranker goes on to registration (step 3) is Eleonora's decision.

Phi across refits: 0.25 to 0.97, median 0.57.

## Each ranker against the calendar (precision@5, development, not a verdict)

- **(a) calendar first, tail within:** 9.9% against 9.4%, gain +0.5 pp [-0.4 pp, +1.5 pp]; the interval does not lie wholly above zero (H8's kill condition is met, as exploration). Below zero in point estimate only: year 2024 -0.3 pp, regime 2024 -0.3 pp, scarcity abundant -0.0 pp, scarcity ample -0.1 pp.
- **(b) tail probability by day type:** 9.7% against 9.4%, gain +0.2 pp [-0.8 pp, +1.4 pp]; the interval does not lie wholly above zero (H8's kill condition is met, as exploration). Loses (interval wholly below zero): year 2024 -1.4 pp, regime 2024 -1.4 pp. Below zero in point estimate only: year 2018 -5.8 pp, regime 2018-19 -0.1 pp, scarcity abundant -0.3 pp, scarcity ample -1.1 pp.
- **(c) blend of calendar and tail ranks:** 9.5% against 9.4%, gain +0.0 pp [-1.1 pp, +1.1 pp]; the interval does not lie wholly above zero (H8's kill condition is met, as exploration). Below zero in point estimate only: year 2018 -5.5 pp, year 2024 -0.8 pp, regime 2018-19 -0.7 pp, regime 2024 -0.8 pp, scarcity abundant -0.2 pp, scarcity ample -0.1 pp, scarcity scarce -0.4 pp.
