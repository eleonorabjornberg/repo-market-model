"""The published panel, built once per process from the tracked fixtures (#848).

`test_onset` and `test_protocol_benchmarks` each ran the same `build` over
`tests/fixtures/snapshots/funding_inputs/` with the manifest's cutoff and decision time. They
share this one build instead. The cache lives in the process only; a fresh process builds
again, and `tests/test_panel_cache.py` shows the cached files equal a fresh build's bytes.
"""

import contextlib
import io
import json
import tempfile
from pathlib import Path

from repo_model.cli import main as cli_main
from repo_model.data import load_daily_panel

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
_MANIFEST = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
CUTOFF = _MANIFEST["build_cutoff"]
DECISION_TIME = _MANIFEST["decision_time"]

_BUILD = {}


def published_build():
    """The built panel: `path` (CSV), `rows` (loaded) and `pit` (point-in-time CSV)."""

    if not _BUILD:
        path = Path(tempfile.mkdtemp()) / "funding_panel.csv"
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli_main(
                [
                    "build",
                    "--raw-root", str(FIXTURES),
                    "--output", str(path),
                    "--build-cutoff", CUTOFF,
                    "--decision-time", DECISION_TIME,
                ]
            )
        if code != 0:
            raise RuntimeError(err.getvalue() or "the fixture panel did not build")
        _BUILD.update(
            path=path,
            rows=load_daily_panel(path),
            pit=path.with_name(path.stem + "_point_in_time.csv"),
        )
    return _BUILD
