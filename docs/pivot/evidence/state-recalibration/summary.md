| row | rule | tier 1, leads 1 to 5: onsets flagged, recall [90%] | false alarms per onset, pooled across horizons (in force; limit 2) | worst single lead (earlier counting) | tier 1 | tier 1, leads 3 to 5: onsets flagged, recall [90%] | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | flat | 16 of 26, 0.615 [0.440, 0.786] | 4.38 | 2.35 | no | 12 of 26, 0.462 [0.280, 0.652] | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb | weighted | 19 of 26, 0.731 [0.560, 0.889] | 3.46 | 1.64 | no | 15 of 26, 0.577 [0.385, 0.762] | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | flat | 14 of 26, 0.538 [0.364, 0.720] | 3.38 | 1.77 | no | 11 of 26, 0.423 [0.238, 0.613] | no | yes | no |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | weighted | 18 of 26, 0.692 [0.518, 0.852] | 3.23 | 2.32 | no | 14 of 26, 0.538 [0.350, 0.733] | no | yes | no |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | flat | 14 of 26, 0.538 [0.360, 0.714] | 3.54 | 2.08 | no | 11 of 26, 0.423 [0.240, 0.611] | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | weighted | 18 of 26, 0.692 [0.519, 0.857] | 2.88 | 1.87 | no | 14 of 26, 0.538 [0.350, 0.733] | no | no | no |
