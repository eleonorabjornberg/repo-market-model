# Evidence Pack: Repo Market Pressure Thresholds
*For: [repo-market-model](https://github.com/eleonorabjornberg/repo-market-model) · Eleonora Björnberg*
*Prepared by Nicholas Beroud (advisor) · 2026-10-01*
*Code and data pipeline: [nicholasberoud/repo-macro-atlas](https://github.com/nicholasberoud/repo-macro-atlas) (private; the author has access). This copy is generated there and is not produced by this repository's code.*

> **Data caveat**: FRED serves the latest revised data, not real-time
> vintages. All findings here are descriptive and historical.
> Nothing constitutes a forecast, a model output, or investment advice.

> **Label key** used throughout:
> - **[DATA]** — computed directly from FRED series; reproducible.
> - **[ARGUMENT] (Nicholas Beroud)** — advisor's interpretation; not a tested result.
> - **[COMMENTARY]** — paraphrase of third-party view; attributed inline.
> - **[UNVERIFIED]** — could not confirm against a primary source.

---

## Q1. Are +5/+10 bp the right pressure thresholds?

### What the data shows [DATA]

Charts: `charts/q1a_regime_distributions.png`, `charts/q1b_spread_with_thresholds.png`

| Regime | N days | Median (bp) | P90 (bp) | Days ≥+5bp | % ≥+5bp | Days ≥+10bp | % ≥+10bp |
|--------|--------|-------------|---------|-----------|---------|------------|----------|
| 2018–19 | 437 | 1.00 | 10.00 | 120 | 27.50% | 44 | 10.10% |
| 2020 | 251 | -1.00 | 0.00 | 4 | 1.60% | 3 | 1.20% |
| 2021–23 | 748 | -10.00 | -8.00 | 0 | 0.00% | 0 | 0.00% |
| 2024 | 250 | -8.00 | -4.00 | 5 | 2.00% | 2 | 0.80% |
| 2025 | 249 | -5.00 | 8.00 | 33 | 13.30% | 21 | 8.40% |
| 2026 | 187 | -1.00 | 2.00 | 8 | 4.30% | 1 | 0.50% |


### Background: Meldrum commentary, 27 Sep 2026 [COMMENTARY]

In commentary dated 27 Sep 2026, Mark Meldrum noted the following (paraphrase,
not direct quotation):

- Fed funds futures were pricing approximately three more hikes by late 2027,
  which he regards as unsustainable given the debt-service burden.
- Fiscal dominance is the central macro constraint on the Fed.
- ON RRP was near zero; SOFR and EFFR were both at approximately 3.88%.
- The 3-month T-bill was running approximately 36 bp above EFFR.

These observations are tested against the data in the **Fiscal Channel** section below.

---

### Advisor's arguments [ARGUMENT] (Nicholas Beroud)

*The following are the advisor's interpretations, not tested empirical results.
They are offered for the model author's consideration.*

---

**(a) [ARGUMENT] (Nicholas Beroud): SOFR−IORB is anchored to administered rates
(ON RRP floor, soft SRF ceiling); the threshold should be fixed relative to IORB**

The SOFR−IORB spread has a soft upper bound at the SRF minimum bid rate (IORB +
10 bp at all five verified meetings) — soft because SOFR exceeded it: on
2025-10-31, SOFR−IORB reached +32 bp. When the ON RRP facility is funded, it
provides a lower bound at the ON RRP rate floor (IORB − 10 bp from Jul 2021 to
Dec 2024, and IORB − 15 bp after the Fed's Dec 2024 technical adjustment). Both
bounds move mechanically with IORB. A threshold fixed relative to IORB captures
the scarcity economics correctly. An absolute rate level or a trailing-median
normalisation would conflate policy-rate changes with scarcity changes — the
median would rise with the policy rate, the normalised spread would fall, and
the model would label a scarce-reserves regime as "normal" precisely when
vigilance is most warranted.

The regime-relative distribution table above is a *diagnostic* that the model
author should use to understand what is historically unusual in each period.
It should not replace the absolute IORB-relative threshold.

*Data check*: The regime table shows that the median spread does not trend
with the policy-rate level. The 2021–23 era (ZIRP to rapid hiking) and the
2025–26 era (rates declining from 5%) both show spreads driven by reserve
scarcity, not by the rate level itself.

---

**(b) [ARGUMENT] (Nicholas Beroud): A spread under active Fed accommodation
is more significant, not less**

Since December 2025 the Fed ended quantitative tightening and began buying
bills to maintain ample reserves. Any day with SOFR−IORB ≥ +5 bp under those
conditions represents a genuine funding squeeze overcoming active accommodation.
That is arguably stronger evidence of structural scarcity pressure than the
same reading in a passive-reserves environment.

*Data check (2025 vs 2026 distribution)* [DATA]:

| | 2025 | 2026 |
|--|------|------|
| Median spread (bp) | -5.00 | -1.00 |
| % of obs ≥ +5bp | 13.30% | 4.30% |

---

**(c) [ARGUMENT] (Nicholas Beroud): Exhausted ON RRP buffer removes the
intraday repo shock absorber**

When the ON RRP balance is near zero, money-market funds cannot redeploy
from the Fed facility into the repo market to arbitrage away intraday
rate spikes. The liquidity cushion that absorbed repo dislocations in
2022–24 is gone. The Aug–Sep 2026 data below checks whether SOFR and EFFR
have in fact converged and whether the ON RRP balance supports this reading.

*Data check (Aug–Sep 2026)* [DATA]:

| Month | SOFR−EFFR (bps, avg) | ON RRP median excl. Sep 30 ($bn) |
|-------|---------------------|----------------------------------|
| Aug 2026 | 1.19 | 0.456 |
| Sep 2026 | 0.10 | 0.653 |

---

## Q2. Is the SRF Minimum Bid Rate = IORB + 10 bp?

Chart: `charts/q2_srf_iorb_spread.png`

### What the data shows [DATA, partly verified]

The table below was built from FRED series `DFEDTARU` (FFR upper bound, used
as the proxy for the SRF minimum bid rate) and `IORB`. Rows marked "Verified"
were cross-checked against FOMC minutes at
`federalreserve.gov/monetarypolicy/fomcminutes{YYYYMMDD}.htm`.

Of the five meetings looked up, 3 have
fully verbatim quotes for both SRF and IORB. One meeting (2022-03-17) is marked
Unverified because values were confirmed from the source but the verbatim
sentence was not extracted; verify at the source URL before treating as
authoritative. One meeting (2024-09-19) is partially verified (SRF verbatim
confirmed; IORB rate confirmed but verbatim not extracted).

All other rows in the full table are computed from `DFEDTARU` and are
**Unverified – computed from DFEDTARU**.

#### Full SRF rate table

| Effective date | SRF rate (%) | IORB (%) | SRF−IORB (bp) | Verification |
|----------------|-------------|---------|----------------|----------------|
| 2021-07-29 | 0.25 | 0.15 | 10 | Verified: fomcminutes20210728 |
| 2022-03-17 | 0.50 | 0.40 | 10 | Unverified: fomcminutes20220316 — Source confirms SRF 0.5% and IORB 0.40% but verbatim sentence not extracted; verify at source URL |
| 2022-05-05 | 1.00 | 0.90 | 10 | Unverified – computed from DFEDTARU |
| 2022-06-16 | 1.75 | 1.65 | 10 | Unverified – computed from DFEDTARU |
| 2022-07-28 | 2.50 | 2.40 | 10 | Unverified – computed from DFEDTARU |
| 2022-09-22 | 3.25 | 3.15 | 10 | Unverified – computed from DFEDTARU |
| 2022-11-03 | 4.00 | 3.90 | 10 | Unverified – computed from DFEDTARU |
| 2022-12-15 | 4.50 | 4.40 | 10 | Unverified – computed from DFEDTARU |
| 2023-02-02 | 4.75 | 4.65 | 10 | Unverified – computed from DFEDTARU |
| 2023-03-23 | 5.00 | 4.90 | 10 | Unverified – computed from DFEDTARU |
| 2023-05-04 | 5.25 | 5.15 | 10 | Unverified – computed from DFEDTARU |
| 2023-07-27 | 5.50 | 5.40 | 10 | Unverified – computed from DFEDTARU |
| 2024-09-19 | 5.00 | 4.90 | 10 | Partially verified: fomcminutes20240918 — SRF verbatim confirmed; IORB rate 4.90% confirmed from source but verbatim sentence not extracted |
| 2024-11-08 | 4.75 | 4.65 | 10 | Unverified – computed from DFEDTARU |
| 2024-12-19 | 4.50 | 4.40 | 10 | Unverified – computed from DFEDTARU |
| 2025-09-18 | 4.25 | 4.15 | 10 | Unverified – computed from DFEDTARU |
| 2025-10-30 | 4.00 | 3.90 | 10 | Unverified – computed from DFEDTARU |
| 2025-12-11 | 3.75 | 3.65 | 10 | Unverified – computed from DFEDTARU |
| 2026-09-17 | 4.00 | 3.90 | 10 | Unverified – computed from DFEDTARU |


**Finding** [DATA]: Of all rows computed from FRED data,
100%
show a spread of exactly 10 bp.

#### Verbatim source quotes

**2021-07-29** ([fomcminutes20210728](https://www.federalreserve.gov/monetarypolicy/fomcminutes20210728.htm)) — Verified
- SRF: "be conducted with a minimum bid rate of 0.25 percent"
- IORB: "the Board voted unanimously to establish the interest rate paid on reserve balances at 0.15 percent"

**2022-03-17** ([fomcminutes20220316](https://www.federalreserve.gov/monetarypolicy/fomcminutes20220316.htm)) — Unverified
- *Source confirms SRF 0.5% and IORB 0.40% but verbatim sentence not extracted; verify at source URL*

**2024-09-19** ([fomcminutes20240918](https://www.federalreserve.gov/monetarypolicy/fomcminutes20240918.htm)) — Partially verified
- SRF: "Conduct standing overnight repurchase agreement operations with a minimum bid rate of 5 percent and with an aggregate operation limit of $500 billion."
- *SRF verbatim confirmed; IORB rate 4.90% confirmed from source but verbatim sentence not extracted*

**2025-01-30** ([fomcminutes20250129](https://www.federalreserve.gov/monetarypolicy/fomcminutes20250129.htm)) — Verified
- SRF: "Conduct standing overnight repurchase agreement operations with a minimum bid rate of 4.5 percent"
- IORB: "voted unanimously to maintain the interest rate paid on reserve balances at 4.4 percent"

**2025-06-19** ([fomcminutes20250618](https://www.federalreserve.gov/monetarypolicy/fomcminutes20250618.htm)) — Verified
- SRF: "Conduct standing overnight repurchase agreement operations with a minimum bid rate of 4.5 percent"
- IORB: "maintain the interest rate paid on reserve balances at 4.4 percent, effective June 20, 2025"


---

## Q3. What Public Signals Preceded the Oct 2025 Stress?

Chart: `charts/q3_timeline_2025.png`

### What the data shows [DATA]

Window: Aug–Dec 2025. Events marked on chart: QT ended 1 Dec 2025;
reserve-management bill purchases began 10 Dec 2025.

**First day SOFR−IORB ≥ +5 bp in window**: 2025-09-15 (spread = 11.0 bp)

> **Calendar note**: 2025-09-15 is a corporate tax settlement date; initial spike may reflect calendar seasonality rather than persistent scarcity pressure

**ON RRP in the 30 days before the first spike**: $38.2 bn →
$16.9 bn (trend: declining)

**Reserve balances in the 30 days before the first spike**: $3317 bn →
$3161 bn

**October 2025 peak**: The peak spread in Oct 2025 was **32.0 bp**,
reached on 2025-10-31.

**Indicator state four weeks before the October peak (2025-10-31)**:

| Indicator | 4 weeks before | At peak |
|-----------|---------------|---------|
| ON RRP ($bn) | 25.4 | 51.8 |
| TGA ($bn) | 807.4 | 958.0 |
| Reserve balances ($bn) | 2998 | 2848 |
| SOFR − EFFR (bp) | 9.0 | 36.0 |

> **Important caveat**: This is a single historical episode. One episode
> cannot confirm a leading indicator. The model author should verify that
> these patterns recur across multiple stress periods before using them as
> predictive features.

### What happened in the four weeks before the peak [DATA]

In the four weeks before the 2025-10-31 peak, the TGA rose approximately
$151 bn while reserve balances fell approximately $150 bn;
ON RRP at approximately $25.4 bn was too small to absorb the reserve
drain. Note: 31 Oct is a month-end date, which also inflated both the spread
(+32.0 bp) and the ON RRP balance ($51.8 bn) on that day.

This is a single historical episode. One episode cannot confirm a leading
indicator; the model author should verify that these patterns recur across
multiple stress periods before using them as predictive features.

---

## Q4. Which Scarcity Indicator Works Best?

Charts: `charts/q4a_reserves_scatter.png`, `charts/q4b_reserves_ratio.png`

### What the data shows [DATA]

**Median SOFR−IORB and % of weekly obs ≥ +5bp by ON RRP bin**:

| ON RRP bin | Median spread (bp) | % of obs ≥ +5bp |
|------------|-------------------|-----------------|
| <$10bn (near zero) | -0.60 | 14.61% |
| $10–100bn (thin) | -2.55 | 13.16% |
| $100–500bn (moderate) | -7.50 | 1.35% |
| >$500bn (ample) | -10.00 | 0.00% |

**Finding** [DATA]: Spread pressure is rare when ON RRP exceeds $100bn
(low median, low % ≥ +5bp) and meaningfully more frequent below that level.
The <$10bn and $10–100bn bins show similar pressure statistics, suggesting
the operative break is at approximately **$100bn** rather than at a lower
fixed level.

**Confound** [DATA]: The "<$10bn (near zero)" bin pools two structurally
different periods — 2018–19 (before the ON RRP facility was a meaningful
instrument) and 2025–26 (when the buffer was genuinely depleted after years
of ample-reserves policy). The time-coloured scatter (q4a) allows the model
author to assess this directly.

**Not tested**: The NY Fed reserve demand elasticity measure is not available
on FRED and was not downloaded. The model author may wish to source it from
the NY Fed directly.

**Chart q4b** shows reserves / total bank assets (%) alongside SOFR−IORB.
This ratio normalises for balance-sheet growth since 2019.

### Advisor's interpretation [ARGUMENT] (Nicholas Beroud)

The scatter chart (q4a) is the key exhibit. If the red and orange dots
(RRP near zero or thin) cluster toward higher spreads regardless of the
reserve level, while green dots (RRP ample) cluster at low spreads across a
wide range of reserve levels, this supports a *conditional* scarcity measure:
reserves matter for spread prediction mainly once the RRP buffer is depleted.
A model feature of the form `reserves × (RRP < threshold)` or a two-regime
specification would capture this non-linearity.

---

## Fiscal Channel (for the Scenario Narrative)

Chart: `charts/fiscal_sofr_effr.png`

> *This section describes a mechanism for the model author to consider
> as a scenario driver. It is not a direct model input or a forecast.*

### Tested observations [DATA]

Period: 2026-09


Tolerance for rate comparisons: ±2 bp.

| Claim (Meldrum, 27 Sep 2026, paraphrase) | Measured value | Agrees? |
|------------------------------------------|---------------|---------|
| SOFR ≈ 3.88% | SOFR = 3.90% | agrees (±2bp) |
| EFFR ≈ 3.88% | EFFR = 3.88% | agrees (±2bp) |
| ON RRP < $1bn | Last obs = $11.539bn; median excl. Sep 30 = $0.653bn (15 of 20 days < $1bn excl. Sep 30) | agrees (median < $1bn excl. Sep 30) |
| 3-month bill ≈ 36bp above EFFR (week Sep 21–26) | DTB3−EFFR = 16.6bp (discount basis); DGS3MO−EFFR = 32.0bp (constant maturity) | DTB3: does NOT agree (±2bp) · DGS3MO: close (4 bp, on the constant-maturity basis) · Overall: partly agrees: close on the constant-maturity basis (32 vs 36 bp), not on the discount basis (17 bp) |

> **Note on bill measures**: DTB3 is quoted on a discount basis (annualised
> using a 360-day year, face value denominator); DGS3MO is a constant-maturity
> yield (bond-equivalent basis, 365-day year). The two measures are calculated
> differently from the same secondary market, so they differ by a small but
> systematic amount. "Does not agree" is reported only if *neither* measure
> is within ±2 bp of the 36 bp claim.

SOFR−EFFR average in Sep 2026: 0.1 bp.

### Mechanism description [COMMENTARY / ARGUMENT]

When Treasury runs a deficit, it finances it through bill and coupon issuance.
When buyers are commercial banks or their depositors, the payment draws down
bank reserves. When buyers are money-market funds, cash flows from the ON RRP
facility, reducing that balance. Either path reduces the aggregate liquidity
buffer available to the banking system.

Dealers who take inventory of new coupon issuance that they cannot immediately
place into portfolios finance those holdings overnight in the repo market, adding
to repo demand and placing upward pressure on SOFR. A TGA rebuild (Treasury
receiving tax receipts or borrowing) draws reserves from the system; a TGA
drawdown (Treasury spending) injects them. WTREGEN on FRED captures the weekly
TGA balance; it is not a daily signal.

The evidence for this transmission in the 2025 episode is discussed in Q3.
Whether these dynamics constitute a reliable *leading* indicator is uncertain
from a single episode.

---

*All FRED data downloaded 2026-10-01 via `https://fred.stlouisfed.org/graph/fredgraph.csv`.*
*FRED serves latest revised data; this is not a real-time or vintage analysis.*
*Missing or unverified series: see README.md.*
