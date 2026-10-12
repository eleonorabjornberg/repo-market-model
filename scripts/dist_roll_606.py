"""The best tier-1 passer's tier 3 and tier 5 failures (#606): step 1, the diagnosis.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. It reads
forecasts that `scripts/satiation_distance_598.py run` and `scripts/announcement_dating_rescore.py run` already wrote, and the
judge's own output (`scripts/pressure_judge.py judge`), and reports, for `risk_gbm+settle+h41+dist_roll` and its parent
`risk_gbm+settle+h41`:

* per regime and lead: the predicted and realised rate of a pressure day at +5 bp, tier 3's test statistic (realised minus
  predicted, with its 90% stationary-bootstrap interval) and its threshold (the interval covers zero), the margin, and which
  regimes fail (only regimes with at least `calibration_min_pressure_days` pressure days are tested);
* tier 5: which of its two conditions fails (calibration; beating climatology) and by how much;
* how much of the shortfall comes from the risk-date part's exact zero on days that are not risk dates, and how many pressure
  days in each regime fall on such days.

No day after the judge's last scored day (2025-12-31) is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/dist_roll_606.py diagnose --panel PUBLISHED.csv --judge OUT/judge_weighted.json \\
        --forecasts OUT/both_h{h}.json OUT/dist_h{h}.json --bench OUT/bench_h{h}.json \\
        --output OUT/diagnosis.json --markdown OUT/diagnosis.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
PARENT = "risk_gbm+settle+h41"
BEST = "risk_gbm+settle+h41+dist_roll"
ROWS = (PARENT, BEST)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


ann = _load("announcement_dating_rescore")


def require_scored_window(last_day) -> None:
    """Refuse a last scored day after the judge's declared last day, or in a locked tier (`lockbox.md`)."""

    day = last_day if isinstance(last_day, date) else date.fromisoformat(last_day)
    pj.require_scored_days(pj.load_declaration(), [day], where="dist_roll_606")


def risk_date_shortfall(probabilities: Sequence[float], outcomes: Sequence[int], risk: Sequence[bool]) -> dict:
    """Split the mean shortfall (realised minus predicted) between risk dates and the days that are not.

    A risk-date row forecasts exactly 0 off its risk dates (`ml.pressure_risk_date_exceedance`); a non-zero forecast there is a
    defect, refused. All figures are per scored day, so that the two parts add to the total.
    """

    if not (len(probabilities) == len(outcomes) == len(risk)):
        raise ValueError("probabilities, outcomes and risk flags differ in length")
    if any(p != 0.0 for p, r in zip(probabilities, risk) if not r):
        raise ValueError("a risk-date row forecast a non-zero probability on a day that is not a risk date")
    n = len(outcomes)
    total = (sum(outcomes) - sum(probabilities)) / n if n else 0.0
    off = sum(y for y, r in zip(outcomes, risk) if not r) / n if n else 0.0
    return {
        "days": n,
        "risk_dates": sum(1 for r in risk if r),
        "pressure_days": sum(outcomes),
        "pressure_days_not_risk": sum(y for y, r in zip(outcomes, risk) if not r),
        "pressure_days_risk": sum(y for y, r in zip(outcomes, risk) if r),
        "mean_predicted": sum(probabilities) / n if n else None,
        "shortfall_total": total,
        "shortfall_not_risk": off,
        "shortfall_risk": total - off,
        "share_not_risk": (off / total) if total > 1e-12 else None,
    }


def regime_cell(cell: Mapping, *, minimum_events: int) -> dict:
    """Tier 3's reading of one regime cell: the statistic, its interval, whether it covers zero, and the margin.

    The margin is the distance from zero to the nearest end of the interval, positive when the interval covers zero (room to
    spare) and negative when it does not (how far the interval is from passing).
    """

    stat = cell["realised_minus_predicted"]
    lower, upper = stat["interval"]["lower"], stat["interval"]["upper"]
    covers = lower <= 0.0 <= upper
    margin = min(-lower, upper) if covers else -(lower if lower > 0.0 else -upper)
    return {
        "days": cell["days"],
        "events": cell["events"],
        "tested": cell["events"] >= minimum_events,
        "predicted": cell["mean_predicted"],
        "realised": cell["realised_frequency"],
        "difference": stat["mean"],
        "lower": lower,
        "upper": upper,
        "covers_zero": covers,
        "margin": margin,
    }


