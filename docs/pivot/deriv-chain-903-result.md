# H2's scratch panel `DERIV.csv`: the chain, and why its digest moves (#903, H2 step 3)

A development measurement of the build, not a result about any forecast. Nothing is scored, nothing is registered, no published record or page is edited and no declaration moves.
Hypothesis and step: H2, step 3 (`docs/research/hypotheses/H2.md`), an input to H5 step 4. Finding #900, found in #882.

## The chain

`scripts/deriv_chain_903.py` is the chain as code. Base for the table below: published panel `4ddc3882…` (`build` and `verify-panel` clean), `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), one thread, `PYTHONHASHSEED=0`.

| # | Step | `--end` |
|---|---|---|
| 1 | `repo_model.cli build` from `tests/fixtures/snapshots/funding_inputs`, cutoff `2026-09-08T21:31:42+00:00`, 16:00:00 (`PUB`) | none |
| 2 | `pressure_v1_1.py panel` (`AUG`) | the script's own |
| 3 | `measurement_fields.py panel` (`AUG2`) | the script's own |
| 4 | `satiation_distance_598.py panel` (`AUG2D`) | the script's own |
| 5 | `net_settlement.py panel` (`AUG3`) | the script's own |
| 6 | `policy_features.py panel` (`AUG4`) | not an option |
| 7 | `fed_liquidity.py panel` (`AUG5`) | the script's own |
| 8 | `nowcast.py panel` (`AUG6`) | the script's own |
| 9 | `dvp_segment_inputs.py panel` and `early_warning_inputs.py panel`, each on `PUB` (`DVP`, `EW`) | the script's own |
| 10 | `source_screen.py panel`, `AUG6` joined with `DVP` and `EW` (`SCREEN`) | not an option |
| 11 | `derived_features_631.py panel` (`DERIV`) | not an option |

Every `--end` is left out. The scripts' own default is at most 2026-09-03 on main (#684) and was earlier on the branch that made H2's record; giving `--end 2025-12-31` to the steps that take one gave the same bytes as the default at main, so the end is not what moves the digest.

```
PYTHONPATH=src python3 scripts/deriv_chain_903.py run --workdir OUT --digests OUT/digests.json
PYTHONPATH=src python3 scripts/deriv_chain_903.py compare A/digests.json B/digests.json
```

## Result

Every commit below was built twice into two fresh directories: **both builds gave the same digest at every step, at every commit** (`evidence/deriv-chain-903/digests.json`, `run_2_identical`). I found no nondeterminism within a commit, so the cause is **code drift between commits**, and nothing needed fixing in code.

Table 1. Digest prefix of each step's output at five commits.

| step | `ec534758` (H2's record) | `2c9bd283` (#679) | `e6e3b01f` (#738) | `38a00d81` (#898's base) | `71cf91d2` (main) |
|---|---|---|---|---|---|
| PUB, AUG, AUG2, AUG2D | `4ddc3882`, `4137d0ad`, `5821868c`, `73534301` | same | same | same | same |
| AUG3 `net_settlement` | `0a38decf` | `6e40ebdd` | `bbd20a27` | `bbd20a27` | `bbd20a27` |
| AUG4 | `27f9de1b` | `18b440a1` | `b6a1c691` | `b6a1c691` | `b6a1c691` |
| AUG5 `fed_liquidity` | `6d3a1b6a` | `cc4bab53` | `e9a030a3` | `4281340e` | `7c1cd551` |
| AUG6 `nowcast` | `a8899489` | `3f7873c8` | `b38fb286` | `88f71f17` | `ccb633da` |
| DVP, EW | `dd4b2e99`, `f74536e7` | same | same | same | same |
| SCREEN | `1e79efa1` | `905f25ea` | `605d3d41` | `ad618b91` | `e832ff78` |
| **DERIV** | `1e5b748a` | **`92bf10a4`** | `b28c6e11` | **`400372d6`** | `69f22bc6` |

* **The first step that moves is `net_settlement` (AUG3)**, between `ec534758` and `2c9bd283` (#679, a partly announced bill class is left out) and again at #738 (cash management bills read point in time); `src/repo_model/net_settlement.py` changed in both. Everything before it is byte-identical at every commit.
* Later changes to `fed_liquidity` and `nowcast` move AUG5 and AUG6 again; `DVP` and `EW` never move.
* **`92bf10a4…` (#758's rerun) is the chain at `2c9bd283`**, and **`400372d6…` (#898) is the chain at `38a00d81`**. Each is reproduced by the step list above at that commit.
* **`08df8d19…` (H2's record) is not reproduced by the chain at `ec534758`, the commit of H2's record, which gives `1e5b748a…`**, nor by putting `satiation_distance_598.py` after `net_settlement.py` (`3432b619…`), nor by reordering the columns into the declaration's order (`metadata/upper_bound_635.json`, `inputs.columns`). So the chain that produced `08df8d19…` is **not identified**. The record says the satiation columns were "placed as the declaration lists them", which no script does; a hand step or a working tree not in the history may be the cause. No digest in a record was edited.

## Marked question for Eleonora (nothing decided here)

1. **Does #758's reading stand?** The ceiling and reachable lines of #758 were scored on a panel (`92bf10a4…`) that the chain reproduces only at `2c9bd283`, and H2's record on a panel (`08df8d19…`) that no commit I tried reproduces. The three digests are three different inputs from three code states, not noise. Whether any reading is re-scored on one named chain, and which, is hers.

## Not checked

H2's fit and scoring were not re-run on any of these panels (the fit takes about two hours on four cores; a long run goes to her Mac). Commits other than the five above were not built, so the table says where the digest moves between those five, not at which commit inside each gap.
