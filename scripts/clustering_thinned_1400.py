"""Do the candidate's misses cluster at leads 2 to 5 on thinned days, and how often does the unthinned test reject a calibrated forecaster (#1400, H5).

A development study, never a verdict. #1378 (`scripts/candidate_calibration_1363.py`) read clustering with an unthinned permutation test whose
null keeps no overlap between consecutive h-step forecasts, so a calibrated forecaster is rejected too often (#998). This study, declared in
`metadata/clustering_thinned_1400.json` before any figure (`sim`, `score` and `page` refuse unless it is committed and unchanged):

1. `sim` measures, in the two-regime AR(1) world of #961/#998 with the forecaster calibrated by construction, how often #1363's unthinned
   permutation test and the thinned reading reject, at h = 1 to 5 and at the sample sizes of the two windows;
2. `score` re-reads the candidate and B1, B1', B2 from walk files of `scripts/candidate_calibration_1363.py walk` (unchanged): at lead 1 the
   unthinned permutation p of #1363 (reproduced to the digit), at leads 2 to 5 Christoffersen's independence test on every phase of the
   thinned series, by lead and (development window) by regime;
3. `page` writes the result page. Nothing is adopted; B4 (#1360) is not compared.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/candidate_calibration_1363.py walk --panel PUB.csv --window development --output WALK/development.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/candidate_calibration_1363.py walk --panel PUB.csv --window 2026 --output WALK/2026.json
    OUT=docs/research/clustering-thinned-1400
    PYTHONPATH=src python3 scripts/clustering_thinned_1400.py sim --output $OUT/sim.json --workers 4
    PYTHONPATH=src python3 scripts/clustering_thinned_1400.py score --walks WALK --sim $OUT/sim.json --output $OUT/result.json --workers 4
    PYTHONPATH=src python3 scripts/clustering_thinned_1400.py page --score $OUT/result.json --output docs/research/clustering-thinned-1400-result.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import coverage_tests, scoring_protocol as sp  # noqa: E402


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


m63 = _load("candidate_calibration_1363", "candidate_calibration_1363_in_1400")
gate = _load("coverage_gate_961", "coverage_gate_961_in_1400")

DECLARATION = REPO / "metadata" / "clustering_thinned_1400.json"
RECORD_1363 = REPO / "docs" / "research" / "candidate-calibration-1363" / "result.json"
SEED = 1400
LEAD1_SEED = m63.SEED
PERMUTATIONS = 10_000
LEADS = tuple(sp.HORIZONS)
THIN_LEADS = tuple(h for h in LEADS if h >= 2)
PHASES_2_TO_5 = sum(THIN_LEADS)
WINDOWS = m63.WINDOWS
CANDIDATE = m63.CANDIDATE
REFERENCES = m63.REFERENCES
MODELS = m63.MODELS
LABELS = m63.LABELS
SEQUENCES = m63.SEQUENCES
ALPHA = sp.ALPHA
MIN_SERIES = 20
# the simulation
PATHS = 500
SIM_SEED = 1400
SIM_PERMUTATIONS = 1999
SAMPLE_SIZES = (1855, 165)
SIM_EVENTS = ("upper", "lower", "band90", "band50")
THINNED_FAMILY_SIM = len(SIM_EVENTS) + len(SIM_EVENTS) * PHASES_2_TO_5
UNTHINNED_FAMILY_SIM = len(SIM_EVENTS) * len(LEADS)


def committed_declaration() -> dict:
    return m63.committed_declaration(DECLARATION)


# -- thinning by phase ---------------------------------------------------------------------------------------------------------


def phase_indices(n: int, h: int, r: int) -> List[int]:
    """Indices of a lead's decision-day list kept by phase `r` of the every-h-th-day reading: those with `i mod h == r`."""

    return list(range(r, n, h))


def thinned_runs(positions: Sequence[int], h: int, breaks: Optional[Sequence[object]] = None) -> List[int]:
    """Run lengths of a thinned series: kept values are adjacent only when their panel positions differ by exactly `h` (and share a break label)."""

    out, length = [], 0
    for i, p in enumerate(positions):
        if i and (p != positions[i - 1] + h or (breaks is not None and breaks[i] != breaks[i - 1])):
            out.append(length)
            length = 0
        length += 1
    if length:
        out.append(length)
    return out


