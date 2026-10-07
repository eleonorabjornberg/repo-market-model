"""Quarter-end remedies layered on pressure model v2 (#327), reported only.

v2 ships without a quarter-end term (PR #252: the declared rule's choice), and its 50% band covers about
30% of quarter-end days. The trees cannot learn the turn from 23 days (#252), so every remedy here is a
turn layer on v2's own vectors, estimated across every earlier quarter-end, with no trees. A remedy changes
quarter-end days only. It does not change v2 or any published record; whether it joins v2 is Eleonora's
decision (the "Publish?" issue of #327).

Declared in one commit before anything was scored (`CANDIDATES`, `SELECTION`, the blocks). The choice is
made on the inner block, 2018-06-29 to 2022-12-31, and committed as `CHOSEN_REMEDY` before 2023-2025 is
read. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`): `require_read_window` refuses one.

Three subcommands, each writing JSON:

    PYTHONPATH=src python3 scripts/quarter_end_remedy.py diagnose --panel PUB.csv --output OUT/diagnosis.json
    PYTHONPATH=src python3 scripts/quarter_end_remedy.py choose   --panel PUB.csv --output OUT/choice.json
    PYTHONPATH=src python3 scripts/quarter_end_remedy.py report   --panel PUB.csv --output OUT/report.json

`PUB.csv` is the published panel (`docs/pivot/next-session.md`); the script reads v2's per-day vectors from
`docs/runs/pressure_model_v2_distribution_h1.json` through 2025-12-31 and no later row. The script needs
nothing beyond the standard library and `repo_model`.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import interior, onset  # noqa: E402
from repo_model.baseline import _split_labels, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
RECORD = REPO / "docs" / "runs" / "pressure_model_v2_distribution_h1.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
BLOCK_LENGTH = 2  # the stationary bootstrap's mean block length, as the final test and #244
MINIMUM_CELL = 20  # a cell under this has no interval: "too few days" (ruling of 6 October 2026)

#: The blocks. The choice reads the inner block only; the outer block is a labelled look, read after the
#: choice is committed. The lockbox's near-blind tier starts on 2026-01-01.
INNER = (date(2018, 6, 29), date(2022, 12, 31))
OUTER = (date(2023, 1, 1), date(2025, 12, 31))
LAST_READ = date(2025, 12, 31)

#: Declared before scoring. A remedy moves a quarter-end day's vector by an estimate from the quarter-ends
#: whose labels were public at that day's anchor. `MIN_PAST` is the fewest past quarter-ends an estimate
#: needs (one year); with fewer the vector is v2's. `POOL_WEIGHT` is the pseudo-count with which the
#: month-end median is pooled into the quarter-end one.
MIN_PAST = 4
MIN_PAST_EMPIRICAL = 8
POOL_MIN_MONTH_ENDS = 8
POOL_WEIGHT = 4
RECENT = 4  # the `_recent` remedies read the last four quarter-ends public at the anchor (the last year)

CANDIDATES = {
    "base": {"what": "v2 as it stands, with no quarter-end remedy", "complexity": 0},
    "qe_shift": {
        "what": ("a location shift: every quantile moves by the median of (y - q50) over the earlier "
                 "quarter-ends"),
        "complexity": 1},
    "turn_pool": {
        "what": ("the shift pooled with the month-end turns: (n_q * median_qe + k * median_me) / (n_q + k) with "
                 f"k = {POOL_WEIGHT}, where median_me is the median of (y - q50) over earlier month-end days "
                 "(not quarter-ends), a size term for the quarter-end's excess"),
        "complexity": 2},
    "qe_shift_width": {
        "what": ("the shift, and a widening of the band about the shifted median by max(1, median |e - shift| / "
                 "median half-IQR) over the earlier quarter-ends, e = y - q50 and half-IQR = (q75 - q25) / 2, "
                 "the factor that would have made the earlier quarter-ends' 50% band right"),
        "complexity": 2},
    "qe_shift_recent": {
        "what": ("`qe_shift` on the last four quarter-ends public at the anchor only, added after the diagnosis "
                 "showed the quarter-end bias changing sign by regime (+21 bp median in 2018-19, about -10 bp "
                 "in 2021-22), so that an all-history median carries one regime's bias into the next. Declared "
                 "before any candidate was scored"),
        "complexity": 1},
    "qe_shift_width_recent": {
        "what": "`qe_shift_width` on the last four quarter-ends public at the anchor only (reason as `qe_shift_recent`)",
        "complexity": 2},
    "qe_empirical": {
        "what": ("a separate small quarter-end model: every level is v2's q50 plus the empirical quantile, at that "
                 "level, of the earlier quarter-ends' (y - q50), once there are 8"),
        "complexity": 5},
}

#: A remedy that needs a new panel column is a new panel digest, so it is declared and not built.
NOT_BUILT = {
    "days_to_quarter_end_market_calendar": (
        "'days to quarter-end on the market calendar' as a panel column of its own (`metadata/market_holidays.json`) "
        "is a new calendar column in `data.py` and `contract.py` and a new panel digest, which is her decision; "
        "`quarter_end` and `days_to_month_end` are the calendar's columns today"),
}

SELECTION = {
    "window": "2018-06-29 to 2022-12-31 (`INNER`), h = 1",
    "rule": ("every candidate is v2 with one remedy on quarter-end days, so only those days differ from `base`. "
             "The candidate with the lowest pooled inner CRPS among the eligible leads; a simpler eligible "
             "candidate (fewer estimated quantities: `complexity`) is chosen instead when the 90% interval "
             "of its paired CRPS difference against the leader includes 0"),
    "eligible": ("the paired CRPS gain over `base` on the inner block is above 0, and the remedy changed no day "
                 "that is not a quarter-end"),
    "none_eligible": "`base` is chosen: no remedy is adopted, and the look at 2023-2025 reports every candidate",
    "interval": "stationary bootstrap, mean block length 2, 90%",
    "cells": ("quarter-end, year-end, tax-date, month-end and ordinary cells are reported, with an interval "
              f"only from {MINIMUM_CELL} days ('too few days' below)"),
    "outer": ("2023-2025 is read once after the choice is committed as `CHOSEN_REMEDY`, and labelled a look: "
              "the inner block chose, the outer block did not"),
}

#: The remedy the inner block chose (`choose`, run on 6 October 2026), committed before 2023-2025 is read. Under
#: `SELECTION` it is `base`: no remedy is adopted. Every candidate's paired CRPS gain over `base` on the inner block is
#: negative (the best, `turn_pool`, -0.017 [-0.041, +0.009]), so none is eligible. On the 19 inner quarter-ends the
#: shift remedies move the 50% band from 31.6% to 0-5%: a median taken over earlier quarter-ends is the wrong
#: location for the next one, because the bias changes sign by regime (`docs/pivot/quarter-end-diagnosis.md`).
CHOSEN_REMEDY = "base"

LOOK_LABEL = ("a labelled look at 2023-2025: the remedy was chosen on 2018-2022 and these days chose nothing, "
              "but 2023-2025 was read by every earlier look at v2 and by the diagnosis, so the figures are "
              "exploratory (selection-adjusted uncertainty not computed). Only a live record can show that a "
              "remedy is better")


# ---------------------------------------------------------------------------
# The layer
# ---------------------------------------------------------------------------


def require_read_window(end) -> None:
    """Refuse any day after `LAST_READ`: the lockbox holds those days back from every comparison."""

    if end > LAST_READ:
        raise ValueError(f"{end} is after {LAST_READ}: those days are locked (docs/decisions/lockbox.md)")


def _median(values):
    return statistics.median(values)


def _quantile(values, level):
    """The linear-interpolation (type 7) quantile of `values`."""

    ordered = sorted(values)
    position = level * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def _residual(day):
    return day["y"] - day["v2"][2]


def _adjusted(day, past, name):
    """`day`'s vector under remedy `name`, from `past`: earlier days whose labels were public at `day`'s anchor.

    Raises:
        LookAheadError: if a past day's label was not public at the anchor.
    """

    for earlier in past:
        if earlier["date"] > day["anchor"]:
            raise LookAheadError(f"{earlier['date']}'s label was not public at the anchor {day['anchor']}")
    vector = list(day["v2"])
    if name == "base" or day["type"] != "quarter_end":
        return vector
    recent = name.endswith("_recent")
    name = name.removesuffix("_recent")
    pool = [p for p in past if p["type"] == "quarter_end"]
    pool = pool[-RECENT:] if recent else pool
    quarter = [_residual(p) for p in pool]
    if name == "qe_empirical":
        if len(quarter) < MIN_PAST_EMPIRICAL:
            return vector
        return _empirical(vector[2], quarter)
    if len(quarter) < MIN_PAST:
        return vector
    shift = _median(quarter)
    if name == "qe_shift":
        return [q + shift for q in vector]
    if name == "turn_pool":
        month = [_residual(p) for p in past if p["type"] == "month_end"]
        if len(month) < POOL_MIN_MONTH_ENDS:
            return vector
        n = len(quarter)
        shift = (n * shift + POOL_WEIGHT * _median(month)) / (n + POOL_WEIGHT)
        return [q + shift for q in vector]
    if name == "qe_shift_width":
        halves = [(p["v2"][3] - p["v2"][1]) / 2.0 for p in pool]
        denominator = _median(halves)
        scale = max(1.0, _median([abs(e - shift) for e in quarter]) / denominator) if denominator > 0 else 1.0
        centre = vector[2]
        return [centre + shift + scale * (q - centre) for q in vector]
    raise ValueError(f"unknown remedy {name!r}")


def _empirical(centre, residuals):
    return [centre + _quantile(residuals, level) for level in LEVELS]


def walk(days, name):
    """Every day's vector under remedy `name`, in date order: each from the days its anchor had public.

    `days` carry `date`, `anchor`, `y`, `v2` (v2's vector), `type` (the pressure-day type). The estimate for a
    day reads v2's vectors for the earlier days, never an earlier remedied vector.
    """

    if name not in CANDIDATES:
        raise ValueError(f"unknown remedy {name!r}")
    out = []
    for k, day in enumerate(days):
        past = [p for p in days[:k] if p["date"] <= day["anchor"]]
        out.append(_adjusted(day, past, name))
    return out


# ---------------------------------------------------------------------------
# Days and cells
# ---------------------------------------------------------------------------


def _tied(a, b):
    return abs(a - b) <= interior.TIE_BPS


def load_days(panel, end):
    """v2's scored days through `end` (never past `LAST_READ`), with anchors and pressure-day types and regimes.

    A row of the published record after `end` is dropped before anything reads it.
    """

    require_read_window(end)
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    rows = load_daily_panel(panel)
    audit_panel(rows)
    if panel_sha256(panel) != record["panel_sha256"]:
        raise ValueError("the panel is not the published panel")
    anchors = dict(record["anchors"])
    kept = [(day, y, v2) for day, y, _pid, _tracked, v2 in record["per_day_h1"]["rows"]
            if date.fromisoformat(day) <= end]
    scored = [date.fromisoformat(day) for day, _y, _v2 in kept]
    regimes, types = _split_labels(load_split_declaration(SPLITS), rows, scored)
    return [{"date": day, "anchor": anchors[day], "y": y, "v2": list(v2), "type": kind, "regime": regime}
            for (day, y, v2), kind, regime in zip(kept, types, regimes)]


def cell_members(day):
    return {
        "all": True,
        "quarter_end": day["type"] == "quarter_end",
        "year_end": day["type"] == "quarter_end" and day["date"][5:7] == "12",
        "tax_date": day["type"] == "tax_date",
        "month_end": day["type"] == "month_end",
        "ordinary": day["type"] == "ordinary",
    }


CELLS = tuple(cell_members({"type": "ordinary", "date": "2000-01-01"}))


def _inside(y, vector, lo, hi):
    if _tied(y, vector[lo]) or _tied(y, vector[hi]):
        return 0.5
    return 1.0 if vector[lo] < y < vector[hi] else 0.0


def coverage(y_values, vectors):
    """The 50% and 90% bands' half-inside coverage, P(y <= q50), the share above q95, mean width (bp)."""

    n = len(vectors)
    return {
        "band_50": 100.0 * sum(_inside(y, v, 1, 3) for y, v in zip(y_values, vectors)) / n,
        "band_90": 100.0 * sum(_inside(y, v, 0, 4) for y, v in zip(y_values, vectors)) / n,
        "p_y_at_most_q50": 100.0 * sum(interior.below_half_tie(y, v[2]) for y, v in zip(y_values, vectors)) / n,
        "above_q95": 100.0 * sum(1.0 - interior.below_half_tie(y, v[4]) for y, v in zip(y_values, vectors)) / n,
        "band_50_mean_width_bps": statistics.fmean(v[3] - v[1] for v in vectors),
        "mean_y_minus_q50_bps": statistics.fmean(y - v[2] for y, v in zip(y_values, vectors)),
    }


def _crps(vector, y):
    return crps_from_quantiles(LEVELS, vector, y)


def _interval(differences, seed_parts):
    """The mean of `differences` with its 90% stationary-bootstrap interval, or 'too few days'."""

    if len(differences) < MINIMUM_CELL:
        return {"days": len(differences), "mean": statistics.fmean(differences) if differences else None,
                "interval": "too few days"}
    cell = onset.paired_difference(differences, [0.0] * len(differences), list(range(len(differences))),
                                   block_length=BLOCK_LENGTH, seed=onset._seed("#327", *seed_parts))
    return {"days": cell["days"], "mean": cell["mean"],
            "interval": {"lower": cell["interval"]["lower"], "upper": cell["interval"]["upper"]}}


def summarise(days, vectors, base_vectors, persistence, seed_parts):
    """One cell's figures for one set of vectors: bands, CRPS, and the paired CRPS gain over `base_vectors`."""

    if not days:
        return {"days": 0}
    y_values = [d["y"] for d in days]
    losses = [_crps(v, y) for v, y in zip(vectors, y_values)]
    base_losses = [_crps(v, y) for v, y in zip(base_vectors, y_values)]
    out = {"days": len(days), **coverage(y_values, vectors), "crps_bps": statistics.fmean(losses),
           "crps_base_bps": statistics.fmean(base_losses),
           "paired_gain_over_base": _interval([b - m for b, m in zip(base_losses, losses)], seed_parts)}
    if persistence is not None:
        out["crps_persistence_bps"] = statistics.fmean(persistence[d["date"]] for d in days)
    if len(days) < MINIMUM_CELL:
        out["bands_interval"] = "too few days"
    return out


def persistence_losses():
    """As-of persistence's per-day CRPS at h = 1, from the two published records, as #244 reads them."""

    published = json.loads((REPO / "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json")
                           .read_text(encoding="utf-8"))
    final = json.loads((REPO / "docs/runs/final_test_near_blind.json").read_text(encoding="utf-8"))
    out = {e["scored_date"]: e["loss_a_bps"] for e in published["comparison"]["per_origin"]}
    out.update({e["scored_date"]: e["loss_a_bps"] for e in final["primary"]["window_per_origin"]})
    return out


def _in(day, window):
    return window[0] <= date.fromisoformat(day["date"]) <= window[1]


# ---------------------------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------------------------


def quarter_end_diagnosis(days):
    """Why v2 misses quarter-ends: a level shift, a band too narrow, or both, by regime.

    For each group of quarter-end days: the bias (y - q50), the share of outcomes at or below the median,
    the bands' coverage, and two ex-post counterfactuals that are diagnostics, not remedies (they read the
    group's own outcomes): the 50% band's coverage if re-centred by the group's median residual (a level
    shift alone), and if also widened by the factor that makes its 50% band exact (shift and width).
    """

    groups = {"2018-19": [d for d in days if d["regime"] == "2018-19"],
              "2020-2025": [d for d in days if d["regime"] != "2018-19"],
              "all": list(days)}
    for label in sorted({d["regime"] for d in days}):
        groups[f"regime {label}"] = [d for d in days if d["regime"] == label]
    out = {}
    for label, group in groups.items():
        quarter = [d for d in group if d["type"] == "quarter_end"]
        if not quarter:
            continue
        vectors = [d["v2"] for d in quarter]
        y_values = [d["y"] for d in quarter]
        errors = [y - v[2] for y, v in zip(y_values, vectors)]
        shift = _median(errors)
        halves = [(v[3] - v[1]) / 2.0 for v in vectors]
        scale = max(1.0, _median([abs(e - shift) for e in errors]) / _median(halves))
        shifted = [[q + shift for q in v] for v in vectors]
        widened = [[v[2] + shift + scale * (q - v[2]) for q in v] for v in vectors]
        out[label] = {
            "days": len(quarter),
            "v2": coverage(y_values, vectors),
            "median_y_minus_q50_bps": shift,
            "median_abs_y_minus_q50_bps": _median([abs(e) for e in errors]),
            "median_half_iqr_bps": _median(halves),
            "share_above_q50_pct": 100.0 * sum(1 for e in errors if e > 0) / len(errors),
            "ex_post_shift_only": {"shift_bps": shift, **coverage(y_values, shifted)},
            "ex_post_shift_and_width": {"shift_bps": shift, "width_factor": scale,
                                        **coverage(y_values, widened)},
            "reading": ("diagnostic, ex post: the counterfactuals read the group's own outcomes; "
                        + ("interval: too few days" if len(quarter) < MINIMUM_CELL else "counts only, no interval")),
        }
    out["per_quarter_end"] = [
        {"date": d["date"], "regime": d["regime"], "y_bps": d["y"], "v2": d["v2"],
         "y_minus_q50_bps": d["y"] - d["v2"][2],
         "year_end": d["date"][5:7] == "12"} for d in days if d["type"] == "quarter_end"]
    return out


# ---------------------------------------------------------------------------
# Choice, and the labelled look
# ---------------------------------------------------------------------------


def _vectors(days):
    return {name: walk(days, name) for name in CANDIDATES}


def check_only_quarter_ends_move(days, vectors):
    for name, vecs in vectors.items():
        moved = [d for d, v in zip(days, vecs) if v != d["v2"] and d["type"] != "quarter_end"]
        if moved:
            raise ValueError(f"{name} moved a day that is not a quarter-end: {moved[0]['date']}")


def choose(days):
    """The remedy chosen on the inner block (`SELECTION`). Refuses any day outside it."""

    if not days or any(not _in(d, INNER) for d in days):
        raise ValueError("the remedy is chosen on the inner block only")
    vectors = _vectors(days)
    check_only_quarter_ends_move(days, vectors)
    losses = {name: [_crps(v, d["y"]) for v, d in zip(vecs, days)] for name, vecs in vectors.items()}
    crps = {name: statistics.fmean(vals) for name, vals in losses.items()}
    # The paired vector has one entry per inner day, so its interval is always computed here.
    full = {name: onset.paired_difference(losses["base"], losses[name], list(range(len(days))),
                                          block_length=BLOCK_LENGTH,
                                          seed=onset._seed("#327", "choose", name, "base"))
            for name in CANDIDATES if name != "base"}
    eligible = sorted(n for n in full if full[n]["mean"] > 0.0)
    if not eligible:
        selection = {"recommended": "base", "eligible": [], "leader": None, "reason": SELECTION["none_eligible"]}
    else:
        leader = min(eligible, key=lambda n: (crps[n], CANDIDATES[n]["complexity"], n))
        simpler = []
        for name in eligible:
            if CANDIDATES[name]["complexity"] >= CANDIDATES[leader]["complexity"]:
                continue
            gap = onset.paired_difference(losses[leader], losses[name], list(range(len(days))),
                                          block_length=BLOCK_LENGTH,
                                          seed=onset._seed("#327", "choose", name, "vs", leader))
            if gap["interval"]["lower"] <= 0.0 <= gap["interval"]["upper"]:
                simpler.append(name)
        chosen = (min(simpler, key=lambda n: (CANDIDATES[n]["complexity"], crps[n], n)) if simpler else leader)
        selection = {"recommended": chosen, "eligible": eligible, "leader": leader,
                     "reason": (f"{leader} has the lowest inner CRPS of the eligible candidates; " +
                                (f"{chosen} is simpler and its paired CRPS difference against {leader} has a 90% "
                                 "interval including 0" if simpler else "no simpler eligible candidate is within "
                                 "its interval"))}
    cells = {}
    for name, vecs in vectors.items():
        cells[name] = {cell: summarise([d for d in days if cell_members(d)[cell]],
                                       [v for d, v in zip(days, vecs) if cell_members(d)[cell]],
                                       [v for d, v in zip(days, vectors["base"]) if cell_members(d)[cell]],
                                       None, ("choose-cell", name, cell)) for cell in CELLS}
    return {
        "declared": {"candidates": CANDIDATES, "selection": SELECTION, "not_built": NOT_BUILT,
                     "min_past": MIN_PAST, "min_past_empirical": MIN_PAST_EMPIRICAL, "pool_weight": POOL_WEIGHT,
                     "pool_min_month_ends": POOL_MIN_MONTH_ENDS},
        "window": [INNER[0].isoformat(), INNER[1].isoformat()],
        "days": len(days),
        "quarter_ends": sum(1 for d in days if d["type"] == "quarter_end"),
        "inner_crps_bps": crps,
        "paired_gain_over_base": {name: {"mean": g["mean"], "interval": g["interval"]} for name, g in full.items()},
        "cells": cells,
        "selection": selection,
    }


def report(days, chosen, persistence):
    """The labelled look at 2023-2025: every candidate and the chosen remedy against `base`, by cell and regime."""

    if chosen is None:
        raise ValueError("no remedy is committed as CHOSEN_REMEDY: choose on the inner block first")
    if chosen not in CANDIDATES:
        raise ValueError(f"CHOSEN_REMEDY {chosen!r} is not a declared candidate")
    if not days or any(not _in(d, OUTER) for d in days):
        raise ValueError("the look reads 2023-2025 only")
    vectors = _vectors(days)
    check_only_quarter_ends_move(days, vectors)
    out = {"label": LOOK_LABEL, "window": [OUTER[0].isoformat(), OUTER[1].isoformat()], "days": len(days),
           "chosen": chosen, "sign": "paired gain = CRPS(base) - CRPS(candidate) per day; a positive mean favours the remedy",
           "cells": {}, "by_regime_quarter_end": {}}
    for name, vecs in vectors.items():
        out["cells"][name] = {
            cell: summarise([d for d in days if cell_members(d)[cell]],
                            [v for d, v in zip(days, vecs) if cell_members(d)[cell]],
                            [v for d, v in zip(days, vectors["base"]) if cell_members(d)[cell]],
                            persistence, ("look", name, cell)) for cell in CELLS}
        out["by_regime_quarter_end"][name] = {}
        for regime in sorted({d["regime"] for d in days}):
            pick = [k for k, d in enumerate(days) if d["regime"] == regime and d["type"] == "quarter_end"]
            out["by_regime_quarter_end"][name][regime] = summarise(
                [days[k] for k in pick], [vecs[k] for k in pick], [vectors["base"][k] for k in pick],
                persistence, ("look-regime", name, regime))
    return out


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def _write(path, document):
    path.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("diagnose", "choose", "report"))
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "diagnose":
        days = load_days(args.panel, LAST_READ)
        result = {"window": [days[0]["date"], days[-1]["date"]], "label": "diagnostic; chooses nothing",
                  "diagnosis": quarter_end_diagnosis(days)}
    elif args.command == "choose":
        days = [d for d in load_days(args.panel, INNER[1])]
        result = choose(days)
        print(json.dumps(result["selection"], indent=1))
    else:
        days = [d for d in load_days(args.panel, LAST_READ) if _in(d, OUTER)]
        result = report(days, CHOSEN_REMEDY, persistence_losses())
    _write(args.output, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
