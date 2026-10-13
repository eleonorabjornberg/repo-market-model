"""Audit of the partly announced bill-class rules (#679, finding #665; H2 and H5 inputs).

Compares four readings of a settlement day's net, as announced at a decision day `t` a lead
`h` business days before the settlement day `s`, with the completed net of `s` (every auction
of the day announced; the figure the day finally drains):

* `old`: the class nets its offerings announced by `t` against the class's maturing figure;
* `announced`: a partly announced class nets its announced offerings against nothing (the rule
  of #620 / #647 as first merged);
* `left_out`: a partly announced class is left out until it is fully announced (the rule in force);
* `completed`: the target.

Two populations are reported: the (day, lead 1-5) cases the net columns read (#665's), and the
(settlement day, class, decision day) groups (#647's). Run:

    PYTHONPATH=src python3 scripts/partly_announced_679.py [--write]

`--write` writes `docs/pivot/evidence/partly-announced/audit.json` and `audit.md`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from statistics import mean

from repo_model import net_settlement as ns
from repo_model.data import next_business_day

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = ROOT / "metadata" / "net_settlement.json"
SNAPSHOT = (
    ROOT / "tests" / "fixtures" / "snapshots" / "net_settlement_inputs" / "treasury_auctions"
    / "20261008T205048Z_568c69347867.json"
)
OUT = ROOT / "docs" / "pivot" / "evidence" / "partly-announced"
RULES = ("old", "announced", "left_out")
LEADS = (1, 2, 3, 4, 5)
WORST = ("2018-10-04", "2024-11-26", "2025-04-08", "2023-08-22", "2021-10-07")


def group_value(members, everything, rule):
    """One class's net under `rule`; `members` are announced by the instant, `everything` all of the day's."""

    figures = [a.maturing for a in members if a.maturing is not None]
    partly = len(members) < len(everything)
    offering = sum(a.offering for a in members)
    maturing = max(figures) if figures else 0.0
    if rule == "old" or not partly:
        return offering - maturing
    return offering if rule == "announced" else 0.0


def net(auctions, instant, rule):
    """The day's net under `rule`, all classes, as announced by `instant`."""

    total = 0.0
    for is_bill in (True, False):
        everything = [a for a in auctions if a.is_bill == is_bill]
        members = [a for a in everything if a.announced_at <= instant]
        if members:
            total += group_value(members, everything, rule)
    return total


def decision_days(settles, lead):
    """The decision days `t` with `next_business_day(t, lead) == settles` (business days only)."""

    out = []
    probe = settles - timedelta(days=lead + 6)
    while probe < settles:
        if next_business_day(probe, lead) == settles and next_business_day(probe - timedelta(days=1), 1) == probe:
            out.append(probe)
        probe += timedelta(days=1)
    return out


def cases(auctions, declaration):
    by_day = defaultdict(list)
    for a in auctions:
        by_day[a.settles].append(a)
    announce = time.fromisoformat(declaration["announcement_time"])
    rows = []
    for s, day_auctions in sorted(by_day.items()):
        full = {r: net(day_auctions, datetime.combine(s, time(23, 59)), "old") for r in ("old",)}["old"]
        for lead in LEADS:
            for t in decision_days(s, lead):
                instant = datetime.combine(t, announce)
                partly = [
                    bill
                    for bill in (True, False)
                    if 0
                    < len([a for a in day_auctions if a.is_bill == bill and a.announced_at <= instant])
                    < len([a for a in day_auctions if a.is_bill == bill])
                ]
                row = {"settles": s.isoformat(), "decision": t.isoformat(), "lead": lead, "completed": full,
                       "partly": [("bill" if b else "coupon") for b in partly]}
                for rule in RULES:
                    row[rule] = net(day_auctions, instant, rule)
                rows.append(row)
    return rows


def stats(rows, rule):
    errors = [r[rule] - r["completed"] for r in rows]
    return {"n": len(errors), "mean_error": mean(errors) if errors else None,
            "mae": mean(abs(e) for e in errors) if errors else None}


def group_cases(auctions, declaration):
    """#647's population: (settlement day, class, decision day) groups that are partly announced."""

    by_day = defaultdict(list)
    for a in auctions:
        by_day[a.settles].append(a)
    announce = time.fromisoformat(declaration["announcement_time"])
    out = []
    for s, day_auctions in sorted(by_day.items()):
        for bill in (True, False):
            everything = [a for a in day_auctions if a.is_bill == bill]
            figures = [a.maturing for a in everything if a.maturing is not None]
            complete = sum(a.offering for a in everything) - (max(figures) if figures else 0.0)
            for t in sorted({a.announced_at.date() for a in everything}):
                members = [a for a in everything if a.announced_at <= datetime.combine(t, announce)]
                if 0 < len(members) < len(everything):
                    out.append({"settles": s, "bill": bill, "decision": t,
                                **{r: group_value(members, everything, r) - complete for r in RULES}})
    return out


