"""The rows of #1226 and #1196 re-read with the no-variance resamples dropped from the mean-d studentization (#1239; H5 step 3).

A development study, never a verdict (scoring protocol v1, #640). Her ruling of 26 October 2026 (ledger item 57 on #1116, option 1 on
finding #1236): when a resample of a row's daily difference has no long-run variance, drop it from the mean-d studentization and report
how many were dropped. The rule is `scripts/spread_mr_variants_761.py`, `mean_d_dropping_row`, reached through `run_pairs(...,
mean_d_fallback=True)` after the earlier fallbacks of #1215 fail; `scoring_protocol.py` is unchanged.

This script reads two score files per study, the committed `result.json` and the same study re-scored on this tree, and reports the
rows that differ. Every row of the old file is matched to the row at the same path of the new one:

* a row that was "no reading" and now has a bound (`dropped_resamples` and `draws` beside it): listed with the bound and the count;
* a row that was "no reading" and has a bound without any dropping (`defined_without_dropping`; there should be none when the old file
  is the same tree's re-score without this change): listed;
* a row that was "no reading" and stays so: listed with its reason;
* a row that had a bound before: it must be unchanged to the last digit; any that moved is listed (there must be none);
* anything else that differs outside the rows (a count, a mean) is listed as `other_differences` (there must be none).

It reads no panel and scores nothing. The re-scores take about 40 minutes each on 4 cores:

    PYTHONPATH=src python3 scripts/s3_huber_calendar_1226.py score --panel PUB.csv --output NEW1226.json
    PYTHONPATH=src python3 scripts/s3_terms_1196.py score --panel PUB.csv --output NEW1196.json
    python3 scripts/mean_d_dropped_1239.py compare --new1226 NEW1226.json --new1196 NEW1196.json \\
        --output docs/research/mean-d-dropped-1239/result.json
    python3 scripts/mean_d_dropped_1239.py page --score docs/research/mean-d-dropped-1239/result.json \\
        --output docs/research/mean-d-dropped-1239-result.md

with PUB.csv the published panel built as in the docstring of either script. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
SOURCES = {
    "1226": REPO / "docs" / "research" / "s3-huber-calendar-1226" / "result.json",
    "1196": REPO / "docs" / "research" / "s3-terms-1196" / "result.json",
}
SEEDS = {"1226": 1226, "1196": 1196}
Path_ = Tuple


def is_row(o) -> bool:
    return isinstance(o, dict) and "days" in o and ("undefined" in o or "difference_interval" in o)


def walk(o, path: Tuple = ()) -> Iterator[Tuple[Tuple, dict]]:
    """Every paired row of a score file with the path to it (a row has `days` and either `undefined` or `difference_interval`)."""

    if is_row(o):
        yield path, o
    elif isinstance(o, dict):
        for key, value in o.items():
            yield from walk(value, path + (key,))
    elif isinstance(o, list):
        for index, value in enumerate(o):
            yield from walk(value, path + (index,))


def _without_rows(o):
    """`o` with every paired row replaced by a marker, to compare what is left."""

    if is_row(o):
        return "<row>"
    if isinstance(o, dict):
        return {k: _without_rows(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_without_rows(v) for v in o]
    return o


def _differences(a, b, path: Tuple = ()) -> List[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for key in sorted(set(a) | set(b), key=str):
            if key not in a or key not in b:
                out.append("/".join(map(str, path + (key,))) + (" only in new" if key in b else " only in old"))
            else:
                out += _differences(a[key], b[key], path + (key,))
        return out
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in _differences(x, y, path + (i,))]
    return [] if a == b else ["/".join(map(str, path))]


def compare(old: dict, new: dict, *, draws: Optional[int] = None) -> dict:
    """The rows of `new` against those of `old` at the same paths."""

    old_rows, new_rows = dict(walk(old)), dict(walk(new))
    gained: List[dict] = []
    still: List[dict] = []
    earlier: List[dict] = []
    moved: List[str] = []
    unchanged_with_bound = 0
    for path in sorted(old_rows, key=lambda p: tuple(map(str, p))):
        before, after = old_rows[path], new_rows.get(path)
        name = "/".join(map(str, path))
        if after is None:
            moved.append(name + " (missing in new)")
        elif "undefined" in before:
            if "undefined" in after:
                still.append({"path": name, "days": after["days"], "reason": after["undefined"], "was": before["undefined"]})
            elif "dropped_resamples" not in after:
                earlier.append({"path": name, "days": after["days"], "was": before["undefined"]})
            else:
                gained.append({"path": name, "days": after["days"], "difference": after["difference"],
                               "difference_interval": after["difference_interval"],
                               "dropped_resamples": after["dropped_resamples"], "draws": after["draws"],
                               "was": before["undefined"]})
        elif json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True):
            unchanged_with_bound += 1
        else:
            moved.append(name)
    moved += [("/".join(map(str, p)) + " (only in new)") for p in new_rows if p not in old_rows]
    other = _differences(_without_rows(old), _without_rows(new))
    return {"rows": len(old_rows), "rows_with_a_bound_before": unchanged_with_bound + len(moved), "unchanged_with_bound": unchanged_with_bound,
            "moved_with_bound": moved, "no_reading_before": len(gained) + len(still) + len(earlier), "gained": gained, "defined_without_dropping": earlier, "still_no_reading": still,
            "other_differences": other}


def build(new_files: Dict[str, Path], sources: Dict[str, Path] = SOURCES) -> dict:
    """`sources` are the old score files: the committed ones, or a re-score of the same tree without this change."""

    out = {"issue": 1239, "ruling": "26 October 2026, ledger item 57 on #1116, option 1 on finding #1236", "studies": {}}
    for study, path in new_files.items():
        old = json.loads(Path(sources[study]).read_text(encoding="utf-8"))
        new = json.loads(Path(path).read_text(encoding="utf-8"))
        for key in ("seed", "draws", "panel_sha256"):
            if old.get(key) != new.get(key):
                raise SystemExit(f"{study}: {key} differs between the committed score and the re-score ({old.get(key)!r} against {new.get(key)!r})")
        result = compare(old, new)
        result.update({"baseline": "committed" if Path(sources[study]) == SOURCES[study] else "re-score without this change",
                       "seed": new["seed"], "draws": new["draws"], "panel_sha256": new["panel_sha256"]})
        if result["baseline"] != "committed":
            # How far the committed file is from the baseline: the rows with a bound that differ, and the rest.
            committed = json.loads(Path(SOURCES[study]).read_text(encoding="utf-8"))
            drift = compare(committed, old)
            result["committed_vs_baseline"] = {"rows_with_a_bound_moved": len(drift["moved_with_bound"]),
                                               "other_differences": len(drift["other_differences"]),
                                               "first_other": drift["other_differences"][:5]}
        out["studies"][study] = result
    return out


def _arm_name(path: str) -> str:
    return path.replace("groups/", "", 1).replace("/vs/", " vs ").replace("/", " / ")


def render(r: dict) -> str:
    out = ["# Mean d with the no-variance resamples dropped, on the rows of #1226 and #1196 (#1239)", "",
           "**Development data, not a verdict** (scoring protocol v1, #640). **Hypothesis H5, step 3 (reporting); H1 (scorer).** "
           "Her ruling of 26 October 2026 (ledger item 57 on #1116, option 1 on finding #1236): when a resample of a row's daily "
           "difference has no long-run variance, drop it from the mean-d studentization and report how many were dropped. A row "
           "that has such resamples is re-read from the same seed and the same draws, the bound is taken from the rest, and the "
           "count of dropped resamples is printed beside it with the draws made. A row where every resample has none, or whose "
           "full series has none, stays \"no reading\", with the reason. `scoring_protocol.py` is unchanged; the rule is in "
           "`scripts/spread_mr_variants_761.py`.", ""]
    for study, s in r["studies"].items():
        out += [f"## #{study}: seed {s['seed']}, {s['draws']:,} draws, panel `{s['panel_sha256'][:8]}…`", "",
                f"The study was re-scored on this tree against "
                + ("its committed `result.json`. " if s["baseline"] == "committed" else "a re-score of main's tree without this change "
                   "(the committed `result.json` no longer reproduces on main: its day counts differ, see below). ")
                + f"{s['rows']} paired rows were compared. "
                f"{s['rows_with_a_bound_before']} had a mean-d bound before; {s['unchanged_with_bound']} of them are unchanged to the "
                f"last digit, and {len(s['moved_with_bound'])} moved. {s['no_reading_before']} were \"no reading\": "
                f"{len(s['gained'])} now have a bound by dropping, {len(s['defined_without_dropping'])} have one without dropping, and "
                f"{len(s['still_no_reading'])} do not. Other differences outside the rows: "
                f"{len(s['other_differences'])}.", ""]
        if "committed_vs_baseline" in s:
            d = s["committed_vs_baseline"]
            out += [f"The committed file differs from that baseline in {d['rows_with_a_bound_moved']} rows with a bound and "
                    f"{d['other_differences']} other entries (for example " + ", ".join(f"`{m}`" for m in d["first_other"]) + "), so it "
                    "is not the comparison for this change (main has since put the B2 thin-pool record in force, #1198, and changed the "
                    "as-of order of a group's fields, #1060); the stale file is reported as a finding.", ""]
        if s["moved_with_bound"]:
            out += ["**Rows that had a bound and moved (there should be none):** " + ", ".join(f"`{m}`" for m in s["moved_with_bound"]), ""]
        if s["other_differences"]:
            out += ["**Other differences:** " + ", ".join(f"`{m}`" for m in s["other_differences"]), ""]
        if s["gained"]:
            out += ["Rows that were \"no reading\" and now have a bound. d is the mean daily difference in score units (positive "
                    "favours the candidate) with its 90% studentized interval from the draws that were kept. **No reading of better "
                    "or worse is given for these rows**: the count beside each bound says how much of the stream was left out, and "
                    "the reading is left for the page that uses it.", "",
                    "| row | days | mean d [90%] | dropped of draws |", "|---|---|---|---|"]
            for g in s["gained"]:
                lo, hi = g["difference_interval"]
                share = 100.0 * g["dropped_resamples"] / g["draws"]
                out.append(f"| {_arm_name(g['path'])} | {g['days']} | {g['difference']:+.4f} [{lo:+.4f}, {hi:+.4f}] | "
                           f"{g['dropped_resamples']:,} of {g['draws']:,} ({share:.1f}%) |")
            out.append("")
        if s["still_no_reading"]:
            out += ["Rows that stay \"no reading\":", "", "| row | days | reason |", "|---|---|---|"]
            out += [f"| {_arm_name(g['path'])} | {g['days']} | {g['reason']} |" for g in s["still_no_reading"]]
            out.append("")
    out += ["## What this does not show", "",
            "It scores nothing new: the tables above come from the same panel and seeds as the baselines they are compared with, and the "
            "committed pages are left as they are. A bound taken from the kept resamples is not the bound the full stream would give; "
            "the dropped resamples are those of a daily difference that is constant on the resample, so a row with a large count is "
            "a row whose difference is zero on most days. The pages of #1226 and #1196 and their `result.json` are not regenerated "
            "here; whether to regenerate them with these rows in place is hers.", ""]
    return "\n".join(out)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--new1226", required=True)
    c.add_argument("--new1196", required=True)
    c.add_argument("--old1226", default=str(SOURCES["1226"]), help="the score to compare with (default: the committed result.json)")
    c.add_argument("--old1196", default=str(SOURCES["1196"]), help="as --old1226")
    c.add_argument("--output", required=True)
    g = sub.add_parser("page")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if args.command == "compare":
        result = build({"1226": Path(args.new1226), "1196": Path(args.new1196)},
                       {"1226": Path(args.old1226), "1196": Path(args.old1196)})
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    else:
        Path(args.output).write_text(render(json.loads(Path(args.score).read_text(encoding="utf-8"))), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
