# Directive: re-score and publish under the as-of rule

Starts after directive 01 has merged. Work it as one pull request, a publish under `docs/decisions/publish-rule.md`.

**Goal.** Replace every published figure with one scored under `docs/decisions/information-set.md`, and archive the
records scored under the earlier rule.

**Do:**
1. Score under the as-of rule, with monthly refit declared, on one fold grid:
   - persistence;
   - gbm with calibration `none`;
   - gbm with `cross_conformal`;
   - the published funding declaration.
2. Score the pressure-probability benchmarks at the thresholds in `metadata/stress_thresholds.json`: calendar-type
   climatology and a persistence-logistic model.
   - Report Brier skill with the Murphy decomposition, precision-recall and CORP reliability.
   - Split every result by regime and by pressure-day type.
   - Pair every comparison, with stationary-bootstrap intervals.
3. Move every record scored under the earlier rule to `docs/runs/archive/pre-asof/`, with a README naming the rule
   they were scored under. Make `scripts/emit_results.py` render only from `docs/runs/` at the top level.
4. Regenerate every page rendered from records in the same commit, never by hand.
5. Update the `PLAN.md` and README statements that the new figures make false (for example "next business day"
   forecasting, and Phase 2's verdicts), and update `docs/pivot/plan.md` §7.

**Acceptance.**
- CI green.
- `tests/test_generated_results.py` passes on the new records.
- Every headline number in the README traces to a record in `docs/runs/`.
- Persistence reproduces directive 01's figure exactly.

**Report in the pull request.** Which earlier conclusions survive, change or reverse, against the list in
`docs/pivot/lag-assessment.md` §4. Open a `finding` issue for each one that reverses.
