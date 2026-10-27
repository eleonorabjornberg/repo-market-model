#!/usr/bin/env python3
"""H1 step 2 (#967), re-read in the ruled orientation (#1013, finding #1000): calibrate on the series the paths use.

#999 built its paths on `e` = S(B1) - S(B2) but calibrated the critical values on `-e` (`scaled_score_967.calibrate`).
Eleonora's ruling of 19 October 2026 on #913 puts each leg in its own orientation, so the calibration series must be the path
series. `calibrate` now does that. This script re-runs #999's study unchanged otherwise: the declaration
`metadata/scaled_score_967.json` (its text and its sha256), the scale, the six designs and the companions, the generator, the
seeds, the paths and the windows. It then reports, side by side with #999's page (which stands, unedited):

- the contiguous and the stationary-10 critical values, size and power of every design, in the ruled orientation and as #999
  recorded them;
- a row check: D0 and D4 calibrated on `-e` again, to show that this script reproduces #999's figures under the old
  orientation.

It changes no constant and decides nothing: whether the primary score changes is Eleonora's section 13 question.

    (panel and the five `gbm_funding` walks as in `scripts/scaled_score_967.py`)
    PYTHONPATH=src python3 scripts/scaled_score_1013.py run --published PUB.csv --walks OUT --output OUT/result.json --workers 4
    python3 scripts/scaled_score_1013.py report OUT/result.json
    python3 scripts/scaled_score_1013.py check

Standard library only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
from pathlib import Path
from typing import Dict

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402


def _study():
    spec = importlib.util.spec_from_file_location("scaled_score_967", REPO / "scripts" / "scaled_score_967.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["scaled_score_967"] = module
    spec.loader.exec_module(module)
    return module


base = _study()

RECORD = base.RESEARCH / "scaled-score-1013" / "result.json"
PAGE = base.RESEARCH / "scaled-score-1013-result.md"
PREVIOUS = base.RECORD  # #999's record, which stands
ROW_CHECK = ("D0", "D4")
FIGURES = ("size", "power_3", "power_10")
TOLERANCE = 1e-12


def run_command(args) -> int:
    base.committed_declaration()
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    manifest = json.loads(base.PANEL_MANIFEST.read_text(encoding="utf-8"))
    digest = base.sha256(args.published)
    if digest != manifest.get("sha256", digest):
        raise ValueError("the panel is not the published one")
    splits = load_split_declaration(base.SPLITS_PATH)
    registry = json.loads(base.SOURCES.read_text(encoding="utf-8"))
    pool = base.build_pool(rows, splits, registry)
    scales = base.trailing_scales(pool.decisions, pool.targets, pool.kinds, pool.s2)
    trap_scales = base.trailing_scales(pool.decisions, pool.targets, pool.kinds, pool.t2)
    series = {d.id: base.design_series(pool, d, scales, trap_scales) for d in base.DESIGNS}
    histories = {d.id: (series[d.id][1], series[d.id][2]) for d in base.DESIGNS}
    row_designs = [base.DESIGN_BY_ID[i] for i in ROW_CHECK]
    with multiprocessing.Pool(max(1, args.workers)) as workers:
        calibrated = dict(workers.map(base.calibrate, [(d, histories[d.id][1], args.windows) for d in base.DESIGNS]))
        previous = dict(workers.map(base.calibrate, [(d, histories[d.id][1], args.windows, -1.0) for d in row_designs]))
    critical = {k: v["critical"] for k, v in calibrated.items()}
    scenarios = base.simulate(histories, critical, base.DESIGNS, paths=args.paths, workers=args.workers)
    rows_ = base.design_rows(scenarios)
    print("row check: the old orientation", flush=True)
    old_critical = {d.id: previous[d.id]["critical"] for d in row_designs}
    old_scenarios = base.simulate(histories, old_critical, row_designs, paths=args.paths, workers=args.workers)
    old_rows = _rows_for(old_scenarios, row_designs)
    record: Dict[str, object] = {
        "declaration_sha256": base.sha256(base.DECLARATION), "panel_sha256": digest, "study_end": base.STUDY_END.isoformat(),
        "calibration_series": "e = S(B1) - S(B2), the series the paths are built on (#1013)",
        "constants": {"windows": args.windows, "paths": args.paths, "seed": base.SEED, "calibration_seed": base.CALIBRATION_SEED,
                      "mme": base.MME, "trailing": base.TRAILING, "scale_lag": base.SCALE_LAG, "minimum_cells": base.MIN_CELLS,
                      "size_limit": base.SIZE_LIMIT, "power_floor": base.POWER_FLOOR},
        "pool": {"first": pool.decisions[0].isoformat(), "last": pool.decisions[-1].isoformat(), "days": len(pool.decisions),
                 "first_scaled": next(d for d, s in zip(pool.decisions, scales) if s is not None).isoformat(),
                 "post_2020_days": sum(1 for d in pool.decisions if d >= base.POST_2020_FIRST)},
        "designs": {d.id: {"days": d.days, "leads": list(d.leads), "scale": d.scale, "score": d.score,
                           **calibrated[d.id], "post_2020": rows_[d.id]} for d in base.DESIGNS},
        "scenarios": scenarios,
        "previous_orientation": {d.id: {**previous[d.id], "post_2020": old_rows[d.id]} for d in row_designs},
    }
    record["kill_scale_buys_nothing"] = base.kill_scale_buys_nothing(record)
    record["regimes"] = base.regime_split(args.published, args.walks, pool, scales, splits)
    record["misranking"] = base.misranking(record["regimes"]["by_regime"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "kill": record["kill_scale_buys_nothing"]["fires"],
                      "misranking": record["misranking"]["holds"]}))
    return 0


def _rows_for(scenarios, designs):
    """`base.design_rows` for a subset of designs."""

    saved = base.DESIGNS
    base.DESIGNS = tuple(designs)
    try:
        return base.design_rows(scenarios)
    finally:
        base.DESIGNS = saved


def row_check(record, previous) -> Dict[str, object]:
    """Whether the old orientation, re-run here, gives #999's figures for D0 and D4 (same seeds, same paths)."""

    out, matches = {}, True
    for design in ROW_CHECK:
        got = record["previous_orientation"][design]["post_2020"]
        then = previous["designs"][design]["post_2020"]
        same = all(abs(got[k] - then[k]) <= TOLERANCE for k in FIGURES) and \
            record["previous_orientation"][design]["critical"] == previous["designs"][design]["critical"]
        out[design] = {"reproduces": same, "figures": {k: [then[k], got[k]] for k in FIGURES}}
        matches = matches and same
    return {"all_reproduce": matches, "designs": out}


