#!/usr/bin/env python3
"""Snapshots, scratch panel and screen for the new data sources (#630).

An exploratory measurement, not a record: nothing is selected, no model changes, no published
figure moves, and no day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

Step 2, the snapshots (each is one plain request per URL, made by the repository's own fetch code):

    PYTHONPATH=src python3 -m repo_model.cli fetch fr2004 --output-root /tmp/pd_export
    PYTHONPATH=src python3 scripts/new_sources.py extract-pd /tmp/pd_export/nyfed_fr2004/<export>.csv
    PYTHONPATH=src python3 scripts/new_sources.py fetch-dts

`extract-pd` cuts the five series `repo_model.new_sources.PD_SERIES` reads, up to 2025-12-31, out of the
26 MB export, copying lines byte for byte, and records the export's digest and size beside the extract
(the posture of `scripts/extract_fr2004.py`). `--check` recomputes the extract from the export and
compares. `fetch-dts` takes the Daily Treasury Statement's debt cash lines for 2018 to 2025.

The weeks the New York Fed withheld, and the panel days the 13-day carry leaves empty (#680):

    PYTHONPATH=src python3 scripts/new_sources.py withheld --panel SCREEN.csv --output docs/pivot/evidence/new-sources-capped/withheld.json

The auction results and the Desk's operation records are read from snapshots already tracked
(`tests/fixtures/snapshots/treasury_auctions/`, `.../on_rrp_inputs/`); nothing is fetched for them.

Step 3, the scratch panel and the screen of the ordinary days (scratch panels as in `scripts/source_screen.py`):

    PYTHONPATH=src python3 scripts/new_sources.py panel --panel SCREEN.csv --output NEW.csv
    PYTHONPATH=src python3 scripts/new_sources.py screen --panel NEW.csv --output docs/pivot/evidence/new-sources

* `panel` adds the ten columns of `repo_model.new_sources.COLUMN_FIELDS` to #478's joined scratch panel
  (which stops at 2025-12-31), from the tracked snapshots.
* `screen` reads every series as of each decision instant with the as-of rule, at the leads of
  `source_screen.LEADS`, exactly as #478 does, and keeps the *ordinary days*: scored days whose pressure-day
  type is `ordinary` (not a quarter-end, month-end or tax date) and that settle no coupon. For each series it
  writes the Spearman correlation with the three targets, the AUROC of the +5 bp indicator against the other
  ordinary days, and the pre-onset contrast for the onsets that fall on ordinary days, with 90 % bootstrap
  intervals (days resampled independently, so serial dependence is not respected and the intervals are too
  narrow), split by the as-of reserve-scarcity band and state; the rank correlation with the target after the
  scarcity state and the tail spread (`sofr_p99_iorb_bps`, #601) are taken out; and the inter-source Spearman
  matrix, pooled and by band, with clusters at |rho| >= 0.8. Every statistical test is counted. Nothing is
  corrected for multiplicity, and nothing is selected.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import random
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import new_sources  # noqa: E402

ROOT = REPO / "tests" / "fixtures" / "snapshots" / "new_sources"
PD_EXTRACT = ROOT / "nyfed_pd_financing" / "pd_financing_extract.csv"
FIRST_DTS_YEAR_START = "2018-01-01"


def cut_pd(raw: bytes) -> bytes:
    """The export's header and the lines of `PD_SERIES` dated up to `END`, byte for byte."""

    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    wanted = set(new_sources.PD_SERIES.values())
    out = [lines[0]]
    for line in lines[1:]:
        row = next(csv.reader([line]))
        if row[1] in wanted and date.fromisoformat(row[0]) <= new_sources.END:
            out.append(line)
    return "".join(out).encode("utf-8")


def pd_sidecar(export: bytes, export_manifest: dict, extract: bytes) -> dict:
    series: Dict[str, List[str]] = {}
    for row in csv.DictReader(io.StringIO(extract.decode("utf-8"))):
        series.setdefault(row["Time Series"], []).append(row["As Of Date"])
    return {
        "source_id": new_sources.SOURCE_PD,
        "url": new_sources.PD_EXPORT_URL,
        "retrieved_at": export_manifest.get("retrieved_at"),
        "export_sha256": hashlib.sha256(export).hexdigest(),
        "export_byte_count": len(export),
        "extract_sha256": hashlib.sha256(extract).hexdigest(),
        "extract_byte_count": len(extract),
        "kept": "the series of repo_model.new_sources.PD_SERIES, dated up to 2025-12-31, lines copied byte for byte",
        "series": {name: {"first": min(days), "last": max(days), "rows": len(days)} for name, days in sorted(series.items())},
    }


