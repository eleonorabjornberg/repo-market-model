"""Two reported-only diagnostics on the onset bar (#429, a track of #374).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into
`docs/runs/`. Neither diagnostic changes the bar. The rows, the buckets and the power settings are in
`metadata/onset_diagnostics.json`, which this script refuses to read unless it is committed and unchanged; the
bar, the cut-off rule and the bootstrap are the judge's (`metadata/pressure_judge.json`).

    PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon H --output OUT/bench_hH.json
    ... each row's own forecast script, h = 1 to 5, as `docs/pivot/onset-diagnostics-result.md` lists ...
    PYTHONPATH=src python3 scripts/onset_diagnostics.py false-alarms --panel PUBLISHED.csv \\
        --bench 'OUT/bench_h{h}.json' --row two_part_gbm='OUT/tp_h{h}.json' ... \\
        --output OUT/false_alarms.json --markdown OUT/false_alarms.md
    PYTHONPATH=src python3 scripts/onset_diagnostics.py power --panel PUBLISHED.csv \\
        --bench 'OUT/bench_h{h}.json' --output OUT/power.json --markdown OUT/power.md

`false-alarms` takes the judge's own flags (the cut-off chosen refit by refit from the training window,
`pressure_judge.choose_cutoffs`) for each declared row at each horizon, and splits the false alarms by the
flagged day's realised spread, its distance to the nearest pressure day, its day type and its regime. It
checks its counts against Table 1 of the re-judge. `power` asks how often a model with a given true onset recall
meets tier 1's recall conditions, on the development window's real onsets and on the confirmation window with
a parameter number of onsets (no day of that window is read). A forecast file scored on a scratch panel is
accepted when its days are the benchmark's; its panel digest is recorded.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import random
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import onset_diagnostics as od  # noqa: E402
from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "onset_diagnostics.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
RESULT = REPO / "docs" / "pivot" / "judge-amendment-result.md"
DAY_TYPES = ("month_end", "ordinary", "quarter_end", "tax_date")


def _judge_script():
    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
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
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def table_one() -> dict:
    """{model: (onsets flagged, onsets, worst false alarms per onset)} from Table 1 of the re-judge."""

    rows, inside = {}, False
    for line in RESULT.read_text().splitlines():
        if line.startswith("Table 1."):
            inside = True
        elif inside and line.startswith("Table 2."):
            break
        elif inside and line.startswith("| ") and not line.startswith(("| model", "|---")):
            cells = [c.strip() for c in line.strip("|").split("|")]
            flagged, total = cells[1].split(" of ")
            rows[cells[0]] = (int(flagged), int(total), float(cells[4]))
    return rows


def _document(template: str, h: int, bench_dates=None) -> dict:
    return json.loads(Path(template.format(h=h)).read_text())


def load_forecasts(bench: str, rows: dict, horizons):
    """{horizon: [Forecast]}: the benchmarks and each declared row, on the benchmark's days."""

    out, digests = {}, {}
    for h in horizons:
        bench_doc = _document(bench, h)
        forecasts = pj.forecasts_from_horizon_document(bench_doc)
        digests[f"bench_h{h}"] = bench_doc["panel_sha256"]
        reference = next(f for f in forecasts if f.name == "calendar_climatology")
        for name, template in rows.items():
            document = _document(template, h)
            if int(document["horizon"]) != h or name not in document["forecasts"]:
                raise SystemExit(f"{template.format(h=h)} holds no {name!r} at h = {h}")
            mine = next(f for f in pj.forecasts_from_horizon_document(document) if f.name == name)
            if mine.dates != reference.dates:
                raise SystemExit(f"{name} h = {h}: its days are not the benchmark's")
            digests[f"{name}_h{h}"] = document["panel_sha256"]
            forecasts.append(mine)
        out[h] = forecasts
    return out, digests


