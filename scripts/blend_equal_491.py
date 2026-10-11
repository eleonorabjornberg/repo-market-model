#!/usr/bin/env python3
"""Publish `blend_equal` as the published distribution at h = 1 (#491), under Eleonora's approval on #456.

`blend_equal` is the equal-weight average of the published model's and the direct-pairs twin's uncalibrated quantile
vectors, then the published conformal calibration unchanged, exactly as declared in `metadata/turning_point_variant.json`
and scored in #455 (`docs/pivot/turning-point-variant-result.md`). This script re-runs nothing new: it takes the blend
walk of `scripts/turning_point_variant.py walk` and writes it as a daily record in the shape of
`published_distribution_daily_h1.json`, `docs/runs/published_distribution_blend_equal_daily_h1.json`, with the
before and after table. Every figure is recomputed with #455's own functions and seed and refused unless it equals
#455's stored score exactly. Scored days are 2018-06-29 to 2025-12-31 only (`docs/decisions/lockbox.md`): the 2026 days
and the frozen final test are not scored, and the live record and the live pin are not read or changed. The old record
`published_distribution_daily_h1.json` stays as it is.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/turning_point_variant.py walk --panel PUB.csv --output WALK.json
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/blend_equal_491.py score --panel PUB.csv --walk WALK.json
    PYTHONPATH=src python3 scripts/blend_equal_491.py render
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.baseline import _code_provenance, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402

RUNS = REPO / "docs" / "runs"
PUBLISHED = RUNS / "published_distribution_daily_h1.json"
OUTPUT = RUNS / "published_distribution_blend_equal_daily_h1.json"
PAGE = REPO / "docs" / "blend_equal_491.md"
EVIDENCE = REPO / "docs" / "pivot" / "evidence" / "turning_point_variant" / "score.json"
MANIFEST = REPO / "metadata" / "funding_panel_manifest.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
END = date(2025, 12, 31)
BEGIN, FINISH = "<!-- generated: blend-equal -->", "<!-- end generated: blend-equal -->"


def _script(name):
    spec = importlib.util.spec_from_file_location(name + "_491", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cell_order(label: str):
    return (0, "") if label == "all" else (1, label)


def check_days(base, days) -> None:
    """Refuse a walk that is not on the published record's days to 2025-12-31, or that scores a later day (#491)."""

    if any(d["date"] > END.isoformat() for d in days):
        raise ValueError(f"the blend walk scores a day after {END}; 2026 days are not scored here")
    if [d["date"] for d in days] != [d["date"] for d in base]:
        raise ValueError("the blend walk is not on the published record's scored days to 2025-12-31")
    for mine, theirs in zip(days, base):
        if mine["actual_bps"] != theirs["actual_bps"]:
            raise ValueError(f"{mine['date']}: the actual spread is not the published record's")
        if any(a > b for a, b in zip(mine["quantiles_bps"], mine["quantiles_bps"][1:])):
            raise ValueError(f"{mine['date']}: a crossing vector")


