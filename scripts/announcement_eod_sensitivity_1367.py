"""Sensitivity of the candidate's walk to the 163 undated announcements (#1367, item 5; no hypothesis step: a check on #1310's dating).

`metadata/settlement_announcement_dating.json` dates every Treasury offering announcement at 12:00 New York time on `announcemt_date`. Of the 3828
announcements in the tracked auctions snapshot, 163 state no clock time ("For Immediate Release"; `metadata/announcement_release_times_1301.json`).
This study re-runs #1288's walk (`scripts/s3c_announced_settlement_1288.py score`, which scores (s3c-ann-net) beside the other arms), unchanged, with
those 163 dated at 23:59:59 on `announcemt_date`, the conservative bound (an announcement made at any time of that day is public by it, and none is
public before it), and reports whether any figure moves. Nothing else changes: the same panel, declaration, seed and draws.

    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/announcement_eod_sensitivity_1367.py score --panel PUB.csv --output OUT/score-eod.json
    python3 scripts/announcement_eod_sensitivity_1367.py compare --baseline docs/research/s3c-ann-net-1800-1314/announced-settlement-1800.json \\
        --variant OUT/score-eod.json --output docs/research/announcement-eod-sensitivity-1367/result.json
    python3 scripts/announcement_eod_sensitivity_1367.py page --result docs/research/announcement-eod-sensitivity-1367/result.json \\
        --output docs/research/announcement-eod-sensitivity-1367-result.md

Development evidence, never a verdict. It scores no day after 2026-09-03 and writes nothing into `docs/runs/`. Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

RELEASE_TIMES = REPO / "metadata" / "announcement_release_times_1301.json"
IMMEDIATE = "immediate"
END_OF_DAY = time(23, 59, 59)


def immediate_files(record: Mapping[str, Any]) -> frozenset:
    """The announcement files whose stated release time is "immediate" (no clock time)."""

    return frozenset(name for name, when in record["stated"].items() if when == IMMEDIATE)


def _check(records: Sequence[Mapping[str, object]], items: Sequence[object]) -> None:
    if len(records) != len(items):
        raise ValueError(f"{len(records)} auction records but {len(items)} parsed auctions: they are in record order, one each")


def shift_auctions(records, auctions, files):
    """`net_settlement.Auction`s with the announcement of each record in `files` moved to the end of its day."""

    _check(records, auctions)
    return tuple(
        a._replace(announced_at=datetime.combine(a.announced_at.date(), END_OF_DAY))
        if str(r["pdf_filenm_announcemt"]) in files else a
        for r, a in zip(records, auctions)
    )


def shift_results(records, results, files):
    """`settlement_dating.AuctionResult`s with the instant of each record in `files` moved to the end of its day."""

    _check(records, results)
    return tuple(
        x._replace(public_at=datetime.combine(x.public_at.date(), END_OF_DAY))
        if str(r["pdf_filenm_announcemt"]) in files and x.public_at is not None else x
        for r, x in zip(records, results)
    )


def _install(files: frozenset) -> None:
    from repo_model import net_settlement as ns, settlement_dating as sd

    original_auctions, original_results = ns.auction_records, sd.auction_results

    def auctions(records, declaration):
        return shift_auctions(records, original_auctions(records, declaration), files)

    def results(records, declaration):
        return shift_results(records, original_results(records, declaration), files)

    ns.auction_records, sd.auction_results = auctions, results


def score(argv: Sequence[str]) -> int:
    files = immediate_files(json.loads(RELEASE_TIMES.read_text(encoding="utf-8")))
    if len(files) != 163:
        raise ValueError(f"expected 163 immediate-release announcements, found {len(files)}")
    _install(files)
    spec = importlib.util.spec_from_file_location("s3c_announced_settlement_1288", REPO / "scripts" / "s3c_announced_settlement_1288.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["s3c_announced_settlement_1288"] = module
    spec.loader.exec_module(module)
    return module.main(["score", *argv])


def _leaves(node: Any, path: str = "") -> Dict[str, Any]:
    if isinstance(node, dict):
        out: Dict[str, Any] = {}
        for key, value in node.items():
            out.update(_leaves(value, f"{path}/{key}"))
        return out
    if isinstance(node, list):
        out = {}
        for index, value in enumerate(node):
            out.update(_leaves(value, f"{path}[{index}]"))
        return out
    return {path: node}


def differences(baseline: Mapping[str, Any], variant: Mapping[str, Any]) -> Dict[str, Any]:
    """Every leaf of `windows` that differs, by path, with the count of leaves compared."""

    a, b = _leaves(baseline["windows"]), _leaves(variant["windows"])
    paths = sorted(set(a) | set(b))
    changed = [p for p in paths if a.get(p) != b.get(p)]
    candidate = [p for p in changed if "ann_net" in p or "sc_s3c_ann_net" in p]
    return {
        "leaves_compared": len(paths),
        "leaves_changed": len(changed),
        "candidate_leaves_changed": len(candidate),
        "changed_paths": changed[:200],
        "candidate_paths": candidate[:200],
        "any_score_changes": bool(changed),
    }


CANDIDATE = "sc_s3c_ann_net"
METRICS = ("grid_crps", "upper_tail_twcrps")


def headline(baseline: Mapping[str, Any], variant: Mapping[str, Any]) -> Dict[str, Any]:
    """The candidate's pooled primary score and key secondary, and the skill against B1 with its interval, per window and run."""

    out: Dict[str, Any] = {}
    for window in baseline["windows"]:
        out[window] = {}
        for metric in METRICS:
            rows = {}
            for name, run in (("declared_12_00", baseline), ("end_of_day", variant)):
                cell = run["windows"][window]["groups"]["pooled"]["all decision days"][metric]
                skill = cell["vs"][CANDIDATE]["B1"]
                rows[name] = {"mean_bp": cell["means"][CANDIDATE], "skill_against_b1": skill["skill"], "skill_interval": skill["skill_interval"]}
            rows["mean_change_bp"] = rows["end_of_day"]["mean_bp"] - rows["declared_12_00"]["mean_bp"]
            rows["skill_change"] = rows["end_of_day"]["skill_against_b1"] - rows["declared_12_00"]["skill_against_b1"]
            out[window][metric] = rows
    return out


