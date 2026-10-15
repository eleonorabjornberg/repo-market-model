#!/usr/bin/env python3
"""Power study of the test in force after ruling 5 (H1, #769).

The rule is `docs/research/power-study-769.md`, committed before this script ran. Development data only; nothing
here is a verdict.

    PYTHONPATH=src python3 scripts/power_study_769.py run --out docs/research/power-study-769 [--paths N]
    PYTHONPATH=src python3 scripts/power_study_769.py check --out docs/research/power-study-769

`run` scores B1 and B2 on the development decision days (the helpers of `scripts/protocol_coverage.py`), simulates
confirmation paths under four readings (history x path generator) at the critical values of `scoring_protocol`, and
writes `result.json`. `check` refuses a result made under another text of the rule or other critical values.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.metrics import stationary_bootstrap_indices  # noqa: E402

RULE = REPO / "docs" / "research" / "power-study-769.md"
CALIBRATION = REPO / "docs" / "research" / "protocol-calibration" / "result.json"
LOOKS = (125, 250)
PATH_DAYS = 250
DELTA = 0.03
NOISE = 1.0
DELTA_GRID = (0.03, 0.04, 0.05, 0.06, 0.08, 0.10)
NOISE_SENSITIVITY = (0.5, 0.25)
TARGET_POWER = 0.80
PATHS = 2000
SEED = 769 * 100_003
READINGS = {
    "a": ("full", "circular"),
    "b": ("post-2020-04", "circular"),
    "c": ("full", "stationary"),
    "d": ("post-2020-04", "stationary"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def critical_values():
    """The grid comparison's values at looks 2 and 3, from `scoring_protocol`; refused if the record disagrees."""

    record = json.loads(CALIBRATION.read_text(encoding="utf-8"))["comparison_critical_values"][sp.GRID_COMPARISON]
    values = {n: sp.CRITICAL_VALUES[sp.GRID_COMPARISON][n] for n in LOOKS}
    for n in LOOKS:
        if record[str(n)] != values[n]:
            raise ValueError(f"scoring_protocol's critical value at {n} days differs from the calibration record")
    return values


def candidate(s1, s2, delta, noise):
    e = [a - b for a, b in zip(s1, s2)]
    centre = sum(e) / len(e)
    return [delta * a + noise * (x - centre) for a, x in zip(s1, e)]


def circular_indices(n, length, rng):
    out = []
    while len(out) < length:
        start = rng.randrange(n)
        out.extend((start + k) % n for k in range(sp.WINDOW_BLOCK))
    return out[:length]


def days_needed(power):
    for n in LOOKS:
        if power[str(n)] >= TARGET_POWER:
            return n
    return None


def detections(s1, s2, *, delta, noise, generator, paths, seed):
    critical = critical_values()
    diff = candidate(s1, s2, delta, noise)
    counts = {"ungated": {n: 0 for n in LOOKS}, "gated": {n: 0 for n in LOOKS}}
    for i in range(paths):
        rng = random.Random(seed + i)
        if generator == "circular":
            index = circular_indices(len(s1), PATH_DAYS, rng)
        elif generator == "stationary":
            index = stationary_bootstrap_indices(len(s1), sp.BLOCK_LENGTH, rng)[:PATH_DAYS]
        else:
            raise ValueError(f"unknown generator {generator!r}")
        bench = [s1[j] for j in index]
        d = [diff[j] for j in index]
        first = {"ungated": None, "gated": None}
        for n in LOOKS:
            window = d[:n]
            mean = sum(window) / n
            se = math.sqrt(sp._long_run_variance(window, sp.HAC_LAG) / n)
            if mean - critical[n] * se > 0.0:
                first["ungated"] = first["ungated"] or n
                if mean / (sum(bench[:n]) / n) >= sp.MME:
                    first["gated"] = first["gated"] or n
        for kind in counts:
            for n in LOOKS:
                counts[kind][n] += first[kind] is not None and first[kind] <= n
    out = {kind: {str(n): v / paths for n, v in c.items()} for kind, c in counts.items()}
    out["monte_carlo_se"] = {str(n): math.sqrt(p * (1 - p) / paths) for n, p in out["gated"].items()}
    return out


def load_protocol_coverage():
    spec = importlib.util.spec_from_file_location("protocol_coverage_for_769", REPO / "scripts" / "protocol_coverage.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_command(args) -> int:
    coverage = load_protocol_coverage()
    out = Path(args.out)
    result = {
        "rule": str(RULE.relative_to(REPO)), "rule_sha256": sha256(RULE),
        "calibration_sha256": sha256(CALIBRATION),
        "constants": {"paths": args.paths, "seed": SEED, "target_power": TARGET_POWER, "mme": sp.MME,
                      "looks": list(LOOKS), "block_length": sp.BLOCK_LENGTH, "hac_lag": sp.HAC_LAG,
                      "critical_values": {str(n): v for n, v in critical_values().items()}},
        "readings": {},
    }
    for name, (history, generator) in READINGS.items():
        s1, s2 = coverage.development_scores(history)
        plan = [(NOISE, d) for d in DELTA_GRID] + [(n, DELTA) for n in NOISE_SENSITIVITY] + [(NOISE, 0.0)]
        cells = {}
        for noise, delta in plan:
            diff = candidate(s1, s2, delta, noise)
            cell = detections(s1, s2, delta=delta, noise=noise, generator=generator, paths=args.paths, seed=SEED)
            cell.update(series_skill_against_b1=sum(diff) / sum(s1), series_mean_d=sum(diff) / len(diff),
                        days_needed=days_needed(cell["gated"]))
            cells[f"noise={noise}, delta={delta}"] = cell
            print(name, history, generator, noise, delta, json.dumps(cell["gated"]), flush=True)
        smallest = next((d for d in DELTA_GRID if cells[f"noise={NOISE}, delta={d}"]["gated"][str(LOOKS[-1])] >= TARGET_POWER), None)
        result["readings"][name] = {
            "history": history, "generator": generator, "series_days": len(s1), "cells": cells,
            "size_null": cells[f"noise={NOISE}, delta=0.0"],
            "days_needed_for_3_percent": cells[f"noise={NOISE}, delta={DELTA}"]["days_needed"],
            "smallest_skill_detected_within_250_days_at_target_power": smallest,
        }
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out / "result.json")
    return 0


def check_command(args) -> int:
    result = json.loads((Path(args.out) / "result.json").read_text(encoding="utf-8"))
    if result["rule_sha256"] != sha256(RULE):
        raise ValueError("result.json was made under another text of the rule")
    if result["calibration_sha256"] != sha256(CALIBRATION):
        raise ValueError("result.json was made under another calibration record")
    if result["constants"]["critical_values"] != {str(n): v for n, v in critical_values().items()}:
        raise ValueError("result.json was made at other critical values than scoring_protocol's")
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--out", required=True)
    run.add_argument("--paths", type=int, default=PATHS)
    run.set_defaults(func=run_command)
    check = sub.add_parser("check")
    check.add_argument("--out", required=True)
    check.set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
