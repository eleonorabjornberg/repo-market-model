# Superseded: #155: pre-correction labels

These five records were published exceedance records, scored under the as-of rule through 2026-09-03:

- `exceedance_calendar_climatology.json`
- `exceedance_climatology.json`
- `exceedance_gbm.json`
- `exceedance_gbm_cross_conformal.json`
- `exceedance_persistence_logistic.json`

**Why they were archived: #155: pre-correction labels.** Their labels counted a day whose spread sat exactly on
+5 or +10 bp as above the threshold, so on those days they did not measure the strict event that
`docs/decisions/pressure-probability.md` declares. Eleonora ruled on
[#155](https://github.com/eleonorabjornberg/repo-market-model/issues/155) that labels compare whole basis
points, and its fix ([#178](https://github.com/eleonorabjornberg/repo-market-model/pull/178)) changed the code.
Her rulings on [#169](https://github.com/eleonorabjornberg/repo-market-model/pull/169) made the pull request for
[#124](https://github.com/eleonorabjornberg/repo-market-model/issues/124) the single corrected publication. It moved
these records here unedited, as the rule "never edit a published record in place" requires.

**What replaced them.** Records of the same names at the top level of `docs/runs/`, scored on whole-bp labels.
Under `docs/decisions/lockbox.md` they score only days from 2018-06-29 to 2025-12-31, and at +20 and +50 bp they
list each event instead of a pooled figure (#130). No figure here is comparable with theirs. The correction note in
`docs/PORTFOLIO_CASE_STUDY.md` gives the figures that moved.

No page is generated from this folder: `scripts/emit_results.py` renders from the records at the top level of
`docs/runs/` only.
