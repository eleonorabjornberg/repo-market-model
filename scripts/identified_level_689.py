"""Identified estimators for the satiation level in the kinked structural model (#689, finding #671): scoring and report.

A scratch measurement on development data, not a record and not a verdict under scoring protocol v1 (#640): it writes JSON and
Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in `metadata/identified_level_689.json`, which
`run` refuses to read unless it is committed and unchanged. Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is
read (`docs/decisions/lockbox.md`). The panel chain is the one of `scripts/kinked_626.py` (its scratch panel carries the rolling
level and the distance columns); the reserves leg of the ratio is read per H.4.1 release (ruling on #541; #622).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
    PYTHONPATH=src python3 scripts/projected_reserves.py panel --panel AUG3.csv --output AUG4.csv
    PYTHONPATH=src python3 scripts/kinked_626.py panel --panel AUG4.csv --output AUG5.csv
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/identified_level_689.py run --panel AUG5.csv --published PUBLISHED.csv --horizon $h --output OUT/id_h$h.json
    PYTHONPATH=src python3 scripts/identified_level_689.py report --published PUBLISHED.csv --scratch AUG5.csv --bench 'OUT/bench_h{h}.json' \\
        --rows 'OUT/id_h{h}.json' --output OUT/report.json --markdown OUT/report.md

`run` scores, walk-forward at +5 and +10 bp on the shared fold grid, the like-for-like control of #626 (`structural_liquidity+h41`),
its two kinked variants (`structural_kinked_fitted`, `structural_kinked_rolling`) and the two new rows (`structural_kinked_profile`,
`structural_kinked_slow`). `report` is the refit path of each level estimator and its stability, and, on days that are not scheduled
risk dates, the AUROC, the Brier skill against the calendar climatology and the reliability line of each row, paired with the two
kinked references, with the same cuts by regime and the 2025 onsets described one by one.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import math
import random
import statistics
import sys
from datetime import date, time
from operator import itemgetter
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import h41_release, measurement_fields, pressure_judge as pj, satiation as sat, structural_liquidity as sl  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "identified_level_689.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
CONTROL = "structural_liquidity+h41"
REFERENCES = ("structural_kinked_fitted", "structural_kinked_rolling")
NEW = ("structural_kinked_profile", "structural_kinked_slow")
ROWS = ((CONTROL, "fixed"), ("structural_kinked_fitted", "kinked_fitted"), ("structural_kinked_rolling", "kinked_rolling"),
        ("structural_kinked_profile", "kinked_profile"), ("structural_kinked_slow", "kinked_slow"))
PRIMARY = "5"
WARNING_QUANTILE = 0.9
WARNING_WINDOW = 252
WARNING_MINIMUM = 63
MIN_EVENTS = 10


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


k626 = _load("kinked_626")


def declared_document() -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD` (a declaration is made before any score)."""

    return k626.rds.committed_declaration(DECLARATION)