def extract_pd_command(args) -> int:
    export_path = Path(args.export)
    export = export_path.read_bytes()
    manifest_path = export_path.with_name(export_path.name + ".manifest.json")
    export_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    extract = cut_pd(export)
    sidecar = pd_sidecar(export, export_manifest, extract)
    sidecar_path = PD_EXTRACT.with_name(PD_EXTRACT.name + ".manifest.json")
    text = json.dumps(sidecar, indent=2, sort_keys=True) + "\n"
    if args.check:
        committed = json.loads(sidecar_path.read_text())
        same = PD_EXTRACT.read_bytes() == extract and committed["export_sha256"] == sidecar["export_sha256"]
        print("extract matches" if same else "extract DIFFERS")
        return 0 if same else 1
    PD_EXTRACT.parent.mkdir(parents=True, exist_ok=True)
    PD_EXTRACT.write_bytes(extract)
    sidecar_path.write_text(text)
    print(json.dumps({"extract_bytes": len(extract), "export_sha256": sidecar["export_sha256"]}))
    return 0


def fetch_dts_command(args) -> int:
    artifacts = new_sources.fetch_dts_debt_cash(ROOT, args.start, args.end)
    print(json.dumps([{"url": a.url, "sha256": a.sha256, "bytes": a.byte_count} for a in artifacts], indent=1))
    return 0


# -- step 3: the scratch panel and the screen of the ordinary days -----------------------------

_spec = importlib.util.spec_from_file_location("source_screen", REPO / "scripts" / "source_screen.py")
screen = importlib.util.module_from_spec(_spec)
sys.modules["source_screen"] = screen
_spec.loader.exec_module(screen)

from unittest import mock  # noqa: E402

from repo_model import measurement_fields, pressure, risk_dates  # noqa: E402
from repo_model.data import DailyObservation, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

BOOTSTRAPS = 300
INTERVAL = (0.05, 0.95)
CLUSTER_THRESHOLD = 0.8
TAIL = "sofr_p99_iorb_bps"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
ON_RRP_DIR = REPO / "tests" / "fixtures" / "snapshots" / "on_rrp_inputs" / "nyfed_on_rrp"
AUCTIONS = REPO / "tests" / "fixtures" / "snapshots" / "treasury_auctions" / "auctions_2018_present.json"
DTS_DIR = ROOT / "treasury_dts_debt_cash"


def new_series() -> Dict[str, Dict[date, float]]:
    """Every new column's values, from the tracked snapshots."""

    out: Dict[str, Dict[date, float]] = {}
    out.update(new_sources.parse_pd_export(PD_EXTRACT.read_bytes()))
    out.update(new_sources.parse_auction_results(AUCTIONS.read_bytes()))
    counts: Dict[date, float] = {}
    amended: set = set()
    for path in sorted(ON_RRP_DIR.glob("*.json")):
        if path.name.endswith("manifest.json"):
            continue
        got = new_sources.parse_on_rrp_counterparties(path.read_bytes())
        counts.update(got["rrp_counterparties"])
        amended.update(got["amended_days"])
    out["rrp_counterparties"] = {d: v for d, v in counts.items() if d not in amended}
    payloads = [p.read_bytes() for p in sorted(DTS_DIR.glob("*.json")) if not p.name.endswith("manifest.json")]
    out.update(new_sources.parse_dts_debt_cash(payloads))
    return out


def withheld_command(args) -> int:
    """The weeks the New York Fed withheld, by column, and the days the 13-day carry leaves as holes (#680)."""

    payload = PD_EXTRACT.read_bytes()
    suppressed = new_sources.parse_pd_suppressed(payload)
    values = new_sources.parse_pd_export(payload)
    rows = load_daily_panel(args.panel)
    capped = new_sources.add_columns(rows, values)
    out = {}
    for column in new_sources.PD_SERIES:
        weeks = suppressed[column]
        out[column] = {
            "weeks_in_extract": len(values[column]) + len(weeks),
            "withheld": new_sources.summarise_suppressed(weeks),
            "longest_run": _longest_run(weeks),
            "days_with_a_value_capped": sum(1 for r in capped if r.values.get(column) is not None),
            "days_with_a_value_uncapped": _uncapped_days(rows, values[column]),
        }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


