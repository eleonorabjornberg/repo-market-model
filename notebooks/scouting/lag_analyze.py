import sys, glob, json, os
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression

panel, outdir = sys.argv[1:3]
d = pd.read_csv(panel, parse_dates=["date"]).reset_index(drop=True)
y = ((d.sofr - d.iorb) * 100).values; n = len(d)
dates = d.date.values.astype("datetime64[D]")
pub = np.searchsorted(dates, dates - np.timedelta64(6, "D"), side="left") - 1
first = int(np.where(d.date == pd.Timestamp("2018-07-05"))[0][0]); S = np.arange(first, n)
yr = d.date.dt.year.values
press = ((d.days_to_month_end <= 1) | (d.quarter_end == 1) | (d.tax_date == 1)).values
groups = {"all": S, "2018-19": S[yr[S] <= 2019], "2020": S[yr[S] == 2020], "2021-23": S[(yr[S] >= 2021) & (yr[S] <= 2023)],
          "2024": S[yr[S] == 2024], "2025-26": S[yr[S] >= 2025], "press": S[press[S]]}
# as-of trailing volatility (RMS of 20 one-step changes ending at T-2), terciles over scored days
dy = np.r_[np.nan, np.diff(y)]
vol = np.array([np.sqrt(np.nanmean(dy[max(1, t - 21):t - 1] ** 2)) if t > 22 else np.nan for t in range(n)])
cut = np.nanquantile(vol[S], [1 / 3, 2 / 3])
terc = {"calm": S[vol[S] <= cut[0]], "mid": S[(vol[S] > cut[0]) & (vol[S] <= cut[1])], "stress": S[vol[S] > cut[1]]}
LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)

def pin(ix, Q):
    return np.mean([np.mean(np.maximum(a * (y[ix] - Q[ix, j]), (a - 1) * (y[ix] - Q[ix, j]))) for j, a in enumerate(LEVELS)])

print("== point/quantile (MAE bp by slice; pinball; raw q05-q95 coverage, below/above miss)")
rows = []
rows.append(("persistence pub rule", {g: np.mean(np.abs(y[ix] - y[pub[ix]])) for g, ix in groups.items()}, None))
rows.append(("persistence as-of", {g: np.mean(np.abs(y[ix] - y[ix - 2])) for g, ix in groups.items()}, None))
order = ["pub4__onestep__q", "pub4__direct__q", "asof4__onestep__q", "asof4__direct__q", "pub_full_calpub__direct__q",
         "asof_full_nocal__direct__q", "asof_full_calpub__direct__q", "asof_full_calT__direct__q", "asof_full_calT_setT__direct__q"]
for tag in order:
    f = f"{outdir}/{tag}.npz"
    if not os.path.exists(f): continue
    Q = np.load(f)["Q"]
    rows.append((tag, {g: np.mean(np.abs(y[ix] - Q[ix, 2])) for g, ix in groups.items()}, Q))
hdr = "".join(f"{g:>9s}" for g in groups)
print(f"{'':32s}{hdr}{'pinball':>9s}{'cov90':>7s}{'below':>7s}{'above':>7s}  calm/mid/stress cov")
for name, m, Q in rows:
    line = f"{name:32s}" + "".join(f"{m[g]:9.3f}" for g in groups)
    if Q is not None:
        ix = S; lo, hi = Q[ix, 0], Q[ix, 4]
        line += f"{pin(ix, Q):9.3f}{np.mean((y[ix] >= lo) & (y[ix] <= hi)):7.3f}{np.mean(y[ix] < lo):7.3f}{np.mean(y[ix] > hi):7.3f}  "
        line += "/".join(f"{np.mean((y[t] >= Q[t, 0]) & (y[t] <= Q[t, 4])):.2f}" for t in terc.values())
    print(line)

print("\n== pressure probability: event = SOFR-IORB >= thr on the scored day")
def refit_logit(xcol):  # monthly-refit logistic on one column, labels observable at the block decision
    P = {5: np.full(n, np.nan), 10: np.full(n, np.nan)}
    for b0 in range(0, len(S), 21):
        T0 = S[b0]; blk = S[b0:b0 + 21]; ts = np.arange(2, T0 - 1)
        for thr in (5, 10):
            lab = (y[ts] >= thr).astype(int); x = xcol[ts].reshape(-1, 1)
            ok = ~np.isnan(x[:, 0])
            if lab[ok].min() == lab[ok].max(): P[thr][blk] = lab[ok][0]; continue
            P[thr][blk] = LogisticRegression().fit(x[ok], lab[ok]).predict_proba(xcol[blk].reshape(-1, 1))[:, 1]
    return P
clim = {thr: np.array([np.mean(y[2:t - 1] >= thr) if t > 3 else np.nan for t in range(n)]) for thr in (5, 10)}
base = {"climatology (expanding)": clim,
        "persistence-logit pub rule": refit_logit(np.where(pub >= 0, y[np.clip(pub, 0, n - 1)], np.nan)),
        "persistence-logit as-of": refit_logit(np.r_[np.nan, np.nan, y[:-2]])}
for tag in ["pub_full_calpub__direct__cls", "asof_full_calT__direct__cls", "asof_full_calT_setT__direct__cls"]:
    f = f"{outdir}/{tag}.npz"
    if os.path.exists(f):
        z = np.load(f); base[tag] = {5: z["P5"], 10: z["P10"]}
for thr in (5, 10):
    ev = y >= thr
    print(f"-- thr {thr} bp: events on {ev[S].sum()} of {len(S)} scored days ({ev[S & 0 + S][press[S]].sum() if False else ev[S][press[S]].sum()} on pressure days)")
    print(f"{'':34s}{'Brier':>8s}{'BSS':>8s}{'AUROC':>8s}{'AUROC 25-26':>12s}{'Brier press':>12s}{'AUROC press':>12s}")
    bc = np.mean((clim[thr][S] - ev[S]) ** 2)
    for name, P in base.items():
        p = P[thr]; r = S[yr[S] >= 2025]; pr = S[press[S]]
        au = lambda ix: roc_auc_score(ev[ix], p[ix]) if 0 < ev[ix].sum() < len(ix) else float("nan")
        b = np.mean((p[S] - ev[S]) ** 2)
        print(f"{name:34s}{b:8.4f}{1 - b / bc:8.3f}{au(S):8.3f}{au(r):12.3f}{np.mean((p[pr] - ev[pr]) ** 2):12.4f}{au(pr):12.3f}")

print("\n== P(>=5bp) around the two episodes")
for lo, hi in (("2019-09-12", "2019-09-19"), ("2025-10-27", "2025-11-03")):
    m = (d.date >= lo) & (d.date <= hi)
    tab = pd.DataFrame({"date": d.date[m].dt.date, "spread": y[m].round(1)})
    for name in ("persistence-logit as-of", "pub_full_calpub__direct__cls", "asof_full_calT_setT__direct__cls"):
        if name in base: tab[name.split("__")[0][:18]] = base[name][5][m].round(2)
    print(tab.to_string(index=False))
