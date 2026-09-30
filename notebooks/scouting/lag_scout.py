"""Scouting run 2, NOT a record: the information-set (lag) question, explored fully.

Every design reads each input at an index array relative to the scored row T:
  pub      last row dated <= T-7 calendar days (the published 6-day purge rule)
  d_asof   T-2 rows: decision is 16:00 on row T-1, so T-2 daily NY Fed / bill values are final
  w_asof   last row dated <= date(T-1) - 6 days (weekly H.4.1: record_date + 5d at 16:30)
  sched    T itself: known-in-advance values (calendar; settlement only under an
           auction-date availability declaration the registry does not yet make)
  s_decl   T-2: settlement under the registry's current declaration (23:59 on settlement day)
Quantile regressors (5 contract levels) and pressure classifiers (level >= 5 / >= 10 bp),
expanding window, refit every 21 scored days, labels only if observable at the block's decision.
"""
import sys, json, time
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

panel, outdir, *ONLY = sys.argv[1:]
d = pd.read_csv(panel, parse_dates=["date"]).reset_index(drop=True)
d["spread_bps"] = (d.sofr - d.iorb) * 100
for c in ("tgcr", "bgcr"):
    d[c + "_spread"] = (d[c] - d.iorb) * 100
n = len(d); dates = d.date.values.astype("datetime64[D]")
T = np.arange(n)
idx = {
    "pub": np.searchsorted(dates, dates - np.timedelta64(6, "D"), side="left") - 1,
    "d_asof": T - 2,
    "w_asof": np.r_[-1, np.searchsorted(dates, dates[:-1] - np.timedelta64(6, "D"), side="right") - 1],
    "sched": T,
    "s_decl": T - 2,
    "own": T,  # a row's own values (one-step pairs)
}
RATES = ["spread_bps", "sofr_p25", "sofr_p75", "sofr_volume"]
DAILY = ["tgcr_spread", "bgcr_spread", "tbill_4w", "tbill_13w"]
WEEKLY = ["reserve_balances", "tga"]
CAL = ["quarter_end", "tax_date", "days_to_month_end"]
SET = ["treasury_settlement_bills", "treasury_settlement_coupons", "treasury_settlement_soma"]

DESIGNS = {  # name -> list of (columns, index key)
    "pub4": [(RATES, "pub")],
    "pub_full_calpub": [(RATES + DAILY, "pub"), (WEEKLY, "pub"), (CAL, "pub"), (SET, "pub")],
    "asof4": [(RATES, "d_asof")],
    "asof_full_nocal": [(RATES + DAILY, "d_asof"), (WEEKLY, "w_asof"), (SET, "s_decl")],
    "asof_full_calpub": [(RATES + DAILY, "d_asof"), (WEEKLY, "w_asof"), (SET, "s_decl"), (CAL, "pub")],
    "asof_full_calT": [(RATES + DAILY, "d_asof"), (WEEKLY, "w_asof"), (SET, "s_decl"), (CAL, "sched")],
    "asof_full_calT_setT": [(RATES + DAILY, "d_asof"), (WEEKLY, "w_asof"), (CAL, "sched"), (SET, "sched")],
}

def matrix(design):
    cols = []
    for names, key in DESIGNS[design]:
        ix = idx[key]
        for c in names:
            v = d[c].values.astype(float)
            cols.append(np.where(ix >= 0, v[np.clip(ix, 0, n - 1)], np.nan))
    return np.column_stack(cols)

y = d.spread_bps.values
first = int(np.where(d.date == pd.Timestamp("2018-07-05"))[0][0])
scored = np.arange(first, n)
BLOCK, LEVELS = 21, (0.05, 0.25, 0.5, 0.75, 0.95)

def label_ok(t, T0, conservative):
    if conservative:  # published purge on training labels
        return dates[t] + np.timedelta64(6, "D") < dates[T0]
    return t <= T0 - 2  # y_t final at 15:00 on row t+1 <= decision row T0-1

def run(design, pairs, classify=False):
    if pairs == "direct":
        X = matrix(design)
    else:  # one-step: a row's own RATES predict the next row; served off the design's rate index
        own = np.column_stack([d[c].values.astype(float) for c in RATES])
        serve_ix = idx["pub" if design.startswith("pub") else "d_asof"]
    conservative = design.startswith("pub")
    Q = np.full((n, len(LEVELS)), np.nan); P = {5: np.full(n, np.nan), 10: np.full(n, np.nan)}
    for b0 in range(0, len(scored), BLOCK):
        T0 = scored[b0]; blk = scored[b0:b0 + BLOCK]
        if pairs == "direct":
            ts = np.array([t for t in range(n) if t < T0 and label_ok(t, T0, conservative)])
            Xt, yt = X[ts], y[ts]
            Xs = X[blk]
        else:
            ts = np.array([t for t in range(1, n) if t < T0 and label_ok(t, T0, conservative)])
            Xt, yt = own[ts - 1], y[ts]
            Xs = own[np.clip(serve_ix[blk], 0, n - 1)]
        ok = ~np.isnan(yt) & (np.isnan(Xt).sum(1) < Xt.shape[1])
        if not classify:
            M = [HistGradientBoostingRegressor(loss="quantile", quantile=a, min_samples_leaf=20,
                 random_state=0).fit(Xt[ok], yt[ok]) for a in LEVELS]
            q = np.sort(np.column_stack([m.predict(Xs) for m in M]), axis=1); Q[blk] = q
        else:
            for thr in (5, 10):
                lab = (yt[ok] >= thr).astype(int)
                if lab.min() == lab.max():
                    P[thr][blk] = lab[0]
                else:
                    P[thr][blk] = HistGradientBoostingClassifier(min_samples_leaf=20, random_state=0
                                  ).fit(Xt[ok], lab).predict_proba(Xs)[:, 1]
    return Q, P

JOBS = [("pub4", "onestep", False), ("asof4", "onestep", False), ("pub4", "direct", False),
        ("asof4", "direct", False), ("pub_full_calpub", "direct", False), ("asof_full_nocal", "direct", False),
        ("asof_full_calpub", "direct", False), ("asof_full_calT", "direct", False),
        ("asof_full_calT_setT", "direct", False),
        ("pub_full_calpub", "direct", True), ("asof_full_calT", "direct", True),
        ("asof_full_calT_setT", "direct", True)]
for design, pairs, cls in JOBS:
    tag = f"{design}__{pairs}__{'cls' if cls else 'q'}"
    if ONLY and tag not in ONLY: continue
    t0 = time.time(); Q, P = run(design, pairs, cls)
    np.savez(f"{outdir}/{tag}.npz", Q=Q, P5=P[5], P10=P[10])
    print(tag, f"{time.time()-t0:.0f}s", flush=True)
