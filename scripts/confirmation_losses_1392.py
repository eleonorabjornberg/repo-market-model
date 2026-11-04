#!/usr/bin/env python3
"""Origin-level loss vectors of (s3c-ann-net) and its comparison arms, for the size-and-power study (#1392; H5, registration design).

A development extract, never a verdict. It walks the candidate exactly as `scripts/b1_anchor_horizon_1388.py` does (the 18:00 decision instant, the two
development windows) and writes, for each decision day (an origin), the 23-quantile score averaged over h = 1..5 (`scoring_protocol.day_scores`) of the
candidate, the announced-flag arm (s3c-ann), B1, B1', B1*, B1'* and B2, with the day's regime label. `scripts/confirmation_size_power_1392.py` reads this file.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/confirmation_losses_1392.py extract --panel PUB.csv \\
        --output docs/research/confirmation-size-power-1392/losses.json

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, policy_events  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mr_calendar as cal  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import require_exploratory_window  # noqa: E402

m1388 = _load("b1_anchor_horizon_1388", "b1_anchor_horizon_1388_in_1392")
m1288, m1273, c, k = m1388.m1288, m1388.m1273, m1388.c, m1388.k

#: model key -> role in the study.
ARMS = {
    m1288.ANNNET: "candidate", m1288.ANN: "flag", "B1": "B1", m1388.B1S: "B1*", m1388.B1P: "B1p", m1388.B1PS: "B1p*", "B2": "B2",
}


def extract_window(window: str, panel, splits, registry, table, register, results, auctions, first: Optional[date]) -> dict:
    """Per-origin scores of every arm in `ARMS` on one development window, and the regime label of each origin."""

    frame, _notes, _walks, _tables, _cells, groups_fn = m1288.build(window, panel, splits, registry, table, register, results, auctions, first)
    star, prime_star, _lags = m1388.forecasts_of(panel, frame, splits, registry)
    forecasts = {m: frame.forecasts[m] for m in (m1288.ANNNET, m1288.ANN, "B1", m1388.B1P, "B2")}
    forecasts[m1388.B1S], forecasts[m1388.B1PS] = star, prime_star
    scores = {m: sp.day_scores({d: forecasts[m][d] for d in frame.days}, frame.outcome, frame.dates, score=sp.grid_crps) for m in ARMS}
    days = sorted(set.intersection(*(set(s) for s in scores.values())))
    labels = c.day_labels(frame, table)
    pressure = k.pressure_labels(frame, sorted(labels))
    regime: Dict[date, str] = {}
    for split, label, _grain, members in groups_fn(frame, labels, pressure):
        if split == "regime":
            for d in members:
                regime[d] = label
    return {
        "origins": [d.isoformat() for d in days],
        "regime": [regime.get(d, "") for d in days],
        "scores": {ARMS[m]: [scores[m][d] for d in days] for m in ARMS},
    }


def extract(args) -> int:
    m1388.require_instant()
    panel_path = Path(args.panel)
    panel = [row for row in m1273.load_daily_panel(panel_path) if row.date <= m1388.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/confirmation_losses_1392")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=c.DECISION_TIME)
    auctions = m1273.load_auctions()
    results = m1288.load_results()
    out = {"issue": 1392, "label": "development, not a verdict", "panel_sha256": panel_sha256(panel_path), "decision_time": "18:00",
           "score": "grid CRPS (23 quantiles) averaged over h = 1..5, per origin", "windows": {}}
    for window in m1388.WINDOWS:
        out["windows"][window] = extract_window(window, panel, splits, registry, table, register, results, auctions, args.first)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("extract")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--first", type=date.fromisoformat, default=None)
    s.set_defaults(func=extract)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
