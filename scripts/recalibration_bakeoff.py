"""Recalibration bake-off (#138): isotonic against Platt, beta and recency-weighted Platt.

The control is the CORP isotonic fit, not the published recalibration: pressure
model v1 is published with Platt scaling (`pc.PUBLISHED`), so read the "vs Platt"
columns for a comparison with what is published (#211).

A scratch measurement, not a record: it writes JSON and a Markdown summary to
the paths it is given, and nothing into `docs/runs/`. Nothing published moves.

Two raw forecasts, each at horizons 1 to 5, every comparison ending on
2025-12-31 (`docs/decisions/lockbox.md`):

* `gbm`: the published `exceedance_gbm` declaration (gbm, uncalibrated, its
  four features), read at +5 and +10 bp;
* `pressure_v1`: pressure model v1's published candidate before its
  recalibration (#114, #124): `distributional_gbm`, the funding declaration's
  gbm calibrated by conformal PID with nested selection, as
  `scripts/pressure_model_v1.py publish` runs it.

Both runs also carry the leap and pressure-leap probabilities at
`onset.LEAP_JUMP_BP[h]` (#139). Every calibrator in
`repo_model.probability_calibration` is then applied, walk-forward, to the
same raw forecasts, and scored by `score`:

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/recalibration_bakeoff.py raw \\
        --panel PANEL --forecast {gbm,pressure_v1} --horizon H --output OUT/RAW_hH.pickle
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/recalibration_bakeoff.py score \\
        --panel PANEL --output OUT/RAW_hH.json OUT/RAW_hH.pickle
    PYTHONPATH=src python3 scripts/recalibration_bakeoff.py assemble \\
        --output OUT/bakeoff.json --markdown OUT/bakeoff.md OUT/*_h?.json
"""

from __future__ import annotations

import argparse
import copyreg
import json
import pickle
import sys
from datetime import date, time
from pathlib import Path
from types import MappingProxyType

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset, probability_calibration as pc  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    calendar_climatology_exceedance,
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import audit_panel, load_daily_panel, load_stress_thresholds  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
THRESHOLDS = REPO / "metadata" / "stress_thresholds.json"
HORIZONS = (1, 2, 3, 4, 5)
MINIMUM_HISTORY = 61
REFIT_EVERY = 21
DECISION = time(16, 0)
#: The last day any comparison may score (`docs/decisions/lockbox.md`).
END = date(2025, 12, 31)
#: The thresholds scored: the headline stress targets (#139's amended order).
SCORED_TAUS = (5.0, 10.0)

#: The published `exceedance_gbm` declaration's features.
GBM_FEATURES = ("sofr_p25", "sofr_p75", "sofr_volume", "spread_bps")
#: Pressure model v1's (the published funding declaration's) features.
V1_FEATURES = (
    "reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps",
    "tbill_13w", "tbill_4w", "tga", "treasury_settlement",
)
CALENDAR_FEATURES = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")
#: Scheduled one business day ahead, so not public at a longer horizon.
SETTLEMENT = "treasury_settlement"

#: The two episodes whose reliability is reported separately (#138, step 4).
EPISODES = {
    "2018-19": (date(2018, 1, 1), date(2019, 12, 31)),
    "2025": (date(2025, 1, 1), date(2025, 12, 31)),
}


def _proxy(mapping):
    return MappingProxyType(mapping)


copyreg.pickle(MappingProxyType, lambda proxy: (_proxy, (dict(proxy),)))


def _at_horizon(features, horizon):
    return tuple(name for name in features if horizon == 1 or name != SETTLEMENT)


