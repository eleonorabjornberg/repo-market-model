#!/usr/bin/env python3
"""The #1145 page read on the studentized bound on mean d, beside the skill interval (#1194; H5 reporting, for #1009 and finding #1187).

Eleonora's ruling on #1009 (20 October 2026, relayed): a development page reports both the skill interval and the studentized
mean-d bound, and reads the mean-d bound; each page states Lens C's caveat. #1021 and #1167 did it for the pages of #959, #965, #941,
#1115, #1133 and #1153. #1145 was declared two days after the ruling and still read the skill interval (finding #1187). Her ruling on
that finding (24 October 2026, relayed): (s3) stays the H5 candidate, the pages are corrected, and its two upper-tail losses (2020 and
the FOMC target days) are an open question to settle before any H5 registration.

This script writes a new page for `docs/research/state-calendar-1145/result.json` and `docs/research/mean-d-reading-1194/result.json`.
The first page, `docs/research/state-calendar-1145-result.md`, stands. Nothing is re-scored: every interval is the one in the
committed record. The bound is read as in `scripts/mean_d_reading_1167.py` (gain: lower bound above zero; loss: upper bound below
zero; else undecided).

    python3 scripts/mean_d_reading_1194.py report
    python3 scripts/mean_d_reading_1194.py check

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
RESEARCH = REPO / "docs" / "research"


def _load(name: str, file: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


mean_d_reading_1167 = _load("mean_d_reading_1167", "mean_d_reading_1167.py")

SOURCE = RESEARCH / "state-calendar-1145" / "result.json"
PAGE = RESEARCH / "state-calendar-1145-mean-d-1194-result.md"
FIRST_PAGE = "state-calendar-1145-result.md"
RECORD = RESEARCH / "mean-d-reading-1194" / "result.json"
CANDIDATE = "sc_s3_robust"
REFERENCE = "mr_cal_a_base"
METRICS = (("grid_crps", "grid CRPS"), ("upper_tail_twcrps", "upper-tail twCRPS"))
REGIMES = ("2018-19", "2020", "2021-23", "2024", "2025-26")
SPLITS = (("pooled", "all decision days"), ("regime", None), ("target_day_type", None))
NAMES = {"mr_cal_a_base": "(a)", "sc_s1_standardised": "(s1)", "sc_s2_scarcity": "(s2)", "sc_s3_robust": "(s3)",
         "sc_s4_fomc_iorb": "(s4)", "B1_prime": "B1'", "spread_mr_ctx": "spread_mr_ctx"}


def candidate_readings(record: dict) -> List[dict]:
    """(s3) against (a), both metrics, pooled and by regime and target-day type, each with both readings."""

    out = []
    for split, only in SPLITS:
        for label, entry in record["groups"].get(split, {}).items():
            if only is not None and label != only:
                continue
            for metric, metric_name in METRICS:
                row = entry[metric]["vs"].get(CANDIDATE, {}).get(REFERENCE)
                if row is None or "undefined" in row:
                    continue
                now = mean_d_reading_1167.verdict_words(row)
                was = mean_d_reading_1167.skill_words(row)
                out.append({"split": split, "label": label, "metric": metric, "metric_name": metric_name, "days": entry["days"],
                            "row": row, "was": was, "now": now, "changed": now != was})
    return out


def regime_line(record: dict) -> Dict[str, Dict[str, str]]:
    """(s3) against (a) by regime on the mean-d bound, for each metric: the regime line of the candidate block."""

    line: Dict[str, Dict[str, str]] = {}
    for metric, _ in METRICS:
        line[metric] = {regime: mean_d_reading_1167.verdict_words(record["groups"]["regime"][regime][metric]["vs"][CANDIDATE][REFERENCE])
                        for regime in REGIMES}
    return line


def _pairs(rows: List[dict]) -> List[dict]:
    """Rename the arms for reading: the base class prints record keys."""

    for r in rows:
        for key, name in NAMES.items():
            r["pair"] = r["pair"].replace(key, name)
    return rows


def regime_and_pooled(rows: Sequence[dict]) -> List[dict]:
    """The pooled and regime readings of grid CRPS and twCRPS (the finding's 319): rows of the pooled and regime splits."""

    return [r for r in rows if r["section"].split(", by ")[-1] in ("all decision days", "regime") and not r["section"].startswith("Politis")
            and r["section"].split(",")[0] in ("grid_crps", "upper_tail_twcrps")]


def render(record: dict) -> str:
    rows = _pairs(mean_d_reading_1167.collect(record))
    changed = [r for r in rows if r["changed"]]
    cand = candidate_readings(record)
    cand_changed = [c for c in cand if c["changed"]]
    cells = mean_d_reading_1167.cells
    lines = [
        "# State-scaled calendar effects, read on the mean-d bound (#1194; H5 reporting, for #1009)", "",
        "**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value "
        "moves; **no claim changes**. Every figure is read from `docs/research/state-calendar-1145/result.json`, the record of the "
        f"first page (`{FIRST_PAGE}`, which stands), by `scripts/mean_d_reading_1194.py report`. Seed {record['seed']}, "
        f"{record['draws']:,} draws, as on the first page.", "",
        "## What changes and why", "",
        "The first page read each row from the studentized skill interval. Her ruling on #1009 (20 October 2026) is that a development "
        "page shows both intervals and reads the studentized bound on mean d, as the protocol's verdict does (ruling 1/5). #1145 was "
        "declared two days after that ruling and read the skill interval (finding #1187). This page shows both for every paired row "
        "and reads the mean-d bound: **gain** when the lower bound of mean d is above zero, **loss** when its upper bound is below zero, "
        "**undecided** otherwise. The 90% two-sided interval on mean d is the pair of one-sided 95% bounds. d = S(reference) - "
        "S(arm), positive favouring the arm; skill is mean(d) / mean(S(reference)). A row the scorer left undefined carries no "
        "interval and is not read here.", "",
        "**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is "
        "understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order "
        "of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here "
        "is narrower than it should be after 2020. A reading on this page is evidence for a question, not a verdict.", "",
        f"Paired rows read: {len(rows)}. Rows whose reading changes: {len(changed)}.", ""]
    if changed:
        lines += ["| reading on the skill interval -> reading on the mean-d bound | rows |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in mean_d_reading_1167.direction_counts(rows).items()]
        lines.append("")
    lines += ["## The candidate (s3) against (a)", "",
              "(s3), the scaled mean reversion with the calendar terms in standardised units, a Huber fit and a heavier ridge, is the H5 "
              "candidate by her ruling on #1151 (23 October 2026). It is read here against (a), the model it replaced, pooled, by regime "
              "and by target-day type, on both scores. Grid CRPS is the primary score; upper-tail twCRPS is the key secondary.", "",
              "| split | group | days | measure | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |",
              "|---|---|---|---|---|---|---|---|"]
    for c in cand:
        mark = "**" if c["changed"] else ""
        lines.append(f"| {c['split']} | {c['label']} | {c['days']} | {c['metric_name']} | {cells({'row': c['row']})} | {c['was']} | "
                     f"{mark}{c['now']}{mark} |")
    line = regime_line(record)
    lines += ["", "**Regime line on the mean-d bound** (decision-day regimes of the target day, (s3) against (a)):", ""]
    for metric, metric_name in METRICS:
        lines.append(f"- {metric_name}: " + "; ".join(f"{k}: {v}" for k, v in line[metric].items()) + ".")
    losses = [c for c in cand if c["now"] == "loss"]
    lines += ["", "**Open question, recorded by her ruling on #1187 (24 October 2026).** (s3) stays the candidate. Read on the mean-d bound, "
              "it is worse than (a) on upper-tail twCRPS " + ", ".join(
                  f"{'in ' if c['split'] == 'regime' else 'on '}{c['label']} (mean d {c['row']['difference']:+.3f} bp, interval "
                  f"[{c['row']['difference_interval'][0]:+.3f}, {c['row']['difference_interval'][1]:+.3f}])"
                  for c in losses if c["metric"] == "upper_tail_twcrps") + ". "
              "Whether those two upper-tail losses matter for the H5 registration is to be settled before any registration; it is her "
              "decision, and the 2020 loss comes with Lens C's caveat above (the 2020 interval is about 2× too narrow), so it is "
              "evidence for a question, not a verdict. This page settles nothing.", ""]
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
    lines += ["", "Nothing here is a verdict for a hypothesis. The first page stands.", ""]
    return "\n".join(lines)


def build() -> Dict[str, str]:
    raw = SOURCE.read_bytes()
    record = json.loads(raw.decode("utf-8"))
    rows = _pairs(mean_d_reading_1167.collect(record))
    changed = [r for r in rows if r["changed"]]
    scoped = regime_and_pooled(rows)
    cand = candidate_readings(record)
    out = {"issue": 1194, "ruling": "1009", "finding": "1187", "source": str(SOURCE.relative_to(REPO)),
           "source_sha256": hashlib.sha256(raw).hexdigest(), "page": str(PAGE.relative_to(REPO)),
           "paired_rows": len(rows), "rows_changed": len(changed),
           "by_direction": mean_d_reading_1167.direction_counts(rows),
           "regime_and_pooled_rows": len(scoped), "regime_and_pooled_changed": sum(r["changed"] for r in scoped),
           "regime_line": regime_line(record),
           "candidate_changed": [{"split": c["split"], "group": c["label"], "metric": c["metric"], "was": c["was"], "now": c["now"]}
                                 for c in cand if c["changed"]],
           "changed": [{"section": r["section"], "group": r["group"], "pair": r["pair"], "was": r["skill_reading"], "now": r["reading"]}
                       for r in changed]}
    return {"page": render(record), "record": json.dumps(out, indent=1, sort_keys=True) + "\n"}


def report_command(_args) -> int:
    built = build()
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(built["record"], encoding="utf-8")
    PAGE.write_text(built["page"], encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args) -> int:
    built = build()
    stale = [p for p, text in ((PAGE, built["page"]), (RECORD, built["record"]))
             if not p.exists() or p.read_text(encoding="utf-8") != text]
    if stale:
        print("not what the record gives; run `report`:", ", ".join(str(p) for p in stale), file=sys.stderr)
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
