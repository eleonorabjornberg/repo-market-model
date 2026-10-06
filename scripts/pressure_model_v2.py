"""Pressure model v2's distribution at h = 1, scored against v1 and as-of persistence (#244).

v2 is #247's candidate (iv), the one the inner block chooses (below): v1's
features, as-of fold grid, refit cadence and nested conformal PID on trees of
maximum depth 3 (`V2_TREE_SETTINGS`), with each interior level (q25, q50,
q75) moved by its own online quantile tracker (`repo_model.interior`). Nothing
in v1 changes: v1 is its own walk, #247's (`final_test_opening.distribution_walk`
with `live_record._compare_sides(1)`), and v2's walk changes the trees only
inside its own process.

The bar (`BAR`, from #244) and the 2026 gate (`GATE`, from Eleonora's scoping
ruling on #244) were declared here before anything was scored.

* The bar is read on the inner and outer blocks, and on 2018-06-29 to
  2025-12-31 pooled, which is exploratory.
* The gate is read on 2026-01-02 to 2026-09-03, the opened near-blind window.
  Those days motivated the fix (#243), so they are seen data, not evidence.
* The tracking step is chosen online, by nested walk-forward selection at each
  21-day refit block from labels observable at that block's anchor.
* No day after 2026-09-03 is read.

Eleonora's ruling on PR #252 (6 October 2026) applies her amendment of #247
here. #247 chose (i) on all of 2018-2025, the data it was diagnosed and tuned
on, so the choice is redone on the inner block (`INNER`, 2018-06-29 to
2022-12-31) under #247's rule, with the conditional gates
(`CONDITIONAL_GATES`) added to the bar. The candidate it chooses is committed
as `CHOSEN`. Only then is the outer block (`OUTER`, 2023-01-01 to 2025-12-31)
scored, once, for v1 and the chosen candidate. Any historical edge of v2 over
v1 is labelled `EXPLORATORY`.

Eleonora's rulings on PR #252 of 14:02 and 14:24 then asked for v2's calibration by
pressure-day type to be diagnosed on the inner block and fixed. `DIAGNOSIS` and
`FIX_CANDIDATES` were declared (3b9ccbb) before the fix was chosen, and `CHOSEN_FIX`
was committed before the outer block was scored a second time. The fix is a width
tracker on the 50% band after (iv)'s levels (`repo_model.interior.OnlineWidth`).

Eleonora's ruling on PR #252 of 6 October 2026 (16:48) then asked for a quarter-end location term. `QE_CANDIDATES`
and `QE_SELECTION` were declared in one commit before any candidate was walked, with (iv)'s depth-3 trees made a
setting of the fit in `ml.py` (`ml.fit_gradient_boosted_quantiles(max_depth=3)`, `candidate_setup`). The choice is on
the inner block only (`choose-quarter-end`), committed as `CHOSEN_QE_FIX` before the outer block is scored a third time.

Six subcommands:

* `choose-quarter-end`: the quarter-end term, chosen on the inner block only (`quarter_end_choice`).

* `diagnose`: v1 and (iv), by pressure-day type and regime, on the inner block only.
* `choose-fix`: the fix, chosen on the inner block only (`fix_choice`).

* `choose`: #247's question 7, redone on the inner block (`inner_choice`).
* `walk`: v2's walk: the published side's features and fold grid with v2's
  trees and calibration. Each scored day keeps its anchor, its outcome, the
  PID vector of v2's trees, the interior layer's vector (`tracked`), its width
  class and v2's vector.
* `assemble`: the record, `docs/runs/pressure_model_v2_distribution_h1.json`.
  It first checks that v1's vectors are #247's to the byte
  (`v1_interior_diagnosis.json`), that they reproduce the published h = 1 CRPS
  records exactly, that the inner block still chooses `CHOSEN`, and that v2's
  vectors are #247's reference implementation of that candidate.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    # #247's walks: v1 and every question 4 variant at h = 1, and v1 at h = 2 to 5.
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/interior_diagnosis.py walk \\
        --panel PUB.csv --horizon 1 --variant NAME --no-in-sample --output OUT/walk_NAME_h1.json
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/interior_diagnosis.py walk \\
        --panel PUB.csv --horizon H --variant v1 --output OUT/v1walk_hH.json
    # The inner block's choice (it printed the CHOSEN committed below).
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_model_v2.py choose --panel PUB.csv \\
        --walks OUT/walk_*_h1.json --output OUT/choice.json
    # The diagnosis and the fix, on the inner block only, from the record as it stood before the fix
    # (git show f33209e:docs/runs/pressure_model_v2_distribution_h1.json > OUT/before_fix.json).
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_model_v2.py diagnose --panel PUB.csv \\
        --before-fix-record OUT/before_fix.json --output OUT/diagnosis.json
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_model_v2.py choose-fix --panel PUB.csv \\
        --before-fix-record OUT/before_fix.json --output OUT/fix_choice.json
    # v2 (the chosen candidate and the fix) at h = 1 to 5, then the record.
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_model_v2.py walk \\
        --panel PUB.csv --horizon H --output OUT/v2_hH.json
    PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_model_v2.py assemble --panel PUB.csv \\
        --walks OUT/v2_h*.json --variant-walks OUT/walk_*_h1.json OUT/v1walk_h*.json \\
        --before-fix-record OUT/before_fix.json --output docs/runs/pressure_model_v2_distribution_h1.json
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


#: Eleonora's ruling on PR #252 (6 October 2026), applying her amendment of
#: #247 here: the choice is redone on an inner block, and an outer block no
#: choice has seen is scored once, for v1 and the chosen candidate only.
INNER = (date(2018, 6, 29), date(2022, 12, 31))
OUTER = (date(2023, 1, 1), date(2025, 12, 31))

#: Any historical edge of v2 over v1 carries this label (ruling on PR #252,
#: item 4). Only v2's live record can show that it is better.
EXPLORATORY = "exploratory (selection-adjusted uncertainty not computed)"

#: The conditional gates (ruling on PR #252, item 2), added to the bar and to
#: the inner block's eligibility rule, declared before the outer block is
#: scored. The thresholds are the orchestrating session's proposal; Eleonora
#: may change them on the PR.
CONDITIONAL_GATES = {
    "declared": ("Eleonora's ruling on PR #252 and her amendment of #247 (6 October 2026); the thresholds "
                 "were proposed by the orchestrating session, and she may change them on the PR"),
    "applies_to": "the inner block, then the outer block, h = 1",
    "minimum_days": 20,
    "inconclusive": "a cell with fewer than 20 days is inconclusive: it neither passes nor fails",
    "measures": {
        "band_90_half_edge": "the 90% band's coverage, an outcome exactly on an edge counting one half inside",
        "above_q95": "the share of outcomes above q95, an outcome exactly on q95 counting one half",
    },
    "cells": {
        "all": "every scored day of the block",
        "quarter_end": ("pressure-day type quarter_end (metadata/evaluation_splits.json): the turn day of each "
                        "quarter; every year-end is a quarter-end"),
        "scarce": ("reserve_scarcity_state 3, read as-of at the day's h = 1 decision instant "
                   "(onset_post_mortem.as_of_reads)"),
        "coupon_settlement": ("treasury_settlement_coupons above 0, read as-of at the day's h = 1 decision "
                              "instant (onset_post_mortem.as_of_reads, as at_risk_by_state reads it)"),
    },
    "gates": [
        {"name": "band_90_quarter_end", "cell": "quarter_end", "measure": "band_90_half_edge", "at_least": 80.0},
        {"name": "band_90_scarce", "cell": "scarce", "measure": "band_90_half_edge", "at_least": 85.0},
        {"name": "band_90_coupon_settlement", "cell": "coupon_settlement", "measure": "band_90_half_edge",
         "at_least": 85.0},
        {"name": "above_q95_pooled", "cell": "all", "measure": "above_q95", "at_most": 8.0},
        {"name": "above_q95_quarter_end", "cell": "quarter_end", "measure": "above_q95", "at_most": 15.0},
    ],
}

#: How the choice is redone on the inner block (ruling on PR #252, item 1).
INNER_SELECTION = {
    "window": "2018-06-29 to 2022-12-31, h = 1",
    "rule": ("#247's question 7 rule (interior_diagnosis.SELECTION_RULE and select_candidate) on the inner "
             "block only: the same candidates, the same eligibility gates, a simpler eligible candidate "
             "preferred when its paired CRPS interval against the leader includes 0"),
    "ii_setting": ("(ii)'s tree setting is chosen again on the inner block, by #247's rule: the question 4 "
                   "variant meeting the bar with the lowest CRPS, or the lowest CRPS if none meets it"),
    "readings": {
        "bar_only": "eligible: #247's bar on the inner block (the ruling on PR #252: 'the same eligibility gates')",
        "bar_and_conditional_gates": ("eligible: #247's bar, and no conditional gate failing, on the inner block "
                                      "(#247's amendment, item 2)"),
    },
    "outer": ("v1 and the chosen candidate only are scored on the outer block, once, after the choice is "
              "committed as CHOSEN"),
}
READINGS = tuple(INNER_SELECTION["readings"])

#: The reading that binds the choice. #247's amendment adds the conditional
#: gates to the selection rule ("a candidate is eligible only if, on the inner
#: block, ... meets the gates"), and the ruling on PR #252 applies that
#: amendment's substance here. The other reading is reported beside it.
BINDING_READING = "bar_and_conditional_gates"

#: The candidate the inner block chose (`choose`, run on 6 October 2026),
#: committed before the outer block is scored. Under the binding reading it is
#: (iv), (ii)'s trees with (i)'s tracking: (i) is eligible but its paired CRPS
#: against (iv) excludes 0, and (iii) fails the coupon-settlement gate. Under
#: #247's bar alone it would be (iii). It is no longer (i).
CHOSEN = "iv_regularised_and_tracking"

#: (iv)'s trees: (ii)'s setting, chosen again on the inner block by #247's rule
#: (no question 4 variant meets the bar there; max depth 3 has the lowest CRPS).
#: #247's walk applied it by replacing the estimator class in its own process
#: (`interior_diagnosis._with_tree_settings`); v2 applies it as a setting of the fit,
#: `ml.fit_gradient_boosted_quantiles(max_depth=3)`, which names it in the fit's
#: `model_settings` (`candidate_setup`). The two give the same trees, which `assemble` checks.
V2_TREE_SETTINGS = {"max_depth": 3}
V2_TREE_VARIANT = "max_depth_3"


def _above_half_tie(y, q):
    return 1.0 - interior.below_half_tie(y, q)


def conditional_gates(days, field) -> dict:
    """Each conditional gate on `days`: its cell's size, value, threshold and verdict.

    Each day carries `y`, its vector under `field`, and `cells`, the set of
    conditional cells it belongs to ("all" is implied).
    """

    out = {}
    for gate in CONDITIONAL_GATES["gates"]:
        cell = gate["cell"]
        subset = [d for d in days if cell == "all" or cell in d["cells"]]
        entry = {"cell": cell, "measure": gate["measure"], "days": len(subset)}
        entry.update({k: gate[k] for k in ("at_least", "at_most") if k in gate})
        if not subset:
            entry.update(value=None, verdict="inconclusive")
            out[gate["name"]] = entry
            continue
        if gate["measure"] == "band_90_half_edge":
            value = 100.0 * statistics.fmean(_inside_half(d, field, 0, 4) for d in subset)
        else:
            value = 100.0 * statistics.fmean(_above_half_tie(d["y"], d[field][4]) for d in subset)
        entry["value"] = value
        if len(subset) < CONDITIONAL_GATES["minimum_days"]:
            entry["verdict"] = "inconclusive"
        elif "at_least" in gate:
            entry["verdict"] = "pass" if value >= gate["at_least"] else "fail"
        else:
            entry["verdict"] = "pass" if value <= gate["at_most"] else "fail"
        out[gate["name"]] = entry
    return out


def eligible_inner(summary: dict, gates: dict, *, reading: str) -> bool:
    """A candidate's eligibility on the inner block under one of `READINGS`."""

    if reading not in READINGS:
        raise ValueError(f"unknown reading {reading!r}")
    if not dx.eligible(summary):
        return False
    if reading == "bar_and_conditional_gates":
        return not any(g["verdict"] == "fail" for g in gates.values())
    return True


