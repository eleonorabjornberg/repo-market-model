"""The narrowed coupon-settlement flag, scored against the published declaration (#339).

The test and its rule are declared in `docs/pivot/settlement-flag-test.md`, in a commit before this script scored
anything. The candidate changes one thing in the published declaration: its conformal PID scorecaster's
coupon-settlement indicator marks only the ruled settlements (3-, 10-, 30-year nominal securities on the 15th or the
next business day; 2-, 5-, 7-year notes at month-end or the next business day), not FRN, TIPS, 20-year or off-date
settlements. Both sides are walked in one process on the published panel, truncated at 2025-12-31 so no later day is
loaded (`docs/decisions/lockbox.md`).

    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/settlement_flag_candidate.py \\
        --panel PUB.csv --output docs/pivot/evidence/settlement-flag/settlement_flag_candidate.json

`PUB.csv` is the published panel (`docs/pivot/next-session.md`). The published side is first checked against the
published records, exactly: the per-day CRPS against the CRPS record, and the Brier of each threshold against the
pressure record.
"""

from __future__ import annotations

import argparse
import calendar
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, onset, pressure  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    benchmark_comparison_document,
    panel_sha256,
    rolling_exceedance_backtest,
    split_document,
)
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402
from repo_model.recalibration import NestedFoldPid  # noqa: E402

LAST = date(2025, 12, 31)
FIRST = date(2018, 4, 3)
AUCTIONS = (REPO / "tests/fixtures/snapshots/funding_inputs/treasury_auctions"
            / "20260914T051023Z_722359ea9bc7.json")
CRPS_RECORD = REPO / "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
PRESSURE_RECORD = REPO / "docs/runs/pressure_model_v1_h1.json"
MINIMUM_CELL_DAYS = 20
CRPS_BLOCK_LENGTH = 2