def render(record, previous) -> str:
    text = base.render(record)
    head = "# A scale-free primary score: size, power and the regime ranking (#967, H1 step 2 and H5)"
    if not text.startswith(head):
        raise ValueError("the #967 page has changed shape")
    text = text.replace(head, "# A scale-free primary score, calibrated on the series the paths use (#1013, H1 step 2 and H5)", 1)
    text = text.replace("on S(B2) - S(B1) alone", "on e = S(B1) - S(B2) alone, the series the paths are built on", 1)
    text = text.replace("`docs/research/scaled-score-967/result.json` by `scripts/scaled_score_967.py report`",
                        "`docs/research/scaled-score-1013/result.json` by `scripts/scaled_score_1013.py report`", 1)
    c = base.pct
    L = ["", "## Against #999 (calibrated on -e)", "",
         "#999 (`docs/research/scaled-score-967-result.md`, which stands) built its paths on `e` = S(B1) - S(B2) and calibrated on "
         "`-e` (finding #1000). This page calibrates on `e`, as the ruling of 19 October 2026 on #913 puts each leg in its own "
         "orientation. Contiguous critical values at the last two looks and the gated figures, #999 then this page. Nothing else "
         "differs: the declaration, scale, generator, seeds, paths and windows are #999's.", "",
         "| design | c at look 2 / 3, #999 | c at look 2 / 3, here | stationary-10, #999 | stationary-10, here | size, #999 | size, here "
         "| power at 10%, #999 | power at 10%, here |",
         "|---|---|---|---|---|---|---|---|---|"]
    for d in base.DESIGNS:
        was, now = previous["designs"][d.id], record["designs"][d.id]
        looks = now["checkpoints"]

        def pair(info, key):
            return f"{info[key][str(looks[1])]:.2f} / {info[key][str(looks[2])]:.2f}"

        L.append(f"| {d.id} | {pair(was, 'critical')} | {pair(now, 'critical')} | {pair(was, 'critical_stationary')} | "
                 f"{pair(now, 'critical_stationary')} | {c(was['post_2020']['size'])} | {c(now['post_2020']['size'])} | "
                 f"{c(was['post_2020']['power_10'])} | {c(now['post_2020']['power_10'])} |")
    check = row_check(record, previous)
    L += ["", "### Row check: this script under the old orientation", "",
          "D0 and D4 calibrated on `-e` again, same seeds and paths. The row check "
          f"{'passes: both reproduce #999 exactly' if check['all_reproduce'] else 'FAILS: the re-run does not reproduce #999'}.", "",
          "| design | figure | #999 | re-run on -e |", "|---|---|---|---|"]
    for design, info in check["designs"].items():
        for k, (then, got) in info["figures"].items():
            L.append(f"| {design} | {k} | {c(then)} | {c(got)} |")
    prev_kill = previous["kill_scale_buys_nothing"]
    kill = record["kill_scale_buys_nothing"]
    L += ["", "### Declared readings, #999 then here", "",
          f"- The scale buys nothing: #999 {'fires' if prev_kill['fires'] else 'does not fire'} (D4 power at 10% "
          f"{c(prev_kill['power_10'])}, size {c(prev_kill['size'])}); here {'fires' if kill['fires'] else 'does not fire'} (D4 power at "
          f"10% {c(kill['power_10'])}, size {c(kill['size'])}).",
          f"- The misranking demonstration: #999 {'holds' if previous['misranking']['holds'] else 'fails'}; here "
          f"{'holds' if record['misranking']['holds'] else 'fails'}. The regime split uses no critical value, so it is #999's.", ""]
    marker = "## Limits"
    if marker not in text:
        raise ValueError("the #967 page has changed shape")
    return text.replace(marker, "\n".join(L[1:]) + "\n\n" + marker, 1)


def report_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(record, previous), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args) -> int:
    if not RECORD.exists():
        print("no record yet: `run` and `report` have not been run", file=sys.stderr)
        return 1
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    if record["declaration_sha256"] != base.sha256(base.DECLARATION):
        print("the record was made under another text of the declaration", file=sys.stderr)
        return 1
    if record["pool"]["last"] > base.STUDY_END.isoformat():
        print("the study scored a day after its end", file=sys.stderr)
        return 1
    if not row_check(record, previous)["all_reproduce"]:
        print("the row check does not reproduce #999", file=sys.stderr)
        return 1
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(record, previous):
        print("the page is not what the record gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


from repo_model import turn_days  # noqa: E402


@turn_days.with_legacy_flag
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--walks", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--workers", type=int, default=4)
    run.add_argument("--paths", type=int, default=base.PATHS)
    run.add_argument("--windows", type=int, default=base.WINDOWS)
    run.set_defaults(func=run_command)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
