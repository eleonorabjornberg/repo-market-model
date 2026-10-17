# H9 step 2: B1 with h-row and with h + 1-row changes on the richer targets (#850)

A measurement on development data for hypothesis **H9** (secondary goal), step 2 of `docs/research/hypotheses/H9.md`, closing the H9 remainder of finding #744. It is not a record and **not a verdict**: development data never gives one (`docs/decisions/scoring-protocol.md` §1). Nothing is published and nothing changes: `richer_targets.b1_quantiles`, the protocol's benchmarks and every published figure are as they were, no day after 2025-12-31 is read (`docs/decisions/lockbox.md`), and the regimes are the as-of scarcity state and the day type, both known at the decision instant (ruling on #515). Every choice is in `metadata/b1_alignment_850.json`, committed before any score; `scripts/b1_alignment_850.py` refuses to read it unless it is committed and unchanged.

Tables: [`evidence/b1-alignment-850/tables.md`](evidence/b1-alignment-850/tables.md); data: [`evidence/b1-alignment-850/alignment.json`](evidence/b1-alignment-850/alignment.json). Panel: step 1's (`metadata/richer_targets_639.json`), digest `347f5afb…`. Intervals are two-sided 90%, stationary bootstrap, mean block 10, 2000 resamples, one set of resamples per cell.

## What was measured

For each of step 1's ten targets and each lead 1 to 10, B1 (the last public value plus the empirical distribution of the lead's own changes over the trailing two years) in two forms: with the h-row changes `b1_quantiles` has, and with the h + 1-row changes. The window, the anchor and the look-ahead guard are the shipped function's. A day on which either form, the climatology B2 or the outcome is missing is dropped for both forms. Scored: the central-90% coverage (outcome between the 0.05 and 0.95 quantiles) and the protocol's grid CRPS.

**Control.** On step 1's day set, the h-row form reproduces `docs/pivot/evidence/richer-targets-639/screen.json` exactly (`python3 scripts/b1_alignment_850.py control`) at all fifty target-and-lead cells step 1 reports.

**The anchor is h + 1 rows back on every target.** For every target and every lead 1 to 10, the as-of anchor of every scored day is the scored day less h + 1 panel days (Table 6). So the h-row changes are one row short for all ten targets, not only for SOFR − IORB.

## What it shows

* **Coverage at lead 1.** With h-row changes the central-90% interval covers 79.5% to 92.7% on the ten targets; with h + 1-row changes 79.9% to 94.2%. The levels move the most: SOFR 99th percentile − IORB 81.6% to 87.2%, TGCR − IORB 80.1% to 86.0%, BGCR − IORB 80.3% to 85.8%, ON RRP take-up 79.6% to 86.0%. The three dispersions, the ON RRP change and the standing repo take-up move by two points or less. The largest difference between the two forms on any target is 6.3 points at lead 1, 3.7 at lead 2 and 2.8 at lead 3, and 1.6 points or less from lead 4 (Table 1).
* **CRPS.** The extra row changes B1's mean grid CRPS by between −1.9% (ON RRP take-up, lead 1) and +1.3% (EFFR − IORB, lead 5) over all scored days. The interval of the difference excludes zero in a minority of cells, in both directions (Table 2).
* **Ranking.** Persistence beats the climatology on all scored days, at every lead 1 to 10, for the four level targets (BGCR − IORB, TGCR − IORB, EFFR − IORB, ON RRP take-up). The climatology beats persistence at every lead for the other six (SOFR 99th percentile − IORB, the three dispersions, the ON RRP change, standing repo take-up). **The ranking is the same under both forms for every target at every lead.** Persistence's skill over the climatology moves by at most 0.01 on all scored days (Table 2).
* **One flip, in a small split.** Of the splits (all days, the two scarcity states, four day types), the only cell where the two forms rank differently is TGCR dispersion on quarter-end days at lead 1, 23 days: B1 scores 35.04 with h-row changes and 35.94 with h + 1-row changes against B2's 35.42. The cell is below the 30-day minimum for an interval (Table 3). It is not a result about the target.

## For Eleonora

**Step 2's persistence-against-climatology ranking does not change for any target** on all scored days or in the regime splits, at any lead 1 to 10. The one flip is quarter-end days of one target at one lead, 23 days, and carries no interval. Marked question: does the h + 1 alignment of B1 matter for H9 enough to change the code? On this evidence it does not change the step 2 reading, so the measurement leaves `richer_targets.b1_quantiles` as it is. Whether to change it is hers.

Coverage is the part that moves (lead 1 level targets by 4 to 7 points), so a coverage claim about B1 on these targets is stated with the form it uses. Nothing in step 2's published reading rests on B1's coverage.