def phase_series(positions: Sequence[int], values: Sequence[int], h: int, r: int, breaks: Optional[Sequence[object]] = None) -> Tuple[List[int], List[int]]:
    """The thinned series of phase `r`: its values and its runs."""

    idx = phase_indices(len(values), h, r)
    return [values[i] for i in idx], thinned_runs([positions[i] for i in idx], h, None if breaks is None else [breaks[i] for i in idx])


def regime_phase_series(positions: Sequence[int], values: Sequence[int], regimes: Sequence[str], h: int, r: int, regime: str) -> Tuple[List[int], List[int]]:
    """Phase `r` of the lead's thinned series, kept inside one regime of the decision day (the thinning is by the lead's order, as the protocol's)."""

    idx = [i for i in phase_indices(len(values), h, r) if regimes[i] == regime]
    return [values[i] for i in idx], thinned_runs([positions[i] for i in idx], h)


def lr_statistic(values: Sequence[int], runs: Sequence[int]) -> float:
    return m63.lr_independence(*m63.transition_counts(values, runs))


def asymptotic_p(values: Sequence[int], runs: Sequence[int]) -> float:
    """Christoffersen's independence test (the protocol's: chi-square 1 df) from transition counts summed over runs."""

    return coverage_tests.chi2_sf(lr_statistic(values, runs), 1)


# -- the size simulation -------------------------------------------------------------------------------------------------------


def miss_sequences(days: int, seed: int) -> Dict[int, Dict[str, List[int]]]:
    """Per lead, the four 0/1 miss sequences (strict rule) of the calibrated forecaster on one simulated path of `days` decision days."""

    y = gate.simulate(days, seed)
    sigma = gate.sigma_schedule(len(y))
    z = gate.Z
    out: Dict[int, Dict[str, List[int]]] = {}
    for h in LEADS:
        seqs = {ev: [] for ev in SIM_EVENTS}
        for t in range(days):
            mean, sd = gate.ideal(y[t], t, h, sigma)
            lo, q25, q75, hi = (mean + sd * z[p] for p in (0.05, 0.25, 0.75, 0.95))
            out_t = y[t + h]
            seqs["upper"].append(int(out_t > hi))
            seqs["lower"].append(int(out_t < lo))
            seqs["band90"].append(int(out_t < lo or out_t > hi))
            seqs["band50"].append(int(out_t < q25 or out_t > q75))
        out[h] = seqs
    return out


def simulate_path(days: int, seed: int, permutations: int) -> dict:
    """The p-values of one path: the unthinned permutation p per lead and event, and the asymptotic p of every phase series."""

    seqs = miss_sequences(days, seed)
    unthinned: Dict[str, Dict[str, float]] = {}
    phases: Dict[str, Dict[str, List[float]]] = {}
    positions = list(range(days))
    for h in LEADS:
        unthinned[str(h)], phases[str(h)] = {}, {}
        for ev in SIM_EVENTS:
            seq = seqs[h][ev]
            unthinned[str(h)][ev] = m63.permutation_p(seq, [days], permutations=permutations, seed=SIM_SEED)
            phases[str(h)][ev] = [asymptotic_p(*phase_series(positions, seq, h, r)) for r in range(h)]
    return {"unthinned": unthinned, "phases": phases}


def _path_task(job):
    days, seed, permutations = job
    return simulate_path(days, seed, permutations)


def _flagged(family: Mapping[str, float]) -> Dict[str, bool]:
    return sp.holm(dict(family), ALPHA)


