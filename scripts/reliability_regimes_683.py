"""Reliability slopes within regimes (#683, finding #670): the page tables the pooled slopes hid.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given. Development data only (no day after
2025-12-31 is read, `docs/decisions/lockbox.md`); nothing here is a verdict. Serves H5 (calibration in 2018-19 and 2025-26) and H2.

    PYTHONPATH=src python3 scripts/reliability_regimes_683.py tracked --output OUT/tracked.json --markdown OUT/tracked.md
    PYTHONPATH=src python3 scripts/reliability_regimes_683.py kinked --published PUBLISHED.csv \\
        --bench 'OUT/bench_h{h}.json' --parents 'OUT/both_h{h}.json' --rows 'OUT/kinked_h{h}.json' \\
        --output OUT/kinked.json --markdown OUT/kinked.md

`tracked` reads the per-regime slopes already in a tracked evidence file (#624's `step2-off-risk-days.json`) and tabulates them: no
forecast is rebuilt, and the file carries points without intervals. `kinked` re-reads the forecast files of #626 (built by the commands in
`scripts/kinked_626.py`'s docstring), takes the same days as its `extras` (the days that are not risk dates) and fits the reliability line
with `repo_model.reliability_regimes`, pooled, per regime (2018-19, 2020-24, 2025-26) and per as-of scarcity state, each with a 90%
stationary-bootstrap interval of the judge's declaration. The pooled cell is there to be compared with the regimes, never read alone.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure_judge as pj  # noqa: E402
from repo_model import reliability_regimes as rr  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

LAST_DAY = date(2025, 12, 31)
#: A fitted slope this large in size is a near-separated fit, not a reading.
UNSTABLE = 25.0
#: A cell with fewer pressure days than this is marked: its slope is a handful of events' worth.
FEW = 5
SPLITS = REPO / "metadata" / "evaluation_splits.json"
STEP2 = REPO / "docs" / "pivot" / "evidence" / "off-risk-day" / "step2-off-risk-days.json"

READING = (
    "Pooled slopes mislead here (#670): a regime with no pressure day (2021-23) forecasts near 0 and adds a long, well-ordered stretch at the "
    "bottom of the curve, which raises the pooled slope. Read calibration within a regime. A cell with no pressure day has no slope. "
    "Figures here are development, not a verdict."
)


def _kinked():
    spec = importlib.util.spec_from_file_location("kinked_626_script", REPO / "scripts" / "kinked_626.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["kinked_626_script"] = module
    spec.loader.exec_module(module)
    return module


def _cells_json(cells) -> dict:
    return {
        k: {
            "days": c.days, "events": c.events, "slope": c.slope, "intercept": c.intercept,
            "slope_interval": c.slope_interval, "intercept_interval": c.intercept_interval,
        }
        for k, c in cells.items()
    }


# -- tracked: the points already in #624's evidence ----------------------------------------------------------------


def tracked_command(args) -> int:
    require_unlocked([LAST_DAY], where="reliability_regimes_683")
    data = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    out: Dict[str, dict] = {}
    for row, leads in data["rows"].items():
        out[row] = {
            h: {
                cell: {"days": v["days"], "pressure_days": v["pressure_days"], "slope": v.get("slope")}
                for cell, v in body["cells"].items()
            }
            for h, body in leads.items()
        }
    result = {"source": str(Path(args.evidence).relative_to(REPO)) if Path(args.evidence).is_absolute() else str(args.evidence), "rows": out, "reading": READING}
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(tracked_text(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _slope_text(cell) -> str:
    if cell is None:
        return "–"
    if cell["pressure_days"] == 0:
        return "undefined"
    if cell["slope"] is None:
        return "–"
    if abs(cell["slope"]) > UNSTABLE:
        return "unstable"
    mark = "†" if cell["pressure_days"] < FEW else ""
    return f"{cell['slope']:.2f}{mark}"


def tracked_text(result: dict) -> str:
    columns = ["all", "regime 2018-19", "regime 2020", "regime 2021-23", "regime 2024", "regime 2025-26"]
    out = [
        "# Reliability slope by regime, from the tracked evidence of #624 (#683)", "",
        READING, "",
        f"Source: `{result['source']}`. Points only: that file carries no interval for a regime's slope. The slope is that of the logistic fit of "
        "the outcome on logit(forecast) on the days that are not risk dates where the forecast is above 1e-4 (1 is reliable); `undefined` is a regime with no pressure day; `–` a "
        "regime whose forecast is constant or whose fit is not formed; `unstable` a near-separated fit (a slope beyond 25 in size); `†` a cell with "
        "fewer than 5 pressure days, whose slope is a handful of events' worth.", "",
    ]
    for row, leads in result["rows"].items():
        out += [
            f"## `{row}`", "",
            "| lead | " + " | ".join(c if c != "all" else "all days (pooled)" for c in columns) + " |",
            "|---|" + "---|" * len(columns),
        ]
        for h, cells in sorted(leads.items(), key=lambda kv: int(kv[0])):
            out.append(f"| {h} | " + " | ".join(_slope_text(cells.get(c)) for c in columns) + " |")
        out.append("")
    return "\n".join(out)


# -- kinked: #626's rows, refitted within regimes ------------------------------------------------------------------


def kinked_command(args) -> int:
    k = _kinked()
    declared = k.declared_document()
    end = date.fromisoformat(declared["scoring"]["last_day"])
    require_unlocked([end], where="reliability_regimes_683")
    judge_script = k._load("pressure_judge")
    judge_script.require_committed_declaration(pj.DEFAULT_DECLARATION)
    base = pj.load_declaration()
    splits = load_split_declaration(SPLITS)
    published = load_daily_panel(args.published)
    states = {h: judge_script._scarcity_states(h, base.last_day) for h in base.horizons}
    names = [
        "structural_liquidity", "structural_liquidity+h41", "structural_kinked_fitted", "structural_kinked_rolling",
        k.OFF, k.COMPARATOR, base.persistence, base.climatology,
    ]
    result: Dict[str, dict] = {}
    for h in base.horizons:
        columns: Dict[str, Dict[str, float]] = {}
        for template in (args.bench, args.parents, args.rows):
            doc = json.loads(Path(template.format(h=h)).read_text())
            for name, column in doc["forecasts"].items():
                if name in names:
                    columns.setdefault(name, column[f"{base.primary:g}"])
        days = sorted(date.fromisoformat(d) for d in columns[base.climatology])
        grid = pj.build_grid(base, h, published, days, splits, scarcity_state=states[h])
        keep = [i for i, label in enumerate(grid.groups["risk_date"]) if label == "0"]
        outcome = [grid.outcomes[base.primary][i] for i in keep]
        regime = [rr.regime_of(days[i]) for i in keep]
        state = [f"scarcity state {grid.groups['scarcity_state'][i]}" for i in keep]
        rows: Dict[str, dict] = {}
        for n in names:
            p = [columns[n][days[i].isoformat()] for i in keep]
            settings = dict(
                block_length=base.block_length, seed=base.seed + h, replications=args.replications or base.replications, level=base.level
            )
            rows[n] = {
                "regime": _cells_json(rr.by_cell(p, outcome, regime, **settings)),
                "scarcity_state": _cells_json(rr.by_cell(p, outcome, state, **settings)),
            }
        result[str(h)] = {"days": len(keep), "events": sum(outcome), "rows": rows}
        print(json.dumps({"horizon": h, "off_risk_days": len(keep)}), flush=True)
    out = {"level": base.level, "replications": args.replications or base.replications, "block_length": base.block_length, "reading": READING, "horizons": result}
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(kinked_text(out), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _cells(d: Dict[str, dict]) -> Dict[str, rr.Cell]:
    return {
        key: rr.Cell(
            v["days"], v["events"], v["slope"], v["intercept"],
            None if v["slope_interval"] is None else tuple(v["slope_interval"]),
            None if v["intercept_interval"] is None else tuple(v["intercept_interval"]),
        )
        for key, v in d.items()
    }


def kinked_text(result: dict) -> str:
    out = [
        "# Reliability slope within regimes, #626's rows on the days that are not risk dates (#683)", "",
        READING, "",
        f"Intercept and slope of `logit P(y = 1) = intercept + slope * logit(p)` (1 and 0 for a reliable forecast), "
        f"{round(result['level'] * 100)}% stationary-bootstrap intervals (block length {result['block_length']}, {result['replications']} "
        "replications); `undefined` where the cell has no pressure day or the forecast is constant there; no interval where the cell has too "
        "few events to give one. Regimes: 2018-19, 2020-24 (which holds 2021-23, with no pressure day) and 2025-26.", "",
    ]
    for h, body in sorted(result["horizons"].items(), key=lambda kv: int(kv[0])):
        out += [f"## h = {h}: {body['days']} days, {body['events']} above +5 bp", ""]
        for row, split in body["rows"].items():
            out += [f"### `{row}`", "", "By regime.", "", rr.markdown_table(_cells(split["regime"]), level=result["level"]),
                    "By as-of scarcity state.", "", rr.markdown_table(_cells(split["scarcity_state"]), level=result["level"])]
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("tracked")
    p.add_argument("--evidence", type=Path, default=STEP2)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("kinked")
    p.add_argument("--published", type=Path, required=True)
    for name in ("bench", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p.add_argument("--replications", type=int, help="override the declaration's bootstrap replications (a smoke run; a record uses the declared number)")
    args = parser.parse_args(argv)
    return {"tracked": tracked_command, "kinked": kinked_command}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