def raw_command(args) -> int:
    from repo_model import ml
    from repo_model.recalibration import NestedFoldPid

    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    taus = tuple(float(tau) for tau in load_stress_thresholds(THRESHOLDS)["taus_bp"])
    h = args.horizon
    registry = json.loads(REGISTRY.read_text())
    built = []

    def online(rows_, rule):
        built.append(NestedFoldPid(rows_, rule, splits=splits, refit_every=REFIT_EVERY))
        return built[-1]

    def run(name, predictor, declared, calibration=None, leap=True):
        return rolling_exceedance_backtest(
            rows,
            predictor=predictor,
            model_name=name,
            features=declared,
            registry=registry,
            decision_time=DECISION,
            taus=taus,
            minimum_history=MINIMUM_HISTORY,
            refit_every=REFIT_EVERY,
            end=END,
            horizon=h,
            leap_jump_bp=onset.LEAP_JUMP_BP[h] if leap else None,
            online_calibration=calibration,
        )

    if args.forecast == "gbm":
        features = GBM_FEATURES
        report = run(
            "gbm",
            ml.gbm_exceedance(
                tuple(name for name in features if name != "spread_bps"),
                minimum_history=MINIMUM_HISTORY,
            ),
            features,
        )
    else:
        features = _at_horizon(V1_FEATURES, h)
        report = run(
            "distributional_gbm",
            ml.gbm_exceedance(
                tuple(name for name in features if name != "spread_bps"),
                minimum_history=MINIMUM_HISTORY,
            ),
            features,
            online,
        )
    benchmarks = {
        "calendar_climatology": run(
            "calendar_climatology",
            calendar_climatology_exceedance(splits, minimum_history=MINIMUM_HISTORY),
            CALENDAR_FEATURES,
            leap=False,
        ),
        "persistence_logistic": run(
            "persistence_logistic",
            persistence_logistic_exceedance(minimum_history=MINIMUM_HISTORY),
            ("spread_bps",),
            leap=False,
        ),
    }
    args.output.write_bytes(
        pickle.dumps({"forecast": args.forecast, "horizon": h, "report": report,
                      "benchmarks": benchmarks})
    )
    print(json.dumps({"forecast": args.forecast, "horizon": h, "output": str(args.output),
                      "scored_days": len(report.scored_dates)}))
    return 0


