"""Coupon settlement dated from its auction result, scored and off (#175).

A scratch measurement, not a record: it writes pickles, JSON and a Markdown
summary to the paths it is given, and nothing into `docs/runs/`.

Two arms of the published pressure model v1 (`scripts/pressure_model_v1.py
publish`, the probability read from the published funding declaration's
distribution, gbm calibrated by conformal PID with nested selection, then
recalibrated out of fold), on one fold grid, scoring only days before
2026-01-01 (`docs/decisions/lockbox.md`):

* `published`: the published declaration. At h >= 2 it drops
  `treasury_settlement` from the features and the coupon-settlement indicator
  from the scorecaster (#114; #170, option A).
* `result_dated`: `metadata/settlement_result_dating.json`. The settlement
  columns are those known h panel days ahead from auction results
  (`settlement_dating.known_columns`, checked by `check_known_columns`), and
  the registry declares them public then (`result_dated_registry`). The
  feature and the indicator are both restored.

At h = 1 the two declarations are the same, so `published` alone is run there,
for lead time. Steps, each one process:

    PYTHONPATH=src python3 scripts/settlement_result_dating.py arm --panel PANEL --horizon H \
        --arm published|result_dated|calendar_climatology|persistence_logistic --output OUT/ARM_hH.pickle
    PYTHONPATH=src python3 scripts/settlement_result_dating.py compare --panel PANEL --runs OUT \
        --output OUT/settlement_result_dating.json --markdown OUT/settlement_result_dating.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pickle
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure, settlement_dating  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    calendar_climatology_exceedance,
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import audit_panel, load_daily_panel, load_stress_thresholds  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

_spec = importlib.util.spec_from_file_location("pressure_model_v1", REPO / "scripts" / "pressure_model_v1.py")
v1 = importlib.util.module_from_spec(_spec)
sys.modules["pressure_model_v1"] = v1  # so its pickling registration resolves
_spec.loader.exec_module(v1)  # also registers the read-only mappings for pickling

DECLARATION = REPO / "metadata" / "settlement_result_dating.json"
SNAPSHOT = (
    REPO / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "treasury_auctions"
    / "20260914T051023Z_722359ea9bc7.json"
)
ARMS = ("published", "result_dated")
BENCHMARKS = ("calendar_climatology", "persistence_logistic")
HEADLINE = (5.0, 10.0)
LONG = (2, 3, 4, 5)


def _taus():
    return tuple(float(tau) for tau in load_stress_thresholds(v1.THRESHOLDS)["taus_bp"])


def _inputs(panel, arm, h):
    """The rows, registry and features an arm is scored on at horizon `h`."""

    rows = load_daily_panel(panel)
    audit_panel(rows)
    registry = json.loads(v1.REGISTRY.read_text())
    if arm != "result_dated":
        return rows, registry, v1._at_horizon(v1.GBM_FEATURES, h)
    declaration = settlement_dating.load_result_dating(DECLARATION)
    results = settlement_dating.load_snapshot_results(SNAPSHOT, declaration)
    known = settlement_dating.known_columns(rows, results, h, declaration)
    settlement_dating.check_known_columns(known, results, h, declaration)
    return known, settlement_dating.result_dated_registry(registry, declaration, h), v1.GBM_FEATURES


def arm_command(args) -> int:
    from repo_model import ml, recalibration

    h, arm = args.horizon, args.arm
    if arm == "result_dated" and h == 1:
        raise SystemExit("at h = 1 the result-dated declaration is the published one; run `published`")
    rows, registry, features = _inputs(args.panel, arm, h)
    splits = load_split_declaration(v1.SPLITS)
    taus = _taus()

    class _AllIndicators(recalibration.NestedFoldPid):
        """Nested PID with all four scorecaster indicators at any horizon (#175)."""

        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._indicators = recalibration.SCORECASTER_INDICATORS

        def _variant(self):
            return {"scorecaster_variant": "coupon settlement dated from its auction result (#175)"}

    built = []

    def online(rows_, rule):
        factory = _AllIndicators if arm == "result_dated" else recalibration.NestedFoldPid
        built.append(factory(rows_, rule, splits=splits, refit_every=v1.REFIT_EVERY))
        return built[-1]

    def run(name, predictor, declared, calibration=None):
        return rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=name, features=declared, registry=registry,
            decision_time=v1.DECISION, taus=taus, minimum_history=v1.MINIMUM_HISTORY,
            refit_every=v1.REFIT_EVERY, end=v1.END, horizon=h, online_calibration=calibration,
        )

    if arm == "calendar_climatology":
        report = run(arm, calendar_climatology_exceedance(splits, minimum_history=v1.MINIMUM_HISTORY),
                     v1.CALENDAR_FEATURES)
        settings = None
    elif arm == "persistence_logistic":
        report = run(arm, persistence_logistic_exceedance(minimum_history=v1.MINIMUM_HISTORY), ("spread_bps",))
        settings = None
    else:
        raw = run(
            arm,
            ml.gbm_exceedance(tuple(n for n in features if n != "spread_bps"), minimum_history=v1.MINIMUM_HISTORY),
            features,
            online,
        )
        report = v1._rescored(pressure.recalibrated(raw))
        settings = built[0].settings
    args.output.write_bytes(pickle.dumps({
        "arm": arm, "horizon": h, "features": list(features), "calibration": settings, "report": report,
    }))
    print(json.dumps({"arm": arm, "horizon": h, "scored_days": len(report.scored_dates),
                      "first": report.scored_dates[0].isoformat(), "last": report.scored_dates[-1].isoformat()}))
    return 0


