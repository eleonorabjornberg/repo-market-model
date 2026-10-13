# Before and after #662: the screen of every data source (#692, of #478)

Scratch evidence for the re-run of `docs/pivot/source-screen-result.md` after PR #662 (#659) corrected the Fed repo take-up columns (the six test operations before 2019-09-17 are no longer counted;
`fed_repo_days_since_positive` no longer restarts at each test; the change is confined to panel rows 2018-05 to 2019-09-16). The published page and its evidence are not edited; the re-run is in this folder
(`screen.json`, `tables.md`, `heatmap.svg`). Development days only (2018-06-29 to 2025-12-31); no 2026 day is read. Nothing here is selected, and the screen's own caution stands: every correlation is exploratory, and the screen draws no interval
(it never did), so no interval is given for a Spearman figure below. The bootstrap AUROC intervals for the same columns on ordinary days are in `docs/pivot/evidence/source-matrix-692/before-after.md`.

Three sources are set side by side in every table:

* **committed**: the figure in the published evidence (`docs/pivot/evidence/source-screen/`), as published and not edited.
* **pre-#662 rebuild**: the same scripts and fixtures as `main` one commit before #662 (`8cd170fe~1`), exported with `git archive` and run with the page's commands unchanged. Against the re-run it differs in the Fed repo columns and nothing else, so it isolates #662. It is not a published record.
* **re-run**: the page's commands unchanged, on `main` as of this branch (`ee9366eb`), with the corrected `fed_repo_*` columns.

Scratch panels are the page's own chain run on the published panel `4ddc3882…` (`verify-panel` clean). Merged scratch panel (`SCREEN.csv`) sha256: committed `d1bb988f…` (reproduced exactly, see below); pre-#662 rebuild `05a1bf72…`; re-run `939d0511…`.

## Result in short

* **Only the 14 `fed_repo_*` series change** (`fed_repo_submitted`, `_accepted`, `_ops`, `_log_accepted`, `_log_accepted_change`, `_rate_iorb_bps`, `_days_since_positive`, each in both availability readings, plain and `_sameday`). Between the pre-#662 rebuild and the re-run every other cell of `screen.json` is identical to 1e-9, including `srf_take_up` and `srf_take_up_positive` (they read `srf_inputs`, not the repo operations).
* **`fed_repo_days_since_positive` moves most**: pooled correlation with a pressure day +0.065 to +0.129 at lead 1 (+0.089 to +0.154 at lead 10), pre-onset AUC 0.50 to 0.60 (std. diff +0.05 to +1.04). Its rank among the 76 series by largest absolute pooled correlation goes from 35 to 27 (`_sameday` 37 to 28); both stay far below Table 1's cut-off (rank 12, largest absolute correlation about 0.25). The rest of the family moves by 0.004 to 0.013 in absolute value at lead 1 (for example `fed_repo_accepted_sameday` +0.068 to +0.055).
* **In 2018 the series are now constant** (no operation is counted before 2019-09-17), so every 2018 cell is empty in the re-run (the screen leaves a constant side empty); before, they carried the test operations (for example `fed_repo_accepted_sameday` +0.374 on 13 pressure days).
* **No ranking or conclusion moved.** Table 1 (the 12 largest) is the same 12 in the same order. None of the page's findings or caveats names a `fed_repo_*` series, and none of their numbers changes. The only changes to the page's tables would be the positions of the `fed_repo_*` rows lower in the ranking, and the positions of the rows they pass (36 series change rank: 10 `fed_repo_*` series, and 26 others by one to four places only because a `fed_repo_*` row passed them).

## Tables

### Spearman correlation with the +5 bp pressure indicator, all scored days pooled

