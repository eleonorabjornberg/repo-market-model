"""The pressure-day audit (#473): what the pressure-day work may be overlooking.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. Nothing published moves. Scored days are 2018-06-29 to 2025-12-31 (`docs/decisions/lockbox.md`);
no 2026 day is read. The rule it scores is declared in `metadata/pressure_audit.json`, which this script
refuses to read unless it is committed and unchanged; the bar is the pressure-day judge's, unchanged
(`metadata/pressure_judge.json`).

    PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/pressure_audit.py inputs --panel AUG2.csv --published PUBLISHED.csv \\
        --output OUT/inputs.json
    PYTHONPATH=src python3 scripts/pressure_audit.py score --panel PUBLISHED.csv --output OUT/score.json \\
        --markdown OUT/score.md OUT/bench_h1.json ... OUT/risk_h1.json ...

`inputs` reads the panel through the as-of rule (`asof.InformationRule`) at each horizon 1 to 5, over the
judge's scored days, and reports for every candidate input the row it reads (how many panel days before the
scored day), how old that observation is at the 16:00 decision, and how well the value read at horizon 1 ranks
pressure days and onsets (AUROC), over all scored days and in the years no model warns (2018, 2020, 2024).
It also reports the row of the target, the spread, that the same rule reads, which is the effective horizon.

`score` chooses, refit by refit and horizon by horizon, which clauses of the declared calendar and settlement
rule are on, from the refit's training window alone (`select_clauses`, the judge's cut-off discipline applied
to clauses), and scores the rule's flags with the judge's own tier 1 (`pressure_judge._onset_tier`), beside
the benchmarks and the five candidates that pass tier 1, by lead, by horizon and by calendar year.
"""

from __future__ import annotations

import argparse
import bisect
import contextlib
import importlib.util
import itertools
import json
import subprocess
import sys
from collections import Counter
from datetime import date, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import measurement_fields  # noqa: E402
from repo_model import pressure as pressure_module  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.asof import InformationRule, fold_grid  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "pressure_audit.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
DECISION = time(16, 0)
MINIMUM_HISTORY = 61
HORIZONS = (1, 2, 3, 4, 5)
MISSED_YEARS = (2018, 2020, 2024)
CLAUSES = ("quarter_end", "tax_date", "month_end_window", "settlement")
VARIANTS = ("calendar", "calendar_settlement")

#: The inputs the audit reads through the as-of rule, in the order of the report. The first group is the panel
#: the published declaration reads; the second is read by no published declaration (measurement fields,
#: `measurement_fields.COLUMN_FIELDS`, and columns of the scratch panel).
PUBLISHED_INPUTS = (
    "spread_bps", "treasury_settlement", "treasury_settlement_bills", "treasury_settlement_coupons",
    "reserve_balances", "tga", "quarter_end", "tax_date", "days_to_month_end", "dealer_treasury_position",
    "tbill_4w", "tbill_13w", "sofr_p75", "sofr_p25",
)
MEASUREMENT_INPUTS = ("on_rrp", "tga_daily", "sofr_p99_iorb_bps", "sofr_p75_iorb_bps", "effr", "iorb_announced_change_bps")


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed_declaration(path: Path) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a rule is declared before any score")
    return json.loads(path.read_text(encoding="utf-8"))


# -- the rule -----------------------------------------------------------------


def clause_options(declared: dict, horizon: int, variant: str) -> dict:
    """The values each clause may take at `horizon` under `variant`, in the declared order.

    The settlement clause exists at the horizons the declaration names (horizon 1: a settlement is public at
    15:00 on the panel day before it) and only in the variant that uses it.
    """

    clauses = declared["rule"]["clauses"]
    settlement = clauses["settlement"]
    on = variant == "calendar_settlement" and horizon in settlement["horizons"]
    return {
        "quarter_end": list(clauses["quarter_end"]["enabled"]),
        "tax_date": list(clauses["tax_date"]["enabled"]),
        "month_end_window": list(clauses["month_end_window"]["within_calendar_days"]),
        "settlement": list(settlement["at_least_bn"]) if on else [None],
    }


def training_end(calendar, first_day, horizon):
    """The last day whose outcome a refit starting at `first_day` can read: the business day before its decision.

    The block's first scored day is `horizon` panel days after the first decision instant, and the outcome of the
    decision day is published the next morning, as in `pressure_judge.choose_cutoffs`. None when no such day.
    """

    position = bisect.bisect_left(calendar, first_day)
    last_known = position - horizon - 1
    return calendar[last_known] if last_known >= 0 else None


