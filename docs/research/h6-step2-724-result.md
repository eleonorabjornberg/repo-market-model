# H6 development step 2: (s3c-ann-net) on the event-day strata, and a risk-date variant (#724)

**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), development step 2, milestone M2: the H5 model scored on risk dates, then a risk-date-specialised variant. **Development data, not a verdict** (scoring protocol v1, #640): the days were seen before the declaration (`metadata/h6_step2_724.json`, committed before any score), no confirmation day is scored, nothing is published and no locked day or day after 2025-12-31 is read. Script `scripts/h6_step2_724.py`; every figure below is read from `docs/research/h6-step2-724/result.json`. Made at the 18:00 decision instant, on the published panel (`4ddc3882cd6d...`).

## 1. What is scored

- **Candidate.** (s3c-ann-net), frozen by Eleonora on 2 November 2026 (SRF cap kept, probability rule b), walked by `scripts/capped_baselines_b2star_1434.py` unchanged. The pooled development means of the candidate, B2*-cap and B1'*-cap reproduce #1434's record within 1e-9 (6 figures checked).
- **Strata.** #1131's (`metadata/h6_design_1131.json`), every one read from the calendar at the target day, over 1425 target days from 2020-04-13 to 2025-12-24 (5.7 years) on which the candidate, the variant, the reference and every benchmark but the calendar one have a forecast at all five leads. A day may be in several strata; the union counts it once.
- **Score.** The H5 metric: grid CRPS averaged over leads 1 to 5 at the target day (primary), upper-tail twCRPS (key secondary). Paired, positive favours the model; #1131's studentized stationary bootstrap (block 3 events, HAC lag 3, 10000 draws, seed 724), two-sided 90%, so the lower end is the one-sided 95% lower bound.
- **Benchmarks.** B1 and B2 decide (default 6 of #1131); B1', the risk-date calendar benchmark (#693), B2*-cap (#1440, merged as #1449) and B1'*-cap are reported. `spread_mr_ctx` (#761) is #1131's reference column, carried beside the candidate; it is not a candidate here.
- **Variant (1 declared, 1 scored).** `sc_s3c_ann_net_riskscale`: the candidate's 23 quantiles stretched about their median by k, chosen from [0.5, 0.67, 0.8, 1.0, 1.25, 1.5, 2.0] per stratum as the k with the lowest mean grid CRPS of the candidate's own rescaled, capped forecasts over the most recent 150 cells of that stratum (fewer than 60: k = 1), using only cells whose outcome was public at the decision (target row at or before the decision's anchor row). A cell's stratum is read at its own decision instant. Direct pairs: the variant fits nothing.

### Defaults and rulings

Rulings: Rewrite on (s3c-ann-net) and #1131's strata (Eleonora, 4 November 2026 docket, option a; this issue); (s3c-ann-net) is the candidate, SRF cap kept, probability rule (b) (Eleonora, 2 November 2026, relayed); H6 is registered ahead of H5 on the strata's unit of evidence (Eleonora, 22 October 2026, option c of #1024, on #1131).

Defaults of #1131's section 6 that Eleonora has not ruled on, taken here: 1. unit of evidence: the union is primary and the strata are reported cuts; 2. the union without the large bill stratum is the primary union; 3. the month-end turn is #959's label; 6. B1 and B2 decide; B1' and the #693 calendar benchmark are reported beside them; 7. no multiplicity correction on reported cuts; 9. settlement flags are read as #849 does.

The coupon flag is read as #849 does: 0 target days have a coupon settlement that was not public at the lead-1 decision instant and are not coupon-stratum members (#1131 read the panel's flag). The declaration's first reading, the lead-5 instant, left the stratum empty (see its amendment).

## 2. The strata

| stratum | events | per year | by calendar year | B1 | B1' | B2 | risk-date calendar (#693) | B2*-cap | B1'*-cap |
|---|---|---|---|---|---|---|---|---|---|
| union without the bill stratum (primary) | 413 | 72.5 | 2020: 55, 2021: 72, 2022: 75, 2023: 73, 2024: 69, 2025: 69 | 413 | 413 | 413 | 207 | 413 | 413 |
| union of the strata | 589 | 103.4 | 2020: 81, 2021: 78, 2022: 91, 2023: 133, 2024: 106, 2025: 100 | 589 | 589 | 589 | 207 | 589 | 589 |
| coupon settlement | 186 | 32.6 | 2020: 26, 2021: 35, 2022: 33, 2023: 31, 2024: 32, 2025: 29 | 186 | 186 | 186 | 111 | 186 | 186 |
| large bill settlement | 245 | 43.0 | 2020: 35, 2021: 9, 2022: 21, 2023: 86, 2024: 53, 2025: 41 | 245 | 245 | 245 | 33 | 245 | 245 |
| month-end turn | 92 | 16.1 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | 92 | 92 | 92 | 92 | 92 | 92 |
| quarter-end turn (Mar, Jun, Sep) | 34 | 6.0 | 2020: 4, 2021: 6, 2022: 6, 2023: 6, 2024: 6, 2025: 6 | 34 | 34 | 34 | 34 | 34 | 34 |
| year-end (thin) | 10 | 1.8 | 2020: 1, 2021: 2, 2022: 2, 2023: 2, 2024: 2, 2025: 1 | 10 | 10 | 10 | 10 | 10 | 10 |
| quarter-end and year-end | 44 | 7.7 | 2020: 5, 2021: 8, 2022: 8, 2023: 8, 2024: 8, 2025: 7 | 44 | 44 | 44 | 44 | 44 | 44 |
| tax date | 71 | 12.5 | 2020: 12, 2021: 12, 2022: 12, 2023: 12, 2024: 12, 2025: 11 | 71 | 71 | 71 | 71 | 71 | 71 |
| FOMC meeting day | 92 | 16.1 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | 92 | 92 | 92 | 26 | 92 | 92 |
| IORB-change window (two days after a meeting) | 92 | 16.1 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | 92 | 92 | 92 | 25 | 92 | 92 |

Columns after the year split: events each benchmark covers. The calendar benchmark exists only on a day typed as one of its four risk types at all five leads.

## 3. Skill by stratum: grid CRPS (primary)

Skill is the share of the benchmark's mean score the model removes, with the 90% interval. Development data, not a verdict.

| stratum | benchmark | events | (s3c-ann-net) | risk-date variant | spread_mr_ctx |
|---|---|---|---|---|---|
| union without the bill stratum (primary) | B1 | 413 | +26.6% [+19.2%, +34.7%] | +26.3% [+18.7%, +34.4%] | +3.0% [-5.5%, +11.2%] |
| union without the bill stratum (primary) | B1' | 413 | +20.3% [+13.2%, +27.7%] | +20.0% [+12.6%, +27.5%] | -5.4% [-12.9%, +1.6%] |
| union without the bill stratum (primary) | B2 | 413 | +53.9% [+44.7%, +63.2%] | +53.7% [+44.8%, +62.9%] | +39.1% [+27.9%, +49.3%] |
| union without the bill stratum (primary) | risk-date calendar (#693) | 207 | +59.0% [+47.4%, +69.5%] | +59.2% [+48.5%, +69.5%] | +41.5% [+28.0%, +52.6%] |
| union without the bill stratum (primary) | B2*-cap | 413 | +64.0% [+57.1%, +70.3%] | +63.8% [+57.3%, +70.0%] | +52.4% [+44.0%, +59.4%] |
| union without the bill stratum (primary) | B1'*-cap | 413 | +19.7% [+12.6%, +26.9%] | +19.3% [+12.1%, +26.7%] | -6.2% [-13.4%, +0.5%] |
| union of the strata | B1 | 589 | +25.6% [+19.7%, +31.8%] | +25.1% [+19.1%, +31.4%] | +6.7% [-0.2%, +13.6%] |
| union of the strata | B1' | 589 | +18.8% [+13.1%, +24.6%] | +18.2% [+12.5%, +24.0%] | -1.9% [-8.0%, +3.7%] |
| union of the strata | B2 | 589 | +51.3% [+43.4%, +58.6%] | +50.9% [+43.3%, +58.1%] | +38.9% [+29.4%, +47.2%] |
| union of the strata | risk-date calendar (#693) | 207 | +59.0% [+47.4%, +69.5%] | +59.2% [+48.5%, +69.5%] | +41.5% [+28.0%, +52.6%] |
| union of the strata | B2*-cap | 589 | +60.9% [+54.8%, +66.2%] | +60.6% [+54.8%, +65.9%] | +50.9% [+43.8%, +57.1%] |
| union of the strata | B1'*-cap | 589 | +18.1% [+12.6%, +23.9%] | +17.5% [+12.0%, +23.2%] | -2.7% [-8.7%, +2.7%] |
| coupon settlement | B1 | 186 | +35.7% [+23.4%, +47.4%] | +36.3% [+24.1%, +47.7%] | +8.8% [-2.6%, +18.2%] |
| coupon settlement | B1' | 186 | +31.6% [+20.0%, +42.3%] | +32.2% [+20.8%, +42.6%] | +2.9% [-6.5%, +10.6%] |
| coupon settlement | B2 | 186 | +57.1% [+46.1%, +68.1%] | +57.5% [+46.9%, +68.3%] | +39.2% [+25.7%, +50.3%] |
| coupon settlement | risk-date calendar (#693) | 111 | +60.3% [+48.5%, +71.8%] | +60.9% [+49.7%, +72.0%] | +40.3% [+25.6%, +52.1%] |
| coupon settlement | B2*-cap | 186 | +67.2% [+60.0%, +74.3%] | +67.5% [+60.6%, +74.4%] | +53.5% [+44.1%, +61.4%] |
| coupon settlement | B1'*-cap | 186 | +30.8% [+19.5%, +41.2%] | +31.4% [+20.3%, +41.5%] | +1.8% [-6.9%, +9.0%] |
| large bill settlement | B1 | 245 | +23.6% [+16.1%, +31.8%] | +23.2% [+15.4%, +31.5%] | +11.2% [+2.9%, +19.3%] |
| large bill settlement | B1' | 245 | +15.7% [+8.7%, +23.4%] | +15.2% [+8.4%, +22.5%] | +2.1% [-4.6%, +8.4%] |
| large bill settlement | B2 | 245 | +46.7% [+35.0%, +57.8%] | +46.3% [+34.9%, +57.5%] | +38.0% [+25.5%, +50.0%] |
| large bill settlement | risk-date calendar (#693) | 33 | +54.6% [+20.1%, +87.5%] | +56.2% [+29.5%, +87.3%] | +37.2% [-2.1%, +69.6%] |
| large bill settlement | B2*-cap | 245 | +52.9% [+43.5%, +61.6%] | +52.7% [+43.3%, +61.4%] | +45.3% [+35.1%, +54.7%] |
| large bill settlement | B1'*-cap | 245 | +14.8% [+7.9%, +22.3%] | +14.3% [+7.7%, +21.4%] | +1.1% [-5.5%, +7.1%] |
| month-end turn | B1 | 92 | +40.9% [+25.1%, +57.5%] | +40.4% [+24.8%, +57.2%] | +9.8% [-13.1%, +25.0%] |
| month-end turn | B1' | 92 | +33.4% [+19.5%, +48.8%] | +32.9% [+19.2%, +48.4%] | -1.6% [-13.2%, +8.7%] |
| month-end turn | B2 | 92 | +58.5% [+40.3%, +78.0%] | +58.2% [+39.8%, +78.0%] | +36.7% [+15.4%, +57.6%] |
| month-end turn | risk-date calendar (#693) | 92 | +58.5% [+40.3%, +78.0%] | +58.2% [+39.8%, +78.0%] | +36.7% [+15.4%, +57.6%] |
| month-end turn | B2*-cap | 92 | +68.8% [+58.3%, +78.5%] | +68.5% [+57.9%, +78.5%] | +52.4% [+40.9%, +62.3%] |
| month-end turn | B1'*-cap | 92 | +32.1% [+18.0%, +47.3%] | +31.5% [+17.7%, +46.9%] | -3.7% [-14.4%, +6.3%] |
| quarter-end turn (Mar, Jun, Sep) | B1 | 34 | +26.6% [+18.1%, +34.7%] | +33.5% [+23.7%, +43.0%] | +6.4% [-8.3%, +15.0%] |
| quarter-end turn (Mar, Jun, Sep) | B1' | 34 | +24.6% [+15.0%, +33.5%] | +31.7% [+20.5%, +42.0%] | +3.9% [-14.0%, +13.0%] |
| quarter-end turn (Mar, Jun, Sep) | B2 | 34 | +32.6% [-33.1%, +57.3%] | +39.0% [-12.4%, +59.6%] | +14.1% [-79.1%, +47.7%] |
| quarter-end turn (Mar, Jun, Sep) | risk-date calendar (#693) | 34 | +32.6% [-33.1%, +57.3%] | +39.0% [-12.4%, +59.6%] | +14.1% [-79.1%, +47.7%] |
| quarter-end turn (Mar, Jun, Sep) | B2*-cap | 34 | +48.6% [+11.1%, +74.6%] | +53.4% [+23.6%, +75.6%] | +34.4% [-34.3%, +65.2%] |
| quarter-end turn (Mar, Jun, Sep) | B1'*-cap | 34 | +23.4% [+13.7%, +32.4%] | +30.7% [+19.4%, +41.1%] | +2.4% [-15.0%, +11.3%] |
| year-end | B1 | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B1' | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B2 | 10 | thin (10) | thin (10) | thin (10) |
| year-end | risk-date calendar (#693) | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B2*-cap | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B1'*-cap | 10 | thin (10) | thin (10) | thin (10) |
| quarter-end and year-end | B1 | 44 | +30.2% [+19.4%, +43.6%] | +35.4% [+23.7%, +48.3%] | +8.9% [-5.1%, +18.8%] |
| quarter-end and year-end | B1' | 44 | +28.6% [+16.7%, +43.3%] | +33.9% [+21.0%, +48.0%] | +6.9% [-9.0%, +17.6%] |
| quarter-end and year-end | B2 | 44 | +34.7% [-4.9%, +53.0%] | +39.5% [+7.5%, +55.3%] | +14.8% [-41.8%, +43.2%] |
| quarter-end and year-end | risk-date calendar (#693) | 44 | +43.3% [+8.2%, +62.6%] | +47.5% [+18.8%, +64.1%] | +26.0% [-25.2%, +54.2%] |
| quarter-end and year-end | B2*-cap | 44 | +51.0% [+26.8%, +67.7%] | +54.6% [+35.4%, +69.0%] | +36.0% [-4.8%, +58.5%] |
| quarter-end and year-end | B1'*-cap | 44 | +27.6% [+15.5%, +42.6%] | +32.9% [+20.1%, +47.5%] | +5.5% [-10.1%, +16.4%] |
| tax date | B1 | 71 | +19.6% [-3.2%, +37.7%] | +14.9% [-7.9%, +35.6%] | -15.7% [-44.7%, +10.9%] |
| tax date | B1' | 71 | +12.5% [-7.1%, +30.1%] | +7.3% [-13.0%, +27.1%] | -25.9% [-53.3%, -0.4%] |
| tax date | B2 | 71 | +70.2% [+58.1%, +82.3%] | +68.5% [+57.2%, +80.1%] | +57.2% [+44.9%, +67.4%] |
| tax date | risk-date calendar (#693) | 71 | +70.2% [+58.1%, +82.3%] | +68.5% [+57.2%, +80.1%] | +57.2% [+44.9%, +67.4%] |
| tax date | B2*-cap | 71 | +73.6% [+63.8%, +82.2%] | +72.1% [+63.0%, +80.2%] | +62.1% [+51.9%, +69.9%] |
| tax date | B1'*-cap | 71 | +12.4% [-7.5%, +29.2%] | +7.3% [-12.7%, +26.0%] | -26.0% [-51.6%, -1.4%] |
| FOMC meeting day | B1 | 92 | +14.1% [+0.8%, +26.4%] | +12.3% [-1.0%, +24.8%] | +0.2% [-14.5%, +14.6%] |
| FOMC meeting day | B1' | 92 | +0.6% [-11.9%, +12.2%] | -1.5% [-14.6%, +10.5%] | -15.4% [-29.7%, -1.6%] |
| FOMC meeting day | B2 | 92 | +45.8% [+28.2%, +61.2%] | +44.6% [+27.4%, +60.1%] | +37.0% [+17.3%, +52.5%] |
| FOMC meeting day | risk-date calendar (#693) | 26 | thin (26) | thin (26) | thin (26) |
| FOMC meeting day | B2*-cap | 92 | +57.8% [+43.9%, +70.2%] | +56.9% [+43.1%, +69.2%] | +51.0% [+34.6%, +63.7%] |
| FOMC meeting day | B1'*-cap | 92 | +0.1% [-12.3%, +11.7%] | -2.1% [-14.8%, +9.8%] | -16.1% [-30.0%, -2.6%] |
| IORB-change window (two days after a meeting) | B1 | 92 | +19.0% [+5.2%, +33.0%] | +16.3% [+2.2%, +30.5%] | -8.6% [-26.8%, +7.2%] |
| IORB-change window (two days after a meeting) | B1' | 92 | +9.8% [-2.7%, +22.7%] | +6.8% [-5.9%, +20.2%] | -20.9% [-38.9%, -8.4%] |
| IORB-change window (two days after a meeting) | B2 | 92 | +57.4% [+40.3%, +71.0%] | +56.0% [+38.8%, +70.0%] | +42.9% [+15.2%, +57.8%] |
| IORB-change window (two days after a meeting) | risk-date calendar (#693) | 25 | thin (25) | thin (25) | thin (25) |
| IORB-change window (two days after a meeting) | B2*-cap | 92 | +65.1% [+49.9%, +75.4%] | +64.0% [+48.9%, +74.5%] | +53.2% [+29.1%, +65.6%] |
| IORB-change window (two days after a meeting) | B1'*-cap | 92 | +9.8% [-2.5%, +21.6%] | +6.8% [-5.6%, +19.1%] | -21.0% [-38.8%, -9.3%] |

## 3. Skill by stratum: upper-tail twCRPS (key secondary)

Skill is the share of the benchmark's mean score the model removes, with the 90% interval. Development data, not a verdict.

| stratum | benchmark | events | (s3c-ann-net) | risk-date variant | spread_mr_ctx |
|---|---|---|---|---|---|
| union without the bill stratum (primary) | B1 | 413 | +30.3% [+15.5%, +50.1%] | +29.0% [+13.9%, +47.5%] | -12.7% [-41.2%, +8.8%] |
| union without the bill stratum (primary) | B1' | 413 | +28.1% [+17.1%, +42.1%] | +26.7% [+15.7%, +39.7%] | -16.3% [-37.0%, -1.1%] |
| union without the bill stratum (primary) | B2 | 413 | +57.4% [+39.7%, +71.4%] | +56.6% [+40.0%, +70.7%] | +31.1% [+9.7%, +52.0%] |
| union without the bill stratum (primary) | risk-date calendar (#693) | 207 | +63.1% [+38.3%, +78.2%] | +62.8% [+41.4%, +77.5%] | +32.5% [+5.9%, +54.9%] |
| union without the bill stratum (primary) | B2*-cap | 413 | +65.2% [+53.3%, +73.6%] | +64.5% [+54.2%, +72.6%] | +43.7% [+32.2%, +54.4%] |
| union without the bill stratum (primary) | B1'*-cap | 413 | +27.3% [+16.8%, +40.7%] | +25.8% [+15.3%, +38.3%] | -17.7% [-37.5%, -3.0%] |
| union of the strata | B1 | 589 | +32.5% [+21.9%, +44.7%] | +31.4% [+21.1%, +43.4%] | +2.5% [-14.7%, +18.1%] |
| union of the strata | B1' | 589 | +25.3% [+15.8%, +36.6%] | +24.0% [+15.1%, +34.6%] | -8.0% [-22.1%, +3.7%] |
| union of the strata | B2 | 589 | +53.2% [+41.1%, +63.9%] | +52.4% [+40.9%, +63.1%] | +32.4% [+17.9%, +46.5%] |
| union of the strata | risk-date calendar (#693) | 207 | +63.1% [+38.3%, +78.2%] | +62.8% [+41.4%, +77.5%] | +32.5% [+5.9%, +54.9%] |
| union of the strata | B2*-cap | 589 | +59.9% [+50.3%, +67.5%] | +59.2% [+50.6%, +66.5%] | +42.0% [+32.4%, +50.7%] |
| union of the strata | B1'*-cap | 589 | +24.3% [+15.0%, +35.3%] | +23.0% [+14.3%, +33.3%] | -9.5% [-23.0%, +1.9%] |
| coupon settlement | B1 | 186 | +38.8% [+15.4%, +63.8%] | +38.2% [+14.1%, +62.8%] | -5.8% [-50.0%, +23.2%] |
| coupon settlement | B1' | 186 | +38.5% [+22.1%, +56.7%] | +38.0% [+21.2%, +56.1%] | -6.2% [-36.3%, +13.9%] |
| coupon settlement | B2 | 186 | +59.1% [+40.5%, +77.4%] | +58.7% [+40.1%, +77.6%] | +29.3% [+4.2%, +53.0%] |
| coupon settlement | risk-date calendar (#693) | 111 | +64.6% [+45.8%, +78.8%] | +64.2% [+45.9%, +78.7%] | +32.8% [+7.5%, +52.3%] |
| coupon settlement | B2*-cap | 186 | +67.2% [+56.5%, +79.0%] | +66.9% [+56.7%, +79.2%] | +43.3% [+32.0%, +54.7%] |
| coupon settlement | B1'*-cap | 186 | +37.5% [+21.7%, +54.9%] | +37.0% [+20.8%, +54.3%] | -7.9% [-36.7%, +11.0%] |
| large bill settlement | B1 | 245 | +34.6% [+19.3%, +49.6%] | +35.2% [+21.5%, +48.8%] | +18.8% [+3.8%, +34.1%] |
| large bill settlement | B1' | 245 | +21.8% [+7.2%, +42.1%] | +22.6% [+10.0%, +39.9%] | +3.0% [-8.7%, +15.0%] |
| large bill settlement | B2 | 245 | +49.3% [+34.6%, +62.3%] | +49.8% [+36.9%, +61.8%] | +37.1% [+24.0%, +49.5%] |
| large bill settlement | risk-date calendar (#693) | 33 | undefined | undefined | undefined |
| large bill settlement | B2*-cap | 245 | +50.6% [+36.8%, +61.4%] | +51.1% [+39.2%, +61.0%] | +38.7% [+27.1%, +48.5%] |
| large bill settlement | B1'*-cap | 245 | +20.5% [+6.0%, +40.0%] | +21.3% [+9.0%, +37.9%] | +1.3% [-10.2%, +12.8%] |
| month-end turn | B1 | 92 | +45.9% [+17.4%, +95.2%] | +43.4% [+10.4%, +103.6%] | -18.5% [-147.3%, +108.7%] |
| month-end turn | B1' | 92 | +47.6% [+30.1%, +68.4%] | +45.2% [+29.1%, +67.4%] | -14.7% [-46.7%, +42.2%] |
| month-end turn | B2 | 92 | +72.1% [+62.3%, +80.6%] | +70.9% [+58.9%, +80.2%] | +39.0% [-5.4%, +65.3%] |
| month-end turn | risk-date calendar (#693) | 92 | +72.1% [+62.3%, +80.6%] | +70.9% [+58.9%, +80.2%] | +39.0% [-5.4%, +65.3%] |
| month-end turn | B2*-cap | 92 | +77.1% [+69.9%, +83.9%] | +76.0% [+69.5%, +82.9%] | +49.8% [+37.2%, +60.6%] |
| month-end turn | B1'*-cap | 92 | +46.5% [+28.2%, +66.7%] | +44.1% [+27.6%, +65.3%] | -17.0% [-45.7%, +27.2%] |
| quarter-end turn (Mar, Jun, Sep) | B1 | 34 | undefined | undefined | undefined |
| quarter-end turn (Mar, Jun, Sep) | B1' | 34 | undefined | undefined | undefined |
| quarter-end turn (Mar, Jun, Sep) | B2 | 34 | undefined | undefined | undefined |
| quarter-end turn (Mar, Jun, Sep) | risk-date calendar (#693) | 34 | undefined | undefined | undefined |
| quarter-end turn (Mar, Jun, Sep) | B2*-cap | 34 | undefined | +46.9% [-22.5%, +98.4%] | +23.1% [-54.9%, +78.4%] |
| quarter-end turn (Mar, Jun, Sep) | B1'*-cap | 34 | undefined | +24.9% [+11.9%, +41.4%] | -8.8% [-64.7%, +11.1%] |
| year-end | B1 | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B1' | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B2 | 10 | thin (10) | thin (10) | thin (10) |
| year-end | risk-date calendar (#693) | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B2*-cap | 10 | thin (10) | thin (10) | thin (10) |
| year-end | B1'*-cap | 10 | thin (10) | thin (10) | thin (10) |
| quarter-end and year-end | B1 | 44 | +23.8% [+11.8%, +40.9%] | +30.2% [+17.7%, +43.2%] | -3.7% [-42.5%, +14.9%] |
| quarter-end and year-end | B1' | 44 | +23.9% [+11.9%, +41.3%] | +30.3% [+18.0%, +43.4%] | -3.7% [-40.8%, +15.1%] |
| quarter-end and year-end | B2 | 44 | +15.3% [-13.6%, +35.9%] | +22.4% [+0.5%, +38.9%] | -15.3% [-50.3%, +10.5%] |
| quarter-end and year-end | risk-date calendar (#693) | 44 | +22.1% [-6.4%, +46.9%] | +28.6% [+5.7%, +47.8%] | -6.1% [-48.0%, +19.8%] |
| quarter-end and year-end | B2*-cap | 44 | +43.2% [-17.7%, +83.9%] | +47.9% [+0.5%, +82.9%] | +22.6% [-29.6%, +68.5%] |
| quarter-end and year-end | B1'*-cap | 44 | +23.2% [+11.5%, +40.6%] | +29.6% [+17.5%, +42.7%] | -4.6% [-42.2%, +14.4%] |
| tax date | B1 | 71 | +35.3% [+1.0%, +62.8%] | +23.5% [-44.6%, +79.5%] | -51.5% [-291.6%, +126.5%] |
| tax date | B1' | 71 | +28.0% [-6.2%, +58.9%] | +14.8% [-54.7%, +76.9%] | -68.6% [-300.3%, +166.8%] |
| tax date | B2 | 71 | undefined | undefined | undefined |
| tax date | risk-date calendar (#693) | 71 | undefined | undefined | undefined |
| tax date | B2*-cap | 71 | +80.6% [+58.8%, +91.8%] | +77.1% [+61.3%, +87.1%] | +54.7% [+41.1%, +64.4%] |
| tax date | B1'*-cap | 71 | +27.2% [-4.9%, +55.7%] | +13.9% [-52.5%, +73.1%] | -70.4% [-296.0%, +169.3%] |
| FOMC meeting day | B1 | 92 | +6.5% [-16.4%, +26.7%] | +0.1% [-38.9%, +38.3%] | -30.5% [-77.2%, +18.0%] |
| FOMC meeting day | B1' | 92 | -8.2% [-39.9%, +20.8%] | -15.6% [-74.2%, +36.8%] | -51.0% [-114.9%, +34.2%] |
| FOMC meeting day | B2 | 92 | +44.8% [+22.0%, +57.9%] | +41.0% [+13.1%, +56.6%] | +23.0% [-5.0%, +38.5%] |
| FOMC meeting day | risk-date calendar (#693) | 26 | thin (26) | thin (26) | thin (26) |
| FOMC meeting day | B2*-cap | 92 | +56.8% [+35.9%, +66.6%] | +53.9% [+37.8%, +61.8%] | +39.7% [+14.5%, +49.4%] |
| FOMC meeting day | B1'*-cap | 92 | -7.9% [-37.4%, +17.3%] | -15.3% [-69.8%, +32.4%] | -50.6% [-110.5%, +29.5%] |
| IORB-change window (two days after a meeting) | B1 | 92 | +28.7% [+2.6%, +58.4%] | +23.1% [-9.5%, +70.9%] | -21.6% [-100.3%, +39.5%] |
| IORB-change window (two days after a meeting) | B1' | 92 | +22.9% [+4.4%, +38.4%] | +16.8% [-7.6%, +40.2%] | -31.6% [-89.2%, +22.6%] |
| IORB-change window (two days after a meeting) | B2 | 92 | +64.8% [+53.2%, +73.4%] | +62.1% [+47.7%, +72.0%] | +40.0% [+17.2%, +58.5%] |
| IORB-change window (two days after a meeting) | risk-date calendar (#693) | 25 | thin (25) | thin (25) | thin (25) |
| IORB-change window (two days after a meeting) | B2*-cap | 92 | +69.7% [+57.7%, +76.1%] | +67.3% [+55.9%, +73.4%] | +48.3% [+36.3%, +55.0%] |
| IORB-change window (two days after a meeting) | B1'*-cap | 92 | +22.1% [+4.5%, +35.8%] | +15.9% [-7.1%, +37.1%] | -33.0% [-85.1%, +15.8%] |

## 4. The variant against (s3c-ann-net)

Paired on the same events, same bootstrap; positive favours the variant. Grid CRPS difference is in bp (candidate minus variant).

| cut | events | grid CRPS skill over (s3c-ann-net) | grid CRPS difference (bp) | twCRPS skill over (s3c-ann-net) |
|---|---|---|---|---|
| union without the bill stratum (primary) | 413 | -0.4% [-2.1%, +1.7%] | -0.005 [-0.021, +0.021] | -2.0% [-7.1%, +4.5%] |
| union of the strata | 589 | -0.7% [-2.0%, +0.8%] | -0.008 [-0.021, +0.009] | -1.7% [-5.3%, +2.7%] |
| coupon settlement | 186 | +0.8% [-0.3%, +2.3%] | +0.010 [-0.004, +0.028] | -0.9% [-3.8%, +2.9%] |
| large bill settlement | 245 | -0.6% [-2.2%, +1.9%] | -0.007 [-0.023, +0.022] | +1.0% [-3.1%, +6.8%] |
| month-end turn | 92 | -0.8% [-2.3%, +0.4%] | -0.009 [-0.024, +0.004] | -4.5% [-15.6%, +4.1%] |
| quarter-end turn (Mar, Jun, Sep) | 34 | +9.5% [+5.1%, +14.2%] | +0.222 [+0.037, +0.753] | undefined |
| year-end | 10 | thin (10) | thin (10) | thin (10) |
| quarter-end and year-end | 44 | +7.4% [+3.8%, +11.4%] | +0.156 [+0.043, +0.439] | +8.4% [+1.7%, +14.1%] |
| tax date | 71 | -5.9% [-15.3%, -1.0%] | -0.059 [-0.132, -0.018] | -18.3% [-57.0%, +8.7%] |
| FOMC meeting day | 92 | -2.1% [-5.2%, +0.2%] | -0.024 [-0.049, -0.000] | -6.8% [-28.2%, +13.1%] |
| IORB-change window (two days after a meeting) | 92 | -3.3% [-5.9%, -1.5%] | -0.035 [-0.064, -0.015] | -7.8% [-19.4%, +0.3%] |

## 5. By regime and by pressure-day type (the union without the bill stratum)

### Regime: grid CRPS skill

| stratum | benchmark | events | (s3c-ann-net) | risk-date variant | spread_mr_ctx |
|---|---|---|---|---|---|
| 2020 | B1 | 55 | +10.8% [-3.6%, +24.2%] | +3.4% [-11.7%, +18.2%] | -52.6% [-73.5%, -35.4%] |
| 2020 | B1' | 55 | +12.0% [-5.7%, +28.5%] | +4.6% [-15.1%, +24.1%] | -50.6% [-73.1%, -31.8%] |
| 2020 | B2 | 55 | +68.5% [+44.8%, +88.4%] | +65.9% [+39.9%, +88.5%] | +46.2% [+11.0%, +79.5%] |
| 2020 | B2*-cap | 55 | +68.5% [+54.5%, +83.1%] | +65.8% [+50.7%, +82.9%] | +46.1% [+27.6%, +71.5%] |
| 2021-23 | B1 | 220 | -0.2% [-13.8%, +8.2%] | -1.1% [-14.3%, +7.0%] | -13.7% [-28.8%, -2.6%] |
| 2021-23 | B1' | 220 | -3.0% [-13.8%, +5.9%] | -4.0% [-14.3%, +4.8%] | -16.9% [-28.0%, -7.7%] |
| 2021-23 | B2 | 220 | +58.7% [+48.3%, +68.7%] | +58.3% [+48.2%, +68.0%] | +53.1% [+44.6%, +60.6%] |
| 2021-23 | B2*-cap | 220 | +72.4% [+64.0%, +79.9%] | +72.1% [+64.1%, +79.5%] | +68.6% [+61.8%, +74.6%] |
| 2024 | B1 | 69 | +35.9% [+28.0%, +44.5%] | +37.8% [+30.8%, +45.1%] | +18.9% [+12.8%, +24.7%] |
| 2024 | B1' | 69 | +26.7% [+17.8%, +38.5%] | +28.8% [+19.3%, +39.4%] | +7.3% [+0.1%, +12.7%] |
| 2024 | B2 | 69 | +27.0% [+16.6%, +35.3%] | +29.2% [+17.7%, +37.1%] | +7.7% [-11.6%, +21.7%] |
| 2024 | B2*-cap | 69 | +42.8% [+32.1%, +50.4%] | +44.5% [+35.1%, +50.9%] | +27.7% [+5.9%, +40.4%] |
| 2025-26 | B1 | 69 | +41.1% [+30.0%, +52.5%] | +41.4% [+31.5%, +52.0%] | +16.1% [+1.0%, +28.0%] |
| 2025-26 | B1' | 69 | +34.2% [+24.8%, +43.6%] | +34.6% [+25.9%, +43.2%] | +6.3% [-7.5%, +16.4%] |
| 2025-26 | B2 | 69 | +52.1% [+26.5%, +72.5%] | +52.4% [+28.4%, +73.0%] | +31.8% [-0.5%, +56.5%] |
| 2025-26 | B2*-cap | 69 | +58.8% [+38.1%, +75.3%] | +59.1% [+39.8%, +75.5%] | +41.3% [+15.7%, +61.2%] |

### Regime: the variant against (s3c-ann-net)

| cut | events | grid CRPS skill over (s3c-ann-net) | grid CRPS difference (bp) | twCRPS skill over (s3c-ann-net) |
|---|---|---|---|---|
| 2020 | 55 | -8.4% [-14.9%, -3.6%] | -0.079 [-0.138, -0.034] | -18.1% [-31.8%, -8.0%] |
| 2021-23 | 220 | -1.0% [-2.8%, +0.7%] | -0.007 [-0.018, +0.005] | -46.1% [-71.1%, -22.0%] |
| 2024 | 69 | +2.9% [-1.0%, +12.5%] | +0.042 [-0.010, +0.264] | +7.1% [-16.3%, +35.2%] |
| 2025-26 | 69 | +0.6% [-1.9%, +5.0%] | +0.014 [-0.038, +0.128] | +0.2% [-2.9%, +5.0%] |

### Pressure-day type: grid CRPS skill

| stratum | benchmark | events | (s3c-ann-net) | risk-date variant | spread_mr_ctx |
|---|---|---|---|---|---|
| ordinary | B1 | 206 | +16.7% [+6.1%, +26.7%] | +15.1% [+4.7%, +25.0%] | +1.5% [-9.9%, +12.2%] |
| ordinary | B1' | 206 | +8.9% [-2.5%, +19.5%] | +7.1% [-4.2%, +18.1%] | -7.8% [-19.1%, +2.3%] |
| ordinary | B2 | 206 | +48.0% [+34.4%, +61.7%] | +47.0% [+33.3%, +61.1%] | +38.5% [+21.9%, +52.9%] |
| ordinary | B2*-cap | 206 | +60.7% [+49.6%, +70.4%] | +59.9% [+48.7%, +69.8%] | +53.5% [+39.2%, +64.5%] |
| quarter_end_turn | B1 | 34 | +26.6% [+18.1%, +34.7%] | +33.5% [+23.7%, +43.0%] | +6.4% [-8.3%, +15.0%] |
| quarter_end_turn | B1' | 34 | +24.6% [+15.0%, +33.5%] | +31.7% [+20.5%, +42.0%] | +3.9% [-14.0%, +13.0%] |
| quarter_end_turn | B2 | 34 | +32.6% [-33.1%, +57.3%] | +39.0% [-12.4%, +59.6%] | +14.1% [-79.1%, +47.7%] |
| quarter_end_turn | B2*-cap | 34 | +48.6% [+11.1%, +74.6%] | +53.4% [+23.6%, +75.6%] | +34.4% [-34.3%, +65.2%] |
| tax_date | B1 | 71 | +19.6% [-3.2%, +37.7%] | +14.9% [-7.9%, +35.6%] | -15.7% [-44.7%, +10.9%] |
| tax_date | B1' | 71 | +12.5% [-7.1%, +30.1%] | +7.3% [-13.0%, +27.1%] | -25.9% [-53.3%, -0.4%] |
| tax_date | B2 | 71 | +70.2% [+58.1%, +82.3%] | +68.5% [+57.2%, +80.1%] | +57.2% [+44.9%, +67.4%] |
| tax_date | B2*-cap | 71 | +73.6% [+63.8%, +82.2%] | +72.1% [+63.0%, +80.2%] | +62.1% [+51.9%, +69.9%] |
| turn | B1 | 92 | +40.9% [+25.1%, +57.5%] | +40.4% [+24.8%, +57.2%] | +9.8% [-13.1%, +25.0%] |
| turn | B1' | 92 | +33.4% [+19.5%, +48.8%] | +32.9% [+19.2%, +48.4%] | -1.6% [-13.2%, +8.7%] |
| turn | B2 | 92 | +58.5% [+40.3%, +78.0%] | +58.2% [+39.8%, +78.0%] | +36.7% [+15.4%, +57.6%] |
| turn | B2*-cap | 92 | +68.8% [+58.3%, +78.5%] | +68.5% [+57.9%, +78.5%] | +52.4% [+40.9%, +62.3%] |
| year_end | B1 | 10 | thin (10) | thin (10) | thin (10) |
| year_end | B1' | 10 | thin (10) | thin (10) | thin (10) |
| year_end | B2 | 10 | thin (10) | thin (10) | thin (10) |
| year_end | B2*-cap | 10 | thin (10) | thin (10) | thin (10) |

### Pressure-day type: the variant against (s3c-ann-net)

| cut | events | grid CRPS skill over (s3c-ann-net) | grid CRPS difference (bp) | twCRPS skill over (s3c-ann-net) |
|---|---|---|---|---|
| ordinary | 206 | -2.0% [-3.4%, -0.5%] | -0.019 [-0.031, -0.007] | -4.1% [-9.3%, +1.2%] |
| quarter_end_turn | 34 | +9.5% [+5.1%, +14.2%] | +0.222 [+0.037, +0.753] | undefined |
| tax_date | 71 | -5.9% [-15.3%, -1.0%] | -0.059 [-0.132, -0.018] | -18.3% [-57.0%, +8.7%] |
| turn | 92 | -0.8% [-2.3%, +0.4%] | -0.009 [-0.024, +0.004] | -4.5% [-15.6%, +4.1%] |
| year_end | 10 | thin (10) | thin (10) | thin (10) |

## 6. What the variant did

| label | cells | cells with k not 1 | geometric mean k | cells by k |
|---|---|---|---|---|
| bill_settlement_large | 1225 | 903 | 0.983 | 0.67: 204, 0.8: 226, 1.0: 322, 1.25: 444, 1.5: 29 |
| coupon_settlement | 96 | 0 | 1.000 | 1.0: 96 |
| fomc_meeting | 336 | 196 | 1.229 | 0.8: 10, 1.0: 140, 1.25: 37, 1.5: 139, 2.0: 10 |
| month_end_turn | 600 | 330 | 1.142 | 0.8: 30, 1.0: 270, 1.25: 210, 1.5: 80, 2.0: 10 |
| none | 5928 | 0 | 1.000 | 1.0: 5928 |
| post_fomc_window | 354 | 145 | 1.024 | 0.67: 30, 0.8: 20, 1.0: 209, 1.25: 75, 1.5: 20 |
| quarter_and_year_end | 291 | 231 | 1.717 | 1.0: 60, 1.5: 10, 2.0: 221 |
| tax_date | 445 | 297 | 1.455 | 1.0: 148, 1.25: 27, 1.5: 91, 2.0: 179 |

A label is the cell's first stratum in the declared order; `none` is a cell in no stratum, which keeps k = 1.

## 7. Reading (development, not a verdict)

**Kill rule, in words.** H6's kill is no CRPS skill against as-of persistence and the risk-date calendar benchmark on the risk dates. Read on development data: (s3c-ann-net) shows no skill on the union without the bill stratum if the 90% interval of its grid CRPS skill against B1 or against B2 includes zero or lies below it, and shows skill if the lower end is above zero against both. Against B1 it is +26.6% [+19.2%, +34.7%], against B2 +53.9% [+44.7%, +63.2%]: **skill**. B1' (+20.3% [+13.2%, +27.7%]) and B2*-cap (+64.0% [+57.1%, +70.3%]) do not decide; they say what the skill is worth. The risk-date calendar benchmark (#693) covers 207 of the 413 events: +59.0% [+47.4%, +69.5%].

The variant, read the same way, is **skill** (against B1 +26.3% [+18.7%, +34.4%], against B2 +53.7% [+44.8%, +62.9%]). The reference `spread_mr_ctx` is +3.0% [-5.5%, +11.2%] against B1 and +39.1% [+27.9%, +49.3%] against B2.

Read the same way inside the union without the bill stratum, the candidate's skill by regime is 2020: no skill shown; 2021-23: no skill shown; 2024: skill; 2025-26: skill, and by pressure-day type ordinary: skill; quarter_end_turn: no skill shown; tax_date: no skill shown; turn: skill; year_end: undefined ("no skill shown" is an interval that includes zero against B1 or B2, not a measured absence; the pooled reading above does not carry into a regime or type where it says so).

This is a development reading on days already seen. It closes nothing and registers nothing; the verdict is for prospective confirmation days only.

## What this shows, and does not

- It shows how the frozen candidate scores on #1131's event-day strata on 2020-2025 development days, split by stratum, regime and pressure-day type, and whether one declared risk-date rescaling improves on it there.
- It does not show skill on any confirmation day, does not change the candidate, and sets no rule. The strata overlap and the days within a stratum are dependent; the intervals use #1131's block of 3 events.
- The reported cuts carry no multiplicity correction (default 7). One variant was declared and scored, so the variant count is 1; the scale grid is part of that variant.
- Not checked: B1' and the calendar benchmark on days outside their cover; the 2026 days (#1394's confirmation, not this step); a stratum-specific calendar benchmark for the FOMC and IORB rows (question 8 of #1131, default not added).

**Does the specialised variant add skill over (s3c-ann-net) on the union (without the bill stratum)? It adds no skill that this data can show on grid CRPS: -0.4% [-2.1%, +1.7%] over 413 events (twCRPS -2.0% [-7.1%, +4.5%]). Development data, not a verdict.**
