"""Longer history (#129): does pre-SOFR EFFR - IOER history help SOFR - IORB pressure forecasts?

A separate study, not a record: it writes JSON and Markdown to the paths it is
given, nothing into `docs/runs/`, and no published declaration reads anything
it adds.

**A different market and a different target.** EFFR - IOER (unsecured
overnight lending between banks and GSEs, 2008-12-16 to 2018-04-02) is not
SOFR - IORB (secured Treasury repo). The history is pooled behind a market
indicator, never read as if it were the same event.

    PYTHONPATH=src python3 scripts/longer_history.py fetch --release H15
    PYTHONPATH=src python3 scripts/longer_history.py fetch --release PRATES
    PYTHONPATH=src python3 scripts/longer_history.py episodes --output OUT/episodes.json --markdown OUT/episodes.md
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/longer_history.py horizon --panel PANEL --horizon H --output OUT/hH.json
    PYTHONPATH=src python3 scripts/longer_history.py assemble --output OUT/longer_history.json \\
        --markdown OUT/longer_history.md OUT/h1.json OUT/h2.json OUT/h3.json OUT/h4.json OUT/h5.json

The control is pressure model v1's direct logistic as merged (#114,
`scripts/pressure_model_v1.py`), on the same fold grid: walk-forward,
expanding, refit every 21 scored days, `minimum_history` 61, 16:00, +5 and
+10 bp, horizons 1 to 5, no scored day on or after 2026-01-01. Paired against
it, with stationary-bootstrap intervals split by regime and pressure-day type:

* `pooled_logistic`: the v1 design without `treasury_settlement` (Treasury's
  auction records in the panel's snapshot begin in 2017), plus a market
  indicator, fitted on every SOFR pair and every history pair
  (`ml._direct_pressure_predictor(..., history=...)`).
* `v1_no_settlement` (horizon 1 only): the same design without the history, so
  the pooled candidate's difference from v1 at horizon 1 can be split into the
  dropped settlement and the added history. At horizons 2 to 5 v1 already
  drops the settlement, so v1 is that ablation.
* Each also recalibrated out of fold (`pressure.recalibrated`), paired against
  v1 recalibrated.

Pre-training (fitting on the history first) needs both label values in the
history; `episodes` counts them. With none above a threshold, a model
pre-trained at that threshold is the constant 0 and is reported as not
estimable rather than scored.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

import pressure_model_v1 as v1  # noqa: E402
from repo_model import effr_history, ingest, pressure  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DDP_DIRECTORY = REPO / "tests" / "fixtures" / "snapshots" / ingest.FRB_DDP_SOURCE_ID
FRED_DIRECTORY = REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "fred-macro-latest-vintage"
POOLED_FEATURES = tuple(name for name in v1.DIRECT_FEATURES if name != v1.SETTLEMENT)
CONTROL = "v1_direct_logistic"


def fetch_command(args) -> int:
    (artifact,) = ingest.fetch_frb_ddp(args.output_root, args.release)
    print(json.dumps({"path": str(artifact.path), "sha256": artifact.sha256, "bytes": artifact.byte_count}))
    return 0


def _history():
    return effr_history.load_history_rows(DDP_DIRECTORY, FRED_DIRECTORY)


def _snapshots():
    out = []
    for manifest in sorted(DDP_DIRECTORY.glob("*.manifest.json")):
        artifact = ingest.load_snapshot_manifest(manifest)
        out.append({"url": artifact.url, "sha256": artifact.sha256, "retrieved_at": artifact.retrieved_at})
    return out


def episodes_command(args) -> int:
    rows = _history()
    by_year = defaultdict(list)
    for row in rows:
        by_year[row.date.year].append(row)
    years = []
    for year, items in sorted(by_year.items()):
        spreads = [row.spread_bps for row in items]
        reserves = [row.values["reserve_balances"] for row in items if row.values["reserve_balances"] is not None]
        years.append({
            "year": year,
            "days": len(items),
            "mean_bps": round(statistics.fmean(spreads), 2),
            "min_bps": round(min(spreads), 2),
            "max_bps": round(max(spreads), 2),
            "days_above_0": sum(value > 0 for value in spreads),
            "reserves_min_bn": round(min(reserves), 1) if reserves else None,
            "reserves_max_bn": round(max(reserves), 1) if reserves else None,
        })
    thresholds = {}
    for tau in (0.0,) + v1.TAUS:
        found = effr_history.episodes(rows, tau)
        thresholds[f"{tau:g}"] = {"days_above": sum(e["days"] for e in found), "episodes": found}
    peak = max(rows, key=lambda row: row.spread_bps)
    document = {
        "directive": "#129",
        "status": "scratch study; nothing published moves",
        "window": {"first": rows[0].date.isoformat(), "last": rows[-1].date.isoformat(), "days": len(rows)},
        "snapshots": _snapshots(),
        "by_year": years,
        "by_threshold": thresholds,
        "peak": {"date": peak.date.isoformat(), "bps": round(peak.spread_bps, 2)},
        "pretraining_estimable": {
            f"{tau:g}": bool(thresholds[f"{tau:g}"]["days_above"]) for tau in v1.TAUS
        },
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    out = [
        f"History window {document['window']['first']} to {document['window']['last']}, "
        f"{document['window']['days']} H.15 business days. Highest EFFR − IOER: "
        f"{document['peak']['bps']:+.2f} bp on {document['peak']['date']}.\n",
        "| Threshold | Days above | Episodes |", "|---|---|---|",
    ]
    for key, entry in thresholds.items():
        out.append(f"| > {float(key):+g} bp | {entry['days_above']} | {len(entry['episodes'])} |")
    out += ["", "| Year | Days | Mean bp | Min bp | Max bp | Days > 0 | Reserves min (USD bn) | Reserves max (USD bn) |",
            "|---|---|---|---|---|---|---|---|"]
    for item in years:
        out.append(
            f"| {item['year']} | {item['days']} | {item['mean_bps']:+.2f} | {item['min_bps']:+.2f} | "
            f"{item['max_bps']:+.2f} | {item['days_above_0']} | {item['reserves_min_bn']} | {item['reserves_max_bn']} |"
        )
    args.markdown.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), **document["window"], "peak": document["peak"]}))
    return 0


def horizon_command(args) -> int:
    from repo_model import ml

    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(v1.SPLITS)
    h = args.horizon
    registry = json.loads(v1.REGISTRY.read_text())
    history = _history()
    rule = effr_history.HistoryRule(registry, decision_time=v1.DECISION, horizon=h)
    direct = v1._at_horizon(v1.DIRECT_FEATURES, h)

    control = v1._run(
        rows, CONTROL,
        ml.pressure_logistic_exceedance(direct, splits, minimum_history=v1.MINIMUM_HISTORY),
        direct, h,
    )
    runs = {
        "pooled_logistic": v1._run(
            rows, "pooled_logistic",
            ml._direct_pressure_predictor(
                "logistic", POOLED_FEATURES, splits, v1.MINIMUM_HISTORY, history=(history, rule)
            ),
            POOLED_FEATURES, h,
        )
    }
    if h == 1:
        runs["v1_no_settlement"] = v1._run(
            rows, "v1_no_settlement",
            ml.pressure_logistic_exceedance(POOLED_FEATURES, splits, minimum_history=v1.MINIMUM_HISTORY),
            POOLED_FEATURES, h,
        )
    benchmarks = {
        CONTROL: control,
        f"{CONTROL}+recalibrated": pressure.recalibrated(control),
        "calendar_climatology": v1._run(
            rows, "calendar_climatology",
            v1.calendar_climatology_exceedance(splits, minimum_history=v1.MINIMUM_HISTORY),
            v1.CALENDAR_FEATURES, h,
        ),
        "persistence_logistic": v1._run(
            rows, "persistence_logistic",
            v1.persistence_logistic_exceedance(minimum_history=v1.MINIMUM_HISTORY),
            ("spread_bps",), h,
        ),
    }
    candidates = {}
    for name, report in runs.items():
        candidates[name] = report
        candidates[f"{name}+recalibrated"] = pressure.recalibrated(report)
    digest = panel_sha256(args.panel)
    card = pressure.scorecard(candidates, benchmarks, rows=rows, declaration=splits, panel_sha256=digest)
    pool_positives = {
        f"{tau:g}": sum(
            spread > tau
            for spread in effr_history.history_pairs(
                ml._PressureDesign(POOLED_FEATURES, splits), rule, history
            ).spreads
        )
        for tau in v1.TAUS
    }
    document = {
        "horizon": h,
        "panel_sha256": digest,
        "scored_window": {
            "first": control.scored_dates[0].isoformat(),
            "last": control.scored_dates[-1].isoformat(),
            "days": len(control.scored_dates),
        },
        "fold_grid": {
            "walk_forward": "expanding window", "refit_every": v1.REFIT_EVERY,
            "minimum_history": v1.MINIMUM_HISTORY,
            "decision_time": v1.DECISION.isoformat(timespec="minutes"), "end": v1.END.isoformat(),
        },
        "history": {
            "first": history[0].date.isoformat(), "last": history[-1].date.isoformat(),
            "rows": len(history), "snapshots": _snapshots(),
            "pool_label_positives": pool_positives,
        },
        "declarations": {
            name: {"features": list(report.features), "model_settings": dict(report.model_settings)}
            for name, report in {CONTROL: control, **runs}.items()
        },
        "scorecard": card,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output), **document["scored_window"],
                      "pool": runs["pooled_logistic"].model_settings["pooled_history"]}))
    return 0


# -- assembly -----------------------------------------------------------------

#: Each candidate is paired against the control in the same recalibration state.
def _control_for(name: str) -> str:
    return f"{CONTROL}+recalibrated" if name.endswith("+recalibrated") else CONTROL


def assemble_command(args) -> int:
    parts = sorted((json.loads(Path(p).read_text()) for p in args.inputs), key=lambda d: d["horizon"])
    document = {
        "directive": "#129",
        "status": "scratch study; not a record, nothing published moves",
        "horizons": {str(part["horizon"]): part for part in parts},
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(parts), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "markdown": str(args.markdown)}))
    return 0


def _markdown(parts) -> str:
    fmt, interval, split_cell = v1._fmt, v1._interval, v1._split_cell
    out = [f"Panel `{parts[0]['panel_sha256'][:12]}…`. History "
           f"{parts[0]['history']['first']} to {parts[0]['history']['last']} "
           f"({parts[0]['history']['rows']} rows). No scored day on or after 2026-01-01.\n",
           "| Horizon | First scored | Last scored | Days | History pairs | History pairs > +5 bp | > +10 bp |",
           "|---|---|---|---|---|---|---|"]
    for part in parts:
        sw = part["scored_window"]
        pooled = part["declarations"]["pooled_logistic"]["model_settings"]["pooled_history"]
        positives = part["history"]["pool_label_positives"]
        out.append(f"| {part['horizon']} | {sw['first']} | {sw['last']} | {sw['days']} | {pooled['pairs']} | "
                   f"{positives['5']} | {positives['10']} |")
    out.append("")
    for tau in v1.TAUS:
        key = f"{tau:g}"
        out.append(f"### +{key} bp\n")
        out.append("Paired difference = Brier(benchmark) − Brier(candidate), mean over scored days, 90% "
                   "stationary-bootstrap interval; positive means the candidate had the lower Brier. "
                   "\"vs v1\" pairs each candidate with v1's direct logistic in the same recalibration state.\n")
        out.append("| Horizon | Model | Brier | Reliability | Resolution | AP | vs v1 | vs persistence-logistic | vs calendar climatology |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for part in parts:
            card = part["scorecard"]
            for name in (CONTROL, f"{CONTROL}+recalibrated"):
                m = card["benchmarks"][name][key]
                d = m.get("decomposition", {})
                out.append(f"| {part['horizon']} | {name} (control) | {fmt(m['brier'])} | {fmt(d.get('reliability'))} | "
                           f"{fmt(d.get('resolution'))} | {fmt(m.get('average_precision'), 3)} | | | |")
            for name, entry in card["candidates"].items():
                m = entry["metrics"][key]
                d = m.get("decomposition", {})
                cells = [interval(entry["paired"][b]["by_tau"][key]["paired_brier_difference"])
                         for b in (_control_for(name), "persistence_logistic", "calendar_climatology")]
                out.append(f"| {part['horizon']} | {name} | {fmt(m['brier'])} | {fmt(d.get('reliability'))} | "
                           f"{fmt(d.get('resolution'))} | {fmt(m.get('average_precision'), 3)} | " + " | ".join(cells) + " |")
        out.append("")
        out.append(f"#### +{key} bp: paired difference against v1, split by regime and pressure-day type\n")
        for part in parts:
            card = part["scorecard"]
            names = list(card["candidates"])
            first = card["candidates"][names[0]]["paired"][CONTROL]["by_tau"][key]["paired_brier_difference"]["splits"]
            regimes, types = list(first["by_regime"]), list(first["by_day_type"])
            out.append(f"**Horizon {part['horizon']}**\n")
            out.append("| Model | " + " | ".join(regimes + types) + " |")
            out.append("|---|" + "---|" * (len(regimes) + len(types)))
            for name in names:
                s = card["candidates"][name]["paired"][_control_for(name)]["by_tau"][key]["paired_brier_difference"]["splits"]
                cells = [split_cell(s["by_regime"][r]) for r in regimes] + [split_cell(s["by_day_type"][t]) for t in types]
                out.append(f"| {name} | " + " | ".join(cells) + " |")
            out.append("")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch", help="fetch one DDP release package into a checksummed snapshot")
    fetch.add_argument("--release", choices=ingest.FRB_DDP_RELEASES, required=True)
    fetch.add_argument("--output-root", type=Path, default=REPO / "tests" / "fixtures" / "snapshots")
    fetch.set_defaults(func=fetch_command)
    desc = sub.add_parser("episodes", help="describe the history and list its episodes")
    desc.add_argument("--output", type=Path, required=True)
    desc.add_argument("--markdown", type=Path, required=True)
    desc.set_defaults(func=episodes_command)
    one = sub.add_parser("horizon", help="score the control and the pooled candidate at one horizon")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--horizon", type=int, choices=v1.HORIZONS, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=horizon_command)
    merge = sub.add_parser("assemble", help="merge the horizons into tables")
    merge.add_argument("--output", type=Path, required=True)
    merge.add_argument("--markdown", type=Path, required=True)
    merge.add_argument("inputs", nargs="+")
    merge.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