def select_clauses(*, days, onset, pressure, options, training_end, limit):
    """The clauses to switch on for one refit, chosen on its training window alone.

    `days` are the window's days (the first `len(days)` days of the grid); `onset` and `pressure` are bitmasks over
    the grid, bit k for the grid's day k; `options[clause][value]` is the bitmask of the days the clause flags at that
    value. The combination with the highest onset recall whose false alarms per onset on the window are at most
    `limit` wins; of equal recall the one that flags fewer days of the window, then the first in declared order.
    A window with no onset, or in which no combination within the limit catches an onset, chooses nothing (None).

    Raises:
        LookAheadError: if a day of the window is after `training_end`, the last day whose outcome the refit could
            read, or the window has a day and no training end.
    """

    if days:
        late = [day for day in days if training_end is None or day > training_end]
        if late:
            raise LookAheadError(
                f"clauses chosen from {len(late)} day(s) from {min(late)} on, after the refit's training end "
                f"({training_end}); a rule is chosen on training data only"
            )
    window = (1 << len(days)) - 1
    onsets = (onset & window).bit_count()
    if not onsets:
        return None
    best, best_key = None, None
    names = list(options)
    for values in itertools.product(*(list(options[name]) for name in names)):
        flags = 0
        for name, value in zip(names, values):
            flags |= options[name][value]
        flags &= window
        caught = (flags & onset).bit_count()
        if not caught:
            continue
        if (flags & ~pressure).bit_count() / onsets > limit + 1e-12:
            continue
        key = (caught, -flags.bit_count())
        if best_key is None or key > best_key:
            best, best_key = dict(zip(names, values)), key
    return best


def _mask(bits):
    out = 0
    for k, bit in enumerate(bits):
        if bit:
            out |= 1 << k
    return out


def rule_flags(declared, variant, horizon, grid, values_by_day, calendar, limit, refit_every, tau):
    """The rule's 0/1 flag on each grid day, chosen block by block, and the choice of each block."""

    days = list(grid.dates)
    pressure = _mask(grid.outcomes[tau])
    onset = _mask(grid.onset_at(tau, tau))
    options = clause_options(declared, horizon, variant)
    column = {name: declared["rule"]["clauses"][name].get("column") for name in CLAUSES}
    masks = {
        "quarter_end": {
            v: _mask([bool(v) and float(values_by_day[d][column["quarter_end"]] or 0.0) == 1.0 for d in days])
            for v in options["quarter_end"]
        },
        "tax_date": {
            v: _mask([bool(v) and float(values_by_day[d][column["tax_date"]] or 0.0) == 1.0 for d in days])
            for v in options["tax_date"]
        },
        "month_end_window": {
            v: _mask([v is not None and float(values_by_day[d][column["month_end_window"]]) <= v for d in days])
            for v in options["month_end_window"]
        },
        "settlement": {
            v: _mask([v is not None and float(values_by_day[d][column["settlement"]] or 0.0) >= v for d in days])
            for v in options["settlement"]
        },
    }
    flags, blocks = [], []
    for start in range(0, len(days), refit_every):
        block = days[start : start + refit_every]
        end = training_end(calendar, block[0], horizon)
        window = [d for d in days[:start] if end is not None and d <= end]
        choice = select_clauses(
            days=window, onset=onset, pressure=pressure, options=masks, training_end=end, limit=limit
        )
        chosen = 0
        if choice is not None:
            for name in CLAUSES:
                chosen |= masks[name][choice[name]]
        flags.extend((chosen >> (start + k)) & 1 for k in range(len(block)))
        blocks.append({"first_day": block[0].isoformat(), "training_days": len(window), "choice": choice})
    return flags, blocks


def rule_forecast(name, horizon, grid, flags, tau):
    """The flags as a `Forecast` the judge's tier 1 reads: probability 1 on a flag, 0 elsewhere, cut-off 0.5."""

    n = len(flags)
    return pj.Forecast(
        name=name, horizon=horizon, dates=tuple(grid.dates),
        probabilities={tau: tuple(float(f) for f in flags)}, cutoffs={tau: tuple([0.5] * n)},
    )


# -- scoring ------------------------------------------------------------------


def _flags_of(forecast, tau):
    return [1 if p >= c else 0 for p, c in zip(forecast.probabilities[tau], forecast.cutoffs[tau])]


