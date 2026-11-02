#!/usr/bin/env python3
"""Size and power of the proposed H5 confirmation test on (s3c-ann-net)'s own loss differences (#1392; H5, registration design).

A development study, never a verdict. The proposed test (the draft of #1393): W_b = 0.97 S_b - S_C per decision origin, for each mandatory baseline b; the
simultaneous one-sided 95% lower bound on mean W across the baselines (max-t studentized stationary block bootstrap of whole origin vectors, each resample
studentized by its own Bartlett HAC standard error at lag 50) must exceed zero to pass; an upper bound below zero for at least one baseline fails at the
threshold; otherwise the test is inconclusive. The gated claim B tests mean S(flag) - S(net) > 0 at one-sided 5% on the same machinery.

Simulated data come from the candidate's development origin-level losses (`scripts/confirmation_losses_1392.py`): block resampling of whole origin vectors
and a regime-switching resampler calibrated to the development regime labels. A skill is imposed by rescaling each baseline's (or the flag arm's) losses
by a constant so that the population mean skill is exactly the stated one, which keeps the rounding, the dependence and the regime structure of the real
vectors. Every choice is in `metadata/confirmation_size_power_1392.json`, which `run` refuses to read unless it is committed and unchanged.

    PYTHONPATH=src python3 scripts/confirmation_size_power_1392.py run --losses docs/research/confirmation-size-power-1392/losses.json \\
        --out docs/research/confirmation-size-power-1392/result.json --mode reduced --workers 4
    PYTHONPATH=src python3 scripts/confirmation_size_power_1392.py run ... --mode full --out .../result-full.json   # the Mac run
    PYTHONPATH=src python3 scripts/confirmation_size_power_1392.py page --result .../result.json --output docs/research/confirmation-size-power-1392-result.md

Stdlib only.
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
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.exploration import require_exploratory_window  # noqa: E402

DECLARATION = REPO / "metadata" / "confirmation_size_power_1392.json"
THRESHOLD = 0.03
HAC_LAG = 50
ALPHA = 0.05
SEED = 1392
#: The mandatory baselines of the draft: B1'* (calendar-aware persistence, corrected horizon) and B2 (stands in for B2*, which is not yet built).
BASELINES = ("B1p*", "B2")


# -- arithmetic ------------------------------------------------------------------------------------------------------


def baseline_factor(mean_candidate: float, mean_other: float, skill: float) -> float:
    """The constant c with 1 - mean_candidate / (c * mean_other) = skill."""

    return mean_candidate / ((1.0 - skill) * mean_other)


def w_vector(candidate: Sequence[float], baseline: Sequence[float]) -> List[float]:
    """W = (1 - THRESHOLD) S_b - S_C per origin; its mean is zero at exactly THRESHOLD skill."""

    return [(1.0 - THRESHOLD) * b - c for b, c in zip(baseline, candidate)]


def hac_se(values: Sequence[float], lag: int) -> float:
    """The Bartlett long-run standard error of the mean, 0.0 for a series with no long-run variance."""

    n = len(values)
    variance = sp._long_run_variance(values, min(lag, n - 1))
    return math.sqrt(variance / n) if variance > 0.0 else 0.0


def segments(n: int, ell: float, rng: random.Random) -> List[tuple]:
    """A stationary resample of range(n) as (start, length) runs over the doubled series; geometric lengths of mean `ell`, the last one cut."""

    keep = 1.0 / ell
    out, total = [], 0
    while total < n:
        length = 1 if keep >= 1.0 else 1 + int(math.log(1.0 - rng.random()) / math.log1p(-keep))
        length = min(length, n - total)
        out.append((rng.randrange(n), length))
        total += length
    return out


def quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, math.ceil(q * (len(ordered) + 1)) - 1))]


def _t_draws(vectors: Sequence[Sequence[float]], ell: float, reps: int, rng: random.Random, lag: int):
    n = len(vectors[0])
    means = [sum(v) / n for v in vectors]
    ses = [hac_se(v, lag) for v in vectors]
    if any(se <= 0.0 for se in ses):
        raise ValueError("a loss-difference vector has no long-run variance; it cannot be studentized")
    doubled = [list(v) + list(v) for v in vectors]
    draws = []
    for _ in range(reps):
        runs = segments(n, ell, rng)
        row = []
        for k, base in enumerate(doubled):
            x: List[float] = []
            for start, length in runs:
                x += base[start:start + length]
            se = hac_se(x, lag)
            row.append((sum(x) / n - means[k]) / se if se > 0.0 else 0.0)
        draws.append(row)
    return means, ses, draws


def decide_main(w: Sequence[Sequence[float]], ell: float, reps: int, rng: random.Random, lag: int = HAC_LAG, alpha: float = ALPHA) -> str:
    """"pass", "fail" or "inconclusive" for the draft's primary claim over the baselines' W vectors."""

    means, ses, draws = _t_draws(w, ell, reps, rng, lag)
    crit = quantile([max(row) for row in draws], 1.0 - alpha)
    if all(m - crit * s > 0.0 for m, s in zip(means, ses)):
        return "pass"
    for k, (m, s) in enumerate(zip(means, ses)):
        if m - quantile([row[k] for row in draws], alpha) * s < 0.0:
            return "fail"
    return "inconclusive"


def decide_gated(d: Sequence[float], ell: float, reps: int, rng: random.Random, lag: int = HAC_LAG, alpha: float = ALPHA) -> bool:
    """True when the one-sided 95% lower bound on mean(S_flag - S_net) is above zero."""

    means, ses, draws = _t_draws([d], ell, reps, rng, lag)
    return means[0] - quantile([row[0] for row in draws], 1.0 - alpha) * ses[0] > 0.0


# -- the data-generating schemes --------------------------------------------------------------------------------------


def regime_chain(regimes: Sequence[str]) -> dict:
    """The first-order chain on the regime labels in time order, its transition matrix and its stationary law (power iteration)."""

    labels = sorted(set(regimes))
    counts = {a: {b: 0 for b in labels} for a in labels}
    for a, b in zip(regimes, regimes[1:]):
        counts[a][b] += 1
    matrix = {}
    for a in labels:
        total = sum(counts[a].values())
        matrix[a] = {b: (counts[a][b] / total if total else (1.0 if a == b else 0.0)) for b in labels}
    law = {a: 1.0 / len(labels) for a in labels}
    for _ in range(5000):
        law = {b: sum(law[a] * matrix[a][b] for a in labels) for b in labels}
    norm = sum(law.values())
    return {"labels": labels, "matrix": matrix, "stationary": {a: v / norm for a, v in law.items()}}


def block_sample(pool_size: int, n: int, gen_block: float, rng: random.Random) -> List[int]:
    out: List[int] = []
    for start, length in segments(pool_size, gen_block, rng):
        out += [(start + j) % pool_size for j in range(length)]
    return out


def regime_sample(regimes: Sequence[str], chain: Mapping[str, object], n: int, gen_block: float, rng: random.Random) -> List[int]:
    """Origins drawn by a regime chain: the state follows `chain`; inside a stay in one state the next origin is the regime's next one with probability
    1 - 1/gen_block, else a fresh draw from that regime."""

    by_regime: Dict[str, List[int]] = {}
    for i, r in enumerate(regimes):
        by_regime.setdefault(r, []).append(i)
    position = {i: p for r, idx in by_regime.items() for p, i in enumerate(idx)}
    labels = list(chain["labels"])
    state = rng.choices(labels, weights=[chain["stationary"][a] for a in labels])[0]
    out: List[int] = []
    previous: Optional[int] = None
    for _ in range(n):
        following = rng.choices(labels, weights=[chain["matrix"][state][b] for b in labels])[0] if out else state
        pool = by_regime[following]
        if out and following == state and rng.random() > 1.0 / gen_block:
            current = pool[(position[previous] + 1) % len(pool)]
        else:
            current = pool[rng.randrange(len(pool))]
        out.append(current)
        previous, state = current, following
    return out


def population_mean(series: Sequence[float], regimes: Sequence[str], scheme: str, chain: Mapping[str, object]) -> float:
    """The mean of `series` under the scheme's own law: the pool mean for blocks, the stationary mixture of regime means for the regime chain."""

    if scheme == "block":
        return sum(series) / len(series)
    total = 0.0
    for a in chain["labels"]:
        members = [x for x, r in zip(series, regimes) if r == a]
        total += chain["stationary"][a] * sum(members) / len(members)
    return total


