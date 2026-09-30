# Literature and similar projects (scan, 30 Sep 2026)

This scan was done by a delegated search agent. It reports that every URL was fetched or returned by search on
30 Sep 2026. Summaries come from page text, so read the primary source before citing it. The only item added from
general knowledge is the nowcasting "ragged edge" literature. It is marked below.

## Reserve demand and money-market pressure

| Item | URL | What it does | What we can borrow |
|---|---|---|---|
| Afonso, Giannone, La Spada & Williams, "Scarce, Abundant, or Ample?", NY Fed SR 1019 (2022, rev. Nov 2025) | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1019.pdf | A time-varying reserve-demand slope; satiation at about 12–13% of bank assets | Reserves/bank assets and the slope as a regime state |
| NY Fed Reserve Demand Elasticity (since Oct 2024) | https://www.newyorkfed.org/research/reserve-demand-elasticity | A monthly, real-time elasticity from 2010 | A slow regime covariate. Check whether it can be downloaded |
| Clouse, Infante & Senyuz, FEDS Note (Jan 2025) | https://www.federalreserve.gov/econres/notes/feds-notes/market-based-indicators-on-the-road-to-ample-reserves-20250131.html | Market-based ampleness indicators | Percentile − IORB spreads; a 15-day rolling spread SD |
| Lopez-Salido & Vissing-Jorgensen (2023) | https://www.ecb.europa.eu/press/conferences/shared/pdf/20231004_mon_pol_conference/Lopez_Salido_paper.pdf | Reserve demand including ON RRP (monthly IV) | A convex prior in logs or ratios |
| Copeland, Duffie & Yang, SR 974; Ferris, Rose & Tase, FEDS Note (Jul 2025) | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr974.pdf ; https://www.federalreserve.gov/econres/notes/feds-notes/what-can-public-fedwire-payments-data-tell-us-about-ample-reserves-20250718.html | Quantile regression and probit on SOFR − IOR, driven by payment timing | The closest methodological match. Public Fedwire data is monthly |
| Sep 2019: Anbil, Anderson & Senyuz; Afonso et al. (EPR); BIS QR | https://www.federalreserve.gov/econres/notes/feds-notes/what-happened-in-money-markets-in-september-2019-20200227.html ; https://www.newyorkfed.org/research/epr/2021/epr_2021_market-events_afonso.html ; https://www.bis.org/publ/qtrpdf/r_qt1912v.htm | Tax date × settlement × low reserves | Interaction features |
| Quarter-ends: Munyan (OFR WP); Correa, Du & Liao (NBER); Bostrom et al., FEDS Note (Jun 2025) | https://www.financialresearch.gov/working-papers/files/OFRwp-2015-22_Repo-Arbitrage.pdf ; https://www.nber.org/papers/w27491 ; https://www.federalreserve.gov/econres/notes/feds-notes/what-happens-on-quarter-ends-in-the-repo-market-20250606.html | Window dressing by foreign dealers | Quarter-end and year-end dummies × tightness |
| Late 2025 to 2026, desk: Perli (Nov 2025, Mar 2026); Teller Window posts (Dec 2025, Jan 2026) | https://www.newyorkfed.org/newsevents/speeches/2025/per251112 ; https://tellerwindow.newyorkfed.org/2025/12/23/standing-repo-operations-in-the-federal-reserves-monetary-policy-implementation-framework/ ; https://tellerwindow.newyorkfed.org/2026/01/16/how-monetary-policy-tools-helped-limit-money-market-pressures-at-year-end | QT ended 1 Dec 2025; SRP changes; reserve-management purchases | Regime-break dates |
| Anbil, Anderson, Cordes & Ruprecht, FEDS Note (Aug 2026); IMF WP/25/127; Dallas Fed (Feb 2026) | https://www.federalreserve.gov/econres/notes/feds-notes/repo-markets-and-the-feds-balance-sheet-implications-for-monetary-policy-implementation-20260826.html ; https://www.imf.org/-/media/files/publications/wp/2025/english/wpiea2025127-print-pdf.pdf ; https://www.dallasfed.org/research/economics/2026/0212-levymccormick-repotiming | Issuance sensitivity jumps below 10% Fed liquidity/GDP; about +2 bp per +$100bn TGA | Net issuance × liquidity; TGA change × reserves |

