#!/usr/bin/env python3
"""H1 step 3 (#1015): #963's contiguous-window rules on the leg against B2.

A report that changes nothing: `scoring_protocol.CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are only read, and
so are the B2-leg values of the draft amendment in PR #953. Everything it computes is declared in
`metadata/b2_leg_contiguous_1015.json`, which `run` refuses to read unless it is committed and unchanged. Development days
only, the series of `scripts/contiguous_calibration_963.py` (its `build`, unchanged).

For d = S(B2) - S(candidate), candidate in {`spread_mr_ctx`, `gbm_funding`}, it applies #963's rules unchanged: the critical
value c at 125, 250 and 500 days on the contiguous, stationary-10 and circular-10 generators, with the size at the values in
force and at the draft values of #953. It recomputes the leg against B1 (d = S(B1) - S(candidate)), checks that it reproduces
#963's record, and states the reading of each leg and the joint reading.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/spread_distribution_634.py walk \\
        --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
    PYTHONPATH=src python3 scripts/b2_leg_contiguous_1015.py run --published PUB.csv --walks OUT --output OUT/result.json
    python3 scripts/b2_leg_contiguous_1015.py report OUT/result.json
    python3 scripts/b2_leg_contiguous_1015.py check

`report` copies the record to `docs/research/b2-leg-contiguous-1015/result.json` and writes the page
`docs/research/b2-leg-contiguous-1015-result.md` from it alone; `check` fails when the page is not what the record gives.
Standard library only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


c963 = _load("contiguous_calibration_963")

RESEARCH = REPO / "docs" / "research"
DECLARATION = REPO / "metadata" / "b2_leg_contiguous_1015.json"
RECORD = RESEARCH / "b2-leg-contiguous-1015" / "result.json"
PAGE = RESEARCH / "b2-leg-contiguous-1015-result.md"
RECORD_963 = c963.RECORD

CANDIDATES = ("spread_mr_ctx", "gbm_funding")
WINDOW_DAYS = c963.WINDOW_DAYS
GENERATORS = c963.GENERATORS
IN_FORCE = c963.IN_FORCE
#: The B2-leg values of draft amendment 3 (PR #953, 'B2|post-2020-04'); not in force. 500 days is read at the 250-day value.
DRAFT_953 = {125: 2.682105672772658, 250: 1.701424623493621, 500: 1.701424623493621}
SURVIVES_BELOW, FAILS_ABOVE = c963.SURVIVES_BELOW, c963.FAILS_ABOVE
REPRODUCTION_TOLERANCE = 1e-9


def _leg_series(data, candidate, benchmark, first):
    b, c = data["day_score"][benchmark], data["day_score"][candidate]
    return {d: b[d] - c[d] for d in data["days"] if d >= first and d in b and d in c}


def b2_leg_series(data, candidate, first: date = c963.POST_2020_FIRST):
    """`{decision day: S(B2) - S(candidate)}` from `first`: the leg against B2, positive favours the candidate."""

    return _leg_series(data, candidate, "B2", first)


def b1_leg_series(data, candidate, first: date = c963.POST_2020_FIRST):
    """`{decision day: S(B1) - S(candidate)}` from `first`: #963's series."""

    return _leg_series(data, candidate, "B1", first)


def reading(c250: float) -> str:
    """#963's rule on a leg's contiguous-window c at 250 days."""

    if c250 < SURVIVES_BELOW:
        return "survives"
    if c250 > FAILS_ABOVE:
        return "fails"
    return "neither"


def joint_reading(c_b1: float, c_b2: float) -> str:
    """The worse of the two legs' readings ("Supported" needs both)."""

    return reading(max(c_b1, c_b2))


def _job(job):
    candidate, days, generator, series = job
    ordered = c963.generator_statistics(series, days, generator)
    return (candidate, days, generator), {
        "windows": len(ordered), "c": sp._bound(ordered, 1.0 - c963.LEVEL, len(ordered)),
        "size_in_force": c963.share_above(ordered, IN_FORCE[days]),
        "size_draft_953": c963.share_above(ordered, DRAFT_953[days]),
        "effective_windows": c963.effective_windows(len(series), days),
    }


def run_command(args) -> int:
    c963.committed_declaration(DECLARATION)
    data = c963.build(args.published, args.walks)
    b2 = {c: b2_leg_series(data, c) for c in CANDIDATES}
    b1 = {c: b1_leg_series(data, c) for c in CANDIDATES}
    days = sorted(b2[CANDIDATES[0]])
    if any(sorted(s) != days for s in list(b2.values()) + list(b1.values())):
        raise ValueError("the series do not cover the same days")
    record_963 = json.loads(RECORD_963.read_text(encoding="utf-8"))
    if record_963["series"]["days"] != len(days):
        raise ValueError(f"{len(days)} days here and {record_963['series']['days']} in #963's record")
    values = {leg: {c: [s[c][d] for d in days] for c in CANDIDATES} for leg, s in (("b2", b2), ("b1", b1))}
    jobs = [(f"{leg}|{c}", n, g, values[leg][c]) for leg in ("b2", "b1") for c in CANDIDATES for n in WINDOW_DAYS for g in GENERATORS]
    cells: Dict[str, Dict] = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for (key, n, g), cell in pool.map(_job, jobs):
            cells.setdefault(key, {}).setdefault(str(n), {})[g] = cell
    for c in CANDIDATES:
        for n in WINDOW_DAYS:
            for g in GENERATORS:
                got, was = cells[f"b1|{c}"][str(n)][g]["c"], record_963["calibration"][c][str(n)][g]["c"]
                if abs(got - was) > REPRODUCTION_TOLERANCE:
                    raise ValueError(f"the B1 leg of {c} at {n} days ({g}) gives c = {got} here and {was} in #963's record")
    record = {
        "declaration_sha256": c963.sha256(DECLARATION), "panel_sha256": c963.sha256(args.published), "seed": c963.SEED,
        "level": c963.LEVEL, "windows": c963.WINDOWS, "window_days": list(WINDOW_DAYS),
        "in_force": {str(k): v for k, v in IN_FORCE.items()}, "draft_953": {str(k): v for k, v in DRAFT_953.items()},
        "series": {"days": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "mean_d": {leg: {c: sum(v) / len(v) for c, v in per.items()} for leg, per in values.items()},
        "cells": cells, "b1_leg_reproduces_963": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "days": len(days)}))
    return 0


