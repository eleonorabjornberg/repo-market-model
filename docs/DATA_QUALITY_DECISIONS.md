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

> **Resolved at `febba6d`: calibrated, and left absolute.** Everything below this
> block is kept as the record of what was known when each part of it was written,
> annotated rather than restated. Two of its measurements were taken before the
> per-era coverage floor landed and on a different denominator than the verdict
> uses, and they no longer agree with the derivation now carried in
> `metadata/sources.json`'s `tolerance_note`: this section counts **69 of 124**
> exceeding and a median residual of **123 ppm** of the cross-section, where the
> calibration counts **80 of 124** refused and a median of **171 ppm** of scale
> taken as the larger side of the identity, the way the verdict takes it. The
> maximum agrees at 6395 ppm. **Neither number has been reconciled against the
> other**, and the reconciliation is a human-side item, not a reason to prefer
> one; the `tolerance_note` is the one derived after the floor.
>
> What the calibration settled, and this section did not anticipate: the case for
> a relative bound rested on a scale range that the per-era floor and monthly
> assembly removed. Over the 2.9x range that remains, scale explains almost none
> of the residual spread (rank correlation +0.05), so `relative_ppm` has nothing
> to correct. The bound stays where it was — not as a provisional number nobody
> has got to, but as a measured decision — and the majority it refuses is
> explained by a one-sided identity break running 2024-06 to 2026-02, beginning
> exactly at the `n_mfp2`-to-`n_mfp3` form-version boundary. **That break is a
> finding against the ingestion or the filings and is not this number's to
> absorb.** It is answered below, under "The 2024-06 identity break is in the
> filings", and the answer leaves this number where it is.

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

**The deferral's condition was met, and the calibration has now run.** It landed at
`febba6d`, and its answer is no. The tolerance stays `{absolute: 0.5, unit: "USD
billions"}` and the registry's `tolerance_note` carries the derivation in place of the
deferral.

Derived over the 124 admitted cross-sections on which every declared identity term is
observed; 65 further admitted cross-sections are not evaluable at all, being the `n_mfp1`
era, which does not report this balance sheet:

- Scale, taken as the larger side of the identity the way the verdict takes it, runs 3178
  to 9254 USD billions — a factor of 2.9, and not the three orders of magnitude this
  section argued from. That population no longer exists: the per-era coverage floor
  refuses the small cross-sections that made the case and monthly assembly merged the
  split month-ends that halved the rest. Over a 2.9x range a relative bound and an
  absolute one are nearly the same bound.
- Normalising the residual by scale moves its dispersion from 0.764 to 0.745 decades and
  leaves its rank correlation with scale at +0.05. Scale explains almost none of the
  spread, so a `relative_ppm` has almost nothing to correct. This is the measurement the
  argument above assumed would come out the other way.
- The bound admits 44 of the 124 and refuses 80. The `tolerance_note` records the outcome
  in those terms, as "an ingestion check that currently fails on a majority of the
  population it checks", and declines to widen the bound into a description of that
  population.
- From 2024-06 to 2026-02 the identity breaks one-sidedly in all 21 months, beginning
  exactly at the declared `n_mfp2` to `n_mfp3` boundary and resolving after it. A bound
  sized to admit that would be sized to admit a defect that starts and stops on a
  form-version boundary. It is a finding against the ingestion or the filings, it is open,
  and it is not this number's to absorb.

**The figures this section carried before `febba6d` are withdrawn.** They were derived at
`37fa054` and read: 192 admitted cross-sections, 69 of 124 exceeding the bound, a median
of 123 ppm. `8d77691`, `346d4ff` and `94bf2db` all landed after them, and all three move
the residuals a calibration is computed from — which the paragraph below anticipated in
as many words, about a calibration that had not yet run. The two derivations agree on the
extremes, 6395 ppm at 35.14 USD billions, and disagree on the count and the median. The
later one is the one computed on the current assembly.

**Neither derivation is reproducible from a clone.** Both were computed against
`data/raw/sec_nmfp/`, which is gitignored, and published as prose; nothing in the suite
can re-derive either. That is why the disagreement above is settled by commit order rather
than by recomputation, and it is the open item this section leaves behind.

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

**Interim position, discharged.** This section used to require that the
`tolerance_note` state it was calibrated against one admitted cross-section and had not
been tested against a second. That requirement is met and withdrawn: the note is
calibrated over 124 of them. What the note must still say, and does, is that this is an
ingestion check and not evidence that a cross-section represents the market.

