"""What separates the every-day part's onset warnings from its false alarms (#601, step 1): declaration and measurement.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
The row is `risk_gbm+every_day+gate+settle+h41+iorb` (#579, PR #582). Its every-day part serves a day that is not a risk date
at a lead. `run` lists the days on which the part flags at some lead 1 to 5, splits them into onset warnings and false alarms,
and compares the two groups on inputs public at each decision instant, read per field under `docs/decisions/information-set.md`
(`asof.InformationRule`; the masked frame of each decision gives the rows a lagged change may use). Every choice is in
`metadata/every_day_separation_601.json`, which this script refuses to read unless it is committed and unchanged. Scored days are
2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`; `require_unlocked`).

    # AUG2D.csv is the scratch panel of satiation_distance_598.py (pressure_v1_1.py panel, measurement_fields.py panel, then
    # satiation_distance_598.py panel); PUBLISHED.csv is the published panel
    PYTHONPATH=src python3 scripts/every_day_separation_601.py declare
    PYTHONPATH=src python3 scripts/every_day_separation_601.py run --panel PUBLISHED.csv --scratch AUG2D.csv \\
        --output OUT/separation.json --markdown OUT/separation.md OUT/bench_h?.json OUT/both_h?.json OUT/iorb_h?.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import statistics
import sys
from dataclasses import replace
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import h41_release, measurement_fields, satiation as sat  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import _as_of_folds  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import DAY_TYPE_COLUMNS, load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import _quantile, stationary_bootstrap_indices  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "every_day_separation_601.json"
LEADS = (1, 2, 3, 4, 5)
#: the columns a "days to the next risk date" count may read: the calendar columns, always known in advance
CALENDAR_COLUMNS = tuple(DAY_TYPE_COLUMNS)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


pg = _load("pooled_gate_595")
sd = _load("satiation_distance_598")
ann = pg.ann
rds = pg.rds

ROW = pg.ROW
TAIL = "sofr_p99_iorb_bps"
P99, P1, P75 = "sofr_p99", "sofr_p1", "sofr_p75"
RESERVES, TGA = "reserve_balances", "tga"
DISTANCE = sat.DISTANCE_COLUMN
#: the features the decision's information set is formed for; every column below is read through them
READ = ("spread_bps", TAIL, P99, P1, P75, RESERVES, TGA, DISTANCE)

#: name -> (family, one line). Order is the order of the tables.
INPUTS = {
    "tail_spread_level": ("tail_spread", "the SOFR 99th percentile less IORB (bp), at its latest public row"),
    "tail_spread_change_1": ("tail_spread", "that level less its value 1 market day earlier"),
    "tail_spread_change_5": ("tail_spread", "that level less its value 5 market days earlier"),
    "tail_spread_change_10": ("tail_spread", "that level less its value 10 market days earlier"),
    "satiation_distance": ("satiation_distance", "the rolling satiation distance of #587 (PR #596), at its latest public row"),
    "reserve_level": ("reserve_trend", "reserve balances (USD bn), as the row reads them (H.4.1 per release)"),
    "reserve_change_5": ("reserve_trend", "reserve balances less their value 5 market days earlier"),
    "reserve_change_20": ("reserve_trend", "reserve balances less their value 20 market days earlier"),
    "rows_to_risk_date": ("days_to_risk_date", "market days from the decision row to the next calendar risk date (quarter-end, month-end window, tax date)"),
    "tga_level": ("tga_path", "the Treasury General Account (USD bn), at its latest public row"),
    "tga_change_5": ("tga_path", "the TGA less its value 5 market days earlier"),
    "tga_change_10": ("tga_path", "the TGA less its value 10 market days earlier"),
    "dispersion_p99_p1": ("percentile_dispersion", "the SOFR 99th percentile less the 1st (percentage points)"),
    "dispersion_p99_p75": ("percentile_dispersion", "the SOFR 99th percentile less the 75th (percentage points)"),
}
FAMILIES = ("tail_spread", "satiation_distance", "reserve_trend", "days_to_risk_date", "tga_path", "percentile_dispersion")


# -- the declaration ---------------------------------------------------------------------------------------


def declaration_document() -> dict:
    judge = json.loads((REPO / "metadata" / "pressure_judge.json").read_text(encoding="utf-8"))
    parents = json.loads(rds.DECLARATION.read_text(encoding="utf-8"))
    return {
        "status": (
            "declared by the pull request that closes #601 before any score; a measurement, not a record. Step 1 only: a comparison of "
            "two groups of days on inputs public at each decision instant. Nothing here is published: no rule, threshold, onset "
            "definition or availability time changes, no 2026 day is scored, and the live record and pin do not move. The comparison reads "
            "2018-2025, so a result is a description of that history and not a confirmation (ruling of 11 October 2026 on #567)"
        ),
        "issue": 601,
        "row": ROW,
        "scoring": parents["scoring"],
        "judge": "the judge as in force on main (metadata/pressure_judge.json, unchanged), under the weighted rule in force; the flag cut-offs are the judge's own for the row",
        "population": (
            "every day of 2018-06-29 to 2025-12-31 scored at all leads 1 to 5 on which the row flags at some lead at which the day is not a risk date "
            "(a lead's flag is the every-day part's when the day is not a risk date at that lead: pooled_gate_595.py's `risk_date_at`)"
        ),
        "groups": {
            "onset_warnings": "such a day that is a +5 bp onset day (the judge's onset definition)",
            "false_alarms": "such a day that is not a pressure day at +5 bp",
            "left_out_and_counted": "such a day that is a pressure day but not an onset; onsets warned by the risk-date part only; false alarms of the risk-date part",
        },
        "unit": "the day. Its inputs are read at the decision instant of the farthest lead at which the every-day part flags it, the first instant at which the part could have warned. A per-lead table beside it takes each flag at a lead as a unit, read at that lead's decision instant",
        "information": (
            "each input is read at its latest public row through asof.InformationRule at the unit's horizon, on the 'both' arm of #541 (settlements dated from the "
            "auction announcement, the H.4.1 weeklies read per release), with the measurement columns and the distance columns switched on for the run only. "
            "A change over k market days is the latest public value less the value k panel rows earlier in the decision's masked frame. The days to the next "
            "risk date read the calendar columns only (always known in advance)"
        ),
        "inputs": {name: {"family": family, "reads": text} for name, (family, text) in INPUTS.items()},
        "input_families": {family: [n for n, (f, _t) in INPUTS.items() if f == family] for family in FAMILIES},
        "separation": (
            "the area under the ROC curve of the input for onset warnings against false alarms (the chance that an onset warning's value is above a false "
            "alarm's, ties half): 0.5 is no separation, above 0.5 the onset warnings read higher. An input separates when the interval excludes 0.5"
        ),
        "bootstrap": {
            "level": judge["bootstrap"]["level"],
            "replications": judge["bootstrap"]["replications"],
            "block_length": judge["bootstrap"]["block_length"],
            "seed": 601,
            "resampling": "the two groups apart: onset warnings one by one (each is a separate episode), false alarms by the judge's stationary bootstrap over their date order, block length as the judge's",
        },
        "second_look": "the same comparison with the false alarms restricted to the calendar years that hold an onset warning, so a difference of year does not pass for a difference of days",
        "multiplicity": "the number of inputs examined is stated beside the result; at a 90% interval about one in ten inputs that do not separate would show an interval that excludes 0.5 by chance",
        "published": "nothing; no variant, input or setting joins any published declaration",
    }


def declare_command(args) -> int:
    DECLARATION.write_text(json.dumps(declaration_document(), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(DECLARATION)}))
    return 0


# -- the readers -------------------------------------------------------------------------------------------


def latest_public(values: Sequence[Optional[float]]) -> Optional[int]:
    """The position of the last value that is not a hole, or `None`."""

    for position in range(len(values) - 1, -1, -1):
        if values[position] is not None:
            return position
    return None


def _read_up_to(position: int, limit: int) -> None:
    """A read may sit at the decision's anchor row or before it, never after."""

    if position > limit:
        raise LookAheadError(f"a value is read at row {position}, after the decision's anchor row {limit}")


