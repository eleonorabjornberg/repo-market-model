"""The alarm cool-down (#459): repeat flags inside five trading days count as one alarm.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given, nothing into
`docs/runs/`, and moves no published figure. The six rows, the cool-down length and the two forms are in
`metadata/alarm_cooldown.json`, committed before any score; each cooled row is a candidate file of its own
under `metadata/pressure_judge/candidates/` (`<row>_cooldown5`, `<row>_cooldown5_strict`) carrying its
`alarm_rule`, which the judge (`pressure_judge.cooldown_flags`) applies to that row's flags. No refit, no
new cut-off: a cooled row reuses its base row's probabilities.

    PYTHONPATH=src python3 scripts/alarm_cooldown.py assemble --panel PUB.csv --bench 'OUT/bench_h{h}.json' \\
        --row two_part_gbm='OUT/tp_h{h}.json' ... --output 'OUT/cd_h{h}.json'
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json \\
        --markdown OUT/judge.md OUT/cd_h?.json
    PYTHONPATH=src python3 scripts/alarm_cooldown.py report OUT/judge.json --output OUT/report.json --markdown OUT/report.md

`assemble` writes, for each horizon, the benchmark rows, each base row and its two cooled copies in the shape
`pressure_judge.py judge` reads. A row scored on a scratch panel carries that panel's digest; it is accepted when its
days are the benchmark's, and the digests are recorded (`forecast_panels`). `report` reads the judge's file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402

DECLARATION = REPO / "metadata" / "alarm_cooldown.json"
BENCHMARKS = ("calendar_climatology", "persistence_logistic")
FORMS = (("{row}_cooldown5", "with the exception"), ("{row}_cooldown5_strict", "strict"))
THRESHOLD_KEY = "5"


def _declared() -> dict:
    return json.loads(DECLARATION.read_text(encoding="utf-8"))


def _read(template: str, horizon: int) -> dict:
    return json.loads(Path(template.format(h=horizon)).read_text(encoding="utf-8"))


def assemble_command(args) -> int:
    declared = _declared()
    wanted = declared["rows"]["chosen"]
    templates = dict(item.split("=", 1) for item in args.row)
    if sorted(templates) != sorted(wanted):
        raise SystemExit(f"--row must name exactly the declared rows {wanted}; got {sorted(templates)}")
    digest = panel_sha256(args.panel)
    horizons = declared["scoring"]["horizons"]
    provenance = {}
    for horizon in horizons:
        bench = _read(args.bench, horizon)
        if bench["panel_sha256"] != digest:
            raise SystemExit(f"the benchmark file of h = {horizon} was scored on another panel")
        forecasts = {name: bench["forecasts"][name] for name in BENCHMARKS}
        reference = pj.forecasts_from_horizon_document(
            {"horizon": horizon, "panel_sha256": digest, "forecasts": forecasts}
        )[0]
        for row in wanted:
            document = _read(templates[row], horizon)
            if int(document["horizon"]) != horizon or row not in document["forecasts"]:
                raise SystemExit(f"{templates[row].format(h=horizon)} holds no {row!r} at h = {horizon}")
            mine = next(
                f for f in pj.forecasts_from_horizon_document(
                    {"horizon": horizon, "panel_sha256": document["panel_sha256"], "forecasts": {row: document["forecasts"][row]}}
                )
            )
            if mine.dates != reference.dates:
                raise SystemExit(f"{row} h = {horizon}: its days are not the benchmark's")
            provenance[f"{row}_h{horizon}"] = document["panel_sha256"]
            forecasts[row] = document["forecasts"][row]
            for pattern, _ in FORMS:
                forecasts[pattern.format(row=row)] = document["forecasts"][row]
        out = {
            "horizon": horizon,
            "panel_sha256": digest,
            "forecasts": forecasts,
            "forecast_panels": {k: v for k, v in provenance.items() if k.endswith(f"_h{horizon}")},
        }
        path = Path(args.output.format(h=horizon))
        path.write_text(json.dumps(out, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(path), "rows": len(forecasts)}))
    return 0


def _f(value, places=3):
    return "–" if value is None else f"{value:.{places}f}"


def report_document(result: dict, declared: dict) -> dict:
    """The comparison of each base row with its cooled forms, read off a judge result."""

    candidates = result["candidates"]
    rows = {}
    for row in declared["rows"]["chosen"]:
        entry = {}
        for label, name in (("base", row), ("with_exception", f"{row}_cooldown5"), ("strict", f"{row}_cooldown5_strict")):
            c = candidates[name]
            near = c["tiers"]["onset_warning"]["lead_at_least_1"]
            by_horizon = near["false_alarms_by_horizon"]
            h1 = c["horizons"]["1"][THRESHOLD_KEY]
            entry[label] = {
                "name": name,
                "onsets": near["onsets"],
                "onsets_flagged": near["onsets_flagged"],
                "recall": near["recall"],
                "worst_false_alarms_per_onset": near["worst_false_alarms_per_onset"],
                "worst_weighted_false_alarms_per_onset": near.get("worst_weighted_false_alarms_per_onset"),
                "weighted_miss_applied": near.get("weighted_miss_applied"),
                "false_alarms_per_onset_by_horizon": {h: v["per_onset"] for h, v in by_horizon.items()},
                "criteria": near["criteria"],
                "tier_1": bool(near["passes"]),
                "tier_3": bool(c["verdict"]["tier_3_no_crying_wolf"]),
                "tier_3_by_horizon": c["verdict"]["tier_3_no_crying_wolf_by_horizon"],
                "tier_5": bool(c["verdict"]["tier_5_week_ahead"]),
                "passes": bool(c["verdict"]["passes"]),
                "h1_flags": h1["flags"],
                "h1_by_regime": {k: v["flags"] for k, v in h1["splits"]["regime"].items()},
                "h1_by_day_type": {k: v["flags"] for k, v in h1["splits"]["day_type"].items()},
            }
        rows[row] = entry
    applied = {e["weighted_miss_applied"] for forms in rows.values() for e in forms.values()}
    return {
        "rows": rows,
        "declaration": result["declaration"]["sha256"],
        "weighted_miss_applied": applied == {True},
    }


def report_markdown(document: dict) -> str:
    rule = (
        "the weighted-miss rule of #454 forced on (a scratch run; the flag cut-offs are chosen on the weighted count, tier 1's limit is on it)"
        if document["weighted_miss_applied"]
        else "the unweighted rule (every false alarm counts 1; the weighted count is shown beside it)"
    )
    lines = [
        "# Alarm cool-down (#459): base rows and their cooled forms",
        "",
        f"Tier 1 at lead >= 1, +5 bp, days to 2025-12-31, under {rule}. `with exception` keeps repeats when a pressure day starts in the window "
        "(reads the days after the flag); `strict` drops every repeat.",
        "",
        "| row | form | onsets warned | recall [90%] | worst false alarms per onset, flat (weighted) | tier 1 | tier 3 | tier 5 | pass |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row, forms in document["rows"].items():
        for label, e in forms.items():
            r = e["recall"]
            lines.append(
                f"| {row} | {label.replace('_', ' ')} | {e['onsets_flagged']:g} of {e['onsets']} | "
                f"{_f(r['mean'])} [{_f((r.get('interval') or {}).get('lower'))}, {_f((r.get('interval') or {}).get('upper'))}] | "
                f"{_f(e['worst_false_alarms_per_onset'], 2)} ({_f(e['worst_weighted_false_alarms_per_onset'], 2)}) | "
                f"{'yes' if e['tier_1'] else 'no'} | {'yes' if e['tier_3'] else 'no'} | {'yes' if e['tier_5'] else 'no'} | "
                f"{'yes' if e['passes'] else 'no'} |"
            )
    lines += ["", "False alarms per onset by horizon:", "",
              "| row | form | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |", "|---|---|---|---|---|---|---|"]
    for row, forms in document["rows"].items():
        for label, e in forms.items():
            cells = " | ".join(_f(e["false_alarms_per_onset_by_horizon"].get(str(h)), 2) for h in range(1, 6))
            lines.append(f"| {row} | {label.replace('_', ' ')} | {cells} |")
    regimes = sorted({k for forms in document["rows"].values() for e in forms.values() for k in e["h1_by_regime"]})
    lines += ["", "Alarms at h = 1 (flags; of them false alarms) by regime:", "",
              "| row | form | " + " | ".join(regimes) + " |", "|---|---|" + "---|" * len(regimes)]
    for row, forms in document["rows"].items():
        for label, e in forms.items():
            cells = " | ".join(
                f"{e['h1_by_regime'][g]['alarms']:g} ({e['h1_by_regime'][g]['false_alarms']:g})" for g in regimes
            )
            lines.append(f"| {row} | {label.replace('_', ' ')} | {cells} |")
    types = sorted({k for forms in document["rows"].values() for e in forms.values() for k in e["h1_by_day_type"]})
    lines += ["", "Alarms at h = 1 (flags; of them false alarms) by pressure-day type:", "",
              "| row | form | " + " | ".join(types) + " |", "|---|---|" + "---|" * len(types)]
    for row, forms in document["rows"].items():
        for label, e in forms.items():
            cells = " | ".join(
                f"{e['h1_by_day_type'][g]['alarms']:g} ({e['h1_by_day_type'][g]['false_alarms']:g})" for g in types
            )
            lines.append(f"| {row} | {label.replace('_', ' ')} | {cells} |")
    return "\n".join(lines) + "\n"


def report_command(args) -> int:
    result = json.loads(args.judge.read_text(encoding="utf-8"))
    if result["mode"] != "development":
        raise SystemExit("the cool-down report reads a development judge file only (docs/decisions/lockbox.md)")
    document = report_document(result, _declared())
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(report_markdown(document), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    assemble = sub.add_parser("assemble")
    assemble.add_argument("--panel", type=Path, required=True)
    assemble.add_argument("--bench", required=True, help="benchmark file template with {h}")
    assemble.add_argument("--row", action="append", required=True, help="NAME=TEMPLATE with {h}")
    assemble.add_argument("--output", required=True, help="output template with {h}")
    assemble.set_defaults(run=assemble_command)
    report = sub.add_parser("report")
    report.add_argument("judge", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--markdown", type=Path)
    report.set_defaults(run=report_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
