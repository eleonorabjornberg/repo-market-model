## Track

- [ ] Track A - data layer (`feature/data-layer`)
- [ ] Track B - model and evaluation (`feature/model-eval`)
- [ ] Human - contract, plan, methodology, CI

## Contract

- [ ] Rebased on current `main`, and `AGENT_CONTRACT.md` re-read at its current revision
- [ ] No file owned by the other track is touched (CI checks this; say so here if it flagged a shared file)
- [ ] Leakage guards raise `LookAheadError`, never `assert`
- [ ] Every new guard has a recorded mutation, run with `-B` and `PYTHONDONTWRITEBYTECODE=1`
- [ ] Stdlib only outside `src/repo_model/ml.py` - no new dependency without the human

## Mutations recorded

<!-- One line each: what was flipped, how many tests failed, which suites. -->

## Expected failures

<!-- If this PR turns an expectedFailure green, it must convert it to a real
     assertion in the same commit. Unexpected success fails CI by design. -->
