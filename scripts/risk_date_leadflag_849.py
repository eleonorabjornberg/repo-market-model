"""H6 step 1 re-read with the coupon-settlement flag read by lead (#849; H6 step 1, development tier).

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/risk_date_leadflag_849.json`, which `run` refuses to read unless it is committed and unchanged.
The corrected arithmetic is `repo_model.risk_date_spread.target_risk_type` (Eleonora's ruling on #720, 13 October 2026,
point 2): a coupon settlement makes a target a risk date only at the leads where it was public at the decision instant. This
script runs #693's score (`scripts/risk_date_spread_693.py`) and #739's studentized re-read (`scripts/risk_date_reread_739.py`)
twice on the same panel: once with the old reading (the coupon clause at every lead) as a control that must reproduce the
published evidence, and once with the corrected one. Their pages are left as published. Scored days are #693's: decision days
whose five targets are on or before 2025-12-31 (`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol
v1, #640).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/risk_date_leadflag_849.py run --panel /tmp/funding_panel.csv \\
        --output docs/research/evidence/risk-date-leadflag-849.json
    PYTHONPATH=src python3 scripts/risk_date_leadflag_849.py page \\
        --result docs/research/evidence/risk-date-leadflag-849.json --output docs/research/risk-date-leadflag-849.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from argparse import Namespace
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import risk_date_spread as rds  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


s693 = _load("risk_date_spread_693")
s739 = _load("risk_date_reread_739")

DECLARATION = REPO / "metadata" / "risk_date_leadflag_849.json"
PUBLISHED_693 = REPO / "docs" / "pivot" / "evidence" / "risk-date-spread" / "score.json"
PUBLISHED_739 = REPO / "docs" / "research" / "evidence" / "risk-date-reread-739.json"
A, C = s693.A, s693.C
LABEL = {A: "H5 mean reversion (#686)", C: "type x state", "B1": "B1 persistence", "calendar": "risk-date calendar"}
READINGS = ("studentized", "percentile")


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s693.committed_declaration(path)


def old_target_risk_type(panel, decision_index, h, *, registry, decision_time, splits):
    """The reading before #849: the coupon clause at every lead."""

    row = panel[decision_index + h]
    return rds.risk_day_type(row.date, row.values, splits)


@contextlib.contextmanager
def reading(target_risk_type: Callable) -> Iterator[None]:
    """Run with `risk_date_spread.target_risk_type` replaced, and restore it."""

    kept = rds.target_risk_type
    rds.target_risk_type = target_risk_type
    try:
        yield
    finally:
        rds.target_risk_type = kept


def scores(panel_path: str, draws: int) -> dict:
    """#693's score and #739's re-read as they run on the code now in `rds` (the caller sets the reading)."""

    with tempfile.TemporaryDirectory() as tmp:
        out693, out739 = Path(tmp) / "693.json", Path(tmp) / "739.json"
        s693.score(Namespace(panel=panel_path, output=str(out693), markdown=None, draws=draws))
        s739.score(Namespace(panel=panel_path, output=str(out739), markdown=None, draws=draws))
        return {"693": json.loads(out693.read_text()), "739": json.loads(out739.read_text())}


def max_difference(left, right) -> Optional[float]:
    """The largest absolute difference between two JSON trees of the same shape, or `None` if the shapes differ.

    Strings and lists of strings must be equal; a number is compared by value. Keys the trees do not share are ignored
    (`notes`, `declaration`, `issue` and the like are compared by the caller where it matters).
    """

    if isinstance(left, bool) or isinstance(right, bool):
        return 0.0 if left == right else None
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right))
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        worst = 0.0
        for key in left.keys() & right.keys():
            part = max_difference(left[key], right[key])
            if part is None:
                return None
            worst = max(worst, part)
        return worst
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return None
        worst = 0.0
        for a, b in zip(left, right):
            part = max_difference(a, b)
            if part is None:
                return None
            worst = max(worst, part)
        return worst
    return 0.0 if left == right else None


def control(rerun: dict) -> dict:
    """Whether the old reading reproduces the published evidence, on the keys that carry the figures."""

    published = {"693": json.loads(PUBLISHED_693.read_text()), "739": json.loads(PUBLISHED_739.read_text())}
    out = {}
    for key, tree in published.items():
        figures = {k: tree[k] for k in ("primary", "kill_rule") if k in tree}
        figures.update({k: tree[k] for k in ("splits", "regime_three", "target_days") if k in tree})
        diff = max_difference(figures, {k: rerun[key][k] for k in figures})
        out[key] = {"reproduces": diff is not None and diff == 0.0, "max_abs_difference": diff}
    return out


