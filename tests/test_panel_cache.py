"""The in-process published-panel cache gives what a fresh build gives (#848).

`tests/panel_cache.py` builds the published panel from the tracked fixtures once per
process, for the modules that used to build it each for themselves. Nothing is scored; the
cache changes no assertion. These tests show the cached CSVs are byte-identical to a fresh
build and that the two former builders now share one.
"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import panel_cache
import test_onset
import test_protocol_benchmarks
from repo_model.cli import main as cli_main


class PanelCacheTests(unittest.TestCase):
    def test_cached_files_are_byte_identical_to_a_fresh_build(self):
        cached = panel_cache.published_build()
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / "funding_panel.csv"
            with contextlib.redirect_stdout(io.StringIO()):
                code = cli_main(
                    [
                        "build",
                        "--raw-root", str(panel_cache.FIXTURES),
                        "--output", str(fresh),
                        "--build-cutoff", panel_cache.CUTOFF,
                        "--decision-time", panel_cache.DECISION_TIME,
                    ]
                )
            self.assertEqual(code, 0)
            self.assertEqual(cached["path"].read_bytes(), fresh.read_bytes())
            self.assertEqual(
                cached["pit"].read_bytes(),
                fresh.with_name(fresh.stem + "_point_in_time.csv").read_bytes(),
            )

    def test_one_build_serves_every_caller(self):
        self.assertIs(panel_cache.published_build(), panel_cache.published_build())
        self.assertIs(test_protocol_benchmarks.published_panel(), panel_cache.published_build())
        self.assertIs(test_onset.published_panel(), panel_cache.published_build()["rows"])


if __name__ == "__main__":
    unittest.main()
