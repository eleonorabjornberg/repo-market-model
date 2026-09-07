# Data Quality Decisions

These open decisions must be resolved before fitting models to the affected fields.
They are recorded publicly so that a green software test suite is not mistaken for
validated economic data.

## SEC Form N-MFP cross-section coverage

The quarterly SEC flat-file extract can contain one complete reporting month plus
amendments and late filings for adjacent months. Aggregating every `REPORT_DATE` as
if it represented the full industry creates implausible level changes that could be
mistaken for genuine stress.

**Required resolution:** declare a minimum count of distinct reporting entities per
reference date in the source registry. Exclude cross-sections below that floor from
the modeling panel and record the exclusion separately from ordinary missingness.
At least one test must establish that the rule rejects an incomplete real snapshot;
a synthetic fixture alone cannot demonstrate that the guard has power.

## N-MFP accounting-identity tolerance

The current assets-to-liabilities identity uses an absolute tolerance of USD 0.5
billion. An absolute bound calibrated on a multi-trillion-dollar cross-section can
be too permissive for a small or partial extract.

**Proposed resolution:** after incomplete cross-sections are excluded, calibrate a
relative tolerance in parts per million, with a small absolute floor for rounding.
The registry schema and validator should express both components explicitly. Until
then, the current tolerance is a provisional ingestion check, not evidence that a
cross-section represents the market.

## Treasury-settlement aggregation

The current adapter combines Treasury offering amounts by issue date into one
`treasury_settlement` series. This removes security type and tenor and does not
separate SOMA-related amounts from the private-sector cash drain.

**Proposed resolution:** derive separate bill, coupon, and SOMA components before
model fitting. If a single aggregate is retained for the first empirical version,
the source limitation must explicitly state what was combined and the model report
must test whether the simplification affects conclusions.

## Decision rule

These are data-modeling decisions, not formatting cleanup. Each resolution requires:

- a machine-readable declaration where possible;
- a behavioral test that can fail on independently anchored data;
- an updated source limitation and quality report; and
- a short rationale in the empirical report.