def _script(name):
    spec = importlib.util.spec_from_file_location(f"flag_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ruled_kind(record: dict):
    """`mid_month` (3-, 10-, 30-year), `month_end` (2-, 5-, 7-year) or None, for a nominal Note or Bond."""
    if record["security_type"] not in ("Note", "Bond"):
        return None
    if record["floating_rate"] == "Yes" or record["inflation_index_security"] == "Yes":
        return None
    term = record["security_term"]
    if term in ("3-Year", "10-Year", "30-Year") or term.startswith(("9-Year", "29-Year")):
        return "mid_month"
    if term in ("2-Year", "5-Year", "7-Year"):
        return "month_end"
    return None


def narrowed_days(panel_days: list, auction_rows: list) -> dict:
    """Day -> the ruled settlements it carries, for every day of the panel up to `LAST`.

    A record counts when its issue date is the next panel business day on or after the 15th (mid-month kinds) or
    the month's last calendar day (month-end kinds).
    """

    days = sorted(d for d in panel_days if FIRST <= d <= LAST)

    def next_business_day(day):
        return next((d for d in days if d >= day), None)

    expected = {}
    for year in range(FIRST.year, LAST.year + 1):
        for month in range(1, 13):
            if not FIRST <= date(year, month, 28) <= LAST:
                continue
            for day, name in ((date(year, month, 15), "mid_month"),
                              (date(year, month, calendar.monthrange(year, month)[1]), "month_end")):
                settles = next_business_day(day)
                if settles is not None:
                    expected[(settles, name)] = True
    flagged = {}
    for record in auction_rows:
        kind = ruled_kind(record)
        if kind is None:
            continue
        issue = date.fromisoformat(record["issue_date"])
        if (issue, kind) in expected:
            flagged.setdefault(issue, []).append(record["security_term"])
    return flagged


class NarrowedFoldPid(NestedFoldPid):
    """The published nested conformal PID with a narrowed coupon-settlement indicator (#339).

    The published indicator is still read, through `scorecaster_calendar` and its availability guard; the last
    indicator is then replaced by the narrowed flag, which must be a subset of it.
    """

    def __init__(self, rows, rule, *, splits, refit_every, narrowed):
        super().__init__(rows, rule, splits=splits, refit_every=refit_every)
        self._narrowed = narrowed

    @property
    def settings(self) -> dict:
        return {**super().settings, "scorecaster_coupon_flag": "narrowed to the ruled settlements (#339)"}

    def _calendar(self, index):
        calendar_ = super()._calendar(index)
        published = calendar_[-1]
        narrowed = 1 if self._dates[index] in self._narrowed else 0
        if narrowed > published:
            raise ValueError(f"{self._dates[index]}: the narrowed flag marks a day the published flag does not")
        return calendar_[:-1] + (narrowed,)


def crps_side(rows, fit, features, online, registry, horizon, parsed, final_opening):
    walk, levels, settings = final_opening.distribution_walk(
        rows, fit=fit, features=features, online_calibration=online, registry=registry, horizon=horizon,
        minimum_history=parsed.minimum_history, refit_every=parsed.refit_every,
    )
    return {rows[i].date: crps_from_quantiles(levels, q, rows[i].spread_bps) for i, q in walk}, settings


def cell_verdict(entry) -> str:
    if entry["count"] < MINIMUM_CELL_DAYS:
        return "too few days"
    if entry["interval"]["upper"] < 0:
        return "worse beyond its interval"
    return "ok"


def judge(name: str, paired: dict) -> dict:
    """The declared rule for one figure: the pooled gate and its cells (`docs/pivot/settlement-flag-test.md`)."""
    interval = paired["interval"]
    gate = paired["mean"] > 0 and interval["lower"] > 0
    cells = {}
    for split in ("by_regime", "by_day_type"):
        for key, entry in paired["splits"][split].items():
            cells[f"{split}/{key}"] = cell_verdict(entry)
    worse = sorted(k for k, v in cells.items() if v == "worse beyond its interval")
    return {"figure": name, "mean": paired["mean"], "interval": interval, "gate": gate,
            "cells": cells, "cells_worse_beyond_interval": worse}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    rows = [r for r in load_daily_panel(args.panel) if r.date <= LAST]
    audit_panel(rows)
    lockbox.require_unlocked([r.date for r in rows if r.date >= date(2026, 1, 1)], where="settlement flag candidate")
    splits = load_split_declaration(REPO / "metadata/evaluation_splits.json")
    registry = json.loads((REPO / "metadata/sources.json").read_text())
    narrowed = narrowed_days([r.date for r in rows], json.loads(AUCTIONS.read_text())["data"])
    published_flag = {r.date for r in rows if float(r.values["treasury_settlement_coupons"]) > 0}
    if not set(narrowed) <= published_flag:
        raise ValueError("the narrowed flag marks a day the published flag does not")

    final_opening = _script("final_test_opening")
    live = _script("live_record")
    final_opening.live_record = live
    sides, parsed = live._compare_sides(1)
    _name, fit, features, published_online = sides["published"]

    def candidate_online(rows_, rule):
        return NarrowedFoldPid(rows_, rule, splits=splits, refit_every=parsed.refit_every, narrowed=narrowed)

    crps_pub, _ = crps_side(rows, fit, features, published_online, registry, 1, parsed, final_opening)
    crps_new, _ = crps_side(rows, fit, features, candidate_online, registry, 1, parsed, final_opening)
    dates = sorted(crps_pub)
    record = json.loads(CRPS_RECORD.read_text())
    expected = {e["scored_date"]: e["loss_b_bps"] for e in record["comparison"]["per_origin"]}
    ours = {d.isoformat(): crps_pub[d] for d in dates}
    if ours != expected:
        raise ValueError("the published side does not reproduce the CRPS record's per-day losses")
    base = [crps_pub[d] for d in dates]
    cand = [crps_new[d] for d in dates]
    positions = list(range(len(dates)))
    block = CRPS_BLOCK_LENGTH
    seed = onset._seed("#339", "crps")
    paired = onset.paired_difference(base, cand, positions, block_length=block, seed=seed)
    paired["splits"] = split_document(splits, rows, dates, [b - c for b, c in zip(base, cand)],
                                      block_length=block, seed=seed)
    figures = {"crps_bps": judge("crps_bps", paired)}
    changed = [d.isoformat() for d in dates if crps_pub[d] != crps_new[d]]

    # The pressure probability: pressure model v1's declaration, published against candidate.
    pm = _script("pressure_model_v1")
    taus = pm.TAUS
    features_p = pm._at_horizon(pm.GBM_FEATURES, 1)
    from repo_model import ml

    def run(online):
        raw = rolling_exceedance_backtest(
            rows, predictor=ml.gbm_exceedance(tuple(n for n in features_p if n != "spread_bps"),
                                              minimum_history=pm.MINIMUM_HISTORY),
            model_name=pm.PUBLISHED, features=features_p, registry=registry, decision_time=pm.DECISION,
            taus=taus, minimum_history=pm.MINIMUM_HISTORY, refit_every=pm.REFIT_EVERY, end=LAST, horizon=1,
            online_calibration=online,
        )
        return pm._rescored(pressure.recalibrated(raw))

    report_pub = run(lambda r, rule: NestedFoldPid(r, rule, splits=splits, refit_every=pm.REFIT_EVERY))
    report_new = run(lambda r, rule: NarrowedFoldPid(r, rule, splits=splits, refit_every=pm.REFIT_EVERY,
                                                      narrowed=narrowed))
    pressure_record = json.loads(PRESSURE_RECORD.read_text())
    reproduced = {}
    for position, tau in enumerate(report_pub.taus):
        predicted, _, realized = report_pub.at_tau(position)
        brier = sum((p - o) ** 2 for p, o in zip(predicted, realized)) / len(realized)
        recorded = pressure_record["benchmarks"]["persistence_logistic"]["by_tau"][f"{tau:g}"]["model_brier"]
        if brier != recorded:
            raise ValueError(f"the published side's Brier at +{tau:g} bp differs from the pressure record's")
        reproduced[f"{tau:g}"] = brier
    comparison = benchmark_comparison_document(report_new, report_pub, panel_sha256=panel_sha256(args.panel),
                                               rows=rows, declaration=splits)
    for tau in comparison["by_tau"]:
        cell = comparison["by_tau"][tau]["paired_brier_difference"]
        figures[f"brier_+{tau}bp"] = judge(f"brier_+{tau}bp", cell)
    decisive = [figures["crps_bps"], figures["brier_+5bp"], figures["brier_+10bp"]]
    passes = all(f["gate"] and not f["cells_worse_beyond_interval"] for f in decisive)
    document = {
        "directive": "#339",
        "declared_in": "docs/pivot/settlement-flag-test.md",
        "panel_sha256": panel_sha256(args.panel),
        "window": [dates[0].isoformat(), dates[-1].isoformat()],
        "days": len(dates),
        "narrowed_flag_days": len(narrowed),
        "published_flag_days": len(published_flag),
        "days_where_the_crps_differs": len(changed),
        "published_reproduces_records": {"crps_per_day": True, "brier": reproduced},
        "mean_crps_bps": {"published": sum(base) / len(base), "candidate": sum(cand) / len(cand)},
        "figures": figures,
        "joins_published_declaration": passes,
        "pressure_comparison": comparison,
        "crps_paired": paired,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"joins": passes, "mean_crps_bps": document["mean_crps_bps"],
                      "figures": {k: {"mean": v["mean"], "lower": v["interval"]["lower"],
                                      "upper": v["interval"]["upper"], "gate": v["gate"],
                                      "worse": v["cells_worse_beyond_interval"]}
                                  for k, v in figures.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
