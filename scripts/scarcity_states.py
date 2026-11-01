"""The reserve-scarcity state of each day on the shared grid, read as of the forecast's decision instant.

Moved out of `scripts/pressure_judge.py` (`_scarcity_states`, #1055 stage 1) so that the H5, H3 and H9 scripts that need
the state no longer load the +5 bp judge. The judge keeps a forwarding name until stage 2 archives its callers.

`scarcity_states(horizon, last_day)` returns `{day: state}`: the reserves, the H.8 total assets and the day's ON RRP are
each read as of the forecast's decision instant at `horizon`, each at its own latest public row (Eleonora's ruling on #571,
11 October 2026; #586). The panel is the measurement panel `scripts/scarcity_validation.py` builds from the tracked
fixtures. Nothing is scored here and it ends at `last_day` through `scarcity.own_leg_states`, which refuses a locked day.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

REGISTRY = REPO / "metadata" / "sources.json"
MINIMUM_HISTORY = 61


def _validation():
    spec = importlib.util.spec_from_file_location("scarcity_validation", REPO / "scripts" / "scarcity_validation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scarcity_states(horizon, last_day):
    """{day: state} on the shared grid, each leg read at its own latest public row (#586)."""

    from repo_model.scarcity import measurement_declaration, own_leg_states

    validation = _validation()
    with measurement_declaration(), tempfile.TemporaryDirectory() as tmp:
        build, _, registry, decision = validation.build_measurement_panel(REGISTRY, Path(tmp))
        scored = own_leg_states(
            build.observations, registry=registry, decision_time=decision,
            minimum_history=MINIMUM_HISTORY, horizon=horizon, end=last_day,
        )
    return {entry.day: entry.state for entry in scored}
