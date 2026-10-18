# #632 re-scored on the current distance columns: commands (#871)

Development data only, not a verdict. The page is `docs/pivot/spread-distribution-871-result.md`. Base commit `80b5ef0a`, published panel `4ddc3882…` (`verify-panel` clean), `/opt/rmm-venv`,
`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`, `PYTHONPATH=src`. `S` holds the scratch files, `OUT` the forecasts.

```
python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output S/PUBLISHED.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
python3 -m repo_model.cli verify-panel S/PUBLISHED.csv --manifest metadata/funding_panel_manifest.json
python3 scripts/pressure_v1_1.py panel --output S/AUG.csv
python3 scripts/measurement_fields.py panel --panel S/AUG.csv --output S/AUG2.csv
python3 scripts/satiation_distance_598.py panel --panel S/AUG2.csv --output S/AUG2D.csv
for h in 1 2 3 4 5:
  python3 scripts/pressure_judge.py forecasts --panel S/PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
  python3 scripts/risk_date_severity.py run --panel S/AUG2.csv --published S/PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
  python3 scripts/pressure_track_q.py forecasts --panel S/PUBLISHED.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
  for m in risk_gbm risk_gbm_base:
    python3 scripts/announcement_dating_rescore.py run --arm both --model $m --panel S/AUG2.csv --published S/PUBLISHED.csv --horizon $h --output OUT/both_${m}_h$h.json
  python3 scripts/satiation_587.py merge --parents OUT/both_risk_gbm_h$h.json OUT/both_risk_gbm_base_h$h.json --output OUT/both_h$h.json
  python3 scripts/satiation_587.py reference --input OUT/q_h$h.json --output OUT/ql_h$h.json
  python3 scripts/satiation_distance_598.py run --panel S/AUG2D.csv --published S/PUBLISHED.csv --horizon $h --output OUT/dist_h$h.json
  python3 scripts/iorb_every_day_579.py run --panel S/AUG2.csv --published S/PUBLISHED.csv --horizon $h --parent OUT/both_risk_gbm_h$h.json --output OUT/iorb_h$h.json
python3 scripts/every_day_conditioning_601.py cap --panel S/PUBLISHED.csv --scratch S/AUG2D.csv --output-dir OUT OUT/iorb_h?.json
for h in 1 2 3 4 5:
  python3 scripts/spread_distribution_632.py run --panel S/AUG2D.csv --published S/PUBLISHED.csv --horizon $h --output OUT/sd_h$h.json
  python3 scripts/spread_distribution_632.py refs --both OUT/both_h$h.json --dist OUT/dist_h$h.json --cap OUT/cap_h$h.json --output OUT/refs_h$h.json
python3 scripts/spread_distribution_632.py distribution --panel S/PUBLISHED.csv 'OUT/sd_h{h}.json' --output OUT/distribution.json --markdown OUT/distribution.md
for r in weighted unweighted:
  python3 scripts/pressure_judge.py judge --panel S/PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/refs_h?.json OUT/sd_h?.json
python3 scripts/spread_distribution_632.py compare --panel S/PUBLISHED.csv --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/refs_h{h}.json' --rows 'OUT/sd_h{h}.json' --output OUT/compare.json --markdown OUT/compare.md
python3 scripts/spread_distribution_632.py ordinary --panel S/PUBLISHED.csv --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/refs_h{h}.json' --rows 'OUT/sd_h{h}.json' --output OUT/ordinary.json
python3 scripts/spread_distribution_632.py report --compare OUT/compare.json --distribution OUT/distribution.json --ordinary OUT/ordinary.json --output OUT/report.md
python3 docs/pivot/evidence/spread-distribution-871/before_after.py > docs/pivot/evidence/spread-distribution-871/before_after.md
```

The files here are `OUT/distribution.{json,md}`, `compare.{json,md}`, `ordinary.json`, `report.md` and `judge_{weighted,unweighted}.md` (as `judge-weighted.md`, `judge-unweighted.md`), under the names of `docs/pivot/evidence/spread-distribution/`.
`before_after.py` reads that folder (the tracked scoring) and this one (the rebuild) and prints `tracked → rebuilt` tables.
The judge declaration (`metadata/pressure_judge.json`) has changed since the page was scored (sha256 `21f988fd…` then, `e936998e…` now); the rows whose forecasts did not change (`risk_gbm+settle+h41` and the `+tailcap75` row) give the same judge row in both, so the move in the other rows comes from the forecasts.
The older distance columns, for the comparison in the page's table of other pages, were built by `scripts/satiation_distance_598.py` of commit `011023cb` in a scratch worktree of main (see `../spread-632-drift/README.md`).
