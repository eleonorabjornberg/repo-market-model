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
only for a source that actually supplies a column it built** — one that supplied at least
one of its declared `fields` among the rows the build can see. A source that supplied none,
such as `nyfed_fr2004` in a build with no FR 2004 snapshot, is not evaluated over nothing;
one whose terms are observed but never together on one date still raises, because that is
a finding about the data. This is a scoping of the
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
> maximum agrees at 6395 ppm. **Reconciled, on the data layer's derivation: the
> `tolerance_note`'s derivation is the one this repository uses.** Not because it
> is the later of the two, which was the only argument available while the
> disagreement stood, but because its denominator is *named* — scale, taken as
> the larger side of the identity — and it is the denominator the verdict itself
> takes. "Of the cross-section" names no side. The figures in this section below
> are the earlier derivation, kept as the record of what was known when they were
> written and deliberately not restated.
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
later one is the one computed on the current assembly, and it is the one adopted above.

**Neither derivation was reproducible from a clone when this was written.** Both were
computed against `data/raw/sec_nmfp/`, which is gitignored, and published as prose; nothing
in the suite could re-derive either, which is why the disagreement above stood on commit
order for as long as it did. `scripts/nmfp_identity_residuals.py` has since re-derived the
`tolerance_note`'s three headline figures by an independent path, so the adopted derivation
rests on a command rather than on a date. It still reads `data/raw/`, so a clone still
cannot run it, and that half of this paragraph stands.

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
a change to a shared contract with tests on both sides of it. The deferral has
since been lifted and answered no, so that edit stays available and unused. `contract.py`
resolves the pair as `max(absolute, relative_ppm * 1e-6 * scale)`, and
`IdentityToleranceScaleTests` in `tests/test_data.py` is what keeps that path exercised
while no declaration uses it.

The restatement of the tolerance rules that used to sit in the registry conformance test
required `absolute` to be present, so an absolute-only bound was the only kind the
repository could express. That was not a decision anyone made; it was a check written
before the question came up. A first attempt at this section's decision changed the
number as well, on the strength of an untracked memo and a stale open-item list, and had
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
  quality report, and it is left as follow-up work rather than taken here.
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

The adapter first combined Treasury offering amounts by issue date into one
`treasury_settlement` series. That removed security type and tenor and did not
separate SOMA-related amounts from the private-sector cash drain.

**Proposed resolution:** derive separate bill, coupon, and SOMA components before
model fitting. If a single aggregate is retained for the first empirical version,
the source limitation must explicitly state what was combined and the model report
must test whether the simplification affects conclusions.

**Done at the adapter.** It reads `security_type` and `soma_accepted` from the snapshot
already committed and emits the aggregate beside its three components. None of the four
is split into panel columns yet.

**Corrected before the split was defined (human, 10 Sep): `offering_amt` excludes SOMA.**
This page and the limitation said the aggregate included SOMA add-ons. It does not: the
Federal Reserve's rollover bids are noncompetitive tenders treated as add-ons to the
announced auction size, and Treasury increases the total issue by the SOMA award
(Federal Reserve Bank of New York, "FAQs: Treasury Rollovers"). The aggregate is
therefore already the public leg, and the claim below that it overstates the private
drain was the wrong way round.

**The split, contract side.** `src/repo_model/contract.py` defines three columns in USD
billions: `treasury_settlement_bill` and `treasury_settlement_coupon`, each a sum of
`offering_amt` over a declared `security_type` set (bills `Bill`, `CMB`; coupons `Note`,
`Bond`, `TIPS`, `FRN`), and `treasury_settlement_soma`, a sum of `soma_accepted`. The
identity is `treasury_settlement` = bill + coupon at an absolute `1e-9`, since both sides
sum the same values; SOMA sits outside it. A `security_type` in neither set raises --
never a coupon by default, which is the residual trap one level down. The sets follow
Treasury's bills-versus-coupons convention; the committed snapshot carries `Bill`,
`Note` and `Bond` only, so `CMB`, `TIPS` and `FRN` are declared and not yet exercised.

**Availability.** `record_date` in this snapshot is the settlement date (it equals
`issue_date` on every record), and `available_at` is 23:59 New York on it for all four
series. `soma_accepted` is an auction result where `offering_amt` is announced; dating
both at settlement puts each after its auction, and the adapter refuses a result whose
`record_date` precedes its `auction_date`. It never reads `total_accepted`,
`high_yield` or `bid_to_cover`.

