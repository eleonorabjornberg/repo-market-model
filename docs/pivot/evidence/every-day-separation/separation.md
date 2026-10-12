Every-day part of `risk_gbm+every_day+gate+settle+h41+iorb`: 5 onset warnings and 131 false alarms (left out and counted: 65 flagged pressure days that are not onsets; 14 onsets warned by the risk-date part only; 53 false alarms of the risk-date part). 14 inputs examined; at a 90% interval about one in ten that do not separate would show one that excludes 0.5 by chance.

Inputs that separate in Table 1 and again, in the same direction, in Table 2 (the trigger for step 2): `tail_spread_level` (lower).

Onset warnings: 2019-05-28 (leads [2, 3, 4, 5], read at lead 5); 2019-06-25 (leads [4, 5], read at lead 5); 2019-08-13 (leads [5], read at lead 5); 2020-03-04 (leads [1], read at lead 1); 2020-03-12 (leads [5], read at lead 5).

Table 1. Pooled: each input at the decision instant of the farthest lead that flags the day.

| input | family | onset warnings: n, median | false alarms: n, median | AUROC [90% interval] | separates |
|---|---|---|---|---|---|
| `tail_spread_level` | tail_spread | 5, 18.00 | 131, 23.00 | 0.304 [0.16, 0.47] | yes |
| `tail_spread_change_1` | tail_spread | 5, 4.00 | 131, 4.00 | 0.463 [0.33, 0.62] | no |
| `tail_spread_change_5` | tail_spread | 5, 3.00 | 131, 9.00 | 0.362 [0.19, 0.55] | no |
| `tail_spread_change_10` | tail_spread | 5, 1.00 | 131, 6.00 | 0.420 [0.24, 0.62] | no |
| `satiation_distance` | satiation_distance | 5, 0.00 | 131, -0.00 | 0.665 [0.42, 0.89] | no |
| `reserve_level` | reserve_trend | 5, 1586.96 | 131, 1626.47 | 0.389 [0.18, 0.62] | no |
| `reserve_change_5` | reserve_trend | 5, 16.20 | 131, 2.66 | 0.627 [0.41, 0.81] | no |
| `reserve_change_20` | reserve_trend | 5, 10.13 | 131, -25.32 | 0.662 [0.47, 0.84] | no |
| `rows_to_risk_date` | days_to_risk_date | 5, 17.00 | 131, 9.00 | 0.547 [0.30, 0.78] | no |
| `tga_level` | tga_path | 5, 323.79 | 131, 380.56 | 0.360 [0.14, 0.61] | no |
| `tga_change_5` | tga_path | 5, -24.57 | 131, 0.28 | 0.378 [0.19, 0.57] | no |
| `tga_change_10` | tga_path | 5, -33.24 | 131, 2.57 | 0.321 [0.13, 0.53] | no |
| `dispersion_p99_p1` | percentile_dispersion | 5, 0.18 | 131, 0.24 | 0.318 [0.16, 0.49] | yes |
| `dispersion_p99_p75` | percentile_dispersion | 5, 0.08 | 131, 0.07 | 0.492 [0.28, 0.71] | no |

Table 2. The same, false alarms restricted to the years with an onset warning ([2019, 2020]; 76 false alarms).

