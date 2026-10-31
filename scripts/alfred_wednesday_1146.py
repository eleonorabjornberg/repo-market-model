"""ALFRED never-revised check of the Wednesday levels `WRBWFRBL` and `WDTGAL` (#1146; H5 step 3, scarcity input).

ALFRED (`alfred.stlouisfed.org`) is not reachable from cloud sessions, so this is a short run on Eleonora's Mac. It fetches
several vintages of each series (`https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<SERIES>&vintage_date=<DATE>`) into a
new, empty directory, one subdirectory per series, and runs `scripts/alfred_vintages.py` on each series' files, which exits 1 if
any observation shared by two vintages differs. The Wednesday level is claimed never revised only if it exits 0 for both.

    PYTHONPATH=src python3 scripts/alfred_wednesday_1146.py docs/research/wednesday-scarcity-1146/alfred

Standard library only. The vintages are the dates of `tests/fixtures/snapshots/alfred-wresbal/`, whose week average this level sits
beside, so the two series are checked over the same span.
"""

from __future__ import annotations

import importlib.util
import sys
import urllib.request
from pathlib import Path
from typing import Callable, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
SERIES = ("WRBWFRBL", "WDTGAL")
VINTAGES = ("2019-09-16", "2021-07-27", "2024-09-24", "2026-09-12")
BASE = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"


def url(series: str, vintage: str) -> str:
    return f"{BASE}?id={series}&vintage_date={vintage}"


def _alfred_vintages():
    spec = importlib.util.spec_from_file_location("alfred_vintages", REPO / "scripts" / "alfred_vintages.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(directory: Path, *, opener: Optional[Callable[[str], object]] = None) -> int:
    """Fetch every vintage of every series into `directory` (new or empty) and compare them: 0 if none was restated, else 1.

    Raises:
        SystemExit: `directory` exists and is not empty.
    """

    if directory.exists() and any(directory.iterdir()):
        raise SystemExit(f"{directory} is not empty; fetch into a new directory")
    open_url = opener or (lambda address: urllib.request.urlopen(address, timeout=60))
    compare = _alfred_vintages()
    failed = []
    for series in SERIES:
        folder = directory / series
        folder.mkdir(parents=True, exist_ok=True)
        files = []
        for vintage in VINTAGES:
            with open_url(url(series, vintage)) as response:
                payload = response.read()
            path = folder / f"{series}_{vintage}.csv"
            path.write_bytes(payload)
            files.append(path)
        print(f"== {series}")
        if compare.main([str(p) for p in files]):
            failed.append(series)
        print(f"{series} never revised: {'no' if series in failed else 'yes'}")
    return 1 if failed else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        raise SystemExit("usage: alfred_wednesday_1146.py NEW_DIRECTORY")
    return run(Path(args[0]))


if __name__ == "__main__":
    sys.exit(main())
