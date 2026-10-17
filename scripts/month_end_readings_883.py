"""The two month-end readings, measured side by side (#883, H5 groundwork G1 / step 3).

A scratch measurement, not a record: it changes no definition, no default and no page. `repo_model.risk_dates` keeps two readings of the
month-end part of a day type: the split declaration's window (`SplitDeclaration.day_type`: `days_to_month_end` at most
`month_end_window` calendar days) and the reporting reading (`SplitDeclaration.reporting_day_type`: one of the month's last two business
days, `data.in_last_business_days_of_month`). Which one is shared is Eleonora's open ruling (#800). This script lists the days on which
they disagree and re-reads the ordinary-day headlines of four pages under both. It recommends nothing.

Development data, not a verdict (scoring protocol v1, #640). No day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/month_end_readings_883.py days --published PUBLISHED.csv --output days.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

SPLITS = REPO / "metadata" / "evaluation_splits.json"
LAST_DAY = date(2025, 12, 31)
#: a pressure day, for the list only: the spread, on whole basis points, above this (`data.exceeds_bp`).
PRESSURE_BP = 5.0
WINDOW, REPORTING = "window", "reporting"


def reading_type(splits, reading: str, row) -> str:
    """The pressure-day type of `row` under one reading."""

    if reading == WINDOW:
        return splits.day_type(row.values)
    if reading == REPORTING:
        return splits.reporting_day_type(row.date, row.values)
    raise ValueError(f"unknown reading {reading!r}; use {WINDOW!r} or {REPORTING!r}")


def disagreeing_days(rows, splits):
    """Every panel day up to `LAST_DAY` whose day type differs between the two readings."""

    out = []
    for row in rows:
        if row.date > LAST_DAY:
            continue
        window, reporting = reading_type(splits, WINDOW, row), reading_type(splits, REPORTING, row)
        if window == reporting:
            continue
        spread = row.spread_bps
        out.append({
            "date": row.date.isoformat(),
            "window": window,
            "reporting": reporting,
            "month_end_by": ("both" if "month_end" in (window, reporting) and window == reporting else
                              "window only" if window == "month_end" else "reporting only"),
            "spread_bp": None if spread is None else round(float(spread), 3),
            "pressure_day": None if spread is None else bool(exceeds_bp(spread, PRESSURE_BP)),
        })
    return out


def summarise(days):
    by_year = Counter(d["date"][:4] for d in days)
    by_type = Counter(f"{d['window']} -> {d['reporting']}" for d in days)
    return {"days": len(days), "by_year": dict(sorted(by_year.items())), "by_type": dict(by_type),
            "pressure_days": sum(1 for d in days if d["pressure_day"])}


# -- the headline figures --------------------------------------------------------------------------------------------------


def dig(document, *path):
    """The value at `path`, or `None` where the document has no such entry."""

    for key in path:
        if not isinstance(document, dict) or key not in document:
            return None
        document = document[key]
    return document


def skill(entry, lower=("skill_interval", 0), upper=("skill_interval", 1)):
    """One paired skill with its interval and day count: `{skill, lo, hi, days}`; the interval of the page being re-read."""

    if entry is None:
        return None
    lo = entry.get(lower[0])
    hi = entry.get(upper[0])
    return {"skill": entry.get("skill"), "lo": None if lo is None else lo[lower[1]] if isinstance(lo, list) else lo,
            "hi": None if hi is None else hi[upper[1]] if isinstance(hi, list) else hi,
            "days": entry.get("days", entry.get("n"))}


def one_sided(entry):
    """#805's tests carry a one-sided 95% lower and upper bound."""

    if entry is None:
        return None
    return {"skill": entry.get("skill"), "lo": entry.get("skill_lower_95_one_sided"), "hi": entry.get("skill_upper_95_one_sided"),
            "days": entry.get("n")}


def figures_805(doc):
    out = {}
    for metric in ("grid_crps", "upper_tail_twcrps"):
        for candidate, groups in (dig(doc, "headlines", metric) or {}).items():
            for group in ("pooled", "anchor:ordinary", "anchor:month_end"):
                tests = dig(groups, group, "tests") or {}
                out[f"{metric}, {candidate}, {group}, vs B1"] = one_sided(tests.get(f"B1 -> {candidate}"))
    out["anchor day types (decision days)"] = dig(doc, "anchor_day_types")
    return out


def figures_761(doc):
    out = {}
    groups = (("all decision days", ("pooled", "all decision days")), ("target day ordinary", ("pressure_day_type", "ordinary")),
              ("anchor ordinary", ("anchor_day_type", "ordinary")), ("anchor month-end", ("anchor_day_type", "month_end")),
              ("target month-end", ("pressure_day_type", "month_end")),
              ("ordinary after an ordinary day", ("context", "ordinary after an ordinary day")),
              ("ordinary after a risk day", ("context", "ordinary after a risk day")), ("risk day", ("context", "risk day")))
    for metric in ("grid_crps", "upper_tail_twcrps"):
        for label, path in groups:
            group = dig(doc["groups"], *path)
            for candidate in ("spread_mr_level10", "spread_mr_ctx", "spread_mr_b2", "spread_mr_ctx_b2"):
                out[f"{metric}, {label}, {candidate}, vs B1"] = skill(dig(group, metric, "vs", candidate, "B1"))
    return out


