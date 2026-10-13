"""Before and after the Fed repo data meaning, for the screens that read its columns (#692): a scratch comparison, not a record.

#659 changed the Fed repo take-up columns on the 2018-05 to 2019-09 rows (the six test operations are left out, and
`fed_repo_days_since_positive` stays at its cap until the facility's first day). Eleonora asked (13 October 2026, #692) for the
screens that read them to be re-run unchanged but for the data. This file compares two runs of one screen on the same tree, the
"before" on a throwaway copy with #659's commit reverted, the "after" on the tree as it is. It reads the JSON the screens
write, scores nothing and reads no 2026 day (`docs/decisions/lockbox.md`).

    PYTHONPATH=src python3 scripts/fed_rescreen_692.py screens --before-screen B/screen.json --after-screen A/screen.json \
        --before-matrix B/source_matrix.json --after-matrix A/source_matrix.json --output-json OUT/screens.json --output-md OUT/screens.md

Exploration on development data: nothing here is a verdict under scoring protocol v1 (#640).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

#: The columns #659 changed (`fed_liquidity`), by prefix. Any other series that moves is a finding.
FED_PREFIX = ("fed_repo_",)
TOLERANCE = 1e-12
LEADS = ("1", "2", "3", "5", "10")


def leaf_diffs(before: Any, after: Any, path: Tuple[str, ...] = ()) -> List[Tuple[Tuple[str, ...], Any, Any]]:
    """Every leaf that differs, by path: a number beyond 1e-12, another value, or a key present on one side only."""

    if isinstance(before, dict) and isinstance(after, dict):
        out: List[Tuple[Tuple[str, ...], Any, Any]] = []
        for key in sorted(set(before) | set(after), key=str):
            if key not in before:
                out.append((path + (str(key),), None, after[key]))
            elif key not in after:
                out.append((path + (str(key),), before[key], None))
            else:
                out.extend(leaf_diffs(before[key], after[key], path + (str(key),)))
        return out
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        out = []
        for i, (b, a) in enumerate(zip(before, after)):
            out.extend(leaf_diffs(b, a, path + (str(i),)))
        return out
    if isinstance(before, (int, float)) and isinstance(after, (int, float)) and not isinstance(before, bool) and not isinstance(after, bool):
        return [] if abs(float(before) - float(after)) <= TOLERANCE else [(path, before, after)]
    return [] if before == after else [(path, before, after)]


def series_of(diffs: Sequence[Tuple[Tuple[str, ...], Any, Any]], section: str) -> Set[str]:
    """The series that moved under `section`: the second path element, or the third under `incremental/cells`."""

    names: Set[str] = set()
    for path, _, _ in diffs:
        if path[0] != section:
            continue
        if section == "incremental":
            if len(path) > 2 and path[1] == "cells":
                names.add(path[2])
        elif len(path) > 1:
            names.add(path[1])
    return names


def outside(names: Set[str], prefixes: Sequence[str]) -> Set[str]:
    return {name for name in names if not name.startswith(tuple(prefixes))}


def _rho(series: Dict[str, Any], lead: str) -> Optional[float]:
    return (((series.get("leads") or {}).get(lead) or {}).get("all") or {}).get("pressure", {}).get("rho")


def screen_ranks(series: Dict[str, Any]) -> Dict[str, int]:
    """Rank by the strongest absolute Spearman correlation with the pressure indicator over the leads (the screen's own order)."""

    strongest = {}
    for name, body in series.items():
        values = [abs(v) for v in (_rho(body, lead) for lead in (body.get("leads") or {})) if v is not None]
        if values:
            strongest[name] = max(values)
    ordered = sorted(strongest, key=lambda n: (-strongest[n], n))
    return {name: i + 1 for i, name in enumerate(ordered)}


def _fmt(value: Optional[float], places: int = 3) -> str:
    return "–" if value is None else f"{value:+.{places}f}"


def _arrow(before: Optional[float], after: Optional[float]) -> str:
    return f"{_fmt(before)} → {_fmt(after)}"


def _interval(auc: Optional[float], interval: Optional[Sequence[float]]) -> str:
    if auc is None:
        return "–"
    if not interval:
        return f"{auc:.3f}"
    return f"{auc:.3f} [{interval[0]:.3f}, {interval[1]:.3f}]"


def _clear_of(interval: Optional[Sequence[float]], line: float) -> Optional[bool]:
    return None if not interval else not (interval[0] <= line <= interval[1])


def fed_names(names: Sequence[str]) -> List[str]:
    return sorted(n for n in names if n.startswith(tuple(FED_PREFIX)))


def compare_screens(b1: Dict[str, Any], a1: Dict[str, Any], b2: Dict[str, Any], a2: Dict[str, Any]) -> Dict[str, Any]:
    """The comparison of the source screen (#620-era, `source_screen.py`) and the source matrix (#629)."""

    diffs1 = leaf_diffs({"series": b1["series"]}, {"series": a1["series"]})
    moved1 = series_of(diffs1, "series")
    diffs2 = leaf_diffs({k: b2[k] for k in ("correlations", "bootstrap", "incremental")}, {k: a2[k] for k in ("correlations", "bootstrap", "incremental")})
    moved2 = series_of(diffs2, "correlations") | series_of(diffs2, "bootstrap") | series_of(diffs2, "incremental")
    ranks_b, ranks_a = screen_ranks(b1["series"]), screen_ranks(a1["series"])
    clusters = {}
    for key in ("ordinary_pooled", "all_pooled"):
        before = sorted(sorted(c["members"]) for c in b2["clusters"][key])
        after = sorted(sorted(c["members"]) for c in a2["clusters"][key])
        clusters[key] = {"same_groups": before == after,
                         "only_before": [c for c in before if c not in after], "only_after": [c for c in after if c not in before]}
    return {
        "screen": {"series_moved": sorted(moved1), "outside_fed_columns": sorted(outside(moved1, FED_PREFIX)),
                   "rank_before": {n: ranks_b.get(n) for n in fed_names(b1["series"])},
                   "rank_after": {n: ranks_a.get(n) for n in fed_names(a1["series"])},
                   "top_10_same": [n for n, r in sorted(ranks_b.items(), key=lambda x: x[1])][:10] == [n for n, r in sorted(ranks_a.items(), key=lambda x: x[1])][:10],
                   "ranks_moved_outside_fed": sorted(n for n in ranks_b if not n.startswith(tuple(FED_PREFIX)) and ranks_b[n] != ranks_a.get(n))},
        "matrix": {"series_moved": sorted(moved2), "outside_fed_columns": sorted(outside(moved2, FED_PREFIX)), "clusters": clusters,
                   "incremental_top_same": b2["incremental"]["top"] == a2["incremental"]["top"],
                   "incremental_top_before": b2["incremental"]["top"], "incremental_top_after": a2["incremental"]["top"]},
    }


def markdown(b1, a1, b2, a2, result) -> str:
    out: List[str] = []
    out.append("# Fed repo re-screen: the source screen and the source matrix, before and after #659 (#692)\n")
    out.append("Exploration on development data (scored days 2018-06-29 to 2025-12-31); not a verdict under scoring protocol v1. \"Before\" is the same tree with")
    out.append("#659's commit reverted, \"after\" is the tree as it is, so only the Fed repo columns differ between the two.\n")
    s, m = result["screen"], result["matrix"]
    out.append("## What moved\n")
    out.append(f"- Source screen: {len(s['series_moved'])} of {len(a1['series'])} series have a changed cell; outside the `fed_repo_*` columns: "
               f"{', '.join('`%s`' % n for n in s['outside_fed_columns']) or 'none'}.")
    out.append(f"- Source matrix: {len(m['series_moved'])} of {len(a2['names'])} series have a changed correlation, AUROC, pre-onset or partial cell; outside the "
               f"`fed_repo_*` columns: {', '.join('`%s`' % n for n in m['outside_fed_columns']) or 'none'}.")
    out.append(f"- Source screen, the ten strongest series: {'the same, in the same order' if s['top_10_same'] else 'changed'}. "
               f"Series outside the `fed_repo_*` columns whose rank changed (the ranks move when a Fed series passes them): "
               f"{len(s['ranks_moved_outside_fed'])}.")
    for key, label in (("ordinary_pooled", "ordinary days, pooled"), ("all_pooled", "all days, pooled")):
        c = m["clusters"][key]
        out.append(f"- Source matrix, groups at |rho| >= 0.8 ({label}): {'unchanged' if c['same_groups'] else 'changed'}"
                   + ("" if c["same_groups"] else f"; before only {c['only_before']}; after only {c['only_after']}") + ".")
    out.append(f"- Source matrix, the 15 series taken into the incremental step: {'unchanged' if m['incremental_top_same'] else 'changed'}"
               + ("" if m["incremental_top_same"] else f"; before {m['incremental_top_before']}; after {m['incremental_top_after']}") + ".\n")
    out.append("## Table 1. Source screen: Spearman with the +5 bp indicator, all scored days (before → after), and rank\n")
    out.append("| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | rank (of %d) |" % len(a1["series"]))
    out.append("|---|---|---|---|---|---|---|")
    for name in fed_names(a1["series"]):
        cells = [_arrow(_rho(b1["series"].get(name, {}), lead), _rho(a1["series"].get(name, {}), lead)) for lead in LEADS]
        out.append(f"| `{name}` | " + " | ".join(cells) + f" | {s['rank_before'].get(name) or '–'} → {s['rank_after'].get(name) or '–'} |")
    out.append("\n## Table 2. Source matrix, ordinary days: Spearman with the +5 bp indicator, pooled (before → after)\n")
    out.append("| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 |")
    out.append("|---|---|---|---|---|---|")
    for name in fed_names(a2["names"]):
        cells = []
        for lead in LEADS:
            cells.append(_arrow(*[(d["correlations"].get(name, {}).get(lead, {}).get("pooled", {}).get("pressure") or {}).get("rho") for d in (b2, a2)]))
        out.append(f"| `{name}` | " + " | ".join(cells) + " |")
    out.append("\n## Table 3. Source matrix, ordinary days: AUROC of the series for pressure days against other ordinary days, with the 90% interval (before → after)\n")
    out.append("| series | lead 1, pooled | lead 1, 2018-19 | pre-onset AUC, pooled | clear of 0.5 at lead 1 pooled (before → after) |")
    out.append("|---|---|---|---|---|")
    for name in fed_names(a2["names"]):
        row = []
        for split in ("pooled", "regime:2018-19"):
            vals = [(d["bootstrap"].get(name, {}).get("auroc", {}).get("1", {}).get(split) or {}) for d in (b2, a2)]
            row.append(" → ".join(_interval(v.get("auc"), v.get("interval")) for v in vals))
        pre = [(d["bootstrap"].get(name, {}).get("pre_onset", {}).get("pooled") or {}) for d in (b2, a2)]
        row.append(" → ".join(_interval(v.get("auc"), v.get("auc_interval")) for v in pre))
        clear = [_clear_of((d["bootstrap"].get(name, {}).get("auroc", {}).get("1", {}).get("pooled") or {}).get("interval"), 0.5) for d in (b2, a2)]
        row.append(" → ".join({True: "yes", False: "no", None: "–"}[c] for c in clear))
        out.append(f"| `{name}` | " + " | ".join(row) + " |")
    cells_b, cells_a = b2["incremental"]["cells"], a2["incremental"]["cells"]
    shared = [n for n in fed_names(list(cells_a)) if n in cells_b]
    if shared or fed_names(list(cells_a)) or fed_names(list(cells_b)):
        out.append("\n## Table 4. Source matrix, incremental step: partial Spearman with the pressure indicator after the scarcity state and the tail spread (before → after)\n")
        out.append("| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 |")
        out.append("|---|---|---|---|---|---|")
        for name in sorted(set(fed_names(list(cells_a))) | set(fed_names(list(cells_b)))):
            out.append(f"| `{name}` | " + " | ".join(
                _arrow(*[(((c.get(name) or {}).get(lead) or {}).get("pressure") or {}).get("partial") for c in (cells_b, cells_a)]) for lead in LEADS) + " |")
    return "\n".join(out) + "\n"


def screens_command(args) -> int:
    b1, a1 = (json.loads(p.read_text(encoding="utf-8")) for p in (args.before_screen, args.after_screen))
    b2, a2 = (json.loads(p.read_text(encoding="utf-8")) for p in (args.before_matrix, args.after_matrix))
    for label, doc in (("before screen", b1), ("after screen", a1), ("before matrix", b2), ("after matrix", a2)):
        last = (doc.get("scope") or {}).get("last_day")
        if last is not None and last > "2025-12-31":
            raise SystemExit(f"{label} scores {last}, past 2025-12-31: the lockbox (docs/decisions/lockbox.md) forbids it")
    result = compare_screens(b1, a1, b2, a2)
    args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(markdown(b1, a1, b2, a2, result), encoding="utf-8")
    print(json.dumps({"screen_series_moved": len(result["screen"]["series_moved"]), "matrix_series_moved": len(result["matrix"]["series_moved"]),
                      "outside_screen": result["screen"]["outside_fed_columns"], "outside_matrix": result["matrix"]["outside_fed_columns"]}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("screens", help="compare two runs of the source screen and the source matrix")
    for name in ("before-screen", "after-screen", "before-matrix", "after-matrix"):
        s.add_argument("--" + name, type=Path, required=True)
    s.add_argument("--output-json", type=Path, required=True)
    s.add_argument("--output-md", type=Path, required=True)
    s.set_defaults(func=screens_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