| input | family | onset warnings: n, median | false alarms: n, median | AUROC [90% interval] | separates |
|---|---|---|---|---|---|
| `tail_spread_level` | tail_spread | 5, 18.00 | 76, 23.00 | 0.276 [0.09, 0.49] | yes |
| `tail_spread_change_1` | tail_spread | 5, 4.00 | 76, 0.00 | 0.521 [0.33, 0.71] | no |
| `tail_spread_change_5` | tail_spread | 5, 3.00 | 76, 5.50 | 0.450 [0.25, 0.66] | no |
| `tail_spread_change_10` | tail_spread | 5, 1.00 | 76, 4.00 | 0.484 [0.28, 0.69] | no |
| `satiation_distance` | satiation_distance | 5, 0.00 | 76, -0.00 | 0.651 [0.39, 0.89] | no |
| `reserve_level` | reserve_trend | 5, 1586.96 | 76, 1530.61 | 0.670 [0.46, 0.87] | no |
| `reserve_change_5` | reserve_trend | 5, 16.20 | 76, 6.05 | 0.549 [0.29, 0.79] | no |
| `reserve_change_20` | reserve_trend | 5, 10.13 | 76, 12.73 | 0.588 [0.36, 0.81] | no |
| `rows_to_risk_date` | days_to_risk_date | 5, 17.00 | 76, 9.00 | 0.563 [0.28, 0.83] | no |
| `tga_level` | tga_path | 5, 323.79 | 76, 284.06 | 0.596 [0.29, 0.88] | no |
| `tga_change_5` | tga_path | 5, -24.57 | 76, -0.68 | 0.430 [0.20, 0.66] | no |
| `tga_change_10` | tga_path | 5, -33.24 | 76, -22.97 | 0.407 [0.17, 0.66] | no |
| `dispersion_p99_p1` | percentile_dispersion | 5, 0.18 | 76, 0.24 | 0.309 [0.10, 0.52] | no |
| `dispersion_p99_p75` | percentile_dispersion | 5, 0.08 | 76, 0.08 | 0.372 [0.13, 0.63] | no |

Table 3, lead 1: 1 onset warnings, 62 false alarms flagged at this lead.

| input | family | onset warnings: n, median | false alarms: n, median | AUROC [90% interval] | separates |
|---|---|---|---|---|---|
| `tail_spread_level` | tail_spread | 1, 16.00 | 62, 19.50 | 0.323 [0.21, 0.44] | no |
| `tail_spread_change_1` | tail_spread | 1, 4.00 | 62, -1.00 | 0.798 [0.70, 0.90] | no |
| `tail_spread_change_5` | tail_spread | 1, 7.00 | 62, 5.50 | 0.516 [0.35, 0.69] | no |
| `tail_spread_change_10` | tail_spread | 1, 7.00 | 62, 4.00 | 0.565 [0.37, 0.76] | no |
| `satiation_distance` | satiation_distance | 1, 0.01 | 62, -0.00 | 0.887 [0.74, 1.00] | no |
| `reserve_level` | reserve_trend | 1, 1626.47 | 62, 1650.99 | 0.484 [0.19, 0.77] | no |
| `reserve_change_5` | reserve_trend | 1, -27.65 | 62, -7.62 | 0.419 [0.26, 0.60] | no |
| `reserve_change_20` | reserve_trend | 1, 10.13 | 62, -51.99 | 0.629 [0.48, 0.77] | no |
| `rows_to_risk_date` | days_to_risk_date | 1, 19.00 | 62, 9.50 | 0.944 [0.92, 0.97] | no |
| `tga_level` | tga_path | 1, 439.37 | 62, 379.90 | 0.597 [0.34, 0.85] | no |
| `tga_change_5` | tga_path | 1, 10.56 | 62, 1.22 | 0.645 [0.52, 0.79] | no |
| `tga_change_10` | tga_path | 1, 28.13 | 62, 7.28 | 0.548 [0.39, 0.73] | no |
| `dispersion_p99_p1` | percentile_dispersion | 1, 0.21 | 62, 0.21 | 0.468 [0.31, 0.62] | no |
| `dispersion_p99_p75` | percentile_dispersion | 1, 0.12 | 62, 0.06 | 0.806 [0.68, 0.92] | no |

Table 3, lead 2: 1 onset warnings, 61 false alarms flagged at this lead.