| series | source | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | rank (max abs over leads) |
|---|---|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#478) | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | 51 of 76 |
| `fed_repo_accepted` | pre-#662 rebuild | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | 51 of 76 |
| `fed_repo_accepted` | re-run | +0.038 | +0.041 | +0.034 | +0.005 | +0.017 | 51 of 76 |
| `fed_repo_accepted_sameday` | committed (#478) | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | 40 of 76 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | 40 of 76 |
| `fed_repo_accepted_sameday` | re-run | +0.055 | +0.038 | +0.042 | +0.020 | +0.027 | 44 of 76 |
| `fed_repo_days_since_positive` | committed (#478) | +0.065 | +0.068 | +0.071 | +0.084 | +0.089 | 35 of 76 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | +0.065 | +0.068 | +0.071 | +0.084 | +0.089 | 36 of 76 |
| `fed_repo_days_since_positive` | re-run | +0.129 | +0.130 | +0.136 | +0.151 | +0.154 | 27 of 76 |
| `fed_repo_days_since_positive_sameday` | committed (#478) | +0.049 | +0.065 | +0.067 | +0.074 | +0.076 | 37 of 76 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | +0.049 | +0.065 | +0.067 | +0.074 | +0.076 | 38 of 76 |
| `fed_repo_days_since_positive_sameday` | re-run | +0.123 | +0.129 | +0.130 | +0.142 | +0.149 | 28 of 76 |
| `fed_repo_log_accepted` | committed (#478) | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | 52 of 76 |
| `fed_repo_log_accepted` | pre-#662 rebuild | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | 52 of 76 |
| `fed_repo_log_accepted` | re-run | +0.038 | +0.041 | +0.034 | +0.005 | +0.017 | 52 of 76 |
| `fed_repo_log_accepted_change` | committed (#478) | +0.035 | +0.008 | +0.004 | -0.032 | -0.020 | 55 of 76 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | +0.035 | +0.008 | +0.004 | -0.032 | -0.020 | 56 of 76 |
| `fed_repo_log_accepted_change` | re-run | +0.031 | +0.008 | +0.004 | -0.032 | -0.017 | 56 of 76 |
| `fed_repo_log_accepted_change_sameday` | committed (#478) | +0.023 | +0.035 | +0.008 | +0.028 | +0.024 | 56 of 76 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | +0.023 | +0.035 | +0.008 | +0.028 | +0.024 | 57 of 76 |
| `fed_repo_log_accepted_change_sameday` | re-run | +0.019 | +0.031 | +0.008 | +0.028 | +0.013 | 58 of 76 |
| `fed_repo_log_accepted_sameday` | committed (#478) | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | 41 of 76 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | 41 of 76 |
| `fed_repo_log_accepted_sameday` | re-run | +0.055 | +0.038 | +0.042 | +0.020 | +0.027 | 45 of 76 |
| `fed_repo_ops` | committed (#478) | +0.032 | +0.028 | +0.027 | -0.006 | +0.001 | 58 of 76 |
| `fed_repo_ops` | pre-#662 rebuild | +0.032 | +0.028 | +0.027 | -0.006 | +0.001 | 58 of 76 |
| `fed_repo_ops` | re-run | +0.025 | +0.025 | +0.024 | -0.009 | +0.002 | 69 of 76 |
| `fed_repo_ops_sameday` | committed (#478) | +0.047 | +0.033 | +0.029 | +0.012 | +0.024 | 48 of 76 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | +0.047 | +0.033 | +0.029 | +0.012 | +0.024 | 48 of 76 |
| `fed_repo_ops_sameday` | re-run | +0.036 | +0.026 | +0.026 | +0.009 | +0.013 | 54 of 76 |
| `fed_repo_rate_iorb_bps` | committed (#478) | -0.009 | +0.031 | +0.028 | +0.004 | +0.004 | 61 of 76 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | -0.009 | +0.031 | +0.028 | +0.004 | +0.004 | 61 of 76 |
| `fed_repo_rate_iorb_bps` | re-run | -0.016 | +0.029 | +0.025 | +0.002 | +0.005 | 63 of 76 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#478) | -0.009 | +0.032 | +0.029 | +0.005 | +0.004 | 59 of 76 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | -0.009 | +0.032 | +0.029 | +0.005 | +0.004 | 59 of 76 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | -0.015 | +0.030 | +0.026 | +0.003 | +0.006 | 61 of 76 |
| `fed_repo_submitted` | committed (#478) | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | 53 of 76 |
| `fed_repo_submitted` | pre-#662 rebuild | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | 53 of 76 |
| `fed_repo_submitted` | re-run | +0.037 | +0.041 | +0.034 | +0.005 | +0.017 | 53 of 76 |
| `fed_repo_submitted_sameday` | committed (#478) | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | 42 of 76 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | 42 of 76 |
| `fed_repo_submitted_sameday` | re-run | +0.055 | +0.038 | +0.042 | +0.019 | +0.027 | 46 of 76 |
| `srf_take_up` | committed (#478) | +0.182 | +0.209 | +0.195 | +0.138 | +0.223 | 14 of 76 |
| `srf_take_up` | pre-#662 rebuild | +0.182 | +0.209 | +0.195 | +0.138 | +0.223 | 14 of 76 |
| `srf_take_up` | re-run | +0.182 | +0.209 | +0.195 | +0.138 | +0.223 | 14 of 76 |
| `srf_take_up_positive` | committed (#478) | -0.023 | -0.007 | -0.007 | -0.036 | -0.000 | 54 of 76 |
| `srf_take_up_positive` | pre-#662 rebuild | -0.023 | -0.007 | -0.007 | -0.036 | -0.000 | 55 of 76 |
| `srf_take_up_positive` | re-run | -0.023 | -0.007 | -0.007 | -0.036 | -0.000 | 55 of 76 |

### Spearman correlation with the spread level, all scored days pooled

| series | source | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 |
|---|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#478) | +0.162 | +0.167 | +0.165 | +0.151 | +0.156 |
| `fed_repo_accepted` | pre-#662 rebuild | +0.162 | +0.167 | +0.165 | +0.151 | +0.156 |
| `fed_repo_accepted` | re-run | +0.155 | +0.161 | +0.159 | +0.144 | +0.149 |
| `fed_repo_accepted_sameday` | committed (#478) | +0.168 | +0.164 | +0.169 | +0.160 | +0.159 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | +0.168 | +0.164 | +0.169 | +0.160 | +0.159 |
| `fed_repo_accepted_sameday` | re-run | +0.160 | +0.157 | +0.162 | +0.154 | +0.151 |
| `fed_repo_days_since_positive` | committed (#478) | +0.102 | +0.100 | +0.103 | +0.107 | +0.107 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | +0.102 | +0.100 | +0.103 | +0.107 | +0.107 |
| `fed_repo_days_since_positive` | re-run | +0.188 | +0.186 | +0.188 | +0.194 | +0.197 |
| `fed_repo_days_since_positive_sameday` | committed (#478) | +0.100 | +0.100 | +0.099 | +0.103 | +0.107 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | +0.100 | +0.100 | +0.099 | +0.103 | +0.107 |
| `fed_repo_days_since_positive_sameday` | re-run | +0.186 | +0.186 | +0.185 | +0.190 | +0.197 |
| `fed_repo_log_accepted` | committed (#478) | +0.162 | +0.167 | +0.165 | +0.151 | +0.156 |
| `fed_repo_log_accepted` | pre-#662 rebuild | +0.162 | +0.167 | +0.165 | +0.151 | +0.156 |
| `fed_repo_log_accepted` | re-run | +0.155 | +0.161 | +0.159 | +0.144 | +0.149 |
| `fed_repo_log_accepted_change` | committed (#478) | +0.005 | +0.003 | +0.004 | -0.001 | -0.005 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | +0.005 | +0.003 | +0.004 | -0.001 | -0.005 |
| `fed_repo_log_accepted_change` | re-run | +0.004 | +0.003 | +0.005 | -0.001 | -0.005 |
| `fed_repo_log_accepted_change_sameday` | committed (#478) | +0.010 | +0.006 | +0.005 | +0.010 | -0.002 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | +0.010 | +0.006 | +0.005 | +0.010 | -0.002 |
| `fed_repo_log_accepted_change_sameday` | re-run | +0.010 | +0.005 | +0.004 | +0.009 | -0.003 |
| `fed_repo_log_accepted_sameday` | committed (#478) | +0.168 | +0.164 | +0.169 | +0.160 | +0.159 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | +0.168 | +0.164 | +0.169 | +0.160 | +0.159 |
| `fed_repo_log_accepted_sameday` | re-run | +0.160 | +0.157 | +0.162 | +0.154 | +0.151 |
| `fed_repo_ops` | committed (#478) | +0.119 | +0.126 | +0.124 | +0.111 | +0.115 |
| `fed_repo_ops` | pre-#662 rebuild | +0.119 | +0.126 | +0.124 | +0.111 | +0.115 |
| `fed_repo_ops` | re-run | +0.112 | +0.121 | +0.120 | +0.106 | +0.110 |
| `fed_repo_ops_sameday` | committed (#478) | +0.123 | +0.121 | +0.128 | +0.120 | +0.119 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | +0.123 | +0.121 | +0.128 | +0.120 | +0.119 |
| `fed_repo_ops_sameday` | re-run | +0.116 | +0.115 | +0.122 | +0.114 | +0.113 |
| `fed_repo_rate_iorb_bps` | committed (#478) | -0.027 | -0.010 | -0.009 | -0.019 | -0.015 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | -0.027 | -0.010 | -0.009 | -0.019 | -0.015 |
| `fed_repo_rate_iorb_bps` | re-run | -0.032 | -0.015 | -0.013 | -0.024 | -0.020 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#478) | -0.024 | -0.008 | -0.008 | -0.018 | -0.014 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | -0.024 | -0.008 | -0.008 | -0.018 | -0.014 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | -0.030 | -0.013 | -0.012 | -0.022 | -0.018 |
| `fed_repo_submitted` | committed (#478) | +0.162 | +0.167 | +0.165 | +0.151 | +0.156 |
| `fed_repo_submitted` | pre-#662 rebuild | +0.162 | +0.167 | +0.165 | +0.151 | +0.156 |
| `fed_repo_submitted` | re-run | +0.154 | +0.161 | +0.159 | +0.144 | +0.149 |
| `fed_repo_submitted_sameday` | committed (#478) | +0.168 | +0.164 | +0.169 | +0.160 | +0.159 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | +0.168 | +0.164 | +0.169 | +0.160 | +0.159 |
| `fed_repo_submitted_sameday` | re-run | +0.160 | +0.157 | +0.162 | +0.154 | +0.151 |
| `srf_take_up` | committed (#478) | +0.293 | +0.303 | +0.299 | +0.275 | +0.283 |
| `srf_take_up` | pre-#662 rebuild | +0.293 | +0.303 | +0.299 | +0.275 | +0.283 |
| `srf_take_up` | re-run | +0.293 | +0.303 | +0.299 | +0.275 | +0.283 |
| `srf_take_up_positive` | committed (#478) | -0.103 | -0.090 | -0.091 | -0.105 | -0.096 |
| `srf_take_up_positive` | pre-#662 rebuild | -0.103 | -0.090 | -0.091 | -0.105 | -0.096 |
| `srf_take_up_positive` | re-run | -0.103 | -0.090 | -0.091 | -0.105 | -0.096 |

### Spearman correlation with the day's spread change, all scored days pooled

| series | source | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 |
|---|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#478) | -0.003 | +0.025 | -0.010 | +0.000 | +0.028 |
| `fed_repo_accepted` | pre-#662 rebuild | -0.003 | +0.025 | -0.010 | +0.000 | +0.028 |
| `fed_repo_accepted` | re-run | -0.000 | +0.033 | -0.007 | +0.004 | +0.034 |
| `fed_repo_accepted_sameday` | committed (#478) | -0.027 | -0.003 | +0.024 | -0.006 | -0.004 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | -0.027 | -0.003 | +0.024 | -0.006 | -0.004 |
| `fed_repo_accepted_sameday` | re-run | -0.027 | -0.000 | +0.032 | -0.010 | -0.005 |
| `fed_repo_days_since_positive` | committed (#478) | -0.005 | -0.013 | -0.001 | -0.006 | -0.029 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | -0.005 | -0.013 | -0.001 | -0.006 | -0.029 |
| `fed_repo_days_since_positive` | re-run | -0.022 | -0.029 | -0.010 | -0.020 | -0.037 |
| `fed_repo_days_since_positive_sameday` | committed (#478) | +0.011 | -0.005 | -0.012 | -0.006 | -0.002 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | +0.011 | -0.005 | -0.012 | -0.006 | -0.002 |
| `fed_repo_days_since_positive_sameday` | re-run | -0.006 | -0.022 | -0.028 | -0.012 | -0.008 |
| `fed_repo_log_accepted` | committed (#478) | -0.003 | +0.025 | -0.010 | +0.000 | +0.028 |
| `fed_repo_log_accepted` | pre-#662 rebuild | -0.003 | +0.025 | -0.010 | +0.000 | +0.028 |
| `fed_repo_log_accepted` | re-run | -0.000 | +0.033 | -0.007 | +0.004 | +0.034 |
| `fed_repo_log_accepted_change` | committed (#478) | -0.030 | +0.011 | -0.036 | -0.027 | +0.010 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | -0.030 | +0.011 | -0.036 | -0.027 | +0.010 |
| `fed_repo_log_accepted_change` | re-run | -0.034 | +0.014 | -0.031 | -0.027 | +0.015 |
| `fed_repo_log_accepted_change_sameday` | committed (#478) | +0.018 | -0.029 | +0.012 | +0.031 | +0.005 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | +0.018 | -0.029 | +0.012 | +0.031 | +0.005 |
| `fed_repo_log_accepted_change_sameday` | re-run | +0.016 | -0.032 | +0.015 | +0.025 | -0.000 |
| `fed_repo_log_accepted_sameday` | committed (#478) | -0.027 | -0.003 | +0.024 | -0.006 | -0.004 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | -0.027 | -0.003 | +0.024 | -0.006 | -0.004 |
| `fed_repo_log_accepted_sameday` | re-run | -0.027 | -0.000 | +0.032 | -0.010 | -0.005 |
| `fed_repo_ops` | committed (#478) | +0.000 | +0.032 | -0.010 | +0.004 | +0.023 |
| `fed_repo_ops` | pre-#662 rebuild | +0.000 | +0.032 | -0.010 | +0.004 | +0.023 |
| `fed_repo_ops` | re-run | +0.003 | +0.039 | -0.006 | +0.008 | +0.028 |
| `fed_repo_ops_sameday` | committed (#478) | -0.026 | +0.000 | +0.030 | -0.003 | -0.008 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | -0.026 | +0.000 | +0.030 | -0.003 | -0.008 |
| `fed_repo_ops_sameday` | re-run | -0.026 | +0.003 | +0.038 | -0.006 | -0.009 |
| `fed_repo_rate_iorb_bps` | committed (#478) | -0.014 | +0.061 | -0.003 | +0.003 | +0.011 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | -0.014 | +0.061 | -0.003 | +0.003 | +0.011 |
| `fed_repo_rate_iorb_bps` | re-run | -0.011 | +0.067 | -0.000 | +0.007 | +0.015 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#478) | -0.014 | +0.059 | -0.005 | +0.004 | +0.011 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | -0.014 | +0.059 | -0.005 | +0.004 | +0.011 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | -0.011 | +0.066 | -0.002 | +0.008 | +0.015 |
| `fed_repo_submitted` | committed (#478) | -0.003 | +0.026 | -0.010 | +0.000 | +0.028 |
| `fed_repo_submitted` | pre-#662 rebuild | -0.003 | +0.026 | -0.010 | +0.000 | +0.028 |
| `fed_repo_submitted` | re-run | -0.000 | +0.034 | -0.006 | +0.004 | +0.034 |
| `fed_repo_submitted_sameday` | committed (#478) | -0.027 | -0.003 | +0.024 | -0.006 | -0.003 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | -0.027 | -0.003 | +0.024 | -0.006 | -0.003 |
| `fed_repo_submitted_sameday` | re-run | -0.027 | -0.000 | +0.032 | -0.010 | -0.005 |
| `srf_take_up` | committed (#478) | +0.004 | +0.066 | -0.021 | +0.015 | +0.052 |
| `srf_take_up` | pre-#662 rebuild | +0.004 | +0.066 | -0.021 | +0.015 | +0.052 |
| `srf_take_up` | re-run | +0.004 | +0.066 | -0.021 | +0.015 | +0.052 |
| `srf_take_up_positive` | committed (#478) | +0.018 | +0.060 | -0.003 | +0.022 | +0.039 |
| `srf_take_up_positive` | pre-#662 rebuild | +0.018 | +0.060 | -0.003 | +0.022 | +0.039 |
| `srf_take_up_positive` | re-run | +0.018 | +0.060 | -0.003 | +0.022 | +0.039 |

### Pressure indicator, lead 1, by as-of regime (the change is confined to 2018-05 to 2019-09-16, almost all of it in the scarce regime)

| series | source | ample (6 pressure days) | scarce (134 pressure days) | 2018 (13) | 2019 (89) |
|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#478) | +0.024 | -0.062 | +0.165 | -0.106 |
| `fed_repo_accepted` | pre-#662 rebuild | +0.024 | -0.062 | +0.165 | -0.106 |
| `fed_repo_accepted` | re-run | +0.024 | -0.068 | - | -0.110 |
| `fed_repo_accepted_sameday` | committed (#478) | +0.032 | -0.034 | +0.374 | -0.108 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | +0.032 | -0.034 | +0.374 | -0.108 |
| `fed_repo_accepted_sameday` | re-run | +0.032 | -0.046 | - | -0.112 |
| `fed_repo_days_since_positive` | committed (#478) | -0.057 | +0.042 | -0.251 | +0.233 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | -0.057 | +0.042 | -0.251 | +0.233 |
| `fed_repo_days_since_positive` | re-run | -0.057 | +0.050 | - | +0.129 |
| `fed_repo_days_since_positive_sameday` | committed (#478) | -0.049 | +0.010 | -0.344 | +0.205 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | -0.049 | +0.010 | -0.344 | +0.205 |
| `fed_repo_days_since_positive_sameday` | re-run | -0.049 | +0.037 | - | +0.116 |
| `fed_repo_log_accepted` | committed (#478) | +0.024 | -0.062 | +0.165 | -0.106 |
| `fed_repo_log_accepted` | pre-#662 rebuild | +0.024 | -0.062 | +0.165 | -0.106 |
| `fed_repo_log_accepted` | re-run | +0.024 | -0.068 | - | -0.110 |
| `fed_repo_log_accepted_change` | committed (#478) | -0.068 | +0.100 | +0.147 | +0.106 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | -0.068 | +0.100 | +0.147 | +0.106 |
| `fed_repo_log_accepted_change` | re-run | -0.068 | +0.096 | - | +0.108 |
| `fed_repo_log_accepted_change_sameday` | committed (#478) | +0.004 | +0.054 | +0.147 | -0.015 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | +0.004 | +0.054 | +0.147 | -0.015 |
| `fed_repo_log_accepted_change_sameday` | re-run | +0.004 | +0.049 | - | -0.014 |
| `fed_repo_log_accepted_sameday` | committed (#478) | +0.032 | -0.034 | +0.374 | -0.108 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | +0.032 | -0.034 | +0.374 | -0.108 |
| `fed_repo_log_accepted_sameday` | re-run | +0.032 | -0.046 | - | -0.112 |
| `fed_repo_ops` | committed (#478) | +0.029 | -0.058 | +0.165 | -0.108 |
| `fed_repo_ops` | pre-#662 rebuild | +0.029 | -0.058 | +0.165 | -0.108 |
| `fed_repo_ops` | re-run | +0.029 | -0.065 | - | -0.114 |
| `fed_repo_ops_sameday` | committed (#478) | +0.029 | -0.035 | +0.374 | -0.120 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | +0.029 | -0.035 | +0.374 | -0.120 |
| `fed_repo_ops_sameday` | re-run | +0.029 | -0.050 | - | -0.125 |
| `fed_repo_rate_iorb_bps` | committed (#478) | +0.033 | +0.016 | +0.164 | -0.072 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | +0.033 | +0.016 | +0.164 | -0.072 |
| `fed_repo_rate_iorb_bps` | re-run | +0.033 | +0.006 | - | -0.080 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#478) | +0.034 | +0.016 | +0.164 | -0.072 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | +0.034 | +0.016 | +0.164 | -0.072 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | +0.034 | +0.006 | - | -0.080 |
| `fed_repo_submitted` | committed (#478) | +0.024 | -0.064 | +0.165 | -0.106 |
| `fed_repo_submitted` | pre-#662 rebuild | +0.024 | -0.064 | +0.165 | -0.106 |
| `fed_repo_submitted` | re-run | +0.024 | -0.070 | - | -0.110 |
| `fed_repo_submitted_sameday` | committed (#478) | +0.032 | -0.035 | +0.374 | -0.106 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | +0.032 | -0.035 | +0.374 | -0.106 |
| `fed_repo_submitted_sameday` | re-run | +0.032 | -0.047 | - | -0.110 |

### Pre-onset contrast at lead 1 (1 to 5 panel days before the 27 onsets against all other days): AUC, and the difference in the other days' standard deviations

| series | source | pooled AUC | pooled std. diff | scarce AUC (114 pre-onset days) | ample AUC (16) |
|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#478) | 0.55 | +0.41 | 0.46 | 0.67 |
| `fed_repo_accepted` | pre-#662 rebuild | 0.55 | +0.41 | 0.46 | 0.67 |
| `fed_repo_accepted` | re-run | 0.55 | +0.41 | 0.47 | 0.67 |
| `fed_repo_accepted_sameday` | committed (#478) | 0.54 | +0.44 | 0.45 | 0.71 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | 0.54 | +0.44 | 0.45 | 0.71 |
| `fed_repo_accepted_sameday` | re-run | 0.54 | +0.44 | 0.46 | 0.71 |
| `fed_repo_days_since_positive` | committed (#478) | 0.50 | +0.05 | 0.46 | 0.24 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | 0.50 | +0.05 | 0.46 | 0.24 |
| `fed_repo_days_since_positive` | re-run | 0.60 | +1.04 | 0.52 | 0.24 |
| `fed_repo_days_since_positive_sameday` | committed (#478) | 0.51 | +0.07 | 0.47 | 0.22 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | 0.51 | +0.07 | 0.47 | 0.22 |
| `fed_repo_days_since_positive_sameday` | re-run | 0.60 | +1.05 | 0.52 | 0.22 |
| `fed_repo_log_accepted` | committed (#478) | 0.55 | +0.37 | 0.46 | 0.67 |
| `fed_repo_log_accepted` | pre-#662 rebuild | 0.55 | +0.37 | 0.46 | 0.67 |
| `fed_repo_log_accepted` | re-run | 0.55 | +0.37 | 0.47 | 0.67 |
| `fed_repo_log_accepted_change` | committed (#478) | 0.49 | -0.07 | 0.50 | 0.50 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | 0.49 | -0.07 | 0.50 | 0.50 |
| `fed_repo_log_accepted_change` | re-run | 0.50 | -0.07 | 0.50 | 0.50 |
| `fed_repo_log_accepted_change_sameday` | committed (#478) | 0.49 | -0.02 | 0.50 | 0.48 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | 0.49 | -0.02 | 0.50 | 0.48 |
| `fed_repo_log_accepted_change_sameday` | re-run | 0.49 | -0.02 | 0.49 | 0.48 |
| `fed_repo_log_accepted_sameday` | committed (#478) | 0.54 | +0.37 | 0.45 | 0.71 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | 0.54 | +0.37 | 0.45 | 0.71 |
| `fed_repo_log_accepted_sameday` | re-run | 0.54 | +0.37 | 0.46 | 0.71 |
| `fed_repo_ops` | committed (#478) | 0.54 | +0.17 | 0.46 | 0.68 |
| `fed_repo_ops` | pre-#662 rebuild | 0.54 | +0.17 | 0.46 | 0.68 |
| `fed_repo_ops` | re-run | 0.54 | +0.17 | 0.46 | 0.68 |
| `fed_repo_ops_sameday` | committed (#478) | 0.53 | +0.17 | 0.45 | 0.71 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | 0.53 | +0.17 | 0.45 | 0.71 |
| `fed_repo_ops_sameday` | re-run | 0.54 | +0.18 | 0.45 | 0.71 |
| `fed_repo_rate_iorb_bps` | committed (#478) | 0.51 | -0.09 | 0.50 | 0.67 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | 0.51 | -0.09 | 0.50 | 0.67 |
| `fed_repo_rate_iorb_bps` | re-run | 0.51 | -0.09 | 0.50 | 0.67 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#478) | 0.51 | -0.09 | 0.50 | 0.68 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | 0.51 | -0.09 | 0.50 | 0.68 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | 0.51 | -0.08 | 0.50 | 0.68 |
| `fed_repo_submitted` | committed (#478) | 0.55 | +0.44 | 0.46 | 0.67 |
| `fed_repo_submitted` | pre-#662 rebuild | 0.55 | +0.44 | 0.46 | 0.67 |
| `fed_repo_submitted` | re-run | 0.55 | +0.44 | 0.47 | 0.67 |
| `fed_repo_submitted_sameday` | committed (#478) | 0.54 | +0.46 | 0.46 | 0.71 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | 0.54 | +0.46 | 0.46 | 0.71 |
| `fed_repo_submitted_sameday` | re-run | 0.54 | +0.46 | 0.46 | 0.71 |

### Did the ranking move?

* Table 1 (the 12 series with the largest absolute pooled pressure correlation): committed ['sofr_p75_iorb_bps', 'spread_bps', 'sofr_p99_iorb_bps', 'policy_reserve_management_in_force', 'ofr_gcf_rate', 'reserve_scarcity_state', 'sofr_above_effr_share_20', 'spread_nowcast_bps', 'reserve_balances', 'sofr_p99_iorb_sd15_bps', 'on_rrp_below_100bn', 'on_rrp']; pre-#662 rebuild ['sofr_p75_iorb_bps', 'spread_bps', 'sofr_p99_iorb_bps', 'policy_reserve_management_in_force', 'ofr_gcf_rate', 'reserve_scarcity_state', 'sofr_above_effr_share_20', 'spread_nowcast_bps', 'reserve_balances', 'sofr_p99_iorb_sd15_bps', 'on_rrp_below_100bn', 'on_rrp']; re-run ['sofr_p75_iorb_bps', 'spread_bps', 'sofr_p99_iorb_bps', 'policy_reserve_management_in_force', 'ofr_gcf_rate', 'reserve_scarcity_state', 'sofr_above_effr_share_20', 'spread_nowcast_bps', 'reserve_balances', 'sofr_p99_iorb_sd15_bps', 'on_rrp_below_100bn', 'on_rrp'].
  Same 12, same order, committed against re-run: **True**; pre-#662 rebuild against re-run: **True**.

Rank by largest absolute pooled pressure correlation over leads 1 to 10, among the series with a value (the rank is Table 1's order, `tables.md`). Series whose rank differs between the pre-#662 rebuild and the re-run (isolating #662):

| series | pre-#662 rank | re-run rank | committed rank |
|---|---|---|---|
| `fed_repo_days_since_positive` (reads fed_repo_*) | 36 | 27 | 35 |
| `fed_repo_days_since_positive_sameday` (reads fed_repo_*) | 38 | 28 | 37 |
| `policy_days_since_known` | 27 | 29 | 27 |
| `bgcr_volume` | 28 | 30 | 28 |
| `dealer_treasury_position` | 29 | 31 | 29 |
| `policy_slr_exclusion_in_force` | 30 | 32 | 30 |
| `iorb_announced_change_bps` | 31 | 33 | 31 |
| `policy_iorb_offset_bp` | 32 | 34 | 32 |
| `quarter_end` | 33 | 35 | 33 |
| `dvp_volume_share_chg20` | 34 | 36 | 34 |
| `net_settlement_due_5d` | 35 | 37 | 38 |
| `policy_pending_count` | 37 | 38 | 36 |
| `tga_change_5d` | 43 | 40 | 43 |
| `treasury_settlement` | 44 | 41 | 44 |
| `tax_date` | 45 | 42 | 45 |
| `sofr_volume` | 46 | 43 | 46 |
| `fed_repo_accepted_sameday` (reads fed_repo_*) | 40 | 44 | 40 |
| `fed_repo_log_accepted_sameday` (reads fed_repo_*) | 41 | 45 | 41 |
| `fed_repo_submitted_sameday` (reads fed_repo_*) | 42 | 46 | 42 |
| `treasury_settlement_soma` | 49 | 48 | 49 |
| `sofr_p99_p75_bps` | 50 | 49 | 50 |
| `net_settlement` | 54 | 50 | 57 |
| `fed_repo_ops_sameday` (reads fed_repo_*) | 48 | 54 | 48 |
| `sofr_p99` | 60 | 57 | 60 |
| `fed_repo_log_accepted_change_sameday` (reads fed_repo_*) | 57 | 58 | 56 |
| `net_settlement_bills` | 62 | 59 | 62 |
| `days_to_month_end` | 63 | 60 | 63 |
| `fed_repo_rate_iorb_bps_sameday` (reads fed_repo_*) | 59 | 61 | 59 |
| `sofr_p75` | 64 | 62 | 64 |
| `fed_repo_rate_iorb_bps` (reads fed_repo_*) | 61 | 63 | 61 |
| `tga_daily_change` | 65 | 64 | 65 |
| `sofr_p1` | 66 | 65 | 66 |
| `bgcr` | 67 | 66 | 67 |
| `tgcr` | 68 | 67 | 68 |
| `sofr_p25` | 69 | 68 | 69 |
| `fed_repo_ops` (reads fed_repo_*) | 58 | 69 | 58 |

36 series change rank between the pre-#662 rebuild and the re-run: 10 of the 14 that read `fed_repo_*` and 26 others, which move only because a `fed_repo_*` series passed them; none of their own figures changed.

### Series whose figures differ, pre-#662 rebuild against re-run (every cell of `screen.json`, tolerance 1e-9)

14 series: `fed_repo_accepted`, `fed_repo_accepted_sameday`, `fed_repo_days_since_positive`, `fed_repo_days_since_positive_sameday`, `fed_repo_log_accepted`, `fed_repo_log_accepted_change`, `fed_repo_log_accepted_change_sameday`, `fed_repo_log_accepted_sameday`, `fed_repo_ops`, `fed_repo_ops_sameday`, `fed_repo_rate_iorb_bps`, `fed_repo_rate_iorb_bps_sameday`, `fed_repo_submitted`, `fed_repo_submitted_sameday`. All 14 read the `repo_ops_inputs` snapshot through `fed_liquidity.py`; `srf_take_up*` reads `srf_inputs` and is identical in all three sources. Every other series is identical to 1e-9.

### Series that do not read `fed_repo_*` whose figure differs from the committed screen

Committed `screen.json` against the pre-#662 rebuild (same code and fixtures as main one commit before #662, so #662 is not the cause): `net_settlement`, `net_settlement_due_5d`, `ofr_dvp_minus_bgcr_bp_backfill`, `ofr_dvp_rate`.


## Series that do not read `fed_repo_*` and differ from the committed screen

Between the committed screen and the pre-#662 rebuild four series differ, none of which reads `fed_repo_*`, and #662 is not the cause (the pre-#662 rebuild is the same code as `main` before #662). They are:

| series | what differs | largest change in the pooled pressure correlation over leads | days at lead 1 |
|---|---|---|---|
| `ofr_dvp_minus_bgcr_bp_backfill` | the OFR real-time guard (#522, noted on the page): the column is now read from 2020-09-09 only | 0.087 | 1,778 to 1,246 |
| `ofr_dvp_rate` | the same guard | 0.028 | 1,778 to 1,246 |
| `net_settlement_due_5d` | construction fixes to the net settlement panel that post-date the screen (#620 and the drain fix of #618, `e6bcf5ba` and `5421c64b`, 11 and 12 October; the screen's evidence is from 10 October) | 0.084 | 1,873 |
| `net_settlement` | the same | 0.035 | 1,873 |

The attribution of the two net settlement changes is by commit dates and the files those commits touch; it was not bisected. The page's own note already records the OFR change (`ofr_dvp_minus_bgcr_bp_backfill` +0.105 to +0.185, `ofr_dvp_rate` +0.017 to -0.010 at lead 1). Table 1's order is unaffected by any of the four.

## Does re-running the unchanged code at the committed state reproduce the old numbers?

Yes. `git archive 6eee5eff` (the commit that published the screen) run with the page's commands gives a merged panel with sha256 `d1bb988fee5c…`, the page's recorded value, and a `screen.json` that is byte-identical to the committed one (`cmp`). So the committed figures are reproducible, and the differences above are the code and data changes named, not drift.

## Not checked

* No interval on the correlations (the screen draws none; the declaration of this record is unchanged), no paired test, no correction for the number of tests.
* The page's prose was not edited; where it would read differently (the inventory sentence on the `fed_repo_*` columns) the substance is unchanged.
* The 2026 days and the +10 bp threshold are not looked at.