def build():
    declaration = ns.load_declaration(DECLARATION)
    auctions = ns.load_snapshot(SNAPSHOT, declaration)
    rows = cases(auctions, declaration)
    differ = [r for r in rows if r["partly"]]
    result = {"fixture": str(SNAPSHOT.relative_to(ROOT)), "rules": list(RULES), "day_lead_cases": {
        "all": len(rows), "partly_announced": len(differ),
        "by_rule_leads_2_to_5": {r: stats([x for x in differ if x["lead"] >= 2], r) for r in RULES},
        "by_rule_all_leads": {r: stats(differ, r) for r in RULES},
        "by_lead": {str(h): {r: stats([x for x in differ if x["lead"] == h], r) for r in RULES} for h in LEADS},
        "by_lead_all_cases": {str(h): {r: stats([x for x in rows if x["lead"] == h], r) for r in RULES} for h in LEADS},
        "by_year_leads_4_5": {},
    }}
    years = defaultdict(list)
    for r in differ:
        if r["lead"] >= 4:
            years[r["decision"][:4]].append(r)
    result["day_lead_cases"]["by_year_leads_4_5"] = {y: {"n": len(v), **{r: stats(v, r) for r in RULES}} for y, v in sorted(years.items())}
    groups = group_cases(auctions, declaration)
    result["groups"] = {"n": len(groups), **{r: {"mean_error": mean(g[r] for g in groups), "mae": mean(abs(g[r]) for g in groups)} for r in RULES}}
    result["worst_cases"] = [
        {k: x[k] for k in ("settles", "decision", "lead", "partly", "completed", *RULES)}
        for x in sorted(differ, key=lambda x: -abs(x["announced"] - x["completed"]))[:15]
    ]
    result["named_cases"] = [
        {k: x[k] for k in ("settles", "decision", "lead", "partly", "completed", *RULES)}
        for x in differ if x["settles"] in WORST
    ]
    return result


def fmt(value):
    return "n/a" if value is None else f"{value:+.1f}"


def unsigned(value):
    return "n/a" if value is None else f"{value:.1f}"


def markdown(result):
    d = result["day_lead_cases"]
    lines = ["# Partly announced bill classes: audit (#679, finding #665)", "",
             "Generated by `scripts/partly_announced_679.py`; do not edit by hand.", "",
             f"Fixture: `{result['fixture']}`. Error = rule's net less the completed day's net (USD bn).", "",
             f"## #665's population: (day, lead) cases a partly announced class changes", "",
             f"{d['partly_announced']} of {d['all']} (day, lead 1-5) cases have a partly announced class.", "",
             "| leads | rule | n | mean error | MAE |", "|---|---|---|---|---|"]
    for label, key in (("2-5", "by_rule_leads_2_to_5"), ("1-5", "by_rule_all_leads")):
        for r in RULES:
            s = d[key][r]
            lines.append(f"| {label} | {r} | {s['n']} | {fmt(s['mean_error'])} | {unsigned(s['mae'])} |")
    lines += ["", "## By lead (cases with a partly announced class)", "", "| lead | rule | n | mean error | MAE |", "|---|---|---|---|---|"]
    for h in LEADS:
        for r in RULES:
            s = d["by_lead"][str(h)][r]
            lines.append(f"| {h} | {r} | {s['n']} | {fmt(s['mean_error'])} | {unsigned(s['mae'])} |")
    lines += ["", "## By lead (all cases, the figure the columns read)", "", "| lead | rule | n | mean error | MAE |", "|---|---|---|---|---|"]
    for h in LEADS:
        for r in RULES:
            s = d["by_lead_all_cases"][str(h)][r]
            lines.append(f"| {h} | {r} | {s['n']} | {fmt(s['mean_error'])} | {unsigned(s['mae'])} |")
    lines += ["", "## By decision year, leads 4-5", "", "| year | n | announced MAE | left_out MAE | old MAE |", "|---|---|---|---|---|"]
    for y, v in d["by_year_leads_4_5"].items():
        lines.append(f"| {y} | {v['n']} | {unsigned(v['announced']['mae'])} | {unsigned(v['left_out']['mae'])} | {unsigned(v['old']['mae'])} |")
    g = result["groups"]
    lines += ["", "## #647's population: (settlement day, class, decision day) groups", "",
              f"{g['n']} partly announced groups, error against the class's completed net.", "",
              "| rule | mean error | MAE |", "|---|---|---|"]
    for r in RULES:
        lines.append(f"| {r} | {fmt(g[r]['mean_error'])} | {unsigned(g[r]['mae'])} |")
    for title, key in (("Worst cases by the announced-rule error", "worst_cases"), ("The cases the finding names", "named_cases")):
        lines += ["", f"## {title}", "", "| settles | decision | lead | partly | completed | old | announced | left_out |", "|---|---|---|---|---|---|---|---|"]
        for x in result[key]:
            lines.append(f"| {x['settles']} | {x['decision']} | {x['lead']} | {','.join(x['partly'])} | {x['completed']:.1f} | {x['old']:.1f} | {x['announced']:.1f} | {x['left_out']:.1f} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    text = markdown(result)
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "audit.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        (OUT / "audit.md").write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
