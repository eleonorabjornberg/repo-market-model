| row | rule | tier 1, leads 1 to 5: onsets flagged, recall [90%], pooled false alarms per onset (limit 2) | tier 1 | tier 1, leads 3 to 5: onsets flagged, recall [90%], pooled false alarms per onset | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| risk_gbm+settle+h41 | flat | 14 of 26, 0.538 [0.353, 0.710], 2.00 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.58 | no | no | no |
| risk_gbm+settle+h41 | weighted | 14 of 26, 0.538 [0.353, 0.710], 1.44 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.23 | no | no | no |
| risk_gbm+settle+h41+dist_roll | flat | 15 of 26, 0.577 [0.400, 0.762], 1.85 | yes | 12 of 26, 0.462 [0.286, 0.643], 1.35 | no | no | no |
| risk_gbm+settle+h41+dist_roll | weighted | 15 of 26, 0.577 [0.400, 0.762], 1.27 | yes | 12 of 26, 0.462 [0.286, 0.643], 0.87 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | flat | 17 of 26, 0.654 [0.480, 0.818], 2.62 | no | 13 of 26, 0.500 [0.312, 0.692], 2.23 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | weighted | 18 of 26, 0.692 [0.522, 0.852], 1.88 | yes | 14 of 26, 0.538 [0.344, 0.731], 1.62 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+floor | flat | 17 of 26, 0.654 [0.500, 0.812], 4.04 | no | 13 of 26, 0.500 [0.318, 0.690], 3.50 | no | yes | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+floor | weighted | 18 of 26, 0.692 [0.529, 0.850], 2.76 | no | 14 of 26, 0.538 [0.348, 0.731], 2.60 | no | yes | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+state_floor | flat | 17 of 26, 0.654 [0.480, 0.813], 4.04 | no | 13 of 26, 0.500 [0.312, 0.686], 3.50 | no | yes | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+state_floor | weighted | 18 of 26, 0.692 [0.522, 0.850], 2.76 | no | 14 of 26, 0.538 [0.346, 0.727], 2.60 | no | yes | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+recent_floor | flat | 17 of 26, 0.654 [0.476, 0.824], 3.31 | no | 12 of 26, 0.462 [0.273, 0.667], 2.50 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+recent_floor | weighted | 18 of 26, 0.692 [0.514, 0.857], 2.60 | no | 14 of 26, 0.538 [0.348, 0.739], 2.38 | no | no | no |
