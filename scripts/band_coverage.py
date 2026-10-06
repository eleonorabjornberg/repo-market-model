#!/usr/bin/env python3
"""The published distribution's band coverage, split by day type, regime and horizon (#265).

`README.md` said of the published distribution that "None of these models has" a
calibration finding, from one pooled interval (88.7%, 87.2% to 90.1%). The
project's own rule is to split a figure by regime and by pressure-day type, and
split that way the 90% band does not hold on tax dates, in the 2018-19 regime and
in 2024. This module is that split. It reads records and one tracked panel and
scores nothing: no model is run and no record in `docs/runs/` changes.

* **h = 1** comes from the origins of
  `docs/runs/backtest_gbm_conformal_pid_nested_funding.json`, which carry every
  scored day's five quantiles, outcome and side. The 50% band is the interval
  between the 25th and 75th percentiles, the 90% band the one between the 5th and
  95th, both closed (an outcome on an edge is inside), as the record's own
  `interval_coverage` is.
* **Day types** are the scheduled pressure-day tags of `scripts/desk_outputs.py`
  (`pressure_day_tags`): month-end, quarter-end, year-end, tax date and coupon
  settlement, read from the panel row's own calendar columns. A day may carry
  several, so those groups overlap; a day with none is "other". The panel is the
  tracked one, rebuilt from fixtures and refused unless its digest is the
  manifest's.
* **Intervals** resample the whole series, with the pooled interval's block length
  and seed, and average the resampled days of the group, as the record's other
  splits do. The pooled row's 90% interval is checked against the record's own
  `coverage_interval` and the build refuses if they differ.
* **A cell under `MINIMUM_DAYS` days** says so and is never flagged.
* **h = 2 to 5** have no per-origin series in any record. `v1_interior_diagnosis.json`
  carries their coverage by exclusive day type and regime as shares, so those are
  tabled from it, with no interval, and say so.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = str(ROOT / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from repo_model import metrics  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.onset import MINIMUM_EVENTS  # noqa: E402

RECORD = "backtest_gbm_conformal_pid_nested_funding.json"
DIAGNOSIS = "v1_interior_diagnosis.json"
MANIFEST = ROOT / "metadata" / "funding_panel_manifest.json"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
FIXTURES = "tests/fixtures/snapshots/funding_inputs"
#: The project's minimum size of a cell: the 20 of `onset.MINIMUM_EVENTS`
#: (`docs/decisions/pressure-probability.md`), here counted in days.
MINIMUM_DAYS = MINIMUM_EVENTS
TAGS = ("month_end", "quarter_end", "year_end", "tax_date", "coupon_settlement")
GROUPS = TAGS + ("other",)
BANDS = ((1, 3, 0.5), (0, 4, 0.9))  # (lower quantile index, upper, nominal)


class BandError(RuntimeError):
    """The records or the panel do not say what the table needs. Do not guess."""


def tags_for(values, when, month_end_window):
    """The scheduled pressure-day tags of a panel row, in `TAGS` order.

    The same rule as `desk_outputs.pressure_day_tags` (a test holds the two equal).
    """

    for column in ("days_to_month_end", "quarter_end", "tax_date"):
        if values.get(column) in (None, ""):
            raise ValueError("the row for %s carries no %r" % (when, column))
    tags = []
    if float(values["days_to_month_end"]) <= month_end_window:
        tags.append("month_end")
    if float(values["quarter_end"]) == 1.0:
        tags.append("quarter_end")
        if when.month == 12:
            tags.append("year_end")
    if float(values["tax_date"]) == 1.0:
        tags.append("tax_date")
    coupons = values.get("treasury_settlement_coupons")
    if coupons not in (None, "") and float(coupons) > 0.0:
        tags.append("coupon_settlement")
    return tuple(tags)


def build_panel_rows():
    """The published panel's rows, rebuilt from the tracked fixtures, by ISO date."""

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as directory:
        out = Path(directory) / "funding_panel.csv"
        done = subprocess.run(
            [sys.executable, "-m", "repo_model.cli", "build", "--raw-root", FIXTURES,
             "--output", str(out), "--build-cutoff", manifest["build_cutoff"],
             "--decision-time", manifest["decision_time"]],
            cwd=ROOT, capture_output=True, text=True,
            env={"PYTHONPATH": SRC, "PYTHONDONTWRITEBYTECODE": "1",
                 "PATH": os.environ.get("PATH", "/usr/bin:/bin")})
        if done.returncode:
            raise BandError("panel build failed: %s" % done.stderr.strip()[-400:])
        import hashlib
        data = out.read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest["sha256"]:
            raise BandError("the rebuilt panel is not the published one; refusing")
    return {row["date"]: row for row in csv.DictReader(data.decode().splitlines())}


