# Project Status

**Measured at the commit that carries this revision of the page.** `git log -1
--format='%h %ci' -- docs/PROJECT_STATUS.md` names it and prints when. The
commit is the timestamp; no date is written onto this page by hand, because a
hand-written date can run ahead of the work it describes, and dating information
other than when it was actually available is the failure this repository exists
to prevent.

This page is a snapshot, not a claim that the repository is complete. It describes
`main` only: work sitting unmerged on a branch is named as such.

## Summary

Repo Market Model is a tested research and evaluation foundation for a
probabilistic repo-market forecast. It is not yet a validated forecasting model.

The strongest completed work is the part that prevents misleading empirical
results: point-in-time provenance, release-lag handling at field granularity,
immutable acquisition, purged time-series evaluation, event-window separation,
and probabilistic scoring. The benchmark now writes its numbers to a file
instead of to a terminal.

**The sentence that stood here through every previous revision of this page --
that every number this repository reports was produced on a synthetic sample --
is no longer true.** Milestone A steps 3 and 4 ran: a funding-only daily panel
was frozen from the 6 September 2026 NY Fed and FRED snapshots, and the
persistence benchmark was measured on it. 2104 rows, 2018-04-03 to 2026-09-03,
no holes in either leg of the spread. The panel is gitignored; its build
manifest and the run records are in `docs/runs/`, and no figure from them is
transcribed onto this page or any other.

What that does *not* establish is forecast skill. The persistence benchmark is
a benchmark, and reading its record will show it under-covering its own nominal
interval. That is the benchmark being honest rather than the pipeline being
broken, and it is the number a challenger model now has to beat.

Three things about the frozen panel belong on a status page rather than only in
a commit message:

- **The administered leg is spliced.** IORB begins 2021-07-29; IOER, which it
  replaced, supplies everything before. Without the splice the panel begins in
  July 2021 and contains no stress episode at all.
- **The panel is funding-only by construction, not by choice.** `tgcr`, `bgcr`
  and `treasury_settlement` are built columns with no observations, because
  their sources were not part of this freeze.

## Evidence available now

- The standard-library suite completes successfully, with no expected failures.
  How many tests that is belongs to CI, not to this page.
- The `fit` / `predict` / `predict_stress` interface and the `ExceedancePredictor`
  interface beside it each have several implementers, discovered by the tests
  rather than listed here, in every module of the package, through one walk; the
  exceedance marker reads the return annotation as a type, so a module without
  `from __future__ import annotations` is not missed. Both sets of conformance tests are parametrized over
  implementations, so each assertion runs once per implementer rather than once in
  total; that multiplication, not the file diff, is what makes each an interface
  rather than a description of one model. A coverage guard asserts that the set of
  implementers and the set of covered ones are the same set, so a new model cannot
  arrive with a bespoke test class and quietly skip the shared assertions.
- Stress probabilities are derived from the predictive distribution, and a
  conformance test asserts the derivation: at a declared level `q`, the exceedance
  reported at that quantile is `1 - q`. A separately fitted classifier fails that
  test even when it is well calibrated on its own terms.
- Fitted transform parameters are checked to come from the training window alone.
  The check is not vacuous: the ARX imputes absent regressors from a training
  window mean, and a mutation that widens that window to the whole frame is caught
  by a named test.
- Regressor names are fitted state on the fitted object, not a global. An absent
  regressor raises; an unobserved value takes the training-window mean. Neither
  becomes `0.0`, which is the one value the contract forbids appearing by accident.
- Prediction intervals use a leave-one-out residual law. The in-sample alternative
  was measured rather than assumed, and is about 11% too narrow at the 90% level on
  the checked-in sample.
- **The purge is derived, never supplied.** `--source` is gone from both evaluation
  commands. The gap comes from the declared feature set, through the registry, and
  what the fitted model actually read is checked against that declaration after the
  fit. A derived purge cannot be zero, so the unpurged backtest is no longer
  expressible.
- **The release lag is a property of a field, not only of a source.** A
  latest-vintage source may back a point-in-time feature for a field declared never
  revised, and only with evidence attached; a field-level record-date block without
  a declared revision policy is refused. One field is declared under this rule and
  every other field of that source stays refused.
- **The backtest publishes rather than prints.** `backtest` requires a report path
  and writes the run's own record: the declared feature set, the sources and purge
  it derived, the decision time, the panel's path, digest and extent, the folds
  with their first and last origins, and the metrics unrounded — mean absolute
  error with a stationary-bootstrap interval, interval coverage, pinball loss at
  each declared level, and CRPS. A value that cannot be computed is absent rather
  than defaulted, and nothing is rounded, because a rounded figure is one nobody
  computed.
