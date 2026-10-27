#!/usr/bin/env python3
"""The #941, #1115, #1133 and #1153 pages read the studentized bound on mean d, beside the skill interval (#1167; H5 reporting, for #1009).

Eleonora's ruling on #1009 (20 October 2026, relayed): a development page reports both the skill interval and the studentized
mean-d bound, and reads the mean-d bound, as ruling 1/5 reads the verdict; each page states Lens C's caveat. #1021 did it for the
#959 and #965 pages (`scripts/mean_d_reading_1021.py`). This script does it for the four pages behind the new H5 candidate:
`docs/research/fhs-scale-941/result.json`, `calendar-mr-1115/result.json`, `walk-calibration-1133/result.json` and
`faster-scale-1153/result.json`. It writes a new page for each. The original pages stand. Nothing is re-scored: every interval is
the one in the committed record.

The mean-d bound: the 90% two-sided studentized interval on mean(d) is the pair of one-sided 95% bounds. A candidate is read as a
gain when the lower bound is above zero, as a loss when the upper bound is below zero, and as undecided otherwise (the words the
four original pages use). A row the scorer left undefined carries no interval and is not read here.

    python3 scripts/mean_d_reading_1167.py report
    python3 scripts/mean_d_reading_1167.py check

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
RESEARCH = REPO / "docs" / "research"
SOURCES = {key: RESEARCH / name / "result.json" for key, name in
           (("941", "fhs-scale-941"), ("1115", "calendar-mr-1115"), ("1133", "walk-calibration-1133"), ("1153", "faster-scale-1153"))}
PAGES = {key: RESEARCH / f"{SOURCES[key].parent.name}-mean-d-1167-result.md" for key in SOURCES}
ORIGINALS_DIR = RESEARCH
ORIGINALS = {key: f"{SOURCES[key].parent.name}-result.md" for key in SOURCES}
TITLES = {"941": "Scaled mean reversion (#941)", "1115": "Calendar and FOMC terms on the scaled mean reversion (#1115)",
          "1133": "Walk-forward calibration of the bands (#1133)", "1153": "Faster-reacting scale arms (#1153)"}
RECORD = RESEARCH / "mean-d-reading-1167" / "result.json"
SPLIT_TITLES = {"pooled": "all decision days", "regime": "regime", "pressure_day_type": "pressure-day type",
                "target_day_type": "target-day type", "lead": "lead"}


def no_reading(row: dict) -> str:
    """The words for a row whose mean-d bound was not computed (#1215): not "undecided", which says the bound straddles zero."""

    return f"**no reading** (mean-d bound not computed: {row['undefined']})"


def verdict_words(row: dict) -> str:
    """The reading of one tested row: the studentized bound on mean d (the verdict's), not the skill interval."""

    if "undefined" in row:
        return no_reading(row)
    low, high = row["difference_interval"]
    return "gain" if low > 0.0 else "loss" if high < 0.0 else "undecided"


def skill_words(row: dict) -> str:
    """The reading the original pages gave: the skill interval."""

    if "undefined" in row:
        return "undecided"
    if row["skill_interval"] is None:
        return "skill undefined"
    low, high = row["skill_interval"]
    return "gain" if low > 0.0 else "loss" if high < 0.0 else "undecided"


def collect(record: dict) -> List[dict]:
    """Every paired row of a record that carries both intervals, in record order, with both readings.

    A row is a dict holding `skill_interval` and `difference_interval`. A row the scorer left undefined holds neither and is
    skipped; so is a block of means with no interval.
    """

    rows: List[dict] = []

    def walk(node, path):
        if not isinstance(node, dict):
            return
        if "skill_interval" in node and "difference_interval" in node:
            reading, before = verdict_words(node), skill_words(node)
            section, group, pair = describe(path)
            rows.append({"section": section, "group": group, "pair": pair, "days": node.get("days"), "row": node,
                         "reading": reading, "skill_reading": before,
                         "changed": before != "skill undefined" and reading != before})
            return
        for key, child in node.items():
            walk(child, path + [key])

    walk(record, [])
    return rows


def describe(path: Sequence[str]) -> tuple:
    """(section, group, comparison) of a row from its path in the record."""

    if path[0] == "groups" and len(path) >= 7 and path[4] == "vs":
        split, label, metric, candidate, benchmark = path[1], path[2], path[3], path[5], path[6]
        return f"{metric}, by {SPLIT_TITLES.get(split, split)}", label, f"{candidate} against {benchmark}"
    if path[0] == "politis_white":
        split, label, metric, arm = path[1], path[2], path[3], path[4]
        return f"Politis-White block beside 10: {metric}, by {SPLIT_TITLES.get(split, split)}", label, f"{arm} against the base (a)"
    return " / ".join(path[:-1]), path[-1], path[-1]


def pct(value: float) -> str:
    return f"{100 * value:+.1f}%"


def interval(pair: Sequence[float], scale: float = 1.0, digits: int = 1) -> str:
    return f"[{pair[0] * scale:+.{digits}f}, {pair[1] * scale:+.{digits}f}]"


def num(value: float) -> str:
    return f"{value:+.4g}"


def cells(r: dict) -> str:
    t = r["row"]
    skill = "skill undefined" if t["skill_interval"] is None else f"{pct(t['skill'])} {interval(t['skill_interval'], 100)}"
    return (f"{skill} | {num(t['difference'])} "
            f"[{num(t['difference_interval'][0])}, {num(t['difference_interval'][1])}]")


def direction_counts(rows: Sequence[dict]) -> Dict[str, int]:
    return dict(sorted(Counter(f"{r['skill_reading']} -> {r['reading']}" for r in rows if r["changed"]).items()))


def render(key: str, record: dict) -> str:
    rows = collect(record)
    changed = [r for r in rows if r["changed"]]
    lines = [
        f"# {TITLES[key]}, read on the mean-d bound (#1167; H5 reporting, for #1009)", "",
        "**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value "
        f"moves. Every figure is read from `docs/research/{SOURCES[key].parent.name}/result.json`, the record of the original page "
        f"(`{ORIGINALS[key]}`, which stands), by `scripts/mean_d_reading_1167.py report`. "
        f"Seed {record['seed']}, {record['draws']:,} draws, as on the original page.", "",
        "## What changes and why", "",
        "The original page read each row from the studentized skill interval. The skill interval and the interval on the mean "
        "difference d are built from different studentized draws, so their ends can fall on different sides of zero (#1009). The "
        "protocol's verdict reads the one-sided studentized bound on mean d (ruling 1/5). By Eleonora's ruling on #1009 this page "
        "shows both intervals for every paired row and reads the mean-d bound: **gain** when the lower bound of mean d is above zero, "
        "**loss** when its upper bound is below zero, **undecided** otherwise. The 90% two-sided interval on mean d is the pair of "
        "one-sided 95% bounds. d = S(benchmark) − S(candidate), positive favouring the candidate; skill is mean(d) / "
        "mean(S(benchmark)). A row the scorer left undefined carries no interval and is not read here.", "",
        "**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is "
        "understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order "
        "of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here "
        "is narrower than it should be after 2020. A development reading on this page is evidence for a question, not a verdict.", "",
        f"Paired rows read: {len(rows)}. Rows whose reading changes: {len(changed)}.", ""]
    if changed:
        lines += ["| reading on the skill interval -> reading on the mean-d bound | rows |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in direction_counts(rows).items()]
        lines.append("")
    lines += ["## Readings that change", ""]
    if changed:
        lines += ["| section | group | comparison | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |",
                  "|---|---|---|---|---|---|---|"]
        lines += [f"| {r['section']} | {r['group']} | {r['pair']} | {cells(r)} | {r['skill_reading']} | **{r['reading']}** |"
                  for r in changed]
    else:
        lines.append("No row changes.")
    lines += ["", "Every other paired row reads the same on both intervals.", "", "## All paired rows", ""]
    section = None
    for r in rows:
        if r["section"] != section:
            section = r["section"]
            if len(lines) and lines[-1] != "":
                lines.append("")
            lines += [f"### {section}", "",
                      "| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |", "|---|---|---|---|---|---|"]
        mark = f" (was {r['skill_reading']})" if r["changed"] else ""
        lines.append(f"| {r['group']} | {r['pair']} | {r['days']} | {cells(r)} | {r['reading']}{mark} |")
    lines += ["", "Nothing here is a verdict for a hypothesis. The originals stand.", ""]
    return "\n".join(lines)


def summary(key: str, record: dict, raw: bytes) -> dict:
    rows = collect(record)
    changed = [r for r in rows if r["changed"]]
    return {"source": str(SOURCES[key].relative_to(REPO)), "source_sha256": hashlib.sha256(raw).hexdigest(),
            "page": str(PAGES[key].relative_to(REPO)), "paired_rows": len(rows), "rows_changed": len(changed),
            "by_direction": direction_counts(rows),
            "changed": [{"section": r["section"], "group": r["group"], "pair": r["pair"], "was": r["skill_reading"],
                         "now": r["reading"]} for r in changed]}


def build() -> Dict[str, object]:
    pages, record = {}, {"issue": 1167, "ruling": "1009", "finding": "1163", "pages": {}}
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