# -- comparison ---------------------------------------------------------------


def _load(runs, arm, h):
    return pickle.loads((runs / f"{arm}_h{h}.pickle").read_bytes())


def _by_day(report, tau):
    position = report.taus.index(tau)
    return {when: curve[position] for when, curve in zip(report.scored_dates, report.forecast)}


def _onset_view(rows, published, dated, tau):
    """Paired Brier on the onset days both arms scored: mean difference and the days."""

    a, b = _by_day(published, tau), _by_day(dated, tau)
    spread = {row.date: float(row.spread_bps) for row in rows}
    days = [when for when in pressure.onsets(rows, tau, published.scored_dates) if when in b]
    per_day = [
        {"date": when.isoformat(), "spread_bps": spread[when], "published": a[when], "result_dated": b[when],
         "difference": (1 - a[when]) ** 2 - (1 - b[when]) ** 2}
        for when in days
    ]
    return {
        "onsets": len(per_day),
        "mean_difference": None if not per_day else sum(d["difference"] for d in per_day) / len(per_day),
        "days": per_day,
    }


def compare_command(args) -> int:
    rows = load_daily_panel(args.panel)
    splits = load_split_declaration(v1.SPLITS)
    digest = panel_sha256(args.panel)
    declaration = settlement_dating.load_result_dating(DECLARATION)
    results = settlement_dating.load_snapshot_results(SNAPSHOT, declaration)
    horizons = {}
    loaded = {}
    for h in LONG:
        published = _load(args.runs, "published", h)
        dated = _load(args.runs, "result_dated", h)
        benches = {name: _load(args.runs, name, h)["report"] for name in BENCHMARKS}
        loaded[h] = (published["report"], dated["report"])
        card = pressure.scorecard(
            {"result_dated": dated["report"]},
            {"published": published["report"], **benches},
            rows=rows, declaration=splits, panel_sha256=digest,
        )
        card_published = pressure.scorecard(
            {"published": published["report"]}, benches, rows=rows, declaration=splits, panel_sha256=digest,
        )
        horizons[str(h)] = {
            "scored_window": {
                "first": dated["report"].scored_dates[0].isoformat(),
                "last": dated["report"].scored_dates[-1].isoformat(),
                "days": len(dated["report"].scored_dates),
            },
            "declarations": {
                arm: {"features": run["features"], "calibration": run["calibration"]}
                for arm, run in (("published", published), ("result_dated", dated))
            },
            "twcrps": {"published": published["report"].twcrps, "result_dated": dated["report"].twcrps},
            "scorecard": card,
            "published_vs_benchmarks": card_published,
            "onset_days": {
                f"{tau:g}": _onset_view(rows, published["report"], dated["report"], tau) for tau in HEADLINE
            },
        }
    h1 = _load(args.runs, "published", 1)["report"]
    lead = {}
    for tau in HEADLINE:
        key = f"{tau:g}"
        common = sorted(set(h1.scored_dates).intersection(*(set(loaded[h][0].scored_dates) for h in LONG)))
        onset_days = pressure.onsets(rows, tau, common)
        lead[key] = {"onsets": [d.isoformat() for d in onset_days], "by_arm": {}}
        for index, arm in enumerate(ARMS):
            per_h = {1: _by_day(h1, tau), **{h: _by_day(loaded[h][index], tau) for h in LONG}}
            lead[key]["by_arm"][arm] = [
                pressure.lead_times(per_h, onset_days, level) for level in pressure.ALARM_LEVELS
            ]
    document = {
        "directive": "#175",
        "status": "scratch measurement; not a record, nothing published moves",
        "panel_sha256": digest,
        "declaration": declaration,
        "coverage": {
            str(h): counts for h, counts in settlement_dating.coverage(
                rows, results, (1,) + LONG, declaration, end=v1.END
            ).items()
        },
        "fold_grid": {"walk_forward": "expanding window", "refit_every": v1.REFIT_EVERY,
                      "minimum_history": v1.MINIMUM_HISTORY, "end": v1.END.isoformat()},
        "horizons": horizons,
        "lead_time": lead,
        "lead_time_definition": "the longest horizon (h = 1 shared by both arms) whose forecast of the onset day reached the alarm level; 0 when none did",
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    args.markdown.write_text(_markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "markdown": str(args.markdown)}))
    return 0