def _longest_run(weeks) -> Optional[List[str]]:
    best: List[date] = []
    run: List[date] = []
    for day in sorted(weeks):
        run = run + [day] if run and (day - run[-1]).days == 7 else [day]
        if len(run) > len(best):
            best = run
    return [best[0].isoformat(), best[-1].isoformat()] if best else None


def _uncapped_days(rows, series) -> int:
    """Panel days with a value under the rule #630 used: carried with no limit (the behaviour #680 removes)."""

    starts = sorted(series)
    cursor, count, seen = 0, 0, False
    for row in rows:
        while cursor < len(starts) and starts[cursor] <= row.date:
            cursor += 1
            seen = True
        count += 1 if seen else 0
    return count


def panel_command(args) -> int:
    rows = load_daily_panel(args.panel)
    with args.panel.open(newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle))
    series = new_series()
    built = new_sources.add_columns(rows, series)
    columns = list(header[1:]) + [c for c in new_sources.COLUMN_FIELDS if c not in header]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date"] + columns)
        for row in built:
            writer.writerow([row.date.isoformat()] + [screen._cell(row.values.get(c)) for c in columns])
    present = {c: sum(1 for r in built if r.values.get(c) is not None) for c in new_sources.COLUMN_FIELDS}
    print(json.dumps({"rows": len(built), "columns": len(columns), "days_with_a_value": present}, indent=1))
    return 0


def auroc(positive: List[float], negative: List[float]) -> Optional[float]:
    if not positive or not negative:
        return None
    ranks = screen.average_ranks(list(positive) + list(negative))
    rank_sum = sum(ranks[: len(positive)])
    return (rank_sum - len(positive) * (len(positive) + 1) / 2.0) / (len(positive) * len(negative))


def seeded(*parts) -> random.Random:
    return random.Random(int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:12], 16))


def interval(draws: List[float]) -> Optional[List[float]]:
    if len(draws) < BOOTSTRAPS // 2:
        return None
    draws = sorted(draws)
    return [draws[int(INTERVAL[0] * (len(draws) - 1))], draws[int(INTERVAL[1] * (len(draws) - 1))]]


def auroc_with_interval(pairs: List[Tuple[float, float]], name: str, lead: int) -> dict:
    """AUROC of the indicator on `(value, indicator)` pairs, with a 90 % bootstrap interval."""

    pos = [v for v, y in pairs if y > 0]
    neg = [v for v, y in pairs if y <= 0]
    point = auroc(pos, neg) if len(pos) >= screen.MINIMUM_PRESSURE and len(neg) >= 1 and len(pairs) >= screen.MINIMUM_DAYS else None
    entry = {"n": len(pairs), "pressure_days": len(pos), "auroc": point, "interval": None}
    if point is None:
        return entry
    rng = seeded("auroc", name, lead)
    draws = []
    for _ in range(BOOTSTRAPS):
        sample = [pairs[rng.randrange(len(pairs))] for _ in range(len(pairs))]
        a = auroc([v for v, y in sample if y > 0], [v for v, y in sample if y <= 0])
        if a is not None:
            draws.append(a)
    entry["interval"] = interval(draws)
    return entry


def contrast_with_interval(pre: List[float], other: List[float], name: str) -> Optional[dict]:
    point = screen.pre_onset_contrast(pre, other)
    if point is None or len(pre) < 3:
        return None
    rng = seeded("pre", name)
    auc_d: List[float] = []
    sd_d: List[float] = []
    for _ in range(BOOTSTRAPS):
        p = [pre[rng.randrange(len(pre))] for _ in range(len(pre))]
        o = [other[rng.randrange(len(other))] for _ in range(len(other))]
        c = screen.pre_onset_contrast(p, o)
        if c is not None:
            auc_d.append(c["auc"])
            if c["std_diff"] is not None:
                sd_d.append(c["std_diff"])
    point["auc_interval"] = interval(auc_d)
    point["std_diff_interval"] = interval(sd_d)
    return point


def residuals(y: List[float], controls: List[List[float]]) -> List[float]:
    """`y` less its least-squares fit on an intercept and `controls` (normal equations)."""

    k = len(controls) + 1
    x = [[1.0] + [c[i] for c in controls] for i in range(len(y))]
    a = [[sum(x[r][i] * x[r][j] for r in range(len(y))) for j in range(k)] for i in range(k)]
    b = [sum(x[r][i] * y[r] for r in range(len(y))) for i in range(k)]
    for i in range(k):
        pivot = max(range(i, k), key=lambda r: abs(a[r][i]))
        a[i], a[pivot], b[i], b[pivot] = a[pivot], a[i], b[pivot], b[i]
        if abs(a[i][i]) < 1e-12:
            raise ValueError("controls are collinear")
        for r in range(i + 1, k):
            f = a[r][i] / a[i][i]
            for c in range(i, k):
                a[r][c] -= f * a[i][c]
            b[r] -= f * b[i]
    beta = [0.0] * k
    for i in reversed(range(k)):
        beta[i] = (b[i] - sum(a[i][c] * beta[c] for c in range(i + 1, k))) / a[i][i]
    return [y[r] - sum(beta[c] * x[r][c] for c in range(k)) for r in range(len(y))]