def _slim(tier):
    keep = (
        "lead_at_least", "horizons", "complete", "days", "onsets", "onsets_flagged", "false_alarms_by_horizon",
        "recall", "climatology_recall", "recall_difference", "worst_false_alarms_per_onset", "criteria", "passes",
        "unavailable",
    )
    return {k: tier[k] for k in keep if k in tier}


def summarise(name, by_name, grids, declaration, calendar, common, tau):
    """Tier 1 by lead, by horizon alone and by calendar year, on the days common to every horizon."""

    scored = list(declaration.horizons)
    tiers = {
        f"lead_at_least_{lead}": _slim(pj._onset_tier(declaration, name, lead, scored, grids, by_name, calendar))
        for lead in scored
    }
    place = {h: {d: k for k, d in enumerate(grids[h].dates)} for h in scored}
    flags = {h: _flags_of(by_name[name][h], tau) for h in scored}
    onset_days = [d for d in common if grids[scored[0]].onset[place[scored[0]][d]]]
    pressure = {h: grids[h].outcomes[tau] for h in scored}
    by_horizon = {}
    for h in scored:
        caught = sum(flags[h][place[h][d]] for d in onset_days)
        raised = sum(1 for d in common if flags[h][place[h][d]] and not pressure[h][place[h][d]])
        by_horizon[str(h)] = {
            "onsets": len(onset_days), "onsets_flagged": caught, "false_alarms": raised,
            "false_alarms_per_onset": raised / len(onset_days) if onset_days else None,
            "flagged_days": sum(flags[h][place[h][d]] for d in common),
        }
    by_year = {}
    for year in sorted({d.year for d in common}):
        in_year = [d for d in common if d.year == year]
        year_onsets = [d for d in in_year if d in set(onset_days)]
        entry = {
            "days": len(in_year), "onsets": len(year_onsets),
            "onsets_flagged": sum(1 for d in year_onsets if any(flags[h][place[h][d]] for h in scored)),
            "false_alarms_by_horizon": {
                str(h): sum(1 for d in in_year if flags[h][place[h][d]] and not pressure[h][place[h][d]])
                for h in scored
            },
        }
        worst = max(entry["false_alarms_by_horizon"].values())
        entry["worst_false_alarms_per_onset"] = worst / len(year_onsets) if year_onsets else None
        by_year[str(year)] = entry
    flagged_at = {
        d.isoformat(): [h for h in scored if flags[h][place[h][d]]] for d in onset_days
    }
    return {"tier_1": tiers, "by_horizon": by_horizon, "by_year": by_year, "onsets_flagged_at_horizons": flagged_at}


def score_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    declaration = pj.load_declaration()
    require_unlocked([date.fromisoformat(declared["scoring"]["last_day"])], where="pressure_audit")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    digest = panel_sha256(args.panel)
    forecasts = []
    for path in args.inputs:
        document = json.loads(Path(path).read_text())
        if document["panel_sha256"] != digest:
            raise SystemExit(f"{path} was scored on another panel ({document['panel_sha256'][:8]})")
        forecasts.extend(pj.forecasts_from_horizon_document(document))
    names = [declaration.climatology, declaration.persistence, *declared["scored"]["reference_rows"]]
    forecasts = [f for f in forecasts if f.name in names]
    missing = [(n, h) for n in names for h in declaration.horizons if not any(f.name == n and f.horizon == h for f in forecasts)]
    if missing:
        raise SystemExit(f"forecast files lack {missing[0]} (and {len(missing) - 1} more)")

    def grids_of(items):
        out = {}
        for h in declaration.horizons:
            reference = next(f for f in items if f.horizon == h and f.name == declaration.climatology)
            out[h] = pj.build_grid(declaration, h, rows, reference.dates, splits, scarcity_state={})
        return out

    calendar = [row.date for row in rows]
    by_date = {row.date: row for row in rows}
    values_by_day = {d: by_date[d].values for d in by_date}
    tau = declaration.primary
    chosen = pj.choose_cutoffs(declaration, grids_of(forecasts), forecasts, calendar)
    grids = grids_of(chosen)
    refit_every = declaration.cutoff_refit_every
    limit = declaration.cutoff_false_alarms_at_most
    by_name = {}
    for forecast in chosen:
        by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
    choices = {}
    for variant in VARIANTS:
        name = f"audit_{variant}"
        by_name[name] = {}
        choices[name] = {}
        for h in declaration.horizons:
            flags, blocks = rule_flags(declared, variant, h, grids[h], values_by_day, calendar, limit, refit_every, tau)
            by_name[name][h] = rule_forecast(name, h, grids[h], flags, tau)
            choices[name][str(h)] = blocks
    common = sorted(set.intersection(*(set(grids[h].dates) for h in declaration.horizons)))
    scored_names = [f"audit_{v}" for v in VARIANTS] + names
    summaries = {name: summarise(name, by_name, grids, declaration, calendar, common, tau) for name in scored_names}
    first = declaration.horizons[0]
    place = {d: k for k, d in enumerate(grids[first].dates)}
    onsets = []
    for d in common:
        if not grids[first].onset[place[d]]:
            continue
        values = by_date[d].values
        onsets.append(
            {
                "day": d.isoformat(), "year": d.year, "regime": splits.regime(d),
                "day_type": splits.reporting_day_type(d, values),
                "days_to_month_end": values["days_to_month_end"], "quarter_end": values["quarter_end"],
                "tax_date": values["tax_date"], "settlement_bn": values["treasury_settlement"],
                "coupons_bn": values["treasury_settlement_coupons"], "bills_bn": values["treasury_settlement_bills"],
                "flagged_at_horizons": {n: summaries[n]["onsets_flagged_at_horizons"][d.isoformat()] for n in scored_names},
            }
        )
    result = {
        "provenance": {
            "panel_sha256": digest, "declaration": declared, "judge_declaration_sha256": declaration.sha256,
            "forecast_files": [str(p) for p in args.inputs],
            "scored_window": [common[0].isoformat(), common[-1].isoformat()], "common_days": len(common),
        },
        "choices": choices, "summaries": summaries, "onsets": onsets,
    }
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "onsets": len(onsets)}))
    return 0


