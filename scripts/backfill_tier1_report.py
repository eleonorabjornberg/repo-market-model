"""The tables of the tier-1 back-fill measurement (#484), from the judge's result and the recorded runs.

A scratch measurement, not a record: it writes Markdown (and JSON) to the paths it is given and nothing into
`docs/runs/`. Declared in `metadata/backfill_tier1.json` before any score.

    PYTHONPATH=src python3 scripts/backfill_tier1_report.py --judge OUT/judge.json --runs OUT \\
        --published PUB.csv --extended EXTAUG.csv --output OUT/tables.md --json OUT/training.json

`--runs` holds `<arm>_<model>_h<h>.folds.json` and `.pairs.json` as `backfill_history.py run` wrote them (`arm` is
`with` or `without`).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import pressure, setup_diagnostic  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

DECLARATION = REPO / "metadata" / "backfill_tier1.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SUFFIX = "+history"
CALLED_OUT = ("2018", "2020", "2024")


def _f(value, digits=3):
    return "–" if value is None else f"{value:.{digits}f}"


def _cell(cell, digits=3, signed=False):
    """A bootstrap cell as `mean [lower, upper]`."""

    if cell is None or cell.get("mean") is None:
        return "–"
    sign = "+" if signed else ""
    shown = f"{cell['mean']:{sign}.{digits}f}"
    interval = cell.get("interval")
    return shown + (f" [{interval['lower']:{sign}.{digits}f}, {interval['upper']:{sign}.{digits}f}]" if interval else " (no interval)")


def _yes(value):
    return "yes" if value else "no"


def judge_rows(result, models):
    lines = [
        "| model | history | onsets flagged | recall [90%] | worst false alarms per onset (weighted; flat) | tier 1 | tier 3 | tier 5 | pass |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for model in models:
        for label, name in (("without", model), ("with", model + SUFFIX)):
            candidate = result["candidates"][name]
            verdict = candidate["verdict"]
            near = candidate["tiers"]["onset_warning"]["lead_at_least_1"]
            weighted = near.get("worst_weighted_false_alarms_per_onset")
            lines.append(
                f"| {model} | {label} | {near['onsets_flagged']:g} of {near['onsets']} | {_cell(near['recall'])} | "
                f"{_f(weighted, 2)}; {_f(near['worst_false_alarms_per_onset'], 2)} | {_yes(verdict['tier_1_onset_warning'])} | "
                f"{_yes(verdict['tier_3_no_crying_wolf'])} | {_yes(verdict['tier_5_week_ahead'])} | {_yes(verdict['passes'])} |"
            )
    return lines


def paired_rows(result, models):
    lines = [
        "| model | recall with | recall without | recall difference (with − without) | " + " | ".join(
            f"Brier difference h = {h}" for h in range(1, 6)
        ) + " |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for model in models:
        entry = result["paired_history"][model]
        lines.append(
            f"| {model} | {_cell(entry['recall_with'])} | {_cell(entry['recall_without'])} | "
            f"{_cell(entry['recall_difference'], signed=True)} | "
            + " | ".join(_cell(entry["brier_difference_by_horizon"][str(h)], digits=5, signed=True) for h in range(1, 6))
            + " |"
        )
    return lines


def recall_by_year(result, models):
    years = sorted({y for m in models for y in result["onset_recall_by_year"][m]})
    lines = [
        "| model | history | " + " | ".join(f"**{y}**" if y in CALLED_OUT else y for y in years) + " | all |",
        "|---|---|" + "---|" * (len(years) + 1),
    ]
    for model in models:
        for label, name in (("without", model), ("with", model + SUFFIX)):
            by = result["onset_recall_by_year"][name]
            cells = [f"{by[y]['flagged']}/{by[y]['onsets']}" if y in by else "–" for y in years]
            flagged = sum(v["flagged"] for v in by.values())
            total = sum(v["onsets"] for v in by.values())
            lines.append(f"| {model} | {label} | " + " | ".join(cells) + f" | {flagged}/{total} |")
    return lines


def alarms_by_year(result, models, *, weighted):
    key = "weighted" if weighted else "flat"
    years = sorted({y for m in models for y in result["onset_recall_by_year"][m]})
    lines = [
        "| model | history | " + " | ".join(f"**{y}**" if y in CALLED_OUT else y for y in years) + " |",
        "|---|---|" + "---|" * len(years),
    ]
    for model in models:
        for label, name in (("without", model), ("with", model + SUFFIX)):
            cells = []
            for y in years:
                onsets = result["onset_recall_by_year"][name].get(y, {}).get("onsets", 0)
                per_h = result["false_alarms_by_year"][name].get(y, {})
                worst = max((c[key] for c in per_h.values()), default=0)
                cells.append(f"{worst / onsets:.2f}" if onsets else "–")
            lines.append(f"| {model} | {label} | " + " | ".join(cells) + " |")
    return lines


def _block(folds, day):
    """The refit block that scores `day`, or None when the horizon does not score it."""

    for block in folds:
        if block["first_scored"] <= day.isoformat() <= block["last_scored"]:
            return block
    return None


def _risk_date(splits, values, horizon):
    """The declared risk-date rule (`metadata/risk_date_severity.json`), read off a panel row."""

    if splits.day_type(values) != "ordinary":
        return True
    return horizon == 1 and float(values.get("treasury_settlement_coupons") or 0.0) > 0.0


def training_history(runs, published, extended, horizons=(1, 5)):
    """For each 2018 onset: the refit in force and what its training window holds, without and with the back-fill.

    The window is the fold's own (`train_start` to `train_end`). It holds `pressure_days` days above +5 bp and
    `onsets` episodes (`setup_diagnostic.training_counts`); `risk_date_pressure_days` of the pressure days are
    risk dates, which is what a risk-date model trains on.
    """

    from repo_model.data import exceeds_bp  # the strict whole-basis-point reading

    splits = load_split_declaration(SPLITS)
    pub_rows = load_daily_panel(published)
    ext_rows = load_daily_panel(extended)
    probe = json.loads((runs / "without_risk_gbm_base_h1.folds.json").read_text())
    first, last = date.fromisoformat(probe[0]["first_scored"]), date(2018, 12, 31)
    scored = [row.date for row in pub_rows if first <= row.date <= last]
    onsets = pressure.onsets(pub_rows, 5.0, scored)
    out = []
    for day in onsets:
        entry = {"onset": day.isoformat(), "horizons": {}}
        for h in horizons:
            cell = {}
            for arm, rows in (("without", pub_rows), ("with", ext_rows)):
                folds = json.loads((runs / f"{arm}_risk_gbm_base_h{h}.folds.json").read_text())
                block = _block(folds, day)
                if block is None:
                    continue
                days = [row.date for row in rows]
                begin = days.index(date.fromisoformat(block["train_start"]))
                end = days.index(date.fromisoformat(block["train_end"]))
                window = rows[begin : end + 1]
                counts = setup_diagnostic.training_counts(
                    [r.date for r in window],
                    [float(r.spread_bps) for r in window],
                    last=window[-1].date,
                    tau=5.0,
                    calm=pressure.ONSET_QUIET_DAYS,
                )
                risk = sum(
                    1 for r in window if exceeds_bp(float(r.spread_bps), 5.0) and _risk_date(splits, r.values, h)
                )
                cell[arm] = {
                    "train_start": block["train_start"],
                    "train_end": block["train_end"],
                    "train_rows": block["train_rows"],
                    "pressure_days": counts["pressure_days"],
                    "onsets": counts["onsets"],
                    "risk_date_pressure_days": risk,
                }
            if cell:
                entry["horizons"][str(h)] = cell
        out.append(entry)
    return out


def training_rows(history):
    lines = [
        "| 2018 onset | h | refit window with → end | rows without / with | pressure days without / with | onsets without / with | pressure days on risk dates without / with |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in history:
        for h, cell in entry["horizons"].items():
            w, b = cell["without"], cell["with"]
            lines.append(
                f"| {entry['onset']} | {h} | {b['train_start']} → {b['train_end']} | {w['train_rows']} / {b['train_rows']} | "
                f"{w['pressure_days']} / {b['pressure_days']} | {w['onsets']} / {b['onsets']} | "
                f"{w['risk_date_pressure_days']} / {b['risk_date_pressure_days']} |"
            )
    return lines


def rows_used(runs, models, horizons=(1, 2, 3, 4, 5)):
    """Per model and horizon: the back-filled rows of the last fit, of which the ones that trained a pair."""

    lines = [
        "| model | h | back-filled rows in the training frame | back-filled label days that trained a pair | of them risk dates (what the fit uses) | all pairs in the last fit |",
        "|---|---|---|---|---|---|",
    ]
    table = {}
    for model in models:
        for h in horizons:
            document = json.loads((runs / f"with_{model}_h{h}.pairs.json").read_text())
            last = document["fits"][max(document["fits"])]
            table[f"{model}/h{h}"] = {"backfilled_rows": document["backfilled_rows"], **last}
            lines.append(
                f"| {model} | {h} | {document['backfilled_rows']} | {last['backfilled_pairs']} | "
                f"{last['backfilled_risk_date_pairs']} | {last['pairs']} |"
            )
    return lines, table


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--judge", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--published", type=Path, required=True)
    parser.add_argument("--extended", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    declared = json.loads(DECLARATION.read_text(encoding="utf-8"))
    models = declared["models"]
    result = json.loads(args.judge.read_text(encoding="utf-8"))
    history = training_history(args.runs, args.published, args.extended)
    used_lines, used = rows_used(args.runs, models)
    sections = [
        ("Table 1. The judge row, with and without the back-filled history (tiers 1, 3 and 5, under the rule in force)", judge_rows(result, models)),
        ("Table 2. Paired, with against without (recall: onsets flagged at some lead 1 to 5; Brier difference on all scored days at +5 bp, positive: the history helps), 90% stationary-bootstrap intervals", paired_rows(result, models)),
        ("Table 3. +5 bp onsets flagged at some lead 1 to 5, by calendar year of the onset", recall_by_year(result, models)),
        ("Table 4. False alarms per onset by calendar year, at the worst horizon, under the weighted miss rule in force", alarms_by_year(result, models, weighted=True)),
        ("Table 5. The same, flat count", alarms_by_year(result, models, weighted=False)),
        ("Table 6. Training history at each 2018 onset (refit in force, window, what it holds), without and with the back-fill", training_rows(history)),
        ("Table 7. Back-filled rows each model actually used (last fit)", used_lines),
    ]
    text = "\n".join(f"{title}\n\n" + "\n".join(lines) + "\n" for title, lines in sections)
    args.output.write_text(text, encoding="utf-8")
    if args.json:
        args.json.write_text(json.dumps({"training_history": history, "rows_used": used}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