def day_cells(rows, scored_dates) -> dict:
    """Per scored date, the conditional cells it belongs to (`CONDITIONAL_GATES["cells"]`).

    The quarter-end type is the split declaration's. The scarcity state and the
    coupon settlement are read as-of at the day's h = 1 decision instant, through
    #214's reads (`onset_post_mortem.as_of_reads`), on the measurement panel
    whose published columns are the published panel's. Only days through
    `OUTER`'s end are read: the lockbox refuses a later `end`.
    """

    import tempfile

    from repo_model.baseline import _split_labels
    from repo_model.scarcity import measurement_declaration, with_reserve_scarcity_state

    if max(scored_dates) > OUTER[1]:
        raise ValueError("the conditional cells are read on the inner and outer blocks only")
    pm = _script("onset_post_mortem")
    validation = _script("scarcity_validation")
    _regimes, types = _split_labels(load_split_declaration(fp.SPLITS), rows, list(scored_dates))
    with tempfile.TemporaryDirectory() as directory:
        with measurement_declaration():
            build, _digest, registry, decision = validation.build_measurement_panel(pm.REGISTRY, Path(directory))
            measured = with_reserve_scarcity_state(build.observations)
            reads = pm.as_of_reads(measured, registry, decision_time=decision,
                                   minimum_history=pm.MINIMUM_HISTORY, end=OUTER[1])
    out = {}
    for when, kind in zip(scored_dates, types):
        read = reads.get(when)
        if read is None:
            raise ValueError(f"{when} has no as-of read on the published fold grid")
        cells = set()
        if kind == "quarter_end":
            cells.add("quarter_end")
        if read["state"] == 3:
            cells.add("scarce")
        if read[pm.COUPONS] is not None and float(read[pm.COUPONS]) > 0.0:
            cells.add("coupon_settlement")
        out[when.isoformat()] = sorted(cells)
    return out


def _with_cells(days, cells, field, vectors=None):
    return [{"date": d["date"], "y": d["y"], field: (vectors[k] if vectors else d[field]),
             "cells": set(cells[d["date"]])} for k, d in enumerate(days)]