def change_over(values: Sequence[Optional[float]], k: int, *, limit: int) -> Optional[float]:
    """The latest public value less the value `k` rows earlier; `None` when either is a hole.

    `limit` is the decision's anchor row: the masked frame holds no row after it, and a series longer than that is refused.

    Raises:
        LookAheadError: when the latest public value sits after `limit`.
    """

    position = latest_public(values)
    if position is None:
        return None
    _read_up_to(position, limit)
    earlier = position - k
    if earlier < 0 or values[earlier] is None:
        return None
    return float(values[position]) - float(values[earlier])


def _calendar_columns_only(columns: Sequence[str]) -> None:
    other = [c for c in columns if c not in CALENDAR_COLUMNS]
    if other:
        raise LookAheadError(f"the days to the next risk date may read calendar columns only, not {other}")


def rows_to_next_risk_date(day_types: Sequence[str], decision: int, *, columns: Sequence[str]) -> Optional[int]:
    """Market days from row `decision` to the next row after it whose day type is not 'ordinary'; `None` when there is none.

    The day types come from the calendar columns (quarter-end, month-end window, tax date), which are known in advance, so a
    future row's type is not a look-ahead. `columns` names what the types were formed from.

    Raises:
        LookAheadError: when `columns` holds a column that is not a calendar column.
    """

    _calendar_columns_only(columns)
    for row in range(decision + 1, len(day_types)):
        if day_types[row] != "ordinary":
            return row - decision
    return None


