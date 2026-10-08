#!/usr/bin/env python3
"""Publish the calendar-adjusted interior bands (#418), under Eleonora's ruling of 8 October 2026 on #415.

`conformal_pid_calendar` met the test declared for #243 on 2018-06-29 to 2025-12-31 and held on 2026-01-02 to
2026-09-03 (#408). This script applies it, exactly as declared in `docs/declarations/interior_calibration_243_addendum.json`
and unchanged, to the published distribution's issued vectors at h = 1, and writes the result as a daily record in
the shape of `published_distribution_daily_h1.json`: `docs/runs/published_distribution_calendar_daily_h1.json`. It
holds every scored day's five quantiles and the actual spread, the 5% and 95% quantiles (the 90% band) exactly as
published, and the before and after table. The CRPS and pooled gain are recomputed with #243's and #408's own
functions and seeds and refused unless they equal those records exactly. The live record and the live pin are not read
or changed.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/calendar_bands_418.py score --panel PUB.csv
    PYTHONPATH=src python3 scripts/calendar_bands_418.py render
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import statistics
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, onset  # noqa: E402
from repo_model.baseline import _code_provenance, _split_labels, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import DAY_TYPES, load_split_declaration  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402

CANDIDATE = "conformal_pid_calendar"
RUNS = REPO / "docs" / "runs"
PUBLISHED = RUNS / "published_distribution_daily_h1.json"
DEVELOPMENT = RUNS / "interior_calibration_243.json"
CONFIRMATION = RUNS / "interior_confirmation_408.json"
OUTPUT = RUNS / "published_distribution_calendar_daily_h1.json"
PAGE = REPO / "docs" / "calendar_bands_418.md"
LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
LAST = date(2026, 9, 3)
SPLIT = "2026-01-01"
PERIODS = (("2018-2025", "#243"), ("2026", "#408"))
BEGIN, END = "<!-- generated: calendar-bands -->", "<!-- end generated: calendar-bands -->"
SHOWN = ("all", "reporting:ordinary", "reporting:month_end", "reporting:quarter_end", "reporting:tax_date",
         "tag:coupon_settlement")


def _judge():
    spec = importlib.util.spec_from_file_location("judge_418", REPO / "scripts" / "interior_calibration_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mean_crps(days) -> float:
    return statistics.fmean(crps_from_quantiles(LEVELS, d["quantiles_bps"], d["actual_bps"]) for d in days)


def score_command(args) -> int:
    judge = _judge()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    manifest = json.loads(judge.MANIFEST.read_text(encoding="utf-8"))
    if panel_sha256(args.panel) != manifest["sha256"]:
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(judge.SPLITS)
    with open(args.panel, newline="", encoding="utf-8") as handle:
        tag_rows = {r["date"]: r for r in csv.DictReader(handle)}
    judge.WINDOW = (judge.WINDOW[0], LAST)
    full = judge.load_days(rows, splits, tag_rows)
    lockbox.require_unlocked([date.fromisoformat(full[-1]["date"])], where="calendar_bands_418")
    if full[-1]["date"] != LAST.isoformat():
        raise ValueError(f"the scored days end {full[-1]['date']}, not {LAST}")
    vectors = judge.candidate_vectors(CANDIDATE, full)
    published = json.loads(PUBLISHED.read_text(encoding="utf-8"))
    if [d["date"] for d in published["days"]] != [d["date"] for d in full]:
        raise ValueError("the published daily record is not on these days")
    for mine, theirs, v in zip(full, published["days"], vectors):
        if mine["issued"] != theirs["quantiles_bps"] or mine["y"] != theirs["actual_bps"]:
            raise ValueError(f"{mine['date']}: the issued vector is not the published daily record's")
        if any(a > b for a, b in zip(v, v[1:])):
            raise ValueError(f"{mine['date']}: a crossing vector")
    moved = [d["date"] for v, d in zip(vectors, full) if v[0] != d["issued"][0] or v[4] != d["issued"][4]]
    outward = all(v[0] <= d["issued"][0] and v[4] >= d["issued"][4] for v, d in zip(vectors, full))

    development = json.loads(DEVELOPMENT.read_text(encoding="utf-8"))
    confirmation = json.loads(CONFIRMATION.read_text(encoding="utf-8"))
    before_after = {}
    for key, directive in PERIODS:
        keep = [k for k, d in enumerate(full) if (d["date"] < SPLIT) == (key == "2018-2025")]
        days = [full[k] for k in keep]
        dates = [date.fromisoformat(d["date"]) for d in days]
        regimes, types = _split_labels(splits, rows, dates)
        groups = {"regime:" + r: [x == r for x in regimes] for r in splits.regime_labels if r in set(regimes)}
        for t in judge.TAGS:
            groups["tag:" + t] = [t in d["tags"] for d in days]
        groups["tag:other"] = [not d["tags"] for d in days]
        for t in DAY_TYPES:
            groups["reporting:" + t] = [x == t for x in types]
        names = list(groups)
        masks = [[True] * len(days)] + [groups[n] for n in names]
        after = [vectors[k] for k in keep]
        before = [d["issued"] for d in days]
        loss_b = [judge._crps(v, d["y"]) for v, d in zip(before, days)]
        loss_a = [judge._crps(v, d["y"]) for v, d in zip(after, days)]
        cells = judge.cell_intervals([a - b for a, b in zip(loss_b, loss_a)], masks,
                                     onset._seed(directive, "gain", CANDIDATE))
        coverage = {}
        for label, vs in (("before", before), ("after", after)):
            out = {"all": judge.coverage(days, vs)}
            for n in names:
                members = [i for i, m in enumerate(groups[n]) if m]
                if members:
                    out[n] = judge.coverage([days[i] for i in members], [vs[i] for i in members])
            coverage[label] = out
        reference = development if key == "2018-2025" else confirmation
        stored = reference["candidates"][CANDIDATE]
        if (statistics.fmean(loss_a) != stored["crps_bps"] or cells[0] != stored["pooled_gain"]
                or statistics.fmean(loss_b) != reference["published"]["crps_bps"]):
            raise ValueError(f"{key}: the figures differ from {directive}'s record")
        before_after[key] = {
            "directive": directive, "first": days[0]["date"], "last": days[-1]["date"], "days": len(days),
            "crps_before": statistics.fmean(loss_b), "crps_after": statistics.fmean(loss_a),
            "pooled_gain": cells[0], "gain_by_group": dict(zip(names, cells[1:])), "coverage_by_group": coverage,
        }

    addendum = json.loads(judge.ADDENDUM.read_text(encoding="utf-8"))
    record = {
        "record": "the published distribution with the calendar-adjusted middle band (conformal_pid_calendar), "
                  "every scored day at h = 1",
        "directive": "#418",
        "decides": "nothing beyond this publication; the live record and the live pin are not read or changed",
        "horizon": 1,
        "levels": LEVELS,
        "first": full[0]["date"],
        "last": full[-1]["date"],
        "candidate": CANDIDATE,
        "settings": addendum["candidates"][CANDIDATE],
        "addendum": str(judge.ADDENDUM.relative_to(REPO)),
        "addendum_sha256": sha256(judge.ADDENDUM),
        "tests": {"2018-2025": str(DEVELOPMENT.relative_to(REPO)), "2026": str(CONFIRMATION.relative_to(REPO))},
        "base_record": str(PUBLISHED.relative_to(REPO)),
        "panel_sha256": panel_sha256(args.panel),
        "outer_band_unchanged": not moved,
        "outer_edge_moved_days": len(moved),
        "outer_edge_moves_outward_only": outward,
        "outer_edge_moved_by_window": {k: sum(1 for m in moved if (m < SPLIT) == (k == "2018-2025"))
                                       for k, _ in PERIODS},
        "sign_convention": judge.SIGN,
        "bootstrap": {"block_length": judge.BLOCK_LENGTH, "replications": judge.REPLICATIONS, "level": judge.LEVEL},
        "before_after": before_after,
        "days": [{"date": d["date"], "actual_bps": d["y"], "quantiles_bps": v} for d, v in zip(full, vectors)],
        "provenance": {"code": _code_provenance()},
    }
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _gain(cell) -> str:
    i = cell["interval"]
    return "%+.3f [%+.3f, %+.3f]" % (cell["mean"], i["lower"], i["upper"])


def _cov(cell, band) -> str:
    return "%.1f%% (%.1f / %.1f)" % (cell[band], cell[band + "_miss_below"], cell[band + "_miss_above"])


def render(record) -> str:
    """The page, from the record alone."""

    ba = record["before_after"]
    lines = [
        "# The published distribution with the calendar-adjusted middle band (#418)", "", BEGIN, "",
        "**Generated by `scripts/calendar_bands_418.py render` from "
        "`docs/runs/published_distribution_calendar_daily_h1.json`; never hand-edited.**", "",
        "The middle band of the published distribution (the 25% to 75% range, and the median inside it) was "
        "recalibrated: each day's quantiles are shifted by what the recent misses on that kind of day "
        "(a turn of the month, quarter or tax date, a coupon settlement, or an ordinary day) say they should have been. "
        f"The setting is `{record['candidate']}`, as declared before it was scored in `{record['addendum']}` "
        f"(sha256 `{record['addendum_sha256'][:12]}`) and unchanged. It met the declared test on "
        f"{ba['2018-2025']['first']} to {ba['2018-2025']['last']} (#243) and held on {ba['2026']['first']} to "
        f"{ba['2026']['last']} (#408). **The 90% band is not adjusted**: its edges (the 5% and 95% quantiles) are "
        f"the published ones. The declared rule sorts each day's vector, so on {record['outer_edge_moved_days']} of "
        f"{len(record['days'])} days an adjusted middle value that crossed an edge became the edge: "
        + ("always outward, never inward. " if record["outer_edge_moves_outward_only"] else "inward on some days. ")
        + "The live record and the live pin are untouched.", "",
        "Gain is CRPS(before) - CRPS(after) per day in bp, so a positive mean favours the adjusted band; intervals are "
        "90% stationary bootstraps (block length 2). Coverage cells: coverage %, then the share of days below / above the band.",
        "", "## CRPS and pooled gain", "",
        "| Window | Days | CRPS before (bp) | CRPS after (bp) | Pooled gain, 90% interval |", "|---|---|---|---|---|"]
    for key in ba:
        b = ba[key]
        lines.append("| %s to %s | %d | %.3f | %.3f | %s |" % (
            b["first"], b["last"], b["days"], b["crps_before"], b["crps_after"], _gain(b["pooled_gain"])))
    for band, label in (("band_50", "50% band"), ("band_90", "90% band")):
        lines += ["", "## Coverage of the %s by day type" % label, "",
                  "A group of under 20 days is too few to read.", "",
                  "| Group | " + " | ".join("%s days | %s before | %s after" % (k, k, k) for k in ba) + " |",
                  "|---|" + "---|---|---|" * len(ba)]
        for group in SHOWN:
            cells = []
            for k in ba:
                c = ba[k]["coverage_by_group"]
                n = c["before"][group]["days"]
                if n < 20:
                    cells += [str(n), "%d days: too few" % n, "%d days: too few" % n]
                else:
                    cells += [str(n), _cov(c["before"][group], band), _cov(c["after"][group], band)]
            lines.append("| %s | %s |" % (group, " | ".join(cells)))
    lines += ["", END, ""]
    return "\n".join(lines)


def render_command(args) -> int:
    args.output.write_text(render(json.loads(args.record.read_text(encoding="utf-8"))), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
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
