Table O1. Flags at +5 bp, h = 1 to 5 together. A false alarm is a flag on a day that is not a pressure day (a day and horizon counted once); a hit is an onset flagged at some horizon h >= 1.

| row | flag-days | false alarms | onsets flagged (of 26) |
|---|---|---|---|
| two_part_gbm | 742 | 445 | 15 |
| ngboost_laplace | 751 | 460 | 17 |
| hierarchical_logistic | 1041 | 634 | 15 |
| vote_2_of_3 | 737 | 432 | 15 |

Table O2 (false alarms): overlap of the three voters.

| pair | in both | in either | share in both |
|---|---|---|---|
| two_part_gbm & ngboost_laplace | 299 | 606 | 0.49 |
| two_part_gbm & hierarchical_logistic | 311 | 768 | 0.40 |
| ngboost_laplace & hierarchical_logistic | 348 | 746 | 0.47 |

Flagged by all three: 263; by at least one: 844; by exactly one / two / three voters: 412 / 169 / 263.

Table O2 (hits (onsets flagged)): overlap of the three voters.

| pair | in both | in either | share in both |
|---|---|---|---|
| two_part_gbm & ngboost_laplace | 14 | 18 | 0.78 |
| two_part_gbm & hierarchical_logistic | 13 | 17 | 0.76 |
| ngboost_laplace & hierarchical_logistic | 14 | 18 | 0.78 |

Flagged by all three: 13; by at least one: 19; by exactly one / two / three voters: 4 / 2 / 13.
