"""What the market-day tax window moved: two `risk_date_false_alarm_controls.py summary` tables side by side (#538).

    PYTHONPATH=src python3 scripts/tax_date_market_days_delta.py OLD/summary.md NEW/summary.md --output delta.md

A scratch measurement. Each row is a candidate of the two tables; a cell is printed as `old -> new` where it moved
and as the plain value where it did not. The rows are the five risk-date passers and their `+gate` variants.
"""

from __future__ import annotations

import argparse
from pathlib import Path

PASSERS = ("risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base")


def read(path: Path):
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("|")]
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows = {}
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows[cells[0]] = cells
    return header, rows


def wanted(name: str) -> bool:
    return name in PASSERS or (name.endswith("+every_day+gate") and name.split("+")[0] in PASSERS) or name in tuple(
        f"{p}+every_day" for p in PASSERS
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    header, old = read(args.old)
    new_header, new = read(args.new)
    if header != new_header or old.keys() != new.keys():
        raise SystemExit("the two summaries do not describe the same rows")
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for name in old:
        if not wanted(name):
            continue
        cells = [name] + [a if a == b else f"{a} -> {b}" for a, b in zip(old[name][1:], new[name][1:])]
        out.append("| " + " | ".join(cells) + " |")
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