def false_alarms_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    judge_script = _judge_script()
    declaration = pj.load_declaration()
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    settings = declared["false_alarms"]
    wanted = settings["rows"]["chosen"]
    templates = dict(item.split("=", 1) for item in args.row)
    if sorted(templates) != sorted(wanted):
        raise SystemExit(f"--row must name exactly the declared rows {wanted}; got {sorted(templates)}")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    tau = float(declared["scoring"]["primary_threshold_bp"])
    last = date.fromisoformat(declared["scoring"]["last_day"])
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

    calendar = [row.date for row in rows]
    position = {day: k for k, day in enumerate(calendar)}
    chosen = pj.choose_cutoffs(declaration, grids_of(flat), flat, calendar)
    grids = grids_of(chosen)
    spread = {row.date: float(row.spread_bps) for row in rows}
    last_position = max(k for k, day in enumerate(calendar) if day <= last)
    pressure_positions = [k for k, day in enumerate(calendar) if day <= last and exceeds_bp(spread[day], tau)]
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    onset_days = [day for day, o in zip(grids[horizons[0]].dates, grids[horizons[0]].onset) if o and day in set(common)]
    s_buckets = settings["realised_spread_bp"]["buckets"]
    d_buckets = settings["distance_to_pressure_day"]["buckets"]
    s_labels, d_labels = [b["label"] for b in s_buckets], [b["label"] for b in d_buckets]
    regimes = sorted({g for h in horizons for g in grids[h].groups["regime"]})
    splits_spec = (
        ("spread_bucket", s_labels),
        ("distance_bucket", d_labels),
        ("day_type", list(DAY_TYPES)),
        ("regime", regimes),
    )

    def records_of(grid, flags):
        keep = [k for k, day in enumerate(grid.dates) if day in set(common)]
        return od.false_alarm_records(
            positions=[position[grid.dates[k]] for k in keep],
            flags=[flags[k] for k in keep],
            pressure=[grid.outcomes[tau][k] for k in keep],
            spreads=[spread[grid.dates[k]] for k in keep],
            day_types=[grid.groups["day_type"][k] for k in keep],
            regimes=[grid.groups["regime"][k] for k in keep],
            pressure_positions=pressure_positions,
            last_position=last_position,
            spread_buckets=s_buckets,
            distance_buckets=d_buckets,
        )

    def split_counts(records):
        return {key: od.tabulate(records, key, labels) for key, labels in splits_spec}

    # The days a flag could fall on: every non-pressure day every horizon scores. The same at each horizon.
    base_grid = grids[horizons[0]]
    base = split_counts(records_of(base_grid, [1] * len(base_grid.dates)))
    onsets = len(onset_days)
    table = table_one()
    result_rows, checks = {}, {}
    for name in wanted:
        per_horizon = {}
        caught = {day: 0 for day in onset_days}
        for h in horizons:
            forecast = next(f for f in chosen if f.name == name and f.horizon == h)
            grid = grids[h]
            flags = [1 if p >= c else 0 for p, c in zip(forecast.probabilities[tau], forecast.cutoffs[tau])]
            for flag, day in zip(flags, grid.dates):
                if flag and day in caught:
                    caught[day] = 1
            records = records_of(grid, flags)
            per_horizon[str(h)] = {"false_alarms": len(records), "per_onset": len(records) / onsets, **split_counts(records)}
        total = {key: {label: sum(per_horizon[str(h)][key][label] for h in horizons) for label in labels} for key, labels in splits_spec}
        total["false_alarms"] = sum(per_horizon[str(h)]["false_alarms"] for h in horizons)
        total["per_onset"] = total["false_alarms"] / onsets
        worst = max(v["per_onset"] for v in per_horizon.values())
        flagged = sum(caught.values())
        index = {day: k for k, day in enumerate(common)}
        onset_positions = [index[day] for day in onset_days]
        point, lower, upper, _ = od.recall_interval(
            onset_positions, [caught[day] for day in onset_days], len(common),
            block_length=declaration.block_length, replications=declaration.replications,
            level=declaration.level, rng=random.Random(declaration.seed),
        )
        expected = table[name]
        checks[name] = {
            "onsets": onsets, "onsets_flagged": flagged, "table_1_onsets_flagged": expected[0],
            "worst_false_alarms_per_onset": round(worst, 2), "table_1_worst": expected[2],
            "recall_interval_here": [lower, upper],
            "matches_table_1": flagged == expected[0] and onsets == expected[1] and round(worst, 2) == expected[2],
        }
        result_rows[name] = {"horizons": per_horizon, "all_horizons": total, "onsets_flagged": flagged, "recall": point}
    document = {
        "declaration": {"path": "metadata/onset_diagnostics.json", "commit": judge_script.require_committed_declaration(DECLARATION)},
        "judge_declaration_sha256": declaration.sha256,
        "scored_window": {"first": common[0].isoformat(), "last": common[-1].isoformat(), "days": len(common)},
        "onsets": onsets,
        "non_pressure_days": {**base, "days": sum(base["day_type"].values())},
        "rows": result_rows,
        "checks_against_table_1": checks,
        "forecast_panels": digests,
    }
    bad = [name for name, c in checks.items() if not c["matches_table_1"]]
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(false_alarm_markdown(document, declared), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "matches_table_1": {n: c["matches_table_1"] for n, c in checks.items()}}))
    if bad:
        print(f"WARNING: these rows do not match Table 1 of the re-judge: {bad}", file=sys.stderr)
        return 1
    return 0