**Panel columns (human, 11 Sep):** `treasury_settlement_bills`, `treasury_settlement_coupons`
and `treasury_settlement_soma`, each in USD billions. A gross figure blends three different
pressures: bill settlements drain cash and are primary-dealer financed; coupon settlements
need repo financing capacity of their own; SOMA add-ons are a non-market adjustment to the
Fed's balance sheet. **A business day with no settlement reads `0.0`** (`build_daily_panel`
rule 8, the first of two declared exceptions to rule 4; rule 10 is the other, and
carries a weekly column's last print forward under a bound), a true zero rather than a fill: the auction
record lists every settlement, so a day without one settled nothing. The zero holds only
inside the snapshot's coverage, from its first settlement date to the New York date of its
`retrieved_at`; a day it cannot speak to stays a hole. SOMA reads `0.0` only on a day with
no settlement at all, so a withheld SOMA result on a settlement day stays a hole. Still
open: the model report's test of whether the aggregate's simplification affected
conclusions.

**The zero is bounded by the build cutoff (A25).** Rule 8 wrote `0.0` on any settlement-free
business day inside the snapshot's coverage, and held only because `sofr` happens to be
published the next day — a rule resting on another column's release lag is a value, not a rule,
and a build declaring no required column has no such guarantee. A grid date now reads `0.0`
only once the auction record that would have listed a settlement is itself observable at the
build cutoff, derived from the same declared `release_lag` the adapter writes into `available_at`
on the rows that are there. A basis other than `record_date` is refused rather than
reinterpreted: a bound that had to be guessed is the unbounded zero one level in. No published
figure moves — the bound is slack on every grid date of the published manifest.

**And the build records how many it wrote (A27).** `DailyPanelBuild.settlement_zeros` counts, per
built column and over the same grid as `holes`, the values that are rule 8 zeros — counted at the
write, not over the dates the cutoff and coverage bounds made eligible, which are a different and
larger set. Holes and written zeros are the two halves of the same grid, and until now only one
half was recorded, so a reader could not tell a fully observed column from one a tenth of whose
values were written in place of an absence. The count is also the audit of the cutoff bound above,
on the build that actually ran.

The **file** manifest does not carry it yet, and that is deliberate rather than forgotten: adding
the key to what `write_daily_panel` writes makes the Milestone A reproduction compare a key that
exists on one side only, and a published record is re-scored by a human, never rewritten inside a
block. On the published build the count is `0` on every column — the tracked funding inputs carry
no auction snapshot — so landing the file half moves no figure, only the key.

## SOFR tail percentiles stay out of the feature panel

**Decided (human, 11 Sep):** `SOFR_p1` and `SOFR_p99` are parsed but are not panel
columns; they may return as an optional diagnostics extension. The tails are sensitive to
bilateral trade quirks and to operational or reporting outliers rather than clearing
rates, and `sofr_p25`/`sofr_p75` already carry dispersion without that leverage.

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

## The ON RRP channel is derived, and this page was wrong about it

**Superseded, and the correction is the finding.** This section previously read *"The ON
RRP channel is declared, empty, and unverified"*, and stated that `mmf_on_rrp` "has never
produced a single row against real data" and that `FEDERAL RESERVE` "occurs zero times in
the holdings table of the archive held". Both sentences were true of the single archive
held when they were written. Ninety-seven archives are held now and both are false.

**The derivation is a command, not prose.** `scripts/nmfp_on_rrp_channel.py` counts the
occurrences per field without importing the adapter, and under `--series` prints the series
the adapter itself produces. Every number below comes from one run of it.

**Where Form N-MFP records repurchase-agreement counterparty identity: in `NAMEOFISSUER`.**
That was this section's first required resolution and it is answered. For a repurchase
agreement the counterparty *is* the issuer, so there is no counterparty table to look for.
`NMFP_COLLATERALISSUERS` is the repo-specific table and it carries collateral issuers,
which is a different fact -- and carries one occurrence of the string across all
ninety-seven archives. The join in `src/repo_model/ingest.py` names its variable
`counterparty`, and the name is accurate.

- `FEDERAL RESERVE` occurs **18,119 times** in the three joined fields, in **87 of the 97**
  archives: 9,137 in `NAMEOFISSUER`, 8,982 in `TITLEOFISSUER`, and **none at all** in
  `BRIEFDESCRIPTION`. Calling the derivation a search of "security-description text" -- as
  this page and `PROJECT_STATUS.md` both did -- named the one field of the three that
  contributes nothing.
- Those matches fall on 9,175 holdings rows, of which **9,161 are repo-category**. The
  census reaches that by a deliberately loose criterion, any `INVESTMENTCATEGORY`
  containing "Repurchase Agreement", while the adapter matches a closed set per era. Two
  criteria that could disagree do not.
- The adapter emits **200 `mmf_on_rrp` rows over 156 reference dates**, and the series is
  the facility: nothing until 2013-09-30, the first month-end after the ON RRP facility
  opened, at 48.6 bn; a peak of **2,273.8 bn on 2022-12-31, 76.4% of `mmf_repo_holdings`**
  at that reference date; 6.8 bn at 2026-06-30. Two observations precede the facility --
  1.2 bn at 2011-03-31 and 0.8 bn at 2012-11-30 -- and are not explained here.

