# Decision (draft): weighted miss criteria for the pressure judge

**Status: a DRAFT for Eleonora's review, drafted by the pull request that closes #454. It is not in force.** It is in
force only once she merges it. Even then, making the weighted rule the judge's bar, or using it on the 2026
confirmation tier, changes a pre-registered test, so it needs her own attested approval on GitHub (#256, ruling of
6 October 2026): a comment, review or label event by her whose `performed_via_github_app` is null. A ruling relayed by
the orchestrating session does not authorise it. The weights below are a draft for her to confirm or change.

Origin: Eleonora's ruling of 9 October 2026, relayed by the orchestrating session, to introduce weighted miss criteria
into the pressure judge.

## The rule

A flagged day that is not a pressure day is a **false alarm of weight `w(d)`**, where `d` is the number of trading days
(panel business days) from the flagged day to the nearest pressure day, before or after it:

| distance `d` to the nearest pressure day | weight `w(d)` |
|---|---|
| 1 to 2 trading days | 0.25 |
| 3 to 5 trading days | 0.5 |
| more than 5 trading days, or no pressure day within 5 | 1 |

Pressure day means a day with SOFR − IORB strictly above the threshold scored (+5 bp at the primary threshold), read on
whole basis points (`docs/decisions/pressure-probability.md`). The limit stays at **2 weighted false alarms per
onset**. Two places count false alarms, and both count the weighted sum when the rule is in force:

1. **The flag cut-off rule** (`cutoff_rule` in `metadata/pressure_judge.json`): at each refit, the cut-off with the
   highest onset recall whose weighted false alarms per onset on the training window are at most 2.
2. **Tier 1, the onset-warning tier** (lead at least 1): the worst horizon's weighted false alarms per onset are at
   most 2.

## Why

The false-alarm study (#440, `docs/pivot/onset-diagnostics-result.md`) found that 81% to 95% of each of the five best
rows' false alarms fall within five panel days of a real pressure day, and that days 21 or more panel days from one
hold 0% to 2% of four rows' false alarms (14% for the fifth). Most false alarms are flags beside an episode, on days
whose spread was already at or near the threshold. A flat count treats such a near miss like a warning in calm water.
Under the current rule no model can pass the 2026 window. The weights discount a near miss without forgiving it:
a flag two days from an episode still costs a quarter of a false alarm, and a flag beyond five days costs a whole one.

## The information set

`docs/decisions/information-set.md` applies. Inside the cut-off rule's walk-forward training window, `d` uses only the
pressure days whose outcome was known at the refit's first decision instant (the scored days up to the business day
before it, as `choose_cutoffs` already reads them). A pressure day after that instant cannot lower a weight, even when
it is only a few days after a flagged day inside the window. `false_alarm_weights` raises `LookAheadError` for a day
after the last day known. The test-only scoring of 2018-06-29 to 2025-12-31 may use the full outcome record of those
days: it asks how many false alarms a rule raised, not what it could have known. No day of 2026 is read
(`docs/decisions/lockbox.md`).

## What stays unchanged

- The limit of 2 false alarms per onset, in both places.
- Tier 1's lead (at least 1), its recall condition (at least 0.5, with the interval above climatology), and the far-lead
  reading; tiers 2 to 5; the pass rule.
- The definition of a pressure day, an onset, and the scored days.
- Every published figure. The switch is `in_force` in `metadata/weighted_miss.json`, false in this draft: the judge
  counts every false alarm as 1, exactly as before, and only reports the weighted count beside it. Turning it on is a
  later pull request, made after her ruling and attested approval.

## What the draft leaves to her

- The weights and the bands (0.25 and 0.5; 2 and 5 trading days), and whether the same bands should apply at +10 bp.
- Whether to adopt the rule as the judge's bar at all, and whether to use it on the 2026 confirmation tier. Either
  changes a pre-registered test.
- The scarce-regime reading (a reported-only pass within the scarce regime alone) distances to the pressure days among
  that regime's days only; a pressure day outside the regime is not seen. The draft leaves that as is.

The evidence under both rules is in `docs/pivot/weighted-miss-result.md`.
