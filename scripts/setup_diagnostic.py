#!/usr/bin/env python3
"""The setup diagnostic (#480): does the evaluation setup itself explain the misses?

**Reported only. No model change, no bar change, nothing published moves, no 2026 day is read.**
The choices are in `metadata/setup_diagnostic.json`, which this script refuses to read unless it is committed and
unchanged. It writes JSON and a Markdown summary to the paths it is given, and nothing into `docs/runs/`.

    PYTHONPATH=src python3 scripts/setup_diagnostic.py run --panel PUB.csv \\
        --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' \\
        --output OUT/setup_diagnostic.json --markdown OUT/setup_diagnostic.md

`--bench` is `pressure_judge.py forecasts` and `--risk` is `risk_date_severity.py run`, h = 1 to 5, as
`docs/pivot/setup-diagnostic-result.md` lists. Five blocks: the training history at each episode, the target by year
and regime with the administered-rate changes, how the episodes move with the onset rule and the threshold, the
panel around each episode, and the benchmarks' tier-1 recall by year.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model import setup_diagnostic as sd  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "setup_diagnostic.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
HOLIDAYS = REPO / "metadata" / "market_holidays.json"
SNAPSHOTS = REPO / "tests" / "fixtures" / "snapshots"
ALFRED = {"reserve_balances": ("alfred-wresbal", "WRESBAL"), "tga": ("alfred-wtregen", "WTREGEN"), "iorb": ("alfred-ioer", "IOER")}


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed_declaration(path: Path) -> dict:
    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any figure is computed")
    return json.loads(path.read_text(encoding="utf-8"))


def _iso(value):
    return value.isoformat() if isinstance(value, date) else value


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) and math.isinf(value):
        return "inf"
    return value


def load_forecasts(bench: str, risk: str, names, horizons):
    """{horizon: [Forecast]}: the benchmarks and the declared risk rows, on one set of days."""

    out, digests = {}, {}
    for h in horizons:
        found = {}
        for template in (bench, risk):
            document = json.loads(Path(template.format(h=h)).read_text())
            digests[f"{Path(template).name.format(h=h)}"] = document["panel_sha256"]
            for forecast in pj.forecasts_from_horizon_document(document):
                if forecast.name in names:
                    found[forecast.name] = forecast
        missing = [n for n in names if n not in found]
        if missing:
            raise SystemExit(f"h = {h}: no forecasts for {missing}")
        reference = found["calendar_climatology"]
        for name, forecast in found.items():
            if forecast.dates != reference.dates:
                raise SystemExit(f"{name} h = {h}: its days are not the benchmark's")
        out[h] = [found[n] for n in names]
    return out, digests


def alfred_series(directory: str, series: str):
    """{vintage date: {observation date: value}} for the tracked ALFRED vintages of a series."""

    out = {}
    for path in sorted((SNAPSHOTS / directory).glob(f"{series}_*.csv")):
        vintage = date.fromisoformat(path.stem.split("_", 1)[1])
        values = {}
        with path.open() as handle:
            for row in csv.DictReader(handle):
                cells = list(row.values())
                if cells[1] not in ("", "."):
                    values[date.fromisoformat(cells[0])] = float(cells[1])
        out[vintage] = values
    return out


def run_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    judge_script = _judge_script()
    judge_commit = judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    declaration = pj.load_declaration()
    last = date.fromisoformat(declared["scoring"]["last_day"])
    tau = float(declared["scoring"]["primary_threshold_bp"])
    calm = int(declared["scoring"]["primary_calm_days"])
    horizons = declaration.horizons
    names = declared["benchmarks_by_year"]["rows"]

    rows = [r for r in load_daily_panel(args.panel) if r.date <= last]
    sd.require_window([r.date for r in rows], last)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    days = [r.date for r in rows]
    position = {d: k for k, d in enumerate(days)}
    spread = [float(r.spread_bps) for r in rows]
    raw = [{k: v for k, v in r.values.items()} for r in rows]
    by_horizon, digests = load_forecasts(args.bench, args.risk, names, horizons)
    for h in horizons:
        sd.require_window(by_horizon[h][0].dates, last)
    flat = [f for h in horizons for f in by_horizon[h]]
    states = {h: judge_script._scarcity_states(h, declaration.last_day) for h in horizons}

    def grids_of(items):
        return {
            h: pj.build_grid(declaration, h, rows, next(f for f in items if f.horizon == h).dates, splits, scarcity_state=states[h])
            for h in horizons
        }

    chosen = pj.choose_cutoffs(declaration, grids_of(flat), flat, days)
    grids = grids_of(chosen)
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    common_set = set(common)
    grid1 = grids[horizons[0]]
    episode_days = [d for d, o in zip(grid1.dates, grid1.onset) if o and d in common_set]
    mine = sd.episodes(days, spread, common, tau=tau, calm=calm)
    if mine != episode_days:
        raise SystemExit("the episodes of setup_diagnostic.episodes are not the judge's onsets")
    step = declaration.cutoff_refit_every

    # ---- 1. training history -------------------------------------------------------------------------------
    history = []
    for t in episode_days:
        entry = {"episode": t, "year": t.year, "regime": splits.regime(t)}
        for h in (1, max(horizons)):
            grid = grids[h]
            block = sd.refit_block(grid.dates, t, step=step)
            first_day = grid.dates[block["first_index"]]
            end = days[position[first_day] - h - 1]
            seen = sd.training_counts(days, spread, last=end, tau=tau, calm=calm)
            window = [k for k, d in enumerate(grid.dates) if d <= end]
            seen["scored_days_in_cutoff_window"] = len(window)
            seen["onsets_in_cutoff_window"] = sum(grid.onset[k] for k in window)
            seen["refit_first_day"] = first_day
            entry[f"h{h}"] = seen
        k = grid1.dates.index(t)
        entry["cutoff_finite_h1"] = {
            f.name: math.isfinite(f.cutoffs[tau][k]) for f in chosen if f.horizon == 1
        }
        history.append(entry)

    # ---- 2. the target ---------------------------------------------------------------------------------------
    target_cfg = declared["target"]
    thresholds = target_cfg["thresholds_bp"]
    quantile_points = target_cfg["distribution_quantiles"]

    def target_block(selector):
        index = [k for k, d in enumerate(days) if selector(d)]
        values = [spread[k] for k in index]
        block = {"days": len(index)}
        if not index:
            return block
        block["spread_bp_quantiles"] = dict(zip(map(str, quantile_points), sd.quantiles(values, quantile_points)))
        block["spread_bp_mean"] = sum(values) / len(values)
        block["spread_bp_max"] = max(values)
        for t_bp in thresholds:
            flags = [exceeds_bp(v, t_bp) for v in values]
            block[f"pressure_days_{t_bp:g}"] = sum(flags)
            block[f"base_rate_{t_bp:g}"] = sum(flags) / len(flags)
        scored = set(common)
        block["onsets_5"] = sum(1 for d in mine if selector(d))
        block["scored_days"] = sum(1 for d in common if selector(d))
        return block

    years = sorted({d.year for d in days})
    target = {
        "by_year": {str(y): target_block(lambda d, y=y: d.year == y) for y in years},
        "by_regime": {r: target_block(lambda d, r=r: splits.regime(d) == r) for r in sorted({splits.regime(d) for d in days})},
    }
    iorb = [float(r.values["iorb"]) for r in rows]
    sofr = [float(r.values["sofr"]) for r in rows]
    changes = sd.iorb_changes(days, iorb, sofr)
    for c in changes:
        k = position[c["date"]]
        window_end = min(k + 15, len(days) - 1)
        c["pressure_days_in_next_15_panel_days"] = sum(1 for j in range(k, window_end + 1) if exceeds_bp(spread[j], tau))
        c["episodes_in_next_15_panel_days"] = sum(1 for e in mine if k <= position[e] <= window_end)
    target["iorb_changes"] = changes

    # ---- 3. episode definition sensitivity -------------------------------------------------------------------
    sens_cfg = declared["episode_sensitivity"]
    grid_of_rules = {}
    for t_bp in sens_cfg["thresholds_bp"]:
        for c in sens_cfg["calm_days"]:
            found = sd.episodes(days, spread, common, tau=t_bp, calm=c)
            grid_of_rules[f"tau{t_bp:g}_calm{c}"] = found
    primary = grid_of_rules[f"tau{tau:g}_calm{calm}"]
    sensitivity = {"counts": {}, "changes_against_primary": {}}
    for key, found in grid_of_rules.items():
        sensitivity["counts"][key] = {"episodes": len(found), "by_year": {str(y): sum(1 for d in found if d.year == y) for y in years}}
        if key != f"tau{tau:g}_calm{calm}":
            diff = sd.compare(primary, found)
            near = {}
            for d in diff["appear"]:
                gaps = [abs(position[d] - position[e]) for e in primary]
                near[d.isoformat()] = min(gaps)
            sensitivity["changes_against_primary"][key] = {
                "kept": len(diff["kept"]),
                "appear": diff["appear"],
                "disappear": diff["disappear"],
                "appear_distance_to_nearest_primary_episode_panel_days": near,
            }

    # ---- 4. data integrity around episodes -------------------------------------------------------------------
    integ_cfg = declared["data_integrity"]
    holidays = [date.fromisoformat(x["date"]) for x in json.loads(HOLIDAYS.read_text())["closed"]]
    vintages = {c: alfred_series(*ALFRED[c]) for c in ALFRED}
    integrity = []
    for t in mine:
        w = sd.window_integrity(
            days, raw, t, integ_cfg["window_panel_days"], holidays, integ_cfg["daily_columns"], integ_cfg["weekly_columns"]
        )
        start = date.fromisoformat(w["first"])
        revised = {}
        for column, series in vintages.items():
            order = sorted(series)
            if not order:
                continue
            latest = series[order[-1]]
            observed = sorted(o for o in latest if start.toordinal() - 14 <= o.toordinal() <= t.toordinal())
            first_values = {}
            for o in observed:
                for v in order:
                    if o in series[v]:
                        first_values[o] = series[v][o]
                        break
            revised[column] = {"observations": len(observed), "differing": sd.revisions(observed, first_values, latest)}
        w["episode"] = t
        w["revisions_against_earliest_tracked_vintage"] = revised
        integrity.append(w)

    # ---- 5. benchmarks by year -------------------------------------------------------------------------------
    caught = {name: {d: 0 for d in mine} for name in names}
    for name in names:
        for h in horizons:
            forecast = next(f for f in chosen if f.name == name and f.horizon == h)
            for flag_day, p, c in zip(forecast.dates, forecast.probabilities[tau], forecast.cutoffs[tau]):
                if flag_day in caught[name] and p >= c:
                    caught[name][flag_day] = 1
    by_year = {}
    for name in names:
        per_year = defaultdict(lambda: [0, 0])
        for d in mine:
            per_year[d.year][1] += 1
            per_year[d.year][0] += caught[name][d]
        by_year[name] = {str(y): {"warned": v[0], "episodes": v[1]} for y, v in sorted(per_year.items())}
        by_year[name]["all"] = {"warned": sum(caught[name].values()), "episodes": len(mine)}
    per_episode = {d.isoformat(): {n: caught[n][d] for n in names} for d in mine}

    document = {
        "declaration": {"path": "metadata/setup_diagnostic.json"},
        "judge_declaration_commit": judge_commit,
        "judge_declaration_sha256": declaration.sha256,
        "scored_window": {"first": common[0], "last": common[-1], "days": len(common)},
        "episodes": mine,
        "training_history": history,
        "target": target,
        "episode_sensitivity": sensitivity,
        "data_integrity": integrity,
        "benchmarks_by_year": by_year,
        "warned_per_episode": per_episode,
        "forecast_panels": digests,
    }
    args.output.write_text(json.dumps(_jsonable(document), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "episodes": len(mine)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--bench", required=True)
    run.add_argument("--risk", required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(run=run_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
