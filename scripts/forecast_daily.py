"""The published distribution's daily forecasts at h = 1, against the actual spread (#246).

Eleonora's ruling of 6 October 2026 on #246: readers should see what the model
forecast each day, what actually happened, and how far off it was in basis
points. No published record holds the per-day quantiles (the final test keeps
only per-day CRPS), so this script writes one descriptive record,
`docs/runs/published_distribution_daily_h1.json`. For every scored day from
2018-06-29 to 2026-09-03 it holds the date, the published distribution's five
quantiles at h = 1 and the actual SOFR - IORB.

The walk is the final test's (`final_test_opening.distribution_walk`) on the
published side of `live_record._compare_sides(1)`: #169's gbm with nested
conformal PID, under the CRPS record's declaration, on the published panel.
Before writing, the per-day CRPS is checked against both published series
exactly: the CRPS record's pre-2026 losses and `final_test_near_blind.json`'s
window losses (`reproduction_check`). The record decides nothing, and no day
after the panel end (2026-09-03) is read: the walk's fold grid ends there.

    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/forecast_daily.py \\
        --panel PUB.csv --output docs/runs/published_distribution_daily_h1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model.baseline import _code_provenance, panel_sha256  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402

RUNS = REPO / "docs" / "runs"
CRPS_RECORD = "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
FINAL_TEST = "docs/runs/final_test_near_blind.json"
HORIZON = 1


def _script(name):
    import importlib.util

    spec = importlib.util.spec_from_file_location(f"daily_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reproduction_check(levels, days) -> dict:
    """Each day's CRPS against the two published series, exactly. Raises `ValueError`."""

    crps = json.loads((REPO / CRPS_RECORD).read_text(encoding="utf-8"))
    final = json.loads((REPO / FINAL_TEST).read_text(encoding="utf-8"))
    expected = {e["scored_date"]: e["loss_b_bps"] for e in crps["comparison"]["per_origin"]}
    expected.update({e["scored_date"]: e["loss_b_bps"]
                     for e in final["primary"]["window_per_origin"]})
    ours = {day["date"]: crps_from_quantiles(levels, day["quantiles_bps"], day["actual_bps"])
            for day in days}
    if set(ours) != set(expected):
        raise ValueError(f"the walk scores {len(ours)} days, the records {len(expected)}")
    mismatched = sorted(day for day in ours if ours[day] != expected[day])
    if mismatched:
        raise ValueError(f"the CRPS differs from the published records on {len(mismatched)} days, "
                         f"first {mismatched[0]}")
    return {"records": [CRPS_RECORD, FINAL_TEST], "exact": True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    fto = _script("final_test_opening")
    fp = fto.fp
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    if panel_sha256(args.panel) != fp._frozen_panel_sha256():
        raise ValueError("the panel is not the published panel")
    lr = fto._script("live_record")
    fto.live_record = lr
    registry = json.loads(fp.REGISTRY.read_text(encoding="utf-8"))
    sides, parsed = lr._compare_sides(HORIZON)
    name, fit, features, online = sides["published"]
    walk, levels, settings = fto.distribution_walk(
        rows, fit=fit, features=features, online_calibration=online, registry=registry,
        horizon=HORIZON, minimum_history=parsed.minimum_history, refit_every=parsed.refit_every,
    )
    lr._require_crps_declaration("published", HORIZON, name, features, settings)
    days = [{"date": rows[index].date.isoformat(), "quantiles_bps": list(quantiles),
             "actual_bps": rows[index].spread_bps} for index, quantiles in walk]
    reproduces = reproduction_check(levels, days)
    if lr.published_distribution_record(HORIZON) != CRPS_RECORD:
        raise ValueError("the published distribution at h = 1 is not the CRPS record's")
    document = {
        "directive": "#246",
        "record": ("the published distribution's daily forecasts at h = 1 against the actual "
                   "SOFR - IORB, every scored day"),
        "decides": "nothing",
        "horizon": HORIZON,
        "panel_sha256": panel_sha256(args.panel),
        "published_record": CRPS_RECORD,
        "published_declaration_sha256": lr.published_declaration_sha256(HORIZON),
        "walk": "final_test_opening.distribution_walk on live_record._compare_sides(1)['published']",
        "levels": list(levels),
        "first": days[0]["date"],
        "last": days[-1]["date"],
        "reproduces": reproduces,
        "provenance": {"code": _code_provenance()},
        "days": days,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"days": len(days), "first": document["first"], "last": document["last"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