# -- the inputs and the effective horizon -------------------------------------


def _median(values):
    ordered = sorted(values)
    return ordered[len(ordered) // 2] if ordered else None


def inputs_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="pressure_audit")
    risk = _load_script("risk_date_severity")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    published = {r.date: r for r in load_daily_panel(args.published)}
    for r in rows:
        if r.date <= last and (r.date not in published or published[r.date].spread_bps != r.spread_bps):
            raise SystemExit(f"{r.date}: the scratch panel's spread is not the published panel's")
    dates = [r.date for r in rows]
    registry = measurement_fields.load_registry()
    features = PUBLISHED_INPUTS + MEASUREMENT_INPUTS
    tau = 5.0
    out = {"panel_sha256": panel_sha256(args.panel), "published_panel_sha256": panel_sha256(args.published), "horizons": {}}
    series = {}
    with risk.switched_on():
        for h in HORIZONS:
            grid = [i for i in fold_grid(dates, registry, decision_time=DECISION, minimum_history=MINIMUM_HISTORY, horizon=h) if dates[i] <= last]
            rule = InformationRule(registry, features, decision_time=DECISION, horizon=h)
            rows_back = {f: Counter() for f in features}
            hours = {f: [] for f in features}
            anchors = Counter()
            for i in grid:
                info = rule.information_set(dates, i)
                anchors[i - info.anchor] += 1
                for read in info.reads:
                    if read.feature not in rows_back:
                        continue
                    rows_back[read.feature][read.rows] += 1
                    if read.hours is not None:
                        hours[read.feature].append(read.hours)
                    if h == 1:
                        series.setdefault(read.feature, {})[dates[i]] = rows[read.row].values.get(read.feature)
            out["horizons"][str(h)] = {
                "scored_days": len(grid),
                "target_row_read_panel_days_before_scored_day": {str(k): v for k, v in sorted(anchors.items())},
                "inputs": {
                    f: {
                        "panel_days_before_scored_day": {str(k): v for k, v in sorted(rows_back[f].items())},
                        "median_hours_between_availability_and_decision": _median(hours[f]),
                    }
                    for f in features
                },
            }
    pressure = {r.date: int(exceeds_bp(r.spread_bps, tau)) for r in rows if r.date <= last}
    scored_days = [d for d in dates if date(2018, 6, 29) <= d <= last]
    onset_days = set(pressure_module.onsets(rows, tau, scored_days))
    ranking = {}
    for f, by_day in series.items():
        cell = {}
        for label, years in (("all_years", None), *((str(y), (y,)) for y in MISSED_YEARS)):
            days = [d for d in by_day if by_day[d] is not None and d in pressure and (years is None or d.year in years)]
            values = [float(by_day[d]) for d in days]
            cell[label] = {
                "days": len(days),
                "pressure_days": sum(pressure[d] for d in days),
                "auroc_pressure_day": pj.auroc(values, [pressure[d] for d in days]),
                "onsets": sum(1 for d in days if d in onset_days),
                "auroc_onset_vs_non_pressure": _onset_auroc(days, values, pressure, onset_days),
            }
        ranking[f] = cell
    out["rank_at_horizon_1"] = ranking
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "inputs": len(features)}))
    return 0


