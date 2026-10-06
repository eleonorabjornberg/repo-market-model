"""Pressure model v2's distribution at h = 1: v1 with its interior calibrated (#244).

Eleonora's ruling of 6 October 2026 on #244 fixes #243 (v1's 50% band covers
about 30% of outcomes) as a new model, v2, beside an unchanged v1. v2 is v1's
issued vector with q25, q50 and q75 moved by one of the interior calibrations
declared in `repo_model.interior` (`CANDIDATES`); q05 and q95 are v1's.

Two runs, then one record:

* `walk --end 2025-12-31`: the **selection run**. The published distribution's
  fold loop at h = 1 (`final_test_opening.distribution_walk`, the frozen
  `compare`'s sides through `live_record._compare_sides(1)`), with v1's nested
  conformal PID wrapped by `interior.FoldInterior`. Every candidate runs over
  every scored day; the band issued is chosen by nested walk-forward selection
  by CRPS on the backtest's 21-day refit blocks, from scored days only. As-of
  persistence runs on the same grid. Nothing after 2025-12-31 is read.
* `walk --end 2026-09-03 --frozen NAME`: the **2026 check** (Eleonora's ruling
  of 6 October 2026, scoping #244). v2 is frozen at the candidate the selection
  run chooses on all of 2018-06-29 to 2025-12-31 (`frozen_choice`), and the
  same walk is run once through the end of the near-blind tier, on the panel,
  window and fold grid of `docs/runs/final_test_near_blind.json`.
* `record`: `docs/runs/pressure_model_v2_distribution_h1.json`. v2 against v1
  and against as-of persistence by CRPS, paired with a 90% stationary-bootstrap
  interval (mean block length 2, as v1's CRPS record), split by regime and
  pressure-day type; the coverage of the 50% and 90% bands, with the misses
  below and above and a 90% interval on each coverage; each band's mean width;
  the median's absolute error. On 2018-2025 from the selection run (nested v2);
  on 2026 from the check run (frozen v2), in a block labelled
  `CHECK_LABEL` that chose nothing. It states plainly whether the directive's
  bar (`bar`) and the proposed gate for #245 (`gate`) hold.

The coverage is counted two ways (the ruling's "Measuring coverage on
whole-basis-point outcomes"): as is, an outcome on a band edge inside; and
counting an outcome exactly on a band edge as half inside. The gate uses the
half-inside count (`GATE_MEASURE`), declared here before the 2026 run.

v1 is untouched: the walk checks v1's declaration against the published CRPS
record, and `record` refuses unless every scored day's v1 CRPS equals the
published one exactly (`compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json`
through 2025, `final_test_near_blind.json` in 2026).

    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_model_v2.py walk \\
        --panel PUB.csv --end 2025-12-31 --output OUT/selection.json
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_model_v2.py walk \\
        --panel PUB.csv --end 2026-09-03 --frozen NAME --output OUT/check_2026.json
    PYTHONPATH=src python3 scripts/pressure_model_v2.py record --panel PUB.csv \\
        --selection OUT/selection.json --check OUT/check_2026.json \\
        --output docs/runs/pressure_model_v2_distribution_h1.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import statistics
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import interior, lockbox, onset  # noqa: E402
from repo_model.baseline import _code_provenance, _split_labels, panel_sha256, split_document  # noqa: E402
from repo_model.contract import QUANTILE_LEVELS  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import crps_from_quantiles, stationary_bootstrap_interval  # noqa: E402
from repo_model.recalibration import select_constants  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(f"v2_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fto = _script("final_test_opening")
fp = fto.fp

HORIZON = 1
#: The selection window: v1's CRPS record's scored days (#244, Do 3).
SELECTION_FIRST = date(2018, 6, 29)
SELECTION_LAST = date(2025, 12, 31)
#: The 2026 check's window: the final test's (`final_test_near_blind.json`).
CHECK_FIRST = date(2026, 1, 2)
CHECK_LAST = fp.CRPS_LAST
BLOCK_LENGTH = fp.CRPS_BLOCK_LENGTH
#: The published records v1's per-day CRPS is checked against.
V1_CRPS_RECORD = "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
V1_CHECK_RECORD = "docs/runs/final_test_near_blind.json"
RECORD = "docs/runs/pressure_model_v2_distribution_h1.json"

SEEN_LABEL = "seen: this window motivated the fix (#243)"
CHECK_LABEL = "2026 check: seen data, not evidence"
#: The coverage count the gate uses, declared before the 2026 run.
GATE_MEASURE = "half_inside"
CRPS_SIGN = ("paired = CRPS(other) - CRPS(v2) per day; a positive mean favours v2. "
             "v2 is not worse than the other when the 90% interval's upper bound is not below 0")
#: The bands: (name, nominal coverage, lower position, upper position).
BANDS = (("50", 0.5, 1, 3), ("90", 0.9, 0, 4))


def _walk_command(args) -> int:
    rows = [row for row in load_daily_panel(args.panel) if row.date <= args.end]
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    if args.end not in (SELECTION_LAST, CHECK_LAST):
        raise ValueError(f"--end is {SELECTION_LAST} (selection) or {CHECK_LAST} (2026 check)")
    if (args.end == CHECK_LAST) != (args.frozen is not None):
        raise ValueError("the 2026 check runs v2 frozen, and only the 2026 check does")
    names = [candidate.name for candidate in interior.CANDIDATES]
    frozen = None if args.frozen is None else names.index(args.frozen)
    live_record = _script("live_record")
    fto.live_record = live_record
    registry = json.loads(fp.REGISTRY.read_text())
    sides, parsed = live_record._compare_sides(HORIZON)
    made = []

    def wrapped(inner):
        def factory(rows_, rule):
            fold = interior.FoldInterior(rows_, inner(rows_, rule), refit_every=parsed.refit_every,
                                         frozen=frozen)
            made.append(fold)
            return fold
        return factory

    walks = {}
    for side, (name, fit, features, online) in sides.items():
        if side == "published":
            online = wrapped(online)
        walk, levels, settings = fto.distribution_walk(
            rows, fit=fit, features=features, online_calibration=online, registry=registry,
            horizon=HORIZON, minimum_history=parsed.minimum_history, refit_every=parsed.refit_every,
        )
        live_record._require_crps_declaration(side, HORIZON, name, features, settings)
        if tuple(levels) != tuple(QUANTILE_LEVELS):
            raise ValueError(f"{side} reports levels {levels}")
        walks[side] = walk
    (fold,) = made
    if [i for i, _ in walks["published"]] != [i for i, _ in walks["persistence"]]:
        raise ValueError("the two sides are not on one fold grid")
    if [day.index for day in fold.days] != [i for i, _ in walks["published"]]:
        raise ValueError("v2 did not see every scored day")
    for day, (_, issued) in zip(fold.days, walks["published"]):
        if tuple(issued) != day.bands[day.chosen]:
            raise ValueError(f"{day.scored_date}: the walk scored a band v2 did not issue")
    persistence = dict(walks["persistence"])
    document = {
        "directive": "#244",
        "run": "check_2026" if frozen is not None else "selection",
        "end": args.end.isoformat(),
        "panel_sha256": panel_sha256(args.panel),
        "provenance": {"code": _code_provenance(), "ml_libraries": _ml_libraries()},
        "v1_record": live_record.published_distribution_record(HORIZON),
        "v1_declaration_sha256": live_record.published_declaration_sha256(HORIZON),
        "interior": fold.interior_settings,
        "blocks": fold.account()["interior_blocks"],
        "days": [
            {
                "scored_date": day.scored_date.isoformat(),
                "anchor": day.anchor.isoformat(),
                "actual": rows[day.index].spread_bps,
                "v1": list(day.v1),
                "bands": [list(band) for band in day.bands],
                "chosen": day.chosen,
                "persistence": list(persistence[day.index]),
            }
            for day in fold.days
        ],
    }
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"days": len(fold.days), "blocks": len(fold.blocks),
                      "first": document["days"][0]["scored_date"],
                      "last": document["days"][-1]["scored_date"]}))
    return 0


def _ml_libraries():
    import numpy
    import sklearn

    return {"numpy": numpy.__version__, "scikit-learn": sklearn.__version__}


# --------------------------------------------------------------------------- scoring


def _mean(values):
    values = list(values)
    return sum(values) / len(values) if values else None


def _interval(series, seed):
    lower, upper = stationary_bootstrap_interval(
        lambda idx: sum(series[i] for i in idx) / len(idx), len(series),
        block_length=BLOCK_LENGTH, seed=seed, replications=onset.REPLICATIONS, level=onset.LEVEL,
    )
    return {"lower": lower, "upper": upper, "level": onset.LEVEL, "method": "stationary_bootstrap",
            "block_length": BLOCK_LENGTH, "replications": onset.REPLICATIONS, "seed": seed}


def inside(actual: float, low: float, high: float, measure: str) -> float:
    """1 inside `[low, high]`, 0 outside; on an edge 1 as is, a half under `half_inside`."""

    if low < actual < high:
        return 1.0
    if actual == low or actual == high:
        return 0.5 if measure == "half_inside" else 1.0
    return 0.0


def coverage(vectors, actuals, *, seed):
    """Each band's coverage both ways, with a 90% interval, its misses and its mean width."""

    out = {}
    for name, nominal, lo, hi in BANDS:
        entry = {"nominal": nominal, "days": len(actuals)}
        for measure in ("as_is", "half_inside"):
            series = [inside(y, v[lo], v[hi], measure) for v, y in zip(vectors, actuals)]
            entry[measure] = {"coverage": _mean(series),
                              "interval": _interval(series, onset._seed(seed, name, measure))}
        entry["below"] = _mean(1.0 if y < v[lo] else 0.0 for v, y in zip(vectors, actuals))
        entry["above"] = _mean(1.0 if y > v[hi] else 0.0 for v, y in zip(vectors, actuals))
        entry["on_edge"] = _mean(1.0 if y in (v[lo], v[hi]) else 0.0 for v, y in zip(vectors, actuals))
        entry["mean_width_bps"] = _mean(v[hi] - v[lo] for v in vectors)
        out[name] = entry
    return out