def size_rates(paths: Sequence[dict]) -> dict:
    """Rejection shares over simulated paths: per lead and event at 0.05 (unthinned, phase 0, any phase, mean over phases), and family-wise by Holm."""

    n = len(paths)
    by: Dict[str, Dict[str, dict]] = {}
    for h in LEADS:
        by[str(h)] = {}
        for ev in SIM_EVENTS:
            un = sum(p["unthinned"][str(h)][ev] < ALPHA for p in paths) / n
            ph0 = sum(p["phases"][str(h)][ev][0] < ALPHA for p in paths) / n
            anyp = sum(any(x < ALPHA for x in p["phases"][str(h)][ev]) for p in paths) / n
            mean = sum(sum(x < ALPHA for x in p["phases"][str(h)][ev]) / h for p in paths) / n
            by[str(h)][ev] = {"unthinned": un, "phase0": ph0, "any_phase": anyp, "mean_phase": mean}
    fam = {k: 0 for k in ("unthinned_all", "thinned_all", "unthinned_2_to_5", "thinned_2_to_5")}
    lead_un = {str(h): 0 for h in LEADS}
    lead_th = {str(h): 0 for h in LEADS}
    for p in paths:
        un_all = {f"{h}/{ev}": p["unthinned"][str(h)][ev] for h in LEADS for ev in SIM_EVENTS}
        th_all = {f"1/{ev}": p["unthinned"]["1"][ev] for ev in SIM_EVENTS}
        th_all.update({f"{h}/{ev}/{r}": x for h in THIN_LEADS for ev in SIM_EVENTS for r, x in enumerate(p["phases"][str(h)][ev])})
        un_25 = {k: v for k, v in un_all.items() if not k.startswith("1/")}
        th_25 = {k: v for k, v in th_all.items() if not k.startswith("1/")}
        fu, ft, fu25, ft25 = _flagged(un_all), _flagged(th_all), _flagged(un_25), _flagged(th_25)
        fam["unthinned_all"] += any(fu.values())
        fam["thinned_all"] += any(ft.values())
        fam["unthinned_2_to_5"] += any(fu25.values())
        fam["thinned_2_to_5"] += any(ft25.values())
        for h in LEADS:
            lead_un[str(h)] += any(v for k, v in fu.items() if k.startswith(f"{h}/"))
            lead_th[str(h)] += any(v for k, v in ft.items() if k.startswith(f"{h}/"))
    return {"paths": n, "by_lead_event": by, "family": {k: v / n for k, v in fam.items()},
            "family_by_lead": {"unthinned": {k: v / n for k, v in lead_un.items()}, "thinned": {k: v / n for k, v in lead_th.items()}}}


def size_study(days: int, *, paths: int = PATHS, permutations: int = SIM_PERMUTATIONS, workers: int = 1) -> dict:
    jobs = [(days, SIM_SEED + 1 + i, permutations) for i in range(paths)]
    if workers > 1:
        with Pool(workers) as pool:
            found = pool.map(_path_task, jobs, chunksize=5)
    else:
        found = [_path_task(j) for j in jobs]
    out = size_rates(found)
    out.update({"days": days, "permutations": permutations})
    return out


def sim_command(args) -> int:
    declared = committed_declaration()
    result = {"issue": 1400, "declaration": "metadata/clustering_thinned_1400.json", "label": "development, a simulation; not a verdict",
              "world": declared["simulation"]["world"], "seed": SIM_SEED, "paths": PATHS, "sizes": {}}
    for days in SAMPLE_SIZES:
        result["sizes"][str(days)] = size_study(days, workers=args.workers)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the real windows ----------------------------------------------------------------------------------------------------------


def _series_task(job):
    key, values, runs, permutations, seed = job
    rep = m63.sequence_report(values, runs, permutations=permutations, seed=seed)
    rep["p_asymptotic"] = asymptotic_p(values, runs)
    return key, rep


def _row(key, rep):
    lead, phase, name, regime = key
    return {"lead": lead, "phase": phase, "sequence": name, "regime": regime, "n": rep["n"], "misses": rep["misses"], "transitions": rep["transitions"],
            "p_asymptotic": rep["p_asymptotic"], "p_permutation": rep["p_permutation"], "read": rep["n"] >= MIN_SERIES}