def score_command(args) -> int:
    variant = _script("turning_point_variant")
    twin = variant.twin_script
    seed = variant.SEED
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    digest = panel_sha256(args.panel)
    if digest != manifest["sha256"]:
        raise ValueError("the panel is not the published panel")
    require_unlocked([END], where="blend_equal_491")
    walk = json.loads(args.walk.read_text(encoding="utf-8"))
    if walk["which"] != "blend" or walk["panel_sha256"] != digest:
        raise ValueError("the walk is not the blend walk on the published panel")
    published = json.loads(PUBLISHED.read_text(encoding="utf-8"))
    base = [d for d in published["days"] if d["date"] <= END.isoformat()]
    days = walk["days"]
    check_days(base, days)
    require_unlocked([date.fromisoformat(d["date"]) for d in days], where="blend_equal_491")
    if list(walk["levels"]) != LEVELS:
        raise ValueError("the blend walk is not on the five published levels")
    by_date = {r.date: r for r in rows}
    splits = load_split_declaration(SPLITS)
    after = [crps_from_quantiles(LEVELS, d["quantiles_bps"], d["actual_bps"]) for d in days]
    before = [crps_from_quantiles(LEVELS, d["quantiles_bps"], d["actual_bps"]) for d in base]
    gain = [b - a for b, a in zip(before, after)]
    groups = {"all": [True] * len(days)}
    labels = {"regime": [], "day_type": [], "outcome": []}
    for d in days:
        when = date.fromisoformat(d["date"])
        row = by_date[when]
        labels["regime"].append(splits.regime(when))
        labels["day_type"].append(splits.reporting_day_type(when, row.values))
        labels["outcome"].append("pressure day (> +5 bp)" if exceeds_bp(row.spread_bps, 5) else "other days")
    for dimension, values in labels.items():
        for label in sorted(set(values)):
            groups[f"{dimension}: {label}"] = [v == label for v in values]
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if evidence["panel_sha256"] != digest:
        raise ValueError("#455's score is on another panel")
    cells = {}
    for name in sorted(groups, key=_cell_order):
        members = [i for i, m in enumerate(groups[name]) if m]
        cell = {"days": len(members),
                "crps_before": sum(before[i] for i in members) / len(members),
                "crps_after": sum(after[i] for i in members) / len(members),
                "gain": twin._mean_ci([gain[i] for i in members], seed)}
        stored = evidence["crps"][name]
        if (cell["days"] != stored["days"] or cell["crps_before"] != stored["mean_crps"]["published"]
                or cell["crps_after"] != stored["mean_crps"]["blend_equal"]
                or cell["gain"] != stored["gain_over_published"]["blend_equal"]):
            raise ValueError(f"{name}: the figures differ from #455's score; stop for Eleonora")
        cells[name] = cell
    coverage = {}
    for label, vectors in (("before", [d["quantiles_bps"] for d in base]), ("after", [d["quantiles_bps"] for d in days])):
        actual = [d["actual_bps"] for d in days]
        coverage[label] = {
            "50%": sum(q[1] <= a <= q[3] for q, a in zip(vectors, actual)) / len(actual),
            "90%": sum(q[0] <= a <= q[4] for q, a in zip(vectors, actual)) / len(actual),
        }
    if (coverage["before"] != evidence["coverage"]["all"]["published"]
            or coverage["after"] != evidence["coverage"]["all"]["blend_equal"]):
        raise ValueError("the coverage differs from #455's score; stop for Eleonora")
    record = {
        "record": "the published distribution as the equal-weight blend of the published model and the direct-pairs "
                  "twin (blend_equal), every scored day at h = 1 from 2018-06-29 to 2025-12-31",
        "directive": "#491",
        "approval": "Eleonora, comment 6087569748 on #456 (performed_via_github_app null)",
        "decides": "nothing beyond this publication; the live record and the live pin are not read or changed, and "
                   "the 2026 days and the frozen final test are not scored",
        "horizon": 1,
        "levels": LEVELS,
        "first": days[0]["date"],
        "last": days[-1]["date"],
        "candidate": "blend_equal",
        "declaration": "metadata/turning_point_variant.json",
        "declaration_commit": evidence["declaration_commit"],
        "base_record": str(PUBLISHED.relative_to(REPO)),
        "test": str(EVIDENCE.relative_to(REPO)),
        "panel_sha256": digest,
        "walk_settings": walk["settings"],
        "sign_convention": "gain = CRPS(published) - CRPS(blend_equal) per day; positive favours the blend",
        "bootstrap": {"method": "stationary_bootstrap", **{k: evidence["interval"][k]
                                                           for k in ("block_length", "replications", "level", "seed")}},
        "before_after": {"cells": cells, "coverage": coverage},
        "days": [{"date": d["date"], "actual_bps": d["actual_bps"], "quantiles_bps": d["quantiles_bps"]} for d in days],
        "provenance": {"code": _code_provenance()},
    }
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _gain(cell) -> str:
    low, high = cell["interval"]
    return "%+.3f [%+.3f, %+.3f]" % (cell["mean"], low, high)


def render(record) -> str:
    """The page, from the record alone."""

    ba = record["before_after"]
    lines = [
        "# The published distribution as the blend of the published model and its direct-pairs twin (#491)", "", BEGIN, "",
        "**Generated by `scripts/blend_equal_491.py render` from "
        "`docs/runs/published_distribution_blend_equal_daily_h1.json`; never hand-edited.**", "",
        "Each day's forecast is the equal-weight average of the published model's and the direct-pairs twin's "
        "uncalibrated quantiles, then the published conformal calibration unchanged. It was declared before it was scored "
        f"in `{record['declaration']}` and scored in #455; the approval is {record['approval']}. Days: {record['first']} "
        f"to {record['last']} only; the 2026 days and the frozen final test are not scored. The live record and the live "
        "pin are untouched. The published model's own record stays in `docs/runs/published_distribution_daily_h1.json`.", "",
        "Gain is CRPS(published) - CRPS(blend) per day in bp, so a positive mean favours the blend; intervals are 90% "
        "stationary bootstraps (block length %d, %d replications). Intervals of the cells are not adjusted for several "
        "comparisons; only the first row is the declared test." % (
            record["bootstrap"]["block_length"], record["bootstrap"]["replications"]), "",
        "## CRPS and gain", "",
        "| Cell | Days | CRPS published (bp) | CRPS blend (bp) | Gain, 90% interval |", "|---|---|---|---|---|"]
    for name, c in ba["cells"].items():
        lines.append("| %s | %d | %.3f | %.3f | %s |" % (name, c["days"], c["crps_before"], c["crps_after"], _gain(c["gain"])))
    lines += ["", "## Coverage over all days", "", "| Band | Published | Blend |", "|---|---|---|"]
    for band in ("50%", "90%"):
        lines.append("| %s | %.3f | %.3f |" % (band, ba["coverage"]["before"][band], ba["coverage"]["after"][band]))
    lines += ["", FINISH, ""]
    return "\n".join(lines)


def render_command(args) -> int:
    args.output.write_text(render(json.loads(args.record.read_text(encoding="utf-8"))), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--walk", type=Path, required=True)
    score.add_argument("--output", type=Path, default=OUTPUT)
    score.set_defaults(func=score_command)
    page = sub.add_parser("render")
    page.add_argument("--record", type=Path, default=OUTPUT)
    page.add_argument("--output", type=Path, default=PAGE)
    page.set_defaults(func=render_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
