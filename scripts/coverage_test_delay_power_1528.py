"""Size and power of amendment 4's coverage design under the publication delay, at spacing h and h + 1 (#1528, H5, step M5).

A development study, never a verdict. It is a check on the test, not a model change: forecasts stay unchanged, the candidate is not read, nothing
is registered or published. Her ruling of 9 November 2026 (docket answer "both" on next-h5-tails-1109, step 1; the ruling comment on #1528 narrows
it to the remaining gap): simulate correctly specified forecasts with the same delay, calendar effects and volatility clustering; measure the
false rejection and the detection power before the spacing rule changes. What earlier studies already measured is cited on the page, not rerun
(#1156: AR(1) data, no delay; #1516: the candidate's own PITs bootstrapped, no delay; #1525: a calibrated AR(1) forecaster with the D - 1 lag,
one regime, normal errors, size only).

The simulator is `repo_model.coverage_delay_sim` (its docstring is the model). This script holds the study around it:

- `calibrate` reads the development walk file (`candidate_calibration_1363.py walk`, 1855 decision days, targets to 2025-12-31) for its calendar,
  regimes, day types and outcomes only, fits the simulator, and writes `metadata/coverage_test_delay_power_1528.json`, the declaration, which
  is committed before any rate is computed. It reads no forecast of the candidate.
- `score` reads the committed declaration only (refused unless committed and unchanged), simulates `--paths` paths over the real decision
  days, regimes and calendar classes, and applies the design to each forecaster of the declaration under three rules: the amendment as set
  (Kupiec and independence at spacing h), independence at h + 1 with Kupiec as set (her ruling on #1525), and both at h + 1.
- `page` writes `docs/research/coverage-test-delay-power-1528-result.md` from the result file.

Commands (the walk takes about two minutes, the calibration seconds, the score minutes: below the `long-run` line):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/candidate_calibration_1363.py walk --panel PUB.csv --window development --output WALK/development.json
    PYTHONPATH=src python3 scripts/coverage_test_delay_power_1528.py calibrate --walk WALK/development.json
    git add metadata/coverage_test_delay_power_1528.json && git commit -m "#1528: declaration"
    PYTHONPATH=src python3 scripts/coverage_test_delay_power_1528.py score --output docs/research/coverage-test-delay-power-1528/result.json
    PYTHONPATH=src python3 scripts/coverage_test_delay_power_1528.py page
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing
import random
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import coverage_delay_sim as sim  # noqa: E402

ISSUE = 1528
SEED = 1528
PATHS = 1000
ALPHA = sim.ALPHA
LAST_DAY = date(2025, 12, 31)
DECLARATION = REPO / "metadata" / "coverage_test_delay_power_1528.json"
OUTPUT = REPO / "docs" / "research" / "coverage-test-delay-power-1528" / "result.json"
PAGE = REPO / "docs" / "research" / "coverage-test-delay-power-1528-result.md"
CODES = {"ordinary": "O", "quarter_end": "Q", "month_end": "M", "tax_date": "T", "settlement": "S", "policy": "P"}
CLASS_OF_CODE = {v: k for k, v in CODES.items()}
#: The central 90% band's coverage under a normal forecast whose standard deviation is cut by the factor, for the two coverages the directive names.
Z90 = 1.6448536269514722
SCALE_75 = 1.1503493803760083 / Z90  # a band that covers 75% where it should cover 90%
SCALE_50 = 0.6744897501960817 / Z90  # 50%

#: name -> (family, description, scale, classes it applies to or None for all, lag in days). `truth` first: it is the size world.
FORECASTERS: Dict[str, Tuple[str, str, float, Optional[Tuple[str, ...]], int]] = {
    "truth": ("size", "the true conditional distribution (correctly specified)", 1.0, None, 0),
    "a_qe75": ("a", "band too narrow on quarter-end days only: 90% band covers about 75%", SCALE_75, ("quarter_end",), 0),
    "a_qe50": ("a", "band too narrow on quarter-end days only: 90% band covers about 50%", SCALE_50, ("quarter_end",), 0),
    "a_cal75": ("a", "band too narrow on every calendar-class day (quarter-end, month-end, tax, settlement, policy): about 75%", SCALE_75,
                ("quarter_end", "month_end", "tax_date", "settlement", "policy"), 0),
    "b_85": ("b", "band too narrow on all days: standard deviation cut to 85%", 0.85, None, 0),
    "b_70": ("b", "band too narrow on all days: standard deviation cut to 70%", 0.70, None, 0),
    "c_lag5": ("c", "volatility state 5 days stale", 1.0, None, 5),
    "c_lag20": ("c", "volatility state 20 days stale", 1.0, None, 20),
}
RULE_TEXT = {
    "h": "amendment 4 as set: Kupiec and independence at spacing h",
    "indep_h1": "independence at spacing h + 1, Kupiec at h (her ruling on #1525)",
    "h1": "Kupiec and independence both at spacing h + 1",
}
P_NAMES = ("kupiec_h", "kupiec_h1", "indep_h", "indep_h1")
#: How the page names a rule.
RULE_SHORT = {"h": "h", "indep_h1": "indep h+1", "h1": "h+1"}




def key_label(key: Sequence) -> str:
    return f"{key[0]}|{key[1]}|{key[2]:g}"


# -- the declaration -----------------------------------------------------------------------------------------------------------


def series_from_walk(doc: Mapping[str, object]) -> dict:
    """The calendar to the window's last day, the class and regime of each day, the spread on each target day, and the decision days.

    Reads the walk file's calendar, regimes, target day types and outcomes only; no forecast. Refuses a day after 2025-12-31.

    Raises:
        ValueError: the file is not the development window.
        LookAheadError: a decision or target day is after the window's last day or in a locked tier.
    """

    if doc.get("window") != "development":
        raise ValueError(f"this study reads the 'development' window only, got {doc.get('window')!r}")
    calendar_all = [date.fromisoformat(d) for d in doc["calendar"]]  # type: ignore[union-attr]
    decisions = sorted(date.fromisoformat(d) for d in doc["regime_of_day"])  # type: ignore[union-attr]
    targets = {date.fromisoformat(d): v for d, v in doc["targets"].items()}  # type: ignore[union-attr]
    outcome = {date.fromisoformat(d): v for d, v in doc["outcome"].items()}  # type: ignore[union-attr]
    sim.require_development(list(decisions) + list(targets) + list(outcome), LAST_DAY, where="coverage_test_delay_power_1528.series_from_walk")
    calendar = [d for d in calendar_all if d <= LAST_DAY]
    position = {d: i for i, d in enumerate(calendar)}
    classes = [sim.day_class(targets[d]["types"]) if d in targets else "ordinary" for d in calendar]
    regime_of_target = [targets[d]["regime"] if d in targets else None for d in calendar]
    spread = [outcome.get(d) for d in calendar]
    regime_of_day = {date.fromisoformat(d): r for d, r in doc["regime_of_day"].items()}  # type: ignore[union-attr]
    return {
        "calendar": calendar, "classes": classes, "regime_of_target": regime_of_target, "spread": spread,
        "positions": [position[d] for d in decisions], "regimes": [regime_of_day[d] for d in decisions],
        "panel_sha256": doc.get("panel_sha256"),
    }


def build_declaration(doc: Mapping[str, object]) -> dict:
    """Fit the simulator to the walk file's spreads, day types and regimes and describe the study; nothing is scored."""

    s = series_from_walk(doc)
    cal = sim.fit_calibration(s["spread"], s["classes"], s["regime_of_target"])
    runs: List[List[object]] = []
    for r in s["regimes"]:
        if runs and runs[-1][0] == r:
            runs[-1][1] += 1  # type: ignore[operator]
        else:
            runs.append([r, 1])
    return {
        "issue": ISSUE,
        "label": "development, not a verdict; declared before any rate is computed",
        "hypothesis": "H5",
        "step": "M5",
        "window": "development",
        "last_day": LAST_DAY.isoformat(),
        "source": {"walk_panel_sha256": s["panel_sha256"], "decision_instant": "18:00", "reads": "calendar, regimes, target-day types and outcomes of the development walk file; no forecast"},
        "structure": {
            "calendar": [d.isoformat() for d in s["calendar"]],
            "class_codes": "".join(CODES[c] for c in s["classes"]),
            "first_decision_position": s["positions"][0],
            "decision_days": len(s["positions"]),
            "regime_runs": runs,
        },
        "calibration": cal.as_dict(),
        "calibration_method": "regime median of ordinary days removed; class scale = the mean-absolute-deviation sd of the class's days (about their median) over that of ordinary days; phi by least squares through the origin; two-state Markov scale mixture on the AR(1) residuals by Baum-Welch (150 iterations)",
        "model": "x[t] = phi x[t-1] + sigma[z[t]] e[t]; spread = level + scale[class] x; the forecaster reads x[D-1], z[D-1] and the class of its target day; PITs are PITs of x",
        "classes": list(sim.CLASSES),
        "forecasters": [
            {"name": n, "family": f, "description": d, "scale": sc, "on": None if on is None else list(on), "lag": lag}
            for n, (f, d, sc, on, lag) in FORECASTERS.items()
        ],
        "rules": {k: {"reads": list(v), "text": RULE_TEXT[k]} for k, v in sim.RULES.items()},
        "design": {"levels": list(sim.LEVELS), "leads": list(sim.LEADS), "family": "holm", "alpha": ALPHA, "rule": "strict hit (continuous PITs; no ties)"},
        "seed": SEED,
        "paths": PATHS,
    }