- **The join from observations to a daily panel exists.** A cell carries the
  latest vintage available at the build's declared cutoff; a column is built only
  if the registry will price it, and the refusal is called rather than restated, so
  a refused column is absent and never quietly revised. The join does **not**
  subtract the release lag — the purge does, and a join that shifted values too
  would apply the gap twice while looking careful. There is no forward fill: a
  reference date with no observation is a hole, counted and left empty; the ingest's
  quality report records why each source cell behind it was absent.
- **An identity that could not be evaluated no longer reads as one that held.**
  Absent terms are never imputed to zero, unevaluable reference dates are recorded
  term by term, and the check walks every date any term was observed on rather than
  the intersection of them all. The intersection is what made years of an unchecked
  balance sheet invisible.
- Under-covered SEC Form N-MFP cross-sections are excluded from the modeling panel
  by an entity-count floor declared in the source registry, or because their holdings
  matched no repo category; each exclusion is judged per vintage and carries its `exclusion_reason`
  (`below_floor`, `no_repo_rows`) and is recorded separately from ordinary missingness. The floor is a **declared absolute
  count**, calibrated from an observed complete month. A fraction of a trailing
  median was considered and rejected: the trailing window is itself computed from
  straggler months, which would set the floor low enough to admit the
  cross-sections it exists to reject.
- **N-MFP refusal is per table, and the value vocabulary is declared.** An absent
  non-spine table costs the fields it would have fed rather than the whole archive;
  a renamed column still refuses the archive, because a renamed column looks
  exactly like an absent value and can silently erase a series. Investment-category
  eras are declared, closing the door that header compatibility left open: every
  column present under the same name for over a decade, and a value vocabulary that
  changed underneath. The declared archive set is recorded with digests and per-table
  refusal verdicts.
- Duplicate and amended N-MFP submissions are resolved before aggregation: the
  latest filing wins per series and report date, with the accession number breaking
  a same-day tie.
- September 2019 and March 2020 event windows are frozen and checksummed, and the
  scoring and knowledge holdouts are kept distinct in code and in reporting.
- Public-source downloads are stored immutably with retrieval timestamps, request
  URLs, byte counts and SHA-256 digests. The tracked Treasury fixtures are the
  exception: their manifests record a ceiling (the time the file was first
  committed), which stands in for the retrieval time by decision, the auctions URL records the
  request but cannot reproduce the bytes, and the 2026 bill-rate file has no
  manifest at all.
- Forecast-distribution, exceedance, calibration, and dependence-aware uncertainty
  metrics are implemented and tested.

These facts show that the research harness operates. They do not establish
forecast skill -- but the reason has changed twice. It is no longer that the
sample is synthetic, and it is no longer that no challenger has been scored:
three have, against the persistence benchmark on the fetched panel under purged
rolling origins. The two ARX specifications lost on absolute error and on CRPS; the
trailing-window residual law won on CRPS and under-covers its own interval (below).
Skill is a *comparison*, and none yet made meets Phase 2's criterion. The figures
are in `docs/runs/`, not here.

## Known gaps in the evidence

Stated explicitly, because each is easy to mistake for something stronger.

