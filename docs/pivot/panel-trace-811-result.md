# Why H5 step 4's rerun of H2's ceiling did not rebuild H2's declared panel (#811)

**Serves:** reproducibility (`REPRODUCIBILITY.md`); H2 step 3 (the upper bound, #635) and H5 step 4 (#758). Development tier. Nothing is scored for a verdict, no rule changes, no published record is edited.

## Answer

The difference is in the **build**, not in the inputs. The published panel (`4ddc3882…`) rebuilds clean from the same tracked snapshots on both trees. What changed between H2's tree and the tree H5 step 4 built on is two corrections to scratch-panel columns:

| change | merged | columns it moves in the scratch panel `DERIV.csv` |
|---|---|---|
| #679, a partly announced bill class is left out until it is fully announced | 13 October 2026 (after H2's branch point) | `net_settlement_due_5d` only |
| #743, a Fed repo operation under $0.1 bn accepted is no take-up | 15 October 2026 (after H5 step 4's panel was built) | the twelve `fed_repo_*` columns |

H2's branch did not contain #679, #684 or #743. H5 step 4 (#775) built its panel on a main that held #679 but not #743.

## What was done

Each panel is built by the chain in `evidence/panel-trace-811/chain.sh` (`pressure_v1_1`, `measurement_fields`, `satiation_distance_598`, `net_settlement`, `policy_features`, `fed_liquidity`, `nowcast`, `dvp_segment_inputs`, `early_warning_inputs`, `source_screen`, `derived_features_631`; the published panel `4ddc3882…` first, from `build`).

| panel | tree | sha256 |
|---|---|---|
| H2's declared panel | H2's tree (`ec534758`), the two satiation columns moved to just after `srf_take_up_positive` as `metadata/upper_bound_635.json` lists them | `08df8d19…` (**matches the declaration**) |
| same values, columns in chain order | H2's tree | `1e5b748a…` |
| H5 step 4's panel | main with #743 left out (main's files, `src/repo_model/fed_liquidity.py` and `ingest.py` at H2's tree) | `92bf10a4…` (**matches the digest H5 step 4 recorded**) |
| main with #679 left out | main, `net_settlement.py` and its metadata at H2's tree | `90f8ada9…` |
| main today | `09f2409c` | `69be91b6…` |

Compared with H2's values, `92bf10a4…` differs in `net_settlement_due_5d` alone (96 rows). Main today also differs in the twelve `fed_repo_*` columns (hundreds of rows each), from #743. The full counts are in `evidence/panel-trace-811/trace.json`.

So the two things that kept H5 step 4 from matching `08df8d19…` were both explained: the column order (two columns placed as the declaration lists them, which the Reproduce section of H2's page gives only in words) and the value of one column (#679).

## Does the difference move a figure?

H2's fits were re-run from the two H2-valued panels on **current main code** (`/opt/rmm-venv`, `OMP_NUM_THREADS=1`; all 505 fit tasks, then `upper_bound_635.py score`). Walk-forward days, ordinary targets, skill of the gradient-boosted fit against B1, with the 90% interval:

| run | reachable gbm | ceiling gbm |
|---|---|---|
| H2 as recorded | +0.192 [+0.007, +0.352] | +0.162 [-0.009, +0.310] |
| control A: `08df8d19…` on main code | +0.192 [+0.007, +0.352] | +0.162 [-0.009, +0.310] |
| control B: `1e5b748a…` on main code | +0.192 [+0.007, +0.352] | +0.162 [-0.009, +0.310] |
| H5 step 4's rerun, `92bf10a4…` | +0.196 [+0.019, +0.354] | +0.168 [+0.003, +0.316] |

* Both controls reproduce the recorded figures to every digit stored (the unrounded values are in `trace.json`). So the code since H2 has not moved them, and **column order does not matter** to the fits.
* H5 step 4's panel differs from control B in `net_settlement_due_5d` alone. The +0.004 and +0.006 are therefore that column's: **#679, a correction, not a change in inputs.** This is attribution by elimination; a third fit on `92bf10a4…` itself was not run here (it is H5 step 4's own fit).

## What is not affected, and what is not checked

* **Published records:** none. The published panel is unchanged and verifies; `DERIV.csv` is a scratch panel. H2's page (`upper-bound-result.md`) stays as recorded and reproduces. H5 step 4's page records a rerun on a panel that is also explained. No published figure moves, so nothing is republished (`docs/decisions/publish-rule.md`).
* **Not checked:** a fit on today's main panel (`69be91b6…`), which also carries #743's twelve `fed_repo_*` columns. Whether those move the ceiling is not measured here; it takes about four hours of fitting.

## Marked questions for Eleonora (judgement calls, not settled here)

1. **Which ceiling stands for H5 step 4.** H5 step 4 relaxed the reproduction tolerance from 0.001 to 0.01 as a declared deviation. The trace shows the check at the original tolerance (the one H2 recorded) passes on the panel H2 declared, rebuilt at its own tree. Should the headroom be reported against that ceiling (H2's declared panel, recorded figures), against the current-main ceiling, or both?
2. **The ceiling's interval.** On H2's panel the ceiling gbm's interval against B1 is [-0.009, +0.310] and covers 0; on `92bf10a4…` it is [+0.003, +0.316] and does not. The reachable fit's interval clears 0 on both. Whether H2's kill rule reads the ceiling or the reachable fit, and what a crossing at this size means, is hers.

## Reproduce

```
git worktree add /tmp/w_h2 ec534758
git worktree add /tmp/w_main <main commit>
bash docs/pivot/evidence/panel-trace-811/chain.sh /tmp/w_h2 /tmp/h2          # DERIV.csv: 1e5b748a…; with the two satiation columns moved as declared: 08df8d19…
bash docs/pivot/evidence/panel-trace-811/chain.sh /tmp/w_main /tmp/main      # main today: 69be91b6…; with #743's two files at H2's tree: 92bf10a4…
PYTHONPATH=src python3 scripts/upper_bound_635.py fit --panel DERIV.csv --output OUT/fits.json
PYTHONPATH=src python3 scripts/upper_bound_635.py score --published PUB.csv --fits OUT/fits.json --output OUT/score.json
```

Evidence: [`evidence/panel-trace-811/`](evidence/panel-trace-811/) (`trace.json`, `chain.sh`).
