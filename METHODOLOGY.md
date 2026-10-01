# Academic methodology

## Status of this work

This is an academic exercise. Its purpose is to demonstrate that a forecasting claim
about a funding market can be made *defensibly* — with point-in-time provenance,
declared availability, honest holdouts, and evaluation that cannot quietly reward a
leak. It is not a production system and produces no investment advice. Where the
repository has not yet earned a claim, the correct entry in these documents is that
it has not, and that convention is enforced rather than left to editorial care.

## Contributors and their roles

| Person | Role |
|---|---|
| Eleonora Björnberg | Author. Designed the model, the methodology and the workflow: research design, implementation, evaluation protocol, and academic responsibility for any submission based on this work. |
| Nicholas Beroud | Advisor. Selected the data the model is built on and settled what it means: which public series carry the funding market's mechanics, which quantities are economically meaningful, and which open decisions are finance questions rather than engineering ones. |

Ownership divides by kind of judgment. What the project measures, and what a
measurement means, answer to the advisor; how it is modelled and evaluated,
and whether a result has been earned, answer to the author. No result is certified by
either judgment alone.

## Research question

Can publicly observable funding, reserve, Treasury-settlement, dealer, money-fund,
and calendar variables forecast the next-day distribution of Treasury repo-market
pressure, including transitions into the upper tail?

The primary outcome is the SOFR spread to the administered reserve rate. Secondary
outcomes are SOFR dispersion, volume, and a pre-declared stress indicator. The headline
target is the probability that the spread is at least +5 bp (and +10 bp) on the scored
day.

**The information set.** "Next-day" means a forecast made at 16:00 on the business day
before the scored day. The as-of information rule
([`docs/decisions/information-set.md`](docs/decisions/information-set.md)) reads each
input at its latest value public at that instant, and the records in `docs/runs/` are
scored under it. The records published before it read every input at the row dated at
least seven calendar days earlier, which never leaks and is about a week stale; they are
archived in `docs/runs/archive/pre-asof/`, and the readings of them below are readings of
that stale design. [`docs/pivot/lag-assessment.md`](docs/pivot/lag-assessment.md) has the
finding and its reach.

## Claims the first version may support

- Predictive associations under rolling out-of-sample evaluation.
- Calibration of next-day conditional distributions, once they are scored under the as-of
  information rule.
- Robustness of forecasts to alternative public-data transformations.
- Scenario sensitivity under explicitly declared assumptions.

## Claims it may not support

- Causal effects of reserves, regulation, or Federal Reserve facilities without a
  separate identification strategy.
- Exact institution-level liquidity buffers from aggregate data.
- The true bilateral funding or collateral network.
- Reliable probabilities for unprecedented stress outside the support of the data.

## Reproducibility protocol

1. Save each raw response immutably.
2. Record retrieval time, complete request URL, byte count, and SHA-256 digest.
3. Keep raw and processed datasets out of Git; commit code and metadata.
4. Record release lags and revision behavior for every feature.
5. Build point-in-time panels using only information available at forecast creation.
6. Fit imputation and normalization inside each training window.
7. Use rolling-origin evaluation and untouched event holdouts.
8. Compare all models with persistence and transparent econometric baselines.
9. Publish uncertainty, ablations, and failed specifications alongside final results.

## Missing information

Missing aggregates may be imputed with time-aware statistical models. Missing
counterparty networks and collateral paths will be represented by posterior ensembles
subject to accounting, relationship, timing, and collateral constraints. Systemic-risk
results will be labelled robust only when they persist across plausible completions.

## Standard of evidence

A claim in this repository is admissible only when the artifact that supports it is
identifiable: a commit, a snapshot digest, a declared feature set, and a run record.
Prose is not evidence, and a passing suite is evidence about software, not about
markets. Two conventions follow, and both are enforced by tests rather than by
diligence:

- No published document transcribes a measurement that rots — a test count, or a
  hand-typed date. The commit is the timestamp.
- A quantity that could not be computed is recorded as absent rather than defaulted,
  because a default is indistinguishable from a measurement once it is written down.

## Where the work stands

