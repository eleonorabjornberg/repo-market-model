> **Archived on 19 October 2026 (#924). Superseded by `docs/pivot/ranking-924-result.md`; do not cite the figures below.** This page (#765, PR #771) was scored on 14 October 2026 with the `calendar` ranker as it stood before the #770 fix (6d8b8262, 15 October), which counts a coupon settlement only where it had been announced at the decision instant. The PR merged without a re-score. The text below is as published; only this note is added. Its research-log entry (`docs/research/log/2026-10-14-model-00771-H8-step2.md`) stays, because the log is append-only; the entry for #924 corrects it. The score it was written from is `score.json` in this directory.

# Ranking the next 20 business days by tail probability and day type: development result (#765)

**Hypothesis and step.** H8 (ranking beats calibrating for desk use), step 2: rank by tail probability combined with the day type. Development data, exploration: not a verdict (scoring protocol v1, #640). Declaration: `metadata/ranking_765.json`, committed before any score. The +5 bp level is only the ranking quantity carried over from step 1; nothing is fitted to the +5 bp event.

**Days.** 1825 decision days, 2018-08-09 to 2025-12-02 (targets to 2025-12-31); 90 offered days skipped for want of history. Panel `4ddc3882…`. Bootstrap: stationary, mean block 20 days, 10,000 draws, seed 765; intervals are the 5th and 95th percentile. A positive gain favours the ranker. Same windows and days as step 1 (#722).

## What a window holds

- Windows with at least one pressure day (> +5 bp): 23.9%; mean 1.47 pressure days per window.
- Scheduled risk dates are 16.3% of window days and 36.4% of the pressure days.
- (b) took the all-type fallback on 0.7% of target leads (pool under 30).
- (c) weights chosen at 87 refits (4 on the default 0.5 for want of 60 trailing windows): w = 0.0: 42, w = 0.25: 3, w = 0.5: 4, w = 0.75: 32, w = 1.0: 6; mean weight in force 0.38.

## Top-k precision and recall (all decision days; recall on windows with a pressure day)

| Ranker | P@3 | P@5 | R@3 | R@5 | share of top 5 on a risk date |
|---|---|---|---|---|---|
| (a) calendar first, tail within | 15.0% | 12.8% | 40.1% | 55.8% | 64.4% |
| (b) tail probability by day type | 10.9% | 9.7% | 27.7% | 39.5% | 27.0% |
| (c) blend of calendar and tail ranks | 14.5% | 12.3% | 38.2% | 52.9% | 39.7% |
| persistence | 8.0% | 7.7% | 16.1% | 26.3% | 16.1% |
| climatology by day type | 11.0% | 9.5% | 28.4% | 38.3% | 24.0% |
| calendar of risk dates | 15.5% | 13.0% | 43.5% | 56.8% | 64.4% |
| step 1: model, P(> +5 bp) (reference) | 8.0% | 7.9% | 17.0% | 28.2% | 16.2% |

## Paired gains over each benchmark (all decision days)

| Ranker | Metric | vs persistence | vs climatology | vs calendar | vs step 1 |
|---|---|---|---|---|---|
| (a) calendar first, tail within | precision@3 | +7.0 pp [+4.0 pp, +10.4 pp] | +4.0 pp [+2.1 pp, +6.1 pp] | -0.5 pp [-1.5 pp, +0.3 pp] | +6.9 pp [+4.0 pp, +10.3 pp] |
| (a) calendar first, tail within | precision@5 | +5.1 pp [+2.9 pp, +7.5 pp] | +3.3 pp [+1.9 pp, +4.9 pp] | -0.2 pp [-0.8 pp, +0.4 pp] | +5.0 pp [+2.9 pp, +7.3 pp] |
| (a) calendar first, tail within | recall@3 | +24.0 pp [+17.0 pp, +31.3 pp] | +11.6 pp [+6.9 pp, +16.0 pp] | -3.4 pp [-8.7 pp, +0.5 pp] | +23.1 pp [+16.2 pp, +30.4 pp] |
| (a) calendar first, tail within | recall@5 | +29.5 pp [+22.1 pp, +37.3 pp] | +17.5 pp [+12.6 pp, +23.2 pp] | -1.0 pp [-3.7 pp, +1.6 pp] | +27.6 pp [+21.1 pp, +34.5 pp] |
| (b) tail probability by day type | precision@3 | +2.9 pp [+1.2 pp, +4.7 pp] | -0.1 pp [-0.9 pp, +0.7 pp] | -4.6 pp [-7.0 pp, -2.5 pp] | +2.8 pp [+1.2 pp, +4.6 pp] |
| (b) tail probability by day type | precision@5 | +2.0 pp [+0.9 pp, +3.1 pp] | +0.2 pp [-0.4 pp, +0.8 pp] | -3.4 pp [-5.1 pp, -1.8 pp] | +1.8 pp [+0.8 pp, +2.9 pp] |
| (b) tail probability by day type | recall@3 | +11.6 pp [+6.4 pp, +17.1 pp] | -0.8 pp [-2.6 pp, +0.9 pp] | -15.9 pp [-20.1 pp, -11.8 pp] | +10.7 pp [+5.3 pp, +16.4 pp] |
| (b) tail probability by day type | recall@5 | +13.2 pp [+7.5 pp, +19.5 pp] | +1.2 pp [-1.2 pp, +3.7 pp] | -17.3 pp [-23.5 pp, -11.4 pp] | +11.4 pp [+5.7 pp, +17.6 pp] |
| (c) blend of calendar and tail ranks | precision@3 | +6.6 pp [+3.7 pp, +9.8 pp] | +3.6 pp [+1.8 pp, +5.6 pp] | -1.0 pp [-1.9 pp, -0.1 pp] | +6.5 pp [+3.6 pp, +9.7 pp] |
| (c) blend of calendar and tail ranks | precision@5 | +4.6 pp [+2.6 pp, +6.8 pp] | +2.8 pp [+1.5 pp, +4.2 pp] | -0.7 pp [-1.5 pp, -0.0 pp] | +4.5 pp [+2.6 pp, +6.5 pp] |
| (c) blend of calendar and tail ranks | recall@3 | +22.1 pp [+15.2 pp, +29.6 pp] | +9.8 pp [+5.1 pp, +14.0 pp] | -5.3 pp [-10.3 pp, -1.5 pp] | +21.2 pp [+14.3 pp, +28.8 pp] |
| (c) blend of calendar and tail ranks | recall@5 | +26.7 pp [+19.6 pp, +34.1 pp] | +14.6 pp [+10.3 pp, +19.6 pp] | -3.9 pp [-7.9 pp, -0.2 pp] | +24.8 pp [+18.6 pp, +31.4 pp] |

## Sensitivity: the protocol's block of 10 days instead of the declared 20

Same draws and seed, only the mean block changes (ruling on #722, item 2). Labelled a sensitivity.

| Ranker | Metric | vs persistence | vs climatology | vs calendar | vs step 1 |
|---|---|---|---|---|---|
| (a) calendar first, tail within | precision@3 | +7.0 pp [+4.6 pp, +9.6 pp] | +4.0 pp [+2.4 pp, +5.7 pp] | -0.5 pp [-1.4 pp, +0.3 pp] | +6.9 pp [+4.6 pp, +9.5 pp] |
| (a) calendar first, tail within | precision@5 | +5.1 pp [+3.4 pp, +7.0 pp] | +3.3 pp [+2.1 pp, +4.6 pp] | -0.2 pp [-0.8 pp, +0.4 pp] | +5.0 pp [+3.3 pp, +6.8 pp] |
| (a) calendar first, tail within | recall@3 | +24.0 pp [+17.5 pp, +30.5 pp] | +11.6 pp [+6.8 pp, +16.1 pp] | -3.4 pp [-8.3 pp, +0.4 pp] | +23.1 pp [+16.6 pp, +29.6 pp] |
| (a) calendar first, tail within | recall@5 | +29.5 pp [+22.7 pp, +36.5 pp] | +17.5 pp [+13.1 pp, +22.6 pp] | -1.0 pp [-3.8 pp, +1.7 pp] | +27.6 pp [+21.6 pp, +33.9 pp] |
| (b) tail probability by day type | precision@3 | +2.9 pp [+1.5 pp, +4.4 pp] | -0.1 pp [-0.9 pp, +0.7 pp] | -4.6 pp [-6.5 pp, -2.9 pp] | +2.8 pp [+1.4 pp, +4.3 pp] |
| (b) tail probability by day type | precision@5 | +2.0 pp [+1.0 pp, +3.0 pp] | +0.2 pp [-0.4 pp, +0.7 pp] | -3.4 pp [-4.8 pp, -2.1 pp] | +1.8 pp [+0.9 pp, +2.8 pp] |
| (b) tail probability by day type | recall@3 | +11.6 pp [+6.8 pp, +16.7 pp] | -0.8 pp [-2.6 pp, +0.9 pp] | -15.9 pp [-20.6 pp, -11.5 pp] | +10.7 pp [+5.7 pp, +16.1 pp] |
| (b) tail probability by day type | recall@5 | +13.2 pp [+7.8 pp, +19.1 pp] | +1.2 pp [-1.2 pp, +3.7 pp] | -17.3 pp [-23.2 pp, -11.6 pp] | +11.4 pp [+6.1 pp, +17.1 pp] |
| (c) blend of calendar and tail ranks | precision@3 | +6.6 pp [+4.2 pp, +9.0 pp] | +3.6 pp [+2.1 pp, +5.2 pp] | -1.0 pp [-1.8 pp, -0.1 pp] | +6.5 pp [+4.3 pp, +8.9 pp] |
| (c) blend of calendar and tail ranks | precision@5 | +4.6 pp [+3.0 pp, +6.3 pp] | +2.8 pp [+1.8 pp, +3.9 pp] | -0.7 pp [-1.4 pp, -0.0 pp] | +4.5 pp [+3.0 pp, +6.1 pp] |
| (c) blend of calendar and tail ranks | recall@3 | +22.1 pp [+15.6 pp, +28.7 pp] | +9.8 pp [+5.1 pp, +14.2 pp] | -5.3 pp [-10.0 pp, -1.6 pp] | +21.2 pp [+14.7 pp, +27.8 pp] |
| (c) blend of calendar and tail ranks | recall@5 | +26.7 pp [+20.0 pp, +33.5 pp] | +14.6 pp [+10.3 pp, +19.6 pp] | -3.9 pp [-7.7 pp, -0.2 pp] | +24.8 pp [+18.9 pp, +31.1 pp] |

Primary under block 10: (a) calendar first, tail within [-0.8 pp, +0.4 pp]; (b) tail probability by day type [-4.8 pp, -2.1 pp]; (c) blend of calendar and tail ranks [-1.4 pp, -0.0 pp].

## Precision on the windows that held a pressure day

| Ranker | Metric | vs persistence | vs climatology | vs calendar | vs step 1 |
|---|---|---|---|---|---|
| (a) calendar first, tail within | precision@3 | +29.2 pp [+22.6 pp, +36.7 pp] | +16.8 pp [+12.0 pp, +21.5 pp] | -2.2 pp [-6.0 pp, +1.3 pp] | +29.0 pp [+22.6 pp, +36.5 pp] |
| (a) calendar first, tail within | precision@5 | +21.4 pp [+16.8 pp, +26.6 pp] | +13.9 pp [+10.6 pp, +17.5 pp] | -0.9 pp [-3.4 pp, +1.6 pp] | +20.8 pp [+16.9 pp, +25.8 pp] |
| (b) tail probability by day type | precision@3 | +12.1 pp [+6.4 pp, +17.3 pp] | -0.4 pp [-3.7 pp, +2.9 pp] | -19.4 pp [-24.9 pp, -14.1 pp] | +11.9 pp [+6.3 pp, +17.1 pp] |
| (b) tail probability by day type | precision@5 | +8.2 pp [+4.6 pp, +11.6 pp] | +0.6 pp [-1.7 pp, +3.1 pp] | -14.1 pp [-18.6 pp, -9.8 pp] | +7.6 pp [+4.5 pp, +10.8 pp] |
| (c) blend of calendar and tail ranks | precision@3 | +27.4 pp [+20.7 pp, +34.6 pp] | +15.0 pp [+10.0 pp, +19.8 pp] | -4.1 pp [-7.5 pp, -0.8 pp] | +27.2 pp [+20.6 pp, +34.5 pp] |
| (c) blend of calendar and tail ranks | precision@5 | +19.3 pp [+15.1 pp, +23.6 pp] | +11.8 pp [+8.8 pp, +14.7 pp] | -3.0 pp [-5.8 pp, -0.1 pp] | +18.7 pp [+15.1 pp, +22.8 pp] |

## Precision@5 of (a) calendar first, tail within, by calendar year of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018 | 97 | 50 | 33.6% | 33.0% | +0.6 pp [-2.9 pp, +4.1 pp] | +15.5 pp [+4.5 pp, +27.1 pp] | +22.4 pp [+5.8 pp, +39.7 pp] |
| 2019 | 250 | 239 | 56.7% | 59.2% | -2.5 pp [-5.9 pp, +0.9 pp] | +10.8 pp [+7.0 pp, +14.8 pp] | +19.0 pp [+15.1 pp, +22.3 pp] |
| 2020 | 251 | 29 | 2.3% | 2.3% | +0.0 pp [-1.0 pp, +1.0 pp] | +1.2 pp [+0.0 pp, +2.8 pp] | +0.6 pp [-0.2 pp, +1.6 pp] |
| 2021 | 250 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2022 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2023 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 5.0% | 5.1% | -0.1 pp [-0.5 pp, +0.2 pp] | +1.7 pp [+0.4 pp, +3.2 pp] | +3.1 pp [+0.6 pp, +6.0 pp] |
| 2025 | 229 | 74 | 18.1% | 17.2% | +0.9 pp [-0.8 pp, +3.2 pp] | +4.8 pp [+1.0 pp, +9.0 pp] | +6.5 pp [+1.4 pp, +12.3 pp] |

## Precision@5 of (b) tail probability by day type, by calendar year of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018 | 97 | 50 | 16.5% | 33.0% | -16.5 pp [-29.1 pp, -4.5 pp] | -1.6 pp [-6.0 pp, +2.4 pp] | +5.3 pp [+0.1 pp, +10.9 pp] |
| 2019 | 250 | 239 | 45.2% | 59.2% | -14.0 pp [-18.1 pp, -10.1 pp] | -0.7 pp [-2.4 pp, +0.9 pp] | +7.4 pp [+2.6 pp, +11.7 pp] |
| 2020 | 251 | 29 | 1.4% | 2.3% | -0.9 pp [-2.7 pp, +0.5 pp] | +0.3 pp [-0.3 pp, +1.1 pp] | -0.3 pp [-1.1 pp, +0.4 pp] |
| 2021 | 250 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2022 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2023 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 2.8% | 5.1% | -2.3 pp [-4.3 pp, -0.5 pp] | -0.4 pp [-1.0 pp, +0.0 pp] | +0.9 pp [+0.0 pp, +2.1 pp] |
| 2025 | 229 | 74 | 16.2% | 17.2% | -1.0 pp [-3.6 pp, +1.4 pp] | +2.8 pp [+0.1 pp, +6.1 pp] | +4.6 pp [+0.3 pp, +9.6 pp] |

## Precision@5 of (c) blend of calendar and tail ranks, by calendar year of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018 | 97 | 50 | 28.9% | 33.0% | -4.1 pp [-10.0 pp, +1.2 pp] | +10.8 pp [+3.8 pp, +17.9 pp] | +17.6 pp [+5.2 pp, +30.5 pp] |
| 2019 | 250 | 239 | 56.7% | 59.2% | -2.5 pp [-5.9 pp, +0.9 pp] | +10.8 pp [+7.0 pp, +14.8 pp] | +19.0 pp [+15.1 pp, +22.3 pp] |
| 2020 | 251 | 29 | 2.3% | 2.3% | +0.0 pp [-1.0 pp, +1.0 pp] | +1.2 pp [+0.0 pp, +2.8 pp] | +0.6 pp [-0.2 pp, +1.6 pp] |
| 2021 | 250 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2022 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2023 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 3.2% | 5.1% | -1.9 pp [-3.7 pp, -0.3 pp] | -0.1 pp [-0.5 pp, +0.3 pp] | +1.3 pp [+0.0 pp, +3.0 pp] |
| 2025 | 229 | 74 | 18.1% | 17.2% | +0.9 pp [-0.8 pp, +3.2 pp] | +4.8 pp [+1.0 pp, +9.0 pp] | +6.5 pp [+1.4 pp, +12.3 pp] |

## Precision@5 of (a) calendar first, tail within, by regime of the decision day (2021-23 is the one called out)

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018-19 | 347 | 289 | 50.3% | 51.9% | -1.6 pp [-4.3 pp, +1.1 pp] | +12.1 pp [+7.4 pp, +17.0 pp] | +19.9 pp [+13.6 pp, +26.5 pp] |
| 2020 | 251 | 29 | 2.3% | 2.3% | +0.0 pp [-1.0 pp, +1.0 pp] | +1.2 pp [+0.0 pp, +2.8 pp] | +0.6 pp [-0.2 pp, +1.6 pp] |
| 2021-23 | 748 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 5.0% | 5.1% | -0.1 pp [-0.5 pp, +0.2 pp] | +1.7 pp [+0.4 pp, +3.2 pp] | +3.1 pp [+0.6 pp, +6.0 pp] |
| 2025-26 | 229 | 74 | 18.1% | 17.2% | +0.9 pp [-0.8 pp, +3.2 pp] | +4.8 pp [+1.0 pp, +9.0 pp] | +6.5 pp [+1.4 pp, +12.3 pp] |

## Precision@5 of (b) tail probability by day type, by regime of the decision day (2021-23 is the one called out)

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018-19 | 347 | 289 | 37.2% | 51.9% | -14.7 pp [-20.0 pp, -9.7 pp] | -1.0 pp [-2.8 pp, +0.7 pp] | +6.8 pp [+2.9 pp, +10.4 pp] |
| 2020 | 251 | 29 | 1.4% | 2.3% | -0.9 pp [-2.7 pp, +0.5 pp] | +0.3 pp [-0.3 pp, +1.1 pp] | -0.3 pp [-1.1 pp, +0.4 pp] |
| 2021-23 | 748 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 2.8% | 5.1% | -2.3 pp [-4.3 pp, -0.5 pp] | -0.4 pp [-1.0 pp, +0.0 pp] | +0.9 pp [+0.0 pp, +2.1 pp] |
| 2025-26 | 229 | 74 | 16.2% | 17.2% | -1.0 pp [-3.6 pp, +1.4 pp] | +2.8 pp [+0.1 pp, +6.1 pp] | +4.6 pp [+0.3 pp, +9.6 pp] |

## Precision@5 of (c) blend of calendar and tail ranks, by regime of the decision day (2021-23 is the one called out)

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018-19 | 347 | 289 | 49.0% | 51.9% | -2.9 pp [-5.7 pp, -0.1 pp] | +10.8 pp [+7.0 pp, +14.5 pp] | +18.6 pp [+13.1 pp, +23.9 pp] |
| 2020 | 251 | 29 | 2.3% | 2.3% | +0.0 pp [-1.0 pp, +1.0 pp] | +1.2 pp [+0.0 pp, +2.8 pp] | +0.6 pp [-0.2 pp, +1.6 pp] |
| 2021-23 | 748 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 3.2% | 5.1% | -1.9 pp [-3.7 pp, -0.3 pp] | -0.1 pp [-0.5 pp, +0.3 pp] | +1.3 pp [+0.0 pp, +3.0 pp] |
| 2025-26 | 229 | 74 | 18.1% | 17.2% | +0.9 pp [-0.8 pp, +3.2 pp] | +4.8 pp [+1.0 pp, +9.0 pp] | +6.5 pp [+1.4 pp, +12.3 pp] |

## Precision@5 of (a) calendar first, tail within, by as-of reserve scarcity state of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| abundant | 1041 | 43 | 1.2% | 1.2% | -0.0 pp [-0.1 pp, +0.1 pp] | +0.4 pp [+0.0 pp, +0.8 pp] | +0.7 pp [+0.1 pp, +1.5 pp] |
| ample | 313 | 17 | 1.5% | 1.5% | -0.1 pp [-0.2 pp, +0.0 pp] | +1.1 pp [+0.0 pp, +2.6 pp] | +1.1 pp [+0.0 pp, +2.6 pp] |
| scarce | 430 | 342 | 45.8% | 47.2% | -1.4 pp [-3.7 pp, +0.9 pp] | +11.2 pp [+7.3 pp, +15.2 pp] | +18.1 pp [+12.6 pp, +24.0 pp] |
| tight | 41 | 34 | 50.2% | 43.9% | +6.3 pp [-3.4 pp, +16.1 pp] | +11.9 pp [+6.5 pp, +17.3 pp] | +10.7 pp [-0.2 pp, +21.5 pp] |

## Precision@5 of (b) tail probability by day type, by as-of reserve scarcity state of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| abundant | 1041 | 43 | 0.7% | 1.2% | -0.5 pp [-1.1 pp, -0.1 pp] | -0.1 pp [-0.2 pp, +0.0 pp] | +0.2 pp [+0.0 pp, +0.5 pp] |
| ample | 313 | 17 | 0.4% | 1.5% | -1.1 pp [-2.7 pp, +0.0 pp] | -0.0 pp [-0.1 pp, +0.0 pp] | +0.0 pp [-0.0 pp, +0.1 pp] |
| scarce | 430 | 342 | 34.5% | 47.2% | -12.7 pp [-17.4 pp, -8.2 pp] | -0.1 pp [-1.8 pp, +1.5 pp] | +6.8 pp [+3.4 pp, +10.2 pp] |
| tight | 41 | 34 | 49.3% | 43.9% | +5.4 pp [-4.9 pp, +15.6 pp] | +10.9 pp [+6.5 pp, +15.7 pp] | +9.7 pp [+1.3 pp, +18.0 pp] |

## Precision@5 of (c) blend of calendar and tail ranks, by as-of reserve scarcity state of the decision day

| Group | Decision days | Windows with a pressure day | ranker P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| abundant | 1041 | 43 | 0.7% | 1.2% | -0.5 pp [-1.0 pp, -0.0 pp] | -0.0 pp [-0.1 pp, +0.1 pp] | +0.3 pp [+0.0 pp, +0.7 pp] |
| ample | 313 | 17 | 1.5% | 1.5% | -0.1 pp [-0.2 pp, +0.0 pp] | +1.1 pp [+0.0 pp, +2.6 pp] | +1.1 pp [+0.0 pp, +2.6 pp] |
| scarce | 430 | 342 | 44.7% | 47.2% | -2.5 pp [-4.9 pp, -0.0 pp] | +10.1 pp [+7.0 pp, +13.2 pp] | +17.1 pp [+12.2 pp, +21.9 pp] |
| tight | 41 | 34 | 50.2% | 43.9% | +6.3 pp [-3.4 pp, +16.1 pp] | +11.9 pp [+6.5 pp, +17.3 pp] | +10.7 pp [-0.2 pp, +21.5 pp] |

## Reading

- (a) puts every scheduled risk date above every other day, so its top 5 are the calendar's whenever the window holds five; the tail probability only chooses among them and fills the places when fewer than five are scheduled. (b) and (c) are the two ways of letting the day type move the probability or the rank.
- A window with no pressure day scores zero precision for every ranker, so years with none (2021-23) add decision days and no information; recall is taken on the windows that have one.
- The risk-date definition is `pressure_judge._scheduled_risk_date`, as in step 1. The calendar benchmark breaks its ties by date; the other rankers by their expected value.
- Development data only, nothing registered, no published figure moves. Whether any ranker goes on to registration (step 3) is Eleonora's decision.

Phi across refits: 0.25 to 0.97, median 0.57.

## Each ranker against the calendar (precision@5, development, not a verdict)

- **(a) calendar first, tail within:** 12.8% against 13.0%, gain -0.2 pp [-0.8 pp, +0.4 pp]; the interval does not lie wholly above zero (H8's kill condition is met, as exploration). Below zero in point estimate only: year 2019 -2.5 pp, year 2024 -0.1 pp, regime 2018-19 -1.6 pp, regime 2024 -0.1 pp, scarcity abundant -0.0 pp, scarcity ample -0.1 pp, scarcity scarce -1.4 pp.
- **(b) tail probability by day type:** 9.7% against 13.0%, gain -3.4 pp [-5.1 pp, -1.8 pp]; the interval lies wholly below zero (H8's kill condition is met, as exploration). Loses (interval wholly below zero): year 2018 -16.5 pp, year 2019 -14.0 pp, year 2024 -2.3 pp, regime 2018-19 -14.7 pp, regime 2024 -2.3 pp, scarcity abundant -0.5 pp, scarcity scarce -12.7 pp. Below zero in point estimate only: year 2020 -0.9 pp, year 2025 -1.0 pp, regime 2020 -0.9 pp, regime 2025-26 -1.0 pp, scarcity ample -1.1 pp.
- **(c) blend of calendar and tail ranks:** 12.3% against 13.0%, gain -0.7 pp [-1.5 pp, -0.0 pp]; the interval lies wholly below zero (H8's kill condition is met, as exploration). Loses (interval wholly below zero): year 2024 -1.9 pp, regime 2018-19 -2.9 pp, regime 2024 -1.9 pp, scarcity abundant -0.5 pp, scarcity scarce -2.5 pp. Below zero in point estimate only: year 2018 -4.1 pp, year 2019 -2.5 pp, scarcity ample -0.1 pp.