| input | family | onset warnings: n, median | false alarms: n, median | AUROC [90% interval] | separates |
|---|---|---|---|---|---|
| `tail_spread_level` | tail_spread | 1, 14.00 | 61, 22.00 | 0.066 [0.00, 0.15] | no |
| `tail_spread_change_1` | tail_spread | 1, -1.00 | 61, 0.00 | 0.393 [0.31, 0.47] | no |
| `tail_spread_change_5` | tail_spread | 1, -11.00 | 61, 6.00 | 0.066 [0.02, 0.11] | no |
| `tail_spread_change_10` | tail_spread | 1, -5.00 | 61, 2.00 | 0.205 [0.15, 0.26] | no |
| `satiation_distance` | satiation_distance | 1, -0.01 | 61, -0.01 | 0.418 [0.16, 0.71] | no |
| `reserve_level` | reserve_trend | 1, 1509.87 | 61, 1544.71 | 0.246 [0.12, 0.38] | no |
| `reserve_change_5` | reserve_trend | 1, 24.89 | 61, 4.72 | 0.787 [0.69, 0.88] | no |
| `reserve_change_20` | reserve_trend | 1, -94.61 | 61, -51.69 | 0.393 [0.17, 0.61] | no |
| `rows_to_risk_date` | days_to_risk_date | 1, 3.00 | 61, 9.00 | 0.090 [0.05, 0.13] | no |
| `tga_level` | tga_path | 1, 323.79 | 61, 348.36 | 0.459 [0.18, 0.75] | no |
| `tga_change_5` | tga_path | 1, -24.57 | 61, -3.16 | 0.311 [0.13, 0.48] | no |
| `tga_change_10` | tga_path | 1, -76.71 | 61, -10.30 | 0.033 [0.00, 0.07] | no |
| `dispersion_p99_p1` | percentile_dispersion | 1, 0.19 | 61, 0.20 | 0.393 [0.21, 0.57] | no |
| `dispersion_p99_p75` | percentile_dispersion | 1, 0.06 | 61, 0.06 | 0.516 [0.29, 0.74] | no |

Table 3, lead 3: 1 onset warnings, 61 false alarms flagged at this lead.

| input | family | onset warnings: n, median | false alarms: n, median | AUROC [90% interval] | separates |
|---|---|---|---|---|---|
| `tail_spread_level` | tail_spread | 1, 15.00 | 61, 22.00 | 0.041 [0.01, 0.07] | no |
| `tail_spread_change_1` | tail_spread | 1, 0.00 | 61, 0.00 | 0.484 [0.42, 0.55] | no |
| `tail_spread_change_5` | tail_spread | 1, -1.00 | 61, 5.00 | 0.246 [0.11, 0.38] | no |
| `tail_spread_change_10` | tail_spread | 1, -5.00 | 61, 2.00 | 0.180 [0.13, 0.23] | no |
| `satiation_distance` | satiation_distance | 1, -0.01 | 61, -0.00 | 0.361 [0.15, 0.57] | no |
| `reserve_level` | reserve_trend | 1, 1509.87 | 61, 1544.71 | 0.254 [0.13, 0.39] | no |
| `reserve_change_5` | reserve_trend | 1, 24.89 | 61, 2.66 | 0.779 [0.66, 0.89] | no |
| `reserve_change_20` | reserve_trend | 1, -94.61 | 61, -35.84 | 0.336 [0.16, 0.52] | no |
| `rows_to_risk_date` | days_to_risk_date | 1, 4.00 | 61, 8.00 | 0.131 [0.07, 0.19] | no |
| `tga_level` | tga_path | 1, 323.79 | 61, 310.19 | 0.566 [0.31, 0.82] | no |
| `tga_change_5` | tga_path | 1, -24.57 | 61, -3.64 | 0.385 [0.21, 0.57] | no |
| `tga_change_10` | tga_path | 1, -76.71 | 61, -24.92 | 0.025 [0.00, 0.06] | no |
| `dispersion_p99_p1` | percentile_dispersion | 1, 0.17 | 61, 0.20 | 0.148 [0.05, 0.25] | no |
| `dispersion_p99_p75` | percentile_dispersion | 1, 0.06 | 61, 0.06 | 0.492 [0.29, 0.68] | no |

Table 3, lead 4: 2 onset warnings, 64 false alarms flagged at this lead.