def median_error(vectors, actuals):
    errors = [abs(v[2] - y) for v, y in zip(vectors, actuals)]
    return {"mean_bps": _mean(errors), "median_bps": statistics.median(errors),
            "share_within_1bp": _mean(1.0 if e <= 1.0 else 0.0 for e in errors),
            "share_within_2bp": _mean(1.0 if e <= 2.0 else 0.0 for e in errors)}


def by_day_type(rows, splits, dates, vectors, actuals):
    """The 50% and 90% coverage (half inside) and the median's error, per pressure-day type."""

    _, types = _split_labels(splits, rows, dates)
    out = {}
    for kind in sorted(set(types)):
        keep = [k for k, t in enumerate(types) if t == kind]
        vs = [vectors[k] for k in keep]
        ys = [actuals[k] for k in keep]
        out[kind] = {
            "days": len(keep),
            "coverage_half_inside": {
                name: _mean(inside(y, v[lo], v[hi], "half_inside") for v, y in zip(vs, ys))
                for name, _, lo, hi in BANDS
            },
            "median_abs_error_bps": _mean(abs(v[2] - y) for v, y in zip(vs, ys)),
        }
    return out


def block(rows, splits, days, v2_vectors, *, seed):
    """One window's evidence: v2 against v1 and as-of persistence, coverage, error."""

    dates = [date.fromisoformat(d["scored_date"]) for d in days]
    actuals = [d["actual"] for d in days]
    vectors = {"v1": [tuple(d["v1"]) for d in days], "v2": v2_vectors,
               "persistence": [tuple(d["persistence"]) for d in days]}
    losses = {name: [crps_from_quantiles(QUANTILE_LEVELS, v, y) for v, y in zip(vs, actuals)]
              for name, vs in vectors.items()}
    positions = list(range(len(days)))
    paired = {}
    for other in ("v1", "persistence"):
        cell = onset.paired_difference(losses[other], losses["v2"], positions,
                                       block_length=BLOCK_LENGTH, seed=onset._seed(seed, other))
        differences = [a - b for a, b in zip(losses[other], losses["v2"])]
        cell["splits"] = split_document(splits, rows, dates, differences,
                                        block_length=BLOCK_LENGTH, seed=onset._seed(seed, other))
        cell["v2_not_worse"] = cell["interval"]["upper"] >= 0
        paired[f"v2_vs_{other}"] = cell
    return {
        "days": len(days),
        "first": dates[0].isoformat(),
        "last": dates[-1].isoformat(),
        "crps_bps": {name: _mean(values) for name, values in losses.items()},
        "paired": paired,
        "sign_convention": CRPS_SIGN,
        "coverage": {name: coverage(vs, actuals, seed=onset._seed(seed, "coverage", name))
                     for name, vs in vectors.items()},
        "median_abs_error": {name: median_error(vs, actuals) for name, vs in vectors.items()},
        "by_day_type": {name: by_day_type(rows, splits, dates, vs, actuals)
                        for name, vs in vectors.items()},
    }, losses