- **The model comparison rests on real data now, and it did not go the way a
  challenger needs it to.** This gap is closed as a gap in evidence and replaced
  by a finding. Two ARX challengers were scored against persistence on the
  fetched panel at paired origins -- one reading SOFR volume, one reading the
  p25/p75 dispersion -- and persistence carried the smaller absolute error in
  both, with neither 90% interval on the paired difference including zero.
  Re-run under `--loss crps`, which scores the whole law rather than its centre,
  persistence again carried the smaller loss in both, again with neither interval
  including zero. The `docs/runs/compare_persistence_vs_arx_*` records carry the
  figures, the origins and the seeds for both losses; none of them is transcribed
  here. **What this does not
  establish is that nothing beats persistence.** Two ARX specifications are two
  points in one family, both constrained to regressors that price the same purge
  gap, because a different gap is a different set of origins and losses at
  different origins are not paired. Of the other models PLAN.md's Phase 2
  names, the trailing-window residual law (`--model rolling-residual`) has been
  scored against persistence under `--loss crps`, in
  `docs/runs/compare_persistence_vs_rolling_residual_w60_mh61_crps.json`, and its
  90% interval on the paired difference excludes zero in rolling-residual's favour.
  The ARX CRPS records were run at the same minimum history, over the same
  origins, so every CRPS finding here is measured against persistence at one
  set of origins; no challenger has been compared with another directly.
  Gradient-boosted conditional quantiles (`--model gbm`, behind the `ml` extra)
  were scored the same way, in `docs/runs/compare_persistence_vs_gbm_mh61_crps.json`,
  and the 90% interval on its mean paired difference also excludes zero in its
  favour, around a mean difference an order of magnitude larger than
  rolling-residual's. Re-scored on a later commit with the same figures, that record
  now names the numpy and scikit-learn versions that fitted it under
  `provenance.ml_libraries`, as every record and event-holdout journal line with an
  ml fit does. These are several challengers against one benchmark at the 90% level,
  on a daily panel scored with an expanding window and a purge. The threshold ARX
  (`--model threshold`) loses to persistence with either regime variable, which
  each record names under `declaration.model_b.regime_variable`: on
  `sofr_volume` (`docs/runs/compare_persistence_vs_threshold_regime_volume_mh61_crps.json`)
  the 90% interval on the mean difference excludes zero in persistence's favour only
  just, and on `spread_bps`, the SETAR
  (`docs/runs/compare_persistence_vs_threshold_regime_spread_mh61_crps.json`), it
  excludes zero clearly. The gbm, threshold and rolling-residual records say which
  days a win or a loss comes from (`comparison.per_origin`); the ARX records predate
  it. The rolling-residual result also makes
  the interval-coverage finding harder rather than easier: the
  model that under-covers its own nominal interval is the one that wins on
  accuracy, so the coverage gap is not a defect of a strawman about to be
  replaced. gbm sharpens it: backtested at the same declaration, its nominal
  interval covers far fewer outcomes than persistence's does
  (`docs/runs/backtest_gbm_mh61.json`, `docs/runs/backtest_persistence_mh61.json`),
  and both fall short of their nominal probability. Split-conformal calibration
  (`--calibration conformal`, `docs/runs/backtest_gbm_conformal_mh61.json`) moves
  gbm's coverage toward nominal without reaching it, and costs it the CRPS win. A
  cross-conformal interval that keeps the full fit (`--calibration cross_conformal`) is built, not scored.
- **Part of the command line is unpublished.** `backfill-nmfp` and
  `event-holdout` ship with no invocation any published document tells a reader
  to run. `tests/test_docs_freshness.py` has checked since `6708755` that a
  published command still parses; it validated in the direction its own defect
  ran, and the complement -- a command published nowhere at all -- is outside
  the set it reads. `compare` and `exceedance-backtest` were in that complement
  until they were published against the shipped fixture, and `build` until the
  reproduction published it against the tracked inputs. `backfill-nmfp` needs a
  route to the SEC; `event-holdout` needs the full panel, which a clone can now
  rebuild, so what keeps it unpublished is its journal write, not a missing file.

- **The daily panel has been built and run.** `data/processed/` is no longer
  empty. What the run exposed is that `build` had been writing a panel `backtest`
  could not open -- the row grid was the union of every source's reference dates,
  so a calendar-daily administered rate beside a business-daily market rate
  produced rows on which the target does not exist. That is fixed and the fix is
  a contract decision, not a repair: see "The frozen funding panel" in the
  Summary.
- **The headline exceedance metric does not yet scale to the panel.**
  `exceedance-backtest` refits at every rolling origin, which is the whole point
  of it, and the cost is roughly quadratic in panel length: seconds on the
  twenty-five-row fixture, minutes on 2104 rows. Nothing about the number is
  wrong; the command simply outgrew the fixture it was developed against. One
  record of it on the frozen panel does exist, and it is deliberately the least
  interesting run available: a climatology scored against itself, which must show
  exactly no skill and does, at every declared threshold. That is the check every
  later skill score rests on, and it is not a result. **No conditional model has
  been scored with this metric on the panel**, which is the real gap between "the
  metric has a path" and "the metric has been taken".
- **The monthly N-MFP panel is no longer a single observation, and is not yet a
  trustworthy series.** The archive history has been backfilled: the declared set is
  fetched and digested in full, none of it refused as unreadable, and the monthly
  `mmf_*` series now span the archive period rather than one reference date. Two
  things follow, and only the first is good news. Supersession and coverage are now
  resolved across the whole archive set rather than within one archive -- an
  amendment routinely lands in a different archive from the filing it restates, and
  per-archive resolution could not see the pair, so it left originals standing that
  a later filing had corrected. What a cross-section *is* has now been settled on
  both open questions: a split month-end is assembled as one cross-section
  (`346d4ff`), and the coverage floor is declared per era rather than as one number
  (`94bf2db`). A monthly N-MFP field's unit of observation is therefore no longer
  under revision on those two axes; what is still open is item 5 below -- the
  identity tolerance calibrated against it. The daily shareholder-flow series were
  unaffected by all of this throughout.
