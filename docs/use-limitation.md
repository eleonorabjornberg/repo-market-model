# Use limitation

The one statement below is read by `scripts/emit_results.py` (the README and `docs/final-test.md`) and by
`scripts/emit_visual.py` (the results page, `site/index.html`). Edit it here and regenerate; the generated copies are
never edited by hand. It is the wording of Eleonora's ruling of 6 October 2026 on #261.

## The statement

> A research forecast of the SOFR − IORB spread. It is not a stress-warning system and not a basis for VaR, limits, liquidity or capital, or desk sizing. Its central quantiles are not yet calibrated, its tail coverage is weaker on quarter-ends and turns, and it has little history in the current scarce-reserve regime. It needs revalidation after a material policy or regime change.

The reasons, each from a finding of the independent review:

- Outer-edge conformal PID can make pooled 90% coverage look right while q25 and q75 are badly under-dispersed (#243),
  and turns under-cover (PR #241).
- The history has few observations of the scarce-reserve, ON RRP near zero regime now in force.
- The scarcity cut-points ($100bn ON RRP, the reserve band) are descriptive classifications chosen and evaluated on
  the same history.
- The final test had 5 events above +5 bp and none above +10 bp.

This statement is carried over to the validation report (#119) and the plain-language page (#120).

## Revalidation triggers

**Proposed for Eleonora. None of the thresholds is decided.** The model needs revalidation, by the same paired and
split evidence as the final test, after any of:

| Trigger | Proposed threshold |
|---|---|
| A QT restart | the FOMC statement announcing a reduction of securities holdings, or its minutes recording a decision to resume it |
| ON RRP balance falls below a level | proposed: below $10bn on any business day (the declared scarcity cut-point is $100bn; this is the near-zero case) |
| A change to the IORB setting | any change of IORB relative to the top of the target range, or any change in the administered-rate technical adjustment |
| A scarcity-state change | the scarcity classification (`repo_model.scarcity`) changes state and stays changed for five consecutive business days |
