#!/usr/bin/env bash
# #902 (H9 step 2 without decision day 2019-09-18): the long run, for the Mac (15 walks: 3 targets x 5 leads).
# Run from the repository root with the `ml` extra installed. Writes to $OUT (default ./out902); nothing under docs/runs/.
set -euo pipefail
OUT=${OUT:-out902}
mkdir -p "$OUT"
export PYTHONPATH=src
python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output "$OUT/PUBLISHED.csv" \
    --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
python3 scripts/tax_date_market_days.py scripts/pressure_v1_1.py panel --output "$OUT/AUG.csv"
python3 scripts/tax_date_market_days.py scripts/measurement_fields.py panel --panel "$OUT/AUG.csv" --output "$OUT/AUG2.csv"
python3 scripts/tax_date_market_days.py scripts/satiation_distance_598.py panel --panel "$OUT/AUG2.csv" --output "$OUT/AUG2D.csv"
python3 scripts/richer_targets_639.py panel --panel "$OUT/AUG2D.csv" --output "$OUT/H9D.csv"
for T in bgcr_dispersion_bps on_rrp_change_bn sofr_dispersion_bps; do
  for h in 1 2 3 4 5; do
    python3 scripts/richer_targets_706.py walk --target "$T" --horizon "$h" --panel "$OUT/H9D.csv" --output "$OUT/${T}_h$h.json"
  done
done
# the tracked score's own inputs: this must reproduce docs/pivot/evidence/richer-targets-706/score.json
python3 scripts/richer_targets_706.py score --panel "$OUT/H9D.csv" --walks "$OUT" --output "$OUT/score.json"
cmp "$OUT/score.json" docs/pivot/evidence/richer-targets-706/score.json
python3 scripts/richer_targets_706.py sensitivity --panel "$OUT/H9D.csv" --walks "$OUT" --output "$OUT/sensitivity.json"
python3 scripts/richer_targets_706.py sensitivity-report --sensitivity "$OUT/sensitivity.json" --output "$OUT/sensitivity.md"