**`mmf_repo_holdings` is not reclassifying Fed exposure as private repo.** This page warned
that a missing ON RRP leg would silently do so. The leg is present, so it does not, and the
size of the error the warning described is now measurable rather than hypothetical: it
would have peaked at the same 2,273.8 bn.

**What survived was the sharper half, and the review now answers it.** Absence was
indistinguishable from a parse failure while `structural_zeros` was empty and
`structural_zeros_reviewed` was `false`, and the series supplied the instance that
argument always lacked. Thirty-three repo report
months carry no `mmf_on_rrp` row, and they are two different things wearing one
representation: thirty-two run 2010-11 to 2013-08 and precede the facility, so their true
value is zero for a reason a reviewer could state, while one is 2026-07-31, a month in
which the facility existed and the month before it reported 6.8 bn. Nothing in the panel
tells them apart, and a field that cannot say "zero, and here is why" cannot say it for
either.

**How this stayed wrong after it was known.** The counts above were derived two days before
this correction, into a working memo that `.gitignore` excludes, and never transcribed. The
brief that queued the question afterwards was written from this page and spent a work item
re-deriving an answer that already existed. The mechanism is not carelessness: **no test in
this suite can see `data/raw/`**, so every claim this repository makes about the archives is
prose, and prose does not decay-check. The sentence was true when written, and nobody
re-measured it when ninety-six more archives arrived.

**Reviewed (human, 10 Sep):** `sec_nmfp` declares `mmf_on_rrp` a structural zero with no
`from` and `through` 2013-08-31. It covers absent cross-sections only, so the thirty-two
pre-facility months are recorded as `declared_structural_zero` and 2026-07-31 as an
undeclared absence; the two observed pre-facility months stay observations and are still
unexplained. The review is qualified, not blanket: `reviewed_note` says it covers this
one field, and that the other ten declaring nothing is not a finding that they have no
structural zeros.

## Dealer Treasury positions: `PDPOSGST-TOT`

**Decided by the human:** `dealer_treasury_position` maps to the NY Fed Primary Dealer
Statistics series `PDPOSGST-TOT`, net outright positions in Treasury securities, total.

What "total" covers was checked rather than read off the label. In the tracked fixture
`tests/fixtures/snapshots/nyfed-primary-dealer/latest.csv`, at its weekly as-of date,
`PDPOSGST-TOT` equals the sum of bills (`PDPOSGS-B`), floating-rate notes
(`PDPOSGS-BFRN`), nominal coupons in every maturity bucket (`PDPOSGSC-L2`, `-G2L3`,
`-G3L6`, `-G6L7`, `-G7L11`, `-G11L21`, `-G21`) and TIPS in every bucket (`PDPOSTIPS-L2`,
`-G2`, `-G6L11`, `-G11`), exactly. The `C`-suffixed series in the same buckets
(`PDPOSGSC-L2C` and its siblings) are not in the sum: a glob over the two prefixes picks
them up and overshoots the total. So the column includes TIPS and
FRNs; a reader who wants nominal coupons alone, or wants to separate bill from coupon
inventory as the settlement split does, needs the components, not the total.

**The history, checked per era (human, 10 Sep).** The all-series export runs from
1998-01-28, but `PDPOSGST-TOT` begins **2013-04-03**. The earlier report used other
vocabularies (`PDPUSGTNOP` and its components from 2001-07-04, another before), which end
on 2013-03-27, so no week carries both and a splice could not be checked against an
overlap. **Decided (10 Sep): the earlier report is not mapped; the column begins
2013-04-03.** The panel it feeds begins 2018-04-03, bound by SOFR, so nothing reads the
earlier weeks. A panel reaching before 2013 would reopen this, from the New York Fed's own
concordance rather than by matching series names. From 2013-04-03 the total equals its components exactly on every weekly as-of
date, in three eras whose component sets differ: no FRN bucket until 2015-01-07, and one
`PDPOSGSC-G11` bucket until 2021-12-29, split into `-G11L21` and `-G21` from 2022-01-05.
So the thirteen components are the current era's, and the identity is declared per
era (`eras` in `metadata/sources.json`): each week is checked against its own era's terms. Two files now carry FR 2004 and they must not be taken for each other.
`tests/fixtures/snapshots/fr2004/pdposgst_tot_and_components.csv` is the tracked **extract**
(the total and every non-`C` component, lines copied byte for byte), made and re-checked by
`scripts/extract_fr2004.py`, whose sidecar records the export's digest and the three eras; it
is what every figure here about weekly as-of dates describes. The **export** it is cut from is
no longer only gitignored under `data/raw/fr2004/`: the adapter's own fetched copy is tracked
beside the other funding snapshots under
`tests/fixtures/snapshots/funding_inputs/nyfed_fr2004/`, and it carries every series the report
has published since 1998-01-28, so its as-of date count is larger and is not the extract's.
`FR2004ExtractCountProseTests` recomputes the extract's counts and fails any prose site that
states a different one.

