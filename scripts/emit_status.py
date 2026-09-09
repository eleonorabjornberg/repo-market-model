#!/usr/bin/env python3
"""Emit docs/status.json: the machine-readable status this repository publishes.

Everything here is measured from the repository except the two constants below,
which record a judgement no script can make: which phase of PLAN.md is current
and whether it is finished. Bump those when a phase lands; nothing else in this
file needs editing.

The date is the commit date of HEAD, never today's date. A status page that can
run ahead of the work it describes is the failure this repository exists to
prevent, and that includes the copy of it published on a website.

Standard library only.

    python3 scripts/emit_status.py            # writes docs/status.json
    python3 scripts/emit_status.py --check    # prints it, writes nothing
"""
import json
import re
import subprocess
import sys
from pathlib import Path

CURRENT_PHASE = 0
CURRENT_STATE = "complete"          # "complete" or "in progress"

# Transcribed once from PLAN.md. A roadmap does not go stale between commits the
# way a measured figure does; if PLAN.md is renumbered, renumber this with it.
PHASES = [
    (0, "Reproducible foundation",
     "one command validates a panel and produces a leakage-safe baseline backtest"),
    (1, "Point-in-time public dataset",
     "frozen checksummed snapshots with provenance and a data-quality report"),
    (2, "Benchmarks and probabilistic models",
     "beats persistence out of sample and stays calibrated in the tails"),
    (3, "Latent reserves and payment needs",
     "stable posterior intervals for aggregate effective liquidity"),
    (4, "Supply, demand and market clearing",
     "coherent rate and volume predictions plus transparent counterfactuals"),
    (5, "Missing-data and network ensemble",
     "mask-and-reconstruct recovers held-out edges and identities within tolerance"),
    (6, "Stress engine",
     "historical replay and sensitivity reports"),
    (7, "European extension",
     "currency, sovereign issuer, collateral eligibility, CCP/CSD and cross-border settlement are represented"),
]

ROOT = Path(__file__).resolve().parent.parent


def git(*args):
    return subprocess.run(("git",) + args, cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def dependency_count():
    """Count declared runtime dependencies. The claim is zero; measure it."""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^dependencies\s*=\s*\[(.*?)\]", text, re.S | re.M)
    if not match:
        return 0
    return len([item for item in match.group(1).split(",") if item.strip()])


def main():
    manifest = json.loads((ROOT / "docs/runs/funding_panel.manifest.json").read_text(encoding="utf-8"))
    events = json.loads((ROOT / "metadata/events.json").read_text(encoding="utf-8"))

    phase = next(p for p in PHASES if p[0] == CURRENT_PHASE)
    following = next((p for p in PHASES if p[0] == CURRENT_PHASE + 1), phase)

    status = {
        "generated_at": git("log", "-1", "--format=%cd", "--date=short"),
        "commit": git("rev-parse", "--short", "HEAD"),
        "phase": {"number": phase[0], "name": phase[1], "state": CURRENT_STATE},
        "next": {"number": following[0], "name": following[1], "exit": following[2]},
        "figures": {
            "panel_start": manifest["start_date"],
            "panel_end": manifest["end_date"],
            "panel_rows": manifest["row_count"],
            "event_holdouts": len(events["windows"]),
            "dependencies": dependency_count(),
        },
        "run_records": sorted(p.name for p in (ROOT / "docs/runs").glob("*.json")),
    }

    text = json.dumps(status, indent=2, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        sys.stdout.write(text)
        return
    (ROOT / "docs/status.json").write_text(text, encoding="utf-8")
    print("wrote docs/status.json — phase %d (%s), %s, at %s"
          % (phase[0], phase[1], CURRENT_STATE, status["generated_at"]))


if __name__ == "__main__":
    main()
