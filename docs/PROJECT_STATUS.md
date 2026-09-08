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
- **IOER's never-revised declaration is not vintage-verified.** No route to
  ALFRED was available from either machine on the day. The claim rests on the
  administrative argument and on the series being closed, and it is weaker than
  the IORB declaration beside it. Every run record built on this panel inherits
  that, and `metadata/sources.json` says so in the entry itself.
- **The panel is funding-only by construction, not by choice.** `tgcr`, `bgcr`
  and `treasury_settlement` are built columns with no observations, because
  their sources were not part of this freeze.

## Evidence available now

- The standard-library suite completes successfully, with no expected failures.
  How many tests that is belongs to CI, not to this page.
- The `fit` / `predict` / `predict_stress` interface has **two** implementers — a
  persistence benchmark and an autoregressive model with exogenous regressors. Its
  conformance tests are parametrized over implementations, so each runs once per
  implementer rather than once in total; that doubling, not the file diff, is what
  makes it an interface rather than a description of one model.
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
  reference date with no observation is a hole, counted and left empty.
- **An identity that could not be evaluated no longer reads as one that held.**
  Absent terms are never imputed to zero, unevaluable reference dates are recorded
  term by term, and the check walks every date any term was observed on rather than
  the intersection of them all. The intersection is what made years of an unchecked
  balance sheet invisible.
- Under-covered SEC Form N-MFP cross-sections are excluded from the modeling panel
  by an entity-count floor declared in the source registry, and the exclusion is
  recorded separately from ordinary missingness. The floor is a **declared absolute
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
  URLs, byte counts and SHA-256 digests.
- Forecast-distribution, exceedance, calibration, and dependence-aware uncertainty
  metrics are implemented and tested.

These facts show that the research harness operates. They do not establish
forecast skill, because the checked-in sample is synthetic.

## Known gaps in the evidence

Stated explicitly, because each is easy to mistake for something stronger.

- **No *model comparison* rests on real data.** This gap has narrowed and not
  closed. The persistence benchmark has now been measured on a fetched panel of
  2104 rows, so its numbers are about the market rather than about the harness.
  The ARX comparison has not: the head-to-head that persistence wins is still the
  two-dozen-row synthetic sample with one constant regressor, and it remains
  evidence about the harness. A challenger measured on the frozen panel is Phase
  2's first job.
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
  wrong; the command simply outgrew the fixture it was developed against, and no
  run record for it exists yet on the frozen panel. This is a real gap between
  "the metric has a path" and "the metric has been taken".
- **The monthly N-MFP panel is a single observation.** One quarterly archive yields
  one complete monthly cross-section, and one archive has been acquired. After the
  coverage floor is applied, the monthly `mmf_*` series have one reference date. No
  monthly N-MFP field can serve as a regressor until the archive history is
  backfilled. The daily shareholder-flow series are not affected. The archive set is
  declared and its members are readable subject to the era boundary; declared is not
  fetched, and fetched is not parsed.
- **The pre-2016 N-MFP balance sheet is missing two of three left-hand terms.**
  `CASH` and `TOTALVALUEPORTFOLIOSECURITIES` are present as columns and entirely
  empty before the 2016 boundary. Those months are now reported as unevaluable
  rather than counted as holding, which is the honest treatment of the symptom; the
  field mapping that would let the identity actually evaluate over that period does
  not exist.
- **The coverage floor is declared for one era.** A single absolute count
  calibrated on a recent month is weak in eras when the filer universe was
  substantially larger — it is roughly a quarter of the early universe and around
  two thirds of the current one. The registry schema is intended to accept a per-era
  declaration, each entry calibrated from an observed complete month; the observed
  counts exist, and the implementation does not.
- **A declared field has never produced data.** `mmf_on_rrp` is declared in the
  source registry and has emitted no row against any real archive. Its derivation
  searches security-description text for a counterparty name. For the period held
  the true value is probably near zero, which is precisely why that period cannot
  distinguish a working derivation from a broken one. `mmf_repo_holdings` is
  affected wherever this is, since private-sector repo is the difference between
  the two series.