def inner_choice(v1_days, variant_days, rows, splits, cells) -> dict:
    """#247's question 7, redone on the inner block (`INNER_SELECTION`), under each reading.

    `v1_days` is v1's h = 1 walk in #247's format (`date`, `anchor`, `y`,
    `issued`); `variant_days` maps each question 4 variant to its walk's days.
    Nothing outside `INNER` is read to choose.
    """

    rows_by_date = {row.date: row for row in rows}
    v1_vectors = [d["issued"] for d in v1_days]
    inner_positions = [k for k, d in enumerate(v1_days) if _in(d["date"], INNER)]
    inner_days = [v1_days[k] for k in inner_positions]

    # (ii)'s tree setting, by #247's rule on the inner block.
    variants = {}
    for name, days in variant_days.items():
        if [d["date"] for d in days] != [d["date"] for d in v1_days]:
            raise ValueError(f"{name} is not on v1's fold grid")
        variants[name] = dx._summary(v1_days, [d["issued"] for d in days], INNER)
    passing = [n for n in variants if dx.eligible(variants[n])]
    best = min(passing or list(variants), key=lambda n: (variants[n]["crps"], n))
    trees = [d["issued"] for d in variant_days[best]]

    tracked, choices = dx.interior_tracking(v1_days)
    tracked_trees, _ = dx.interior_tracking([dict(d, issued=v) for d, v in zip(v1_days, trees)])
    # The step selection is walk-forward: run on the inner block alone, it issues the same vectors.
    inner_only, inner_choices = dx.interior_tracking(inner_days)
    if inner_only != tracked[: len(inner_days)] or inner_positions != list(range(len(inner_days))):
        raise ValueError("(i) on the inner block alone differs from its walk's inner days")
    inner_trees, inner_choices_trees = dx.interior_tracking(
        [dict(d, issued=v) for d, v in zip(inner_days, trees)])
    if inner_trees != tracked_trees[: len(inner_days)]:
        raise ValueError("(iv) on the inner block alone differs from its walk's inner days")
    vectors = {
        "i_interior_tracking": tracked,
        "ii_regularised_trees": trees,
        "iii_residual_law": dx.residual_law(v1_days, rows_by_date, scaled=False),
        "iii_residual_law_scaled": dx.residual_law(v1_days, rows_by_date, scaled=True),
        "iv_regularised_and_tracking": tracked_trees,
    }
    candidates, summaries, gates = {}, {}, {}
    for name in dx.CANDIDATES:
        summaries[name] = dx._summary(v1_days, vectors[name], INNER)
        gates[name] = conditional_gates(_with_cells(inner_days, cells, "v", vectors[name]), "v")
        candidates[name] = {
            "inner": summaries[name],
            "conditional_gates_inner": gates[name],
            "paired_vs_v1_inner": dx.paired(v1_days, v1_vectors, vectors[name], rows, splits, INNER,
                                            ("#244", "inner", name)),
            "complexity": list(dx.COMPLEXITY[name]),
        }
    pair_cache = {}

    def paired_to_leader(name, leader):
        if (name, leader) not in pair_cache:
            pair_cache[(name, leader)] = dx.paired(v1_days, vectors[leader], vectors[name], rows, splits,
                                                   INNER, ("#244", "inner", name, "vs", leader))
        return pair_cache[(name, leader)]

    selections = {}
    for reading in READINGS:
        eligible = {n: summaries[n] for n in dx.CANDIDATES if eligible_inner(summaries[n], gates[n], reading=reading)}
        selections[reading] = dx.select_candidate(eligible, paired_to_leader)
    v1_inner = dx._summary(v1_days, v1_vectors, INNER)
    return {
        "declared": INNER_SELECTION,
        "window": [INNER[0].isoformat(), INNER[1].isoformat()],
        "days": len(inner_days),
        "v1": {"inner": v1_inner,
               "conditional_gates_inner": conditional_gates(_with_cells(inner_days, cells, "issued"), "issued")},
        "q4_variants_inner": variants,
        "ii_setting": {"variant": best, "tree_settings": dx.VARIANTS[best], "eligible_variants": sorted(passing)},
        "candidates": candidates,
        "selection": selections,
        "paired_against_leader": {f"{a}_vs_{b}": {k: v for k, v in p.items() if k != "splits"}
                                  for (a, b), p in pair_cache.items()},
        "i_step_choices_inner": inner_choices,
        "iv_step_choices_inner": inner_choices_trees,
        "inner_alone_equals_walk": ("(i) and (iv), with their step selection run on the inner block's days "
                                    "alone, issue exactly their walks' inner vectors"),
        "vectors": vectors,
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
# The calibration diagnosis and the fix (Eleonora's rulings on PR #252, 14:02 and 14:24)
# ---------------------------------------------------------------------------

#: The ruling of 6 October 2026, 14:02 ("diagnose, then fix") as the 14:24 ruling
#: amends it: the diagnosis is made on the inner block only, by pressure-day type
#: and by regime, and the per-day-type 50% bands are diagnostics, not gates. The
#: month-end and quarter-end cells are too small to gate on.
DIAGNOSIS = {
    "window": "2018-06-29 to 2022-12-31 (the inner block), h = 1; the outer block is not read",
    "models": "v1, and (iv) as it stood before the fix (v1's features, fold grid and nested PID on depth-3 trees, with the interior tracked)",
    "measures": [
        "50% band coverage and 90% band coverage, each half-inside, with a 90% stationary-bootstrap interval and the day count",
        "P(y <= q25), P(y <= q50), P(y <= q75), an outcome on the quantile counting one half",
        "the share of 50% band misses below and above the band",
        "the mean and the median of y - q50, the median absolute y - q50, and the mean 50% band width",
    ],
    "cells": {
        "all": "every inner day",
        "quarter_end": "pressure-day type quarter_end (the split declaration's `day_type`, the definition in force)",
        "year_end": "the quarter-end days of December (a subset of quarter_end)",
        "tax_date": "pressure-day type tax_date",
        "month_end": ("pressure-day type month_end under `day_type` (days_to_month_end calendar days, "
                      "the definition the scorecaster uses); `by_reporting_day_type` re-splits it under #278's "
                      "last two business days"),
        "coupon_settlement": "treasury_settlement_coupons above 0, read as-of (`day_cells`)",
        "scarce": "reserve_scarcity_state 3, read as-of (`day_cells`)",
        "ordinary": "pressure-day type ordinary",
    },
    "status": "diagnostics only: none of these per-day-type figures is a pass/fail gate (ruling of 14:24)",
}

#: The fix's declaration, written before the fix is chosen and before the outer
#: block is scored a second time. Each candidate is built on the inner block's
#: days only, by the reference implementations below (`class_level_tracking`,
#: `width_tracking`), and judged by `FIX_SELECTION`.
#:
#: What the diagnosis found, by day type, is the reason for these candidates: the
#: trees and the pooled interior trackers issue the same 50% band width on a turn
#: day as on an ordinary one, while the realised |y - q50| is larger there. (v)
#: gives the level trackers a day type of their own; (vi) to (viii) add a width
#: tracker after (iv)'s levels, by the partition they name.
FIX_PARTITIONS = {
    "pooled": "one class: every day",
    "turn_vs_ordinary": "two classes: ordinary, and every other pressure-day type (quarter_end, month_end, tax_date)",
    "by_type": "four classes: the split declaration's pressure-day types",
}
FIX_CANDIDATES = {
    "iv_base": {"what": "(iv) unchanged: the choice before the fix", "complexity": (2, 1, 1)},
    "v_level_tracking_by_type": {
        "what": "(iv)'s trees, with each interior level tracked separately by pressure-day type (four classes)",
        "partition": "by_type", "complexity": (2, 1, 4)},
    "vi_width_pooled": {
        "what": "(iv), then a pooled online width tracker on the 50% band", "partition": "pooled",
        "complexity": (3, 1, 1)},
    "vii_width_turn_vs_ordinary": {
        "what": "(iv), then an online width tracker on the 50% band per class: turn days and ordinary days",
        "partition": "turn_vs_ordinary", "complexity": (3, 1, 2)},
    "viii_width_by_type": {
        "what": "(iv), then an online width tracker on the 50% band per pressure-day type",
        "partition": "by_type", "complexity": (3, 1, 4)},
}
#: The width tracker. Each class has a log scale, starting at 0, that multiplies
#: q25 - q50 and q75 - q50 and moves by `rate * (0.5 - inside)` on each observable
#: label (`inside` counts an edge tie as one half): a band that covers less than
#: half widens, one that covers more narrows. The rate is chosen by nested
#: walk-forward selection at each refit block, as (i)'s step is.
WIDTH_RATES = (0.02, 0.05, 0.1, 0.2)
WIDTH_FALLBACK = 0.05
FIX_SELECTION = {
    "window": INNER_SELECTION["window"],
    "rule": ("#247's question 7 rule on the inner block, as `inner_choice` applies it under the binding reading "
             "(the bar and the conditional gates in eligibility): the eligible candidate with the lowest mean "
             "CRPS leads; a simpler eligible candidate whose paired CRPS interval against the leader includes 0 "
             "is preferred. Simplicity is `complexity`: layers added to v1, then output patches, then classes"),
    "diagnostic": "the per-day-type 50% bands are reported for every candidate and decide nothing (ruling of 14:24)",
    "outer": ("the outer block is scored a second time, once, for the chosen candidate, after it is committed "
              "as `CHOSEN_FIX`; the first look (for (iv)) is kept in the record"),
}


#: The fix the inner block chose (`choose-fix`, run on 6 October 2026), committed
#: before the outer block is scored a second time: (iv), then a width tracker on
#: the 50% band with one class for turn days and one for ordinary days. It has the
#: lowest inner CRPS of the eligible candidates, its CRPS gain over (iv) has a 90%
#: interval above 0, and the simpler candidates' intervals against it exclude 0.
CHOSEN_FIX = "vii_width_turn_vs_ordinary"


# ---------------------------------------------------------------------------
# The quarter-end location term (Eleonora's ruling on PR #252, 6 October 2026, 16:48)
# ---------------------------------------------------------------------------

#: The ruling: "build the quarter-end correction into v2 now". The width fix does not move the quarter-end
#: shortfall, which is a location shift (the realised median sits above the band on quarter-ends in 2018-19 and
#: the outer block). These candidates for a quarter-end location term are declared in one commit, before any of
#: them is walked or scored. They are chosen on the inner block only, by `QE_SELECTION`; the choice is committed
#: as `CHOSEN_QE_FIX` before the outer block is scored a third time. Every candidate is v2 as it stands (the trees
#: of depth `V2_TREE_SETTINGS`, the nested PID, the interior layer, the width layer) with one change to the trees.
#:
#: * (a) a calendar feature in the trees. `quarter_end` and `days_to_month_end` are `contract.CALENDAR_FEATURES`:
#:   panel columns, a function of the date, read at the scored day itself by the as-of rule, so they need no new
#:   code in `ml.py` and no new panel column. "Days to quarter-end on the market calendar"
#:   (`metadata/market_holidays.json`) as a column of its own would be a new calendar column in `data.py` and
#:   `contract.py` and a new panel digest; it is not built here (a question for Eleonora in the PR).
#: * (b) direct per-horizon training pairs (#105, `ml.TRAINING_PAIRS`): each target is paired with the as-of read
#:   a forecast of it makes, as the fit is served.
#: * (c) the simplest version of either: `qe_indicator` (one added column) and `direct_pairs` (the plain setting).
#:
#: Complexity is (changes to how the trees are trained, input columns added): changing how the trees are trained is
#: less simple than adding an input, and both are less simple than leaving the trees as they are.
QE_CANDIDATES = {
    "base": {"what": "v2 as it stands, with no quarter-end term (the choice before this ruling)",
             "features": (), "training_pairs": None, "complexity": (0, 0)},
    "qe_indicator": {"what": "a quarter-end indicator, `quarter_end`, added to the trees' features",
                     "features": ("quarter_end",), "training_pairs": None, "complexity": (0, 1)},
    "qe_indicator_and_month_end_countdown": {
        "what": ("the indicator and `days_to_month_end` (calendar days to the month's end: 0, 1, 2 on the days "
                 "before a quarter-end), both panel columns, added to the trees' features"),
        "features": ("quarter_end", "days_to_month_end"), "training_pairs": None, "complexity": (0, 2)},
    "direct_pairs": {"what": "the trees trained on direct per-horizon pairs (`training_pairs=\"direct\"`)",
                     "features": (), "training_pairs": "direct", "complexity": (1, 0)},
}
QE_SELECTION = {
    "window": INNER_SELECTION["window"],
    "rule": FIX_SELECTION["rule"],
    "unchanged": ("the pooled 90% gate stays pass/fail; the per-day-type 50% bands, quarter-end and year-end "
                  "included, are diagnostics with counts, and no interval under "
                  "`CONDITIONAL_GATES['minimum_days']` days ('too few days')"),
    "outer": ("the outer block is scored a third time, once, for the chosen candidate, after it is committed as "
              "`CHOSEN_QE_FIX`; the first and second looks are kept as they are"),
}


#: The quarter-end term the inner block chose (`choose-quarter-end`, run on 6 October 2026), committed before the
#: outer block is scored a third time. Under `QE_SELECTION` it is the leader (inner CRPS 1.799 against the base's
#: 1.828, paired gain +0.029 [+0.005, +0.052]) and the interval of each simpler eligible candidate against it
#: excludes 0, so none is preferred. The quarter-end indicator alone leaves v2's vectors unchanged (the trees never
#: split on it: 19 inner quarter-ends against `min_samples_leaf` 20). The choice does NOT move the quarter-end 50% band
#: (31.6% on 19 days, as before); the evidence for it is the pooled inner CRPS.
CHOSEN_QE_FIX = "qe_indicator_and_month_end_countdown"

THIRD_LOOK_LABEL = ("a third look at 2023-2025, scored once for v1 and the final v2 only (ruling of 6 October 2026, "
                    "16:48). The outer block has now been read three times: the first look, for (iv) before the "
                    "width fix, is `outer_block_before_fix`; the second, for v2 with the width fix, is "
                    "`outer_block_second_look`; both are kept as they were. The width fix and the quarter-end "
                    "term were each designed after an earlier look, so this block is no longer unseen by the "
                    "design, and every historical edge of v2 over v1 stays exploratory")


def candidate_setup(fit, features, name):
    """A quarter-end candidate's fitter and feature list, from the published side's.

    `fit` is the published side's `functools.partial` of
    `ml.fit_gradient_boosted_quantiles`, `features` its declared features. v2's
    trees are the same fitter with `ml`'s `max_depth` setting (`V2_TREE_SETTINGS`);
    the candidate adds its calendar columns to both lists, or its training
    pairs, and nothing else. No estimator class is replaced.
    """

    if name not in QE_CANDIDATES:
        raise ValueError(f"unknown quarter-end candidate {name!r}")
    spec = QE_CANDIDATES[name]
    extras = tuple(spec["features"])
    clash = sorted(set(extras) & set(features))
    if clash:
        raise ValueError(f"{clash} are already among the published features")
    keywords = dict(fit.keywords)
    keywords["regressors"] = tuple(keywords["regressors"]) + extras
    keywords.update(V2_TREE_SETTINGS)
    if spec["training_pairs"] is not None:
        keywords["training_pairs"] = spec["training_pairs"]
    return functools.partial(fit.func, *fit.args, **keywords), tuple(features) + extras



def _partition_class(partition, kind):
    if partition == "pooled":
        return "all"
    if partition == "turn_vs_ordinary":
        return "ordinary" if kind == "ordinary" else "turn"
    if partition == "by_type":
        return kind
    raise ValueError(f"unknown partition {partition!r}")


def _crps(vector, y):
    return crps_from_quantiles(LEVELS, vector, y)


def class_level_tracking(days, partition, *, steps=interior.INTERIOR_STEPS, fallback=interior.INTERIOR_FALLBACK,
                         refit_every=dx.REFIT_EVERY):
    """The reference for (v): `dx.interior_tracking`, each interior level tracked per class.

    `days` carry `date`, `anchor`, `y`, `issued` (the vector to move) and `kind`
    (the pressure-day type). With the `pooled` partition this is
    `dx.interior_tracking`'s own computation.
    """

    import bisect

    dates = [d["date"] for d in days]
    offsets = {}
    issued = {s: [] for s in steps}
    losses = {s: [] for s in steps}
    learned = 0
    chosen = fallback
    out, choices = [], []
    for j, d in enumerate(days):
        seen = bisect.bisect_right(dates, d["anchor"], 0, j)
        if seen < learned:
            raise ValueError("an anchor moved back")
        for k in range(learned, seen):
            y = days[k]["y"]
            klass = _partition_class(partition, days[k]["kind"])
            for s in steps:
                vector = issued[s][k]
                state = offsets.setdefault((s, klass), [0.0, 0.0, 0.0])
                for slot, i in enumerate(dx.INTERIOR):
                    state[slot] += s * (LEVELS[i] - interior.below_half_tie(y, vector[i]))
                losses[s].append(_crps(vector, y))
        learned = seen
        if j % refit_every == 0:
            chosen = min(steps, key=lambda s: (sum(losses[s][:seen]) / seen, s)) if seen else fallback
            choices.append({"first": d["date"], "step": chosen, "observable": seen})
        klass = _partition_class(partition, d["kind"])
        for s in steps:
            vector = list(d["issued"])
            state = offsets.get((s, klass), [0.0, 0.0, 0.0])
            for slot, i in enumerate(dx.INTERIOR):
                vector[i] += state[slot]
            issued[s].append(sorted(vector))
        out.append(issued[chosen][j])
    return out, choices


def _inside_half_band(y, vector):
    if _tied(y, vector[1]) or _tied(y, vector[3]):
        return 0.5
    return 1.0 if vector[1] < y < vector[3] else 0.0


def width_tracking(days, partition, *, rates=WIDTH_RATES, fallback=WIDTH_FALLBACK, refit_every=dx.REFIT_EVERY):
    """The reference for (vi) to (viii): the 50% band's width, tracked online per class (`FIX_CANDIDATES`).

    `days` carry `date`, `anchor`, `y`, `issued` (the vector to widen: (iv)'s) and
    `kind`. For each rate, each class keeps a log scale; the vector issued is
    `issued` with q25 and q75 moved to `q50 + scale * (q - q50)`, sorted. A day
    updates the scales of every rate once its label is observable at a later
    day's anchor, from the band that rate issued for it. The rate is chosen at
    the first day of each block of `refit_every` days by least pooled CRPS
    over the observable days, `fallback` while there are none.
    """

    import bisect
    import math

    dates = [d["date"] for d in days]
    log_scale = {}
    issued = {r: [] for r in rates}
    losses = {r: [] for r in rates}
    learned = 0
    chosen = fallback
    out, choices = [], []
    for j, d in enumerate(days):
        seen = bisect.bisect_right(dates, d["anchor"], 0, j)
        if seen < learned:
            raise ValueError("an anchor moved back")
        for k in range(learned, seen):
            y = days[k]["y"]
            klass = _partition_class(partition, days[k]["kind"])
            for r in rates:
                vector = issued[r][k]
                log_scale[(r, klass)] = log_scale.get((r, klass), 0.0) + r * (0.5 - _inside_half_band(y, vector))
                losses[r].append(_crps(vector, y))
        learned = seen
        if j % refit_every == 0:
            chosen = min(rates, key=lambda r: (sum(losses[r][:seen]) / seen, r)) if seen else fallback
            choices.append({"first": d["date"], "rate": chosen, "observable": seen})
        klass = _partition_class(partition, d["kind"])
        for r in rates:
            scale = math.exp(log_scale.get((r, klass), 0.0))
            vector = list(d["issued"])
            centre = vector[2]
            vector[1] = centre + (vector[1] - centre) * scale
            vector[3] = centre + (vector[3] - centre) * scale
            issued[r].append(sorted(vector))
        out.append(issued[chosen][j])
    return out, choices


def fix_vectors(days):
    """Each fix candidate's vectors on `days` (`date`, `anchor`, `y`, `pid`, `kind`), and its step or rate choices.

    (iv) is `class_level_tracking` over the `pooled` partition of the PID
    vectors; (vi) to (viii) move (iv)'s vectors by `width_tracking`.
    """

    on_pid = [dict(d, issued=d["pid"]) for d in days]
    base, base_choices = class_level_tracking(on_pid, "pooled")
    out = {"iv_base": (base, base_choices)}
    for name, spec in FIX_CANDIDATES.items():
        if name == "iv_base":
            continue
        if name == "v_level_tracking_by_type":
            out[name] = class_level_tracking(on_pid, spec["partition"])
        else:
            out[name] = width_tracking([dict(d, issued=v) for d, v in zip(days, base)], spec["partition"])
    return out


def _select_simplest(summaries, paired_to_leader, complexity):
    """The declared rule on eligible candidates' summaries: the lowest CRPS leads; a simpler candidate within its interval wins."""

    passing = sorted(summaries)
    if not passing:
        return {"recommended": None, "eligible": [], "leader": None, "reason": "no candidate is eligible"}
    leader = min(passing, key=lambda n: (summaries[n]["crps"], complexity[n], n))
    simpler = []
    for name in passing:
        if complexity[name] >= complexity[leader]:
            continue
        interval = paired_to_leader(name, leader)["interval"]
        if interval["lower"] <= 0.0 <= interval["upper"]:
            simpler.append(name)
    if simpler:
        chosen = min(simpler, key=lambda n: (complexity[n], summaries[n]["crps"], n))
        reason = (f"{leader} has the lowest CRPS of the eligible candidates; {chosen} is simpler and its "
                  f"CRPS difference against {leader} has a 90% interval including 0")
    else:
        chosen = leader
        reason = (f"{leader} has the lowest CRPS of the eligible candidates, and no simpler eligible "
                  f"candidate is within its interval")
    return {"recommended": chosen, "eligible": passing, "leader": leader, "reason": reason}


def select_fix(summaries, paired_to_leader):
    """`FIX_SELECTION`, applied to the eligible candidates' summaries."""

    return _select_simplest(summaries, paired_to_leader,
                            {name: FIX_CANDIDATES[name]["complexity"] for name in summaries})


def fix_choice(days, v1_days, cells, rows, splits) -> dict:
    """The fix, chosen on the inner block only (`FIX_SELECTION`).

    `days` are the inner block's days (`date`, `anchor`, `y`, `pid`, `kind`);
    `v1_days` the same days in #247's format, v1's vectors under `issued`.
    """

    if any(not _in(d["date"], INNER) for d in days):
        raise ValueError("the fix is chosen on the inner block only")
    vectors = fix_vectors(days)
    v1_vectors = [d["issued"] for d in v1_days]
    summaries, gates, candidates = {}, {}, {}
    for name, (vecs, choices) in vectors.items():
        summaries[name] = dx._summary(v1_days, vecs, INNER)
        gates[name] = conditional_gates(_with_cells(days, cells, "v", vecs), "v")
        candidates[name] = {
            "what": FIX_CANDIDATES[name]["what"],
            "partition": FIX_CANDIDATES[name].get("partition"),
            "complexity": list(FIX_CANDIDATES[name]["complexity"]),
            "inner": summaries[name],
            "conditional_gates_inner": gates[name],
            "paired_vs_v1_inner": dx.paired(v1_days, v1_vectors, vecs, rows, splits, INNER, ("#244", "fix", name, "v1")),
            "paired_vs_iv_inner": (None if name == "iv_base" else
                                   dx.paired(v1_days, vectors["iv_base"][0], vecs, rows, splits, INNER,
                                             ("#244", "fix", name, "iv"))),
            "band_by_day_type": {
                kind: band_coverage([{"y": d["y"], "v": v} for d, v in zip(days, vecs) if d["kind"] == kind], "v")
                for kind in sorted({d["kind"] for d in days})},
            "choices": choices,
        }
    pair_cache = {}

    def paired_to_leader(name, leader):
        if (name, leader) not in pair_cache:
            pair_cache[(name, leader)] = dx.paired(v1_days, vectors[leader][0], vectors[name][0], rows, splits,
                                                   INNER, ("#244", "fix", name, "vs", leader))
        return pair_cache[(name, leader)]

    eligible = {n: summaries[n] for n in vectors if eligible_inner(summaries[n], gates[n], reading=BINDING_READING)}
    selection = select_fix(eligible, paired_to_leader)
    return {
        "declared": {"candidates": FIX_CANDIDATES, "partitions": FIX_PARTITIONS, "selection": FIX_SELECTION,
                     "width_rates": list(WIDTH_RATES), "width_fallback": WIDTH_FALLBACK,
                     "reading": BINDING_READING},
        "window": [INNER[0].isoformat(), INNER[1].isoformat()],
        "days": len(days),
        "candidates": candidates,
        "selection": selection,
        "paired_against_leader": {f"{a}_vs_{b}": {k: v for k, v in p.items() if k != "splits"}
                                  for (a, b), p in pair_cache.items()},
        "vectors": {name: vecs for name, (vecs, _c) in vectors.items()},
    }


def select_quarter_end(summaries, paired_to_leader):
    """`QE_SELECTION`, applied to the eligible candidates' summaries."""

    return _select_simplest(summaries, paired_to_leader,
                            {name: QE_CANDIDATES[name]["complexity"] for name in summaries})


def with_day_types(days, rows, splits):
    """`days` with each day's pressure-day type under `type` (the split declaration's; a walk's `kind` is a width class)."""

    from repo_model.baseline import _split_labels

    _regimes, types = _split_labels(splits, rows, [date.fromisoformat(d["date"]) for d in days])
    return [dict(d, type=kind) for d, kind in zip(days, types)]


def quarter_end_choice(candidate_days, v1_days, cells, rows, splits) -> dict:
    """The quarter-end term, chosen on the inner block only (`QE_SELECTION`).

    `candidate_days` maps each candidate to its days (`date`, `anchor`, `y`,
    `type`, the pressure-day type, and `v2`, the vector of v2 built on that candidate's trees); every
    candidate walks the same days. `v1_days` is v1 on the same days in #247's
    format (`issued`). `cells` maps a date to its conditional cells. Refuses a
    day outside the inner block.
    """

    if not candidate_days or any(not _in(d["date"], INNER) for days in candidate_days.values() for d in days):
        raise ValueError("the quarter-end term is chosen on the inner block only")
    reference = candidate_days["base"]
    if any([(d["date"], d["y"]) for d in days] != [(d["date"], d["y"]) for d in reference]
           for days in candidate_days.values()):
        raise ValueError("the candidates' walks score different days")
    v1_vectors = [d["issued"] for d in v1_days]
    vectors = {name: [d["v2"] for d in days] for name, days in candidate_days.items()}
    summaries, gates, candidates = {}, {}, {}
    for name, vecs in vectors.items():
        summaries[name] = dx._summary(v1_days, vecs, INNER)
        gates[name] = conditional_gates(_with_cells(reference, cells, "v", vecs), "v")
        diagnostic = [{"date": d["date"], "y": d["y"], "v": v, "type": d["type"], "cells": set(cells[d["date"]])}
                      for d, v in zip(reference, vecs)]
        candidates[name] = {
            "what": QE_CANDIDATES[name]["what"],
            "features_added": list(QE_CANDIDATES[name]["features"]),
            "training_pairs": QE_CANDIDATES[name]["training_pairs"],
            "complexity": list(QE_CANDIDATES[name]["complexity"]),
            "inner": summaries[name],
            "conditional_gates_inner": gates[name],
            "paired_vs_v1_inner": dx.paired(v1_days, v1_vectors, vecs, rows, splits, INNER, ("#244", "qe", name, "v1")),
            "paired_vs_base_inner": (None if name == "base" else
                                     dx.paired(v1_days, vectors["base"], vecs, rows, splits, INNER,
                                               ("#244", "qe", name, "base"))),
            "by_day_type": {
                cell: _diagnostic_cell([d for d in diagnostic if _cell_members(d)[cell]], "v", ("qe", name, cell))
                for cell in ("all", "quarter_end", "year_end", "tax_date", "month_end", "ordinary")},
        }
    pair_cache = {}

    def paired_to_leader(name, leader):
        if (name, leader) not in pair_cache:
            pair_cache[(name, leader)] = dx.paired(v1_days, vectors[leader], vectors[name], rows, splits, INNER,
                                                   ("#244", "qe", name, "vs", leader))
        return pair_cache[(name, leader)]

    eligible = {n: summaries[n] for n in vectors if eligible_inner(summaries[n], gates[n], reading=BINDING_READING)}
    selection = select_quarter_end(eligible, paired_to_leader)
    return {
        "declared": {"candidates": QE_CANDIDATES, "selection": QE_SELECTION, "tree_settings": V2_TREE_SETTINGS,
                     "reading": BINDING_READING},
        "window": [INNER[0].isoformat(), INNER[1].isoformat()],
        "days": len(reference),
        "candidates": candidates,
        "selection": selection,
        "paired_against_leader": {f"{a}_vs_{b}": {k: v for k, v in p.items() if k != "splits"}
                                  for (a, b), p in pair_cache.items()},
        "vectors": vectors,
    }


def _cell_members(day) -> dict:
    kind = day["type"]
    return {
        "all": True,
        "quarter_end": kind == "quarter_end",
        "year_end": kind == "quarter_end" and day["date"][5:7] == "12",
        "tax_date": kind == "tax_date",
        "month_end": kind == "month_end",
        "coupon_settlement": "coupon_settlement" in day["cells"],
        "scarce": "scarce" in day["cells"],
        "ordinary": kind == "ordinary",
    }


def _diagnostic_cell(days, field, seed_parts) -> dict:
    n = len(days)
    out = {"days": n}
    if not n:
        return out
    cov = band_coverage(days, field)
    centre = sorted(d["y"] - d[field][2] for d in days)
    if n < CONDITIONAL_GATES["minimum_days"]:
        # The minimum-cell rule (ruling of 6 October 2026, 16:48): no interval under the minimum.
        band_50 = {"coverage": cov["band_50_half_edge"], "interval": "too few days"}
        band_90 = {"coverage": cov["band_90_half_edge"], "interval": "too few days"}
    else:
        interval = coverage_interval(days, field, seed_parts)
        band_50 = {"coverage": cov["band_50_half_edge"], "lower": interval["band_50"]["lower"],
                   "upper": interval["band_50"]["upper"]}
        band_90 = {"coverage": cov["band_90_half_edge"], "lower": interval["band_90"]["lower"],
                   "upper": interval["band_90"]["upper"]}
    out.update(
        band_50=band_50,
        band_90=band_90,
        p_below={level: cov["coverage_half_tie"][level] for level in ("0.25", "0.5", "0.75")},
        band_50_miss_below=cov["band_50_miss_below"],
        band_50_miss_above=cov["band_50_miss_above"],
        mean_y_minus_q50_bps=statistics.fmean(centre),
        median_y_minus_q50_bps=statistics.median(centre),
        median_abs_y_minus_q50_bps=statistics.median(abs(c) for c in centre),
        band_50_mean_width_bps=cov["band_50_mean_width_bps"],
    )
    return out


def inner_diagnosis(days, fields, regimes) -> dict:
    """`DIAGNOSIS`: each model in `fields` by pressure-day type and by regime, on the inner block.

    `days` carry `date`, `y`, one vector per field, `type`, `reporting_type`,
    `regime` and `cells`.
    """

    if any(not _in(d["date"], INNER) for d in days):
        raise ValueError("the diagnosis reads the inner block only")
    out = {"declared": DIAGNOSIS, "days": len(days), "models": {}}
    for field, label in fields.items():
        by_cell = {}
        for cell in DIAGNOSIS["cells"]:
            subset = [d for d in days if _cell_members(d)[cell]]
            by_cell[cell] = _diagnostic_cell(subset, field, ("diagnosis", field, cell))
        by_regime = {}
        for regime in regimes:
            subset = [d for d in days if d["regime"] == regime]
            by_regime[regime] = _diagnostic_cell(subset, field, ("diagnosis", field, "regime", regime))
        by_regime_and_type = {}
        for regime in regimes:
            for kind in ("quarter_end", "tax_date", "month_end", "ordinary"):
                subset = [d for d in days if d["regime"] == regime and d["type"] == kind]
                by_regime_and_type[f"{regime} / {kind}"] = _diagnostic_cell(
                    subset, field, ("diagnosis", field, regime, kind))
        by_reporting = {}
        for kind in ("quarter_end", "tax_date", "month_end", "ordinary"):
            subset = [d for d in days if d["reporting_type"] == kind]
            by_reporting[kind] = _diagnostic_cell(subset, field, ("diagnosis", field, "reporting", kind))
        out["models"][field] = {"label": label, "by_cell": by_cell, "by_regime": by_regime,
                                "by_regime_and_day_type": by_regime_and_type,
                                "by_reporting_day_type": by_reporting}
    return out


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
    fit, features = candidate_setup(fit, features, args.candidate)
    built = []

    def v2_online(rows_, rule):
        calibration = interior.NestedInteriorFoldPid(
            rows_, rule, splits=load_splits(fp.SPLITS), refit_every=parsed.refit_every, width_layer=True)
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
                     "y": rows[index].spread_bps, "pid": list(d.pid), "tracked": list(d.tracked),
                     "kind": d.kind, "v2": list(d.vector)})
    account = calibration.account()
    document = {"directive": "#244", "horizon": h, "panel_sha256": panel_sha256(args.panel),
                "model": name, "settings": settings, "tree_settings": V2_TREE_SETTINGS,
                "candidate": args.candidate, "features": list(features),
                "interior_blocks": account["interior_blocks"], "width_blocks": account["width_blocks"],
                "days": days}
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
        if document.get("tree_settings") != V2_TREE_SETTINGS:
            raise ValueError(f"{path} was not walked with v2's trees")
        if document.get("candidate") != CHOSEN_QE_FIX:
            raise ValueError(f"{path} was walked for {document.get('candidate')!r}, not for CHOSEN_QE_FIX")
        walks[document["horizon"]] = document
    candidate_walks = {}
    for path in args.candidate_walks:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["panel_sha256"] != panel_sha256(args.panel) or document["horizon"] != 1:
            raise ValueError(f"{path} is not a candidate walk at h = 1 on the published panel")
        if document.get("tree_settings") != V2_TREE_SETTINGS:
            raise ValueError(f"{path} was not walked with v2's trees")
        candidate_walks[document["candidate"]] = document
    if set(candidate_walks) != set(QE_CANDIDATES):
        raise ValueError(f"the candidate walks are for {sorted(candidate_walks)}, not {sorted(QE_CANDIDATES)}")
    if candidate_walks[CHOSEN_QE_FIX]["days"] != walks[1]["days"]:
        raise ValueError("CHOSEN_QE_FIX's candidate walk is not the walk the record is assembled from")
    base_days = candidate_walks["base"]["days"]

    # v1 at each horizon is its own walk (#247's, unchanged trees), joined by date.
    v1_walks = {}
    for path in args.variant_walks:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["variant"] == "v1":
            if document["panel_sha256"] != panel_sha256(args.panel):
                raise ValueError(f"{path} was walked on another panel")
            v1_walks[document["horizon"]] = document["days"]
    for h, document in walks.items():
        if h not in v1_walks:
            raise ValueError(f"no v1 walk at h = {h}")
        if [(d["date"], d["y"]) for d in document["days"]] != [(e["date"], e["y"]) for e in v1_walks[h]]:
            raise ValueError(f"v1's and v2's walks at h = {h} score different days")
        for d, e in zip(document["days"], v1_walks[h]):
            d["v1"] = e["issued"]
    days = walks[1]["days"]

    # v1 untouched: #247's vectors to the byte, and the published CRPS exactly.
    diagnosis = json.loads(DIAGNOSIS_RECORD.read_text(encoding="utf-8"))
    before = [[day, vector] for day, _y, vector in diagnosis["v1_h1_per_day"]]
    ours = [[d["date"], d["v1"]] for d in days]
    if vectors_sha256(ours) != vectors_sha256(before):
        raise ValueError("v1's vectors differ from #247's walk")
    dx.reproduction_check([{"date": d["date"], "y": d["y"], "issued": d["v1"]} for d in days])

    # The interior layer is #247's reference implementation of (iv): (i)'s tracking applied to (ii)'s PID
    # vectors; v2 is the width reference over it, by the chosen fix's partition.
    reference, choices = dx.interior_tracking(
        [{"date": d["date"], "anchor": d["anchor"], "y": d["y"], "issued": d["pid"]} for d in days])
    if [d["tracked"] for d in days] != reference:
        raise ValueError("the interior layer's vectors differ from #247's reference implementation")
    fix_partition = FIX_CANDIDATES[CHOSEN_FIX]["partition"]
    widened, width_choices = width_tracking(
        [{"date": d["date"], "anchor": d["anchor"], "y": d["y"], "issued": d["tracked"], "kind": d["kind"]}
         for d in days], fix_partition)
    if [d["v2"] for d in days] != widened:
        raise ValueError("v2's vectors differ from the width reference implementation")

    persistence = persistence_losses()
    if set(persistence) != {d["date"] for d in days}:
        raise ValueError("the persistence records and the walk score different days")
    decides = [d for d in days if _in(d["date"], DECIDES)]
    check = [d for d in days if _in(d["date"], CHECK)]

    # The choice, redone on the inner block; it must be the candidate committed as CHOSEN.
    variant_walks = _variant_walks(args.variant_walks, args.panel)
    v1_walk = variant_walks.pop("v1")
    if [[d["date"], d["issued"]] for d in v1_walk] != ours:
        raise ValueError("#247's v1 walk and v2's walk carry different v1 vectors")
    cells = _cells_through_outer(rows, v1_walk)
    choice = inner_choice(v1_walk, variant_walks, rows, splits, cells)
    chosen_vectors = choice.pop("vectors")
    picks = {reading: choice["selection"][reading]["recommended"] for reading in READINGS}
    if picks[BINDING_READING] != CHOSEN:
        raise ValueError(f"the inner block chooses {picks}; CHOSEN is {CHOSEN!r}")
    if chosen_vectors[CHOSEN] != [d["tracked"] for d in base_days]:
        raise ValueError("the interior layer's vectors are not the chosen candidate's")
    # The depth-3 setting of `ml` gives the trees #247's walk gave by replacing the estimator class.
    if [d["issued"] for d in variant_walks[V2_TREE_VARIANT]] != [d["pid"] for d in base_days]:
        raise ValueError("v2's trees and PID are not #247's walk of its tree setting")

    # The fix, chosen on the inner block only; it must be the candidate committed as CHOSEN_FIX.
    before_fix = json.loads(args.before_fix_record.read_text(encoding="utf-8"))
    inner_days, _inner_cells = inner_days_from_record(
        {"anchors": [[d["date"], d["anchor"]] for d in base_days],
         "per_day_h1": {"rows": [[d["date"], d["y"], d["pid"], d["tracked"]] for d in base_days]}}, rows, splits)
    v1_inner = [{"date": d["date"], "anchor": d["anchor"], "y": d["y"], "issued": d["v1"]} for d in inner_days]
    fix = fix_choice(inner_days, v1_inner, cells, rows, splits)
    fix_candidate_vectors = fix.pop("vectors")
    if fix["selection"]["recommended"] != CHOSEN_FIX:
        raise ValueError(f"the inner block chooses {fix['selection']['recommended']!r}; CHOSEN_FIX is {CHOSEN_FIX!r}")
    inner_base = [d for d in base_days if _in(d["date"], INNER)]
    inner_final = [d for d in days if _in(d["date"], INNER)]
    if fix_candidate_vectors[CHOSEN_FIX] != [d["v2"] for d in inner_base]:
        raise ValueError("the base walk's inner vectors are not the chosen fix's")
    if fix_candidate_vectors["iv_base"] != [d["tracked"] for d in inner_base]:
        raise ValueError("(iv)'s inner vectors are not the walk's interior layer")
    first_look = {row[0]: row[3] for row in before_fix["per_day_h1"]["rows"]}
    if any(first_look[d["date"]] != d["tracked"] for d in base_days if d["date"] in first_look):
        raise ValueError("the interior layer differs from the record as it stood before the fix")
    for d, e, f in zip(inner_days, inner_base, inner_final):
        d["fixed"] = e["v2"]
        d["final"] = f["v2"]

    # The quarter-end term, chosen on the inner block only; it must be the candidate committed as CHOSEN_QE_FIX.
    qe_inner = {name: with_day_types([d for d in doc["days"] if _in(d["date"], INNER)], rows, splits)
                for name, doc in candidate_walks.items()}
    qe = quarter_end_choice(qe_inner, v1_inner, cells, rows, splits)
    qe_vectors = qe.pop("vectors")
    if qe["selection"]["recommended"] != CHOSEN_QE_FIX:
        raise ValueError(f"the inner block chooses {qe['selection']['recommended']!r}; CHOSEN_QE_FIX is "
                         f"{CHOSEN_QE_FIX!r}")
    if qe_vectors[CHOSEN_QE_FIX] != [d["v2"] for d in inner_final] or qe_vectors["base"] != [d["v2"] for d in inner_base]:
        raise ValueError("the quarter-end choice's vectors are not the walks'")
    diagnosis_block = inner_diagnosis(
        inner_days, {"v1": "v1", "iv": "v2 before the fix: (iv)", "fixed": "v2 after the width fix, no quarter-end term",
                     "final": f"v2 with the quarter-end choice: {CHOSEN_QE_FIX}"},
        splits.regime_labels)

    def validation_block(window, label):
        sub = [d for d in days if _in(d["date"], window)]
        block = window_block(sub, rows, splits, persistence, label)
        block["crps"]["v2_vs_v1"]["edge_label"] = EXPLORATORY
        block["bar"] = bar_verdict(block["coverage"], block["crps"]["v2_vs_v1"])
        block["conditional_gates"] = conditional_gates(_with_cells(sub, cells, "v2"), "v2")
        block["conditional_gates_v1"] = conditional_gates(_with_cells(sub, cells, "v1"), "v1")
        return block

    inner_block = validation_block(INNER, "inner")
    outer_block = validation_block(OUTER, "outer")
    outer_block["label"] = (THIRD_LOOK_LABEL)
    looks = json.loads(args.second_look_record.read_text(encoding="utf-8"))
    first_outer, second_outer = looks["outer_block_before_fix"], looks["outer_block"]
    if "first look" not in first_outer["label"] or "second look" not in second_outer["label"]:
        raise ValueError("--second-look-record does not carry the first and second looks")
    outer_days = [d for d in days if _in(d["date"], OUTER)]
    outer_base = [d for d in base_days if _in(d["date"], OUTER)]
    outer_scored = [date.fromisoformat(d["date"]) for d in outer_days]
    from repo_model.baseline import _split_labels

    _regimes, outer_types = _split_labels(splits, rows, outer_scored)
    outer_diag = [{"date": d["date"], "y": d["y"], "v1": d["v1"], "base": b["v2"], "v2": d["v2"], "type": kind,
                   "cells": set(cells[d["date"]])} for d, b, kind in zip(outer_days, outer_base, outer_types)]
    outer_diagnosis = {"label": ("diagnostics only, outer block, third look: counts and intervals per day type; "
                                 "no interval under the minimum-cell rule ('too few days')"),
                       "models": {}}
    for field, label in (("v1", "v1"), ("base", "v2 before the quarter-end term"), ("v2", "v2 final")):
        outer_diagnosis["models"][field] = {"label": label, "by_cell": {
            cell: _diagnostic_cell([d for d in outer_diag if _cell_members(d)[cell]], field, ("outer", field, cell))
            for cell in ("all", "quarter_end", "year_end", "tax_date", "month_end", "ordinary")}}

    main_block = window_block(decides, rows, splits, persistence, "2018-2025")
    main_block["bar"] = bar_verdict(main_block["coverage"], main_block["crps"]["v2_vs_v1"])
    main_block["crps"]["v2_vs_v1"]["edge_label"] = EXPLORATORY
    main_block["label"] = ("pooled 2018-2025, the window #247 diagnosed, tuned and chose on: exploratory, "
                           "superseded as evidence by the inner and outer blocks")
    check_block = window_block(check, rows, splits, persistence, "2026")
    check_block["label"] = CHECK_LABEL
    check_block["coverage_interval"] = coverage_interval(check, "v2", ("2026", "v2"))
    check_block["coverage_interval_v1"] = coverage_interval(check, "v1", ("2026", "v1"))
    check_block["gate"] = gate_verdict(check_block["coverage_interval"], check_block["crps"]["v2_vs_v1"])

    outer_moved = sum(1 for d in days if d["v2"][0] != d["pid"][0] or d["v2"][4] != d["pid"][4])
    record = {
        "record": "pressure_model_v2_distribution_h1",
        "directive": "#244",
        "descriptive": ("v2 against v1 and as-of persistence at h = 1. It changes no published figure: "
                        "whether v2 joins the live record is Eleonora's decision (#245)"),
        "model": {
            "name": "pressure model v2 (distribution)",
            "built_from": ("#247's candidate (iv), chosen again on the inner block (ruling on PR #252): "
                           "v1's features, fold grid and nested PID on trees of maximum depth 3, with "
                           "each interior level tracked online; then the fix chosen on the inner block "
                           "(rulings of 14:02 and 14:24): an online width tracker on the 50% band, one "
                           "class for turn days and one for ordinary days; then the quarter-end term chosen "
                           f"on the inner block (ruling of 16:48): {CHOSEN_QE_FIX}"),
            "v1": walks[1]["model"],
            "settings": walks[1]["settings"],
            "tree_settings": V2_TREE_SETTINGS,
            "quarter_end_candidate": CHOSEN_QE_FIX,
            "features": walks[1]["features"],
            "code": ("src/repo_model/interior.py (NestedInteriorFoldPid); the tree setting is applied as "
                     "#247's walk applies it (scripts/interior_diagnosis._with_tree_settings)"),
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
        "per_day_h1": {"columns": ["date", "y", "pid_of_v2_trees", "interior_tracked", "v2"],
                       "rows": [[d["date"], d["y"], d["pid"], d["tracked"], d["v2"]] for d in days]},
        "width_classes_per_day": [[d["date"], d["kind"]] for d in days],
        "days_the_sort_moved_an_outer_quantile": outer_moved,
        "interior_step_choices": walks[1]["interior_blocks"],
        "width_rate_choices": walks[1]["width_blocks"],
        "outer_validation_declared": {"inner": [INNER[0].isoformat(), INNER[1].isoformat()],
                                      "outer": [OUTER[0].isoformat(), OUTER[1].isoformat()],
                                      "inner_selection": INNER_SELECTION,
                                      "conditional_gates": CONDITIONAL_GATES,
                                      "chosen": CHOSEN,
                                      "diagnosis": DIAGNOSIS,
                                      "fix": {"candidates": FIX_CANDIDATES, "partitions": FIX_PARTITIONS,
                                              "selection": FIX_SELECTION, "chosen": CHOSEN_FIX,
                                              "width_rates": list(WIDTH_RATES),
                                              "width_fallback": WIDTH_FALLBACK},
                                      "quarter_end": {"candidates": QE_CANDIDATES, "selection": QE_SELECTION,
                                                      "chosen": CHOSEN_QE_FIX},
                                      "historical_edge_label": EXPLORATORY},
        "quarter_end_choice": qe,
        "inner_choice": choice,
        "inner_diagnosis": diagnosis_block,
        "fix_choice": fix,
        "inner_block": inner_block,
        "outer_block": outer_block,
        "outer_block_before_fix": first_outer,
        "outer_block_second_look": second_outer,
        "outer_diagnosis": outer_diagnosis,
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
    print(json.dumps({"chosen": CHOSEN, "bar_2018_2025": main_block["bar"], "gate_2026": check_block["gate"],
                      **{name: {"bar": block["bar"],
                                "conditional_gates": {k: g["verdict"] for k, g in block["conditional_gates"].items()}}
                         for name, block in (("inner", inner_block), ("outer", outer_block))}}, indent=1))
    return 0


def _variant_walks(paths, panel):
    walks = {}
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["panel_sha256"] != panel_sha256(panel):
            raise ValueError(f"{path} was walked on another panel")
        if document["horizon"] == 1:
            walks[document["variant"]] = document["days"]
    missing = sorted(set(dx.VARIANTS) - set(walks))
    if missing:
        raise ValueError(f"missing #247 walks: {missing}")
    return walks


def _cells_through_outer(rows, days):
    return day_cells(rows, [date.fromisoformat(d["date"]) for d in days if _in(d["date"], (DECIDES[0], OUTER[1]))])


def choose_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    walks = _variant_walks(args.walks, args.panel)
    v1_days = walks.pop("v1")
    dx.reproduction_check(v1_days)
    cells = _cells_through_outer(rows, v1_days)
    choice = inner_choice(v1_days, walks, rows, load_split_declaration(fp.SPLITS), cells)
    choice.pop("vectors")
    args.output.write_text(json.dumps(choice, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ii_setting": choice["ii_setting"], "selection": choice["selection"]}, indent=1))
    return 0


def inner_days_from_record(record, rows, splits):
    """The inner block's days, from a record's per-day rows, with v1's vectors and each day's labels.

    Reads the inner block only. A day carries `pid` (the depth-3 trees' nested
    PID vector), `iv` ((iv)'s vector, the record's before the fix), `v1`, its pressure-day type
    (`type`, also `kind`), the type under #278's reporting split, its regime and
    its conditional-gate cells.
    """

    from repo_model.baseline import _split_labels

    anchors = dict(record["anchors"])
    diagnosis = json.loads(DIAGNOSIS_RECORD.read_text(encoding="utf-8"))
    v1 = {day: vector for day, _y, vector in diagnosis["v1_h1_per_day"]}
    # The first column after the PID vector is (iv)'s vector: the record's `v2` before the fix, its `interior_tracked` after it.
    days = [{"date": day, "anchor": anchors[day], "y": y, "pid": pid, "iv": row[0], "v1": v1[day]}
            for day, y, pid, *row in record["per_day_h1"]["rows"] if _in(day, INNER)]
    scored = [date.fromisoformat(d["date"]) for d in days]
    regimes, types = _split_labels(splits, rows, scored)
    cells = day_cells(rows, scored)
    by_date = {row.date: row for row in rows}
    for d, when, regime, kind in zip(days, scored, regimes, types):
        d.update(regime=regime, type=kind, kind=kind, cells=set(cells[d["date"]]),
                 reporting_type=splits.reporting_day_type(when, by_date[when].values))
    return days, cells


def _inner_inputs(args):
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(fp.SPLITS)
    record = json.loads(args.before_fix_record.read_text(encoding="utf-8"))
    days, cells = inner_days_from_record(record, rows, splits)
    return rows, splits, days, cells


def diagnose_command(args) -> int:
    rows, splits, days, _cells = _inner_inputs(args)
    result = inner_diagnosis(days, {"v1": "v1", "iv": "v2 before the fix: (iv)"}, splits.regime_labels)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"days": result["days"]}))
    return 0


def choose_fix_command(args) -> int:
    rows, splits, days, cells = _inner_inputs(args)
    v1_days = [{"date": d["date"], "anchor": d["anchor"], "y": d["y"], "issued": d["v1"]} for d in days]
    result = fix_choice(days, v1_days, cells, rows, splits)
    result.pop("vectors")
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"selection": result["selection"]}, indent=1))
    return 0


