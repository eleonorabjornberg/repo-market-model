"""The judge's candidates under both false-alarm rules (#454): a scratch comparison, not a record.

    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule unweighted \
        --output OUT/judge_flat.json IN/*_h?.json
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule weighted \
        --output OUT/judge_weighted.json IN/*_h?.json
    PYTHONPATH=src python3 scripts/weighted_miss.py table OUT/judge_flat.json OUT/judge_weighted.json \
        --output OUT/table.md

Both runs score 2018-06-29 to 2025-12-31 and nothing later (`docs/decisions/lockbox.md`); the file refuses a judge
result in the single-look mode. Under the unweighted rule the flag cut-offs are chosen on the flat count of false
alarms, under the weighted rule on the weighted count (`docs/decisions/weighted-miss.md`, a draft). The table reads,
for each candidate, the onset-warning tier (lead at least 1) of each run, tiers 3 and 5, and the same flags' cost
under the other count.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

LEAD = "lead_at_least_1"


def _yes(value):
    return "–" if value is None else ("pass" if value else "fail")


def _f(value):
    return "–" if value is None else f"{value:.2f}"


def _near(candidate):
    return candidate["tiers"]["onset_warning"].get(LEAD, {})


def _read(path):
    result = json.loads(Path(path).read_text())
    if result.get("mode") != "development":
        raise SystemExit(f"{path} is not a development-mode judge result; the 2026 tier is not compared (lockbox.md)")
    return result


def _rule_applied(result):
    rule = result["declaration"].get("weighted_miss")
    return None if rule is None else rule["applied"]


def regime_rows(flat, weighted):
    """Per candidate and regime: onsets, onsets flagged and the worst horizon's false alarms, under both rules."""

    rows = []
    for name in sorted(flat["candidates"]):
        for label, run in (("unweighted", flat), ("weighted", weighted)):
            near = _near(run["candidates"][name])
            for regime, cell in sorted(near.get("by_regime", {}).items()):
                horizons = cell["false_alarms_by_horizon"]
                worst_flat = max(h["flat"] for h in horizons.values())
                worst_weighted = max(h["weighted"] for h in horizons.values())
                rows.append((name, label, regime, cell["onsets"], cell["onsets_flagged"], worst_flat, worst_weighted))
    return rows


def table(flat, weighted):
    if _rule_applied(flat) is not False or _rule_applied(weighted) is not True:
        raise SystemExit("the first file must be a --rule unweighted run and the second a --rule weighted run")
    if flat["scored_window"] != weighted["scored_window"]:
        raise SystemExit("the two runs scored different windows")
    names = sorted(set(flat["candidates"]) & set(weighted["candidates"]))
    lines = [
        f"Scored days {flat['scored_window']['first']} to {flat['scored_window']['last']}; tier 1 at lead >= 1, +5 bp, "
        "limit 2 per onset; h = 1 to 5.",
        "",
        "Table 1. Each candidate under the unweighted rule (the current bar) and the weighted rule (the draft). "
        "False alarms per onset are the worst horizon's. 'flat' counts every false alarm as 1, 'weighted' by its "
        "distance to a pressure day. Each rule chooses its own flag cut-offs.",
        "",
        "| candidate | onsets | warned, unweighted rule | warned, weighted rule | FA/onset, unweighted rule (flat / weighted) "
        "| FA/onset, weighted rule (flat / weighted) | tier 1, unweighted | tier 1, weighted | tier 3 (unw. / w.) "
        "| tier 5 (unw. / w.) |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name in names:
        a, b = flat["candidates"][name], weighted["candidates"][name]
        na, nb = _near(a), _near(b)
        if "unavailable" in na or "unavailable" in nb:
            lines.append(f"| {name} | – | – | – | – | – | – | – | – | – |")
            continue
        va, vb = a["verdict"], b["verdict"]
        lines.append(
            f"| {name} | {na['onsets']} | {na['onsets_flagged']} | {nb['onsets_flagged']} "
            f"| {_f(na['worst_false_alarms_per_onset'])} / {_f(na.get('worst_weighted_false_alarms_per_onset'))} "
            f"| {_f(nb['worst_false_alarms_per_onset'])} / {_f(nb.get('worst_weighted_false_alarms_per_onset'))} "
            f"| {_yes(va['tier_1_onset_warning'])} | {_yes(vb['tier_1_onset_warning'])} "
            f"| {_yes(va['tier_3_no_crying_wolf'])} / {_yes(vb['tier_3_no_crying_wolf'])} "
            f"| {_yes(va['tier_5_week_ahead'])} / {_yes(vb['tier_5_week_ahead'])} |"
        )
    lines += [
        "",
        "Table 2. The same split by regime: onsets, onsets warned, and the worst horizon's false alarms (flat / weighted "
        "count), per candidate under each rule.",
        "",
        "| candidate | rule | regime | onsets | warned | false alarms (flat / weighted) |",
        "|---|---|---|---|---|---|",
    ]
    for name, label, regime, onsets, flagged, worst_flat, worst_weighted in regime_rows(flat, weighted):
        lines.append(f"| {name} | {label} | {regime} | {onsets} | {flagged} | {worst_flat} / {worst_weighted:.2f} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("table")
    command.add_argument("unweighted", type=Path)
    command.add_argument("weighted", type=Path)
    command.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    text = table(_read(args.unweighted), _read(args.weighted))
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
