Table O1. Flags at +5 bp, h = 1 to 5 together. A false alarm is a flag on a day that is not a pressure day (a day and horizon counted once); a hit is an onset flagged at some horizon h >= 1.

| row | flag-days | false alarms | onsets flagged (of 26) |
|---|---|---|---|
| two_part_gbm | 304 | 176 | 15 |
| ngboost_laplace | 395 | 233 | 15 |
| hierarchical_logistic | 707 | 382 | 15 |
| vote_2_of_3 | 385 | 211 | 15 |

Table O2 (false alarms): overlap of the three voters.

| pair | in both | in either | share in both |
|---|---|---|---|
| two_part_gbm & ngboost_laplace | 72 | 337 | 0.21 |
| two_part_gbm & hierarchical_logistic | 96 | 462 | 0.21 |
| ngboost_laplace & hierarchical_logistic | 113 | 502 | 0.23 |

Flagged by all three: 35; by at least one: 545; by exactly one / two / three voters: 334 / 176 / 35.

Table O2 (hits (onsets flagged)): overlap of the three voters.

| pair | in both | in either | share in both |
|---|---|---|---|
| two_part_gbm & ngboost_laplace | 13 | 17 | 0.76 |
| two_part_gbm & hierarchical_logistic | 13 | 17 | 0.76 |
| ngboost_laplace & hierarchical_logistic | 13 | 17 | 0.76 |

Flagged by all three: 12; by at least one: 18; by exactly one / two / three voters: 3 / 3 / 12.