def _onset_auroc(days, values, pressure, onset_days):
    keep = [(v, 1 if d in onset_days else 0) for d, v in zip(days, values) if d in onset_days or not pressure[d]]
    if not any(o for _, o in keep):
        return None
    return pj.auroc([v for v, _ in keep], [o for _, o in keep])


# -- the summary --------------------------------------------------------------


def _pct(x):
    return "–" if x is None else f"{x:.2f}"


def markdown(result) -> str:
    summaries = result["summaries"]
    names = list(summaries)
    lines = [
        "Table A. Tier 1 (onset warning) of the rule and the reference rows, +5 bp, on the days common to every horizon. "
        "Lead >= k: the share of onsets flagged at some horizon h >= k, worst horizon's false alarms per onset, 90% "
        "stationary-bootstrap interval on the recall, climatology's recall at the same false alarms.",
        "",
        "| row | lead | onsets flagged | recall [90%] | climatology recall, same false alarms | worst false alarms per onset |",
        "|---|---|---|---|---|---|",
    ]
    for name in names:
        for lead in (1, 2, 3, 4, 5):
            t = summaries[name]["tier_1"][f"lead_at_least_{lead}"]
            recall = t.get("recall") or {}
            interval = recall.get("interval")
            ci = f"{recall['mean']:.3f} [{interval['lower']:.3f}, {interval['upper']:.3f}]" if interval else _pct(recall.get("mean"))
            lines.append(
                f"| {name} | {lead} | {t.get('onsets_flagged')} of {t.get('onsets')} | {ci} | "
                f"{_pct(t.get('climatology_recall'))} | {_pct(t.get('worst_false_alarms_per_onset'))} |"
            )
    lines += [
        "",
        "Table B. One horizon alone. Horizon h is a decision 16:00 on the h-th business day before the scored day; "
        "the effective horizon from the last observed spread is h + 1 business days.",
        "",
        "| row | h | onsets flagged | false alarms per onset | days flagged |",
        "|---|---|---|---|---|",
    ]
    for name in names:
        for h in (1, 2, 3, 4, 5):
            c = summaries[name]["by_horizon"][str(h)]
            lines.append(f"| {name} | {h} | {c['onsets_flagged']} of {c['onsets']} | {_pct(c['false_alarms_per_onset'])} | {c['flagged_days']} |")
    lines += [
        "",
        "Table C. By calendar year: onsets flagged at some horizon h >= 1 / onsets, and the worst horizon's false "
        "alarms per onset of the year (blank when the year has no onset).",
        "",
        "| row | " + " | ".join(summaries[names[0]]["by_year"]) + " |",
        "|---|" + "---|" * len(summaries[names[0]]["by_year"]),
    ]
    for name in names:
        cells = []
        for year, c in summaries[name]["by_year"].items():
            cells.append(f"{c['onsets_flagged']}/{c['onsets']}, {_pct(c['worst_false_alarms_per_onset'])}" if c["onsets"] else f"0/0, {c['false_alarms_by_horizon']['1']} FA")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Table D. Each onset: the calendar facts and the horizons (1 to 5) at which each row flagged it.",
        "",
        "| day | day type | days to month end | settlement bn (coupons) | " + " | ".join(names) + " |",
        "|---|---|---|---|" + "---|" * len(names),
    ]
    for o in result["onsets"]:
        hits = " | ".join(",".join(str(h) for h in o["flagged_at_horizons"][n]) or "–" for n in names)
        lines.append(
            f"| {o['day']} | {o['day_type']} | {o['days_to_month_end']:g} | {o['settlement_bn']:g} ({o['coupons_bn']:g}) | {hits} |"
        )
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    score = commands.add_parser("score", help="the calendar and settlement rule and the reference rows, tier 1")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--markdown", type=Path)
    score.add_argument("inputs", nargs="+", type=Path)
    score.set_defaults(handler=score_command)
    inputs = commands.add_parser("inputs", help="the as-of read and the ranking of each candidate input")
    inputs.add_argument("--panel", type=Path, required=True)
    inputs.add_argument("--published", type=Path, required=True)
    inputs.add_argument("--output", type=Path, required=True)
    inputs.set_defaults(handler=inputs_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