def structure_from_declaration(decl: Mapping[str, object]) -> Tuple[sim.Structure, sim.Calibration]:
    """The study's `Structure` and `Calibration` from a declaration; refuses a calendar day after the window's last day."""

    st = decl["structure"]
    calendar = [date.fromisoformat(d) for d in st["calendar"]]  # type: ignore[index]
    sim.require_development(calendar, date.fromisoformat(decl["last_day"]), where="coverage_test_delay_power_1528.structure")  # type: ignore[arg-type]
    classes = [CLASS_OF_CODE[c] for c in st["class_codes"]]  # type: ignore[index]
    first = st["first_decision_position"]  # type: ignore[index]
    positions: List[int] = []
    regimes: List[str] = []
    for name, count in st["regime_runs"]:  # type: ignore[index]
        regimes.extend([name] * count)
    positions = list(range(first, first + len(regimes)))
    return sim.Structure(calendar, classes, positions, regimes), sim.Calibration.from_dict(decl["calibration"])  # type: ignore[arg-type]


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any rate")
    return json.loads(path.read_text(encoding="utf-8"))


def forecasters_from_declaration(decl: Mapping[str, object]) -> Dict[str, sim.Forecaster]:
    return {
        f["name"]: sim.Forecaster(f["name"], f["scale"], None if f["on"] is None else frozenset(f["on"]), f["lag"])
        for f in decl["forecasters"]  # type: ignore[union-attr]
    }