The current phase is not written on this page. It is generated from `PLAN.md` into the
status block at the top of [`README.md`](README.md) and into
[`docs/status.json`](docs/status.json), and the figures are generated from the run records
into the README's key-findings block. This page carries what those blocks cannot: what
the harness guarantees, what is still open, and how to read the records.
`docs/EXECUTIVE_SUMMARY.md`, `docs/PROJECT_STATUS.md` and `docs/RESEARCH_NOTES.md` were
folded into this page and the README; their history is in git.

## What the harness guarantees

These hold independently of the information-set correction above. They are properties of
the data layer and the evaluation code, and each is held by a test rather than by prose.

- **A value is read only once it was public.** Every field declares its release lag, its
  availability time and its timezone in `metadata/sources.json`. A latest-vintage source
  may back a point-in-time feature only for a field declared never revised, and only with
  evidence attached. Leakage guards raise `LookAheadError`; they do not quietly produce a
  better score.
- **The panel is point in time and reproducible.** A cell carries the latest vintage
  available at the build's declared cutoff. There is no forward fill: a reference date with
  no observation is a hole, counted and left empty, except the declared Treasury settlement
  columns, which read `0.0` on a business day inside the snapshot's coverage. The published
  panel rebuilds from tracked fixtures and is checked against its digest
  (`REPRODUCIBILITY.md`).
- **The panel's administered leg is spliced.** IORB begins 2021-07-29; IOER, which it
  replaced, supplies everything before. Without the splice the panel would begin in July
  2021 and contain no stress episode at all.
- **Absence is typed.** A missing value, a declared structural zero, an excluded
  cross-section and a withheld field are different things, and each carries its reason into
  the record. A quantity that could not be computed is recorded as absent rather than
  defaulted, and no regressor becomes `0.0` by accident.
- **Fitted state comes from the training window alone.** Imputation means, regressor names
  and interval laws are fitted per fold; a mutation that widens the window to the whole
  frame is caught by a named test.
- **Stress probabilities come from the predictive distribution**, not from a separately
  fitted classifier: at a declared level `q`, the exceedance reported at that quantile is
  `1 - q`, and a conformance test asserts it for every implementer of the forecast
  interface.
- **The two holdout roles stay apart.** Rolling-origin scoring and the frozen, checksummed
  September 2019 and March 2020 event windows are distinct in code and in reporting.
- **A run publishes a record, not a printout.** `backtest`, `compare` and
  `exceedance-backtest` write the declared feature set, the sources, the decision time, the
  panel's digest and extent, the folds, and the metrics unrounded, with stationary-bootstrap
  intervals where they are defined.
- **SEC Form N-MFP cross-sections are admitted or refused per vintage.** An entity-count
  floor declared per era refuses under-covered cross-sections; a split month-end is assembled
  as one cross-section; duplicate and amended filings are resolved across the whole archive
  set before aggregation; and each exclusion carries its reason.

## Known limitations

Each of these is stated because it is easy to mistake for something stronger. Several are
checked by `tests/test_docs_freshness.py`, which fails if a limitation that still holds
stops being published here, or if one that has been repaired is still published.

- **The information set is stale in every published record.** Above, and in
  `docs/pivot/lag-assessment.md`. The records stay valid as measurements of the conservative
  design and do not measure a forecast made from what was public the afternoon before.
- **Rates volatility and the cash-futures basis are not in the panel.** The MOVE
  index is licensed, and the Treasury cash-futures basis needs licensed futures prices;
  this repository takes public sources only. A public proxy for each is open.
- **The N-MFP identity tolerance is a single absolute bound** and after calibration it
  stays one, by decision (`docs/DATA_QUALITY_DECISIONS.md`). It still refuses a majority
  of the cross-sections it checks. The reason is a finding rather than a bound problem:
  from 2024-06 to 2026-02, starting exactly at the declared `n_mfp2`-to-`n_mfp3` form
  boundary, assets exceed liabilities plus net assets in every month, and a bound sized to
  admit that would admit a defect that starts and stops on a form-version boundary.
  `metadata/sources.json`'s `tolerance_note` carries the derivation.
- **The pre-2016 N-MFP balance sheet is missing two of three left-hand terms.** Those
  months are reported as unevaluable rather than counted as holding.