Wired: the `nyfed_fr2004` adapter supplies the column through `contract.FEATURE_FIELDS`,
millions converted to billions. It dates each series by its own as-of date, never the
file's, and reads `*` (suppressed for confidentiality) as neither zero nor a failed read:
it is recorded as `suppressed` (below).
The published Milestone A panel does not carry the column; it is pinned to its manifest's
`built_columns`.

## An absent value keeps its reason

The SEC's Form N-MFP data-set readme marks fields nullable but defines no token for a
missing value, so `"."` in the archives is undocumented by the publisher. The New York
Fed's FR 2004 export writes `*` for a figure suppressed for confidentiality.

**Decided: every absent cell is recorded with the token it was read from.** An absent
cell still yields no observation; the ingest's quality report records it, in runs of
consecutive rows, with one reason of `blank`, `na`, `dot`, `null` or `suppressed`. Each adapter keeps its own tokens: New
York Fed rates and N-MFP accept blank, `NA`, `N/A` and `"."`; FRED blank and `"."`;
Treasury auctions blank and Fiscal Data's string `"null"`; bill rates blank; FR 2004 `*`
in a declared series. A token outside an adapter's list is refused, and so is a reason
outside the vocabulary.

## Bill-rate panel columns

**Decided (11 Sep):** `tbill_4w` and `tbill_13w`, each the coupon-equivalent yield in
percent as Treasury publishes it. The 4-week bill is money funds' nearest substitute for
overnight repo and the 13-week the benchmark bill; both run unbroken from 2018. The basis
is actual/365 against SOFR's actual/360, documented rather than converted. Treasury takes
the quotations at about 3:30 PM; availability is declared at end of day, so a 16:00
decision reads the previous business day's rate. The 2026 export has no manifest, so a
reported run cannot draw on 2026 bill rates until one exists.

## An empty repo cross-section is excluded, with its reason

A cross-section whose holdings table was read in a declared category era and matched no
repo category supplies no `mmf_repo_holdings`, and nothing recorded why. The fund industry
always holds repo, so an admitted month with none is a vocabulary failure until shown
otherwise. **Decided (11 Sep):** it is excluded like a cross-section below the coverage
floor, with the reason `no_repo_rows` in its coverage record; it is never a hole that looks
like a quiet month, and never a zero. Judged per vintage (A21): an amendment that removes
every repo row excludes only its own vintage, which writes no rows; earlier vintages stand.

**The sibling case, decided the same way (A24).** An amendment that *keeps* its repo rows but
swaps the counterparty away from the Fed supersedes every submission that supplied
`mmf_on_rrp`, and re-totalling what is left gave a bare `0.0` that nothing declared. **Decided:
that vintage writes no row and its coverage record names the cause**, `no_fed_counterparty` in
`CrossSectionCoverage.withheld_fields`, from a closed vocabulary refused outside it exactly as
`exclusion_reason` is. It is the same rule one level down: whole cross-section, then single
field of an admitted one. `mmf_repo_holdings` keeps its rows and is untouched. On the declared
archives the rule fires nowhere -- A21's census found no `sec_nmfp` repo row equal to `0.0` --
so no published figure moves; it exists so that the zero cannot appear unexplained later.

Two things that came out of it, both recorded in the tracked test docstrings rather than here.
The mutation A21 left behind has stopped discriminating, because this rule now withholds the
zero that mutation injects; its live form is the same mutation on `mmf_repo_holdings`, which
has no declared derivation, and that still kills. And a field with no declared derivation whose
last contributor is superseded still re-totals to `0.0` -- an amendment refiling every Treasury
holding under another category writes `mmf_treasury_holdings 0.0`. Same mechanism, different
criterion: the behaviour is pinned by a test so that deciding it later moves a test rather than
discovering an assumption.

## The purge is stated against the target date

`splits.clears_purge` compares a row's publication against the *scored* date:
``row_date + purge < opens``. The decision is taken at the declared decision time on
the last panel day strictly before that scored date, which is the calendar day before
only when the two are consecutive. After a weekend or a holiday the decision comes
earlier, so on those folds the rule alone no longer establishes that the last training
row had been published by the time the forecast was made. The gap was found by the
bill-rate block, whose columns carry a one-day lag, and it is recorded in
`BillRatePanelTests`' docstring.

