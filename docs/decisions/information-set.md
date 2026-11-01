# Decision: a forecast uses exactly the information public at its decision instant

**Status: decided and implemented** (#27; the guards are `repo_model.asof`). Every record scored
under the previous rule was re-scored or archived.

> **Proposed in #267, for Eleonora to review:** the corrected wording of rule 1 below (the H.4.1
> read lag). A decision is in force only once she merges it.
>
> **In force (#541, #1299):** the wording of rule 1's H.4.1 sentence and of rule 2's Treasury-settlement
> bullet records her ruling of 10 October 2026 (relayed on #541): a settlement is dated from the auction
> announcement, not the auction results, and the H.4.1 is read per release, at the release's own publication
> instant. It is in force as wording from her ruling of 29 October 2026 on #1299 (ledger item 73 on #1116,
> option 1 of decision 1 in the 28 October message). The H.4.1 reading is still off in the published registry:
> `metadata/sources.json` is frozen by the final-test pre-registration (bytes), so turning it on is a later
> pull request, with the re-pin that needs, under her own `GO`. The settlement reading was adopted in
> `metadata/sources.json` by #1311 (her ruling of 29 October 2026 on #1310): the `treasury_auctions` note and
> evidence date a settlement from its auction's announcement and take `metadata/settlement_announcement_dating.json`'s
> rule and evidence as their own. Its machine-read availability is still the one instant that block can state (15:00 on
> the panel day before a settlement, days = 1), so every published record and the live record read a settlement at
> h = 1 only, where the announcement dating gives the same column. Only the development arms of the H5 candidate
> (`repo_model.settlement_dating`, `repo_model.s3c_announced`) read the announcement dating at h = 2 to 5.
> **Proposed in #1327, for Eleonora to review:** this paragraph and the "no clock time" sentence in rule 2 below
> are corrected to #1301's check (`metadata/announcement_release_times_1301.json`). It is **not in force** until she
> merges it, with her own `GO #1327`.
>
> **Proposed in #586, for Eleonora to review:** the amendment at the end of this record, which records her
> ruling of 11 October 2026 on #571 (relayed by the orchestrating session): the reserve-scarcity state reads each
> of its legs at its own latest public row. It was drafted by the pull request that closes #586 and is **not in
> force** until she merges it.

> **Proposed in #1312, for Eleonora to review:** the amendment at the end of this record, "The decision instant is 18:00 New
> York time", which records her ruling of 29 October 2026 (chat, relayed on #1312; ledger item 77). It was drafted by the
> pull request that closes #1312 and is **not in force** until she has merged it, with her own `GO #1312`.

## The rule

A forecast for scored day `T` is made at the declared decision time on the last panel day before
`T`, called the decision instant.

1. **Each input is read per field, at its latest value whose declared first-observable instant is at
   or before the decision instant.** The declarations are the registry's own `release_lag` blocks,
   read through `baseline._declared_availability`. Under them, the daily NY Fed rates and bill rates
   are read at the row two panel days before `T`. The H.4.1 weekly series are read per release: a
   Wednesday level is first observable at the print of its own release, the Thursday after the Wednesday
   at 16:30 New York time, or the date the Board moved the release to when a holiday moves it (the
   Board's release pages are the evidence, recorded with the declaration). Each Wednesday level is carried
   on the rows after it (`weekly-carry.md`), and a forecast reads it from the first decision at or after
   the print and never before. A newer print that was public at the decision is read, not left unread.
   A record's `hours_observable` counts from the observation row's declared instant and says so.
2. **Values that refer to `T` itself are admissible only as declared scheduled inputs**, meaning a
   value announced before the decision instant. That covers:
   - the calendar columns, which are always known;
   - FOMC schedules, under `docs/decisions/fomc-point-in-time.md`;
   - Treasury settlements, under a `treasury_auctions` availability declaration dated from the
     auction announcement: each settlement's first-observable instant is the announcement time of its
     auction. Treasury's own announcement files state a release time for most announcements: 3,665 of 3,828 state
     one (almost all 11:00 or earlier; one, for a note settling eleven business days later, states 16:15, after the
     16:00 decision, and a few state a time between 12:00 and 16:00), and 163 say "for immediate release", 153 of
     them cash management bills (`metadata/announcement_release_times_1301.json`, #1301). The 12:00 instant is a
     declared setting checked against those files, not a published clock time, and the declaration records what it
     rests on. On the 2020 development days the net arm's loss is not separable from the immediate-release cash
     management bills (they carry 67.5% of it; `docs/research/s3c-ann-net-diagnosis-1319-result.md`, #1320, Table 4d):
     development evidence, not a verdict. The risk-date calendar then marks a settlement as known at the
     decision instant from the day it is announced.
   Each scheduled input passes the same availability check as any other input.
3. **A training target is admissible only if it was observable by the fold's decision instant.**
   This replaces the purge as the rule for training labels.
4. **The purge does not choose the feature row**, and the fold grid does not depend on which features a
   declaration names. Every declaration is scored on the same grid, so any two are paired by construction.
5. **Both directions are guarded.** Nothing read may be newer than the decision instant (leakage).
   No admissible value may be newer than the one read (staleness). A record reports each field's
   staleness at the decision instant.

## What it supersedes

`docs/process/AGENT_CONTRACT.md`'s "The purge stays a scalar", wherever the purge chooses what a forecast reads. The contract's own
as-of rule is unchanged, and this decision is what implements it. The evidence and the alternatives considered are in
[`docs/pivot/lag-assessment.md`](../pivot/lag-assessment.md). That assessment's §4 verdicts were not re-measured
when the feature set was fixed; re-scoring them belongs with next-version research.

## Decided with it

- **Refit cadence:** records are refitted every 21 scored days, and the cadence is declared in each record.
- **Old records:** records scored under the previous rule move to `docs/runs/archive/pre-asof/`,
  with a README naming the rule they were scored under. The move happens in the re-scoring pull
  request, because the generated pages render from `docs/runs/`.

## Method notes

- **Calibration masking is a calibration bias, not leakage.** A calibrated fit (conformal or
  cross-conformal) scores held-out rows of its own training frame as forecasts, each read as-of its own
  decision instant. The excluding models it trains for them, though, train on the frame as masked at
  the fold's decision instant, not at each held-out row's. A declared column that was public by the
  fold's decision but not yet by a held-out row's can therefore reach an excluding model's training
  rows. No value the forecast itself reads is affected, and nothing public after the fold's decision
  instant is used anywhere. The effect is a possible optimism in the calibration scores, and it is
  limited to declared columns slower than the target (the H.4.1 weeklies, for example). It is
  bounded to those rows and left as is.

## Amendment: back-filled repo-rate history is training history only (#374, #430)

**The change from #1230 is in force from the merge of PR #1231 on 26 October 2026 (her GO #1230).** It amends items 1
and 4 below: it admits IOER/IORB on back-filled rows as training history only (her ruling of 26 October 2026), and
corrects item 1's line on the SOFR volume to her ruling of 19 October 2026 on #742. The rest of this amendment is in
force as it stands.

The snapshot and the guard are merged. **Posting instant established: 2018-05-17** (the start of that day, New York
time) for TGCR, BGCR and SOFR, by her ruling of 13 October 2026 on PR #661 (#633); the source is
`metadata/backfill_posting.json`. The amendment is in force from the merge of the pull request that closes #734.
Eleonora ruled on 8 October 2026 (#374) that the New York Fed's
back-filled history of SOFR, TGCR and BGCR may be used as training history. The Bank's reference-rate
API begins on 2018-04-02. For the months before it, the Bank published a workbook of indicative values
of the same three rates and their volumes, computed after the fact on the same method, from 2014-08-22
to 2018-03-29. It carries no percentiles. Its source, checksum and what is known of its publication date
are in `docs/pivot/backfilled-history-result.md`.

1. **A back-filled value is training history.** It may sit in a fold's training frame, for a day before
   2018-04-03, the first day the API serves. Rule 3 above is unchanged: a training target is admissible
   only if it was observable by the fold's decision instant. The workbook's own properties date it May
   2018, before the first scored decision instant. The Bank's original posting date was established on
   13 October 2026: 2018-05-17, by her ruling on PR #661, with its evidence in #781 and
   `docs/pivot/posting-dates-due-diligence.md`. The series admitted, each from that date, are listed in
   `metadata/backfill_posting.json` (`admitted`) and here:
   <!-- backfill-admitted: bgcr@2018-05-17, iorb@2018-05-17, sofr@2018-05-17, tgcr@2018-05-17 -->
   That is TGCR, BGCR and SOFR from 2018-05-17, by her ruling of 14 October 2026 on #742, and IOER/IORB from
   the same date, by her ruling of 26 October 2026 (ledger item 56 on #1223, option 1; directive #1230), and no
   other series. IOER/IORB on a back-filled row is admitted as training history only, on the same terms as the
   back-filled SOFR: it is never an as-of input at a scored decision instant (item 2), and a model trained on it
   stays a scratch measurement until a later decision (item 3). It is a series like the others:
   `repo_model.backfill.require_series_admitted` checks a fit that reads it, and a fit that reads it outside
   training history raises `LookAheadError`. The workbook's volumes are not admitted by this record, the SOFR
   volume among them (her ruling of 19 October 2026 on #742).
2. **It is never an as-of input at a scored decision instant.** No scored day is a back-filled day, and
   no scored forecast is conditioned on a back-filled row (its feature date is a published day).
   `repo_model.backfill.require_training_only` raises `LookAheadError` for a backtest in which either
   is not so.
3. **Nothing published moves.** No declaration in `docs/runs/` reads the back-fill, and the published
   panel (digest in `metadata/funding_panel_manifest.json`) does not carry it. A model that trains on it
   is a scratch measurement until a later decision puts it in a declaration.
4. **Every other input is blank on a back-filled row.** The bill rates, Treasury auctions, the Desk's ON RRP
   results, the H.8 first prints, FRED's reserves, TGA and IOER, the FR 2004 extract and the derived
   scarcity state are not in the admitted list of item 1, so each is blank on a back-filled row, and a fit
   that reads one of them on those rows raises `LookAheadError`
   (`repo_model.backfill.require_series_admitted`). Only the calendar columns, which are functions of the
   date, and the admitted series of item 1 (IORB among them) are filled there; the calendar columns use the workbook's own
   publication days as the business-day schedule, because the market holiday table begins on 2018-01-01.

## Amendment: the scarcity state reads each leg at its own latest public row (#571, #586)

**Proposed, for Eleonora to review. Not in force until she has merged it.** Eleonora ruled on 11 October 2026
(#571; the ruling was relayed by the orchestrating session) that the reserve-scarcity state
(`repo_model.scarcity`, #115) may be assembled from more than one row.

1. **Each leg is read at its own latest public row.** The state's three legs are the reserves (the H.4.1's
   WRESBAL), the H.8's total assets and the day's ON RRP. As of a forecast's decision instant, each is read
   at the latest row whose own declared first-observable instant is at or before it (rule 1 above, per
   field), and the state is formed from the three reads. The ratio's legs may then belong to different
   weeks, and the ON RRP leg is no older than the Desk's declared lag; the H.8's lag no longer sets the row
   the other two are read at.
2. **Each read passes the usual guards.** Every leg passes the availability check (`LookAheadError` for a read
   newer than the decision instant) and the staleness check (`StaleReadError` for a read older than the
   latest admissible row), through `InformationRule` (rule 5 above), and `scarcity._require_public_legs`
   restates the first for the three legs. A leg that is a hole at its row leaves the state a hole.
3. **The scope is this indicator only.** This replaces the rule that an indicator is "never assembled from two
   rows" for the scarcity state, and for no other feature. No other input, threshold, cut-point, onset
   definition or availability time changes.
4. **Where it is in force.** `scarcity.own_leg_states` is the state the judge reads (`pressure_judge.py`,
   `_scarcity_states`), and `scarcity.own_leg_composition` reads it as a composed feature in a measurement run,
   which is how a model that takes the state as an input is fed it. `asof.py` and `contract.py` are not edited:
   they are in the final test's pipeline checksum, and the published declaration, the published panel and the
   pre-registered model are unchanged. The same-row read (`with_reserve_scarcity_state`, the column) is kept
   for the published map's off declaration and for the before-and-after count. Whether the own-leg read
   replaces it in `contract.py`, which would move that checksum, is not decided here.

## Amendment: the decision instant is 18:00 New York time (#1312)

**Drafted by the pull request that closes #1312, for Eleonora to review.** In force only once she has merged it, and the pull
request is binding only with her own `GO #1312` on that issue (a comment by her, not through an app), cited in
`metadata/owner_attestations.json`. It records her ruling of 29 October 2026 (chat, relayed; ledger item 77): **move the
decision instant from 16:00 to 18:00 America/New_York.** This is step 1 of 3. Step 2 (the new live record and its pin) and step 3
(the re-runs of the results that matter) are separate directives; this pull request does neither.

1. **The instant.** A forecast for scored day `T` is made at 18:00 New York time on the last panel day before `T`, from the merge
   of this pull request. The clock is one declared constant, `repo_model.decision_instant.DECISION_TIME`, and every default,
   constant and declaration in `src/` that means "the decision instant" takes it; `tests/test_decision_instant_1312.py` refuses a
   module that types the clock again. `metadata/funding_panel_manifest.json` states it as the build setting (`18:00:00`).
   Rule 1's per-field reads, rule 2's scheduled inputs and rule 5's two guards are unchanged; they compare each input's declared
   first-observable instant with this one.
2. **Why.** DTCC posts the GCF Repo Index at about 16:00 to 16:05 (her Mac's capture, 27 to 29 October 2026; #1280), after the old
   instant. Between 16:00 and 18:00 the H.15 (16:15), the weekly FR 2004 (about 16:15), the H.8 (16:15) and, on Thursdays, the
   H.4.1 (about 16:30) also arrive. A forecast at 18:00 is still made before any trade of the next business day.
3. **Records made at 16:00 stand as records of that instant.** A published record, a dated study declaration, a captured file or a
   result page that states `16:00` is labelled by it, not edited, and not provisional on this account, unless she rules otherwise
   (the provisional register is for the calendar rule, and is unchanged). Nothing in `docs/runs/` is edited; the published
   panel record `docs/runs/funding_panel.manifest.json` keeps its `16:00:00`. A reader that must still accept such a record
   reads it against the instant it declares (`repo_model.gcf_index`: a capture file declaring 16:00 is judged at 16:00).
4. **What it moves, by source** (`scripts/decision_instant_1312.py audit`, `docs/research/decision-instant-1312/audit.json`; the
   registry's own declared availability and the published panel's dates, no outcome). A declared first-observable instant
   after 16:00 and at or before 18:00 was invisible to the old decision and is visible to the new one. The declarations
   themselves are unchanged (they state when a source publishes); what moves is the row the as-of rule reads:

   | Source and field | Declared instant | Effect at 18:00, against 16:00 |
   |---|---|---|
   | `fred_macro_latest_vintage` IORB, IOER | 16:15, same day | the decision day's rate is read, not the day before's: one row later on every scored day. The target `spread_bps` is still read at the anchor row (SOFR is not public until the next business day), so the spread does not change. |
   | `treasury_bill_rates` (all tenors; `tbill_4w`, `tbill_13w` in the panel) | 16:30, same day | the decision day's bill rate is read: one row later on every scored day |
   | `frb_ddp` EFFR, IOER, IORB (no panel column reads it) | 16:15 | one row later on every scored day |
   | `fred_macro_latest_vintage` WRESBAL, WTREGEN, WLRRAOL (the H.4.1 weeklies; `reserve_balances`, `tga`) | 16:30, five calendar days after the Wednesday | one row later on the Monday, Tuesday and Wednesday decisions |
   | `fred_macro_latest_vintage` DFF | 16:15, five days | the same days |
   | `frb_h8` total assets | 16:15, twelve days | one row later on the Monday, Tuesday and Wednesday decisions |
   | `nyfed_fr2004` (`dealer_treasury_position`, and the series of #1296) | 16:30, six business days | one row later on every scored day |
   | `fed_iorb_announcements` (announced IORB changes) | **declared at the decision instant itself**, 16:00 until now | the declaration is re-declared at 18:00 (`scheduled_availability.available_time`), because the features read the notes announced at or before the decision instant. The table's one note announced after 16:00 (17:00 on Sunday 15 March 2020) is not announced on a panel day. |
   | DTCC GCF Repo Index (forward capture, not in the registry) | about 16:00 to 16:05 | a fetch from 16:00 to 18:00 is a capture, not `fetched_after_decision` (`repo_model.gcf_index`) |

   Not moved, because the declared instant is at or before 16:00 or on a later day: SOFR, TGCR, BGCR (15:00 on the next business
   day), the NY Fed EFFR (15:00), ON RRP and SRF (16:00 on the next business day), the OFR repo series (16:00, two business days)
   and the Treasury settlement schedule. The declared lags of the weeklies and of DFF were derived at 16:00 by purge arithmetic;
   they are kept as declared, and the per-release H.4.1 reading of rule 1 stays off in the registry (see the marked questions in
   the pull request).
5. **Nothing the target day's spread is computed from becomes visible.** The spread of day `T` is SOFR(`T`) less IORB(`T`).
   SOFR(`T`) is public at 15:00 on the next business day after `T` (first print about 08:00), IORB(`T`) at 16:15 on `T`
   itself: both after the decision on the day before `T`, at 18:00 or at any instant of that day. The audit checks it over every
   scored day of the published panel and `tests/test_decision_instant_1312.py` pins it, with a leakage test that fails when a
   value announced at 17:00 on the day before is declared for the target.
6. **The published panel.** Rebuilt at 18:00 from the tracked fixtures, the panel's bytes and digest do not change
   (`4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`); the build's `decision_time` is the one field of its
   manifest that does. At 18:00 the build prices `iorb`, `tbill_4w` and `tbill_13w` at a zero purge (every source is public by the
   decision on its own day), which the pricing function's "nonzero purge" refusal had made impossible; the panel build now treats
   exactly that refusal as priced, and every other caller of `registry.max_release_lag_days` still gets it.
7. **What does not change.** The lockbox and its tiers; the scoring protocol; the live record and its pin (step 2); every
   published record; the calendar-first rule and the provisional register; the declared lags.