# -- the simulation ------------------------------------------------------------------------------------------------------------

_STATE: dict = {}


def columns_for(cal: sim.Calibration, x, z, st: sim.Structure, fc: sim.Forecaster, truth: Mapping[int, List[float]]) -> Dict[int, List[float]]:
    """PITs of one forecaster; a scale confined to some classes changes only those target days of the true forecaster's PITs."""

    if fc.on is None or fc.lag:
        return sim.pit_columns(cal, x, z, st, fc)
    out = {}
    for h in sim.LEADS:
        col = list(truth[h])
        for i, p in enumerate(st.positions):
            if st.classes[p + h] in fc.on:
                col[i] = sim.pit(cal, x, z, p, h, st.classes[p + h], fc)
        out[h] = col
    return out


def one_path(path: int) -> dict:
    """One simulated path: for each forecaster and rule the Holm outcome, the raw rejections per cell and the tail frequencies of its PITs."""

    cal, st, fcs, seed = _STATE["cal"], _STATE["st"], _STATE["fcs"], _STATE["seed"]
    rng = random.Random(seed * 1_000_003 + path)
    x, z = sim.simulate_latent(cal, len(st.calendar), rng)
    truth = sim.pit_columns(cal, x, z, st, fcs["truth"])
    out: dict = {}
    for name, fc in fcs.items():
        u = truth if name == "truth" else columns_for(cal, x, z, st, fc, truth)
        table = sim.cell_p_values(st, u)
        rec: dict = {"rules": {}, "raw": {}, "band": [0, 0]}
        for key, row in table.items():
            rec["raw"][key_label(key)] = [int(row[p] < ALPHA) for p in P_NAMES]
        for rule in sim.RULES:
            ps, who = sim.family(table, rule)
            rej = sim.holm_rejected(ps, ALPHA)
            kinds = {who[i][1] for i in rej}
            raw_either = {}
            kp, ip = sim.RULES[rule]
            for key, row in table.items():
                raw_either[key_label(key)] = int(row[kp] < ALPHA or row[ip] < ALPHA)
            rec["rules"][rule] = {"min_p": min(ps), "rejected": len(rej), "kupiec": int("kupiec" in kinds), "independence": int("independence" in kinds), "either_raw": raw_either}
        affected = [(h, i) for h in sim.LEADS for i, p in enumerate(st.positions) if fc.on is None or st.classes[p + h] in fc.on]
        rec["band"] = [sum(1 for h, i in affected if 0.05 <= u[h][i] <= 0.95), len(affected)]
        if name == "truth":
            rec["calibration"] = {str(h): {f"{lv:g}": sum(1 for v in u[h] if (v > lv if lv > 0.5 else v < lv)) for lv in sim.LEVELS} for h in sim.LEADS}
        out[name] = rec
    return out


