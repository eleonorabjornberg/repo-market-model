#!/usr/bin/env python3
"""A dated correction of #853's ordinary-day page (#934; H5 step 3, development tier).

Eleonora's ruling on #917 (19 October 2026): #853's ordinary-day result is reported within each regime, and no pooled gain is
claimed. This renders that restatement from the committed score of #844; it scores nothing again, and it edits neither
`docs/pivot/ordinary-day-p5-844/report.md` nor `docs/pivot/ordinary-day-p5-result.md`.

    PYTHONPATH=src python3 scripts/ordinary_day_p5_934.py --output docs/pivot/ordinary-day-p5-844/correction-934.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
SCORE = ROOT / "docs" / "pivot" / "ordinary-day-p5-844" / "score.json"

_spec = importlib.util.spec_from_file_location("ordinary_day_p5_844", ROOT / "scripts" / "ordinary_day_p5_844.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

REGIMES = tuple(cell for cell in base.CELLS if cell != "pooled")


def _cell(result: dict, h: int, cell: str) -> Optional[dict]:
    return result["definitions"]["non_ordinary"].get(str(h), {}).get(cell)


def render(result: dict) -> str:
    level = round(result["level"] * 100)
    out = [
        "# Correction of the ordinary-day page (#844, PR #853): the result within each regime (#934)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3. **Development data only: this is not a verdict** (scoring protocol v1, #640). "
        "Dated 19 October 2026, on Eleonora's ruling on #917: the ordinary-day result is reported within each regime, and "
        "**no pooled gain is claimed**. What counts as a ranking gain for H5's kill clause stays Eleonora's.", "",
        "This page corrects how `docs/pivot/ordinary-day-p5-result.md` and `docs/pivot/ordinary-day-p5-844/report.md` read; both stand as "
        "published and neither is edited. Nothing is scored again: every figure below is read from "
        f"`docs/pivot/ordinary-day-p5-844/score.json`, the {level}% stationary-bootstrap percentile intervals (block {result['block_length']}, "
        f"{result['replications']} replications) and the seed of that run. Each cell is the paired AUROC difference from persistence-logistic "
        "on ordinary target days (not a risk date under `risk_dates.NON_ORDINARY`); above zero is better than persistence-logistic. "
        "`n/a`: fewer than 3 pressure days. `†`: no interval.", "",
    ]
    for name in base.MODEL_ROWS:
        out += [f"## {base.LABELS[name]}", "", "| lead | " + " | ".join(REGIMES) + " |", "|---|" + "---|" * len(REGIMES)]
        for h in base.HORIZONS:
            cells = []
            for regime in REGIMES:
                body = _cell(result, h, regime)
                if body is None or body["pressure_days"] < base.MINIMUM_PRESSURE_DAYS:
                    cells.append("n/a")
                    continue
                entry = body["rows"][name]["auroc_minus_reference"]
                cells.append(f"{base.fmt(entry, signed=True)} ({body['pressure_days']} pressure days)")
            out.append(f"| {h} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["## Tally of regime-by-lead cells (development)", "", *base.kill_lines(result), "",
            "These lines count cells; they set no threshold.", ""]
    rows, exceeds = [], 0
    for name in base.MODEL_ROWS:
        for h in base.HORIZONS:
            pooled = _cell(result, h, "pooled")["rows"][name]["auroc_minus_reference"]
            regimes = []
            for regime in REGIMES:
                body = _cell(result, h, regime)
                if body is not None and body["pressure_days"] >= base.MINIMUM_PRESSURE_DAYS:
                    entry = body["rows"][name]["auroc_minus_reference"]
                    if entry is not None and entry["value"] is not None:
                        regimes.append(entry["value"])
            if pooled is None or pooled["value"] is None or not regimes:
                continue
            above = pooled["value"] > max(regimes)
            exceeds += above
            rows.append(f"| {base.LABELS[name]} | {h} | {base.fmt(pooled, signed=True)} | {max(regimes):+.3f} | {'yes' if above else 'no'} |")
    out += ["## Why the pooled rows are not read as a gain (#917)", "",
            "A pooled paired AUROC difference larger than the difference in every one of its regimes can only come from pairs that cross "
            "regimes: a 2018-19 pressure day ranked above a calm day of 2020-24. Most pressure days are in 2018-19 (61 of 81 at lead 1) and "
            "2020-24 has 5, so such a gain reflects the 2018-19 base-rate gap, not ranking within a regime. "
            f"In {exceeds} of {len(rows)} model-by-lead rows below the pooled difference exceeds every regime's. "
            "The pooled rows are shown only to show this; they are not claimed.", "",
            "| model | lead | pooled (not claimed) | largest regime difference | pooled above every regime |", "|---|---|---|---|---|", *rows]
    out.append("")
    return "\n".join(out)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score", default=str(SCORE))
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    result = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
