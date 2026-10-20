# Decision (draft): the FOMC meeting calendar as columns read at the target day

**Status: DRAFT for Eleonora's review (#1038). Not in force until she merges it.** The module, the register and the
source declaration it describes are built and tested; no published declaration, panel or record reads them.

## What is built

- `metadata/fomc_calendar.json`: every scheduled meeting from January 2018 (the 2018 schedule was public from 11 May
  2017), each dated by the Board's press release that first listed it, with the release's own "For release at" time;
  the unscheduled meetings, each dated by the release that first reported it; the notation votes, listed apart (they
  are not meetings); and the one cancellation. It is built by `scripts/build_fomc_calendar.py` from the Board's pages
  tracked under `tests/fixtures/snapshots/fomc_calendar/`, and `--check` rebuilds it.
- `repo_model.fomc_calendar`: `fomc_meeting_day` and `fomc_days_to_next_meeting` for a target day, read at the decision
  instant of the panel day `h` rows before it (rule 2 of `information-set.md`), and `require_public`, the guard that
  raises `LookAheadError` for a meeting used before it was public.
- `fomc_calendar` in `metadata/sources_measurement.json`: the source declaration. It is not in `metadata/sources.json`,
  which the final-test pre-registration freezes by its bytes, and the columns are not in `contract.FEATURE_FIELDS`.

## The rule it applies

`fomc-point-in-time.md` decides it: a meeting counts from the moment it was publicly scheduled and stops counting from
the moment its cancellation was public. The Board's calendar pages say each date is tentative until the Committee
confirms it at the meeting before it; in the tracked schedules no date moved except the cancelled 17-18 March 2020
meeting, so the first listing is the declared availability.

## Marked questions for Eleonora

1. **The cancellation instant of 17-18 March 2020.** The Board's page marks the meeting "(cancelled)" and dates
   nothing. The register declares it public at 17:00 EDT on 15 March 2020, the release of the statement that closed the
   Committee's unscheduled meeting that day. The meeting stays visible, rather than vanishing early, until that instant; a decision made
   on 13 March or before reads it as a meeting day for the 17th and 18th, and one made on 16 March reads it as none.
2. **Both days of a two-day meeting are meeting days.** The alternative is the decision day (the second day, when the
   statement is released) alone. The columns are built for the first reading; the second is one line to add.
3. **The wait to the next meeting** counts to a meeting's first day, is 0 on that day and the next meeting's distance
   on the second day, and is capped at 90 calendar days (never missing). The cap binds only past the last published
   schedule.
4. **Unscheduled meetings** are meeting days only from their own announcement, which for 4 October 2019 (reported on 11
   October) and 15 March 2020 is after the day itself. At any horizon of one or more panel days they therefore never
   mark their own day, which is the point-in-time reading and not an omission.
5. **Publishing** (whether the columns join a published declaration) is not decided here and is a separate
   `needs-eleonora` issue.
