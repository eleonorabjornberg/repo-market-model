#!/usr/bin/env python3
"""The OFR cleared-repo comparison of #968, re-run with the lag counted on days the government is open (#1016, of finding #1003).

A scratch measurement, not a record: nothing is selected, no model changes, no published declaration changes, and no day in a
locked tier is read. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.

`ofr_stfm_repo_cleared` counted its one-day lag on panel rows, which are SOFR publication days, so on the three statutory holidays
the market opened (2021-06-18, 2021-12-31, 2023-11-10) the value dated the day before was read at 15:00 on the holiday, before the
OFR published it. `repo_model.government_calendar.government_open_dating()` counts it on the days the government is open. The
screen scripts take `--government-open-days` to run inside it. The commands are in `docs/research/ofr-cleared-holidays-1016.md`.

    scripts/ofr_cleared_lag_968.py compare SCREEN_GOV.json --government-open-days --output OUT/screen_compare.json --markdown OUT/screen_compare.md
    scripts/ofr_cleared_holidays_1016.py gbm --runs RUNS --output OUT/gbm.json
    scripts/ofr_cleared_holidays_1016.py page --screen OUT/screen_compare.json --gbm OUT/gbm.json --output OUT/page_tables.md

`gbm` reads only the corrected reading's runs (`ofr_dvp_minus_bgcr_bp@1d` under the new dating) and classifies it under the
same narrow Holm family as #968; `page` sets it beside #968's two readings, read from `docs/research/ofr-cleared-lag-968/`.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

_spec = importlib.util.spec_from_file_location("ofr_cleared_lag_968", REPO / "scripts" / "ofr_cleared_lag_968.py")
lag968 = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = lag968
_spec.loader.exec_module(lag968)

from repo_model.dvp_segment import BENCHMARKS, HORIZONS, ONSET, POOLED, THRESHOLDS, comparison_key  # noqa: E402

EVIDENCE_968 = REPO / "docs" / "research" / "ofr-cleared-lag-968"
GROUP = lag968.GROUP
CORRECTED = (GROUP + "@1d", "government-open days (#1016)")
#: The three readings, in the order the tables use: #968's declared and panel-row readings, then this directive's.
LABELS = ((GROUP, "declared (2 days)"), (GROUP + "@1d", "panel rows (#968)"), ("corrected", "government-open days (#1016)"))


def gbm_command(args) -> int:
    result = lag968.gbm(args.runs, readings=(CORRECTED,))
    result["directive"] = "#1016"
    result["status"] = "scratch measurement; development data, not a verdict; nothing published moves"
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"outcome": result["outcomes"][CORRECTED[0]]["outcome"]}))
    return 0


def _entry(old: Mapping, new: Mapping, label: str, key_tail: str) -> Mapping:
    if label == "corrected":
        return new["comparisons"][f"{CORRECTED[0]}|{key_tail}"]
    return old["comparisons"][f"{label}|{key_tail}"]


def tables(screen: Mapping, new: Mapping, old: Mapping) -> str:
    out: List[str] = ["## Screen: pooled Spearman correlation at lead 1, and rank at the strongest lead", ""]
    out += ["| series | declared (2 days) | panel rows (#968) | government-open days (#1016) | rank, declared / #968 / #1016 |", "|---|---|---|---|---|"]
    prior = json.loads((EVIDENCE_968 / "screen_compare.json").read_text())
    for name, pair in screen["pairs"].items():
        two = pair["pressure_by_lead"]["1"]["two_day"]["rho"]
        panel = prior["pairs"][name]["pressure_by_lead"]["1"]["one_day"]["rho"]
        now = pair["pressure_by_lead"]["1"]["one_day"]["rho"]
        ranks = " / ".join(f"{r[0]} of {r[1]}" for r in (pair["rank_two_day"], prior["pairs"][name]["rank_one_day"], pair["rank_one_day"]))
        out.append(f"| `{name}` | {two:+.4f} | {panel:+.4f} | {now:+.4f} | {ranks} |")
    out += ["", "## Paired test (#187) for `ofr_dvp_minus_bgcr_bp`: Brier difference, benchmark minus candidate, and one-sided p", ""]
    out += ["| day set | h | comparison | declared (2 days) | panel rows (#968) | government-open days (#1016) |", "|---|---|---|---|---|---|"]
    for day_set in (POOLED, ONSET):
        for h in HORIZONS:
            for tau in THRESHOLDS:
                for bench in BENCHMARKS:
                    tail = comparison_key("", "brier", day_set, tau, h, bench).split("|", 1)[1]
                    cells = []
                    for _name, label in LABELS:
                        e = _entry(old, new, _name, tail)
                        cells.append(f"{lag968._iv(e)}; p {e['p_improve']:.4f}")
                    out.append(f"| {day_set} | {h} | +{tau} bp vs {bench} | " + " | ".join(cells) + " |")
    out += ["", "## CRPS, horizon 1: control minus candidate, bp", "", "| reading | CRPS candidate | difference | p improve |", "|---|---|---|---|"]
    for _name, label in LABELS:
        e = _entry(old, new, _name, "crps")
        out.append(f"| {label} | {e['candidate_crps_bps']:.4f} | {lag968._iv(e)} | {e['p_improve']:.4f} |")
    out += ["", "## The win rule (#187), as `dvp_segment.classify` reads it", "", "| reading | outcome | +5 bp | +10 bp |", "|---|---|---|---|"]
    for name, label in LABELS:
        verdict = (new if name == "corrected" else old)["outcomes"][CORRECTED[0] if name == "corrected" else name]
        cells = []
        for tau in ("5", "10"):
            t = verdict["by_threshold"][tau]
            cells.append(f"{t['outcome']}; survives at h={t['horizons_surviving_correction'] or '–'}")
        out.append(f"| {label} | **{verdict['outcome']}** | " + " | ".join(cells) + " |")
    out.append("")
    return "\n".join(out)


def page_command(args) -> int:
    screen = json.loads(args.screen.read_text())
    new = json.loads(args.gbm.read_text())
    old = json.loads((EVIDENCE_968 / "gbm.json").read_text())
    args.output.write_text(tables(screen, new, old), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("gbm")
    one.add_argument("--runs", type=Path, required=True)
    one.add_argument("--output", type=Path, required=True)
    one.set_defaults(func=gbm_command)
    two = sub.add_parser("page")
    two.add_argument("--screen", type=Path, required=True)
    two.add_argument("--gbm", type=Path, required=True)
    two.add_argument("--output", type=Path, required=True)
    two.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
