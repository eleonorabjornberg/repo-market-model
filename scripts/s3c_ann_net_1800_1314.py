"""The H5 candidate (s3c-ann-net) and its comparison, re-made at the 18:00 decision instant (#1314; H5 step 3; her ruling of 29 October 2026, ledger item 77,
widened on 30 October 2026, ledger item 80, #1316 option 2).

A development study, never a verdict. Step 3 of 3 in moving the decision instant from 16:00 to 18:00 New York time (#1312 amended the information set, #1313
opens the new live record). The walks, fits and forecasts are #1288's and #1320's, **run unchanged** by their own scripts at the 18:00 instant
(`repo_model.decision_instant.DECISION_TIME`); this script adds only what a re-run at a new instant needs:

* the 16:00 side of a paired comparison, kept as per-cell scores (`cells`, run from a checkout of the last commit before #1312 merged);
* the paired 18:00-against-16:00 row for (s3c-ann-net) itself, and for (s3c) and (s3c-ann) beside it;
* B3, the incumbent, scored on its own five levels at lead 1 (protocol v1 section 4), against the candidate at both instants;
* the figure-by-figure comparison of each 18:00 record with the 16:00 record at the same paths, so that every table carries a 16:00 column;
* the page, which says it was made at 18:00 and links the 16:00 page it replaces.

Every choice is in `metadata/s3c_ann_net_1800_1314.json`, which this script refuses to read unless it is committed and unchanged. It writes only under
`docs/research/s3c-ann-net-1800-1314/` and the page, and nothing into `docs/runs/`.

Commands, in order, from a clone of the branch (each step is under two hours on four cores in the cloud: the first about ninety minutes, the second about
half an hour, the rest minutes):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    OUT=docs/research/s3c-ann-net-1800-1314
    PYTHONPATH=src python3 scripts/s3c_announced_settlement_1288.py score --panel PUB.csv --output $OUT/announced-settlement-1800.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_diagnosis_1319.py score --panel PUB.csv --output $OUT/diagnosis-1800.json
    # the 16:00 side, from the last commit before #1312 merged (a worktree; its own panel build at 16:00 is byte-identical to PUB.csv):
    git worktree add ../rmm-1600 29732943ea64882bdf81bc1337278fb2c9cf67a7
    (cd ../rmm-1600 && PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB1600.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00)
    PYTHONPATH=src python3 scripts/s3c_ann_net_1800_1314.py cells --root ../rmm-1600 --panel ../rmm-1600/PUB1600.csv --output $OUT/cells-1600.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_1800_1314.py score --panel PUB.csv --cells-1600 $OUT/cells-1600.json \\
        --announced $OUT/announced-settlement-1800.json --diagnosis $OUT/diagnosis-1800.json --output $OUT/result.json
    PYTHONPATH=src python3 scripts/s3c_ann_net_1800_1314.py page --score $OUT/result.json --output docs/research/s3c-ann-net-1800-1314-result.md

Stdlib only; every `repo_model` import is made inside a function, so that `cells` can load the 16:00 checkout's own modules.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
DECLARATION = REPO / "metadata" / "s3c_ann_net_1800_1314.json"
OUT = REPO / "docs" / "research" / "s3c-ann-net-1800-1314"
RECORD_1288 = REPO / "docs" / "research" / "s3c-announced-settlement-1288" / "result.json"
RECORD_1319 = REPO / "docs" / "research" / "s3c-ann-net-diagnosis-1319" / "result.json"
B3_DAILY = REPO / "docs" / "runs" / "published_distribution_daily_h1.json"
SEED = 1314
TOLERANCE = 1e-9

#: The decision instant this study is made at, and the one it replaces. The page says the first and links the pages of the second.
INSTANT_TIME = time(18, 0)
INSTANT_TEXT = INSTANT_TIME.isoformat(timespec="minutes")
EARLIER_TEXT = "16:00"
EARLIER_PAGES = ("s3c-announced-settlement-1288-result.md", "s3c-ann-net-diagnosis-1319-result.md")
B3_LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
SCORES = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
SCORE_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)"}
MODEL_NAMES = ("sc_s3c", "sc_s3c_ann", "sc_s3c_ann_net")
MODEL_LABELS = {"sc_s3c": "(s3c)", "sc_s3c_ann": "(s3c-ann)", "sc_s3c_ann_net": "(s3c-ann-net)"}
WINDOWS = ("development", "2026")
WINDOW_TITLES = {"development": "Development window (targets to 2025-12-31)", "2026": "The 2026 development days (targets 2026-01-02 to 2026-09-03)"}


# -- the two guards ------------------------------------------------------------------------------------------------------


def require_instant(decision_time: time) -> None:
    """Refuse to make an 18:00 study at another decision instant.

    Raises:
        ValueError: the repository's decision instant is not the declared one.
    """

    if decision_time != INSTANT_TIME:
        raise ValueError(f"this study is made at {INSTANT_TEXT}; the repository's decision instant is {decision_time.isoformat(timespec='minutes')}")


def check_cells(doc: Mapping[str, object], panel_sha256: str) -> None:
    """Refuse a cells file that is not the 16:00 walk of this panel.

    Raises:
        ValueError: it was made at another instant, or from another panel.
    """

    if doc.get("instant") != EARLIER_TEXT:
        raise ValueError(f"the cells file was made at {doc.get('instant')}, not {EARLIER_TEXT}: it cannot be the 16:00 side")
    if doc.get("panel_sha256") != panel_sha256:
        raise ValueError("the cells file was made from another panel than this run's")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    out = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", str(path)], capture_output=True, text=True, check=True).stdout
    if out.strip():
        raise ValueError(f"{path} is not committed and unchanged: {out.strip()}")
    return json.loads(path.read_text(encoding="utf-8"))


# -- the figure-by-figure comparison -------------------------------------------------------------------------------------


def flatten(node, prefix: str = "") -> Dict[str, float]:
    """Every numeric leaf of a record by its path (booleans, text and null left out; lists are indexed)."""

    out: Dict[str, float] = {}
    if isinstance(node, bool):
        return out
    if isinstance(node, (int, float)):
        out[prefix] = float(node)
    elif isinstance(node, Mapping):
        for key, value in node.items():
            out.update(flatten(value, f"{prefix}/{key}" if prefix else str(key)))
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            out.update(flatten(value, f"{prefix}/{i}" if prefix else str(i)))
    return out


def _unequal(a: float, b: float, tolerance: float) -> bool:
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) != math.isnan(b)
    return abs(a - b) > tolerance * max(1.0, abs(b))


def compare(new, old, tolerance: float = TOLERANCE, keep: int = 200) -> dict:
    """Every number of `new` set against the number of `old` at the same path: how many were compared, how many differ, the largest difference."""

    a, b = flatten(new), flatten(old)
    shared = sorted(set(a) & set(b))
    differing = [p for p in shared if _unequal(a[p], b[p], tolerance)]
    biggest = max((abs(a[p] - b[p]) for p in shared if not (math.isnan(a[p]) or math.isnan(b[p]))), default=0.0)
    return {"compared": len(shared), "differ": len(differing), "max_abs": biggest,
            "paths": [{"path": p, "new": a[p], "old": b[p]} for p in differing[:keep]],
            "only_new": sorted(set(a) - set(b))[:keep], "only_old": sorted(set(b) - set(a))[:keep]}


def compare_sections(new, old, depth: int, tolerance: float = TOLERANCE) -> Dict[str, dict]:
    """`compare` by the first `depth` components of the path (a table of the record), as counts only."""

    a, b = flatten(new), flatten(old)
    out: Dict[str, dict] = {}
    for p in sorted(set(a) | set(b)):
        section = "/".join(p.split("/")[:depth])
        row = out.setdefault(section, {"compared": 0, "differ": 0, "only_one_side": 0, "max_abs": 0.0})
        if p in a and p in b:
            row["compared"] += 1
            if _unequal(a[p], b[p], tolerance):
                row["differ"] += 1
            if not (math.isnan(a[p]) or math.isnan(b[p])):
                row["max_abs"] = max(row["max_abs"], abs(a[p] - b[p]))
        else:
            row["only_one_side"] += 1
    return out


# -- the paired row ------------------------------------------------------------------------------------------------------


def paired_cells(new_cells: Sequence[Sequence], old_cells: Sequence[Sequence], model_index: int) -> List[tuple]:
    """`(decision day, lead, new scores, old scores)` of one model, the two lists refused unless they cover the same (day, lead) cells.

    Raises:
        ValueError: the cells differ.
    """

    new = {(row[0], row[1]): row[2][model_index] for row in new_cells}
    old = {(row[0], row[1]): row[2][model_index] for row in old_cells}
    if set(new) != set(old) or len(new) != len(new_cells) or len(old) != len(old_cells):
        raise ValueError("the 18:00 and the 16:00 cells do not cover the same decision days and leads")
    return [(d, h, new[(d, h)], old[(d, h)]) for (d, h) in sorted(new)]


def paired_summary(rows: Sequence[tuple], run_pairs: Optional[Callable] = None) -> dict:
    """The 18:00 run against the 16:00 run of one model over paired cells.

    d is 16:00 less 18:00 on each score (the protocol's sign: above zero favours 18:00). The leads of a decision day are averaged and the days compared.
    Where no cell differs the studentized bound has no variance and the interval is [0, 0], stated as exact; otherwise `run_pairs` (protocol v1's
    studentized test, `spread_mr_variants_761.run_pairs`) reads it, or the interval is left out when none is given.
    """

    days = sorted({r[0] for r in rows})
    per = {name: {} for name in range(len(SCORES))}
    for j in range(len(SCORES)):
        new_by, old_by = {}, {}
        for d, _h, new, old in rows:
            new_by.setdefault(d, []).append(new[j])
            old_by.setdefault(d, []).append(old[j])
        per[j] = ({d: sum(v) / len(v) for d, v in new_by.items()}, {d: sum(v) / len(v) for d, v in old_by.items()})
    differing = [r for r in rows if any(x != y for x, y in zip(r[2], r[3]))]
    biggest = max((abs(x - y) for r in rows for x, y in zip(r[2], r[3])), default=0.0)
    out = {"cells": len(rows), "days": len(days), "differing_cells": len(differing), "max_abs": biggest, "scores": []}
    for j, name in enumerate(SCORES):
        new_d, old_d = per[j]
        mean_new = sum(new_d[d] for d in days) / len(days)
        mean_old = sum(old_d[d] for d in days) / len(days)
        diffs = [old_d[d] - new_d[d] for d in days]
        entry = {"score": name, "mean_18": mean_new, "mean_16": mean_old, "difference": sum(diffs) / len(diffs),
                 "identical": all(x == 0.0 for x in diffs), "interval": None, "test": None}
        if entry["identical"]:
            entry.update(interval=[0.0, 0.0], test="exact: no cell differs, so the studentized bound has no variance and the difference is 0 on every day")
        elif run_pairs is not None:
            keys = [date.fromisoformat(d) for d in days]
            test = run_pairs({"16:00": {date.fromisoformat(d): old_d[d] for d in days}}, {date.fromisoformat(d): new_d[d] for d in days}, keys,
                             seed=SEED, mean_d_fallback=True)["16:00"]
            entry.update(interval=test.get("difference_interval"), test=test)
        out["scores"].append(entry)
    return out


# -- B3 on its own five levels -------------------------------------------------------------------------------------------


def five_level_score(quantiles: Sequence[float], observed: float, levels: Sequence[float] = B3_LEVELS) -> float:
    """A 23-level forecast read at B3's five levels and scored there (protocol v1 section 4, ruling of 13 October 2026)."""

    from repo_model import scoring_protocol as sp

    return sp.level_crps(levels)(sp.on_levels(quantiles, levels), observed)


def b3_score(daily: Mapping[str, Mapping[str, object]], target: date, observed: float, levels: Sequence[float] = B3_LEVELS) -> Optional[float]:
    """The published distribution's five-level score on `target`, or None when its record does not cover the day.

    Raises:
        ValueError: the record's outcome for the day is not the panel's.
    """

    entry = daily.get(target.isoformat())
    if entry is None:
        return None
    if abs(float(entry["actual_bps"]) - float(observed)) > 1e-9:
        raise ValueError(f"the published record's outcome for {target} is {entry['actual_bps']}, the panel's is {observed}")
    from repo_model import scoring_protocol as sp

    return sp.level_crps(levels)([float(x) for x in entry["quantiles_bps"]], float(observed))


# -- the page's pieces ---------------------------------------------------------------------------------------------------


def banner() -> str:
    links = " and ".join(f"[{name}]({name})" for name in EARLIER_PAGES)
    return (f"> **Made at {INSTANT_TEXT} New York time** (the decision instant in force since #1312, her ruling of 29 October 2026), a re-run of the "
            f"records made at {EARLIER_TEXT}. It replaces, and does not edit, {links}; those pages and their `result.json` stay as the records of the earlier "
            f"instant, and so does every result not re-run here.")


def _pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{100.0 * x:+.1f}%"


def _iv(interval: Optional[Sequence[float]], digits: int = 3) -> str:
    return "not read" if not interval else f"[{interval[0]:+.{digits}f}, {interval[1]:+.{digits}f}]"


def _diff_cell(entry: Optional[Mapping[str, object]]) -> str:
    if not entry or "mean_d" not in entry:
        return "n/a"
    return f"d {entry['mean_d']:+.3f} {_iv(entry.get('interval'))} **{entry.get('reading', 'not read')}**"


def two_column_table(rows18: Mapping[str, dict], rows16: Mapping[str, dict], metrics: Sequence[str], first: str) -> List[str]:
    """Markdown rows of `diff_row` results with the 18:00 figure and the 16:00 figure of each score side by side (d is the arm less the reference)."""

    head = [first, "cells", "days"]
    for m in metrics:
        head += [f"{SCORE_TITLES[m]}, {INSTANT_TEXT}", f"{SCORE_TITLES[m]}, {EARLIER_TEXT}"]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for label, row in rows18.items():
        old = rows16.get(label)
        cells = [label, str(row["cells"]), str(row["units"])]
        for m in metrics:
            cells += [_diff_cell(row.get(m)), _diff_cell(old.get(m)) if old else "not in the 16:00 record"]
        out.append("| " + " | ".join(cells) + " |")
    return out


# -- the walks -----------------------------------------------------------------------------------------------------------


def load_tree(root: Path):
    """#1319's module (and through it #1288's) loaded from the checkout at `root`, with that checkout's own `src` first on the path."""

    root = Path(root).resolve()
    sys.path.insert(0, str(root / "src"))
    alias = "s3c_ann_net_diagnosis_1319_in_1314"
    spec = importlib.util.spec_from_file_location(alias, root / "scripts" / "s3c_ann_net_diagnosis_1319.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def walk_windows(m, panel_path: Path) -> Dict[str, tuple]:
    """#1319's `build_cells`, keeping each window's frame: `{window: (frame, cells)}`."""

    panel = [row for row in m.m1288.load_daily_panel(Path(panel_path)) if row.date <= m.m1288.LAST_DAY]
    m.require_exploratory_window([row.date for row in panel], where="scripts/s3c_ann_net_1800_1314")
    splits = m.load_split_declaration(m.c.SPLITS)
    registry = json.loads(m.c.SOURCES.read_text(encoding="utf-8"))
    register = m.policy_events.load_register()
    table = m.cal.TermTable(panel, m.announced_iorb.load_announcements(m.c.IORB_TABLE), decision_time=m.c.DECISION_TIME)
    auctions = m.m1273.load_auctions()
    results = m.m1288.load_results()
    states = m.k.d1145.decision_states(m.c.SOURCES)
    immediate = m.release_days()
    out = {}
    for window in m.m1288.WINDOWS:
        frame, _notes, walks, (term_table, net_table), _ct, _gf = m.m1288.build(window, panel, splits, registry, table, register, results, auctions, None)
        cells = m.assemble(frame, walks, term_table, net_table, panel, auctions, states, immediate, m.m1288.WINDOW_LAST[window])
        out[window] = (frame, cells)
    return out


def to_document(m, windows: Mapping[str, tuple], panel_sha256: str, commit: str, instant_text: str) -> dict:
    """The per-cell scores of (s3c), (s3c-ann) and (s3c-ann-net), their scarcity-state label, and the lead-1 forecasts of (s3c) and (s3c-ann-net)."""

    models = (m.S3C, m.ANN, m.NET)
    assert tuple(models) == MODEL_NAMES, models
    doc = {"instant": instant_text, "commit": commit, "panel_sha256": panel_sha256, "models": list(models), "scores": list(SCORES), "windows": {}}
    for window, (frame, cells) in windows.items():
        rows = [[x["d"].isoformat(), x["h"], [[x["score"][mm][s] for s in SCORES] for mm in models], x["state"]] for x in cells]
        lead1 = []
        for d in frame.days:
            t = frame.target(d, 1)
            lead1.append([d.isoformat(), t.isoformat(), frame.outcome[t], list(frame.forecasts[m.S3C][d][1]), list(frame.forecasts[m.NET][d][1])])
        doc["windows"][window] = {"cells": rows, "lead1": lead1}
    return doc


def _git_head(root: Path) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def cmd_cells(args) -> int:
    root = Path(args.root).resolve()
    m = load_tree(root)
    panel_path = Path(args.panel)
    sha = m.panel_sha256(panel_path)
    instant = m.k.DECISION_TIME.isoformat(timespec="minutes")
    windows = walk_windows(m, panel_path)
    doc = to_document(m, windows, sha, _git_head(root), instant)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: instant {instant}, commit {doc['commit']}, " + ", ".join(f"{w} {len(v['cells'])} cells" for w, v in doc["windows"].items()))
    return 0


# -- the score -----------------------------------------------------------------------------------------------------------


def cmd_score(args) -> int:
    m = load_tree(REPO)
    from repo_model import decision_instant, scoring_protocol as sp

    require_instant(decision_instant.DECISION_TIME)
    require_instant(m.k.DECISION_TIME)
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    sha = m.panel_sha256(panel_path)
    old = json.loads(Path(args.cells_1600).read_text(encoding="utf-8"))
    check_cells(old, sha)
    announced = json.loads(Path(args.announced).read_text(encoding="utf-8"))
    diagnosis = json.loads(Path(args.diagnosis).read_text(encoding="utf-8"))
    for name, rec in (("announced", announced), ("diagnosis", diagnosis)):
        if rec.get("panel_sha256") != sha:
            raise ValueError(f"the {name} record was made from another panel than this run's")
    new_doc = to_document(m, walk_windows(m, panel_path), sha, "working tree", INSTANT_TEXT)
    daily = {x["date"]: x for x in json.loads(B3_DAILY.read_text(encoding="utf-8"))["days"]}
    s761 = m.m1288.s761
    run_pairs = lambda benchmarks, candidate, days, **kw: s761.run_pairs(benchmarks, candidate, days, draws=sp.DRAWS, **kw)  # noqa: E731
    result: dict = {
        "issue": 1314, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": sha, "label": "development, not a verdict",
        "instant": INSTANT_TEXT, "earlier_instant": EARLIER_TEXT, "seed": SEED, "draws": sp.DRAWS,
        "cells_1600": {"commit": old["commit"], "path": str(Path(args.cells_1600).resolve().relative_to(REPO))},
        "amendments": declaration["amendments"], "paired": {}, "state_labels": {}, "b3": {}, "compare": {},
    }
    for window in WINDOWS:
        new_w, old_w = new_doc["windows"][window], old["windows"][window]
        result["paired"][window] = {}
        for i, name in enumerate(MODEL_NAMES):
            rows = paired_cells(new_w["cells"], old_w["cells"], i)
            entry = paired_summary(rows, run_pairs)
            entry["by_lead"] = {str(h): paired_summary([r for r in rows if r[1] == h], run_pairs) for h in sp.HORIZONS}
            result["paired"][window][name] = entry
        moved = sorted({(a[0], a[3], b[3]) for a, b in zip(new_w["cells"], old_w["cells"]) if a[3] != b[3]})
        result["state_labels"][window] = {"cells": sum(1 for a, b in zip(new_w["cells"], old_w["cells"]) if a[3] != b[3]),
                                          "decision_days": [{"day": d, "state_18": s18, "state_16": s16} for d, s18, s16 in moved]}
        result["b3"][window] = b3_window(new_w["lead1"], old_w["lead1"], daily, run_pairs)
    result["compare"] = {
        "announced": {"all": compare(announced, json.loads(RECORD_1288.read_text(encoding="utf-8"))),
                      "sections": compare_sections(announced, json.loads(RECORD_1288.read_text(encoding="utf-8")), 3)},
        "diagnosis": {"all": compare(diagnosis, json.loads(RECORD_1319.read_text(encoding="utf-8"))),
                      "sections": compare_sections(diagnosis, json.loads(RECORD_1319.read_text(encoding="utf-8")), 3)},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return 0


def b3_window(new_lead1: Sequence[Sequence], old_lead1: Sequence[Sequence], daily: Mapping[str, dict], run_pairs: Callable) -> dict:
    """The candidate against B3 on B3's five levels at lead 1, at 18:00 and at 16:00, on the decision days the published record covers.

    d is S(B3) less S(candidate), the protocol's sign (above zero favours the candidate), read by the same studentized test as the 23-level comparisons.
    """

    out: dict = {"levels": list(B3_LEVELS), "note": "B3's forecasts are the published record's, made at 16:00 and not re-run; lead 1 only"}
    series: Dict[str, Dict[date, float]] = {"B3": {}}
    for tag, rows in (("18", new_lead1), ("16", old_lead1)):
        for position, name in ((3, "sc_s3c"), (4, "sc_s3c_ann_net")):
            series[f"{name}@{tag}"] = {}
            for row in rows:
                d, t, y = date.fromisoformat(row[0]), date.fromisoformat(row[1]), float(row[2])
                b3 = b3_score(daily, t, y)
                if b3 is None:
                    continue
                series["B3"][d] = b3
                series[f"{name}@{tag}"][d] = five_level_score(row[position], y)
    days = sorted(series["B3"])
    out["days"] = len(days)
    out["first"], out["last"] = (days[0].isoformat(), days[-1].isoformat()) if days else (None, None)
    out["rows"] = {}
    for key, s in series.items():
        if key == "B3" or not days:
            continue
        if set(days) - set(s):
            raise ValueError(f"{key} does not cover the days B3 does")
        test = run_pairs({"B3": {d: series["B3"][d] for d in days}}, {d: s[d] for d in days}, days, seed=SEED, mean_d_fallback=True)["B3"]
        out["rows"][key] = test
    out["means"] = {k: sum(v[d] for d in days) / len(days) for k, v in series.items() if days}
    return out


# -- the page ------------------------------------------------------------------------------------------------------------


def _load_pages(args) -> Tuple[dict, dict, dict, dict, dict]:
    return (json.loads(Path(args.score).read_text(encoding="utf-8")),
            json.loads((OUT / "announced-settlement-1800.json").read_text(encoding="utf-8")),
            json.loads((OUT / "diagnosis-1800.json").read_text(encoding="utf-8")),
            json.loads(RECORD_1288.read_text(encoding="utf-8")),
            json.loads(RECORD_1319.read_text(encoding="utf-8")))


def _sub(node: Mapping, *path: str) -> Mapping:
    for p in path:
        node = node[p]
    return node


def paired_table(r: Mapping[str, dict]) -> List[str]:
    out = ["| window | model | cells | days | cells that differ | largest difference | score | mean at 18:00 | mean at 16:00 | d (16:00 less 18:00) | interval |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for window in WINDOWS:
        for name in MODEL_NAMES:
            e = r["paired"][window][name]
            for s in e["scores"]:
                out.append(f"| {window} | {MODEL_LABELS[name]} | {e['cells']} | {e['days']} | {e['differing_cells']} | {e['max_abs']:.3g} | "
                           f"{SCORE_TITLES[s['score']]} | {s['mean_18']:.4f} | {s['mean_16']:.4f} | {s['difference']:+.4f} | {_iv(s['interval'], 4)}"
                           f"{' (exact)' if s['identical'] else ''} |")
    return out


def b3_table(r: Mapping[str, dict]) -> List[str]:
    out = ["| window | decision days | candidate | instant | mean five-level CRPS | B3 | d = S(B3) less S(candidate) | interval |", "|---|---|---|---|---|---|---|---|"]
    for window in WINDOWS:
        b = r["b3"][window]
        for key, test in b["rows"].items():
            name, tag = key.split("@")
            lo_hi = test.get("difference_interval") if isinstance(test, dict) else None
            d = test.get("difference") if isinstance(test, dict) else None
            out.append(f"| {window} | {b['days']} | {MODEL_LABELS[name]} | {tag}:00 | {b['means'][key]:.4f} | {b['means']['B3']:.4f} | "
                       f"{'n/a' if d is None else f'{d:+.4f}'} | {_iv(lo_hi, 4)} |")
    return out


def compare_table(c: Mapping[str, dict]) -> List[str]:
    out = ["| record | numbers compared | differ | largest difference | numbers in one record only |", "|---|---|---|---|---|"]
    for key, label in (("announced", "#1288's tables (announced-settlement-1800.json)"), ("diagnosis", "#1320's tables (diagnosis-1800.json)")):
        a = c[key]["all"]
        out.append(f"| {label} | {a['compared']} | {a['differ']} | {a['max_abs']:.3g} | {len(a['only_new']) + len(a['only_old'])} |")
    return out


def differing_sections(c: Mapping[str, dict]) -> List[str]:
    out = []
    for key in ("announced", "diagnosis"):
        for section, row in c[key]["sections"].items():
            if row["differ"] or row["only_one_side"]:
                out.append(f"| {key} | `{section}` | {row['compared']} | {row['differ']} | {row['only_one_side']} | {row['max_abs']:.3g} |")
    return out


def render(args) -> str:
    r, ann, dia, ann16, dia16 = _load_pages(args)
    out: List[str] = []
    add = out.append
    d18, d16 = dia["windows"]["development"], dia16["windows"]["development"]
    n18, n16 = dia["windows"]["2026"], dia16["windows"]["2026"]
    add("# The H5 candidate (s3c-ann-net) re-run at the 18:00 decision instant (#1314)\n")
    add(banner() + "\n")
    p = r["paired"]["development"]["sc_s3c_ann_net"]
    p26 = r["paired"]["2026"]["sc_s3c_ann_net"]
    cmp_a, cmp_d = r["compare"]["announced"]["all"], r["compare"]["diagnosis"]["all"]
    add("**What the move from 16:00 to 18:00 bought (s3c-ann-net).** "
        + (f"Nothing, on these days: not one of the {p['cells'] + p26['cells']:,} (decision day, lead) cells of the two windows scores differently at 18:00 than at 16:00 "
           f"(largest difference {max(p['max_abs'], p26['max_abs']):.3g}), and the same holds for (s3c) and (s3c-ann). "
           if all(r["paired"][w][n]["differing_cells"] == 0 for w in WINDOWS for n in MODEL_NAMES) else
           f"The cells that score differently are listed in the paired table below. ")
        + f"Every number of #1288's re-run tables was set against the 16:00 record at the same path: {cmp_a['compared']:,} compared, {cmp_a['differ']} differ; "
        f"#1320's: {cmp_d['compared']:,} compared, {cmp_d['differ']} differ. **Development data on seen days, not a verdict.**\n")
    add("**Hypothesis and step:** H5 (primary goal), step 3, the candidate (s3c-ann-net); step 3 of 3 in moving the decision instant to 18:00 ET (#1312, #1313, "
        "#1314). Nothing is registered or published: no record in `docs/runs/` is edited, the live record and its pin do not change, no day after 2026-09-03 is "
        f"scored and no lockbox day is scored. Declared in `{r['declaration']}` before any figure of this study was read; generated by "
        "`scripts/s3c_ann_net_1800_1314.py page` from `docs/research/s3c-ann-net-1800-1314/result.json`, not edited by hand. Panel "
        f"`{r['panel_sha256'][:8]}...` (byte-identical at 16:00 and 18:00; the instant moves what a forecast may read, not the daily panel's columns).\n")
    add("## Why the answer is zero\n")
    add("The walks read the daily panel, the announcement dating (an auction's settlement date and offering are public from 12:00 on its announcement date, #541), "
        "the net settlement tables (12:00 as well), the IORB announcement table (no note was announced between 16:00 and 18:00 on a panel day) and "
        "the SRF policy events. None of these is published between 16:00 and 18:00, so a decision at 18:00 reads exactly what a decision at 16:00 read. "
        "What does publish in the two hours (the H.15 at 16:15, the Treasury bill rates at 16:30, the primary dealers' weekly figures) is read by no arm "
        "of (s3c): (s3) models the spread's own history and the calendar. "
        "The move matters to the models that read those series (H3's candidates, H9's targets), and to the live record (#1313), not to this one.\n")
    sl = r["state_labels"]["development"]
    add(f"One thing did move: the scarcity-state label that #1320's Table 4c groups by. It differs on {sl['cells']} development-window cells "
        f"({len(sl['decision_days'])} decision days: " + ", ".join(f"{x['day']} ({x['state_16']:g} at 16:00, {x['state_18']:g} at 18:00)" for x in sl["decision_days"])
        + "). The model's own state is held at its maximum, so no score moves; only the grouping of Table 4c does.\n")
    add("## 1. The candidate against (s3c) and the benchmarks, at 18:00\n")
    add("From `scripts/s3c_announced_settlement_1288.py score`, unchanged, at the 18:00 instant (`docs/research/s3c-ann-net-1800-1314/announced-settlement-1800.json`). "
        "Grid CRPS averaged over leads 1 to 5 is the primary score, upper-tail twCRPS the key secondary, and the Brier score of P(> +5 bp) is reported "
        "beside (`docs/decisions/pressure-probability.md`). Each row is a paired test on scoring protocol v1's studentized stationary bootstrap, read on the "
        "bound on mean d, with the skill interval beside; **skill above zero favours the arm**. B1' is Lens C's calendar-aware persistence "
        "(#960), reported beside B1.\n")
    m1288 = load_tree(REPO).m1288
    for window in WINDOWS:
        w = ann["windows"][window]
        add(f"### {WINDOW_TITLES[window]}\n")
        pooled = w["groups"]["pooled"]["all decision days"]
        for arm in (m1288.ANNNET, m1288.ANN):
            add(f"**{m1288.LABELS[arm]} against each reference (pooled)**\n")
            out += m1288.against_table(pooled, arm) + [""]
        for split, title in (("lead", "By lead"), ("regime", "By regime"), ("pressure_day_type", "By pressure-day type of the target day")):
            for ref in (m1288.S3C, "B1", "B2"):
                table = m1288.split_table(w, split, m1288.ANNNET, ref)
                if table:
                    out += [f"**{title}: {m1288.LABELS[m1288.ANNNET]} against {m1288.LABELS[ref]}**", ""] + table + [""]
        table = m1288.split_table(w, "lead", m1288.ANN, m1288.S3C)
        out += [f"**By lead: {m1288.LABELS[m1288.ANN]} (the flag arm) against {m1288.LABELS[m1288.S3C]}**", ""] + table + [""]
    add("### B3, the incumbent, on its own five levels at lead 1 (the secondary comparison of protocol v1 section 4)\n")
    add("B3 is the published v1 distribution's daily forecast (`docs/runs/published_distribution_daily_h1.json`, lead 1 only, five levels). It is a record "
        "made at 16:00 and is **not re-run**: the candidate is read at the same five levels at each instant, and the rows are paired on the decision days "
        "the record covers. d = S(B3) less S(candidate): above zero favours the candidate.\n")
    out += b3_table(r) + [""]
    add("## 2. The 16:00 against 18:00 difference for the candidate itself\n")
    add("One paired row per window and model, over (decision day, lead) cells, the leads of a decision day averaged and the days compared. The 16:00 side is "
        f"the same walks rebuilt at commit `{r['cells_1600']['commit'][:8]}`, the last before #1312 merged (`{r['cells_1600']['path']}`). d is 16:00 less 18:00, "
        "so above zero favours 18:00. Where no cell differs there is no variance to studentize: the difference is 0 on every day and the interval is "
        "stated as exact.\n")
    out += paired_table(r) + [""]
    add("## 3. The DTCC capture\n")
    add("`scripts/gcf_index_capture.py`, its launchd job (`scripts/launchd/org.rmm.gcf-index-capture.plist`) and `repo_model.gcf_index` capture from 15:30 ET up to "
        "the decision instant, 18:00 ET, since #1312; a value posted before 18:00 is kept as the same day's, and a fetch after it is a missed day with no value. "
        "This directive adds `tests/test_gcf_capture_window_1314.py`: a run at 16:05 fetches and a value posted at 16:30 is kept and read by the 18:00 decision; "
        "a fetch after 18:00 is still missed; and the UTC span a schedule must cover (19:30 to 22:00 in EDT, 20:30 to 23:00 in EST). **The private "
        "repository's workflow cron** must cover 16:00 to 18:00 ET in both EDT (20:00 to 22:00 UTC) and EST (21:00 to 23:00 UTC), that is 20:00 to 23:00 UTC; "
        "the orchestrating session pushes that change, not this directive.\n")
    add("## 4. #1320's three splits, re-asked at 18:00, each with its 16:00 column\n")
    add("From `scripts/s3c_ann_net_diagnosis_1319.py score`, unchanged, at the 18:00 instant (`docs/research/s3c-ann-net-1800-1314/diagnosis-1800.json`); the 16:00 column is "
        "the same path of #1320's record (`docs/research/s3c-ann-net-diagnosis-1319/result.json`). d is the arm less the reference, so **a positive d is a loss**. "
        "Intervals are 90% stationary-bootstrap intervals on mean d over days in date order (a diagnostic interval, not the protocol's studentized test). "
        "Readings are development data and decide nothing.\n")
    t1, t1o = d18["table_1"], d16["table_1"]
    add("### (a) Lead 1: (s3c-ann-net) against (s3c), by settlement-day type, net-to-gross class and maturing-share third (Tables 1 to 3 of #1320)\n")
    out += two_column_table({"all lead-1 cells": t1["all lead-1 cells"], **t1["by_type"]}, {"all lead-1 cells": t1o["all lead-1 cells"], **t1o["by_type"]},
                            ("brier_gt5", "grid_crps"), "target-day type") + [""]
    out += two_column_table(t1["by_class"], t1o["by_class"], ("brier_gt5", "grid_crps"), "net-to-gross class") + [""]
    out += two_column_table(t1["by_maturing_third"], t1o["by_maturing_third"], ("brier_gt5", "grid_crps"), "maturing share") + [""]
    add("### (b) 2020: both announced arms against (s3c), by period and month, with the fitted shift against the realised premium (Table 4 of #1320)\n")
    for arm, label in (("sc_s3c_ann", "(s3c-ann), the flag"), ("sc_s3c_ann_net", "(s3c-ann-net), the net")):
        x, xo = d18["table_4"]["4a"][arm], d16["table_4"]["4a"][arm]
        add(f"**{label} against (s3c): 2020 by period**\n")
        out += two_column_table({k: v for k, v in x.items() if k != "by_month"}, {k: v for k, v in xo.items() if k != "by_month"}, ("grid_crps",), "period") + [""]
        out += two_column_table(x["by_month"], xo["by_month"], ("grid_crps",), "month") + [""]
    add("**The settlement terms against the realised spread, by regime (leads 2 to 5)**: shift is the arm's fitted settlement contribution in bp on settlement "
        "cells; premium the realised mean spread on settlement target days less the others.\n")
    out += ["| regime | arm | shift, 18:00 | shift, 16:00 | realised premium, 18:00 | realised premium, 16:00 |", "|---|---|---|---|---|---|"]
    for regime, e in d18["table_4"]["4b"]["by_regime"].items():
        eo = d16["table_4"]["4b"]["by_regime"][regime]
        for arm in MODEL_NAMES:
            out.append(f"| {regime} | {MODEL_LABELS[arm]} | {e[arm]['shift']:+.2f} | {eo[arm]['shift']:+.2f} | {e[arm]['premium']:+.2f} | {eo[arm]['premium']:+.2f} |")
    out.append("")
    add("**The immediate-release cash management bill days: the share of the net arm's 2020 loss**\n")
    out += ["| group | share of the loss, 18:00 | share of the loss, 16:00 |", "|---|---|---|"]
    for arm in ("sc_s3c_ann", "sc_s3c_ann_net"):
        for key, row in d18["table_4"]["4d"][arm].items():
            if "share_of_loss" in row:
                out.append(f"| {MODEL_LABELS[arm]}: {key} | {_pct(row['share_of_loss'])} | {_pct(d16['table_4']['4d'][arm][key]['share_of_loss'])} |")
    out.append("")
    add("### (c) Net against flag: Brier at every lead, split by whether the spread went above +5 bp, and 2018-19 on all three scores (Table 3 of #1320)\n")
    t3, t3o = d18["table_3"], d16["table_3"]
    out += two_column_table(t3["by_lead"], t3o["by_lead"], ("brier_gt5", "grid_crps"), "lead") + [""]
    out += ["| lead | set | cells | Brier difference summed, 18:00 | Brier difference summed, 16:00 | mean probability (net / flag), 18:00 | 16:00 |", "|---|---|---|---|---|---|---|"]
    for h in (1, 2, 3, 4, 5):
        for label, v in t3["by_event"][f"h={h}"]["sets"].items():
            vo = t3o["by_event"][f"h={h}"]["sets"][label]
            out.append(f"| h={h} | {label} | {v['cells']} | {v['brier_difference_sum']:+.3f} | {vo['brier_difference_sum']:+.3f} | "
                       f"{v['mean_prob_net']:.3f} / {v['mean_prob_flag']:.3f} | {vo['mean_prob_net']:.3f} / {vo['mean_prob_flag']:.3f} |")
    out.append("")
    out += two_column_table({"2018-19": t3["by_regime"]["2018-19"]}, {"2018-19": t3o["by_regime"]["2018-19"]}, SCORES, "regime") + [""]
    add("### The 2026 days (descriptive, decide nothing): lead 1 and net against flag by lead\n")
    out += two_column_table({"all lead-1 cells": n18["table_1"]["all lead-1 cells"]}, {"all lead-1 cells": n16["table_1"]["all lead-1 cells"]}, ("brier_gt5", "grid_crps"),
                            "target-day type") + [""]
    out += two_column_table(n18["table_3"]["by_lead"], n16["table_3"]["by_lead"], ("brier_gt5", "grid_crps"), "lead") + [""]
    add("## 5. Every table against its 16:00 record\n")
    out += compare_table(r["compare"]) + [""]
    rows = differing_sections(r["compare"])
    if rows:
        add("Sections (the first three components of a path) with a number that differs or is in one record only:\n")
        out += ["| record | section | compared | differ | in one record only | largest difference |", "|---|---|---|---|---|---|"] + rows + [""]
    else:
        add("No section of either record has a number that differs or is in one record only.\n")
    differing = r["compare"]["announced"]["all"]["paths"] + r["compare"]["diagnosis"]["all"]["paths"]
    if differing:
        add("Differing numbers (first listed; 18:00, then 16:00):\n")
        out += [f"- `{x['path']}`: {x['new']:.6g} against {x['old']:.6g}" for x in differing[:40]] + [""]
    add("## What was checked, and what was not\n")
    add("**Checked.** The declaration is committed and unchanged (the script refuses otherwise). The repository's decision instant and the module's are 18:00 "
        "(`require_instant`). The 16:00 cells file is the 16:00 walk of this panel (`check_cells`). #1288's script reproduces #1255's and #1273's pooled means to the "
        "last digit at 18:00 (it refuses to write otherwise), and #1319's script reproduces #1288's record. The published daily record's outcomes equal the "
        "panel's on every B3 day (`b3_score` refuses otherwise).\n")
    add("**Not checked.** B3 is scored at lead 1 only, because the published record has no other lead, and its forecasts are the 16:00 record's. The scarcity-state "
        "label change is reported, not investigated. The H3 and H9 candidates that do read series published between 16:00 and 18:00 are not re-run here. "
        "No claim changes: (s3c-ann-net) stays the candidate Eleonora named on 29 October 2026, and these figures are on days already seen.\n")
    return "\n".join(out).rstrip() + "\n"


def cmd_page(args) -> int:
    text = render(args)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(text, encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("cells", help="the per-cell scores of (s3c), (s3c-ann), (s3c-ann-net) from a checkout (run on the 16:00 checkout)")
    c.add_argument("--root", required=True)
    c.add_argument("--panel", required=True)
    c.add_argument("--output", required=True)
    s = sub.add_parser("score", help="the paired row, B3, and the comparison of the 18:00 records with the 16:00 records")
    s.add_argument("--panel", required=True)
    s.add_argument("--cells-1600", required=True)
    s.add_argument("--announced", required=True)
    s.add_argument("--diagnosis", required=True)
    s.add_argument("--output", required=True)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    return {"cells": cmd_cells, "score": cmd_score, "page": cmd_page}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
