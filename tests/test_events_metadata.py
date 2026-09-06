import hashlib
import json
import unittest
from datetime import date
from pathlib import Path


EVENTS_PATH = Path(__file__).parents[1] / "metadata" / "events.json"


class EventMetadataTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))

    def test_frozen_windows_have_the_pinned_consumer_shape(self):
        self.assertEqual(self.payload["version"], 1)
        self.assertEqual(self.payload["checksum_algorithm"], "sha256")
        windows = self.payload["windows"]
        self.assertEqual(
            [(window["name"], window["start"], window["end"]) for window in windows],
            [
                ("sep-2019", "2019-09-16", "2019-09-20"),
                ("mar-2020", "2020-03-09", "2020-03-20"),
            ],
        )
        self.assertEqual(len({window["name"] for window in windows}), len(windows))
        for window in windows:
            self.assertEqual(
                set(window),
                {"name", "start", "end", "checksum"},
            )
            start = date.fromisoformat(window["start"])
            end = date.fromisoformat(window["end"])
            self.assertLessEqual(start, end)

    def test_each_checksum_pins_its_name_and_boundaries(self):
        for window in self.payload["windows"]:
            declaration = {
                "name": window["name"],
                "start": window["start"],
                "end": window["end"],
            }
            canonical = json.dumps(
                declaration,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            self.assertEqual(
                window["checksum"],
                hashlib.sha256(canonical).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
