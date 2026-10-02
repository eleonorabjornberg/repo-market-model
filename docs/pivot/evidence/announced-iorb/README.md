# Announced IORB: comparison records (directive #38)

Not published records. `docs/runs/` is unchanged, and no generated page reads this folder. The verdict on these
results is Eleonora's.

Each comparison scores gbm on `sofr_p25`, `sofr_p75`, `sofr_volume` and `spread_bps` (side a) against the same model
plus `iorb_announced_change_bps` and `iorb_days_to_announced_change` (side b). Both sides are paired on one as-of
grid, refit every 21 scored days, at the 16:00 decision, with every scored day before 2026-01-01
(`docs/decisions/lockbox.md`).

| File | What it is |
|---|---|
| `compare_gbm_vs_gbm_iorb_mae.json` | The directive's comparison, absolute error |
| `compare_gbm_vs_gbm_iorb_crps.json` | The directive's comparison, CRPS |
| `compare_gbm_vs_gbm_iorb_direct_{mae,crps}.json` | Supplementary: both sides with `--training-pairs direct` (#37) |
| `window_3bd.json` | Each record split into days within ±3 panel business days of an effective date, and the rest |

## Reproduce

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
python3 scripts/announced_iorb_panel.py /tmp/funding_panel.csv /tmp/panel_iorb.csv --decision-time 16:00
OMP_NUM_THREADS=1 PYTHONPATH=src python3 -m repo_model.cli compare /tmp/panel_iorb.csv --end 2025-12-31 --registry metadata/sources.json --decision-time 16:00 --minimum-history 61 --refit-every 21 --splits metadata/evaluation_splits.json --model-a gbm --feature-a sofr_p25 --feature-a sofr_p75 --feature-a sofr_volume --feature-a spread_bps --model-b gbm --feature-b sofr_p25 --feature-b sofr_p75 --feature-b sofr_volume --feature-b spread_bps --feature-b iorb_announced_change_bps --feature-b iorb_days_to_announced_change --loss crps --report /tmp/compare_crps.json
python3 scripts/announced_iorb_window.py /tmp/panel_iorb.csv /tmp/compare_crps.json --days 3
```

`--loss absolute-error` gives the MAE record, and `--training-pairs-a direct --training-pairs-b direct` the
supplementary ones. `OMP_NUM_THREADS=1` changes only the speed. Without it, several gbm runs on one machine
oversubscribe its cores and can take hours.
