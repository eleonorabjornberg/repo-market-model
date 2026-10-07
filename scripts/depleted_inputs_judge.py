"""Judge the ON RRP depletion inputs against the rule declared in `docs/pivot/depleted-inputs-test.md` (#132).

Reads the outputs of `scripts/pressure_v1_1.py` for the run `conditional_scarcity`: `crps_conditional_scarcity.json`
(`crps`) and `pair_conditional_scarcity_h1.json` (`pair`), both scored on days before 2026-01-01.

    python3 scripts/depleted_inputs_judge.py --runs OUT --output docs/pivot/evidence/depleted-inputs/depleted_inputs.json

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

RUN = "conditional_scarcity"
LAST = date(2025, 12, 31)
MINIMUM_CELL_DAYS = 20
BENCHMARK = "pressure_model_v1"


def cell_verdict(entry: dict) -> str:
    if entry["count"] < MINIMUM_CELL_DAYS:
        return "too few days"
    if entry["interval"]["upper"] < 0:
        return "worse beyond its interval"
    return "ok"


def judge(name: str, mean: float, interval: dict, splits: dict) -> dict:
    """The declared rule for one figure: the pooled gate and its cells."""

    cells = {}
    for split in ("by_regime", "by_day_type"):
        for key, entry in splits[split].items():
            cells[f"{split}/{key}"] = cell_verdict(entry)
    worse = sorted(k for k, v in cells.items() if v == "worse beyond its interval")
    return {"figure": name, "mean": mean, "interval": {"lower": interval["lower"], "upper": interval["upper"]},
            "gate": bool(mean > 0 and interval["lower"] > 0), "cells": cells, "cells_worse_beyond_interval": worse}


def decide(figures: dict) -> bool:
    decisive = [figures["crps_bps"], figures["brier_+5bp"], figures["brier_+10bp"]]
    return all(f["gate"] and not f["cells_worse_beyond_interval"] for f in decisive)


def assemble(crps_document: dict, pair_document: dict) -> dict:
    comparison = crps_document["comparison"]
    if max(o["scored_date"] for o in comparison["per_origin"]) > LAST.isoformat():
        raise ValueError("the CRPS comparison scored a locked day")
    figures = {"crps_bps": judge("crps_bps", comparison["mean_difference_bps"],
                                 comparison["mean_difference_interval"], comparison["splits"])}
    for tau in (5, 10):
        entry = pair_document["entries"][f"{RUN}|brier|all_days|{tau}|1|{BENCHMARK}"]
        figures[f"brier_+{tau}bp"] = judge(f"brier_+{tau}bp", entry["mean"], entry["interval"], entry["splits"])
    return {
        "directive": "#132",
        "declared_in": "docs/pivot/depleted-inputs-test.md",
        "window": [min(o["scored_date"] for o in comparison["per_origin"]),
                   max(o["scored_date"] for o in comparison["per_origin"])],
        "days": comparison["origin_count"],
        "mean_crps_bps": {"published": comparison["model_a"]["crps_bps"],
                          "candidate": comparison["model_b"]["crps_bps"]},
        "figures": figures,
        "joins_published_declaration": decide(figures),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    crps_document = json.loads((args.runs / f"crps_{RUN}.json").read_text())
    pair_document = json.loads((args.runs / f"pair_{RUN}_h1.json").read_text())
    document = assemble(crps_document, pair_document)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"joins": document["joins_published_declaration"],
                      "figures": {k: {"mean": v["mean"], **v["interval"], "gate": v["gate"],
                                      "worse": v["cells_worse_beyond_interval"]}
                                  for k, v in document["figures"].items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