def dispersion(upper: Optional[float], lower: Optional[float]) -> Optional[float]:
    return None if upper is None or lower is None else float(upper) - float(lower)


def read_inputs(series: Mapping[str, Sequence[Optional[float]]], *, anchor: int, rows_to_risk: Optional[int]) -> Dict[str, Optional[float]]:
    """Every declared input of one decision: `series[column]` is the masked frame's column, ending at the anchor row."""

    def level(column):
        position = latest_public(series[column])
        if position is None:
            return None
        _read_up_to(position, anchor)
        return float(series[column][position])

    p99, p1, p75 = level(P99), level(P1), level(P75)
    return {
        "tail_spread_level": level(TAIL),
        "tail_spread_change_1": change_over(series[TAIL], 1, limit=anchor),
        "tail_spread_change_5": change_over(series[TAIL], 5, limit=anchor),
        "tail_spread_change_10": change_over(series[TAIL], 10, limit=anchor),
        "satiation_distance": level(DISTANCE),
        "reserve_level": level(RESERVES),
        "reserve_change_5": change_over(series[RESERVES], 5, limit=anchor),
        "reserve_change_20": change_over(series[RESERVES], 20, limit=anchor),
        "rows_to_risk_date": None if rows_to_risk is None else float(rows_to_risk),
        "tga_level": level(TGA),
        "tga_change_5": change_over(series[TGA], 5, limit=anchor),
        "tga_change_10": change_over(series[TGA], 10, limit=anchor),
        "dispersion_p99_p1": dispersion(p99, p1),
        "dispersion_p99_p75": dispersion(p99, p75),
    }



# -- units and the separation ------------------------------------------------------------------------------


def every_day_leads(flagged_at: Sequence[int], risk_date_at: Sequence[int]) -> List[int]:
    """The leads at which the flag is the every-day part's: flagged at a lead where the day is not a risk date."""

    return [h for h in flagged_at if h not in risk_date_at]


def decision_lead(leads: Sequence[int]) -> int:
    """The farthest lead that flags the day: its decision instant is the earliest at which the part could have warned."""

    return max(leads)


def split_units(days: Sequence[Mapping]) -> dict:
    """Onset warnings and false alarms of the every-day part, and the days that belong to neither (counted)."""

    onset_warnings, false_alarms = [], []
    pressure_not_onset = risk_only_onsets = risk_false_alarms = 0
    for day in days:
        leads = every_day_leads(day["flagged_at"], day["risk_date_at"])
        flagged = bool(day["flagged_at"])
        unit = dict(day, every_day_leads=leads, decision_lead=decision_lead(leads) if leads else None)
        if day["onset"]:
            if leads:
                onset_warnings.append(unit)
            elif flagged:
                risk_only_onsets += 1
        elif day["pressure_day"]:
            if leads:
                pressure_not_onset += 1
        elif flagged:
            if leads:
                false_alarms.append(unit)
            else:
                risk_false_alarms += 1
    return {
        "onset_warnings": onset_warnings,
        "false_alarms": false_alarms,
        "flagged_pressure_days_not_onsets": pressure_not_onset,
        "onsets_warned_by_the_risk_date_part_only": risk_only_onsets,
        "risk_date_false_alarms": risk_false_alarms,
    }


