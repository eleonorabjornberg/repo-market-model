"""Sensitivity of the pressure-day judge's results to its setup (#482): a reported-only measurement.

Four readings, for the five tier-1 rows of `metadata/setup_sensitivity.json` and the two benchmarks, beside the declared
reading of `metadata/pressure_judge.json`, which is not changed:

* 2018-19 dominance: the flag cut-off chosen with 2018-19 days down-weighted to their share of all days; tier 1 and
  tier 3 by calendar year; how 2024 compares with 2018-19.
* Refit cadence: the flag cut-off refitted every 5 and every 10 scored days instead of 21; the onsets whose warning changes.
* The week-ahead combiner: tier 5 under the maximum (declared) and under independence.
* Tier 3 coverage: the calibration table in every regime, with the alarm rate per year in the abundant stretches.

    PYTHONPATH=src python3 scripts/setup_sensitivity.py run --panel PUB.csv --bench 'OUT/bench_h{h}.json' \\
        --row two_part_gbm='OUT/tp_h{h}.json' ... --output OUT/setup_sensitivity.json --markdown OUT/setup_sensitivity.md

It writes nothing into `docs/runs/` and refuses an uncommitted declaration (`metadata/setup_sensitivity.json`, the judge's).
Scored days are before 2026-01-01 (`docs/decisions/lockbox.md`); no day of the 2026 window is read.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import subprocess
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model import setup_sensitivity as ss  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "setup_sensitivity.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
PERIOD_COLUMNS = (
    "reserve_balances", "tga", "sofr_volume", "dealer_treasury_position", "treasury_settlement", "tbill_13w",
)


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed(path: Path) -> dict:
    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def load_forecasts(bench: str, templates: dict, horizons):
    out, digests = {}, {}
    for h in horizons:
        bench_doc = json.loads(Path(bench.format(h=h)).read_text())
        forecasts = pj.forecasts_from_horizon_document(bench_doc)
        digests[f"bench_h{h}"] = bench_doc["panel_sha256"]
        reference = next(f for f in forecasts if f.name == "calendar_climatology")
        for name, template in templates.items():
            document = json.loads(Path(template.format(h=h)).read_text())
            if int(document["horizon"]) != h or name not in document["forecasts"]:
                raise SystemExit(f"{template.format(h=h)} holds no {name!r} at h = {h}")
            mine = next(f for f in pj.forecasts_from_horizon_document(document) if f.name == name)
            if mine.dates != reference.dates:
                raise SystemExit(f"{name} h = {h}: its days are not the benchmark's")
            digests[f"{name}_h{h}"] = document["panel_sha256"]
            forecasts.append(mine)
        out[h] = forecasts
    return out, digests


def flags_of(forecast, tau):
    return [1 if p >= c else 0 for p, c in zip(forecast.probabilities[tau], forecast.cutoffs[tau])]


def tier_readings(declaration, forecasts, grids, years):
    """Tier 1 and tier 3 point readings of each forecast, overall and by calendar year of the flagged day."""

    tau, horizons = declaration.primary, declaration.horizons
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    keep = {h: [k for k, d in enumerate(grids[h].dates) if d in set(common)] for h in horizons}
    first = horizons[0]
    onset = [grids[first].onset[k] for k in keep[first]]
    year = [str(common[i].year) for i in range(len(common))]
    out = {}
    for name in sorted({f.name for f in forecasts}):
        caught = [0] * len(common)
        alarms, flagged_all = {}, {}
        abundant_flags = {}
        for h in horizons:
            forecast = next(f for f in forecasts if f.name == name and f.horizon == h)
            flags = flags_of(forecast, tau)
            f_h = [flags[k] for k in keep[h]]
            pressure = [grids[h].outcomes[tau][k] for k in keep[h]]
            caught = [max(c, f) for c, f in zip(caught, f_h)]
            alarms[h] = [1 if f and not y else 0 for f, y in zip(f_h, pressure)]
            flagged_all[h] = f_h
            state = [str(grids[h].groups["scarcity_state"][k]) for k in keep[h]]
            abundant_flags[h] = [f if s == declaration.abundant_state else 0 for f, s in zip(f_h, state)]
        onsets = sum(onset)
        total_worst = max(sum(a) for a in alarms.values())
        by_year = ss.tier_one_by_group(year, onset, caught, alarms)
        rates = {h: ss.flag_rate_by_group(year, flagged_all[h], declaration.business_days_per_year) for h in horizons}
        abundant_days = {
            y: sum(1 for k, label in enumerate(year) if label == y and str(grids[first].groups["scarcity_state"][keep[first][k]]) == declaration.abundant_state)
            for y in sorted(set(year))
        }
        for y, cell in by_year.items():
            cell["flags_per_year_worst_horizon"] = max(rates[h][y]["flags_per_year"] for h in horizons)
            cell["abundant_state_days"] = abundant_days[y]
            cell["abundant_flags_per_year_worst_horizon"] = (
                max(
                    sum(abundant_flags[h][k] for k, label in enumerate(year) if label == y)
                    / abundant_days[y] * declaration.business_days_per_year
                    for h in horizons
                )
                if abundant_days[y] else None
            )
        out[name] = {
            "onsets": onsets,
            "onsets_flagged": sum(o * c for o, c in zip(onset, caught)),
            "worst_false_alarms_per_onset": total_worst / onsets if onsets else None,
            "by_year": by_year,
            "caught": caught,
            "onset": onset,
            "days": [d.isoformat() for d in common],
        }
    return out


def pooled_calibration(declaration, forecasts, grids, first, last):
    """Mean predicted, realised and their difference over the scored days: all, inside the period, outside it.

    Weighting the period to its share of all days leaves the pooled mean unchanged (the weights are 1), so the
    reading that can differ is the one outside the period.
    """

    tau = declaration.primary
    out = {}
    for f in forecasts:
        h = f.horizon
        p, y, dates = f.probabilities[tau], grids[h].outcomes[tau], grids[h].dates
        cell = {}
        for label, keep in (
            ("all_days", lambda d: True),
            ("inside_period", lambda d: first <= d <= last),
            ("outside_period", lambda d: not first <= d <= last),
        ):
            members = [k for k, d in enumerate(dates) if keep(d)]
            predicted = sum(p[k] for k in members) / len(members)
            realised = sum(y[k] for k in members) / len(members)
            cell[label] = {
                "days": len(members), "mean_predicted": predicted, "realised": realised,
                "realised_minus_predicted": realised - predicted,
            }
        out.setdefault(f.name, {})[str(h)] = cell
    return out


def period_profile(rows, grid, first, last, tau, common):
    """What a stretch of days looks like: spread, pressure days, episodes, and the panel's inputs.

    Onsets are counted on the days every horizon scores (`common`), as tier 1 counts them.
    """

    spread = {r.date: float(r.spread_bps) for r in rows}
    start = grid.dates[0]
    days = [r for r in rows if max(first, start) <= r.date <= min(last, grid.dates[-1])]
    pressure = [exceeds_bp(spread[r.date], tau) for r in days]
    episodes, run, lengths = 0, 0, []
    for flag in pressure:
        if flag:
            run += 1
        elif run:
            lengths.append(run)
            run = 0
    if run:
        lengths.append(run)
    scored = [(d, o, y, s) for d, o, y, s in zip(grid.dates, grid.onset, grid.outcomes[tau], grid.groups["scarcity_state"]) if first <= d <= last and d in common]
    values = [spread[r.date] for r in days]
    out = {
        "days": len(days),
        "scored_days": len(scored),
        "pressure_days": sum(1 for f in pressure if f),
        "pressure_share": sum(1 for f in pressure if f) / len(days) if days else None,
        "onsets": sum(o for _, o, _, _ in scored),
        "episodes": len(lengths),
        "episode_lengths": sorted(lengths, reverse=True),
        "spread_bp": {
            "median": statistics.median(values), "p90": sorted(values)[int(0.9 * (len(values) - 1))], "max": max(values),
            "mean": statistics.fmean(values),
        } if values else None,
        "scarcity_state_share": {
            label: sum(1 for *_, s in scored if str(s) == label) / len(scored) for label in sorted({str(s) for *_, s in scored})
        } if scored else None,
        "inputs_median": {},
    }
    for column in PERIOD_COLUMNS:
        series = [r.values.get(column) for r in days if r.values.get(column) is not None]
        out["inputs_median"][column] = statistics.median(series) if series else None
    return out


def concentration(tier_three, declaration):
    """Where tier 3's failures fall: the regimes whose calibration interval misses zero, the abundant stretches
    whose alarm rate is over the limit, counted over the five leads, for each row."""

    out = {}
    for name, row in tier_three.items():
        miss, over = {}, {}
        for h, cell in row["by_horizon"].items():
            for label, regime in cell["regimes"].items():
                interval = regime["realised_minus_predicted"].get("interval")
                if interval is not None and not interval["lower"] <= 0.0 <= interval["upper"]:
                    miss[label] = miss.get(label, 0) + 1
            for label, stretch in cell["abundant_stretches"].items():
                if stretch["flags_per_year"] is not None and stretch["flags_per_year"] > declaration.flags_per_year_at_most:
                    over[label] = over.get(label, 0) + 1
        out[name] = {"calibration_misses_zero_by_regime": miss, "alarm_rate_over_limit_by_stretch": over}
    return out


def command(args) -> int:
    declared = committed(DECLARATION)
    judge_script = _judge_script()
    declaration = pj.load_declaration()
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    judge_script.require_committed_file(pj.DEFAULT_WEIGHTED_MISS)
    declaration = replace(declaration, weighted_miss=pj.load_weighted_miss(applied=None))
    if declaration.weighting_applied:
        raise SystemExit("the weighted miss rule is on in the declaration; this diagnostic reads the declared cut-off rule")
    templates = dict(item.split("=", 1) for item in args.row)
    if sorted(templates) != sorted(declared["rows"]["chosen"]):
        raise SystemExit(f"--row must name exactly the declared rows {declared['rows']['chosen']}; got {sorted(templates)}")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    tau = declaration.primary
    horizons = declaration.horizons
    by_horizon, digests = load_forecasts(args.bench, templates, horizons)
    flat = [f for h in horizons for f in by_horizon[h]]
    states = {h: judge_script._scarcity_states(h, declaration.last_day) for h in horizons}

    def grids_of(items):
        out = {}
        for h in horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state=states[h])
        return out

    calendar = [r.date for r in rows]
    grids = grids_of(flat)
    last = declaration.last_day
    for h in horizons:
        pj.require_scored_days(declaration, grids[h].dates, where="setup sensitivity")
    names = declared["rows"]["chosen"] + declared["rows"]["benchmarks"]
    result = {
        "declaration": {"path": "metadata/setup_sensitivity.json", "judge_sha256": declaration.sha256},
        "panel_sha256": panel_sha256(args.panel),
        "forecast_panels": digests,
        "scored_window": {"first": grids[horizons[0]].dates[0].isoformat(), "last": grids[horizons[0]].dates[-1].isoformat()},
    }

    # The declared reading.
    chosen = pj.choose_cutoffs(declaration, grids, flat, calendar)
    declared_reading = tier_readings(declaration, chosen, grids, None)

    # 1. 2018-19 down-weighted.
    period = declared["year_dominance"]["period"]
    p_first, p_last = date.fromisoformat(period["first"]), date.fromisoformat(period["last"])
    all_days = grids[horizons[0]].dates
    share = sum(1 for d in all_days if p_first <= d <= p_last) / len(all_days)

    def selector(**kwargs):
        weights = ss.downweights([p_first <= d <= p_last for d in kwargs["days"]], share)
        return ss.select_cutoff_weighted(
            declaration.cutoff_false_alarms_at_most, weights=weights,
            **{k: v for k, v in kwargs.items()},
        )

    weighted = ss.choose_cutoffs_with(declaration, grids, flat, calendar, selector)
    weighted_reading = tier_readings(declaration, weighted, grids, None)
    calibration = pooled_calibration(declaration, flat, grids, p_first, p_last)
    later = declared["year_dominance"]["later_regime"]
    common_days = set.intersection(*(set(grids[h].dates) for h in horizons))
    profile_periods = {
        "2018-19": (p_first, p_last),
        "2020": (date(2020, 1, 1), date(2020, 12, 31)),
        "2021-23": (date(2021, 1, 1), date(2023, 12, 31)),
        "2024": (date.fromisoformat(later["first"]), date.fromisoformat(later["last"])),
        "2025": (date(2025, 1, 1), date(2025, 12, 31)),
    }
    result["year_dominance"] = {
        "share_of_all_days": share,
        "declared": {n: {k: v for k, v in declared_reading[n].items() if k not in ("caught", "onset", "days")} for n in names},
        "downweighted": {n: {k: v for k, v in weighted_reading[n].items() if k not in ("caught", "onset", "days")} for n in names},
        "cutoff_medians": {
            n: {
                "declared": {str(h): statistics.median([c for c in next(f for f in chosen if f.name == n and f.horizon == h).cutoffs[tau] if c != float("inf")] or [float("nan")]) for h in horizons},
                "downweighted": {str(h): statistics.median([c for c in next(f for f in weighted if f.name == n and f.horizon == h).cutoffs[tau] if c != float("inf")] or [float("nan")]) for h in horizons},
            }
            for n in names
        },
        "pooled_calibration": calibration,
        "profiles": {label: period_profile(rows, grids[horizons[0]], a, b, tau, common_days) for label, (a, b) in profile_periods.items()},
    }

    # 2. Refit cadence.
    cadence = {}
    for every in declared["refit_cadence"]["every"]:
        other = pj.choose_cutoffs(replace(declaration, cutoff_refit_every=every), grids, flat, calendar)
        reading = tier_readings(declaration, other, grids, None)
        cadence[str(every)] = {
            n: {
                **{k: v for k, v in reading[n].items() if k not in ("caught", "onset", "days")},
                "changed_onsets": ss.changed_onsets(
                    [date.fromisoformat(d) for d in reading[n]["days"]], reading[n]["onset"],
                    declared_reading[n]["caught"], reading[n]["caught"],
                ),
            }
            for n in names
        }
    result["refit_cadence"] = cadence

    # 3 and 4. The judge under both combiners; the regime calibration tables.
    holdouts = judge_script._holdouts()
    # A row the judge's declaration does not name (ngboost_laplace was scored by the pull request of #416 under a
    # declaration that is not on main) is added in memory for this scratch reading only; no file under
    # metadata/pressure_judge/ is written and the declaration's digest is unchanged.
    extra = {
        name: {"role": "candidate", "features": [], "calibration": "as in the row's own script (scratch reading, #482)"}
        for name in declared["rows"]["chosen"] if name not in declaration.candidates
    }
    declaration = replace(declaration, candidates={**declaration.candidates, **extra})
    result["undeclared_rows_added_in_memory"] = sorted(extra)
    judged = {}
    for combine in (declared["week_ahead_combiner"]["declared"], declared["week_ahead_combiner"]["other"]):
        judged[combine] = pj.judge(
            replace(declaration, week_combine=combine), grids, chosen, calendar=calendar, holdouts=holdouts,
        )
    result["week_ahead"] = {
        combine: {
            n: {key: value for key, value in judged[combine]["candidates"][n]["tiers"]["week_ahead"].items() if key != "reliability_steps"}
            for n in names
        }
        for combine in judged
    }
    primary = f"{declaration.primary:g}"
    tier_three = {}
    for n in names:
        candidate = judged[declared["week_ahead_combiner"]["declared"]]["candidates"][n]
        tier_three[n] = {
            "verdict_tier_1": candidate["verdict"]["tier_1_onset_warning"],
            "verdict_tier_3": candidate["verdict"]["tier_3_no_crying_wolf"],
            "verdict_tier_5": candidate["verdict"]["tier_5_week_ahead"],
            "by_horizon": {
                str(h): {
                    "abundant_stretches": row[primary]["no_crying_wolf"]["abundant_stretches"],
                    "regimes": {
                        label: {
                            "days": cell["days"], "events": cell["events"], "mean_predicted": cell["mean_predicted"],
                            "realised": cell["realised_frequency"],
                            "realised_minus_predicted": cell["realised_minus_predicted"],
                        }
                        for label, cell in row[primary]["splits"]["regime"].items()
                    },
                }
                for h, row in candidate["horizons"].items()
            },
        }
    result["tier_three"] = tier_three
    result["tier_three_concentration"] = concentration(tier_three, declaration)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result, declared), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _pct(value, places=2):
    return "–" if value is None else f"{value:.{places}f}"


def _cell(cell):
    if cell is None or cell.get("mean") is None:
        return "–"
    interval = cell.get("interval")
    if interval is None:
        return f"{cell['mean']:+.4f} (no interval)"
    return f"{cell['mean']:+.4f} [{interval['lower']:+.4f}, {interval['upper']:+.4f}]"


def markdown(result, declared) -> str:
    """The tables of the result page (docs/pivot/setup-sensitivity-result.md); every figure comes from `result`."""

    rows = declared["rows"]["chosen"]
    names = rows + declared["rows"]["benchmarks"]
    yd = result["year_dominance"]
    years = sorted(next(iter(yd["declared"].values()))["by_year"])
    lines = []

    def table(title, header, body):
        lines.extend(["", title, "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)])
        lines.extend("| " + " | ".join(str(c) for c in row) + " |" for row in body)

    onsets_by_year = {y: yd["declared"][rows[0]]["by_year"][y]["onsets"] for y in years}
    table(
        "Table 1. Tier 1 at lead >= 1, +5 bp, h = 1 to 5, whole window: the declared reading, and the cut-off chosen with the "
        f"period {declared['year_dominance']['period']['first'][:4]}-{declared['year_dominance']['period']['last'][:4]} "
        f"down-weighted to its share of all days ({yd['share_of_all_days']:.3f}). Onsets flagged, worst false alarms per onset (limit 2).",
        ["row", "declared: onsets flagged", "declared: worst FA per onset", "down-weighted: onsets flagged", "down-weighted: worst FA per onset"],
        [
            [n, f"{yd['declared'][n]['onsets_flagged']} of {yd['declared'][n]['onsets']}", _pct(yd["declared"][n]["worst_false_alarms_per_onset"]),
             f"{yd['downweighted'][n]['onsets_flagged']} of {yd['downweighted'][n]['onsets']}", _pct(yd["downweighted"][n]["worst_false_alarms_per_onset"])]
            for n in names
        ],
    )
    for label in ("declared", "downweighted"):
        table(
            f"Table 2{'a' if label == 'declared' else 'b'}. Tier 1 by calendar year of the flagged day, {label} reading: onsets flagged of onsets "
            "(worst false alarms at one horizon). Onsets by year: " + ", ".join(f"{y}: {onsets_by_year[y]}" for y in years) + ".",
            ["row"] + years,
            [
                [n] + [
                    "–" if not yd[label][n]["by_year"][y]["days"] else
                    f"{yd[label][n]['by_year'][y]['onsets_flagged']} of {yd[label][n]['by_year'][y]['onsets']} ({yd[label][n]['by_year'][y]['worst_false_alarms']})"
                    for y in years
                ]
                for n in names
            ],
        )
        table(
            f"Table 3{'a' if label == 'declared' else 'b'}. Tier 3 by calendar year, {label} reading: flags per 252 business days over all days "
            "(worst horizon); in brackets over the days in scarcity state 0 (limit 21), where the year has any.",
            ["row"] + years,
            [
                [n] + [
                    f"{yd[label][n]['by_year'][y]['flags_per_year_worst_horizon']:.0f}"
                    + (
                        f" ({yd[label][n]['by_year'][y]['abundant_flags_per_year_worst_horizon']:.0f})"
                        if yd[label][n]["by_year"][y]["abundant_flags_per_year_worst_horizon"] is not None else ""
                    )
                    for y in years
                ]
                for n in names
            ],
        )
    table(
        "Table 4. Pooled calibration at h = 1, +5 bp: realised minus mean predicted, over all scored days, inside and outside 2018-19 "
        "(weighting 2018-19 to its share of all days leaves the pooled mean unchanged, so the outside reading is the one that can differ).",
        ["row", "all days", "inside 2018-19", "outside 2018-19"],
        [
            [n] + [f"{yd['pooled_calibration'][n]['1'][k]['realised_minus_predicted']:+.4f}" for k in ("all_days", "inside_period", "outside_period")]
            for n in names
        ],
    )
    profiles = yd["profiles"]
    table(
        "Table 5. How the stretches differ (scored days; spread SOFR - IORB in basis points; panel medians of the inputs).",
        ["", *profiles],
        [
            ["scored days", *[p["scored_days"] for p in profiles.values()]],
            ["pressure days (> +5 bp)", *[f"{p['pressure_days']} ({p['pressure_share']:.1%})" for p in profiles.values()]],
            ["onsets / episodes", *[f"{p['onsets']} / {p['episodes']}" for p in profiles.values()]],
            ["longest episodes (days)", *[", ".join(str(x) for x in p["episode_lengths"][:4]) or "–" for p in profiles.values()]],
            ["spread median / p90 / max", *[f"{p['spread_bp']['median']:.0f} / {p['spread_bp']['p90']:.0f} / {p['spread_bp']['max']:.0f}" for p in profiles.values()]],
            ["scarcity state shares", *[", ".join(f"{k}: {v:.0%}" for k, v in p["scarcity_state_share"].items()) for p in profiles.values()]],
            *[
                [column, *[("–" if p["inputs_median"][column] is None else f"{p['inputs_median'][column]:,.1f}") for p in profiles.values()]]
                for column in PERIOD_COLUMNS
            ],
        ],
    )
    cadence = result["refit_cadence"]
    table(
        "Table 6. Refit cadence of the flag cut-off, tier 1 at lead >= 1: onsets flagged of 26 and worst false alarms per onset, "
        "for a cut-off refitted every 21 (declared), 10 and 5 scored days.",
        ["row", "every 21", "every 10", "every 5"],
        [
            [n, f"{yd['declared'][n]['onsets_flagged']} ({yd['declared'][n]['worst_false_alarms_per_onset']:.2f})"]
            + [f"{cadence[e][n]['onsets_flagged']} ({cadence[e][n]['worst_false_alarms_per_onset']:.2f})" for e in ("10", "5")]
            for n in names
        ],
    )
    table(
        "Table 7. Tier 1 by calendar year, cut-off refitted every 10 and every 5 scored days: onsets flagged of onsets, "
        "worst false alarms at one horizon (the declared reading is Table 2a).",
        ["row", "refit"] + [y for y in years if onsets_by_year[y]],
        [
            [n, e] + [f"{cadence[e][n]['by_year'][y]['onsets_flagged']} of {cadence[e][n]['by_year'][y]['onsets']} ({cadence[e][n]['by_year'][y]['worst_false_alarms']})" for y in years if onsets_by_year[y]]
            for n in names for e in ("10", "5")
        ],
    )
    changes = [
        [n, e, c["day"], "flagged" if c["declared_flagged"] else "not flagged", "flagged" if c["other_flagged"] else "not flagged"]
        for n in names for e in ("10", "5") for c in cadence[e][n]["changed_onsets"]
    ]
    table("Table 8. Onsets whose warning changes when the cut-off is refitted more often.", ["row", "refit every", "onset day", "declared (21)", "this cadence"], changes or [["none", "", "", "", ""]])
    week = result["week_ahead"]
    table(
        "Table 9. Tier 5 (week-ahead window, +5 bp) under the declared combiner (the maximum) and under independence. "
        "Realised minus predicted, and Brier difference against calendar climatology (positive: better), 90% intervals; calibrated = interval covers zero, beats = interval above zero.",
        ["row", "combiner", "base rate", "mean predicted", "realised - predicted", "Brier diff vs climatology", "calibrated", "beats clim.", "tier 5"],
        [
            [n, c, _pct(w["base_rate"], 3), _pct(w["mean_predicted"], 3), _cell(w["realised_minus_predicted"]), _cell(w["brier_difference_vs_climatology"]),
             "yes" if w["criteria"]["calibrated"] else "no", "yes" if w["criteria"]["beats_climatology_brier"] else "no", "pass" if w["passes"] else "fail"]
            for n in names for c in week for w in [week[c][n]]
        ],
    )
    regimes = list(result["tier_three"][rows[0]]["by_horizon"]["1"]["regimes"])
    first_regime = result["tier_three"][rows[0]]["by_horizon"]["1"]["regimes"]
    table(
        "Table 10. Tier 3 calibration in every regime (+5 bp): realised minus predicted frequency; a star marks an interval that misses zero. "
        "Pressure days in the regime: " + ", ".join(f"{k}: {v['events']} of {v['days']} days" for k, v in first_regime.items()) + ".",
        ["row", "h", *regimes],
        [
            [n, h, *[
                f"{cell['realised_minus_predicted']['mean']:+.4f}" + ("" if (cell['realised_minus_predicted'].get('interval') is None or cell['realised_minus_predicted']['interval']['lower'] <= 0 <= cell['realised_minus_predicted']['interval']['upper']) else " *")
                for cell in (result["tier_three"][n]["by_horizon"][h]["regimes"][r] for r in regimes)
            ]]
            for n in names for h in ("1", "2", "3", "4", "5")
        ],
    )
    conc = result["tier_three_concentration"]
    table(
        "Table 11. Where tier 3 fails, counted over the five leads: regimes whose calibration interval misses zero, and abundant stretches over the 21-flags limit.",
        ["row", "tier 3", "calibration misses zero (leads)", "alarm rate over limit (leads)"],
        [
            [n, "pass" if result["tier_three"][n]["verdict_tier_3"] else "fail",
             ", ".join(f"{k}: {v}" for k, v in conc[n]["calibration_misses_zero_by_regime"].items()) or "none",
             ", ".join(f"{k}: {v}" for k, v in conc[n]["alarm_rate_over_limit_by_stretch"].items()) or "none"]
            for n in names
        ],
    )
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--bench", required=True)
    run.add_argument("--row", action="append", required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--markdown", type=Path)
    run.set_defaults(run=command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
