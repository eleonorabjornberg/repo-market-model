import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.data import DataContractError, audit_panel, load_daily_panel


class DataContractTests(unittest.TestCase):
    def write_csv(self, contents: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_load_and_audit(self):
        path = self.write_csv(
            "date,sofr,iorb,sofr_p25,sofr_p75,reserve_balances\n"
            "2026-01-02,4.31,4.30,4.30,4.32,3200\n"
            "2026-01-05,4.33,4.30,4.31,4.34,3190\n"
        )
        rows = load_daily_panel(path)
        report = audit_panel(rows)
        self.assertEqual(report.row_count, 2)
        self.assertAlmostEqual(rows[0].spread_bps, 1.0)
        self.assertEqual(report.warnings, [])

    def test_rejects_unsorted_dates(self):
        path = self.write_csv(
            "date,sofr,iorb\n"
            "2026-01-05,4.33,4.30\n"
            "2026-01-02,4.31,4.30\n"
        )
        with self.assertRaisesRegex(DataContractError, "sorted"):
            audit_panel(load_daily_panel(path))

    def test_warns_on_impossible_percentiles(self):
        path = self.write_csv(
            "date,sofr,iorb,sofr_p25,sofr_p75\n"
            "2026-01-02,4.31,4.30,4.35,4.30\n"
        )
        report = audit_panel(load_daily_panel(path))
        self.assertEqual(len(report.warnings), 1)


if __name__ == "__main__":
    unittest.main()
