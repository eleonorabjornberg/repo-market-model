# Before and after #662: the source matrix on ordinary days (#692, of #629)

Scratch evidence for the re-run of `docs/pivot/source-matrix-ordinary-days-result.md` after PR #662 (#659) corrected the Fed repo take-up columns (the six test operations before 2019-09-17 are no longer counted;
`fed_repo_days_since_positive` no longer restarts at each test; the change is confined to panel rows 2018-05 to 2019-09-16). The published page and evidence are not edited; the re-run is in this folder
(`source_matrix.json`, `tables.md`, `matrix_*.csv`, `matrices.json`, the two heatmaps). Development days only (2018-06-29 to 2025-12-31); no 2026 day is read. Everything remains exploratory and uncorrected for the number of tests;
the intervals are the record's own 90% stationary bootstrap (AUROC and the pre-onset contrast), and the record draws none for a Spearman correlation.

Three sources are set side by side in every table:

* **committed**: the figure in the published evidence (`docs/pivot/evidence/source-matrix/`), as published and not edited.
* **pre-#662 rebuild**: the same scripts and fixtures as `main` one commit before #662 (`8cd170fe~1`), exported with `git archive` and run with the page's commands unchanged. Against the re-run it differs in the Fed repo columns and nothing else, so it isolates #662. It is not a published record.
* **re-run**: the page's commands unchanged, on `main` as of this branch (`ee9366eb`), with the corrected `fed_repo_*` columns.

Scratch panels are the page's own chain run on the published panel `4ddc3882…` (`verify-panel` clean). Merged scratch panel with the satiation columns (`SCREEN2.csv`) sha256: committed `8299bac3…` (reproduced exactly, see below); pre-#662 rebuild `84d00907…`; re-run `a6f14260…`. `scripts/source_matrix_629.py` refuses any panel whose sha256 is not the declared `8299bac3…`; for the two rebuilt panels it was run through a scratch wrapper (not committed) that substitutes the rebuilt panel's own sha256 for that one comparison and changes nothing else, so `scope.panel_sha256` in the re-run `source_matrix.json` is `a6f14260…`. The declaration (`metadata/source_matrix_629.json`) is untouched. The `AUG2D.csv` input is the page's `scripts/satiation_distance_598.py panel` step on `AUG2.csv` (its docstring).

## Result in short