def _auroc(onset: Sequence[float], alarm: Sequence[float]) -> Optional[float]:
    from repo_model import pressure_judge as pj

    return pj.auroc(list(onset) + list(alarm), [1] * len(onset) + [0] * len(alarm))


def resample_groups(n_onset: int, n_alarm: int, *, block_length: float, rng: random.Random):
    """One resample of each group, apart: the onset warnings one by one, the false alarms by the stationary bootstrap."""

    onset = stationary_bootstrap_indices(n_onset, 1, rng) if n_onset else ()
    alarm = stationary_bootstrap_indices(n_alarm, block_length, rng) if n_alarm else ()
    return onset, alarm


def separation(onset: Sequence[Optional[float]], alarm: Sequence[Optional[float]], *, seed: int, replications: int, block_length: float, level: float) -> dict:
    """The input's area under the ROC curve for onset warnings against false alarms, with a bootstrap interval.

    `alarm` is in date order, which the block bootstrap relies on. Holes are dropped and counted.
    """

    o = [float(x) for x in onset if x is not None]
    a = [float(x) for x in alarm if x is not None]
    out = {
        "onset_n": len(o), "alarm_n": len(a),
        "onset_holes": len(onset) - len(o), "alarm_holes": len(alarm) - len(a),
        "onset_median": statistics.median(o) if o else None,
        "alarm_median": statistics.median(a) if a else None,
        "auroc": None, "interval": None,
    }
    if not o or not a:
        return out
    out["auroc"] = _auroc(o, a)
    rng = random.Random(seed)
    draws = []
    for _ in range(replications):
        i, j = resample_groups(len(o), len(a), block_length=block_length, rng=rng)
        draws.append(_auroc([o[k] for k in i], [a[k] for k in j]))
    draws.sort()
    tail = (1.0 - level) / 2.0
    out["interval"] = (_quantile(draws, tail), _quantile(draws, 1.0 - tail))
    return out


def separates(result: Mapping) -> bool:
    interval = result.get("interval")
    return interval is not None and (interval[0] > 0.5 or interval[1] < 0.5)


# -- the measurement ---------------------------------------------------------------------------------------


def day_table(pj, declaration, by_name, grids, calendar, scratch, splits) -> List[dict]:
    """Every common scored day of leads 1 to 5 with what the row did on it (as `pooled_gate_595.diagnose` lists it, for every day)."""

    tau = declaration.primary
    settle, _h41, _suffix = ann.ARMS["both"]
    leads = [h for h in LEADS if h in declaration.horizons]
    common = sorted(set.intersection(*(set(grids[h].dates) for h in leads)))
    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in leads}
    first = leads[0]
    pressure = [bool(grids[first].outcomes[tau][position[first][day]]) for day in common]
    onset = [bool(grids[first].onset_at(tau, tau)[position[first][day]]) for day in common]
    place = {day: k for k, day in enumerate(calendar)}
    places = [place[day] for day in common]
    weights = (
        list(pj.false_alarm_weights(declaration.weighted_miss, positions=places, pressure=[int(p) for p in pressure], known_through=places[-1]))
        if declaration.weighted_miss is not None else [1.0] * len(common)
    )
    days = []
    for k, day in enumerate(common):
        values = scratch[day].values
        flagged = [
            h for h in leads
            if by_name[ROW][h].probabilities[tau][position[h][day]] >= by_name[ROW][h].cutoffs[tau][position[h][day]]
        ]
        days.append({
            "date": day.isoformat(),
            "year": day.year,
            "regime": grids[first].groups["regime"][position[first][day]],
            "day_type": grids[first].groups["day_type"][position[first][day]],
            "pressure_day": pressure[k],
            "onset": onset[k],
            "weight": weights[k],
            "flagged_at": flagged,
            "risk_date_at": [h for h in leads if ann.risk_flag(splits, values, settle or h == 1)],
        })
    return days