def _week_split(grids, by_horizon: Mapping[int, "pj.Forecast"], risk_by_h: Mapping[int, List[bool]], calendar: Sequence[date], tau: float, width: int) -> dict:
    """Tier 5's decision days, split by whether the forecast (the maximum over five leads) is exactly zero."""

    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in range(1, width + 1)}
    outcomes, combined = [], []
    for i in range(len(calendar) - width):
        targets = [calendar[i + h] for h in range(1, width + 1)]
        if any(day not in position[h] for h, day in zip(range(1, width + 1), targets)):
            continue
        at = [position[h][day] for h, day in zip(range(1, width + 1), targets)]
        outcomes.append(max(grids[h].outcomes[tau][k] for h, k in zip(range(1, width + 1), at)))
        combined.append(max(by_horizon[h].probabilities[tau][k] for h, k in zip(range(1, width + 1), at)))
    zero = [p == 0.0 for p in combined]
    n = len(outcomes)
    return {
        "decision_days": n,
        "weeks_with_pressure": sum(outcomes),
        "weeks_forecast_zero": sum(zero),
        "weeks_with_pressure_forecast_zero": sum(1 for y, z in zip(outcomes, zero) if y and z),
        "mean_predicted": sum(combined) / n,
        "base_rate": sum(outcomes) / n,
        "shortfall_total": (sum(outcomes) - sum(combined)) / n,
        "shortfall_zero_forecast": sum(1 for y, z in zip(outcomes, zero) if y and z) / n,
    }


def diagnose(args) -> dict:
    declaration = pj.load_declaration()
    require_scored_window(declaration.last_day)
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    by_date = {row.date: row for row in rows}
    calendar = [row.date for row in rows]
    judge = json.loads(Path(args.judge).read_text())
    digest = panel_sha256(args.panel)
    tau, width = declaration.primary, declaration.week_days
    minimum = declaration.calibration_min_events
    horizons = declaration.horizons

    forecasts: Dict[str, Dict[int, "pj.Forecast"]] = {name: {} for name in ROWS}
    reference = {}
    for h in horizons:
        for template in args.forecasts:
            document = json.loads(Path(template.format(h=h)).read_text())
            if document["panel_sha256"] != digest:
                raise SystemExit(f"{template.format(h=h)} was scored on another panel ({document['panel_sha256'][:8]})")
            for forecast in pj.forecasts_from_horizon_document(document):
                if forecast.name in forecasts:
                    forecasts[forecast.name][h] = forecast
        bench = json.loads(Path(args.bench.format(h=h)).read_text())
        reference[h] = next(f for f in pj.forecasts_from_horizon_document(bench) if f.name == declaration.climatology)
    for name in ROWS:
        missing = [h for h in horizons if h not in forecasts[name]]
        if missing:
            raise SystemExit(f"{name} has no forecast at horizons {missing}")
    grids = {h: pj.build_grid(declaration, h, rows, reference[h].dates, splits, scarcity_state={}) for h in horizons}

    out: Dict[str, dict] = {"panel_sha256": digest, "threshold_bp": tau, "rows": {}}
    for name in ROWS:
        verdict = judge["candidates"][name]["verdict"]
        cell = {"verdict": {k: verdict[k] for k in ("tier_1_onset_warning", "tier_3_no_crying_wolf", "tier_5_week_ahead", "passes")}}
        by_lead = {}
        for h in horizons:
            detail = judge["candidates"][name]["horizons"][str(h)][f"{tau:g}"]
            regimes = {label: regime_cell(c, minimum_events=minimum) for label, c in detail["splits"]["regime"].items()}
            by_lead[str(h)] = {
                "regimes": regimes,
                "failing": sorted(label for label, c in regimes.items() if c["tested"] and not c["covers_zero"]),
                "tier_3_ok": judge["candidates"][name]["tiers"]["no_crying_wolf"][str(h)]["ok"],
            }
        cell["tier_3_by_lead"] = by_lead
        week = judge["candidates"][name]["tiers"]["week_ahead"]
        stat = week["realised_minus_predicted"]
        clim = week["brier_difference_vs_climatology"]
        cell["tier_5"] = {
            "decision_days": week["days"],
            "events": week["events"],
            "base_rate": week["base_rate"],
            "mean_predicted": week["mean_predicted"],
            "criteria": week["criteria"],
            "calibration": {"difference": stat["mean"], "lower": stat["interval"]["lower"], "upper": stat["interval"]["upper"],
                            "covers_zero": stat["interval"]["lower"] <= 0.0 <= stat["interval"]["upper"],
                            "margin": stat["interval"]["lower"] if stat["interval"]["lower"] > 0 else None},
            "beats_climatology": {"difference": clim["mean"], "lower": clim["interval"]["lower"], "upper": clim["interval"]["upper"],
                                  "margin": clim["interval"]["lower"]},
        }
        risk_by_h = {}
        shortfall = {}
        for h in horizons:
            grid = grids[h]
            forecast = forecasts[name][h]
            if tuple(forecast.dates) != tuple(grid.dates):
                raise SystemExit(f"{name} h={h}: forecast days differ from the judge's grid")
            risk = [ann.risk_flag(splits, by_date[day].values, True) for day in grid.dates]
            risk_by_h[h] = risk
            p = forecast.probabilities[tau]
            y = grid.outcomes[tau]
            per = {"all": risk_date_shortfall(p, y, risk)}
            for label in sorted(set(grid.groups["regime"])):
                idx = [k for k, g in enumerate(grid.groups["regime"]) if g == label]
                per[label] = risk_date_shortfall([p[k] for k in idx], [y[k] for k in idx], [risk[k] for k in idx])
            shortfall[str(h)] = per
        cell["shortfall_by_lead"] = shortfall
        cell["week_split"] = _week_split(grids, forecasts[name], risk_by_h, calendar, tau, width)
        out["rows"][name] = cell
    return out


