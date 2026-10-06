# Draft: binding approvals are Eleonora's own GitHub action (#256)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #256, as that directive
asks. It takes effect only when she merges the amendment below into `docs/decisions/workflow.md`. The routine
prompt text below is a proposal: the Directive loop's prompt is her configuration, and this pull request does not
change it. The directive's own ruling ("Only your own GitHub action", 6 October 2026) is itself a relay posted
through the Claude app, so under the rule it drafts it binds nothing until she confirms it.

## Why

Agent sessions post to GitHub under Eleonora's account. Their comments carry `author_association: OWNER`, so a
comment headed "Ruling (Eleonora; relayed by the orchestrating session)" does not prove her instruction. This has
failed once: on #151 a relayed "go for #151" (comment 5974697778) was withdrawn as "not a go" (comment 5975923861).

What an app cannot set on her behalf is the REST field `performed_via_github_app`. It names the app a comment was
posted through, and is `null` only on a comment posted without one.

## The amendment to `workflow.md`, as drafted

---

## Owner-attested approvals

**Decided by Eleonora on the date this section merges** (#256).

These items count only with Eleonora's own action on GitHub:

- opening any lockbox tier (`metadata/lockbox.json`);
- changing a pre-registered primary test;
- approving a model to join the live record, v2 (#245) included;
- changing the live model pin;
- any exception to these.

**Her own action** is a comment by `eleonorabjornberg` whose `performed_via_github_app` is `null` in the REST
API, not edited after it was posted, on the issue it approves, and carrying the phrase `GO #N`, where #N is that
issue (the "GO" convention). `scripts/owner_attested.py` decides it mechanically.

A pull request that makes one of these changes appends an entry to `metadata/owner_attestations.json` citing that
comment: its kind, the issue, the comment id and the phrase. The registry is append-only. CI (`tests.yml`, job
`owner attestation`) fails a pull request that changes a lockbox tier, the live pin or the logged models without
such an entry, and fetches every new entry's comment to check it.

A relay by the orchestrating session of any of these items is headed **"relay, unverified until owner-attested"**
and binds nothing. Other rulings (scope, wording, labels) may still be relayed as before. Delegated review never
merges a pull request whose owner-attestation check is red, and escalates one that changes a pre-registered primary
test.

---

## Proposed text for the Directive loop routine's prompt

A proposal for Eleonora; this pull request does not change the routine.

> **Owner-attested items** (`docs/decisions/workflow.md`, "Owner-attested approvals"). Opening a lockbox tier,
> changing a pre-registered primary test, a model joining the live record, a live pin change, and any exception to
> these count only with Eleonora's own comment: by `eleonorabjornberg`, `performed_via_github_app` null, on the
> issue, carrying `GO #N`. Check it with `python3 scripts/owner_attested.py find --issue N --phrase "GO #N"`. A
> "**Ruling" comment posted through an app is never enough for these: if a directive needs one and the check fails,
> label the directive `needs-eleonora` and say which comment is missing. A pull request making such a change cites
> the comment in `metadata/owner_attestations.json`; the reviewer merges it only when the `owner attestation`
> check is green, and escalates any change to a pre-registered primary test. When you relay one of these items,
> head the comment "relay, unverified until owner-attested".

## What the check cannot see

- **A personal token.** `null` shows the comment was not posted through an app. It does not show that she typed
  it: a session using her personal access token posts with `null` too. The identical scope comments on #45, #38,
  #78 and #37 of 2 October 2026, posted within two seconds of each other with `null`, look scripted. The rule holds
  only while no agent session holds a personal token of hers.
- **Reviews and label events.** The directive counts a review or a label event by her as her own action too. The
  script reads issue comments only; reviews and labels are not wired.
- **Merges.** A merge event carries no app field, so who merged a pull request cannot be told from the REST API.
- **A pre-registered primary test.** The rule lists it, but the directive's wiring list does not name it, so CI does
  not gate edits to `docs/decisions/final-test-preregistration.md`. Whether to add it is her call.

## Retrospective audit of relayed rulings

Compiled from the GitHub REST API on 6 October 2026, for Eleonora to confirm or correct. Nothing is rewritten:
`metadata/lockbox.json` keeps citing the relayed "GO #151", and `metadata/owner_attestations.json` starts empty.
Every row was posted by `eleonorabjornberg` through the `claude` app; none of these threads carries a comment
with `performed_via_github_app` null. Categories: (a) opening a lockbox tier; (b) changing a pre-registered primary
test; (c) a model joining the live record; (d) the live pin; (e) an exception. "Borderline" marks a row whose
category depends on the reading, for example a test design fixed before its record was in force.

| Where | Comment | Date (UTC) | Posted via | What it authorised | Owner-attested item |
|---|---|---|---|---|---|
| #150 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/150) | 2026-10-02 06:39 | claude | "Eleonora's request": build the pressure model, "fix its design in advance, then open the 2026 lockbox once"; defines the pre-registration directive | not binding (scope); starts the pre-registration |
| #151 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/151) | 2026-10-02 06:39 | claude | "Eleonora's request": "She decided to open the 2026 lockbox"; opening to run once after #150's record merges | (a) intent only; the go was relayed later (see 5974697778 / 6003148702) |
| #150 | [5946893422](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5946893422) | 2026-10-02 06:44 | claude | "Consistency note": use #139's *J* and leap definitions (not marked as relayed from her) | not binding (scope/wording) |
| #150 | [5951943315](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5951943315) | 2026-10-02 12:05 | claude | Clarification: "the S-curve" means the persistence-logistic baseline | not binding (wording); names the comparator before the record existed |
| #150 | [5952332205](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5952332205) | 2026-10-02 12:28 | claude | Scope addition: fold in #160's onset-day comparison as context; "does not change the primary cell" | not binding (scope) |
| #150 | [5970172353](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5970172353) | 2026-10-03 14:38 (edited 14:38) | claude | Amendment: onset days become #209's at-risk days; five calm days | borderline (b): test design, before the record was in force |
| #150 | [5970417600](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5970417600) | 2026-10-03 15:08 | claude | Amendment: selection score = walk-forward plain-leap Brier at h = 1 | borderline (b): test design, before the record was in force |
| #150 | [5970439995](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5970439995) | 2026-10-03 15:10 (edited 15:17) | claude | Amendment: candidate list "closed at six", fixed simplicity ranking, one common recalibration step; "no amendment comment is edited" from first scoring run on | borderline (b): test design, before the record was in force |
| #150 | [5971149551](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5971149551) | 2026-10-03 16:36 | claude | Amendment: calibrator rule, "Platt is the default", replaced only by a gain whose 90% interval excludes 0 | borderline (b): test design, before the record was in force |
| #150 | [5971159688](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5971159688) | 2026-10-03 16:37 | claude | Amendment: calibrator-selection cell "is computed, not read" | borderline (b): test design, before the record was in force |
| #150 | [5971256301](https://github.com/eleonorabjornberg/repo-market-model/issues/150#issuecomment-5971256301) | 2026-10-03 16:49 | claude | Amendment: test scores "no day after the panel end, 2026-09-03"; no overlap with live record | borderline (b): test design, before the record was in force |
| #215 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/215) | 2026-10-03 16:47 | claude | "Eleonora's decision, 3 October 2026": log "the published model's forecast every business day as a frozen live record" via Actions | borderline (c): puts published v1 into the live record (the merge of #226 did it) |
| #215 | [5971274890](https://github.com/eleonorabjornberg/repo-market-model/issues/215#issuecomment-5971274890) | 2026-10-03 16:51 | claude | Note: she has set `live-log` branch protection; PR must say how the push was checked | not binding (scope) |
| #215 | [5971287555](https://github.com/eleonorabjornberg/repo-market-model/issues/215#issuecomment-5971287555) | 2026-10-03 16:53 | claude | Note: protection is ruleset 24422476 (deletion, non_fast_forward only) | not binding (scope) |
| #216 | [5974170640](https://github.com/eleonorabjornberg/repo-market-model/issues/216#issuecomment-5974170640) | 2026-10-03 22:31 | claude | Ruling on Q1/Q2: paired reading, so "The dynamic logit (#137) is the frozen model"; CRPS target kept as reported only; guard raises `LookAheadError` | borderline (b): chose the frozen model "after both outcomes had been shown", before the record was in force |
| #215 | [5974171406](https://github.com/eleonorabjornberg/repo-market-model/issues/215#issuecomment-5974171406) | 2026-10-03 22:31 | claude | Ruling on permission block: hosts being added; resume from branch | not binding (scope) |
| #151 | [5974172527](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5974172527) | 2026-10-03 22:31 | claude | Ruling: "this directive starts only on Eleonora's explicit go"; adds `needs-eleonora` | not binding (gate on (a)) |
| #151 | [5974697778](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5974697778) | 2026-10-03 23:43 | claude | Ruling: "go for #151"; removes `needs-eleonora`; runs after #216 merges. **Withdrawn** by 5975923861 | (a) — withdrawn, "It was not a go" |
| #216 | [5975902619](https://github.com/eleonorabjornberg/repo-market-model/issues/216#issuecomment-5975902619) | 2026-10-04 02:46 | claude | Ruling: "the pre-registration at ff138fb is accepted ... Merge it"; "the orchestrating session merges this PR"; PR merged 3 s later (d76bdf9) | (b): puts the pre-registered primary test in force; the merge was the session's, not hers |
| #151 | [5975923861](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5975923861) | 2026-10-04 02:50 | claude | Ruling: the 23:45 go "is withdrawn. It was not a go"; go must be her exact words "GO #151" | (a) — withdrawal; itself a relay |
| #151 | [5975956989](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5975956989) | 2026-10-04 02:55 | claude | Amendment to the pre-registration: "A second primary test: CRPS" vs as-of persistence; freeze extended; near-blind disclosure | (b) |
| #221 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/221) (PR) | 2026-10-04 03:49 | claude | PR drafting the CRPS-primary amendment; body summarises her rulings, no ruling of its own | not binding (summary of other rows) |
| #221 | [5981849520](https://github.com/eleonorabjornberg/repo-market-model/issues/221#issuecomment-5981849520) | 2026-10-04 15:58 | claude | Ruling: three CRPS choices accepted (one compare, block 2, seed 1970125677; pass rule); labels and block-10 report; "may merge this PR under delegation" | (b); delegated merge of a pre-registration change is also (e)-like |
| #151 | [5982000201](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5982000201) | 2026-10-04 16:17 | claude | Note: "a conditional go has been given"; session to relay "GO #151" once #221 merged and #215 logged its first day | (a) — conditional; delegates the trigger to the session |
| #215 | [5982003724](https://github.com/eleonorabjornberg/repo-market-model/issues/215#issuecomment-5982003724) | 2026-10-04 16:17 | claude | Ruling: "the hosts are added"; resume | not binding (scope) |
| #151 | [5982161024](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5982161024) | 2026-10-04 16:37 | claude | Amendment: expected ≈14.8 leaps, three outcome labels, event-based leap verdict at 40 pooled events; third go condition (#222 merged) | (b) (leap test was then still primary); (a) condition |
| #222 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/222) | 2026-10-04 16:36 (revised same day) | claude | "Eleonora's amendment ... made before any opening"; revised: "Eleonora cut the pooled-at-40 jump report", record-only amendment | borderline (b): records/revises the 16:37 amendment |
| #221 | [5982222615](https://github.com/eleonorabjornberg/repo-market-model/issues/221#issuecomment-5982222615) | 2026-10-04 16:45 | claude | Ruling: "the full-range test is the primary cell"; CRPS h = 1 the one primary cell, every leap/threshold cell "reported only"; may merge under delegation. PR merged by reviewer 18:17 (38bbe1a) | **(b)** — replaces the pre-registered primary test; merged under delegation |
| #215 | [5982223313](https://github.com/eleonorabjornberg/repo-market-model/issues/215#issuecomment-5982223313) | 2026-10-04 16:45 | claude | Ruling: live record logs full distribution; CRPS "is the live record's primary result" | borderline (b): sets the live record's primary result |
| #151 | [5982224483](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5982224483) | 2026-10-04 16:45 | claude | Ruling: primary cell "is now the CRPS cell"; restates three go conditions | (b) restated; (a) conditions |
| #151 | [5982268709](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5982268709) | 2026-10-04 16:50 | claude | Note: go condition 2 tightened (first live file must carry both distributions) | (a) condition |
| #222 | [5982282222](https://github.com/eleonorabjornberg/repo-market-model/issues/222#issuecomment-5982282222) | 2026-10-04 16:52 | claude | Scope: "qualify the 0.11"; recount per-year Jan–Aug leaps | not binding (scope/wording) |
| #224 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/224) (PR) | 2026-10-04 19:41 | claude | PR drafting #222's amendment; quotes the "Scope comment (qualify the 0.11)" | not binding (summary) |
| #226 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/226) (PR) | 2026-10-04 21:35 | claude | PR for #215; table lists "Ruling 4 Oct, 1–4" and "Note of 3 Oct" as implemented | not binding (summary); merged under delegation 21:46 (c69a361, the live pin) |
| #224 | [5985413939](https://github.com/eleonorabjornberg/repo-market-model/issues/224#issuecomment-5985413939) | 2026-10-04 23:04 | claude | Ruling: reported cells' "shown better" uses the leap rule; "Merge it"; "The orchestrating session is merging at a9863ba"; merged 3 s later (f1e390e) | not (b) (reported-only cells), but a pre-registration amendment merged by the session on a relay |
| #151 | [5985434901](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-5985434901) | 2026-10-04 23:07 | claude | Ruling: h = 2–5 CRPS cells carry the label "... not evidence"; "This is not the go" | not binding (wording) |
| #229 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/229) | 2026-10-04 23:07 | claude | Ruling: accepts the h = 2–5 reading; same label in the live record | not binding (wording) |
| #231 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/231) (PR) | 2026-10-04 23:33 | claude | PR applying #229's label; no ruling of its own | not binding (summary) |
| #151 | [6003148702](https://github.com/eleonorabjornberg/repo-market-model/issues/151#issuecomment-6003148702) | 2026-10-05 21:20 (dated "4 October") | claude | Ruling: "GO #151"; says she gave it ~23:20 UTC 4 Oct as "GO eleonorabjornberg/repo-market-model#151" and held it until the first live file was verified; removes `needs-eleonora`. Cited as the opening ruling in `metadata/lockbox.json` | **(a)** — the only authority for opening `near_blind`; no owner-attested comment exists |
| #236 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/236) (PR) | 2026-10-05 23:30 | claude | PR that opens `near_blind` "on Eleonora's 'GO #151'" and drafts the `lockbox.md` amendment; review escalated (`needs-eleonora`); merged 2026-10-06 01:44 (ab08b19) with no ruling comment on the thread | (a) executed; merge actor not attributable (merge events carry no app field) |
| #244 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/244) | 2026-10-06 03:24 | claude | Ruling: fix #243 "as a new model, v2, logged alongside the unchanged v1" | borderline (c): intent for v2 to join; join left to #245 |
| #245 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/245) | 2026-10-06 03:25 | claude | Ruling: v2 "logged alongside the unchanged v1"; "a merge [of #244] means she has accepted v2 for the live record"; version-bump the pinned code | **(c)** and **(d)** — not yet executed (#245 open) |
| #244 | [6008722509](https://github.com/eleonorabjornberg/repo-market-model/issues/244#issuecomment-6008722509) | 2026-10-06 03:27 | claude | Ruling: a further 2026 check of v2 (paraphrased); 2026 check is a gate for #245; gate thresholds "proposed by the orchestrating session" | not binding (scope); gate for (c) |
| #244 | [6008759888](https://github.com/eleonorabjornberg/repo-market-model/issues/244#issuecomment-6008759888) | 2026-10-06 03:31 | claude | Ruling: rescope, wait for #247 diagnosis, build its fix as "pressure model v2" | not binding (scope) |
| #255 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/255) | 2026-10-06 13:45 | claude | Ruling: "file every finding ... put the live-record fixes first"; pin transitions need her own approval | not binding (scope); mechanism for (d) |
| #256 | [issue body](https://github.com/eleonorabjornberg/repo-market-model/issues/256) | 2026-10-06 13:45 | claude | Ruling: "Only your own GitHub action"; defines the owner-attested items (a)–(e) | governance rule itself; not one of (a)–(e) |
| #252 | [6017674192](https://github.com/eleonorabjornberg/repo-market-model/issues/252#issuecomment-6017674192) | 2026-10-06 13:47 | claude | Ruling: outer-validation design (inner 2018–2022, outer 2023–2025), conditional 90% gates "proposed"; v2 joins only on "Eleonora's own GitHub approval" | not binding (scope); gate for (c) |
| #252 | [6017941654](https://github.com/eleonorabjornberg/repo-market-model/issues/252#issuecomment-6017941654) | 2026-10-06 14:02 | claude | Ruling: pressure-day calibration "top priority. Diagnose, then fix"; 50% gates 40–60% proposed | not binding (scope) |
| #255 | [6017974379](https://github.com/eleonorabjornberg/repo-market-model/issues/255#issuecomment-6017974379) | 2026-10-06 14:03 | claude | Ruling: added scope from findings 6 and 10 (pin ancestry test, refuse unknown pins, freeze digests); "Do not regenerate existing pins" | not binding (scope); mechanism for (d) |