def day_table(record, rows, splits):
    """One entry per scored day: date, regime, tags, both bands' hits and the 90% side."""

    origins = record["metrics"]["interval_calibration"].get("origins")
    if not origins:
        raise BandError("the record carries no per-origin block")
    days = []
    for origin in origins:
        iso = origin["scored_date"]
        if iso not in rows:
            raise BandError("scored day %s is not a row of the published panel" % iso)
        when = date.fromisoformat(iso)
        quantiles = origin["quantiles_bps"]
        actual = origin["actual_bps"]
        hits = {}
        for lower, upper, nominal in BANDS:
            hits[nominal] = 1.0 if quantiles[lower] <= actual <= quantiles[upper] else 0.0
        if (hits[0.9] == 1.0) != (origin["side"] == "inside"):
            raise BandError("the 90%% band disagrees with the record's side on %s" % iso)
        days.append({
            "date": iso,
            "regime": splits.regime(when),
            "tags": tags_for(rows[iso], when, splits.month_end_window),
            "hits": hits,
            "side": origin["side"],
        })
    return days


def _members(days, kind, name):
    if kind == "all":
        return [True] * len(days)
    if kind == "regime":
        return [day["regime"] == name for day in days]
    if name == "other":
        return [not day["tags"] for day in days]
    return [name in day["tags"] for day in days]


def cells(record, days, splits):
    """Every cell: `{"kind", "name", "days", "bands": {nominal: {...}}, "below", "above"}`."""

    calibration = record["metrics"]["interval_calibration"]
    interval = calibration["coverage_interval"]
    plan = [("all", "all days")]
    plan += [("day type", name) for name in GROUPS]
    plan += [("regime", label) for label in splits.regime_labels]
    masks = [_members(days, "all" if kind == "all" else
                      ("regime" if kind == "regime" else "tag"), name)
             for kind, name in plan]
    sizes = [sum(mask) for mask in masks]
    live = [k for k, size in enumerate(sizes) if size >= MINIMUM_DAYS]
    series = {nominal: [day["hits"][nominal] for day in days] for _, _, nominal in BANDS}

    def statistic(indices):
        sums = {nominal: [0.0] * len(plan) for nominal in series}
        counts = [0] * len(plan)
        for index in indices:
            for k in live:
                if masks[k][index]:
                    counts[k] += 1
                    for nominal in series:
                        sums[nominal][k] += series[nominal][index]
        out = []
        for nominal in series:
            out.extend(sums[nominal][k] / counts[k] if counts[k] else float("nan")
                       for k in live)
        return out

    spans = metrics.stationary_bootstrap_intervals(
        statistic, len(days), block_length=interval["block_length"],
        seed=interval["seed"], replications=interval["replications"],
        level=interval["level"])
    where = {}
    for slot, nominal in enumerate(series):
        for position, k in enumerate(live):
            where[(nominal, k)] = spans[slot * len(live) + position]
    out = []
    for k, (kind, name) in enumerate(plan):
        member = [day for day, keep in zip(days, masks[k]) if keep]
        cell = {"kind": kind, "name": name, "days": sizes[k], "enough": k in live,
                "bands": {}, "below": sum(day["side"] == "below" for day in member),
                "above": sum(day["side"] == "above" for day in member)}
        for nominal in series:
            share = sum(day["hits"][nominal] for day in member) / len(member) if member else None
            low, high = where.get((nominal, k), (None, None))
            excludes = k in live and not (low <= nominal <= high)
            cell["bands"][nominal] = {"coverage": share, "lower": low, "upper": high,
                                      "excludes": bool(excludes)}
        out.append(cell)
    pooled = out[0]["bands"][0.9]
    if abs(pooled["lower"] - interval["lower"]) > 1e-12 or abs(pooled["upper"] - interval["upper"]) > 1e-12:
        raise BandError("the pooled 90%% interval does not reproduce the record's own "
                        "(%.6f to %.6f against %.6f to %.6f)" % (
                            pooled["lower"], pooled["upper"], interval["lower"], interval["upper"]))
    return out


