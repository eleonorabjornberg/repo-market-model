#!/usr/bin/env python3
"""Do the #243 band candidates that met its test hold on 2026? (#408)

#393 reported five candidates meeting the #243 test on 2018-06-29 to 2025-12-31. Eleonora's ruling of
8 October 2026 on #393: nothing is published until they are confirmed on 2026-01-01 to 2026-09-03 under the
same test. That window is ordinary history since the lockbox amendment of #151 (`docs/decisions/lockbox.md`).

The window and the candidates are declared in `docs/declarations/interior_confirmation_408.json`, committed
before any candidate was scored on 2026; this script reads it, records its sha256 and the two #243 files',
and refuses a candidate it does not list. The candidates, the test and the bootstrap are
`scripts/interior_calibration_judge.py`'s, unchanged: every candidate is an online layer over the published
distribution's issued vectors, so its state runs from 2018-06-29 as under #243 and only the 2026 days are scored.

    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/interior_confirmation_408.py score --panel PUB.csv
    PYTHONPATH=src python3 scripts/interior_confirmation_408.py render
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import statistics
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, onset  # noqa: E402
from repo_model.baseline import _split_labels, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import DAY_TYPES, load_split_declaration  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = REPO / "docs" / "declarations" / "interior_confirmation_408.json"
DEVELOPMENT = REPO / "docs" / "runs" / "interior_calibration_243.json"
OUTPUT = REPO / "docs" / "runs" / "interior_confirmation_408.json"
PAGE = REPO / "docs" / "interior_confirmation_408.md"
WINDOW = (date(2026, 1, 1), date(2026, 9, 3))


def _load_judge():
    spec = importlib.util.spec_from_file_location(
        "judge_interior_calibration", REPO / "scripts" / "interior_calibration_judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


judge = _load_judge()


def declaration() -> dict:
    return json.loads(DECLARATION.read_text(encoding="utf-8"))


def declared_candidates() -> list:
    return list(declaration()["candidates"])


def require_declared(name: str) -> None:
    """Refuse a candidate the #408 declaration does not list."""

    if name not in declared_candidates():
        raise ValueError(f"candidate {name!r} is not in the declaration {DECLARATION.name}")


def check_scored(dates) -> None:
    """Refuse to score a day outside 2026-01-01 to 2026-09-03; a day in a tier not opened is refused too."""

    days = [date.fromisoformat(d) if isinstance(d, str) else d for d in dates]
    first, last = min(days), max(days)
    if first < WINDOW[0] or last > WINDOW[1]:
        raise LookAheadError(f"{first}..{last} is outside the declared window {WINDOW[0]}..{WINDOW[1]}")
    lockbox.require_unlocked([last], where="interior_confirmation_408")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    manifest = json.loads(judge.MANIFEST.read_text(encoding="utf-8"))
    if panel_sha256(args.panel) != manifest["sha256"]:
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(judge.SPLITS)
    with open(args.panel, newline="", encoding="utf-8") as handle:
        tag_rows = {r["date"]: r for r in csv.DictReader(handle)}

    # The history runs to the window's last day so the online state is #243's; the guard below refuses more.
    judge.WINDOW = (judge.WINDOW[0], WINDOW[1])
    full = judge.load_days(rows, splits, tag_rows)
    keep = [k for k, d in enumerate(full) if d["date"] >= WINDOW[0].isoformat()]
    days = [full[k] for k in keep]
    check_scored([d["date"] for d in days])
    check_scored([full[-1]["date"]])
    dates = [date.fromisoformat(d["date"]) for d in days]
    regimes, types = _split_labels(splits, rows, dates)
    regime_names = [r for r in splits.regime_labels if r in set(regimes)]

    groups = {}
    for r in regime_names:
        groups["regime:" + r] = [x == r for x in regimes]
    for t in judge.TAGS:
        groups["tag:" + t] = [t in d["tags"] for d in days]
    groups["tag:other"] = [not d["tags"] for d in days]
    for t in DAY_TYPES:
        groups["reporting:" + t] = [x == t for x in types]
    names = list(groups)
    masks = [[True] * len(days)] + [groups[n] for n in names]

    published = [d["issued"] for d in days]
    pub_loss = [judge._crps(v, d["y"]) for v, d in zip(published, days)]

    def by_group(vectors):
        out = {"all": judge.coverage(days, vectors)}
        for n in names:
            members = [i for i, m in enumerate(groups[n]) if m]
            if members:
                out[n] = judge.coverage([days[i] for i in members], [vectors[i] for i in members])
        return out

    record = {
        "directive": "#408",
        "record": "2026 confirmation of the #243 band candidates against the published distribution (h = 1)",
        "declaration": str(DECLARATION.relative_to(REPO)),
        "declaration_sha256": _sha(DECLARATION),
        "test_files": {str(p.relative_to(REPO)): _sha(p) for p in (judge.DECLARATION, judge.ADDENDUM)},
        "panel_sha256": panel_sha256(args.panel),
        "window": {"first": days[0]["date"], "last": days[-1]["date"], "days": len(days)},
        "sign_convention": judge.SIGN,
        "bootstrap": {"block_length": judge.BLOCK_LENGTH, "replications": judge.REPLICATIONS, "level": judge.LEVEL},
        "published": {"crps_bps": statistics.fmean(pub_loss), "coverage_by_group": by_group(published)},
        "candidates": {},
    }
    for name in declared_candidates():
        require_declared(name)
        vectors = judge.candidate_vectors(name, full)
        vectors = [vectors[k] for k in keep]
        for v in vectors:
            if any(a > b for a, b in zip(v, v[1:])):
                raise ValueError(f"{name} issued a crossing vector")
        loss = [judge._crps(v, d["y"]) for v, d in zip(vectors, days)]
        gain = [a - b for a, b in zip(pub_loss, loss)]
        cells = judge.cell_intervals(gain, masks, onset._seed("#408", "gain", name))
        pooled, rest = cells[0], dict(zip(names, cells[1:]))
        record["candidates"][name] = {
            "crps_bps": statistics.fmean(loss),
            "pooled_gain": pooled,
            "gain_by_group": rest,
            "coverage_by_group": by_group(vectors),
            "test": judge.verdict(pooled, rest),
        }
    development = json.loads(DEVELOPMENT.read_text(encoding="utf-8"))
    record["holds_on_both"] = [n for n, c in record["candidates"].items()
                               if c["test"]["met"] and development["candidates"][n]["test"]["met"]]
    record["outcome"] = (
        "meeting the declared test on 2026 as well as on 2018-2025: %s. Whether and which joins the published "
        "declaration is Eleonora's; this record changes no published figure" % ", ".join(record["holds_on_both"])
        if record["holds_on_both"] else
        "no candidate meets the declared test on both windows: report only, the published declaration is unchanged")
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _cov(cell, band):
    return "%.1f%% (%.1f / %.1f)" % (cell[band], cell[band + "_miss_below"], cell[band + "_miss_above"])


