# Draft: registering the Wednesday-level scarcity input as a secondary candidate (#1146)

**Status: a draft for Eleonora, not in force, and not registered.** Drafted by the pull request that closes #1146, as her ruling of 22
October 2026 (option 2 on #1143) asks: "Prepare, for her, the text of a registration that would score the Wednesday-level input
prospectively." A registration is her own attested action (`docs/decisions/scoring-protocol.md` section 2; `docs/decisions/workflow.md`,
owner-attested items): a relayed ruling does not register anything, and **this pull request registers nothing, changes no published
declaration, and leaves `metadata/sources.json` as it is.** Nothing here is in force until she acts herself on GitHub.

## Read this first: why it should not be signed for the current candidate

The H5 candidate (#941's scaled mean reversion) does not read the scarcity state, so its forecasts are identical under the week average
and the Wednesday level (`docs/research/wednesday-scarcity-1146-result.md`: every quantile of every cell identical on both panels).
Registering the Wednesday-level reading of that candidate would register the same forecasts twice, and its prospective days would add no
information. The text below is therefore written for **a candidate that reads the scarcity state** (#1145's arm (s2), or a probe arm she asks
for), and has one slot, `<MODEL>`, that she or a later directive fills before it is signed.

## The registration, as it would read

**Candidate (secondary, protocol section 2):** `<MODEL>` with its scarcity state formed from the Wednesday level of reserve balances
(`WRBWFRBL`), beside the primary candidate, which reads the week average (`WRESBAL`) as the published declaration does. At most two secondary
candidates may be registered; this would be one.

**What differs between the two registered candidates, and only this:** the value of `reserve_balances` in the scarcity state
(`repo_model.scarcity.reserve_scarcity_state`). Cut-points, the bank-assets leg, the ON RRP leg, the training rule, the refit cadence, the
horizons and the code commit are the primary candidate's and frozen with it by hash.

**Input and availability (same release, same instant).** `WRBWFRBL` is a line of the same H.4.1 release as `WRESBAL`. It takes the
registry's declaration of the average it sits beside, unchanged (`metadata/sources.json`, `fred_macro_latest_vintage`, `field_release_lags`:
16:30 America/New_York, five calendar days after the Wednesday, basis `record_date`), so a forecast at the 16:00 decision instant reads it at
the same row as the average and never earlier (`scripts/wednesday_scarcity_1146.py`, `require_same_release`, raises `LookAheadError`
otherwise). Registering it as a live input needs an availability entry for `WRBWFRBL` in `metadata/sources.json` and `contract.py`; that is a
change to the registry and the declaration, so it is **a second, separate act of hers**, made in the pull request that registers, never in
this one.

**Precondition: the never-revised check.** `WRBWFRBL` is the latest FRED vintage in the repository; its never-revised status is not
verified. The registration should not be signed before `scripts/alfred_wednesday_1146.py` (a short run on her Mac; the `needs-mac:` comment on
the pull request holds the paste) exits 0 for both `WRBWFRBL` and `WDTGAL`. A restated observation would mean the live forecast could not
reproduce its training values, and the input should then be dropped or read at a stated vintage.

**Primary metric, benchmarks, checkpoints:** as the protocol's section 3 and the primary candidate's registration: grid CRPS averaged over
h = 1 to 5, upper-tail twCRPS as key secondary, benchmarks B1, B2 and B3 (B1' beside B1), the studentized stationary bootstrap, checkpoints at 60,
125 and 250 prospective days with Lan-DeMets O'Brien-Fleming spending, Holm across the primary and the key secondary. The comparison that
matters is the paired difference between the two registered candidates, `<MODEL>` on the Wednesday level against `<MODEL>` on the week average,
reported with the same bootstrap; the benchmarks are reported beside it.

**Minimum meaningful effect:** none is set by this draft. The protocol's 3% against persistence is for a candidate against a benchmark; the effect
of a change of input between two candidates is much smaller (the two readings differ on 34 of 1,873 scored days at lead 1 and on none of the 27
pressure onsets, #970), and its power is a question for the power study (#656) she has not asked for. **Her decision:** whether to register a
comparison that cannot reach a verdict in 250 prospective days, or to read the Wednesday level as a reported secondary and not a decision.

**Development variant count to date (protocol section 2):** two readings of the scarcity state, on the candidate of #941 (#1146); the counts of
the other arms are those of their own pages.

**Frozen by hash at registration:** the code commit; the configuration of `<MODEL>` for both readings; the two snapshots of
`tests/fixtures/snapshots/h41_wednesday_levels/` (checksums in `metadata/h41_wednesday_levels_970.json`); and the live pipeline's read of
`WRBWFRBL`.

**Not part of this text, and hers:** opening any confirmation day (each opening is her own attested action, #256), the choice of `<MODEL>`, the
availability entry in the registry, and whether to register at all.

## Options for her

1. **Do not register yet (default).** The candidate does not read the state; wait for #1145's arm (s2) or a probe arm, then fill `<MODEL>`.
2. **Ask for a probe arm first** (a development arm of the candidate that reads the as-of state, run under both readings), then decide.
3. **Register after the ALFRED check passes, with a model that reads the state.** Fill `<MODEL>`, add the registry entry in the registering
   pull request, and sign.