def _cell(paired):
    i = paired["interval"]
    return f"{paired['mean']:+.4f} [{i['lower']:+.4f}, {i['upper']:+.4f}]"


def _split(entry):
    if "mean" not in entry:
        return "– (n=0)"
    i = entry.get("interval")
    if not i:
        return f"{entry['mean']:+.4f} (n={entry['count']}, no interval)"
    return f"{entry['mean']:+.4f} [{i['lower']:+.4f}, {i['upper']:+.4f}] (n={entry['count']})"


def _markdown(doc) -> str:
    out = [f"Panel `{doc['panel_sha256'][:12]}…`; no scored day on or after 2026-01-01.\n"]
    out.append("**Settlement days (to 2025-12-31) whose auction results were public at the decision**\n")
    out.append("| Horizon | Settlement days | All results public | Some | None |\n|---|---|---|---|---|")
    for h, c in doc["coverage"].items():
        out.append(f"| {h} | {c['settlement_days']} | {c['complete']} | {c['partial']} | {c['none']} |")
    out.append("")
    out.append("Paired difference = Brier(other) − Brier(result_dated), mean over scored days, 90% stationary-"
               "bootstrap interval; positive means the result-dated declaration had the lower Brier.\n")
    for tau in HEADLINE:
        key = f"{tau:g}"
        out.append(f"### +{key} bp\n")
        out.append("| Horizon | Days | Brier published | Brier result-dated | result-dated vs published | "
                   "result-dated vs calendar climatology | result-dated vs persistence-logistic | "
                   "published vs persistence-logistic |")
        out.append("|---|---|---|---|---|---|---|---|")
        for h, part in doc["horizons"].items():
            card = part["scorecard"]
            paired = card["candidates"]["result_dated"]["paired"]
            out.append(
                f"| {h} | {part['scored_window']['days']} | "
                f"{card['benchmarks']['published'][key]['brier']:.4f} | "
                f"{card['candidates']['result_dated']['metrics'][key]['brier']:.4f} | "
                + " | ".join(_cell(paired[b]["by_tau"][key]["paired_brier_difference"])
                             for b in ("published",) + BENCHMARKS)
                + " | "
                + _cell(part["published_vs_benchmarks"]["candidates"]["published"]["paired"]["persistence_logistic"]
                        ["by_tau"][key]["paired_brier_difference"])
                + " |"
            )
        out.append("")
        out.append(f"**+{key} bp, result-dated vs published, split by regime and pressure-day type**\n")
        first = next(iter(doc["horizons"].values()))
        s0 = first["scorecard"]["candidates"]["result_dated"]["paired"]["published"]["by_tau"][key]["paired_brier_difference"]["splits"]
        regimes, types = list(s0["by_regime"]), list(s0["by_day_type"])
        out.append("| Horizon | " + " | ".join(regimes + types) + " |")
        out.append("|---|" + "---|" * (len(regimes) + len(types)))
        for h, part in doc["horizons"].items():
            s = part["scorecard"]["candidates"]["result_dated"]["paired"]["published"]["by_tau"][key]["paired_brier_difference"]["splits"]
            out.append(f"| {h} | " + " | ".join([_split(s["by_regime"][r]) for r in regimes]
                                                 + [_split(s["by_day_type"][t]) for t in types]) + " |")
        out.append("")
        out.append(f"**+{key} bp, onset days**: Brier(published) − Brier(result_dated), mean over the onset days\n")
        out.append("| Horizon | Onsets | Mean difference |\n|---|---|---|")
        for h, part in doc["horizons"].items():
            o = part["onset_days"][key]
            mean = "–" if o["mean_difference"] is None else f"{o['mean_difference']:+.4f}"
            out.append(f"| {h} | {o['onsets']} | {mean} |")
        out.append("")
    out.append("### Lead time to pressure onset (h = 1 shared)\n")
    for tau in HEADLINE:
        key = f"{tau:g}"
        out.append(f"**+{key} bp**: {len(doc['lead_time'][key]['onsets'])} onsets\n")
        out.append("| Arm | " + " | ".join(f"flagged at {lv:g} | mean lead at {lv:g}" for lv in pressure.ALARM_LEVELS)
                   + " |\n|---|" + "---|---|" * len(pressure.ALARM_LEVELS))
        for arm, results in doc["lead_time"][key]["by_arm"].items():
            cells = []
            for r in results:
                lead = "–" if r["mean_lead_days"] is None else f"{r['mean_lead_days']:.2f}"
                cells += [f"{r['flagged']}/{r['onsets']}", lead]
            out.append(f"| {arm} | " + " | ".join(cells) + " |")
        out.append("")
    out.append("### twCRPS (mean over scored days, all declared thresholds)\n")
    out.append("| Horizon | published | result-dated |\n|---|---|---|")
    for h, part in doc["horizons"].items():
        t = part["twcrps"]
        out.append(f"| {h} | {t['published']:.4f} | {t['result_dated']:.4f} |")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("arm", help="score one arm at one horizon")
    one.add_argument("--panel", type=Path, required=True)
    one.add_argument("--horizon", type=int, choices=(1,) + LONG, required=True)
    one.add_argument("--arm", choices=ARMS + BENCHMARKS, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=arm_command)
    both = sub.add_parser("compare", help="pair the arms; splits, onset days, lead time, tables")
    both.add_argument("--panel", type=Path, required=True)
    both.add_argument("--runs", type=Path, required=True)
    both.add_argument("--output", type=Path, required=True)
    both.add_argument("--markdown", type=Path, required=True)
    both.set_defaults(func=compare_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
