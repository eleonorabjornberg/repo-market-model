#!/usr/bin/env python3
"""H1 step 3 (#1022): the block length of H5's loss differentials after April 2020, with and without 2019-09-18.

A report that changes nothing: `scoring_protocol.BLOCK_LENGTH`, `WINDOW_BLOCK` and `HAC_LAG` stay as decided and so does
`docs/decisions/scoring-protocol.md` section 5. Development days only (no day after 2025-12-31, no lockbox day), from the
walks of `gbm_funding` that #980 (`scripts/block_length_949.py`) read; the decision days, the d_t and the Politis-White
function are #980's, and `run` refuses to write unless it reproduces #980's recorded figures for the pooled full history.

For d_t = S(B) - S(`gbm_funding`), lead-averaged, with B = B1 and with B = B2, and for the proxy S(B1) - S(B2) that Lens C of
the five-lens review (#958) read, it measures, on each history (full, without 2019-09-18, without the decision days whose
five targets include 2019-09-18, post-2020-04) and, for the post-2020-04 history, within each declared regime:
- the autocorrelation function at lags 1, 2, 3, 5, 10, 21 and 42;
- the Politis-White automatic block length for the stationary bootstrap, with the truncation capped as Patton, Politis and
  White (2009) cap it (ceil(sqrt N) + K_N) and with the cap widened to N / 4;
- the long-run-variance ratio of Newey and West at lags 10, 40 and 100 (Lens C's formula, 1 + 2 sum (1 - k / (L + 1)) rho(k)),
  and the factor by which the lag-10 standard error understates the lag-100 one.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk \\
        --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
    PYTHONPATH=src python3 scripts/block_length_1022.py run --published PUB.csv --walks OUT --output OUT/block1022.json
    python3 scripts/block_length_1022.py report OUT/block1022.json
    python3 scripts/block_length_1022.py check

`run` writes the record; `report` copies it to `docs/research/block-length-1022/result.json` and writes the page
`docs/research/block-length-1022-result.md`; `check` fails when the page is not what the record gives.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402

RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "block-length-1022" / "result.json"
PAGE = RESEARCH / "block-length-1022-result.md"
RECORD_980 = RESEARCH / "block-length-949" / "result.json"
PROTOCOL_BLOCK = 10
#: Decision days from this day are "post-2020-04" (as #886, #922 and #1014 read them).
FIRST_POST_2020 = date(2020, 4, 3)
EXCLUDED_DAY = date(2019, 9, 18)
ACF_LAGS = (1, 2, 3, 5, 10, 21, 42)
LRV_LAGS = (10, 40, 100)
ACF_MAX = max(LRV_LAGS)
#: A group needs this many days to be summarised, and a long-run ratio at lag L needs 3 L days.
MINIMUM_DAYS = 120
HISTORIES = ("full", "without 2019-09-18", "without the decision days reaching 2019-09-18", "post-2020-04")
SERIES = ("B1", "B2", "proxy")
SERIES_TITLE = {
    "B1": "d = S(B1) - S(gbm_funding), the B1 leg",
    "B2": "d = S(B2) - S(gbm_funding), the B2 leg",
    "proxy": "d = S(B1) - S(B2), the proxy Lens C read",
}
#: Lens C of the five-lens review (docs/reviews/2026-10-19-five-lens/lens-C-rates-quant.md, section 3.3 and appendix), on a
#: proxy of the loss differential (B1 and B2 grid CRPS, decision day, post-2020-04): the figures to reproduce or refute.
LENS_C = {
    "acf": {"1": 0.726, "2": 0.484, "3": 0.363, "5": 0.249, "10": 0.278, "21": 0.307, "42": 0.162},
    "lrv_ratio": {"10": 4.94, "40": 11.9, "100": 19.3},
    "politis_white_post_2020": 108.0,
    "politis_white_2021_23": 114.0,
    "politis_white_full": 8.6,
}
REPRODUCTION_TOLERANCE = 1e-9


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


base = _load("block_length_949")


# -- the pieces --------------------------------------------------------------------------------------------------------


def lrv_ratio(rho: Sequence[float], lag: int) -> float:
    """Newey and West's long-run variance of the mean over the variance, 1 + 2 sum_{k<=L} (1 - k / (L + 1)) rho(k)."""

    if lag > len(rho):
        raise ValueError(f"a long-run ratio at lag {lag} needs {lag} autocorrelations and there are {len(rho)}")
    return 1.0 + 2.0 * sum((1.0 - k / (lag + 1.0)) * rho[k - 1] for k in range(1, lag + 1))


