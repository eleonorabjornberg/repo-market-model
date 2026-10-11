"""Before-and-after tables for the re-score after the audit's construction fixes (#578).

A scratch measurement, not a record: it reads result documents and writes Markdown. It writes nothing into `docs/runs/`.

    PYTHONPATH=src python3 scripts/audit_fixes_578.py report --before-ref origin/main --output docs/pivot/audit-fixes-578-result.md

`report` reads each affected result document twice: as it stood at `--before-ref` (`git show REF:PATH`) and as it is in
the working tree (re-scored after the fixes). For each row it prints, under the weighted miss rule in force (the flat
rule's count beside it), tier 1 as declared (lead >= 1, pooled over h = 1 to 5) and at lead >= 3, tier 1 at each
horizon, tiers 3 and 5, the pass, and onsets warned by calendar year with 2018, 2020 and 2024 called out. A verdict
that changes is listed at the head of the page.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]

EVIDENCE = "docs/pivot/evidence"
#: document path -> (title, the rows re-scored, in the order shown)
DOCUMENTS: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    f"{EVIDENCE}/structural-liquidity/result.json": (
        "Structural liquidity (#542)", ("structural_liquidity", "risk_gbm+structural"),
    ),
    f"{EVIDENCE}/projected-reserves/result.json": (
        "Projected reserves (#545)", ("projected_reserves", "risk_gbm+projected"),
    ),
    f"{EVIDENCE}/latent-factor/compare.json": (
        "Latent factor (#543)",
        (
            "latent_factor", "latent_factor_resid", "latent_factor_logit",
            "risk_gbm+latent_factor", "risk_gbm+latent_factor_resid", "risk_gbm+latent_factor_logit",
        ),
    ),
    f"{EVIDENCE}/combined-model/compare.json": (
        "Combined model (#561) and its controls",
        (
            "risk_gbm+combined", "risk_gbm+combined_nogate", "risk_logistic+combined", "risk_logistic+combined_nogate",
            "risk_gbm+combined_no_factor", "risk_gbm+combined_no_structural", "risk_gbm+combined_no_projected",
            "risk_gbm+settle+h41", "risk_gbm+every_day+gate+settle+h41",
        ),
    ),
}
CALLED_OUT = ("2018", "2020", "2024")
RULE = "weighted"


def _yes(value) -> str:
    return "–" if value is None else ("yes" if value else "no")


def _f(value, places: int = 2) -> str:
    return "–" if value is None else f"{value:.{places}f}"


def by_year(document: dict, name: str) -> Optional[Dict[str, list]]:
    """`{year: [onsets, onsets warned]}` of `name`, from the top level or from the row's own block."""

    if name in document.get("by_year", {}):
        return document["by_year"][name]
    for row in document.get("rows", {}).values():
        if name in row.get("by_year", {}):
            return row["by_year"][name]
    return None


def table_one_row(document: dict, name: str) -> Optional[List[str]]:
    """The cells of the judge's Table 1 row of `name` under the weighted rule, or `None` when it has none."""

    text = document.get("judge_tables", {}).get(RULE)
    if not text:
        return None
    for line in text.splitlines():
        if line.startswith(f"| {name} |"):
            return [cell.strip() for cell in line.strip().strip("|").split(" | ")]
    return None


def summary(document: dict, name: str) -> Optional[dict]:
    """What the page needs of one row, or `None` if the document does not carry it."""

    judged = document.get("judge", {}).get(RULE, {}).get(name)
    if judged is None:
        return None
    near = judged["onset_warning"]["lead_at_least_1"]
    far = judged["onset_warning"].get("lead_at_least_3", {})
    readings = document.get("readings", {}).get(RULE, {}).get(name, {})
    per_horizon = {h: cell for h, cell in readings.get("b1", {}).items()}
    cells = table_one_row(document, name)
    verdict = judged["verdict"]
    interval = near["recall"].get("interval") or {}
    return {
        "flagged": near["onsets_flagged"], "onsets": near["onsets"], "recall": near["recall"]["mean"],
        "recall_interval": (interval.get("lower"), interval.get("upper")),
        "weighted_fa": near.get("worst_weighted_false_alarms_per_onset"),
        "flat_fa": near.get("worst_false_alarms_per_onset"),
        "far_flagged": far.get("onsets_flagged"), "far_recall": (far.get("recall") or {}).get("mean"),
        "per_horizon": per_horizon,
        "tier1": verdict["tier_1_onset_warning"], "tier3": verdict["tier_3_no_crying_wolf"],
        "tier5": verdict["tier_5_week_ahead"], "passes": verdict["passes"],
        "tier3_flags": cells[5] if cells and len(cells) > 5 else None,
        "tier5_cell": cells[7] if cells and len(cells) > 7 else None,
        "years": by_year(document, name),
    }


def _recall_cell(s: dict) -> str:
    low, high = s["recall_interval"]
    interval = "" if low is None else f" [{low:.3f}, {high:.3f}]"
    return f"{s['flagged']} of {s['onsets']}, {_f(s['recall'], 3)}{interval}"