**The schema half landed and the number was declined.** `contract.py` now accepts
`relative_ppm` alongside `absolute` on any identity tolerance, with `absolute` acting as
a floor under the relative part, and `data.py` resolves the bound at the magnitude of
the quantity the identity is about. Nothing declares a relative bound. This was
separated out deliberately: the deferral is about calibrating a number against one
observation, and a schema calibrates against nothing. The consequence is that lifting
this deferral is a one-line edit to a declaration in `metadata/sources.json` rather than
a change to a shared contract with two tracks' tests attached to it. The deferral has
since been lifted and answered no, so that edit stays available and unused. `contract.py`
resolves the pair as `max(absolute, relative_ppm * 1e-6 * scale)`, and
`IdentityToleranceScaleTests` in `tests/test_data.py` is what keeps that path exercised
while no declaration uses it.

The restatement of the tolerance rules that used to sit in the registry conformance test
required `absolute` to be present, so an absolute-only bound was the only kind the
repository could express. That was not a decision anyone made; it was a check written
before the question came up. A first attempt at this section's decision changed the
number as well, on the strength of the Track A memo and a stale open-item list, and had
to be split back apart — this file is the record that was overridden, and it is tracked
precisely so that cannot happen quietly.

## The 2024-06 identity break is in the filings, and it is one cash line

The calibration above left one thing open and called it the largest thing open: from
2024-06 to 2026-02 the identity breaks one-sidedly in all 21 months, assets exceeding
liabilities plus net assets, beginning exactly at the declared `n_mfp2`-to-`n_mfp3`
boundary. **It is the filings.** The adapter reads what the filers filed.

**The finding about this repository is the unit the identity is evaluated on.** The
verdict in `src/repo_model/data.py` is taken over the aggregated cross-section: one
residual per reference date, summed across every reporting series. An eight-billion-dollar
defect in one filer's balance sheet arrives at that verdict as a single number attached to
a whole month, arithmetically indistinguishable from three hundred funds each rounding the
same way — so the question "is this the bound or the data" could not be asked of the data
at all. Evaluated one filing at a time it answers immediately.

**The mechanism.** For a small set of series, `TOTALVALUEPORTFOLIOSECURITIES` plus
`TOTALVALUEOTHERASSETS` already equals `TOTALVALUELIABILITIES` plus `NETASSETOFSERIES`,
while `CASH` is positive: the filer has counted its cash inside another asset line and
reports it again on the cash line as a memo. The adapter adds all three asset terms, as
the form's instructions define them, so the cross-section overstates assets by exactly
that series' cash. Written as a ratio,

    r = -((securities + other assets) - (liabilities + net assets)) / cash

`r` is 1 when cash is additive and 0 when it is a memo, and the two bands that are neither
answer are counted rather than folded into the nearest one. On the declared archive set,
across every archive and era: 75 filings sit at `|r| < 0.10`; 33 sit in the 0.10–0.90
partial band, of which three fall inside this break's window and none of the three carries
more than USD 0.3 billion of cash; 28 carry a residual the cash line does not explain at
all, and **not one of those 28 is inside the window**. The classification is categorical
rather than a threshold anybody chose, which is the only reason it is worth stating as
one.

**The population.** 64 of the 75 memo filings fall in the 20 consecutive report months
2024-06 to 2026-01, across ten distinct series; the run's twenty-first month, 2026-02,
carries none and is a residual of about USD 1 billion with no memo filer in it. They
concentrate in two fund families — one series, `S000000128`, appears in 19 of those 20
months and carries up to USD 9.6 billion of cash, and a second family contributes
intermittently. **It is not new and it is not
random: it recurs at form transitions.** The same shape appears in 2016-06, 2016-09 and
2016-10, in the months immediately after the Form N-MFP2 relabelling, and in 2018-11, in
the same fund family. What is new after 2024-06 is that it runs for twenty months without
a gap and at ten times the size.

**What it accounts for, and what it does not.** Removing the memo filings' cash from the
asset side takes the monthly residual over those 21 months from a median of about USD 8.6
billion to about USD 1.0 billion, and from 1035 ppm of scale at the median and 2597 ppm at
its worst to about 117 and 247. What survives is a residual still positive in 20 of the
21 months, larger than the two-sided ±0.5 billion of the months on either side of the
window. **The cash line explains the size of the break and not the whole of its sign**,
and the remainder is not claimed to be explained here.

**Decided: this repository does not correct a filer's arithmetic.** Netting the memo cash
out of the asset side would be the adapter deciding what a filer meant, on the same
argument the decimal-comma hazard above is deliberately left unfixed. Three things follow
instead.

- **The identity is evaluated per reporting entity, not only per cross-section.** A
  per-entity verdict is what makes this defect a named filing rather than a month, and it
  is what any future one will surface as. That is a change to the adapter and to the
  quality report, and it is queued for Track A rather than taken here.
