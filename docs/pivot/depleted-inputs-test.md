# The ON RRP depletion inputs: the test, declared before scoring (#132)

Status: declared in a commit before anything was scored. Eleonora's ruling on #132 ("Publish 132 if it improves the
model"), with the test her ruling on #339 sets out, fixes the test below; this file only fixes its details. The panel,
the runs and the judgement are produced by `scripts/pressure_v1_1.py` (its `panel`, `run`, `crps` and `pair` commands)
and `scripts/depleted_inputs_judge.py`. Nothing in this file changes after the scoring commit except by a new commit
that says why.

## The candidate

`on_rrp_depleted` (1 when the New York Fed's ON RRP take-up is below $100bn, `contract.ON_RRP_DEPLETION_BREAK_BN`)
and `reserves_when_depleted` (`reserve_balances` times that indicator), the pressure-v1.1 candidate
`conditional_scarcity` (#88). `on_rrp` reads the Desk's operation results (`nyfed_on_rrp`, #45), public at 16:00 the
next business day. The candidate adds the two columns to the published declaration's features and changes nothing
else: same fits, refits, grid and nested conformal calibration.

## The test

- **Days:** the published window, 2018-06-29 to 2025-12-31 only. No row after 2025-12-31 is loaded
  (`docs/decisions/lockbox.md`); the scratch panel stops there.
- **Control:** the published declaration. The distribution side is the published funding declaration
  (gbm, `conformal_pid_nested`); the pressure side is pressure model v1 as published, at horizon 1.
- **Pairing:** each scored day, control against candidate, on one fold grid.
- **Five-quantile score:** `compare --loss crps`; paired difference = CRPS(control) - CRPS(candidate), so a positive
  mean favours the candidate. 90% stationary-bootstrap interval.
- **Pressure probability:** the Brier of pressure model v1 with the two columns added, at +5 bp and +10 bp, paired
  against pressure model v1 as published, the same way. The model reads the input as a gbm feature, so the Brier tests
  apply.
- **Splits:** each paired figure split by regime and by pressure-day type, as the records are. A cell under 20 days is
  "too few days" and decides nothing.

## The rule

The two inputs join the published declaration in this pull request only if all of these hold:

1. CRPS: mean difference above 0 and the 90% interval's lower bound above 0.
2. Brier at +5 bp: mean difference above 0 and the lower bound above 0.
3. Brier at +10 bp: mean difference above 0 and the lower bound above 0.
4. No regime cell and no pressure-day-type cell (cells of 20 days or more) of the CRPS or of either Brier figure has
   its interval's upper bound below 0.

Otherwise the inputs stay off, and the pull request reports the figures only. The live record and its pin are not
touched either way.

Not part of the test: the $50bn and $200bn breaks (#131 reported them as sensitivity; the declared break stays
$100bn), and the plain `on_rrp` form (not meeting the rule on #176's re-score).

## Result

Scored after the declaration commit, on the scratch panel `scripts/pressure_v1_1.py panel` builds (published columns
checked against the published digest first), days 2018-06-29 to 2025-12-31. The figures are in
`evidence/depleted-inputs/depleted_inputs.json`; positive favours the candidate.

| Figure | Mean difference | 90% interval | Gate | Cells worse beyond their interval |
|---|---|---|---|---|
| CRPS (bp) | +0.0076 | +0.0027 to +0.0124 | met | none |
| Brier at +5 bp | +0.00041 | +0.00012 to +0.00075 | met | regime 2020 |
| Brier at +10 bp | +0.00008 | -0.00001 to +0.00018 | **not met** | regime 2020, tax date |

The rule is not met (the +10 bp gate, and cells under 4), so the inputs stay off the published declaration. No
published record or page moves.