def tier_table(before: Dict[str, dict], after: Dict[str, dict], names: Sequence[str]) -> List[str]:
    lines = [
        "| row | | tier 1 pooled (lead >= 1): onsets flagged, recall [90%] | worst false alarms per onset, weighted (flat) "
        "| tier 1 at lead >= 3 (reported) | tier 3: worst flags per 252 days, state 0 / 2021-23 | tier 5: calibrated, beats clim. "
        "| tiers 1 / 3 / 5 | pass |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name in names:
        for label, source in (("before", before), ("after", after)):
            s = source.get(name)
            if s is None:
                lines.append(f"| {name if label == 'before' else ''} | {label} | not in this document | | | | | | |")
                continue
            far = "–" if s["far_flagged"] is None else f"{s['far_flagged']} of {s['onsets']}, {_f(s['far_recall'], 3)}"
            lines.append(
                f"| {name if label == 'before' else ''} | {label} | {_recall_cell(s)} | {_f(s['weighted_fa'])} ({_f(s['flat_fa'])}) "
                f"| {far} | {s['tier3_flags'] or '–'} | {s['tier5_cell'] or '–'} "
                f"| {_yes(s['tier1'])} / {_yes(s['tier3'])} / {_yes(s['tier5'])} | {'PASS' if s['passes'] else 'fail'} |"
            )
    return lines


def horizon_table(before: Dict[str, dict], after: Dict[str, dict], names: Sequence[str]) -> List[str]:
    lines = [
        "| row | | " + " | ".join(f"h = {h}: flagged, worst weighted FA, tier 1" for h in range(1, 6)) + " |",
        "|---|---|" + "---|" * 5,
    ]
    for name in names:
        for label, source in (("before", before), ("after", after)):
            s = source.get(name)
            if s is None:
                continue
            cells = []
            for h in range(1, 6):
                cell = s["per_horizon"].get(str(h))
                cells.append(
                    "–" if cell is None
                    else f"{cell['onsets_flagged']}, {_f(cell.get('false_alarms_per_onset_weighted'))}, {_yes(cell.get('passes'))}"
                )
            lines.append(f"| {name if label == 'before' else ''} | {label} | " + " | ".join(cells) + " |")
    return lines


def year_table(before: Dict[str, dict], after: Dict[str, dict], names: Sequence[str]) -> List[str]:
    years = sorted({y for source in (before, after) for s in source.values() if s and s["years"] for y in s["years"]})
    head = [f"**{y}**" if y in CALLED_OUT else y for y in years]
    lines = [
        "| row | | " + " | ".join(head) + " |",
        "|---|---|" + "---|" * len(years),
    ]
    for name in names:
        for label, source in (("before", before), ("after", after)):
            s = source.get(name)
            if s is None or not s["years"]:
                continue
            cells = []
            for y in years:
                cell = s["years"].get(y)
                cells.append("–" if cell is None else f"{cell[1]} of {cell[0]}")
            lines.append(f"| {name if label == 'before' else ''} | {label} | " + " | ".join(cells) + " |")
    return lines


def changed_verdicts(title: str, before: Dict[str, dict], after: Dict[str, dict], names: Sequence[str]) -> List[str]:
    out = []
    for name in names:
        b, a = before.get(name), after.get(name)
        if b is None or a is None:
            continue
        moved = [
            f"{label} {_yes(b[key])} to {_yes(a[key])}"
            for key, label in (("tier1", "tier 1"), ("tier3", "tier 3"), ("tier5", "tier 5"), ("passes", "pass"))
            if b[key] != a[key]
        ]
        if moved:
            out.append(f"- {title}: `{name}`: " + ", ".join(moved))
    return out


def _git_show(ref: str, path: str) -> dict:
    text = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=REPO, check=True, capture_output=True, text=True
    ).stdout
    return json.loads(text)


def report(before_ref: str) -> str:
    sections: List[str] = []
    verdicts: List[str] = []
    for path, (title, names) in DOCUMENTS.items():
        before_doc = _git_show(before_ref, path)
        after_doc = json.loads((REPO / path).read_text(encoding="utf-8"))
        before = {n: summary(before_doc, n) for n in names}
        after = {n: summary(after_doc, n) for n in names}
        verdicts += changed_verdicts(title, before, after, names)
        sections += [
            f"## {title}", "",
            f"Source: `{path}`; before is `{before_ref}`, after is the re-score of this change. Weighted rule in force.", "",
            "### Tiers", "", *tier_table(before, after, names), "",
            "### Tier 1 at each horizon (onsets flagged, worst weighted false alarms per onset, passes)", "",
            *horizon_table(before, after, names), "",
            "### Onsets warned by calendar year (lead >= 1, any horizon 1 to 5; 2018, 2020 and 2024 in bold)", "",
            *year_table(before, after, names), "",
        ]
    head = [
        "# Re-score after the audit's construction fixes (#578)", "",
        "Generated by `scripts/audit_fixes_578.py report`; not edited by hand.", "",
        "## Verdicts that change", "",
        *(verdicts or ["None: no tier or pass of any re-scored row changes."]), "",
    ]
    return "\n".join(head + sections) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    rep = commands.add_parser("report")
    rep.add_argument("--before-ref", default="origin/main")
    rep.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    args.output.write_text(report(args.before_ref), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
