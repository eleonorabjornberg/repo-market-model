"""Before and after tables for #632's headline figures (#871).

Reads the tracked evidence of the page as it was scored (`docs/pivot/evidence/spread-distribution/`) and the same evidence rebuilt on the current
distance columns (`docs/pivot/evidence/spread-distribution-871/`), and prints Markdown tables of "tracked -> rebuilt" cells.

    python3 docs/pivot/evidence/spread-distribution-871/before_after.py > docs/pivot/evidence/spread-distribution-871/before_after.md
"""

import json
import re
import sys
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1]
OLD = EVIDENCE / "spread-distribution"
NEW = EVIDENCE / "spread-distribution-871"
A = "spread_q_gbm+settle+h41+dist_roll"
B = "spread_q_gbm+two_part+settle+h41+dist_roll"
LABEL = {A: "(a)", B: "(b)"}
COMPARATOR = "risk_gbm+settle+h41+dist_roll"
TAILCAP = "risk_gbm+every_day+gate+settle+h41+iorb+tailcap75"


def load(root, name):
    return json.loads((root / name).read_text(encoding="utf-8"))


def pair(old, new):
    return old if old == new else f"{old} → {new}"


def num(x, digits=3, sign=False):
    return format(x, f"+.{digits}f" if sign else f".{digits}f")


def mean_interval(cell, digits=3, sign=True):
    interval = cell.get("interval")
    text = num(cell["mean"], digits, sign)
    if interval:
        text += f" [{num(interval[0], digits, sign)}, {num(interval[1], digits, sign)}]"
    return text


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def markdown_tables(path, section):
    """The rows of the first Markdown table after the heading line that starts with `section`."""

    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(section))
    rows, seen = [], False
    for line in lines[start + 1:]:
        if line.startswith("|"):
            seen = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not set("".join(cells)) <= set("-: "):
                rows.append(cells)
        elif seen:
            break
    return rows


def step1(old, new):
    rows = []
    for h in "135":
        for key in (A, B):
            o, n = old["horizons"][h][key], new["horizons"][h][key]
            rows.append([
                h, LABEL[key], n["days"],
                pair(num(o["variant"]["crps_bps"]), num(n["variant"]["crps_bps"])),
                num(n["as_of_persistence"]["crps_bps"]), num(n["published_distribution"]["crps_bps"]),
                pair(mean_interval(o["paired"]["as_of_persistence"]["pooled"]), mean_interval(n["paired"]["as_of_persistence"]["pooled"])),
                pair(mean_interval(o["paired"]["published_distribution"]["pooled"]), mean_interval(n["paired"]["published_distribution"]["pooled"])),
            ])
    return table(["h", "variant", "days", "CRPS (bp), variant", "persistence CRPS", "published CRPS", "persistence minus variant [90%]", "published minus variant [90%]"], rows)


def mae_coverage(old, new):
    rows = []
    for h in "135":
        for key in (A, B):
            o, n = old["horizons"][h][key], new["horizons"][h][key]
            rows.append([
                h, LABEL[key], n["days"],
                pair(num(o["variant"]["mae_median_bps"], 2), num(n["variant"]["mae_median_bps"], 2)),
                pair(num(o["variant"]["coverage_50"], 2), num(n["variant"]["coverage_50"], 2)),
                pair(num(o["variant"]["coverage_90"], 2), num(n["variant"]["coverage_90"], 2)),
                pair(mean_interval(o["mae_median"]["as_of_persistence"]["pooled"], 3), mean_interval(n["mae_median"]["as_of_persistence"]["pooled"], 3)),
                pair(mean_interval(o["mae_median"]["published_distribution"]["pooled"], 3), mean_interval(n["mae_median"]["published_distribution"]["pooled"], 3)),
            ])
    return table(["h", "variant", "days", "MAE of the median (bp)", "50% coverage", "90% coverage", "MAE: persistence minus variant [90%]", "MAE: published minus variant [90%]"], rows)


def judge(old_path, new_path):
    section = "### Table 1"
    # the weighted-rule section's Table 1 is the first "### Table 1" in the report
    orows = markdown_tables(old_path, section)
    nrows = markdown_tables(new_path, section)
    header = ["model", "onsets flagged", "recall [90%]", "false alarms per onset, flat / weighted", "tier 3: worst flags per 252 days", "calibrated regimes tested, h = 1", "tier 5", "pass"]
    index = [0, 1, 2, 4, 5, 6, 7, 8]
    old_by = {r[0]: r for r in orows[1:]}
    out = []
    for r in nrows[1:]:
        o = old_by[r[0]]
        out.append([r[0]] + [pair(re.sub(r" \(tier 1 on the weighted count\)", "", o[i]), re.sub(r" \(tier 1 on the weighted count\)", "", r[i])) for i in index[1:]])
    return table(header, out)