- **The pre-2016 N-MFP balance sheet is missing two of three left-hand terms.**
  `CASH` and `TOTALVALUEPORTFOLIOSECURITIES` are present as columns and entirely
  empty before the 2016 boundary. Those months are now reported as unevaluable
  rather than counted as holding, which is the honest treatment of the symptom; the
  field mapping that would let the identity actually evaluate over that period does
  not exist.
- **The coverage floor is now declared per era (`94bf2db`)**, closing the gap
  where one absolute count -- roughly a quarter of the early universe and two
  thirds of the current one -- was weak in the eras it was not calibrated on.
  Each era entry is calibrated from an observed complete month, assembled by
  `346d4ff`'s cross-section rule rather than by report date.
- **A declared field was reported as never producing data, and it produces the
  facility.** `mmf_on_rrp` emits 200 rows over 156 reference dates, carries nothing
  until the first month-end after the ON RRP facility opened, and peaks at 2,273.8 bn
  on 2022-12-31 -- 76.4% of `mmf_repo_holdings`. This page stated the opposite on
  evidence from the single archive then held: `FEDERAL RESERVE` occurs 18,119 times
  across the 87 of 97 archives held now, and never once in the description field the
  derivation was said to search. The half this page did not lead with is now
  declared: a month through 2013-08 with no row is a reviewed structural zero, and
  2026-07-31, after the facility opened, stays an undeclared absence -- two records,
  not one representation.
- **The N-MFP identity tolerance is a single absolute bound** and after
  calibration it stays one. That is now a decision rather than a deferral
  (`febba6d`), and two claims this page previously made about it were measured
  and are false. The admitted cross-sections do **not** span three orders of
  magnitude: post-floor and post-assembly, scale runs 3178 to 9254 USD billions,
  a factor of 2.9, and the population of small months that made the case for a
  relative bound no longer exists. Nor is the bound "loose on the smallest and
  tight on the largest" — normalising the residual by scale moves its dispersion
  from 0.764 to 0.745 decades and leaves its rank correlation with scale at
  +0.05, so a `relative_ppm` has almost nothing to correct. The schema accepts
  one and `contract.py` resolves the pair; the mechanism is present and
  exercised. What is absent is a reason to use it here.

  **The bound is still refused by a majority of the population it checks** — it
  admits 44 of the 124 evaluable cross-sections — and the reason is a finding
  rather than a bound problem. From 2024-06 to 2026-02, twenty-one consecutive
  months beginning exactly at the declared `n_mfp2`-to-`n_mfp3` boundary and
  resolving after it, the identity breaks one-sidedly: assets exceed liabilities
  plus net assets in all twenty-one. A bound sized to admit that would be sized
  to admit a defect that starts and stops on a form-version boundary. Outside
  that window the residual is two-sided and still exceeds the bound on 59 of 103,
  so the check is tight for the well-behaved regime too — tight in absolute terms
  at every scale, which is not what a relative bound corrects.
  `metadata/sources.json`'s `tolerance_note` carries the derivation and
  `DATA_QUALITY_DECISIONS.md` records the decision.
- **No model reads the Treasury settlement split yet.** `treasury_settlement_bills`,
  `treasury_settlement_coupons` and `treasury_settlement_soma` are panel columns, SOMA
  outside the aggregate because `offering_amt` excludes it. The `0.0` on a day with no
  settlement is decided and not yet emitted, and nothing tests whether the aggregate's
  simplification affects conclusions.
- **Rates volatility and the cash-futures basis are not in the panel.** The MOVE
  index is licensed, and the Treasury cash-futures basis needs licensed futures prices;
  this repository takes public sources only (human decision, 10 Sep). A public proxy
  for each is open, and neither blocks a block.
- **The never-revised claim is prose.** The field-level release lag is licensed by
  a `revision_evidence` string. The comparison behind it was done outside the
  repository, so if a future vintage restated an observation, nothing here would go
  red. Committing the vintages and recomputing the comparison in a test is briefed
  and not built.

## Work required before empirical claims

The first two items of every previous revision of this list -- build and freeze a
panel, and backfill the archive history -- have been done, and the list now starts
where they left off.

1. Score the threshold ARX (`--model threshold`) against the persistence benchmark
   on the frozen panel under `--loss crps`, before building another model. The
   model exists; the comparison does not.
