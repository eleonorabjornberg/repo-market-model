#!/usr/bin/env python3
"""The live-monitoring read (#969), reported only: it decides nothing and opens no tier.

    PYTHONPATH=src python3 scripts/live_monitor.py replay --panel PANEL --output OUT.json
    PYTHONPATH=src python3 scripts/live_monitor.py run --live-dir LIVE --digests DIGESTS.jsonl --panel PANEL \\
        --output OUT.json

`replay` runs the read on the published model's development record (`docs/runs/published_distribution_daily_h1.json`,
to 2025-12-31), so a reader can see whether the 2021-23 and 2024 signatures would have fired under the proposed
thresholds of `metadata/live_monitoring_969.json`. It reads no day after the study window and no locked day.

`run` reads the live record and the public outcomes. It refuses unless `docs/decisions/live-monitoring.md` is merged
(`repo_model.live_monitor.require_decision_record`, `LookAheadError`). It verifies the live log's integrity first, as
`scripts/live_score.py` does, then reports (never raises on) a record made at a code SHA that is not a registered pin.
Standard library only; the statistics are `repo_model.live_monitor`'s.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, time
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import live_monitor as lm  # noqa: E402
from repo_model import protocol_benchmarks as pb  # noqa: E402
from repo_model.contract import QUANTILE_LEVELS  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.scoring_protocol import GRID  # noqa: E402

DECLARATION = REPO / "metadata" / "live_monitoring_969.json"
SOURCES = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
DEV_RECORD = REPO / "docs" / "runs" / "published_distribution_daily_h1.json"
DECISION_TIME = time(16, 0)


def _script(name):
    spec = spec_from_file_location(f"monitor_{name}", REPO / "scripts" / f"{name}.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_declaration(path: Path = DECLARATION) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _subset(vector):
    """The five monitored levels of a protocol-grid vector."""

    return [vector[GRID.index(level)] for level in QUANTILE_LEVELS]


def development_rows(panel_rows, registry, splits) -> list:
    """The development record's days to 2025-12-31 as monitor rows, with B1 and B2 from the panel where formable."""

    record = json.loads(DEV_RECORD.read_text(encoding="utf-8"))
    if list(record["levels"]) != list(QUANTILE_LEVELS):
        raise ValueError("the development record is not on the monitored levels")
    days = [day for day in record["days"] if date.fromisoformat(day["date"]) <= lm.DEV_LAST]
    lm.require_development_window(date.fromisoformat(day["date"]) for day in days)
    require_unlocked([date.fromisoformat(day["date"]) for day in days], where="live_monitor replay")
    position = {row.date: index for index, row in enumerate(panel_rows)}
    rows = []
    for day in days:
        target = date.fromisoformat(day["date"])
        row = {"date": target, "outcome": float(day["actual_bps"]), "published": list(day["quantiles_bps"]),
               "b1": None, "b2": None}
        decision_index = position[target] - 1
        for name, make in (("b1", lambda: pb.b1_forecast(panel_rows, decision_index, registry=registry,
                                                          decision_time=DECISION_TIME)[1]),
                           ("b2", lambda: pb.b2_forecast(panel_rows, decision_index, registry=registry,
                                                          decision_time=DECISION_TIME, splits=splits)[1])):
            try:
                row[name] = _subset(make())
            except pb.ProtocolError:
                row[name] = None
        rows.append(row)
    return rows


def _round(value, places=4):
    return None if value is None else round(value, places)


def regime_summary(rows, series, splits, thresholds) -> list:
    out = []
    by_date = {point["date"]: point for point in series}
    for label in splits.regime_labels:
        mine = [row for row in rows if splits.regime(row["date"]) == label]
        if not mine:
            continue
        points = [by_date[row["date"]] for row in mine]
        covered = [p["coverage_60"] for p in points if p["coverage_60"] is not None]
        misses = lm.tail_misses(mine)
        kup, chri = lm.kupiec(misses, 0.05), lm.christoffersen(misses)
        flags = {}
        for point in points:
            for flag in point["flags"]:
                flags[flag] = flags.get(flag, 0) + 1
        out.append({
            "regime": label, "days": len(mine),
            "band_coverage": _round(sum(lm.band_hits(mine)) / len(mine)),
            "min_coverage_60": _round(min(covered)) if covered else None,
            "coverage_60_days": len(covered),
            "tail_q95": {"misses": kup["misses"], "rate": _round(kup["rate"]), "kupiec_lr": _round(kup["lr"]),
                         "kupiec_p": _round(kup["p_value"], 6), "christoffersen_lr": _round(chri["lr"]),
                         "christoffersen_p": _round(chri["p_value"], 6)},
            "pit": lm.pit_shares(mine),
            "crps_ratio_b1": lm.crps_ratio(mine, "b1"), "crps_ratio_b2": lm.crps_ratio(mine, "b2"),
            "flag_days": dict(sorted(flags.items())),
            "first_flag_dates": {flag: min(p["date"] for p in points if flag in p["flags"]).isoformat()
                                 for flag in sorted(flags)},
        })
    return out