# -- run -----------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declared = declared_document()
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="identified_level_689")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    dated = k626.dated_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = scoring["minimum_history"]

    def backtest(predictor, name, features):
        with k626.switched_on(), h41_release.release_dating():
            return rolling_exceedance_backtest(
                rows, predictor=predictor, model_name=name, features=features, registry=dated,
                decision_time=time.fromisoformat(scoring["decision_time"]), taus=taus, minimum_history=minimum,
                refit_every=scoring["refit_every"], end=last, horizon=h,
            )

    forecasts: Dict[str, dict] = {}
    refits: Dict[str, list] = {}
    for name, form in ROWS:
        features = sl.features_at_horizon(h, form)
        log: list = []
        inner = sl.structural_exceedance(features, splits, minimum_history=minimum, satiation=form)
        report = backtest(_logged(inner, log), name, features)
        forecast = pj.report_forecast(name, report)
        forecasts[name] = {
            f"{tau:g}": {day.isoformat(): p for day, p in zip(forecast.dates, values)} for tau, values in forecast.probabilities.items()
        }
        refits[name] = log
        print(json.dumps({"horizon": h, "row": name, "refits": len(log), "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "refits": refits,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "output": str(args.output)}))
    return 0


def _logged(predictor, log: list):
    """The predictor, unchanged, with each refit's record kept (the profile's per-level excess is dropped: 49 numbers a refit)."""

    def fit_predict(train_rows, feature_rows, taus, information=None, histories=None):
        result = predictor(train_rows, feature_rows, taus, information=information, histories=histories)
        entry = {
            "first_anchor": feature_rows[0].date.isoformat(),
            "last_training_row": train_rows[-1].date.isoformat(),
            "training_rows": len(train_rows),
            "served_days": len(feature_rows),
        }
        if getattr(predictor, "fits", None):
            record = predictor.fits[-1]
            entry.update({key: value for key, value in record.items() if key in (
                "satiation_level", "fitted", "reason", "pairs", "slope", "profile_level", "previous_level", "interval", "local_minima",
            )})
            if "excess" in record:
                entry["excess_at_fixed"] = _at(record["excess"], sat.FIXED)
        log.append(entry)
        return result

    return fit_predict


def _at(excess: Sequence[Optional[float]], level: float) -> Optional[float]:
    for k, e in zip(sat.KINK_GRID, excess):
        if abs(k - level) < 1e-9:
            return e
    return None


# -- report --------------------------------------------------------------------------------------------------------


def stability(levels: Sequence[float]) -> dict:
    """The path statistics of a sequence of levels, one per refit (declared in `reports.refit_path`)."""

    moves = [abs(b - a) for a, b in zip(levels, levels[1:])]
    return {
        "refits": len(levels),
        "distinct_levels": len({round(v, 6) for v in levels}),
        "mean_abs_change": statistics.fmean(moves) if moves else None,
        "max_abs_change": max(moves) if moves else None,
        "changes_of_0.01_or_more": sum(1 for m in moves if m >= 0.01 - 1e-12),
        "sd": statistics.pstdev(levels) if len(levels) > 1 else None,
        "last": levels[-1] if levels else None,
    }


def rolling_levels_at(scratch, refits: Sequence[dict]) -> List[float]:
    """The scratch panel's `satiation_roll` at each refit's last training row."""

    index = {r.date.isoformat(): r for r in scratch}
    return [float(index[entry["last_training_row"]].values[sat.ROLLING_COLUMN]) for entry in refits]


def _interval(values: Sequence[Optional[float]], level: float) -> Optional[List[float]]:
    kept = sorted(v for v in values if v is not None)
    if len(kept) < 0.5 * len(values) or not kept:
        return None
    lo, hi = (1.0 - level) / 2.0, 1.0 - (1.0 - level) / 2.0
    return [kept[int(lo * (len(kept) - 1))], kept[int(hi * (len(kept) - 1))]]


def brier(p: Sequence[float], y: Sequence[int]) -> float:
    return sum((a - b) ** 2 for a, b in zip(p, y)) / len(y)


def brier_skill(p: Sequence[float], clim: Sequence[float], y: Sequence[int]) -> Optional[float]:
    base = brier(clim, y)
    return None if base <= 0.0 else 1.0 - brier(p, y) / base


def warned(p_by_day: Dict[date, float], days: Sequence[date], day: date) -> Optional[bool]:
    """Whether the forecast on `day` is above the as-of 90th percentile of the row's forecasts on the 252 scored days before it."""

    position = days.index(day)
    past = [p_by_day[d] for d in days[max(0, position - WARNING_WINDOW): position]]
    if len(past) < WARNING_MINIMUM:
        return None
    return p_by_day[day] > sat.quantile(past, WARNING_QUANTILE)


def report_command(args) -> int:
    declared = declared_document()
    end = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([end], where="identified_level_689")
    judge_script = _load("pressure_judge")
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    base = pj.load_declaration()
    splits = load_split_declaration(SPLITS)
    published = load_daily_panel(args.published)
    scratch = [r for r in load_daily_panel(args.scratch) if r.date <= end]
    names = [name for name, _form in ROWS]
    docs = {h: json.loads(Path(args.rows.format(h=h)).read_text()) for h in declared["horizons"]}
    # ---- the refit path of each level estimator
    paths: Dict[str, dict] = {}
    for h, doc in docs.items():
        cell: Dict[str, dict] = {}
        fitted = doc["refits"]["structural_kinked_fitted"]
        cell["least_squares (kinked_fitted)"] = {
            "path": [(e["last_training_row"], e.get("satiation_level")) for e in fitted],
            "stability": stability([e["satiation_level"] for e in fitted if e.get("fitted")]),
        }
        rolling = doc["refits"]["structural_kinked_rolling"]
        levels = rolling_levels_at(scratch, rolling)
        cell["rolling (kinked_rolling)"] = {
            "path": [(e["last_training_row"], v) for e, v in zip(rolling, levels)], "stability": stability(levels),
        }
        for name in NEW:
            log = doc["refits"][name]
            used = [e for e in log if e.get("fitted")]
            widths = [e["interval"][1] - e["interval"][0] for e in used]
            cell[name] = {
                "path": [(e["last_training_row"], e["satiation_level"]) for e in log],
                "stability": stability([e["satiation_level"] for e in used]),
                "median_interval_width": statistics.median(widths) if widths else None,
                "share_interval_at_the_grid_edge": (
                    sum(1 for e in used if e["interval"][0] <= min(sat.KINK_GRID) + 1e-9 or e["interval"][1] >= max(sat.KINK_GRID) - 1e-9)
                    / len(used) if used else None
                ),
                "share_with_several_local_minima": sum(1 for e in used if e["local_minima"] > 1) / len(used) if used else None,
                "median_excess_at_fixed_nats": statistics.median([e["excess_at_fixed"] for e in used if e.get("excess_at_fixed") is not None] or [math.nan]),
            }
        if "structural_kinked_slow" in cell and "structural_kinked_profile" in cell:
            profile_levels = [e["profile_level"] for e in docs[h]["refits"]["structural_kinked_slow"] if e.get("fitted")]
            cell["structural_kinked_slow"]["profile_level_stability"] = stability(profile_levels)
        paths[str(h)] = cell
    # ---- ordinary days
    judge_script = _load("pressure_judge")
    level, replications, block, seed = base.level, base.replications, base.block_length, base.seed
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in base.horizons}
    out: Dict[str, dict] = {}
    onsets_2025: Dict[str, dict] = {}
    for h in declared["horizons"]:
        columns: Dict[str, Dict[str, float]] = {n: docs[h]["forecasts"][n][PRIMARY] for n in names}
        bench = json.loads(Path(args.bench.format(h=h)).read_text())["forecasts"]
        clim = bench[base.climatology][PRIMARY]
        days = sorted(date.fromisoformat(d) for d in columns[CONTROL])
        grid = pj.build_grid(base, h, published, days, splits, scarcity_state=states[h])
        outcome_all = list(grid.outcomes[base.primary])
        keep = [i for i, label in enumerate(grid.groups["risk_date"]) if label == "0"]
        y = [outcome_all[i] for i in keep]
        p = {n: [columns[n][days[i].isoformat()] for i in keep] for n in names}
        c = [clim[days[i].isoformat()] for i in keep]
        regimes = [grid.groups["regime"][i] for i in keep]
        rng = random.Random(seed + h)
        resamples = [pj.stationary_bootstrap_indices(len(keep), block, rng) for _ in range(replications)]
        boot = {n: {"auroc": [], "skill": []} for n in names}
        for idx in resamples:
            pick = itemgetter(*idx)
            y_b, c_b = list(pick(y)), list(pick(c))
            for n in names:
                p_b = list(pick(p[n]))
                boot[n]["auroc"].append(pj.auroc(p_b, y_b))
                boot[n]["skill"].append(brier_skill(p_b, c_b, y_b))
        cell: Dict[str, dict] = {"days": len(keep), "events": sum(y)}
        for n in names:
            line = k626.reliability(p[n], y)
            auc = pj.auroc(p[n], y)
            skill = brier_skill(p[n], c, y)
            entry = {
                "auroc": auc, "auroc_interval": _interval(boot[n]["auroc"], level),
                "brier_skill": skill, "brier_skill_interval": _interval(boot[n]["skill"], level),
                "intercept": None if line is None else line[0], "slope": None if line is None else line[1],
                "mean_forecast": sum(p[n]) / len(p[n]), "realised": sum(y) / len(y),
                "by_regime": {},
            }
            for regime in sorted(set(regimes)):
                sel = [i for i, r in enumerate(regimes) if r == regime]
                ys = [y[i] for i in sel]
                if sum(ys) < MIN_EVENTS:
                    entry["by_regime"][regime] = {"days": len(sel), "events": sum(ys)}
                    continue
                reg_line = k626.reliability([p[n][i] for i in sel], ys)
                entry["by_regime"][regime] = {
                    "days": len(sel), "events": sum(ys), "brier_skill": brier_skill([p[n][i] for i in sel], [c[i] for i in sel], ys),
                    "intercept": None if reg_line is None else reg_line[0], "slope": None if reg_line is None else reg_line[1],
                }
            for ref in REFERENCES:
                if n == ref:
                    continue
                diffs_auc = [None if a is None or b is None else a - b for a, b in zip(boot[n]["auroc"], boot[ref]["auroc"])]
                diffs_skill = [None if a is None or b is None else a - b for a, b in zip(boot[n]["skill"], boot[ref]["skill"])]
                auc_ref, skill_ref = pj.auroc(p[ref], y), brier_skill(p[ref], c, y)
                entry[f"minus_{ref}"] = {
                    "auroc": None if auc is None or auc_ref is None else auc - auc_ref,
                    "auroc_interval": _interval(diffs_auc, level),
                    "brier_skill": None if skill is None or skill_ref is None else skill - skill_ref,
                    "brier_skill_interval": _interval(diffs_skill, level),
                }
            cell[n] = entry
        out[str(h)] = cell
        # ---- the 2025 onsets, all scored days (a risk date can be an onset)
        every = {n: {date.fromisoformat(d): v for d, v in columns[n].items()} for n in names}
        listing = []
        for i, day in enumerate(days):
            if day.year == 2025 and grid.onset[i]:
                row = {"day": day.isoformat(), "risk_date": grid.groups["risk_date"][i]}
                for n in names:
                    row[n] = {"p": every[n][day], "warned": warned(every[n], days, day)}
                listing.append(row)
        onsets_2025[str(h)] = {"onsets": listing}
        print(json.dumps({"horizon": h, "ordinary_days": len(keep), "events": sum(y)}), flush=True)
    result = {
        "level": level, "replications": replications, "paths": paths, "ordinary_days": out, "onsets_2025": onsets_2025,
        "declaration_penalty_per_pair": declared["penalty_per_pair"],
    }
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(report_text(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _f(value, places=3):
    return "–" if value is None else f"{value:.{places}f}"


def _iv(point, interval, places=3):
    if point is None:
        return "–"
    if interval is None:
        return f"{point:.{places}f}"
    return f"{point:.{places}f} [{interval[0]:.{places}f}, {interval[1]:.{places}f}]"


def report_text(result: dict) -> str:
    lines = ["# Identified estimators for the satiation level (#689)", "",
             "Generated by `scripts/identified_level_689.py report`; not edited by hand. Development data, exploratory, no verdict.", ""]
    lines += ["## The refit path of the level, by estimator and horizon", "",
              "| h | estimator | fitted refits | distinct levels | mean abs change | largest change | changes of 0.01 or more | sd | last level |",
              "|---|---|---|---|---|---|---|---|---|"]
    for h, cell in sorted(result["paths"].items()):
        for name, entry in cell.items():
            s = entry["stability"]
            lines.append(
                f"| {h} | {name} | {s['refits']} | {s['distinct_levels']} | {_f(s['mean_abs_change'], 4)} | {_f(s['max_abs_change'], 4)} | "
                f"{s['changes_of_0.01_or_more']} | {_f(s['sd'], 4)} | {_f(s['last'], 4)} |"
            )
    lines += ["", "## How well the profile identifies the level", "",
              "| h | estimator | median width of the 1.92-nat interval | share of refits whose interval touches the grid edge | share with several local minima | median excess of the fixed 0.12 (nats) |",
              "|---|---|---|---|---|---|"]
    for h, cell in sorted(result["paths"].items()):
        for name in NEW:
            e = cell[name]
            lines.append(
                f"| {h} | {name} | {_f(e['median_interval_width'], 4)} | {_f(e['share_interval_at_the_grid_edge'], 2)} | "
                f"{_f(e['share_with_several_local_minima'], 2)} | {_f(e['median_excess_at_fixed_nats'], 2)} |"
            )
    lines += ["", "## Days that are not risk dates, +5 bp: AUROC, Brier skill against the calendar climatology, reliability line", "",
              "90% stationary-bootstrap intervals. The differences are against `structural_kinked_fitted` and `structural_kinked_rolling`, on shared resamples.", ""]
    for h, cell in sorted(result["ordinary_days"].items()):
        lines += [f"### h = {h}: {cell['days']} days, {cell['events']} above +5 bp", "",
                  "| row | AUROC | Brier skill | intercept | slope | mean forecast / realised | AUROC minus kinked_fitted | AUROC minus kinked_rolling | Brier skill minus kinked_fitted | Brier skill minus kinked_rolling |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for name, c in cell.items():
            if not isinstance(c, dict):
                continue
            def d(ref, key):
                entry = c.get(f"minus_{ref}")
                return "–" if entry is None else _iv(entry[key], entry[f"{key}_interval"])
            lines.append(
                f"| {name} | {_iv(c['auroc'], c['auroc_interval'])} | {_iv(c['brier_skill'], c['brier_skill_interval'])} | {_f(c['intercept'])} | "
                f"{_f(c['slope'])} | {c['mean_forecast']:.4f} / {c['realised']:.4f} | {d('structural_kinked_fitted', 'auroc')} | "
                f"{d('structural_kinked_rolling', 'auroc')} | {d('structural_kinked_fitted', 'brier_skill')} | {d('structural_kinked_rolling', 'brier_skill')} |"
            )
        lines.append("")
        regimes = sorted({r for c in cell.values() if isinstance(c, dict) for r in c["by_regime"]})
        lines += ["Within each regime (Brier skill; reliability intercept and slope; blank where fewer than 10 events):", "",
                  "| row | " + " | ".join(regimes) + " |", "|---|" + "---|" * len(regimes)]
        for name, c in cell.items():
            if not isinstance(c, dict):
                continue
            cells = []
            for r in regimes:
                e = c["by_regime"].get(r)
                cells.append("–" if not e or "brier_skill" not in e else f"{_f(e['brier_skill'])}; {_f(e['intercept'], 2)}, {_f(e['slope'], 2)}")
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
        lines.append("")
    lines += ["## The 2025 onsets", "",
              "`w` = above the as-of 90th percentile of the row's own forecasts over the 252 scored days before it; `–` = fewer than 63 days. "
              "Not the judge's cut-off rule.", ""]
    for h, cell in sorted(result["onsets_2025"].items()):
        rows = cell["onsets"]
        if not rows:
            continue
        lines += [f"### h = {h}", "", "| onset day | " + " | ".join(n for n, _ in ROWS) + " |", "|---|" + "---|" * len(ROWS)]
        for r in rows:
            lines.append(f"| {r['day']}{' (risk date)' if r['risk_date'] == '1' else ''} | " + " | ".join(
                f"{r[n]['p']:.3f}{' w' if r[n]['warned'] else ('' if r[n]['warned'] is False else ' –')}" for n, _ in ROWS) + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--horizon", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("report")
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--scratch", type=Path, required=True)
    p.add_argument("--bench", required=True)
    p.add_argument("--rows", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    args = parser.parse_args(argv)
    return {"run": run_command, "report": report_command}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
