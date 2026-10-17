# Are the recurring ~$0.1 bn Fed repo trades announced test exercises? (#872, finding #860)

**Serves:** H3 groundwork G1 (data quality for the take-up recency input), and the inputs of H5 and H7m. **Development data, not a
verdict:** nothing is scored, no spread or forecast is read, the columns stay off `FEATURE_FIELDS` and out of every published
declaration, and no published figure moves. The take-up counts run to 2026-09-03 as the directive asks; they read operation amounts only,
so no locked day counts toward a choice (`docs/decisions/lockbox.md`).

## Answer

**No announcement was found for the recurring trade, so its classification does not change and no size threshold is added.** The Desk's public
record names small value exercises that were announced in advance; every one of them in the tracked snapshots is a morning operation of
$94 mn to $100 mn made of three or four $1 mn propositions per security type (the per-line amounts are in the evidence table), and each already carries the Desk's own
"Small Value Exercise" note, so the rule in force already treats it as not take-up. The recurring operation of #860 is a different thing:
a single afternoon operation (13:29 or 13:30 release, 13:45 close) of $100 mn to $113 mn, mostly one line (27 of 35) and one rate, with no
note and no statement before it. The question whether it is take-up is left to Eleonora with the table below (data meaning is hers).
All figures below are under the rule now in force, #826's (a whole number of millions of at most $7 mn is a test trade, `ingest._effective_accepted`).
Under it the announcement-keyed rule differs from the rule in force on one day, 2024-09-24, an announced $57 mn term repo (see 3 below).

## What was checked

1. **The list** (`evidence/repo-test-trades-872/result.md`): every Repo operation with $0.09 to $0.13 bn accepted in the tracked
   snapshots, 40 operations, with date, id, release and close time, tenor, method, accepted and submitted amounts, the rate or rates, the
   accepted amount per line, and the note. Five carry a small value exercise note and match an announcement; the other 35 do not.
   Of those, all 35 count as take-up under the rule in force (each is above $7 mn). Under the superseded $0.1 bn floor, 34 did (one, 2024-07-09 at $97 mn, was below it).
2. **The Fed's public record**, saved with checksums in `evidence/repo-test-trades-872/sources/` (17 October 2026, one request per page
   from www.newyorkfed.org): the Statements and Operating Policies index, the Desk's repo page and the repo FAQ (neither mentions an
   advance schedule of test trades), and the ten statements from 2024 to May 2026 whose exercise date has passed and that announce a Repo small value exercise
   (each gives its operation date and window; the statement of 13 October 2026 announces a later exercise and is saved, not matched). Two points from them:
   * every announced exercise is a morning operation (08:15 to 10:45), limited to "one $1 million proposition per eligible security type" or
     tranche. None announces an afternoon operation of $0.1 bn;
   * the statement of 10 December 2025 makes the standing overnight repo operations twice daily from 11 December 2025, which is why a
     08:15 operation of $100 mn appears on 2026-04-08 and 2026-07-15. It is a regular operation, not an announced exercise.
3. **Classification, point in time.** The announcement-keyed rule of the directive (an operation announced before it as a small value
   exercise is not take-up) is implemented in the script only, and matches by operation date and announced window. Within the $0.09 to $0.13 bn
   band it matches those five morning operations and nothing else; they are already dropped by their note. Across all operations it also matches
   the term repo of 2024-09-24 (statement of 2024-09-19, window 10:30 to 10:45), which accepted $57 mn and carries no note. Under the superseded
   $0.1 bn floor it was no take-up; under #826's rule (not a whole number of millions) it is take-up, and the announcement-keyed rule would drop it.
   That changes the `fed_repo_*` columns on 2024-09-24 to 2024-09-27 (the day itself, its change column and the days-since count), nothing else.
   No rule was added to `src/`, so there is no new availability guard and no new recorded mutation: the rule has nothing to add.

## `fed_repo_days_since_positive` by year (longest value / number of take-up days)

The panel is the scratch panel to 2026-09-03 (`pressure_v1_1.py panel --end 2026-09-03`, then the script's own assembly).

| year | in force (#826: whole $1-7 mn is a test trade) | superseded floor ($0.1 bn), for comparison | announcement-keyed (this PR) |
|---|---|---|---|
| 2018 | 250 / 0 | 250 / 0 | 250 / 0 |
| 2019 | 250 / 72 | 250 / 72 | 250 / 72 |
| 2020 | 66 / 125 | 124 / 124 | 66 / 125 |
| 2021 | 156 / 1 | 250 / 0 | 156 / 1 |
| 2022 | 250 / 3 | 250 / 0 | 250 / 3 |
| 2023 | 39 / 16 | 250 / 1 | 39 / 16 |
| 2024 | 50 / 24 | 52 / 13 | 50 / 23 |
| 2025 | 32 / 55 | 41 / 44 | 32 / 55 |
| 2026 | 17 / 27 | 22 / 16 | 17 / 27 |
| 2024-01 to 2026-09 | 50 / 106 | 52 / 73 | 50 / 105 |

The superseded-floor column reproduces #860's figures for 2024 to 2026 (longest 52, 41, 22; 13, 44, 16 take-up days). The rule in force (#826)
counts the ~$0.1 bn trade as take-up and drops the whole-million trades of $1 mn to $7 mn, so it has more take-up days than the floor did. The
announcement-keyed column equals it in every cell except 2024 (23 take-up days instead of 24, from the 2024-09-24 term repo), so the `fed_repo_*` panel
columns are not identical under the two: they differ on 2024-09-24 to 2024-09-27 only.

**Effect on H5's candidate inputs:** none. No H5 declaration (the eight listed in the evidence file) names a `fed_repo` column, so the
change on 2024-09-24 to 2024-09-27 reaches none of them. The recency input is read by H2's upper bound (#635) and the unused-inputs
records, not by an H5 candidate.

## Not checked, or for Eleonora

* **Her question (data meaning), second part:** whether the rule in force should also drop an operation the Desk announced as a small value
  exercise beforehand when it is not a whole number of millions of at most $7 mn (one case, the $57 mn term repo of 2024-09-24). Not settled here.
* **Her question (data meaning):** whether the recurring ~$0.1 bn afternoon operation is take-up. The evidence is above: not announced, on calm
  days, roughly monthly (the dates are in the table of the evidence file). A rule that is not a size threshold and not an announcement would
  have to be one she names; none is drafted here. No section of `docs/DATA_QUALITY_DECISIONS.md` is drafted because nothing is classified
  differently; if she rules the trade is not take-up, that is a new rule and a new directive.
* The statement index lists older Repo small value exercise statements (2016 to 2023); they were not fetched, because the operations in
  the $0.09 to $0.13 bn band all fall in 2024 to 2026 in the tracked snapshots, so none could be matched by an older statement.
* Announcements are matched by operation date and window as the statements state them; a Desk change announced elsewhere (a press release,
  a counterparty notice) is not in the public pages read here.
* The ~$0.1 bn trade could be a counterparty's routine use of the facility. That is a reading of the table, not a finding; the Desk's pages
  say nothing about it.