def figures_849(doc):
    out = {}
    for lead in ("1", "2", "3", "4", "5"):
        cells = dig(doc, "day_set", "new", "cells", lead) or {}
        out[f"risk-type cells at lead {lead}: month_end"] = cells.get("month_end")
        out[f"risk-type cells at lead {lead}: all four types"] = sum(cells.values()) if cells else None
    for page, metric in (("693", "grid_crps"), ("739", "grid_crps"), ("739", "mae")):
        for candidate in ("h5_mean_reversion", "type_state"):
            for benchmark in ("B1", "calendar"):
                entry = dig(doc, "corrected", page, "primary", metric, "vs", candidate, benchmark)
                out[f"#{page} {metric}, {candidate}, vs {benchmark}"] = skill(entry)
    out["#739 kill rule met (weaker reading)"] = dig(doc, "corrected", "739", "kill_rule", "killed_on_the_weaker_reading")
    out["#739 kill rule met"] = dig(doc, "corrected", "739", "kill_rule", "killed")
    out["control reproduces #693 / #739"] = [dig(doc, "control", "693", "reproduces"), dig(doc, "control", "739", "reproduces")]
    return out


def figures_694(doc):
    out = {}
    for ranker in ("model_prob", "model_median"):
        for metric in ("precision@3", "precision@5", "recall@3", "recall@5"):
            for benchmark in ("calendar", "climatology", "persistence"):
                entry = dig(doc, "paired", "all", ranker, metric, benchmark)
                if entry is not None:
                    out[f"{ranker}, {metric}, gain over {benchmark}"] = {
                        "skill": entry["gain"], "lo": entry["gain_interval"][0], "hi": entry["gain_interval"][1], "days": entry["days"]}
    for k in ("3", "5"):
        out[f"calendar ranker's own precision@{k} (all windows)"] = {
            "skill": dig(doc, "means", "calendar", k, "precision_all_windows"), "lo": None, "hi": None, "days": None}
    return out


EXTRACTORS = {"805": ("score", figures_805), "761": ("score", figures_761), "849": ("result", figures_849), "694": ("score", figures_694)}
TRACKED = {"805": REPORTING, "761": REPORTING, "849": REPORTING, "694": REPORTING}
TITLES = {
    "805": "#805 (the page of #820): H5 splits by the decision day's anchor type",
    "761": "#761 (the pages of #815): mean-reversion variants",
    "849": "#849 (the page of #857): H6 risk-date set, lead-flag re-read",
    "694": "#694 (the page of #819 and #770): H8 ranking",
    "758": "#758 (the page of #775): H5 candidates against H2's ceiling, ordinary targets",
}


def pct(value):
    return "n/a" if value is None else f"{100 * value:+.1f}%"


def cell(entry):
    if entry is None:
        return "-"
    if isinstance(entry, dict) and "skill" in entry:
        text = pct(entry["skill"]) if entry["skill"] is not None else "n/a"
        if entry.get("lo") is not None and entry.get("hi") is not None:
            text += f" [{pct(entry['lo'])}, {pct(entry['hi'])}]"
        if entry.get("days") is not None:
            text += f" ({entry['days']} d)"
        return text
    return str(entry)


def report_command(args) -> int:
    figures = {}
    lines = ["# Generated by `scripts/month_end_readings_883.py report`; do not edit by hand.", ""]
    for page, (stem, extract) in EXTRACTORS.items():
        loaded = {}
        for reading in (REPORTING, WINDOW):
            loaded[reading] = extract(json.loads((args.results / page / f"{stem}_{reading}.json").read_text(encoding="utf-8")))
        figures[page] = loaded
        lines += [f"## {TITLES[page]}", "", "| figure | reporting reading (business days) | window reading (calendar days) |", "|---|---|---|"]
        for key in loaded[REPORTING]:
            lines.append(f"| {key} | {cell(loaded[REPORTING][key])} | {cell(loaded[WINDOW].get(key))} |")
        lines.append("")
    args.figures.write_text(json.dumps(figures, indent=1) + "\n", encoding="utf-8")
    args.markdown.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.figures} and {args.markdown}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    report = sub.add_parser("report", help="the headline figures of each page under both readings")
    report.add_argument("--results", type=Path, required=True, help="a directory holding <page>/<file>_<reading>.json for each page")
    report.add_argument("--days", type=Path, required=True, help="the output of `days`")
    report.add_argument("--figures", type=Path, required=True, help="the extracted figures, JSON")
    report.add_argument("--markdown", type=Path, required=True)
    days = sub.add_parser("days", help="list the days on which the two readings disagree")
    days.add_argument("--published", type=Path, required=True)
    days.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "report":
        return report_command(args)
    require_unlocked([LAST_DAY], where="month_end_readings_883")
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    listed = disagreeing_days(rows, load_split_declaration(SPLITS))
    args.output.write_text(json.dumps({"summary": summarise(listed), "days": listed}, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summarise(listed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
