#!/usr/bin/env python3
"""The replay of #792 read at the critical values of the protocol, not each pair's own (H1 step 4, #873).

#792 (`scripts/power_replay.py`) called its families a1 and a2 "the current test", but calibrated each pair's critical
values on that pair's own series (#833). The protocol applies one set of values to every comparison. This script replays
the same windows over the same real forecast pairs and known-equal series, at 250 days and the looks 60, 125 and 250,
and reads each window at the protocol's grid-comparison values at looks 2 and 3 (`scoring_protocol.CRITICAL_VALUES`
today; the recalibration of #873, `docs/research/protocol-calibration-873/result.json`, as a draft). Development data
only (no day after 2025-12-31, as in #792); nothing here is a verdict.

    PYTHONPATH=src python3 scripts/power_replay_inforce_873.py run --out docs/research/power-replay-873
    PYTHONPATH=src python3 scripts/power_replay_inforce_873.py check --out docs/research/power-replay-873

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

_spec = importlib.util.spec_from_file_location("power_replay_for_873", REPO / "scripts" / "power_replay.py")
pr = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = pr
_spec.loader.exec_module(pr)

CALIBRATION = REPO / "docs" / "research" / "protocol-calibration" / "result.json"
CALIBRATION_873 = REPO / "docs" / "research" / "protocol-calibration-873" / "result.json"
PUBLISHED_792 = REPO / "docs" / "research" / "power-replay-754" / "result.json"
DAYS = 250
LOOKS = pr.cd.checkpoints(DAYS)


FIVE_LEVEL_SETS = (
    "in force today, B3 five-level values (calibrated on S(B3) - S(B1))",
    "draft of #873, B3 five-level values (calibrated on S(B1) - S(B3))",
)


def value_sets():
    """The protocol's values at looks 2 and 3: those in force today and the draft's, for the grid comparison (read
    on every pair) and for B3's five-level comparison (read on P3 only, the pair that is B3 against B1)."""

    draft = json.loads(CALIBRATION_873.read_text(encoding="utf-8"))["comparison_critical_values"]
    return {
        "in force today (calibrated on S(B2) - S(B1))": {n: sp.CRITICAL_VALUES[sp.GRID_COMPARISON][n] for n in LOOKS[1:]},
        "draft of #873 (calibrated on S(B1) - S(candidate))": {n: draft[sp.GRID_COMPARISON][str(n)] for n in LOOKS[1:]},
        FIVE_LEVEL_SETS[0]: {n: sp.CRITICAL_VALUES[sp.FIVE_LEVEL_COMPARISON][n] for n in LOOKS[1:]},
        FIVE_LEVEL_SETS[1]: {n: draft[sp.FIVE_LEVEL_COMPARISON][str(n)] for n in LOOKS[1:]},
    }


def replay(cell, kind, critical):
    """Each 250-day window of a series: its last day and (test, gated, undefined) at `critical`."""

    base = pr.null_cell(cell, kind)
    out = []
    for start in pr.window_starts(len(base.d), DAYS):
        end = start + DAYS
        d5 = base.d[start:end]
        if kind == "E3":
            d5 = pr.flip_blocks(d5, pr.SEED * 1_000_003 + start * 31 + DAYS)
        out.append((base.dates[end - 1], pr.detect_a(d5, base.b[start:end], LOOKS, critical)))
    return out


def summarize(windows):
    rng = random.Random(pr.SEED)
    block = math.ceil(DAYS / pr.STEP)
    out = {}
    for label in ("all",) + pr.REGIMES:
        part = [w for w in windows if label == "all" or pr.regime_of(w[0]) == label]
        if not part:
            continue
        cell = {"windows": len(part), "effective": max(1, round((len(part) - 1) * pr.STEP / DAYS) + 1)}
        for name, position in (("test", 0), ("gated", 1)):
            cell[name] = list(pr.share_interval([int(w[1][position]) for w in part], block=block, rng=rng))
        out[label] = cell
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(args) -> int:
    cells, _kinds, digest, _pool = pr.build_cells()
    sets = value_sets()
    result = {
        "panel_sha256": digest, "calibration_sha256": sha256(CALIBRATION),
        "draft_calibration_sha256": sha256(CALIBRATION_873), "published_792_sha256": sha256(PUBLISHED_792),
        "days": DAYS, "looks": list(LOOKS), "study_end": pr.STUDY_END.isoformat(), "step": pr.STEP, "seed": pr.SEED,
        "values": {name: {str(n): v for n, v in c.items()} for name, c in sets.items()},
        "replay": {},
    }
    for name, critical in sets.items():
        for pair in (("P3",) if name in FIVE_LEVEL_SETS else pr.PAIRS):
            for kind in pr.KINDS:
                result["replay"][f"{name}|{pair}|{kind}"] = summarize(replay(cells[pair], kind, critical))
            print("replayed", name, pair, flush=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out / "result.json")
    return 0


def check_command(args) -> int:
    result = json.loads((Path(args.out) / "result.json").read_text(encoding="utf-8"))
    for key, path in (("calibration_sha256", CALIBRATION), ("draft_calibration_sha256", CALIBRATION_873),
                      ("published_792_sha256", PUBLISHED_792)):
        if result[key] != sha256(path):
            raise ValueError(f"result.json was made from another {path.name} ({key})")
    wanted = {name: {str(n): v for n, v in c.items()} for name, c in value_sets().items()}
    if result["values"] != wanted:
        raise ValueError("result.json was made at other critical values")
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--out", required=True)
    run.set_defaults(func=run_command)
    check = sub.add_parser("check")
    check.add_argument("--out", required=True)
    check.set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