def history(pairs: Iterable[Tuple[date, float]], name: str, window: Iterable[date] = ()) -> List[float]:
    """The values of (day, d) pairs on one history. `window` holds the decision days whose targets include 2019-09-18."""

    if name == "full":
        return [v for _, v in pairs]
    if name == "without 2019-09-18":
        return [v for d, v in pairs if d != EXCLUDED_DAY]
    if name == "without the decision days reaching 2019-09-18":
        drop = set(window) | {EXCLUDED_DAY}
        return [v for d, v in pairs if d not in drop]
    if name == "post-2020-04":
        return [v for d, v in pairs if d >= FIRST_POST_2020]
    if name == "post-2020-04 without 2019-09-18":
        return [v for d, v in pairs if d >= FIRST_POST_2020 and d != EXCLUDED_DAY]
    raise ValueError(f"{name!r} is not a history of this study")


def days_reaching(calendar: Sequence[date], days: Iterable[date], hit: date, leads: Sequence[int] = sp.HORIZONS) -> Set[date]:
    """The decision days among `days` whose targets at `leads` business days include `hit`, other than `hit` itself."""

    position = {d: i for i, d in enumerate(calendar)}
    out = set()
    for day in days:
        i = position[day]
        if day != hit and any(i + h < len(calendar) and calendar[i + h] == hit for h in leads):
            out.add(day)
    return out


def proxy(d_b1: Dict[date, float], d_b2: Dict[date, float]) -> Dict[date, float]:
    """S(B1) - S(B2) = (S(B1) - S(g)) - (S(B2) - S(g)), on the days both legs have."""

    return {d: d_b1[d] - d_b2[d] for d in d_b1 if d in d_b2}