2. Make the exceedance metric affordable at panel length, then take it with a
   conditional model rather than with climatology alone.
3. ~~Settle what a monthly N-MFP cross-section *is*~~ -- done: a split month-end is
   assembled as one cross-section (`346d4ff`) and the coverage floor is declared per
   era (`94bf2db`). What is not yet done is recalibrating the identity tolerance (item
   5) against the cross-sections this unlocks.
4. ~~Establish whether `mmf_on_rrp` is derived correctly~~ -- done: it is, against
   2022-12-31, when money funds held 2,273.8 bn of Fed reverse repo, 76.4% of their repo
   book (`scripts/nmfp_on_rrp_channel.py`). What is not done is making an absent declared
   field distinguishable from a parsing failure, which is now the whole of this item.
5. Calibrate the N-MFP identity tolerance -- after item 3, not before -- and source
   panel columns from the Treasury-settlement components the adapter now emits.
   Both decisions are recorded in `DATA_QUALITY_DECISIONS.md`.
6. Replace the never-revised prose with committed vintages and a test that
   recomputes the comparison offline. The IOER declaration is the weaker of the two
   and the one covering the earlier stress episode.
7. Extend the same freeze to the remaining sources, with a machine-readable quality
   report.
8. Report the frozen event windows separately from rolling-origin evaluation.
9. Add a quantile machine-learning model only after the baselines are frozen.

## Who is responsible for what

The project has two co-owners. Eleonora Björnberg, the author, designed the model, the
methodology and the workflow, and holds implementation, evaluation and every claim
about what the model has earned. Nicholas Beroud, Financial Advisor, selected the data
the model is built on and settled what it means: which of the open decisions in
`DATA_QUALITY_DECISIONS.md` are questions about markets rather than about code, and
what a series has to represent before it is worth fitting on.

The split is worth stating on a status page specifically, because the gaps listed
above are not all of one kind. Some are engineering — a join not yet run, a freeze not
yet taken — and those are the author's. Others are finance judgments that no amount of
test coverage will settle: whether a summed settlement series can stand in for a
collateral-supply channel, whether an accounting identity means anything on a partial
cross-section, what a stress regime should be declared to be. Those are his.

## Portfolio interpretation

The repository may accurately be described as a leakage-safe, point-in-time
financial research pipeline with a tested probabilistic evaluation harness, a
model interface with several implementers, purged rolling-origin evaluation of them,
and a benchmark that publishes a reproducible record of its own run. It should
not yet be described as a successful machine-learning forecast of repo stress. A
frozen funding panel now exists and the persistence benchmark has been measured
on it, so the phrase that stood here -- that no result rests on real data -- has
stopped being true. What has not happened is the part that would make it a
forecast: no challenger has met Phase 2's exit criterion against that benchmark, the
headline exceedance metric has been taken on the panel only against climatology,
and the monthly money-fund panel, though no longer a single cross-section, rests
on a unit of observation still under revision.

As an academic exercise, its current contribution is methodological: the repository
shows what it takes to keep a funding-market forecast honest before any forecast is
made. That is a real contribution and it is also a limited one, and this page exists to
keep the two from being confused.

The next portfolio milestone is a compact results package containing a frozen data
snapshot, a persistence-versus-challenger comparison under purged evaluation,
tail-calibration evidence, event-window plots, limitations, and exact reproduction
instructions. The reporting half of that package existed before Milestone A; the
frozen snapshot and the persistence half of the comparison exist now. What is
still missing from it is the challenger comparison and the tail-calibration
evidence, which is Phase 2.

## Where the run records live, and why there

`docs/runs/` holds the frozen panel's build manifest and the records measured on
it. The panel itself stays gitignored under `data/processed/`; the manifest is
the committable half, and it reached nobody while it sat beside the panel. That
manifest predates the panel digest. The one that carries it, beside the tracked
inputs, is `metadata/funding_panel_manifest.json`; `verify_daily_panel` checks a panel
against it and refuses the older one, or a malformed digest, rather than passing it. So
the published records bind their manifest by extent, and a re-run binds by digest.

`docs/runs/` was chosen over `metadata/panels/` -- which would have followed the
N-MFP archive-manifest precedent -- because `metadata/` is Track A's and a human
commit there while Track A's N-MFP packet is in flight is a conflict waiting to
happen. It is also outside `tests/test_docs_freshness.py`'s Markdown scope, and
it is where the records that cite the manifest land, so the panel and the numbers
measured on it sit together. It can move to `metadata/` once that packet is done.
Recorded here because a path chosen and unrecorded is the next session's
archaeology.
