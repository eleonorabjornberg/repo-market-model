# `new-sources-due-diligence.md` against the Fed repo take-up change (#692)

**Finding: nothing in the page depends on the 2018-05 to 2019-09 values of the `fed_repo_*` columns. No statement or figure
in it moves, and it does not need a re-run.** It is a table of candidate sources, not a scored screen (#630 step 1, "before any
fetch"): it reads no panel column and reports no score.

## Evidence

The change (`docs/pivot/fed-repo-data-meaning-result.md`) is confined to panel rows 2018-05-09 to 2019-09-16 of the `fed_repo_*`
columns (see `data-diff.md` in this directory). A search of the page for every way it could depend on them:

```
grep -n -i "fed_repo\|fed_liquidity\|days_since\|test operation\|take-up\|take up\|srf\|repo_" docs/pivot/new-sources-due-diligence.md
grep -n "2018\|2019" docs/pivot/new-sources-due-diligence.md
```

* `fed_repo`, `fed_liquidity`, `days_since` and `test operation` do not occur anywhere in the page.
* The page touches the Fed repo operations in one place, **row 1** (line 26), "Standing repo facility, daily take-up and
  propositions": verdict **Do not use**, because take-up and propositions "are carried; a second copy would only repeat them". The
  row names the series by their source and field names (`nyfed_srf`/`srf_total_accepted`, and `nyfed_repo_ops` with
  `repo_accepted`, `repo_submitted`, `repo_rate`, `repo_ops_accepting`) and says the declared lags apply. It states no value,
  count, date range or score for them. #662 changed what `repo_accepted` and `repo_submitted` mean (take-up demand signals,
  `field_meanings` in `metadata/sources_measurement.json`) and left out the six test operations; the row's claim, that the
  take-up and propositions are already held, is still true after it, and the verdict does not rest on any 2018-2019 value.
* The other `repo_` hits are not the Desk's repo operations: primary dealer repo financing (`pd_repo_ust`, `pd_repo_mbs`,
  `pd_reverse_repo_ust`, rows 4 and the notes), OFR segments, N-MFP `mmf_repo_holdings`, and ON RRP (`nyfed_on_rrp*`, row 2).
  None of them is read through `fed_liquidity.py`.
* The figures in the page are about other sources: withheld primary dealer weeks (85 of 666, 72, 3), the real-time start
  2020-09-09 of the OFR series, and 3,557 of 3,562 auction rows with a result. None is derived from a panel or from any
  `fed_repo_*` value. The 2018 and 2019 hits in the page are the start of tracked tables (`auctions_2018_present.json`, "back to
  2018", renamed DTS lines between 2018 and 2024), not Desk repo values.
* The published panel `4ddc3882…` and every panel stage before `fed_liquidity.py` are byte-identical before and after #662
  (`data-diff.md`), so a statement resting on the registry or the published panel (`nyfed_srf`, ON RRP, the lag declarations)
  is not touched either.

## What would make it depend on them

Only a later step that scores a candidate against a panel including `fed_repo_*` columns (none is in the page). Row 1 is
"Do not use", so no such step follows from it.

## Not checked

The page was read in full for the Fed repo series and searched as above; the later notes (corrections of #680 and others)
were read for the same terms. Whether Eleonora wants the record annotated is her call; no record is edited in place.