def bakeoff(part, *, rows, splits, registry, digest) -> dict:
    """Every calibrator applied to one raw run, and each target scored."""

    from repo_model import pressure
    from repo_model.baseline import _maximum_horizon_overlap

    report = part["report"]
    h = part["horizon"]
    scored = list(report.scored_dates)
    train_ends = [fold.train_end for fold in report.folds]
    block = _maximum_horizon_overlap(report.folds)
    if any(when >= date(2026, 1, 1) for when in scored):
        raise ValueError("a scored day is locked (docs/decisions/lockbox.md)")

    def seeder(target):
        return lambda *names: onset._seed(digest, part["forecast"], h, target, *names)

    positions = [report.taus.index(tau) for tau in SCORED_TAUS]
    raw_cols, outcomes = {}, {}
    for tau, position in zip(SCORED_TAUS, positions):
        forecast, _, realized = report.at_tau(position)
        raw_cols[tau], outcomes[tau] = list(forecast), list(realized)
    calibrated = {}
    for method in pc.CALIBRATORS:
        columns = [
            pc.walk_forward(method, raw_cols[tau], outcomes[tau], scored, train_ends)
            for tau in SCORED_TAUS
        ]
        curves = pc.monotone_curves(list(zip(*columns)))
        calibrated[method] = {tau: [curve[k] for curve in curves] for k, tau in enumerate(SCORED_TAUS)}

    out = {
        "forecast": part["forecast"],
        "model": report.model_name,
        "features": list(report.features),
        "horizon": h,
        "scored_window": {"first": scored[0].isoformat(), "last": scored[-1].isoformat(),
                          "days": len(scored)},
        "block_length": block,
        "targets": {},
    }
    published = pressure.recalibrated(report)
    out["platt_vs_pressure_recalibrated_max_abs_difference"] = max(
        abs(calibrated["platt"][tau][k] - published.forecast[k][position])
        for tau, position in zip(SCORED_TAUS, positions)
        for k in range(len(scored))
    )
    for tau, position in zip(SCORED_TAUS, positions):
        bench = {name: list(b.at_tau(position)[0]) for name, b in part["benchmarks"].items()}
        for b in part["benchmarks"].values():
            if list(b.at_tau(position)[2]) != outcomes[tau] or list(b.scored_dates) != scored:
                raise ValueError("a benchmark is not on the candidate's grid")
        venn = pc.venn_abers(raw_cols[tau], outcomes[tau], scored, train_ends)
        out["targets"][f"+{tau:g}bp"] = pc.score_target(
            raw_cols[tau],
            {m: calibrated[m][tau] for m in pc.CALIBRATORS},
            outcomes[tau],
            scored,
            episodes=EPISODES,
            venn=venn,
            block_length=block,
            seed=seeder(tau),
            splits=splits,
            rows=rows,
            benchmarks=bench,
        )
        out["targets"][f"+{tau:g}bp"]["venn_abers_by_day"] = [
            None if pair is None else [round(pair[0], 6), round(pair[1], 6)] for pair in venn
        ]

    rule = InformationRule(registry, ("spread_bps",), decision_time=DECISION, horizon=h)
    targets = onset.LeapTargets(rows, rule, report.leap_threshold_bp)
    position_of = {when: index for index, when in enumerate(targets.dates)}
    indices = [position_of[when] for when in scored]
    groups = onset.day_groups(rows, scored, splits)
    for target, forecast in (("leap", report.leap_forecast),
                             ("pressure_leap", report.pressure_leap_forecast)):
        labels = targets.labels(target)
        realized = [1 if labels[i] else 0 for i in indices]
        raw = list(forecast)
        cols = {m: list(pc.walk_forward(m, raw, realized, scored, train_ends)) for m in pc.CALIBRATORS}
        baselines = {
            onset.LEAP_CALENDAR_CLIMATOLOGY: onset.leap_calendar_climatology(
                targets, target, scored, train_ends, splits),
            onset.LEAP_PERSISTENCE_LOGISTIC: onset.leap_persistence_logistic(
                targets, target, scored, train_ends),
        }
        venn = pc.venn_abers(raw, realized, scored, train_ends)
        entry = pc.score_target(
            raw, cols, realized, scored, episodes=EPISODES, venn=venn, block_length=block,
            seed=seeder(target), splits=splits, rows=rows, benchmarks=baselines,
        )
        target_groups = {
            onset.GROUP_ALL: groups[onset.GROUP_ALL],
            onset.GROUP_SCHEDULED: groups[onset.GROUP_SCHEDULED],
            onset.GROUP_LEAP_ONSET: onset.leap_onset_group(targets, scored),
        }
        entry["leap_threshold_bp"] = report.leap_threshold_bp
        entry["against_leap_baselines"] = {}
        for name, column in {"raw": raw, **cols}.items():
            block_doc = onset._group_block(
                name, {name: column, **baselines}, realized, target_groups,
                block_length=block, seed_parts=(digest, part["forecast"], h, target, name),
            )
            block_doc["verdict"] = onset.leap_verdict(block_doc[onset.GROUP_ALL])
            entry["against_leap_baselines"][name] = block_doc
        out["targets"][target] = entry
    return out


def score_command(args) -> int:
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    registry = json.loads(REGISTRY.read_text())
    part = pickle.loads(Path(args.input).read_bytes())
    document = bakeoff(part, rows=rows, splits=splits, registry=registry, digest=digest)
    document["panel_sha256"] = digest
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"scored": args.input, "output": str(args.output)}))
    return 0


def assemble_command(args) -> int:
    parts = [json.loads(Path(path).read_text()) for path in args.inputs]
    parts.sort(key=lambda part: (part["forecast"] != "gbm", part["horizon"]))
    document = {
        "directive": "#138",
        "status": "scratch measurement; not a record, nothing published moves",
        "panel_sha256": parts[0]["panel_sha256"],
        "declaration": pc.declaration(),
        "episodes": {name: [a.isoformat(), b.isoformat()] for name, (a, b) in EPISODES.items()},
        "results": {f"{part['forecast']}_h{part['horizon']}": part for part in parts},
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "markdown": str(args.markdown)}))
    return 0