def read_units(units: Sequence[dict], rows, registry, last: date, horizons: Sequence[int]) -> Dict[int, Dict[str, dict]]:
    """For each horizon, the inputs of every unit day with a flag at that horizon, read at that horizon's decision instant."""

    wanted: Dict[int, set] = {h: set() for h in horizons}
    for unit in units:
        for h in unit["every_day_leads"]:
            if h in wanted:
                wanted[h].add(unit["date"])
    splits = load_split_declaration(rds.SPLITS)
    out: Dict[int, Dict[str, dict]] = {}
    for h in horizons:
        timed_rows, timed_registry = ann.arm_inputs("both", rows, registry, h)
        dates = [row.date for row in timed_rows]
        in_window = [row for row in timed_rows if row.date <= last]
        day_types = [splits.day_type(row.values) for row in in_window]
        rule = InformationRule(timed_registry, READ, decision_time=time(16, 0), horizon=h)
        out[h] = {}
        with sd.switched_on(), h41_release.release_dating():
            for fold in _as_of_folds(
                timed_rows, rule, minimum_history=61, refit_every=len(timed_rows), entry="every_day_separation_601", end=last
            ):
                day = dates[fold.index].isoformat()
                if day not in wanted[h]:
                    continue
                frame = rule.frame(timed_rows, fold.info)
                anchor = len(frame) - 1
                series = {column: [row.values.get(column) for row in frame] for column in (TAIL, P99, P1, P75, RESERVES, TGA, DISTANCE)}
                decision_row = fold.index - h
                out[h][day] = read_inputs(
                    series, anchor=anchor,
                    rows_to_risk=rows_to_next_risk_date(day_types, decision_row, columns=CALENDAR_COLUMNS),
                )
    return out


def compare_groups(warnings: Sequence[dict], alarms: Sequence[dict], bootstrap: Mapping, *, seed_offset: int = 0) -> dict:
    """Each input's separation of the two groups; `alarms` is in date order. `inputs` of a unit are under `unit['inputs']`."""

    table = {}
    for index, name in enumerate(INPUTS):
        table[name] = separation(
            [u["inputs"][name] for u in warnings],
            [u["inputs"][name] for u in alarms],
            seed=bootstrap["seed"] + seed_offset + index,
            replications=bootstrap["replications"],
            block_length=bootstrap["block_length"],
            level=bootstrap["level"],
        )
    return table


def _fmt(x, digits=2):
    return "–" if x is None else f"{x:.{digits}f}"


def table_markdown(title: str, table: Mapping[str, dict]) -> str:
    lines = [
        f"{title}\n",
        "| input | family | onset warnings: n, median | false alarms: n, median | AUROC [90% interval] | separates |",
        "|---|---|---|---|---|---|",
    ]
    for name, r in table.items():
        interval = "–" if r["interval"] is None else f"[{r['interval'][0]:.2f}, {r['interval'][1]:.2f}]"
        lines.append(
            f"| `{name}` | {INPUTS[name][0]} | {r['onset_n']}, {_fmt(r['onset_median'])} | {r['alarm_n']}, {_fmt(r['alarm_median'])} | "
            f"{_fmt(r['auroc'], 3)} {interval} | {'yes' if separates(r) else 'no'} |"
        )
    return "\n".join(lines) + "\n"


