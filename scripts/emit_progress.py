#!/usr/bin/env python3
"""Emit docs/pivot/progress.md and docs/research/progress.json: progress beyond pass or fail (#637).

H5 (the SOFR - IORB spread distribution in bp) is the primary goal and H9 the secondary one. This page shows, for
every candidate that has committed evidence, how far it has got: the spread forecast against as-of persistence,
the ordinary-day ranking, the Brier difference against climatology, the calibration per regime and the judge's
tier 1, 3 and 5 verdicts, together with the count of variants tried.

Nothing is scored here. Every figure is copied from a committed evidence file under `docs/pivot/evidence/`
(`SOURCES` names them); a figure the evidence does not hold is printed as "not measured" and never computed. Every
figure is development evidence and none is a verdict (scoring protocol v1, #640). The judge's tiers are reported
only: the +5 bp judge is retired as a decision rule. The data file is keyed by hypothesis (`hypotheses.H5`) so the
results page (#645) can read it; it is written by this script and never by hand.

Candidates are ordered by the commit that added their file, which is their position in the variant count; that
needs the full history, so a shallow clone is refused as in `scripts/emit_status.py`.

Standard library only.

    python3 scripts/emit_progress.py            # writes docs/pivot/progress.md and docs/research/progress.json
    python3 scripts/emit_progress.py --check    # writes nothing; fails if either is stale
"""
import difflib
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = "docs/pivot/progress.md"
DATA = "docs/research/progress.json"
CANDIDATES = "metadata/pressure_judge/candidates"
DECLARATIONS = "metadata/*.json"
EVIDENCE = "docs/pivot/evidence"
SOURCES = {
    "spread": EVIDENCE + "/spread-distribution/distribution.json",
    "ordinary": EVIDENCE + "/spread-distribution/ordinary.json",
    "calibration": EVIDENCE + "/spread-distribution/compare.json",
    "tiers": EVIDENCE + "/weighted-miss/tier1.json",
    "brier": EVIDENCE + "/*/compare*.json and " + EVIDENCE + "/*/paired*.json (those with a `brier` block)",
}
NOT_MEASURED = "not measured"
LABEL = "development, not a verdict"
HORIZONS = ("1", "2", "3", "4", "5")


def load(root, rel):
    path = Path(root) / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def interval(block):
    """A recorded interval as [lower, upper], or None when the evidence has none."""
    if block is None:
        return None
    if isinstance(block, dict):
        if "lower" in block and "upper" in block:
            return [block["lower"], block["upper"]]
        return None
    return list(block)


def group_figure(block):
    """One paired figure as the evidence records it: mean, interval, days."""
    if not block:
        return None
    return {"mean": block.get("mean"), "interval": interval(block.get("interval")), "days": block.get("days")}


def groups(by_group):
    """{'pooled': ..., 'regime': {...}, 'day_type': {...}} with every figure copied, none computed."""
    if not by_group:
        return None
    return {"pooled": group_figure(by_group.get("pooled")),
            "regime": {k: group_figure(v) for k, v in sorted((by_group.get("regime") or {}).items())},
            "day_type": {k: group_figure(v) for k, v in sorted((by_group.get("day_type") or {}).items())}}


def read_spread(root):
    doc = load(root, SOURCES["spread"])
    out = {}
    if not doc:
        return out
    for horizon, variants in sorted(doc.get("horizons", {}).items()):
        for name, v in variants.items():
            paired, mae = v.get("paired") or {}, v.get("mae_median") or {}
            out.setdefault(name, {})[horizon] = {
                "days": v.get("days"), "first": v.get("first"), "last": v.get("last"),
                "crps_bps": v.get("variant", {}).get("crps_bps"),
                "crps_bps_as_of_persistence": (v.get("as_of_persistence") or {}).get("crps_bps"),
                "crps_difference_vs_persistence": groups(paired.get("as_of_persistence")),
                "mae_median_difference_vs_persistence": groups(mae.get("as_of_persistence")),
            }
    return out


def read_ordinary(root):
    doc = load(root, SOURCES["ordinary"])
    out = {}
    for name, row in ((doc or {}).get("rows") or {}).items():
        lead = (row.get("leads") or {}).get("1") or {}
        out[name] = {
            "pooled_auroc": (row.get("pooled") or {}).get("auroc"),
            "lead_1": {"auroc": lead.get("auroc"), "auroc_interval": interval(lead.get("auroc_interval")),
                       "reliability_slope": (lead.get("reliability") or {}).get("slope"),
                       "slope_interval": interval(lead.get("slope_interval")),
                       "days": lead.get("days"), "events": lead.get("events")},
        }
    return out