It has since been measured rather than argued, by
`scripts/purge_availability_audit.py`, which rebuilds a published record's folds from
the panel and checks each fold's last training row against the decision instant two
ways. Under the conservative gap the run was purged at, the folds whose scored date
follows a weekend or a holiday are exactly the ones that fail, by up to about three
days. Under the release lags the sources themselves declare -- the SOFR complex final
on the next business day, the administered rate the day after its record date -- every
fold in the published four-feature runs clears the decision instant, with days to
spare. **No published figure rests on a value that had not been published.**

One case the audit used to skip now counts against it: a business-day lag whose
declared publication day runs off the end of the panel is reported **late**, not
unknown. The panel is the only calendar the audit has, so a value dated past it has not
been published by any instant the panel can name -- and the evaluation path had already
settled the same case the same way. Skipping it would have quietly exempted the folds at
the end of the panel, which is where a long-lagged column is least likely to have
arrived. The published runs are unaffected, because none of their fields lags that far;
the change is what keeps that true when one does.

That is the safe direction and not a licence to leave the rule as it stands. The margin
comes from a purge sized for a source slower than the features in use, and it narrows
as soon as a slower column joins the feature set: the bill-rate columns, the settlement
components, or the dealer positions at six business days. Restating the gap against the
decision date is a change to the split's definition and therefore the human's; until it
is made, the audit script is what establishes that a feature set is safe, and it is run
before a new column is declared. **The guard now lands.** `baseline._check_decision_relative_availability` refuses a fold,
per field, when a field's declared release lag puts the feature row's availability after the
decision instant, raising `LookAheadError` and naming the field and the fold. It took three
blocks to get there, and the two it took to *not* get there are the record: the guard was
correct from the start and the fixtures were wrong, in two different ways. The fixtures that
run at a six-day purge keep their gapped, weekday calendars and adopt the real registry's
declaration shape instead; only the one-day fixtures were re-dated onto a gapless panel, and
each reproduction literal that moved carries its old value and the reason in the docstring of
the test that pins it. The real registry is silent under the guard, and the published
`backtest` command's output is unchanged.

The guard and `scripts/purge_availability_audit.py` derive a field's availability the same way,
line for line, so the two cannot answer differently. Two questions about it are open and are
the human's: the guard reads `release_lag` directly, where the contract at the time said evaluation code
should go through `registry.max_release_lag_days` — which answers a deliberately more conservative
question and would fire where the measurement says the registry is silent; and
`max_release_lag_days` checks the declared timezone for a `record_date` source but not for a
`ref_date` one, so `ref_date` availability times are still compared naively.

## Decision rule

These are data-modeling decisions, not formatting cleanup. Each resolution requires:

- a machine-readable declaration where possible;
- a behavioral test that can fail on independently anchored data;
- an updated source limitation and quality report; and
- a short rationale in the empirical report.

## The rebuild takes all nine newly buildable columns

Nine columns the tracked manifest listed as refused now build: `treasury_settlement_bills`,
`treasury_settlement_coupons`, `treasury_settlement_soma`, `dealer_treasury_position`,
`tbill_4w` and `tbill_13w`, which became buildable as the data layer gained the capability
to price them, and `days_to_month_end`, `quarter_end` and `tax_date`, the calendar columns
derived from the scored date. The decision is to take **all nine** rather than a subset: a
column the build can produce and the registry can price is carried in the panel, and
whether a model reads it is answered per run by that run's declared feature list.

The persistence run declares `spread_bps` as its only feature and derives from `nyfed_sofr`
and `fred_macro_latest_vintage` alone, so none of the nine can enter the model. The re-score
demonstrates that rather than assuming it: `folds`, `derived`, `declaration`, `crps_bps`,
`forecast_count` and the entire coverage series come back bit-identical, and the publish
refuses if any of them moves.

Two things do move, and both follow from the panel's identity rather than from the model.
The panel's digest changes, and `_report_seed` derives the bootstrap seed from that digest
together with the feature set, the purge gap and the decision time -- deliberately, so that
two runs differing in any of those respects do not silently share a resample stream. A
rebuilt panel therefore *must* draw a different bootstrap sample, and the stationary-bootstrap
bounds on the MAE and on interval coverage shift by about one observation in two thousand.
The published point estimates do not move at all. The publish step recomputes the seed from
the record's own fields and refuses unless it is the one the specification derives, so the
shift is accounted for rather than accepted. Second, the record's build-manifest binding
strengthens from `extent` to `digest`, because the rebuilt manifest carries a digest of the
panel it describes where the previous embedded manifest carried none.

The rebuild is required because the manifest and the record are coupled by digest:
`scripts/track_funding_inputs.py` is the only way `metadata/funding_panel_manifest.json` is
made, and it refuses unless the local panel hashes to the digest the published record scored.
A manifest edited to anticipate a rebuild would publish a digest no build produced. The
thirty-one published records that embed a build manifest bind it by extent -- row count and
first and last date -- and the rebuild leaves all three unchanged, so none needs re-scoring.