* **Only the 14 `fed_repo_*` series change** (every cell of `source_matrix.json`, tolerance 1e-9, pre-#662 rebuild against re-run). `incremental` is unchanged (no `fed_repo_*` series is among its top series), and so is every pair with no `fed_repo_*` member. `srf_take_up` and `srf_take_up_positive` read `srf_inputs` and are unchanged.
* **`fed_repo_days_since_positive` is the only series with a visible move; the rest of the family moves little.** Pressure AUROC on ordinary days, lead 1: 0.58 [0.43, 0.72] to 0.64 [0.48, 0.79]; lead 10: 0.61 [0.45, 0.75] to 0.68 [0.51, 0.82] (`_sameday` the same within 0.01). The lead-1 to lead-3 intervals still contain 0.5; at leads 5 and 10 the lower bound is 0.51, one or two cells of the 505 series-by-lead cells the record tests, uncorrected, so this is what chance gives as readily as a signal. The column counts days since the facility last took anything, so it rises with time through the era, as the era indicators do. Its Spearman with the spread level goes from +0.126 to +0.210 at lead 1; the pre-onset AUC from 0.48 [0.28, 0.70] to 0.59 [0.30, 0.88] (std. diff -0.11 [-0.55, +0.51] to +0.94 [-0.14, +2.06]), both intervals containing no difference. In the 2018-19 split (62 of the 82 ordinary-day pressure days, where the changed rows are) it goes from 0.51 [0.38, 0.65] to 0.49 [0.40, 0.58]. The other 13 series change by at most 0.02 in AUROC at lead 1 pooled.
* **No grouping or ranking moved.** The groups of redundant series (|rho| >= 0.8) are identical, on ordinary days and on all days, in all three sources. No `fed_repo_*` series is in Table 2's top 25 in any source, and Table 2 is the same 25 in the same order between the pre-#662 rebuild and the re-run. The page's conclusions (sections 1 to 3 and the due-diligence table) do not name a `fed_repo_*` series as a signal, and none of them changes. `srf_take_up` still groups with `fed_repo_submitted` and its family.
* **Table 2 differs in order between the committed record and the re-run, for reasons that are not #662** (see the last section).

## Tables

### AUROC for a pressure day (+5 bp), ordinary days, 90% stationary-bootstrap interval, pooled, by lead

| series | source | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 |
|---|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#629) | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.54 [0.44, 0.66] | 0.51 [0.43, 0.62] | 0.51 [0.42, 0.62] |
| `fed_repo_accepted` | pre-#662 rebuild | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.54 [0.44, 0.66] | 0.51 [0.43, 0.62] | 0.51 [0.42, 0.62] |
| `fed_repo_accepted` | re-run | 0.53 [0.43, 0.65] | 0.53 [0.43, 0.64] | 0.53 [0.44, 0.66] | 0.51 [0.42, 0.61] | 0.51 [0.42, 0.62] |
| `fed_repo_accepted_sameday` | committed (#629) | 0.57 [0.47, 0.69] | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.52 [0.43, 0.64] |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | 0.57 [0.47, 0.69] | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.52 [0.43, 0.64] |
| `fed_repo_accepted_sameday` | re-run | 0.55 [0.44, 0.68] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.53 [0.43, 0.65] | 0.51 [0.42, 0.63] |
| `fed_repo_days_since_positive` | committed (#629) | 0.58 [0.43, 0.72] | 0.59 [0.44, 0.73] | 0.59 [0.43, 0.72] | 0.60 [0.45, 0.73] | 0.61 [0.45, 0.75] |
| `fed_repo_days_since_positive` | pre-#662 rebuild | 0.58 [0.43, 0.72] | 0.59 [0.44, 0.73] | 0.59 [0.43, 0.72] | 0.60 [0.45, 0.73] | 0.61 [0.45, 0.75] |
| `fed_repo_days_since_positive` | re-run | 0.64 [0.48, 0.79] | 0.65 [0.49, 0.79] | 0.65 [0.47, 0.79] | 0.67 [0.51, 0.81] | 0.68 [0.51, 0.82] |
| `fed_repo_days_since_positive_sameday` | committed (#629) | 0.55 [0.40, 0.69] | 0.58 [0.43, 0.72] | 0.59 [0.43, 0.71] | 0.60 [0.44, 0.72] | 0.61 [0.45, 0.74] |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | 0.55 [0.40, 0.69] | 0.58 [0.43, 0.72] | 0.59 [0.43, 0.71] | 0.60 [0.44, 0.72] | 0.61 [0.45, 0.74] |
| `fed_repo_days_since_positive_sameday` | re-run | 0.63 [0.46, 0.79] | 0.64 [0.48, 0.79] | 0.65 [0.48, 0.79] | 0.66 [0.48, 0.80] | 0.67 [0.50, 0.82] |
| `fed_repo_log_accepted` | committed (#629) | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.54 [0.44, 0.66] | 0.51 [0.43, 0.62] | 0.51 [0.42, 0.62] |
| `fed_repo_log_accepted` | pre-#662 rebuild | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.54 [0.44, 0.66] | 0.51 [0.43, 0.62] | 0.51 [0.42, 0.62] |
| `fed_repo_log_accepted` | re-run | 0.53 [0.43, 0.65] | 0.53 [0.43, 0.64] | 0.53 [0.44, 0.66] | 0.51 [0.42, 0.61] | 0.51 [0.42, 0.62] |
| `fed_repo_log_accepted_change` | committed (#629) | 0.52 [0.48, 0.55] | 0.52 [0.48, 0.55] | 0.49 [0.44, 0.53] | 0.49 [0.45, 0.53] | 0.49 [0.45, 0.54] |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | 0.52 [0.48, 0.55] | 0.52 [0.48, 0.55] | 0.49 [0.44, 0.53] | 0.49 [0.45, 0.53] | 0.49 [0.45, 0.54] |
| `fed_repo_log_accepted_change` | re-run | 0.52 [0.48, 0.55] | 0.52 [0.48, 0.55] | 0.48 [0.44, 0.52] | 0.49 [0.45, 0.53] | 0.50 [0.46, 0.54] |
| `fed_repo_log_accepted_change_sameday` | committed (#629) | 0.55 [0.51, 0.59] | 0.52 [0.48, 0.55] | 0.52 [0.48, 0.55] | 0.53 [0.48, 0.58] | 0.51 [0.46, 0.55] |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | 0.55 [0.51, 0.59] | 0.52 [0.48, 0.55] | 0.52 [0.48, 0.55] | 0.53 [0.48, 0.58] | 0.51 [0.46, 0.55] |
| `fed_repo_log_accepted_change_sameday` | re-run | 0.54 [0.50, 0.58] | 0.52 [0.49, 0.55] | 0.52 [0.48, 0.55] | 0.53 [0.49, 0.58] | 0.50 [0.45, 0.54] |
| `fed_repo_log_accepted_sameday` | committed (#629) | 0.57 [0.47, 0.69] | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.52 [0.43, 0.64] |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | 0.57 [0.47, 0.69] | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.52 [0.43, 0.64] |
| `fed_repo_log_accepted_sameday` | re-run | 0.55 [0.44, 0.68] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.53 [0.43, 0.65] | 0.51 [0.42, 0.63] |
| `fed_repo_ops` | committed (#629) | 0.52 [0.43, 0.63] | 0.52 [0.43, 0.62] | 0.52 [0.44, 0.64] | 0.50 [0.42, 0.60] | 0.49 [0.41, 0.60] |
| `fed_repo_ops` | pre-#662 rebuild | 0.52 [0.43, 0.63] | 0.52 [0.43, 0.62] | 0.52 [0.44, 0.64] | 0.50 [0.42, 0.60] | 0.49 [0.41, 0.60] |
| `fed_repo_ops` | re-run | 0.52 [0.42, 0.62] | 0.51 [0.42, 0.62] | 0.52 [0.43, 0.64] | 0.50 [0.42, 0.60] | 0.49 [0.41, 0.60] |
| `fed_repo_ops_sameday` | committed (#629) | 0.55 [0.45, 0.66] | 0.52 [0.44, 0.63] | 0.52 [0.43, 0.63] | 0.52 [0.42, 0.63] | 0.50 [0.42, 0.61] |
| `fed_repo_ops_sameday` | pre-#662 rebuild | 0.55 [0.45, 0.66] | 0.52 [0.44, 0.63] | 0.52 [0.43, 0.63] | 0.52 [0.42, 0.63] | 0.50 [0.42, 0.61] |
| `fed_repo_ops_sameday` | re-run | 0.53 [0.44, 0.65] | 0.52 [0.43, 0.62] | 0.52 [0.43, 0.63] | 0.52 [0.42, 0.63] | 0.50 [0.42, 0.61] |
| `fed_repo_rate_iorb_bps` | committed (#629) | 0.50 [0.42, 0.60] | 0.52 [0.44, 0.62] | 0.54 [0.46, 0.66] | 0.51 [0.44, 0.59] | 0.50 [0.41, 0.60] |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | 0.50 [0.42, 0.60] | 0.52 [0.44, 0.62] | 0.54 [0.46, 0.66] | 0.51 [0.44, 0.59] | 0.50 [0.41, 0.60] |
| `fed_repo_rate_iorb_bps` | re-run | 0.50 [0.41, 0.59] | 0.52 [0.43, 0.61] | 0.54 [0.45, 0.66] | 0.50 [0.43, 0.59] | 0.50 [0.41, 0.60] |
| `fed_repo_rate_iorb_bps_sameday` | committed (#629) | 0.51 [0.42, 0.60] | 0.52 [0.44, 0.62] | 0.55 [0.46, 0.66] | 0.51 [0.44, 0.59] | 0.50 [0.41, 0.60] |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | 0.51 [0.42, 0.60] | 0.52 [0.44, 0.62] | 0.55 [0.46, 0.66] | 0.51 [0.44, 0.59] | 0.50 [0.41, 0.60] |
| `fed_repo_rate_iorb_bps_sameday` | re-run | 0.50 [0.41, 0.59] | 0.52 [0.43, 0.61] | 0.54 [0.46, 0.66] | 0.50 [0.43, 0.59] | 0.50 [0.41, 0.60] |
| `fed_repo_submitted` | committed (#629) | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.54 [0.45, 0.66] | 0.51 [0.43, 0.62] | 0.51 [0.42, 0.62] |
| `fed_repo_submitted` | pre-#662 rebuild | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.54 [0.45, 0.66] | 0.51 [0.43, 0.62] | 0.51 [0.42, 0.62] |
| `fed_repo_submitted` | re-run | 0.53 [0.43, 0.65] | 0.53 [0.43, 0.64] | 0.54 [0.44, 0.66] | 0.51 [0.42, 0.61] | 0.51 [0.42, 0.62] |
| `fed_repo_submitted_sameday` | committed (#629) | 0.57 [0.47, 0.69] | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.52 [0.43, 0.64] |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | 0.57 [0.47, 0.69] | 0.54 [0.44, 0.65] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.52 [0.43, 0.64] |
| `fed_repo_submitted_sameday` | re-run | 0.55 [0.44, 0.68] | 0.53 [0.44, 0.65] | 0.53 [0.43, 0.65] | 0.53 [0.43, 0.65] | 0.51 [0.42, 0.63] |
| `srf_take_up` | committed (#629) | 0.74 [0.59, 0.84] | 0.76 [0.57, 0.84] | 0.85 [0.80, 0.90] | 0.76 [0.67, 0.89] | 0.84 [0.78, 0.98] |
| `srf_take_up` | pre-#662 rebuild | 0.74 [0.59, 0.84] | 0.76 [0.57, 0.84] | 0.85 [0.80, 0.90] | 0.76 [0.67, 0.89] | 0.84 [0.78, 0.98] |
| `srf_take_up` | re-run | 0.74 [0.59, 0.84] | 0.76 [0.57, 0.84] | 0.85 [0.80, 0.90] | 0.76 [0.67, 0.89] | 0.84 [0.78, 0.98] |
| `srf_take_up_positive` | committed (#629) | 0.47 [0.41, 0.55] | 0.47 [0.41, 0.56] | 0.49 [0.41, 0.59] | 0.47 [0.41, 0.54] | 0.49 [0.42, 0.57] |
| `srf_take_up_positive` | pre-#662 rebuild | 0.47 [0.41, 0.55] | 0.47 [0.41, 0.56] | 0.49 [0.41, 0.59] | 0.47 [0.41, 0.54] | 0.49 [0.42, 0.57] |
| `srf_take_up_positive` | re-run | 0.47 [0.41, 0.55] | 0.47 [0.41, 0.56] | 0.49 [0.41, 0.59] | 0.47 [0.41, 0.54] | 0.49 [0.42, 0.57] |

### AUROC at lead 1 in the splits that contain the changed rows (2018-19 holds 62 of the 82 ordinary-day pressure days; the scarce state holds 80)

| series | source | 2018-19 | scarce | 2020 | 2025-26 |
|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#629) | 0.51 [0.42, 0.61] | 0.47 [0.38, 0.57] | 0.91 [0.80, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_accepted` | pre-#662 rebuild | 0.51 [0.42, 0.61] | 0.47 [0.38, 0.57] | 0.91 [0.80, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_accepted` | re-run | 0.51 [0.42, 0.60] | 0.46 [0.38, 0.57] | 0.91 [0.80, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_accepted_sameday` | committed (#629) | 0.53 [0.44, 0.62] | 0.49 [0.40, 0.60] | 0.98 [0.96, 0.99] | 0.82 [0.74, 0.97] |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | 0.53 [0.44, 0.62] | 0.49 [0.40, 0.60] | 0.98 [0.96, 0.99] | 0.82 [0.74, 0.97] |
| `fed_repo_accepted_sameday` | re-run | 0.51 [0.42, 0.60] | 0.48 [0.39, 0.59] | 0.98 [0.96, 0.99] | 0.82 [0.74, 0.97] |
| `fed_repo_days_since_positive` | committed (#629) | 0.51 [0.38, 0.65] | 0.53 [0.40, 0.65] | 0.25 [0.16, 0.37] | 0.34 [0.25, 0.46] |
| `fed_repo_days_since_positive` | pre-#662 rebuild | 0.51 [0.38, 0.65] | 0.53 [0.40, 0.65] | 0.25 [0.16, 0.37] | 0.34 [0.25, 0.46] |
| `fed_repo_days_since_positive` | re-run | 0.49 [0.40, 0.58] | 0.53 [0.42, 0.62] | 0.25 [0.16, 0.37] | 0.34 [0.25, 0.46] |
| `fed_repo_days_since_positive_sameday` | committed (#629) | 0.48 [0.34, 0.62] | 0.51 [0.37, 0.63] | 0.25 [0.15, 0.37] | 0.29 [0.22, 0.35] |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | 0.48 [0.34, 0.62] | 0.51 [0.37, 0.63] | 0.25 [0.15, 0.37] | 0.29 [0.22, 0.35] |
| `fed_repo_days_since_positive_sameday` | re-run | 0.49 [0.40, 0.58] | 0.52 [0.41, 0.62] | 0.25 [0.15, 0.37] | 0.29 [0.22, 0.35] |
| `fed_repo_log_accepted` | committed (#629) | 0.51 [0.42, 0.61] | 0.47 [0.38, 0.57] | 0.91 [0.80, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_log_accepted` | pre-#662 rebuild | 0.51 [0.42, 0.61] | 0.47 [0.38, 0.57] | 0.91 [0.80, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_log_accepted` | re-run | 0.51 [0.42, 0.60] | 0.46 [0.38, 0.57] | 0.91 [0.80, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_log_accepted_change` | committed (#629) | 0.52 [0.49, 0.56] | 0.53 [0.50, 0.56] | 0.60 [0.28, 0.95] | 0.52 [0.41, 0.64] |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | 0.52 [0.49, 0.56] | 0.53 [0.50, 0.56] | 0.60 [0.28, 0.95] | 0.52 [0.41, 0.64] |
| `fed_repo_log_accepted_change` | re-run | 0.52 [0.49, 0.55] | 0.53 [0.50, 0.56] | 0.60 [0.28, 0.95] | 0.52 [0.41, 0.64] |
| `fed_repo_log_accepted_change_sameday` | committed (#629) | 0.53 [0.50, 0.55] | 0.56 [0.52, 0.61] | 0.69 [0.54, 0.98] | 0.67 [0.56, 0.87] |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | 0.53 [0.50, 0.55] | 0.56 [0.52, 0.61] | 0.69 [0.54, 0.98] | 0.67 [0.56, 0.87] |
| `fed_repo_log_accepted_change_sameday` | re-run | 0.51 [0.50, 0.53] | 0.55 [0.51, 0.60] | 0.69 [0.54, 0.98] | 0.67 [0.56, 0.87] |
| `fed_repo_log_accepted_sameday` | committed (#629) | 0.53 [0.44, 0.62] | 0.49 [0.40, 0.60] | 0.98 [0.96, 0.99] | 0.82 [0.74, 0.97] |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | 0.53 [0.44, 0.62] | 0.49 [0.40, 0.60] | 0.98 [0.96, 0.99] | 0.82 [0.74, 0.97] |
| `fed_repo_log_accepted_sameday` | re-run | 0.51 [0.42, 0.60] | 0.48 [0.39, 0.59] | 0.98 [0.96, 0.99] | 0.82 [0.74, 0.97] |
| `fed_repo_ops` | committed (#629) | 0.51 [0.42, 0.61] | 0.46 [0.38, 0.57] | 0.83 [0.61, 0.96] | 0.65 [0.53, 0.75] |
| `fed_repo_ops` | pre-#662 rebuild | 0.51 [0.42, 0.61] | 0.46 [0.38, 0.57] | 0.83 [0.61, 0.96] | 0.65 [0.53, 0.75] |
| `fed_repo_ops` | re-run | 0.51 [0.42, 0.60] | 0.46 [0.38, 0.56] | 0.83 [0.61, 0.96] | 0.65 [0.53, 0.75] |
| `fed_repo_ops_sameday` | committed (#629) | 0.52 [0.43, 0.62] | 0.49 [0.39, 0.60] | 0.83 [0.71, 0.96] | 0.73 [0.65, 0.82] |
| `fed_repo_ops_sameday` | pre-#662 rebuild | 0.52 [0.43, 0.62] | 0.49 [0.39, 0.60] | 0.83 [0.71, 0.96] | 0.73 [0.65, 0.82] |
| `fed_repo_ops_sameday` | re-run | 0.50 [0.42, 0.59] | 0.47 [0.38, 0.58] | 0.83 [0.71, 0.96] | 0.73 [0.65, 0.82] |
| `fed_repo_rate_iorb_bps` | committed (#629) | 0.52 [0.44, 0.60] | 0.52 [0.43, 0.61] | 0.14 [0.00, 0.45] | 0.71 [0.56, 0.86] |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | 0.52 [0.44, 0.60] | 0.52 [0.43, 0.61] | 0.14 [0.00, 0.45] | 0.71 [0.56, 0.86] |
| `fed_repo_rate_iorb_bps` | re-run | 0.52 [0.44, 0.60] | 0.52 [0.43, 0.60] | 0.14 [0.00, 0.45] | 0.71 [0.56, 0.86] |
| `fed_repo_rate_iorb_bps_sameday` | committed (#629) | 0.52 [0.44, 0.60] | 0.52 [0.43, 0.61] | 0.14 [0.00, 0.45] | 0.71 [0.56, 0.86] |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | 0.52 [0.44, 0.60] | 0.52 [0.43, 0.61] | 0.14 [0.00, 0.45] | 0.71 [0.56, 0.86] |
| `fed_repo_rate_iorb_bps_sameday` | re-run | 0.52 [0.44, 0.60] | 0.52 [0.43, 0.60] | 0.14 [0.00, 0.45] | 0.71 [0.56, 0.86] |
| `fed_repo_submitted` | committed (#629) | 0.51 [0.42, 0.61] | 0.47 [0.38, 0.57] | 0.91 [0.79, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_submitted` | pre-#662 rebuild | 0.51 [0.42, 0.61] | 0.47 [0.38, 0.57] | 0.91 [0.79, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_submitted` | re-run | 0.51 [0.42, 0.60] | 0.46 [0.37, 0.57] | 0.91 [0.79, 0.97] | 0.69 [0.55, 0.80] |
| `fed_repo_submitted_sameday` | committed (#629) | 0.53 [0.44, 0.62] | 0.49 [0.40, 0.61] | 0.98 [0.96, 1.00] | 0.82 [0.74, 0.97] |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | 0.53 [0.44, 0.62] | 0.49 [0.40, 0.61] | 0.98 [0.96, 1.00] | 0.82 [0.74, 0.97] |
| `fed_repo_submitted_sameday` | re-run | 0.51 [0.42, 0.60] | 0.48 [0.39, 0.59] | 0.98 [0.96, 1.00] | 0.82 [0.74, 0.97] |
| `srf_take_up` | committed (#629) | - | 0.49 [0.31, 0.67] | - | 0.69 [0.55, 0.80] |
| `srf_take_up` | pre-#662 rebuild | - | 0.49 [0.31, 0.67] | - | 0.69 [0.55, 0.80] |
| `srf_take_up` | re-run | - | 0.49 [0.31, 0.67] | - | 0.69 [0.55, 0.80] |
| `srf_take_up_positive` | committed (#629) | 0.50 [0.50, 0.50] | 0.53 [0.48, 0.59] | 0.50 [0.50, 0.50] | 0.63 [0.52, 0.73] |
| `srf_take_up_positive` | pre-#662 rebuild | 0.50 [0.50, 0.50] | 0.53 [0.48, 0.59] | 0.50 [0.50, 0.50] | 0.63 [0.52, 0.73] |
| `srf_take_up_positive` | re-run | 0.50 [0.50, 0.50] | 0.53 [0.48, 0.59] | 0.50 [0.50, 0.50] | 0.63 [0.52, 0.73] |

### Spearman correlation with the +5 bp pressure indicator, ordinary days pooled (no interval is drawn for a correlation in this record)

| series | source | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | rank (max abs over leads) |
|---|---|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#629) | +0.038 | +0.033 | +0.039 | +0.014 | +0.006 | 76 of 96 |
| `fed_repo_accepted` | pre-#662 rebuild | +0.038 | +0.033 | +0.039 | +0.014 | +0.006 | 76 of 96 |
| `fed_repo_accepted` | re-run | +0.032 | +0.028 | +0.033 | +0.009 | +0.007 | 77 of 96 |
| `fed_repo_accepted_sameday` | committed (#629) | +0.071 | +0.038 | +0.034 | +0.025 | +0.018 | 59 of 96 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | +0.071 | +0.038 | +0.034 | +0.025 | +0.018 | 59 of 96 |
| `fed_repo_accepted_sameday` | re-run | +0.052 | +0.032 | +0.028 | +0.026 | +0.012 | 65 of 96 |
| `fed_repo_days_since_positive` | committed (#629) | +0.065 | +0.071 | +0.073 | +0.085 | +0.092 | 45 of 96 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | +0.065 | +0.071 | +0.073 | +0.085 | +0.092 | 45 of 96 |
| `fed_repo_days_since_positive` | re-run | +0.116 | +0.121 | +0.124 | +0.140 | +0.147 | 35 of 96 |
| `fed_repo_days_since_positive_sameday` | committed (#629) | +0.041 | +0.065 | +0.071 | +0.078 | +0.087 | 47 of 96 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | +0.041 | +0.065 | +0.071 | +0.078 | +0.087 | 47 of 96 |
| `fed_repo_days_since_positive_sameday` | re-run | +0.109 | +0.116 | +0.121 | +0.129 | +0.142 | 36 of 96 |
| `fed_repo_log_accepted` | committed (#629) | +0.038 | +0.033 | +0.039 | +0.014 | +0.006 | 77 of 96 |
| `fed_repo_log_accepted` | pre-#662 rebuild | +0.038 | +0.033 | +0.039 | +0.014 | +0.006 | 77 of 96 |
| `fed_repo_log_accepted` | re-run | +0.032 | +0.028 | +0.033 | +0.009 | +0.007 | 78 of 96 |
| `fed_repo_log_accepted_change` | committed (#629) | +0.014 | +0.014 | -0.011 | -0.009 | -0.007 | 93 of 96 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | +0.014 | +0.014 | -0.011 | -0.009 | -0.007 | 93 of 96 |
| `fed_repo_log_accepted_change` | re-run | +0.014 | +0.014 | -0.016 | -0.009 | -0.003 | 92 of 96 |
| `fed_repo_log_accepted_change_sameday` | committed (#629) | +0.045 | +0.014 | +0.014 | +0.025 | +0.006 | 69 of 96 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | +0.045 | +0.014 | +0.014 | +0.025 | +0.006 | 69 of 96 |
| `fed_repo_log_accepted_change_sameday` | re-run | +0.036 | +0.014 | +0.014 | +0.030 | +0.001 | 74 of 96 |
| `fed_repo_log_accepted_sameday` | committed (#629) | +0.071 | +0.038 | +0.034 | +0.025 | +0.018 | 60 of 96 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | +0.071 | +0.038 | +0.034 | +0.025 | +0.018 | 60 of 96 |
| `fed_repo_log_accepted_sameday` | re-run | +0.052 | +0.032 | +0.028 | +0.026 | +0.012 | 66 of 96 |
| `fed_repo_ops` | committed (#629) | +0.023 | +0.019 | +0.024 | +0.002 | -0.007 | 81 of 96 |
| `fed_repo_ops` | pre-#662 rebuild | +0.023 | +0.019 | +0.024 | +0.002 | -0.007 | 81 of 96 |
| `fed_repo_ops` | re-run | +0.018 | +0.014 | +0.019 | -0.003 | -0.006 | 87 of 96 |
| `fed_repo_ops_sameday` | committed (#629) | +0.050 | +0.024 | +0.019 | +0.016 | +0.005 | 67 of 96 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | +0.050 | +0.024 | +0.019 | +0.016 | +0.005 | 67 of 96 |
| `fed_repo_ops_sameday` | re-run | +0.034 | +0.019 | +0.015 | +0.017 | -0.000 | 75 of 96 |
| `fed_repo_rate_iorb_bps` | committed (#629) | +0.005 | +0.021 | +0.045 | +0.007 | -0.004 | 70 of 96 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | +0.005 | +0.021 | +0.045 | +0.007 | -0.004 | 70 of 96 |
| `fed_repo_rate_iorb_bps` | re-run | +0.000 | +0.017 | +0.041 | +0.003 | -0.003 | 71 of 96 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#629) | +0.005 | +0.021 | +0.046 | +0.007 | -0.003 | 68 of 96 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | +0.005 | +0.021 | +0.046 | +0.007 | -0.003 | 68 of 96 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | +0.001 | +0.017 | +0.042 | +0.003 | -0.002 | 70 of 96 |
| `fed_repo_submitted` | committed (#629) | +0.038 | +0.033 | +0.039 | +0.014 | +0.006 | 75 of 96 |
| `fed_repo_submitted` | pre-#662 rebuild | +0.038 | +0.033 | +0.039 | +0.014 | +0.006 | 75 of 96 |
| `fed_repo_submitted` | re-run | +0.032 | +0.028 | +0.034 | +0.008 | +0.007 | 76 of 96 |
| `fed_repo_submitted_sameday` | committed (#629) | +0.071 | +0.038 | +0.033 | +0.025 | +0.018 | 58 of 96 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | +0.071 | +0.038 | +0.033 | +0.025 | +0.018 | 58 of 96 |
| `fed_repo_submitted_sameday` | re-run | +0.052 | +0.032 | +0.028 | +0.026 | +0.012 | 64 of 96 |
| `srf_take_up` | committed (#629) | +0.133 | +0.148 | +0.195 | +0.145 | +0.191 | 25 of 96 |
| `srf_take_up` | pre-#662 rebuild | +0.133 | +0.148 | +0.195 | +0.145 | +0.191 | 25 of 96 |
| `srf_take_up` | re-run | +0.133 | +0.148 | +0.195 | +0.145 | +0.191 | 25 of 96 |
| `srf_take_up_positive` | committed (#629) | -0.037 | -0.031 | -0.012 | -0.039 | -0.015 | 74 of 96 |
| `srf_take_up_positive` | pre-#662 rebuild | -0.037 | -0.031 | -0.012 | -0.039 | -0.015 | 74 of 96 |
| `srf_take_up_positive` | re-run | -0.037 | -0.031 | -0.012 | -0.039 | -0.015 | 72 of 96 |

### Spearman correlation with the spread level, ordinary days pooled (no interval is drawn for a correlation in this record)

| series | source | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 |
|---|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#629) | +0.144 | +0.158 | +0.156 | +0.156 | +0.148 |
| `fed_repo_accepted` | pre-#662 rebuild | +0.144 | +0.158 | +0.156 | +0.156 | +0.148 |
| `fed_repo_accepted` | re-run | +0.136 | +0.149 | +0.148 | +0.148 | +0.142 |
| `fed_repo_accepted_sameday` | committed (#629) | +0.161 | +0.145 | +0.158 | +0.153 | +0.147 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | +0.161 | +0.145 | +0.158 | +0.153 | +0.147 |
| `fed_repo_accepted_sameday` | re-run | +0.151 | +0.138 | +0.149 | +0.146 | +0.143 |
| `fed_repo_days_since_positive` | committed (#629) | +0.126 | +0.120 | +0.124 | +0.124 | +0.125 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | +0.126 | +0.120 | +0.124 | +0.124 | +0.125 |
| `fed_repo_days_since_positive` | re-run | +0.210 | +0.203 | +0.205 | +0.206 | +0.211 |
| `fed_repo_days_since_positive_sameday` | committed (#629) | +0.117 | +0.126 | +0.120 | +0.126 | +0.127 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | +0.117 | +0.126 | +0.120 | +0.126 | +0.127 |
| `fed_repo_days_since_positive_sameday` | re-run | +0.204 | +0.210 | +0.203 | +0.207 | +0.210 |
| `fed_repo_log_accepted` | committed (#629) | +0.144 | +0.158 | +0.156 | +0.156 | +0.148 |
| `fed_repo_log_accepted` | pre-#662 rebuild | +0.144 | +0.158 | +0.156 | +0.156 | +0.148 |
| `fed_repo_log_accepted` | re-run | +0.136 | +0.149 | +0.148 | +0.148 | +0.142 |
| `fed_repo_log_accepted_change` | committed (#629) | -0.014 | +0.011 | +0.009 | +0.012 | +0.002 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | -0.014 | +0.011 | +0.009 | +0.012 | +0.002 |
| `fed_repo_log_accepted_change` | re-run | -0.013 | +0.010 | +0.008 | +0.012 | +0.002 |
| `fed_repo_log_accepted_change_sameday` | committed (#629) | +0.018 | -0.013 | +0.012 | -0.006 | -0.012 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | +0.018 | -0.013 | +0.012 | -0.006 | -0.012 |
| `fed_repo_log_accepted_change_sameday` | re-run | +0.016 | -0.012 | +0.011 | -0.005 | -0.011 |
| `fed_repo_log_accepted_sameday` | committed (#629) | +0.161 | +0.145 | +0.158 | +0.153 | +0.147 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | +0.161 | +0.145 | +0.158 | +0.153 | +0.147 |
| `fed_repo_log_accepted_sameday` | re-run | +0.151 | +0.138 | +0.149 | +0.146 | +0.143 |
| `fed_repo_ops` | committed (#629) | +0.098 | +0.115 | +0.110 | +0.115 | +0.106 |
| `fed_repo_ops` | pre-#662 rebuild | +0.098 | +0.115 | +0.110 | +0.115 | +0.106 |
| `fed_repo_ops` | re-run | +0.091 | +0.107 | +0.103 | +0.108 | +0.101 |
| `fed_repo_ops_sameday` | committed (#629) | +0.114 | +0.099 | +0.115 | +0.110 | +0.108 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | +0.114 | +0.099 | +0.115 | +0.110 | +0.108 |
| `fed_repo_ops_sameday` | re-run | +0.106 | +0.093 | +0.108 | +0.105 | +0.104 |
| `fed_repo_rate_iorb_bps` | committed (#629) | -0.040 | -0.025 | -0.022 | -0.027 | -0.031 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | -0.040 | -0.025 | -0.022 | -0.027 | -0.031 |
| `fed_repo_rate_iorb_bps` | re-run | -0.046 | -0.031 | -0.027 | -0.033 | -0.036 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#629) | -0.038 | -0.024 | -0.021 | -0.025 | -0.029 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | -0.038 | -0.024 | -0.021 | -0.025 | -0.029 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | -0.044 | -0.030 | -0.026 | -0.031 | -0.034 |
| `fed_repo_submitted` | committed (#629) | +0.144 | +0.157 | +0.156 | +0.156 | +0.148 |
| `fed_repo_submitted` | pre-#662 rebuild | +0.144 | +0.157 | +0.156 | +0.156 | +0.148 |
| `fed_repo_submitted` | re-run | +0.136 | +0.149 | +0.148 | +0.148 | +0.142 |
| `fed_repo_submitted_sameday` | committed (#629) | +0.161 | +0.145 | +0.158 | +0.153 | +0.147 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | +0.161 | +0.145 | +0.158 | +0.153 | +0.147 |
| `fed_repo_submitted_sameday` | re-run | +0.151 | +0.138 | +0.149 | +0.146 | +0.143 |
| `srf_take_up` | committed (#629) | +0.238 | +0.270 | +0.269 | +0.272 | +0.262 |
| `srf_take_up` | pre-#662 rebuild | +0.238 | +0.270 | +0.269 | +0.272 | +0.262 |
| `srf_take_up` | re-run | +0.238 | +0.270 | +0.269 | +0.272 | +0.262 |
| `srf_take_up_positive` | committed (#629) | -0.141 | -0.123 | -0.123 | -0.120 | -0.119 |
| `srf_take_up_positive` | pre-#662 rebuild | -0.141 | -0.123 | -0.123 | -0.120 | -0.119 |
| `srf_take_up_positive` | re-run | -0.141 | -0.123 | -0.123 | -0.120 | -0.119 |

### Spearman correlation with the spread change, ordinary days pooled (no interval is drawn for a correlation in this record)

| series | source | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 |
|---|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#629) | -0.008 | +0.015 | -0.011 | +0.006 | +0.033 |
| `fed_repo_accepted` | pre-#662 rebuild | -0.008 | +0.015 | -0.011 | +0.006 | +0.033 |
| `fed_repo_accepted` | re-run | -0.002 | +0.026 | -0.007 | +0.011 | +0.038 |
| `fed_repo_accepted_sameday` | committed (#629) | -0.012 | -0.008 | +0.014 | -0.006 | -0.002 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | -0.012 | -0.008 | +0.014 | -0.006 | -0.002 |
| `fed_repo_accepted_sameday` | re-run | -0.013 | -0.002 | +0.024 | -0.008 | -0.003 |
| `fed_repo_days_since_positive` | committed (#629) | -0.009 | -0.015 | -0.008 | -0.012 | -0.036 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | -0.009 | -0.015 | -0.008 | -0.012 | -0.036 |
| `fed_repo_days_since_positive` | re-run | -0.041 | -0.046 | -0.030 | -0.039 | -0.052 |
| `fed_repo_days_since_positive_sameday` | committed (#629) | -0.002 | -0.008 | -0.015 | -0.010 | -0.011 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | -0.002 | -0.008 | -0.015 | -0.010 | -0.011 |
| `fed_repo_days_since_positive_sameday` | re-run | -0.033 | -0.041 | -0.045 | -0.030 | -0.026 |
| `fed_repo_log_accepted` | committed (#629) | -0.008 | +0.015 | -0.011 | +0.006 | +0.033 |
| `fed_repo_log_accepted` | pre-#662 rebuild | -0.008 | +0.015 | -0.011 | +0.006 | +0.033 |
| `fed_repo_log_accepted` | re-run | -0.002 | +0.026 | -0.007 | +0.011 | +0.038 |
| `fed_repo_log_accepted_change` | committed (#629) | -0.024 | +0.005 | -0.056 | -0.001 | +0.035 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | -0.024 | +0.005 | -0.056 | -0.001 | +0.035 |
| `fed_repo_log_accepted_change` | re-run | -0.026 | +0.010 | -0.051 | -0.001 | +0.040 |
| `fed_repo_log_accepted_change_sameday` | committed (#629) | +0.039 | -0.021 | +0.007 | +0.014 | -0.021 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | +0.039 | -0.021 | +0.007 | +0.014 | -0.021 |
| `fed_repo_log_accepted_change_sameday` | re-run | +0.034 | -0.024 | +0.011 | +0.008 | -0.026 |
| `fed_repo_log_accepted_sameday` | committed (#629) | -0.012 | -0.008 | +0.014 | -0.006 | -0.002 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | -0.012 | -0.008 | +0.014 | -0.006 | -0.002 |
| `fed_repo_log_accepted_sameday` | re-run | -0.013 | -0.002 | +0.024 | -0.008 | -0.003 |
| `fed_repo_ops` | committed (#629) | -0.003 | +0.029 | -0.012 | +0.015 | +0.034 |
| `fed_repo_ops` | pre-#662 rebuild | -0.003 | +0.029 | -0.012 | +0.015 | +0.034 |
| `fed_repo_ops` | re-run | +0.003 | +0.038 | -0.008 | +0.019 | +0.038 |
| `fed_repo_ops_sameday` | committed (#629) | -0.010 | -0.004 | +0.027 | +0.005 | -0.005 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | -0.010 | -0.004 | +0.027 | +0.005 | -0.005 |
| `fed_repo_ops_sameday` | re-run | -0.011 | +0.002 | +0.036 | +0.003 | -0.006 |
| `fed_repo_rate_iorb_bps` | committed (#629) | +0.001 | +0.057 | +0.011 | +0.013 | +0.013 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | +0.001 | +0.057 | +0.011 | +0.013 | +0.013 |
| `fed_repo_rate_iorb_bps` | re-run | +0.006 | +0.065 | +0.014 | +0.017 | +0.017 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#629) | +0.000 | +0.055 | +0.008 | +0.013 | +0.013 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | +0.000 | +0.055 | +0.008 | +0.013 | +0.013 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | +0.006 | +0.063 | +0.011 | +0.017 | +0.017 |
| `fed_repo_submitted` | committed (#629) | -0.008 | +0.016 | -0.011 | +0.006 | +0.033 |
| `fed_repo_submitted` | pre-#662 rebuild | -0.008 | +0.016 | -0.011 | +0.006 | +0.033 |
| `fed_repo_submitted` | re-run | -0.002 | +0.026 | -0.006 | +0.011 | +0.038 |
| `fed_repo_submitted_sameday` | committed (#629) | -0.013 | -0.008 | +0.014 | -0.006 | -0.002 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | -0.013 | -0.008 | +0.014 | -0.006 | -0.002 |
| `fed_repo_submitted_sameday` | re-run | -0.013 | -0.002 | +0.024 | -0.009 | -0.003 |
| `srf_take_up` | committed (#629) | -0.005 | +0.045 | -0.025 | +0.018 | +0.050 |
| `srf_take_up` | pre-#662 rebuild | -0.005 | +0.045 | -0.025 | +0.018 | +0.050 |
| `srf_take_up` | re-run | -0.005 | +0.045 | -0.025 | +0.018 | +0.050 |
| `srf_take_up_positive` | committed (#629) | +0.028 | +0.064 | +0.003 | +0.033 | +0.049 |
| `srf_take_up_positive` | pre-#662 rebuild | +0.028 | +0.064 | +0.003 | +0.033 | +0.049 |
| `srf_take_up_positive` | re-run | +0.028 | +0.064 | +0.003 | +0.033 | +0.049 |

### Pre-onset contrast on ordinary days, lead 1 (24 pre-onset days before 6 onsets), pooled, with 90% intervals

| series | source | AUC | std. diff |
|---|---|---|---|
| `fed_repo_accepted` | committed (#629) | 0.56 [0.36, 0.78] | +0.92 [-0.29, +2.43] |
| `fed_repo_accepted` | pre-#662 rebuild | 0.56 [0.36, 0.78] | +0.92 [-0.29, +2.43] |
| `fed_repo_accepted` | re-run | 0.56 [0.37, 0.78] | +0.92 [-0.29, +2.43] |
| `fed_repo_accepted_sameday` | committed (#629) | 0.56 [0.36, 0.79] | +1.09 [-0.29, +2.74] |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | 0.56 [0.36, 0.79] | +1.09 [-0.29, +2.74] |
| `fed_repo_accepted_sameday` | re-run | 0.57 [0.37, 0.79] | +1.09 [-0.29, +2.74] |
| `fed_repo_days_since_positive` | committed (#629) | 0.48 [0.28, 0.70] | -0.11 [-0.55, +0.51] |
| `fed_repo_days_since_positive` | pre-#662 rebuild | 0.48 [0.28, 0.70] | -0.11 [-0.55, +0.51] |
| `fed_repo_days_since_positive` | re-run | 0.59 [0.30, 0.88] | +0.94 [-0.14, +2.06] |
| `fed_repo_days_since_positive_sameday` | committed (#629) | 0.49 [0.28, 0.71] | -0.09 [-0.54, +0.54] |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | 0.49 [0.28, 0.71] | -0.09 [-0.54, +0.54] |
| `fed_repo_days_since_positive_sameday` | re-run | 0.59 [0.30, 0.88] | +0.94 [-0.15, +2.06] |
| `fed_repo_log_accepted` | committed (#629) | 0.56 [0.36, 0.78] | +0.73 [-0.35, +2.05] |
| `fed_repo_log_accepted` | pre-#662 rebuild | 0.56 [0.36, 0.78] | +0.73 [-0.35, +2.05] |
| `fed_repo_log_accepted` | re-run | 0.56 [0.37, 0.78] | +0.73 [-0.35, +2.05] |
| `fed_repo_log_accepted_change` | committed (#629) | 0.49 [0.41, 0.55] | +0.07 [-0.03, +0.21] |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | 0.49 [0.41, 0.55] | +0.07 [-0.03, +0.21] |
| `fed_repo_log_accepted_change` | re-run | 0.49 [0.41, 0.55] | +0.07 [-0.03, +0.21] |
| `fed_repo_log_accepted_change_sameday` | committed (#629) | 0.56 [0.49, 0.64] | +0.22 [+0.00, +0.55] |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | 0.56 [0.49, 0.64] | +0.22 [+0.00, +0.55] |
| `fed_repo_log_accepted_change_sameday` | re-run | 0.56 [0.49, 0.64] | +0.22 [+0.00, +0.55] |
| `fed_repo_log_accepted_sameday` | committed (#629) | 0.56 [0.36, 0.79] | +0.79 [-0.34, +2.18] |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | 0.56 [0.36, 0.79] | +0.79 [-0.34, +2.18] |
| `fed_repo_log_accepted_sameday` | re-run | 0.57 [0.37, 0.79] | +0.79 [-0.34, +2.18] |
| `fed_repo_ops` | committed (#629) | 0.53 [0.36, 0.71] | +0.13 [-0.56, +0.84] |
| `fed_repo_ops` | pre-#662 rebuild | 0.53 [0.36, 0.71] | +0.13 [-0.56, +0.84] |
| `fed_repo_ops` | re-run | 0.53 [0.37, 0.71] | +0.13 [-0.56, +0.84] |
| `fed_repo_ops_sameday` | committed (#629) | 0.54 [0.37, 0.73] | +0.19 [-0.56, +0.98] |
| `fed_repo_ops_sameday` | pre-#662 rebuild | 0.54 [0.37, 0.73] | +0.19 [-0.56, +0.98] |
| `fed_repo_ops_sameday` | re-run | 0.54 [0.37, 0.73] | +0.20 [-0.55, +0.99] |
| `fed_repo_rate_iorb_bps` | committed (#629) | 0.46 [0.37, 0.55] | -0.28 [-0.53, +0.06] |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | 0.46 [0.37, 0.55] | -0.28 [-0.53, +0.06] |
| `fed_repo_rate_iorb_bps` | re-run | 0.46 [0.37, 0.55] | -0.27 [-0.52, +0.06] |
| `fed_repo_rate_iorb_bps_sameday` | committed (#629) | 0.46 [0.37, 0.55] | -0.27 [-0.52, +0.06] |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | 0.46 [0.37, 0.55] | -0.27 [-0.52, +0.06] |
| `fed_repo_rate_iorb_bps_sameday` | re-run | 0.46 [0.37, 0.55] | -0.27 [-0.52, +0.06] |
| `fed_repo_submitted` | committed (#629) | 0.56 [0.36, 0.78] | +1.10 [-0.29, +2.81] |
| `fed_repo_submitted` | pre-#662 rebuild | 0.56 [0.36, 0.78] | +1.10 [-0.29, +2.81] |
| `fed_repo_submitted` | re-run | 0.56 [0.37, 0.78] | +1.10 [-0.29, +2.81] |
| `fed_repo_submitted_sameday` | committed (#629) | 0.56 [0.36, 0.79] | +1.22 [-0.28, +2.96] |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | 0.56 [0.36, 0.79] | +1.22 [-0.28, +2.96] |
| `fed_repo_submitted_sameday` | re-run | 0.57 [0.37, 0.79] | +1.22 [-0.28, +2.96] |
| `srf_take_up` | committed (#629) | - | - |
| `srf_take_up` | pre-#662 rebuild | - | - |
| `srf_take_up` | re-run | - | - |
| `srf_take_up_positive` | committed (#629) | 0.44 [0.39, 0.52] | -0.31 [-0.54, +0.08] |
| `srf_take_up_positive` | pre-#662 rebuild | 0.44 [0.39, 0.52] | -0.31 [-0.54, +0.08] |
| `srf_take_up_positive` | re-run | 0.44 [0.39, 0.52] | -0.31 [-0.54, +0.08] |

### Spearman with the +5 bp indicator at lead 1, ordinary days, by split

| series | source | 2018-19 | scarce | 2020 | 2025-26 |
|---|---|---|---|---|---|
| `fed_repo_accepted` | committed (#629) | +0.022 | -0.053 | +0.187 | +0.184 |
| `fed_repo_accepted` | pre-#662 rebuild | +0.022 | -0.053 | +0.187 | +0.184 |
| `fed_repo_accepted` | re-run | +0.016 | -0.056 | +0.187 | +0.184 |
| `fed_repo_accepted_sameday` | committed (#629) | +0.051 | -0.010 | +0.219 | +0.315 |
| `fed_repo_accepted_sameday` | pre-#662 rebuild | +0.051 | -0.010 | +0.219 | +0.315 |
| `fed_repo_accepted_sameday` | re-run | +0.015 | -0.029 | +0.219 | +0.315 |
| `fed_repo_days_since_positive` | committed (#629) | +0.017 | +0.049 | -0.113 | -0.154 |
| `fed_repo_days_since_positive` | pre-#662 rebuild | +0.017 | +0.049 | -0.113 | -0.154 |
| `fed_repo_days_since_positive` | re-run | -0.013 | +0.041 | -0.113 | -0.154 |
| `fed_repo_days_since_positive_sameday` | committed (#629) | -0.026 | +0.011 | -0.114 | -0.211 |
| `fed_repo_days_since_positive_sameday` | pre-#662 rebuild | -0.026 | +0.011 | -0.114 | -0.211 |
| `fed_repo_days_since_positive_sameday` | re-run | -0.013 | +0.032 | -0.114 | -0.211 |
| `fed_repo_log_accepted` | committed (#629) | +0.022 | -0.053 | +0.187 | +0.184 |
| `fed_repo_log_accepted` | pre-#662 rebuild | +0.022 | -0.053 | +0.187 | +0.184 |
| `fed_repo_log_accepted` | re-run | +0.016 | -0.056 | +0.187 | +0.184 |
| `fed_repo_log_accepted_change` | committed (#629) | +0.039 | +0.050 | +0.047 | +0.021 |
| `fed_repo_log_accepted_change` | pre-#662 rebuild | +0.039 | +0.050 | +0.047 | +0.021 |
| `fed_repo_log_accepted_change` | re-run | +0.038 | +0.049 | +0.047 | +0.021 |
| `fed_repo_log_accepted_change_sameday` | committed (#629) | +0.055 | +0.094 | +0.087 | +0.159 |
| `fed_repo_log_accepted_change_sameday` | pre-#662 rebuild | +0.055 | +0.094 | +0.087 | +0.159 |
| `fed_repo_log_accepted_change_sameday` | re-run | +0.027 | +0.082 | +0.087 | +0.159 |
| `fed_repo_log_accepted_sameday` | committed (#629) | +0.051 | -0.010 | +0.219 | +0.315 |
| `fed_repo_log_accepted_sameday` | pre-#662 rebuild | +0.051 | -0.010 | +0.219 | +0.315 |
| `fed_repo_log_accepted_sameday` | re-run | +0.015 | -0.029 | +0.219 | +0.315 |
| `fed_repo_ops` | committed (#629) | +0.019 | -0.057 | +0.152 | +0.153 |
| `fed_repo_ops` | pre-#662 rebuild | +0.019 | -0.057 | +0.152 | +0.153 |
| `fed_repo_ops` | re-run | +0.012 | -0.061 | +0.152 | +0.153 |
| `fed_repo_ops_sameday` | committed (#629) | +0.049 | -0.018 | +0.153 | +0.236 |
| `fed_repo_ops_sameday` | pre-#662 rebuild | +0.049 | -0.018 | +0.153 | +0.236 |
| `fed_repo_ops_sameday` | re-run | +0.008 | -0.041 | +0.153 | +0.236 |
| `fed_repo_rate_iorb_bps` | committed (#629) | +0.044 | +0.034 | -0.213 | +0.214 |
| `fed_repo_rate_iorb_bps` | pre-#662 rebuild | +0.044 | +0.034 | -0.213 | +0.214 |
| `fed_repo_rate_iorb_bps` | re-run | +0.036 | +0.028 | -0.213 | +0.214 |
| `fed_repo_rate_iorb_bps_sameday` | committed (#629) | +0.044 | +0.034 | -0.213 | +0.214 |
| `fed_repo_rate_iorb_bps_sameday` | pre-#662 rebuild | +0.044 | +0.034 | -0.213 | +0.214 |
| `fed_repo_rate_iorb_bps_sameday` | re-run | +0.036 | +0.028 | -0.213 | +0.214 |
| `fed_repo_submitted` | committed (#629) | +0.022 | -0.054 | +0.185 | +0.184 |
| `fed_repo_submitted` | pre-#662 rebuild | +0.022 | -0.054 | +0.185 | +0.184 |
| `fed_repo_submitted` | re-run | +0.016 | -0.057 | +0.185 | +0.184 |
| `fed_repo_submitted_sameday` | committed (#629) | +0.054 | -0.009 | +0.219 | +0.315 |
| `fed_repo_submitted_sameday` | pre-#662 rebuild | +0.054 | -0.009 | +0.219 | +0.315 |
| `fed_repo_submitted_sameday` | re-run | +0.017 | -0.029 | +0.219 | +0.315 |

### Did the grouping or the ranking move?

* Groups of redundant series (|rho| >= 0.8, ordinary pooled), lead 1: committed against re-run identical: **True**; pre-#662 rebuild against re-run identical: **True**.
* Groups of redundant series (|rho| >= 0.8, all pooled), lead 1: committed against re-run identical: **True**; pre-#662 rebuild against re-run identical: **True**.
* Table 2 (the 25 series with the largest absolute pooled pressure correlation on ordinary days): committed against re-run, same 25 in the same order: **False** (as sets: **True**); pre-#662 rebuild against re-run, same order: **True**. No `fed_repo_*` series is in any of the three lists: **True**.
* Rank (by that statistic, among the 101 series) differs between the pre-#662 rebuild and the re-run for 43 series: 14 of the 14 that read `fed_repo_*` and 29 others, which move only because a `fed_repo_*` series passed them (none of their own figures changed). The `fed_repo_*` moves: `fed_repo_accepted` 76 to 77, `fed_repo_accepted_sameday` 59 to 65, `fed_repo_days_since_positive` 45 to 35, `fed_repo_days_since_positive_sameday` 47 to 36, `fed_repo_log_accepted` 77 to 78, `fed_repo_log_accepted_change` 93 to 92, `fed_repo_log_accepted_change_sameday` 69 to 74, `fed_repo_log_accepted_sameday` 60 to 66, `fed_repo_ops` 81 to 87, `fed_repo_ops_sameday` 67 to 75, `fed_repo_rate_iorb_bps` 70 to 71, `fed_repo_rate_iorb_bps_sameday` 68 to 70, `fed_repo_submitted` 75 to 76, `fed_repo_submitted_sameday` 58 to 64.

### Series whose figures differ, pre-#662 rebuild against re-run (every cell of `source_matrix.json`, tolerance 1e-9)

14 series: `fed_repo_accepted`, `fed_repo_accepted_sameday`, `fed_repo_days_since_positive`, `fed_repo_days_since_positive_sameday`, `fed_repo_log_accepted`, `fed_repo_log_accepted_change`, `fed_repo_log_accepted_change_sameday`, `fed_repo_log_accepted_sameday`, `fed_repo_ops`, `fed_repo_ops_sameday`, `fed_repo_rate_iorb_bps`, `fed_repo_rate_iorb_bps_sameday`, `fed_repo_submitted`, `fed_repo_submitted_sameday`. Sections touched: ['bootstrap', 'correlations', 'scope']. `incremental` (partial correlations) is unchanged: no `fed_repo_*` series is among its top series. `srf_take_up` and `srf_take_up_positive` read `srf_inputs`, not the repo operations, and are identical in all three sources. Every other series is identical to 1e-9.

### Pairwise matrix (ordinary days, pooled, lead 1)

* 1239 pairs involve a `fed_repo_*` series; the largest absolute change in a pair's rho, pre-#662 rebuild to re-run, is 0.162. Pairs that cross |rho| = 0.8 (in or out of a group): 3: `fed_repo_accepted`-`fed_repo_days_since_positive` -0.800 to -0.800; `fed_repo_days_since_positive`-`fed_repo_submitted` -0.800 to -0.800; `fed_repo_days_since_positive`-`fed_repo_log_accepted` -0.800 to -0.800.
* Pairs with no `fed_repo_*` member whose rho changed (pre-#662 rebuild to re-run): 0.

### Series that do not read `fed_repo_*` whose figure differs from the committed record

Committed `source_matrix.json` against the pre-#662 rebuild (same code and fixtures as main one commit before #662, so #662 is not the cause): `net_settlement_due_5d`, `satiation_dist_roll`, `satiation_distance`, `satiation_hinge_roll`.


Three pairs are within rounding of the 0.8 line (the CSV is rounded to three decimals, so `-0.800` appears on both sides); the groups themselves are computed on the unrounded values and are identical, as stated above.

## Does re-running the unchanged code at the committed state reproduce the old numbers?

Yes. `git archive 6ca061b6` (the commit that published the matrix) run with the page's commands gives a merged panel with sha256 `8299bac3…`, the declared value, and a `source_matrix.json` that is byte-identical to the committed one (`cmp`).

The committed-against-pre-#662 differences above (`net_settlement_due_5d`, `satiation_dist_roll`, `satiation_distance`, `satiation_hinge_roll`) are therefore code or data changes on `main` between 12 October and #662 that are not #662: the net settlement and satiation-distance construction fixes (#620 and #622, `e6bcf5ba`, `5421c64b`). They are small (the largest change in a pooled pressure correlation over leads is 0.021, `satiation_hinge_roll`; 0.014 for `net_settlement_due_5d`; 0.006 for the two distance columns) and they change the order of a few rows in Tables 2, 6 and 7. The attribution is by commit dates and the files those commits touch; it was not bisected. Note that these re-runs are of the page's commands at `ee9366eb`, so the committed record's `satiation_*` and `net_settlement_due_5d` figures are themselves stale against current `main` independently of #662.

## Not checked

* No interval on a Spearman correlation (the record draws none), no correction for the number of tests.
* The page's prose was not edited.
* The 2026 days and the +10 bp threshold are not looked at.