def ordinary(old, new):
    rows = []
    for key in (COMPARATOR, TAILCAP, A, B, "persistence_logistic", "ngboost_laplace"):
        o, n = old["rows"][key], new["rows"][key]
        cells = [LABEL.get(key, f"`{key}`")]
        for h in "135":
            ol, nl = o["leads"][h], n["leads"][h]
            f = lambda cell: f"{cell['auroc']:.3f} [{cell['auroc_interval'][0]:.3f}, {cell['auroc_interval'][1]:.3f}]" if cell.get("auroc_interval") else f"{cell['auroc']:.3f}"
            cells.append(pair(f(ol), f(nl)))
        cells.append(pair(num(o["pooled"]["auroc"]), num(n["pooled"]["auroc"])))
        cells.append(pair(f"{o['pooled']['reliability']['slope']:.2f}, {o['pooled']['reliability']['intercept']:.2f}", f"{n['pooled']['reliability']['slope']:.2f}, {n['pooled']['reliability']['intercept']:.2f}"))
        ol, nl = o["leads"]["1"], n["leads"]["1"]
        g = lambda cell, k: f"{cell['reliability'][k]:.3f} [{cell[k + '_interval'][0]:.3f}, {cell[k + '_interval'][1]:.3f}]" if cell.get(k + "_interval") else f"{cell['reliability'][k]:.3f}"
        cells.append(pair(g(ol, "slope"), g(nl, "slope")))
        cells.append(pair(g(ol, "intercept"), g(nl, "intercept")))
        rows.append(cells)
    return table(["row", "AUROC h = 1", "h = 3", "h = 5", "AUROC pooled h = 1 to 5", "slope, intercept pooled", "slope [90%] h = 1", "intercept [90%] h = 1"], rows)


def brier(old, new):
    rows = []
    for key, refs in ((A, (COMPARATOR, TAILCAP)), (B, (COMPARATOR, TAILCAP, "persistence_logistic", "ngboost_laplace"))):
        for ref in refs:
            o, n = old["paired"][key][ref], new["paired"][key][ref]
            rows.append([
                LABEL[key], f"`{ref}`",
                pair(mean_interval(o["brier"]["1"]["pooled"], 4), mean_interval(n["brier"]["1"]["pooled"], 4)),
                pair(mean_interval(o["brier"]["5"]["pooled"], 4), mean_interval(n["brier"]["5"]["pooled"], 4)),
                pair(mean_interval(o["recall"]["pooled"]), mean_interval(n["recall"]["pooled"])),
            ])
    return table(["variant", "reference", "Brier difference h = 1", "Brier difference h = 5", "onset recall difference"], rows)


def onsets(old, new):
    rows = []
    for key in (A, B):
        for ref in (COMPARATOR, TAILCAP):
            o, n = old["gained_lost"][key][ref], new["gained_lost"][key][ref]
            rows.append([LABEL[key], f"`{ref}`", pair(f"{o['both']} of {o['onsets']}", f"{n['both']} of {n['onsets']}"),
                         pair(", ".join(o["gained"]) or "none", ", ".join(n["gained"]) or "none"),
                         pair(", ".join(o["lost"]) or "none", ", ".join(n["lost"]) or "none")])
    return table(["variant", "against", "warned by both", "gained", "lost"], rows)


def by_year(old, new):
    rows = []
    for key in (COMPARATOR, TAILCAP, A, B):
        o, n = old["by_year"][key], new["by_year"][key]
        rows.append([LABEL.get(key, f"`{key}`")] + [pair(f"{o[y][1]} of {o[y][0]}", f"{n[y][1]} of {n[y][0]}") for y in ("2018", "2019", "2020", "2024", "2025")])
    return table(["row", "2018", "2019", "2020", "2024", "2025"], rows)


def calibration(old, new):
    rows = []
    for cell in ("all", "day type ordinary", "regime 2018-19", "regime 2020", "regime 2021-23", "regime 2024", "regime 2025-26"):
        o, n = old["calibration"][B][cell], new["calibration"][B][cell]
        rows.append([cell.replace("day type ", "").replace("regime ", ""), pair(f"{o['days']:,.0f}", f"{n['days']:,.0f}"), pair(num(o["predicted"], 4), num(n["predicted"], 4)), pair(num(o["realised"], 4), num(n["realised"], 4))])
    return table(["cell", "days", "predicted", "realised"], rows)


def main():
    od, nd = load(OLD, "distribution.json"), load(NEW, "distribution.json")
    oc, nc = load(OLD, "compare.json"), load(NEW, "compare.json")
    oo, no = load(OLD, "ordinary.json"), load(NEW, "ordinary.json")
    if od["panel_sha256"] != nd["panel_sha256"]:
        raise ValueError("the two evidence sets were scored on different published panels")
    sections = [
        ("Step 1: CRPS against as-of persistence and the published distribution (tracked → rebuilt)", step1(od, nd)),
        ("MAE of the median and central coverage", mae_coverage(od, nd)),
        ("The judge, weighted rule in force: Table 1", judge(OLD / "report.md", NEW / "report.md")),
        ("Against the references, +5 bp (Brier difference, reference minus row; onset recall difference, row minus reference)", brier(oc, nc)),
        ("Onsets kept and lost, by date", onsets(oc, nc)),
        ("Recall by calendar year", by_year(oc, nc)),
        ("The ordinary days: AUROC and reliability", ordinary(oo, no)),
        ("Calibration of (b), pooled over h = 1 to 5", calibration(oc, nc)),
    ]
    print("# #632 re-scored: tracked → rebuilt (#871)\n")
    print(f"Published panel `{nd['panel_sha256'][:8]}…` in both. A cell reads `tracked → rebuilt`, or one value where the two are equal. Development data, 2018-06-29 to 2025-12-31.\n")
    for title, body in sections:
        print(f"## {title}\n\n{body}\n")


if __name__ == "__main__":
    main()