What "buildable" meant **at this rebuild** was narrower than it reads, and the manifest was the
evidence. Six of the nine were declared and **empty**: `treasury_settlement_bills`,
`treasury_settlement_coupons`, `treasury_settlement_soma`, `dealer_treasury_position`, `tbill_4w`
and `tbill_13w` each carried a hole on every row of that build, as `treasury_settlement` already
did, because the snapshots their sources would be priced from were not under `data/raw/`. The build
had stopped refusing them; it did not follow that data had arrived. Only the three calendar columns,
computed from the scored date, carried a value on every row.

**That is no longer the panel's state, and what changed is two later decisions rather than a
correction to this one.** Rule 10 carries a weekly column's nearest earlier print forward under a
bounded gap, and re-fetching the auction source from before the panel's own start closed the
settlement columns' last holes, which were a fetch-range artefact rather than missing data. All
seven now carry a value on every row of the published build, and the paragraph above is kept as the
record of what was true when the rebuild was decided.

A model that declares a genuinely unobserved regressor as a feature is still refused at its first
fold rather than handed zeros, which is contract test 5 working: an unobserved regressor is never
coerced.

The bootstrap seed a re-scored record carries can be recomputed from the record itself with
`baseline.backtest_record_seed`, and the decision time it digests is the `HH:MM:SS` form rather than
the `HH:MM` the declaration states.

## A Fed repo operation under $0.1 bn accepted is no take-up, in every era