def false_alarm_markdown(document: dict, declared: dict) -> str:
    lines = [
        "# Where the false alarms fall (#429)",
        "",
        f"Declaration `metadata/onset_diagnostics.json` (commit `{document['declaration']['commit'][:12]}`), the judge's flags "
        f"(declaration sha256 `{document['judge_declaration_sha256'][:12]}…`), +5 bp, scored days {document['scored_window']['first']} to "
        f"{document['scored_window']['last']} ({document['scored_window']['days']} days every horizon scores, {document['onsets']} onsets). "
        "A false alarm is a flag on a day that is not a pressure day; the day is the flagged (target) day.",
        "",
        "Table A. False alarms by horizon: the count, and per onset (Table 1 of the re-judge reports the worst horizon).",
        "",
    ]
    horizons = list(next(iter(document["rows"].values()))["horizons"])
    lines += ["| row | " + " | ".join(f"h={h}" for h in horizons) + " | all horizons | onsets flagged |", "|---|" + "---|" * (len(horizons) + 2)]
    for name, row in document["rows"].items():
        cells = [f"{row['horizons'][h]['false_alarms']} ({row['horizons'][h]['per_onset']:.2f})" for h in horizons]
        lines.append(
            f"| {name} | " + " | ".join(cells) + f" | {row['all_horizons']['false_alarms']} ({row['all_horizons']['per_onset']:.2f}) | "
            f"{row['onsets_flagged']} of {document['onsets']} |"
        )
    settings = declared["false_alarms"]
    titles = {
        "spread_bucket": "the flagged day's realised spread (whole basis points)",
        "distance_bucket": "the flagged day's distance to the nearest pressure day (panel days)",
        "day_type": "the flagged day's type",
        "regime": "the flagged day's regime",
    }
    letters = iter("BCDE")
    for key, title in titles.items():
        labels = list(document["non_pressure_days"][key])
        lines += [
            "",
            f"Table {next(letters)}. False alarms (all five horizons together) by {title}. The first row is the non-pressure days "
            "a flag could fall on, summed over the five horizons; a cell is the count and the share of that row's false alarms.",
            "",
            "| row | " + " | ".join(labels) + " | total |",
            "|---|" + "---|" * (len(labels) + 1),
        ]
        total_base = len(horizons) * sum(document["non_pressure_days"][key].values())
        base_cells = [
            f"{len(horizons) * document['non_pressure_days'][key][l]} ({100 * document['non_pressure_days'][key][l] / sum(document['non_pressure_days'][key].values()):.0f}%)"
            for l in labels
        ]
        lines.append("| non-pressure days (flag-days available) | " + " | ".join(base_cells) + f" | {total_base} |")
        for name, row in document["rows"].items():
            counts = row["all_horizons"][key]
            total = sum(counts.values())
            cells = [f"{counts[l]} ({100 * counts[l] / total:.0f}%)" if total else f"{counts[l]}" for l in labels]
            lines.append(f"| {name} | " + " | ".join(cells) + f" | {total} |")
    lines += ["", "Table F. Flag rate by the flagged day's distance to the nearest pressure day: false alarms divided by the non-pressure days in the group (all five horizons).", ""]
    labels = list(document["non_pressure_days"]["distance_bucket"])
    lines += ["| row | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
    for name, row in document["rows"].items():
        cells = [
            f"{row['all_horizons']['distance_bucket'][l] / (len(horizons) * document['non_pressure_days']['distance_bucket'][l]):.3f}"
            if document["non_pressure_days"]["distance_bucket"][l] else "–"
            for l in labels
        ]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines += ["", "Check against Table 1 of the re-judge (onsets flagged, worst false alarms per onset): "
              + "; ".join(f"{n} {'matches' if c['matches_table_1'] else 'DOES NOT MATCH'}" for n, c in document["checks_against_table_1"].items()) + ".", ""]
    return "\n".join(lines) + "\n"


# -- power -------------------------------------------------------------------


def _power_task(args):
    window, positions, n, r, settings, bootstrap = args
    return window, f"{r:g}", od.recall_power(
        positions, n, true_recalls=(r,), climatology_recalls=settings["climatology_recalls"],
        experiments=settings["experiments"], seed=settings["seed"] + (0 if window == "development" else 1000 * int(window.split("_")[-1])),
        block_length=bootstrap.block_length, replications=bootstrap.replications, level=bootstrap.level,
    )[f"{r:g}"]


def power_command(args) -> int:
    declared = committed_declaration(DECLARATION)
    judge_script = _judge_script()
    declaration = pj.load_declaration()
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    settings = declared["power"]
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    horizons = declaration.horizons
    dates = None
    for h in horizons:
        reference = next(f for f in pj.forecasts_from_horizon_document(_document(args.bench, h)) if f.name == declaration.climatology)
        dates = set(reference.dates) if dates is None else dates & set(reference.dates)
    common = sorted(dates)
    grid = pj.build_grid(declaration, horizons[0], rows, common, splits, scarcity_state={})
    positions = [k for k, o in enumerate(grid.onset) if o]
    tasks = []
    for r in settings["true_recalls"]:
        tasks.append(("development", positions, len(common), r, settings, declaration))
    window = settings["confirmation_window"]
    for count in window["onsets"]:
        for r in settings["true_recalls"]:
            tasks.append((f"confirmation_{count}", od.evenly_spaced(count, window["days"]), window["days"], r, settings, declaration))
    with multiprocessing.Pool(args.processes) as pool:
        done = pool.map(_power_task, tasks)
    out = {"development": {}, **{f"confirmation_{c}": {} for c in window["onsets"]}}
    for name, key, cell in done:
        out[name][key] = cell
    analytic = {
        "development": {f"{r:g}": od.binomial_at_least(len(positions), r, declaration.onset_recall_at_least) for r in settings["true_recalls"]},
        **{
            f"confirmation_{c}": {f"{r:g}": od.binomial_at_least(c, r, declaration.onset_recall_at_least) for r in settings["true_recalls"]}
            for c in window["onsets"]
        },
    }
    document = {
        "declaration": {"path": "metadata/onset_diagnostics.json", "commit": judge_script.require_committed_declaration(DECLARATION)},
        "judge_declaration_sha256": declaration.sha256,
        "development": {"days": len(common), "onsets": len(positions), "first": common[0].isoformat(), "last": common[-1].isoformat()},
        "confirmation": {"days": window["days"], "onsets": window["onsets"]},
        "bootstrap": {"level": declaration.level, "replications": declaration.replications, "block_length": declaration.block_length},
        "experiments": settings["experiments"],
        "recall_at_least": declaration.onset_recall_at_least,
        "climatology_recalls": settings["climatology_recalls"],
        "analytic_point_condition": analytic,
        "power": out,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(power_markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "development_onsets": len(positions)}))
    return 0