def summarize(values: Sequence[float]) -> Dict[str, object]:
    """The autocorrelations, the automatic block lengths and the long-run ratios of one consecutive series."""

    n = len(values)
    if n < MINIMUM_DAYS:
        return {"n": n, "thin": True}
    rho = base.acf(values, ACF_MAX)
    lrv = {str(lag): (lrv_ratio(rho, lag) if n >= 3 * lag else None) for lag in LRV_LAGS}
    long_lag, short_lag = lrv[str(LRV_LAGS[-1])], lrv[str(LRV_LAGS[0])]
    understated = math.sqrt(long_lag / short_lag) if long_lag is not None and short_lag and long_lag > 0 else None
    return {
        "n": n,
        "mean_d": sum(values) / n,
        "acf": {str(k): rho[k - 1] for k in ACF_LAGS},
        "politis_white": base.politis_white(values),
        "politis_white_wide": base.politis_white(values, max_truncation=n // 4),
        "lrv_ratio": lrv,
        "se_understated_10_vs_100": understated,
    }


# -- the data ----------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    from repo_model.data import load_daily_panel

    d_series, meta = base.series(args.published, args.walks)
    calendar = [row.date for row in load_daily_panel(args.published)]
    days = meta["days"]
    legs = {"B1": d_series["B1"]["avg"], "B2": d_series["B2"]["avg"]}
    legs["proxy"] = proxy(legs["B1"], legs["B2"])
    window = days_reaching(calendar, days, EXCLUDED_DAY)

    recorded = json.loads(RECORD_980.read_text(encoding="utf-8"))["comparisons"]
    reproduced, recorded_block = {}, {}
    for b in ("B1", "B2"):
        got = base.politis_white([legs[b][d] for d in sorted(legs[b])])
        want = recorded[b]["avg"]["all"]
        reproduced[b], recorded_block[b] = got, want["politis_white"]
        if abs(got - want["politis_white"]) > REPRODUCTION_TOLERANCE or len(legs[b]) != want["n"]:
            raise ValueError(f"{b}: Politis-White {got} over {len(legs[b])} days here and {want['politis_white']} over "
                             f"{want['n']} days in #980's record")
    record: Dict[str, object] = {
        "panel_sha256": hashlib.sha256(args.published.read_bytes()).hexdigest(),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "first_post_2020_day": FIRST_POST_2020.isoformat(),
        "excluded_day": EXCLUDED_DAY.isoformat(),
        "window_days_dropped": sorted(d.isoformat() for d in window),
        "gbm_funding_missing": meta["missing"],
        "regimes": [r for r in meta["regimes"] if any(meta["regime"][d] == r for d in days)],
        "reproduces_980": {"days": len(legs["B1"]), "recorded_days": recorded["B1"]["avg"]["all"]["n"],
                           "politis_white": reproduced, "recorded_politis_white": recorded_block},
        "series": {},
    }
    for name in SERIES:
        pairs = sorted(legs[name].items())
        entry: Dict[str, object] = {"all": {h: summarize(history(pairs, h, window)) for h in HISTORIES}, "regime": {}}
        post = [(d, v) for d, v in pairs if d >= FIRST_POST_2020]
        for label in record["regimes"]:
            chosen = [v for d, v in post if meta["regime"][d] == label]
            if chosen:
                entry["regime"][label] = summarize(chosen)
        early = [(d, v) for d, v in pairs if meta["regime"][d] == "2018-19"]
        entry["regime"]["2018-19 (with 2019-09-18)"] = summarize([v for _, v in early])
        entry["regime"]["2018-19 (without 2019-09-18)"] = summarize(history(early, "without 2019-09-18"))
        record["series"][name] = entry
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


# -- the report --------------------------------------------------------------------------------------------------------


def f(value, digits=2):
    return "n/a" if value is None else f"{value:.{digits}f}"


def _rows(entries: Dict[str, Dict[str, object]], order: Sequence[str]):
    acf_head = " | ".join(f"rho({k})" for k in ACF_LAGS)
    acf = ["| group | days | mean d | " + acf_head + " |", "|---|---|---|" + "---|" * len(ACF_LAGS)]
    blk = ["| group | days | Politis-White block | block, cap widened to N / 4 | long-run ratio, lag 10 | lag 40 | lag 100 | "
           "lag-10 s.e. understates lag-100 by |", "|---|---|---|---|---|---|---|---|"]
    for name in order:
        e = entries[name]
        if e.get("thin"):
            acf.append(f"| {name} | {e['n']} | too thin | " + " | ".join("" for _ in ACF_LAGS) + " |")
            blk.append(f"| {name} | {e['n']} | too thin | | | | | |")
            continue
        acf.append(f"| {name} | {e['n']} | {f(e['mean_d'], 3)} | " + " | ".join(f(e["acf"][str(k)]) for k in ACF_LAGS) + " |")
        r = e["lrv_ratio"]
        blk.append(f"| {name} | {e['n']} | {f(e['politis_white'], 1)} | {f(e['politis_white_wide'], 1)} | "
                   f"{f(r['10'], 1)} | {f(r['40'], 1)} | {f(r['100'], 1)} | {'n/a' if e['se_understated_10_vs_100'] is None else f(e['se_understated_10_vs_100'], 1) + 'x'} |")
    return acf, blk


def render(record) -> str:
    rep = record["reproduces_980"]
    first = record["first_post_2020_day"]
    lines = [
        "# Block length of the loss differentials after April 2020, without 2019-09-18 (#1022, H1 step 3)", "",
        "**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.BLOCK_LENGTH` stays "
        f"{PROTOCOL_BLOCK}, `WINDOW_BLOCK` and `HAC_LAG` stay as decided, and `docs/decisions/scoring-protocol.md` section 5 is "
        "unchanged. No day after 2025-12-31 and no lockbox day is scored. Every figure is read from "
        "`docs/research/block-length-1022/result.json` by `scripts/block_length_1022.py report`.", "",
        "## Question for Eleonora", "",
        "**Marked question (section 13; the default applies if she has not answered by the next 5 pm batch).** Should the "
        "stationary bootstrap's mean block change from 10 business days, now that the post-2020 figures are recomputed? Options:", "",
        "1. Keep 10 and change nothing now; carry this page and #980's into the confirmation-design decision. **Default.**",
        "2. Move the block for the post-2020 confirmation tests only, to a value she names after reading the table below.",
        "3. Keep the bootstrap's block and take the dependence into the test instead (a fixed-b statistic, or calibration on "
        "contiguous windows), as Lens C proposes; this needs its own directive.", "",
        "## Method", "",
        "d_t = S(B) - S(`gbm_funding`) on the grid CRPS, lead-averaged, with B = B1 and with B = B2, on the "
        f"{record['decision_days']['n']} decision days {record['decision_days']['first']} to {record['decision_days']['last']} that #980 read "
        f"({record['gbm_funding_missing']['days']} missing forecasts, filled by B1), from the same walks. The proxy S(B1) - S(B2) is "
        "the difference of the two legs, the series Lens C's `bench_scores.csv` held (B1 and B2 grid CRPS per decision day). "
        f"Post-2020-04 is the decision days from {first}, as #886, #922 and #1014 read it. A day removed is dropped from the "
        "series (the series is then one day shorter, as #922 trims it). Three histories carry 2019-09-18 or not: the full one, "
        "the one without that decision day, and the one without that day and the "
        f"{len(record['window_days_dropped'])} decision days whose five targets include it. The post-2020-04 history holds none "
        "of them, so with and without is one row there. The ACF is the sample autocorrelation about the mean; the automatic "
        "block is Politis and White's with the correction of Patton, Politis and White (2009), as in #980, and again with the "
        "cap on the truncation lag widened from ceil(sqrt N) + K_N to N / 4; the long-run ratio is Lens C's "
        "1 + 2 sum (1 - k / (L + 1)) rho(k). A group under 120 days is not summarised, and a ratio at lag L needs 3 L days.", "",
        "Reproduction of #980: the Politis-White block of the pooled full history is "
        f"{f(rep['politis_white']['B1'], 1)} against B1 and {f(rep['politis_white']['B2'], 1)} against B2 over {rep['days']} days here, "
        f"and {f(rep['recorded_politis_white']['B1'], 1)} and {f(rep['recorded_politis_white']['B2'], 1)} over {rep['recorded_days']} days "
        "in #980's record (equal to 1e-9; the run stops otherwise).", "",
    ]
    for name in SERIES:
        s = record["series"][name]
        acf, blk = _rows(s["all"], list(HISTORIES))
        lines += [f"## {SERIES_TITLE[name]}", "", "### Autocorrelation", ""] + acf
        lines += ["", "### Block length and long-run ratio", ""] + blk
        regimes = [r for r in record["regimes"] if r in s["regime"]] + [k for k in s["regime"] if k.startswith("2018-19")]
        acf, blk = _rows(s["regime"], regimes)
        lines += ["", f"### Within regime (post-2020-04 days from {first}; 2018-19 shown with and without 2019-09-18)", ""] + acf
        lines += [""] + blk + [""]
    lines += lens_c_section(record)
    lines += reading(record)
    return "\n".join(lines)


def lens_c_section(record) -> List[str]:
    lc = LENS_C
    mine = {name: record["series"][name]["all"]["post-2020-04"] for name in SERIES}
    out = ["## Against Lens C's figures (#958)", "",
           "Lens C's figures are on a proxy built outside the repository, post-2020-04. The first row is what it reports; the "
           "others are this study's, on the same history.", "",
           "| series | days | " + " | ".join(f"rho({k})" for k in ACF_LAGS) + " | Politis-White | ratio lag 10 / 40 / 100 |",
           "|---|---|" + "---|" * len(ACF_LAGS) + "---|---|",
           "| Lens C (its proxy) | | " + " | ".join(f(lc["acf"][str(k)], 3) for k in ACF_LAGS)
           + f" | {f(lc['politis_white_post_2020'], 0)} | " + " / ".join(f(lc["lrv_ratio"][str(k)], 1) for k in LRV_LAGS) + " |"]
    for name in SERIES:
        e = mine[name]
        out.append(f"| this study, {SERIES_TITLE[name]} | {e['n']} | " + " | ".join(f(e["acf"][str(k)], 3) for k in ACF_LAGS)
                   + f" | {f(e['politis_white'], 1)} ({f(e['politis_white_wide'], 1)} widened) | "
                   + " / ".join(f(e["lrv_ratio"][str(k)], 1) for k in LRV_LAGS) + " |")
    e = record["series"]["proxy"]["regime"].get("2021-23")
    if e and not e.get("thin"):
        out += ["", f"Lens C's Politis-White block for 2021-23 is {f(LENS_C['politis_white_2021_23'], 0)} days; the proxy here gives "
                f"{f(e['politis_white'], 1)} ({f(e['politis_white_wide'], 1)} with the widened cap). #980's pooled figures were 4.8 "
                "against B1 and 73.2 against B2 on the full history.", ""]
    return out


def reading(record) -> List[str]:
    s = {name: record["series"][name] for name in SERIES}
    post = {name: s[name]["all"]["post-2020-04"] for name in SERIES}
    full = {name: s[name]["all"]["full"] for name in SERIES}
    wo = {name: s[name]["all"]["without 2019-09-18"] for name in SERIES}
    rg = {name: s[name]["regime"] for name in SERIES}
    return [
        "## Reading", "",
        "Development data; nothing here is a verdict and no constant moves.", "",
        f"1. **Without 2019-09-18, the B1 leg's block moves from {f(full['B1']['politis_white'], 1)} to {f(wo['B1']['politis_white'], 1)} "
        f"and the B2 leg's does not move ({f(full['B2']['politis_white'], 1)} to {f(wo['B2']['politis_white'], 1)}).** The day is one "
        f"observation in {full['B1']['n']}, but it is B1's one large loss, and it hides B1's dependence; dropping the "
        f"{len(record['window_days_dropped'])} decision days whose targets include it changes nothing further. Post-2020-04 holds none of them.",
        f"2. **Post-2020-04, the B1 leg's block is {f(post['B1']['politis_white'], 1)}, close to the protocol's {PROTOCOL_BLOCK}; the B2 leg's is "
        f"{f(post['B2']['politis_white'], 1)} ({f(post['B2']['politis_white_wide'], 1)} with the cap widened).** #980's pooled ~10 was an "
        "average over the two legs of a number that was 4.8 against B1 and 73.2 against B2 on the full history; it does not "
        "describe the B2 leg. The long-run ratio at lag 100 is "
        f"{f(post['B2']['lrv_ratio']['100'], 1)} for the B2 leg and {f(post['B1']['lrv_ratio']['100'], 1)} for the B1 leg: the lag-10 standard "
        f"error understates the lag-100 one by {f(post['B2']['se_understated_10_vs_100'], 1)}x for the B2 leg.",
        f"3. **By regime** the B2 leg's block is {f(rg['B2']['2020']['politis_white'], 1)} in 2020, {f(rg['B2']['2021-23']['politis_white'], 1)} in 2021-23 "
        f"({f(rg['B2']['2021-23']['politis_white_wide'], 1)} widened), {f(rg['B2']['2024']['politis_white'], 1)} in 2024 and "
        f"{f(rg['B2']['2025-26']['politis_white'], 1)} in 2025-26; the B1 leg's is {f(rg['B1']['2020']['politis_white'], 1)}, "
        f"{f(rg['B1']['2021-23']['politis_white'], 1)}, {f(rg['B1']['2024']['politis_white'], 1)} and {f(rg['B1']['2025-26']['politis_white'], 1)}. "
        "The slow dependence is a 2020 to 2023 feature (the B2 leg's rho(21) is "
        f"{f(rg['B2']['2021-23']['acf']['21'], 2)} in 2021-23 and {f(rg['B2']['2024']['acf']['21'], 2)} in 2024).",
        "4. **Lens C's figures.** Its autocorrelations are reproduced by the proxy S(B1) - S(B2) post-2020-04 "
        f"(rho(1) {f(post['proxy']['acf']['1'], 3)} against 0.726, rho(10) {f(post['proxy']['acf']['10'], 3)} against 0.278, "
        f"rho(42) {f(post['proxy']['acf']['42'], 3)} against 0.162) and its long-run ratios nearly so "
        f"({' / '.join(f(post['proxy']['lrv_ratio'][str(k)], 1) for k in LRV_LAGS)} against 4.9 / 11.9 / 19.3). Its Politis-White "
        f"block of 108 is not reproduced exactly: the proxy gives {f(post['proxy']['politis_white'], 1)} with the published cap on the "
        f"truncation lag and {f(post['proxy']['politis_white_wide'], 1)} with it widened to N / 4, so the figure of 108 lies in the same range and "
        "depends on that cap (and on the unseen proxy file); the order of magnitude, tens of days, is confirmed. The refutation "
        "is of #980's ~10 as a description of the series the protocol tests against B2, not of Lens C's number. Lens C's proxy is "
        "S(B1) - S(B2), which is not either leg; for the legs, the B1 leg is near 10 and the B2 leg near 65 to 90.",
        "5. **What stays open.** The Politis-White rule picks the block for the mean of a series; the protocol's interval is for "
        "the mean of a lead-averaged d_t, studentized, so the right block for the test is a question of coverage, which this page does "
        "not measure. #980 measured the interval at blocks 5, 10 and 20 and that is not repeated. The block choice is the marked "
        "question above and stays Eleonora's.", "",
    ]


# -- the commands -----------------------------------------------------------------------------------------------------


def report_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(record), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check(record_path: Path = RECORD, page_path: Path = PAGE) -> int:
    if not record_path.exists():
        print("no record yet: `run` and `report` have not been run", file=sys.stderr)
        return 1
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if not page_path.exists() or page_path.read_text(encoding="utf-8") != render(record):
        print("the page is not what the record gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--walks", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=lambda _a: check())
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
