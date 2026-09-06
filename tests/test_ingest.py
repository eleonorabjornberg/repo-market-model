import hashlib
import gzip
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.ingest import _decode_transport, fetch_fred_macro, fetch_nyfed_reference_rate


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)

    def test_nyfed_snapshots_are_checksummed(self):
        payloads = {
            "rate": b'{"refRates":[{"effectiveDate":"2026-01-02","percentRate":4.31}]}',
            "volume": b'{"refRates":[{"effectiveDate":"2026-01-02","volumeInBillions":2000}]}',
        }

        def downloader(url: str) -> bytes:
            return payloads["volume" if "type=volume" in url else "rate"]

        artifacts = fetch_nyfed_reference_rate(
            self.output_root, "sofr", "2026-01-01", "2026-01-03", downloader
        )
        self.assertEqual(len(artifacts), 2)
        for artifact in artifacts:
            self.assertTrue(artifact.path.exists())
            self.assertEqual(hashlib.sha256(artifact.path.read_bytes()).hexdigest(), artifact.sha256)
            manifest = json.loads(
                artifact.path.with_suffix(artifact.path.suffix + ".manifest.json").read_text()
            )
            self.assertEqual(manifest["sha256"], artifact.sha256)

    def test_fred_rejects_non_csv_response(self):
        with self.assertRaisesRegex(ValueError, "expected CSV"):
            fetch_fred_macro(self.output_root, lambda _: b"not,data\n")

    def test_fred_accepts_and_preserves_zip_snapshot(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("fredgraph.csv", "observation_date,IORB\n2026-01-01,4.30\n")
        artifacts = fetch_fred_macro(self.output_root, lambda _: buffer.getvalue())
        self.assertEqual(artifacts[0].path.suffix, ".zip")
        self.assertEqual(artifacts[0].path.read_bytes(), buffer.getvalue())

    def test_download_decodes_gzip_by_magic_bytes(self):
        payload = b"observation_date,IORB\n2026-01-01,4.30\n"
        self.assertEqual(_decode_transport(gzip.compress(payload)), payload)


if __name__ == "__main__":
    unittest.main()