def read_calibration(root):
    doc = load(root, SOURCES["calibration"])
    out = {}
    for name, cells in ((doc or {}).get("calibration") or {}).items():
        out[name] = {cell: {"days": v.get("days"), "predicted": v.get("predicted"), "realised": v.get("realised")}
                     for cell, v in sorted(cells.items())}
    return out


def read_tiers(root):
    doc = load(root, SOURCES["tiers"])
    out = {}
    for name, row in ((doc or {}).get("weighted") or {}).items():
        v = row.get("verdict") or {}
        out[name] = {"tier_1": v.get("tier_1_onset_warning"), "tier_3": v.get("tier_3_no_crying_wolf"),
                     "tier_5": v.get("tier_5_week_ahead")}
    return out


def read_brier(root):
    """Brier difference against climatology at h = 1 (positive favours the candidate), first file in path order."""
    out = {}
    paths = sorted(glob.glob(str(Path(root) / EVIDENCE / "*" / "compare*.json"))
                   + glob.glob(str(Path(root) / EVIDENCE / "*" / "paired*.json")))
    for path in paths:
        doc = json.loads(Path(path).read_text())
        if not isinstance(doc, dict) or "brier" not in doc:
            continue
        rel = os.path.relpath(path, root)
        for name, horizons in doc["brier"].items():
            cells = (horizons or {}).get("1") or {}
            if name in out or not any("vs_climatology" in c for c in cells.values()):
                continue
            figures = {cell: group_figure(c["vs_climatology"]) for cell, c in sorted(cells.items())
                       if "vs_climatology" in c}
            out[name] = {"source": rel, "pooled": figures.get("all"),
                         "regime": {k[len("regime "):]: v for k, v in figures.items() if k.startswith("regime ")}}
    return out


def candidate_order(root):
    """Candidate file names in the order their files were added to the repository."""
    if subprocess.run(["git", "-C", str(root), "rev-parse", "--is-shallow-repository"],
                      capture_output=True, text=True, check=True).stdout.strip() != "false":
        raise SystemExit("emit_progress: shallow clone; run `git fetch --unshallow` first")
    log = subprocess.run(["git", "-C", str(root), "log", "--no-merges", "--diff-filter=A", "--name-only",
                          "--format=%x00%ct", "--", CANDIDATES], capture_output=True, text=True, check=True).stdout
    added = {}
    for block in log.split("\0")[1:]:
        stamp, *files = block.split("\n")
        for f in files:
            if f.endswith(".json"):
                added[Path(f).stem] = min(int(stamp), added.get(Path(f).stem, int(stamp)))
    present = sorted(Path(p).stem for p in glob.glob(str(Path(root) / CANDIDATES / "*.json")))
    return sorted(present, key=lambda n: (added.get(n, 0), n))


def declared_variants(decl):
    """The `variants` block of a declaration (top level, else under `model`), or None when it has none (#732)."""
    if not isinstance(decl, dict):
        return None
    block = decl.get("variants")
    if block is None and isinstance(decl.get("model"), dict):
        block = decl["model"].get("variants")
    return block if isinstance(block, (dict, list)) else None


def is_model_declaration(decl):
    """A model declaration has a `variants` block, or both `model` and `scoring` (#732)."""
    return isinstance(decl, dict) and (declared_variants(decl) is not None or ("model" in decl and "scoring" in decl))


ARM_KEYS = ("candidates", "arms")


def declared_arms(decl):
    """Arms a declaration names under `candidates` or `arms` (top level, else under `model`): their number, or 0 (#803)."""
    if not isinstance(decl, dict):
        return 0
    total = 0
    for key in ARM_KEYS:
        block = decl.get(key)
        if block is None and isinstance(decl.get("model"), dict):
            block = decl["model"].get(key)
        if isinstance(block, (dict, list)):
            total += len(block)
    return total


def is_scored_declaration(decl):
    """A `hypothesis`, `scoring` or `model` key marks a declaration, whether or not its arms can be counted (#803)."""
    return isinstance(decl, dict) and any(k in decl for k in ("hypothesis", "scoring", "model"))


def count_variants(root, order):
    """Count by content, not by file name, every `metadata/*.json` (#732, #803).

    `variants` blocks are counted as before. A file with no `variants` block that names its arms `candidates` or `arms`
    is counted apart (`arm_declarations`, `arms`), so the first figure keeps its meaning. A declaration whose arms
    cannot be read from either (a `hypothesis`, `scoring` or `model` key and no block) is listed in `unread`.
    """
    declarations = variants = arm_declarations = arms = 0
    unread = []
    for path in sorted(glob.glob(str(Path(root) / DECLARATIONS))):
        decl = json.loads(Path(path).read_text())
        block = declared_variants(decl)
        if block is not None:
            declarations += 1
            variants += len(block)
        elif declared_arms(decl):
            arm_declarations += 1
            arms += declared_arms(decl)
        elif is_scored_declaration(decl):
            unread.append(Path(path).name)
    return {"candidate_files": len(order), "declarations": declarations, "variants": variants,
            "arm_declarations": arm_declarations, "arms": arms, "unread": unread}


