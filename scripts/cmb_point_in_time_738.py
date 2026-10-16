"""Cash management bills read point in time: what the rule of #738 changes (H5 step 2's settlement family, and H6).

Development exploration only: nothing here is a verdict (scoring protocol v1, #640). Compares, on the tracked
auctions fixture and as #679's audit did, a settlement day's net as announced at a decision day `t` a lead `h`
business days before it with the completed net of the day, under two readings of a class's partial status:

* `before`: the rule of #679 as merged, where whether a bill class is partly announced is read from the day's
  whole auction list, cash management bills (CMBs) announced later included, which is look-ahead (#738);
* `after`: the rule in force, where a CMB counts only from its own announcement.

It also rebuilds `projected_reserves.ahead_columns` both ways and counts the cells that move, and splits every
comparison by the declared regime of the decision day (`metadata/evaluation_splits.json`). Run:

    PYTHONPATH=src python3 scripts/cmb_point_in_time_738.py [--write]

`--write` writes `docs/pivot/evidence/cmb-point-in-time-738/result.json` and `result.md`.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from statistics import mean

from repo_model import net_settlement as ns
from repo_model import projected_reserves as pr
from repo_model.data import DailyObservation, next_business_day
from repo_model.evaluation_splits import load_split_declaration
from repo_model.lockbox import require_unlocked

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "pivot" / "evidence" / "cmb-point-in-time-738"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
LEADS = (1, 2, 3, 4, 5)
#: The development span: the first declared regime day to the last day of the opened near-blind tier
#: (`metadata/lockbox.json`). No day from 2026-09-04 is read; `require_unlocked` refuses one.
FIRST_DAY = date(2018, 1, 1)
LAST_DAY = date(2026, 9, 3)

_spec = importlib.util.spec_from_file_location("partly_announced_679", ROOT / "scripts" / "partly_announced_679.py")
audit = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = audit
_spec.loader.exec_module(audit)


def case_rows(auctions, declaration, splits):
    """Every (settlement day, lead, decision day) case: both readings, the completed net, the regime, the CMB role."""

    by_day = defaultdict(list)
    for a in auctions:
        by_day[a.settles].append(a)
    announce = time.fromisoformat(declaration["announcement_time"])
    rows = []
    for s, day in sorted(by_day.items()):
        if not FIRST_DAY <= s <= LAST_DAY:
            continue
        completed = audit.net(day, datetime.combine(s, time(23, 59)), "old")
        for lead in LEADS:
            for t in audit.decision_days(s, lead):
                if t < FIRST_DAY:
                    continue
                require_unlocked([t, s], where="scripts/cmb_point_in_time_738.py")
                instant = datetime.combine(t, announce)
                before = audit.net(day, instant, "left_out")
                after = audit.net(day, instant, "left_out_pit")
                rows.append({
                    "settles": s.isoformat(), "decision": t.isoformat(), "lead": lead, "regime": splits.regime(t),
                    "completed": completed, "before": before, "after": after,
                    "cmb_only_partial": abs(before - after) > 1e-9,
                })
    return rows


def stats(rows, rule):
    errors = [r[rule] - r["completed"] for r in rows]
    return {"n": len(errors), "mean_error": mean(errors) if errors else None,
            "mae": mean(abs(e) for e in errors) if errors else None}


def table(rows):
    return {"before": stats(rows, "before"), "after": stats(rows, "after")}


def ahead_cells(auctions, declaration):
    """Cells of `ahead_columns` that move when a CMB is read from its announcement, by regime and in all."""

    by_day = ns._by_day(auctions)
    splits = load_split_declaration(SPLITS)
    rows, day = [], next_business_day(FIRST_DAY - timedelta(days=1), 1)
    while day <= LAST_DAY:
        rows.append(DailyObservation(day, {}))
        day = next_business_day(day, 1)
    require_unlocked([r.date for r in rows], where="scripts/cmb_point_in_time_738.py")
    new = pr.ahead_columns(rows, auctions, declaration)
    changed, by_regime, by_year, largest = 0, defaultdict(int), defaultdict(int), []
    for row, built in zip(rows, new):
        instant = ns._instant(row.date, declaration)
        total, day = 0.0, row.date
        for name in pr.AHEAD_COLUMNS:
            day = next_business_day(day, 1)
            total += ns.net_for_day(by_day.get(day, ()), instant, future_cmb=True)[0]
            gap = built.values[name] - total
            if abs(gap) > 1e-9:
                changed += 1
                by_regime[splits.regime(row.date)] += 1
                by_year[str(row.date.year)] += 1
                largest.append((abs(gap), row.date.isoformat(), name, total, built.values[name]))
    largest.sort(reverse=True)
    return {
        "cells_checked": len(rows) * len(pr.AHEAD_COLUMNS), "cells_changed": changed,
        "by_regime": dict(sorted(by_regime.items())), "by_year": dict(sorted(by_year.items())),
        "largest": [{"day": d, "column": c, "before": round(b, 1), "after": round(a, 1)} for _, d, c, b, a in largest[:5]],
    }


def build():
    declaration = ns.load_declaration(audit.DECLARATION)
    auctions = ns.load_snapshot(audit.SNAPSHOT, declaration)
    splits = load_split_declaration(SPLITS)
    rows = case_rows(auctions, declaration, splits)
    cmb_cases = [r for r in rows if r["cmb_only_partial"]]
    regimes = splits.regime_labels
    return {
        "fixture": str(audit.SNAPSHOT.relative_to(ROOT)),
        "cases": len(rows),
        "cases_where_a_late_cmb_alone_made_a_class_partial": len(cmb_cases),
        "all_cases": table(rows),
        "cmb_cases": table(cmb_cases),
        "cmb_cases_by_year": {y: table([r for r in cmb_cases if r["decision"][:4] == y])
                              for y in sorted({r["decision"][:4] for r in cmb_cases})},
        "all_cases_by_regime": {g: table([r for r in rows if r["regime"] == g]) for g in regimes
                                if any(r["regime"] == g for r in rows)},
        "cmb_cases_by_regime": {g: table([r for r in cmb_cases if r["regime"] == g]) for g in regimes
                                if any(r["regime"] == g for r in cmb_cases)},
        "cmb_cases_by_lead": {str(h): table([r for r in cmb_cases if r["lead"] == h]) for h in LEADS},
        "ahead_columns": ahead_cells(auctions, declaration),
    }


def fmt(v):
    return "n/a" if v is None else f"{v:.1f}"


def _rows(name, tables):
    lines = []
    for key, t in tables.items():
        lines.append(f"| {name} {key} | {t['before']['n']} | {fmt(t['before']['mean_error'])} | {fmt(t['before']['mae'])} | "
                     f"{fmt(t['after']['mean_error'])} | {fmt(t['after']['mae'])} |")
    return lines


def markdown(r):
    a = r["ahead_columns"]
    lines = ["# Cash management bills, point in time (#738)", "",
             "Generated by `scripts/cmb_point_in_time_738.py`; do not edit by hand. Development exploration "
             "(scoring protocol v1, #640): no verdict.", "",
             f"Fixture: `{r['fixture']}`. Error = a reading's net less the completed day's net (USD bn). `before` is the "
             "rule of #679 as merged (a later CMB makes a class partial); `after` reads a CMB only from its own "
             "announcement.", "",
             f"{r['cases_where_a_late_cmb_alone_made_a_class_partial']} of {r['cases']} (day, lead 1-5) cases change.", "",
             "| cases | n | before mean error | before MAE | after mean error | after MAE |", "|---|---|---|---|---|---|"]
    lines += _rows("all cases", {"": r["all_cases"]}) + _rows("changed cases", {"": r["cmb_cases"]})
    lines += _rows("changed, regime", r["cmb_cases_by_regime"]) + _rows("changed, year", r["cmb_cases_by_year"])
    lines += _rows("changed, lead", r["cmb_cases_by_lead"]) + _rows("all cases, regime", r["all_cases_by_regime"])
    lines += ["", "## `projected_reserves.ahead_columns`", "",
              f"{a['cells_changed']} of {a['cells_checked']} cells move. By regime: {a['by_regime']}. By year: {a['by_year']}.", "",
              "| day | column | before | after |", "|---|---|---|---|"]
    lines += [f"| {x['day']} | {x['column']} | {x['before']} | {x['after']} |" for x in a["largest"]]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    text = markdown(result)
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        (OUT / "result.md").write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