def wilson(hits: int, n: int, z: float = 1.959964) -> List[float]:
    """The Wilson score 95% interval of a rate."""

    if n == 0:
        return [0.0, 1.0]
    p = hits / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [max(0.0, centre - half), min(1.0, centre + half)]


def aggregate(results: Sequence[dict], st: sim.Structure, decl: Mapping[str, object]) -> dict:
    """Sum the paths into the figures the page quotes."""

    n = len(results)
    keys = sorted({k for k in results[0]["truth"]["raw"]}, key=lambda k: (int(k.split("|")[0]), k.split("|")[1], float(k.split("|")[2])))
    truth_min = {rule: sorted(r["truth"]["rules"][rule]["min_p"] for r in results) for rule in sim.RULES}
    # the 5th percentile of the smallest p under the true forecaster: the size-adjusted rejection threshold of each rule
    critical = {rule: truth_min[rule][max(0, int(math.floor(ALPHA * n)) - 1)] if int(math.floor(ALPHA * n)) >= 1 else 0.0 for rule in sim.RULES}
    out: dict = {"paths": n, "forecasters": {}, "size_adjusted_threshold": critical}
    for name in FORECASTERS:
        recs = [r[name] for r in results]
        block: dict = {"rules": {}, "cells": [], "band": [sum(r["band"][0] for r in recs), sum(r["band"][1] for r in recs)]}
        for rule in sim.RULES:
            fw = sum(1 for r in recs if r["rules"][rule]["rejected"] > 0)
            adj = sum(1 for r in recs if r["rules"][rule]["min_p"] <= critical[rule])
            kup = sum(r["rules"][rule]["kupiec"] for r in recs)
            ind = sum(r["rules"][rule]["independence"] for r in recs)
            block["rules"][rule] = {
                "family_wise": fw / n, "family_wise_interval": wilson(fw, n), "any_kupiec": kup / n, "any_independence": ind / n,
                "size_adjusted": adj / n, "size_adjusted_interval": wilson(adj, n), "mean_rejected": sum(r["rules"][rule]["rejected"] for r in recs) / n,
                "median_min_p": sorted(r["rules"][rule]["min_p"] for r in recs)[n // 2],
            }
        for k in keys:
            lead, regime, level = k.split("|")
            counts = [sum(r["raw"][k][j] for r in recs) for j in range(4)]
            cell = {"lead": int(lead), "regime": regime, "level": float(level), "raw": dict(zip(P_NAMES, [c / n for c in counts]))}
            cell["either"] = {rule: sum(r["rules"][rule]["either_raw"][k] for r in recs) / n for rule in sim.RULES}
            block["cells"].append(cell)
        out["forecasters"][name] = block
    cal = {str(h): {lv: sum(r["truth"]["calibration"][str(h)][lv] for r in results) / (n * len(st.positions)) for lv in results[0]["truth"]["calibration"][str(h)]} for h in sim.LEADS}
    out["truth_tail_frequency"] = cal
    return out


def score_command(args) -> int:
    decl = committed_declaration()
    st, cal = structure_from_declaration(decl)
    fcs = forecasters_from_declaration(decl)
    paths = int(args.paths or decl["paths"])
    _STATE.update(cal=cal, st=st, fcs=fcs, seed=int(decl["seed"]))
    if args.workers > 1:
        with multiprocessing.get_context("fork").Pool(args.workers) as pool:
            results = []
            for i, r in enumerate(pool.imap(one_path, range(paths), chunksize=2), start=1):
                results.append(r)
                if i % 50 == 0:
                    print(f"{i}/{paths} paths", flush=True)
    else:
        results = [one_path(p) for p in range(paths)]
    agg = aggregate(results, st, decl)
    regimes = sorted(set(st.regimes))
    result = {
        "issue": ISSUE, "label": "development, not a verdict", "hypothesis": "H5", "step": "M5", "window": "development", "last_day": decl["last_day"],
        "seed": decl["seed"], "alpha": ALPHA, "paths": paths, "decision_days": len(st.positions), "regimes": regimes,
        "regime_days": {r: sum(1 for x in st.regimes if x == r) for r in regimes},
        "calibration": decl["calibration"], "calibration_source": decl["source"],
        "forecasters": decl["forecasters"], "rules": decl["rules"],
        "class_days": {c: sum(1 for p in st.positions for h in sim.LEADS if st.classes[p + h] == c) for c in sim.CLASSES},
        "decision_target_pairs": len(st.positions) * len(sim.LEADS),
        "results": agg,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


def calibrate_command(args) -> int:
    doc = json.loads(Path(args.walk).read_text(encoding="utf-8"))
    decl = build_declaration(doc)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(decl, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out}: {json.dumps(decl['calibration'])}")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------------


def _pc(x: float, d: int = 1) -> str:
    return f"{100 * x:.{d}f}%"


def _iv(x: Sequence[float]) -> str:
    return f"[{100 * x[0]:.1f}%, {100 * x[1]:.1f}%]"


def pooled(cells: Sequence[Mapping[str, object]], select, value) -> float:
    chosen = [c for c in cells if select(c)]
    return sum(value(c) for c in chosen) / len(chosen)


def render(r: Mapping[str, object]) -> str:
    res = r["results"]
    n = res["paths"]
    fcs = res["forecasters"]
    truth = fcs["truth"]
    rules = list(sim.RULES)
    cal = r["calibration"]
    out: List[str] = []
    w = out.append
    w("# Size and power of the amendment 4 coverage design under the publication delay, at spacing h and h + 1 (#1528)")
    w("")
    w("**Hypothesis and step:** H5, step M5 (registration). **Development data, not a verdict.** Generated by `scripts/coverage_test_delay_power_1528.py page` from "
      "`docs/research/coverage-test-delay-power-1528/result.json`, not edited by hand. This is a check on the test: forecasts, the candidate, the protocol "
      "and the spacing rule are unchanged, and nothing is registered or published. It feeds #1527 (the spacing amendment). Her ruling of 9 November 2026 "
      "(docket \"both\", then the narrowing on #1528): simulate correct forecasts with the same delay, calendar effects and volatility clustering; measure "
      "false rejection and detection power before the spacing rule changes.")
    w("")
    w("## What was measured")
    w("")
    w(f"The design of amendment 4 (Kupiec and Christoffersen independence at q05/q95 and q01/q99, leads 1 to 5, each regime, Holm over its whole family of tests at 5%) "
      f"was applied to {n} simulated paths over the real development calendar: {r['decision_days']} decision days, targets to {r['last_day']}, the regimes "
      f"({', '.join(f'{k} {v}' for k, v in r['regime_days'].items())} days) and the class of every target day as the real report has them. A decision "
      f"on day D reads the last published spread, that of D - 1, so lead h looks h + 1 days ahead of its last value (the one-day publication delay). The "
      f"data are a latent AR(1) with a two-state Markov volatility (clustering) and a scale by calendar class (quarter-end, month-end, tax date, settlement, "
      f"policy day), fitted to the development spreads and declared in `metadata/coverage_test_delay_power_1528.json` before any rate was computed: "
      f"phi {cal['phi']:.3f}; innovation scale {cal['sigma'][0]:.2f} calm and {cal['sigma'][1]:.2f} stress, staying {cal['stay'][0]:.3f} and "
      f"{cal['stay'][1]:.3f}; class scales "
      + ", ".join(f"{k} {v:.2f}" for k, v in cal["scale"].items() if k != "ordinary") + " (ordinary 1). "
      "The true forecaster knows the latent value and the volatility state at D - 1 and the class of its target day, and its distribution is the exact "
      "mixture over the volatility paths it cannot see. Three rules are read on the same paths: **h** (the amendment as set: Kupiec and independence on every "
      "h-th decision day), **indep h+1** (independence on every (h+1)-th day, Kupiec as set: her ruling on #1525) and **h+1** (both on every (h+1)-th day).")
    w("")
    w("Why spacing matters here, exactly. With the delay, the forecast made on D + h for target D + 2h has not seen the innovation of D + h, and neither "
      "has the forecast of D + h seen it: their PITs share it, so hits h apart are dependent for a correct forecaster. The target of the forecast made on D is "
      "public when the forecast of D + h + 1 is made, so hits h + 1 apart are independent whatever the data (a martingale argument; the simulation shows "
      "it at finite sample). Volatility clustering and calendar effects do not change that; they change power.")
    w("")
    w("**Already measured, not rerun:** #1156 (AR(1) data, no delay: the design near its size), #1516 (the candidate's own PITs bootstrapped, no delay) and "
      "#1525 (a calibrated AR(1) forecaster with the D - 1 lag, one regime, normal errors: independence at spacing h rejects 83% to 100% of paths, at h + 1 "
      "4% to 8%; size only). This study adds volatility clustering and calendar effects to the delay, and measures power at h + 1, which none measured.")
    w("")
    w("## Size: how often the design rejects a correctly specified forecaster")
    w("")
    w(f"Family-wise: the share of {n} paths with at least one Holm rejection across the whole family of tests (nominal 5.0%), Wilson 95% interval.")
    w("")
    w("| Rule | family-wise rejection | of which a Kupiec test | of which an independence test | mean tests rejected |")
    w("|---|---|---|---|---|")
    for rule in rules:
        b = truth["rules"][rule]
        w(f"| {r['rules'][rule]['text']} | {_pc(b['family_wise'])} {_iv(b['family_wise_interval'])} | {_pc(b['any_kupiec'])} | {_pc(b['any_independence'])} | {b['mean_rejected']:.3f} |")
    w("")
    w("Per test, before Holm: the share of (path, regime) cells whose raw p-value is below 5% (nominal 5.0%), pooled over the five regimes, by lead and level. "
      "Combined is a cell in which either test is below 5%, under the rule's own pair of tests.")
    w("")
    w("| Lead | Level | Kupiec at h | Kupiec at h+1 | independence at h | independence at h+1 | combined, rule h | combined, indep h+1 | combined, rule h+1 |")
    w("|---|---|---|---|---|---|---|---|---|")
    for h in sim.LEADS:
        for lv in sim.LEVELS:
            cs = [c for c in truth["cells"] if c["lead"] == h and c["level"] == lv]
            m = lambda f: sum(f(c) for c in cs) / len(cs)
            w(f"| {h} | q{lv:g} | " + " | ".join(_pc(m(lambda c, k=k: c["raw"][k])) for k in P_NAMES[0:2] + P_NAMES[2:4]) + " | "
              + " | ".join(_pc(m(lambda c, k=k: c["either"][k])) for k in rules) + " |")
    w("")
    w("Pooled over the 20 lead-and-level cells of a regime (the regime split of the report; the cells of one path are dependent, so the interval is Wilson on "
      f"{n * 20} cell draws and is a little narrow):")
    w("")
    w("| Regime | days | " + " | ".join(f"combined, rule {RULE_SHORT[k]}" for k in rules) + " |")
    w("|---|---|" + "---|" * len(rules))
    for reg in r["regimes"]:
        cs = [c for c in truth["cells"] if c["regime"] == reg]
        cells_cols = []
        for rule in rules:
            rate = sum(c["either"][rule] for c in cs) / len(cs)
            cells_cols.append(f"{_pc(rate)} {_iv(wilson(round(rate * n * len(cs)), n * len(cs)))}")
        w(f"| {reg} | {r['regime_days'][reg]} | " + " | ".join(cells_cols) + " |")
    w("")
    w("Check that the simulated forecaster is correct: the share of its PITs beyond each level, by lead, against nominal "
      "(mean over paths): " + "; ".join(f"lead {h}: " + ", ".join(f"q{lv}: {_pc(v, 2)}" for lv, v in sorted(res['truth_tail_frequency'][str(h)].items(), key=lambda kv: float(kv[0]))) for h in sim.LEADS) + ".")
    w("")
    w("## Power: how often it rejects a misspecified forecaster")
    w("")
    w("Detection is the family-wise rejection rate (Holm at 5%). Because a rule that over-rejects a correct forecaster also detects more, the size-adjusted rate "
      "is beside it: the share of paths whose smallest p-value is at most the 5th percentile of that rule's smallest p-value under the true forecaster "
      "(thresholds in `result.json`). Band coverage is the share of the forecaster's own PITs inside [0.05, 0.95] on the target days it is misspecified on, "
      "so a correct band reads 90%.")
    w("")
    w("| Forecaster | 90% band covers | Rule | detection (Holm) | size-adjusted | of which Kupiec | of which independence |")
    w("|---|---|---|---|---|---|---|")
    for name, (fam, desc, *_rest) in FORECASTERS.items():
        b = fcs[name]
        for rule in rules:
            x = b["rules"][rule]
            cover = _pc(b["band"][0] / b["band"][1]) if b["band"][1] else "n/a"
            w(f"| {desc} | {cover} | {RULE_SHORT[rule]} | {_pc(x['family_wise'])} {_iv(x['family_wise_interval'])} | {_pc(x['size_adjusted'])} {_iv(x['size_adjusted_interval'])} | {_pc(x['any_kupiec'])} | {_pc(x['any_independence'])} |")
    w("")
    w(f"Target days by class in the {r['decision_target_pairs']} (decision, lead) pairs: " + ", ".join(f"{k} {v}" for k, v in r["class_days"].items()) + ".")
    w("")
    w("Raw detection per level (the share of (path, regime, lead) cells with a raw p below 5% under the rule's pair of tests, pooled over leads and regimes):")
    w("")
    w("| Forecaster | Level | " + " | ".join(f"rule {RULE_SHORT[k]}" for k in rules) + " |")
    w("|---|---|" + "---|" * len(rules))
    for name in FORECASTERS:
        for lv in sim.LEVELS:
            cs = [c for c in fcs[name]["cells"] if c["level"] == lv]
            w(f"| {name} | q{lv:g} | " + " | ".join(_pc(sum(c["either"][k] for c in cs) / len(cs)) for k in rules) + " |")
    w("")
    w("Raw detection by regime (the share of (path, lead, level) cells with a raw p below 5% under the rule's pair of tests, pooled over the 20 lead-and-level cells of the "
      "regime): the regime split of the report. The day-type split of the report is the class of the target day, whose counts are above; a fault confined to a class "
      "can only be seen in the cells that hold its days.")
    w("")
    w("| Forecaster | Rule | " + " | ".join(r["regimes"]) + " |")
    w("|---|---|" + "---|" * len(r["regimes"]))
    for name in FORECASTERS:
        for rule in rules:
            cols = []
            for reg in r["regimes"]:
                cs = [c for c in fcs[name]["cells"] if c["regime"] == reg]
                cols.append(_pc(sum(c["either"][rule] for c in cs) / len(cs)))
            w(f"| {name} | {RULE_SHORT[rule]} | " + " | ".join(cols) + " |")
    w("")
    w("## Read-out")
    w("")
    read = readout(r)
    out.extend(read)
    w("")
    w("## What this does and does not show")
    w("")
    w("- It is a simulation of a model fitted to the development spreads, not the candidate: the volatility state is taken as public (a stand-in for the "
      "volatility information a real forecaster has), the level and the class means are removed by a correct forecaster and do not enter, and there are two "
      "volatility states. A real forecaster's errors are not this model's.")
    w("- The misspecified forecasters are the three of the directive (band too narrow on calendar days, narrow overall, a stale volatility state); the "
      "narrowing factors and lags are the declaration's, none tuned after a score.")
    w("- Quarter-end target days are few in the report (see the class counts above), so power against a quarter-end-only fault is limited by how many such days a "
      "regime holds, at any spacing; #1531 is the arm that studies that day type.")
    w("- It changes no rule and registers nothing. Whether to read independence at spacing h + 1 is hers (#1527); this page says what the rule would give.")
    w("- Development data, not a verdict: no locked day, nothing after 2025-12-31.")
    return "\n".join(out) + "\n"


def readout(r: Mapping[str, object]) -> List[str]:
    """The plain-language reading, from the figures. Two conventions are this page's own, not the protocol's: size is "above nominal" when the Wilson
    interval of the family-wise rate lies above 5%, and a fault is "detected" when its size-adjusted detection is at least 80%."""

    fcs = r["results"]["forecasters"]
    truth = fcs["truth"]["rules"]
    short = RULE_SHORT
    lines: List[str] = []
    above = {rule: truth[rule]["family_wise_interval"][0] > ALPHA for rule in sim.RULES}
    for rule in sim.RULES:
        t = truth[rule]
        where = "above nominal" if above[rule] else ("below nominal" if t["family_wise_interval"][1] < ALPHA else "at nominal")
        lines.append(
            f"- **Size, rule {short[rule]} ({r['rules'][rule]['text']}):** a correct forecaster is rejected in {_pc(t['family_wise'])} {_iv(t['family_wise_interval'])} "
            f"of paths, {where} (independence {_pc(t['any_independence'])}, Kupiec {_pc(t['any_kupiec'])})."
        )
    lines.append("")
    for rule in sim.RULES:
        det = {n: fcs[n]["rules"][rule] for n in FORECASTERS if n != "truth"}
        bits = ", ".join(f"{n} {_pc(d['family_wise'], 0)} ({_pc(d['size_adjusted'], 0)})" for n, d in det.items())
        lines.append(f"- **Detection, rule {short[rule]}** (Holm, size-adjusted in brackets): {bits}.")
    lines.append("")
    adj = lambda rule, n: fcs[n]["rules"][rule]["size_adjusted"]
    a_all = [n for n, v in FORECASTERS.items() if v[0] == "a"]
    a_qe = [n for n in a_all if FORECASTERS[n][3] == ("quarter_end",)]
    for rule in sim.RULES:
        lines.append(
            f"- **Fault (a), rule {short[rule]}**, size-adjusted: " + ", ".join(f"{n} {_pc(adj(rule, n), 0)}" for n in a_all)
            + f"; {'detected in all variants' if all(adj(rule, n) >= 0.80 for n in a_all) else 'not detected in all variants'} (at least 80%)."
        )
    lines.append("")
    lines.append("**Plainly.**")
    lines.append("")
    for rule in ("indep_h1", "h1"):
        t = truth[rule]
        lines.append(
            f"- Spacing h + 1, rule {short[rule]}: size is {'above nominal at ' + _pc(t['family_wise']) if above[rule] else 'kept (' + _pc(t['family_wise']) + ', not above 5%)'}"
            + (f"; the excess is Kupiec's at spacing h ({_pc(t['any_kupiec'])}), independence adds {_pc(t['any_independence'])}" if above[rule] and rule == "indep_h1" else "")
            + f". It detects (a) restricted to calendar-class days at {_pc(adj(rule, 'a_cal75'), 0)}, and (a) restricted to quarter-end days at "
            + " and ".join(_pc(adj(rule, n), 0) for n in a_qe) + "; narrow overall at " + " and ".join(_pc(adj(rule, n), 0) for n in ("b_85", "b_70"))
            + "; a stale volatility state at " + " and ".join(_pc(adj(rule, n), 0) for n in ("c_lag5", "c_lag20")) + "."
        )
    lines.append(
        f"- Spacing h (the amendment as set) rejects a correct forecaster in {_pc(truth['h']['family_wise'], 0)} of paths, so its detection of any fault is not "
        f"informative; size-adjusted, its power against (a) restricted to quarter-end days is {' and '.join(_pc(adj('h', n), 0) for n in a_qe)}."
    )
    ok = [rule for rule in ("indep_h1", "h1") if not above[rule] and all(adj(rule, n) >= 0.80 for n in a_all)]
    if ok:
        lines.append(f"- Rule(s) {', '.join(short[x] for x in ok)} keep size and detect every variant of (a).")
    else:
        lines.append(
            "- **No spacing both keeps size and detects every variant of (a).** Independence at spacing h + 1 with Kupiec at h is above nominal because of Kupiec at "
            "spacing h; both at h + 1 keep size, below nominal, and detect (a) on calendar-class days at less than the other. A fault confined to quarter-end "
            "days is not detected at any spacing, the current one included: the report holds too few such days (see the class counts). Detection of an overall "
            "narrowing and of a stale volatility state is in the rows above. The rule is not tuned here; #1527 and her own ruling decide."
        )
    return lines


def page_command(args) -> int:
    r = json.loads(Path(args.result).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(r), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("calibrate", help="fit the simulator to the development walk file and write the declaration")
    c.add_argument("--walk", required=True)
    c.add_argument("--output", default=str(DECLARATION))
    c.set_defaults(func=calibrate_command)
    s = sub.add_parser("score", help="simulate and apply the design (needs the committed declaration)")
    s.add_argument("--output", default=str(OUTPUT))
    s.add_argument("--paths", type=int, default=0)
    s.add_argument("--workers", type=int, default=4)
    s.set_defaults(func=score_command)
    p = sub.add_parser("page", help="write the result page from the result file")
    p.add_argument("--result", default=str(OUTPUT))
    p.add_argument("--output", default=str(PAGE))
    p.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