# -- the report -------------------------------------------------------------------------------------------------------------

f, pct = c963.f, c963.pct


def render(record) -> str:
    cells = record["cells"]
    n = record["series"]["days"]
    c250 = {(leg, c): cells[f"{leg}|{c}"]["250"]["contiguous"]["c"] for leg in ("b1", "b2") for c in CANDIDATES}
    L = [
        "# The B2 leg of \"Supported\" on contiguous post-2020 windows (#1015, H1 step 3)", "",
        "**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.CRITICAL_VALUES`, "
        "`docs/decisions/scoring-protocol.md` and the draft amendment of PR #953 are only read. No day after 2025-12-31 and no lockbox day "
        "is scored. Everything is declared in `metadata/b2_leg_contiguous_1015.json` before any score and read from "
        "`docs/research/b2-leg-contiguous-1015/result.json` by `scripts/b2_leg_contiguous_1015.py report`. It adds to the page of #963 "
        "(`contiguous-calibration-963-result.md`), which stands: that page reads only the leg against B1.", "",
        "## Questions for Eleonora (marked)", "",
        "1. **Does the 250-day confirmation window stay, given both legs?** The readings below apply #963's declared rules to each leg; "
        "the design is hers.",
        "2. **Is the joint reading (the worse of the two legs) the one to use,** or should a joint rule be written? It is stated here as "
        "the plain consequence of \"Supported\" needing both legs, not decided.", "",
        "## Series", "",
        f"{n} decision days {record['series']['first']} to {record['series']['last']}, the days of #963's page. The leg against B1 "
        "is d = S(B1) - S(candidate); the leg against B2 is d = S(B2) - S(candidate); both positive when the candidate is better. "
        "The recomputed leg against B1 reproduces #963's recorded c in every cell (to 1e-9).", "",
        "| candidate | mean d, leg against B1 | mean d, leg against B2 |", "|---|---|---|",
    ]
    for c in CANDIDATES:
        L.append(f"| {c} | {f(record['mean_d']['b1'][c], 3)} | {f(record['mean_d']['b2'][c], 3)} |")
    L += ["", "## 1. Critical values of the leg against B2", "",
          f"c is the {1 - record['level']:.2f} quantile of the window statistics. Size is the share of the generator's windows above the value: "
          f"in force (125 days {record['in_force']['125']:.3f}; 250 days {record['in_force']['250']:.3f}; 500 days has none and is read at the "
          f"250-day value) and the draft values of PR #953 for this leg (125 days {record['draft_953']['125']:.3f}; 250 days "
          f"{record['draft_953']['250']:.3f}; 500 days read at the 250-day value). The draft is not in force.", "",
          "| candidate | days | non-overlapping | c contiguous | c stationary-10 | c circular-10 | size in force, contiguous | size in force, "
          "stationary-10 | size in force, circular-10 | size at draft, contiguous | size at draft, stationary-10 | size at draft, circular-10 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in CANDIDATES:
        for days in map(str, record["window_days"]):
            row = cells[f"b2|{c}"][days]
            L.append(f"| {c} | {days} | {f(row['contiguous']['effective_windows'], 1)} | "
                     + " | ".join(f(row[g]["c"], 2) for g in GENERATORS) + " | "
                     + " | ".join(pct(row[g]["size_in_force"]) for g in GENERATORS) + " | "
                     + " | ".join(pct(row[g]["size_draft_953"]) for g in GENERATORS) + " |")
    L += ["", "## 2. Readings (#963's rule, declared)", "",
          f"Survives below {SURVIVES_BELOW}, fails above {FAILS_ABOVE}, neither rule applies between; on the contiguous-window c at 250 days. "
          "\"Supported\" needs both legs, so the joint reading is the worse of the two.", "",
          "| candidate | c, leg against B1 | reading | c, leg against B2 | reading | joint reading |", "|---|---|---|---|---|---|"]
    for c in CANDIDATES:
        a, b = c250[("b1", c)], c250[("b2", c)]
        L.append(f"| {c} | {a:.2f} | {reading(a)} | {b:.2f} | {reading(b)} | {joint_reading(a, b)} |")
    L += ["", "## Limits", "",
          "Development data seen before the declaration. Contiguous windows overlap heavily, so a quantile of them rests on a handful of "
          "independent stretches; the non-overlapping count says how few. B1' (#960) has not replaced B1, as in #963. The draft values of "
          "#953 are read as a comparison; whether they are adopted is hers. Nothing here is registered or changed.", ""]
    return "\n".join(L)


def report_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(record), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args) -> int:
    if not RECORD.exists():
        print("no record yet: `run` and `report` have not been run", file=sys.stderr)
        return 1
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(record):
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
    run.add_argument("--workers", type=int, default=4)
    run.set_defaults(func=run_command)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
