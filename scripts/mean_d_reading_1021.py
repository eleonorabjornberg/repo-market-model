#!/usr/bin/env python3
"""Development pages read the studentized bound on mean d, beside the skill interval (#1021; H5 reporting, for #1009).

Eleonora's ruling on #1009 (20 October 2026, relayed): a development page reports both the skill interval and the
studentized mean-d bound, and reads the mean-d bound, as ruling 1/5 reads the verdict. This script re-reads the tracked
results of #959 and #965 (`docs/research/turn-day-labels-959/result.json`, `docs/research/tax-date-october-965/result.json`)
and writes a new page for each. The original pages stand. Nothing is re-scored: the intervals are the ones in those records.

The mean-d bound: the 90% two-sided studentized interval on mean(d) is the pair of one-sided 95% bounds, the lower
`mean - q95 * se` and the upper `mean - q05 * se` (`scoring_protocol.PairedTest`). The candidate is read better when the lower bound
is above zero, worse when the upper bound is below zero, and no different otherwise.

    python3 scripts/mean_d_reading_1021.py report
    python3 scripts/mean_d_reading_1021.py check

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
RESEARCH = REPO / "docs" / "research"
SOURCES = {"959": RESEARCH / "turn-day-labels-959" / "result.json", "965": RESEARCH / "tax-date-october-965" / "result.json"}
PAGES = {"959": RESEARCH / "turn-day-labels-959-mean-d-1021-result.md",
         "965": RESEARCH / "tax-date-october-965-mean-d-1021-result.md"}
ORIGINALS = {"959": "turn-day-labels-959-result.md", "965": "tax-date-october-965-result.md"}
TITLES = {"959": "Turn-day labels against the month-end label (#959)", "965": "15 October as a tax date (#965)"}
RECORD = RESEARCH / "mean-d-reading-1021" / "result.json"
SKIP = {"comparisons", "groups", "metrics"}


def verdict_words(row: dict) -> str:
    """The reading of one tested row: the studentized bound on mean d (the verdict's), not the skill interval."""

    if "undefined" in row:
        return "scores identical" if row["difference"] == 0.0 else "undefined"
    low, high = row["difference_interval"]
    if low > 0.0:
        return "candidate better"
    if high < 0.0:
        return "candidate worse"
    return "no difference"


def skill_words(row: dict) -> str:
    """The reading the original pages gave: the skill interval."""

    if "undefined" in row:
        return verdict_words(row)
    low, high = row["skill_interval"]
    if low > 0.0:
        return "candidate better"
    if high < 0.0:
        return "candidate worse"
    return "no difference"


def collect(record: dict) -> List[dict]:
    """Every tested row of a record, in record order, with both readings. Rows the scorer left undefined carry no interval."""

    rows: List[dict] = []

    def walk(node, path):
        if not isinstance(node, dict):
            return
        if isinstance(node.get("tests"), dict):
            section = " / ".join(p for p in path[:-1] if p not in SKIP)
            count = node.get("decision_days", node.get("target_days"))
            for pair, test in node["tests"].items():
                if "undefined" in test:
                    continue
                reading, before = verdict_words(test), skill_words(test)
                rows.append({"section": section, "group": path[-1], "pair": pair, "days": count, "row": test,
                             "reading": reading, "skill_reading": before, "changed": reading != before})
            return
        for key, child in node.items():
            walk(child, path + [key])

    walk(record["comparisons"], [])
    return rows


def pct(value: float) -> str:
    return f"{100 * value:+.1f}%"


def interval(pair: Sequence[float], scale: float = 1.0, digits: int = 3) -> str:
    return f"[{pair[0] * scale:+.{digits}f}, {pair[1] * scale:+.{digits}f}]"


def _cells(r: dict) -> str:
    t = r["row"]
    return (f"{pct(t['skill'])} {interval(t['skill_interval'], 100, 1)} | {t['difference']:+.4f} "
            f"{interval(t['difference_interval'], 1, 4)}")


def render(key: str, record: dict) -> str:
    rows = collect(record)
    changed = [r for r in rows if r["changed"]]
    lines = [
        f"# {TITLES[key]}, read on the mean-d bound (#1021; H5 step 2, reporting)", "",
        "**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value "
        f"moves. Every figure is read from `docs/research/{SOURCES[key].parent.name}/result.json`, the record of the original page "
        f"(`{ORIGINALS[key]}`, which stands), by `scripts/mean_d_reading_1021.py report`.", "",
        "## What changes and why", "",
        "The original page read each row from the studentized skill interval. The skill interval and the interval on the mean "
        "difference d are built from different studentized draws, so their ends can fall on different sides of zero (#1009). The "
        "protocol's verdict reads the one-sided studentized bound on mean d (ruling 1/5). By Eleonora's ruling on #1009 this page "
        "shows both intervals for every row and reads the mean-d bound: **better** when the lower bound of mean d is above zero, "
        "**worse** when its upper bound is below zero, **no difference** otherwise. The 90% two-sided interval on mean d is the "
        "pair of one-sided 95% bounds. d = S(benchmark) − S(candidate), positive favouring the candidate; skill is mean(d) / "
        f"mean(S(benchmark)); seed {record['seed']}, {record['draws']:,} draws, as on the original page.", "",
        "**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is "
        "understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order "
        "of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here "
        "is narrower than it should be after 2020. A development reading on this page is evidence for a question, not a verdict.", "",
        "## Rows whose reading changes", ""]
    if changed:
        lines += ["| section | group | comparison | skill [90%] | mean d [90%] | reading on the skill interval | reading on the mean-d bound |",
                  "|---|---|---|---|---|---|---|"]
        lines += [f"| {r['section']} | {r['group']} | {r['pair']} | {_cells(r)} | {r['skill_reading']} | **{r['reading']}** |"
                  for r in changed]
    else:
        lines.append("No row changes.")
    lines += ["", "Every other tested row reads the same on both intervals.", "", "## All tested rows", "",
              "Rows the scorer left undefined (scores identical, or a zero benchmark) are on the original page and carry no interval "
              "here."]
    section = None
    for r in rows:
        if r["section"] != section:
            section = r["section"]
            lines += ["", f"### {section}", "", "| group | comparison | decision or target days | skill [90%] | mean d [90%] | reading (mean-d bound) |",
                      "|---|---|---|---|---|---|"]
        mark = f" (was {r['skill_reading']})" if r["changed"] else ""
        lines.append(f"| {r['group']} | {r['pair']} | {r['days']} | {_cells(r)} | {r['reading']}{mark} |")
    if key == "965":
        lines += ["", "### The ranker tables (b)", "",
                  "The precision and recall gains of the original page's part (b) are differences of means with their own studentized "
                  "interval, and were already read on that interval. They are not re-read here."]
    lines += ["", "Nothing here is a verdict for a hypothesis. The originals stand.", ""]
    return "\n".join(lines)


def summary(key: str, record: dict, raw: bytes) -> dict:
    rows = collect(record)
    changed = [r for r in rows if r["changed"]]
    return {"source": str(SOURCES[key].relative_to(REPO)), "source_sha256": hashlib.sha256(raw).hexdigest(),
            "page": str(PAGES[key].relative_to(REPO)), "tested_rows": len(rows),
            "rows_changed": len(changed),
            "changed": [{"section": r["section"], "group": r["group"], "pair": r["pair"], "was": r["skill_reading"],
                         "now": r["reading"]} for r in changed]}


def build() -> Dict[str, object]:
    pages, record = {}, {"issue": 1021, "ruling": "1009", "pages": {}}
    for key, source in SOURCES.items():
        raw = source.read_bytes()
        data = json.loads(raw.decode("utf-8"))
        pages[key] = render(key, data)
        record["pages"][key] = summary(key, data, raw)
    return {"pages": pages, "record": json.dumps(record, indent=1, sort_keys=True) + "\n"}


def report_command(_args) -> int:
    built = build()
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(built["record"], encoding="utf-8")
    for key, text in built["pages"].items():
        PAGES[key].write_text(text, encoding="utf-8")
        print("wrote", PAGES[key])
    return 0


def check_command(_args) -> int:
    built = build()
    stale = [p for k, p in PAGES.items() if not p.exists() or p.read_text(encoding="utf-8") != built["pages"][k]]
    if not RECORD.exists() or RECORD.read_text(encoding="utf-8") != built["record"]:
        stale.append(RECORD)
    if stale:
        print("not what the records give; run `report`:", ", ".join(str(p) for p in stale), file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("report").set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
