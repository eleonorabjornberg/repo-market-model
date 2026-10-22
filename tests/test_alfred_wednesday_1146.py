"""`scripts/alfred_wednesday_1146.py` (#1146): the ALFRED never-revised check of `WRBWFRBL` and `WDTGAL`, as a short run on Eleonora's Mac.

Written before the script. ALFRED is not reachable from cloud sessions, so the fetch takes an injectable opener and these tests
run it on local text: the URLs, the files written (one directory per series, a new empty one), the verdict of
`scripts/alfred_vintages.py` (exit 1 on any restated observation), and the refusal to write into a directory that is not empty.
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("alfred_wednesday_1146", ROOT / "scripts" / "alfred_wednesday_1146.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["alfred_wednesday_1146"] = script
_spec.loader.exec_module(script)


def csv_text(series: str, vintage: str, rows) -> bytes:
    stamp = vintage.replace("-", "")
    return ("observation_date,%s_%s\n" % (series, stamp) + "".join(f"{d},{v}\n" for d, v in rows)).encode()


class UrlTests(unittest.TestCase):

    def test_the_url_is_alfreds_graph_csv_for_the_series_and_vintage(self):
        self.assertEqual(
            script.url("WRBWFRBL", "2019-09-16"),
            "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=WRBWFRBL&vintage_date=2019-09-16",
        )

    def test_both_series_and_at_least_two_vintages_each_are_checked(self):
        self.assertEqual(sorted(script.SERIES), ["WDTGAL", "WRBWFRBL"])
        self.assertGreaterEqual(len(script.VINTAGES), 2)
        self.assertEqual(list(script.VINTAGES), sorted(script.VINTAGES))


class RunTests(unittest.TestCase):

    def opener(self, restate=False):
        def serve(address):
            series = address.split("id=")[1].split("&")[0]
            vintage = address.split("vintage_date=")[1]
            later = vintage >= "2025"
            rows = [("2019-09-11", "100.5"), ("2019-09-18", "101.5")]
            if later:
                rows.append(("2025-01-08", "300.0"))
                if restate:
                    rows[0] = ("2019-09-11", "100.6")
            return io.BytesIO(csv_text(series, vintage, rows))
        return serve

    def run_in(self, tmp, restate):
        out = io.StringIO()
        with redirect_stdout(out):
            code = script.run(Path(tmp) / "alfred", opener=self.opener(restate))
        return code, out.getvalue()

    def test_unrestated_vintages_exit_zero_and_every_file_is_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, text = self.run_in(tmp, restate=False)
            self.assertEqual(code, 0, text)
            for series in script.SERIES:
                files = sorted(p.name for p in (Path(tmp) / "alfred" / series).glob("*.csv"))
                self.assertEqual(files, [f"{series}_{v}.csv" for v in script.VINTAGES])
            self.assertIn("never revised: yes", text)

    def test_one_restated_observation_exits_one_and_says_which_series(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, text = self.run_in(tmp, restate=True)
            self.assertEqual(code, 1, text)
            self.assertIn("restated", text)
            self.assertIn("never revised: no", text)

    def test_a_directory_that_is_not_empty_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "alfred").mkdir()
            (Path(tmp) / "alfred" / "x").write_text("planted")
            with self.assertRaisesRegex(SystemExit, "not empty"):
                script.run(Path(tmp) / "alfred", opener=self.opener())


if __name__ == "__main__":
    unittest.main()