def replay(panel_path: Path) -> dict:
    declaration = load_declaration()
    thresholds = declaration["proposed_thresholds"]
    windows = declaration["windows"]
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    splits = load_split_declaration(SPLITS)
    panel_rows = load_daily_panel(panel_path)
    rows = development_rows(panel_rows, registry, splits)
    series = lm.rolling(rows, thresholds, coverage_days=windows["coverage_days"],
                        calibration_days=windows["calibration_days"])
    overall = lm.report(rows, thresholds, coverage_days=windows["coverage_days"],
                        calibration_days=windows["calibration_days"])
    compact = [{"date": p["date"].isoformat(), "coverage_60": _round(p["coverage_60"]),
                "kupiec_p": _round(p["kupiec_p"], 6), "christoffersen_p": _round(p["christoffersen_p"], 6),
                "pit_share_at_or_below_q25": _round(p["pit_share_at_or_below_q25"]),
                "crps_ratio_b1": _round(p["crps_ratio_b1"]), "flags": p["flags"]} for p in series]
    return {
        "directive": "#969", "decides": "nothing", "tier": "development",
        "label": "development data, not a verdict",
        "declaration": "metadata/live_monitoring_969.json", "thresholds_status": lm.THRESHOLDS_STATUS,
        "source": str(DEV_RECORD.relative_to(REPO)), "lead": 1, "first_day": rows[0]["date"].isoformat(),
        "last_day": rows[-1]["date"].isoformat(), "days": len(rows),
        "panel_sha256": __import__("hashlib").sha256(Path(panel_path).read_bytes()).hexdigest(),
        "overall": {k: v for k, v in overall.items() if k not in ("series", "latest")},
        "by_regime": regime_summary(rows, series, splits, thresholds),
        "series": compact,
    }


def live_run(live_dir: Path, digests, panel_path: Path) -> dict:
    lm.require_decision_record()
    declaration = load_declaration()
    thresholds = declaration["proposed_thresholds"]
    windows = declaration["windows"]
    integrity, pins, live = _script("live_integrity"), _script("live_pin"), _script("live_record")
    integrity.verify(live_dir, integrity.parse_digests(digests))
    records = []
    for path in sorted((Path(live_dir) / "live").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        live.validate_record(record)
        if not record.get("dry_run"):
            records.append(record)
    outcomes = {row.date: row.spread_bps for row in load_daily_panel(panel_path)}
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    leads = {}
    for lead in live.HORIZONS:
        rows = lm.rows_from_records(records, outcomes, lead=lead)
        leads[str(lead)] = (lm.report(rows, thresholds, coverage_days=windows["coverage_days"],
                                      calibration_days=windows["calibration_days"]) if rows else None)
    return {
        "directive": "#969", "decides": "nothing", "thresholds_status": lm.THRESHOLDS_STATUS,
        "records": len(records), "leads": leads,
        "pin": lm.pin_check(records, pins.registered(pins.load_manifest())),
        "staleness": [lm.staleness(record, registry) for record in records[-1:]],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("replay")
    one.add_argument("--panel", required=True, type=Path)
    one.add_argument("--output", required=True, type=Path)
    two = sub.add_parser("run")
    two.add_argument("--live-dir", required=True, type=Path)
    two.add_argument("--digests", required=True, type=Path)
    two.add_argument("--panel", required=True, type=Path)
    two.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.command == "replay":
        result = replay(args.panel)
    else:
        digests = [line for line in args.digests.read_text(encoding="utf-8").splitlines() if line.strip()]
        result = live_run(args.live_dir, digests, args.panel)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
