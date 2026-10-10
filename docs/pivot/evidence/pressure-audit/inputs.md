Table F. What each input reads at the 16:00 decision, from the as-of rule (`InformationRule.information_set`) over the judge's scored days. Rows before: panel days between the scored day and the observation read (range over the scored days). Hours: how long the observation had been public at the decision, median; negative means the value the rule would read was not yet public, so the input cannot be read at that horizon.

| input | rows before, h = 1 | hours public, h = 1 | rows before, h = 2 | hours public, h = 2 |
|---|---|---|---|---|
| spread (the target) | 2 | – | 3 | – |
| spread_bps | 2 | 1.0 | 3 | 1.0 |
| treasury_settlement | 0 | 1.0 | 0 | -23.0 |
| treasury_settlement_bills | 0 | 1.0 | 0 | -23.0 |
| treasury_settlement_coupons | 0 | 1.0 | 0 | -23.0 |
| reserve_balances | 4 to 6 | 23.5 | 5 to 7 | 23.5 |
| tga | 4 to 6 | 23.5 | 5 to 7 | 23.5 |
| quarter_end | 0 | calendar | 0 | calendar |
| tax_date | 0 | calendar | 0 | calendar |
| days_to_month_end | 0 | calendar | 0 | calendar |
| dealer_treasury_position | 8 | 23.5 | 9 | 23.5 |
| tbill_4w | 2 | 23.5 | 3 | 23.5 |
| tbill_13w | 2 | 23.5 | 3 | 23.5 |
| sofr_p75 | 2 | 1.0 | 3 | 1.0 |
| sofr_p25 | 2 | 1.0 | 3 | 1.0 |
| on_rrp | 2 | 0.0 | 3 | 0.0 |
| tga_daily | 3 | 23.5 | 4 | 23.5 |
| sofr_p99_iorb_bps | 2 | 1.0 | 3 | 1.0 |
| sofr_p75_iorb_bps | 2 | 1.0 | 3 | 1.0 |
| effr | 2 | 1.0 | 3 | 1.0 |
| iorb_announced_change_bps | 0 | 0.0 | 0 | -24.0 |

Table G. How well the value read at h = 1 ranks the +5 bp pressure days and the onsets (AUROC; below 0.5 means a low value goes with pressure), over the judge's shared scored days and, for the onsets, in the years no model warns. Onset AUROC compares an onset with the days that are not pressure days. 2018, 2020 and 2024 hold 4, 2 and 2 onsets, so those cells are descriptions of a few days and not evidence.

| input | pressure days, all years | onsets, all years | onsets 2018 (4) | onsets 2020 (2) | onsets 2024 (2) |
|---|---|---|---|---|---|
| spread_bps | 0.94 | 0.84 | 0.71 | 0.79 | 0.41 |
| treasury_settlement | 0.56 | 0.69 | 0.83 | 0.38 | 0.79 |
| treasury_settlement_bills | 0.50 | 0.51 | 0.53 | 0.43 | 0.62 |
| treasury_settlement_coupons | 0.60 | 0.82 | 0.96 | 0.43 | 0.71 |
| reserve_balances | 0.12 | 0.16 | 0.11 | 0.13 | 0.34 |
| tga | 0.30 | 0.32 | 0.41 | 0.17 | 0.43 |
| quarter_end | 0.52 | 0.55 | 0.50 | 0.49 | 0.75 |
| tax_date | 0.53 | 0.57 | 0.61 | 0.48 | 0.48 |
| days_to_month_end | 0.47 | 0.32 | 0.29 | 0.78 | 0.09 |
| dealer_treasury_position | 0.63 | 0.61 | 0.89 | 0.16 | 0.88 |
| tbill_4w | 0.50 | 0.51 | 0.94 | 0.82 | 0.11 |
| tbill_13w | 0.48 | 0.49 | 0.94 | 0.82 | 0.10 |
| sofr_p75 | 0.53 | 0.51 | 0.81 | 0.89 | 0.10 |
| sofr_p25 | 0.52 | 0.51 | 0.81 | 0.89 | 0.10 |
| on_rrp | 0.24 | 0.24 | 0.25 | 0.69 | 0.28 |
| tga_daily | 0.31 | 0.31 | 0.56 | 0.05 | 0.43 |
| sofr_p99_iorb_bps | 0.93 | 0.85 | 0.72 | 0.96 | 0.62 |
| sofr_p75_iorb_bps | 0.94 | 0.85 | 0.71 | 0.90 | 0.53 |
| effr | 0.52 | 0.51 | 0.85 | 0.90 | 0.10 |
| iorb_announced_change_bps | 0.48 | 0.48 | 0.49 | 0.25 | 0.51 |