def partial_spearman(x: List[float], y: List[float], controls: List[List[float]]) -> Optional[float]:
    rx, ry = screen.average_ranks(x), screen.average_ranks(y)
    rc = [screen.average_ranks(c) for c in controls]
    try:
        return screen.pearson(residuals(rx, rc), residuals(ry, rc))
    except ValueError:
        return None


def clusters(names: List[str], rho: Dict[Tuple[str, str], Optional[float]], observed: Dict[str, int]) -> List[dict]:
    """Redundant groups: a representative and every unassigned series with |rho| >= the threshold against it.

    Greedy, most observed days first (ties by name), so a group is never chained through a series that
    is only close to a member: every member is within the threshold of the representative itself.
    """

    def r(a, b):
        return rho.get((a, b), rho.get((b, a)))

    left = sorted(names, key=lambda n: (-observed[n], n))
    out = []
    while left:
        rep = left.pop(0)
        members = [rep] + [n for n in left if r(rep, n) is not None and abs(r(rep, n)) >= CLUSTER_THRESHOLD]
        left = [n for n in left if n not in members]
        out.append({"representative": rep, "members": sorted(members)})
    return sorted(out, key=lambda g: (-len(g["members"]), g["representative"]))


def screen_command(args) -> int:
    rows = load_daily_panel(args.panel)
    if rows[-1].date > new_sources.END:
        raise SystemExit(f"the panel runs past {new_sources.END}; a screen reads no day in a locked tier")
    registry = measurement_fields.load_registry()
    base_switched = screen.switched_on_fields

    def switched():
        merged = dict(base_switched())
        merged.update(new_sources.COLUMN_FIELDS)
        return merged

    with mock.patch.object(screen, "switched_on_fields", switched), screen.Switched():
        columns = screen.screened_columns(rows)
        readable, unreadable = screen.probe(registry, columns, rows)
        scored, series, not_public, kinds = screen.read_series(rows, registry, readable)
    position = {row.date: i for i, row in enumerate(rows)}
    values_of = {row.date: row.values for row in rows}
    splits = load_split_declaration(SPLITS)
    ordinary = [
        i
        for i, d in enumerate(scored)
        if not risk_dates.is_risk_date(values_of[d], risk_dates.NON_ORDINARY, splits=splits)
    ]
    spreads = [row.spread_bps for row in rows]
    targets = {
        "level": [spreads[position[d]] for d in scored],
        "change": [spreads[position[d]] - spreads[position[d] - 1] for d in scored],
        "pressure": [1.0 if exceeds_bp(spreads[position[d]], screen.THRESHOLD_BP) else 0.0 for d in scored],
    }
    ordinary_set = set(ordinary)
    onsets = [d for d in pressure.onsets(rows, screen.THRESHOLD_BP, scored) if scored.index(d) in ordinary_set]
    scored_index = {d: i for i, d in enumerate(scored)}
    pre_days = set()
    for onset in onsets:
        for back in range(screen.PRE_ONSET_DAYS[0], screen.PRE_ONSET_DAYS[1] + 1):
            day = rows[position[onset] - back].date
            if day in scored_index and scored_index[day] in ordinary_set:
                pre_days.add(scored_index[day])
    pre_index = sorted(pre_days)
    other_index = [i for i in ordinary if i not in pre_days]
    state = {lead: series[lead][screen.SCARCITY] for lead in screen.LEADS}
    band = lambda lead, i: screen.band(state[lead][i])  # noqa: E731
    tests = {"spearman": 0, "auroc": 0, "pre_onset": 0, "partial": 0, "inter_source": 0}
    new_columns = set(new_sources.COLUMN_FIELDS)

    out_series: Dict[str, dict] = {}
    for column in readable + [screen.SPREAD_LAG]:
        per_lead = {}
        for lead in screen.LEADS:
            x = series[lead][column]
            groups = {"ordinary": ordinary}
            for name in screen.BANDS:
                groups[f"band:{name}"] = [i for i in ordinary if band(lead, i) == name]
            if lead == 1:
                for s in (0, 1, 2, 3):
                    groups[f"state:{s}"] = [i for i in ordinary if state[lead][i] == float(s)]
            cell = {}
            for name, idx in groups.items():
                corr = screen.correlate(x, targets, idx)
                tests["spearman"] += sum(1 for t in corr.values() if t["rho"] is not None)
                pairs = [(x[i], targets["pressure"][i]) for i in idx if x[i] is not None]
                with_ci = lead in (1, 5) and name in ("ordinary", "band:ample", "band:scarce")
                if with_ci:
                    roc = auroc_with_interval(pairs, f"{column}|{name}", lead)
                else:
                    pos = [v for v, y in pairs if y > 0]
                    neg = [v for v, y in pairs if y <= 0]
                    ok = len(pos) >= screen.MINIMUM_PRESSURE and neg and len(pairs) >= screen.MINIMUM_DAYS
                    roc = {"n": len(pairs), "pressure_days": len(pos), "auroc": auroc(pos, neg) if ok else None, "interval": None}
                if roc["auroc"] is not None:
                    tests["auroc"] += 1
                cell[name] = {"spearman": corr, "auroc": roc}
            per_lead[str(lead)] = cell
        x1 = series[1][column]
        pre = {}
        for name, keep in {
            "ordinary": lambda i: True,
            "band:ample": lambda i: band(1, i) == "ample",
            "band:scarce": lambda i: band(1, i) == "scarce",
        }.items():
            p = [x1[i] for i in pre_index if keep(i) and x1[i] is not None]
            o = [x1[i] for i in other_index if keep(i) and x1[i] is not None]
            c = contrast_with_interval(p, o, f"{column}|{name}") if name == "ordinary" else screen.pre_onset_contrast(p, o)
            if c is not None:
                tests["pre_onset"] += 1
            pre[name] = c
        out_series[column] = {"kind": kinds[column], "new": column in new_columns, "leads": per_lead, "pre_onset": pre}

    # Rank correlation with the target after the scarcity state and the tail spread are taken out.
    tail = series[1].get(TAIL)
    st = state[1]
    for column in readable:
        x = series[1][column]
        if column in (TAIL, screen.SCARCITY) or tail is None:
            continue
        idx = [i for i in ordinary if x[i] is not None and tail[i] is not None and st[i] is not None]
        if len(idx) < screen.MINIMUM_DAYS:
            continue
        entry = {"n": len(idx)}
        for target in ("pressure", "level"):
            y = [targets[target][i] for i in idx]
            raw = screen.spearman([x[i] for i in idx], y)
            part = partial_spearman([x[i] for i in idx], y, [[st[i] for i in idx], [tail[i] for i in idx]])
            entry[target] = {"raw": raw, "partial": part}
            tests["partial"] += 1
        out_series[column]["partial"] = entry
        entry["idx"] = idx

    held_by_partial = sorted(
        (c for c in out_series if "partial" in out_series[c] and c not in new_columns),
        key=lambda c: -abs(out_series[c]["partial"]["pressure"]["partial"] or 0.0),
    )[:12]
    for column in [c for c in out_series if "partial" in out_series[c] and c in new_columns] + held_by_partial:
        entry = out_series[column]["partial"]
        idx = entry["idx"]
        x = [series[1][column][i] for i in idx]
        y = [targets["pressure"][i] for i in idx]
        controls = [[st[i] for i in idx], [tail[i] for i in idx]]
        rng = seeded("partial", column)
        draws = []
        for _ in range(BOOTSTRAPS):
            pick = [rng.randrange(len(idx)) for _ in range(len(idx))]
            value = partial_spearman([x[k] for k in pick], [y[k] for k in pick], [[c[k] for k in pick] for c in controls])
            if value is not None:
                draws.append(value)
        entry["pressure"]["interval"] = interval(draws)
    for column in out_series:
        if "partial" in out_series[column]:
            out_series[column]["partial"].pop("idx", None)

    # Inter-source matrix at lead 1: pooled and by band, on all scored days.
    names = [c for c in readable if c != screen.SCARCITY] + [screen.SPREAD_LAG]
    observed = {n: sum(1 for v in series[1][n] if v is not None) for n in names}
    matrices = {}
    for label, idx in {
        "pooled": list(range(len(scored))),
        "ample": [i for i in range(len(scored)) if band(1, i) == "ample"],
        "scarce": [i for i in range(len(scored)) if band(1, i) == "scarce"],
    }.items():
        rho: Dict[Tuple[str, str], Optional[float]] = {}
        for a in range(len(names)):
            xa = series[1][names[a]]
            for b in range(a + 1, len(names)):
                xb = series[1][names[b]]
                both = [i for i in idx if xa[i] is not None and xb[i] is not None]
                r = screen.spearman([xa[i] for i in both], [xb[i] for i in both]) if len(both) >= screen.MINIMUM_DAYS else None
                rho[(names[a], names[b])] = r
                if r is not None:
                    tests["inter_source"] += 1
        matrices[label] = rho
    groups = clusters(names, matrices["pooled"], observed)
    duplicates = {}
    for n in sorted(new_columns & set(names)):
        best = None
        for (a, b), r in matrices["pooled"].items():
            other = b if a == n else a if b == n else None
            if other is not None and r is not None and other not in new_columns and (best is None or abs(r) > abs(best[1])):
                best = (other, r)
        duplicates[n] = {"closest_old_series": best[0] if best else None, "rho": best[1] if best else None}

    args.output.mkdir(parents=True, exist_ok=True)
    for label, rho in matrices.items():
        with (args.output / f"inter_source_{label}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([""] + names)
            for a in names:
                writer.writerow([a] + ["" if (r := rho.get((a, b) if (a, b) in rho else (b, a))) is None or a == b else f"{r:.4f}" for b in names])
    result = {
        "scope": {
            "first_day": scored[0].isoformat(),
            "last_day": scored[-1].isoformat(),
            "scored_days": len(scored),
            "ordinary_days": len(ordinary),
            "ordinary_pressure_days": int(sum(targets["pressure"][i] for i in ordinary)),
            "ordinary_onsets": [d.isoformat() for d in onsets],
            "pre_onset_days": len(pre_index),
            "other_days": len(other_index),
            "leads": list(screen.LEADS),
            "bootstraps": BOOTSTRAPS,
            "interval": "90 % percentile bootstrap, days resampled independently",
            "cluster_threshold": CLUSTER_THRESHOLD,
            "series_screened": len(out_series),
            "new_series": sorted(new_columns & set(out_series)),
            "tests_run": tests,
            "tests_total": sum(tests.values()),
            "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(),
        },
        "series": out_series,
        "clusters": groups,
        "new_vs_old": duplicates,
        "unreadable": unreadable,
        "not_public_at_lead": {c: {str(l): n for l, n in v.items()} for c, v in sorted(not_public.items())},
    }
    (args.output / "screen.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result["scope"].items() if k not in ("new_series",)}, indent=1))
    print(f"unreadable: {len(unreadable)}; clusters: {len(groups)}")
    return 0


def _f(v, d=3, sign=True):
    if v is None:
        return "-"
    return f"{v:+.{d}f}" if sign else f"{v:.{d}f}"


def _ci(entry):
    iv = entry.get("interval") if entry else None
    return "-" if not iv else f"[{iv[0]:.2f}, {iv[1]:.2f}]"


def lead_cell(series, lead, split="ordinary"):
    return series["leads"][str(lead)][split]


def excludes_half(entry):
    iv = entry.get("interval") if entry else None
    return bool(iv) and (iv[0] > 0.5 or iv[1] < 0.5)


def report_command(args) -> int:
    result = json.loads((args.output / "screen.json").read_text())
    series = result["series"]
    new = set(result["scope"]["new_series"])
    scope = result["scope"]
    rep_of = {m: g["representative"] for g in result["clusters"] for m in g["members"]}
    size_of = {m: len(g["members"]) for g in result["clusters"] for m in g["members"]}

    def best(name):
        """The lead (1 or 5) with the larger distance of the ordinary-day AUROC from 0.5."""
        cands = [(abs((lead_cell(series[name], l)["auroc"]["auroc"] or 0.5) - 0.5), l) for l in (1, 5)]
        return max(cands)

    lines: List[str] = []
    lines.append(f"Ordinary days: {scope['ordinary_days']} of {scope['scored_days']} scored days, {scope['ordinary_pressure_days']} above +5 bp, "
                 f"{len(scope['ordinary_onsets'])} onsets ({', '.join(scope['ordinary_onsets'])}), {scope['pre_onset_days']} pre-onset days against {scope['other_days']} other ordinary days.")
    lines.append("")
    lines.append("Table 1. The new series on ordinary days. AUROC of the +5 bp indicator against the other ordinary days (0.5 is no information), 90 % interval, "
                 "lead 1 and lead 5; Spearman with the indicator and the spread change at lead 1; the pre-onset AUC (1 to 5 days before the six onsets on ordinary days) with interval; "
                 "the partial rank correlation with the indicator after the scarcity state and the tail spread; the closest earlier series and its pooled Spearman; the cluster.")
    lines.append("")
    lines.append("| series | AUROC l1 | 90 % | AUROC l5 | 90 % | rho ind. l1 | rho chg l1 | pre-onset AUC | 90 % | partial rho (raw) | closest held series | cluster (size) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name in sorted(new & set(series)):
        s = series[name]
        a1, a5 = lead_cell(s, 1)["auroc"], lead_cell(s, 5)["auroc"]
        sp = lead_cell(s, 1)["spearman"]
        pre = s["pre_onset"]["ordinary"]
        part = s.get("partial", {}).get("pressure", {})
        near = result["new_vs_old"].get(name, {})
        lines.append(
            f"| `{name}` | {_f(a1['auroc'], 3, False)} | {_ci(a1)} | {_f(a5['auroc'], 3, False)} | {_ci(a5)} | {_f(sp['pressure']['rho'])} | {_f(sp['change']['rho'])} | "
            f"{_f(pre['auc'], 3, False) if pre else '-'} | {('[%.2f, %.2f]' % tuple(pre['auc_interval'])) if pre and pre.get('auc_interval') else '-'} | "
            f"{_f(part.get('partial'))} {('[%.2f, %.2f]' % tuple(part['interval'])) if part.get('interval') else ''} ({_f(part.get('raw'))}) | `{near.get('closest_old_series')}` {_f(near.get('rho'), 2)} | `{rep_of.get(name)}` ({size_of.get(name)}) |"
        )
    lines.append("")

    def lead_rows(names, title):
        lines.append(title)
        lines.append("")
        lines.append("| rank | series | new | lead | AUROC | 90 % | rho ind. | pre-onset AUC | 90 % | partial rho | cluster representative (size) |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for rank, name in enumerate(names, 1):
            dist, lead = best(name)
            s = series[name]
            a = lead_cell(s, lead)["auroc"]
            sp = lead_cell(s, lead)["spearman"]["pressure"]["rho"]
            pre = s["pre_onset"]["ordinary"]
            part = s.get("partial", {}).get("pressure", {}).get("partial")
            lines.append(
                f"| {rank} | `{name}` | {'yes' if name in new else 'no'} | {lead} | {_f(a['auroc'], 3, False)} | {_ci(a)} | {_f(sp)} | "
                f"{_f(pre['auc'], 3, False) if pre else '-'} | {('[%.2f, %.2f]' % tuple(pre['auc_interval'])) if pre and pre.get('auc_interval') else '-'} | {_f(part)} | `{rep_of.get(name)}` ({size_of.get(name)}) |"
            )
        lines.append("")

    ranked = sorted((n for n in series if n != "spread_bps" and lead_cell(series[n], 1)["auroc"]["auroc"] is not None), key=lambda n: -best(n)[0])
    flagged = [n for n in ranked if excludes_half(lead_cell(series[n], 1)["auroc"]) or excludes_half(lead_cell(series[n], 5)["auroc"])]
    scope_tests = scope["tests_run"]
    lead_rows(ranked[:25], "Table 2. The 25 series with the largest distance of the ordinary-day AUROC from 0.5 (the larger of lead 1 and lead 5), new and held together. "
                           "A series is a lead only if its interval excludes 0.5; the rank is by distance and is not a significance ranking.")
    withpartial = sorted((n for n in series if series[n].get("partial", {}).get("pressure", {}).get("partial") is not None and n != "spread_bps"),
                         key=lambda n: -abs(series[n]["partial"]["pressure"]["partial"]))
    lines.append("Table 4. The series ranked by the rank correlation with the +5 bp indicator on ordinary days after the scarcity state and the tail spread are taken out (lead 1; "
                 "interval only for the new series and the 12 held series with the largest value). This is the incremental check: a series that ranks high in Table 2 and low here "
                 "tells the same story as the scarcity state or the tail spread.")
    lines.append("")
    lines.append("| rank | series | new | partial rho | 90 % | raw rho | AUROC l1 | 90 % | pre-onset AUC | 90 % |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for rank, name in enumerate(withpartial[:25], 1):
        s_ = series[name]
        part = s_["partial"]["pressure"]
        a = lead_cell(s_, 1)["auroc"]
        pre = s_["pre_onset"]["ordinary"]
        lines.append(f"| {rank} | `{name}` | {'yes' if name in new else 'no'} | {_f(part['partial'])} | {('[%.2f, %.2f]' % tuple(part['interval'])) if part.get('interval') else '-'} | {_f(part['raw'])} | "
                     f"{_f(a['auroc'], 3, False)} | {_ci(a)} | {_f(pre['auc'], 3, False) if pre else '-'} | {('[%.2f, %.2f]' % tuple(pre['auc_interval'])) if pre and pre.get('auc_interval') else '-'} |")
    lines.append("")
    lines.append(f"Series whose ordinary-day AUROC interval excludes 0.5 at lead 1 or 5: {len(flagged)} of {len(ranked)}; of the new series: "
                 f"{', '.join('`%s`' % n for n in flagged if n in new) or 'none'}.")
    lines.append("")
    lines.append("Table 3. Redundant groups (pooled lead-1 Spearman, |rho| >= %.1f, each member within the threshold of the representative) that hold a new series." % scope["cluster_threshold"])
    lines.append("")
    lines.append("| representative | members |")
    lines.append("|---|---|")
    for g in result["clusters"]:
        if any(m in new for m in g["members"]):
            lines.append(f"| `{g['representative']}` | {', '.join('`%s`' % m for m in g['members'])} |")
    lines.append("")
    lines.append("Tests run (none corrected for multiplicity): " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in scope_tests.items()) + f"; {scope['tests_total']} in all.")
    (args.output / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Heatmap: Spearman with the indicator on ordinary days, series by lead, the new series and the 12 held ones with the largest distance.
    held = [n for n in ranked if n not in new][:12]
    names = sorted(new & set(series)) + held
    cell, left, top = 46, 210, 40
    width, height = left + cell * 5 + 20, top + cell * len(names) // 2 + 30
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Spearman with the +5 bp indicator on ordinary days, series by lead">',
             '<style>text{font:11px sans-serif;fill:#222}@media (prefers-color-scheme: dark){text{fill:#ddd}}</style>']
    for j, lead in enumerate(screen.LEADS):
        parts.append(f'<text x="{left + j * cell + cell // 2}" y="{top - 8}" text-anchor="middle">lead {lead}</text>')
    row_h = cell // 2
    for i, name in enumerate(names):
        y = top + i * row_h
        parts.append(f'<text x="{left - 6}" y="{y + row_h - 6}" text-anchor="end">{name}{" (new)" if name in new else ""}</text>')
        for j, lead in enumerate(screen.LEADS):
            rho = lead_cell(series[name], lead)["spearman"]["pressure"]["rho"]
            if rho is None:
                fill, label = "#bbb", "-"
            else:
                t = max(-0.4, min(0.4, rho)) / 0.4
                fill = f"rgb({int(255 - 120 * max(t, 0))},{int(255 - 120 * abs(t))},{int(255 - 120 * max(-t, 0))})"
                label = f"{rho:+.2f}"
            parts.append(f'<rect x="{left + j * cell}" y="{y}" width="{cell - 2}" height="{row_h - 2}" fill="{fill}"/>'
                         f'<text x="{left + j * cell + cell // 2 - 1}" y="{y + row_h - 8}" text-anchor="middle" style="fill:#111">{label}</text>')
    parts.append("</svg>")
    (args.output / "heatmap.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"tables.md {len(lines)} lines; heatmap rows {len(names)}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    extract = sub.add_parser("extract-pd")
    extract.add_argument("export")
    extract.add_argument("--check", action="store_true")
    extract.set_defaults(func=extract_pd_command)
    fetch = sub.add_parser("fetch-dts")
    fetch.add_argument("--start", default=FIRST_DTS_YEAR_START)
    fetch.add_argument("--end", default=new_sources.END.isoformat())
    fetch.set_defaults(func=fetch_dts_command)
    wh = sub.add_parser("withheld")
    wh.add_argument("--panel", type=Path, required=True)
    wh.add_argument("--output", type=Path, required=True)
    wh.set_defaults(func=withheld_command)
    pan = sub.add_parser("panel")
    pan.add_argument("--panel", type=Path, required=True)
    pan.add_argument("--output", type=Path, required=True)
    pan.set_defaults(func=panel_command)
    scr = sub.add_parser("screen")
    scr.add_argument("--panel", type=Path, required=True)
    scr.add_argument("--output", type=Path, required=True)
    scr.set_defaults(func=screen_command)
    rep = sub.add_parser("report")
    rep.add_argument("--output", type=Path, required=True)
    rep.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
