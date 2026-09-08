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

## A cross-section is not an archive

Two decisions in the N-MFP adapter are made per archive that are not properties of an
archive. Both were correct when the repository held one extract, and the backfill made
them wrong without anything going red, because each archive on its own still looks as it
always did.

**Supersession is resolved inside `_sec_nmfp_rows`, over one archive's submissions.** On
`2016-04-30` there are 506 submissions across five archives for 413 distinct series.
Resolved globally, 93 are superseded — **47 of them by a filing in a different archive**.
Those 47 are carried in the panel as their superseded originals: over 11% of that
cross-section holds a value a later filing corrected. The coverage floor compounds it,
because the amending cohorts are small and are excluded as stragglers, which is the right
verdict about a cross-section and the wrong one about an amendment.

**Decided:** supersession is per `(SERIESID, REPORTDATE)` across every archive; coverage
is per `REPORTDATE` across every archive; neither is per archive. Landing this does not
fix the identity violation — on `2016-04-30` the residual is about 680 ppm before and
after, because the corrections fell on both sides and cancelled.

## The split month-end

A month-end that is not a business day splits the reporting universe across two adjacent
`REPORTDATE`s: funds reporting as of the last business day and funds reporting as of the
last calendar day. 2013-06 files 159 series on the 28th and 473 on the 30th; together 632,
against 629 and 634 in the adjacent complete months.

Because the coverage floor judges a reference date, in a split month the whole universe is
never in one cross-section, and usually only the larger half clears the floor. Where both
halves cleared it — 2011-07 and 2011-12 — the same month contributes two partial
cross-sections to the panel. The alternating identity scale, roughly 5,500 against 3,900
USD billions, tracks this split exactly, so some of the residual spread above is partial
cross-sections being reconciled as though whole.

**Decided: a split month-end is one cross-section, assembled by month.** This removes the
alternation, makes "the observed complete-month count" unambiguous — which the per-era
floor needs — and stops the identity being evaluated on a partial universe. It changes
what the early era admits, and that consequence is accepted rather than discovered: it
must be reported when it lands.

## Whether a source may abort a build it contributes nothing to

`mmf_assets` is refused by the pricing function in every build, because `sec_nmfp` is a
`snapshot_retrieved_at` source with no declared revision policy. The source therefore
supplies no column to the wide panel — and a violated identity in it still halts the whole
build, including builds of the eight columns that have nothing to do with it.

**Decided: the identity verdict is always recorded in the quality report; the build aborts
only for a source that actually supplies a column it built.** This is a scoping of the
guard and not a loosening of it. A violated identity in a source the panel depends on
still stops the panel; a violated identity in a source the panel does not contain is a
finding about that source, reported where findings go. Silently skipping the evaluation
would be the loosening, and is not what this says.

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

**The deferral's condition is now met, and its premise is void.** The backfill supplies
97 archives and 192 admitted cross-sections, of which 124 have every declared identity
term observed. The bound is not merely uncalibrated against them; it is refuted by them:

- **69 of the 124 evaluable cross-sections exceed the absolute 0.5 USD billions** — a
  majority, not a tail.
- Residual as a fraction of the cross-section: median 123 ppm, p90 786 ppm, p99 5754 ppm,
  maximum 6395 ppm on 2021-03-31 at 35.14 USD billions.
- **All 69 violating reference dates carry their month's largest cross-section.** They are
  the complete months. No coverage floor can clear this, and a floor tuned until the
  identity agreed would be the anchoring failure this repository keeps finding.
- The `tolerance_note` says 0.5 is "about 35 parts per million of the largest
  cross-section observed". The median admitted cross-section is over three times that,
  and the worst is nearly two hundred times.

An absolute bound also tightens as the industry grows: 0.5 USD billions is about 141 ppm
of a 3,500 billion cross-section and about 54 ppm of a 9,200 billion one. A bound that
gets stricter every year without anyone deciding it should is not a bound anyone chose.

**Decided: the number is calibrated last, not now.** Two changes below — cross-archive
supersession and the split month-end — both move the residuals a calibration would be
computed from, and computing it first would mean fitting a shared shape to numbers that
are about to change. Admitting every currently-evaluable cross-section would need roughly
6400 ppm, which is large enough that it would be a judgement about what the identity
means rather than a tolerance, and it would make the check vacuous.

What is settled: **the absolute bound is known to be wrong and is retained only because
nothing yet depends on it.** That is a different statement from the one above it, and the
earlier deferral must not be read as still standing.

**Interim position:** the absolute bound of USD 0.5 billion is retained, and its
`tolerance_note` must state that it is calibrated against one admitted cross-section and
has not been tested against a second. It remains a provisional ingestion check, not
evidence that a cross-section represents the market. **The note now says this**; before,
it read as though USD 0.5 billion had been calibrated against the market rather than
against one extract.

**The schema half has landed and the number has not.** `contract.py` now accepts
`relative_ppm` alongside `absolute` on any identity tolerance, with `absolute` acting as
a floor under the relative part, and `data.py` resolves the bound at the magnitude of
the quantity the identity is about. Nothing declares a relative bound. This was
separated out deliberately: the deferral is about calibrating a number against one
observation, and a schema calibrates against nothing. The consequence is that lifting
this deferral is a one-line edit to a declaration in `metadata/sources.json` rather than
a change to a shared contract with two tracks' tests attached to it.

The restatement of the tolerance rules that used to sit in the registry conformance test
required `absolute` to be present, so an absolute-only bound was the only kind the
repository could express. That was not a decision anyone made; it was a check written
before the question came up. A first attempt at this section's decision changed the
number as well, on the strength of the Track A memo and a stale open-item list, and had
to be split back apart — this file is the record that was overridden, and it is tracked
precisely so that cannot happen quietly.

## Treasury-settlement aggregation

The current adapter combines Treasury offering amounts by issue date into one
`treasury_settlement` series. This removes security type and tenor and does not
separate SOMA-related amounts from the private-sector cash drain.

**Proposed resolution:** derive separate bill, coupon, and SOMA components before
model fitting. If a single aggregate is retained for the first empirical version,
the source limitation must explicitly state what was combined and the model report
must test whether the simplification affects conclusions.

**Half done.** The `limitation` now states what was combined: all security types
aggregated, SOMA add-ons included, tenor and the private-versus-Fed split not
represented, and `security_type`, `security_term` and `soma_accepted` present in the
snapshot and unread, so the split needs no new download. It also retires the note it
replaced, which said announcement and result vintages must be separated to avoid using
auction outcomes too early. That risk is avoided by construction — `record_date` drives
`available_at` and the adapter reads `offering_amt` alone, never `total_accepted`,
`high_yield` or `bid_to_cover` — so the note described a hazard the adapter cannot have
while saying nothing about the one it creates, which reads as vigilance.

Still open: the split itself, and the model report's test of whether the simplification
affects conclusions. Both matter to this project specifically. Bill and coupon
settlements have different collateral and reserve-drain profiles and bill supply is
close to the centre of the 2018–19 episode; SOMA add-ons do not drain private cash, so
the aggregate overstates the private-sector drain exactly when the Fed is rolling over
most heavily.

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
