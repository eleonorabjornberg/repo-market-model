# H5 step 4 again, on two named panels: the ceiling, the reachable line and the headroom (#904)

**Development data, not a verdict.** A measurement run on development days to 2025-12-31 and nothing later; no locked day is scored (`docs/decisions/lockbox.md`). Nothing is registered, no declaration or published record is edited, and no rule moves.
Hypothesis and step: H5, step 4 (an input to milestone M4 and to H2.M3). Directive #904; Eleonora's rulings of 19 October 2026 on #904 and #900 (option (c)).

## Status: the run is waiting for Eleonora's Mac

The fits take about three hours each on three cores and each walk 15 to 40 minutes (`h5-step4-result.md`), so by the rule on #46 the run is not made in the cloud. This page holds what is settled without it: which two panels, how each is built and checked, and the commands. **The tables below are empty until the result commit comes back on this branch.**

## The two panels (the ruling)

| panel | chain built at | `DERIV.csv` digest | what it is |
|---|---|---|---|
| H2's record commit | `ec534758` | `1e5b748a…` | the chain at the commit of H2's record; it does not give H2's `08df8d19…` (`deriv-chain-903-result.md`) |
| main's panel | `71cf91d2` | `69f22bc6…` | the digest the ruling names as main's, "the reproducible panel on main (see #909)" |

`scripts/h5_step4_904.py` builds each in a detached worktree at its commit with the chain of #903 and refuses (`ValueError`) a `DERIV.csv` whose digest is not the ruled one. Both builds were made in the cloud while preparing this page and gave exactly those digests, from the published panel `4ddc3882…` and `AUG2D` `73534301…` (the same bytes at both commits, which is why the walks are made once).

**Finding: the head of main no longer gives `69f22bc6…`.** At `b008b564` the chain gives `eaf24b55…`. Steps up to `nowcast` (`AUG6`) match #903's table for main; the first step that moves is `source_screen` (`SCREEN` `8666800a…` against `e832ff78…`). The ruling's "main's panel" is therefore read here by its digest, which is reproduced at the commit #903 used. Whether the run should rather use the head of main's `eaf24b55…` is Eleonora's; it needs a third fit, and nothing here settles it.

## What is run, unchanged

`scripts/h5_step4_758.py`, `scripts/upper_bound_635.py` and `scripts/spread_distribution_634.py` are not edited, and `metadata/h5_step4_758.json` is not either (seed 758, the interval in force, tolerance 0.01 from its deviation 1). The candidates' walks (`gbm_funding`, `c_two_part_new`, five leads) read the published panel and `AUG2D`, so they are the same for both panels and are made once; the candidate rows must reproduce #758's exactly. Only the cross-fitted ceiling and the reachable line are refit on each `DERIV.csv`.

```
PYTHONPATH=src python3 scripts/h5_step4_904.py plan --workdir OUT   # the 18 commands, in order
PYTHONPATH=src python3 scripts/h5_step4_904.py run --workdir OUT    # runs them; a step whose output exists is skipped
```

with `/opt/rmm-venv` (or the same versions) and `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1` (the script sets both). The outputs are `OUT/<panel>/score.json` and `report.md`, to be copied to `evidence/h5-step4-904/<panel>/`. If the declared reproduction check (the rerun against H2's recorded skills, tolerance 0.01) refuses on a panel, the score stops there and says so; a wider tolerance is a new deviation and is hers to accept, so the run does not set one.

## Result

To come from the Mac: for each panel, the ceiling, the reachable line and the headroom of the ceiling over the best candidate, pooled and by regime including 2024, beside #758's tracked figures (`h5-step4-result.md`) and #898's (`without-day-882-result.md`).

## Marked question for Eleonora (nothing decided here)

1. Does #758's "continue in 2024" stand? Its answer is read from the result above once the run is back; it is hers.
2. The head of main gives `eaf24b55…`, not the ruled `69f22bc6…` (above). Should the main-panel arm be refit on the head of main as well?

## Not checked

Nothing is scored on this page yet. The reproduction check, the candidate rows' exactness and the headroom are not run.