def _pct(x):
    return "–" if x is None else f"{100 * x:.1f}%"


def markdown(result: dict) -> str:
    tau = result["threshold_bp"]
    lines = [
        "# Step 1: the best tier-1 passer's tier 3 and tier 5 failures (#606)", "",
        "Generated by `scripts/dist_roll_606.py diagnose`; not edited by hand.", "",
    ]
    for name, cell in result["rows"].items():
        v = cell["verdict"]
        lines += [f"## `{name}`", "",
                  f"Verdicts: tier 1 {'met' if v['tier_1_onset_warning'] else 'not met'}; tier 3 {'met' if v['tier_3_no_crying_wolf'] else 'not met'}; "
                  f"tier 5 {'met' if v['tier_5_week_ahead'] else 'not met'}; pass: {'yes' if v['passes'] else 'no'}.", "",
                  f"### Tier 3 by regime and lead (+{tau:g} bp): predicted, realised, realised minus predicted [90% interval], margin", "",
                  "A regime is tested when it has at least 20 pressure days; it passes when the interval covers zero. Margin: the distance from "
                  "the nearer end of the interval to zero, negative when the interval excludes zero.", "",
                  "| lead | regime | days | pressure days | predicted | realised | difference [interval] | tested | covers zero | margin |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for h, lead in cell["tier_3_by_lead"].items():
            for label, c in lead["regimes"].items():
                lines.append(
                    f"| {h} | {label} | {c['days']} | {c['events']} | {c['predicted']:.4f} | {c['realised']:.4f} | "
                    f"{c['difference']:+.4f} [{c['lower']:+.4f}, {c['upper']:+.4f}] | {'yes' if c['tested'] else 'no'} | "
                    f"{'yes' if c['covers_zero'] else 'no'} | {c['margin']:+.4f} |")
        lines += ["", "Failing regimes by lead: " + "; ".join(f"h = {h}: {', '.join(l['failing']) or 'none'}" for h, l in cell["tier_3_by_lead"].items()) + ".", ""]
        t5 = cell["tier_5"]
        cal, clim = t5["calibration"], t5["beats_climatology"]
        lines += ["### Tier 5 (probability of a pressure day in the next five business days, maximum over the five leads)", "",
                  f"{t5['decision_days']} decision days, {t5['events']} with a pressure day (base rate {t5['base_rate']:.4f}); mean forecast {t5['mean_predicted']:.4f}.", "",
                  f"- Condition 1, calibrated (realised minus predicted, interval covers zero): {cal['difference']:+.4f} [{cal['lower']:+.4f}, {cal['upper']:+.4f}]: "
                  f"**{'holds' if t5['criteria']['calibrated'] else 'fails'}**" + (f", the interval's lower end is {cal['margin']:.4f} above zero." if cal["margin"] is not None else "."),
                  f"- Condition 2, beats climatology on Brier (difference, climatology minus row, interval above zero): {clim['difference']:+.4f} [{clim['lower']:+.4f}, {clim['upper']:+.4f}]: "
                  f"**{'holds' if t5['criteria']['beats_climatology_brier'] else 'fails'}**, margin {clim['margin']:+.4f}.", ""]
        w = cell["week_split"]
        lines += [f"Weeks: {w['weeks_with_pressure']} of {w['decision_days']} have a pressure day; the row forecasts exactly 0 for {w['weeks_forecast_zero']} weeks, "
                  f"and {w['weeks_with_pressure_forecast_zero']} of the weeks with a pressure day are among them. Shortfall per decision day "
                  f"{w['shortfall_total']:+.4f}, of which {w['shortfall_zero_forecast']:.4f} sits on the zero-forecast weeks.", ""]
        lines += [f"### Do the misses come from the exact zero off the risk dates? (+{tau:g} bp, per lead)", "",
                  "Shortfall = mean of realised minus predicted per scored day; 'off' = the part carried by pressure days on days that are not risk dates.", "",
                  "| lead | regime | days | risk dates | pressure days | of which not on a risk date | shortfall | off-risk-date part | share off |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for h, per in cell["shortfall_by_lead"].items():
            for label, s in per.items():
                lines.append(f"| {h} | {label} | {s['days']} | {s['risk_dates']} | {s['pressure_days']} | {s['pressure_days_not_risk']} | "
                             f"{s['shortfall_total']:+.4f} | {s['shortfall_not_risk']:.4f} | {_pct(s['share_not_risk'])} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def diagnose_command(args) -> int:
    result = diagnose(args)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("diagnose")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--judge", type=Path, required=True)
    p.add_argument("--forecasts", nargs="+", required=True)
    p.add_argument("--bench", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    args = parser.parse_args(argv)
    return {"diagnose": diagnose_command}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