def build(root, order=None):
    root = Path(root)
    order = candidate_order(root) if order is None else list(order)
    spread, ordinary = read_spread(root), read_ordinary(root)
    calibration, tiers, brier = read_calibration(root), read_tiers(root), read_brier(root)
    rows, without = [], []
    for position, name in enumerate(order, 1):
        measured = [name in s for s in (spread, ordinary, calibration, tiers, brier)]
        if not any(measured):
            without.append(name)
            continue
        rows.append({"name": name, "position": position, "spread": spread.get(name),
                     "ordinary": ordinary.get(name), "brier": brier.get(name),
                     "calibration": calibration.get(name), "tiers": tiers.get(name)})
    count = count_variants(root, order)
    count["without_evidence"] = without
    return {
        "label": LABEL,
        "sources": SOURCES,
        "variant_count": count,
        "candidates": rows,
        "hypotheses": {"H5": {"label": LABEL, "target": "the SOFR - IORB spread distribution in bp",
                              "spread": {r["name"]: r["spread"] for r in rows if r["spread"]}}},
    }


def num(x, places=3, signed=False):
    if x is None:
        return NOT_MEASURED
    return format(x, "+.%df" % places if signed else ".%df" % places)


def with_interval(figure, places=3, signed=True):
    if not figure or figure.get("mean") is None:
        return NOT_MEASURED
    text = num(figure["mean"], places, signed)
    lo = figure.get("interval")
    return text + (" [%s, %s]" % (num(lo[0], places, signed), num(lo[1], places, signed)) if lo else " (no interval)")


def verdict(x):
    return NOT_MEASURED if x is None else ("yes" if x else "no")