| input | family | onset warnings: n, median | false alarms: n, median | AUROC [90% interval] | separates |
|---|---|---|---|---|---|
| `tail_spread_level` | tail_spread | 2, 15.50 | 64, 22.50 | 0.129 [0.05, 0.21] | no |
| `tail_spread_change_1` | tail_spread | 2, -2.00 | 64, 1.00 | 0.289 [0.21, 0.37] | no |
| `tail_spread_change_5` | tail_spread | 2, 1.00 | 64, 5.50 | 0.289 [0.18, 0.41] | no |
| `tail_spread_change_10` | tail_spread | 2, -1.50 | 64, 2.00 | 0.363 [0.22, 0.54] | no |
| `satiation_distance` | satiation_distance | 2, -0.00 | 64, -0.01 | 0.598 [0.22, 0.95] | no |
| `reserve_level` | reserve_trend | 2, 1548.41 | 64, 1541.98 | 0.445 [0.20, 0.73] | no |
| `reserve_change_5` | reserve_trend | 2, 37.38 | 64, 5.38 | 0.875 [0.72, 0.98] | no |
| `reserve_change_20` | reserve_trend | 2, -8.76 | 64, -35.84 | 0.609 [0.25, 0.94] | no |
| `rows_to_risk_date` | days_to_risk_date | 2, 6.00 | 64, 9.00 | 0.266 [0.18, 0.36] | no |
| `tga_level` | tga_path | 2, 255.67 | 64, 336.07 | 0.328 [0.06, 0.64] | no |
| `tga_change_5` | tga_path | 2, -30.32 | 64, -3.64 | 0.273 [0.08, 0.50] | no |
| `tga_change_10` | tga_path | 2, -68.46 | 64, -10.30 | 0.102 [0.00, 0.27] | no |
| `dispersion_p99_p1` | percentile_dispersion | 2, 0.17 | 64, 0.22 | 0.207 [0.08, 0.35] | no |
| `dispersion_p99_p75` | percentile_dispersion | 2, 0.06 | 64, 0.06 | 0.496 [0.24, 0.73] | no |

Table 3, lead 5: 4 onset warnings, 63 false alarms flagged at this lead.

| input | family | onset warnings: n, median | false alarms: n, median | AUROC [90% interval] | separates |
|---|---|---|---|---|---|
| `tail_spread_level` | tail_spread | 4, 18.00 | 63, 22.00 | 0.367 [0.18, 0.59] | no |
| `tail_spread_change_1` | tail_spread | 4, 2.00 | 63, 1.00 | 0.510 [0.31, 0.71] | no |
| `tail_spread_change_5` | tail_spread | 4, 2.50 | 63, 5.00 | 0.460 [0.25, 0.67] | no |
| `tail_spread_change_10` | tail_spread | 4, 0.50 | 63, 3.00 | 0.484 [0.27, 0.70] | no |
| `satiation_distance` | satiation_distance | 4, -0.00 | 63, -0.01 | 0.710 [0.43, 0.93] | no |
| `reserve_level` | reserve_trend | 4, 1560.74 | 63, 1537.09 | 0.528 [0.29, 0.77] | no |
| `reserve_change_5` | reserve_trend | 4, 20.55 | 63, 6.05 | 0.690 [0.44, 0.90] | no |
| `reserve_change_20` | reserve_trend | 4, 43.61 | 63, -35.84 | 0.643 [0.39, 0.88] | no |
| `rows_to_risk_date` | days_to_risk_date | 4, 11.50 | 63, 9.00 | 0.520 [0.27, 0.79] | no |
| `tga_level` | tga_path | 4, 255.67 | 63, 323.79 | 0.373 [0.11, 0.67] | no |
| `tga_change_5` | tga_path | 4, -27.09 | 63, -3.64 | 0.397 [0.17, 0.63] | no |
| `tga_change_10` | tga_path | 4, -46.73 | 63, -17.75 | 0.317 [0.10, 0.57] | no |
| `dispersion_p99_p1` | percentile_dispersion | 4, 0.18 | 63, 0.21 | 0.355 [0.13, 0.60] | no |
| `dispersion_p99_p75` | percentile_dispersion | 4, 0.07 | 63, 0.07 | 0.464 [0.22, 0.73] | no |
