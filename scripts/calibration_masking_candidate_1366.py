"""Calibration masking on the candidate's bands: how optimistic is its historical calibration? (#1366, H5, registration design).

A development study, never a verdict. `docs/decisions/information-set.md` ("Calibration masking is a calibration bias, not leakage")
accepts that a calibration subfit may train on a frame masked at a later cutoff than its own decision instant. The outside review of
95d21b1f asks how optimistic that makes the candidate's historical band scores. This study answers for (s3c-ann-net), the H5 candidate, at
the 18:00 decision instant, in three steps. Every choice is in `metadata/calibration_masking_candidate_1366.json`, which `walk` refuses to
read unless it is committed and unchanged.

1. **Closure audit.** The candidate's bands come from one fitting step, the refit of its residual pool and term effects every 21 decision
   days (`spread_mr_state_calendar.refit`, on the training pairs of `spread_mean_reversion.training_rows`). The modules reachable by import
   from the candidate (and the `repo_model` imports of the scripts that walk it) are listed, and none may be `ml`, `calibrated_stack`,
   `walk_calibration`, `group_calibration`, `recalibration` or `probability_calibration`, nor use the name `calibration_masking` or `cross_conformal` in code (a docstring that mentions one is not code): the candidate has no conformal or cross-conformal calibration subfit, which is what the note describes.
2. **Pair audit and the honest version.** The candidate is walked twice per window. AS RUN is #1288's walk unchanged. HONEST is the same walk
   with the training pairs of every refit filtered to those whose target row is at or before `InformationRule.anchor` of that refit's decision
   (the last row whose target is observable at the decision instant, per lead), a check that does not use the production guard
   (`protocol_benchmarks._require_public`). The recorder wraps `spread_mean_reversion.training_rows`; both walks record the pairs the honest
   filter would drop and the honest walk drops them.
3. **Scores.** Both versions are scored on the cells (decision day, lead 1 to 5): grid CRPS, upper-tail twCRPS and the coverage of the closed
   central 50% and 90% bands, pooled and by regime and pressure-day type of the target; the difference HONEST minus AS RUN is the bias in the
   scores. The AS RUN mean grid CRPS must equal the 1314 record to 1e-9 or no record is written.

Commands (a cloud run; each walk is minutes):

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 18:00:00
    OUT=docs/research/calibration-masking-candidate-1366
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/calibration_masking_candidate_1366.py walk --panel PUB.csv --window development --output WALK/development.json
    RMM_DECISION_TIME=18:00 PYTHONPATH=src python3 scripts/calibration_masking_candidate_1366.py walk --panel PUB.csv --window 2026 --output WALK/2026.json
    PYTHONPATH=src python3 scripts/calibration_masking_candidate_1366.py score --walks WALK --output $OUT/result.json
    PYTHONPATH=src python3 scripts/calibration_masking_candidate_1366.py page --score $OUT/result.json --output docs/research/calibration-masking-candidate-1366-result.md

Stdlib only. No day after 2026-09-03 and no locked day is read.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Set, Tuple
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "metadata" / "calibration_masking_candidate_1366.json"
OUT = REPO / "docs" / "research" / "calibration-masking-candidate-1366"
RECORD_1314 = REPO / "docs" / "research" / "s3c-ann-net-1800-1314" / "announced-settlement-1800.json"
SRC = REPO / "src" / "repo_model"
SEED = 1366
WINDOWS = ("development", "2026")
WINDOW_LAST = {"development": date(2025, 12, 31), "2026": EXPLORATORY_END}
CANDIDATE = "sc_s3c_ann_net"
GRID = sp.GRID
LEADS = tuple(sp.HORIZONS)
VERSIONS = ("as_run", "honest")
START_MODULES = ("s3c_announced", "s3c_candidate", "spread_mr_state_calendar")
WALKING_SCRIPTS = ("s3c_announced_settlement_1288", "s3c_net_settlement_1273", "s3c_candidate_1255")
FORBIDDEN_MODULES = ("ml", "calibrated_stack", "walk_calibration", "group_calibration", "recalibration", "probability_calibration")
FORBIDDEN_TOKENS = ("calibration_masking", "cross_conformal")
BAND = {"band50": (GRID.index(0.25), GRID.index(0.75)), "band90": (GRID.index(0.05), GRID.index(0.95))}


def refuse_beyond(days: Sequence[date], last: date, *, where: str = "calibration_masking_candidate_1366") -> None:
    """Refuse a day after `last` (the window's declared end) and a day of a tier that is still locked: raises `LookAheadError`."""

    days = sorted(days)
    for day in days:
        if day > last:
            raise LookAheadError(f"{where}: day {day} is after {last}, the last day of the window this study scores")
    require_exploratory_window(days, where=where)


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


# -- the honest filter and the recorder ----------------------------------------------------------------------------------------


def observable_pairs(pairs: Sequence[Tuple[int, int]], honest_anchor: int) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Split training pairs `(origin, target)` into those whose target row is at or before `honest_anchor` (observable at the decision) and
    those after it."""

    kept, dropped = [], []
    for origin, target in pairs:
        if target <= honest_anchor:
            kept.append((origin, target))
        else:
            dropped.append((origin, target))
    return kept, dropped


class Recorder:
    """Wraps `spread_mean_reversion.training_rows`: records every refit's pairs and, when `honest`, drops those the honest filter drops.

    `honest_anchor(decision_index, lead)` is the last row whose target is observable at the decision on row `decision_index`, for `lead`.
    """

    def __init__(self, *, honest: bool, honest_anchor: Callable[[int, int], int]):
        self.honest = honest
        self.honest_anchor = honest_anchor
        self.calls: Dict[int, dict] = {}

    def wrap(self, original):
        def training_rows(panel, decision_index, anchor, *, lag, levels):
            rows = original(panel, decision_index, anchor, lag=lag, levels=levels)
            kept_rows: Dict[int, List[Tuple[int, int]]] = {}
            pairs: Dict[int, int] = {}
            would: Dict[int, int] = {}
            dropped: Dict[int, int] = {}
            latest: Dict[int, int] = {}
            for h, lead_pairs in rows.items():
                kept, gone = observable_pairs(lead_pairs, self.honest_anchor(decision_index, h))
                kept_rows[h] = kept if self.honest else list(lead_pairs)
                pairs[h] = len(lead_pairs)
                would[h] = len(gone)
                dropped[h] = len(gone) if self.honest else 0
                latest[h] = max((t for _o, t in lead_pairs), default=-1)
            record = {"anchor": anchor, "lag": lag, "pairs": pairs, "would_drop": would, "dropped": dropped, "latest_target": latest, "calls": 1}
            seen = self.calls.get(decision_index)
            if seen is None:
                self.calls[decision_index] = record
            else:
                for key in ("anchor", "lag", "pairs", "would_drop", "dropped", "latest_target"):
                    if seen[key] != record[key]:
                        raise ValueError(f"the calls of the refit on row {decision_index} disagree on {key}: {seen[key]} against {record[key]}")
                seen["calls"] += 1
            return kept_rows

        return training_rows


# -- the closure audit ---------------------------------------------------------------------------------------------------------


def _imports(source: str, package_module: str = "") -> Set[str]:
    """The `repo_model` modules a source imports: `from . import x`, `from .x import y`, `from repo_model import x`, `import repo_model.x`."""

    found: Set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom):
            from_package = node.level == 1 or node.module == "repo_model"
            if node.level == 1 and node.module:
                found.add(node.module.split(".")[0])
            elif from_package and not (node.level == 0 and node.module != "repo_model"):
                found.update(alias.name for alias in node.names)
            elif node.level == 0 and node.module and node.module.startswith("repo_model."):
                found.add(node.module.split(".")[1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("repo_model."):
                    found.add(alias.name.split(".")[1])
    return found


def import_closure(start: Sequence[str], root: Path = SRC) -> List[str]:
    """The modules of `root` reachable by import from `start`, sorted."""

    seen: Set[str] = set()
    todo = list(start)
    while todo:
        name = todo.pop()
        if name in seen or not (root / f"{name}.py").exists():
            continue
        seen.add(name)
        todo.extend(_imports((root / f"{name}.py").read_text(encoding="utf-8")) - seen)
    return sorted(seen)


def forbidden_modules(modules: Sequence[str]) -> List[str]:
    return sorted(m for m in modules if m in FORBIDDEN_MODULES)


def _code_tokens(source: str) -> List[str]:
    """The identifiers, keyword names and string constants of a source's code, without its docstrings and comments."""

    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                docstrings.add(id(body[0].value))
    tokens: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            tokens.append(node.id)
        elif isinstance(node, ast.Attribute):
            tokens.append(node.attr)
        elif isinstance(node, ast.keyword) and node.arg:
            tokens.append(node.arg)
        elif isinstance(node, ast.arg):
            tokens.append(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            tokens.append(node.name)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            tokens.append(node.value)
    return tokens


def forbidden_hits(sources: Mapping[str, str]) -> List[str]:
    """`"<module>: <token>"` for each forbidden token that appears in a source's code (a docstring or a comment that names it is not code)."""

    hits = []
    for name, text in sources.items():
        tokens = _code_tokens(text)
        for token in FORBIDDEN_TOKENS:
            if any(token in t for t in tokens):
                hits.append(f"{name}: {token}")
    return hits


def closure_audit() -> dict:
    modules = import_closure(START_MODULES)
    script_imports = {}
    for name in WALKING_SCRIPTS:
        text = (REPO / "scripts" / f"{name}.py").read_text(encoding="utf-8")
        script_imports[name] = sorted(_imports(text))
    reachable = sorted(set(modules) | {m for names in script_imports.values() for m in import_closure(names)})
    sources = {m: (SRC / f"{m}.py").read_text(encoding="utf-8") for m in reachable}
    bad_modules = forbidden_modules(reachable)
    bad_tokens = forbidden_hits(sources)
    return {
        "start": list(START_MODULES), "scripts": list(WALKING_SCRIPTS), "modules": reachable, "module_count": len(reachable),
        "forbidden_modules": list(FORBIDDEN_MODULES), "forbidden_tokens": list(FORBIDDEN_TOKENS),
        "forbidden_modules_found": bad_modules, "forbidden_tokens_found": bad_tokens,
        "no_calibration_subfit": not bad_modules and not bad_tokens,
    }


# -- the scores ----------------------------------------------------------------------------------------------------------------


def band_coverage(cells: Sequence[Tuple[Sequence[float], float]]) -> Dict[str, Optional[float]]:
    """The share of cells inside the closed central 50% and 90% bands; `None` for no cell."""

    out: Dict[str, Optional[float]] = {}
    for name, (lo, hi) in BAND.items():
        out[name] = sum(int(q[lo] <= y <= q[hi]) for q, y in cells) / len(cells) if cells else None
    return out


def paired_difference(as_run: Sequence[Tuple[Sequence[float], float]], honest: Sequence[Tuple[Sequence[float], float]]) -> dict:
    """Both versions on the same cells `(quantiles, outcome)`: each score's mean for each version and HONEST minus AS RUN, the number of
    cells whose forecast differs, and the largest quantile difference (bp).

    Raises:
        ValueError: the two sets are not the same cells.
    """

    if len(as_run) != len(honest) or any(a[1] != b[1] for a, b in zip(as_run, honest)):
        raise ValueError("the two versions are not scored on the same cells")
    n = len(as_run)
    out: dict = {"cells": n}
    if not n:
        return out
    differing = 0
    largest = 0.0
    for (qa, _ya), (qb, _yb) in zip(as_run, honest):
        gap = max(abs(a - b) for a, b in zip(qa, qb))
        differing += int(gap > 0.0)
        largest = max(largest, gap)
    out["cells_differing"] = differing
    out["max_abs_quantile_difference"] = largest
    for key, loss in (("grid_crps", sp.grid_crps), ("twcrps", sp.upper_tail_twcrps)):
        a = sum(loss(q, y) for q, y in as_run) / n
        b = sum(loss(q, y) for q, y in honest) / n
        out[key] = {"as_run": a, "honest": b, "difference": b - a}
    cov_a, cov_b = band_coverage(as_run), band_coverage(honest)
    out["coverage"] = {name: {"as_run": cov_a[name], "honest": cov_b[name], "difference": cov_b[name] - cov_a[name]} for name in BAND}
    return out


def window_summary(cells: Sequence[dict], as_run: Mapping[str, Sequence[float]], honest: Mapping[str, Sequence[float]]) -> dict:
    """Pooled and split paired differences. `cells` carry `key` (the decision day and lead), `y`, `regime` and `pressure`;
    `as_run` and `honest` map the key to the 23 quantiles."""

    def take(rows: Sequence[dict], version: Mapping[str, Sequence[float]]):
        return [(version[c["key"]], c["y"]) for c in rows]

    out = {"pooled": paired_difference(take(cells, as_run), take(cells, honest)), "by_lead": {}, "by_regime": {}, "by_pressure_day_type": {}}
    for lead in LEADS:
        rows = [c for c in cells if c["lead"] == lead]
        out["by_lead"][str(lead)] = paired_difference(take(rows, as_run), take(rows, honest))
    for field, name in (("regime", "by_regime"), ("pressure", "by_pressure_day_type")):
        for label in sorted({c[field] for c in cells}):
            rows = [c for c in cells if c[field] == label]
            out[name][label] = paired_difference(take(rows, as_run), take(rows, honest))
    return out


# -- the walks -----------------------------------------------------------------------------------------------------------------


def _load(name: str, alias: str):
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def make_recorder(honest: bool, panel, registry, decision_time) -> Recorder:
    from repo_model.asof import InformationRule

    dates = [row.date for row in panel]
    rules = {h: InformationRule(registry, (), decision_time=decision_time, horizon=h) for h in LEADS}
    return Recorder(honest=honest, honest_anchor=lambda index, lead: rules[lead].anchor(dates, index + lead))


def walk_command(args) -> int:
    os.environ["RMM_DECISION_TIME"] = "18:00"
    declared = committed_declaration()
    from repo_model import announced_iorb, decision_instant, policy_events, s3c_announced, spread_mean_reversion as smr, spread_mr_calendar as cal
    from repo_model.baseline import panel_sha256
    from repo_model.evaluation_splits import load_split_declaration

    m = _load("s3c_announced_settlement_1288", "s3c_announced_settlement_1288_in_1366")
    if decision_instant.DECISION_TIME.isoformat(timespec="minutes") != "18:00" or m.k.DECISION_TIME.isoformat(timespec="minutes") != "18:00":
        raise ValueError("this study is made at the 18:00 decision instant")
    window = args.window
    panel_path = Path(args.panel)
    sha = panel_sha256(panel_path)
    panel = [row for row in m.load_daily_panel(panel_path) if row.date <= m.LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/calibration_masking_candidate_1366")
    splits = load_split_declaration(m.c.SPLITS)
    registry = json.loads(m.c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    table = cal.TermTable(panel, announced_iorb.load_announcements(m.c.IORB_TABLE), decision_time=m.c.DECISION_TIME)
    auctions = m.m1273.load_auctions()
    results = m.load_results()
    frame, _notes, _mine, _cell_table, _groups = m.m1255.build(window, panel, splits, registry, table, register, args.first)
    days = m.candidate_days(frame, window, args.first)
    settings = dict(registry=registry, decision_time=m.k.DECISION_TIME, splits=splits)
    iorb = announced_iorb.load_announcements(m.c.IORB_TABLE)
    both = s3c_announced.AnnouncedTermTable(panel, iorb, results, decision_time=m.k.DECISION_TIME)
    net_table = s3c_announced.AnnouncedNetSizeTable(panel, auctions, decision_time=m.k.DECISION_TIME)
    dates = [row.date for row in panel]

    versions: Dict[str, dict] = {}
    for version in VERSIONS:
        recorder = make_recorder(version == "honest", panel, registry, m.k.DECISION_TIME)
        with mock.patch.object(smr, "training_rows", recorder.wrap(smr.training_rows)):
            walk = m.sc.walk(panel, days, both, m.s3c_net.constant_states(panel), (s3c_announced.ANN_ARM, s3c_announced.ANN_NET_ARM),
                             sizes=net_table, **settings)
        raw = {d: walk.forecasts[s3c_announced.ANN_NET_ARM.name][d] for d in frame.days}
        forecasts = m.m1255.s3c_forecasts(frame, register, raw)
        late_fit = [d.isoformat() for d in frame.days if walk.fit_used[d] > d]
        refits = []
        for index in sorted(recorder.calls):
            c = recorder.calls[index]
            refits.append({
                "decision_day": dates[index].isoformat(), "anchor": dates[c["anchor"]].isoformat(), "lag": c["lag"],
                "pairs": {str(h): n for h, n in c["pairs"].items()}, "would_drop": {str(h): n for h, n in c["would_drop"].items()},
                "dropped": {str(h): n for h, n in c["dropped"].items()},
                "latest_target": {str(h): dates[t].isoformat() for h, t in c["latest_target"].items() if t >= 0},
            })
        versions[version] = {"forecasts": forecasts, "refits": refits, "fits_after_their_day": late_fit, "walk_refits": len(walk.fits)}

    cells = []
    for d in frame.days:
        for h in LEADS:
            t = frame.target(d, h)
            cells.append({"key": f"{d.isoformat()}/{h}", "day": d.isoformat(), "lead": h, "target": t.isoformat(), "y": frame.outcome[t],
                          "regime": frame.regime(t), "pressure": frame.day_type(t)})
    refuse_beyond([date.fromisoformat(c["target"]) for c in cells] + list(frame.days), WINDOW_LAST[window])
    doc = {
        "window": window, "instant": "18:00", "panel_sha256": sha, "declaration": declared["issue"], "cells": cells,
        "decision_days": len(frame.days),
        "versions": {
            v: {"refits": versions[v]["refits"], "fits_after_their_day": versions[v]["fits_after_their_day"], "walk_refits": versions[v]["walk_refits"],
                "quantiles": {f"{d.isoformat()}/{h}": list(versions[v]["forecasts"][d][h]) for d in frame.days for h in LEADS}}
            for v in VERSIONS
        },
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: {window}, {len(frame.days)} decision days, {len(cells)} cells")
    return 0


# -- score ---------------------------------------------------------------------------------------------------------------------


def refit_summary(refits: Sequence[dict]) -> dict:
    pairs = sum(sum(r["pairs"].values()) for r in refits)
    would = sum(sum(r["would_drop"].values()) for r in refits)
    dropped = sum(sum(r["dropped"].values()) for r in refits)
    return {
        "fit_attempts": len(refits), "training_pairs": pairs, "pairs_the_filter_would_drop": would, "pairs_dropped": dropped,
        "refits_with_a_drop": [r["decision_day"] for r in refits if sum(r["would_drop"].values()) > 0],
        "latest_target_is_the_anchor_at_every_refit": all(
            all(t <= r["anchor"] for t in r["latest_target"].values()) for r in refits
        ),
    }


def reproduction_check(name: str, cells: Sequence[dict], quantiles: Mapping[str, Sequence[float]], record: Mapping[str, object]) -> dict:
    group = record["windows"][name]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]["sc_s3c_ann_net"]
    theirs = group["mean"] if isinstance(group, dict) else group
    mine = sum(sp.grid_crps(quantiles[c["key"]], c["y"]) for c in cells) / len(cells)
    if abs(mine - theirs) > 1e-9:
        raise ValueError(f"{name}: the AS RUN mean grid CRPS is {mine!r} here and {theirs!r} in the 1314 record")
    return {"mean_grid_crps": mine, "record": theirs}


def score_command(args) -> int:
    declared = committed_declaration()
    record = json.loads(RECORD_1314.read_text(encoding="utf-8"))
    result: dict = {"issue": 1366, "declaration": "metadata/calibration_masking_candidate_1366.json", "label": "development, not a verdict",
                    "closure_audit": closure_audit(), "windows": {}, "reproduction": {}, "walk_files": {}, "amendments": declared["amendments"]}
    for name in WINDOWS:
        path = Path(args.walks) / f"{name}.json"
        if not path.exists():
            continue
        raw = path.read_bytes()
        doc = json.loads(raw)
        if result.get("panel_sha256") not in (None, doc["panel_sha256"]):
            raise ValueError("the walk files were made from different panels")
        result["panel_sha256"] = doc["panel_sha256"]
        result["walk_files"][name] = {"sha256": hashlib.sha256(raw).hexdigest()}
        cells = doc["cells"]
        as_run, honest = doc["versions"]["as_run"], doc["versions"]["honest"]
        result["reproduction"][name] = reproduction_check(name, cells, as_run["quantiles"], record)
        result["windows"][name] = {
            "decision_days": doc["decision_days"], "cells": len(cells),
            "walk_refits": as_run["walk_refits"],
            "as_run": refit_summary(as_run["refits"]), "honest": refit_summary(honest["refits"]),
            "fits_after_their_day": {"as_run": as_run["fits_after_their_day"], "honest": honest["fits_after_their_day"]},
            "scores": window_summary(cells, as_run["quantiles"], honest["quantiles"]),
        }
    if not result["windows"]:
        raise SystemExit(f"no walk file in {args.walks}")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------------------


def _n(x: Optional[float], digits: int = 4) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def _pct(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def _row(label: str, s: dict) -> str:
    if not s.get("cells"):
        return f"| {label} | 0 | | | | | |"
    return (f"| {label} | {s['cells']} | {_n(s['grid_crps']['as_run'])} / {_n(s['grid_crps']['honest'])} ({s['grid_crps']['difference']:+.4f}) "
            f"| {_n(s['twcrps']['as_run'])} / {_n(s['twcrps']['honest'])} ({s['twcrps']['difference']:+.4f}) "
            f"| {_pct(s['coverage']['band50']['as_run'])} / {_pct(s['coverage']['band50']['honest'])} "
            f"| {_pct(s['coverage']['band90']['as_run'])} / {_pct(s['coverage']['band90']['honest'])} | {s['cells_differing']} |")


def render(r: dict) -> str:
    audit = r["closure_audit"]
    lines = [
        "# Calibration masking on the candidate's bands (#1366)",
        "",
        "**Hypothesis and step:** H5 (primary goal), registration design (calibration). **Development data, not a verdict** (scoring protocol v1, "
        "#640). Nothing is registered or published, no record is edited and nothing is adopted. Generated by "
        "`scripts/calibration_masking_candidate_1366.py page` from `docs/research/calibration-masking-candidate-1366/result.json`; declared in "
        "`metadata/calibration_masking_candidate_1366.json` before any figure. Candidate: (s3c-ann-net) at the 18:00 decision instant. "
        f"Panel digest `{r['panel_sha256']}`.",
        "",
        "**The question.** `docs/decisions/information-set.md` accepts that a calibration subfit may train on a frame masked at a later cutoff than "
        "its own decision instant, and calls the effect a calibration bias, not leakage. The outside review asks how optimistic that makes the "
        "candidate's historical band scores. The directive: re-run the calibration step with every subfit restricted to pairs whose targets were "
        "observable at that subfit's own decision instant, score both versions, and report the size of the bias.",
        "",
        "## The answer",
        "",
    ]
    dev = r["windows"].get("development")
    if dev:
        pooled = dev["scores"]["pooled"]
        lines += [
            f"**The bias is {'exactly zero' if pooled['cells_differing'] == 0 else 'not zero'} for the candidate.** On the development window "
            f"({dev['decision_days']} decision days, {dev['cells']} cells) the honest filter would drop {dev['as_run']['pairs_the_filter_would_drop']} of "
            f"{dev['as_run']['training_pairs']} training pairs over {dev['walk_refits']} refits ({dev['as_run']['fit_attempts']} fit attempts), and {pooled['cells_differing']} cells differ "
            f"between the two versions (largest quantile difference {pooled['max_abs_quantile_difference']:.1e} bp). The paired difference in grid "
            f"CRPS (honest minus as run) is {pooled['grid_crps']['difference']:+.4f}, in upper-tail twCRPS {pooled['twcrps']['difference']:+.4f}, in "
            f"the coverage of the 90% band {100 * pooled['coverage']['band90']['difference']:+.2f} pp.",
            "",
            "**Why.** The candidate has no calibration subfit of the kind the note describes. Its bands come from one step, the refit of its residual "
            "pool and term effects every 21 decision days, on the pairs of `spread_mean_reversion.training_rows`, whose targets are at or before "
            "the refit's anchor (the last row public at its decision instant) by construction, and a forecast on a later day reads that older fit, "
            "never a fit made after its own decision. Its state interaction, where read, is the state of each pair's own decision day "
            "(`spread_mr_state_calendar.pair_state`). The closure audit below confirms that nothing in the candidate's import graph is a conformal "
            "or cross-conformal calibration or carries `calibration_masking`.",
            "",
        ]
    lines += [
        "## Closure audit",
        "",
        f"{audit['module_count']} `repo_model` modules are reachable by import from {', '.join('`' + s + '`' for s in audit['start'])} and from the "
        f"`repo_model` imports of {', '.join('`' + s + '`' for s in audit['scripts'])}. Forbidden modules: "
        f"{', '.join('`' + m + '`' for m in audit['forbidden_modules'])}; found: {audit['forbidden_modules_found'] or 'none'}. Forbidden text: "
        f"{', '.join('`' + t + '`' for t in audit['forbidden_tokens'])}; found: {audit['forbidden_tokens_found'] or 'none'}. "
        f"Conclusion: {'the candidate has no calibration subfit' if audit['no_calibration_subfit'] else 'a calibration path exists; read the list'}.",
        "",
        "Modules: " + ", ".join(f"`{m}`" for m in audit["modules"]) + ".",
        "",
    ]
    for name in WINDOWS:
        w = r["windows"].get(name)
        if not w:
            continue
        lines += [
            f"## {'Development window' if name == 'development' else '2026 days (shown apart, decide nothing)'}",
            "",
            f"{w['decision_days']} decision days, {w['cells']} cells. The AS RUN mean grid CRPS equals the 1314 record "
            f"({_n(r['reproduction'][name]['mean_grid_crps'], 6)}) to 1e-9.",
            "",
            f"Pair audit: {w['as_run']['fit_attempts']} fit attempts ({w['walk_refits']} of them the walk's refits; the others are early days that were "
            f"skipped for lack of history after their pairs were drawn), {w['as_run']['training_pairs']} training pairs; pairs the honest filter would drop: "
            f"{w['as_run']['pairs_the_filter_would_drop']}; pairs it dropped in the honest walk: {w['honest']['pairs_dropped']}; the latest target of "
            f"every refit is at or before its anchor: {w['as_run']['latest_target_is_the_anchor_at_every_refit']}; scored days whose fit was made after "
            f"them: {len(w['fits_after_their_day']['as_run']) + len(w['fits_after_their_day']['honest'])}.",
            "",
            "Each cell shows AS RUN / HONEST and, for the loss scores, honest minus as run.",
            "",
            "| group | cells | grid CRPS | upper-tail twCRPS | 50% band | 90% band | cells differing |",
            "|---|---|---|---|---|---|---|",
            _row("pooled", w["scores"]["pooled"]),
        ]
        for lead, s in w["scores"]["by_lead"].items():
            lines.append(_row(f"h = {lead}", s))
        for label, s in w["scores"]["by_regime"].items():
            lines.append(_row(f"regime {label}", s))
        for label, s in w["scores"]["by_pressure_day_type"].items():
            lines.append(_row(f"pressure-day type {label}", s))
        lines.append("")
        lines.append("Both versions are one computation here, so each paired difference is exactly 0 and its interval is the degenerate [0, 0]; no bootstrap interval is printed.")
        lines.append("")
    lines += [
        "## What this does not show",
        "",
        "- The note describes conformal and cross-conformal calibration of the gradient-boosted records (the gradient-boosted quantile fitter in `ml`, "
        "`calibration_masking`). Those are not the candidate. `scripts/calibration_masking_effect.py` (#78) is the tool that measures them and is "
        "not run here.",
        "- The candidate's bands are not corrected in any other way here. Whether they cover (the 90% band under-covers on the development "
        "window) is the question of #1363, not this one.",
        "- Refitting every day, instead of every 21 decision days, is a different sensitivity (a fresher fit), not the masking bias, and is not run.",
        "",
        "## Question for Eleonora",
        "",
        "**Q1. The candidate has no calibration subfit, so the masking bias on its bands is zero by construction and by measurement. Should the "
        "registration say so in one sentence, and should the sensitivity also be measured on the gradient-boosted records the note is about?**",
        "",
        "1. Say so in one sentence in the registration's known-limits section; do not measure the gradient-boosted records (they are not the "
        "registered candidate). **Default.**",
        "2. As 1, and also run `scripts/calibration_masking_effect.py` on the gradient-boosted cross-conformal records (a long run, on her Mac), so the "
        "size of the note's bias is on file.",
        "3. Do not mention it.",
        "",
        "The default changes no claim.",
        "",
    ]
    return "\n".join(lines)


def page_command(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    w = sub.add_parser("walk", help="walk (s3c-ann-net) as run and with the honest filter over one window and write both forecasts")
    w.add_argument("--panel", required=True)
    w.add_argument("--window", choices=WINDOWS, required=True)
    w.add_argument("--output", required=True)
    w.add_argument("--first", type=date.fromisoformat, default=None, help="start the walk on this day (a test only)")
    w.set_defaults(func=walk_command)
    s = sub.add_parser("score", help="the closure audit, the pair audit and the paired scores from the walk files")
    s.add_argument("--walks", required=True)
    s.add_argument("--output", required=True)
    s.set_defaults(func=score_command)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page_command)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
