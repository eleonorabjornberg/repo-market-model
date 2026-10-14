"""Before-and-after tables for the re-score of the satiation (#587) and kinked (#626) pages after #618 and #679 (#691, finding #673).

A scratch measurement, not a record: it reads result documents and writes Markdown, nothing into `docs/runs/`.

    PYTHONPATH=src python3 scripts/declarations_691.py report --before-ref origin/main --output docs/pivot/declarations-691-result.md

It is `scripts/audit_fixes_578.py report` over the two comparison documents the re-score rewrote. Before is the document at `--before-ref`
(scored on the five-day sum and the old netting); after is the working tree (the drain columns of #618 and the rule of #679).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("audit_fixes_578_base", REPO / "scripts" / "audit_fixes_578.py")
base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = base
_spec.loader.exec_module(base)

EVIDENCE = base.EVIDENCE
DOCUMENTS = {
    f"{EVIDENCE}/satiation/compare.json": (
        "A time-varying satiation level (#587)",
        (
            "structural_liquidity", "structural_rolling", "structural_fitted", "projected_reserves", "projected_hinge_fixed",
            "projected_rolling", "projected_fitted", "risk_gbm+combined", "risk_gbm+combined_hinge_fixed",
            "risk_gbm+combined_rolling", "risk_gbm+combined_fitted",
        ),
    ),
    f"{EVIDENCE}/kinked/compare.json": (
        "A kinked elasticity (#626)",
        ("structural_liquidity", "structural_liquidity+h41", "structural_kinked_rolling", "structural_kinked_fitted"),
    ),
}


def report(before_ref: str) -> str:
    base.DOCUMENTS = DOCUMENTS
    text = base.report(before_ref)
    return text.replace(
        "# Re-score after the audit's construction fixes (#578)", "# Re-score of the satiation and kinked pages (#691, finding #673)"
    ).replace("scripts/audit_fixes_578.py report", "scripts/declarations_691.py report")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    rep = commands.add_parser("report")
    rep.add_argument("--before-ref", default="origin/main")
    rep.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    args.output.write_text(report(args.before_ref), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