**Superseded on 15 October 2026 by the section "A Fed repo operation is no take-up only if it is a test trade" below (ruling on #802).** The text that follows is kept as the record of #743.

Decided by Eleonora on 14 October 2026 (ruling on #743; data meaning is hers, #735). In every era,
a Fed repo operation with less than $0.1 bn accepted counts as no take-up. One amount, no date:
`ingest.REPO_TAKE_UP_FLOOR` (USD 100 million), applied by `ingest._effective_accepted`.

**Why.** #659 dropped the six test operations of $64-66 mn before 2019-09-17 and, from then on,
only operations whose `note` names a small value exercise. The facility-era test trades of $1-7 mn
(on hundreds of operation dates in 2021-2025 in the tracked snapshots, typically $1 mn per collateral type) carry
no such note and were counted as take-up. So `fed_repo_days_since_positive` marked the pre-facility
era (at its cap of 250 on every 2018 row) and never reached the cap after 2020. A rule that differs by
era builds a regime dummy (#672); one floor covers both the tests and the trades.

**What the rule does.**

* An operation below the floor contributes zero to `fed_repo_accepted`,
  is not counted by `fed_repo_ops`, and its detail rates do not enter `fed_repo_rate_iorb_bps`.
  A day is zero take-up if all its operations are below the floor, and an operation at exactly
  $0.1 bn counts.
* The operation still happened, so its date keeps a row at zero (the facility operated that day) rather
  than becoming missing. `fed_repo_submitted` is the amount submitted and is not changed.
* Unchanged: `REPO_FACILITY_START` still decides which dates before the facility are structural zeros and
  which are missing, and the small-value-exercise note still drops an operation. Both are about whether
  the facility operated, not about how much was taken.
* `srf_total_accepted` (`nyfed_srf`, the Standing Repo Facility total that the results page reads) is **not**
  changed: it still counts the small trades. Applying the floor to it moves a published figure, so it waits for
  her decision (a "Publish?" issue).
* The columns stay off `FEATURE_FIELDS` and out of every published declaration; no published figure moves.
  The material-use dates ($1 bn or more) are the same set.

**Consequence for earlier evidence.** Any record that read the Fed repo take-up columns before this
change read the $1-7 mn trades as take-up. #727's gains attributed to #662 are re-run in
`docs/pivot/fed-repo-floor-743-result.md`; no 2018 warning gain is claimed before that re-run.

## A Fed repo operation is no take-up only if it is a test trade

*Draft for Eleonora's review (PR for #802); in force once she has merged it.* Decided by Eleonora on 15 October 2026 (ruling on #802, option (b); data meaning is hers, #735). It narrows the
$0.1 bn floor above, which also zeroed about 40 days of $8-97 mn take-up that carry no test note, several in the days before onsets.

**The rule.** A Fed repo operation counts as no take-up only if it is a test trade:

* an operation whose `note` names a small value exercise is dropped, as before (`ingest._is_small_value_exercise`); and
* otherwise an operation is a test trade if it accepted more than zero and at most USD 7 million (`ingest.TEST_TRADE_MAX`) and a whole number of millions
  (`ingest._is_test_trade`, applied by `ingest._effective_accepted`). Every other operation counts in full.

It is judged per operation, in every era, with no date: a rule that differs by era builds a regime dummy (#672). A day with a $3 mn trade and a $9 mn trade has $9 mn of take-up.

**What does not change.** The operation still happened, so its date keeps a row at zero (the facility operated that day). `REPO_FACILITY_START` still decides which dates before the facility are
structural zeros and which are missing. `fed_repo_submitted` is not changed. `srf_total_accepted` (`nyfed_srf`, read by the results page) is **not** changed here: applying the rule to it moves a
published figure, and #787 does that. The columns stay off `FEATURE_FIELDS` and out of every published declaration; no published figure moves.

**Limit.** The Desk's data mark no operation under $44 mn as a test (the small value exercises it labels are $44-116 mn), so the $7 mn ceiling is a size rule: it cannot tell a test from a real $1-7 mn
borrow. If the Desk publishes a test note, the note should be read first.

**Consequence for earlier evidence.** #743's figures read the $0.1 bn floor. The Fed repo columns are re-read under this rule, with an arm that removes the whole group, in
`docs/pivot/test-trade-802-result.md`: the ordinary-day AUROC gain of `fed_repo_days_since_positive` is 0.60 [0.42, 0.76] at lead 1 (interval contains 0.5), and the 2018 warnings survive with every `fed_repo_*` column zeroed.

## A Fed repo operation marked as a Desk test is no take-up

*Draft for Eleonora's review (PR for #933); in force once she has merged it.* Decided by Eleonora on 19 October 2026 (ruling on #916; data meaning is hers, #735).

**The rule.** A `Repo` operation is a Desk test (a small-value exercise) if any of these holds, and it is then dropped before the test-trade rule above is read:

* its `note` names a small value exercise (as before);
* its `operationId` ends in " 99";
* its `operationLimit` is present and at most USD 250 million (`ingest.DESK_TEST_LIMIT_MAX`); a normal operation's limit is $500 bn, and the labelled exercises are $75-250 mn.

It is judged per operation, in every era, by `ingest._is_small_value_exercise`. A `Repo` operation whose `operationLimit` is present and not a number raises `ValueError`. `fed_repo_accepted`, `srf_total_accepted` and the other columns that read the helper follow.

**What it changes in the tracked snapshots.** Six repo operations carried the marks and not the note: 2020-06-17, 2020-10-07, 2021-05-26, 2023-03-08 (term, limit $75 mn), 2023-05-23 and 2024-09-24 (term, limit $75 mn). They are no longer take-up; their dates keep any other operations' take-up and otherwise a row at zero. `docs/pivot/desk-test-marks-933-result.md` has the figures.

**What does not change.** A reverse repo is read by its note alone: an id ending " 99" is not a test mark there (the ON RRP operation of 2023-07-17 took $1.7 trillion). The recurring $10 mn / $0 / $10 mn split pattern (and the even three-way splits) is **not ruled** and is counted as take-up exactly as before; it stays with Eleonora (#916). The columns stay off `FEATURE_FIELDS` and out of every published declaration.

**Limit.** The marks are structural, not the Desk's own label. In the tracked snapshots every operation they drop has a note or is one of the six; a later operation placed with a limit of $250 mn or less and no note would be read as a test whatever it was.

**Consequence for earlier evidence.** `docs/pivot/test-trade-802-result.md` (which lists 2024-09-24 at $57 mn as take-up) and #908's `srf_total_accepted` counts stand as published records; the figures are published anew in `docs/pivot/desk-test-marks-933-result.md`.

## DRAFT for Eleonora: the recurring ~$0.1 bn afternoon repo operation

*Draft for Eleonora's review (PR for #872, updated by the PR for #938 to state option (C)); not in force until she has merged it. Her merge is her own GitHub action: a relayed ruling does not authorise it.* Ruling of 17 October 2026 on #860 (relayed): the recurring ~$0.1 bn calm-day operation is a test trade and is not take-up. Data meaning is hers (#735).

**What the evidence shows** (`docs/pivot/repo-test-trades-872-result.md`). The tracked snapshots hold 40 Repo operations with $0.09 to $0.13 bn accepted. Five are Desk-announced morning small value exercises, each already dropped by its `note`. The other 35 (31 released at 13:30, 2 at 13:29, 2 at 08:15) carry no note and no public statement; 27 of 35 are one line at one rate. No field in the snapshot separates them from a real borrow of the same size except the amount and the time of day.

**The rule cannot be stated without a cutoff or a list.** A rule that classifies the 35 as no take-up must name one of these, and each has a cost:

* **(A) A size band** (for example, accepted of USD 90 to 130 million with no note): a new size cutoff. It would also zero real take-up inside the band that has no test note, which is what the #802 ruling kept when it replaced the $0.1 bn floor with the whole-million $7 mn rule.
* **(B) An operation list** (the 35 operations by id, as the evidence applies the ruling): known only after the fact, so it cannot be point in time. A list drawn at a later date has no availability instant for the operations it names. It is usable for a development column and not for a forecast input.
* **(C) A pattern** (one afternoon operation of a single line and rate within the band, at the 13:30 release): a regime-style rule that differs by operation shape and may move if the Desk changes its schedule.
* **(D) Keep the rule in force** (#826) and treat the ruling as an evidence column only.

**Question for Eleonora (marked):** which of (A) to (D), and the exact definition (bounds, fields and any date) if (A) or (C). If she chooses (A) or (C), a directive puts it in `ingest._effective_accepted` test first, with an availability guard and one recorded mutation if the rule reads a public time.

**Ruled: option (C), as worded on 20 October 2026 (PR for #938).** A test trade is an operation whose main line is in the ~$100 mn band and released at 13:29 to 13:30, ignoring accompanying lines under $10 mn. The two 08:15 operations are regular operations and are not test trades. `ingest._is_afternoon_test_trade` reads it per operation, from the operation's own results release only: an overnight `Repo` operation with no `note`, `releaseTime` 13:29 or 13:30, a main line (the largest `amtAccepted`) of USD 90 to 130 million inclusive (`ingest.PATTERN_BAND_MIN`, `PATTERN_BAND_MAX`), every other line that accepted anything under USD 10 million (`PATTERN_SIDE_LINE_MAX`), and a main line with one rate (when it states both `percentLowRate` and `percentHighRate` they are equal). It is read after the Desk-test marks and beside the whole-million rule of #802; `ingest._effective_taken` applies it, so `fed_repo_accepted`, `repo_ops_accepting`, `repo_rate` and `srf_total_accepted` follow. The operation still happened, so its date keeps a row at zero; `repo_submitted` is unchanged. A `Repo` operation whose `releaseTime` is present and not HH:MM, or a detail line with no numeric `amtAccepted`, raises `ValueError`. The figures are in `docs/pivot/afternoon-test-trade-938-result.md`.

**Still open for her (marked questions in the PR for #938):** how "single rate" reads on Full Allotment operations that state no rate (default: they count as one rate); the ruling comment's count of 31 against the 32 the wording catches; 13:29 releases (caught); a $10 mn accompanying line (not caught, not under $10 mn). The default applies if she has not answered by the next 5 pm batch; it changes nothing the project claims.

**What the draft did not do at #872.** `ingest.TEST_TRADE_MAX` and `_is_test_trade` stay as #802 left them; the `fed_repo_*` columns of the published panel are unchanged (the published panel digest is unchanged by #938 too); the columns stay off `FEATURE_FIELDS` and out of every published declaration. The ruling's effect is shown as a fourth column in the evidence, computed by operation id in `scripts/repo_test_trades_872.py` (`_rule_ruling`): longest gap of `fed_repo_days_since_positive` in 2024, 2025 and 2026 is 134, 62 and 27 days under it, against 50, 32 and 17 under the rule in force.

## What `srf_total_accepted` counts today (#936)

This section restates rules already in force above; it decides nothing new. The `limitation` text of `nyfed_srf` in `metadata/sources.json` was written before them and is left byte-identical, because the frozen final-test declarations hash that file (Eleonora's ruling of 26 October 2026 on the pull request for #936). Where the registry text and this section differ, this section describes what `ingest._nyfed_srf_rows` computes.

`srf_total_accepted` is `totalAmtAccepted` summed over the overnight `Repo` operations of an `operationDate`, from 2021-07-29, in USD billions. Before it is summed, `ingest._effective_taken` reads each operation:

* A Desk test is not take-up and is dropped: an operation whose `note` names a small value exercise, whose `operationId` ends in " 99", or whose `operationLimit` is at most $250 million (a normal operation's limit is $500 billion). The two term repos since the inception were such tests (#933).
* A test trade adds nothing: an operation that accepted at most $7 million and a whole number of millions counts as zero (#802).
* The afternoon pattern adds nothing: a note-free operation released at 13:29 to 13:30 whose main line is $90 to 130 million, with every other line under $10 million (#938, ruled option (C)).

An operation that happened keeps its date as a row, at zero. Recount from the tracked snapshots (`tests/fixtures/snapshots/srf_inputs/nyfed_srf`, read by `ingest._nyfed_srf_rows`): from 2021-07-29 to 2025-12-31 the take-up is above zero on 71 operation days and at least 0.1 billion on 35, out of 1,104 operation days. The registry text still says 397 and 58. The test `NyFedSrfAdapterTests.test_the_data_quality_page_states_the_srf_rule_and_the_recounted_days` recounts these from the snapshots.
