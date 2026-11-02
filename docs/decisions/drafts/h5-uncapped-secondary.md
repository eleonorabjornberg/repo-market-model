# Draft: the candidate without the SRF cap, a secondary result of the H5 registration (#1361)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1361, as that directive asks. It
rests on her ruling of 2 November 2026 (chat, relayed on #1361), after an outside publication-readiness review: report an
uncapped version of the candidate as a secondary result, so that the Standing Repo Facility cap is not what rules out large
upward moves. It takes effect only when she moves the section below into the H5 registration herself. **Registering is her own
`GO` action**: this pull request registers nothing, changes no declaration already merged, no pin, no live record and no record
in `docs/runs/`, and the candidate, (s3c-ann-net), does not change.

## Why

The candidate clips every quantile at the Standing Repo Facility line (IORB + 10 bp, margin 0) on target days at full
allotment (`docs/research/h5-candidate.json`, `cap`). A policy rate is not a frictionless ceiling for every participant, and
the full-allotment period holds little tail experience. A registered test in which the cap alone rules out a large upward move
would not show whether the model sees one. The uncapped version, scored beside the candidate, shows what the cap does and
leaves the candidate's claim exactly as it is.

The development evidence is `docs/research/s3c-uncapped-1361-result.md` (declaration `metadata/s3c_uncapped_1361.json`,
committed before any score). It is development data on days already seen, not a verdict; it is cited here and no figure of it
is restated.

## The section, as drafted

---

### Secondary result: the candidate without the SRF cap (#1361)

**Decided by Eleonora on the date this section merges.**

1. **The version.** `sc_s3c_ann_net_uncapped` is (s3c-ann-net) with the cap off and nothing else changed: the same walk, the
   same refits, the same settlement terms read from the auction announcement and sized by net settlement, and
   `repo_model.s3c_candidate.capped_quantiles` not applied. Wherever the facility is not at full allotment on the target day
   it is, cell for cell, the candidate. It fits nothing of its own; its quantiles are the candidate's quantiles before the
   cap.
2. **Its role: reported, not deciding.** The uncapped version cannot pass or fail the registered test, enters no primary or key
   secondary result, changes no verdict, and no decision rule reads it. The candidate is what is registered; the uncapped
   version is logged and scored beside it so that a reader can see what the cap did.
3. **What is scored, prospectively.** On every confirmation day, under scoring protocol v1 and for both versions: grid CRPS
   averaged over h = 1 to 5, upper-tail twCRPS, the Brier score of P(> +5 bp), the coverage of the central 90% and 50% bands
   and the exceedance rate of q95. Each is split into target days at full allotment and the other target days, and by regime
   and pressure-day type as the protocol requires. The uncapped version is paired with the candidate with the protocol's
   studentized stationary bootstrap, and the reading is taken from the bound on mean d as everywhere else. All of it is
   reported only.
4. **How often and by how much the cap binds.** At every scoring date the report carries, for the cells at full allotment, the
   share in which the cap moves a quantile, the size of the move of the 0.95 and 0.99 quantiles and of the largest quantile,
   and the share whose outcome is above the line, by lead. A reader can then see on which days the cap decided the forecast.
5. **Reading it.** The full-allotment period is short, and a tail rate on few days carries a wide interval whichever version
   is read. The report gives the number of days beside each rate, and no claim is made from a rate that the interval cannot
   support.
6. **The cap is a stated assumption of the candidate.** The registration's known limits say so in one sentence, and point to
   this secondary result as the place where its effect is shown.

---

## The live record's hook

This is a proposal for how the live record would carry the uncapped version; **none of it is built here**. The live record
does not carry the H5 candidate at present (`scripts/live_record.py` logs the published distributions and the baselines), so
the hook waits on the candidate entering it, which is her registration and a pin change under `docs/decisions/live-pin.md`.
When it does, the record would carry, beside the candidate's quantiles:

- `distributions.secondary.sc_s3c_ann_net_uncapped.quantiles_bps`: the uncapped quantiles at every horizon, on the contract's
  quantile grid, written before the outcome exists, in the same chain and under the same digest as the candidate's;
- `distributions.secondary.sc_s3c_ann_net_uncapped.cap`: for each horizon, the line in bp the candidate's cap used (or `null`
  where the facility is not at full allotment as known at the decision instant), so that the scorer can split the days and
  count the binding cells without re-deriving the line.

`scripts/live_score.py` would score the block with the same cells as the candidate's and print it in a section labelled
"secondary, reported only". It would add a record version (`READABLE_VERSIONS`) and a validator for the block
(`_validate_distributions`'s sibling), and a pin transition: each is a code change and an owner-attested one. They belong to the
directive that puts the candidate in the live record, not to this draft.

## What is not decided here

The margin of the cap (0 bp) and the line are the candidate's, as the earlier rulings made them. Whether the candidate keeps the
cap is not asked here: the candidate does not change.

## Options for her (the default applies if she has not answered by the next 5 pm batch; it changes no claim)

1. **Merge the section as drafted into the H5 registration** (default). The uncapped version is logged and scored beside the
   candidate, reported only.
2. **Merge it with the binding table (item 4) as a standing line of the report, not only at scoring dates.**
3. **Leave the uncapped version out of the registration** and keep its development page only.
