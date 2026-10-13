"""Before-and-after tables for the re-score after the partly announced class is left out (#679, finding #665).

A scratch measurement, not a record: it reads result documents and writes Markdown, nothing into `docs/runs/`.

    PYTHONPATH=src python3 scripts/audit_fixes_679.py report --before-ref origin/main --output docs/pivot/partly-announced-679-result.md

It is `scripts/audit_fixes_578.py report` over the documents #647 re-scored that read `net_settlement_*`: the structural, projected-reserves
and combined models. The #598 rows do not read the net settlement columns and are not re-scored. Before is the document at `--before-ref`;
after is the working tree.
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
    f"{EVIDENCE}/structural-liquidity/result.json": base.DOCUMENTS[f"{EVIDENCE}/structural-liquidity/result.json"],
    f"{EVIDENCE}/projected-reserves/result.json": base.DOCUMENTS[f"{EVIDENCE}/projected-reserves/result.json"],
    f"{EVIDENCE}/combined-model/compare.json": base.DOCUMENTS[f"{EVIDENCE}/combined-model/compare.json"],
}


def report(before_ref: str) -> str:
    base.DOCUMENTS = DOCUMENTS
    text = base.report(before_ref)
    return text.replace(
        "# Re-score after the audit's construction fixes (#578)", "# Re-score after leaving the partly announced class out (#679, finding #665)"
    ).replace("scripts/audit_fixes_578.py report", "scripts/audit_fixes_679.py report")


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
