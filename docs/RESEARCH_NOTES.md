# Research notes

Two things the status pages do not hold: what the published records say about
volatility and the tails, read in words, and the quantitative work on the repo market
this project sits next to. Every figure lives in the run records under [`runs/`](runs)
and in the generated block of the [README](../README.md); this page quotes none of
them, so a re-scored record cannot leave it stale.

## Volatility and the tails

Phase 2's exit criterion has two halves: beat persistence out of sample, and stay
calibrated in the tails. One model family has met the first half. None has met the
second, and the records show why it is the harder half.

1. **Every nominal 90% band is too narrow, the benchmark's included.** Persistence's
   band covers fewer outcomes than it promises, and the bootstrap interval around its
   realised coverage excludes the nominal probability, so the gap is a calibration
   finding rather than sampling luck ([`runs/backtest_persistence_mh61.json`](runs/backtest_persistence_mh61.json)).
2. **The most accurate model is the least honest about its range.** Gradient-boosted
   quantiles win on CRPS, but their band covers far fewer outcomes than persistence's,
   and their upper-tail pinball loss (quantile 0.95) is worse than persistence's
   ([`runs/backtest_gbm_mh61.json`](runs/backtest_gbm_mh61.json)). The accuracy is won
   in the body of the distribution, on ordinary days. The upper tail, where funding
   stress lives, is where the model is weakest.
3. **Honesty need not cost the edge.** Split-conformal calibration moves gbm's coverage toward
   nominal without reaching it, and its CRPS advantage over persistence stops being
   distinguishable from zero
   ([`runs/backtest_gbm_conformal_mh61.json`](runs/backtest_gbm_conformal_mh61.json),
   [`runs/compare_persistence_vs_gbm_conformal_mh61_crps.json`](runs/compare_persistence_vs_gbm_conformal_mh61_crps.json)).
   Cross-conformal calibration, which keeps the full fit's interior and calibrates the
   band over purged blocks, shows the trade-off was not forced: its band covers a little
   more than it promises, and its CRPS advantage stays distinguishable from zero
   ([`runs/backtest_gbm_cross_conformal_mh61.json`](runs/backtest_gbm_cross_conformal_mh61.json),
   [`runs/compare_persistence_vs_gbm_cross_conformal_mh61_crps.json`](runs/compare_persistence_vs_gbm_cross_conformal_mh61_crps.json)).
   Its upper-tail pinball loss is still worse than persistence's.
4. **Volatility clustering adds nothing measurable.** A GARCH(1,1) conditional-volatility
   feature leaves gbm's CRPS against persistence indistinguishable from gbm without it,
   calibrated or not
   ([`runs/compare_persistence_vs_gbm_garch11_mh61_crps.json`](runs/compare_persistence_vs_gbm_garch11_mh61_crps.json),
   [`runs/compare_persistence_vs_gbm_garch11_conformal_mh61_crps.json`](runs/compare_persistence_vs_gbm_garch11_conformal_mh61_crps.json)).
   Longer windows of lagged spread changes do not move it either.
5. **Regime-switching models do worse, not better.** The threshold (SETAR-type) models,
   which change dynamics when the spread or SOFR volume crosses a level, lose to
   persistence on either regime variable, and clearly so on the spread
   ([`runs/compare_persistence_vs_threshold_regime_spread_mh61_crps.json`](runs/compare_persistence_vs_threshold_regime_spread_mh61_crps.json),
   [`runs/compare_persistence_vs_threshold_regime_volume_mh61_crps.json`](runs/compare_persistence_vs_threshold_regime_volume_mh61_crps.json)).
6. **Stress probabilities carry skill at the shoulder and none in the tail.** The
   climatology control scores exactly no skill, as it must
   ([`runs/exceedance_funding_climatology.json`](runs/exceedance_funding_climatology.json)),
   and the conditional model scored against it beats it only at the lowest declared
   threshold; at the highest, climatology wins and the fitted probabilities carry no
   information at all
   ([`runs/exceedance_gbm_mh61.json`](runs/exceedance_gbm_mh61.json), with the figures
   in the generated tail section of the README). That is the same boundary the four
   findings above run into, met from the other side.

**Interpretation — a reading, not a tested claim.** The pattern fits what the
structural work below finds: repo spikes arrive with the calendar and the balance
sheet — tax dates, Treasury coupon settlements, quarter-ends, reserves drifting toward
scarcity — rather than out of yesterday's turbulence. A volatility feature can learn
that rough days follow rough days; it cannot learn that a mid-September settlement is
about to meet a reserve level that has quietly become scarce. Two consequences follow
for the plan. The tail inputs worth adding are calendar and reserve-scarcity
variables (Phases 3 and 4), not further transforms of past volatility. And accuracy on
ordinary days is no evidence about the tails, which is why the exit criterion names
both halves.

## Related quantitative work

Most quantitative work on repo stress is structural: it explains an episode after the
fact, often with supervisory, bank-level or bilateral repo data that was not public at
the time. The forecasting literature on overnight rates mostly predates SOFR, or models
the term structure in continuous time. This project asks a narrower question — a
next-day distribution of the SOFR–IORB spread, built from public data as it was
available, scored out of sample against a benchmark — and we found no published model
of that exact form. That is a statement about our search, not a claim of novelty.