def choose_quarter_end_command(args) -> int:
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    splits = load_split_declaration(fp.SPLITS)
    candidate_days = {}
    for path in args.walks:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["panel_sha256"] != panel_sha256(args.panel):
            raise ValueError(f"{path} was walked on another panel")
        if document["horizon"] != 1 or document.get("tree_settings") != V2_TREE_SETTINGS:
            raise ValueError(f"{path} is not a v2 walk at h = 1")
        # The walk reaches past the inner block; the choice reads the inner block's days and no others.
        candidate_days[document["candidate"]] = with_day_types(
            [d for d in document["days"] if _in(d["date"], INNER)], rows, splits)
    if set(candidate_days) != set(QE_CANDIDATES):
        raise ValueError(f"the walks are for {sorted(candidate_days)}, not {sorted(QE_CANDIDATES)}")
    v1 = json.loads(args.v1_walk.read_text(encoding="utf-8"))
    if v1["variant"] != "v1" or v1["horizon"] != 1 or v1["panel_sha256"] != panel_sha256(args.panel):
        raise ValueError(f"{args.v1_walk} is not v1's walk at h = 1 on the published panel")
    v1_days = [d for d in v1["days"] if _in(d["date"], INNER)]
    scored = [date.fromisoformat(d["date"]) for d in candidate_days["base"]]
    cells = day_cells(rows, scored)
    result = quarter_end_choice(candidate_days, v1_days, cells, rows, splits)
    result.pop("vectors")
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=_plain) + "\n", encoding="utf-8")
    print(json.dumps({"selection": result["selection"]}, indent=1))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    wk = sub.add_parser("walk", help="the published side's walk with v2's calibration")
    wk.add_argument("--panel", type=Path, required=True)
    wk.add_argument("--horizon", type=int, choices=dx.HORIZONS, default=1)
    wk.add_argument("--candidate", choices=sorted(QE_CANDIDATES), default="base",
                    help="the quarter-end candidate whose trees v2 is built on (QE_CANDIDATES)")
    wk.add_argument("--output", type=Path, required=True)
    wk.set_defaults(func=walk_command)
    ch = sub.add_parser("choose", help="#247's choice, redone on the inner block (ruling on PR #252)")
    ch.add_argument("--panel", type=Path, required=True)
    ch.add_argument("--walks", type=Path, nargs="+", required=True, help="#247's h = 1 walks, v1 and every variant")
    ch.add_argument("--output", type=Path, required=True)
    ch.set_defaults(func=choose_command)
    dg = sub.add_parser("diagnose", help="v1 and v2 before the fix, by pressure-day type and regime, inner block only")
    dg.add_argument("--panel", type=Path, required=True)
    dg.add_argument("--before-fix-record", type=Path, required=True, help="the record as it stood before the fix")
    dg.add_argument("--output", type=Path, required=True)
    dg.set_defaults(func=diagnose_command)
    cf = sub.add_parser("choose-fix", help="the fix, chosen on the inner block only")
    cf.add_argument("--panel", type=Path, required=True)
    cf.add_argument("--before-fix-record", type=Path, required=True)
    cf.add_argument("--output", type=Path, required=True)
    cf.set_defaults(func=choose_fix_command)
    cq = sub.add_parser("choose-quarter-end", help="the quarter-end term, chosen on the inner block only")
    cq.add_argument("--panel", type=Path, required=True)
    cq.add_argument("--walks", type=Path, nargs="+", required=True, help="every candidate's v2 walk at h = 1")
    cq.add_argument("--v1-walk", type=Path, required=True, help="#247's v1 walk at h = 1")
    cq.add_argument("--output", type=Path, required=True)
    cq.set_defaults(func=choose_quarter_end_command)
    asm = sub.add_parser("assemble", help="the record, from the walks")
    asm.add_argument("--panel", type=Path, required=True)
    asm.add_argument("--walks", type=Path, nargs="+", required=True)
    asm.add_argument("--variant-walks", type=Path, nargs="+", required=True,
                     help="#247's walks: v1 and every variant at h = 1, and v1 at h = 2 to 5")
    asm.add_argument("--candidate-walks", type=Path, nargs="+", required=True,
                     help="every quarter-end candidate's v2 walk at h = 1")
    asm.add_argument("--second-look-record", type=Path, required=True,
                     help="the record as it stood at the second look: its first and second looks at the outer block")
    asm.add_argument("--before-fix-record", type=Path, required=True,
                     help="the record as it stood before the fix: its (iv) vectors and its first look at the outer block")
    asm.add_argument("--output", type=Path, default=RECORD)
    asm.set_defaults(func=assemble_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
