"""Run a scoring script with the scarcity state read one of two ways, for #586's before-and-after.

A scratch measurement tool: it writes only what the script it runs writes. Eleonora's ruling on #571 (relayed 11 October
2026): the as-of scarcity state reads each leg (the reserves, the H.8 total assets, the day's ON RRP) at its own latest
public row. The judge's states (`pressure_judge._scarcity_states`) are now read that way by default; this wrapper runs
any script that scores a state-reading row under either read, on the same panel and declaration:

    PYTHONPATH=src python3 scripts/own_leg_rescore.py own_leg  risk_date_hurdle run --panel AUG2.csv ...
    PYTHONPATH=src python3 scripts/own_leg_rescore.py same_row risk_date_hurdle run --panel AUG2.csv ...

`own_leg` runs the script inside `scarcity.own_leg_composition()`, so a model that reads `reserve_scarcity_state` as an
input is fed the own-leg state in its training frame and at its forecast, and leaves the judge's read at the default.
`same_row` runs it as before #586: the column read at the one row where all three legs are public, and the judge's
`RMM_SCARCITY_READ=same_row` read. Nothing is written to `docs/runs/`; the wrapped script's own refusals (a committed
declaration, the lockbox) all apply.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import scarcity  # noqa: E402

READS = ("own_leg", "same_row")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 2 or argv[0] not in READS:
        raise SystemExit(f"usage: own_leg_rescore.py {{{'|'.join(READS)}}} SCRIPT [ARGS...]")
    read, name, rest = argv[0], argv[1], argv[2:]
    path = REPO / "scripts" / f"{name}.py"
    if not path.is_file():
        raise SystemExit(f"no script {path}")
    if read == "same_row":
        os.environ["RMM_SCARCITY_READ"] = "same_row"
    else:
        os.environ.pop("RMM_SCARCITY_READ", None)
    spec = importlib.util.spec_from_file_location(f"{name}_wrapped", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if read == "own_leg":
        with scarcity.own_leg_composition():
            return int(module.main(rest) or 0)
    return int(module.main(rest) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