def _clusters(rows: Sequence[dict]) -> Tuple[Dict[str, Dict[str, bool]], int]:
    """Holm over the read phase series (asymptotic p); a (lead, sequence) clusters when any of its phases is flagged. Returns the flags and the count not read."""

    family = {f"{r['lead']}/{r['phase']}/{r['sequence']}": r["p_asymptotic"] for r in rows if r["read"]}
    flags = sp.holm(family, ALPHA) if family else {}
    clusters: Dict[str, Dict[str, bool]] = {str(h): {name: False for name in SEQUENCES} for h in THIN_LEADS}
    for r in rows:
        key = f"{r['lead']}/{r['phase']}/{r['sequence']}"
        r["holm_clusters"] = bool(flags.get(key, False))
        if r["holm_clusters"]:
            clusters[str(r["lead"])][r["sequence"]] = True
    return clusters, sum(not r["read"] for r in rows)


def thinned_clustering(window: "m63.Window", model: str, *, permutations: int = PERMUTATIONS, workers: int = 1, regimes: bool = True) -> dict:
    jobs = []
    for lead in LEADS:
        positions, seqs, regime_labels = m63.lead_sequences(window, model, lead)
        if lead == 1:
            runs = m63.runs_of(positions)
            for name, seq in seqs.items():
                jobs.append(((1, 0, name, None), seq, runs, permutations, LEAD1_SEED))
            continue
        for r in range(lead):
            for name, seq in seqs.items():
                values, runs = phase_series(positions, seq, lead, r)
                jobs.append(((lead, r, name, None), values, runs, permutations, SEED))
                if regimes:
                    for reg in sorted(set(regime_labels)):
                        sub, sub_runs = regime_phase_series(positions, seq, regime_labels, lead, r, reg)
                        if sub:
                            jobs.append(((lead, r, name, reg), sub, sub_runs, permutations, SEED))
    if workers > 1:
        with Pool(workers) as pool:
            found = pool.map(_series_task, jobs, chunksize=8)
    else:
        found = [_series_task(j) for j in jobs]
    lead1 = {key[2]: rep for key, rep in found if key[0] == 1}
    flags = sp.holm({name: rep["p_permutation"] for name, rep in lead1.items()}, ALPHA)
    for name, rep in lead1.items():
        rep["holm_clusters"] = flags[name]
    rows = [_row(key, rep) for key, rep in found if key[0] > 1 and key[3] is None]
    clusters, unread = _clusters(rows)
    out = {"lead1": lead1, "phases": rows, "clusters": clusters, "unread": unread, "regime": {}}
    for reg in sorted({key[3] for key, _rep in found if key[3] is not None}):
        reg_rows = [_row(key, rep) for key, rep in found if key[3] == reg]
        reg_clusters, reg_unread = _clusters(reg_rows)
        out["regime"][reg] = {"phases": reg_rows, "clusters": reg_clusters, "unread": reg_unread}
    return out


def window_report(window: "m63.Window", *, permutations: int = PERMUTATIONS, workers: int = 1) -> dict:
    m63.refuse_beyond(sorted({t for _d, _h, t in window.cells} | set(window.days)), m63.WINDOW_LAST[window.name], where="clustering_thinned_1400")
    out = {"window": window.name, "decision_days": len(window.days), "cells": len(window.cells), "first_decision": window.days[0].isoformat(),
           "last_decision": window.days[-1].isoformat(), "last_target": window.last_day().isoformat(), "models": {}}
    for model in MODELS:
        out["models"][model] = thinned_clustering(window, model, permutations=permutations, workers=workers, regimes=window.name == "development")
    return out


def lead1_reproduction(window_name: str, rep: dict, record: Mapping[str, object]) -> dict:
    """The lead-1 permutation p of every model and sequence against #1378's record: the largest difference, and whether the Holm flags agree."""

    worst, flag_changes = 0.0, []
    for model in MODELS:
        old = record["windows"][window_name]["models"][model]["clustering"]["all"]["1"]
        new = rep["models"][model]["lead1"]
        for name in SEQUENCES:
            worst = max(worst, abs(old[name]["p_permutation"] - new[name]["p_permutation"]))
            if bool(old[name]["holm_clusters"]) != bool(new[name]["holm_clusters"]):
                flag_changes.append(f"{model}/{name}")
    return {"max_abs_difference_p_permutation": worst, "holm_flag_differences": flag_changes}


