#!/usr/bin/env python3
"""The result page of #873 (H1 step 4), written from the three records it compares; no figure on it is typed.

    python3 scripts/orientation_873.py report
    python3 scripts/orientation_873.py check

Reads `docs/research/protocol-calibration/result.json` (in force) and `protocol-calibration-873/result.json` (the
recalibration in the orientation the protocol applies), `power-study-769/result.json` and `power-study-873/result.json`
(`scripts/power_study_769.py`, without and with `--values draft-873`), `power-replay-754/result.json` (#792) and
`power-replay-873/result.json` (`scripts/power_replay_inforce_873.py`). `report` writes
`docs/research/orientation-873-result.md`; `check` fails if the page on disk is not what `report` would write.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESEARCH = REPO / "docs" / "research"
PAGE = RESEARCH / "orientation-873-result.md"
GRID, FIVE = "B2-B1", "B3-B1 (five levels)"
IN_FORCE, DRAFT = "in force today (calibrated on S(B2) - S(B1))", "draft of #873 (calibrated on S(B1) - S(candidate))"


def load(*parts):
    return json.loads(RESEARCH.joinpath(*parts).read_text(encoding="utf-8"))


def pct(p, se=None):
    return f"{100 * p:.1f}%" if se is None else f"{100 * p:.1f}% ± {196 * se:.1f}"


def interval(p, paths):
    return pct(p, math.sqrt(p * (1 - p) / paths))


def table(header, rows):
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(r) + " |" for r in rows]


def num(value):
    return "none" if value is None else f"{value:.3f}"


def calibration_section(old, new):
    rows = []
    for comparison, label in ((GRID, "efficacy, grid comparison (B2 against B1, 23 levels)"),
                              (FIVE, "efficacy, B3 against B1 (five levels)")):
        for n in ("125", "250"):
            rows.append([label, n, num(old["comparison_critical_values"][comparison][n]),
                         num(new["comparison_critical_values"][comparison][n]),
                         pct(old["null_false_detection_full_history"][comparison][n]),
                         pct(new["null_false_detection_full_history"][comparison][n])])
    for n in ("60", "125", "250"):
        rows.append(["futility (upper bound of skill, grid comparison)", n,
                     num(old["futility_critical_values"][GRID][n]), num(new["futility_critical_values"][GRID][n]), "", ""])
    paths = new["null_false_detection_full_history"][GRID]["paths"]
    return [
        "## 1. The calibrated values, old and new", "",
        f"Same windows ({', '.join(f'{n}: {w:,}' for n, w in new['windows'].items())} for the efficacy value, "
        f"{new['futility_windows']:,} for futility), block {new['window_block']} and seed {new['seed']} as the record in force; "
        f"only the orientation changes. The efficacy value is the `1 - level` quantile of the studentized mean of `d` over resampled "
        f"windows; the daily `d` is skewed, so reversing its sign moves the quantile. The look-1 efficacy value does not exist "
        f"(Q-B: look 1 checks futility only). The last two columns are the share of null paths (no true difference, "
        f"{paths:,} paths, first 250 days of a stationary-bootstrap resample of the full development history) detected "
        f"by that day: the nominal overall size is 5%.", "",
        *table(["value", "days", "old (in force)", "new (draft)", "old null detection", "new null detection"], rows), "",
    ]


def power_cells(result, reading):
    paths = result["constants"]["paths"]
    cells = result["readings"][reading]["cells"]
    return paths, cells


def power_section(old, new):
    names = {"a": "full history, circular blocks", "b": "post-2020-04, circular blocks",
             "c": "full history, stationary bootstrap", "d": "post-2020-04, stationary bootstrap"}
    rows = []
    for reading, label in names.items():
        for title, source in (("old", old), ("new", new)):
            paths, cells = power_cells(source, reading)
            row = [f"({reading}) {label}", title]
            for key in ("noise=1.0, delta=0.0", "noise=1.0, delta=0.03", "noise=1.0, delta=0.1"):
                for kind in ("ungated", "gated") if key.endswith("0.0") else ("gated",):
                    for n in ("125", "250"):
                        row.append(interval(cells[key][kind][n], paths))
            rows.append(row)
    header = ["reading", "values", "size 125", "size 250", "3% (the MME) 125", "3% 250", "10% 125", "10% 250"]
    # the null cell is read ungated only, so drop the gated size columns
    trimmed = [r[:2] + r[2:4] + r[6:] for r in rows]
    paths = new["constants"]["paths"]
    return [
        "## 2. The power study of #769 and #791 re-run on the new values", "",
        f"`scripts/power_study_769.py run --values draft-873`: the rule, the paths ({paths:,} per cell, seed {new['constants']['seed']}) "
        f"and the four readings are #769's; only the critical values at looks 2 and 3 change (old {', '.join(f'{k}: {v:.3f}' for k, v in old['constants']['critical_values'].items())}; "
        f"new {', '.join(f'{k}: {v:.3f}' for k, v in new['constants']['critical_values'].items())}). Each figure is a share of paths with "
        f"± 1.96 Monte Carlo standard errors. Size is the share of null paths detected by that look (the test without the MME gate); "
        f"power is the gated share at a true skill of 3% and 10% against B1 (`NOISE` = 1). The B2 half of Supported is not simulated, so "
        f"each power is an upper bound on the full rule's.", "",
        *table(header, trimmed), "",
    ]


def replay_section(published, replay):
    out = ["## 3. The replay of #792 at the values of the protocol", "",
           f"`scripts/power_replay_inforce_873.py run`: windows of {replay['days']} days slid every {replay['step']} days over the "
           f"same real pairs and known-equal series as #792 (no day after {replay['study_end']}), each read at looks "
           f"{', '.join(str(n) for n in replay['looks'])} at the protocol's grid-comparison values (the same two values for every "
           "pair), not at values calibrated on the pair itself. Shares of windows flagged (test; gated by the MME in brackets), "
           "with a moving-block 95% interval for the test share. Windows overlap, so the effective number of independent windows is "
           "small: read an interval, not the share.", ""]
    names = {"real": "real pair", "E1": "E1 relabelled copy", "E2": "E2 demeaned", "E3": "E3 sign-flipped"}
    pairs = {"P2": "P2 B2 vs B1", "P2r": "P2r B1 vs B2 (a reversed pair, a diagnostic)", "P3": "P3 B3 vs B1"}
    for values in replay["values"]:
        out += [f"### Values {values}", ""]
        rows = []
        for pair, plabel in pairs.items():
            if f"{values}|{pair}|real" not in replay["replay"]:
                continue
            for kind, klabel in names.items():
                cell = replay["replay"][f"{values}|{pair}|{kind}"]["all"]
                s, lo, hi = cell["test"]
                rows.append([plabel, klabel, str(cell["windows"]), str(cell["effective"]),
                             f"{pct(s)} ({pct(cell['gated'][0])}) [{pct(lo)}, {pct(hi)}]"])
        out += table(["pair", "series", "windows", "effective", "test (gated) [interval]"], rows) + [""]
    rows = []
    for pair, plabel in pairs.items():
        cell = published["replay"][f"{pair}|all|real|250"]["all"]
        e3 = published["replay"][f"{pair}|all|E3|250"]["all"]
        rows.append([plabel, pct(cell["a1.test"][0]), pct(cell["a2.test"][0]), pct(e3["a1.test"][0]), pct(e3["a2.test"][0])])
    out += [
        "### What #792's tables described", "",
        "#792 labelled its families a1 and a2 \"the current test\". They are the test's *form* (the studentized mean at the spent "
        "levels) with each pair's critical values calibrated on that pair's own series at 250 days (circular blocks for a1, the "
        "path generator for a2). They are not the test in force, whose two values are the same for every pair (#833). Its 250-day "
        "figures on the same windows, relabelled:", "",
        *table(["pair", "per-pair a1, real", "per-pair a2, real", "per-pair a1, sign-flipped", "per-pair a2, sign-flipped"], rows), "",
    ]
    return out


def render():
    old, new = load("protocol-calibration", "result.json"), load("protocol-calibration-873", "result.json")
    p_old, p_new = load("power-study-769", "result.json"), load("power-study-873", "result.json")
    published, replay = load("power-replay-754", "result.json"), load("power-replay-873", "result.json")
    lines = [
        "# Calibrated values in the candidate orientation: result (H1 step 4, #873)", "",
        "**Development and simulated data only; no verdict, no lockbox day scored.** Every figure below is read from "
        "`docs/research/protocol-calibration-873/result.json`, `power-study-873/result.json` and `power-replay-873/result.json` "
        "by `scripts/orientation_873.py report`; the amendment that would put the new values in force is a draft decision record "
        "(`docs/decisions/scoring-protocol.md`) for Eleonora to merge, and `scoring_protocol.CRITICAL_VALUES` and "
        "`FUTILITY_CRITICAL_VALUES` are unchanged by this pull request.", "",
        *calibration_section(old, new), *power_section(p_old, p_new), *replay_section(published, replay),
    ]
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("report", "check"))
    args = parser.parse_args(argv)
    text = render()
    if args.command == "report":
        PAGE.write_text(text, encoding="utf-8")
        print("wrote", PAGE)
        return 0
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != text:
        print("the page is not what the records give; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