def run_command(args) -> int:
    from repo_model import pressure_judge as pj

    declared = rds.committed_declaration(DECLARATION)
    last = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([last], where="every_day_separation_601")
    declaration = replace(pj.load_declaration(), weighted_miss=pj.load_weighted_miss(applied=True))
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    scratch_rows = load_daily_panel(args.scratch)
    scratch = {row.date: row for row in scratch_rows}
    splits = load_split_declaration(rds.SPLITS)
    by_name, grids, calendar = pg.judged_forecasts(pj, declaration, rows, splits, args.panel, args.inputs)
    days = day_table(pj, declaration, by_name, grids, calendar, scratch, splits)
    units = split_units(days)
    registry = measurement_fields.load_registry()
    flagged = units["onset_warnings"] + units["false_alarms"]
    inputs = read_units(flagged, scratch_rows, registry, last, [h for h in LEADS if h in declaration.horizons])
    for unit in flagged:
        unit["inputs"] = inputs[unit["decision_lead"]][unit["date"]]
        unit["inputs_by_lead"] = {str(h): inputs[h][unit["date"]] for h in unit["every_day_leads"]}
    bootstrap = declared["bootstrap"]
    warnings = sorted(units["onset_warnings"], key=lambda u: u["date"])
    alarms = sorted(units["false_alarms"], key=lambda u: u["date"])
    pooled = compare_groups(warnings, alarms, bootstrap)
    years = sorted({u["year"] for u in warnings})
    same_years = [u for u in alarms if u["year"] in years]
    second = compare_groups(warnings, same_years, bootstrap, seed_offset=100)
    per_lead = {}
    for h in LEADS:
        w = [dict(u, inputs=u["inputs_by_lead"][str(h)]) for u in warnings if h in u["every_day_leads"]]
        a = [dict(u, inputs=u["inputs_by_lead"][str(h)]) for u in alarms if h in u["every_day_leads"]]
        per_lead[str(h)] = {"onset_warnings": len(w), "false_alarms": len(a), "table": compare_groups(w, a, bootstrap, seed_offset=200 + 20 * h)}
    document = {
        "row": ROW,
        "counts": {
            "onset_warnings": len(warnings),
            "false_alarms": len(alarms),
            "false_alarms_in_years_with_an_onset_warning": len(same_years),
            "years_with_an_onset_warning": years,
            **{k: v for k, v in units.items() if isinstance(v, int)},
        },
        "inputs_examined": len(INPUTS),
        "onset_warning_dates": [{"date": u["date"], "leads": u["every_day_leads"], "decision_lead": u["decision_lead"], "regime": u["regime"]} for u in warnings],
        "pooled": pooled,
        "same_years": second,
        "per_lead": per_lead,
        "units": warnings + alarms,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    text = markdown(document)
    if args.markdown:
        args.markdown.write_text(text, encoding="utf-8")
    print(text)
    return 0


def markdown(document: Mapping) -> str:
    c = document["counts"]
    out = [
        f"Every-day part of `{document['row']}`: {c['onset_warnings']} onset warnings and {c['false_alarms']} false alarms "
        f"(left out and counted: {c['flagged_pressure_days_not_onsets']} flagged pressure days that are not onsets; "
        f"{c['onsets_warned_by_the_risk_date_part_only']} onsets warned by the risk-date part only; {c['risk_date_false_alarms']} false alarms of the risk-date part). "
        f"{document['inputs_examined']} inputs examined; at a 90% interval about one in ten that do not separate would show one that excludes 0.5 by chance.\n",
        "Onset warnings: " + "; ".join(f"{u['date']} (leads {u['leads']}, read at lead {u['decision_lead']})" for u in document["onset_warning_dates"]) + ".\n",
        table_markdown("Table 1. Pooled: each input at the decision instant of the farthest lead that flags the day.", document["pooled"]),
        table_markdown(
            f"Table 2. The same, false alarms restricted to the years with an onset warning ({document['counts']['years_with_an_onset_warning']}; "
            f"{c['false_alarms_in_years_with_an_onset_warning']} false alarms).",
            document["same_years"],
        ),
    ]
    for h, cell in document["per_lead"].items():
        out.append(table_markdown(f"Table 3, lead {h}: {cell['onset_warnings']} onset warnings, {cell['false_alarms']} false alarms flagged at this lead.", cell["table"]))
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("declare").set_defaults(func=declare_command)
    run = sub.add_parser("run")
    run.add_argument("--panel", type=Path, required=True)
    run.add_argument("--scratch", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--markdown", type=Path)
    run.add_argument("inputs", nargs="+", type=Path)
    run.set_defaults(func=run_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