def score_command(args) -> int:
    declared = committed_declaration()
    record_1314 = json.loads(m63.RECORD_1314.read_text(encoding="utf-8"))
    record_1363 = json.loads(RECORD_1363.read_text(encoding="utf-8"))
    result: dict = {"issue": 1400, "declaration": "metadata/clustering_thinned_1400.json", "label": "development, not a verdict", "seed": SEED,
                    "lead1_seed": LEAD1_SEED, "permutations": PERMUTATIONS, "windows": {}, "reproduction": {}, "lead1_reproduction": {}, "walk_files": {},
                    "b4": declared["b4"], "amendments": declared["amendments"]}
    for name in WINDOWS:
        path = Path(args.walks) / f"{name}.json"
        if not path.exists():
            continue
        raw = path.read_bytes()
        doc = json.loads(raw)
        if result.get("panel_sha256") not in (None, doc["panel_sha256"]):
            raise ValueError("the walk files were made from different panels")
        if record_1363.get("panel_sha256") != doc["panel_sha256"]:
            raise ValueError("the walk's panel is not the panel of #1363's record")
        result["panel_sha256"] = doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": hashlib.sha256(raw).hexdigest(), "refits": doc.get("refits")}
        window = m63.Window(doc)
        result["reproduction"][name] = m63.reproduction_check(window, record_1314)
        result["windows"][name] = window_report(window, workers=args.workers)
        result["lead1_reproduction"][name] = lead1_reproduction(name, result["windows"][name], record_1363)
    if not result["windows"]:
        raise SystemExit(f"no walk file in {args.walks}")
    if args.sim:
        result["simulation"] = json.loads(Path(args.sim).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------------


def _pct(x: float, digits: int = 1) -> str:
    return f"{100 * x:.{digits}f}%"


def _fp(p: Optional[float]) -> str:
    return "n/a" if p is None else ("<0.0001" if p < 1e-4 else f"{p:.4f}")


def sim_tables(sim: dict) -> List[str]:
    out: List[str] = []
    for days, rates in sim["sizes"].items():
        out += [f"### {days} decision days ({rates['paths']} paths, {rates['permutations']} shuffles per unthinned test)", "",
                "Share of paths on which one test rejects at 0.05 (unadjusted), for a forecaster that is calibrated by construction. Nominal 5%.", "",
                "| lead | event | #1363 unthinned permutation | thinned, phase 0 (the protocol's series) | thinned, any phase | thinned, mean over phases |", "|---|---|---|---|---|---|"]
        for h in LEADS:
            for ev in SIM_EVENTS:
                c = rates["by_lead_event"][str(h)][ev]
                out.append(f"| {h} | {ev} | {_pct(c['unthinned'])} | {_pct(c['phase0'])} | {_pct(c['any_phase'])} | {_pct(c['mean_phase'])} |")
        f = rates["family"]
        out += ["", "Share of paths on which Holm (alpha 0.05) flags at least one sequence, so the false-alarm rate of the rule as the page applies it. "
                f"Unthinned family: {UNTHINNED_FAMILY_SIM} sequences (4 events, 5 leads). Thinned family: {THINNED_FAMILY_SIM} p-values (lead 1 unthinned, leads 2 to 5 by phase).", "",
                "| family | share of paths with a flag |", "|---|---|",
                f"| unthinned, all leads | {_pct(f['unthinned_all'])} |", f"| thinned reading, all leads | {_pct(f['thinned_all'])} |",
                f"| unthinned, leads 2 to 5 | {_pct(f['unthinned_2_to_5'])} |", f"| thinned reading, leads 2 to 5 | {_pct(f['thinned_2_to_5'])} |", "",
                "| lead | unthinned family flags the lead | thinned family flags the lead |", "|---|---|---|"]
        for h in LEADS:
            out.append(f"| {h} | {_pct(rates['family_by_lead']['unthinned'][str(h)])} | {_pct(rates['family_by_lead']['thinned'][str(h)])} |")
        out.append("")
    return out


def _leads_clustering(model_rep: dict) -> Dict[int, List[str]]:
    """Per lead, the sequences that cluster on the declared reading."""

    out: Dict[int, List[str]] = {1: sorted(n for n, r in model_rep["lead1"].items() if r["holm_clusters"])}
    for h in THIN_LEADS:
        out[h] = [n for n in SEQUENCES if model_rep["clusters"][str(h)][n]]
    return out


def lead_summary_table(rep: dict, models: Sequence[str]) -> List[str]:
    out = ["| model | lead | reading | sequences that cluster (of 8) | which |", "|---|---|---|---|---|"]
    for model in models:
        by_lead = _leads_clustering(rep["models"][model])
        for h in LEADS:
            names = by_lead[h]
            reading = "unthinned permutation (#1363, unchanged)" if h == 1 else "thinned, by phase (Holm)"
            out.append(f"| {LABELS[model]} | {h} | {reading} | {len(names)} | {', '.join(names) if names else 'none'} |")
    return out


def phase_count_table(rep: dict, model: str) -> List[str]:
    out = ["| lead | sequence | phase series | with p < 0.05 | smallest p (asymptotic) | smallest p (permutation) | clusters (Holm) |", "|---|---|---|---|---|---|---|"]
    rows = rep["models"][model]["phases"]
    for h in THIN_LEADS:
        for name in SEQUENCES:
            sel = [r for r in rows if r["lead"] == h and r["sequence"] == name]
            out.append(f"| {h} | {name} | {len(sel)} | {sum(r['p_asymptotic'] < ALPHA for r in sel)} | {_fp(min(r['p_asymptotic'] for r in sel))} | "
                       f"{_fp(min(r['p_permutation'] for r in sel))} | {'yes' if rep['models'][model]['clusters'][str(h)][name] else 'no'} |")
    return out


def lead1_table(rep: dict, model: str) -> List[str]:
    out = ["| sequence | misses (rate) | P(miss after miss) | P(miss after hit) | p (permutation) | clusters (Holm, 8 sequences) |", "|---|---|---|---|---|---|"]
    for name in SEQUENCES:
        r = rep["models"][model]["lead1"][name]
        after_miss = "n/a" if r["p_miss_after_miss"] is None else _pct(r["p_miss_after_miss"])
        after_hit = "n/a" if r["p_miss_after_hit"] is None else _pct(r["p_miss_after_hit"])
        out.append(f"| {name} | {r['misses']} ({_pct(r['rate'])}) | {after_miss} | {after_hit} | {_fp(r['p_permutation'])} | {'yes' if r['holm_clusters'] else 'no'} |")
    return out


def regime_table(rep: dict, model: str) -> List[str]:
    out = ["| regime | lead | series read | sequences that cluster (of 8) | which |", "|---|---|---|---|---|"]
    for reg, block in rep["models"][model]["regime"].items():
        for h in THIN_LEADS:
            names = [n for n in SEQUENCES if block["clusters"][str(h)][n]]
            read = sum(r["read"] for r in block["phases"] if r["lead"] == h)
            out.append(f"| {reg} | {h} | {read} of {sum(1 for r in block['phases'] if r['lead'] == h)} | {len(names)} | {', '.join(names) if names else 'none'} |")
    return out


def unadjusted_counts(rep: dict) -> List[str]:
    out = ["| model | leads 2 to 5: phase series read | with unadjusted p < 0.05 | share | a calibrated forecaster gives about |", "|---|---|---|---|---|"]
    for model in MODELS:
        rows = [r for r in rep["models"][model]["phases"] if r["read"]]
        k = sum(r["p_asymptotic"] < ALPHA for r in rows)
        out.append(f"| {LABELS[model]} | {len(rows)} | {k} | {_pct(k / len(rows)) if rows else 'n/a'} | 5% |")
    return out


def answer(r: dict) -> List[str]:
    dev = r["windows"]["development"]
    by = _leads_clustering(dev["models"][CANDIDATE])
    clustered = [h for h in LEADS if by[h]]
    quiet = [h for h in LEADS if not by[h]]
    out = ["## The answer", "",
           "**Which leads' misses cluster, on the declared reading, for the candidate on the development window.** "
           + "; ".join(f"lead {h}: {', '.join(by[h]) if by[h] else 'none of the 8 sequences'}" for h in LEADS) + ".",
           f"Leads where at least one sequence clusters: {', '.join(map(str, clustered)) if clustered else 'none'}; leads where none does: {', '.join(map(str, quiet)) if quiet else 'none'}. "
           "At lead 1 the reading is #1363's unchanged; at leads 2 to 5 it is Christoffersen's independence on every phase of the thinned series, Holm-adjusted over the phase series of the model.", ""]
    for model in REFERENCES:
        b = _leads_clustering(dev["models"][model])
        out.append(f"{LABELS[model]}: " + "; ".join(f"lead {h}: {len(b[h])} of 8" for h in LEADS) + ".")
    reg = dev["models"][CANDIDATE]["regime"]
    parts = []
    for rname, block in reg.items():
        hit = [f"lead {h} ({len([n for n in SEQUENCES if block['clusters'][str(h)][n]])} of 8)" for h in THIN_LEADS if any(block["clusters"][str(h)].values())]
        parts.append(f"{rname}: " + (", ".join(hit) if hit else "none"))
    out += ["", "**Inside regimes, leads 2 to 5, candidate (the pooled window mixes regimes whose miss rates differ, which also breaks independence; this is the cleaner reading).** " + "; ".join(parts) + "."]
    y26 = r["windows"].get("2026")
    if y26:
        b = _leads_clustering(y26["models"][CANDIDATE])
        out += ["", "2026 days (shown apart, decide nothing), candidate: " + "; ".join(f"lead {h}: {len(b[h])} of 8" for h in LEADS) + "."]
    sim = r.get("simulation")
    if sim:
        big = sim["sizes"][str(SAMPLE_SIZES[0])]
        out += ["", f"**Size of the old reading.** At {SAMPLE_SIZES[0]} decision days, a forecaster that is calibrated by construction is flagged on at least one sequence of leads 2 to 5 in "
                f"{_pct(big['family']['unthinned_2_to_5'])} of paths by the unthinned permutation family and in {_pct(big['family']['thinned_2_to_5'])} by the thinned reading "
                "(nominal 5%). So the #1378 rows at leads 2 to 5 mostly measure the overlap, and the thinned reading is the one to cite."]
    return out


def render(r: dict) -> str:
    dev, y26 = r["windows"].get("development"), r["windows"].get("2026")
    lines = [
        "# Clustering at leads 2 to 5 on thinned days, and the size of the unthinned test (#1400)",
        "",
        "**Hypothesis and step:** H5 (primary goal), registration design (known limits): for the known-limits section and rule 7 of the confirmation-design draft (#1393). "
        "**Development data, not a verdict** (scoring protocol v1, #640). Nothing is registered or published, no record is edited, and nothing is adopted. "
        "This page is new; the page of #1378 (`docs/research/candidate-calibration-1363-result.md`) stays as it is. "
        f"Generated by `scripts/clustering_thinned_1400.py page` from `docs/research/clustering-thinned-1400/result.json`; declared in `metadata/clustering_thinned_1400.json` "
        f"before any figure. Candidate: (s3c-ann-net) at the 18:00 decision instant, walked unchanged. Panel digest `{r['panel_sha256']}`. {r['b4']}.",
        "",
        "**Why.** Consecutive h-step forecasts share h - 1 outcomes, so a calibrated forecaster's hit sequence is serially dependent from one day to the next, and an unthinned "
        "test rejects it too often (#998). The protocol reads independence on every h-th decision day. #1378 read clustering unthinned; this page reads leads 2 to 5 the protocol's way, "
        "on all h phases of the thinned series (phase 0 is the series `scoring_protocol.coverage_cells` reads), and measures how often each reading rejects a calibrated forecaster. "
        "Lead 1 is unchanged. Thinning removes the overlap, not a miss rate that moves with the regime or the day type: the regime rows are there for that, and no day-type split of the clustering is made.",
        "",
        "**Reproduction.** Each walk's mean grid CRPS (candidate, B1, B1' and B2) equals the 18:00 record of #1314 to 1e-9, or the script refused to write this record. "
        "The lead-1 permutation p-values equal #1378's: "
        + "; ".join(f"{w}: largest difference {v['max_abs_difference_p_permutation']:.2e}, Holm flags that differ from #1378's (its family was 40 sequences, this one 8): "
                   f"{', '.join(v['holm_flag_differences']) if v['holm_flag_differences'] else 'none'}" for w, v in r["lead1_reproduction"].items()) + ".",
        "",
    ]
    lines += answer(r)
    sim = r.get("simulation")
    if sim:
        lines += ["", "## How often each reading rejects a calibrated forecaster", "",
                  f"The two-regime AR(1) world of #961 and #998 (phi 0.9, innovation sd 1.0 in calm and 2.5 in stress blocks of 250 days), the forecaster that knows the dynamics, so it is calibrated at every lead by construction. "
                  f"Seed {sim['seed']}, {sim['paths']} paths; the standard error of a rate near 5% is about 1 percentage point. The outcome is continuous, so ties do not arise and the strict rule only is simulated; "
                  "the real target is in whole basis points, which this does not copy. It measures size, not power against the clustering the market may have.", ""]
        lines += sim_tables(sim)
    for name, rep in (("The development window", dev), ("The 2026 development days (shown apart; decide nothing)", y26)):
        if rep is None:
            continue
        lines += [f"## {name}", "", f"{rep['decision_days']} decision days ({rep['first_decision']} to {rep['last_decision']}), {rep['cells']} cells, last target {rep['last_target']}.", "",
                  "### Which leads' misses cluster, by model", ""]
        lines += lead_summary_table(rep, MODELS) + ["", "### Phase series with an unadjusted p below 0.05, leads 2 to 5", ""]
        lines += unadjusted_counts(rep)
        lines += ["", "### The candidate at lead 1 (unthinned permutation, as #1363)", ""] + lead1_table(rep, CANDIDATE)
        lines += ["", "### The candidate at leads 2 to 5, by sequence (thinned phase series)", ""] + phase_count_table(rep, CANDIDATE) + [""]
        if rep["models"][CANDIDATE]["regime"]:
            lines += ["### The candidate inside each regime (phase series with fewer than 20 kept values are not read; Holm per regime)", ""] + regime_table(rep, CANDIDATE) + [""]
    lines += ["## For the known-limits section and rule 7 of #1393 (a draft for her; nothing is adopted)", "",
              "The text below is generated from the development window. Whether and how it is written in is hers.", ""]
    by = _leads_clustering(dev["models"][CANDIDATE])
    for h in LEADS:
        lines.append(f"- Lead {h}: " + (f"the candidate's misses cluster in time on the declared reading over the whole window ({', '.join(by[h])})." if by[h] else "no cluster is read on the declared reading."))
        if h > 1:
            regs = [f"{rname} ({len([n for n in SEQUENCES if b['clusters'][str(h)][n]])} of 8)" for rname, b in dev["models"][CANDIDATE]["regime"].items() if any(b["clusters"][str(h)].values())]
            lines.append(f"  Inside regimes: " + (", ".join(regs) if regs else "none") + ".")
    lines += ["", "## What it does and does not show", "",
              "It shows which leads' hit sequences are serially dependent once the overlap of consecutive forecasts is removed, and how often each reading rejects a calibrated forecaster at this sample size. "
              "It does not separate clustering in time from a miss rate that moves with the regime beyond the regime rows, it reads no day-type group, it says nothing about power, and nothing here is a verdict. "
              "Nothing is corrected for the number of readings across models and windows. B4 (#1360) is not compared.", ""]
    return "\n".join(lines)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("sim", help="the size of the unthinned and the thinned reading for a calibrated forecaster")
    s.add_argument("--output", required=True)
    s.add_argument("--workers", type=int, default=4)
    s.set_defaults(func=sim_command)
    c = sub.add_parser("score", help="the thinned clustering reading from the walk files of scripts/candidate_calibration_1363.py walk")
    c.add_argument("--walks", required=True)
    c.add_argument("--sim", default=None)
    c.add_argument("--output", required=True)
    c.add_argument("--workers", type=int, default=4)
    c.set_defaults(func=score_command)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
