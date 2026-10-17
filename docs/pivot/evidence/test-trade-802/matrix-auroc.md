# Pressure AUROC (+5 bp) of the Fed repo take-up series on ordinary days, 90% stationary-bootstrap interval (#802)

Columns: `counted` is the tree before #743 (the $1-7 mn trades counted as take-up); `floor $0.1 bn` is #743's rule; `test trade` is this change (an operation is no take-up only if it is a whole-million trade of at most $7 mn). The first two columns are copied from `docs/pivot/evidence/fed-repo-floor-743/matrix-auroc.md`, which is not edited. Same panel chain, same scripts, same days (2018-06-29 to 2025-12-31).

| series | lead | split | counted | floor $0.1 bn | test trade |
|---|---|---|---|---|---|
| `fed_repo_days_since_positive` | 1 | pooled | 0.64 [0.48, 0.79] | 0.50 [0.35, 0.65] | 0.60 [0.42, 0.76] |
| `fed_repo_days_since_positive` | 1 | regime:2018-19 | 0.49 [0.40, 0.58] | 0.49 [0.40, 0.58] | 0.49 [0.40, 0.58] |
| `fed_repo_days_since_positive` | 1 | regime:2025-26 | 0.34 [0.25, 0.46] | 0.19 [0.10, 0.32] | 0.23 [0.13, 0.36] |
| `fed_repo_days_since_positive` | 3 | pooled | 0.65 [0.47, 0.79] | 0.52 [0.36, 0.65] | 0.61 [0.43, 0.77] |
| `fed_repo_days_since_positive` | 3 | regime:2018-19 | 0.51 [0.43, 0.59] | 0.51 [0.43, 0.59] | 0.51 [0.43, 0.59] |
| `fed_repo_days_since_positive` | 3 | regime:2025-26 | 0.27 [0.22, 0.32] | 0.16 [0.08, 0.26] | 0.17 [0.11, 0.28] |
| `fed_repo_days_since_positive` | 5 | pooled | 0.67 [0.51, 0.81] | 0.53 [0.37, 0.65] | 0.62 [0.44, 0.77] |
| `fed_repo_days_since_positive` | 5 | regime:2018-19 | 0.52 [0.42, 0.60] | 0.52 [0.42, 0.60] | 0.52 [0.42, 0.60] |
| `fed_repo_days_since_positive` | 5 | regime:2025-26 | 0.39 [0.28, 0.48] | 0.19 [0.11, 0.29] | 0.21 [0.12, 0.32] |
| `fed_repo_days_since_positive` | 10 | pooled | 0.68 [0.51, 0.82] | 0.54 [0.39, 0.67] | 0.64 [0.46, 0.79] |
| `fed_repo_days_since_positive` | 10 | regime:2018-19 | 0.53 [0.45, 0.61] | 0.53 [0.45, 0.61] | 0.53 [0.45, 0.61] |
| `fed_repo_days_since_positive` | 10 | regime:2025-26 | 0.29 [0.21, 0.37] | 0.16 [0.07, 0.24] | 0.18 [0.08, 0.27] |
| `fed_repo_days_since_positive_sameday` | 1 | pooled | 0.63 [0.46, 0.79] | 0.50 [0.34, 0.64] | 0.59 [0.41, 0.76] |
| `fed_repo_days_since_positive_sameday` | 1 | regime:2018-19 | 0.49 [0.40, 0.58] | 0.49 [0.40, 0.58] | 0.49 [0.40, 0.58] |
| `fed_repo_days_since_positive_sameday` | 1 | regime:2025-26 | 0.29 [0.22, 0.35] | 0.13 [0.06, 0.22] | 0.16 [0.08, 0.25] |
| `fed_repo_days_since_positive_sameday` | 3 | pooled | 0.65 [0.48, 0.79] | 0.51 [0.36, 0.64] | 0.61 [0.42, 0.76] |
| `fed_repo_days_since_positive_sameday` | 3 | regime:2018-19 | 0.50 [0.42, 0.58] | 0.50 [0.42, 0.58] | 0.50 [0.42, 0.58] |
| `fed_repo_days_since_positive_sameday` | 3 | regime:2025-26 | 0.32 [0.25, 0.41] | 0.17 [0.09, 0.29] | 0.20 [0.11, 0.31] |
| `fed_repo_days_since_positive_sameday` | 5 | pooled | 0.66 [0.48, 0.80] | 0.52 [0.36, 0.65] | 0.61 [0.42, 0.76] |
| `fed_repo_days_since_positive_sameday` | 5 | regime:2018-19 | 0.51 [0.41, 0.59] | 0.51 [0.41, 0.59] | 0.51 [0.41, 0.59] |
| `fed_repo_days_since_positive_sameday` | 5 | regime:2025-26 | 0.31 [0.23, 0.39] | 0.17 [0.09, 0.29] | 0.19 [0.11, 0.31] |
| `fed_repo_days_since_positive_sameday` | 10 | pooled | 0.67 [0.50, 0.82] | 0.53 [0.38, 0.66] | 0.63 [0.45, 0.78] |
| `fed_repo_days_since_positive_sameday` | 10 | regime:2018-19 | 0.52 [0.44, 0.61] | 0.52 [0.44, 0.61] | 0.52 [0.44, 0.61] |
| `fed_repo_days_since_positive_sameday` | 10 | regime:2025-26 | 0.33 [0.23, 0.43] | 0.16 [0.05, 0.25] | 0.20 [0.08, 0.31] |
| `fed_repo_log_accepted` | 1 | pooled | 0.53 [0.43, 0.65] | 0.58 [0.50, 0.67] | 0.57 [0.49, 0.67] |
| `fed_repo_log_accepted` | 1 | regime:2018-19 | 0.51 [0.42, 0.60] | 0.51 [0.42, 0.60] | 0.51 [0.42, 0.60] |
| `fed_repo_log_accepted` | 1 | regime:2025-26 | 0.69 [0.55, 0.80] | 0.68 [0.55, 0.77] | 0.67 [0.53, 0.76] |
| `fed_repo_log_accepted` | 3 | pooled | 0.53 [0.44, 0.66] | 0.56 [0.49, 0.65] | 0.56 [0.48, 0.65] |
| `fed_repo_log_accepted` | 3 | regime:2018-19 | 0.49 [0.41, 0.57] | 0.49 [0.41, 0.57] | 0.49 [0.41, 0.57] |
| `fed_repo_log_accepted` | 3 | regime:2025-26 | 0.78 [0.69, 0.85] | 0.67 [0.47, 0.80] | 0.69 [0.54, 0.80] |
| `fed_repo_log_accepted` | 5 | pooled | 0.51 [0.42, 0.61] | 0.55 [0.48, 0.64] | 0.56 [0.48, 0.65] |
| `fed_repo_log_accepted` | 5 | regime:2018-19 | 0.48 [0.40, 0.57] | 0.48 [0.40, 0.57] | 0.48 [0.40, 0.57] |
| `fed_repo_log_accepted` | 5 | regime:2025-26 | 0.67 [0.56, 0.81] | 0.67 [0.51, 0.76] | 0.71 [0.57, 0.83] |
| `fed_repo_log_accepted` | 10 | pooled | 0.51 [0.42, 0.62] | 0.54 [0.48, 0.62] | 0.54 [0.48, 0.63] |
| `fed_repo_log_accepted` | 10 | regime:2018-19 | 0.46 [0.38, 0.54] | 0.46 [0.38, 0.54] | 0.46 [0.38, 0.54] |
| `fed_repo_log_accepted` | 10 | regime:2025-26 | 0.75 [0.65, 0.92] | 0.65 [0.55, 0.83] | 0.69 [0.61, 0.89] |
| `fed_repo_ops` | 1 | pooled | 0.52 [0.42, 0.62] | 0.57 [0.49, 0.66] | 0.57 [0.49, 0.66] |
| `fed_repo_ops` | 1 | regime:2018-19 | 0.51 [0.42, 0.60] | 0.51 [0.42, 0.60] | 0.51 [0.42, 0.60] |
| `fed_repo_ops` | 1 | regime:2025-26 | 0.65 [0.53, 0.75] | 0.67 [0.55, 0.76] | 0.65 [0.52, 0.75] |
| `fed_repo_ops` | 3 | pooled | 0.52 [0.43, 0.64] | 0.56 [0.48, 0.64] | 0.55 [0.48, 0.64] |
| `fed_repo_ops` | 3 | regime:2018-19 | 0.49 [0.41, 0.57] | 0.49 [0.41, 0.57] | 0.49 [0.41, 0.57] |
| `fed_repo_ops` | 3 | regime:2025-26 | 0.71 [0.65, 0.77] | 0.65 [0.46, 0.78] | 0.68 [0.54, 0.77] |
| `fed_repo_ops` | 5 | pooled | 0.50 [0.42, 0.60] | 0.55 [0.48, 0.63] | 0.56 [0.48, 0.65] |
| `fed_repo_ops` | 5 | regime:2018-19 | 0.48 [0.40, 0.58] | 0.48 [0.40, 0.58] | 0.48 [0.40, 0.58] |
| `fed_repo_ops` | 5 | regime:2025-26 | 0.63 [0.50, 0.81] | 0.67 [0.52, 0.77] | 0.72 [0.57, 0.86] |
| `fed_repo_ops` | 10 | pooled | 0.49 [0.41, 0.60] | 0.54 [0.48, 0.62] | 0.54 [0.48, 0.63] |
| `fed_repo_ops` | 10 | regime:2018-19 | 0.47 [0.38, 0.54] | 0.47 [0.38, 0.54] | 0.47 [0.38, 0.54] |
| `fed_repo_ops` | 10 | regime:2025-26 | 0.68 [0.60, 0.80] | 0.64 [0.55, 0.81] | 0.68 [0.60, 0.87] |
| `fed_repo_rate_iorb_bps` | 1 | pooled | 0.50 [0.41, 0.59] | 0.56 [0.48, 0.64] | 0.55 [0.48, 0.64] |
| `fed_repo_rate_iorb_bps` | 1 | regime:2018-19 | 0.52 [0.44, 0.60] | 0.52 [0.44, 0.60] | 0.52 [0.44, 0.60] |
| `fed_repo_rate_iorb_bps` | 1 | regime:2025-26 | 0.71 [0.56, 0.86] | 0.68 [0.56, 0.77] | 0.66 [0.54, 0.75] |
| `fed_repo_rate_iorb_bps` | 3 | pooled | 0.54 [0.45, 0.66] | 0.59 [0.52, 0.68] | 0.58 [0.51, 0.67] |
| `fed_repo_rate_iorb_bps` | 3 | regime:2018-19 | 0.51 [0.43, 0.59] | 0.51 [0.43, 0.59] | 0.51 [0.43, 0.59] |
| `fed_repo_rate_iorb_bps` | 3 | regime:2025-26 | 0.78 [0.68, 0.97] | 0.66 [0.47, 0.79] | 0.68 [0.55, 0.78] |
| `fed_repo_rate_iorb_bps` | 5 | pooled | 0.50 [0.43, 0.59] | 0.57 [0.51, 0.65] | 0.58 [0.51, 0.66] |
| `fed_repo_rate_iorb_bps` | 5 | regime:2018-19 | 0.50 [0.42, 0.59] | 0.50 [0.42, 0.59] | 0.50 [0.42, 0.59] |
| `fed_repo_rate_iorb_bps` | 5 | regime:2025-26 | 0.64 [0.50, 0.84] | 0.67 [0.53, 0.77] | 0.72 [0.58, 0.87] |
| `fed_repo_rate_iorb_bps` | 10 | pooled | 0.50 [0.41, 0.60] | 0.55 [0.48, 0.62] | 0.55 [0.49, 0.63] |
| `fed_repo_rate_iorb_bps` | 10 | regime:2018-19 | 0.49 [0.42, 0.57] | 0.49 [0.42, 0.57] | 0.49 [0.42, 0.57] |
| `fed_repo_rate_iorb_bps` | 10 | regime:2025-26 | 0.72 [0.60, 0.92] | 0.64 [0.55, 0.81] | 0.69 [0.60, 0.87] |