- **Part of the command line is unpublished.** `backfill-nmfp` and `event-holdout` ship
  with no invocation any published document tells a reader to run. `backfill-nmfp` needs a
  route to the SEC; `event-holdout` needs the full panel, which a clone can now rebuild, so
  what keeps it unpublished is its journal write, not a missing file.
- **The never-revised claim is prose.** The field-level release lag is licensed by a
  `revision_evidence` string. The comparison behind it was done outside the repository, so
  a future vintage that restated an observation would turn nothing red.
- **No event-window result is claimed.** The event-window evaluator cannot yet express the
  published model's calibration and tail settings.
- **Everything is a backtest.** No forecast here has been made against a day that had not
  already happened.

## Reading the pre-as-of records

*Pre-as-of; re-score pending.* This is what the published records say about volatility and
the tails, read in words. Every one of these readings rests on the stale information set,
and `docs/pivot/lag-assessment.md` lists them among the verdicts to re-open after the
re-score. They are kept because the re-score will be read against them. No figure is
quoted here; the figures are in the run records under [`docs/runs/`](docs/runs) and in the
README's generated blocks.

1. **Every nominal 90% band was too narrow, the benchmark's included.** Persistence's band
   covered fewer outcomes than it promised, and the bootstrap interval around its realised
   coverage excluded the nominal probability.
2. **The most accurate model was the least honest about its range.** Gradient-boosted
   quantiles won on CRPS, but their band covered far fewer outcomes than persistence's, and
   their upper-tail pinball loss was worse. The accuracy was won on ordinary days.
3. **Calibration need not have cost the edge.** Split-conformal calibration moved gbm's
   coverage toward nominal and lost the CRPS advantage; cross-conformal calibration kept
   both, while the upper-tail pinball loss stayed worse than persistence's.
4. **Volatility clustering added nothing measurable** (a GARCH(1,1) feature, longer windows
   of lagged spread changes), and **regime-switching models did worse** (threshold models on
   either regime variable).
5. **Stress probabilities carried skill at the shoulder and none in the tail.** The
   climatology control scored exactly no skill, as it must; the conditional model beat it
   only at the lowest declared threshold.

*A reading, not a tested claim:* repo spikes arrive with the calendar and the balance sheet
— tax dates, Treasury settlements, quarter-ends, reserves drifting toward scarcity — rather
than out of yesterday's turbulence. That is why the pivot's plan puts scheduled inputs and a
reserve-scarcity state ahead of further transforms of past volatility. The scouting run
behind the lag finding also suggests part of the tail failure was the week-old information
set itself; the re-score decides.

## Related quantitative work

Most quantitative work on repo stress is structural: it explains an episode after the fact,
often with supervisory or bilateral data that was not public at the time. The forecasting
literature on overnight rates mostly predates SOFR, or models the term structure in
continuous time. This project asks a narrower question — a next-day distribution and
pressure probability for the SOFR–IORB spread, from public data as it was available, scored
out of sample against fixed benchmarks — and we found no published model of that exact
form. That is a statement about our search, not a claim of novelty.
[`docs/pivot/literature.md`](docs/pivot/literature.md) lists the methods and free data the
redesign borrows.

**Structural models of repo stress and reserve demand**

