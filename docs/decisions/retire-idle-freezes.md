# Decision (draft): retire the freezes that protect no live registration

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1134, on her ruling of 22
October 2026 ("we need to move away from freezing things"). It takes effect only once she merges it with her own `GO`.
**The code change behind it is not in this pull request** (see "What is not done"). Serves the process directive
#1134 and unblocks #1106.

## Why

Nothing is registered today, and the freezes block fixes. #1106's corrected `nyfed_sofr` text edits
`metadata/sources.json`, which the final-test pre-registration freezes by its bytes (amendment of 7 October 2026,
#324), so it moves both pinned checksums and fails `tests/test_final_test_freeze.py` until a re-pin she merges.

## The rule

A freeze stays only where it guards one of three things: a **published record** (`docs/runs/`), the **lockbox**
(`docs/decisions/lockbox.md`, `metadata/lockbox.json`), or the **live pin** (`docs/decisions/live-pin.md`,
`metadata/live_pin.json`). A freeze that guards none of them is retired: the file or definition becomes an ordinary
reviewed file, changed in an ordinary pull request with no re-pin.

## Inventory

| Freeze | Where | Guards | Proposal |
|---|---|---|---|
| The `inputs` key of both final-test declarations: sha256 of `metadata/sources.json`, `metadata/evaluation_splits.json`, `metadata/market_holidays.json`, and the as-of, loader, splitter and contract code (`asof.py`, `splits.py`, `evaluation_splits.py`, `contract.py`, `registry.py`, and three definitions of `data.py`) | `scripts/final_test_preregistration.py` (`_FROZEN_METADATA`, `_FROZEN_PIPELINE`, `frozen_inputs`); pins in `docs/decisions/final-test-preregistration.md`; `FrozenInputsTests` in `tests/test_final_test_freeze.py` | Nothing live. The published run (`docs/runs/final_test_near_blind.json`) carries the checksums from before #324, and the record keeps them "at opening". | **Retire.** This is the freeze that blocks #1106. |
| The pinned extended checksums ("Declaration checksum", "CRPS declaration checksum") | `docs/decisions/final-test-preregistration.md` | Only the `inputs` extension above. | **Re-pin once** when the `inputs` key goes: the leap checksum returns to the one the opening run carried; the CRPS checksum moves once (its source hash reaches `crps_declaration`). After that, edits to the retired files need no re-pin. |
| The model, calibrator, leap-target, baseline and CRPS-path source hashes of both declarations, and the cells and their roles | same script and test | The published run's record, and the blind tier, which `lockbox.md` says "becomes the next test" and is still locked. | **Keep.** |
| "At opening" checksums and the opening-hash tests (`test_without_the_inputs_…`, `test_the_leap_checksum_is_the_regenerated_one`) | `tests/test_final_test_freeze.py`, `tests/test_final_test_opening.py`, `tests/test_score_naming.py` | A published record: the run names the declaration it ran. | **Keep** (adapted: with `inputs` gone the leap checksum equals the opening one directly). |
| Live scorer checksum (`live_declaration_checksum`) | `scripts/live_score.py`, `tests/test_live_score_freeze.py`, pin in `docs/decisions/drafts/lockbox-live-record.md` | The scoring of the live record on the blind tier. That amendment is itself still a draft. | **Keep, and ask** (Question 1). |
| The live pin and its environment lock | `metadata/live_pin.json`, `metadata/live_requirements.lock`, `scripts/live_pin.py`, `tests/test_live_pin.py` | The live pin. | **Keep.** |
| Lockbox tiers | `metadata/lockbox.json`, `src/repo_model/lockbox.py`, `tests/test_lockbox.py` | The lockbox. | **Keep.** |
| Published records of `docs/runs/` and their tests | `docs/runs/`, "never edit a published record in place" | Published records. | **Keep.** |
| `ONE_STEP_ALLOW_LIST`: `published_distribution_crps` | `src/repo_model/one_step_guard.py` | The final test's frozen `CRPS_COMMAND` and the live record, whose bytes must reproduce. | **Keep.** |
| `ONE_STEP_ALLOW_LIST`: `gbm_funding_634`, `pressure_model_v2`, `aligned_calendar_1027_h1`, `aligned_calendar_1027_h2_to_h5` | same | Declarations whose figures must reproduce, three with an end date. None is a published record or a registration. | **Ask** (Question 2). Adding to this list is already hers; removing is hers too. |
| Frozen declarations under `metadata/` (for example `spread_distribution_632.json`, `dist_roll_606.json`, `kinked_626.json`), the `uncommitted declaration is refused` checks, and the percentile pin of `backfill_spread_633.py` | `metadata/*.json`, their scripts and tests | Development evidence, not a registration. Their results are in `docs/research/`, with the ones published in `docs/runs/`. | **Keep for now.** Not read one by one: they stop nothing today, and none edits `sources.json` or the pipeline. Listed so she can rule on them (Question 3). |
| The freeze of `metadata/sources.json` by bytes, as written in `docs/decisions/information-set.md` (line on turning a source on) and `docs/decisions/fomc-calendar.md` | those records | The `inputs` extension above. | **Amend the two sentences** with the same merge so they no longer say the file is frozen. The separate `metadata/sources_measurement.json` registry was created to avoid this freeze (#968); it may stay as it is. |

## What changes when she merges this

1. The `inputs` key leaves `declaration()` and `crps_declaration()` in `scripts/final_test_preregistration.py`
   (`_FROZEN_METADATA`, `_FROZEN_PIPELINE`, `frozen_inputs`). `FrozenInputsTests` is replaced by tests that an edit to
   `metadata/sources.json`, `metadata/evaluation_splits.json`, `metadata/market_holidays.json` or the as-of code moves
   neither checksum, and that the leap checksum is the one the opening run carried.
2. The two pins in `docs/decisions/final-test-preregistration.md` are re-pinned once, and its amendment of 7 October
   2026 gets a note that it is retired by this record.
3. #1106 lands its corrected text with no re-pin.

Everything else in the table marked **Keep** is untouched.

## What is not done

The code change in "What changes" is **not in this pull request**: the session's permission check refused the edit that
removes the `inputs` freeze's tests, as "Security Test Removal", and this session did not work around that. Until it
lands, the record is a draft with nothing behind it. Her `GO` on this pull request, or on the change itself, lets a
later run write it.

## Questions for Eleonora

Each has a default that applies if she has not answered by the next 5 pm batch. No default changes what the project
claims.

1. **The live scorer checksum (`tests/test_live_score_freeze.py`).** (a) Keep it; (b) retire it until the live record's
   scoring amendment is merged. *Default: (a).*
2. **The four non-published `ONE_STEP_ALLOW_LIST` entries.** (a) Keep all, each with its end date; (b) retire
   `gbm_funding_634` and `pressure_model_v2` now, and let the two 1027 entries lapse on their end date. *Default: (a).*
3. **Frozen declarations under `metadata/`.** (a) Keep; (b) a follow-up directive inventories them one by one.
   *Default: (a).*
