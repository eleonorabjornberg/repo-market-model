"""Run a repository script or module with the tax-date window on market days (#538).

A scratch measurement, not a record: it publishes nothing and writes only what the script it runs writes. The
published `tax_date` column counts the two days after a corporate estimated-tax deadline with the District of
Columbia's holidays removed. Eleonora's ruling of 10 October 2026 on #521 counts them on the market calendar
(`data.tax_date_market_days`). This runs another script, or `repo_model.cli`, inside
`data.tax_window_on_market_days()`, so every panel that run builds carries the market-day column and the
published declaration stays as it is.

    PYTHONPATH=src python3 scripts/tax_date_market_days.py -m repo_model.cli build --raw-root \\
        tests/fixtures/snapshots/funding_inputs --output NEW/PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 \\
        --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/pressure_v1_1.py panel --output NEW/AUG.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/risk_date_severity.py run ...

The script reads `tax_date` from the panel it is given, so a run that is given the panel built here scores with the
market-day window. A run that rebuilds a calendar value from the date inside this process does too.
"""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import data  # noqa: E402

DECLARATION = REPO / "metadata" / "tax_date_market_days.json"

_published_verifier = data.verify_daily_panel


def _verify_either(panel_path, manifest_path):
    """The published manifest's digest, or the declared digest of the market-day build; nothing else."""

    try:
        return _published_verifier(panel_path, manifest_path)
    except data.DataContractError:
        declared = json.loads(DECLARATION.read_text(encoding="utf-8"))["market_days_panel_sha256"]
        computed = data.hashlib.sha256(Path(panel_path).read_bytes()).hexdigest()
        if computed != declared:
            raise
        return computed


def main(argv) -> int:
    if len(argv) < 2:
        raise SystemExit("usage: tax_date_market_days.py (-m MODULE | SCRIPT) [args ...]")
    data.verify_daily_panel = _verify_either
    with data.tax_window_on_market_days():
        if argv[0] == "-m":
            sys.argv = [argv[1], *argv[2:]]
            runpy.run_module(argv[1], run_name="__main__", alter_sys=True)
        else:
            sys.argv = [argv[0], *argv[1:]]
            runpy.run_path(argv[0], run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