### Structural models of repo stress and reserve demand

- Afonso, Cipriani, Copeland, Kovner, La Spada and Martin (2021), [*The Market Events of
  Mid-September 2019*](https://www.newyorkfed.org/research/epr/2021/epr_2021_market-events_afonso.html),
  FRBNY *Economic Policy Review* 27(2). The September 2019 spike as a coincidence of
  Treasury settlement, corporate-tax outflows and reserve scarcity, reconstructed from
  granular data. Explains one episode; does not forecast.
- Copeland, Duffie and Yang (2021), [*Reserves Were Not So Ample After
  All*](https://www.nber.org/papers/w29090), NBER Working Paper 29090. Ties the spike to
  how reserves were distributed across banks and to intraday payment timing. The
  mechanism our calendar and reserve inputs are meant to proxy from public data.
- Paddrik, Young, Kahn, McCormick and Nguyen (2023), [*Anatomy of the Repo Rate Spikes
  in September 2019*](https://www.financialresearch.gov/working-papers/2023/04/25/anatomy-of-the-repo-rate-spikes-in-september-2019/),
  OFR Working Paper 23-04. Decomposes the spike across the repo network and dealer
  balance sheets using non-public transaction data.
- Avalos, Ehlers and Eren (2019), [*September stress in dollar repo markets: passing or
  structural?*](https://www.bis.org/publ/qtrpdf/r_qt1912v.htm), *BIS Quarterly Review*,
  December 2019. Balance-sheet constraints on the marginal lenders; narrative and
  aggregate, no backtest.
- Afonso, Giannone, La Spada and Williams (2022), [*Scarce, Abundant, or Ample? A
  Time-Varying Model of the Reserve Demand Curve*](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1019.pdf),
  FRBNY Staff Report 1019. A time-varying reserve demand curve estimated on daily data;
  the basis of the New York Fed's
  [reserve demand elasticity](https://www.newyorkfed.org/research/reserve-demand-elasticity)
  indicator, a candidate public input for the latent-reserves phase.
- Lopez-Salido and Vissing-Jorgensen (2023), [*Reserve Demand, Interest Rate Control,
  and Quantitative Tightening*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4371999).
  A nonlinear reserve demand curve that gauges distance to scarcity; structural, not a
  next-day forecast.

### Statistical models of overnight rates

- Hamilton (1996), [*The Daily Market for Federal Funds*](https://doi.org/10.1086/262016),
  *Journal of Political Economy* 104(1). Calendar and settlement-day effects in the daily
  funds rate, with conditional heteroskedasticity. The ancestor of the calendar reading
  above, from the pre-SOFR target regime.
- Bartolini, Bertola and Prati (2002), [*Day-to-Day Monetary Policy and the Volatility of
  the Federal Funds Interest Rate*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=880858),
  *Journal of Money, Credit and Banking*. Volatility of the overnight rate around
  reserve-settlement dates and the central bank's operating framework.
- Archontakis and Lemke (2008), [*Threshold Dynamics of Short-Term Interest
  Rates*](https://onlinelibrary.wiley.com/doi/10.1111/j.1468-0300.2008.00189.x),
  *Economic Notes* 37(1). A SETAR model of short-rate dynamics; the design behind this
  project's threshold challenger.
- Backwell and Hayes (2022), [*Expected and Unexpected Jumps in the Overnight
  Rate*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3989108), working paper.
  Separates scheduled from unscheduled jumps in an overnight rate for the LIBOR transition.
- Fang, Yeh, He and Lin (2024), [*What Drives Jumps in the Secured Overnight Financing
  Rate?*](https://www.sciencedirect.com/science/article/abs/pii/S0927538X24001434),
  *Pacific-Basin Finance Journal* 86. SOFR spikes in a jump-diffusion term-structure model;
  continuous-time and in-sample, where this project is next-day and out of sample.

### Methods this project borrows

- Gneiting and Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and
  Estimation*, *Journal of the American Statistical Association* 102(477): CRPS and the
  case for scoring a forecast as a distribution.
- Romano, Patterson and Candès (2019), *Conformalized Quantile Regression*, NeurIPS; and
  Barber, Candès, Ramdas and Tibshirani (2021), *Predictive Inference with the
  Jackknife+*, *Annals of Statistics* 49(1): the split-conformal and cross-conformal
  (CV+) calibration of gbm's quantile band.
- Stankevičiūtė, Alaa and van der Schaar (2021), [*Conformal Time-Series
  Forecasting*](https://proceedings.neurips.cc/paper/2021/file/312f1ba2a72318edaaa995a67835fad5-Paper.pdf),
  NeurIPS: conformal coverage when observations are ordered in time.

### Public monitors

- Office of Financial Research, [Short-term Funding
  Monitor](https://www.financialresearch.gov/short-term-funding-monitor/): public repo
  rates, volumes and money-fund data, overlapping this project's inputs. A monitor, not
  a forecast.
- Monin (2019), [*The OFR Financial Stress Index*](https://www.financialresearch.gov/working-papers/files/OFRwp-17-04_The-OFR-Financial-Stress-Index.pdf),
  *Risks* 7(1). A daily contemporaneous stress index across markets, much broader than
  repo funding.
