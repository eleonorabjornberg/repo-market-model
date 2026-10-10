"""The published distribution against its direct-pairs twin (#450).

Declared before any score in `metadata/direct_pairs_twin.json`. Scored days are 2018-06-29 to 2025-12-31 only: the panel is cut
at 2025-12-31 before any fit (`docs/decisions/lockbox.md`). Writes nothing into `docs/runs/` and changes no published figure.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for W in persistence published twin; do
        OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/direct_pairs_twin.py walk --panel PUB.csv --which $W --output OUT/walk_$W.json
    done
    PYTHONPATH=src python3 scripts/direct_pairs_twin.py score --panel PUB.csv OUT/walk_persistence.json OUT/walk_published.json OUT/walk_twin.json --output OUT/score.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import crps_from_quantiles, stationary_bootstrap_interval  # noqa: E402

DECLARATION = REPO / "metadata" / "direct_pairs_twin.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
DAILY_RECORD = REPO / "docs" / "runs" / "published_distribution_daily_h1.json"
END = date(2025, 12, 31)
LAGS = tuple(range(-3, 6))
BLOCK, REPLICATIONS, LEVEL = 2, 2000, 0.90
MINIMUM_MOVE_BP = 2.0
WALKS = ("persistence", "published", "twin")


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def declaration_commit() -> str:
    """The commit that last changed the declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(DECLARATION.relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True,
                           text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return subprocess.run(["git", "log", "-1", "--format=%H", "--", relative], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip()


def twin_side(live_record):
    """The published side of `live_record._compare_sides(1)` with `--training-pairs-b direct`, nothing else changed."""

    from repo_model.cli import build_parser
    from repo_model.cli_eval import FITTER_FACTORIES, _online_calibration, _select_fitter, _side

    argv = list(live_record.final_test.CRPS_COMMAND)
    argv[argv.index("--splits") + 1] = str(live_record.SPLITS)
    argv[argv.index("--registry") + 1] = str(live_record.REGISTRY)
    at = argv.index("--calibration-b")
    argv[at:at] = ["--training-pairs-b", "direct"]
    args = build_parser().parse_args(argv)
    projected, online = _online_calibration(
        _side(args, "b"), FITTER_FACTORIES.get(args.model_b),
        splits=args.splits, refit_every=args.refit_every, side="-b",
    )
    name, fit = _select_fitter(projected, side="-b")
    return name, fit, tuple(args.feature_b), online, args


def walk_command(args) -> int:
    declaration_commit()
    fto = _script("final_test_opening")
    live_record = fto._script("live_record")
    fto.live_record = live_record
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    rows = [row for row in rows if row.date <= END]
    require_unlocked([row.date for row in rows], where="direct-pairs twin")
    registry = json.loads(live_record.REGISTRY.read_text(encoding="utf-8"))
    if args.which == "twin":
        name, fit, features, online, parsed = twin_side(live_record)
    else:
        sides, parsed = live_record._compare_sides(1)
        name, fit, features, online = sides[args.which]
    walk, levels, settings = fto.distribution_walk(
        rows, fit=fit, features=features, online_calibration=online, registry=registry, horizon=1,
        minimum_history=parsed.minimum_history, refit_every=parsed.refit_every,
    )
    if args.which == "twin" and settings.get("training_pairs") != "direct":
        raise SystemExit(f"the twin did not train on direct pairs: {settings}")
    if args.which == "published" and "training_pairs" in settings:
        raise SystemExit(f"the published side names training_pairs: {settings}")
    days = [{"date": rows[i].date.isoformat(), "quantiles_bps": list(q), "actual_bps": rows[i].spread_bps}
            for i, q in walk]
    document = {
        "which": args.which, "model": name, "features": list(features), "levels": list(levels),
        "settings": settings, "panel_sha256": hashlib.sha256(args.panel.read_bytes()).hexdigest(),
        "first": days[0]["date"], "last": days[-1]["date"], "days": days,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=dict) + "\n", encoding="utf-8")
    print(json.dumps({"which": args.which, "days": len(days), "first": document["first"], "last": document["last"]}))
    return 0


def _interval(statistic, n, seed):
    return list(stationary_bootstrap_interval(statistic, n, block_length=BLOCK, seed=seed,
                                              replications=REPLICATIONS, level=LEVEL))


def _mean_ci(values, seed):
    n = len(values)
    mean = sum(values) / n if n else None
    if n < 2 or not any(v != values[0] for v in values):
        return {"days": n, "mean": mean, "interval": [mean, mean] if n else None}
    return {"days": n, "mean": mean,
            "interval": _interval(lambda idx, v=values: sum(v[i] for i in idx) / len(idx), n, seed)}


def verdict(cell) -> str:
    low, high = cell["interval"]
    return "twin better" if low > 0 else "twin worse" if high < 0 else "no difference"


def turning_points(series, minimum_move):
    flags = [None] * len(series)
    for t in range(1, len(series) - 1):
        into, out_of = series[t] - series[t - 1], series[t + 1] - series[t]
        flags[t] = abs(into) >= minimum_move and abs(out_of) >= minimum_move and into * out_of < 0
    return flags


def _corr(m, a):
    n = len(m)
    mm, ma = sum(m) / n, sum(a) / n
    vm, va = sum((x - mm) ** 2 for x in m), sum((y - ma) ** 2 for y in a)
    if vm <= 0 or va <= 0:
        return None
    return sum((x - mm) * (y - ma) for x, y in zip(m, a)) / math.sqrt(vm * va)


def _best(table):
    return -max((c, -k) for k, c in table.items() if c is not None)[1]


def cut_series(rows):
    """The spreads the score may read: every panel day to `END`, none after it (`docs/decisions/lockbox.md`)."""

    return [row.spread_bps for row in rows if row.date <= END]


def lag_members(positions, series):
    """The members whose lag at the largest negative `k` is still inside the cut series (the last days of 2025 have no
    spread three days on, and 2026 is not read to supply one)."""

    return [i for i, p in enumerate(positions) if p + max(-min(LAGS), 0) < len(series)]


def _lag_table(medians, series, positions):
    return {k: _corr(medians, [series[p - k] for p in positions]) for k in LAGS}


def score_command(args) -> int:
    commit = declaration_commit()
    require_unlocked([END], where="direct-pairs twin")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    by_date = {r.date: r for r in rows}
    position = {r.date: i for i, r in enumerate(rows)}
    splits = load_split_declaration(SPLITS)
    walks, digest = {}, None
    for path in args.inputs:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        walks[document["which"]] = document
        digest = digest or document["panel_sha256"]
        if document["panel_sha256"] != digest:
            raise SystemExit("the walks were run on different panels")
    if set(walks) != set(WALKS):
        raise SystemExit(f"score needs the walks {list(WALKS)}")
    published = {d["date"]: d for d in json.loads(DAILY_RECORD.read_text(encoding="utf-8"))["days"]
                 if d["date"] <= END.isoformat()}
    days = sorted(published)
    by_walk = {}
    for which, document in walks.items():
        have = {d["date"]: d for d in document["days"]}
        if sorted(have) != days:
            raise SystemExit(f"the {which} walk is not on the published record's scored days")
        by_walk[which] = have
    differing = [d for d in days if by_walk["published"][d]["quantiles_bps"] != published[d]["quantiles_bps"]]
    if differing:
        raise SystemExit(f"the published walk differs from the published record on {len(differing)} days")
    levels = tuple(walks["published"]["levels"])
    actual = [by_date[date.fromisoformat(d)].spread_bps for d in days]
    series = cut_series(rows)
    pos = [position[date.fromisoformat(d)] for d in days]
    losses = {w: [crps_from_quantiles(levels, by_walk[w][d]["quantiles_bps"], a) for d, a in zip(days, actual)]
              for w in WALKS}
    median_at = levels.index(0.5)
    median = {w: [by_walk[w][d]["quantiles_bps"][median_at] for d in days] for w in WALKS}
    abs_error = {w: [abs(m - a) for m, a in zip(median[w], actual)] for w in WALKS}
    # Cells: all days, regime, pressure-day type, +5 bp outcome, turning-point days.
    groups = {"regime": [], "day_type": [], "outcome": []}
    for d in days:
        when = date.fromisoformat(d)
        row = by_date[when]
        groups["regime"].append(splits.regime(when))
        groups["day_type"].append(splits.reporting_day_type(when, row.values))
        groups["outcome"].append("pressure day (> +5 bp)" if exceeds_bp(row.spread_bps, 5) else "other days")
    cells = {"all": list(range(len(days)))}
    for dimension, labels in groups.items():
        for label in sorted(set(labels)):
            cells[f"{dimension}: {label}"] = [i for i, g in enumerate(labels) if g == label]
    flags = turning_points(series, MINIMUM_MOVE_BP)
    turning = [flags[p] for p in pos]
    cells["turning-point days"] = [i for i, t in enumerate(turning) if t is True]
    seed = 450

    def gain(a, b, members):
        return [losses[a][i] - losses[b][i] for i in members]

    crps = {}
    for label, members in cells.items():
        entry = {"days": len(members),
                 "mean_crps": {w: (sum(losses[w][i] for i in members) / len(members) if members else None)
                               for w in WALKS}}
        if members:
            entry["twin_gain_over_published"] = _mean_ci(gain("published", "twin", members), seed)
            entry["twin_gain_over_published"]["verdict"] = verdict(entry["twin_gain_over_published"])
            entry["published_gain_over_persistence"] = _mean_ci(gain("persistence", "published", members), seed)
            entry["twin_gain_over_persistence"] = _mean_ci(gain("persistence", "twin", members), seed)
        crps[label] = entry
    # The lag.
    lag = {}
    for label, members in cells.items():
        if len(members) < 30:
            continue
        members = [members[j] for j in lag_members([pos[i] for i in members], series)]
        member_pos = [pos[i] for i in members]
        tables = {w: _lag_table([median[w][i] for i in members], series, member_pos) for w in WALKS}
        if len(members) < 30:
            continue
        entry = {"days": len(members),
                 "correlation_by_lag": {w: {str(k): c for k, c in t.items()} for w, t in tables.items()},
                 "best_lag": {w: _best(t) for w, t in tables.items()}}
        if label in ("all",) or label.startswith("regime"):
            n = len(members)

            def tab(w, idx, member_pos=member_pos, members=members):
                return _lag_table([median[w][members[i]] for i in idx], series, [member_pos[i] for i in idx])

            entry["twin_minus_published"] = {
                "best_lag_difference": entry["best_lag"]["twin"] - entry["best_lag"]["published"],
                "best_lag_difference_interval": _interval(
                    lambda idx: float(_best(tab("twin", idx)) - _best(tab("published", idx))), n, seed),
                **{f"correlation_difference_at_lag_{k}": {
                    "mean": tables["twin"][k] - tables["published"][k],
                    "interval": _interval(
                        lambda idx, k=k: tab("twin", idx)[k] - tab("published", idx)[k], n, seed)}
                   for k in (0, 1, 2)},
            }
        lag[label] = entry
    # Turning-point days: the median's absolute error.
    members = cells["turning-point days"]
    turning_error = {
        "days": len(members),
        "mean_abs_error": {w: sum(abs_error[w][i] for i in members) / len(members) for w in WALKS},
        "twin_closer_than_published": _mean_ci([abs_error["published"][i] - abs_error["twin"][i] for i in members], seed),
    }
    all_members = cells["all"]
    mae = {"all": {w: sum(abs_error[w]) / len(abs_error[w]) for w in WALKS},
           "twin_closer_than_published_all": _mean_ci(
               [abs_error["published"][i] - abs_error["twin"][i] for i in all_members], seed)}
    # Calibration: coverage of the 50% and 90% bands, by regime.
    lo50, hi50, lo90, hi90 = (levels.index(x) for x in (0.25, 0.75, 0.05, 0.95))
    coverage = {}
    for label, members in cells.items():
        if label != "all" and not label.startswith("regime"):
            continue
        entry = {"days": len(members)}
        for w in WALKS:
            q = [by_walk[w][days[i]]["quantiles_bps"] for i in members]
            a = [actual[i] for i in members]
            entry[w] = {
                "50%": sum(x[lo50] <= v <= x[hi50] for x, v in zip(q, a)) / len(a),
                "90%": sum(x[lo90] <= v <= x[hi90] for x, v in zip(q, a)) / len(a),
            }
        coverage[label] = entry
    out = {
        "directive": "#450", "declaration": str(DECLARATION.relative_to(REPO)), "declaration_commit": commit,
        "panel_sha256": digest, "first": days[0], "last": days[-1], "days": len(days),
        "published_walk_reproduces_the_record": {"days": len(days), "differing": 0},
        "twin_settings": walks["twin"]["settings"], "published_settings": walks["published"]["settings"],
        "interval": {"method": "stationary_bootstrap", "block_length": BLOCK, "replications": REPLICATIONS,
                     "level": LEVEL, "seed": seed},
        "sign": "gain = CRPS(first) - CRPS(second) per day; positive favours the second",
        "primary": crps["all"]["twin_gain_over_published"],
        "crps": crps, "lag": lag, "median_error": mae, "turning_point_error": turning_error, "coverage": coverage,
    }
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"primary": out["primary"], "best_lag": lag["all"]["best_lag"]}, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    walk = commands.add_parser("walk")
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--which", choices=WALKS, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(handler=walk_command)
    score = commands.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("inputs", nargs=3, type=Path)
    score.set_defaults(handler=score_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
