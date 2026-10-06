"""Pressure model v2's distribution at h = 1, scored against v1 and as-of persistence (#244).

v2 is the fix #247 recommends, built in `repo_model.interior`: v1's trees and
nested conformal PID, unchanged, with each interior level (q25, q50, q75)
moved by its own online quantile tracker. Nothing in v1 changes: its walk is
the final test's (`final_test_opening.distribution_walk` with
`live_record._compare_sides(1)`), and v2's calibration runs v1's nested PID
first and keeps its vector beside v2's.

The bar (`BAR`, from #244) and the 2026 gate (`GATE`, from Eleonora's scoping
ruling on #244) are declared here before anything is scored.

* The bar is read on 2018-06-29 to 2025-12-31.
* The gate is read on 2026-01-02 to 2026-09-03, the opened near-blind window.
  Those days motivated the fix (#243), so they are seen data, not evidence.
* v2 has no other choice to make. Its only setting, the tracking step, is
  chosen online, by nested walk-forward selection at each 21-day refit block
  from labels observable at that block's anchor.
* No day after 2026-09-03 is read.

Two subcommands:

* `walk`: the published side's walk with v2's calibration. Each scored day
  keeps its anchor, its outcome, v1's vector and v2's.
* `assemble`: the record, `docs/runs/pressure_model_v2_distribution_h1.json`.
  It first checks that v1's vectors are #247's to the byte
  (`v1_interior_diagnosis.json`), that they reproduce the published h = 1 CRPS
  records exactly, and that v2's vectors are #247's reference implementation
  applied to them.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_model_v2.py walk \\
        --panel PUB.csv --horizon H --output OUT/v2_hH.json
    PYTHONPATH=src python3 scripts/pressure_model_v2.py assemble --panel PUB.csv \\
        --walks OUT/v2_h*.json --output docs/runs/pressure_model_v2_distribution_h1.json
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import statistics
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import interior, onset  # noqa: E402
from repo_model.baseline import panel_sha256, split_document  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(f"v2_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dx = _script("interior_diagnosis")
fto = dx.fto
fp = dx.fp

LEVELS = dx.LEVELS
DECIDES = dx.DIAGNOSIS  # 2018-06-29 to 2025-12-31
CHECK = dx.OPENED  # 2026-01-02 to 2026-09-03
LAST_READ = dx.LAST_READ
BLOCK_LENGTH = fp.CRPS_BLOCK_LENGTH
RECORD = REPO / "docs" / "runs" / "pressure_model_v2_distribution_h1.json"
DIAGNOSIS_RECORD = dx.RECORD
CRPS_RECORD = REPO / "docs" / "runs" / "compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
FINAL_RECORD = REPO / "docs" / "runs" / "final_test_near_blind.json"
CHECK_LABEL = ("2026 check: seen data, not evidence. This window motivated the fix (#243); "
               "only v2's live record is evidence for v2")
SIGN = "paired = CRPS(benchmark) - CRPS(v2) per day; a positive mean favours v2"

# ---------------------------------------------------------------------------
# Declared before anything is scored.
# ---------------------------------------------------------------------------

#: #244, "What this stage must show". Coverage counts an outcome on a band
#: edge as half inside (`band_*_half_edge`), the measure #247's rule used.
BAR = {
    "window": "2018-06-29 to 2025-12-31, h = 1",
    "band_50_half_edge": [45.0, 55.0],
    "band_90_half_edge": [87.0, 93.0],
    "crps_vs_v1": ("paired CRPS(v1) - CRPS(v2): the 90% interval's upper bound is not below 0 "
                   "(v2 is no worse than v1)"),
    "band_90_reading": ("'stays calibrated' is read as #247's bar for the 90% band: 87-93% "
                        "counting an edge as half inside"),
}

#: Eleonora's scoping ruling on #244 (6 October 2026), with the gate the
#: orchestrating session proposed; the coverage measure is the half-inside count.
GATE = {
    "window": "2026-01-02 to 2026-09-03, h = 1, run once, frozen",
    "coverage": "half-inside: an outcome exactly on a band edge counts one half",
    "band_50": "the 90% interval on the 50% band's coverage includes 50%",
    "band_90": "the 90% interval on the 90% band's coverage includes 90%",
    "crps_vs_v1": "paired CRPS(v1) - CRPS(v2): the 90% interval's upper bound is not below 0",
    "interval": "stationary bootstrap, mean block length 2, as the final test",
}


def bar_verdict(coverage: dict, paired_vs_v1: dict) -> dict:
    """Whether each item of `BAR` holds."""

    low50, high50 = BAR["band_50_half_edge"]
    low90, high90 = BAR["band_90_half_edge"]
    return {
        "band_50": low50 <= coverage["band_50_half_edge"] <= high50,
        "band_90": low90 <= coverage["band_90_half_edge"] <= high90,
        "crps_no_worse": paired_vs_v1["interval"]["upper"] >= 0.0,
    }


def gate_verdict(coverage_interval: dict, paired_vs_v1: dict) -> dict:
    """Whether each item of `GATE` holds."""

    band50, band90 = coverage_interval["band_50"], coverage_interval["band_90"]
    return {
        "band_50_interval_includes_50": band50["lower"] <= 50.0 <= band50["upper"],
        "band_90_interval_includes_90": band90["lower"] <= 90.0 <= band90["upper"],
        "crps_not_worse_than_v1": paired_vs_v1["interval"]["upper"] >= 0.0,
    }


def vectors_sha256(rows) -> str:
    """The SHA-256 of `[[date, vector], ...]` as compact JSON: a byte-level fingerprint."""

    text = json.dumps([[day, [float(v) for v in vector]] for day, vector in rows], separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# The walk
# ---------------------------------------------------------------------------


def _plain(value):
    """A read-only mapping or a tuple in a declaration, as JSON writes it."""

    return dict(value) if hasattr(value, "keys") else list(value)


def walk_command(args) -> int:
    from repo_model.evaluation_splits import load_split_declaration as load_splits

    h = args.horizon
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    if rows[-1].date > LAST_READ:
        raise ValueError(f"the panel runs past {LAST_READ}")
    lr = fto._script("live_record")
    fto.live_record = lr
    registry = json.loads(fp.REGISTRY.read_text())
    sides, parsed = lr._compare_sides(h)
    name, fit, features, _v1_online = sides["published"]
    built = []

    def v2_online(rows_, rule):
        calibration = interior.NestedInteriorFoldPid(
            rows_, rule, splits=load_splits(fp.SPLITS), refit_every=parsed.refit_every)
        built.append(calibration)
        return calibration

    walk, levels, settings = fto.distribution_walk(
        rows, fit=fit, features=features, online_calibration=v2_online,
        registry=registry, horizon=h, minimum_history=parsed.minimum_history,
        refit_every=parsed.refit_every,
    )
    if tuple(levels) != LEVELS:
        raise ValueError(f"levels {levels}")
    (calibration,) = built
    issued = {d.index: d for d in calibration.issued_days}
    days = []
    for index, vector in walk:
        d = issued[index]
        if list(d.vector) != vector:
            raise ValueError(f"{rows[index].date}: the walk read another vector than v2 issued")
        days.append({"date": rows[index].date.isoformat(), "anchor": d.anchor.isoformat(),
                     "y": rows[index].spread_bps, "v1": list(d.pid), "v2": list(d.vector)})
    document = {"directive": "#244", "horizon": h, "panel_sha256": panel_sha256(args.panel),
                "model": name, "settings": settings,
                "interior_blocks": calibration.account()["interior_blocks"], "days": days}
    args.output.write_text(json.dumps(document, sort_keys=True, default=_plain) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": h, "days": len(days)}))
    return 0


# ---------------------------------------------------------------------------
# Measures
# ---------------------------------------------------------------------------


def _tied(a, b):
    return abs(a - b) <= interior.TIE_BPS


def band_coverage(days, field) -> dict:
    """The 50% and 90% bands' coverage, misses below and above, edge ties, and mean widths (percent, bp)."""

    n = len(days)
    out = {"days": n}
    for name, (lo, hi) in (("band_50", (1, 3)), ("band_90", (0, 4))):
        below = above = edge = 0
        for d in days:
            v, y = d[field], d["y"]
            if _tied(y, v[lo]) or _tied(y, v[hi]):
                edge += 1
            elif y < v[lo]:
                below += 1
            elif y > v[hi]:
                above += 1
        out[f"{name}_half_edge"] = 100.0 * (n - below - above - 0.5 * edge) / n
        out[f"{name}_closed"] = 100.0 * (n - below - above) / n
        out[f"{name}_miss_below"] = 100.0 * below / n
        out[f"{name}_miss_above"] = 100.0 * above / n
        out[f"{name}_on_an_edge"] = 100.0 * edge / n
        out[f"{name}_mean_width_bps"] = statistics.fmean(d[field][hi] - d[field][lo] for d in days)
    out["coverage_half_tie"] = {
        str(level): 100.0 * sum(interior.below_half_tie(d["y"], d[field][i]) for d in days) / n
        for i, level in enumerate(LEVELS)
    }
    return out


