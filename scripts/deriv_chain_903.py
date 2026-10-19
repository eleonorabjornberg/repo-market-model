#!/usr/bin/env python3
"""The chain that builds H2's scratch panel `DERIV.csv`, with a digest for every step (#903, H2 step 3, finding #900).

Development tooling. It writes under the directory it is given and nothing into `docs/runs/`; it scores nothing.
The steps are those of `docs/pivot/derived-features-result.md` (Reproduce), in the order of finding #900, with
`satiation_distance_598.py panel` between `measurement_fields.py panel` and `net_settlement.py panel`:

    PYTHONPATH=src python3 scripts/deriv_chain_903.py run --workdir OUT --digests OUT/digests.json
    PYTHONPATH=src python3 scripts/deriv_chain_903.py run --workdir OUT --end 2025-12-31 --stop-after AUG3
    PYTHONPATH=src python3 scripts/deriv_chain_903.py compare A/digests.json B/digests.json

`--end` is given to the steps that take one; without it each step keeps its own default end (at most 2026-09-03, #684).
`compare` names the first step whose output differs between two digest files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_CUTOFF = "2026-09-08T21:31:42+00:00"


@dataclass(frozen=True)
class Step:
    name: str
    script: str
    inputs: tuple  # (flag, step name that produced the file)
    takes_end: bool = True
    extra: tuple = ()  # further inputs: names, after `--extra`
    side_output: tuple = ()  # (flag, file name) of a summary the script also writes


STEPS = (
    Step("AUG", "pressure_v1_1.py", ()),
    Step("AUG2", "measurement_fields.py", (("--panel", "AUG"),)),
    Step("AUG2D", "satiation_distance_598.py", (("--panel", "AUG2"),)),
    Step("AUG3", "net_settlement.py", (("--panel", "AUG2D"),)),
    Step("AUG4", "policy_features.py", (("--panel", "AUG3"),), takes_end=False),
    Step("AUG5", "fed_liquidity.py", (("--panel", "AUG4"),)),
    Step("AUG6", "nowcast.py", (("--panel", "AUG5"),), side_output=("--summary", "nowcast_panel.json")),
    Step("DVP", "dvp_segment_inputs.py", (("--panel", "PUB"),)),
    Step("EW", "early_warning_inputs.py", (("--panel", "PUB"),)),
    Step("SCREEN", "source_screen.py", (("--panel", "AUG6"),), takes_end=False, extra=("DVP", "EW")),
    Step("DERIV", "derived_features_631.py", (("--panel", "SCREEN"),), takes_end=False),
)


def commands(workdir: Path, end: str | None = None):
    """Each step with the argument vector that runs it (the interpreter and script path included)."""
    out = []
    for step in STEPS:
        argv = [sys.executable, str(ROOT / "scripts" / step.script), "panel"]
        for flag, source in step.inputs:
            argv += [flag, str(workdir / f"{source}.csv")]
        if step.extra:
            argv += ["--extra"] + [str(workdir / f"{name}.csv") for name in step.extra]
        argv += ["--output", str(workdir / f"{step.name}.csv")]
        if step.side_output:
            argv += [step.side_output[0], str(workdir / step.side_output[1])]
        if end and step.takes_end:
            argv += ["--end", end]
        out.append((step, argv))
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment() -> dict:
    env = dict(os.environ)
    env.update(PYTHONPATH=str(ROOT / "src"), PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1",
               OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    return env


def run(workdir: Path, end: str | None = None, stop_after: str | None = None) -> dict:
    """Build the published panel from the tracked fixtures and then each step; return {step: sha256 of its output}."""
    workdir.mkdir(parents=True, exist_ok=True)
    env = environment()
    build = [sys.executable, "-m", "repo_model.cli", "build", "--raw-root",
             str(ROOT / "tests/fixtures/snapshots/funding_inputs"), "--output", str(workdir / "PUB.csv"),
             "--build-cutoff", BUILD_CUTOFF, "--decision-time", "16:00:00"]
    subprocess.run(build, cwd=ROOT, env=env, check=True, capture_output=True)
    digests = {"PUB": sha256(workdir / "PUB.csv")}
    for step, argv in commands(workdir, end):
        subprocess.run(argv, cwd=ROOT, env=env, check=True, capture_output=True)
        digests[step.name] = sha256(workdir / f"{step.name}.csv")
        if step.name == stop_after:
            break
    return digests


def first_difference(a: dict, b: dict) -> str | None:
    """The first step, in chain order, whose digest differs; None when the two agree on every step both hold."""
    for name in ["PUB"] + [step.name for step in STEPS]:
        if name in a and name in b and a[name] != b[name]:
            return name
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("run")
    one.add_argument("--workdir", type=Path, required=True)
    one.add_argument("--end")
    one.add_argument("--stop-after", choices=[step.name for step in STEPS])
    one.add_argument("--digests", type=Path)
    two = sub.add_parser("compare")
    two.add_argument("first", type=Path)
    two.add_argument("second", type=Path)
    args = parser.parse_args(argv)
    if args.command == "run":
        digests = run(args.workdir, args.end, args.stop_after)
        text = json.dumps(digests, indent=1) + "\n"
        if args.digests:
            args.digests.write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    first = json.loads(args.first.read_text())
    second = json.loads(args.second.read_text())
    moved = first_difference(first, second)
    print(f"first step that moves: {moved}" if moved else "no step moves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