def _published_v1_losses():
    compare = json.loads((REPO / V1_CRPS_RECORD).read_text(encoding="utf-8"))
    final = json.loads((REPO / V1_CHECK_RECORD).read_text(encoding="utf-8"))
    out = {entry["scored_date"]: entry["loss_b_bps"] for entry in compare["comparison"]["per_origin"]}
    for entry in final["primary"]["window_per_origin"]:
        out.setdefault(entry["scored_date"], entry["loss_b_bps"])
        if out[entry["scored_date"]] != entry["loss_b_bps"]:
            raise ValueError(f"{entry['scored_date']}: the two published v1 records disagree")
    return out


def require_v1_unchanged(days, published=None):
    """Every day's v1 CRPS is the published one, exactly; returns the days checked.

    Raises:
        ValueError: a day's v1 vector scores other than v1's published CRPS,
            or a scored day has no published CRPS.
    """

    published = _published_v1_losses() if published is None else published
    for d in days:
        loss = crps_from_quantiles(QUANTILE_LEVELS, tuple(d["v1"]), d["actual"])
        if d["scored_date"] not in published:
            raise ValueError(f"{d['scored_date']}: no published v1 CRPS")
        if loss != published[d["scored_date"]]:
            raise ValueError(f"{d['scored_date']}: v1 scores {loss!r}, published {published[d['scored_date']]!r}")
    return len(days)