def _inside_half(d, field, lo, hi):
    v, y = d[field], d["y"]
    if _tied(y, v[lo]) or _tied(y, v[hi]):
        return 0.5
    return 1.0 if v[lo] < y < v[hi] else 0.0


def coverage_interval(days, field, seed_parts) -> dict:
    """Each band's half-inside coverage with a 90% stationary-bootstrap interval (percent)."""

    out = {}
    positions = list(range(len(days)))
    for name, (lo, hi) in (("band_50", (1, 3)), ("band_90", (0, 4))):
        hits = [100.0 * _inside_half(d, field, lo, hi) for d in days]
        cell = onset.paired_difference(hits, [0.0] * len(hits), positions, block_length=BLOCK_LENGTH,
                                       seed=onset._seed("#244", "coverage", name, *seed_parts))
        out[name] = {"coverage": cell["mean"], "lower": cell["interval"]["lower"],
                     "upper": cell["interval"]["upper"], "interval": cell["interval"]}
    return out


def median_error(days, field) -> dict:
    """The median forecast's absolute error against the actual spread."""

    errors = sorted(abs(d["y"] - d[field][2]) for d in days)
    return {
        "mean_bps": statistics.fmean(errors),
        "median_bps": statistics.median(errors),
        "share_within_1bp": 100.0 * sum(1 for e in errors if e <= 1.0 + interior.TIE_BPS) / len(errors),
        "share_within_2bp": 100.0 * sum(1 for e in errors if e <= 2.0 + interior.TIE_BPS) / len(errors),
    }


