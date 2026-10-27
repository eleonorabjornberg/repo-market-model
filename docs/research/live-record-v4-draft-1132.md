# Drafts for Eleonora's own GO: the Wednesday wording, and live record version 4 (#1132, from #984)

**Status: a draft, in force only once she approves it.** Nothing on this page is a decision record. Each part below changes a
decision record, a frozen file or the live pin, which a pull request may not do without her own `GO` (`scripts/owner_attested.py`).
They are held here, outside `docs/decisions/`, so this pull request's CI does not need an attestation it cannot cite. Serves H5
groundwork G3 (prospective logging) and development step 3. Development data, not a verdict; nothing is scored or published.

## 1. The wording: `WRESBAL` and `WTREGEN` are week averages, not Wednesday levels

Finding #485 (item 5) and #984 part 3 established that the panel's `reserve_balances` (`WRESBAL`) and `tga` (`WTREGEN`) are the
averages of daily figures over the week ending Wednesday. The Wednesday levels are other series (`WRBWFRBL`, `WDTGAL`). This pull
request corrects the places that are neither a decision record nor frozen: the comment on `WEEKLY_OBSERVATION_WEEKDAY` in
`src/repo_model/asof.py` (outside every definition the final test hashes; `tests/test_final_test_freeze.py` passes), the two table
lines of `docs/diagnosis-exceedance-flattening.md`, and a test docstring.

**Held for her GO (two places).**

(a) `docs/decisions/information-set.md`, rule 1, a decision record. Proposed text, replacing "The H.4.1 weekly series are read per
release: a Wednesday level is first observable ... Each Wednesday level is carried on the rows after it":

> The H.4.1 weekly series are read per release: a weekly value, dated to the Wednesday that ends its week, is first observable at the
> print of its own release, the Thursday after the Wednesday at 16:30 New York time, or the date the Board moved the release to when
> a holiday moves it (the Board's release pages are the evidence, recorded with the declaration). `WRESBAL` and `WTREGEN` are the
> averages of daily figures over that week, not the Wednesday levels. Each weekly value is carried on the rows after it
> (`weekly-carry.md`), and a forecast reads it from the first decision at or after the print and never before.

and in the amendment's first point, "the H.4.1's WRESBAL" read as "the H.4.1's week average of reserve balances (`WRESBAL`)". No rule
changes: the instants, the lags and the carry are as they were. Only the name of the quantity changes.

(b) `src/repo_model/asof.py`, the docstring of `InformationRule._observation_available` ("A weekly field ... is an H.4.1-style
Wednesday level carried forward"). It sits inside `InformationRule`, which the final test freezes by content
(`_FROZEN_PIPELINE`), so even a docstring word moves the frozen checksum. Proposed: "is an H.4.1-style weekly value (the average over
the week ending Wednesday, or a Wednesday level such as `WLRRAOL`) carried forward". Whether to move that checksum is hers.

## 2. Live record version 4: per-field staleness and imputation flags

The change in this pull request (`src/repo_model/field_flags.py`, `scripts/live_record.py`): a version 4 file is a version 3 file
plus a `field_flags` block, and every field a version 3 file has is written as before (`tests/test_live_v4.py` strips the block and
compares bytes). For each horizon and each declared feature, the block records `age_hours`, `latest_public`, `carried` and
`imputed`, with their meanings in the block's own `basis`. They are facts read from the same `InformationRule` reads the forecasts use. **No
threshold is set**: what age counts as too stale is not decided, and nothing is scored from the flags.

Files already in `live-log` stay as they are and still score; `live_score.py` and `live_gap.py` read the versions they read.

**The pin does not move here.** The workflow logs the code the live pin names, so version 4 reaches the live record only when the
pin moves to a commit that has it (`docs/decisions/live-pin.md`: her own attested approval, an entry in
`metadata/owner_attestations.json`). Proposed next step, if she approves: a version-bump record `docs/decisions/live-pin-v4-bump.md`
in the style of `live-pin-v3-bump.md`, and the pin follow-up, each with her `GO`. The pin follow-up must merge outside the window from
16:00 ET until that day's live-log run finishes.
