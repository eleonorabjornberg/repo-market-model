#!/usr/bin/env python3
"""H5 step 4 on the two panels Eleonora named (#904, ruling of 19 October 2026, option (c) on #900): the plan for her Mac.

Development tooling, never a claim and never a verdict (scoring protocol v1, #46). It scores nothing itself: it plans and
runs the commands that do, and refuses a panel whose digest is not the ruled one. `scripts/h5_step4_758.py`,
`scripts/upper_bound_635.py` and `scripts/spread_distribution_634.py` run unchanged, and no declaration is edited.

* `ec534758` is H2's record commit; its chain gives `1e5b748a…` (#903), not H2's `08df8d19…`.
* `71cf91d2` is the commit #903 calls main; its chain gives `69f22bc6…`, the panel the ruling names as main's. Main's chain has
  moved since (`source_screen` and the steps before it differ), so the head of main does not give that digest.

The walks read the published panel and `AUG2D`, which are byte-identical at both commits, so they are made once; only
the cross-fitted ceiling and the reachable line (`upper_bound_635.py fit`) are refit on each `DERIV.csv`. The fit takes
about three hours on three cores and each walk 15 to 40 minutes (`docs/pivot/h5-step4-result.md`): this is a needs-mac run.

    PYTHONPATH=src python3 scripts/h5_step4_904.py plan --workdir OUT        # print the commands
    PYTHONPATH=src python3 scripts/h5_step4_904.py run --workdir OUT         # run them, skipping a step whose output exists
    PYTHONPATH=src python3 scripts/h5_step4_904.py chain --commit 71cf91d2 --workdir OUT/main_71cf91d2   # one panel only
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = "0.01"
VARIANTS = ("gbm_funding", "c_two_part_new")
LEADS = (1, 2, 3, 4, 5)
#: the published panel and `AUG2D`, the same bytes at every commit #903 built
PUBLISHED_DIGEST = "4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999"
AUG2D_DIGEST = "73534301328be94872f5408e28ead65466847d6f69bd1cb39a15a72a3f97bc3f"
EVIDENCE = Path("docs") / "pivot" / "evidence" / "h5-step4-904"


@dataclass(frozen=True)
class Panel:
    name: str
    commit: str
    digest: str  # the sha256 of `DERIV.csv` the ruling names


PANELS = (
    Panel("h2_record_ec534758", "ec534758", "1e5b748a00ad6334e09f39b3b4135db969da5d32218f66dae3572fb8fca10e34"),
    Panel("main_71cf91d2", "71cf91d2", "69f22bc66efb349375f9ee8577031ba382a1be8954a96472d5600591952efabe"),
)


@dataclass(frozen=True)
class Item:
    name: str
    argv: List[str]
    produces: Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_panel(panel: Panel, path: Path) -> None:
    """Refuse a `DERIV.csv` whose digest is not the one the ruling names for this panel (`ValueError`)."""

    found = sha256(path)
    if found != panel.digest:
        raise ValueError(f"{path} has digest {found[:8]}…; the ruling names {panel.digest[:8]}… for {panel.name} (commit {panel.commit})")


def plan(workdir: Path) -> List[Item]:
    script = lambda name: str(ROOT / "scripts" / name)  # noqa: E731
    first = workdir / PANELS[0].name
    items: List[Item] = []
    for panel in PANELS:
        items.append(Item(f"chain:{panel.name}", [sys.executable, script("h5_step4_904.py"), "chain", "--commit", panel.commit, "--workdir", str(workdir / panel.name)], workdir / panel.name / "DERIV.csv"))
    for variant in VARIANTS:
        for lead in LEADS:
            out = workdir / "walks" / f"{variant}_h{lead}.json"
            items.append(Item(f"walk:{variant}_h{lead}", [sys.executable, script("spread_distribution_634.py"), "walk", "--variant", variant, "--horizon", str(lead),
                                                       "--published", str(first / "PUB.csv"), "--panel", str(first / "AUG2D.csv"), "--output", str(out)], out))
    for panel in PANELS:
        base = workdir / panel.name
        items.append(Item(f"fit:{panel.name}", [sys.executable, script("upper_bound_635.py"), "fit", "--panel", str(base / "DERIV.csv"), "--output", str(base / "fits.json")], base / "fits.json"))
    for panel in PANELS:
        base = workdir / panel.name
        items.append(Item(f"score:{panel.name}", [sys.executable, script("h5_step4_758.py"), "score", "--published", str(first / "PUB.csv"), "--fits", str(base / "fits.json"),
                                                  "--walks", str(workdir / "walks"), "--tolerance", TOLERANCE, "--output", str(base / "score.json")], base / "score.json"))
        items.append(Item(f"report:{panel.name}", [sys.executable, script("h5_step4_758.py"), "report", str(base / "score.json"), "--output", str(base / "report.md")], base / "report.md"))
    return items


def environment() -> dict:
    env = dict(os.environ)
    env.update(PYTHONPATH=str(ROOT / "src"), PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    return env


def build_chain(commit: str, workdir: Path) -> None:
    """Build the chain of #903 in a detached worktree at `commit` (with this tree's `deriv_chain_903.py`) and check the digests."""

    panel = next(p for p in PANELS if p.commit == commit)
    workdir.mkdir(parents=True, exist_ok=True)
    tree = workdir / "worktree"
    if not tree.exists():
        subprocess.run(["git", "worktree", "add", "--detach", str(tree), commit], cwd=ROOT, check=True)
    shutil.copy(ROOT / "scripts" / "deriv_chain_903.py", tree / "scripts" / "deriv_chain_903.py")
    subprocess.run([sys.executable, str(tree / "scripts" / "deriv_chain_903.py"), "run", "--workdir", str(workdir), "--digests", str(workdir / "digests.json")],
                   cwd=tree, env={**environment(), "PYTHONPATH": str(tree / "src")}, check=True)
    for name, digest in (("PUB", PUBLISHED_DIGEST), ("AUG2D", AUG2D_DIGEST)):
        if sha256(workdir / f"{name}.csv") != digest:
            raise ValueError(f"{name}.csv at {commit} is not the panel the walks of #758 read ({digest[:8]}…)")
    verify_panel(panel, workdir / "DERIV.csv")


def run(workdir: Path) -> None:
    for item in plan(workdir):
        if item.produces.exists():
            print(f"skip {item.name}: {item.produces} exists", flush=True)
            continue
        item.produces.parent.mkdir(parents=True, exist_ok=True)
        print(f"run  {item.name}", flush=True)
        subprocess.run(item.argv, cwd=ROOT, env=environment(), check=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "run"):
        p = sub.add_parser(name)
        p.add_argument("--workdir", type=Path, required=True)
    p = sub.add_parser("chain")
    p.add_argument("--commit", required=True, choices=[panel.commit for panel in PANELS])
    p.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "plan":
        for item in plan(args.workdir):
            print(f"# {item.name}\n" + " ".join(item.argv))
    elif args.command == "run":
        run(args.workdir)
    else:
        build_chain(args.commit, args.workdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
