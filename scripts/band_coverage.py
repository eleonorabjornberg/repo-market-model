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
* **h = 2 to 5** (#290) come from `docs/runs/published_distribution_daily_h{2..5}.json`,
  the same published distribution walked at each horizon (`scripts/forecast_daily.py
  --horizon H`), kept over the h = 1 record's own window and no later day. Their cells
  are built exactly as h = 1's, with the h = 1 record's block length, seed and
  replications. No record has a pooled interval they reproduce, so each horizon's pooled
  shares are checked against `v1_interior_diagnosis.json`'s (`check_against_diagnosis`),
  which was walked separately.
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
LATER_HORIZONS = (2, 3, 4, 5)
DAILY = "published_distribution_daily_h%d.json"
DAILY_PATTERN = "published_distribution_daily_h{2..5}.json"
LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
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


def daily_day_table(daily, rows, splits, last):
    """`day_table`'s entries for a daily record (h = 2 to 5): the same fields, from its quantiles.

    Refuses a day after `last`, the h = 1 record's own last scored day: a later day is outside
    the window the table is for (and, past 2026-09-03, locked).
    """

    if daily["levels"] != LEVELS:
        raise BandError("h = %s levels are %s" % (daily["horizon"], daily["levels"]))
    days = []
    for entry in daily["days"]:
        iso = entry["date"]
        if iso > last:
            raise BandError("the h = %s record holds %s, after the window's last day %s"
                            % (daily["horizon"], iso, last))
        if iso not in rows:
            raise BandError("scored day %s is not a row of the published panel" % iso)
        when = date.fromisoformat(iso)
        quantiles = entry["quantiles_bps"]
        actual = entry["actual_bps"]
        hits = {}
        for lower, upper, nominal in BANDS:
            hits[nominal] = 1.0 if quantiles[lower] <= actual <= quantiles[upper] else 0.0
        side = "below" if actual < quantiles[0] else "above" if actual > quantiles[4] else "inside"
        days.append({"date": iso, "regime": splits.regime(when),
                     "tags": tags_for(rows[iso], when, splits.month_end_window),
                     "hits": hits, "side": side})
    return days


def _members(days, kind, name):
    if kind == "all":
        return [True] * len(days)
    if kind == "regime":
        return [day["regime"] == name for day in days]
    if name == "other":
        return [not day["tags"] for day in days]
    return [name in day["tags"] for day in days]


def cells(record, days, splits, check=True):
    """Every cell: `{"kind", "name", "days", "bands": {nominal: {...}}, "below", "above"}`.

    The bootstrap is the `record`'s own (block length, seed, replications). With `check` the
    pooled 90% interval must reproduce the record's; h = 2 to 5 have no such record and pass
    `check=False`.
    """

    calibration = record["metrics"]["interval_calibration"]
    interval = calibration["coverage_interval"]
    plan = [("all", "all days")]
    plan += [("day type", name) for name in GROUPS]
    plan += [("regime", label) for label in splits.regime_labels]
    masks = [_members(days, "all" if kind == "all" else
                      ("regime" if kind == "regime" else "tag"), name)
             for kind, name in plan]
    # A declared regime that no scored day falls in (a regime declared ahead of its days) has no row.
    kept = [k for k, mask in enumerate(masks) if sum(mask) or plan[k][0] != "regime"]
    plan = [plan[k] for k in kept]
    masks = [masks[k] for k in kept]
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
    if check and (abs(pooled["lower"] - interval["lower"]) > 1e-12
                  or abs(pooled["upper"] - interval["upper"]) > 1e-12):
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


def check_against_diagnosis(horizon, days, diagnosis):
    """A horizon's pooled and per-regime shares against `v1_interior_diagnosis.json`'s.

    The diagnosis walked the same distribution separately (`scripts/interior_diagnosis.py walk`).
    It counts an outcome within `TIE_BPS` (1e-9 bp) of a band edge as on the edge, while this table
    counts an outcome on the edge only when it is exactly there, as the h = 1 record does. So the
    exact share must lie between the diagnosis's open share (an edge outcome outside) and its
    closed share (inside), and the day counts must be equal. Raises `BandError` otherwise.
    """

    block = diagnosis["q1_calibration"]["h%d_2018_2025" % horizon]

    def share(subset, nominal):
        return 100.0 * sum(day["hits"][nominal] for day in subset) / len(subset)

    def require(subset, nominal, opened, closed, where):
        value = share(subset, nominal)
        if not opened - 1e-9 <= value <= closed + 1e-9:
            raise BandError("h = %d, %s: the %d%% band's share is %.6f, outside the diagnosis's "
                            "%.6f to %.6f" % (horizon, where, round(100 * nominal), value, opened, closed))

    pooled = block["issued"]
    if len(days) != pooled["days"]:
        raise BandError("h = %d: %d days, the diagnosis has %d" % (horizon, len(days), pooled["days"]))
    require(days, 0.5, pooled["band_50_open"], pooled["band_50_closed"], "pooled")
    require(days, 0.9, pooled["band_90_open"], pooled["band_90_closed"], "pooled")
    for name, entry in block["splits"]["by_regime"].items():
        subset = [day for day in days if day["regime"] == name]
        if len(subset) != entry.get("days", 0):
            raise BandError("h = %d, regime %s: %d days, the diagnosis has %s"
                            % (horizon, name, len(subset), entry.get("days", 0)))
        if subset:
            closed = entry["band_50_closed"]
            require(subset, 0.5, 2.0 * entry["band_50_half_edge"] - closed, closed, "regime " + name)


def cell_label(cell):
    return cell["name"].replace("_", " ")


def _names(found):
    def figures(band, cell):
        return cell["bands"][0.5 if band == "50%" else 0.9]

    return "; ".join("%s band on %s (%s, %s to %s)" % (
        band, "%s %s" % (cell["kind"], cell_label(cell)) if cell["kind"] != "all" else "all days",
        _pct(figures(band, cell)["coverage"]), _pct(figures(band, cell)["lower"]),
        _pct(figures(band, cell)["upper"])) for band, cell in found)


def finding_sentence(table, later=()):
    """The sentence the README carries in place of the pooled one: every excluding cell, named.

    `table` is h = 1's cells, `later` the h = 2 to 5 horizons (`{"horizon", "table", ...}`), each
    named in turn, so no excluding cell at any horizon goes unsaid.
    """

    horizons = [(1, table)] + [(entry["horizon"], entry["table"]) for entry in later]
    counted = [(h, excluded(cells_)) for h, cells_ in horizons]
    span = "h = 1" if not later else "h = 1 to %d" % horizons[-1][0]
    total = sum(len(found) for _, found in counted)
    if not total:
        return ("Split by pressure-day type and regime (`%s`), no cell of at least %d days "
                "at %s has an interval that excludes its nominal coverage." % (PATH, MINIMUM_DAYS, span))
    parts = ["at h = %d, %s" % (h, "%d %s: %s" % (len(found), "cell" if len(found) == 1 else "cells",
                                                   _names(found)) if found else "none")
             for h, found in counted]
    return ("Split by pressure-day type and regime (`%s`), the published distribution's %s "
            "bands do not hold on %d cells, each an interval that excludes the nominal "
            "level: %s." % (PATH, span, total, "; ".join(parts)))


PATH = "docs/band_coverage_by_split.md"  # emit_results.BAND_PAGE


def _rows(table):
    lines = []
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
    return lines


HEADER = ["| Split | Group | Days | 50% band | 50% interval | 90% band | 90% interval | "
          "90% misses below | 90% misses above | Excludes nominal |",
          "|---|---|---|---|---|---|---|---|---|---|"]


def render(record, table, later, days):
    """The reported-only page, as Markdown."""

    n = len(days)
    calibration = record["metrics"]["interval_calibration"]["coverage_interval"]
    lines = [
        "# Band coverage by day type, regime and horizon",
        "",
        "<!-- generated: band-coverage -->",
        "",
        "**Generated by `scripts/emit_results.py` from `scripts/band_coverage.py`; never hand-edited.** "
        "Reported only: the records it reads are scored elsewhere, and no record in `docs/runs/` changes.",
        "",
        "The published distribution at h = 1 (`docs/runs/%s`), **%d origins**, %s to %s, and at "
        "h = 2 to 5 (`docs/runs/%s`, from `scripts/forecast_daily.py --horizon H`, the same "
        "walk, kept over the same window). A band's coverage is the share of scored days whose "
        "outcome fell inside it, edges included. The 50%% band runs from the 25th to the 75th "
        "percentile and the 90%% band from the 5th to the 95th. Each interval is a stationary "
        "bootstrap on the whole series (block length %d, seed %d, %d replications, the h = 1 "
        "record's, for every horizon) averaging the resampled days of the group; the pooled h = 1 "
        "90%% interval reproduces the record's own, and each later horizon's pooled shares "
        "agree with `docs/runs/%s`', which walked the same distribution separately and counts an "
        "outcome within 1e-9 bp of an edge as on it. A cell with fewer than %d days is marked **too few "
        "days** (the project's minimum of %d, `onset.MINIMUM_EVENTS`, counted in days) and is "
        "never flagged. Day-type groups overlap, because a day can carry several tags; a day with "
        "none is `other`."
        % (RECORD, n, days[0]["date"], days[-1]["date"], DAILY_PATTERN, calibration["block_length"],
           calibration["seed"], calibration["replications"], DIAGNOSIS, MINIMUM_DAYS, MINIMUM_DAYS),
        "",
        "## h = 1",
        "",
    ] + HEADER + _rows(table)
    for entry in later:
        lines += ["", "## h = %d" % entry["horizon"], "",
                  "%d scored days, %s to %s." % (len(entry["days"]), entry["days"][0]["date"],
                                                 entry["days"][-1]["date"]), ""]
        lines += HEADER + _rows(entry["table"])
    lines += ["", "<!-- end generated: band-coverage -->", ""]
    return "\n".join(lines)


def compute(runs):
    """`(record, table, later, days)` from the records in `runs`.

    `later` is `[{"horizon", "days", "table"}]` for h = 2 to 5, each reproduced against the
    diagnosis record before it is returned.
    """

    record = json.loads((runs / RECORD).read_text(encoding="utf-8"))
    diagnosis = json.loads((runs / DIAGNOSIS).read_text(encoding="utf-8"))
    splits = load_split_declaration(SPLITS)
    rows = build_panel_rows()
    days = day_table(record, rows, splits)
    later = []
    for horizon in LATER_HORIZONS:
        daily = json.loads((runs / (DAILY % horizon)).read_text(encoding="utf-8"))
        if daily["horizon"] != horizon:
            raise BandError("%s is the record of h = %s" % (DAILY % horizon, daily["horizon"]))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if daily["panel_sha256"] != manifest["sha256"]:
            raise BandError("h = %d was scored on a panel that is not the published one" % horizon)
        entries = daily_day_table(daily, rows, splits, days[-1]["date"])
        check_against_diagnosis(horizon, entries, diagnosis)
        later.append({"horizon": horizon, "days": entries,
                      "table": cells(record, entries, splits, check=False)})
    return record, cells(record, days, splits), later, days
