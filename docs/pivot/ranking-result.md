# Ranking the next 20 business days: development result (#694)

**Hypothesis and step.** H8 (ranking beats calibrating for desk use), step 1: the target, the benchmarks and a development score. Development data, exploration: not a verdict (scoring protocol v1, #640). Declaration: `metadata/ranking_694.json`, committed before any score.

**Days.** 1825 decision days, 2018-08-09 to 2025-12-02 (targets to 2025-12-31); 90 offered days skipped for want of history. Panel `4ddc3882…`. Bootstrap: stationary, mean block 20 days, 10,000 draws, seed 694; intervals are the 5th and 95th percentile. A positive gain favours the ranker.

## What a window holds

- Windows with at least one pressure day (> +5 bp): 23.9%; mean 1.47 pressure days per window.
- Scheduled risk dates are 16.3% of window days and 36.4% of the pressure days.

## Answer against the kill rule

Primary: precision@5 of the probability ranker against the calendar of known risk dates: 7.9% against 13.0%, gain -5.2 pp [-7.7 pp, -3.0 pp].

The interval does not lie wholly above zero: **no ranking skill beyond the calendar of known risk dates** on development data (H8's kill condition is met, as exploration, not a verdict).

## Top-k precision and recall (all decision days; recall on windows with a pressure day)

| Ranker | P@3 | P@5 | R@3 | R@5 | share of top 5 on a risk date |
|---|---|---|---|---|---|
| model, P(> +5 bp) | 8.0% | 7.9% | 17.0% | 28.2% | 16.2% |
| model, median | 7.3% | 6.9% | 14.7% | 23.1% | 14.5% |
| persistence | 8.0% | 7.7% | 16.1% | 26.3% | 16.1% |
| climatology by day type | 11.0% | 9.5% | 28.4% | 38.3% | 24.0% |
| calendar of risk dates | 15.5% | 13.0% | 43.5% | 56.8% | 64.4% |

## Paired gains over each benchmark (all decision days)

| Ranker | Metric | vs persistence | vs climatology | vs calendar |
|---|---|---|---|---|
| model, P(> +5 bp) | precision@3 | +0.1 pp [-0.4 pp, +0.5 pp] | -2.9 pp [-4.9 pp, -1.2 pp] | -7.5 pp [-11.2 pp, -4.2 pp] |
| model, P(> +5 bp) | precision@5 | +0.1 pp [-0.3 pp, +0.6 pp] | -1.7 pp [-2.8 pp, -0.6 pp] | -5.2 pp [-7.7 pp, -3.0 pp] |
| model, P(> +5 bp) | recall@3 | +0.9 pp [-0.9 pp, +3.1 pp] | -11.4 pp [-18.0 pp, -5.7 pp] | -26.5 pp [-34.5 pp, -19.2 pp] |
| model, P(> +5 bp) | recall@5 | +1.9 pp [-0.3 pp, +4.4 pp] | -10.1 pp [-16.3 pp, -4.5 pp] | -28.6 pp [-36.2 pp, -21.3 pp] |
| model, median | precision@3 | -0.7 pp [-1.6 pp, +0.2 pp] | -3.7 pp [-5.7 pp, -1.9 pp] | -8.2 pp [-12.1 pp, -4.8 pp] |
| model, median | precision@5 | -0.8 pp [-1.6 pp, -0.1 pp] | -2.6 pp [-4.0 pp, -1.3 pp] | -6.1 pp [-8.8 pp, -3.6 pp] |
| model, median | recall@3 | -1.4 pp [-4.0 pp, +1.3 pp] | -13.7 pp [-19.5 pp, -8.5 pp] | -28.8 pp [-36.6 pp, -21.5 pp] |
| model, median | recall@5 | -3.2 pp [-6.5 pp, +0.1 pp] | -15.2 pp [-21.3 pp, -9.8 pp] | -33.7 pp [-41.4 pp, -26.4 pp] |

## Sensitivity: the protocol's block of 10 days instead of the declared 20

Same draws and seed, only the mean block changes (ruling on #722, item 2). Labelled a sensitivity: the declared block is 20 days.

| Ranker | Metric | vs persistence | vs climatology | vs calendar |
|---|---|---|---|---|
| model, P(> +5 bp) | precision@3 | +0.1 pp [-0.5 pp, +0.6 pp] | -2.9 pp [-4.6 pp, -1.4 pp] | -7.5 pp [-10.4 pp, -4.9 pp] |
| model, P(> +5 bp) | precision@5 | +0.1 pp [-0.3 pp, +0.6 pp] | -1.7 pp [-2.7 pp, -0.7 pp] | -5.2 pp [-7.2 pp, -3.4 pp] |
| model, P(> +5 bp) | recall@3 | +0.9 pp [-1.1 pp, +3.2 pp] | -11.4 pp [-17.5 pp, -5.9 pp] | -26.5 pp [-33.9 pp, -19.5 pp] |
| model, P(> +5 bp) | recall@5 | +1.9 pp [-0.6 pp, +4.7 pp] | -10.1 pp [-16.1 pp, -4.6 pp] | -28.6 pp [-35.9 pp, -21.6 pp] |
| model, median | precision@3 | -0.7 pp [-1.6 pp, +0.2 pp] | -3.7 pp [-5.4 pp, -2.1 pp] | -8.2 pp [-11.3 pp, -5.4 pp] |
| model, median | precision@5 | -0.8 pp [-1.6 pp, -0.0 pp] | -2.6 pp [-3.8 pp, -1.5 pp] | -6.1 pp [-8.3 pp, -4.1 pp] |
| model, median | recall@3 | -1.4 pp [-4.1 pp, +1.5 pp] | -13.7 pp [-19.2 pp, -8.7 pp] | -28.8 pp [-36.1 pp, -21.8 pp] |
| model, median | recall@5 | -3.2 pp [-6.8 pp, +0.5 pp] | -15.2 pp [-21.0 pp, -9.9 pp] | -33.7 pp [-40.8 pp, -26.8 pp] |

Primary under block 10: interval [-7.2 pp, -3.4 pp]; it does not lie wholly above zero, as under the declared block.

## Precision on the windows that held a pressure day

| Ranker | Metric | vs persistence | vs climatology | vs calendar |
|---|---|---|---|---|
| model, P(> +5 bp) | precision@3 | +0.2 pp [-1.8 pp, +2.2 pp] | -12.2 pp [-18.3 pp, -6.5 pp] | -31.3 pp [-39.4 pp, -23.5 pp] |
| model, P(> +5 bp) | precision@5 | +0.6 pp [-1.2 pp, +2.2 pp] | -7.0 pp [-10.5 pp, -3.7 pp] | -21.7 pp [-27.0 pp, -16.9 pp] |
| model, median | precision@3 | -2.9 pp [-6.4 pp, +0.8 pp] | -15.4 pp [-20.6 pp, -10.0 pp] | -34.4 pp [-41.9 pp, -26.7 pp] |
| model, median | precision@5 | -3.3 pp [-6.3 pp, -0.3 pp] | -10.8 pp [-14.5 pp, -7.1 pp] | -25.5 pp [-30.4 pp, -20.7 pp] |

## Precision@5 gain of the probability ranker, by calendar year of the decision day

| Group | Decision days | Windows with a pressure day | model P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018 | 97 | 50 | 12.2% | 33.0% | -20.8 pp [-39.2 pp, -4.1 pp] | -5.9 pp [-14.9 pp, +2.2 pp] | +0.9 pp [-1.1 pp, +3.3 pp] |
| 2019 | 250 | 239 | 38.3% | 59.2% | -20.9 pp [-25.2 pp, -16.6 pp] | -7.6 pp [-11.9 pp, -3.5 pp] | +0.6 pp [-2.0 pp, +3.0 pp] |
| 2020 | 251 | 29 | 1.7% | 2.3% | -0.6 pp [-2.7 pp, +1.0 pp] | +0.6 pp [-0.5 pp, +1.8 pp] | -0.1 pp [-0.4 pp, +0.3 pp] |
| 2021 | 250 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2022 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2023 | 249 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 2.1% | 5.1% | -3.1 pp [-6.0 pp, -0.6 pp] | -1.2 pp [-2.9 pp, +0.0 pp] | +0.2 pp [-0.1 pp, +0.5 pp] |
| 2025 | 229 | 74 | 11.5% | 17.2% | -5.7 pp [-11.1 pp, -1.0 pp] | -1.8 pp [-4.9 pp, +0.6 pp] | -0.1 pp [-1.8 pp, +1.6 pp] |

## Precision@5 gain of the probability ranker, by regime of the decision day

| Group | Decision days | Windows with a pressure day | model P@5 | calendar P@5 | gain vs calendar | gain vs climatology | gain vs persistence |
|---|---|---|---|---|---|---|---|
| 2018-19 | 347 | 289 | 31.0% | 51.9% | -20.8 pp [-27.7 pp, -14.2 pp] | -7.1 pp [-11.2 pp, -3.1 pp] | +0.7 pp [-1.3 pp, +2.5 pp] |
| 2020 | 251 | 29 | 1.7% | 2.3% | -0.6 pp [-2.7 pp, +1.0 pp] | +0.6 pp [-0.5 pp, +1.8 pp] | -0.1 pp [-0.4 pp, +0.3 pp] |
| 2021-23 | 748 | 0 | 0.0% | 0.0% | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] | +0.0 pp [+0.0 pp, +0.0 pp] |
| 2024 | 250 | 44 | 2.1% | 5.1% | -3.1 pp [-6.0 pp, -0.6 pp] | -1.2 pp [-2.9 pp, +0.0 pp] | +0.2 pp [-0.1 pp, +0.5 pp] |
| 2025-26 | 229 | 74 | 11.5% | 17.2% | -5.7 pp [-11.1 pp, -1.0 pp] | -1.8 pp [-4.9 pp, +0.6 pp] | -0.1 pp [-1.8 pp, +1.6 pp] |

## Reading

- The model reads no calendar: its 20 scores are the reverted deviation of the last spread plus lead-specific residual quantiles, so within a window its ranking follows the lead, and it cannot place a quarter-end, a tax date or a coupon settlement above a quiet day. The calendar benchmark and the climatology by day type can; that is the comparison the kill rule is stated against.
- The calendar benchmark breaks its ties by date (the earliest first), as declared; the other rankers break ties by their expected value.
- A window with no pressure day scores zero precision for every ranker, so years with none (2021-23) add decision days and no information; recall is taken on the windows that have one.
- The risk-date definition is `pressure_judge._scheduled_risk_date`; #682 (one shared definition) had not merged.
- Development data only, nothing registered, no published figure moves.


Phi across refits: 0.25 to 0.97, median 0.57.
