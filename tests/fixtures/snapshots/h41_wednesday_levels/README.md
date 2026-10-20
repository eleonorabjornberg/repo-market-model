# H.4.1 Wednesday levels (#970)

Two FRED series, fetched on 19 October 2026 (one request each, `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`)
and kept as served, in millions of US dollars, latest vintage:

- `WRBWFRBL`: reserve balances with Federal Reserve Banks, Wednesday level. Beside `WRESBAL`, its week average.
- `WDTGAL`: Treasury General Account, Wednesday level. Beside `WTREGEN`, its week average.

Same release as the week averages (the H.4.1, FRED release 20). Checksums: `SHA256SUMS`.

FRED serves the latest vintage, so a re-fetch does not reproduce these bytes. The ALFRED check of the never-revised claim was not
made: `alfred.stlouisfed.org` is refused by this environment's proxy (`CONNECT` 403), and `fred.stlouisfed.org/graph/fredgraph.csv`
ignores a `vintage_date` parameter (it returned the latest vintage, 22,870 bytes, for `WRBWFRBL` with `vintage_date=2019-09-16`).
