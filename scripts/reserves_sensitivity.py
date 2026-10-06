#!/usr/bin/env python3
"""How far reserves and the TGA move the published forecast (#267, second review finding 15).

The published declaration reads `reserve_balances` and `tga` as two of its nine
features. A tree model is flat outside the range it was trained on, so a drain
of reserves or a swollen TGA at 2026-27 levels may reach the forecast hardly at
all. This script measures that: it fits the published gbm (uncalibrated; the
conformal PID shifts the quantiles by a scorecaster on past errors, not by these
two inputs) once per day's fold, then re-reads the last day's feature
row with `reserve_balances` and `tga` set across a grid, everything else held at
the day's reads, and reports the largest change of any quantile against the
unchanged read, on each of `SCORED_DAYS`. It scores no day: every fold is in
2025, inside `docs/decisions/lockbox.md`.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/reserves_sensitivity.py \\
        --panel /tmp/funding_panel.csv --output /tmp/reserves_sensitivity.json

Reserves and the TGA are in USD billions in the panel. The grid is the plausible
2026-27 range: reserves 2800 to 3500, TGA 500 to 1100.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

import live_record as live  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import _AsOfFold, _at_decision, _fit_at_origin, _reads_information  # noqa: E402
from repo_model.data import DailyObservation, load_daily_panel  # noqa: E402

#: Ordinary days and the two quarter-ends of the last pre-2026 half-year; all inside the lockbox.
SCORED_DAYS = (date(2025, 7, 15), date(2025, 9, 30), date(2025, 10, 15), date(2025, 11, 14),
               date(2025, 12, 15), date(2025, 12, 31))
RESERVES_GRID = (2800.0, 3000.0, 3200.0, 3500.0)
TGA_GRID = (500.0, 700.0, 900.0, 1100.0)
#: The finding's claim: no read in the grid moves any quantile by more than this, in bp.
CLAIM_BP = 0.3


def measure(panel: Path, day: date) -> dict:
    rows = [row for row in load_daily_panel(panel) if row.date <= day]
    registry = json.loads((REPO / "metadata" / "sources.json").read_text())
    sides, args = live._compare_sides(1)
    _name, fit, features, _online = sides["published"]
    rule = InformationRule(registry, tuple(features), decision_time=live.DECISION, horizon=1)
    dates = [row.date for row in rows]
    index = len(rows) - 1
    info = rule.information_set(dates, index)
    rule.check(dates, info)
    frame = rule.frame(rows, info)
    fitted = _fit_at_origin(fit, frame, minimum_history=args.minimum_history,
                            information=rule, reads_information=_reads_information(fit))
    fold = _AsOfFold(index, info, frame, rule.observation(rows, info))
    view = _at_decision(fitted, rows, rule, fold)
    base_row = fold.feature_row
    base = [float(v) for v in view.predict(base_row)]
    levels = list(view.levels)
    trained = {name: (min(r.values[name] for r in frame if r.values.get(name) is not None),
                      max(r.values[name] for r in frame if r.values.get(name) is not None))
               for name in ("reserve_balances", "tga")}
    cells = []
    worst = 0.0
    for reserves in RESERVES_GRID:
        for tga in TGA_GRID:
            row = DailyObservation(base_row.date, {**base_row.values, "reserve_balances": reserves,
                                                   "tga": tga})
            moved = [float(v) for v in view.predict(row)]
            delta = max(abs(a - b) for a, b in zip(moved, base))
            worst = max(worst, delta)
            cells.append({"reserve_balances": reserves, "tga": tga, "max_abs_quantile_change_bp": delta})
    return {"scored_day": day.isoformat(), "levels": levels, "base_quantiles_bp": base,
            "base_reserve_balances": base_row.values["reserve_balances"], "base_tga": base_row.values["tga"],
            "trained_range": trained, "grid": cells, "worst_change_bp": worst,
            "claim_bp": CLAIM_BP, "claim_holds": worst <= CLAIM_BP}


def measure_all(panel: Path) -> dict:
    days = [measure(panel, day) for day in SCORED_DAYS]
    return {"days": days, "worst_change_bp": max(d["worst_change_bp"] for d in days),
            "worst_change_bp_by_day": {d["scored_day"]: d["worst_change_bp"] for d in days}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = measure_all(args.panel)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("worst_change_bp", "worst_change_bp_by_day")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