def persistence_losses() -> dict:
    """As-of persistence's per-day CRPS at h = 1, from the two published records."""

    published = json.loads(CRPS_RECORD.read_text(encoding="utf-8"))
    final = json.loads(FINAL_RECORD.read_text(encoding="utf-8"))
    out = {e["scored_date"]: e["loss_a_bps"] for e in published["comparison"]["per_origin"]}
    out.update({e["scored_date"]: e["loss_a_bps"] for e in final["primary"]["window_per_origin"]})
    return out


def paired_against(days, benchmark, rows, splits, label) -> dict:
    """CRPS(benchmark) - CRPS(v2) over `days`, paired, with a 90% interval and splits."""

    v2_losses = [crps_from_quantiles(LEVELS, d["v2"], d["y"]) for d in days]
    positions = list(range(len(days)))
    seed = onset._seed("#244", label)
    out = onset.paired_difference(benchmark, v2_losses, positions, block_length=BLOCK_LENGTH, seed=seed)
    out["crps_benchmark_bps"] = statistics.fmean(benchmark)
    out["crps_v2_bps"] = statistics.fmean(v2_losses)
    out["splits"] = split_document(splits, rows, [date.fromisoformat(d["date"]) for d in days],
                                   [b - m for b, m in zip(benchmark, v2_losses)],
                                   block_length=BLOCK_LENGTH, seed=seed)
    out["sign_convention"] = SIGN
    return out


def _split_coverage(days, rows, splits) -> dict:
    from repo_model.baseline import _split_labels

    scored = [date.fromisoformat(d["date"]) for d in days]
    regimes, types = _split_labels(splits, rows, scored)
    out = {"by_regime": {}, "by_day_type": {}}
    for key, labels in (("by_regime", regimes), ("by_day_type", types)):
        for label in sorted(set(labels)):
            subset = [d for d, lab in zip(days, labels) if lab == label]
            out[key][label] = {"v2": band_coverage(subset, "v2"), "v1": band_coverage(subset, "v1")}
    return out


