"""#1196's (s3) terms study re-scored on current main, with what changed against the committed score (#1243, #1247; H5 step 3).

A development study, never a verdict (scoring protocol v1, #640). Her ruling of 26 October 2026 (ledger item 59 on #1116, option 1 on
finding #1243): re-run #1196's declared setup on current main, unchanged (same arms, seed, draws, panel and block, the current scorer),
and publish it anew beside the old page, which stays as the record of what was run.

The scoring is `scripts/s3_terms_1196.py score`, unchanged. This script adds the stage-by-stage comparison: the committed
`docs/research/s3-terms-1196/result.json` is stage 0, and each later stage is the same `score` command run on a named commit of main
(the merge of one change, in the order main took them), the last being the tree of this branch. A row (a paired comparison with a
`days` count and a mean-d bound or a reason for none) is compared at the same path in each pair of consecutive stages. A change is
attributed to the first stage at which the row's content differs from the stage before it, and the stage lists the merged changes that
came with it; where a stage carries more than one change that can reach the scorer, the page says so and does not split it.

    # per stage commit C, in a clone of main at C (the declaration is read from that tree):
    PYTHONPATH=src python3 scripts/s3_terms_1196.py score --panel PUB.csv --output stage_C.json
    python3 scripts/s3_terms_rescore_1243.py build --score NEW.json --stage LABEL=COMMIT=CHANGES=stage_C.json ... \\
        --old docs/research/s3-terms-1196/result.json --base-sha SHA --output docs/research/s3-terms-1243/result.json
    python3 scripts/s3_terms_rescore_1243.py page --score docs/research/s3-terms-1243/result.json \\
        --output docs/research/s3-terms-1243-result.md

with PUB.csv the published panel built as in the docstring of `scripts/s3_terms_1196.py` (digest `4ddc3882…`). Each score takes about
40 minutes on 4 cores. Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
OLD_RESULT = REPO / "docs" / "research" / "s3-terms-1196" / "result.json"
OLD_PAGE = "docs/research/s3-terms-1196-result.md"
RANK = {"loss": 0, "undecided": 1, "gain": 2}
NO_READING = "no reading"
Stage = Tuple[str, str, str, dict]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


d1239 = _load("mean_d_dropped_1239")
walk, _without_rows, _differences = d1239.walk, d1239._without_rows, d1239._differences


def reading(row: Optional[dict]) -> str:
    """The reading of a row from its mean-d bound (#1009, #1172, #1215): gain, loss, undecided, or no reading where the bound
    could not be computed. This is `s3_terms_1196.verdict`'s rule, kept here so that the comparison loads no walk code."""

    if row is None:
        return "undecided"
    if "undefined" in row:
        return NO_READING
    low, high = row["difference_interval"]
    if low > 0:
        return "gain"
    if high < 0:
        return "loss"
    return "undecided"


def move(before: str, after: str) -> str:
    """How a reading moved: improved or worsened (on the order loss, undecided, gain), lost its reading, gained one, or same."""

    if before == after:
        return "same"
    if after == NO_READING:
        return "lost its reading"
    if before == NO_READING:
        return "gained a reading"
    return "improved" if RANK[after] > RANK[before] else "worsened"


MOVES = ("improved", "worsened", "lost its reading", "gained a reading")


def _same_setup(stages: Sequence[Stage]) -> None:
    first = stages[0][3]
    for label, _, _, d in stages[1:]:
        for key in ("seed", "draws", "panel_sha256"):
            if d.get(key) != first.get(key):
                raise SystemExit(f"stage {label}: {key} differs from the first stage ({d.get(key)!r} against {first.get(key)!r})")


def _lead_days(d: dict) -> Dict[str, int]:
    return {k: v["days"] for k, v in d["groups"]["lead"].items()}


def _days(d: dict) -> Dict[str, int]:
    """Every group's day count, by path (`groups/<kind>/<label>/days`), and the day-type counts."""

    out = {}
    for kind, groups in d["groups"].items():
        for label, entry in groups.items():
            if isinstance(entry, dict) and "days" in entry:
                out[f"groups/{kind}/{label}/days"] = entry["days"]
    for label, n in d.get("day_type_counts", {}).items():
        out[f"day_type_counts/{label}"] = n
    return out


def compare(stages: Sequence[Stage]) -> dict:
    """The stages, in order (label, commit, the changes it carries, score file), compared pair by pair."""

    _same_setup(stages)
    rows = [dict(walk(d)) for _, _, _, d in stages]
    paths = sorted(set().union(*rows), key=lambda p: tuple(map(str, p)))
    transitions: List[dict] = []
    for k in range(1, len(stages)):
        before, after = rows[k - 1], rows[k]
        differing, changes, dropping = 0, 0, 0
        for p in paths:
            a, b = before.get(p), after.get(p)
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                differing += 1
                changes += reading(a) != reading(b) if a is not None and b is not None else 1
                dropping += b is not None and "dropped_resamples" in b and (a is None or "dropped_resamples" not in a)
        transitions.append({
            "from": stages[k - 1][0], "to": stages[k][0], "commit": stages[k][1], "changes": stages[k][2], "rows": len(paths),
            "rows_differing": differing, "reading_changes": changes,
            "rows_with_dropped_resamples": dropping,
            "other_differences": _differences(_without_rows(stages[k - 1][3]), _without_rows(stages[k][3]))})
    reading_rows: List[dict] = []
    overall = {m: 0 for m in MOVES}
    for p in paths:
        reads = [reading(r.get(p)) if p in r else "absent" for r in rows]
        if len(set(reads)) == 1:
            continue
        changed = [stages[k][0] for k in range(1, len(stages)) if reads[k] != reads[k - 1]]
        reading_rows.append({"path": "/".join(map(str, p)), "readings": reads, "changed_at": changed,
                             "move": move(reads[0], reads[-1]) if "absent" not in (reads[0], reads[-1]) else "absent"})
        if reading_rows[-1]["move"] in overall:
            overall[reading_rows[-1]["move"]] += 1
    days = [_days(d) for _, _, _, d in stages]
    day_changes = []
    for k in range(1, len(stages)):
        keys = sorted(set(days[k - 1]) | set(days[k]))
        day_changes.append({"stage": stages[k][0], "moved": [x for x in keys if days[k - 1].get(x) != days[k].get(x)]})
    return {
        "stages": [{"label": s[0], "commit": s[1], "changes": s[2]} for s in stages],
        "transitions": transitions, "overall": dict(overall, rows=len(paths), rows_with_a_changed_reading=len(reading_rows)),
        "reading_rows": reading_rows,
        "lead_days": {h: [_lead_days(d)[h] for _, _, _, d in stages] for h in _lead_days(stages[0][3])},
        "day_changes": day_changes,
        "days_by_stage": {k: [x.get(k) for x in days] for k in sorted(set().union(*days)) if len({x.get(k) for x in days}) > 1}}


# -- the page --------------------------------------------------------------------------------------------------------------


def _name(path: str) -> str:
    return path.replace("groups/", "", 1).replace("/vs/", " vs ").replace("/", " / ")


def section(r: dict) -> List[str]:
    """The section "What changed against #1196": the stages, the day counts by lead, the readings that moved."""

    stages = r["stages"]
    out = ["## What changed against #1196", "",
           f"The committed score of #1196 (`docs/research/s3-terms-1196/result.json`, stage `{stages[0]['label']}`) no longer reproduces on "
           f"main. The same `score` command, with the same declaration, seed, draws and panel, was run on each of the commits below, in "
           f"the order main took them; the last is this tree (base `{r.get('base_sha', '?')}`). A row is a paired comparison; its "
           "reading is taken from the mean-d bound, as on the page being replaced.", "",
           "| stage | commit | merged since the stage before | rows whose content differs | rows whose reading moved | rows with dropped resamples (#1239) |", "|---|---|---|---|---|---|"]
    out.append(f"| {stages[0]['label']} | {stages[0]['commit']} | {stages[0]['changes']} | | | |")
    for t in r["transitions"]:
        out.append(f"| {t['to']} | {t['commit']} | {t['changes']} | {t['rows_differing']} of {t['rows']} | {t['reading_changes']} | {t['rows_with_dropped_resamples']} |")
    out.append("")
    other = [t for t in r["transitions"] if t["other_differences"]]
    if other:
        out += ["Differences outside the rows (a count, a mean, a record): " + "; ".join(
            f"{t['to']}: " + ", ".join(f"`{x}`" for x in t["other_differences"][:6]) for t in other) + ".", ""]
    labels = [s["label"] for s in stages]
    out += ["**Decision days by lead** (the days scored at each lead, at each stage):", "",
            "| lead | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
    for h, v in r["lead_days"].items():
        out.append(f"| {h} | " + " | ".join(str(x) for x in v) + " |")
    out.append("")
    moved_days = {t["stage"]: t["moved"] for t in r["day_changes"] if t["moved"]}
    if moved_days:
        out += ["Day counts that moved, by stage (a group is a lead, the pooled set, a regime or a day type): " + "; ".join(
            f"{stage}: {len(m)} ({', '.join('`' + x + '`' for x in m[:5])}{', …' if len(m) > 5 else ''})" for stage, m in moved_days.items())
            + ". Every count, by stage, is in `result.json`.", ""]
    o = r["overall"]
    out += [f"**Readings.** Of {o['rows']} paired rows, {o['rows_with_a_changed_reading']} have a different reading at some stage. Against "
            f"the committed score, on the last stage: {o['improved']} improved (towards a gain), {o['worsened']} worsened (towards a "
            f"loss), {o['lost its reading']} lost their reading and {o['gained a reading']} gained one (from \"no reading\"). A row whose "
            "mean-d bound moved without its reading moving is counted in the table above and not listed.", ""]
    if r["reading_rows"]:
        out += ["| row | readings at each stage | moved at | against the committed score |", "|---|---|---|---|"]
        for m in r["reading_rows"]:
            out.append(f"| {_name(m['path'])} | " + " → ".join(m["readings"]) + f" | {', '.join(m['changed_at'])} | {m['move']} |")
        out.append("")
    out += ["**Which change explains which.** A stage is the merge of one pull request together with whatever main took between it and "
            "the stage before (the `merged since` column). The change a row moved at is the one named there: the as-of order of a "
            "group's fields is #1060, the B2 thin-pool record in force is #1198, and the no-variance resamples dropped from the "
            "mean-d studentization (with their count) is #1239; the stage named for #1215 is the tree on which the committed file is "
            "reproduced, so a row that moved there would be #1215's reporting change. Where a stage carries other changes that can reach the scorer, a move "
            "at that stage is not attributed to one of them. A change that moved a row at no stage listed, or at the last stage "
            "without the dropped-resample count beside it, is not attributed.", ""]
    return out


HEADER = ("# The scarcity interaction and the FOMC/IORB terms on (s3)'s robust fit (#1196)", "(#1196)")
GENERATED = ("`scripts/s3_terms_1196.py page` from `docs/research/s3-terms-1196/result.json`",
             "`scripts/s3_terms_rescore_1243.py page` from `docs/research/s3-terms-1243/result.json`")


def retitle(body: str) -> str:
    """The page of `scripts/s3_terms_1196.py` as the page of this re-score: a new title, a pointer to its own `result.json`, and a
    note that it replaces the old page, which stays as the record of what was run."""

    if HEADER[0] not in body or GENERATED[0] not in body:
        raise SystemExit("the rendered page does not have the header this script rewrites")
    title = "# The scarcity interaction and the FOMC/IORB terms on (s3)'s robust fit, re-scored on main (#1243)"
    body = body.replace(HEADER[0], title, 1).replace(GENERATED[0], GENERATED[1], 1)
    first, rest = body.split("\n", 1)
    note = (f"\n**This page replaces `{OLD_PAGE}` (#1196), which no longer reproduces on main and is kept as the record of what was "
            "run.** The setup is #1196's, unchanged: the same arms, seed, draws, panel and block, scored with the scorer now on main "
            "(including #1215's mean-d fallback and #1239's dropped-resample count). Where a figure here differs from that page, the "
            "section \"What changed against #1196\" says by how much and at which merged change.\n")
    return first + "\n" + note + rest


def superseded_note(base_sha: str, pr: int, old_base: str) -> str:
    """The dated note put at the top of the old page and in its `result.json` (the rest of both stays byte-identical)."""

    return (f"Superseded on main by #{pr} (finding #1243); kept as the record of what was run on {old_base}. Re-scored on {base_sha}; "
            "see docs/research/s3-terms-1243-result.md. 26 October 2026.")


def page_text(r: dict) -> str:
    """The page for a `result.json` of this script: #1196's page of the new score, retitled, then the section on what changed."""

    flat = dict(r["against_1196"], base_sha=r["base_sha"])
    return retitle(_load("s3_terms_1196").render(r)).rstrip("\n") + "\n\n" + "\n".join(section(flat)) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="write result.json: the new score and the comparison")
    b.add_argument("--score", required=True, help="the score on this tree")
    b.add_argument("--stage", action="append", default=[], help="LABEL=COMMIT=CHANGES=SCOREFILE, in the order main took the changes")
    b.add_argument("--old", default=str(OLD_RESULT))
    b.add_argument("--old-commit", required=True, help="the commit the committed score was run on")
    b.add_argument("--base-sha", required=True)
    b.add_argument("--main-changes", default="this tree", help="what main took since the last stage, for the last row of the table")
    b.add_argument("--output", required=True)
    g = sub.add_parser("page", help="write the result page from result.json")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if args.command == "build":
        stages: List[Stage] = [("committed", args.old_commit, "the committed score of #1196", json.loads(Path(args.old).read_text(encoding="utf-8")))]
        for spec in args.stage:
            label, commit, changes, path = spec.split("=", 3)
            stages.append((label, commit, changes, json.loads(Path(path).read_text(encoding="utf-8"))))
        new = json.loads(Path(args.score).read_text(encoding="utf-8"))
        stages.append(("main", args.base_sha, args.main_changes, new))
        result = dict(new)
        result.update({"issue": 1243, "rescore_of": 1196, "base_sha": args.base_sha, "old_page": OLD_PAGE})
        result["against_1196"] = compare(stages)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(page_text(r), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
