#!/usr/bin/env python3
"""The onset-day blend candidate (#160), scored once against the published pressure model v1 at h = 1.

A scratch measurement, not a record: it writes JSON to the path it is given and nothing into `docs/runs/`.
The candidate and the test are declared in `docs/pivot/onset-blend-160.md`, committed before this script
scored anything.

`blend` is the unweighted mean of pressure model v1's recalibrated probability and the persistence-logistic's,
per threshold, on the shared fold grid. It is paired against v1 (Brier(v1) minus Brier(blend); positive favours
the blend) on scored days before 2026-01-01, overall, by regime and by pressure-day type. The onset groups are
reported for v1 and the blend against the persistence-logistic, descriptively.

    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/onset_blend_160.py \
        --panel PANEL --output OUT/onset_blend_160.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Mapping, Sequence
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import baseline, onset  # noqa: E402
from repo_model.baseline import _maximum_horizon_overlap, _split_labels, panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
TEST_END = date(2026, 1, 1)
TAUS = (5.0, 10.0)
MINIMUM_CELL_DAYS = 20
BLEND = "blend"


def require_before_2026(scored_dates: Sequence[date]) -> None:
    """The test scores days before 2026-01-01 only (`docs/decisions/lockbox.md`, Eleonora's ruling on #339)."""

    for day in scored_dates:
        if day >= TEST_END:
            raise LookAheadError(f"{day} is on or after {TEST_END}: the blend test scores earlier days only")


def blend(first: Sequence[float], second: Sequence[float]) -> list:
    if len(first) != len(second):
        raise ValueError("the two probability columns differ in length")
    return [(a + b) / 2.0 for a, b in zip(first, second)]


def judge(cells: Mapping[str, Mapping[str, dict]]) -> dict:
    """The declared pass rule over `cells[tau][cell]` = paired(v1 minus blend)."""

    passes = True
    worse = {}
    for tau, by_cell in cells.items():
        everyone = by_cell["all"]
        if not (everyone.get("interval") and everyone["interval"]["lower"] > 0):
            passes = False
        worse[tau] = [
            name
            for name, cell in by_cell.items()
            if name != "all"
            and cell.get("days", 0) >= MINIMUM_CELL_DAYS
            and cell.get("interval")
            and cell["interval"]["upper"] < 0
        ]
        if worse[tau]:
            passes = False
    return {"passes": passes, "worse_cells": worse}


def _pressure_model_v1():
    spec = importlib.util.spec_from_file_location("pressure_model_v1", REPO / "scripts" / "pressure_model_v1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    captured = {"benchmarks": []}
    real = baseline.benchmark_comparison_document

    def capture(report, bench, **kwargs):
        captured["report"] = report
        captured["benchmarks"].append(bench)
        return real(report, bench, **kwargs)

    with tempfile.TemporaryDirectory() as scratch, mock.patch.object(
        baseline, "benchmark_comparison_document", capture
    ):
        code = _pressure_model_v1().main(
            ["publish", "--panel", str(args.panel), "--horizon", "1", "--report", str(Path(scratch) / "discarded.json")]
        )
    if code != 0:
        return code
    report = captured["report"]
    require_before_2026(report.scored_dates)
    logistic = next(b for b in captured["benchmarks"] if "persistence" in b.model_name)

    rows = load_daily_panel(args.panel)
    digest = panel_sha256(args.panel)
    declaration = load_split_declaration(SPLITS)
    groups = onset.day_groups(rows, report.scored_dates, declaration)
    regimes, day_types = _split_labels(declaration, rows, report.scored_dates)
    block = _maximum_horizon_overlap(report.folds)

    out = {
        "panel_sha256": digest,
        "model": report.model_name,
        "benchmark": logistic.model_name,
        "candidate": BLEND,
        "first_scored": report.scored_dates[0].isoformat(),
        "last_scored": report.scored_dates[-1].isoformat(),
        "sign_convention": "paired = brier(first) - brier(second); positive favours the second",
        "test": {},
        "onset_groups": {},
    }
    test_cells = {}
    for tau in TAUS:
        position = report.taus.index(tau)
        v1, _, outcomes = report.at_tau(position)
        pl = logistic.at_tau(position)[0]
        mixed = blend(v1, pl)
        loss = {
            "v1": [(p - o) ** 2 for p, o in zip(v1, outcomes)],
            "logistic": [(p - o) ** 2 for p, o in zip(pl, outcomes)],
            BLEND: [(p - o) ** 2 for p, o in zip(mixed, outcomes)],
        }
        cell_positions = {"all": list(range(len(outcomes)))}
        for label in sorted(set(regimes)):
            cell_positions[f"regime {label}"] = [k for k, r in enumerate(regimes) if r == label]
        for label in sorted(set(day_types)):
            cell_positions[f"day type {label}"] = [k for k, t in enumerate(day_types) if t == label]

        def paired(first, second, positions, tag):
            return onset.paired_difference(
                loss[first], loss[second], positions, block_length=block,
                seed=onset._seed(digest, "160", f"{tau:g}", tag, first, second),
            )

        cells = {}
        for name, positions in cell_positions.items():
            cell = paired("v1", BLEND, positions, name)
            cell["events"] = sum(outcomes[k] for k in positions)
            cell["brier"] = {k: sum(v[i] for i in positions) / len(positions) for k, v in loss.items()}
            cells[name] = cell
        test_cells[f"{tau:g}"] = cells
        out["test"][f"{tau:g}"] = cells
        by_group = {}
        for group in (onset.GROUP_ONSET, onset.GROUP_ONSET_ONE_DAY):
            positions = groups[group]
            by_group[group] = {
                "days": len(positions),
                "events": sum(outcomes[k] for k in positions),
                "brier": {k: sum(v[i] for i in positions) / len(positions) for k, v in loss.items()},
                "logistic_minus_v1": paired("logistic", "v1", positions, group),
                "logistic_minus_blend": paired("logistic", BLEND, positions, group),
                "v1_minus_blend": paired("v1", BLEND, positions, group),
            }
        out["onset_groups"][f"{tau:g}"] = by_group
    out["verdict"] = judge(test_cells)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def show(cell):
        i = cell["interval"]
        return f"{cell['mean']:+.4f} [{i['lower']:+.4f}, {i['upper']:+.4f}]"

    for tau, cells in test_cells.items():
        for name, cell in cells.items():
            print(f"+{tau} bp | v1 minus blend | {name} | days {cell['days']} | events {cell['events']} | {show(cell)}")
    for tau, by_group in out["onset_groups"].items():
        for group, cell in by_group.items():
            print(
                f"+{tau} bp | {group} | days {cell['days']} | events {cell['events']} | "
                f"logistic-v1 {show(cell['logistic_minus_v1'])} | logistic-blend {show(cell['logistic_minus_blend'])}"
            )
    print(json.dumps(out["verdict"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
