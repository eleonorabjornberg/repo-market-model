"""The onset groups after #209, on the published pressure model v1 at h = 1.

A scratch measurement, not a record: it runs `scripts/pressure_model_v1.py
publish` at horizon 1 (the published declaration, last scored day 2025-12-31,
so no locked day is scored), keeps the scored report and both benchmark
reports, and prints the Brier score of each by onset group, each benchmark
paired against the model (benchmark minus model, 90% stationary-bootstrap
interval). The record `publish` writes goes to a temporary file and is
discarded: nothing is written into `docs/runs/`.

    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/onset_at_risk_example.py \
        --panel PANEL --output OUT/onset_at_risk_h1.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from datetime import date
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import baseline, onset  # noqa: E402
from repo_model.baseline import _maximum_horizon_overlap, panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
#: The onsets alone, the group before #209, shown for contrast only.
ONSETS_ONLY = "onsets_only_before_209"


def _pressure_model_v1():
    spec = importlib.util.spec_from_file_location(
        "pressure_model_v1", REPO / "scripts" / "pressure_model_v1.py"
    )
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
            ["publish", "--panel", str(args.panel), "--horizon", "1",
             "--report", str(Path(scratch) / "discarded.json")]
        )
    if code != 0:
        return code
    report = captured["report"]
    if max(report.scored_dates) >= date(2026, 1, 1):
        raise ValueError("a scored day is locked (docs/decisions/lockbox.md)")

    rows = load_daily_panel(args.panel)
    digest = panel_sha256(args.panel)
    every = onset.day_groups(rows, report.scored_dates, load_split_declaration(SPLITS))
    groups = {
        onset.GROUP_ALL: every[onset.GROUP_ALL],
        onset.GROUP_ONSET: every[onset.GROUP_ONSET],
        onset.GROUP_ONSET_ONE_DAY: every[onset.GROUP_ONSET_ONE_DAY],
        ONSETS_ONLY: onset.onset_positions(rows, report.scored_dates),
    }
    block = _maximum_horizon_overlap(report.folds)
    out = {
        "panel_sha256": digest,
        "model": report.model_name,
        "horizon": 1,
        "first_scored": report.scored_dates[0].isoformat(),
        "last_scored": report.scored_dates[-1].isoformat(),
        "sign_convention": f"paired = brier(benchmark) - brier({report.model_name}); positive: the model is better",
        "by_tau": {},
    }
    for tau in (5.0, 10.0):
        position = report.taus.index(tau)
        predicted, _, outcomes = report.at_tau(position)
        columns = {report.model_name: predicted}
        for bench in captured["benchmarks"]:
            columns[bench.model_name] = bench.at_tau(position)[0]
        out["by_tau"][f"{tau:g}"] = onset._group_block(
            report.model_name, columns, outcomes, groups,
            block_length=block, seed_parts=(digest, "209", f"{tau:g}"), test_all_days=False,
        )
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for tau, entry in out["by_tau"].items():
        for group, cell in entry.items():
            paired = "; ".join(
                f"{name} {p['mean']:+.4f} [{p['interval']['lower']:+.4f}, {p['interval']['upper']:+.4f}]"
                for name, p in cell["paired"].items() if "interval" in p
            )
            print(f"+{tau} bp | {group} | days {cell['days']} | events {cell['events']} | {paired}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
