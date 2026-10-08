"""Why the published exceedance curve flattens across thresholds (#373).

Descriptive: it changes no model, no published record and nothing the live
record logs. Two subcommands.

* `walk`: the published pressure model v1 (`scripts/pressure_model_v1.py`,
  `publish`) walked at one horizon, every scored day kept with, at each
  threshold, the probability before the out-of-fold Platt step (`raw`, the
  distribution's exceedance after conformal PID), the probability after it
  (`final`, the published figure), the climatology reference and the outcome.
  Only days before 2026-01-01 are scored (`docs/decisions/lockbox.md`).

      OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/exceedance_flattening_diagnosis.py walk \\
          --panel PUB.csv --horizon H --output OUT/walk_hH.json

* `assemble`: the diagnosis record from the walks (added below).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _script(name):
    spec = importlib.util.spec_from_file_location(f"flat_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def walk_command(args) -> int:
    from repo_model import ml, pressure
    from repo_model.baseline import (
        panel_sha256,
        persistence_logistic_exceedance,
        rolling_exceedance_backtest,
    )
    from repo_model.data import audit_panel, load_daily_panel, load_stress_thresholds
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.recalibration import NestedFoldPid

    v1 = _script("pressure_model_v1")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(v1.SPLITS)
    taus = tuple(float(t) for t in load_stress_thresholds(v1.THRESHOLDS)["taus_bp"])
    h = args.horizon
    features = v1._at_horizon(v1.GBM_FEATURES, h)
    built = []
    knots = {}

    def online(rows_, rule):
        pid = NestedFoldPid(rows_, rule, splits=splits, refit_every=v1.REFIT_EVERY)
        issue = pid.law

        def law(index, *rest, **named):
            values, levels = issue(index, *rest, **named)
            knots[index] = [float(v) for v in values]
            return values, levels

        pid.law = law  # keeps the knots `curve` reads each day's probabilities off
        built.append(pid)
        return pid

    raw = rolling_exceedance_backtest(
        rows,
        predictor=ml.gbm_exceedance(
            tuple(name for name in features if name != "spread_bps"),
            minimum_history=v1.MINIMUM_HISTORY,
        ),
        model_name=v1.PUBLISHED,
        features=features,
        registry=json.loads(v1.REGISTRY.read_text()),
        decision_time=v1.DECISION,
        taus=taus,
        minimum_history=v1.MINIMUM_HISTORY,
        refit_every=v1.REFIT_EVERY,
        end=v1.END,
        horizon=h,
        online_calibration=online,
    )
    final = pressure.recalibrated(raw)
    persistence = rolling_exceedance_backtest(
        rows,
        predictor=persistence_logistic_exceedance(minimum_history=v1.MINIMUM_HISTORY),
        model_name="persistence_logistic",
        features=("spread_bps",),
        registry=json.loads(v1.REGISTRY.read_text()),
        decision_time=v1.DECISION,
        taus=taus,
        minimum_history=v1.MINIMUM_HISTORY,
        refit_every=v1.REFIT_EVERY,
        end=v1.END,
        horizon=h,
    )
    if persistence.scored_dates != raw.scored_dates:
        raise ValueError("the benchmark and the model were scored on different days")
    order = sorted(knots)
    if len(order) != len(raw.scored_dates):
        raise ValueError(f"{len(order)} laws were issued for {len(raw.scored_dates)} scored days")
    days = [
        {
            "date": when.isoformat(),
            "realized_bps": raw.realized_bps[i],
            "outcomes": list(raw.outcomes[i]),
            "raw": list(raw.forecast[i]),
            "final": list(final.forecast[i]),
            "reference": list(raw.reference[i]),
            "persistence_logistic": list(persistence.forecast[i]),
            "train_end": raw.folds[i].train_end.isoformat(),
            "knots_bps": knots[order[i]],
        }
        for i, when in enumerate(raw.scored_dates)
    ]
    document = {
        "directive": "#373",
        "horizon": h,
        "taus_bp": list(taus),
        "panel_sha256": panel_sha256(args.panel),
        "end": v1.END.isoformat(),
        "recalibration": dict(pressure.RECALIBRATION),
        "days": days,
    }
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "days": len(days), "output": str(args.output)}))
    return 0


# -- assembly -----------------------------------------------------------------

#: The days compared: before the near-blind tier (`docs/decisions/lockbox.md`).
LAST_DAY = "2025-12-31"
BIN_EDGES = (0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0000001)
REPLICATIONS = 2000
SEED = 373
LEVEL = 0.90
#: Bootstrap intervals for the splits are drawn at this horizon only; the other
#: horizons report counts and means.
INTERVAL_HORIZON = 1
#: A top segment wider than this (bp) is one the law reads a historic spike into.
WIDE_SEGMENT_BP = 100.0
TOLERANCE = 1e-12


def _mean(values):
    values = list(values)
    return sum(values) / len(values) if values else None


def _auc(scores, labels):
    """Mann-Whitney area under the ROC curve; ties count one half."""

    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return None
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    rank_sum = 0.0
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        mid = (i + j) / 2.0 + 1.0
        rank_sum += mid * sum(labels[order[k]] for k in range(i, j + 1))
        i = j + 1
    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def _interval(statistic, n, block_length):
    from repo_model.metrics import stationary_bootstrap_interval

    lower, upper = stationary_bootstrap_interval(
        statistic, n, block_length=block_length, seed=SEED, replications=REPLICATIONS, level=LEVEL
    )
    return {"lower": lower, "upper": upper, "level": LEVEL, "method": "stationary_bootstrap",
            "block_length": block_length, "replications": REPLICATIONS, "seed": SEED}


def _group_rows(days, labels, order, k, with_interval, block_length):
    """Predicted against realised exceedance rate, per group, at threshold index `k`."""

    out = {}
    for group in order:
        members = [i for i, label in enumerate(labels) if label == group]
        entry = {"days": len(members)}
        if members:
            outcomes = [days[i]["outcomes"][k] for i in members]
            brier = {
                name: _mean((days[i][name][k] - days[i]["outcomes"][k]) ** 2 for i in members)
                for name in ("raw", "final", "reference", "persistence_logistic")
            }
            entry.update(
                events=sum(outcomes),
                realised_rate=_mean(outcomes),
                mean_raw=_mean(days[i]["raw"][k] for i in members),
                mean_final=_mean(days[i]["final"][k] for i in members),
                mean_climatology=_mean(days[i]["reference"][k] for i in members),
                brier=brier,
                brier_skill_vs_climatology=_skill(brier["final"], brier["reference"]),
            )
            if with_interval and len(members) >= 2:
                difference = [
                    (days[i]["reference"][k] - days[i]["outcomes"][k]) ** 2
                    - (days[i]["final"][k] - days[i]["outcomes"][k]) ** 2
                    for i in range(len(days))
                ]
                member = [label == group for label in labels]

                def statistic(indices, member=member, difference=difference):
                    drawn = [difference[i] for i in indices if member[i]]
                    return sum(drawn) / len(drawn) if drawn else float("nan")

                try:
                    entry["climatology_minus_final_brier"] = {
                        "mean": _mean(difference[i] for i in members),
                        "interval": _interval(statistic, len(days), block_length),
                    }
                except Exception as error:  # an interval needs both a draw and a day in the group
                    entry["climatology_minus_final_brier"] = {
                        "mean": _mean(difference[i] for i in members),
                        "interval_unavailable": str(error),
                    }
        out[group] = entry
    return out


def _skill(model, reference):
    return None if not reference else 1.0 - model / reference


def _reliability_bins(days, k, name):
    out = []
    for low, high in zip(BIN_EDGES, BIN_EDGES[1:]):
        members = [d for d in days if low <= d[name][k] < high]
        out.append(
            {
                "from": low,
                "to": min(high, 1.0),
                "days": len(members),
                "events": sum(d["outcomes"][k] for d in members),
                "mean_forecast": _mean(d[name][k] for d in members),
                "realised_rate": _mean(d["outcomes"][k] for d in members),
            }
        )
    return out


def _quantiles(values, cuts=10):
    import statistics

    return [round(v, 4) for v in statistics.quantiles(values, n=cuts)]


def assemble_command(args) -> int:
    from repo_model.baseline import _logistic_fit, _sigmoid
    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.pressure import RECALIBRATION, _logit

    v1 = _script("pressure_model_v1")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    by_date = {row.date.isoformat(): row for row in rows}
    splits = load_split_declaration(v1.SPLITS)
    regime_order = [name for name, _, _ in splits.regimes]
    day_types = ["ordinary", "month_end", "tax_date", "quarter_end"]
    spreads = {row.date.isoformat(): row.spread_bps for row in rows if row.spread_bps is not None}
    peak_day = max((day for day in spreads if day <= LAST_DAY), key=lambda day: spreads[day], default=None)

    record = {
        "directive": "#373",
        "decides": "nothing",
        "record": (
            "why the published pressure model's exceedance curve flattens across thresholds; "
            "descriptive, on days before 2026-01-01"
        ),
        "thresholds_bp": None,
        "last_day": LAST_DAY,
        "peak_spread": {"date": peak_day, "bps": spreads.get(peak_day)},
        "horizons": {},
    }
    for path in sorted(args.walks):
        walk = json.loads(Path(path).read_text())
        h = walk["horizon"]
        days = walk["days"]
        taus = walk["taus_bp"]
        record["thresholds_bp"] = taus
        record["panel_sha256"] = walk["panel_sha256"]
        if days[-1]["date"] > LAST_DAY:
            raise ValueError(f"a walk scores {days[-1]['date']}, after {LAST_DAY}; that tier is locked")
        n = len(days)
        block_length = h + 1
        regimes = [splits.regime(date.fromisoformat(d["date"])) for d in days]
        types = [splits.day_type(by_date[d["date"]].values) for d in days]

        # reproduction: the walk's published figures are the published record's own
        published = json.loads((REPO / "docs" / "runs" / f"pressure_model_v1_h{h}.json").read_text())
        reproduction = {}
        for k, tau in enumerate(taus):
            entry = published["metrics"]["by_tau"][f"{tau:g}"]
            if "brier" not in entry:
                continue
            mine = _mean((d["final"][k] - d["outcomes"][k]) ** 2 for d in days)
            if abs(mine - entry["brier"]) > TOLERANCE:
                raise ValueError(
                    f"h = {h}, +{tau:g} bp: the walk's Brier {mine!r} is not the published {entry['brier']!r}"
                )
            reproduction[f"{tau:g}"] = {"walk": mine, "published": entry["brier"]}

        section = {"days": n, "first": days[0]["date"], "last": days[-1]["date"],
                   "reproduces_published_record": reproduction}

        # 1. predicted and realised exceedance rate by threshold
        by_tau = {}
        for k, tau in enumerate(taus):
            outcomes = [d["outcomes"][k] for d in days]
            by_tau[f"{tau:g}"] = {
                "events": sum(outcomes),
                "realised_rate": _mean(outcomes),
                "mean_raw": _mean(d["raw"][k] for d in days),
                "mean_final": _mean(d["final"][k] for d in days),
                "mean_climatology": _mean(d["reference"][k] for d in days),
                "mean_persistence_logistic": _mean(d["persistence_logistic"][k] for d in days),
            }
        base = by_tau[f"{taus[0]:g}"]
        for key, entry in by_tau.items():
            entry["ratio_to_lowest_threshold"] = {
                name: (entry[name] / base[name] if base[name] else None)
                for name in ("realised_rate", "mean_raw", "mean_final", "mean_climatology")
            }
        section["by_threshold"] = by_tau

        # 2. reliability by threshold, regime and pressure-day type
        section["reliability"] = {}
        for k, tau in enumerate(taus):
            with_interval = h == INTERVAL_HORIZON
            section["reliability"][f"{tau:g}"] = {
                "pooled": _group_rows(days, ["all"] * n, ["all"], k, with_interval, block_length)["all"],
                "bins_final": _reliability_bins(days, k, "final"),
                "bins_raw": _reliability_bins(days, k, "raw"),
                "by_regime": _group_rows(days, regimes, regime_order, k, with_interval, block_length),
                "by_day_type": _group_rows(days, types, day_types, k, with_interval, block_length),
            }

        # 3. how the flattening arises
        mechanism = {}
        # 3a. the law: the top segment [Q(0.95), top knot] carries the whole upper 5% at constant density
        top = [d["knots_bps"][-1] for d in days]
        q95 = [d["knots_bps"][-2] for d in days]
        width = [t - q for t, q in zip(top, q95)]
        wide = [i for i, w in enumerate(width) if w > WIDE_SEGMENT_BP]
        first_wide = days[wide[0]]["date"] if wide else None
        in_segment = {}
        for k, tau in enumerate(taus):
            inside = [i for i in range(n) if q95[i] <= tau < top[i]]
            in_segment[f"{tau:g}"] = {
                "days_tau_in_top_segment": len(inside),
                "share": len(inside) / n,
                "mean_raw_on_those_days": _mean(days[i]["raw"][k] for i in inside),
                "realised_rate_on_those_days": _mean(days[i]["outcomes"][k] for i in inside),
            }
        ratio = [
            d["raw"][taus.index(50.0)] / d["raw"][taus.index(10.0)]
            for d in days
            if d["raw"][taus.index(10.0)] > 0 and d["knots_bps"][-2] < 10.0 <= d["knots_bps"][-1]
        ]
        mechanism["law"] = {
            "top_knot_bps_deciles": _quantiles(top),
            "top_segment_width_bps_deciles": _quantiles(width),
            "days_with_top_segment_wider_than_100bp": len(wide),
            "first_such_scored_day": first_wide,
            "uniform_density_per_bp_if_wide": 0.05 / _mean(w for w in width if w > WIDE_SEGMENT_BP)
            if wide else None,
            "tau_in_top_segment": in_segment,
            "median_raw_ratio_p50_to_p10_when_both_in_top_segment": sorted(ratio)[len(ratio) // 2] if ratio else None,
            "realised_ratio_p50_to_p10": by_tau["50"]["realised_rate"] / by_tau["10"]["realised_rate"]
            if by_tau["10"]["realised_rate"] else None,
        }

        # 3b. the recalibration step
        k_all = range(len(taus))
        blocks = {}
        for k, tau in enumerate(taus):
            identity = sum(1 for d in days if abs(d["final"][k] - d["raw"][k]) < TOLERANCE)
            tie_next = (
                sum(1 for d in days if d["final"][k] == d["final"][k + 1]) if k + 1 < len(taus) else None
            )
            snapshots = []
            seen = []
            for index, d in enumerate(days):
                if not seen or seen[-1] != d["train_end"]:
                    seen.append(d["train_end"])
                    past = [j for j in range(index) if days[j]["date"] <= d["train_end"]]
                    events = sum(days[j]["outcomes"][k] for j in past)
                    if (len(past) >= RECALIBRATION["minimum_pairs"]
                            and RECALIBRATION["minimum_events"] <= events < len(past)):
                        b0, b1 = _logistic_fit([_logit(days[j]["raw"][k]) for j in past],
                                               [days[j]["outcomes"][k] for j in past])
                        snapshots.append({"first_scored": d["date"], "pairs": len(past), "events": events,
                                          "intercept": b0, "slope": b1,
                                          "p_when_raw_is_floor": _sigmoid(b0 + b1 * _logit(0.0))})
            blocks[f"{tau:g}"] = {
                "days_recalibration_is_identity": identity,
                "days_final_equals_next_threshold": tie_next,
                "first_block_fitted": snapshots[0] if snapshots else None,
                "last_block_fitted": snapshots[-1] if snapshots else None,
                "fitted_blocks": len(snapshots),
            }
        mechanism["recalibration"] = blocks

        # 3c/3d. what the model can rank, per threshold: the features and the targets
        discrimination = {}
        for k, tau in enumerate(taus):
            outcomes = [d["outcomes"][k] for d in days]
            discrimination[f"{tau:g}"] = {
                "auc_raw": _auc([d["raw"][k] for d in days], outcomes),
                "auc_final": _auc([d["final"][k] for d in days], outcomes),
                "auc_climatology": _auc([d["reference"][k] for d in days], outcomes),
                "auc_persistence_logistic": _auc([d["persistence_logistic"][k] for d in days], outcomes),
                "auc_of_lowest_threshold_raw": _auc([d["raw"][0] for d in days], outcomes),
                "events": sum(outcomes),
            }
        mechanism["discrimination"] = discrimination
        share_beyond = {
            f"{tau:g}": sum(1 for q in q95 if q <= tau) / n for tau in taus
        }
        mechanism["targets"] = {
            "quantile_levels_fitted": [0.05, 0.25, 0.5, 0.75, 0.95],
            "share_of_days_whose_q95_is_at_or_below_tau": share_beyond,
            "events_by_threshold": {f"{tau:g}": sum(d["outcomes"][k] for d in days) for k, tau in enumerate(taus)},
            "fraction_positive_by_threshold": {
                f"{tau:g}": by_tau[f"{tau:g}"]["realised_rate"] for tau in taus
            },
        }
        events_over_time = {}
        for k, tau in enumerate(taus):
            running = 0
            first_five = None
            for d in days:
                running += d["outcomes"][k]
                if running >= RECALIBRATION["minimum_events"] and first_five is None:
                    first_five = d["date"]
            events_over_time[f"{tau:g}"] = first_five
        mechanism["class_imbalance"] = {
            "first_scored_day_with_minimum_events_so_far": events_over_time,
            "minimum_events_for_recalibration": RECALIBRATION["minimum_events"],
            "minimum_pairs_for_recalibration": RECALIBRATION["minimum_pairs"],
        }
        section["mechanism"] = mechanism
        record["horizons"][str(h)] = section
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizons": sorted(record["horizons"]), "output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk", help="walk the published model at one horizon")
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--horizon", type=int, required=True)
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(func=walk_command)
    assemble = sub.add_parser("assemble", help="the diagnosis record from the walks")
    assemble.add_argument("--panel", type=Path, required=True)
    assemble.add_argument("--walks", type=Path, nargs="+", required=True)
    assemble.add_argument("--output", type=Path, required=True)
    assemble.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