def excluded(table):
    """The cells whose interval excludes their nominal level: `(band label, cell)`, in table order."""

    return [("%d%%" % round(nominal * 100), cell)
            for cell in table for nominal in (0.5, 0.9)
            if cell["bands"][nominal]["excludes"]]


def _pct(value):
    return "%.1f%%" % (100.0 * value)


def horizon_cells(diagnosis):
    """h = 2 to 5 coverage shares by exclusive day type and regime, from the diagnosis record.

    Each is `{"horizon", "kind", "name", "days", "band_50", "band_90", "miss_below", "miss_above"}`
    in percent, the half-edge definition (an outcome exactly on an edge counts one half).
    """

    out = []
    for horizon in (2, 3, 4, 5):
        block = diagnosis["q1_calibration"]["h%d_2018_2025" % horizon]
        pooled = block["issued"]
        out.append({"horizon": horizon, "kind": "all", "name": "all days", "days": pooled["days"],
                    "band_50": pooled["band_50_half_edge"], "band_90": pooled["band_90_half_edge"],
                    "miss_below": pooled["band_50_miss_below"], "miss_above": pooled["band_50_miss_above"]})
        for kind, key in (("day type", "by_day_type"), ("regime", "by_regime")):
            for name, entry in block["splits"][key].items():
                if not entry.get("days"):
                    continue
                out.append({"horizon": horizon, "kind": kind, "name": name.replace("_", " "),
                            "days": entry["days"], "band_50": entry["band_50_half_edge"],
                            "band_90": entry["band_90_half_edge"],
                            "miss_below": entry["band_50_miss_below"],
                            "miss_above": entry["band_50_miss_above"]})
    return out


def cell_label(cell):
    return cell["name"].replace("_", " ")


def finding_sentence(table):
    """The sentence the README carries in place of the pooled one: every excluding cell, named."""

    found = excluded(table)
    if not found:
        return ("Split by pressure-day type and regime (`%s`), no cell of at least %d days "
                "has an interval that excludes its nominal coverage." % (PATH, MINIMUM_DAYS))
    names = "; ".join("%s band on %s (%s, %s to %s)" % (
        band, "%s %s" % (cell["kind"], cell_label(cell)) if cell["kind"] != "all" else "all days",
        _pct(cell["bands"][0.5 if band == "50%" else 0.9]["coverage"]),
        _pct(cell["bands"][0.5 if band == "50%" else 0.9]["lower"]),
        _pct(cell["bands"][0.5 if band == "50%" else 0.9]["upper"])) for band, cell in found)
    return ("Split by pressure-day type and regime (`%s`), the published distribution's "
            "h = 1 bands do not hold on %d cells, each an interval that excludes the nominal "
            "level: %s." % (PATH, len(found), names))


PATH = "docs/band_coverage_by_split.md"  # emit_results.BAND_PAGE