## Forecasting methodology

| Item | URL | What we can borrow |
|---|---|---|
| *(General knowledge)* Giannone, Reichlin & Small (2008), JME; Bańbura, Giannone, Modugno & Reichlin (2013), Handbook of Economic Forecasting | — | The "ragged edge": each series read at its own latest release. This is the as-of fix |
| Adrian, Boyarchenko & Giannone, "Vulnerable Growth" (AER 2019); Plagborg-Møller et al. (Brookings) | https://ideas.repec.org/a/aea/aecrev/v109y2019i4p1263-89.html ; https://www.brookings.edu/articles/when-is-growth-at-risk | A quantile grid smoothed to a distribution, giving P(≥ x). The caveat is that financial variables add little to the tail |
| Romano, Patterson & Candès, CQR (2019); Barber et al., jackknife+/CV+ (2021) | https://papers.nips.cc/paper/8613-conformalized-quantile-regression ; https://candes.su.domains/publications/downloads/Jackknife+.pdf | What we already use |
| Gibbs & Candès, ACI (2021); DtACI (JMLR 2024) | https://arxiv.org/abs/2106.00170 ; https://jmlr.org/beta/papers/v25/22-1218.html | Online α updating under regime shift |
| Angelopoulos, Candès & Tibshirani, conformal PID (2023) | https://arxiv.org/abs/2307.16895 ; https://github.com/aangelopoulos/conformal-time-series | A calendar scorecaster (MIT code) |
| Barber et al., "Beyond exchangeability" (AoS 2023) | https://arxiv.org/abs/2202.13415 | Recency or regime weights on calibration scores |
| Gibbs, Cherian & Candès, conditional guarantees | https://arxiv.org/abs/2305.12616 ; https://github.com/jjcherian/conditional-conformal | Coverage by group: calendar type × regime |
| Xu & Xie, EnbPI; MAPIE | https://proceedings.mlr.press/v139/xu21h.html ; https://mapie.readthedocs.io/en/latest/ | Baseline comparisons |
| Alessi & Detken (2011); Sarlin (2013); Drehmann & Juselius (2014) | https://econpapers.repec.org/RePEc:eee:poleco:v:27:y:2011:i:3:p:520-533 ; https://www.sciencedirect.com/science/article/abs/pii/S0165176513000025 ; https://ideas.repec.org/p/bis/biswps/421.html | Early-warning evaluation: AUROC, usefulness, lead time |
| Dimitriadis, Gneiting & Jordan, CORP (PNAS 2021); Gneiting & Raftery (2007) | https://arxiv.org/abs/2008.03033 ; https://scores.readthedocs.io/en/stable/tutorials/Isotonic_Regression_And_Reliability_Diagrams.html | Reliability diagrams and the Brier decomposition |

## Similar code, and free data

| Item | URL | Note |
|---|---|---|
| `seiche` (GitHub) | https://github.com/beepboop2025/seiche | The closest project: P(SOFR − IORB ≥ 2/5/10/20 bp) from a calendar, walk-forward. Its README says the ML does not beat climatology. It is unreviewed and AGPL, so take ideas only |
| OFR Short-term Funding Monitor + API | https://www.financialresearch.gov/short-term-funding-monitor/ ; https://data.financialresearch.gov/v1/metadata/mnemonics | Daily repo segment series and MMF holdings. Watch the preliminary and final vintages |
| OFR Financial Stress Index | https://www.financialresearch.gov/financial-stress-index/ | A cross-asset covariate |
| NY Fed Markets Data API | https://markets.newyorkfed.org/static/docs/markets-api.html | SOFR and EFFR 1st/99th percentiles; repo operations, including SRF |
| Treasury FiscalData API | https://fiscaldata.treasury.gov/api-documentation/ | Daily TGA from the DTS; auctions with issue dates |
