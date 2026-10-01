#!/usr/bin/env python3
"""How far the calibration masking of `information-set.md`'s Method notes reaches.

The decision's Method notes accept one bias and bound it without sizing it: a
cross-conformal fit trains each block's excluding model on the frame as masked
at the **fold's** decision instant, not at each held-out row's. A declared
column slower than the target (the H.4.1 weeklies, `reserve_balances` and
`tga`) can therefore carry, on an excluding model's training rows, a value that
was public by the fold's decision but not yet by a held-out row's. Directive 03
(#27, Eleonora's comment) asks for the size of that bias on the calibrated
records with such a column, or a statement that none apply.

This measures its **exposure**, not its effect on the scores: for every refit
block of the as-of grid, every cross-conformal block of that fit's frame, and
every training pair its excluding model fits on rows *before* the block, the
pair is exposed when its origin row carries a slow declared value that is in
the frame (public at the fold's decision) but was not yet observable at the
decision instant of the block's first held-out row. The first held-out row has
the earliest decision in the block, so this counts the most pairs any held-out
row of the block could see; later rows see fewer. Rows *after* the block are
not counted: CV+ trains on them by construction, their labels included, and
the Method note is about the declared columns only.

Standard library only. Reads the panel, the registry and the declaration's
features; writes nothing.

    PYTHONPATH=src python3 scripts/calibration_masking_exposure.py PANEL \\
        --feature reserve_balances --feature tga ... --minimum-history 61 \\
        --refit-every 21 --calibration-folds 5
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from repo_model.asof import InformationRule, fold_grid, refit_blocks  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402

KIND_OBSERVED = "observed"


def exposure(rows, rule, *, minimum_history, refit_every, folds):
    dates = [row.date for row in rows]
    slow = [
        group
        for group in rule.groups[1:]
        if group.kind == KIND_OBSERVED and group.fields != rule.groups[0].fields
    ]
    grid = fold_grid(
        dates, rule.registry, decision_time=rule.decision_time, minimum_history=minimum_history
    )
    total_pairs = 0
    exposed_pairs = 0
    exposed_by_column = {}
    worst = 0
    fits = 0
    for block in refit_blocks(grid, refit_every):
        first = block[0]
        info = rule.information_set(dates, first)
        frame = rule.frame(rows, info)
        frame_dates = [row.date for row in frame]
        n = len(frame)
        bounds = [n * number // folds for number in range(folds + 1)]
        fit_exposed = 0
        for number in range(folds):
            start = bounds[number]
            if start <= 0:
                continue
            before = rule.anchor(frame_dates, start)
            held_out_decision = rule.decision_instant(frame_dates, start)
            for origin in range(0, max(0, before)):
                # A pair (origin, origin + 1), both at or before `before`.
                total_pairs += 1
                late = []
                for group in slow:
                    values = [frame[origin].values.get(column) for column in group.columns]
                    if any(value is None for value in values):
                        continue
                    if rule.availability(frame_dates, group.fields, origin) > held_out_decision:
                        late.extend(group.columns)
                if late:
                    exposed_pairs += 1
                    fit_exposed += 1
                    for column in late:
                        exposed_by_column[column] = exposed_by_column.get(column, 0) + 1
        worst = max(worst, fit_exposed)
        fits += 1
    return {
        "fits": fits,
        "calibration_folds": folds,
        "observed_columns_checked": sorted({c for group in slow for c in group.columns}),
        "pairs_before_held_out_blocks": total_pairs,
        "exposed_pairs": exposed_pairs,
        "exposed_share": exposed_pairs / total_pairs if total_pairs else 0.0,
        "exposed_pairs_by_column": dict(sorted(exposed_by_column.items())),
        "most_exposed_pairs_in_one_fit": worst,
        "what_is_counted": (
            "excluding-model training pairs before a held-out block whose origin row "
            "carries a declared value public at the fold's decision but not at the "
            "block's first held-out row's decision; an upper bound for every held-out "
            "row of the block. Exposure only: the effect on calibration scores is not "
            "measured here."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("panel", type=Path)
    parser.add_argument("--registry", type=Path, default=ROOT / "metadata" / "sources.json")
    parser.add_argument("--feature", action="append", required=True)
    parser.add_argument("--decision-time", default="16:00")
    parser.add_argument("--minimum-history", type=int, required=True)
    parser.add_argument("--refit-every", type=int, required=True)
    parser.add_argument("--calibration-folds", type=int, default=5)
    args = parser.parse_args(argv)
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    rows = load_daily_panel(args.panel)
    rule = InformationRule(
        registry, tuple(args.feature), decision_time=time.fromisoformat(args.decision_time)
    )
    result = exposure(
        rows,
        rule,
        minimum_history=args.minimum_history,
        refit_every=args.refit_every,
        folds=args.calibration_folds,
    )
    result["features"] = sorted(args.feature)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