def render(record, table, diagnosis_cells, days):
    """The reported-only page, as Markdown."""

    n = len(days)
    calibration = record["metrics"]["interval_calibration"]["coverage_interval"]
    lines = [
        "# Band coverage by day type, regime and horizon",
        "",
        "<!-- generated: band-coverage -->",
        "",
        "**Generated by `scripts/emit_results.py` from `scripts/band_coverage.py`; never hand-edited.** "
        "Reported only: no new scoring, and no record in `docs/runs/` changes.",
        "",
        "The published distribution (`docs/runs/%s`) at h = 1, **%d origins**, %s to %s. "
        "A band's coverage is the share of scored days whose outcome fell inside it, edges "
        "included. The 50%% band runs from the 25th to the 75th percentile and the 90%% band "
        "from the 5th to the 95th. Each interval is a stationary bootstrap on the whole series "
        "(block length %d, seed %d, %d replications) averaging the resampled days of the "
        "group, the pooled row's 90%% interval reproducing the record's own. A cell with "
        "fewer than %d days is marked **too few days** (the project's minimum of %d, "
        "`onset.MINIMUM_EVENTS`, counted in days) and is never flagged. Day-type groups "
        "overlap, because a day can carry several tags; a day with none is `other`."
        % (RECORD, n, days[0]["date"], days[-1]["date"], calibration["block_length"],
           calibration["seed"], calibration["replications"], MINIMUM_DAYS, MINIMUM_DAYS),
        "",
        "| Split | Group | Days | 50% band | 50% interval | 90% band | 90% interval | "
        "90% misses below | 90% misses above | Excludes nominal |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cell in table:
        if not cell["enough"]:
            lines.append("| %s | %s | %d | too few days (under %d) | | too few days (under %d) | | "
                         "%d | %d | |" % (cell["kind"], cell_label(cell), cell["days"], MINIMUM_DAYS,
                                         MINIMUM_DAYS, cell["below"], cell["above"]))
            continue
        flags = [band for band, _ in excluded([cell])]
        row = [cell["kind"], cell_label(cell), str(cell["days"])]
        for nominal in (0.5, 0.9):
            band = cell["bands"][nominal]
            row += [_pct(band["coverage"]), "%s to %s" % (_pct(band["lower"]), _pct(band["upper"]))]
        row += ["%d (%s)" % (cell["below"], _pct(cell["below"] / cell["days"])),
                "%d (%s)" % (cell["above"], _pct(cell["above"] / cell["days"])),
                ", ".join(flags) or "no"]
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "## h = 2 to 5",
        "",
        "No record carries a per-origin series at h = 2 to 5, so there is **no interval** here "
        "and a bootstrap would need new scoring. The shares are `docs/runs/%s`' "
        "(question 1, 2018-06-29 to 2025-12-31), by its four exclusive day types and by regime, "
        "with an outcome exactly on an edge counting one half. Misses are shares of the 50%% band's "
        "days. A cell with fewer than %d days is marked **too few days**." % (DIAGNOSIS, MINIMUM_DAYS),
        "",
        "| h | Split | Group | Days | 50% band | 90% band | 50% misses below | 50% misses above |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cell in diagnosis_cells:
        if cell["days"] < MINIMUM_DAYS:
            lines.append("| %d | %s | %s | %d | too few days (under %d) | too few days (under %d) | | |"
                         % (cell["horizon"], cell["kind"], cell["name"], cell["days"],
                            MINIMUM_DAYS, MINIMUM_DAYS))
            continue
        lines.append("| %d | %s | %s | %d | %.1f%% | %.1f%% | %.1f%% | %.1f%% |" % (
            cell["horizon"], cell["kind"], cell["name"], cell["days"], cell["band_50"],
            cell["band_90"], cell["miss_below"], cell["miss_above"]))
    lines += ["", "<!-- end generated: band-coverage -->", ""]
    return "\n".join(lines)


def compute(runs):
    """`(record, table, diagnosis_cells, days)` from the records in `runs`."""

    record = json.loads((runs / RECORD).read_text(encoding="utf-8"))
    diagnosis = json.loads((runs / DIAGNOSIS).read_text(encoding="utf-8"))
    splits = load_split_declaration(SPLITS)
    days = day_table(record, build_panel_rows(), splits)
    return record, cells(record, days, splits), horizon_cells(diagnosis), days