def window_block(days, rows, splits, persistence, label) -> dict:
    v1_losses = [crps_from_quantiles(LEVELS, d["v1"], d["y"]) for d in days]
    return {
        "days": len(days),
        "first": days[0]["date"],
        "last": days[-1]["date"],
        "crps": {
            "v2_bps": statistics.fmean(crps_from_quantiles(LEVELS, d["v2"], d["y"]) for d in days),
            "v1_bps": statistics.fmean(v1_losses),
            "persistence_bps": statistics.fmean(persistence[d["date"]] for d in days),
            "v2_vs_v1": paired_against(days, v1_losses, rows, splits, f"{label}-v1"),
            "v2_vs_persistence": paired_against(days, [persistence[d["date"]] for d in days], rows, splits,
                                                f"{label}-persistence"),
        },
        "coverage": band_coverage(days, "v2"),
        "coverage_v1": band_coverage(days, "v1"),
        "coverage_splits": _split_coverage(days, rows, splits),
        "median_abs_error": {"v2": median_error(days, "v2"), "v1": median_error(days, "v1")},
    }


def _in(day, window):
    return window[0] <= date.fromisoformat(day) <= window[1]


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def assemble_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(fp.SPLITS)
    walks = {}
    for path in args.walks:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["panel_sha256"] != panel_sha256(args.panel):
            raise ValueError(f"{path} was walked on another panel")
        if max(d["date"] for d in document["days"]) > LAST_READ.isoformat():
            raise ValueError(f"{path} reads a day after {LAST_READ}")
        walks[document["horizon"]] = document
    days = walks[1]["days"]

    # v1 untouched: #247's vectors to the byte, and the published CRPS exactly.
    diagnosis = json.loads(DIAGNOSIS_RECORD.read_text(encoding="utf-8"))
    before = [[day, vector] for day, _y, vector in diagnosis["v1_h1_per_day"]]
    ours = [[d["date"], d["v1"]] for d in days]
    if vectors_sha256(ours) != vectors_sha256(before):
        raise ValueError("v1's vectors differ from #247's walk")
    dx.reproduction_check([{"date": d["date"], "y": d["y"], "issued": d["v1"]} for d in days])

    # v2 is #247's reference implementation applied to v1.
    reference, choices = dx.interior_tracking(
        [{"date": d["date"], "anchor": d["anchor"], "y": d["y"], "issued": d["v1"]} for d in days])
    if [d["v2"] for d in days] != reference:
        raise ValueError("v2's vectors differ from #247's reference implementation")

    persistence = persistence_losses()
    if set(persistence) != {d["date"] for d in days}:
        raise ValueError("the persistence records and the walk score different days")
    decides = [d for d in days if _in(d["date"], DECIDES)]
    check = [d for d in days if _in(d["date"], CHECK)]

    main_block = window_block(decides, rows, splits, persistence, "2018-2025")
    main_block["bar"] = bar_verdict(main_block["coverage"], main_block["crps"]["v2_vs_v1"])
    check_block = window_block(check, rows, splits, persistence, "2026")
    check_block["label"] = CHECK_LABEL
    check_block["coverage_interval"] = coverage_interval(check, "v2", ("2026", "v2"))
    check_block["coverage_interval_v1"] = coverage_interval(check, "v1", ("2026", "v1"))
    check_block["gate"] = gate_verdict(check_block["coverage_interval"], check_block["crps"]["v2_vs_v1"])

    outer_moved = sum(1 for d in days if d["v2"][0] != d["v1"][0] or d["v2"][4] != d["v1"][4])
    record = {
        "record": "pressure_model_v2_distribution_h1",
        "directive": "#244",
        "descriptive": ("v2 against v1 and as-of persistence at h = 1. It changes no published figure: "
                        "whether v2 joins the live record is Eleonora's decision (#245)"),
        "model": {
            "name": "pressure model v2 (distribution)",
            "built_from": "#247's recommendation (docs/diagnosis-interior-calibration.md)",
            "v1": walks[1]["model"],
            "settings": walks[1]["settings"],
            "code": "src/repo_model/interior.py (NestedInteriorFoldPid)",
        },
        "panel_sha256": walks[1]["panel_sha256"],
        "walk": "scripts/final_test_opening.distribution_walk with live_record._compare_sides(1)",
        "windows": {
            "decides": {"first": DECIDES[0].isoformat(), "last": DECIDES[1].isoformat()},
            "check_2026": {"first": CHECK[0].isoformat(), "last": CHECK[1].isoformat(),
                           "label": CHECK_LABEL},
            "last_day_read": LAST_READ.isoformat(),
        },
        "bar_declared": BAR,
        "gate_declared": GATE,
        "v1_unchanged": {
            "v1_vectors_sha256": vectors_sha256(ours),
            "identical_to_v1_interior_diagnosis": True,
            "reproduces_published_crps": True,
            "records": [str(CRPS_RECORD.relative_to(REPO)), str(FINAL_RECORD.relative_to(REPO)),
                        str(DIAGNOSIS_RECORD.relative_to(REPO))],
        },
        "v2_vectors_sha256": vectors_sha256([[d["date"], d["v2"]] for d in days]),
        "v2_equals_reference": True,
        "days_the_sort_moved_an_outer_quantile": outer_moved,
        "interior_step_choices": walks[1]["interior_blocks"],
        "window_2018_2025": main_block,
        "check_2026": check_block,
        "anchors": [[d["date"], d["anchor"]] for d in days],
    }
    others = {}
    final_cells = {cell["horizon"]: cell
                   for cell in json.loads(FINAL_RECORD.read_text(encoding="utf-8"))["crps_reported_only"]}
    for h in sorted(k for k in walks if k != 1):
        hd = walks[h]["days"]
        opened = [d for d in hd if _in(d["date"], CHECK)]
        v1_opened = sum(crps_from_quantiles(LEVELS, d["v1"], d["y"]) for d in opened) / len(opened)
        if len(opened) != final_cells[h]["days"] or v1_opened != final_cells[h]["crps_published_bps"]:
            raise ValueError(f"v1 at h = {h} does not reproduce the final test's cell")
        sub = [d for d in hd if _in(d["date"], DECIDES)]
        v1_losses = [crps_from_quantiles(LEVELS, d["v1"], d["y"]) for d in sub]
        v2_losses = [crps_from_quantiles(LEVELS, d["v2"], d["y"]) for d in sub]
        cell = onset.paired_difference(v1_losses, v2_losses, list(range(len(sub))),
                                       block_length=BLOCK_LENGTH + (h - 1),
                                       seed=onset._seed("#244", "carry-over", h))
        others[f"h{h}"] = {"days": len(sub), "crps_v1_bps": statistics.fmean(v1_losses),
                           "crps_v2_bps": statistics.fmean(v2_losses), "v2_vs_v1": cell,
                           "v1_reproduces_final_test_cell": True,
                           "coverage": band_coverage(sub, "v2"), "coverage_v1": band_coverage(sub, "v1")}
    if others:
        record["carry_over_h2_to_h5_reported_only"] = {
            "window": "2018-06-29 to 2025-12-31",
            "note": ("whether the fix carries over to longer horizons (#247 asked #244 to confirm); "
                     "reported only, it decides nothing. Block length 2 + (h - 1), as the final test"),
            **others,
        }
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"bar": main_block["bar"], "gate": check_block["gate"]}, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    wk = sub.add_parser("walk", help="the published side's walk with v2's calibration")
    wk.add_argument("--panel", type=Path, required=True)
    wk.add_argument("--horizon", type=int, choices=dx.HORIZONS, default=1)
    wk.add_argument("--output", type=Path, required=True)
    wk.set_defaults(func=walk_command)
    asm = sub.add_parser("assemble", help="the record, from the walks")
    asm.add_argument("--panel", type=Path, required=True)
    asm.add_argument("--walks", type=Path, nargs="+", required=True)
    asm.add_argument("--output", type=Path, default=RECORD)
    asm.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