def run_chunk(pool: Mapping[str, object], spec: Mapping[str, object], count: int, key: str, seed: int) -> dict:
    """`count` simulated confirmation data sets of one cell, each decided by the draft's test. Reproducible from (seed, key)."""

    regimes = pool["regime"]
    chain = regime_chain(regimes) if spec["scheme"] == "regime" else None
    mc = population_mean(pool["cand"], regimes, spec["scheme"], chain)
    factors = [1.0 if e is None else baseline_factor(mc, population_mean(b, regimes, spec["scheme"], chain), e)
               for b, e in zip(pool["bases"], spec["effects"])]
    flag_effect = spec.get("flag_effect")
    flag_factor = None if flag_effect is None else baseline_factor(mc, population_mean(pool["flag"], regimes, spec["scheme"], chain), flag_effect)
    out = {"main": {"pass": 0, "fail": 0, "inconclusive": 0}, "count": count}
    if flag_effect is not None:
        out["gated"] = {"reject": 0}
        out["joint"] = {"pass_and_reject": 0}
    for m in range(count):
        rng = random.Random(f"{seed}/{key}/{m}")
        if spec["scheme"] == "block":
            idx = block_sample(len(pool["cand"]), spec["n"], spec["gen_block"], rng)
        else:
            idx = regime_sample(regimes, chain, spec["n"], spec["gen_block"], rng)
        cand = [pool["cand"][i] for i in idx]
        w = [w_vector(cand, [f * b[i] for i in idx]) for f, b in zip(factors, pool["bases"])]
        verdict = decide_main(w, spec["ell"], spec["reps"], rng, lag=spec["lag"])
        out["main"][verdict] += 1
        if flag_effect is not None:
            rejected = decide_gated([flag_factor * pool["flag"][i] - c for i, c in zip(idx, cand)], spec["ell"], spec["reps"], rng, lag=spec["lag"])
            out["gated"]["reject"] += int(rejected)
            out["joint"]["pass_and_reject"] += int(rejected and verdict == "pass")
    return out