def render(model):
    c = model["variant_count"]
    rows = model["candidates"]
    out = ["# Progress", "",
           "Generated by `scripts/emit_progress.py` from the committed evidence; never edited by hand. Nothing here is "
           "scored: every figure is copied from the file named for it, and a figure the evidence does not hold is "
           "printed as \"%s\". Every figure is %s (scoring protocol v1, #640): development days only, no hypothesis "
           "is decided by them. The judge's tiers are reported only; the +5 bp judge is retired as a decision rule." % (
               NOT_MEASURED, model["label"]), "",
           "Primary goal H5: the SOFR - IORB spread distribution in bp. Secondary goal H9: richer targets.", "",
           "## Variant count", "",
           "- Candidate files under `%s/`: %d." % (CANDIDATES, c["candidate_files"]),
           "- Declarations with a `variants` block (`%s`, by content): %d, declaring %d variants." % (
               DECLARATIONS, c["declarations"], c["variants"]),
           "- Files with no `variants` block that name their arms `candidates` or `arms` (by content): %d, naming %d arms. "
           "They are not added to the variants above: what counts as a variant under protocol section 2 is Eleonora's." % (
               c["arm_declarations"], c["arms"]),
           "- Declarations whose arms this count cannot read (%d): %s." % (
               len(c["unread"]), ", ".join("`%s`" % n for n in c["unread"]) or "none"),
           "- Candidates with evidence in this page: %d. Candidate files with no committed evidence this page reads: "
           "%d (listed at the end)." % (len(rows), len(c["without_evidence"])),
           "", "Position is the order in which the candidate file was added.", "",
           "## Spread forecast (H5, primary)", "",
           "CRPS in bp on the contract's levels, over the days the variant has a law (`%s`). The difference is "
           "as-of persistence minus the variant, as the evidence records it: positive favours the variant. 90%% "
           "intervals where the evidence has them; the MAE column is the same difference for the median forecast." % (
               SOURCES["spread"]), ""]
    spread_rows = [r for r in rows if r["spread"]]
    if not spread_rows:
        out += ["No spread forecast has committed evidence.", ""]
    for h in HORIZONS:
        cells = [(r, r["spread"][h]) for r in spread_rows if h in r["spread"]]
        if not cells:
            continue
        out += ["### h = %s" % h, "",
                "| # | candidate | days | CRPS | as-of persistence CRPS | CRPS difference [90%] | MAE difference [90%] |",
                "|---|---|---|---|---|---|---|"]
        for r, s in cells:
            d = s["crps_difference_vs_persistence"] or {}
            m = s["mae_median_difference_vs_persistence"] or {}
            out.append("| %d | %s | %s | %s | %s | %s | %s |" % (
                r["position"], r["name"], s["days"], num(s["crps_bps"]), num(s["crps_bps_as_of_persistence"]),
                with_interval(d.get("pooled")), with_interval(m.get("pooled"))))
        out.append("")
        regimes = sorted({k for _, s in cells for k in ((s["crps_difference_vs_persistence"] or {}).get("regime") or {})})
        if regimes:
            out += ["CRPS difference against as-of persistence by regime, h = %s:" % h, "",
                    "| candidate | " + " | ".join(regimes) + " |", "|---|" + "---|" * len(regimes)]
            for r, s in cells:
                reg = (s["crps_difference_vs_persistence"] or {}).get("regime") or {}
                out.append("| %s | %s |" % (r["name"], " | ".join(with_interval(reg.get(k)) for k in regimes)))
            out.append("")
    out += ["## Pressure (+5 bp), by candidate", "",
            "Ordinary-day AUROC from `%s` (pooled over leads 1 to 5, and at lead 1 with its 90%% interval). Brier "
            "difference against climatology at h = 1, climatology minus candidate, so positive favours the candidate "
            "(%s). Judge tiers 1, 3 and 5 from `%s`, reported only." % (
                SOURCES["ordinary"], SOURCES["brier"], SOURCES["tiers"]), "",
            "| # | candidate | ordinary-day AUROC, pooled | AUROC at lead 1 [90%] | Brier difference, h = 1 [90%] | tier 1 | tier 3 | tier 5 |",
            "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        o = r["ordinary"]
        t = r["tiers"] or {}
        lead = (o or {}).get("lead_1") or {}
        auroc = NOT_MEASURED if not o or lead.get("auroc") is None else with_interval(
            {"mean": lead["auroc"], "interval": lead.get("auroc_interval")}, signed=False)
        out.append("| %d | %s | %s | %s | %s | %s | %s | %s |" % (
            r["position"], r["name"], num((o or {}).get("pooled_auroc")), auroc,
            with_interval((r["brier"] or {}).get("pooled")),
            verdict(t.get("tier_1")), verdict(t.get("tier_3")), verdict(t.get("tier_5"))))
    out += [""]
    brier_rows = [r for r in rows if r["brier"] and r["brier"]["regime"]]
    regimes = sorted({k for r in brier_rows for k in r["brier"]["regime"]})
    out += ["## Brier difference against climatology by regime (h = 1, +5 bp)", ""]
    if brier_rows:
        out += ["| candidate | " + " | ".join(regimes) + " | source |", "|---|" + "---|" * len(regimes) + "---|"]
        for r in brier_rows:
            out.append("| %s | %s | `%s` |" % (r["name"], " | ".join(
                with_interval(r["brier"]["regime"].get(k)) for k in regimes), r["brier"]["source"]))
    else:
        out.append("No candidate has a committed Brier figure by regime.")
    out += ["", "## Calibration by regime (predicted against realised)", "",
            "Predicted and realised rate of a +5 bp pressure day, pooled over h = 1 to 5, from `%s`. The evidence "
            "records no interval for these cells." % SOURCES["calibration"], ""]
    cal_rows = [r for r in rows if r["calibration"]]
    cells = sorted({k for r in cal_rows for k in r["calibration"] if k.startswith("regime ")})
    if cal_rows:
        out += ["| candidate | " + " | ".join(k + " (predicted / realised)" for k in cells) + " |",
                "|---|" + "---|" * len(cells)]
        for r in cal_rows:
            out.append("| %s | %s |" % (r["name"], " | ".join(
                "%s / %s" % (num(r["calibration"][k]["predicted"]), num(r["calibration"][k]["realised"]))
                if k in r["calibration"] else NOT_MEASURED for k in cells)))
    else:
        out.append("No candidate has committed calibration figures.")
    out += ["", "## Candidate files with no committed evidence this page reads", ""]
    out += ["- `%s`" % n for n in c["without_evidence"]] or ["None."]
    out.append("")
    return "\n".join(out)


def outputs(root, order=None):
    model = build(root, order)
    return {PAGE: render(model), DATA: json.dumps(model, indent=1, sort_keys=True) + "\n"}


def write_outputs(root, order=None):
    for rel, text in outputs(root, order).items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def check(root, order=None):
    """Differences between the committed files and what the evidence produces; empty when current."""
    problems = []
    for rel, want in outputs(root, order).items():
        path = Path(root) / rel
        have = path.read_text() if path.is_file() else ""
        if have != want:
            problems.append("".join(list(difflib.unified_diff(have.splitlines(True), want.splitlines(True),
                                                              "committed " + rel, "generated " + rel))[:40]) or rel)
    return problems


def main(argv):
    if "--check" in argv:
        problems = check(ROOT)
        if problems:
            print("emit_progress: stale; run `python3 scripts/emit_progress.py` and commit the result.\n")
            print("\n".join(problems))
            return 1
        return 0
    write_outputs(ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