def power_markdown(document: dict) -> str:
    clim = document["climatology_recalls"]
    lines = [
        "# What 26 onsets can prove (#429)",
        "",
        f"Declaration `metadata/onset_diagnostics.json` (commit `{document['declaration']['commit'][:12]}`), the judge's bootstrap "
        f"({document['bootstrap']['level']:.0%} stationary, block length {document['bootstrap']['block_length']}, "
        f"{document['bootstrap']['replications']} replications), {document['experiments']} experiments per cell. A cell is the share of experiments in which "
        "the condition holds. A model flags each onset independently with its true recall; only the recall conditions are simulated, not the "
        "false-alarm limit. 'Both' is tier 1's recall conditions together: the point recall is at least "
        f"{document['recall_at_least']:g} and the lower end of the bootstrap interval is above the climatology recall at the same false alarms.",
        "",
    ]
    for name, cells in document["power"].items():
        if name == "development":
            info = document["development"]
            title = f"Development window: {info['onsets']} onsets over {info['days']} days ({info['first']} to {info['last']}), the real onset positions."
        else:
            title = (f"Confirmation window: {name.split('_')[1]} onset(s), a parameter, evenly spaced over {document['confirmation']['days']} days "
                     "(no day of the window is read).")
        lines += [
            f"## {title}",
            "",
            "| true recall | point recall at least the bar (exact) | (simulated) | interval unavailable | "
            + " | ".join(f"lower end above clim. recall {c:g}" for c in clim) + " | "
            + " | ".join(f"both, clim. recall {c:g}" for c in clim) + " |",
            "|---|---|---|---|" + "---|" * (2 * len(clim)),
        ]
        for key, cell in cells.items():
            lines.append(
                f"| {key} | {document['analytic_point_condition'][name][key]:.3f} | {cell['point_at_least']:.3f} | {cell['interval_unavailable']:.3f} | "
                + " | ".join(f"{cell['lower_above'][f'{c:g}']:.3f}" for c in clim) + " | "
                + " | ".join(f"{cell['both'][f'{c:g}']:.3f}" for c in clim) + " |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    fa = commands.add_parser("false-alarms")
    fa.add_argument("--panel", type=Path, required=True)
    fa.add_argument("--bench", required=True, help="the benchmarks' forecast file, with {h} for the horizon")
    fa.add_argument("--row", action="append", required=True, help="NAME=TEMPLATE for each declared row, with {h}")
    fa.add_argument("--output", type=Path, required=True)
    fa.add_argument("--markdown", type=Path)
    fa.set_defaults(run=false_alarms_command)
    power = commands.add_parser("power")
    power.add_argument("--panel", type=Path, required=True)
    power.add_argument("--bench", required=True)
    power.add_argument("--output", type=Path, required=True)
    power.add_argument("--markdown", type=Path)
    power.add_argument("--processes", type=int, default=4)
    power.set_defaults(run=power_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
