# Data Quality Decisions

These open decisions must be resolved before fitting models to the affected fields.
They are recorded publicly so that a green software test suite is not mistaken for
validated economic data.

## SEC Form N-MFP cross-section coverage

The quarterly SEC flat-file extract can contain one complete reporting month plus
amendments and late filings for adjacent months. Aggregating every `REPORT_DATE` as
if it represented the full industry creates implausible level changes that could be
mistaken for genuine stress.

**Resolved** by `declared_coverage_floor` (implemented at `9e67f43`, merged into
`main` at `f52c7c8`): a minimum count of distinct reporting entities per reference
date is declared in the source registry, cross-sections below the floor are excluded
from the modeling panel, and the exclusion is recorded separately from ordinary
missingness.

**Consequence, and it is larger than the fix.** Applied to the single quarterly extract
currently held, the floor admits exactly one reference date. See "N-MFP series length"
below. The floor is correct; the panel it produces is one observation, and that is a
property of how many archives have been downloaded rather than of the rule.

The floor is an absolute count, not a fraction of a trailing median. That is
deliberate: the trailing median in the held extract is itself computed from the
adjacent straggler months, so deriving the guard from it would admit the incomplete
cross-sections the guard exists to reject. A backfilled history must still establish
whether the absolute floor remains conservative as the industry's reporting population
changes, but any revision needs evidence independent of the cross-section it guards.

## N-MFP accounting-identity tolerance

The current assets-to-liabilities identity uses an absolute tolerance of USD 0.5
billion. An absolute bound calibrated on a multi-trillion-dollar cross-section can
be too permissive for a small or partial extract.

**Deliberately deferred at `7ea8f08`.** The argument for a relative bound rested
on the admitted cross-sections spanning roughly 4500x in size, where one absolute number
is 35 ppm of the largest month and a quarter of the smallest. Excluding under-covered
cross-sections removes exactly those small months: the residuals that made the case are
the ones the floor rejects. Post-floor, one month is admitted, at 0.312 USD billion on
9,005 USD billion of net assets, or 35 ppm.

Changing the tolerance now would calibrate a shared-schema shape against a single
observation, which is the failure the change was meant to prevent. The decision waits on
a backfilled history with at least three admitted months.

**Interim position:** the absolute bound of USD 0.5 billion is retained, and its
`tolerance_note` must state that it is calibrated against one admitted cross-section and
has not been tested against a second. It remains a provisional ingestion check, not
evidence that a cross-section represents the market.

## Treasury-settlement aggregation

The current adapter combines Treasury offering amounts by issue date into one
`treasury_settlement` series. This removes security type and tenor and does not
separate SOMA-related amounts from the private-sector cash drain.

**Proposed resolution:** derive separate bill, coupon, and SOMA components before
model fitting. If a single aggregate is retained for the first empirical version,
the source limitation must explicitly state what was combined and the model report
must test whether the simplification affects conclusions.

## N-MFP series length: one archive yields one usable month

The SEC quarterly flat-file extract contains one complete reporting month plus
amendments and stragglers for adjacent months. After the coverage floor is applied, one
extract therefore yields **one** monthly cross-section — roughly one archive per usable
observation.

At the time of writing the repository holds one archive, so `mmf_net_assets` has one
`ref_date` (alongside 23 daily shareholder-flow dates, which are unaffected).

**Consequence for modeling:** the monthly `mmf_*` series cannot support a fit of any
kind, and no benchmark may take a monthly N-MFP field as a regressor until several
archives are ingested. The daily flow series are not subject to this. This is a data
availability limit, not a modeling choice, and a green test suite says nothing about it.

**Required resolution:** backfill the SEC monthly N-MFP data sets and the earlier
quarterly sets, applying the coverage floor to every reference date found rather than
trusting the archives' own contents.

## N-MFP schema drift is a silent-emptiness hazard, not a loud one

The adapter reads four tables by hard-coded name and reads columns out of them with
`record.get(...)`. Form N-MFP has been through multiple versions over the archive period.
The two failure modes are not equally safe:

- a **missing table** raises, and is caught immediately;
- a **renamed or restructured column** in a table that still exists yields `None`, the
  row is skipped, and the archive parses "successfully" while contributing nothing, or
  contributing a partial balance sheet that still satisfies the accounting identity
  because both sides lost the same rows.

The second mode produces no error, no missingness signal, and a green identity check. It
is the coverage failure one level lower down: a check computed from the same partial
extract it validates cannot fail.

**Required resolution:** version boundaries established empirically from the archives
themselves — table and column lists diffed against the schema the parser assumes — and a
posture of **refusing** an archive that cannot be read faithfully rather than parsing
what it can. A partially-read archive that passes the identity check is worse than no
archive. Overlap between quarterly and monthly sets covering the same month, and between
original and amended accessions for the same series and report date, must be shown not to
double count.

## The ON RRP channel is declared, empty, and unverified

`mmf_on_rrp` is a declared field of the source registry that has never produced a single
row against real data. It is derived by testing three security-**description** fields of
a repo holding for the substring `FEDERAL RESERVE`; the string occurs zero times in the
holdings table of the archive held. The one test covering the branch asserts a value
against a fixture written for the purpose, which demonstrates that the match operator
works, not that the data keeps the counterparty where the adapter looks for it.

Two consequences:

- Absence is currently **indistinguishable from a parse failure**. No row is emitted,
  `structural_zeros` is empty and `structural_zeros_reviewed` is `false`, so "money funds
  held no Fed ON RRP" and "we never found it" have the same representation.
- `mmf_repo_holdings` is affected wherever this is. The Fed leg is added to both series,
  so private-sector money-fund repo is the difference between them. A missing ON RRP leg
  does not merely blank one series; it silently reclassifies Fed exposure as private repo
  in the other.

For the reference date currently held the true value is very likely near zero, since the
Fed's own ON RRP series runs under one billion daily over the same period. **That is not
evidence the derivation works.** Where the true value is near zero, a correct matcher and
a broken one are observationally identical. Only a period in which money funds held ON
RRP at scale distinguishes them.

**Required resolution:** establish where Form N-MFP records repurchase-agreement
counterparty identity; make an absent declared field recordable without coercing it to
`0.0`, which would destroy the very distinction the structural-zero declaration exists to
preserve; and either demonstrate the derivation against a period of material ON RRP usage
or declare the field unverified rather than declared. An unqualified
`structural_zeros_reviewed: true` justified only by a near-zero period is not a
resolution.

## Decision rule

These are data-modeling decisions, not formatting cleanup. Each resolution requires:

- a machine-readable declaration where possible;
- a behavioral test that can fail on independently anchored data;
- an updated source limitation and quality report; and
- a short rationale in the empirical report.