# -- the loss file and the declaration ---------------------------------------------------------------------------------


def _fill_regimes(rows: list) -> list:
    """An origin the regime split leaves unlabelled takes the label of the origin before it (of the one after, at the start)."""

    labels = [r[1] for r in rows]
    for i, label in enumerate(labels):
        if not label:
            labels[i] = next((labels[j] for j in range(i - 1, -1, -1) if labels[j]), next((x for x in labels[i:] if x), "unlabelled"))
    return [(r[0], label, r[2]) for r, label in zip(rows, labels)]


def load_losses(path: Path) -> dict:
    """The development origin-level losses of both windows in time order, as the pool the schemes resample.

    Raises:
        ValueError: an origin after the development end (2026-09-03), or arms of unequal length.
    """

    record = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for window in record["windows"].values():
        days = [date.fromisoformat(d) for d in window["origins"]]
        require_exploratory_window(days, where="scripts/confirmation_size_power_1392")
        for i, d in enumerate(days):
            rows.append((d, window["regime"][i], {a: s[i] for a, s in window["scores"].items()}))
    rows.sort(key=lambda r: r[0])
    rows = _fill_regimes(rows)
    if len({r[0] for r in rows}) != len(rows):
        raise ValueError("an origin appears in both windows")
    return {"origins": [r[0].isoformat() for r in rows], "regime": [r[1] for r in rows], "cand": [r[2]["candidate"] for r in rows],
            "flag": [r[2]["flag"] for r in rows], "bases": [[r[2][b] for r in rows] for b in BASELINES], "legacy_b1": [r[2]["B1"] for r in rows]}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is tracked and unchanged since HEAD."""

    rel = str(path.relative_to(REPO))
    if subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=REPO, capture_output=True).returncode != 0 or \
            subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=REPO).returncode != 0:
        raise SystemExit(f"{rel} must be committed and unchanged before any score is computed")
    return json.loads(path.read_text(encoding="utf-8"))


def cells_of(decl: Mapping[str, object]) -> List[dict]:
    """Every declared cell (the test block other than the primary is a "sensitivity" cell): (key, group, scheme, n, ell, effects, flag_effect)."""

    g = decl["grid"]
    cells: List[dict] = []

    def add(group, scheme, n, ell, effects, flag=None):
        tag = "-".join("observed" if e is None else f"{e:g}" for e in effects) + ("" if flag is None else f"_b{flag:g}")
        cells.append({"key": f"{group}/{scheme}/n{n}/ell{ell}/{tag}", "group": group, "scheme": scheme, "n": n, "ell": ell, "effects": list(effects), "flag_effect": flag})

    for scheme in g["schemes"]:
        for n in g["lengths"]:
            for e in g["effects_main"]:
                add("main", scheme, n, g["primary_block"], [e, e])
            for ell in g["test_blocks"]:
                if ell != g["primary_block"]:
                    for e in g["effects_main"][1:]:
                        add("sensitivity", scheme, n, ell, [e, e])
            add("observed", scheme, n, g["primary_block"], [None, None])
            for first, other in ((g["binding"]["effect"], g["binding"]["other"]), (g["binding"]["other"], g["binding"]["effect"])):
                add("binding", scheme, n, g["primary_block"], [first, other])
            for b in g["gated"]["b_effects"]:
                add("gated", scheme, n, g["primary_block"], [g["gated"]["a_effect"]] * 2, b)
        for n in g["length_extension"]["lengths"]:
            add("extension", scheme, n, g["primary_block"], [g["length_extension"]["effect"]] * 2)
    return cells


def _task(job):
    pool, spec, count, key, seed = job
    return key, run_chunk(pool, spec, count, key, seed)


def run(args) -> int:
    decl = committed_declaration()
    mode = decl["modes"][args.mode]
    pool = load_losses(Path(args.losses))
    cells = cells_of(decl)
    wanted = args.only.split(",") if args.only else mode["groups"]
    cells = [c for c in cells if c["group"] in wanted]
    jobs = []
    chunk = max(1, mode["M"] // 20)
    for cell in cells:
        spec = dict(cell, reps=mode["reps"], lag=decl["grid"]["hac_lag"], gen_block=decl["grid"]["generation_block"])
        done = 0
        while done < mode["M"]:
            count = min(chunk, mode["M"] - done)
            jobs.append((pool, spec, count, cell["key"], SEED + done))
            done += count
    totals: Dict[str, dict] = {}
    with multiprocessing.get_context("fork").Pool(args.workers) as workers:
        for key, part in workers.imap_unordered(_task, jobs, chunksize=1):
            t = totals.setdefault(key, {"count": 0, "main": {"pass": 0, "fail": 0, "inconclusive": 0}})
            t["count"] += part["count"]
            for k, v in part["main"].items():
                t["main"][k] += v
            for group in ("gated", "joint"):
                if group in part:
                    for k, v in part[group].items():
                        t.setdefault(group, {}).setdefault(k, 0)
                        t[group][k] += v
    result = {"issue": 1392, "label": "development, not a verdict", "declaration": str(DECLARATION.relative_to(REPO)), "mode": args.mode, "M": mode["M"],
              "reps": mode["reps"], "seed": SEED, "pool_origins": len(pool["cand"]), "first_origin": pool["origins"][0], "last_origin": pool["origins"][-1],
              "baselines": list(BASELINES), "pool_means": {"candidate": sum(pool["cand"]) / len(pool["cand"]), "flag": sum(pool["flag"]) / len(pool["flag"]),
                                                          **{b: sum(s) / len(s) for b, s in zip(BASELINES, pool["bases"])}, "B1": sum(pool["legacy_b1"]) / len(pool["legacy_b1"])},
              "chain": regime_chain(pool["regime"]), "cells": []}
    for cell in cells:
        result["cells"].append(dict(cell, **totals[cell["key"]]))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run")
    r.add_argument("--losses", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--mode", choices=("reduced", "full"), default="reduced")
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--only", default="", help="comma list of cell groups (main, observed, binding, gated, extension, sensitivity); default: the mode's own")
    r.set_defaults(func=run)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