- **The N-MFP identity tolerance is a single absolute bound** across cross-sections
  spanning three orders of magnitude, so it is loose on the smallest and tight on
  the largest. The schema now accepts a relative bound with an absolute floor, so
  the change is a one-line edit to a declaration rather than a change to a shared
  contract — but it is **deliberately not made**, because the coverage floor rejects
  exactly the small cross-sections that make the case for it, and recalibrating
  against the one admitted cross-section is the failure the change was meant to
  prevent. See `DATA_QUALITY_DECISIONS.md`.
- **The Treasury settlement series aggregates decisions it does not implement.**
  Security type, tenor, and Fed SOMA add-ons are summed into one series. The source
  limitation now says so, and names the fields that are present in the snapshot and
  unread, so the split needs no new download. The split itself is not done, and
  nothing yet tests whether the simplification affects conclusions.
- **The never-revised claim is prose.** The field-level release lag is licensed by
  a `revision_evidence` string. The comparison behind it was done outside the
  repository, so if a future vintage restated an observation, nothing here would go
  red. Committing the vintages and recomputing the comparison in a test is briefed
  and not built.

## Work required before empirical claims

1. Run the panel build against the fetched snapshots and freeze the result. The
   join exists; nothing has been produced with it. This is what ends the synthetic
   era, and everything below reads differently once a panel is on disk.
2. Backfill and freeze the SEC Form N-MFP archive history, applying the coverage
   floor to every reference date found rather than trusting an archive's contents,
   refusing any archive whose schema the adapter cannot read faithfully, and proving
   that overlapping archives, amendments and straggler filings do not double count.
3. Establish whether `mmf_on_rrp` is derived correctly, against a period in which
   money funds held Fed reverse repo at scale, and make an absent declared field
   distinguishable from a parsing failure.
4. Resolve the N-MFP identity-tolerance and Treasury-settlement aggregation
   decisions recorded in `DATA_QUALITY_DECISIONS.md`. The tolerance decision waits
   on item 2: it cannot honestly be calibrated against one cross-section.
5. Replace the never-revised prose with committed vintages and a test that
   recomputes the comparison offline.
6. Extend the same freeze to the remaining sources, with a machine-readable quality
   report.
7. Add a threshold benchmark against the shared interface, and re-run the
   persistence-versus-ARX comparison on the built panel, where the result carries
   evidence.
8. Report the frozen event windows separately from rolling-origin evaluation.
9. Add a quantile machine-learning model only after the baselines are frozen.

## Who is responsible for what

The author holds research design, implementation, evaluation, and every claim on this
page. Nicholas Beroud is the project's finance collaborator, contributing repo- and
money-market domain expertise and the finance side of the research design: which of
the open decisions in `DATA_QUALITY_DECISIONS.md` are questions about markets rather
than about code, and what a series has to represent before it is worth fitting on.

The split is worth stating on a status page specifically, because the gaps listed
above are not all of one kind. Some are engineering — a join not yet run, a freeze not
yet taken. Others are finance judgments that no amount of test coverage will settle:
whether a summed settlement series can stand in for a collateral-supply channel,
whether an accounting identity means anything on a partial cross-section, what a
stress regime should be declared to be. Advisory input does not transfer
responsibility for any of them.

## Portfolio interpretation

The repository may accurately be described as a leakage-safe, point-in-time
financial research pipeline with a tested probabilistic evaluation harness, a
model interface with two implementers, purged rolling-origin evaluation of both,
and a benchmark that publishes a reproducible record of its own run. It should
not yet be described as a successful machine-learning forecast of repo stress. A
frozen funding panel now exists and the persistence benchmark has been measured
on it, so the phrase that stood here -- that no result rests on real data -- has
stopped being true. What has not happened is the part that would make it a
forecast: no challenger has been scored against that benchmark on real data, the
headline exceedance metric has not been taken on the panel at all, and the
monthly money-fund panel is still one cross-section rather than a series.

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
the committable half, and it reached nobody while it sat beside the panel.

`docs/runs/` was chosen over `metadata/panels/` -- which would have followed the
N-MFP archive-manifest precedent -- because `metadata/` is Track A's and a human
commit there while Track A's N-MFP packet is in flight is a conflict waiting to
happen. It is also outside `tests/test_docs_freshness.py`'s Markdown scope, and
it is where the records that cite the manifest land, so the panel and the numbers
measured on it sit together. It can move to `metadata/` once that packet is done.
Recorded here because a path chosen and unrecorded is the next session's
archaeology.