- Afonso, Cipriani, Copeland, Kovner, La Spada and Martin (2021), [*The Market Events of
  Mid-September 2019*](https://www.newyorkfed.org/research/epr/2021/epr_2021_market-events_afonso.html),
  FRBNY *Economic Policy Review* 27(2). The September 2019 spike as a coincidence of
  Treasury settlement, corporate-tax outflows and reserve scarcity.
- Copeland, Duffie and Yang (2021), [*Reserves Were Not So Ample After
  All*](https://www.nber.org/papers/w29090), NBER Working Paper 29090. The distribution of
  reserves across banks and intraday payment timing.
- Paddrik, Young, Kahn, McCormick and Nguyen (2023), [*Anatomy of the Repo Rate Spikes in
  September 2019*](https://www.financialresearch.gov/working-papers/2023/04/25/anatomy-of-the-repo-rate-spikes-in-september-2019/),
  OFR Working Paper 23-04. The spike across the repo network, from non-public data.
- Avalos, Ehlers and Eren (2019), [*September stress in dollar repo markets: passing or
  structural?*](https://www.bis.org/publ/qtrpdf/r_qt1912v.htm), *BIS Quarterly Review*,
  December 2019. Balance-sheet constraints on the marginal lenders.
- Afonso, Giannone, La Spada and Williams (2022), [*Scarce, Abundant, or Ample? A
  Time-Varying Model of the Reserve Demand Curve*](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1019.pdf),
  FRBNY Staff Report 1019. The basis of the New York Fed's
  [reserve demand elasticity](https://www.newyorkfed.org/research/reserve-demand-elasticity)
  indicator, a candidate input for the scarcity state.
- Lopez-Salido and Vissing-Jorgensen (2023), [*Reserve Demand, Interest Rate Control, and
  Quantitative Tightening*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4371999).
  A nonlinear reserve demand curve that gauges distance to scarcity.

**Statistical models of overnight rates**

- Hamilton (1996), [*The Daily Market for Federal Funds*](https://doi.org/10.1086/262016),
  *Journal of Political Economy* 104(1). Calendar and settlement-day effects in the daily
  funds rate.
- Bartolini, Bertola and Prati (2002), [*Day-to-Day Monetary Policy and the Volatility of
  the Federal Funds Interest Rate*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=880858),
  *Journal of Money, Credit and Banking*.
- Archontakis and Lemke (2008), [*Threshold Dynamics of Short-Term Interest
  Rates*](https://onlinelibrary.wiley.com/doi/10.1111/j.1468-0300.2008.00189.x),
  *Economic Notes* 37(1). The design behind the threshold challenger.
- Backwell and Hayes (2022), [*Expected and Unexpected Jumps in the Overnight
  Rate*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3989108), working paper.
- Fang, Yeh, He and Lin (2024), [*What Drives Jumps in the Secured Overnight Financing
  Rate?*](https://www.sciencedirect.com/science/article/abs/pii/S0927538X24001434),
  *Pacific-Basin Finance Journal* 86. Continuous-time and in-sample, where this project is
  next-day and out of sample.

**Methods borrowed**

- Gneiting and Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*,
  *Journal of the American Statistical Association* 102(477): CRPS, and scoring a forecast
  as a distribution.
- Romano, Patterson and Candès (2019), *Conformalized Quantile Regression*, NeurIPS; and
  Barber, Candès, Ramdas and Tibshirani (2021), *Predictive Inference with the Jackknife+*,
  *Annals of Statistics* 49(1): split-conformal and cross-conformal (CV+) calibration.
- Stankevičiūtė, Alaa and van der Schaar (2021), [*Conformal Time-Series
  Forecasting*](https://proceedings.neurips.cc/paper/2021/file/312f1ba2a72318edaaa995a67835fad5-Paper.pdf),
  NeurIPS.
- Giannone, Reichlin and Small (2008), and Bańbura et al. (2013): the ragged-edge
  information set of real-time forecasting, which is the as-of rule.

**Public monitors**

- Office of Financial Research, [Short-term Funding
  Monitor](https://www.financialresearch.gov/short-term-funding-monitor/): public repo
  rates, volumes and money-fund data. A monitor, not a forecast.
- Monin (2019), [*The OFR Financial Stress Index*](https://www.financialresearch.gov/working-papers/files/OFRwp-17-04_The-OFR-Financial-Stress-Index.pdf),
  *Risks* 7(1).

## Where the run records live

`docs/runs/` holds the published records and the frozen panel's original build manifest.
The panel itself is not tracked; it rebuilds from the tracked inputs, and the manifest that
carries its digest is `metadata/funding_panel_manifest.json`, against which
`verify-panel` checks a rebuilt panel. Under the pivot's plan the records scored under the
old information set move to `docs/runs/archive/pre-asof/` in the re-scoring pull request;
records are never edited in place.

## Literature access

The project uses publisher-open articles, working papers, author manuscripts,
government publications, and institutional repositories. It does not circumvent
paywalls or access controls. Citations should identify the version actually analyzed.