def render(record, development) -> str:
    """The results page, from the two records alone."""

    names = list(record["candidates"])
    lines = ["# Confirming the interior-band candidates on 2026 (#408)", "",
             "<!-- generated: interior-confirmation -->", "",
             "**Generated by `scripts/interior_confirmation_408.py render` from `docs/runs/interior_confirmation_408.json` "
             "and `docs/runs/interior_calibration_243.json`; never hand-edited.** Reported only: the published declaration "
             "is unchanged.", "",
             "The five candidates that met the #243 test on 2018-06-29 to 2025-12-31 (#393), scored on %d days, %s to %s, "
             "under the same test, declared in `%s` (sha256 `%s`) before they were scored. Gain is CRPS(published) - "
             "CRPS(candidate) per day in bp, so a positive mean favours the candidate; intervals are 90%% stationary "
             "bootstraps (block length 2). Coverage cells: coverage %%, with the share of days below / above the band." % (
                 record["window"]["days"], record["window"]["first"], record["window"]["last"],
                 record["declaration"], record["declaration_sha256"][:12]), "",
             "## The declared test, development beside 2026", "",
             "| Candidate | 2018-2025 CRPS | 2018-2025 pooled gain | 2018-2025 test | 2026 CRPS | 2026 pooled gain | 2026 cells worse | 2026 test | Holds on both |",
             "|---|---|---|---|---|---|---|---|---|",
             "| published | %.3f | | | %.3f | | | | |" % (development["published"]["crps_bps"], record["published"]["crps_bps"])]
    for n in names:
        c, d = record["candidates"][n], development["candidates"][n]
        lines.append("| %s | %.3f | %s | %s | %.3f | %s | %s | %s | %s |" % (
            n, d["crps_bps"], judge._gain(d["pooled_gain"]), "met" if d["test"]["met"] else "not met",
            c["crps_bps"], judge._gain(c["pooled_gain"]), ", ".join(c["test"]["worse_cells"]) or "none",
            "met" if c["test"]["met"] else "not met", "**yes**" if n in record["holds_on_both"] else "no"))
    lines += ["", "Candidates " + record["outcome"] + ".", "", "## Gain by regime and by day type (2026)", "",
              "| Group | days | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    for group, cell in record["candidates"][names[0]]["gain_by_group"].items():
        lines.append("| %s | %d | %s |" % (group, cell["days"], " | ".join(
            judge._gain(record["candidates"][n]["gain_by_group"][group]) for n in names)))
    sets = [("published", record["published"])] + list(record["candidates"].items())
    for band, label in (("band_50", "50% band"), ("band_90", "90% band")):
        lines += ["", "## Coverage of the %s by group (2026)" % label, "",
                  "A group of under 20 days is too few to read.", "",
                  "| Group | days | " + " | ".join(n for n, _ in sets) + " |", "|---|---|" + "---|" * len(sets)]
        for group, cell in record["published"]["coverage_by_group"].items():
            lines.append("| %s | %d | %s |" % (group, cell["days"], " | ".join(
                _cov(s["coverage_by_group"][group], band) for _, s in sets)))
        dev_sets = [("published", development["published"])] + [(n, development["candidates"][n]) for n in names]
        lines += ["", "The same cells on 2018-2025 (#243), for the day types #393 named:", "",
                  "| Group | " + " | ".join(n for n, _ in dev_sets) + " |", "|---|" + "---|" * len(dev_sets)]
        for group in ("all", "reporting:quarter_end", "tag:coupon_settlement"):
            lines.append("| %s | %s |" % (group, " | ".join(_cov(s["coverage_by_group"][group], band) for _, s in dev_sets)))
    lines += ["", "<!-- end generated: interior-confirmation -->", ""]
    return "\n".join(lines)


def render_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    development = json.loads(DEVELOPMENT.read_text(encoding="utf-8"))
    args.output.write_text(render(record, development), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score")
    score.add_argument("--panel", type=Path, required=True)
    score.add_argument("--output", type=Path, default=OUTPUT)
    score.set_defaults(func=score_command)
    page = sub.add_parser("render")
    page.add_argument("--record", type=Path, default=OUTPUT)
    page.add_argument("--output", type=Path, default=PAGE)
    page.set_defaults(func=render_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