def v1_digest(days) -> str:
    """The SHA-256 of every scored day's v1 vector, canonical JSON."""

    canonical = json.dumps([[d["scored_date"], list(d["v1"])] for d in days], separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def frozen_choice(days):
    """The candidate with the least pooled CRPS over every selection-window day, by name."""

    history = [
        (date.fromisoformat(d["scored_date"]),
         [crps_from_quantiles(QUANTILE_LEVELS, tuple(band), d["actual"]) for band in d["bands"]])
        for d in days
    ]
    chosen, _ = select_constants(history, SELECTION_LAST, len(interior.CANDIDATES),
                                 fallback=interior.FALLBACK)
    return interior.CANDIDATES[chosen].name


def _bar(evidence):
    v2 = evidence["coverage"]["v2"]
    v1 = evidence["coverage"]["v1"]
    out = {}
    for measure in ("as_is", "half_inside"):
        value = v2["50"][measure]["coverage"]
        out[f"50_band_45_to_55_{measure}"] = {"coverage": value, "holds": 0.45 <= value <= 0.55}
    out["90_band_stays_calibrated"] = {
        "coverage_half_inside": v2["90"]["half_inside"]["coverage"],
        "interval": v2["90"]["half_inside"]["interval"],
        "identical_to_v1": v2["90"] == v1["90"],
        "holds": v2["90"] == v1["90"],
        "reading": "v2's q05 and q95 are v1's exactly, so its 90% band is v1's on every day",
    }
    paired = evidence["paired"]["v2_vs_v1"]
    out["crps_no_worse_than_v1"] = {"mean_bps": paired["mean"], "interval": paired["interval"],
                                    "holds": paired["v2_not_worse"]}
    return out


def _gate(check):
    cov = check["coverage"]["v2"]
    out = {"measure": GATE_MEASURE}
    for name, nominal in (("50", 0.5), ("90", 0.9)):
        interval = cov[name][GATE_MEASURE]["interval"]
        out[f"{name}_band_interval_includes_{name}"] = {
            "coverage": cov[name][GATE_MEASURE]["coverage"], "interval": interval,
            "holds": interval["lower"] <= nominal <= interval["upper"],
        }
    paired = check["paired"]["v2_vs_v1"]
    out["crps_not_worse_than_v1"] = {"mean_bps": paired["mean"], "interval": paired["interval"],
                                     "holds": paired["v2_not_worse"]}
    out["holds"] = all(entry["holds"] for key, entry in out.items() if isinstance(entry, dict))
    return out


def _record_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(fp.SPLITS)
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    check = json.loads(args.check.read_text(encoding="utf-8"))
    if (selection["run"], check["run"]) != ("selection", "check_2026"):
        raise ValueError("--selection is the selection run, --check the 2026 check")
    for run in (selection, check):
        if run["provenance"]["code"] != selection["provenance"]["code"]:
            raise ValueError("the two runs were made at different code")
        if run["interior"]["candidates"] != interior.declaration()["candidates"]:
            raise ValueError("a run's candidates are not the declared ones")
    sel_days = [d for d in selection["days"]
                if SELECTION_FIRST <= date.fromisoformat(d["scored_date"]) <= SELECTION_LAST]
    if len(sel_days) != len(selection["days"]):
        raise ValueError("the selection run scored a day outside its window")
    chosen = frozen_choice(sel_days)
    if check["interior"]["selection"] != {"method": "frozen", "candidate": chosen}:
        raise ValueError(f"the 2026 check did not run the frozen choice {chosen}")
    position = [c.name for c in interior.CANDIDATES].index(chosen)
    before = {d["scored_date"]: d for d in sel_days}
    for d in check["days"]:
        if d["scored_date"] in before:
            earlier = before[d["scored_date"]]
            if (d["v1"], d["bands"], d["persistence"]) != (earlier["v1"], earlier["bands"],
                                                           earlier["persistence"]):
                raise ValueError(f"{d['scored_date']}: the two runs disagree before 2026")
    check_days = [d for d in check["days"]
                  if CHECK_FIRST <= date.fromisoformat(d["scored_date"]) <= CHECK_LAST]
    lockbox.require_unlocked([date.fromisoformat(d["scored_date"]) for d in check_days],
                             where="pressure model v2's 2026 check")
    if len(check_days) != fp.CRPS_WINDOW_DAYS:
        raise ValueError(f"the 2026 check scores {len(check_days)} days, not {fp.CRPS_WINDOW_DAYS}")
    checked = require_v1_unchanged(sel_days) + require_v1_unchanged(check_days)

    nested = [tuple(d["bands"][d["chosen"]]) for d in sel_days]
    evidence, _ = block(rows, splits, sel_days, nested, seed=onset._seed("#244", "selection"))
    frozen_in_window, _ = block(rows, splits, sel_days, [tuple(d["bands"][position]) for d in sel_days],
                                seed=onset._seed("#244", "frozen", "selection"))
    check_block, _ = block(rows, splits, check_days, [tuple(d["bands"][position]) for d in check_days],
                           seed=onset._seed("#244", "check_2026"))
    candidates = {}
    for k, candidate in enumerate(interior.CANDIDATES):
        vs = [tuple(d["bands"][k]) for d in sel_days]
        ys = [d["actual"] for d in sel_days]
        candidates[candidate.name] = {
            "crps_bps": _mean(crps_from_quantiles(QUANTILE_LEVELS, v, y) for v, y in zip(vs, ys)),
            "coverage_50_half_inside": _mean(inside(y, v[1], v[3], "half_inside") for v, y in zip(vs, ys)),
            "chosen_blocks": sum(1 for b in selection["blocks"] if b["chosen"] == candidate.name),
        }
    check_block["label"] = CHECK_LABEL
    check_block["seen"] = SEEN_LABEL
    check_block["decides"] = ("nothing in v2's choice; it is the gate for #245 (v2 going live), "
                              "and only v2's live record is evidence for v2")
    check_block["gate"] = _gate(check_block)
    evidence["bar"] = _bar(evidence)
    record = {
        "directive": "#244",
        "record": "pressure model v2's distribution at h = 1: v1 with its interior quantiles calibrated",
        "ruling": ("Eleonora, 6 October 2026, on #244: v2 is a new model logged alongside the "
                   "unchanged v1; v1's records and live record stay exactly as they are"),
        "horizon": HORIZON,
        "panel_sha256": selection["panel_sha256"],
        "provenance": selection["provenance"],
        "model_declaration": {
            "v1_record": selection["v1_record"],
            "v1_declaration_sha256": selection["v1_declaration_sha256"],
            "interior": {key: value for key, value in selection["interior"].items() if key != "selection"},
            "selection": {**selection["interior"]["selection"],
                          "window": {"first": SELECTION_FIRST.isoformat(), "last": SELECTION_LAST.isoformat()},
                          "never_sees": "any day after 2025-12-31"},
            "frozen_choice": chosen,
            "frozen_choice_rule": ("the candidate with the least pooled CRPS over every scored "
                                   "day of the selection window"),
        },
        "v1_unchanged": {
            "days_checked": checked,
            "reading": (f"every scored day's v1 vector scores exactly the CRPS published in "
                        f"{V1_CRPS_RECORD} (2018-2025) and {V1_CHECK_RECORD} (2026)"),
            "v1_vectors_sha256": v1_digest(sel_days + check_days),
        },
        "selection_blocks": selection["blocks"],
        "candidates_2018_2025": candidates,
        "evidence_2018_2025": evidence,
        "frozen_choice_2018_2025": {
            **{key: frozen_in_window[key] for key in ("days", "crps_bps", "coverage")},
            "reading": "in-sample for the frozen choice, which was chosen on these days; reported only",
        },
        "check_2026": check_block,
        "per_day": [
            {"scored_date": d["scored_date"], "actual": d["actual"], "v1": d["v1"],
             "v2": d["bands"][d["chosen"] if rule == "nested" else position], "v2_rule": rule}
            for days, rule in ((sel_days, "nested"), (check_days, "frozen")) for d in days
        ],
    }
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"frozen_choice": chosen, "bar": evidence["bar"], "gate": check_block["gate"],
                      "crps_2018_2025": evidence["crps_bps"], "crps_2026": check_block["crps_bps"]},
                     indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk = sub.add_parser("walk", help="the published distribution's walk with v2 beside it")
    walk.add_argument("--panel", type=Path, required=True)
    walk.add_argument("--end", type=date.fromisoformat, required=True)
    walk.add_argument("--frozen", choices=[c.name for c in interior.CANDIDATES])
    walk.add_argument("--output", type=Path, required=True)
    walk.set_defaults(func=_walk_command)
    rec = sub.add_parser("record", help="the published record from the two runs")
    rec.add_argument("--panel", type=Path, required=True)
    rec.add_argument("--selection", type=Path, required=True)
    rec.add_argument("--check", type=Path, required=True)
    rec.add_argument("--output", type=Path, required=True)
    rec.set_defaults(func=_record_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
