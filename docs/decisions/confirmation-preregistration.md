# Decision: the 2026 confirmation window, pre-registered for the three frozen candidates

**Status: DRAFT, for Eleonora to review and merge.** A decision is in force only once she has merged this record. The
pull request that closes #585 drafts it, with `metadata/confirmation_preregistration.json`, `repo_model.confirmation` and
`tests/test_confirmation_preregistration.py`. **Merging this record, and opening the window, are Eleonora's own attested
actions** (#256): neither is done by the pull request, and a relayed ruling does not stand in for them. Nothing here scores
a 2026 day.

## The ruling this records

Eleonora, 11 October 2026, on #567 (relayed by the orchestrating session; the freeze itself is hers):

1. The shortlist is frozen at three candidates for the 2026 confirmation window:
   `risk_gbm+every_day+gate+settle+h41+iorb` (PR #582), `risk_gbm+settle+h41` (PR #563's control) and `ngboost_laplace`.
2. No new variant is built to improve scores on the 2018-2025 window for a headline claim. A pass on those days is not a
   confirmation.
3. The pre-registration of the three is drafted as a pull request (code, declaration hashes, judge version). Opening the
   confirmation window is owner-attested.

## What is frozen

`metadata/confirmation_preregistration.json` carries, for each candidate:

* the declaration (`metadata/pressure_judge/candidates/<name>.json`) and its features;
* the sha256 of every file the candidate is scored under: its scoring scripts, the library modules they read directly,
  and the metadata declarations they read (settlement and H.4.1 dating, the risk-date model and its every-day component,
  the false-alarm gate, the announced-IORB input);
* its inputs' availability declarations (`docs/decisions/information-set.md`, `metadata/sources.json`,
  `metadata/sources_measurement.json`, the dating declarations, and for the announced-IORB row
  `docs/decisions/fomc-point-in-time.md` and `docs/decisions/iorb-availability.md`), also hashed;
* the commit the hashes were taken on (`frozen_at.commit`).

For the judge, the same file carries the sha256 of `src/repo_model/pressure_judge.py`, `scripts/pressure_judge.py`,
`metadata/weighted_miss.json`, `docs/decisions/weighted-miss.md` and
`docs/decisions/judge-rulings-10-october.md`, and the digest of `metadata/pressure_judge.json` with
`confirmation.candidates` emptied. That list is left out because naming the candidates in it is the opening; every
other field of the declaration is frozen. The published panel's digest (`metadata/funding_panel_manifest.json`) is frozen
too.

The judge version is the judge as in force at `frozen_at.commit`, which includes the rulings of 10 October 2026 (#536,
PR #550): the pooled tier 1 false-alarm count, the pass rule that requires nothing outside 2018-19, and tier 3 tested only
in regimes with at least 20 pressure days.

## The primary test, the pass rule and the benchmarks

* **Primary test and pass rule:** as in force, and not applied differently here. Tier 1 (onset warning) at lead at least 1,
  tier 3 at every lead and tier 5, under the weighted miss rule in force. Per-lead readings, recall inside and outside
  2018-19 and the equal-weight-per-regime recall are reported, not tiers.
* **Pending amendments, named and not applied:** the start-up cut-off for 2018 (#584), and the open measurements on the
  scarcity state's legs (#586), the satiation level (#587) and always-flag blocks (#588). None changes this record. If one
  merges before the window opens it changes a frozen file; the pre-registration is then amended by a decision, and the guard
  below refuses the window until it is.
* **Benchmarks:** `calendar_climatology` and `persistence_logistic` for the pressure probability, produced the way every
  candidate is, paired on the same days, with the judge's stationary-bootstrap interval, and split by regime, scarcity state
  and pressure-day type. A pooled figure alone is not a result.
* **The window:** 2026-01-01 to 2026-09-03, the judge's `confirmation` window. The look scores that window and nothing else.

## How the three are compared (for Eleonora)

**This is a proposal. The multiplicity correction is a judgement call and is hers.** The draft:

* The family is the three candidates. The contrast for each is the judge's tier 1 recall condition: the recall of onsets
  warned at lead at least 1 against climatology's recall at the same false-alarm rate, paired.
* **Bonferroni across the three:** a candidate is said to beat a benchmark only if the paired interval at level
  1 - 0.10/3 (about 96.7%) excludes zero, in place of the judge's 90%. The 90% intervals are reported beside them.
* The pass rule is read as in force and is reported for all three, unadjusted.
* The three are compared with one another only through the same paired differences, each with the corrected interval. No
  winner is declared from a pooled figure, and no fourth candidate is added after the window is read.

Alternatives she may prefer: Holm's step-down in place of Bonferroni (less conservative, same family), a single
pre-named primary candidate with the other two reported, or a different family if she wants the benchmarks counted. No
scoring code applies the correction yet: it is the scoring directive's to build, from this record.

## The guard, and what opening is

`repo_model.confirmation.require_confirmation_open(candidate, days, where=...)` is the call a scoring script makes before
any model is fitted. It raises `LookAheadError` for a day outside the window, a day of a lockbox tier that has not been
opened, a candidate the judge's `confirmation.candidates` does not name, or a hashed file that no longer matches
(`ValueError` for a name that is not one of the three). It reads the tracked files at call time and takes no argument
that opens anything.

**Opening is naming the three candidates in `confirmation.candidates` of `metadata/pressure_judge.json`,** with her own
attestation in `metadata/owner_attestations.json` (#256). Until then the guard refuses every window day for all three.

**A finding for Eleonora.** `metadata/lockbox.json` already shows the near-blind tier (the same 2026-01-01 to 2026-09-03
days) as opened on 2026-10-05, once, for the final test (#151). It is ordinary history there, so the lockbox no longer
locks the window; the judge's `confirmation.candidates` is the only gate on it, and the guard reads that. The days have
appeared inside published aggregates (`docs/decisions/lockbox.md`, "What it does not change"), so a look at them is
confirmation in the sense of a pre-registered, one-time look at the three, not a blind test. Whether that is what she
means by "confirmation window" is hers to say; this record does not change the lockbox. Days after 2026-09-03 stay locked,
and the guard refuses them whatever the judge's list says.

## What this changes

Nothing about how any published figure is scored, and nothing in `metadata/lockbox.json`, `metadata/pressure_judge.json` or
`docs/runs/`. It adds a file, a module that checks it, a script that fills its hashes (`scripts/confirmation_preregistration.py`),
and tests.

## Not checked

* The code each candidate runs through is hashed at the files its scoring scripts read directly. A module they reach
  further down is not listed; the full test suite and the recorded results are the check on those.
* The availability of each input is the declarations' own; this record does not re-audit them.
* No scoring code applies the multiplicity correction; none scores the window.