- **The tolerance stays where the calibration left it.** Nothing above changes the bound;
  the break was never the bound's to absorb, and it is now attributed rather than absorbed.
- **`mmf_cash` and `mmf_other_assets` are not disjoint for the affected filings**, and any
  downstream sum of the three asset terms over those months inherits the overlap. The
  panel carries both fields as filed.

**The derivation is a command, not prose.** `scripts/nmfp_identity_residuals.py` resolves
supersession across archives on `(SERIESID, REPORTDATE)`, assembles split month-ends into
one report month, evaluates the identity per filing and prints the four bands. It reaches
the residual by its own path rather than calling the adapter, and it reproduces the
`tolerance_note`'s three headline figures exactly — the median monthly residual, the
median ppm and the worst ppm. Two derivations agreeing across independent code is why
those figures can now be cited rather than merely cited from. It reads `data/raw/`, which
no clone has, so it is a script and not a test; that is the honest half of the answer to
the reproducibility complaint recorded above, and the complaint is narrowed rather than
closed.

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

When this was written the repository held one archive, so `mmf_net_assets` had one
`ref_date`. **That is no longer so.** The backfill landed at `992a91c`, which also recorded
the archive set in `metadata/sec_nmfp_archives.json`. That manifest is the count, and it is
deliberately not transcribed here: a number written where nothing can update it is the
defect this document exists to name.

**Consequence for modeling:** the monthly `mmf_*` series cannot support a fit of any
kind, and no benchmark may take a monthly N-MFP field as a regressor until several
archives are ingested. The daily flow series are not subject to this. This is a data
availability limit, not a modeling choice, and a green test suite says nothing about it.

**Resolved** by the backfill at `992a91c`, by cross-archive supersession at `8d77691`,
and by `346d4ff`, which moved the unit of assembly from the report date to the calendar
month so a split month-end is one cross-section rather than two. The coverage floor is
applied to every assembled cross-section rather than to the archives' own contents.

**What this leaves open is the floor, not the series length.** A single declared absolute
of 200 distinct `SERIESID` stands across a reporting universe that changed size by roughly
a factor of two over the archive period; the per-era replacement is specified and not yet
implemented. See the coverage section at the head of this document.

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

**Resolved** — and the two bullets above now describe the hazard rather than this adapter.
Both failure modes moved, in opposite directions, and neither reads as written any more:

- **A renamed or restructured column no longer yields `None`. It refuses the archive.**
  `NMFP_REQUIRED_COLUMNS` is derived from the balance-field and flow-field mappings the
  parser actually reads — not from a copy in the registry, which would drift from the
  parser silently — and `_nmfp_table` compares it against the header before a single
  record is parsed, naming the table and the missing columns. Implemented at `cbbc864`,
  extended to per-table refusal at `a675a11`.
- **A missing table raises only for the spine.** `_nmfp_table_if_present` returns `None`
  for an absent non-spine table, which costs the panel the fields that table supplies —
  named in `NMFP_TABLE_FIELDS` — and refuses nothing, because a field with no observation
  is a state the panel already represents. Absence and unreadability are different claims
  about a file and are now priced differently. So "a missing table raises" is true of
  `NMFP_SUBMISSION.tsv` and of no other table.

The empirical half is done too. Every archive in `metadata/sec_nmfp_archives.json` was
diffed against the schema the parser assumes, and the boundaries that scan established are
recorded in the `sec_nmfp` limitation in `metadata/sources.json`. On that set the guard
refuses no archive outright; the only refusals are absent fields, all from
`NMFP_DLYSHAREHOLDERFLOWREPORT.tsv`, which did not exist before Form N-MFP3. **Refusing
nothing is a result here, not a null:** it is what licenses the coverage floors to be
calibrated from the admitted set as it stands.

The double-counting clause is resolved separately, at `8d77691`: supersession and coverage
resolve across archives on `(SERIESID, month)` rather than within one, so quarterly and
monthly sets covering the same month, and original and amended accessions for the same
series, resolve to one cross-section rather than two.

**One hazard of this shape remains open, and is deliberately unfixed.** `_nmfp_number`
strips commas as thousands separators before `float()`, so an extract written in a
decimal-comma locale parses silently and wrong by a power of ten. It is recorded in the
`sec_nmfp` limitation and pinned to the parser by `NMFPDecimalCommaTests` at `19968d6`.
It is not fixed: a locale-sniffing heuristic would be a silent behaviour change calibrated
on data nobody has seen, and a differently formatted extract should fail loudly rather
than parse plausibly. That is the posture of refusing an unreadable header, applied to a
value rather than to a column name.

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
