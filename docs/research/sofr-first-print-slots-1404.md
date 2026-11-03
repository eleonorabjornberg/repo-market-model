# SOFR first-print capture: how late the scheduled slots started (#1404)

**Operational record, not a result.** Serves H5 (primary goal), groundwork for the prospective confirmation, whose
outcome is "SOFR - IORB as first published" (#940). It changes no data meaning and no published figure.

## What the run history shows

The workflow `sofr-first-print.yml` had five schedule slots (UTC 12:20, 13:20, 13:50, 14:20, 15:20). Read from its run
history on 2 November 2026 (`gh api "repos/eleonorabjornberg/repo-market-model/actions/workflows/sofr-first-print.yml/runs?per_page=100"`,
field `created_at`): on each of the nine business days from 20 October to 30 October exactly five runs started, so the
runs are matched to the slots in order of start. (The API does not record which cron line fired; this matching is an
assumption, and the only one the history allows.)

| Slot (UTC) | Slot (ET, EDT) | Delay, shortest | Delay, median | Delay, longest |
|---|---|---|---|---|
| 12:20 | 08:20 | 4 h 53 min | 5 h 42 min | 6 h 22 min |
| 13:20 | 09:20 | 4 h 32 min | 5 h 17 min | 5 h 59 min |
| 13:50 | 09:50 | 4 h 07 min | 5 h 03 min | 5 h 45 min |
| 14:20 | 10:20 | 4 h 02 min | 5 h 03 min | 5 h 37 min |
| 15:20 | 11:20 | 3 h 56 min | 4 h 37 min | 5 h 16 min |

Every slot started late, by about four to six hours, on each of the nine days; none was on time. The first run of the
day started between 17:13 and 18:42 UTC. The safe window closes at 18:30 UTC while the clocks are on EDT (14:30 ET)
and at 19:30 UTC on EST (from 1 November).

| Day the print was published | First run (UTC) | Outcome | Effective date |
|---|---|---|---|
| 20-23 Oct | 17:13-17:16 | kept | 19, 20, 21, 22 Oct |
| 26 Oct | 18:42:48 | all five refused | 23 Oct lost |
| 27 Oct | 18:03:16 | kept | 26 Oct |
| 28 Oct | 18:22:16 | kept | 27 Oct |
| 29 Oct | 18:30:52 | all five refused (52 s after the revision instant) | 28 Oct lost |
| 30 Oct | 18:02:40 | kept | 29 Oct |
| 2 Nov | 21:44:13 | refused | 30 Oct lost |

Three of ten effective dates are lost since the capture began (23, 28 and 30 October), and two of the three were lost
by minutes. The first print of 16 October (published 19 October) predates the workflow and is outside the list.

## What this change does

* **More slots, same refusal.** A slot every 30 minutes from 12:10 to 19:10 UTC replaces the five; a late slot is still
  refused (`LookAheadError`) and the add-only commit is unchanged. More slots help when the delay varies from slot to
  slot; they cannot help when GitHub starts nothing before 14:30 ET, as on 2 November. That residual risk is the
  reason for the question in the pull request (a second, independent capture path).
* **An alert.** After every slot, `python3 scripts/sofr_first_print.py missing` fails the run and names each business
  day past its revision instant with no file on `sofr-first-prints` and no entry in the tracked list; the workflow
  comments once per day on #225. A 21:30 UTC slot is the evening check.
* **A tracked list.** `metadata/sofr_missed_first_prints.json` holds each lost day with its reason, for the
  confirmation's missing-outcome rule (#1393, rule 8). Nothing is back-filled, and the 14:30 ET refusal is not relaxed.