def _f(value, places=4):
    return "–" if value is None else f"{value:.{places}f}"


def _ci(paired):
    i = paired["interval"]
    return f"{paired['mean']:+.4f} [{i['lower']:+.4f}, {i['upper']:+.4f}]"


def _cell(entry):
    if "mean" not in entry:
        return "– (n=0)"
    i = entry.get("interval")
    if not i:
        return f"{entry['mean']:+.4f} (n={entry['count']})"
    return f"{entry['mean']:+.4f} [{i['lower']:+.4f}, {i['upper']:+.4f}]"


TARGET_ORDER = ("+5bp", "+10bp", "leap", "pressure_leap")
CANDIDATES = tuple(m for m in pc.CALIBRATORS if m != pc.CONTROL)


def markdown(document) -> str:
    out = []
    results = document["results"]
    forecasts = sorted({p["forecast"] for p in results.values()}, key=lambda f: f != "gbm")
    out.append(f"Panel `{document['panel_sha256'][:12]}…`; no scored day on or after 2026-01-01. "
               f"Paired = Brier(reference) − Brier(candidate), mean over scored days, 90% "
               f"stationary-bootstrap interval; positive means the candidate had the lower Brier.\n")
    for forecast in forecasts:
        parts = [p for p in results.values() if p["forecast"] == forecast]
        parts.sort(key=lambda p: p["horizon"])
        out.append(f"## Raw forecast: `{forecast}` ({parts[0]['model']})\n")
        out.append("| Horizon | First scored | Last scored | Days | Platt = published recalibration (max abs diff) |")
        out.append("|---|---|---|---|---|")
        for p in parts:
            w = p["scored_window"]
            out.append(f"| {p['horizon']} | {w['first']} | {w['last']} | {w['days']} | "
                       f"{p['platt_vs_pressure_recalibrated_max_abs_difference']:.1e} |")
        out.append("")
        for target in TARGET_ORDER:
            out.append(f"### {forecast}, {target}\n")
            out.append("**Paired against the control (isotonic; not the published recalibration, which is Platt: see \"vs Platt\")**, all scored days\n")
            out.append("| Candidate | " + " | ".join(f"h={p['horizon']}" for p in parts) + " |")
            out.append("|---|" + "---|" * len(parts))
            for m in CANDIDATES + ("raw",):
                out.append(f"| {m} | " + " | ".join(
                    _ci(p["targets"][target]["methods"][m]["paired"]["vs_control"]) for p in parts) + " |")
            out.append("")
            out.append("**Brier, reliability (REL) and resolution (RES)** (CORP decomposition)\n")
            out.append("| Method | " + " | ".join(f"h={p['horizon']} Brier / REL / RES" for p in parts) + " |")
            out.append("|---|" + "---|" * len(parts))
            for m in ("raw",) + pc.CALIBRATORS:
                cells = []
                for p in parts:
                    e = p["targets"][target]["methods"][m]
                    cells.append(f"{_f(e['brier'])} / {_f(e.get('reliability'))} / {_f(e.get('resolution'))}")
                out.append(f"| {m} | " + " | ".join(cells) + " |")
            ev = [p["targets"][target]["events"] for p in parts]
            out.append(f"\nEvents per horizon: {', '.join(str(e) for e in ev)}.\n")
            out.append("**Reliability by episode** (REL, lower is better; events in brackets)\n")
            out.append("| Method | " + " | ".join(
                f"h={p['horizon']} {ep}" for p in parts for ep in document["episodes"]) + " |")
            out.append("|---|" + "---|" * (len(parts) * len(document["episodes"])))
            for m in ("raw",) + pc.CALIBRATORS:
                cells = []
                for p in parts:
                    for ep in document["episodes"]:
                        e = p["targets"][target]["methods"][m]["episodes"][ep]
                        cells.append(f"{_f(e.get('reliability'))} ({e['events']})")
                out.append(f"| {m} | " + " | ".join(cells) + " |")
            out.append("")
            benches = [k for k in parts[0]["targets"][target]["methods"]["raw"]["paired"]
                       if k not in ("vs_control", "vs_platt")]
            for bench in benches:
                out.append(f"**Paired against {bench[3:]}**, all scored days\n")
                out.append("| Method | " + " | ".join(f"h={p['horizon']}" for p in parts) + " |")
                out.append("|---|" + "---|" * len(parts))
                for m in ("raw",) + pc.CALIBRATORS:
                    out.append(f"| {m} | " + " | ".join(
                        _ci(p["targets"][target]["methods"][m]["paired"][bench]) for p in parts) + " |")
                out.append("")
            if "against_leap_baselines" in parts[0]["targets"][target]:
                out.append("**Leap verdict** (beats a baseline when its paired 90% interval lies wholly above zero)\n")
                out.append("| Method | " + " | ".join(f"h={p['horizon']}" for p in parts) + " |")
                out.append("|---|" + "---|" * len(parts))
                for m in ("raw",) + pc.CALIBRATORS:
                    out.append(f"| {m} | " + " | ".join(
                        p["targets"][target]["against_leap_baselines"][m]["verdict"]["result"]
                        for p in parts) + " |")
                out.append("")
            out.append("**Split by regime and pressure-day type, against the control**\n")
            for p in parts:
                first = p["targets"][target]["methods"][CANDIDATES[0]]["paired"]["vs_control"]["splits"]
                regimes, types = list(first["by_regime"]), list(first["by_day_type"])
                out.append(f"h={p['horizon']}\n")
                out.append("| Candidate | " + " | ".join(regimes + types) + " |")
                out.append("|---|" + "---|" * (len(regimes) + len(types)))
                for m in CANDIDATES:
                    s = p["targets"][target]["methods"][m]["paired"]["vs_control"]["splits"]
                    out.append(f"| {m} | " + " | ".join(
                        [_cell(s["by_regime"][r]) for r in regimes] + [_cell(s["by_day_type"][t]) for t in types]) + " |")
                out.append("")
            out.append("**Venn–Abers interval width** (p1 − p0 of the raw forecast; mean by year)\n")
            years = sorted({y for p in parts for y in p["targets"][target]["venn_abers"]["by_year"]})
            out.append("| Horizon | first day | " + " | ".join(years) + " | share > 0.10, all years |")
            out.append("|---|---|" + "---|" * len(years) + "---|")
            for p in parts:
                va = p["targets"][target]["venn_abers"]
                by = va["by_year"]
                total = sum(v["days"] for v in by.values())
                wide = sum(v["days"] * v["share_wider_than_0.10"] for v in by.values())
                out.append(f"| {p['horizon']} | {va['first_day']} | " + " | ".join(
                    _f(by[y]["mean_width"], 3) if y in by else "–" for y in years) +
                    f" | {_f(wide / total if total else None, 3)} |")
            out.append("")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    raw = sub.add_parser("raw", help="run one raw forecast at one horizon and pickle it")
    raw.add_argument("--panel", type=Path, required=True)
    raw.add_argument("--forecast", choices=("gbm", "pressure_v1"), required=True)
    raw.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    raw.add_argument("--output", type=Path, required=True)
    raw.set_defaults(func=raw_command)
    score = sub.add_parser("score", help="apply every calibrator to one raw run and score it")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("input")
    score.set_defaults(func=score_command)
    merge = sub.add_parser("assemble", help="merge the scored runs; tables")
    merge.add_argument("--output", type=Path, required=True)
    merge.add_argument("--markdown", type=Path, required=True)
    merge.add_argument("inputs", nargs="+")
    merge.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