def cell_counts(panel, splits, registry, kind_of: Callable) -> dict:
    """Per lead and risk type, the decision days (up to 2025-12-31 targets) whose lead-h target is a risk date."""

    counts: Dict[int, Counter] = {h: Counter() for h in sp.HORIZONS}
    targets: Dict[int, Counter] = {}
    seen = {}
    for i in range(len(panel) - max(sp.HORIZONS)):
        if panel[i + max(sp.HORIZONS)].date > s693.LAST_DAY:
            break
        for h in sp.HORIZONS:
            kind = kind_of(panel, i, h, registry=registry, decision_time=s693.DECISION_TIME, splits=splits)
            if kind is not None:
                counts[h][kind] += 1
                seen.setdefault(panel[i + h].date, kind)
    by_type = Counter(seen.values())
    return {
        "cells": {str(h): {k: counts[h][k] for k in rds.RISK_TYPES} for h in sp.HORIZONS},
        "target_days_by_type": {k: by_type[k] for k in rds.RISK_TYPES},
    }


def run(args) -> int:
    declaration = committed_declaration()
    panel_path = args.panel
    panel = load_daily_panel(Path(panel_path))
    splits = load_split_declaration(s693.SPLITS)
    registry = json.loads(s693.SOURCES.read_text(encoding="utf-8"))
    with reading(old_target_risk_type):
        old = scores(panel_path, args.draws)
        old_cells = cell_counts(panel, splits, registry, old_target_risk_type)
    new = scores(panel_path, args.draws)
    new_cells = cell_counts(panel, splits, registry, rds.target_risk_type)
    result = {
        "issue": 849, "declaration": str(DECLARATION.relative_to(REPO)), "label": "development, not a verdict",
        "panel_sha256": panel_sha256(Path(panel_path)), "draws": args.draws, "seed": s693.SEED,
        "control": control(old),
        "day_set": {"old": old_cells, "new": new_cells,
                    "scored_cells": {"old": old["693"]["notes"]["risk_date_cells"], "new": new["693"]["notes"]["risk_date_cells"]},
                    "scored_target_days": {"old": old["693"]["target_days"], "new": new["693"]["target_days"]}},
        "corrected": {"693": new["693"], "739": new["739"]},
        "published": {"693": json.loads(PUBLISHED_693.read_text()), "739": json.loads(PUBLISHED_739.read_text())},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------


def pct(value: float) -> str:
    return f"{100.0 * value:+.2f}%"


def skill(row: dict) -> str:
    if "undefined" in row:
        return "undefined"
    low, high = row["skill_interval"]
    return f"{pct(row['skill'])} [{pct(low)}, {pct(high)}]"


def moved_pairs(day_set: dict) -> List[str]:
    old, new = day_set["old"]["cells"], day_set["new"]["cells"]
    return [f"lead {h} {k}" for h in sorted(old, key=int) for k in rds.RISK_TYPES if old[h][k] != new[h][k]]


def kill_words(rule: dict) -> str:
    if not rule["killed"]:
        return "not killed (skill against both benchmarks on CRPS or MAE)"
    if not rule["killed_on_the_weaker_reading"]:
        return "killed on the declared reading, not on the weaker one"
    return "killed on both readings"


def page_text(r: dict) -> str:
    c693, c739 = r["corrected"]["693"], r["corrected"]["739"]
    p693, p739 = r["published"]["693"], r["published"]["739"]
    day_set = r["day_set"]
    moved = moved_pairs(day_set)
    lines = [
        "# H6 step 1 with the coupon-settlement flag read by lead (#849)", "",
        "**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), step 1, re-read after a leak fix. "
        "**Development data only: this is not a verdict** (scoring protocol v1, #640). Generated by "
        "`scripts/risk_date_leadflag_849.py page` from `docs/research/evidence/risk-date-leadflag-849.json`; the declaration is "
        "`metadata/risk_date_leadflag_849.json`, committed before any addendum score. The pages of #693 and #739 are left as published.", "",
        "**What changed.** Eleonora's ruling on #720 (13 October 2026, point 2): a settlement flag counts only at leads where it was "
        "already announced. #693's day set read a coupon settlement at every lead 1 to 5, so a target day whose only claim to be a risk "
        "date was a coupon settlement was typed and forecast as one at leads 2 to 5 although the flag was not public at the decision. "
        "Under the registry's declared availability a settlement is public one panel day ahead, so it counts at lead 1 only. "
        "Quarter-ends, month-ends and tax dates are calendar facts and count at every lead.", "",
        "**Control.** With the old reading restored, the same two scripts "
        + ("reproduce" if all(v["reproduces"] for v in r["control"].values()) else "DO NOT reproduce")
        + " the published evidence: #693's `score.json` "
        + f"(largest absolute difference {r['control']['693']['max_abs_difference']}) and #739's `risk-date-reread-739.json` "
        + f"({r['control']['739']['max_abs_difference']}).", "",
        "## The day set", "",
        f"Scored (decision day, lead) cells: {day_set['scored_cells']['old']} before, {day_set['scored_cells']['new']} after. "
        f"Scored target days: {day_set['scored_target_days']['old']['total']} before, {day_set['scored_target_days']['new']['total']} after.", "",
        "| lead | " + " | ".join(f"{k} before / after" for k in rds.RISK_TYPES) + " |",
        "|---|" + "---|" * len(rds.RISK_TYPES),
    ]
    for h in sorted(day_set["old"]["cells"], key=int):
        o, n = day_set["old"]["cells"][h], day_set["new"]["cells"][h]
        lines.append(f"| {h} | " + " | ".join(f"{o[k]} / {n[k]}" for k in rds.RISK_TYPES) + " |")
    lines += [
        "", f"Of the 5 leads x 4 risk types, **{len(moved)} pairs move**: {', '.join(moved) if moved else 'none'}.", "",
        "Target days by type (before / after): " + ", ".join(
            f"{k} {day_set['scored_target_days']['old']['by_type'].get(k, 0)} / {day_set['scored_target_days']['new']['by_type'].get(k, 0)}"
            for k in rds.RISK_TYPES) + ".", "",
        "## Pooled scores", "",
        "| metric | model | published mean | corrected mean |", "|---|---|---|---|",
    ]
    for metric, title in (("grid_crps", "grid CRPS bp"), ("mae", "MAE of the median bp")):
        for m in s693.MODELS:
            lines.append(f"| {title} | {LABEL[m]} | {p693['primary'][metric]['means'][m]:.3f} | {c693['primary'][metric]['means'][m]:.3f} |")
    for name, p, c, interval in (("#693's percentile interval", p693, c693, "percentile"), ("the studentized interval of #739", p739, c739, "studentized")):
        lines += ["", f"Skill [90%], {name}: published, then corrected.", "",
                  "| metric | candidate vs benchmark | published | corrected |", "|---|---|---|---|"]
        for metric, title in (("grid_crps", "CRPS"), ("mae", "MAE")):
            for cand in s693.CANDIDATES:
                for b in s693.BENCHMARKS:
                    lines.append(f"| {title} | {LABEL[cand]} vs {LABEL[b]} | {skill(p['primary'][metric]['vs'][cand][b])} | {skill(c['primary'][metric]['vs'][cand][b])} |")
    lines += ["", "## The declared kill rule", "",
              f"* #693's reading (percentile interval): published {kill_words(p693['kill_rule'])}; corrected {kill_words(c693['kill_rule'])}.",
              f"* #739's reading (studentized interval): published {kill_words(p739['kill_rule'])}; corrected {kill_words(c739['kill_rule'])}.", ""]
    flipped = (p693["kill_rule"]["killed"] != c693["kill_rule"]["killed"]) or (p739["kill_rule"]["killed"] != c739["kill_rule"]["killed"])
    signs = [
        (metric, cand, b)
        for metric in ("grid_crps", "mae") for cand in s693.CANDIDATES for b in s693.BENCHMARKS
        if (p693["primary"][metric]["vs"][cand][b]["skill"] > 0) != (c693["primary"][metric]["vs"][cand][b]["skill"] > 0)
    ]
    lines += ["## By regime and by day type (first candidate, CRPS, #693's interval)", "",
              "| split | group | days (published / corrected) | vs B1 published | vs B1 corrected | vs calendar published | vs calendar corrected |",
              "|---|---|---|---|---|---|---|"]
    for split in ("regime_three", "day_type"):
        for label in sorted(c693["splits"][split]):
            pc, cc = p693["splits"][split].get(label, {}), c693["splits"][split][label]
            if "grid_crps" not in cc or "grid_crps" not in pc:
                lines.append(f"| {split} | {label} | {pc.get('days', 0)} / {cc['days']} | not tested (fewer than 20 days) | | | |")
                continue
            vs_p, vs_c = pc["grid_crps"]["vs"][A], cc["grid_crps"]["vs"][A]
            lines.append(f"| {split} | {label} | {pc['days']} / {cc['days']} | {skill(vs_p['B1'])} | {skill(vs_c['B1'])} | "
                         f"{skill(vs_p['calendar'])} | {skill(vs_c['calendar'])} |")
    lines += [
        "", "## For Eleonora", "",
        ("**The corrected rows change step 1's reading.** " if flipped or signs else "**The corrected rows leave step 1's reading unchanged:** ")
        + (f"the kill rule's outcome {'flips' if flipped else 'is the same'} and {len(signs)} pooled skill sign(s) change. " if flipped or signs
           else "the kill rule's outcome is the same on both intervals and no pooled skill changes sign. ")
        + "Marked question: " + ("this changes what step 1 says, so whether the #693 and #739 pages carry a note pointing here is hers."
                                 if flipped or signs else "none from this re-read; whether the #693 and #739 pages carry a note pointing here is hers."), "",
        "Nothing is corrected for multiplicity, no model is refitted beyond what #693 does, and the published pages and records are not edited.", "",
    ]
    return "\n".join(lines)


def page(args) -> int:
    result = json.loads(Path(args.result).read_text())
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(page_text(result), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="score #693 and #739 on the old and the corrected reading")
    r.add_argument("--panel", required=True)
    r.add_argument("--output", required=True)
    r.add_argument("--draws", type=int, default=sp.DRAWS)
    r.set_defaults(func=run)
    g = sub.add_parser("page", help="write the addendum page from a result file")
    g.add_argument("--result", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