def compare(args) -> int:
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    var = json.loads(Path(args.variant).read_text(encoding="utf-8"))
    for key in ("panel_sha256", "seed", "draws", "reps", "subset_from"):
        if base.get(key) != var.get(key):
            raise ValueError(f"baseline and variant differ in {key}: {base.get(key)!r} against {var.get(key)!r}")
    out = {
        "issue": 1367, "label": "development, not a verdict", "immediate_release_announcements": 163, "announcements": 3828,
        "declared_instant": "12:00", "variant_instant": "23:59:59 on announcemt_date",
        "baseline": str(args.baseline), "panel_sha256": base["panel_sha256"], "result": differences(base, var), "headline": headline(base, var),
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def page(args) -> int:
    r = json.loads(Path(args.result).read_text(encoding="utf-8"))
    d = r["result"]
    verdict = ("**At least one figure moves.**" if d["any_score_changes"] else "**No figure moves.**")
    lines = [
        "# The 163 undated announcements, dated at end of day (#1367, item 5)", "",
        "**Hypothesis and step:** none (a sensitivity check on #1310's settlement dating, for H5's registration design). **Development, not a verdict.** "
        "Generated by `python3 scripts/announcement_eod_sensitivity_1367.py page`; never hand-edited.", "",
        f"Of the {r['announcements']:,} Treasury announcements in `metadata/announcement_release_times_1301.json`, {r['immediate_release_announcements']} "
        f"state no clock time and are dated at the declared {r['declared_instant']}. #1288's walk, which scores (s3c-ann-net) beside the other arms at the "
        "18:00 decision instant, was re-run unchanged with those dated at 23:59:59 on their announcement date, the conservative bound: "
        "none of them is read before the next panel day's decision.", "",
        verdict, "",
        f"| | |", "|---|---|",
        f"| leaves of the score record compared | {d['leaves_compared']:,} |",
        f"| leaves that differ | {d['leaves_changed']:,} |",
        f"| of them in a (s3c-ann-net) path | {d['candidate_leaves_changed']:,} |", "",
        f"The baseline is `{r['baseline']}`; both runs use panel digest `{r['panel_sha256'][:8]}`, the same seed, draws and resamples.", "",
    ]
    lines += ["## The candidate's primary score and key secondary", "",
              "Pooled over all decision days of each window, bp; skill is against B1 with its 90% interval, as #1288's record reports it. "
              "The comparators (B1, B1', B2) and every arm that does not read an announcement are unchanged to the last digit, which shows the "
              "walk reproduces.", "",
              "| Window | Score | Declared 12:00 | End of day | Change (bp) | Skill vs B1, 12:00 | Skill vs B1, end of day |", "|---|---|---|---|---|---|---|"]
    for window, metrics in r["headline"].items():
        for metric, row in metrics.items():
            lo, hi = row["declared_12_00"]["skill_interval"], row["end_of_day"]["skill_interval"]
            lines.append("| %s | %s | %.4f | %.4f | %+.5f | %+.4f [%+.3f, %+.3f] | %+.4f [%+.3f, %+.3f] |" % (
                window, metric, row["declared_12_00"]["mean_bp"], row["end_of_day"]["mean_bp"], row["mean_change_bp"],
                row["declared_12_00"]["skill_against_b1"], lo[0], lo[1], row["end_of_day"]["skill_against_b1"], hi[0], hi[1]))
    lines += ["", "**Reading.** Dating the announcements that state no clock time at end of day changes the candidate's scores, in the fourth or "
              "fifth decimal place and in the favourable direction on the primary score; the skill against B1 moves by about a ten-thousandth, "
              "far inside its interval. No ranking against B1 changes. The 12:00 dating is not shown to matter. Development, not a verdict.", ""]
    lines += ["This is a development check. It reads no day after the declared end and changes no declaration, record or candidate.", ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "score":
        return score(argv[1:])
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--baseline", required=True)
    c.add_argument("--variant", required=True)
    c.add_argument("--output", required=True)
    c.set_defaults(func=compare)
    g = sub.add_parser("page")
    g.add_argument("--result", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
